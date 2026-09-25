# -*- coding: utf-8 -*-
"""Przekroje A-A i B-B wariantu W3 (os pozioma: y budynku, S po lewej, N po prawej)."""
import sys, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon as MPoly
import model_w3 as M
import draw_common as D
from sec_data import SEC

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
P, S = M.POZ, M.SCHODY
STY = {"zb": dict(facecolor="#9a9a9a", edgecolor="black", hatch="////", lw=0.5), "mur": dict(facecolor="#c9c9c9", edgecolor="black", lw=0.5),
       "ins": dict(facecolor="#f3e6b3", edgecolor="#8a7a40", lw=0.4), "gl": dict(facecolor="#9fc3e6", edgecolor="#2d6aa8", lw=0.6),
       "wid": dict(facecolor="none", edgecolor="#777", lw=0.5, ls="--"), "zie": dict(facecolor="#b9d99a", edgecolor="#4e7a2a", lw=0.5),
       "bal": dict(facecolor="#cfe3f7", edgecolor="#2d6aa8", lw=0.6), "lam": dict(facecolor="#a67c4e", edgecolor="none")}


def stairs(ax, cut):
    """Biegi 1 i 3 (pas wsch., w gore ku pn.), spoczniki, biegi 2 i 4 (pas zach., w gore ku pd.)."""
    y0, yl0, yl1 = S["bieg_E"]["y0"], *S["spocznik"]["y"]
    for base in (0.0, P["wys_kond"]):
        # bieg nieparzysty: od y0 (z=base) do yl0 (z=base+1,575)
        pts = [(y0, base)]
        for k in range(9):
            y = y0 + k * S["s"]; z = base + (k + 1) * S["h"]
            pts += [(y, z), (min(y + S["s"], yl0), z)] if k < 8 else [(y, z)]
        pts += [(yl0, base + 1.575 - 0.2), (y0, base - 0.2 if base > 0 else base)]
        kw = dict(facecolor="#9a9a9a", edgecolor="black", hatch="////", lw=0.5) if cut else dict(facecolor="none", edgecolor="#555", lw=0.6)
        ax.add_patch(MPoly(pts, closed=True, zorder=4, **kw))
        ax.add_patch(Rectangle((yl0, base + 1.575 - 0.2), yl1 - yl0, 0.2, zorder=4, **kw))
        # bieg parzysty (w widoku za cieciem): od spocznika w gore ku pd.
        ys = [yl0 - k * S["s"] for k in range(9)]
        zs = [base + 1.575 + (k + 1) * S["h"] for k in range(9)]
        xs, zz = [yl0], [base + 1.575]
        for y, z in zip(ys, zs):
            xs += [y, y]; zz += [zz[-1], z]
        ax.plot(xs, zz, color="#555", lw=0.6, zorder=3.5)
    ax.text(6.6, 1.0, "bieg 1\n9 x 17,5/28", fontsize=5.5, ha="center", zorder=8)


def section(ax, key):
    d = SEC[key]
    ys = np.linspace(-6.0, 15.0, 50)
    zt = [M.teren_wzgl(d["x"], y) for y in ys]
    ax.fill_between(ys, zt, -1.5, color="#e7e1d4", zorder=0.2)
    ax.plot(ys, zt, color="#6b5b3e", lw=1.2, zorder=0.3)
    for kind, y0, y1, z0, z1, lbl in d["el"]:
        ax.add_patch(Rectangle((y0, z0), y1 - y0, z1 - z0, zorder=5 if kind != "wid" else 3, **STY[kind]))
    stairs(ax, key == "B")
    for y, z, t in d["pom"]:
        ax.text(y, z, t, fontsize=6.5, ha="center", va="center", zorder=9, color="#333")
    for z, t in [(0.0, "±0,000 P0"), (P["P1"], "+3,150 P1"), (P["P2"], "+6,300 P2"), (2.80, "+2,800"), (5.70, "+5,700"), (5.95, "+5,950"),
                 (9.10, "+9,100"), (P["attyka_P2"], "+9,850 attyka"), (P["attyka_P0"], "+3,400"), (-0.28, "-0,28 teren śr.")]:
        ax.plot([13.2, 13.6], [z, z], color="black", lw=0.6)
        ax.add_patch(MPoly([(13.4, z), (13.3, z + 0.15), (13.5, z + 0.15)], closed=True, facecolor="black"))
        ax.text(13.7, z, t, fontsize=6, va="center")
    D.dim_v(ax, 0.0, 2.80, -2.4, "2,80", fs=6); D.dim_v(ax, 3.15, 5.95, -2.4, "2,80", fs=6); D.dim_v(ax, 6.30, 9.10, -2.4, "2,80", fs=6)
    D.dim_v(ax, -0.28, P["attyka_P2"], -3.4, f"H = {D.fmt(P['attyka_P2'] + 0.28)} (≤ 11,00 MPZP)", fs=6)
    ax.text(-1.2, -1.35, "S ←", fontsize=8, fontweight="bold"); ax.text(11.8, -1.35, "→ N", fontsize=8, fontweight="bold")
    ax.set_xlim(-4.0, 16.0); ax.set_ylim(-1.6, 10.6); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(d["tytul"], fontsize=10, loc="left", fontweight="bold")


def main():
    fig, axs = plt.subplots(1, 2, figsize=(18, 8.2))
    for ax, k in zip(axs, ("A", "B")):
        section(ax, k)
    fig.suptitle("W3 — PRZEKROJE A-A i B-B (rzędne względem ±0,000 = 101,65 m n.p.m.)", fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.98)
    fig.text(0.02, 0.02, "Stropy: ST1 20 cm (+2,80/+3,00), ST2 20 cm (+5,95/+6,15), ST2L loggii obniżona (+5,70/+5,90), ST3 22 cm (+9,10/+9,32). "
             "Schody: 2 x 9 podnóżków 17,5/28 cm (2h+s = 0,63), bieg 1,00 m, spocznik 1,05 x 2,14 m; prześwit nad biegami ≈ 2,94 m.", fontsize=7.5)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.92, bottom=0.07, wspace=0.04)
    fn = os.path.join(OUT, "przekroj.png"); fig.savefig(fn, dpi=150); plt.close(fig); print(fn)


if __name__ == "__main__":
    main()
