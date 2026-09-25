"""IS-K — rzut kanalizacji sanitarnej: podejścia (średnice, spadki), piony, czyszczaki, wentylacja pionów (wywiewki,
zawory napowietrzające), przewody odpływowe pod posadzką z rzędnymi dna, przykanalik i studzienka.

Dane: ``lamela.obliczenia.sanitarne.kanalizacja`` (piony, odcinki z DN, spadkami, rzędne, wentylacja, studzienka)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point

from ...draft import dims, fmt, symbols as S
from ...draft.dims import arrowhead
from ...draft.geom import circle_pts, dir_deg
from ...obliczenia.sanitarne.przybory import KATALOG
from .baza import Rysunek
from .trasy import Siatka
from .wspolne import H_S, num, table_block


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
