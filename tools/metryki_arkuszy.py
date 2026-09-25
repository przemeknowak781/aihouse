#!/usr/bin/env python3
"""Metryki ekonomii arkuszy rysunkowych: format, powierzchnia papieru, współczynnik wypełnienia, plan składania do A4.

Wejście: katalogi z arkuszami z generatora (``raport_widokow.json`` + PDF; bez raportu — wszystkie ``*.pdf`` poza
``tom_*.pdf``). Dla każdego arkusza liczy:

* format i wymiary [mm] (z PDF), powierzchnię [m²], pole wewnątrz ramki (ramka ``lamela.draft.Sheet``: 20 mm po
  lewej, 10 mm z pozostałych stron — odczytana z PDF, gdy znaleziona),
* **współczynnik wypełnienia** W = pole sumy obwiedni bloków treści / pole wewnątrz ramki,
* plan składania do A4 (``lamela.draft.sheet.fold_positions``: pasy harmonijki, zgięcia poziome) i jego ocenę,
* sumy na komplet.

Metoda wyznaczania bloków treści (z rzeczywistej zawartości PDF, PyMuPDF):
1. Prymitywy wektorowe (``page.get_drawings``) rozbijane na pojedyncze odcinki/krzywe/prostokąty (obwiednia każdego
   segmentu osobno — ścieżki zbiorcze matplotlib nie „sklejają” odległych widoków) oraz obwiednie spanów tekstu
   (``page.get_text('dict')``).
2. Pomijane: wszystko, co nie leży w całości wewnątrz ramki (znaki składania, centrujące, siatka pól, opis formatu),
   sama ramka (obiekt o obwiedni ≥ 95 % ramki), niewidoczne białe wypełnienia (maski pod tekstem), tabliczka
   z tabelą zmian (wykrywana jako białe wypełnienie szer. ≈ 180 mm w prawym dolnym rogu ramki) — tabliczka jest
   doliczana jako osobny, stały blok.
3. Obwiednie rzutowane na siatkę 1 mm (maska zajętości), domknięcie morfologiczne o promieniu ``--odstep``
   (domyślnie 6 mm: łączy elementy jednego widoku/tabeli, nie łączy bloków rozdzielonych normalnym odstępem),
   wypełnienie dziur; każda spójna składowa → prostokątna obwiednia bloku.
4. W (obwiednie) = pole sumy (bez podwójnego liczenia) prostokątów bloków + tabliczki / pole wewnątrz ramki.
   Dodatkowo: W_kontur (pole samej domkniętej maski, bez prostokątów), W_skł (jak W obw., ale składowa wklęsła —
   maska < 75 % obwiedni, np. „L” z bloków sklejonych domknięciem — liczona obwiedniami części po domknięciu
   1 mm; pokazuje puste pola, które W obw. zamyka w jednej obwiedni), największy pusty prostokąt wewnątrz ramki
   (na obwiedniach części jak W skł.)
   oraz „arkusz przycięty” — obwiednia całej treści + marginesy 20/10 mm (ile papieru zostaje przy obecnym
   układzie po odcięciu pustych pasów).

Użycie::

    PYTHONPATH=src python3 tools/metryki_arkuszy.py AR=projekt/01_koncepcja/widoki PZT=projekt/02_PZT/rysunki \\
        --md docs/30_arkusze/metryki.md --json metryki.json [--podglad katalog_png] [--odstep 6]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pymupdf
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PT = 25.4 / 72.0          # pt → mm
A4_AREA = 0.210 * 0.297   # m²
BINDING, MARGIN, TB_W = 20.0, 10.0, 180.0


# ================================================================================================ wejście
def load_set(katalog: Path) -> list[dict]:
    """Lista arkuszy kompletu: {nr, tytul, format_cfg, skala, pdf}."""
    katalog = Path(katalog)
    rap = katalog / "raport_widokow.json"
    out = []
    if rap.exists():
        d = json.loads(rap.read_text(encoding="utf-8"))
        for a in d.get("arkusze", []):
            pdf = (a.get("pliki") or {}).get("pdf")
            if not pdf:
                continue
            cands = [Path(pdf), ROOT / pdf, katalog / Path(pdf).name]
            p = next((c for c in cands if c.exists()), None)
            if p is None:
                continue
            out.append(dict(nr=a.get("nr"), tytul=a.get("tytul"), format_cfg=a.get("format"), skala=a.get("skala"),
                            pdf=p))
    if not out:
        for p in sorted(katalog.glob("*.pdf")):
            if p.name.startswith("tom"):
                continue
            nr = p.stem.split("_")[0]
            out.append(dict(nr=nr, tytul=p.stem, format_cfg=None, skala=None, pdf=p))
    return out


# ================================================================================================ treść PDF
def _segments(dr) -> list[tuple]:
    """Obwiednie pojedynczych segmentów ścieżki [mm, układ PDF: y w dół]."""
    out = []
    for it in dr["items"]:
        op = it[0]
        if op == "l":
            pts = [it[1], it[2]]
        elif op == "c":
            pts = [it[1], it[2], it[3], it[4]]
        elif op == "re":
            r = it[1]
            pts = [r.tl, r.br]
        elif op == "qu":
            q = it[1]
            pts = [q.ul, q.ur, q.ll, q.lr]
        else:
            continue
        xs = [p.x * PT for p in pts]
        ys = [p.y * PT for p in pts]
        out.append((min(xs), min(ys), max(xs), max(ys)))
    return out


def _is_white(c) -> bool:
    return c is not None and all(v > 0.99 for v in c)


def _find_frame(drawings, W, H):
    """Ramka: największy obrysowany prostokąt wewnątrz arkusza (domyślnie 20/10/10/10 mm)."""
    best = None
    for dr in drawings:
        if dr.get("color") is None:
            continue
        r = dr["rect"]
        x0, y0, x1, y1 = r.x0 * PT, r.y0 * PT, r.x1 * PT, r.y1 * PT
        if x0 > 1 and y0 > 1 and x1 < W - 1 and y1 < H - 1 and (x1 - x0) > 0.8 * W and (y1 - y0) > 0.8 * H:
            if best is None or (x1 - x0) * (y1 - y0) > (best[2] - best[0]) * (best[3] - best[1]):
                best = (x0, y0, x1, y1)
    return best or (BINDING, MARGIN, W - MARGIN, H - MARGIN)


def _find_title_block(drawings, frame):
    """Tabliczka (+ tabela zmian): białe wypełnienia szer. ≈ 180 mm, przyległe do prawego dolnego rogu ramki."""
    fx0, fy0, fx1, fy1 = frame
    fills = []
    for dr in drawings:
        if dr.get("type") != "f" or not _is_white(dr.get("fill")):
            continue
        r = dr["rect"]
        x0, y0, x1, y1 = r.x0 * PT, r.y0 * PT, r.x1 * PT, r.y1 * PT
        if abs(x1 - fx1) < 1.0 and abs((x1 - x0) - TB_W) < 2.0:
            fills.append((x0, y0, x1, y1))
    if not fills:
        return None
    fills.sort(key=lambda r: -r[3])
    if abs(fills[0][3] - fy1) > 1.0:
        return None
    top = fills[0][1]
    x0 = fills[0][0]
    for r in fills[1:]:
        if abs(r[3] - top) < 1.0:
            top = r[1]
    return (x0, top, fx1, fy1)


def _largest_empty_rect(occ: np.ndarray) -> tuple[int, int, int, int, int]:
    """Największy prostokąt z samych False (histogram wierszami). Zwraca (pole, r0, c0, h, w) w komórkach."""
    rows, cols = occ.shape
    hist = np.zeros(cols, dtype=np.int32)
    best = (0, 0, 0, 0, 0)
    for r in range(rows):
        hist = np.where(occ[r], 0, hist + 1)
        stack: list[int] = []
        h = hist.tolist() + [0]
        for c in range(cols + 1):
            while stack and h[stack[-1]] >= h[c]:
                top = stack.pop()
                width = c - (stack[-1] + 1 if stack else 0)
                area = h[top] * width
                if area > best[0]:
                    best = (area, r - h[top] + 1, (stack[-1] + 1 if stack else 0), h[top], width)
            stack.append(c)
    return best


def analyze_pdf(pdf: Path, odstep: float = 6.0, res: float = 1.0) -> dict:
    """Metryki jednego arkusza (pierwsza strona PDF). Współrzędne wyniku: mm, układ PDF (x w prawo, y w dół)."""
    doc = pymupdf.open(str(pdf))
    pg = doc[0]
    W, H = pg.rect.width * PT, pg.rect.height * PT
    drawings = pg.get_drawings()
    frame = _find_frame(drawings, W, H)
    fx0, fy0, fx1, fy1 = frame
    tb = _find_title_block(drawings, frame)
    tol = 0.5
    boxes = []
    for dr in drawings:
        stroke = dr.get("color")
        fill = dr.get("fill")
        if stroke is None and (fill is None or _is_white(fill)):
            continue                                   # niewidoczne (maski, tła)
        r = dr["rect"]
        rw, rh = r.width * PT, r.height * PT
        if rw > 0.95 * (fx1 - fx0) and rh > 0.95 * (fy1 - fy0):
            continue                                   # ramka
        boxes.extend(_segments(dr))
    td = pg.get_text("dict")
    for b in td["blocks"]:
        if b.get("type") != 0:
            continue
        for ln in b["lines"]:
            for sp in ln["spans"]:
                if sp["text"].strip():
                    x0, y0, x1, y1 = sp["bbox"]
                    boxes.append((x0 * PT, y0 * PT, x1 * PT, y1 * PT))
    doc.close()
    # siatka zajętości wewnątrz ramki
    nx, ny = int(math.ceil((fx1 - fx0) / res)), int(math.ceil((fy1 - fy0) / res))
    occ = np.zeros((ny, nx), dtype=bool)
    n_used = 0
    for x0, y0, x1, y1 in boxes:
        if x0 < fx0 - tol or y0 < fy0 - tol or x1 > fx1 + tol or y1 > fy1 + tol:
            continue                                   # poza ramką / przecina ramkę (znaki, siatka pól)
        if tb and x0 >= tb[0] - tol and y0 >= tb[1] - tol:
            continue                                   # tabliczka — stały blok
        c0, r0 = int((x0 - fx0) / res), int((y0 - fy0) / res)
        c1, r1 = int(math.ceil((x1 - fx0) / res)), int(math.ceil((y1 - fy0) / res))
        occ[max(r0, 0):max(r1, r0 + 1), max(c0, 0):max(c1, c0 + 1)] = True
        n_used += 1
    k = max(1, int(round(odstep / res)))
    closed = ndimage.binary_dilation(occ, structure=np.ones((2 * k + 1, 2 * k + 1), bool))
    closed = ndimage.binary_erosion(closed, structure=np.ones((2 * k + 1, 2 * k + 1), bool), border_value=1)
    closed = ndimage.binary_fill_holes(closed | occ)
    lab, n = ndimage.label(closed)
    blocks = []
    for sl in ndimage.find_objects(lab):
        r0, r1, c0, c1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        blocks.append((fx0 + c0 * res, fy0 + r0 * res, fx0 + c1 * res, fy0 + r1 * res))
    union = np.zeros_like(occ)
    for bx0, by0, bx1, by1 in blocks:
        union[int(round((by0 - fy0) / res)):int(round((by1 - fy0) / res)),
              int(round((bx0 - fx0) / res)):int(round((bx1 - fx0) / res))] = True
    tb_mask = np.zeros_like(occ)
    if tb:
        tb_mask[int(round((tb[1] - fy0) / res)):, int(round((tb[0] - fx0) / res)):] = True
    # W skł. — obwiednie składowych, ale składowa wklęsła (np. „L” z bloków połączonych domknięciem 6 mm, których
    # obwiednia obejmuje puste pole) — dzielona domknięciem 1 mm na części i liczona obwiedniami części
    # (odstępy bloków silnika układu ≥ 5 mm, na siatce 1 mm ≥ 4 komórki; zgłoszenie AR: PB-AR-01 W obw. 93 % przy
    # pustym polu 230×110 mm)
    k2 = max(1, int(round(1.0 / res)))
    st2 = np.ones((2 * k2 + 1, 2 * k2 + 1), bool)
    closed2 = ndimage.binary_fill_holes(
        ndimage.binary_erosion(ndimage.binary_dilation(occ, structure=st2), structure=st2, border_value=1) | occ)
    union_s = np.zeros_like(occ)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        comp = lab[sl] == i + 1
        if comp.mean() >= 0.75:
            union_s[sl] = True
            continue
        lab2, _n2 = ndimage.label(closed2[sl] & comp)
        part = union_s[sl]
        for sl2 in ndimage.find_objects(lab2):
            part[sl2] = True
    frame_area = (fx1 - fx0) * (fy1 - fy0)
    cell = res * res
    a_blocks = float((union | tb_mask).sum()) * cell
    a_blocks_no_tb = float((union & ~tb_mask).sum()) * cell
    a_contour = float((closed | tb_mask).sum()) * cell
    a_skl = float((union_s | tb_mask).sum()) * cell
    a_tb = float(tb_mask.sum()) * cell
    # największy pusty prostokąt (siatka 2 mm) — na obwiedniach części składowych (jak W skł.), nie obwiedniach
    # po domknięciu 6 mm: puste pole wewnątrz „L” z bloków sklejonych domknięciem jest widoczne (weryfikacja C 2.13:
    # PT-IE-04 — pole 170×235 mm pod tytułem widoku raportowane dawniej jako 360×52 mm)
    s = max(1, int(round(2.0 / res)))
    hh, ww = union.shape[0] // s * s, union.shape[1] // s * s
    coarse = (union_s | tb_mask)[:hh, :ww].reshape(hh // s, s, ww // s, s).any(axis=(1, 3))
    le = _largest_empty_rect(coarse)
    empty = dict(pole_m2=le[0] * (s * res) ** 2 / 1e6, w=le[4] * s * res, h=le[3] * s * res,
                 x=fx0 + le[2] * s * res, y=fy0 + le[1] * s * res)
    # obwiednia całej treści → arkusz „przycięty”
    allm = union | tb_mask
    if allm.any():
        rr = np.where(allm.any(axis=1))[0]
        cc = np.where(allm.any(axis=0))[0]
        cw, ch = (cc[-1] - cc[0] + 1) * res, (rr[-1] - rr[0] + 1) * res
    else:
        cw = ch = 0.0
    trim_w, trim_h = cw + BINDING + MARGIN, ch + 2 * MARGIN
    return dict(W=W, H=H, frame=frame, tb=tb, pole_arkusza_m2=W * H / 1e6, pole_ramki_m2=frame_area / 1e6,
                pole_tabliczki_m2=a_tb / 1e6, n_prymitywow=n_used, bloki=blocks,
                wypelnienie=a_blocks / frame_area,
                wypelnienie_rys=a_blocks_no_tb / max(1e-9, frame_area - a_tb),
                wypelnienie_kontur=a_contour / frame_area, wypelnienie_skl=a_skl / frame_area,
                pusty_prostokat=empty, przyciety=dict(W=trim_w, H=trim_h, pole_m2=trim_w * trim_h / 1e6))


def preview(pdf: Path, res: dict, out_png: Path, dpi: int = 40) -> Path:
    """Podgląd kontrolny: arkusz + obwiednie bloków (czerwone), tabliczka (niebieska), największy pusty prostokąt
    (zielony), linie składania (fioletowe, przerywane)."""
    from PIL import Image, ImageDraw
    doc = pymupdf.open(str(pdf))
    pix = doc[0].get_pixmap(dpi=dpi)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    doc.close()
    s = dpi / 25.4
    d = ImageDraw.Draw(img, "RGBA")
    for x0, y0, x1, y1 in res["bloki"]:
        d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(220, 0, 0, 255), fill=(255, 0, 0, 40), width=2)
    if res["tb"]:
        x0, y0, x1, y1 = res["tb"]
        d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], outline=(0, 0, 220, 255), fill=(0, 0, 255, 40), width=2)
    e = res["pusty_prostokat"]
    d.rectangle([e["x"] * s, e["y"] * s, (e["x"] + e["w"]) * s, (e["y"] + e["h"]) * s], outline=(0, 160, 0, 255),
                fill=(0, 200, 0, 50), width=2)
    fp = res.get("skladanie") or {}
    for x in fp.get("zgiecia_pionowe", []):
        for yy in range(0, int(res["H"] * s), 12):
            d.line([x * s, yy, x * s, yy + 6], fill=(150, 0, 200, 255), width=2)
    for y in fp.get("zgiecia_poziome", []):        # od dolnej krawędzi → układ PDF
        yp = (res["H"] - y) * s
        for xx in range(0, int(res["W"] * s), 12):
            d.line([xx, yp, xx + 6, yp], fill=(150, 0, 200, 255), width=2)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return out_png


# ================================================================================================ składanie
def fold_plan(W: float, H: float) -> dict:
    """Plan składania do A4 wg ``lamela.draft.sheet.fold_positions`` i jego ocena.

    Ocena „ładnego” składania (wymaganie inwestora: równe pasy bliskie 190–210 mm, wysokość bliska wielokrotności
    297 mm):
    * pasy pionowe: szerokość paczki ≤ 210 mm (warunek konieczny); pasy harmonijki poza pierwszym (210 z marginesem
      20 mm) i ostatnim (190 z tabliczką) — „równe” (różnica ≤ 5 mm) i w przedziale 180–210 mm → dobre;
      ≥ 120 mm → poprawne; węższe → słabe (zbędne warstwy). Arkusze 210 < W ≤ 420 składane są klasycznie
      (105 + reszta + 190): dobre dla W ≥ 400 mm.
    * zgięcia poziome: ostatni rząd (górny) ≥ 0,9·297 mm → dobre; ≥ 0,35·297 (≈ 104 mm, jak A2: 297 + 123)
      → poprawne; węższy → słabe (wąski pasek zaginany „na siłę”).
    """
    from lamela.draft.sheet import fold_positions
    xs, ys = fold_positions(W, H)
    edges = [0.0] + list(xs) + [W]
    pasy = [round(b - a, 1) for a, b in zip(edges[:-1], edges[1:])]
    hedges = [0.0] + list(ys) + [H]
    rzedy = [round(b - a, 1) for a, b in zip(hedges[:-1], hedges[1:])]
    paczka_w = max(pasy)
    uw = []
    if W <= 210.5:
        ov = "dobre"
    elif W <= 420.5:
        ov = "dobre" if W >= 399.5 else "poprawne"
        if W < 399.5:
            uw.append(f"pas środkowy {pasy[1]:.0f} mm (klasyczne A3: 125 mm)")
    else:
        mid = pasy[1:-1] if len(pasy) > 2 else pasy
        rozrzut = max(mid) - min(mid)
        if min(mid) >= 180 and rozrzut <= 5.0:
            ov = "dobre"
        elif min(mid) >= 120:
            ov = "poprawne"
        else:
            ov = "słabe"
        if min(mid) < 180:
            uw.append(f"najwęższy pas pośredni {min(mid):.0f} mm")
        if rozrzut > 5.0:
            uw.append(f"pasy nierówne (rozrzut {rozrzut:.0f} mm)")
    if paczka_w > 210.5:
        ov = "słabe"
        uw.append(f"paczka szersza niż A4 ({paczka_w:.0f} mm)")
    last = rzedy[-1]
    if len(rzedy) == 1 or last >= 0.9 * 297.0:
        oh = "dobre"
    elif last >= 0.35 * 297.0:
        oh = "poprawne"
        uw.append(f"górny rząd {last:.0f} mm (niepełny)")
    else:
        oh = "słabe"
        uw.append(f"górny rząd tylko {last:.0f} mm (wąski pasek)")
    rank = {"dobre": 2, "poprawne": 1, "słabe": 0}
    ocena = min((ov, oh), key=lambda o: rank[o])
    n_pan = len(pasy) * len(rzedy)
    return dict(zgiecia_pionowe=[round(x, 1) for x in xs], zgiecia_poziome=[round(y, 1) for y in ys], pasy=pasy,
                rzedy=rzedy, n_pasow=len(pasy), n_rzedow=len(rzedy), warstwy=n_pan,
                wykorzystanie_paczki=W * H / (n_pan * 210.0 * 297.0), ocena=ocena, ocena_pion=ov, ocena_poziom=oh,
                uwagi=uw)


# ================================================================================================ komplet
def format_name(W: float, H: float) -> str:
    try:
        from lamela.dokumenty.formaty import wykryj_format
        return wykryj_format(W, H) or f"{W:.0f}×{H:.0f}"
    except Exception:      # pragma: no cover
        return f"{W:.0f}×{H:.0f}"


def measure_set(nazwa: str, katalog: Path, odstep: float = 6.0, podglad: Path | None = None) -> dict:
    wiersze = []
    for a in load_set(katalog):
        r = analyze_pdf(a["pdf"], odstep)
        r["skladanie"] = fold_plan(r["W"], r["H"])
        r["przyciety"]["W"] = float(min(r["przyciety"]["W"], r["W"]))
        r["przyciety"]["H"] = float(min(r["przyciety"]["H"], r["H"]))
        r["przyciety"]["pole_m2"] = r["przyciety"]["W"] * r["przyciety"]["H"] / 1e6
        r.update(nr=a["nr"], tytul=a["tytul"], skala=a["skala"], pdf=str(a["pdf"]),
                 format=a["format_cfg"] or format_name(r["W"], r["H"]))
        if podglad:
            r["podglad"] = str(preview(a["pdf"], r, Path(podglad) / nazwa / f"{a['nr']}.png"))
        r["bloki"] = [[round(v, 1) for v in b] for b in r["bloki"]]
        wiersze.append(r)
    import datetime as _dt
    mt = max((Path(w["pdf"]).stat().st_mtime for w in wiersze), default=None)
    stan = _dt.datetime.fromtimestamp(mt).strftime("%Y-%m-%d %H:%M") if mt else None
    return dict(komplet=nazwa, katalog=str(katalog), stan_plikow=stan, arkusze=wiersze, sumy=totals(wiersze))


def totals(ws: list[dict]) -> dict:
    if not ws:
        return dict(arkuszy=0)
    pole = sum(w["pole_arkusza_m2"] for w in ws)
    ramka = sum(w["pole_ramki_m2"] for w in ws)
    tresc = sum(w["wypelnienie"] * w["pole_ramki_m2"] for w in ws)
    fmts: dict = {}
    for w in ws:
        fmts[w["format"]] = fmts.get(w["format"], 0) + 1
    oceny = {o: sum(1 for w in ws if w["skladanie"]["ocena"] == o) for o in ("dobre", "poprawne", "słabe")}
    worst = min(ws, key=lambda w: w["wypelnienie"])
    return dict(arkuszy=len(ws), pole_m2=pole, a4_ekw=pole / A4_AREA, pole_ramki_m2=ramka,
                wypelnienie_wazone=tresc / ramka, wypelnienie_srednie=sum(w["wypelnienie"] for w in ws) / len(ws),
                wypelnienie_min=worst["wypelnienie"], najgorsze=worst["nr"],
                puste_m2=ramka - tresc, przyciete_m2=sum(w["przyciety"]["pole_m2"] for w in ws),
                warstwy_a4=sum(w["skladanie"]["warstwy"] for w in ws), formaty=fmts, oceny_skladania=oceny)


# ================================================================================================ raport
def _pl(x: float, n: int = 2) -> str:
    return f"{x:.{n}f}".replace(".", ",")


def _pct(x: float) -> str:
    return f"{x * 100:.0f} %"


def markdown_set(k: dict) -> str:
    s = k["sumy"]
    L = [f"### {k['komplet']} — `{k['katalog']}`", ""]
    if k.get("stan_plikow"):
        L += [f"Stan plików PDF: {k['stan_plikow']}.", ""]
    if not s.get("arkuszy"):
        return "\n".join(L + ["Brak arkuszy PDF.", ""])
    L += ["| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W skł. | W rys. | W kontur | Największy pusty prostokąt | "
          "Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for w in k["arkusze"]:
        e, p, f = w["pusty_prostokat"], w["przyciety"], w["skladanie"]
        ocena = f["ocena"] + (" — " + "; ".join(f["uwagi"]) if f["uwagi"] else "")
        L.append(f"| {w['nr']} | {w['format']} | {w['W']:.0f}×{w['H']:.0f} | {_pl(w['pole_arkusza_m2'], 3)} | "
                 f"{_pct(w['wypelnienie'])} | {_pct(w.get('wypelnienie_skl', w['wypelnienie']))} | "
                 f"{_pct(w['wypelnienie_rys'])} | {_pct(w['wypelnienie_kontur'])} | "
                 f"{e['w']:.0f}×{e['h']:.0f} ({_pl(e['pole_m2'], 3)} m²) | {p['W']:.0f}×{p['H']:.0f} | "
                 f"{' + '.join(f'{x:.0f}' for x in f['pasy'])} | {' + '.join(f'{x:.0f}' for x in f['rzedy'])} | "
                 f"{f['warstwy']} | {ocena} |")
    fm = ", ".join(f"{n}× {f}" for f, n in s["formaty"].items())
    oc = ", ".join(f"{o}: {n}" for o, n in s["oceny_skladania"].items() if n)
    L += ["", f"**Suma:** {s['arkuszy']} ark. ({fm}); papier {_pl(s['pole_m2'])} m² (≈ {_pl(s['a4_ekw'], 1)} A4); "
          f"wypełnienie ważone {_pct(s['wypelnienie_wazone'])}, średnie {_pct(s['wypelnienie_srednie'])}, "
          f"najniższe {_pct(s['wypelnienie_min'])} ({s['najgorsze']}); puste pole w ramkach "
          f"{_pl(s['puste_m2'])} m²; po samym przycięciu pustych pasów {_pl(s['przyciete_m2'])} m² "
          f"(−{_pct(1 - s['przyciete_m2'] / s['pole_m2'])}); warstw A4 po złożeniu: {s['warstwy_a4']}; "
          f"składanie — {oc}.", ""]
    return "\n".join(L)


def markdown_summary(wyniki: list[dict]) -> str:
    """Tabela zbiorcza kompletów."""
    L = ["| Komplet | Arkuszy | Formaty | Papier [m²] | ≈ A4 | W ważone | W średnie | W min (arkusz) | Puste [m²] | "
         "Po przycięciu [m²] | Warstwy A4 | Składanie (dobre/poprawne/słabe) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in wyniki:
        s = k["sumy"]
        if not s.get("arkuszy"):
            L.append(f"| {k['komplet']} | 0 | — | — | — | — | — | — | — | — | — | — |")
            continue
        fm = ", ".join(f"{n}× {f}" for f, n in s["formaty"].items())
        o = s["oceny_skladania"]
        L.append(f"| {k['komplet']} | {s['arkuszy']} | {fm} | {_pl(s['pole_m2'])} | {_pl(s['a4_ekw'], 0)} | "
                 f"{_pct(s['wypelnienie_wazone'])} | {_pct(s['wypelnienie_srednie'])} | "
                 f"{_pct(s['wypelnienie_min'])} ({s['najgorsze']}) | {_pl(s['puste_m2'])} | {_pl(s['przyciete_m2'])} | "
                 f"{s['warstwy_a4']} | {o['dobre']}/{o['poprawne']}/{o['słabe']} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("komplety", nargs="+", help="NAZWA=katalog (lub sam katalog)")
    ap.add_argument("--md", help="raport Markdown (tabele kompletów)")
    ap.add_argument("--json", help="wyniki JSON")
    ap.add_argument("--podglad", help="katalog na podglądy PNG z obwiedniami bloków")
    ap.add_argument("--odstep", type=float, default=6.0, help="promień domknięcia bloków [mm] (domyślnie 6)")
    a = ap.parse_args(argv)
    wyniki = []
    for spec in a.komplety:
        nazwa, _, kat = spec.partition("=") if "=" in spec else (Path(spec).name, "", spec)
        if not Path(kat).is_dir():
            print(f"[pominięto] {nazwa}: brak katalogu {kat}", file=sys.stderr)
            continue
        k = measure_set(nazwa, Path(kat), a.odstep, Path(a.podglad) if a.podglad else None)
        wyniki.append(k)
        s = k["sumy"]
        if s.get("arkuszy"):
            print(f"{nazwa:8s} {s['arkuszy']:3d} ark.  {s['pole_m2']:6.2f} m²  W={s['wypelnienie_wazone']:.2f} "
                  f"(min {s['wypelnienie_min']:.2f} {s['najgorsze']})  warstw A4 {s['warstwy_a4']}  "
                  f"{s['oceny_skladania']}")
    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(wyniki, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    if a.md:
        Path(a.md).parent.mkdir(parents=True, exist_ok=True)
        Path(a.md).write_text(markdown_summary(wyniki) + "\n" + "\n".join(markdown_set(k) for k in wyniki),
                              encoding="utf-8")
    return wyniki


if __name__ == "__main__":
    main()
