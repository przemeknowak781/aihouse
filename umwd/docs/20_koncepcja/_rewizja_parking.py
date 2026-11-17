#!/usr/bin/env python3
"""Rewizja v1.1 – garaż: dowód liczby miejsc postojowych (układ stanowisk w shapely).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_parking.py [--png]
Założenia (WT § 21; wt_kluczowe.md 4.3): stanowisko 2,50 × 5,00 m, OzN 3,60 × 5,00 m, równoległe 2,50 × 6,00 m;
droga manewrowa 6,00 m (prostopadłe); rampa jednopasowa 3,50 m (+ 2 × 0,20 m odboje); ściana szczelinowa 0,60 m;
słupy wieży 0,60 × 0,60 m (linie u = 0 / 8,10 / 16,20 / 24,30 / 32,40 / 40,00) i siatka v1.1 v = 0 / 8,70 / 16,00 / 23,15
(słupy w liniach v = 8,70 i 23,15 jako 0,60 × 0,35 m w licu ścian korytarzy); stanowiska w trójkach 3 × 2,50 m między słupami.
Skrzydło i segment – bez słupów wewnętrznych (płyty sprężone 14,2 m; słupy w licach ścian, w strefie ściany szczelinowej).
Rzędne v1.1: posadzka −1 = −4,20 (115,10 m n.p.m.; kondygnacja 4,20 m, w świetle pod stropem 3,65 m – stackery zależne
2-poziomowe bez zagłębienia, wymagane ≥ 3,50 m [Z]); posadzka −2 = −7,20 (112,10 m n.p.m.; w świetle 2,70 m).
−2 obejmuje wieżę, segment, pas 5 m i skrzydło od s = 12,15 (bez M1 przy Maz. 19).
Wynik: liczba stanowisk na −1 i −2, spójność dróg, powierzchnie techniki, wymagana liczba wg MPZP § 13.
"""
import math
import sys

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _rewizja_wspolne import (uv2en, sd2en, rect_uv, rect_sd, poly_uv, level_m1, level_m2, W, SEG, M, DW, fmt)

# --------------------------------------------------------------------------- wymagana liczba miejsc (MPZP § 13)
PU_V11 = 8850.37    # m² PU v1.1 wg PN-ISO 9836 = suma pomieszczeń kategorii PU modelu pomieszczeń (F.15.A / F.15.C I.12;
                     # bez powierzchni ruchu RU 4 342, usługowej US 590 i garażowej PG 2 334 m²) – build/tabele/kontrola.md
try:                 # v1.2: PU z bilansu koncepcji (liczone przez _v12_koszt.py [K0]: PU v1.1 + S-3; zapis _v12_scalenie.py)
    import json as _json, os as _os
    _K = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", "model", "koncepcja.json"), encoding="utf-8"))
    PU = float(_K["bilans"]["PU_m2"])
    PU_SRC = f"model/koncepcja.json bilans.PU_m2 (meta.wersja {_K['meta']['wersja']}; _v12_koszt.py [K0])"
except (OSError, KeyError, ValueError):
    PU, PU_SRC = PU_V11, "PU v1.1 (model pomieszczeń)"
PU_GASTRO = 88.47    # m² PU bistro (SW.07 68,05 + SW.08 20,42) – 6 m.p./1000 m²
PU_PROGRAM = 8582.0  # m² PU programu M.01 (kontrola)
REQ = math.ceil(12 / 1000 * (PU - PU_GASTRO) + 6 / 1000 * PU_GASTRO)
REQ_PROG = math.ceil(12 / 1000 * (PU_PROGRAM - PU_GASTRO) + 6 / 1000 * PU_GASTRO)
REQ_CONS = math.ceil(12 / 1000 * PU) + math.ceil(6 / 1000 * PU_GASTRO)   # odczyt ostrożny: całe PU × 12 + bistro osobno

# --------------------------------------------------------------------------- konstrukcja
U_COLS = [0.0, 8.10, 16.20, 24.30, 32.40, 40.0]
V_COLS = {0.0: (0.6, 0.6), 8.70: (0.6, 0.35), 16.00: (0.6, 0.6), 23.15: (0.6, 0.35), 29.70: (0.6, 0.6)}  # v: (wymiar u, wymiar v)


def columns():
    out = []
    for v, (du, dv) in V_COLS.items():
        for u in U_COLS:
            c = rect_uv(u - du / 2, v - dv / 2, u + du / 2, v + dv / 2)
            if c.centroid.within(W.buffer(0.05)):
                out.append(c)
    return out


CORES = {
    "A": rect_uv(8.30, 12.45, 15.50, 20.85),
    "B": rect_uv(24.85, 0.50, 31.10, 9.90),
    "C": rect_sd(0.5, 8.4, 8.6, 14.5),
    # szyb dźwigu T 2 000 kg przeniesiony z trzonu B do narożnika SE segmentu (P-I5), przystanki −2…4,
    # na parterze przy drzwiach od Wybrzeża (punkt odpadów, dostawy ręczne)
    "T": rect_uv(36.90, -9.70, 39.20, -6.45),
}


RAMP_S = 0.18; RAMP_T = 0.09; RAMP_TL = 3.0     # spadek rampy i przejść (≤ 18 %, jak v1.0 – krytyka 20 % w K5)
Z_M1 = -4.20; Z_M2 = -7.20; SILL = -0.20        # posadzki −1, −2 i próg bramy (119,10 m n.p.m.) względem ±0,00


def ramp_len(drop):
    return 2 * RAMP_TL + (drop - 2 * RAMP_TL * RAMP_T) / RAMP_S


L_STREET = ramp_len(SILL - Z_M1)        # 25,2 m
L_INT = ramp_len(Z_M1 - Z_M2)           # 19,7 m


def street_ramp():
    """Rampa z Wybrzeża (G-K-2, G-I-1): pas 3,50 m przy ścianie pn. segmentu, v −0,35…−3,85 (+ odboje 0,20),
    od bramy w licu wsch. (u 40,0) na zach. do stopy na −1 (u 40,0 − L_STREET)."""
    return rect_uv(40.0 - L_STREET, -4.05, 40.0, -0.15)


def internal_ramp(level):
    """Rampa −1 ↔ −2 w kieszeni wsch. wieży (u 34,6–38,5): jednopasowa 3,50 m, 18 % + 2 × 3,0 m po 9 % (L_INT);
    wierzch na −1 przy drodze A2 (v 16,6), stopa na −2 w segmencie (droga A4).
    Obrys zajęty: −1 – otwór do miejsca, w którym strop −1 mieści się nad rampą (2,20 m + 0,30 m); −2 – cała długość."""
    x_open = RAMP_TL + ((Z_M1 - 0.30 - 2.20) - (Z_M1 - RAMP_TL * RAMP_T)) / -RAMP_S   # strop −1 nad rampą od tego miejsca
    return rect_uv(34.60, (16.60 - x_open) if level == "-1" else (16.60 - L_INT), 38.50, 16.60)


# ------------------------------------------------------------------- układ stanowisk: rzędy i drogi (współrzędne układów)
# droga: (układ, (a0, a1) wzdłuż osi u lub s, (b0, b1) wzdłuż v lub d)
# rząd:  (układ, (a0, a1), (b0, b1), typ 'P' prostopadłe / 'R' równoległe, trójki w siatce słupów 8,10 m: True/False)
COMMON_AISLES = [("uv", (-9.0, 24.6), (0.6, 6.6)),        # A1 – pd. (pas pod dziedzińcem / wieża), łączy się z A3
                 ("uv", (-6.0, 37.6), (16.6, 22.6)),      # A2 – pn. (przy trzonie A tylko 1,75 m – brak przejazdu)
                 ("sd", (12.2, 52.0), (5.75, 11.75))]     # A3 – skrzydło
COMMON_ROWS = [("uv", (0.3, 24.6), (6.6, 11.6), "P", True),     # R2 – do A1
               ("uv", (22.5, 31.1), (11.6, 16.6), "P", True),   # R3 wsch. – do A2 (na −2 strefa GPC – odrzucane)
               ("uv", (0.3, 8.3), (11.6, 16.6), "P", True),     # R3 zach. – do A2
               ("uv", (22.5, 34.4), (11.6, 16.6), "P", True),   # R3 wsch. – do A2
               ("uv", (-6.0, 37.6), (22.6, 27.6), "P", True),   # R4 – do A2 (łuk przycina)
               ("sd", (12.2, 54.0), (0.75, 5.75), "P", False),  # skrzydło, rząd zach. 90°
               ("sd", (12.2, 34.0), (11.75, 14.25), "R", False),  # skrzydło, rząd wsch. równoległy
               ("sd", (34.0, 52.0), (11.75, 16.75), "P", False)]  # skrzydło/wieża – klin przy licu zach. wieży
# rzędy ze stackerami zależnymi 2-poziomowymi (tylko −1, wys. w świetle ≥ 3,60 m): (układ, (a0, a1), (b0, b1))
STACK_ROWS_M1 = [("sd", (12.2, 54.0), (0.75, 5.75)),     # skrzydło, rząd zach. – jednostki podwójne 5,0 m (bez słupów)
                 ("uv", (-6.0, 37.6), (22.6, 27.6)),     # R4 – w przęśle 8,10 m: 1 jednostka 5,0 m + 1 stanowisko zwykłe
                 ("uv", (0.3, 24.6), (6.6, 11.6)),       # R2 – jw.
                 ("uv", (-3.3, 8.1), (-4.4, 0.6)),       # R1 – pas pod dziedzińcem, jw.
                 ("uv", (0.3, 8.3), (11.6, 16.6)),       # R3 zach. – jw.
                 ("uv", (22.5, 31.1), (11.6, 16.6))]     # R3 wsch. – jw.
STACK_UNIT_W = 5.0   # szerokość systemu 2 platform obok siebie (2 × 2,30 m + słupki) – wartość katalogowa typowa [Z]

# ------------------------------------------------------------------- układ stanowisk: rzędy i drogi (współrzędne układów)
# droga: (układ, (a0, a1) wzdłuż osi u lub s, (b0, b1) wzdłuż v lub d)
# rząd:  (układ, (a0, a1), (b0, b1), typ 'P' prostopadłe / 'R' równoległe, trójki w siatce słupów 8,10 m: True/False)
COMMON_AISLES = [("uv", (-9.0, 24.6), (0.6, 6.6)),        # A1 – pd. (pas pod dziedzińcem / wieża), łączy się z A3
                 ("uv", (-6.0, 37.6), (16.6, 22.6)),      # A2 – pn. (przy trzonie A tylko 1,75 m – brak przejazdu)
                 ("sd", (12.2, 52.0), (5.75, 11.75))]     # A3 – skrzydło
COMMON_ROWS = [("uv", (0.3, 24.6), (6.6, 11.6), "P", True),     # R2 – do A1
               ("uv", (22.5, 31.1), (11.6, 16.6), "P", True),   # R3 wsch. – do A2 (na −2 strefa GPC – odrzucane)
               ("uv", (0.3, 8.3), (11.6, 16.6), "P", True),     # R3 zach. – do A2
               ("uv", (-6.0, 37.6), (22.6, 27.6), "P", True),   # R4 – do A2 (łuk przycina)
               ("sd", (12.2, 54.0), (0.75, 5.75), "P", False),  # skrzydło, rząd zach. 90°
               ("sd", (12.2, 34.0), (11.75, 14.25), "R", False),  # skrzydło, rząd wsch. równoległy
               ("sd", (34.0, 52.0), (11.75, 16.75), "P", False)]  # skrzydło/wieża – klin przy licu zach. wieży
# pomieszczenia: nazwa -> (prostokąt strefy, wymagana powierzchnia netto m²); powierzchnia dostępna = strefa ∩ wnętrze − drogi
LEVELS = {
    "-1": {
        "aisles": COMMON_AISLES + [("uv", (16.5, 22.5), (-0.15, 16.7)),     # łącznik wsch.
                                   ("uv", (8.4, 14.8), (-4.05, 0.7))],      # stopa rampy ulicznej → A1
        "rows": COMMON_ROWS + [("uv", (-3.3, 8.1), (-4.4, 0.6), "P", True)],  # R1 – pas pod dziedzińcem
        "plant": {
            "warsztat PPT 40 + odpady 24 + magazyn MDS 20 (M1, przy trzonie C)": (rect_sd(1.25, 0.75, 12.0, 14.4), 84),
            "sanitariaty MDS / WC dostępne garażu 30 + pralnia 10 + porządkowe 8 (pn. od trzonu A)": (rect_uv(8.30, 21.0, 16.0, 29.1), 48),
            "centrala wentylacyjna S 40 (wsch. od trzonu B, piony w szachcie po dźwigu T); centrala P – kond. 1, pas zach.":
                (rect_uv(31.1, 0.6, 34.6, 16.6), 40),
            "woda szara – kompaktowa stacja podczyszczania (MBR) 27 (łuk NE, pn. od A2)": (rect_uv(30.0, 22.6, 39.4, 29.1), 27),
            "przyłącze wody i wodomierz 20 (pod wierzchem rampy ulicznej, h ≥ 2,3 m)": (rect_uv(33.4, -4.05, 39.3, -0.15), 20),
            "korytarz obsługi do dźwigu T, szer. ≥ 1,5 m (segment pd.)": (rect_uv(22.6, -6.4, 36.8, -4.25), 20),
        },
    },
    "-2": {
        "aisles": COMMON_AISLES + [("uv", (16.5, 22.5), (-4.4, 16.6)),       # łącznik wsch.
                                   ("uv", (16.5, 38.5), (-6.4, -0.4))],      # A4 – segment, do stopy rampy wewn.
        "rows": COMMON_ROWS + [("uv", (-3.3, 16.5), (-4.4, 0.6), "P", True)],
        "plant": {
            "maszynownia GPC + bufory 95 (przy trzonie B)": (unary_union([rect_uv(24.85, 9.9, 34.6, 16.6), rect_uv(31.1, 0.6, 34.6, 9.9)]), 95),
            "filtrowentylacja ukrycia 30 + WC ukrycia 15 (pn. od trzonu A)": (rect_uv(8.30, 21.0, 16.0, 29.1), 45),
            "zbiornik deszczówki 50 m³ (27 m² × h 1,85 m) (łuk NE, pn. od A2)": (rect_uv(30.0, 22.6, 39.4, 29.1), 27),
        },
    },
}


def to_poly(frame, a, b):
    return rect_uv(a[0], b[0], a[1], b[1]) if frame == "uv" else rect_sd(a[0], b[0], a[1], b[1])


def stalls_in_row(frame, a, b, typ, grid):
    out = []
    if typ == "P":
        w = 2.5
        if grid and frame == "uv":
            k0 = math.floor(a[0] / 8.1) - 1
            starts = [8.1 * k + 0.3 + 2.5 * j for k in range(k0, k0 + 8) for j in range(3)]
        else:
            starts = [a[0] + w * j for j in range(int((a[1] - a[0]) / w) + 1)]
    else:
        w = 6.0
        starts = [a[0] + w * j for j in range(int((a[1] - a[0]) / w) + 1)]
    for s0 in starts:
        if s0 >= a[0] - 1e-6 and s0 + w <= a[1] + 1e-6:
            out.append(to_poly(frame, (s0, s0 + w), b))
    return out


def layout(interior, obstacles, spec):
    aisles = [to_poly(f, a, b) for f, a, b in spec["aisles"]]
    aisle_u = unary_union([x.intersection(interior).difference(obstacles) for x in aisles])
    aisle_raw = unary_union(aisles)
    plant = unary_union([v[0] for v in spec["plant"].values()])
    stalls = []
    for f, a, b, typ, grid in spec["rows"]:
        for st in stalls_in_row(f, a, b, typ, grid):
            if st.difference(interior).area > 0.02 or st.intersection(obstacles).area > 0.02:
                continue
            if st.intersection(aisle_raw).area > 0.05 or st.intersection(plant).area > 0.05:
                continue
            if any(st.intersection(x).area > 0.01 for x in stalls):
                continue
            if st.buffer(1.0, join_style=2).intersection(aisle_u).area < 1.5:
                continue
            stalls.append(st)
    return stalls, aisle_u


def parts(g):
    return 1 if g.geom_type == "Polygon" else len(g.geoms)


def ozn(stalls, n, near):
    """Zamiana n stanowisk najbliższych trzonom A/B na OzN 3,60 m: każde OzN zabiera 1 sąsiednie stanowisko co drugie
    (3,6 + 3,6 = 7,2 m ≤ 3 × 2,5 m) – licząc konserwatywnie: n OzN = n stanowisk − ceil(n/2)."""
    return len(stalls) - math.ceil(n / 2)


def stacker_bonus(stalls):
    """Dodatkowe miejsca z jednostek podwójnych (2 sąsiednie stanowiska 2 × 2,50 m = 5,0 m → 4 miejsca)."""
    bonus = 0
    used = set()
    for f, a, b in STACK_ROWS_M1:
        row = to_poly(f, a, b).buffer(0.01)
        inrow = [i for i, x in enumerate(stalls) if x.within(row)]
        for i in inrow:
            if i in used:
                continue
            for j in inrow:
                if j != i and j not in used and stalls[i].buffer(0.02).intersection(stalls[j]).area > 0.01:
                    if stalls[i].union(stalls[j]).area > 24.0:   # dwa przyległe 12,5 m² – zwarta jednostka 5,0 × 5,0
                        used |= {i, j}
                        bonus += 2
                        break
    return bonus, len(used) // 2


def run(png=False):
    res = {}
    cols = columns()
    for lvl, L in (("-1", level_m1()), ("-2", level_m2())):
        I = L.buffer(-DW, join_style=2)
        cores = [c for k, c in CORES.items() if not (lvl == "-2" and k == "C")]
        obst = unary_union(cores + cols + [internal_ramp(lvl)] + ([street_ramp()] if lvl == "-1" else []))
        spec = LEVELS[lvl]
        st, au = layout(I, obst, spec)
        plant_ok = {}
        for k, (zone, need) in spec["plant"].items():
            avail = zone.intersection(I).difference(au)
            if "pod wierzchem rampy" not in k:      # pod rampą uliczną (u ≥ 33,4) wys. w świetle ≥ 2,3 m – pomieszczenie pod rampą
                avail = avail.difference(obst)
            plant_ok[k] = (round(avail.area, 1), need, avail.area >= need)
        bonus, units = stacker_bonus(st) if lvl == "-1" else (0, 0)
        res[lvl] = dict(L=L, I=I, stalls=st, aisles=au, cols=cols, obst=obst, plant=plant_ok, spec=spec,
                        bonus=bonus, units=units)
        if png:
            plot(lvl, res[lvl])
    return res


def plot(lvl, r):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(13, 13))

    def draw(g, **kw):
        gs = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
        for p_ in gs:
            if p_.geom_type == "Polygon":
                x, y = p_.exterior.xy
                ax.fill(x, y, **kw)
    draw(r["L"], fc="none", ec="k", lw=1.5)
    draw(r["I"], fc="#f4f4f4", ec="#999", lw=0.5)
    draw(r["aisles"], fc="#cde", ec="none")
    draw(r["obst"], fc="#888", ec="k", lw=0.5)
    for k, v in r["spec"]["plant"].items():
        draw(v[0].intersection(r["I"]).difference(r["aisles"]), fc="#fdb", ec="#a60", lw=0.7)
    for s_ in r["stalls"]:
        draw(s_, fc="#9c9", ec="g", lw=0.5)
    draw(W, fc="none", ec="b", lw=0.5, ls="--")
    draw(M, fc="none", ec="b", lw=0.5, ls="--")
    draw(SEG, fc="none", ec="b", lw=0.5, ls="--")
    ax.set_aspect("equal")
    ax.set_title(f"{lvl} v1.1: {len(r['stalls'])} stanowisk (przed OzN)")
    fig.savefig(f"/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/park_{lvl}.png", dpi=70)
    plt.close(fig)


def main():
    res = run("--png" in sys.argv)
    print(f"rampa uliczna {L_STREET:.2f} m (stopa u {40 - L_STREET:.2f}); rampa wewn. {L_INT:.2f} m")
    print(f"PU: {PU:.2f} m² – {PU_SRC}")
    print(f"wymagane MPZP § 13: 12/1000 × (PU {PU:.0f} − {PU_GASTRO:.0f}) + 6/1000 × {PU_GASTRO:.0f} = "
          f"{12 / 1000 * (PU - PU_GASTRO) + 6 / 1000 * PU_GASTRO:.2f} → {REQ} m.p.; PU programu {PU_PROGRAM:.0f} → {REQ_PROG} m.p.")
    tot = 0
    for lvl, r in res.items():
        n = len(r["stalls"])
        tot += n + r["bonus"]
        print(f"{lvl}: obrys {r['L'].area:.1f} m², wnętrze {r['I'].area:.1f} m², stanowisk na posadzce {n}; "
              f"stackery: {r['units']} jedn. podwójnych → +{r['bonus']} m.p.; razem {n + r['bonus']}; drogi – części {parts(r['aisles'])}")
        for k, v in r["plant"].items():
            print(f"     pomieszczenie: {k}: dostępne {v[0]} m² ≥ wymagane {v[1]} m²: {'TAK' if v[2] else 'NIE'}")
    n_ozn = 6
    net = tot - math.ceil(n_ozn / 2)
    print(f"RAZEM pozycji: {tot}; po wydzieleniu {n_ozn} stanowisk OzN 3,60 m (2 OzN w miejsce 3 zwykłych): {net} m.p.")
    print(f"wymagane {REQ} (PU {PU:.2f}, bistro {PU_GASTRO}) / ostrożnie {REQ_CONS} / PU programu {REQ_PROG} → zapas "
          f"{net - REQ} / {net - REQ_CONS} / {net - REQ_PROG}")
    conv = sum(len(r["stalls"]) for r in res.values()) - math.ceil(n_ozn / 2)
    print(f"bez stackerów (sama posadzka): {conv} m.p.; w stackerach (poziom górny platform): {tot - sum(len(r['stalls']) for r in res.values())}")
    return res


if __name__ == "__main__":
    main()
