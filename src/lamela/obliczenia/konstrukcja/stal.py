"""Konstrukcje stalowe wg PN-EN 1993-1-1:2006 + A1 + NA:2010 i PN-EN 1993-1-8 (R5-70…R5-72, W-271).

Zakres: klasa przekroju (tabl. 5.2), nośność przekroju (6.2: N, M, V, interakcja M–V), wyboczenie giętne (6.3.1,
krzywe a/b/c/d), zwichrzenie — przypadek ogólny 6.3.2.2 z M_cr wg wzoru trzyczłonowego (C₁, C₂ — NCCI SN003),
interakcja N + M (6.3.3, zał. B — metoda 2), belki (zginanie, ścinanie, zwichrzenie, ugięcia L/250 — NA 7.2),
połączenia: śruby (ścinanie, docisk, rozciąganie — PN-EN 1993-1-8 tabl. 3.4), spoiny pachwinowe (metoda uproszczona 4.5.3.3).
γ_M0 = γ_M1 = 1,0, γ_M2 = 1,25 (NA). Jednostki: N [kN], M [kNm], L [m]; przekroje w mm (materialy.Przekroj).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .materialy import Przekroj, StalKonstr, przekroj
from .wspolne import BladDanych, Parametry, Wynik, f

ALFA_KRZYWEJ = {"a0": 0.13, "a": 0.21, "b": 0.34, "c": 0.49, "d": 0.76}


def chi(lam: float, krzywa: str) -> float:
    """χ = 1/(Φ + √(Φ² − λ̄²)) ≤ 1, Φ = 0,5·[1 + α·(λ̄ − 0,2) + λ̄²] (6.49)."""
    a = ALFA_KRZYWEJ[krzywa]
    if lam <= 0.2:
        return 1.0
    F = 0.5 * (1 + a * (lam - 0.2) + lam * lam)
    return min(1.0, 1.0 / (F + math.sqrt(max(F * F - lam * lam, 0.0))))


def krzywe_wyboczenia(prz: Przekroj) -> tuple[str, str]:
    """Krzywe wyboczeniowe (tabl. 6.2) dla osi y i z."""
    if prz.typ in ("RK", "RO"):
        return ("c", "c") if prz.formowany_na_zimno else ("a", "a")
    if prz.typ == "I":
        if prz.h / prz.b > 1.2:
            return "a", "b"
        return "b", "c"
    return "c", "c"


@dataclass
class KlasaPrzekroju(Wynik):
    klasa: int = 1


def klasa_przekroju(prz: Przekroj, stal: StalKonstr, rodzaj: str = "sciskanie") -> KlasaPrzekroju:
    """Klasa przekroju (tabl. 5.2) dla ściskania ('sciskanie') lub zginania ('zginanie')."""
    e = stal.eps
    w = KlasaPrzekroju(nazwa=f"Klasa przekroju {prz.nazwa} ({rodzaj}, {stal.gatunek}, ε = {f(e, 3)})")
    klasy = []
    if prz.typ == "RK":
        for bok in (prz.h, prz.b):
            c = bok - 3 * prz.t
            ct = c / prz.t
            lim = (33, 38, 42) if rodzaj == "sciskanie" else (72, 83, 124)
            k = next((i + 1 for i, L in enumerate(lim) if ct <= L * e), 4)
            w.krok(f"Ścianka {f(bok, 0)} mm", "c/t = (b − 3t)/t", f"({f(bok, 0)} − 3·{f(prz.t, 1)})/{f(prz.t, 1)}", ct, nd=1,
                   zrodlo=f"klasa {k}: ≤ {lim[min(k, 3) - 1]}ε = {f(lim[min(k, 3) - 1] * e, 1)}")
            klasy.append(k)
    elif prz.typ == "RO":
        dt = prz.h / prz.t
        lim = (50, 70, 90)
        k = next((i + 1 for i, L in enumerate(lim) if dt <= L * e * e), 4)
        w.krok("Rura okrągła", "d/t", f"{f(prz.h, 1)}/{f(prz.t, 1)}", dt, nd=1, zrodlo=f"klasa {k}")
        klasy.append(k)
    elif prz.typ == "I":
        cf = (prz.b - prz.t_w - 2 * prz.r) / 2 / prz.t_f
        kf = next((i + 1 for i, L in enumerate((9, 10, 14)) if cf <= L * e), 4)
        w.krok("Półka (wspornikowa, ściskana)", "c/t_f", "", cf, nd=2, zrodlo=f"klasa {kf}")
        cw = (prz.h - 2 * prz.t_f - 2 * prz.r) / prz.t_w
        lim = (33, 38, 42) if rodzaj == "sciskanie" else (72, 83, 124)
        kw = next((i + 1 for i, L in enumerate(lim) if cw <= L * e), 4)
        w.krok("Środnik", "c/t_w", "", cw, nd=2, zrodlo=f"klasa {kw}")
        klasy += [kf, kw]
    else:
        klasy.append(1)
    w.klasa = max(klasy)
    w.krok("Klasa przekroju", "", "", str(w.klasa))
    if w.klasa == 4:
        w.uwaga("Przekrój klasy 4 — wymaga przekroju efektywnego (PN-EN 1993-1-5); poza zakresem biblioteki.")
    return w


@dataclass
class ElementStalowy(Wynik):
    klasa: int = 1
    N_Rd: float = 0.0
    M_Rd: float = 0.0
    V_Rd: float = 0.0
    chi_y: float = 1.0
    chi_z: float = 1.0
    chi_LT: float = 1.0
    M_cr: float = 0.0
    w: float = 0.0
    w_dop: float = 0.0


def M_cr_dwuteownik(prz: Przekroj, stal: StalKonstr, L: float, C1: float = 1.127, C2: float = 0.454, z_g: float = 0.0) -> float:
    """Moment krytyczny zwichrzenia [kNm] dwuteownika bisymetrycznego (k = k_w = 1): M_cr = C₁·π²·E·I_z/L²·
    {√[I_w/I_z + L²·G·I_t/(π²·E·I_z) + (C₂·z_g)²] − C₂·z_g} (NCCI SN003; z_g [mm] > 0 — obciążenie nad środkiem ścinania)."""
    E, G = stal.E, stal.G
    Lm = L * 1000
    a = C1 * math.pi ** 2 * E * prz.I_z / Lm ** 2
    b = math.sqrt(prz.I_w / prz.I_z + Lm ** 2 * G * prz.I_t / (math.pi ** 2 * E * prz.I_z) + (C2 * z_g) ** 2) - C2 * z_g
    return a * b / 1e6


def slup(prz: Przekroj | str, stal: StalKonstr | str, N_Ed: float, L_cr_y: float, L_cr_z: float | None = None,
         M_y_Ed: float = 0.0, psi: float = 1.0, wykres: str = "liniowy", p: Parametry | None = None,
         nazwa: str = "Słup stalowy — ściskanie z wyboczeniem") -> ElementStalowy:
    """Pręt ściskany (ew. z momentem M_y,Ed) — 6.2, 6.3.1, 6.3.3 + zał. B (metoda 2, przekroje nie podatne na
    skręcanie: rury; dla dwuteowników — z założeniem zabezpieczenia przed zwichrzeniem [UPR]).
    wykres: 'liniowy' (C_my = 0,6 + 0,4ψ ≥ 0,4), 'rownomierne' (0,95), 'skupione' (0,90) — tabl. B.3."""
    p = p or Parametry()
    prz = przekroj(prz) if isinstance(prz, str) else prz
    stal = StalKonstr(stal) if isinstance(stal, str) else stal
    L_cr_z = L_cr_y if L_cr_z is None else L_cr_z
    w = ElementStalowy(nazwa=nazwa)
    w.krok("Przekrój", prz.nazwa, "", prz.opis().split(": ", 1)[1])
    w.krok("Stal", stal.gatunek, "", f"f_y = {f(stal.f_y, 0)} MPa, E = {f(stal.E / 1000, 0)} GPa")
    kl = klasa_przekroju(prz, stal, "sciskanie")
    w.dolacz(kl)
    w.klasa = kl.klasa
    NRk = prz.A * stal.f_y / 1000
    w.krok("Nośność przekroju przy ściskaniu", "N_c,Rd = A·f_y/γ_M0", f"{f(prz.A, 0)}·{f(stal.f_y, 0)}/{f(p.gM0, 2)}·10⁻³",
           NRk / p.gM0, "kN", zrodlo="(6.10)")
    ky, kz = krzywe_wyboczenia(prz)
    res = {}
    for os_, Lcr, I, kr in (("y", L_cr_y, prz.I_y, ky), ("z", L_cr_z, prz.I_z, kz)):
        Ncr = math.pi ** 2 * stal.E * I / (Lcr * 1000) ** 2 / 1000
        lam = math.sqrt(NRk / Ncr)
        c = chi(lam, kr)
        w.krok(f"Smukłość względna (oś {os_}, L_cr = {f(Lcr, 2)} m)", f"λ̄_{os_} = √(A·f_y/N_cr), N_cr = π²·E·I_{os_}/L_cr²",
               f"√({f(NRk, 1)}/{f(Ncr, 1)})", lam, nd=3, zrodlo="(6.50)")
        w.krok(f"Współczynnik wyboczeniowy (krzywa {kr})", f"χ_{os_}", f"α = {f(ALFA_KRZYWEJ[kr], 2)}", c, nd=3, zrodlo="(6.49), tabl. 6.2")
        res[os_] = (lam, c)
    w.chi_y, w.chi_z = res["y"][1], res["z"][1]
    NbRd = min(w.chi_y, w.chi_z) * NRk / p.gM1
    w.N_Rd = NbRd
    w.krok("Nośność na wyboczenie", "N_b,Rd = χ_min·A·f_y/γ_M1", "", NbRd, "kN", zrodlo="(6.47)")
    w.warunek("Wyboczenie giętne", N_Ed, NbRd, "kN", "(6.46)", symbol_E="N_Ed", symbol_R="N_b,Rd")
    if abs(M_y_Ed) > 1e-9:
        W = prz.W_pl_y if w.klasa <= 2 else prz.W_el_y
        MRk = W * stal.f_y / 1e6
        w.M_Rd = MRk / p.gM0
        Cmy = {"rownomierne": 0.95, "skupione": 0.90}.get(wykres, max(0.6 + 0.4 * psi, 0.4))
        ny = N_Ed / (w.chi_y * NRk / p.gM1)
        nz = N_Ed / (w.chi_z * NRk / p.gM1)
        kyy = min(Cmy * (1 + (res["y"][0] - 0.2) * ny), Cmy * (1 + 0.8 * ny))
        kzy = 0.6 * kyy
        w.krok("Nośność na zginanie", "M_y,Rk = W·f_y", f"{f(W / 1e3, 1)}·10³·{f(stal.f_y, 0)}·10⁻⁶", MRk, "kNm", zrodlo="(6.13)/(6.14)")
        w.krok("Współczynniki interakcji (zał. B, metoda 2)", "C_my; k_yy; k_zy = 0,6·k_yy", "", f"{f(Cmy, 2)}; {f(kyy, 3)}; {f(kzy, 3)}",
               zrodlo="tabl. B.1, B.3")
        u1 = ny + kyy * abs(M_y_Ed) / (MRk / p.gM1)
        u2 = nz + kzy * abs(M_y_Ed) / (MRk / p.gM1)
        w.krok("Warunek (6.61)", "N_Ed/(χ_y·N_Rk/γ_M1) + k_yy·M_y,Ed/(M_y,Rk/γ_M1)", f"{f(ny, 3)} + {f(kyy, 3)}·{f(abs(M_y_Ed), 2)}/{f(MRk, 2)}", u1, nd=3)
        w.krok("Warunek (6.62)", "N_Ed/(χ_z·N_Rk/γ_M1) + k_zy·M_y,Ed/(M_y,Rk/γ_M1)", f"{f(nz, 3)} + {f(kzy, 3)}·{f(abs(M_y_Ed), 2)}/{f(MRk, 2)}", u2, nd=3)
        w.warunek("Interakcja N + M (6.61)", u1, 1.0, "", "(6.61)", nd=3, symbol_E="Σ", symbol_R="1,0")
        w.warunek("Interakcja N + M (6.62)", u2, 1.0, "", "(6.62)", nd=3, symbol_E="Σ", symbol_R="1,0")
    return w


def belka_stalowa(prz: Przekroj | str, stal: StalKonstr | str, L: float, M_Ed: float, V_Ed: float, w_k: float | None = None,
                  L_LT: float | None = None, C1: float = 1.127, C2: float = 0.454, obc_na_pasie: bool = True,
                  w_lim_mian: float = 250.0, p: Parametry | None = None, nazwa: str = "Belka stalowa") -> ElementStalowy:
    """Belka zginana: M_c,Rd (6.13/6.14), V_pl,Rd (6.18), interakcja M–V (6.2.8), zwichrzenie (6.3.2.2 — przypadek ogólny;
    L_LT = None → pas ściskany stężony ciągle), ugięcie w_k [mm] (z obliczeń SLS) ≤ L/250 (NA 7.2, R5-71)."""
    p = p or Parametry()
    prz = przekroj(prz) if isinstance(prz, str) else prz
    stal = StalKonstr(stal) if isinstance(stal, str) else stal
    w = ElementStalowy(nazwa=nazwa)
    w.krok("Przekrój", prz.nazwa, "", prz.opis().split(": ", 1)[1])
    kl = klasa_przekroju(prz, stal, "zginanie")
    w.dolacz(kl)
    w.klasa = kl.klasa
    W = prz.W_pl_y if kl.klasa <= 2 else prz.W_el_y
    McRd = W * stal.f_y / p.gM0 / 1e6
    w.krok("Nośność na zginanie", "M_c,Rd = W·f_y/γ_M0", f"{f(W / 1e3, 1)}·10³·{f(stal.f_y, 0)}·10⁻⁶", McRd, "kNm", zrodlo="(6.13)")
    Vpl = prz.A_vz * stal.f_y / math.sqrt(3) / p.gM0 / 1000
    w.krok("Nośność na ścinanie", "V_pl,Rd = A_v·(f_y/√3)/γ_M0", f"{f(prz.A_vz, 0)}·({f(stal.f_y, 0)}/√3)·10⁻³", Vpl, "kN", zrodlo="(6.18)")
    w.V_Rd = Vpl
    if abs(V_Ed) > 0.5 * Vpl:
        rho = (2 * abs(V_Ed) / Vpl - 1) ** 2
        McRd *= (1 - rho)
        w.krok("Redukcja nośności na zginanie (V_Ed > 0,5·V_pl,Rd)", "ρ = (2V_Ed/V_pl,Rd − 1)²", "", rho, nd=3, zrodlo="6.2.8")
    w.M_Rd = McRd
    w.warunek("Zginanie — nośność przekroju", abs(M_Ed), McRd, "kNm", "(6.12)", symbol_E="M_Ed", symbol_R="M_c,Rd")
    w.warunek("Ścinanie", abs(V_Ed), Vpl, "kN", "(6.17)", symbol_E="V_Ed", symbol_R="V_pl,Rd")
    if L_LT and prz.typ == "I":
        zg = prz.h / 2 if obc_na_pasie else 0.0
        Mcr = M_cr_dwuteownik(prz, stal, L_LT, C1, C2, zg)
        lam = math.sqrt(W * stal.f_y / 1e6 / Mcr)
        kr = "a" if prz.h / prz.b <= 2 else "b"
        cLT = 1.0 if (lam <= 0.2 or abs(M_Ed) / Mcr <= 0.04) else chi(lam, kr)
        w.krok("Moment krytyczny zwichrzenia", "M_cr (C₁, C₂, z_g)", f"C₁ = {f(C1, 3)}, C₂ = {f(C2, 3)}, z_g = {f(zg, 0)} mm, L = {f(L_LT, 2)} m",
               Mcr, "kNm", zrodlo="NCCI SN003")
        w.krok(f"Smukłość i współczynnik zwichrzenia (krzywa {kr})", "λ̄_LT = √(W·f_y/M_cr); χ_LT", f"λ̄_LT = {f(lam, 3)}", cLT, nd=3,
               zrodlo="6.3.2.2, tabl. 6.4")
        MbRd = cLT * W * stal.f_y / p.gM1 / 1e6
        w.krok("Nośność na zwichrzenie", "M_b,Rd = χ_LT·W·f_y/γ_M1", "", MbRd, "kNm", zrodlo="(6.55)")
        w.chi_LT, w.M_cr = cLT, Mcr
        w.warunek("Zwichrzenie", abs(M_Ed), MbRd, "kNm", "(6.54)", symbol_E="M_Ed", symbol_R="M_b,Rd")
    if w_k is not None:
        wd = L * 1000 / w_lim_mian
        w.krok("Ugięcie (SLS, charakterystyczna)", "w", "", w_k, "mm", nd=1)
        w.w, w.w_dop = w_k, wd
        w.warunek(f"Ugięcie ≤ L/{f(w_lim_mian, 0)}", w_k, wd, "mm", "NA 7.2 (R5-71)", nd=1, symbol_E="w", symbol_R="w_lim")
    return w


# ==================================================================================================
# Połączenia (PN-EN 1993-1-8)
# ==================================================================================================
SRUBY = {12: 84.3, 16: 157.0, 20: 245.0, 24: 353.0, 27: 459.0, 30: 561.0}
KLASY_SRUB = {"4.6": (400.0, 0.6), "5.6": (500.0, 0.6), "8.8": (800.0, 0.6), "10.9": (1000.0, 0.5), "4.8": (400.0, 0.5),
              "5.8": (500.0, 0.5)}


def sruby(n: int, d: int, klasa: str, t: float, stal: StalKonstr | str, F_v_Ed: float = 0.0, F_t_Ed: float = 0.0,
          e1: float | None = None, e2: float | None = None, p1: float | None = None, p2: float | None = None,
          ciecia: int = 1, p: Parametry | None = None, nazwa: str | None = None) -> Wynik:
    """Połączenie na n śrubach kategorii A/D (PN-EN 1993-1-8 tabl. 3.4): F_v,Rd = α_v·f_ub·A_s/γ_M2 (gwint w płaszczyźnie
    ścinania), F_b,Rd = k₁·α_b·f_u·d·t/γ_M2, F_t,Rd = 0,9·f_ub·A_s/γ_M2, interakcja F_v/F_v,Rd + F_t/(1,4·F_t,Rd) ≤ 1.
    F_v_Ed, F_t_Ed — siły całkowite [kN] (rozdział równomierny); t — grubość najcieńszej części [mm]; e/p [mm]."""
    p = p or Parametry()
    stal = StalKonstr(stal) if isinstance(stal, str) else stal
    if d not in SRUBY or klasa not in KLASY_SRUB:
        raise BladDanych("śruba M{d} kl. {klasa} poza tablicą")
    As = SRUBY[d]
    fub, av = KLASY_SRUB[klasa]
    d0 = d + (2 if d <= 24 else 3)
    e1 = e1 or 1.2 * d0 * 1.5
    e2 = e2 or 1.2 * d0 * 1.5
    w = Wynik(nazwa=nazwa or f"Połączenie śrubowe {n}×M{d} kl. {klasa}")
    Fv = ciecia * av * fub * As / p.gM2 / 1000
    w.krok("Nośność śruby na ścinanie", "F_v,Rd = n_s·α_v·f_ub·A_s/γ_M2", f"{ciecia}·{f(av, 1)}·{f(fub, 0)}·{f(As, 1)}/{f(p.gM2, 2)}·10⁻³",
           Fv, "kN", zrodlo="PN-EN 1993-1-8 tabl. 3.4")
    ad = e1 / (3 * d0) if p1 is None else min(e1 / (3 * d0), p1 / (3 * d0) - 0.25)
    ab = min(ad, fub / stal.f_u, 1.0)
    k1 = min(2.8 * e2 / d0 - 1.7, 2.5) if p2 is None else min(2.8 * e2 / d0 - 1.7, 1.4 * p2 / d0 - 1.7, 2.5)
    Fb = k1 * ab * stal.f_u * d * t / p.gM2 / 1000
    w.krok("Nośność na docisk", "F_b,Rd = k₁·α_b·f_u·d·t/γ_M2", f"{f(k1, 2)}·{f(ab, 3)}·{f(stal.f_u, 0)}·{d}·{f(t, 1)}/{f(p.gM2, 2)}·10⁻³",
           Fb, "kN", zrodlo="tabl. 3.4")
    Ft = 0.9 * fub * As / p.gM2 / 1000
    w.krok("Nośność na rozciąganie", "F_t,Rd = 0,9·f_ub·A_s/γ_M2", f"0,9·{f(fub, 0)}·{f(As, 1)}/{f(p.gM2, 2)}·10⁻³", Ft, "kN")
    fv1, ft1 = F_v_Ed / n, F_t_Ed / n
    w.warunek("Ścinanie śruby", fv1, Fv, "kN", "tabl. 3.4", symbol_E="F_v,Ed", symbol_R="F_v,Rd")
    w.warunek("Docisk", fv1, Fb, "kN", "tabl. 3.4", symbol_E="F_v,Ed", symbol_R="F_b,Rd")
    if F_t_Ed:
        w.warunek("Rozciąganie", ft1, Ft, "kN", "tabl. 3.4", symbol_E="F_t,Ed", symbol_R="F_t,Rd")
        w.warunek("Interakcja ścinanie + rozciąganie", fv1 / Fv + ft1 / (1.4 * Ft), 1.0, "", "tabl. 3.4", nd=3,
                  symbol_E="Σ", symbol_R="1,0")
    return w


def spoina_pachwinowa(a: float, l: float, F_Ed: float, stal: StalKonstr | str, p: Parametry | None = None,
                      nazwa: str | None = None) -> Wynik:
    """Metoda uproszczona (PN-EN 1993-1-8 p. 4.5.3.3): F_w,Rd = f_vw,d·a·l_eff, f_vw,d = f_u/(√3·β_w·γ_M2),
    l_eff = l − 2a; a ≥ 3 mm. a, l [mm], F_Ed [kN]."""
    p = p or Parametry()
    stal = StalKonstr(stal) if isinstance(stal, str) else stal
    w = Wynik(nazwa=nazwa or f"Spoina pachwinowa a = {f(a, 0)} mm, l = {f(l, 0)} mm")
    fvw = stal.f_u / (math.sqrt(3) * stal.beta_w * p.gM2)
    leff = max(l - 2 * a, 0)
    FR = fvw * a * leff / 1000
    w.krok("Wytrzymałość spoiny na ścinanie", "f_vw,d = f_u/(√3·β_w·γ_M2)", f"{f(stal.f_u, 0)}/(√3·{f(stal.beta_w, 2)}·{f(p.gM2, 2)})",
           fvw, "MPa", nd=1, zrodlo="(4.4)")
    w.krok("Nośność spoiny", "F_w,Rd = f_vw,d·a·(l − 2a)", f"{f(fvw, 1)}·{f(a, 0)}·{f(leff, 0)}·10⁻³", FR, "kN", zrodlo="(4.3)")
    w.warunek("Spoina pachwinowa", abs(F_Ed), FR, "kN", "PN-EN 1993-1-8 4.5.3.3", symbol_E="F_w,Ed", symbol_R="F_w,Rd")
    if a < 3:
        w.uwaga("a < 3 mm — niedopuszczalne (4.5.2(2)).")
    return w
