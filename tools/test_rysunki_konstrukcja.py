#!/usr/bin/env python3
"""Testy generatora rysunków konstrukcyjnych (``lamela.views.konstrukcja``, ``konstrukcja_dane``) i analizy MES płyty
fundamentowej (``lamela.obliczenia.konstrukcja.plyta_fundamentowa``).

Uruchomienie:
    PYTHONPATH=src python3 tools/test_rysunki_konstrukcja.py          # testy jednostkowe (szybkie)
    PYTHONPATH=src python3 tools/test_rysunki_konstrukcja.py --model  # dodatkowo: dane z model/budynek.yaml
Funkcje test_* są zgodne z pytest.

Źródła wartości wzorcowych:
[E2]  PN-EN 1992-1-1:2008 + NA:2010 — (9.1N) A_s,min, 9.2.1.1(3) A_s,max, 9.3.1.1(3) s_max, tabl. 8.1N (trzpień).
[ISO] PN-EN ISO 3766:2006 — wymiary zewnętrzne kształtów; odliczenie gięcia jak BS 8666:2020 tabl. 3 (0,5·r + φ).
[H]   M. Hetényi, *Beams on Elastic Foundation*, Univ. of Michigan Press 1946, rozdz. II: belka nieskończona pod siłą P:
      w₀ = P·λ/(2k), M₀ = P/(4λ), M(x) = M₀·e^(−λx)(cos λx − sin λx), λ = ⁴√(k/(4EI)).
[B]   J.E. Bowles, *Foundation Analysis and Design*, 5th ed., McGraw-Hill 1996, (5-16a) — I_c prostokąta wiotkiego:
      m = 1 → I_c = 1,122; m = 2 → 1,532 (wartości tablicowe tabl. 5-2 × 4 dla środka, ν osobno).
"""
from __future__ import annotations

import math
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.obliczenia.konstrukcja.materialy import pole_preta  # noqa: E402
from lamela.views import konstrukcja_dane as KD  # noqa: E402


def test_dobierz_siatke_warunki_ec2():
    """A_s,prov ≥ max(A_s,req; A_s,min), s ≤ s_max, rozstaw w świetle ≥ max(φ; d_g + 5; 20) [E2]."""
    for h, req, amin in ((0.25, 300.0, 273.0), (0.22, 850.0, 257.0), (0.18, 0.0, 201.0), (0.25, 1400.0, 273.0)):
        fi, s, As = KD.dobierz_siatke(req, amin, h)
        assert As + 1e-6 >= max(req, amin), (h, req, fi, s, As)
        assert s <= KD.s_max_plyty(h) + 1e-9
        assert s - fi >= max(fi, 16 + 5, 20) - 1e-9
        assert abs(As - pole_preta(fi) * 1000 / s) < 1e-6
    # najmniejsza masa: 300 mm²/m przy h = 0,25 → φ10 co 250 (314 mm²/m) — φ8 wymagałoby s = 160 (314) — ta sama masa?
    fi, s, As = KD.dobierz_siatke(300.0, 0.0, 0.25)
    assert As < 340.0
    # s_max: główne 2h ≤ 250 (strefa M_max); h = 0,10 → 200 mm
    assert KD.s_max_plyty(0.10) == 200.0 and KD.s_max_plyty(0.30) == 250.0
    # A_s,min (9.1N): C25/30 f_ctm = 2,6 MPa, d = 200 mm → max(0,26·2,6/500; 0,0013)·1000·200 = 270,4 mm²/m
    assert abs(KD.as_min_plyty(0.25, 0.20, 2.6) - 270.4) < 0.1


def test_dobierz_prety_belki():
    n, fi, As = KD.dobierz_prety_belki(900.0, 0.25, 25.0, 8)
    assert As >= 900.0 and n >= 2
    smin = max(fi, 21, 20)
    assert n * fi + (n - 1) * smin <= 250 - 2 * 25 - 2 * 8 + 1e-6


def test_dlugosci_pretow_iso3766():
    """Odliczenie gięcia 90°: Δ = 0,5·r + φ, r = φ_m/2, φ_m = 4φ (φ ≤ 16) [ISO], [E2 tabl. 8.1N]."""
    assert KD.trzpien(12) == 48 and KD.trzpien(20) == 140
    assert abs(KD.odgiecie(12) - (0.5 * 24 + 12)) < 1e-9
    assert KD.dlugosc_preta(12, "00", (5000,)) == 5000
    assert abs(KD.dlugosc_preta(12, "11", (2000, 300)) - (2300 - 24)) < 1e-9
    assert abs(KD.dlugosc_preta(10, "21", (200, 1000, 200)) - (1400 - 2 * 20)) < 1e-9
    L51 = KD.dlugosc_preta(8, "51", (200, 500))
    assert 1400 + 2 * 80 - 3 * 16 < L51 < 1400 + 2 * 130
    p = KD.Pret(12, "11", (2004, 296), 5, "T")
    assert p.wym == (2000, 300) and p.L_mm == 2280.0 and p.n == 5


def test_zestawienie_scalanie_i_masy():
    z = KD.Zestawienie()
    a = z.dodaj(KD.Pret(10, "00", (3000,), 4, "A"))
    b = z.dodaj(KD.Pret(10, "00", (3000,), 6, "B"))
    c = z.dodaj(KD.Pret(12, "00", (3000,), 2, "B"))
    assert a is b and a.n == 10 and a.nr == 1 and c.nr == 2
    assert z.srednice() == [10, 12]
    mj = lambda fi: math.pi * (fi / 2000.0) ** 2 * 7850.0      # masa 1 m pręta [kg/m], ρ = 7850 kg/m³  # noqa: E731
    m10 = 10 * 3.0 * mj(10)
    assert abs(mj(10) - 0.617) < 0.001 and abs(mj(12) - 0.888) < 0.001
    assert abs(z.masy()[10] - m10) < 1e-6 and abs(z.masa - (m10 + 2 * 3.0 * mj(12))) < 1e-6


def test_skanowanie_pretow_w_wieloboku():
    """Rozkład prętów: pozycje t_k = t₀ + (k + ½)·Δ, Δ ≤ s; wielobok L — dwie grupy długości."""
    from shapely.geometry import Polygon
    P = Polygon([(0, 0), (4, 0), (4, 1), (1, 1), (1, 3), (0, 3)])
    g = KD.skanuj(P, "x", 0.0, 3.0, 0.2)
    dl = sorted({round(b - a, 2) for a, b, ts in g})
    assert dl == [1.0, 4.0]
    n = sum(len(ts) for a, b, ts in g)
    assert n == 15
    ts = sorted(t for a, b, tt in g for t in tt)
    assert abs(ts[0] - 0.1) < 1e-9 and max(b - a for a, b in zip(ts[:-1], ts[1:])) <= 0.2 + 1e-9


def test_kontrola_as_rejestr():
    D = KD.DaneKonstr(an=None)
    r = KD.rejestruj(D, "ST1", "pole P1 — dół x", "2.1", 250.0, 257.0, 265.0, "Ø8 co 19", s=190, s_max=250,
                     As_max=0.04 * 0.22 * 1e6)
    assert r["ok"] and r["zapas"] > 0
    r = KD.rejestruj(D, "ST1", "pole P2 — dół x", "2.1", 400.0, 257.0, 265.0, "Ø8 co 19", s=190, s_max=250)
    assert not r["ok"]
    r = KD.rejestruj(D, "ST1", "pole P3 — dół x", "2.1", 100.0, 100.0, 300.0, "Ø8 co 30", s=300, s_max=250)
    assert not r["ok"] and "s_max" in r["uwagi"]


def test_parsowanie_opisow_biblioteki():
    assert KD.fi_s("φ10 co 15 cm") == (10, 150.0)
    assert KD.fi_s("dołem φ12 co 12,5 cm") == (12, 125.0)
    assert KD.n_fi("4φ12 (A_s = 4,52 cm²)") == (4, 12)


def test_k_s_bowles():
    """I_c: m = 1 → 1,122; m = 2 → 1,532 [B]; k_s = E_s/(α·B·(1−ν²)·I_c)."""
    from lamela.obliczenia.konstrukcja.plyta_fundamentowa import k_s_z_geotechniki, wsp_wplywu_prostokata
    assert abs(wsp_wplywu_prostokata(1.0) - 1.122) < 0.002
    assert abs(wsp_wplywu_prostokata(2.0) - 1.532) < 0.002
    w = k_s_z_geotechniki(10.0, 20.0, 80000.0, nu=0.3)
    Es = 80000 * 1.3 * 0.4 / 0.7
    assert abs(w.E_s - Es) < 1e-6
    assert abs(w.k_s - Es / (0.85 * 10.0 * 0.91 * 1.532)) / w.k_s < 0.002
    assert abs(w.k_min * 4 - w.k_max) < 1e-6


def test_hetenyi():
    """MES płyty na sprężynach (pasmo 24 × 1 m, siła liniowa w środku) vs belka nieskończona [H]."""
    from lamela.obliczenia.konstrukcja.plyta_fundamentowa import weryfikacja_hetenyi
    r = weryfikacja_hetenyi(siatka=0.2)
    assert r["L_lambda"] > 10.0                 # pasmo „nieskończone” (λL > 2π)
    assert r["blad_w"] < 0.01, r
    assert r["blad_M"] < 0.03, r


def test_kontakt_jednostronny():
    """Płyta 6 × 6 m, siła w narożu: kontakt jednostronny odrywa przeciwległe naroże; równowaga ΣR = P."""
    import numpy as np
    from shapely.geometry import box
    from lamela.obliczenia.konstrukcja.plyta_fundamentowa import PlytaWinkler
    pl = PlytaWinkler(box(0, 0, 6, 6), 0.25, 31e6, 5000.0, siatka=0.5)
    f = pl.wektor(0.0, punkty=[((0.25, 0.25), 500.0)])
    r = pl.rozwiaz_kontakt(f)
    assert not r.aktywne.all() and r.aktywne.any()
    assert abs(float((r.p * pl.A_el).sum()) - 500.0) / 500.0 < 0.05
    assert float(r.p.min()) >= 0.0


def test_model_dane(sciezka=ROOT / "model" / "budynek.yaml"):
    """Dane z modelu: poziomy płyt z polami i zbrojeniem, pręty poziomu z numeracją, zbrojenie ≥ wymagane."""
    from lamela.model import load_model
    from lamela.views.common import ViewContext
    m = load_model(str(sciezka), str(sciezka.with_name("dzialka.yaml")), strict=False)
    ctx = ViewContext(m, None, {}, [], {}, str(sciezka))
    D = KD.dane(ctx)
    assert D.poziomy, "brak poziomów płyt"
    for lv in D.poziomy:
        P = KD.prety_poziomu(D, lv)
        assert P["dol"] and P["zest"].prety
        for g in P["dol"] + P["gora"]:
            if g.wym is not None and g.rola in ("przeslo", "podpora", "wspornik"):
                assert pole_preta(g.pret.fi) * 1000 / g.s + 1e-6 >= g.wym.As_req, (g.element, g.pole, g.rola)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    if "--model" not in argv:
        tests = [t for t in tests if t[0] != "test_model_dane"]
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
    print(f"\n{ok} zaliczonych, {fail} niezaliczonych, czas {time.time() - t0:.0f} s")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
