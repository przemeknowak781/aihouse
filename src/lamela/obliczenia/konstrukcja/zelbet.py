"""Konstrukcje żelbetowe wg PN-EN 1992-1-1:2008 + NA (R5-50…R5-56, W-266…W-269).

Zakres: otulenie (4.4.1), zginanie przekroju prostokątnego i teowego (6.1, prostokątny wykres naprężeń 3.1.7(3)),
zbrojenie minimalne/maksymalne (9.2.1.1, 9.3.1.1, 7.3.2), ścinanie bez zbrojenia poprzecznego (6.2.2) i ze strzemionami
(6.2.3, metoda kratownicy o zmiennym nachyleniu krzyżulców), stan ugięć — metoda l/d (7.4.2) i obliczeniowa z
interpolacją ζ między stanem niezarysowanym i zarysowanym + pełzanie i skurcz (7.4.3), rysy — bez obliczeń bezpośrednich
(7.3.3, tabl. 7.2N/7.3N) i szerokość w_k (7.3.4), zakotwienie i zakłady (8.4, 8.7), wieńce/ściągi (9.10), belki-ściany
(model kratownicowy 5.6.4 + 6.5, zbrojenie minimalne 9.7), wsporniki płytowe (EQU), nadproża, zestawienie stali
(PN-EN ISO 3766 — kody kształtu, masy).

Jednostki argumentów: M [kNm], V [kN], wymiary [m]; wewnątrz przeliczane na N i mm. Wyniki A_s w [mm²] (belki) lub
[mm²/m] (płyty), podawane w raporcie w cm² lub cm²/m.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .materialy import Beton, StalZbrojeniowa, masa_preta, pole_preta
from .wspolne import BladDanych, Krok, Parametry, Wynik, f, tabela

# ==================================================================================================
# Otulenie (4.4.1)
# ==================================================================================================
_CMIN_DUR = {  # tabl. 4.4N — stal zbrojeniowa: X0, XC1, XC2/XC3, XC4, XD1/XS1, XD2/XS2, XD3/XS3
    "S1": (10, 10, 10, 15, 20, 25, 30), "S2": (10, 10, 15, 20, 25, 30, 35), "S3": (10, 10, 20, 25, 30, 35, 40),
    "S4": (10, 15, 25, 30, 35, 40, 45), "S5": (15, 20, 30, 35, 40, 45, 50), "S6": (20, 25, 35, 40, 45, 50, 55)}
_EXP_IDX = {"X0": 0, "XC1": 1, "XC2": 2, "XC3": 2, "XC4": 3, "XD1": 4, "XS1": 4, "XD2": 5, "XS2": 5, "XD3": 6, "XS3": 6}


@dataclass
class Otulina(Wynik):
    ekspozycja: str = "XC1"
    c_min_b: float = 0.0
    c_min_dur: float = 0.0
    c_min: float = 0.0
    c_nom: float = 0.0     # mm


def otulina(ekspozycja: str, fi: float, p: Parametry | None = None, plyta: bool = False, na_gruncie: str | None = None,
            fi_strzemion: float = 0.0) -> Otulina:
    """Otulenie nominalne c_nom = c_min + Δc_dev (4.1), c_min = max{c_min,b; c_min,dur; 10 mm} (4.2).

    ekspozycja — klasa (XC1…XD3; dla XC4+XF1 podać 'XC4'); fi — średnica pręta [mm]; plyta=True — redukcja klasy
    konstrukcji o 1 dla elementów o geometrii płyty (tabl. 4.3N) — domyślnie wyłączona (R5 3.6 przyjmuje S4);
    na_gruncie: 'podbeton' (k₁ = 40 mm) | 'grunt' (k₂ = 75 mm) — 4.4.1.3(4) [NZW]; fi_strzemion — otulenie liczone
    do prętów głównych przy strzemionach: c = max(c_nom(φ), c_nom(φ_s) + φ_s)."""
    p = p or Parametry()
    ex = ekspozycja.upper().replace("+XF1", "").replace(" ", "")
    if ex not in _EXP_IDX:
        raise BladDanych(f"klasa ekspozycji {ekspozycja}?")
    kl = p.klasa_konstrukcji
    if plyta:
        kl = f"S{max(int(kl[1]) - 1, 1)}"
    w = Otulina(nazwa=f"Otulenie zbrojenia ({ekspozycja}, φ{f(fi, 0)})", ekspozycja=ekspozycja)
    cdur = _CMIN_DUR[kl][_EXP_IDX[ex]]
    w.krok(f"Minimalne otulenie ze względu na trwałość (klasa konstrukcji {kl})", "c_min,dur", "", cdur, "mm", nd=0,
           zrodlo="tabl. 4.4N")
    cb = fi
    w.krok("Minimalne otulenie ze względu na przyczepność", "c_min,b = φ", "", cb, "mm", nd=0, zrodlo="tabl. 4.2")
    cmin = max(cb, cdur, 10.0)
    w.krok("Otulenie minimalne", "c_min = max{c_min,b; c_min,dur; 10 mm}", f"max{{{f(cb, 0)}; {f(cdur, 0)}; 10}}", cmin,
           "mm", nd=0, zrodlo="(4.2)")
    cnom = cmin + p.dc_dev
    w.krok("Otulenie nominalne", "c_nom = c_min + Δc_dev", f"{f(cmin, 0)} + {f(p.dc_dev, 0)}", cnom, "mm", nd=0,
           zrodlo="(4.1), 4.4.1.3 (Δc_dev = 10 mm)")
    if fi_strzemion:
        cs = max(fi_strzemion, cdur, 10.0) + p.dc_dev
        c2 = cs + fi_strzemion
        if c2 > cnom:
            w.krok("Otulenie prętów głównych przy strzemionach", "c = c_nom(φ_s) + φ_s", f"{f(cs, 0)} + {f(fi_strzemion, 0)}",
                   c2, "mm", nd=0)
            cnom = c2
    if na_gruncie:
        k = 40.0 if na_gruncie == "podbeton" else 75.0
        if k > cnom:
            w.krok("Betonowanie na podłożu", "c_nom ≥ k₁ (podbeton) / k₂ (grunt)", "", k, "mm", nd=0,
                   zrodlo="4.4.1.3(4) [NZW]")
            cnom = k
    w.c_min_b, w.c_min_dur, w.c_min, w.c_nom = cb, cdur, cmin, cnom
    return w


# ==================================================================================================
# Zginanie
# ==================================================================================================
@dataclass
class Zginanie(Wynik):
    M_Ed: float = 0.0
    b: float = 0.0            # mm
    h: float = 0.0
    d: float = 0.0
    mu: float = 0.0
    xi_eff: float = 0.0
    xi_lim: float = 0.0
    z: float = 0.0            # mm
    As_req: float = 0.0       # mm² (belka) lub mm²/m (płyta, b = 1000)
    As2_req: float = 0.0
    As_min: float = 0.0
    As_max: float = 0.0
    As_prov: float = 0.0
    zbrojenie: str = ""
    M_Rd: float = 0.0


def zginanie_prostokat(M_Ed: float, b: float, h: float, d: float, beton: Beton, stal: StalZbrojeniowa | None = None,
                       d2: float | None = None, nazwa: str = "Zginanie", element: str = "belka") -> Zginanie:
    """Wymiarowanie przekroju prostokątnego zginanego (prostokątny wykres naprężeń, λ = 0,8, η = 1,0 — 3.1.7(3)).

    μ = M_Ed/(b·d²·η·f_cd); ξ_eff = 1 − √(1 − 2μ); A_s1 = ξ_eff·b·d·η·f_cd/f_yd; gdy ξ_eff > ξ_eff,lim — zbrojenie
    ściskane A_s2 = (M_Ed − M_lim)/(f_yd·(d − d₂)). A_s,min = max(0,26·f_ctm/f_yk·b·d; 0,0013·b·d) (9.1N),
    A_s,max = 0,04·A_c (9.2.1.1(3)). b, h, d, d2 w [m]; M_Ed w [kNm] (dla płyt: na 1 m szerokości, b = 1,0)."""
    stal = stal or StalZbrojeniowa()
    bm, hm, dm = b * 1000, h * 1000, d * 1000
    fcd, fyd = beton.f_cd, stal.f_yd
    M = abs(M_Ed) * 1e6
    w = Zginanie(nazwa=nazwa, M_Ed=abs(M_Ed), b=bm, h=hm, d=dm)
    w.krok("Wysokość użyteczna", "d", "", dm, "mm", nd=0)
    mu = M / (bm * dm ** 2 * beton.eta * fcd)
    w.krok("Moment względny", "μ = M_Ed/(b·d²·η·f_cd)", f"{f(abs(M_Ed), 2)}·10⁶/({f(bm, 0)}·{f(dm, 0)}²·{f(beton.eta, 1)}·{f(fcd, 2)})",
           mu, nd=4, zrodlo="3.1.7(3)")
    xl = stal.xi_eff_lim(beton)
    mul = xl * (1 - 0.5 * xl)
    w.xi_lim = xl
    if mu <= 1e-12:
        w.krok("Moment pomijalny", "A_s1", "", 0.0, "mm²")
        xi = 0.0
        As1 = As2 = 0.0
    elif mu <= mul:
        xi = 1 - math.sqrt(1 - 2 * mu)
        w.krok("Względna wysokość strefy ściskanej", "ξ_eff = 1 − √(1 − 2μ)", f"1 − √(1 − 2·{f(mu, 4)})", xi, nd=4)
        w.krok("Warunek ciągliwości", "ξ_eff ≤ ξ_eff,lim = λ·ε_cu3/(ε_cu3 + f_yd/E_s)", f"{f(xi, 3)} ≤ {f(xl, 3)}", "spełniony")
        As1 = xi * bm * dm * beton.eta * fcd / fyd
        As2 = 0.0
        w.krok("Wymagane zbrojenie rozciągane", "A_s1 = ξ_eff·b·d·η·f_cd/f_yd",
               f"{f(xi, 4)}·{f(bm, 0)}·{f(dm, 0)}·{f(beton.eta, 1)}·{f(fcd, 2)}/{f(fyd, 1)}", As1, "mm²", nd=0)
    else:
        if d2 is None:
            d2 = 0.05
        d2m = d2 * 1000
        xi = xl
        Mlim = mul * bm * dm ** 2 * beton.eta * fcd
        As2 = (M - Mlim) / (fyd * (dm - d2m))
        As1 = xl * bm * dm * beton.eta * fcd / fyd + As2
        w.krok("μ > μ_lim — przekrój podwójnie zbrojony", "μ_lim = ξ_lim·(1 − 0,5·ξ_lim)", f"{f(xl, 3)}·(1 − 0,5·{f(xl, 3)})",
               mul, nd=4)
        w.krok("Zbrojenie ściskane", "A_s2 = (M_Ed − M_lim)/(f_yd·(d − d₂))",
               f"({f(M / 1e6, 2)} − {f(Mlim / 1e6, 2)})·10⁶/({f(fyd, 1)}·({f(dm, 0)} − {f(d2m, 0)}))", As2, "mm²", nd=0)
        w.krok("Zbrojenie rozciągane", "A_s1 = ξ_lim·b·d·η·f_cd/f_yd + A_s2", "", As1, "mm²", nd=0)
        w.uwaga("Przekrój podwójnie zbrojony — zalecane zwiększenie wysokości przekroju.")
    z = dm * (1 - 0.5 * xi) if xi > 0 else 0.9 * dm
    Asmin = max(0.26 * beton.f_ctm / stal.f_yk * bm * dm, 0.0013 * bm * dm)
    w.krok("Zbrojenie minimalne", "A_s,min = max(0,26·f_ctm/f_yk·b·d; 0,0013·b·d)",
           f"max(0,26·{f(beton.f_ctm, 1)}/{f(stal.f_yk, 0)}·{f(bm, 0)}·{f(dm, 0)}; 0,0013·{f(bm, 0)}·{f(dm, 0)})", Asmin, "mm²",
           nd=0, zrodlo="(9.1N) + NA")
    Asmax = 0.04 * bm * hm
    w.mu, w.xi_eff, w.z, w.As_req, w.As2_req, w.As_min, w.As_max = mu, xi, z, As1, As2, Asmin, Asmax
    return w


def nosnosc_zginanie(As: float, b: float, d: float, beton: Beton, stal: StalZbrojeniowa | None = None) -> tuple[float, float]:
    """M_Rd [kNm] i ξ_eff dla przekroju prostokątnego pojedynczo zbrojonego (A_s [mm²], b, d [m])."""
    stal = stal or StalZbrojeniowa()
    bm, dm = b * 1000, d * 1000
    x_eff = As * stal.f_yd / (bm * beton.eta * beton.f_cd)
    xi = x_eff / dm
    xl = stal.xi_eff_lim(beton)
    if xi > xl:
        x_eff = xl * dm
    MRd = min(As * stal.f_yd, bm * beton.eta * beton.f_cd * x_eff) * (dm - 0.5 * x_eff) / 1e6
    return MRd, xi


def zginanie_teowy(M_Ed: float, b_eff: float, b_w: float, h: float, h_f: float, d: float, beton: Beton,
                   stal: StalZbrojeniowa | None = None, nazwa: str = "Zginanie (przekrój teowy)") -> Zginanie:
    """Przekrój teowy (płyta w strefie ściskanej): gdy x_eff ≤ h_f — jak prostokąt b_eff; w przeciwnym razie
    rozkład na półki i środnik (3.1.7(3))."""
    stal = stal or StalZbrojeniowa()
    w = zginanie_prostokat(M_Ed, b_eff, h, d, beton, stal, nazwa=nazwa)
    if w.xi_eff * w.d <= h_f * 1000 + 1e-9:
        w.krok("Strefa ściskana w półce", "x_eff = ξ_eff·d ≤ h_f", f"{f(w.xi_eff * w.d, 0)} ≤ {f(h_f * 1000, 0)}", "przekrój pozornie teowy")
        w.As_min = max(0.26 * beton.f_ctm / stal.f_yk * b_w * 1000 * w.d, 0.0013 * b_w * 1000 * w.d)
        return w
    fcd = beton.f_cd
    Mf = (b_eff - b_w) * 1000 * h_f * 1000 * fcd * (w.d - h_f * 500) / 1e6
    Asf = (b_eff - b_w) * 1000 * h_f * 1000 * fcd / stal.f_yd
    w2 = zginanie_prostokat(M_Ed - Mf, b_w, h, d, beton, stal, nazwa=nazwa)
    w2.krok("Przekrój rzeczywiście teowy: udział półek", "M_f = (b_eff − b_w)·h_f·f_cd·(d − h_f/2)", "", Mf, "kNm")
    w2.As_req += Asf
    w2.krok("Zbrojenie łączne", "A_s1 = A_s,f + A_s,w", "", w2.As_req, "mm²", nd=0)
    return w2


# ==================================================================================================
# Dobór prętów
# ==================================================================================================
def dobierz_plyta(As_req: float, s_max: float, fi_min: int = 8, fi_max: int = 16, s_min: float = 100.0,
                  As_min: float = 0.0) -> tuple[int, float, float]:
    """Dobór siatki płyty: (φ [mm], s [mm], A_s,prov [mm²/m]) — najmniejsza masa przy A_s,prov ≥ max(A_s,req, A_s,min),
    s ≤ s_max, rozstaw co 10 mm (≥ s_min; w razie potrzeby do 75 mm)."""
    need = max(As_req, As_min, 1e-9)
    best = None
    for fi in (8, 10, 12, 14, 16, 20):
        if fi < fi_min or fi > fi_max:
            continue
        a = pole_preta(fi)
        for s in range(int(s_max // 10 * 10), 70, -10):
            if s < s_min and best is not None:
                break
            As = a * 1000 / s
            if As >= need:
                cand = (As, -fi, s, fi)
                if best is None or cand < best:
                    best = cand
                break
    if best is None:
        fi = fi_max
        s = 75.0
        return fi, s, pole_preta(fi) * 1000 / s
    As, _, s, fi = best
    return fi, float(s), As


def dobierz_belka(As_req: float, b_w: float, c_nom: float, fi_s: float = 8, d_g: float = 16,
                  srednice=(12, 14, 16, 20, 25), n_min: int = 2) -> tuple[int, int, int, float]:
    """Dobór prętów belki: (n, φ, liczba warstw, A_s,prov [mm²]); rozstaw w świetle ≥ max(φ; d_g + 5; 20 mm) (8.2)."""
    best = None
    for fi in srednice:
        a = pole_preta(fi)
        n = max(n_min, int(math.ceil(As_req / a - 1e-9)))
        smin = max(fi, d_g + 5, 20)
        n_row = max(int((b_w * 1000 - 2 * (c_nom) - 2 * fi_s + smin) // (fi + smin)), 2)
        rows = int(math.ceil(n / n_row))
        if rows > 2:
            continue
        cand = (n * a, rows, fi, n)
        if best is None or cand < best:
            best = cand
    if best is None:
        fi = srednice[-1]
        n = int(math.ceil(As_req / pole_preta(fi)))
        return n, fi, 3, n * pole_preta(fi)
    As, rows, fi, n = best
    return n, fi, rows, As


def smax_plyta(h: float, glowne: bool = True, strefa_max: bool = True) -> float:
    """Maks. rozstaw prętów płyty [mm] (9.3.1.1(3)): główne 3h ≤ 400 (w strefie M_max: 2h ≤ 250); rozdzielcze 3,5h ≤ 450
    (w strefie M_max: 3h ≤ 400)."""
    hm = h * 1000
    if glowne:
        return min(2 * hm, 250.0) if strefa_max else min(3 * hm, 400.0)
    return min(3 * hm, 400.0) if strefa_max else min(3.5 * hm, 450.0)


# ==================================================================================================
# Ścinanie
# ==================================================================================================
@dataclass
class Scinanie(Wynik):
    V_Ed: float = 0.0
    V_Rd_c: float = 0.0
    V_Rd_s: float = 0.0
    V_Rd_max: float = 0.0
    cot_theta: float = 0.0
    strzemiona: str = ""
    s: float = 0.0


def scinanie_bez_zbrojenia(V_Ed: float, b_w: float, d: float, As_l: float, beton: Beton, sigma_cp: float = 0.0,
                           nazwa: str = "Ścinanie — element bez zbrojenia na ścinanie") -> Scinanie:
    """V_Rd,c = [C_Rd,c·k·(100·ρ_l·f_ck)^(1/3) + k₁·σ_cp]·b_w·d ≥ (v_min + k₁·σ_cp)·b_w·d (6.2), C_Rd,c = 0,18/γ_c,
    k = 1 + √(200/d) ≤ 2,0, ρ_l = A_sl/(b_w·d) ≤ 0,02, v_min = 0,035·k^(3/2)·f_ck^(1/2) (6.3N), k₁ = 0,15.
    V_Ed [kN], b_w, d [m], A_sl [mm²] (dla płyt — na b_w = 1 m)."""
    bw, dm = b_w * 1000, d * 1000
    w = Scinanie(nazwa=nazwa, V_Ed=abs(V_Ed))
    C = 0.18 / beton.gamma_c
    k = min(1 + math.sqrt(200 / dm), 2.0)
    rho = min(As_l / (bw * dm), 0.02)
    w.krok("Współczynnik skali", "k = 1 + √(200/d) ≤ 2,0", f"1 + √(200/{f(dm, 0)})", k, nd=3)
    w.krok("Stopień zbrojenia podłużnego", "ρ_l = A_sl/(b_w·d) ≤ 0,02", f"{f(As_l, 0)}/({f(bw, 0)}·{f(dm, 0)})", rho, nd=5)
    vmin = 0.035 * k ** 1.5 * math.sqrt(beton.f_ck)
    v = C * k * (100 * rho * beton.f_ck) ** (1 / 3) + 0.15 * sigma_cp
    VRdc = max(v, vmin + 0.15 * sigma_cp) * bw * dm / 1000
    w.krok("Nośność na ścinanie", "V_Rd,c = C_Rd,c·k·(100·ρ_l·f_ck)^(1/3)·b_w·d",
           f"{f(C, 4)}·{f(k, 3)}·(100·{f(rho, 5)}·{f(beton.f_ck, 0)})^(1/3)·{f(bw, 0)}·{f(dm, 0)}·10⁻³", v * bw * dm / 1000, "kN",
           zrodlo="(6.2.a); C_Rd,c = 0,18/γ_c")
    w.krok("Wartość minimalna", "V_Rd,c,min = v_min·b_w·d, v_min = 0,035·k^(3/2)·f_ck^(1/2)",
           f"{f(vmin, 4)}·{f(bw, 0)}·{f(dm, 0)}·10⁻³", vmin * bw * dm / 1000, "kN", zrodlo="(6.2.b), (6.3N)")
    w.V_Rd_c = VRdc
    w.warunek("Ścinanie bez zbrojenia poprzecznego (6.2.2)", abs(V_Ed), VRdc, "kN", "PN-EN 1992-1-1 6.2.2",
              symbol_E="V_Ed", symbol_R="V_Rd,c")
    return w


def scinanie_strzemiona(V_Ed: float, b_w: float, d: float, As_l: float, beton: Beton, stal: StalZbrojeniowa | None = None,
                        fi_s: int = 8, n_ramion: int = 2, nazwa: str = "Ścinanie — strzemiona pionowe") -> Scinanie:
    """Zbrojenie na ścinanie (6.2.3): z = 0,9d; V_Rd,max = α_cw·b_w·z·ν₁·f_cd/(cot θ + tan θ) (6.9), 1 ≤ cot θ ≤ 2
    (NA); V_Rd,s = A_sw/s·z·f_ywd·cot θ (6.8); ρ_w,min = 0,08·√f_ck/f_yk (9.5N); s_l,max = 0,75·d (9.6N)."""
    stal = stal or StalZbrojeniowa()
    w = scinanie_bez_zbrojenia(V_Ed, b_w, d, As_l, beton, nazwa=nazwa)
    VRdc = w.V_Rd_c
    w.warunki.clear()
    bw, dm = b_w * 1000, d * 1000
    z = 0.9 * dm
    nu1 = beton.nu_1
    fcd = beton.f_cd
    fywd = stal.f_yd

    def vmax(ct):
        return bw * z * nu1 * fcd / (ct + 1 / ct) / 1000
    ct = 2.0
    while ct > 1.0 and vmax(ct) < abs(V_Ed):
        ct -= 0.05
    ct = max(ct, 1.0)
    VRdmax = vmax(ct)
    w.krok("Ramię sił wewnętrznych", "z = 0,9·d", f"0,9·{f(dm, 0)}", z, "mm", nd=0)
    w.krok("Przyjęto nachylenie krzyżulców betonowych", "cot θ", "(1,0 ≤ cot θ ≤ 2,0 — NA)", ct, nd=2, zrodlo="(6.7N)")
    w.krok("Nośność krzyżulców ściskanych", "V_Rd,max = b_w·z·ν₁·f_cd/(cot θ + tan θ)",
           f"{f(bw, 0)}·{f(z, 0)}·{f(nu1, 3)}·{f(fcd, 2)}/({f(ct, 2)} + {f(1 / ct, 3)})·10⁻³", VRdmax, "kN", zrodlo="(6.9), ν₁ = ν (6.6N)")
    Asw = n_ramion * pole_preta(fi_s)
    s_req = Asw * z * fywd * ct / (abs(V_Ed) * 1000) if abs(V_Ed) > 0 else 1e9
    s_lmax = 0.75 * dm
    rho_min = 0.08 * math.sqrt(beton.f_ck) / stal.f_yk
    s_rho = Asw / (rho_min * bw)
    s = min(s_req, s_lmax, s_rho, 400.0)
    s = max(math.floor(s / 10) * 10, 50.0)
    w.krok("Rozstaw z warunku nośności", "s = A_sw·z·f_ywd·cot θ/V_Ed",
           f"{f(Asw, 1)}·{f(z, 0)}·{f(fywd, 1)}·{f(ct, 2)}/({f(abs(V_Ed), 2)}·10³)", s_req, "mm", nd=0, zrodlo="(6.8)")
    w.krok("Rozstaw maksymalny", "s_l,max = 0,75·d", f"0,75·{f(dm, 0)}", s_lmax, "mm", nd=0, zrodlo="(9.6N)")
    w.krok("Stopień zbrojenia minimalny", "ρ_w,min = 0,08·√f_ck/f_yk → s ≤ A_sw/(ρ_w,min·b_w)",
           f"{f(Asw, 1)}/({f(rho_min, 5)}·{f(bw, 0)})", s_rho, "mm", nd=0, zrodlo="(9.5N)")
    VRds = Asw / s * z * fywd * ct / 1000
    w.krok("Przyjęto strzemiona", f"φ{fi_s} {n_ramion}-cięte co s", "", s, "mm", nd=0)
    w.krok("Nośność zbrojenia na ścinanie", "V_Rd,s = A_sw/s·z·f_ywd·cot θ",
           f"{f(Asw, 1)}/{f(s, 0)}·{f(z, 0)}·{f(fywd, 1)}·{f(ct, 2)}·10⁻³", VRds, "kN")
    w.V_Rd_s, w.V_Rd_max, w.cot_theta, w.s = VRds, VRdmax, ct, s
    w.strzemiona = f"φ{fi_s} co {f(s / 10, 0)} cm ({n_ramion}-cięte)"
    w.warunek("Nośność krzyżulców betonowych", abs(V_Ed), VRdmax, "kN", "(6.9)", symbol_E="V_Ed", symbol_R="V_Rd,max")
    w.warunek("Nośność strzemion", abs(V_Ed), max(VRds, VRdc), "kN", "(6.8)", symbol_E="V_Ed", symbol_R="V_Rd,s")
    if abs(V_Ed) <= VRdc:
        w.uwaga(f"V_Ed ≤ V_Rd,c = {f(VRdc)} kN — zbrojenie poprzeczne minimalne (9.2.2(5)).")
    return w


# ==================================================================================================
# Ugięcia
# ==================================================================================================
@dataclass
class Ugiecie(Wynik):
    l_d_dop: float = 0.0
    l_d_rzecz: float = 0.0
    w: float = 0.0            # mm
    w_dop: float = 0.0        # mm


def ugiecie_ld(l_eff: float, d: float, As_req: float, As_prov: float, b: float, beton: Beton, K: float = 1.0,
               As2: float = 0.0, stal: StalZbrojeniowa | None = None, teowy: bool = False, plaska: bool = False,
               nazwa: str = "Ugięcie — sprawdzenie uproszczone l/d") -> Ugiecie:
    """Graniczna smukłość l/d (7.4.2, wzory 7.16a/b): ρ₀ = √f_ck·10⁻³;
    ρ ≤ ρ₀: l/d = K·[11 + 1,5·√f_ck·ρ₀/ρ + 3,2·√f_ck·(ρ₀/ρ − 1)^(3/2)],
    ρ > ρ₀: l/d = K·[11 + 1,5·√f_ck·ρ₀/(ρ − ρ') + 1/12·√f_ck·√(ρ'/ρ₀)];
    mnożniki: 310/σ_s ≈ 500/(f_yk·A_s,req/A_s,prov) ≤ 1,5 (7.17, ograniczenie [UPR]), teowy b_eff/b_w > 3 → 0,8,
    l_eff > 7 m → 7/l_eff (nie dla płyt płaskich). K — tabl. 7.4N (1,0 / 1,3 / 1,5 / 1,2 / 0,4)."""
    stal = stal or StalZbrojeniowa()
    w = Ugiecie(nazwa=nazwa)
    fck = beton.f_ck
    rho0 = math.sqrt(fck) * 1e-3
    bm, dm = b * 1000, d * 1000
    rho = max(As_req / (bm * dm), 1e-6)
    rhop = As2 / (bm * dm)
    w.krok("Stopień zbrojenia wymagany", "ρ = A_s,req/(b·d)", f"{f(As_req, 0)}/({f(bm, 0)}·{f(dm, 0)})", rho, nd=5)
    w.krok("Wartość odniesienia", "ρ₀ = √f_ck·10⁻³", f"√{f(fck, 0)}·10⁻³", rho0, nd=5)
    if rho <= rho0:
        ld = K * (11 + 1.5 * math.sqrt(fck) * rho0 / rho + 3.2 * math.sqrt(fck) * (rho0 / rho - 1) ** 1.5)
        w.krok("Graniczne l/d (ρ ≤ ρ₀)", "K·[11 + 1,5·√f_ck·ρ₀/ρ + 3,2·√f_ck·(ρ₀/ρ − 1)^(3/2)]",
               f"{f(K, 1)}·[11 + 1,5·{f(math.sqrt(fck), 3)}·{f(rho0 / rho, 3)} + 3,2·{f(math.sqrt(fck), 3)}·({f(rho0 / rho, 3)} − 1)^1,5]",
               ld, nd=1, zrodlo="(7.16a)")
    else:
        ld = K * (11 + 1.5 * math.sqrt(fck) * rho0 / max(rho - rhop, 1e-9) + math.sqrt(fck) / 12 * math.sqrt(rhop / rho0))
        w.krok("Graniczne l/d (ρ > ρ₀)", "K·[11 + 1,5·√f_ck·ρ₀/(ρ − ρ') + 1/12·√f_ck·√(ρ'/ρ₀)]", "", ld, nd=1,
               zrodlo="(7.16b)")
    k_s = min(500.0 / (stal.f_yk * As_req / max(As_prov, 1e-9)), 1.5) if As_prov > 0 else 1.0
    w.krok("Mnożnik od naprężeń w stali", "310/σ_s ≈ 500/(f_yk·A_s,req/A_s,prov) ≤ 1,5",
           f"500/({f(stal.f_yk, 0)}·{f(As_req, 0)}/{f(As_prov, 0)})", k_s, nd=3, zrodlo="(7.17)")
    ld *= k_s
    if teowy:
        ld *= 0.8
        w.krok("Przekrój teowy b_eff/b_w > 3", "× 0,8", "", 0.8)
    if l_eff > 7.0 and not plaska:
        ld *= 7.0 / l_eff
        w.krok("Rozpiętość > 7 m", "× 7/l_eff", f"7/{f(l_eff)}", 7.0 / l_eff, nd=3, zrodlo="7.4.2(2)")
    rz = l_eff / d
    w.krok("Smukłość rzeczywista", "l_eff/d", f"{f(l_eff, 2)}/{f(d, 3)}", rz, nd=1)
    w.l_d_dop, w.l_d_rzecz = ld, rz
    w.warunek("Ugięcie — graniczna smukłość l/d (7.4.2)", rz, ld, "", "(7.16), tabl. 7.4N", nd=1, symbol_E="l/d",
              symbol_R="(l/d)_lim")
    return w


def przekroj_niezarysowany(b: float, h: float, d: float, As: float, As2: float, d2: float, alfa_e: float) -> tuple[float, float]:
    """(x_I [mm], I_I [mm⁴]) — przekrój sprowadzony niezarysowany (b, h, d, d2 [mm]; A_s [mm²])."""
    A = b * h + alfa_e * (As + As2)
    S = b * h * h / 2 + alfa_e * (As * d + As2 * d2)
    x = S / A
    I = b * h ** 3 / 12 + b * h * (h / 2 - x) ** 2 + alfa_e * (As * (d - x) ** 2 + As2 * (x - d2) ** 2)
    return x, I


def przekroj_zarysowany(b: float, d: float, As: float, As2: float, d2: float, alfa_e: float) -> tuple[float, float]:
    """(x_II [mm], I_II [mm⁴]) — przekrój zarysowany (beton rozciągany pominięty, liniowo-sprężysty)."""
    a = b / 2
    bb = alfa_e * (As + As2)
    c = -alfa_e * (As * d + As2 * d2)
    x = (-bb + math.sqrt(bb * bb - 4 * a * c)) / (2 * a)
    I = b * x ** 3 / 3 + alfa_e * (As * (d - x) ** 2 + As2 * (x - d2) ** 2)
    return x, I


def ugiecie_obliczeniowe(M_qp: float, w_EI1: float, l: float, b: float, h: float, d: float, As: float, beton: Beton,
                         p: Parametry | None = None, As2: float = 0.0, d2: float = 0.04, k_skurcz: float = 0.125,
                         w_lim_mian: float | None = None, L_ref: float | None = None,
                         nazwa: str = "Ugięcie — metoda obliczeniowa (7.4.3)") -> Ugiecie:
    """Ugięcie długotrwałe z uwzględnieniem zarysowania, pełzania i skurczu (7.4.3):
    E_c,eff = E_cm/(1 + φ(∞,t₀)) (7.20); α = ζ·α_II + (1 − ζ)·α_I (7.18); ζ = 1 − β·(M_cr/M)² (7.19), β = 0,5;
    krzywizna skurczowa 1/r_cs = ε_cs·α_e·S/I (7.21). w_EI1 — ugięcie sprężyste od kombinacji quasi-stałej przy EI = 1 kNm²
    (z analizy statycznej, np. MES); M_qp — moment quasi-stały w przekroju miarodajnym [kNm]; l — rozpiętość [m];
    k_skurcz — współczynnik ugięcia od krzywizny stałej (1/8 — belka swobodnie podparta, 1/2 — wspornik);
    L_ref — długość odniesienia limitu (np. 2·wysięg dla wspornika)."""
    p = p or Parametry()
    w = Ugiecie(nazwa=nazwa)
    bm, hm, dm, d2m = b * 1000, h * 1000, d * 1000, d2 * 1000
    Eeff = beton.E_cm / (1 + p.fi_pelzania)
    ae = p.E_s / Eeff
    w.krok("Efektywny moduł sprężystości", "E_c,eff = E_cm/(1 + φ)", f"{f(beton.E_cm, 0)}/(1 + {f(p.fi_pelzania, 1)})", Eeff,
           "MPa", nd=0, zrodlo="(7.20)")
    w.krok("Stosunek modułów", "α_e = E_s/E_c,eff", f"{f(p.E_s, 0)}/{f(Eeff, 0)}", ae, nd=2)
    xI, II = przekroj_niezarysowany(bm, hm, dm, As, As2, d2m, ae)
    xII, III = przekroj_zarysowany(bm, dm, As, As2, d2m, ae)
    w.krok("Przekrój niezarysowany", "x_I; I_I", "", f"{f(xI, 1)} mm; {f(II / 1e6, 1)}·10⁶ mm⁴")
    w.krok("Przekrój zarysowany", "x_II; I_II", "", f"{f(xII, 1)} mm; {f(III / 1e6, 1)}·10⁶ mm⁴")
    Mcr = beton.f_ctm * II / (hm - xI) / 1e6
    w.krok("Moment rysujący", "M_cr = f_ctm·I_I/(h − x_I)", f"{f(beton.f_ctm, 1)}·{f(II / 1e6, 1)}·10⁶/({f(hm, 0)} − {f(xI, 1)})",
           Mcr, "kNm")
    Mq = abs(M_qp)
    zeta = 0.0 if Mq <= Mcr else 1 - 0.5 * (Mcr / Mq) ** 2
    w.krok("Współczynnik rozkładu", "ζ = 1 − β·(M_cr/M_qp)², β = 0,5", f"1 − 0,5·({f(Mcr, 2)}/{f(Mq, 2)})²" if Mq > Mcr else "M_qp ≤ M_cr → 0",
           zeta, nd=3, zrodlo="(7.19)")
    # ugięcie od obciążeń
    EI_I = Eeff * II * 1e-9            # kNm²
    EI_II = Eeff * III * 1e-9
    wI, wII = w_EI1 / EI_I * 1000, w_EI1 / EI_II * 1000   # mm
    wl = zeta * wII + (1 - zeta) * wI
    w.krok("Ugięcie od obciążeń (quasi-stała)", "w_q = ζ·w_II + (1 − ζ)·w_I", f"{f(zeta, 3)}·{f(wII, 2)} + {f(1 - zeta, 3)}·{f(wI, 2)}",
           wl, "mm", nd=2, zrodlo="(7.18)")
    # skurcz
    S_I = As * (dm - xI) - As2 * (xI - d2m)
    S_II = As * (dm - xII) - As2 * (xII - d2m)
    kI = p.eps_cs * ae * S_I / II
    kII = p.eps_cs * ae * S_II / III
    kcs = zeta * kII + (1 - zeta) * kI          # 1/mm
    wcs = k_skurcz * kcs * (l * 1000) ** 2
    w.krok("Ugięcie od skurczu", "w_cs = k·(1/r_cs)·l², 1/r_cs = ε_cs·α_e·S/I",
           f"{f(k_skurcz, 3)}·{f(kcs * 1e6, 3)}·10⁻⁶·{f(l * 1000, 0)}²", wcs, "mm", nd=2, zrodlo="(7.21)")
    wt = wl + wcs
    Lr = L_ref if L_ref is not None else l
    mian = w_lim_mian or p.ugiecie_mian
    wdop = Lr * 1000 / mian
    w.krok("Ugięcie całkowite", "w = w_q + w_cs", f"{f(wl, 2)} + {f(wcs, 2)}", wt, "mm", nd=2)
    w.krok("Ugięcie dopuszczalne", f"w_lim = L/{f(mian, 0)}", f"{f(Lr * 1000, 0)}/{f(mian, 0)}", wdop, "mm", nd=1,
           zrodlo="7.4.1(4)")
    w.w, w.w_dop = wt, wdop
    w.warunek("Ugięcie długotrwałe (quasi-stała) ≤ L/250", wt, wdop, "mm", "7.4.1(4), 7.4.3", nd=1, symbol_E="w",
              symbol_R="w_lim")
    return w


# ==================================================================================================
# Rysy
# ==================================================================================================
_T72N = [(160, 40, 32, 25), (200, 32, 25, 16), (240, 20, 16, 12), (280, 16, 12, 8), (320, 12, 10, 6), (360, 10, 8, 5),
         (400, 8, 6, 4), (450, 6, 5, 0)]
_T73N = [(160, 300, 300, 200), (200, 300, 250, 150), (240, 250, 200, 100), (280, 200, 150, 50), (320, 150, 100, 0),
         (360, 100, 50, 0)]


def _interp_tab_rys(tab, sigma, wmax):
    col = {0.4: 1, 0.3: 2, 0.2: 3}.get(round(wmax, 1), 2)
    xs = [r[0] for r in tab]
    ys = [r[col] for r in tab]
    if sigma <= xs[0]:
        return ys[0]
    if sigma >= xs[-1]:
        return ys[-1] if sigma == xs[-1] else 0.0
    return float(np.interp(sigma, xs, ys))


@dataclass
class Rysy(Wynik):
    sigma_s: float = 0.0
    w_k: float = 0.0
    fi_max: float = 0.0
    s_max: float = 0.0


def naprezenie_stali(M: float, b: float, d: float, As: float, alfa_e: float = 15.0, As2: float = 0.0, d2: float = 0.04) -> float:
    """σ_s [MPa] w przekroju zarysowanym (b, d [m], A_s [mm²], M [kNm]); α_e ≈ 15 (obciążenia długotrwałe)."""
    x, I = przekroj_zarysowany(b * 1000, d * 1000, As, As2, d2 * 1000, alfa_e)
    return alfa_e * abs(M) * 1e6 * (d * 1000 - x) / I


def rysy_bez_obliczen(M_qp: float, b: float, h: float, d: float, As: float, fi: float, s: float, beton: Beton,
                      w_max: float = 0.4, nazwa: str = "Rysy — sprawdzenie bez obliczeń bezpośrednich (7.3.3)",
                      k_c: float = 0.4) -> Rysy:
    """σ_s z kombinacji quasi-stałej (przekrój zarysowany, α_e = 15), tabl. 7.2N (φ*_s) z poprawką (7.6N):
    φ_s = φ*_s·(f_ct,eff/2,9)·k_c·h_cr/(2(h − d)) oraz tabl. 7.3N (rozstaw) — wystarczy jeden z warunków (7.3.3(2))."""
    w = Rysy(nazwa=nazwa)
    sig = naprezenie_stali(M_qp, b, d, As)
    w.krok("Naprężenie w stali (quasi-stała, przekrój zarysowany, α_e = 15)", "σ_s = α_e·M_qp·(d − x_II)/I_II", "", sig, "MPa", nd=0)
    fi_star = _interp_tab_rys(_T72N, sig, w_max)
    hcr = h / 2 * 1000
    fi_lim = fi_star * (beton.f_ctm / 2.9) * k_c * hcr / (2 * (h - d) * 1000) if fi_star > 0 else 0.0
    w.krok(f"Maksymalna średnica (w_max = {f(w_max, 1)} mm)", "φ_s = φ*_s·(f_ct,eff/2,9)·k_c·h_cr/(2(h − d))",
           f"{f(fi_star, 1)}·({f(beton.f_ctm, 1)}/2,9)·{f(k_c, 1)}·{f(hcr, 0)}/(2·{f((h - d) * 1000, 0)})", fi_lim, "mm", nd=1,
           zrodlo="tabl. 7.2N, (7.6N)")
    smax = _interp_tab_rys(_T73N, sig, w_max)
    w.krok("Maksymalny rozstaw prętów", "s_max", f"(σ_s = {f(sig, 0)} MPa)", smax, "mm", nd=0, zrodlo="tabl. 7.3N")
    ok_fi = fi <= fi_lim + 1e-9
    ok_s = s <= smax + 1e-9
    w.sigma_s, w.fi_max, w.s_max = sig, fi_lim, smax
    # jeden z warunków wystarcza — do tabeli warunków wpisujemy korzystniejszy
    if ok_fi or not ok_s:
        w.warunek("Rysy: średnica prętów (tabl. 7.2N)", fi, max(fi_lim, 1e-6), "mm", "7.3.3(2)", nd=0, symbol_E="φ",
                  symbol_R="φ_s,max")
    else:
        w.warunek("Rysy: rozstaw prętów (tabl. 7.3N)", s, max(smax, 1e-6), "mm", "7.3.3(2)", nd=0, symbol_E="s",
                  symbol_R="s_max")
    return w


def rysy_wk(M_qp: float, b: float, h: float, d: float, As: float, fi: float, c: float, beton: Beton,
            p: Parametry | None = None, w_max: float = 0.4, nazwa: str = "Rysy — szerokość rys w_k (7.3.4)") -> Rysy:
    """w_k = s_r,max·(ε_sm − ε_cm) (7.8); ε_sm − ε_cm = [σ_s − k_t·f_ct,eff/ρ_p,eff·(1 + α_e·ρ_p,eff)]/E_s ≥ 0,6·σ_s/E_s (7.9);
    s_r,max = k₃·c + k₁·k₂·k₄·φ/ρ_p,eff (7.11), k₁ = 0,8, k₂ = 0,5, k₃ = 3,4, k₄ = 0,425; h_c,ef = min(2,5(h−d); (h−x)/3; h/2)."""
    p = p or Parametry()
    w = Rysy(nazwa=nazwa)
    bm, hm, dm = b * 1000, h * 1000, d * 1000
    ae = p.E_s / beton.E_cm
    Eeff = beton.E_cm / (1 + p.fi_pelzania)
    x, I = przekroj_zarysowany(bm, dm, As, 0.0, 0.0, p.E_s / Eeff)
    sig = p.E_s / Eeff * abs(M_qp) * 1e6 * (dm - x) / I
    w.krok("Naprężenie w stali (quasi-stała)", "σ_s", "", sig, "MPa", nd=0)
    hce = min(2.5 * (hm - dm), (hm - x) / 3, hm / 2)
    rho = As / (bm * hce)
    w.krok("Efektywny stopień zbrojenia", "ρ_p,eff = A_s/(b·h_c,ef)", f"{f(As, 0)}/({f(bm, 0)}·{f(hce, 1)})", rho, nd=5, zrodlo="(7.10)")
    kt = 0.4
    de = max((sig - kt * beton.f_ctm / rho * (1 + ae * rho)) / p.E_s, 0.6 * sig / p.E_s)
    w.krok("Różnica odkształceń", "ε_sm − ε_cm", "", de * 1000, "‰", nd=4, zrodlo="(7.9), k_t = 0,4")
    sr = 3.4 * c + 0.8 * 0.5 * 0.425 * fi / rho
    w.krok("Maksymalny rozstaw rys", "s_r,max = 3,4·c + 0,8·0,5·0,425·φ/ρ_p,eff", f"3,4·{f(c, 0)} + 0,17·{f(fi, 0)}/{f(rho, 5)}",
           sr, "mm", nd=0, zrodlo="(7.11)")
    wk = sr * de
    w.krok("Szerokość rys", "w_k = s_r,max·(ε_sm − ε_cm)", f"{f(sr, 0)}·{f(de * 1000, 4)}·10⁻³", wk, "mm", nd=3, zrodlo="(7.8)")
    w.sigma_s, w.w_k = sig, wk
    w.warunek("Szerokość rys (quasi-stała)", wk, w_max, "mm", "tabl. 7.1N", nd=3, symbol_E="w_k", symbol_R="w_max")
    return w


def zbrojenie_min_rysy(b: float, h: float, beton: Beton, sigma_s: float = 500.0, k_c: float = 0.4) -> float:
    """A_s,min = k_c·k·f_ct,eff·A_ct/σ_s (7.1), zginanie: A_ct = b·h/2, k = 1,0 (h ≤ 300) … 0,65 (h ≥ 800) [mm²]."""
    hm = h * 1000
    k = 1.0 if hm <= 300 else (0.65 if hm >= 800 else 1.0 - 0.35 * (hm - 300) / 500)
    return k_c * k * beton.f_ctm * (b * 1000 * hm / 2) / sigma_s


# ==================================================================================================
# Zakotwienie i zakłady (8.4, 8.7)
# ==================================================================================================
@dataclass
class Zakotwienie(Wynik):
    f_bd: float = 0.0
    l_b_rqd: float = 0.0
    l_bd: float = 0.0
    l_0: float = 0.0


def zakotwienie(fi: float, beton: Beton, stal: StalZbrojeniowa | None = None, sigma_sd: float | None = None,
                dobra_przyczepnosc: bool = True, alfa2: float = 1.0, proc_laczonych: float = 50.0, scisk: bool = False,
                nazwa: str | None = None) -> Zakotwienie:
    """f_bd = 2,25·η₁·η₂·f_ctd (8.2); l_b,rqd = (φ/4)·(σ_sd/f_bd) (8.3); l_bd = α₁…α₅·l_b,rqd ≥ l_b,min (8.4), l_b,min =
    max(0,3·l_b,rqd; 10φ; 100 mm) (8.6) [ściskanie: 0,6·l_b,rqd (8.7)]; zakład l₀ = α₁α₂α₃α₅α₆·l_b,rqd ≥ l₀,min =
    max(0,3·α₆·l_b,rqd; 15φ; 200 mm) (8.10, 8.11), α₆ = √(ρ₁/25) ∈ [1,0; 1,5]. Domyślnie α = 1 (pręty proste, bezpiecznie)."""
    stal = stal or StalZbrojeniowa()
    sig = stal.f_yd if sigma_sd is None else sigma_sd
    w = Zakotwienie(nazwa=nazwa or f"Zakotwienie i zakład pręta φ{f(fi, 0)} ({beton.klasa}, {stal.gatunek})")
    eta1 = 1.0 if dobra_przyczepnosc else 0.7
    eta2 = 1.0 if fi <= 32 else (132 - fi) / 100
    fbd = 2.25 * eta1 * eta2 * beton.f_ctd
    w.krok("Graniczne naprężenie przyczepności", "f_bd = 2,25·η₁·η₂·f_ctd", f"2,25·{f(eta1, 1)}·{f(eta2, 1)}·{f(beton.f_ctd, 3)}",
           fbd, "MPa", nd=3, zrodlo="(8.2)" + ("" if dobra_przyczepnosc else "; warunki przyczepności „inne” η₁ = 0,7"))
    lb = fi / 4 * sig / fbd
    w.krok("Podstawowa długość zakotwienia", "l_b,rqd = (φ/4)·(σ_sd/f_bd)", f"({f(fi, 0)}/4)·({f(sig, 1)}/{f(fbd, 3)})", lb,
           "mm", nd=0, zrodlo="(8.3)")
    lbmin = max((0.6 if scisk else 0.3) * lb, 10 * fi, 100.0)
    lbd = max(alfa2 * lb, lbmin)
    w.krok("Obliczeniowa długość zakotwienia", "l_bd = α₁·α₂·α₃·α₄·α₅·l_b,rqd ≥ l_b,min",
           f"{f(alfa2, 2)}·{f(lb, 0)} ≥ {f(lbmin, 0)}", lbd, "mm", nd=0, zrodlo="(8.4), (8.6)")
    a6 = min(max(math.sqrt(proc_laczonych / 25), 1.0), 1.5)
    l0min = max(0.3 * a6 * lb, 15 * fi, 200.0)
    l0 = max(a6 * alfa2 * lb, l0min)
    w.krok(f"Długość zakładu ({f(proc_laczonych, 0)}% prętów łączonych w przekroju)", "l₀ = α₆·l_b,rqd ≥ l₀,min, α₆ = √(ρ₁/25)",
           f"{f(a6, 2)}·{f(lb, 0)} ≥ {f(l0min, 0)}", l0, "mm", nd=0, zrodlo="(8.10), (8.11), tabl. 8.3")
    w.f_bd, w.l_b_rqd, w.l_bd, w.l_0 = fbd, lb, lbd, l0
    return w


def tabela_zakotwien(beton: Beton, srednice=(8, 10, 12, 16, 20), stal: StalZbrojeniowa | None = None) -> str:
    rows = []
    for fi in srednice:
        a = zakotwienie(fi, beton, stal)
        b = zakotwienie(fi, beton, stal, dobra_przyczepnosc=False)
        rows.append([f"φ{fi}", (a.l_bd, 0), (b.l_bd, 0), (a.l_0, 0), (b.l_0, 0)])
    return tabela(["Pręt", "l_bd dobre [mm]", "l_bd inne [mm]", "l₀ (50%) dobre [mm]", "l₀ (50%) inne [mm]"], rows)


# ==================================================================================================
# Wieńce i ściągi (9.10)
# ==================================================================================================
def wieniec(l_i: float, beton: Beton, stal: StalZbrojeniowa | None = None, q1: float = 10.0, q2: float = 70.0,
            nazwa: str = "Wieniec — ściąg obwodowy (9.10.2.2)") -> Wynik:
    """Ściąg obwodowy: F_tie,per = l_i·q₁ ≤ q₂ (9.15), q₁ = 10 kN/m, q₂ = 70 kN (zalecane [NZW NA]); zbrojenie może
    pracować przy f_yk (9.10.1(4)): A_s = F_tie/f_yk; praktyka krajowa: min. 4φ12 (A_s = 4,52 cm²)."""
    stal = stal or StalZbrojeniowa()
    w = Wynik(nazwa=nazwa)
    F = min(l_i * q1, q2)
    w.krok("Siła w ściągu obwodowym", "F_tie,per = l_i·q₁ ≤ q₂", f"{f(l_i)}·{f(q1, 0)} ≤ {f(q2, 0)}", F, "kN", zrodlo="(9.15) + NA [NZW]")
    As = F * 1000 / stal.f_yk
    w.krok("Wymagane zbrojenie", "A_s = F_tie,per/f_yk", f"{f(F, 1)}·10³/{f(stal.f_yk, 0)}", As, "mm²", nd=0, zrodlo="9.10.1(4)")
    Asp = 4 * pole_preta(12)
    w.krok("Przyjęto (min. konstrukcyjne)", "4φ12", "", Asp, "mm²", nd=0)
    w.warunek("Ściąg obwodowy", As, Asp, "mm²", "9.10.2.2", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
    return w


# ==================================================================================================
# Belka-ściana (tarcza) — model kratownicowy (5.6.4, 6.5, 9.7)
# ==================================================================================================
@dataclass
class BelkaSciana(Wynik):
    z: float = 0.0
    T: float = 0.0
    As_req: float = 0.0
    As_siatka: float = 0.0


def belka_sciana(l: float, h: float, b: float, q_d: float, beton: Beton, a_podp: float = 0.25,
                 stal: StalZbrojeniowa | None = None, nazwa: str = "Belka-ściana — model kratownicowy") -> BelkaSciana:
    """Jednoprzęsłowa belka-ściana (l/h < 3, 5.3.1(3)) obciążona równomiernie od góry q_d [kN/m] — prosty model
    kratownicowy (5.6.4): wypadkowe q_d·l/2 w odległości l/4 od podpór, ramię z = 0,2·(l + 2h) dla 1 ≤ l/h < 2,
    z = 0,6·l dla l/h < 1 (CEB-FIP; dla 2 ≤ l/h < 3: z = min(0,2·(l+2h); 0,9·d) [UPR]); ściąg T = q_d·l²/(8z);
    węzeł podporowy CCT σ ≤ k₂·ν'·f_cd (6.61, k₂ = 0,85, ν' = 1 − f_ck/250); krzyżulec σ ≤ 0,6·ν'·f_cd (6.56);
    siatka przy obu powierzchniach ρ ≥ 0,1 %, ≥ 150 mm²/m (9.7 [NZW NA]).
    OGRANICZENIE: tarcze z otworami, wieloprzęsłowe, wspornikowe lub obciążone od dołu — analiza MES/STM indywidualna."""
    stal = stal or StalZbrojeniowa()
    w = BelkaSciana(nazwa=nazwa)
    r = l / h
    w.krok("Smukłość tarczy", "l/h", f"{f(l)}/{f(h)}", r, nd=2, zrodlo="5.3.1(3): belka-ściana gdy l/h < 3")
    if r >= 3:
        w.uwaga("l/h ≥ 3 — element nie jest belką-ścianą; wymiarować jak belkę.")
    if r < 1:
        z = 0.6 * l
        w.krok("Ramię sił wewnętrznych", "z = 0,6·l", f"0,6·{f(l)}", z, "m", zrodlo="CEB-FIP (l/h < 1) [UPR]")
    else:
        z = 0.2 * (l + 2 * h)
        if r >= 2:
            z = min(z, 0.9 * (h - 0.05))
        w.krok("Ramię sił wewnętrznych", "z = 0,2·(l + 2h)", f"0,2·({f(l)} + 2·{f(h)})", z, "m", zrodlo="CEB-FIP (1 ≤ l/h < 2) [UPR]")
    M = q_d * l * l / 8
    T = M / z
    w.krok("Moment", "M_Ed = q_d·l²/8", f"{f(q_d)}·{f(l)}²/8", M, "kNm")
    w.krok("Siła w ściągu", "T = M_Ed/z", f"{f(M)}/{f(z, 3)}", T, "kN")
    As = T * 1000 / stal.f_yd
    w.krok("Zbrojenie ściągu (w pasie 0,1–0,2·h od dołu, zakotwione za podporą)", "A_s = T/f_yd", f"{f(T)}·10³/{f(stal.f_yd, 1)}",
           As, "mm²", nd=0, zrodlo="6.5.3")
    R = q_d * l / 2
    nup = 1 - beton.f_ck / 250
    sig_n = R * 1000 / (b * 1000 * a_podp * 1000)
    lim_n = 0.85 * nup * beton.f_cd
    w.krok("Naprężenie w węźle podporowym", "σ = R/(b·a)", f"{f(R)}·10³/({f(b * 1000, 0)}·{f(a_podp * 1000, 0)})", sig_n, "MPa", nd=2)
    w.warunek("Węzeł podporowy CCT", sig_n, lim_n, "MPa", "(6.61), k₂ = 0,85", symbol_E="σ_Ed", symbol_R="σ_Rd,max")
    th = math.atan2(z, l / 4)
    u = 2 * 0.06
    ws = a_podp * math.sin(th) + u * math.cos(th)
    C = R / math.sin(th)
    sig_c = C * 1000 / (b * 1000 * ws * 1000)
    w.krok("Krzyżulec ściskany", "C = R/sin θ; σ = C/(b·(a·sin θ + u·cos θ))", f"θ = {f(math.degrees(th), 1)}°", sig_c, "MPa", nd=2)
    w.warunek("Krzyżulec ściskany (strefa zarysowana)", sig_c, 0.6 * nup * beton.f_cd, "MPa", "(6.56)", symbol_E="σ_Ed",
              symbol_R="σ_Rd,max")
    As_s = max(0.001 * b * 1000 * 1000 / 2, 150.0)
    w.krok("Siatka przy każdej powierzchni, w obu kierunkach", "A_s,dbmin = max(0,1 %·A_c/2; 150 mm²/m)", "", As_s, "mm²/m", nd=0,
           zrodlo="9.7(1) [NZW NA]")
    w.z, w.T, w.As_req, w.As_siatka = z, T, As, As_s
    w.uwaga("Model kratownicowy uproszczony — tarcze z otworami, wieloprzęsłowe, wspornikowe lub z obciążeniem podwieszonym "
            "wymagają analizy MES (tarcza) lub indywidualnego modelu STM.")
    return w


# ==================================================================================================
# Zestawienie stali (PN-EN ISO 3766)
# ==================================================================================================
@dataclass
class Pret:
    """Pozycja pręta w wykazie stali. ksztalt — kod kształtu wg PN-EN ISO 3766 (00 prosty, 11 odgięty 90°,
    21 U, 51 strzemię zamknięte …); wymiary — długości odcinków a, b, c… [mm] (opisowo)."""
    element: str
    nr: int
    fi: int
    dl: float                 # długość pręta [m]
    n: int                    # liczba sztuk (łącznie)
    ksztalt: str = "00"
    wymiary: str = ""
    gatunek: str = "B500SP"

    @property
    def dl_calk(self) -> float:
        return self.dl * self.n

    @property
    def masa(self) -> float:
        return self.dl_calk * masa_preta(self.fi)


def wykaz_stali(prety: list[Pret], zapas: float = 0.0) -> str:
    """Wykaz stali zbrojeniowej (układ tabeli rysunku zbrojenia: nr, φ, kod kształtu ISO 3766, długość, szt., długości
    łączne wg średnic, masy)."""
    srednice = sorted({p.fi for p in prety})
    head = ["Element", "Nr", "φ [mm]", "Kształt (ISO 3766)", "Długość [m]", "Szt."] + [f"φ{d} [m]" for d in srednice]
    rows = []
    for p in prety:
        rows.append([p.element, p.nr, p.fi, f"{p.ksztalt} {p.wymiary}".strip(), (p.dl, 2), p.n] +
                    [(p.dl_calk, 2) if p.fi == d else "" for d in srednice])
    sum_l = [sum(p.dl_calk for p in prety if p.fi == d) for d in srednice]
    rows.append(["**Długość łączna [m]**", "", "", "", "", ""] + [(x, 1) for x in sum_l])
    rows.append(["Masa 1 m [kg/m]", "", "", "", "", ""] + [(masa_preta(d), 3) for d in srednice])
    masy = [x * masa_preta(d) for x, d in zip(sum_l, srednice)]
    rows.append(["**Masa [kg]**", "", "", "", "", ""] + [(m, 1) for m in masy])
    tot = sum(masy) * (1 + zapas)
    out = tabela(head, rows)
    gat = sorted({p.gatunek for p in prety})
    out += f"\n\nMasa całkowita stali {', '.join(gat)}: **{f(tot, 1)} kg**" + (f" (z zapasem {f(zapas * 100, 0)}%)" if zapas else "") + "."
    return out


def masa_stali(prety: list[Pret]) -> float:
    return sum(p.masa for p in prety)


# ==================================================================================================
# Procedury złożone
# ==================================================================================================
def ugiecie_komplet(l_eff: float, K: float, h: float, d: float, As_req: float, As_prov: float, beton: Beton,
                    M_qp: float, w_EI1: float, p: Parametry | None = None, b: float = 1.0, k_skurcz: float = 0.125,
                    L_ref: float | None = None, stal: StalZbrojeniowa | None = None, teowy: bool = False,
                    nazwa: str = "Stan graniczny ugięć") -> Wynik:
    """Ugięcie: najpierw l/d (7.4.2); gdy niespełnione — decyduje obliczenie (7.4.3). Wynik zawiera oba sprawdzenia,
    warunkiem jest to miarodajne (7.4.2(1): spełnienie l/d zwalnia z obliczeń)."""
    p = p or Parametry()
    w = Wynik(nazwa=nazwa)
    ld = ugiecie_ld(l_eff, d, As_req, As_prov, b, beton, K=K, stal=stal, teowy=teowy)
    ug = ugiecie_obliczeniowe(M_qp, w_EI1, l_eff, b, h, d, As_prov, beton, p, k_skurcz=k_skurcz, L_ref=L_ref)
    w.kroki += ld.kroki
    w.kroki.append(Krok("*Obliczenie ugięcia (7.4.3)*"))
    w.kroki += ug.kroki
    if ld.ok:
        w.warunki += ld.warunki
        w.uwaga(f"l/d spełnione — obliczenie (7.4.3) informacyjnie: w = {f(ug.w, 1)} mm ≤? {f(ug.w_dop, 1)} mm.")
    else:
        w.warunki += ug.warunki
        w.uwaga(f"l/d niespełnione ({f(ld.l_d_rzecz, 1)} > {f(ld.l_d_dop, 1)}) — miarodajne obliczenie ugięcia (7.4.3).")
    w.l_d = ld
    w.obl = ug
    return w


def wymiaruj_plyte(M_Ed: float, h: float, d: float, beton: Beton, stal: StalZbrojeniowa | None = None, s_max: float = 250.0,
                   fi_min: int = 8, fi_max: int = 16, nazwa: str = "Zginanie płyty (na 1 m)") -> tuple[Zginanie, int, float, float]:
    """Wymiarowanie pasma płyty b = 1 m: (wynik zginania, φ, s [mm], A_s,prov [mm²/m]) — A_s ≥ max(A_s,req; A_s,min)."""
    stal = stal or StalZbrojeniowa()
    zg = zginanie_prostokat(M_Ed, 1.0, h, d, beton, stal, nazwa=nazwa, element="plyta")
    fi, s, As = dobierz_plyta(zg.As_req, s_max, fi_min, fi_max, As_min=zg.As_min if abs(M_Ed) > 1e-6 else 0.0)
    zg.As_prov = As
    zg.zbrojenie = f"φ{fi} co {f(s / 10, 0)} cm"
    zg.krok("Przyjęto", zg.zbrojenie, "", As / 100, "cm²/m", nd=2)
    zg.warunek("Zbrojenie na zginanie", max(zg.As_req, zg.As_min), As, "mm²/m", "6.1, (9.1N)", nd=0,
               symbol_E="A_s,req", symbol_R="A_s,prov")
    return zg, fi, s, As
