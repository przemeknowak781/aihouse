#!/usr/bin/env python3
"""Rewizja v1.1 – koszt realizacji (F.14.B, mid, netto, II kw. 2026) z limitem 150 mln zł (R-049, R-222).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_koszt.py
Zapisuje wejście modelu: docs/20_koncepcja/_rewizja_koszt_wejscie_v1_1.json (wszystkie klucze `tools/koszty_model.py`),
tak by `python3 -I tools/koszty_model.py docs/20_koncepcja/_rewizja_koszt_wejscie_v1_1.json` odtworzył część modelową.

Kroki:
  0. v1.0 odtworzona przez weryfikatora (144,18) i jego korekta C (151,72) – import `_weryfikacja_koszt_eko.py`;
  1. v1.1 – ilości z geometrii v1.1 (`_rewizja_wspolne.py`, garaż wg `_rewizja_parking.py`), pozycje spoza modelu
     z rozbiciem; każda pozycja spoza modelu jest objęta KS 3 % i rezerwą (contingency);
  2. dźwignie projektowe v1.1 – każda z osobnym efektem (różnica modelu);
  3. wynik: roboty + KS, rezerwa (≥ 4 %, przyjęto 5 %), razem ≤ 150; zł/m² PC i zł/m² PU z pasmami benchmarków.
Pozycje [Z] = założenia zespołu (status jak stawki [Z] modelu, `50_research/koszty_benchmarki.md`).
"""
import importlib.util
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from _rewizja_wspolne import ROOT, W, M, SEG, level_m1, level_m2, rect_sd, unary_union

HERE = os.path.dirname(__file__)
_s = importlib.util.spec_from_file_location("wer", os.path.join(HERE, "_weryfikacja_koszt_eko.py"))
wer = importlib.util.module_from_spec(_s)
_s.loader.exec_module(wer)
km = wer.km
LIMIT = 150.0


def total(p, extra=0.0, rez=None):
    q = dict(km.REF)
    q.update(p)
    if rez is not None:
        old = km.REZ
        km.REZ = (old[0], rez, old[2])
    r = km.compute(q, "mid")
    k = (1 + km.KS[1]) * (1 + km.REZ[1])
    tot = r["total"] / 1e6 + extra * k / 1e6
    works_ks = (r["works"] + r["ks"]) / 1e6 + extra * (1 + km.KS[1]) / 1e6
    if rez is not None:
        km.REZ = old
    return tot, works_ks, r


def geometry():
    L1, L2 = level_m1(), level_m2()
    fpw = L1.difference(unary_union([W, M, SEG]).buffer(0.1)).area
    t_m2 = 110.90      # spód płyty −2 (posadzka 112,10 − warstwy 0,10 − płyta 1,10 pod wieżą / 0,90 + chudy beton)
    t_m1 = 114.10      # spód płyty −1 poza −2 (posadzka 115,10 − 0,10 − 0,90)
    terr = 118.95      # średni teren w obrysie podziemia (NMT `site.json`: 118,36–119,44)
    a2 = L2.area
    a1only = L1.area - a2
    h_wyk = (a2 * (terr - t_m2 + 0.10) + a1only * (terr - t_m1 + 0.10)) / L1.area
    plyta = W.area * 1.10 + (a2 - W.area) * 0.90 + a1only * 0.90
    dw_len = L1.length - 15.0          # obwód −1 minus odcinek przy Maz. 19 (iniekcja strumieniowa)
    return dict(L1=L1.area, L2=a2, per=L1.length, fpw=fpw, h_wyk=h_wyk, t_plyty=plyta / L1.area, dw_len=dw_len)


def main():
    g = geometry()
    print("== 0. Punkt wyjścia (weryfikator)")
    sp = dict(wer.SPEC, **wer.UKRYTE)
    t0, _, _ = total(sp)
    kor = dict(sp, **wer.KOREKTA)
    ex = sum(wer.POZA_MODELEM.values())
    rw, rm, _ = wer.oscieza()
    tC, _, _ = total(dict(kor, fas_kamien=kor["fas_kamien"] + rw, fas_went=kor["fas_went"] + rm), ex)
    print(f"  v1.0 odtworzona {t0:.2f}; korekta weryfikatora C (ościeża, pale, uskok, dry-cooler, GPC) {tC:.2f} mln")

    print("== 1. v1.1 – ilości (geometria v1.1, garaż 106 m.p.)")
    A_nad = 14151.2 + 5 * 2.66 + 110.0      # + skrzydło wg tab. 4.1 (P–4) + rezerwa na antresolę S do ≈ 180 m² (kondygnacja_S2)
    dw_area = g["dw_len"] * 19.0
    P = dict(sp)
    P.update({
        "A_nad": round(A_nad, 1), "A_pod": round(g["L1"] + g["L2"], 1), "fp_pod": round(g["L1"], 1),
        "obw_pod": round(g["dw_len"], 1), "h_sz": 19.0, "h_wyk": round(g["h_wyk"], 2), "t_plyty": round(g["t_plyty"], 3),
        "h_pod": 8.0, "fp_nad": 2165.7, "fp_wypor": round(g["fpw"], 1),
        "fas_went": 2100 + 236 - 310 + 147,    # ceramika + panele Al: + płyciny wieży bez BIPV, − ściana pd. segmentu (BIPV), + cokół skrzydła
        "fas_kamien": 1810 - 147,              # granit: bez cokołu skrzydła (→ ceramika); lico filarów bez węgarów (ościeża Al)
        "okna": 2167, "fas_bipv": 82 + 295 + 80, "przeslony": 240, "dach": 2163, "stal_kg": 73000,
        "kwp_dach": 351, "kwh_bess": 150, "mb_odw": 58 * 91, "t_ziel": 630, "drzewa": 26, "t_kam": 500,
    })
    POZA = {
        # pozycja: (kwota zł netto robót, uzasadnienie)
        "budowla ochronna – ukrycie na −2 (art. 93 ustawy o ochronie ludności)": (1.5e6, "spec. v1.0"),
        "lapidarium i ekspozycja reliktów (in situ w posadzce + ściana witryn)": (0.3e6, "dźwignia: 0,5 → 0,3"),
        "pale CFA 36 × Ø 0,8 × 14 m = 504 mb × 1 100 zł": (504 * 1100, "weryfikator [Z]"),
        "ściana na uskoku −1/−2 (skrzydło, s 12,15): 14,9 m × 7,5 m × 1 250 zł/m²": (14.9 * 7.5 * 1250, "geometria v1.1"),
        "iniekcja strumieniowa przy Maz. 19: 17 kolumn Ø 1,2 × 19 m × 600 zł/mb + kształtowniki co 2. kolumna "
        "8 × 19 m × 100 kg/m × 8 zł + okładzina żelbetowa 38 m³ × 1 500 zł + podbicie fundamentu 19 kol. × 6 m × 600 zł":
            (17 * 19 * 600 + 8 * 19 * 100 * 8 + 38 * 1500 + 19 * 6 * 600, "[Z]"),
        "dry-cooler hybrydowy 2 × 150 kW + żaluzje akustyczne i tłumiki": (0.45e6, "weryfikator [Z]"),
        "GPC: wiercenie 58 otworów z dna wykopu (3 000 zł/otw.) + kolektory podpłytowe i 2 przejścia szczelne": (58 * 3000 + 0.15e6, "[Z]"),
        "GPC: absorbery w ścianach szczelinowych (60 zł/m²) i 36 palach (80 zł/mb)": (dw_area * 60 + 504 * 80, "[Z]"),
        "stackery zależne 2-poziomowe: 15 jednostek podwójnych × 70 000 zł": (15 * 70000, "[Z] katalogowe"),
        "zapora przeciwpowodziowa samoczynna w bramie 4,0 m + sygnalizacja wahadłowa ramp": (0.12e6 + 0.04e6, "[Z]"),
        "szyb wyjścia zapasowego MDS + tunel 8 m (P-I6)": (0.25e6, "[Z]"),
        "agregat w segmencie: wzmocnienie stropu + przewód spalin do korony 35 m": (0.11e6, "[Z]"),
        "pielęgnacja zachowanych ogródków 470 m² × 100 zł (zamiast nowej zieleni)": (470 * 100, "[Z]"),
        "ościeża wieży 0,45 m: blacha Al 2 mm lakierowana proszkowo na wełnie, 824 m² × 650 zł": (824 * 650, "[Z] 230 zł/mb ÷ 0,35 m"),
        "ościeża okien i witryn skrzydła i segmentu 0,35 m: blacha Al, 673 m² × 650 zł": (673 * 650, "[Z]"),
        "korekta stawki ściany szczelinowej 0,60 m (zamiast 0,80): −16 % × 1 400 = −224 → 1 176, przyjęto 1 200 zł/m²":
            (-(1400 - 1200) * dw_area, "objętość wykopu i betonu −25 % × udział 65 %"),
        "ścieżki ogrodu z cegły z wykopu / płyt na podbudowie przepuszczalnej 550 m² × 400 zł": (550 * 400, "[Z]"),
        "rampy jednopasowe (175 m² wobec 243 m² v1.0): poz. 3.14 – udział ramp 0,6 × (−28 %)": (-0.6 * 0.28 * 0.8e6, "proporcja"),
        "szyb C1 w stanie surowym (rezerwa – połączenie z Maz. 19), bez urządzenia dźwigowego": (0.0, "windy_os 6 → 5"),
    }
    P["windy_os"] = 5
    # elewacje dziedzińcowe skrzydła i segmentu: tynk cienkowarstwowy mineralny na wełnie w tonie ceramiki posesji
    P["fas_went"] -= 410
    P["fas_tynk"] = 410
    # −2 bez dzioba skrzydła s > 52 (brak stanowisk; ≈ 60 m²)
    P["A_pod"] = round(P["A_pod"] - 60.0, 1)
    ex11 = sum(v[0] for v in POZA.values())
    t11, wk11, r11 = total(P, ex11)
    print(f"  A_nad {P['A_nad']}, A_pod {P['A_pod']} (−1 {g['L1']:.1f} + −2 {g['L2'] - 60:.1f}), obwód ścian {P['obw_pod']} m × 19 m, "
          f"wykop śr. {P['h_wyk']} m, płyta zastępcza {P['t_plyty']} m, wypór poza obrysem {P['fp_wypor']} m²")
    for k, (v, why) in POZA.items():
        print(f"     + {k}: {v * 1.0815 / 1e6:+.3f} mln (z KS i rezerwą; {why})")
    print(f"  grupy F.14.B: { {k: round(v / 1e6, 2) for k, v in sorted(r11['groups'].items())} }")

    print("== 2. Dźwignie projektowe v1.1 (efekt pojedynczy, mln zł z KS i rezerwą)")
    levers = [
        ("ościeża wieży 0,60 granit → 0,45 Al proszkowe", dict(), -(rw * 2000 - 824 * 650)),
        ("ościeża skrzydła ceramika → blacha Al", dict(), -(rm * 1450 - 673 * 650)),
        ("cokół skrzydła granit → ceramika (147 m²)", dict(), -147 * (2000 - 1450)),
        ("lamele korony 450 → 240 m² (redesign I-7)", dict(), -(450 - 240) * 800),
        ("BESS 250 → 150 kWh", dict(), -100 * 2200),
        ("ściany szczelinowe 0,80 → 0,60 m", dict(), -(1400 - 1200) * dw_area),
        ("pole sond 75 × 99 m → 58 × 91 m (+ ściany i pale energetyczne)", dict(), -(7425 - 58 * 91) * 240 + dw_area * 60 + 504 * 80),
        ("nawierzchnie: granit 1 050 → 500 m², ścieżki z cegły z wykopu 550 m²", dict(), -550 * (900 - 400)),
        ("zieleń: zachowane ogródki – pielęgnacja zamiast nowej zieleni", dict(), -470 * (500 - 100)),
        ("elewacje dziedzińcowe skrzydła i segmentu: ceramika → tynk mineralny (410 m²)", dict(), -410 * (1450 - 350)),
        ("dźwig C1 – szyb rezerwowy bez urządzenia", dict(), -0.6e6),
        ("lapidarium 0,5 → 0,3 mln", dict(), -0.2e6),
        ("rampy jednopasowe (poz. 3.14)", dict(), -0.6 * 0.28 * 0.8e6),
        ("−2 bez dzioba skrzydła (60 m²)", dict(), None),
    ]
    k = (1 + km.KS[1]) * (1 + km.REZ[1])
    for name, _, v in levers:
        if v is None:
            a, _, _ = total(dict(P, A_pod=P["A_pod"] + 60.0), ex11)
            v_m = t11 - a
        else:
            v_m = v * k / 1e6
        print(f"  {name}: {v_m:+.2f}")

    print("== 3. Wynik v1.1 (mid, netto, II kw. 2026)")
    rez = km.REZ[1]
    t_r = wk11 * rez
    print(f"  roboty + koszty stałe (KS 3 %): {wk11:.2f} mln")
    print(f"  rezerwa na nieprzewidziane (contingency) {rez:.0%} (wymóg ≥ 4 %): {t_r:.2f} mln")
    print(f"  RAZEM {t11:.2f} mln ≤ {LIMIT:.0f}: {'TAK' if t11 <= LIMIT else 'NIE'}; zapas do limitu {LIMIT - t11:.2f} mln "
          f"({(LIMIT - t11) / LIMIT:.1%}); bufor łącznie (rezerwa + zapas) {t_r + LIMIT - t11:.2f} mln ({(t_r + LIMIT - t11) / wk11:.1%} robót)")
    t4, _, _ = total(P, ex11, rez=0.04)
    print(f"  wariant kontrolny: rezerwa 4,0 % → {t4:.2f} mln (zapas {LIMIT - t4:.2f})")
    pc = P["A_nad"] + P["A_pod"]
    pu = 8400.0
    print(f"  wskaźniki: {t11 * 1e6 / pc:,.0f} zł/m² PC (PC {pc:,.0f} m²); {t11 * 1e6 / P['A_nad']:,.0f} zł/m² PC nadziemnej; "
          f"{t11 * 1e6 / pu:,.0f} zł/m² PU (PU {pu:,.0f}); PC/PU {pc / pu:.2f}")
    print("  pasma (koszty_benchmarki.md): 7 400–9 300 zł/m² PC; 11 400–14 900 zł/m² PU (B1/B2/B6) – PU v1.1 POWYŻEJ pasma "
          "(udział garażu MDS 2 kondygnacji, holi, sali Sejmiku; PC/PU wysokie)")
    lo, _, _ = (None, None, None)
    for lvl, fac in (("low", 0.8), ("high", 1.3)):
        q = dict(km.REF)
        q.update(P)
        r = km.compute(q, lvl)
        i = km.LEVELS[lvl]
        print(f"  scenariusz {lvl}: {r['total'] / 1e6 + ex11 * fac * (1 + km.KS[i]) * (1 + km.REZ[i]) / 1e6:.1f} mln")
    print(f"  waloryzacja +5 % (2027) od kosztu całkowitego: {t11 * 1.05:.1f} mln (ryzyko opisane, poza F.14.B)")
    out = os.path.join(HERE, "_rewizja_koszt_wejscie_v1_1.json")
    json.dump({k_: P[k_] for k_ in sorted(P)}, open(out, "w"), ensure_ascii=False, indent=1)
    print(f"  wejście modelu zapisane: {os.path.relpath(out, ROOT)}; pozycje spoza modelu: {ex11 / 1e6:.3f} mln (robót)")
    return dict(total=t11, works_ks=wk11, rez=t_r, P=P, poza=POZA, pc=pc)


if __name__ == "__main__":
    main()
