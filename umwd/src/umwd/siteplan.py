"""Site plan (zagospodarowanie) renderer 1:500 from model/site.json + building massing.

Layers (bottom→top): water, roads, sidewalks, lawns, curbs, tram tracks, existing buildings (with shadows),
proposal ground surfaces, proposal roofs (white, heights, storeys), shadows (sun SW at 45° per Regulamin),
trees (existing kept / removed / new), boundaries, labels.
"""
from __future__ import annotations
import json, math
from pathlib import Path
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from shapely import affinity
from .svg import Svg, View, model_rings, model_poly

ROOT = Path(__file__).resolve().parents[2]
C = {
    "water": "#dfe9ec", "water_line": "#9fb8c0", "road": "#ebe9e5", "walk": "#f5f3ef", "lawn": "#e4ead8",
    "curb": "#a8a39b", "bld": "#d9d5ce", "bld_line": "#6f6a63", "shadow": "#1f1d1a", "roof": "#ffffff",
    "ink": "#1f1d1a", "tree_old": "#8fa37a", "tree_new": "#6f8f5e", "accent": "#a8483a",
}


def load_site():
    return json.loads((ROOT / "model" / "site.json").read_text(encoding="utf-8"))


def poly_of(item):
    pts = item["pts"] if isinstance(item, dict) else item
    if len(pts) < 3:
        return None
    try:
        p = Polygon(pts).buffer(0)
        return p if p.area > 0.05 else None
    except Exception:
        return None


def shadow_poly(footprint: Polygon, height: float, az_sun=225.0, el_sun=45.0):
    """Shadow on flat ground of a prism (footprint, height) for sun from azimuth az_sun at elevation el_sun."""
    L = height / math.tan(math.radians(el_sun))
    a = math.radians(az_sun + 180.0)           # shadow direction
    dx, dy = L * math.sin(a), L * math.cos(a)
    moved = affinity.translate(footprint, dx, dy)
    parts = [footprint, moved]
    coords = list(footprint.exterior.coords)
    for i in range(len(coords) - 1):
        p, q = coords[i], coords[i + 1]
        parts.append(Polygon([p, q, (q[0] + dx, q[1] + dy), (p[0] + dx, p[1] + dy)]).buffer(0))
    return unary_union(parts).difference(footprint)


def draw_base(svg: Svg, v: View, site: dict, with_shadows=True, existing_trees=True, trees_removed=()):
    u = site["ulice_i_sytuacja"]
    for w in site["woda"]["linia_brzegu"]:
        pts = w["pts"]
        svg.poly([v.p(*p) for p in pts], fill="none", stroke=C["water_line"], sw=0.25, close=False)
    # water body approximation: area east of shoreline within view (polygon closing along the view edge)
    for key, col in (("jezdnie", C["road"]), ("chodniki", C["walk"]), ("trawniki", C["lawn"])):
        for it in u[key]:
            if it.get("zamknieta", True):
                pg = poly_of(it)
                if pg is not None:
                    model_rings(svg, v, pg, fill=col, stroke="none")
    for it in u["krawezniki"]:
        svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke=C["curb"], sw=0.12, close=False)
    for it in u["tory_tramwajowe"]:
        svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke="#8c877f", sw=0.15, close=False, extra='stroke-dasharray="1.2,0.6"')
    for it in u["mury"]:
        svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke=C["bld_line"], sw=0.25, close=False)
    # existing buildings
    blds = []
    for b in site["budynki"]["items"]:
        pg = poly_of(b)
        if pg is None:
            continue
        blds.append((pg, b.get("wysokosc_szac_m", 6.0), b))
    if with_shadows:
        sh = unary_union([shadow_poly(pg, h) for pg, h, _ in blds])
        model_rings(svg, v, sh, fill=C["shadow"], stroke="none", extra='fill-opacity="0.13"')
    for pg, h, b in blds:
        model_rings(svg, v, pg, fill=C["bld"], stroke=C["bld_line"], sw=0.2)
        c = pg.representative_point()
        lab = (b.get("etykieta") or "").upper()
        svg.text(v.p(c.x, c.y), lab, size=1.8, anchor="middle", fill="#5a554e")
    return blds


def draw_trees(svg: Svg, v: View, trees, kind="old", removed=False, crown=None):
    for t in trees:
        r = crown or (3.0 if t.get("typ") == "lisciaste" else 2.0)
        x, y = v.p(t["e"], t["n"])
        rr = v.mm(r)
        if removed:
            svg.circle((x, y), rr, fill="none", stroke="#b0aaa2", sw=0.12, extra='stroke-dasharray="0.6,0.5"')
            svg.line((x - rr * 0.5, y - rr * 0.5), (x + rr * 0.5, y + rr * 0.5), stroke="#b0aaa2", sw=0.12)
            svg.line((x - rr * 0.5, y + rr * 0.5), (x + rr * 0.5, y - rr * 0.5), stroke="#b0aaa2", sw=0.12)
            continue
        col = C["tree_old"] if kind == "old" else C["tree_new"]
        svg.circle((x, y), rr, fill=col, stroke="#ffffff", sw=0.15, extra='fill-opacity="0.55"')
        svg.circle((x, y), v.mm(0.25), fill="#3d4a33", stroke="none")


def draw_boundaries(svg: Svg, v: View, site: dict, inv=True, comp=True, A=False):
    g = site["granice"]
    if comp:
        model_poly(svg, v, g["granica_opracowania_konkursowego"]["pts"], fill="none", stroke="#2f6f8f", sw=0.35, extra='stroke-dasharray="3,1.2"')
    if inv:
        model_poly(svg, v, g["obszar_inwestycji"]["pts"], fill="none", stroke=C["accent"], sw=0.4, extra='stroke-dasharray="4,1,0.8,1"')
    if A:
        model_poly(svg, v, g["wydzielenie_A_mpzp"]["pts"], fill="none", stroke="#c2185b", sw=0.25, extra='stroke-dasharray="1.5,1"')
