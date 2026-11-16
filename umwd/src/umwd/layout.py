"""Rule-based floor layout: perimeter office bands along façades, corridor ring around a core, corner rooms.

Conventions (from programme M.01 + clarifications):
  * module 1.35 m along façade; office = 3 modules (axis width 4.05 m); GW office = 4 modules (5.40 m)
  * clear room depth chosen so that net area >= 24.0 m² (3 modules) / >= 32.0 m² (4 modules)
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

MODULE = 1.35
PART = 0.12          # partition thickness
EXT = 0.45           # external wall zone (structure + insulation + cladding) measured inward from outline
CORR = 1.80          # corridor clear width


def room_depth_for(area=24.0, modules=3, module=MODULE, part=PART):
    clear_w = modules * module - part
    return math.ceil(area / clear_w * 100) / 100.0   # clear depth rounded up to cm


@dataclass
class Cell:
    poly: Polygon
    edge: int
    s0: float
    s1: float
    kind: str = "free"      # office3 | office4 | corner | special
    facade_dir: int = 1


@dataclass
class FloorLayout:
    outline: Polygon
    core: Polygon | None
    bands: list = field(default_factory=list)
    cells: list = field(default_factory=list)
    corners: list = field(default_factory=list)
    corridor: Polygon | None = None
    inner: Polygon | None = None


def _ccw(poly: Polygon) -> list:
    c = list(poly.exterior.coords)[:-1]
    a = sum(c[i][0] * c[(i + 1) % len(c)][1] - c[(i + 1) % len(c)][0] * c[i][1] for i in range(len(c)))
    return c if a > 0 else c[::-1]


def perimeter_layout(outline: Polygon, core: Polygon | None, depth_clear=None, module=MODULE, ext=EXT,
                     corridor=CORR, edges=None, office_modules=3):
    """edges: list of edge indices (of CCW outline) that carry office bands (others e.g. party walls)."""
    if depth_clear is None:
        depth_clear = room_depth_for(24.0, office_modules, module)
    pts = _ccw(outline)
    n = len(pts)
    band_depth = ext + depth_clear + PART / 2
    inner = Polygon(pts).buffer(-band_depth, join_style=2, mitre_limit=10)
    lay = FloorLayout(outline=Polygon(pts), core=core, inner=inner)
    use = set(range(n)) if edges is None else set(edges)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        if i not in use:
            continue
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        vx, vy = -uy, ux                       # inward normal for CCW polygon
        def W(s, t):
            return (a[0] + ux * s + vx * t, a[1] + uy * s + vy * t)
        # straight usable span: where the full-depth rectangle stays inside the outline
        # find s_start / s_end by probing the inner polygon's projection
        probe = LineString([W(-1000, band_depth + 0.01), W(1000 + L, band_depth + 0.01)]).intersection(Polygon(pts))
        if probe.is_empty:
            continue
        coords = list(probe.coords) if probe.geom_type == "LineString" else [c for g in probe.geoms for c in g.coords]
        ss = [((x - a[0]) * ux + (y - a[1]) * uy) for x, y in coords]
        s_start, s_end = max(0.0, min(ss)), min(L, max(ss))
        band = Polygon([W(s_start, 0), W(s_end, 0), W(s_end, band_depth), W(s_start, band_depth)])
        lay.bands.append((i, band, s_start, s_end))
        nmod = int((s_end - s_start - 2 * ext + 1e-6) // module)
        s = s_start + ext + ((s_end - s_start - 2 * ext) - nmod * module) / 2
        for k in range(nmod):
            c = Polygon([W(s + k * module, ext), W(s + (k + 1) * module, ext),
                         W(s + (k + 1) * module, ext + depth_clear), W(s + k * module, ext + depth_clear)])
            lay.cells.append(Cell(c, i, s + k * module, s + (k + 1) * module))
    # corners: ring minus bands
    ring = Polygon(pts).difference(inner)
    bands_u = unary_union([b for _, b, _, _ in lay.bands]) if lay.bands else Polygon()
    rest = ring.difference(bands_u)
    lay.corners = [g for g in getattr(rest, "geoms", [rest]) if not g.is_empty and g.area > 4.0]
    if core is not None:
        lay.corridor = inner.difference(core.buffer(0))
    return lay


def group_cells(cells, edge, start_idx, count):
    sel = [c for c in cells if c.edge == edge][start_idx:start_idx + count]
    if not sel:
        return None
    return unary_union([c.poly for c in sel]).buffer(0)


def assign_offices(lay: FloorLayout, plan_per_edge: dict):
    """plan_per_edge: {edge: [("office3"|"office4"|("special", modules, name)), ...]} consumed left→right.
    Returns list of rooms dicts: {kind, name, poly, edge, modules}."""
    rooms = []
    for e, seq in plan_per_edge.items():
        cells = [c for c in lay.cells if c.edge == e]
        idx = 0
        for item in seq:
            if item == "office3":
                m, kind, name = 3, "office3", "Pokój biurowy"
            elif item == "office4":
                m, kind, name = 4, "office4", "Pokój biurowy (GW)"
            else:
                kind, m, name = item
            if idx + m > len(cells):
                break
            poly = unary_union([c.poly for c in cells[idx:idx + m]]).buffer(-PART / 2, join_style=2)
            rooms.append({"kind": kind, "name": name, "poly": poly, "edge": e, "modules": m})
            idx += m
    return rooms


def capacity(lay: FloorLayout, office_modules=3):
    per_edge = {}
    for c in lay.cells:
        per_edge[c.edge] = per_edge.get(c.edge, 0) + 1
    return {e: {"modules": m, "offices": m // office_modules, "rest_modules": m % office_modules} for e, m in per_edge.items()}
