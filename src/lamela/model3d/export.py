"""Eksport IR → glTF 2.0 (.glb) i OBJ (+ .mtl) przez trimesh.

Struktura sceny glTF (oś Y w górę; X = x_bud (E), Y = z, Z = −y_bud (S))::

    LAMELA
    ├── budynek
    │   ├── fundamenty
    │   ├── P0 / P1 / P2 …           ← elementy (węzeł = id elementu, np. "S0-01")
    │   │   └── S0-01                     └── węzły-siatki per materiał: "S0-01|SIL18"
    │   └── dach
    ├── teren
    └── otoczenie

Węzły mają ``extras`` z oryginalnym id, grupą, rodzajem (kind) i kodem materiału (three.js: ``userData``).
Scena ma ``extras.metadata`` z metadanymi IR (kondygnacje, pomieszczenia, układ).
"""
from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapely
import trimesh
from shapely.geometry import Polygon
from trimesh.visual import TextureVisuals
from trimesh.visual.material import PBRMaterial

from ..ir import IR, Mesh, Prism
from .materials import PBR, hex_rgb, pbr_for
from .textures import texture

GROUP_PARENT = {"fundamenty": "budynek", "dach": "budynek", "teren": "LAMELA", "otoczenie": "LAMELA",
                "budynek": "LAMELA"}


def _srgb_to_lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _safe(name: str) -> str:
    return re.sub(r"[.:/\\\[\]\s]", "_", str(name))


def _to_gltf(P: np.ndarray) -> np.ndarray:
    """Układ budynku (x, y, z) → glTF (x, z, −y)."""
    P = np.asarray(P, float)
    return np.column_stack([P[:, 0], P[:, 2], -P[:, 1]])


# --------------------------------------------------------------------------------------------------
# Triangulacja pryzm
# --------------------------------------------------------------------------------------------------
def _triangulate(poly: Polygon) -> np.ndarray:
    """Trójkąty (k, 3, 2) CCW pokrywające wielobok (z otworami)."""
    ext = np.asarray(poly.exterior.coords)[:-1]
    if not poly.interiors and len(ext) <= 8 and abs(poly.convex_hull.area - poly.area) < 1e-9 * max(1.0, poly.area):
        tris = np.array([[ext[0], ext[i], ext[i + 1]] for i in range(1, len(ext) - 1)])
    else:
        tris = _cdt(poly)
    if len(tris) == 0:
        return tris
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    tris = tris[np.abs(cr) > 1e-14]
    cr = cr[np.abs(cr) > 1e-14]
    tris[cr < 0] = tris[cr < 0][:, [0, 2, 1]]
    return tris


def _cdt(poly: Polygon) -> np.ndarray:
    """Triangulacja z ograniczeniami (GEOS); przy błędzie — naprawa wieloboku lub Delaunay + filtr środków."""
    for cand in (poly, poly.buffer(0), shapely.set_precision(poly.buffer(0), 1e-6).simplify(1e-7)):
        try:
            if cand.is_empty:
                continue
            gc = shapely.constrained_delaunay_triangles(cand)
            if not gc.is_empty:
                return np.array([np.asarray(t.exterior.coords)[:3] for t in gc.geoms])
        except shapely.errors.GEOSException:
            continue
    from scipy.spatial import Delaunay
    pts = [np.asarray(poly.exterior.coords)[:-1]] + [np.asarray(r.coords)[:-1] for r in poly.interiors]
    P = np.unique(np.vstack(pts), axis=0)
    if len(P) < 3:
        return np.zeros((0, 3, 2))
    t = Delaunay(P)
    tris = P[t.simplices]
    c = tris.mean(axis=1)
    return tris[shapely.contains_xy(poly, c[:, 0], c[:, 1])]


def prism_arrays(p: Prism, uv_scale: float = 1.0):
    """Wierzchołki (układ budynku), normalne, UV [m/uv_scale], trójkąty — ściany płaskie (bez współdzielenia)."""
    poly = Polygon(p.polygon, p.holes)
    V, N, U = [], [], []
    tris = _triangulate(poly)
    z0, z1 = p.z0, p.z1
    for t in tris:
        for q in t:
            V.append((q[0], q[1], z1)); N.append((0, 0, 1)); U.append((q[0], q[1]))
        for q in t[[0, 2, 1]]:
            V.append((q[0], q[1], z0)); N.append((0, 0, -1)); U.append((q[0], -q[1]))
    rings = [np.asarray(poly.exterior.coords)] + [np.asarray(r.coords) for r in poly.interiors]
    for ring in rings:
        for a, b in zip(ring[:-1], ring[1:]):
            d = b - a
            L = math.hypot(d[0], d[1])
            if L < 1e-9:
                continue
            nx, ny = d[1] / L, -d[0] / L
            ua = (a[0] * d[0] + a[1] * d[1]) / L
            ub = ua + L
            quad = [(a[0], a[1], z0, ua, z0), (b[0], b[1], z0, ub, z0), (b[0], b[1], z1, ub, z1),
                    (a[0], a[1], z0, ua, z0), (b[0], b[1], z1, ub, z1), (a[0], a[1], z1, ua, z1)]
            for x, y, z, u, v in quad:
                V.append((x, y, z)); N.append((nx, ny, 0)); U.append((u, v))
    V = np.asarray(V, float).reshape(-1, 3)
    N = np.asarray(N, float).reshape(-1, 3)
    U = np.asarray(U, float).reshape(-1, 2) / uv_scale
    F = np.arange(len(V)).reshape(-1, 3)
    return V, N, U, F


def mesh_arrays(m: Mesh, uv_scale: float = 1.0):
    V = np.asarray(m.vertices, float)
    F = np.asarray(m.faces, int)
    if m.smooth:
        tm = trimesh.Trimesh(V, F, process=False)
        N = np.asarray(tm.vertex_normals)
        U = np.column_stack([V[:, 0] + V[:, 2] * 0.5, V[:, 1] + V[:, 2] * 0.5]) / uv_scale
        return V, N, U, F
    tri = V[F]
    fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(fn, axis=1, keepdims=True)
    fn = fn / np.where(ln > 0, ln, 1)
    VV = tri.reshape(-1, 3)
    NN = np.repeat(fn, 3, axis=0)
    ax = np.argmax(np.abs(NN), axis=1)
    U = np.where(ax[:, None] == 2, VV[:, [0, 1]], np.where(ax[:, None] == 0, VV[:, [1, 2]], VV[:, [0, 2]])) / uv_scale
    FF = np.arange(len(VV)).reshape(-1, 3)
    return VV, NN, U, FF


def terrain_arrays(ir: IR, material: str, uv_scale: float):
    t = ir.terrain
    mask = np.array([m == material for m in t.face_material])
    if not mask.any():
        return None
    F = t.faces[mask]
    used = np.unique(F)
    remap = -np.ones(len(t.vertices), int)
    remap[used] = np.arange(len(used))
    V = t.vertices[used]
    F2 = remap[F]
    tm = trimesh.Trimesh(t.vertices, t.faces, process=False)
    N = np.asarray(tm.vertex_normals)[used]
    U = V[:, :2] / uv_scale
    return V, N, U, F2


# --------------------------------------------------------------------------------------------------
# Scena trimesh
# --------------------------------------------------------------------------------------------------
class _MatCache:
    def __init__(self, model=None, textures=True):
        self.model = model
        self.textures = textures
        self.cache: dict[str, tuple[PBRMaterial, PBR]] = {}

    def get(self, code: str) -> tuple[PBRMaterial, PBR]:
        if code in self.cache:
            return self.cache[code]
        p = pbr_for(code, self.model)
        r, g, b = hex_rgb(p.color)
        img = None
        if self.textures and p.texture:
            img = texture(p.texture, p.color)
            factor = [1.0, 1.0, 1.0, p.alpha]
        else:
            factor = [_srgb_to_lin(r), _srgb_to_lin(g), _srgb_to_lin(b), p.alpha]
        kw = dict(name=code, baseColorFactor=factor, metallicFactor=p.metallic, roughnessFactor=p.roughness,
                  doubleSided=p.double_sided, alphaMode="BLEND" if p.alpha < 0.999 else "OPAQUE")
        if img is not None:
            kw["baseColorTexture"] = img
        m = PBRMaterial(**kw)
        self.cache[code] = (m, p)
        return self.cache[code]


def ir_to_scene(ir: IR, model=None, textures: bool = True, explode: dict | None = None) -> tuple[trimesh.Scene, dict]:
    """Buduje scenę trimesh. Zwraca (scena, słownik extras węzłów wg nazwy węzła)."""
    mats = _MatCache(model, textures)
    buckets: dict[tuple, list] = defaultdict(list)
    kinds: dict[tuple, str] = {}
    for p in ir.prisms:
        key = (p.meta.get("group", "otoczenie"), p.element, p.material)
        buckets[key].append(("prism", p))
        kinds.setdefault(key, p.kind)
    for m in ir.meshes:
        key = (m.meta.get("group", "otoczenie"), m.element, m.material)
        buckets[key].append(("mesh", m))
        kinds.setdefault(key, m.kind)

    scene = trimesh.Scene()
    extras: dict[str, dict] = {}
    levels = [k["id"] for k in ir.meta.get("kondygnacje", [])]
    made = set()

    def ensure(node, parent):
        if node in made:
            return
        if parent not in made and parent != "LAMELA":
            ensure(parent, GROUP_PARENT.get(parent, "budynek"))
        if parent == "LAMELA" and "LAMELA" not in made:
            scene.graph.update(frame_from=scene.graph.base_frame, frame_to="LAMELA", matrix=np.eye(4))
            made.add("LAMELA")
            extras["LAMELA"] = {"id": "LAMELA", "rola": "korzen"}
        scene.graph.update(frame_from=parent, frame_to=node, matrix=np.eye(4))
        made.add(node)

    for g in ["budynek", "fundamenty"] + levels + ["dach", "teren", "otoczenie"]:
        par = GROUP_PARENT.get(g, "budynek")
        ensure(g, par)
        extras[g] = {"id": g, "rola": "grupa", "group": g}

    for key, items in buckets.items():
        group, elem, matcode = key
        pm, pb = mats.get(matcode)
        if not pb.visible:
            continue
        Vs, Ns, Us, Fs = [], [], [], []
        off = 0
        for typ, obj in items:
            if typ == "prism":
                V, N, U, F = prism_arrays(obj, pb.uv)
            else:
                V, N, U, F = mesh_arrays(obj, pb.uv)
            if len(V) == 0:
                continue
            Vs.append(V); Ns.append(N); Us.append(U); Fs.append(F + off)
            off += len(V)
        if not Vs:
            continue
        V = _to_gltf(np.vstack(Vs))
        N = _to_gltf(np.vstack(Ns))
        U = np.vstack(Us)
        F = np.vstack(Fs)
        tm = trimesh.Trimesh(vertices=V, faces=F, vertex_normals=N, process=False,
                             visual=TextureVisuals(uv=U, material=pm))
        gparent = group if group in made else "otoczenie"
        enode = _safe(elem) if _safe(elem) not in ("LAMELA",) else elem + "_"
        if enode in made and enode not in extras.get(enode, {}).get("_elem_of", [enode]):
            enode = f"{enode}_{_safe(group)}"
        if enode not in made:
            scene.graph.update(frame_from=gparent, frame_to=enode, matrix=np.eye(4))
            made.add(enode)
            extras[enode] = {"id": elem, "rola": "element", "group": group, "kind": kinds[key], "_elem_of": [enode]}
        nname = f"{enode}|{_safe(matcode)}"
        scene.add_geometry(tm, node_name=nname, geom_name=nname, parent_node_name=enode)
        made.add(nname)
        extras[nname] = {"id": elem, "rola": "siatka", "group": group, "kind": kinds[key], "material": matcode,
                         "castShadow": pb.cast_shadow, "alpha": pb.alpha}

    if ir.terrain is not None:
        for code in sorted(set(ir.terrain.face_material)):
            pm, pb = mats.get(code)
            arr = terrain_arrays(ir, code, pb.uv)
            if arr is None:
                continue
            V, N, U, F = arr
            tm = trimesh.Trimesh(vertices=_to_gltf(V), faces=F, vertex_normals=_to_gltf(N), process=False,
                                 visual=TextureVisuals(uv=U, material=pm))
            nname = f"TEREN|{code}"
            scene.add_geometry(tm, node_name=nname, geom_name=nname, parent_node_name="teren")
            made.add(nname)
            extras[nname] = {"id": "TEREN", "rola": "siatka", "group": "teren", "kind": "terrain", "material": code,
                             "castShadow": False, "receiveShadow": True}
    for v in extras.values():
        v.pop("_elem_of", None)
    return scene, extras


def _metadata(ir: IR) -> dict:
    return json.loads(json.dumps(ir.meta, default=float))


def export_glb(ir: IR, path, model=None, textures: bool = True) -> dict:
    """Zapisuje scenę do .glb. Zwraca statystyki."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scene, extras = ir_to_scene(ir, model, textures)
    scene.metadata = {"lamela": _metadata(ir)}

    def post(tree):
        for nd in tree.get("nodes", []):
            nm = nd.get("name")
            if nm in extras:
                nd["extras"] = extras[nm]
        tree.setdefault("asset", {})["generator"] = "lamela.model3d (trimesh)"
        tree["asset"]["copyright"] = "Dom LAMELA — model generowany z model/budynek.yaml"

    data = trimesh.exchange.gltf.export_glb(scene, include_normals=True, tree_postprocessor=post)
    path.write_bytes(data)
    ntri = sum(len(g.faces) for g in scene.geometry.values())
    return {"plik": str(path), "bajty": len(data), "siatki": len(scene.geometry), "trojkaty": int(ntri),
            "wezly": len(scene.graph.nodes)}


def export_obj(ir: IR, path, model=None) -> dict:
    """Zapisuje .obj + .mtl (+ tekstury PNG/JPG obok). Układ Y-w-górę jak w glTF."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    scene, _ = ir_to_scene(ir, model, textures=True)
    mtl_name = path.with_suffix(".mtl").name
    text, tex = trimesh.exchange.obj.export_obj(scene, include_normals=True, include_texture=True,
                                                return_texture=True, write_texture=False, mtl_name=mtl_name)
    path.write_text(text, encoding="utf-8")
    written = [str(path)]
    for fn, blob in (tex or {}).items():
        fp = path.parent / fn
        fp.write_bytes(blob if isinstance(blob, (bytes, bytearray)) else bytes(blob))
        written.append(str(fp))
    return {"plik": str(path), "pliki": written}


def load_glb_check(path) -> dict:
    """Szybka kontrola pliku .glb (pygltflib): liczba węzłów, siatek, materiałów, nazwy grup."""
    import pygltflib
    g = pygltflib.GLTF2().load(str(path))
    names = [n.name for n in g.nodes]
    return {"wezly": len(g.nodes), "siatki": len(g.meshes), "materialy": len(g.materials),
            "tekstury": len(g.textures or []), "grupy": [n for n in names if n in ("budynek", "P0", "P1", "P2", "P3",
                                                                                    "dach", "fundamenty", "teren",
                                                                                    "otoczenie")],
            "nazwy_wezlow": names}
