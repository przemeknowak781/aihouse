"""Symbole zagospodarowania terenu i mapy (PN-EN ISO 11091, praktyka map do celów projektowych — rozp. w sprawie
standardów technicznych dla mapy zasadniczej: oznaczenia przybliżone).

Wymiary rzeczywiste w metrach modelu (korona drzewa, studzienka), symbole umowne w mm papieru.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from . import fmt, text as T
from .geom import (arr, circle_pts, dir_deg, lines_of, perp, polygons_of, readable_angle, rect_c, rect_pts,
                   stable_seed, to_polygon, unit)

__all__ = [
    "tree", "shrub", "hedge", "lawn", "paving", "pole", "hydrant", "manhole", "cable_box", "utility_box",
    "plot_boundary", "building_line", "contours", "spot_height", "gate",
]


def _scallop(center, r, n=None, depth=0.18):
    n = n or max(8, int(2 * math.pi * r / (r * 0.55)))
    t = np.linspace(0, 2 * math.pi, n * 12, endpoint=False)
    rr = r * (1 - depth * np.abs(np.sin(n * t / 2)))
    return np.column_stack([center[0] + rr * np.cos(t), center[1] + rr * np.sin(t)])


def tree(c, pos, crown_d: float = 5.0, existing: bool = True, remove: bool = False, conifer: bool = False,
         layer: str = "Z-ZIELEN", label: str | None = None):
    """Drzewo: istniejące — okrąg korony + pień + kropka; projektowane — korona falista; do wycinki — krzyż;
    iglaste — korona z promienistymi kreskami."""
    k = c.k
    P = np.asarray(pos, float)
    R = crown_d / 2
    with c.on(layer):
        if conifer:
            n = 14
            pts = []
            for i in range(2 * n):
                a = math.pi * i / n
                rr = R if i % 2 == 0 else R * 0.72
                pts.append(P + rr * np.array([math.cos(a), math.sin(a)]))
            c.polygon(pts, pen="cienka")
        elif existing:
            c.circle(P, R, pen="cienka")
        else:
            c.polygon(_scallop(P, R), pen="cienka")
        c.circle(P, max(0.15, 0.6 * k), pen="cienka")
        c.dot(P, 0.6, layer)
        if remove:
            a = R * 0.75
            c.line(P + [-a, -a], P + [a, a], pen="srednia", color="#c00000")
            c.line(P + [-a, a], P + [a, -a], pen="srednia", color="#c00000")
        if label:
            c.text(P + np.array([R * 0.75, -R * 0.75]), label, 2.0, 0.0, "left", "top")


def shrub(c, pos, d: float = 1.2, layer: str = "Z-ZIELEN"):
    c.polygon(_scallop(pos, d / 2, 7, 0.25), layer, pen="b_cienka")


def hedge(c, pts, width: float = 0.8, layer: str = "Z-ZIELEN"):
    """Żywopłot: pas wzdłuż łamanej z obrysem falistym."""
    ls = LineString(arr(pts))
    L = ls.length
    step = width * 0.7
    n = max(2, int(L / step))
    with c.on(layer):
        for i in range(n):
            q = np.asarray(ls.interpolate((i + 0.5) * L / n).coords)[0]
            c.polygon(_scallop(q, width / 2, 6, 0.2), pen="b_cienka")


def lawn(c, poly, density_per_cm2: float = 0.35, layer: str = "Z-ZIELEN", seed=None, outline: bool = False):
    """Trawnik: rzadkie kępki (3 kreski) rozmieszczone równomiernie w wieloboku (gęstość na cm² papieru)."""
    from .hatch import _random_points, _rng
    k = c.k
    g = to_polygon(poly)
    for pg in polygons_of(g):
        rng = _rng(pg, seed)
        pts = _random_points(pg, density_per_cm2 / 100.0, k, rng, inset=1.2 * k)
        for p in pts:
            for a, L in ((90, 1.0), (65, 0.8), (115, 0.8)):
                c.line(p, p + dir_deg(a) * L * k, layer, pen="b_cienka")
        if outline:
            c.geom(pg, layer, pen="cienka")


def paving(c, poly, kind: str = "kostka", layer: str = "Z-UTWARDZENIA", spacing_mm: float = 1.6, angle: float = 0.0,
           outline: bool = True):
    """Nawierzchnia utwardzona: 'kostka' — siatka drobna, 'plyty' — siatka większa, 'zwir' — kropki,
    'asfalt' — tło szare, 'deska' — linie równoległe (taras)."""
    from .hatch import _parallel, _dots, _rng
    k = c.k
    g = to_polygon(poly)
    for pg in polygons_of(g):
        if kind in ("kostka", "plyty"):
            sp = spacing_mm if kind == "kostka" else spacing_mm * 2.5
            for a in (angle, angle + 90):
                for ln in _parallel(pg, a, sp * k):
                    c.polyline(ln, layer, pen="b_cienka")
        elif kind == "deska":
            for ln in _parallel(pg, angle, spacing_mm * 0.6 * k):
                c.polyline(ln, layer, pen="b_cienka")
        elif kind == "zwir":
            _dots(c, pg, 0.8, _rng(pg), layer, 0.12)
        elif kind == "asfalt":
            c.fill(pg, layer, "#d8d8d8")
        if outline:
            c.geom(pg, layer, pen="cienka")


def pole(c, pos, kind: str = "en", s_mm: float = 2.0, layer: str = "Z-UZBROJENIE"):
    """Słup: 'en' — elektroenergetyczny (okrąg z kropką), 'osw' — oświetleniowy (okrąg z krzyżykiem),
    'tel' — telekomunikacyjny (okrąg pusty)."""
    k = c.k
    R = s_mm * k / 2
    with c.on(layer):
        c.circle(pos, R)
        if kind == "en":
            c.dot(pos, s_mm * 0.45, layer)
        elif kind == "osw":
            P = np.asarray(pos)
            c.line(P + [-R, 0], P + [R, 0])
            c.line(P + [0, -R], P + [0, R])


def hydrant(c, pos, s_mm: float = 3.0, underground: bool = False, layer: str = "Z-UZBROJENIE"):
    """Hydrant (okrąg z literą H; podziemny — okrąg przekreślony)."""
    k = c.k
    R = s_mm * k / 2
    with c.on(layer):
        c.circle(pos, R)
        if underground:
            P = np.asarray(pos)
            c.line(P + [-R, -R] * np.array([0.7, 0.7]), P + [R, R] * np.array([0.7, 0.7]))
        c.text(pos, "H", 2.0, 0.0, "center", "middle")


def manhole(c, pos, d: float = 1.0, label: str | None = "Sk", layer: str = "Z-UZBROJENIE", h: float = 2.0):
    """Studzienka (okrąg o średnicy rzeczywistej, min. 2 mm na papierze) z oznaczeniem."""
    R = max(d / 2, 1.0 * c.k)
    with c.on(layer):
        c.circle(pos, R)
        c.dot(pos, 0.5, layer)
        if label:
            c.text(np.asarray(pos) + np.array([R + 0.8 * c.k, 0.0]), label, h, 0.0, "left", "middle")


def cable_box(c, pos, rot: float = 0.0, w: float = 0.9, d: float = 0.35, label: str = "ZK",
              layer: str = "Z-UZBROJENIE"):
    """Złącze kablowe / kablowo-pomiarowe (prostokąt z opisem) — wymiary rzeczywiste."""
    from .geom import Xf
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        q = xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2))
        c.polygon(q, pen="srednia")
        c.line(q[0], q[2], pen="b_cienka")
        c.text(xf.pt(0, d / 2 + 0.8 * c.k), label, 2.0, 0.0, "center", "bottom", style="bold")


def utility_box(c, pos, rot: float = 0.0, w: float = 0.6, d: float = 0.3, label: str = "SG",
                layer: str = "Z-UZBROJENIE"):
    """Skrzynka (gazowa SG, wodomierzowa, telekom.) — prostokąt z opisem."""
    from .geom import Xf
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2)), pen="cienka")
        c.text(xf.pt(0, d / 2 + 0.8 * c.k), label, 2.0, 0.0, "center", "bottom")


def plot_boundary(c, pts, closed: bool = True, point_labels=None, point_r_mm: float = 0.9,
                  layer: str = "Z-GRANICE", h: float = 2.0, label_offset_mm: float = 2.2):
    """Granica działki (linia dwupunktowa gruba) z punktami granicznymi (kółka) i ich numerami."""
    k = c.k
    P = arr(pts)
    with c.on(layer):
        c.polyline(P, closed=closed, pen="gruba", lt="DWUPUNKTOWA")
        ctr = P.mean(axis=0)
        for i, p in enumerate(P):
            c.fill(circle_pts(p, point_r_mm * k, 24), layer, "#ffffff", z=23.2)
            c.circle(p, point_r_mm * k, pen="cienka", lt="CIAGLA", z=23.3)
            if point_labels is not None:
                v = unit(p - ctr)
                c.text(p + v * label_offset_mm * k, str(point_labels[i]), h, 0.0, "center", "middle")


def building_line(c, p1, p2, label: str = "nieprzekraczalna linia zabudowy", layer: str = "Z-LINIE-ZABUDOWY",
                  h: float = 2.0, dist_label: str | None = None):
    """Linia zabudowy (MPZP) — linia punktowa z opisem wzdłuż."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    with c.on(layer):
        c.line(A, B)
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        up = perp(dir_deg(ang))
        M = A + (B - A) * 0.3
        c.text(M + up * 0.8 * k, label, h, ang, "center", "baseline")


def contours(c, lines, step_label: float = 0.5, layer: str = "Z-WARSTWICE", h: float = 1.8, nd: int = 2,
             label_every: float = 60.0):
    """Warstwice: lines = [(punkty, H), …]. Warstwice zasadnicze (wielokrotność ``step_label``) grubsze i opisane
    (opis wzdłuż warstwicy, co ~``label_every`` mm papieru, z przerwą — maska)."""
    k = c.k
    for pts, H in lines:
        P = arr(pts)
        major = abs((H / step_label) - round(H / step_label)) < 1e-6
        c.polyline(P, layer, pen="cienka" if major else "b_cienka")
        if major:
            ls = LineString(P)
            L = ls.length
            n = max(1, int(L / (label_every * k)))
            for i in range(n):
                s = (i + 0.5) * L / n
                q = np.asarray(ls.interpolate(s).coords)[0]
                q2 = np.asarray(ls.interpolate(min(L, s + 0.5 * k)).coords)[0]
                q1 = np.asarray(ls.interpolate(max(0, s - 0.5 * k)).coords)[0]
                dd = unit(q2 - q1)
                ang = readable_angle(math.degrees(math.atan2(dd[1], dd[0])))
                c.text(q, fmt.num(H, nd), h, ang, "center", "middle", layer, mask=0.4)


def spot_height(c, pos, H: float, existing: bool = True, nd: int = 2, layer: str = "Z-WARSTWICE", h: float = 1.8):
    """Punkt wysokościowy: istniejący — krzyżyk + wartość (kursywa); projektowany — kropka + wartość w ramce."""
    k = c.k
    P = np.asarray(pos, float)
    s = 0.8 * k
    lab = fmt.num(H, nd)
    with c.on(layer):
        if existing:
            c.line(P + [-s, 0], P + [s, 0], pen="cienka")
            c.line(P + [0, -s], P + [0, s], pen="cienka")
            c.text(P + np.array([1.2 * k, 0.6 * k]), lab, h, 0.0, "left", "baseline", style="italic")
        else:
            c.dot(P, 0.8, layer)
            w = T.width(lab, h) * k
            x0 = P[0] + 1.2 * k
            c.rect(x0 - 0.5 * k, P[1] + 0.2 * k, x0 + w + 0.5 * k, P[1] + h * k + 1.1 * k, pen="cienka")
            c.text((x0, P[1] + 0.65 * k), lab, h, 0.0, "left", "baseline")


def gate(c, p1, p2, kind: str = "przesuwna", layer: str = "Z-OGRODZENIE"):
    """Brama/furtka w ogrodzeniu: przesuwna — skrzydło z kierunkiem przesuwu; furtka — skrzydło z łukiem."""
    from .dims import arrowhead
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d)
    W = float(np.hypot(*(B - A)))
    with c.on(layer):
        if kind == "przesuwna":
            c.line(A + n * 0.15, B + n * 0.15, pen="srednia")
            a0, a1 = A + d * W * 0.7 + n * (0.15 + 2 * k), A + d * W * 0.2 + n * (0.15 + 2 * k)
            c.line(a0, a1, pen="cienka")
            arrowhead(c, a1, a1 - a0, 2.0, 12, True, layer)
        else:
            tip = A + n * W
            c.line(A, tip, pen="srednia")
            a0 = math.degrees(math.atan2(d[1], d[0]))
            c.arc(A, W, a0, a0 + 90, pen="b_cienka")
