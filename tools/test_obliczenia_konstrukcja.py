#!/usr/bin/env python3
"""Testy biblioteki obliczeń konstrukcyjnych ``lamela.obliczenia.konstrukcja`` (Eurokody + NA PL).

Uruchomienie:
    PYTHONPATH=src python3 tools/test_obliczenia_konstrukcja.py            # testy + demo raport modelu testowego
    PYTHONPATH=src python3 tools/test_obliczenia_konstrukcja.py --bez-demo # tylko testy
    PYTHONPATH=src python3 tools/test_obliczenia_konstrukcja.py --lamela   # dodatkowo model/budynek.yaml (jeśli istnieje)
Demo raport: projekt/08_obliczenia/demo_test/konstrukcja/ (obliczenia_statyczne.md/.html, rys/, wyniki.json,
porownanie_reczne.md). Funkcje test_* są zgodne z pytest.

Źródła przykładów (wartości wzorcowe):
[T]  S. Timoshenko, S. Woinowsky-Krieger, *Theory of Plates and Shells*, 2nd ed., McGraw-Hill 1959 — tabl. 8 (płyta
     swobodnie podparta, ν = 0,3) i tabl. 35 (płyta utwierdzona, ν = 0,3).
[M]  W.H. Mosley, J.H. Bungey, R. Hulse, *Reinforced Concrete Design to Eurocode 2*, 7th ed., Palgrave Macmillan 2012,
     rozdz. 4 — przekrój pojedynczo zbrojony b = 260 mm, d = 440 mm, M = 165 kNm, C25/30, B500: z ≈ 381 mm,
     A_s ≈ 996 mm² (γ_c = 1,5, α_cc = 0,85 — zalecenia UK; w teście te same parametry).
[E2] PN-EN 1992-1-1:2008, tabl. 7.4N — graniczne l/d dla C30/37, σ_s = 310 MPa: belka swobodnie podparta 14 (ρ = 1,5 %)
     i 20 (ρ = 0,5 %); wspornik 6 i 8.
[CC] The Concrete Centre, *How to design concrete structures using Eurocode 2*, rozdz. „Detailing” (2006) — l_b,rqd dla
     C25/30, f_yk = 500 MPa, γ_c = 1,5: 40φ (dobre warunki), 58φ (inne warunki).
[E3] PN-EN 1993-1-1:2006, 6.3.1.2 (krzywe wyboczeniowe) — χ(λ̄ = 1,0): a 0,666; b 0,597; c 0,540; d 0,467
     (wartości tablicowane np. w SCI P362 / ECCS); katalog ArcelorMittal: IPE 200 (A 28,5 cm², I_y 1943 cm⁴,
     W_pl,y 221 cm³), HEB 160 (54,3 cm², 2492 cm⁴, 354 cm³).
[E8] PN-EN 1993-1-8 tabl. 3.4 — F_v,Rd śruby M16 kl. 8.8 (gwint w płaszczyźnie ścinania) = 60,3 kN; M20 8.8 = 94,1 kN.
[R5] Rejestr R5 projektu (docs/10_podstawy_prawne/R5_...): s = 0,72 kN/m²; attyka 0,6 m → 1,20 kN/m²; q_p(11 m, II) = 0,71,
     q_p(10,5 m, III) = 0,58 kN/m²; f_k = 7,66 MPa, f_d = 4,50 MPa; nośność ławy B = 0,6 m, D = 0,8 m, γ = 18,5:
     φ' = 32° → R_k/A' = 497, R_d/A' = 355 kPa; φ' = 33° → 567 / 405 kPa (sprawdzone niezależnie w weryfikacji R5).
Uwaga: wartości [M], [CC] przytoczone z pamięci autora testów — w każdym przypadku sprawdzone dodatkowo niezależnym
rachunkiem ręcznym w teście (wzory zamknięte).
"""
from __future__ import annotations

import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.model import load_model  # noqa: E402
from lamela.obliczenia.konstrukcja import fundamenty as fund  # noqa: E402
from lamela.obliczenia.konstrukcja import mur as murm  # noqa: E402
from lamela.obliczenia.konstrukcja import obciazenia as obc  # noqa: E402
from lamela.obliczenia.konstrukcja import stal as stalm  # noqa: E402
from lamela.obliczenia.konstrukcja import zelbet  # noqa: E402
from lamela.obliczenia.konstrukcja.materialy import Beton, Mur, StalKonstr, przekroj  # noqa: E402
from lamela.obliczenia.konstrukcja.plyty import PlytaMES, PodporaLiniowa, wspolczynniki_plyty, wood_armer  # noqa: E402
from lamela.obliczenia.konstrukcja.pozycje import AnalizaKonstrukcji  # noqa: E402
from lamela.obliczenia.konstrukcja.raport import generuj_raport  # noqa: E402
from lamela.obliczenia.konstrukcja.statyka import Belka, ObcP, ObcQ, Podpora, obwiednia_ULS  # noqa: E402
from lamela.obliczenia.konstrukcja.wspolne import Grunt, Parametry, f  # noqa: E402

B_TEST = ROOT / "model" / "test" / "dom_testowy.yaml"
D_TEST = ROOT / "model" / "test" / "dzialka_testowa.yaml"
DEMO = ROOT / "projekt" / "08_obliczenia" / "demo_test" / "konstrukcja"


def close(a, b, tol, what=""):
    assert abs(a - b) <= tol * max(abs(b), 1e-12), f"{what}: {a:.5g} ≠ {b:.5g} (tol {tol:.1%})"


# ==================================================================================================
# 1. Statyka i płyty
# ==================================================================================================
def test_belka_wzory_zamkniete():
    b = Belka(6, [Podpora(0), Podpora(6)], EI=1000)
    r = b.rozwiaz([ObcQ(10)])
    close(r.M.max(), 10 * 36 / 8, 1e-6, "M = ql²/8")
    close(r.w.max(), 5 * 10 * 6 ** 4 / 384 / 1000, 1e-6, "w = 5ql⁴/384EI")
    r = Belka(8, [Podpora(0), Podpora(4), Podpora(8)]).rozwiaz([ObcQ(10)])
    close(r.M.min(), -10 * 16 / 8, 1e-6, "belka 2-przęsłowa M_B = −ql²/8")
    close(r.R[1], 1.25 * 10 * 4, 1e-6, "R_B = 1,25ql")
    r = Belka(6, [Podpora(0, "utwierdzenie"), Podpora(6, "utwierdzenie")]).rozwiaz([ObcQ(12)])
    close(r.M[0], -12 * 36 / 12, 1e-6, "utwierdzona −ql²/12")
    close(r.M.max(), 12 * 36 / 24, 1e-6, "utwierdzona ql²/24")
    r = Belka(6, [Podpora(0, "utwierdzenie"), Podpora(6)]).rozwiaz([ObcQ(8)])
    close(r.M.max(), 9 / 128 * 8 * 36, 1e-6, "jednostronnie utwierdzona 9ql²/128")
    r = Belka(3, [Podpora(0, "utwierdzenie")]).rozwiaz([ObcQ(10), ObcP(5, 3)])
    close(r.M[0], -(10 * 9 / 2 + 5 * 3), 1e-6, "wspornik")
    b = Belka(12, [Podpora(0), Podpora(4), Podpora(8), Podpora(12)])
    ob, _ = obwiednia_ULS(b, [ObcQ(5)], [[ObcQ(3, a, c)] for a, c in b.przesla()])
    assert ob.kombinacje == 16 and ob.M_podpora < 0 < ob.M_przeslo


def test_plyty_tablice_timoshenko():
    """[T] tabl. 8 i 35 (ν = 0,3): w·D/(q·a⁴), M/(q·a²)."""
    wzorce_ss = {1.0: (0.00406, 0.0479, 0.0479), 1.5: (0.00772, 0.0812, 0.0498), 2.0: (0.01013, 0.1017, 0.0464)}
    for r, (w, mx, my) in wzorce_ss.items():
        k = wspolczynniki_plyty(1.0, r, "SSSS", 0.3)
        close(k.k_w, w, 0.01, f"SSSS {r} w")
        close(k.alfa_x, mx, 0.01, f"SSSS {r} M_x")
        close(k.alfa_y, my, 0.01, f"SSSS {r} M_y")
    wzorce_cc = {1.0: (0.00126, 0.0231, -0.0513), 1.5: (0.00220, 0.0368, -0.0757), 2.0: (0.00254, 0.0412, -0.0829)}
    for r, (w, mx, mex) in wzorce_cc.items():
        k = wspolczynniki_plyty(1.0, r, "UUUU", 0.3)
        close(k.k_w, w, 0.015, f"UUUU {r} w")
        close(k.alfa_x, mx, 0.015, f"UUUU {r} M_x środek")
        close(k.beta_x[0], mex, 0.01, f"UUUU {r} M_x krawędź")


def test_mes_plyty_acm():
    from shapely.geometry import LineString, box
    a = 4.0
    sup = [PodporaLiniowa(n, LineString(c)) for n, c in (("a", [(0, 0), (a, 0)]), ("b", [(a, 0), (a, a)]),
                                                          ("c", [(a, a), (0, a)]), ("d", [(0, a), (0, 0)]))]
    pl = PlytaMES(box(0, 0, a, a), 0.2, 30e6, 0.3, sup, siatka=0.1)
    r = pl.rozwiaz(pl.wektor(10.0))
    close(r.w.max() * pl.D / (10 * a ** 4), 0.00406, 0.01, "ACM w (SS)")
    close(r.m[:, 0].max() / (10 * a * a), 0.0479, 0.01, "ACM M (SS)")
    close(r.R.sum(), 10 * a * a, 1e-6, "ΣR = q·A")
    wa = wood_armer(np.array([[10.0, 4.0, 3.0], [-10.0, -4.0, 3.0]]))
    assert wa["dol_x"][0] == 13.0 and wa["gora_x"][1] == -13.0


# ==================================================================================================
# 2. Obciążenia
# ==================================================================================================
def test_obciazenia_R5():
    p = Parametry()
    close(obc.snieg_dach_plaski(p).s1, 0.72, 1e-9, "śnieg dach płaski [R5]")
    close(obc.snieg_attyka(0.6, p).s2, 1.20, 1e-9, "attyka 0,6 m [R5 3.4]")
    close(obc.snieg_attyka(0.3, p).s2, 0.72, 1e-9, "attyka 0,3 m — bez zaspy [R5 3.4]")
    close(obc.wiatr_qp(11.0, p, "II").q_p, 0.71, 0.01, "q_p(11, II) [R5]")
    close(obc.wiatr_qp(10.5, p, "III").q_p, 0.58, 0.01, "q_p(10,5, III) [R5]")
    su = obc.snieg_uskok(3.0, 8.0, 6.0, p)            # μ_w = 14/6 = 2,333 < γh/s_k = 6,67
    close(su.mu2, 14 / 6, 1e-9, "μ₂ uskok")
    close(su.l_s, 6.0, 1e-9, "l_s = 2h")
    b2 = obc.snieg_B2_uskok(3.0, 8.0, 6.0, p)          # l_s = min(15; 8; 15) = 8; μ = min(6,67; 2; 8) = 2
    close(b2.s2, 2.0 * 0.9, 1e-9, "B2 [R5-38]")
    kb = obc.kombinacje([obc.Oddz("G", "G"), obc.Oddz("Q", "Q", "A")], p, "STR")
    vals = [k.wsp["G"] * 5 + k.wsp.get("Q", 0) * 2 for k in kb]
    close(max(vals), 1.35 * 5 + 1.05 * 2, 1e-9, "6.10a/b")


def test_ciezary_warstw_z_modelu():
    m = load_model(B_TEST, D_TEST)
    z = obc.zestawienie_przegrody(m, "SD-D1")
    # EPDM 1150·9,81·0,0015 + PIR 32·9,81·0,22 + PAROIZ 1100·9,81·0,002 + żelbet 25·0,20 + tynk 1300·9,81·0,01
    exp = (1150 * 0.0015 + 32 * 0.22 + 1100 * 0.002 + 1300 * 0.01) * 9.81 / 1000 + 25 * 0.20
    close(z.g_k, exp, 1e-9, "ciężar stropodachu ρ·g·d")


# ==================================================================================================
# 3. Żelbet
# ==================================================================================================
def test_zelbet_zginanie_mosley():
    b = Beton("C25/30", gamma_c=1.5, alfa_cc=0.85)
    w = zelbet.zginanie_prostokat(165, 0.26, 0.5, 0.44, b)
    close(w.As_req, 996, 0.005, "A_s [M]")
    close(w.z, 381, 0.005, "z [M]")
    # niezależnie: A_s = M/(f_yd·z), z = d(1 − ξ/2)
    fcd = 0.85 * 25 / 1.5
    mu = 165e6 / (260 * 440 ** 2 * fcd)
    xi = 1 - math.sqrt(1 - 2 * mu)
    close(w.As_req, 165e6 / (500 / 1.15 * 440 * (1 - xi / 2)), 1e-9, "A_s ręcznie")


def test_zelbet_ld_tablica_74N():
    b = Beton("C30/37")
    for K, rho, exp in ((1.0, 0.005, 20.0), (1.0, 0.015, 14.0), (0.4, 0.005, 8.0), (0.4, 0.015, 6.0)):
        As = rho * 1000 * 170
        u = zelbet.ugiecie_ld(5, 0.17, As, As, 1.0, b, K=K)
        assert abs(u.l_d_dop - exp) <= 0.6, (K, rho, u.l_d_dop, exp)


def test_zelbet_zakotwienie_scinanie_otulina():
    b = Beton("C25/30", gamma_c=1.5)
    close(zelbet.zakotwienie(12, b).l_b_rqd / 12, 40.3, 0.01, "l_b,rqd dobre [CC]")
    close(zelbet.zakotwienie(12, b, dobra_przyczepnosc=False).l_b_rqd / 12, 57.5, 0.01, "l_b,rqd inne [CC]")
    # V_Rd,c ręcznie: C25/30 (γc 1,4), b = 1000, d = 170, A_sl = 524 mm²
    b = Beton("C25/30")
    k = min(1 + math.sqrt(200 / 170), 2)
    v = 0.18 / 1.4 * k * (100 * 524 / 170000 * 25) ** (1 / 3)
    vmin = 0.035 * k ** 1.5 * 5
    close(zelbet.scinanie_bez_zbrojenia(10, 1.0, 0.17, 524, b).V_Rd_c, max(v, vmin) * 170, 1e-9, "V_Rd,c")
    assert zelbet.otulina("XC1", 12).c_nom == 25 and zelbet.otulina("XC2", 12).c_nom == 35
    assert zelbet.otulina("XC4", 12).c_nom == 40 and zelbet.otulina("XC3", 12).c_nom == 35   # R5 3.6
    w = zelbet.belka_sciana(4.0, 3.0, 0.18, 60, b)
    close(w.T, 60 * 16 / 8 / (0.2 * (4 + 6)), 1e-9, "tarcza — ściąg")


def test_zelbet_rysy_ugiecie_obliczeniowe():
    b = Beton("C25/30")
    r = zelbet.rysy_wk(20, 1.0, 0.2, 0.17, 524, 10, 25, b)
    assert 0.05 < r.w_k < 0.4
    ug = zelbet.ugiecie_obliczeniowe(10, 5 * 10 * 5 ** 4 / 384, 5.0, 1.0, 0.2, 0.17, 524, b)
    # M_qp < M_cr → w = w_I (+ skurcz)
    assert ug.w < 20


# ==================================================================================================
# 4. Mur, stal, fundamenty
# ==================================================================================================
def test_mur():
    m = Mur()
    close(m.f_k, 7.66, 0.001, "f_k [R5-61]")
    close(m.f_d, 4.50, 0.002, "f_d [R5-62]")
    # zał. G ręcznie: h_ef/t_ef = 20, e_mk/t = 0,05, E = 1000 f_k → λ = 0,632, u = 0,848, Φ_m = 0,9·e^(−u²/2)
    Pm, lam, u = murm.phi_m(0.05 * 0.2, 0.2, 4.0, 0.2, m)
    close(Pm, 0.9 * math.exp(-((20 / math.sqrt(1000) - 0.063) / (0.73 - 1.17 * 0.05)) ** 2 / 2), 1e-9, "Φ_m")
    close(murm.eta_A(0.12), 1.43, 1e-9, "η_A [R5-63]")
    d = murm.docisk(60, 0.3, 0.2, 0.18, 1.5, m)
    assert 1.0 <= d.beta <= 1.5


def test_stal():
    for k, v in {"a": 0.6656, "b": 0.5970, "c": 0.5399, "d": 0.4671}.items():
        close(stalm.chi(1.0, k), v, 0.001, f"χ krzywa {k} [E3]")
    p = przekroj("IPE 200")
    close(p.A / 100, 28.5, 0.01, "IPE 200 A")
    close(p.I_y / 1e4, 1943, 0.005, "IPE 200 I_y")
    close(p.W_pl_y / 1e3, 221, 0.01, "IPE 200 W_pl,y")
    p = przekroj("HEB 160")
    close(p.A / 100, 54.3, 0.01, "HEB 160 A")
    close(p.I_y / 1e4, 2492, 0.005, "HEB 160 I_y")
    close(p.W_pl_y / 1e3, 354, 0.01, "HEB 160 W_pl,y")
    # M_cr IPE 200, L = 5 m, C1 = 1 (moment stały) — wzór zamknięty
    s = StalKonstr("S235")
    E, G = 210000, 81000
    q = przekroj("IPE 200")
    Mcr = math.pi / 5000 * math.sqrt(E * q.I_z * G * q.I_t) * math.sqrt(1 + math.pi ** 2 * E * q.I_w / (5000 ** 2 * G * q.I_t)) / 1e6
    close(stalm.M_cr_dwuteownik(q, s, 5.0, 1.0, 0.0, 0.0), Mcr, 1e-6, "M_cr")
    w = stalm.sruby(1, 16, "8.8", 10, "S355", F_v_Ed=10)
    close(w.kroki[0].wynik, 60.3, 0.002, "F_v,Rd M16 8.8 [E8]")
    close(stalm.sruby(1, 20, "8.8", 10, "S355").kroki[0].wynik, 94.1, 0.002, "F_v,Rd M20 8.8 [E8]")


def test_fundamenty_R5():
    for fi, (Rk, Rd) in {32: (497, 355), 33: (567, 405)}.items():
        n = fund.nosnosc_podloza(0.6, 0.8, 100, 100, Grunt(fi_k=fi), Parametry())
        close(n.q_Rk, Rk, 0.002, f"R_k/A' φ={fi} [R5]")
        close(n.q_Rk / 1.4, Rd, 0.002, f"R_d/A' φ={fi} [R5]")
    close(4 * fund.wsp_naroznika(0.5, 0.5, 1.0), 0.3361, 0.002, "Boussinesq — środek kwadratu 1×1 m, z = 1 m")
    lw = fund.lawa("L", 0.6, 0.3, 0.18, 1.0, 60, 12, Grunt(), Beton("C25/30"))
    assert lw.ok and "nie wymaga" in lw.zbrojenie_poprz


# ==================================================================================================
# 5. Model testowy — ścieżka obciążeń
# ==================================================================================================
_AN = None


def analiza(rys_dir=None):
    global _AN
    if _AN is None or rys_dir is not None:
        m = load_model(B_TEST, D_TEST)
        _AN = AnalizaKonstrukcji(m, Parametry.z_wymagan(), rys_dir=rys_dir).uruchom()
    return _AN


def test_model_pozycje():
    an = analiza()
    assert not [u for u in an.uwagi if u.startswith("BŁĄD")], [u for u in an.uwagi if u.startswith("BŁĄD")]
    ids = {pz.ident for g in an.pozycje for pz in g.podpozycje}
    for need in ("D1", "ST1", "PL-D", "SCH1", "B1", "SL1", "SL2", "S0-05", "S1-01", "L1", "L5", "F1", "F2", "N-O0-01"):
        assert need in ids, f"brak pozycji {need}"
    assert [g.tytul for g in an.pozycje][0] == "Dachy i stropodachy"


def test_model_rownowaga_plyt():
    an = analiza()
    for g in an.grupy:
        fe = g.fe
        area_load = sum(e.zest.g_k * fe.elementy_w(e.poly_full).astype(float) @ (fe.el_ab[:, 0] * fe.el_ab[:, 1]) for e in g.el)
        lines = sum(ln.length * q for ln, cs, q, _ in g.linie if ln is not None and cs == "G")
        close(g.res["G"].R.sum(), area_load + lines, 1e-6, f"ΣR_G = ΣG ({g.nazwa})")
    d1 = next(g for g in an.grupy if g.nazwa == "D1")
    close(d1.res["G"].R.sum(), 83.2724 * obc.zestawienie_przegrody(an.m, "SD-D1", grubosc_konstr=0.2).g_k, 1e-3, "D1: pole × g_k")


def test_model_tablice_vs_mes():
    an = analiza()
    d1 = next(pz for pz in an.pos_plyty if pz.ident == "D1")
    p2 = next(d for d in d1.dane["pola"] if d["brzegi"] == "USSS")
    close(p2["Mx"], p2["Mx_tabl"], 0.10, "D1 P2: MES vs tablice (M_x)")


def test_model_przeplyw_obciazen():
    an = analiza()
    # schody → krawędź stropu ST1 i ściana S0-03
    st1 = next(g for g in an.grupy if g.nazwa == "ST1")
    assert any("schodów" in opis for _, _, _, opis in st1.linie)
    assert "S0-03" in an.pending_sciany
    # belka B1 → słup SL1 (reakcja) i ściana S0-02
    assert an.slupy_N["SL1"]["G"] > 10 and "S0-02" in an.pending_sciany
    # ścianki działowe P1 (> 3 kN/m) — obciążenia liniowe stropu
    assert sum(1 for _, cs, _, o in st1.linie if "ścianka działowa" in o and cs == "G") == 3
    # globalnie: obciążenia stałe na fundamentach ≈ płyty + ściany + ściany fund. + słupy (reakcje ujemne pominięte → ≥)
    Gf = sum(an.prof[w.id]["dol"].calka("G") for w in an.m.sciany("P0") if w.id in an.prof)
    Gs = sum(an.slupy_N[c]["G"] for c in an.slupy_N)
    Gpl = sum(g.res["G"].R.sum() for g in an.grupy)
    Gsc = sum(an.prof[w.id]["gm2"] * an.prof[w.id]["h"] * w.L - sum(o.szer * (o.z1 - o.z0) for o in an.prof[w.id]["otw"])
              * an.prof[w.id]["gm2"] for w in an.m.sciany() if w.id in an.prof)
    Gb = sum(float(b["b"]) * float(b["h"]) * 25 * 3.82 for b in an.m.belki())                  # ciężar B1
    Gsch = sum(P for lst in an.pending_sciany.values() for cs, P, _, szer in lst if cs == "G" and szer > 0.5)  # schody → ściana
    ratio = (Gf + Gs) / (Gpl + Gsc + Gb + Gsch)
    assert 0.98 <= ratio <= 1.05, f"równowaga globalna G: {ratio:.3f}"


def test_model_wyniki_rozsadne():
    an = analiza()
    pos = {pz.ident: pz for g in an.pozycje for pz in g.podpozycje}
    for k in ("D1", "ST1", "PL-D", "B1", "SL1", "S0-05"):
        assert pos[k].ok, f"{k}: η = {pos[k].wykorzystanie:.2f}"
    assert not pos["SCH1"].ok and pos["SCH1"].dane.get("hmin", 0) >= 0.16    # h = 15 cm (domyślne) — za mało
    assert not pos["L1"].ok     # D = 0,75 m < 1,0 m (W-284)


def test_wspornik_swobodny_EQU():
    """Wariant modelu testowego: płyta PL-D bez belki i słupów → wspornik swobodny 3,91 m połączony momentowo ze stropem ST1
    (łącznik termiczny) — EQU (PN-EN 1990 tabl. A1.2(A)) i ugięcie wspornika (K = 0,4; L = 2·wysięg)."""
    import copy
    import yaml
    from lamela.model import Model
    raw = yaml.safe_load(B_TEST.read_text(encoding="utf-8"))
    rawd = yaml.safe_load(D_TEST.read_text(encoding="utf-8"))
    raw = copy.deepcopy(raw)
    raw["slupy"], raw["belki"] = [], []
    raw["fundamenty"]["elementy"] = [e for e in raw["fundamenty"]["elementy"] if e["id"] not in ("F1", "F2")]
    for w in raw["wsporniki_plyty"]:
        w["obrys"] = [[10.09, 0.0], [11.6, 0.0], [11.6, 5.0], [10.09, 5.0]]     # wysięg 1,51 m
    raw["balustrady"] = [b for b in raw["balustrady"] if b["id"] != "BL4"]
    m = Model(raw, rawd)
    an = AnalizaKonstrukcji(m, Parametry()).uruchom()
    g = next(gg for gg in an.grupy if "PL-D" in gg.nazwa)
    assert "ST1" in g.nazwa, "wspornik swobodny powinien być liczony wspólnie ze stropem (ciągłość)"
    pz = next(p_ for p_ in an.pos_plyty if p_.ident == "PL-D")
    equ = next(w for w in pz.wyniki if "EQU" in w.nazwa)
    wz = next(w for w in equ.warunki)
    lc = 11.6 - 10.0
    gc = next(e for e in g.el if e.id == "PL-D").zest.g_k
    close(wz.E, (1.1 * gc + 1.5 * 4.0) * lc ** 2 / 2, 0.02, "M_dst wspornika")
    assert wz.ok
    ug = [w for w in pz.podpozycje[0].wyniki if "ugięcie" in w.nazwa]
    assert ug and "K = 0,4" in ug[0].nazwa


def test_plyta_fundamentowa_bez_dzialki():
    """Wariant: płyta fundamentowa zamiast ław, brak pliku działki (teren domyślny) — ścieżka Winklera i osiadania."""
    import copy
    import yaml
    from lamela.model import Model
    raw = copy.deepcopy(yaml.safe_load(B_TEST.read_text(encoding="utf-8")))
    raw["fundamenty"] = {"typ": "plyta", "elementy": [{"id": "PF1", "obrys": [[-0.4, -0.4], [10.4, -0.4], [10.4, 8.4], [-0.4, 8.4]],
                                                        "h": 0.30, "spod": -0.60}]}
    an = AnalizaKonstrukcji(Model(raw, None), Parametry()).uruchom()
    pf = next(pz for pz in an.pos_fund if pz.ident == "PF1")
    assert any("Winkler" in w.nazwa for w in pf.wyniki) and any("Osiadanie" in w.nazwa for w in pf.wyniki)


def test_sciana_nosna_na_stropie():
    """Wariant: ściana nośna piętra S1-05 przesunięta (x = 5,0 m) — bez ściany poniżej → obciążenie liniowe stropu ST1
    (reakcja dachu + ciężar ściany) i ostrzeżenie o konieczności podciągu."""
    import copy
    import yaml
    from lamela.model import Model
    raw = copy.deepcopy(yaml.safe_load(B_TEST.read_text(encoding="utf-8")))
    for w in raw["sciany"]:
        if w["id"] == "S1-05":
            w["os"] = [[5.0, 0.0], [5.0, 8.0]]
        if w["id"] == "S1-07":
            w["os"] = [[5.0, 4.5], [10.0, 4.5]]
    raw["otwory"] = [o for o in raw["otwory"] if o["sciana"] not in ("S1-05",)]
    raw["pomieszczenia"] = [r for r in raw["pomieszczenia"] if r["kond"] != "P1"]
    an = AnalizaKonstrukcji(Model(raw, yaml.safe_load(D_TEST.read_text(encoding="utf-8"))), Parametry()).uruchom(scisle=True)
    st1 = next(g for g in an.grupy if g.nazwa == "ST1")
    assert any("S1-05 bez podparcia" in o for _, _, _, o in st1.linie)
    assert any("S1-05" in u and "bez ściany poniżej" in u for u in an.uwagi)


def test_mur_przesklepienie():
    m = Mur()
    r = murm.sciana_luk(1.33, 2.86, 0.18, m)
    close(r.warunki[0].R, 4.504 * 1000 * (0.18 / 2.86) ** 2, 0.001, "q_lat,d = f_d(t/l_a)²")


# ==================================================================================================
# 6. Niezależne przeliczenie ręczne 3 pozycji (wzory zamknięte, bez funkcji biblioteki)
# ==================================================================================================
def porownanie_reczne(an) -> list[dict]:
    p = an.p
    out = []
    # --- (1) płyta D1, pole P2 (5,80 × 8,00 m, brzegi USSS) — metoda pasmowa z rozdziałem obciążeń (zgodność ugięć
    #     pasm środkowych; bez momentów skręcających — oszacowanie górne dla M_x w przęśle)
    d1 = next(pz for pz in an.pos_plyty if pz.ident == "D1")
    P2 = next(d for d in d1.dane["pola"] if d["brzegi"] == "USSS")
    lx, ly = P2["lx"], P2["ly"]
    gk = obc.zestawienie_przegrody(an.m, "SD-D1", grubosc_konstr=0.2).g_k
    sk = 0.8 * p.s_k
    qd = max(1.35 * gk + 1.5 * 0.5 * sk, 0.85 * 1.35 * gk + 1.5 * sk)
    cx, cy = 2 / 384, 5 / 384                         # pasmo x: utwierdzone–przegubowe; y: swobodnie podparte
    kx = cy * ly ** 4 / (cx * lx ** 4 + cy * ly ** 4)
    Mx = 9 / 128 * kx * qd * lx ** 2
    Mp = -kx * qd * lx ** 2 / 8
    out.append({"poz": "D1 / P2", "wielkosc": "M_x,przęsło [kNm/m]", "reczne": Mx, "biblioteka_MES": P2["Mx"],
                "biblioteka_tabl": P2["Mx_tabl"],
                "opis": f"q_d = max(1,35·{f(gk, 3)} + 1,5·0,5·{f(sk)}; 0,85·1,35·{f(gk, 3)} + 1,5·{f(sk)}) = {f(qd, 3)} kN/m²; "
                        f"k_x = c_y·l_y⁴/(c_x·l_x⁴ + c_y·l_y⁴) = {f(kx, 4)}; M_x = 9/128·k_x·q_d·l_x² (pasmo bez skręcania — "
                        "górne oszacowanie)"})
    out.append({"poz": "D1 / P2", "wielkosc": "M_x,podpora [kNm/m]", "reczne": Mp, "biblioteka_MES": P2["Mgx"],
                "biblioteka_tabl": None, "opis": "M = −k_x·q_d·l_x²/8 (pasmo utwierdzone–przegubowe)"})
    # --- (2) belka B1 — obciążenie zastępcze równomierne z sumy reakcji płyty (charakterystycznych) + ciężar własny
    b1 = next(pz for pz in an.pos_belki if pz.ident == "B1")
    g = next(gg for gg in an.grupy if any(sid == "B1" for sid, _ in gg.belki))
    L_line = next(s.linia.length for s in g.podp_l if s.id == "B1")
    RG = max(g.fe.reakcja(g.res["G"], "B1"), 0)
    RQ = max(g.fe.reakcja(g.res["QA"], "B1"), 0) if "QA" in g.res else 0.0
    RS = max(g.fe.reakcja(g.res["S2"], "B1"), 0) if "S2" in g.res else 0.0
    bw, hb = 0.20, 0.30
    qG = RG / L_line + bw * hb * 25
    qQ = RQ / L_line
    qS = RS / L_line
    # taras (kat. A) i śnieg nie są łączone (PN-EN 1991-1-1 p. 3.3.2(1)) — wiodące jedno z nich
    qd_b = max(1.35 * qG + 1.5 * 0.7 * qQ, 0.85 * 1.35 * qG + 1.5 * qQ, 1.35 * qG + 1.5 * 0.5 * qS, 0.85 * 1.35 * qG + 1.5 * qS)
    Ls = 3.76                                         # rozstaw podpór: ściana S0-02 (x = 10,09 → 0) — słup SL1 (13,85)
    Mb = qd_b * Ls ** 2 / 8
    M_lib = b1.wyniki[0].kroki[0].wynik
    out.append({"poz": "B1", "wielkosc": "M_Ed,przęsło [kNm]", "reczne": Mb, "biblioteka_MES": M_lib, "biblioteka_tabl": None,
                "opis": f"q_G = ΣR_G/L + b·h·25 = {f(RG)}/{f(L_line)} + {f(bw * hb * 25)} = {f(qG)}; q_Q = {f(qQ)}; q_S = {f(qS)} "
                        f"kN/m; q_d = {f(qd_b)} kN/m; M = q_d·l²/8, l = {f(Ls)} m (rozkład równomierny zamiast rzeczywistego)"})
    # A_s (przekrój teowy, strefa ściskana w półce): x = d − √(d² − 2M/(b_eff·f_cd))
    fcd = 30 / 1.4 * 1000
    d = 0.5 - 0.037 - 0.008
    beff = min(0.2 + 0.2 * 0.85 * 3.82, 0.2 + 2 * 0.1 * 3.82 + 0.2 * 3.82, 1.2)
    x = d - math.sqrt(d * d - 2 * M_lib / (beff * fcd))
    As = M_lib / (435e3 * (d - x / 2)) * 1e6
    As_lib = next(w for w in b1.wyniki if "przęśle" in w.nazwa).As_req
    out.append({"poz": "B1", "wielkosc": "A_s,req [mm²]", "reczne": As, "biblioteka_MES": As_lib, "biblioteka_tabl": None,
                "opis": f"b_eff = {f(beff)} m, d = {f(d, 3)} m, x = d − √(d² − 2M/(b_eff·f_cd)) = {f(x * 1000, 1)} mm, "
                        "A_s = M/(f_yd·(d − x/2))"})
    # --- (3) ława L1 — nośność podłoża wzorem zał. D (warunki z odpływem, pasmo) i warunek ławy niezbrojonej
    l1 = next(pz for pz in an.pos_fund if pz.ident == "L1")
    Gk, Qk, D = l1.dane["G_k"], l1.dane["Q_k"], l1.dane["D"]
    B, h = 0.6, 0.3
    gr = p.grunt
    Gt = Gk + B * h * 25 + (B - 0.18) * (D - h) * 18
    Vd = max(1.35 * Gt + 1.5 * 0.7 * Qk, 0.85 * 1.35 * Gt + 1.5 * Qk)
    fi = math.radians(gr.fi_k)
    Nq = math.exp(math.pi * math.tan(fi)) * math.tan(math.pi / 4 + fi / 2) ** 2
    Ng = 2 * (Nq - 1) * math.tan(fi)
    qR = gr.gamma * D * Nq + 0.5 * gr.gamma * B * Ng
    Rd = qR * B / 1.4
    lib = next(w for w in l1.wyniki[0].warunki if "Nośność podłoża" in w.opis)
    out.append({"poz": "L1", "wielkosc": "V_d [kN/m]", "reczne": Vd, "biblioteka_MES": lib.E, "biblioteka_tabl": None,
                "opis": f"G = {f(Gk)} + ława {f(B * h * 25)} + odsadzki {f((B - 0.18) * (D - h) * 18)}; Q ≈ {f(Qk)} kN/m "
                        "(Q — suma obciążeń zmiennych, ψ₀ = 0,7 dla wszystkich — bezpiecznie)"})
    out.append({"poz": "L1", "wielkosc": "R_d [kN/m]", "reczne": Rd, "biblioteka_MES": lib.R, "biblioteka_tabl": None,
                "opis": f"N_q = {f(Nq, 3)}, N_γ = {f(Ng, 3)}; R_k/A' = γD·N_q + ½γB'N_γ = {f(qR, 1)} kPa; R_d = R_k·B/1,4"})
    sig = Vd / B / 1000
    ok_pl = 0.85 * h / ((B - 0.18) / 2) >= math.sqrt(3 * sig / (0.8 * 1.8 / 1.4))
    out.append({"poz": "L1", "wielkosc": "ława niezbrojona (12.13)", "reczne": float(ok_pl), "biblioteka_MES": float(
        "nie wymaga" in l1.wyniki[0].zbrojenie_poprz), "biblioteka_tabl": None, "opis": "1 — warunek spełniony"})
    return out


def test_porownanie_reczne():
    an = analiza()
    rows = porownanie_reczne(an)
    tol = {"M_x,przęsło [kNm/m]": 0.20, "M_x,podpora [kNm/m]": 0.10, "M_Ed,przęsło [kNm]": 0.15, "A_s,req [mm²]": 0.03,
           "V_d [kN/m]": 0.10, "R_d [kN/m]": 0.01, "ława niezbrojona (12.13)": 0.0}
    for r in rows:
        close(r["biblioteka_MES"], r["reczne"], tol[r["wielkosc"]], f"{r['poz']} {r['wielkosc']}")


def zapisz_porownanie(an, path: Path):
    rows = porownanie_reczne(an)
    L = ["# Niezależne przeliczenie ręczne wybranych pozycji — model testowy", "",
         "Porównanie wyników biblioteki z rachunkiem ręcznym (wzory zamknięte, bez funkcji biblioteki). Różnice wynikają z "
         "uproszczeń rachunku ręcznego (pasmo bez skręcania, obciążenie belki równomierne zamiast rzeczywistego rozkładu "
         "reakcji płyty, jedno obciążenie zmienne wiodące).", "",
         "| Pozycja | Wielkość | Ręcznie | Biblioteka (MES/obl.) | Biblioteka (tablice) | Różnica | Opis rachunku ręcznego |",
         "|---|---|---|---|---|---|---|"]
    for r in rows:
        dif = (r["biblioteka_MES"] - r["reczne"]) / r["reczne"] * 100 if r["reczne"] else 0.0
        L.append(f"| {r['poz']} | {r['wielkosc']} | {f(r['reczne'], 2)} | {f(r['biblioteka_MES'], 2)} | "
                 f"{f(r['biblioteka_tabl'], 2) if r['biblioteka_tabl'] is not None else '—'} | {f(dif, 1)}% | {r['opis']} |")
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")
    return rows


# ==================================================================================================
def demo(lamela: bool = False):
    DEMO.mkdir(parents=True, exist_ok=True)
    m = load_model(B_TEST, D_TEST)
    an = AnalizaKonstrukcji(m, Parametry.z_wymagan(), rys_dir=DEMO / "rys").uruchom()
    fmd = generuj_raport(an, DEMO, tytul="Obliczenia statyczne — model testowy (demo biblioteki)",
                         status="PRZYKŁAD – MODEL TESTOWY PIPELINE'U (nie jest projektem Domu LAMELA) – NIE DO ZŁOŻENIA")
    zapisz_porownanie(an, DEMO / "porownanie_reczne.md")
    print(f"demo: {fmd}")
    if lamela:
        bud = ROOT / "model" / "budynek.yaml"
        dz = ROOT / "model" / "dzialka.yaml"
        if bud.exists():
            out = ROOT / "build" / "test" / "konstrukcja_lamela"
            t = time.time()
            ml = load_model(bud, dz if dz.exists() else None, strict=False)
            anl = AnalizaKonstrukcji(ml, Parametry.z_wymagan(), rys_dir=out / "rys").uruchom()
            f2 = generuj_raport(anl, out, status="WERSJA ROBOCZA — model w opracowaniu")
            n = sum(len(g.podpozycje) for g in anl.pozycje)
            print(f"LAMELA: {f2} ({n} pozycji, {time.time() - t:.0f} s)")
        else:
            print("LAMELA: brak model/budynek.yaml — pominięto")


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bez-demo", action="store_true")
    ap.add_argument("--lamela", action="store_true")
    a = ap.parse_args(argv)
    tests = [(n, fn) for n, fn in globals().items() if n.startswith("test_") and callable(fn)]
    ok = fail = 0
    t0 = time.time()
    for n, fn in tests:
        t1 = time.time()
        try:
            fn()
            ok += 1
            print(f"PASS  {n}  ({time.time() - t1:.1f} s)", flush=True)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"FAIL  {n}: {e}", flush=True)
            traceback.print_exc(limit=3)
    if not a.bez_demo:
        try:
            demo(a.lamela)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"FAIL  demo: {e}")
            traceback.print_exc(limit=5)
    print(f"\n{ok} zaliczonych, {fail} niezaliczonych, czas {time.time() - t0:.0f} s")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
