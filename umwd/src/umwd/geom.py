"""Geometry utilities on shapely for the UMWD model (local grid e,n in metres)."""
from __future__ import annotations
import math
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity


def P(pts):
    return Polygon(pts)


def unit(v):
    l = math.hypot(*v)
    return (v[0] / l, v[1] / l)


def band(a, b, depth, side=+1, start=0.0, end=None):
    """Rectangle along segment a→b (façade line), extending `depth` to the left (side=+1) or right (side=-1).
    start/end: distances along the segment (default whole length)."""
    ux, uy = unit((b[0] - a[0], b[1] - a[1]))
    nx, ny = (-uy * side, ux * side)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    e = L if end is None else end
    p0 = (a[0] + ux * start, a[1] + uy * start)
    p1 = (a[0] + ux * e, a[1] + uy * e)
    return Polygon([p0, p1, (p1[0] + nx * depth, p1[1] + ny * depth), (p0[0] + nx * depth, p0[1] + ny * depth)])


def frame(a, b, side=+1):
    """Local frame of a façade segment: origin a, u along, v inward (left if side=+1)."""
    ux, uy = unit((b[0] - a[0], b[1] - a[1]))
    vx, vy = (-uy * side, ux * side)
    def to_world(s, t):
        return (a[0] + ux * s + vx * t, a[1] + uy * s + vy * t)
    def to_local(p):
        dx, dy = p[0] - a[0], p[1] - a[1]
        return (dx * ux + dy * uy, dx * vx + dy * vy)
    return to_world, to_local, math.hypot(b[0] - a[0], b[1] - a[1])


def rect_local(to_world, s0, s1, t0, t1):
    return Polygon([to_world(s0, t0), to_world(s1, t0), to_world(s1, t1), to_world(s0, t1)])


def area(g):
    return g.area


def rings(g):
    if isinstance(g, Polygon):
        return [list(g.exterior.coords)] + [list(r.coords) for r in g.interiors]
    out = []
    for pg in getattr(g, "geoms", []):
        out += rings(pg)
    return out


def walls_from_rooms(room_polys, outer, ext_thick=0.45, int_thick=0.12):
    """Approximate wall poché: outer wall ring (inward offset) + thin partitions as buffered room boundaries."""
    outer_wall = outer.difference(outer.buffer(-ext_thick, join_style=2))
    parts = []
    for r in room_polys:
        parts.append(r.exterior.buffer(int_thick / 2, cap_style=2, join_style=2))
    inner = unary_union(parts).intersection(outer.buffer(-ext_thick * 0.5, join_style=2))
    return unary_union([outer_wall, inner])
