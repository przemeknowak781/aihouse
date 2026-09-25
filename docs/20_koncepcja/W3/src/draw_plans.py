# -*- coding: utf-8 -*-
"""Rzuty kondygnacji P0, P1, P2 - wariant W2."""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
from shapely.geometry import box
from shapely.ops import unary_union
import model_w3 as M
import draw_common as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
S = M.SCHODY


def stairs(ax, kond):
    xw0, xw1 = S["bieg_W"]["x"]
    xe0, xe1 = S["bieg_E"]["x"]
    y0 = S["bieg_W"]["y0"]
    yl0, yl1 = S["spocznik"]["y"]
    cut_k = 5  # linia ciecia ok. 1,0 m nad posadzka

    def treads(x0, x1, ys, style):
        for y in ys:
            ax.plot([x0, x1], [y, y], color="black", lw=0.5, ls=style, zorder=4)

    ysW = [y0 + S["s"] * k for k in range(0, 9)]
    ysE = [yl0 - S["s"] * k for k in range(0, 9)]
    if kond in ("P0", "P1"):
        treads(xw0, xw1, ysW[:cut_k + 1], "-")
        treads(xw0, xw1, ysW[cut_k + 1:], (0, (3, 2)))
        ax.plot([xw0, xw1], [ysW[cut_k] + 0.12, ysW[cut_k] + 0.30], color="black", lw=0.8, zorder=5)  # linia ciecia
        ax.annotate("", xy=((xw0 + xw1) / 2, ysW[cut_k] + 0.1), xytext=((xw0 + xw1) / 2, y0 + 0.12),
                    arrowprops=dict(arrowstyle="->", lw=0.9), zorder=6)
        ax.text((xw0 + xw1) / 2, y0 + 0.35, "G", fontsize=6, ha="center", va="bottom", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
        ax.add_patch(Rectangle((xw0, yl0), xe1 - xw0, yl1 - yl0, facecolor="none", edgecolor="black", lw=0.5, ls=(0, (3, 2)), zorder=4))
        ax.text(xe1 - 0.05, yl1 - 0.05, f"spocznik +{D.fmt(M.POZ[kond] + 1.575, 3)}", fontsize=4.6, ha="right", va="top", zorder=6)
    if kond == "P0":
        treads(xe0, xe1, ysE, (0, (3, 2)))
        ax.text((xe0 + xe1) / 2, 5.3, "bieg 2\n(nad)", fontsize=5, ha="center", va="bottom", color="#555", zorder=6)
    if kond in ("P1", "P2"):
        treads(xe0, xe1, ysE, "-")
        ax.annotate("", xy=((xe0 + xe1) / 2, y0 + 0.1), xytext=((xe0 + xe1) / 2, yl0 - 0.12),
                    arrowprops=dict(arrowstyle="->", lw=0.9), zorder=6)
        ax.text((xe0 + xe1) / 2, y0 + 0.30, "D" if kond == "P2" else "D", fontsize=6, ha="center", va="bottom", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    if kond == "P2":
        ax.plot([xw0, xw1], [y0, yl0], color="#777", lw=0.5, zorder=4)
        ax.plot([xw0, xw1], [yl0, y0], color="#777", lw=0.5, zorder=4)
        ax.text((xw0 + xw1) / 2, (y0 + yl0) / 2 + 0.55, "pustka\nnad\nbiegiem 1", fontsize=5, ha="center", va="center", color="#555", zorder=6,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.3))
        ax.add_patch(Rectangle((xw0, yl0), xe1 - xw0, yl1 - yl0, facecolor="none", edgecolor="black", lw=0.5, zorder=4))
        ax.text((xw0 + xe1) / 2, (yl0 + yl1) / 2, "spocznik +4,725\n(poniżej)", fontsize=5.5, ha="center", va="center", zorder=6)
        ax.add_patch(Rectangle((6.35, 5.20), 1.7, 2.9, facecolor="none", edgecolor="#3b7dd8", lw=0.6, ls=(0, (2, 2)), zorder=6))
        ax.text(7.2, 8.05, "świetlik 1,7x2,9 (nad)", fontsize=4.8, ha="center", va="top", color="#3b7dd8", zorder=6)
    ax.text(6.70, 4.92, "18 x 17,5/28", fontsize=4.8, ha="center", va="bottom", rotation=90, zorder=6) if False else None


def furniture(ax, kond):
    f, fc = D.furn, D.furn_circle
    if kond == "P0":
        f(ax, 0.6, 2.9, 3.3, 3.8, "sofa"); f(ax, 1.3, 1.8, 2.5, 2.5)
        f(ax, 0.5, 4.1, 3.2, 4.65, "RTV/regał", 4.5)
        f(ax, 5.0, 1.7, 7.4, 2.7, "stół 8 os."); f(ax, 8.90, 1.80, 10.70, 2.75, "wyspa")
        f(ax, 11.295, 2.05, 11.895, 4.695, "zabudowa", 4.5); f(ax, 10.30, 4.095, 11.295, 4.695, "", 4.5)
        f(ax, 0.40, 6.295, 1.80, 8.295, "łóżko\n140"); f(ax, 3.17, 6.30, 3.77, 8.295, "szafa", 4.5)
        f(ax, 5.09, 7.395, 5.99, 8.295, "natrysk", 4.5); f(ax, 3.98, 7.55, 4.60, 8.25, "WC", 4.5); f(ax, 3.98, 6.45, 4.50, 7.05, "umyw.", 4.2)
        f(ax, 8.60, 7.60, 9.30, 8.25, "WC", 4.5); f(ax, 9.05, 6.50, 9.55, 6.95, "", 4)
        f(ax, 11.295, 6.45, 11.895, 8.295, "szafa", 4.5)
        f(ax, 12.80, 3.95, 14.70, 8.75, "auto 1"); f(ax, 15.40, 3.95, 17.30, 8.75, "auto 2")
        f(ax, 17.75, 6.05, 18.25, 8.80, "rowery", 4.2); f(ax, 17.75, 2.90, 18.25, 4.85, "ogród", 4.2)
        fc(ax, 16.10, 1.30, 0.33, "CWU\n300 l", 4); f(ax, 16.60, 0.20, 17.40, 0.65, "PC wewn.", 4)
        f(ax, 17.55, 0.20, 18.25, 0.45, "RG", 4); f(ax, 17.55, 1.9, 18.25, 2.45, "bufor", 4)
        f(ax, 13.60, 0.15, 14.20, 0.60, "buty", 4.2); f(ax, 14.40, 0.15, 15.35, 0.55, "półki", 4)
    if kond == "P1":
        f(ax, 2.80, 0.30, 3.80, 2.30, "łóżko\n90x200", 4.5); f(ax, 0.3, 0.2, 1.9, 0.8, "biurko", 4.5); f(ax, 0.2, 2.95, 2.55, 3.50, "szafa", 4.5)
        f(ax, 0.3, 5.3, 1.9, 7.3, "łóżko\n90x200", 4.5); f(ax, 3.17, 5.95, 3.77, 8.20, "szafa", 4.5); f(ax, 1.2, 7.7, 3.0, 8.25, "biurko", 4.5)
        f(ax, 4.0, 0.2, 4.45, 3.5, "regały - biblioteka", 4.2); f(ax, 6.2, 1.2, 8.6, 2.1, "sofa"); f(ax, 9.3, 0.8, 11.6, 3.0, "strefa\nnauki/gier", 4.5)
        f(ax, 3.98, 7.40, 5.60, 8.295, "wanna", 4.5); f(ax, 5.09, 5.70, 5.99, 6.60, "natr.", 4.2); f(ax, 3.98, 5.80, 4.50, 6.90, "2 umyw.", 4.2); f(ax, 5.40, 6.75, 5.99, 7.35, "WC", 4.2)
        f(ax, 8.95, 7.65, 10.25, 8.25, "pralka+susz.", 4.2); f(ax, 10.3, 7.65, 11.85, 8.25, "blat/zlew", 4.2); f(ax, 11.25, 5.0, 11.85, 7.4, "szafy", 4.2)
    if kond == "P2":
        f(ax, 1.60, 0.90, 3.60, 2.70, "łóżko\n180x200", 4.8); f(ax, -0.7, 3.9, 1.8, 4.5, "komoda", 4.5)
        f(ax, 3.75, 0.2, 4.35, 3.2, "szafy", 4.2); f(ax, 5.45, 0.2, 6.05, 3.0, "szafy", 4.2)
        f(ax, 3.98, 7.35, 5.99, 8.295, "wanna wolnost.", 4.2); f(ax, 5.09, 5.70, 5.99, 6.60, "natr.", 4.2); f(ax, 3.98, 5.80, 4.50, 6.90, "2 umyw.", 4.2); f(ax, 5.40, 6.75, 5.99, 7.30, "WC", 4.2)
        f(ax, 9.0, 0.3, 11.6, 1.1, "biurko", 4.5); f(ax, 8.47, 0.30, 8.87, 3.10, "regał", 4.0)
        f(ax, 6.35, 0.25, 7.35, 0.85, "centrala\nrekuper.", 4); f(ax, 7.40, 1.60, 8.25, 2.45, "klapa\n90x90", 4.2, ls=(0, (2, 1)))


def roofs_below(ax, kond):
    green = unary_union([box(12.3, -0.30, 18.70, 9.30)])
    if kond in ("P1", "P2"):
        D.draw_poly(ax, green, facecolor="#e3f0d3", edgecolor="#6b8e3a", lw=0.8, zorder=0.5, hatch="..")
        ax.text(15.5, 4.2 if kond == "P1" else 4.2, "DACH ZIELONY GARAŻU\n(ekstensywny, nieużytkowy)\nattyka +3,85", fontsize=6.5,
                ha="center", va="center", color="#3d5a1c", zorder=3, bbox=dict(facecolor="#e3f0d3", edgecolor="none", pad=1))
    if kond == "P2":
        roofP1 = box(-0.30, 5.10, 12.30, 8.70).difference(box(3.575, 5.10, 8.725, 8.70))
        D.draw_poly(ax, roofP1, facecolor="#eeeeee", edgecolor="#777", lw=0.6, zorder=0.5)
        ax.text(1.7, 7.0, "dach P1 (+6,50)\nżwirowy, PV", fontsize=6, ha="center", va="center", color="#444", zorder=3)
        ax.text(10.5, 7.0, "dach P1 (+6,50)\nżwirowy, PV", fontsize=6, ha="center", va="center", color="#444", zorder=3)


def overhangs(ax, kond):
    by = {p["id"]: p for p in M.PLYTY}
    if kond == "P0":
        for k in ("E-okap", "E-okap-W", "daszek"):
            D.outline_dashed(ax, by[k]["poly"], color="#444", lw=0.7)
        ax.text(5.0, -1.05, "okap ST1 (linia E) +2,80 - wysunięcie 1,00 m", fontsize=5.5, ha="center", va="center", color="#444")
        ax.text(-1.05, 2.4, "okap zach. 1,50 m", fontsize=5.5, rotation=90, ha="center", va="center", color="#444")
        ax.text(10.9, 9.62, "daszek nad wejściem", fontsize=5.3, ha="center", va="center", color="#444")
        a2 = box(-1.30, -0.30, -0.30, 5.10)
        D.outline_dashed(ax, a2, color="#b04a4a", ls=(0, (6, 2, 1, 2)), lw=0.7)
        ax.text(-0.8, 5.35, "wspornik P2", fontsize=5, ha="center", va="bottom", color="#b04a4a")
        terr = unary_union([box(-1.80, -4.30, 11.70, -0.30), box(-1.80, -0.30, -0.30, 4.80)])
        D.draw_poly(ax, terr, facecolor="#f4efe6", edgecolor="#b8a88a", lw=0.6, zorder=0.3)
        ax.text(4.9, -3.4, "TARAS OGRODOWY -0,05 (deska kompozytowa / płyty)  61,7 m²", fontsize=6.5, ha="center", va="center", color="#6b5b3e")
        ax.add_patch(Rectangle((9.80, 8.70), 2.50, 1.30, facecolor="#ececec", edgecolor="#999", lw=0.5, zorder=0.4))
        ax.text(11.05, 9.25, "podest -0,02 / 1 stopień", fontsize=4.8, ha="center", va="center", color="#555", zorder=1)
    if kond == "P1":
        for k in ("E-okap", "E-okap-W", "C-dol"):
            D.draw_poly(ax, by[k]["poly"], facecolor="#f2f2f2", edgecolor="#555", lw=0.6, zorder=0.6)
        D.outline_dashed(ax, by["C-gora"]["poly"], color="#444")
        D.outline_dashed(ax, by["ST2-okap"]["poly"], color="#888", ls=(0, (2, 2)), lw=0.6)
        for x in (3.60, 12.45):
            ax.add_patch(Rectangle((x, -1.30), 0.15, 1.0, facecolor="#555", edgecolor="none", zorder=3))
        ax.text(8.1, -0.8, "RAMA C: płyta dolna +3,65/+3,85 (linia D), płyta górna +5,35/+5,55, wysunięcie 1,00 m", fontsize=5.5,
                ha="center", va="center", color="#333", zorder=3)
        ax.text(-1.05, 2.4, "okap ST1 poniżej", fontsize=5.3, rotation=90, ha="center", va="center", color="#555", zorder=3)
    if kond == "P2":
        D.draw_poly(ax, by["ST2-okap"]["poly"], facecolor="#f2f2f2", edgecolor="#555", lw=0.6, zorder=0.6)
        D.outline_dashed(ax, by["ST3-okap"]["poly"], color="#444")
        L = M.LAMELE
        ax.plot([L["x"][0], L["x"][1]], [L["y"], L["y"]], color="#8a6a3a", lw=1.6, zorder=3)
        x = L["x"][0]
        while x <= L["x"][1] + 1e-6:
            ax.plot([x, x], [L["y"] - 0.05, L["y"] + 0.05], color="#8a6a3a", lw=0.5, zorder=3)
            x += 0.36
        ax.text(5.5, -0.95, "lamele pionowe 40x80 co 12 cm, odsunięte 15 cm od lica (drewno termo)", fontsize=5.5, ha="center",
                va="center", color="#6b4f25", zorder=3)
        ax.text(-1.85, 2.4, "okap ST3 1,10 m", fontsize=5.3, rotation=90, ha="center", va="center", color="#444", zorder=3)
        for sl in []:
            pass


def shafts(ax, kond):
    for g, t in ((M.SI, "SI"), (M.S2, "K2")):
        if kond == "P2" and t == "K2":
            continue
        D.draw_poly(ax, g, facecolor="#d6e6f5", edgecolor="#2d6aa8", lw=0.6, zorder=6, hatch="xx")
        c = g.centroid
        ax.text(c.x, c.y, t, fontsize=4.8, ha="center", va="center", color="#1c4a78", zorder=7,
                bbox=dict(facecolor="white", edgecolor="none", pad=0.2, alpha=0.7))


def columns(ax, kond):
    if kond == "P0":
        for s in M.SLUPY:
            x, y = s["xy"]
            ax.add_patch(Rectangle((x - 0.06, y - 0.06), 0.12, 0.12, facecolor="black", zorder=9))
            ax.text(x, y + 0.35, s["id"], fontsize=5, ha="center", va="bottom", zorder=9,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.2))


def dims(ax, kond):
    if kond == "P0":
        ext = [-0.30, 18.70]
        D.dim_chain_h(ax, [M.OSIE_X[k] for k in ("A", "B", "C", "D", "E", "F")], -5.0, fs=6)
        D.dim_h(ax, -0.30, 18.70, -5.7, "18,90 (lica zewn. P0)", fs=6.5, ext_from=-0.30)
        D.dim_chain_h(ax, [-0.30, 0.30, 0.30 + 2.28, 0.30 + 4.56, 0.30 + 6.84, 0.30 + 9.12, 11.70, 12.30], -4.6, fs=5.3)
        D.dim_chain_v(ax, [M.OSIE_Y[k] for k in ("1", "2", "3", "4", "5")], 20.9, fs=6)
        D.dim_v(ax, -0.30, 9.30, 21.5, "9,60", fs=6.5, left=False)
        D.dim_v(ax, -0.30, 8.70, -3.9, "9,00", fs=6.5)
        D.dim_chain_v(ax, [-0.30, 0.0, 4.8, 8.4, 8.7], -3.3, fs=5.5)
    elif kond == "P1":
        D.dim_chain_h(ax, [M.OSIE_X[k] for k in ("A", "B", "C", "D", "E")], -5.0, fs=6)
        D.dim_h(ax, -0.30, 12.30, -5.7, "12,60 (bryła B)", fs=6.5, ext_from=-0.30)
        D.dim_chain_h(ax, [-0.30, 3.60, 4.10, 11.10, 12.60], -4.3, fs=5.5)
        ax.text(7.6, -3.95, "boks C: 3 x 2,33", fontsize=5.3, ha="center")
        D.dim_chain_v(ax, [M.OSIE_Y[k] for k in ("1", "3", "4")], 19.6, fs=6)
        D.dim_v(ax, -0.30, 8.70, -3.9, "9,00", fs=6.5)
    else:
        D.dim_chain_h(ax, [M.OSIE_X[k] for k in ("A'", "A", "B", "C", "D", "E")], -5.0, fs=6)
        D.dim_h(ax, -1.30, 12.30, -5.7, "13,60 (bryła A)", fs=6.5, ext_from=-1.30)
        D.dim_h(ax, -2.40, 12.60, -4.3, "15,00 (płyta ST3)", fs=6.0)
        D.dim_chain_v(ax, [M.OSIE_Y[k] for k in ("1", "3", "4")], 19.6, fs=6)
        D.dim_v(ax, -1.30, 5.10, -3.9, "6,40 (A)", fs=6.2)


INFO = {
    "P0": ("W2 - RZUT PARTERU P0   (±0,00 = 101,65 m n.p.m.; posadzka P0 = 0,00; h w świetle 2,80 m)",
           "Konstrukcja: ściany nośne silikat 18 cm w osiach A, B, C, D, E, F, 1(strefa gosp.), 3, 4, 5 - ciągłe przez P0-P1 (P2: A' lekka na wsporniku, E, 1, 3, B, C, D). "
           "Fasada pd. (E): przeszklenie 5 kwater na słupach stalowych SL1-SL4 + belka B1 25x105 (+2,80...+3,85). "
           "Strop ST1 20 cm, rozpiętości 4,80 / 3,60 m (N-S); garaż: płyta 24 cm, rozp. 6,40 m (E-W)."),
    "P1": ("W2 - RZUT I PIĘTRA P1   (posadzka +3,15; h w świetle 2,80 m)",
           "Bryła B 12,60 m; boks C (3 kwatery 2,33 m, parapet 0,70 z dolną częścią stałą VSG do 0,85) w ramie wysuniętej 1,00 m. "
           "Pokoje dzieci od zachodu (elewacja pd. bryły B pełna jak w szkicu). Pion SI (kanalizacja K1 + kanały rekuperacji) nad pionem P0 i pod P2."),
    "P2": ("W2 - RZUT II PIĘTRA P2   (posadzka +6,30; h w świetle 2,80 m)",
           "Bryła A 13,60 m w lamelach, wspornik 1,00 m na zachód (ściany-tarcze żelbetowe w osiach 1 i 3 na odc. A'–x 2,0), płyty ST2/ST3 wysunięte 1,00-1,10 m. "
           "Nadbudowa klatki schodowej i łazienki rodziców nad osiami B-D (niewidoczna od południa). Wyjście na dach: klapa 0,9x0,9 w pom. techn. 2.06."),
}


def plan(kond):
    fig, ax = plt.subplots(figsize=(16.5, 11.2))
    ax.set_aspect("equal")
    ax.set_xlim(-5.2, 23.0)
    ax.set_ylim(-7.4, 12.2)
    ax.axis("off")
    roofs_below(ax, kond)
    overhangs(ax, kond)
    furniture(ax, kond)
    stairs(ax, kond)
    D.draw_walls(ax, kond)
    D.draw_openings(ax, kond)
    columns(ax, kond)
    shafts(ax, kond)
    offs = {"0.06": (3.0, 1.0), "0.07": (4.75, 5.55), "0.05": (7.82, 5.45), "0.04": (6.7, 6.4), "0.02": (10.9, 5.6),
            "0.03": (9.07, 7.05), "0.13": (15.2, 5.0), "1.01": (1.9, 4.17), "1.02": (8.0, 2.9), "1.06": (7.26, 7.55),
            "2.01": (7.26, 3.55), "2.06": (7.26, 1.35), "1.05": (4.95, 6.55), "2.04": (4.95, 6.55), "0.08": (4.95, 6.9),
            "0.12": (16.9, 1.35), "0.11": (14.87, 1.3), "0.10": (13.15, 1.35)}
    if kond == "P2":
        offs["2.04"] = (4.95, 6.3)
    D.label_rooms(ax, kond, fs=6.3, offsets=offs)
    if kond == "P0":
        ax.text(1.8, 0.45, "salon", fontsize=7, ha="center", style="italic", color="#555", zorder=20)
        ax.text(6.2, 0.45, "jadalnia", fontsize=7, ha="center", style="italic", color="#555", zorder=20)
        ax.text(10.2, 0.45, "kuchnia", fontsize=7, ha="center", style="italic", color="#555", zorder=20)
        ax.text(20.0, 1.1, "PC\njedn.\nzewn.", fontsize=5, ha="center", va="center", zorder=20)
        ax.add_patch(Rectangle((19.60, 0.60), 0.80, 1.0, facecolor="#e8e8e8", edgecolor="black", lw=0.6))
    dims(ax, kond)
    names_x = [k for k in M.OSIE_X if not (kond != "P2" and k == "A'") and not (kond != "P0" and k == "F")]
    names_y = ["1", "3", "4"] + (["2", "5"] if kond == "P0" else [])
    D.axes_bubbles(ax, names_x, names_y, -6.6, 11.5, -4.7, 22.3 if kond == "P0" else 20.6)
    D.north_arrow(ax, 20.8, 9.8 if kond != "P0" else 10.6, 0.7)
    t, sub = INFO[kond]
    fig.suptitle(t, fontsize=12.5, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945, sub, fontsize=7.6, ha="left", va="top", color="#333", wrap=True)
    pu = sum(M.room_area(r) for r in M.POMIESZCZENIA if r["kond"] == kond and r["kat"] != "garaż")
    txt = f"PU kondygnacji (bez garażu): {D.fmt(pu)} m²"
    if kond == "P0":
        g = next(r for r in M.POMIESZCZENIA if r["id"] == "0.13")
        txt += f"   |   garaż: {D.fmt(M.room_area(g))} m²"
    fig.text(0.02, 0.03, txt + "   |   wymiary w m, lica wykończone; osie = środek warstwy konstrukcyjnej   |   SI - szacht instałacyjny (pion K1 + wentylacja), K2 - pion kanalizacyjny pralni/WC",
             fontsize=7.5, ha="left", va="bottom")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.05)
    fn = os.path.join(OUT, f"rzut_{kond}.png")
    fig.savefig(fn, dpi=150)
    plt.close(fig)
    return fn


if __name__ == "__main__":
    for k in ("P0", "P1", "P2"):
        print(plan(k))
