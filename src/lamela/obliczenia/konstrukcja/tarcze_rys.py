"""Rysunki pozycji tarczowej (matplotlib, PNG 150 dpi): schemat statyczny z obciążeniami, mapy naprężeń MES, naprężenia
główne z trajektoriami, model kratownicowy STM z siłami, siły w pasach (MES vs STM) i kontrola równowagi, ugięcia
i reakcje, szkic zbrojenia. Styl jak w :mod:`.rysunki` (atrament, skale jednego odcienia, rozbieżne dla znaku).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np

from .rysunki import BLUE, FILL, GRID, INK, INK2, MUTED, ORANGE, RED, SEQ_BLUE, SEQ_ORANGE, _pl, _save, plt  # noqa: F401
from .tarcze_mes import ObcLiniowe, ObcProfil, ObcSkupione, glowne
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Polygon as MplPolygon, Rectangle  # noqa: E402
from matplotlib.tri import Triangulation  # noqa: E402

GREEN = "#2f8a4c"
DIV = LinearSegmentedColormap.from_list("div_tarcza", ["#0d366b", "#3987e5", "#cde2fb", "#f7f7f5", "#f9d2c1", "#eb6834", "#7a2c10"])


def _ladna(v: float) -> float:
    """Zaokrąglenie w górę do „ładnej” wartości (1, 1,5, 2, 2,5, 3, 4, 5, 6, 8 × 10ⁿ)."""
    if v <= 0:
        return 1e-6
    e = 10 ** math.floor(math.log10(v))
    for m_ in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m_ * e >= v - 1e-12:
            return m_ * e
    return 10 * e


def _tri(mes):
    return Triangulation(mes.nodes[:, 0], mes.nodes[:, 1], np.vstack([mes.els[:, [0, 1, 2]], mes.els[:, [0, 2, 3]]]))


def _obrys(ax, P, fill=False, lw=1.0, color=INK):
    x, y = P.exterior.xy
    if fill:
        ax.fill(x, y, color=FILL, zorder=0)
    ax.plot(x, y, color=color, lw=lw, zorder=5)
    for h in P.interiors:
        x, y = h.xy
        if fill:
            ax.fill(x, y, color="white", zorder=1)
        ax.plot(x, y, color=color, lw=lw, zorder=5)


def _osie(ax, an, pad=0.35):
    x0, z0, x1, z1 = an.P.bounds
    ax.set_xlim(x0 - pad, x1 + pad)
    ax.set_aspect("equal")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("z [m]")
    ax.grid(color=GRID, lw=0.4, zorder=-1)


def _otwory_opis(ax, an, fs=7):
    for o in an.d.otwory:
        ax.text(0.5 * (o.s0 + o.s1), 0.5 * (o.z0 + o.z1), f"{o.id}\n{_pl(o.szer)}×{_pl(o.wys)}", ha="center", va="center",
                fontsize=fs, color=INK2, zorder=6)


def _podpory(ax, an, h=0.14):
    for s in an.d.podpory:
        if s.dl > 1e-9:
            ax.add_patch(Rectangle((s.s0, s.z - h), s.dl, h, fc="white", ec=INK, lw=0.8, hatch="////", zorder=4))
        else:
            ax.add_patch(MplPolygon([[s.s0, s.z], [s.s0 - 0.12, s.z - h], [s.s0 + 0.12, s.z - h]], closed=True, fc="white",
                                    ec=INK, lw=0.8, zorder=4))


# ==================================================================================================
def rys_schemat(an, path: Path) -> list:
    """Schemat statyczny: obrys z otworami, podpory (ściany poniżej), obciążenia charakterystyczne, wymiary."""
    d = an.d
    x0, z0, x1, z1 = an.P.bounds
    L = x1 - x0
    fig, ax = plt.subplots(figsize=(min(max(L * 0.95, 7.5), 13.0), 4.6))
    _obrys(ax, an.P, fill=True, lw=1.2)
    for o in d.otwory:
        ax.plot([o.s0, o.s1], [o.z0, o.z1], color=MUTED, lw=0.5, zorder=2)
        ax.plot([o.s0, o.s1], [o.z1, o.z0], color=MUTED, lw=0.5, zorder=2)
    _otwory_opis(ax, an)
    _podpory(ax, an)
    for s in d.podpory:
        k = "sztywna" if s.k is None else f"k = {_pl(s.k / 1000, 0)} MN/m²"
        ax.text(0.5 * (s.s0 + s.s1), s.z - 0.34, f"{s.id}{(' — ' + s.opis) if s.opis else ''}\n{k}", ha="center", va="top",
                fontsize=6.5, color=INK2)
    # obciążenia liniowe — grupowane wg poziomu
    lv: dict = {}
    for o in d.obciazenia:
        if isinstance(o, (ObcLiniowe, ObcProfil)):
            lv.setdefault(round(o.z, 3), []).append(o)
    H = z1 - z0
    for z, lst in lv.items():
        gora = z >= z0 + 0.5 * H
        col = BLUE if gora else ORANGE
        xa = min(o.s0 for o in lst)
        xb = max(o.s1 for o in lst)
        n = max(int((xb - xa) / 0.45), 2)
        if gora:
            base, top = z1 + 0.06, z1 + 0.46
            for x in np.linspace(xa + 0.1, xb - 0.1, n):
                ax.annotate("", (x, base), (x, top), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.7, mutation_scale=6), zorder=7)
            ax.plot([xa, xb], [top, top], color=col, lw=0.8, zorder=7)
            ytxt = top
        else:
            # obciążenie podwieszone (strop pod tarczą) — krótkie strzałki przy krawędzi dolnej, tylko w betonie
            for x in np.linspace(xa + 0.1, xb - 0.1, n):
                if not an.P.buffer(-0.005).contains(__import__("shapely").geometry.Point(x, z + 0.2)):
                    continue
                ax.annotate("", (x, z + 0.01), (x, z + 0.24), arrowprops=dict(arrowstyle="-|>", color=col, lw=0.7, mutation_scale=5),
                            zorder=7)
            ytxt = z + 0.12
        cases: dict = {}
        for o in lst:
            q = o.wypadkowa / max(o.s1 - o.s0, 1e-9)
            cases[o.przypadek] = cases.get(o.przypadek, 0.0) + q
        opis = ", ".join(f"{c}: {_pl(v, 1)}" for c, v in cases.items())
        nazwy = sorted({(o.opis.split("—")[0].strip() if o.opis else "") for o in lst} - {""})
        ax.text(x1 + 0.12, ytxt, f"{' / '.join(nazwy)} (z = {_pl(z, 2)} m)\n{opis} kN/m", fontsize=6.5, color=col, va="center",
                ha="left", zorder=8)
    pk: dict = {}
    for o in d.obciazenia:
        if isinstance(o, ObcSkupione):
            pk.setdefault((round(o.s, 3), round(o.z, 3)), []).append(o)
    for (xs_, zs_), lst in pk.items():
        up = zs_ > z0 + 0.5 * H
        y_st = zs_ + (0.75 if up else 0.62)
        ax.annotate("", (xs_, zs_), (xs_, y_st), arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.3), zorder=8)
        txt = " + ".join(f"{o.przypadek}: {_pl(o.P, 1)}" for o in lst) + " kN"
        nm = sorted({(o.opis.split("—")[0].strip() if o.opis else "") for o in lst} - {""})
        ax.text(xs_ + 0.07, y_st, (" / ".join(nm) + ": " if nm else "") + txt, fontsize=6.5, color=RED, va="bottom", zorder=8,
                bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))
    # łańcuch wymiarowy
    xs = sorted({round(v, 3) for v in [x0, x1] + [o.s0 for o in d.otwory] + [o.s1 for o in d.otwory]
                 + [s.s0 for s in d.podpory] + [s.s1 for s in d.podpory]})
    yd = z0 - 0.95
    ax.plot([xs[0], xs[-1]], [yd, yd], color=INK2, lw=0.6)
    for a, b in zip(xs[:-1], xs[1:]):
        ax.text(0.5 * (a + b), yd + 0.04, _pl(b - a, 2), ha="center", va="bottom", fontsize=6, color=INK2)
    for v in xs:
        ax.plot([v, v], [yd - 0.06, yd + 0.06], color=INK2, lw=0.6)
    ax.plot([z0, z0], [z0, z0], alpha=0)
    ax.text(x0 - 0.25, 0.5 * (z0 + z1), f"H = {_pl(H, 2)} m, t = {_pl(d.t * 100, 0)} cm, {an.beton.klasa}", rotation=90, ha="right",
            va="center", fontsize=7, color=INK2)
    ax.set_xlim(x0 - 0.5, x1 + 2.6)
    ax.set_ylim(z0 - 1.25, z1 + 0.95)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"Tarcza {d.id} — schemat statyczny, podpory i obciążenia charakterystyczne (kN/m, kN)", loc="left")
    leg = [Line2D([], [], color=BLUE, lw=1, label="obciążenie na krawędzi górnej (strop nad tarczą)"),
           Line2D([], [], color=ORANGE, lw=1, label="obciążenie podwieszone na krawędzi dolnej (strop pod tarczą)"),
           Line2D([], [], color=RED, lw=1.2, label="siły skupione"),
           Rectangle((0, 0), 1, 1, fc="white", ec=INK, hatch="////", label="podpora (ściana poniżej)")]
    ax.legend(handles=leg, fontsize=6.5, frameon=False, loc="upper left", bbox_to_anchor=(0.0, -0.02), ncol=4)
    return [(_save(fig, path), f"Tarcza {d.id}: schemat statyczny — obrys z otworami, podpory na ścianach poniżej, obciążenia "
             "charakterystyczne wg przypadków.")]


# ==================================================================================================
def _mapa(ax, an, val_el, tyt, jedn="MPa", cmap=DIV, sym=True, pct=99.0, vmin=None, vmax=None):
    mes = an.mes
    vn = mes.wartosci_wezlowe(val_el)
    tri = _tri(mes)
    if sym:
        v = _ladna(max(float(np.percentile(np.abs(vn), pct)), 1e-6))
        lev = np.linspace(-v, v, 21)
        cs = ax.tricontourf(tri, np.clip(vn, -v, v), levels=lev, cmap=cmap, extend="both")
    else:
        lo = vmin if vmin is not None else -_ladna(-float(np.percentile(vn, 100 - pct)))
        hi = vmax if vmax is not None else _ladna(float(np.percentile(vn, pct)))
        if hi - lo < 1e-9:
            hi = lo + 1e-6
        lev = np.linspace(lo, hi, 16)
        cs = ax.tricontourf(tri, np.clip(vn, lo, hi), levels=lev, cmap=cmap, extend="both")
    _obrys(ax, an.P, lw=0.8)
    _podpory(ax, an, h=0.10)
    _osie(ax, an, pad=0.15)
    ax.set_ylim(an.P.bounds[1] - 0.14, an.P.bounds[3] + 0.05)
    cb = plt.colorbar(cs, ax=ax, fraction=0.025, pad=0.01, ticks=np.linspace(lev[0], lev[-1], 5))
    cb.set_label(jedn, fontsize=7)
    cb.ax.tick_params(labelsize=6.5)
    ax.set_title(tyt, loc="left", fontsize=8.5)
    ex = (float(val_el.min()), float(val_el.max()))
    ax.text(1.0, 1.01, f"min {_pl(ex[0], 2)} / max {_pl(ex[1], 2)} {jedn}", transform=ax.transAxes, ha="right", va="bottom",
            fontsize=6.5, color=INK2)
    return cs


def rys_mapy(an, path: Path, kombinacja: str | None = None) -> list:
    """Mapy σ_x, σ_z, τ_xz (MPa) dla kombinacji miarodajnej ULS."""
    k = kombinacja or an.k_gov
    r = an.r_uls[k]
    L = an.P.bounds[2] - an.P.bounds[0]
    fig, axs = plt.subplots(3, 1, figsize=(min(max(L * 0.85, 7), 12.5), 8.6))
    for ax, j, t in zip(axs, range(3), ("σ_x — naprężenia poziome (+ rozciąganie)", "σ_z — naprężenia pionowe",
                                          "τ_xz — naprężenia styczne")):
        _mapa(ax, an, r.sig[:, j] / 1000, t)
    fig.suptitle(f"Tarcza {an.d.id} — naprężenia MES [MPa], kombinacja {k} (skala obcięta do 99. percentyla |σ| — osobliwości "
                 "w narożach)", fontsize=8.5, x=0.01, ha="left")
    fig.tight_layout()
    return [(_save(fig, path), f"Tarcza {an.d.id}: mapy naprężeń σ_x, σ_z, τ_xz (MES, stan niezarysowany, {k}).")]


def rys_glowne(an, path: Path, kombinacja: str | None = None, krok: float = 0.25) -> list:
    """σ₁ (rozciąganie), σ₂ (ściskanie) i trajektorie naprężeń głównych (krzyżyki kierunków, długość ∝ |σ|)."""
    k = kombinacja or an.k_gov
    r = an.r_uls[k]
    mes = an.mes
    s1, s2, th = glowne(r.sig)
    L = an.P.bounds[2] - an.P.bounds[0]
    fig, axs = plt.subplots(3, 1, figsize=(min(max(L * 0.85, 7), 12.5), 8.8))
    _mapa(axs[0], an, np.clip(s1, 0, None) / 1000, f"σ₁ — naprężenia główne rozciągające (f_ctm = {_pl(an.beton.f_ctm, 1)} MPa)",
          cmap=SEQ_ORANGE, sym=False, vmin=0.0, pct=99.0)
    _mapa(axs[1], an, np.clip(s2, None, 0) / 1000, f"σ₂ — naprężenia główne ściskające (f_cd = {_pl(an.beton.f_cd, 1)} MPa)",
          cmap=SEQ_BLUE.reversed(), sym=False, vmax=0.0, pct=99.0)
    ax = axs[2]
    _obrys(ax, an.P, fill=True, lw=0.8)
    _podpory(ax, an, h=0.10)
    x0, z0, x1, z1 = an.P.bounds
    pts = []
    for x in np.arange(x0 + krok / 2, x1, krok):
        for z in np.arange(z0 + krok / 2, z1, krok):
            e = mes.element_w(x, z)
            if e is not None and an.P.contains(__import__("shapely").geometry.Point(x, z)):
                pts.append((x, z))
    if pts:
        pts = np.array(pts)
        S = np.array([mes.naprezenia_xy(r, x, z) for x, z in pts])
        a1, a2, at = glowne(S)
        smax = max(float(np.percentile(np.abs(np.concatenate([a1, a2])), 97)), 1e-6)
        for (cx, cz), v1, v2, ang in zip(pts, a1, a2, at):
            for val, an_, col in ((v1, ang, RED), (v2, ang + math.pi / 2, BLUE)):
                c_ = RED if val > 0 else BLUE
                ln = 0.92 * krok * min(abs(val) / smax, 1.0) ** 0.5
                if ln < 0.12 * krok:
                    continue
                dx, dz = 0.5 * ln * math.cos(an_), 0.5 * ln * math.sin(an_)
                ax.plot([cx - dx, cx + dx], [cz - dz, cz + dz], color=c_, lw=0.9 if val > 0 else 0.8, zorder=6,
                        solid_capstyle="butt")
    _osie(ax, an, pad=0.15)
    ax.set_ylim(z0 - 0.14, z1 + 0.05)
    from matplotlib.cm import ScalarMappable
    cb = plt.colorbar(ScalarMappable(cmap=SEQ_BLUE), ax=ax, fraction=0.025, pad=0.01)
    cb.ax.set_visible(False)
    ax.set_title("Trajektorie naprężeń głównych: rozciąganie (czerwone) i ściskanie (niebieskie), długość kreski ∝ √|σ|",
                 loc="left", fontsize=8.5)
    fig.suptitle(f"Tarcza {an.d.id} — naprężenia główne [MPa], kombinacja {k}", fontsize=8.5, x=0.01, ha="left")
    fig.tight_layout()
    return [(_save(fig, path), f"Tarcza {an.d.id}: naprężenia główne σ₁, σ₂ i trajektorie — podstawa orientacji modelu "
             "kratownicowego (EC2 5.6.4(5)).")]


# ==================================================================================================
def rys_stm(an, path: Path, kombinacja: str | None = None) -> list:
    """Model kratownicowy: cięgna (czerwone, ciągłe), krzyżulce (niebieskie, przerywane), grubość ∝ |F|, siły [kN]."""
    m = an.stm
    k = kombinacja or an.k_stm
    F = m.F[k]
    Fm = max(float(np.abs(F).max()), 1e-9)
    L = an.P.bounds[2] - an.P.bounds[0]
    fig, ax = plt.subplots(figsize=(min(max(L * 0.95, 7.5), 13.5), 4.8))
    _obrys(ax, an.P, fill=True, lw=0.9)
    _otwory_opis(ax, an, fs=6.5)
    _podpory(ax, an)
    order = np.argsort(np.abs(F))
    for q in order:
        if abs(F[q]) < 0.01 * Fm:
            continue
        a, b = m.wezly[m.ii[q]], m.wezly[m.jj[q]]
        small = abs(F[q]) < 0.08 * Fm
        col = MUTED if small else (RED if F[q] > 0 else BLUE)
        lw = 0.3 if small else 0.7 + 3.3 * abs(F[q]) / Fm
        ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=lw, ls="-" if F[q] > 0 else (0, (3, 1.6)), zorder=6,
                solid_capstyle="round", alpha=0.35 if small else 1.0)
    # etykiety — największe siły, bez nakładania
    placed = []
    for q in np.argsort(-np.abs(F)):
        if abs(F[q]) < 0.18 * Fm:
            break
        a, b = m.wezly[m.ii[q]], m.wezly[m.jj[q]]
        c = 0.5 * (a + b)
        if any(np.hypot(*(c - p_)) < 0.45 for p_ in placed):
            continue
        placed.append(c)
        ax.text(c[0], c[1], _pl(F[q], 0), fontsize=6.3, ha="center", va="center", color=RED if F[q] > 0 else BLUE, zorder=9,
                bbox=dict(fc="white", ec="none", pad=0.4, alpha=0.9))
    # reakcje w węzłach
    Rw = m.Rw[k][:, 1]
    Rm = max(float(np.abs(Rw).max()), 1e-9)
    for i in np.nonzero(np.abs(Rw) > 0.05 * Rm)[0]:
        x, z = m.wezly[i]
        ln = 0.18 + 0.45 * abs(Rw[i]) / Rm
        if Rw[i] > 0:
            ax.annotate("", (x, z - 0.02), (x, z - 0.02 - ln), arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=0.9), zorder=8)
        else:
            ax.annotate("", (x, z - 0.02 - ln), (x, z - 0.02), arrowprops=dict(arrowstyle="-|>", color=RED, lw=0.9), zorder=8)
    # typy węzłów podporowych — znaczniki
    typy = getattr(an, "typ_wezla", {}).get(k, {})
    mk = {"CCC": "o", "CCT": "^", "CTT": "s"}
    for i, t_ in typy.items():
        if Rw[i] > 0.05 * Rm:
            ax.plot(m.wezly[i, 0], m.wezly[i, 1], marker=mk[t_], ms=4.5, mfc="white", mec=INK, mew=0.8, ls="", zorder=10)
    _osie(ax, an, pad=0.3)
    ax.set_ylim(an.P.bounds[1] - 0.85, an.P.bounds[3] + 0.3)
    ax.set_title(f"Tarcza {an.d.id} — model kratownicowy (STM) z MES, kombinacja {k}; siły [kN] (+ cięgno, − krzyżulec)",
                 loc="left")
    leg = [Line2D([], [], color=RED, lw=2, label="cięgno (zbrojenie)"),
           Line2D([], [], color=BLUE, lw=2, ls=(0, (3, 1.6)), label="krzyżulec ściskany (beton)"),
           Line2D([], [], color=MUTED, lw=0.6, label="pręty < 8 % F_max"),
           Line2D([], [], color=GREEN, lw=1, marker=r"$\uparrow$", ls="", label="reakcja podpory"),
           Line2D([], [], marker="o", mfc="white", mec=INK, ls="", label="węzeł CCC"),
           Line2D([], [], marker="^", mfc="white", mec=INK, ls="", label="CCT"),
           Line2D([], [], marker="s", mfc="white", mec=INK, ls="", label="CTT")]
    ax.legend(handles=leg, fontsize=6.5, frameon=False, loc="upper left", bbox_to_anchor=(0, -0.13), ncol=7)
    return [(_save(fig, path), f"Tarcza {an.d.id}: model kratownicowy wygenerowany z pola naprężeń MES (programowanie liniowe, "
             f"kombinacja {k}); CCC/CCT/CTT — typ węzła podporowego.")]


# ==================================================================================================
def rys_pasy(an, path: Path) -> list:
    """(a) wypadkowa rozciągania przy krawędzi górnej i dolnej z MES (obwiednia) na tle cięgien STM;
    (b) kontrola równowagi: M(x), V(x) z całkowania naprężeń MES i ze statyki (kombinacja miarodajna)."""
    fig, axs = plt.subplots(2, 1, figsize=(10.5, 6.2), sharex=True)
    ax = axs[0]
    cols = {"krawędź górna": BLUE, "krawędź dolna": ORANGE}
    for e in an.kraw:
        if e.otwor is not None or e.typ != "h":
            continue
        base = e.opis.split(" (")[0]
        col = cols.get(base, INK2)
        env = {}
        for n in an.r_uls:
            for b in an.bloki.get((e.id, n), []):
                env[b["x"]] = max(env.get(b["x"], 0.0), b["F"])
        if env:
            xs = np.array(sorted(env))
            ax.plot(xs, [max(env[x], 0) for x in xs], color=col, lw=1.3, label=f"MES — wypadkowa rozciągania: {e.opis}")
        seg = an.odcinki_ciegien.get(e.id, []) if hasattr(an, "odcinki_ciegien") else []
        if seg:
            for j, (xa, xb, Fv) in enumerate(seg):
                ax.hlines(Fv, xa, xb, color=col, lw=2.2, alpha=0.55, label=f"STM — cięgna przy krawędzi: {e.opis} (obwiednia)" if j == 0 else None)
    for s in an.d.podpory:
        ax.axvspan(s.s0, s.s1, color=FILL, zorder=-2)
    ax.set_ylabel("T [kN]")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=6.3, frameon=False, loc="upper right")
    ax.set_title("Siły w pasach tarczy: obwiednia ULS (MES) i cięgna STM; tło — zasięg podpór", loc="left")
    ax = axs[1]
    r = an.r_uls[an.k_gov]
    mes = an.mes
    cx = 0.5 * (mes.gx[:-1] + mes.gx[1:])
    Mm, Vm, Ms, Vs = [], [], [], []
    fz = r.f[1::2] + r.R[1::2]
    fx = r.f[0::2] + r.R[0::2]
    for x in cx:
        c = mes.przekroj_pionowy(r, x)
        lewe = mes.nodes[:, 0] < x
        Mm.append(c["M"])
        Vm.append(c["V"])
        Vs.append(-float(fz[lewe].sum()))
        Ms.append(float((fz[lewe] * (mes.nodes[lewe, 0] - x)).sum()) - float((fx[lewe] * mes.nodes[lewe, 1]).sum()))
    ax.plot(cx, Mm, color=INK, lw=1.4, label="M — całkowanie σ_x (MES) [kNm]")
    ax.plot(cx, Ms, color=ORANGE, lw=0.9, ls=(0, (3, 2)), label="M — statyka części lewej [kNm]")
    ax.plot(cx, Vm, color=BLUE, lw=1.2, label="V — całkowanie τ (MES) [kN]")
    ax.plot(cx, Vs, color=RED, lw=0.8, ls=(0, (3, 2)), label="V — statyka [kN]")
    ax.axhline(0, color=INK2, lw=0.5)
    ax.set_xlabel("x [m]")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=6.3, frameon=False, ncol=2, loc="lower right")
    ax.set_title(f"Kontrola równowagi w przekrojach pionowych ({an.k_gov}); M > 0 — rozciąganie górą", loc="left")
    fig.tight_layout()
    return [(_save(fig, path), f"Tarcza {an.d.id}: siły w pasach (MES vs STM) i kontrola równowagi przekrojów (MES vs statyka).")]


def rys_ugiecia(an, path: Path) -> list:
    """Postać odkształcenia SLS (quasi-stała, t = ∞, zarysowanie) — przeskalowana, oraz rozkład reakcji podpór."""
    mes = an.mes
    r = getattr(an, "r_qp_II", None) or an.r_qp[an.k_qp_gov]
    fig, axs = plt.subplots(2, 1, figsize=(10.5, 5.8), gridspec_kw={"height_ratios": [1.25, 1]})
    ax = axs[0]
    umax = max(float(np.abs(r.u).max()), 1e-12)
    L = an.P.bounds[2] - an.P.bounds[0]
    sk = 0.06 * L / umax
    xy = mes.nodes + sk * np.stack([r.u[0::2], r.u[1::2]], axis=1)
    tri0 = _tri(mes)
    tri1 = Triangulation(xy[:, 0], xy[:, 1], tri0.triangles)
    wz = -r.u[1::2] * 1000
    cs = ax.tripcolor(tri1, wz, shading="gouraud", cmap=SEQ_BLUE)
    _obrys(ax, an.P, lw=0.6, color=MUTED)
    cb = plt.colorbar(cs, ax=ax, fraction=0.025, pad=0.01)
    cb.set_label("w [mm] (w dół +)", fontsize=7)
    _osie(ax, an, pad=0.2)
    ax.set_aspect("equal", adjustable="datalim")
    txt = "; ".join(f"{u_['opis']}: w = {_pl(u_['w_II'], 2)} mm (lim {_pl(u_['w_dop'], 1)})" for u_ in getattr(an, "ugiecia", []))
    ax.set_title(f"Postać odkształcenia — SLS quasi-stała, t = ∞, sztywność zarysowana (skala ×{sk:.0f})", loc="left")
    if txt:
        ax.text(0.0, -0.32, txt, transform=ax.transAxes, fontsize=6.5, color=INK2, va="top")
    ax = axs[1]
    rg = mes.reakcje(an.r_uls[an.k_gov])
    rc = mes.reakcje(an.r_char[an.k_char_gov])
    for s in an.d.podpory:
        a = rg[s.id]
        b = rc[s.id]
        if len(a["x"]) > 1:
            ax.plot(a["x"], a["r"], color=INK, lw=1.2)
            ax.plot(b["x"], b["r"], color=BLUE, lw=1.0, ls=(0, (3, 2)))
            ax.text(0.5 * (s.s0 + s.s1), 0.08 * max(a["r"].max(), 1.0), f"{s.id}: R_d = {_pl(a['R'], 0)} kN\nR_k = {_pl(b['R'], 0)} kN",
                    ha="center", va="bottom", fontsize=6.5, bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.4))
        else:
            ax.bar(a["x"], a["R"], width=0.1, color=INK)
    ax.axhline(0, color=INK2, lw=0.5)
    ax.set_xlim(an.P.bounds[0] - 0.2, an.P.bounds[2] + 0.2)
    ax.set_ylabel("r [kN/m]")
    ax.set_xlabel("x [m]")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(handles=[Line2D([], [], color=INK, lw=1.2, label=f"ULS ({an.k_gov})"),
                       Line2D([], [], color=BLUE, lw=1, ls=(0, (3, 2)), label=f"SLS char. ({an.k_char_gov})")],
              fontsize=6.5, frameon=False, loc="upper right")
    ax.set_title("Rozkład reakcji na ściany poniżej (przekazanie obciążeń — bilans ścieżki)", loc="left")
    fig.tight_layout()
    return [(_save(fig, path), f"Tarcza {an.d.id}: ugięcia SLS (zarysowanie, pełzanie) i rozkład reakcji podpór.")]


def rys_zbrojenie(an, path: Path) -> list:
    """Szkic zbrojenia: cięgna (pręty przy obu powierzchniach), U-pręty na końcach, pręty obwodowe i ukośne przy otworach,
    siatki (opis)."""
    d = an.d
    L = an.P.bounds[2] - an.P.bounds[0]
    fig, ax = plt.subplots(figsize=(min(max(L * 0.95, 7.5), 13.5), 4.6))
    _obrys(ax, an.P, fill=True, lw=1.1)
    _podpory(ax, an)
    kolory = [RED, "#b8461c", "#7a2c10", ORANGE, "#d6336c", "#9c2a2a"]
    placed = []
    for i, pas in enumerate(an.pasy):
        e = pas.krawedz
        if e is None:
            continue
        col = kolory[i % len(kolory)]
        ext = [z_ for z_ in pas.zakotwienie]
        a0, a1 = pas.zakres
        for z_ in ext:
            if z_["sposob"] == "proste":
                if z_["strona"] < 0:
                    a0 -= min(z_["l_req"], max(z_["l_av"], 0))
                else:
                    a1 += min(z_["l_req"], max(z_["l_av"], 0))
            else:
                if z_["strona"] < 0:
                    a0 -= max(z_["l_av"], 0)
                else:
                    a1 += max(z_["l_av"], 0)
        off = e.strona * pas.a
        if e.typ == "h":
            y = e.wsp + off
            ax.plot([a0, a1], [y, y], color=col, lw=2.0, zorder=7, solid_capstyle="butt")
            for z_ in ext:
                xe = a1 if z_["strona"] > 0 else a0
                if not z_["sposob"] == "proste":
                    ax.plot([xe, xe], [y, y + e.strona * 0.18], color=col, lw=2.0, zorder=7)
            c = (0.5 * (a0 + a1), y)
            lab = f"{pas.n}φ{pas.fi}"
            va = "bottom" if e.strona < 0 else "top"
            dy = -0.05 if e.strona < 0 else 0.05
        else:
            xl = e.wsp + off
            ax.plot([xl, xl], [a0, a1], color=col, lw=2.0, zorder=7, solid_capstyle="butt")
            c = (xl, 0.5 * (a0 + a1))
            lab = f"{pas.n}φ{pas.fi}"
            va, dy = "center", 0
        if any(np.hypot(c[0] - p_[0], c[1] - p_[1]) < 0.5 for p_ in placed):
            c = (c[0] + 0.6, c[1])
        placed.append(c)
        ax.text(c[0], c[1] + dy, lab, fontsize=6.5, color=col, ha="center", va=va, zorder=9,
                bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.85))
    fi = d.fi_otwory
    for o in d.otwory:
        g = 0.07
        ax.add_patch(Rectangle((o.s0 - g, o.z0 - g), o.szer + 2 * g, o.wys + 2 * g, fc="none", ec=INK2, lw=0.9, zorder=6))
        for (x, z, bx, bz) in ((o.s0, o.z1, -1, 1), (o.s1, o.z1, 1, 1), (o.s0, o.z0, -1, -1), (o.s1, o.z0, 1, -1)):
            cx, cz = x + bx * 0.17, z + bz * 0.17
            ux, uz = 1 / math.sqrt(2), -bx * bz / math.sqrt(2)      # pręt prostopadły do dwusiecznej naroża
            ln_ = __import__("shapely").geometry.LineString([(cx - ux * 0.3, cz - uz * 0.3), (cx + ux * 0.3, cz + uz * 0.3)])
            ln_ = ln_.intersection(an.P.buffer(-0.04))
            if not ln_.is_empty and ln_.geom_type == "LineString":
                xx, zz = ln_.xy
                ax.plot(xx, zz, color=INK, lw=1.1, zorder=7)
        ax.text(0.5 * (o.s0 + o.s1), 0.5 * (o.z0 + o.z1), f"{o.id}\nobwodowe 2φ{fi}/pow.\nukośne 2φ{fi}/pow.", ha="center", va="center",
                fontsize=6, color=INK2)
    ax.set_title(f"Tarcza {d.id} — szkic zbrojenia głównego (pręty przy obu powierzchniach); siatki φ{an.siatka_fi} co "
                 f"{an.siatka_s} mm × 2", loc="left")
    _osie(ax, an, pad=0.3)
    ax.set_ylim(an.P.bounds[1] - 0.4, an.P.bounds[3] + 0.25)
    return [(_save(fig, path), f"Tarcza {d.id}: szkic zbrojenia — cięgna (kolor), U-pręty na końcach, pręty obwodowe i ukośne "
             "przy otworach; siatki przy obu powierzchniach.")]


def rys_zal_F(an, path: Path) -> list:
    """Zbrojenie wymagane z pola naprężeń (zał. F, obwiednia ULS) — kierunek x i z [mm²/m, łącznie], izolinia nośności siatek."""
    L = an.P.bounds[2] - an.P.bounds[0]
    fig, axs = plt.subplots(2, 1, figsize=(min(max(L * 0.85, 7), 12.5), 5.8))
    cap = 2 * an.siatka_As
    vmax = max(float(np.percentile(np.concatenate([an.req_x, an.req_z]), 99.5)), cap * 1.2)
    for ax, val, t in ((axs[0], an.req_x, "a_sx — zbrojenie poziome wymagane"), (axs[1], an.req_z, "a_sz — zbrojenie pionowe wymagane")):
        _mapa(ax, an, val, t + f" (izolinia — nośność siatek 2×{_pl(an.siatka_As, 0)} mm²/m)", jedn="mm²/m", cmap=SEQ_ORANGE,
              sym=False, vmin=0.0, vmax=vmax)
        tri = _tri(an.mes)
        vn = an.mes.wartosci_wezlowe(val)
        if vn.max() > cap:
            ax.tricontour(tri, vn, levels=[cap], colors=[INK], linewidths=0.9)
    fig.suptitle(f"Tarcza {an.d.id} — zbrojenie z pola naprężeń wg PN-EN 1992-1-1 zał. F (obwiednia STR)", fontsize=8.5, x=0.01,
                 ha="left")
    fig.tight_layout()
    return [(_save(fig, path), f"Tarcza {an.d.id}: zbrojenie wymagane z pola naprężeń (zał. F) na tle nośności siatek.")]


def rysunki_tarczy(an, rys_dir: Path, prefiks: str | None = None) -> list:
    """Komplet rysunków pozycji tarczowej → [(ścieżka, podpis)]."""
    import re
    rys_dir = Path(rys_dir)
    pf = prefiks or "tarcza_" + re.sub(r"[^A-Za-z0-9_-]+", "_", an.d.id)
    out = []
    out += rys_schemat(an, rys_dir / f"{pf}_schemat.png")
    out += rys_mapy(an, rys_dir / f"{pf}_mapy.png")
    out += rys_glowne(an, rys_dir / f"{pf}_glowne.png")
    if hasattr(an, "stm"):
        out += rys_stm(an, rys_dir / f"{pf}_stm.png")
    out += rys_pasy(an, rys_dir / f"{pf}_pasy.png")
    if hasattr(an, "req_x"):
        out += rys_zal_F(an, rys_dir / f"{pf}_zalF.png")
    out += rys_ugiecia(an, rys_dir / f"{pf}_ugiecia.png")
    out += rys_zbrojenie(an, rys_dir / f"{pf}_zbrojenie.png")
    return out
