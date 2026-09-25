"""Rysowanie elementów projektu zagospodarowania działki (PZT) silnikiem ``lamela.draft``.

Konwencje: PN-B-01027 (oznaczenia PZT — grubości linii jawnie w mm), PN-EN ISO 11091, PN-EN ISO 128-2 (linie),
PN-B-01025 (rzędne — 2 miejsca na PZT), PN-B-01029 (wymiary w m z dokładnością 0,01 m); uzbrojenie — kolory i litery
wg praktyki mapy zasadniczej (rozp. BDOT500, Dz.U. 2021 poz. 1385, zał. 4). Współrzędne — układ działki [m].

Zawiera: warstwy PZT, ``Labeler`` (opisy z odnośnikami bez kolizji — ``common.Placer``), podkład mapowy, elementy
projektu, sieci, wymiary odległości, rzędne i spadki, legendę i tabele arkusza.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import styles, text as T
from ..draft.core import Viewport
from ..draft.geom import circle_pts, lines_of, perp, polygons_of, readable_angle, unit
from .common import Placer

# ------------------------------------------------------------------------------------------------ warstwy PZT
_L = styles.LayerDef
for _ld in [
    _L("Z-MAPA", "Podkład: mapa do celów projektowych (przykładowa, fikcyjna)", "b_cienka", aci=8,
       plot_rgb="#5a5a5a", z=12),
    _L("Z-MAPA-OPISY", "Podkład: opisy mapy (numery działek, budynki, sieci)", "cienka", aci=8, plot_rgb="#5a5a5a",
       z=26),
    _L("Z-MAPA-RAMKA", "Ramka i opis podkładu mapowego", "srednia", aci=7, z=27),
    _L("Z-DZIALKA", "Granica działki budowlanej (PN-B-01027 poz. 2.7)", "srednia", aci=1, z=23),
    _L("Z-LZ", "Nieprzekraczalna linia zabudowy (MPZP, PN-B-01027 poz. 2.2)", "srednia", aci=1, plot_rgb="#c00000",
       z=22),
    _L("Z-DROGA", "Droga publiczna: linie rozgraniczające, jezdnia", "srednia", aci=8, plot_rgb="#404040", z=14),
    _L("Z-BUDYNEK", "Budynek projektowany — obrys przyziemia 1,0 m nad terenem (PN-B-01027 poz. 1.1)", "b_gruba",
       aci=7, z=24),
    _L("Z-BUDYNEK-NAD", "Obrys wyższych kondygnacji, płyt i okapów (PN-B-01027 poz. 1.6)", "gruba", "KRESKOWA",
       aci=7, z=23),
    _L("Z-WYMIARY", "Wymiarowanie PZT — linie 0,18 (PN-B-01027 poz. 4)", "b_cienka", aci=1, z=25),
    _L("Z-RZEDNE", "Rzędne terenu istniejącego i projektowanego (PN-B-01025)", "b_cienka", aci=32,
       plot_rgb="#6b4423", z=25),
    _L("Z-RZEDNE-PROJ", "Rzędne terenu projektowanego", "b_cienka", aci=1, z=25),
    _L("Z-ODWODNIENIE", "Odwodnienie terenu, spadki, kierunki spływu", "cienka", aci=150, plot_rgb="#00808a", z=21),
    _L("Z-SIECI-IST", "Uzbrojenie istniejące (wg mapy)", "cienka", aci=5, z=19),
    _L("Z-SIECI-PROJ", "Uzbrojenie projektowane (przyłącza, kolektory)", "gruba", aci=5, z=21),
    _L("Z-KOLIZJE", "Kolizje, zbliżenia i skrzyżowania sieci", "srednia", aci=6, plot_rgb="#c000c0", z=27),
    _L("Z-TYCZENIE", "Punkty tyczenia budynku", "cienka", aci=1, z=26),
    _L("Z-STREFY", "Strefy (R290 pompy ciepła)", "cienka", aci=6, plot_rgb="#b000b0", z=13),
    _L("Z-TLO", "Tło (maski wypełnień)", "b_cienka", aci=7, z=9),
]:
    styles.LAYERS.setdefault(_ld.name, _ld)

GREY = "#5a5a5a"
H = 2.5          # podstawowa wysokość pisma w rzutniach PZT (min. 2,5 mm — PN-B-01027, plot.qa)


# ------------------------------------------------------------------------------------------------ geometria
def clip(g, win):
    """Część geometrii w oknie (Polygon); None gdy pusta."""
    if g is None or win is None:
        return g
    r = g.intersection(win)
    return None if r.is_empty else r


def draw_geom(c, g, layer, pen=None, lt=None, color=None, z=None):
    if g is None or g.is_empty:
        return
    for a in lines_of(g):
        if len(a) >= 2:
            closed = len(a) > 2 and np.allclose(a[0], a[-1])
            c.polyline(a[:-1] if closed else a, layer, closed=closed, pen=pen, lt=lt, color=color, z=z)


def fill_white(c, g, z=9.5):
    """Białe tło pod elementem (zakrywa kreskowania/kropki podkładu)."""
    if g is not None and not g.is_empty:
        c.fill(g, "Z-TLO", "#ffffff", z=z)


def seg_dir(a, b):
    d = np.asarray(b, float) - np.asarray(a, float)
    return d / (np.hypot(*d) or 1.0)


# ------------------------------------------------------------------------------------------------ napisy
def text_block(c, pos, lines, h=H, ha="left", layer="Z-OPISY", style="normal", color=None, mask=0.0, gap=1.45,
               rot=0.0):
    """Blok wierszy: ``pos`` = punkt górnej krawędzi bloku (wg ``ha``); zwraca (szer., wys.) w jedn. płótna."""
    k = c.k
    lines = [ln for ln in (lines if isinstance(lines, (list, tuple)) else [lines]) if ln is not None]
    a = math.radians(rot)
    ex, ey = np.array([math.cos(a), math.sin(a)]), np.array([-math.sin(a), math.cos(a)])
    P = np.asarray(pos, float)
    for i, s in enumerate(lines):
        st = style[i] if isinstance(style, (list, tuple)) else style
        q = P - ey * (h + i * h * gap) * k
        c.text(q, str(s), h, rot, ha, "baseline", layer, style=st, color=color, mask=mask)
    W = max((T.width(str(s), h, "bold" if st_is_bold(style, i) else "normal") for i, s in enumerate(lines)),
            default=0.0) * k
    return W, (h + (len(lines) - 1) * h * gap + 0.22 * h) * k


def st_is_bold(style, i):
    st = style[i] if isinstance(style, (list, tuple)) else style
    return st == "bold"


def block_size(lines, h=H, style="normal", gap=1.45):
    """Wymiary bloku [mm papieru]."""
    lines = [ln for ln in (lines if isinstance(lines, (list, tuple)) else [lines]) if ln is not None]
    W = max((T.width(str(s), h, "bold" if st_is_bold(style, i) else "normal") for i, s in enumerate(lines)),
            default=0.0)
    return W, h + (len(lines) - 1) * h * gap + 0.22 * h


DIRS = [(1, 0), (1, 1), (0, 1), (-1, 0), (1, -1), (0, -1), (-1, 1), (-1, -1)]


class Labeler:
    """Opisy bez kolizji: rejestr zajętości (``common.Placer``) i wybór położenia z kandydatów wokół punktu
    (8 kierunków × rosnące odsunięcie); przy odsunięciu — odnośnik od punktu do bloku napisu."""

    def __init__(self, vp: Viewport, bounds=None):
        self.vp = vp
        self.k = vp.k
        self.pl = Placer(vp.k)
        self.bounds = bounds
        self.failed = []

    def mark(self) -> int:
        return len(self.vp.prims)

    def reg(self, n0: int, w_text=1.0, w_line=0.5, w_fill=1.0):
        self.pl.add_prims(self.vp.prims[n0:], w_text=w_text, w_line=w_line, w_fill=w_fill)

    def area(self, g, w=1.0):
        if g is not None and not g.is_empty:
            self.pl.add(g, "area", w)

    def lines(self, g, w=0.4, buf_mm=0.3):
        if g is not None and not g.is_empty:
            self.pl.add_lines(g, w=w, buf_mm=buf_mm)

    def label(self, anchor, lines, h=H, layer="Z-OPISY", style="normal", color=None, mask=0.5,
              dists=(0.8, 2.0, 4.0, 7.0, 11.0, 16.0, 22.0), dirs=None, leader_from=3.0, dot=False,
              max_cost=None, frame=False, register=True, leader_color=None, penalty=0.02):
        k = self.k
        W, Hh = block_size(lines, h, style)
        A = np.asarray(anchor, float)
        cands = []
        for d in dists:
            for (ux, uy) in (dirs or DIRS):
                cx = A[0] + (ux * (d + W / 2.0) * k if ux else 0.0)
                cy = A[1] + (uy * (d + Hh / 2.0) * k if uy else 0.0)
                cands.append((cx, cy, ux, uy, d))

        def fn(cv, cand):
            cx, cy, ux, uy, d = cand
            ha = "left" if ux > 0 else "right" if ux < 0 else "center"
            x = cx - W / 2.0 * k if ha == "left" else cx + W / 2.0 * k if ha == "right" else cx
            top = cy + Hh / 2.0 * k
            text_block(cv, (x, top), lines, h, ha, layer, style, color, mask)
            bx = box(cx - W / 2.0 * k - 0.6 * k, cy - Hh / 2.0 * k - 0.5 * k,
                     cx + W / 2.0 * k + 0.6 * k, cy + Hh / 2.0 * k + 0.5 * k)
            if frame:
                cv.polygon(np.asarray(bx.exterior.coords)[:-1], layer, pen=0.18, color=color)
            if d >= leader_from:
                q = np.asarray(bx.exterior.interpolate(bx.exterior.project(Point(A))).coords[0])
                if np.hypot(*(q - A)) > 1.2 * k:
                    cv.line(A, q, layer, pen=0.18, color=leader_color or color)
                    if dot:
                        cv.dot(A, 0.7, layer, color=leader_color or color or "#000000")
        pos, cost = self.pl.place(self.vp, fn, cands, penalty_step=penalty, bounds=self.bounds, max_cost=max_cost,
                                  register=register)
        if pos is None:
            self.failed.append(lines)
        return pos, cost

    def along(self, ls: LineString, text, h=H, layer="Z-OPISY", color=None, n=1, fracs=None, offset_mm=0.0,
              max_cost=4.0, style="normal", mask=0.4, min_len_mm=12.0):
        """Opis wzdłuż łamanej (np. warstwica, sieć) — ``n`` wystąpień w najlepszych miejscach."""
        k = self.k
        L = ls.length
        w = T.width(text, h, style) * k
        if L < max(w * 1.2, min_len_mm * k):
            return 0
        fr = fracs or [i / 20.0 for i in range(1, 20)]
        placed = 0
        used = []

        def fn(cv, cand):
            p, ang, up = cand
            cv.text(p + up * offset_mm * k, text, h, ang, "center", "middle", layer, style=style, color=color,
                    mask=mask)
        for _ in range(n):
            cands = []
            for f in fr:
                s = f * L
                if s < w / 2 or s > L - w / 2 or any(abs(s - u) < max(L / (n + 1) * 0.6, w * 1.5) for u in used):
                    continue
                p = np.asarray(ls.interpolate(s).coords[0])
                a = np.asarray(ls.interpolate(max(0.0, s - w / 2)).coords[0])
                b = np.asarray(ls.interpolate(min(L, s + w / 2)).coords[0])
                if np.hypot(*(b - a)) < w * 0.92:          # zakręt pod napisem
                    continue
                d = unit(b - a)
                ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
                cands.append((p, ang, perp(np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]))))
            if not cands:
                break
            mid = len(cands) // 2
            cands = [c_ for _i, c_ in sorted(enumerate(cands), key=lambda t: abs(t[0] - mid))]
            pos, _c = self.pl.place(self.vp, fn, cands, penalty_step=0.01, bounds=self.bounds, max_cost=max_cost)
            if pos is None:
                break
            used.append(ls.project(Point(pos[0])))
            placed += 1
        return placed


# ================================================================================================ podkład mapowy
def map_window(s, opts: dict, margin=4.0):
    """Okno podkładu: działka + budynki sąsiednie + hydrant (± margines), przycięte do zasięgu danych mapy."""
    if opts.get("okno"):
        return tuple(float(v) for v in opts["okno"])
    geoms = [s.plot] + [x["bud"] for x in s.sasiedzi if x["bud"] is not None]
    geoms += [Point(o.xy) for o in s.obiekty.values() if o.id.upper().startswith("HYD")]
    x0, y0, x1, y1 = unary_union(geoms).bounds
    x0, y0, x1, y1 = x0 - margin, y0 - margin - 4.0, x1 + margin, y1 + margin
    data = [x["poly"] for x in s.sasiedzi if x["poly"] is not None] + \
        [g for g in (s.droga["pas"], s.plot) if g is not None]
    bx0, by0, bx1, by1 = unary_union(data).bounds
    return max(x0, bx0), max(y0, by0), min(x1, bx1), min(y1, by1)


def draw_base_map(c, s, lab: Labeler, win: Polygon, used: set, opts: dict, spot_every=9.0):
    """Treść podkładu (mapy do celów projektowych — SYNTETYCZNEJ, z dzialka.yaml): działki sąsiednie z numerami,
    budynki sąsiednie, droga, uzbrojenie istniejące, warstwice i pikiety terenu istniejącego, zieleń istniejąca."""
    from ..draft import symbols as S
    k = c.k
    n0 = lab.mark()
    # działki sąsiednie
    for x in s.sasiedzi:
        g = clip(x["poly"], win)
        if g is not None:
            draw_geom(c, clip(x["poly"].exterior, win), "Z-MAPA", pen=0.25, lt="CIAGLA")
    # droga: pas w liniach rozgraniczających (0,7 — PN-B-01027 poz. 2.5), jezdnia
    pas, jez = s.droga["pas"], s.droga["jezdnia"]
    if jez is not None and clip(jez, win) is not None:
        c.fill(clip(jez, win), "Z-DROGA", "#e6e6e6", z=8.0)
        draw_geom(c, clip(jez.exterior, win), "Z-MAPA", pen=0.25, lt="CIAGLA")
        used.add("jezdnia")
    if pas is not None:
        draw_geom(c, clip(pas.exterior, win), "Z-DROGA", pen=0.7, lt="CIAGLA", color="#303030")
        used.add("rozgraniczajaca")
    # budynki sąsiednie (kreskowanie 45° cienkie, opis funkcja + liczba kondygnacji wg BDOT500)
    from ..draft.hatch import _parallel
    for x in s.sasiedzi:
        g = clip(x["bud"], win)
        if g is None:
            continue
        fill_white(c, g)
        for ln in _parallel(g, 45.0, 1.5 * k):
            c.polyline(ln, "Z-MAPA", pen=0.13, color="#8a8a8a")
        draw_geom(c, g, "Z-MAPA", pen=0.35, lt="CIAGLA", color="#3a3a3a")
        used.add("bud_sasiedni")
    lab.reg(n0, w_line=0.3, w_fill=0.3)
    for x in s.sasiedzi:
        g = clip(x["bud"], win)
        if g is not None:
            txt = "m" + (str(x["kond"]) if x.get("kond") else "")
            p = np.asarray(g.representative_point().coords[0])
            n1 = lab.mark()
            c.text(p, txt, 3.5, 0.0, "center", "middle", "Z-MAPA-OPISY", style="italic", color=GREY, mask=0.6)
            lab.reg(n1)
    # uzbrojenie istniejące
    for sx in [x for x in s.sieci if x.istn]:
        g = clip(sx.geom, win)
        if g is not None:
            utility(c, g, sx, existing=True)
            used.add(f"ist_{sx.branza}")
    lab.reg(n0, w_line=0.25)
    return n0


def label_base_map(c, s, lab: Labeler, win: Polygon, used: set, opts: dict, spot_every=9.0, contours=True):
    """Opisy podkładu po narysowaniu projektu (niższy priorytet niż treść projektu)."""
    k = c.k
    # numery działek
    for x in s.sasiedzi:
        g = clip(x["poly"], win)
        if g is None:
            continue
        free = g.difference(x["bud"].buffer(1.0)) if x["bud"] is not None else g
        p = np.asarray((free if not free.is_empty else g).representative_point().coords[0])
        lab.label(p, [x["nr"]], 3.5, "Z-MAPA-OPISY", "italic", GREY, dists=(0.0, 3.0, 8.0, 14.0), leader_from=99,
                  max_cost=6.0)
    for sx in [x for x in s.sieci if x.istn]:
        g = clip(sx.geom, win)
        if g is None:
            continue
        for ls in (g.geoms if hasattr(g, "geoms") else [g]):
            lab.along(ls, sx.lit, H, "Z-SIECI-IST", sx.kolor, n=3, max_cost=3.0)
            short = sx.opis.split("(")[0].split(",")[0].strip()
            lab.along(ls, f"{sx.lit} — {short}", H, "Z-SIECI-IST", sx.kolor, n=1, max_cost=6.0,
                      fracs=[0.35, 0.3, 0.4, 0.25, 0.45, 0.2, 0.5, 0.55, 0.6, 0.65])
    if s.droga["pas"] is not None and clip(s.droga["pas"], win) is not None:
        g = clip(s.droga["pas"], win)
        cy = g.centroid.y
        x0, _y0, x1, _y1 = g.bounds
        axis = LineString([(x0, cy), (x1, cy)])
        lab.along(axis, f"{s.droga['symbol']} — {s.droga['nazwa']}", 3.5, "Z-MAPA-OPISY", GREY, n=1, max_cost=30.0,
                  style="bold")
    if contours:
        bb = win.bounds
        for pts, Hh in s.contours(bb):
            ls = LineString(pts)
            g = clip(ls, win.buffer(-1.0 * k))
            if g is None:
                continue
            for part in (g.geoms if hasattr(g, "geoms") else [g]):
                lab.along(part, f"{Hh:.2f}".replace(".", ","), H, "Z-RZEDNE", None, n=1, max_cost=2.5)


def draw_contours(c, s, win: Polygon, used: set, projected=False, exclude=None):
    """Warstwice terenu istniejącego (0,18) / projektowanego (0,5) — PN-B-01027 poz. 5.2."""
    n = 0
    zone = s.strefa_zmian if projected else None
    for pts, _Hh in s.contours(win.bounds, projected=projected):
        g = clip(LineString(pts), win)
        if g is None:
            continue
        if exclude is not None:
            g = g.difference(exclude)
        if zone is not None:
            g = g.intersection(zone)
        if g.is_empty:
            continue
        draw_geom(c, g, "Z-RZEDNE-PROJ" if projected else "Z-RZEDNE", pen=0.5 if projected else 0.18, lt="CIAGLA",
                  color=None if projected else "#8a5a2a")
        n += 1
    if n:
        used.add("warstwice_proj" if projected else "warstwice")


# ================================================================================================ sieci
def utility(c, g, sx, existing=False, pen=None, inside=None, flow=True, every_mm=30.0):
    """Sieć/przyłącze (kolor i litera wg mapy zasadniczej; grubości PN-B-01027: kanalizacja, kabel e 0,7;
    wodociąg, telekomunikacja 0,5; istniejące 0,35). ``inside`` — obszar (budynek), w którym linia kreskowa
    (przewód pod płytą / w budynku); kierunek przepływu kanalizacji — trójkąty (Ks pełny, Kd pusty)."""
    k = c.k
    col = sx.kolor
    w = pen or (0.35 if existing else (0.7 if sx.branza in ("kan_sanit", "kan_deszcz", "en") else 0.5))
    layer = "Z-SIECI-IST" if existing else "Z-SIECI-PROJ"
    parts_out, parts_in = [g], []
    if inside is not None and not inside.is_empty:
        parts_out = [g.difference(inside)]
        parts_in = [g.intersection(inside)]
    for pg in parts_out:
        draw_geom(c, pg, layer, pen=w, lt="CIAGLA", color=col)
    for pg in parts_in:
        draw_geom(c, pg, layer, pen=0.35, lt="KRESKOWA", color=col)
    if flow and not existing and sx.branza in ("kan_sanit", "kan_deszcz"):
        for ls in [LineString(a) for a in lines_of(parts_out[0]) if len(a) >= 2]:
            L = ls.length
            s_ = every_mm * k * 0.5
            while s_ < L - 2 * k:
                p = np.asarray(ls.interpolate(s_).coords[0])
                q = np.asarray(ls.interpolate(min(L, s_ + 0.1 * k)).coords[0])
                d = unit(q - p)
                nn = perp(d)
                a = 2.4 * k
                tri = [p + d * a * 0.87, p + nn * a / 2, p - nn * a / 2]
                if sx.branza == "kan_sanit":
                    c.fill(tri, layer, col)
                else:
                    c.fill(tri, layer, "#ffffff", z=21.5)
                c.polygon(tri, layer, pen=0.25, color=col, z=21.6)
                s_ += every_mm * k


def cross_mark(c, p, layer="Z-SIECI-PROJ", size_mm=1.4, pen=0.5, color=None):
    """„×” w miejscu włączenia do sieci istniejącej (PN-B-01027 poz. 6)."""
    k = c.k
    a = size_mm * k
    P = np.asarray(p, float)
    c.line(P + [-a, -a], P + [a, a], layer, pen=pen, color=color)
    c.line(P + [-a, a], P + [a, -a], layer, pen=pen, color=color)


# ================================================================================================ projekt
def paving_kind(txt: str):
    t = (txt or "").lower()
    if "fundament" in t:
        return None
    if "ażur" in t or "azur" in t or "w trawie" in t:
        return "azur"
    if "kostk" in t:
        return "drobne"
    if "płyt" in t or "plyt" in t:
        return "duze"
    if "desk" in t:
        return "deska"
    if "żwir" in t or "zwir" in t:
        return "zwir"
    if "asfalt" in t:
        return "asfalt"
    return "duze"


def draw_hardscape(c, s, used: set, hatch=True, band_mm=None, opaska_polys=()):
    """Nawierzchnie utwardzone (PN-B-01027 poz. 7.10–7.11), tarasy, opaska żwirowa."""
    from ..draft import symbols as S
    from ..draft.hatch import _dots, _rng
    k = c.k
    band = band_mm if band_mm is not None else (3.0 if c.scale >= 400 else 5.0)
    for u in s.utwardzenia:
        pg = u["poly"].difference(s.p0)
        if pg.is_empty:
            continue
        kind = paving_kind(u["raw"].get("nawierzchnia", ""))
        fill_white(c, pg)
        if kind is None:
            draw_geom(c, pg, "Z-UTWARDZENIA", pen=0.35, lt="CIAGLA")
            continue
        if hatch:
            if kind == "azur":
                S.paving(c, pg, "duze", outline=False)
                _dots(c, pg, 0.15, _rng(pg), "Z-ZIELEN", 0.14, pen=0.25)
            else:
                S.paving(c, pg, kind, outline=False, band_mm=band if kind == "drobne" else None)
        draw_geom(c, pg, "Z-UTWARDZENIA", pen=0.35, lt="CIAGLA")
        used.add(f"naw_{kind}")
    for t in s.tarasy:
        pg = t["poly"].difference(s.p0)
        if pg.is_empty:
            continue
        fill_white(c, pg)
        kind = paving_kind(t["naw"]) or "duze"
        if hatch:
            S.paving(c, pg, kind, outline=False, angle=0.0, band_mm=band if kind == "drobne" else None)
        draw_geom(c, pg, "Z-UTWARDZENIA", pen=0.35, lt="CIAGLA")
        used.add("taras" if kind == "deska" else f"naw_{kind}")
    for o in opaska_polys:
        fill_white(c, o["poly"])
        if hatch:
            _dots(c, o["poly"], 0.35, _rng(o["poly"]), "Z-UTWARDZENIA", 0.3, pen=0.25)
        draw_geom(c, o["poly"], "Z-UTWARDZENIA", pen=0.18, lt="CIAGLA")
        used.add("opaska")


def hedge_axis(pg: Polygon):
    """Oś i szerokość pasa (prostokąt obrócony minimalny)."""
    r = pg.minimum_rotated_rectangle
    C = np.asarray(r.exterior.coords)[:4]
    e = [np.hypot(*(C[(i + 1) % 4] - C[i])) for i in range(4)]
    i = int(np.argmax(e))
    a, b = C[i], C[(i + 1) % 4]
    w = min(e)
    off = unit(C[(i + 2) % 4] - b) * w / 2
    return a + off, b + off, w


def draw_green(c, s, used: set, cover=None, lawn=True, trees=True, labels_lab=None, green=None):
    """Zieleń: trawnik (kropki), rabaty, żywopłoty, drzewa istniejące/projektowane/do usunięcia (PN-B-01027 poz. 7)."""
    from ..draft import symbols as S
    k = c.k
    rab = [z for z in s.zielen if str(z["raw"].get("typ")) == "rabata"]
    hed = [z for z in s.zielen if str(z["raw"].get("typ")) == "zywoplot"]
    if lawn and green is not None:
        g = green.difference(unary_union([z["poly"] for z in rab + hed] or [Polygon()]))
        if s.rozsaczanie and s.rozsaczanie["poly"] is not None:
            g = g.difference(s.rozsaczanie["poly"])
        S.lawn(c, g, 2.0 if c.scale >= 400 else 1.4, seed=7)
        used.add("trawnik")
    for z in rab:
        pg = z["poly"].difference(s.p0)
        draw_geom(c, pg, "Z-ZIELEN", pen=0.25, lt="KRESKOWA")
        step = max(1.6, 5.0 * k)
        x0, y0, x1, y1 = pg.bounds
        for x in np.arange(x0 + step / 2, x1, step):
            for y in np.arange(y0 + step / 2, y1, step):
                if pg.buffer(-0.3).contains(Point(x, y)):
                    S.shrub(c, (x, y), min(1.0, max(0.6, 3.0 * k)))
        used.add("rabata")
    for z in hed:
        a, b, w = hedge_axis(z["poly"])
        S.hedge(c, [a, b], width=min(w, 1.2), conifer=False)
        used.add("zywoplot")
    if trees:
        for t in s.drzewa:
            S.tree(c, t["xy"], t["d"], existing=t["istn"], remove=t["usun"], conifer=t["iglaste"])
            used.add("drzewo_ist" if t["istn"] else "drzewo_proj")
            if t["usun"]:
                used.add("drzewo_usun")


def draw_building(c, s, used: set, slab_lt="PUNKTOWA", pen_outline=1.4):
    """Budynek: obrys przyziemia 1,4 (PN-B-01027 poz. 1.1), obrys wyższych kondygnacji — kreskowa 0,7 (poz. 1.6d),
    płyty/okapy/daszki wykraczające poza obrys — ``slab_lt`` 0,7 (poz. 1.6c: punktowa), wejście główne (poz. 1.7)."""
    from ..draft import symbols as S
    from ..draft.dims import arrowhead
    k = c.k
    fill_white(c, s.p0, z=9.6)
    draw_geom(c, s.upper_lines, "Z-BUDYNEK-NAD", pen=0.7, lt="KRESKOWA")
    if not s.upper_lines.is_empty:
        used.add("bud_wyzsze")
    draw_geom(c, s.slab_lines, "Z-BUDYNEK-NAD", pen=0.7 if slab_lt == "PUNKTOWA" else 0.5, lt=slab_lt)
    if not s.slab_lines.is_empty:
        used.add("bud_plyty")
    draw_geom(c, s.p0, "Z-BUDYNEK", pen=pen_outline, lt="CIAGLA")
    used.add("budynek")
    e = s.wejscie_gl
    if e is not None:
        ang = math.degrees(math.atan2(-e["out"][1], -e["out"][0]))
        S.site_entrance(c, e["pt"], ang, layer="Z-BUDYNEK")
        used.add("wejscie")
    for w in s.wjazdy:
        a = w["pt"] + w["out"] * 9.0 * k
        b = w["pt"] + w["out"] * 1.2 * k
        c.line(a, b, "Z-BUDYNEK", pen=0.35)
        arrowhead(c, b, b - a, 2.5, 14, False, "Z-BUDYNEK", pen=0.35)
        used.add("wjazd")


def draw_building_line(c, s, used: set, win=None):
    """Nieprzekraczalna linia zabudowy (PN-B-01027 poz. 2.2): ciągła 0,35 z niezaczernionymi trójkątami 2 mm
    (rytm 12·2·12) po stronie terenu zabudowy."""
    from .site_data import linia_zabudowy_spr
    lz = s.linia_zabudowy
    if lz is None:
        return
    g = clip(lz, win) if win is not None else lz
    if g is None:
        return
    k = c.k
    spr = linia_zabudowy_spr(s)
    n = spr.get("n", np.array([0.0, -1.0]))
    col = styles.layer("Z-LZ").plot_rgb
    for a in lines_of(g):
        c.polyline(a, "Z-LZ", pen=0.35, lt="CIAGLA", color=col)
        ls = LineString(a)
        L = ls.length
        d = unit(a[-1] - a[0])
        side = 1.0 if float(perp(d) @ n) > 0 else -1.0
        t = 7.0 * k
        while t < L:
            p = np.asarray(ls.interpolate(t).coords[0])
            s2 = 1.0 * k
            tri = [p - d * s2, p + d * s2, p + perp(d) * side * 2.0 * k * 0.866]
            c.polygon(tri, "Z-LZ", pen=0.25, lt="CIAGLA", color=col)
            t += 14.0 * k
    used.add("linia_zabudowy")


def draw_plot_boundary(c, s, used: set, labels=True):
    """Granica działki budowlanej (PN-B-01027 poz. 2.7): ciągła 0,35, punkty Ø1,0 mm, narożniki — kółko z literą."""
    k = c.k
    if s.plot.is_empty:
        return []
    C = s.corners
    c.polyline(C, "Z-DZIALKA", closed=True, pen=0.35, lt="CIAGLA", color="#000000")
    ctr = np.asarray(s.plot.centroid.coords[0])
    out = []
    for i, p in enumerate(C):
        c.dot(p, 1.0, "Z-DZIALKA")
        if labels:
            q = p + unit(p - ctr) * 4.2 * k
            lab = chr(ord("A") + i)
            c.fill(circle_pts(q, 2.3 * k, 24), "Z-DZIALKA", "#ffffff", z=26.2)
            c.circle(q, 2.3 * k, "Z-DZIALKA", pen=0.25, z=26.3)
            c.text(q, lab, H, 0.0, "center", "middle", "Z-DZIALKA")
            out.append((lab, p))
    used.add("granica")
    return out


def _inward_offset(s, ls: LineString, d):
    for sg in (1.0, -1.0):
        o = ls.offset_curve(sg * d)
        if o is not None and not o.is_empty and s.plot.buffer(1e-6).contains(o.interpolate(0.5, normalized=True)):
            return o
    return ls


def draw_fence(c, s, used: set):
    """Ogrodzenie (PN-B-01027 poz. 2.8 — 0,35 z kreskami; odsunięte 0,6 mm do wnętrza działki, gdy biegnie po
    granicy), bramy i furtki (poz. 2.9) otwierane do wewnątrz działki (WT § 42)."""
    from ..draft import symbols as S
    k = c.k
    for f in s.ogrodzenie:
        g = f["geom"]
        on_b = g.buffer(0.05).within(s.plot.exterior.buffer(0.1))
        if on_b:
            g = _inward_offset(s, g, 0.6 * k)
        for a in lines_of(g):
            if len(a) >= 2 and LineString(a).length > 0.2:
                S.fence(c, a, "Z-OGRODZENIE")
        used.add("ogrodzenie")
    for b in s.bramy:
        d = b["kier"]
        p1, p2 = b["xy"] - d * b["szer"] / 2, b["xy"] + d * b["szer"] / 2
        if b["typ"] == "furtka":
            inside = s.plot.contains(Point(b["xy"] + perp(d) * 0.3))
            if not inside:
                p1, p2 = p2, p1
            S.gate(c, p1, p2, "furtka", "Z-OGRODZENIE")
            used.add("furtka")
        else:
            nin = perp(d)
            if not s.plot.contains(Point(b["xy"] + nin * 0.3)):
                p1, p2 = p2, p1
            S.gate(c, p1, p2, "przesuwna", "Z-OGRODZENIE")
            used.add("brama")


def draw_parking(c, s, used: set):
    """Miejsca postojowe (PN-B-01027 poz. 3.4: krawędzie 0,25, opis „P”); w garażu — tylko opis w budynku."""
    for q in s.miejsca:
        pg = q["poly"]
        if pg.difference(s.p0).area < 0.1:
            continue
        draw_geom(c, pg, "Z-UTWARDZENIA", pen=0.25, lt="CIAGLA")
        used.add("parking")


def draw_bins(c, s, used: set):
    """Miejsce na pojemniki na odpady (WT § 22): obrys osłony 0,35 + pojemniki."""
    o = s.odpady
    if not o or o["poly"] is None:
        return
    pg = o["poly"]
    draw_geom(c, pg, "Z-OGRODZENIE", pen=0.35, lt="CIAGLA")
    a, b, w = hedge_axis(pg)
    n = max(1, min(6, int(round(np.hypot(*(b - a)) / 0.8))))
    d = unit(b - a)
    nn = perp(d)
    L = np.hypot(*(b - a))
    for i in range(n):
        m = a + d * (L * (i + 0.5) / n)
        q = [m - d * 0.3 - nn * 0.3, m + d * 0.3 - nn * 0.3, m + d * 0.3 + nn * 0.3, m - d * 0.3 + nn * 0.3]
        c.polygon(q, "Z-OGRODZENIE", pen=0.18, lt="CIAGLA")
    used.add("odpady")


def draw_pc(c, s, used: set):
    """Jednostka zewnętrzna pompy ciepła + strefa czynnika R290 (kreskowanie 45°, obrys kreskowy)."""
    from ..draft.hatch import _parallel
    if s.pc is None:
        return
    k = c.k
    Z = s.pc["strefa"].difference(s.p0)
    for ln in _parallel(Z.difference(s.pc["body"]), 45.0, 1.2 * k):
        c.polyline(ln, "Z-STREFY", pen=0.13)
    draw_geom(c, Z, "Z-STREFY", pen=0.25, lt="KRESKOWA")
    fill_white(c, s.pc["body"], z=9.7)
    draw_geom(c, s.pc["body"], "Z-UZBROJENIE", pen=0.5, lt="CIAGLA")
    b = s.pc["body"].bounds
    c.line((b[0], b[1]), (b[2], b[3]), "Z-UZBROJENIE", pen=0.18)
    used.add("pc")


def draw_retention(c, s, used: set):
    """Zbiornik retencyjny (prostokąt ≥ 7×4 mm — jak osadnik, PN-B-01027 poz. 6) i niecka chłonna."""
    from ..draft.hatch import _parallel
    k = c.k
    if s.rozsaczanie and s.rozsaczanie["poly"] is not None:
        pg = s.rozsaczanie["poly"]
        fill_white(c, pg, z=9.8)
        for ln in _parallel(pg.buffer(-0.8 * k), 0.0, 1.6 * k):
            L = LineString(ln)
            pts = []
            n = max(4, int(L.length / (0.6 * k)))
            for i in range(n + 1):
                p = np.asarray(L.interpolate(L.length * i / n).coords[0])
                pts.append(p + np.array([0.0, 0.25 * k * (1 if i % 2 else -1)]))
            c.polyline(pts, "Z-ODWODNIENIE", pen=0.18)
        draw_geom(c, pg, "Z-ODWODNIENIE", pen=0.5, lt="CIAGLA")
        used.add("niecka_chlonna")
    zb = s.zbiornik
    if zb:
        if zb["poly"] is not None or zb.get("sr"):
            g = zb["poly"] or Point(zb["xy"]).buffer(float(zb["sr"]) / 2)
        else:
            w, h = max(7.0 * k, 1.5), max(4.0 * k, 0.9)
            x, y = zb["xy"]
            g = box(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        fill_white(c, g, z=9.8)
        draw_geom(c, g, "Z-ODWODNIENIE", pen=0.5, lt="CIAGLA")
        c.text(zb["xy"], "ZB", H, 0.0, "center", "middle", "Z-ODWODNIENIE")
        zb["draw_poly"] = g
        used.add("zbiornik")


def draw_drainage(c, s, used: set, detail=False, lab: Labeler | None = None):
    """Odwodnienie powierzchniowe: odwodnienia liniowe (linia 0,5 z kratką), niecki trawiaste z kierunkiem spływu."""
    from ..draft.dims import arrowhead
    k = c.k
    for o in s.odwodnienia:
        g = o["geom"]
        if g is None or g.length < 0.05:
            continue
        if o["typ"] == "liniowe":
            for off in (-0.45 * k, 0.45 * k):
                c.polyline(np.asarray(g.offset_curve(off).coords), "Z-ODWODNIENIE", pen=0.25)
            L = g.length
            t = 0.6 * k
            while t < L:
                p = np.asarray(g.interpolate(t).coords[0])
                q = np.asarray(g.interpolate(min(L, t + 0.01)).coords[0])
                nn = perp(unit(q - p)) * 0.45 * k
                c.line(p - nn, p + nn, "Z-ODWODNIENIE", pen=0.18)
                t += 1.0 * k
            used.add("odw_liniowe")
        elif o["typ"] == "niecka":
            c.polyline(np.asarray(g.coords), "Z-ODWODNIENIE", pen=0.35, lt="KRESKA_DLUGA")
            a, b = np.asarray(g.coords[0]), np.asarray(g.coords[-1])
            ha, hb = s.H_proj(a)[0], s.H_proj(b)[0]
            lo, hi = (a, b) if ha <= hb else (b, a)
            ls = LineString([hi, lo]) if len(g.coords) == 2 else (g if ha > hb else LineString(g.coords[::-1]))
            L = ls.length
            for f in (0.35, 0.8):
                p = np.asarray(ls.interpolate(f * L).coords[0])
                q = np.asarray(ls.interpolate(min(L, f * L + 3.0 * k)).coords[0])
                arrowhead(c, q, q - p, 2.5, 12, True, "Z-ODWODNIENIE", pen=0.25)
            used.add("odw_niecka")


def draw_downpipes(c, s, used: set):
    """Rury spustowe (budynek.yaml: dachy[].rury_spustowe) — kółko Ø1,5 mm; wewnętrzne (w szachcie) — kreskowe."""
    k = c.k
    for r in s.rury:
        c.circle(r["xy"], 0.9 * k, "Z-ODWODNIENIE", pen=0.35, lt="CIAGLA" if r["trasa"] == "zewn" else "KRESKOWA_DROBNA")
        c.dot(r["xy"], 0.5, "Z-ODWODNIENIE")
        used.add("rura_spustowa")


def zjazd_poly(s, skos=1.0):
    """Zjazd: z modelu (dzialka.yaml: zjazd.obrys) albo przedłużenie bramy wjazdowej do krawędzi jezdni ze skosami
    ``skos`` [m] — geometria zastępcza [DO UZUPEŁNIENIA wg zezwolenia zarządcy drogi]."""
    if s.zjazd and s.zjazd["poly"] is not None:
        return s.zjazd["poly"], False
    jez = s.droga["jezdnia"]
    b = next((x for x in s.bramy if x["typ"] == "przesuwna"), None) or \
        next((x for x in s.bramy if x["typ"] != "furtka"), None)
    if b is None or jez is None:
        return None, True
    d = b["kier"]
    u = perp(d)
    if s.plot.contains(Point(b["xy"] + u * 0.3)):
        u = -u
    ray = LineString([b["xy"], b["xy"] + u * 60.0])
    X = ray.intersection(jez)
    if X.is_empty:
        return None, True
    t = min(np.hypot(*(np.asarray(q) - b["xy"])) for q in (X.coords if X.geom_type == "LineString" else
                                                          [g.coords[0] for g in X.geoms]))
    w = b["szer"] / 2
    G = b["xy"]
    pg = Polygon([G - d * w, G + d * w, G + d * (w + skos) + u * t, G - d * (w + skos) + u * t])
    return pg, True


def draw_objects(c, s, used: set, win=None):
    """Obiekty uzbrojenia: ZK/ZKP (prostokąt z przekątną), studzienki (okrąg rzeczywisty ≥ 2 mm), studnia
    chłonna, hydrant (PN-B-01027 poz. 6)."""
    k = c.k
    for o in s.obiekty.values():
        if win is not None and not win.contains(Point(o.xy)):
            continue
        idu = o.id.upper()
        t = o.opis.lower()
        if idu.startswith("ZK"):
            fence = next((f["geom"] for f in s.ogrodzenie if f["geom"].distance(Point(o.xy)) < 1.0), None)
            ang = 0.0
            if fence is not None:
                q = fence.interpolate(fence.project(Point(o.xy)))
                q2 = fence.interpolate(min(fence.length, fence.project(Point(o.xy)) + 0.1))
                ang = math.degrees(math.atan2(q2.y - q.y, q2.x - q.x))
            w, d = 0.9, 0.35
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            R = np.array([[ca, -sa], [sa, ca]])
            q = (np.array([[-w / 2, -d / 2], [w / 2, -d / 2], [w / 2, d / 2], [-w / 2, d / 2]]) @ R.T) + o.xy
            fill_white(c, Polygon(q), z=21.0)
            c.polygon(q, "Z-UZBROJENIE", pen=0.5, color=BRANZE_COL("en"))
            c.line(q[0], q[2], "Z-UZBROJENIE", pen=0.25, color=BRANZE_COL("en"))
            used.add("zkp")
        elif idu.startswith("HYD"):
            c.circle(o.xy, 1.5 * k, "Z-SIECI-IST", pen=0.35, color=BRANZE_COL("woda"))
            c.dot(o.xy, 0.8, "Z-SIECI-IST", color=BRANZE_COL("woda"))
            used.add("hydrant")
        elif idu.startswith("PC"):
            continue
        elif "studnia" in t or "chłonn" in t:
            c.circle(o.xy, max(0.4, 1.2 * k), "Z-ODWODNIENIE", pen=0.35)
            c.circle(o.xy, max(0.25, 0.6 * k), "Z-ODWODNIENIE", pen=0.18)
            used.add("studnia_chlonna")
        else:
            dm = 0.425 if "425" in t else 1.0 if "1000" in t else 0.6
            r = max(dm / 2, 1.0 * k)
            col = BRANZE_COL("kan_sanit") if ("kanaliz" in t or "rewiz" in t) else None
            fill_white(c, Point(o.xy).buffer(r), z=21.0)
            c.circle(o.xy, r, "Z-UZBROJENIE", pen=0.35, color=col)
            c.dot(o.xy, 0.5, "Z-UZBROJENIE", color=col or "#000000")
            used.add("studzienka")


def BRANZE_COL(b):
    from .site_data import BRANZE
    return BRANZE.get(b, ("", "", "#000000"))[2]


def draw_utilities(c, s, used: set, win=None, inside=None, marks=True):
    """Sieci projektowane (przyłącza, kolektory) z oznaczeniem miejsc włączenia „×”."""
    for sx in [x for x in s.sieci if not x.istn]:
        g = clip(sx.geom, win) if win is not None else sx.geom
        if g is None:
            continue
        utility(c, g, sx, existing=False, inside=inside)
        used.add(f"proj_{sx.branza}")
        if marks:
            for q in (sx.geom.coords[0], sx.geom.coords[-1]):
                if any(E.istn and E.branza == sx.branza and E.geom.distance(Point(q)) < 0.05 for E in s.sieci):
                    cross_mark(c, q, color=sx.kolor)
                    used.add("wlaczenie")


# ================================================================================================ wymiary i rzędne
def dim_pts(c, a, b, h=H, label=None, layer="Z-WYMIARY"):
    """Wymiar odcinka a–b w m (2 miejsca — RPB § 15 ust. 3), linie 0,18 (PN-B-01027 poz. 4.1)."""
    from ..draft import dims
    a, b = np.asarray(a, float), np.asarray(b, float)
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return dims.dim_chain(c, [a, b], a, ang, layer=layer, h=h, unit_="m", tick_pen=0.18, ext_len=(1.5, 1.5),
                          overshoot_mm=1.5, tick_mm=2.5, labels=[label] if label else None, mask=0.3)


def place_dim(lab: Labeler, a, b, el=None, bnd=None, span=8.0, step=0.25, label=None, max_cost=None,
              prefer=0.0):
    """Wymiar odległości a–b (np. lico ściany – granica) przesuwany równolegle (wzdłuż lica) w miejsce o
    najmniejszej kolizji; ``el``/``bnd`` — geometrie, na których muszą leżeć końce po przesunięciu."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    if np.hypot(*(b - a)) < 1e-3:
        return None
    t = perp(unit(b - a))
    shifts = sorted(np.arange(-span, span + 1e-9, step), key=lambda v: abs(v - prefer))
    cands = []
    for sh in shifts:
        a2, b2 = a + t * sh, b + t * sh
        if el is not None and el.distance(Point(a2)) > 0.02:
            continue
        if bnd is not None and bnd.distance(Point(b2)) > 0.02:
            continue
        if el is not None and not isinstance(el, LineString):
            seg = LineString([a2 + unit(b2 - a2) * 0.02, b2])
            if el.buffer(-0.005).intersects(seg):
                continue
        cands.append(sh)
    if not cands:
        cands = [0.0]

    def fn(cv, sh):
        dim_pts(cv, a + t * sh, b + t * sh, label=label)
    pos, _c = lab.pl.place(lab.vp, fn, cands, penalty_step=0.01, max_cost=max_cost)
    return pos


def spot(lab: Labeler, p, Hh, projected=False, max_cost=None, dists=(0.6, 1.5, 3.0, 5.0), dirs=None,
         color=None, h=H):
    """Rzędna terenu (m n.p.m., 2 miejsca): istniejąca — krzyżyk + wartość kursywą; projektowana — kropka +
    wartość w ramce (PN-B-01025, praktyka PZT)."""
    c = lab.vp
    k = c.k
    P = np.asarray(p, float)
    txt = f"{Hh:.2f}".replace(".", ",")
    n0 = lab.mark()
    if projected:
        c.dot(P, 0.9, "Z-RZEDNE-PROJ")
        layer, style = "Z-RZEDNE-PROJ", "normal"
    else:
        s_ = 0.8 * k
        c.line(P + [-s_, 0], P + [s_, 0], "Z-RZEDNE", pen=0.18, color=color or "#6b4423")
        c.line(P + [0, -s_], P + [0, s_], "Z-RZEDNE", pen=0.18, color=color or "#6b4423")
        layer, style = "Z-RZEDNE", "italic"
    lab.reg(n0, w_fill=0.6, w_line=0.6)
    return lab.label(P, [txt], h, layer, style, color or (None if projected else "#6b4423"), mask=0.4,
                     dists=dists, dirs=dirs, frame=projected, leader_from=2.5, max_cost=max_cost)


def slope_arrow(lab: Labeler, poly, direction, pct, length_mm=10.0, max_cost=None, text=None):
    """Strzałka spadku w polu ``poly`` (grot w kierunku spadku) z wartością w % (PN-B-01025)."""
    from ..draft import dims
    c = lab.vp
    k = c.k
    d = unit(direction)
    L = length_mm * k
    P0 = np.asarray(poly.representative_point().coords[0])
    inner = poly.buffer(-1.0 * k)
    cands = []
    for r in (0.0, 2.0, 4.0, 6.0, 9.0):
        for i in range(8 if r else 1):
            a = 2 * math.pi * i / 8
            q = P0 + np.array([math.cos(a), math.sin(a)]) * r * k
            A, B = q - d * L / 2, q + d * L / 2
            if inner.is_empty or inner.contains(LineString([A, B])):
                cands.append((A, B))
    if not cands:
        cands = [(P0 - d * L / 2, P0 + d * L / 2)]
    lbl = text or (f"{pct * 100:.1f}%".replace(".", ","))

    def fn(cv, ab):
        dims.slope(cv, ab[0], ab[1], text=lbl, h=H, layer="Z-ODWODNIENIE")
    return lab.pl.place(c, fn, cands, penalty_step=0.02, max_cost=max_cost)


# ================================================================================================ legenda (arkusz)
def _lg_line(pen, lt=None, color=None, layer="R-LEGENDA"):
    def f(sh, x, y):
        sh.line((x + 1, y), (x + 15, y), layer, pen=pen, lt=lt or "CIAGLA", color=color)
    return f


def _lg_util(branza, existing):
    def f(sh, x, y):
        from .site_data import BRANZE, Siec
        sx = Siec(branza, LineString([(x + 1, y), (x + 15, y)]), "", existing)
        utility(sh, sx.geom, sx, existing=existing, flow=False)
        sh.text((x + 8, y + 0.9), BRANZE[branza][0], 1.8, 0.0, "center", "bottom", "R-LEGENDA", color=sx.kolor)
    return f


def _lg_rect(kind):
    def f(sh, x, y):
        from ..draft import symbols as S
        from ..draft.hatch import _dots, _rng
        r = box(x + 1, y - 1.8, x + 15, y + 1.8)
        if kind == "jezdnia":
            sh.fill(r, "Z-DROGA", "#e6e6e6")
        elif kind == "bud_sasiedni":
            from ..draft.hatch import _parallel
            for ln in _parallel(r, 45.0, 1.5):
                sh.polyline(ln, "Z-MAPA", pen=0.13, color="#8a8a8a")
            sh.polygon(np.asarray(r.exterior.coords)[:-1], "Z-MAPA", pen=0.35, color="#3a3a3a")
            sh.text((x + 8, y), "m2", 1.8, 0, "center", "middle", "R-LEGENDA", style="italic", mask=0.3)
            return
        elif kind in ("drobne", "duze", "deska"):
            S.paving(sh, r, kind, outline=False, band_mm=1.2 if kind == "drobne" else None)
        elif kind == "azur":
            S.paving(sh, r, "duze", outline=False)
            _dots(sh, r, 0.15, _rng(r, 3), "Z-ZIELEN", 0.14, pen=0.25)
        elif kind == "opaska":
            _dots(sh, r, 0.35, _rng(r, 4), "Z-UTWARDZENIA", 0.3, pen=0.25)
        elif kind == "trawnik":
            S.lawn(sh, r, 3.0, seed=5)
            return
        elif kind == "niecka":
            for yy in (y - 0.8, y + 0.8):
                sh.polyline([(x + 2 + i * 0.6, yy + (0.25 if i % 2 else -0.25)) for i in range(21)], "Z-ODWODNIENIE",
                            pen=0.18)
            sh.polygon(np.asarray(r.exterior.coords)[:-1], "Z-ODWODNIENIE", pen=0.5)
            return
        elif kind == "strefa":
            from ..draft.hatch import _parallel
            for ln in _parallel(r, 45.0, 1.2):
                sh.polyline(ln, "Z-STREFY", pen=0.13)
            sh.polygon(np.asarray(r.exterior.coords)[:-1], "Z-STREFY", pen=0.25, lt="KRESKOWA")
            b = box(x + 5.5, y - 0.9, x + 10.5, y + 0.9)
            sh.fill(b, "Z-TLO", "#ffffff", z=20)
            sh.polygon(np.asarray(b.exterior.coords)[:-1], "Z-UZBROJENIE", pen=0.5)
            sh.line((x + 5.5, y - 0.9), (x + 10.5, y + 0.9), "Z-UZBROJENIE", pen=0.18)
            return
        elif kind == "zbiornik":
            b = box(x + 4.5, y - 2.0, x + 11.5, y + 2.0)
            sh.polygon(np.asarray(b.exterior.coords)[:-1], "Z-ODWODNIENIE", pen=0.5)
            sh.text((x + 8, y), "ZB", 1.8, 0, "center", "middle", "Z-ODWODNIENIE")
            return
        elif kind == "zjazd":
            sh.polygon(np.asarray(r.exterior.coords)[:-1], "Z-UTWARDZENIA", pen=0.35, lt="KRESKOWA")
            return
        pen = 0.35 if kind != "jezdnia" else 0.25
        sh.polygon(np.asarray(r.exterior.coords)[:-1], "Z-UTWARDZENIA", pen=pen)
    return f


def _lg_sym(kind):
    def f(sh, x, y):
        from ..draft import symbols as S
        from ..draft.dims import arrowhead, slope
        p = np.array([x + 8.0, y])
        if kind == "granica":
            sh.line((x + 1, y), (x + 15, y), "Z-DZIALKA", pen=0.35, lt="CIAGLA", color="#000000")
            sh.dot((x + 1, y), 1.0, "Z-DZIALKA")
            sh.dot((x + 15, y), 1.0, "Z-DZIALKA")
            sh.fill(circle_pts(p, 2.0, 24), "Z-DZIALKA", "#ffffff", z=26.2)
            sh.circle(p, 2.0, "Z-DZIALKA", pen=0.25, z=26.3)
            sh.text(p, "A", 1.8, 0, "center", "middle", "Z-DZIALKA")
        elif kind == "linia_zabudowy":
            col = styles.layer("Z-LZ").plot_rgb
            sh.line((x + 1, y), (x + 15, y), "Z-LZ", pen=0.35, lt="CIAGLA", color=col)
            for xx in (x + 4.5, x + 11.5):
                sh.polygon([(xx - 1, y), (xx + 1, y), (xx, y - 1.73)], "Z-LZ", pen=0.25, lt="CIAGLA", color=col)
        elif kind == "wejscie":
            S.site_entrance(sh, (x + 10, y), 0.0, layer="Z-BUDYNEK")
        elif kind == "wjazd":
            sh.line((x + 2, y), (x + 13, y), "Z-BUDYNEK", pen=0.35)
            arrowhead(sh, (x + 14, y), (1, 0), 2.5, 14, False, "Z-BUDYNEK", pen=0.35)
        elif kind == "zywoplot":
            S.hedge(sh, [(x + 1, y), (x + 15, y)], width=1.6)
        elif kind == "rabata":
            sh.polygon(np.asarray(box(x + 1, y - 1.8, x + 15, y + 1.8).exterior.coords)[:-1], "Z-ZIELEN", pen=0.25,
                       lt="KRESKOWA")
            for xx in (x + 4.5, x + 8, x + 11.5):
                S.shrub(sh, (xx, y), 2.2)
        elif kind in ("drzewo_proj", "drzewo_ist", "drzewo_usun"):
            S.tree(sh, p, 5.0, existing=kind != "drzewo_proj", remove=kind == "drzewo_usun")
        elif kind == "ogrodzenie":
            S.fence(sh, [(x + 1, y), (x + 15, y)], "Z-OGRODZENIE")
        elif kind == "brama":
            S.gate(sh, (x + 2, y - 1.5), (x + 14, y - 1.5), "przesuwna", "Z-OGRODZENIE")
        elif kind == "furtka":
            sh.line((x + 1, y - 1.5), (x + 5, y - 1.5), "Z-OGRODZENIE", pen=0.35)
            S.gate(sh, (x + 5, y - 1.5), (x + 9, y - 1.5), "furtka", "Z-OGRODZENIE")
        elif kind == "parking":
            sh.polygon(np.asarray(box(x + 3, y - 2.0, x + 13, y + 2.0).exterior.coords)[:-1], "Z-UTWARDZENIA",
                       pen=0.25)
            sh.text(p, "P", 1.8, 0, "center", "middle", "R-LEGENDA", style="bold")
        elif kind == "odpady":
            sh.polygon(np.asarray(box(x + 2, y - 1.5, x + 14, y + 1.5).exterior.coords)[:-1], "Z-OGRODZENIE",
                       pen=0.35)
            for xx in (x + 4, x + 7, x + 10, x + 12.5):
                sh.polygon(np.asarray(box(xx - 0.9, y - 0.9, xx + 0.9, y + 0.9).exterior.coords)[:-1],
                           "Z-OGRODZENIE", pen=0.18)
        elif kind == "odw_liniowe":
            for off in (-0.45, 0.45):
                sh.line((x + 1, y + off), (x + 15, y + off), "Z-ODWODNIENIE", pen=0.25)
            for xx in np.arange(x + 1.5, x + 15, 1.0):
                sh.line((xx, y - 0.45), (xx, y + 0.45), "Z-ODWODNIENIE", pen=0.18)
        elif kind == "odw_niecka":
            sh.line((x + 1, y), (x + 15, y), "Z-ODWODNIENIE", pen=0.35, lt="KRESKA_DLUGA")
            arrowhead(sh, (x + 12, y), (1, 0), 2.5, 12, True, "Z-ODWODNIENIE", pen=0.25)
        elif kind == "rura_spustowa":
            sh.circle((x + 5, y), 0.9, "Z-ODWODNIENIE", pen=0.35)
            sh.dot((x + 5, y), 0.5, "Z-ODWODNIENIE")
            sh.circle((x + 11, y), 0.9, "Z-ODWODNIENIE", pen=0.35, lt="KRESKOWA_DROBNA")
            sh.dot((x + 11, y), 0.5, "Z-ODWODNIENIE")
        elif kind == "wlaczenie":
            sh.line((x + 1, y), (x + 8, y), "Z-SIECI-IST", pen=0.35, color="#0050c8")
            sh.line((x + 8, y), (x + 8, y - 2), "Z-SIECI-PROJ", pen=0.5, color="#0050c8")
            cross_mark(sh, (x + 8, y), color="#0050c8")
        elif kind == "zkp":
            q = [(x + 5, y - 1), (x + 11, y - 1), (x + 11, y + 1), (x + 5, y + 1)]
            sh.polygon(q, "Z-UZBROJENIE", pen=0.5, color=BRANZE_COL("en"))
            sh.line(q[0], q[2], "Z-UZBROJENIE", pen=0.25, color=BRANZE_COL("en"))
        elif kind == "studzienka":
            sh.circle(p, 1.2, "Z-UZBROJENIE", pen=0.35, color=BRANZE_COL("kan_sanit"))
            sh.dot(p, 0.5, "Z-UZBROJENIE", color=BRANZE_COL("kan_sanit"))
        elif kind == "studnia_chlonna":
            sh.circle(p, 1.4, "Z-ODWODNIENIE", pen=0.35)
            sh.circle(p, 0.7, "Z-ODWODNIENIE", pen=0.18)
        elif kind == "hydrant":
            sh.circle(p, 1.5, "Z-SIECI-IST", pen=0.35, color=BRANZE_COL("woda"))
            sh.dot(p, 0.8, "Z-SIECI-IST", color=BRANZE_COL("woda"))
        elif kind == "spot_ist":
            sh.line((x + 2, y), (x + 3.6, y), "Z-RZEDNE", pen=0.18, color="#6b4423")
            sh.line((x + 2.8, y - 0.8), (x + 2.8, y + 0.8), "Z-RZEDNE", pen=0.18, color="#6b4423")
            sh.text((x + 4.2, y + 0.3), "101,25", 1.8, 0, "left", "baseline", "Z-RZEDNE", style="italic",
                    color="#6b4423")
        elif kind == "spot_proj":
            sh.dot((x + 2.8, y), 0.9, "Z-RZEDNE-PROJ")
            sh.text((x + 4.4, y + 0.3), "101,35", 1.8, 0, "left", "baseline", "Z-RZEDNE-PROJ")
            sh.rect(x + 3.9, y - 0.4, x + 4.4 + T.width("101,35", 1.8) + 0.5, y + 2.4, "Z-RZEDNE-PROJ", pen=0.18)
        elif kind in ("spadek", "splyw"):
            slope(sh, (x + 1, y - 0.6), (x + 15, y - 0.6), text="2,0%" if kind == "spadek" else "i", h=1.8,
                  layer="Z-ODWODNIENIE")
        elif kind == "zero":
            sh.text((x + 8, y + 0.2), "±0,00=101,65", 1.8, 0, "center", "baseline", "R-LEGENDA")
        elif kind == "wymiar":
            dim_pts(sh, (x + 1, y - 1.2), (x + 15, y - 1.2), h=1.8, label="4,30", layer="R-LEGENDA")
        elif kind == "tyczenie":
            tyczenie_mark(sh, p, "T1")
        elif kind == "kolizja":
            sh.circle(p, 2.0, "Z-KOLIZJE", pen=0.5)
            sh.text(p, "K1", 1.8, 0, "center", "middle", "Z-KOLIZJE", style="bold")
        elif kind == "skrzyzowanie":
            sh.line((x + 2, y), (x + 14, y), "Z-SIECI-PROJ", pen=0.5, color="#0050c8")
            sh.line((p[0], y - 2), (p[0], y + 2), "Z-SIECI-PROJ", pen=0.7, color="#d00000")
            sh.circle(p, 1.0, "Z-KOLIZJE", pen=0.25)
        elif kind == "mapa_ramka":
            sh.rect(x + 1, y - 1.8, x + 15, y + 1.8, "Z-MAPA-RAMKA", pen=0.5)
    return f


def tyczenie_mark(c, p, label=None, layer="Z-TYCZENIE"):
    """Punkt tyczenia: kółko Ø2 mm z krzyżem (współrzędne w wykazie)."""
    k = c.k
    P = np.asarray(p, float)
    c.circle(P, 1.0 * k, layer, pen=0.25)
    c.line(P + [-1.6 * k, 0], P + [1.6 * k, 0], layer, pen=0.18)
    c.line(P + [0, -1.6 * k], P + [0, 1.6 * k], layer, pen=0.18)
    if label and c.k == 1.0:
        c.text(P + [2.2, 0.4], label, 1.8, 0, "left", "baseline", layer)
