"""Charakterystyka energetyczna budynku — metoda miesięczna wg metodologii (rozp. MIiR z 27.02.2015, Dz.U. 2015 poz. 376,
zm. Dz.U. 2017 poz. 22, 2019 poz. 1829, 2023 poz. 697 — w_el = 2,50; rejestr W-240…W-242, R6-13…R6-21).

Zakres (zał. 1 metodologii):
* pkt 5.2 — Q_H,nd = Σ_n (Q_H,ht,n − η_H,gn,n·Q_H,gn,n) (wzory (50)–(52), wartości > 0);
  Q_tr,n = H_tr·(θ_int,H − θ_e,n)·t_M·10⁻³ (54), H_tr = H_tr,ie + H_tr,iue + H_tr,ig (+ H_TB) (55) — H wg metody
  podstawowej PN-EN 12831 (grunt: f_g1·f_g2·G_w·A·U_equiv); Q_ve,n = H_ve·(θ_int,H − θ_e,n)·t_M·10⁻³ (56),
  H_ve = ρ_a·c_a·Σ b_ve,k·V_ve,k (57): wentylacja nawiewno-wywiewna k=1: b = 1 − η_oc, V = r_n·V_su; k=2: b = 1,
  V_x,su = V·n50·e/(1 + (f/e)·((V_su − V_ex)/(V·n50))²), e = 0,07, f = 15 (PN-EN ISO 13789 tab. B) [NZW] (tab. 21);
  zyski: Q_sol = Σ C_i·A_i·I_i·F_sh,gl·F_sh·g_gl (59), g_gl = F_w·g_n, F_w = 0,9 (PN-EN ISO 13790 p. 11.4.2) [NZW];
  Q_int = q_int·A_f·t_M·10⁻³ (60), q_int = 6,8 W/m² (tab. 26);
  η_H,gn — PN-EN ISO 13790:2008 p. 12.2.1.1: γ = Q_gn/Q_ht, a_H = 1 + τ/15 h, τ = C_m/3600/(H_tr + H_ve),
  η = (1 − γ^a)/(1 − γ^(a+1)) (γ ≠ 1), a/(a+1) (γ = 1); C_m wg klasy (PN-EN ISO 13790 tab. 12) [NZW];
* pkt 5.3 — Q_W,nd = V_Wi·A_f·c_W·ρ_W·(θ_W − θ_0)·k_R·t_R/3600 (61), V_Wi = 1,40 dm³/(m²·d), k_R = 0,90 (tab. 27);
* pkt 4.1 — Q_K,H = Q_H,nd/(η_H,g·η_H,s·η_H,d·η_H,e); Q_K,W = Q_W,nd/(η_W,g·η_W,s·η_W,d); η wg deklaracji producenta
  (SCOP PN-EN 14825, COP_cwu PN-EN 16147) albo tab. 2, 3, 6, 8, 9, 12, 14; energia pomocnicza (37)–(38) z mocy
  zainstalowanych urządzeń (dopuszczone w pkt 4.1.6.5) albo tab. 20;
* pkt 3.1 — Q_p = Σ w_i·Q_K,i + w_el·E_el,pom (5)–(8); w_el = 2,50, gaz 1,10, energia słoneczna 0,00 (tab. 1);
* pkt 2.1 — EP = Q_p/A_f, EK = Q_K/A_f, EU = Q_u/A_f; pkt 6 — E_CO2 (72)–(77) ze wskaźnikami KOBiZE;
  pkt 8 — U_oze (100) (PC: Q_k,oze = Q_k·(1 − 1/η_g));
* WT § 329 — EP ≤ EP_max = 70 kWh/(m²·rok) (+ΔEP_C = 5·A_f,C/A_f tylko przy chłodzeniu).
PV — `energia.pv` (autokonsumpcja miesięczna). Dane klimatyczne — TMY Poznań (MIiR).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..wspolne import (GODZINY_MIES, DNI_MIES, INT, NZW, PRZYKL, RHO_C_WH, ZAL, Zalozenia, fmt, miesiace_pl,
                       naglowek_raportu, ok, tabela_md, wym, wyrob)
from .klimat import klimat_miesieczny, opis_zrodla
from .pv import DanePV, autokonsumpcja, dane_pv, produkcja_miesieczna

POJEMNOSC = {"bardzo_lekka": 80e3, "lekka": 110e3, "srednia": 165e3, "ciezka": 260e3, "bardzo_ciezka": 370e3}
W_I = {"el": 2.50, "gaz": 1.10, "pv": 0.00}


@dataclass
class Pomocnicze:
    opis: str
    P_W: float
    h_rok: float
    system: str = "H"        # H | W
    tryb: str = "sezon"      # sezon (miesiące grzewcze) | ciagly | cwu


@dataclass
class System:
    nazwa: str
    opis: str
    nosnik_H: str = "el"
    eta_H_g: float = 4.5
    eta_H_s: float = 1.0
    eta_H_d: float = 0.96
    eta_H_e: float = 0.89
    zrodlo_H: str = ""
    nosnik_W: str = "el"
    eta_W_g: float = 3.2
    eta_W_s: float = 0.85
    eta_W_d: float = 0.80
    zrodlo_W: str = ""
    pomocnicze: list[Pomocnicze] = field(default_factory=list)
    pv: DanePV | None = None
    autokonsumpcja: Any = "symulacja"      # 'symulacja' | float | lista 12
    sterowanie_cwu_pv: bool = True
    udzial_grzalki: float = 0.0
    E_dezynfekcja_kWh: float = 0.0
    capex_zl: float | None = None
    status: str = ""

    @property
    def eta_H_g_ef(self) -> float:
        """Sprawność wytwarzania z udziałem grzałki (η = 1,0) w PC: 1/((1 − x)/η_g + x)."""
        if self.nosnik_H != "el" or self.udzial_grzalki <= 0:
            return self.eta_H_g
        x = self.udzial_grzalki
        return 1.0 / ((1 - x) / self.eta_H_g + x)

    @property
    def eta_H_tot(self) -> float:
        return self.eta_H_g_ef * self.eta_H_s * self.eta_H_d * self.eta_H_e

    @property
    def eta_W_tot(self) -> float:
        return self.eta_W_g * self.eta_W_s * self.eta_W_d


@dataclass
class WynikEP:
    system: System
    A_f: float
    V: float
    theta_int: float
    H_tr_skladniki: dict
    H_tr: float
    H_ve: float
    V_su_m3h: float
    V_x_m3h: float
    eta_oc: float
    C_m: float
    tau_h: float
    a_H: float
    mies: dict                  # tablice 12-elementowe
    Q_H_nd: float
    Q_W_nd: float
    Q_K_H: float
    Q_K_W: float
    E_pom_H: float
    E_pom_W: float
    E_PV: float
    E_PV_sys: float
    E_PV_a: list
    Q_K: float
    Q_P: float
    EU: float
    EK: float
    EP: float
    EP_max: float
    E_CO2_t: float
    U_oze: float
    koszt_zl: float
    koszt_skladniki: dict
    pv_sym: dict | None = None
    zal: Zalozenia | None = None

    @property
    def spelnia(self) -> bool:
        return self.EP <= self.EP_max + 1e-9

    @property
    def EP_H(self):
        return self.mies["Q_P_H"].sum() / self.A_f

    @property
    def EP_W(self):
        return self.mies["Q_P_W"].sum() / self.A_f


def eta_gn(gamma: float, a: float) -> float:
    """PN-EN ISO 13790:2008 wzory (52)–(53): współczynnik wykorzystania zysków ciepła."""
    if gamma <= 0:
        return 1.0
    if abs(gamma - 1.0) < 1e-9:
        return a / (a + 1.0)
    return (1.0 - gamma ** a) / (1.0 - gamma ** (a + 1.0))


def q_w_nd(A_f: float, V_Wi: float | None = None, k_R: float | None = None, theta_W: float = 55.0,
           theta_0: float = 10.0, t_R: int = 365) -> float:
    """Metodologia wzór (61), tab. 27 — roczne zapotrzebowanie na energię użytkową do c.w.u. [kWh/rok]."""
    V_Wi = float(wym("energia", "V_Wi", 1.40)) if V_Wi is None else V_Wi
    k_R = float(wym("energia", "k_R", 0.90)) if k_R is None else k_R
    return V_Wi * A_f * 4.19 * 1.0 * (theta_W - theta_0) * k_R * t_R / 3600.0


# --------------------------------------------------------------------------------------------------
# Systemy
# --------------------------------------------------------------------------------------------------
def system_projektowy(cfg: dict, went, A_f: float, dobor: dict | None = None, zal: Zalozenia | None = None,
                      *, z_pv: bool = True) -> System:
    """PC powietrze–woda R290 + ogrzewanie podłogowe z regulacją pokojową + c.w.u. z PC (zasobnik) + wentylacja z odzyskiem
    + PV (autokonsumpcja). Parametry z `energia.ogrzewanie/cwu/pv` modelu, domyślnie dane przykładowe."""
    og = cfg.get("ogrzewanie") or {}
    cw = cfg.get("cwu") or {}
    zr = og.get("zrodlo")
    pc = dict(wyrob("pompa_ciepla", zr if isinstance(zr, str) else "PC_R290_monoblok"))
    if isinstance(zr, dict):
        pc.update(zr)
    temp_zas = float(og.get("temp_zasilania", 35))
    scop = float(og.get("SCOP", pc.get("SCOP_35" if temp_zas <= 40 else "SCOP_55", 4.5)))
    zb = dict(wyrob("zasobnik_cwu", cw.get("zasobnik", "Z250")))
    Q_W = q_w_nd(A_f)
    eta_W_s = cw.get("eta_W_s")
    if eta_W_s is None and zb.get("strata_W"):
        straty = float(zb["strata_W"]) * 8760 / 1000.0
        eta_W_s = Q_W / (Q_W + straty)
    eta_W_s = float(eta_W_s if eta_W_s is not None else 0.85)
    cyrk = cw.get("cyrkulacja", {"moc_W": 5.0, "h_doba": 8.0})
    eta_W_d = float(cw.get("eta_W_d", 0.80 if cyrk else 0.60))
    V_zb = float(zb.get("V_dm3", 250))
    E_dez = float(cw.get("dezynfekcja_kWh_rok", V_zb * 4.19 * 15 / 3600 * 52))    # 1×/tydz. 55→70 °C grzałką
    pom = [Pomocnicze("pompa obiegowa ogrzewania podłogowego (EC)", float(og.get("pompy_W", 25)), 0.0, "H", "sezon"),
           Pomocnicze("sterownik/grzałka tacy PC (poza SCOP)", float(pc.get("P_pomocnicze_W", 15)), 8760.0, "H", "ciagly"),
           Pomocnicze("wentylatory centrali (P = SFP·q)", float(went.P_el_W), 8760.0, "H", "ciagly")]
    if cyrk:
        pom.append(Pomocnicze("pompa cyrkulacyjna c.w.u. z zegarem", float(cyrk.get("moc_W", 5)),
                              float(cyrk.get("h_doba", 8)) * 365, "W", "ciagly"))
    pvc = cfg.get("pv", {} if cfg.get("pv") is None else cfg.get("pv")) if z_pv else False
    s = System("A: PC R290 + PV + rekuperacja", "pompa ciepła powietrze–woda (R290) + ogrzewanie podłogowe 35/28 °C "
               "z regulacją pokojową + c.w.u. z PC (zasobnik) + wentylacja z odzyskiem + PV",
               "el", scop, float(og.get("eta_H_s", 1.0)), float(og.get("eta_H_d", 0.96)), float(og.get("eta_H_e", 0.89)),
               f"SCOP = {fmt(scop, 2)} (PN-EN 14825, {pc.get('zrodlo', '')}); η_H,e = 0,89 (tab. 3 lp. 6b), "
               "η_H,d = 0,96 (tab. 6 lp. 3a), η_H,s = 1,00 (tab. 8 lp. 3)",
               "el", float(cw.get("COP", pc.get("COP_cwu", 3.2))), eta_W_s, eta_W_d,
               f"COP_cwu = {fmt(pc.get('COP_cwu', 3.2), 2)} (PN-EN 16147); η_W,s = {fmt(eta_W_s, 3)} "
               f"(strata zasobnika {zb.get('strata_W', '—')} W); η_W,d = {fmt(eta_W_d, 2)} (tab. 12 lp. 6.1a — cyrkulacja "
               "z ograniczeniem czasu pracy)", pom, dane_pv(pvc) if pvc is not False else None,
               (pvc or {}).get("autokonsumpcja", "symulacja") if isinstance(pvc, dict) else "symulacja",
               bool((pvc or {}).get("sterowanie_cwu_pv", True)) if isinstance(pvc, dict) else True,
               float((dobor or {}).get("udzial_grzalki", 0.0)), E_dez, capex_zl=None, status=PRZYKL)
    cx = wyrob("ceny").get("capex_zl", {}) or {}
    s.capex_zl = cfg.get("capex_A") or ((cx.get("PC_R290_z_zasobnikiem") or 0) + ((cx.get("PV_6_5kWp") or 0) if s.pv else 0)
                                        or None)
    if zal:
        zal.dodaj(f"PC: SCOP = {fmt(scop, 2)}, COP_cwu = {fmt(s.eta_W_g, 2)}, udział grzałki w ogrzewaniu "
                  f"{fmt(s.udzial_grzalki * 100, 2)} % (TMY)", PRZYKL, pc.get("zrodlo", ""))
        zal.dodaj(f"Dezynfekcja termiczna c.w.u. grzałką: {fmt(E_dez, 0)} kWh/rok (1×/tydz., {fmt(V_zb, 0)} dm³, 55→70 °C)",
                  ZAL, "WT § 120 ust. 2a; rejestr W-133")
    return s


def system_gazowy(A_f: float, went, cfg: dict | None = None) -> System:
    """System konwencjonalny do analizy RPB § 20 ust. 1 pkt 10: gazowy kocioł kondensacyjny (ogrzewanie + c.w.u.
    z zasobnikiem), ogrzewanie podłogowe, wentylacja z odzyskiem, bez PV; sprawności i energia pomocnicza — wartości
    tabelaryczne metodologii (tab. 2 lp. 16a, 9 lp. 5a, 20 lp. 2, 6a, 7a)."""
    k = wyrob("kociol_gazowy", "kondensacyjny_20kW")
    pom = [Pomocnicze("pompa obiegowa ogrzewania podłogowego (tab. 20 lp. 2: 0,50 W/m² × 6700 h)", 0.50 * A_f, 6700.0, "H", "sezon"),
           Pomocnicze("napęd i regulacja kotła — ogrzewanie (tab. 20 lp. 7a: 0,50 W/m² × 2520 h)",
                      (0.50 if A_f <= 250 else 0.15) * A_f, 2520.0 if A_f <= 250 else 3900.0, "H", "sezon"),
           Pomocnicze("wentylatory centrali (P = SFP·q)", float(went.P_el_W), 8760.0, "H", "ciagly"),
           Pomocnicze("napęd i regulacja kotła — c.w.u. (tab. 20 lp. 6a: 1,40 W/m² × 310 h)",
                      (1.40 if A_f <= 250 else 0.50) * A_f, 310.0 if A_f <= 250 else 410.0, "W", "ciagly"),
           Pomocnicze("pompa cyrkulacyjna c.w.u. z zegarem", 5.0, 8 * 365, "W", "ciagly")]
    return System("B: kocioł gazowy kondensacyjny + rekuperacja", "gazowy kocioł kondensacyjny 55/45 °C ≤ 50 kW "
                  "(ogrzewanie podłogowe z regulacją pokojową, c.w.u. z zasobnika), wentylacja z odzyskiem, bez PV",
                  "gaz", float(k.get("eta_H_g", 0.94)), 1.0, 0.96, 0.89,
                  "η_H,g = 0,94 (tab. 2 lp. 16a), η_H,e = 0,89, η_H,d = 0,96",
                  "gaz", float(k.get("eta_W_g", 0.85)), 0.85, 0.80, "η_W,g = 0,85 (tab. 9 lp. 5a), η_W,s = 0,85, η_W,d = 0,80",
                  pom, None, capex_zl=(cfg or {}).get("capex_B") or ((wyrob("ceny").get("capex_zl") or {}).get(
                      "kociol_gazowy_z_zasobnikiem", 0) + (wyrob("ceny").get("capex_zl") or {}).get(
                      "przylacze_gazowe_i_instalacja", 0) or None), status="wartości tabelaryczne metodologii")


def system_pc_domyslny(A_f: float, went) -> System:
    """PC z wartościami domyślnymi metodologii (tab. 2 lp. 21b: 3,00; tab. 9 lp. 11: 2,60; η_W,d = 0,60; tab. 20) —
    wariant wrażliwości (R6 3.3: EP ≈ 99 przy wartościach domyślnych)."""
    pom = [Pomocnicze("pompy obiegowe ogrzewania podłogowego (tab. 20 lp. 2)", 0.50 * A_f, 6700.0, "H", "sezon"),
           Pomocnicze("wentylator centrali nawiewno-wywiewnej (tab. 20 lp. 12a)", 0.50 * A_f, 8760.0, "H", "ciagly"),
           Pomocnicze("pompa ładująca zasobnik c.w.u. (tab. 20 lp. 4)", (0.25 if A_f <= 250 else 0.20) * A_f,
                      270.0 if A_f <= 250 else 580.0, "W", "ciagly")]
    return System("C: PC — wartości domyślne metodologii, bez PV", "PC powietrze–woda 35/28 °C, η wg tab. 2, 3, 6, 9, 12, 14, "
                  "energia pomocnicza wg tab. 20", "el", 3.00, 1.0, 0.96, 0.89, "tab. 2 lp. 21b, 3 lp. 6b, 6 lp. 3a",
                  "el", 2.60, 0.85, 0.60, "tab. 9 lp. 11, 14 lp. 1d, 12 lp. 3.1", pom, None,
                  status="wartości tabelaryczne metodologii")


# --------------------------------------------------------------------------------------------------
# Obliczenie
# --------------------------------------------------------------------------------------------------
def oblicz_ep(ob, went, system: System, *, obc=None, n50: float | None = None, pojemnosc: str | float | None = None,
              r_n: float | None = None, F_w: float = 0.9, zal: Zalozenia | None = None) -> WynikEP:
    zal = zal if zal is not None else Zalozenia()
    cfg = ob.cfg
    br = ob.bryla
    k = klimat_miesieczny()
    tM = np.array(GODZINY_MIES, float)
    A_f = br.A_f
    V = br.V_netto
    th = br.theta_srednia()
    # --- H_tr ---
    b_u = (obc.b_u if obc is not None else {})
    Hie = Hiue = Hig = 0.0
    sk = {"ściany zewnętrzne": 0.0, "okna i drzwi balkonowe": 0.0, "drzwi zewnętrzne": 0.0, "dachy/stropodachy": 0.0,
          "stropy nad powietrzem zewn.": 0.0, "grunt (f_g1·f_g2·G_w·A·U)": 0.0, "przestrzenie nieogrzewane (b_u)": 0.0,
          "mostki cieplne H_TB": ob.H_TB}
    g = ob.grunt
    for e in br.elementy_obudowy():
        U = ob.U(e)
        if e.sasiad == "zewn":
            h = e.A * U
            Hie += h
            key = {"sciana": "ściany zewnętrzne", "okno": "okna i drzwi balkonowe", "drzwi": "drzwi zewnętrzne",
                   "dach": "dachy/stropodachy", "strop": "stropy nad powietrzem zewn.", "podloga": "stropy nad powietrzem zewn.",
                   "brama": "drzwi zewnętrzne"}.get(e.rodzaj, "ściany zewnętrzne")
            sk[key] += h
        elif e.sasiad == "grunt":
            f = (g.f_g1 * g.f_g2 * g.G_w) if g else 0.461
            h = f * e.A * U
            Hig += h
            sk["grunt (f_g1·f_g2·G_w·A·U)"] += h
        else:
            b = b_u.get(e.sasiad, 0.8)
            h = e.A * U * b
            Hiue += h
            sk["przestrzenie nieogrzewane (b_u)"] += h
    H_tr = Hie + Hiue + Hig + ob.H_TB
    # --- H_ve ---
    n50 = float(n50 if n50 is not None else cfg.get("n50", wym("energia", "n50_cel", 1.0)))
    r_n = float(r_n if r_n is not None else (cfg.get("wentylacja") or {}).get("r_n", 1.0))
    eta_oc = float(went.eta)
    V_su = went.suma_naw * r_n
    V_ex = went.suma_wyw * r_n
    e_, f_ = 0.07, 15.0
    V_x = V * n50 * e_ / (1 + f_ / e_ * ((V_su - V_ex) / (V * n50)) ** 2) if V * n50 > 0 else 0.0
    H_ve = RHO_C_WH * ((1 - eta_oc) * V_su + V_x)
    # --- zyski ---
    q_int = float(wym("energia", "q_int", 6.8))
    Q_int = q_int * A_f * tM / 1000.0
    Q_sol = np.zeros(12)
    okna_sol = []
    for e in br.elementy_obudowy():
        if e.rodzaj != "okno" or e.sasiad != "zewn":
            continue
        wo = ob.okna[e.id]
        I = k.I(e.azymut, 90.0)
        Fsh = np.array(ob.zacienienie[e.id]["F_sh"]) if e.id in ob.zacienienie else np.ones(12)
        g_gl = F_w * (wo.g_n if wo.g_n is not None else 0.5)
        q = wo.C * e.A * I * Fsh * g_gl
        Q_sol += q
        okna_sol.append((e.id, e.azymut, e.A, wo.C, g_gl, float(q.sum())))
    # --- bilans miesięczny ---
    if pojemnosc is None:
        pojemnosc = cfg.get("pojemnosc", "ciezka")
    C_m = (POJEMNOSC.get(pojemnosc, 260e3) if isinstance(pojemnosc, str) else float(pojemnosc)) * A_f
    tau = C_m / 3600.0 / (H_tr + H_ve)
    a_H = 1.0 + tau / 15.0
    dT = th - k.theta_e
    Q_tr = H_tr * dT * tM / 1000.0
    Q_ve = H_ve * dT * tM / 1000.0
    Q_ht = Q_tr + Q_ve
    Q_gn = Q_int + Q_sol
    gam = np.where(Q_ht > 0, Q_gn / np.maximum(Q_ht, 1e-9), 99.0)
    eta = np.array([eta_gn(gg, a_H) for gg in gam])
    Q_Hnd_n = np.maximum(Q_ht - eta * Q_gn, 0.0)
    Q_Hnd = float(Q_Hnd_n.sum())
    Q_Wnd = q_w_nd(A_f)
    Q_Wnd_n = Q_Wnd * np.array(DNI_MIES) / 365.0
    # --- energia końcowa ---
    Q_KH_n = Q_Hnd_n / system.eta_H_tot
    Q_KW_n = Q_Wnd_n / system.eta_W_tot
    if system.nosnik_W == "el" and system.E_dezynfekcja_kWh:
        Q_KW_n = Q_KW_n + system.E_dezynfekcja_kWh * np.array(DNI_MIES) / 365.0
    sezon = Q_Hnd_n > 0.02 * max(Q_Hnd_n.max(), 1e-9)
    h_sezon = float(tM[sezon].sum())
    E_H_n = np.zeros(12)
    E_W_n = np.zeros(12)
    for p in system.pomocnicze:
        if p.tryb == "sezon":
            h = p.h_rok if p.h_rok > 0 else h_sezon
            dist = np.where(sezon, tM, 0.0)
            dist = dist / dist.sum() if dist.sum() else tM / tM.sum()
            E = p.P_W * h / 1000.0 * dist
            if p.h_rok <= 0:
                p.h_rok = h
        else:
            E = p.P_W * p.h_rok / 1000.0 * tM / tM.sum()
        if p.system == "W":
            E_W_n += E
        else:
            E_H_n += E
    # --- PV ---
    E_pv_n = np.zeros(12)
    a_n = [0.0] * 12
    pv_sym = None
    el_sys_n = (Q_KH_n if system.nosnik_H == "el" else 0) + (Q_KW_n if system.nosnik_W == "el" else 0) + E_H_n + E_W_n
    if system.pv is not None:
        E_pv_n = produkcja_miesieczna(system.pv)
        if system.autokonsumpcja == "symulacja":
            P_st = sum(p.P_W for p in system.pomocnicze if p.tryb == "ciagly" and p.system == "H")
            pv_sym = autokonsumpcja(system.pv, Q_KH_n if system.nosnik_H == "el" else np.zeros(12),
                                    Q_KW_n if system.nosnik_W == "el" else np.zeros(12), P_st,
                                    E_dom_rok=float((cfg.get("pv") or {}).get("E_dom_kWh", 2500.0))
                                    if isinstance(cfg.get("pv"), dict) else 2500.0,
                                    sterowanie_cwu_pv=system.sterowanie_cwu_pv)
            a_n = pv_sym["a_n"]
        elif isinstance(system.autokonsumpcja, (int, float)):
            a_n = [float(system.autokonsumpcja)] * 12
        else:
            a_n = list(system.autokonsumpcja)
    E_pv_sys_n = np.minimum(np.array(a_n) * E_pv_n, el_sys_n)
    udz = np.where(el_sys_n > 0, E_pv_sys_n / np.maximum(el_sys_n, 1e-9), 0.0)
    # --- energia pierwotna ---
    wH = W_I[system.nosnik_H]
    wW = W_I[system.nosnik_W]
    w_el = float(wym("energia", "w_el_siec", 2.5))
    wH = w_el if system.nosnik_H == "el" else wH
    wW = w_el if system.nosnik_W == "el" else wW
    Q_P_H = wH * Q_KH_n * (1 - udz if system.nosnik_H == "el" else 1) + w_el * E_H_n * (1 - udz)
    Q_P_W = wW * Q_KW_n * (1 - udz if system.nosnik_W == "el" else 1) + w_el * E_W_n * (1 - udz)
    Q_P = float(Q_P_H.sum() + Q_P_W.sum())
    Q_K = float(Q_KH_n.sum() + Q_KW_n.sum() + E_H_n.sum() + E_W_n.sum())
    EU = (Q_Hnd + Q_Wnd) / A_f
    EK = Q_K / A_f
    EP = Q_P / A_f
    dEP_C = 0.0
    if cfg.get("chlodzenie"):
        dEP_C = float(wym("energia", "dEP_C_wspolczynnik", 5)) * float(cfg.get("A_f_C", A_f)) / A_f
    EP_max = float(wym("energia", "EP_max", 70)) + dEP_C
    # --- CO2 (metodologia pkt 6; KOBiZE) ---
    em = wyrob("emisje")
    We_el = float(em.get("energia_elektryczna_kgCO2_MWh", 553)) / 1000.0         # t/MWh
    We_gaz = float(em.get("gaz_ziemny_kgCO2_GJ", 56.16)) * 3.6 / 1000.0          # t/MWh
    E_el_siec = float(((el_sys_n) * (1 - udz)).sum())
    Q_gaz = float((Q_KH_n.sum() if system.nosnik_H == "gaz" else 0) + (Q_KW_n.sum() if system.nosnik_W == "gaz" else 0))
    E_CO2 = (E_el_siec * We_el + Q_gaz * We_gaz) / 1000.0
    # --- U_oze (pkt 8, wzór (100)) [INT] ---
    oze = 0.0
    if system.nosnik_H == "el" and system.eta_H_g > 1:
        oze += float(Q_KH_n.sum()) * (1 - 1 / system.eta_H_g_ef) + float((Q_KH_n * udz).sum()) / system.eta_H_g_ef
    if system.nosnik_W == "el" and system.eta_W_g > 1:
        oze += float(Q_KW_n.sum()) * (1 - 1 / system.eta_W_g) + float((Q_KW_n * udz).sum()) / system.eta_W_g
    oze += float(((E_H_n + E_W_n) * udz).sum())
    U_oze = min(100.0, 100.0 * oze / Q_K) if Q_K else 0.0
    # --- koszty [ZAŁ] ---
    ceny = wyrob("ceny")
    k_el = E_el_siec * float(ceny.get("energia_elektryczna_zl_kWh", 1.05)) + 12 * float(ceny.get("energia_elektryczna_oplaty_stale_zl_mies", 45))
    k_gaz = (Q_gaz * float(ceny.get("gaz_zl_kWh", 0.36)) + 12 * float(ceny.get("gaz_oplaty_stale_zl_mies", 55))) if Q_gaz > 0 else 0.0
    mies = {"theta_e": k.theta_e, "Q_tr": Q_tr, "Q_ve": Q_ve, "Q_ht": Q_ht, "Q_int": Q_int, "Q_sol": Q_sol, "Q_gn": Q_gn,
            "gamma": gam, "eta": eta, "Q_H_nd": Q_Hnd_n, "Q_W_nd": Q_Wnd_n, "Q_K_H": Q_KH_n, "Q_K_W": Q_KW_n,
            "E_pom_H": E_H_n, "E_pom_W": E_W_n, "E_PV": E_pv_n, "E_PV_sys": E_pv_sys_n, "a_n": np.array(a_n),
            "Q_P_H": Q_P_H, "Q_P_W": Q_P_W, "E_el_sys": el_sys_n}
    W = WynikEP(system, A_f, V, th, sk, H_tr, H_ve, V_su, V_x, eta_oc, C_m, tau, a_H, mies, Q_Hnd, Q_Wnd,
                float(Q_KH_n.sum()), float(Q_KW_n.sum()), float(E_H_n.sum()), float(E_W_n.sum()), float(E_pv_n.sum()),
                float(E_pv_sys_n.sum()), list(a_n), Q_K, Q_P, EU, EK, EP, EP_max, E_CO2, U_oze, k_el + k_gaz,
                {"energia elektryczna": k_el, "gaz": k_gaz}, pv_sym, zal)
    W.mies["okna_sol"] = okna_sol
    zal.dodaj(f"Dane klimatyczne: {opis_zrodla()}", "")
    zal.dodaj(f"θ_int,H = {fmt(th, 2)} °C (średnia ważona kubaturą temperatur pomieszczeń wg WT § 134 ust. 2)", "",
              "metodologia pkt 5.2.3.1.1, przypis *")
    zal.dodaj(f"Pojemność cieplna: klasa „{pojemnosc}” — C_m = {fmt(C_m / A_f / 1000, 0)} kJ/(m²·K)·A_f", NZW,
              "PN-EN ISO 13790:2008 tab. 12")
    zal.dodaj(f"Infiltracja przy pracy wentylatorów: V_x = V·n50·e/(1 + (f/e)·(ΔV/(V·n50))²), n50 = {fmt(n50, 1)} h⁻¹ "
              "(cel — do potwierdzenia próbą; bez próby metodologia każe przyjąć 4 h⁻¹), e = 0,07, f = 15", NZW,
              "metodologia tab. 21 i przypis do V_x,su; PN-EN ISO 13789")
    zal.dodaj("Zyski słoneczne: C_i = A_g/A_w z obliczeń U_w, g_gl = 0,9·g_n, F_sh,gl = 1 (osłony ruchome podniesione "
              "w sezonie grzewczym), F_sh — zacienienie stałe z TMY", NZW, "metodologia wzór (59); PN-EN ISO 13790 p. 11.4")
    zal.dodaj(f"Wskaźniki emisji CO2: energia elektryczna {fmt(We_el * 1000, 0)} kg/MWh; gaz ziemny "
              f"{fmt(em.get('gaz_ziemny_kgCO2_GJ'), 2)} kg/GJ", "", f"{em.get('energia_elektryczna_zrodlo')}; "
              f"{em.get('gaz_ziemny_zrodlo')}")
    zal.dodaj(f"Ceny energii (koszty eksploatacji, poza EP): {fmt(ceny.get('energia_elektryczna_zl_kWh'), 2)} zł/kWh el., "
              f"{fmt(ceny.get('gaz_zl_kWh'), 2)} zł/kWh gazu + opłaty stałe", ZAL, str(ceny.get("zrodlo", "")))
    if system.pv is not None:
        zal.dodaj(f"PV {fmt(system.pv.P_kWp, 2)} kWp ({system.pv.opis}), azymut {fmt(system.pv.azymut, 0)}°, nachylenie "
                  f"{fmt(system.pv.nachylenie, 0)}°, PR = {fmt(system.pv.PR, 2)}; autokonsumpcja przez systemy techniczne — "
                  "miesięczny współczynnik a_n z symulacji godzinowej TMY (urządzenia domowe 2500 kWh/rok konkurują o energię PV, "
                  f"sterowanie ładowania c.w.u. w godz. 11–15: {'tak' if system.sterowanie_cwu_pv else 'nie'})", INT,
                  "metodologia tab. 1 lp. 6 (w = 0); R6-15 (brak wytycznych — założenie zachowawcze)")
    return W


# --------------------------------------------------------------------------------------------------
# Raporty i wykresy
# --------------------------------------------------------------------------------------------------
def raport_ep(W: WynikEP, *, wykres: str | None = None, zal: Zalozenia | None = None) -> str:
    M = W.mies
    s = [naglowek_raportu(f"Charakterystyka energetyczna — {W.system.nazwa}",
                          "rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm., ost. Dz.U. 2023 poz. 697) — metoda "
                          "obliczeniowa miesięczna; WT § 328–329 (EP_max); RPB § 23 pkt 11 lit. a–d",
                          [f"System: {W.system.opis}."])]
    s.append("### Współczynniki strat ciepła")
    s.append("")
    rows = [[k_, fmt(v, 2)] for k_, v in W.H_tr_skladniki.items()]
    rows.append(["**H_tr razem**", f"**{fmt(W.H_tr, 2)}**"])
    rows.append([f"H_ve = 0,34·[(1 − η_oc)·V_su + V_x] (V_su = {fmt(W.V_su_m3h, 0)} m³/h, η_oc = {fmt(W.eta_oc, 2)}, "
                 f"V_x = {fmt(W.V_x_m3h, 1)} m³/h)", fmt(W.H_ve, 2)])
    s.append(tabela_md(["Składnik", "H [W/K]"], rows, "lr"))
    s.append("")
    s.append(f"A_f = {fmt(W.A_f, 2)} m²; V = {fmt(W.V, 1)} m³; θ_int,H = {fmt(W.theta_int, 2)} °C; C_m = "
             f"{fmt(W.C_m / 1e6, 1)} MJ/K; τ = {fmt(W.tau_h, 1)} h; a_H = {fmt(W.a_H, 2)}.")
    s.append("")
    s.append("### Bilans miesięczny [kWh]")
    s.append("")
    naz = [("θ_e [°C]", "theta_e", 1), ("Q_tr", "Q_tr", 0), ("Q_ve", "Q_ve", 0), ("Q_int", "Q_int", 0),
           ("Q_sol", "Q_sol", 0), ("γ", "gamma", 2), ("η_H,gn", "eta", 3), ("Q_H,nd", "Q_H_nd", 0),
           ("Q_W,nd", "Q_W_nd", 0), ("Q_K,H", "Q_K_H", 0), ("Q_K,W", "Q_K_W", 0), ("E_pom", None, 0),
           ("E_PV", "E_PV", 0), ("a_n", "a_n", 2), ("E_PV,sys", "E_PV_sys", 0)]
    rows = []
    for nm, key, n in naz:
        arr = (M["E_pom_H"] + M["E_pom_W"]) if key is None else M[key]
        suma = "" if key in ("theta_e", "gamma", "eta", "a_n") else fmt(float(np.sum(arr)), 0)
        rows.append([nm] + [fmt(float(x), n) if (key != "gamma" or x < 50) else "—" for x in arr] + [suma])
    s.append(tabela_md(["Wielkość"] + miesiace_pl() + ["Rok"], rows))
    s.append("")
    if wykres:
        s.append(f"![Bilans miesięczny]({wykres})")
        s.append("")
    sy = W.system
    s.append("### Sprawności i energia pomocnicza")
    s.append("")
    s.append(tabela_md(["System", "η_g", "η_s", "η_d", "η_e", "η_tot", "Źródło"], [
        ["ogrzewanie", fmt(sy.eta_H_g_ef, 3), fmt(sy.eta_H_s, 2), fmt(sy.eta_H_d, 2), fmt(sy.eta_H_e, 2),
         fmt(sy.eta_H_tot, 3), sy.zrodlo_H + (f"; grzałka {fmt(sy.udzial_grzalki * 100, 2)} %" if sy.udzial_grzalki else "")],
        ["c.w.u.", fmt(sy.eta_W_g, 3), fmt(sy.eta_W_s, 3), fmt(sy.eta_W_d, 2), "—", fmt(sy.eta_W_tot, 3), sy.zrodlo_W]], "lrrrrrl"))
    s.append("")
    s.append(tabela_md(["Urządzenie pomocnicze", "P [W]", "t [h/rok]", "E [kWh/rok]", "System"],
                       [[p.opis, fmt(p.P_W, 1), fmt(p.h_rok, 0), fmt(p.P_W * p.h_rok / 1000, 0), p.system]
                        for p in sy.pomocnicze], "lrrrl"))
    s.append("")
    s.append("### Wskaźniki")
    s.append("")
    s.append(tabela_md(["Wskaźnik", "Wartość", "Jedn."], [
        ["Q_H,nd (ogrzewanie i wentylacja)", fmt(W.Q_H_nd, 0), "kWh/rok"],
        ["Q_W,nd (c.w.u., wzór (61))", fmt(W.Q_W_nd, 0), "kWh/rok"],
        ["EU = (Q_H,nd + Q_W,nd)/A_f", fmt(W.EU, 1), "kWh/(m²·rok)"],
        ["Q_K = Q_K,H + Q_K,W + E_el,pom", fmt(W.Q_K, 0), "kWh/rok"],
        ["EK = Q_K/A_f", fmt(W.EK, 1), "kWh/(m²·rok)"],
        ["Produkcja PV / zużyta przez systemy (w = 0)", f"{fmt(W.E_PV, 0)} / {fmt(W.E_PV_sys, 0)}", "kWh/rok"],
        ["EP_H (ogrzewanie + pomocnicze H)", fmt(W.EP_H, 1), "kWh/(m²·rok)"],
        ["EP_W (c.w.u. + pomocnicze W)", fmt(W.EP_W, 1), "kWh/(m²·rok)"],
        ["**EP = Q_p/A_f**", f"**{fmt(W.EP, 1)}**", "kWh/(m²·rok)"],
        ["EP_max (WT § 329)", fmt(W.EP_max, 1), "kWh/(m²·rok)"],
        ["Wynik", ok(W.spelnia), ""],
        ["E_CO2", fmt(W.E_CO2_t / W.A_f, 4), "t CO2/(m²·rok)"],
        ["U_oze (wzór (100)) " + INT, fmt(W.U_oze, 1), "%"],
        ["Koszt energii (eksploatacja) " + ZAL, fmt(W.koszt_zl, 0), "zł/rok"]], "lrl"))
    s.append("")
    if W.pv_sym:
        p = W.pv_sym
        s.append(f"Autokonsumpcja PV (symulacja godzinowa TMY): produkcja {fmt(p['E_pv_rok'], 0)} kWh/rok, zużyta przez "
                 f"systemy techniczne {fmt(p['E_self_sys_rok'], 0)} kWh/rok (a = {fmt(p['a_rok'], 2)}), przez urządzenia "
                 f"domowe {fmt(p['E_self_dom_rok'], 0)} kWh/rok; reszta oddana do sieci (nie obniża EP).")
        s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)


def wykres_bilans(W: WynikEP, plik) -> str:
    """Wykres miesięcznego bilansu energii (straty/zyski/Q_H,nd) i energii elektrycznej/PV — PNG."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    M = W.mies
    x = np.arange(12)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), dpi=150)
    a1.bar(x - 0.2, M["Q_tr"], 0.4, label="Q_tr (przenikanie)", color="#9e9ac8")
    a1.bar(x - 0.2, M["Q_ve"], 0.4, bottom=M["Q_tr"], label="Q_ve (wentylacja)", color="#cbc9e2")
    a1.bar(x + 0.2, M["Q_int"] * M["eta"], 0.4, label="η·Q_int", color="#fdae6b")
    a1.bar(x + 0.2, M["Q_sol"] * M["eta"], 0.4, bottom=M["Q_int"] * M["eta"], label="η·Q_sol", color="#fdd0a2")
    a1.plot(x, M["Q_H_nd"], "o-", color="#b30000", label="Q_H,nd")
    a1.plot(x, M["Q_W_nd"], "s--", color="#08519c", label="Q_W,nd", ms=3)
    a1.set_xticks(x, miesiace_pl())
    a1.set_ylabel("kWh/mies.")
    a1.set_title("Bilans ciepła strefy ogrzewanej")
    a1.legend(fontsize=7)
    el = M["E_el_sys"]
    a2.bar(x, el, 0.6, label="energia el. systemów (H, W, pomocnicze)", color="#9ecae1")
    a2.bar(x, M["E_PV_sys"], 0.6, label="w tym z PV (w = 0)", color="#31a354")
    a2.plot(x, M["E_PV"], "o-", color="#e6550d", label="produkcja PV")
    a2.set_xticks(x, miesiace_pl())
    a2.set_ylabel("kWh/mies.")
    a2.set_title(f"Energia końcowa i PV — EP = {W.EP:.1f} kWh/(m²·rok)".replace(".", ","))
    a2.legend(fontsize=7)
    fig.suptitle(f"{W.system.nazwa} — metoda miesięczna (TMY Poznań)", fontsize=9)
    fig.tight_layout()
    fig.savefig(plik)
    plt.close(fig)
    return str(plik)


def raport_alternatywy(wyniki: list[WynikEP], zal: Zalozenia | None = None) -> str:
    """Tabela porównawcza systemów (RPB § 20 ust. 1 pkt 10 lit. a–e)."""
    s = [naglowek_raportu("Analiza alternatywnych systemów zaopatrzenia w energię (RPB § 20 ust. 1 pkt 10)",
                          "RPB § 20 ust. 1 pkt 10 lit. a–e; metodologia Dz.U. 2015 poz. 376 ze zm.; WT § 329",
                          ["Nakłady inwestycyjne i ceny energii — założenia orientacyjne [ZAŁ] (dane/wyroby_przykladowe.yaml: "
                           "ceny, capex_zl) — do aktualizacji ofertami i taryfami URE.",
                           "(a) szacunek rocznej energii użytkowej: EU; (b) nośniki dostępne na działce: energia elektryczna "
                           "(sieć nN), gaz ziemny (sieć w drodze), energia słoneczna (PV); sieć ciepłownicza — brak; "
                           "(c) system konwencjonalny (B) i alternatywny/hybrydowy (A); (d) obliczenia porównawcze; "
                           "(e) wynik i wybór."])]
    base = next((w for w in wyniki if w.system.nosnik_H == "gaz"), None)
    rows = []
    for w in wyniki:
        rows.append([w.system.nazwa, fmt(w.EU, 1), fmt(w.EK, 1), fmt(w.EP, 1), ok(w.spelnia), fmt(w.E_CO2_t, 2),
                     fmt(w.U_oze, 0), fmt(w.koszt_zl, 0),
                     fmt(w.system.capex_zl, 0) if w.system.capex_zl else "—"])
    s.append(tabela_md(["System", "EU", "EK", "EP", "EP ≤ 70", "E_CO2 [t/rok]", "U_oze [%]", "Koszt [zł/rok] " + ZAL,
                        "Nakłady [zł] " + ZAL], rows, "lrrrlrrrr"))
    s.append("")
    s.append("Jednostki: EU, EK, EP — kWh/(m²·rok).")
    s.append("")
    wyb = min((w for w in wyniki if w.spelnia), key=lambda w: (w.EP, w.koszt_zl), default=None)
    if wyb:
        txt = f"**Wybór:** {wyb.system.nazwa} — najniższe EP ({fmt(wyb.EP, 1)} kWh/(m²·rok)) spośród wariantów spełniających EP_max"
        if base and base is not wyb:
            d = base.koszt_zl - wyb.koszt_zl
            txt += (f"; roczny koszt energii niższy o {fmt(d, 0)} zł względem systemu konwencjonalnego (B)" if d > 0 else
                    f"; roczny koszt energii wyższy o {fmt(-d, 0)} zł względem systemu konwencjonalnego (B)")
            if wyb.system.capex_zl and base.system.capex_zl and d > 0:
                txt += f", prosty okres zwrotu nakładów dodatkowych ≈ {fmt((wyb.system.capex_zl - base.system.capex_zl) / d, 1)} lat"
        s.append(txt + ".")
    else:
        s.append("**Żaden wariant nie spełnia EP_max — wymagane zmiany przegród/instalacji.**")
    s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
