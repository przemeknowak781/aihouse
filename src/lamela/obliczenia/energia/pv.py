"""Instalacja fotowoltaiczna — produkcja miesięczna i autokonsumpcja przez systemy techniczne budynku (do EP).

Metodologia (Dz.U. 2015 poz. 376 ze zm., tab. 1 lp. 6 w brzmieniu Dz.U. 2023 poz. 697): energia słoneczna wytworzona
miejscowo — w = 0,00 dla części zapotrzebowania systemów technicznych (H, W, pomocnicze), którą pokrywa; energia oddana
do sieci nie obniża EP (rejestr W-241, R6-15). Brak wytycznych ministerialnych co do kroku bilansowania
(R6-15 — NIEZWERYFIKOWANE) ⇒ przyjęto **metodę miesięczną z współczynnikiem autokonsumpcji a_n** wyznaczonym
symulacją godzinową na typowym roku meteorologicznym Poznań:
  E_PV,sys,n = min(a_n·E_PV,n; E_el,sys,n),  a_n = Σ_h min(P_PV,h; P_sys,h + P_dom,h)·P_sys,h/(P_sys,h + P_dom,h) / Σ_h P_PV,h
(zachowawczo: energia PV zużywana jednocześnie dzielona proporcjonalnie między systemy techniczne i urządzenia
gospodarstwa domowego, które nie wchodzą do EP; bez magazynu energii; z opcjonalnym sterowaniem ładowania c.w.u.
w godzinach produkcji PV).
Produkcja: E_PV = P_p·H_pł·PR/(1 kW/m²), H_pł — napromieniowanie płaszczyzny modułów (TMY, interpolacja nachylenia
0°/30°/90° i azymutu), PR — współczynnik wydajności (domyślnie 0,80 [ZAŁ]).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..wspolne import wyrob
from .klimat import klimat_godzinowy, klimat_miesieczny


@dataclass
class DanePV:
    P_kWp: float
    azymut: float = 180.0
    nachylenie: float = 30.0
    PR: float = 0.80
    opis: str = ""
    zrodlo: str = ""


def dane_pv(cfg: dict | None) -> DanePV | None:
    """Z `energia.pv` modelu: {moduly, P_modul_Wp, azymut, nachylenie, PR} lub {P_kWp, …}; None — brak PV."""
    if cfg is None or cfg is False:
        return None
    base = wyrob("pv", "modul_430")
    if cfg is True:
        cfg = {}
    n = cfg.get("moduly", base.get("liczba", 15))
    P = cfg.get("P_kWp", n * cfg.get("P_modul_Wp", base.get("P_modul_Wp", 430)) / 1000.0)
    return DanePV(float(P), float(cfg.get("azymut", 180.0)), float(cfg.get("nachylenie", 30.0)),
                  float(cfg.get("PR", base.get("PR", 0.80))), f"{n} × {cfg.get('P_modul_Wp', base.get('P_modul_Wp'))} Wp",
                  base.get("zrodlo", ""))


def _I_godz(azymut: float, nachylenie: float) -> np.ndarray:
    k = klimat_godzinowy()
    if nachylenie <= 0:
        return k.ITH
    if nachylenie <= 30:
        f = nachylenie / 30.0
        return (1 - f) * k.ITH + f * k.I(azymut, 30)
    f = (nachylenie - 30.0) / 60.0
    return (1 - f) * k.I(azymut, 30) + f * k.I(azymut, 90)


def produkcja_godzinowa(pv: DanePV) -> np.ndarray:
    """Produkcja godzinowa [kWh] (8760)."""
    return pv.P_kWp * _I_godz(pv.azymut, pv.nachylenie) / 1000.0 * pv.PR


def produkcja_miesieczna(pv: DanePV) -> np.ndarray:
    """E_PV,n [kWh/mies.] z sum miesięcznych napromieniowania płaszczyzny (dane MIiR)."""
    k = klimat_miesieczny()
    if pv.nachylenie <= 30:
        f = pv.nachylenie / 30.0
        H = (1 - f) * k.irr["poziom"] + f * k.I(pv.azymut, 30)
    else:
        H = k.I(pv.azymut, pv.nachylenie)
    return pv.P_kWp * H * pv.PR


def profil_dom(E_rok: float = 2500.0) -> np.ndarray:
    """Profil godzinowy zużycia urządzeń gospodarstwa domowego (poza EP) [kWh] — założenie: obciążenie podstawowe
    + szczyt poranny 6–8 i wieczorny 17–22; skala do E_rok [ZAŁ]."""
    k = klimat_godzinowy()
    H = k.H
    w = np.full(len(H), 1.0)
    w[(H >= 6) & (H < 8)] += 1.5
    w[(H >= 17) & (H < 22)] += 2.5
    w[(H >= 11) & (H < 14)] += 0.5
    return w / w.sum() * E_rok


def profil_systemy(E_H_n: np.ndarray, E_W_n: np.ndarray, P_stale_W: float, *, sterowanie_cwu_pv: bool = True,
                   theta_bal: float = 16.0) -> np.ndarray:
    """Profil godzinowy energii elektrycznej systemów technicznych [kWh]: ogrzewanie ∝ max(0, θ_bal − θ_h) w miesiącu,
    c.w.u. — ładowanie 11–15 (sterowanie pod PV) albo 5–7 i 18–21, stałe (wentylatory, sterowniki) — równomiernie."""
    k = klimat_godzinowy()
    out = np.full(len(k.H), P_stale_W / 1000.0)
    for m in range(12):
        s = k.M == m + 1
        dh = np.maximum(0.0, theta_bal - k.DBT[s])
        if dh.sum() <= 0:
            dh = np.ones(s.sum())
        out[s] += E_H_n[m] * dh / dh.sum()
        hh = k.H[s]
        if sterowanie_cwu_pv:
            w = ((hh >= 11) & (hh < 15)).astype(float)
        else:
            w = (((hh >= 5) & (hh < 7)) | ((hh >= 18) & (hh < 21))).astype(float)
        out[s] += E_W_n[m] * w / w.sum()
    return out


def autokonsumpcja(pv: DanePV, E_H_n, E_W_n, P_stale_W: float, *, E_dom_rok: float = 2500.0,
                   sterowanie_cwu_pv: bool = True) -> dict:
    """Miesięczne współczynniki autokonsumpcji a_n (udział produkcji PV zużyty jednocześnie przez systemy techniczne)."""
    k = klimat_godzinowy()
    E_pv = produkcja_godzinowa(pv)
    sys_ = profil_systemy(np.asarray(E_H_n), np.asarray(E_W_n), P_stale_W, sterowanie_cwu_pv=sterowanie_cwu_pv)
    dom = profil_dom(E_dom_rok)
    tot = sys_ + dom
    self_ = np.minimum(E_pv, tot)
    self_sys = np.where(tot > 0, self_ * sys_ / np.maximum(tot, 1e-12), 0.0)
    a = []
    pokr = []
    for m in range(12):
        s = k.M == m + 1
        a.append(float(self_sys[s].sum() / E_pv[s].sum()) if E_pv[s].sum() > 0 else 0.0)
        pokr.append(float(self_sys[s].sum() / sys_[s].sum()) if sys_[s].sum() > 0 else 0.0)
    return {"a_n": a, "pokrycie_sys_n": pokr, "E_pv_rok": float(E_pv.sum()), "E_sys_rok": float(sys_.sum()),
            "E_self_sys_rok": float(self_sys.sum()), "E_self_dom_rok": float((self_ - self_sys).sum()),
            "E_dom_rok": E_dom_rok, "sterowanie_cwu_pv": sterowanie_cwu_pv,
            "a_rok": float(self_sys.sum() / E_pv.sum()) if E_pv.sum() else 0.0}
