"""IS-W — rzut instalacji wodociągowej: woda zimna (Wz), ciepła (Wc), cyrkulacja (Cyrk), zestaw wodomierzowy,
rozdzielacze w pomieszczeniu technicznym, zasobnik c.w.u., piony, zawory, podejścia do przyborów.

Dane: sieć węzłów i odcinków z ``lamela.obliczenia.sanitarne.woda`` (średnice, przepływy, wodomierz, zasobnik,
cyrkulacja, izolacje) + położenia przyborów z ``wyposazenie.yaml``/``instalacje.yaml``. Trasy — algorytm
``trasy.Siatka`` (model nie zawiera przebiegów przewodów)."""
from __future__ import annotations

import math
import re

import numpy as np

from ...draft import symbols as S
from ...draft.geom import dir_deg, perp
from ...obliczenia.sanitarne.woda import RURY_WIELOWARSTWOWE, dobierz_rure
from .baza import Rysunek
from .wspolne import num, rura_krotko, table_block

OFF = {"ZW": np.array([-0.10, 0.16]), "CWU": np.array([0.03, 0.16]), "CYRK": np.array([0.16, 0.16])}
MED = {"ZW": "WZ", "CWU": "WC", "CYRK": "CYRK"}
SKROT = {"ZW": "Wz", "CWU": "Wc", "CYRK": "Cyrk"}


def punkt_przyboru(p, rot: float, medium: str) -> np.ndarray:
    """Punkt podłączenia: 0,08 m od lica ściany; c.w.u. po lewej stronie armatury (WT §120 ust. 5), woda zimna
    po prawej (±0,07 m wzdłuż ściany)."""
    d = dir_deg(rot)
    t = perp(d)                      # w lewo patrząc od ściany do pomieszczenia
    q = np.asarray(p.xy, float) + d * 0.08
    if p.t.qn_cw > 0 and p.t.qn_zw > 0:
        q = q + (t * 0.07 if medium == "ZW" else -t * 0.07)
    return q


class RysW(Rysunek):
    kod = "IS-W"

    def run(self):
        W = self.W
        wo = W.woda
        self.podklad(meble=False)
        k0 = self.kids[0]
        wz = wo.wezly
        on = {n for n, v in wz.items() if v[3] == self.kid}
        pts = [v[:2] for n, v in wz.items() if n in on]
        self.siatka(extra_pts=pts, nieogrzewane=4.0)
        avoid = [np.asarray(x.get("xy"), float) for x in (W.dane.inst.get("piony_deszczowe") or []) if x.get("xy")]
        avoid += [np.asarray(pn.xy, float) for pn in W.kanalizacja.piony]
        self.ppos = {}
        for pn in wo.piony:
            top = max(self.kids.index(k) for k in pn.kondygnacje)
            pp = self.pion_punkty(pn.id, pn.xy, self.kids[:top + 1], 3, avoid=avoid)
            self.ppos[pn.id] = dict(zip(("ZW", "CWU", "CYRK"), pp))
        self.cyrk = wo.cwu.get("cyrkulacja", "brak") != "brak"
        q_c = float(wo.cwu.get("V_cyrk_dm3h", 0.0)) / 3600.0
        r = dobierz_rure(q_c, 0.5, RURY_WIELOWARSTWOWE, 16) if self.cyrk else None
        self.cyrk_rura = f"{r[0]}×{num(r[1], 1)}" if r else ""
        self.przyb = {p.id: p for p in wo.przybory}
        self.piony = {pn.id: pn for pn in wo.piony}
        self.leg.line("S-WODA", "Wz — woda zimna (PE-RT/Al/PE-RT lub równoważne), średnica d_z×s wg obliczeń",
                      lt=None)
        self.leg.line("S-CWU", "Wc — ciepła woda użytkowa (c.w.u.), izolowana wg WT zał. 2 pkt 1.5", lt="KRESKOWA")
        if self.cyrk:
            self.leg.line("S-CYRK", f"Cyrk — cyrkulacja c.w.u. {self.cyrk_rura} (praca czasowa)", lt="PUNKTOWA_KROTKA")
        self.pos = {}
        if self.kid == k0:
            self.urzadzenia()
        self.mains()
        self.pionowe()
        self.pomieszczenia()
        self.opisy()
        self.room_extra = {}
        self.braki_wspolne()
        zas_m = next((e for e in W.dane.wyposazenie if e.get("typ") == "zasobnik" and "cwu" in str(e.get("opis", "")).lower()),
                     None)
        mm = re.search(r"(\d+)\s*dm", str((zas_m or {}).get("opis", "")))
        if mm and int(mm.group(1)) != int(wo.cwu["V_zas"]):
            self.brak("Zasobnik c.w.u. — pojemność", f"wyposazenie.yaml: {mm.group(1)} dm³, obliczenia (PN-EN 12831-3 / "
                      f"zapotrzebowanie): {wo.cwu['V_zas']} dm³ — na rysunku wartość z obliczeń",
                      "wyposazenie: {typ: zasobnik, V_dm3: 400, …} lub instalacje.wyroby.zasobnik")
        return self.finish()

    # --------------------------------------------------------------------------------------------- węzły
    def xy(self, name: str, medium: str) -> np.ndarray:
        wz = self.W.woda.wezly
        m = re.match(r"^(.+?)([ZC])@(P\w+)$", name)
        if m:                                        # węzeł pionu
            return self.ppos[m.group(1)]["ZW" if m.group(2) == "Z" else "CWU"]
        m = re.match(r"^([A-Z]{3}\d{2})([ZC])$", name)
        if m and m.group(1) in self.przyb:
            p = self.przyb[m.group(1)]
            return punkt_przyboru(p, self.obrot(p.kond, p.xy), "ZW" if m.group(2) == "Z" else "CWU")
        if name in self.przyb:
            p = self.przyb[name]
            return punkt_przyboru(p, self.obrot(p.kond, p.xy), "ZW")
        if name in self.pos:
            return self.pos[name]
        return np.asarray(wz[name][:2], float)

    # --------------------------------------------------------------------------------------------- urządzenia
    def urzadzenia(self):
        W, vp = self.W, self.vp
        wo = W.woda
        wz = wo.wezly
        wod = np.asarray(wz["WOD"][:2], float)
        t0 = np.asarray(wz["T0"][:2], float)
        wej = np.asarray(wz["WEJ"][:2], float)
        siec = np.asarray(wz["SIEC"][:2], float)
        # rozdzielacz Wz (T0) — 0,35 m od wodomierza w głąb pomieszczenia technicznego
        tech = self.room_at(wod)
        c = np.asarray(tech.polygon.centroid.coords[0]) if tech is not None else t0
        d = c - wod
        d = np.array([np.sign(d[0]) or 1.0, 0.0]) if abs(d[0]) >= abs(d[1]) else np.array([0.0, np.sign(d[1]) or 1.0])
        self.pos["WOD"] = wod
        self.pos["T0"] = wod + d * 0.45
        # przyłącze: trasa z dzialka.yaml (uzbrojenie projektowane) w obrębie 2 m od budynku, dalej wg PZT
        prz = next((o for o in wo.odcinki if o.typ == "przylacze"), None)
        linie = self.linie_dzialki("woda")
        outl = self.pod.outline
        if linie and outl is not None and not outl.is_empty:
            from shapely.geometry import LineString
            ln = LineString(linie[0][0])
            part = ln.intersection(outl.buffer(2.0, join_style=2))
            seg = max((np.asarray(g.coords) for g in getattr(part, "geoms", [part]) if not g.is_empty),
                      key=lambda a: len(a), default=None)
            if seg is not None and len(seg) >= 2:
                if outl.distance(__import__("shapely").geometry.Point(seg[0])) < outl.distance(
                        __import__("shapely").geometry.Point(seg[-1])):
                    seg = seg[::-1]
                if outl.contains(__import__("shapely").geometry.Point(seg[0])):
                    seg = seg[::-1]
                out, inner = seg[0], seg[-1]
                self.pipe(seg, "WZ", pen="gruba")
                path = self.g.route(inner, wod, "ZW:WEJ")
                self.pipe(path, "WZ", pen="gruba")
                self.g.mark(path, "ZW:WEJ")
                u = seg[0] - seg[1]
                u = u / (np.hypot(*u) or 1.0)
                wej = inner
            else:
                linie = []
        if not linie:
            u = siec - wej
            u = np.array([0.0, np.sign(u[1])]) if abs(u[1]) >= abs(u[0]) else np.array([np.sign(u[0]), 0.0])
            out = wej + u * 1.8
            path = self.g.route(wej, wod, "ZW:WEJ")
            self.pipe([out, wej], "WZ", pen="gruba")
            self.pipe(path, "WZ", pen="gruba")
            self.g.mark(path, "ZW:WEJ")
            self.brak("Przyłącze wodociągowe", "brak trasy przyłącza w dzialka.yaml (uzbrojenie.projektowane, branza: woda)"
                      " — narysowano odcinek do sieci wg obliczeń", "uzbrojenie: {projektowane: [{branza: woda, linia: "
                      "[[x,y],…], opis, dl}]}")
        n0 = len(vp.prims)
        from ...draft.dims import arrowhead
        arrowhead(vp, out, -u, 2.5, 12, True, "S-WODA")
        self.reg(n0)
        if prz is not None:
            self.tag(out, [f"Przyłącze wodociągowe {prz.rura}, L = {num(prz.L, 1)} m",
                           "z sieci — trasa i rzędne wg PZT; pod płytą w rurze osłonowej, przejście szczelne"],
                     "S-OPISY", style="bold")
        # zestaw wodomierzowy
        self.sym(S.water_meter, wod, 0.0, s_mm=4.0, label="WM")
        seg = self.g.route(wod, self.pos["T0"], "ZW:T0")
        self.pipe(seg, "WZ", pen="gruba")
        wm = wo.wodomierz
        ur = wo.urzadzenia
        self.tag(wod, [f"Zestaw wodomierzowy DN{ur.get('DN_arm', wm['DN'])}: ZO – F – WM – EA – RED – ZO",
                       f"wodomierz DN{wm['DN']}, Q3 = {num(wm['Q3'], 1)} m³/h (q = {num(wm['q'], 2)} dm³/s, "
                       f"∆p = {num(wm['dp'], 0)} kPa)",
                       f"zawór antyskażeniowy EA DN{ur.get('DN_arm', 25)} (PN-EN 1717), reduktor "
                       f"{num(0.40, 2)} MPa, filtr"], "S-OPISY", style="bold")
        self.leg.sym(lambda c, p: S.water_meter(c, p, 0.0, s_mm=4.0, label="WM"),
                     "WM — zestaw wodomierzowy: zawory odcinające (ZO), filtr (F), wodomierz, zawór antyskażeniowy "
                     "EA (PN-EN 1717), reduktor ciśnienia (RED)")
        # rozdzielacz Wz
        self.sym(S.manifold, self.pos["T0"] - np.array([0.0, 0.03]), 0.0, n=3, label=None)
        self.leg.sym(lambda c, p: S.manifold(c, p - np.array([6.0, 0.0]), 0.0, n=3, label=None),
                     "rozdzielacz wody z zaworami odcinającymi na odejściach (pom. techniczne)")
        # zasobnik c.w.u., TZM, pompa cyrkulacyjna
        zas = np.asarray(wz["ZAS"][:2], float)
        self.pos["ZAS"] = zas
        dz = next((float(e["wym"][0]) for e in W.dane.wyposazenie if e.get("typ") == "zasobnik"
                   and abs(e["xy"][0] - zas[0]) < 0.3), 0.7)
        self.sym(S.tank, zas, d=dz, label="")
        self.tag(zas, [f"Zasobnik c.w.u. {wo.cwu['V_zas']} dm³ (obl.)", f"wężownica ≥ {num(wo.cwu['A_wez'], 1)} m², "
                       f"grzałka (dezynfekcja 70 °C)", "grupa bezpieczeństwa 6 bar + NW c.w.u."], "S-OPISY",
                 style="bold")
        self.leg.sym(lambda c, p: S.tank(c, p, d=7.0, label=""), "zasobnik c.w.u. / bufor (rzut, wymiar rzeczywisty)")

    # --------------------------------------------------------------------------------------------- przewody
    def _seg_floor(self, o):
        wz = self.W.woda.wezly
        return wz[o.od][3] == self.kid and wz[o.do][3] == self.kid

    def _route_pipe(self, a, b, med, key, companion=None, pen=None, targets=None):
        path = self.g.route(a, b, key, other=2.5, companion=companion, targets=targets)
        self.pipe(path, MED[med], pen=pen)
        self.g.mark(path, key)
        return path

    def _valve(self, path, dist=0.3):
        P = np.asarray(path, float)
        acc = 0.0
        for a, b in zip(P[:-1], P[1:]):
            L = float(np.hypot(*(b - a)))
            if acc + L >= dist and L > 1e-6:
                q = a + (b - a) * (dist - acc) / L
                ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                self.sym(S.valve, q, ang, s_mm=2.4, kind="kulowy")
                self.leg.sym(lambda c, p: S.valve(c, p, 0.0, s_mm=3.0, kind="kulowy"),
                             "zawór odcinający kulowy (na odejściach z rozdzielaczy i odgałęzieniach do pomieszczeń)")
                return q
            acc += L
        return None

    def mains(self):
        wo = self.W.woda
        mains = [o for o in wo.odcinki if self._seg_floor(o) and o.od in ("T0", "ZAS")]
        mains.sort(key=lambda o: -o.L)
        drawn_valve = False
        for o in mains:
            med = o.medium
            a = self.xy(o.od, med)
            b = self.xy(o.do, med)
            comp = None
            if med == "CWU":
                comp = "ZW:" + re.sub(r"C@", "Z@", o.do)
            path = self._route_pipe(a, b, med, f"{med}:{o.do}", companion=comp, pen="gruba" if o.typ == "glowny"
                                    else None)
            if o.do != "ZAS":
                self._valve(path, 0.3)
                drawn_valve = True
            opis = f"{SKROT[med]} {rura_krotko(o.rura)}"
            self.label(path, opis, "S-OPISY" if med == "ZW" else "S-OPISY", color=None)
            m = re.match(r"^(.+?)C@", o.do)
            if med == "CWU" and self.cyrk and m:
                pn = self.piony[m.group(1)]
                c = self.ppos[pn.id]["CYRK"]
                pc = self._route_pipe(b * 0 + a + np.array([0.12, 0.0]), c, "CYRK", f"CYRK:{pn.id}",
                                      companion=f"CWU:{o.do}")
                self.label(pc, f"Cyrk {self.cyrk_rura}", "S-OPISY")
        if drawn_valve:
            self.leg.sym(lambda c, p: S.valve(c, p, 0.0, s_mm=3.0, kind="kulowy"),
                         "zawór odcinający kulowy (na odejściach z rozdzielaczy i odgałęzieniach do pomieszczeń)")
        if self.cyrk and self.kid == self.kids[0] and "ZAS" in self.pos:
            q = self.pos["ZAS"] + np.array([0.12, -0.45])
            self.sym(S.pump, q, 90.0, s_mm=3.0)
            self.tag(q, [f"pompa cyrkulacyjna c.w.u. — {num(self.W.woda.cwu['V_cyrk_dm3h'], 0)} dm³/h, praca czasowa "
                         f"{num(self.W.woda.cwu['h_cyrk'], 0)} h/d, TZM na wyjściu c.w.u."], "S-OPISY")
            self.leg.sym(lambda c, p: S.pump(c, p, 0.0, s_mm=3.0), "pompa cyrkulacyjna (kierunek tłoczenia)")

    def pionowe(self):
        wo = self.W.woda
        i = self.kids.index(self.kid)
        for pn in wo.piony:
            top = max(self.kids.index(k) for k in pn.kondygnacje)
            if i > top or top == 0:          # pion jednokondygnacyjny = węzeł podłączenia (bez symbolu pionu)
                continue
            lines = [f"Pion {pn.id}"]
            has_c = any(p.t.qn_cw > 0 for p in pn.przybory)
            for med in ("ZW", "CWU", "CYRK"):
                if med == "CWU" and not has_c:
                    continue
                if med == "CYRK" and (not has_c or not self.cyrk):
                    continue
                self.sym(S.riser, self.ppos[pn.id][med], None, MED[med], s_mm=2.0)
                if med == "CYRK":
                    d = self.cyrk_rura
                else:
                    tag = "Z" if med == "ZW" else "C"
                    up = next((o for o in wo.odcinki if o.typ == "pion" and o.od == f"{pn.id}{tag}@{self.kid}"), None)
                    dn = next((o for o in wo.odcinki if o.typ == "pion" and o.do == f"{pn.id}{tag}@{self.kid}"), None)
                    d = rura_krotko((up or dn).rura) if (up or dn) else ""
                arrow = ("↑" if i < top else "") + ("↓" if i > 0 else "")
                lines.append(f"{SKROT[med]} {d} {arrow}".strip())
            self.tag(self.ppos[pn.id]["CWU"], lines, "S-OPISY", style="bold", radii=(6.0, 9.0, 13.0, 18.0, 24.0))
        self.leg.sym(lambda c, p: S.riser(c, p, None, "WZ", s_mm=2.4),
                     "pion instalacji (Wz / Wc / Cyrk); ↑ — prowadzony na kondygnację wyższą, ↓ — z kondygnacji niższej")

    def pomieszczenia(self):
        wo = self.W.woda
        for med in ("ZW", "CWU"):
            tag = "Z" if med == "ZW" else "C"
            roots = [o for o in wo.odcinki if self._seg_floor(o) and o.medium == med
                     and re.match(rf"^.+{tag}@P\w+$", o.od) and o.do.startswith(f"R{tag}_")]
            for o in roots:
                a = self.xy(o.od, med)
                subs = [s for s in wo.odcinki if s.od == o.do]
                fx = [(s, self.xy(s.do, med)) for s in subs]
                if not fx:
                    continue
                fx.sort(key=lambda t: abs(t[1][0] - a[0]) + abs(t[1][1] - a[1]))
                key = f"{med}:{o.do}"
                comp = f"ZW:R{'Z'}_{o.do.split('_', 1)[1]}" if med == "CWU" else None
                p0 = self._route_pipe(a, fx[0][1], med, key, companion=comp)
                self._valve(p0, 0.25)
                if rura_krotko(o.rura) != "16×2,0":
                    self.label(p0, f"{SKROT[med]} {rura_krotko(o.rura)}", "S-OPISY")
                for s, q in fx[1:]:
                    self._route_pipe(q, None, med, key, companion=comp, targets=self.g.occ[key])
                for s, q in fx:
                    if rura_krotko(s.rura) != "16×2,0":
                        self.tag(q, [f"{SKROT[med]} {rura_krotko(s.rura)}"], "S-OPISY", radii=(4.0, 6.0, 9.0))
        # punkty czerpalne poza pionami (zawory ogrodowe) — oznaczenie
        for p in wo.przybory:
            if p.kond != self.kid:
                continue
            if p.typ == "zawor_ogrodowy":
                q = np.asarray(p.xy, float)
                self.sym(S.valve, q, 0.0, s_mm=2.4)
                self.tag(q, ["zawór ogrodowy mrozoodporny DN15 z zabezpieczeniem HA/HD (PN-EN 1717)"], "S-OPISY")

    def opisy(self):
        W = self.W
        wo = W.woda
        pk = wo.punkt_krytyczny
        if pk.przybor.kond == self.kid:
            q = self.xy(pk.przybor.id + ("C" if pk.medium == "CWU" else "Z"), "CWU" if pk.medium == "CWU" else "ZW")
            self.tag(q, [f"punkt krytyczny {pk.przybor.id}: p_wym = {num(pk.p_wym, 0)} kPa"], "S-OPISY")
        self.notes += [
            "Instalacja wodociągowa wg PN-EN 806-1…5 i WT § 113–121; obliczenia przepływów wg PN-92/B-01706 (norma "
            "wycofana — stosowana jako praktyka projektowa, powołana w WT zał. 1) z kontrolą wg PN-EN 806-3; ochrona "
            "przed wtórnym zanieczyszczeniem wg PN-EN 1717.",
            "Średnice przewodów z obliczeń (lamela.obliczenia.sanitarne.woda); podejścia do przyborów 16×2,0, jeżeli nie "
            "opisano inaczej. Rury wielowarstwowe PE-RT/Al/PE-RT (lub równoważne) z kształtkami zaprasowywanymi.",
            f"Wymagane ciśnienie przed wodomierzem p_wym = {num(pk.p_wym, 0)} kPa (punkt krytyczny {pk.przybor.id}); "
            f"q_obl = {num(wo.wodomierz['q'], 3)} dm³/s.",
            "Trasy przewodów wyznaczono algorytmicznie (model nie zawiera przebiegów): ortogonalnie, przy ścianach, "
            "z rozdzielaczy w pom. technicznym i z pionów w szachcie SI do przyborów — w warstwie posadzki/bruzdach "
            "ściennych; do weryfikacji na budowie z zachowaniem średnic i zasady rozdziału.",
            "C.w.u. po lewej stronie armatury (WT § 120 ust. 5); temperatura c.w.u. 55–60 °C, dezynfekcja termiczna "
            "70 °C (WT § 120 ust. 2a); izolacja c.w.u. i cyrkulacji wg WT zał. 2 pkt 1.5 (tabela), wody zimnej — "
            "przeciwroszeniowa 9 mm.",
            "Próba szczelności wg PN-EN 806-4; płukanie i dezynfekcja przed odbiorem.",
        ]
        rows = [[r[0].replace("PE-RT/Al/PE-RT ", ""), r[4], r[5], r[7].replace(" (W-135)", "")] for r in wo.izolacje]
        if self.kid == self.kids[0]:
            self.res.column_blocks.append(("izol", table_block(
                "IZOLACJA CIEPLNA PRZEWODÓW (obliczenia)", [("Przewód", 60), ("t [mm]", 18), ("przejścia [mm]", 26),
                                                           ("Podstawa", 76)], rows,
                align=["left", "right", "right", "left"])))
            d = wo.do_dict()
            self.res.column_blocks.append(("wyn", table_block(
                "WYNIKI OBLICZEŃ — WODA (lamela.obliczenia.sanitarne.woda)", [("Wielkość", 90), ("Wartość", 90)],
                [["przepływ obliczeniowy q", f"{num(d['q_obl_dm3s'], 3)} dm³/s"],
                 ["wodomierz", f"DN{wo.wodomierz['DN']}, Q3 = {num(wo.wodomierz['Q3'], 1)} m³/h"],
                 ["p_wym (punkt krytyczny)", f"{num(d['p_wym_kPa'], 0)} kPa ({d['punkt_krytyczny']})"],
                 ["zasobnik c.w.u.", f"{d['zasobnik_l']} dm³"], ["cyrkulacja", str(d["cyrkulacja"])],
                 ["zapotrzebowanie Q_d,śr", f"{num(d['Q_d_sr_m3'], 2)} m³/d"]], align=["left", "left"])))
