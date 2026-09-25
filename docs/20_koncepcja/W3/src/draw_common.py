# -*- coding: utf-8 -*-
"""Wspolne funkcje rysunkowe (matplotlib) dla wariantu W3."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Arc, Circle, Rectangle, FancyArrowPatch
from shapely.geometry import box, Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
import model_w3 as M

C_CORE = "#4a4a4a"
C_INS = "#f3e6b3"
C_PART = "#9a9a9a"
C_GLASS = "#3b7dd8"
C_TXT = "#1a1a1a"
C_FURN = "#9aa3ad"
C_DIM = "#333333"


def fmt(v, nd=2):
    return f"{v:.{nd}f}".replace(".", ",")


def draw_poly(ax, geom, **kw):
    if geom.is_empty:
        return
    geoms = geom.geoms if hasattr(geom, "geoms") else [geom]
    for g in geoms:
        if g.geom_type != "Polygon":
            continue
        ax.add_patch(MPoly(list(g.exterior.coords), closed=True, **kw))
        for hole in g.interiors:
            ax.add_patch(MPoly(list(hole.coords), closed=True, facecolor="white", edgecolor=kw.get("edgecolor", "none"), lw=kw.get("lw", 0.5)))


def core_poly(w):
    t = w["typ"]
    half = {"SZ1": 0.09, "SZL": 0.09, "SW18": 0.09, "SWG": 0.09, "SC12": 0.06, "DZ12": 0.06, "DZL": 0.05, "SK": 0.02, "LAM": 0.02}[t]
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    e1, e2 = [min(e, half) if e > 0 else 0.0 for e in w["ext"]]
    ax_, ay_ = x1 - ux * e1, y1 - uy * e1
    bx, by = x2 + ux * e2, y2 + uy * e2
    return Polygon([(ax_ + nx * half, ay_ + ny * half), (bx + nx * half, by + ny * half),
                    (bx - nx * half, by - ny * half), (ax_ - nx * half, ay_ - ny * half)])


def draw_walls(ax, kond):
    walls = [w for w in M.SCIANY if w["kond"] == kond]
    cuts = unary_union([M.opening_cut(o) for o in M.OTWORY if M.wall_by_id(o["sciana"])["kond"] == kond])
    full_ext = unary_union([M.wall_poly(w) for w in walls if w["typ"] in ("SZ1", "SZL", "SWG")]).difference(cuts)
    full_int = unary_union([M.wall_poly(w) for w in walls if w["typ"] in ("SW18",)]).difference(cuts)
    part = unary_union([M.wall_poly(w) for w in walls if w["typ"] in ("DZ12", "SC12")]).difference(cuts)
    core = unary_union([core_poly(w) for w in walls if w["typ"] in ("SZ1", "SW18", "SWG")]).difference(cuts)
    light = unary_union([core_poly(w) for w in walls if w["typ"] == "SZL"]).difference(cuts)
    draw_poly(ax, full_ext, facecolor=C_INS, edgecolor="black", lw=0.6, zorder=5)
    draw_poly(ax, full_int, facecolor="#d9d9d9", edgecolor="black", lw=0.6, zorder=5)
    draw_poly(ax, part, facecolor="#cfcfcf", edgecolor="black", lw=0.5, zorder=5)
    draw_poly(ax, core, facecolor=C_CORE, edgecolor="none", zorder=6)
    lekkie = unary_union([M.wall_poly(w) for w in walls if w["typ"] == "DZL"]).difference(cuts)
    draw_poly(ax, lekkie, facecolor="#f4f4f4", edgecolor="black", lw=0.5, zorder=5, hatch="....")
    szklo = unary_union([M.wall_poly(w) for w in walls if w["typ"] == "SK"]).difference(cuts)
    draw_poly(ax, szklo, facecolor="#cfe3f7", edgecolor=C_GLASS, lw=0.8, zorder=5)
    for w in walls:
        if w["typ"] == "LAM":
            (x1, y1), (x2, y2) = w["p1"], w["p2"]
            L = math.hypot(x2 - x1, y2 - y1); n = int(L / 0.12)
            for k in range(n + 1):
                px, py = x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n
                ax.add_patch(Rectangle((px - 0.02, py - 0.04) if abs(x2 - x1) < 1e-9 else (px - 0.02, py - 0.04), 0.04, 0.08,
                                       facecolor="#a07a3c", edgecolor="none", zorder=6))
    draw_poly(ax, light, facecolor="#a08c5a", edgecolor="none", zorder=6, hatch="////")


def wall_geom(o):
    w = M.wall_by_id(o["sciana"])
    t = M.TYPY[w["typ"]]
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    horiz = abs(y2 - y1) < 1e-9
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    # lica: lewe = os + n*L, prawe = os - n*R ; wyznacz wsp. lic w osi prostopadlej
    if horiz:
        c = y1
        f1, f2 = c + ny * t["L"], c - ny * t["R"]
    else:
        c = x1
        f1, f2 = c + nx * t["L"], c - nx * t["R"]
    lo, hi = min(f1, f2), max(f1, f2)
    return horiz, c, lo, hi


def draw_openings(ax, kond):
    for o in M.OTWORY:
        w = M.wall_by_id(o["sciana"])
        if w["kond"] != kond:
            continue
        horiz, c, lo, hi = wall_geom(o)
        a, b = o["a"], o["b"]

        def P(s, t):  # s wzdluz sciany, t w poprzek
            return (s, t) if horiz else (t, s)

        typ = o["typ"]
        if typ in ("okno", "fasada", "boks"):
            mid = (lo + hi) / 2
            for off in (-0.04, 0.04):
                p1, p2 = P(a, mid + off), P(b, mid + off)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=C_GLASS, lw=0.9, zorder=7)
            for s in (a, b):  # oscieza
                p1, p2 = P(s, lo), P(s, hi)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.6, zorder=7)
            # parapet zewn.
            p1, p2 = P(a, lo), P(b, lo)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.4, zorder=7)
            p1, p2 = P(a, hi), P(b, hi)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.4, zorder=7)
            if o["kw"] > 1:
                step = (b - a) / o["kw"]
                pods = o["podz"] or [a + k * step for k in range(1, o["kw"])]
                for s in pods:
                    ax.add_patch(Rectangle(P(s - 0.06, c - 0.06) if horiz else (c - 0.06, s - 0.06), 0.12, 0.12,
                                           facecolor="black", zorder=8))
                edges = [a] + list(pods) + [b]
                for k in o["hs"]:  # drzwi HS w kwaterach wskazanych w modelu
                        s0, s1 = edges[k - 1], edges[k]
                        step = s1 - s0
                        p1, p2 = P(s0 + 0.1, mid + 0.14), P(s0 + step * 0.55, mid + 0.14)
                        ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", lw=0.7, color=C_GLASS), zorder=8)
                        tp = P(s0 + step / 2, mid - 0.45)
                        ax.text(*tp, "HS", fontsize=5.5, color=C_GLASS, ha="center", va="center", zorder=8)
        elif typ in ("drzwi", "drzwi_zewn"):
            sgn = 1 if o["kier"][0] == "+" else -1
            face = hi if sgn > 0 else lo
            hinge = a if o["zaw"] == "a" else b
            other = b if o["zaw"] == "a" else a
            wd = b - a
            p_h = P(hinge, face)
            p_open = P(hinge, face + sgn * wd)
            ax.plot([p_h[0], p_open[0]], [p_h[1], p_open[1]], color="black", lw=0.9, zorder=8)
            # luk
            cx, cy = p_h
            ang_open = math.degrees(math.atan2(p_open[1] - cy, p_open[0] - cx))
            p_c = P(other, face)
            ang_cl = math.degrees(math.atan2(p_c[1] - cy, p_c[0] - cx))
            a1, a2 = sorted([ang_open, ang_cl])
            if a2 - a1 > 180:
                a1, a2 = a2, a1 + 360
            ax.add_patch(Arc((cx, cy), 2 * wd, 2 * wd, theta1=a1, theta2=a2, color="black", lw=0.5, ls="-", zorder=8))
            for s in (a, b):
                p1, p2 = P(s, lo), P(s, hi)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.6, zorder=7)
        elif typ == "brama":
            mid = (lo + hi) / 2
            p1, p2 = P(a, mid), P(b, mid)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=1.2, ls=(0, (4, 2)), zorder=8)
            p1, p2 = P(a, lo - 0.5), P(b, lo - 0.5)
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.5, ls=":", zorder=8)
            for s in (a, b):
                p1, p2 = P(s, lo), P(s, hi)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.6, zorder=7)
        elif typ == "otwor":
            for s in (a, b):
                p1, p2 = P(s, lo), P(s, hi)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.6, zorder=7)
            for t in (lo, hi):
                p1, p2 = P(a, t), P(b, t)
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black", lw=0.4, ls=(0, (3, 2)), zorder=7)


def label_rooms(ax, kond, fs=7.0, offsets=None):
    offsets = offsets or {}
    for r in M.POMIESZCZENIA:
        if r["kond"] != kond:
            continue
        p = r["poly"].representative_point() if r["id"] not in offsets else None
        x, y = (p.x, p.y) if p is not None else offsets[r["id"]]
        if r["id"] in offsets and p is not None:
            x, y = offsets[r["id"]]
        nm = r["nazwa"]
        ax.text(x, y, f"{r['id']}\n{nm}\n{fmt(M.room_area(r))} m²", fontsize=fs, ha="center", va="center",
                color=C_TXT, zorder=20, linespacing=1.15,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.8))


def dim_h(ax, x1, x2, y, txt=None, fs=6.5, ext_from=None, above=True):
    ax.plot([x1, x2], [y, y], color=C_DIM, lw=0.5, zorder=9)
    for x in (x1, x2):
        ax.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color=C_DIM, lw=0.8, zorder=9)
        if ext_from is not None:
            ax.plot([x, x], [ext_from, y + (0.1 if y > ext_from else -0.1)], color=C_DIM, lw=0.3, zorder=9)
    t = txt if txt is not None else fmt(abs(x2 - x1))
    ax.text((x1 + x2) / 2, y + (0.08 if above else -0.08), t, fontsize=fs, ha="center", va="bottom" if above else "top", color=C_DIM, zorder=9)


def dim_v(ax, y1, y2, x, txt=None, fs=6.5, ext_from=None, left=True):
    ax.plot([x, x], [y1, y2], color=C_DIM, lw=0.5, zorder=9)
    for y in (y1, y2):
        ax.plot([x - 0.08, x + 0.08], [y - 0.08, y + 0.08], color=C_DIM, lw=0.8, zorder=9)
        if ext_from is not None:
            ax.plot([ext_from, x + (0.1 if x > ext_from else -0.1)], [y, y], color=C_DIM, lw=0.3, zorder=9)
    t = txt if txt is not None else fmt(abs(y2 - y1))
    ax.text(x + (-0.08 if left else 0.08), (y1 + y2) / 2, t, fontsize=fs, ha="right" if left else "left", va="center",
            rotation=90, color=C_DIM, zorder=9)


def dim_chain_h(ax, xs, y, ext_from=None, fs=6.0):
    xs = sorted(xs)
    for a, b in zip(xs[:-1], xs[1:]):
        dim_h(ax, a, b, y, fs=fs, ext_from=ext_from)


def dim_chain_v(ax, ys, x, ext_from=None, fs=6.0):
    ys = sorted(ys)
    for a, b in zip(ys[:-1], ys[1:]):
        dim_v(ax, a, b, x, fs=fs, ext_from=ext_from)


def axes_bubbles(ax, xs_names, ys_names, y_bot, y_top, x_left, x_right):
    for n in xs_names:
        x = M.OSIE_X[n]
        ax.plot([x, x], [y_bot + 0.35, y_top - 0.35], color="#c04040", lw=0.35, ls=(0, (8, 2, 1, 2)), zorder=1)
        for yy in (y_bot, y_top):
            ax.add_patch(Circle((x, yy), 0.33, facecolor="white", edgecolor="#c04040", lw=0.7, zorder=10))
            ax.text(x, yy, n, fontsize=6.5, ha="center", va="center", color="#c04040", zorder=11)
    for n in ys_names:
        y = M.OSIE_Y[n]
        ax.plot([x_left + 0.35, x_right - 0.35], [y, y], color="#c04040", lw=0.35, ls=(0, (8, 2, 1, 2)), zorder=1)
        for xx in (x_left, x_right):
            ax.add_patch(Circle((xx, y), 0.33, facecolor="white", edgecolor="#c04040", lw=0.7, zorder=10))
            ax.text(xx, y, n, fontsize=6.5, ha="center", va="center", color="#c04040", zorder=11)


def north_arrow(ax, x, y, s=1.0):
    ax.add_patch(FancyArrowPatch((x, y - s), (x, y + s), arrowstyle="-|>", mutation_scale=14, color="black", lw=1.2, zorder=30))
    ax.text(x, y + s + 0.25, "N", fontsize=10, ha="center", va="bottom", fontweight="bold", zorder=30)


def furn(ax, x1, y1, x2, y2, lbl=None, fs=5, fc="none", ls="-"):
    ax.add_patch(Rectangle((x1, y1), x2 - x1, y2 - y1, facecolor=fc, edgecolor=C_FURN, lw=0.6, ls=ls, zorder=4))
    if lbl:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, lbl, fontsize=fs, ha="center", va="center", color="#6d7680", zorder=4)


def furn_circle(ax, x, y, r, lbl=None, fs=5):
    ax.add_patch(Circle((x, y), r, facecolor="none", edgecolor=C_FURN, lw=0.6, zorder=4))
    if lbl:
        ax.text(x, y, lbl, fontsize=fs, ha="center", va="center", color="#6d7680", zorder=4)


def outline_dashed(ax, geom, color="#555555", ls=(0, (5, 3)), lw=0.8, z=3, label=None):
    geoms = geom.geoms if hasattr(geom, "geoms") else [geom]
    for g in geoms:
        xs, ys = g.exterior.xy
        ax.plot(xs, ys, color=color, ls=ls, lw=lw, zorder=z)


def title(ax, fig, t, sub=None):
    fig.suptitle(t, fontsize=13, fontweight="bold", x=0.02, ha="left", y=0.985)
    if sub:
        fig.text(0.02, 0.945, sub, fontsize=8.5, ha="left", va="top", color="#333333")
