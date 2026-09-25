"""PRZEKRÓJ PIONOWY budynku wzdłuż dowolnej linii (w tym prostopadłej do osi x/y) z kierunkiem patrzenia.

* elementy PRZECIĘTE — przecięcie pryzm IR (ściany warstwami, stropy, dachy z warstwami, posadzki, fundamenty,
  płyty wspornikowe, attyki, schody, spoczniki, słupy, belki, stolarka) z płaszczyzną: prostokąty (s, z) kreskowane
  wg materiałów (PN-B-01030 + oznaczenia przyjęte), kontury wg rodzaju warstwy; teren — grunt rodzimy pod linią
  terenu i pod warstwami podłogi na gruncie,
* elementy WIDOCZNE za płaszczyzną — rzut prostokątny z usuwaniem linii niewidocznych (``hlr``), linią cienką,
* opisy: rzędne (poziomy kondygnacji, wierzch stropów, pokrycie, attyki, teren, spód fundamentów; ±0,000 z rzędną
  bezwzględną), łańcuchy wysokości (szczegółowy: posadzki / okna / spody stropów; kondygnacje; całkowity),
  wysokości w świetle pomieszczeń, opis warstw przegród („drabinka” z kodem przegrody z modelu, materiały
  i grubości w cm), osie konstrukcyjne, numery i nazwy pomieszczeń, wysokość budynku wg § 6 WT.

Definicja przekroju (``arkusze.yaml → przekroje``):
  {id: A, x: 0.6, patrz: E}              — płaszczyzna x = 0,6 (prostopadła do osi x), patrzymy na wschód (+x),
  {id: B, y: 4.0, patrz: N}              — płaszczyzna y = 4,0, patrzymy na północ (+y),
  {id: C, linia: [[x1,y1],[x2,y2]], patrz: lewo|prawo|N|S|E|W|[dx,dy]}  — dowolna linia.
Kierunki N/S/E/W w układzie budynku (N = +y, E = +x).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, elements as E, fmt, symbols as S
from ..draft.geom import lines_of, perp, unit
from . import hlr
from .common import (NO_HATCH, Placer, ViewContext, clean, cut_kind, draw_lines, hatch_code, klasa_mat,
                     layer_text, material_name, room_label)

DIRS = {"N": (0.0, 1.0), "S": (0.0, -1.0), "E": (1.0, 0.0), "W": (-1.0, 0.0),
        "PN": (0.0, 1.0), "PD": (0.0, -1.0), "WSCH": (1.0, 0.0), "ZACH": (-1.0, 0.0)}
SEC_EXCL = {"furniture"}


@dataclass
class SectionResult:
    sec: dict
    hatches: list = field(default_factory=list)
    hatch_mats: dict = field(default_factory=dict)
    height: dict = field(default_factory=dict)
    extent: tuple | None = None
    notes: list = field(default_factory=list)


# ================================================================================================ definicje
def normalize_section(d: dict, model=None) -> dict:
    sid = str(d.get("id") or d.get("litera") or "A")
    look = d.get("patrz", d.get("kierunek"))
    if "linia" in d:
        p1, p2 = np.asarray(d["linia"][0], float), np.asarray(d["linia"][1], float)
        o, t = p1, unit(p2 - p1)
    elif "x" in d:
        o, t = np.array([float(d["x"]), 0.0]), np.array([0.0, 1.0])
    elif "y" in d:
        o, t = np.array([0.0, float(d["y"])]), np.array([1.0, 0.0])
    else:
        raise ValueError(f"przekrój {sid}: podaj 'x', 'y' albo 'linia'")
    if isinstance(look, (list, tuple)):
        L = unit(np.asarray(look, float))
    elif isinstance(look, str) and look.lower() in ("lewo", "l"):
        L = perp(t)
    elif isinstance(look, str) and look.lower() in ("prawo", "p"):
        L = -perp(t)
    elif isinstance(look, str) and look.upper() in DIRS:
        L = np.asarray(DIRS[look.upper()], float)
    else:
        L = perp(t)
    L = L - t * float(L @ t)
    if np.hypot(*L) < 1e-6:
        raise ValueError(f"przekrój {sid}: kierunek patrzenia równoległy do linii przekroju")
    L = unit(L)
    R = np.array([L[1], -L[0]])
    o = o + L * 0.0007          # odsunięcie od lic zbiegających się z płaszczyzną (brak przecięć stycznych)
    return dict(id=sid, litera=str(d.get("litera", sid)), o=o, L=L, R=R, t=t,
                nazwa=str(d.get("nazwa") or f"PRZEKRÓJ {sid}-{sid}"), glebokosc=d.get("glebokosc"),
                raw=dict(d))


def auto_sections(model) -> list[dict]:
    """Domyślne przekroje: A-A wzdłuż pierwszego biegu schodów (przez schody i stropy), B-B prostopadle przez
    środek budynku. Kierunek patrzenia — ku większej części budynku."""
    out = []
    try:
        ob = unary_union([model.obrys_kondygnacji(k.id) for k in model.kondygnacje])
        c = ob.centroid
        cx, cy = c.x, c.y
        x0, y0, x1, y1 = ob.bounds
    except Exception:
        x0, y0, x1, y1 = model.bbox()
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    sch = model.schody()
    if sch and (sch[0].get("biegi") or []):
        bg = sch[0]["biegi"][0]
        S0 = np.asarray(bg["start"], float)
        d = unit(np.asarray(bg["kierunek"], float))
        if abs(d[0]) < abs(d[1]):
            look = "E" if cx > S0[0] else "W"
            out.append(dict(id="A", x=round(float(S0[0]), 3), patrz=look))
            out.append(dict(id="B", y=round(_free_coord(model, "y", cy, (y0, y1)), 3), patrz="N"))
        else:
            look = "N" if cy > S0[1] else "S"
            out.append(dict(id="A", y=round(float(S0[1]), 3), patrz=look))
            out.append(dict(id="B", x=round(_free_coord(model, "x", cx, (x0, x1)), 3), patrz="E"))
    else:
        out.append(dict(id="A", x=round(_free_coord(model, "x", cx, (x0, x1)), 3), patrz="E"))
        out.append(dict(id="B", y=round(_free_coord(model, "y", cy, (y0, y1)), 3), patrz="N"))
    return out


def _free_coord(model, axis, c, rng):
    """Współrzędna blisko ``c`` nieleżąca w ścianie równoległej do płaszczyzny (unikanie cięcia wzdłuż muru)."""
    walls = unary_union([w.polygon for w in model.sciany() if w.polygon is not None])
    lo, hi = rng
    best = c
    for dv in [0.0] + [s * i * 0.15 for i in range(1, 20) for s in (1, -1)]:
        v = c + dv
        if not (lo + 0.5 < v < hi - 0.5):
            continue
        ln = LineString([(v, lo - 1), (v, hi + 1)]) if axis == "x" else LineString([(lo - 1, v), (hi + 1, v)])
        inter = ln.intersection(walls)
        mx = max((LineString(a).length for a in lines_of(inter) if len(a) >= 2), default=0.0)
        if mx < 0.8:
            return v
        best = v
    return best


# ================================================================================================ teren, wysokość
def terrain_profile(ctx: ViewContext, o, R, s0: float, s1: float, step: float = 0.25, L=None, depth: float = 0.0):
    """Profil terenu [(s, z)] wzdłuż linii o + R·s (+ L·depth). Bez działki — poziom −0,30 m."""
    terr = ctx.ir.terrain
    ss = np.arange(s0, s1 + step * 0.5, step)
    pts = np.asarray(o)[None, :] + np.outer(ss, R)
    if L is not None and depth:
        pts = pts + np.asarray(L) * depth
    if terr is None or terr.height_fn is None:
        zs = np.full(len(ss), -0.30)
    else:
        zs = np.asarray(terr.height_fn(pts), float)
        zs = np.where(np.isfinite(zs), zs, -0.30)
    return np.column_stack([ss, zs])


def building_height(ctx: ViewContext) -> dict:
    """Wysokość budynku wg § 6 WT — JEDNO ŹRÓDŁO: ``lamela.wskazniki.wskazniki()["wysokosc_WT6"]`` (wydanie, weryfikacja V1-03;
    K-3). Gdy moduł nie zwróci wartości (model bez działki) — metoda zastępcza: teren IR przy najniżej położonym wejściu do
    wierzchu najwyżej położonego stropodachu (bez attyk)."""
    m = ctx.model
    try:
        from ..wskazniki import wskazniki
        w6 = wskazniki(m).get("wysokosc_WT6") or {}
        if w6.get("wartosc") is not None and w6.get("H_teren") is not None:
            z0 = float(((m.raw or {}).get("uklad") or {}).get("zero_abs", 0.0))
            z_att = max([float(sl.get("top_attyki") or sl["top"]) for sl in m.plyty() if sl["typ"] == "dach"]
                        or [float(w6["z_top"])])
            return dict(z_ent=float(w6["H_teren"]) - z0, wejscie=w6.get("wejscie"), z_top=float(w6["z_top"]),
                        dach=w6.get("dach"), H=float(w6["wartosc"]), z_attyka=z_att, zrodlo="lamela.wskazniki")
    except Exception:  # noqa: BLE001 — metoda zastępcza poniżej
        pass
    terr = ctx.ir.terrain
    ent = []
    k0 = m.kondygnacje[0].id if m.kondygnacje else None
    for o in m.otwory():
        if o.typ not in ("drzwi_zewn",) or o.kond != k0:
            continue
        w = o.sciana
        es = w.ext_side if w.ext_side is not None else 1
        p = w.pt((o.s0 + o.s1) / 2, w.face_t(es, "all") + es * 0.6)
        z = terr.height_at(p[0], p[1]) if terr is not None else -0.30
        ent.append((float(z), o.id))
    if not ent:
        for o in m.otwory():
            if o.typ in ("drzwi_przesuwne_HS", "drzwi") and o.kond == k0 and o.sciana.ext_side is not None:
                w = o.sciana
                p = w.pt((o.s0 + o.s1) / 2, w.face_t(w.ext_side, "all") + w.ext_side * 0.6)
                z = terr.height_at(p[0], p[1]) if terr is not None else -0.30
                ent.append((float(z), o.id))
    z_ent, eid = min(ent) if ent else (-0.30, None)
    tops = []
    for sl in m.plyty():
        if sl["typ"] == "dach":
            tops.append((float(sl["top"]), sl["id"]))
    if not tops:
        b = ctx.ir.bounds(groups=tuple(k.id for k in m.kondygnacje) + ("dach",))
        tops = [(b[5], "?")]
    z_top, rid = max(tops)
    z_att = max([float(sl.get("top_attyki") or sl["top"]) for sl in m.plyty() if sl["typ"] == "dach"] or [z_top])
    return dict(z_ent=z_ent, wejscie=eid, z_top=z_top, dach=rid, H=z_top - z_ent, z_attyka=z_att)


# ================================================================================================ rysowanie
def _cut_kind_for(ctx: ViewContext, p, hc: str) -> str:
    m = ctx.model
    part = p.meta.get("part")
    kind = p.kind
    if kind in ("wall", "insulation"):
        if p.meta.get("opening"):
            return "wyk"
        wid = p.meta.get("wall")
        if part == "sciana_fundamentowa":
            return "konstr"
        if part == "izolacja_fundamentu":
            return "izol"
        w = m.sciana(wid) if wid else None
        kl = p.meta.get("klasa") or klasa_mat(m, p.material)
        return cut_kind(hc, kl, kl == "konstrukcja", w.typ if w else None)
    if kind == "footing":
        return "fund"
    if kind in ("slab", "roof", "canopy", "terrace"):
        if part == "plyta":
            return "strop"
        if part in ("sufit", "podsufitka"):
            return "wyk"
        return cut_kind(hc, klasa_mat(m, p.material), False)
    if kind == "parapet":
        if part == "attyka":
            return "konstr"
        if part in ("obrobka", "pas_czolowy"):
            return "stal"
        return "wyk"
    if kind in ("column",):
        return "stal" if hc == "STAL" else "konstr"
    if kind in ("beam", "stair_step", "landing"):
        return "konstr"
    if kind == "frame":
        return "stal" if hc == "STAL" else "warstwa"
    if kind in ("glass", "door_leaf", "railing", "lamella"):
        return "stal" if hc == "STAL" else "warstwa"
    return cut_kind(hc, None, False)


class SectionBuilder:
    def __init__(self, vp, ctx: ViewContext, sec: dict, opts: dict):
        self.vp, self.ctx, self.sec, self.opts = vp, ctx, sec, opts
        self.m = ctx.model
        self.o, self.L, self.R = sec["o"], sec["L"], sec["R"]
        self.placer = Placer(vp.k)
        self.res = SectionResult(sec)
        self.num_mode = ctx.opt("numeracja_pomieszczen", "iso")

    def s_of(self, p):
        return float((np.asarray(p, float) - self.o) @ self.R)

    def run(self):
        self.cut()
        self.beyond()
        self.terrain_line()
        self.annotate()
        self.res.extent = self.vp.extents()
        return self.res

    # ------------------------------------------------------------------ przecięcie
    def cut(self):
        m, vp = self.m, self.vp
        o, R = self.o, self.R
        line = LineString([tuple(o - R * 1e3), tuple(o + R * 1e3)])
        cs = E.CutSet()
        self.items = []
        prisms = [p for p in self.ctx.building_prisms if p.kind not in SEC_EXCL]
        self.prisms = prisms
        for p in prisms:
            g = p.shape()
            if not g.intersects(line):
                continue
            inter = g.intersection(line)
            for a in lines_of(inter):
                if len(a) < 2:
                    continue
                sa, sb = sorted([self.s_of(a[0]), self.s_of(a[-1])])
                if sb - sa < 1e-4:
                    continue
                hc = hatch_code(m, p.material)
                if hc == "DREWNO_POPRZ" and (p.z1 - p.z0) > 4.0 * (sb - sa):
                    hc = "DREWNO_WZDL"
                kind = _cut_kind_for(self.ctx, p, hc)
                rect = box(sa, p.z0, sb, p.z1)
                horiz = (sb - sa) >= (p.z1 - p.z0)
                zm, sm = (p.z0 + p.z1) / 2, (sa + sb) / 2
                axis = ((sa, zm), (sb, zm)) if horiz else ((sm, p.z0), (sm, p.z1))
                cs.add(rect, hc, kind, axis=axis)
                self.items.append(dict(p=p, s0=sa, s1=sb, z0=p.z0, z1=p.z1, hc=hc, kind=kind, elem=p.element))
        if not self.items:
            self.ctx.note(f"przekrój {self.sec['id']}", "płaszczyzna nie przecina budynku")
        bb = [(it["s0"], it["z0"], it["s1"], it["z1"]) for it in self.items] or [(0, 0, 1, 1)]
        self.s_min = min(b[0] for b in bb)
        self.s_max = max(b[2] for b in bb)
        self.z_min = min(b[1] for b in bb)
        self.z_max = max(b[3] for b in bb)
        # grunt
        marg = float(self.opts.get("margines_terenu", 1.5))
        prof = terrain_profile(self.ctx, o, R, self.s_min - marg, self.s_max + marg)
        self.profile = prof
        z_bot = min(self.z_min, float(prof[:, 1].min())) - 0.45
        gpoly = Polygon([(prof[0, 0], z_bot)] + [tuple(p) for p in prof] + [(prof[-1, 0], z_bot)])
        self.ground = gpoly.buffer(0)
        cs.add(self.ground, "GRUNT_RODZIMY", "grunt", priority=5, outline=False)
        n0 = len(vp.prims)
        res = cs.draw(vp)
        self.res.hatches = sorted({it.mat for it, _g in res if it.mat != NO_HATCH})
        hm = {}
        for it in self.items:
            hm.setdefault(it["hc"], set()).add(it["p"].material)
        hm.setdefault("GRUNT_RODZIMY", set()).add("GRUNT")
        self.res.hatch_mats = {hc: sorted(v) for hc, v in hm.items() if hc in self.res.hatches}
        self.cut_region = clean(unary_union([g for it, g in res if it.kind != "grunt"]))
        self.ground_vis = clean(unary_union([g for it, g in res if it.kind == "grunt"]))
        self.placer.add(self.cut_region, "area", 1.0)

    # ------------------------------------------------------------------ widok za płaszczyzną
    def beyond(self):
        dep = self.sec.get("glebokosc") or self.opts.get("glebokosc")
        prisms = [p for p in self.prisms if p.meta.get("group") != "fundamenty"]
        groups = hlr.side_groups(prisms, self.o, self.L, depth_min=0.0, depth_max=float(dep) if dep else None,
                                 key_fn=lambda p: (p.material, _cls(p)))
        occ = unary_union([self.cut_region, self.ground])
        order = hlr.hidden_lines(groups, occluder=occ, tol=4e-4, min_len=0.01)
        allg = []
        for g in order:
            if g.lines is None or g.lines.is_empty:
                continue
            pen = "b_cienka" if g.material in ("SZKLO", "SZKLO_BAL") else "cienka"
            draw_lines(self.vp, g.lines, "A-WIDOK", pen=pen, min_len=0.01)
            allg.append(g.lines)
        self.bx = [self.s_min, self.z_min, self.s_max, self.z_max]
        if allg:
            U = unary_union(allg)
            self.placer.add_lines(U, w=0.2)
            b = U.bounds
            self.bx = [min(self.s_min, b[0]), min(self.z_min, b[1]), max(self.s_max, b[2]), max(self.z_max, b[3])]

    def terrain_line(self):
        prof = self.profile
        ln = LineString([tuple(p) for p in prof])
        vis = ln.difference(self.cut_region.buffer(1e-3))
        draw_lines(self.vp, vis, "A-TEREN", pen="b_gruba", min_len=0.02)
        self.placer.add_lines(vis, w=0.8, buf_mm=0.8)

    # ------------------------------------------------------------------ opisy
    def annotate(self):
        vp, k, m = self.vp, self.vp.k, self.m
        H = building_height(self.ctx)
        self.res.height = H
        ext = vp.extents()
        X0, Y0, X1, Y1 = ext
        # rzędne — kolumna po prawej
        items = []
        zero_abs = m.zero_abs
        items.append((0.0, "zero", zero_abs))
        for kk in m.kondygnacje:
            if abs(kk.rzedna) > 1e-4 and self._storey_cut(kk):
                items.append((kk.rzedna, "wyk"))
        for sl in m.plyty():
            if not self._elem_cut(sl["id"]):
                continue
            if sl["typ"] == "dach":
                items.append((float(sl["top"]), "wyk"))
                if sl.get("top_attyki"):
                    items.append((float(sl["top_attyki"]), "wyk"))
                items.append((float(sl["wierzch"]), "konstr"))
            elif sl["typ"] == "strop":
                items.append((float(sl["wierzch"]), "konstr"))
            else:
                items.append((float(sl["top"]), "wyk"))
        foot = [it["z0"] for it in self.items if it["kind"] == "fund"]
        if foot:
            items.append((min(foot), "konstr"))
        zt_r = float(np.interp(self.s_max + 0.6, self.profile[:, 0], self.profile[:, 1]))
        items.append((zt_r, "wyk"))
        items = _dedupe_levels(items)
        x_lv = self.bx[2] + 8.0 * k
        n0 = len(vp.prims)
        dims.levels(vp, x_lv, items, side="right")
        self.placer.add_prims(vp.prims[n0:])
        # łańcuchy wysokości — po lewej
        zt_l = float(np.interp(self.s_min - 0.6, self.profile[:, 0], self.profile[:, 1]))
        chain_detail = {zt_l}
        chain_storey = {zt_l}
        left_walls = self._edge_walls(left=True)
        for kk in m.kondygnacje:
            if self._storey_cut(kk):
                chain_detail.add(kk.rzedna)
                chain_storey.add(kk.rzedna)
        for w in left_walls:
            sw = self._wall_s(w)
            if sw is None:
                continue
            for op in w.otwory:
                if op.s0 - 1e-6 <= sw <= op.s1 + 1e-6:
                    chain_detail |= {op.z0, op.z1}
        for it in self.items:
            if it["kind"] == "strop" and it["s0"] <= self.s_min + 0.8:
                chain_detail.add(it["z0"])
        tops = [it["z1"] for it in self.items if it["s0"] <= self.s_min + 0.8 and it["kind"] != "grunt"]
        ztop_l = max(tops) if tops else self.z_max
        roof_l = [float(sl["top"]) for sl in m.plyty() if sl["typ"] == "dach" and self._elem_cut(sl["id"])]
        for z in roof_l:
            if z <= ztop_l + 1e-6:
                chain_detail.add(z)
                chain_storey.add(z)
        chain_detail.add(ztop_l)
        chain_storey.add(ztop_l)
        # łańcuch szczegółowy tylko do wysokości ściany skrajnej; kondygnacyjny — wszystkie poziomy i dachy
        chain_detail = {z for z in chain_detail if z <= ztop_l + 1e-6}
        for z in [float(sl["top"]) for sl in m.plyty() if sl["typ"] == "dach" and self._elem_cut(sl["id"])]:
            chain_storey.add(z)
        att = [float(sl.get("top_attyki") or 0) for sl in m.plyty() if sl["typ"] == "dach" and self._elem_cut(sl["id"])]
        if att:
            chain_storey.add(max(att))
        rnd = lambda v: round(float(v), 3)    # noqa: E731 — punkty na siatce 1 mm (sumy łańcuchów = całość)
        chain_detail = {rnd(v) for v in chain_detail}
        chain_storey = {rnd(v) for v in chain_storey}
        chains = [sorted(chain_detail), sorted(chain_storey), [rnd(min(zt_l, 0.0)), rnd(max(self.z_max, ztop_l))]]
        base = self.bx[0] - 2.0 * k
        off = 10.0
        n0 = len(vp.prims)
        prev = None
        for ch in chains:
            ch = _uniq(ch)
            if len(ch) < 2 or ch == prev:
                continue
            dims.dim_v(vp, ch, base - off * k, base)
            prev = ch
            off += 7.0
        # wysokość budynku wg § 6 WT
        xh = base - off * k
        dims.dim_v(vp, [round(H["z_ent"], 3), round(H["z_top"], 3)], xh, base)
        wt = f"wysokość budynku wg § 6 WT: H = {fmt.num(H['H'], 2)} m"
        vp.text((xh - 5.0 * k, (H["z_ent"] + H["z_top"]) / 2), wt, 2.5, 90.0, "center", "baseline",
                layer="A-WYMIARY", mask=0.4)
        vp.line((xh - 2 * k, H["z_ent"]), (base - 10 * k + 2 * k, H["z_ent"]), "A-WYMIARY", pen="cienka",
                lt="KRESKOWA")
        self.placer.add_prims(vp.prims[n0:])
        # osie
        self.axes()
        # opis warstw (duże bloki — najpierw), potem wysokości w świetle i opisy pomieszczeń
        self.callouts()
        self.rooms()

    def _dedupe(self):
        pass

    def _storey_cut(self, kk) -> bool:
        return any(it["p"].level == kk.id for it in self.items)

    def _elem_cut(self, eid) -> bool:
        return any(it["elem"] == str(eid) for it in self.items)

    def _edge_walls(self, left=True):
        out = []
        lim = self.s_min + 0.8 if left else self.s_max - 0.8
        for it in self.items:
            wid = it["p"].meta.get("wall")
            if not wid or it["p"].kind not in ("wall", "insulation"):
                continue
            if (left and it["s0"] <= lim) or (not left and it["s1"] >= lim):
                w = self.m.sciana(wid)
                if w is not None and w not in out:
                    out.append(w)
        return out

    def _wall_s(self, w):
        """Położenie (wzdłuż osi ściany) punktu przecięcia osi ściany z płaszczyzną przekroju."""
        a = LineString([tuple(w.p1), tuple(w.p2)])
        ln = LineString([tuple(self.o - self.R * 1e3), tuple(self.o + self.R * 1e3)])
        x = a.intersection(ln)
        if x.is_empty or not isinstance(x, Point):
            return None
        return w.st((x.x, x.y))[0]

    def axes(self):
        vp, k, m = self.vp, self.vp.k, self.m
        t = self.sec["t"]
        z0 = self.z_min - 0.4
        z1 = self.z_max + 0.6
        pts = []
        if abs(t[1]) > 0.99:           # płaszczyzna wzdłuż y → osie y
            for name, y in (m.osie.get("y") or {}).items():
                pts.append((str(name), self.s_of((self.o[0], y))))
        elif abs(t[0]) > 0.99:
            for name, x in (m.osie.get("x") or {}).items():
                pts.append((str(name), self.s_of((x, self.o[1]))))
        n0 = len(vp.prims)
        for name, s in pts:
            if self.s_min - 0.4 <= s <= self.s_max + 0.4:
                S.axis_line(vp, (s, z0 - 6 * k), (s, z1 + 6 * k), name, "both")
        self.placer.add_prims(vp.prims[n0:], w_line=0.2)

    def rooms(self):
        vp, k, m = self.vp, self.vp.k, self.m
        ln = LineString([tuple(self.o - self.R * 1e3), tuple(self.o + self.R * 1e3)])
        for r in m.pomieszczenia():
            if r.polygon is None or r.polygon.is_empty:
                continue
            inter = r.polygon.intersection(ln)
            segs = [a for a in lines_of(inter) if len(a) >= 2]
            if not segs:
                continue
            kk = m.kondygnacja(r.kond)
            zf = float(r.raw.get("rzedna", kk.rzedna)) if isinstance(r.raw.get("rzedna"), (int, float)) else kk.rzedna
            hgt = r.wysokosc or kk.wys_w_swietle or 2.5
            for a in segs:
                sa, sb = sorted([self.s_of(a[0]), self.s_of(a[-1])])
                if sb - sa < 0.6:
                    continue
                # wysokość w świetle
                cands = [sa + f * (sb - sa) for f in (0.12, 0.88, 0.25, 0.75, 0.4, 0.6)]

                def fn(cv, s, zf=zf, hgt=hgt):
                    dims.dim_v(cv, [zf, zf + hgt], s, s + 0.2, ext="short")
                self.placer.place(vp, fn, cands, penalty_step=0.2)
                # numer i nazwa
                num = room_label(m, r.id, self.num_mode)
                cz = zf + hgt * 0.5
                cc = [(sa + f * (sb - sa), cz + dz) for f in (0.5, 0.35, 0.65) for dz in (0.0, 0.4, -0.4, 0.8)]
                bounds = box(sa + 0.05, zf + 0.05, sb - 0.05, zf + hgt - 0.05)

                def fn2(cv, pos, num=num, name=r.nazwa):
                    S.room_tag(cv, pos, num, name, None, h=2.5, h_num=2.5)
                if self.placer.place(vp, fn2, cc, bounds=bounds, max_cost=2.0)[0] is None:
                    def fn3(cv, pos, num=num):
                        S.room_tag(cv, pos, num, None, None, h=2.5, h_num=2.5)
                    self.placer.place(vp, fn3, cc, bounds=bounds, max_cost=4.0)
                break

    # ------------------------------------------------------------------ opis warstw
    def callouts(self):
        vp, k, m = self.vp, self.vp.k, self.m
        if not self.opts.get("opisy_warstw", self.ctx.opt("opisy_warstw", True)):
            return
        self.max_callout = float(self.opts.get("max_kolizja_opisu", 60.0))
        self.skipped = []
        done = set()
        # przegrody poziome
        horiz = []
        for sl in m.plyty():
            horiz.append((str(sl["id"]), sl["typ"], sl))
        for kk in m.kondygnacje[:1]:
            horiz.insert(0, (f"POD-{kk.id}", "podloga", kk))
        for eid, typ, data in horiz:
            its = [it for it in self.items if it["elem"] == eid and it["kind"] not in ("grunt",)]
            if not its:
                continue
            code, title, texts = self._horiz_texts(typ, data)
            if not texts or code in done:
                continue
            done.add(code)
            self._place_horiz(its, title, texts)
        # ściany zewnętrzne (jedna na przegrodę)
        for left in (True, False):
            for w in self._edge_walls(left=left):
                if w.typ != "sciana_zewn" or w.przegroda_kod in done:
                    continue
                its = [it for it in self.items if it["p"].meta.get("wall") == w.id]
                if not its:
                    continue
                done.add(w.przegroda_kod)
                self._place_wall(w, its, left)
        if self.skipped:
            nm = str(self.sec.get("nazwa") or "").strip()      # arkusz z kilkoma przekrojami — do którego uwaga
            if nm.upper().startswith("PRZEKRÓJ "):
                nm = "Przekrój " + nm[9:].strip()
            self.res.notes.append((f"{nm}: o" if nm else "O") + "pisy warstw pominięte na rysunku (brak miejsca w "
                                  "podziałce "
                                  f"1:{int(vp.scale)}): {', '.join(self.skipped)} — układ warstw wg zestawienia "
                                  "przegród w części opisowej / przekroju 1:50.")

    def _horiz_texts(self, typ, data):
        m = self.m
        if typ == "podloga":
            p = m.przegroda(data.podloga) if data.podloga else None
            if p is None:
                return None, None, []
            return p.kod, f"{p.kod} — {p.nazwa}", [layer_text(m, w.mat, w.d) for w in p.warstwy]
        raw = data["raw"]
        if typ == "strop":
            pk = raw.get("podloga")
            p = m.przegroda(str(pk)) if pk else None
            texts = []
            if p is not None:
                texts += [layer_text(m, w.mat, w.d) for w in (p.warstwy if p.ma_oznaczona_konstr else p.warstwy)]
            if p is None or not p.ma_oznaczona_konstr:
                mat = str(raw.get("mat") or "")
                nm = material_name(m, mat) if mat else "Strop żelbetowy"
                if not mat:
                    for pp in m.przegrody.values():
                        if pp.typ in ("stropodach", "taras", "strop") and pp.ma_oznaczona_konstr:
                            nm = material_name(m, pp.warstwy[pp.idx_konstr].mat)
                            break
                texts.append(f"{nm} (strop {raw.get('id')}) {fmt.num(float(raw['grubosc']) * 100, 1, strip=True)} cm")
            suf = raw.get("sufit")
            if suf:
                sp = m.przegroda(str(suf))
                if sp is not None:
                    texts += [layer_text(m, w.mat, w.d) for w in sp.warstwy]
                else:
                    texts.append(layer_text(m, str(suf), 0.01))
            code = f"{raw.get('id')}/{pk}"
            title = f"STROP {raw.get('id')}" + (f" + {p.kod} — {p.nazwa}" if p is not None else "")
            return code, title, texts
        pk = raw.get("przegroda")
        p = m.przegroda(str(pk)) if pk else None
        if p is None:
            return None, None, []
        title = f"{p.kod} — {p.nazwa}" + (f" ({raw.get('id')})" if typ == "wspornik" else "")
        return p.kod, title, [layer_text(m, w.mat, w.d) for w in p.warstwy]

    def _place_horiz(self, its, title, texts):
        vp, k = self.vp, self.vp.k
        s0 = min(it["s0"] for it in its)
        s1 = max(it["s1"] for it in its)
        cands = []
        n = max(6, int((s1 - s0) / 0.35))
        fr = sorted(np.linspace(0.06, 0.94, n), key=lambda f: abs(f - 0.5))
        for f in fr:
            s = s0 + f * (s1 - s0)
            here = [it for it in its if it["s0"] + 0.05 <= s <= it["s1"] - 0.05]
            if len(here) < max(1, len(texts) // 2):
                continue
            here.sort(key=lambda it: -it["z1"])
            ztop = here[0]["z1"]
            marks = [(s, (it["z0"] + it["z1"]) / 2) for it in here[:-1]]
            pstart = (s, (here[-1]["z0"] + here[-1]["z1"]) / 2)
            for rise in (6.0, 10.0, 16.0, 24.0):
                for side in ("right", "left"):
                    cands.append((pstart, (s, ztop + rise * k), side, marks))

        def fn(cv, c):
            ps, pe, side, marks = c
            _callout(cv, ps, pe, texts, side, marks, title)
        if not cands or self.placer.place(vp, fn, cands, penalty_step=0.05, max_cost=self.max_callout)[0] is None:
            self.skipped.append(title.split(" — ")[0])

    def _place_wall(self, w, its, left):
        vp, k, m = self.vp, self.vp.k, self.m
        order = list(reversed(w.przegroda.warstwy)) if left else list(w.przegroda.warstwy)
        texts = [layer_text(m, x.mat, x.d) for x in order]
        title = f"{w.przegroda_kod} — {w.przegroda.nazwa}"
        cands = []
        walls = [v for v in self._edge_walls(left=left) if v.przegroda_kod == w.przegroda_kod]
        combos = []
        for v in walls:
            vits = sorted([it for it in self.items if it["p"].meta.get("wall") == v.id], key=lambda it: it["s0"])
            if vits:
                for zf in (0.55, 0.45, 0.65, 0.35, 0.25, 0.72, 0.18, 0.8):
                    combos.append((v, vits, zf))
        combos.sort(key=lambda t: abs(t[2] - 0.5))
        for v, its, zf in combos:
            kk = m.kondygnacja(v.kond)
            sa = min(it["s0"] for it in its)
            sb = max(it["s1"] for it in its)
            z = kk.rzedna + kk.wys_kondygnacji * zf
            here = [it for it in its if it["z0"] <= z <= it["z1"]]
            if len(here) < 2:
                continue
            here.sort(key=lambda it: it["s0"])
            outer = here[0] if left else here[-1]
            ps = ((outer["s0"] + outer["s1"]) / 2, z)
            marks = [((it["s0"] + it["s1"]) / 2, z) for it in here]
            for dx in (10.0, 16.0, 24.0, 34.0, 46.0):
                pe = (sb + dx * k, z) if left else (sa - dx * k, z)
                cands.append((ps, pe, "right" if left else "left", marks))

        def fn(cv, c):
            ps, pe, side, marks = c
            _callout(cv, ps, pe, texts, side, marks, title)
        if not cands or self.placer.place(vp, fn, cands, penalty_step=0.05, max_cost=self.max_callout)[0] is None:
            self.skipped.append(w.przegroda_kod)


def _callout(cv, ps, pe, texts, side, marks, title):
    """Opis warstw z maskami pod napisami (czytelność na tle linii widoku)."""
    from ..draft.core import PText
    from ..draft import text as TT
    wmax = max(TT.width(t, 1.8) for t in texts) + 6.0
    if title and TT.width(title, 1.8, "bold") > wmax:
        words = title.split()
        while len(words) > 2 and TT.width(" ".join(words) + "…", 1.8, "bold") > wmax:
            words.pop()
        title = " ".join(words).rstrip(",;:—-") + "…"
    n0 = len(cv.prims)
    S.layer_callout(cv, ps, pe, texts, side=side, h=1.8, row_mm=3.6, marks=marks, title=title)
    for p in cv.prims[n0:]:
        if isinstance(p, PText):
            p.mask = 0.35


def _cls(p):
    if p.kind in ("glass",):
        return "glass"
    if p.kind in ("frame", "door_leaf"):
        return "stolarka"
    if p.kind in ("railing", "lamella"):
        return p.kind
    return "bryla"


def _uniq(vals, tol=1e-3):
    out = []
    for v in sorted(vals):
        if not out or v - out[-1] > tol:
            out.append(v)
    return out


def _dedupe_levels(items, tol=0.005):
    out = []
    for it in sorted(items, key=lambda t: (t[0], 0 if t[1] == "zero" else 1)):
        if out and abs(out[-1][0] - it[0]) < tol:
            continue
        out.append(it)
    return out


def draw_section(vp, ctx: ViewContext, sec: dict, opts: dict | None = None) -> SectionResult:
    """Rysuje przekrój ``sec`` (znormalizowana definicja — ``normalize_section``) do rzutni ``vp``.
    Układ rzutni: x = s (w prawo wg kierunku patrzenia), y = z (rzędne względne)."""
    return SectionBuilder(vp, ctx, sec, dict(opts or {})).run()
