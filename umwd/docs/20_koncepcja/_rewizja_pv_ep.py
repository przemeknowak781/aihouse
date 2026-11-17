#!/usr/bin/env python3
"""Rewizja v1.1 – fotowoltaika na działce (M.12: ≥ 0,4 MWp) i wskaźnik EP metodą docs/40_prawo/_bilans_energii.py.

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_pv_ep.py
Zasady (MPZP § 6 pkt 13 – zakaz urządzeń na dachach i na elewacjach od ulic/bulwaru; wykładnia K-05: BIPV jako
materiał pokrycia/okładziny, nie urządzenie; WT § 216 ust. 8 – powyżej 25 m okładziny niepalne, więc BIPV tylko ≤ 25 m):
  * dachy wieży i skrzydła – BIPV szkło-szkło jako pokrycie (BROOF(t1)); pole netto = obrys − attyka (0,50 / 0,52 m)
    − pas przy attyce (wieża 1,00 m – cień attyki 1,0 m i dojście serwisowe; skrzydło 0,50 m – attyka 0,45–0,65 m)
    − wyłaz, wpusty, wsporniki zwodów; skrzydło dodatkowo przerwa 1,0 m (podział pola < 40 m, dostęp ratowniczy);
  * gęstość mocy pola dachowego 0,215 kWp/m² = sprawność modułu 22,5 % (moduły n-typ szkło-szkło) × pokrycie pola 0,955;
  * płyciny wieży od dziedzińca ≤ 25 m – BIPV w kolorze grafitowego brązu 0,13 kWp/m² (E-D-10), bez płycin czerpni;
  * ściana pd. segmentu (az. ≈ 177°, od dz. 10/2 – nie ulica; ≤ 25 m) – BIPV satynowane w tonie ceramiki 0,14 kWp/m²;
  * zadaszenie tarasu ogrodowego wzdłuż elewacji pd. wieży (element elewacji dziedzińcowej, wejście ogrodowe i rowerownia)
    – BIPV szkło-szkło półprzezierne (pokrycie ogniwami 70 %): 0,225 × 0,70 = 0,158 kWp/m².
Uzyski [kWh/kWp·rok]: dach wieży 880 (PVGIS, z cieniem attyki), dach skrzydła 895 × (1 − 0,116) (cień wieży wg
`_weryfikacja_koszt_eko.py --cien`: 11,4–11,8 %), elewacje 450 / 452 (cień własny i WS 5), zadaszenie 983 × 0,70 (PVGIS S 10°,
cień drzew i segmentu – szacunek).
"""
import importlib.util
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
from _rewizja_wspolne import ROOT, W, M, SEG, rect_uv, sd2en, en2sd
from shapely.geometry import Polygon, LineString

ETA, COVER = 0.225, 0.955
D_ROOF = ETA * COVER                 # 0,215 kWp/m²


def fields():
    tw = W.buffer(-0.50, join_style=2).buffer(-1.00, join_style=2)
    tower = tw.area - 1.4 - 6 * 0.5 - 2.0             # wyłaz przy trzonie B, 6 wpustów z koszami, wsporniki zwodów
    wg = M.buffer(-0.52, join_style=2).buffer(-0.50, join_style=2)
    gap = Polygon([sd2en(30.0, -1), sd2en(31.0, -1), sd2en(31.0, 30), sd2en(30.0, 30)])   # przerwa 1,0 m na granicy M2/M3
    wing = wg.difference(gap).area - 1.4 - 4 * 0.5 - 1.5   # wyłaz nad klatką C, 4 wpusty, zwody
    # płyciny wieży od dziedzińca (elewacja pd.): przęsła 2,70 m, płycina 1,65 × 1,30 m
    pl = 2.145
    n_pl = 8 * 5 - 8 - 1 + 7     # 8 przęseł × 5 rzędów (P/1, 1/2, 2/3, 3/4, 5/6) − czerpnia 2 rzędy × 4 przęsła − czerpnia nadciśnienia + rząd 5/6 nad segmentem
    span = 8 * 5 - 8 - 1 + 7
    seg_wall = LineString([(96.694, 38.813), (115.979, 39.930)]).length * (20.85 - 4.80) * 0.95   # 5 % fugi reliefu
    canopy = 20.0 * 4.0          # u 0,5–20,5 × głęb. 4,0 m, h ≈ 4,0 m
    return {"tower": tw.area, "tower_net": tower, "wing_gross": wg.area, "wing_net": wing, "pl_n": n_pl,
            "pl_m2": n_pl * pl, "seg_wall": seg_wall, "canopy": canopy}


def pv_table(f):
    rows = [
        ("dach wieży – BIPV pokrycie", f["tower_net"], D_ROOF, 880),
        ("dach skrzydła – BIPV pokrycie (cień wieży −11,6 %)", f["wing_net"], D_ROOF, round(895 * (1 - 0.116))),
        ("płyciny wieży od dziedzińca ≤ 25 m (BIPV grafitowy brąz)", f["pl_m2"], 0.13, 450),
        ("ściana pd. segmentu ≤ 25 m (BIPV satynowane, ton ceramiki)", f["seg_wall"], 0.14, 452),
        ("zadaszenie tarasu ogrodowego przy elewacji pd. wieży (BIPV półprzezierne)", f["canopy"], ETA * 0.70, round(983 * 0.70)),
    ]
    return [(n, a, d, round(a * d, 1), y) for n, a, d, y in rows]


def ep_from_bilans(pv_rows):
    """Uruchamia docs/40_prawo/_bilans_energii.py z PV v1.1 (Af = 297 MWh / 23,9 jak w spec. 10)."""
    spec = importlib.util.spec_from_file_location("bilans", os.path.join(ROOT, "docs", "40_prawo", "_bilans_energii.py"))
    b = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(b)
    b.AF = round(297e3 / 23.9)
    b.PV_BASE = [(n[:66], int(round(k)), y) for n, a, d, k, y in pv_rows]
    b.PV = b.PV_BASE
    b.INCLUDE_OPTION = False
    b.N_BHE, b.L_BHE, b.L_ACT = 58, 92.0, 91.0          # pole sond v1.1 (E-I-2) – informacyjnie w wydruku
    buf = io.StringIO()
    with redirect_stdout(buf):
        b.main()
    out = buf.getvalue()
    epb = b.Q_H / b.SCOP_H + b.Q_W / b.COP_W + b.Q_C * b.FC_SHARE / b.SEER_FC + b.Q_C * (1 - b.FC_SHARE) / b.EER_ACT \
        + b.E_FANS + b.E_AUX + b.E_LIGHT
    mwh = sum(k * y for _, _, _, k, y in pv_rows) / 1000
    sc = mwh * b.SELF_CONS
    pv_epb = min(sc, epb * b.AF / 1000) * 0.6
    ep = (epb * b.AF / 1000 - pv_epb) * 1000 / b.AF * b.W_EL
    co2 = (epb * b.AF / 1000 - pv_epb) * b.EF_GRID * 1000 / b.AF
    total = (epb + b.E_PLUG + b.E_LIFT + b.E_OTHER + b.IT_KW * 8760 / b.AF) * b.AF / 1000
    return out, dict(epb=epb, epb_mwh=epb * b.AF / 1000, total_mwh=total, pv_mwh=mwh, ep=ep, ep0=epb * b.W_EL, co2=co2)


def main():
    f = fields()
    rows = pv_table(f)
    print(f"gęstość pola dachowego: {ETA:.3f} × {COVER} = {D_ROOF:.3f} kWp/m²")
    print(f"dach wieży: wnętrze − pas 1,0 m = {f['tower']:.1f} m² → netto {f['tower_net']:.1f} m²")
    print(f"dach skrzydła: wnętrze − pas 0,5 m = {f['wing_gross']:.1f} m² → netto (przerwa 1,0 m, wyłaz, wpusty) {f['wing_net']:.1f} m²")
    print(f"płyciny: {f['pl_n']} × 2,145 m² = {f['pl_m2']:.1f} m²; ściana segmentu {f['seg_wall']:.1f} m²; zadaszenie {f['canopy']:.0f} m²")
    print("| Pole | m² | kWp/m² | kWp | kWh/kWp | MWh/rok |")
    print("|---|---:|---:|---:|---:|---:|")
    for n, a, d, k, y in rows:
        print(f"| {n} | {a:.0f} | {d:.3f} | {k:.1f} | {y} | {k * y / 1000:.1f} |")
    kwp = sum(r[3] for r in rows)
    roof = rows[0][3] + rows[1][3]
    out, e = ep_from_bilans(rows)
    print(f"RAZEM {kwp:.1f} kWp (dachy {roof:.1f}, poza dachami {kwp - roof:.1f}); {e['pv_mwh']:.0f} MWh/rok; "
          f"M.12 ≥ 400 kWp: {'TAK' if kwp >= 400 else 'NIE'} (zapas {kwp - 400:.1f} kWp)")
    print(f"wrażliwość: przy sprawności 21 % (0,20 kWp/m²) dachy {roof * 0.20 / D_ROOF:.0f} → razem {kwp - roof + roof * 0.20 / D_ROOF:.0f} kWp")
    print(f"EPB {e['epb']:.1f} kWh/m² ({e['epb_mwh']:.0f} MWh), całość {e['total_mwh']:.0f} MWh; PV/EPB {e['pv_mwh'] / e['epb_mwh']:.0%}; "
          f"PV/całość {e['pv_mwh'] / e['total_mwh']:.0%}; EP bez PV {e['ep0']:.0f}; EP z PV {e['ep']:.1f}; emisje EPB {e['co2']:.1f} kg/(m²·rok)")
    print("\n--- wydruk docs/40_prawo/_bilans_energii.py z danymi v1.1 ---")
    print(out)
    return rows, e


if __name__ == "__main__":
    main()
