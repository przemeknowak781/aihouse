"""Rysunki do „Obliczeń statycznych” (matplotlib, PNG 150 dpi): schematy statyczne, mapy momentów i ugięć płyt (MES),
wykresy sił wewnętrznych belek i schodów, profile obciążeń ścian i ław, plan fundamentów, zaspy śnieżne.

Kolory: atrament #0b0b0b / #52514e (tekst, konstrukcja), skale sekwencyjne jednego odcienia (niebieska — momenty dolne,
ugięcia; pomarańczowa — momenty górne), wykresy M/V: obwiednia max (niebieski) / min (czerwony).
"""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon, Rectangle  # noqa: E402

INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#8a8984"
GRID = "#dcdbd6"
BLUE = "#2a78d6"
RED = "#e34948"
ORANGE = "#eb6834"
FILL = "#f0efec"
SEQ_BLUE = LinearSegmentedColormap.from_list("seq_blue", ["#f4f8fd", "#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])
SEQ_ORANGE = LinearSegmentedColormap.from_list("seq_orange", ["#fdf3ee", "#f9d2c1", "#f3a383", "#eb6834", "#b8461c", "#7a2c10"])

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": INK2, "axes.labelcolor": INK,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.titlesize": 9.5, "axes.titleweight": "bold",
                     "axes.titlecolor": INK, "figure.dpi": 150, "savefig.dpi": 150, "axes.spines.top": False,
                     "axes.spines.right": False})


def _pl(x, nd=2):
    return f"{x:.{nd}f}".replace(".", ",").replace("-", "−")


def _save(fig, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _ring(ax, geom, **kw):
    polys = [geom] if geom.geom_type == "Polygon" else list(getattr(geom, "geoms", []))
    for pg in polys:
        x, y = pg.exterior.xy
        ax.plot(x, y, **kw)
        for h in pg.interiors:
            x, y = h.xy
            ax.plot(x, y, **kw)


def _podpory(ax, g, lw=3.2):
    for s in g.podp_l:
        x, y = s.linia.xy
        if s.rodzaj == "sciana":
            ax.plot(x, y, color=INK2, lw=lw, solid_capstyle="butt", zorder=5)
        else:
            ax.plot(x, y, color=INK, lw=1.6, ls=(0, (5, 2)), zorder=5)
        mx, my = s.linia.interpolate(0.5, normalized=True).coords[0]
        ax.annotate(s.id, (mx, my), xytext=(3, 3), textcoords="offset points", fontsize=6.5, color=INK2, zorder=6)
    for s in g.podp_p:
        ax.add_patch(Rectangle((s.xy[0] - 0.08, s.xy[1] - 0.08), 0.16, 0.16, fc=INK, ec=INK, zorder=6))
        ax.annotate(s.id, s.xy, xytext=(4, -9), textcoords="offset points", fontsize=6.5, color=INK)


# ==================================================================================================
# Płyty
# ==================================================================================================
def rys_plyta(an, g, path: Path) -> list:
    """Schemat statyczny płyty (pola, podpory, obciążenia liniowe) i mapy: M dół/góra (Wood–Armer), ugięcie SLS."""
    fe = g.fe
    out = []
    # (a) schemat
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    _ring(ax, g.poly, color=INK, lw=0.9)
    for e in g.el:
        _ring(ax, e.poly_full, color=MUTED, lw=0.5, ls=":")
    for c in g.komorki:
        cx, cy = c["rect"].representative_point().coords[0]
        ax.text(cx, cy, f"{c['id']}\n{_pl(c['lx'])}×{_pl(c['ly'])} m\n{c['brzegi']}", ha="center", va="center",
                fontsize=7, color=INK, bbox=dict(fc="white", ec=GRID, lw=0.5, boxstyle="round,pad=0.25"))
    _podpory(ax, g)
    for ln, cs, q, _ in g.linie:
        if ln is None:
            continue
        x, y = ln.xy
        ax.plot(x, y, color=ORANGE, lw=1.4, zorder=4)
    ax.set_aspect("equal")
    ax.set_title(f"Schemat statyczny płyty {g.nazwa} (rzut; poziom +{_pl(g.wierzch, 3)} m)", loc="left")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color=INK2, lw=3.2, label="ściana nośna (podpora liniowa)"),
                       Line2D([], [], color=INK, lw=1.6, ls=(0, (5, 2)), label="belka (podpora liniowa)"),
                       Line2D([], [], marker="s", color=INK, lw=0, label="słup (podpora punktowa)"),
                       Line2D([], [], color=ORANGE, lw=1.4, label="obciążenie liniowe (ścianki, schody)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2, frameon=False, fontsize=7)
    ax.grid(color=GRID, lw=0.4)
    p1 = Path(path).with_name(Path(path).stem + "_schemat.png")
    out.append((_save(fig, p1), f"Schemat statyczny płyty {g.nazwa}: pola (P — wymiary, warunki brzegowe x=0/x=l_x/y=0/y=l_y: "
                                "S — podparcie swobodne, U — ciągłość/utwierdzenie, W — brzeg swobodny/niepełny), podpory."))
    # (b) mapy
    verts = []
    for (x0, y0), (a, b) in zip(fe.el_x0, fe.el_ab):
        verts.append([(x0, y0), (x0 + a, y0), (x0 + a, y0 + b), (x0, y0 + b)])
    env = g.env
    dol = np.maximum(env["dol_x"], env["dol_y"])
    gora = np.minimum(env["gora_x"], env["gora_y"])
    wq = env["qp"].w
    w_el = wq[fe.el_nodes].mean(axis=1) * 1000
    fig, axs = plt.subplots(1, 3, figsize=(10.5, 3.9))
    for ax, val, cmap, tyt, lab in ((axs[0], dol, SEQ_BLUE, "Moment dolny max(m_x*, m_y*)", "kNm/m"),
                                    (axs[1], -gora, SEQ_ORANGE, "Moment górny |min(m_x*, m_y*)|", "kNm/m"),
                                    (axs[2], w_el, SEQ_BLUE, "Ugięcie sprężyste (quasi-stała)", "mm")):
        pc = PolyCollection(verts, array=val, cmap=cmap, edgecolors="face", linewidths=0.2)
        ax.add_collection(pc)
        _ring(ax, g.poly, color=INK, lw=0.7)
        for s in g.podp_l:
            x, y = s.linia.xy
            ax.plot(x, y, color=INK2, lw=1.4)
        for s in g.podp_p:
            ax.plot(*s.xy, "s", color=INK, ms=4)
        ax.set_aspect("equal")
        ax.autoscale_view()
        ax.set_title(tyt, loc="left", fontsize=8.5)
        k = int(np.argmax(val))
        cx0 = np.mean(fe.el_c[:, 0])
        ha = "right" if fe.el_c[k][0] > cx0 else "left"
        ax.annotate(f"max {_pl(val[k], 1)}", fe.el_c[k], xytext=(-6 if ha == "right" else 6, 10), textcoords="offset points",
                    fontsize=7, ha=ha, color=INK, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5),
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.6))
        cb = fig.colorbar(pc, ax=ax, shrink=0.8, pad=0.02)
        cb.set_label(lab, fontsize=7)
        cb.ax.tick_params(labelsize=6.5)
        ax.tick_params(labelsize=6.5)
    fig.suptitle(f"Płyta {g.nazwa} — obwiednia ULS (Wood–Armer) i ugięcie sprężyste SLS", x=0.01, ha="left", fontsize=9.5,
                 fontweight="bold", color=INK)
    fig.tight_layout()
    p2 = Path(path).with_name(Path(path).stem + "_mapy.png")
    out.append((_save(fig, p2), f"Płyta {g.nazwa}: momenty wymiarujące (obwiednia kombinacji 6.10a/b, obciążeń "
                                "szachownicowych i sytuacji wyjątkowej) oraz ugięcie sprężyste od kombinacji quasi-stałej "
                                "(bez zarysowania i pełzania — te w obliczeniach 7.4.3)."))
    return out


# ==================================================================================================
# Belki
# ==================================================================================================
def _schemat_belki(ax, L, pods, qopis="q"):
    ax.plot([0, L], [0, 0], color=INK, lw=2.4, solid_capstyle="butt")
    for s, *_ in pods:
        ax.add_patch(MplPolygon([[s, 0], [s - 0.09, -0.16], [s + 0.09, -0.16]], closed=True, fc="white", ec=INK, lw=1))
        ax.plot([s - 0.13, s + 0.13], [-0.2, -0.2], color=INK, lw=0.8)
    for x in np.linspace(0, L, max(int(L / 0.35), 4)):
        ax.annotate("", (x, 0.02), (x, 0.32), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=0.7, mutation_scale=6))
    ax.plot([0, L], [0.32, 0.32], color=BLUE, lw=0.8)
    ax.text(L / 2, 0.38, qopis, ha="center", va="bottom", fontsize=7.5, color=INK)
    ax.set_ylim(-0.35, 0.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)


def _wykres(ax, x, vmax, vmin, jedn, tyt, odwr=True):
    ax.axhline(0, color=INK2, lw=0.7)
    ax.fill_between(x, 0, vmax, color=BLUE, alpha=0.18, lw=0)
    ax.plot(x, vmax, color=BLUE, lw=1.4, label="obwiednia max")
    if vmin is not None:
        ax.fill_between(x, 0, vmin, color=RED, alpha=0.15, lw=0)
        ax.plot(x, vmin, color=RED, lw=1.4, label="obwiednia min")
    for arr in (vmax, vmin) if vmin is not None else (vmax,):
        k = int(np.argmax(np.abs(arr)))
        if abs(arr[k]) > 1e-6:
            ax.annotate(f"{_pl(arr[k])} {jedn}", (x[k], arr[k]), xytext=(4, 4 if arr[k] > 0 else -10), textcoords="offset points",
                        fontsize=7, color=INK)
    if odwr:
        ax.invert_yaxis()
    ax.set_ylabel(jedn)
    ax.set_title(tyt, loc="left", fontsize=8.5)
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")


def rys_belka(belka, pods, rozw, Ms, Vs, bid, path: Path) -> list:
    """Schemat belki i obwiednie M, V."""
    x = belka.x
    L = belka.L
    fig, axs = plt.subplots(3, 1, figsize=(7.0, 5.6), sharex=True, gridspec_kw={"height_ratios": [0.8, 1.2, 1.2]})
    gq = sum(r.R.sum() for c, r in rozw.items() if c == "G")
    _schemat_belki(axs[0], L, pods, f"q(x): reakcje płyty (MES) + ciężar własny; ΣG_k = {_pl(gq, 1)} kN")
    axs[0].set_title(f"Belka {bid} — schemat statyczny (L = {_pl(L, 3)} m)", loc="left")
    _wykres(axs[1], x, Ms.max(0), Ms.min(0), "kNm", "Moment zginający M_Ed (obwiednia ULS)")
    Vmax = np.max(np.array([v for v in Vs]), axis=0)
    _wykres(axs[2], x, Vmax, None, "kN", "|V_Ed| (obwiednia ULS)", odwr=False)
    axs[2].set_xlabel("x [m]")
    fig.tight_layout()
    return [(_save(fig, path), f"Belka {bid}: schemat statyczny i obwiednie sił wewnętrznych (M dodatni — rozciąganie dołem).")]


# ==================================================================================================
# Schody
# ==================================================================================================
def rys_schody(wyn, odc, path: Path) -> list:
    """Widok boczny płyty schodowej i obwiednia M."""
    fig, axs = plt.subplots(2, 1, figsize=(7.0, 4.6), sharex=True, gridspec_kw={"height_ratios": [1.2, 1]})
    ax = axs[0]
    z = 0.0
    tg = math.tan(math.radians(wyn.alfa))
    xs, zs = [], []
    for o in odc:
        if o.typ == "bieg":
            xs += [o.x0, o.x1]
            zs += [z, z + (o.x1 - o.x0) * tg]
            z = zs[-1]
        else:
            xs += [o.x0, o.x1]
            zs += [z, z]
    ax.plot(xs, zs, color=INK, lw=2.2)
    zb = np.array(zs) - wyn.h / math.cos(math.radians(wyn.alfa))
    ax.fill_between(xs, zb, zs, color=FILL, lw=0)
    for xx in (odc[0].x0, odc[-1].x1):
        zz = np.interp(xx, xs, zs) - 0.2
        ax.add_patch(MplPolygon([[xx, zz], [xx - 0.08, zz - 0.14], [xx + 0.08, zz - 0.14]], closed=True, fc="white", ec=INK))
    ax.set_aspect("equal")
    ax.set_title(f"{wyn.nazwa} — schemat (widok boczny; L = {_pl(wyn.L, 3)} m, α = {_pl(wyn.alfa, 1)}°, h = "
                 f"{_pl(wyn.h * 100, 0)} cm)", loc="left", fontsize=8.5)
    ax.set_ylabel("z [m]")
    ax.grid(color=GRID, lw=0.4)
    ob = wyn.obwiednia
    _wykres(axs[1], ob.x, ob.M_max, None, "kNm/m", "Moment M_Ed (obwiednia 6.10a/b)")
    axs[1].set_xlabel("x — rzut poziomy [m]")
    fig.tight_layout()
    return [(_save(fig, path), f"{wyn.nazwa}: schemat statyczny płyty schodowej i obwiednia momentów zginających.")]


# ==================================================================================================
# Ściany
# ==================================================================================================
def rys_sciana(w, pr, path: Path) -> list:
    """Widok ściany z otworami i profile obciążeń liniowych (góra/dół)."""
    fig, axs = plt.subplots(2, 1, figsize=(7.0, 4.8), sharex=True, gridspec_kw={"height_ratios": [1, 1.1]})
    ax = axs[0]
    ax.add_patch(Rectangle((0, w.z_od), w.L, w.z_do - w.z_od, fc=FILL, ec=INK, lw=1))
    for o in pr["otw"]:
        ax.add_patch(Rectangle((o.s0, o.z0), o.s1 - o.s0, o.z1 - o.z0, fc="white", ec=INK2, lw=0.8))
        ax.text((o.s0 + o.s1) / 2, (o.z0 + o.z1) / 2, o.id, ha="center", va="center", fontsize=6.5, color=INK2)
    ax.set_xlim(-0.2, w.L + 0.2)
    ax.set_ylim(w.z_od - 0.15, w.z_do + 0.15)
    ax.set_ylabel("z [m]")
    ax.set_title(f"Ściana {w.id} — widok (od punktu początkowego osi)", loc="left")
    ax.grid(color=GRID, lw=0.4)
    ax = axs[1]
    d = pr["dol"]
    top = pr["top_s"]
    g_top = top.srednia_ruchoma(top.get("G") + pr["top_a"].get("G"), 0.5)
    q_top = top.srednia_ruchoma(sum((top.get(c) + pr["top_a"].get(c)) for c in ("QA", "S2", "H") if c in top.q or c in pr["top_a"].q)
                                if any(c in top.q or c in pr["top_a"].q for c in ("QA", "S2", "H")) else np.zeros_like(top.s), 0.5)
    ax.plot(top.s, g_top, color=INK2, lw=1.3, label="G_k — góra ściany (śr. 0,5 m)")
    ax.plot(top.s, q_top, color=BLUE, lw=1.3, label="Q_k — góra (użytkowe/śnieg)")
    ax.plot(d.s, d.srednia_ruchoma(d.get("G"), 0.5), color=ORANGE, lw=1.3, label="G_k — dół (po przekazaniu na filarki)")
    ax.set_ylabel("kN/m")
    ax.set_xlabel("s [m]")
    ax.legend(fontsize=6.5, frameon=False, loc="upper right")
    ax.grid(color=GRID, lw=0.4)
    ax.set_title("Obciążenia liniowe wzdłuż ściany (charakterystyczne)", loc="left", fontsize=8.5)
    fig.tight_layout()
    return [(_save(fig, path), f"Ściana {w.id}: widok z otworami i rozkład obciążeń charakterystycznych wzdłuż osi.")]


def rys_slup(cid, L, NEd, path: Path) -> list:
    """Schemat słupa (przegubowo zamocowanego)."""
    fig, ax = plt.subplots(figsize=(2.6, 3.6))
    ax.plot([0, 0], [0, L], color=INK, lw=2.4)
    for yy, s in ((0, 1), (L, -1)):
        ax.add_patch(MplPolygon([[0, yy], [-0.12, yy - s * 0.2], [0.12, yy - s * 0.2]], closed=True, fc="white", ec=INK))
    ax.annotate("", (0, L + 0.02), (0, L + 0.6), arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.2))
    ax.text(0.08, L + 0.35, f"N_Ed = {_pl(NEd, 1)} kN", fontsize=7.5, color=INK)
    ax.text(0.15, L / 2, f"L = L_cr = {_pl(L, 2)} m", fontsize=7.5, color=INK, rotation=90, va="center")
    ax.set_xlim(-0.8, 0.8)
    ax.set_ylim(-0.4, L + 0.8)
    ax.axis("off")
    ax.set_title(f"Słup {cid} — schemat", loc="left")
    return [(_save(fig, path), f"Słup {cid}: schemat statyczny (przegubowo-przesuwny, układ usztywniony).")]


# ==================================================================================================
# Fundamenty
# ==================================================================================================
def rys_lawa(fid, B, h, tw, D, prof, path: Path) -> list:
    """Przekrój ławy i rozkład obciążenia wzdłuż ławy."""
    fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.2), gridspec_kw={"width_ratios": [1, 1.7]})
    ax = axs[0]
    ax.add_patch(Rectangle((-B / 2, 0), B, h, fc=FILL, ec=INK, lw=1.1))
    ax.add_patch(Rectangle((-tw / 2, h), tw, D - h + 0.25, fc="#e4e2dc", ec=INK, lw=1.0))
    ax.plot([-B / 2 - 0.4, B / 2 + 0.4], [D, D], color=INK2, lw=0.9, ls="--")
    ax.text(B / 2 + 0.05, D + 0.03, "teren / posadzka", fontsize=6.5, color=INK2)
    ax.annotate("", (-B / 2, -0.08), (B / 2, -0.08), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
    ax.text(0, -0.17, f"B = {_pl(B * 100, 0)} cm", ha="center", fontsize=7)
    ax.annotate("", (B / 2 + 0.28, 0), (B / 2 + 0.28, D), arrowprops=dict(arrowstyle="<->", color=INK2, lw=0.7))
    ax.text(B / 2 + 0.31, D / 2, f"D = {_pl(D, 2)} m", fontsize=7, rotation=90, va="center")
    ax.text(0, h / 2, f"h = {_pl(h * 100, 0)} cm", ha="center", va="center", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xlim(-B / 2 - 0.5, B / 2 + 0.55)
    ax.set_ylim(-0.3, D + 0.4)
    ax.axis("off")
    ax.set_title(f"Ława {fid} — przekrój", loc="left")
    ax = axs[1]
    ax.plot(prof.s, prof.srednia_ruchoma(prof.get("G"), 1.0), color=INK2, lw=1.3, label="G_k (śr. 1 m)")
    q = sum(prof.get(c) for c in prof.przypadki() if c in ("QA", "S2", "H"))
    if isinstance(q, np.ndarray):
        ax.plot(prof.s, prof.srednia_ruchoma(q, 1.0), color=BLUE, lw=1.3, label="Q_k (śr. 1 m)")
    ax.set_xlabel("s [m]")
    ax.set_ylabel("kN/m")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=6.5, frameon=False)
    ax.set_title("Obciążenie ławy (charakterystyczne)", loc="left", fontsize=8.5)
    fig.tight_layout()
    return [(_save(fig, path), f"Ława {fid}: przekrój poprzeczny i rozkład obciążenia wzdłuż ławy.")]


def rys_fundamenty(an, path: Path) -> list:
    """Rzut fundamentów z wykorzystaniem nośności."""
    m = an.m
    fig, ax = plt.subplots(figsize=(7.2, 5.4))
    k0 = m.kondygnacje[0].id if m.kondygnacje else None
    if k0:
        for w in m.sciany(k0):
            try:
                _ring(ax, w.polygon, color=MUTED, lw=0.5)
            except Exception:  # noqa: BLE001
                pass
    etas = {p.ident: p.wykorzystanie for p in an.pos_fund}
    for el in m.fundamenty().get("elementy") or []:
        fid = str(el.get("id"))
        if "os" in el:
            (x0, y0), (x1, y1) = el["os"][0], el["os"][1]
            L = math.hypot(x1 - x0, y1 - y0)
            ux, uy = ((x1 - x0) / L, (y1 - y0) / L) if L else (1, 0)
            b = float(el["b"])
            e = b / 2
            nx, ny = -uy, ux
            pts = [(x0 - ux * e + nx * b / 2, y0 - uy * e + ny * b / 2), (x1 + ux * e + nx * b / 2, y1 + uy * e + ny * b / 2),
                   (x1 + ux * e - nx * b / 2, y1 + uy * e - ny * b / 2), (x0 - ux * e - nx * b / 2, y0 - uy * e - ny * b / 2)]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        else:
            pts = el["obrys"]
            cx, cy = np.mean(np.asarray(pts), axis=0)
        eta = etas.get(fid, 0)
        ax.add_patch(MplPolygon(pts, closed=True, fc=FILL, ec=INK, lw=0.9))
        P = np.asarray(pts, float)
        maly = max(np.ptp(P[:, 0]), np.ptp(P[:, 1])) < 2.0
        ax.annotate(f"{fid}\nη = {_pl(eta * 100, 0)}%" + (" ✗" if eta > 1 else ""), (cx, cy),
                    xytext=(0, 26) if maly else (0, 0), textcoords="offset points", ha="center", va="center", fontsize=6.8,
                    color=INK, bbox=dict(fc="white", ec=GRID, lw=0.4, boxstyle="round,pad=0.2"),
                    arrowprops=dict(arrowstyle="-", color=INK2, lw=0.5) if maly else None)
    for c in m.slupy():
        ax.plot(*c["xy"], "s", color=INK, ms=4)
    ax.set_aspect("equal")
    ax.grid(color=GRID, lw=0.4)
    ax.set_title("Rzut fundamentów — elementy i maksymalne wykorzystanie nośności η", loc="left")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.autoscale_view()
    return [(_save(fig, path), "Rzut fundamentów: oznaczenia elementów i maks. wykorzystanie η (✗ — warunek niespełniony, "
                               "w tym głębokość posadowienia).")]


def rys_zaspy(sniegi: list, path: Path) -> list:
    """Profile zasp śnieżnych s(x)."""
    if not sniegi:
        return []
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    cols = [BLUE, ORANGE, "#1baf7a", "#4a3aa7"]
    for k, sn in enumerate(sniegi[:4]):
        L = max(sn.l_s * 1.3, 6.0)
        x = np.linspace(0, L, 200)
        ax.plot(x, sn.profil(x), color=cols[k], lw=1.5, label=sn.nazwa.replace("Śnieg — ", "").split(" — ")[0][:60])
    ax.set_xlabel("odległość od przeszkody / uskoku [m]")
    ax.set_ylabel("s [kN/m²]")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=6.3, frameon=False, loc="upper right")
    ax.set_title("Zaspy śnieżne — wartości charakterystyczne", loc="left")
    fig.tight_layout()
    return [(_save(fig, path), "Rozkłady obciążenia śniegiem w zaspach (PN-EN 1991-1-3 p. 5.3.6, 6.2, zał. B).")]
