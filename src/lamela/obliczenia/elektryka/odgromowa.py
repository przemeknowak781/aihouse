"""Ochrona odgromowa: uproszczona ocena ryzyka R1 (utrata życia) wg PN-EN 62305-2, decyzja o LPS, uziom
(fundamentowy / otokowy), połączenia wyrównawcze, parametry LPS i odstęp separacyjny od PV.

Podstawy (W-187, W-188, W-191, R7-K01…K05, R7-G01…G08):

* **WT §53 ust. 2, §184 ust. 3** — instalacja piorunochronna, gdy wynika z PN (seria PN-EN 62305 nie ma listy obiektów →
  decyduje ocena ryzyka); formalnie PN-EN 62305-2:2008 (zał. 1 WT), aktualnie PN-EN IEC 62305-2:2025-09 (EN) — wyniki
  mogą się różnić [NZW].
* **Ocena R1 = R_A + R_B + R_U + R_V** (budynek mieszkalny — bez R_C, R_M, R_W, R_Z): N_D = N_G·A_D·C_D·10⁻⁶,
  A_D — powierzchnia zbierania: obrys powiększony o 3H (suma buforów części budynku o różnych wysokościach);
  N_L = N_G·A_L·C_I·C_E·C_T·10⁻⁶, A_L = 40·L_L (linia kablowa nN; L_L = 1000 m gdy nieznana); R_A = N_D·P_A·L_A,
  R_B = N_D·P_B·L_B, R_U = N_L·P_U·L_U, R_V = N_L·P_V·L_V; L_A = L_U = r_t·L_T, L_B = L_V = r_p·r_f·h_z·L_F;
  L_T = 10⁻², L_F = 10⁻² (budynki mieszkalne); r_f: 10⁻³ / 10⁻² / 10⁻¹ (obciążenie ogniowe < 400 / 400–800 / > 800 MJ/m²);
  r_p: 1 (brak), 0,5 (gaśnice, hydranty…), 0,2 (instalacja automatyczna); P_B: bez LPS 1, LPS IV 0,2, III 0,1;
  P_EB (SPD LPL III–IV) 0,05; **R_T = 10⁻⁵/rok** (PN-EN 62305-2:2012 zał. A–C — współczynniki wg R7-K05 [NZW]).
* **Obciążenie ogniowe domu**: PN-EN 1991-1-2 zał. E tabl. E.4 — mieszkania: średnio 780 MJ/m², kwantyl 80 % 948 MJ/m² [W]
  → klasa „zwykłe” (średnia) / „wysokie” (kwantyl) — rozstrzygające dla wyniku (D-13).
* **N_G = 1,8** wył./(km²·rok) (Poznań, na północ od 51°30′ — SEP; W-186 [NZW]).
* **Uziom** — WT §184 ust. 1; PN-HD 60364-5-54:2011 zał. C: fundament izolowany (XPS pod płytą, folia > 0,5 mm) → uziom
  otokowy w gruncie (Cu/StCu/StSt); rezystancja orientacyjnie: otok R ≈ 2ρ/(3D), fundamentowy R ≈ 2ρ/(πD)
  (D — średnica koła o polu obejmowanym) [W — DEHN, Lightning Protection Guide].
* **LPS III/IV** (PN-EN 62305-3): oczka zwodów 15×15 / 20×20 m, promień kuli 45 / 60 m, odstęp przewodów odprowadzających
  15 / 20 m; odstęp separacyjny s = k_i·(k_c/k_m)·l, k_i = 0,04 (III–IV), k_m = 1 (powietrze) [NZW].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import DaneBudynku, Krok, Raport, Warunek, f, fa, wym, wym_zrodlo

R_F = {"niskie": 1e-3, "zwykłe": 1e-2, "wysokie": 1e-1}
P_B_LPS = {None: 1.0, "IV": 0.2, "III": 0.1, "II": 0.05, "I": 0.02}
P_EB_SPD = {None: 1.0, "III-IV": 0.05, "II": 0.02, "I": 0.01}


def klasa_pozarowa(q_f: float) -> str:
    lo, hi = wym("elektryka", "obciazenie_ogniowe_progi", [400, 800]) or [400, 800]
    return "niskie" if q_f < lo else ("zwykłe" if q_f <= hi else "wysokie")


def ryzyko_R1(N_D: float, N_L: float, r_f: float, r_p: float = 1.0, h_z: float = 1.0, r_t: float = 1e-2, L_T: float = 1e-2,
              L_F: float = 1e-2, lps: str | None = None, spd: str | None = None) -> dict:
    """R1 = R_A + R_B + R_U + R_V (PN-EN 62305-2, budynek mieszkalny, jedna strefa)."""
    P_B = P_B_LPS[lps]
    P_A = 1.0 * P_B                     # P_TA = 1 (brak środków przed napięciem dotykowym na zewnątrz)
    P_EB = P_EB_SPD[spd]
    P_U = 1.0 * P_EB * 1.0 * 1.0        # P_TU·P_EB·P_LD·C_LD
    P_V = P_EB * 1.0 * 1.0
    L_A = r_t * L_T
    L_B = r_p * r_f * h_z * L_F
    RA, RB, RU, RV = N_D * P_A * L_A, N_D * P_B * L_B, N_L * P_U * L_A, N_L * P_V * L_B
    return {"R_A": RA, "R_B": RB, "R_U": RU, "R_V": RV, "R1": RA + RB + RU + RV}


@dataclass
class ParametryOdgrom:
    N_G: float | None = None
    C_D: float = 1.0                  # obiekt wolnostojący (zachowawczo; 0,5 — otoczony obiektami podobnej wysokości)
    L_L: float = 1000.0               # m — długość linii zasilającej (nieznana)
    C_I: float = 0.5                  # linia kablowa w ziemi
    C_E: float = 0.5                  # środowisko podmiejskie
    C_T: float = 1.0                  # linia nN
    q_f: float = 780.0                # MJ/m² — mieszkania (PN-EN 1991-1-2 E.4, średnia) [W]
    q_f_80: float = 948.0             # kwantyl 80 %
    r_p: float = 1.0
    r_t: float = 1e-2
    R_T: float | None = None
    rho_gruntu: float = 400.0         # Ω·m — piaski [ZAŁ]
    otok_odsuniecie: float = 1.0      # m od lica ściany


@dataclass
class WynikOdgrom:
    dane: DaneBudynku
    par: ParametryOdgrom
    A_D: float
    H: float
    N_D: float
    N_L: float
    scenariusze: list
    klasa: str
    decyzja: str
    uziom: dict
    lps: dict
    wyrownawcze: list
    warunki: list
    kroki: list
    zalozenia: list

    def do_dict(self) -> dict:
        return {"A_D_m2": round(self.A_D, 0), "N_D": round(self.N_D, 5), "N_L": round(self.N_L, 4), "klasa_pozarowa": self.klasa,
                "decyzja_LPS": self.decyzja, "uziom": self.uziom["typ"].split(" (")[0].split(" —")[0], "R_uziomu_ohm": round(self.uziom["R"], 1)}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def ocena_ryzyka(dane: DaneBudynku, par: ParametryOdgrom | None = None, pv=None) -> WynikOdgrom:
    par = par or ParametryOdgrom()
    from shapely.ops import unary_union
    NG = par.N_G if par.N_G is not None else float(wym("elektryka", "Ng", 1.8) or 1.8)
    RT = par.R_T if par.R_T is not None else float(wym("elektryka", "odgromowa_RT", 1e-5) or 1e-5)
    teren = min((dane.teren_z(c) for c in list(dane.obrys_zabudowy.exterior.coords)[:-1]), default=-0.3) \
        if not dane.obrys_zabudowy.is_empty else -0.3
    czesci = []
    for dd in dane.dachy:
        if dd.typ in ("taras", "wspornik"):
            continue
        Hc = dd.rzedna + (dd.attyka_wys or 0.0) - teren
        czesci.append((dd.obrys, Hc))
    if not czesci:
        czesci = [(dane.obrys_zabudowy, dane.H_max - teren)]
    H = max(h for _, h in czesci)
    A_D = unary_union([g.buffer(3.0 * h, resolution=32) for g, h in czesci]).area
    N_D = NG * A_D * par.C_D * 1e-6
    A_L = 40.0 * par.L_L
    N_L = NG * A_L * par.C_I * par.C_E * par.C_T * 1e-6
    kl = klasa_pozarowa(par.q_f)
    kl80 = klasa_pozarowa(par.q_f_80)
    scen = []
    for nazwa, lps, spd, rp in (("brak ochrony", None, None, par.r_p), ("SPD typ 1 (LPL III–IV) — projektowane (W-186)", None, "III-IV", par.r_p),
                                ("SPD T1 + gaśnica (r_p = 0,5)", None, "III-IV", 0.5), ("LPS IV + SPD T1", "IV", "III-IV", par.r_p),
                                ("LPS III + SPD T1", "III", "III-IV", par.r_p)):
        for klasa in (kl, kl80):
            r = ryzyko_R1(N_D, N_L, R_F[klasa], rp, 1.0, par.r_t, lps=lps, spd=spd)
            scen.append({"nazwa": nazwa, "klasa": klasa, **r, "ok": r["R1"] <= RT})
    base = next(s for s in scen if s["nazwa"].startswith("SPD typ 1") and s["klasa"] == kl)
    base80 = next(s for s in scen if s["nazwa"].startswith("SPD typ 1") and s["klasa"] == kl80)
    if base["ok"] and base80["ok"]:
        dec = "LPS NIEWYMAGANY (R1 ≤ R_T przy SPD T1 dla obu klas obciążenia ogniowego)"
    elif base["ok"]:
        alt = next((s for s in scen if s["klasa"] == kl80 and s["ok"]), None)
        dec = (f"LPS NIEWYMAGANY dla klasy „{kl}” (q_f = {f(par.q_f, 0)} MJ/m²); dla „{kl80}” wymagany dodatkowy środek: "
               f"{alt['nazwa'] if alt else 'LPS'} — rekomendacja: gaśnica w budynku (r_p = 0,5) + uziom przygotowany pod LPS")
    else:
        alt = next((s for s in scen if s["klasa"] == kl and s["ok"]), None)
        dec = f"LPS WYMAGANY — minimalnie: {alt['nazwa'] if alt else 'LPS III + SPD'}"
    kroki = [
        Krok(f"Wysokość budynku nad terenem (najwyższa attyka), części: {len(czesci)}", "H", "", H, "m", "model", 2),
        Krok("Powierzchnia zbierania wyładowań bezpośrednich", "A_D = pole(∪ bufor(obrys_i; 3H_i))", "", A_D, "m²",
             "PN-EN 62305-2 zał. A (A.2)", 0),
        Krok("Liczba wyładowań w obiekt", "N_D = N_G·A_D·C_D·10⁻⁶", f"{f(NG, 1)}·{f(A_D, 0)}·{f(par.C_D, 1)}·10⁻⁶", fa(N_D, 3), "1/rok",
             wym_zrodlo("elektryka", "Ng")),
        Krok("Liczba wyładowań w linię zasilającą (kabel nN)", "N_L = N_G·40·L_L·C_I·C_E·C_T·10⁻⁶",
             f"{f(NG, 1)}·40·{f(par.L_L, 0)}·{f(par.C_I, 1)}·{f(par.C_E, 1)}·{f(par.C_T, 1)}·10⁻⁶", fa(N_L, 3), "1/rok", "zał. A (A.4)"),
        Krok("Klasa ryzyka pożaru: q_f,śr / q_f,80%", "q_f", f"{f(par.q_f, 0)} / {f(par.q_f_80, 0)} MJ/m²", f"{kl} / {kl80}", "",
             "PN-EN 1991-1-2 zał. E tabl. E.4 [W]; progi 400/800 MJ/m² (R7-K02)"),
    ]
    # uziom
    fund = dane.model.fundamenty() if dane.model is not None else {}
    typ_f = fund.get("typ", "lawy")
    podl = None
    try:
        k0 = dane.model.kondygnacja(dane.kondygnacje[0]["id"])
        podl = dane.model.przegroda(k0.podloga)
    except Exception:
        pass
    xps_pod = False
    if podl is not None and typ_f == "plyta":
        ik = next((i for i, w in enumerate(podl.warstwy) if w.konstrukcyjna), 0)
        xps_pod = any("XPS" in w.mat.upper() or "EPS" in w.mat.upper() for w in podl.warstwy[ik + 1:])
    obr = dane.obrys_zabudowy
    otok = typ_f == "plyta" and xps_pod
    if otok:
        typ_u = "otokowy w gruncie (fundament izolowany termicznie — PN-HD 60364-5-54 zał. C.2)"
        A_u = obr.buffer(par.otok_odsuniecie, join_style=2).area
        D = math.sqrt(4 * A_u / math.pi)
        R = 2 * par.rho_gruntu / (3 * D)
        mat = "drut/płaskownik Cu 50 mm² lub StCu Ø10 mm lub StSt 30×3,5 mm, ≥ 0,5 m w gruncie, ≥ 1 m od ścian [ZAŁ]"
    else:
        typ_u = "fundamentowy w ławach (zbrojenie + płaskownik/pręt w betonie) — WT §184 ust. 1" + (
            "; UWAGA: przy izolacji przeciwwodnej z folii > 0,5 mm lub XPS na ławach — uziom otokowy" if typ_f == "lawy" else "")
        A_u = obr.area
        D = math.sqrt(4 * A_u / math.pi)
        R = 2 * par.rho_gruntu / (math.pi * D)
        mat = "pręt stalowy Ø10 mm lub płaskownik 30×3,5 mm w betonie, otulina ≥ 5 cm, mocowany do zbrojenia co ≤ 2 m, bez drutu wiązałkowego (W-187)"
    per = obr.exterior.length
    uziom = {"typ": typ_u, "D": D, "R": R, "material": mat, "wyprowadzenia": ["GSU w pomieszczeniu technicznym (≥ 16 mm² Cu, W-188)",
                                                                               "ZKP / rozdział PEN (jeśli wymaga OSD)",
                                                                               f"{max(4, math.ceil(per / 15))} wyprowadzenia w narożnikach/co ≤ 15 m pod przewody odprowadzające LPS (rezerwa)",
                                                                               "konstrukcja PV (połączenie wyrównawcze, jeden punkt)"]}
    kroki += [Krok(f"Uziom {typ_u.split('(')[0].strip()}: średnica zastępcza", "D = √(4A/π)", f"√(4·{f(A_u, 1)}/π)", D, "m", "", 2),
              Krok("Rezystancja uziemienia (orientacyjnie, ρ = " + f(par.rho_gruntu, 0) + " Ω·m [ZAŁ])",
                   "R ≈ 2ρ/(3D)" if otok else "R ≈ 2ρ/(πD)", f"2·{f(par.rho_gruntu, 0)}/({'3' if otok else 'π'}·{f(D, 2)})", R, "Ω",
                   "DEHN LPG [W]; pomiar po wykonaniu", 1)]
    # LPS — parametry (jeśli potrzebny / rezerwa)
    n_odpr = {"III": max(2, math.ceil(per / 15)), "IV": max(2, math.ceil(per / 20))}
    k_c = 0.44 if n_odpr["IV"] >= 4 else 0.66
    s_sep = 0.04 * k_c / 1.0 * H
    lps = {"klasa": "IV", "oczko": "20 × 20 m (III: 15 × 15 m)", "kula": "60 m (III: 45 m)", "n_odpr": n_odpr, "k_c": k_c, "s": s_sep,
           "opis": "zwody poziome na attykach i w oczkach na dachach płaskich; iglice przy wywiewkach/czerpniach/PV; przewody "
                   "odprowadzające w elewacji (pod okładziną w rurach niepalnych) do złączy kontrolnych i uziomu otokowego"}
    war = [Warunek(f"R1 (SPD T1, klasa „{kl}”) ≤ R_T", base["R1"], "<=", RT, "1/rok", wym_zrodlo("elektryka", "odgromowa_RT"), "W-191", nd=7),
           Warunek(f"R1 (SPD T1, klasa „{kl80}”) ≤ R_T", base80["R1"], "<=", RT, "1/rok", "PN-EN 62305-2 [NZW]", "W-191", nd=7)]
    if pv is not None and pv.dach:
        war.append(Warunek("Odstęp separacyjny PV od zwodów LPS (jeśli LPS) — wymagany s", s_sep, "info", None, "m",
                           "PN-EN 62305-3 p. 6.3 [NZW]", "W-191"))
    wyr = [["Główna szyna uziemiająca (GSU)", "pomieszczenie techniczne, przy RG", "przewód uziemiający ≥ 16 mm² Cu (W-188)"],
           ["Wodociąg metalowy (przed/za wodomierzem — mostek)", "zestaw wodomierzowy", "≥ 6 mm² Cu (tylko przy rurach przewodzących)"],
           ["Rury c.o./c.w.u. metalowe, zasobnik, bufor", "pom. techniczne", "≥ 6 mm² Cu"],
           ["Kanały wentylacyjne metalowe, obudowa rekuperatora", "", "≥ 6 mm² Cu (WT §183 ust. 1a)"],
           ["Zbrojenie fundamentów / płyty", "zaciski przyłączeniowe", "≥ 16 mm² Cu / Ø10 Fe"],
           ["Konstrukcja PV (uziemienie funkcjonalne, jeden punkt)", "dach", "wg DTR i 5-54 (≥ 6 mm² Cu) (712.444.5.5.101)"],
           ["Obudowa szafki teletechnicznej / RACK", "", "≥ 6 mm² Cu (WT §183 ust. 1a pkt 8)"],
           ["Łazienki — miejscowe połączenia wyrównawcze", "łazienki", "wg PN-HD 60364-7-701:2025-02 (przy tworzywach zwykle niewymagane)"],
           ["Balustrady, lamele stalowe/aluminiowe na elewacji, stolarka metalowa przy zwodach", "", "przy LPS — w strefie odstępu separacyjnego"]]
    zal = [f"C_D = {f(par.C_D, 1)}, L_L = {f(par.L_L, 0)} m, C_I = {f(par.C_I, 1)}, C_E = {f(par.C_E, 1)}, r_t = {fa(par.r_t)}, r_p = {f(par.r_p, 1)}, "
           "h_z = 1, L_T = L_F = 10⁻² [NZW — współczynniki wg R7-K05; pełna analiza w PT programem wg PN-EN IEC 62305-2:2025].",
           "Linia telekomunikacyjna: światłowód dielektryczny — pominięta w analizie.",
           "Niezależnie od wyniku: uziom (otokowy lub fundamentowy) z wyprowadzeniami pod LPS i SPD typu 1+2 w RG (R7 §3.7)."]
    return WynikOdgrom(dane=dane, par=par, A_D=A_D, H=H, N_D=N_D, N_L=N_L, scenariusze=scen, klasa=kl, decyzja=dec, uziom=uziom,
                       lps=lps, wyrownawcze=wyr, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikOdgrom) -> Raport:
    R = Raport("Ochrona odgromowa — ocena ryzyka (uproszczona), uziom, połączenia wyrównawcze",
               f"Obiekt: {w.dane.nazwa}. PN-EN 62305-2 (WT: 2008; aktualna PN-EN IEC 62305-2:2025-09). Wynik wstępny — [NZW].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §53 ust. 2, §184 ust. 1–3 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-187, W-188, W-191; D-13."] + w.zalozenia)
    R.h(2, "2. Częstość zagrożeń")
    R.kroki(w.kroki[:5])
    R.h(2, "3. Ryzyko R1 — scenariusze")
    R.tab(["Scenariusz", "Klasa pożarowa", "R_A", "R_B", "R_U", "R_V", "R1", "R1 ≤ R_T = 10⁻⁵"],
          [[s["nazwa"], s["klasa"], fa(s["R_A"]), fa(s["R_B"]), fa(s["R_U"]), fa(s["R_V"]), fa(s["R1"]), "tak" if s["ok"] else "**NIE**"]
           for s in w.scenariusze], "llrrrrrl")
    R.p(f"**Decyzja: {w.decyzja}.**")
    R.h(2, "4. Uziom")
    R.kroki(w.kroki[5:])
    R.lista([f"Typ: {w.uziom['typ']}.", f"Materiał: {w.uziom['material']}.", "Wyprowadzenia: " + "; ".join(w.uziom["wyprowadzenia"]) + ".",
             "TN-S: brak normowej wartości rezystancji uziemienia GSU; przy LPS zalecane R ≤ 10 Ω (PN-EN 62305-3) — sprawdzić pomiarem; "
             "OSD może określić wymagania dla uziemienia PEN w warunkach przyłączenia."])
    R.h(2, "5. LPS — parametry (gdy wymagany / rezerwa)")
    L = w.lps
    R.lista([f"Klasa LPS: IV (III przy wyniku rozstrzygającym „wysokie”); oczka zwodów {L['oczko']}; promień kuli {L['kula']}.",
             f"Liczba przewodów odprowadzających: IV — {L['n_odpr']['IV']}, III — {L['n_odpr']['III']} (co 20/15 m obwodu).",
             f"Odstęp separacyjny (PV, instalacje na dachu): s = k_i·(k_c/k_m)·l = 0,04·({f(L['k_c'], 2)}/1)·{f(w.H, 2)} ≈ **{f(L['s'], 2)} m** [NZW].",
             L["opis"] + "."])
    R.h(2, "6. Połączenia wyrównawcze")
    R.tab(["Element", "Miejsce", "Przekrój / uwagi"], w.wyrownawcze, "lll")
    R.h(2, "7. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("PN-EN 62305-2:2008/2012 (zał. A–C) — metodyka; PN-EN IEC 62305-2:2025-09 (EN) — do PT", "Rejestr R7: R7-K01…K05, R7-G01…G08; D-13",
             "SEP (Boczkowski 2013) — N_G = 1,8 dla Poznania [W]", "PN-EN 1991-1-2 zał. E tabl. E.4 — gęstość obciążenia ogniowego [W]",
             "DEHN, Lightning Protection Guide — rezystancja uziomów otokowych/fundamentowych [W]")
    return R
