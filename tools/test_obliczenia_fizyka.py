#!/usr/bin/env python3
"""Testy biblioteki obliczeń fizyki budowli i charakterystyki energetycznej (`lamela.obliczenia`).

Uruchomienie:
    PYTHONPATH=src python3 tools/test_obliczenia_fizyka.py            # testy + demo do projekt/08_obliczenia/demo_test/
    PYTHONPATH=src python3 tools/test_obliczenia_fizyka.py --bez-demo # tylko testy
Funkcje test_* są zgodne z pytest. Przykłady jednostkowe mają wartości oczekiwane policzone ręcznie (komentarze).
Gdy istnieje model/budynek.yaml (+ dzialka.yaml), wykonywany jest dodatkowo pełny łańcuch obliczeń dla tego modelu
(tylko odczyt; wyniki do build/test/obliczenia_budynek/).
"""
from __future__ import annotations

import copy
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.model import Model, load_model  # noqa: E402
from lamela.obliczenia.energia import ep as EP  # noqa: E402
from lamela.obliczenia.energia.klimat import klimat_godzinowy, klimat_miesieczny, p_sat  # noqa: E402
from lamela.obliczenia.energia.obciazenie_cieplne import obciazenie_cieplne  # noqa: E402
from lamela.obliczenia.energia.obudowa import oblicz_obudowe  # noqa: E402
from lamela.obliczenia.energia.wentylacja import bilans_wentylacji  # noqa: E402
from lamela.obliczenia.fizyka import grunt as G  # noqa: E402
from lamela.obliczenia.fizyka import kondensacja as KD  # noqa: E402
from lamela.obliczenia.fizyka import mostki as MB  # noqa: E402
from lamela.obliczenia.fizyka import okna as OK  # noqa: E402
from lamela.obliczenia.fizyka.u_przegrody import (PoprawkiU, oblicz_u, u_klin_prostokat,  # noqa: E402
                                                   u_klin_trojkat_max_w_wierzcholku, u_klin_trojkat_min_w_wierzcholku,
                                                   u_klin_wielobok)
from lamela.obliczenia.fizyka.warstwy import sprawdz_ciaglosc  # noqa: E402
from lamela.obliczenia.raport import oblicz_wszystko, zapisz_raporty  # noqa: E402

B_TEST = ROOT / "model" / "test" / "dom_testowy.yaml"
D_TEST = ROOT / "model" / "test" / "dzialka_testowa.yaml"
DEMO = ROOT / "projekt" / "08_obliczenia" / "demo_test"
B_DOCEL = ROOT / "model" / "budynek.yaml"
D_DOCEL = ROOT / "model" / "dzialka.yaml"

MAT = {"TG": {"nazwa": "Tynk gipsowy", "lambda": 0.40, "mu": 10, "kreskowanie": "TYNK"},
       "SIL": {"nazwa": "Silikat", "lambda": 0.77, "mu": 15, "kreskowanie": "MUR_SILIKAT"},
       "EPS": {"nazwa": "Styropian EPS 031", "lambda": 0.031, "mu": 30, "kreskowanie": "IZOL_TWARDA"},
       "TS": {"nazwa": "Tynk silikonowy", "lambda": 0.70, "mu": 60, "kreskowanie": "TYNK"},
       "GK": {"nazwa": "Płyta GK", "lambda": 0.25, "mu": 8, "kreskowanie": "PLYTA_GK"},
       "MW": {"nazwa": "Wełna mineralna", "lambda": 0.035, "mu": 1, "kreskowanie": "IZOL_MIEKKA"},
       "KVH": {"nazwa": "Drewno KVH", "lambda": 0.13, "mu": 50, "kreskowanie": "DREWNO_POPRZ"},
       "OSB": {"nazwa": "Płyta OSB", "lambda": 0.13, "mu": 200, "kreskowanie": "PLYTA_DREWNOPOCHODNA"},
       "ZB": {"nazwa": "Żelbet", "lambda": 2.3, "mu": 130, "kreskowanie": "ZELBET"},
       "PAR": {"nazwa": "Paroizolacja bitumiczna", "lambda": 0.23, "mu": 50000, "kreskowanie": "PAROIZOLACJA"},
       "PIR": {"nazwa": "Płyty PIR", "lambda": 0.022, "mu": 60, "kreskowanie": "IZOL_PIR"},
       "EPDM": {"nazwa": "Membrana EPDM", "lambda": 0.25, "mu": 75000, "kreskowanie": "IZOL_PRZECIWWODNA"},
       "XPS": {"nazwa": "XPS", "lambda": 0.035, "mu": 150, "kreskowanie": "IZOL_XPS"},
       "SUB": {"nazwa": "Substrat dachu zielonego", "lambda": 0.6, "mu": 2, "kreskowanie": "HUMUS"}}


def close(a, b, tol, msg=""):
    assert abs(a - b) <= tol, f"{msg}: {a!r} ≠ {b!r} (tol {tol})"


# --------------------------------------------------------------------------------------------------
# Jednostkowe — PN-EN ISO 6946
# --------------------------------------------------------------------------------------------------
def test_u_sciana_warstwowa_reczne():
    """SZ1 modelu testowego: R_T = 0,13 + 0,0375 + 0,233766 + 6,451613 + 0,01 + 0,04 = 6,902879;
    U0 = 0,144867; ΔU_g = 0,01·(6,451613/6,902879)² = 0,008735; ΔU_f = 6·0,002 = 0,012; U_c = 0,165602."""
    ws = [{"mat": "TG", "d": 0.015}, {"mat": "SIL", "d": 0.18}, {"mat": "EPS", "d": 0.20}, {"mat": "TS", "d": 0.007}]
    r = oblicz_u(ws, MAT, rola="sciana_zewn", poprawki=PoprawkiU(1, {"n_f": 6, "chi_p": 0.002}))
    close(r.R_T, 6.902879, 1e-6, "R_T")
    close(r.U0, 0.144867, 1e-6, "U0")
    close(r.dU_g, 0.008735, 1e-6, "ΔU_g")
    close(r.dU_f, 0.012, 1e-12, "ΔU_f")
    close(r.U_c, 0.165602, 1e-6, "U_c")
    assert r.U_zaokr == 0.17 and r.spelnia_WT and not r.spelnia_cel


def test_u_metoda_kresow_ruszt():
    """Ściana szkieletowa: GK 12,5 mm (λ 0,25) | wełna 150 mm (λ 0,035) z ruszt. 15 % (λ 0,13) | OSB 12 mm (λ 0,13).
    Kres górny: R_a = 0,13+0,05+4,285714+0,092308+0,04 = 4,598022; R_b = 0,13+0,05+1,153846+0,092308+0,04 = 1,466154;
    R' = 1/(0,85/4,598022 + 0,15/1,466154) = 3,482262. Kres dolny: λ'' = 0,04925 → R'' = 3,357993.
    R_T = 3,420127; e = 1,817 %; U = 0,292387."""
    ws = [{"mat": "GK", "d": 0.0125},
          {"mat": "MW", "d": 0.15, "frakcje": [{"mat": "MW", "udzial": 0.85}, {"mat": "KVH", "udzial": 0.15}]},
          {"mat": "OSB", "d": 0.012}]
    r = oblicz_u(ws, MAT, rola="sciana_zewn")
    close(r.R_gorny, 3.482262, 2e-5, "R'")
    close(r.R_dolny, 3.357993, 2e-5, "R''")
    close(r.R_T, 3.420127, 2e-5, "R_T")
    close(r.blad_wzgl, 0.01817, 2e-4, "e")
    close(r.U0, 0.292387, 5e-6, "U")


def test_u_pustki_i_wentylowana():
    """Pustka niewentylowana 50 mm poziomo: R = 0,18 (tab. 8); dobrze wentylowana: warstwy zewn. pominięte, R_se = R_si."""
    ws = [{"mat": "TG", "d": 0.015}, {"mat": "SIL", "d": 0.18}, {"mat": "MW", "d": 0.15},
          {"mat": None, "d": 0.05, "pustka": "nw"}, {"mat": "SIL", "d": 0.12}]
    r = oblicz_u(ws, MAT, rola="sciana_zewn")
    close(next(x.R for x in r.warstwy if x.rodzaj == "pustka_nw"), 0.18, 1e-9, "R pustki")
    ws[3]["pustka"] = "dw"
    r2 = oblicz_u(ws, MAT, rola="sciana_zewn")
    exp = 0.13 + 0.015 / 0.40 + 0.18 / 0.77 + 0.15 / 0.035 + 0.13      # R_se = R_si = 0,13
    close(r2.R_T, exp, 1e-9, "R_T went.")
    assert r2.warstwy[-1].rodzaj == "pominieta"


def test_u_dach_odwrocony_dUr():
    """Dach odwrócony (XPS nad EPDM): ΔU_r = p·f·x·(R_1/R_T)², p = 1,4, f·x = 0,04."""
    ws = [{"mat": "XPS", "d": 0.20}, {"mat": "EPDM", "d": 0.002}, {"mat": "ZB", "d": 0.20}]
    r = oblicz_u(ws, MAT, rola="dach", poprawki=PoprawkiU(0, None, {"p": 1.4, "fx": 0.04}))
    R1 = 0.20 / 0.035
    RT = 0.10 + 0.20 / 2.3 + 0.002 / 0.25 + R1 + 0.04
    close(r.R_T, RT, 1e-9, "R_T")
    close(r.dU_r, 1.4 * 0.04 * (R1 / RT) ** 2, 1e-9, "ΔU_r")


def test_klin_zal_C():
    """Zał. C: całkowanie numeryczne = wzory analityczne (prostokąt C.3, trójkąty C.4/C.5); granica R1→0: U → 1/R0."""
    R0, lam, i = 5.0, 0.022, 0.02
    R1 = i * 10.0 / lam
    a = u_klin_prostokat(R0, R1)
    n = u_klin_wielobok([[0, 0], [10, 0], [10, 8], [0, 8]], R0, lam, d_add_fn=lambda x, y: i * x, krok=0.05)
    close(n["U_sr"], a, 2e-4 * a, "prostokąt")
    tri = [[0, 0], [10, 0], [5, 8]]
    dmax = 0.16
    n4 = u_klin_wielobok(tri, R0, lam, d_add_fn=lambda x, y: dmax * y / 8.0, krok=0.02)
    close(n4["U_sr"], u_klin_trojkat_max_w_wierzcholku(R0, dmax / lam), 3e-3 * n4["U_sr"], "trójkąt C.4")
    n5 = u_klin_wielobok(tri, R0, lam, d_add_fn=lambda x, y: dmax * (1 - y / 8.0), krok=0.02)
    close(n5["U_sr"], u_klin_trojkat_min_w_wierzcholku(R0, dmax / lam), 3e-3 * n5["U_sr"], "trójkąt C.5")
    close(u_klin_prostokat(R0, 1e-9), 1 / R0, 1e-9, "granica")
    # ciągłość szereg (x < 1e-4) / wzór pełny: przyrost = pochodna·Δx, dU/dx = −1/(3R0) (C.4), −2/(3R0) (C.5)
    for f, k in ((u_klin_trojkat_max_w_wierzcholku, 1 / 3), (u_klin_trojkat_min_w_wierzcholku, 2 / 3)):
        close(f(R0, R0 * 0.99e-4) - f(R0, R0 * 1.01e-4), k / R0 * 2e-6, 2e-10, f.__name__)


# --------------------------------------------------------------------------------------------------
# PN-EN ISO 13370
# --------------------------------------------------------------------------------------------------
def test_grunt_reczne():
    """A = 100, P = 40 → B' = 5; w = 0,3; R_f = 0,5; λ = 2: d_t = 1,72 < B' → U = 4/(5π + 1,72)·ln(5π/1,72 + 1)
    = 0,229516·2,315751 = 0,531503. Izolacja pionowa D = 1,0 m, d_n = 0,10 m, λ_n = 0,035: R_n = 2,857143,
    d' = (2,857143 − 0,05)·2 = 5,614286, ΔΨ = −(2/π)·[ln(2/1,72 + 1) − ln(2/(1,72 + 5,614286) + 1)]
    = −0,63662·(0,771399 − 0,241135) = −0,337578; U' = U + 2ΔΨ/B' = 0,396472.
    Dobrze izolowana: R_f = 4,0 → d_t = 8,72 ≥ B' → U = 2/(0,457·5 + 8,72) = 0,181736."""
    U, B, dt, _ = G.u_podloga_na_gruncie(100, 40, 0.3, 0.5, 2.0)
    close(B, 5.0, 1e-12, "B'")
    close(dt, 1.72, 1e-12, "d_t")
    close(U, 0.531503, 2e-6, "U")
    iz = G.IzolacjaKrawedziowa("pionowa", 1.0, 0.10, 0.035)
    r = G.oblicz_grunt(100, 40, 0.3, 0.5, izolacja=iz, klimat_mies=list(klimat_miesieczny().theta_e))
    close(r.dpsi, -0.337578, 2e-6, "ΔΨ")
    close(r.U, 0.396472, 2e-6, "U'")
    U2, _, _, _ = G.u_podloga_na_gruncie(100, 40, 0.3, 4.0, 2.0)
    close(U2, 0.181736, 2e-6, "U dobrze izolowana")
    assert r.spelnia_obwodowa and len(r.Phi_mies) == 12 and max(r.Phi_mies) > min(r.Phi_mies)


# --------------------------------------------------------------------------------------------------
# PN-EN ISO 10077-1, g
# --------------------------------------------------------------------------------------------------
def test_okno_reczne():
    """1,80 × 1,50, 2 kwatery, b_f = 0,115, b_s = 0,165: w_g = 0,7025, h_g = 1,27, A_g = 1,78435, l_g = 7,89,
    A_f = 0,91565; U_w = (1,78435·0,5 + 0,91565·0,95 + 7,89·0,035)/2,7 = 0,754886."""
    d = OK.DaneStolarki("T", "okno", U_g=0.5, U_f=0.95, psi_g=0.035, b_f=0.115, b_s=0.165, g_n=0.5)
    w = OK.u_okna(1.8, 1.5, d, n_kw=2)
    close(w.A_g, 1.78435, 1e-9, "A_g")
    close(w.l_g, 7.89, 1e-9, "l_g")
    close(w.U_w, 0.754886, 1e-6, "U_w")
    assert w.spelnia_WT and w.spelnia_cel


def test_g_osłony():
    """WT f_C (białe żaluzje zewn., τ = 0,1) = 0,15; ISO 52022-1 zewn.: τ = 0,1, ρ = 0,55, g = 0,5, U_g = 0,5:
    G = 1/(1/0,5 + 1/5 + 1/10) = 0,434783; g_tot = 0,05 + 0,35·G/10 + 0,1·0,5·G/5 = 0,069565."""
    assert OK.f_c_wt("zaluzja_biala", "zewn", 0.1) == 0.15
    assert OK.f_c_wt("zaslona_aluminiowa", "zewn", 0.05) == 0.08
    close(OK.g_tot_uproszczona(0.5, 0.5, 0.10, 0.55, "zewn"), 0.069565, 1e-6, "g_tot")
    g = OK.sprawdz_g("X", "X", 180.0, 2.0, 0.5, 0.5, "brak")
    assert g.spelnia is False
    assert OK.sprawdz_g("X", "X", 10.0, 2.0, 0.5, 0.5, "brak").spelnia        # N ± 45°
    assert OK.sprawdz_g("X", "X", 180.0, 0.4, 0.5, 0.5, "brak").spelnia       # < 0,5 m²
    assert OK.sprawdz_g("X", "X", 180.0, 2.0, 0.5, 0.5, "brak", F_sh_lato=0.6).spelnia


def test_zacienienie_okap():
    """Okap nad oknem S: F_sh latem < zimą; okap zerowy → F_sh = 1."""
    r = OK.zacienienie_miesieczne(180.0, 2.0, 1.5, okap=OK.Okap(1.2, 0.3))
    assert r["F_sh_lato"] < r["F_sh_zima"] < 1.0
    r0 = OK.zacienienie_miesieczne(180.0, 2.0, 1.5)
    close(r0["F_sh_lato"], 1.0, 1e-12, "bez okapu")


# --------------------------------------------------------------------------------------------------
# PN-EN ISO 13788
# --------------------------------------------------------------------------------------------------
def test_psat_frsi():
    """p_sat(20) = 2336,95 Pa, p_sat(0) = 610,5 Pa; f_Rsi,min (φ_i = 50 %) — luty: θ_e = −1,76, p_i = 1168,5,
    p_sat,min = 1460,6, θ_si,min = 12,625 °C → f = (12,625 + 1,76)/21,76 = 0,6611."""
    close(float(p_sat(20.0)), 2336.95, 0.05, "p_sat(20)")
    close(float(p_sat(0.0)), 610.5, 1e-9, "p_sat(0)")
    fr = KD.f_rsi_min(20.0, phi_i=0.5)
    assert fr.miesiac_kryt == 2
    close(fr.f_Rsi_kryt, 0.6611, 5e-4, "f_Rsi,max")
    close(fr.f_Rsi_wym, 0.72, 1e-12, "f_Rsi,wym (WT)")


def test_glaser_reczne():
    """Dwie warstwy: 1) R = 5, s_d = 1 m; 2) R = 0,01, s_d = 10 m; R_si = 0,13, R_se = 0,04; θ_i = 20 °C,
    p_i = 1200 Pa, p_e = 400 Pa, θ_e dobrane tak, by θ_c = −2,5 °C: θ_e = 20 − 22,5·5,18/5,13 = −2,719298.
    p_sat(−2,5) = 495,86 Pa; g = 2·10⁻¹⁰·[(1200 − 495,86)/1 − (495,86 − 400)/10]·31·86400 = 0,37207 kg/m² (X)."""
    ws = [KD.WarstwaG("A", "A", "izolacja", 0.1, 5.0, 1.0, 10), KD.WarstwaG("B", "B", "inna", 0.01, 0.01, 10.0, 1000)]
    te = 20 - 22.5 * 5.18 / 5.13
    pi = 1200.0
    r = KD.glaser(ws, 0.13, 0.04, theta_i=20.0, phi_i=pi / float(p_sat(20.0)), theta_e=[te] * 12, p_e=[400.0] * 12,
                  _licz_sd=False)
    assert r.kondensacja and not r.wysycha and r.plaszczyzny == [1]
    m0 = r.kolejnosc[0]
    ps = float(p_sat(-2.5))
    exp = 2e-10 * ((pi - ps) / 1.0 - (ps - 400.0) / 10.0) * 744 * 3600
    close(r.theta[m0][1], -2.5, 1e-9, "θ_c")
    close(r.g_c[m0][1], exp, 1e-6, "g_c")
    close(exp, 0.37207, 1e-4, "g_c ręcznie")


def test_glaser_sd_paroizolacji():
    """Ściana z izolacją wewnętrzną (wełna) bez paroizolacji: kondensacja; wymagane s_d > 0 i usuwa kondensację."""
    ws = [{"mat": "GK", "d": 0.0125}, {"mat": "MW", "d": 0.10}, {"mat": "SIL", "d": 0.24}, {"mat": "TS", "d": 0.01}]
    wg, Rsi, Rse = KD.warstwy_glaser(ws, MAT, rola="sciana_zewn")
    r = KD.glaser(wg, Rsi, Rse, klasa=3)
    assert r.kondensacja and r.sd_par_wym and r.sd_par_wym > 0
    ws2 = [ws[0], {"mat": "PAR", "d": r.sd_par_wym / 50000 * 1.01}] + ws[1:]
    wg2, _, _ = KD.warstwy_glaser(ws2, MAT, rola="sciana_zewn")
    assert not KD.glaser(wg2, Rsi, Rse, klasa=3, _licz_sd=False).kondensacja


# --------------------------------------------------------------------------------------------------
# Ciągłość warstw, mostki
# --------------------------------------------------------------------------------------------------
def test_ciaglosc_warstw():
    ok = sprawdz_ciaglosc("D", "dach", [{"mat": "EPDM", "d": 0.002}, {"mat": "PIR", "d": 0.2}, {"mat": "PAR", "d": 0.004},
                                        {"mat": "ZB", "d": 0.2}], MAT, "dach")
    assert ok.ok
    bez = sprawdz_ciaglosc("D", "dach", [{"mat": "EPDM", "d": 0.002}, {"mat": "PIR", "d": 0.2}, {"mat": "ZB", "d": 0.2}],
                           MAT, "dach")
    assert any(u.linia == "szczelnosc" for u in bez.braki)
    ziel = sprawdz_ciaglosc("DZ", "dach zielony", [{"mat": "SUB", "d": 0.08}, {"mat": "EPDM", "d": 0.002},
                                                    {"mat": "PIR", "d": 0.2}, {"mat": "PAR", "d": 0.004},
                                                    {"mat": "ZB", "d": 0.2}], MAT, "dach")
    assert len(ziel.braki) >= 2          # drenaż, geowłóknina, bariera przeciwkorzenna
    sc = sprawdz_ciaglosc("S", "ściana", [{"mat": "SIL", "d": 0.18}, {"mat": "EPS", "d": 0.2}], MAT, "sciana_zewn")
    assert {u.linia for u in sc.braki} >= {"szczelnosc", "zewnetrzna"}
    pod = sprawdz_ciaglosc("P", "podłoga", [{"mat": "XPS", "d": 0.15}, {"mat": "ZB", "d": 0.12}], MAT, "podloga_grunt")
    assert any(u.linia == "hydroizolacja" for u in pod.braki)


def test_mostki_symulacja_nadpisuje():
    auto = [{"typ": "attyka", "dlugosc": 10.0, "opis": "a"}, {"typ": "plyta_wspornikowa_lacznik", "dlugosc": 5.0, "opis": "b"}]
    w = MB.wezly_z_modelu(None, None, wezly_auto=auto)
    close(MB.h_tb(w), 10 * 0.75 + 5 * 0.15, 1e-9, "H_TB domyślne")
    w2 = MB.wezly_z_modelu(None, {"AUTO-01": {"psi": 0.08, "f_rsi": 0.86}}, wezly_auto=auto)
    close(MB.h_tb(w2), 10 * 0.08 + 5 * 0.15, 1e-9, "H_TB symulacja")
    assert w2[0].status == "symulacja" and w2[0].f_rsi == 0.86
    chk = MB.sprawdz_frsi(w2, 0.72)
    assert chk[0]["ok"] and chk[1]["ok"]


# --------------------------------------------------------------------------------------------------
# Metodologia EP — elementy
# --------------------------------------------------------------------------------------------------
def test_qwnd_i_eta():
    """Q_W,nd = 1,40·A_f·4,19·45·0,90·365/3600 → 24,09 kWh/(m²·rok) (rejestr W-242); η_gn: γ = 1 → a/(a+1)."""
    close(EP.q_w_nd(100.0) / 100.0, 24.09, 0.005, "Q_W,nd/A_f")
    close(EP.eta_gn(1.0, 4.0), 0.8, 1e-12, "η(γ=1)")
    close(EP.eta_gn(0.5, 5.41), (1 - 0.5 ** 5.41) / (1 - 0.5 ** 6.41), 1e-12, "η")


def test_klimat_tmy():
    """Dane MIiR Poznań: 8760 h, średnia roczna 8,26 °C, sumy godzinowe = statystyki; zgodność godzin ze Słońcem."""
    k = klimat_miesieczny()
    g = klimat_godzinowy()
    assert len(g.DBT) == 8760
    close(float(g.DBT.mean()), 8.26, 0.01, "θ_e rok")
    for m in range(12):
        s = g.M == m + 1
        close(float(g.kol["S_90"][s].sum() / 1000), float(k.irr["S_90"][m]), 0.02, f"S_90 m{m + 1}")
    az, el = g.pozycja_slonca()
    assert int(np.sum((g.ITH > 0) & (el <= 0))) <= 10


# --------------------------------------------------------------------------------------------------
# Model testowy — pełny łańcuch
# --------------------------------------------------------------------------------------------------
_R = None


def _wyniki():
    global _R
    if _R is None:
        m = load_model(B_TEST, D_TEST)
        _R = (m, oblicz_wszystko(m))
    return _R


def test_model_bryla_bilans_pol():
    m, R = _wyniki()
    br = R["obudowa"].bryla
    A0 = sum(r.pow_netto for r in m.pomieszczenia("P0"))
    A1 = sum(r.pow_netto for r in m.pomieszczenia("P1"))
    close(sum(e.A for e in br.elementy if e.rola == "podloga_grunt"), A0, 1e-6, "podłoga = Σ pomieszczeń P0")
    close(sum(e.A for e in br.elementy if e.rola == "dach"), sum(r.polygon.area for r in m.pomieszczenia("P1")), 1e-6,
          "dach = Σ pomieszczeń P1")
    zewn = [o for o in m.otwory() if o.sciana.typ == "sciana_zewn"]
    close(sum(e.A for e in br.elementy if e.rodzaj in ("okno", "drzwi") and e.sasiad == "zewn"),
          sum(o.szer * o.wys for o in zewn), 1e-6, "otwory zewnętrzne")
    assert not [w for w in br.ostrzezenia if "bez ściany" in w]
    close(br.A_f, A0 + A1, 1e-6, "A_f")


def test_model_obciazenie_vs_H_tr():
    """Wszystkie pomieszczenia 20 °C, brak nieogrzewanych: Σ Φ_T,i = H_tr(EP)·(20 − θ_e)."""
    m, R = _wyniki()
    w = R["ep"]
    close(R["obc"].Phi_T, w.H_tr * 38.0, 1e-6 * w.H_tr * 38.0, "Φ_T vs H_tr")
    assert 3000 < R["obc"].Phi_HL < 8000


def test_model_ep():
    m, R = _wyniki()
    A, A0, B, C = R["ep_alt"]
    close(A.Q_W_nd / A.A_f, 24.09, 0.01, "Q_W,nd/A_f")
    assert A.EP < A0.EP < C.EP and A.EP < B.EP
    assert A.spelnia and not C.spelnia
    close(A.EK, A0.EK, 1e-9, "EK niezależne od PV")
    Mm = A.mies
    close(float(Mm["Q_H_nd"].sum()), A.Q_H_nd, 1e-6, "Σ miesięcy")
    assert all(0 <= a <= 1 for a in A.E_PV_a) and A.E_PV_sys <= A.E_PV
    # EP = w_el·(Q_K − E_PV,sys)/A_f dla systemu all-electric
    close(A.EP, 2.5 * (A.Q_K - A.E_PV_sys) / A.A_f, 1e-6, "EP")


def test_model_wentylacja_i_glaser():
    m, R = _wyniki()
    W = R["went"]
    assert W.zrownowazony and W.suma_naw >= 100 - 1e-6
    gl = {g.kod: g for g in R["glaser"]}
    assert not gl["SZ1"].kondensacja
    assert gl["SD-D1"].kondensacja and gl["SD-D1"].wysycha and gl["SD-D1"].dopuszczalna
    assert gl["SD-D1"].sd_par_wym_dop is not None and gl["SD-D1"].sd_par_wym_dop <= gl["SD-D1"].sd_par_ist
    c = {x.kod: x for x in R["obudowa"].ciaglosc}
    assert c["SZ1"].ok and c["SD-D1"].ok and not c["POD-0"].ok      # POD-0 bez izolacji przeciwwilgociowej


def test_model_nieogrzewane_bu():
    """Wariant: garderoba 1.04 nieogrzewana → θ_u między θ_e i 20 °C, przegrody do pom. nieogrzewanego, Φ sąsiadów rośnie."""
    raw = yaml.safe_load(B_TEST.read_text(encoding="utf-8"))
    raw2 = copy.deepcopy(raw)
    for p in raw2["pomieszczenia"]:
        if str(p["id"]) == "1.04":
            p["temp"] = None
    m2 = Model(raw2, yaml.safe_load(D_TEST.read_text(encoding="utf-8")))
    ob = oblicz_obudowe(m2, zacienienie=False)
    W = bilans_wentylacji(ob.bryla, cfg=ob.cfg)
    O = obciazenie_cieplne(ob, W)
    assert "1.04" in O.theta_u and -18 < O.theta_u["1.04"] < 20 and 0 < O.b_u["1.04"] < 1
    assert any(e.rola == "sciana_nieogrz" for e in ob.bryla.elementy)
    m, R = _wyniki()
    phi1 = {o.id: o.Phi_T for o in R["obc"].pomieszczenia}
    phi2 = {o.id: o.Phi_T for o in O.pomieszczenia}
    assert phi2["1.05"] > phi1["1.05"]
    w2 = EP.oblicz_ep(ob, W, EP.system_projektowy(ob.cfg, W, ob.bryla.A_f, O.dobor), obc=O)
    assert w2.H_tr_skladniki["przestrzenie nieogrzewane (b_u)"] > 0


def test_demo_raporty(katalog: Path | None = None):
    m, R = _wyniki()
    out = katalog or (ROOT / "build" / "test" / "obliczenia_demo")
    pl = zapisz_raporty(R, out, tytul="model testowy (dom_testowy.yaml)",
                        model_opis="Model: `model/test/dom_testowy.yaml` + `model/test/dzialka_testowa.yaml` — "
                                   "model TESTOWY pipeline'u (nie jest projektem Domu LAMELA).")
    names = {Path(p).name for p in pl}
    for n in ("00_zestawienie.md", "01_przegrody_U.md", "05_wilgotnosc.md", "09_charakterystyka_energetyczna.md",
              "bilans_energii.png", "glaser_SD-D1.png", "wyniki.json"):
        assert n in names, n
    for p in pl:
        assert Path(p).stat().st_size > 200, p


def test_model_docelowy_jesli_istnieje():
    """Drugi test — model/budynek.yaml (tylko odczyt), jeśli już istnieje."""
    if not B_DOCEL.exists():
        print("      (pominięto: brak model/budynek.yaml)")
        return
    m = load_model(B_DOCEL, D_DOCEL if D_DOCEL.exists() else None, strict=False)
    R = oblicz_wszystko(m)
    pl = zapisz_raporty(R, ROOT / "build" / "test" / "obliczenia_budynek", tytul="model/budynek.yaml (kontrola)")
    w = R["ep"]
    print(f"      budynek.yaml: A_f = {w.A_f:.1f} m², Φ_HL = {R['obc'].Phi_HL / 1000:.2f} kW, EP = {w.EP:.1f}; "
          f"ostrzeżeń geometrii: {len(R['obudowa'].bryla.ostrzezenia)}; plików: {len(pl)}")
    assert w.A_f > 50 and math.isfinite(w.EP)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bez-demo", action="store_true")
    a = ap.parse_args(argv)
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    ok_ = fail = 0
    t0 = time.time()
    for n, f in tests:
        t1 = time.time()
        try:
            if n == "test_demo_raporty":
                f(None if a.bez_demo else DEMO)
            else:
                f()
            ok_ += 1
            print(f"PASS  {n}  ({time.time() - t1:.1f} s)", flush=True)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"FAIL  {n}: {e}", flush=True)
            traceback.print_exc(limit=4)
    print(f"\n{ok_} zaliczonych, {fail} niezaliczonych, czas {time.time() - t0:.0f} s")
    if not a.bez_demo:
        print(f"Demo: {DEMO}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
