"""Rysowanie elementów projektu zagospodarowania działki (PZT) silnikiem ``lamela.draft``.

Konwencje: PN-B-01027 (oznaczenia PZT — grubości linii jawnie w mm), PN-EN ISO 11091, PN-EN ISO 128-2 (linie),
PN-B-01025 (rzędne — 2 miejsca na PZT), PN-B-01029 (wymiary w m z dokładnością 0,01 m); uzbrojenie — kolory i litery
wg praktyki mapy zasadniczej (rozp. BDOT500, Dz.U. 2021 poz. 1385, zał. 4). Współrzędne — układ działki [m].

Zawiera: warstwy PZT, ``Labeler`` (opisy z odnośnikami bez kolizji — ``common.Placer``), podkład mapowy, elementy
projektu, sieci, wymiary odległości, rzędne i spadki, legendę i tabele arkusza.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import styles, text as T
from ..draft.core import Viewport
from ..draft.geom import circle_pts, lines_of, perp, polygons_of, readable_angle, unit
from .common import Placer

# ------------------------------------------------------------------------------------------------ warstwy PZT
_L = styles.LayerDef
for _ld in [
    _L("Z-MAPA", "Podkład: mapa do celów projektowych (przykładowa, fikcyjna)", "b_cienka", aci=8,
       plot_rgb="#5a5a5a", z=12),
    _L("Z-MAPA-OPISY", "Podkład: opisy mapy (numery działek, budynki, sieci)", "cienka", aci=8, plot_rgb="#5a5a5a",
       z=26),
    _L("Z-MAPA-RAMKA", "Ramka i opis podkładu mapowego", "srednia", aci=7, z=27),
    _L("Z-DZIALKA", "Granica działki budowlanej (PN-B-01027 poz. 2.7)", "srednia", aci=1, z=23),
    _L("Z-LZ", "Nieprzekraczalna linia zabudowy (MPZP, PN-B-01027 poz. 2.2)", "srednia", aci=1, plot_rgb="#c00000",
       z=22),
    _L("Z-DROGA", "Droga publiczna: linie rozgraniczające, jezdnia", "srednia", aci=8, plot_rgb="#404040", z=14),
    _L("Z-BUDYNEK", "Budynek projektowany — obrys przyziemia 1,0 m nad terenem (PN-B-01027 poz. 1.1)", "b_gruba",
       aci=7, z=24),
    _L("Z-BUDYNEK-NAD", "Obrys wyższych kondygnacji, płyt i okapów (PN-B-01027 poz. 1.6)", "gruba", "KRESKOWA",
       aci=7, z=23),
    _L("Z-WYMIARY", "Wymiarowanie PZT — linie 0,18 (PN-B-01027 poz. 4)", "b_cienka", aci=1, z=25),
    _L("Z-RZEDNE", "Rzędne terenu istniejącego i projektowanego (PN-B-01025)", "b_cienka", aci=32,
       plot_rgb="#6b4423", z=25),
    _L("Z-RZEDNE-PROJ", "Rzędne terenu projektowanego", "b_cienka", aci=1, z=25),
    _L("Z-ODWODNIENIE", "Odwodnienie terenu, spadki, kierunki spływu", "cienka", aci=150, plot_rgb="#00808a", z=21),
    _L("Z-SIECI-IST", "Uzbrojenie istniejące (wg mapy)", "cienka", aci=5, z=19),
    _L("Z-SIECI-PROJ", "Uzbrojenie projektowane (przyłącza, kolektory)", "gruba", aci=5, z=21),
    _L("Z-KOLIZJE", "Kolizje, zbliżenia i skrzyżowania sieci", "srednia", aci=6, plot_rgb="#c000c0", z=27),
    _L("Z-TYCZENIE", "Punkty tyczenia budynku", "cienka", aci=1, z=26),
    _L("Z-STREFY", "Strefy (R290 pompy ciepła)", "cienka", aci=6, plot_rgb="#b000b0", z=13),
    _L("Z-TLO", "Tło (maski wypełnień)", "b_cienka", aci=7, z=9),
]:
    styles.LAYERS.setdefault(_ld.name, _ld)

GREY = "#5a5a5a"
H = 2.5          # podstawowa wysokość pisma w rzutniach PZT (min. 2,5 mm — PN-B-01027, plot.qa)


# ------------------------------------------------------------------------------------------------ geometria
def clip(g, win):
    """Część geometrii w oknie (Polygon); None gdy pusta."""
    if g is None or win is None:
        return g
    r = g.intersection(win)
    return None if r.is_empty else r


def draw_geom(c, g, layer, pen=None, lt=None, color=None, z=None):
    if g is None or g.is_empty:
        return
    for a in lines_of(g):
        if len(a) >= 2:
            closed = len(a) > 2 and np.allclose(a[0], a[-1])
            c.polyline(a[:-1] if closed else a, layer, closed=closed, pen=pen, lt=lt, color=color, z=z)


def fill_white(c, g, z=9.5):
    """Białe tło pod elementem (zakrywa kreskowania/kropki podkładu)."""
    if g is not None and not g.is_empty:
        c.fill(g, "Z-TLO", "#ffffff", z=z)


def seg_dir(a, b):
    d = np.asarray(b, float) - np.asarray(a, float)
    return d / (np.hypot(*d) or 1.0)


# ------------------------------------------------------------------------------------------------ napisy
def text_block(c, pos, lines, h=H, ha="left", layer="Z-OPISY", style="normal", color=None, mask=0.0, gap=1.45,
               rot=0.0):
    """Blok wierszy: ``pos`` = punkt górnej krawędzi bloku (wg ``ha``); zwraca (szer., wys.) w jedn. płótna."""
    k = c.k
    lines = [ln for ln in (lines if isinstance(lines, (list, tuple)) else [lines]) if ln is not None]
    a = math.radians(rot)
    ex, ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    P = np.asarray(pos, float)
    for i, s in enumerate(lines):
        st = style[i] if isinstance(style, (list, tuple)) else style
        q = P - ey * (h + i * h * gap) * k
        c.text(q, str(s), h, rot, ha, "baseline", layer, style=st, color=color, mask=mask)
    W = max((T.width(str(s), h, "bold" if st_is_bold(style, i) else "normal") for i, s in enumerate(lines)),
            default=0.0) * k
    return W, (h + (len(lines) - 1) * h * gap + 0.22 * h) * k


def st_is_bold(style, i):
    st = style[i] if isinstance(style, (list, tuple)) else style
    return st == "bold"


def block_size(lines, h=H, style="normal", gap=1.45):
    """Wymiary bloku [mm papieru]."""
    lines = [ln for ln in (lines if isinstance(lines, (list, tuple)) else [lines]) if ln is not None]
    W = max((T.width(str(s), h, "bold" if st_is_bold(style, i) else "normal") for i, s in enumerate(lines)),
            default=0.0)
    return W, h + (len(lines) - 1) * h * gap + 0.22 * h


DIRS = [(1, 0), (1, 1), (0, 1), (-1, 0), (1, -1), (0, -1), (-1, 1), (-1, -1)]


class Labeler:
    """Opisy bez kolizji: rejestr zajętości (``common.Placer``) i wybór położenia z kandydatów wokół punktu
    (8 kierunków × rosnące odsunięcie); przy odsunięciu — odnośnik od punktu do bloku napisu."""

    def __init__(self, vp: Viewport, bounds=None):
        self.vp = vp
        self.k = vp.k
        self.pl = Placer(vp.k)
        self.bounds = bounds
        self.failed = []

    def mark(self) -> int:
        return len(self.vp.prims)

    def reg(self, n0: int, w_text=1.0, w_line=0.5, w_fill=1.0):
        self.pl.add_prims(self.vp.prims[n0:], w_text=w_text, w_line=w_line, w_fill=w_fill)

    def area(self, g, w=1.0):
        if g is not None and not g.is_empty:
            self.pl.add(g, "area", w)

    def lines(self, g, w=0.4, buf_mm=0.3):
        if g is not None and not g.is_empty:
            self.pl.add_lines(g, w=w, buf_mm=buf_mm)

    def label(self, anchor, lines, h=H, layer="Z-OPISY", style="normal", color=None, mask=0.5,
              dists=(0.8, 2.0, 4.0, 7.0, 11.0, 16.0, 22.0), dirs=None, leader_from=3.0, dot=False,
              max_cost=None, frame=False, register=True, leader_color=None, penalty=0.02):
        k = self.k
        W, Hh = block_size(lines, h, style)
        A = np.asarray(anchor, float)
        cands = []
        for d in dists:
            for (ux, uy) in (dirs or DIRS):
                cx = A[0] + (ux * (d + W / 2.0) * k if ux else 0.0)
                cy = A[1] + (uy * (d + Hh / 2.0) * k if uy else 0.0)
                cands.append((cx, cy, ux, uy, d))

        def fn(cv, cand):
            cx, cy, ux, uy, d = cand
            ha = "left" if ux > 0 else "right" if ux < 0 else "center"
            x = cx - W / 2.0 * k if ha == "left" else cx + W / 2.0 * k if ha == "right" else cx
            top = cy + Hh / 2.0 * k
            text_block(cv, (x, top), lines, h, ha, layer, style, color, mask)
            bx = box(cx - W / 2.0 * k - 0.6 * k, cy - Hh / 2.0 * k - 0.5 * k,
                     cx + W / 2.0 * k + 0.6 * k, cy + Hh / 2.0 * k + 0.5 * k)
            if frame:
                cv.polygon(np.asarray(bx.exterior.coords)[:-1], layer, pen=0.18, color=color)
            if d >= leader_from:
                q = np.asarray(bx.exterior.interpolate(bx.exterior.project(Point(A))).coords[0])
                if np.hypot(*(q - A)) > 1.2 * k:
                    cv.line(A, q, layer, pen=0.18, color=leader_color or color)
                    if dot:
                        cv.dot(A, 0.7, layer, color=leader_color or color or "#000000")
        pos, cost = self.pl.place(self.vp, fn, cands, penalty_step=penalty, bounds=self.bounds, max_cost=max_cost,
                                  register=register)
        if pos is None:
            self.failed.append(lines)
        return pos, cost

    def along(self, ls: LineString, text, h=H, layer="Z-OPISY", color=None, n=1, fracs=None, offset_mm=0.0,
              max_cost=4.0, style="normal", mask=0.4, min_len_mm=12.0):
        """Opis wzdłuż łamanej (np. warstwica, sieć) — ``n`` wystąpień w najlepszych miejscach."""
        k = self.k
        L = ls.length
        w = T.width(text, h, style) * k
        if L < max(w * 1.2, min_len_mm * k):
            return 0
        fr = fracs or [i / 20.0 for i in range(1, 20)]
        placed = 0
        used = []

        def fn(cv, cand):
            p, ang, up = cand
            cv.text(p + up * offset_mm * k, text, h, ang, "center", "middle", layer, style=style, color=color,
                    mask=mask)
        for _ in range(n):
            cands = []
            for f in fr:
                s = f * L
                if s < w / 2 or s > L - w / 2 or any(abs(s - u) < max(L / (n + 1) * 0.6, w * 1.5) for u in used):
                    continue
                p = np.asarray(ls.interpolate(s).coords[0])
                a = np.asarray(ls.interpolate(max(0.0, s - w / 2)).coords[0])
                b = np.asarray(ls.interpolate(min(L, s + w / 2)).coords[0])
                if np.hypot(*(b - a)) < w * 0.92:          # zakręt pod napisem
                    continue
                d = unit(b - a)
                ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
                cands.append((p, ang, perp(np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]))))
            if not cands:
                break
            mid = len(cands) // 2
            cands = [c_ for _i, c_ in sorted(enumerate(cands), key=lambda t: abs(t[0] - mid))]
            pos, _c = self.pl.place(self.vp, fn, cands, penalty_step=0.01, bounds=self.bounds, max_cost=max_cost)
            if pos is None:
                break
            used.append(ls.project(Point(pos[0])))
            placed += 1
        return placed


# ================================================================================================ podkład mapowy
def map_window(s, opts: dict, margin=4.0):
    """Okno podkładu: działka + budynki sąsiednie + hydrant (± margines), przycięte do zasięgu danych mapy."""
    if opts.get("okno"):
        return tuple(float(v) for v in opts["okno"])
    geoms = [s.plot] + [x["bud"] for x in s.sasiedzi if x["bud"] is not None]
    geoms += [Point(o.xy) for o in s.obiekty.values() if o.id.upper().startswith("HYD")]
    x0, y0, x1, y1 = unary_union(geoms).bounds
    x0, y0, x1, y1 = x0 - margin, y0 - margin - 4.0, x1 + margin, y1 + margin
    data = [x["poly"] for x in s.sasiedzi if x["poly"] is not None] + \
        [g for g in (s.droga["pas"], s.plot) if g is not None]
    bx0, by0, bx1, by1 = unary_union(data).bounds
    return max(x0, bx0), max(y0, by0), min(x1, bx1), min(y1, by1)


def draw_base_map(c, s, lab: Labeler, win: Polygon, used: set, opts: dict, spot_every=9.0):
    """Treść podkładu (mapy do celów projektowych — SYNTETYCZNEJ, z dzialka.yaml): działki sąsiednie z numerami,
    budynki sąsiednie, droga, uzbrojenie istniejące, warstwice i pikiety terenu istniejącego, zieleń istniejąca."""
    from ..draft import symbols as S
    k = c.k
    n0 = lab.mark()
    # działki sąsiednie
    for x in s.sasiedzi:
        g = clip(x["poly"], win)
        if g is not None:
            draw_geom(c, clip(x["poly"].exterior, win), "Z-MAPA", pen=0.25, lt="CIAGLA")
    # droga: pas w liniach rozgraniczających (0,7 — PN-B-01027 poz. 2.5), jezdnia
    pas, jez = s.droga["pas"], s.droga["jezdnia"]
    if jez is not None and clip(jez, win) is not None:
        c.fill(clip(jez, win), "Z-DROGA", "#e6e6e6", z=8.0)
        draw_geom(c, clip(jez.exterior, win), "Z-MAPA", pen=0.25, lt="CIAGLA")
        used.add("jezdnia")
    if pas is not None:
        draw_geom(c, clip(pas.exterior, win), "Z-DROGA", pen=0.7, lt="CIAGLA", color="#303030")
        used.add("rozgraniczajaca")
    # budynki sąsiednie (kreskowanie 45° cienkie, opis funkcja + liczba kondygnacji wg BDOT500)
    from ..draft.hatch import _parallel
    for x in s.sasiedzi:
        g = clip(x["bud"], win)
        if g is None:
            continue
        fill_white(c, g)
        for ln in _parallel(g, 45.0, 1.5 * k):
            c.polyline(ln, "Z-MAPA", pen=0.13, color="#8a8a8a")
        draw_geom(c, g, "Z-MAPA", pen=0.35, lt="CIAGLA", color="#3a3a3a")
        used.add("bud_sasiedni")
    lab.reg(n0, w_line=0.3, w_fill=0.3)
    for x in s.sasiedzi:
        g = clip(x["bud"], win)
        if g is not None:
            txt = "m" + (str(x["kond"]) if x.get("kond") else "")
            p = np.asarray(g.representative_point().coords[0])
            n1 = lab.mark()
            c.text(p, txt, 3.5, 0.0, "center", "middle", "Z-MAPA-OPISY", style="italic", color=GREY, mask=0.6)
            lab.reg(n1)
    # uzbrojenie istniejące
    for sx in [x for x in s.sieci if x.istn]:
        g = clip(sx.geom, win)
        if g is not None:
            utility(c, g, sx, existing=True)
            used.add(f"ist_{sx.branza}")
    lab.reg(n0, w_line=0.25)
    return n0


def label_base_map(c, s, lab: Labeler, win: Polygon, used: set, opts: dict, spot_every=9.0, contours=True):
    """Opisy podkładu po narysowaniu projektu (niższy priorytet niż treść projektu)."""
    k = c.k
    # numery działek
    for x in s.sasiedzi:
        g = clip(x["poly"], win)
        if g is None:
            continue
        free = g.difference(x["bud"].buffer(1.0)) if x["bud"] is not None else g
        p = np.asarray((free if not free.is_empty else g).representative_point().coords[0])
        lab.label(p, [x["nr"]], 3.5, "Z-MAPA-OPISY", "italic", GREY, dists=(0.0, 3.0, 8.0, 14.0), leader_from=99,
                  max_cost=6.0)
    for sx in [x for x in s.sieci if x.istn]:
        g = clip(sx.geom, win)
        if g is None:
            continue
        for ls in (g.geoms if hasattr(g, "geoms") else [g]):
            lab.along(ls, sx.lit, H, "Z-SIECI-IST", sx.kolor, n=3, max_cost=3.0)
            short = sx.opis.split("(")[0].split(",")[0].strip()
            lab.along(ls, f"{sx.lit} — {short}", H, "Z-SIECI-IST", sx.kolor, n=1, max_cost=6.0,
                      fracs=[0.35, 0.3, 0.4, 0.25, 0.45, 0.2, 0.5, 0.55, 0.6, 0.65])
    if s.droga["pas"] is not None and clip(s.droga["pas"], win) is not None:
        g = clip(s.droga["pas"], win)
        cy = g.centroid.y
        x0, _y0, x1, _y1 = g.bounds
        axis = LineString([(x0, cy), (x1, cy)])
        lab.along(axis, f"{s.droga['symbol']} — {s.droga['nazwa']}", 3.5, "Z-MAPA-OPISY", GREY, n=1, max_cost=30.0,
                  style="bold")
    if contours:
        bb = win.bounds
        for pts, Hh in s.contours(bb):
            ls = LineString(pts)
            g = clip(ls, win.buffer(-1.0 * k))
            if g is None:
                continue
            for part in (g.geoms if hasattr(g, "geoms") else [g]):
                lab.along(part, f"{Hh:.2f}".replace(".", ","), H, "Z-RZEDNE", None, n=1, max_cost=2.5)
