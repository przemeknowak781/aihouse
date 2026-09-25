"""Reprezentacja pośrednia (IR) modelu — bryły pryzmatyczne + siatki (docs/SCHEMAT_MODELU.md §4).

Każdy element fizyczny budynku i otoczenia rozwiązywany jest do listy :class:`Prism` (wielobok podstawy × zakres z);
teren to :class:`TerrainMesh` (triangulacja Delaunaya), a bryły nieprzystające do pryzm (korony drzew, auta, dachy
dwuspadowe sąsiadów) — :class:`Mesh`. IR zasila: eksport 3D (glTF/OBJ), przekroje, elewacje, kontrolę kolizji.

    from lamela.model import load_model
    from lamela.ir import build_ir
    ir = build_ir(load_model("model/budynek.yaml", "model/dzialka.yaml"))
    ir.summary()                       # liczności wg rodzaju
    [p for p in ir.prisms if p.kind == "glass"]

Grupy (``meta['group']``): P0/P1/P2…, dach, fundamenty, teren, otoczenie — używane przez eksport glTF i podgląd www.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import shapely
from shapely.geometry import LineString, MultiPoint, MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from .model import (Model, Sciana, clean_geom, is_circular, iter_polys, make_polygon, parse_przekroj, _is_num, _is_pt,
                    _is_ring)

# --------------------------------------------------------------------------------------------------
# Struktury IR
# --------------------------------------------------------------------------------------------------
KINDS = ("wall", "slab", "roof", "parapet", "insulation", "column", "beam", "footing", "stair_step", "landing",
         "railing", "lamella", "frame", "glass", "door_leaf", "canopy", "terrace", "pavement", "fence", "terrain",
         "furniture",
         # rozszerzenia (otoczenie)
         "vegetation", "context", "vehicle", "road")


@dataclass
class Prism:
    id: str                 # identyfikator elementu źródłowego + sufiks części (np. "S0-01#3")
    kind: str               # patrz KINDS
    polygon: list           # [(x, y), ...] CCW, układ budynku [m]
    z0: float               # rzędna spodu (względem ±0,00)
    z1: float               # rzędna wierzchu
    material: str           # kod materiału (kolor 3D, kreskowanie w przekroju)
    level: str | None       # P0/P1/P2/None
    meta: dict = field(default_factory=dict)   # np. {"layer": "EPS031", "opening": "O0-01", "group": "P0"}
    holes: list = field(default_factory=list)  # otwory wieloboku: [[(x, y), ...], ...] (CW)

    @property
    def element(self) -> str:
        return self.id.split("#")[0]

    def shape(self) -> Polygon:
        return Polygon(self.polygon, self.holes)

    @property
    def area(self) -> float:
        return float(self.shape().area)

    @property
    def volume(self) -> float:
        return self.area * (self.z1 - self.z0)


@dataclass
class Mesh:
    """Dowolna bryła trójkątowa (korony drzew, auta, dachy dwuspadowe sąsiadów)."""
    id: str
    kind: str
    vertices: np.ndarray    # (N, 3) układ budynku
    faces: np.ndarray       # (M, 3) indeksy, CCW patrząc z zewnątrz
    material: str
    level: str | None = None
    meta: dict = field(default_factory=dict)
    smooth: bool = False    # True — normalne uśrednione (korony drzew)

    @property
    def element(self) -> str:
        return self.id.split("#")[0]


@dataclass
class TerrainMesh:
    """Teren: triangulacja Delaunaya punktów wysokościowych (+ zagęszczenie), z wycięciem pod budynkiem."""
    id: str
    vertices: np.ndarray    # (N, 3) układ budynku, z względne
    faces: np.ndarray       # (M, 3) CCW (normalne w górę)
    face_material: list     # kod materiału dla każdego trójkąta
    height_fn: Callable | None = None
    meta: dict = field(default_factory=dict)

    def height_at(self, x, y):
        """Rzędna terenu (względna) w punkcie/punktach budynku (interpolacja TIN punktów wysokościowych)."""
        if self.height_fn is None:
            return 0.0
        arr = np.atleast_2d(np.column_stack([np.atleast_1d(x), np.atleast_1d(y)]))
        z = self.height_fn(arr)
        return float(z[0]) if np.ndim(x) == 0 else z


@dataclass
class IR:
    prisms: list[Prism] = field(default_factory=list)
    meshes: list[Mesh] = field(default_factory=list)
    terrain: TerrainMesh | None = None
    meta: dict = field(default_factory=dict)

    def by_kind(self, kind: str) -> list[Prism]:
        return [p for p in self.prisms if p.kind == kind]

    def by_level(self, level: str) -> list[Prism]:
        return [p for p in self.prisms if p.level == level]

    def by_group(self, group: str) -> list:
        return [p for p in self.prisms + self.meshes if p.meta.get("group") == group]

    def element(self, eid: str) -> list:
        return [p for p in self.prisms + self.meshes if p.element == eid]

    def summary(self) -> dict:
        out: dict[str, int] = {}
        for p in self.prisms:
            out[p.kind] = out.get(p.kind, 0) + 1
        for m in self.meshes:
            out["mesh:" + m.kind] = out.get("mesh:" + m.kind, 0) + 1
        if self.terrain is not None:
            out["terrain_triangles"] = int(len(self.terrain.faces))
        return dict(sorted(out.items()))

    def bounds(self, groups: tuple | None = None) -> tuple:
        xs, ys, zs = [], [], []
        for p in self.prisms:
            if groups and p.meta.get("group") not in groups:
                continue
            a = np.asarray(p.polygon)
            xs += [a[:, 0].min(), a[:, 0].max()]
            ys += [a[:, 1].min(), a[:, 1].max()]
            zs += [p.z0, p.z1]
        if not xs:
            return (0, 0, 0, 0, 0, 0)
        return (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))

    def section(self, z: float) -> list[tuple[Prism, Polygon]]:
        """Przekrój poziomy na rzędnej z: lista (pryzma, wielobok) dla pryzm przeciętych płaszczyzną."""
        return [(p, p.shape()) for p in self.prisms if p.z0 <= z <= p.z1]


# --------------------------------------------------------------------------------------------------
# Materiały wizualne (kody pomocnicze niewystępujące w budynek.yaml)
# --------------------------------------------------------------------------------------------------
M_RAMA = "RAMA_ALU"
M_SZKLO = "SZKLO"
M_SZKLO_BAL = "SZKLO_BAL"
M_STAL_BAL = "STAL_BAL"
M_STAL_NIERDZ = "STAL_NIERDZ"
M_DRZWI_WEWN = "DRZWI_WEWN"
M_DRZWI_ZEWN = "DRZWI_ZEWN"
M_BRAMA = "BRAMA_GAR"
M_OBROBKA = "OBROBKA_BLACH"
M_PARAPET_WEWN = "PARAPET_WEWN"
M_SCHODY = "SCHODY"
M_TEREN = "TEREN_TRAWA"
M_TEREN_POZA = "TEREN_POZA"


def material_nawierzchni(txt: str | None) -> str:
    t = (txt or "").lower()
    if "desk" in t or "drewn" in t:
        return "NAW_DESKA"
    if "krat" in t or "ażur" in t:
        return "NAW_KRATKA"
    if "asfalt" in t or "bitum" in t:
        return "NAW_ASFALT"
    if "żwir" in t or "zwir" in t or "grys" in t:
        return "NAW_ZWIR"
    if "płyt" in t or "plyt" in t or "gres" in t or "kamie" in t:
        return "NAW_PLYTY"
    if "kostk" in t or "bruk" in t:
        return "NAW_KOSTKA_JASNA" if ("jasn" in t or "szar" in t and "grafit" not in t) else "NAW_KOSTKA"
    return "NAW_BETON"


# --------------------------------------------------------------------------------------------------
# Budowa IR
# --------------------------------------------------------------------------------------------------
def build_ir(model: Model, *, otoczenie: bool = True, auta: bool = True, ramy: bool = True) -> IR:
    """Konwertuje CAŁY model (budynek + działka) do IR."""
    return _Builder(model, otoczenie=otoczenie, auta=auta, ramy=ramy).run()


class _Builder:
    def __init__(self, m: Model, *, otoczenie: bool, auta: bool, ramy: bool):
        self.m = m
        self.otoczenie = otoczenie
        self.auta = auta
        self.ramy = ramy
        self.ir = IR()
        self._h = None
        self._ids: dict[str, int] = {}
        self.kondy = [k.id for k in m.kondygnacje]
        self.beton = self._default_concrete()

    # ---------------- narzędzia ----------------
    def _default_concrete(self) -> str:
        for p in self.m.przegrody.values():
            if p.typ in ("stropodach", "strop", "taras") and p.ma_oznaczona_konstr:
                return p.warstwy[p.idx_konstr].mat
        for kod in self.m.materialy:
            if re.match(r"^(ZB|ZELBET|ŻELBET|BET)", kod.upper()):
                return kod
        return "ZB_C30"

    def _uid(self, base: str) -> str:
        n = self._ids.get(base, 0)
        self._ids[base] = n + 1
        return f"{base}#{n}"

    def group_of_level(self, level: str | None) -> str:
        return level if level else "otoczenie"

    def add(self, base_id: str, kind: str, geom, z0: float, z1: float, material: str, level: str | None,
            group: str | None = None, **meta) -> list[Prism]:
        """Dodaje pryzmy z geometrii shapely (Polygon/MultiPolygon) lub listy punktów."""
        if z1 - z0 < 1e-5:
            return []
        if isinstance(geom, (list, tuple)):
            geom = Polygon([tuple(map(float, q[:2])) for q in geom])
        out = []
        if not geom.is_valid:
            geom = shapely.make_valid(geom)
        for p in iter_polys(geom):
            if p.area < 1e-6:
                continue
            if not p.is_valid or len(p.exterior.coords) > 5:
                p = p.buffer(0)
                if p.is_empty or not isinstance(p, Polygon):
                    for q in iter_polys(p):
                        self.add(base_id, kind, q, z0, z1, material, level, group=group, **meta)
                    continue
            p = orient(p, 1.0)
            ext = [(round(x, 6), round(y, 6)) for x, y in list(p.exterior.coords)[:-1]]
            holes = [[(round(x, 6), round(y, 6)) for x, y in list(r.coords)[:-1]] for r in p.interiors]
            md = dict(meta)
            md["group"] = group or self.group_of_level(level)
            pr = Prism(id=self._uid(base_id), kind=kind, polygon=ext, z0=float(z0), z1=float(z1), material=material,
                       level=level, meta=md, holes=holes)
            self.ir.prisms.append(pr)
            out.append(pr)
        return out

    def add_mesh(self, base_id, kind, V, Fc, material, level=None, group="otoczenie", smooth=False, **meta):
        V = np.asarray(V, float)
        Fc = np.asarray(Fc, int)
        if meta.pop("closed", True) and len(Fc):
            t = V[Fc]
            vol = float(np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])).sum()) / 6.0
            if vol < 0:
                Fc = Fc[:, ::-1]
        md = dict(meta)
        md["group"] = group
        mm = Mesh(id=self._uid(base_id), kind=kind, vertices=np.asarray(V, float), faces=np.asarray(Fc, int),
                  material=material, level=level, meta=md, smooth=smooth)
        self.ir.meshes.append(mm)
        return mm

    def h(self, x, y) -> float:
        """Rzędna terenu (względna); bez działki — 0,30 m poniżej ±0,00."""
        if self._h is None:
            return -0.30
        return float(self._h(np.array([[x, y]], float))[0])

    def hs(self, pts) -> np.ndarray:
        pts = np.asarray(pts, float).reshape(-1, 2)
        if self._h is None:
            return np.full(len(pts), -0.30)
        return self._h(pts)

    # ---------------- przebieg ----------------
    def run(self) -> IR:
        m = self.m
        self.footprint = unary_union([m.obrys_kondygnacji(k.id) for k in m.kondygnacje[:1]]) if m.kondygnacje else Polygon()
        if self.otoczenie and m.dz is not None:
            self._terrain()
        self._walls()
        if self.ramy:
            self._openings()
        self._floors_on_ground()
        self._stropy()
        self._dachy()
        self._wsporniki()
        self._slupy()
        self._belki()
        self._fundamenty()
        self._schody()
        self._balustrady()
        self._lamele()
        self._tarasy()
        if self.otoczenie and m.dz is not None:
            self._otoczenie()
        self._meta()
        return self.ir

    def _meta(self):
        m = self.m
        rooms = []
        for r in m.pomieszczenia():
            if r.polygon is None or r.polygon.is_empty:
                continue
            c = r.polygon.representative_point()
            rooms.append({"id": r.id, "nazwa": r.nazwa, "kond": r.kond, "xy": [round(c.x, 3), round(c.y, 3)],
                          "z": m.kondygnacja(r.kond).rzedna, "wys": r.wysokosc, "pow": round(r.pow_netto, 2),
                          "kategoria": r.kategoria})
        b = self.ir.bounds(groups=tuple(self.kondy) + ("dach",))
        dzm = {}
        if m.dz is not None:
            ob = m.dz.obrys
            if ob is not None:
                dzm["obrys"] = [[round(x, 3), round(y, 3)] for x, y in list(ob.exterior.coords)[:-1]]
            dr = m.dz.raw.get("droga") or {}
            if _is_ring(dr.get("jezdnia")):
                jz = m.dz.poly_bud(dr["jezdnia"])
                dzm["jezdnia"] = [[round(x, 3), round(y, 3)] for x, y in list(jz.exterior.coords)[:-1]]
            if self.ir.terrain is not None:
                c = self.footprint.centroid if not self.footprint.is_empty else Point(0, 0)
                dzm["teren_z_budynek"] = round(self.h(c.x, c.y), 3)
        self.ir.meta.update({
            "dzialka": dzm,
            "nazwa": (m.meta or {}).get("nazwa", ""),
            "wersja": (m.meta or {}).get("wersja", ""),
            "zero_abs": m.zero_abs,
            "azymut_osi_y": m.azymut_osi_y,
            "kondygnacje": [{"id": k.id, "nazwa": k.nazwa, "rzedna": k.rzedna} for k in m.kondygnacje],
            "grupy": list(self.kondy) + ["dach", "fundamenty", "teren", "otoczenie"],
            "bbox_budynku": [round(v, 3) for v in b],
            "pomieszczenia": rooms,
            "uklad": "x→E, y→N, z↑ (układ budynku, m); glTF: X=x, Y=z, Z=−y",
        })

    # ---------------- ściany ----------------
    def _walls(self):
        for w in self.m.sciany():
            for lay in w.warstwy:
                kind = "insulation" if lay.klasa == "izolacja" else "wall"
                for part in iter_polys(lay.polygon):
                    for poly, z0, z1, pname, oid in self._split_by_openings(w, lay, part):
                        meta = {"layer": lay.mat, "wall": w.id, "klasa": lay.klasa, "part": pname,
                                "strona": lay.strona}
                        if oid:
                            meta["opening"] = oid
                        self.add(w.id, kind, poly, z0, z1, lay.mat, w.kond, **meta)

    def _split_by_openings(self, w: Sciana, lay, part: Polygon):
        ops = [o for o in w.otwory if min(o.z1, lay.z1) - max(o.z0, lay.z0) > 1e-6]
        z0, z1 = lay.z0, lay.z1
        if not ops:
            return [(part, z0, z1, "pelna", None)]
        coords = np.asarray(part.exterior.coords)
        ss = (coords - w.p1) @ w.u
        smin, smax = float(ss.min()), float(ss.max())
        bps = {smin, smax}
        for o in ops:
            for s in (o.s0, o.s1):
                if smin + 1e-6 < s < smax - 1e-6:
                    bps.add(s)
        bps = sorted(bps)
        out = []
        for a, b in zip(bps[:-1], bps[1:]):
            if b - a < 1e-6:
                continue
            strip = clean_geom(part.intersection(w.band(t0=-50, t1=50, s0=a, s1=b)), min_area=1e-7)
            if strip.is_empty:
                continue
            cov = [o for o in ops if o.s0 <= a + 1e-6 and o.s1 >= b - 1e-6]
            if not cov:
                out.append((strip, z0, z1, "filar", None))
                continue
            gaps = sorted((max(o.z0, z0), min(o.z1, z1), o.id) for o in cov)
            zc = z0
            for i, (g0, g1, oid) in enumerate(gaps):
                if g0 - zc > 1e-4:
                    out.append((strip, zc, g0, "podokienny" if i == 0 else "miedzy", oid))
                zc = max(zc, g1)
            if z1 - zc > 1e-4:
                out.append((strip, zc, z1, "nadproze", gaps[-1][2]))
        return out

    # ---------------- stolarka ----------------
    def _openings(self):
        for o in self.m.otwory():
            w = o.sciana
            lvl = w.kond
            oid = o.id
            ta, tb = o.rama_t
            es = w.ext_side
            typ = o.typ

            def box_st(s0, s1, t0, t1):
                return Polygon([tuple(w.pt(s0, t0)), tuple(w.pt(s1, t0)), tuple(w.pt(s1, t1)), tuple(w.pt(s0, t1))])

            # ościeża (okładziny ościeży — tynk zewn./wewn.)
            lin = 0.012
            outer_mat = w.warstwy[-1].mat if w.sgn_int > 0 else w.warstwy[0].mat
            inner_mat = w.warstwy[0].mat if w.sgn_int > 0 else w.warstwy[-1].mat
            if es is not None:
                t_out = w.face_t(es, "all")
                t_in = w.face_t(-es, "all")
                tf_out = tb if es > 0 else ta
                tf_in = ta if es > 0 else tb
                zones = [(tf_out, t_out, outer_mat, "oscieze_zewn")]
                if typ not in ("otwor",):
                    zones.append((t_in, tf_in, inner_mat, "oscieze_wewn"))
            elif typ == "otwor":
                zones = [(w.t_min, w.t_max, w.warstwy[0].mat, "oscieze")]
            else:
                zones = []
            for t0, t1, mat, nm in zones:
                t0, t1 = min(t0, t1), max(t0, t1)
                if t1 - t0 < 1e-3:
                    continue
                self.add(oid, "wall", box_st(o.s0, o.s0 + lin, t0, t1), o.z0, o.z1, mat, lvl, part=nm, opening=oid)
                self.add(oid, "wall", box_st(o.s1 - lin, o.s1, t0, t1), o.z0, o.z1, mat, lvl, part=nm, opening=oid)
                self.add(oid, "wall", box_st(o.s0 + lin, o.s1 - lin, t0, t1), o.z1 - lin, o.z1, mat, lvl, part=nm,
                         opening=oid)
                if typ == "otwor":
                    pass
            if typ == "otwor":
                continue
            if typ == "drzwi":
                # ościeżnica na pełną grubość ściany + skrzydło
                fw = 0.025
                t0, t1 = w.t_min - 0.005, w.t_max + 0.005
                self.add(oid, "frame", box_st(o.s0, o.s0 + fw, t0, t1), o.z0, o.z1, M_DRZWI_WEWN, lvl, opening=oid)
                self.add(oid, "frame", box_st(o.s1 - fw, o.s1, t0, t1), o.z0, o.z1, M_DRZWI_WEWN, lvl, opening=oid)
                self.add(oid, "frame", box_st(o.s0 + fw, o.s1 - fw, t0, t1), o.z1 - fw, o.z1, M_DRZWI_WEWN, lvl,
                         opening=oid)
                tm = (w.t_min + w.t_max) / 2
                self.add(oid, "door_leaf", box_st(o.s0 + fw, o.s1 - fw, tm - 0.02, tm + 0.02), o.z0 + 0.01,
                         o.z1 - fw, M_DRZWI_WEWN, lvl, opening=oid)
                continue
            if typ == "brama":
                n = max(1, math.ceil(o.wys / 0.55))
                hh = o.wys / n
                for i in range(n):
                    self.add(oid, "door_leaf", box_st(o.s0 + 0.02, o.s1 - 0.02, ta, ta + 0.045),
                             o.z0 + i * hh + 0.004, o.z0 + (i + 1) * hh - 0.004, M_BRAMA, lvl, opening=oid)
                continue
            fw = {"fix": 0.055, "okno": 0.075, "drzwi_zewn": 0.085, "drzwi_przesuwne_HS": 0.085}.get(typ, 0.075)
            fb = 0.03 if typ in ("drzwi_zewn", "drzwi_przesuwne_HS") or o.parapet < 0.05 else fw
            # rama
            self.add(oid, "frame", box_st(o.s0, o.s0 + fw, ta, tb), o.z0, o.z1, M_RAMA, lvl, opening=oid)
            self.add(oid, "frame", box_st(o.s1 - fw, o.s1, ta, tb), o.z0, o.z1, M_RAMA, lvl, opening=oid)
            self.add(oid, "frame", box_st(o.s0 + fw, o.s1 - fw, ta, tb), o.z1 - fw, o.z1, M_RAMA, lvl, opening=oid)
            self.add(oid, "frame", box_st(o.s0 + fw, o.s1 - fw, ta, tb), o.z0, o.z0 + fb, M_RAMA, lvl, opening=oid)
            tm = (ta + tb) / 2
            if typ == "drzwi_zewn":
                self.add(oid, "door_leaf", box_st(o.s0 + fw, o.s1 - fw, tm - 0.035, tm + 0.035), o.z0 + fb,
                         o.z1 - fw, M_DRZWI_ZEWN, lvl, opening=oid)
                if es is not None:
                    strona = (o.otwieranie or {}).get("strona", "lewa")
                    sh = o.s1 - fw - 0.16 if strona == "lewa" else o.s0 + fw + 0.13
                    t_face = tm + es * 0.035
                    self.add(oid, "door_leaf", box_st(sh, sh + 0.03, t_face, t_face + es * 0.06),
                             o.z0 + 0.45, min(o.z1 - 0.25, o.z0 + 1.85), M_STAL_NIERDZ, lvl, opening=oid, part="pochwyt")
                continue
            # kwatery i szyby
            nk = o.raw.get("kwatery")
            if not _is_num(nk):
                pane = {"okno": 1.6, "fix": 3.0, "drzwi_przesuwne_HS": 3.0}.get(typ, 1.6)
                nk = max(2 if typ == "drzwi_przesuwne_HS" else 1, math.ceil((o.szer - 1e-6) / pane))
            nk = int(nk)
            inner = (o.s1 - fw) - (o.s0 + fw)
            pw = (inner - (nk - 1) * fw) / nk
            for i in range(nk):
                a = o.s0 + fw + i * (pw + fw)
                b = a + pw
                if i < nk - 1:
                    self.add(oid, "frame", box_st(b, b + fw, ta, tb), o.z0 + fb, o.z1 - fw, M_RAMA, lvl, opening=oid)
                self.add(oid, "glass", box_st(a, b, tm - 0.012, tm + 0.012), o.z0 + fb, o.z1 - fw, M_SZKLO, lvl,
                         opening=oid, kwatera=i + 1)
            # parapety
            if es is not None and o.parapet > 0.05 and typ in ("okno", "fix"):
                t_out = w.face_t(es, "all")
                tf_out = tb if es > 0 else ta
                t0, t1 = sorted((tf_out, t_out + es * 0.04))
                self.add(oid, "frame", box_st(o.s0 - 0.015, o.s1 + 0.015, t0, t1), o.z0 - 0.025, o.z0 + 0.004,
                         M_OBROBKA, lvl, opening=oid, part="parapet_zewn")
                if o.parapet > 0.3:
                    t_in = w.face_t(-es, "all")
                    tf_in = ta if es > 0 else tb
                    t0, t1 = sorted((tf_in, t_in - es * 0.03))
                    self.add(oid, "frame", box_st(o.s0 - 0.02, o.s1 + 0.02, t0, t1), o.z0 - 0.02, o.z0 + 0.004,
                             M_PARAPET_WEWN, lvl, opening=oid, part="parapet_wewn")

    # ---------------- podłogi i stropy ----------------
    def _stack_layers(self, base_id, region, z_top, layers, level, kind="slab", rooms=None, part="posadzka",
                      downward=True, group=None):
        """Układa warstwy (lista Warstwa, od góry) od rzędnej z_top w dół (downward) lub w górę."""
        z = z_top
        seq = layers if downward else list(reversed(layers))
        for i, lay in enumerate(seq):
            if downward:
                za, zb = z - lay.d, z
                z = za
            else:
                za, zb = z, z + lay.d
                z = zb
            is_top = (i == 0) if downward else (i == len(seq) - 1)
            klasa = self.m._klasa_mat(lay.mat)
            k = "insulation" if klasa == "izolacja" else kind
            if is_top and rooms and part == "posadzka":
                rest = region
                for r in rooms:
                    if r.polygon is None or r.polygon.is_empty:
                        continue
                    rp = clean_geom(r.polygon.intersection(region))
                    if rp.is_empty:
                        continue
                    mat = str(r.posadzka) if r.posadzka else lay.mat
                    self.add(base_id, k, rp, za, zb, mat, level, group=group, layer=lay.mat, part=part, room=r.id)
                    rest = rest.difference(rp)
                rest = clean_geom(rest)
                if not rest.is_empty:
                    self.add(base_id, k, rest, za, zb, lay.mat, level, group=group, layer=lay.mat, part=part)
            else:
                self.add(base_id, k, region, za, zb, lay.mat, level, group=group, layer=lay.mat, part=part)
        return z

    def _free(self, kid):
        regs = self.m.wolna_przestrzen(kid)
        return unary_union(regs) if regs else Polygon()

    def _floors_on_ground(self):
        m = self.m
        if not m.kondygnacje:
            return
        k = m.kondygnacje[0]
        p = m.przegroda(k.podloga) if k.podloga else None
        region = self._free(k.id)
        if p is None or region.is_empty:
            return
        rooms = m.pomieszczenia(k.id)
        self._stack_layers(f"POD-{k.id}", region, k.rzedna, p.warstwy, k.id, rooms=rooms)

    def _level_above(self, kid):
        ids = self.kondy
        i = ids.index(kid) if kid in ids else -1
        return ids[i + 1] if 0 <= i < len(ids) - 1 else kid

    def _stropy(self):
        m = self.m
        for st in m.stropy():
            if not (_is_ring(st.get("obrys")) and _is_num(st.get("wierzch")) and _is_num(st.get("grubosc"))):
                continue
            sid = str(st["id"])
            nad = str(st.get("nad"))
            lvl = self._level_above(nad)
            poly = make_polygon(st["obrys"], st.get("otwory") or [])
            mat = str(st.get("mat") or self.beton)
            self.add(sid, "slab", poly, st["wierzch"] - st["grubosc"], st["wierzch"], mat, lvl, part="plyta")
            self._soffit(sid, poly, st["wierzch"] - st["grubosc"], nad, lvl, None)
            # warstwy podłogi nad płytą
            pk = st.get("podloga") or (m.kondygnacja(lvl).podloga if lvl in self.kondy and lvl != nad else None)
            p = m.przegroda(str(pk)) if pk else None
            if p is not None and lvl != nad:
                region = clean_geom(self._free(lvl).intersection(poly))
                if not region.is_empty:
                    lays = p.warstwy_nad_konstr()
                    ztop = st["wierzch"] + sum(x.d for x in lays)
                    self._stack_layers(f"{sid}", region, ztop, lays, lvl, rooms=m.pomieszczenia(lvl))
            # sufit pod płytą
            suf = st.get("sufit")
            if suf and nad in self.kondy:
                region = clean_geom(self._free(nad).intersection(poly))
                if not region.is_empty:
                    sp = m.przegroda(str(suf))
                    d = sp.grubosc if sp else 0.01
                    zs = st["wierzch"] - st["grubosc"]
                    self.add(sid, "slab", region, zs - d, zs, str(suf) if not sp else sp.warstwy[-1].mat, nad,
                             part="sufit")

    def _attic_ring(self, obrys: Polygon, szer: float, z_level: float) -> Any:
        ring = clean_geom(obrys.difference(obrys.buffer(-szer, join_style=2)))
        # bez attyki wzdłuż ścian wyższych kondygnacji stojących na płycie
        higher = [self.m.obrys_kondygnacji(k.id) for k in self.m.kondygnacje
                  if self.m.kond_z_od(k.id) >= z_level - 0.10]
        higher = [g for g in higher if not g.is_empty]
        if higher:
            ring = clean_geom(ring.difference(unary_union(higher).buffer(szer + 0.05, join_style=2)), min_area=1e-3)
        return ring

    def _roof_like(self, rid, obrys_poly, wierzch, grubosc, prz, attyka, kind_slab, lvl, group, below_kond=None,
                   slab_mat=None):
        m = self.m
        mat = slab_mat or (prz.warstwy[prz.idx_konstr].mat if prz is not None and prz.ma_oznaczona_konstr else self.beton)
        spod = wierzch - grubosc
        self.add(rid, kind_slab, obrys_poly, spod, wierzch, mat, lvl, group=group, part="plyta")
        self._soffit(rid, obrys_poly, spod, below_kond, lvl, group)
        lays_up = prz.warstwy_nad_konstr() if prz is not None else []
        d_up = sum(x.d for x in lays_up)
        top = wierzch + d_up
        full = Polygon(obrys_poly.exterior) if isinstance(obrys_poly, Polygon) else obrys_poly
        if attyka:
            szer = float(attyka.get("szer", 0.25))
            wys = float(attyka.get("wys_nad_pokryciem", 0.30))
            ring = self._attic_ring(full, szer, wierzch)
            inner = clean_geom(obrys_poly.difference(ring))
            if lays_up:
                kk = "terrace" if kind_slab == "canopy" else "roof"
                self._stack_layers(rid, inner, top, lays_up, lvl, kind=kk, part="pokrycie", group=group)
            if not ring.is_empty:
                zt = top + wys
                self.add(rid, "parapet", ring, wierzch, zt, mat, lvl, group=group, part="attyka")
                # okładzina czołowa (ETICS/tynk) i obróbka blacharska
                clad = clean_geom(full.buffer(0.10, join_style=2).difference(full)
                                  .intersection(ring.buffer(0.12, join_style=2)), min_area=1e-4)
                fin = self._facade_finish()
                self.add(rid, "parapet", clad, spod, zt, fin, lvl, group=group, part="okladzina_attyki")
                cop = clean_geom(ring.buffer(0.03, join_style=2).union(clad.buffer(0.03, join_style=2))
                                 .intersection(full.buffer(0.13, join_style=2)), min_area=1e-4)
                self.add(rid, "parapet", cop, zt, zt + 0.02, M_OBROBKA, lvl, group=group, part="obrobka")
        else:
            if lays_up:
                kk = "terrace" if kind_slab == "canopy" else "roof"
                self._stack_layers(rid, obrys_poly, top, lays_up, lvl, kind=kk, part="pokrycie", group=group)
            if kind_slab == "roof":
                band = clean_geom(full.buffer(0.02, join_style=2).difference(full), min_area=1e-5)
                self.add(rid, "parapet", band, spod - 0.02, top + 0.03, M_OBROBKA, lvl, group=group, part="pas_czolowy")
        lays_dn = prz.warstwy_pod_konstr() if prz is not None else []
        if lays_dn and below_kond in self.kondy:
            region = clean_geom(self._free(below_kond).intersection(obrys_poly))
            if not region.is_empty:
                self._stack_layers(rid, region, spod, lays_dn, below_kond, kind=kind_slab, part="sufit", group=group)
        return top

    def _soffit(self, rid, poly, spod, below_kond, lvl, group):
        """Podsufitka (tynk elewacyjny) pod częścią płyty wysuniętą poza obrys kondygnacji niżej."""
        if below_kond not in self.kondy:
            outline = Polygon()
        else:
            outline = self.m.obrys_kondygnacji(below_kond)
        full = Polygon(poly.exterior) if isinstance(poly, Polygon) else poly
        reg = clean_geom(full.difference(outline.buffer(0.02, join_style=2)) if not outline.is_empty else full,
                         min_area=0.05)
        if not reg.is_empty:
            self.add(rid, "slab", reg, spod - 0.015, spod, self._facade_finish(), lvl, group=group, part="podsufitka")

    def _facade_finish(self) -> str:
        for s in self.m.sciany():
            if s.typ == "sciana_zewn":
                return s.warstwy[-1].mat if s.sgn_int > 0 else s.warstwy[0].mat
        return "TYNK_SIL"

    def _dachy(self):
        m = self.m
        for d in m.dachy():
            if not (_is_ring(d.get("obrys")) and isinstance(d.get("plyta"), dict)):
                continue
            pl = d["plyta"]
            if not (_is_num(pl.get("wierzch")) and _is_num(pl.get("grubosc"))):
                continue
            rid = str(d["id"])
            prz = m.przegroda(str(d.get("przegroda")))
            poly = make_polygon(d["obrys"], d.get("otwory") or [])
            below = None
            for k in reversed(m.kondygnacje):
                if m.kond_z_od(k.id) < pl["wierzch"] - 0.5:
                    below = k.id
                    break
            self._roof_like(rid, poly, pl["wierzch"], pl["grubosc"], prz, d.get("attyka"), "roof", below, "dach",
                            below_kond=below, slab_mat=d.get("mat"))

    def _wsporniki(self):
        m = self.m
        for w in m.wsporniki():
            if not (_is_ring(w.get("obrys")) and _is_num(w.get("wierzch")) and _is_num(w.get("grubosc"))):
                continue
            wid = str(w["id"])
            prz = m.przegroda(str(w.get("przegroda"))) if w.get("przegroda") else None
            lvl = m.kond_poziomu(w["wierzch"] + 0.05)
            poly = make_polygon(w["obrys"])
            below = None
            for k in reversed(m.kondygnacje):
                if m.kond_z_od(k.id) < w["wierzch"] - 0.5:
                    below = k.id
                    break
            self._roof_like(wid, poly, w["wierzch"], w["grubosc"], prz, w.get("attyka"), "canopy", lvl, lvl,
                            below_kond=below, slab_mat=w.get("mat"))

    # ---------------- konstrukcja ----------------
    def _slupy(self):
        for s in self.m.slupy():
            if not (_is_pt(s.get("xy")) and _is_num(s.get("z_od")) and _is_num(s.get("z_do"))):
                continue
            x, y = s["xy"]
            txt = str(s.get("przekroj", ""))
            a, b = parse_przekroj(txt)
            if is_circular(txt):
                poly = Point(x, y).buffer(a / 2, quad_segs=6)
            else:
                poly = box(x - a / 2, y - b / 2, x + a / 2, y + b / 2)
            lvl = self.m.kond_poziomu(s["z_od"] + 0.5)
            self.add(str(s["id"]), "column", poly, s["z_od"], s["z_do"], str(s.get("mat")), lvl, przekroj=txt)

    def _rect_along(self, p1, p2, b, ext=0.0):
        p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
        v = p2 - p1
        L = float(np.hypot(*v))
        if L < 1e-9:
            return box(p1[0] - b / 2, p1[1] - b / 2, p1[0] + b / 2, p1[1] + b / 2)
        u = v / L
        n = np.array([-u[1], u[0]])
        a, c = p1 - u * ext, p2 + u * ext
        return Polygon([tuple(a - n * b / 2), tuple(c - n * b / 2), tuple(c + n * b / 2), tuple(a + n * b / 2)])

    def _belki(self):
        for bm in self.m.belki():
            if not (isinstance(bm.get("os"), list) and _is_num(bm.get("b")) and _is_num(bm.get("h"))):
                continue
            poly = self._rect_along(bm["os"][0], bm["os"][1], bm["b"])
            lvl = self.m.kond_poziomu(bm["spod"])
            self.add(str(bm["id"]), "beam", poly, bm["spod"], bm["spod"] + bm["h"], str(bm.get("mat")), lvl)

    def _fundamenty(self):
        m = self.m
        fu = m.fundamenty()
        els = fu.get("elementy") or []
        foot_polys = []
        for e in els:
            if not isinstance(e, dict):
                continue
            if "os" in e and _is_num(e.get("b")):
                poly = self._rect_along(e["os"][0], e["os"][1], e["b"], ext=e["b"] / 2)
            elif _is_ring(e.get("obrys")):
                poly = make_polygon(e["obrys"])
            else:
                continue
            if not (_is_num(e.get("spod")) and _is_num(e.get("h"))):
                continue
            mat = str(e.get("mat") or self.beton)
            self.add(str(e.get("id", "F")), "footing", poly, e["spod"], e["spod"] + e["h"], mat, None,
                     group="fundamenty")
            foot_polys.append((poly, e["spod"] + e["h"]))
        # ściany fundamentowe pod ścianami nośnymi najniższej kondygnacji (ławy)
        if fu.get("typ") == "lawy" and m.kondygnacje and foot_polys:
            k0 = m.kondygnacje[0].id
            xps = next((c for c in m.materialy if "XPS" in c.upper()), None)
            for w in m.sciany(k0):
                if w.typ not in ("sciana_zewn", "sciana_wewn_nosna"):
                    continue
                kl = w.warstwa_konstr
                tops = [zt for fp, zt in foot_polys if fp.intersects(kl.polygon)]
                if not tops:
                    continue
                zt = max(tops)
                if w.z_od - zt < 0.05:
                    continue
                self.add(f"{w.id}-F", "footing", kl.polygon, zt, w.z_od, kl.mat, None, group="fundamenty",
                         part="sciana_fundamentowa", wall=w.id)
                if w.ext_side is not None and xps:
                    tk = w.face_t(w.ext_side, "k")
                    t2 = tk + w.ext_side * 0.12
                    band = clean_geom(w.band(t0=min(tk, t2), t1=max(tk, t2), s0=-0.4, s1=w.L + 0.4)
                                      .difference(unary_union([s.polygon for s in m.sciany(k0)])))
                    zb = min(l.z0 for l in w.warstwy)
                    if not band.is_empty and zb - zt > 0.05:
                        self.add(f"{w.id}-F", "insulation", band, zt, zb, xps, None, group="fundamenty",
                                 part="izolacja_fundamentu", wall=w.id)

    # ---------------- schody, balustrady, lamele, tarasy ----------------
    def _schody(self):
        m = self.m
        for sch in m.schody():
            sid = str(sch["id"])
            try:
                zk = m.kondygnacja(str(sch["z_kond"]))
            except KeyError:
                continue
            h = float(sch["wys_stopnia"])
            g = float(sch["szer_stopnia"])
            mat = str(sch.get("mat") or M_SCHODY)
            z = zk.rzedna
            lvl = zk.id
            for bi, bg in enumerate(sch.get("biegi") or []):
                if not isinstance(bg, dict) or not (_is_pt(bg.get("start")) and _is_pt(bg.get("kierunek"))):
                    continue
                S = np.asarray(bg["start"], float)
                d = np.asarray(bg["kierunek"], float)
                d = d / np.hypot(*d)
                n = np.array([-d[1], d[0]])
                b = float(bg.get("szer", 1.0))
                ns = int(bg.get("stopni", 0))
                for j in range(max(ns - 1, 0)):
                    a0, a1 = S + d * j * g, S + d * (j + 1) * g
                    poly = Polygon([tuple(a0 - n * b / 2), tuple(a1 - n * b / 2), tuple(a1 + n * b / 2),
                                    tuple(a0 + n * b / 2)])
                    top = z + (j + 1) * h
                    self.add(sid, "stair_step", poly, max(top - h - 0.14, z - 0.02) if j == 0 else top - h - 0.14,
                             top, mat, lvl, bieg=bi + 1, stopien=j + 1)
                z += ns * h
            for sp in sch.get("spoczniki") or []:
                if isinstance(sp, dict) and _is_ring(sp.get("obrys")) and _is_num(sp.get("rzedna")):
                    self.add(sid, "landing", make_polygon(sp["obrys"]), sp["rzedna"] - 0.18, sp["rzedna"], mat, lvl)

    def _balustrady(self):
        for bl in self.m.balustrady():
            pts = bl.get("polilinia")
            if not isinstance(pts, list) or len(pts) < 2:
                continue
            bid = str(bl["id"])
            H = float(bl.get("wys", 1.1))
            typ = str(bl.get("typ") or "").lower()
            glass = "szk" in typ
            stal = M_STAL_NIERDZ if "nierdz" in typ else M_STAL_BAL
            lvl = self.m.kond_poziomu(min(p[2] for p in pts) + 0.3)
            for a, b in zip(pts[:-1], pts[1:]):
                A, B = np.asarray(a, float), np.asarray(b, float)
                L = float(np.hypot(*(B[:2] - A[:2])))
                if L < 1e-6:
                    continue
                sloped = abs(B[2] - A[2]) > 0.01
                npc = max(1, math.ceil(L / 0.25)) if sloped else 1
                for i in range(npc):
                    f0, f1 = i / npc, (i + 1) / npc
                    P0 = A + (B - A) * f0
                    P1 = A + (B - A) * f1
                    zb = (P0[2] + P1[2]) / 2
                    if glass:
                        self.add(bid, "railing", self._rect_along(P0[:2], P1[:2], 0.02), zb + 0.02, zb + H - 0.05,
                                 M_SZKLO_BAL, lvl, part="szyba")
                    self.add(bid, "railing", self._rect_along(P0[:2], P1[:2], 0.05 if glass else 0.045),
                             zb + H - 0.05, zb + H, stal, lvl, part="pochwyt")
                    if not glass:
                        self.add(bid, "railing", self._rect_along(P0[:2], P1[:2], 0.012), zb + 0.05, zb + 0.09, stal,
                                 lvl, part="przeczka")
                if not glass:
                    nb = max(1, math.ceil(L / 0.11))
                    for i in range(nb + 1):
                        f = i / nb
                        P = A + (B - A) * f
                        self.add(bid, "railing", box(P[0] - 0.007, P[1] - 0.007, P[0] + 0.007, P[1] + 0.007),
                                 P[2] + 0.05, P[2] + H - 0.05, stal, lvl, part="pret")

    def _lamele(self):
        dirs = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0), "SE": (1, -1), "SW": (-1, -1), "NE": (1, 1),
                "NW": (-1, 1), "PD": (0, -1), "PN": (0, 1), "WSCH": (1, 0), "ZACH": (-1, 0), "Z": (-1, 0)}
        for lam in self.m.lamele():
            if not isinstance(lam.get("linia"), list):
                continue
            lid = str(lam["id"])
            A, B = np.asarray(lam["linia"][0], float), np.asarray(lam["linia"][1], float)
            L = float(np.hypot(*(B - A)))
            if L < 1e-6:
                continue
            u = (B - A) / L
            n = np.array([-u[1], u[0]])
            el = str(lam.get("elewacja", "")).upper()
            if el in dirs:
                dv = np.asarray(dirs[el], float)
                if float(dv @ n) < 0:
                    n = -n
            bw, hh, rs, od = float(lam["b"]), float(lam["h"]), float(lam["rozstaw"]), float(lam["odsuniecie"])
            z0, z1 = float(lam["z_od"]), float(lam["z_do"])
            cnt = int(math.floor((L - bw) / rs + 1e-9)) + 1
            margin = (L - bw - (cnt - 1) * rs) / 2
            lvl = self.m.kond_poziomu(z0 + 0.3)
            mat = str(lam["mat"])
            for j in range(cnt):
                sc = margin + bw / 2 + j * rs
                p0, p1 = A + u * (sc - bw / 2), A + u * (sc + bw / 2)
                poly = Polygon([tuple(p0 + n * od), tuple(p1 + n * od), tuple(p1 + n * (od + hh)),
                                tuple(p0 + n * (od + hh))])
                self.add(lid, "lamella", poly, z0, z1, mat, lvl, nr=j + 1)
            # rygle nośne (stal) za lamelami
            for zc in (z0 + 0.18, z1 - 0.18):
                poly = Polygon([tuple(A + n * max(od - 0.04, 0.005)), tuple(B + n * max(od - 0.04, 0.005)),
                                tuple(B + n * od), tuple(A + n * od)])
                self.add(lid, "lamella", poly, zc - 0.03, zc + 0.03, M_STAL_BAL, lvl, part="rygiel")

    def _tarasy(self):
        for t in self.m.tarasy():
            if not (_is_ring(t.get("obrys")) and _is_num(t.get("rzedna"))):
                continue
            poly = make_polygon(t["obrys"])
            gr = float(t.get("grubosc") or 0.12)
            z1 = float(t["rzedna"])
            z0 = z1 - gr
            if self._h is not None:
                c = np.asarray(poly.exterior.coords)
                z0 = min(z0, float(self.hs(c[:, :2]).min()) - 0.05)
            lvl = self.m.kond_poziomu(z1)
            mat = material_nawierzchni(t.get("nawierzchnia"))
            self.add(str(t["id"]), "terrace", poly, z1 - 0.03, z1, mat, lvl, part="nawierzchnia")
            self.add(str(t["id"]), "terrace", poly, z0, z1 - 0.03, "NAW_PODBUDOWA", lvl, part="podbudowa")

    # ==================================================================================================
    # Teren i otoczenie
    # ==================================================================================================
    def _terrain(self):
        from scipy.interpolate import LinearNDInterpolator
        from scipy.spatial import Delaunay
        dz = self.m.dz
        pts = dz.teren_punkty()
        if len(pts) < 3:
            return
        tri0 = Delaunay(pts[:, :2])
        lin = LinearNDInterpolator(tri0, pts[:, 2])
        A = np.c_[pts[:, 0], pts[:, 1], np.ones(len(pts))]
        coef, *_ = np.linalg.lstsq(A, pts[:, 2], rcond=None)
        hull = MultiPoint([tuple(p) for p in pts[:, :2]]).convex_hull
        hc = np.array(hull.centroid.coords[0])
        ring = hull.exterior if isinstance(hull, Polygon) else None

        def plane(xy):
            return coef[0] * xy[:, 0] + coef[1] * xy[:, 1] + coef[2]

        def height(xy):
            xy = np.asarray(xy, float).reshape(-1, 2)
            z = np.asarray(lin(xy), float).reshape(-1)
            bad = ~np.isfinite(z)
            if bad.any():
                if ring is not None:
                    pos = shapely.line_locate_point(ring, shapely.points(xy[bad]))
                    q = shapely.get_coordinates(shapely.line_interpolate_point(ring, pos))
                    q = q + (hc - q) * 1e-6
                    zq = np.asarray(lin(q), float).reshape(-1)
                    zq = np.where(np.isfinite(zq), zq, plane(q))
                    z[bad] = plane(xy[bad]) + (zq - plane(q))
                else:
                    z[bad] = plane(xy[bad])
            return z

        self._h = height
        # zasięg
        geoms = [g for g in [dz.obrys, self.footprint] if g is not None and not g.is_empty]
        for s in dz.lista("sasiedzi"):
            if isinstance(s, dict) and _is_ring(s.get("obrys")):
                geoms.append(dz.poly_bud(s["obrys"]))
        dr = dz.raw.get("droga") or {}
        if _is_ring(dr.get("jezdnia")):
            geoms.append(dz.poly_bud(dr["jezdnia"]))
        U = unary_union(geoms)
        plot = dz.obrys if dz.obrys is not None else self.footprint.buffer(15)
        pb = plot.bounds
        ext = box(*U.bounds).buffer(25, join_style=2)
        lim = box(pb[0] - 90, pb[1] - 90, pb[2] + 90, pb[3] + 90)
        ext = ext.intersection(lim)
        xb0, yb0, xb1, yb1 = ext.bounds
        fine = plot.buffer(8, join_style=2)
        fx0, fy0, fx1, fy1 = fine.bounds
        g1 = np.mgrid[fx0:fx1 + 1e-9:1.0, fy0:fy1 + 1e-9:1.0].reshape(2, -1).T
        g5 = np.mgrid[xb0:xb1 + 1e-9:5.0, yb0:yb1 + 1e-9:5.0].reshape(2, -1).T
        g5 = g5[~shapely.contains_xy(fine.buffer(1.0), g5[:, 0], g5[:, 1])]
        grid = np.vstack([g1, g5, np.array(ext.exterior.coords[:-1])])
        fp = self.footprint
        if not fp.is_empty:
            keep = ~shapely.contains_xy(fp.buffer(0.35, join_style=2), grid[:, 0], grid[:, 1])
            grid = grid[keep]
            bnd = []
            for poly in iter_polys(fp):
                seg = shapely.segmentize(poly.exterior, 0.3)
                bnd.append(np.asarray(seg.coords)[:-1])
            bnd = np.vstack(bnd) if bnd else np.zeros((0, 2))
            sp = pts[:, :2][~shapely.contains_xy(fp.buffer(0.35), pts[:, 0], pts[:, 1])]
            allp = np.vstack([grid, bnd, sp])
        else:
            allp = np.vstack([grid, pts[:, :2]])
        allp = np.unique(np.round(allp, 4), axis=0)
        tri = Delaunay(allp)
        F = tri.simplices.copy()
        V2 = allp
        c = V2[F].mean(axis=1)
        if not fp.is_empty:
            inside = shapely.contains_xy(fp, c[:, 0], c[:, 1])
            F = F[~inside]
            c = c[~inside]
        # orientacja CCW
        a, b, cc = V2[F[:, 0]], V2[F[:, 1]], V2[F[:, 2]]
        cr = (b[:, 0] - a[:, 0]) * (cc[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (cc[:, 0] - a[:, 0])
        F[cr < 0] = F[cr < 0][:, [0, 2, 1]]
        Z = height(V2)
        V = np.column_stack([V2, Z])
        inplot = shapely.contains_xy(plot, c[:, 0], c[:, 1])
        mats = np.where(inplot, M_TEREN, M_TEREN_POZA).tolist()
        self.ir.terrain = TerrainMesh(id="TEREN", vertices=V, faces=F, face_material=mats, height_fn=height,
                                      meta={"group": "teren", "punkty_wysokosciowe": int(len(pts)),
                                            "zasieg": [round(v, 2) for v in ext.bounds]})

    def _draped(self, base_id, kind, poly, material, dz_top, depth, cell=1.5, group="otoczenie", **meta):
        """Pryzmy dopasowane do terenu: wielobok dzielony na komórki; wierzch = teren + dz_top."""
        if poly is None or poly.is_empty:
            return
        x0, y0, x1, y1 = poly.bounds
        nx = max(1, math.ceil((x1 - x0) / cell))
        ny = max(1, math.ceil((y1 - y0) / cell))
        for i in range(nx):
            for j in range(ny):
                cb = box(x0 + i * cell, y0 + j * cell, min(x1, x0 + (i + 1) * cell), min(y1, y0 + (j + 1) * cell))
                part = clean_geom(poly.intersection(cb), min_area=1e-4)
                for pp in iter_polys(part):
                    cc = np.asarray(pp.exterior.coords)[:, :2]
                    hz = self.hs(cc)
                    self.add(base_id, kind, pp, float(hz.min()) - depth, float(hz.max()) + dz_top, material, None,
                             group=group, **meta)

    def _otoczenie(self):
        dz = self.m.dz
        fp = self.footprint.buffer(0.01)
        terr = unary_union([make_polygon(t["obrys"]) for t in self.m.tarasy() if _is_ring(t.get("obrys"))]) \
            if self.m.tarasy() else Polygon()
        blocked = unary_union([fp, terr])
        # droga
        dr = dz.raw.get("droga") or {}
        if _is_ring(dr.get("jezdnia")):
            self._draped(f"DROGA-{dr.get('symbol', '')}".rstrip("-"), "road", dz.poly_bud(dr["jezdnia"]),
                         material_nawierzchni(dr.get("nawierzchnia") or "asfalt"), 0.04, 0.25, cell=3.0)
        # utwardzenia
        for i, u in enumerate(dz.lista("utwardzenia")):
            if isinstance(u, dict) and _is_ring(u.get("obrys")):
                poly = clean_geom(dz.poly_bud(u["obrys"]).difference(blocked))
                self._draped(str(u.get("id", f"U{i + 1}")), "pavement", poly, material_nawierzchni(u.get("nawierzchnia")),
                             0.035, 0.25, nawierzchnia=u.get("nawierzchnia"))
        # miejsca postojowe
        for i, mp in enumerate(dz.lista("miejsca_postojowe")):
            if not (isinstance(mp, dict) and _is_ring(mp.get("obrys"))):
                continue
            poly = dz.poly_bud(mp["obrys"])
            mid = str(mp.get("id", f"MP{i + 1}"))
            free = clean_geom(poly.difference(blocked))
            self._draped(mid, "pavement", free, "NAW_KOSTKA_JASNA" if mp.get("typ") == "zewn" else "NAW_KOSTKA",
                         0.04, 0.25, typ=mp.get("typ"))
            if self.auta and mp.get("auto", True):
                self._cars_in(mid, poly, i)
        # zieleń
        for i, z in enumerate(dz.lista("zielen")):
            if not (isinstance(z, dict) and _is_ring(z.get("obrys"))):
                continue
            poly = clean_geom(dz.poly_bud(z["obrys"]).difference(blocked))
            zid = str(z.get("id", f"Z{i + 1}"))
            if z.get("typ") == "zywoplot":
                self._draped(zid, "vegetation", poly, "ZYWOPLOT", float(z.get("wys") or 1.5), 0.1, cell=1.5,
                             typ="zywoplot")
            elif z.get("typ") == "rabata":
                self._draped(zid, "vegetation", poly, "MULCZ", 0.06, 0.1, cell=1.5, typ="rabata")
                self._shrubs(zid, poly, i)
        # drzewa
        for i, t in enumerate(dz.lista("drzewa")):
            if isinstance(t, dict) and _is_pt(t.get("xy")) and not t.get("do_wyciecia"):
                self._tree(t, i)
        # ogrodzenia i bramy
        for i, f in enumerate(dz.lista("ogrodzenie")):
            if isinstance(f, dict) and isinstance(f.get("linia"), list) and len(f["linia"]) >= 2:
                self._fence(f"OGR{i + 1}", dz.ring_bud(f["linia"]), float(f.get("wys", 1.5)), str(f.get("typ") or ""))
        for i, g in enumerate(dz.lista("bramy")):
            if isinstance(g, dict) and _is_pt(g.get("xy")):
                self._gate(g, i)
        # odpady
        od = dz.raw.get("odpady")
        if isinstance(od, dict) and _is_ring(od.get("obrys")):
            poly = dz.poly_bud(od["obrys"])
            cc = np.asarray(poly.exterior.coords)[:, :2]
            hz = self.hs(cc)
            shell = clean_geom(poly.difference(poly.buffer(-0.04, join_style=2)))
            self.add("ODPADY", "fence", shell, float(hz.min()) - 0.05, float(hz.max()) + 1.35, "OSLONA_DREWNO", None,
                     group="otoczenie", part="oslona_smietnikowa")
            self.add("ODPADY", "pavement", poly, float(hz.min()) - 0.15, float(hz.max()) + 0.04, "NAW_PLYTY", None,
                     group="otoczenie")
        # sąsiedzi
        for i, s in enumerate(dz.lista("sasiedzi")):
            if isinstance(s, dict) and s.get("zabudowa") is not None:
                self._neighbour(s, i)

    # ---------------- elementy otoczenia ----------------
    def _tree(self, t, i):
        dz = self.m.dz
        x, y = dz.do_budynku(np.asarray(t["xy"], float))
        sr = float(t.get("sr_korony", 4.0))
        gat = str(t.get("gat") or "").lower()
        conifer = bool(re.search(r"sosn|świerk|swierk|jodł|jodl|modrzew|tuj|thuj|cis|jałow|jalow|daglez", gat))
        birch = "brzoz" in gat
        H = float(t.get("wys") or (2.2 * sr + 1.0 if conifer else max(4.0, 1.35 * sr + 1.8)))
        z = self.h(x, y)
        tid = str(t.get("id", f"DRZ{i + 1}"))
        rng = np.random.default_rng(1000 + i)
        rt = 0.07 + 0.025 * sr
        trunk_h = (0.25 if conifer else 0.38) * H
        oct_ = Point(x, y).buffer(rt, quad_segs=2)
        self.add(tid, "vegetation", oct_, z - 0.2, z + trunk_h + (0.3 * H if not conifer else 0.1 * H),
                 "PIEN_BRZOZA" if birch else "PIEN", None, group="otoczenie", part="pien", gatunek=t.get("gat"),
                 istniejace=bool(t.get("istn", False)))
        if conifer:
            V, Fc = _cone(x, y, z + trunk_h * 0.8, sr / 2, H - trunk_h * 0.8, 10, rng)
            self.add_mesh(tid, "vegetation", V, Fc, "KORONA_IGL", part="korona", gatunek=t.get("gat"))
        else:
            rx = sr / 2 * (0.8 if birch else 1.0)
            ch = H - trunk_h
            zc = z + trunk_h + ch / 2
            nb = 6 if not birch else 5
            Vs, Fs, off = [], [], 0
            for k in range(nb):
                if k == 0:
                    ox, oy, oz, rr = 0.0, 0.0, 0.0, 0.62
                else:
                    a = 2 * math.pi * (k - 1) / (nb - 1) + rng.uniform(-0.4, 0.4)
                    ox, oy = math.cos(a) * rx * 0.42, math.sin(a) * rx * 0.42
                    oz = rng.uniform(-0.25, 0.3) * ch / 2
                    rr = rng.uniform(0.5, 0.62)
                V, Fc = _blob(x + ox, y + oy, zc + oz, rx * rr, rx * rr, ch / 2 * rr * 1.05, rng, 2)
                Vs.append(V)
                Fs.append(Fc + off)
                off += len(V)
            self.add_mesh(tid, "vegetation", np.vstack(Vs), np.vstack(Fs), "KORONA_BRZOZA" if birch else "KORONA",
                          part="korona", gatunek=t.get("gat"), smooth=True)

    def _shrubs(self, zid, poly, i):
        rng = np.random.default_rng(500 + i)
        area = poly.area
        n = int(min(40, max(2, area / 1.2)))
        x0, y0, x1, y1 = poly.bounds
        cnt = 0
        tries = 0
        while cnt < n and tries < n * 20:
            tries += 1
            px, py = rng.uniform(x0, x1), rng.uniform(y0, y1)
            if not poly.contains(Point(px, py)):
                continue
            r = rng.uniform(0.25, 0.45)
            zc = self.h(px, py) + r * 0.7
            V, Fc = _blob(px, py, zc, r, r, r * 0.8, rng, 1)
            self.add_mesh(zid, "vegetation", V, Fc, "KRZEW", part="krzew", smooth=True)
            cnt += 1

    def _fence(self, fid, line, H, typ):
        t = typ.lower()
        solid = "mur" in t or "pełn" in t or "peln" in t
        slats = "szta" in t or "ażur" in t or "azur" in t or "lamel" in t
        for a, b in zip(line[:-1], line[1:]):
            A, B = np.asarray(a, float), np.asarray(b, float)
            L = float(np.hypot(*(B - A)))
            if L < 1e-6:
                continue
            u = (B - A) / L
            n = np.array([-u[1], u[0]])
            npst = max(1, math.ceil(L / 2.5))
            for k in range(npst + 1):
                P = A + u * (L * k / npst)
                zc = self.h(*P)
                self.add(fid, "fence", box(P[0] - 0.04, P[1] - 0.04, P[0] + 0.04, P[1] + 0.04), zc - 0.3, zc + H + 0.03,
                         "OGRODZENIE", None, group="otoczenie", part="slupek")
            nseg = max(1, math.ceil(L / 2.5))
            for k in range(nseg):
                P0, P1 = A + u * (L * k / nseg), A + u * (L * (k + 1) / nseg)
                z0 = min(self.h(*P0), self.h(*P1))
                if solid:
                    self.add(fid, "fence", self._rect_along(P0, P1, 0.2), z0 - 0.3, z0 + H, "PODMUROWKA", None,
                             group="otoczenie", part="mur")
                    continue
                if slats:
                    self.add(fid, "fence", self._rect_along(P0, P1, 0.18), z0 - 0.3, z0 + 0.25, "PODMUROWKA", None,
                             group="otoczenie", part="podmurowka")
                    ls = float(np.hypot(*(P1 - P0)))
                    ns = max(1, int(ls / 0.11))
                    for s in range(ns):
                        c = P0 + u * (ls * (s + 0.5) / ns)
                        poly = Polygon([tuple(c - u * 0.02 - n * 0.015), tuple(c + u * 0.02 - n * 0.015),
                                        tuple(c + u * 0.02 + n * 0.015), tuple(c - u * 0.02 + n * 0.015)])
                        self.add(fid, "fence", poly, z0 + 0.25, z0 + H, "OGRODZENIE", None, group="otoczenie",
                                 part="sztacheta")
                    self.add(fid, "fence", self._rect_along(P0, P1, 0.02), z0 + H - 0.2, z0 + H - 0.16, "OGRODZENIE",
                             None, group="otoczenie", part="rygiel")
                else:
                    self.add(fid, "fence", self._rect_along(P0, P1, 0.006), z0 + 0.05, z0 + H, "SIATKA", None,
                             group="otoczenie", part="panel")

    def _gate(self, g, i):
        dz = self.m.dz
        c = dz.do_budynku(np.asarray(g["xy"], float))
        szer = float(g["szer"])
        u = None
        if _is_pt(g.get("kierunek")):
            u = np.asarray(g["kierunek"], float)
        else:
            best = 1e9
            for f in dz.lista("ogrodzenie"):
                if not (isinstance(f, dict) and isinstance(f.get("linia"), list)):
                    continue
                line = dz.ring_bud(f["linia"])
                for a, b in zip(line[:-1], line[1:]):
                    ls = LineString([a, b])
                    d = ls.distance(Point(c))
                    if d < best:
                        best = d
                        v = np.asarray(b) - np.asarray(a)
                        u = v
            if best > 3.0:
                u = None
        if u is None:
            u = np.array([1.0, 0.0])
        u = u / np.hypot(*u)
        n = np.array([-u[1], u[0]])
        H = float(g.get("wys") or 1.5)
        gid = f"BRAMA{i + 1}"
        A, B = c - u * szer / 2, c + u * szer / 2
        for P in (A, B):
            zc = self.h(*P)
            self.add(gid, "fence", box(P[0] - 0.06, P[1] - 0.06, P[0] + 0.06, P[1] + 0.06), zc - 0.3, zc + H + 0.08,
                     "OGRODZENIE", None, group="otoczenie", part="slup_bramy")
        z0 = min(self.h(*A), self.h(*B))
        L = szer - 0.14
        P0 = A + u * 0.07
        ns = max(1, int(L / 0.11))
        for s in range(ns):
            cc = P0 + u * (L * (s + 0.5) / ns)
            poly = Polygon([tuple(cc - u * 0.02 - n * 0.015), tuple(cc + u * 0.02 - n * 0.015),
                            tuple(cc + u * 0.02 + n * 0.015), tuple(cc - u * 0.02 + n * 0.015)])
            self.add(gid, "fence", poly, z0 + 0.06, z0 + H, "OGRODZENIE", None, group="otoczenie", part="brama",
                     typ=g.get("typ"))
        for zz in (z0 + 0.06, z0 + H - 0.06):
            self.add(gid, "fence", self._rect_along(P0, P0 + u * L, 0.04), zz, zz + 0.06, "OGRODZENIE", None,
                     group="otoczenie", part="rama_bramy")

    def _neighbour(self, s, i):
        dz = self.m.dz
        zb = s.get("zabudowa")
        rings = []
        if _is_ring(zb):
            rings = [zb]
        elif isinstance(zb, list) and zb and all(_is_ring(r) for r in zb):
            rings = zb
        H = float(s.get("wys") or 7.5)
        flat = str(s.get("dach") or "").lower().startswith("pla")
        for j, r in enumerate(rings):
            poly = dz.poly_bud(r)
            cc = np.asarray(poly.exterior.coords)[:, :2]
            z0 = float(self.hs(cc).min())
            nid = f"SASIAD-{s.get('nr', i + 1)}".replace("/", "_") + (f"-{j + 1}" if len(rings) > 1 else "")
            if flat:
                self.add(nid, "context", poly, z0 - 0.3, z0 + H, "SASIEDNI_SCIANA", None, group="otoczenie")
                self.add(nid, "context", clean_geom(poly.difference(poly.buffer(-0.25))), z0 + H, z0 + H + 0.35,
                         "SASIEDNI_SCIANA", None, group="otoczenie")
                continue
            eave = z0 + max(3.0, H * 0.58)
            self.add(nid, "context", poly, z0 - 0.3, eave, "SASIEDNI_SCIANA", None, group="otoczenie")
            V, Fc, Vg, Fg = _gable_roof(poly, eave, z0 + H, 0.45)
            if V is not None:
                self.add_mesh(nid, "context", V, Fc, "SASIEDNI_DACH", part="dach")
                self.add_mesh(nid, "context", Vg, Fg, "SASIEDNI_SCIANA", part="szczyt", closed=False)

    def _cars_in(self, mid, poly, i):
        mrr = poly.minimum_rotated_rectangle
        c = np.asarray(mrr.exterior.coords)[:4]
        e1, e2 = c[1] - c[0], c[2] - c[1]
        l1, l2 = float(np.hypot(*e1)), float(np.hypot(*e2))
        if max(l1, l2) < 4.3 or min(l1, l2) < 2.2:
            return
        u = e1 / l1 if l1 >= l2 else e2 / l2
        width = min(l1, l2)
        ctr = np.asarray(poly.centroid.coords[0])
        n = np.array([-u[1], u[0]])
        slots = [ctr]
        if width >= 5.0:
            slots = [ctr - n * width / 4, ctr + n * width / 4]
        cols = ["AUTO_LAKIER_1", "AUTO_LAKIER_2", "AUTO_LAKIER_3"]
        for k, sc in enumerate(slots):
            inside = self.footprint.contains(Point(*sc))
            zc = self.m.kondygnacje[0].rzedna if inside else self.h(*sc) + 0.035
            for kind_mat, V, Fc in _car(sc, u if (i + k) % 2 == 0 else -u, zc):
                mat = cols[(i + k) % len(cols)] if kind_mat == "LAKIER" else "AUTO_" + kind_mat
                self.add_mesh(f"AUTO-{mid}-{k + 1}", "vehicle", V, Fc, mat, part=kind_mat.lower())


# --------------------------------------------------------------------------------------------------
# Siatki proste (drzewa, auta, dachy)
# --------------------------------------------------------------------------------------------------
def _icosphere(sub: int):
    t = (1 + 5 ** 0.5) / 2
    V = [(-1, t, 0), (1, t, 0), (-1, -t, 0), (1, -t, 0), (0, -1, t), (0, 1, t), (0, -1, -t), (0, 1, -t),
         (t, 0, -1), (t, 0, 1), (-t, 0, -1), (-t, 0, 1)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in V]
    F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6),
         (7, 1, 8), (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10),
         (8, 6, 7), (9, 8, 1)]
    for _ in range(sub):
        cache = {}
        nf = []

        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key not in cache:
                v = V[a] + V[b]
                V.append(v / np.linalg.norm(v))
                cache[key] = len(V) - 1
            return cache[key]
        for a, b, c in F:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            nf += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        F = nf
    return np.array(V), np.array(F)


def _blob(x, y, z, rx, ry, rz, rng, sub=1):
    V, F = _icosphere(sub)
    jit = 1.0 + rng.uniform(-0.12, 0.12, size=(len(V), 1))
    V = V * jit
    V = V * np.array([rx, ry, rz]) + np.array([x, y, z])
    return V, F


def _cone(x, y, z0, r, h, n, rng):
    V = []
    F = []
    tiers = 3
    for k in range(tiers):
        zb = z0 + h * k / tiers * 0.75
        rr = r * (1 - 0.22 * k)
        ht = h * 0.55
        base = len(V)
        for i in range(n):
            a = 2 * math.pi * i / n
            j = 1 + rng.uniform(-0.08, 0.08)
            V.append((x + rr * j * math.cos(a), y + rr * j * math.sin(a), zb))
        V.append((x, y, zb + ht))
        V.append((x, y, zb))
        apex, bc = base + n, base + n + 1
        for i in range(n):
            a, b = base + i, base + (i + 1) % n
            F.append((a, b, apex))
            F.append((b, a, bc))
    return np.array(V, float), np.array(F, int)


def _gable_roof(poly: Polygon, z_eave: float, z_ridge: float, overhang: float):
    mrr = poly.minimum_rotated_rectangle
    c = np.asarray(mrr.exterior.coords)[:4]
    e1, e2 = c[1] - c[0], c[2] - c[1]
    if np.hypot(*e1) < np.hypot(*e2):
        c = np.roll(c, -1, axis=0)
        e1, e2 = c[1] - c[0], c[2] - c[1]
    u = e1 / np.hypot(*e1)
    v = e2 / np.hypot(*e2)
    p0 = c[0] - u * overhang - v * overhang
    p1 = c[1] + u * overhang - v * overhang
    p2 = c[2] + u * overhang + v * overhang
    p3 = c[3] - u * overhang + v * overhang
    r0 = (c[0] + c[3]) / 2 - u * overhang
    r1 = (c[1] + c[2]) / 2 + u * overhang
    ze = z_eave - overhang * (z_ridge - z_eave) / (np.hypot(*e2) / 2)
    V = np.array([[*p0, ze], [*p1, ze], [*r1, z_ridge], [*r0, z_ridge], [*p3, ze], [*p2, ze]], float)
    th = 0.18
    Vb = V.copy()
    Vb[:, 2] -= th
    VV = np.vstack([V, Vb])
    F = [(0, 1, 2), (0, 2, 3), (4, 3, 2), (4, 2, 5),                      # połacie (góra)
         (6, 8, 7), (6, 9, 8), (10, 8, 9), (10, 11, 8),                   # spód
         (0, 6, 7), (0, 7, 1), (5, 11, 10), (5, 10, 4),                   # okapy
         (1, 7, 8), (1, 8, 2), (5, 2, 8), (5, 8, 11),                     # krawędź szczytowa E
         (0, 3, 9), (0, 9, 6), (4, 10, 9), (4, 9, 3)]                     # krawędź szczytowa W
    # szczyty (ściany trójkątne)
    q0, q1, q2, q3 = c
    m03, m12 = (q0 + q3) / 2, (q1 + q2) / 2
    Vg = np.array([[*q0, z_eave], [*q3, z_eave], [*m03, z_ridge - th], [*q1, z_eave], [*q2, z_eave], [*m12, z_ridge - th]])
    Fg = np.array([(0, 2, 1), (0, 1, 2), (3, 4, 5), (3, 5, 4)])
    return VV, np.array(F), Vg, Fg


def _extrude_profile(profile, width, origin, u, zoff):
    """Profil (s, z) w płaszczyźnie pionowej wzdłuż u, wyciągnięty na szerokość (±width/2 wzdłuż normalnej)."""
    import shapely as _sh
    P = Polygon(profile)
    tris = [np.asarray(t.exterior.coords)[:3] for t in _sh.constrained_delaunay_triangles(P).geoms]
    n = np.array([-u[1], u[0]])
    o = np.asarray(origin, float)

    def to3(s, z, side):
        xy = o + u * s + n * side * width / 2
        return (xy[0], xy[1], zoff + z)
    V, F = [], []
    for tri in tris:
        a = sum((tri[k][0] * tri[(k + 1) % 3][1] - tri[(k + 1) % 3][0] * tri[k][1]) for k in range(3))
        if a < 0:
            tri = tri[::-1]
        for side, order in ((1, (0, 1, 2)), (-1, (0, 2, 1))):
            base = len(V)
            for k in order:
                V.append(to3(tri[k][0], tri[k][1], side))
            F.append((base, base + 1, base + 2))
    ring = list(P.exterior.coords)[:-1]
    if Polygon(ring).exterior.is_ccw is False:
        ring = ring[::-1]
    for k in range(len(ring)):
        s0, z0 = ring[k]
        s1, z1 = ring[(k + 1) % len(ring)]
        base = len(V)
        V += [to3(s0, z0, 1), to3(s1, z1, 1), to3(s1, z1, -1), to3(s0, z0, -1)]
        F += [(base, base + 2, base + 1), (base, base + 3, base + 2)]
    return np.array(V, float), np.array(F, int)


def _cylinder_h(center, axis_n, r, w, zc, seg=14):
    """Walec o osi poziomej (wzdłuż axis_n) — koło auta."""
    c = np.asarray(center, float)
    n = np.asarray(axis_n, float)
    u = np.array([n[1], -n[0]])
    V, F = [], []
    for side in (-1, 1):
        for i in range(seg):
            a = 2 * math.pi * i / seg
            p = c + n * side * w / 2 + u * r * math.cos(a)
            V.append((p[0], p[1], zc + r * math.sin(a)))
    for side_idx, side in enumerate((-1, 1)):
        ctr = c + n * side * w / 2
        V.append((ctr[0], ctr[1], zc))
    cA, cB = 2 * seg, 2 * seg + 1
    for i in range(seg):
        a0, a1 = i, (i + 1) % seg
        b0, b1 = seg + i, seg + (i + 1) % seg
        F += [(a0, a1, b1), (a0, b1, b0), (cA, a1, a0), (cB, b0, b1)]
    return np.array(V, float), np.array(F, int)


def _car(center, u, z):
    """Uproszczona bryła samochodu osobowego (dł. 4,6 m) — do skali na wizualizacjach."""
    u = np.asarray(u, float) / np.hypot(*u)
    L = 4.6
    body = [(-L / 2, 0.30), (L / 2 - 0.05, 0.30), (L / 2, 0.45), (L / 2 - 0.08, 0.78), (L / 2 - 0.9, 0.92),
            (-L / 2 + 0.25, 0.95), (-L / 2, 0.85), (-L / 2 - 0.02, 0.45)]
    cabin = [(L / 2 - 0.95, 0.90), (-L / 2 + 0.35, 0.93), (-L / 2 + 0.55, 1.42), (L / 2 - 1.85, 1.44)]
    roof = [(L / 2 - 1.80, 1.40), (-L / 2 + 0.60, 1.40), (-L / 2 + 0.62, 1.47), (L / 2 - 1.86, 1.47)]
    out = []
    V, F = _extrude_profile(body, 1.82, center, u, z)
    out.append(("LAKIER", V, F))
    V, F = _extrude_profile(cabin, 1.58, center, u, z)
    out.append(("SZYBA", V, F))
    V, F = _extrude_profile(roof, 1.52, center, u, z)
    out.append(("LAKIER", V, F))
    n = np.array([-u[1], u[0]])
    for sx in (-1.45, 1.40):
        for sy in (-1, 1):
            c = np.asarray(center) + u * sx + n * sy * 0.78
            V, F = _cylinder_h(c, n, 0.33, 0.24, z + 0.33)
            out.append(("OPONA", V, F))
    return out
