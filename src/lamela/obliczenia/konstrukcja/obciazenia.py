"""Oddziaływania i kombinacje (PN-EN 1990 + NA, PN-EN 1991-1-1/-1-3/-1-4 + NA).

* ciężary warstw przegród modelu: g_k = γ·d, γ = ρ·g/1000 [kN/m³] (ρ — gęstość materiału w modelu; żelbet —
  25 kN/m³ wg PN-EN 1991-1-1 zał. A, R5-25; pole ``ciezar`` materiału [kN/m³] ma pierwszeństwo);
* obciążenia użytkowe kat. A, schody, tarasy, dachy kat. H, ścianki działowe (PN-EN 1991-1-1 tabl. 6.1–6.2, 6.10,
  p. 6.3.1.2(8)) — wartości R5 3.3 / W-263;
* śnieg: dach płaski (μ₁, p. 5.3.2), zaspa przy uskoku (μ₂ = μ_s + μ_w, p. 5.3.6), przy attyce/przeszkodzie (p. 6.2),
  sytuacja wyjątkowa B2 (zał. B — B.3 uskoki, B.4 przeszkody) [NZW — wzory zał. B wg R5-38];
* wiatr: q_p(z) = c_e(z)·q_b (NA tabl. NA.3), c_pe ścian (tabl. 7.1) i dachu płaskiego z attyką (tabl. 7.2) [NZW — R5-45];
* kombinacje: STR/GEO 6.10a/6.10b (NA: mniej korzystne), EQU (tabl. A1.2(A)), wyjątkowa 6.11b, SLS: charakterystyczna,
  częsta, quasi-stała (6.14b–6.16b).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .wspolne import G_GRAV, BladDanych, Parametry, Wynik, f, tabela


# ==================================================================================================
# Ciężary własne warstw
# ==================================================================================================
def ciezar_materialu(mat, p: Parametry | None = None) -> tuple[float, str]:
    """Ciężar objętościowy γ [kN/m³] materiału modelu i opis jego pochodzenia."""
    p = p or Parametry()
    raw = getattr(mat, "raw", {}) or {}
    if raw.get("ciezar") is not None:
        return float(raw["ciezar"]), "γ z modelu (pole ciezar)"
    if (getattr(mat, "kreskowanie", "") or "").upper() == "ZELBET":
        return p.ciezar_zelbetu, "żelbet — PN-EN 1991-1-1 zał. A (24 + 1)"
    rho = getattr(mat, "rho", None)
    if rho is None:
        return 0.0, f"brak ρ materiału {getattr(mat, 'kod', '?')} — ciężar pominięty [DO UZUPEŁNIENIA]"
    return float(rho) * G_GRAV / 1000.0, f"ρ = {f(rho, 0)} kg/m³ × g"


@dataclass
class WarstwaObc:
    nazwa: str
    kod: str
    d: float           # m
    gamma: float       # kN/m³
    g_k: float         # kN/m²
    uwaga: str = ""


@dataclass
class ZestawienieStale:
    """Zestawienie obciążeń stałych warstw (na 1 m² rzutu)."""
    tytul: str
    warstwy: list = field(default_factory=list)

    @property
    def g_k(self) -> float:
        return sum(w.g_k for w in self.warstwy)

    def dodaj(self, nazwa, kod, d, gamma, uwaga=""):
        self.warstwy.append(WarstwaObc(nazwa, kod, d, gamma, d * gamma, uwaga))

    def dodaj_wartosc(self, nazwa, g_k, uwaga=""):
        self.warstwy.append(WarstwaObc(nazwa, "", 0.0, 0.0, g_k, uwaga))

    def md(self, p: Parametry | None = None) -> str:
        p = p or Parametry()
        rows = []
        for w in self.warstwy:
            wz = f"{f(w.d * 100, 1)} cm × {f(w.gamma, 2)} kN/m³" if w.d else (w.uwaga or "")
            rows.append([w.nazwa, wz, (w.g_k, 3), (p.gG_sup, 2), (w.g_k * p.gG_sup, 3), (p.xi * p.gG_sup, 2),
                         (w.g_k * p.xi * p.gG_sup, 3)])
        rows.append(["**Razem g_k**", "", (self.g_k, 3), "", (self.g_k * p.gG_sup, 3), "",
                     (self.g_k * p.xi * p.gG_sup, 3)])
        return tabela(["Warstwa", "Obliczenie", "g_k [kN/m²]", "γ_G (6.10a)", "g_d [kN/m²]", "ξγ_G (6.10b)",
                       "g_d [kN/m²]"], rows)


def zestawienie_przegrody(model, kod: str, p: Parametry | None = None, grubosc_konstr: float | None = None,
                          pomin_konstr: bool = False, tylko: str | None = None, tytul: str | None = None) -> ZestawienieStale:
    """Zestawienie ciężarów warstw przegrody modelu (``przegrody[kod]``). ``grubosc_konstr`` nadpisuje grubość warstwy
    konstrukcyjnej (np. płyta dachu z ``plyta.grubosc``); ``tylko`` = 'nad' | 'pod' — tylko warstwy nad/pod konstrukcją."""
    p = p or Parametry()
    prz = model.przegroda(kod)
    if prz is None:
        raise BladDanych(f"brak przegrody {kod}")
    z = ZestawienieStale(tytul or f"{kod} — {prz.nazwa}")
    k = prz.idx_konstr if prz.ma_oznaczona_konstr else None
    for i, w in enumerate(prz.warstwy):
        if tylko == "nad" and k is not None and i >= k:
            continue
        if tylko == "pod" and (k is None or i <= k):
            continue
        is_k = k is not None and i == k
        if is_k and pomin_konstr:
            continue
        mat = model.material(w.mat)
        gam, _ = ciezar_materialu(mat, p)
        d = grubosc_konstr if (is_k and grubosc_konstr is not None) else w.d
        nm = mat.nazwa if mat else w.mat
        if mat is not None and str((getattr(mat, "raw", None) or {}).get("funkcja") or "") == "substrat":
            nm += " — ciężar w stanie nasycenia wodą"          # dach zielony: substrat nasycony (obciążenie stałe)
        z.dodaj(nm, w.mat, d, gam, "warstwa konstrukcyjna" if is_k else "")
    return z


def ciezar_sciany_m2(model, kod: str, p: Parametry | None = None) -> tuple[float, ZestawienieStale]:
    """Ciężar ściany [kN/m²] (wszystkie warstwy przegrody)."""
    z = zestawienie_przegrody(model, kod, p)
    return z.g_k, z


# ==================================================================================================
# Obciążenia użytkowe (PN-EN 1991-1-1 + NA; R5 3.3, W-263)
# ==================================================================================================
@dataclass
class Uzytkowe:
    kategoria: str
    q_k: float
    Q_k: float
    psi: tuple
    opis: str
    zrodlo: str


def obciazenie_uzytkowe(rodzaj: str, p: Parametry | None = None) -> Uzytkowe:
    """rodzaj: 'strop' (kat. A), 'schody', 'taras' (balkon kat. A), 'dach' (kat. H), 'garaz' (kat. F)."""
    p = p or Parametry()
    r = rodzaj.lower()
    if r in ("strop", "a", "stropodach_uzytkowy"):
        return Uzytkowe("A", p.q_strop, p.Q_strop, p.psi_of("A"), "stropy mieszkalne (kat. A)",
                        "PN-EN 1991-1-1 tabl. 6.2 + NA; R5 3.3 [NZW NA — górna granica EN]")
    if r == "schody":
        return Uzytkowe("A", p.q_schody, p.Q_schody, p.psi_of("schody"), "schody (kat. A)", "PN-EN 1991-1-1 tabl. 6.2")
    if r in ("taras", "balkon"):
        return Uzytkowe("A", p.q_taras, p.Q_taras, p.psi_of("taras"), "taras/balkon (kat. A, I)",
                        "PN-EN 1991-1-1 tabl. 6.2, 6.9 (p. 6.3.4.1); R5 3.3")
    if r in ("dach", "h", "stropodach"):
        return Uzytkowe("H", p.q_dach_H, p.Q_dach_H, p.psi_of("H"), "dach bez dostępu (kat. H)",
                        "PN-EN 1991-1-1 tabl. 6.10 + NA; nie łączyć ze śniegiem i wiatrem (p. 3.3.2)")
    if r in ("garaz", "f"):
        return Uzytkowe("F", p.q_garaz, p.Q_garaz, p.psi_of("F"), "garaż (kat. F)", "PN-EN 1991-1-1 tabl. 6.8")
    raise BladDanych(f"nieznany rodzaj obciążenia użytkowego: {rodzaj}")


def zastepcze_dzialowe(g_liniowe: float) -> float | None:
    """Zastępcze obciążenie od ścianek działowych (PN-EN 1991-1-1 p. 6.3.1.2(8)): ≤ 1,0 kN/m → 0,5; ≤ 2,0 → 0,8;
    ≤ 3,0 → 1,2 kN/m²; cięższe — None (uwzględnić jako obciążenie liniowe, p. 6.3.1.2(9))."""
    if g_liniowe <= 1.0:
        return 0.5
    if g_liniowe <= 2.0:
        return 0.8
    if g_liniowe <= 3.0:
        return 1.2
    return None


# ==================================================================================================
# Śnieg (PN-EN 1991-1-3 + NA)
# ==================================================================================================
@dataclass
class Snieg(Wynik):
    """Obciążenie śniegiem: s1 — równomierne (przypadek (i)), s2 — maks. w zaspie (przypadek (ii)) [kN/m²],
    l_s — długość zaspy [m], profil(x) — obciążenie w odległości x od przeszkody."""
    mu1: float = 0.8
    mu2: float = 0.8
    s1: float = 0.0
    s2: float = 0.0
    l_s: float = 0.0
    b_zaspy: float = 0.0          # zasięg zaspy na dachu niższym (≤ l_s, obcięcie na krawędzi)
    wyjatkowa: bool = False

    def profil(self, x) -> np.ndarray:
        x = np.asarray(x, float)
        if self.l_s <= 0:
            return np.full_like(x, self.s1)
        base = 0.0 if self.wyjatkowa else self.s1
        return np.where(x <= self.l_s, base + (self.s2 - base) * np.clip(1 - x / self.l_s, 0, 1), base)


def snieg_dach_plaski(p: Parametry | None = None, alfa: float = 0.0) -> Snieg:
    """s = μ₁·C_e·C_t·s_k (5.7), μ₁ = 0,8 dla 0° ≤ α ≤ 30° (tabl. 5.2)."""
    p = p or Parametry()
    w = Snieg(nazwa="Śnieg — dach płaski (przypadek A, trwała sytuacja obliczeniowa)")
    if alfa > 30:
        mu1 = 0.8 * (60 - alfa) / 30 if alfa < 60 else 0.0
    else:
        mu1 = 0.8
    w.krok("Strefa 2, wartość charakterystyczna", "s_k", "", p.s_k, "kN/m²", zrodlo="PN-EN 1991-1-3 NA rys. NA.1; R5-30")
    w.krok("Współczynnik kształtu dachu", "μ₁", f"(α = {f(alfa, 1)}° ≤ 30°)", mu1, "", zrodlo="tabl. 5.2")
    s = mu1 * p.C_e * p.C_t * p.s_k
    w.krok("Obciążenie śniegiem", "s = μ₁·C_e·C_t·s_k", f"{f(mu1)}·{f(p.C_e)}·{f(p.C_t)}·{f(p.s_k)}", s, "kN/m²",
           nd=3, zrodlo="(5.7)")
    w.mu1 = w.mu2 = mu1
    w.s1 = w.s2 = s
    return w


def snieg_uskok(h: float, b1: float, b2: float, p: Parametry | None = None, alfa_gorny: float = 0.0) -> Snieg:
    """Zaspa na dachu przylegającym do wyższej budowli (PN-EN 1991-1-3 p. 5.3.6, rys. 5.7).

    h — różnica wysokości [m] (od powierzchni dachu niższego do górnej krawędzi wyższego), b1 — szerokość dachu
    wyższego, b2 — szerokość dachu niższego (prostopadle do uskoku) [m]."""
    p = p or Parametry()
    w = Snieg(nazwa=f"Śnieg — zaspa przy uskoku h = {f(h)} m (trwała sytuacja obliczeniowa)")
    mu_s = 0.0 if alfa_gorny <= 15 else 0.5 * 0.8   # zsuw z wyższego dachu (α > 15° — uproszczenie [UPR])
    w.krok("Współczynnik od zsuwania się śniegu z dachu wyższego", "μ_s", f"α = {f(alfa_gorny, 0)}° ≤ 15°" if alfa_gorny <= 15 else "",
           mu_s, zrodlo="p. 5.3.6(1)")
    mu_w_raw = (b1 + b2) / (2 * h)
    lim_g = p.gamma_snieg * h / p.s_k
    w.krok("Współczynnik od nawiewania", "μ_w = (b₁ + b₂)/(2h)", f"({f(b1)} + {f(b2)})/(2·{f(h)})", mu_w_raw, nd=3,
           zrodlo="(5.8)")
    w.krok("Ograniczenie", "μ_w ≤ γ·h/s_k", f"{f(p.gamma_snieg)}·{f(h)}/{f(p.s_k)}", lim_g, nd=3,
           zrodlo="(5.8); γ = 2 kN/m³")
    mu_w = min(max(min(mu_w_raw, lim_g), p.mu_w_min), p.mu_w_max)
    w.krok("Przyjęto (zakres 0,8 ≤ μ_w ≤ 4,0)", "μ_w", "", mu_w, nd=3, zrodlo="p. 5.3.6(1) uwaga 1 (wartość zalecana) [NZW NA]")
    mu2 = mu_s + mu_w
    w.krok("Współczynnik kształtu przy uskoku", "μ₂ = μ_s + μ_w", f"{f(mu_s)} + {f(mu_w, 3)}", mu2, nd=3)
    ls = min(max(2 * h, p.ls_min), p.ls_max)
    w.krok("Długość zaspy", "l_s = 2h (5 ≤ l_s ≤ 15 m)", f"2·{f(h)}", ls, "m", zrodlo="(5.9)")
    s1 = 0.8 * p.C_e * p.C_t * p.s_k
    s2 = mu2 * p.C_e * p.C_t * p.s_k
    w.krok("Obciążenie przy uskoku", "s₂ = μ₂·C_e·C_t·s_k", f"{f(mu2, 3)}·{f(p.C_e)}·{f(p.C_t)}·{f(p.s_k)}", s2, "kN/m²", nd=3)
    w.krok("Obciążenie poza zaspą (μ₁ = 0,8)", "s₁", "", s1, "kN/m²", nd=3)
    if b2 < ls:
        w.uwaga(f"b₂ = {f(b2)} m < l_s = {f(ls)} m — zaspa obcięta na krawędzi dachu niższego (p. 5.3.6(3)).")
    w.mu1, w.mu2, w.s1, w.s2, w.l_s, w.b_zaspy = 0.8, mu2, s1, s2, ls, min(b2, ls)
    return w


def snieg_attyka(h: float, p: Parametry | None = None) -> Snieg:
    """Zaspa przy attyce/przeszkodzie (PN-EN 1991-1-3 p. 6.2): μ₂ = γ·h/s_k, 0,8 ≤ μ₂ ≤ 2,0, l_s = 2h (5–15 m)."""
    p = p or Parametry()
    w = Snieg(nazwa=f"Śnieg — zaspa przy attyce h = {f(h)} m (trwała sytuacja obliczeniowa)")
    raw = p.gamma_snieg * h / p.s_k
    w.krok("Współczynnik kształtu przy przeszkodzie", "μ₂ = γ·h/s_k", f"{f(p.gamma_snieg)}·{f(h)}/{f(p.s_k)}", raw, nd=3,
           zrodlo="(6.1)")
    mu2 = min(max(raw, 0.8), p.mu_attyka_max)
    w.krok("Przyjęto (0,8 ≤ μ₂ ≤ 2,0)", "μ₂", "", mu2, nd=3, zrodlo="p. 6.2(2)")
    ls = min(max(2 * h, p.ls_min), p.ls_max)
    w.krok("Długość zaspy", "l_s = 2h (5 ≤ l_s ≤ 15 m)", f"2·{f(h)}", ls, "m", zrodlo="(6.2)")
    s1 = 0.8 * p.C_e * p.C_t * p.s_k
    s2 = mu2 * p.C_e * p.C_t * p.s_k
    w.krok("Obciążenie przy attyce", "s₂ = μ₂·C_e·C_t·s_k", f"{f(mu2, 3)}·{f(p.C_e)}·{f(p.C_t)}·{f(p.s_k)}", s2, "kN/m²", nd=3)
    w.mu1, w.mu2, w.s1, w.s2, w.l_s, w.b_zaspy = 0.8, mu2, s1, s2, ls, ls
    return w


def snieg_B2_uskok(h: float, b1: float, b2: float, p: Parametry | None = None) -> Snieg:
    """Sytuacja wyjątkowa B2 — zaspa przy wyższej budowli (PN-EN 1991-1-3 zał. B.3, wymagane przez NA; R5-38):
    μ₁ = min{2h/s_k; 2b/l_s; 8}, b = max(b₁, b₂), l_s = min(5h; b₁; 15 m); s = μ₁·s_k (bez C_e, C_t); rozkład trójkątny
    od μ₁ przy ścianie do 0 w odległości l_s. [NZW — wzory zał. B do potwierdzenia w tekście normy, N-12]"""
    p = p or Parametry()
    w = Snieg(nazwa=f"Śnieg — zaspa wyjątkowa B2 przy uskoku h = {f(h)} m (zał. B.3)", wyjatkowa=True)
    b = max(b1, b2)
    ls = min(5 * h, b1, p.ls_max)
    w.krok("Długość zaspy", "l_s = min(5h; b₁; 15 m)", f"min(5·{f(h)}; {f(b1)}; {f(p.ls_max, 0)})", ls, "m",
           zrodlo="zał. B.3 [NZW]")
    a1, a2 = 2 * h / p.s_k, 2 * b / ls
    mu = min(a1, a2, p.mu_B2_max)
    w.krok("Współczynnik kształtu", "μ₁ = min{2h/s_k; 2b/l_s; 8}", f"min{{{f(a1, 2)}; {f(a2, 2)}; {f(p.mu_B2_max, 0)}}}",
           mu, nd=3, zrodlo="zał. B.3 (B.2) [NZW]")
    s = mu * p.s_k
    w.krok("Obciążenie wyjątkowe", "s_Ad = μ₁·s_k", f"{f(mu, 3)}·{f(p.s_k)}", s, "kN/m²", nd=3, zrodlo="(4.2)")
    w.uwaga("Sytuacja wyjątkowa (PN-EN 1990 6.11b): γ = 1,0; [NZW] wzory zał. B wg R5-38 — potwierdzić w normie (N-12).")
    w.mu1, w.mu2, w.s1, w.s2, w.l_s, w.b_zaspy = 0.0, mu, 0.0, s, ls, min(b2, ls)
    return w


def snieg_B2_attyka(h: float, p: Parametry | None = None) -> Snieg | None:
    """Sytuacja wyjątkowa B2 przy attyce/przeszkodzie (zał. B.4): μ = min{2h/s_k; 5}, l_s = min(5h; 15 m), rozkład
    trójkątny; pominięcie przy h ≤ 1 m wg B4(2) po AC:2009 (interpretacja IB) — [NZW]. Zwraca None, gdy pominięto."""
    p = p or Parametry()
    if h <= p.B2_pomin_przeszkody_do_h:
        return None
    w = Snieg(nazwa=f"Śnieg — zaspa wyjątkowa B2 przy attyce h = {f(h)} m (zał. B.4)", wyjatkowa=True)
    mu = min(2 * h / p.s_k, 5.0)
    ls = min(5 * h, p.ls_max)
    w.krok("Współczynnik kształtu", "μ₁ = min{2h/s_k; 5}", f"min{{{f(2 * h / p.s_k)}; 5}}", mu, nd=3, zrodlo="zał. B.4 [NZW]")
    w.krok("Długość zaspy", "l_s = min(5h; 15 m)", f"min(5·{f(h)}; 15)", ls, "m", zrodlo="zał. B.4 [NZW]")
    w.mu2, w.s2, w.l_s, w.b_zaspy = mu, mu * p.s_k, ls, ls
    return w


# ==================================================================================================
# Wiatr (PN-EN 1991-1-4 + NA)
# ==================================================================================================
CE_NA = {"0": (3.0, 0.17, 1.0), "I": (2.8, 0.19, 1.0), "II": (2.3, 0.24, 2.0), "III": (1.9, 0.26, 5.0),
         "IV": (1.5, 0.29, 10.0)}     # c_e(z) = a·(z/10)^b, z_min — NA tabl. NA.3 (R5-43)


@dataclass
class Wiatr(Wynik):
    q_b: float = 0.0
    c_e: float = 0.0
    q_p: float = 0.0
    z: float = 0.0


def wiatr_qp(z: float, p: Parametry | None = None, kategoria: str | None = None) -> Wiatr:
    """Szczytowe ciśnienie prędkości q_p(z) = c_e(z)·q_b (NA tabl. NA.3), q_b = ½·ρ·v_b², v_b = c_dir·c_season·v_b,0."""
    p = p or Parametry()
    kat = (kategoria or p.kategoria_terenu).upper()
    if kat not in CE_NA:
        raise BladDanych(f"kategoria terenu {kat}?")
    a, b, zmin = CE_NA[kat]
    w = Wiatr(nazwa=f"Wiatr — szczytowe ciśnienie prędkości (teren kat. {kat}, z = {f(z)} m)")
    vb = p.c_dir * p.c_season * p.v_b0
    w.krok("Bazowa prędkość wiatru (strefa 1, A ≤ 300 m)", "v_b = c_dir·c_season·v_b,0",
           f"{f(p.c_dir)}·{f(p.c_season)}·{f(p.v_b0, 1)}", vb, "m/s", zrodlo="(4.1); NA tabl. NA.1")
    qb = 0.5 * p.rho_air * vb ** 2 / 1000.0
    w.krok("Ciśnienie prędkości bazowej", "q_b = ½·ρ·v_b²", f"0,5·{f(p.rho_air)}·{f(vb, 1)}²", qb, "kN/m²", nd=4,
           zrodlo="(4.10)")
    zz = max(z, zmin)
    ce = a * (zz / 10.0) ** b
    w.krok("Współczynnik ekspozycji", f"c_e(z) = {f(a, 1)}·(z/10)^{f(b, 2)}", f"{f(a, 1)}·({f(zz)}/10)^{f(b, 2)}", ce,
           nd=3, zrodlo=f"NA tabl. NA.3 (z_min = {f(zmin, 0)} m)")
    qp = ce * qb
    w.krok("Szczytowe ciśnienie prędkości", "q_p(z) = c_e(z)·q_b", f"{f(ce, 3)}·{f(qb, 4)}", qp, "kN/m²", nd=3,
           zrodlo="(4.8)")
    w.q_b, w.c_e, w.q_p, w.z = qb, ce, qp, z
    return w


# tabl. 7.1 — ściany pionowe budynków na rzucie prostokąta: h/d → {strefa: (c_pe,10, c_pe,1)}
_T71 = {5.0: {"A": (-1.2, -1.4), "B": (-0.8, -1.1), "C": (-0.5, -0.5), "D": (0.8, 1.0), "E": (-0.7, -0.7)},
        1.0: {"A": (-1.2, -1.4), "B": (-0.8, -1.1), "C": (-0.5, -0.5), "D": (0.8, 1.0), "E": (-0.5, -0.5)},
        0.25: {"A": (-1.2, -1.4), "B": (-0.8, -1.1), "C": (-0.5, -0.5), "D": (0.7, 1.0), "E": (-0.3, -0.3)}}
# tabl. 7.2 — dachy płaskie: h_p/h → {strefa: (c_pe,10, c_pe,1)} (0 = ostre krawędzie)
_T72 = {0.0: {"F": (-1.8, -2.5), "G": (-1.2, -2.0), "H": (-0.7, -1.2), "I": (0.2, -0.2)},
        0.025: {"F": (-1.6, -2.2), "G": (-1.1, -1.8), "H": (-0.7, -1.2), "I": (0.2, -0.2)},
        0.05: {"F": (-1.4, -2.0), "G": (-0.9, -1.6), "H": (-0.7, -1.2), "I": (0.2, -0.2)},
        0.10: {"F": (-1.2, -1.8), "G": (-0.8, -1.4), "H": (-0.7, -1.2), "I": (0.2, -0.2)}}


def _interp_tab(tab: dict, x: float) -> dict:
    ks = sorted(tab)
    x = min(max(x, ks[0]), ks[-1])
    for a, b in zip(ks[:-1], ks[1:]):
        if a <= x <= b:
            t = (x - a) / (b - a) if b > a else 0
            return {z: tuple(tab[a][z][i] + t * (tab[b][z][i] - tab[a][z][i]) for i in (0, 1)) for z in tab[a]}
    return dict(tab[ks[-1]])


def c_pe_pole(cpe10: float, cpe1: float, A: float) -> float:
    """c_pe dla pola A [m²] (PN-EN 1991-1-4 rys. 7.2): A ≤ 1 → c_pe,1; A ≥ 10 → c_pe,10; pomiędzy — log10."""
    if A <= 1:
        return cpe1
    if A >= 10:
        return cpe10
    return cpe1 - (cpe1 - cpe10) * math.log10(A)


@dataclass
class WiatrStrefy(Wynik):
    e: float = 0.0
    strefy: dict = field(default_factory=dict)      # strefa → (c_pe,10, c_pe,1, szerokość/opis)
    q_p: float = 0.0
    w_max_parcie: float = 0.0
    w_max_ssanie: float = 0.0


def wiatr_sciany(h: float, b: float, d: float, q_p: float, p: Parametry | None = None) -> WiatrStrefy:
    """Ciśnienie wiatru na ściany (PN-EN 1991-1-4 p. 7.2.2, tabl. 7.1) — b: wymiar prostopadły do wiatru, d: równoległy.
    Wynik: strefy A–E, e = min(b, 2h), oraz ciśnienie netto na ścianę w_e ± c_pi (7.2.9, c_pi = +0,2/−0,3)."""
    p = p or Parametry()
    w = WiatrStrefy(nazwa=f"Wiatr — ściany (b = {f(b)} m, d = {f(d)} m, h = {f(h)} m)")
    e = min(b, 2 * h)
    tab = _interp_tab(_T71, h / d)
    w.krok("Parametr stref", "e = min(b; 2h)", f"min({f(b)}; 2·{f(h)})", e, "m", zrodlo="rys. 7.5")
    w.krok("Smukłość", "h/d", f"{f(h)}/{f(d)}", h / d, nd=3, zrodlo="tabl. 7.1 (interpolacja liniowa)")
    for z, (c10, c1) in tab.items():
        w.strefy[z] = (c10, c1)
    cpi_p, cpi_s = p.c_pi
    parcie = q_p * (tab["D"][0] - cpi_s)
    ssanie = q_p * (tab["A"][0] - cpi_p)
    w.krok("Parcie netto (strefa D, c_pi = −0,3)", "w = q_p·(c_pe,D − c_pi)", f"{f(q_p, 3)}·({f(tab['D'][0])} + 0,3)",
           parcie, "kN/m²", nd=3, zrodlo="(5.1), (5.2); p. 7.2.9(6) uwaga 2")
    w.krok("Ssanie netto (strefa A, c_pi = +0,2)", "w = q_p·(c_pe,A − c_pi)", f"{f(q_p, 3)}·({f(tab['A'][0])} − 0,2)",
           ssanie, "kN/m²", nd=3)
    w.e, w.q_p, w.w_max_parcie, w.w_max_ssanie = e, q_p, parcie, ssanie
    w.uwaga("Wartości tabl. 7.1 — [NZW] (R5-45: odczytać z normy przed PT).")
    return w


def wiatr_dach_plaski(h: float, h_p: float, b: float, q_p: float, p: Parametry | None = None) -> WiatrStrefy:
    """Dach płaski z attyką (PN-EN 1991-1-4 p. 7.2.3, tabl. 7.2): strefy F (e/4 × e/10), G, H (do e/2), I; h_p — wysokość
    attyki ponad dachem, h — wysokość budynku (z attyką), b — wymiar prostopadły do wiatru."""
    p = p or Parametry()
    w = WiatrStrefy(nazwa=f"Wiatr — dach płaski (h_p/h = {f(h_p / h if h else 0, 3)})")
    e = min(b, 2 * h)
    r = h_p / h if h > 0 else 0.0
    tab = _interp_tab(_T72, r)
    w.krok("Parametr stref", "e = min(b; 2h)", f"min({f(b)}; 2·{f(h)})", e, "m", zrodlo="rys. 7.6")
    w.krok("Attyka", "h_p/h", f"{f(h_p)}/{f(h)}", r, nd=3, zrodlo="tabl. 7.2 (interpolacja)")
    for z, (c10, c1) in tab.items():
        w.strefy[z] = (c10, c1)
    ss = q_p * (tab["F"][0] - p.c_pi[0])
    w.krok("Ssanie netto w strefie F (c_pi = +0,2)", "w = q_p·(c_pe,10,F − c_pi)", f"{f(q_p, 3)}·({f(tab['F'][0])} − 0,2)",
           ss, "kN/m²", nd=3)
    w.krok("Ssanie netto w strefie H", "w = q_p·(c_pe,10,H − c_pi)", f"{f(q_p, 3)}·({f(tab['H'][0])} − 0,2)",
           q_p * (tab["H"][0] - p.c_pi[0]), "kN/m²", nd=3)
    w.e, w.q_p, w.w_max_ssanie, w.w_max_parcie = e, q_p, ss, q_p * (tab["I"][0] - p.c_pi[1])
    w.uwaga("Wartości tabl. 7.2 — [NZW] (R5-45). Dach żelbetowy: ssanie nie decyduje (ciężar własny ≫ ssanie); "
            "istotne dla balastu PV i obróbek attyk.")
    return w


# ==================================================================================================
# Kombinacje oddziaływań (PN-EN 1990 + NA)
# ==================================================================================================
@dataclass
class Oddz:
    """Oddziaływanie: rodzaj 'G' (stałe), 'Q' (zmienne), 'A' (wyjątkowe); kat — do ψ (A, H, S, W, schody, taras…);
    grupa — oddziaływania wzajemnie wykluczające się (np. 'dach': użytkowe H i śnieg)."""
    nazwa: str
    rodzaj: str = "Q"
    kat: str = "A"
    grupa: str = ""


@dataclass
class Kombinacja:
    nazwa: str
    wsp: dict                # nazwa oddziaływania → współczynnik
    typ: str = "STR"

    def opis(self) -> str:
        return " + ".join(f"{f(v, 3).rstrip('0').rstrip(',')}·{k}" for k, v in self.wsp.items() if v)


def kombinacje(oddz: list[Oddz], p: Parametry | None = None, typ: str = "STR", G_korzystne: bool = False) -> list[Kombinacja]:
    """Generator kombinacji (PN-EN 1990 + NA). typ: 'STR' (6.10a i 6.10b dla każdego wiodącego Q), 'EQU' (tabl. A1.2(A):
    1,10·G_dst + 1,5·Q_dst; G o rodzaju 'Gstb' ×0,90), 'char' (6.14b), 'czesta' (6.15b), 'quasi' (6.16b), 'wyj' (6.11b).
    Oddziaływania z tej samej ``grupy`` wykluczają się (np. śnieg i obciążenie użytkowe dachu kat. H — PN-EN 1991-1-1
    p. 3.3.2) — dla towarzyszących generowane są warianty. G_korzystne=True dodaje kombinacje z γ_G,inf = 1,0."""
    p = p or Parametry()
    G = [o for o in oddz if o.rodzaj in ("G", "Gstb")]
    Q = [o for o in oddz if o.rodzaj == "Q"]
    A = [o for o in oddz if o.rodzaj == "A"]
    out: list[Kombinacja] = []
    seen = set()

    def add(nazwa, wsp, t):
        key = tuple(sorted((k, round(v, 6)) for k, v in wsp.items() if v))
        if key in seen:
            return
        seen.add(key)
        out.append(Kombinacja(nazwa, wsp, t))

    def warianty_tow(excl: list):
        """Zbiory oddziaływań towarzyszących: z każdej grupy co najwyżej jedno (wszystkie warianty)."""
        free = [o for o in Q if o not in excl and not any(e.grupa and o.grupa == e.grupa for e in excl)]
        grupy: dict = {}
        solo = []
        for o in free:
            (grupy.setdefault(o.grupa, []) if o.grupa else solo).append(o)
        import itertools as _it
        wyb = [g for g in grupy.values()]
        if not wyb:
            return [solo]
        return [solo + list(c) for c in _it.product(*wyb)]

    leads = Q if Q else [None]
    idx = {"char": 0, "czesta": 2, "quasi": 2}
    for lead in leads:
        ln = lead.nazwa if lead else "—"
        excl = [lead] if lead else []
        for tow in warianty_tow(excl):
            if typ == "STR":
                wa = {g.nazwa: p.gG_sup for g in G}
                wb = {g.nazwa: p.xi * p.gG_sup for g in G}
                if lead:
                    wa[lead.nazwa] = p.gQ * p.psi_of(lead.kat)[0]
                    wb[lead.nazwa] = p.gQ
                for o in tow:
                    wa[o.nazwa] = wb[o.nazwa] = p.gQ * p.psi_of(o.kat)[0]
                add(f"6.10a (wiodące: {ln})", wa, "STR")
                add(f"6.10b (wiodące: {ln})", wb, "STR")
                if G_korzystne and lead:
                    wc = {g.nazwa: p.gG_inf for g in G}
                    wc[lead.nazwa] = p.gQ
                    add(f"6.10 G korzystne (wiodące: {ln})", wc, "STR")
            elif typ == "EQU":
                w = {g.nazwa: (p.EQU_gG_stb if g.rodzaj == "Gstb" else p.EQU_gG_dst) for g in G}
                if lead:
                    w[lead.nazwa] = p.EQU_gQ
                add(f"EQU (wiodące: {ln})", w, "EQU")
            elif typ in ("char", "czesta", "quasi"):
                w = {g.nazwa: 1.0 for g in G}
                if lead:
                    w[lead.nazwa] = {"char": 1.0, "czesta": p.psi_of(lead.kat)[1], "quasi": p.psi_of(lead.kat)[2]}[typ]
                for o in tow:
                    w[o.nazwa] = p.psi_of(o.kat)[idx[typ]]
                add(f"SLS {typ} (wiodące: {ln})", w, typ)
            elif typ == "wyj":
                for a in A:
                    if lead and lead.grupa and lead.grupa == a.grupa:
                        continue
                    w = {g.nazwa: 1.0 for g in G}
                    w[a.nazwa] = 1.0
                    if lead:
                        w[lead.nazwa] = p.psi_of(lead.kat)[1 if p.psi_wyjatkowa == "psi1" else 2]
                    for o in tow:
                        if not (o.grupa and o.grupa == a.grupa):
                            w[o.nazwa] = p.psi_of(o.kat)[2]
                    add(f"6.11b ({a.nazwa}; wiodące: {ln})", w, "wyj")
            else:
                raise BladDanych(f"typ kombinacji {typ}?")
    if typ == "STR":
        add("6.10a (tylko G)", {g.nazwa: p.gG_sup for g in G}, "STR")
    if typ == "wyj" and not out:
        for a in A:
            add(f"6.11b ({a.nazwa})", {**{g.nazwa: 1.0 for g in G}, a.nazwa: 1.0}, "wyj")
    return out


def obliczeniowe_powierzchniowe(g_k: float, q_k: float, psi0: float, p: Parametry | None = None) -> tuple[float, float, str]:
    """Obciążenie obliczeniowe (jedno oddziaływanie zmienne): max(6.10a, 6.10b) → (q_d, wartość z drugiego, nazwa)."""
    p = p or Parametry()
    a = p.gG_sup * g_k + p.gQ * psi0 * q_k
    b = p.xi * p.gG_sup * g_k + p.gQ * q_k
    return (a, b, "6.10a") if a >= b else (b, a, "6.10b")


def krok_obliczeniowe(w: Wynik, g_k: float, q_k: float, psi0: float, p: Parametry | None = None, sym: str = "q") -> float:
    """Dopisuje do wyniku kroki 6.10a/6.10b i zwraca obciążenie obliczeniowe (miarodajne)."""
    p = p or Parametry()
    a = p.gG_sup * g_k + p.gQ * psi0 * q_k
    b = p.xi * p.gG_sup * g_k + p.gQ * q_k
    w.krok("Kombinacja 6.10a", f"{sym}_d = γ_G·g_k + γ_Q·ψ₀·q_k", f"{f(p.gG_sup)}·{f(g_k, 3)} + {f(p.gQ)}·{f(psi0, 1)}·{f(q_k, 3)}",
           a, "kN/m²", nd=3, zrodlo="PN-EN 1990 (6.10a) + NA")
    w.krok("Kombinacja 6.10b", f"{sym}_d = ξ·γ_G·g_k + γ_Q·q_k", f"{f(p.xi)}·{f(p.gG_sup)}·{f(g_k, 3)} + {f(p.gQ)}·{f(q_k, 3)}",
           b, "kN/m²", nd=3, zrodlo="PN-EN 1990 (6.10b) + NA")
    return max(a, b)
