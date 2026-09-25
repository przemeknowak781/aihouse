"""Drenaż opaskowy i odwodnienie powierzchniowe wokół budynku — decyzja z uzasadnieniem (brief §9 pkt 6).

Kryteria (wiedza techniczna; polskie przepisy nie rozstrzygają wprost o drenażu budynku bez podziemia):

* **PN-EN 1997-1:2008 (EC7), p. 2.4.6.1 i p. 4** — w projekcie geotechnicznym uwzględnia się poziomy wody gruntowej
  i możliwość wody zawieszonej / okresowego podtopienia; rozwiązanie ochrony przed wodą wynika z warunków gruntowo-wodnych
  (kategoria geotechniczna II — W-280, dokumentacja badań) [NZW — numery punktów].
* **DIN 18533-1:2017** (Abdichtung von erdberührten Bauteilen) — klasy oddziaływania wody: **W1.1-E** (wilgoć gruntowa
  i woda nienaporowa) gdy grunt silnie przepuszczalny **k_f > 10⁻⁴ m/s** i obliczeniowy poziom wody ≥ 0,5 m poniżej spodu
  elementu; **W1.2-E** — grunt słabo przepuszczalny (k_f ≤ 10⁻⁴ m/s) **z drenażem wg DIN 4095**; bez drenażu — woda
  zastoiskowa, **W2.1-E** (woda naporowa ≤ 3 m) [W — norma niemiecka jako wiedza techniczna].
* **DIN 4095:1990** (Dränung zum Schutz baulicher Anlagen) — drenaż przy gruntach słabo przepuszczalnych i
  pomieszczeniach poniżej terenu; nie stosuje się do obniżania zwierciadła wody gruntowej [W].
* **WT §28 ust. 2, §316 ust. 2** — spływ wód od budynku, bez kierowania na działki sąsiednie; **W-019**: teren ze spadkiem
  ≥ 2 % od budynku [ZAŁ] na odcinku 1,5–2 m (brief §9 pkt 6); **brief §9 pkt 4** — cokół ≥ 0,30 m nad terenem albo
  odwodnienie liniowe przy drzwiach bezprogowych.

Przepuszczalność gruntów (orientacyjnie): piaski średnie 10⁻⁴–10⁻³ m/s, piaski drobne 10⁻⁵–10⁻⁴ m/s, piaski gliniaste
10⁻⁶–10⁻⁵ m/s, gliny < 10⁻⁷ m/s (Wiłun Z., Zarys geotechniki, WKŁ; Aquanet 2024 tab. 1) [W].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..inst_wspolne import DaneBudynku, Krok, Raport, Warunek, f, fa, wym

KF_GRUNTOW = {"żwiry": 1e-2, "pospółki": 1e-3, "piaski grube": 1e-3, "piaski średnie": 3e-4, "piaski drobne": 5e-5,
              "piaski pylaste": 1e-5, "piaski gliniaste": 3e-6, "gliny": 1e-8, "iły": 1e-10}


@dataclass
class ParametryDrenaz:
    grunt: str = "piaski średnie"          # brief §2 (dane przykładowe)
    k_f: float | None = None               # m/s — z badań; None → wartość typowa dla gruntu [W]
    ZWG_ppt: float | None = None           # m p.p.t.; domyślnie geotechnika.ZWG_ppt
    zasypka_przepuszczalna: bool = True    # zasypka wykopów gruntem przepuszczalnym (piasek)
    pomieszczenia_ponizej_terenu: bool | None = None   # None → z modelu (posadzka P0 vs teren)
    spadek_min: float = 0.02
    pas_spadku: float = 2.0                # m
    cokol_min: float = 0.30                # m


@dataclass
class WynikDrenaz:
    dane: DaneBudynku
    par: ParametryDrenaz
    decyzja: str
    klasa: str
    uzasadnienie: list
    spod_fund: float
    teren_sr: float
    glebokosc_posadowienia: float
    odl_ZWG_pod_fund: float
    spadki: list
    cokol_min: float
    warunki: list
    zalecenia: list

    def do_dict(self) -> dict:
        return {"drenaz_opaskowy": self.decyzja, "klasa_oddzialywania_wody": self.klasa,
                "glebokosc_posadowienia_m": round(self.glebokosc_posadowienia, 2), "ZWG_pod_fundamentem_m": round(self.odl_ZWG_pod_fund, 2)}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def ocen_drenaz(dane: DaneBudynku, par: ParametryDrenaz | None = None) -> WynikDrenaz:
    par = par or ParametryDrenaz()
    kf = par.k_f if par.k_f is not None else KF_GRUNTOW.get(par.grunt, 1e-4)
    ZWG = par.ZWG_ppt if par.ZWG_ppt is not None else float(wym("geotechnika", "ZWG_ppt", 3.8) or 3.8)
    m = dane.model
    fund = m.fundamenty() if m is not None else {}
    spody = [float(e.get("spod")) for e in (fund.get("elementy") or []) if e.get("spod") is not None]
    spod = min(spody) if spody else -1.10
    obrys = dane.obrysy.get(dane.kondygnacje[0]["id"])
    per = obrys.exterior
    pts = [per.interpolate(t, normalized=True) for t in np.linspace(0, 1, 60, endpoint=False)]
    tz = [dane.teren_z((p.x, p.y)) for p in pts]
    teren_sr = float(np.mean(tz))
    h_pos = teren_sr - spod
    d_ZWG = ZWG - h_pos
    ponizej = par.pomieszczenia_ponizej_terenu
    if ponizej is None:
        ponizej = dane.rzedna(dane.kondygnacje[0]["id"]) < max(tz) - 0.05
    uz = [f"Grunt: {par.grunt}, k_f = {fa(kf)} m/s " + ("(z badań)" if par.k_f is not None else "(wartość typowa [W]; wymagane badania — E-04)"),
          f"Zwierciadło wody gruntowej {f(ZWG, 2)} m p.p.t.; spód fundamentu {f(spod, 2)} m (wzgl. ±0,00), teren przy budynku "
          f"średnio {f(teren_sr, 2)} m → głębokość posadowienia {f(h_pos, 2)} m; ZWG {f(d_ZWG, 2)} m poniżej spodu fundamentu.",
          "Pomieszczenia poniżej terenu: " + ("TAK" if ponizej else "brak (budynek niepodpiwniczony, posadzka parteru nad terenem)")]
    if d_ZWG < 0.5:
        klasa, dec = "W2.1-E (woda naporowa)", "nie dotyczy — wymagana izolacja przeciwwodna (drenaż nie obniża ZWG)"
        uz.append("ZWG < 0,5 m pod spodem fundamentu — oddziaływanie wody naporowej; drenaż opaskowy nie jest właściwym środkiem.")
    elif kf > 1e-4 and par.zasypka_przepuszczalna:
        klasa, dec = "W1.1-E (wilgoć gruntowa, woda nienaporowa)", "NIEWYMAGANY"
        uz.append("Grunt silnie przepuszczalny (k_f > 10⁻⁴ m/s) i ZWG ≥ 0,5 m pod fundamentem — woda opadowa infiltruje "
                  "pionowo, nie powstaje woda zastoiskowa przy ścianach; wystarcza izolacja przeciwwilgociowa.")
        if ponizej:
            uz.append("Uwaga: przy pomieszczeniach poniżej terenu zaleca się mimo to kontrolę zasypki i odwodnienie powierzchniowe.")
    else:
        klasa = "W1.2-E (z drenażem) / W2.1-E (bez drenażu — woda zastoiskowa)"
        dec = "ZALECANY (drenaż opaskowy wg DIN 4095) albo izolacja jak dla wody naporowej"
        uz.append("Grunt słabo przepuszczalny (k_f ≤ 10⁻⁴ m/s) lub zasypka nieprzepuszczalna — możliwa woda zastoiskowa przy "
                  "ścianach i płycie; drenaż opaskowy DN100 (rura perforowana w obsypce żwirowej 8/16 w geowłókninie, spadek "
                  "≥ 0,5 %, studzienki kontrolne w narożach) z odprowadzeniem do niecki/zbiornika [W — DIN 4095].")
    # spadki terenu wokół budynku (istniejące / projektowane)
    spadki = []
    proj = ((dane.dzialka.get("raw") or {}).get("teren") or {}).get("punkty_projektowane")
    zrodlo = "rzędne projektowane (dzialka.yaml)" if proj else "teren istniejący (brak rzędnych projektowanych)"
    for k, (a, b) in enumerate(zip(list(per.coords)[:-1], list(per.coords)[1:])):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1.0:
            continue
        nx, ny = dy / L, -dx / L           # normalna zewnętrzna dla obiegu CCW
        p1 = (mx + nx * 0.3, my + ny * 0.3)
        p2 = (mx + nx * (0.3 + par.pas_spadku), my + ny * (0.3 + par.pas_spadku))
        z1, z2 = dane.teren_z(p1), dane.teren_z(p2)
        s = (z1 - z2) / par.pas_spadku
        spadki.append({"odcinek": k + 1, "srodek": (mx, my), "L": L, "z_przy": z1, "z_2m": z2, "spadek": s})
    war = []
    for s in spadki:
        war.append(Warunek(f"Spadek terenu od budynku, ściana {s['odcinek']} (śr. {f(s['srodek'][0], 1)}; {f(s['srodek'][1], 1)})",
                           s["spadek"], ">=", par.spadek_min, "", f"W-019; brief §9 pkt 6 ({zrodlo})", "W-019", nd=3))
    cokol = min(dane.rzedna(dane.kondygnacje[0]["id"]) - z for z in tz)
    war.append(Warunek("Wysokość cokołu (posadzka parteru − teren), minimum na obwodzie", cokol, ">=", par.cokol_min, "m",
                       "brief §9 pkt 4 (≥ 0,30 m lub odwodnienie liniowe przy drzwiach bezprogowych)", "W-019", nd=2))
    zal = ["Odwodnienie powierzchniowe: profilowanie terenu ze spadkiem ≥ 2 % od budynku na pasie ≥ 2,0 m (rzędne projektowane "
           "w dzialka.yaml: teren.punkty_projektowane) — wymagane niezależnie od drenażu.",
           "Opaska żwirowa szer. 0,5 m wokół budynku (żwir płukany 16/32 mm na geowłókninie, obrzeże), spadek od ściany; "
           "chroni cokół przed rozbryzgiem i ułatwia kontrolę izolacji [W].",
           "Izolacja przeciwwilgociowa ścian fundamentowych/cokołu i płyty (klasa " + klasa.split(' ')[0] + "), wywinięta ≥ 0,30 m "
           "ponad teren (brief §9 pkt 4); przy drzwiach bezprogowych odwodnienie liniowe (moduł deszczowa).",
           "Rury spustowe i odwodnienia liniowe nie mogą zrzucać wody przy fundamentach — odprowadzenie do zbiornika / niecki "
           "(≥ 3,0 m od fundamentów, W-144).",
           "Decyzję zweryfikować po badaniach podłoża (kategoria geotechniczna II — W-280): k_f in situ w strefie zasypki, "
           "obserwacje wody zawieszonej po roztopach."]
    return WynikDrenaz(dane=dane, par=par, decyzja=dec, klasa=klasa, uzasadnienie=uz, spod_fund=spod, teren_sr=teren_sr,
                       glebokosc_posadowienia=h_pos, odl_ZWG_pod_fund=d_ZWG, spadki=spadki, cokol_min=cokol, warunki=war,
                       zalecenia=zal)


def _raport(w: WynikDrenaz) -> Raport:
    R = Raport("Drenaż opaskowy i odwodnienie powierzchniowe — decyzja projektowa",
               f"Obiekt: {w.dane.nazwa}. Wymaganie Inwestora 25.09.2026 (brief §9 pkt 6). Dane gruntowe przykładowe [ZAŁ].")
    R.h(2, "1. Dane i kryteria")
    R.lista(w.uzasadnienie)
    R.tab(["Kryterium (DIN 18533-1 / DIN 4095 — wiedza techniczna)", "Stan", "Wniosek"],
          [["Przepuszczalność gruntu k_f > 10⁻⁴ m/s", fa(w.par.k_f or KF_GRUNTOW.get(w.par.grunt, 1e-4)) + " m/s",
            "silnie przepuszczalny" if (w.par.k_f or KF_GRUNTOW.get(w.par.grunt, 1e-4)) > 1e-4 else "słabo przepuszczalny"],
           ["ZWG ≥ 0,5 m pod spodem fundamentu", f(w.odl_ZWG_pod_fund, 2) + " m", "spełnione" if w.odl_ZWG_pod_fund >= 0.5 else "NIE"],
           ["Zasypka wykopów z gruntu przepuszczalnego", "tak" if w.par.zasypka_przepuszczalna else "nie", "—"],
           ["Klasa oddziaływania wody", w.klasa, ""]], "lll")
    R.h(2, "2. Decyzja")
    R.p(f"**Drenaż opaskowy: {w.decyzja}.**")
    R.h(2, "3. Odwodnienie powierzchniowe i zalecenia")
    R.lista(w.zalecenia)
    R.tab(["Ściana", "L [m]", "Teren przy ścianie [m]", "Teren 2 m dalej [m]", "Spadek"],
          [[s["odcinek"], f(s["L"], 1), f(s["z_przy"], 3), f(s["z_2m"], 3), f(s["spadek"], 3)] for s in w.spadki], "rrrrr")
    R.h(2, "4. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("PN-EN 1997-1:2008 + NA (EC7) — sytuacje obliczeniowe z wodą gruntową [NZW numeracja]",
             "DIN 18533-1:2017-07 Abdichtung von erdberührten Bauteilen — klasy W1.1-E, W1.2-E, W2.1-E [W]",
             "DIN 4095:1990-06 Dränung zum Schutz baulicher Anlagen [W]",
             "Wiłun Z., Zarys geotechniki, WKŁ — współczynniki filtracji gruntów [W]; Aquanet 2024 tab. 1",
             "WT §28, §316; rejestr wymagań W-019, W-144, W-280, W-285; brief §9 pkt 4 i 6")
    return R
