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
    "T": rect_uv(21.30, -7.30, 23.50, -4.05),   # szyb dźwigu T 2 000 kg (P-I5: z trzonu B do segmentu), przystanki −1…4
}
CORES_M2 = {k: v for k, v in CORES.items() if k != "C"}


def street_ramp():
    """Rampa z Wybrzeża (G-K-2, G-I-1): pas 3,50 m przy ścianie pn. segmentu, v −0,35…−3,85 (+ odboje), u 40,0 → 17,3."""
    return rect_uv(17.30, -4.05, 40.0, -0.15)


def internal_ramp():
    """Rampa −1 ↔ −2 (jednopasowa 3,50 m, 18 % + 2 × 3,0 m po 9 %, dł. 21,1 m): pas zach. wieży u 0,30–4,20, v 1,0…22,1."""
    return rect_uv(0.30, 1.00, 4.20, 22.10)


# ------------------------------------------------------------------- układ stanowisk: rzędy i drogi (współrzędne układów)
# rząd: (układ, (a0, a1) wzdłuż, (b0, b1) w poprzek, typ 'P' prostopadłe / 'R' równoległe, siatka trójek True/False)
LEVELS = {
    "-1": {
        "aisles": [("uv", (-3.3, 24.6), (0.6, 6.6)),        # A1 pd. (pas pod dziedzińcem + wieża)
                   ("uv", (16.5, 22.5), (6.6, 16.6)),       # łącznik wsch. przy trzonie A
                   ("uv", (4.2, 37.6), (16.6, 22.6)),       # A2 pn. (przerwa przy trzonie A – patrz spójność)
                   ("uv", (11.0, 17.3), (-4.05, 0.6)),      # strefa wjazdu z rampy ulicznej
                   ("sd", (12.2, 52.0), (5.75, 11.75))],    # A3 skrzydło
        "rows": [("uv", (-3.3, 11.0), (-4.4, 0.6), "P", True),
                 ("uv", (4.2, 24.6), (6.6, 11.6), "P", True),
                 ("uv", (22.5, 37.6), (11.6, 16.6), "P", True),
                 ("uv", (4.2, 8.3), (11.6, 16.6), "P", True),
                 ("uv", (4.2, 37.6), (22.6, 27.6), "P", True),
                 ("sd", (12.2, 54.0), (0.75, 5.75), "P", False),
                 ("sd", (12.2, 34.0), (11.75, 14.25), "R", False)],
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


def layout(level, interior, obstacles, spec):
    aisles = [to_poly(f, a, b) for f, a, b in spec["aisles"]]
    aisle_u = unary_union([x.intersection(interior).difference(obstacles) for x in aisles])
    stalls = []
    for f, a, b, typ, grid in spec["rows"]:
        for st in stalls_in_row(f, a, b, typ, grid):
            if st.difference(interior).area > 0.02 or st.intersection(obstacles).area > 0.02:
                continue
            if any(st.intersection(s).area > 0.01 for s in stalls):
                continue
            front = st.buffer(1.0, join_style=2).intersection(aisle_u).area
            if front < 1.0:
                continue
            stalls.append(st)
    return stalls, aisle_u


def main():
    png = "--png" in sys.argv
    L1 = level_m1()
    I1 = L1.buffer(-DW, join_style=2)
    cols = columns()
    obst1 = unary_union(list(CORES.values()) + cols + [street_ramp(), internal_ramp()])
    st1, au1 = layout("-1", I1, obst1, LEVELS["-1"])
    print(f"wymagane MPZP § 13: PU {PU:.0f} → {REQ} m.p.; PU programu {PU_PROGRAM:.0f} → {REQ_PROG} m.p.")
    print(f"−1: obrys {L1.area:.1f} m², wnętrze {I1.area:.1f} m², stanowisk {len(st1)}; drogi części: "
          f"{1 if au1.geom_type == 'Polygon' else len(au1.geoms)}")
    if png:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(14, 14))

        def draw(g, **kw):
            gs = [g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))
            for p in gs:
                if p.geom_type != "Polygon":
                    continue
                x, y = p.exterior.xy
                ax.fill(x, y, **kw)
        draw(L1, fc="none", ec="k", lw=1.5)
        draw(I1, fc="#f4f4f4", ec="#999", lw=0.5)
        draw(au1, fc="#cde", ec="none")
        for c in CORES.values():
            draw(c, fc="#888", ec="k")
        for c in cols:
            draw(c, fc="r", ec="r")
        draw(street_ramp(), fc="#fc8", ec="k")
        draw(internal_ramp(), fc="#fd9", ec="k")
        for s in st1:
            draw(s, fc="#9c9", ec="g", lw=0.5)
        draw(W, fc="none", ec="b", lw=0.5, ls="--")
        draw(M, fc="none", ec="b", lw=0.5, ls="--")
        ax.set_aspect("equal")
        ax.set_title(f"−1 v1.1: {len(st1)} stanowisk")
        fig.savefig("/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/park_m1.png", dpi=70)


if __name__ == "__main__":
    main()
