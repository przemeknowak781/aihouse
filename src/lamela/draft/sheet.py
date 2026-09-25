"""Arkusz rysunkowy: formaty (PN-EN ISO 5457 / ISO 216), ramka, znaki składania do A4, znaki centrujące,
tabliczka rysunkowa (PN-EN ISO 7200 + pola polskiej praktyki), legenda, uwagi, podziałka liniowa, tytuły rzutni.

Wymiary w mm, początek układu = lewy dolny róg arkusza.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from . import fmt, styles, text as T
from .core import SheetBase, Viewport
from .geom import rect_pts

# ------------------------------------------------------------------------------------------------ formaty
ISO_A = {"A0": (841, 1189), "A1": (594, 841), "A2": (420, 594), "A3": (297, 420), "A4": (210, 297)}
# Formaty wydłużone wg PN-EN ISO 5457 (tabl. 2 i 3) — wymiary zaokrąglone jak w normie
ISO_ELONGATED = {
    "A3x3": (420, 891), "A3x4": (420, 1189), "A4x3": (297, 630), "A4x4": (297, 841), "A4x5": (297, 1051),
    "A0x2": (1189, 1682), "A0x3": (1189, 2523), "A1x3": (841, 1783), "A1x4": (841, 2378), "A2x3": (594, 1261),
    "A2x4": (594, 1682), "A2x5": (594, 2102), "A3x5": (420, 1486), "A3x6": (420, 1783), "A3x7": (420, 2080),
    "A4x6": (297, 1261), "A4x7": (297, 1471), "A4x8": (297, 1682), "A4x9": (297, 1892),
}


def custom_size(fmt_name) -> tuple[float, float] | None:
    """Format niestandardowy podany wymiarami: '780x594' / '780×594' / 'nst. 780×594' / (780, 594) → (szer., wys.)
    w kolejności zapisu; None — to nie jest zapis wymiarów."""
    if isinstance(fmt_name, (tuple, list)) and len(fmt_name) == 2:
        return float(fmt_name[0]), float(fmt_name[1])
    s = str(fmt_name).lower().replace("nst.", "").replace("×", "x").replace(" ", "").replace(",", ".")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)", s)
    return (float(m.group(1)), float(m.group(2))) if m else None


def sheet_size(fmt_name: str, orientation: str | None = None) -> tuple[float, float]:
    """(szerokość, wysokość) [mm]. ``fmt_name``: 'A0'…'A4', formaty wydłużone 'A3x3' / 'A3×3' / 'A2x2' (ogólnie
    Ak×n: krótszy bok = dłuższy bok Ak, dłuższy = n × krótszy bok Ak) albo format niestandardowy '780x594'
    (szerokość × wysokość, jak zapisano). ``orientation``: 'landscape' | 'portrait' (domyślnie: A4 pionowo, formaty
    niestandardowe jak zapisano, pozostałe poziomo)."""
    cs = custom_size(fmt_name)
    if cs is not None:
        if orientation is None:
            return cs
        short, long_ = min(cs), max(cs)
        return (long_, short) if orientation == "landscape" else (short, long_)
    key = fmt_name.upper().replace("×", "X").replace(" ", "")
    key = key.replace("X", "x")
    if key in ISO_A:
        a, b = ISO_A[key]
    elif key in ISO_ELONGATED:
        a, b = ISO_ELONGATED[key]
    else:
        m = re.fullmatch(r"(A[0-4])x(\d+)", key)
        if not m:
            raise ValueError(f"Nieznany format {fmt_name!r}")
        s, l = ISO_A[m.group(1)]
        a, b = l, s * int(m.group(2))
    short, long_ = min(a, b), max(a, b)
    if orientation is None:
        orientation = "portrait" if key == "A4" else "landscape"
    return (long_, short) if orientation == "landscape" else (short, long_)


def fold_positions(W: float, H: float):
    """Linie składania do formatu A4 (sposób „do wpięcia” z marginesem 20 mm — praktyka DIN 824 forma A,
    uogólniona na formaty wydłużone i niestandardowe; PN-N-01603:1986 wycofana — przywołanie informacyjne).
    Zwraca (xs od lewej krawędzi, ys od dolnej krawędzi) [mm]. Geometria harmonijki i jej ocena:
    ``lamela.draft.skladanie`` (pasy w parach równych, pas z tabliczką ≥ 190 mm na wierzchu)."""
    from .skladanie import fold_positions as _fp
    return _fp(W, H)


# Znaki centrujące — ISO 5457:1999 p. 4.3 (PN-EN ISO 5457:2002; tekst sprawdzony na próbce normy, rejestr R4-B04):
# cztery znaki na końcach osi symetrii arkusza obciętego (tolerancja 1 mm); „kształt znaków dowolny; zaleca się
# linie ciągłe 0,7 mm od pola siatki odniesień, wchodzące 10 mm za ramkę pola rysunkowego”.
ZNAK_CENTR_DL = 10.0          # zalecana długość wejścia za ramkę [mm]
ZNAK_CENTR_GR = 0.7           # grubość linii [mm]
ZNAK_CENTR_ODSTEP = 1.5       # najmniejszy odstęp treści od znaku [mm]
ZNAK_CENTR_MIN = 2.0          # krótszego wejścia za ramkę nie rysuje się — znak kończy się na ramce


def znaki_centrujace(W: float, H: float, frame, glebokosc: dict | None = None) -> dict:
    """Odcinki znaków centrujących: {strona: (punkt na krawędzi arkusza, koniec za ramką)}; strony ``g`` (góra),
    ``d`` (dół), ``l`` (lewo), ``p`` (prawo). ``glebokosc`` — wejście za ramkę [mm] dla stron (domyślnie 10)."""
    x0, y0, x1, y1 = frame
    g = {s: ZNAK_CENTR_DL for s in "gdlp"}
    g.update({k: float(v) for k, v in (glebokosc or {}).items() if k in g})
    cx, cy = W / 2.0, H / 2.0
    return {"d": ((cx, 0.0), (cx, y0 + g["d"])), "g": ((cx, H), (cx, y1 - g["g"])),
            "l": ((0.0, cy), (x0 + g["l"], cy)), "p": ((W, cy), (x1 - g["p"], cy))}


# ------------------------------------------------------------------------------------------------ tabliczka
DO_UZUP = "[DO UZUPEŁNIENIA]"                          # konwencja znaczników — rejestr wymagań, sekcja E.1
SPRAWDZAJACY_ND = "nie dotyczy (art. 20 ust. 3 pkt 2 PB)"   # W-305: dom jednorodzinny — bez sprawdzającego


@dataclass
class Osoba:
    """Wiersz metryki w tabliczce (RPB § 10 ust. 1 pkt 3). Dane osób nie są fabrykowane: pola bez danych
    niosą znacznik ``[DO UZUPEŁNIENIA]`` (W-320), a nie pozostają puste."""
    funkcja: str
    imie_nazwisko: str = DO_UZUP
    specjalnosc_uprawnienia: str = DO_UZUP
    data: str = ""


def _osoby_domyslne():
    return [Osoba("Projektant"), Osoba("Projektant (wsp.)"),
            Osoba("Sprawdzający", imie_nazwisko=SPRAWDZAJACY_ND, specjalnosc_uprawnienia="—"),
            Osoba("Opracował")]


@dataclass
class TitleBlock:
    pracownia: str = ""
    pracownia_adres: str = ""
    inwestor: str = ""
    obiekt: str = ""
    lokalizacja: str = ""        # adres; nr działki, obręb, jednostka ewidencyjna
    kategoria: str = ""          # kategoria obiektu budowlanego (zał. do Prawa budowlanego)
    stadium: str = ""            # np. PB, PT, PW
    branza: str = ""
    tytul: str = ""
    skala: str = ""
    nr_rysunku: str = ""
    format: str = ""             # uzupełniany automatycznie
    data: str = ""
    rewizja: str = ""
    arkusz: str = ""             # nr arkusza / liczba arkuszy (ISO 7200), np. "1/3"
    rodzaj: str = ""             # rodzaj dokumentu (ISO 7200): rzut / przekrój / elewacja / zestawienie / schemat
    sprawdzenie: bool = True     # False — bez wiersza "Sprawdzający" (art. 20 ust. 3 pkt 2 PB, R4 pkt 3.1)
    osoby: list = field(default_factory=_osoby_domyslne)
    rewizje: list = field(default_factory=list)   # [(rew, opis, data), ...] — tabela zmian nad tabliczką


TB_WIDTH = 180.0  # PN-EN ISO 7200: szerokość tabliczki ≤ 180 mm


def wrap(s: str, max_w: float, h: float, style: str = "normal") -> list[str]:
    words = s.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if T.width(t, h, style) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def fit(s: str, max_w: float, h: float, min_h: float = 1.8, style: str = "normal") -> float:
    """Największa wysokość pisma z szeregu ISO 3098 (≤ h, ≥ min_h), przy której napis mieści się w max_w
    (jeśli nie mieści się nawet przy min_h — zwraca min_h)."""
    for hh in reversed(styles.TEXT_SERIES):
        if hh > h + 1e-6 or hh < min_h - 1e-6:
            continue
        if T.width(s, hh, style) <= max_w:
            return hh
    return min_h


# ------------------------------------------------------------------------------------------------ arkusz
class Sheet(SheetBase):
    """Arkusz rysunkowy z ramką, znakami składania i tabliczką.

    >>> sh = Sheet("A3", title_block=TitleBlock(tytul="RZUT PARTERU", skala="1:50", nr_rysunku="A-01"))
    >>> vp = sh.add_viewport(50, "RZUT PARTERU")
    >>> ... rysowanie w vp (metry) ...
    >>> sh.place(vp, sh.frame[0] + 10, sh.frame[3] - 10, "tl")
    >>> sh.save("wyniki/A-01")      # .dxf .pdf .png
    """

    def __init__(self, fmt_name: str = "A3", orientation: str | None = None, title_block: TitleBlock | None = None,
                 binding: float = 20.0, margin: float = 10.0, fold_marks: bool = True, centring_marks: bool = True,
                 grid_reference: bool | None = None, draw_frame: bool = True):
        W, H = sheet_size(fmt_name, orientation)
        super().__init__(W, H)
        self.custom = custom_size(fmt_name) is not None          # format niestandardowy (wymiary „na miarę”)
        self.fmt_name = f"{W:.0f}×{H:.0f}" if self.custom else str(fmt_name).replace("x", "×").replace("X", "×")
        self.frame = (binding, margin, W - margin, H - margin)  # x0, y0, x1, y1
        self.tb = title_block
        self.tb_rect = None
        self.znaki = {}                                          # znaki centrujące {strona: PLine}
        self.meta = {"title": title_block.tytul if title_block else "", "nr": title_block.nr_rysunku if title_block else ""}
        if draw_frame:
            self._draw_frame(fold_marks, centring_marks, grid_reference)
        if title_block is not None:
            if not title_block.format:
                title_block.format = self.fmt_name
            self.tb_rect = draw_title_block(self, title_block)

    # ------------------------------------------------------------------ ramka
    def _draw_frame(self, fold_marks, centring_marks, grid_reference):
        W, H = self.width, self.height
        x0, y0, x1, y1 = self.frame
        with self.on("R-RAMKA"):
            self.rect(x0, y0, x1, y1, pen=0.7)
            if centring_marks:  # PN-EN ISO 5457 4.3: na osiach symetrii arkusza, 0,7 mm, 10 mm za ramkę
                # (``centring_marks`` jako słownik {strona: mm} — krótsze wejście za ramkę; patrz
                # ``przytnij_znaki_centrujace``)
                gl = centring_marks if isinstance(centring_marks, dict) else None
                for s, (p0, p1) in znaki_centrujace(W, H, self.frame, gl).items():
                    self.znaki[s] = self.line(p0, p1, pen=ZNAK_CENTR_GR)
            if fold_marks:
                xs, ys = fold_positions(W, H)
                for x in xs:
                    self.line((x, 0.0), (x, min(5.0, y0)), pen=0.35)
                    self.line((x, H), (x, H - min(5.0, H - y1)), pen=0.35)
                for y in ys:
                    self.line((0.0, y), (min(5.0, x0), y), pen=0.35)
                    self.line((W, y), (W - min(5.0, W - x1), y), pen=0.35)
                # numery zgięć na marginesie (kolejność składania: pionowe od prawej — od pasa z tabliczką,
                # potem poziome od dołu); pismo 1,8 mm przy dolnej / lewej krawędzi arkusza
                for i, x in enumerate(sorted(xs, reverse=True)):
                    self.text((x + 0.8, 0.8), str(i + 1), 1.8)
                for j, y in enumerate(ys):
                    self.text((0.8, y + 0.8), str(len(xs) + j + 1), 1.8)
            if grid_reference is None:
                grid_reference = W * H >= 420 * 594 - 1   # R4 pkt 3.1: A2 i większe
            if grid_reference:
                self._grid_reference()
        # oznaczenie formatu w dolnym marginesie przy prawym rogu (PN-EN ISO 5457 / R4-B07)
        lab = (f"nst. {self.fmt_name}" if getattr(self, "custom", False)      # format niestandardowy (krótko:
               else f"{self.fmt_name} ({int(round(W))}×{int(round(H))})")     # nie wchodzi na numery siatki)
        # numery pól siatki w dolnym marginesie stoją na wysokości y0 − 5 (pismo 3,5 mm) — napis formatu pod nimi,
        # przy krawędzi arkusza, aby nie nachodził na numer ostatniego pola (weryfikacja PT: „18” na „A3×3”)
        y_lab = y0 / 2.0
        if getattr(self, "_siatka_dol", False):
            y_lab = max(0.9 + 0.1, (y0 - 5.0 - 3.5 / 2.0 - 0.4) / 2.0)
        self.text((x1, y_lab), lab, 1.8, 0.0, "right", "middle", layer="R-RAMKA")

    def _grid_reference(self):
        """Siatka odniesień (PN-EN ISO 5457 4.4): pola 50 mm liczone od osi symetrii arkusza, różnice w polach
        narożnych; wiersze literami od góry (bez I i O), kolumny cyframi od lewej; znaki 3,5 mm, linie 0,35 mm.
        Na A4 opisy tylko u góry i z prawej."""
        W, H = self.width, self.height
        x0, y0, x1, y1 = self.frame
        letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        a4 = min(W, H) < 220 and max(W, H) < 310

        def splits(lo, hi, c):
            pos = [c]
            k = 1
            while c - 50 * k > lo + 25:
                pos.append(c - 50 * k)
                k += 1
            k = 1
            while c + 50 * k < hi - 25:
                pos.append(c + 50 * k)
                k += 1
            return sorted(pos)

        xs = splits(x0, x1, W / 2.0)
        ys = splits(y0, y1, H / 2.0)
        self._siatka_dol = not a4                   # numery kolumn także w dolnym marginesie (napis formatu niżej)
        with self.on("R-RAMKA"):
            for x in xs:
                if not a4:
                    self.line((x, y0), (x, y0 - 5.0), pen=0.35)
                self.line((x, y1), (x, y1 + 5.0), pen=0.35)
            for y in ys:
                if not a4:
                    self.line((x0, y), (x0 - 5.0, y), pen=0.35)
                self.line((x1, y), (x1 + 5.0, y), pen=0.35)
            bx = [x0] + xs + [x1]
            by = [y0] + ys + [y1]
            for i in range(len(bx) - 1):
                xm = (bx[i] + bx[i + 1]) / 2.0
                self.text((xm, y1 + 5.0), str(i + 1), 3.5, ha="center", va="middle")
                if not a4:
                    self.text((xm, y0 - 5.0), str(i + 1), 3.5, ha="center", va="middle")
            nrow = len(by) - 1
            for j in range(nrow):
                ym = (by[nrow - j] + by[nrow - j - 1]) / 2.0
                ch = letters[j % len(letters)]
                self.text((x1 + 5.0, ym), ch, 3.5, ha="center", va="middle")
                if not a4:
                    self.text((x0 - 5.0, ym), ch, 3.5, ha="center", va="middle")

    # ------------------------------------------------------------------ pola robocze
    @property
    def drawing_area(self):
        """Pole rysunkowe (wewnątrz ramki) [x0,y0,x1,y1]."""
        return self.frame

    def free_above_title_block(self):
        """Prostokąt nad tabliczką (x0, y0, x1, y1) — miejsce na legendę/uwagi."""
        x0, y0, x1, y1 = self.frame
        if not self.tb_rect:
            return (x1 - TB_WIDTH, y0, x1, y1)
        tx0, ty0, tx1, ty1 = self.tb_rect
        return (tx0, ty1, tx1, y1)

    # ------------------------------------------------------------------ znaki centrujące
    def przytnij_znaki_centrujace(self, odstep: float = ZNAK_CENTR_ODSTEP, min_gl: float = ZNAK_CENTR_MIN) -> dict:
        """Skraca wejście znaków centrujących za ramkę tak, aby nie dotykały treści (widoków, bloków, tabliczki):
        koniec znaku stoi ``odstep`` przed najbliższym elementem w pasie znaku; wejście krótsze niż ``min_gl`` —
        znak kończy się na ramce (część w marginesie zostaje; ISO 5457 4.3: kształt znaku dowolny, 10 mm za
        ramką — zalecenie). Wywoływać po narysowaniu całej treści. Zwraca {strona: wejście za ramkę [mm]}."""
        if not self.znaki:
            return {}
        x0, y0, x1, y1 = self.frame
        a = ZNAK_CENTR_GR / 2.0 + odstep
        L = ZNAK_CENTR_DL
        cx, cy = self.width / 2.0, self.height / 2.0
        pasy = {"g": (cx - a, y1 - L - odstep, cx + a, y1), "d": (cx - a, y0, cx + a, y0 + L + odstep),
                "l": (x0, cy - a, x0 + L + odstep, cy + a), "p": (x1 - L - odstep, cy - a, x1, cy + a)}
        pasy = {s: r for s, r in pasy.items() if s in self.znaki}
        gl = {s: L for s in pasy}
        for B in _obwiednie_w_pasach(self, pasy):          # (n, 4) obwiednie treści [mm arkusza]
            for s, r in pasy.items():
                m = (B[:, 0] < r[2]) & (B[:, 2] > r[0]) & (B[:, 1] < r[3]) & (B[:, 3] > r[1])
                if not m.any():
                    continue
                Bm = B[m]
                d = {"g": y1 - Bm[:, 3].max(), "d": Bm[:, 1].min() - y0, "l": Bm[:, 0].min() - x0,
                     "p": x1 - Bm[:, 2].max()}[s] - odstep
                gl[s] = min(gl[s], float(d))
        out = {}
        for s, d in gl.items():
            d = d if d >= min_gl - 1e-9 else 0.0
            out[s] = round(d, 1)
            p = self.znaki[s]
            end = {"g": (cx, y1 - d), "d": (cx, y0 + d), "l": (x0 + d, cy), "p": (x1 - d, cy)}[s]
            p.pts = np.array([p.pts[0], end], float)
        self.znaki_gl = out
        return out

    # ------------------------------------------------------------------ tytuł rzutni
    def view_title(self, vp: Viewport, text: str | None = None, scale: bool = True, where: str = "below",
                   dx: float = 0.0, dy: float = 0.0, h: float = 5.0, subtitle: str | None = None):
        """Tytuł rzutni (np. „RZUT PARTERU  1:50”) z podkreśleniem, pod lub nad rzutnią."""
        if vp.clip is None:
            raise ValueError("Najpierw umieść rzutnię (sheet.place)")
        x0, y0, x1, y1 = vp.clip
        title = text if text is not None else (vp.title or "")
        sc = fmt.scale_str(vp.scale) if scale else ""
        if where == "below":
            bx, by = x0 + dx, y0 - 7.0 + dy
        else:
            bx, by = x0 + dx, y1 + 3.0 + dy
        with self.on("R-OPISY"):
            self.text((bx, by), title, h, style="bold")
            w = T.width(title, h, "bold")
            if sc:
                self.text((bx + w + 3.0, by), sc, h * 0.7)
                w += 3.0 + T.width(sc, h * 0.7)
            self.line((bx, by - 1.5), (bx + w, by - 1.5), pen=0.5)
            sub = subtitle if subtitle is not None else vp.subtitle
            if sub:
                self.text((bx, by - 5.0), sub, 2.5)
        return (bx, by)

    # ------------------------------------------------------------------ zapis
    def save(self, base: str | Path, formats=("dxf", "pdf", "png"), dpi: int = 200, mode: str = "branze",
             dxf_mode: str = "layout") -> dict:
        """Zapisuje arkusz: ``base``.dxf / .pdf / .png. Zwraca słownik ścieżek."""
        from . import dxfout, render
        base = Path(base)
        base.parent.mkdir(parents=True, exist_ok=True)
        out = {}
        if "pdf" in formats or "png" in formats:
            pdf = base.with_suffix(".pdf")
            render.to_pdf(self, pdf, mode)
            out["pdf"] = str(pdf)
            if "png" in formats:
                png = base.with_suffix(".png")
                render.pdf_to_png(pdf, png, dpi)
                out["png"] = str(png)
            if "pdf" not in formats:
                pdf.unlink()
                out.pop("pdf")
        if "dxf" in formats:
            dxf = base.with_suffix(".dxf")
            dxfout.to_dxf(self, dxf, mode=dxf_mode)
            out["dxf"] = str(dxf)
        return out


def _obwiednie_w_pasach(sh, pasy: dict):
    """Obwiednie (n, 4) [mm arkusza] prymitywów treści arkusza i jego rzutni, leżących przy prostokątach ``pasy``
    [mm arkusza]. Pomijane: warstwa ramki (R-RAMKA), warstwy niedrukowane i same znaki centrujące. Linie łamane —
    obwiednia każdego odcinka osobno; tekst — prostokąt napisu; rzutnie — przycięte do okna rzutni."""
    from .core import PArc, PFill, PLine, PText, prim_points
    if not pasy:
        return
    R = np.array(list(pasy.values()), float)
    znaki = {id(p) for p in (getattr(sh, "znaki", None) or {}).values()}

    def boxes(prims, k, rects):
        rx0, ry0 = rects[:, 0].min(), rects[:, 1].min()
        rx1, ry1 = rects[:, 2].max(), rects[:, 3].max()
        out = []
        for p in prims:
            if id(p) in znaki or p.layer == "R-RAMKA":
                continue
            try:
                if not styles.layer(p.layer).plot:
                    continue
            except Exception:                          # noqa: BLE001 — warstwa spoza słownika: treść
                pass
            if isinstance(p, PLine):
                a = np.asarray(p.pts, float)
                if len(a) < 2:
                    continue
                if p.closed:
                    a = np.vstack([a, a[:1]])
                b = np.hstack([np.minimum(a[:-1], a[1:]), np.maximum(a[:-1], a[1:])])
            elif isinstance(p, (PText, PFill, PArc)):
                if isinstance(p, PText):               # szybki odsiew: punkt wstawienia daleko od pasów
                    rad = (len(p.string) + 2) * p.h * k
                    q = p.pos
                    if q[0] < rx0 - rad or q[0] > rx1 + rad or q[1] < ry0 - rad or q[1] > ry1 + rad:
                        continue
                pts = [np.asarray(x, float).reshape(-1, 2) for x in prim_points(p, k)]
                if not pts:
                    continue
                pts = np.vstack(pts)
                b = np.array([[pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()]])
            else:
                continue
            m = (b[:, 0] < rx1) & (b[:, 2] > rx0) & (b[:, 1] < ry1) & (b[:, 3] > ry0)
            if m.any():
                out.append(b[m])
        return np.vstack(out) if out else None

    b = boxes(sh.prims, sh.k, R)
    if b is not None:
        yield b
    for vp in getattr(sh, "viewports", []):
        c = vp.clip
        if c is None:
            continue
        Rc = np.column_stack([np.maximum(R[:, 0], c[0]), np.maximum(R[:, 1], c[1]), np.minimum(R[:, 2], c[2]),
                              np.minimum(R[:, 3], c[3])])
        Rc = Rc[(Rc[:, 2] > Rc[:, 0]) & (Rc[:, 3] > Rc[:, 1])]
        if not len(Rc):
            continue
        Rm = np.hstack([vp.to_model(Rc[:, :2]), vp.to_model(Rc[:, 2:])])
        b = boxes(vp.prims, vp.k, Rm)
        if b is None:
            continue
        bs = np.hstack([vp.to_sheet(b[:, :2]), vp.to_sheet(b[:, 2:])])
        bs = np.column_stack([np.maximum(bs[:, 0], c[0]), np.maximum(bs[:, 1], c[1]), np.minimum(bs[:, 2], c[2]),
                              np.minimum(bs[:, 3], c[3])])
        bs = bs[(bs[:, 2] >= bs[:, 0]) & (bs[:, 3] >= bs[:, 1])]
        if len(bs):
            yield bs


# ------------------------------------------------------------------------------------------------ rysowanie tabliczki
def _cell(sh, x, y, w, h, label, value="", vh=2.5, style="normal", lines_max=1, align="left", label_h=1.8,
          value_dy=None):
    """Komórka tabliczki: nazwa pola małym pismem u góry, treść niżej (dopasowana do szerokości)."""
    pad = 1.2
    if label:
        sh.text((x + pad, y + h - pad - label_h), label, label_h, layer="R-TABLICZKA")
    if not value:
        return
    avail = w - 2 * pad
    top = y + h - (pad + label_h + 0.7 if label else pad)
    if lines_max <= 1:
        hh = fit(value, avail, vh, 1.8, style)
        hh = styles.snap_text_h(min(hh, max(1.8, (top - y) - 1.0)))
        bot = y + max(0.9, 0.24 * hh + 0.5)
        yy = bot + max(0.0, (top - bot - hh) / 2.0) if value_dy is None else y + value_dy
        xx = x + pad if align == "left" else x + w / 2.0
        sh.text((xx, yy), value, hh, style=style, layer="R-TABLICZKA", ha="left" if align == "left" else "center")
    else:
        cands = [x for x in reversed(styles.TEXT_SERIES) if x <= vh + 1e-6] or [1.8]
        for hh in cands:
            ls = wrap(value, avail, hh, style)
            block = hh * 1.45 * (len(ls[:lines_max]) - 1) + hh
            if len(ls) <= lines_max and block <= (top - y) - (0.24 * hh + 0.5):
                break
        gap = hh * 1.45
        block = gap * (len(ls[:lines_max]) - 1) + hh
        bot = y + max(0.9, 0.24 * hh + 0.5)
        yy = bot + max(0.0, (top - bot - block) / 2.0) + block - hh
        for i, ln in enumerate(ls[:lines_max]):
            sh.text((x + pad, yy - i * gap), ln, hh, style=style, layer="R-TABLICZKA")


def draw_title_block(sh: Sheet, tb: TitleBlock):
    """Tabliczka rysunkowa w prawym dolnym rogu ramki. Zwraca jej prostokąt (x0, y0, x1, y1)."""
    fx0, fy0, fx1, fy1 = sh.frame
    W = TB_WIDTH
    x0 = fx1 - W
    # wysokości wierszy (od góry)
    rows = {"prac": 12.0, "inw": 8.0, "obj": 10.5, "lok": 9.0, "hdr": 4.5, "os": 7.0, "tyt": 12.0, "dol": 9.0}
    osoby = [o for o in tb.osoby if tb.sprawdzenie or not o.funkcja.lower().startswith("sprawdz")]
    n_os = len(osoby)
    Htot = rows["prac"] + rows["inw"] + rows["obj"] + rows["lok"] + rows["hdr"] + n_os * rows["os"] + rows["tyt"] + rows["dol"]
    y1 = fy0 + Htot
    ly = "R-TABLICZKA"
    thin, mid, thick = 0.18, 0.25, 0.5
    with sh.on(ly):
        # białe tło (gdyby rysunek zachodził) i obrys
        sh.fill(rect_pts(x0, fy0, fx1, y1), ly, "#ffffff", z=28.5)
        y = y1
        # --- pracownia | stadium | branża
        h = rows["prac"]
        y -= h
        _cell(sh, x0, y, 110, h, "PRACOWNIA PROJEKTOWA", "", 0)
        if tb.pracownia:
            hh = fit(tb.pracownia, 106, 3.5, 2.0, "bold")
            sh.text((x0 + 1.2, y + h - 1.2 - 1.8 - 1.4 - hh), tb.pracownia, hh, style="bold")
        if tb.pracownia_adres:
            hh = fit(tb.pracownia_adres, 106, 2.0, 1.8)
            sh.text((x0 + 1.2, y + 1.4), tb.pracownia_adres, hh)
        _cell(sh, x0 + 110, y, 25, h, "STADIUM", tb.stadium, 5.0, "bold", align="center")
        _cell(sh, x0 + 135, y, 45, h, "BRANŻA", tb.branza, 2.5, "bold", lines_max=2)
        sh.line((x0 + 110, y), (x0 + 110, y + h), pen=mid)
        sh.line((x0 + 135, y), (x0 + 135, y + h), pen=mid)
        sh.line((x0, y), (fx1, y), pen=mid)
        # --- inwestor
        h = rows["inw"]
        y -= h
        _cell(sh, x0, y, W, h, "INWESTOR", tb.inwestor, 2.5)
        sh.line((x0, y), (fx1, y), pen=thin)
        # --- obiekt
        h = rows["obj"]
        y -= h
        _cell(sh, x0, y, W, h, "OBIEKT / NAZWA ZAMIERZENIA BUDOWLANEGO", tb.obiekt, 2.5, "bold", lines_max=2)
        sh.line((x0, y), (fx1, y), pen=thin)
        # --- lokalizacja | kategoria
        h = rows["lok"]
        y -= h
        _cell(sh, x0, y, 150, h, "ADRES / LOKALIZACJA (NR DZIAŁKI, OBRĘB, JEDN. EWIDENCYJNA)", tb.lokalizacja, 2.2,
              lines_max=2)
        _cell(sh, x0 + 150, y, 30, h, "KAT. OBIEKTU", tb.kategoria, 3.5, "bold", align="center")
        sh.line((x0 + 150, y), (x0 + 150, y + h), pen=thin)
        sh.line((x0, y), (fx1, y), pen=mid)
        # --- metryka: nagłówek
        cols = [("FUNKCJA", 27.0), ("IMIĘ I NAZWISKO", 43.0), ("SPECJALNOŚĆ, NR UPRAWNIEŃ", 55.0), ("DATA", 20.0),
                ("PODPIS", 35.0)]
        h = rows["hdr"]
        y -= h
        xx = x0
        for name, w in cols:
            sh.text((xx + w / 2.0, y + h / 2.0), name, 1.8, ha="center", va="middle")
            xx += w
        sh.line((x0, y), (fx1, y), pen=thin)
        y_hdr_top = y + h
        # --- osoby
        h = rows["os"]
        for o in osoby:
            y -= h
            vals = [o.funkcja, o.imie_nazwisko, o.specjalnosc_uprawnienia, o.data, ""]
            xx = x0
            for (name, w), v in zip(cols, vals):
                if v:
                    if name == "SPECJALNOŚĆ, NR UPRAWNIEŃ":
                        ls = wrap(v, w - 2.4, 1.8)
                        if len(ls) > 1:
                            sh.text((xx + 1.2, y + h / 2.0 + 0.4), ls[0], 1.8)
                            sh.text((xx + 1.2, y + h / 2.0 - 2.6), " ".join(ls[1:]), fit(" ".join(ls[1:]), w - 2.4, 1.8))
                        else:
                            sh.text((xx + 1.2, y + h / 2.0), v, 1.8, va="middle")
                    else:
                        hh = fit(v, w - 2.4, 2.5 if name != "FUNKCJA" else 2.2)
                        sh.text((xx + 1.2, y + h / 2.0), v, hh, va="middle", style="normal")
                xx += w
            sh.line((x0, y), (fx1, y), pen=thin)
        xx = x0
        for name, w in cols[:-1]:
            xx += w
            sh.line((xx, y), (xx, y_hdr_top), pen=thin)
        sh.line((x0, y), (fx1, y), pen=mid)
        # --- tytuł rysunku
        h = rows["tyt"]
        y -= h
        _cell(sh, x0, y, W, h, "TYTUŁ RYSUNKU", tb.tytul, 5.0, "bold", lines_max=2)
        sh.line((x0, y), (fx1, y), pen=mid)
        # --- skala | format | data | nr rysunku | rewizja
        h = rows["dol"]
        y -= h
        bottom = [("SKALA", tb.skala, 24.0, "bold", 3.5), ("FORMAT", tb.format, 16.0, "normal", 2.5),
                  ("DATA WYDANIA", tb.data, 24.0, "normal", 2.5), ("RODZAJ DOK.", tb.rodzaj, 28.0, "normal", 2.5),
                  ("NR RYSUNKU", tb.nr_rysunku, 52.0, "bold", 5.0), ("ARKUSZ", tb.arkusz, 18.0, "normal", 2.5),
                  ("REW.", tb.rewizja, 18.0, "bold", 3.5)]
        xx = x0
        for i, (lab, val, w, st, vh) in enumerate(bottom):
            _cell(sh, xx, y, w, h, lab, val, vh, st, align="center")
            if i:
                sh.line((xx, y), (xx, y + h), pen=mid)
            xx += w
        # obrys zewnętrzny
        sh.rect(x0, fy0, fx1, y1, pen=thick)
        # --- tabela zmian (rewizji) nad tabliczką
        top = y1
        if tb.rewizje:
            rh = 5.0
            cw = [(18.0, "REW."), (122.0, "OPIS ZMIANY"), (40.0, "DATA")]
            yy = top
            sh.fill(rect_pts(x0, top, fx1, top + rh * (len(tb.rewizje) + 1)), ly, "#ffffff", z=28.5)
            for row in list(reversed(tb.rewizje)) + [None]:
                vals = [c[1] for c in cw] if row is None else list(row)
                xx = x0
                for (w, _n), v in zip(cw, vals):
                    sh.text((xx + 1.2, yy + rh / 2.0), str(v), 1.8 if row is None else 2.5, va="middle")
                    xx += w
                yy += rh
                sh.line((x0, yy), (fx1, yy), pen=thin)
            xx = x0
            for w, _n in cw[:-1]:
                xx += w
                sh.line((xx, top), (xx, yy), pen=thin)
            sh.rect(x0, top, fx1, yy, pen=mid)
            top = yy
    return (x0, fy0, fx1, top)


# ------------------------------------------------------------------------------------------------ bloki tekstowe
def notes_box(sh: Sheet, x: float, y_top: float, w: float, lines: list[str], title: str = "UWAGI", h: float = 2.5,
              numbered: bool = True, frame: bool = True, layer: str = "R-OPISY", start: int = 1) -> tuple:
    """Blok uwag (zawijany do szerokości w). ``start`` — numer pierwszej uwagi (ciąg dalszy bloku podzielonego
    na kolumny). Zwraca prostokąt (x0, y0, x1, y1)."""
    pad = 2.0
    y = y_top - pad - 3.5
    with sh.on(layer):
        if title:
            sh.text((x + pad, y), title, 3.5, style="bold")
            y -= 3.5 * 1.8
        for i, ln in enumerate(lines):
            prefix = f"{i + start}. " if numbered else ""
            ind = T.width(prefix, h) if prefix else 0.0
            ls = wrap(ln, w - 2 * pad - ind, h)
            for j, s in enumerate(ls):
                if j == 0 and prefix:
                    sh.text((x + pad, y), prefix, h)
                sh.text((x + pad + ind, y), s, h)
                y -= h * 1.6
            y -= h * 0.3
        y0 = y + h * 0.9
        if frame:
            sh.rect(x, y0 - pad + 1.0, x + w, y_top, pen=0.25)
    return (x, y0 - pad + 1.0, x + w, y_top)


def table(sh, x: float, y_top: float, cols: list[tuple[str, float]], rows: list[list[str]], h: float = 2.5,
          row_h: float = 5.0, title: str | None = None, layer: str = "R-OPISY", align: list[str] | None = None,
          header_h: float | None = None, zawijaj=False) -> tuple:
    """Prosta tabela (np. zestawienie pomieszczeń, stolarki). cols: [(nagłówek, szerokość), …].

    Tekst komórki jest zmniejszany (``fit``: szereg ISO 3098 do 1,8 mm). ``zawijaj=True`` — gdy nie mieści się
    nawet przy 1,8 mm, jest łamany na wiersze (najpierw w wysokości wiersza tabeli, potem wiersz rośnie), zamiast
    wychodzić na sąsiednią kolumnę; ``zawijaj="wiersze"`` — tekst dłuższy niż kolumna łamany pismem ``h`` (bez
    zmniejszania; jednolite pismo kolumny, np. tytuły w spisie rysunków). Bez przepełnień tabela jest identyczna
    jak przy ``zawijaj=False``."""
    W = sum(w for _n, w in cols)
    y = y_top
    header_h = header_h or row_h
    with sh.on(layer):
        if title:
            sh.text((x, y + 2.0), title, 3.5, style="bold")
        sh.fill(rect_pts(x, y - header_h, x + W, y), layer, "#eeeeee", z=5)
        xx = x
        for name, w in cols:
            ls = name.split("\n")
            for i, s_ in enumerate(ls):
                yy = y - header_h / 2.0 + (len(ls) - 1) * 1.3 - i * 2.6
                sh.text((xx + w / 2.0, yy), s_, 1.8, ha="center", va="middle", style="bold")
            xx += w
        y -= header_h
        sh.line((x, y), (x + W, y), pen=0.25)
        for r in rows:
            cells = []
            rh = row_h
            for (name, w), v in zip(cols, r):
                v = str(v)
                hh = fit(v, w - 2.0, h)
                ls = [v]
                if zawijaj == "wiersze" and T.width(v, h) > w - 2.0 + 1e-6:
                    ls = wrap(v, w - 2.0, h)
                    hh = h if all(T.width(s_, h) <= w - 2.0 + 1e-6 for s_ in ls) else 1.8
                    ls = wrap(v, w - 2.0, hh)
                    rh = max(rh, (len(ls) - 1) * hh * 1.45 + hh + 2.2)
                elif zawijaj and T.width(v, hh) > w - 2.0 + 1e-6:
                    hh, ls = _zawin_komorke(v, w - 2.0, h, row_h)
                    rh = max(rh, (len(ls) - 1) * hh * 1.45 + hh + 2.2)
                cells.append((hh, ls))
            xx = x
            for i, ((name, w), (hh, ls)) in enumerate(zip(cols, cells)):
                a = (align[i] if align else ("left" if i else "center"))
                lh = hh * 1.45
                for j, v in enumerate(ls):
                    yy = y - rh / 2.0 + (len(ls) - 1) * lh / 2.0 - j * lh
                    if a == "left":
                        sh.text((xx + 1.0, yy), v, hh, va="middle")
                    elif a == "right":
                        sh.text((xx + w - 1.0, yy), v, hh, va="middle", ha="right")
                    else:
                        sh.text((xx + w / 2.0, yy), v, hh, va="middle", ha="center")
                xx += w
            y -= rh
            sh.line((x, y), (x + W, y), pen=0.13)
        xx = x
        for name, w in cols[:-1]:
            xx += w
            sh.line((xx, y), (xx, y_top), pen=0.13)
        sh.rect(x, y, x + W, y_top, pen=0.35)
    return (x, y, x + W, y_top)


def _zawin_komorke(v: str, avail: float, h: float, row_h: float) -> tuple[float, list[str]]:
    """(wysokość pisma, wiersze) tekstu komórki łamanego do szerokości ``avail``: największe pismo z szeregu
    ISO 3098 (≤ h, ≥ 1,8 mm), przy którym wiersze mieszczą się w wysokości wiersza tabeli; inaczej 1,8 mm."""
    for hh in [x for x in reversed(styles.TEXT_SERIES) if 1.8 - 1e-6 <= x <= h + 1e-6]:
        ls = wrap(v, avail, hh)
        if all(T.width(s_, hh) <= avail + 1e-6 for s_ in ls) and (len(ls) - 1) * hh * 1.45 + hh <= row_h - 2.2:
            return hh, ls
    return 1.8, wrap(v, avail, 1.8)


def scale_bar(c, pos, scale: float, length_m: float | None = None, h: float = 1.8, layer: str = "R-OPISY",
              unit_label: str = "m"):
    """Podziałka liniowa (PN-EN ISO 5455 / praktyka kartograficzna) rysowana NA ARKUSZU dla rzutni 1:scale.

    Segmenty naprzemiennie czarne/białe; pierwszy segment podzielony na części. ``pos`` = lewy dolny róg [mm]."""
    if length_m is None:
        # długość „ładna” (1-2-2,5-5) taka, by cała podziałka (z odcinkiem dzielonym) miała ≤ 125 mm na papierze:
        # 1:5 → 0,5 m, 1:10 → 1 m, 1:20 → 2 m, 1:50 → 5 m, 1:100 → 10 m, 1:500 → 50 m (jak dotąd dla skal 1:50+)
        lim = 125.0 * scale / 1000.0 / 1.2
        nice = [0.05, 0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 10.0, 20.0, 25.0, 50.0, 100.0, 200.0, 250.0, 500.0]
        length_m = max([v for v in nice if v <= lim + 1e-9] or [nice[0]])
    mm_per_m = 1000.0 / scale
    n = 5
    step = length_m / n
    x0, y0 = pos
    bh = 1.6
    with c.on(layer):
        # pierwszy segment podzielony na 5 części (lewo od zera)
        sub = step / 5.0
        for i in range(5):
            xa = x0 + i * sub * mm_per_m
            xb = xa + sub * mm_per_m
            if i % 2 == 0:
                c.fill(rect_pts(xa, y0, xb, y0 + bh), layer, "#000000")
        c.rect(x0, y0, x0 + step * mm_per_m, y0 + bh, pen=0.18)
        xz = x0 + step * mm_per_m
        for i in range(n):
            xa = xz + i * step * mm_per_m
            xb = xa + step * mm_per_m
            if i % 2 == 1:
                c.fill(rect_pts(xa, y0, xb, y0 + bh), layer, "#000000")
            c.rect(xa, y0, xb, y0 + bh, pen=0.18)
        c.text((x0, y0 + bh + 1.0), fmt.num(step, 2, strip=True), h, ha="center")
        for i in range(n + 1):
            v = i * step
            c.text((xz + i * step * mm_per_m, y0 + bh + 1.0), fmt.num(v, 2, strip=True), h, ha="center")
        c.text((xz + n * step * mm_per_m + 2.0, y0), unit_label, h)
        c.text((x0, y0 - 1.2 - h), "PODZIAŁKA " + fmt.scale_str(scale), h, style="bold")
    return (x0, y0, xz + n * step * mm_per_m + 4.0, y0 + bh + 1.0 + h)


def control_segment(sh: Sheet, pos, length: float = 100.0, h: float = 1.8, vertical: bool = False,
                    tekst_obok: bool = False):
    """Odcinek kontrolny wydruku (np. 100 mm) — do sprawdzenia, czy arkusz wydrukowano w skali 1:1.
    ``vertical=True`` — pionowo (np. w marginesie na oprawę). ``tekst_obok`` — napis równolegle do odcinka, po
    stronie kresek podziału (zamiast za jego końcem, np. gdy tam jest znak centrujący)."""
    if tekst_obok:
        x, y = pos
        P = np.array([x, y], float)
        d = np.array([0.0, 1.0]) if vertical else np.array([1.0, 0.0])
        n = np.array([-1.0, 0.0]) if vertical else np.array([0.0, 1.0])
        with sh.on("R-OPISY"):
            sh.line(P, P + d * length, pen=0.35)
            for i in range(0, int(length) + 1, 10):
                t = 1.6 if i % 50 == 0 else 0.9
                sh.line(P + d * i, P + d * i + n * t, pen=0.18)
            q = P + n * (1.6 + 0.9) + d * 2.0
            sh.text(q, f"odcinek kontrolny {int(length)} mm (wydruk 1:1)", h, 90.0 if vertical else 0.0, "left",
                    "baseline")
        return
    x, y = pos
    d = np.array([0.0, 1.0]) if vertical else np.array([1.0, 0.0])
    n = np.array([-1.0, 0.0]) if vertical else np.array([0.0, 1.0])
    P = np.array([x, y], float)
    with sh.on("R-OPISY"):
        sh.line(P, P + d * length, pen=0.35)
        for i in range(0, int(length) + 1, 10):
            t = 1.6 if i % 50 == 0 else 0.9
            sh.line(P + d * i, P + d * i + n * t, pen=0.18)
        sh.text(P + d * (length + 1.5), f"odcinek kontrolny {int(length)} mm (wydruk 1:1)", h,
                90.0 if vertical else 0.0, "left", "middle" if not vertical else "top")


LINE_LEGEND = [
    # (opis, rodzaj linii, rola pióra, zastosowanie)
    ("ciągła bardzo gruba", "CIAGLA", "b_gruba", "kontury przekroju bez kreskowania, pręty zbrojeniowe, izolacje przeciwwodne"),
    ("ciągła gruba", "CIAGLA", "gruba", "kontury elementów konstrukcyjnych w przekroju (z kreskowaniem)"),
    ("ciągła średnia", "CIAGLA", "srednia", "warstwy nienośne w przekroju, stolarka, krawędzie widoczne bliskie"),
    ("ciągła cienka", "CIAGLA", "cienka", "wymiary, linie pomocnicze, odnośniki, wyposażenie, krawędzie widoczne"),
    ("ciągła bardzo cienka", "CIAGLA", "b_cienka", "kreskowanie materiałów, meble"),
    ("kreskowa cienka", "KRESKOWA", "cienka", "krawędzie niewidoczne, elementy nad płaszczyzną cięcia"),
    ("punktowa cienka", "PUNKTOWA", "cienka", "osie konstrukcyjne, osie symetrii"),
    ("punktowa gruba (krótka)", "PUNKTOWA_KROTKA", "gruba", "ślad płaszczyzny przekroju (końce i załamania)"),
    ("dwupunktowa", "DWUPUNKTOWA", "gruba", "granice działki, elementy usuwane/projektowane, skrajne położenia"),
    ("kropkowa", "KROPKOWA", "cienka", "elementy pomocnicze, zakres robót"),
]


def lines_legend(c, x: float, y_top: float, entries=None, scales=(20, 50, 100, 500), h: float = 1.8,
                 title: str = "RODZAJE I GRUBOŚCI LINII (PN-EN ISO 128-2, grupy linii wg podziałki)",
                 layer: str = "R-LEGENDA"):
    """Tabela rodzajów linii: próbka, nazwa, zastosowanie i grubości [mm] w podziałkach ``scales``."""
    from .styles import pen_mm
    entries = entries or LINE_LEGEND
    cols = [("Próbka", 30.0), ("Rodzaj linii", 38.0), ("Zastosowanie", 108.0)] + [(f"1:{s}", 13.0) for s in scales]
    W = sum(w for _n, w in cols)
    rh = 5.5
    with c.on(layer):
        c.text((x, y_top + 2.0), title, 3.5, style="bold")
        y = y_top
        c.fill(rect_pts(x, y - rh, x + W, y), layer, "#eeeeee", z=5)
        xx = x
        for n, w in cols:
            c.text((xx + w / 2, y - rh / 2), n, 1.8, ha="center", va="middle", style="bold")
            xx += w
        y -= rh
        for (name, lt, role, use) in entries:
            ym = y - rh / 2
            c.line((x + 3, ym), (x + 27, ym), layer, pen=pen_mm(role, 50), lt=None if lt == "CIAGLA" else lt,
                   color="#000000", z=22)
            c.text((x + 31, ym), name, h, va="middle")
            c.text((x + 69, ym), use, fit(use, 106, h), va="middle")
            xx = x + 176
            for sc in scales:
                c.text((xx + 6.5, ym), fmt.num(pen_mm(role, sc), 2), h, ha="center", va="middle")
                xx += 13
            y -= rh
            c.line((x, y), (x + W, y), pen=0.13)
        xx = x
        for n, w in cols[:-1]:
            xx += w
            c.line((xx, y), (xx, y_top), pen=0.13)
        c.rect(x, y, x + W, y_top, pen=0.35)
    return (x, y, x + W, y_top)


def lettering_sample(c, x: float, y_top: float, heights=(1.8, 2.5, 3.5, 5.0, 7.0), layer: str = "R-LEGENDA"):
    """Próbka pisma (PN-EN ISO 3098: h = wysokość wielkich liter) z polskimi znakami diakrytycznymi."""
    y = y_top
    with c.on(layer):
        c.text((x, y + 2.0), "PISMO (PN-EN ISO 3098; Liberation Sans — metrycznie zgodna z Arial)", 3.5,
               style="bold")
        y -= 3.0
        for hh in heights:
            y -= hh * 1.6
            c.text((x, y), f"h = {fmt.num(hh, 1)} mm", 1.8)
            c.text((x + 22, y), None, hh, runs=[("ĄĆĘŁŃÓŚŹŻ ąćęłńóśźż 0123456789 ±0,00 −1,20 24", 1.0, 0.0),
                                                 ("5", T.SUP_SIZE, T.SUP_RAISE)])
    return (x, y - 2.0, x + 200, y_top)
