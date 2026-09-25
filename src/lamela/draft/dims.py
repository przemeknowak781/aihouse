"""Wymiarowanie wg PN-B-01029:2000 (rysunki architektoniczno-budowlane) i oznaczenia poziomów wg PN-B-01025:2004.

* Linie wymiarowe i pomocnicze — linia cienka ciągła; ograniczniki — kreski ukośne pod kątem 45° (linia średnia);
  linia wymiarowa przedłużona poza skrajne linie pomocnicze; linie pomocnicze jednakowej długości, nie
  doprowadzane do obrysu (tryb ``ext='short'``) albo od obiektu z odstępem (``ext='full'``).
* Liczby wymiarowe nad linią wymiarową, czytelne od dołu lub od prawej strony arkusza; jednostka cm,
  milimetry w indeksie górnym (np. 24⁵); na PZT metry.
* Automatyczne rozsuwanie kolidujących liczb: poza odcinek (przy wolnym miejscu), pod linię, na drugi poziom
  z odnośnikiem.
* Rzędne: przekroje/elewacje — trójkąt 90° zaczerniony (wykończenie), niezaczerniony (konstrukcja), w połowie
  zaczerniony (poziom ±0,00 + rzędna bezwzględna), grot otwarty (PN); rzuty — znak „X” z linią odniesienia lub
  wartość w ramce.
"""
from __future__ import annotations

import math

import numpy as np

from . import fmt, text as T
from .geom import arr, dir_deg, perp, readable_angle, rot, unit

DIM_LAYER = "A-WYMIARY"
LEVEL_LAYER = "A-RZEDNE"


# ================================================================================================ pomocnicze
def arrowhead(c, tip, direction, length_mm: float = 2.5, half_angle: float = 10.0, filled: bool = True,
              layer=None, pen="cienka"):
    """Grot strzałki (ISO 129: 15°…90°) z wierzchołkiem w ``tip`` skierowany zgodnie z ``direction``."""
    d = unit(direction)
    L = length_mm * c.k
    a = math.radians(half_angle)
    back = -d * L
    p1 = np.asarray(tip) + rot([back], half_angle)[0]
    p2 = np.asarray(tip) + rot([back], -half_angle)[0]
    if filled:
        c.fill([tip, p1, p2], layer, "#000000")
        c.polygon([tip, p1, p2], layer, pen=pen)
    else:
        c.polyline([p1, tip, p2], layer, pen=pen)


def dim_runs(value_m: float, unit_: str = "cm", prefix: str = "", suffix: str = ""):
    main, sup = fmt.dim_parts(value_m, unit_)
    runs = [(prefix + main, 1.0, 0.0)]
    if sup:
        runs.append((sup, T.SUP_SIZE, T.SUP_RAISE))
    if suffix:
        runs.append((suffix, 1.0, 0.0))
    return runs


# ================================================================================================ łańcuch wymiarowy
def dim_chain(c, pts, at, direction="h", layer: str = DIM_LAYER, h: float = 2.5, unit_: str = "cm",
              ext: str = "short", ext_len=(2.0, 1.8), gap_mm: float = 1.5, tick_mm: float = 2.6,
              overshoot_mm: float = 1.8, text_gap_mm: float = 0.7, labels=None, min_seg: float = 1e-4,
              tick_pen="srednia", mask: float = 0.0):
    """Łańcuch wymiarowy.

    pts        — punkty wymiarowane (współrzędne płótna); rzutowane na linię wymiarową,
    at         — punkt, przez który przechodzi linia wymiarowa (albo liczba: y dla 'h', x dla 'v'),
    direction  — 'h' | 'v' | kąt [°] kierunku linii wymiarowej,
    ext        — 'short': krótkie linie pomocnicze jednakowej długości (ext_len = (od strony obiektu, poza linię)
                 [mm]); 'full': od punktu (z odstępem gap_mm) do linii wymiarowej + nadmiar,
    labels     — opcjonalne własne opisy odcinków (lista napisów/None),
    Zwraca słownik z pozycjami (do łączenia z kolejnymi łańcuchami).
    """
    k = c.k
    if direction == "h":
        d = np.array([1.0, 0.0])
    elif direction == "v":
        d = np.array([0.0, 1.0])
    else:
        d = dir_deg(float(direction))
    n = perp(d)
    P = arr(pts)
    if np.isscalar(at) or (isinstance(at, (int, float))):
        at_pt = np.array([0.0, float(at)]) if direction == "h" else np.array([float(at), 0.0])
    else:
        at_pt = np.asarray(at, float)
    s_line = float(at_pt @ n)
    ts = sorted(set(round(float(p @ d), 9) for p in P))
    # scal punkty bardzo bliskie
    tt = []
    for t in ts:
        if not tt or t - tt[-1] > min_seg:
            tt.append(t)
    if len(tt) < 2:
        return None
    # strona obiektu: średnio punkty po której stronie linii
    s_obj = float(np.mean(P @ n))
    side = 1.0 if s_line >= s_obj else -1.0   # kierunek od obiektu do linii wymiarowej
    nn = n * side
    foot = lambda t: n * s_line + d * t  # noqa: E731

    with c.on(layer):
        # linia wymiarowa
        c.line(foot(tt[0]) - d * overshoot_mm * k, foot(tt[-1]) + d * overshoot_mm * k)
        # linie pomocnicze + ograniczniki
        tick_dir = rot([d], 45.0)[0]
        for t in tt:
            F = foot(t)
            if ext == "full":
                src = [p for p in P if abs(float(p @ d) - t) < 1e-6]
                s_src = min((float(p @ n) for p in src), key=lambda s: abs(s - s_line)) if src else s_obj
                A = n * (s_src + side * gap_mm * k) + d * t
                B = F + nn * ext_len[1] * k
                if (B - A) @ nn > 0:
                    c.line(A, B)
            else:
                c.line(F - nn * ext_len[0] * k, F + nn * ext_len[1] * k)
            half = tick_mm * k / 2.0
            c.line(F - tick_dir * half, F + tick_dir * half, pen=tick_pen)

        # liczby wymiarowe
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        r = dir_deg(ang)                 # kierunek czytania
        up = perp(r)                     # "nad" linią w układzie napisu
        sgn = 1.0 if (r @ d) > 0 else -1.0
        segs = []
        for i in range(len(tt) - 1):
            L = tt[i + 1] - tt[i]
            if labels is not None and i < len(labels) and labels[i] is not None:
                lab = labels[i]
                runs = list(lab) if isinstance(lab, (list, tuple)) else [(str(lab), 1.0, 0.0)]
            else:
                runs = dim_runs(L, unit_)
            w = T.runs_width(runs, h) * k
            segs.append({"i": i, "t0": tt[i], "t1": tt[i + 1], "L": L, "w": w, "runs": runs})
        _place_dim_texts(c, segs, foot, d, r, up, sgn, ang, h, text_gap_mm, tick_mm, layer, mask)
    return {"t": tt, "s": s_line, "d": d, "n": n}


def _place_dim_texts(c, segs, foot, d, r, up, sgn, ang, h, gap_mm, tick_mm, layer, mask=0.0):
    k = c.k
    clear = 0.6 * k
    tick_clear = (tick_mm / 2.0 * 0.72 + 0.35) * k
    tiers = {0: [], -1: [], 1: []}
    all_t = sorted(set([s["t0"] for s in segs] + [s["t1"] for s in segs]))

    def free(tier, a, b):
        return all(b + clear <= x0 or a - clear >= x1 for (x0, x1) in tiers[tier])

    def ticks_in(a, b):
        return any(a - tick_clear < t < b + tick_clear for t in all_t)

    def put(s, tier, a):
        b = a + s["w"]
        tiers[tier].append((a, b))
        s["pos"] = (tier, a)

    # 1) mieszczące się — na środku
    for s in segs:
        a = (s["t0"] + s["t1"]) / 2.0 - s["w"] / 2.0
        if s["w"] + 2 * tick_clear <= s["L"]:
            put(s, 0, a)
    # 2) pozostałe
    rest = [s for s in segs if "pos" not in s]
    for s in rest:
        w = s["w"]
        mid = (s["t0"] + s["t1"]) / 2.0
        cands = []
        # obok odcinka (prawo / lewo) na poziomie 0 — bez przecinania kresek
        cands.append((0, s["t1"] + tick_clear))
        cands.append((0, s["t0"] - tick_clear - w))
        placed = False
        for tier, a in cands:
            if free(tier, a, a + w) and not ticks_in(a, a + w):
                put(s, tier, a)
                placed = True
                break
        if placed:
            continue
        # pod linią, wyśrodkowany
        a = mid - w / 2.0
        if free(-1, a, a + w):
            put(s, -1, a)
            continue
        # drugi poziom nad linią (z odnośnikiem)
        a = mid - w / 2.0
        step = 0.0
        while not free(1, a + step, a + step + w) and step < 30 * k:
            step += 0.5 * k
        put(s, 1, a + step)

    for s in segs:
        tier, a = s["pos"]
        t_mid = a + s["w"] / 2.0
        base = foot(t_mid)
        if tier == 0:
            pos = base + up * gap_mm * k
            va = "bottom_line"
        elif tier == -1:
            pos = base - up * (gap_mm * k + h * k)
            va = "bottom_line"
        else:
            pos = base + up * (gap_mm * k + h * 1.9 * k)
            va = "bottom_line"
            # odnośnik od środka odcinka do napisu
            mid = foot((s["t0"] + s["t1"]) / 2.0)
            c.line(mid, base + up * (gap_mm * k + h * 1.9 * k - 0.5 * k))
        c.text(pos, None, h, ang, "center", "baseline", runs=s["runs"], mask=mask)


def dim_h(c, xs, y, y_ref=None, **kw):
    """Łańcuch poziomy: xs — współrzędne x punktów, y — rzędna linii wymiarowej, y_ref — y obiektu
    (strona, z której przychodzą linie pomocnicze; domyślnie poniżej linii jeśli y_ref < y)."""
    y_ref = y - 1.0 if y_ref is None else y_ref
    return dim_chain(c, [(x, y_ref) for x in xs], (0.0, y), "h", **kw)


def dim_v(c, ys, x, x_ref=None, **kw):
    """Łańcuch pionowy: ys — współrzędne y punktów, x — odcięta linii wymiarowej."""
    x_ref = x - 1.0 if x_ref is None else x_ref
    return dim_chain(c, [(x_ref, y) for y in ys], (x, 0.0), "v", **kw)


def dim_aligned(c, p1, p2, offset_mm: float = 8.0, **kw):
    """Wymiar równoległy (ukośny) odcinka p1-p2, linia wymiarowa odsunięta o offset_mm (w lewo od p1→p2)."""
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(p2 - p1)
    ang = math.degrees(math.atan2(d[1], d[0]))
    at = p1 + perp(d) * offset_mm * c.k
    return dim_chain(c, [p1, p2], at, ang, **kw)


# ================================================================================================ otwory
def opening_dim(c, center, wall_dir, width: float, height: float, sill: float | None = None, side: float = 1.0,
                symbol: str | None = None, h: float = 2.5, start_mm: float = 1.0, axis_mm: float = 14.0,
                layer: str = DIM_LAYER, unit_: str = "cm", symbol_shape: str = "circle", sym_r_mm: float = 3.2):
    """Wymiar otworu wg PN-B-01029: ułamek na osi otworu (licznik — szerokość, mianownik — wysokość;
    wysokość parapetu w nawiasie przed wysokością otworu). Oś otworu prowadzona prostopadle do ściany od punktu
    ``center`` (np. lico ściany w osi otworu) w stronę ``side`` (+1 = w lewo od kierunku ściany).
    Opcjonalnie symbol stolarki w kółku na końcu osi (zamiast/obok wymiarów, gdy istnieje zestawienie stolarki).
    """
    k = c.k
    d = unit(wall_dir)
    n = perp(d) * side
    C = np.asarray(center, float)
    top_runs = dim_runs(width, unit_) if width is not None else None
    bot_runs = None
    if height is not None:
        bot_runs = dim_runs(height, unit_)
        if sill is not None:
            m, sp = fmt.dim_parts(sill, unit_)
            bot_runs = [("(" + m, 1.0, 0.0)] + ([(sp, T.SUP_SIZE, T.SUP_RAISE)] if sp else []) + \
                [(") ", 1.0, 0.0)] + bot_runs
    wtxt = max([T.runs_width(r, h) for r in (top_runs, bot_runs) if r] or [0.0])
    axis_mm = max(axis_mm, wtxt + 2.0) if wtxt else axis_mm
    A = C + n * start_mm * k
    B = C + n * (start_mm + axis_mm) * k
    with c.on(layer):
        c.line(A, B)
        ang = readable_angle(math.degrees(math.atan2(n[1], n[0])))
        r = dir_deg(ang)
        up = perp(r)
        M = (A + B) / 2.0
        if top_runs:
            c.text(M + up * 0.7 * k, None, h, ang, "center", "baseline", runs=top_runs)
        if bot_runs:
            c.text(M - up * (0.7 * k + h * k), None, h, ang, "center", "baseline", runs=bot_runs)
        if symbol:
            from .symbols import tag
            tag(c, B + n * sym_r_mm * k, symbol, shape=symbol_shape, r_mm=sym_r_mm, layer="A-OPISY")
    return B


# ================================================================================================ rzędne
def level_section(c, pt, z: float | None = None, kind: str = "wyk", side: str = "right", text: str | None = None,
                  abs_z: float | None = None, h: float = 2.5, nd: int = 2, stub_mm: float = 5.0,
                  layer: str = LEVEL_LAYER, size_mm: float = 2.2, stem_mm: float = 1.2, mask: float = 0.4):
    """Rzędna na przekroju/elewacji. ``pt`` — punkt na poziomie (wierzchołek trójkąta).

    kind: 'wyk'   — trójkąt zaczerniony (poziom wykończenia, np. posadzki),
          'konstr'— trójkąt niezaczerniony (poziom konstrukcji — wierzch stropu, spód płyty),
          'zero'  — trójkąt w połowie zaczerniony + rzędna bezwzględna pod linią odniesienia (PN-B-01025),
          'pn'    — grot otwarty 90° (PN-B-01025, kolejne poziomy).
    side: 'right' | 'left' — strona linii odniesienia z opisem.
    """
    k = c.k
    P = np.asarray(pt, float)
    s = size_mm * k
    sg = 1.0 if side == "right" else -1.0
    label = text if text is not None else fmt.level(z, nd)
    if kind == "zero" and text is None:
        label = fmt.level(0.0, nd)
    with c.on(layer):
        # krótki odcinek poziomu (wskazanie linii)
        if stub_mm:
            c.line(P - np.array([stub_mm * k * 0.5 * sg, 0]), P + np.array([stub_mm * k * 0.6 * sg, 0]))
        apex = P
        bl = P + np.array([-s, s])
        br = P + np.array([s, s])
        if kind == "pn":
            c.polyline([bl, apex, br])
        else:
            c.polygon([apex, br, bl])
            if kind == "wyk":
                c.fill([apex, br, bl], layer, "#000000")
            elif kind == "zero":
                if sg > 0:
                    c.fill([apex, br, P + np.array([0, s])], layer, "#000000")
                else:
                    c.fill([apex, P + np.array([0, s]), bl], layer, "#000000")
        top = P + np.array([0.0, s])
        if abs_z is not None:  # miejsce na rzędną bezwzględną pod linią odniesienia (PN-B-01025)
            stem_mm = max(stem_mm, h + 2.0)
        stem_top = top + np.array([0.0, stem_mm * k])
        c.line(top, stem_top)
        w = T.width(label, h) * k
        if abs_z is not None:
            w = max(w, T.width(fmt.level_abs(abs_z), h) * k)
        ref_end = stem_top + np.array([sg * (w + 1.5 * k), 0.0])
        c.line(stem_top, ref_end)
        tx = stem_top + np.array([sg * 0.8 * k, 0.7 * k])
        c.text(tx, label, h, 0.0, "left" if sg > 0 else "right", "baseline", mask=mask)
        if abs_z is not None:
            c.text(stem_top + np.array([sg * 0.8 * k, -0.9 * k]), fmt.level_abs(abs_z), h, 0.0,
                   "left" if sg > 0 else "right", "top", mask=mask)


def levels(c, x: float, items, side: str = "right", h: float = 2.5, nd: int = 2, gap_mm: float = 1.5,
           layer: str = LEVEL_LAYER, stub_mm: float = 4.0, **kw):
    """Zestaw rzędnych przy jednej krawędzi przekroju z automatycznym rozsuwaniem: znaczniki, które zachodziłyby
    na siebie w pionie, są przesuwane do kolejnej "kolumny" (w stronę ``side``).
    items: [(z, kind) | (z, kind, abs_z)], x — położenie wierzchołków trójkątów pierwszej kolumny."""
    k = c.k
    sg = 1.0 if side == "right" else -1.0
    hgt = (2.2 + 1.2 + 0.7 + h + gap_mm) * k       # wysokość znacznika (trójkąt + trzonek + napis)
    cols: list[list[tuple]] = []
    widths: list[float] = []
    for it in sorted(items, key=lambda t: t[0]):
        z, kind = it[0], it[1]
        abs_z = it[2] if len(it) > 2 else None
        lab = fmt.level(z, nd)
        w = (T.width(lab, h) + 4.5) * k
        lo, hi = z, z + hgt + ((h + 0.8) * k if abs_z is not None else 0.0)
        ci = 0
        while ci < len(cols) and any(not (hi <= a or lo >= b) for a, b in cols[ci]):
            ci += 1
        if ci == len(cols):
            cols.append([])
            widths.append(0.0)
        cols[ci].append((lo, hi))
        widths[ci] = max(widths[ci], w)
        xx = x + sg * sum(widths[:ci])
        level_section(c, (xx, z), z, kind, side, abs_z=abs_z, h=h, nd=nd, layer=layer,
                      stub_mm=stub_mm if ci == 0 else 0.0, **kw)


def level_plan(c, pt, z: float | None = None, style: str = "x", text: str | None = None, h: float = 2.5,
               nd: int = 2, layer: str = LEVEL_LAYER, direction: float = 1.0):
    """Rzędna na rzucie. style: 'x' — znak „X” + linia odniesienia z wartością nad nią (PN-B-01025);
    'o' — kółko (punkt wyznaczony przecięciem linii zarysu); 'box' — wartość w ramce (praktyka: rzędna posadzki)."""
    k = c.k
    P = np.asarray(pt, float)
    label = text if text is not None else fmt.level(z, nd)
    w = T.width(label, h) * k
    with c.on(layer):
        if style == "box":
            pad = 0.8 * k
            c.rect(P[0] - w / 2 - pad, P[1] - h * k / 2 - pad, P[0] + w / 2 + pad, P[1] + h * k / 2 + pad)
            c.text(P, label, h, 0, "center", "middle")
            return
        s = 1.1 * k
        if style == "x":
            c.line(P + [-s, -s], P + [s, s])
            c.line(P + [-s, s], P + [s, -s])
        else:
            c.circle(P, 0.9 * k)
        sg = direction
        end = P + np.array([sg * (w + 2.0 * k + s), 0.0])
        c.line(P, end)
        c.text(P + np.array([sg * (s + 0.8 * k), 0.8 * k]), label, h, 0, "left" if sg > 0 else "right", "baseline")


# ================================================================================================ spadki, promienie, kąty
def slope(c, p_from, p_to, value_pct: float | None = None, text: str | None = None, h: float = 2.5,
          layer: str = "A-SYMBOLE", ramp: bool = False):
    """Spadek: strzałka z grotem w kierunku spadku (PN-B-01025) i opis nad strzałką (np. 2,0%).
    ``ramp=True`` — pochylnia: kółko na początku, grot wskazuje kierunek wznoszenia."""
    k = c.k
    A, B = np.asarray(p_from, float), np.asarray(p_to, float)
    d = unit(B - A)
    label = text if text is not None else fmt.percent(value_pct, 1)
    with c.on(layer):
        c.line(A, B - d * 2.2 * k)
        arrowhead(c, B, d, 2.6, 11.0, True, layer)
        if ramp:
            c.circle(A, 0.8 * k)
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        up = perp(dir_deg(ang))
        c.text((A + B) / 2 + up * 0.8 * k, label, h, ang, "center", "baseline")


def dim_radius(c, center, r: float, angle_deg: float = 45.0, unit_: str = "cm", h: float = 2.5,
               layer: str = DIM_LAYER):
    """Wymiar promienia: linia od środka do łuku z grotem, opis „R …”."""
    k = c.k
    C = np.asarray(center, float)
    d = dir_deg(angle_deg)
    E = C + d * r
    with c.on(layer):
        c.line(C, E - d * 2.0 * k)
        arrowhead(c, E, d, 2.5, 10, True, layer)
        ang = readable_angle(angle_deg)
        up = perp(dir_deg(ang))
        c.text((C + E) / 2 + up * 0.7 * k, None, h, ang, "center", "baseline", runs=dim_runs(r, unit_, prefix="R"))


def dim_angle(c, vertex, a0: float, a1: float, radius_mm: float = 12.0, h: float = 2.5, layer: str = DIM_LAYER,
              nd: int = 0):
    """Wymiar kąta: łuk między kierunkami a0→a1 [°] z grotami, opis w stopniach."""
    k = c.k
    V = np.asarray(vertex, float)
    R = radius_mm * k
    if a1 < a0:
        a1 += 360
    with c.on(layer):
        c.arc(V, R, a0, a1)
        for a, sgn in ((a0, -1), (a1, 1)):
            tip = V + dir_deg(a) * R
            tang = dir_deg(a + 90 * sgn)
            arrowhead(c, tip, tang, 2.2, 10, True, layer)
        am = (a0 + a1) / 2
        pos = V + dir_deg(am) * (R + 1.2 * k)
        c.text(pos, fmt.num(a1 - a0, nd) + "°", h, readable_angle(am - 90), "center", "baseline")


def leader(c, pts, text: str | list | None = None, h: float = 2.5, end: str = "arrow", layer: str = "A-OPISY",
           shelf_mm: float | None = None, above: bool = True):
    """Odnośnik (PN-B-01025 / ISO 128): linia wskazująca (pierwszy punkt = wskazywany obiekt) + linia odniesienia
    z opisem nad nią. end: 'arrow' (do krawędzi), 'dot' (wewnątrz pola), 'none' (na innej linii)."""
    k = c.k
    P = arr(pts)
    lines = text if isinstance(text, list) else ([text] if text else [])
    with c.on(layer):
        c.polyline(P)
        if end == "arrow":
            arrowhead(c, P[0], P[0] - P[1], 2.5, 10, True, layer)
        elif end == "dot":
            c.dot(P[0], 0.9, layer)
        if lines:
            last = P[-1]
            dirx = 1.0 if (P[-1][0] - P[-2][0]) >= 0 else -1.0
            w = max(T.width(s, h) for s in lines) * k
            shelf = shelf_mm * k if shelf_mm else w + 1.5 * k
            end_pt = last + np.array([dirx * shelf, 0.0])
            c.line(last, end_pt)
            x0 = last[0] + dirx * 0.8 * k
            for i, s in enumerate(lines):
                y = last[1] + 0.8 * k + (len(lines) - 1 - i) * h * 1.6 * k if above else last[1] - (i + 1) * h * 1.6 * k
                c.text((x0, y), s, h, 0, "left" if dirx > 0 else "right", "baseline")
