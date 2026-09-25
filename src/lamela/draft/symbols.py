"""Symbole rysunkowe: adnotacje i architektura (PN-B-01025:2004, PN-EN ISO 4157, PN-EN ISO 128).

Konwencje:
* ``pos`` — punkt wstawienia w jednostkach płótna (w rzutni: metry modelu),
* ``rot`` — kąt obrotu [°] CCW; dla wyposażenia przyściennego lokalna oś +y wskazuje "w głąb pomieszczenia"
  (od ściany), punkt wstawienia leży na licu ściany w osi elementu,
* elementy rzeczywiste (meble, wyposażenie sanitarne, stolarka) — wymiary w metrach modelu,
* symbole umowne (strzałka północy, kółka osi, symbole elektryczne…) — wymiary w mm papieru (``*_mm``).

Symbole instalacyjne: ``symbols_inst`` (PN-EN 60617, instalacje sanitarne), zagospodarowania terenu:
``symbols_site`` — wszystkie są re-eksportowane z tego modułu.
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Polygon

from . import fmt, text as T
from .dims import arrowhead, dim_runs
from .geom import Xf, arc_pts, arr, circle_pts, dir_deg, perp, readable_angle, rect_c, rect_pts, rot, unit


# ================================================================================================ narzędzia
def X(pos, rot_deg=0.0, scale=1.0, mirror=False) -> Xf:
    return Xf.make(np.asarray(pos, float), rot_deg, scale, mirror)


def rrect(x0, y0, x1, y1, r, n=6):
    """Prostokąt z zaokrąglonymi narożnikami (punkty)."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        t = np.radians(np.linspace(a0, a0 + 90, n))
        pts.extend(np.column_stack([cx + r * np.cos(t), cy + r * np.sin(t)]).tolist())
    return np.array(pts)


def ellipse_pts(cx, cy, a, b, n=48, a0=0.0, a1=360.0):
    t = np.radians(np.linspace(a0, a1, n, endpoint=(a1 - a0) < 360))
    return np.column_stack([cx + a * np.cos(t), cy + b * np.sin(t)])


def tag(c, pos, text: str, shape: str = "circle", r_mm: float = 3.2, h: float = 2.5, layer: str = "A-OPISY",
        pen="cienka", mask: bool = True, style: str = "normal"):
    """Symbol w obwódce (oznaczenie stolarki, detalu, pozycji): circle | ellipse | hex | rect | diamond."""
    k = c.k
    P = np.asarray(pos, float)
    w = T.width(text, h, style) * k
    r = max(r_mm * k, w / 2 + 1.0 * k)
    with c.on(layer):
        if shape == "circle":
            pts = circle_pts(P, r, 48)
        elif shape == "ellipse":
            a = max(r_mm * k, w / 2 + 1.6 * k)
            pts = ellipse_pts(P[0], P[1], a, r_mm * k * 0.75, 48)
        elif shape == "hex":
            a = max(r_mm * k * 0.9, w / 2 + 1.8 * k)
            hh = r_mm * k * 0.75
            pts = np.array([[-a, 0], [-a + hh * 0.6, hh], [a - hh * 0.6, hh], [a, 0], [a - hh * 0.6, -hh],
                            [-a + hh * 0.6, -hh]]) + P
        elif shape == "rect":
            a = max(r_mm * k, w / 2 + 1.2 * k)
            pts = rect_c(P[0], P[1], 2 * a, 2 * r_mm * k * 0.72)
        elif shape == "diamond":
            pts = np.array([[-r * 1.2, 0], [0, r], [r * 1.2, 0], [0, -r]]) + P
        else:
            raise ValueError(shape)
        if mask:
            c.fill(pts, layer, "#ffffff", z=26.5)
        c.polygon(pts, pen=pen, z=26.6)
        c.text(P, text, h, 0.0, "center", "middle", style=style, z=26.7)


# ================================================================================================ północ, osie, przekroje
def north_arrow(c, pos, size_mm: float = 16.0, north_deg: float = 0.0, layer: str = "A-SYMBOLE", h: float = 5.0,
                style: str = "pn"):
    """Strzałka północy (PN-B-01025). ``north_deg`` — kierunek północy na rysunku, CCW od osi +y arkusza
    (0 = w górę). Dla układu budynku z ``azymut_osi_y`` = α (azymut osi +y, zgodnie z ruchem wskazówek
    zegara od N) przyjmij ``north_deg = α``."""
    k = c.k
    R = size_mm * k / 2
    xf = X(pos, north_deg)
    with c.on(layer):
        c.circle(pos, R, pen="cienka")
        tip = xf.pt(0, R * 1.15)
        tail = xf.pt(0, -R * 0.95)
        l = xf.pt(-R * 0.32, -R * 0.55)
        r = xf.pt(R * 0.32, -R * 0.55)
        c.fill([tip, xf.pt(0, -R * 0.35), l], layer, "#000000")
        c.polygon([tip, r, xf.pt(0, -R * 0.35), l], pen="srednia")
        c.line(xf.pt(0, -R * 0.35), tail, pen="cienka")
        c.text(xf.pt(0, R * 1.15 + 1.2 * k), "N", h, north_deg, "center", "bottom", style="bold")


def axis_line(c, p1, p2, label: str, bubbles: str = "both", r_mm: float = 5.0, h: float = 3.5,
              layer: str = "A-OSIE", gap_mm: float = 0.0):
    """Oś konstrukcyjna: linia punktowa cienka p1–p2, kółka z oznaczeniem na końcach (PN-B-01025)."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    R = r_mm * k
    L = float(np.hypot(*(B - A)))
    # dopasowanie wzoru tak, by linia zaczynała i kończyła się kreską
    from .styles import LINETYPES
    lt = LINETYPES["PUNKTOWA"]
    per = lt.period * k
    dash = lt.pattern[0] * k
    n = max(1, round((L - dash) / per))
    lts = (L / (n * per + dash)) if L > dash else 1.0
    c.line(A, B, layer, lt="PUNKTOWA", lt_scale=lts)
    ends = []
    if bubbles in ("both", "start"):
        ends.append((A, -d))
    if bubbles in ("both", "end"):
        ends.append((B, d))
    for P, dd in ends:
        C = P + dd * (R + gap_mm * k)
        c.fill(circle_pts(C, R, 48), layer, "#ffffff", z=12.5)
        c.circle(C, R, layer, pen="cienka", lt="CIAGLA", z=12.6)
        c.text(C, label, h, 0.0, "center", "middle", layer, z=12.7)


def axes_grid(c, xs: dict, ys: dict, bbox, ext_mm: float = 14.0, r_mm: float = 5.0, h: float = 3.5,
              layer: str = "A-OSIE", sides: str = "all"):
    """Siatka osi: xs = {nazwa: x} (osie pionowe), ys = {nazwa: y} (osie poziome); bbox = zasięg obiektu
    (x0, y0, x1, y1) — linie wychodzą ``ext_mm`` poza obiekt. sides: 'all' | 'bl' (kółka tylko dół/lewo)."""
    k = c.k
    x0, y0, x1, y1 = bbox
    e = ext_mm * k
    for name, x in xs.items():
        axis_line(c, (x, y0 - e), (x, y1 + e), name, "both" if sides == "all" else "start", r_mm, h, layer)
    for name, y in ys.items():
        axis_line(c, (x0 - e, y), (x1 + e, y), name, "both" if sides == "all" else "start", r_mm, h, layer)


def section_mark(c, p1, p2, label: str = "A", look: float = 1.0, h: float = 5.0, end_mm: float = 10.0,
                 arrow_mm: float = 6.0, full: bool = True, layer: str = "A-PRZEKROJE", label2: str | None = None):
    """Oznaczenie przekroju na rzucie (PN-B-01025 3.3, ISO 128-2 04.1/04.2): cienka linia punktowa na całej
    długości, gruba linia punktowa na końcach (``end_mm`` = 10 mm, R4 pkt 3.7), strzałki kierunku patrzenia
    linią grubą i wielkie litery 5 mm (≈1,41 × pismo 3,5 mm).

    look = +1: patrzymy w lewo od kierunku p1→p2; −1: w prawo."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d) * look
    with c.on(layer):
        if full:
            c.line(A, B, pen="cienka", lt="PUNKTOWA")
        c.line(A, A + d * end_mm * k, pen="gruba", lt="PUNKTOWA_KROTKA", lt_scale=0.6)
        c.line(B, B - d * end_mm * k, pen="gruba", lt="PUNKTOWA_KROTKA", lt_scale=0.6)
        for P in (A, B):
            c.line(P, P + n * (arrow_mm - 2.5) * k, pen="gruba", lt="CIAGLA")
            arrowhead(c, P + n * arrow_mm * k, n, 2.8, 12, True, layer, pen="srednia")
            lp = P + n * arrow_mm * 0.55 * k + (d if P is B else -d) * (T.width(label, h, "bold") / 2 + 2.0) * k
            c.text(lp, label if P is A or label2 is None else label2, h, 0.0, "center", "middle", style="bold")


def detail_callout(c, center, r_mm: float, label: str, leader_to=None, h: float = 5.0, layer: str = "A-OPISY"):
    """Odnośnik szczegółu (PN-B-01025): okrąg obejmujący fragment + linia wskazująca + litera nad linią."""
    k = c.k
    C = np.asarray(center, float)
    R = r_mm * k
    with c.on(layer):
        c.circle(C, R, pen="cienka")
        if leader_to is None:
            leader_to = C + np.array([R * 1.3, -R * 1.3])
        E = np.asarray(leader_to, float)
        d = unit(E - C)
        c.line(C + d * R, E)
        w = T.width(label, h, "bold") * k
        c.line(E, E + np.array([w + 2 * k, 0]))
        c.text(E + np.array([1.0 * k, 0.8 * k]), label, h, 0.0, "left", "baseline", style="bold")


def room_tag(c, pos, number: str, name: str | None, area_m2: float | None = None, floor: str | None = None,
             level_z: float | None = None, h: float = 2.5, layer: str = "A-POMIESZCZENIA", mask: bool = True,
             upper: bool = False, h_num: float = 3.5):
    """Oznaczenie pomieszczenia (PN-EN ISO 4157-2 4.3, PN-B-01025 3.4): numer i nazwa PODKREŚLONE, powierzchnia
    [m², 2 miejsca po przecinku], opcjonalnie posadzka i rzędna posadzki (w ramce). ``name=None`` — tylko numer
    (małe pomieszczenia, nazwa w tabeli)."""
    k = c.k
    P = np.asarray(pos, float)
    items = [("num", number, h_num, "bold", True)]
    if name:
        items.append(("name", name.upper() if upper else name, h, "normal", True))
    if area_m2 is not None:
        items.append(("area", fmt.area(area_m2), h, "normal", False))
    if floor:
        items.append(("floor", floor, 1.8, "italic", False))
    if level_z is not None:
        items.append(("level", fmt.level(level_z), 1.8, "normal", False))
    gap = 1.0
    tot = sum(hh * (1 + gap) for _t, _s, hh, _st, _u in items) - items[-1][2] * gap
    y = P[1] + tot / 2 * k
    with c.on(layer):
        for t, s_, hh, st, underline in items:
            y -= hh * k
            w = T.width(s_, hh, st) * k
            pad = 0.6 * k
            if mask:
                c.fill(rect_pts(P[0] - w / 2 - pad, y - pad * 1.5, P[0] + w / 2 + pad, y + hh * k + pad), layer,
                       "#ffffff", z=26.0)
            if underline:
                c.line((P[0] - w / 2, y - 0.7 * k), (P[0] + w / 2, y - 0.7 * k), pen="cienka")
            if t == "level":
                c.polygon(rect_pts(P[0] - w / 2 - pad, y - pad, P[0] + w / 2 + pad, y + hh * k + pad), pen="cienka")
            c.text((P[0], y), s_, hh, 0.0, "center", "baseline", style=st)
            y -= hh * gap * k


def layer_callout(c, p_start, p_end, texts: list[str], side: str = "right", h: float = 2.2, row_mm: float = 4.6,
                  marks=None, layer: str = "A-OPISY", numbered: bool = False, width_mm: float | None = None,
                  title: str | None = None):
    """Opis warstw — odnośnik elementu wielowarstwowego („drabinka”, PN-B-01025).

    Linia wskazująca od ``p_start`` (w najdalszej warstwie) do ``p_end`` (poza elementem), w punktach ``marks``
    (przecięcia z warstwami) kropki; od ``p_end`` pionowy „grzbiet” z półkami — kolejne opisy od góry (dla warstw
    poziomych: od warstwy najwyższej). Zwraca prostokąt opisu."""
    k = c.k
    A, B = np.asarray(p_start, float), np.asarray(p_end, float)
    sg = 1.0 if side == "right" else -1.0
    items = [(f"{i + 1}. " if numbered else "") + t for i, t in enumerate(texts)]
    wmax = max(T.width(s, h) for s in items) * k
    W = width_mm * k if width_mm else wmax + 2.0 * k
    n = len(items)
    R = row_mm * k
    with c.on(layer):
        c.line(A, B)
        c.dot(A, 0.8, layer)
        for m in (marks or []):
            c.dot(m, 0.6, layer)
        top = B + np.array([0.0, R * n])
        c.line(B, top)
        for i, s in enumerate(items):
            y = top[1] - i * R
            c.line((B[0], y), (B[0] + sg * W, y))
            c.text((B[0] + sg * 0.8 * k, y + 0.8 * k), s, h, 0.0, "left" if sg > 0 else "right", "baseline")
        if title:
            c.text((B[0] + sg * 0.8 * k, top[1] + 0.8 * k + h * 1.7 * k), title, h, 0.0,
                   "left" if sg > 0 else "right", "baseline", style="bold")
    x0, x1 = sorted([B[0], B[0] + sg * W])
    return (x0, B[1], x1, top[1] + (0.8 + h * 2.7) * k if title else top[1] + (0.8 + h) * k)


# ================================================================================================ stolarka
def _wall_frame(p_a, p_b, side):
    A, B = np.asarray(p_a, float), np.asarray(p_b, float)
    d = unit(B - A)
    n = perp(d) * side
    return A, B, d, n, float(np.hypot(*(B - A)))


def door(c, p_a, p_b, wall_t: float, side: float = 1.0, hinge: str = "a", leaves: int = 1, frame_w: float = 0.05,
         leaf_t: float = 0.04, threshold: bool = False, style: str = "arc", layer: str = "A-DRZWI",
         center_offset: float = 0.0, swing_deg: float = 90.0):
    """Drzwi rozwierane w otworze (PN-B-01025, oznaczenie uproszczone 1:50–1:200).

    p_a, p_b — krawędzie otworu w OSI ściany (środek grubości), wall_t — grubość ściany w otworze,
    side — strona otwierania (+1 = w lewo od kierunku p_a→p_b), hinge — zawiasy przy 'a' lub 'b'.
    Rysuje ościeżnicę, skrzydło otwarte o 90° (prostokąt lub linia) i łuk zakresu ruchu (linia cienka);
    style='line30' — skrzydło pod kątem 30° bez łuku (oznaczenie umowne 1:200)."""
    k = c.k
    A, B, d, n, W = _wall_frame(p_a, p_b, side)
    half_t = wall_t / 2
    with c.on(layer):
        # ościeżnica (rama w otworze)
        for P, s in ((A, 1), (B, -1)):
            q = [P + n * half_t, P + n * half_t + d * s * frame_w, P - n * half_t + d * s * frame_w, P - n * half_t]
            c.polygon(q, pen="cienka")
        if threshold:
            c.line(A + d * frame_w, B - d * frame_w, pen="cienka")
        clear = W - 2 * frame_w
        face = n * half_t  # lico po stronie otwierania
        leaf_list = []
        if leaves == 1:
            if hinge == "a":
                leaf_list.append((A + d * frame_w + face, d, clear))
            else:
                leaf_list.append((B - d * frame_w + face, -d, clear))
        else:
            wl = clear / 2
            leaf_list.append((A + d * frame_w + face, d, wl))
            leaf_list.append((B - d * frame_w + face, -d, wl))
        for H, dd, wl in leaf_list:
            ang = swing_deg if style == "arc" else 30.0
            # kierunek skrzydła otwartego: od zawiasu, obrót od dd w stronę n
            a_dd = math.degrees(math.atan2(dd[1], dd[0]))
            a_n = math.degrees(math.atan2(n[1], n[0]))
            sgn = 1.0 if ((a_n - a_dd + 360) % 360) < 180 else -1.0
            leaf_dir = dir_deg(a_dd + sgn * ang)
            tip = H + leaf_dir * wl
            if leaf_t / k >= 0.45:
                lp = perp(leaf_dir) * (-sgn) * leaf_t
                c.polygon([H, tip, tip + lp, H + lp], pen="srednia")
            else:
                c.line(H, tip, pen="srednia")
            if style == "arc":
                a0 = a_dd
                a1 = a_dd + sgn * ang
                c.arc(H, wl, min(a0, a1), max(a0, a1), pen="b_cienka")


def sliding_door(c, p_a, p_b, wall_t: float, side: float = 1.0, kind: str = "HS", fixed: str = "a",
                 frame_pos: float = 0.0, frame_depth: float = 0.17, layer: str = "A-DRZWI", arrow: bool = True,
                 panels: int = 2):
    """Drzwi przesuwne (PN-B-01025: skrzydło przesuwne rysowane równolegle do ściany + kierunek przesuwu).
    kind='HS' — drzwi podnoszono-przesuwne w ramie: skrzydło stałe i przesuwne w dwóch prowadnicach;
    kind='chowane' — skrzydło chowane w ścianie (kaseta); kind='naścienne' — skrzydło przed licem ściany.
    frame_pos — przesunięcie osi ramy względem osi ściany (w stronę ``side``)."""
    k = c.k
    A, B, d, n, W = _wall_frame(p_a, p_b, side)
    with c.on(layer):
        if kind == "HS":
            O = n * frame_pos
            fd = frame_depth
            # ościeżnica (rama) na całej szerokości otworu
            c.polygon([A + O + n * fd / 2, B + O + n * fd / 2, B + O - n * fd / 2, A + O - n * fd / 2], pen="srednia")
            sash_t = 0.06
            fw = 0.045
            inner = W - 2 * fw
            pw = inner / panels + 0.04
            # prowadnice: zewnętrzna (skrzydło stałe) i wewnętrzna (skrzydło przesuwne)
            tr_out, tr_in = -fd / 4, fd / 4
            for i in range(panels):
                s0 = fw + i * (inner - pw) / max(1, panels - 1)
                is_fixed = (i == 0 and fixed == "a") or (i == panels - 1 and fixed == "b")
                tr = tr_out if is_fixed else tr_in
                P0 = A + d * s0 + O + n * tr
                q = [P0 - n * sash_t / 2, P0 + d * pw - n * sash_t / 2, P0 + d * pw + n * sash_t / 2,
                     P0 + n * sash_t / 2]
                c.polygon(q, pen="cienka")
                c.line(P0 + d * 0.04, P0 + d * (pw - 0.04), pen="b_cienka")  # szyba
                if arrow and not is_fixed:
                    y = O + n * (fd / 2 + 1.8 * k)
                    a0 = A + d * (s0 + pw * 0.15) + y
                    a1 = A + d * (s0 + pw * 0.85) + y
                    if fixed == "a":
                        a0, a1 = a1, a0
                    c.line(a0, a1, pen="cienka")
                    arrowhead(c, a1, a1 - a0, 2.2, 12, True, layer)
        else:
            off = (wall_t / 2 + 0.03) if kind == "naścienne" else 0.0
            leaf_t = 0.04
            P0 = A + n * off
            L = W + 0.05
            s = 1.0 if fixed == "b" else -1.0
            q = [P0 - n * leaf_t / 2, P0 + d * L - n * leaf_t / 2, P0 + d * L + n * leaf_t / 2, P0 + n * leaf_t / 2]
            shift = -d * (W * 0.55) if kind == "chowane" else d * 0
            c.polygon([p + shift for p in q], pen="srednia")
            if arrow:
                y = n * (leaf_t + 2.0 * k)
                a0, a1 = A + d * W * 0.3 + y, A + d * W * 0.7 + y
                c.line(a1, a0, pen="cienka")
                arrowhead(c, a0, a0 - a1, 2.0, 12, True, layer)


def window(c, p_a, p_b, s_int: float, s_ext: float, frame_in: float, frame_out: float, side: float = 1.0,
           glass: int = 2, sill_in: bool = True, sill_out: bool = True, sill_in_over: float = 0.03,
           sill_out_over: float = 0.04, layer: str = "A-OKNA", fixed_mullions=(), below_cut: bool = False):
    """Okno w rzucie (PN-B-01025, oznaczenie uproszczone): rama, szyba (1–2 linie), parapet wewnętrzny
    i zewnętrzny.

    p_a, p_b     — krawędzie otworu mierzone na OSI ściany (punkty odniesienia wzdłuż ściany),
    s_int, s_ext — odległości lica wewnętrznego / zewnętrznego od osi (wewn. > 0 w stronę ``side``, zewn. < 0),
    frame_in/out — położenie ramy (odległości od osi, jak wyżej), np. rama 8 cm na zewnętrznym licu muru.
    """
    k = c.k
    A, B, d, n, W = _wall_frame(p_a, p_b, side)
    with c.on(layer):
        fr = [A + n * frame_in, B + n * frame_in, B + n * frame_out, A + n * frame_out]
        c.polygon(fr, pen="srednia")
        fw = 0.06
        for P, s in ((A, 1), (B, -1)):
            c.line(P + d * s * fw + n * frame_in, P + d * s * fw + n * frame_out, pen="cienka")
        for m in fixed_mullions:
            P = A + d * m
            c.line(P + n * frame_in, P + n * frame_out, pen="cienka")
        mid = (frame_in + frame_out) / 2
        if glass == 1:
            c.line(A + d * fw + n * mid, B - d * fw + n * mid, pen="cienka")
        else:
            g = abs(frame_in - frame_out) * 0.18
            for s in (-g, g):
                c.line(A + d * fw + n * (mid + s), B - d * fw + n * (mid + s), pen="b_cienka")
        if sill_in and s_int > frame_in + 1e-6:
            e = s_int + sill_in_over
            c.polygon([A + n * frame_in - d * 0.02, B + n * frame_in + d * 0.02, B + n * e + d * 0.02,
                       A + n * e - d * 0.02], pen="cienka")
        if sill_out and s_ext < frame_out - 1e-6:
            e = s_ext - sill_out_over
            c.polygon([A + n * frame_out - d * 0.03, B + n * frame_out + d * 0.03, B + n * e + d * 0.03,
                       A + n * e - d * 0.03], pen="cienka")


# ================================================================================================ schody, otwory
def stairs(c, start, direction, width: float, n_steps: int, tread: float, riser: float | None = None,
           first_no: int = 1, cut_after: int | None = None, numbering: bool = True, arrow: bool = True,
           label: bool = True, layer: str = "A-SCHODY", side_label: float = 1.0, show_above: str = "dashed",
           h: float = 2.0, total_steps: int | None = None, arrow_end_extra: float = 0.0,
           label_at: float | None = None, label_values: tuple | None = None, label_style: str = "inline"):
    """Bieg schodów prostych na rzucie (PN-B-01025).

    start      — środek krawędzi pierwszego stopnia (początek biegu), direction — kierunek wejścia [° lub wektor],
    n_steps    — liczba stopni (podstopnic) w biegu, tread/riser — szerokość (s) / wysokość (h) stopnia [m],
    cut_after  — numer stopnia (licząc w biegu od 1), za którym przebiega płaszczyzna cięcia rzutu: rysowana jest
                 linia cięcia zygzakiem; dalsze stopnie linią kreskową (show_above='dashed') lub pominięte ('none'),
    arrow      — strzałka kierunku wejścia: kółko przy pierwszym stopniu, grot na końcu biegu,
    label      — opis „n × h / s” (liczba i wysokość stopni nad linią, szerokość pod linią) przy strzałce.
    """
    k = c.k
    S = np.asarray(start, float)
    d = dir_deg(direction) if np.isscalar(direction) else unit(direction)
    n = perp(d)
    Wv = n * width / 2
    L = n_steps * tread
    with c.on(layer):
        # krawędzie stopni i obrys
        cut_s = None
        if cut_after is not None:
            cut_s = cut_after * tread + tread * 0.5
        for i in range(n_steps + 1):
            s = i * tread
            P = S + d * s
            above = cut_s is not None and s > cut_s + 1e-9
            if above and show_above == "none":
                continue
            c.line(P - Wv, P + Wv, lt="KRESKOWA" if above else None, pen="cienka")
        for sgn in (-1, 1):
            e0 = S + sgn * Wv
            if cut_s is None:
                c.line(e0, e0 + d * L, pen="srednia")
            else:
                c.line(e0, e0 + d * cut_s, pen="srednia")
                if show_above != "none":
                    c.line(e0 + d * cut_s, e0 + d * L, pen="cienka", lt="KRESKOWA")
        if cut_s is not None:
            # linia cięcia — ukośna z zygzakiem
            p0 = S - Wv + d * (cut_s - tread * 0.6)
            p1 = S + Wv + d * (cut_s + tread * 0.6)
            m = (p0 + p1) / 2
            dd = unit(p1 - p0)
            z = 1.2 * k
            q = [p0 - dd * 1.5 * k, m - dd * z, m + perp(dd) * z * 1.3, m - perp(dd) * z * 1.3, m + dd * z,
                 p1 + dd * 1.5 * k]
            c.polyline(q, pen="cienka")
        if numbering:
            last = n_steps if cut_s is None or show_above != "none" else cut_after
            for i in range(last):
                P = S + d * (i + 0.5) * tread + n * width * 0.33 * side_label
                c.text(P, str(first_no + i), 1.8, readable_angle(math.degrees(math.atan2(d[1], d[0]))),
                       "center", "middle", color=None)
        if arrow:
            a0 = S + d * tread * 0.5
            end_s = (L - tread * 0.3 if cut_s is None else cut_s + tread * 0.1) + arrow_end_extra
            a1 = S + d * end_s
            c.circle(a0, 0.9 * k, pen="cienka")
            c.line(a0 + d * 0.9 * k, a1 - d * 2.0 * k, pen="cienka")
            arrowhead(c, a1, d, 2.4, 12, True, layer)
            if label and riser is not None:
                ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
                r = dir_deg(ang)
                up = perp(r)
                nsteps = total_steps or n_steps
                s_lab = (end_s + tread * 0.5) / 2.0 if label_at is None else label_at
                M = S + d * s_lab
                rv, tv = label_values if label_values else (riser, tread)
                if label_style == "fraction":   # wariant: n × h nad strzałką, s pod strzałką (PN-B-01025, AGH)
                    top = [(f"{nsteps}×", 1.0, 0.0)] + dim_runs(rv, "cm")
                    c.text(M + up * 0.7 * k, None, h, ang, "center", "baseline", runs=top, mask=0.3)
                    c.text(M - up * (0.7 * k + h * k), None, h, ang, "center", "baseline",
                           runs=dim_runs(tv, "cm"), mask=0.3)
                else:                           # "n × h × s" przy strzałce biegu (R4 pkt 3.5)
                    runs = [(f"{nsteps} × ", 1.0, 0.0)] + dim_runs(rv, "cm") + [(" × ", 1.0, 0.0)] + \
                        dim_runs(tv, "cm")
                    c.text(M + up * 0.7 * k, None, h, ang, "center", "baseline", runs=runs, mask=0.3)


def floor_opening(c, poly, layer: str = "A-WIDOK", pen="cienka", closed_opening: bool = False, kind: str = "otwor"):
    """Otwór w stropie/ścianie na rzucie (PN-B-01025 4.6, ISO 7519 6.1): obrys + dwie przekątne (otwór odkryty;
    ``closed_opening`` — przekątne kreskowe); kind='wneka' — jedna przekątna (wnęka)."""
    P = arr(poly)
    with c.on(layer):
        c.polygon(P, pen=pen)
        if len(P) == 4:
            lt = "KRESKOWA" if closed_opening else None
            c.line(P[0], P[2], pen="cienka", lt=lt)
            if kind != "wneka":
                c.line(P[1], P[3], pen="cienka", lt=lt)


def duct(c, poly, kind: str = "went", layer: str = "A-WIDOK"):
    """Kanał w ścianie (PN-B-01025, R4-H11): 'went' — wentylacyjny (przekątna), 'spalinowy' — przekątna z zaczernioną
    połową, 'dymowy' — całość zaczerniona."""
    P = arr(poly)
    with c.on(layer):
        if kind == "dymowy":
            c.fill(P, layer, "#000000")
        elif kind == "spalinowy" and len(P) == 4:
            c.fill([P[0], P[1], P[2]], layer, "#000000")
        c.polygon(P, pen="cienka")
        if len(P) == 4 and kind != "dymowy":
            c.line(P[0], P[2], pen="cienka")


def entrance_arrow(c, pos, direction, filled: bool = True, size_mm: float = 7.0, layer: str = "A-SYMBOLE"):
    """Wejście do budynku (PN-B-01025): strzałka zaczerniona (wejście na poziomie ±0,00 lub wyżej), pusta — poniżej."""
    k = c.k
    d = dir_deg(direction) if np.isscalar(direction) else unit(direction)
    P = np.asarray(pos, float)
    n = perp(d)
    L = size_mm * k
    tri = [P, P - d * L + n * L * 0.35, P - d * L - n * L * 0.35]
    with c.on(layer):
        if filled:
            c.fill(tri, layer, "#000000")
        c.polygon(tri, pen="srednia")


# ================================================================================================ wyposażenie sanitarne i kuchenne
def _poly(c, xf, pts, **kw):
    return c.polygon(xf(arr(pts)), **kw)


def _pl(c, xf, pts, **kw):
    return c.polyline(xf(arr(pts)), **kw)


def _circ(c, xf, x, y, r, **kw):
    return c.circle(xf.pt(x, y), r * xf.scale, **kw)


def wc_hung(c, pos, rot=0.0, w=0.36, d=0.54, frame=True, layer="A-SANITARNE"):
    """Miska WC podwieszana (stelaż podtynkowy linią kreskową). pos — środek na licu ściany."""
    xf = X(pos, rot - 90.0)
    t = np.linspace(0.0, math.pi, 40)
    with c.on(layer):
        if frame:
            _poly(c, xf, rect_pts(-0.25, -0.15, 0.25, 0.0), lt="KRESKOWA", pen="b_cienka")
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, 0.12), pen="cienka")
        bowl = np.column_stack([(w / 2) * np.cos(t), 0.12 + (d - 0.12) * np.sin(t)])
        _pl(c, xf, bowl, pen="cienka")
        _poly(c, xf, ellipse_pts(0.0, 0.12 + (d - 0.12) * 0.46, w / 2 - 0.045, (d - 0.12) * 0.36, 40),
              pen="b_cienka")


def washbasin(c, pos, rot=0.0, w=0.60, d=0.46, layer="A-SANITARNE"):
    """Umywalka ścienna."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rrect(-w / 2, 0.0, w / 2, d, 0.06), pen="cienka")
        _poly(c, xf, ellipse_pts(0, d * 0.55, w * 0.36, d * 0.33, 40), pen="b_cienka")
        _circ(c, xf, 0, 0.07, 0.015, pen="b_cienka")


def washbasin_counter(c, pos, rot=0.0, w=1.20, d=0.50, bowls=1, bowl_w=0.46, bowl_d=0.34, layer="A-SANITARNE"):
    """Umywalka nablatowa (misa na blacie) z blatem."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        for i in range(bowls):
            cx = -w / 2 + w * (i + 0.5) / bowls
            _poly(c, xf, rrect(cx - bowl_w / 2, d * 0.5 - bowl_d / 2 + 0.03, cx + bowl_w / 2,
                              d * 0.5 + bowl_d / 2 + 0.03, 0.08), pen="cienka")
            _poly(c, xf, rrect(cx - bowl_w / 2 + 0.03, d * 0.5 - bowl_d / 2 + 0.06, cx + bowl_w / 2 - 0.03,
                              d * 0.5 + bowl_d / 2, 0.06), pen="b_cienka")
            _circ(c, xf, cx, 0.06, 0.015, pen="b_cienka")


def bathtub(c, pos, rot=0.0, w=1.70, d=0.75, layer="A-SANITARNE"):
    """Wanna prostokątna (pos — środek dłuższego boku przy ścianie)."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        _poly(c, xf, rrect(-w / 2 + 0.07, 0.07, w / 2 - 0.07, d - 0.07, 0.2), pen="b_cienka")
        _circ(c, xf, -w / 2 + 0.22, d / 2, 0.025, pen="b_cienka")


def shower_walkin(c, pos, rot=0.0, w=1.20, d=0.90, drain="linear", glass_side="right", glass_len=None,
                  layer="A-SANITARNE"):
    """Prysznic walk-in bez brodzika: pole natrysku, odpływ liniowy przy ścianie, ścianka szklana,
    spadki posadzki (strzałki). pos — środek boku przy ścianie."""
    k = c.k
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="b_cienka", lt="KRESKOWA_DROBNA")
        if drain == "linear":
            _poly(c, xf, rect_pts(-w / 2 + 0.1, 0.05, w / 2 - 0.1, 0.12), pen="cienka")
            _pl(c, xf, [(-w / 2 + 0.12, 0.085), (w / 2 - 0.12, 0.085)], pen="b_cienka")
            for x in np.linspace(-w / 2 + 0.25, w / 2 - 0.25, 3):
                a = xf.pt(x, d * 0.7)
                b = xf.pt(x, 0.2)
                c.line(a, b - (b - a) / np.hypot(*(b - a)) * 1.8 * k, pen="b_cienka")
                arrowhead(c, b, b - a, 1.8, 12, True, layer, pen="b_cienka")
        else:
            _poly(c, xf, rect_pts(-0.06, d / 2 - 0.06, 0.06, d / 2 + 0.06), pen="cienka")
            _pl(c, xf, [(-w / 2, 0), (w / 2, d)], pen="b_cienka")
            _pl(c, xf, [(-w / 2, d), (w / 2, 0)], pen="b_cienka")
        gl = glass_len if glass_len is not None else d
        xg = w / 2 if glass_side == "right" else -w / 2
        _poly(c, xf, rect_pts(xg - 0.005, 0.0, xg + 0.005, gl), pen="srednia")


def washing_machine(c, pos, rot=0.0, w=0.60, d=0.60, label="P", layer="A-SANITARNE"):
    """Pralka (label 'P') / suszarka (label 'S') — prostokąt z bębnem i literą."""
    k = c.k
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        _circ(c, xf, 0, d * 0.55, min(w, d) * 0.32, pen="b_cienka")
        c.text(xf.pt(0, d * 0.55), label, 2.5, 0.0, "center", "middle")


def dryer(c, pos, rot=0.0, w=0.60, d=0.60, layer="A-SANITARNE"):
    washing_machine(c, pos, rot, w, d, "S", layer)


def kitchen_sink(c, pos, rot=0.0, w=0.80, d=0.50, bowls=1, drainer=True, layer="A-SANITARNE"):
    """Zlewozmywak (komora + ociekacz) w blacie."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rrect(-w / 2, 0.05, w / 2, d - 0.03, 0.03), pen="cienka")
        bw = (w * 0.55 if drainer else w - 0.08) / bowls
        x0 = -w / 2 + 0.04
        for i in range(bowls):
            _poly(c, xf, rrect(x0 + i * bw + 0.01, 0.1, x0 + (i + 1) * bw - 0.01, d - 0.08, 0.04), pen="b_cienka")
            _circ(c, xf, x0 + (i + 0.5) * bw, (d - 0.08 + 0.1) / 2, 0.02, pen="b_cienka")
        if drainer:
            for y in np.linspace(0.14, d - 0.12, 5):
                _pl(c, xf, [(x0 + bowls * bw + 0.05, y), (w / 2 - 0.05, y)], pen="b_cienka")
        _circ(c, xf, x0 + bw * bowls / 2, 0.08, 0.018, pen="b_cienka")


def hob(c, pos, rot=0.0, w=0.60, d=0.52, zones=4, layer="A-SANITARNE"):
    """Płyta indukcyjna (4 pola grzejne)."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.04, w / 2, 0.04 + d), pen="cienka")
        cs = [(-w * 0.24, 0.04 + d * 0.3, 0.09), (w * 0.24, 0.04 + d * 0.3, 0.075),
              (-w * 0.24, 0.04 + d * 0.72, 0.075), (w * 0.24, 0.04 + d * 0.72, 0.09)][:zones]
        for (x, y, r) in cs:
            _circ(c, xf, x, y, r, pen="b_cienka")


def appliance(c, pos, rot=0.0, w=0.60, d=0.60, label="LOD", layer="A-SANITARNE", h=2.0):
    """Urządzenie w zabudowie (lodówka 'LOD', zmywarka 'ZM', piekarnik 'PK', …): prostokąt z opisem."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        _pl(c, xf, [(-w / 2, d - 0.04), (w / 2, d - 0.04)], pen="b_cienka")
        c.text(xf.pt(0, d * 0.5), label, h, 0.0, "center", "middle")


def fridge(c, pos, rot=0.0, w=0.60, d=0.65, layer="A-SANITARNE"):
    appliance(c, pos, rot, w, d, "LOD", layer)


def dishwasher(c, pos, rot=0.0, w=0.60, d=0.58, layer="A-SANITARNE"):
    appliance(c, pos, rot, w, d, "ZM", layer)


def counter(c, pts, depth=0.60, side=1.0, layer="A-MEBLE", upper: bool = False):
    """Blat kuchenny wzdłuż łamanej przy ścianie (lico ściany), głębokość ``depth`` w stronę ``side``.
    upper=True — dodatkowo szafki wiszące (linia kreskowa, gł. 0,35 m)."""
    P = arr(pts)
    ls = LineString(P)
    off = ls.offset_curve(depth * side, join_style=2)
    Q = np.asarray(off.coords)
    with c.on(layer):
        c.polyline(Q, pen="cienka")
        c.line(P[0], Q[0], pen="cienka")
        c.line(P[-1], Q[-1], pen="cienka")
        if upper:
            off2 = np.asarray(ls.offset_curve(0.35 * side, join_style=2).coords)
            c.polyline(off2, pen="b_cienka", lt="KRESKOWA")


# ================================================================================================ meble
def bed(c, pos, rot=0.0, w=1.60, l=2.00, pillows=None, layer="A-MEBLE"):
    """Łóżko (pos — środek wezgłowia przy ścianie)."""
    xf = X(pos, rot - 90.0)
    pillows = pillows or (2 if w >= 1.2 else 1)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, l), pen="cienka")
        _pl(c, xf, [(-w / 2, 0.06), (w / 2, 0.06)], pen="b_cienka")
        pw = (w - 0.12 - (pillows - 1) * 0.06) / pillows
        for i in range(pillows):
            x0 = -w / 2 + 0.06 + i * (pw + 0.06)
            _poly(c, xf, rrect(x0, 0.1, x0 + pw, 0.42, 0.05), pen="b_cienka")
        _pl(c, xf, [(-w / 2, 0.62), (w / 2, 0.62)], pen="b_cienka")
        _pl(c, xf, [(-w / 2, 0.62), (-w / 2 + 0.35, 0.95), (w / 2, 0.95)], pen="b_cienka")


def wardrobe(c, pos, rot=0.0, w=1.20, d=0.60, doors="hinged", layer="A-MEBLE"):
    """Szafa (pos — środek tylnej ściany przy ścianie): drążek + wieszaki; drzwi przesuwne — dwie prowadnice."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        _pl(c, xf, [(-w / 2 + 0.03, d / 2 - 0.03), (w / 2 - 0.03, d / 2 - 0.03)], pen="b_cienka")
        n = max(2, int(w / 0.12))
        for x in np.linspace(-w / 2 + 0.08, w / 2 - 0.08, n):
            _pl(c, xf, [(x - 0.03, d * 0.18), (x + 0.03, d * 0.78)], pen="b_cienka")
        if doors == "sliding":
            _pl(c, xf, [(-w / 2, d - 0.02), (0.05, d - 0.02)], pen="cienka")
            _pl(c, xf, [(-0.05, d - 0.05), (w / 2, d - 0.05)], pen="cienka")


def sofa(c, pos, rot=0.0, w=2.20, d=0.92, seats=3, layer="A-MEBLE"):
    """Sofa (pos — środek oparcia)."""
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rrect(-w / 2, 0.0, w / 2, d, 0.06), pen="cienka")
        _poly(c, xf, rect_pts(-w / 2 + 0.2, 0.2, w / 2 - 0.2, d - 0.02), pen="b_cienka")
        for i in range(1, seats):
            x = -w / 2 + 0.2 + (w - 0.4) * i / seats
            _pl(c, xf, [(x, 0.2), (x, d - 0.02)], pen="b_cienka")


def table_chairs(c, center, rot=0.0, w=1.80, d=0.90, chairs=6, layer="A-MEBLE", round_table=False):
    """Stół z krzesłami (center — środek stołu)."""
    xf = X(center, rot)
    cw, cd = 0.44, 0.42
    with c.on(layer):
        if round_table:
            _circ(c, xf, 0, 0, w / 2, pen="cienka")
        else:
            _poly(c, xf, rect_pts(-w / 2, -d / 2, w / 2, d / 2), pen="cienka")
        per_side = chairs // 2
        pos = []
        for i in range(per_side):
            x = -w / 2 + w * (i + 0.5) / per_side
            pos.append((x, d / 2 + 0.08, 0))
            pos.append((x, -d / 2 - 0.08, 180))
        if chairs % 2:
            pos.append((w / 2 + 0.08, 0, -90))
        for (x, y, a) in pos:
            cx = X(xf.pt(x, y), xf.angle + a)
            pts = rrect(-cw / 2, 0.0, cw / 2, cd, 0.05)
            c.polygon(cx(pts), pen="b_cienka")
            c.line(cx.pt(-cw / 2 + 0.03, cd - 0.07), cx.pt(cw / 2 - 0.03, cd - 0.07), pen="b_cienka")


def desk(c, pos, rot=0.0, w=1.40, d=0.70, chair=True, layer="A-MEBLE"):
    xf = X(pos, rot - 90.0)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, 0.0, w / 2, d), pen="cienka")
        if chair:
            cx = X(xf.pt(0.0, d + 0.45), xf.angle + 180)
            c.polygon(cx(rrect(-0.24, 0.0, 0.24, 0.46, 0.08)), pen="b_cienka")
            c.line(cx.pt(-0.2, 0.40), cx.pt(0.2, 0.40), pen="b_cienka")


def kitchen_island(c, center, rot=0.0, w=2.40, d=1.00, stools=3, hob_on=True, layer="A-MEBLE"):
    """Wyspa kuchenna z hokerami po stronie +y (lokalnie) i opcjonalnie płytą grzejną."""
    xf = X(center, rot)
    with c.on(layer):
        _poly(c, xf, rect_pts(-w / 2, -d / 2, w / 2, d / 2), pen="cienka")
        _pl(c, xf, [(-w / 2, d / 2 - 0.3), (w / 2, d / 2 - 0.3)], pen="b_cienka", lt="KRESKOWA_DROBNA")
        for i in range(stools):
            x = -w / 2 + w * (i + 0.5) / stools
            _circ(c, xf, x, d / 2 + 0.25, 0.18, pen="b_cienka")
    if hob_on:
        hob(c, xf.pt(0.0, -d / 2), xf.angle + 90.0, 0.6, 0.5)


# ------------------------------------------------------------------------------------------------ re-eksport
from .symbols_inst import *  # noqa: E402,F401,F403
from .symbols_site import *  # noqa: E402,F401,F403
