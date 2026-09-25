"""ELEWACJA (N / S / E / W) — rzut prostokątny budynku z usuwaniem linii niewidocznych.

Algorytm (``hlr``): ściany boczne pryzm IR zwrócone do obserwatora → prostokąty (s, z); ściany współpłaszczyznowe
z tego samego materiału scalane (brak krawędzi pozornych podziału IR); grupy od najbliższej — widoczna część
= obszar − suma bliższych, widoczne krawędzie = brzeg − suma bliższych (+ tolerancja). Grunt przed elewacją
zasłania części poniżej linii terenu (fundamenty, cokół ocieplenia).

Na rysunku: podziały stolarki (ramy, słupki, skrzydła, szyby), lamele, attyki z obróbkami, wysunięte płyty,
balustrady, linia terenu z rzędnymi, kolorystyka materiałów wykończenia (wypełnienia wg ``kolor`` materiałów modelu)
z oznaczeniami (numery w sześciokątach) i legendą, rzędne charakterystyczne, osie skrajne, wysokość budynku
wg § 6 WT.

Elewacja „S” (południowa) = widok ściany zwróconej na południe (obserwator po stronie południowej patrzy na północ);
kierunki geograficzne z ``uklad.azymut_osi_y`` modelu.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, fmt, hatch as H, symbols as S
from ..draft.geom import polygons_of
from . import hlr
from .common import Placer, ViewContext, clean, draw_lines, label_point, material_color, material_name
from .section import building_height, terrain_profile

NAMES = {"N": "ELEWACJA PÓŁNOCNA", "S": "ELEWACJA POŁUDNIOWA", "E": "ELEWACJA WSCHODNIA", "W": "ELEWACJA ZACHODNIA"}
EL_EXCL = {"furniture"}


@dataclass
class ElevationResult:
    side: str
    materials: list = field(default_factory=list)   # [(nr, kod, nazwa, kolor, pow_m2)]
    height: dict = field(default_factory=dict)
    extent: tuple | None = None


def look_dir(model, side: str) -> np.ndarray:
    """Kierunek patrzenia dla elewacji strony ``side`` (N/S/E/W) w układzie budynku."""
    a = math.radians(getattr(model, "azymut_osi_y", 0.0) or 0.0)
    N = np.array([-math.sin(a), math.cos(a)])
    Ev = np.array([math.cos(a), math.sin(a)])
    side = side.upper()
    return {"S": N, "N": -N, "E": -Ev, "W": Ev}[side]


def _light(hexc: str, f: float = 0.0) -> str:
    c = hexc.lstrip("#")
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    if lum < 0.30:          # bardzo ciemne (antracyt) — rozjaśnienie, żeby linie pozostały czytelne
        f = max(f, 0.30)
    r, g, b = (int(v + (255 - v) * f) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


class ElevationBuilder:
    def __init__(self, vp, ctx: ViewContext, side: str, opts: dict):
        self.vp, self.ctx, self.side, self.opts = vp, ctx, side.upper(), opts
        self.m = ctx.model
        self.L = look_dir(self.m, self.side)
        self.R = np.array([self.L[1], -self.L[0]])
        x0, y0, x1, y1 = self.m.bbox()
        c = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
        self.c = c
        self.o = c - self.L * 200.0
        self.placer = Placer(vp.k)
        self.res = ElevationResult(self.side)

    def s_of(self, p):
        return float((np.asarray(p, float) - self.o) @ self.R)

    def d_of(self, p):
        return float((np.asarray(p, float) - self.o) @ self.L)

    def run(self):
        self.project()
        self.annotate()
        self.res.extent = self.vp.extents()
        return self.res

    def project(self):
        vp, m = self.vp, self.m
        prisms = [p for p in self.ctx.building_prisms if p.kind not in EL_EXCL and p.meta.get("group") != "fundamenty"]
        groups = hlr.side_groups(prisms, self.o, self.L, key_fn=lambda p: (p.material, _cls(p)))
        if not groups:
            self.ctx.note(f"elewacja {self.side}", "brak elementów budynku")
            self.s_min = self.s_max = 0.0
            self.z_min = self.z_max = 0.0
            self.profile = np.array([[0, 0], [1, 0]])
            self.sil = Polygon()
            return
        sil = unary_union([g.poly for g in groups])
        bx = sil.bounds
        self.s_min, self.s_max = bx[0], bx[2]
        # front budynku: najbliższe lico ścian najniższej kondygnacji
        ob = m.obrys_kondygnacji(m.kondygnacje[0].id) if m.kondygnacje else Polygon()
        if not ob.is_empty:
            d_front = min(self.d_of(p) for pg in polygons_of(ob) for p in pg.exterior.coords)
        else:
            d_front = 200.0 - 5.0
        marg = float(self.opts.get("margines_terenu", 2.0))
        prof = terrain_profile(self.ctx, self.o, self.R, self.s_min - marg, self.s_max + marg, 0.25, L=self.L,
                               depth=d_front - 0.3)
        self.profile = prof
        z_bot = float(prof[:, 1].min()) - 1.2
        ground = Polygon([(prof[0, 0], z_bot)] + [tuple(p) for p in prof] + [(prof[-1, 0], z_bot)]).buffer(0)
        self.ground = ground
        order = hlr.hidden_lines(groups, occluder=ground, tol=4e-4, min_len=0.01)
        self.sil = clean(sil.difference(ground))
        self.z_min, self.z_max = self.sil.bounds[1], self.sil.bounds[3]
        colour = self.opts.get("kolorystyka", self.ctx.opt("kolorystyka", True))
        mats = {}
        for g in order:
            if g.vis is None or g.vis.is_empty:
                continue
            a = g.vis.area
            if a < 1e-4:
                continue
            e = mats.setdefault(g.material, dict(area=0.0, polys=[]))
            e["area"] += a
            e["polys"].append(g.vis)
            if colour:
                col = _light(material_color(m, g.material), 0.08 if g.kind != "glass" else 0.0)
                vp.fill(g.vis, "A-ELEWACJE", col, z=4.0)
        allg = []
        for g in order:
            if g.lines is None or g.lines.is_empty:
                continue
            draw_lines(vp, g.lines, "A-ELEWACJE", pen="cienka", min_len=0.01)
            allg.append(g.lines)
        gv = [g.vis for g in order if g.kind == "glass" and g.vis is not None and not g.vis.is_empty]
        self.glass_vis = unary_union(gv) if gv else Polygon()
        # sylweta — linia średnia
        silb = self.sil.boundary.difference(ground.buffer(1e-3))
        draw_lines(vp, silb, "A-ELEWACJE", pen="srednia", min_len=0.02)
        self.placer.add_lines(unary_union(allg) if allg else None, w=0.15)
        self.mats = mats
        # linia terenu
        vp.polyline(prof, "A-TEREN", pen="b_gruba")
        H.ground_band(vp, prof)
        self.placer.add_lines(LineString([tuple(p) for p in prof]), w=1.0, buf_mm=1.5)

    # ------------------------------------------------------------------ opisy
    def annotate(self):
        vp, k, m = self.vp, self.vp.k, self.m
        if self.sil.is_empty:
            return
        # kierunki otwierania stolarki (trójkąty — wierzchołek po stronie zawiasów; kreskowo: do wewnątrz)
        self.opening_marks()
        # oznaczenia materiałów
        rows = []
        mats = sorted(self.mats.items(), key=lambda kv: -kv[1]["area"])
        nr = 0
        for code, e in mats:
            if e["area"] < float(self.opts.get("min_pow_materialu", 0.25)):
                continue
            nr += 1
            name = material_name(m, code)
            rows.append((nr, code, name, material_color(m, code), e["area"]))
            big = max((p for g in e["polys"] for p in polygons_of(g)), key=lambda p: p.area)
            c = label_point(big)
            cands = [(c[0] + dx, c[1] + dy) for dx in (0.0, 0.4, -0.4, 0.8, -0.8) for dy in (0.0, 0.3, -0.3)]
            cands = [p for p in cands if big.buffer(-0.12).contains(Point(p))]

            def fn(cv, pos, nr=nr):
                S.tag(cv, pos, str(nr), shape="hex", r_mm=2.6, h=2.5)
            if not cands or self.placer.place(vp, fn, cands, max_cost=6.0)[0] is None:
                # poza obszarem materiału — z odnośnikiem (kropka w polu materiału)
                oc = []
                for dx in (14.0, -14.0, 22.0, -22.0):
                    for dy in (10.0, -10.0, 16.0, -16.0, 0.0):
                        oc.append((c, (c[0] + dx * k, c[1] + dy * k)))

                def fn2(cv, cc, nr=nr):
                    P, Q = np.asarray(cc[0]), np.asarray(cc[1])
                    d = Q - P
                    L = float(np.hypot(*d))
                    cv.line(P, Q - d / L * 3.0 * k, "A-OPISY", pen="cienka")
                    cv.dot(P, 0.9, "A-OPISY")
                    S.tag(cv, Q, str(nr), shape="hex", r_mm=2.6, h=2.5)
                self.placer.place(vp, fn2, oc)
        self.res.materials = rows
        # rzędne — po prawej
        ext = vp.extents()
        X0, Y0, X1, Y1 = ext
        items = [(0.0, "zero", m.zero_abs)]
        for kk in m.kondygnacje:
            if abs(kk.rzedna) > 1e-4:
                items.append((kk.rzedna, "wyk"))
        for sl in m.plyty():
            if sl["typ"] == "dach":
                items.append((float(sl["top"]), "wyk"))
                if sl.get("top_attyki"):
                    items.append((float(sl["top_attyki"]), "wyk"))
        if all(abs(self.z_max - it[0]) > 0.05 for it in items):
            items.append((round(self.z_max, 3), "wyk"))
        zt_r = round(float(np.interp(self.s_max + 0.5, self.profile[:, 0], self.profile[:, 1])), 3)
        items.append((zt_r, "wyk"))
        out = []
        for it in sorted(items, key=lambda t: (t[0], 0 if t[1] == "zero" else 1)):
            if out and abs(out[-1][0] - it[0]) < 0.005:
                continue
            out.append(it)
        n0 = len(vp.prims)
        dims.levels(vp, self.s_max + 8.0 * k, out, side="right")
        self.placer.add_prims(vp.prims[n0:])
        # teren przy narożnikach (rzędna)
        zt_l = round(float(np.interp(self.s_min - 0.5, self.profile[:, 0], self.profile[:, 1])), 3)
        # wysokość budynku wg § 6 WT — po lewej
        Hh = building_height(self.ctx)
        self.res.height = Hh
        xh = self.s_min - 14.0 * k
        n0 = len(vp.prims)
        dims.level_section(vp, (self.s_min - 3.0 * k, zt_l), zt_l, "wyk", side="left", stub_mm=4.0)
        dims.dim_v(vp, [round(Hh["z_ent"], 3), round(Hh["z_top"], 3)], xh - 10.0 * k, xh)
        dims.dim_v(vp, [zt_l, 0.0] + [kk.rzedna for kk in m.kondygnacje[1:]] +
                   [round(Hh["z_top"], 3), round(self.z_max, 3)], xh, xh + 2 * k)
        wt = f"wysokość budynku wg § 6 WT: H = {fmt.num(Hh['H'], 2)} m"
        vp.text((xh - 15.0 * k, (Hh["z_ent"] + Hh["z_top"]) / 2), wt, 2.5, 90.0, "center", "baseline",
                layer="A-WYMIARY", mask=0.4)
        self.placer.add_prims(vp.prims[n0:])
        # osie skrajne (i pozostałe) pod linią terenu
        self.axes()
        # wymiar całkowity długości elewacji (pod terenem)
        zb = float(self.profile[:, 1].min())
        n0 = len(vp.prims)
        dims.dim_h(vp, [self.s_min, self.s_max], zb - 7.0 * k, zb)
        self.placer.add_prims(vp.prims[n0:])

    def opening_marks(self):
        vp, k, m = self.vp, self.vp.k, self.m
        if self.glass_vis.is_empty:
            return
        from ..draft.dims import arrowhead
        for o in m.otwory():
            w = o.sciana
            if w is None or w.ext_side is None or o.typ not in ("okno", "drzwi_przesuwne_HS"):
                continue
            if float((w.n * w.ext_side) @ self.L) > -0.9:
                continue
            ow = o.otwieranie or {}
            rodzaj = str(ow.get("rodzaj", "")).upper()
            if not rodzaj or rodzaj == "F":
                continue
            nk = o.raw.get("kwatery")
            if not isinstance(nk, (int, float)):
                pane = {"okno": 1.6, "drzwi_przesuwne_HS": 3.0}.get(o.typ, 1.6)
                nk = max(2 if o.typ == "drzwi_przesuwne_HS" else 1, math.ceil((o.szer - 1e-6) / pane))
            nk = int(nk)
            fw = {"okno": 0.075, "drzwi_przesuwne_HS": 0.085}.get(o.typ, 0.075)
            fb = 0.03 if o.typ == "drzwi_przesuwne_HS" or o.parapet < 0.05 else fw
            inner = o.szer - 2 * fw
            pw = (inner - (nk - 1) * fw) / nk
            z0, z1 = o.z0 + fb, o.z1 - fw
            # strona zawiasów: „lewa” patrząc od wewnątrz → prawa na elewacji (widok od zewnątrz)
            hinge_right = str(ow.get("strona", "lewa")) != "prawa"
            inward = str(ow.get("kierunek", "do_wewn")) != "na_zewn"
            lt = "KRESKOWA" if inward else None
            segs = []
            for i in range(nk):
                a = o.s0 + fw + i * (pw + fw)
                b = a + pw
                sa, sb = sorted([self.s_of(w.pt(a, 0.0)), self.s_of(w.pt(b, 0.0))])
                if o.typ == "drzwi_przesuwne_HS":
                    moving = (i == nk - 1) if hinge_right else (i == 0)
                    if moving:
                        zc = z0 + (z1 - z0) * 0.45
                        d = -1.0 if hinge_right else 1.0
                        p0 = ((sa + sb) / 2 - d * pw * 0.25, zc)
                        p1 = ((sa + sb) / 2 + d * pw * 0.25, zc)
                        if self.glass_vis.buffer(1e-3).contains(Point(p1)):
                            vp.line(p0, (p1[0] - d * 2.0 * k, zc), "A-ELEWACJE", pen="cienka")
                            arrowhead(vp, p1, (d, 0.0), 2.4, 12, True, "A-ELEWACJE")
                    continue
                hs = sb if hinge_right else sa
                os_ = sa if hinge_right else sb
                if "R" in rodzaj or "D" in rodzaj:
                    segs.append([(os_, z1), (hs, (z0 + z1) / 2), (os_, z0)])
                if "U" in rodzaj or "K" in rodzaj:
                    segs.append([(sa, z1), ((sa + sb) / 2, z0), (sb, z1)])
            if segs:
                from shapely.geometry import MultiLineString
                g = MultiLineString(segs).intersection(self.glass_vis)
                draw_lines(vp, g, "A-ELEWACJE", pen="b_cienka", lt=lt, min_len=0.02)

    def axes(self):
        vp, k, m = self.vp, self.vp.k, self.m
        zb = float(self.profile[:, 1].min())
        pts = []
        if abs(self.R[0]) > 0.99:
            for name, x in (m.osie.get("x") or {}).items():
                pts.append((str(name), self.s_of((x, self.c[1]))))
        elif abs(self.R[1]) > 0.99:
            for name, y in (m.osie.get("y") or {}).items():
                pts.append((str(name), self.s_of((self.c[0], y))))
        pts = [(n, s) for n, s in pts if self.s_min - 0.4 <= s <= self.s_max + 0.4]
        if not pts:
            return
        pts.sort(key=lambda t: t[1])
        sel = pts if self.opts.get("osie_wszystkie", True) else [pts[0], pts[-1]]
        n0 = len(vp.prims)
        for name, s in sel:
            S.axis_line(vp, (s, zb - 12.0 * k), (s, zb - 1.5 * k + 0.0), name, "start")
        self.placer.add_prims(vp.prims[n0:], w_line=0.2)


def _cls(p):
    if p.kind == "glass":
        return "glass"
    if p.kind in ("frame", "door_leaf"):
        return "stolarka"
    if p.kind in ("railing", "lamella"):
        return p.kind
    return "bryla"


def draw_elevation(vp, ctx: ViewContext, side: str, opts: dict | None = None) -> ElevationResult:
    """Rysuje elewację ``side`` (N/S/E/W) do rzutni ``vp`` (x = s w prawo, y = z)."""
    return ElevationBuilder(vp, ctx, side, dict(opts or {})).run()
