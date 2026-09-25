#!/usr/bin/env python3
"""Testy automatyczne pakietu `lamela.obliczenia.mostki2d` (mostki cieplne 2D wg PN-EN ISO 10211:2017).

Uruchomienie:
    PYTHONPATH=src python3 tools/test_mostki2d.py            # pełny (walidacja + katalog modelu testowego, ~40 s)
    PYTHONPATH=src python3 tools/test_mostki2d.py --szybko   # bez katalogu i wykresów (~10 s)
Wyniki pomocnicze: build/test/mostki2d/ (katalog ignorowany przez git).
Funkcje test_* są zgodne z pytest. WALIDACJA MUSI PRZECHODZIĆ (ISO 10211 zał. C: ±0,1 K, ±0,1 W/m).
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

from lamela.obliczenia.mostki2d import geometria as G  # noqa: E402
from lamela.obliczenia.mostki2d import walidacja as V  # noqa: E402
from lamela.obliczenia.mostki2d import wyniki as R  # noqa: E402
from lamela.obliczenia.mostki2d.siatka import podzial, siatka_dla_wezla  # noqa: E402
from lamela.obliczenia.mostki2d.solver import ModelMOS  # noqa: E402

B_TEST = ROOT / "model" / "test" / "dom_testowy.yaml"
D_TEST = ROOT / "model" / "test" / "dzialka_testowa.yaml"
OUT = ROOT / "build" / "test" / "mostki2d"


def _model():
    from lamela.model import load_model
    return load_model(str(B_TEST), str(D_TEST))


def _sz():
    return G.warstwy_z_modelu(_model(), "SZ1")


# ------------------------------------------------------------------------------------------ walidacja
def test_iso10211_przypadek1():
    w, wa = V.waliduj_przypadek1()
    assert len(w.wiersze) == 28
    assert w.ok, f"przypadek 1: max |Δθ| = {w.max_odch_T:.4f} K > 0,1 K"
    assert wa.ok, f"przypadek 1 vs Fourier: {wa.max_odch_T:.4f} K"


def test_iso10211_przypadek2():
    w = V.waliduj_przypadek2()
    assert w.max_odch_T <= V.TOL_T, f"przypadek 2: max |Δθ| = {w.max_odch_T:.4f} K"
    assert abs(w.odch_phi) <= V.TOL_PHI, f"przypadek 2: ΔΦ = {w.odch_phi:.4f} W/m"
    assert w.ok


def test_analityczne_1d_i_naroze():
    w = V.waliduj_1d()
    assert w.ok, w.max_odch_T
    n = V.waliduj_naroze()
    assert n.ok, n.wiersze


def test_fourier_srodek_kwadratu():
    # środek pełnego kwadratu z jedną krawędzią 20 °C = 20/4 (superpozycja)
    assert abs(V.przypadek1_analityczny(1.0, 1.0) - 5.0) < 1e-9


# ------------------------------------------------------------------------------------------ elementy
def test_pustki_iso6946():
    # ISO 6946:2017 tab. 8 (niewentylowane, ε = 0,9): 25 mm — w górę 0,16; poziomo 0,18; w dół 0,19 m²K/W
    for kier, R_ref in (("gora", 0.16), ("poziomo", 0.18), ("dol", 0.19)):
        R_ = 0.025 / G.lambda_eq_pustki(0.025, kier)
        assert abs(R_ - R_ref) < 0.006, (kier, R_)
    # małe pustki: szerokość b < 10 d → mniejsze h_r → większy opór niż warstwy
    assert G.lambda_eq_pustki(0.02, "poziomo", b=0.02) < G.lambda_eq_pustki(0.02, "poziomo")


def test_siatka_podzial():
    e = podzial(0.0, 1.0, 0.002, 0.05, 1.25, 2)
    assert abs(e[0]) < 1e-15 and abs(e[-1] - 1) < 1e-15 and np.all(np.diff(e) > 0)
    assert np.diff(e).max() <= 0.05 + 1e-12 and np.diff(e)[0] <= 0.002 + 1e-12
    e2 = podzial(0.0, 0.0015, 0.002, 0.05, 1.25, 2)
    assert len(e2) == 3


def test_U_13370():
    U, dt = G.U_podlogi_13370(8.0, 0.4, 3.0)
    assert 0.1 < U < 0.3 and dt > 0.4
    U2, _ = G.U_podlogi_13370(8.0, 0.4, 5.0)
    assert U2 < U


# ------------------------------------------------------------------------------------------ węzły
def test_sciana_psi_zero_i_bilans():
    w = R.oblicz_wezel(G.wezel_sciana_1d(_sz()))
    p = w.psi_glowne
    assert abs(p.psi_e) < 1e-6 and abs(p.psi_i) < 1e-6
    assert w.bilans < R.KRYT_BILANSU


def test_naroze_psi_e_ujemne_psi_i_dodatnie():
    w = R.oblicz_wezel(G.wezel_naroznik_zewnetrzny(_sz()))
    p = w.psi_glowne
    assert p.psi_e < 0 < p.psi_i
    # ψ_i − ψ_e = U·Σ(l_e − l_i) = U·2d
    U = G.U_warstw(_sz())
    assert abs((p.psi_i - p.psi_e) - U * 2 * G.grubosc(_sz())) < 1e-9
    assert w.zbieznosc_ok and w.bilans < R.KRYT_BILANSU
    assert w.fRsi_ok


def test_kierunki_Rs():
    m = _model()
    wz = G.wezel_attyka(_sz(), G.warstwy_z_modelu(m, "SD-D1"))
    s = siatka_dla_wezla(wz)
    mod = ModelMOS(wz, s)
    mod.rozwiaz()
    b = mod.b
    wew = np.array([wz.strefy[k].rodzaj == "wewn" for k in b.strefa])
    sufit = wew & (b.orient == 1) & (b.strona < 0)        # strefa pod komórką → sufit, strumień w górę
    sciana = wew & (b.orient == 0)
    assert np.allclose(mod.Rs[sufit], 0.10) and np.allclose(mod.Rs[sciana], 0.13)
    assert np.allclose(mod.Rs[~wew], 0.04)
    wz2 = G.wezel_wspornik(_sz(), 0.2, None, G.warstwy_z_modelu(m, "POD-1"), [], wysieg=1.0)
    mod2 = ModelMOS(wz2, siatka_dla_wezla(wz2))
    mod2.rozwiaz()
    b2 = mod2.b
    wew2 = np.array([wz2.strefy[k].rodzaj == "wewn" for k in b2.strefa])
    podl = wew2 & (b2.orient == 1) & (b2.strona > 0)      # strefa nad komórką → podłoga, strumień w dół
    assert podl.any() and np.allclose(mod2.Rs[podl], 0.17)
    mf = ModelMOS(wz, s, "fRsi")
    assert np.allclose(mf.Rs[wew], 0.25)


def test_trzy_temperatury_symetria_i_wagi():
    sz = _sz()
    wg = [G.Warstwa(G.MATERIALY_DOMYSLNE["SIL24"], 0.24, True)]
    w = R.oblicz_wezel(G.wezel_garaz(sz, wg, przerwa_izolacji=True))
    assert abs(w.L[("i", "u")] - w.L[("u", "i")]) < 1e-12
    assert abs(sum(w.f["g"].values()) - 1.0) < 1e-9
    assert len(w.psi) == 3


def test_lacznik_zmniejsza_psi():
    m = _model()
    pod = G.warstwy_z_modelu(m, "POD-1")
    b1 = R.oblicz_wezel(G.wezel_wspornik(_sz(), 0.2, None, pod, [], wysieg=1.2))
    b0 = R.oblicz_wezel(G.wezel_wspornik(_sz(), 0.2, None, pod, [], wysieg=1.2, lacznik=None))
    assert b1.psi_glowne.psi_e < 0.5 * b0.psi_glowne.psi_e
    assert b1.f["f_Rsi"] > b0.f["f_Rsi"]


def test_katalog_modelu_testowego():
    from lamela.obliczenia.mostki2d.katalog import dlugosci_z_modelu, katalog_z_modelu
    m = _model()
    wezly = katalog_z_modelu(m)
    ids = [w.id for w in wezly]
    for k in ("WZ-C1", "WZ-IF1", "WZ-B1", "WZ-B0", "WZ-R1", "WZ-W1", "WZ-W2", "WZ-GF1", "WZ-G1", "WZ-G2", "WZ-RS1"):
        assert k in ids, k
    wyn = [R.oblicz_wezel(w, katalog_wykresow=OUT / "rys") for w in wezly]
    for w in wyn:
        assert w.zbieznosc_ok, (w.wezel.id, w.zmiana)
        assert w.bilans < R.KRYT_BILANSU, (w.wezel.id, w.bilans)
        assert all(Path(p).exists() for p in w.wykresy.values())
        assert math.isfinite(w.psi_glowne.psi_e)
        assert 0 < w.f["f_Rsi"] < 1
    # węzły z ciągłą izolacją spełniają f_Rsi ≥ 0,72
    for w in wyn:
        if w.wezel.id != "WZ-B0":
            assert w.fRsi_ok, (w.wezel.id, w.f["f_Rsi"])
    dl, _ = dlugosci_z_modelu(m)
    txt = R.raport_katalogu(wyn, OUT / "katalog_mostkow.md", "Katalog mostków — model testowy", dlugosci=dl)
    assert "H_TB" in txt and "WZ-GF1" in txt


def test_raport_walidacji():
    txt = V.raport_walidacji(plik=OUT / "walidacja_ISO10211.md")
    assert "NIE SPEŁNIA" not in txt and txt.count("**SPEŁNIA**") == 5


# ------------------------------------------------------------------------------------------ runner
def main() -> int:
    szybko = "--szybko" in sys.argv
    testy = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    if szybko:
        testy = [(n, f) for n, f in testy if n not in ("test_katalog_modelu_testowego",)]
    OUT.mkdir(parents=True, exist_ok=True)
    bledy = 0
    for n, f in testy:
        t = time.time()
        try:
            f()
            print(f"OK    {n} ({time.time() - t:.1f} s)")
        except Exception:
            bledy += 1
            print(f"BŁĄD  {n}")
            traceback.print_exc()
    print(f"\n{len(testy) - bledy}/{len(testy)} testów zaliczonych")
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
