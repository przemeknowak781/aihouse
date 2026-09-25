"""Konstrukcje murowe wg PN-EN 1996-1-1+A1:2013 + NA:2014 (+Ap2) oraz PN-EN 1996-3 (metody uproszczone) — R5-60…R5-63, W-270.

Zakres: nośność ścian obciążonych pionowo (6.1.2: Φ_i na górze/dole (6.4), Φ_m w połowie wysokości wg zał. G, smukłość
h_ef/t_ef ≤ 27, mimośrody: od stropu, wiatru, e_init = h_ef/450, pełzania e_k), docisk pod belkami/nadprożami (6.1.3),
filarki z redukcją η_A (pole < 0,3 m², NA; wartości η_A — R5-63 [NZW — źródło producenta]), ściany obciążone poziomo
wiatrem (6.3.1 — nośność na zginanie, dolne oszacowanie pasmem jednokierunkowym), metoda uproszczona PN-EN 1996-3 4.2.2
(Φ_s) jako sprawdzenie porównawcze [NZW].

Jednostki: N [kN/m] (ściany) lub [kN] (filarki, docisk), t, h [m], f [MPa].
Mimośród reakcji stropu na ścianie: e = t/2 − a/3 (reakcja w ⅓ głębokości oparcia a od lica wewnętrznego — rozkład
trójkątny docisku przy obrocie płyty) [UPR — alternatywa: rama zastępcza wg zał. C].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .materialy import Mur
from .wspolne import BladDanych, Parametry, Wynik, f

# η_A — NA (wg Xella 2017, tabl. 4.5; R5-63): pole [m²] → η_A (interpolacja liniowa; ≤ 0,09 → 2,00)
ETA_A = [(0.09, 2.00), (0.12, 1.43), (0.20, 1.25), (0.30, 1.00)]


def eta_A(A: float) -> float:
    """Współczynnik redukcji wytrzymałości filarka o polu A < 0,3 m²: f_d/η_A (NA do PN-EN 1996-1-1) [NZW]."""
    if A >= 0.30:
        return 1.0
    if A <= ETA_A[0][0]:
        return ETA_A[0][1]
    xs, ys = zip(*ETA_A)
    return float(np.interp(A, xs, ys))


def rho_n(h: float, podparcie: str = "2", l: float | None = None, rho2: float = 0.75) -> tuple[float, str]:
    """Współczynnik redukcyjny wysokości ściany (5.5.1.2): '2' — podparta górą i dołem (ρ₂ = 0,75 przy stropach
    żelbetowych o oparciu ≥ ⅔t, inaczej 1,0); '3' — dodatkowo jedna krawędź pionowa usztywniona (ρ₃, 5.6); '4' — obie
    krawędzie pionowe usztywnione (ρ₄, 5.8); l — odległość krawędzi usztywnionych [m]."""
    if podparcie == "2" or not l:
        return rho2, "ρ₂"
    if podparcie == "3":
        if h <= 3.5 * l:
            return rho2 / (1 + (rho2 * h / (3 * l)) ** 2), "ρ₃ = ρ₂/(1 + (ρ₂·h/(3l))²)"
        return 1.5 * l / h, "ρ₃ = 1,5·l/h"
    if podparcie == "4":
        if h <= 1.15 * l:
            return rho2 / (1 + (rho2 * h / l) ** 2), "ρ₄ = ρ₂/(1 + (ρ₂·h/l)²)"
        return 0.5 * l / h, "ρ₄ = 0,5·l/h"
    raise BladDanych(f"podparcie ściany {podparcie}?")


def phi_m(e_mk: float, t: float, h_ef: float, t_ef: float, mur: Mur) -> tuple[float, float, float]:
    """Φ_m wg zał. G (G.1–G.4): A₁ = 1 − 2e_mk/t, u = (λ − 0,063)/(0,73 − 1,17·e_mk/t), λ = (h_ef/t_ef)·√(f_k/E),
    Φ_m = A₁·exp(−u²/2). Zwraca (Φ_m, λ, u)."""
    lam = h_ef / t_ef * math.sqrt(mur.f_k / mur.E)
    A1 = 1 - 2 * e_mk / t
    u = (lam - 0.063) / (0.73 - 1.17 * e_mk / t)
    return max(A1 * math.exp(-u * u / 2), 0.0), lam, u


@dataclass
class SciananN(Wynik):
    h_ef: float = 0.0
    smuklosc: float = 0.0
    Phi_g: float = 0.0
    Phi_d: float = 0.0
    Phi_m: float = 0.0
    N_Rd_g: float = 0.0
    N_Rd_m: float = 0.0
    N_Rd_d: float = 0.0


def sciana_nosnosc(N_g: float, N_m: float, N_d: float, t: float, h: float, mur: Mur, M_g: float = 0.0, M_d: float = 0.0,
                   M_w: float = 0.0, podparcie: str = "2", l: float | None = None, rho2: float = 0.75,
                   p: Parametry | None = None, A_red: float = 1.0, nazwa: str = "Ściana obciążona pionowo") -> SciananN:
    """Nośność ściany jednowarstwowej obciążonej głównie pionowo (PN-EN 1996-1-1 p. 6.1.2), na 1 m długości.

    N_g, N_m, N_d — obliczeniowe siły pionowe na górze, w połowie wysokości i na dole [kN/m]; M_g, M_d — momenty od
    mimośrodowego oparcia stropów [kNm/m] (znak: ten sam kierunek dodatni); M_w — moment od wiatru w połowie wysokości
    [kNm/m]; A_red — mnożnik f_d (1/η_A dla filarków). Wynik: Φ_i (6.4), Φ_m (zał. G), N_Rd = Φ·t·f_d (6.2)."""
    p = p or Parametry()
    w = SciananN(nazwa=nazwa)
    fd = mur.f_d * A_red
    w.krok("Wytrzymałość charakterystyczna muru", "f_k = K·f_b^0,85", f"{f(mur.K, 2)}·{f(mur.f_b, 0)}^0,85", mur.f_k, "MPa",
           nd=2, zrodlo="(3.2) + NA tabl. NA.5 (K = 0,60, Ap2:2014-09)")
    w.krok("Wytrzymałość obliczeniowa", "f_d = f_k/γ_M" + (" · (1/η_A)" if A_red != 1.0 else ""),
           f"{f(mur.f_k, 2)}/{f(mur.gamma_M, 1)}" + (f"·{f(A_red, 3)}" if A_red != 1.0 else ""), fd, "MPa", nd=2,
           zrodlo="NA tabl. NA.1 (kat. I, zaprawa projektowana, klasa wykonania A)")
    rn, rn_opis = rho_n(h, podparcie, l, rho2)
    hef = rn * h
    w.krok("Wysokość efektywna", f"h_ef = {rn_opis.split(' = ')[0]}·h", f"{f(rn, 3)}·{f(h, 2)}", hef, "m", nd=3,
           zrodlo="(5.2), 5.5.1.2")
    sm = hef / t
    w.krok("Smukłość", "h_ef/t_ef", f"{f(hef, 3)}/{f(t, 3)}", sm, nd=2)
    w.warunek("Smukłość ściany", sm, 27.0, "", "5.5.1.4", nd=1, symbol_E="h_ef/t_ef", symbol_R="27")
    einit = hef / 450
    w.krok("Mimośród przypadkowy", "e_init = h_ef/450", f"{f(hef * 1000, 0)}/450", einit * 1000, "mm", nd=1, zrodlo="5.5.1.1(4)")
    emin = 0.05 * t

    def e_i(N, M):
        e = (abs(M) / N if N > 0 else 0.0) + einit
        return max(e, emin)
    eg, ed = e_i(N_g, M_g), e_i(N_d, M_d)
    w.krok("Mimośród na górze", "e_g = M_g/N_g + e_init ≥ 0,05t", f"{f(abs(M_g), 2)}/{f(N_g, 1)} + {f(einit, 4)}", eg * 1000,
           "mm", nd=1, zrodlo="(6.5)")
    w.krok("Mimośród na dole", "e_d = M_d/N_d + e_init ≥ 0,05t", f"{f(abs(M_d), 2)}/{f(N_d, 1)} + {f(einit, 4)}", ed * 1000,
           "mm", nd=1, zrodlo="(6.5)")
    Pg, Pd = 1 - 2 * eg / t, 1 - 2 * ed / t
    w.krok("Współczynnik redukcyjny — góra", "Φ_g = 1 − 2e_g/t", f"1 − 2·{f(eg * 1000, 1)}/{f(t * 1000, 0)}", Pg, nd=3, zrodlo="(6.4)")
    w.krok("Współczynnik redukcyjny — dół", "Φ_d = 1 − 2e_d/t", f"1 − 2·{f(ed * 1000, 1)}/{f(t * 1000, 0)}", Pd, nd=3, zrodlo="(6.4)")
    Mm = 0.5 * (M_g + M_d)
    em = (abs(Mm) + abs(M_w)) / N_m + einit if N_m > 0 else einit
    w.krok("Mimośród w połowie wysokości", "e_m = (M_md + M_w)/N_m + e_init", f"({f(abs(Mm), 2)} + {f(abs(M_w), 2)})/{f(N_m, 1)} + {f(einit, 4)}",
           em * 1000, "mm", nd=1, zrodlo="(6.7)")
    if sm <= p.mur_lambda_c:
        ek = 0.0
        w.krok("Mimośród od pełzania", "e_k = 0 (h_ef/t_ef ≤ λ_c)", "", 0.0, "mm", nd=1, zrodlo="6.1.2.2(2) [NZW NA]")
    else:
        ek = 0.002 * mur.fi_inf * sm * math.sqrt(t * em)
        w.krok("Mimośród od pełzania", "e_k = 0,002·φ_∞·(h_ef/t_ef)·√(t·e_m)", f"0,002·{f(mur.fi_inf, 1)}·{f(sm, 2)}·√({f(t, 3)}·{f(em, 4)})",
               ek * 1000, "mm", nd=1, zrodlo="(6.8)")
    emk = max(em + ek, emin)
    w.krok("Mimośród całkowity", "e_mk = e_m + e_k ≥ 0,05t", "", emk * 1000, "mm", nd=1, zrodlo="(6.6)")
    Pm, lam, u = phi_m(emk, t, hef, t, mur)
    w.krok("Współczynnik redukcyjny w połowie wysokości", "Φ_m = A₁·exp(−u²/2), A₁ = 1 − 2e_mk/t, u = (λ − 0,063)/(0,73 − 1,17e_mk/t)",
           f"λ = {f(lam, 3)}, A₁ = {f(1 - 2 * emk / t, 3)}, u = {f(u, 3)}", Pm, nd=3, zrodlo="zał. G (G.1–G.4), E = K_E·f_k")
    NRg, NRm, NRd = Pg * t * 1000 * fd, Pm * t * 1000 * fd, Pd * t * 1000 * fd
    w.krok("Nośność", "N_Rd = Φ·t·f_d", f"(góra / środek / dół) {f(Pg, 3)} / {f(Pm, 3)} / {f(Pd, 3)} · {f(t * 1000, 0)} mm · {f(fd, 2)} MPa",
           f"{f(NRg, 1)} / {f(NRm, 1)} / {f(NRd, 1)}", "kN/m", zrodlo="(6.2)")
    w.warunek("Nośność — przekrój górny", N_g, NRg, "kN/m", "(6.2), (6.4)", symbol_E="N_Ed", symbol_R="N_Rd")
    w.warunek("Nośność — połowa wysokości", N_m, NRm, "kN/m", "(6.2), zał. G", symbol_E="N_Ed", symbol_R="N_Rd")
    w.warunek("Nośność — przekrój dolny", N_d, NRd, "kN/m", "(6.2), (6.4)", symbol_E="N_Ed", symbol_R="N_Rd")
    w.h_ef, w.smuklosc, w.Phi_g, w.Phi_d, w.Phi_m = hef, sm, Pg, Pd, Pm
    w.N_Rd_g, w.N_Rd_m, w.N_Rd_d = NRg, NRm, NRd
    return w


def mimosrod_stropu(N_lewy: float, N_prawy: float, t: float, a_lewy: float | None = None, a_prawy: float | None = None) -> float:
    """Moment od mimośrodowego oparcia stropów na ścianie [kNm/m]: M = N_l·e_l − N_p·e_p, e = t/2 − a/3 [UPR]."""
    al = a_lewy if a_lewy is not None else t
    ap = a_prawy if a_prawy is not None else t
    return N_lewy * (t / 2 - al / 3) - N_prawy * (t / 2 - ap / 3)


def filarek(N_g: float, N_d: float, b: float, t: float, h: float, mur: Mur, M_g: float = 0.0, p: Parametry | None = None,
            nazwa: str = "Filarek międzyokienny") -> SciananN:
    """Filarek b × t (siły N [kN] — całkowite na filarek). Pole A = b·t < 0,3 m² → f_d/η_A (NA) [NZW η_A]."""
    A = b * t
    ea = eta_A(A)
    w = sciana_nosnosc(N_g / b, 0.5 * (N_g + N_d) / b, N_d / b, t, h, mur, M_g=M_g / b, p=p, A_red=1 / ea,
                       rho2=1.0, nazwa=nazwa)
    w.kroki.insert(0, w.kroki[0].__class__("Pole przekroju filarka", "A = b·t", f"{f(b, 2)}·{f(t, 2)}", A, "m²", nd=3))
    w.kroki.insert(1, w.kroki[0].__class__("Współczynnik η_A (A < 0,3 m²)", "η_A", "(NA; interpolacja wg R5-63)", ea, nd=2,
                                           zrodlo="NA do PN-EN 1996-1-1 [NZW]"))
    w.uwaga("Filarek liczony jako ściana podparta górą i dołem, ρ₂ = 1,0 (bezpiecznie); siły N na 1 m = N/b.")
    return w


@dataclass
class Docisk(Wynik):
    beta: float = 1.0
    N_Rdc: float = 0.0


def docisk(N_Edc: float, a1: float, l_b: float, t: float, h_c: float, mur: Mur, szer_opar: float | None = None,
           nazwa: str = "Docisk pod oparciem belki/nadproża") -> Docisk:
    """Docisk (PN-EN 1996-1-1 p. 6.1.3, elementy grupy 1): N_Rdc = β·A_b·f_d (6.9),
    β = (1 + 0,3·a₁/h_c)·(1,5 − 1,1·A_b/A_ef) (6.10), 1,0 ≤ β ≤ min(1,25 + a₁/(2h_c); 1,5), A_b/A_ef ≤ 0,45;
    A_ef = l_efm·t, l_efm — długość efektywna w połowie wysokości ściany (rozkład pod kątem 60° — rys. 6.2).
    a₁ — odległość krawędzi oparcia od końca ściany [m], l_b — długość oparcia [m], h_c — wysokość do poziomu obciążenia [m]."""
    w = Docisk(nazwa=nazwa)
    b_op = szer_opar if szer_opar is not None else t
    Ab = l_b * b_op
    spread = h_c / 2 * math.tan(math.radians(30))
    lefm = l_b + min(a1, spread) + spread
    Aef = lefm * t
    w.krok("Pole docisku", "A_b = l_b·b", f"{f(l_b, 3)}·{f(b_op, 3)}", Ab, "m²", nd=4)
    w.krok("Długość efektywna w połowie wysokości", "l_efm = l_b + 2·(h_c/2)·tg 30° (ograniczona a₁)", "", lefm, "m", nd=3,
           zrodlo="rys. 6.2")
    r = min(Ab / Aef, 0.45)
    beta = (1 + 0.3 * a1 / h_c) * (1.5 - 1.1 * r)
    beta = min(max(beta, 1.0), min(1.25 + a1 / (2 * h_c), 1.5))
    w.krok("Współczynnik zwiększający", "β = (1 + 0,3·a₁/h_c)·(1,5 − 1,1·A_b/A_ef)", f"(1 + 0,3·{f(a1, 2)}/{f(h_c, 2)})·(1,5 − 1,1·{f(r, 3)})",
           beta, nd=3, zrodlo="(6.10)")
    NR = beta * Ab * mur.f_d * 1000
    w.krok("Nośność na docisk", "N_Rdc = β·A_b·f_d", f"{f(beta, 3)}·{f(Ab, 4)}·{f(mur.f_d, 2)}·10³", NR, "kN", zrodlo="(6.9)")
    w.beta, w.N_Rdc = beta, NR
    w.warunek("Docisk", N_Edc, NR, "kN", "PN-EN 1996-1-1 (6.9)", symbol_E="N_Edc", symbol_R="N_Rdc")
    w.uwaga("Dodatkowo sprawdzić ścianę w połowie wysokości pod oparciem (6.1.3(4)) — obejmuje to sprawdzenie ściany/filarka.")
    return w


def sciana_wiatr(w_Ed: float, h: float, t: float, mur: Mur, l: float | None = None, sigma_d: float = 0.0,
                 p: Parametry | None = None, nazwa: str = "Ściana obciążona poziomo (wiatr)") -> Wynik:
    """Nośność na zginanie z płaszczyzny (6.3.1): M_Ed ≤ M_Rd = f_xd·Z, Z = t²/6 (na 1 m). Dolne oszacowanie pasmem
    jednokierunkowym: pionowym (h, f_xd1 + σ_d — 6.3.1(3)) lub poziomym (l, f_xd2), momenty q·L²/8 [UPR — zał. E daje
    wartości korzystniejsze dla ścian podpartych na 3–4 krawędziach]. f_xk1/f_xk2 — [NZW NA]."""
    p = p or Parametry()
    w = Wynik(nazwa=nazwa)
    Z = t * t / 6
    fxd1 = p.mur_f_xk1 / mur.gamma_M + sigma_d
    fxd2 = p.mur_f_xk2 / mur.gamma_M
    Mv = w_Ed * h * h / 8
    Rv = fxd1 * 1000 * Z
    w.krok("Wskaźnik wytrzymałości (1 m)", "Z = t²/6", f"{f(t, 3)}²/6", Z * 1e6, "cm³/m", nd=0)
    w.krok("Pasmo pionowe — moment", "M_Ed = w_Ed·h²/8", f"{f(w_Ed, 3)}·{f(h, 2)}²/8", Mv, "kNm/m", nd=3)
    w.krok("Pasmo pionowe — nośność", "M_Rd = (f_xk1/γ_M + σ_d)·Z", f"({f(p.mur_f_xk1, 2)}/{f(mur.gamma_M, 1)} + {f(sigma_d, 3)})·10³·{f(Z, 5)}",
           Rv, "kNm/m", nd=3, zrodlo="(6.15), 6.3.1(3) [NZW f_xk1]")
    etas = [(Mv / Rv if Rv > 0 else float("inf"), Mv, Rv, "pionowe")]
    if l:
        Mh = w_Ed * l * l / 8
        Rh = fxd2 * 1000 * Z
        w.krok("Pasmo poziome — moment", "M_Ed = w_Ed·l²/8", f"{f(w_Ed, 3)}·{f(l, 2)}²/8", Mh, "kNm/m", nd=3)
        w.krok("Pasmo poziome — nośność", "M_Rd = f_xk2/γ_M·Z", f"{f(p.mur_f_xk2, 2)}/{f(mur.gamma_M, 1)}·10³·{f(Z, 5)}", Rh,
               "kNm/m", nd=3, zrodlo="(6.15) [NZW f_xk2]")
        etas.append((Mh / Rh, Mh, Rh, "poziome"))
    eta, M, R, kier = min(etas)
    w.warunek(f"Zginanie z płaszczyzny (pasmo {kier} — dolne oszacowanie)", M, R, "kNm/m", "PN-EN 1996-1-1 6.3.1",
              nd=3, symbol_E="M_Ed", symbol_R="M_Rd")
    return w


def sciana_uproszczona_1996_3(N_Ed: float, t: float, h: float, mur: Mur, l_f: float = 0.0, rho2: float = 0.75,
                              nazwa: str = "Metoda uproszczona PN-EN 1996-3 (sprawdzenie porównawcze)") -> Wynik:
    """PN-EN 1996-3 p. 4.2.2: N_Rd = Φ_s·f_d·A, Φ_s = 0,85 − 0,0011·(h_ef/t_ef)², przy rozpiętości stropu l_f,ef > 4,25 m
    Φ_s ≤ 1,3 − l_f,ef/8 [NZW — warunki stosowalności 4.2.1.1 i wartości do potwierdzenia w normie]."""
    w = Wynik(nazwa=nazwa)
    hef = rho2 * h
    s = hef / t
    Ps = 0.85 - 0.0011 * s * s
    w.krok("Współczynnik redukcyjny", "Φ_s = 0,85 − 0,0011·(h_ef/t_ef)²", f"0,85 − 0,0011·{f(s, 2)}²", Ps, nd=3, zrodlo="PN-EN 1996-3 (4.3) [NZW]")
    if l_f > 4.25:
        Ps = min(Ps, 1.3 - l_f / 8)
        w.krok("Ograniczenie od rozpiętości stropu", "Φ_s ≤ 1,3 − l_f,ef/8", f"1,3 − {f(l_f, 2)}/8", Ps, nd=3, zrodlo="(4.4) [NZW]")
    NR = Ps * mur.f_d * t * 1000
    w.krok("Nośność", "N_Rd = Φ_s·f_d·t", f"{f(Ps, 3)}·{f(mur.f_d, 2)}·{f(t * 1000, 0)}", NR, "kN/m")
    w.warunek("Nośność (PN-EN 1996-3)", N_Ed, NR, "kN/m", "PN-EN 1996-3 4.2.2 [NZW]", symbol_E="N_Ed", symbol_R="N_Rd")
    return w


def sciana_luk(w_Ed: float, l_a: float, t: float, mur: Mur, nazwa: str = "Ściana obciążona poziomo — efekt przesklepienia (6.3.2)") -> Wynik:
    """Ściana wykonana szczelnie między podporami zdolnymi przenieść rozpór (stropy/wieńce): łuk trójprzegubowy w grubości
    ściany (PN-EN 1996-1-1 p. 6.3.2): q_lat,d = f_d·(t/l_a)² (6.20), rozpór N_ad = 1,5·f_d·t/10 (6.19); ugięcie łuku d_a
    pominięte dla l_a/t ≤ 25 [NZW — wzory z pamięci, potwierdzić w normie]."""
    w = Wynik(nazwa=nazwa)
    sm = l_a / t
    w.krok("Smukłość łuku", "l_a/t", f"{f(l_a, 2)}/{f(t, 3)}", sm, nd=1)
    q = mur.f_d * 1000 * (t / l_a) ** 2
    w.krok("Nośność na obciążenie poziome", "q_lat,d = f_d·(t/l_a)²", f"{f(mur.f_d, 2)}·10³·({f(t, 3)}/{f(l_a, 2)})²", q, "kN/m²",
           nd=2, zrodlo="(6.20) [NZW]")
    Nad = 1.5 * mur.f_d * 1000 * t / 10
    w.krok("Obliczeniowy rozpór łuku (przenoszony przez stropy/wieńce)", "N_ad = 1,5·f_d·t/10", "", Nad, "kN/m", nd=1,
           zrodlo="(6.19) [NZW]")
    w.warunek("Obciążenie poziome — przesklepienie", w_Ed, q, "kN/m²", "PN-EN 1996-1-1 6.3.2", nd=2, symbol_E="W_Ed",
              symbol_R="q_lat,d")
    if sm > 25:
        w.uwaga("l_a/t > 25 — uwzględnić ugięcie łuku d_a (6.3.2(3)).")
    return w
