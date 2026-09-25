"""Rzutowanie prostokątne brył IR (pryzm) z usuwaniem linii niewidocznych — algorytm „od najbliższych” na shapely.

Widok z boku (przekroje — część widoczna za płaszczyzną cięcia, elewacje):
  * kierunek patrzenia ``L`` (wersor poziomy), oś pozioma rysunku ``R = (L_y, −L_x)`` (prawa ręka obserwatora),
    współrzędne rysunku (s, z): s = (p − o)·R, głębokość d = (p − o)·L,
  * ściany boczne pryzm zwrócone do obserwatora (normalna zewn. · L < 0) rzutują się na prostokąty [s_a, s_b]×[z0, z1],
  * ściany współpłaszczyznowe z tego samego materiału są SCALANE (sumowane) — znikają krawędzie pozorne (podział
    ściany IR na filary / pasy podokienne / nadproża, styki warstw ETICS kolejnych kondygnacji),
  * grupy sortowane wg głębokości (najbliższe pierwsze); widoczna część grupy = obszar − suma obszarów bliższych;
    widoczne krawędzie = brzeg obszaru − (suma bliższych powiększona o tolerancję).
Widok z góry / z dołu (rzuty): to samo dla ścian poziomych (wierzch pryzmy przy patrzeniu w dół, spód przy
patrzeniu w górę) — głębokość = −z1 / z0.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import shapely
from shapely.geometry import MultiPolygon, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from ..draft.geom import polygons_of

Q = 1e-5   # siatka przyciągania współrzędnych [m]


def _q(v):
    return np.round(np.asarray(v, float) / Q) * Q


@dataclass
class Group:
    key: tuple
    polys: list
    depth: float
    material: str
    kind: str
    elem: str
    meta: dict = field(default_factory=dict)
    poly: object = None       # suma (s,z) lub (x,y)
    vis: object = None        # część widoczna (obszar)
    lines: object = None      # widoczne krawędzie

    def finish(self):
        if self.poly is None:
            u = unary_union(self.polys)
            try:
                u = shapely.set_precision(u, Q)
            except Exception:  # pragma: no cover
                pass
            self.poly = u.buffer(0) if not u.is_valid else u
        return self.poly


def _prism_poly(p):
    try:
        g = Polygon(p.polygon, p.holes)
        if not g.is_valid:
            g = g.buffer(0)
        return g
    except Exception:
        return Polygon()


def side_groups(prisms, o, L, *, depth_min: float | None = None, depth_max: float | None = None,
                key_fn=None, z_clip: tuple | None = None) -> list[Group]:
    """Grupy ścian bocznych zwróconych do obserwatora (patrzenie w kierunku ``L`` z płaszczyzny przez ``o``).

    depth_min / depth_max — przycięcie pryzm do pasa głębokości (np. 0 dla części „za” płaszczyzną przekroju).
    key_fn(prism) → (materiał, rodzaj) do grupowania (domyślnie (material, kind))."""
    o = np.asarray(o, float)
    L = np.asarray(L, float)
    L = L / np.hypot(*L)
    R = np.array([L[1], -L[0]])
    big = 1e4
    clip = None
    if depth_min is not None or depth_max is not None:
        d0 = -big if depth_min is None else depth_min
        d1 = big if depth_max is None else depth_max
        c = [o + L * d0 - R * big, o + L * d0 + R * big, o + L * d1 + R * big, o + L * d1 - R * big]
        clip = Polygon(c)
    groups: dict = {}
    for p in prisms:
        z0, z1 = p.z0, p.z1
        if z_clip is not None:
            z0, z1 = max(z0, z_clip[0]), min(z1, z_clip[1])
        if z1 - z0 < 1e-6:
            continue
        g = _prism_poly(p)
        if g.is_empty:
            continue
        if clip is not None:
            if not g.intersects(clip):
                continue
            g = g.intersection(clip)
        mk = key_fn(p) if key_fn else (p.material, p.kind)
        if mk is None:
            continue
        for pg in polygons_of(g):
            if pg.area < 1e-9:
                continue
            pg = orient(pg, 1.0)
            for ring in [pg.exterior] + list(pg.interiors):
                c = np.asarray(ring.coords)
                a, b = c[:-1], c[1:]
                e = b - a
                ln = np.hypot(e[:, 0], e[:, 1])
                ok = ln > 1e-7
                if not ok.any():
                    continue
                n = np.zeros_like(e)
                n[ok] = np.column_stack([e[ok, 1], -e[ok, 0]]) / ln[ok, None]
                front = ok & ((n @ L) < -1e-6)
                for i in np.nonzero(front)[0]:
                    sa, sb = float((a[i] - o) @ R), float((b[i] - o) @ R)
                    if abs(sb - sa) < 1e-6:
                        continue
                    da, db = float((a[i] - o) @ L), float((b[i] - o) @ L)
                    s0, s1 = sorted((sa, sb))
                    s0, s1, zz0, zz1 = _q([s0, s1, z0, z1])
                    if s1 - s0 < Q or zz1 - zz0 < Q:
                        continue
                    off = float(n[i] @ a[i])
                    key = (round(float(n[i][0]), 3), round(float(n[i][1]), 3), round(off, 3)) + tuple(mk)
                    gr = groups.get(key)
                    dep = min(da, db)
                    if gr is None:
                        gr = Group(key, [], dep, mk[0], mk[1], p.element, dict(p.meta))
                        groups[key] = gr
                    gr.depth = min(gr.depth, dep)
                    gr.polys.append(box(s0, zz0, s1, zz1))
    out = list(groups.values())
    for g in out:
        g.finish()
    return out


def top_groups(prisms, *, looking: str = "down", z_cut: float | None = None, key_fn=None) -> list[Group]:
    """Grupy ścian poziomych: looking='down' — wierzchy (głębokość −z1, wierzch przycięty do z_cut),
    'up' — spody (głębokość z0)."""
    groups: dict = {}
    for p in prisms:
        g = _prism_poly(p)
        if g.is_empty:
            continue
        mk = key_fn(p) if key_fn else (p.material, p.kind)
        if mk is None:
            continue
        if looking == "down":
            z = p.z1 if z_cut is None else min(p.z1, z_cut)
            dep = -z
        else:
            z = p.z0 if z_cut is None else max(p.z0, z_cut)
            dep = z
        key = (round(z, 3),) + tuple(mk)
        gr = groups.get(key)
        if gr is None:
            gr = Group(key, [], dep, mk[0], mk[1], p.element, dict(p.meta))
            groups[key] = gr
        gr.polys.append(g)
    out = list(groups.values())
    for g in out:
        g.finish()
    return out


def hidden_lines(groups: list[Group], occluder=None, tol: float = 2e-4, min_len: float = 1e-3) -> list[Group]:
    """Usuwanie linii niewidocznych: grupy od najbliższej; ``occluder`` — obszar zasłaniający od początku
    (np. elementy przecięte, grunt). Uzupełnia ``g.vis`` i ``g.lines``. Zwraca grupy w kolejności przetwarzania."""
    order = sorted(groups, key=lambda g: (g.depth, g.key))
    occ = []
    if occluder is not None and not occluder.is_empty:
        occ.extend([pg for pg in polygons_of(occluder) if pg.area > 0])
    bnds = [pg.bounds for pg in occ]
    for g in order:
        P = g.poly
        if P is None or P.is_empty:
            g.vis, g.lines = Polygon(), None
            continue
        x0, y0, x1, y1 = P.bounds
        if bnds:
            B = np.asarray(bnds)
            idx = np.nonzero((B[:, 0] <= x1 + tol) & (B[:, 2] >= x0 - tol) & (B[:, 1] <= y1 + tol) &
                             (B[:, 3] >= y0 - tol))[0]
        else:
            idx = []
        bnd = P.boundary
        if len(idx):
            local = unary_union([occ[i] for i in idx])
            try:
                vis = P.difference(local)
            except Exception:
                vis = P.buffer(0).difference(local.buffer(0))
            lines = bnd.difference(local.buffer(tol, join_style=2))
        else:
            vis, lines = P, bnd
        if lines is not None and not lines.is_empty and min_len:
            from shapely.geometry import LineString, MultiLineString
            from ..draft.geom import lines_of
            keep = [LineString(a) for a in lines_of(lines) if len(a) >= 2 and LineString(a).length >= min_len]
            lines = MultiLineString(keep) if keep else None
        g.vis, g.lines = vis, lines
        for pg in polygons_of(P):
            occ.append(pg)
            bnds.append(pg.bounds)
    return order


def silhouette(groups: list[Group]):
    """Obrys sumy wszystkich grup (sylweta)."""
    u = unary_union([g.poly for g in groups if g.poly is not None and not g.poly.is_empty])
    return u
