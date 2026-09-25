# -*- coding: utf-8 -*-
"""Elewacja poludniowa W2 + porownanie ze szkicem (wycinek 1770x690 px z oryginalu)."""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly, Circle
from PIL import Image
import model_w2 as M
import draw_common as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
P = M.POZ

C_WALL = "#f4f2ee"
C_WALL_B = "#e9e6df"
C_WALL_G = "#d8d6d0"
C_SLAB = "#6f6f6f"
C_GL = "#9fc3e6"
C_LAM = "#a67c4e"


def rect(ax, x0, x1, z0, z1, fc, ec="black", lw=0.6, z=2, **kw):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc, edgecolor=ec, lw=lw, zorder=z, **kw))


def glazing(ax, x0, x1, z0, z1, n, z=3, frame=0.06):
    rect(ax, x0, x1, z0, z1, C_GL, "black", 0.6, z)
    step = (x1 - x0) / n
    for k in range(1, n):
        xm = x0 + k * step
        rect(ax, xm - frame, xm + frame, z0, z1, "#3a3a3a", "none", 0, z + 0.1)
    for k in range(n):  # refleks
        xa = x0 + k * step + 0.25
        ax.plot([xa, xa + 0.5], [z0 + 0.3, z0 + 0.3 + (z1 - z0) * 0.5], color="white", lw=0.7, alpha=0.8, zorder=z + 0.2)


def terrain_line(x):
    return np.array([M.teren_wzgl(xx, -0.30) for xx in x])


def elevation(ax, detail=True, color_override=None):
    """Rysuje elewacje pd. w ukladzie (x, z). Kolejnosc: od najdalszych do najblizszych."""
    # teren i grunt
    xs = np.linspace(-8.5, 25.5, 60)
    zt = terrain_line(xs)
    ax.fill_between(xs, zt, -1.6, color="#e7e1d4", zorder=0.5)
    ax.plot(xs, zt, color="#6b5b3e", lw=1.2, zorder=10)
    # attyka P2 w licu sciany (cofnieta)
    rect(ax, -1.30, 12.30, 9.42, P["attyka_P2"], "#cfcfcf", "black", 0.5, 1.5)
    # --- bryla G + strefa gosp. (lico y=-0.30)
    rect(ax, 11.70, 18.70, 0.0, P["attyka_G"], C_WALL_G, "black", 0.8, 2)
    # drzwi gospodarcze przedsionka (przeszklone) - poczatek pelnej sciany G przesuniety na x = 13,15
    o = M.otwor("O0-19")
    glazing(ax, o["a"], o["b"], 0.0, o["wys"], 1, z=2.6)
    # --- parter czesci mieszkalnej
    rect(ax, -0.30, 12.30, 0.0, 2.80, C_WALL, "black", 0.8, 2)
    glazing(ax, 0.30, 11.70, 0.0, 2.75, 5, z=3)
    for s in M.SLUPY:
        x = s["xy"][0]
        rect(ax, x - 0.07, x + 0.07, 0.0, 2.75, "#262626", "none", 0, 3.3)
    # --- bryla B
    rect(ax, -0.30, 12.30, 3.00, 5.95, C_WALL_B, "black", 0.8, 2)
    glazing(ax, 4.10, 11.10, 3.85, 5.35, 3, z=3)
    # --- bryla A
    rect(ax, -1.30, 12.30, 6.15, 9.10, "#d9d4c8", "black", 0.8, 2)
    for o in ("O2-01", "O2-02", "O2-03"):
        oo = M.otwor(o)
        rect(ax, oo["a"], oo["b"], P["P2"] + oo["par"], P["P2"] + oo["par"] + oo["wys"], "#6d879e", "none", 0, 2.5)
    # lamele (przed licem)
    L = M.LAMELE
    x = L["x"][0] + 0.02
    while x < L["x"][1]:
        rect(ax, x, x + L["b"], L["z"][0], L["z"][1], C_LAM, "none", 0, 4)
        x += L["rozstaw"]
    rect(ax, L["x"][0], L["x"][1], L["z"][0], L["z"][0] + 0.06, "#6b4f2a", "none", 0, 4.1)
    rect(ax, L["x"][0], L["x"][1], L["z"][1] - 0.06, L["z"][1], "#6b4f2a", "none", 0, 4.1)
    # --- krawedzie plyt (y=-1.30, najblizej)
    rect(ax, -1.80, 12.60, 2.75, 3.05, C_SLAB, "black", 0.5, 6)          # E - okap ST1
    rect(ax, 3.60, 12.60, 3.65, 3.85, "#3d3d3d", "black", 0.5, 6)       # D - plyta dolna ramy C
    rect(ax, 3.60, 12.60, 5.35, 5.55, "#3d3d3d", "black", 0.5, 6)       # rama C - gora
    rect(ax, 3.60, 3.75, 3.85, 5.35, "#3d3d3d", "none", 0, 6)            # rama C - boki
    rect(ax, 12.45, 12.60, 3.85, 5.35, "#3d3d3d", "none", 0, 6)
    rect(ax, 11.70, 18.70, 3.65, 3.85, "#3d3d3d", "black", 0.5, 5.5)      # attyka garazu = linia D
    rect(ax, -2.40, 12.60, 5.95, 6.25, C_SLAB, "black", 0.5, 6)          # ST2
    rect(ax, -2.40, 12.60, 9.10, 9.42, C_SLAB, "black", 0.5, 6)          # ST3
    # taras
    rect(ax, -1.80, 11.70, -0.08, -0.02, "#b8a88a", "none", 0, 9)
    # jednostka zewn. PC
    rect(ax, 19.10, 20.10, M.teren_wzgl(19.6, 1.0) + 0.10, M.teren_wzgl(19.6, 1.0) + 1.00, "#dcdcdc", "black", 0.5, 2)
    # stopien przed pasem - opaska
    return


def levels(ax, xpos, items):
    for z, t in items:
        ax.plot([xpos - 0.25, xpos + 0.25], [z, z], color="black", lw=0.6, zorder=12)
        ax.add_patch(MPoly([(xpos, z), (xpos - 0.14, z + 0.2), (xpos + 0.14, z + 0.2)], closed=True, facecolor="black", zorder=12))
        ax.text(xpos + 0.35, z, t, fontsize=6.3, va="center", ha="left", zorder=12)


def band_labels(ax):
    tags = [("A", -2.9, 7.6, "#1f6fb4"), ("B", -1.4, 4.4, "#7b3fa0"), ("C", 13.35, 4.6, "#e07b00"),
            ("D", 17.9, 4.45, "#333333"), ("G", 15.2, 1.8, "#c0392b"), ("E", -2.9, 1.4, "#1c8a4a")]
    for t, x, z, c in tags:
        ax.add_patch(Circle((x, z), 0.42, facecolor="white", edgecolor=c, lw=1.4, zorder=15))
        ax.text(x, z, t, fontsize=9, fontweight="bold", color=c, ha="center", va="center", zorder=16)
    # sylweta S (rytm przesuniec zachod-wschod-zachod)
    pts = np.array([(0.2, 7.6), (9.0, 7.6), (5.2, 4.6), (16.2, 2.2), (9.0, 1.3), (0.8, 1.3)])
    ax.plot(pts[:, 0], pts[:, 1], color="#f2c200", lw=5, alpha=0.55, zorder=14, solid_capstyle="round", solid_joinstyle="round")


def main():
    fig = plt.figure(figsize=(16.5, 13.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.10)
    # ---------- 1: szkic z nalozonym obrysem W2
    ax1 = fig.add_subplot(gs[0])
    img = Image.open(os.path.join(ROOT, "00_wejscie", "szkic_koncepcyjny.jpg")).crop((563, 865, 2333, 1555)).convert("L")
    arr = np.asarray(img)
    sx = 45.8                                  # px/m (brief 1.1: bryla B 500..1050 px = 12,0 m)
    x_left = -0.30 - 500 / sx                  # lico zach. bryly B (px 500) = x -0,30
    x_right = -0.30 + (1770 - 500) / sx
    sz = (640 - 80) / (P["attyka_P2"] + 0.30)  # skala pionowa (umowna): teren px640 -> -0,30; gora A px80 -> +9,80
    z_top = -0.30 + 640 / sz
    z_bot = -0.30 - (690 - 640) / sz
    ax1.imshow(arr, cmap="gray", extent=(x_left, x_right, z_bot, z_top), aspect="auto", zorder=0, alpha=0.85)
    # obrys W2 (czerwony)
    red = dict(fill=False, edgecolor="#d0021b", lw=1.6, zorder=5)
    for (x0, x1, z0, z1) in [(-2.40, 12.60, 9.10, 9.42), (-1.30, 12.30, 6.15, 9.10), (-2.40, 12.60, 5.95, 6.25),
                             (-0.30, 12.30, 3.00, 5.95), (4.10, 11.10, 3.85, 5.35), (3.60, 12.60, 3.65, 5.55),
                             (-1.80, 12.60, 2.75, 3.05), (13.15, 18.70, 0.0, 3.85), (0.30, 11.70, 0.0, 2.75)]:
        ax1.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, **red))
    ax1.set_xlim(-6.5, 23.5)
    ax1.set_ylim(-1.2, 11.5)
    ax1.set_aspect("auto")
    ax1.set_title("Szkic inwestora (wycinek, skala pozioma 45,8 px/m wg briefu; pionowa umowna) + obrys W2 (czerwony) — kontrola wierności",
                  fontsize=9.5, loc="left")
    ax1.set_yticks([])
    ax1.set_xticks(range(-6, 24, 2))
    ax1.tick_params(labelsize=7)
    ax1.set_xlabel("x [m] (0 = oś A; lico zach. bryły B = -0,30)", fontsize=7)
    # ---------- 2: elewacja W2
    ax2 = fig.add_subplot(gs[1])
    elevation(ax2)
    band_labels(ax2)
    levels(ax2, 22.2, [(0.0, "±0,00 = 101,65"), (2.80, "+2,80"), (3.15, "+3,15 P1"), (3.85, "+3,85 linia D / attyka G"),
                       (5.95, "+5,95"), (6.30, "+6,30 P2"), (9.10, "+9,10"), (P["attyka_P2"], "+9,80 attyka (maks.)"),
                       (round(M.teren_wzgl(18.0, -0.3), 2) - 0.25, f"{D.fmt(M.teren_wzgl(18.0, -0.3))} teren przy G")])
    # wymiary poziome
    y0 = -1.05
    D.dim_chain_h(ax2, [-2.40, -1.30, -0.30, 0.30, 11.70, 12.30, 18.70], y0, fs=6)
    D.dim_h(ax2, -0.30, 18.70, y0 - 0.45, "19,00 (lico zach. B → pion D; szkic ≈ 19,0)", fs=6.5)
    D.dim_h(ax2, -1.30, 12.30, 10.35, "A = 13,60 (szkic ≈ 13,2)", fs=6.5)
    D.dim_h(ax2, 4.10, 11.10, 5.62, "C = 7,00 (3 kw.)", fs=6.0)
    D.dim_h(ax2, 3.60, 18.70, y0 - 0.95, "linia D 15,10 (szkic ≈ 3,8→19,0)", fs=6.0)
    D.dim_h(ax2, 13.15, 18.70, 1.2, "G 5,55 (szkic ≈ 5,8)", fs=6.0)
    ax2.text(-2.3, 3.2, "okap E 1,50 ←", fontsize=6, ha="left", va="bottom")
    ax2.text(-2.3, 9.55, "wspornik A 1,00 + płyta 1,10", fontsize=6, ha="left", va="bottom")
    ax2.text(15.9, 0.55, "garaż 2-st. (brama od pn.)\nściana pełna — dach zielony", fontsize=6.3, ha="center", va="center", color="#444", zorder=15)
    ax2.text(19.6, 1.35, "PC", fontsize=6, ha="center", zorder=15)
    ax2.set_xlim(-6.5, 23.5)
    ax2.set_ylim(-2.6, 11.0)
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_title("W2 — ELEWACJA POŁUDNIOWA (ogrodowa), skala 1:100 w oryginale — rytm przesunięć brył zachód–wschód–zachód („S”)",
                  fontsize=10, loc="left", fontweight="bold")
    fig.suptitle("W2 — elewacja południowa vs szkic", fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.985)
    fig.text(0.02, 0.012, "A — II piętro w lamelach, wspornik 1,00 m na zachód; B — I piętro pełne; C — boks przeszklony w ramie wysuniętej 1,00 m; "
             "D — dolna płyta ramy C przechodząca w attykę garażu (+3,85) do narożnika G; E — przeszklenie parteru 5 kwater z okapem 1,00 m (pd.) / 1,50 m (zach.).",
             fontsize=7.5, ha="left")
    fig.subplots_adjust(left=0.03, right=0.99, top=0.95, bottom=0.04)
    fn = os.path.join(OUT, "elewacja_S.png")
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    print(fn)


if __name__ == "__main__":
    main()
