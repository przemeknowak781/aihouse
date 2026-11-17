"""Parametric façade generator for Blender (bpy 5.2).

A volume = footprint polygon (CCW, local e,n) extruded between z0 and z1, clad with a façade system:
  * solid "wall" mass set back by `reveal` (window plane), piers/fins standing proud on the façade line,
  * spandrel/floor bands, plinth (cokół), cornice (gzyms) and attic,
  * glazing panes on the window plane (with frames),
  * curved edges: polygon arcs are handled because every edge is processed independently (short segments).
All dimensions in metres. The spec dict is documented in `default_spec()`.
"""
from __future__ import annotations
import math
import bmesh
import bpy
from mathutils import Vector


def default_spec():
    return {
        "levels": [(0.0, 4.8), (4.8, 3.75), (8.55, 3.75)],   # (z_floor, storey height) list
        "bay": 2.70,              # façade bay (axis spacing)
        "pier_w": 1.05,           # pier width (proud element)
        "pier_d": 0.30,           # pier projection beyond window plane (= reveal depth)
        "sill": 0.90,             # window sill above floor
        "head": 0.35,             # spandrel depth under next floor (lintel band)
        "frame": 0.06,            # frame width
        "plinth_h": 0.0,          # extra plinth band height at ground (0 = none)
        "cornice_h": 0.9, "cornice_d": 0.15,
        "attic_h": 0.0,
        "ground_glass_sill": 0.0, # ground floor windows down to floor
        "mat_wall": None, "mat_pier": None, "mat_glass": None, "mat_frame": None, "mat_cornice": None, "mat_plinth": None,
        "skip_edges": [],         # edge indices without windows (party walls)
        "blind_edges": [],        # edges clad but without windows
    }


def _edges(poly):
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        yield i, a, b


def _box_on_edge(bm, a, b, s0, s1, t0, t1, z0, z1, outward):
    """Box along edge a→b between distances s0..s1, offset t0..t1 along outward normal (t>0 = outside), z0..z1."""
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = outward
    pts = []
    for s, t in ((s0, t0), (s1, t0), (s1, t1), (s0, t1)):
        pts.append((a[0] + ux * s + nx * t, a[1] + uy * s + ny * t))
    vb = [bm.verts.new((x, y, z0)) for x, y in pts]
    vt = [bm.verts.new((x, y, z1)) for x, y in pts]
    faces = [vb[::-1], vt] + [[vb[i], vb[(i + 1) % 4], vt[(i + 1) % 4], vt[i]] for i in range(4)]
    for f in faces:
        try:
            bm.faces.new(f)
        except ValueError:
            pass


def _mesh_obj(name, bm, mat, coll):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me)
    (coll or bpy.context.scene.collection).objects.link(ob)
    if mat is not None:
        ob.data.materials.append(mat)
    return ob


def build_volume(name, poly, z0, z1, spec, coll=None):
    """Create façade objects for one volume. Returns list of objects."""
    from . import blib
    sp = default_spec(); sp.update(spec)
    # CCW check → outward normal is to the right of edge direction
    area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    if area < 0:
        poly = poly[::-1]
    d = sp["pier_d"]
    objs = []
    # inner mass (window plane) — prism set back by d from façade line
    from shapely.geometry import Polygon
    inner = Polygon(poly).buffer(-d, join_style=2)
    ring = list(inner.exterior.coords)[:-1]
    objs.append(blib.extrude_polygon(name + "_masa", ring, z0, z1, sp["mat_wall"], coll))
    bm_p, bm_g, bm_f, bm_b = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    levels = [(zf, h) for zf, h in sp["levels"] if zf >= z0 - 1e-6 and zf < z1 - 1e-6]
    for i, a, b in _edges(poly):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 0.3 or i in sp["skip_edges"]:
            continue
        ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        out = (uy, -ux)
        nb = max(1, round(L / sp["bay"]))
        bay = L / nb
        # horizontal bands at each floor (spandrels) — only BETWEEN piers (no overlapping solids)
        for zf, h in levels:
            zb0 = zf - sp["head"] if zf > z0 + 1e-6 else zf
            zb1 = zf + (sp["sill"] if zf > z0 + 0.01 else sp["ground_glass_sill"])
            if zb1 - zb0 < 0.02:
                continue
            for k in range(nb):
                q0, q1 = k * bay + sp["pier_w"] / 2, (k + 1) * bay - sp["pier_w"] / 2
                if q1 - q0 > 0.05:
                    _box_on_edge(bm_b, a, b, q0, q1, -d + 0.002, -0.002, zb0, zb1, out)
        # piers
        for k in range(nb + 1):
            s = k * bay
            s0, s1 = max(0.0, s - sp["pier_w"] / 2), min(L, s + sp["pier_w"] / 2)
            if s1 - s0 < 0.05:
                continue
            _box_on_edge(bm_p, a, b, s0, s1, -d, 0.0, z0, z1, out)
        if i in sp["blind_edges"]:
            for k in range(nb):
                q0, q1 = k * bay + sp["pier_w"] / 2, (k + 1) * bay - sp["pier_w"] / 2
                if q1 - q0 > 0.05:
                    _box_on_edge(bm_b, a, b, q0, q1, -d + 0.002, -0.002, z0, z1, out)
            continue
        # glazing per bay per level, on window plane (t = -d + 0.02)
        for zf, h in levels:
            sill = sp["ground_glass_sill"] if abs(zf - z0) < 0.01 else sp["sill"]
            zt = zf + h - sp["head"]
            zb = zf + sill
            if zt - zb < 0.4:
                continue
            for k in range(nb):
                s0 = k * bay + sp["pier_w"] / 2
                s1 = (k + 1) * bay - sp["pier_w"] / 2
                if s1 - s0 < 0.3:
                    continue
                _box_on_edge(bm_g, a, b, s0, s1, -d + 0.01, -d + 0.03, zb, zt, out)
                fw = sp["frame"]
                for (q0, q1, r0, r1) in ((s0, s0 + fw, zb, zt), (s1 - fw, s1, zb, zt), (s0, s1, zb, zb + fw), (s0, s1, zt - fw, zt)):
                    _box_on_edge(bm_f, a, b, q0, q1, -d + 0.03, -d + 0.08, r0, r1, out)
    objs.append(_mesh_obj(name + "_filary", bm_p, sp["mat_pier"], coll))
    objs.append(_mesh_obj(name + "_pasy", bm_b, sp["mat_pier"], coll))
    objs.append(_mesh_obj(name + "_szklo", bm_g, sp["mat_glass"], coll))
    objs.append(_mesh_obj(name + "_ramy", bm_f, sp["mat_frame"], coll))
    # cornice + attic
    if sp["cornice_h"] > 0:
        outer = Polygon(poly).buffer(sp["cornice_d"], join_style=2)
        objs.append(blib.extrude_polygon(name + "_gzyms", list(outer.exterior.coords)[:-1], z1, z1 + sp["cornice_h"], sp["mat_cornice"] or sp["mat_pier"], coll))
    if sp["plinth_h"] > 0:
        outer = Polygon(poly).buffer(0.04, join_style=2)
        objs.append(blib.extrude_polygon(name + "_cokol", list(outer.exterior.coords)[:-1], z0, z0 + sp["plinth_h"], sp["mat_plinth"] or sp["mat_pier"], coll))
    return objs


def arc_polygon(poly, vertex_index, R, segs=16):
    """Replace a convex vertex of a polygon by a circular fillet of radius R."""
    n = len(poly)
    p = Vector((*poly[vertex_index], 0)); a = Vector((*poly[vertex_index - 1], 0)); b = Vector((*poly[(vertex_index + 1) % n], 0))
    u1 = (a - p).normalized(); u2 = (b - p).normalized()
    ang = math.acos(max(-1, min(1, u1.dot(u2))))
    t = R / math.tan(ang / 2)
    p1 = p + u1 * t; p2 = p + u2 * t
    bis = (u1 + u2).normalized()
    c = p + bis * (R / math.sin(ang / 2))
    a1 = math.atan2(p1.y - c.y, p1.x - c.x); a2 = math.atan2(p2.y - c.y, p2.x - c.x)
    da = a2 - a1
    while da > math.pi: da -= 2 * math.pi
    while da < -math.pi: da += 2 * math.pi
    arc = [(c.x + R * math.cos(a1 + da * k / segs), c.y + R * math.sin(a1 + da * k / segs)) for k in range(segs + 1)]
    return list(poly[:vertex_index]) + arc + list(poly[vertex_index + 1:])
