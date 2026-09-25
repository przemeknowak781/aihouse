"""Wydruk: składanie arkuszy w tom PDF, kontrola skali wydruku i rozdzielczości podglądu.

* ``volume`` — tom: wiele arkuszy (różne formaty) w jednym PDF, opcjonalnie ze spisem rysunków (A4),
* ``pdf_segments`` / ``check_scale`` — pomiar odcinków w wygenerowanym PDF (kontrola, że 1 m w 1:100 = 10,0 mm),
* ``check_png`` — kontrola rozdzielczości PNG (≥ 150 dpi względem formatu arkusza),
* ``add_control_marks`` — odcinek kontrolny 100 mm i informacja o skali na marginesie arkusza.
"""
from __future__ import annotations

import numpy as np

from . import render
from . import text as T
from .sheet import ZNAK_CENTR_DL, Sheet, TitleBlock, control_segment, table, wrap

PT2MM = 25.4 / 72.0


def volume(sheets, pdf_path, title: str = "Tom rysunków", toc: bool = True, toc_tb: TitleBlock | None = None,
           mode: str = "branze") -> str:
    """Składa arkusze w jeden PDF. ``toc=True`` — pierwsza strona A4 ze spisem rysunków (``spis_rysunkow``)."""
    pages = list(sheets)
    if toc:
        pages = [spis_rysunkow(pages, title, toc_tb)] + pages
    render.sheets_to_pdf(pages, pdf_path, mode, title)
    return str(pdf_path)


def spis_rysunkow(sheets, title: str = "Tom rysunków", toc_tb: TitleBlock | None = None) -> Sheet:
    """Strona A4 ze spisem rysunków tomu. Pole spisu leży między znakami centrującymi (lewy i prawy: 10 mm za
    ramką na osi H/2, górny: 10 mm w dół na osi W/2) z odstępem 3 mm. Nagłówek (tytuł tomu) — pismo 5 mm
    (≤ 2 wiersze), a gdy się nie mieści — 3,5 mm (≤ 3 wiersze), łamany do szerokości pola; tytuły rysunków
    łamane w komórce jednolitym pismem 2,5 mm (``table(zawijaj="wiersze")``); wysokość wiersza dopasowana do
    miejsca nad tabliczką."""
    tb = toc_tb or TitleBlock(tytul="SPIS RYSUNKÓW", nr_rysunku="00", skala="—")
    sh = Sheet("A4", title_block=tb)
    rows = []
    for i, s in enumerate(sheets):
        t = s.tb
        rows.append([str(i + 1), t.nr_rysunku if t else "", t.tytul if t else s.meta.get("title", ""),
                     t.skala if t else "", s.fmt_name])
    x0, y0, x1, y1 = sh.frame
    tx = x0 + ZNAK_CENTR_DL + 3.0
    avail = (x1 - ZNAK_CENTR_DL - 3.0) - tx
    tt = title.upper()
    for hh, nmax in ((5.0, 1), (5.0, 2), (3.5, 1), (3.5, 2), (3.5, 3)):
        ls = wrap(tt, avail, hh, "bold")
        if len(ls) <= nmax and all(T.width(x, hh, "bold") <= avail + 1e-6 for x in ls):
            break
    ls = ls[:3]
    y = y1 - ZNAK_CENTR_DL - 2.5 - hh
    for ln in ls:
        sh.text((tx, y), ln, hh, style="bold")
        y -= hh * 1.6
    top = y + hh * 1.6 - 5.5
    cols = [("Lp.", 9.0), ("Nr rys.", 26.0), ("Tytuł rysunku", 81.0), ("Skala", 18.0), ("Format", 20.0)]
    k = avail / sum(w for _n, w in cols)
    cols = [(n, w * k) for n, w in cols]
    tb_top = (sh.tb_rect[3] if sh.tb_rect else y0) + 6.0
    row_h = max(4.5, min(6.0, (top - tb_top) / (len(rows) + 1)))
    table(sh, tx, top, cols, rows, h=2.5, row_h=row_h, zawijaj="wiersze")
    sh.przytnij_znaki_centrujace()
    return sh


def pdf_segments(pdf_path, page: int = 0):
    """Odcinki prostoliniowe z PDF w mm arkusza (początek w lewym dolnym rogu): tablica (n, 4) x1,y1,x2,y2."""
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    pg = doc[page]
    Hmm = pg.rect.height * PT2MM
    segs = []
    for d in pg.get_drawings():
        for it in d.get("items", []):
            if it[0] == "l":
                a, b = it[1], it[2]
                segs.append((a.x * PT2MM, Hmm - a.y * PT2MM, b.x * PT2MM, Hmm - b.y * PT2MM))
    size = (pg.rect.width * PT2MM, Hmm)
    doc.close()
    return np.array(segs), size


def check_scale(pdf_path, sheet, vp, p1_model, p2_model, page: int = 0, tol_mm: float = 0.05) -> dict:
    """Sprawdza w PDF, że odcinek modelu p1–p2 [m] (narysowany w rzutni ``vp``) ma na arkuszu długość
    |p1p2| × 1000 / scale [mm]. Szuka w PDF odcinka o końcach w oczekiwanych miejscach (±tol) i mierzy go."""
    segs, size = pdf_segments(pdf_path, page)
    a, b = vp.to_sheet([p1_model, p2_model])
    expected = float(np.hypot(*(np.asarray(p2_model) - np.asarray(p1_model)))) * 1000.0 / vp.scale
    best = None
    for s in segs:
        for (x1, y1, x2, y2) in ((s[0], s[1], s[2], s[3]), (s[2], s[3], s[0], s[1])):
            e = max(np.hypot(x1 - a[0], y1 - a[1]), np.hypot(x2 - b[0], y2 - b[1]))
            if best is None or e < best[0]:
                best = (e, float(np.hypot(x2 - x1, y2 - y1)))
    ok = best is not None and best[0] <= tol_mm and abs(best[1] - expected) <= tol_mm
    return {"expected_mm": expected, "measured_mm": None if best is None else best[1],
            "endpoint_err_mm": None if best is None else best[0], "page_mm": size,
            "sheet_mm": (sheet.width, sheet.height), "ok": bool(ok)}


def check_png(png_path, sheet, min_dpi: float = 150.0) -> dict:
    from PIL import Image
    im = Image.open(str(png_path))
    w, h = im.size
    dpi_x = w / (sheet.width / 25.4)
    dpi_y = h / (sheet.height / 25.4)
    return {"px": (w, h), "dpi_eff": (round(dpi_x, 1), round(dpi_y, 1)), "dpi_meta": im.info.get("dpi"),
            "ok": min(dpi_x, dpi_y) >= min_dpi - 0.5}


def add_control_marks(sheet: Sheet, length: float = 100.0):
    """Odcinek kontrolny w dolnym marginesie arkusza (sprawdzenie wydruku w skali 1:1)."""
    x0, y0, x1, y1 = sheet.frame
    # napis za odcinkiem nie może trafić na lewy znak centrujący (oś H/2, np. H = 297) — wtedy napis obok odcinka
    y_s = y0 + 8.0
    tw = T.width(f"odcinek kontrolny {int(length)} mm (wydruk 1:1)", 1.8)
    obok = y_s + length + 1.5 < sheet.height / 2.0 + 3.0 and y_s + length + 1.5 + tw > sheet.height / 2.0 - 3.0
    control_segment(sheet, (x0 * 0.55, y_s), length, vertical=True, tekst_obok=obok)


# ------------------------------------------------------------------------------------------------ kontrola jakości
def qa(sheet, kind: str | None = None) -> dict:
    """Automatyczna kontrola arkusza wg R4 pkt 3.14.

    kind: 'PZT' | 'PAB' | 'PT' | None (z pola ``stadium`` tabliczki). Zwraca {"ok", "errors", "warnings", "stats"}.
    Sprawdza: pola metryki (§ 10 rozp.), obecność legendy (§ 9), podziałki minimalne (PAB/PT ≥ 1:100, PZT ≥ 1:500),
    grubości linii z szeregu ISO 128-2, wysokości pisma z szeregu ISO 3098 (PZT ≥ 2,5 mm), zgodność sum łańcuchów
    wymiarowych z wymiarem całkowitym (po zaokrągleniu do mm, tolerancja 0)."""
    from . import styles, fmt as F
    from .core import PArc, PLine, PText, text_items
    errors, warnings = [], []
    tb = sheet.tb
    stad = (kind or (tb.stadium if tb else "") or "").upper()
    # 1. metryka
    if tb is None:
        errors.append("brak tabliczki rysunkowej")
    else:
        for f, name in (("obiekt", "nazwa obiektu"), ("tytul", "tytuł rysunku"), ("skala", "skala"),
                        ("nr_rysunku", "nr rysunku"), ("data", "data"), ("format", "format")):
            if not getattr(tb, f):
                errors.append(f"tabliczka: brak pola „{name}”")
        proj = [o for o in tb.osoby if o.funkcja.lower().startswith("projektant")]
        if not proj or not proj[0].imie_nazwisko or not proj[0].specjalnosc_uprawnienia:
            errors.append("tabliczka: puste pole projektanta bez znacznika [DO UZUPEŁNIENIA] (RPB § 10 ust. 1 pkt 3, W-320)")
        elif "DO UZUPEŁNIENIA" in proj[0].imie_nazwisko + proj[0].specjalnosc_uprawnienia:
            warnings.append("tabliczka: projektant (imię, nazwisko, nr uprawnień) — [DO UZUPEŁNIENIA] (§ 10 rozp.)")
        spr = [o for o in tb.osoby if o.funkcja.lower().startswith("sprawdz")]
        if tb.sprawdzenie and spr and not spr[0].imie_nazwisko:
            errors.append("tabliczka: puste pole „Sprawdzający” — wpisać osobę albo „nie dotyczy (art. 20 ust. 3 pkt 2 PB)” (W-305)")
    # 2. legenda
    all_prims = [(None, sheet, p) for p in sheet.prims] + [(vp, vp, p) for vp in sheet.viewports for p in vp.prims]
    if not any(p.layer == "R-LEGENDA" for _v, _c, p in all_prims):
        warnings.append("brak legendy na arkuszu (R-LEGENDA) — wymagana dla oznaczeń spoza norm z zał. 2 rozp.")
    # 3. podziałki
    lim = 500 if "PZT" in stad else 100
    for vp in sheet.viewports:
        if vp.scale > lim + 1e-9 and stad:
            errors.append(f"rzutnia „{vp.title}”: podziałka 1:{vp.scale:g} mniejsza niż dopuszczalna 1:{lim}")
    # 4. grubości linii i 5. pismo
    series_lw = set(round(x, 2) for x in styles.ISO_LINEWEIGHTS)
    bad_lw, bad_h, bad_gl = {}, {}, {}
    min_h = 2.5 if "PZT" in stad else 1.8
    n_txt = 0
    for vp, canvas, p in all_prims:
        if not styles.layer(p.layer).plot:
            continue
        if isinstance(p, (PLine, PArc)):
            lw = round(canvas.pen_mm(p.pen, p.layer), 2)
            if lw not in series_lw:
                bad_lw[lw] = bad_lw.get(lw, 0) + 1
        elif isinstance(p, PText):
            for _xy, s, hh in text_items(p, canvas.k)[0]:
                n_txt += 1
                for ch in T.brakujace_znaki(s, p.style):
                    bad_gl.setdefault(ch, []).append(s[:20])
                h2 = round(hh, 2)
                too_small = vp is not None and h2 < min_h - 0.02   # min. 2,5 mm na PZT — treść rysunku
                if not any(abs(h2 - x) < 0.02 for x in styles.TEXT_SERIES) or too_small:
                    bad_h.setdefault(h2, []).append(s[:20])
    for lw, n in sorted(bad_lw.items()):
        errors.append(f"grubość linii {lw} mm spoza szeregu ISO 128-2 ({n}×)")
    for ch, ex in sorted(bad_gl.items()):
        warnings.append(f"znak „{ch}” (U+{ord(ch):04X}) spoza kroju pisma — w PDF pusty prostokąt ({len(ex)}×, "
                        f"np. {ex[:2]}); dodać zamiennik w draft.text.ZAMIENNIKI")
    for h, ex in sorted(bad_h.items()):
        errors.append(f"wysokość pisma {h} mm spoza szeregu ISO 3098 / poniżej minimum ({len(ex)}×, np. {ex[:3]})")
    # 7. łańcuchy wymiarowe: suma zaokrąglonych odcinków = zaokrąglony wymiar całkowity
    n_ch = 0
    for vp in sheet.viewports:
        chains = getattr(vp, "dim_chains", [])
        for ch in chains:
            t = ch["t"]
            if len(t) < 3 or ch.get("labels"):
                continue
            for other in chains:
                ot = other["t"]
                if other is ch or len(ot) != 2 or other.get("labels"):
                    continue
                if abs(ot[0] - t[0]) < 1e-6 and abs(ot[1] - t[-1]) < 1e-6 and np.allclose(other["d"], ch["d"]):
                    n_ch += 1
                    parts = [F.round_half_up((b - a) * 1000) for a, b in zip(t[:-1], t[1:])]
                    total = F.round_half_up((t[-1] - t[0]) * 1000)
                    if sum(parts) != total:
                        errors.append(f"rzutnia „{vp.title}”: łańcuch {[p_ / 10 for p_ in parts]} cm sumuje się do "
                                      f"{sum(parts) / 10} cm ≠ wymiar całkowity {total / 10} cm")
    return {"ok": not errors, "errors": errors, "warnings": warnings,
            "stats": {"prymitywy": len(all_prims), "napisy": n_txt, "sprawdzone_lancuchy": n_ch}}
