"""Façade generator v2 — runs (straight or curved polylines) with bays distributed by arc length.

Volume outline (CCW) is split into runs: consecutive edges joined while the turning angle < `curve_angle`
(fillets made of short segments become ONE curved run). Each run gets an integer number of bays.
Elements per bay: pier (proud, centred on bay boundary), spandrel bands per storey between piers, glazing + frames
on the window plane recessed by `pier_d`. Curved parts are tessellated into ≤ `seg` m chords.
"""
from __future__ import annotations
import math
import bmesh
import bpy
from shapely.geometry import Polygon, LineString


def default_spec():
    return {"levels": [(0.0, 4.8)], "bay": 2.70, "pier_w": 1.05, "pier_d": 0.30, "sill": 0.90, "head": 0.35,
            "frame": 0.06, "cornice_h": 0.9, "cornice_d": 0.15, "plinth_h": 0.0, "ground_glass_sill": 0.0,
            "curve_angle": 25.0, "seg": 0.6, "skip_runs": [], "blind_runs": [], "bay_override": {},
            "mat_wall": None, "mat_pier": None, "mat_glass": None, "mat_frame": None, "mat_cornice": None,
            "mat_plinth": None, "mat_band": None}


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def runs_of(poly, curve_angle=25.0):
    """Split closed CCW polygon into runs (lists of points incl. both ends)."""
    n = len(poly)
    def heading(i):
        a, b = poly[i], poly[(i + 1) % n]
        return math.atan2(b[1] - a[1], b[0] - a[0])
    turn = []
    for i in range(n):
        h0, h1 = heading(i - 1), heading(i)
        d = math.degrees((h1 - h0 + math.pi) % (2 * math.pi) - math.pi)
        turn.append(abs(d))          # turn at vertex i
    breaks = [i for i in range(n) if turn[i] >= curve_angle]
    if not breaks:
        breaks = [0]
    runs = []
    for k, b0 in enumerate(breaks):
        b1 = breaks[(k + 1) % len(breaks)]
        idx = [b0]
        j = b0
        while True:
            j = (j + 1) % n
            idx.append(j)
            if j == b1:
                break
        runs.append([poly[i] for i in idx])
    return runs


class Run:
    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for i in range(1, len(pts)):
            self.cum.append(self.cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        self.L = self.cum[-1]

    def at(self, s):
        s = max(0.0, min(self.L, s))
        for i in range(1, len(self.pts)):
            if s <= self.cum[i] + 1e-9:
                a, b = self.pts[i - 1], self.pts[i]
                l = self.cum[i] - self.cum[i - 1]
                t = 0 if l < 1e-9 else (s - self.cum[i - 1]) / l
                ux, uy = ((b[0] - a[0]) / l, (b[1] - a[1]) / l) if l > 1e-9 else (1, 0)
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), (ux, uy)
        a, b = self.pts[-2], self.pts[-1]
        l = max(1e-9, self.cum[-1] - self.cum[-2])
        return b, ((b[0] - a[0]) / l, (b[1] - a[1]) / l)

    def strip(self, s0, s1, seg):
        """Sample points along the run from s0 to s1 (inclusive), including interior vertices."""
        ss = [s0] + [c for c in self.cum if s0 < c < s1] + [s1]
        out = []
        for i in range(len(ss) - 1):
            n = max(1, math.ceil((ss[i + 1] - ss[i]) / seg))
            for k in range(n):
                out.append(ss[i] + (ss[i + 1] - ss[i]) * k / n)
        out.append(s1)
        return out


def _quad_strip(bm, run, s_list, t0, t1, z0, z1):
    """Closed slab following the run between offsets t0..t1 (outward normal = right of tangent)."""
    P = []
    for s in s_list:
        (x, y), (ux, uy) = run.at(s)
        nx, ny = uy, -ux
        P.append(((x + nx * t0, y + ny * t0), (x + nx * t1, y + ny * t1)))
    vin_b = [bm.verts.new((p[0][0], p[0][1], z0)) for p in P]
    vout_b = [bm.verts.new((p[1][0], p[1][1], z0)) for p in P]
    vin_t = [bm.verts.new((p[0][0], p[0][1], z1)) for p in P]
    vout_t = [bm.verts.new((p[1][0], p[1][1], z1)) for p in P]
    m = len(P)
    for i in range(m - 1):
        for quad in ((vout_b[i], vout_b[i + 1], vout_t[i + 1], vout_t[i]),      # outer face
                     (vin_b[i + 1], vin_b[i], vin_t[i], vin_t[i + 1]),          # inner face
                     (vin_t[i], vout_t[i], vout_t[i + 1], vin_t[i + 1]),        # top
                     (vin_b[i + 1], vout_b[i + 1], vout_b[i], vin_b[i])):       # bottom
            try:
                bm.faces.new(quad)
            except ValueError:
                pass
    for i in (0, m - 1):
        try:
            bm.faces.new((vin_b[i], vout_b[i], vout_t[i], vin_t[i]))
        except ValueError:
            pass


def _obj(name, bm, mat, coll):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = False
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def build_volume(name, poly, z0, z1, spec, coll=None):
    from . import blib
    sp = default_spec(); sp.update(spec)
    poly = ccw([tuple(p) for p in poly])
    d = sp["pier_d"]
    objs = []
    inner = Polygon(poly).buffer(-d, join_style=2, mitre_limit=8)
    objs.append(blib.extrude_polygon(name + "_masa", list(inner.exterior.coords)[:-1], z0, z1, sp["mat_wall"], coll))
    bm_p, bm_b, bm_g, bm_f = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    levels = [(zf, h) for zf, h in sp["levels"] if z0 - 1e-6 <= zf < z1 - 1e-6]
    for ri, pts in enumerate(runs_of(poly, sp["curve_angle"])):
        run = Run(pts)
        if run.L < 0.4 or ri in sp["skip_runs"]:
            continue
        bay_t = sp["bay_override"].get(ri, sp["bay"])
        nb = max(1, round(run.L / bay_t)); bay = run.L / nb
        pw = min(sp["pier_w"], bay * 0.6)
        # piers (centred on bay boundaries; end piers half inside the run)
        for k in range(nb + 1):
            s0, s1 = max(0.0, k * bay - pw / 2), min(run.L, k * bay + pw / 2)
            if s1 - s0 > 0.04:
                _quad_strip(bm_p, run, run.strip(s0, s1, sp["seg"]), -d, 0.0, z0, z1)
        for k in range(nb):
            q0, q1 = k * bay + pw / 2, (k + 1) * bay - pw / 2
            if q1 - q0 < 0.08:
                continue
            ss = run.strip(q0, q1, sp["seg"])
            if ri in sp["blind_runs"]:
                _quad_strip(bm_b, run, ss, -d + 0.002, -0.002, z0, z1)
                continue
            for zf, h in levels:
                ground = abs(zf - z0) < 0.01
                zb0 = zf if ground else zf - sp["head"]
                zb1 = zf + (sp["ground_glass_sill"] if ground else sp["sill"])
                if zb1 - zb0 > 0.02:
                    _quad_strip(bm_b, run, ss, -d + 0.002, -0.002, zb0, zb1)
                zt = min(zf + h - sp["head"], z1 - sp["head"] * 0.5)
                if zt - zb1 > 0.4:
                    _quad_strip(bm_g, run, ss, -d + 0.01, -d + 0.03, zb1, zt)
                    fw = sp["frame"]
                    _quad_strip(bm_f, run, run.strip(q0, q0 + fw, 1), -d + 0.03, -d + 0.08, zb1, zt)
                    _quad_strip(bm_f, run, run.strip(q1 - fw, q1, 1), -d + 0.03, -d + 0.08, zb1, zt)
                    _quad_strip(bm_f, run, ss, -d + 0.03, -d + 0.08, zb1, zb1 + fw)
                    _quad_strip(bm_f, run, ss, -d + 0.03, -d + 0.08, zt - fw, zt)
            # top band to roof (above last storey's head)
    objs.append(_obj(name + "_filary", bm_p, sp["mat_pier"], coll))
    objs.append(_obj(name + "_pasy", bm_b, sp["mat_band"] or sp["mat_pier"], coll))
    objs.append(_obj(name + "_szklo", bm_g, sp["mat_glass"], coll))
    objs.append(_obj(name + "_ramy", bm_f, sp["mat_frame"], coll))
    if sp["cornice_h"] > 0:
        outer = Polygon(poly).buffer(sp["cornice_d"], join_style=2, mitre_limit=8)
        objs.append(blib.extrude_polygon(name + "_gzyms", list(outer.exterior.coords)[:-1], z1, z1 + sp["cornice_h"], sp["mat_cornice"] or sp["mat_pier"], coll))
    if sp["plinth_h"] > 0:
        outer = Polygon(poly).buffer(0.03, join_style=2, mitre_limit=8)
        ring = outer.difference(Polygon(poly).buffer(-d - 0.05, join_style=2))
        for g in getattr(ring, "geoms", [ring]):
            pass
    return objs


def fillet(poly, vertex_index, R, segs=18):
    from .facade import arc_polygon
    return arc_polygon(poly, vertex_index, R, segs)
