#!/usr/bin/env python3
"""Weryfikacja KOSZT / EKOLOGIA / ELEWACJE dla koncepcji „Brama i Latarnia” (synteza 1.0, 17.11.2026).

Dowód do raportu docs/20_koncepcja/weryfikacja_koszt_eko.md. Specyfikacji ani koncepcja.json nie zmienia.
Uruchomienie z katalogu repozytorium umwd:
    python3 -I docs/20_koncepcja/_weryfikacja_koszt_eko.py            # koszt, ościeża, PV/EP, dźwignie
    python3 -I docs/20_koncepcja/_weryfikacja_koszt_eko.py --cien     # + symulacja zacienienia dachów i ściany pd. segmentu (ok. 1–3 min)
Stawki: tools/koszty_model.py (poziom mid, II kw. 2026). Pozycje spoza modelu oznaczone [Z] = założenie weryfikatora.
"""
import importlib.util
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_s = importlib.util.spec_from_file_location("km", os.path.join(ROOT, "tools", "koszty_model.py"))
km = importlib.util.module_from_spec(_s)
_s.loader.exec_module(km)
F = (1 + km.KS[1]) * (1 + km.REZ[1])  # KS 3 % i rezerwa 5 % dla pozycji spoza modelu

# ---- 1. Parametry ze specyfikacji (rozdz. 12, akapit „Parametry”) ---------------------------------
SPEC = {"A_nad": 14151, "A_pod": 3763, "fp_pod": 2337, "obw_pod": 245, "h_sz": 18, "h_wyk": 6.9, "t_plyty": 1.1,
        "fp_nad": 2163, "fp_wypor": 175, "n_klatek": 3, "n_kond_klatki": 8.67, "windy_os": 6, "windy_tow": 1,
        "fas_went": 2100, "fas_kamien": 1810, "okna": 2180, "fas_sr": 410, "fas_bipv": 320, "przeslony": 450,
        "dach": 2160, "dach_ext": 0, "dach_int": 167, "stal_kg": 70000, "kwp_dach": 364, "kwh_bess": 250,
        "mb_odw": 7425, "A_teren": 2224, "t_kam": 1050, "t_ziel": 1100, "drzewa": 18, "ev": 55, "sciany_mobilne": 60}
# parametry nieujawnione w spec., dopasowane tak, by odtworzyć grupy z tabeli 12 (144,2 mln)
UKRYTE = {"h_pod": 6.5, "drogi": 0, "ogrodzenie": 0, "bal_zew": 60, "bal_wew": 125, "okna_wew": 142.5, "drzwi_zew": 106}
# korekta ilości (weryfikator): wykop i płyta z geometrii, PV wg poprawki K-2
KOREKTA = {"h_wyk": 6.49, "t_plyty": round(2389 / 2337, 3), "fas_bipv": 400, "fas_went": 2020, "kwp_dach": 351}
POZA_MODELEM = {  # zł netto robót, [Z]
    "korekty spec. (budowla ochronna 1,5 + lapidarium 0,5) – objęte KS i rezerwą": 2.0e6,
    "pale CFA 36 × Ø0,8 × 14 m = 504 mb × 1 100 zł": 0.554e6,
    "ściana na uskoku −1/−2: 38,1 m × 7,5 m × 1 250 zł/m²": 0.357e6,
    "dry-cooler hybrydowy 2 × 150 kW + żaluzje akustyczne i tłumiki": 0.45e6,
    "GPC: wiercenie z dna wykopu + 75 przepustów w białej wannie": 0.75e6,
}


def total(p, extra=0.0, lvl="mid"):
    q = dict(km.REF)
    q.update(p)
    r = km.compute(q, lvl)
    i = km.LEVELS[lvl]
    return r["total"] / 1e6 + extra * (1 + km.KS[i]) * (1 + km.REZ[i]) / 1e6, r


def grupy(r):
    return {k: round(v / 1e6, 2) for k, v in sorted(r["groups"].items())}


# ---- 2. Ościeża pominięte w ilościach elewacji --------------------------------------------------
def oscieza():
    P = 2.70  # przęsło filarów wieży; filar 1,05; ościeże 0,60
    lica = [("pn. u 0–26", 26.0, 4.80, 37.20), ("wsch. v 0–15,7", 15.7, 4.80, 37.20), ("pd. u 0–21", 21.0, 4.80, 37.20),
            ("pd. u 21–40 nad segmentem", 19.0, 20.85, 37.20), ("zach. nad skrzydłem", 29.7, 20.85, 37.20)]
    h = sum(int(L // P) * (b - a) for _, L, a, b in lica)
    ret_w = h * 2 * 0.60 - 41 * 1.05 * 2 * 0.60  # minus strefa kordonu +19,80–20,85
    osi = round(57.72 / 2.025) + round(34.15 / 2.025) + 1 + round(10.55 / 2.025) + round(7.07 / 2.025)
    ret_m = osi * 4 * 2 * (1.20 + 2.40) * 0.35 + round((57.7 + 34.2 + 10.6 + 7.1) / 4.05) * (2 * 4.40 + 3.70) * 0.35
    return round(ret_w), round(ret_m), osi


# ---- 3. PV / EP (metoda docs/40_prawo/_bilans_energii.py) ---------------------------------------
EPB, TOT = 297.0, 646.0
AF = 297e3 / 23.9


def ep(pv_mwh):
    sc = 0.8 * pv_mwh
    g = EPB - min(sc, EPB) * 0.6
    return g * 1000 / AF * 2.5, g * 0.6 * 1000 / AF


PV = {
    "SPEC": [("dach wieży 1 040 m² × 0,20", 208, 880), ("dach skrzydła 780 m² × 0,20", 156, 878), ("płyciny 318 m² × 0,15", 48, 562)],
    "REALNIE": [("dach wieży 935 m² × 0,20", 187, 880), ("dach skrzydła 635 m² × 0,20, cień wieży −11,4 %", 127, 793),
                ("płyciny od dziedzińca ≤ 25 m 92 m² × 0,15", 14, 450)],
    "POPRAWKA": [("dach wieży 935 m² × 0,215", 201, 880), ("dach skrzydła 700 m² × 0,215 (pas 0,5 m)", 150, 793),
                 ("płyciny 92 m² × 0,15", 14, 450), ("ściana pd. segmentu 310 m² × 0,15 (cień WS 5)", 46, 452)],
}


# ---- 4. Symulacja zacienienia (opcjonalnie) -----------------------------------------------------
def cien():
    import numpy as np
    import shapely
    from shapely.geometry import Polygon, Point, LineString
    from shapely.validation import make_valid
    d = json.load(open(os.path.join(ROOT, "model", "koncepcja.json")))
    W = Polygon(d["bryly"][0]["obrys_ccw"])
    M = make_valid(Polygon(d["bryly"][1]["obrys_ccw"]))
    if M.geom_type != "Polygon":
        M = max([g for g in M.geoms if g.geom_type == "Polygon"], key=lambda g: g.area)
    LAT, LON, GAM = 51.11, 17.03, math.radians(-0.75)

    def sun(doy, h):
        g = 2 * math.pi / 365 * (doy - 1 + (h - 12) / 24)
        de = (0.006918 - 0.399912 * math.cos(g) + 0.070257 * math.sin(g) - 0.006758 * math.cos(2 * g)
              + 0.000907 * math.sin(2 * g) - 0.002697 * math.cos(3 * g) + 0.00148 * math.sin(3 * g))
        eq = 229.18 * (0.000075 + 0.001868 * math.cos(g) - 0.032077 * math.sin(g) - 0.014615 * math.cos(2 * g)
                       - 0.040849 * math.sin(2 * g))
        ha = math.radians((h * 60 + eq + 4 * LON) / 4 - 180)
        la = math.radians(LAT)
        alt = math.asin(math.sin(la) * math.sin(de) + math.cos(la) * math.cos(de) * math.cos(ha))
        az = math.atan2(math.sin(ha), math.cos(ha) * math.sin(la) - math.tan(de) * math.cos(la)) + math.pi
        return alt, az - GAM

    steps = []
    for doy in range(1, 366, 3):
        for h in np.arange(3.25, 20, 0.5):
            alt, az = sun(doy, h)
            if alt > math.radians(2):
                am = 1 / (math.sin(alt) + 0.50572 * (math.degrees(alt) + 6.07995) ** -1.6364)
                steps.append((alt, az, 1361 * 0.7 ** (am ** 0.678)))

    def grid(poly, st=1.0):
        x0, y0, x1, y1 = poly.bounds
        return [Point(x, y) for x in np.arange(x0, x1, st) for y in np.arange(y0, y1, st) if poly.contains(Point(x, y))]

    def roof(pts, obst, dz):
        P = np.array([[p.x, p.y] for p in pts])
        blk = np.zeros(len(P))
        wsum = 0.0
        for alt, az, dni in steps:
            w = dni * math.sin(alt)
            wsum += w
            L = min(dz / math.tan(alt), 400.0)
            ln = shapely.linestrings(np.stack([P, P + [math.sin(az) * L, math.cos(az) * L]], axis=1))
            blk += shapely.intersects(ln, obst) * w
        bl = (blk / wsum).mean()
        s = 0.0
        sub = pts[::4]
        for p in sub:
            for k in range(72):
                a = 2 * math.pi * (k + 0.5) / 72
                it = LineString([(p.x, p.y), (p.x + math.sin(a) * 300, p.y + math.cos(a) * 300)]).intersection(obst)
                if not it.is_empty:
                    s += math.sin(math.atan(dz / max(Point(p.x, p.y).distance(it), 0.05))) ** 2
        svf = 1 - s / (72 * len(sub))
        return bl, svf, 0.48 * bl + 0.52 * (1 - svf)

    for nm, buf in (("skrzydło, wnętrze (−0,5 m)", 0.5), ("skrzydło, netto (−1,5 m)", 1.5)):
        pg = M.buffer(-buf, join_style=2)
        b, s, l = roof(grid(pg), W, 16.85)
        print(f"  dach {nm}: {pg.area:6.1f} m²; strata bezpośr. {b:.3f}; SVF {s:.3f}; strata roczna {l:.3f}")
    ring = W.difference(W.buffer(-0.5, join_style=2))
    for nm, buf in (("wieża, wnętrze (−0,55 m)", 0.55), ("wieża, netto (−1,5 m)", 1.5)):
        pg = W.buffer(-buf, join_style=2)
        b, s, l = roof(grid(pg), ring, 0.85)
        print(f"  dach {nm}: {pg.area:6.1f} m²; strata bezpośr. {b:.3f}; SVF {s:.3f}; strata roczna {l:.3f}")
    nb = json.load(open(os.path.join(ROOT, "model", "sasiedzi.json")))["budynki"]
    WS5 = Polygon([b for b in nb if b["id"] == "wybrzeze_slowackiego_5"][0]["obrys_egib_en"]).buffer(0)
    H = 139.5 - 119.3
    A, B = np.array([96.694, 38.813]), np.array([115.979, 39.930])
    t = (B - A) / np.linalg.norm(B - A)
    n = np.array([t[1], -t[0]])
    naz = math.atan2(n[0], n[1]) % (2 * math.pi)
    pts = [(A + t * s + n * 0.1, z) for s in np.arange(1, 19, 1.5) for z in (6, 9, 12, 15, 18)]
    num = den = 0.0
    for alt, az, dni in steps:
        ci = math.cos(alt) * math.cos(az - naz)
        if ci <= 0:
            continue
        for p, z in pts:
            L = max(H - z, 0) / math.tan(alt)
            hit = L > 0 and shapely.intersects(shapely.linestrings([p, p + [math.sin(az) * L, math.cos(az) * L]]), WS5)
            den += dni * ci
            num += 0 if hit else dni * ci
    eps = sum(math.atan(max(H - z, 0) / 10.58) for _, z in pts) / len(pts)
    fac = 0.48 * num / den + 0.52 * (1 - math.sin(eps))
    print(f"  ściana pd. segmentu: współczynnik uzysku {fac:.2f} → ≈ {787 * fac:.0f} kWh/kWp (pion S 787 wg strategii)")


def main():
    print("== 1. KOSZT (mid, mln zł netto, II kw. 2026)")
    t, r = total(SPEC)
    print(f"  parametry jawne spec.: {t:.2f}  grupy {grupy(r)}")
    sp = dict(SPEC, **UKRYTE)
    t, r = total(sp)
    print(f"  + parametry nieujawnione (dopasowanie do tabeli 12): {t:.2f}  grupy {grupy(r)}")
    t, _ = total(sp, 2.0e6)
    print(f"  spec. 144,2 + 2,0 objęte KS i rezerwą: {t:.2f} (spec.: 146,2)")
    kor = dict(sp, **KOREKTA)
    ex = sum(POZA_MODELEM.values())
    tb, rb = total(kor, ex)
    print(f"  B. korekta ilości + pozycje spoza modelu: {tb:.2f}")
    for k, v in POZA_MODELEM.items():
        print(f"     + {k}: {v * F / 1e6:.2f}")
    rw, rm, osi = oscieza()
    c = dict(kor, fas_kamien=kor["fas_kamien"] + rw, fas_went=kor["fas_went"] + rm)
    tc, _ = total(c, ex)
    tcl, _ = total(kor, ex + rw * 1600 + rm * 800)
    print(f"  ościeża pominięte: granit (filary wieży, 2 × 0,60 m) {rw} m²; ościeża okien i witryn skrzydła/segmentu {rm} m² ({osi} osi)")
    print(f"  C. B + ościeża: stawki modelu {tc:.2f}; stawki obniżone (granit 1 600, okładzina Al 800) {tcl:.2f}")
    for lvl, k in (("low", 0.8), ("high", 1.3)):
        print(f"     C {lvl}: {total(c, ex * k, lvl)[0]:.1f}")
    print(f"  zł/m² PC (C): {tc * 1e6 / 17914:.0f}; zł/m² PU 8 400 (C): {tc * 1e6 / 8400:.0f}; spec.: {146.2e6 / 8400:.0f} zł/m² PU")
    # dźwignie deklarowane w spec. (−1,6 mln) – sprawdzenie modelem
    base, _ = total(sp)
    dA = (1426.2 - 1145.8 - 167.4) / 7 * 3
    l1, _ = total(dict(sp, A_pod=sp["A_pod"] - dA, h_wyk=sp["h_wyk"] - dA * 3.35 / 2337))
    l2, _ = total(dict(sp, przeslony=sp["przeslony"] * 0.6))
    print(f"  dźwignie: pas −2 7→4 m ({dA:.1f} m²) {l1 - base:+.2f} (spec. −0,7); lamele −40 % {l2 - base:+.2f} (spec. −0,3); "
          f"granit cokołu skrzydła → ceramika (147 m²) {-147 * 550 * F / 1e6:+.2f} (spec. −0,4); ceramika 2 odcienie −0,2 (bez zmian)")
    # pakiet poprawek P
    retw45 = rw * 0.45 / 0.60
    p = dict(kor, przeslony=270, kwh_bess=150, A_pod=kor["A_pod"] - dA, h_wyk=kor["h_wyk"] - dA * 3.35 / 2337,
             fas_kamien=kor["fas_kamien"] - 147, fas_went=kor["fas_went"] + 147)
    tp, _ = total(p, ex + retw45 * 1000 + rm * 800)
    tp -= 0.2
    print(f"  P. pakiet (ościeża wieży 0,45 m okładzina Al {retw45:.0f} m², ościeża skrzydła Al, dźwignie realne, BESS 150 kWh): "
          f"{tp:.2f}, zapas {150 - tp:.2f}")

    print("\n== 2. PV / EP (autokonsumpcja 80 %, 60 % przypisane EPB, w_el 2,5; Af = 297 MWh / 23,9)")
    for k, v in PV.items():
        kwp = sum(x[1] for x in v)
        mwh = sum(x[1] * x[2] for x in v) / 1000
        e, co2 = ep(mwh)
        print(f"  {k}: {kwp} kWp, {mwh:.0f} MWh/rok, PV/EPB {mwh / EPB:.0%}, PV/całość {mwh / TOT:.0%}, EP {e:.1f}, emisje EPB {co2:.1f}")
        for x in v:
            print(f"      {x[0]:50s} {x[1]:4d} kWp × {x[2]:4d} kWh/kWp = {x[1] * x[2] / 1000:6.1f} MWh")

    print("\n== 3. Okna (wysokość w świetle a nadproże)")
    for nm, clear, sill, h in (("skrzydło (spec.)", 3.20, 0.90, 2.40), ("wieża, parapet 0,85", 3.32, 0.85, 2.45),
                               ("skrzydło – poprawka", 3.20, 0.60, 2.35), ("wieża – poprawka", 3.32, 0.55, 2.45)):
        head = sill + h
        print(f"  {nm:22s}: nadproże {head:.2f}, kaseta ZIP do {head + 0.18:.2f}, spód stropu {clear:.2f} → "
              f"{'OK' if head + 0.18 <= clear else 'KOLIZJA'}")
    print(f"  WWR skrzydła po poprawce: {1.20 * 2.35 / (2.025 * 3.75):.1%}")
    print("\n== 4. Lamele korony 0,25 × 0,60 co 0,90 m")
    print(f"  pełne przesłonięcie od kąta {math.degrees(math.atan((0.90 - 0.25) / 0.60)):.1f}° od normalnej (spec.: 34°)")
    for d in (80, 150, 200):
        print(f"  z {d} m: {1 / math.degrees(math.atan(0.90 / d)):.1f} cykla/stopień")
    print("\n== 5. Ściana zewnętrzna: wełna 200 mm λ 0,033 + żelbet 200")
    u0 = 1 / (0.26 + 0.2 / 0.033 + 0.2 / 2.5)
    print(f"  U bez łączników {u0:.3f}; z konsolami Al (ΔU 0,02–0,07) {u0 + 0.02:.2f}–{u0 + 0.07:.2f} (spec.: 0,15; WT: ≤ 0,20)")
    u1 = 1 / (0.26 + 0.26 / 0.033 + 0.2 / 2.5)
    print(f"  poprawka: 260 mm λ 0,033 → U0 {u1:.3f}, z łącznikami nierdzewnymi/GRP (ΔU ≤ 0,025) ≤ {u1 + 0.025:.2f}")

    print("\n== 6. GWP A1–A5 – szacunek zgrubny (ilości ze spec., wskaźniki rzędu wielkości EPD/ICE/TM65)")
    pc, pcn = 17914, 14151
    beton = (244.6 * 18 * 0.8 + 1426 * 1.1 + 911 * 0.9 + 36 * 14 * 0.503 + 38 * 7 * 0.6 + (1426 + 2337) * 0.35
             + 7 * 1146 * 0.28 + 1146 * 0.15 + 5 * 847 * 0.40 + 5 * 167 * 0.28 + 1617 + 6880 * 0.62 * 0.22 + 0.022 * pc + 208)
    rows = [(beton, 200, 260), (beton * 110, 0.45, 0.85), (70000, 1.0, 1.7), (2180, 90, 150), (410, 120, 200),
            (2908, 30, 55), (2773, 35, 65), (320, 150, 250), (1820, 120, 200), (2160, 25, 45), (pcn, 35, 65),
            (pcn, 70, 140), (7425, 10, 20), (250, 70, 120)]
    lo = sum(q * a for q, a, _ in rows) / pc * 1.08
    hi = sum(q * b for q, _, b in rows) / pc * 1.12
    print(f"  beton ≈ {beton:.0f} m³; A1–A5 ≈ {lo:.0f}–{hi:.0f} kg CO2e/m² PC (cel spec. ≤ 500)")

    if "--cien" in sys.argv:
        print("\n== 7. Zacienienie (tor słońca co 0,5 h, co 3 dni; udział bezpośr./rozpr. 0,48/0,52)")
        cien()


if __name__ == "__main__":
    main()
