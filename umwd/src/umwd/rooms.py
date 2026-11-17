"""Silnik układu pomieszczeń: pasma elewacyjne (pokoje w module), korytarz liczony za pomieszczeniami,
strefa środkowa, ściany jako różnica (wnętrze − pomieszczenia), drzwi, okna.

Wszystko w układzie e,n [m]. Pomieszczenia są wielokątami W ŚWIETLE ŚCIAN (PN-ISO 9836: powierzchnia netto),
więc szczeliny między nimi = ściany działowe (poché).
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box
from shapely.ops import unary_union, nearest_points
from shapely import affinity
from .frames import Frame, annulus_sector

MITRE = dict(join_style=2, mitre_limit=10.0)


def polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon) and not p.is_empty]


def largest(g):
    ps = polys(g)
    return max(ps, key=lambda p: p.area) if ps else Polygon()


def clean(g, eps=0.02):
    """Usuwa drobne odpryski (opening/closing)."""
    if g.is_empty:
        return g
    g2 = g.buffer(-eps, **MITRE).buffer(eps, **MITRE)
    return g2.intersection(g) if not g2.is_empty else g2


def ext_band(plate: Polygon, thick_of_segment, min_len=0.01):
    """Strefa ścian zewnętrznych: dla każdego odcinka brzegu płyty pasek do wnętrza o grubości thick_of_segment(a,b)."""
    bands = []
    rings = [plate.exterior] + list(plate.interiors)
    for ri, ring in enumerate(rings):
        cs = list(ring.coords)
        # orientacja: wnętrze po lewej dla CCW zewnętrznego; dla otworów odwrotnie
        ccw = ring.is_ccw
        inner_left = ccw if ri == 0 else (not ccw)
        for a, b in zip(cs[:-1], cs[1:]):
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            if L < min_len:
                continue
            t = thick_of_segment(a, b)
            if t <= 0:
                continue
            ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            nx, ny = (-uy, ux) if inner_left else (uy, -ux)
            ext = min(t, 0.6)  # wydłużenie, żeby domknąć narożniki wypukłe
            pa = (a[0] - ux * 0.0, a[1] - uy * 0.0)
            pb = (b[0] + ux * 0.0, b[1] + uy * 0.0)
            q = Polygon([pa, pb, (pb[0] + nx * t, pb[1] + ny * t), (pa[0] + nx * t, pa[1] + ny * t)])
            bands.append(q.buffer(0))
    u = unary_union(bands).intersection(plate)
    # domknięcie narożników: inner = plate − u może mieć zęby w narożach wklęsłych – wygładzamy
    return u


@dataclass
class Space:
    """Pomieszczenie / przestrzeń w modelu."""
    poly: Polygon
    nazwa: str
    kod: str
    prog_id: str = ""             # pozycja programu (np. DOS.2.1.1.PR, SN.01)
    komorka: str = ""             # komórka organizacyjna (nr z tabeli 1 M.01)
    dept: str = ""                # departament / blok
    osoby: int | None = None
    uwagi: list = field(default_factory=list)
    kind: str = "room"            # room | office | corridor | core_stair | core_lift | core_lobby | shaft | void | parking ...
    furn: str | None = None       # office3 | office4 | office1 | table | wc | ...
    seats: int = 0
    facade_dir: tuple | None = None   # kierunek do elewacji (wektor en) – meble przy oknie
    numer: str = ""
    label: bool = True
    tags: set = field(default_factory=set)
    door_to: str | None = None    # 'corr' | numer pomieszczenia | None

    @property
    def area(self):
        return self.poly.area


class Run:
    """Pasmo elewacyjne prostoliniowe: oś x wzdłuż lica, y do wnętrza (od lica zewnętrznego obrysu)."""

    def __init__(self, frame: Frame, x0: float, x1: float, ext: float, name: str, reverse=False, side=+1, origin_y=0.0):
        # frame: lokalny układ, w którym lico elewacji to prosta y = origin_y, wnętrze w stronę +y*side
        self.f = frame
        self.x0, self.x1 = x0, x1
        self.ext = ext
        self.name = name
        self.reverse = reverse
        self.side = side
        self.y0 = origin_y
        self.items = []

    def y(self, depth):
        return self.y0 + self.side * depth

    def rect(self, a, b, d0, d1):
        ya, yb = self.y(d0), self.y(d1)
        return self.f.rect(min(a, b), max(a, b), min(ya, yb), max(ya, yb))

    @property
    def length(self):
        return abs(self.x1 - self.x0)

    def inward(self):
        """Wektor en do wnętrza."""
        return (self.f.ey[0] * self.side, self.f.ey[1] * self.side)


class ArcRun:
    """Pasmo na łuku: środek c (lokalne x,y w frame), promień lica R (zewn. obrys), kąty a0→a1 (stopnie)."""

    def __init__(self, frame: Frame, c, R, a0, a1, ext, name):
        self.f = frame
        self.c = c
        self.R = R
        self.a0, self.a1 = a0, a1
        self.ext = ext
        self.name = name
        self.items = []

    def sector(self, a, b, d0, d1):
        r1 = self.R - d0
        r0 = max(0.0, self.R - d1)
        lo, hi = min(a, b), max(a, b)
        return annulus_sector(self.f, self.c, r0, r1, lo, hi)


def place_run(run: Run, seq, gap_default=0.10, start=None, align="start"):
    """Układa elementy seq wzdłuż pasma. seq: lista dict {w, depth, gap(opcjonalnie), ...}.
    Zwraca listę (x_a, x_b, item). Kierunek: od x0 do x1."""
    out = []
    total = sum(it["w"] for it in seq) + sum(it.get("gap", gap_default) for it in seq[1:])
    L = run.length
    if start is None:
        start = 0.0 if align == "start" else (L - total if align == "end" else (L - total) / 2)
    cur = start
    sgn = 1 if run.x1 >= run.x0 else -1
    for k, it in enumerate(seq):
        if k > 0:
            cur += it.get("gap", gap_default)
        a = run.x0 + sgn * cur
        b = run.x0 + sgn * (cur + it["w"])
        out.append((a, b, it))
        cur += it["w"]
    return out, total


def corridor_behind(run: Run, placed, wall=0.12, corr=1.80, ext_a=0.0, ext_b=0.0, gap_default=0.10):
    """Korytarz za elementami pasma: prostokąty za każdym elementem + łączniki przy zmianie głębokości."""
    parts = []
    sgn = 1 if run.x1 >= run.x0 else -1
    n = len(placed)
    for i, (a, b, it) in enumerate(placed):
        if it.get("no_corr"):
            continue
        dep = run.ext + it["depth"]
        g0 = (it.get("gap", gap_default) if i > 0 else 0.0)
        g1 = (placed[i + 1][2].get("gap", gap_default) if i + 1 < n else 0.0)
        aa = a - sgn * g0 - (sgn * ext_a if i == 0 else 0.0)
        bb = b + sgn * g1 + (sgn * ext_b if i == n - 1 else 0.0)
        parts.append(run.rect(aa, bb, dep + wall, dep + wall + corr))
    # łączniki
    for i in range(n - 1):
        (a1, b1, i1), (a2, b2, i2) = placed[i], placed[i + 1]
        if i1.get("no_corr") or i2.get("no_corr"):
            continue
        d1, d2 = run.ext + i1["depth"], run.ext + i2["depth"]
        if abs(d1 - d2) < 0.01:
            continue
        if d1 < d2:   # płytszy pierwszy: łącznik po stronie i1, przy jego końcu b1
            lo, hi = b1 - sgn * corr, b2 - (b2 - a2)  # do początku i2
            parts.append(run.rect(b1 - sgn * corr, a2, d1 + wall, d2 + wall + corr))
        else:
            parts.append(run.rect(b1, a2 + sgn * corr, d2 + wall, d1 + wall + corr))
    return unary_union(parts) if parts else Polygon()


def arc_place(run: ArcRun, seq):
    """seq: lista dict {ang (stopnie), depth}. Od a0 w stronę a1."""
    out = []
    sgn = 1 if run.a1 >= run.a0 else -1
    cur = run.a0
    for it in seq:
        a, b = cur, cur + sgn * it["ang"]
        out.append((a, b, it))
        cur = b
    return out


def arc_corridor(run: ArcRun, placed, wall=0.12, corr=1.80, ext_deg=(0.0, 0.0)):
    parts = []
    sgn = 1 if run.a1 >= run.a0 else -1
    n = len(placed)
    for i, (a, b, it) in enumerate(placed):
        dep = run.ext + it["depth"]
        aa = a - sgn * (ext_deg[0] if i == 0 else 0.3)
        bb = b + sgn * (ext_deg[1] if i == n - 1 else 0.3)
        parts.append(run.sector(aa, bb, dep + wall, dep + wall + corr))
    return unary_union(parts) if parts else Polygon()


def subtract_gap(poly, others, gap):
    """poly minus (others powiększone o gap) – zapewnia ścianę o grubości gap."""
    if not others:
        return poly
    o = unary_union([x.buffer(gap, **MITRE) for x in others if not x.is_empty])
    return poly.difference(o)


def door_on(space_poly: Polygon, target: Polygon, width=0.9, wall=0.12, prefer=None):
    """Znajduje odcinek wspólnej granicy pomieszczenia z celem (korytarzem) i zwraca (p0, p1, normal_do_wnetrza)
    – położenie skrzydła drzwi na licu pomieszczenia. prefer: punkt en, do którego drzwi mają być blisko."""
    shell = space_poly.exterior
    probe = target.buffer(wall + 0.06, **MITRE)
    cs = list(shell.coords)
    best = None
    for a, b in zip(cs[:-1], cs[1:]):
        seg = LineString([a, b])
        if seg.length < width + 0.2:
            continue
        inter = seg.intersection(probe)
        if inter.is_empty:
            continue
        for g in ([inter] if inter.geom_type == "LineString" else [x for x in getattr(inter, "geoms", []) if x.geom_type == "LineString"]):
            if g.length < width + 0.2:
                continue
            score = g.length
            if prefer is not None:
                score = -Point(prefer).distance(g)
            if best is None or score > best[0]:
                best = (score, g, (a, b))
    if best is None:
        return None
    g = best[1]
    (a, b) = best[2]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    gc = list(g.coords)
    # pozycja: przy końcu bliższym 'prefer' albo 0,35 m od narożnika
    p_start, p_end = gc[0], gc[-1]
    if prefer is not None and Point(prefer).distance(Point(p_end)) < Point(prefer).distance(Point(p_start)):
        p_start, p_end = p_end, p_start
    vx, vy = p_end[0] - p_start[0], p_end[1] - p_start[1]
    lv = math.hypot(vx, vy)
    vx, vy = vx / lv, vy / lv
    off = 0.30
    p0 = (p_start[0] + vx * off, p_start[1] + vy * off)
    p1 = (p0[0] + vx * width, p0[1] + vy * width)
    # normalna do wnętrza pomieszczenia
    mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
    nx, ny = -vy, vx
    if not space_poly.contains(Point(mx + nx * 0.2, my + ny * 0.2)):
        nx, ny = -nx, -ny
    return p0, p1, (nx, ny)
