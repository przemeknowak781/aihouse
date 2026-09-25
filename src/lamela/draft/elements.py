"""Budowa elementów przeciętych (rzuty, przekroje) z warstw materiałowych.

* ``CutSet`` — zbiór wieloboków przekroju z priorytetami (konstrukcja > ścianki działowe > izolacje > wykończenie):
  nakładające się fragmenty niższego priorytetu są odejmowane, wieloboki tego samego materiału i rodzaju scalane
  (brak linii na styku jednorodnego muru), kontur rysowany piórem wg rodzaju (konstrukcja — gruba, izolacja —
  średnia, tynk — bardzo cienka), wnętrze kreskowane wg PN-B-01030.
* ``ring_layers`` — warstwy ściany zewnętrznej wzdłuż zamkniętego obrysu osi (narożniki na ucios), z podziałem na
  odcinki (kierunek warstwy dla wężyka/zygzaka).
* ``wall_layers`` — ściana prosta z warstw; ``section_h`` / ``section_v`` — warstwy przegród w przekroju.
Wszystkie współrzędne w metrach modelu.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, MultiPolygon, Polygon, box
from shapely.ops import unary_union

from . import hatch as H
from .geom import arr, perp, polygons_of, rect_pts, unit

KIND_STYLE = {
    # rodzaj: (warstwa konturu, pióro, priorytet domyślny)
    "konstr": ("A-SCIANY-KONSTR", "gruba", 100),
    "strop": ("A-STROPY", "gruba", 100),
    "fund": ("A-FUNDAMENTY", "gruba", 100),
    "dzial": ("A-SCIANY-DZIAL", "srednia", 80),
    "izol": ("A-SCIANY-IZOL", "srednia", 60),
    "warstwa": ("A-WARSTWY", "cienka", 50),
    "wyk": ("A-SCIANY-WYK", "b_cienka", 40),
    "membrana": ("A-IZOL-WODNA", None, 70),
    "grunt": ("A-TEREN", None, 10),
    "stal": ("A-SCIANY-KONSTR", "srednia", 110),
}


@dataclass
class CutItem:
    poly: object
    mat: str
    kind: str
    priority: float
    axis: tuple | None = None
    angle: float | None = None
    outline: bool = True
    group: str | None = None
    params: dict = field(default_factory=dict)


class CutSet:
    def __init__(self):
        self.items: list[CutItem] = []
        self.voids = []

    def add(self, poly, mat: str, kind: str = "konstr", priority: float | None = None, axis=None,
            angle: float | None = None, outline: bool = True, group: str | None = None, **params) -> CutItem:
        if not isinstance(poly, (Polygon, MultiPolygon)):
            poly = Polygon(arr(poly))
        pr = KIND_STYLE[kind][2] if priority is None else priority
        it = CutItem(poly, mat, kind, pr, axis, angle, outline, group, params)
        self.items.append(it)
        return it

    def cut_out(self, poly):
        """Otwór (np. okno, drzwi) — odejmowany od wszystkich elementów."""
        if not isinstance(poly, (Polygon, MultiPolygon)):
            poly = Polygon(arr(poly))
        self.voids.append(poly)

    def resolve(self):
        voids = unary_union(self.voids) if self.voids else None
        order = sorted(range(len(self.items)), key=lambda i: -self.items[i].priority)
        acc = None
        out = []
        for i in order:
            it = self.items[i]
            g = it.poly
            if voids is not None:
                g = g.difference(voids)
            if acc is not None:
                g = g.difference(acc)
            g = g.buffer(0)
            if not g.is_empty:
                out.append((it, g))
            acc = it.poly if acc is None else acc.union(it.poly)
        return out

    def draw(self, c, hatch: bool = True, outlines: bool = True, fill_konstr: str | None = None,
             merge_thin_mm: float = 0.7, blacken_mm: float = 1.5, black_gap_mm: float = 0.7):
        """Rysuje przekrój: kreskowanie (każdy element osobno — własny kierunek warstwy) i kontury scalonych grup.

        Reguły (R4-C04, PN-EN ISO 128-3 7.5, R4 pkt 3.8):
        * warstwy cieńsze niż ``merge_thin_mm`` na papierze (tynki, okładziny, cienkie warstwy — bez membran)
          dołącza się do sąsiedniego elementu o najwyższym priorytecie (jedna linia obrysu zamiast dwóch < 0,7 mm),
        * przekroje konstrukcyjne węższe niż ``blacken_mm`` zaczernia się, zostawiając prześwit ``black_gap_mm``
          między stykającymi się zaczernionymi przekrojami.
        """
        res = [[it, g] for it, g in self.resolve()]
        k = c.k
        # --- 1) scalanie cienkich warstw
        if merge_thin_mm:
            thick = [_width(g) for _it, g in res]
            for i, (it, g) in enumerate(res):
                if it.kind in ("membrana", "grunt") or thick[i] >= merge_thin_mm * k:
                    continue
                best = None
                for j, (jt, jg) in enumerate(res):
                    if j == i or thick[j] < merge_thin_mm * k or jt.kind in ("membrana", "grunt"):
                        continue
                    if g.distance(jg) > 1e-6 * max(1.0, k):
                        continue
                    if best is None or jt.priority > res[best][0].priority:
                        best = j
                if best is not None:
                    res[best][1] = res[best][1].union(g).buffer(1e-9 * k).buffer(-1e-9 * k)
                    res[i][1] = None
            res = [r for r in res if r[1] is not None and not r[1].is_empty]
        # --- 2) zaczernianie wąskich przekrojów konstrukcyjnych
        blacks = []
        groups: dict[tuple, list] = {}
        for it, g in res:
            is_black = (blacken_mm and it.kind in ("konstr", "strop", "fund", "dzial")
                        and _width(g) < blacken_mm * k)
            if is_black:
                fillg = g
                for bg in blacks:
                    fillg = fillg.difference(bg.buffer(black_gap_mm * k, join_style=2))
                c.fill(fillg, "A-WYPELNIENIA", "#000000")
                blacks.append(g)
                continue
            if hatch:
                kw = dict(it.params)
                if it.axis is not None:
                    kw["axis"] = it.axis
                if it.angle is not None:
                    kw["angle"] = it.angle
                if fill_konstr and it.kind in ("konstr", "strop", "fund"):
                    c.fill(g, "A-WYPELNIENIA", fill_konstr)
                else:
                    H.hatch(c, g, it.mat, **kw)
            key = (it.group or H.resolve(it.mat), it.kind)
            groups.setdefault(key, []).append((it, g))
        if outlines:
            for (grp, kind), lst in groups.items():
                if kind in ("membrana", "grunt"):
                    continue
                if not any(it.outline for it, _ in lst):
                    continue
                u = unary_union([g for _, g in lst]).buffer(1e-7 * k).buffer(-1e-7 * k)
                ly, pen, _ = KIND_STYLE[kind]
                c.geom(u, ly, pen=pen)
        return res


def _width(g) -> float:
    """Szerokość elementu = średnica największego koła wpisanego (miara "grubości" warstwy)."""
    try:
        import shapely
        best = 0.0
        for pg in polygons_of(g):
            ln = shapely.maximum_inscribed_circle(pg, tolerance=max(pg.length, 1e-9) * 1e-4)
            best = max(best, 2.0 * ln.length)
        return best
    except Exception:  # pragma: no cover
        from .geom import strip_frame
        return min(strip_frame(pg)[4] for pg in polygons_of(g))


# ================================================================================================ ściany w rzucie
def _edge_normals(P):
    """Normalne zewnętrzne krawędzi wieloboku CCW."""
    n = len(P)
    out = []
    for i in range(n):
        d = unit(P[(i + 1) % n] - P[i])
        out.append(np.array([d[1], -d[0]]))
    return out


def _corner(P, normals, i, s):
    """Narożnik przesunięcia o s (na zewnątrz >0) w wierzchołku i (przecięcie przesuniętych krawędzi i-1, i)."""
    n = len(P)
    a = P[i]
    n0 = normals[(i - 1) % n]
    n1 = normals[i]
    # rozwiązanie: punkt X taki, że (X - a)·n0 = s i (X - a)·n1 = s
    M = np.array([n0, n1])
    try:
        v = np.linalg.solve(M, np.array([s, s]))
    except np.linalg.LinAlgError:
        v = n1 * s
    return a + v


def layer_offsets(layers, ref: str = "konstr"):
    """Zakresy przesunięć warstw względem osi warstwy konstrukcyjnej.

    layers — lista warstw od WNĘTRZA do ZEWNĄTRZ: [(materiał, grubość, rodzaj), …], dokładnie jedna rodzaju
    'konstr' (albo pierwsza warstwa, jeśli brak). Zwraca listę (mat, kind, s0, s1) — s rośnie na zewnątrz,
    oś konstrukcji s=0."""
    idx = next((i for i, l in enumerate(layers) if (l[2] if len(l) > 2 else "konstr") == ref), 0)
    t_ref = layers[idx][1]
    s = -t_ref / 2 - sum(l[1] for l in layers[:idx])
    out = []
    for l in layers:
        kind = l[2] if len(l) > 2 else "konstr"
        out.append((l[0], kind, s, s + l[1]))
        s += l[1]
    return out


def ring_layers(cs: CutSet, axis_poly, layers, group_prefix: str = "SZ"):
    """Warstwy ściany zewnętrznej wzdłuż zamkniętego obrysu OSI konstrukcji (wielobok CCW, wnętrze po lewej).
    Każda warstwa × każda krawędź = osobny element (trapez z ucięciem narożnym)."""
    P = arr(axis_poly)
    if Polygon(P).exterior.is_ccw is False:
        P = P[::-1]
    N = len(P)
    normals = _edge_normals(P)
    items = []
    for mat, kind, s0, s1 in layer_offsets(layers):
        for i in range(N):
            j = (i + 1) % N
            q = [_corner(P, normals, i, s0), _corner(P, normals, j, s0), _corner(P, normals, j, s1),
                 _corner(P, normals, i, s1)]
            pg = Polygon(q).buffer(0)
            items.append(cs.add(pg, mat, kind, axis=(P[i], P[j]), group=f"{group_prefix}:{mat}"))
    return items


def wall_layers(cs: CutSet, p1, p2, layers, justification: str = "konstr", priority_shift: float = 0.0,
                extend=(0.0, 0.0), angle: float | None = None, group: str | None = None, kind_override=None):
    """Ściana prosta z warstw [(mat, d, rodzaj)] od strony LEWEJ (względem p1→p2) do PRAWEJ.
    justification: 'konstr' — p1-p2 to oś warstwy konstrukcyjnej; 'left'/'right' — lico; 'center' — środek."""
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    nR = np.array([d[1], -d[0]])  # w prawo
    T = sum(l[1] for l in layers)
    if justification == "konstr":
        offs = layer_offsets(layers)
    else:
        s = {"left": 0.0, "center": -T / 2, "right": -T}[justification]
        offs = []
        for l in layers:
            offs.append((l[0], l[2] if len(l) > 2 else "konstr", s, s + l[1]))
            s += l[1]
    A2 = A - d * extend[0]
    B2 = B + d * extend[1]
    items = []
    for mat, kind, s0, s1 in offs:
        kind = kind_override or kind
        q = [A2 + nR * s0, B2 + nR * s0, B2 + nR * s1, A2 + nR * s1]
        pr = None if not priority_shift else KIND_STYLE[kind][2] + priority_shift
        items.append(cs.add(Polygon(q), mat, kind, pr, axis=(A, B), angle=angle, group=group))
    return items


def opening_rect(p1, p2, a: float, b: float, depth: float = 0.35):
    """Prostokąt otworu w ścianie p1→p2 (oś) od odległości a do b wzdłuż ściany; ``depth`` — zasięg w obie strony
    od osi (musi objąć wszystkie warstwy ściany, ale nie sięgać ścian sąsiednich)."""
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d)
    return Polygon([A + d * a - n * depth, A + d * b - n * depth, A + d * b + n * depth, A + d * a + n * depth])


# ================================================================================================ przekroje
def section_h(cs: CutSet, x0: float, x1: float, z_top: float, layers, default_kind: str = "warstwa"):
    """Warstwy poziome (podłoga, strop, dach) od GÓRY: [(mat, d, rodzaj), …]. Zwraca [(mat, z_spód, z_wierzch)]."""
    z = z_top
    out = []
    for l in layers:
        mat, d = l[0], l[1]
        kind = l[2] if len(l) > 2 else default_kind
        pg = box(x0, z - d, x1, z)
        cs.add(pg, mat, kind, axis=((x0, z - d / 2), (x1, z - d / 2)))
        out.append((mat, z - d, z))
        z -= d
    return out


def section_v(cs: CutSet, z0: float, z1: float, x_start: float, layers, direction: float = 1.0,
              default_kind: str = "warstwa"):
    """Warstwy pionowe (ściana) od ``x_start`` w kierunku ``direction`` (+1 = w prawo). Zwraca [(mat, xa, xb)]."""
    x = x_start
    out = []
    for l in layers:
        mat, d = l[0], l[1]
        kind = l[2] if len(l) > 2 else default_kind
        xa, xb = sorted([x, x + direction * d])
        cs.add(box(xa, z0, xb, z1), mat, kind, axis=(((xa + xb) / 2, z0), ((xa + xb) / 2, z1)))
        out.append((mat, xa, xb))
        x += direction * d
    return out
