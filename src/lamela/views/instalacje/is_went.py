"""IS-WM — wentylacja mechaniczna nawiewno-wywiewna z odzyskiem ciepła: centrala, kanały SUP/ETA (drzewo od pionu
wentylacyjnego do nawiewników/wywiewników), anemostaty z wydatkami [m³/h], czerpnia (ODA) i wyrzutnia (EHA).

Dane: bilans wentylacji ``lamela.obliczenia.energia.wentylacja`` (strumienie pomieszczeń, centrala) — w razie braku
pola ``went`` pomieszczeń modelu; położenie centrali (``wyposazenie.yaml``: rekuperator), czerpni i wyrzutni
(``instalacje.yaml`` / ``energia.wentylacja``). Średnice kanałów dobrane w generatorze: D = √(4·q/(π·v)),
v ≤ 2,5 m/s (odgałęzienia) / 3,5 m/s (pnie), szereg 75/90/100/125/160/200/250 mm."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point

from ...draft import fmt, symbols as S
from ...draft.dims import arrowhead
from ...draft.geom import dir_deg
from ..common import label_point
from .baza import Rysunek
from .is_co import paski
from .wspolne import BRAK, H_S, num, table_block

SZEREG = (75, 90, 100, 125, 160, 200, 250, 315)


def srednica(q_m3h: float, v: float) -> int:
    d = math.sqrt(4 * q_m3h / 3600.0 / (math.pi * v)) * 1000.0
    return next((s for s in SZEREG if s >= d - 1e-6), SZEREG[-1])


def terminal(c, pos, kind="N", r_mm=2.2, layer="S-WENT"):
    """Anemostat / zawór wentylacyjny (okrąg z okręgiem wewnętrznym; strzałki na zewnątrz — nawiew, do środka —
    wywiew)."""
    k = c.k
    P = np.asarray(pos, float)
    R = r_mm * k
    c.fill(__import__("lamela.draft.geom", fromlist=["circle_pts"]).circle_pts(P, R, 36), layer, "#ffffff", z=23.5)
    c.circle(P, R, layer, pen="srednia", lt="CIAGLA", z=23.6)
    c.circle(P, R * 0.45, layer, pen="b_cienka", lt="CIAGLA", z=23.6)
    for a in (45, 135, 225, 315):
        v = dir_deg(a)
        if kind == "N":
            a0, a1 = P + v * R * 0.5, P + v * R * 1.45
        else:
            a0, a1 = P + v * R * 1.55, P + v * R * 0.6
        c.line(a0, a1, layer, pen="b_cienka", lt="CIAGLA", z=23.6)
        arrowhead(c, a1, a1 - a0, 1.0, 16, True, layer, pen="b_cienka")


class RysWM(Rysunek):
    kod = "IS-WM"

    def run(self):
        W = self.W
        self.podklad(meble=False)
        self.siatka(extra_pts=[], przy_scianie=0.6)
        self.went = self._strumienie()
        rek = next((e for e in W.dane.wyposazenie if e.get("typ") == "rekuperator"), None)
        self.rek = rek
        self.rek_kid = str(rek.get("kond")) if rek else self.kids[-1]
        self.rek_xy = (np.asarray(rek["xy"], float) + dir_deg(float(rek.get("obrot", 90))) *
                       float((rek.get("wym") or [1.2, 0.7])[1]) / 2) if rek else None
        self.leg.line("S-WENT", "SUP — powietrze nawiewane (kanały okrągłe, izolowane w przestrzeniach "
                      "nieogrzewanych)", lt="CIAGLA", pen="srednia")
        self.leg.line("S-WENT", "ETA — powietrze wywiewane", lt="KRESKOWA", pen="srednia")
        self.pion = self._pion()
        self.terminale()
        if self.kid == self.rek_kid and self.rek_xy is not None:
            self.centrala()
        self.opisy()
        self.room_extra = {}
        for rid, (n, w) in self.went.items():
            s = []
            if n:
                s.append(f"N {num(n, 0)}")
            if w:
                s.append(f"W {num(w, 0)}")
            if s:
                self.room_extra[rid] = [" / ".join(s) + " m³/h"]
        return self.finish()

    # --------------------------------------------------------------------------------------------- dane
    def _strumienie(self) -> dict:
        ew = self.W.energia_went
        out = {}
        if ew is not None:
            for p in ew.pomieszczenia:
                out[p.id] = (float(p.naw or 0.0), float(p.wyw or 0.0))
        else:
            for rid, v in (self.W.wentylacja.get("pom") or {}).items():
                out[rid] = (float(v.get("naw", 0.0)), float(v.get("wyw", 0.0)))
        return out

    def _pion(self):
        """Pion wentylacyjny (SUP + ETA) — model nie zawiera szachtu wentylacyjnego: punkt przy ścianie w
        pomieszczeniach komunikacji/pomocniczych wszystkich kondygnacji, najbliżej centrali (algorytm)."""
        c = getattr(self.ctx, "_inst_went_pion", None)
        if c is not None:
            return c
        ref = self.rek_xy if self.rek_xy is not None else np.array([0.0, 0.0])
        walls = self.sciany_union(self.kids)
        best = None
        ok_cat = ("ruchu", "pomocnicza", "techniczna")
        import shapely
        X, Y = np.meshgrid(np.arange(ref[0] - 6.0, ref[0] + 6.0, 0.1), np.arange(ref[1] - 6.0, ref[1] + 8.0, 0.1))
        D = shapely.distance(walls, shapely.points(X.ravel(), Y.ravel()))
        for x, y, dw in zip(X.ravel(), Y.ravel(), D):
            if dw < 0.14 or dw > 0.30:
                continue
            if True:
                P = Point(x, y)
                good = True
                for kid in self.kids:
                    r = next((r for r in self.m.pomieszczenia(kid) if r.polygon is not None and r.polygon.contains(P)),
                             None)
                    if r is None or r.kategoria not in ok_cat or "szacht" in r.nazwa.lower():
                        good = False
                        break
                if not good:
                    continue
                sc = abs(x - ref[0]) + abs(y - ref[1])
                if best is None or sc < best[0]:
                    best = (sc, np.array([x, y]))
        pos = best[1] if best else ref
        pp = self.pion_punkty("WENT", pos, self.kids, n=2, step=0.22)
        self.ctx._inst_went_pion = pp
        return pp

    # --------------------------------------------------------------------------------------------- nawiewniki / wywiewniki
    def _punkty(self, r, n, w):
        pg = r.polygon.buffer(-0.45, join_style=2)
        if pg.is_empty:
            pg = r.polygon.buffer(-0.15, join_style=2)
        if pg.is_empty:
            return []
        from ...draft.geom import polygons_of
        pg = max(polygons_of(pg), key=lambda g: g.area)
        out = []
        parts = paski(pg, 2) if (n > 0 and w > 0) else [pg]
        if n > 0 and w > 0:
            fx = [np.asarray(e["xy"], float) for e in self.W.dane.wyposazenie if str(e.get("kond")) == self.kid and
                  e.get("typ") in ("zlew", "plyta", "wc", "prysznic", "wanna") and r.polygon.buffer(0.3).contains(
                      Point(e["xy"]))]
            if fx:
                cf = np.mean(fx, axis=0)
                parts.sort(key=lambda g: -g.distance(Point(cf)))
        kinds = ([("N", n)] if n > 0 else []) + ([("W", w)] if w > 0 else [])
        for (kind, q), part in zip(kinds, parts):
            cnt = max(1, int(math.ceil(q / 50.0 - 1e-9)))
            for sub in paski(part, cnt):
                out.append((kind, q / cnt, label_point(sub), r))
        return out

    def terminale(self):
        vp = self.vp
        pts = []
        for r in self.m.pomieszczenia(self.kid):
            n, w = self.went.get(r.id, (0.0, 0.0))
            if (n > 0 or w > 0) and r.polygon is not None:
                pts += self._punkty(r, n, w)
        i = self.kids.index(self.kid)
        irek = self.kids.index(self.rek_kid)
        below = [k for k in self.kids if self.kids.index(k) <= i]
        tot = {"N": 0.0, "W": 0.0}
        for rid, (n, w) in self.went.items():
            rr = self.m.pomieszczenie(rid)
            if rr is not None and rr.kond in below:
                tot["N"] += n
                tot["W"] += w
        for kind, med, key, rp in (("N", "SUP", "SUP", self.pion[0]), ("W", "ETA", "ETA", self.pion[1])):
            lst = [t for t in pts if t[0] == kind]
            for t in lst:
                self.sym(terminal, t[2], kind)
            lst.sort(key=lambda t: -(abs(t[2][0] - rp[0]) + abs(t[2][1] - rp[1])))
            first = True
            for kk, q, c, r in lst:
                if first:
                    path = self.g.route(rp, c, key, other=3.0, reuse=0.3)
                    first = False
                else:
                    path = self.g.route(c, None, key, other=3.0, reuse=0.3, targets=self.g.occ[key])
                self.pipe(path, med, pen="srednia")
                self.g.mark(path, key)
                d = max(100, srednica(q, 2.5))
                self.tag(c, [f"{kk} {num(q, 0)} m³/h, Ø{d}"], "S-OPISY", radii=(4.0, 6.0, 9.0, 12.0))
            if i <= irek and tot[kind] > 0:
                self.sym(S.riser, rp, None, med, s_mm=3.4)
        if i <= irek:
            arrow = ("↑" if i < irek else "") + ("↓" if i > 0 else "")
            self.tag(self.pion[0], [f"{BRAK} pion wentylacyjny W1 (proponowany) {arrow}",
                                    f"SUP Ø{srednica(tot['N'], 3.5)} (Q = {num(tot['N'], 0)} m³/h), "
                                    f"ETA Ø{srednica(tot['W'], 3.5)} (Q = {num(tot['W'], 0)} m³/h)",
                                    "obudowa GK EI 30 / izolacja akustyczna"], "I-BRAKI", color="#b0008a",
                     style="bold")
            self.brak("Pion/szacht wentylacyjny (SUP, ETA)", "brak w modelu szachtu wentylacyjnego (szacht SI zajęty "
                      "przez piony wod.-kan. i deszczowe) — przyjęto lokalizację proponowaną algorytmicznie",
                      "pomieszczenia: {nazwa: 'Szacht wentylacyjny SW', wielobok} + instalacje.piony: [{id: W1, xy, "
                      "rodzaj: wentylacja, kond: [P0, P1, P2]}]")
        self.leg.sym(lambda c, p: terminal(c, p, "N"), "nawiewnik (anemostat/zawór nawiewny) — N, wydatek [m³/h], "
                     "średnica przyłącza")
        self.leg.sym(lambda c, p: terminal(c, p, "W"), "wywiewnik (zawór wywiewny) — W, wydatek [m³/h]")
        self.leg.sym(lambda c, p: S.riser(c, p, None, "SUP", s_mm=3.4), "pion wentylacyjny (kanał pionowy SUP/ETA)")
