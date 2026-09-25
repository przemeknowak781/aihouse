"""Schematy instalacji (widoki bez skali): rozwinięcie kanalizacji (piony), rozwinięcie instalacji wodociągowej,
schemat PC / c.o. / c.w.u. (``obliczenia.sanitarne.schemat_pc``) i schemat rozdzielnicy RG
(``obliczenia.elektryka.schemat_rg``).

Schematy PC i RG są rysowane przez funkcje bibliotek w matplotlib — figura jest przechwytywana i ODTWARZANA
WEKTOROWO w silniku ``lamela.draft`` (linie, wieloboki, napisy jako prymitywy rzutni: DXF + PDF wektorowy, RPB § 2b),
z przeskalowaniem tak, aby najmniejsze pismo miało ≥ 1,8 mm (PN-EN ISO 3098) i z rozsunięciem kolidujących napisów."""
from __future__ import annotations

import io
import math

import numpy as np
from matplotlib import colors as mcolors

from ...draft import styles
from ...draft import text as T
from ...draft.core import PText, Viewport
from ..common import Placer
from .wspolne import InstResult

styles.LAYERS.setdefault("I-SCHEMAT", styles.LayerDef("I-SCHEMAT", "Schematy instalacji (odtworzone z bibliotek "
                                                     "obliczeniowych)", "cienka", aci=7, z=20))
SERIA_LW = (0.18, 0.25, 0.35, 0.5, 0.7)


def _hex(c, alpha_bg=True):
    r, g, b, a = mcolors.to_rgba(c)
    if alpha_bg and a < 1.0:
        r, g, b = (r * a + (1 - a), g * a + (1 - a), b * a + (1 - a))
    return mcolors.to_hex((r, g, b)), a


def _pen(lw_pt):
    for lim, mm in ((0.7, 0.18), (1.05, 0.25), (1.35, 0.35), (1.9, 0.5)):
        if lw_pt <= lim:
            return mm
    return 0.7


def _lt(ls):
    ls = str(ls)
    if ls in ("--", "dashed") or ls.startswith("(0, (3") or ls.startswith("(0.0, (3"):
        return "KRESKOWA_DROBNA"
    if ls in (":", "dotted") or ls.startswith("(0, (1") or ls.startswith("(0.0, (1"):
        return "KROPKOWA"
    if ls in ("-.", "dashdot"):
        return "PUNKTOWA_KROTKA"
    return "CIAGLA"


def przechwyc(fn, *a, **kw):
    """Uruchamia funkcję rysującą (zapis do pamięci) i zwraca figurę matplotlib przed zamknięciem."""
    import matplotlib.pyplot as plt
    box = {}
    orig = plt.close

    def fake(fig=None, *aa, **kk):
        if fig is not None and not isinstance(fig, str):
            box.setdefault("fig", fig)
        return orig(fig, *aa, **kk)
    plt.close = fake
    try:
        fn(*a, io.BytesIO(), **kw)
    finally:
        plt.close = orig
    return box.get("fig")


def odtworz(fig, vp, min_h=1.8, layer="I-SCHEMAT"):
    """Odtwarza osie figury w rzutni ``vp``. Zwraca współczynnik f [mm papieru na jednostkę danych]."""
    ax = fig.axes[0]
    tr = ax.transData
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    renderer = FigureCanvasAgg(fig).get_renderer()
    ppu = abs(tr.transform((1, 0))[0] - tr.transform((0, 0))[0]) * 72.0 / fig.dpi   # pt na jednostkę danych
    cap = T.cap_ratio("normal")
    fs = [t.get_fontsize() for t in ax.texts if t.get_text().strip()]
    f = max(1.0, min_h / (min(fs) / ppu * cap)) if fs else 1.0
    s = f * vp.k

    def X(pts):
        return np.asarray(pts, float) * s

    for ln in ax.lines:
        xy = (ln.get_transform() - tr).transform(ln.get_xydata())
        if len(xy) < 2 or ln.get_linestyle() in ("None", "none", " ", ""):
            continue
        col, a = _hex(ln.get_color())
        vp.polyline(X(xy), layer, pen=_pen(ln.get_linewidth()), lt=_lt(ln.get_linestyle()), color=col)
    for p in ax.patches:
        trp = p.get_transform() - tr
        polys = p.get_path().to_polygons(transform=trp, closed_only=False)
        fc, fa = _hex(p.get_facecolor())
        ec, ea = _hex(p.get_edgecolor(), alpha_bg=False)
        for pg in polys:
            if len(pg) < 2:
                continue
            closed = np.allclose(pg[0], pg[-1])
            P = X(pg[:-1] if closed else pg)
            if p.get_fill() and fa > 0.01 and closed and len(P) >= 3:
                vp.fill(P, layer, fc, z=15.0)
            if p.get_linewidth() > 0 and ea > 0.01:
                vp.polyline(P, layer, closed=closed, pen=_pen(p.get_linewidth()), lt=_lt(p.get_linestyle()),
                            color=ec, z=19.0)
    for t in ax.texts:
        txt = t.get_text()
        if not txt.strip():
            continue
        x, y = (t.get_transform() - tr).transform(t.get_position())
        h = styles.snap_text_h(max(min_h, t.get_fontsize() / ppu * cap * f))
        col, _a = _hex(t.get_color())
        rot = float(t.get_rotation())
        ha = t.get_ha()
        va = {"center": "middle", "center_baseline": "middle"}.get(t.get_va(), t.get_va())
        style = "bold" if str(t.get_weight()) in ("bold", "700", "heavy") else "normal"
        lines = txt.split("\n")
        lh = h * 1.55
        n = len(lines)
        r90 = round(rot) % 360
        if r90 in (90, 270):
            # rotation_mode='default': wyrównanie wg obwiedni po obrocie — odtworzenie z obwiedni renderowanej
            bb = t.get_window_extent(renderer)
            (bx0, by0), (bx1, by1) = tr.inverted().transform([[bb.x0, bb.y0], [bb.x1, bb.y1]])
            order = range(n) if r90 == 90 else range(n - 1, -1, -1)
            for j, i in enumerate(order):
                if not lines[i].strip():
                    continue
                xc = bx0 + (j + 0.5) * (bx1 - bx0) / n
                P = X([xc, by0 if r90 == 90 else by1])
                vp.text(P, lines[i], h, float(r90), "left", "middle", layer, style=style, color=col, z=31.0,
                        mask=0.3)
            continue
        if va == "top":
            offs = [-(i * lh) for i in range(n)]
        elif va == "bottom" or va == "baseline":
            offs = [(n - 1 - i) * lh for i in range(n)]
        else:
            offs = [((n - 1) / 2 - i) * lh for i in range(n)]
        ca, sa = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        for s_, o in zip(lines, offs):
            if not s_.strip():
                continue
            P = X([x, y]) + np.array([-sa * o, ca * o]) * vp.k
            vp.text(P, s_, h, rot, ha, va if n == 1 else ("top" if va == "top" else ("bottom" if va in (
                "bottom", "baseline") else "middle")), layer, style=style, color=col, z=31.0,
                mask=0.3)                           # maska: linie schematu nie przecinają napisów (weryf. C 2.6)
    return f


def rozsun_napisy(vp, kroki_mm=(0.0, 1.2, 2.4, 3.6, 5.0)):
    """Usuwa nakładanie napisów: każdy kolejny napis przesuwany o najmniejszy wektor, przy którym nie koliduje
    z napisami już rozmieszczonymi (i ogranicza kolizje z liniami)."""
    k = vp.k
    texts = [p for p in vp.prims if isinstance(p, PText)]
    pl = Placer(k)                      # tylko kolizje napis–napis (położenie względem linii — jak w bibliotece)
    moved = 0
    for t in texts:
        base = t.pos.copy()
        cands = []
        for r in kroki_mm:
            for dx, dy in ((0, 0), (0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)):
                if r == 0 and (dx or dy):
                    continue
                cands.append(base + np.array([dx, dy]) * r * k)
        best, bc = None, None
        for i, c in enumerate(cands):
            t.pos = c
            from ..common import prim_shapes
            tx, _l, _f = prim_shapes([t], k, text_pad_mm=0.3)
            cost = pl.cost(tx) + i * 0.01
            if bc is None or cost < bc - 1e-9:
                best, bc = c, cost
            if cost <= i * 0.01 + 1e-9:
                break
        t.pos = best
        if not np.allclose(best, base):
            moved += 1
        pl.add_prims([t])
    return moved


# ================================================================================================ widoki
TYTULY = {"kanalizacja": "ROZWINIĘCIE KANALIZACJI SANITARNEJ (PIONY)",
          "woda": "ROZWINIĘCIE INSTALACJI WODOCIĄGOWEJ",
          "pc": "SCHEMAT IDEOWY POMPY CIEPŁA, C.O. I C.W.U.",
          "rg": "SCHEMAT IDEOWY ROZDZIELNICY GŁÓWNEJ RG"}


def rysuj(ctx, W, spec, scale, opts):
    kind = str(spec.get("schemat", "")).lower()
    if kind not in TYTULY:
        raise ValueError(f"nieznany schemat '{kind}' ({', '.join(TYTULY)})")
    title = spec.get("tytul_widoku") or TYTULY[kind]
    vp = Viewport(scale, title)
    res = InstResult(bez_skali=True)
    if kind in ("pc", "rg"):
        _mpl(vp, W, kind, res)
    elif kind == "kanalizacja":
        from .sch_kan import rozwiniecie_kan
        rozwiniecie_kan(vp, ctx, W, res)
    else:
        from .sch_kan import rozwiniecie_wody
        rozwiniecie_wody(vp, ctx, W, res)
    from .wspolne import text_collisions
    res.kolizje = text_collisions(vp)
    if res.kolizje:
        ctx.note(f"arkusz {spec.get('nr', '')}", f"kolizje napisów: {res.kolizje}")
    res.units_note = "Schemat bez skali; rzędne w m względem ±0,000 (posadzka parteru), średnice w mm."
    return vp, res, title


def _mpl(vp, W, kind, res):
    if kind == "pc":
        from ...obliczenia.sanitarne.schemat_pc import rysuj_schemat_pc
        fig = przechwyc(rysuj_schemat_pc, W.ogrzewanie, W.woda)
        zr = "lamela.obliczenia.sanitarne.schemat_pc (dane: ogrzewanie, woda)"
    else:
        from ...obliczenia.elektryka.schemat_rg import rysuj_schemat_rg
        fig = przechwyc(rysuj_schemat_rg, W.obwody)
        zr = "lamela.obliczenia.elektryka.schemat_rg (dane: obwody, WLZ, SPD, PWP)"
    if fig is None:
        raise RuntimeError(f"schemat {kind}: nie przechwycono figury matplotlib")
    f = odtworz(fig, vp)
    n = rozsun_napisy(vp)
    # legenda symboli jest częścią schematu — osobny blok „OZNACZENIA” z jedną pozycją pominięty (weryf. C 2.6)
    res.notes += ["Legenda symboli — na schemacie (PN-EN 60617 / PN-EN ISO 14617 w uproszczeniu; oznaczenia "
                  "instalacji sanitarnych — praktyka branżowa).",f"Schemat odtworzony wektorowo z funkcji {zr} — treść i wartości z obliczeń na aktualnym modelu; "
                  f"skala rysunkowa {f:.2f} mm/jedn. (pismo ≥ 1,8 mm), przesunięto {n} napisów kolidujących.",
                  "Dane urządzeń przykładowe (bez nazw handlowych) — do zastąpienia DTR wybranych wyrobów "
                  "(lub równoważnych)."]
    if kind == "rg":
        o = W.obwody
        from .wspolne import num
        res.notes += [f"WLZ {o.wlz['przewod']}, L = {num(o.wlz['L'], 1)} m; SPD: {o.spd['RG']}.",
                      "Aparatura modułowa wg PN-EN 60898-1, PN-EN 61009-1, PN-EN 61008-1; rozdzielnica wg "
                      "PN-EN IEC 61439-3; PWP wg WT § 183 (przycisk przy wejściu, oznakowany)."]
    else:
        res.notes += ["Ogrzewanie wg PN-EN 1264, PN-EN 12828 (zabezpieczenie instalacji wodnych), c.w.u. wg "
                      "PN-EN 806 i WT § 120; naczynia wzbiorcze i zawory bezpieczeństwa z obliczeń."]
