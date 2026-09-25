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
            cands = sorted(cands, key=lambda c_: abs(cands.index(c_) - mid))
            pos, _c = self.pl.place(self.vp, fn, cands, penalty_step=0.01, bounds=self.bounds, max_cost=max_cost)
            if pos is None:
                break
            used.append(ls.project(Point(pos[0])))
            placed += 1
        return placed
