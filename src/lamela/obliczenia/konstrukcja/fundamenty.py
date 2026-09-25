"""Posadowienie bezpośrednie wg PN-EN 1997-1:2008 + NA (DA2*) — R5-80…R5-95, W-280…W-286.

Zakres:
* nośność podłoża w warunkach z odpływem (zał. D, D.4): R/A' = c'N_c b_c s_c i_c + q'N_q b_q s_q i_q + ½γ'B'N_γ b_γ s_γ i_γ;
  podejście DA2* (NA.2.6 — Ap2:2010): opór graniczny z charakterystycznych efektów oddziaływań, R_d = R_k/γ_R;v,
  γ_R;v = 1,4; sprawdzenie V_d ≤ R_d, V_d z kombinacji STR/GEO (6.10a/b); przesunięcie: γ_R;h = 1,1;
* osiadanie (uproszczone): sumowanie warstw pod środkiem fundamentu, naprężenia wg Boussinesqa dla prostokąta
  obciążonego równomiernie (wzór narożny Steinbrennera/Newmarka), zasięg do σ_z ≤ 0,2·σ'_v0 (PN-EN 1997-1 6.6.2(6)),
  s = Σσ_z·h_i/M₀ (moduł edometryczny), bez odciążenia wykopem i bez wpływu sąsiednich fundamentów [UPR]; s ≤ 50 mm (NA.3);
* ławy i stopy: sprawdzenie jako betonowe niezbrojone poprzecznie (PN-EN 1992-1-1 12.9.3, (12.13)) albo zbrojenie na
  zginanie wspornika odsadzki; zbrojenie podłużne ław (minimalne/konstrukcyjne); przebicie stóp (6.4.4);
* płyta fundamentowa — model Winklera: k_s = p/s (z osiadania płyty), pasmo płyty pod ścianą jak belka na podłożu
  sprężystym (Hetényi: belka nieskończona i półnieskończona) [UPR — analiza szczegółowa MES płyty na podłożu];
* głębokość posadowienia: h_z = 0,8 m (PN-81/B-03020 — wiedza techniczna), wymagania projektu D ≥ 1,0 m (zewn.),
  ≥ 0,5 m (wewn.) (R5 3.8, W-284).
Jednostki: kN, m, kPa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .materialy import Beton, StalZbrojeniowa, pole_preta
from .wspolne import Grunt, Parametry, Wynik, f
from . import zelbet


# ==================================================================================================
# Nośność podłoża (zał. D)
# ==================================================================================================
@dataclass
class Nosnosc(Wynik):
    N_q: float = 0.0
    N_c: float = 0.0
    N_g: float = 0.0
    q_Rk: float = 0.0      # R_k/A' [kPa]
    R_k: float = 0.0       # [kN] (na 1 m dla ław)
    R_d: float = 0.0
    B_ef: float = 0.0
    L_ef: float = 0.0


def wspolczynniki_nosnosci(fi_deg: float) -> tuple[float, float, float]:
    """N_q = e^(π·tg φ')·tg²(45° + φ'/2), N_c = (N_q − 1)·ctg φ', N_γ = 2·(N_q − 1)·tg φ' (zał. D, D.4, δ ≥ φ'/2)."""
    fi = math.radians(fi_deg)
    Nq = math.exp(math.pi * math.tan(fi)) * math.tan(math.pi / 4 + fi / 2) ** 2
    Nc = (Nq - 1) / math.tan(fi) if fi > 0 else math.pi + 2
    Ng = 2 * (Nq - 1) * math.tan(fi)
    return Nq, Nc, Ng


def gamma_efektywny(grunt: Grunt, z_od: float, z_do: float) -> float:
    """Średni ciężar objętościowy efektywny warstwy między głębokościami z_od…z_do [m p.p.t.] (γ nad ZWG, γ' pod)."""
    if z_do <= z_od:
        return grunt.gamma
    a = max(min(grunt.ZWG, z_do) - z_od, 0.0)
    b = (z_do - z_od) - a
    return (a * grunt.gamma + b * grunt.gamma_prim) / (z_do - z_od)


def nosnosc_podloza(B: float, D: float, V_k: float, V_d: float, grunt: Grunt, p: Parametry | None = None,
                    L: float | None = None, H_k: float = 0.0, e_B: float = 0.0, e_L: float = 0.0,
                    nazwa: str = "Nośność podłoża (PN-EN 1997-1 zał. D, DA2*)") -> Nosnosc:
    """Warunki z odpływem. B [m], L [m] (None — ława, wynik na 1 m), D — zagłębienie (min. z obu stron) [m],
    V_k, V_d — siła pionowa charakterystyczna i obliczeniowa [kN lub kN/m], H_k — siła pozioma char. (w kierunku B)."""
    p = p or Parametry()
    w = Nosnosc(nazwa=nazwa)
    Nq, Nc, Ng = wspolczynniki_nosnosci(grunt.fi_k)
    w.krok("Parametry podłoża (charakterystyczne, M1: γ_φ = 1,0)", "φ'_k; c'_k; γ", "",
           f"{f(grunt.fi_k, 1)}°; {f(grunt.c_k, 1)} kPa; {f(grunt.gamma, 1)} kN/m³ — {grunt.nazwa}")
    w.krok("Współczynnik nośności (nadkład)", "N_q = e^(π·tg φ')·tg²(45° + φ'/2)", "", Nq, nd=2, zrodlo="(D.2)")
    w.krok("Współczynnik nośności (spójność)", "N_c = (N_q − 1)·ctg φ'", "", Nc, nd=2)
    w.krok("Współczynnik nośności (ciężar gruntu)", "N_γ = 2·(N_q − 1)·tg φ'", "", Ng, nd=2)
    Bp = B - 2 * abs(e_B)
    pasmo = L is None
    Lp = (L - 2 * abs(e_L)) if not pasmo else 1.0
    if pasmo:
        w.krok("Szerokość efektywna ławy", "B' = B − 2e_B", f"{f(B, 2)} − 2·{f(e_B, 3)}", Bp, "m", nd=3)
        sq = sg = sc = 1.0
    else:
        w.krok("Wymiary efektywne", "B' = B − 2e_B; L' = L − 2e_L", "", f"{f(Bp, 3)} m × {f(Lp, 3)} m")
        r = Bp / Lp
        sq = 1 + r * math.sin(math.radians(grunt.fi_k))
        sg = 1 - 0.3 * r
        sc = (sq * Nq - 1) / (Nq - 1)
        w.krok("Współczynniki kształtu", "s_q = 1 + (B'/L')·sin φ'; s_γ = 1 − 0,3·B'/L'", "", f"s_q = {f(sq, 3)}; s_γ = {f(sg, 3)}",
               zrodlo="(D.4)")
    A = Bp * Lp
    if H_k > 0:
        m = (2 + Bp / Lp) / (1 + Bp / Lp) if not pasmo else 2.0
        base = 1 - H_k / (V_k + A * grunt.c_k / math.tan(math.radians(grunt.fi_k)))
        iq = max(base, 0) ** m
        ig = max(base, 0) ** (m + 1)
        w.krok("Współczynniki nachylenia obciążenia", "i_q = [1 − H/(V + A'c'ctg φ')]^m; i_γ = […]^(m+1)", "", f"{f(iq, 3)}; {f(ig, 3)}",
               zrodlo="zał. D (D.4)")
    else:
        iq = ig = 1.0
    ic = iq - (1 - iq) / (Nc * math.tan(math.radians(grunt.fi_k))) if grunt.fi_k > 0 else 1.0
    g_nad = gamma_efektywny(grunt, 0.0, D)
    qprim = g_nad * D
    g_pod = gamma_efektywny(grunt, D, D + B)
    w.krok("Naprężenie od nadkładu w poziomie posadowienia", "q' = γ·D", f"{f(g_nad, 2)}·{f(D, 2)}", qprim, "kPa", nd=2)
    if abs(g_pod - grunt.gamma) > 1e-6:
        w.krok("Ciężar efektywny gruntu pod fundamentem (wpływ ZWG)", "γ'", "", g_pod, "kN/m³", nd=2)
    t1 = grunt.c_k * Nc * sc * ic
    t2 = qprim * Nq * sq * iq
    t3 = 0.5 * g_pod * Bp * Ng * sg * ig
    qR = t1 + t2 + t3
    w.krok("Jednostkowy opór graniczny", "R_k/A' = c'·N_c·s_c·i_c + q'·N_q·s_q·i_q + ½·γ'·B'·N_γ·s_γ·i_γ",
           f"{f(t1, 1)} + {f(qprim, 2)}·{f(Nq, 2)}·{f(sq, 3)}·{f(iq, 3)} + 0,5·{f(g_pod, 2)}·{f(Bp, 3)}·{f(Ng, 2)}·{f(sg, 3)}·{f(ig, 3)}",
           qR, "kPa", nd=1, zrodlo="(D.2)")
    Rk = qR * A
    Rd = Rk / p.gR_v
    w.krok("Opór graniczny" + (" (na 1 m ławy)" if pasmo else ""), "R_k = (R_k/A')·A'", f"{f(qR, 1)}·{f(A, 3)}", Rk, "kN" + ("/m" if pasmo else ""), nd=1)
    w.krok("Obliczeniowy opór graniczny (DA2*)", "R_d = R_k/γ_R;v", f"{f(Rk, 1)}/{f(p.gR_v, 2)}", Rd, "kN" + ("/m" if pasmo else ""), nd=1,
           zrodlo="NA.2.6 (Ap2:2010), tabl. A.5")
    w.N_q, w.N_c, w.N_g, w.q_Rk, w.R_k, w.R_d, w.B_ef, w.L_ef = Nq, Nc, Ng, qR, Rk, Rd, Bp, Lp
    w.warunek("Nośność podłoża (GEO, DA2*)", V_d, Rd, "kN" + ("/m" if pasmo else ""), "PN-EN 1997-1 (6.1), NA.2.6",
              nd=1, symbol_E="V_d", symbol_R="R_d")
    if grunt.status != "zweryfikowane":
        w.uwaga("Parametry gruntu PRZYKŁADOWE (brief) — w II kat. geotechnicznej wymagane badania CPT/DPL (W-282, E-04).")
    return w


def przesuniecie(H_d: float, V_k_korzystne: float, grunt: Grunt, p: Parametry | None = None, delta: float | None = None) -> Wynik:
    """Nośność na przesunięcie (6.5.3, warunki z odpływem): R_h;d = V'_k·tg δ_k/γ_R;h, δ_k = φ'_k (fundament
    betonowany na miejscu), γ_R;h = 1,1 (DA2)."""
    p = p or Parametry()
    w = Wynik(nazwa="Przesunięcie w poziomie posadowienia")
    d = grunt.fi_k if delta is None else delta
    R = V_k_korzystne * math.tan(math.radians(d)) / p.gR_h
    w.krok("Opór na przesunięcie", "R_h;d = V'·tg δ/γ_R;h", f"{f(V_k_korzystne, 1)}·tg {f(d, 1)}°/{f(p.gR_h, 2)}", R, "kN", zrodlo="(6.3a)")
    w.warunek("Przesunięcie", H_d, R, "kN", "(6.2)", symbol_E="H_d", symbol_R="R_h;d")
    return w


# ==================================================================================================
# Osiadanie
# ==================================================================================================
def wsp_naroznika(B: float, L: float, z: float) -> float:
    """Współczynnik wpływu naroża prostokąta B×L obciążonego równomiernie na głębokości z (Boussinesq — Newmark)."""
    if z <= 1e-9:
        return 0.25
    m, n = B / z, L / z
    m2, n2 = m * m, n * n
    V = m2 + n2 + 1
    a = 2 * m * n * math.sqrt(V) / (V + m2 * n2) * (m2 + n2 + 2) / V
    den = V - m2 * n2
    b = math.atan2(2 * m * n * math.sqrt(V), den)
    return (a + b) / (4 * math.pi)


@dataclass
class Osiadanie(Wynik):
    s: float = 0.0           # mm
    z_max: float = 0.0
    warstwy: list = field(default_factory=list)


def osiadanie(B: float, L: float | None, D: float, q: float, grunt: Grunt, p: Parametry | None = None,
              nazwa: str = "Osiadanie (metoda sumowania warstw)") -> Osiadanie:
    """Osiadanie pod środkiem fundamentu B×L [m] (L = None → ława, L = 10B) od nacisku q [kPa] (SLS): σ_z = 4·q·I(B/2, L/2, z),
    s = Σσ_z·h_i/M₀; zasięg: σ_z ≤ 0,2·σ'_v0 (6.6.2(6)) [UPR: nacisk całkowity bez odciążenia wykopem — bezpiecznie]."""
    p = p or Parametry()
    w = Osiadanie(nazwa=nazwa)
    Lx = 10 * B if L is None else L
    hi = min(0.25 * B, 0.5)
    z = 0.0
    s = 0.0
    rows = []
    while z < 20 * B:
        zc = z + hi / 2
        sz = 4 * q * wsp_naroznika(B / 2, Lx / 2, zc)
        sv0 = gamma_efektywny(grunt, 0, D + zc) * (D + zc)
        ds = sz * hi / grunt.M0 * 1000
        s += ds
        rows.append((zc, sz, sv0, ds))
        z += hi
        if sz <= 0.2 * sv0:
            break
    w.krok("Nacisk pod fundamentem (SLS)", "q", "", q, "kPa", nd=1)
    w.krok("Moduł edometryczny", "M₀", "", grunt.M0 / 1000, "MPa", nd=0, zrodlo="[ZAŁ — do badań]")
    w.krok("Zasięg strefy aktywnej", "z_max: σ_z ≤ 0,2·σ'_v0", f"(warstwy h_i = {f(hi, 3)} m)", z, "m", nd=2, zrodlo="PN-EN 1997-1 6.6.2(6)")
    w.krok("Osiadanie", "s = Σ σ_z,i·h_i/M₀", f"Σ ({len(rows)} warstw)", s, "mm", nd=1)
    w.s, w.z_max, w.warstwy = s, z, rows
    w.warunek("Osiadanie", s, p.s_max_mm, "mm", "PN-EN 1997-1 NA.3 (tabl. NA.3)", nd=1, symbol_E="s", symbol_R="s_max")
    w.uwaga("Osiadanie orientacyjne: pominięto wpływ fundamentów sąsiednich i odciążenie wykopem; M₀ — dane przykładowe.")
    return w


# ==================================================================================================
# Ława fundamentowa
# ==================================================================================================
@dataclass
class Lawa(Wynik):
    B: float = 0.0
    h: float = 0.0
    sigma_d: float = 0.0
    zbrojenie_podl: str = ""
    zbrojenie_poprz: str = ""
    prety: list = field(default_factory=list)


def lawa(nazwa: str, B: float, h: float, t_w: float, D: float, G_k: float, Q_k: float | list, grunt: Grunt, beton: Beton,
         p: Parametry | None = None, psi0: float = 0.7, dlugosc: float = 1.0, zewnetrzna: bool = True,
         G_nad_odsadzka: float | None = None, stal: StalZbrojeniowa | None = None, Q_k_inne: float = 0.0) -> Lawa:
    """Ława pod ścianą: G_k — obciążenie stałe od ściany [kN/m]; Q_k — zmienne [kN/m]: liczba (z ψ0 = psi0) albo lista
    par (Q_k,i, ψ0,i) — każde kolejno wiodące (6.10a/6.10b), pozostałe z ψ0;
    dodaje ciężar ławy i gruntu na odsadzkach; sprawdza nośność (DA2*), osiadanie, głębokość posadowienia, ławę
    niezbrojoną poprzecznie (12.9.3) lub zbrojenie odsadzki, zbrojenie podłużne (konstrukcyjne, 9.2.1.1)."""
    p = p or Parametry()
    stal = stal or StalZbrojeniowa()
    w = Lawa(nazwa=nazwa, B=B, h=h)
    g_f = B * h * p.ciezar_zelbetu
    odsadzki = max(B - t_w, 0) * max(D - h, 0) * 18.0 if G_nad_odsadzka is None else G_nad_odsadzka
    w.krok("Ciężar ławy", "g_ł = B·h·25", f"{f(B, 2)}·{f(h, 2)}·25", g_f, "kN/m", nd=2)
    w.krok("Grunt/posadzka na odsadzkach", "g_o ≈ (B − t)·(D − h)·18", "", odsadzki, "kN/m", nd=2, zrodlo="[UPR]")
    Gk = G_k + g_f + odsadzki
    Ql = list(Q_k) if isinstance(Q_k, (list, tuple)) else [(Q_k, psi0)] + ([(Q_k_inne, psi0)] if Q_k_inne else [])
    Qk = sum(q for q, _ in Ql)
    w.krok("Obciążenie charakterystyczne w poziomie posadowienia", "V_k = G_k + ΣQ_k", f"{f(Gk, 1)} + {f(Qk, 1)}", Gk + Qk, "kN/m", nd=1)
    Va = p.gG_sup * Gk + sum(p.gQ * ps * q for q, ps in Ql)
    Vb = max([p.xi * p.gG_sup * Gk + p.gQ * q + sum(p.gQ * ps2 * q2 for j, (q2, ps2) in enumerate(Ql) if j != i)
              for i, (q, ps) in enumerate(Ql)] or [p.xi * p.gG_sup * Gk])
    Vd = max(Va, Vb)
    w.krok("Obciążenie obliczeniowe (STR/GEO)", "V_d = max(6.10a; 6.10b)", f"max({f(Va, 1)}; {f(Vb, 1)})", Vd, "kN/m", nd=1,
           zrodlo="PN-EN 1990 + NA")
    Q_k_inne = 0.0
    nos = nosnosc_podloza(B, D, Gk + Qk, Vd, grunt, p)
    w.dolacz(nos, "Nośność podłoża")
    sig_k = (Gk + Qk) / B
    osi = osiadanie(B, None, D, sig_k, grunt, p)
    w.dolacz(osi, "Osiadanie")
    # głębokość posadowienia
    Dmin = p.D_min_zewn if zewnetrzna else p.D_min_wewn
    w.krok("Głębokość posadowienia", "D (od terenu/posadzki)", "", D, "m", nd=2)
    w.warunek("Głębokość posadowienia (R5 3.8: zewn. ≥ 1,0 m, wewn. ≥ 0,5 m)", Dmin, D, "m", "W-284", nd=2,
              symbol_E="D_min", symbol_R="D")
    if zewnetrzna and grunt.wysadzinowy:
        w.warunek("Grunt wysadzinowy: D ≥ h_z", p.h_z, D, "m", "PN-B-03020:1981 p. 2.2.2 b (wycof.)", nd=2, symbol_E="h_z", symbol_R="D")
    # konstrukcja: ława niezbrojona poprzecznie
    sig_d = Vd / B
    a = (B - t_w) / 2
    fctd_pl = 0.8 * beton.f_ctk005 / beton.gamma_c
    lhs = 0.85 * h / a if a > 0 else float("inf")
    rhs = math.sqrt(3 * sig_d / 1000 / fctd_pl)
    w.krok("Odpór obliczeniowy", "σ_gd = V_d/B", f"{f(Vd, 1)}/{f(B, 2)}", sig_d, "kPa", nd=1)
    w.krok("Wysięg odsadzki", "a = (B − t)/2", f"({f(B, 2)} − {f(t_w, 2)})/2", a, "m", nd=3)
    w.krok("Warunek ławy niezbrojonej poprzecznie", "0,85·h_F/a ≥ √(3·σ_gd/f_ctd,pl), f_ctd,pl = 0,8·f_ctk,0,05/γ_c",
           f"{f(lhs, 2)} ≥ √(3·{f(sig_d / 1000, 4)}/{f(fctd_pl, 3)}) = {f(rhs, 3)}", "spełniony" if lhs >= rhs else "niespełniony",
           zrodlo="PN-EN 1992-1-1 (12.13), α_ct,pl = 0,8 [NZW NA]")
    ex = p.ekspozycja.get("fundament", "XC2")
    c = zelbet.otulina(ex, 12, p, na_gruncie="podbeton").c_nom
    d = h - c / 1000 - 0.006
    if lhs >= rhs:
        w.zbrojenie_poprz = "nie wymaga zbrojenia poprzecznego (strzemiona konstrukcyjne φ6 co 30 cm)"
        w.warunek("Ława betonowa — odsadzka (12.13)", rhs, lhs, "", "(12.13)", nd=3, symbol_E="√(3σ/f)", symbol_R="0,85h/a")
    else:
        M = sig_d * a * a / 2
        zg = zelbet.zginanie_prostokat(M, 1.0, h, d, beton, stal, nazwa="Zginanie odsadzki ławy (na 1 m)")
        fi, s, As = zelbet.dobierz_plyta(zg.As_req, 250.0, 10, 16, As_min=zg.As_min)
        w.dolacz(zg, "Zbrojenie poprzeczne odsadzki")
        w.zbrojenie_poprz = f"φ{fi} co {f(s / 10, 0)} cm"
        w.warunek("Zbrojenie poprzeczne ławy", zg.As_req, As, "mm²/m", "6.1", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
    # zbrojenie podłużne
    Asmin = max(0.0013 * B * 1000 * d * 1000, 4 * pole_preta(12))
    n12 = max(4, int(math.ceil(Asmin / pole_preta(12))))
    w.krok("Zbrojenie podłużne (konstrukcyjne, rozkład nierównomiernych osiadań)", "A_s ≥ max(0,0013·B·d; 4φ12)",
           f"max(0,0013·{f(B * 1000, 0)}·{f(d * 1000, 0)}; 452)", Asmin, "mm²", nd=0, zrodlo="9.2.1.1 (analogia belki) [UPR]")
    w.zbrojenie_podl = f"{n12}φ12 (A_s = {f(n12 * pole_preta(12) / 100, 2)} cm²), strzemiona φ6 co 30 cm"
    w.krok("Przyjęto zbrojenie podłużne", "", "", w.zbrojenie_podl)
    w.sigma_d = sig_d
    Ls = dlugosc
    w.prety = [zelbet.Pret(nazwa, 1, 12, round(Ls + 2 * 0.5, 2), n12, "00", "(+ zakłady/zakotwienia w narożach)"),
               zelbet.Pret(nazwa, 2, 6, round(2 * (B - 0.1) + 2 * (h - 0.1) + 0.2, 2), int(Ls / 0.3) + 1, "51",
                           f"{f((B - 0.1) * 100, 0)}×{f((h - 0.1) * 100, 0)} cm")]
    return w


# ==================================================================================================
# Stopa fundamentowa
# ==================================================================================================
def stopa(nazwa: str, B: float, L: float, h: float, a_sl: float, D: float, G_k: float, Q_k: float, grunt: Grunt,
          beton: Beton, p: Parametry | None = None, psi0: float = 0.7, M_k: float = 0.0, H_k: float = 0.0,
          stal: StalZbrojeniowa | None = None) -> Lawa:
    """Stopa B×L×h pod słupem a_sl × a_sl: nośność (DA2*, mimośród od M_k), osiadanie, przebicie (6.4.4), zginanie
    wsporników stopy (lub warunek stopy niezbrojonej 12.9.3)."""
    p = p or Parametry()
    stal = stal or StalZbrojeniowa()
    w = Lawa(nazwa=nazwa, B=B, h=h)
    gf = B * L * h * p.ciezar_zelbetu + B * L * max(D - h, 0) * 18.0
    w.krok("Ciężar stopy i gruntu nad nią", "G_f = B·L·h·25 + B·L·(D − h)·18", "", gf, "kN", nd=2)
    Gk = G_k + gf
    Vk = Gk + Q_k
    Vd = max(p.gG_sup * Gk + p.gQ * psi0 * Q_k, p.xi * p.gG_sup * Gk + p.gQ * Q_k)
    w.krok("Obciążenie obliczeniowe", "V_d = max(6.10a; 6.10b)", "", Vd, "kN", nd=1)
    e = abs(M_k) / Vk if Vk > 0 else 0.0
    nos = nosnosc_podloza(B, D, Vk, Vd, grunt, p, L=L, H_k=H_k, e_B=e)
    w.dolacz(nos, "Nośność podłoża")
    osi = osiadanie(B, L, D, Vk / (B * L), grunt, p)
    w.dolacz(osi, "Osiadanie")
    w.warunek("Głębokość posadowienia", p.D_min_zewn, D, "m", "W-284", nd=2, symbol_E="D_min", symbol_R="D")
    # przebicie (6.4.4): obwód kontrolny w odległości a = d
    c = zelbet.otulina(p.ekspozycja.get("fundament", "XC2"), 12, p, na_gruncie="podbeton").c_nom
    d = h - c / 1000 - 0.012
    sig = (Vd - p.gG_sup * gf) / (B * L)
    VEd = Vd - p.gG_sup * gf
    a = d
    u = 4 * a_sl + 2 * math.pi * a
    Ain = a_sl * a_sl + 4 * a_sl * a + math.pi * a * a
    VEd_red = max(VEd - sig * min(Ain, B * L), 0.0)
    vEd = VEd_red / (u * d) / 1000
    k = min(1 + math.sqrt(200 / (d * 1000)), 2.0)
    rho = 0.002
    vRd = max(0.18 / beton.gamma_c * k * (100 * rho * beton.f_ck) ** (1 / 3), 0.035 * k ** 1.5 * math.sqrt(beton.f_ck)) * 2 * d / a
    w.krok("Przebicie — obwód kontrolny w odległości a = d", "u = 4·c + 2π·a", f"4·{f(a_sl, 2)} + 2π·{f(a, 3)}", u, "m", nd=3,
           zrodlo="6.4.4(2)")
    w.krok("Siła przebijająca zredukowana o odpór", "V_Ed,red = V_Ed − σ·A_in", "", VEd_red, "kN", nd=1)
    w.krok("Naprężenie", "v_Ed = V_Ed,red/(u·d)", "", vEd, "MPa", nd=3)
    w.krok("Nośność (ρ_l = 0,2 % — min.)", "v_Rd = C_Rd,c·k·(100ρf_ck)^(1/3)·2d/a ≥ v_min·2d/a", "", vRd, "MPa", nd=3, zrodlo="(6.50)")
    w.warunek("Przebicie stopy", vEd, vRd, "MPa", "(6.50)", nd=3, symbol_E="v_Ed", symbol_R="v_Rd")
    # zginanie wspornika stopy
    cw = (B - a_sl) / 2
    M = sig * L * cw * cw / 2
    zg = zelbet.zginanie_prostokat(M, L, h, d, beton, stal, nazwa="Zginanie wspornika stopy")
    w.dolacz(zg, "Zbrojenie dolne stopy")
    fi, s, As = zelbet.dobierz_plyta(zg.As_req / L, 250.0, 10, 16, As_min=zg.As_min / L)
    w.zbrojenie_poprz = f"siatka dołem φ{fi} co {f(s / 10, 0)} cm w obu kierunkach"
    n = int(B / (s / 1000)) + 1
    w.prety = [zelbet.Pret(nazwa, 1, fi, round(B - 0.1 + 2 * 0.15, 2), 2 * n, "21", "z odgięciem 15 cm")]
    w.sigma_d = sig
    return w


# ==================================================================================================
# Płyta fundamentowa — model Winklera
# ==================================================================================================
def plyta_winkler(h: float, beton: Beton, P_d: float, k_s: float, krawedz: bool = False, stal: StalZbrojeniowa | None = None,
                  p: Parametry | None = None, nazwa: str = "Płyta fundamentowa — pasmo pod ścianą (Winkler/Hetényi)") -> Wynik:
    """Pasmo płyty b = 1 m pod obciążeniem liniowym P_d [kN/m] (ściana): λ = ⁴√(k_s·b/(4·E·I)); belka nieskończona:
    M = P/(4λ), w = P·λ/(2k); obciążenie przy krawędzi (półnieskończona): M_max ≈ 0,3224·P/λ, w = 2·P·λ/k [UPR].
    E·I — przekrój niezarysowany z E_cm/2 (uwzględnienie zarysowania i pełzania) [UPR]."""
    p = p or Parametry()
    stal = stal or StalZbrojeniowa()
    w = Wynik(nazwa=nazwa)
    EI = beton.E_cm * 1000 / 2 * h ** 3 / 12
    lam = (k_s * 1.0 / (4 * EI)) ** 0.25
    w.krok("Sztywność pasma", "E·I = (E_cm/2)·h³/12", "", EI, "kNm²", nd=0)
    w.krok("Charakterystyka belki na podłożu sprężystym", "λ = ⁴√(k_s·b/(4EI))", f"k_s = {f(k_s, 0)} kN/m³", lam, "1/m", nd=4)
    if krawedz:
        M = 0.3224 * P_d / lam
        wy = 2 * P_d * lam / k_s
        w.krok("Moment maksymalny (obciążenie na krawędzi)", "M = 0,3224·P/λ", f"0,3224·{f(P_d, 1)}/{f(lam, 4)}", M, "kNm/m")
    else:
        M = P_d / (4 * lam)
        wy = P_d * lam / (2 * k_s)
        w.krok("Moment pod obciążeniem", "M = P/(4λ)", f"{f(P_d, 1)}/(4·{f(lam, 4)})", M, "kNm/m")
    w.krok("Osiadanie lokalne / nacisk", "w; σ = k_s·w", "", f"{f(wy * 1000, 2)} mm; {f(k_s * wy, 1)} kPa")
    c = zelbet.otulina("XC2", 12, p, na_gruncie="podbeton").c_nom
    zg = zelbet.zginanie_prostokat(M, 1.0, h, h - c / 1000 - 0.008, beton, stal, nazwa="Zbrojenie pasma płyty (dół/góra)")
    w.dolacz(zg)
    return w


def k_podatnosci(q: float, s_mm: float) -> float:
    """Współczynnik podłoża Winklera k_s = q/s [kN/m³] z osiadania płyty (q [kPa], s [mm])."""
    return q / max(s_mm / 1000, 1e-6)
