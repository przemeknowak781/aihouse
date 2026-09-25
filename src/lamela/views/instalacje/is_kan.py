"""IS-K — rzut kanalizacji sanitarnej: podejścia (średnice, spadki), piony, czyszczaki, wentylacja pionów (wywiewki,
zawory napowietrzające), przewody odpływowe pod posadzką z rzędnymi dna, przykanalik i studzienka.

Dane: ``lamela.obliczenia.sanitarne.kanalizacja`` (piony, odcinki z DN, spadkami, rzędne, wentylacja, studzienka)."""
from __future__ import annotations


import numpy as np
from shapely.geometry import Point

from ...draft import fmt, symbols as S
from ...draft.dims import arrowhead
from ...draft.geom import dir_deg
from ...obliczenia.sanitarne.przybory import KATALOG
from .baza import Rysunek
from .trasy import Siatka
from .wspolne import num, table_block


def punkt_odplywu(p, rot):
    return np.asarray(p.xy, float) + dir_deg(rot) * 0.10


class RysK(Rysunek):
    kod = "IS-K"

    def run(self):
        W = self.W
        kn = W.kanalizacja
        self.podklad(meble=False)
        pts = [p.xy for p in kn.przybory if p.kond == self.kid] + [pn.xy for pn in kn.piony]
        self.siatka(extra_pts=pts)
        self.odc = {o.id: o for o in kn.odcinki}
        self.leg.line("S-KANAL", "Ks — kanalizacja sanitarna, podejścia i piony PP-HT (PN-EN 1451-1), średnica "
                      "nominalna wg obliczeń; i — spadek")
        self.piony_rys()
        self.podejscia()
        if self.kid == self.kids[0]:
            self.kolektor()
        self.opisy()
        self.braki_wspolne()
        return self.finish()

    # --------------------------------------------------------------------------------------------- piony
    def piony_rys(self):
        kn = self.W.kanalizacja
        i = self.kids.index(self.kid)
        went = {w["pion"]: w for w in kn.wentylacja}
        for pn in kn.piony:
            top = max(self.kids.index(k) for k in pn.kondygnacje)
            if i > top:
                continue
            q = np.asarray(pn.xy, float)
            o = self.odc.get(f"PION_{pn.id}")
            dn = o.dn if o else 100
            self.sym(S.riser, q, None, "KS", s_mm=3.2)
            arrow = ("↑" if i < top else "") + ("↓" if i > 0 else "")
            lines = [f"Pion {pn.id} Ø{o.rura.split()[-1] if o else dn} PP-HT {arrow}".strip()]
            if i == 0:
                self.sym(S.cleanout, q + np.array([0.16, -0.16]), 0.0, s_mm=2.4, label="")
                lines.append("czyszczak 1,0 m nad posadzką")
                if f"pion {pn.id}" in kn.rzedne:
                    lines.append(f"dno pod posadzką {fmt.level(kn.rzedne[f'pion {pn.id}'])}")
            w = went.get(pn.id)
            if i == top and w:
                if w.get("z_wylotu") is not None:
                    lines.append(f"wywiewka Ø{o.rura.split()[-1] if o else dn} ponad dach, wylot "
                                 f"{fmt.level(w['z_wylotu'])}")
                else:
                    lines.append("zawór napowietrzający (PN-EN 12380) — dostęp rewizyjny")
                    self.sym(S.tag, q + np.array([-0.2, 0.2]), "ZN", shape="circle", r_mm=1.8, h=1.8,
                             layer="S-KANAL")
                    self.leg.sym(lambda c, p: S.tag(c, p, "ZN", shape="circle", r_mm=1.8, h=1.8, layer="S-KANAL"),
                                 "ZN — zawór napowietrzający pionu (PN-EN 12380, montaż ponad podejściami)")
            self.tag(q, lines, "S-OPISY", style="bold", radii=(6.0, 9.0, 13.0, 18.0, 24.0))
        self.leg.sym(lambda c, p: S.riser(c, p, None, "KS", s_mm=3.2),
                     "pion kanalizacyjny; ↑ — prowadzony wyżej, ↓ — z kondygnacji wyższej/niższej")
        if i == 0:
            self.leg.sym(lambda c, p: S.cleanout(c, p, 0.0, s_mm=2.4, label=""),
                         "czyszczak (rewizja) na pionie, 1,0 m nad posadzką, z drzwiczkami rewizyjnymi")

    # --------------------------------------------------------------------------------------------- podejścia
    def podejscia(self):
        kn = self.W.kanalizacja
        for pn in kn.piony:
            for rid in pn.pomieszczenia.get(self.kid, []):
                lst = [p for p in pn.przybory if p.pom == rid and p.kond == self.kid]
                if not lst:
                    continue
                a = np.asarray(pn.xy, float)
                fx = [(p, punkt_odplywu(p, self.obrot(p.kond, p.xy))) for p in lst]
                fx.sort(key=lambda t: (-(KATALOG[t[0].typ].dn_kan or 0), abs(t[1][0] - a[0]) + abs(t[1][1] - a[1])))
                key = f"KS:{rid}"
                zb = self.odc.get(f"PZ_{rid}")
                trunk = self.g.route(a, fx[0][1], key, other=3.0)
                self.g.mark(trunk, key)
                dn0 = (zb.dn if zb else self.odc[fx[0][0].id].dn)
                self.pipe(trunk, "KS", pen="gruba" if dn0 >= 100 else "srednia")
                self._spadek(trunk[::-1], dn0, self.odc[fx[0][0].id].i or 0.02)
                for p, q in fx:
                    o = self.odc.get(p.id)
                    if p is not fx[0][0]:
                        path = self.g.route(q, None, key, other=3.0, targets=self.g.occ[key])
                        self.g.mark(path, key)
                        self.pipe(path, "KS", pen="gruba" if (o and o.dn >= 100) else "srednia")
                    if p.typ.startswith("wpust"):
                        self.sym(S.floor_drain, q, 0.15, layer="S-KANAL", label=None)
                        self.leg.sym(lambda c, pp: S.floor_drain(c, pp, 3.0, layer="S-KANAL", label=None),
                                     "wpust podłogowy z syfonem (zamknięcie wodne ≥ 50 mm)")
                    if o is not None:
                        self.tag(q, [f"Ø{o.rura.split()[-1]}"], "S-OPISY", radii=(3.5, 5.5, 8.0, 11.0), n_ang=16)

    def _spadek(self, path, dn, i):
        """Opis podejścia zbiorczego (średnica, spadek) + grot kierunku przepływu na najdłuższym odcinku."""
        P = np.asarray(path, float)
        if len(P) < 2:
            return
        j = max(range(len(P) - 1), key=lambda j: float(np.hypot(*(P[j + 1] - P[j]))))
        A, B = P[j], P[j + 1]
        L = float(np.hypot(*(B - A)))
        if L > 6.0 * self.k:
            n0 = len(self.vp.prims)
            arrowhead(self.vp, A + (B - A) * 0.62, B - A, 2.2, 14, True, "S-KANAL")
            self.reg(n0)
        rura = next((o.rura for o in self.W.kanalizacja.odcinki if o.dn == dn), f"{dn}")
        self.label(P, f"Ks Ø{rura.split()[-1]}, i = {num(100 * i, 1)} %", "S-OPISY")
        self.leg.sym(lambda c, p: arrowhead(c, p + np.array([3.0, 0.0]), np.array([1.0, 0.0]), 2.2, 14, True,
                                            "S-KANAL"), "kierunek przepływu (spadek przewodu)")

    # --------------------------------------------------------------------------------------------- pod posadzką
    def kolektor(self):
        from shapely.ops import nearest_points
        kn = self.W.kanalizacja
        vp = self.vp
        st = kn.studzienka or {}
        s_xy = np.asarray(st.get("xy", (0.0, 0.0)), float)
        ob = self.W.dane.obrysy.get(self.kids[0]) or self.pod.outline
        E = nearest_points(ob.exterior, Point(*s_xy))[0]
        E = np.array([E.x, E.y])
        x0, y0, x1, y1 = ob.bounds
        g2 = Siatka((min(x0, s_xy[0]) - 2, min(y0, s_xy[1]) - 2, max(x1, s_xy[0]) + 2, max(y1, s_xy[1]) + 2))
        kol = sorted(kn.piony, key=lambda p: -(abs(p.xy[0] - E[0]) + abs(p.xy[1] - E[1])))
        kols = [o for o in kn.odcinki if o.rodzaj == "poziom"]
        for i, pn in enumerate(kol):
            nxt = np.asarray(kol[i + 1].xy, float) if i + 1 < len(kol) else E
            path = g2.route(np.asarray(pn.xy, float), nxt, "KOL", reuse=0.3, turn=1.5, margin=4.0)
            g2.mark(path, "KOL")
            self.pipe(path, "KS", pen="gruba", lt="KRESKOWA")
            o = kols[i] if i < len(kols) else None
            if o is not None:
                self.label(path, f"{o.rura}, i = {num(100 * (o.i or 0.02), 1)} % (pod płytą)", "S-OPISY")
        prz = next((o for o in kn.odcinki if o.rodzaj == "przykanalik"), None)
        path = [E, np.array([E[0], s_xy[1]]), s_xy] if abs(E[0] - s_xy[0]) > 0.02 else [E, s_xy]
        d = s_xy - np.asarray(path[-2], float)
        dl = float(np.hypot(*d)) or 1.0
        path[-1] = s_xy - d / dl * 0.2125
        self.pipe(path, "KS", pen="gruba", lt="KRESKOWA")
        n0 = len(vp.prims)
        vp.circle(s_xy, 0.2125, "S-KANAL", pen="srednia")
        vp.circle(s_xy, 0.16, "S-KANAL", pen="b_cienka")
        self.reg(n0)
        if prz is not None:
            self.label(path, f"przykanalik {prz.rura}, i = {num(100 * prz.i, 1)} %", "S-OPISY")
        self.tag(s_xy, [f"Studzienka rewizyjna SR1: {st.get('typ', 'PP DN425')}",
                        f"dno wlotu {fmt.level(st.get('dno', 0.0))}, teren {fmt.level(st.get('teren', 0.0))}; "
                        f"dalej do sieci wg PZT"], "S-OPISY", style="bold")
        rz = kn.rzedne.get("wyjście z budynku")
        if rz is not None:
            self.tag(E, [f"wyjście z budynku: dno {fmt.level(rz)}", "przejście szczelne przez płytę (tuleja)"],
                     "S-OPISY")
        self.leg.line("S-KANAL", "przewody odpływowe pod płytą fundamentową i przykanalik PVC-U SN8 "
                      "(PN-EN 1401-1) — linia kreskowa", lt="KRESKOWA", pen="gruba")
        self.leg.sym(lambda c, p: (c.circle(p, 3.0, "S-KANAL", pen="srednia"), c.circle(p, 2.2, "S-KANAL",
                                                                                          pen="b_cienka")),
                     "studzienka rewizyjna (tworzywowa DN425)")

    # --------------------------------------------------------------------------------------------- opisy
    def opisy(self):
        kn = self.W.kanalizacja
        d = kn.do_dict()
        self.notes += [
            "Kanalizacja sanitarna wg PN-EN 12056-1, -2 (system I), -5 i WT § 122–124; obliczenia: lamela.obliczenia."
            "sanitarne.kanalizacja (K = 0,5; ΣDU, Q_ww, napełnienia, wentylacja pionów).",
            "Podejścia i piony: PP-HT (PN-EN 1451-1) lub równoważne; pod płytą i przykanalik: PVC-U SN8 lity "
            "(PN-EN 1401-1). Spadki podejść ≥ 2 %, przewodów pod płytą 2 % (≤ DN100).",
            "Trasy podejść wyznaczono algorytmicznie (ortogonalnie, przy ścianach, do pionów w szachcie SI) — "
            "średnice i spadki z obliczeń; przebieg do weryfikacji na budowie.",
            "Czyszczaki na pionach w najniższej kondygnacji 1,0 m nad posadzką; rewizje w studzience SR1. Piony w "
            "szachcie izolowane akustycznie, przejścia przez stropy z opaskami/kołnierzami ppoż. wg klasy stropu.",
            "Odpływ skroplin PC i zmywarki przez syfon; wpusty podłogowe z zamknięciem wodnym ≥ 50 mm.",
        ]
        if self.kid == self.kids[0]:
            rows = [[o.id, o.opis[:44], f"Ø{o.rura.split()[-1]}", num(o.L, 2), num(o.sum_DU, 1), num(o.Q, 2),
                     (num(100 * o.i, 1) if o.i else "—")] for o in kn.odcinki
                    if o.rodzaj in ("pion", "poziom", "przykanalik", "podejscie_zbiorcze")]
            self.res.column_blocks.append(("kan", table_block(
                "WYNIKI OBLICZEŃ — KANALIZACJA (PN-EN 12056-2)",
                [("Odcinek", 18), ("Opis", 74), ("DN", 16), ("L [m]", 16), ("ΣDU", 14), ("Q [l/s]", 18),
                 ("i [%]", 14)], rows, align=["left", "left", "center", "right", "right", "right", "right"])))
            self.notes.append(f"ΣDU = {num(d['sum_DU'], 1)} l/s, Q_ww = {num(d['Q_ww_l_s'], 2)} l/s; przykanalik "
                              f"{d.get('przykanalik', '')}.")
