"""Oznaczenia graficzne materiałów w przekrojach (PN-B-01030:2000 + uzupełnienia wg praktyki biur).

Kreskowania są generowane jako GEOMETRIA (odcinki, łuki, wypełnienia) przycięta biblioteką shapely do wieloboku.
Rozstawy i rozmiary motywów są podawane w mm NA ARKUSZU i przeliczane przez ``c.k`` — wygląd kreskowania nie
zależy więc od podziałki rzutni (1:20, 1:50, 1:100 wyglądają tak samo "gęsto").

Kody wzorów odpowiadają polu ``kreskowanie`` materiałów w ``model/budynek.yaml`` (np. MUR_SILIKAT).

Źródło oznaczeń:
* PN-B-01030:2000 (tabl. 1): powierzchnia gruntu, podsypka/tynk/zaprawa (kropki), beton niezbrojony i kamień
  (kreski przerywane 45°), beton zbrojony (gęste kreski przerywane 45°), beton lekki (+ kółka), cegły i pustaki
  (linie 45°), drewno (poprzecznie / wzdłuż włókien), sklejka, płyty drewnopochodne, metale (zaczernienie),
  izolacja termiczna i akustyczna (wężyk / zygzak), izolacja wodochronna (pas czarno-biały), szkło, tworzywa.
* Praktyka (materiały nieujęte w normie — oznaczenie przyjęte i objaśniane w legendzie): mur silikatowy,
  rozróżnienie izolacji miękkiej/twardej (wężyk = wełna, zygzak = EPS/XPS/PIR), paroizolacja, grunty
  (nasyp, piasek, żwir, pospółka, ziemia urodzajna), jastrych, płytki.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, Point, Polygon
from shapely.geometry.base import BaseGeometry

from .geom import (arr, circle_pts, dir_deg, lines_of, perp, polygons_of, rect_pts, stable_seed, strip_frame,
                   to_polygon, unit)

HATCH_LAYER = "A-KRESKOWANIE"


@dataclass
class Pattern:
    code: str
    name: str
    source: str
    fn: Callable
    kind: str = "area"   # area | strip (warstwa kierunkowa) | membrane (warstwa cienka / linia)


PATTERNS: dict[str, Pattern] = {}

ALIASES = {
    "ZELBET": "ZELBET", "ŻELBET": "ZELBET", "BETON_ZBROJONY": "ZELBET", "ZB": "ZELBET",
    "BETON": "BETON", "KAMIEN": "BETON", "BETON_NIEZBROJONY": "BETON",
    "SILIKAT": "MUR_SILIKAT", "MUR_SILIKAT": "MUR_SILIKAT", "CERAMIKA": "MUR_CERAMIKA", "CEGLA": "MUR_CERAMIKA",
    "PUSTAK": "MUR_CERAMIKA", "MUR": "MUR_CERAMIKA",
    "BETON_KOMORKOWY": "BETON_KOMORKOWY", "GAZOBETON": "BETON_KOMORKOWY", "BETON_LEKKI": "BETON_LEKKI",
    "WELNA": "IZOL_MIEKKA", "WEŁNA": "IZOL_MIEKKA", "IZOLACJA_MIEKKA": "IZOL_MIEKKA", "MW": "IZOL_MIEKKA",
    "EPS": "IZOL_TWARDA", "STYROPIAN": "IZOL_TWARDA", "IZOLACJA_TWARDA": "IZOL_TWARDA",
    "XPS": "IZOL_XPS", "PIR": "IZOL_PIR",
    "HYDRO": "IZOL_PRZECIWWODNA", "PAPA": "IZOL_PRZECIWWODNA", "MEMBRANA_PVC": "IZOL_PRZECIWWODNA",
    "FOLIA_PE": "PAROIZOLACJA",
    "STAL": "STAL", "METAL": "STAL", "ALUMINIUM": "STAL",
    "DREWNO": "DREWNO_POPRZ", "SZKLO": "SZKLO", "SZKŁO": "SZKLO",
    "TYNK": "TYNK", "ZAPRAWA": "TYNK", "PODSYPKA": "PIASEK", "GK": "PLYTA_GK",
    "JASTRYCH": "JASTRYCH", "WYLEWKA": "JASTRYCH", "PLYTKI": "PLYTKI", "GRES": "PLYTKI",
    "GRUNT": "GRUNT_RODZIMY", "ZASYPKA": "NASYP", "ZWIR": "ZWIR", "ŻWIR": "ZWIR",
}


def resolve(code: str) -> str:
    c = code.upper().strip()
    if c in PATTERNS:
        return c
    if c in ALIASES:
        return ALIASES[c]
    raise KeyError(f"Nieznane oznaczenie materiału {code!r}. Dostępne: {sorted(PATTERNS)}")


def register(code, name, source, kind="area"):
    def deco(fn):
        PATTERNS[code] = Pattern(code, name, source, fn, kind)
        return fn
    return deco


# ================================================================================================ narzędzia
def _parallel(poly: BaseGeometry, angle: float, spacing: float, phase: float = 0.0):
    """Linie równoległe (kąt [°], rozstaw w jednostkach płótna) przycięte do wieloboku.

    Położenie linii zakotwiczone w początku układu — sąsiednie wieloboki mają ciągłe kreskowanie."""
    d = dir_deg(angle)
    n = perp(d)
    x0, y0, x1, y1 = poly.bounds
    corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    s = corners @ n
    t = corners @ d
    smin, smax = s.min(), s.max()
    tmin, tmax = t.min() - spacing, t.max() + spacing
    k0 = math.floor((smin - phase) / spacing)
    k1 = math.ceil((smax - phase) / spacing)
    segs = []
    for k in range(k0, k1 + 1):
        ss = phase + k * spacing
        segs.append([n * ss + d * tmin, n * ss + d * tmax])
    if not segs:
        return []
    ml = MultiLineString(segs)
    return lines_of(ml.intersection(poly))


def _parallel_dashed(poly, angle, spacing, dash, gap, stagger=0.5):
    """Linie przerywane równoległe (beton). ``stagger`` — przesunięcie wzoru w kolejnych liniach (ułamek okresu)."""
    d = dir_deg(angle)
    n = perp(d)
    x0, y0, x1, y1 = poly.bounds
    corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    s = corners @ n
    t = corners @ d
    per = dash + gap
    k0 = math.floor(s.min() / spacing)
    k1 = math.ceil(s.max() / spacing)
    segs = []
    for k in range(k0, k1 + 1):
        ss = k * spacing
        off = (k * stagger * per) % per
        j0 = math.floor((t.min() - off) / per) - 1
        j1 = math.ceil((t.max() - off) / per) + 1
        for j in range(j0, j1 + 1):
            ta = off + j * per
            segs.append([n * ss + d * ta, n * ss + d * (ta + dash)])
    return lines_of(MultiLineString(segs).intersection(poly))


def _rng(poly, seed=None):
    return np.random.default_rng(seed if seed is not None else stable_seed(poly.bounds, poly.area))


def _random_points(poly, density_per_mm2: float, k: float, rng, min_dist_mm: float = 0.0, inset: float = 0.0):
    """Punkty losowe (rozkład "jittered grid" — równomierny, bez skupisk) wewnątrz wieloboku."""
    x0, y0, x1, y1 = poly.bounds
    step = 1.0 / math.sqrt(density_per_mm2) * k  # jednostki płótna
    if step <= 0:
        return np.zeros((0, 2))
    xs = np.arange(x0, x1 + step, step)
    ys = np.arange(y0, y1 + step, step)
    if len(xs) * len(ys) > 400000:
        step *= math.sqrt(len(xs) * len(ys) / 400000)
        xs = np.arange(x0, x1 + step, step)
        ys = np.arange(y0, y1 + step, step)
    gx, gy = np.meshgrid(xs, ys)
    pts = np.column_stack([gx.ravel(), gy.ravel()])
    pts = pts + (rng.random(pts.shape) - 0.5) * step * 0.9
    target = poly.buffer(-inset) if inset > 0 else poly
    if target.is_empty:
        return np.zeros((0, 2))
    inside = shapely.contains_xy(target, pts[:, 0], pts[:, 1])
    return pts[inside]


def _dots(c, poly, density, rng, layer, dot_mm=0.14, pen=0.25):
    pts = _random_points(poly, density, c.k, rng, inset=0.15 * c.k)
    L = dot_mm * c.k
    ang = rng.random(len(pts)) * math.pi
    for p, a in zip(pts, ang):
        c.prims.append(_seg(layer, pen, p, p + np.array([math.cos(a), math.sin(a)]) * L))


def _seg(layer, pen, a, b):
    from .core import PLine
    return PLine(layer, pen, None, None, None, np.array([a, b]), False, 1.0)


def _emit_lines(c, lines, layer, pen=None, lt=None):
    from .core import PLine
    for ln in lines:
        if len(ln) >= 2:
            c.prims.append(PLine(layer, pen, lt, None, None, np.asarray(ln), False, 1.0))


def _local(ctr, u, v):
    """Funkcja: współrzędne lokalne paska (x wzdłuż u, y wzdłuż v) -> płótno."""
    def f(xy):
        xy = arr(xy)
        return ctr + np.outer(xy[:, 0], u) + np.outer(xy[:, 1], v)
    return f


def _strip(poly, axis=None):
    """Oś paska: z parametru ``axis`` (p1, p2) albo z minimalnego prostokąta opisanego."""
    if axis is not None:
        p1, p2 = np.asarray(axis[0], float), np.asarray(axis[1], float)
        u = unit(p2 - p1)
        if u[0] < -1e-9 or (abs(u[0]) < 1e-9 and u[1] < 0):
            u = -u
        v = perp(u)
        pts = np.asarray(poly.exterior.coords)
        su, sv = pts @ u, pts @ v
        ctr = u * (su.min() + su.max()) / 2 + v * (sv.min() + sv.max()) / 2
        return ctr, u, v, su.max() - su.min(), sv.max() - sv.min()
    return strip_frame(poly)


# ================================================================================================ wzory — PN-B-01030
@register("ZELBET", "Beton zbrojony (żelbet)", "PN-B-01030:2000 poz. 4")
def _zelbet(c, poly, layer, angle=45.0, spacing=1.0, **kw):
    k = c.k
    _emit_lines(c, _parallel_dashed(poly, angle, spacing * k, 4.5 * k, 0.7 * k, stagger=0.37), layer)


@register("BETON", "Beton niezbrojony, kamień", "PN-B-01030:2000 poz. 3")
def _beton(c, poly, layer, angle=45.0, spacing=1.4, **kw):
    k = c.k
    _emit_lines(c, _parallel_dashed(poly, angle, spacing * k, 2.0 * k, 1.1 * k, stagger=0.45), layer)


@register("BETON_LEKKI", "Beton lekki", "PN-B-01030:2000 poz. 5")
def _beton_lekki(c, poly, layer, angle=45.0, spacing=1.6, seed=None, **kw):
    k = c.k
    _emit_lines(c, _parallel(poly, angle, spacing * k), layer)
    _circles(c, poly, 0.10, (0.28, 0.40), layer, _rng(poly, seed))


@register("BETON_KOMORKOWY", "Beton komórkowy (autoklawizowany)", "PN-B-01030:2000 poz. 5 (beton lekki)")
def _beton_kom(c, poly, layer, angle=45.0, spacing=2.0, seed=None, **kw):
    k = c.k
    _emit_lines(c, _parallel(poly, angle, spacing * k), layer)
    _circles(c, poly, 0.16, (0.22, 0.34), layer, _rng(poly, seed))


@register("MUR_CERAMIKA", "Mur z cegieł i pustaków ceramicznych", "PN-B-01030:2000 poz. 7")
def _ceramika(c, poly, layer, angle=45.0, spacing=1.2, **kw):
    _emit_lines(c, _parallel(poly, angle, spacing * c.k), layer)


@register("MUR_SILIKAT", "Mur z bloczków wapienno-piaskowych (silikatowych)",
          "oznaczenie przyjęte (odmiana poz. 7 PN-B-01030)")
def _silikat(c, poly, layer, angle=45.0, spacing=1.2, **kw):
    k = c.k
    _emit_lines(c, _parallel(poly, angle, spacing * k), layer)
    _emit_lines(c, _parallel_dashed(poly, angle + 90.0, 3.6 * k, 0.9 * k, 2.7 * k, stagger=0.5), layer)


@register("DREWNO_POPRZ", "Drewno — przekrój prostopadły do włókien", "PN-B-01030:2000 poz. 8a")
def _drewno_poprz(c, poly, layer, **kw):
    mrr = poly.minimum_rotated_rectangle
    q = np.asarray(mrr.exterior.coords)[:4]
    _emit_lines(c, lines_of(MultiLineString([[q[0], q[2]], [q[1], q[3]]]).intersection(poly)), layer)
    ctr = q.mean(axis=0)
    r_max = 0.5 * min(np.linalg.norm(q[1] - q[0]), np.linalg.norm(q[2] - q[1]))
    for f in (0.3, 0.55, 0.8):
        ring = LineString(np.vstack([circle_pts(ctr, r_max * f, 48), circle_pts(ctr, r_max * f, 48)[:1]]))
        _emit_lines(c, lines_of(ring.intersection(poly)), layer)


@register("DREWNO_WZDL", "Drewno — przekrój wzdłuż włókien", "PN-B-01030:2000 poz. 8b", kind="strip")
def _drewno_wzdl(c, poly, layer, axis=None, spacing=1.1, **kw):
    k = c.k
    ctr, u, v, L, t = _strip(poly, axis)
    f = _local(ctr, u, v)
    n = max(1, int(t / (spacing * k)))
    lines = []
    xs = np.linspace(-L / 2, L / 2, max(8, int(L / (0.8 * k))))
    for i in range(n):
        y = -t / 2 + (i + 0.5) * t / n
        ph = i * 1.7
        amp = 0.18 * k
        wl = 18.0 * k
        ys = y + amp * np.sin(2 * math.pi * xs / wl + ph)
        lines.append(f(np.column_stack([xs, ys])))
    ml = MultiLineString([ln.tolist() for ln in lines])
    _emit_lines(c, lines_of(ml.intersection(poly)), layer)


@register("SKLEJKA", "Sklejka", "PN-B-01030:2000 poz. 9", kind="strip")
def _sklejka(c, poly, layer, axis=None, spacing=0.4, **kw):
    ctr, u, v, L, t = _strip(poly, axis)
    _emit_lines(c, _parallel(poly, math.degrees(math.atan2(u[1], u[0])), spacing * c.k,
                             phase=float(ctr @ v)), layer)


@register("PLYTA_DREWNOPOCHODNA", "Płyty drewnopochodne (OSB, MFP, wiórowe)", "PN-B-01030:2000 poz. 10",
          kind="strip")
def _osb(c, poly, layer, axis=None, spacing=1.5, **kw):
    ctr, u, v, L, t = _strip(poly, axis)
    _emit_lines(c, _parallel(poly, math.degrees(math.atan2(u[1], u[0])) + 90.0, spacing * c.k,
                             phase=float(ctr @ u)), layer)


@register("STAL", "Metale (stal, aluminium) — zaczernienie", "PN-B-01030:2000 poz. 11")
def _stal(c, poly, layer, **kw):
    ctr, u, v, L, t = strip_frame(poly)
    if t / c.k <= 3.0:
        c.fill(poly, "A-WYPELNIENIA", "#000000")
    else:
        _emit_lines(c, _parallel(poly, 45.0, 0.5 * c.k), layer)
        _emit_lines(c, _parallel(poly, 135.0, 0.5 * c.k), layer)


def _meander(c, poly, layer, axis, pitch_rel, pitch_min, pitch_max, gap_mm=0.15):
    k = c.k
    ctr, u, v, L, t = _strip(poly, axis)
    f = _local(ctr, u, v)
    g = gap_mm * k
    tt = t - 2 * g
    if tt <= 0:
        return
    p = min(max(pitch_rel * t / k, pitch_min), pitch_max) * k   # rozstaw nóżek
    r = p / 2.0
    y0, y1 = -tt / 2, tt / 2
    if tt < 2 * r + 0.05 * k:  # za cienko na nóżki — sinusoida
        xs = np.linspace(-L / 2, L / 2, max(16, int(L / (0.2 * k))))
        ys = (tt / 2) * np.sin(2 * math.pi * xs / (2 * p))
        pts = [np.column_stack([xs, ys])]
    else:
        n = int(math.ceil(L / p)) + 2
        x = -L / 2 - p
        pts_list = []
        up = True
        for i in range(n):
            if up:
                pts_list.append([x, y0 + r if i else y0])
                pts_list.append([x, y1 - r])
                a = np.linspace(math.pi, 0.0, 10)
                pts_list.extend(np.column_stack([x + r + r * np.cos(a), y1 - r + r * np.sin(a)]).tolist())
            else:
                pts_list.append([x, y1 - r])
                pts_list.append([x, y0 + r])
                a = np.linspace(math.pi, 2 * math.pi, 10)
                pts_list.extend(np.column_stack([x + r + r * np.cos(a), y0 + r + r * np.sin(a)]).tolist())
            x += p
            up = not up
        pts = [np.array(pts_list)]
    ls = LineString(f(pts[0]).tolist())
    _emit_lines(c, lines_of(ls.intersection(poly)), layer)


def _zigzag(c, poly, layer, axis, per_rel, per_min, per_max, gap_mm=0.15, double=False):
    k = c.k
    ctr, u, v, L, t = _strip(poly, axis)
    f = _local(ctr, u, v)
    g = gap_mm * k
    tt = t - 2 * g
    if tt <= 0:
        return
    per = min(max(per_rel * t / k, per_min), per_max) * k
    n = int(math.ceil(L / per)) + 2
    xs = -L / 2 - per + np.arange(2 * n + 1) * per / 2.0
    ys = np.where(np.arange(len(xs)) % 2 == 0, -tt / 2, tt / 2)
    ls = LineString(f(np.column_stack([xs, ys])).tolist())
    _emit_lines(c, lines_of(ls.intersection(poly)), layer)
    if double:
        ls2 = LineString(f(np.column_stack([xs + per / 2.0, ys])).tolist())
        _emit_lines(c, lines_of(ls2.intersection(poly)), layer)


@register("IZOL_MIEKKA", "Izolacja termiczna miękka (wełna mineralna) — „wężyk”", "PN-B-01030:2000 poz. 12",
          kind="strip")
def _welna(c, poly, layer, axis=None, **kw):
    _meander(c, poly, layer, axis, 0.33, 0.7, 2.6)


@register("IZOL_TWARDA", "Izolacja termiczna twarda (EPS) — zygzak", "PN-B-01030:2000 poz. 12", kind="strip")
def _eps(c, poly, layer, axis=None, **kw):
    _zigzag(c, poly, layer, axis, 0.55, 1.0, 4.0)


@register("IZOL_XPS", "Izolacja termiczna twarda (XPS) — zygzak podwójny", "oznaczenie przyjęte (odmiana poz. 12)",
          kind="strip")
def _xps(c, poly, layer, axis=None, **kw):
    _zigzag(c, poly, layer, axis, 0.7, 1.4, 4.4, double=True)


@register("IZOL_PIR", "Izolacja termiczna twarda (PIR/PUR) — zygzak z okładzinami",
          "oznaczenie przyjęte (odmiana poz. 12)", kind="strip")
def _pir(c, poly, layer, axis=None, **kw):
    k = c.k
    ctr, u, v, L, t = _strip(poly, axis)
    f = _local(ctr, u, v)
    g = 0.35 * k
    if t > 3 * g:
        for y in (-t / 2 + g, t / 2 - g):
            ls = LineString(f([[-L, y], [L, y]]).tolist())
            _emit_lines(c, lines_of(ls.intersection(poly)), layer)
    _zigzag(c, poly, layer, axis, 0.55, 1.0, 4.0, gap_mm=0.5)


def _membrane_center(poly, axis):
    ctr, u, v, L, t = _strip(poly, axis)
    return ctr - u * L / 2, ctr + u * L / 2, t


@register("IZOL_PRZECIWWODNA", "Izolacja przeciwwodna (papa, membrana) — pas czarno-biały",
          "PN-B-01030:2000 poz. 13", kind="membrane")
def _hydro(c, poly, layer, axis=None, **kw):
    a, b, t = _membrane_center(poly, axis)
    membrane(c, [a, b], "przeciwwodna", width_mm=max(0.8, min(t / c.k, 1.4)))


@register("IZOL_PRZECIWWILGOCIOWA", "Izolacja przeciwwilgociowa — linia pogrubiona", "praktyka (PN-B-01025:2004)",
          kind="membrane")
def _hydro2(c, poly, layer, axis=None, **kw):
    a, b, t = _membrane_center(poly, axis)
    membrane(c, [a, b], "przeciwwilgociowa")


@register("PAROIZOLACJA", "Paroizolacja (folia PE) — linia kreskowa", "oznaczenie przyjęte", kind="membrane")
def _paro(c, poly, layer, axis=None, **kw):
    a, b, t = _membrane_center(poly, axis)
    membrane(c, [a, b], "paroizolacja")


@register("MEMBRANA_PAROPRZEP", "Membrana paroprzepuszczalna / wiatroizolacja", "oznaczenie przyjęte",
          kind="membrane")
def _wiatro(c, poly, layer, axis=None, **kw):
    a, b, t = _membrane_center(poly, axis)
    membrane(c, [a, b], "paroprzepuszczalna")


@register("SZKLO", "Szkło i inne materiały przezroczyste", "PN-B-01030:2000 poz. 14", kind="strip")
def _szklo(c, poly, layer, axis=None, **kw):
    k = c.k
    ctr, u, v, L, t = _strip(poly, axis)
    f = _local(ctr, u, v)
    step = 7.0 * k
    segs = []
    n = int(L / step)
    for i in range(n + 1):
        x0 = -L / 2 + (i + 0.5) * step - 0.5 * k
        for j in range(3):
            xa = x0 + j * 0.45 * k
            segs.append(f([[xa - 0.3 * t, -0.42 * t], [xa + 0.3 * t, 0.42 * t]]).tolist())
    if segs:
        _emit_lines(c, lines_of(MultiLineString(segs).intersection(poly)), layer)


@register("TWORZYWO", "Tworzywa sztuczne", "PN-B-01030:2000 poz. 15")
def _tworzywo(c, poly, layer, angle=45.0, **kw):
    _emit_lines(c, _parallel(poly, angle, 0.35 * c.k), layer)


@register("TYNK", "Tynk, zaprawa", "PN-B-01030:2000 poz. 2")
def _tynk(c, poly, layer, seed=None, **kw):
    ctr, u, v, L, t = strip_frame(poly)
    if t / c.k < 0.5:
        return
    _dots(c, poly, 3.0, _rng(poly, seed), layer, 0.1)


@register("PLYTA_GK", "Płyta gipsowo-kartonowa", "oznaczenie przyjęte (odmiana poz. 2)")
def _gk(c, poly, layer, seed=None, **kw):
    ctr, u, v, L, t = strip_frame(poly)
    if t / c.k < 0.5:
        return
    _dots(c, poly, 5.0, _rng(poly, seed), layer, 0.08)


@register("JASTRYCH", "Jastrych (wylewka) cementowy/anhydrytowy", "oznaczenie przyjęte (zaprawa + kruszywo)")
def _jastrych(c, poly, layer, seed=None, **kw):
    rng = _rng(poly, seed)
    ctr, u, v, L, t = strip_frame(poly)
    if t / c.k < 0.5:
        return
    _dots(c, poly, 1.6, rng, layer, 0.12)
    pts = _random_points(poly, 0.10, c.k, rng, inset=0.5 * c.k)
    s = 0.55 * c.k
    for p in pts:
        a = rng.random() * 2 * math.pi
        tri = np.array([[math.cos(a + i * 2 * math.pi / 3), math.sin(a + i * 2 * math.pi / 3)] for i in range(3)]) * s / 1.732
        tri = tri + p
        c.polygon(tri, layer)


@register("PLYTKI", "Płytki ceramiczne / gres (okładzina)", "oznaczenie przyjęte")
def _plytki(c, poly, layer, **kw):
    ctr, u, v, L, t = strip_frame(poly)
    if t / c.k < 0.5:
        return
    _emit_lines(c, _parallel(poly, 45.0, 0.45 * c.k), layer)
    _emit_lines(c, _parallel(poly, math.degrees(math.atan2(u[1], u[0])) + 90.0, 8.0 * c.k), layer, pen="cienka")


# ------------------------------------------------------------------------------------------------ grunty
def _circles(c, poly, density, r_mm, layer, rng):
    pts = _random_points(poly, density, c.k, rng, inset=r_mm[1] * c.k * 1.2)
    rs = (r_mm[0] + (r_mm[1] - r_mm[0]) * rng.random(len(pts))) * c.k
    placed = []
    for p, r in zip(pts, rs):
        ok = True
        for q, rq in placed[-40:]:
            if (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 < (r + rq + 0.2 * c.k) ** 2:
                ok = False
                break
        if ok:
            placed.append((p, r))
            c.circle(p, r, layer, pen="b_cienka")


@register("GRUNT_RODZIMY", "Grunt rodzimy (powierzchnia gruntu w przekroju)", "PN-B-01030:2000 poz. 1")
def _grunt(c, poly, layer, depth_mm=2.4, **kw):
    """Pas oznaczenia przy krawędziach "górnych" wieloboku (normalna zewn. skierowana w górę)."""
    k = c.k
    ext = np.asarray(poly.exterior.coords)
    if poly.exterior.is_ccw is False:
        ext = ext[::-1]
    for a, b in zip(ext[:-1], ext[1:]):
        d = b - a
        L = np.hypot(*d)
        if L < 1e-9:
            continue
        uu = d / L
        nout = np.array([uu[1], -uu[0]])  # dla CCW normalna zewnętrzna = obrót o -90°
        if nout[1] < 0.5:
            continue
        ground_band(c, [a, b], layer=layer, depth_mm=depth_mm, below=-nout, clip=poly)


def ground_band(c, pts, layer=HATCH_LAYER, depth_mm=2.4, period_mm=2.4, below=None, clip=None):
    """Symbol powierzchni gruntu wg PN-B-01030 (poz. 1): pod linią terenu pas trójkątów z kreskowaniem."""
    k = c.k
    pts = arr(pts)
    D = depth_mm * k
    per = period_mm * k
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a
        L = float(np.hypot(*d))
        if L < 1e-9:
            continue
        uu = d / L
        nb = below if below is not None else np.array([uu[1], -uu[0]])
        nb = np.asarray(nb) / np.hypot(*nb)
        n = max(1, int(round(L / per)))
        pp = L / n
        zig = []
        segs = []
        for i in range(n + 1):
            x = i * pp
            zig.append(a + uu * x + (nb * D if i % 2 else 0 * nb))
        for i in range(n):
            x0 = i * pp
            if i % 2 == 0:  # trójkąt o wierzchołku w dole: kreski równoległe do boku
                p0 = a + uu * x0
                p1 = a + uu * (x0 + pp) + nb * D
                for f in (0.35, 0.7):
                    s0 = p0 + uu * pp * f
                    segs.append([s0, s0 + (p1 - p0) * (1 - f) * 0.98])
        geo = MultiLineString([np.asarray(zig).tolist()] + [np.asarray(s).tolist() for s in segs])
        if clip is not None:
            geo = geo.intersection(clip)
        _emit_lines(c, lines_of(geo), layer)


@register("NASYP", "Nasyp, zasypka (grunt nasypowy)", "oznaczenie przyjęte")
def _nasyp(c, poly, layer, seed=None, **kw):
    rng = _rng(poly, seed)
    k = c.k
    pts = _random_points(poly, 0.35, k, rng, inset=0.6 * k)
    for i, p in enumerate(pts):
        a = rng.random() * math.pi
        L = (0.5 + 0.5 * rng.random()) * k
        if i % 3 == 0:
            c.circle(p, 0.22 * k, layer, pen="b_cienka")
        else:
            dvec = np.array([math.cos(a), math.sin(a)]) * L / 2
            c.prims.append(_seg(layer, None, p - dvec, p + dvec))
    _dots(c, poly, 0.5, rng, layer, 0.12)


@register("PIASEK", "Piasek, podsypka piaskowa", "PN-B-01030:2000 poz. 2 (podsypka)")
def _piasek(c, poly, layer, seed=None, **kw):
    _dots(c, poly, 1.3, _rng(poly, seed), layer, 0.12)


@register("ZWIR", "Żwir, tłuczeń", "oznaczenie przyjęte")
def _zwir(c, poly, layer, seed=None, **kw):
    _circles(c, poly, 0.45, (0.25, 0.55), layer, _rng(poly, seed))


@register("POSPOLKA", "Pospółka (mieszanka piaskowo-żwirowa)", "oznaczenie przyjęte")
def _pospolka(c, poly, layer, seed=None, **kw):
    rng = _rng(poly, seed)
    _circles(c, poly, 0.22, (0.25, 0.5), layer, rng)
    _dots(c, poly, 0.9, rng, layer, 0.12)


@register("HUMUS", "Ziemia urodzajna (humus)", "oznaczenie przyjęte")
def _humus(c, poly, layer, seed=None, **kw):
    rng = _rng(poly, seed)
    k = c.k
    pts = _random_points(poly, 0.22, k, rng, inset=0.8 * k)
    for p in pts:
        for dx in (-0.35, 0.0, 0.35):
            a = p + np.array([dx * k, 0])
            c.prims.append(_seg(layer, None, a, a + np.array([dx * 0.6 * k, 0.6 * k])))
    _dots(c, poly, 0.6, rng, layer, 0.12)


# ================================================================================================ API
def hatch(c, shape, material: str, layer: str = HATCH_LAYER, outline: bool = False, outline_layer: str | None = None,
          outline_pen=None, **params):
    """Kreskuje wielobok(i) ``shape`` (shapely lub lista punktów) wzorem materiału ``material``.

    Parametry wzorów (opcjonalne): ``angle`` [°] (kreskowania liniowe; sąsiednie elementy kreskować w różnych
    kierunkach), ``spacing`` [mm papieru], ``axis`` ((p1, p2) — kierunek warstwy dla wzorów kierunkowych: wężyk,
    zygzak, drewno wzdłużne), ``seed`` (wzory losowe).
    """
    code = resolve(material)
    g = to_polygon(shape)
    for poly in polygons_of(g):
        if poly.area <= 0:
            continue
        PATTERNS[code].fn(c, poly, layer, **params)
        if outline:
            c.geom(poly, outline_layer or layer, pen=outline_pen)


def membrane(c, pts, kind: str = "przeciwwodna", layer: str = "A-IZOL-WODNA", width_mm: float | None = None):
    """Warstwa cienka rysowana wzdłuż łamanej ``pts``:

    * ``przeciwwodna`` — pas czarno-biały (PN-B-01030 poz. 13): gruba czarna linia z białymi przerwami,
    * ``przeciwwilgociowa`` — linia pogrubiona,
    * ``paroizolacja`` — linia kreskowa drobna średniej grubości,
    * ``paroprzepuszczalna`` — linia punktowa krótka cienka.
    """
    pts = arr(pts)
    if kind == "przeciwwodna":
        w = width_mm or 0.9
        c.polyline(pts, layer, pen=w, color="#000000")
        c.polyline(pts, layer, pen=max(0.25, w * 0.45), lt="KRESKOWA_DROBNA", color="#ffffff", z=23.5,
                   lt_scale=0.9)
    elif kind == "przeciwwilgociowa":
        c.polyline(pts, layer, pen=width_mm or 0.7)
    elif kind == "paroizolacja":
        c.polyline(pts, layer, pen=width_mm or 0.35, lt="KRESKOWA_DROBNA")
    elif kind == "paroprzepuszczalna":
        c.polyline(pts, layer, pen=width_mm or 0.25, lt="PUNKTOWA_KROTKA", lt_scale=0.6)
    else:
        raise ValueError(kind)


def ground_line(c, pts, layer: str = "A-TEREN", band: bool = True, depth_mm: float = 2.4):
    """Linia terenu w przekroju/elewacji: linia gruba + (opcjonalnie) pas oznaczenia gruntu pod nią."""
    c.polyline(pts, layer, pen="b_gruba")
    if band:
        ground_band(c, pts, HATCH_LAYER, depth_mm)


# ------------------------------------------------------------------------------------------------ legenda
def legend(c, x: float, y_top: float, codes, cols: int = 1, col_w: float = 88.0, sw: tuple = (14.0, 7.0),
           h: float = 2.2, title: str | None = "OZNACZENIA MATERIAŁÓW (PN-B-01030)", row_gap: float = 2.2,
           show_source: bool = True, layer: str = "R-LEGENDA"):
    """Legenda materiałów: próbka (kreskowanie w ramce) + nazwa (+ źródło oznaczenia). Rysowana na płótnie ``c``
    (zwykle arkusz, mm). Zwraca prostokąt (x0, y0, x1, y1)."""
    from .sheet import wrap
    k = c.k
    y = y_top
    if title:
        c.text((x, y - 3.5 * k), title, 3.5, style="bold", layer=layer)
        y -= 7.0 * k
    rows = []
    for code in codes:
        cd = resolve(code) if not isinstance(code, tuple) else resolve(code[0])
        label = PATTERNS[cd].name if not isinstance(code, tuple) else code[1]
        rows.append((cd, label))
    n = len(rows)
    per_col = int(math.ceil(n / cols))
    ymin = y
    for i, (cd, label) in enumerate(rows):
        col = i // per_col
        r = i % per_col
        x0 = x + col * col_w * k
        rh = sw[1] * k + row_gap * k
        y0 = y - (r + 1) * rh + row_gap * k
        box = Polygon(rect_pts(x0, y0, x0 + sw[0] * k, y0 + sw[1] * k))
        pat = PATTERNS[cd]
        if pat.kind == "membrane":
            PATTERNS[cd].fn(c, box, HATCH_LAYER, axis=[(x0, y0 + sw[1] * k / 2), (x0 + sw[0] * k, y0 + sw[1] * k / 2)])
            c.rect(x0, y0, x0 + sw[0] * k, y0 + sw[1] * k, layer=layer, pen="b_cienka", lt="KROPKOWA")
        elif cd == "GRUNT_RODZIMY":
            ground_line(c, [(x0, y0 + sw[1] * k * 0.8), (x0 + sw[0] * k, y0 + sw[1] * k * 0.8)], layer=layer)
        else:
            hatch(c, box, cd, HATCH_LAYER)
            c.rect(x0, y0, x0 + sw[0] * k, y0 + sw[1] * k, layer=layer, pen="srednia")
        tx = x0 + (sw[0] + 2.5) * k
        avail = col_w - sw[0] - 4.0
        ls = wrap(label, avail, h)
        yy = y0 + sw[1] * k / 2 + (len(ls) - 1) * h * 1.5 * k / 2 + (0.8 * k if show_source else -h * k / 2)
        for j, s in enumerate(ls):
            c.text((tx, yy - j * h * 1.5 * k), s, h, layer=layer)
        if show_source:
            c.text((tx, yy - len(ls) * h * 1.5 * k + 0.2 * k), PATTERNS[cd].source, 1.8, layer=layer,
                   style="italic", color="#505050")
        ymin = min(ymin, y0)
    return (x, ymin, x + cols * col_w * k, y_top)
