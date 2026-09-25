"""RZUT KONDYGNACJI i RZUT DACHU generowane z modelu (``Model`` + IR) do rzutni silnika ``lamela.draft``.

Rzut kondygnacji = przekrój poziomy na wysokości ``wysokosc_ciecia`` (domyślnie 1,10 m) nad posadzką (PN-B-01025,
R4-H05):
  * ściany przecięte: wieloboki warstw z modelu (połączenia naroży L/T wyliczone w rdzeniu), kreskowanie wg pola
    ``kreskowanie`` materiałów przegród (adapter ``common.hatch_code``), kontury wg rodzaju warstwy (konstrukcja
    gruba, izolacja średnia, tynk scalany — R4-C04), otwory wycięte w całej grubości przegrody,
  * stolarka: okna (rama, szyby, parapety, słupki kwater), drzwi (ościeżnica, skrzydło 90° z łukiem wg kierunku
    i strony otwierania z modelu), drzwi HS (skrzydło stałe/przesuwne), brama garażowa (położenie podniesione linią
    kreskową), otwory bez stolarki (nadproże linią kreskową),
  * elementy PONIŻEJ płaszczyzny cięcia — linią cienką (widok z góry z usuwaniem linii niewidocznych: tarasy,
    stopnie, dachy niższych brył, płyty balkonów, krawędzie posadzek),
  * elementy POWYŻEJ — linią kreskową (widok z dołu z usuwaniem linii zasłoniętych: obrysy wysuniętych płyt,
    wsporników, brył wyższych kondygnacji, otwory w stropie nad, belki) + opis „obrys … nad”,
  * schody z modelu: numeracja stopni, strzałka od kółka (początek) do grota, linia cięcia z zygzakiem, część nad
    płaszczyzną cięcia kreskowana, spoczniki z rzędną, opis „n × h × s”; balustrady (przecięte / poniżej / powyżej),
  * osie konstrukcyjne, 4 łańcuchy zewnętrzne na każdej stronie (R4 pkt 3.5), łańcuchy wewnętrzne (szerokości
    pomieszczeń i grubości ścian), symbole pomieszczeń (nr wg PN-B-01025, nazwa, pow., posadzka, rzędna),
    oznaczenia stolarki (symbol + szer./(parapet) wys.), znaki przekrojów, wejście, wyposażenie (wyposazenie.yaml).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, elements as E, symbols as S
from ..draft.geom import lines_of, perp, polygons_of, unit
from . import hlr
from .common import (NO_HATCH, Placer, ViewContext, clean, cut_kind, draw_lines, hatch_code,
                     label_point, material_name, room_label, spiral)

EXCL_BELOW = {"frame", "glass", "door_leaf", "railing", "lamella", "stair_step", "landing", "furniture"}
ABOVE_KINDS = {"slab", "roof", "canopy", "beam", "parapet", "terrace", "wall", "insulation", "column"}
CUT_OTHER = {"column", "beam", "parapet", "slab", "roof", "canopy", "terrace"}
SIDES = {"dol": (0.0, -1.0), "prawo": (1.0, 0.0), "gora": (0.0, 1.0), "lewo": (-1.0, 0.0)}


@dataclass
class PlanResult:
    kond: str | None
    z_cut: float | None
    hatches: list = field(default_factory=list)       # kody kreskowań użyte w przekroju (legenda)
    hatch_mats: dict = field(default_factory=dict)    # kod kreskowania → kody materiałów modelu
    rooms: list = field(default_factory=list)         # wiersze zestawienia pomieszczeń
    openings: list = field(default_factory=list)      # symbole stolarki na rzucie
    notes: list = field(default_factory=list)
    extent: tuple | None = None


def _pts_proj(pts, D):
    return [float(np.asarray(p) @ D) for p in pts]


def _uniq(vals, tol=1e-3):
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > tol:
            out.append(v)
    return out


# ================================================================================================ wymiary zewn.
def exterior_dims(vp, ctx: ViewContext, outline, walls=(), cut_extent=None, openings=True, columns=(),
                  struct=None, sides=("dol", "prawo", "gora", "lewo"), axes=True, placer: Placer | None = None):
    """Łańcuchy zewnętrzne (R4 pkt 3.5): 1 — otwory i filary (+ uskoki lica), 2 — osie otworów i ściany wewnętrzne
    dochodzące do ścian zewnętrznych, 3 — osie konstrukcyjne, 4 — wymiar całkowity. Zwraca {strona: odsunięcie
    zewnętrznej krawędzi opisu [m]} (dla osi i znaków przekrojów)."""
    m = ctx.model
    k = vp.k
    if outline is None or outline.is_empty:
        return {}
    ext = cut_extent or outline.bounds
    X0, Y0, X1, Y1 = ext
    ob = outline.bounds
    out = {}
    polys = polygons_of(outline)
    for side in sides:
        N = np.array(SIDES[side])
        D = np.array([1.0, 0.0]) if side in ("dol", "gora") else np.array([0.0, 1.0])
        lo, hi = (ob[0], ob[2]) if side in ("dol", "gora") else (ob[1], ob[3])
        # krawędzie obrysu zwrócone ku stronie
        edge_pts = []
        for pg in polys:
            c = np.asarray(pg.exterior.coords)
            if not pg.exterior.is_ccw:
                c = c[::-1]
            for a, b in zip(c[:-1], c[1:]):
                e = b - a
                L = math.hypot(*e)
                if L < 0.05:
                    continue
                nout = np.array([e[1], -e[0]]) / L
                if nout @ N > 0.9:
                    edge_pts += [a @ D, b @ D]
        facing = [w for w in walls if w.ext_side is not None and (w.n * w.ext_side) @ N > 0.9]
        op_edges, op_mid = [], []
        if openings:
            for w in facing:
                for o in w.otwory:
                    op_edges += [w.pt(o.s0, 0.0) @ D, w.pt(o.s1, 0.0) @ D]
                    op_mid.append(w.pt((o.s0 + o.s1) / 2, 0.0) @ D)
        inner = []
        if struct is not None:
            for w in facing:
                si = w.sgn_int
                tp = w.face_t(si, "k") + si * 0.04
                ln = LineString([tuple(w.pt(-0.6, tp)), tuple(w.pt(w.L + 0.6, tp))])
                own = unary_union([l.polygon for l in w.warstwy if l.konstrukcyjna and l.polygon is not None])
                g = ln.intersection(struct.difference(own.buffer(1e-4)))
                for a in lines_of(g):
                    if len(a) < 2:
                        continue
                    t0, t1 = sorted([float(a[0] @ D), float(a[-1] @ D)])
                    if t1 - t0 < 0.03:
                        continue
                    mid = (a[0] + a[-1]) / 2
                    v = _wall_at(walls, mid)
                    if v is not None and v.ext_side is not None:
                        dint = float((v.n * v.sgn_int) @ D)
                        inner.append(t1 if dint > 0 else t0)
                    else:
                        inner += [t0, t1]
        col_c = [float(np.asarray(c) @ D) for c in columns]
        chains = []
        c1 = _uniq(edge_pts + op_edges)
        if op_edges or len(_uniq(edge_pts)) > 2:
            chains.append(c1)
        c2 = _uniq(edge_pts + op_mid + inner + col_c)
        c2 = [v for v in c2 if lo - 3.0 <= v <= hi + 5.0]
        if len(c2) > 2 and c2 != c1 and (op_mid or inner or col_c):
            chains.append(c2)
        if axes:
            key = "x" if side in ("dol", "gora") else "y"
            ax = [float(v) for v in (m.osie.get(key) or {}).values()]
            ax = [v for v in ax if lo - 0.35 <= v <= hi + 0.35]
            if len(ax) >= 2:
                chains.append(_uniq(ax))
        chains.append([lo, hi])
        # położenie
        if side == "dol":
            base = Y0
        elif side == "gora":
            base = Y1
        elif side == "lewo":
            base = X0
        else:
            base = X1
        sg = 1.0 if side in ("prawo", "gora") else -1.0
        off = 10.0
        n0 = len(vp.prims)
        for i, ch in enumerate(chains):
            pos = base + sg * off * k
            if len(ch) < 2:
                continue
            if side in ("dol", "gora"):
                dims.dim_h(vp, ch, pos, base, mask=0.3)
            else:
                dims.dim_v(vp, ch, pos, base, mask=0.3)
            off += 7.0
        out[side] = base + sg * (off - 7.0 + 4.0) * k
        if placer is not None:
            placer.add_prims(vp.prims[n0:])
    return out


def _wall_at(walls, pt):
    P = Point(float(pt[0]), float(pt[1]))
    for w in walls:
        g = w.polygon
        if g is not None and not g.is_empty and g.buffer(0.01).contains(P):
            return w
    return None


def draw_axes(vp, ctx: ViewContext, extent, offs: dict, bounds, h_ext_mm: float = 3.0):
    """Osie konstrukcyjne (linia punktowa + kółka na obu końcach poza łańcuchami wymiarowymi)."""
    m = ctx.model
    k = vp.k
    X0, Y0, X1, Y1 = extent
    y_lo = offs.get("dol", Y0 - 12 * k) - h_ext_mm * k
    y_hi = offs.get("gora", Y1 + 12 * k) + h_ext_mm * k
    x_lo = offs.get("lewo", X0 - 12 * k) - h_ext_mm * k
    x_hi = offs.get("prawo", X1 + 12 * k) + h_ext_mm * k
    bx0, by0, bx1, by1 = bounds
    for name, x in (m.osie.get("x") or {}).items():
        if bx0 - 0.35 <= x <= bx1 + 0.35:
            S.axis_line(vp, (x, y_lo), (x, y_hi), str(name), "both")
    for name, y in (m.osie.get("y") or {}).items():
        if by0 - 0.35 <= y <= by1 + 0.35:
            S.axis_line(vp, (x_lo, y), (x_hi, y), str(name), "both")
    return (x_lo - 11 * k, y_lo - 11 * k, x_hi + 11 * k, y_hi + 11 * k)


def section_line(sec: dict, bounds, margin: float):
    """Punkty p1, p2 śladu płaszczyzny przekroju na rzucie (w granicach ``bounds`` + margines) i look (±1)."""
    o = np.asarray(sec["o"], float)
    R = np.asarray(sec["R"], float)
    L = np.asarray(sec["L"], float)
    x0, y0, x1, y1 = bounds
    corners = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    ss = (corners - o) @ R
    s0, s1 = ss.min() - margin, ss.max() + margin
    p1, p2 = o + R * s0, o + R * s1
    d = unit(p2 - p1)
    look = 1.0 if (perp(d) @ L) > 0 else -1.0
    return p1, p2, look


# ================================================================================================ rzut kondygnacji
class PlanBuilder:
    def __init__(self, vp, ctx: ViewContext, kid: str, opts: dict):
        self.vp = vp
        self.ctx = ctx
        self.m = ctx.model
        self.ir = ctx.ir
        self.kid = kid
        self.k = self.m.kondygnacja(kid)
        self.opts = opts
        self.h_cut = float(opts.get("wysokosc_ciecia", ctx.opt("wysokosc_ciecia", 1.10)))
        self.z_floor = self.k.rzedna
        self.z_cut = self.z_floor + self.h_cut
        ks = self.m.kondygnacje
        i = [x.id for x in ks].index(kid)
        self.k_next = ks[i + 1] if i + 1 < len(ks) else None
        self.k_prev = ks[i - 1] if i > 0 else None
        self.z_ceiling_lvl = self.k_next.rzedna if self.k_next else self.z_floor + self.k.wys_kondygnacji
        self.placer = Placer(vp.k)
        self.res = PlanResult(kid, self.z_cut)
        self.num_mode = ctx.opt("numeracja_pomieszczen", "iso")
        self.rooms = [r for r in self.m.pomieszczenia(kid) if r.polygon is not None and not r.polygon.is_empty]
        self._later_levels = []     # rzędne do opisania (spoczniki)
        self._stair_label = []      # opisy „n × h × s” do rozmieszczenia
        self.stair_areas = []       # obrysy widocznych schodów (przeszkody dla opisów)

    # ------------------------------------------------------------------ przebieg
    def run(self):
        self.cut()
        self.view_below()
        self.view_above()
        self.stairs()
        self.railings()
        self.lamellas()
        self.openings()
        self.furniture()
        self.entrance()
        self.annotate()
        return self.res

    # ------------------------------------------------------------------ elementy przecięte
    def cut(self):
        m, vp, z = self.m, self.vp, self.z_cut
        cs = E.CutSet()
        self._hm = {}
        self.cut_walls, self.cut_walls_k = [], []
        struct = []
        voids = []
        for w in m.sciany():
            lays = [l for l in w.warstwy if l.polygon is not None and not l.polygon.is_empty
                    and l.z0 - 1e-6 <= z <= l.z1 + 1e-6]
            if not lays:
                continue
            self.cut_walls.append(w)
            konstr_cut = w.z_od - 1e-6 <= z <= w.z_do + 1e-6
            if konstr_cut:
                self.cut_walls_k.append(w)
            for l in lays:
                hc = hatch_code(m, l.mat)
                kind = cut_kind(hc, l.klasa, l.konstrukcyjna, w.typ)
                cs.add(l.polygon, hc, kind, axis=(tuple(w.p1), tuple(w.p2)))
                self._hm.setdefault(hc, set()).add(l.mat)
                if l.konstrukcyjna:
                    struct.append(l.polygon)
            for o in w.otwory:
                if konstr_cut or o.z0 - 1e-6 <= z <= o.z1 + 1e-6:
                    voids.append(w.band(t0=w.t_min - 0.02, t1=w.t_max + 0.02, s0=o.s0, s1=o.s1))
        for v in voids:
            cs.cut_out(v)
        self.columns = []
        for p in self.ctx.building_prisms:
            if p.kind not in CUT_OTHER or p.meta.get("wall") or p.meta.get("opening"):
                continue
            if not (p.z0 - 1e-6 <= z <= p.z1 + 1e-6):
                continue
            hc = hatch_code(m, p.material)
            part = p.meta.get("part")
            if p.kind == "column":
                kind = "stal" if hc == "STAL" else "konstr"
                c = p.shape().centroid
                self.columns.append((c.x, c.y))
            elif p.kind == "beam" or part == "attyka" or part == "plyta":
                kind = "konstr"
            else:
                kind = cut_kind(hc, None, False)
            cs.add(p.shape(), hc, kind)
            self._hm.setdefault(hc, set()).add(p.material)
            if kind in ("konstr", "stal"):
                struct.append(p.shape())
        n0 = len(vp.prims)
        res = cs.draw(vp)
        self.hatch_prims = (n0, len(vp.prims))
        self.res.hatches = sorted({it.mat for it, _g in res if it.mat != NO_HATCH})
        self.res.hatch_mats = {hc: sorted(v) for hc, v in self._hm.items() if hc in self.res.hatches}
        self.cut_region = clean(unary_union([g for _it, g in res])) if res else Polygon()
        self.struct = clean(unary_union(struct)) if struct else Polygon()
        self.voids = unary_union(voids) if voids else Polygon()
        self.placer.add(self.cut_region, "area", 1.0)
        self.outline = self.m.obrys_kondygnacji(self.kid)

    # ------------------------------------------------------------------ widok w dół (cienko)
    def view_below(self):
        m, ctx = self.m, self.ctx
        excl_walls = {w.id for w in self.cut_walls}
        if self.k_prev is None:
            z_min = -50.0
        else:
            z_min = self.z_floor - float(self.opts.get("glebokosc_widoku", ctx.opt("glebokosc_widoku", 1.5)))
        terr = ctx.ir.terrain
        cands = []
        for p in ctx.building_prisms:
            if p.kind in EXCL_BELOW or p.meta.get("opening") or p.meta.get("wall") in excl_walls:
                continue
            if p.meta.get("group") == "fundamenty" or p.meta.get("part") == "sufit":
                continue
            if p.z1 > self.z_cut - 1e-6 or p.z1 < z_min:
                continue
            if terr is not None and self.k_prev is None:
                c = p.shape().representative_point()
                try:
                    if p.z1 < terr.height_at(c.x, c.y) - 0.05 and p.kind not in ("terrace", "slab"):
                        continue
                except Exception:
                    pass
            cands.append(p)
        groups = hlr.top_groups(cands, looking="down", key_fn=lambda p: (p.material, "x"))
        order = hlr.hidden_lines(groups, occluder=self.cut_region, tol=5e-4, min_len=0.01)
        allg = []
        for g in order:
            if g.lines is not None and not g.lines.is_empty:
                draw_lines(self.vp, g.lines, "A-WIDOK", pen="cienka", min_len=0.02)
                allg.append(g.lines)
        if allg:
            self.placer.add_lines(unary_union(allg), w=0.25)

    # ------------------------------------------------------------------ widok w górę (kreskowo)
    def view_above(self):
        ctx = self.ctx
        excl_walls = {w.id for w in self.cut_walls}
        cands = []
        depth = float(self.opts.get("wysokosc_widoku_nad", ctx.opt("wysokosc_widoku_nad", 100.0)))
        for p in ctx.building_prisms:
            if p.kind not in ABOVE_KINDS or p.meta.get("opening") or p.meta.get("wall") in excl_walls:
                continue
            if p.meta.get("part") in ("sufit", "posadzka"):
                continue
            if p.z0 < self.z_cut - 1e-6 or p.z0 > self.z_cut + depth:
                continue
            cands.append(p)

        def key(p):
            return (p.element if p.kind in ("slab", "roof", "canopy", "terrace", "beam", "parapet") else
                    f"bryła {p.level}", "x")
        groups = hlr.top_groups(cands, looking="up", key_fn=key)
        # zasłaniają: elementy przecięte i nadproża nad otworami (linie w świetle otworów pomijane)
        occ = unary_union([self.cut_region, self.voids]) if not self.voids.is_empty else self.cut_region
        order = hlr.hidden_lines(groups, occluder=occ, tol=5e-4, min_len=0.05)
        self.above_lines = {}
        allg = []
        ob = self.outline.buffer(0.05, join_style=2) if not self.outline.is_empty else None
        for g in order:
            if g.lines is None or g.lines.is_empty:
                continue
            ln = g.lines
            if str(g.material).startswith("bryła") and ob is not None:
                ln = ln.difference(ob)          # bryły wyższe — tylko poza obrysem kondygnacji (wsporniki)
                if ln.is_empty:
                    continue
            draw_lines(self.vp, ln, "A-NAD-CIECIEM", pen="cienka", lt="KRESKOWA", min_len=0.05)
            self.above_lines.setdefault(g.material, []).append(ln)
            allg.append(ln)
        if allg:
            self.placer.add_lines(unary_union(allg), w=0.15)

    # ------------------------------------------------------------------ schody
    def stairs(self):
        """Schody kondygnacji: wszystkie biegi „z” i „na” tę kondygnację razem — widok z góry z zasłanianiem
        (stopnie wyższe zasłaniają niższe, płyta stropu zasłania schody z kondygnacji niższej), część biegu nad
        płaszczyzną cięcia kreskowo tylko tam, gdzie pod nią nie widać biegu przychodzącego (schody nad schodami)."""
        m, vp, k = self.m, self.vp, self.vp.k
        from ..draft.dims import arrowhead
        from ..draft.geom import readable_angle
        items = []
        for sch in m.schody():
            zk, nk = str(sch.get("z_kond")), str(sch.get("na_kond"))
            if self.kid not in (zk, nk):
                continue
            try:
                z = m.kondygnacja(zk).rzedna
            except KeyError:
                continue
            h = float(sch["wys_stopnia"])
            g = float(sch["szer_stopnia"])
            steps, flights = [], []
            no = 0
            for bg in sch.get("biegi") or []:
                Sx = np.asarray(bg["start"], float)
                d = unit(np.asarray(bg["kierunek"], float))
                n = perp(d)
                b = float(bg.get("szer", 1.0))
                ns = int(bg.get("stopni", 0))
                for j in range(max(ns - 1, 0)):
                    no += 1
                    a0, a1 = Sx + d * j * g, Sx + d * (j + 1) * g
                    poly = Polygon([tuple(a0 - n * b / 2), tuple(a1 - n * b / 2), tuple(a1 + n * b / 2),
                                    tuple(a0 + n * b / 2)])
                    steps.append(dict(no=no, poly=poly, top=z + (j + 1) * h, fl=len(flights), j=j, a0=a0, a1=a1))
                flights.append(dict(S=Sx, d=d, n=n, b=b, ns=ns, E=Sx + d * max(ns - 1, 0) * g))
                z += ns * h
            landings = [(Polygon(sp["obrys"]), float(sp["rzedna"])) for sp in sch.get("spoczniki") or []
                        if sp.get("obrys")]
            starting = self.kid == zk
            for st in steps:
                st["state"] = "below" if (not starting or st["top"] <= self.z_cut + 1e-6) else "above"
            lands = [dict(poly=pg, rz=rz, state="below" if (not starting or rz <= self.z_cut + 1e-6) else "above")
                     for pg, rz in landings]
            items.append(dict(sch=sch, starting=starting, steps=steps, flights=flights, lands=lands,
                              landings=landings, g=g, h=h))
        if not items:
            return
        n0 = len(vp.prims)
        arriving = [it for it in items if not it["starting"]]
        slab = Polygon()
        z_slab = None
        if arriving and self.k_prev is not None:
            sl = [st for st in m.stropy() if str(st.get("nad")) == self.k_prev.id]
            if sl:
                slab = unary_union([Polygon(st["obrys"], st.get("otwory") or []) for st in sl])
                z_slab = max(float(st["wierzch"]) for st in sl)
        # --- widok z góry: stopnie, spoczniki, płyta — od najwyższych
        faces = []
        for it in items:
            for st in it["steps"]:
                if st["state"] == "below":
                    faces.append((st["top"], st["poly"], st))
            for ld in it["lands"]:
                if ld["state"] == "below":
                    faces.append((ld["rz"], ld["poly"], ld))
        if z_slab is not None and not slab.is_empty:
            faces.append((z_slab, slab, None))
        faces.sort(key=lambda f: -f[0])
        occ = self.cut_region
        for z, poly, ref in faces:
            if ref is not None:
                vis_line = poly.boundary.difference(occ.buffer(1e-4))
                draw_lines(vp, vis_line, "A-SCHODY", pen="cienka")
                ref["vis"] = poly.difference(occ)
            occ = occ.union(poly)
        below_vis = unary_union([st["vis"] for it in items for st in it["steps"] + it["lands"]
                                 if st.get("vis") is not None and not st["vis"].is_empty] or [Polygon()])
        arr_foot = unary_union([st["poly"] for it in arriving for st in it["steps"]] +
                               [pg for it in arriving for pg, _ in it["landings"]]) if arriving else Polygon()
        # --- część nad płaszczyzną cięcia (kreskowo), linia cięcia, numeracja, strzałki
        for it in items:
            g, flights, steps = it["g"], it["flights"], it["steps"]
            hide = self.cut_region.union(arr_foot.buffer(1e-3)) if it["starting"] and arriving else self.cut_region
            for st in steps:
                if st["state"] != "above":
                    continue
                vis_line = st["poly"].boundary.difference(hide.buffer(1e-4))
                if not vis_line.is_empty:
                    draw_lines(vp, vis_line, "A-SCHODY", pen="cienka", lt="KRESKOWA")
                    st["vis"] = st["poly"].difference(hide)
            for ld in it["lands"]:
                if ld["state"] == "above":
                    vis_line = ld["poly"].boundary.difference(hide.buffer(1e-4))
                    if not vis_line.is_empty:
                        draw_lines(vp, vis_line, "A-SCHODY", pen="cienka", lt="KRESKOWA")
                        ld["vis"] = ld["poly"].difference(hide)
            for ld in it["lands"]:
                va = ld.get("vis")
                if va is not None and va.area > 0.05:
                    self._later_levels.append((label_point(va), ld["rz"], ld["poly"]))
            if it["starting"]:
                for fi, fl in enumerate(flights):
                    fs = [s for s in steps if s["fl"] == fi]
                    tr = [i for i in range(1, len(fs)) if fs[i - 1]["state"] == "below" and fs[i]["state"] == "above"]
                    if not tr:
                        continue
                    st = fs[tr[0]]
                    Wv = fl["n"] * fl["b"] / 2
                    cs_ = (st["j"] + 0.5) * g
                    p0 = fl["S"] - Wv + fl["d"] * (cs_ - g * 0.55)
                    p1 = fl["S"] + Wv + fl["d"] * (cs_ + g * 0.55)
                    mm_ = (p0 + p1) / 2
                    dd = unit(p1 - p0)
                    zz = 1.2 * k
                    q = [p0 - dd * 1.0 * k, mm_ - dd * zz, mm_ + perp(dd) * zz * 1.3, mm_ - perp(dd) * zz * 1.3,
                         mm_ + dd * zz, p1 + dd * 1.0 * k]
                    vp.polyline(q, "A-SCHODY", pen="cienka")
            for st in steps:
                va = st.get("vis")
                if va is None or va.area < 0.25 * st["poly"].area:
                    continue
                fl = flights[st["fl"]]
                c = (st["a0"] + st["a1"]) / 2 + fl["n"] * fl["b"] * 0.30
                if not va.buffer(-0.02).contains(Point(c)):
                    continue
                ang = math.degrees(math.atan2(fl["d"][1], fl["d"][0]))
                vp.text(c, str(st["no"]), 1.8, readable_angle(ang - 90.0), "center", "middle", layer="A-SCHODY")
            # strzałka: kółko przy pierwszym stopniu, grot na końcu biegu (lub przy linii cięcia)
            path = []
            for fi, fl in enumerate(flights):
                a = fl["S"] + fl["d"] * g * 0.5
                if fi > 0:
                    prev = flights[fi - 1]
                    lc = self._landing_between(it["landings"], prev["E"], fl["S"])
                    if lc is not None:
                        m1 = prev["E"] + prev["d"] * float((lc - prev["E"]) @ prev["d"])
                        m2 = fl["S"] - fl["d"] * float((fl["S"] - lc) @ fl["d"])
                        path += [m1, m2]
                path += [a if fi == 0 else fl["S"], fl["E"]]
            if it["starting"]:
                cut_at = next((st for st in steps if st["state"] == "above"), None)
                if cut_at is not None:
                    fl = flights[cut_at["fl"]]
                    path = self._truncate_path(path, fl["S"] + fl["d"] * (cut_at["j"] + 0.35) * g)
            if len(path) >= 2:
                pl = LineString([tuple(p) for p in path])
                if it["starting"]:
                    vis = pl.difference(self.cut_region.buffer(1e-4))
                else:
                    upper = unary_union([s["poly"] for o in items if o["starting"] for s in o["steps"]
                                         if s["state"] == "below"] or [Polygon()])
                    vis = pl.difference(unary_union([self.cut_region, slab, upper]).buffer(1e-4))
                segs = [a for a in lines_of(vis) if len(a) >= 2]
                for a in segs:
                    vp.polyline(a, "A-SCHODY", pen="cienka")
                if segs and Point(tuple(path[0])).distance(LineString(segs[0])) < 1e-3:
                    vp.fill(Point(tuple(path[0])).buffer(0.9 * k, 16), "A-SCHODY", "#ffffff", z=19.5)
                    vp.circle(path[0], 0.9 * k, "A-SCHODY", pen="cienka", z=19.6)
                if segs:
                    last = segs[-1]
                    arrowhead(vp, last[-1], last[-1] - last[-2], 2.4, 12, True, "A-SCHODY")
                if it["starting"] or not any(o["starting"] for o in items):
                    self._stair_label.append((it["sch"], [np.asarray(p) for p in (segs[0] if segs else path)],
                                              it["starting"]))
        self.placer.add_prims(vp.prims[n0:], w_text=1.0, w_line=0.6)
        vis_foot = unary_union([below_vis] + [st["vis"] for it in items for st in it["steps"] + it["lands"]
                                              if st.get("vis") is not None])
        if not vis_foot.is_empty:
            self.placer.add(vis_foot, "area", 0.6)
            self.stair_areas.append(vis_foot)

    @staticmethod
    def _landing_between(landings, e, s):
        best = None
        for pg, _rz in landings:
            d = pg.distance(Point(tuple(e))) + pg.distance(Point(tuple(s)))
            if best is None or d < best[0]:
                best = (d, pg)
        if best is None or best[0] > 0.2:
            return None
        c = best[1].centroid
        return np.array([c.x, c.y])

    @staticmethod
    def _truncate_path(path, endp):
        pl = LineString([tuple(p) for p in path])
        t = pl.project(Point(tuple(endp)))
        out = [path[0]]
        acc = 0.0
        for a, b in zip(path[:-1], path[1:]):
            L = float(np.hypot(*(b - a)))
            if acc + L >= t:
                out.append(a + (b - a) * ((t - acc) / max(L, 1e-9)))
                return [np.asarray(p) for p in out]
            out.append(b)
            acc += L
        return [np.asarray(p) for p in out]

    # ------------------------------------------------------------------ balustrady
    def railings(self):
        vp = self.vp
        z = self.z_cut
        n0 = len(vp.prims)
        for bl in self.m.balustrady():
            pts = bl.get("polilinia")
            if not isinstance(pts, list) or len(pts) < 2:
                continue
            H = float(bl.get("wys", 1.1))
            for a, b in zip(pts[:-1], pts[1:]):
                A, B = np.asarray(a, float), np.asarray(b, float)
                if len(A) < 3:
                    continue
                cuts = sorted({0.0, 1.0} | {t for t in _param_at(A[2], B[2], (z - H, z)) if 0 < t < 1})
                for t0, t1 in zip(cuts[:-1], cuts[1:]):
                    P0, P1 = A + (B - A) * t0, A + (B - A) * t1
                    zm = (P0[2] + P1[2]) / 2
                    if zm <= z + 1e-6 <= zm + H + 1e-6 or (zm <= z <= zm + H):
                        st = "cut"
                    elif zm + H < z:
                        st = "below"
                    else:
                        st = "above"
                    if st == "above" and zm > self.z_ceiling_lvl - 0.3:
                        continue
                    if st == "below" and self.k_prev is not None and zm + H < self.z_floor - 1.5:
                        continue
                    ln = LineString([tuple(P0[:2]), tuple(P1[:2])]).difference(self.cut_region.buffer(1e-4))
                    if st == "cut":
                        draw_lines(vp, ln, "A-SCHODY", pen="srednia")
                    elif st == "below":
                        occ = self.cut_region
                        draw_lines(vp, ln.difference(occ), "A-SCHODY", pen="cienka")
                    else:
                        draw_lines(vp, ln, "A-SCHODY", pen="cienka", lt="KRESKOWA")
        self.placer.add_prims(vp.prims[n0:], w_line=0.5)

    # ------------------------------------------------------------------ lamele
    def lamellas(self):
        vp = self.vp
        n0 = len(vp.prims)
        for p in self.ctx.building_prisms:
            if p.kind != "lamella" or p.meta.get("part") == "rygiel":
                continue
            if p.z0 - 1e-6 <= self.z_cut <= p.z1 + 1e-6:
                vp.polygon(p.polygon, "A-SCIANY-KONSTR", pen="srednia")
        self.placer.add_prims(vp.prims[n0:], w_line=0.5)

    # ------------------------------------------------------------------ stolarka
    def openings(self):
        m, vp = self.m, self.vp
        n0 = len(vp.prims)
        self._op_tags = []
        for w in self.cut_walls:
            konstr_cut = w in self.cut_walls_k
            for o in w.otwory:
                if not (konstr_cut or o.z0 - 1e-6 <= self.z_cut <= o.z1 + 1e-6):
                    continue
                try:
                    self._opening(w, o)
                except Exception as ex:  # pragma: no cover - diagnostyka
                    self.ctx.note(f"rzut {self.kid}", f"otwór {o.id}: błąd rysowania ({ex})")
        self.placer.add_prims(vp.prims[n0:], w_text=1.0, w_line=0.6)

    def _swing_side(self, w, o) -> int:
        """Strona otwierania skrzydła jako znak normalnej ściany (+1 = strona +n)."""
        ow = o.otwieranie or {}
        kier = str(ow.get("kierunek", "do_wewn"))
        if w.ext_side is not None:
            s_in = w.sgn_int
            return s_in if kier != "na_zewn" else -s_in
        mid = (o.s0 + o.s1) / 2
        rp = self._room_at(w.pt(mid, w.t_max + 0.35))
        rm = self._room_at(w.pt(mid, w.t_min - 0.35))

        def score(r):
            if r is None:
                return (9, 9, 0.0)
            return (self._door_count(r), 1 if r.kategoria == "ruchu" else 0, r.pow_netto)
        # „do wnętrza” = do pomieszczenia „głębszego”: mniej drzwi (ślepe), nie komunikacja, mniejsze
        into = 1 if score(rp) <= score(rm) else -1
        return into if kier != "na_zewn" else -into

    def _door_count(self, r) -> int:
        if not hasattr(self, "_dc"):
            self._dc = {}
            for w in self.cut_walls_k:
                for o in w.otwory:
                    if o.typ not in ("drzwi", "otwor", "drzwi_zewn", "drzwi_przesuwne_HS"):
                        continue
                    mid = (o.s0 + o.s1) / 2
                    for t in (w.t_max + 0.35, w.t_min - 0.35):
                        rr = self._room_at(w.pt(mid, t))
                        if rr is not None:
                            self._dc[rr.id] = self._dc.get(rr.id, 0) + 1
        return self._dc.get(r.id, 0)

    def _room_at(self, pt):
        P = Point(float(pt[0]), float(pt[1]))
        for r in self.rooms:
            if r.polygon.buffer(0.02).contains(P):
                return r
        return None

    @staticmethod
    def _hinge(w, swing: int, strona: str) -> str:
        nsw = w.n * swing
        f = -nsw
        left = perp(f)
        on_b = (w.u @ left) > 0
        if strona == "prawa":
            on_b = not on_b
        return "b" if on_b else "a"

    def _panes(self, o):
        nk = o.raw.get("kwatery")
        if not isinstance(nk, (int, float)):
            pane = {"okno": 1.6, "fix": 3.0, "drzwi_przesuwne_HS": 3.0}.get(o.typ, 1.6)
            nk = max(2 if o.typ == "drzwi_przesuwne_HS" else 1, math.ceil((o.szer - 1e-6) / pane))
        return int(nk)

    def _opening(self, w, o):
        vp, k = self.vp, self.vp.k
        typ = o.typ
        si = w.sgn_int if w.ext_side is not None else 1
        t_in = w.face_t(si, "all")
        t_out = w.face_t(-si, "all")
        ta, tb = o.rama_t
        pa, pb = w.pt(o.s0, 0.0), w.pt(o.s1, 0.0)
        mid = (o.s0 + o.s1) / 2
        label_side = si
        if typ in ("okno", "fix"):
            fr = sorted([ta * si, tb * si])
            nk = self._panes(o)
            fw = {"fix": 0.055, "okno": 0.075}.get(typ, 0.075)
            inner = o.szer - 2 * fw
            pw = (inner - (nk - 1) * fw) / nk
            mull = [fw + i * (pw + fw) + pw + fw / 2 for i in range(nk - 1)]
            S.window(vp, pa, pb, t_in * si, t_out * si, fr[1], fr[0], side=si, glass=2,
                     sill_in=o.parapet > 0.3 and w.ext_side is not None, sill_out=o.parapet > 0.05 and w.ext_side is not None,
                     fixed_mullions=mull)
        elif typ == "drzwi_przesuwne_HS":
            ow = o.otwieranie or {}
            nsi = w.n * si
            left = perp(-nsi)
            moving_b = (w.u @ left) > 0
            if str(ow.get("strona", "lewa")) == "prawa":
                moving_b = not moving_b
            tc = (ta + tb) / 2
            S.sliding_door(vp, pa, pb, abs(t_in - t_out), side=si, kind="HS", fixed="a" if moving_b else "b",
                           frame_pos=tc * si, frame_depth=max(0.12, abs(tb - ta)), panels=self._panes(o))
        elif typ in ("drzwi", "drzwi_zewn"):
            ow = o.otwieranie or {}
            swing = self._swing_side(w, o)
            if w.ext_side is None:
                tc, wt = (w.t_min + w.t_max) / 2, w.t_max - w.t_min
            else:
                tc, wt = (ta + tb) / 2, abs(tb - ta)
            hinge = self._hinge(w, swing, str(ow.get("strona", "lewa")))
            leaves = int(ow.get("skrzydla", 2 if o.szer >= 1.5 else 1))
            A, B = w.pt(o.s0, tc), w.pt(o.s1, tc)
            S.door(vp, A, B, wt, side=float(swing), hinge=hinge, leaves=leaves, threshold=(typ == "drzwi_zewn"))
            if w.ext_side is None:
                label_side = -swing
            self._door_swings = getattr(self, "_door_swings", [])
        elif typ == "brama":
            tf = w.face_t(si, "k")
            t_frame = (ta + tb) / 2
            A, B = w.pt(o.s0, t_frame), w.pt(o.s1, t_frame)
            with vp.on("A-DRZWI"):
                vp.polygon([w.pt(o.s0 + 0.02, ta), w.pt(o.s1 - 0.02, ta), w.pt(o.s1 - 0.02, tb),
                            w.pt(o.s0 + 0.02, tb)], pen="srednia")
                depth = min(o.wys, 3.0)
                q = [w.pt(o.s0 + 0.05, tf), w.pt(o.s1 - 0.05, tf), w.pt(o.s1 - 0.05, tf + si * depth),
                     w.pt(o.s0 + 0.05, tf + si * depth)]
                vp.polygon(q, pen="cienka", lt="KRESKOWA")
        elif typ == "otwor":
            if o.z1 < w.z_do - 0.05:
                for t in (w.t_min, w.t_max):
                    vp.line(w.pt(o.s0, t), w.pt(o.s1, t), "A-NAD-CIECIEM", pen="cienka", lt="KRESKOWA")
        # oznaczenie (symbol + wymiar) — rozmieszczane później
        center = w.pt(mid, w.face_t(label_side, "all"))
        sill = o.parapet if (typ in ("okno", "fix") and o.parapet > 0.001) else None
        self._op_tags.append(dict(o=o, w=w, center=center, side=label_side, sill=sill))
        self.res.openings.append(o)

    # ------------------------------------------------------------------ wyposażenie
    def furniture(self):
        vp = self.vp
        n0 = len(vp.prims)
        for it in self.ctx.furniture:
            if str(it.get("kond")) != self.kid:
                continue
            try:
                draw_furniture(vp, it)
            except Exception as ex:
                self.ctx.note("wyposazenie.yaml", f"element {it}: {ex}")
        self.placer.add_prims(vp.prims[n0:], w_text=1.0, w_line=0.3)

    # ------------------------------------------------------------------ wejście
    def entrance(self):
        if self.k_prev is not None:
            return
        vp = self.vp
        for w in self.cut_walls_k:
            if w.ext_side is None:
                continue
            for o in w.otwory:
                if o.typ != "drzwi_zewn":
                    continue
                mid = (o.s0 + o.s1) / 2
                out = w.n * w.ext_side
                pos = w.pt(mid, w.face_t(w.ext_side, "all")) + out * 0.35
                ang = math.degrees(math.atan2(-out[1], -out[0]))
                n0 = len(vp.prims)
                S.entrance_arrow(vp, pos + (-out) * 0.0, ang, filled=o.z0 >= -0.01, size_mm=6.0)
                self.placer.add_prims(vp.prims[n0:])

    # ------------------------------------------------------------------ opisy
    def annotate(self):
        vp, k = self.vp, self.vp.k
        # wymiary zewnętrzne, osie — poza całym narysowanym obszarem (tarasy, płyty nad, słupy)
        ext = vp.extents() or (self.cut_region.bounds if not self.cut_region.is_empty else self.outline.bounds)
        walls_k = [w for w in self.cut_walls_k if w.kond == self.kid] or self.cut_walls_k
        cols = [c for c in self.columns if not self.outline.buffer(0.05).contains(Point(c))]
        offs = exterior_dims(vp, self.ctx, self.outline, walls_k, ext, openings=True, columns=cols,
                             struct=self.struct, placer=self.placer)
        ob = self.outline.bounds if not self.outline.is_empty else ext
        axb = draw_axes(vp, self.ctx, ext, offs, ob)
        self.placer.add(box(*axb).difference(box(*ext).buffer(6 * k)), "line", 0.1)
        # stolarka (położenie ograniczone do osi otworu) — przed opisami pomieszczeń
        self.opening_tags()
        # pomieszczenia
        self.room_tags()
        # schody — opis n × h × s
        self.stair_labels()
        # rzędne (spoczniki, tarasy)
        self.level_marks()
        # wymiary wewnętrzne
        if self.opts.get("wymiary_wewnetrzne", self.ctx.opt("wymiary_wewnetrzne", True)):
            self.interior_dims()
        # opisy linii „nad”
        self.above_labels()
        # znaki przekrojów
        self.section_marks(axb)
        self.res.extent = vp.extents()

    def room_tags(self):
        vp, k, m = self.vp, self.vp.k, self.m
        for r in sorted(self.rooms, key=lambda r: -r.pow_netto):
            pg = r.polygon
            num = room_label(m, r.id, self.num_mode)
            floor = material_name(m, str(r.posadzka)) if r.posadzka else None
            if floor and len(floor) > 28:
                floor = floor[:27].rstrip() + "…"
            lvl = float(r.raw.get("rzedna", self.k.rzedna)) if isinstance(r.raw.get("rzedna"), (int, float)) \
                else self.k.rzedna
            c = label_point(pg)
            cands = [p for p in spiral(c, 0.25, 6, 8) if pg.contains(Point(p))]
            if not cands:
                cands = [tuple(c)]
            bounds = pg.buffer(-0.03)
            variants = [dict(name=r.nazwa, area=r.pow_netto, floor=floor, level_z=lvl),
                        dict(name=r.nazwa, area=r.pow_netto, floor=None, level_z=lvl),
                        dict(name=r.nazwa, area=r.pow_netto, floor=None, level_z=None),
                        dict(name=None, area=r.pow_netto, floor=None, level_z=None),
                        dict(name=None, area=None, floor=None, level_z=None)]
            for vi, var in enumerate(variants):
                def fn(cv, pos, var=var):
                    S.room_tag(cv, pos, num, var["name"], var["area"], floor=var["floor"], level_z=var["level_z"],
                               h=2.5, h_num=3.5)
                last = vi == len(variants) - 1
                pos, cost = self.placer.place(vp, fn, cands, bounds=bounds, max_cost=None if last else 2.5,
                                              penalty_step=0.004)
                if pos is not None:
                    break
            self.res.rooms.append(dict(nr=num, id=r.id, nazwa=r.nazwa, pow=r.pow_netto, kategoria=r.kategoria,
                                       posadzka=material_name(m, str(r.posadzka)) if r.posadzka else "",
                                       wys=r.wysokosc))

    def opening_tags(self):
        vp = self.vp
        for t in self._op_tags:
            o, w = t["o"], t["w"]
            shape = "ellipse" if (o.symbol and len(str(o.symbol)) > 2) else "circle"
            width, height = o.szer, o.wys
            cands = [4.0, 8.0, 12.0, 16.0, 20.0, 26.0]

            def fn(cv, a, t=t, o=o, w=w, shape=shape):
                dims.opening_dim(cv, t["center"], w.u, width, height, t["sill"], side=float(t["side"]),
                                 symbol=str(o.symbol) if o.symbol else None, axis_mm=a, symbol_shape=shape,
                                 start_mm=1.0)
            self.placer.place(vp, fn, cands, penalty_step=0.3)

    def stair_labels(self):
        vp, k = self.vp, self.vp.k
        for sch, path, starting in self._stair_label:
            N = int(sch.get("liczba_stopni", 0))
            h = float(sch["wys_stopnia"])
            g = float(sch["szer_stopnia"])
            runs = [(f"{N} × ", 1.0, 0.0)] + dims.dim_runs(h, "cm") + [(" × ", 1.0, 0.0)] + dims.dim_runs(g, "cm")
            pl = LineString([tuple(p) for p in path])
            cands = []
            for f in (0.35, 0.5, 0.25, 0.65, 0.15, 0.8):
                P = np.asarray(pl.interpolate(f, normalized=True).coords[0])
                Q = np.asarray(pl.interpolate(min(1.0, f + 0.02), normalized=True).coords[0])
                d = unit(Q - P)
                for off in (0.7, -0.7 - 2.5, 3.5, -6.0):
                    cands.append((P, d, off))
            from ..draft.geom import readable_angle, dir_deg

            def fn(cv, c, runs=runs):
                P, d, off = c
                ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
                up = perp(dir_deg(ang))
                cv.text(P + up * off * k, None, 2.5, ang, "center", "baseline", runs=runs, mask=0.3, layer="A-SCHODY")
            self.placer.place(vp, fn, cands)

    def level_marks(self):
        vp, k = self.vp, self.vp.k
        items = list(self._later_levels)
        for t in self.m.tarasy():
            try:
                pg = Polygon(t["obrys"])
                rz = float(t["rzedna"])
            except Exception:
                continue
            if self.k_prev is None and rz < self.z_cut and pg.difference(self.cut_region).area > 0.3:
                items.append((label_point(pg), rz, pg))
        for c, rz, pg in items:
            cands = [p for p in spiral(c, 0.3, 4, 8) if pg.buffer(-0.02).contains(Point(p))] or [tuple(c)]

            def fn(cv, pos, rz=rz):
                dims.level_plan(cv, pos, rz, style="x")
            self.placer.place(vp, fn, cands)

    # ------------------------------------------------------------------ wymiary wewnętrzne
    def interior_dims(self):
        vp, k = self.vp, self.vp.k
        rooms = [r for r in self.rooms if r.polygon.area > 1.2]
        if not rooms or self.struct.is_empty:
            return
        S_ = self.struct
        X0, Y0, X1, Y1 = self.outline.bounds if not self.outline.is_empty else self.cut_region.bounds
        for axis in ("h", "v"):
            todo = {r.id: r for r in rooms}
            guard = 0
            while todo and guard < 12:
                guard += 1
                best = None
                for r in list(todo.values()):
                    x0, y0, x1, y1 = r.polygon.bounds
                    for f in (0.3, 0.22, 0.38, 0.62, 0.7, 0.78, 0.15, 0.85, 0.1, 0.9, 0.45, 0.55):
                        c = (y0 + f * (y1 - y0)) if axis == "h" else (x0 + f * (x1 - x0))
                        for only in (None, r):
                            ev = self._eval_line(axis, c, todo, [r] if only is not None else rooms, S_,
                                                 (X0, Y0, X1, Y1))
                            if ev is None:
                                continue
                            if best is None or ev["score"] > best["score"]:
                                best = ev
                if best is None or best["score"] <= -1.0:
                    break
                n0 = len(vp.prims)
                for ch in best["chains"]:
                    if axis == "h":
                        dims.dim_h(vp, ch, best["c"], best["c"] - 0.2, ext="short", mask=0.3)
                    else:
                        dims.dim_v(vp, ch, best["c"], best["c"] + 0.2, ext="short", mask=0.3)
                self.placer.add_prims(vp.prims[n0:], w_text=1.0, w_line=0.6)
                for rid in best["covered"]:
                    todo.pop(rid, None)

    def _eval_line(self, axis, c, todo, rooms, S_, ext):
        X0, Y0, X1, Y1 = ext
        if axis == "h":
            ln = LineString([(X0 - 1.0, c), (X1 + 1.0, c)])
            D = np.array([1.0, 0.0])
        else:
            ln = LineString([(c, Y0 - 1.0), (c, Y1 + 1.0)])
            D = np.array([0.0, 1.0])
        walls = []
        for a in lines_of(ln.intersection(S_)):
            if len(a) >= 2:
                t0, t1 = sorted([float(a[0] @ D), float(a[-1] @ D)])
                if t1 - t0 > 0.02:
                    walls.append((t0, t1))
        walls.sort()
        if len(walls) < 2:
            return None
        covered, runs = [], []
        for r in rooms:
            if r.id not in todo:
                continue
            g = ln.intersection(r.polygon)
            segs = [a for a in lines_of(g) if len(a) >= 2]
            if not segs:
                continue
            x0, y0, x1, y1 = r.polygon.bounds
            width = (x1 - x0) if axis == "h" else (y1 - y0)
            seglen = sum(LineString(a).length for a in segs)
            if seglen < 0.6 * width:
                continue
            # odległość linii od brzegów pomieszczenia (unikanie zbyt bliskiego prowadzenia przy ścianach)
            ta = min(float(a[0] @ D) for a in segs + [s[::-1] for s in segs])
            tb = max(float(a[-1] @ D) for a in segs + [s[::-1] for s in segs])
            left = [wl for wl in walls if wl[1] <= ta + 0.05]
            right = [wr for wr in walls if wr[0] >= tb - 0.05]
            if not left or not right:
                continue
            wl, wr = left[-1], right[0]
            if wr[0] - wl[1] < 0.4:
                continue
            covered.append(r.id)
            runs.append((wl, wr))
        if not covered:
            return None
        # łańcuchy: kolejne pomieszczenia dzielące ściany łączone
        runs.sort()
        chains = []
        for wl, wr in runs:
            pts = [wl[0], wl[1], wr[0], wr[1]]
            if chains and abs(chains[-1][-2] - wl[0]) < 1e-6:
                chains[-1] += [wr[0], wr[1]]
            else:
                chains.append(pts)
        # bez grubości ścian zewnętrznych na końcach (są w łańcuchach zewnętrznych) — zostaw lico wewn.
        out_ch = []
        for ch in chains:
            ch = list(ch)
            if self._is_ext_wall_interval(axis, c, ch[0], ch[1]):
                ch = ch[1:]
            if self._is_ext_wall_interval(axis, c, ch[-2], ch[-1]):
                ch = ch[:-1]
            if len(ch) >= 2:
                out_ch.append(ch)
        if not out_ch:
            return None
        vp = self.vp
        k = vp.k

        def fn(cv, _c):
            for ch in out_ch:
                if axis == "h":
                    dims.dim_h(cv, ch, c, c - 0.2, ext="short")
                else:
                    dims.dim_v(cv, ch, c, c + 0.2, ext="short")
        cost, _ = self.placer.trial_cost(vp, fn, None)
        # kara za przecięcie otworów drzwiowych/okiennych (linia przez otwór = zła szerokość)
        pen = 0.0
        if not self.voids.is_empty and ln.intersects(self.voids):
            pen += 2.5
        for sa in self.stair_areas:
            if ln.intersects(sa):
                pen += 1.0
        score = len(covered) * 4.0 - cost * 0.35 - pen
        return dict(score=score, c=c, chains=out_ch, covered=covered)

    def _is_ext_wall_interval(self, axis, c, t0, t1):
        mid = ((t0 + t1) / 2, c) if axis == "h" else (c, (t0 + t1) / 2)
        w = _wall_at(self.cut_walls_k, mid)
        return w is not None and w.ext_side is not None

    # ------------------------------------------------------------------ opisy linii nad płaszczyzną cięcia
    def above_labels(self):
        vp, k = self.vp, self.vp.k
        if not self.opts.get("opisy_nad", self.ctx.opt("opisy_nad", True)):
            return
        from ..draft.geom import readable_angle, dir_deg
        for elem, geoms in getattr(self, "above_lines", {}).items():
            g = unary_union(geoms)
            segs = []
            for a in lines_of(g):
                for p, q in zip(a[:-1], a[1:]):
                    L = float(np.hypot(*(q - p)))
                    if L > 1.2:
                        segs.append((L, p, q))
            if not segs:
                continue
            segs.sort(key=lambda t: -t[0])
            ob = self.outline.buffer(-0.02) if not self.outline.is_empty else None
            flags = [ob is not None and ob.contains(Point((s_[1] + s_[2]) / 2)) for s_ in segs]
            inside = [s_ for s_, f in zip(segs, flags) if f]
            outside = [s_ for s_, f in zip(segs, flags) if not f]
            if str(elem).startswith("bryła"):
                text, use = f"obrys {elem.replace('bryła ', 'bryły ')} nad", outside
            elif outside:
                text, use = f"obrys płyty {elem} nad", outside
            else:
                text, use = f"otwór w stropie {elem} nad", inside
            if not use:
                continue
            cands = []
            for L, p, q in use[:4]:
                d = unit(q - p)
                for f in (0.5, 0.3, 0.7):
                    P = p + (q - p) * f
                    for side in (1, -1):
                        cands.append((P, d, side))

            def fn(cv, cnd, text=text):
                P, d, side = cnd
                ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
                up = perp(dir_deg(ang))
                pos = P + up * (0.8 * k if side > 0 else -(0.8 + 1.8) * k)
                cv.text(pos, text, 1.8, ang, "center", "baseline", layer="A-OPISY", style="italic", mask=0.3)
            self.placer.place(vp, fn, cands, max_cost=2.0)

    # ------------------------------------------------------------------ przekroje
    def section_marks(self, axb):
        vp, k = self.vp, self.vp.k
        for sid, sec in self.ctx.sections.items():
            p1, p2, look = section_line(sec, axb, 3.0 * k)
            S.section_mark(vp, p1, p2, str(sec.get("litera", sid)), look=look)


def _param_at(za, zb, levels):
    out = []
    if abs(zb - za) < 1e-9:
        return out
    for z in levels:
        out.append((z - za) / (zb - za))
    return out


# ================================================================================================ wyposażenie
FURN = {
    "wc": ("wc_hung", ("w", "d")), "miska_wc": ("wc_hung", ("w", "d")),
    "umywalka": ("washbasin", ("w", "d")), "umywalka_blat": ("washbasin_counter", ("w", "d")),
    "wanna": ("bathtub", ("w", "d")), "prysznic": ("shower_walkin", ("w", "d")),
    "pralka": ("washing_machine", ("w", "d")), "suszarka": ("dryer", ("w", "d")),
    "zlew": ("kitchen_sink", ("w", "d")), "zlewozmywak": ("kitchen_sink", ("w", "d")),
    "plyta": ("hob", ("w", "d")), "plyta_grzewcza": ("hob", ("w", "d")),
    "lodowka": ("fridge", ("w", "d")), "zmywarka": ("dishwasher", ("w", "d")),
    "lozko": ("bed", ("w", "l")), "szafa": ("wardrobe", ("w", "d")), "sofa": ("sofa", ("w", "d")),
    "stol": ("table_chairs", ("w", "d")), "biurko": ("desk", ("w", "d")), "wyspa": ("kitchen_island", ("w", "d")),
    "urzadzenie": ("appliance", ("w", "d")), "pompa_ciepla": ("heat_pump", ("w", "d")),
    "zasobnik": ("tank", ("d",)), "rekuperator": ("recuperator", ("w", "d")),
}


def draw_furniture(vp, it: dict):
    """Element wyposażenia: {typ, xy, obrot (kierunek „od ściany do pomieszczenia” [°]), wym: [w, d], opis?}.
    Typ ``blat``: {linia: [[x,y],…], gl: 0.6, strona: 1|-1, gorne: bool} — blat wzdłuż lica ściany."""
    typ = str(it.get("typ", "")).lower()
    if typ == "blat":
        S.counter(vp, it["linia"], float(it.get("gl", 0.6)), float(it.get("strona", 1.0)),
                  upper=bool(it.get("gorne", False)))
        return
    if typ not in FURN:
        raise ValueError(f"nieznany typ wyposażenia '{typ}' (dostępne: {', '.join(sorted(FURN))}, blat)")
    fname, pnames = FURN[typ]
    fn = getattr(S, fname)
    kw = {}
    wym = it.get("wym")
    if isinstance(wym, dict):
        for p in pnames:
            if p in wym:
                kw[p] = float(wym[p])
    elif isinstance(wym, (list, tuple)):
        for p, v in zip(pnames, wym):
            kw[p] = float(v)
    if typ == "urzadzenie" and it.get("opis"):
        kw["label"] = str(it["opis"])
    pos = it.get("xy") or it.get("pos")
    rot = float(it.get("obrot", 90.0))
    if fname in ("table_chairs", "kitchen_island"):
        if "krzesla" in it:
            kw["chairs"] = int(it["krzesla"])
        fn(vp, pos, rot - 90.0, **kw)
    elif fname == "tank":
        fn(vp, pos, **kw)
    else:
        fn(vp, pos, rot, **kw)


def draw_plan(vp, ctx: ViewContext, kond: str, opts: dict | None = None) -> PlanResult:
    """Rysuje rzut kondygnacji ``kond`` do rzutni ``vp`` (metry modelu). Zwraca ``PlanResult``."""
    return PlanBuilder(vp, ctx, kond, dict(opts or {})).run()


# ================================================================================================ rzut dachu
def draw_roof_plan(vp, ctx: ViewContext, opts: dict | None = None) -> PlanResult:
    """Rzut dachu: widok z góry całego budynku z usuwaniem linii niewidocznych, spadki do wpustów, wpusty,
    rzędne pokrycia i attyk, osie, wymiary obrysu, znaki przekrojów."""
    opts = dict(opts or {})
    m, vp, k = ctx.model, vp, vp.k
    res = PlanResult(None, None)
    placer = Placer(k)
    prisms = [p for p in ctx.building_prisms if p.kind not in ("furniture",) and p.meta.get("group") != "fundamenty"]
    groups = hlr.top_groups(prisms, looking="down", key_fn=lambda p: (p.material, p.kind if p.kind in (
        "roof", "parapet", "canopy", "terrace") else "x"))
    order = hlr.hidden_lines(groups, occluder=None, tol=5e-4, min_len=0.01)
    allg = []
    for g in order:
        if g.lines is None or g.lines.is_empty:
            continue
        pen = "srednia" if g.kind in ("parapet",) or g.material == "OBROBKA_BLACH" else "cienka"
        draw_lines(vp, g.lines, "A-WIDOK", pen=pen, min_len=0.01)
        allg.append(g.lines)
    if allg:
        placer.add_lines(unary_union(allg), w=0.3)
    walls_out = unary_union([m.obrys_kondygnacji(kk.id) for kk in m.kondygnacje])
    parts = [walls_out]
    for d in list(m.dachy()) + list(m.wsporniki()):
        try:
            parts.append(Polygon(d["obrys"]))
        except Exception:
            pass
    foot = clean(unary_union(parts))
    outline = clean(unary_union([Polygon(pg.exterior) for pg in polygons_of(foot)])) if not foot.is_empty else Polygon()
    # lica ścian kondygnacji zasłonięte dachem / wyższą bryłą — linią kreskową
    if allg:
        visb = unary_union(allg).buffer(0.03)
        hid = unary_union([m.obrys_kondygnacji(kk.id).boundary for kk in m.kondygnacje]).difference(visb)
        draw_lines(vp, hid, "A-NIEWIDOCZNE", pen="cienka", lt="KRESKOWA", min_len=0.1)
    # spadki i wpusty
    for d in m.dachy():
        try:
            poly = Polygon(d["obrys"])
        except Exception:
            continue
        at = d.get("attyka") if isinstance(d.get("attyka"), dict) else None
        inner = poly.buffer(-(float(at.get("szer", 0.25)) if at else 0.0), join_style=2)
        pz = m.przegroda(str(d.get("przegroda")))
        top = float(d["plyta"]["wierzch"]) + (pz.d_nad_konstr() if pz is not None else 0.0)
        sp = d.get("spadek")
        drains = [np.asarray(p.get("xy") if isinstance(p, dict) else p, float) for p in (d.get("wpusty") or [])]   # SCHEMAT p. 6
        spouts = [np.asarray(p, float) for p in (d.get("rzygacze") or [])]
        n0 = len(vp.prims)
        for pt in drains:
            S.floor_drain(vp, pt, 0.2, layer="A-SYMBOLE", label="WD")
        placer.add_prims(vp.prims[n0:])
        targets = drains or spouts
        if sp and targets and not inner.is_empty:
            x0, y0, x1, y1 = inner.bounds
            for T in targets:
                for far in ((x0, T[1]), (x1, T[1]), (T[0], y0), (T[0], y1)):
                    far = np.asarray(far, float)
                    L = float(np.hypot(*(far - T)))
                    if L < 1.2:
                        continue
                    a = T + (far - T) * 0.75
                    b = T + (far - T) * 0.25
                    if not (inner.contains(Point(a)) and inner.contains(Point(b))):
                        continue
                    n0 = len(vp.prims)
                    dims.slope(vp, a, b, float(sp) * 100.0)
                    placer.add_prims(vp.prims[n0:])
        # rzędna pokrycia i opis dachu
        if not inner.is_empty:
            c = label_point(inner)
            cands = spiral(c, 0.4, 5, 8)
            text = [f"DACH {d.get('id', '')}", (pz.nazwa if pz is not None else "")]
            # opcja ``opis_dachu_szer`` [mm na papierze]: opis przegrody zawijany do szerokości pola dachu (bez niej —
            # jeden wiersz, jak dotąd; podkład rzutu dachu instalacji wywołuje bez opcji)
            szer = opts.get("opis_dachu_szer")
            if szer and text[1]:
                from ..draft.sheet import wrap as _wrap
                bx0, _by0, bx1, _by1 = inner.bounds
                ww = max(40.0, min(float(szer), (bx1 - bx0) / k - 8.0))
                rows = _wrap(text[1], ww, 2.5)
            else:
                rows = [text[1]] if text[1] else []

            def fn(cv, pos, text=text, top=top, rows=rows):
                cv.text(pos, text[0], 3.5, 0.0, "center", "baseline", layer="A-OPISY", style="bold", mask=0.4)
                for j, s in enumerate(rows):
                    cv.text((pos[0], pos[1] - (4.2 + 3.4 * j) * k), s, 2.5, 0.0, "center", "baseline",
                            layer="A-OPISY", mask=0.4)
                dy = 9.5 + 3.4 * max(0, len(rows) - 1)
                dims.level_plan(cv, (pos[0] - 6.0 * k, pos[1] - dy * k), top, style="x")
            placer.place(vp, fn, [p for p in cands if inner.buffer(-0.1).contains(Point(p))] or [tuple(c)])
        if at:
            zat = top + float(at.get("wys_nad_pokryciem", 0.3))
            ring = LineString(list(poly.exterior.coords))
            cands = []
            for f in np.linspace(0.05, 0.95, 10):
                P = np.asarray(ring.interpolate(f, normalized=True).coords[0])
                cands.append(tuple(P))

            def fn2(cv, pos, zat=zat):
                dims.level_plan(cv, pos, zat, style="x")
            placer.place(vp, fn2, cands)
    # rzędne wierzchów płyt wspornikowych (balkony, okapy)
    for w in m.wsporniki():
        try:
            pg = Polygon(w["obrys"])
        except Exception:
            continue
        c = label_point(pg)

        def fn3(cv, pos, z=float(w["wierzch"])):
            dims.level_plan(cv, pos, z, style="x")
        placer.place(vp, fn3, [p for p in spiral(c, 0.3, 4, 8) if pg.contains(Point(p))] or [tuple(c)])
    # wymiary i osie — poza całym narysowanym obszarem
    ext = vp.extents() or (outline.bounds if not outline.is_empty else m.bbox())
    offs = exterior_dims(vp, ctx, outline, [], ext, openings=False, placer=placer)
    axb = draw_axes(vp, ctx, ext, offs, walls_out.bounds if not walls_out.is_empty else ext)
    for sid, sec in ctx.sections.items():
        p1, p2, look = section_line(sec, axb, 3.0 * k)
        S.section_mark(vp, p1, p2, str(sec.get("litera", sid)), look=look)
    res.extent = vp.extents()
    return res
