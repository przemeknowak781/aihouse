"""Stolarka: U_w wg PN-EN ISO 10077-1:2017, przepuszczalność energii g, osłony (PN-EN ISO 52022-1, WT) i zacienienie.

* U_w = (A_g·U_g + A_f·U_f + l_g·Ψ_g)/(A_g + A_f) — PN-EN ISO 10077-1:2017 p. 6.2, wzór (1); geometria kwater
  jak w rdzeniu 3D (`lamela.ir`: kwatera okna ≤ 1,6 m, fix/HS ≤ 3,0 m, HS min. 2 kwatery) lub pole `kwatery`;
  U_g, U_f, Ψ_g, szerokości ram — z deklaracji (DoP) wyrobu; domyślnie DANE PRZYKŁADOWE (`dane/wyroby_przykladowe.yaml`);
* drzwi — U_D z deklaracji (PN-EN 14351-1);
* g osłony wg WT zał. 2 pkt 2.1.1–2.1.3: g = f_C·g_n ≤ 0,35 (lato); zwolnienia pkt 2.1.4: płaszczyzny N ± 45°,
  okna < 0,5 m², okna chronione elementem zacieniającym spełniającym pkt 2.1.1 [INT — wykazanie: g_n·F_sh,lato ≤ 0,35
  dla okresu VI–VIII z danych godzinowych TMY];
* g_tot z osłoną — PN-EN ISO 52022-1:2017 metoda uproszczona (wzory z EN 13363-1+A1):
  zewnętrzna: g_tot = τ_e,B·g + α_e,B·G/G₂ + τ_e,B·(1 − g)·G/G₁, G₁ = 5, G₂ = 10 W/(m²K), G = (1/U_g + 1/G₁ + 1/G₂)⁻¹;
  wewnętrzna: g_tot = g·(1 − g·ρ_e,B − α_e,B·G/G₂), G₂ = 30 W/(m²K), G = (1/U_g + 1/G₂)⁻¹  [NZW — wzory z literatury];
* zacienienie stałe (okapy — wysunięte płyty, lamele pionowe) — współczynnik F_sh miesięczny z danych godzinowych TMY
  Poznań i położenia Słońca (`lamela.sun`): promieniowanie bezpośrednie — cień geometryczny (okap skończony,
  lamele: przepuszczalność max(0, (s − b − h·|tg γ|)/s)), rozproszone nieba — izotropowe z czynnikiem widoku
  (okap nieskończony: sin φ_o), odbite od gruntu ρ_g = 0,2 [ZAŁ — model uproszczony zgodny z ideą PN-EN ISO 52016-1
  p. 6.5.13 / PN-EN ISO 13790 p. 11.4.4].
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from ..wspolne import (INT, NZW, Zalozenia, fmt, fmt_u, miesiace_pl, naglowek_raportu, ok, orientacja, tabela_md, wym,
                       wyrob, zaokr_znaczace)

# WT zał. 2 pkt 2.1.3 — f_C: {typ: {przepuszczalność: (wewnętrzna, zewnętrzna)}}
FC_WT = {
    "zaluzja_biala": {0.05: (0.25, 0.10), 0.1: (0.30, 0.15), 0.3: (0.45, 0.35)},
    "zaslona_biala": {0.5: (0.65, 0.55), 0.7: (0.80, 0.75), 0.9: (0.95, 0.95)},
    "zaslona_kolorowa": {0.1: (0.42, 0.17), 0.3: (0.57, 0.37), 0.5: (0.77, 0.57)},
    "zaslona_aluminiowa": {0.05: (0.20, 0.08)},
}
TYP_DOMYSLNY = {"okno": "okno_PVC_3sz", "fix": "fix_ALU_3sz", "drzwi_przesuwne_HS": "HS_ALU_3sz",
                "drzwi_zewn": "drzwi_zewn", "brama": "brama_segmentowa", "drzwi": "drzwi_dom_garaz"}
PRZEZROCZYSTE = ("okno", "fix", "drzwi_przesuwne_HS")


def f_c_wt(typ: str, polozenie: str, tau: float) -> float:
    """f_C z tabeli WT zał. 2 pkt 2.1.3 (najbliższa tabelaryczna przepuszczalność ≥ podanej)."""
    t = FC_WT[typ]
    klucze = sorted(t)
    k = next((x for x in klucze if x >= tau - 1e-9), klucze[-1])
    return t[k][1 if polozenie == "zewn" else 0]


def g_tot_uproszczona(g: float, U_g: float, tau_e: float, rho_e: float, polozenie: str = "zewn") -> float:
    """PN-EN ISO 52022-1:2017 (EN 13363-1) metoda uproszczona — g_tot oszklenia z osłoną [NZW]."""
    alfa = max(0.0, 1.0 - tau_e - rho_e)
    if polozenie == "zewn":
        G1, G2 = 5.0, 10.0
        G = 1.0 / (1.0 / U_g + 1.0 / G1 + 1.0 / G2)
        return tau_e * g + alfa * G / G2 + tau_e * (1 - g) * G / G1
    if polozenie == "wewn":
        G2 = 30.0
        G = 1.0 / (1.0 / U_g + 1.0 / G2)
        return g * (1 - g * rho_e - alfa * G / G2)
    return g


@dataclass
class DaneStolarki:
    symbol: str
    typ: str
    klucz: str = ""
    opis: str = ""
    U_g: float | None = None
    U_f: float | None = None
    psi_g: float | None = None
    b_f: float = 0.11
    b_s: float = 0.15
    g_n: float | None = None
    U_D: float | None = None
    klasa_szczelnosci: int | None = None
    status: str = ""
    zrodlo: str = ""


def dane_stolarki(symbol: str | None, typ: str, model_stolarka: dict | None = None) -> DaneStolarki:
    """Dane wyrobu: sekcja `stolarka.<symbol>` modelu (pola jak w wyroby_przykladowe.yaml, opcjonalnie `wyrob: <klucz>`)
    → wartości przykładowe wg typu otworu."""
    ms = (model_stolarka or {}).get(symbol or "", {}) if model_stolarka else {}
    klucz = ms.get("wyrob") or TYP_DOMYSLNY.get(typ, "okno_PVC_3sz")
    base = dict(wyrob("stolarka", klucz))
    base.update({k: v for k, v in ms.items() if k != "wyrob"})
    return DaneStolarki(symbol=symbol or "?", typ=typ, klucz=klucz, opis=base.get("opis", ""), U_g=base.get("U_g"),
                        U_f=base.get("U_f"), psi_g=base.get("psi_g"), b_f=float(base.get("b_f", 0.11)),
                        b_s=float(base.get("b_s", 0.15)), g_n=base.get("g_n"), U_D=base.get("U_D"),
                        klasa_szczelnosci=base.get("klasa_szczelnosci"),
                        status=base.get("status", "") if not ms else ("model" + (f"; {base.get('status')}" if base.get('status') else "")),
                        zrodlo=base.get("zrodlo", ""))


def liczba_kwater(typ: str, szer: float, kwatery: Any = None) -> int:
    if isinstance(kwatery, (int, float)) and kwatery >= 1:
        return int(kwatery)
    pane = {"okno": 1.6, "fix": 3.0, "drzwi_przesuwne_HS": 3.0}.get(typ, 1.6)
    return max(2 if typ == "drzwi_przesuwne_HS" else 1, math.ceil((szer - 1e-6) / pane))


@dataclass
class WynikOkno:
    symbol: str
    typ: str
    szer: float
    wys: float
    n_kw: int
    A_w: float
    A_g: float
    A_f: float
    l_g: float
    U_g: float | None
    U_f: float | None
    psi_g: float | None
    U_w: float
    g_n: float | None
    dane: DaneStolarki
    U_max: float | None = None
    U_cel: float | None = None
    rola: str = "okno"

    @property
    def C(self) -> float:
        """Udział oszklenia A_g/A_w (metodologia wzór (59): C_i)."""
        return self.A_g / self.A_w if self.A_w else 0.0

    @property
    def U_zaokr(self) -> float:
        return zaokr_znaczace(self.U_w, 2)

    @property
    def spelnia_WT(self):
        return None if self.U_max is None else self.U_zaokr <= self.U_max + 1e-9

    @property
    def spelnia_cel(self):
        return None if self.U_cel is None else self.U_zaokr <= self.U_cel + 1e-9


def u_okna(szer: float, wys: float, dane: DaneStolarki, *, n_kw: int | None = None, rola: str | None = None) -> WynikOkno:
    """PN-EN ISO 10077-1:2017 wzór (1). Rama obwodowa b_f, słupki między kwaterami b_s; próg HS/drzwi jak rama."""
    typ = dane.typ
    if typ in ("drzwi_zewn", "brama", "drzwi"):
        U = float(dane.U_D if dane.U_D is not None else 1.3)
        A = szer * wys
        r = rola or ("brama" if typ == "brama" else "drzwi")
        Umax, Ucel = (None, None)
        if r == "drzwi":
            Umax = wym("energia", "U_max_drzwi_zewn")
            Ucel = wym("energia", "U_cel_drzwi")
        return WynikOkno(dane.symbol, typ, szer, wys, 1, A, 0.0, A, 0.0, None, None, None, U, None, dane, Umax, Ucel, r)
    n = n_kw or liczba_kwater(typ, szer)
    wg = (szer - 2 * dane.b_f - (n - 1) * dane.b_s) / n
    hg = wys - 2 * dane.b_f
    if wg <= 0 or hg <= 0:
        raise ValueError(f"{dane.symbol}: ramy szersze niż otwór ({szer}×{wys}, {n} kwater)")
    A_w = szer * wys
    A_g = n * wg * hg
    l_g = n * 2 * (wg + hg)
    A_f = A_w - A_g
    U = (A_g * dane.U_g + A_f * dane.U_f + l_g * dane.psi_g) / A_w
    r = rola or "okno"
    Umax = wym("energia", "U_max_okno") if r == "okno" else None
    Ucel = wym("energia", "U_cel_okno") if r == "okno" else None
    return WynikOkno(dane.symbol, typ, szer, wys, n, A_w, A_g, A_f, l_g, dane.U_g, dane.U_f, dane.psi_g, U, dane.g_n,
                     dane, Umax, Ucel, r)


# --------------------------------------------------------------------------------------------------
# Zacienienie stałe (okap, lamele) — z danych godzinowych
# --------------------------------------------------------------------------------------------------
@dataclass
class Okap:
    wysieg: float             # P — wysunięcie krawędzi okapu przed płaszczyznę oszklenia [m]
    odstep: float             # G — od górnej krawędzi okna do spodu okapu [m]
    ext_lewa: float = 50.0    # przedłużenie poza lewą krawędź okna (patrząc z zewnątrz) [m]
    ext_prawa: float = 50.0


@dataclass
class Lamele:
    rozstaw: float            # s — rozstaw osiowy lamel [m]
    b: float                  # grubość lameli wzdłuż elewacji [m]
    h: float                  # głębokość lameli prostopadle do elewacji [m]
    opis: str = ""


def _tr_lamele(gamma: np.ndarray, L: Lamele) -> np.ndarray:
    return np.clip((L.rozstaw - L.b - L.h * np.abs(np.tan(np.clip(gamma, -1.55, 1.55)))) / L.rozstaw, 0.0, 1.0)


def _dif_lamele(L: Lamele) -> float:
    g = np.linspace(-math.pi / 2 + 1e-4, math.pi / 2 - 1e-4, 721)
    return float(np.trapezoid(_tr_lamele(g, L) * np.cos(g), g) / 2.0)


def zacienienie_miesieczne(azymut: float, szer: float, wys: float, *, okap: Okap | None = None,
                           lamele: Lamele | None = None, rho_g: float = 0.2) -> dict:
    """Miesięczny współczynnik zacienienia F_sh = Σ I_zacienione / Σ I_pełne (pionowe okno o azymucie `azymut`)
    z danych godzinowych TMY Poznań. Zwraca {"F_sh": [12], "F_sh_lato": (VI–VIII), "F_sh_zima": (X–IV)}."""
    from shapely.geometry import Polygon, box
    from ..energia.klimat import klimat_godzinowy
    k = klimat_godzinowy()
    az, el = k.pozycja_slonca()
    gam = np.radians(az - azymut)
    gam = (gam + math.pi) % (2 * math.pi) - math.pi
    elr = np.radians(el)
    cos_inc = np.cos(elr) * np.cos(gam)
    sin_el = np.sin(elr)
    beam = np.where((el > 2.0) & (cos_inc > 0), np.minimum(k.IDH / np.maximum(sin_el, 1e-3), 1100.0) * cos_inc, 0.0)
    dif = 0.5 * k.ISH
    gr = 0.5 * rho_g * k.ITH
    # okap: cień geometryczny (skończony okap) i czynnik widoku nieba
    f_ov = np.ones_like(beam)
    r_dif_ov = 1.0
    if okap is not None and okap.wysieg > 0:
        okno = box(0.0, 0.0, szer, wys)
        zo = wys + okap.odstep
        idx = np.nonzero(beam > 0)[0]
        for i in idx:
            s_n = cos_inc[i]                       # składowa normalna (ku zewnątrz) kierunku do Słońca (wersor)
            s_x = np.cos(elr[i]) * np.sin(gam[i])   # wzdłuż elewacji (w prawo patrząc od zewnątrz → − dla lewej?)
            s_z = sin_el[i]
            dx = -s_x * okap.wysieg / s_n
            dz = -s_z * okap.wysieg / s_n
            poly = Polygon([(-okap.ext_lewa, zo), (szer + okap.ext_prawa, zo), (szer + okap.ext_prawa + dx, zo + dz),
                            (-okap.ext_lewa + dx, zo + dz)])
            cien = poly.intersection(okno).area / (szer * wys) if poly.is_valid else 0.0
            f_ov[i] = 1.0 - cien
        zs = np.linspace(0.0, wys, 41)
        phi = np.arctan2(wys + okap.odstep - zs, okap.wysieg)
        r_dif_ov = float(np.mean(np.sin(phi)))
    f_lam = np.ones_like(beam)
    r_dif_lam = 1.0
    if lamele is not None:
        f_lam = _tr_lamele(gam, lamele)
        r_dif_lam = _dif_lamele(lamele)
    I0 = beam + dif + gr
    Ish = beam * f_ov * f_lam + dif * r_dif_ov * r_dif_lam + gr * r_dif_lam
    F = []
    for m in range(1, 13):
        s = k.M == m
        F.append(float(Ish[s].sum() / I0[s].sum()) if I0[s].sum() > 0 else 1.0)
    lato = np.isin(k.M, (6, 7, 8))
    zima = np.isin(k.M, (10, 11, 12, 1, 2, 3, 4))
    return {"F_sh": F, "F_sh_lato": float(Ish[lato].sum() / I0[lato].sum()),
            "F_sh_zima": float(Ish[zima].sum() / I0[zima].sum()), "r_dif_okap": r_dif_ov, "r_dif_lamele": r_dif_lam}


# --------------------------------------------------------------------------------------------------
# Sprawdzenie g wg WT
# --------------------------------------------------------------------------------------------------
@dataclass
class WynikG:
    id: str
    symbol: str
    azymut: float | None
    A: float
    g_n: float | None
    oslona: str | None
    f_C: float | None
    g_tot: float | None
    g: float | None
    F_sh_lato: float | None
    zwolnienie: str
    spelnia: bool | None
    metoda: str


def sprawdz_g(id_: str, symbol: str, azymut: float | None, A: float, g_n: float | None, U_g: float | None,
              oslona: str | None, F_sh_lato: float | None = None, nachylenie: float = 90.0) -> WynikG:
    """WT zał. 2 pkt 2.1.1–2.1.4 (rejestr W-247): g = f_C·g_n ≤ 0,35 dla okien E, S, W."""
    gmax = wym("energia", "g_c_max", 0.35)
    if g_n is None:
        g_n = wym("energia", "g_n_domyslne_potrojne", 0.5)
    amin = wym("energia", "g_okno_male_zwolnione_pow", 0.5)
    if nachylenie > 60 and azymut is not None and (azymut % 360 >= 315 or azymut % 360 <= 45):
        return WynikG(id_, symbol, azymut, A, g_n, oslona, None, None, None, F_sh_lato,
                      "orientacja N ± 45° (pkt 2.1.4)", True, "—")
    if A < amin:
        return WynikG(id_, symbol, azymut, A, g_n, oslona, None, None, None, F_sh_lato,
                      f"pole < {fmt(amin, 1)} m² (pkt 2.1.4)", True, "—")
    os_ = wyrob("oslony", oslona or "brak") or wyrob("oslony", "brak")
    f_C = g_tot = None
    metoda = ""
    if oslona and oslona != "brak" and os_:
        if os_.get("f_C_WT") is not None:
            f_C = float(os_["f_C_WT"])
            metoda = "f_C wg WT zał. 2 pkt 2.1.3"
        else:
            g_tot = g_tot_uproszczona(g_n, U_g or 0.5, float(os_["tau_e"]), float(os_["rho_e"]), os_.get("polozenie", "zewn"))
            f_C = g_tot / g_n
            metoda = f"f_C = g_tot/g_n, g_tot wg PN-EN ISO 52022-1 (metoda uproszczona) {NZW}"
        g = f_C * g_n
        if g <= gmax + 1e-9:
            return WynikG(id_, symbol, azymut, A, g_n, oslona, f_C, g_tot, g, F_sh_lato, "—", True, metoda)
    else:
        g = g_n
    # okap / lamele — element zacieniający (pkt 2.1.4) wykazany obliczeniowo
    if F_sh_lato is not None and F_sh_lato < 0.999:
        g_ef = (g if (oslona and oslona != "brak") else g_n) * F_sh_lato
        if g_ef <= gmax + 1e-9:
            return WynikG(id_, symbol, azymut, A, g_n, oslona, f_C, g_tot, g, F_sh_lato,
                          f"element zacieniający stały: g·F_sh,lato = {fmt(g_ef, 2)} ≤ {fmt(gmax, 2)} (pkt 2.1.4) {INT}",
                          True, metoda or "zacienienie stałe (TMY VI–VIII)")
    return WynikG(id_, symbol, azymut, A, g_n, oslona, f_C, g_tot, g, F_sh_lato, "—", g <= gmax + 1e-9,
                  metoda or "brak osłony")


# --------------------------------------------------------------------------------------------------
# Raport
# --------------------------------------------------------------------------------------------------
def raport_okna(okna: Sequence[WynikOkno], g_wyniki: Sequence[WynikG] = (), zacienienie: dict | None = None,
                zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu("Stolarka — U_w, g i ochrona przed przegrzewaniem",
                          "PN-EN ISO 10077-1:2017-10 p. 6.2 wzór (1); WT zał. 2 pkt 1.2 (U_max), pkt 2.1.1–2.1.4 (g ≤ 0,35); "
                          "PN-EN ISO 52022-1:2017 (g_tot, metoda uproszczona)",
                          ["U_w = (A_g·U_g + A_f·U_f + l_g·Ψ_g)/(A_g + A_f); g = f_C·g_n.",
                           "Dane wyrobów — z deklaracji właściwości użytkowych; w tej wersji DANE PRZYKŁADOWE typowych "
                           "wyrobów danej klasy (lub równoważne) — do zastąpienia danymi wybranego producenta."])]
    rows = []
    seen = set()
    for o in okna:
        key = (o.symbol, round(o.szer, 3), round(o.wys, 3))
        if key in seen:
            continue
        seen.add(key)
        if o.typ in ("drzwi_zewn", "brama", "drzwi"):
            rows.append([o.symbol, o.typ, f"{fmt(o.szer)}×{fmt(o.wys)}", "—", fmt(o.A_w), "—", "—", "—", "—",
                         f"U_D = {fmt(o.U_w, 2)}", fmt(o.U_max) if o.U_max else "bez wym.", ok(o.spelnia_WT)])
            continue
        rows.append([o.symbol, o.typ, f"{fmt(o.szer)}×{fmt(o.wys)}", o.n_kw, fmt(o.A_w), fmt(o.A_g), fmt(o.l_g),
                     f"{fmt(o.U_g)}/{fmt(o.U_f)}/{fmt(o.psi_g, 3)}", fmt(o.C, 2), fmt_u(o.U_w),
                     fmt(o.U_max) if o.U_max else "—", ok(o.spelnia_WT)])
    s.append(tabela_md(["Symbol", "Typ", "Wymiar [m]", "Kwatery", "A_w [m²]", "A_g [m²]", "l_g [m]",
                        "U_g/U_f/Ψ_g", "C = A_g/A_w", "U_w [W/(m²K)]", "U_max", "WT"], rows, "llllrrrlrrrl"))
    s.append("")
    dane = {}
    for o in okna:
        dane.setdefault(o.dane.klucz or o.symbol, o.dane)
    s.append("Dane wyrobów:")
    s.append("")
    for k, d in dane.items():
        s.append(f"* **{k}** — {d.opis}; {d.status} {('— ' + d.zrodlo) if d.zrodlo else ''}")
    s.append("")
    if g_wyniki:
        s.append("### Ochrona przed przegrzewaniem — g ≤ 0,35 (WT zał. 2 pkt 2.1)")
        s.append("")
        rows = []
        for g in g_wyniki:
            rows.append([g.id, g.symbol, orientacja(g.azymut) + (f" ({fmt(g.azymut, 0)}°)" if g.azymut is not None else ""),
                         fmt(g.A), fmt(g.g_n), g.oslona or "brak", fmt(g.f_C, 2), fmt(g.g, 2),
                         fmt(g.F_sh_lato, 2) if g.F_sh_lato is not None else "—", g.zwolnienie, ok(g.spelnia)])
        s.append(tabela_md(["Otwór", "Symbol", "Orientacja", "A [m²]", "g_n", "Osłona", "f_C", "g = f_C·g_n",
                            "F_sh,lato", "Zwolnienie / wykazanie", "Wynik"], rows, "lllrrlrrrll"))
        s.append("")
        met = sorted({g.metoda for g in g_wyniki if g.metoda and g.metoda != "—"})
        for mt in met:
            s.append(f"* {mt}")
        s.append("")
    if zacienienie:
        s.append("### Zacienienie stałe — współczynniki miesięczne F_sh (TMY Poznań, okap/lamele)")
        s.append("")
        rows = [[k] + [fmt(x, 2) for x in v["F_sh"]] + [fmt(v["F_sh_lato"], 2)] for k, v in zacienienie.items()]
        s.append(tabela_md(["Otwór"] + miesiace_pl() + ["VI–VIII"], rows))
        s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
