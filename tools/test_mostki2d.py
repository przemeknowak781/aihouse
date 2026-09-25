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


def test_przypadek2_niezalezny_od_siatki():
    # regresja (weryfikacja niezależna, uwaga 1): G na styku Al/drewno/korek — |ΔG| < 0,1 K przy h_min 0,5 i 0,1 mm
    wz = V.wezel_przypadek2()
    G_ = []
    for h_min, h_max in ((0.5e-3, 5e-3), (0.1e-3, 2e-3)):
        roz = ModelMOS(wz, siatka_dla_wezla(wz, h_min=h_min, h_max=h_max)).rozwiaz()
        x, y = V.PRZYPADEK2_PUNKTY["G"]
        g = roz.temperatura(x * 1e-3, y * 1e-3)
        assert abs(g - V.PRZYPADEK2_T["G"]) < 0.1, (h_min, g)
        assert abs(g - 16.334) < 0.01, (h_min, g)          # niezależny solver węzłowy
        G_.append(g)
    assert abs(G_[0] - G_[1]) < 0.005
    assert V.waliduj_przypadek2_siatki().ok


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


def test_siatka_bez_przepelnienia_i_granice():
    e = podzial(0.0, 20.0, 0.003, 0.003, 1.25, 2)          # wcześniej OverflowError
    d = np.diff(e)
    assert abs(e[-1] - 20.0) < 1e-12 and d.max() <= 0.003 * (1 + 1e-9)
    from lamela.obliczenia.mostki2d.siatka import krawedzie
    k = krawedzie(np.array([0.0, 0.1, 0.1001, 0.3]), 0.002, 0.05, 1.25, 2)
    d = np.diff(k)
    assert (d[1:] / d[:-1]).max() <= 2.0 + 1e-9 and (d[:-1] / d[1:]).max() <= 2.0 + 1e-9


def test_szczeliny_wykrywane():
    from shapely.geometry import box
    M = G.Material

    def wezel(gap):
        ob = [G.Obszar(box(0, 0, 0.18, 1), M("SIL", 0.77)), G.Obszar(box(0.18 + gap, 0, 0.38, 1), M("EPS", 0.031))]
        st = G.strefy_z_dopelnienia(ob, box(-0.05, 0, 0.43, 1), [((-0.025, 0.5), G._nas("i", 20, "wewn")),
                                                                   ((0.405, 0.5), G._nas("e", -18, "zewn"))])
        return G.Wezel("x", "x", "t", ob, st, przekroj="poziomy")
    r = ModelMOS(wezel(2e-7), siatka_dla_wezla(wezel(2e-7))).rozwiaz()   # < 0,5 µm — przyciąganie do 1 µm
    assert abs(r.Phi_grup()["i"] / 38 - 1 / (0.13 + 0.18 / 0.77 + 0.2 / 0.031 + 0.04)) < 1e-4
    for gap in (2e-6, 1e-4, 2e-3):
        try:
            ModelMOS(wezel(gap), siatka_dla_wezla(wezel(gap)))
        except ValueError as e:
            assert "szczelina" in str(e)
        else:
            raise AssertionError(f"szczelina {gap} m nie wykryta")


def test_theta_si_w_wierzcholku():
    # naroże słabo ocieplone (R_si = 0,25): minimum w narożu wewn. (0, 0), odniesienie 10,737 °C (siatka zbieżna)
    wl = [G.Warstwa(G.Material("TG", 0.4), 0.015), G.Warstwa(G.Material("CEG", 0.77), 0.25, True),
          G.Warstwa(G.Material("EPS", 0.04), 0.05)]
    wz = G.wezel_naroznik_zewnetrzny(wl, theta_i=20, theta_e=-18)
    t, x, y, k = ModelMOS(wz, siatka_dla_wezla(wz), "fRsi").rozwiaz().theta_si_min()
    assert k == -1 and abs(x) < 1e-9 and abs(y) < 1e-9
    assert abs(t - 10.737) < 0.02, t


def test_systemy_wymiarow_psi_oi():
    m = _model()
    sz = _sz()
    U = G.U_warstw(sz)
    c = R.oblicz_wezel(G.wezel_naroznik_zewnetrzny(sz)).psi_glowne
    assert abs(c.psi_oi - c.psi_i) < 1e-12
    pod = G.warstwy_z_modelu(m, "POD-1")
    f = R.oblicz_wezel(G.wezel_wspornik(sz, 0.2, None, pod, [G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.01)],
                                        wysieg=0.0)).psi_glowne
    assert abs(f.psi_oi - f.psi_e) < 1e-9                   # „od podłogi do podłogi” ⇒ ψ_oi = ψ_e
    wz = G.wezel_oscieze_okna(sz, polozenie="w_izolacji")   # x0 = −0,03 (rama za murem)
    w = R.oblicz_wezel(wz).psi_glowne
    Uw = G.U_w_okna(0.95, 0.50, 0.115)
    assert abs((w.psi_oi - w.psi_e) - (U - Uw) * (-0.03)) < 1e-9
    a = R.oblicz_wezel(G.wezel_attyka(sz, G.warstwy_z_modelu(m, "SD-D1"))).psi_glowne
    assert a.psi_oi > a.psi_e + 0.05                          # attyka: ψ_oi ≈ ψ_i ≫ ψ_e


def test_attyka_wentylowana_i_legary():
    m = _model()
    assert G.material_z_modelu(m, "LEGARY").rodzaj == "powietrze"        # „(pustka)” — niewentylowana
    wd = [G.Warstwa(G.Material("PW", 0.5, "pustka wentylowana", rodzaj="powietrze_went"), 0.05),
          G.Warstwa(G.Material("PIR", 0.022), 0.2), G.Warstwa(G.Material("ZB", 2.3), 0.2, True)]
    assert len(G.pomin_pustki_wentylowane(wd)) == 2
    try:
        G.wezel_attyka(_sz(), wd)
    except ValueError:
        pass
    else:
        raise AssertionError("attyka z pustką wentylowaną powinna zgłosić błąd")


def test_otwory_i_dlugosci_oi():
    from lamela.obliczenia.mostki2d.katalog import B_prim, dlugosci_z_modelu, otwory_zewnetrzne
    m = _model()
    otw = otwory_zewnetrzne(m)
    ids = {o.id for o in otw}
    assert not ids & {"O0-06", "O0-07", "O1-08", "O1-09", "O1-10", "O1-11"}   # ściany wewn./działowe, typ otwor
    assert {"O0-01", "O0-03", "O1-03"} <= ids
    dl, _ = dlugosci_z_modelu(m)
    assert abs(dl["WZ-W1"] - sum(2 * o.wys for o in otw)) < 1e-9
    assert abs(dl["WZ-T1"] - 5.1) < 1e-9 and abs(dl["WZ-T3"] - 2.4) < 1e-9 and abs(dl["WZ-T2"] - 3.6) < 1e-9
    assert abs(dl["WZ-N1"] + dl["WZ-N2"] - sum(o.szer for o in otw)) < 1e-9
    assert abs(dl["WZ-P1"] - sum(o.szer for o in otw if o.parapet > 0.05)) < 1e-9
    B, _ = B_prim(m)
    assert 4.5 < B < 5.0


def test_eksport_do_fizyka_mostki():
    import json
    from lamela.obliczenia.fizyka.mostki import psi_z_symulacji, wczytaj_wyniki_symulacji
    sz = _sz()
    w = R.oblicz_wezel(G.wezel_naroznik_zewnetrzny(sz))
    plik = OUT / "eksport_test.json"
    d = R.eksport_wynikow([w], {"WZ-C1": 11.54}, plik)
    assert d["WZ-C1"]["dlugosc_oi"] == 11.54 and "psi_oi" in d["WZ-C1"]
    wcz = wczytaj_wyniki_symulacji(plik)
    psi, rodz = psi_z_symulacji(wcz["WZ-C1"], wcz["WZ-C1"]["typ"])
    assert rodz == "Ψ_oi" and abs(psi - w.psi_glowne.psi_oi) < 1e-5
    assert json.loads(plik.read_text(encoding="utf-8"))["WZ-C1"]["system_wymiarow"].startswith("oi")


def test_bilans_wymuszany():
    from shapely.geometry import box
    M = G.Material
    # dwie izolowane części materiału (brak styku) z pustką przy brzegu ramki — bilans poprawny, ale strefa i ma
    # kontakt tylko z jedną częścią: wynik akceptowany; sprawdzamy, że kryterium bilansu jest egzekwowane w
    # _rozwiaz_zbieznie (monkeypatch progu)
    ob = [G.Obszar(box(0, 0, 0.2, 1), M("A", 1.0))]
    st = [G.Strefa("i", box(-0.05, 0, 0, 1), 20.0, "wewn", "i", Rs=0.13),
          G.Strefa("e", box(0.2, 0, 0.25, 1), -18.0, "zewn", "e", Rs=0.04)]
    wz = G.Wezel("b", "b", "t", ob, st, przekroj="poziomy")
    stary = R.KRYT_BILANSU
    try:
        R.KRYT_BILANSU = 0.0
        R.oblicz_wezel(wz)
    except ValueError as e:
        assert "bilans" in str(e)
    else:
        raise AssertionError("brak kontroli bilansu")
    finally:
        R.KRYT_BILANSU = stary


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
    for k in ("WZ-C1", "WZ-IF1", "WZ-B1", "WZ-B0", "WZ-R1", "WZ-W1", "WZ-W2", "WZ-N1", "WZ-N2", "WZ-P1", "WZ-GF1",
              "WZ-T1", "WZ-T2", "WZ-T3", "WZ-G1", "WZ-G2", "WZ-RS1"):
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
    assert "H_TB" in txt and "WZ-GF1" in txt and "ψ_oi" in txt
    H, wiersze = R.zestawienie_HTB(wyn, dl, "oi")
    assert len(wiersze) == len([k for k in dl if k in ids]) and 10.0 < H < 40.0
    ex = R.eksport_wynikow(wyn, dl, OUT / "wyniki_mostki2d.json")
    assert all("psi_oi" in v and "f_rsi" in v for v in ex.values())


def test_raport_walidacji():
    txt = V.raport_walidacji(plik=OUT / "walidacja_ISO10211.md")
    assert "NIE SPEŁNIA" not in txt and txt.count("**SPEŁNIA**") == 6
    assert "Weryfikacja niezależna i poprawki" in txt and "**BŁĄD**" not in txt


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
