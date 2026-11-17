#!/usr/bin/env python3
"""Rewizja v1.1 – bilans drzew wg numeracji i położeń operatu M.06 (wiążący – Wyj. 13 odp. 65, R-215).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_rewizja_drzewa.py
Metoda położeń (jak `30_lokalizacja/dendrologia.md`, rozdz. 0): z wektorowego PDF załącznika graficznego M.06 (1:200)
odczytano symbole pni (wypełnione okręgi) i numery z liniami odnośników; rysunek przesunięto (bez obrotu, skala
1 pt = 0,2 × 0,3528 mm × 1000 = 0,0705556 m) tak, by pnie nr 1 i 2 pokryły się z D701 i D702 (M.02). Dokładność ±0,5–1 m.
Rekomendacje Z1/Z2/Z3/U/K/P i strefy projektowe – tabela 2 `dendrologia.md` (wniosek tamtego opracowania).
Kryteria v1.1:
  * usuwane – kolizja: pień w obrysie bryły nadziemnej lub podziemia v1.1, albo ≤ 1,0 m od lica podziemia
    (ściana szczelinowa 0,60 m + ściana prowadząca + pas roboczy – przyjęto 1,5 m), albo strefa projektowa Z1/Z2 przecięta przez obrys
    podziemia/bryły o > 1,0 m (zasady SOD operatu: bez robót ziemnych, bez przecinania korzeni Ø > 4 cm);
  * usuwane – sanitarnie: rekomendacja U (martwe/zamierające), niezależnie od inwestycji;
  * zachowane z ochroną: strefa przecięta o ≤ 1,0 m (wygrodzenie korona + 1 m, ręczne odkrywki, nadzór arborysty);
  * zachowane: pozostałe.
"""
import glob
import json
import math
import os
import sys

import pymupdf
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(__file__))
from _rewizja_wspolne import ROOT, SITE, OI, A, OGR, W, M, SEG, level_m1, uv2en, rect_uv

TREES_M06 = {  # nr: (gatunek, rekomendacja, strefa projektowa [m]) – dendrologia.md tab. 2 (44 gatunki drzewiaste)
    1: ("klon zwyczajny", "K", 4.5), 2: ("klon zwyczajny", "Z2/U", 6.4), 3: ("klon zwyczajny", "Z1", 4.2),
    4: ("klon zwyczajny", "Z3", 3.5), 5: ("brzoza brodawkowata", "U", 3.1), 6: ("brzoza brodawkowata", "Z3", 3.0),
    7: ("brzoza brodawkowata", "Z2", 5.1), 8: ("świerk pospolity", "Z3", 5.1), 9: ("śliwa tarnina", "Z3", 3.1),
    10: ("kasztanowiec biały", "Z2", 6.2), 12: ("lipa drobnolistna", "Z2", 6.3), 13: ("robinia akacjowa", "U", 3.0),
    14: ("jesion wyniosły", "Z2", 6.2), 15: ("sosna zwyczajna", "Z3", 2.1), 16: ("sosna zwyczajna", "Z3", 3.0),
    17: ("sosna czarna", "Z3", 3.1), 18: ("robinia akacjowa", "U", 3.0), 19: ("robinia akacjowa", "U", 3.0),
    20: ("robinia akacjowa", "U", 3.0), 26: ("lipa szerokolistna", "Z1", 4.0), 27: ("magnolia pośrednia", "P", 3.0),
    28: ("robinia akacjowa", "Z2", 6.4), 38: ("sosna czarna", "U", 3.0), 46: ("klon zwyczajny", "Z1", 5.2),
    50: ("jesion wyniosły", "Z1", 4.2), 52: ("świerk pospolity", "Z3", 3.0), 53: ("świerk pospolity", "U", 3.0),
    54: ("świerk pospolity", "Z3", 3.0), 55: ("świerk pospolity", "P", 3.0), 56: ("świerk pospolity", "P", 3.0),
    57: ("świerk pospolity", "U", 3.0), 58: ("klon zwyczajny", "Z1", 4.2), 59: ("sosna zwyczajna", "U", 3.0),
    60: ("wierzba mandżurska", "Z2", 6.2), 61: ("jesion wyniosły", "Z3", 3.5), 62: ("jesion wyniosły", "U", 3.1),
    67: ("klon zwyczajny", "Z1", 3.1), 72: ("jodła pospolita", "P", 1.1), 78: ("świerk pospolity", "Z1", 3.1),
    79: ("śliwa wiśniowa 'Pissardii'", "Z2", 5.1), 80: ("śliwa wiśniowa 'Pissardii'", "Z2", 3.2),
    81: ("śliwa wiśniowa 'Pissardii'", "Z2", 3.2), 89: ("klon zwyczajny", "Z1", 3.8), 90: ("klon zwyczajny", "Z1", 4.0),
}
PT = 0.2 * 25.4 / 72  # m na punkt PDF w skali 1:200


def m06_positions():
    f = glob.glob(os.path.join(ROOT, "00_materialy", "_rozpak", "5_Zal*pop*", "M.06*", "M.06*", "*graficzny.pdf"))[0]
    page = pymupdf.open(f)[0]
    d = page.get_drawings()
    sym = [((x["rect"].x0 + x["rect"].x1) / 2, (x["rect"].y0 + x["rect"].y1) / 2)
           for x in d if x["type"] == "f" and len(x["items"]) == 16]
    lines = [x["items"][0] for x in d if x["type"] == "s" and len(x["items"]) == 1 and x["items"][0][0] == "l"]
    words = [w for w in page.get_text("words") if w[4].isdigit() and w[1] < 1600]   # bez tabliczki rysunku
    pos = {}
    for x0, y0, x1, y1, t, *_ in words:
        nr = int(t)
        if nr not in TREES_M06 or nr in pos:
            continue
        best = None
        for _, a, b in lines:
            for P_, Q_ in ((a, b), (b, a)):
                dl = math.hypot(max(x0 - P_.x, 0, P_.x - x1), max(y0 - P_.y, 0, P_.y - y1))
                if dl < 2.5:
                    s = min(sym, key=lambda s: math.hypot(s[0] - Q_.x, s[1] - Q_.y))
                    ds = math.hypot(s[0] - Q_.x, s[1] - Q_.y)
                    if best is None or ds < best[0]:
                        best = (ds, s)
        if best is None or best[0] > 6:
            s = min(sym, key=lambda s: math.hypot(s[0] - (x0 + x1) / 2, s[1] - (y0 + y1) / 2))
            best = (0, s)
        pos[nr] = best[1]
    # georeferencja: translacja dopasowana do D701 (nr 1) i D702 (nr 2, średnia z 2 punktów)
    m02 = {}
    for t in SITE["zielen"]["drzewa"]:
        m02.setdefault(t["nr"], []).append((t["e"], t["n"]))
    ref = {1: m02["D701"][0], 2: tuple(sum(c) / len(c) for c in zip(*m02["D702"]))}
    de = sum(ref[k][0] - pos[k][0] * PT for k in ref) / 2
    dn = sum(ref[k][1] + pos[k][1] * PT for k in ref) / 2
    return {k: (round(de + x * PT, 2), round(dn - y * PT, 2)) for k, (x, y) in pos.items()}, m02


def main():
    pos, m02 = m06_positions()
    L1 = level_m1()
    bryly = unary_union([W, M, SEG])
    # elementy zagospodarowania v1.1 w gruncie (poza obrysem podziemia)
    shaft = Point(91.75, 32.00).buffer(1.6)                     # szyb wyjścia zapasowego MDS (P-I6) – obrys z obudową
    tunnel = Polygon([uv2en(13.9, -4.4), uv2en(15.3, -4.4), uv2en(15.3, -12.6), uv2en(13.9, -12.6)])
    crates = rect_uv(23.0, -14.3, 38.0, -11.4)                 # skrzynki rozsączające pod nawierzchnią pasa 4,6 m (E-I-9)
    extra = unary_union([shaft, tunnel])
    rows, stat = [], {"kolizja": [], "przesadzane": [], "sanitarnie": [], "ochrona": [], "zachowane": []}
    for nr in sorted(TREES_M06):
        sp, rec, zone = TREES_M06[nr]
        if nr not in pos:
            print("BRAK położenia nr", nr)
            continue
        p = Point(pos[nr])
        d_ug = L1.exterior.distance(p) if not L1.contains(p) else -L1.exterior.distance(p)
        d_b = bryly.distance(p) if not bryly.contains(p) else 0.0
        d_x = extra.distance(p)
        intr = max(0.0, zone - min(max(d_ug, 0), d_b if d_b > 0 else 0, d_x)) if d_ug > 0 else zone
        inside = L1.contains(p) or bryly.contains(p)
        if rec == "U":
            cat = "sanitarnie"
        elif inside or d_ug <= 1.5 or d_b <= 0.5 or (rec in ("Z1", "Z2", "K", "Z2/U") and intr > 1.0) or A.contains(p):
            cat = "kolizja"
        elif intr > 0:
            cat = "ochrona"
        else:
            cat = "zachowane"
        if cat == "kolizja" and rec == "P":       # kandydat do przesadzenia (młode drzewo) – przesadzane w obrębie ogrodu
            cat = "przesadzane"
        stat[cat].append(nr)
        near = min(((k, Point(c).distance(p)) for k, cs in m02.items() for c in cs), key=lambda x: x[1])
        rows.append((nr, sp, rec, zone, d_ug, d_b, intr, cat, near, OGR.contains(p), OI.contains(p)))
    print("| Nr M.06 | Gatunek | Rek. | Strefa [m] | Odl. od lica −1 [m] | Odl. od bryły [m] | Wejście w strefę [m] | "
          "Ogródki | Najbliższy pkt M.02 | Decyzja v1.1 |")
    print("|---:|---|---|---:|---:|---:|---:|---|---|---|")
    for nr, sp, rec, zone, d_ug, d_b, intr, cat, near, og, oi in rows:
        print(f"| {nr} | {sp} | {rec} | {zone:.1f} | {d_ug:.2f} | {d_b:.2f} | {intr:.2f} | {'tak' if og else 'nie'} | "
              f"{near[0]} ({near[1]:.1f} m) | {cat} |")
    n = len(rows)
    kept = len(stat["zachowane"]) + len(stat["ochrona"])
    keep_all = kept + len(stat["przesadzane"]) + len(stat["sanitarnie"])
    print(f"\nDrzewa M.06 (gatunki drzewiaste): {n}")
    for k, v in stat.items():
        print(f"  {k}: {len(v)} → nr {v}")
    print(f"  zachowane w miejscu: {kept}; + przesadzane {len(stat['przesadzane'])}; usuwane kolizyjnie {len(stat['kolizja'])}; "
          f"sanitarnie (U) {len(stat['sanitarnie'])}")
    print(f"  bilans: zachowane {keep_all} z {n} ({keep_all / n:.0%}) bez usunięć sanitarnych; "
          f"{keep_all - len(stat['sanitarnie'])} z {n} ({(keep_all - len(stat['sanitarnie'])) / n:.0%}) po usunięciach sanitarnych")
    z12 = [r for r in rows if r[2] in ("Z1", "Z2")]
    z12k = [r for r in z12 if r[7] in ("zachowane", "ochrona")]
    print(f"  Z1+Z2: {len(z12)}, zachowane {len(z12k)}; usunięte Z1/Z2: {[r[0] for r in z12 if r not in z12k]}")
    print(f"  kontrola elementów w gruncie: szyb MDS – najbliższe drzewo "
          f"{min(Point(pos[k]).distance(shaft) for k in pos):.1f} m; skrzynki rozsączające – najbliższe drzewo "
          f"{min(Point(pos[k]).distance(crates) for k in pos):.1f} m")
    json.dump({"polozenia_M06": {str(k): v for k, v in pos.items()}, "bilans": stat},
              open(os.path.join(os.path.dirname(__file__), "_rewizja_drzewa_wynik.json"), "w"), ensure_ascii=False, indent=1)
    return stat, pos


if __name__ == "__main__":
    main()
