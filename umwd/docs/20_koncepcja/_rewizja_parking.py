#!/usr/bin/env python3
"""Rewizja v1.1 – garaż: dowód liczby miejsc postojowych (układ stanowisk w shapely).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_parking.py [--png]
Założenia (WT § 21; wt_kluczowe.md 4.3): stanowisko 2,50 × 5,00 m, OzN 3,60 × 5,00 m, równoległe 2,50 × 6,00 m;
droga manewrowa 6,00 m (prostopadłe); rampa jednopasowa 3,50 m (+ 2 × 0,20 m odboje); ściana szczelinowa 0,60 m;
słupy wieży 0,60 × 0,60 m (linie u = 0 / 8,10 / 16,20 / 24,30 / 32,40 / 40,00) i siatka v1.1 v = 0 / 8,67 / 16,00 / 22,95
(słupy w liniach v = 8,67 i 22,95 jako 0,60 × 0,35 m w licu ścian korytarzy); stanowiska w trójkach 3 × 2,50 m między słupami.
Skrzydło i segment – bez słupów wewnętrznych (płyty sprężone 14,2 m; słupy w licach ścian, w strefie ściany szczelinowej).
Wynik: liczba stanowisk na −1 i −2, spójność dróg, powierzchnie techniki, wymagana liczba wg MPZP § 13.
"""
import math
import sys

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _rewizja_wspolne import (uv2en, sd2en, rect_uv, rect_sd, poly_uv, level_m1, level_m2, W, SEG, M, DW, fmt)

# --------------------------------------------------------------------------- wymagana liczba miejsc (MPZP § 13)
PU = 8400.0          # m² PU wg PN-ISO 9836 (bez powierzchni ruchu i usługowej; spec. rozdz. 12)
PU_GASTRO = 92.0     # m² PU bistro (6 m.p./1000 m²)
PU_PROGRAM = 8582.0  # m² PU programu M.01 (kontrola)
REQ = math.ceil(12 / 1000 * (PU - PU_GASTRO) + 6 / 1000 * PU_GASTRO)
REQ_PROG = math.ceil(12 / 1000 * (PU_PROGRAM - PU_GASTRO) + 6 / 1000 * PU_GASTRO)

# --------------------------------------------------------------------------- konstrukcja
U_COLS = [0.0, 8.10, 16.20, 24.30, 32.40, 40.0]
V_COLS = {0.0: (0.6, 0.6), 8.67: (0.6, 0.35), 16.00: (0.6, 0.6), 22.95: (0.6, 0.35), 29.70: (0.6, 0.6)}  # v: (wymiar u, wymiar v)


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


def street_ramp():
    """Rampa z Wybrzeża (G-K-2, G-I-1): pas 3,50 m przy ścianie pn. segmentu, v −0,35…−3,85 (+ odboje 0,20), u 40,0 → 17,3."""
    return rect_uv(17.30, -4.05, 40.0, -0.15)


def internal_ramp(level):
    """Rampa −1 ↔ −2 w kieszeni wsch. wieży (u 34,6–38,5): jednopasowa 3,50 m, 20 % (WT § 70: garaż dwupoziomowy pod dachem)
    + 2 × 3,0 m po 10 %, dł. 19,25 m; wierzch na −1 przy drodze A2 (v 16,6), stopa na −2 w segmencie (v −2,65).
    Obrys zajęty: −1 – otwór v 2,6…16,6 (dalej strop nad rampą); −2 – v −2,65…16,6 (część pn. o wys. < 2,2 m – technika)."""
    return rect_uv(34.60, 2.60 if level == "-1" else -2.65, 38.50, 16.60)


# ------------------------------------------------------------------- układ stanowisk: rzędy i drogi (współrzędne układów)
# droga: (układ, (a0, a1) wzdłuż osi u lub s, (b0, b1) wzdłuż v lub d)
# rząd:  (układ, (a0, a1), (b0, b1), typ 'P' prostopadłe / 'R' równoległe, trójki w siatce słupów 8,10 m: True/False)
COMMON_AISLES = [("uv", (-9.0, 24.6), (0.6, 6.6)),        # A1 – pd. (pas pod dziedzińcem / wieża), łączy się z A3
                 ("uv", (-6.0, 37.6), (16.6, 22.6)),      # A2 – pn. (przy trzonie A tylko 1,75 m – brak przejazdu)
                 ("sd", (12.2, 52.0), (5.75, 11.75))]     # A3 – skrzydło
COMMON_ROWS = [("uv", (0.3, 24.6), (6.6, 11.6), "P", True),     # R2 – do A1
               ("uv", (0.3, 8.3), (11.6, 16.6), "P", True),     # R3 zach. – do A2
               ("uv", (22.5, 34.4), (11.6, 16.6), "P", True),   # R3 wsch. – do A2
               ("uv", (-6.0, 37.6), (22.6, 27.6), "P", True),   # R4 – do A2 (łuk przycina)
               ("sd", (12.2, 54.0), (0.75, 5.75), "P", False),  # skrzydło, rząd zach. 90°
               ("sd", (12.2, 34.0), (11.75, 14.25), "R", False),  # skrzydło, rząd wsch. równoległy
               ("sd", (34.0, 52.0), (11.75, 16.75), "P", False)]  # skrzydło/wieża – klin przy licu zach. wieży
LEVELS = {
    "-1": {
        "aisles": COMMON_AISLES + [("uv", (16.5, 22.5), (-4.05, 16.6))],   # łącznik wsch. + stopa rampy ulicznej (u 17,3)
        "rows": COMMON_ROWS + [("uv", (-3.3, 16.5), (-4.4, 0.6), "P", True)],  # R1 – pas pod dziedzińcem
        "plant": {   # pomieszczenia na −1 (m² programu) – położenie
            "PPT 40 + szatnie/prysznice personelu 40 + magazyn MDS 20 (M1, przy trzonie C)": rect_sd(1.8, 0.75, 12.0, 8.3),
            "sanitariaty MDS / WC dostępne garażu 30 + zaplecze MDS (pn. od trzonu A)": rect_uv(8.30, 21.0, 16.0, 27.6),
            "centrale P i S 80 + przyłącze wody / woda szara 50 (łuk NE)": rect_uv(30.0, 16.8, 34.4, 27.4),
            "centrale c.d. (łuk NE, przy rampie)": rect_uv(34.6, 16.8, 37.4, 24.0),
            "odpady 24 + pralnia 10 + korytarz dostaw do dźwigu T (segment pd.)": rect_uv(22.6, -6.4, 36.8, -4.25),
            "pom. pod wierzchem rampy ulicznej (h ≥ 2,3 m, magazyn)": rect_uv(33.4, -4.05, 39.3, -0.15),
        },
    },
    "-2": {
        "aisles": COMMON_AISLES + [("uv", (16.5, 22.5), (-4.4, 16.6)),       # łącznik wsch.
                                   ("uv", (16.5, 38.5), (-6.4, -0.4))],      # A4 – segment, do stopy rampy wewn.
        "rows": COMMON_ROWS + [("uv", (-3.3, 16.5), (-4.4, 0.6), "P", True)],
        "plant": {
            "maszynownia GPC 100 + bufory (łuk NE)": rect_uv(30.0, 16.8, 37.4, 27.4),
            "filtrowentylacja ukrycia 30 (przy trzonie A)": rect_uv(8.30, 21.0, 16.0, 25.5),
            "zbiornik deszczówki 50 m³ (segment pd., h 2,0 m)": rect_uv(23.0, -9.0, 36.8, -6.6),
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
    plant = unary_union(list(spec["plant"].values()))
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


def run(png=False):
    res = {}
    cols = columns()
    for lvl, L in (("-1", level_m1()), ("-2", level_m2())):
        I = L.buffer(-DW, join_style=2)
        cores = [c for k, c in CORES.items() if not (lvl == "-2" and k == "C")]
        obst = unary_union(cores + cols + [internal_ramp(lvl)] + ([street_ramp()] if lvl == "-1" else []))
        spec = LEVELS[lvl]
        st, au = layout(I, obst, spec)
        plant_ok = {k: (round(v.intersection(I).area, 1), v.difference(I).area < 0.5,
                        v.intersection(au).area < 0.5) for k, v in spec["plant"].items()}
        res[lvl] = dict(L=L, I=I, stalls=st, aisles=au, cols=cols, obst=obst, plant=plant_ok, spec=spec)
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
        draw(v, fc="#fdb", ec="#a60", lw=0.7)
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
    print(f"wymagane MPZP § 13: 12/1000 × (PU {PU:.0f} − {PU_GASTRO:.0f}) + 6/1000 × {PU_GASTRO:.0f} = "
          f"{12 / 1000 * (PU - PU_GASTRO) + 6 / 1000 * PU_GASTRO:.2f} → {REQ} m.p.; PU programu {PU_PROGRAM:.0f} → {REQ_PROG} m.p.")
    tot = 0
    for lvl, r in res.items():
        n = len(r["stalls"])
        tot += n
        print(f"{lvl}: obrys {r['L'].area:.1f} m², wnętrze {r['I'].area:.1f} m², stanowisk {n}; drogi – części {parts(r['aisles'])}")
        for k, v in r["plant"].items():
            print(f"     technika: {k}: {v[0]} m² (w obrysie: {v[1]}, bez kolizji z drogą: {v[2]})")
    print(f"RAZEM konwencjonalnie: {tot}")
    return res


if __name__ == "__main__":
    main()
