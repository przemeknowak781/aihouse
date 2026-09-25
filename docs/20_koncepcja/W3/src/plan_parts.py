# -*- coding: utf-8 -*-
"""W3 - elementy rzutow: schody, wyposazenie, dachy nizsze, plyty wysuniete."""
from matplotlib.patches import Rectangle
from shapely.geometry import box
import model_w3 as M
import draw_common as D

S = M.SCHODY


def stairs(ax, kond):
    xE0, xE1 = S["bieg_E"]["x"]
    xW0, xW1 = S["bieg_W"]["x"]
    y0 = S["bieg_E"]["y0"]
    yl0, yl1 = S["spocznik"]["y"]
    cut = 5
    ysE = [y0 + S["s"] * k for k in range(9)]
    ysW = [yl0 - S["s"] * k for k in range(9)]

    def tr(x0, x1, ys, st):
        for y in ys:
            ax.plot([x0, x1], [y, y], color="black", lw=0.5, ls=st, zorder=4)

    def arrow(x, ya, yb, t):
        ax.annotate("", xy=(x, yb), xytext=(x, ya), arrowprops=dict(arrowstyle="->", lw=0.9), zorder=6)
        ax.text(x, ya + (0.25 if yb > ya else -0.25), t, fontsize=6, ha="center", va="center", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.4))
    ax.plot([xW1 + 0.07, xW1 + 0.07], [y0, yl0], color=D.C_GLASS, lw=0.8, zorder=4)  # oko - balustrada szklana
    if kond in ("P0", "P1"):
        tr(xE0, xE1, ysE[:cut + 1], "-")
        tr(xE0, xE1, ysE[cut + 1:], (0, (3, 2)))
        ax.plot([xE0, xE1], [ysE[cut] + 0.10, ysE[cut] + 0.30], color="black", lw=0.8, zorder=5)
        arrow((xE0 + xE1) / 2, y0 + 0.05, ysE[cut] + 0.05, "G")
        ax.add_patch(Rectangle((xW0, yl0), xE1 - xW0, yl1 - yl0, facecolor="none", edgecolor="black", lw=0.5, ls=(0, (3, 2)), zorder=4))
        ax.text(xE1 - 0.05, yl1 - 0.05, f"spocznik +{D.fmt(M.POZ[kond] + 1.575, 3)}", fontsize=4.6, ha="right", va="top", zorder=6)
    if kond == "P0":
        tr(xW0, xW1, ysW, (0, (3, 2)))
        ax.text((xW0 + xW1) / 2, 6.3, "bieg 2\n(nad)", fontsize=5, ha="center", va="center", color="#555", zorder=6)
    if kond in ("P1", "P2"):
        tr(xW0, xW1, ysW, "-")
        arrow((xW0 + xW1) / 2, yl0 - 0.2, y0 + 0.05, "D" if kond == "P1" else "")
    if kond == "P2":
        tr(xE0, xE1, ysE, "-")
        ax.text((xE0 + xE1) / 2, 6.5, "bieg 3\n(poniżej)", fontsize=5, ha="center", va="center", color="#555", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.3))
        ax.add_patch(Rectangle((xW0, yl0), xE1 - xW0, yl1 - yl0, facecolor="none", edgecolor="black", lw=0.5, zorder=4))
        ax.text((xW0 + xE1) / 2, (yl0 + yl1) / 2, "spocznik +4,725 (poniżej)", fontsize=5, ha="center", va="center", zorder=6)
        ax.plot([xE0 - 0.05, xE1], [5.40, 5.40], color=D.C_GLASS, lw=1.4, zorder=7)  # balustrada nad biegiem 3
        sw = next(s for s in M.SWIETLIKI if s["id"] == "SW1")["poly"]
        D.outline_dashed(ax, sw, color=D.C_GLASS, lw=0.7)
        ax.text(5.2, 8.5, "latarnia SW1 (nad)", fontsize=4.8, ha="center", va="center", color=D.C_GLASS, zorder=7)


def furniture(ax, kond):
    f, fc = D.furn, D.furn_circle
    if kond == "P0":
        f(ax, 0.6, 2.6, 3.4, 3.4, "sofa"); f(ax, 3.4, 1.5, 4.2, 3.4); f(ax, 1.5, 1.4, 2.6, 2.1)
        f(ax, 0.3, 4.65, 3.6, 5.25, "regał / TV", 4.5)
        f(ax, 5.3, 1.7, 7.6, 2.7, "stół 8 os. (pod pustką)", 4.3)
        f(ax, 9.0, 1.9, 10.9, 2.9, "wyspa"); f(ax, 11.295, 2.25, 11.895, 3.85, "zabud.", 4.2); f(ax, 9.65, 4.695, 10.50, 5.295, "sł. AGD", 4)
        f(ax, 1.2, 5.65, 2.6, 7.65, "łóżko\n140"); f(ax, 3.345, 5.60, 3.945, 7.60, "szafa", 4.2); f(ax, 0.105, 7.8, 0.7, 8.7, "", 4)
        f(ax, 1.35, 10.10, 2.475, 11.195, "natrysk", 4.2); f(ax, 0.105, 10.3, 0.75, 10.95, "WC", 4.2); f(ax, 0.105, 9.2, 0.6, 9.9, "um.", 4)
        f(ax, 3.20, 10.55, 3.875, 11.195, "WC", 4.2)
        f(ax, 4.10, 10.595, 6.30, 11.195, "szafy wejściowe", 4.2)
        f(ax, 10.0, 10.8, 11.2, 11.195, "buty", 4)
        fc(ax, 10.25, 6.0, 0.33, "CWU\n300 l", 4); f(ax, 11.3, 5.6, 11.895, 6.4, "PC\nwewn.", 3.8)
        f(ax, 11.3, 6.5, 11.895, 7.1, "bufor", 3.8); f(ax, 10.4, 7.35, 11.895, 7.95, "centrala went.", 3.8); f(ax, 9.755, 6.6, 10.0, 7.3, "RG", 3.6)
        f(ax, 12.8, 5.7, 14.7, 10.5, "auto 1"); f(ax, 15.5, 5.7, 17.4, 10.5, "auto 2")
        f(ax, 17.75, 7.0, 18.25, 10.9, "rowery", 4.2); f(ax, 12.3, 4.95, 14.0, 5.45, "ogród", 4)
    if kond == "P1":
        f(ax, 3.3, 0.3, 4.2, 2.3, "łóżko\n90", 4.5); f(ax, 0.105, 1.0, 0.7, 3.0, "biurko", 4); f(ax, 0.3, 3.35, 2.6, 3.94, "szafa wnękowa", 4.2)
        f(ax, 3.0, 6.2, 3.9, 8.2, "łóżko\n90", 4.5); f(ax, 0.105, 6.2, 0.7, 8.0, "biurko", 4); f(ax, 1.0, 8.2, 2.9, 8.795, "szafa", 4.2)
        f(ax, 9.0, 1.4, 11.3, 2.3, "sofa"); f(ax, 11.295, 3.6, 11.895, 5.2, "regały", 4); f(ax, 8.6, 3.2, 10.8, 3.6, "regał niski", 4)
        f(ax, 7.80, 7.95, 9.545, 8.795, "wanna", 4.5); f(ax, 8.6, 5.505, 9.545, 6.50, "natr.", 4.2)
        f(ax, 6.505, 6.10, 7.05, 7.50, "2 um.", 4.2); f(ax, 6.505, 7.90, 7.10, 8.55, "WC", 4.2)
        f(ax, 10.3, 8.2, 11.895, 8.795, "pralka+susz.", 4.2); f(ax, 11.3, 6.4, 11.895, 8.1, "blat", 4)
    if kond == "P2":
        f(ax, 0.4, 1.7, 2.6, 2.5, "biurko", 4.5); f(ax, -0.8, 4.90, 3.4, 5.295, "regały", 4.2); f(ax, -0.8, 2.8, 0.1, 4.7, "sofa", 4.2)
        f(ax, 4.75, 2.2, 5.65, 3.1, "klapa\n90x90", 4.2, ls=(0, (2, 1)))
        f(ax, 6.475, 1.6, 7.075, 3.9, "szafy", 4.2)
        f(ax, 9.1, 3.3, 10.9, 5.295, "łóżko\n180", 4.8); f(ax, 8.6, 4.8, 9.05, 5.29, "", 4); f(ax, 10.95, 4.8, 11.4, 5.29, "", 4)
        f(ax, 7.80, 7.90, 9.40, 8.70, "wanna wolnost.", 4.2); f(ax, 8.5, 5.505, 9.545, 6.80, "natrysk", 4.2)
        f(ax, 6.505, 6.2, 7.05, 7.6, "2 um.", 4.2); f(ax, 6.505, 7.9, 7.10, 8.55, "WC", 4.2)


def roofs_below(ax, kond):
    if kond == "P0":
        return
    by = {d["id"]: d for d in M.DACHY}
    for k in ("D-G", "D-P0"):
        D.draw_poly(ax, by[k]["poly"], facecolor="#e3f0d3", edgecolor="#6b8e3a", lw=0.8, zorder=0.5, hatch="..")
    ax.text(15.5, 8.0, "DACH ZIELONY GARAŻU\n(ekstensywny, nieużytkowy)\nattyka +3,65", fontsize=6.3, ha="center", va="center",
            color="#3d5a1c", zorder=3, bbox=dict(facecolor="#e3f0d3", edgecolor="none", pad=1))
    ax.text(2.0, 10.4, "dach zielony skrzydła wejściowego, attyka +3,40", fontsize=5.8, ha="center", va="center", color="#3d5a1c", zorder=3)
    sw2 = next(s for s in M.SWIETLIKI if s["id"] == "SW2")["poly"]
    D.draw_poly(ax, sw2, facecolor="#d6e6f5", edgecolor=D.C_GLASS, lw=0.7, zorder=0.7)
    ax.text(8.0, 10.3, "SW2", fontsize=5, ha="center", va="center", color=D.C_GLASS, zorder=3)
    if kond == "P2":
        for k in ("D-P1W", "D-P1E"):
            D.draw_poly(ax, by[k]["poly"], facecolor="#eeeeee", edgecolor="#777", lw=0.6, zorder=0.5)
        ax.text(1.7, 7.3, "dach P1 +6,50\n(żwir/rozchodnik)", fontsize=5.8, ha="center", va="center", color="#444", zorder=3)
        ax.text(11.1, 7.3, "dach P1\n+6,50", fontsize=5.8, ha="center", va="center", color="#444", zorder=3)
