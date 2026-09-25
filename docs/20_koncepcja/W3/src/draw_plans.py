# -*- coding: utf-8 -*-
"""Rzuty kondygnacji P0, P1, P2 - wariant W3."""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from shapely.geometry import box
import model_w3 as M
import draw_common as D
from plan_parts import stairs, furniture, roofs_below

OUT = sys.argv[1] if len(sys.argv) > 1 else "."


def overhangs(ax, kond):
    by = {p["id"]: p for p in M.PLYTY}
    if kond == "P0":
        for k in ("E-okap", "E-okap-W", "daszek"):
            D.outline_dashed(ax, by[k]["poly"], color="#444", lw=0.7)
        ax.text(5.0, -1.05, "okap ST1 (linia E) - wysunięcie 1,00 m", fontsize=5.5, ha="center", color="#444")
        ax.text(-1.05, 2.8, "okap zach. 1,50 m", fontsize=5.5, rotation=90, ha="center", va="center", color="#444")
        ax.text(8.25, 12.55, "daszek 2,70x1,20", fontsize=5.2, ha="center", color="#444")
        D.outline_dashed(ax, box(-1.30, 0.90, -0.30, 5.70), color="#b04a4a", ls=(0, (6, 2, 1, 2)), lw=0.7)
        ax.text(-0.8, 5.85, "wspornik P2", fontsize=5, ha="center", va="bottom", color="#b04a4a")
        for k, c in (("taras", "#f4efe6"), ("patio", "#efe9dc")):
            D.draw_poly(ax, M.TEREN_ELEM[k]["poly"], facecolor=c, edgecolor="#b8a88a", lw=0.6, zorder=0.3)
        ax.text(5.0, -3.3, "TARAS OGRODOWY S+W  -0,05", fontsize=6.5, ha="center", color="#6b5b3e")
        ax.text(14.85, 1.8, "PATIO PORANNE\n(E, osłonięte od pn.)", fontsize=6.2, ha="center", va="center", color="#6b5b3e")
        D.outline_dashed(ax, by["G-okap"]["poly"], color="#444", lw=0.6)
        ax.text(15.5, 3.75, "okap dachu garażu (linia D)", fontsize=5, ha="center", color="#444")
        ax.plot([8.0, 8.0], [-4.4, 12.6], color="#d08a1e", lw=0.9, ls=(0, (8, 3)), zorder=0.8)
        ax.text(8.12, -4.3, "OŚ WIDOKU: furtka → drzwi → hol → jadalnia → ogród", fontsize=6, color="#b06d0a", rotation=0, zorder=21)
    if kond == "P1":
        D.draw_poly(ax, by["E-okap"]["poly"], facecolor="#f2f2f2", edgecolor="#777", lw=0.5, zorder=0.4)
        D.draw_poly(ax, by["E-okap-W"]["poly"], facecolor="#f2f2f2", edgecolor="#777", lw=0.5, zorder=0.4)
        D.draw_poly(ax, by["C-dol"]["poly"], facecolor="#e6e6e6", edgecolor="#444", lw=0.6, zorder=0.6)
        D.draw_poly(ax, by["C-boki"]["poly"], facecolor="#555", edgecolor="none", zorder=0.7)
        D.outline_dashed(ax, by["ST2L"]["poly"], color="#888", ls=(0, (2, 2)), lw=0.6)
        ax.text(8.25, -0.8, "RAMA C: płyta dolna +3,45/+3,65 (linia D), górna +5,15/+5,35, wysunięcie 1,00 m", fontsize=5.4, ha="center", va="center", color="#333", zorder=3)
        D.draw_poly(ax, M.PUSTKA, facecolor="#fbf6e8", edgecolor="#c9a64a", lw=0.8, zorder=0.9, hatch="//")
        ax.plot([4.5, 4.5, 8.4], [0.15, 4.0, 4.0], color=D.C_GLASS, lw=1.6, zorder=8)
        ax.plot([8.4, 8.4], [0.15, 4.0], color=D.C_GLASS, lw=1.6, zorder=8)
        ax.text(6.45, 2.1, "PUSTKA\nnad jadalnią\n(h = 5,70 / 5,95)", fontsize=7, ha="center", va="center", color="#8a6d1c", zorder=9,
                bbox=dict(facecolor="#fbf6e8", edgecolor="none", pad=0.8))
    if kond == "P2":
        D.draw_poly(ax, by["ST2L"]["poly"], facecolor="#f2f2f2", edgecolor="#555", lw=0.6, zorder=0.4)
        D.draw_poly(ax, M.LOGGIA["poly"], facecolor="#f4efe6", edgecolor="#b8a88a", lw=0.5, zorder=0.5)
        ax.text(5.5, 0.45, "LOGGIA +6,28 (deska na wspornikach, odwodnienie liniowe)", fontsize=5.8, ha="center", va="center", color="#6b5b3e", zorder=3)
        D.outline_dashed(ax, by["ST3-okap"]["poly"], color="#444")
        L = M.LAMELE
        ax.plot(L["x"], [L["y"], L["y"]], color="#8a6a3a", lw=1.6, zorder=3)
        ax.text(5.5, -0.8, "ekran lamel pionowych 40x80 co 12 cm (lico bryły A), płyty ST2L/ST3 wysunięte 0,90 m", fontsize=5.5, ha="center", color="#6b4f25", zorder=3)
        for s in M.SLUPY_P2:
            x, y = s["xy"]
            ax.add_patch(Rectangle((x - 0.05, y - 0.05), 0.10, 0.10, facecolor="black", zorder=9))


def shafts(ax, kond):
    for g, t in ((M.SZACHT_SI, "SI"), (M.SZACHT_S2, "K2")):
        if kond == "P2" and t == "K2":
            continue
        D.draw_poly(ax, g, facecolor="#d6e6f5", edgecolor="#2d6aa8", lw=0.6, zorder=6, hatch="xx")
        c = g.centroid
        ax.text(c.x, c.y, t, fontsize=4.6, ha="center", va="center", color="#1c4a78", zorder=7)


def columns(ax, kond):
    lst = M.SLUPY if kond == "P0" else (M.SLUPKI_C if kond == "P1" else [])
    for s in lst:
        x, y = s["xy"]
        ax.add_patch(Rectangle((x - 0.06, y - 0.06), 0.12, 0.12, facecolor="black", zorder=9))
        ax.text(x, y + 0.3, s["id"], fontsize=4.8, ha="center", va="bottom", zorder=9, bbox=dict(facecolor="white", edgecolor="none", pad=0.2))


def dims(ax, kond):
    X, Y = M.OSIE_X, M.OSIE_Y
    if kond == "P0":
        D.dim_chain_h(ax, [X[k] for k in ("A", "B", "C", "D", "E", "F")], -5.6, fs=6)
        D.dim_h(ax, -0.30, 18.70, -6.3, "19,00 (lica zewn. P0: bryła B + garaż)", fs=6.5, ext_from=-0.30)
        D.dim_chain_h(ax, [-0.30, 1.00, 2.60, 4.50, 6.90, 9.30, 11.85, 12.30], -5.0, fs=5.3)
        D.dim_chain_v(ax, [Y[k] for k in ("1", "2", "3", "4", "5")], 20.4, fs=6)
        D.dim_v(ax, -0.30, 11.60, 21.1, "11,90", fs=6.5, left=False)
        D.dim_chain_v(ax, [-0.30, 5.40, 8.90, 11.60], -3.3, fs=5.5)
    elif kond == "P1":
        D.dim_chain_h(ax, [X[k] for k in ("A", "B", "B'", "C", "D", "E")], -5.0, fs=6)
        D.dim_h(ax, -0.30, 12.30, -5.7, "12,60 (bryła B)", fs=6.5, ext_from=-0.30)
        D.dim_chain_h(ax, [3.60, 4.50, 6.90, 9.30, 11.70, 12.90], -4.3, fs=5.5)
        D.dim_chain_v(ax, [Y[k] for k in ("1", "3", "4")], 19.6, fs=6)
        D.dim_v(ax, -0.30, 9.20, -3.9, "9,50", fs=6.5)
    else:
        D.dim_chain_h(ax, [X[k] for k in ("A'", "A", "B", "C", "D", "E")], -5.0, fs=6)
        D.dim_h(ax, -1.30, 12.30, -5.7, "13,60 (bryła A)", fs=6.5, ext_from=-1.30)
        D.dim_h(ax, -2.20, 12.60, -4.3, "14,80 (płyta ST3)", fs=6.0)
        D.dim_chain_v(ax, [Y[k] for k in ("1", "1'", "3", "4")], 19.6, fs=6)
        D.dim_v(ax, -1.20, 5.70, -3.9, "6,90 (A z płytą)", fs=6.0)


INFO = {
    "P0": ("W3 - RZUT PARTERU P0   (±0,00 = 101,65 m n.p.m.; h w świetle 2,80 m; jadalnia 5,70-5,95 m)",
           "Sekwencja wejścia na osi x = 8,00: furtka → dojście → daszek → wiatrołap (świetlik SW2) → szklana przegroda → hol → wylot 2,6 m → jadalnia pod pustką → HS kw. 4 → taras → oś ogrodowa. "
           "Ściany nośne silikat 18: osie A, E, F, 3, 4, 5, B, D (P0-P2 w pionie). Fasada pd. 5 kwater na słupach SL1-SL4 (RK 120) + podciąg PD-1 w ST1."),
    "P1": ("W3 - RZUT I PIĘTRA P1   (posadzka +3,15; h w świetle 2,80 m; pod loggią 2,55 m)",
           "Galeria nad pustką jadalni (x 4,50-8,40) otwarta na boks C; pokój rodzinny otwarty na galerię. Pokoje dzieci od zachodu. "
           "Ściany lekkie GK (DZL) nad otwartą strefą parteru na podciągach PD-2 (oś B') i krawędzi pustki."),
    "P2": ("W3 - RZUT II PIĘTRA P2   (posadzka +6,30; h w świetle 2,80 m)",
           "Bryła A 13,60 m w lamelach, wspornik 1,00 m na zach.; pokoje cofnięte do osi 1' (y = 1,20) - loggia 1,20 m za lamelami. "
           "Nadbudowa nad osiami B-D (klatka z latarnią SW1 + łazienka rodziców nad łazienką P1). Wyjście na dach: klapa 0,9x0,9 w holu 2.01."),
}


def plan(kond):
    fig, ax = plt.subplots(figsize=(16.5, 11.6))
    ax.set_aspect("equal"); ax.set_xlim(-5.2, 22.6); ax.set_ylim(-7.4, 13.4); ax.axis("off")
    roofs_below(ax, kond); overhangs(ax, kond); furniture(ax, kond); stairs(ax, kond)
    D.draw_walls(ax, kond); D.draw_openings(ax, kond); columns(ax, kond); shafts(ax, kond)
    offs = {"0.01": (4.0, 3.9), "0.04": (5.2, 7.2), "0.05": (8.0, 7.2), "0.06": (10.8, 6.8), "0.02": (11.28, 4.7),
            "0.07": (8.0, 10.1), "0.08": (10.8, 9.6), "0.09": (1.2, 9.6), "0.10": (3.25, 10.0), "0.11": (5.2, 9.35),
            "0.12": (15.3, 8.3), "1.01": (2.4, 4.7), "1.02": (10.1, 4.1), "1.05": (5.2, 7.2), "1.06": (8.0, 7.0), "1.07": (10.8, 7.0),
            "2.06": (5.2, 7.2), "2.05": (8.0, 7.0), "2.03": (7.2, 2.2)}
    D.label_rooms(ax, kond, fs=6.2, offsets=offs)
    if kond == "P0":
        for x, t in ((1.9, "salon"), (6.45, "jadalnia"), (10.2, "kuchnia")):
            ax.text(x, 0.45, t, fontsize=7, ha="center", style="italic", color="#555", zorder=20)
        ax.add_patch(Rectangle((10.20, 11.85), 1.20, 0.60, facecolor="#e8e8e8", edgecolor="black", lw=0.6, zorder=20))
        ax.text(10.8, 12.15, "PC zewn.", fontsize=4.6, ha="center", va="center", zorder=21)
    dims(ax, kond)
    names_x = [k for k in M.OSIE_X if not (kond != "P2" and k == "A'") and not (kond != "P0" and k == "F") and not (kond != "P1" and k == "B'")]
    names_y = ["1", "3", "4"] + (["2", "5"] if kond == "P0" else []) + (["1'"] if kond == "P2" else [])
    D.axes_bubbles(ax, names_x, names_y, -6.9, 12.6, -4.7, 21.8 if kond == "P0" else 20.6)
    D.north_arrow(ax, 21.3, 11.0, 0.7)
    t, sub = INFO[kond]
    fig.suptitle(t, fontsize=12.5, fontweight="bold", x=0.02, ha="left", y=0.975)
    fig.text(0.02, 0.945, sub, fontsize=7.4, ha="left", va="top", color="#333", wrap=True)
    txt = f"PU kondygnacji (bez garażu): {D.fmt(M.pu(kond))} m²"
    if kond == "P0":
        g = next(r for r in M.POMIESZCZENIA if r["id"] == "0.12")
        txt += f"   |   garaż: {D.fmt(M.room_area(g))} m²"
    fig.text(0.02, 0.025, txt + "   |   wymiary w m, lica wykończone; osie = środek warstwy konstrukcyjnej   |   SI - szacht (pion K1 + wentylacja), K2 - pion pralni",
             fontsize=7.5, ha="left", va="bottom")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.05)
    fn = os.path.join(OUT, f"rzut_{kond}.png")
    fig.savefig(fn, dpi=150); plt.close(fig)
    return fn


if __name__ == "__main__":
    for k in (sys.argv[2:] or ["P0", "P1", "P2"]):
        print(plan(k))
