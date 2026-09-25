"""IE-PV — instalacja fotowoltaiczna (moduły na dachu, łańcuchy, trasa DC, falownik, SPD) i IE-U — uziom,
połączenia wyrównawcze, ochrona odgromowa (decyzja z analizy ryzyka PN-EN IEC 62305-2 — obliczenia).

Dane: ``lamela.obliczenia.elektryka.pv`` (liczba modułów, moc, wariant EW/S, łańcuchy, DC, SPD) i
``lamela.obliczenia.elektryka.odgromowa`` (uziom, LPS, wyrównania). Rozmieszczenie modułów wyznaczane
algorytmicznie w polu użytkowym dachu (odsunięcie od krawędzi z obliczeń, bez otworów, wpustów, czerpni/wyrzutni
i wywiewek z odstępem 1,0 m)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from ...draft import symbols as S
from ...draft.geom import polygons_of
from .ie_rzut import RysE, _box
from .wspolne import BRAK, num, table_block


def uklad_modulow(pole, n, dl, sz, wariant="EW10", przerwa=0.60):
    """Rozmieszczenie n modułów w wieloboku ``pole`` (zachłannie rzędami). EW: pary zachód–wschód (grzbiet N–S),
    rzędy ciągłe w kierunku N–S, przejście serwisowe ``przerwa`` co 2 pary; S: moduły poziomo z odstępem
    przeciwcieniowym. Zwraca listę (prostokąt, strona 'E'|'W'|'S')."""
    if n <= 0 or pole is None or pole.is_empty:
        return []
    from shapely.prepared import prep
    P = prep(pole)
    ew = str(wariant).upper().startswith("EW")
    tilt = math.radians(10.0 if ew else 15.0)
    L = dl * math.cos(tilt)
    ph = sz + 0.02 if ew else L + 0.9
    x0, y0, x1, y1 = pole.bounds
    best = []
    for oy in np.linspace(0, ph, 5, endpoint=False):
        mods = []
        y = y0 + oy
        while y + (sz if ew else L) <= y1 + 1e-9 and len(mods) < n:
            x = x0
            k = 0
            while x <= x1 and len(mods) < n:
                if ew:
                    rw = box(x, y, x + L, y + sz)
                    re_ = box(x + L + 0.05, y, x + 2 * L + 0.05, y + sz)
                    if P.contains(rw) and P.contains(re_) and len(mods) <= n - 2:
                        mods += [(rw, "W"), (re_, "E")]
                        k += 1
                        x += 2 * L + 0.05 + (przerwa if k % 2 == 0 else 0.0)
                        continue
                    if P.contains(rw):
                        mods.append((rw, "W"))
                        x += L + 0.05
                        continue
                else:
                    r = box(x, y, x + sz, y + L)
                    if P.contains(r):
                        mods.append((r, "S"))
                        x += sz + 0.02
                        continue
                x += 0.05
            y += ph
        if len(mods) > len(best):
            best = mods
        if len(best) >= n:
            break
    return best[:n]


class RysPV(RysE):
    br = "IE"
    kod = "IE-PV"

    def run(self):
        if self.dach:
            self.podklad()
            self.siatka(extra_pts=[], sciany=0.0, przy_scianie=1.0, poza=0.0)
            self.obw = self.W.obwody.obwody
            self.circuits_used = set()
            self.dach_pv()
        else:
            self.prepare()
            self.parter_pv()
        self.opisy()
        return self.finish(rooms=not self.dach)

    def _pole(self):
        pv = self.W.pv
        did = (pv.dach or {}).get("id", "D1")
        d = next((d for d in self.m.dachy() if str(d.get("id")) == did), None)
        if d is None:
            return None, None
        poly = Polygon(d["obrys"])
        at = float((d.get("attyka") or {}).get("szer", 0.25))
        pole = poly.buffer(-(at + float(pv.par.odstep_od_krawedzi)), join_style=2)
        obst = [Polygon(o).buffer(0.3, join_style=2) for o in (d.get("otwory") or [])]
        lok = self.W.dane.inst.get("lokalizacje") or {}
        for key in ("czerpnia", "wyrzutnia"):
            if lok.get(key):
                obst.append(Point(lok[key][:2]).buffer(0.6))
        for w in (self.W.dane.inst.get("piony") or []):
            if "wywiewk" in str(w.get("opis", "")).lower() or "ponad dach" in str(w.get("opis", "")).lower():
                obst.append(Point(w["xy"][:2]).buffer(0.6))
        for w in d.get("wpusty") or []:
            xy = w.get("xy") if isinstance(w, dict) else w
            obst.append(Point(xy).buffer(0.5))
        if obst:
            pole = pole.difference(unary_union(obst))
        return d, pole

    def dach_pv(self):
        pv = self.W.pv
        vp = self.vp
        d, pole = self._pole()
        if d is None:
            self.brak("PV — dach", "brak dachu wskazanego w obliczeniach PV", "")
            return
        mod = pv.par.modul
        n = int(pv.n_mod)
        a = uklad_modulow(pole, n, float(mod["dl"]), float(mod["szer"]), pv.wariant)
        b = uklad_modulow(pole, n, float(mod["szer"]), float(mod["dl"]), pv.wariant)   # moduły obrócone o 90°
        mods = a if len(a) >= len(b) else b
        if len(mods) < n:
            self.brak("PV — rozmieszczenie modułów", f"w polu użytkowym dachu {d.get('id')} zmieszczono {len(mods)} z {n} "
                      "modułów (odsunięcia od krawędzi, otworów, czerpni/wyrzutni)", "energia.pv.pole: [[x, y], …] "
                      "(jawne pole montażu) lub zmiana liczby modułów")
        # łańcuchy
        ln = pv.lancuchy or {}
        n_str = int(ln.get("n_str", 1) or 1)
        per = [n // n_str + (1 if i < n % n_str else 0) for i in range(n_str)]
        order = sorted(range(len(mods)), key=lambda i: (round(mods[i][0].bounds[0], 1), mods[i][0].bounds[1]))
        idx = 0
        for si, cnt in enumerate(per):
            grp = [order[j] for j in range(idx, min(idx + cnt, len(order)))]
            idx += cnt
            cs = []
            for gi in grp:
                r, side = mods[gi]
                n0 = len(vp.prims)
                vp.geom(r, "E-PV", pen="cienka", lt="CIAGLA")
                x0, y0, x1, y1 = r.bounds
                if side in ("E", "W"):
                    xr = x1 if side == "W" else x0          # grzbiet (krawędź wyższa) po stronie środka pary
                    vp.line((xr, y0), (xr, y1), "E-PV", pen="srednia", lt="CIAGLA")
                vp.text(r.centroid.coords[0], f"{si + 1}.{len(cs) + 1}", 1.8, 0.0, "center", "middle", "E-PV")
                self.reg(n0)
                cs.append(np.asarray(r.centroid.coords[0]))
            if len(cs) > 1:
                vp.polyline(np.array(cs), "E-PV", pen="b_cienka", lt="KRESKOWA_DROBNA")
            if cs:
                self.tag(cs[0], [f"łańcuch S{si + 1}: {len(cs)} × {num(mod['P'], 0)} Wp"], "E-OPISY", style="bold")
        # trasa DC: od pola PV do krawędzi dachu najbliżej falownika (RG), dalej po elewacji / dachu niższym
        rg = self.W.obwody.rg_xy
        if mods and rg is not None:
            c = np.mean([np.asarray(r.centroid.coords[0]) for r, _s in mods], axis=0)
            tgt = np.asarray(rg[:2], float)
            path = self.g.route(c, tgt, "DC", turn=0.5, margin=10.0)
            self.pipe(path, "WZ", layer="E-PV", pen="srednia", lt="KRESKOWA")
            dc = pv.dc or {}
            self.label(path, f"trasa DC: 2 × 2 × H1Z2Z2-K 1×{num(pv.par.s_DC, 0)} mm² w korycie/rurze metalowej, "
                       f"L ≈ {num(dc.get('L', 0), 1)} m, ∆U = {num(dc.get('dU', 0), 2)} %", "E-OPISY")
            self.tag(tgt, [f"{BRAK} przepust DC do pom. technicznego (falownik przy RG) — trasa proponowana"],
                     "I-BRAKI", color="#b0008a")
            self.brak("PV — trasa DC", "brak w modelu trasy przewodów DC i przepustu dachowego — przyjęto trasę po "
                      "dachach (poza drogami ewakuacyjnymi) do pom. technicznego", "energia.pv.trasa_dc: [[x, y, z], …], "
                      "przepust: [x, y]")
        self.leg.sym(lambda c, p: (c.rect(p[0] - 5, p[1] - 3, p[0] + 5, p[1] + 3, "E-PV", pen="cienka", lt="CIAGLA"),
                                   c.line((p[0] + 5, p[1] - 3), (p[0] + 5, p[1] + 3), "E-PV", pen="srednia",
                                          lt="CIAGLA")),
                     "moduł PV (wymiar rzeczywisty, układ wschód–zachód 10°; linia gruba — krawędź wyższa); "
                     "<łańcuch>.<nr>")
        self.leg.line("E-PV", "trasa przewodów DC (H1Z2Z2-K) w korytach/rurach metalowych", lt="KRESKOWA")

    def parter_pv(self):
        pv = self.W.pv
        rg = self.rg()
        if rg is None:
            return
        e = next((e for e in self.W.dane.wyposazenie if "rozdzielnica" in str(e.get("opis", "")).lower()), None)
        from ...draft.geom import dir_deg, perp
        rot = float(e.get("obrot", 90))
        q = rg - perp(dir_deg(rot)) * 0.8 + dir_deg(rot) * 0.15
        self.sym(_box, q, "FAL", w_mm=7.0, layer="E-PV")
        dc = pv.dc or {}
        fal = pv.par.falownik
        self.tag(q, [f"falownik {str(fal.get('model', '')).replace(' (dane przykładowe)', '')} (dane przykładowe, lub "
                     "równoważny): P_AC = "
                     f"{num(fal.get('P_AC', 0), 1)} kW, {fal.get('n_mppt', 2)} MPPT",
                     str(dc.get("SPD", "SPD DC typ 2"))[:90], str(dc.get("rozlacznik", "rozłącznik DC"))[:90]],
                     "E-OPISY", style="bold")
        q2 = q + dir_deg(rot) * 0.6
        self.sym(S.riser, q2, None, "WZ", s_mm=2.4)
        self.tag(q2, ["DC ↓ z dachu (przepust przez strop D4, rura metalowa) — trasa wg arkusza PV dachu"],
                 "E-OPISY")
        path = self.g.route(q2, q, "DC")
        self.pipe(path, "WZ", layer="E-PV", pen="srednia", lt="KRESKOWA")
        path = self.g.route(q, rg, "AC")
        self.pipe(path, "WZ", layer="E-TRASY", pen="cienka", lt="CIAGLA")
        o = next((o for o in self.obw if o.odb.grupa == "pv"), None)
        if o is not None:
            self.circuit_tag((q + rg) / 2, o.odb.id, f"AC {o.przewod}, {o.zab}, {o.odb.rcd.split(' (')[0]}")
        # tabliczki ostrzegawcze PWP / DC
        self.notes.append("Przy RG, przycisku PWP i falowniku — tabliczki ostrzegawcze: „instalacja PV — strona DC pod "
                          "napięciem po wyłączeniu PWP” (WT § 183, PN-HD 60364-7-712).")
        self.leg.sym(lambda c, p: _box(c, p, "FAL", w_mm=7.0, layer="E-PV"), "falownik PV (SPD DC typ 2, rozłącznik DC)")
        self.leg.sym(lambda c, p: S.riser(c, p, None, "WZ", s_mm=2.4), "przepust / pion przewodów DC")

    def opisy(self):
        pv = self.W.pv
        ln = pv.lancuchy or {}
        self.notes += [
            "Instalacja fotowoltaiczna wg PN-HD 60364-7-712, PN-EN 62446-1 (dokumentacja, badania), WT § 184 i "
            f"art. 29 ust. 4 pkt 3 lit. c PB (moc ≤ 6,5 kWp): {pv.n_mod} × {num(pv.par.modul['P'], 0)} Wp = "
            f"{num(pv.P_kWp, 2)} kWp, układ {pv.wariant}, E ≈ {num(pv.E_y, 0)} kWh/a (PVGIS; obliczenia lamela.obliczenia."
            "elektryka.pv).",
            f"Łańcuchy: {ln.get('n_str', '?')} × do {ln.get('Ns', '?')} modułów; U_oc,max = {num(ln.get('Uoc_max', 0), 0)} V, "
            f"U_mpp {num(ln.get('Umpp_min', 0), 0)}–{num(ln.get('Umpp_max', 0), 0)} V, I_sc = {num(ln.get('I_sc', 0), 1)} A "
            "(obliczenia) — sprawdzić z DTR wybranych modułów i falownika (dane przykładowe, lub równoważne).",
            "Rozmieszczenie modułów wyznaczono algorytmicznie w polu użytkowym dachu (odsunięcie ≥ 1,0 m od krawędzi, "
            "odstępy od otworów, wpustów, czerpni, wyrzutni i wywiewek); konstrukcja balastowa niskoprofilowa — "
            "górna krawędź ≤ wierzchu attyki; obciążenia i balast wg PN-EN 1991-1-4 (projekt konstrukcji).",
            "Konstrukcję wsporczą PV połączyć z GSU przewodem wyrównawczym ≥ 6 mm² Cu (712.444.5.5.101); odstęp "
            "separacyjny od ewentualnych zwodów wg PN-EN IEC 62305-3.",
        ]
        bad = [w for w in pv.warunki if w.ok is False]
        for w in bad[:3]:
            self.notes.append(f"SPRAWDZENIE NIESPEŁNIONE (obliczenia): {w.opis} ({w.podstawa}) — do korekty.")
        if self.dach:
            rows = [["moduły", f"{pv.n_mod} × {pv.par.modul['model']}"], ["moc", f"{num(pv.P_kWp, 2)} kWp"],
                    ["falownik", pv.par.falownik.get("model", "")], ["energia roczna", f"{num(pv.E_y, 0)} kWh/a"],
                    ["pole dachu / użytkowe", f"{num(pv.dach['A'], 1)} / {num(pv.dach['A_uz'], 1)} m²"]]
            self.res.column_blocks.append(("pv", table_block("WYNIKI OBLICZEŃ — PV (lamela.obliczenia.elektryka.pv)",
                                                             [("Wielkość", 60), ("Wartość", 120)], rows,
                                                             align=["left", "left"])))


# ================================================================================================ IE-U
class RysU(RysE):
    kod = "IE-U"

    def run(self):
        if self.dach:
            self.podklad()
            self.siatka(extra_pts=[], sciany=0.0, przy_scianie=1.0, poza=0.0)
            self.obw = self.W.obwody.obwody
            self.circuits_used = set()
            self.dach_u()
        else:
            self.prepare()
            self.parter_u()
        self.opisy()
        return self.finish(rooms=not self.dach)

    def _otok(self):
        og = self.W.odgromowa
        ob = unary_union([self.m.obrys_kondygnacji(self.kids[0])])
        off = float(getattr(og.par, "otok_odsuniecie", 1.0))
        ring = ob.buffer(off, join_style=2)
        ring = max(polygons_of(ring), key=lambda g: g.area)
        return ring, off

    def parter_u(self):
        og = self.W.odgromowa
        vp = self.vp
        uz = og.uziom or {}
        ring, off = self._otok()
        otok = "otokow" in str(uz.get("typ", "")).lower()
        n0 = len(vp.prims)
        if otok:
            vp.polygon(np.asarray(ring.exterior.coords)[:-1], "E-ODGROM", pen="gruba", lt="CIAGLA")
        else:
            ob = self.m.obrys_kondygnacji(self.kids[0]).buffer(-0.35, join_style=2)
            vp.polygon(np.asarray(max(polygons_of(ob), key=lambda g: g.area).exterior.coords)[:-1], "E-ODGROM",
                       pen="gruba", lt="KRESKOWA")
        self.reg(n0)
        self.label(np.asarray(ring.exterior.coords), f"uziom {'otokowy' if otok else 'fundamentowy'}: "
                   f"{str(uz.get('material', ''))[:70]}", "E-OPISY")
        self.leg.line("E-ODGROM", f"uziom {'otokowy w gruncie (≥ 0,5 m p.p.t., ≥ 1,0 m od ścian)' if otok else 'fundamentowy'}"
                      f" — R_obl ≈ {num(uz.get('R', 0), 1)} Ω", pen="gruba", lt="CIAGLA")
        # wyprowadzenia w narożnikach
        cs = np.asarray(ring.exterior.coords)[:-1]
        x0, y0, x1, y1 = ring.bounds
        corners = []
        for tgt in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            corners.append(min(cs, key=lambda p: abs(p[0] - tgt[0]) + abs(p[1] - tgt[1])))
        for q in corners:
            self.sym(S.earth, q, -90.0, s_mm=3.0)
        self.tag(corners[0], ["wyprowadzenia uziomu w narożnikach — złącza kontrolne (rezerwa pod przewody "
                              "odprowadzające LPS, h = 0,5 m nad terenem)"], "E-OPISY")
        # GSU i połączenia wyrównawcze
        rg = self.rg()
        if rg is None:
            return
        gsu = rg + np.array([0.0, 0.45])
        self.sym(_box, gsu, "GSU", w_mm=6.0, layer="E-ODGROM")
        near = min(cs, key=lambda p: abs(p[0] - gsu[0]) + abs(p[1] - gsu[1]))
        path = self.g.route(near, gsu, "PE", margin=4.0)
        self.pipe(path, "WZ", layer="E-ODGROM", pen="srednia", lt="CIAGLA")
        self.label(path, "przewód uziemiający ≥ 16 mm² Cu (W-188)", "E-OPISY")
        lok = self.W.dane.inst.get("lokalizacje") or {}
        cele = [("wodomierz", "wodociąg (mostek na wodomierzu)"), ("zasobnik", "zasobnik, bufor, rury c.o./c.w.u.")]
        for key, txt in cele:
            if lok.get(key) and (len(lok[key]) < 3 or str(lok[key][2]) == self.kid):
                q = np.asarray(lok[key][:2], float)
                p2 = self.g.route(gsu, q, "PE", margin=4.0)
                self.pipe(p2, "WZ", layer="E-ODGROM", pen="cienka", lt="CIAGLA")
                self.tag(q, [f"połączenie wyrównawcze ≥ 6 mm² Cu — {txt}"], "E-OPISY")
        self.tag(gsu, ["GSU — główna szyna uziemiająca: PE z RG, uziom, zbrojenie płyty, wodociąg, c.o., RACK, "
                       "kanały went., konstrukcja PV (PN-HD 60364-5-54, WT § 183 ust. 1a)"], "E-OPISY", style="bold")
        self.leg.sym(lambda c, p: _box(c, p, "GSU", w_mm=6.0, layer="E-ODGROM"), "GSU — główna szyna uziemiająca")
        self.leg.sym(lambda c, p: S.earth(c, p + np.array([0, 1.5]), -90.0, s_mm=3.0),
                     "wyprowadzenie uziomu / złącze kontrolne (PN-EN 60617 02-15-01)")
        rows = [[a, b, c] for a, b, c in og.wyrownawcze]
        self.res.column_blocks.append(("wyr", table_block(
            "POŁĄCZENIA WYRÓWNAWCZE (obliczenia — lamela.obliczenia.elektryka.odgromowa)",
            [("Element", 70), ("Miejsce", 50), ("Przewód / uwagi", 60)], rows, align=["left", "left", "left"])))

    def dach_u(self):
        og = self.W.odgromowa
        lps = "NIEWYMAGANY" not in str(og.decyzja).upper()
        vp = self.vp
        if lps:
            info = og.lps or {}
            for d in self.m.dachy():
                poly = Polygon(d["obrys"]).buffer(-0.12, join_style=2)
                n0 = len(vp.prims)
                vp.polygon(np.asarray(poly.exterior.coords)[:-1], "E-ODGROM", pen="srednia", lt="CIAGLA")
                self.reg(n0)
            self.tag(np.asarray(Polygon(self.m.dachy()[0]["obrys"]).exterior.coords[0]),
                     [f"LPS klasy {info.get('klasa', 'IV')}: zwody na attykach, oczka {info.get('oczko', '')}, "
                      f"przewody odprowadzające {info.get('n_odpr', {}).get(info.get('klasa', 'IV'), 3)} szt."],
                     "E-OPISY", style="bold")
            self.leg.line("E-ODGROM", "zwody poziome LPS na attykach (PN-EN IEC 62305-3)", pen="srednia", lt="CIAGLA")
        # połączenie konstrukcji PV (moduły — obrys pomocniczy wg arkusza PV)
        d, pole = RysPV._pole(self)
        if d is not None and pole is not None and not pole.is_empty:
            mod = self.W.pv.par.modul
            mods = uklad_modulow(pole, int(self.W.pv.n_mod), float(mod["dl"]), float(mod["szer"]), self.W.pv.wariant)
            for r, _s in mods:
                vp.geom(r, "E-PV", pen=0.18, lt="CIAGLA", color="#9a86b5")
            if mods:
                c = np.asarray(unary_union([r for r, _s in mods]).centroid.coords[0])
            else:
                c = np.asarray(pole.representative_point().coords[0])
            if not lps:
                self.tag(c + np.array([0.0, 1.8]), [f"Analiza ryzyka PN-EN IEC 62305-2: {og.decyzja}",
                                                   "bez zwodów; ochrona przepięciowa SPD T1+T2 (RG) i SPD DC"],
                         "E-OPISY", style="bold")
            rg = self.W.obwody.rg_xy
            if rg is not None:
                path = self.g.route(c, np.asarray(rg[:2], float), "PE", margin=10.0)
                self.pipe(path, "WZ", layer="E-ODGROM", pen="cienka", lt="KRESKOWA")
                self.label(path, "przewód wyrównawczy konstrukcji PV ≥ 6 mm² Cu do GSU (712.444)", "E-OPISY")
            self.tag(c, [f"konstrukcja PV — {'w strefie ochronnej LPS, odstęp s ≥ ' + num(og.lps['s'], 2) + ' m' if lps else 'uziemienie funkcjonalne (jeden punkt)'}"],
                     "E-OPISY")
        self.leg.line("E-ODGROM", "przewód wyrównawczy (konstrukcja PV → GSU)", pen="cienka", lt="KRESKOWA")

    def opisy(self):
        og = self.W.odgromowa
        self.notes += [
            f"Ochrona odgromowa — analiza ryzyka wg PN-EN IEC 62305-2 (obliczenia lamela.obliczenia.elektryka.odgromowa): "
            f"A_D = {num(og.A_D, 0)} m², N_D = {num(og.N_D, 4)} 1/a; decyzja: {og.decyzja}. Ochrona przepięciowa: "
            "SPD T1+T2 w RG, SPD DC przy falowniku (WT § 184, PN-HD 60364-4-443/-5-534).",
            f"Uziom: {og.uziom.get('typ', '')}; R ≈ {num(og.uziom.get('R', 0), 1)} Ω (ρ = {num(og.par.rho_gruntu, 0)} Ωm) — "
            "pomiar rezystancji po wykonaniu; połączenia w gruncie zgrzewane/zaciskowe z ochroną antykorozyjną "
            "(PN-EN 62561-1/-2).",
            "Połączenia wyrównawcze główne i miejscowe wg PN-HD 60364-4-41 p. 411.3.1.2 i PN-HD 60364-5-54; "
            "w łazienkach — wg PN-HD 60364-7-701 (przy rurach z tworzyw zwykle niewymagane).",
            "Przebiegi przewodów wyznaczono algorytmicznie (uziom — obrys parteru odsunięty o wartość z obliczeń); "
            "wyprowadzenia i miejsca złączy — do koordynacji z projektem konstrukcji i PZT.",
        ]
