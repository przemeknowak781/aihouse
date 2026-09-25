"""Symbole zagospodarowania terenu (PN-B-01027:2002 — wg R4 sekcja M, PN-EN ISO 11091).

Grubości linii PN-B-01027 podawane są jawnie w mm (niezależnie od grupy linii rzutni): obrys budynku 1,4;
linie rozgraniczające, kanalizacja, gaz, kabel e 0,7; wodociąg, jezdnie, warstwice projektowane 0,5; granica działki,
ogrodzenie, linie zabudowy, zieleń 0,35; opisy 0,25; wymiary i warstwice istniejące 0,18.
Wymiary rzeczywiste w metrach modelu (korona drzewa, studzienka), symbole umowne w mm papieru.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from . import fmt, text as T
from .dims import arrowhead
from .geom import (Xf, arr, circle_pts, dir_deg, lines_of, perp, polygons_of, readable_angle, rect_c, rect_pts,
                   to_polygon, unit)

__all__ = [
    "tree", "shrub", "hedge", "lawn", "paving", "pole", "hydrant", "manhole", "cable_box", "utility_box",
    "plot_boundary", "building_line", "boundary_line", "fence", "utility_line", "retaining_wall", "building_label",
    "site_entrance", "contours", "spot_height", "gate", "UTILITY",
]


def _along(ls: LineString, step: float, offset: float = 0.0):
    """Punkty i kierunki co ``step`` wzdłuż łamanej (s, punkt, wektor jednostkowy)."""
    L = ls.length
    out = []
    s = offset if offset > 0 else step / 2.0
    while s < L:
        p = np.asarray(ls.interpolate(s).coords)[0]
        q = np.asarray(ls.interpolate(min(L, s + L * 1e-4 + 1e-9)).coords)[0]
        p0 = np.asarray(ls.interpolate(max(0.0, s - L * 1e-4 - 1e-9)).coords)[0]
        out.append((s, p, unit(q - p0)))
        s += step
    return out


def _label_along(c, ls, text, every_mm, layer, h=2.0):
    k = c.k
    for s, p, d in _along(ls, every_mm * k, every_mm * k * 0.5):
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        c.text(p, text, h, ang, "center", "middle", layer, mask=0.4)


# ================================================================================================ zieleń
def tree(c, pos, crown_d: float = 5.0, existing: bool = True, remove: bool = False, conifer: bool = False,
         transplant: bool = False, layer: str = "Z-ZIELEN", label: str | None = None):
    """Drzewo (PN-B-01027 poz. 7.1–7.5, R4-M13): liściaste projektowane — okrąg korony 0,35 + krzyżyk pnia 0,25;
    istniejące — okrąg 0,35 + kropka pnia ≥ 1 mm; iglaste — okrąg z krótkimi kreskami promieniowymi;
    do przesadzenia — okrąg kreskowy + nr; do usunięcia — skreślenie „X” 0,5."""
    k = c.k
    P = np.asarray(pos, float)
    R = crown_d / 2
    with c.on(layer):
        c.circle(P, R, pen=0.35, lt="KRESKOWA" if transplant else None)
        if conifer:
            for i in range(16):
                a = 2 * math.pi * i / 16
                v = np.array([math.cos(a), math.sin(a)])
                c.line(P + v * R, P + v * (R - max(1.0 * k, 0.12 * R)), pen=0.25)
        if existing:
            c.dot(P, 1.0, layer)
        else:
            s = max(0.8 * k, 0.1 * R)
            c.line(P + [-s, 0], P + [s, 0], pen=0.25)
            c.line(P + [0, -s], P + [0, s], pen=0.25)
        if remove:
            a = R * 0.72
            c.line(P + [-a, -a], P + [a, a], pen=0.5)
            c.line(P + [-a, a], P + [a, -a], pen=0.5)
        if label:
            c.text(P + np.array([R * 0.75, -R * 0.75]), label, 2.0, 0.0, "left", "top")


def shrub(c, pos, d: float = 1.2, layer: str = "Z-ZIELEN"):
    """Krzew (okrąg falisty)."""
    P = np.asarray(pos, float)
    n = 7
    t = np.linspace(0, 2 * math.pi, n * 12, endpoint=False)
    rr = d / 2 * (1 - 0.22 * np.abs(np.sin(n * t / 2)))
    c.polygon(np.column_stack([P[0] + rr * np.cos(t), P[1] + rr * np.sin(t)]), layer, pen=0.25)


def hedge(c, pts, width: float = 0.8, conifer: bool = False, existing: bool = False, layer: str = "Z-ZIELEN"):
    """Żywopłot (PN-B-01027 poz. 7.6–7.7): projektowany liściasty — linia falista, iglasty — zygzak, 0,35;
    istniejący 0,25. ``width`` — szerokość pasa [m]."""
    k = c.k
    ls = LineString(arr(pts))
    L = ls.length
    step = max(1.6 * k, width * 0.6)
    pen = 0.25 if existing else 0.35
    n = max(2, int(L / step) * 2)
    pts_out = []
    for i in range(n + 1):
        s = L * i / n
        p = np.asarray(ls.interpolate(s).coords)[0]
        q = np.asarray(ls.interpolate(min(L, s + L * 1e-3)).coords)[0]
        p0 = np.asarray(ls.interpolate(max(0.0, s - L * 1e-3)).coords)[0]
        nrm = perp(unit(q - p0))
        amp = width / 2 * (1 if i % 2 else -1)
        pts_out.append(p + nrm * amp)
    P = np.array(pts_out)
    c.polyline(P if conifer else _smooth(P), layer, pen=pen)   # iglasty — zygzak, liściasty — fala


def _smooth(P, n=8):
    """Łamana wygładzona łukami (Chaikin ×2)."""
    Q = np.asarray(P, float)
    for _ in range(3):
        R = [Q[0]]
        for a, b in zip(Q[:-1], Q[1:]):
            R.append(0.75 * a + 0.25 * b)
            R.append(0.25 * a + 0.75 * b)
        R.append(Q[-1])
        Q = np.array(R)
    return Q


def lawn(c, poly, density_per_cm2: float = 3.0, layer: str = "Z-ZIELEN", seed=None, outline: bool = False):
    """Trawnik projektowany — kropki (PN-B-01027 poz. 7.8); gęstość na cm² papieru."""
    from .hatch import _dots, _rng
    g = to_polygon(poly)
    for pg in polygons_of(g):
        _dots(c, pg, density_per_cm2 / 100.0, _rng(pg, seed), layer, 0.12, pen=0.25)
        if outline:
            c.geom(pg, layer, pen=0.25, lt="KRESKOWA")


def paving(c, poly, kind: str = "drobne", layer: str = "Z-UTWARDZENIA", angle: float = 0.0, outline: bool = True,
           band_mm: float | None = 6.0):
    """Nawierzchnia (PN-B-01027 poz. 7.10–7.11): 'drobne' (kostka) — linie 0,18 co 2 mm, nie na całej powierzchni
    (pas ``band_mm`` przy krawędziach); 'duze' (płyty) — kwadraty 0,18 o boku 4 mm; 'zwir' — kropki;
    'asfalt' — tło szare; 'deska' — linie równoległe (taras)."""
    from .hatch import _dots, _parallel, _rng
    k = c.k
    g = to_polygon(poly)
    for pg in polygons_of(g):
        target = pg
        if band_mm and kind in ("drobne", "kostka"):
            inner = pg.buffer(-band_mm * k)
            if not inner.is_empty:
                target = pg.difference(inner)
        if kind in ("drobne", "kostka"):
            for ln in _parallel(target, angle + 90.0, 2.0 * k):
                c.polyline(ln, layer, pen=0.18)
        elif kind in ("duze", "plyty"):
            for a in (angle, angle + 90.0):
                for ln in _parallel(pg, a, 4.0 * k):
                    c.polyline(ln, layer, pen=0.18)
        elif kind == "deska":
            for ln in _parallel(pg, angle, 1.0 * k):
                c.polyline(ln, layer, pen=0.18)
        elif kind == "zwir":
            _dots(c, pg, 0.4, _rng(pg), layer, 0.12)
        elif kind == "asfalt":
            c.fill(pg, layer, "#d8d8d8")
        if outline:
            c.geom(pg, layer, pen=0.35)


def retaining_wall(c, pts, side: float = 1.0, layer: str = "Z-OGRODZENIE"):
    """Ściana oporowa (PN-B-01027 poz. 7): linia 0,7 z kreskami od strony skarpy (``side`` = +1 lewa strona)."""
    k = c.k
    ls = LineString(arr(pts))
    c.polyline(arr(pts), layer, pen=0.7)
    for s, p, d in _along(ls, 2.0 * k):
        c.line(p, p + perp(d) * side * 1.0 * k, layer, pen=0.25)


# ================================================================================================ uzbrojenie i obiekty
def pole(c, pos, kind: str = "en", s_mm: float = 2.0, layer: str = "Z-UZBROJENIE"):
    """Słup: 'en' — elektroenergetyczny / oświetleniowy (punkt zaczerniony Ø2 mm, PN-B-01027 poz. 6),
    'osw' — punkt świetlny (kółko Ø5 mm z zaczernionym słupem), 'tel' — telekomunikacyjny (okrąg pusty)."""
    k = c.k
    with c.on(layer):
        if kind == "osw":
            c.circle(pos, 2.5 * k, pen=0.25)
            c.dot(pos, 2.0, layer)
        elif kind == "tel":
            c.circle(pos, s_mm * k / 2, pen=0.25)
        else:
            c.dot(pos, s_mm, layer)


def hydrant(c, pos, s_mm: float = 3.0, underground: bool = False, layer: str = "Z-UZBROJENIE"):
    """Hydrant (okrąg + opis „HP” — hydrant podziemny wg PN-B-01027; nadziemny „H”)."""
    k = c.k
    R = s_mm * k / 2
    with c.on(layer):
        c.circle(pos, R, pen=0.35)
        c.dot(pos, 0.8, layer)
        c.text(np.asarray(pos) + np.array([R + 0.8 * k, 0.0]), "HP" if underground else "H", 2.0, 0.0, "left",
               "middle")


def manhole(c, pos, d: float = 1.0, label: str | None = "Sk", layer: str = "Z-UZBROJENIE", h: float = 2.0):
    """Studzienka (okrąg o średnicy rzeczywistej, min. 2 mm na papierze) z oznaczeniem."""
    R = max(d / 2, 1.0 * c.k)
    with c.on(layer):
        c.circle(pos, R, pen=0.35)
        c.dot(pos, 0.5, layer)
        if label:
            c.text(np.asarray(pos) + np.array([R + 0.8 * c.k, 0.0]), label, h, 0.0, "left", "middle")


def cable_box(c, pos, rot: float = 0.0, w: float = 0.9, d: float = 0.35, label: str = "ZK",
              layer: str = "Z-UZBROJENIE"):
    """Złącze kablowe / kablowo-pomiarowe (prostokąt z przekątną i opisem) — wymiary rzeczywiste."""
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        q = xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2))
        c.polygon(q, pen=0.5)
        c.line(q[0], q[2], pen=0.25)
        c.text(xf.pt(0, d / 2 + 0.8 * c.k), label, 2.5, 0.0, "center", "bottom", style="bold")


def utility_box(c, pos, rot: float = 0.0, w: float = 0.6, d: float = 0.3, label: str = "SW",
                layer: str = "Z-UZBROJENIE"):
    """Skrzynka / studzienka wodomierzowa „SW”, skrzynka gazowa „SG” — prostokąt z opisem."""
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2)), pen=0.35)
        c.text(xf.pt(0, d / 2 + 0.8 * c.k), label, 2.5, 0.0, "center", "bottom")


# ================================================================================================ granice i linie
def plot_boundary(c, pts, closed: bool = True, corner_labels=None, point_labels=None, coords: bool = False,
                  layer: str = "Z-GRANICE", h: float = 2.5, label_offset_mm: float = 4.5):
    """Granica działki budowlanej (PN-B-01027 poz. 2.7): linia ciągła 0,35 z punktami Ø1,0 mm; narożniki opisane
    kółkiem z literą (A, B, C…); ``coords=True`` — obok współrzędne „x …, y …” (najpierw x, potem y).
    ``point_labels`` (numery punktów granicznych z mapy) — opis bez kółka."""
    k = c.k
    P = arr(pts)
    labels = corner_labels
    with c.on(layer):
        c.polyline(P, closed=closed, pen=0.35)
        ctr = P.mean(axis=0)
        for i, p in enumerate(P):
            c.dot(p, 1.0, layer)
            v = unit(p - ctr)
            if labels is not None and i < len(labels) and labels[i]:
                q = p + v * label_offset_mm * k
                c.fill(circle_pts(q, 2.2 * k, 24), layer, "#ffffff", z=26.2)
                c.circle(q, 2.2 * k, pen=0.25, z=26.3)
                c.text(q, str(labels[i]), h, 0.0, "center", "middle")
                if coords:
                    c.text(q + np.array([3.0 * k, -1.0 * k]),
                           f"x {fmt.num(p[1], 2)}, y {fmt.num(p[0], 2)}", 1.8, 0.0, "left", "top")
            elif point_labels is not None and i < len(point_labels):
                c.text(p + v * 2.2 * k, str(point_labels[i]), 1.8, 0.0, "center", "middle")


def boundary_line(c, pts, label: str | None = None, layer: str = "Z-GRANICE"):
    """Linia rozgraniczająca tereny o różnym przeznaczeniu (PN-B-01027 poz. 2.5): linia ciągła 0,7."""
    c.polyline(arr(pts), layer, pen=0.7)
    if label:
        _label_along(c, LineString(arr(pts)), label, 80.0, layer)


def building_line(c, p1, p2, kind: str = "nieprzekraczalna", side: float = 1.0, layer: str = "Z-LINIE-ZABUDOWY",
                  label: str | None = None, h: float = 2.0):
    """Linia zabudowy (PN-B-01027 poz. 2.1–2.2): linia ciągła 0,35 z trójkątami równobocznymi o boku 2 mm
    w rytmie 12·2·12 mm po stronie terenu zabudowy (``side`` +1 = lewa strona p1→p2); obowiązująca — trójkąty
    zaczernione, nieprzekraczalna — niezaczernione."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d) * side
    ls = LineString([A, B])
    with c.on(layer):
        c.line(A, B, pen=0.35)
        a = 2.0 * k
        hgt = a * math.sqrt(3) / 2
        for s, p, dd in _along(ls, 14.0 * k, 7.0 * k):
            tri = [p - d * a / 2, p + d * a / 2, p + n * hgt]
            if kind == "obowiazujaca" or kind == "obowiązująca":
                c.fill(tri, layer, None or "#000000")
            c.polygon(tri, pen=0.25)
        if label:   # opis po stronie przeciwnej do trójkątów
            ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
            up = perp(dir_deg(ang))
            M = A + (B - A) * 0.5
            pos = M + up * 1.0 * k if (up @ n) < 0 else M - up * (1.0 * k + h * k)
            c.text(pos, label, h, ang, "center", "baseline")


def fence(c, pts, layer: str = "Z-OGRODZENIE"):
    """Ogrodzenie projektowane (PN-B-01027 poz. 2.8): linia ciągła 0,35 z kreskami poprzecznymi."""
    k = c.k
    ls = LineString(arr(pts))
    c.polyline(arr(pts), layer, pen=0.35)
    for s, p, d in _along(ls, 6.0 * k):
        nn = perp(d) * 0.9 * k
        c.line(p - nn, p + nn, layer, pen=0.35)


UTILITY = {
    # rodzaj: (grubość [mm], rodzaj linii, znacznik, opis, kolor wydruku w trybie 'branze')
    "woda": (0.5, None, "chevron", "w", "#0050c8"),
    "kan_sanit": (0.7, None, "tri_fill", "Ks", "#7a4500"),
    "kan_deszcz": (0.7, None, "tri_open", "Kd", "#00808a"),
    "gaz": (0.7, "PUNKTOWA_KROTKA", None, "g", "#b0a000"),
    "energ": (0.7, "KABEL_E", None, "e", "#c00000"),
    "tele": (0.5, "WIELOPUNKTOWA", None, "t", "#6a00a0"),
    "cieplo": (0.5, None, "double", "c", "#d06000"),
}


def utility_line(c, pts, kind: str = "woda", label: str | None = None, existing: bool = False,
                 layer: str = "Z-UZBROJENIE", every_mm: float = 25.0, connection_end: bool = False):
    """Sieć/przyłącze na PZT (PN-B-01027 poz. 6, R4-M12): wodociąg 0,5 z otwartymi „<” (kierunek przepływu
    p1→p2), kanalizacja sanitarna 0,7 z trójkątem zaczernionym 3 mm „Ks”, deszczowa 0,7 z trójkątem pustym „Kd”,
    gaz punktowa 0,7 „g”, kabel energetyczny kreskowa 0,7 „e”, telekomunikacja wielopunktowa 0,5 „t”,
    ciepłownicza — dwie linie 0,5 w odstępie 2 mm „c”. ``connection_end`` — „×” w miejscu włączenia do sieci."""
    k = c.k
    w, lt, marker, code, rgb = UTILITY[kind]
    P = arr(pts)
    ls = LineString(P)
    color = "#606060" if existing else None
    with c.on(layer):
        if marker == "double":
            for off in (-1.0, 1.0):
                c.polyline(np.asarray(ls.offset_curve(off * k).coords), pen=w, color=color)
        else:
            c.polyline(P, pen=w, lt=lt, color=color)
        for s, p, d in _along(ls, every_mm * k, every_mm * k * 0.25):
            nn = perp(d)
            if marker == "chevron":
                a = 1.2 * k
                c.polyline([p + d * a + nn * a, p, p + d * a - nn * a], pen=0.35, color=color)
            elif marker in ("tri_fill", "tri_open"):
                a = 3.0 * k
                tri = [p + d * a * 0.87, p + nn * a / 2, p - nn * a / 2]
                if marker == "tri_fill":
                    c.fill(tri, layer, "#000000")
                c.polygon(tri, pen=0.25, color=color)
        txt = label if label is not None else code
        if txt:
            _label_along(c, ls, txt, every_mm, layer)
        if connection_end:
            q = P[-1]
            a = 1.5 * k
            c.line(q + [-a, -a], q + [a, a], pen=0.5)
            c.line(q + [-a, a], q + [a, -a], pen=0.5)


def building_label(c, pos, zero_abs: float, storeys_roman: str = "III", nr: str | None = None, h: float = 2.5,
                   layer: str = "Z-OPISY"):
    """Opis budynku na PZT (PN-B-01027 poz. 1.8): „±0,00=101,65” (2 miejsca), liczba kondygnacji nadziemnych cyfrą
    rzymską w kółku, opcjonalnie nr porządkowy."""
    k = c.k
    P = np.asarray(pos, float)
    txt = f"{fmt.PLUSMINUS}0,00={fmt.num(zero_abs, fmt.LEVEL_DECIMALS_PZT)}"
    with c.on(layer):
        c.text(P, txt, h, 0.0, "center", "baseline", mask=0.5)
        r = max(T.width(storeys_roman, h) / 2 + 1.0, 2.6) * k
        C = P + np.array([0.0, -r - 1.6 * k])
        c.fill(circle_pts(C, r, 32), layer, "#ffffff", z=26.2)
        c.circle(C, r, pen=0.25, z=26.3)
        c.text(C, storeys_roman, h, 0.0, "center", "middle")
        if nr:
            c.text(P + np.array([0.0, h * k * 1.6]), nr, h, 0.0, "center", "baseline")


def site_entrance(c, pos, direction: float, layer: str = "Z-ZABUDOWA"):
    """Wejście główne na PZT (PN-B-01027 poz. 1.7): trójkąt równoboczny zaczerniony o boku 4 mm."""
    k = c.k
    d = dir_deg(direction)
    n = perp(d)
    a = 4.0 * k
    P = np.asarray(pos, float)
    tri = [P, P - d * a * 0.866 + n * a / 2, P - d * a * 0.866 - n * a / 2]
    c.fill(tri, layer, "#000000")
    c.polygon(tri, layer, pen=0.25)


def contours(c, lines, step_label: float = 0.5, layer: str = "Z-WARSTWICE", h: float = 1.8,
             nd: int | None = None, label_every: float = 60.0, projected: bool = False):
    """Warstwice (PN-B-01027 poz. 5.2): istniejące — ciągła 0,18, projektowane — ciągła 0,5; lines = [(punkty, H)].
    Opis wartości (co ``step_label``) wzdłuż warstwicy z maską."""
    k = c.k
    nd = fmt.LEVEL_DECIMALS_PZT if nd is None else nd
    pen = 0.5 if projected else 0.18
    for pts, H in lines:
        P = arr(pts)
        c.polyline(P, layer, pen=pen)
        major = abs((H / step_label) - round(H / step_label)) < 1e-6
        if major:
            ls = LineString(P)
            L = ls.length
            n = max(1, int(L / (label_every * k)))
            for i in range(n):
                s = (i + 0.5) * L / n
                q = np.asarray(ls.interpolate(s).coords)[0]
                q2 = np.asarray(ls.interpolate(min(L, s + 0.5 * k)).coords)[0]
                q1 = np.asarray(ls.interpolate(max(0, s - 0.5 * k)).coords)[0]
                dd = unit(q2 - q1)
                ang = readable_angle(math.degrees(math.atan2(dd[1], dd[0])))
                c.text(q, fmt.num(H, nd), h, ang, "center", "middle", layer, mask=0.4)


def spot_height(c, pos, H: float, existing: bool = True, nd: int | None = None, layer: str = "Z-WARSTWICE",
                h: float = 2.5):
    """Punkt wysokościowy (m n.p.m., 2 miejsca): istniejący — krzyżyk + wartość kursywą; projektowany — kropka +
    wartość w ramce."""
    k = c.k
    nd = fmt.LEVEL_DECIMALS_PZT if nd is None else nd
    P = np.asarray(pos, float)
    s = 0.8 * k
    lab = fmt.num(H, nd)
    with c.on(layer):
        if existing:
            c.line(P + [-s, 0], P + [s, 0], pen=0.18)
            c.line(P + [0, -s], P + [0, s], pen=0.18)
            c.text(P + np.array([1.2 * k, 0.6 * k]), lab, h, 0.0, "left", "baseline", style="italic")
        else:
            c.dot(P, 0.8, layer)
            w = T.width(lab, h) * k
            x0 = P[0] + 1.2 * k
            c.rect(x0 - 0.5 * k, P[1] + 0.2 * k, x0 + w + 0.5 * k, P[1] + h * k + 1.1 * k, pen=0.25)
            c.text((x0, P[1] + 0.65 * k), lab, h, 0.0, "left", "baseline")


def gate(c, p1, p2, kind: str = "przesuwna", layer: str = "Z-OGRODZENIE"):
    """Brama/furtka w ogrodzeniu (PN-B-01027 poz. 2.9): przesuwna — skrzydło z kierunkiem przesuwu; furtka —
    skrzydło z łukiem (0,35)."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d)
    W = float(np.hypot(*(B - A)))
    with c.on(layer):
        if kind == "przesuwna":
            c.line(A + n * 0.8 * k, B + n * 0.8 * k, pen=0.35)
            a0, a1 = A + d * W * 0.7 + n * 2.6 * k, A + d * W * 0.2 + n * 2.6 * k
            c.line(a0, a1, pen=0.25)
            arrowhead(c, a1, a1 - a0, 2.0, 12, True, layer, pen=0.25)
        else:
            tip = A + n * W
            c.line(A, tip, pen=0.35)
            a0 = math.degrees(math.atan2(d[1], d[0]))
            c.arc(A, W, a0, a0 + 90, pen=0.18)
