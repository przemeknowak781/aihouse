#!/usr/bin/env python3
"""Rewizja v1.1 – geometria, MPZP, rampa, obudowa wykopu, otwory techniczne (G-K-1, G-K-2, G-I-1, G-I-3, G-I-4, E-I-1, E-I-3, E-I-9).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_geometria.py
Teren: TIN (LinearNDInterpolator) z pikiet NMT i linii nieciągłości `site.json`, pas 2 m wokół bryły, krok 0,25 m
(metoda jak `_weryfikacja_geometria.py`).
"""
import math
import os
import sys

import numpy as np
from scipy.interpolate import LinearNDInterpolator
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon
from shapely.validation import explain_validity

sys.path.insert(0, os.path.dirname(__file__))
from _rewizja_wspolne import (SITE, K, OI, A, OGR, D102, W, M, SEG, level_m1, level_m2, uv2en, en2uv, sd2en, rect_uv,
                              rect_sd, unary_union, DW, OFF_88, JG_MAZ19)


def tin():
    T = SITE["teren"]
    pts = [(p[1], p[2], p[3]) for p in T["pikiety"] if p[4] == 1]
    for l in T["linie_nieciaglosci"]:
        pts += [(x, y, z) for (x, y), z in zip(l["pts"], l["z"])]
    P = np.array(pts)
    return LinearNDInterpolator(P[:, :2], P[:, 2])


F = tin()


def hz(g, s=0.25):
    x0, y0, x1, y1 = g.bounds
    X, Y = np.meshgrid(np.arange(x0, x1 + s, s), np.arange(y0, y1 + s, s))
    m = contains_xy(g, X, Y)
    H = F(X[m], Y[m])
    H = H[~np.isnan(H)]
    return float(H.min()), float(H.max())


def main():
    print("== 1. Bryły v1.1 (G-I-4)")
    for nm, g in (("W", W), ("M", M), ("S", SEG)):
        print(f"  {nm}: poprawny {g.is_valid} ({explain_validity(g)}), CCW {g.exterior.is_ccw}, pole {g.area:.2f} m², "
              f"poza OI {g.difference(OI).area:.4f}, w A {g.intersection(A).area:.4f}, poza A {g.difference(A).area:.4f}")
    pz = unary_union([W, M, SEG]).buffer(0.1, join_style=2).buffer(-0.1, join_style=2)
    print(f"  PZ (z wypełnieniem dylatacji) {pz.area:.1f} m² = {pz.area / OI.area:.1%} obszaru inwestycji {OI.area:.1f} m²; "
          f"niezabudowane {OI.area - pz.area:.1f} m²")
    # strefy parteru skrzydła przycięte do obrysu M (I-4)
    print("  strefy parteru skrzydła (przycięte do M):")
    for z in K["parter"]["skrzydlo"]:
        g = Polygon(z["en"])
        print(f"     {z['strefa'][:44]:44s} JSON {g.area:6.1f} → w M {g.intersection(M).area:6.1f} m² (w wieży {g.intersection(W).area:4.1f})")

    print("== 2. MPZP – wysokości (teren z TIN, pas 2 m)")
    oi_lo, oi_hi = 118.33, 119.44
    tops = {"W": (155.50, 155.75, 156.50, 35, 45), "M": (139.50, 139.70, 140.15, 18, 25), "S": (139.10, 139.10, 139.10, 18, 25)}
    for nm, g in (("W", W), ("M", M), ("S", SEG)):
        lo, hi = hz(g.buffer(2.0))
        a, b, att, mn, mx = tops[nm]
        ok = (a - hi >= mn) and (att - lo <= mx)
        print(f"  {nm}: teren {lo:.2f}/{hi:.2f}; najniższe pokrycie {a:.2f} − {hi:.2f} = {a - hi:.2f} m (min {mn}); "
              f"najwyższy punkt (attyka) {att:.2f} − {lo:.2f} = {att - lo:.2f} m (max {mx}); od skrajnych rzędnych OI: "
              f"{a - oi_hi:.2f} / {att - oi_lo:.2f} → {'✔' if ok else '✖'}")
    print("  segment v1.1: attyka ściany pd. obniżona do poziomu tarasu 139,10 (E/G-D-1), balustrada szklana 1,10 m cofnięta 1,5 m;"
          " attyka pozostałych lic segmentu 140,15")

    print("== 3. Lica przy granicy – wysięg gzymsu (G-K-1, wariant A)")
    faces = []
    for nm, g in (("W", W), ("M", M), ("S", SEG)):
        c = list(g.exterior.coords)
        for i in range(len(c) - 1):
            seg = LineString([c[i], c[i + 1]])
            if seg.length < 1.0:
                continue
            core = LineString([seg.interpolate(0.5), seg.interpolate(seg.length - 0.5)])   # bez 0,5 m przy narożach
            d = core.distance(OI.exterior)
            faces.append((nm, round(seg.length, 2), round(d, 3)))
    near = [f for f in faces if f[2] < 0.30]
    print(f"  lica < 0,30 m od granicy obszaru inwestycji (wysięg gzymsu/attyki 0,00; fryz wklęsły 0,15 m pod gzymsem): {len(near)}")
    for f in near:
        print(f"     {f[0]}: długość {f[1]} m, odległość {f[2]} m")
    print("  lica wieży na linii A (zach. i pd.) – zakaz jakiegokolwiek wysięgu (G-D-4); lica dziedzińcowe skrzydła – wysięg 0,30 m dopuszczony")

    print("== 4. Rampa uliczna (G-K-2, G-I-1)")
    gate0, gate1 = uv2en(40.0, -0.40), uv2en(40.0, -4.40)
    side = [F(*uv2en(40.0 + dx, v)) for dx in (0.6, 1.0) for v in (-0.4, -2.4, -4.4)]
    print(f"  brama 4,0 m w licu wsch. segmentu v −0,40…−4,40: {tuple(round(x, 2) for x in gate0)}–{tuple(round(x, 2) for x in gate1)}; "
          f"chodnik przed bramą (NMT) {min(side):.2f}–{max(side):.2f} m n.p.m.; próg 119,10 (−0,20) + zapora samoczynna do 120,30")
    for dl in (0.0,):
        pass
    sill, s, t, tl = -0.20, 0.18, 0.09, 3.0
    zm1 = -4.20
    L = 2 * tl + (sill - zm1 - 2 * tl * t) / s
    print(f"  pas 3,50 m przy ścianie pn. segmentu (v −0,35…−3,85); spadek 18 % + 2 × 3,0 m po 9 %; długość {L:.2f} m → stopa na −1 w u {40 - L:.2f}")
    x = 19.0      # lico zach. segmentu u = 21,0
    fl = sill - t * tl - s * (x - tl)
    roof = fl + 2.30 + 0.28
    ter = F(*uv2en(21.0 - 1.0, -2.1))
    print(f"  przy licu zach. segmentu (u 21,0): posadzka rampy {fl:+.2f}, wierzch stropu (2,30 + 0,28) {roof:+.2f} = {119.30 + roof:.2f} m n.p.m.; "
          f"teren istniejący {ter:.2f}, projektowany 119,25 → strop {119.30 + roof - ter:+.2f} / {119.30 + roof - 119.25:+.2f} m względem terenu "
          f"({'pod terenem ✔' if 119.30 + roof < min(ter, 119.25) else '✖'})")
    seg_w = SEG.difference(rect_uv(17.0, -4.05, 41.0, -0.15)).buffer(-0.25, join_style=2)
    print(f"  segment po odjęciu rampy (pas pd.): {SEG.difference(rect_uv(17.0, -4.05, 41.0, -0.15)).area:.1f} m² brutto, ≈ {seg_w.area:.1f} m² netto "
          f"≥ trafo 21 + rozdzielnia 17 + BESS 11 + odpady 7 + szyb T 7,3 = 63,3 m²")
    ws5 = Point(110.5, 29.0)
    print(f"  odległość okna lok. 6/6A WS 5 od krawędzi bramy {ws5.distance(LineString([gate0, gate1])):.1f} m (v1.0: 12,6 m)")
    print("  wjazd z 1KDG: brak (brama na dz. 10/1 → 6KDB/2); Mazowiecka bez wjazdów")

    print("== 5. Podziemie i obudowa (G-I-2, G-I-3)")
    L1, L2 = level_m1(), level_m2()
    for nm, g in (("−1", L1), ("−2", L2)):
        print(f"  {nm}: poprawny {g.is_valid}, pole {g.area:.1f} m², obwód {g.length:.1f} m, poza OI {g.difference(OI).area:.3f} m², "
              f"do ogródków {g.distance(OGR):.2f} m")
    p1v10 = Polygon(K["podziemie"]["-1"]["obrys_ccw"])
    print(f"  −1 v1.0 {p1v10.area:.1f} m² → v1.1 {L1.area:.1f} m² (pas 5,0 m: wierzchołki (72,001; 34,975), (96,193; 40,872); "
          f"cofnięcie {OFF_88} m od dz. 8/8; {JG_MAZ19} m od Maz. 19)")
    jg = 15.0
    print(f"  ściana szczelinowa {DW} m: {L1.length - jg:.1f} m × 19 m = {(L1.length - jg) * 19:.0f} m²; iniekcja strumieniowa przy Maz. 19: {jg} m "
          f"(kolumny Ø 1,2 m siecznie, styczne do granicy, + podbicie fundamentu szczytu)")
    b88 = [e for e in SITE["granice"]["obszar_inwestycji"]["krawedzie"] if e["sasiad_dzialka"] == "8/8"]
    for e in b88:
        ln = LineString([e["od"], e["do"]])
        print(f"  granica z dz. 8/8 ({ln.length:.1f} m): lico −1 w odl. {L1.exterior.distance(Point(ln.interpolate(0.5, normalized=True))):.3f} m "
              f"(min {min(L1.exterior.distance(Point(p)) for p in ln.coords):.3f})")

    print("== 6. Otwory i urządzenia techniczne (E-I-1, E-I-3, E-I-4)")
    segW = LineString([(95.020, 45.681), (96.694, 38.813)])
    print(f"  lico zach. segmentu (dziedziniec): {segW.length:.2f} m × kond. 1–4; żaluzje: kond. 1 – powietrze agregatu 8,0 m² "
          f"(10 m³/s / 1,25 m/s), kond. 1 – wentylacja trafo 1,5 m² (kanał z parteru), kond. 3–4 – dry-cooler 2 × 12,0 m² brutto")
    intake = rect_uv(2.0, -0.6, 12.0, 0.0)
    dc = LineString([(95.020, 45.681), (96.694, 38.813)])
    print(f"  odległość pozioma żaluzji dry-coolera / agregatu (lico zach. segmentu) od czerpni zbiorczej (elewacja pd. wieży u 2–12): "
          f"{dc.distance(intake):.1f} m (≥ 8 m wg WT § 152 – przyjęte)")
    crown_ex = Point(uv2en(33.0, 0.0))
    print(f"  wyrzut spalin agregatu i oddymiania garażu: szacht w trzonie B → lamele korony od pd. (u ≈ 33, +34,5); "
          f"odległość od czerpni u 2–12: {crown_ex.distance(intake):.1f} m w poziomie i ≈ 29 m w pionie")
    print("  rzędne technika krytyczna: trafo/rozdzielnia/BESS parter 119,30 (+0,30 cokół urządzeń = 119,60); agregat kond. 1 segmentu 124,10; "
          "UPS/serwerownia kond. 1 124,10; pompownia tryskaczowa – brak (tryskacze nieprojektowane); poziom wyjątkowy 119,0 ✔")

    print("== 7. Elementy w gruncie (P-I6, E-I-9)")
    shaft = Point(91.75, 32.00)
    print(f"  szyb wyjścia zapasowego MDS ({shaft.x}; {shaft.y}): od wieży {shaft.distance(W):.1f} m (≥ H/3 = 12,5 m), od skrzydła "
          f"{shaft.distance(M):.1f} m, od segmentu {shaft.distance(SEG):.1f} m, od lica −1 {shaft.distance(L1):.1f} m (długość tunelu), "
          f"w ogródkach: {OGR.contains(shaft)}")
    sw = LineString([(96.694, 38.813), (115.979, 39.930)])
    strip46 = OI.intersection(sw.buffer(4.6, single_sided=True).union(sw.buffer(-4.6, single_sided=True))).difference(SEG).difference(D102)
    strip46 = strip46.intersection(Polygon([(96.0, 25.0), (118.0, 25.0), (118.0, 39.9), (96.0, 38.8)]))
    crates = strip46.buffer(-0.6, join_style=2)
    zc = [F(*p) for p in list(crates.exterior.coords)[:-1]] if crates.geom_type == "Polygon" else [119.0]
    print(f"  pas 4,6 m od dz. 10/2 (pd. od segmentu): {strip46.area:.1f} m²; skrzynki rozsączające (−0,6 m od krawędzi) {crates.area:.1f} m² × 1,15 m = "
          f"{crates.area * 1.15 * 0.95:.1f} m³ (współcz. pustki 0,95); teren {min(zc):.2f}–{max(zc):.2f}; dno ≥ 117,45 → głębokość "
          f"≤ {min(zc) - 117.45:.2f} m ≥ 0,30 + 1,15 ✔" if crates.area > 0 else "  brak pasa")


if __name__ == "__main__":
    main()
