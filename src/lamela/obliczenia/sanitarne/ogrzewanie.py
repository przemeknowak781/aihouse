"""Ogrzewanie: dobór pompy ciepła powietrze–woda (monoblok R290), punkt biwalentny, ogrzewanie podłogowe (PN-EN 1264),
rozdzielacze, bufor, naczynia wzbiorcze (c.o. i c.w.u.), hałas jednostki zewnętrznej na granicy działki.

Dane wejściowe z modułów fizyki/energii (budowane równolegle): **projektowe obciążenie cieplne pomieszczeń Φ_HL**
(``phi_hl`` — patrz :func:`lamela.obliczenia.inst_wspolne.phi_hl_z`). Bez nich moduł używa wartości **wskaźnikowych
zastępczych** (35 W/m² dla 20 °C, 45 W/m² dla 24 °C) — oznaczonych w raporcie jako [ZAŁ — do zastąpienia].

Podstawy (W-150…W-156, W-024, R6 §3.4, §3.9):

* **WT §134–135** — θ_i 20/24 °C, θ_e = −18 °C (Poznań, strefa II), regulacja pomieszczeniowa (§135 ust. 7–9),
  czynnik ≤ 90 °C; podłogówka ≤ 35 °C [ZAŁ W-153].
* **Rozp. (UE) 2024/573 zał. IV pkt 8–9** — od 01.01.2027 monobloki/splity powietrze–woda ≤ 12 kW z F-gazem GWP ≥ 150
  zakazane → **R290** (W-155); **rozp. (UE) 813/2013** — η_s ≥ 125 % (niskotemperaturowe), L_WA zewn. ≤ 65 dB (≤ 6 kW) /
  ≤ 70 dB (6–12 kW); strefa bezpieczeństwa R290 ≈ 1 m (W-156, [NZW]).
* **Moc PC:** Φ_PC ≥ Φ_HL (przy θ_e) + dodatek na c.w.u. **0,25 kW/os** (VDI 4645 [W]); układ monoenergetyczny z grzałką —
  **punkt biwalentny θ_biv ≤ −7 °C** i udział grzałki ≤ 5 % energii [ZAŁ — praktyka PORT PC/VDI 4645]; linia
  zapotrzebowania Φ(θ) = Φ_HL·(θ_i − θ)/(θ_i − θ_e); energia sezonowa metodą godzinową (TMY Poznań, PVGIS 5.3,
  granica grzania 15 °C) [UPR].
* **PN-EN 1264-2/-3** — charakterystyka bazowa q = 8,92·(θ_F,m − θ_i)^1,1 (θ_F,max 29 °C strefa przebywania, 33 °C
  łazienki, 35 °C strefy brzegowe); **q = K_H·∆θ_H**, K_H = B·a_B·a_T^m_T·a_u^m_u·a_D^m_D (system A, zał. A; tablice
  a_T, a_u, a_D wg literatury [NZW]); ∆θ_H — średnia logarytmiczna; θ_V,des z pomieszczenia o największym q (bez łazienek);
  strumień wody m_H = A_F·q/(σ·c)·(1 + R_o/R_u + (θ_i − θ_u)/(q·R_u)); PN-EN 1264-4 — minimalny opór izolacji pod
  wężownicą (0,75 / 1,25 m²·K/W).
* **Naczynie wzbiorcze** — PN-EN 12828 zał. D (PN-B-02414:1999 powołana w WT) [W]: V_n = (V_e + V_V)·(p_e + 1)/(p_e − p_0).
* **Hałas** — L_A = L_WA + 10·log(Q/(4πr²)) (PORT PC, „Wytyczne ograniczania hałasu instalacji z pompami ciepła” p. 4.4;
  Q = 2/4/8 — ≡ L_WA − 20·log r − 8 + DI, DI = 10·log(Q/2)); limit noc 40 dB, dzień 50 dB (Dz.U. 2014 poz. 112 tab. 1
  lp. 2a; W-024), cel 35 dB [ZAŁ].

Przykłady sprawdzalne ręcznie (test): PORT PC — L_WA = 61 dB(A), r = 10 m, Q = 2 → 33 dB(A); R6 §3.9 — L_WA = 55, Q = 4,
r = 4 m → 38,0 dB; 8 m → 32,0 dB; L_WA 60, r 6 m → 39,5 dB. PN-EN 1264: θ_F − θ_i = 9 K → q = 8,92·9^1,1 = 100,3 W/m².
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..inst_wspolne import (DaneBudynku, Krok, Raport, Warunek, ceil_to, f, fa, manhattan, phi_hl_budynku_z, phi_hl_z, tmy, wym, wym_zrodlo)
from .woda import RURY_WIELOWARSTWOWE, dobierz_rure, grubosc_izolacji_WT, rho_wody, spadek_jednostkowy

# --------------------------------------------------------------------------------------------------
# Katalog przykładowy monobloków R290 [ZAŁ — dane przykładowe typowe dla klasy urządzeń; zastąpić DTR/DWU wyrobu]
# P — moc grzewcza maks. przy W35 [kW] dla θ_e: -15, -7, 2, 7, 12 °C; COP przy tych punktach; L_WA [dB(A)] normalnie/noc
# --------------------------------------------------------------------------------------------------
KATALOG_PC = [
    {"model": "PC-R290-05 (przykład)", "T": [-15, -7, 2, 7, 12], "P": [3.6, 4.4, 4.8, 5.0, 5.2], "COP": [2.4, 2.9, 4.0, 5.0, 5.9],
     "L_WA": 55.0, "L_WA_noc": 50.0, "SCOP_35": 4.8, "eta_s_35": 1.89, "P_min": 1.8, "COP_cwu": 3.3, "V_wewn": 3.0,
     "dp_wewn_kPa": 15.0},
    {"model": "PC-R290-07 (przykład)", "T": [-15, -7, 2, 7, 12], "P": [5.0, 6.2, 7.0, 7.2, 7.4], "COP": [2.4, 2.9, 4.0, 5.0, 5.8],
     "L_WA": 57.0, "L_WA_noc": 52.0, "SCOP_35": 4.7, "eta_s_35": 1.85, "P_min": 2.2, "COP_cwu": 3.2, "V_wewn": 3.5,
     "dp_wewn_kPa": 18.0},
    {"model": "PC-R290-09 (przykład)", "T": [-15, -7, 2, 7, 12], "P": [6.6, 8.0, 9.0, 9.2, 9.4], "COP": [2.3, 2.8, 3.9, 4.9, 5.7],
     "L_WA": 58.0, "L_WA_noc": 53.0, "SCOP_35": 4.6, "eta_s_35": 1.81, "P_min": 2.8, "COP_cwu": 3.2, "V_wewn": 4.0,
     "dp_wewn_kPa": 20.0},
    {"model": "PC-R290-12 (przykład)", "T": [-15, -7, 2, 7, 12], "P": [8.5, 10.2, 11.5, 12.0, 12.2], "COP": [2.3, 2.8, 3.9, 4.8, 5.6],
     "L_WA": 60.0, "L_WA_noc": 55.0, "SCOP_35": 4.5, "eta_s_35": 1.77, "P_min": 3.5, "COP_cwu": 3.1, "V_wewn": 5.0,
     "dp_wewn_kPa": 22.0},
]
BUFORY = [25, 40, 50, 80, 100, 150, 200]
NACZYNIA = [8, 12, 18, 25, 35, 50, 80, 100]

# PN-EN 1264-2 zał. A — współczynniki (system A: rury w jastrychu) [NZW — wartości wg literatury]
_T = [0.05, 0.075, 0.10, 0.15, 0.20, 0.225, 0.25, 0.30, 0.375]
_RLB = [0.0, 0.05, 0.10, 0.15]
A_T = {0.0: 1.23, 0.05: 1.188, 0.10: 1.156, 0.15: 1.134}
A_U = {0.0: [1.069, 1.066, 1.063, 1.057, 1.051, 1.048, 1.045, 1.039, 1.030],
       0.05: [1.056, 1.053, 1.050, 1.046, 1.041, 1.038, 1.036, 1.031, 1.024],
       0.10: [1.043, 1.041, 1.039, 1.035, 1.031, 1.028, 1.026, 1.022, 1.017],
       0.15: [1.037, 1.035, 1.033, 1.030, 1.027, 1.025, 1.024, 1.019, 1.015]}
A_D = {0.0: [1.013, 1.013, 1.012, 1.011, 1.010, 1.009, 1.009, 1.008, 1.006],
       0.05: [1.013, 1.012, 1.011, 1.010, 1.009, 1.009, 1.008, 1.007, 1.006],
       0.10: [1.012, 1.011, 1.010, 1.009, 1.008, 1.008, 1.007, 1.007, 1.005],
       0.15: [1.011, 1.010, 1.009, 1.008, 1.007, 1.007, 1.006, 1.006, 1.004]}
ROZSTAWY = [0.10, 0.15, 0.20, 0.25, 0.30]


def interp_ekstrap(x, xs, ys):
    """Interpolacja liniowa z ekstrapolacją liniową poza zakresem (dane katalogowe PC poniżej −15 °C) [UPR]."""
    x = np.asarray(x, float)
    y = np.interp(x, xs, ys)
    lo = x < xs[0]
    hi = x > xs[-1]
    k0 = (ys[1] - ys[0]) / (xs[1] - xs[0])
    k1 = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
    y = np.where(lo, ys[0] + k0 * (x - xs[0]), y)
    y = np.where(hi, ys[-1] + k1 * (x - xs[-1]), y)
    return y


def _interp_R(tab: dict, R: float, T: float | None = None) -> float:
    Rs = sorted(tab)
    R = min(max(R, Rs[0]), Rs[-1])
    def val(r):
        v = tab[r]
        return float(np.interp(T, _T, v)) if T is not None else v
    for a, b in zip(Rs, Rs[1:]):
        if a <= R <= b:
            t = (R - a) / (b - a) if b > a else 0
            return val(a) * (1 - t) + val(b) * t
    return val(Rs[-1])


def K_H(T: float, R_lB: float, s_u: float = 0.045, lam_E: float = 1.2, D: float = 0.017, B: float = 6.7) -> float:
    """Równoważny współczynnik przenikania K_H [W/(m²·K)] wg PN-EN 1264-2 zał. A (system A): q = K_H·∆θ_H.
    a_B = (1/α + s_u0/λ_u0)/(1/α + s_u/λ_E + R_λ,B), α = 10,8, s_u0 = 0,045 m, λ_u0 = 1,0; m_T = 1 − T/0,075;
    m_u = 100·(0,045 − s_u); m_D = 250·(D − 0,020)."""
    alfa = 10.8
    aB = (1 / alfa + 0.045 / 1.0) / (1 / alfa + s_u / lam_E + R_lB)
    aT = _interp_R(A_T, R_lB)
    aU = _interp_R(A_U, R_lB, T)
    aD = _interp_R(A_D, R_lB, T)
    mT = 1 - T / 0.075
    mU = 100 * (0.045 - s_u)
    mD = 250 * (D - 0.020)
    return B * aB * aT ** mT * aU ** mU * aD ** mD


def q_charakterystyka(dT_F: float) -> float:
    """Charakterystyka bazowa PN-EN 1264: q = 8,92·(θ_F,m − θ_i)^1,1 [W/m²]."""
    return 8.92 * max(dT_F, 0.0) ** 1.1


def dT_H_log(theta_V: float, theta_R: float, theta_i: float) -> float:
    a, b = theta_V - theta_i, theta_R - theta_i
    if a <= 0 or b <= 0:
        return 0.0
    if abs(a - b) < 1e-9:
        return a
    return (a - b) / math.log(a / b)


def theta_V_z(dT_H: float, sigma: float, theta_i: float) -> float:
    """θ_V dla zadanego ∆θ_H i σ (dokładnie, z definicji średniej logarytmicznej): (θ_V−θ_i) = σ·e^(σ/∆θ_H)/(e^(σ/∆θ_H) − 1)."""
    x = sigma / dT_H
    return theta_i + sigma * math.exp(x) / (math.exp(x) - 1.0)


def theta_R_z(theta_V: float, dT_H: float, theta_i: float) -> float | None:
    """θ_R przy zadanych θ_V i ∆θ_H (bisekcja); None, gdy ∆θ_H ≥ θ_V − θ_i."""
    a = theta_V - theta_i
    if dT_H >= a - 1e-6:
        return None
    lo, hi = theta_i + 1e-6, theta_V - 1e-6
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        if dT_H_log(theta_V, mid, theta_i) > dT_H:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def poziom_halasu(L_WA: float, r: float, Q: float = 2.0) -> float:
    """L_A = L_WA + 10·log10(Q/(4·π·r²)) [dB(A)] (PORT PC p. 4.4)."""
    return L_WA + 10.0 * math.log10(Q / (4.0 * math.pi * r * r))


def odleglosc_dla_limitu(L_WA: float, L_lim: float, Q: float = 2.0) -> float:
    return math.sqrt(Q / (4.0 * math.pi) * 10 ** ((L_WA - L_lim) / 10.0))


def naczynie_wzbiorcze(V_c: float, theta_max: float, h_stat: float, p_SV: float = 3.0, theta_0: float = 10.0,
                       p_0_min: float = 0.5) -> dict:
    """Naczynie przeponowe c.o. (PN-EN 12828 zał. D [W]): e = ρ(θ_0)/ρ(θ_max) − 1; V_e = e·V_c; V_V = max(0,005·V_c; 3 dm³);
    p_0 = max(h_stat/10 + 0,2; p_0_min) [bar]; p_e = p_SV − 0,5; V_n = (V_e + V_V)·(p_e + 1)/(p_e − p_0)."""
    e = rho_wody(theta_0) / rho_wody(theta_max) - 1.0
    Ve = e * V_c
    VV = max(0.005 * V_c, 3.0)
    p0 = max(h_stat / 10.0 + 0.2, p_0_min)
    pe = p_SV - 0.5
    Vn = (Ve + VV) * (pe + 1.0) / (pe - p0)
    return {"e": e, "V_e": Ve, "V_V": VV, "p_0": p0, "p_e": pe, "V_n": Vn, "V_dob": ceil_to(Vn, NACZYNIA) or NACZYNIA[-1],
            "V_c": V_c, "theta_max": theta_max}


@dataclass
class ParametryOgrz:
    theta_e: float | None = None
    theta_i: float = 20.0
    theta_V_max: float = 35.0
    sigma: float = 5.0
    T_des: float = 0.10                 # rozstaw w pomieszczeniu projektowym [m]
    sigma_min: float = 3.0              # K — minimalne schłodzenie w pętlach pozostałych pomieszczeń [ZAŁ]
    q_wsk_20: float = 35.0              # W/m² — ZASTĘPCZO gdy brak Φ_HL [ZAŁ]
    q_wsk_24: float = 45.0
    phi_cwu_os: float = 0.25            # kW/os (VDI 4645) [W]
    theta_biv_max: float = -7.0         # [ZAŁ]
    udzial_grzalki_max: float = 0.05    # [ZAŁ]
    theta_granica: float = 15.0         # granica grzania (bilans energii) [UPR]
    L_petli_max: float = 100.0          # m — PE-X 16×2 [W]
    dp_petli_max: float = 25.0          # kPa [ZAŁ]
    d_rury_petli: tuple = (16, 2.0)
    udzial_petli_otwartych: float = 0.3  # udział objętości pętli bez siłowników (łazienki, hole) [ZAŁ]
    t_odszraniania_min: float = 5.0
    dT_bufora: float = 5.0
    t_min_pracy_min: float = 10.0
    p_SV: float = 3.0
    theta_max_co: float = 60.0          # maks. temperatura wody w obiegu PC (tryb c.w.u.) [ZAŁ]
    p_zasilania_cwu: float = 4.0        # bar — reduktor [ZAŁ]
    p_SV_cwu: float = 6.0
    theta_dez: float = 75.0
    V_zas_cwu: float | None = None      # z modułu wody
    L_noc: float | None = None
    L_dzien: float | None = None
    L_cel: float | None = None
    grzalka_kW: float = 6.0             # grzałka rezerwowa (3f) [ZAŁ]
    f_zabudowy: dict = field(default_factory=lambda: {"lazienka": 0.60, "wc": 0.50, "kuchnia": 0.75, "garderoba": 0.60,
                                                      "techniczne": 0.50, "inne": 0.85})
    model_pc: str | None = None         # wymuszenie modelu z katalogu


@dataclass
class Petla:
    pom: str
    nr: int
    T: float
    L: float
    m_kgh: float
    dp: float
    V_l: float


@dataclass
class WynikOgrzewanie:
    dane: DaneBudynku
    par: ParametryOgrz
    phi: dict
    phi_zrodlo: str
    Phi_HL: float
    Phi_W: float
    pc: dict
    biwalentny: dict
    bin: dict
    podlogowka: list
    petle: list
    rozdzielacze: list
    theta_V: float
    bufor: dict
    naczynie_co: dict
    naczynie_cwu: dict
    halas: dict
    przewody_pc: dict
    warunki: list
    kroki: dict
    zalozenia: list

    def do_dict(self) -> dict:
        return {"Phi_HL_kW": round(self.Phi_HL / 1000, 2), "zrodlo_Phi_HL": self.phi_zrodlo, "PC": self.pc["model"],
                "P_PC_theta_e_kW": round(self.biwalentny["P_te"], 2), "theta_biv": round(self.biwalentny["theta_biv"], 1),
                "udzial_grzalki": round(self.bin["udzial_grzalki"], 4), "SCOP_dekl": self.pc["SCOP_35"],
                "SCOP_obl_TMY": round(self.bin["SCOP"], 2), "theta_V_des": round(self.theta_V, 1),
                "bufor_l": self.bufor["V_dob"], "naczynie_co_l": self.naczynie_co["V_dob"], "naczynie_cwu_l": self.naczynie_cwu["V_dob"],
                "L_A_granica_dB": round(self.halas["L_A_granica"], 1),
                "do_EP": {"eta_H_g_SCOP": round(min(self.pc["SCOP_35"], self.bin["SCOP"]), 2), "COP_cwu": self.pc["COP_cwu"], "eta_H_e": 0.89, "eta_H_d": 0.96,
                          "E_el_PC_kWh_a": round(self.bin["E_el"], 0), "E_grzalka_kWh_a": round(self.bin["E_grz"], 0),
                          "Q_H_TMY_kWh_a": round(self.bin["Q_H"], 0)}}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def _R_lambda_B(dane: DaneBudynku, pom) -> tuple[float, str]:
    """Opór cieplny wykładziny R_λ,B [m²·K/W] z kodu posadzki pomieszczenia (model) [ZAŁ — typowe wartości]."""
    m = dane.model
    kod = ""
    try:
        raw = next(r for r in m.pomieszczenia() if r.id == pom.id)
        kod = str(raw.posadzka or "")
    except Exception:
        pass
    k = kod.upper()
    if any(s in k for s in ("GRES", "PLYT", "KAMIEN", "TERRAZ")):
        return 0.02, f"{kod} (płytki) 0,02"
    if "DESKA" in k or "PARKIET" in k:
        return 0.10, f"{kod} (drewno 15 mm) 0,10"
    if "PANEL" in k:
        return 0.07, f"{kod} (panele) 0,07"
    if "WYKL" in k or "DYWAN" in k:
        return 0.15, f"{kod} (wykładzina) 0,15"
    return 0.10, f"{kod or '—'} (założenie PN-EN 1264: 0,10)"


def _podloga(dane: DaneBudynku, kond: str):
    """Warstwy podłogi kondygnacji: (s_u [m], λ_E, R_u [m²K/W], opis) — z przegrody podłogi w modelu."""
    m = dane.model
    try:
        k = m.kondygnacja(kond)
        prz = m.przegroda(k.podloga)
    except Exception:
        prz = None
    if prz is None:
        return 0.045, 1.2, 1.25, "brak przegrody podłogi — założenia"
    s_u, lamE, R_u = 0.045, 1.2, 0.0
    jast = [w for w in prz.warstwy if "JAST" in w.mat.upper() or "WYLEW" in w.mat.upper()]
    if jast:
        s_u = max(0.030, jast[0].d - 0.017)
        mat = m.material(jast[0].mat)
        lamE = float(mat.lambda_) if (mat is not None and mat.lambda_) else 1.2
    idx = prz.warstwy.index(jast[0]) if jast else 0
    for w in prz.warstwy[idx + 1:]:
        mat = m.material(w.mat)
        lam = mat.lambda_ if mat is not None else None
        if lam and lam < 0.1:
            R_u += w.d / lam
    return s_u, lamE, R_u, f"przegroda {prz.kod}"


def oblicz_ogrzewanie(dane: DaneBudynku, phi_hl=None, par: ParametryOgrz | None = None, cwu: dict | None = None) -> WynikOgrzewanie:
    """Obliczenia ogrzewania. ``phi_hl`` — Φ_HL pomieszczeń (dowolna postać akceptowana przez ``phi_hl_z``);
    ``cwu`` — wynik c.w.u. z modułu wody (``WynikWoda.cwu``) dla naczynia c.w.u."""
    par = par or ParametryOgrz()
    te = par.theta_e if par.theta_e is not None else float(wym("ogrzewanie", "theta_e", -18) or -18)
    war: list[Warunek] = []
    kroki: dict[str, list] = {}
    zal: list[str] = []
    phi = phi_hl_z(phi_hl) or phi_hl_z(dane.inst.get("obciazenie_cieplne"))
    zr = "moduł fizyki/energii (PN-EN 12831)" if phi else ""
    if not phi:
        phi = {}
        for p in dane.pomieszczenia:
            if not p.ogrzewane:
                continue
            q = par.q_wsk_24 if (p.temp or 20) >= 24 else par.q_wsk_20
            phi[p.id] = q * p.pow
        zr = "WSKAŹNIKOWE ZASTĘPCZE [ZAŁ] — do zastąpienia wynikami PN-EN 12831 (moduł energii)"
        zal.append(f"Φ_HL pomieszczeń przyjęto wskaźnikowo: {f(par.q_wsk_20, 0)} W/m² (20 °C), {f(par.q_wsk_24, 0)} W/m² (24 °C) — "
                   "WYŁĄCZNIE do czasu otrzymania wyników z modułu obciążenia cieplnego.")
    Phi_sum = sum(phi.values())
    Phi_bud = phi_hl_budynku_z(phi_hl) if phi_hl is not None else phi_hl_budynku_z(dane.inst.get("obciazenie_cieplne"))
    Phi = Phi_bud if Phi_bud else Phi_sum
    osoby = dane.osoby
    Phi_W = par.phi_cwu_os * 1000 * osoby
    kroki["moc"] = [
        Krok("Suma obciążeń cieplnych pomieszczeń (do wymiarowania podłogówki)", "ΣΦ_HL,i", "", Phi_sum / 1000, "kW", zr, 2),
        Krok("Projektowe obciążenie cieplne budynku (do doboru źródła)",
             "Φ_HL,bud (bez strumieni między pomieszczeniami ogrzewanymi)" if Phi_bud else "Φ_HL = ΣΦ_HL,i", "", Phi / 1000, "kW",
             "PN-EN 12831-1 — wynik modułu energii" if Phi_bud else zr, 2),
        Krok("Dodatek na przygotowanie c.w.u.", "Φ_W = 0,25 kW/os·N", f"0,25·{osoby}", Phi_W / 1000, "kW", "VDI 4645 [W]", 2),
        Krok("Wymagana moc źródła przy θ_e (układ monowalentny)", "Φ_PC = Φ_HL + Φ_W", f"{f(Phi / 1000, 2)} + {f(Phi_W / 1000, 2)}",
             (Phi + Phi_W) / 1000, "kW", "", 2),
    ]
    # ---- klimat TMY
    T = tmy()["T2m"]
    H = Phi / (par.theta_i - te)          # W/K

    def ocen(pc):
        Ts, Ps, Cs = pc["T"], pc["P"], pc["COP"]
        P_at = lambda t: float(interp_ekstrap(t, Ts, Ps)) * 1000.0
        # punkt biwalentny: Φ(θ) + Φ_W_sr? — linia budynku (bez c.w.u.; c.w.u. w trybie priorytetowym, krótkotrwale)
        lo, hi = te, par.theta_granica
        f_ = lambda t: P_at(t) - H * (par.theta_i - t)
        if f_(te) >= 0:
            tb = te
        else:
            for _ in range(60):
                mid = 0.5 * (lo + hi)
                if f_(mid) >= 0:
                    hi = mid
                else:
                    lo = mid
            tb = 0.5 * (lo + hi)
        mask = T < par.theta_granica
        Q = H * np.clip(par.theta_granica - T, 0, None)            # zapotrzebowanie godzinowe (z zyskami) [W]
        Pmax = interp_ekstrap(T, Ts, Ps) * 1000.0
        cop = np.maximum(interp_ekstrap(T, Ts, Cs), 1.0)
        Q_pc = np.minimum(Q, Pmax)
        Q_gr = Q - Q_pc
        E_el = float(np.sum(Q_pc[mask] / cop[mask])) / 1000.0
        return {"theta_biv": tb, "P_te": P_at(te) / 1000.0, "Q_H": float(Q[mask].sum()) / 1000.0,
                "Q_grz": float(Q_gr[mask].sum()) / 1000.0, "E_el": E_el, "E_grz": float(Q_gr[mask].sum()) / 1000.0,
                "udzial_grzalki": float(Q_gr[mask].sum() / max(Q[mask].sum(), 1e-9)),
                "SCOP": float(Q_pc[mask].sum() / 1000.0 / max(E_el, 1e-9)), "h_grz": int(np.sum((Q_gr > 0) & mask))}
    wybor = None
    oceny = []
    for pc in KATALOG_PC:
        o = ocen(pc)
        oceny.append((pc, o))
        if par.model_pc and pc["model"].startswith(par.model_pc):
            wybor = (pc, o)
    if wybor is None:
        for pc, o in oceny:
            if o["theta_biv"] <= par.theta_biv_max + 1e-6 and o["udzial_grzalki"] <= par.udzial_grzalki_max:
                wybor = (pc, o)
                break
        if wybor is None:
            wybor = oceny[-1]
            zal.append("Żaden model z katalogu przykładowego nie spełnia kryterium punktu biwalentnego — przyjęto największy; "
                       "zwiększyć moc lub rozważyć układ biwalentny.")
    pc, o = wybor
    zal.append(f"Pompa ciepła: {pc['model']} — dane przykładowe typowe dla monobloków R290 [ZAŁ — zastąpić DTR/DWU wyrobu, E-13].")
    tb = o["theta_biv"]
    kroki["biw"] = [
        Krok("Współczynnik strat budynku", "H = Φ_HL/(θ_i − θ_e)", f"{f(Phi, 0)}/({f(par.theta_i, 0)} − ({f(te, 0)}))", H, "W/K", "", 1),
        Krok("Moc PC przy θ_e (W35)", "P_PC(θ_e)", "interpolacja danych katalogowych", o["P_te"], "kW", "[ZAŁ]", 2),
        Krok("Punkt biwalentny (P_PC(θ) = H·(θ_i − θ))", "θ_biv", "bisekcja", tb, "°C", f"kryterium θ_biv ≤ {f(par.theta_biv_max, 0)} °C [ZAŁ]", 1),
        Krok("Ciepło do bilansu godzinowego PC — metoda uproszczona (stopniogodziny TMY Poznań, granica grzania 15 °C, "
             "bez bilansu zysków ciepła; NIE jest to zapotrzebowanie Q_H,nd — to podaje charakterystyka energetyczna)",
             "Q_H,PC = Σ H·(15 − θ_e,h)", "", o["Q_H"], "kWh/a",
             "PVGIS 5.3 TMY [UPR — tylko do udziału grzałki i SCOP]", 0),
        Krok("Energia z grzałki (godziny z P_PC < Φ)", "Q_grz = Σ max(0, Φ − P_PC)", "", o["Q_grz"], "kWh/a", "", 0),
        Krok("Udział grzałki", "Q_grz/Q_H", "", 100 * o["udzial_grzalki"], "%", f"≤ {f(100 * par.udzial_grzalki_max, 0)} % [ZAŁ]", 2),
        Krok("Sezonowy COP z obliczenia godzinowego (do EP — mniejsza z wartości: ta albo SCOP deklarowany)", "SCOP = ΣQ_PC/ΣE_el", "", o["SCOP"], "",
             "", 2),
    ]
    kroki["biw"].append(Krok(f"Uwaga: TMY Poznań — min. θ_e = {f(float(T.min()), 1)} °C (rok typowy nie zawiera temperatury obliczeniowej "
                             f"{f(te, 0)} °C); w latach mroźnych udział grzałki większy — pokrycie mocy przy θ_e sprawdzono niżej", "", "", None))
    war.append(Warunek("Punkt biwalentny", tb, "<=", par.theta_biv_max, "°C", "VDI 4645 / praktyka [ZAŁ]", "W-155", nd=1))
    war.append(Warunek("Pokrycie mocy przy θ_e (układ monoenergetyczny): P_PC(θ_e) + P_grzałki ≥ Φ_HL + Φ_W",
                       o["P_te"] + par.grzalka_kW, ">=", (Phi + Phi_W) / 1000.0, "kW", "PN-EN 12831 / VDI 4645 [W]", "W-155"))
    war.append(Warunek("Udział grzałki w pokryciu Q_H", o["udzial_grzalki"], "<=", par.udzial_grzalki_max, "", "[ZAŁ]", "W-155", nd=3))
    war.append(Warunek("Moc nominalna PC (zakaz F-gazów dotyczy ≤ 12 kW — czynnik R290, GWP₁₀₀ = 0,02)", max(pc["P"]), "<=", 12.0, "kW",
                       "rozp. (UE) 2024/573 zał. IV pkt 8 lit. b", "W-155"))
    war.append(Warunek("Sezonowa efektywność η_s (35 °C)", pc["eta_s_35"], ">=",
                       float(wym("ogrzewanie", "pc_eta_s_niskotemp_min", 1.25) or 1.25), "", "rozp. (UE) 813/2013 zał. II", "W-155"))
    Lmax = float(wym("ogrzewanie", "pc_LWA_zewn_do_6kW_max", 65)) if max(pc["P"]) <= 6 else float(wym("ogrzewanie", "pc_LWA_zewn_6_12kW_max", 70))
    war.append(Warunek("Poziom mocy akustycznej jednostki zewn.", pc["L_WA"], "<=", Lmax, "dB(A)", "rozp. (UE) 813/2013 zał. II pkt 3",
                       "W-155", nd=0))
    # ---- podłogówka
    rozdz = dane.inst.get("lokalizacje", {}).get("rozdzielacze_co") or {}
    podl = []
    try:
        from .przybory import przybory_z_modelu
        mokre = {x.pom for x in przybory_z_modelu(dane) if x.typ in ("wanna", "prysznic")}
    except Exception:
        mokre = set()
    # dodatkowe powierzchnie grzewcze wodne (ściany grzewcze / grzejniki niskotemperaturowe z obiegu PC) — `instalacje.grzejniki`
    # [{pom, kond, xy, typ, moc_W}] (runda 2, K-10): pokrywają część Φ_HL, podłoga — resztę (PN-EN 1264-3; PN-EN 12831-1)
    dod: dict[str, float] = {}
    for g in dane.inst.get("grzejniki") or []:
        if isinstance(g, dict) and g.get("pom") and g.get("moc_W"):
            dod[str(g["pom"])] = dod.get(str(g["pom"]), 0.0) + float(g["moc_W"])
    for pid, ph in phi.items():
        p = dane.pom(pid)
        if p is None or ph <= 0:
            continue
        if dod.get(pid):
            war.append(Warunek(f"{p.id} {p.nazwa}: dodatkowa powierzchnia grzewcza wodna (instalacje.grzejniki)", dod[pid], "info",
                               None, "W", "PN-EN 1264-3 / PN-EN 12831-1 — podłoga pokrywa Φ_HL − P_dod", "W-153", nd=0))
            ph = ph - dod[pid]
            if ph <= 0:
                continue
        rodz = "lazienka" if pid in mokre else p.rodzaj
        fz = par.f_zabudowy.get(rodz, par.f_zabudowy["inne"])
        A_F = p.pow * fz
        q = ph / A_F
        R_lB, R_opis = _R_lambda_B(dane, p)
        s_u, lamE, R_u, _ = _podloga(dane, p.kond)
        ti = p.temp or 20.0
        dTF_max = 9.0
        q_lim = q_charakterystyka(dTF_max)
        podl.append({"pom": p, "rodzaj": rodz, "phi": ph, "A_F": A_F, "fz": fz, "q": q, "R_lB": R_lB, "R_opis": R_opis, "s_u": s_u, "lamE": lamE,
                     "R_u": R_u, "ti": ti, "q_lim": q_lim, "theta_F": ti + (q / 8.92) ** (1 / 1.1) if q > 0 else ti})
    niel = [x for x in podl if x["rodzaj"] not in ("lazienka", "wc")] or podl
    # pomieszczenie projektowe: największa wymagana θ_V przy T_des i σ (uogólnienie PN-EN 1264-3 na różne R_λ,B)
    for x in niel:
        x["_Kd"] = K_H(par.T_des, x["R_lB"], x["s_u"], x["lamE"])
        x["_thV"] = theta_V_z(x["q"] / x["_Kd"], par.sigma, x["ti"])
    des = max(niel, key=lambda x: x["_thV"])
    Kd = des["_Kd"]
    dTH_des = des["q"] / Kd
    thV_wym = des["_thV"]
    # θ_V ograniczona do θ_V,max (W-153): pomieszczenia, których Φ_HL podłoga nie pokrywa przy θ_V,max, dostają
    # warunek niedoboru mocy (dodatkowa powierzchnia grzewcza) — zamiast podnoszenia temperatury całego układu
    thV = min(thV_wym, par.theta_V_max)
    kroki["podl"] = [
        Krok(f"Pomieszczenie projektowe: {des['pom'].id} {des['pom'].nazwa}", "q_des = Φ_HL/A_F",
             f"{f(des['phi'], 0)}/{f(des['A_F'], 2)}", des["q"], "W/m²", "PN-EN 1264-3 (bez łazienek; największa wymagana θ_V)", 1),
        Krok(f"K_H dla T = {f(par.T_des, 2)} m, R_λ,B = {f(des['R_lB'], 2)}, s_u = {f(des['s_u'], 3)} m, λ_E = {f(des['lamE'], 2)}",
             "K_H = B·a_B·a_T^m_T·a_u^m_u·a_D^m_D", "", Kd, "W/(m²·K)", "PN-EN 1264-2 zał. A [NZW tablice]", 3),
        Krok("Nadwyżka temperatury czynnika", "∆θ_H = q/K_H", f"{f(des['q'], 1)}/{f(Kd, 3)}", dTH_des, "K", "", 2),
        Krok(f"Temperatura zasilania wymagana (σ = {f(par.sigma, 0)} K)", "θ_V = θ_i + σ·e^(σ/∆θ_H)/(e^(σ/∆θ_H) − 1)", "", thV_wym, "°C",
             "definicja ∆θ_H (średnia logarytmiczna)", 1),
        Krok("Projektowa temperatura zasilania", "θ_V,des = min(θ_V; θ_V,max)", f"min({f(thV_wym, 1)}; {f(par.theta_V_max, 1)})", thV,
             "°C", "W-153 (R6 3.4)" + (" — niedobór mocy w pomieszczeniu projektowym pokrywa dodatkowa powierzchnia grzewcza"
                                       if thV_wym > par.theta_V_max + 1e-9 else ""), 1),
        Krok("Charakterystyka bazowa — gęstość graniczna przy θ_F,max − θ_i = 9 K", "q_G = 8,92·9^1,1", "", q_charakterystyka(9.0),
             "W/m²", "PN-EN 1264-2 (29 °C / 33 °C łazienki)", 1),
    ]
    war.append(Warunek("Temperatura zasilania ogrzewania podłogowego", thV, "<=", par.theta_V_max, "°C",
                       wym_zrodlo("ogrzewanie", "podlogowka_zasilanie_max"), "W-153", nd=1))
    petle = []
    wiersze = []
    L_d, d_w = par.d_rury_petli[0], par.d_rury_petli[0] - 2 * par.d_rury_petli[1]
    for x in podl:
        p = x["pom"]
        war.append(Warunek(f"{p.id} {p.nazwa}: gęstość strumienia ≤ q_G (θ_F ≤ {f(x['ti'] + 9, 0)} °C)", x["q"], "<=", x["q_lim"],
                           "W/m²", "PN-EN 1264-2", "W-153", nd=1))
        # najrzadszy rozstaw, przy którym schłodzenie σ_j ≥ σ_min
        T_ok, dTH, thR = None, None, None
        for Tr in reversed(ROZSTAWY):
            K = K_H(Tr, x["R_lB"], x["s_u"], x["lamE"])
            d = x["q"] / K
            r = theta_R_z(thV, d, x["ti"])
            if r is not None and thV - r >= par.sigma_min - 1e-9:
                T_ok, dTH, thR = Tr, d, r
                break
        if T_ok is None:
            Tr = ROZSTAWY[0]
            K = K_H(Tr, x["R_lB"], x["s_u"], x["lamE"])
            T_ok, dTH, thR = Tr, x["q"] / K, None
            # osiągalne q przy θ_V i σ = 2 K → brakująca moc do pokrycia dodatkową powierzchnią grzewczą
            dTH_ach = dT_H_log(thV, thV - 2.0, x["ti"])
            q_ach = K * dTH_ach
            deficyt = max(0.0, (x["q"] - q_ach) * x["A_F"])
            war.append(Warunek(f"{p.id} {p.nazwa}: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL", q_ach * x["A_F"], ">=", x["phi"], "W",
                               "PN-EN 1264-3 — " + ("łazienka: dogrzewanie grzejnikiem drabinkowym" if x["rodzaj"] in ("lazienka", "wc")
                                                    else "dodatkowa powierzchnia grzewcza (ściana) lub mniejsze R_λ,B"),
                               "W-153", nd=0, uwagi=f"brak ≈ {f(deficyt, 0)} W"))
        sigma_j = (thV - thR) if thR is not None else par.sigma
        R_o = 1 / 10.8 + x["R_lB"] + x["s_u"] / x["lamE"]
        R_u = max(x["R_u"], 0.1)
        th_u = 10.0 if dane.rzedna(p.kond) == dane.rzedna(dane.kondygnacje[0]["id"]) else 20.0
        mH = x["A_F"] * x["q"] / (sigma_j * 4190.0) * (1 + R_o / R_u + (x["ti"] - th_u) / (x["q"] * R_u)) * 3600.0   # kg/h
        rxy = rozdz.get(p.kond)
        rxy = rxy if rxy else dane.lok("RG")[:2] if dane.lok("RG") else p.centroid
        L_dop = manhattan(rxy, p.centroid) * 2 + 1.0
        L_tot = x["A_F"] / T_ok + L_dop
        n = max(1, math.ceil(L_tot / par.L_petli_max))

        def _dp(nn):
            q_l = mH / nn / 3600.0 / rho_wody(30.0) * 1000.0
            v, R, _ = spadek_jednostkowy(q_l, d_w, 30.0)
            return 1.3 * R * (L_tot / nn) + 5.0       # +30 % miejscowe, zawór regulacyjny/rozdzielacz 5 kPa [ZAŁ]
        while _dp(n) > par.dp_petli_max and n < 8:
            n += 1
        for k in range(n):
            Lk = L_tot / n
            mk = mH / n
            petle.append(Petla(pom=p.id, nr=k + 1, T=T_ok, L=Lk, m_kgh=mk, dp=_dp(n),
                               V_l=math.pi * (d_w / 1000) ** 2 / 4 * Lk * 1000))
            war.append(Warunek(f"Pętla {p.id}/{k + 1}: długość", Lk, "<=", par.L_petli_max, "m", "PE-X 16×2 [W]", "W-154", nd=1))
        wiersze.append([p.id, p.nazwa, p.kond, f(x["phi"], 0), f(x["A_F"], 1), f(x["q"], 1), f(x["theta_F"], 1), x["R_opis"],
                        f(100 * T_ok, 0), f(dTH, 2), f(thR, 1) if thR else "—", f(sigma_j, 2), f(mH, 1), n, f(L_tot, 1)])
        if x["R_u"] < (1.25 if th_u < 15 else 0.75):
            war.append(Warunek(f"{p.id}: opór izolacji pod wężownicą", x["R_u"], ">=", 1.25 if th_u < 15 else 0.75, "m²·K/W",
                               "PN-EN 1264-4 tabl. 1", "W-153"))
    # rozdzielacze
    rozdzielacze = []
    for kond in sorted({pp.kond for pp in [x["pom"] for x in podl]}):
        pl = [pt for pt in petle if dane.pom(pt.pom).kond == kond]
        n = len(pl)
        n_r = math.ceil(n / 12)
        rozdzielacze.append({"kond": kond, "petle": n, "rozdzielacze": n_r, "sekcje": [math.ceil(n / n_r)] * n_r,
                             "m_kgh": sum(p.m_kgh for p in pl), "dp_max": max((p.dp for p in pl), default=0.0),
                             "xy": rozdz.get(kond)})
    dp_crit = max((p.dp for p in petle), default=0.0)
    m_tot = sum(p.m_kgh for p in petle)
    war.append(Warunek("Maks. strata ciśnienia pętli", dp_crit, "<=", par.dp_petli_max, "kPa", "[ZAŁ]", "W-154", nd=1))
    # ---- przewody PC ↔ budynek, pompa obiegowa
    P_nom = max(pc["P"]) * 1000
    m_pc = P_nom / (4190 * par.sigma) * 3600                 # kg/h
    q_pc = m_pc / 3600 / 0.995
    rura = dobierz_rure(q_pc, 1.0, RURY_WIELOWARSTWOWE, 25)
    v_pc, R_pc, _ = spadek_jednostkowy(q_pc, rura[2], 35.0)
    jz = dane.lok("pompa_ciepla_jz")
    rg = dane.lok("zasobnik") or dane.lok("RG")
    L_pc = (manhattan(jz[:2], rg[:2]) + 3.0) if (jz and rg) else 12.0
    dp_pc = 2 * 1.3 * R_pc * L_pc
    H_pompy = dp_crit + dp_pc + pc["dp_wewn_kPa"] + 5.0
    t_ref = grubosc_izolacji_WT(rura[2])
    przew = {"rura": f"PE-RT/Al/PE-RT {rura[0]}×{f(rura[1], 1)}", "d_w": rura[2], "v": v_pc, "R": R_pc, "L": L_pc, "dp": dp_pc,
             "m_kgh": m_pc, "H_pompy_kPa": H_pompy, "izol_WT": t_ref, "izol_zewn": 2 * t_ref}
    kroki["pompa"] = [
        Krok("Przepływ w obiegu PC (moc nominalna, ∆θ = 5 K)", "ṁ = P/(c·∆θ)", f"{f(P_nom, 0)}/(4190·{f(par.sigma, 0)})·3600", m_pc, "kg/h", "", 0),
        Krok(f"Przewody PC ↔ budynek {przew['rura']}, L = {f(L_pc, 1)} m (×2)", "∆p = 2·1,3·R·L", f"2·1,3·{f(R_pc, 3)}·{f(L_pc, 1)}", dp_pc,
             "kPa", "", 1),
        Krok("Wysokość podnoszenia pompy obiegowej (obieg z buforem szeregowym na powrocie)", "H = ∆p_pętli,max + ∆p_przew + ∆p_PC + 5",
             f"{f(dp_crit, 1)} + {f(dp_pc, 1)} + {f(pc['dp_wewn_kPa'], 0)} + 5", H_pompy, "kPa", "rozdzielacz/zawory 5 kPa [ZAŁ]", 1),
        Krok("Suma przepływów pętli podłogowych", "Σṁ_H", "", m_tot, "kg/h", "", 0),
    ]
    # ---- bufor
    V_petli = sum(p.V_l for p in petle)
    V_open = par.udzial_petli_otwartych * V_petli
    E_def = P_nom * par.t_odszraniania_min * 60 / 1000.0                  # kJ
    V_def = E_def / (4.19 * par.dT_bufora)
    V_run = pc["P_min"] * 1000 * par.t_min_pracy_min * 60 / 1000.0 / (4.19 * par.dT_bufora)
    V_req = max(V_def, V_run)
    V_buf = max(0.0, V_req - V_open)
    V_dob = ceil_to(V_buf, BUFORY) if V_buf > 0 else 0
    buf = {"V_petli": V_petli, "V_open": V_open, "V_def": V_def, "V_run": V_run, "V_req": V_req, "V_buf": V_buf, "V_dob": V_dob}
    kroki["bufor"] = [
        Krok("Objętość wody w pętlach", "V = Σπd²/4·L", "", V_petli, "dm³", "", 1),
        Krok("Objętość stale otwarta (pętle bez siłowników)", "V_otw = u·V", f"{f(par.udzial_petli_otwartych, 2)}·{f(V_petli, 1)}", V_open, "dm³", "[ZAŁ]", 1),
        Krok("Energia odszraniania", "E = P_nom·t_def", f"{f(P_nom / 1000, 1)}·{f(par.t_odszraniania_min, 0)}·60", E_def, "kJ", "[ZAŁ]", 0),
        Krok("Objętość na odszranianie przy spadku 5 K", "V_def = E/(c·∆θ)", f"{f(E_def, 0)}/(4,19·{f(par.dT_bufora, 0)})", V_def, "dm³", "", 1),
        Krok("Objętość na minimalny czas pracy sprężarki", "V_run = P_min·t_min/(c·∆θ)",
             f"{f(pc['P_min'], 1)}·{f(par.t_min_pracy_min, 0)}·60/(4,19·{f(par.dT_bufora, 0)})", V_run, "dm³", "", 1),
        Krok("Wymagana pojemność bufora", "V_buf = max(V_def, V_run) − V_otw", "", V_buf, "dm³", "", 1),
        Krok("Dobrano bufor szeregowy na powrocie", "V", "", V_dob, "dm³", "", 0),
    ]
    # ---- naczynia
    kond_ids = [k["id"] for k in dane.kondygnacje]
    top = max((kond_ids.index(x["pom"].kond) for x in podl), default=0)
    h_stat = dane.rzedna(kond_ids[top]) + 0.5 - (dane.rzedna(kond_ids[0]) + 0.5)
    V_c = V_petli + V_dob + pc["V_wewn"] + 10.0 + math.pi * (rura[2] / 1000) ** 2 / 4 * 2 * L_pc * 1000 + 5.0
    nco = naczynie_wzbiorcze(V_c, par.theta_max_co, h_stat, par.p_SV)
    Vz = par.V_zas_cwu or (cwu or {}).get("V_zas", 200)
    e_c = rho_wody(10.0) / rho_wody(par.theta_dez) - 1.0
    Ve_c = e_c * Vz
    p0c = par.p_zasilania_cwu - 0.2
    pec = par.p_SV_cwu - 0.5
    Vn_c = Ve_c * (pec + 1) / (pec - p0c)
    ncwu = {"V_zas": Vz, "e": e_c, "V_e": Ve_c, "p_0": p0c, "p_e": pec, "V_n": Vn_c, "V_dob": ceil_to(Vn_c, NACZYNIA) or NACZYNIA[-1]}
    kroki["nacz"] = [
        Krok("Pojemność instalacji c.o.", "V_c = V_pętli + V_bufora + V_PC + V_wężownicy + V_przewodów", "", V_c, "dm³", "", 1),
        Krok(f"Współczynnik rozszerzalności (10 → {f(par.theta_max_co, 0)} °C)", "e = ρ(10)/ρ(θ_max) − 1", "", 100 * nco["e"], "%",
             "gęstość wody (Kell)", 2),
        Krok("Ciśnienia", "p_0 = h/10 + 0,2 (≥ 0,5); p_e = p_SV − 0,5", f"h = {f(h_stat, 2)} m; p_SV = {f(par.p_SV, 1)} bar",
             f"p_0 = {f(nco['p_0'], 2)} bar; p_e = {f(nco['p_e'], 2)} bar", "", "PN-EN 12828 zał. D [W]"),
        Krok("Pojemność naczynia c.o.", "V_n = (V_e + V_V)·(p_e + 1)/(p_e − p_0)",
             f"({f(nco['V_e'], 2)} + {f(nco['V_V'], 2)})·({f(nco['p_e'], 2)} + 1)/({f(nco['p_e'], 2)} − {f(nco['p_0'], 2)})", nco["V_n"],
             "dm³", "", 1),
        Krok("Dobrano naczynie przeponowe c.o.", "", "", nco["V_dob"], "dm³", "(sprawdzić naczynie wbudowane w PC)", 0),
        Krok(f"Naczynie c.w.u. (zasobnik {f(Vz, 0)} dm³, 10 → {f(par.theta_dez, 0)} °C)", "V_n = e·V_zas·(p_e + 1)/(p_e − p_0)",
             f"{f(e_c, 4)}·{f(Vz, 0)}·({f(pec, 1)} + 1)/({f(pec, 1)} − {f(p0c, 1)})", Vn_c, "dm³",
             "p_0 = p_red − 0,2; p_e = p_SV − 0,5 [W]", 1),
        Krok("Dobrano naczynie przeponowe c.w.u. (przepływowe, atest PZH)", "", "", ncwu["V_dob"], "dm³", "", 0),
    ]
    # ---- hałas
    L_noc = par.L_noc if par.L_noc is not None else float(wym("usytuowanie", "halas_LAeq_noc_max", 40) or 40)
    L_dz = par.L_dzien if par.L_dzien is not None else float(wym("usytuowanie", "halas_LAeq_dzien_max", 50) or 50)
    L_cel = par.L_cel if par.L_cel is not None else float(wym("usytuowanie", "halas_noc_cel", 35) or 35)
    Q_dir = 4.0
    if jz is None:
        obr = dane.obrysy.get(kond_ids[0])
        x0, y0, x1, y1 = obr.bounds
        xy = ((x0 + x1) / 2, y1 + 1.0)
        zal.append("Położenie jednostki zewnętrznej PC nie podane (instalacje.yaml: lokalizacje.pompa_ciepla_jz) — przyjęto 1 m od "
                   "elewacji północnej, przy ścianie (Q = 4) [ZAŁ].")
    else:
        xy = jz[:2]
        ust = (dane.inst.get("lokalizacje", {}).get("pompa_ciepla_jz") or {}).get("ustawienie", "przy_scianie") \
            if isinstance(dane.inst.get("lokalizacje", {}).get("pompa_ciepla_jz"), dict) else "przy_scianie"
        Q_dir = {"wolnostojaca": 2.0, "przy_scianie": 4.0, "naroze": 8.0}.get(ust, 4.0)
    from shapely.geometry import Point
    D = dane.dzialka.get("transform")
    granice = []
    if D is not None:
        for s in D.lista("sasiedzi"):
            if s.get("obrys"):
                P = D.poly_bud(s["obrys"])
                granice.append((f"działka sąsiednia {s.get('nr')}", P.distance(Point(*xy))))
    if not granice and dane.dzialka.get("obrys") is not None:
        granice.append(("granica działki", dane.dystans_do_granicy(xy)))
    r_gr = min((g[1] for g in granice), default=10.0)
    nazwa_gr = min(granice, key=lambda g: g[1])[0] if granice else "granica działki"
    LA = poziom_halasu(pc["L_WA_noc"], max(r_gr, 1.0), Q_dir)
    LA_dz = poziom_halasu(pc["L_WA"], max(r_gr, 1.0), Q_dir)
    r_sas = dane.dystans_do_sasiada(xy)
    LA_sas = poziom_halasu(pc["L_WA_noc"], r_sas, Q_dir) if r_sas == r_sas else float("nan")
    DI = 10 * math.log10(Q_dir / 2)
    halas = {"xy": xy, "Q": Q_dir, "r": r_gr, "granica": nazwa_gr, "L_A_granica": LA, "L_A_dzien": LA_dz, "r_sas": r_sas, "L_A_sas": LA_sas,
             "r_40": odleglosc_dla_limitu(pc["L_WA_noc"], L_noc, Q_dir), "r_35": odleglosc_dla_limitu(pc["L_WA_noc"], L_cel, Q_dir)}
    kroki["halas"] = [
        Krok(f"Jednostka zewnętrzna ({f(xy[0])}; {f(xy[1])}), ustawienie Q = {f(Q_dir, 0)} (DI = {f(DI, 1)} dB); najbliższa: {nazwa_gr}",
             "r", "", r_gr, "m", "", 2),
        Krok("Poziom dźwięku w nocy na granicy (tryb cichy)", "L_A = L_WA − 20·log r − 8 + DI",
             f"{f(pc['L_WA_noc'], 0)} − 20·log({f(r_gr, 2)}) − 8 + {f(DI, 1)}", LA, "dB(A)", "PORT PC p. 4.4 [W]", 1),
        Krok("Poziom dźwięku w dzień na granicy", "L_A = L_WA − 20·log r − 8 + DI", f"{f(pc['L_WA'], 0)} − 20·log({f(r_gr, 2)}) − 8 + {f(DI, 1)}",
             LA_dz, "dB(A)", "", 1),
        Krok("Odległość zapewniająca 40 dB / 35 dB w nocy", "r = √(Q/(4π)·10^((L_WA − L)/10))", "",
             f"{f(halas['r_40'], 1)} m / {f(halas['r_35'], 1)} m", "", ""),
    ]
    war.append(Warunek(f"Hałas PC w nocy na granicy ({nazwa_gr})", LA, "<=", L_noc, "dB(A)", "Dz.U. 2014 poz. 112 tab. 1 lp. 2a (L_Aeq,N)",
                       "W-024", nd=1))
    war.append(Warunek(f"Hałas PC w dzień na granicy ({nazwa_gr})", LA_dz, "<=", L_dz, "dB(A)", "Dz.U. 2014 poz. 112 (L_Aeq,D)", "W-024", nd=1))
    war.append(Warunek("Hałas PC w nocy — cel projektowy", LA, "<=", L_cel, "dB(A)", "R8 3.4 [ZAŁ]", "W-024", nd=1))
    d_min = float(wym("usytuowanie", "pc_odl_granica_E_min", 6.0) or 6.0)
    war.append(Warunek("Odległość jednostki PC od granicy z działką sąsiednią (MN)", r_gr, ">=", d_min, "m",
                       "W-024 (dla LAMELA: granica E) [ZAŁ]", "W-024"))
    # strefa R290 — otwory w promieniu 1 m
    strefa = float(wym("ogrzewanie", "pc_R290_strefa_bezp", 1.0) or 1.0)
    kol = []
    if dane.model is not None:
        for ot in dane.model.otwory(kond=kond_ids[0]):
            try:
                dd = ot.footprint.distance(Point(*xy))
            except Exception:
                continue
            if dd <= strefa + 0.4 and ot.typ != "drzwi":
                kol.append((ot.id, dd))
    war.append(Warunek(f"Strefa bezpieczeństwa R290 ({f(strefa, 1)} m + wymiar urządzenia ≈ 0,4 m): otwory w strefie", len(kol), "==", 0,
                       "szt.", "PN-EN 378-1; DTR (W-156) — " + (", ".join(o for o, _ in kol) if kol else "brak"), "W-156", nd=0))
    zal += [f"θ_e = {f(te, 0)} °C ({wym_zrodlo('ogrzewanie', 'theta_e')}); θ_i wg modelu (20/24 °C).",
            "Ogrzewanie podłogowe: PE-X/PE-RT 16×2,0, jastrych cementowy, wykładziny wg kodów posadzek modelu; "
            "współczynniki zabudowy A_F/A: " + ", ".join(f"{k} {f(v, 2)}" for k, v in par.f_zabudowy.items()) + " [ZAŁ].",
            "Regulacja pomieszczeniowa: termostaty + siłowniki na pętlach (WT §135 ust. 7–9; W-152) → bufor szeregowy.",
            "Przewody PC ↔ budynek (monoblok): na zewnątrz izolacja 2× grubość wg WT z płaszczem UV, zabezpieczenie przed "
            "zamarzaniem (zawory antyzamarzaniowe lub glikol + wymiennik) [ZAŁ]."]
    return WynikOgrzewanie(dane=dane, par=par, phi=phi, phi_zrodlo=zr, Phi_HL=Phi, Phi_W=Phi_W, pc=pc, biwalentny=o, bin=o,
                           podlogowka=wiersze, petle=petle, rozdzielacze=rozdzielacze, theta_V=thV, bufor=buf, naczynie_co=nco,
                           naczynie_cwu=ncwu, halas=halas, przewody_pc=przew, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikOgrzewanie) -> Raport:
    d = w.dane
    R = Raport("Ogrzewanie — pompa ciepła, ogrzewanie podłogowe, bufor, naczynia, hałas",
               f"Obiekt: {d.nazwa}. Φ_HL: {w.phi_zrodlo}. Dane urządzeń przykładowe [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §133–135 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-150…W-156; W-024.",
             "PN-EN 12831:2006 (WT) / PN-EN 12831-1:2017 — obciążenie cieplne: moduł energii (dane wejściowe tego modułu).",
             "PN-EN 1264-2/-3/-4 — ogrzewanie płaszczyznowe; PN-EN 14825:2022-11 (SCOP); PN-EN 12828 / PN-B-02414:1999 — naczynia.",
             "Rozp. (UE) 2024/573 (F-gazy), 813/2013 (ekoprojekt), Dz.U. 2014 poz. 112 (hałas)."] + w.zalozenia + d.uwagi)
    R.h(2, "2. Moc źródła i pompa ciepła")
    R.kroki(w.kroki["moc"])
    R.tab(["Pomieszczenie", "Φ_HL [W]"], [[f"{k} {d.pom(k).nazwa if d.pom(k) else ''}", f(v, 0)] for k, v in w.phi.items()], "lr")
    pc = w.pc
    R.tab(["θ_e [°C]"] + [f(t, 0) for t in pc["T"]], [["P_PC,max W35 [kW]"] + [f(x, 1) for x in pc["P"]],
                                                     ["COP W35"] + [f(x, 2) for x in pc["COP"]]], "l" + "r" * len(pc["T"]))
    R.p(f"Dobrano: **{pc['model']}** — monoblok powietrze–woda, czynnik R290; SCOP (35 °C, klimat umiarkowany) {f(pc['SCOP_35'], 2)}; "
        f"η_s = {f(100 * pc['eta_s_35'], 0)} %; L_WA {f(pc['L_WA'], 0)} dB(A) (tryb cichy {f(pc['L_WA_noc'], 0)} dB(A)); COP c.w.u. "
        f"{f(pc['COP_cwu'], 1)}; grzałka rezerwowa {f(w.par.grzalka_kW, 1)} kW (3f).")
    R.h(3, "2.1 Punkt biwalentny i bilans roczny (TMY)")
    R.kroki(w.kroki["biw"])
    R.h(2, "3. Ogrzewanie podłogowe (PN-EN 1264)")
    R.kroki(w.kroki["podl"])
    R.tab(["Pom.", "Nazwa", "Kond.", "Φ_HL [W]", "A_F [m²]", "q [W/m²]", "θ_F,m [°C]", "R_λ,B", "T [cm]", "∆θ_H [K]", "θ_R [°C]",
           "σ [K]", "ṁ [kg/h]", "Pętle", "L [m]"], w.podlogowka, "lllrrrrlrrrrrrr")
    R.tab(["Pętla", "T [cm]", "L [m]", "ṁ [kg/h]", "∆p [kPa]", "V [dm³]"],
          [[f"{p.pom}/{p.nr}", f(100 * p.T, 0), f(p.L, 1), f(p.m_kgh, 1), f(p.dp, 1), f(p.V_l, 1)] for p in w.petle], "lrrrrr")
    R.tab(["Kondygnacja", "Pętle", "Rozdzielacze (sekcje)", "Σṁ [kg/h]", "∆p_max [kPa]"],
          [[r["kond"], r["petle"], f"{r['rozdzielacze']} × ({', '.join(str(s) for s in r['sekcje'])})", f(r["m_kgh"], 1), f(r["dp_max"], 1)]
           for r in w.rozdzielacze], "lrlrr")
    R.p("Rozdzielacze z przepływomierzami i zaworami termostatycznymi pod siłowniki; termostaty pokojowe w każdym pomieszczeniu "
        "(W-152); łazienki — dodatkowo grzejnik drabinkowy z grzałką (okres przejściowy) [ZAŁ].")
    R.h(2, "4. Obieg PC, pompa, bufor")
    R.kroki(w.kroki["pompa"])
    R.kroki(w.kroki["bufor"])
    R.h(2, "5. Naczynia wzbiorcze")
    R.kroki(w.kroki["nacz"])
    R.h(2, "6. Hałas jednostki zewnętrznej")
    R.kroki(w.kroki["halas"])
    R.lista(["Posadowienie antywibracyjne (fundament, wibroizolatory), połączenia elastyczne (WT §327 ust. 2–3; W-232).",
             "Nie pod oknami sypialni; strefa R290 wolna od okien, drzwi, wpustów, studzienek i zagłębień (W-156) — wrysować na PZT.",
             "Skropliny — do gruntu w strefie niezamarzającej (studzienka żwirowa), nie do studzienek w strefie R290 (W-146)."])
    R.h(2, "7. Sprawdzenia")
    R.war(w.warunki)
    R.h(2, "8. Dane do charakterystyki energetycznej")
    R.tab(["Wielkość", "Wartość"], [[k, fa(v, 4) if isinstance(v, float) else str(v)] for k, v in w.do_dict()["do_EP"].items()], "lr")
    R.zrodlo("WT §133–135, §327 (t.j. Dz.U. 2022 poz. 1225 ze zm.)", "PN-EN 1264-2:2009+A1:2012, -3, -4 — zał. A (K_H) [NZW tablice]",
             "Rozp. (UE) 2024/573 zał. IV pkt 8–9; rozp. (UE) 813/2013 zał. II",
             "PORT PC, Wytyczne do ograniczania hałasu instalacji z pompami ciepła, p. 4.4",
             "Rozp. MŚ — dopuszczalne poziomy hałasu, t.j. Dz.U. 2014 poz. 112, tab. 1 lp. 2a",
             "VDI 4645:2018 — dodatek mocy na c.w.u., punkt biwalentny [W]; PN-EN 12828 zał. D [W]",
             "PVGIS 5.3 TMY Poznań (JRC KE), pobrano 2026-09-25 — rozkład godzinowy temperatur")
    return R
