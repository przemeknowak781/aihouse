# -*- coding: utf-8 -*-
"""Elewacja poludniowa W3 + porownanie ze szkicem (wycinek 1770x690 px z oryginalu)."""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly, Circle
from PIL import Image
import model_w3 as M
import draw_common as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
P = M.POZ
C_WALL, C_WALL_B, C_WALL_G, C_SLAB, C_GL, C_LAM = "#f4f2ee", "#e9e6df", "#d8d6d0", "#6f6f6f", "#9fc3e6", "#a67c4e"
BY = {p["id"]: p for p in M.PLYTY}


def rect(ax, x0, x1, z0, z1, fc, ec="black", lw=0.6, z=2, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc, edgecolor=ec, lw=lw, zorder=z, **kw))


def glazing(ax, x0, x1, z0, z1, pods, z=3, frame=0.06, fc=C_GL):
    rect(ax, x0, x1, z0, z1, fc, "black", 0.6, z)
    edges = [x0] + list(pods) + [x1]
    for xm in pods:
        rect(ax, xm - frame, xm + frame, z0, z1, "#3a3a3a", "none", 0, z + 0.1)
    for a, b in zip(edges[:-1], edges[1:]):
        xa = a + 0.2
        ax.plot([xa, xa + 0.45], [z0 + 0.3, z0 + 0.3 + (z1 - z0) * 0.5], color="white", lw=0.7, alpha=0.8, zorder=z + 0.2)


def slab(ax, key, z0=None, z1=None, fc=C_SLAB, zo=6):
    b = BY[key]["poly"].bounds
    zz = BY[key]["z"]
    rect(ax, b[0], b[2], zz[0] if z0 is None else z0, zz[1] if z1 is None else z1, fc, "black", 0.5, zo)


def elevation(ax):
    """Elewacja pd. w ukladzie (x, z); kolejnosc rysowania od najdalszych do najblizszych."""
    xs = np.linspace(-8.5, 25.5, 60)
    zt = np.array([M.teren_wzgl(x, -0.30) for x in xs])
    ax.fill_between(xs, zt, -1.6, color="#e7e1d4", zorder=0.5)
    ax.plot(xs, zt, color="#6b5b3e", lw=1.2, zorder=10)
    # --- G: garaz cofniety (lico y = 4,50), sciana pelna z pnaczami, attyka = linia D
    rect(ax, 12.30, 18.70, 0.0, P["attyka_G"], C_WALL_G, "black", 0.8, 1.2)
    for x in np.arange(12.6, 18.6, 0.5):
        ax.plot([x, x], [0.1, 3.2], color="#7f9a5a", lw=0.5, zorder=1.3)
    slab(ax, "G-okap", 3.35, 3.65, fc="#3d3d3d", zo=1.5)
    rect(ax, 12.30, 17.40, -0.06, 0.0, "#b8a88a", "none", 0, 9)  # patio
    # --- E: parter strefy dziennej
    rect(ax, -0.30, 12.30, 0.0, 2.80, C_WALL, "black", 0.8, 2)
    o = M.otwor("O0-01")
    glazing(ax, o["a"], o["b"], 0.0, o["wys"], o["podz"])
    for s in M.SLUPY:
        rect(ax, s["xy"][0] - 0.07, s["xy"][0] + 0.07, 0.0, 2.75, "#262626", "none", 0, 3.3)
    # --- B: I pietro pelne + boks C (za nim pustka jadalni i pokoj rodzinny)
    rect(ax, -0.30, 12.30, 3.05, 5.70, C_WALL_B, "black", 0.8, 2)
    o = M.otwor("O1-01")
    glazing(ax, o["a"], o["b"], 3.65, 5.15, o["podz"])
    # --- A: II pietro - tlo loggii (cien), przeszklenia pokoi w osi 1', lamele przed licem
    rect(ax, -1.30, 12.30, 5.90, 9.10, "#7b7f84", "black", 0.8, 2)
    for oid in ("O2-01", "O2-02", "O2-03", "O2-04"):
        oo = M.otwor(oid)
        rect(ax, oo["a"], oo["b"], P["P2"] + oo["par"], P["P2"] + oo["par"] + oo["wys"], "#4f6a82", "none", 0, 2.5)
    rect(ax, -1.30, 12.30, 9.40, P["attyka_P2"], "#cfcfcf", "black", 0.5, 1.8)  # attyka (cofnieta nad licem)
    L = M.LAMELE
    x = L["x"][0] + 0.02
    while x < L["x"][1]:
        rect(ax, x, x + L["b"], L["z"][0], L["z"][1], C_LAM, "none", 0, 4)
        x += L["rozstaw"]
    # --- krawedzie plyt i rama C (najblizej)
    slab(ax, "E-okap")                    # E - okap ST1 (-1,80...13,80)
    slab(ax, "C-dol", fc="#3d3d3d")        # D - dolna plyta ramy C
    slab(ax, "C-gora", fc="#3d3d3d")
    for xb in (3.60, 12.70):
        rect(ax, xb, xb + 0.20, 3.65, 5.15, "#3d3d3d", "none", 0, 6)
    slab(ax, "ST2L")                      # plyta loggii pod A
    slab(ax, "ST3-okap")                  # plyta dachu A
    rect(ax, -1.80, 12.30, -0.08, -0.02, "#b8a88a", "none", 0, 9)  # taras


def levels(ax, xpos, items):
    for z, t in items:
        ax.plot([xpos - 0.25, xpos + 0.25], [z, z], color="black", lw=0.6, zorder=12)
        ax.add_patch(MPoly([(xpos, z), (xpos - 0.14, z + 0.2), (xpos + 0.14, z + 0.2)], closed=True, facecolor="black", zorder=12))
        ax.text(xpos + 0.35, z, t, fontsize=6.3, va="center", ha="left", zorder=12)


def band_labels(ax):
    tags = [("A", -2.9, 7.6, "#1f6fb4"), ("B", -1.4, 4.4, "#7b3fa0"), ("C", 13.6, 4.4, "#e07b00"),
            ("D", 19.3, 3.5, "#333333"), ("G", 17.6, 1.6, "#c0392b"), ("E", -2.9, 1.4, "#1c8a4a")]
    for t, x, z, c in tags:
        ax.add_patch(Circle((x, z), 0.42, facecolor="white", edgecolor=c, lw=1.4, zorder=15))
        ax.text(x, z, t, fontsize=9, fontweight="bold", color=c, ha="center", va="center", zorder=16)
    pts = np.array([(0.2, 7.6), (9.0, 7.6), (5.4, 4.4), (16.2, 1.9), (9.0, 1.3), (0.8, 1.3)])
    ax.plot(pts[:, 0], pts[:, 1], color="#f2c200", lw=5, alpha=0.55, zorder=14, solid_capstyle="round", solid_joinstyle="round")


def main():
    fig = plt.figure(figsize=(16.5, 13.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.10)
    ax1 = fig.add_subplot(gs[0])
    img = Image.open(os.path.join(ROOT, "00_wejscie", "szkic_koncepcyjny.jpg")).crop((563, 865, 2333, 1555)).convert("L")
    arr = np.asarray(img)
    sx = 45.8                                  # px/m (brief 1.1: bryla B 500..1050 px = 12,0 m)
    x_left, x_right = -0.30 - 500 / sx, -0.30 + (1770 - 500) / sx
    sz = (640 - 80) / (P["attyka_P2"] + 0.30)  # skala pionowa umowna: teren px640 -> -0,30; gora A px80 -> attyka
    z_top, z_bot = -0.30 + 640 / sz, -0.30 - (690 - 640) / sz
    ax1.imshow(arr, cmap="gray", extent=(x_left, x_right, z_bot, z_top), aspect="auto", zorder=0, alpha=0.85)
    red = dict(fill=False, edgecolor="#d0021b", lw=1.6, zorder=5)
    for (x0, x1, z0, z1) in [(-2.20, 12.60, 9.10, 9.40), (-1.30, 12.30, 5.90, 9.10), (-2.20, 12.60, 5.70, 5.90),
                             (-0.30, 12.30, 3.05, 5.70), (4.50, 11.70, 3.65, 5.15), (3.60, 12.90, 3.45, 5.35),
                             (-1.80, 13.80, 2.75, 3.05), (12.30, 18.70, 0.0, 3.65), (1.00, 11.85, 0.0, 2.75)]:
        ax1.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, **red))
    ax1.set_xlim(-6.5, 23.5); ax1.set_ylim(-1.2, 11.5); ax1.set_aspect("auto")
    ax1.set_title("Szkic inwestora (wycinek, skala pozioma 45,8 px/m wg briefu; pionowa umowna) + obrys W3 (czerwony) — kontrola wierności",
                  fontsize=9.5, loc="left")
    ax1.set_yticks([]); ax1.set_xticks(range(-6, 24, 2)); ax1.tick_params(labelsize=7)
    ax1.set_xlabel("x [m] (0 = oś A; lico zach. bryły B = -0,30)", fontsize=7)
    ax2 = fig.add_subplot(gs[1])
    elevation(ax2)
    band_labels(ax2)
    tg = M.teren_wzgl(18.0, -0.3)
    levels(ax2, 22.2, [(0.0, "±0,00 = 101,65"), (2.80, "+2,80"), (3.15, "+3,15 P1"), (3.65, "+3,65 linia D / attyka G"),
                       (5.70, "+5,70 spód loggii"), (6.30, "+6,30 P2"), (9.10, "+9,10"), (P["attyka_P2"], "+9,85 attyka (maks.)"),
                       (round(tg, 2) - 0.25, f"{D.fmt(tg)} teren przy G")])
    y0 = -1.05
    D.dim_chain_h(ax2, [-2.20, -1.30, -0.30, 1.00, 11.85, 12.30, 18.70], y0, fs=6)
    D.dim_h(ax2, -0.30, 18.70, y0 - 0.45, "19,00 (lico zach. B → pion D; szkic ≈ 19,0)", fs=6.5)
    D.dim_h(ax2, -1.30, 12.30, 10.35, "A = 13,60 (szkic ≈ 13,2)", fs=6.5)
    D.dim_h(ax2, 4.50, 11.70, 5.50, "C = 7,20 (3 kw.; szkic ≈ 7,2)", fs=6.0)
    D.dim_h(ax2, 3.60, 18.70, y0 - 0.95, "linia D 15,10 (szkic ≈ 3,8→19,0)", fs=6.0)
    ax2.text(-2.3, 3.2, "okap E 1,50 ←", fontsize=6, ha="left", va="bottom")
    ax2.text(-2.3, 9.55, "wspornik A 1,00 + płyta 0,90", fontsize=6, ha="left", va="bottom")
    ax2.text(15.5, 0.8, "garaż 2-st. cofnięty 4,8 m (patio poranne przed nim)\nściana pełna z pnączami — dach zielony", fontsize=6.0,
             ha="center", va="center", color="#333", zorder=15)
    ax2.text(5.5, 7.6, "loggia 1,20 m za lamelami", fontsize=6.3, ha="center", color="white", zorder=15,
             bbox=dict(facecolor="#6b4f2a", edgecolor="none", pad=1, alpha=0.8))
    ax2.set_xlim(-6.5, 23.5); ax2.set_ylim(-2.6, 11.0); ax2.set_aspect("equal"); ax2.axis("off")
    ax2.set_title("W3 — ELEWACJA POŁUDNIOWA (ogrodowa), skala 1:100 w oryginale — rytm przesunięć brył zachód–wschód–zachód („S”)",
                  fontsize=10, loc="left", fontweight="bold")
    fig.suptitle("W3 — elewacja południowa vs szkic", fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.012, "A — II piętro w lamelach (loggia 1,20 m za ekranem), wspornik 1,00 m na zach.; B — I piętro pełne; C — boks przeszklony w ramie 1,00 m "
             "(za nim pustka jadalni); D — dolna płyta ramy C → attyka garażu +3,65 do narożnika G; E — przeszklenie parteru 5 kwater (rytm szkicu), okap 1,00 (S) / 1,50 m (W).",
             fontsize=7.3, ha="left")
    fig.subplots_adjust(left=0.03, right=0.99, top=0.95, bottom=0.04)
    fn = os.path.join(OUT, "elewacja_S.png")
    fig.savefig(fn, dpi=150); plt.close(fig)
    print(fn)


if __name__ == "__main__":
    main()
