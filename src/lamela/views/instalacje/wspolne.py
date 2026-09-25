"""Wspólne elementy generatora rzutów instalacji: warstwy podkładu, wynik widoku, rejestr braków danych modelu,
opisy wzdłuż tras i legenda symboli (bloki kolumny opisowej arkusza)."""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ...draft import styles
from ...draft import text as T
from ...draft.geom import dir_deg, perp, readable_angle, unit
from ...draft.sheet import wrap

# ------------------------------------------------------------------------------------------------ warstwy
_L = styles.LayerDef
for _ld in [
    _L("I-PODKLAD", "Podkład architektoniczny — rzut AR (szary, cienki)", "b_cienka", aci=8, plot_rgb="#9a9a9a", z=8),
    _L("I-PODKLAD-SCIANY", "Podkład architektoniczny — kontury ścian przeciętych", "cienka", aci=8, plot_rgb="#6e6e6e",
       z=9),
    _L("I-PODKLAD-WYPELN", "Podkład architektoniczny — wypełnienie ścian przeciętych", "b_cienka", aci=254,
       plot_rgb="#e6e6e6", z=3),
    _L("I-POMIESZCZENIA", "Podkład — numery i nazwy pomieszczeń", "cienka", aci=8, plot_rgb="#4a4a4a", z=26),
    _L("I-OSIE", "Podkład — osie konstrukcyjne", "b_cienka", "PUNKTOWA", aci=8, plot_rgb="#7a7a7a", z=12),
    _L("I-BRAKI", "Elementy do uzupełnienia w modelu [DO UZUPEŁNIENIA] / proponowane", "cienka", "KRESKOWA", aci=6,
       plot_rgb="#b0008a", z=27),
    _L("E-PV", "Instalacja fotowoltaiczna: moduły, trasy DC", "srednia", aci=200, plot_rgb="#5b2c83", z=24),
    _L("E-ALARM", "Sygnalizacja włamania i napadu (SSWiN), czujki", "srednia", aci=5, plot_rgb="#1f5fa8", z=24),
    _L("S-PC", "Pompa ciepła — przewody czynnika grzewczego (zasilanie/powrót)", "srednia", aci=1, plot_rgb="#c0392b",
       z=23),
]:
    styles.LAYERS.setdefault(_ld.name, _ld)

GRAY = "#8c8c8c"
BRAK = "[DO UZUPEŁNIENIA]"
H_S, H_M, H_L = 1.8, 2.5, 3.5          # wysokości pisma (PN-EN ISO 3098)


# ------------------------------------------------------------------------------------------------ wynik widoku
@dataclass
class InstResult:
    """Wynik widoku instalacji (kontrakt ``sheets.register_view``)."""
    notes: list = field(default_factory=list)
    column_blocks: list = field(default_factory=list)
    north: bool = False
    units_note: str | None = None
    bez_skali: bool = False
    hatch_mats: dict = field(default_factory=dict)
    rooms: list = field(default_factory=list)
    obliczenia: dict = field(default_factory=dict)       # wyniki obliczeń pokazane na rysunku (raport)
    kolizje: int = 0                                     # liczba kolizji napisów (kontrola)


# ------------------------------------------------------------------------------------------------ braki danych
class Braki:
    """Rejestr braków danych modelu per branża ('IS' | 'IE'): (element, opis, proponowany format)."""

    def __init__(self):
        self.items: dict[str, dict] = {"IS": {}, "IE": {}}

    def add(self, br: str, element: str, opis: str, fmt_: str = "", arkusz: str = ""):
        key = (element, opis)
        d = self.items.setdefault(br, {})
        if key not in d:
            d[key] = dict(element=element, opis=opis, format=fmt_, arkusze=set())
        if arkusz:
            d[key]["arkusze"].add(arkusz)

    def markdown(self, br: str, tytul: str, zrodla: str) -> str:
        rows = list(self.items.get(br, {}).values())
        out = [f"# Braki danych modelu — {tytul}", "",
               "Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy "
               "narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) "
               "wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.", "",
               f"Źródła: {zrodla}.", "", "| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |",
               "|---:|:---|:---|:---|:---|"]
        for i, r in enumerate(sorted(rows, key=lambda r: r["element"])):
            ark = ", ".join(sorted(r["arkusze"])) or "—"
            esc = lambda t: str(t).replace("|", "\\|")      # noqa: E731 — „|” w komórkach tabeli Markdown
            out.append(f"| {i + 1} | {esc(r['element'])} | {esc(r['opis'])} | {esc(r['format'] or '—')} | {ark} |")
        out += ["", "Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie "
                "wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml "
                "--out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).", ""]
        return "\n".join(out)


def braki_of(ctx) -> Braki:
    b = getattr(ctx, "_inst_braki", None)
    if b is None:
        b = Braki()
        ctx._inst_braki = b
    return b


def zapisz_braki(ctx, br: str):
    """Zapis BRAKI_DANYCH.md (ścieżka z konfiguracji ``wspolne.braki_danych``) — nadpisywany przy każdym arkuszu."""
    path = ctx.cfg.get("braki_danych")
    if not path:
        return
    tyt = {"IS": "instalacje sanitarne (PT-IS)", "IE": "instalacje elektryczne (PT-IE)"}[br]
    src = ", ".join(f"`{p}`" for p in ("model/budynek.yaml", "model/instalacje.yaml", "model/wyposazenie.yaml",
                                        "model/dzialka.yaml"))
    try:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(braki_of(ctx).markdown(br, tyt, src), encoding="utf-8")
    except OSError as ex:  # pragma: no cover
        ctx.note("instalacje", f"nie zapisano {path}: {ex}")


# ------------------------------------------------------------------------------------------------ liczby
def num(x, nd=1) -> str:
    from ...draft import fmt
    return fmt.num(float(x), nd)


def rura_krotko(s: str) -> str:
    """'PE-RT/Al/PE-RT 20×2,0' → '20×2,0'; 'PP-HT 110' → 'Ø110'."""
    s = str(s)
    m = re.search(r"(\d+×\d+,\d)", s)
    if m:
        return m.group(1)
    m = re.search(r"(\d{2,3})\s*$", s)
    return f"Ø{m.group(1)}" if m else s


# ------------------------------------------------------------------------------------------------ opisy
def _text_fn(text, h, layer, color=None, style="normal"):
    def fn(cv, cand):
        P, ang, va = cand
        cv.text(P, text, h, ang, "center", va, layer, style=style, color=color, mask=0.35)
    return fn


def label_along(vp, placer, path, text: str, layer: str, h: float = H_S, color=None, max_cost=6.0,
                prefer=(0.5, 0.3, 0.7, 0.18, 0.82), leader_ok: bool = True, style="normal"):
    """Opis przewodu równolegle do odcinka trasy (nad/pod linią), położenie o najmniejszej kolizji; gdy żaden
    odcinek nie mieści napisu — odnośnik do wolnego miejsca. Zwraca True, gdy opis narysowano."""
    k = vp.k
    P = np.asarray(path, float)
    if len(P) < 2:
        return False
    w = T.width(text, h, style) * k
    cands = []
    segs = sorted(range(len(P) - 1), key=lambda i: -float(np.hypot(*(P[i + 1] - P[i]))))
    for i in segs:
        A, B = P[i], P[i + 1]
        L = float(np.hypot(*(B - A)))
        if L < w + 2.0 * k:
            continue
        d = unit(B - A)
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        up = perp(dir_deg(ang))
        for f in prefer:
            f = min(max(f, (w / 2 + k) / L), 1 - (w / 2 + k) / L)
            Q = A + (B - A) * f
            cands.append((Q + up * 0.7 * k, ang, "baseline"))
            cands.append((Q - up * 0.7 * k, ang, "top"))
    if cands:
        best, cost = placer.place(vp, _text_fn(text, h, layer, color, style), cands, penalty_step=0.02,
                                  max_cost=max_cost if leader_ok else None)
        if best is not None:
            return True
    if not leader_ok:
        return False
    i = segs[0]
    anchor = (P[i] + P[i + 1]) / 2
    return tag_leader(vp, placer, anchor, [text], layer, h=h, color=color) is not None


def tag_leader(vp, placer, anchor, lines, layer: str, h: float = H_S, color=None, radii=(5.0, 8.0, 12.0, 17.0, 23.0),
               n_ang: int = 12, style="normal", min_r: float = 0.0, bounds=None, dot=True):
    """Blok opisu (1…n wierszy) w pobliżu punktu ``anchor`` z odnośnikiem (kropka + linia) — pozycja o najmniejszej
    kolizji z już narysowanymi elementami. Zwraca wybraną pozycję lub None."""
    k = vp.k
    A = np.asarray(anchor, float)
    lines = [s for s in lines if s]
    if not lines:
        return None
    w = max(T.width(s, h, style) for s in lines) * k
    lh = h * 1.55 * k
    H = lh * len(lines)
    cands = []
    for r in radii:
        if r < min_r:
            continue
        for j in range(n_ang):
            a = 2 * math.pi * (j + 0.5 * (r > 6)) / n_ang
            c = A + np.array([math.cos(a), math.sin(a)]) * r * k
            ha = "left" if math.cos(a) >= -0.2 else "right"
            cands.append((c, ha))

    def fn(cv, cand):
        c, ha = cand
        x0 = c[0] if ha == "left" else c[0] - w
        top = c[1] + H / 2
        # odnośnik do najbliższego punktu ramki opisu
        qx = min(max(A[0], x0), x0 + w)
        qy = min(max(A[1], top - H), top)
        q = np.array([qx, qy])
        if float(np.hypot(*(q - A))) > 1.5 * k:
            cv.line(A, q, layer, pen="b_cienka", color=color)
            if dot:
                cv.dot(A, 0.7, layer, color=color or "#000000")
        for i, s in enumerate(lines):
            cv.text((x0, top - (i + 1) * lh + 0.35 * h * k), s, h, 0.0, "left", "baseline", layer, color=color,
                    mask=0.35, style=style if i == 0 else "normal")
    best, _c = placer.place(vp, fn, cands, penalty_step=0.015, bounds=bounds)
    return best


def text_block(vp, placer, center, lines, layer, h=H_S, color=None, radius_mm=(0, 3, 6, 10, 15), bounds=None,
               style="normal", max_cost=None):
    """Opis bez odnośnika (np. opis pomieszczenia) — środek bloku jak najbliżej ``center``."""
    k = vp.k
    C = np.asarray(center, float)
    lines = [s for s in lines if s]
    lh = h * 1.55 * k
    H = lh * len(lines)
    cands = [tuple(C)]
    for r in radius_mm[1:]:
        for j in range(8):
            a = 2 * math.pi * j / 8
            cands.append((C[0] + math.cos(a) * r * k, C[1] + math.sin(a) * r * k))

    def fn(cv, c):
        for i, s in enumerate(lines):
            cv.text((c[0], c[1] + H / 2 - (i + 1) * lh + 0.35 * h * k), s, h, 0.0, "center", "baseline", layer,
                    color=color, mask=0.3, style=style if i == 0 else "normal")
    return placer.place(vp, fn, cands, penalty_step=0.01, bounds=bounds, max_cost=max_cost)[0]


def text_collisions(vp, pad_mm: float = 0.0) -> int:
    """Liczba par napisów rzutni o nachodzących obrysach (kontrola czytelności)."""
    from shapely import STRtree
    from shapely.geometry import Polygon
    from ...draft.core import PText, text_items
    boxes = [Polygon(text_items(p, vp.k)[1]) for p in vp.prims if isinstance(p, PText) and p.string.strip()]
    boxes = [b.buffer(-0.15 * vp.k) for b in boxes]
    tree = STRtree(boxes)
    n = 0
    for i, b in enumerate(boxes):
        for j in tree.query(b):
            if j > i and b.intersects(boxes[j]) and b.intersection(boxes[j]).area > (0.1 * vp.k) ** 2:
                n += 1
    return n


# ------------------------------------------------------------------------------------------------ legenda
class Legenda:
    """Legenda symboli arkusza instalacji (blok kolumny opisowej). Pozycje: linie mediów (warstwa, rodzaj linii)
    i symbole (funkcja rysująca w mm arkusza, środek symbolu w punkcie ``pos``)."""

    def __init__(self, tytul: str = "OZNACZENIA — LEGENDA SYMBOLI", zrodlo: str = ""):
        self.tytul = tytul
        self.zrodlo = zrodlo
        self.items: list = []
        self._keys: set = set()

    def line(self, layer: str, text: str, lt=None, pen=None, key=None, color=None):
        key = key or ("L", layer, lt, text)
        if key not in self._keys:
            self._keys.add(key)
            self.items.append(("line", (layer, lt, pen, color), text))

    def sym(self, fn, text: str, key=None):
        key = key or ("S", text)
        if key not in self._keys:
            self._keys.add(key)
            self.items.append(("sym", fn, text))

    def block(self):
        items = list(self.items)
        tytul, zrodlo = self.tytul, self.zrodlo

        def fn(sh, x, y, w):
            if not items:
                return y
            cols = 2
            cw = w / cols
            tw = cw - 19.0
            with sh.on("R-LEGENDA"):
                sh.text((x, y - 3.5), tytul, 3.5, style="bold")
                yy = y - 8.5
                if zrodlo:
                    for s in wrap(zrodlo, w - 8.0, 1.8, "italic"):
                        sh.text((x, yy), s, 1.8, style="italic")
                        yy -= 2.7
                    yy -= 1.0
                rows = []
                for kind, payload, text in items:
                    ls = wrap(text, tw, 1.8)
                    rows.append((kind, payload, ls, max(5.2, 2.7 * len(ls) + 1.6)))
                # rozkład na 2 kolumny o zbliżonej wysokości
                tot = sum(r[3] for r in rows)
                acc, split = 0.0, len(rows)
                for i, r in enumerate(rows):
                    if acc >= tot / 2:
                        split = i
                        break
                    acc += r[3]
                y_end = yy
                for ci, part in enumerate((rows[:split], rows[split:])):
                    cy = yy
                    cx = x + ci * cw
                    for kind, payload, ls, rh in part:
                        mid = cy - rh / 2 + 0.6
                        if kind == "line":
                            layer, lt, pen, color = payload
                            sh.line((cx + 1.0, mid), (cx + 15.0, mid), layer, pen=pen, lt=lt, color=color)
                        else:
                            try:
                                payload(sh, np.array([cx + 8.0, mid]))
                            except Exception as ex:  # pragma: no cover
                                sh.text((cx + 1.0, mid), f"? {ex}"[:20], 1.8)
                        for j, s in enumerate(ls):
                            sh.text((cx + 18.0, cy - 2.2 - j * 2.7), s, 1.8)
                        cy -= rh
                    y_end = min(y_end, cy)
            return y_end - 1.0
        return fn


def table_block(title, cols, rows, align=None, h=1.8, row_h=4.2):
    """Tabela w kolumnie opisowej (szerokości kolumn skalowane do szerokości kolumny arkusza)."""
    from ...draft.sheet import table

    def fn(sh, x, y, w):
        if not rows:
            return y
        tot = sum(c[1] for c in cols)
        cs = [(n, cw * w / tot) for n, cw in cols]
        r = table(sh, x, y - 6.5, cs, rows, h=h, row_h=row_h, title=title, align=align, header_h=6.0)
        return r[1]
    return fn


def text_lines_block(title, lines, h=1.8):
    def fn(sh, x, y, w):
        with sh.on("R-OPISY"):
            sh.text((x, y - 3.5), title, 3.5, style="bold")
            yy = y - 8.5
            for ln in lines:
                for s in wrap(ln, w - 2.0, h):
                    sh.text((x + 1.0, yy), s, h)
                    yy -= h * 1.55
                yy -= 0.6
        return yy
    return fn
