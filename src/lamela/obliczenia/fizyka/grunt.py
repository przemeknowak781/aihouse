"""Przenoszenie ciepła przez grunt — podłoga na gruncie / płyta fundamentowa wg PN-EN ISO 13370:2017-09.

* wymiar charakterystyczny B' = A/(0,5·P) (p. 7.1 / 6.7.1 — A i P z wymiarów wewnętrznych; P — obwód eksponowany:
  ściany do powietrza zewnętrznego i do przestrzeni nieogrzewanych poza izolowaną kubaturą);
* grubość równoważna d_t = w + λ·(R_si + R_f + R_se), R_si = 0,17, R_se = 0,04 (p. 7.2);
* U podłogi: d_t < B' → U = 2λ/(π·B' + d_t)·ln(π·B'/d_t + 1); d_t ≥ B' → U = λ/(0,457·B' + d_t) (p. 7.2)
  [NZW — wzory z wyd. 2007, tożsame w wyd. 2017 wg literatury; w próbce normy dostępny tylko wzór (1) H_g = A·U + P·Ψ];
* izolacja krawędziowa (zał. B / D): ΔΨ = −λ/π·[ln(D/d_t + 1) − ln(D/(d_t + d') + 1)] (pozioma, D = szerokość)
  lub z 2D w miejsce D (pionowa, D = głębokość), d' = R'·λ, R' = R_n − d_n/λ; U' = U + 2ΔΨ/B';
* H_g = A·U + P·Ψ_wf (wzór (1));
* współczynniki okresowe (zał. C / A wyd. 2007): δ = √(3,15·10⁷·λ/(π·ρc)); H_pi = A·λ/d_t·√(2/((1 + δ/d_t)² + 1));
  H_pe = 0,37·P·λ·ln(δ/d_t + 1) (z izolacją krawędziową — z wagami e^(−D/δ)); miesięczny strumień
  Φ_m = H_g·(θ̄_i − θ̄_e) − H_pi·(θ̄_i − θ_i,m) + H_pe·(θ̄_e − θ_e,m−β), β = 1 mies. [NZW];
* dla EP (metodologia pkt 5.2.3.1.1 — „podstawowa metoda wg PN dot. projektowego obciążenia cieplnego”):
  H_tr,ig = f_g1·f_g2·G_w·A·U_equiv (PN-EN 12831:2006 p. 7.1.3 / PN-EN 12831-1:2017 p. 6.3.2.5),
  f_g1 = 1,45; f_g2 = (θ_int − θ_m,e)/(θ_int − θ_e); G_w = 1,0 (ZWG > 1 m pod podłogą) [NZW — NA];
* sprawdzenie izolacji obwodowej R ≥ 2,0 m²·K/W (WT zał. 2 pkt 1.4; rejestr W-246).
Grunt: kategoria wg PN-EN ISO 13370 tab. (λ, ρc): glina/pył 1,5 / 3,0·10⁶; piasek/żwir 2,0 / 2,0·10⁶;
skała 3,5 / 2,0·10⁶ [NZW].
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Sequence

from ..wspolne import (NZW, ZAL, Zalozenia, fmt, fmt_u, naglowek_raportu, ok, tabela_md, wym, wymaganie,
                       zaokr_znaczace, miesiace_pl, GODZINY_MIES)

GRUNTY = {"glina": (1.5, 3.0e6), "piasek": (2.0, 2.0e6), "skala": (3.5, 2.0e6)}


@dataclass
class IzolacjaKrawedziowa:
    typ: str            # 'pozioma' | 'pionowa'
    D: float            # szerokość (pozioma) lub głębokość poniżej poziomu terenu (pionowa) [m]
    d_n: float          # grubość izolacji [m]
    lam_n: float        # λ izolacji [W/(m·K)]
    opis: str = ""

    @property
    def R_n(self) -> float:
        return self.d_n / self.lam_n


@dataclass
class WynikGrunt:
    A: float
    P: float
    B: float
    w: float
    R_f: float
    lam: float
    rho_c: float
    d_t: float
    U0: float
    dpsi: float = 0.0
    d_prim: float = 0.0
    U: float = 0.0
    psi_wf: float = 0.0
    H_g: float = 0.0
    izolacja: IzolacjaKrawedziowa | None = None
    delta: float = 0.0
    H_pi: float = 0.0
    H_pe: float = 0.0
    f_g1: float = 1.45
    f_g2: float = 0.0
    G_w: float = 1.0
    H_g_12831: float = 0.0
    theta_int: float = 20.0
    theta_e: float = -18.0
    theta_me: float = 7.9
    wzor: str = ""
    U_max: float | None = None
    U_cel: float | None = None
    R_obwod_min: float | None = None
    uwagi: list[str] = field(default_factory=list)
    Phi_mies: list[float] | None = None     # ISO 13370 miesięczny strumień [W]

    @property
    def U_zaokr(self):
        return zaokr_znaczace(self.U, 2)

    @property
    def spelnia_WT(self):
        return None if self.U_max is None else self.U_zaokr <= self.U_max + 1e-9

    @property
    def spelnia_cel(self):
        return None if self.U_cel is None else self.U_zaokr <= self.U_cel + 1e-9

    @property
    def spelnia_obwodowa(self):
        if self.R_obwod_min is None:
            return None
        if self.izolacja is None:
            return None
        return self.izolacja.R_n >= self.R_obwod_min - 1e-9


def u_podloga_na_gruncie(A: float, P: float, w: float, R_f: float, lam: float = 2.0, *, Rsi: float = 0.17,
                         Rse: float = 0.04) -> tuple[float, float, float, str]:
    """PN-EN ISO 13370:2017 p. 7.2 — U podłogi na gruncie (bez izolacji krawędziowej). Zwraca (U, B', d_t, wzór)."""
    B = A / (0.5 * P)
    d_t = w + lam * (Rsi + R_f + Rse)
    if d_t < B:
        U = 2 * lam / (math.pi * B + d_t) * math.log(math.pi * B / d_t + 1)
        wz = "d_t < B': U = 2λ/(πB' + d_t)·ln(πB'/d_t + 1)"
    else:
        U = lam / (0.457 * B + d_t)
        wz = "d_t ≥ B': U = λ/(0,457·B' + d_t)"
    return U, B, d_t, wz


def dpsi_krawedziowa(d_t: float, lam: float, iz: IzolacjaKrawedziowa) -> tuple[float, float]:
    """PN-EN ISO 13370 zał. B (izolacja krawędziowa): (ΔΨ [W/(m·K)], d' [m])."""
    Rprim = iz.R_n - iz.d_n / lam
    dp = Rprim * lam
    D = iz.D if iz.typ == "pozioma" else 2 * iz.D
    dpsi = -lam / math.pi * (math.log(D / d_t + 1) - math.log(D / (d_t + dp) + 1))
    return dpsi, dp


def wspolczynniki_okresowe(A: float, P: float, d_t: float, lam: float, rho_c: float,
                           iz: IzolacjaKrawedziowa | None = None, d_prim: float = 0.0) -> tuple[float, float, float]:
    """(δ, H_pi, H_pe) dla podłogi na gruncie — PN-EN ISO 13370 zał. C (wzory wyd. 2007 zał. A) [NZW]."""
    delta = math.sqrt(3.15e7 * lam / (math.pi * rho_c))
    H_pi = A * lam / d_t * math.sqrt(2.0 / ((1 + delta / d_t) ** 2 + 1))
    if iz is None:
        H_pe = 0.37 * P * lam * math.log(delta / d_t + 1)
    else:
        D = iz.D if iz.typ == "pozioma" else 2 * iz.D
        ex = math.exp(-D / delta)
        H_pe = 0.37 * P * lam * ((1 - ex) * math.log(delta / (d_t + d_prim) + 1) + ex * math.log(delta / d_t + 1))
    return delta, H_pi, H_pe


def strumien_miesieczny(H_g: float, H_pi: float, H_pe: float, theta_i: Sequence[float], theta_e: Sequence[float],
                        beta: int = 1, alfa: int = 0) -> list[float]:
    """PN-EN ISO 13370 zał. C — miesięczny strumień ciepła przez grunt [W] z temperatur miesięcznych (przesunięcia
    fazowe α (wewn.), β (zewn.) w miesiącach) [NZW]."""
    ti_sr = sum(theta_i) / 12.0
    te_sr = sum(theta_e) / 12.0
    out = []
    for m in range(12):
        out.append(H_g * (ti_sr - te_sr) - H_pi * (ti_sr - theta_i[(m - alfa) % 12]) + H_pe * (te_sr - theta_e[(m - beta) % 12]))
    return out


def h_g_12831(A: float, U_equiv: float, theta_int: float, theta_e: float, theta_me: float, *, f_g1: float = 1.45,
              G_w: float = 1.0, psi_l: float = 0.0) -> tuple[float, float]:
    """PN-EN 12831:2006 p. 7.1.3 (PN-EN 12831-1:2017 p. 6.3.2.5): H_T,ig = f_g1·f_g2·(A·U_equiv)·G_w.
    Zwraca (H_T,ig [W/K], f_g2)."""
    f_g2 = (theta_int - theta_me) / (theta_int - theta_e)
    return f_g1 * f_g2 * (A * U_equiv) * G_w + psi_l, f_g2


def oblicz_grunt(A: float, P: float, w: float, R_f: float, *, grunt: str = "piasek", lam: float | None = None,
                 rho_c: float | None = None, izolacja: IzolacjaKrawedziowa | None = None, psi_wf: float = 0.0,
                 theta_int: float = 20.0, theta_e: float | None = None, theta_me: float | None = None,
                 G_w: float = 1.0, f_g1: float = 1.45, klimat_mies: Sequence[float] | None = None,
                 zal: Zalozenia | None = None) -> WynikGrunt:
    """Pełne obliczenie podłogi na gruncie: U (13370), izolacja krawędziowa, H_g, współczynniki okresowe, H_T,ig (12831)."""
    l0, rc0 = GRUNTY[grunt]
    lam = lam or l0
    rho_c = rho_c or rc0
    theta_e = wym("ogrzewanie", "theta_e", -18) if theta_e is None else theta_e
    theta_me = wym("ogrzewanie", "theta_me", 7.9) if theta_me is None else theta_me
    U0, B, d_t, wz = u_podloga_na_gruncie(A, P, w, R_f, lam)
    dpsi = dp = 0.0
    if izolacja is not None:
        dpsi, dp = dpsi_krawedziowa(d_t, lam, izolacja)
    U = U0 + 2 * dpsi / B
    H_g = A * U + P * psi_wf
    delta, H_pi, H_pe = wspolczynniki_okresowe(A, P, d_t, lam, rho_c, izolacja, dp)
    H12831, f_g2 = h_g_12831(A, U, theta_int, theta_e, theta_me, f_g1=f_g1, G_w=G_w)
    wm = wymaganie("energia", "U_max_podloga_na_gruncie")
    wc = wymaganie("energia", "U_cel_podloga")
    r = WynikGrunt(A=A, P=P, B=B, w=w, R_f=R_f, lam=lam, rho_c=rho_c, d_t=d_t, U0=U0, dpsi=dpsi, d_prim=dp, U=U,
                   psi_wf=psi_wf, H_g=H_g, izolacja=izolacja, delta=delta, H_pi=H_pi, H_pe=H_pe, f_g1=f_g1, f_g2=f_g2,
                   G_w=G_w, H_g_12831=H12831, theta_int=theta_int, theta_e=theta_e, theta_me=theta_me, wzor=wz,
                   U_max=wm.wartosc, U_cel=wc.wartosc, R_obwod_min=wym("energia", "R_izolacji_obwodowej_min", 2.0))
    if klimat_mies is not None:
        r.Phi_mies = strumien_miesieczny(H_g, H_pi, H_pe, [theta_int] * 12, klimat_mies)
    if izolacja is None:
        r.uwagi.append("brak zdefiniowanej izolacji obwodowej — wymaganie WT zał. 2 pkt 1.4 (R ≥ 2,0 m²K/W) do wykazania "
                       "(przy płycie fundamentowej: izolacja pod płytą ciągła z izolacją ściany/cokołu)")
    if zal:
        zal.dodaj(f"Grunt: {grunt} — λ = {fmt(lam, 1)} W/(m·K), ρc = {fmt(rho_c / 1e6, 1)} MJ/(m³·K) "
                  "(PN-EN ISO 13370 tab. kategorii gruntu; opinia geotechniczna przykładowa: piaski średnie)", NZW)
        zal.dodaj(f"f_g1 = {fmt(f_g1)}, G_w = {fmt(G_w, 2)} (ZWG ≈ 3,8 m p.p.t. > 1 m), θ_m,e = {fmt(theta_me, 1)} °C",
                  NZW, "PN-EN 12831:2006 p. 7.1.3 i NA; rejestr W-150")
    return r


def raport_grunt(r: WynikGrunt, nazwa: str = "Podłoga na gruncie", zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu(f"Przenikanie ciepła przez grunt — {nazwa} (PN-EN ISO 13370:2017)",
                          "PN-EN ISO 13370:2017-09 p. 5.2 wzór (1), p. 7 (podłoga na gruncie), zał. B/C [NZW — wzory "
                          "wg wyd. 2007]; PN-EN 12831:2006 p. 7.1.3 (H_T,ig); WT zał. 2 pkt 1.1 i 1.4")]
    rows = [["A (pole podłogi, wymiary wewn.)", fmt(r.A), "m²"], ["P (obwód eksponowany)", fmt(r.P), "m"],
            ["B' = A/(0,5·P)", fmt(r.B, 3), "m"], ["w (grubość ścian zewn.)", fmt(r.w, 3), "m"],
            ["R_f (warstwy podłogi)", fmt(r.R_f, 3), "m²K/W"], ["λ gruntu", fmt(r.lam, 2), "W/(m·K)"],
            ["d_t = w + λ(R_si + R_f + R_se)", fmt(r.d_t, 3), "m"], ["wzór", r.wzor, ""],
            ["U₀ (bez izolacji krawędziowej)", fmt(r.U0, 4), "W/(m²K)"]]
    if r.izolacja:
        iz = r.izolacja
        rows += [[f"izolacja krawędziowa {iz.typ}: D = {fmt(iz.D)} m, d_n = {fmt(iz.d_n * 100, 0)} cm, λ_n = {fmt(iz.lam_n, 3)}",
                  f"R_n = {fmt(iz.R_n, 2)}", "m²K/W"],
                 ["d' = (R_n − d_n/λ)·λ", fmt(r.d_prim, 3), "m"], ["ΔΨ (zał. B)", fmt(r.dpsi, 4), "W/(m·K)"]]
    rows += [["U = U₀ + 2ΔΨ/B'", fmt(r.U, 4), "W/(m²K)"], ["Ψ_wf (złącze ściana–podłoga)", fmt(r.psi_wf, 3), "W/(m·K)"],
             ["H_g = A·U + P·Ψ_wf", fmt(r.H_g, 2), "W/K"], ["δ (głębokość wnikania)", fmt(r.delta, 2), "m"],
             ["H_pi", fmt(r.H_pi, 2), "W/K"], ["H_pe", fmt(r.H_pe, 2), "W/K"],
             ["f_g2 = (θ_int − θ_m,e)/(θ_int − θ_e)", fmt(r.f_g2, 3), "—"],
             ["H_T,ig = f_g1·f_g2·A·U·G_w (do EP i obciążenia cieplnego)", fmt(r.H_g_12831, 2), "W/K"]]
    s.append(tabela_md(["Wielkość", "Wartość", "Jedn."], rows, "lrl"))
    s.append("")
    s.append(f"**U_equiv = {fmt_u(r.U)} W/(m²K)** — wymaganie WT U ≤ {fmt(r.U_max)} ({ok(r.spelnia_WT)}), cel ≤ "
             f"{fmt(r.U_cel)} ({ok(r.spelnia_cel)}).")
    if r.izolacja:
        s.append(f"Izolacja obwodowa: R_n = {fmt(r.izolacja.R_n, 2)} m²K/W ≥ {fmt(r.R_obwod_min, 1)} "
                 f"({ok(r.spelnia_obwodowa)}) — WT zał. 2 pkt 1.4 (W-246).")
    if r.Phi_mies:
        s.append("")
        s.append("Miesięczny strumień ciepła przez grunt (PN-EN ISO 13370 zał. C, θ_i = const) [NZW]:")
        s.append("")
        s.append(tabela_md(["Miesiąc"] + miesiace_pl(), [["Φ_m [W]"] + [fmt(x, 0) for x in r.Phi_mies],
                                                         ["Q [kWh]"] + [fmt(x * h / 1000, 0) for x, h in zip(r.Phi_mies, GODZINY_MIES)]]))
    for u in r.uwagi:
        s.append(f"* {u}")
    s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
