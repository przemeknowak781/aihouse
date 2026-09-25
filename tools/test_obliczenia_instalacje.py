#!/usr/bin/env python3
"""Testy biblioteki obliczeń instalacji (``lamela.obliczenia.sanitarne``, ``lamela.obliczenia.elektryka``) i demo raportów.

Uruchomienie:
    PYTHONPATH=src python3 tools/test_obliczenia_instalacje.py            # testy + demo → projekt/08_obliczenia/demo_test/instalacje
    PYTHONPATH=src python3 tools/test_obliczenia_instalacje.py --bez-demo # tylko testy jednostkowe
    PYTHONPATH=src python3 tools/test_obliczenia_instalacje.py --out KATALOG

Testy jednostkowe na przykładach sprawdzalnych ręcznie — źródła przy każdym teście:
* [PWr]  Politechnika Wrocławska, „Materiały pomocnicze do projektu instalacji wodociągowej” (przykład dla domu
         jednorodzinnego, tab. 3–4, dobór wodomierza) — PN-92/B-01706;
* [R6]   docs/10_podstawy_prawne/R6_energia_instalacje_sanitarne.md (§3.6–3.9 i weryfikacja niezależna: przeliczenia
         q = 0,682·Σq_n^0,45 − 0,14; Q_ww; hałas; retencja — przykład skrzynek);
* [AQN]  Aquanet S.A., Załącznik C (2024), rozdz. IV — przykład obliczeniowy V_obl = 1937,68 m³ (t_d = 484 min);
* [PORT] PORT PC, „Wytyczne do ograniczania hałasu instalacji z pompami ciepła”, p. 4.4 (61 dB(A), 10 m, Q = 2 → 33 dB(A));
* [R7]   docs/10_podstawy_prawne/R7_elektryka_odgromowa.md (§3.1, R7-L09, R7-F03, R7-K05 + weryfikacja: ∆U, CRL, A_D, R1);
* [1264] PN-EN 1264-2 — charakterystyka bazowa q = 8,92·∆θ^1,1; definicja średniej logarytmicznej ∆θ_H;
* [WT]   WT zał. 2 pkt 1.5 — grubości izolacji przewodów.
Funkcje test_* są zgodne z pytest.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

B = ROOT / "model" / "test" / "dom_testowy.yaml"
DZ = ROOT / "model" / "test" / "dzialka_testowa.yaml"
WY = ROOT / "model" / "test" / "wyposazenie_testowe.yaml"
IN = ROOT / "model" / "test" / "instalacje_testowe.yaml"
DEMO = ROOT / "projekt" / "08_obliczenia" / "demo_test" / "instalacje"


def blisko(a, b, tol_rel=0.02, tol_abs=0.0):
    assert abs(a - b) <= max(tol_abs, tol_rel * abs(b)), f"{a} ≠ {b} (tol {tol_rel:.1%}/{tol_abs})"


# ================================================================ woda
def test_przeplyw_pn01706_pwr():
    """[PWr] tab. 3: Σq_n 1,82 → 0,75; 0,54 → 0,38; 0,70 → 0,44; 0,22 → 0,21; [R6] 3,3 → 1,03 dm³/s."""
    from lamela.obliczenia.sanitarne.woda import przeplyw_pn01706, przeplyw_odcinka
    for s, q in ((1.82, 0.75), (0.54, 0.38), (0.70, 0.44), (0.22, 0.21), (3.3, 1.03)):
        blisko(przeplyw_pn01706(s), q, tol_abs=0.006)
    assert przeplyw_odcinka([0.30]) == 0.30            # jeden punkt: q = q_n
    assert przeplyw_odcinka([0.07, 0.07]) <= 0.14 + 1e-9


def test_straty_liniowe_pwr():
    """[PWr] tab. 3: PE-RT/Al/PE-RT 16×2 (d_w 12 mm), q = 0,07 dm³/s → v = 0,62 m/s, R = 0,57 kPa/m;
    40×4 (d_w 32), q = 0,75 → v = 0,94, R = 0,34 kPa/m (Darcy–Weisbach + Colebrook–White, 10 °C)."""
    from lamela.obliczenia.sanitarne.woda import spadek_jednostkowy
    v, R, _ = spadek_jednostkowy(0.07, 12.0, 10.0)
    blisko(v, 0.62, tol_abs=0.01)
    blisko(R, 0.57, tol_rel=0.06)
    v, R, _ = spadek_jednostkowy(0.75, 32.0, 10.0)
    blisko(v, 0.94, tol_abs=0.01)
    blisko(R, 0.34, tol_rel=0.08)


def test_wodomierz_pwr():
    """[PWr]: q = 0,75 dm³/s = 2,7 m³/h → wodomierz Q3 = 4,0 m³/h DN20, ∆p ≈ 28 kPa (nomogram katalogowy)."""
    from lamela.obliczenia.sanitarne.woda import dobierz_wodomierz
    dn, q3, qh, dp = dobierz_wodomierz(0.75)
    assert (dn, q3) == (20, 4.0)
    blisko(qh, 2.7, tol_abs=0.01)
    blisko(dp, 28.0, tol_rel=0.05)


def test_izolacja_wt():
    """[WT] zał. 2 pkt 1.5: d_w ≤ 22 → 20 mm; 22–35 → 30 mm; 35–100 → d_w; > 100 → 100 mm; przeliczenie λ — tożsamość."""
    from lamela.obliczenia.sanitarne.woda import grubosc_izolacji_WT, grubosc_rownowazna
    assert [grubosc_izolacji_WT(d) for d in (12, 22, 28, 35, 50, 120)] == [20, 20, 30, 30, 50, 100]
    blisko(grubosc_rownowazna(20, 20, 0.035), 20.0, tol_abs=1e-9)
    assert grubosc_rownowazna(20, 20, 0.040) > 20.0


# ================================================================ kanalizacja
def test_qww_r6():
    """[R6] §3.7: ΣDU = 17 → Q_ww = 0,5·√17 = 2,06 l/s; pojedyncza miska ustępowa: Q_ww = DU = 2,0 l/s."""
    from lamela.obliczenia.sanitarne.kanalizacja import q_ww
    blisko(q_ww(17.0), 2.06, tol_abs=0.005)
    assert q_ww(2.0, 0.5, 2.0) == 2.0


def test_przeplyw_czesciowy():
    """Przewód do połowy wypełniony: R_h = D/4 (jak pełny) → Q(h/d = 0,5) = Q_pełny/2, v równe (geometria)."""
    from lamela.obliczenia.sanitarne.kanalizacja import napelnienie, przeplyw_czesciowy
    qf, vf = przeplyw_czesciowy(0.1036, 1.0, 0.01)
    qh, vh = przeplyw_czesciowy(0.1036, 0.5, 0.01)
    blisko(qh, qf / 2, tol_rel=1e-9)
    blisko(vh, vf, tol_rel=1e-9)
    hd, _ = napelnienie(qh, 0.1036, 0.01)
    blisko(hd, 0.5, tol_abs=1e-4)


# ================================================================ deszczowa
def test_retencja_skrzynki_r6():
    """[R6] §3.8 (po weryfikacji): A_red = 200 m², skrzynki 4,8×2,4×0,66, k_f = 10⁻⁴ → A_inf = 16,27 m², Q_inf = 0,81 l/s,
    V_obl ≈ 4,2 m³ (t_d ≈ 30 min), V_min = 1,2·V_obl ≈ 5,1 m³, opróżnianie ≈ 1,7 h."""
    from lamela.obliczenia.sanitarne.deszczowa import objetosc_bilansowa
    A_inf = 4.8 * 2.4 + 0.5 * 2 * (4.8 + 2.4) * 0.66
    blisko(A_inf, 16.27, tol_abs=0.01)
    Qi = 1000 * A_inf * 0.5e-4
    blisko(Qi, 0.81, tol_abs=0.01)
    V, td = objetosc_bilansowa(0.02, Qi)
    blisko(V, 4.2, tol_abs=0.05)
    assert 25 <= td <= 35
    blisko(1.2 * V, 5.1, tol_abs=0.1)
    blisko(1.2 * V / (Qi / 1000) / 3600, 1.7, tol_abs=0.1)


def test_aquanet_przyklad():
    """[AQN] rozdz. IV: q(484) = 17,388; V_obl = 0,06·(17,388·4,84 + 55,5 − 52,93 − 20)·484 = 1937,68 m³ (metoda bilansowa)."""
    from lamela.obliczenia.sanitarne.deszczowa import objetosc_bilansowa, q_panda
    blisko(q_panda(484), 17.388, tol_abs=0.005)
    blisko(q_panda(5), 464.59, tol_abs=1e-6)
    V, td = objetosc_bilansowa(4.84, 52.93 + 20.0, 4320, Q_o=55.5)
    blisko(V, 1937.68, tol_rel=0.005)
    assert 470 <= td <= 510


def test_przelew_i_rura_spustowa():
    """Przelew prostokątny (Poleni) — obliczenie niezależne; rura spustowa: wzór Q_RWP monotoniczny, DN100 ≈ 10,7 l/s (f = 0,33)."""
    from lamela.obliczenia.sanitarne.deszczowa import przepustowosc_przelewu, przepustowosc_rury_spustowej
    blisko(przepustowosc_przelewu(0.2, 0.08), 2 / 3 * 0.6 * 0.2 * (2 * 9.81) ** 0.5 * 0.08 ** 1.5 * 1000, tol_rel=1e-9)
    blisko(przepustowosc_rury_spustowej(100.0), 10.7, tol_abs=0.1)
    assert przepustowosc_rury_spustowej(96.0) < przepustowosc_rury_spustowej(100.0)


# ================================================================ drenaż
def test_drenaz_decyzja():
    """Piaski średnie (k_f 3·10⁻⁴), ZWG ≈ 3 m pod fundamentem → drenaż niewymagany; grunt spoisty (k_f 10⁻⁷) → zalecany."""
    from lamela.obliczenia.inst_wspolne import dane_z_modelu
    from lamela.obliczenia.sanitarne.drenaz import ParametryDrenaz, ocen_drenaz
    d = dane_z_modelu(B, DZ, WY, IN)
    assert ocen_drenaz(d).decyzja == "NIEWYMAGANY"
    assert ocen_drenaz(d, ParametryDrenaz(grunt="gliny", k_f=1e-7)).decyzja.startswith("ZALECANY")


# ================================================================ ogrzewanie
def test_halas_port_r6():
    """[PORT] 61 dB(A), 10 m, Q = 2 → 33 dB(A); [R6] §3.9: 55 dB(A), Q = 4: 4 m → 38,0; 8 m → 32,0; 60 dB(A), 6 m → 39,5."""
    from lamela.obliczenia.sanitarne.ogrzewanie import odleglosc_dla_limitu, poziom_halasu
    blisko(poziom_halasu(61, 10, 2), 33.0, tol_abs=0.05)
    blisko(poziom_halasu(55, 4, 4), 38.0, tol_abs=0.05)
    blisko(poziom_halasu(55, 8, 4), 32.0, tol_abs=0.05)
    blisko(poziom_halasu(60, 6, 4), 39.5, tol_abs=0.05)
    blisko(poziom_halasu(60, odleglosc_dla_limitu(60, 35, 4), 4), 35.0, tol_abs=1e-9)
    # ≡ L_WA − 20·log r − 8 + DI (DI = 10·log(Q/2))
    blisko(poziom_halasu(55, 7, 8), 55 - 20 * math.log10(7) - 8 + 10 * math.log10(4), tol_abs=0.02)


def test_pn1264():
    """[1264] q(∆θ_F = 9 K) = 8,92·9^1,1 = 100,0 W/m²; ∆θ_H(35/30/20) = 5/ln(15/10) = 12,33 K; θ_V ↔ ∆θ_H (odwracalność);
    K_H(T = 0,10; R_λ,B = 0,10; s_u = 45 mm; λ_E = 1,2) = 6,7·0,598·1,156^−1/3·1,010^−0,75 ≈ 3,79 W/(m²·K)."""
    from lamela.obliczenia.sanitarne.ogrzewanie import K_H, dT_H_log, q_charakterystyka, theta_R_z, theta_V_z
    blisko(q_charakterystyka(9.0), 100.0, tol_abs=0.1)
    blisko(dT_H_log(35, 30, 20), 5 / math.log(1.5), tol_rel=1e-9)
    tv = theta_V_z(12.0, 5.0, 20.0)
    blisko(dT_H_log(tv, tv - 5.0, 20.0), 12.0, tol_rel=1e-9)
    blisko(theta_R_z(35.0, 12.3315, 20.0), 30.0, tol_abs=0.01)
    blisko(K_H(0.10, 0.10, 0.045, 1.2), 3.79, tol_abs=0.02)


def test_naczynie_wzbiorcze():
    """PN-EN 12828 zał. D: V_c = 200 dm³, 10 → 50 °C: e = ρ10/ρ50 − 1 ≈ 1,18 %; h = 5 m → p₀ = 0,7 bar; p_SV = 3 → p_e = 2,5;
    V_n = (2,36 + 3,0)·3,5/1,8 ≈ 10,4 dm³ → 12 dm³."""
    from lamela.obliczenia.sanitarne.ogrzewanie import naczynie_wzbiorcze
    n = naczynie_wzbiorcze(200, 50, 5.0)
    blisko(n["e"], 0.0118, tol_abs=0.0002)
    blisko(n["V_n"], (200 * n["e"] + 3.0) * 3.5 / 1.8, tol_rel=1e-9)
    assert n["V_dob"] == 12


# ================================================================ elektryka
def test_spadki_napiec_r7():
    """[R7] §3.1–3.3 + weryfikacja (20 °C): WLZ 40 A/25 m/16 mm² (3f) 0,50 %; gniazda 16 A/24 m/2,5 mm² 2,47 %; oświetlenie
    3 A/30 m/1,5 mm² 0,95 %; EV 16 A/15 m/6 mm² (3f) 0,32 %; falownik 10 A/20 m/4 mm² (3f) 0,40 %; D14 6 A/40 m/2,5 mm² 1,55 %."""
    from lamela.obliczenia.elektryka.obwody import dU_proc
    for args, ref in (((40, 25, 16, 3), 0.50), ((16, 24, 2.5, 1), 2.47), ((3, 30, 1.5, 1), 0.95), ((16, 15, 6, 3), 0.32),
                      ((10, 20, 4, 3), 0.40), ((6, 40, 2.5, 1), 1.55)):
        blisko(dU_proc(*args, 1.0, 20.0), ref, tol_abs=0.006)


def test_moc_zabezpieczenie_r7():
    """[R7-L09] P = √3·400·I: 40 A → 27,7 kW; 32 A → 22,2 kW."""
    blisko(math.sqrt(3) * 400 * 40 / 1000, 27.7, tol_abs=0.05)
    blisko(math.sqrt(3) * 400 * 32 / 1000, 22.2, tol_abs=0.05)


def test_tabele_iz():
    """PN-HD 60364-5-52 tabl. B.52.2/B.52.4 (wartości wg literatury): C/2 żyły 2,5 mm² → 27 A; D1/3 żyły 16 mm² → 64 A."""
    from lamela.obliczenia.elektryka import tabele as T
    assert T.iz("C", 2, 2.5) == 27.0 and T.iz("D1", 3, 16.0) == 64.0 and T.iz("A1", 2, 1.5) == 14.5
    assert T.MNOZNIK_IA["B"] * 16 == 80


def test_crl_r7():
    """[R7-F03] CRL = 170/(0,1·1,8) = 944 (< 1000 → SPD); graniczna długość linii kablowej 94 m."""
    blisko(170 / (0.1 * 1.8), 944.4, tol_abs=0.1)
    blisko(170 / (1000 * 1.8) * 1000, 94.4, tol_abs=0.1)


def test_odgromowa_r7():
    """[R7-K05] + weryfikacja: dom 19 × 11 × 10,5 m: A_D = 5216 m², N_D = 0,0094, N_L = 0,018; R1 = 5,5·10⁻⁶ (zwykłe) i 3,0·10⁻⁵ (wysokie)."""
    from shapely.geometry import box

    from lamela.obliczenia.elektryka.odgromowa import ryzyko_R1
    A = box(0, 0, 19, 11).buffer(3 * 10.5, resolution=128).area
    blisko(A, 5216, tol_abs=2)
    ND = 1.8 * A * 1e-6
    NL = 1.8 * 40 * 1000 * 0.5 * 0.5 * 1e-6
    blisko(ND, 0.0094, tol_abs=0.0001)
    blisko(NL, 0.018, tol_abs=1e-9)
    blisko(ryzyko_R1(ND, NL, 1e-2)["R1"], 5.5e-6, tol_abs=0.05e-6)
    blisko(ryzyko_R1(ND, NL, 1e-1)["R1"], 3.0e-5, tol_abs=0.05e-5)


def test_pv_liczba_modulow():
    """[R6 §3.10] 15 × 430 Wp = 6,45 kWp ≤ 6,5 kWp; U_oc,max = N_s·U_oc·(1 + β·(θ_min − 25)) — obliczenie niezależne."""
    from lamela.obliczenia.elektryka.pv import MODUL_PRZYKLAD
    assert math.floor(6500 / 430) == 15 and 15 * 430 / 1000 == 6.45
    m = MODUL_PRZYKLAD
    blisko(8 * m["U_oc"] * (1 + m["beta_Uoc"] * (-25 - 25)), 8 * 38.9 * 1.125, tol_rel=1e-9)


# ================================================================ integracja (model testowy)
def test_integracja_model_testowy(out: Path | None = None):
    """Pełny komplet obliczeń dla model/test/*.yaml: raporty, schematy, JSON; wyniki w granicach sensowności."""
    from lamela.obliczenia.instalacje import RAPORTY, oblicz_wszystko
    import tempfile
    tmp = Path(out) if out else Path(tempfile.mkdtemp())
    wyn = oblicz_wszystko(B, DZ, WY, IN, out=tmp)
    for _, plik, _ in RAPORTY:
        t = (tmp / plik).read_text(encoding="utf-8")
        assert t.startswith("# ") and "## Źródła" in t, plik
    assert (tmp / "schemat_RG.png").stat().st_size > 50_000 and (tmp / "schemat_PC_CWU.png").stat().st_size > 50_000
    js = json.loads((tmp / "wyniki_instalacje.json").read_text(encoding="utf-8"))
    assert "do_EP" in js and js["pv"]["P_kWp"] <= 6.5
    w = wyn["woda"]
    assert 0.5 < w.wodomierz["q"] < 1.5 and w.wodomierz["DN"] == 20
    assert wyn["kanalizacja"].do_dict()["piony"] and all(v == "DN100" for v in wyn["kanalizacja"].do_dict()["piony"].values())
    assert wyn["bilans"].P_s_dlm <= wyn["bilans"].P_przyl
    assert all(o.I_B <= o.I_n <= o.I_z + 1e-9 for o in wyn["obwody"].obwody)
    assert all(o.I_k1 >= o.I_a for o in wyn["obwody"].obwody)
    assert wyn["obwody"].spd["CRL"] < 1000
    assert wyn["ogrzewanie"].theta_V <= 35.0 + 1e-6
    assert wyn["ogrzewanie"].halas["L_A_granica"] <= 40.0
    return wyn


def test_integracja_z_modulem_energii():
    """Kontrakt z modułem energii: WynikObc (Φ_HL pomieszczeń + Φ_HL budynku) i WynikWent przyjęte bez konwersji;
    podłogówka z ΣΦ_HL,i, dobór PC z Φ_HL,bud; θ_V,des ≤ 35 °C (niedobory jako warunki pomieszczeń)."""
    try:
        from lamela.obliczenia.instalacje import z_modulu_energii
        obc, went = z_modulu_energii(B, DZ)
    except ImportError as e:
        return f"pominięty (brak modułu energii: {e})"
    from lamela.obliczenia.inst_wspolne import dane_z_modelu, phi_hl_budynku_z, phi_hl_z, wentylacja_z
    from lamela.obliczenia.sanitarne.ogrzewanie import oblicz_ogrzewanie
    ph = phi_hl_z(obc)
    assert ph and abs(sum(ph.values()) - sum(p.Phi_HL for p in obc.pomieszczenia)) < 1e-6
    assert abs(phi_hl_budynku_z(obc) - obc.Phi_HL) < 1e-9
    w = wentylacja_z(went)
    assert abs(w["suma_naw"] - went.suma_naw) < 1e-6 and w["zrodlo"] == "moduł wentylacji"
    dane = dane_z_modelu(B, DZ, WY, IN)
    og = oblicz_ogrzewanie(dane, phi_hl=obc)
    assert abs(og.Phi_HL - obc.Phi_HL) < 1e-6 and og.phi_zrodlo.startswith("moduł")
    assert og.theta_V <= 35.0 + 1e-9
    nied = [x for x in og.warunki if "moc podłogi" in x.opis and x.ok is False]
    return f"OK (Φ_HL,bud {obc.Phi_HL / 1000:.2f} kW, ΣΦ_HL,i {sum(ph.values()) / 1000:.2f} kW, niedobory podłogówki: {len(nied)})"


def test_model_docelowy_jesli_istnieje():
    """Drugi test: model/budynek.yaml (+ dzialka/wyposazenie/instalacje) — tylko odczyt; pominięty, gdy brak pliku."""
    b = ROOT / "model" / "budynek.yaml"
    if not b.exists():
        return "pominięty (brak model/budynek.yaml)"
    from lamela.obliczenia.instalacje import oblicz_wszystko
    dz = ROOT / "model" / "dzialka.yaml"
    wy = ROOT / "model" / "wyposazenie.yaml"
    ins = ROOT / "model" / "instalacje.yaml"
    wyn = oblicz_wszystko(b, dz if dz.exists() else None, wy if wy.exists() else None, ins if ins.exists() else None,
                          out=ROOT / "build" / "test" / "instalacje_budynek")
    return f"OK ({len(wyn['obwody'].obwody)} obwodów, przybory: {len(wyn['woda'].przybory)})"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bez-demo", action="store_true")
    ap.add_argument("--out", default=str(DEMO))
    a = ap.parse_args(argv)
    testy = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    bledy = 0
    for nazwa, fn in testy:
        try:
            if nazwa == "test_integracja_model_testowy":
                r = fn(None if a.bez_demo else Path(a.out))
            else:
                r = fn()
            print(f"OK    {nazwa}" + (f" — {r}" if isinstance(r, str) else ""))
        except Exception as e:  # noqa: BLE001
            bledy += 1
            print(f"BŁĄD  {nazwa}: {e}")
            traceback.print_exc()
    print(f"\n{len(testy) - bledy}/{len(testy)} testów zaliczonych" + ("" if a.bez_demo else f"; demo: {a.out}"))
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
