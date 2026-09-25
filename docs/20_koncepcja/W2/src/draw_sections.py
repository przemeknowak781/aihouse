# -*- coding: utf-8 -*-
"""Przekroje A-A (N-S, x = 6,70, przez biegi 1 schodow i boks C) oraz B-B (W-E, y = 2,00, przez wspornik A i garaz)."""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
import model_w2 as M
import draw_common as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
P = M.POZ
CUT = "#3c3c3c"
INS = "#f3e6b3"
SLAB = "#7a7a7a"
GL = "#9fc3e6"


def R(ax, a0, a1, z0, z1, fc=CUT, ec="black", lw=0.5, z=5, hatch=None):
    ax.add_patch(Rectangle((a0, z0), a1 - a0, z1 - z0, facecolor=fc, edgecolor=ec, lw=lw, zorder=z, hatch=hatch))


def wall_cut(ax, c, z0, z1, outer=None, core=0.18, ins=0.20):
    """Sciana przecieta: rdzen 18 cm na osi c; outer = -1/+1 strona ocieplenia (None = wewn.)."""
    R(ax, c - core / 2, c + core / 2, z0, z1, CUT, "black", 0.4, 6)
    if outer is not None:
        a = c + outer * core / 2
        R(ax, min(a, a + outer * ins), max(a, a + outer * ins), z0, z1, INS, "black", 0.3, 5.5)


def opening(ax, c, z0, z1, w=0.26, glass=True):
    R(ax, c - w / 2, c + w / 2, z0, z1, "white", "white", 0, 7)
    if glass:
        ax.plot([c - 0.03, c - 0.03], [z0, z1], color="#2b6cb0", lw=0.8, zorder=8)
        ax.plot([c + 0.03, c + 0.03], [z0, z1], color="#2b6cb0", lw=0.8, zorder=8)


def slab(ax, a0, a1, z0, z1, z=6):
    R(ax, a0, a1, z0, z1, SLAB, "black", 0.5, z, hatch="////")


def stairs_section(ax, y0, zb, n=9, h=0.175, s=0.28, landing=(7.145, 8.295)):
    pts = [(y0, zb)]
    y, zz = y0, zb
    for k in range(n - 1):
        zz += h
        pts.append((y, zz))
        y += s
        pts.append((y, zz))
    zz += h
    pts.append((y, zz))
    pts.append((landing[1], zz))
    pts.append((landing[1], zz - 0.20))
    pts.append((landing[0], zz - 0.20))
    pts.append((y0 + 0.02, zb - 0.18))
    ax.add_patch(MPoly(pts, closed=True, facecolor="#8c8c8c", edgecolor="black", lw=0.5, zorder=6, hatch="////"))


def levels(ax, a, items, left=False):
    for zz, t in items:
        ax.plot([a - 0.25, a + 0.25], [zz, zz], color="black", lw=0.6, zorder=12)
        ax.add_patch(MPoly([(a, zz), (a - 0.14, zz + 0.2), (a + 0.14, zz + 0.2)], closed=True, facecolor="black", zorder=12))
        ax.text(a + (-0.35 if left else 0.35), zz, t, fontsize=6.2, va="center", ha="right" if left else "left", zorder=12)


def ground(ax, a_arr, z_arr):
    ax.fill_between(a_arr, z_arr, -1.6, color="#e7e1d4", zorder=0.5)
    ax.plot(a_arr, z_arr, color="#6b5b3e", lw=1.1, zorder=9)


def section_AA(ax):
    x = 6.70
    ys = np.linspace(-6.0, 13.5, 40)
    ground(ax, ys, [M.teren_wzgl(x, y) for y in ys])
    # fundamenty
    for c in (0.0, 4.8, 8.4):
        R(ax, c - 0.30, c + 0.30, P["lawa_spod"], P["lawa_spod"] + 0.35, "#9d9d9d", "black", 0.5, 4, hatch="..")
        R(ax, c - 0.12, c + 0.12, P["lawa_spod"] + 0.35, -0.40, "#9d9d9d", "black", 0.5, 4, hatch="..")
    R(ax, -0.30, 8.70, -0.55, -0.40, INS, "black", 0.3, 4)       # XPS
    R(ax, -0.30, 8.70, -0.40, -0.15, "#9d9d9d", "black", 0.4, 4, hatch="..")   # plyta posadzki
    R(ax, -0.30, 8.70, -0.15, 0.0, "#e0d6c4", "black", 0.3, 4)   # warstwy podlogi
    R(ax, -4.30, -0.30, -0.08, -0.02, "#b8a88a", "none", 0, 4)   # taras
    # --- P0: fasada pd. (przeszklenie + belka B1), sciana grzbietowa (otwor biegu 1), sciana pn.
    opening(ax, 0.0, 0.0, 2.75)
    R(ax, -0.125, 0.125, 2.80, 3.85, CUT, "black", 0.4, 6)       # belka B1
    R(ax, -0.33, -0.125, 3.05, 3.85, INS, "black", 0.3, 5.5)
    R(ax, 4.8 - 0.09, 4.8 + 0.09, 2.55, 2.80, CUT, "black", 0.4, 6)   # nadproze nad biegiem
    wall_cut(ax, 8.4, -0.40, 2.80, outer=+1)
    # --- ST1 (otwor klatki y 4,905-8,295)
    slab(ax, -1.30, 4.905, 2.80, 3.00)
    slab(ax, 8.295, 8.70, 2.80, 3.00)
    R(ax, -1.30, -1.20, 2.75, 3.05, SLAB, "black", 0.4, 6)
    # --- rama C (plyta dolna, boks, plyta gorna) + belka B2
    R(ax, -1.30, -0.125, 3.65, 3.85, "#4a4a4a", "black", 0.4, 6)
    opening(ax, 0.0, 3.85, 5.35)
    R(ax, -1.30, -0.125, 5.35, 5.55, "#4a4a4a", "black", 0.4, 6)
    R(ax, -0.125, 0.125, 5.35, 6.15, CUT, "black", 0.4, 6)       # belka B2
    R(ax, -0.33, -0.125, 5.55, 6.15, INS, "black", 0.3, 5.5)
    R(ax, 4.8 - 0.09, 4.8 + 0.09, 5.70, 5.95, CUT, "black", 0.4, 6)
    wall_cut(ax, 8.4, 3.00, 5.95, outer=+1)
    # --- ST2
    slab(ax, -1.30, 4.905, 5.95, 6.15)
    slab(ax, 8.295, 8.70, 5.95, 6.15)
    R(ax, -1.30, -1.20, 5.95, 6.25, SLAB, "black", 0.4, 6)
    # --- P2: sciana pd. (pelna, x=6,7 = pom. techn.), lamele, scianka 2.725, os 3 (zamknieta nad biegiem 1), sciana pn. z oknem
    wall_cut(ax, 0.0, 6.15, 9.10, outer=-1)
    R(ax, -0.47, -0.43, 6.15, 9.10, "#a67c4e", "none", 0, 6)
    R(ax, 2.725 - 0.075, 2.725 + 0.075, 6.15 + 2.05 + 0.15, 9.10, "#9a9a9a", "black", 0.3, 6)
    wall_cut(ax, 4.8, 6.15, 9.10, outer=None)
    wall_cut(ax, 8.4, 6.15, 9.10, outer=+1)
    opening(ax, 8.4 + 0.1, 6.30 + 0.90, 6.30 + 2.40, w=0.45)
    # --- ST3 + dach
    slab(ax, -1.30, 5.20, 9.10, 9.32)
    slab(ax, 8.10, 8.70, 9.10, 9.32)
    R(ax, -1.30, -1.20, 9.10, 9.42, SLAB, "black", 0.4, 6)
    R(ax, -0.30, 5.20, 9.32, 9.60, INS, "black", 0.3, 5)
    R(ax, 8.10, 8.70, 9.32, 9.60, INS, "black", 0.3, 5)
    R(ax, 5.05, 5.20, 9.32, 9.95, CUT, "black", 0.3, 6)
    R(ax, 8.10, 8.25, 9.32, 9.95, CUT, "black", 0.3, 6)
    ax.plot([5.05, 8.25], [9.95, 9.95], color="#2b6cb0", lw=1.4, zorder=7)
    R(ax, -0.30, -0.10, 9.32, 9.80, "#bdbdbd", "black", 0.3, 5)
    R(ax, 8.50, 8.70, 9.32, 9.80, "#bdbdbd", "black", 0.3, 5)
    # --- schody (bieg 1 w pasie W: P0->spocznik, P1->spocznik)
    for zb in (0.0, 3.15):
        stairs_section(ax, 4.905, zb)
    # przeswit
    ax.annotate("", xy=(5.75, 3.15 + 0.175 * 3 - 0.25), xytext=(5.75, 0.175 * 4),
                arrowprops=dict(arrowstyle="<->", lw=0.6, color="#b00020"), zorder=12)
    ax.text(5.85, 2.0, "prześwit\n≈2,75 m\n(≥2,00)", fontsize=5.8, color="#b00020", zorder=12)
    # opisy pomieszczen
    for (y, z, t) in [(2.3, 1.2, "0.06 jadalnia\nh = 2,80"), (6.8, 1.0, "bieg 1\n9 × 17,5/28"), (2.3, 4.5, "1.02 pokój rodzinny\n(boks C) h = 2,80"),
                      (1.3, 7.6, "2.06 pom. techn.\n(reku + wyłaz)"), (3.75, 7.6, "2.01 hol"), (6.6, 7.7, "klatka\n(nadbudowa)"),
                      (-0.9, 4.6, "rama C\n1,00"), (-2.6, 8.0, "lamele"), (6.6, 4.3, "bieg 1\nP1→P2")]:
        ax.text(y, z, t, fontsize=6.2, ha="center", va="center", zorder=13, bbox=dict(facecolor="white", edgecolor="none", pad=0.4, alpha=0.8))
    levels(ax, 10.3, [(0.0, "±0,00 P0"), (2.80, "+2,80"), (3.15, "+3,15 P1"), (1.575, "+1,575 spocznik"), (4.725, "+4,725 spocznik"),
                      (5.95, "+5,95"), (6.30, "+6,30 P2"), (9.10, "+9,10"), (9.60, "+9,60 wierzch dachu (WT §6)"), (9.80, "+9,80 attyka"),
                      (P["lawa_spod"], "−1,10 spód ławy")])
    levels(ax, -4.9, [(3.65, "+3,65 / +3,85 linia D"), (5.35, "+5,35"), (M.teren_wzgl(x, -1.3), f"{D.fmt(M.teren_wzgl(x, -1.3))} teren")], left=True)
    D.dim_chain_h(ax, [-1.30, 0.0, 4.8, 8.4, 8.70], -1.95, fs=6)
    for c, n in ((0.0, "1"), (4.8, "3"), (8.4, "4")):
        ax.plot([c, c], [-1.7, 10.5], color="#c04040", lw=0.3, ls=(0, (8, 2, 1, 2)), zorder=1)
        ax.text(c, 10.6, n, fontsize=7, color="#c04040", ha="center", va="bottom",
                bbox=dict(boxstyle="circle,pad=0.25", facecolor="white", edgecolor="#c04040", lw=0.6))
    ax.text(-5.8, 11.25, "PRZEKRÓJ A-A (x = 6,70; widok na zachód)   S ←  → N", fontsize=9.5, fontweight="bold", ha="left")
    ax.set_xlim(-6.2, 13.8)
    ax.set_ylim(-2.4, 11.8)
    ax.set_aspect("equal")
    ax.axis("off")


def section_BB(ax):
    y = 2.0
    xs = np.linspace(-7.5, 24.4, 40)
    ground(ax, xs, [M.teren_wzgl(xx, y) for xx in xs])
    for c in (0.0, 12.0, 18.4):
        R(ax, c - 0.30, c + 0.30, P["lawa_spod"], P["lawa_spod"] + 0.35, "#9d9d9d", "black", 0.5, 4, hatch="..")
        R(ax, c - 0.12, c + 0.12, P["lawa_spod"] + 0.35, -0.40, "#9d9d9d", "black", 0.5, 4, hatch="..")
    R(ax, -0.30, 18.70, -0.55, -0.40, INS, "black", 0.3, 4)
    R(ax, -0.30, 18.70, -0.40, -0.15, "#9d9d9d", "black", 0.4, 4, hatch="..")
    R(ax, -0.30, 18.70, -0.15, 0.0, "#e0d6c4", "black", 0.3, 4)
    R(ax, -1.80, -0.30, -0.08, -0.02, "#b8a88a", "none", 0, 4)
    # --- P0
    wall_cut(ax, 0.0, -0.40, 2.80, outer=-1)
    opening(ax, -0.05, 0.45, 2.60, w=0.45)
    wall_cut(ax, 12.0, -0.40, 2.80)
    R(ax, 14.275 - 0.075, 14.275 + 0.075, 0.0, 2.76, "#9a9a9a", "black", 0.3, 6)
    R(ax, 15.475 - 0.075, 15.475 + 0.075, 0.0, 2.76, "#9a9a9a", "black", 0.3, 6)
    wall_cut(ax, 18.4, -0.40, 2.76, outer=+1)
    # --- ST1 + okap zach. + strop garazu (24 cm) + dach zielony + attyka
    slab(ax, -1.80, 12.0, 2.80, 3.00)
    R(ax, -1.80, -1.70, 2.75, 3.05, SLAB, "black", 0.4, 6)
    slab(ax, 12.0, 18.70, 2.76, 3.00)
    R(ax, 12.09, 18.40, 3.00, 3.22, INS, "black", 0.3, 5)
    R(ax, 12.09, 18.40, 3.22, 3.35, "#9ccc65", "black", 0.3, 5)
    R(ax, 18.40, 18.70, 3.00, 3.85, INS, "black", 0.3, 5)
    R(ax, 18.31, 18.49, 3.00, 3.65, CUT, "black", 0.3, 6)
    ax.text(15.3, 3.55, "dach zielony ekstensywny (nieużytkowy), spadek 2% → wpust", fontsize=5.8, ha="center", va="bottom", zorder=13)
    # --- P1
    wall_cut(ax, 0.0, 3.00, 5.95, outer=-1)
    opening(ax, -0.05, 3.15 + 0.85, 3.15 + 2.35, w=0.45)
    R(ax, 3.875 - 0.075, 3.875 + 0.075, 3.15, 5.95, "#9a9a9a", "black", 0.3, 6)
    wall_cut(ax, 12.0, 3.00, 5.95, outer=+1)
    opening(ax, 12.05, 3.15 + 0.85, 3.15 + 2.35, w=0.45)
    # --- ST2 (wspornik 1,00 + plyta 1,10)
    slab(ax, -2.40, 12.30, 5.95, 6.15)
    R(ax, -2.40, -2.30, 5.95, 6.25, SLAB, "black", 0.4, 6)
    # --- P2
    R(ax, -1.30, -0.895, 6.15, 9.10, "#b0a58c", "black", 0.4, 6, hatch="////")
    opening(ax, -1.0, 6.30 + 0.60, 6.30 + 2.60, w=0.65)
    R(ax, 3.675 - 0.075, 3.675 + 0.075, 6.15, 9.10, "#9a9a9a", "black", 0.3, 6)
    R(ax, 6.125 - 0.075, 6.125 + 0.075, 6.15, 9.10, "#9a9a9a", "black", 0.3, 6)
    R(ax, 8.395 - 0.075, 8.395 + 0.075, 6.15, 9.10, "#9a9a9a", "black", 0.3, 6)
    wall_cut(ax, 12.0, 6.15, 9.10, outer=+1)
    opening(ax, 12.05, 6.30 + 0.85, 6.30 + 2.60, w=0.45)
    # sciana-tarcza zelbetowa (widok, os 3) x -1,0..2,0
    R(ax, -1.30, 2.0, 6.15, 9.10, "none", "#b00020", 0.8, 3, hatch="\\\\")
    ax.text(0.9, 8.55, "ściana-tarcza ŻB (oś 3, widok)\nprzenosi wspornik bryły A", fontsize=5.6, color="#b00020", ha="center", zorder=13,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.3, alpha=0.85))
    # --- ST3 + dach P2
    slab(ax, -2.40, 12.60, 9.10, 9.32)
    R(ax, -2.40, -2.30, 9.10, 9.42, SLAB, "black", 0.4, 6)
    R(ax, 12.50, 12.60, 9.10, 9.42, SLAB, "black", 0.4, 6)
    R(ax, -1.30, 12.30, 9.32, 9.60, INS, "black", 0.3, 5)
    R(ax, -1.30, -1.10, 9.60, 9.80, "#bdbdbd", "black", 0.3, 5)
    R(ax, 12.10, 12.30, 9.60, 9.80, "#bdbdbd", "black", 0.3, 5)
    for k in range(6):
        x0 = 1.0 + k * 1.75
        ax.add_patch(MPoly([(x0, 9.62), (x0 + 1.6, 9.62), (x0 + 1.6, 9.72), (x0, 9.78)], closed=True, facecolor="#1f3b63", edgecolor="none", zorder=6))
    ax.text(5.8, 9.98, "PV (E-W, niskie stelaże ≤ +9,80)", fontsize=5.8, ha="center", zorder=13)
    for (xx, z, t) in [(5.9, 1.4, "0.06 salon + jadalnia + kuchnia  h = 2,80"), (13.2, 1.4, "0.10 przedsionek"), (14.87, 0.6, "0.11"),
                       (16.9, 1.4, "0.12 pom. techn."), (1.9, 4.5, "1.03 pokój dz. 1"), (8.0, 4.5, "1.02 pokój rodzinny"),
                       (1.2, 7.9, "2.02 sypialnia"), (4.9, 7.9, "2.03 garderoba"), (7.26, 7.9, "2.06"), (10.2, 7.9, "2.05 gabinet"),
                       (-1.9, 7.6, "wspornik\n1,00")]:
        ax.text(xx, z, t, fontsize=6.2, ha="center", va="center", zorder=13, bbox=dict(facecolor="white", edgecolor="none", pad=0.4, alpha=0.8))
    levels(ax, 21.0, [(0.0, "±0,00"), (2.76, "+2,76 spód stropu garażu"), (3.35, "+3,35"), (3.85, "+3,85 attyka G (linia D)"),
                      (5.95, "+5,95"), (6.30, "+6,30"), (9.10, "+9,10"), (9.60, "+9,60"), (9.80, "+9,80")])
    D.dim_chain_h(ax, [-2.40, -1.30, -0.30, 0.0, 12.0, 18.4, 18.70], -1.95, fs=6)
    for c, n in ((-1.0, "A'"), (0.0, "A"), (3.875, "B"), (6.095, "C"), (8.425, "D"), (12.0, "E"), (18.4, "F")):
        ax.plot([c, c], [-1.7, 10.5], color="#c04040", lw=0.3, ls=(0, (8, 2, 1, 2)), zorder=1)
        ax.text(c, 10.6, n, fontsize=7, color="#c04040", ha="center", va="bottom",
                bbox=dict(boxstyle="circle,pad=0.25", facecolor="white", edgecolor="#c04040", lw=0.6))
    ax.text(-7.3, 11.25, "PRZEKRÓJ B-B (y = 2,00; widok na północ)   W ←  → E", fontsize=9.5, fontweight="bold", ha="left")
    ax.set_xlim(-7.6, 25.0)
    ax.set_ylim(-2.4, 11.8)
    ax.set_aspect("equal")
    ax.axis("off")


def main():
    fig = plt.figure(figsize=(16.5, 15.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.06)
    a1 = fig.add_subplot(gs[0])
    a2 = fig.add_subplot(gs[1])
    section_AA(a1)
    section_BB(a2)
    fig.suptitle("W2 — PRZEKROJE A-A i B-B (rzędne względem ±0,00 = 101,65 m n.p.m.)", fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.012, "Kondygnacje 3 × 3,15 m: warstwy podłogi 0,15 + strop ŻB 0,20 + h w świetle 2,80 m. Stropodach P2: płyta 0,22 + PIR ~0,24 + membrana/balast. "
             "Okapy i rama C z łącznikami termoizolacyjnymi. Posadowienie: ławy ŻB 60×35 cm, spód −1,10 (h_z = 0,8 m pod terenem ~−0,30).",
             fontsize=7.5, ha="left")
    fig.subplots_adjust(left=0.02, right=0.99, top=0.965, bottom=0.03)
    fn = os.path.join(OUT, "przekroj.png")
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(fn)


if __name__ == "__main__":
    main()
