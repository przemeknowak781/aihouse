"""IS-CO — ogrzewanie: pompa ciepła powietrze–woda (jednostka zewnętrzna i moduł hydrauliczny), bufor, zasobnik c.w.u.,
rozdzielacze ogrzewania podłogowego na kondygnacjach, pętle (obszar grzejny ze skokiem T i długością L z obliczeń
PN-EN 1264), przyłącza pętli, piony zasilające rozdzielacze.

Dane: ``lamela.obliczenia.sanitarne.ogrzewanie`` (Φ_HL pomieszczeń, pętle, rozdzielacze, PC, bufor, przewody PC),
lokalizacje z ``instalacje.yaml`` (rozdzielacze_co, pompa_ciepla_jz, zasobnik) i ``wyposazenie.yaml``."""
from __future__ import annotations

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ...draft import hatch as Hh
from ...draft import symbols as S
from ...draft.geom import dir_deg, polygons_of
from ...obliczenia.sanitarne.woda import RURY_WIELOWARSTWOWE, dobierz_rure
from ..common import label_point
from .baza import Rysunek
from .wspolne import BRAK, H_S, num, table_block, text_block


def paski(pg, n):
    """Podział wieloboku na n pasów o równych polach wzdłuż dłuższego boku obwiedni (strefy pętli)."""
    if n <= 1:
        return [pg]
    x0, y0, x1, y1 = pg.bounds
    horiz = (x1 - x0) >= (y1 - y0)
    A = pg.area
    cuts = []
    lo = x0 if horiz else y0
    hi = x1 if horiz else y1
    for i in range(1, n):
        target = A * i / n
        a, b = lo, hi
        for _ in range(40):
            c = (a + b) / 2
            part = pg.intersection(box(x0, y0, c, y1) if horiz else box(x0, y0, x1, c))
            if part.area < target:
                a = c
            else:
                b = c
        cuts.append((a + b) / 2)
    edges = [lo] + cuts + [hi]
    out = []
    for i in range(n):
        bx = box(edges[i], y0, edges[i + 1], y1) if horiz else box(x0, edges[i], x1, edges[i + 1])
        out.append(pg.intersection(bx))
    return out


def rura_dla(m_kgh, v=0.8):
    r = dobierz_rure(m_kgh / 3600.0, v, RURY_WIELOWARSTWOWE, 16)
    return f"{r[0]}×{num(r[1], 1)}"


class RysCO(Rysunek):
    kod = "IS-CO"

    def run(self):
        W = self.W
        og = W.ogrzewanie
        self.podklad(meble=False)
        lok = W.dane.inst.get("lokalizacje") or {}
        self.rozdz_xy = {k: np.asarray(v[:2], float) for k, v in (lok.get("rozdzielacze_co") or {}).items()}
        pts = list(self.rozdz_xy.values())
        jz = (lok.get("pompa_ciepla_jz") or {}).get("xy")
        if jz:
            pts.append(jz)
        self.siatka(extra_pts=pts, nieogrzewane=4.0)
        self.leg.line("S-OGRZ", "przyłącza pętli ogrzewania podłogowego (zasilanie/powrót PE-X/Al/PE-X 16×2, "
                      "prowadzone wiązką od rozdzielacza)", pen="cienka")
        self.leg.line("S-PC", "Z/P — przewody zasilania i powrotu c.o. (PC → bufor → rozdzielacze), piony c.o.",
                      pen="srednia")
        self.petle()
        if self.kid == self.kids[0]:
            self.zrodlo()
        self.piony_co()
        self.rozdzielacz()
        self.opisy()
        self.room_extra = {r: [f"{num(og.phi.get(r, 0), 0)} W"] for r in og.phi}
        for r in self.m.pomieszczenia(self.kid):
            if r.temp is not None and r.id in self.room_extra:
                self.room_extra[r.id] = [f"θ_i = {num(r.temp, 0)} °C, Φ_HL = {num(og.phi.get(r.id, 0), 0)} W"]
        return self.finish()

    # --------------------------------------------------------------------------------------------- pętle
    def petle(self):
        og = self.W.ogrzewanie
        vp = self.vp
        by = {}
        for p in og.petle:
            by.setdefault(p.pom, []).append(p)
        R = self.rozdz_xy.get(self.kid)
        self.regions = []
        for r in self.m.pomieszczenia(self.kid):
            lst = by.get(r.id)
            if not lst or r.polygon is None:
                continue
            base = r.polygon.buffer(-0.15, join_style=2)
            if base.is_empty:
                continue
            base = max(polygons_of(base), key=lambda g: g.area)
            parts = paski(base, len(lst))
            for p, pg in zip(sorted(lst, key=lambda p: p.nr), parts):
                pg = max(polygons_of(pg.buffer(-0.04, join_style=2)) or [pg], key=lambda g: g.area)
                if pg.is_empty:
                    continue
                n0 = len(vp.prims)
                vp.geom(pg, "S-OGRZ", pen=0.18, lt="KRESKOWA_DROBNA")
                self._meander(pg, p.T)
                self.pl.add(pg.boundary.buffer(0.3 * self.k), "line", 0.2)
                self.regions.append((r, p, pg))
                c = label_point(pg)
                lines = [f"{r.id}/{p.nr}", f"T = {num(100 * p.T, 0)} cm, L = {num(p.L, 0)} m"]
                text_block(vp, self.pl, c, lines, "S-OPISY", h=H_S, bounds=pg.buffer(-0.05), style="bold")
                if R is not None:
                    tg = self.g.mask(pg.boundary.buffer(0.06))
                    if tg.any():
                        path = self.g.route(R, None, "CO", reuse=0.3, other=2.0, targets=tg, margin=8.0)
                        self.pipe(path, "Z", pen=0.25, layer="S-OGRZ")
                        self.g.mark(path, "CO")
        self.leg.sym(lambda c, p: (c.polygon([p + np.array([-6, -2.5]), p + np.array([6, -2.5]),
                                              p + np.array([6, 2.5]), p + np.array([-6, 2.5])], "S-OGRZ", pen=0.18,
                                             lt="KRESKOWA_DROBNA"),
                                   c.polyline([p + np.array([-5, -1.5]), p + np.array([5, -1.5]), p + np.array([5, 0]),
                                               p + np.array([-5, 0]), p + np.array([-5, 1.5]), p + np.array([5, 1.5])],
                                              "S-OGRZ", pen=0.13, color="#e59a70")),
                     "strefa pętli ogrzewania podłogowego <pom.>/<nr>: T — rozstaw rur, L — długość pętli (z obliczeń "
                     "PN-EN 1264); meander symboliczny (co 4 rozstawy)")

    def _meander(self, pg, T):
        """Meander symboliczny w strefie (rozstaw rysunkowy 4·T, min. 0,40 m) — ilustracja układu pętli."""
        s = max(4 * T, 0.40)
        x0, y0, x1, y1 = pg.bounds
        horiz = (x1 - x0) >= (y1 - y0)
        pts = []
        if horiz:
            ys = np.arange(y0 + s / 2, y1, s)
            for i, y in enumerate(ys):
                pts += [(x0, y), (x1, y)] if i % 2 == 0 else [(x1, y), (x0, y)]
        else:
            xs = np.arange(x0 + s / 2, x1, s)
            for i, x in enumerate(xs):
                pts += [(x, y0), (x, y1)] if i % 2 == 0 else [(x, y1), (x, y0)]
        if len(pts) < 2:
            return
        g = LineString(pts).intersection(pg.buffer(-0.08, join_style=2))
        for a in [np.asarray(q.coords) for q in getattr(g, "geoms", [g]) if not q.is_empty and q.length > 0.05]:
            self.vp.polyline(a, "S-OGRZ", pen=0.13, lt="CIAGLA", color="#e59a70")

    # --------------------------------------------------------------------------------------------- źródło ciepła
    def _wyp(self, typ, szuk=None):
        for e in self.W.dane.wyposazenie:
            if e.get("typ") == typ and str(e.get("kond", "P0")) == self.kid and \
                    (szuk is None or szuk in str(e.get("opis", "")).lower()):
                return e
        return None

    def _srodek(self, e):
        d = dir_deg(float(e.get("obrot", 90.0)))
        dep = float((e.get("wym") or [0.6, 0.6])[1] if len(e.get("wym") or []) > 1 else (e.get("wym") or [0.6])[0])
        return np.asarray(e["xy"], float) + d * dep / 2

    def zrodlo(self):
        og, W = self.W.ogrzewanie, self.W
        pc = og.pc
        lok = W.dane.inst.get("lokalizacje") or {}
        jz = (lok.get("pompa_ciepla_jz") or {}).get("xy")
        mod = self._wyp("pompa_ciepla")
        buf = self._wyp("zasobnik", "bufor")
        zas = self._wyp("zasobnik", "cwu")
        P7 = dict(zip(pc["T"], pc["P"])).get(-7, None)
        self.mod_xy = self._srodek(mod) if mod else None
        if jz:
            q = np.asarray(jz, float)
            self.sym(S.heat_pump, q - np.array([0.0, 0.225]), 0.0, w=1.10, d=0.45, label="PC", outdoor=True)
            h = og.halas
            self.tag(q, [f"PC — pompa ciepła powietrze–woda monoblok R290 ({pc['model']}, lub równoważna)",
                         (f"P(A−7/W35) = {num(P7, 1)} kW; " if P7 else "") + f"SCOP {num(pc['SCOP_35'], 1)}; "
                         f"L_WA = {num(pc['L_WA'], 0)} dB(A); θ_biv = {num(og.biwalentny['theta_biv'], 1)} °C",
                         f"hałas na granicy działki {num(h['L_A_granica'], 1)} dB(A) (r = {num(h['r'], 1)} m); "
                         "strefa R290 1,0 m bez otworów i wpustów"], "S-OPISY", style="bold")
            self.leg.sym(lambda c, p: S.heat_pump(c, p - np.array([0.0, 2.5]), 0.0, w=10.0, d=5.0, label="PC"),
                         "PC — jednostka zewnętrzna pompy ciepła (monoblok) na fundamencie z tłumieniem drgań")
        if mod is not None:
            c = self.mod_xy
            self.sym(S.heat_pump, c - np.array([0.0, 0.15]), 0.0, w=0.6, d=0.3, label="MH", outdoor=False)
            self.tag(c, ["MH — moduł hydrauliczny PC: pompa obiegowa (H ≈ "
                         f"{num(og.przewody_pc['H_pompy_kPa'], 0)} kPa), zawór 3D c.o./c.w.u.,",
                         f"NW c.o. {og.naczynie_co['V_dob']} dm³ (p₀ = {num(og.naczynie_co['p_0'], 1)} bar), "
                         f"ZB {num(og.par.p_SV, 1)} bar, grzałka {num(og.par.grzalka_kW, 1)} kW"], "S-OPISY")
            if jz:
                a = np.asarray(jz, float) + np.array([0.0, 0.25])
                for key, off, comp in (("PCZ", -0.06, None), ("PCP", 0.06, "PCZ")):
                    path = self.g.route(a + np.array([off, 0.0]), c + np.array([off, 0.0]), key, companion=comp)
                    self.pipe(path, "Z", layer="S-PC", lt="CIAGLA" if key == "PCZ" else "KRESKOWA")
                    self.g.mark(path, key)
                self.label(path, f"Z/P {og.przewody_pc['rura']}, izolacja {num(og.przewody_pc['izol_zewn'], 0)} mm "
                           f"(zewn.) / {num(og.przewody_pc['izol_WT'], 0)} mm", "S-OPISY")
        V_buf = og.bufor["V_dob"]
        for e, lab, txt in ((buf, "B", f"bufor c.o. — obl. V ≥ {V_buf} dm³ ({(buf or {}).get('opis', '')})"),
                            (zas, "", f"zasobnik c.w.u. {W.woda.cwu['V_zas']} dm³ (obl.) z wężownicą "
                                      f"≥ {num(W.woda.cwu['A_wez'], 1)} m²")):
            if e is None:
                continue
            c = self._srodek(e)
            dd = float((e.get("wym") or [0.6])[0])
            self.sym(S.tank, c, d=dd, label=lab)
            self.tag(c, [txt], "S-OPISY")
            if self.mod_xy is not None:
                path = self.g.route(self.mod_xy, c, "PCB")
                self.pipe(path, "Z", layer="S-PC")
                self.g.mark(path, "PCB")
        self.leg.sym(lambda c, p: S.tank(c, p, d=6.0, label="B"), "bufor c.o. / zasobnik c.w.u. (wymiar rzeczywisty)")

    # --------------------------------------------------------------------------------------------- piony, rozdzielacze
    def _rozdz(self, kid):
        return next((r for r in self.W.ogrzewanie.rozdzielacze if r["kond"] == kid), None)

    def piony_co(self):
        """Pion c.o. zasilający rozdzielacze wyższych kondygnacji (model nie zawiera pionów c.o. — proponowany przy
        rozdzielaczu najniższej z wyższych kondygnacji)."""
        wyzsze = [k for k in self.kids[1:] if k in self.rozdz_xy and self._rozdz(k)]
        if not wyzsze:
            return
        i = self.kids.index(self.kid)
        top = max(self.kids.index(k) for k in wyzsze)
        if i > top:
            return
        base = self.rozdz_xy[wyzsze[0]]
        kids_rng = self.kids[:top + 1]
        pp = self.pion_punkty("PCO", base, kids_rng, n=2, step=0.10)
        flows = [(k, self._rozdz(k)["m_kgh"]) for k in wyzsze if self.kids.index(k) > i]
        lines = [f"{BRAK} pion c.o. PCO (proponowany)"]
        for k, mk in flows:
            lines.append(f"Z/P {rura_dla(mk)} → R-{k} (ṁ = {num(mk, 0)} kg/h)")
        if i > 0:
            lines.append("↓ z kondygnacji niższej")
        for q in pp:
            self.sym(S.riser, q, None, "Z", s_mm=2.2)
        self.tag(pp[0], lines, "I-BRAKI", color="#b0008a", style="bold")
        self.brak("Piony c.o. (zasilanie rozdzielaczy P1, P2)", "brak tras pionów c.o. w instalacje.yaml — przyjęto pion "
                  "proponowany przy rozdzielaczu R-" + wyzsze[0], "piony: [{id: PCO, xy: [x, y], rodzaj: co, kond: "
                  "[P0, P1, P2], opis}]")
        # połączenie z modułem (P0) lub z rozdzielaczem na tej kondygnacji
        src = self.mod_xy if (i == 0 and getattr(self, "mod_xy", None) is not None) else None
        R = self.rozdz_xy.get(self.kid)
        if src is not None:
            path = self.g.route(src, pp[0], "PCR")
            self.pipe(path, "Z", layer="S-PC")
            self.g.mark(path, "PCR")
            self.label(path, f"Z/P {rura_dla(sum(m for _k, m in flows))}", "S-OPISY")
        if R is not None and i > 0:
            path = self.g.route(pp[0], R, "PCR")
            self.pipe(path, "Z", layer="S-PC")
            self.g.mark(path, "PCR")
        self.leg.sym(lambda c, p: S.riser(c, p, None, "Z", s_mm=2.2), "pion c.o. (zasilanie/powrót rozdzielaczy)")

    def rozdzielacz(self):
        R = self.rozdz_xy.get(self.kid)
        r = self._rozdz(self.kid)
        if R is None or r is None:
            return
        e = next((e for e in self.W.dane.wyposazenie if str(e.get("kond")) == self.kid and "rozdzielacz" in
                  str(e.get("opis", "")).lower()), None)
        rot = float(e.get("obrot", 90.0)) - 90.0 if e else 0.0
        n = int(max(r.get("sekcje") or [r["petle"]]))
        pitch = min(3.0, 36.0 / max(n, 1))
        d = dir_deg(rot)
        L = (min(n, 12) + 1) * pitch * self.k
        self.sym(S.manifold, R - d * L / 2, rot, n=min(n, 12), pitch_mm=pitch, label=None)
        sek = " + ".join(str(s) for s in (r.get("sekcje") or []))
        self.tag(R, [f"R-{self.kid}: rozdzielacz ogrzewania podłogowego {r['petle']} obiegów "
                     f"({r['rozdzielacze']} szt.: {sek})",
                     f"Σṁ = {num(r['m_kgh'], 0)} kg/h, ∆p_max pętli = {num(r['dp_max'], 1)} kPa; przepływomierze, "
                     "siłowniki 230 V, listwa sterująca, szafka podtynkowa"], "S-OPISY", style="bold")
        if self.kid == self.kids[0] and getattr(self, "mod_xy", None) is not None:
            path = self.g.route(self.mod_xy, R, "PCR0")
            self.pipe(path, "Z", layer="S-PC")
            self.g.mark(path, "PCR0")
            self.label(path, f"Z/P {rura_dla(r['m_kgh'])}", "S-OPISY")
        self.leg.sym(lambda c, p: S.manifold(c, p - np.array([7.5, 0.0]), 0.0, n=4, label=None),
                     "R — rozdzielacz ogrzewania podłogowego z przepływomierzami i siłownikami")

    def opisy(self):
        og = self.W.ogrzewanie
        d = og.do_dict()
        self.notes += [
            "Ogrzewanie podłogowe niskotemperaturowe wg PN-EN 1264-1…5; obciążenie cieplne pomieszczeń wg PN-EN 12831-1 "
            f"({og.phi_zrodlo}); θ_V,des = {num(og.theta_V, 1)} °C, σ ≤ 5 K; rury PE-X/Al/PE-X 16×2 (lub równoważne) "
            "na płycie systemowej z izolacją; regulacja pomieszczeniowa — termostaty i siłowniki (WT § 135 ust. 7).",
            "Strefy pętli (obszar, rozstaw T, długość L) z obliczeń lamela.obliczenia.sanitarne.ogrzewanie; granice "
            "stref i przebieg przyłączy pętli wyznaczono algorytmicznie (podział pomieszczenia na pasy o równych "
            "polach, przyłącza ortogonalnie od rozdzielacza) — do uściślenia w projekcie wykonawczym dostawcy systemu.",
            f"Źródło ciepła: PC powietrze–woda R290 (W-155), θ_biv = {num(d['theta_biv'], 1)} °C, SCOP {num(d['SCOP_dekl'], 1)}; "
            f"bufor ≥ {d['bufor_l']} dm³, NW c.o. {d['naczynie_co_l']} dm³, NW c.w.u. {d['naczynie_cwu_l']} dm³ "
            "(obliczenia) — dane PC przykładowe, zastąpić DTR wybranego wyrobu (lub równoważnego).",
            "Próba szczelności instalacji ogrzewania podłogowego wg PN-EN 1264-4 (przed wylaniem jastrychu, "
            "ciśnienie 1,5 × p_rob ≥ 6 bar); wygrzewanie jastrychu wg PN-EN 1264-4.",
        ]
        bad = [w for w in og.warunki if w.ok is False]
        for w in bad[:5]:
            self.notes.append(f"SPRAWDZENIE NIESPEŁNIONE (obliczenia): {w.opis} ({w.podstawa}) — dogrzewanie "
                              "(np. grzejnik łazienkowy elektryczny) lub zmniejszenie T/zwiększenie θ_V do analizy.")
        if bad:
            self.brak("Ogrzewanie — pomieszczenia z niedoborem mocy podłogi", "; ".join(w.opis for w in bad[:6]),
                      "wyposazenie.yaml: {typ: grzejnik, xy, obrot, moc_W} (grzejnik łazienkowy) lub decyzja projektowa")
        rows = [[f"{p.pom}/{p.nr}", num(100 * p.T, 0), num(p.L, 1), num(p.m_kgh, 0), num(p.dp, 1)]
                for p in og.petle if (self.m.pomieszczenie(p.pom) and self.m.pomieszczenie(p.pom).kond == self.kid)]
        self.res.column_blocks.append(("petle", table_block(
            f"PĘTLE OGRZEWANIA PODŁOGOWEGO — {self.kid} (PN-EN 1264)",
            [("Pętla", 30), ("T [cm]", 22), ("L [m]", 22), ("ṁ [kg/h]", 26), ("∆p [kPa]", 26)], rows,
            align=["left", "right", "right", "right", "right"])))
