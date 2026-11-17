# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 – podgląd rzutów S (+27,30) i antresoli (+30,90) oraz przekrój linii wzroku z galerii.

Uruchomienie (z katalogu umwd/):  python3 docs/20_koncepcja/_s2_rzut.py
Zapisuje: docs/20_koncepcja/img/s2_plan.png, docs/20_koncepcja/img/s2_przekroj.png
Układ (u, v) wieży: u – oś wzdłuż elewacji pd. (az. 76,3°), v – ku pn. (az. 346,3°).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s2_model as M  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Polygon as MPoly  # noqa: E402

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(IMG, exist_ok=True)
S = M.level_S()
A = M.level_ANT()
rows, aisles = M.build_rows()

COL = {"zamk": "#dbe8f5", "sala": "#f6ead2", "hol": "#e6f2dc", "kom": "#fff4c2", "antresola": "#d9efd0",
       "wc": "#e9dcf5", "pub": "#f8d9d9", "trzon": "#9a9a9a"}


def cat(k):
    if k.startswith("PHS") or k in ("PP.06", "IT.02"):
        return "wc"
    if k in ("KW.A.01", "KW.A.02", "PHS.05c", "SWD.01g"):
        return "pub"
    return {"zamk": "zamk", "sala": "sala", "hol": "hol", "kom": "kom", "antresola": "antresola"}.get(
        M.PROG.get(k, ("", "kom"))[1], "kom")


def draw(ax, g, fc, ec="#333", lw=0.6, alpha=1.0, z=1, hatch=None):
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    for p in gs:
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z, hatch=hatch))


def label(ax, g, txt, fs=5.2, dy=0.0):
    c = g.representative_point()
    ax.text(c.x, c.y + dy, txt, fontsize=fs, ha="center", va="center", zorder=10)


def base(ax, title):
    draw(ax, M.W_UV, "#cfcfcf", lw=0.8)
    draw(ax, M.INNER, "white", lw=0.4)
    for c, nm in ((M.CORE_A, "A"), (M.CORE_B, "B")):
        draw(ax, c, "#bdbdbd", lw=0.8, z=2)
    for cells in (M.CORE_A_CELLS, M.CORE_B_CELLS):
        for k, g in cells.items():
            fc = "#8a8a8a" if k in ("A1", "A2", "R", "P1", "P2") else ("#a9a9a9" if "klatka" in k else "#c9c9c9")
            draw(ax, g, fc, lw=0.4, z=3)
            label(ax, g, {"klatka_A": "kl. A", "klatka_B": "kl. B", "przedsionek_A": "prz. A\nMOE", "przedsionek_B": "prz. B\nMOE",
                          "szachty_B": "szachty"}.get(k, k), fs=4.6)
    ax.set_title(title, fontsize=9, loc="left")
    ax.set_xlim(-0.8, 40.8)
    ax.set_ylim(-1.6, 30.6)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=5)
    ax.set_xlabel("u [m]", fontsize=6)
    ax.set_ylabel("v [m]", fontsize=6)


fig, axs = plt.subplots(2, 1, figsize=(11.0, 17.0))
ax = axs[0]
base(ax, "Kondygnacja S (+27,30) – wariant S-3 „hol z galerią” (S-2 po weryfikacji)")
for k, g in S.items():
    draw(ax, g, COL[cat(k)], z=4)
    if k == "SWD.01":
        continue
    nm = {"KUL": "KUL – kuluar 2,2 m (EI 30)", "KW.S.01": "pasaż", "KW.S.03": "łącznik", "KW.S.02": "doj.",
          "KW.S.04": "schody", "SWD.02": "SWD.02 hol\n(2 kond. NW)"}.get(k, k)
    label(ax, g, f"{nm}\n{g.area:.1f}")
# sala
for a in ("east", "west_ramp"):
    draw(ax, aisles[a], "#f2b8e6", lw=0.4, z=5)
draw(ax, aisles["west_flat"], "#f7e8c8", lw=0.3, z=5)
for r in rows:
    draw(ax, r["band"], "#f3dcc0", lw=0.3, z=5)
    for d in r["desks"]:
        draw(ax, d, "#8b5a2b", lw=0.2, z=6)
    draw(ax, r["wc"], "#3aa655", lw=0.3, z=6)
    ax.text(*r["wc_pt"], "♿", fontsize=5, ha="center", va="center", zorder=11, color="white")
    p = r["seats"][len(r["seats"]) // 2]
    ax.text(p[0], p[1], f"R{r['k']} +{r['z']:.2f}\n{r['n']}+1", fontsize=4.6, ha="center", va="center", zorder=11)
draw(ax, M.PRES, "#4d4d4d", z=6)
draw(ax, M.LECTERN, "#c0392b", z=6)
for (u, v, t) in M.floor_seats():
    if t in ("gosc", "media", "obsluga", "PJM"):
        ax.plot(u, v, "o", ms=2.0, color={"gosc": "#1f77b4", "media": "#9467bd", "obsluga": "#555", "PJM": "#d62728"}[t], zorder=12)
ax.text(28.6, 17.7, f"SWD.01 sala obrad – płyta {S['SWD.01'].area:.1f} m²\n47 stanowisk (43 + 4 ♿)", fontsize=5.6, ha="center", zorder=12)
ax.text(31.0, 23.5, "pochylnie 5 %", fontsize=4.6, color="#a0007a", zorder=12)
ax.text(24.4, 27.7, "goście 12", fontsize=4.6, color="#1f77b4", zorder=12)
ax.text(30.3, 27.2, "media 8", fontsize=4.6, color="#9467bd", zorder=12)
ax.text(25.0, 12.95, "prezydium", fontsize=4.6, color="white", zorder=12)
# drzwi
for a_, b_, (u, v), w in M.DOORS_S:
    ax.plot(u, v, "s", ms=2.2, color="#d35400", zorder=12)
for lift, pt, d, levels in M.LIFT_DOORS:
    if any(l.startswith("S") for l in levels):
        ax.annotate("", xy=(pt[0] + d[0] * 0.9, pt[1] + d[1] * 0.9), xytext=pt,
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="#c0392b"), zorder=12)
ax.text(0.6, -1.3, "■ drzwi  → wyjście z dźwigu  ♿ stanowisko dla wózka; pas 1,35 m przy elewacjach bez antresoli (okna 1,65×4,20/5,00 bez zmian)",
        fontsize=5.5)

ax = axs[1]
base(ax, "Antresola +30,90 – zach.: górny hol radnych (bar, strefa multimedialna); wsch./środek: galeria i dojście publiczności z P1/P2")
draw(ax, M.VOID_HALL, "#eef3ff", ec="#88a", lw=0.4, z=4, hatch="////")
label(ax, M.VOID_HALL, "pustka holu", fs=5)
draw(ax, S["SWD.01"], "#fbf6ec", ec="#bbb", lw=0.4, z=4)
label(ax, S["SWD.01"], "pustka sali (h 6,85 m)", fs=6)
for k, g in A.items():
    draw(ax, g, COL[cat(k)], z=5)
    nm = {"KW.A.01": "hol P1/P2", "KW.A.02": "korytarz publiczny EI 30", "KW.A.03": "prz. A'\nMOE",
          "SWD.01g": "SWD.01g galeria\n31 + 3 ♿", "SWD.02g": "SWD.02g hol górny"}.get(k, k)
    label(ax, g, f"{nm}\n{g.area:.1f}", dy=(-2.2 if k == "SWD.01g" else 0))
for (u, v, h, t) in M.gallery_seats():
    ax.plot(u, v, "s" if t == "wozek" else "o", ms=2.6 if t == "wozek" else 1.8,
            color="#3aa655" if t == "wozek" else "#333", zorder=12)
for g in M.GAL_STEPS:
    draw(ax, g, "#e0c9a6", lw=0.3, z=6)
for a_, b_, (u, v), w in M.DOORS_ANT:
    ax.plot(u, v, "s", ms=2.2, color="#d35400", zorder=12)
for lift, pt, d, levels in M.LIFT_DOORS:
    if "ANT" in levels:
        ax.annotate("", xy=(pt[0] + d[0] * 0.9, pt[1] + d[1] * 0.9), xytext=pt,
                    arrowprops=dict(arrowstyle="->", lw=0.7, color="#c0392b"), zorder=12)
ax.text(0.6, -1.3, "kolor różowy – strefa publiczności (Wejście Obywatelskie → P1/P2 → +30,90), zielony – strefa radnych;"
        " drogi z galerii: przedsionek A (zach.) i B (korytarz)", fontsize=5.5)
plt.tight_layout()
out = os.path.join(IMG, "s2_plan.png")
plt.savefig(out, dpi=170)
print("Zapisano", os.path.relpath(out, M.ROOT))

# ------------------------------------------------------------------------------------------------
# Przekrój w płaszczyźnie linii wzroku: galeria (rząd 1 i 2, v 20,0) → prezydium (miejsce skrajne zach.) i mówca
fig, ax = plt.subplots(figsize=(10, 4.2))
H = M.Z_ANT - M.Z_S
v0 = 20.0
seats = [(M.GAL_ROWS[0][1], H + M.EYE), (M.GAL_ROWS[1][1], H + M.GAL_ROWS[1][2] + M.EYE)]
targets = [((M.F[0] - 2.25, 13.25), M.EYE, "prezydium (skrajne zach.)", "#c0392b"), ((M.F[0], M.F[1]), 1.60, "mówca 1,60", "#2c7fb8"),
           ((M.F[0] + 0.75, 13.25), M.EYE, "przewodniczący(a)", "#8e44ad")]


def s_of(u, v):   # odległość pozioma od rzędu 1 wzdłuż linii (rozwinięcie na płaszczyznę)
    return math.hypot(u - seats[0][0], v - v0) * (1 if u >= seats[0][0] else -1)


ax.add_patch(plt.Rectangle((-6.5, 0), 6.5 + 0.55, -0.35, fc="#bbb"))
ax.add_patch(plt.Rectangle((-6.0, H - 0.3), 6.55, 0.3, fc="#999"))                        # strop antresoli
ax.add_patch(plt.Rectangle((0.45, H), 0.10, M.GAL_CURB_H, fc="#555"))                      # cokół
ax.add_patch(plt.Rectangle((0.45, H + M.GAL_CURB_H), 0.04, M.GAL_GLASS_H - M.GAL_CURB_H, fc="#9ecae1", alpha=0.7))  # szkło
x_r2 = M.GAL_ROWS[1][1] - M.GAL_ROWS[0][1]
ax.add_patch(plt.Rectangle((x_r2 - 0.45, H), 0.85, M.GAL_ROWS[1][2], fc="#d9c7a6"))    # podest rzędu 2 (+0,90)
ax.add_patch(plt.Rectangle((0.25, 0), 0.30, H - 0.3, fc="#999"))                          # ściana sali pod galerią
ax.text(-3.0, 1.6, "hol dźwigów A1/A2\n(pod galerią, h 3,30)", fontsize=6, ha="center")
ax.plot([-6.5, 14], [M.H_SALA, M.H_SALA], "--", color="#777", lw=0.6)
ax.text(10.5, M.H_SALA + 0.08, "spód kratownic +6,85", fontsize=6)
for (su, sz), nm in zip(seats, ("rząd 1", "rząd 2")):
    x = s_of(su, v0)
    ax.plot(x, sz, "ko", ms=3)
    ax.text(x - 0.2, sz + 0.15, nm, fontsize=6, ha="right")
    for (T, zt, tn, c) in targets:
        xt = s_of(*T) if T[0] >= su else 0
        ax.plot([x, s_of(*T)], [sz, zt], "-", color=c, lw=0.7)
for (T, zt, tn, c) in targets:
    ax.plot(s_of(*T), zt, "o", color=c, ms=3)
    ax.text(s_of(*T), zt - (0.35 if "mówca" in tn else 0.6 if "skrajne" in tn else 0.35), tn, fontsize=6, color=c,
            ha="right" if "skrajne" in tn else "left")
for r in rows:
    # głowy radnych na drodze linii (rzut) – poglądowo na promieniu do prezydium
    pass
ax.text(-6.3, H + 0.05, "+30,90 galeria", fontsize=6)
ax.text(-6.3, 0.08, "+27,30 sala", fontsize=6)
ax.set_xlim(-6.5, 14)
ax.set_ylim(-0.5, 7.2)
ax.set_aspect("equal")
ax.set_title("Przekrój rozwinięty wzdłuż linii wzroku z galerii (miejsca przy v 20,0) – szkło 1,10 m na cokole 0,20 m;"
             " rząd 2 na +0,90", fontsize=8, loc="left")
ax.tick_params(labelsize=6)
plt.tight_layout()
out2 = os.path.join(IMG, "s2_przekroj.png")
plt.savefig(out2, dpi=170)
print("Zapisano", os.path.relpath(out2, M.ROOT))
