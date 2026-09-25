#!/usr/bin/env python3
"""Test modułu ``lamela.wskazniki`` (jedyne źródło wskaźników MPZP) + porównanie z audytem ``tools/audyt_wt.py`` (A1).

Sprawdza: kompletność pozycji (wartość, jednostka, podstawa, metoda), spójność arytmetyczną (udziały, intensywność,
H = z_top − t_śr, t_min ≤ t_śr ≤ t_max), bilans powierzchni (PBC + pokrycie ≤ działka), logikę terenu „niższa z
rzędnych” na danych syntetycznych, oraz raportuje różnice względem audytu A1 (audyt NIE jest poprawiany — różnica
metody wysokości zabudowy: A1 liczy od t_min, definicja upzp art. 2 pkt 30 lit. a — od średniej z min. i maks.).

Użycie: PYTHONPATH=src python3 tools/test_wskazniki.py [--bez-audytu]
Kod wyjścia: 0 — testy zaliczone, 1 — błąd.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from lamela import wskazniki as WS  # noqa: E402
from lamela.ir import build_ir  # noqa: E402
from lamela.model import load_model  # noqa: E402

BLEDY: list[str] = []


def ok(cond, msg):
    print(("  OK   " if cond else "  BŁĄD ") + msg)
    if not cond:
        BLEDY.append(msg)


def test_teren_syntetyczny():
    print("Teren syntetyczny (niższa z rzędnych istn./proj.):")
    t = WS.Teren({"punkty": [[0, 0, 100.0], [10, 0, 100.0], [0, 10, 101.0], [10, 10, 101.0]],
                  "punkty_projektowane": [[5, 5, 100.2], [6, 5, 100.2], [5, 6, 100.2]]})
    n, a, b = t.nizsza([[5, 5], [9, 9]])
    ok(abs(a[0] - 100.5) < 1e-9 and abs(b[0] - 100.2) < 1e-9 and abs(n[0] - 100.2) < 1e-9,
       f"punkt z rzędną projektowaną niższą: istn {a[0]:.3f}, proj {b[0]:.3f} → {n[0]:.3f}")
    ok(np.isnan(b[1]) and abs(n[1] - a[1]) < 1e-9, "poza zasięgiem punktów projektowanych → teren istniejący")


def test_model():
    m = load_model(ROOT / "model/budynek.yaml", ROOT / "model/dzialka.yaml", strict=False)
    ir = build_ir(m, otoczenie=True, auta=False)
    w = WS.wskazniki(m, ir=ir)
    print("Model (model/budynek.yaml + dzialka.yaml):")
    for k, v in w.items():
        if k.startswith("_"):
            continue
        ok(all(v.get(f) not in (None, "") for f in ("jedn", "podstawa", "metoda")) and "wartosc" in v,
           f"{k}: pola wartosc/jedn/podstawa/metoda")
    A = w["pow_dzialki"]["wartosc"]
    ok(abs(A - float(w["pow_dzialki"]["pow_ewid"] or A)) <= max(1.0, 0.005 * A), f"pow. działki {A:.2f} = ewid.")
    ok(abs(w["udzial_zabudowy"]["wartosc"] - w["pow_zabudowy"]["wartosc"] / A) < 1e-9, "udział zabudowy = pow./A")
    ok(w["pow_zabudowy"]["wartosc"] <= w["pow_zabudowy_kontrolna"]["wartosc"] + 1e-9, "wariant z płytami ≥ podstawowy")
    ok(abs(w["intensywnosc_nadziemna"]["wartosc"] - w["suma_pow_kondygnacji_nadziemnych"]["wartosc"] / A) < 1e-9,
       "intensywność nadziemna = Σ pow. kondygnacji nadz. / A")
    g = w["_geom"]
    ok(w["pbc"]["wartosc"] + g["cover"].intersection(g["pbc"]).area <= A + 1e-6 and
       g["pbc"].intersection(g["cover"]).area < 1e-6, "PBC rozłączna z pokryciem terenu, ≤ pow. działki")
    h = w["wysokosc_zabudowy"]
    ok(h["t_min"] <= h["t_sr"] <= h["t_max"], f"t_min {h['t_min']:.3f} ≤ t_śr {h['t_sr']:.3f} ≤ t_max {h['t_max']:.3f}")
    ok(abs(h["wartosc"] - (h["z_top_abs"] - h["t_sr"])) < 1e-9, "H = z_top − t_śr (upzp art. 2 pkt 30 lit. a)")
    ok(abs(h["t_sr"] - (h["t_min"] + h["t_max"]) / 2) < 1e-9, "t_śr = (t_min + t_max) / 2")
    ok(w["kondygnacje_nadziemne"]["wartosc"] == len(m.kondygnacje), "kondygnacje nadziemne (pkt 34)")
    went = ((m.raw.get("energia") or {}).get("wentylacja") or {})
    zt = [max(float(went[k][2]), float(went.get(f"{k}_z_top") or went[k][2])) for k in ("czerpnia", "wyrzutnia") if went.get(k)]
    ok(not zt or h["z_top"] >= max(zt) - 1e-9, "z_top ≥ maks. wysokość urządzeń dachowych (czerpnia/wyrzutnia z_top — V2 N-2)")
    print("\nWARTOŚCI:")
    for k, val, j, pod, _met in WS.tabela(w):
        vv = {kk: round(x, 2) for kk, x in val.items()} if isinstance(val, dict) else \
            (round(val, 4) if isinstance(val, float) else val)
        print(f"  {k:36s} {vv} {j}   [{pod}]")
    print(f"  wysokość zabudowy: element {h['element']}; z_top {h['z_top_abs']:.3f}; t_min {h['t_min']:.3f}; "
          f"t_max {h['t_max']:.3f}; t_śr {h['t_sr']:.3f}; H {h['wartosc']:.2f} m"
          + (f"; bez założeń ({h['bez_zalozen'][1]}): {h['bez_zalozen'][0]:.2f} m" if h.get("bez_zalozen") else ""))
    return m, w


def porownanie_audyt(w):
    print("\nPorównanie z tools/audyt_wt.py (audytor A1):")
    try:
        import audyt_wt as AW
        a = AW.AudytWT((ROOT / "model/budynek.yaml").resolve(), (ROOT / "model/dzialka.yaml").resolve(),
                       ROOT / "docs/10_podstawy_prawne/wymagania.yaml")
        A = a.run()
    except Exception as ex:  # noqa: BLE001
        print(f"  (audyt niedostępny: {type(ex).__name__}: {ex})")
        return
    ia = A.info.get("wysokosc") or {}
    h = w["wysokosc_zabudowy"]
    rows = [("wysokość zabudowy [m]", h["wartosc"], ia.get("H_upzp"), "A1 = lamela.wskazniki (runda 2, K-11); od t_min tylko informacyjnie"),
            ("  j.w. A1 „od średniej” [m]", h["wartosc"], ia.get("H_upzp_sr"), "A1 = lamela.wskazniki (K-11)"),
            ("t_min [m n.p.m.]", h["t_min"], ia.get("t_min"), ""),
            ("t_śr [m n.p.m.]", h["t_sr"], ia.get("t_sr"), ""),
            ("z_top [m wzgl.]", h["z_top"], ia.get("z_top"), f"{h['element']} / A1: {ia.get('el_top')}"),
            ("wysokość wg WT § 6 [m]", (w.get("wysokosc_WT6") or {}).get("wartosc"), ia.get("H_WT"),
             "A1 = lamela.wskazniki (K-11)"),
            ("PBC teren [m²]", w["pbc"]["wartosc"], (A.info.get("PBC") or {}).get("teren"),
             "opaska: pas przy ścianach vs wielobok 'obrys' (A1)"),
            ("PBC rezerwa dach 50 % [m²]", w["pbc_rezerwa_dach"]["wartosc"],
             (A.info.get("PBC") or {}).get("dach_zielony_50"), "")]
    for nm, a_, b_, why in rows:
        d = (a_ - b_) if (a_ is not None and b_ is not None) else None
        print(f"  {nm:30s} moduł {a_ if a_ is None else round(a_, 3)!s:>10}  A1 {b_ if b_ is None else round(b_, 3)!s:>10}"
              f"  Δ {'' if d is None else f'{d:+.3f}'}  {why}")


if __name__ == "__main__":
    test_teren_syntetyczny()
    _m, w = test_model()
    if "--bez-audytu" not in sys.argv:
        porownanie_audyt(w)
    print(f"\nWynik: {'ZALICZONE' if not BLEDY else f'BŁĘDY: {len(BLEDY)}'}")
    sys.exit(1 if BLEDY else 0)
