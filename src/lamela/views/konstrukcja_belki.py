"""Rysunki zbrojenia belek, nadproży i schodów (``k_zbrojenie``, ``element: belki | nadproza | schody``).

Belka: widok podłużny (beton, podpory, pręty dolne/górne z odgięciami, strzemiona z rozstawem), przekrój poprzeczny
w środku rozpiętości (pręty, strzemię, płyta współpracująca), wyciąg prętów (kształty ISO 3766 z wymiarami). Liczby
i średnice prętów, rozstaw strzemion — z pozycji obliczeniowych biblioteki (``konstrukcja_dane.BelkaZ``); długości
i kształty — z geometrii (oś belki z modelu, otulina c_nom z klasy ekspozycji).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, box

from ..draft import dims, hatch as H
from . import konstrukcja_dane as KD
from .common import Placer

L_OBR = "K-KONSTR"
L_ZBR = "K-ZBROJENIE"
L_OPI = "K-ZBROJENIE-OPIS"
L_OPS = "A-OPISY"


def prety_belki(B: KD.BelkaZ, zest: KD.Zestawienie, a_op: float = 0.15) -> dict:
    """Pręty belki (ISO 3766): dolne i górne kształt 21 (odgięcia ≤ 25 cm w podporach), strzemiona 51.
    ``a_op`` — oparcie (poza oś podpory skrajnej) [m]."""
    c = B.c_nom / 1000.0
    fs = B.strz[0] / 1000.0
    L = B.L + 2 * a_op
    cm = c + fs                                   # otulina prętów głównych
    leg = min(0.25, B.h - 2 * cm)
    out = {}
    out["dol"] = zest.dodaj(KD.Pret(B.dol[1], "21", (leg * 1000, (L - 2 * cm) * 1000, leg * 1000), B.dol[0], B.id, "dołem"))
    out["gora"] = zest.dodaj(KD.Pret(B.gora[1], "21", (leg * 1000, (L - 2 * cm) * 1000, leg * 1000), B.gora[0], B.id,
                                     "górą"))
    ns = int(math.ceil((L - 2 * 0.05) / (B.strz[1] / 1000.0))) + 1
    out["strz"] = zest.dodaj(KD.Pret(B.strz[0], "51", ((B.b - 2 * c) * 1000, (B.h - 2 * c) * 1000), ns, B.id, "strzemię"))
    out.update(L=L, leg=leg, cm=cm, ns=ns, a_op=a_op)
    return out


def _nr(c, pos, nr):
    from .konstrukcja import _nr_poz
    _nr_poz(c, pos, nr, 2.5, L_OPI)


def rysuj_belke(vp, placer: Placer, B: KD.BelkaZ, pr: dict, X0: float, Y0: float, podpory=(), tytul: str = "",
                h_txt: float = 2.5) -> tuple:
    """Widok podłużny + przekrój + wyciąg prętów belki w rzutni (układ lokalny: X0, Y0 — spód belki na początku
    osi). Zwraca prostokąt zajęty (x0, y0, x1, y1)."""
    k = vp.k
    L, a, cm, leg = pr["L"], pr["a_op"], pr["cm"], pr["leg"]
    x0, x1 = X0 - a, X0 + B.L + a
    y0, y1 = Y0, Y0 + B.h
    g = box(x0, y0, x1, y1)
    H.hatch(vp, g, "ZELBET")
    vp.geom(g, L_OBR, pen="gruba")
    if B.h_pl > 0:
        vp.line((x0, y1 - B.h_pl), (x1, y1 - B.h_pl), L_OBR, pen="cienka", lt="KRESKOWA")
    # podpory (szkic: mur/słup pod końcami i w punktach pośrednich)
    for s, typ in podpory:
        w_ = 0.18 if typ == "sciana" else 0.12
        gp = box(X0 + s - w_ / 2, y0 - 0.45, X0 + s + w_ / 2, y0)
        if typ == "sciana":
            H.hatch(vp, gp, "MUR_SILIKAT")
        else:
            vp.fill(gp, L_OBR, "#000000")
        vp.geom(gp, L_OBR, pen="srednia")
    # pręty
    fd, fg = B.dol[1] / 1000.0, B.gora[1] / 1000.0
    zd, zg = y0 + cm + fd / 2, y1 - cm - fg / 2
    xa, xb = x0 + cm, x1 - cm
    vp.polyline([(xa, zd + leg), (xa, zd), (xb, zd), (xb, zd + leg)], L_ZBR, pen=0.5)
    vp.polyline([(xa + 0.02, zg - leg), (xa + 0.02, zg), (xb - 0.02, zg), (xb - 0.02, zg - leg)], L_ZBR, pen=0.5)
    ns = pr["ns"]
    st = B.strz[1] / 1000.0
    xs = [x0 + 0.05 + i * st for i in range(ns) if x0 + 0.05 + i * st <= x1 - 0.049]
    c = B.c_nom / 1000.0
    for xx in xs:
        vp.line((xx, y0 + c), (xx, y1 - c), L_ZBR, pen=0.25)
    placer.add(g.buffer(0.02), "area", 0.6)
    # opisy prętów
    from .konstrukcja import etykieta
    etykieta(vp, placer, ((xa + xb) / 2, zd), (1, 0), f"{B.dol[0]} Ø{B.dol[1]} l={pr['dol'].L_mm / 10:g}",
             pr["dol"].nr, h_txt, offs=(B.h * 1000 / vp.scale * 0.5 + 3.0, 8.0), ts=(0.0, -0.3 * L, 0.3 * L))
    etykieta(vp, placer, ((xa + xb) / 2, zg), (1, 0), f"{B.gora[0]} Ø{B.gora[1]} l={pr['gora'].L_mm / 10:g}",
             pr["gora"].nr, h_txt, offs=(3.0, 6.0), ts=(0.2 * L, -0.2 * L, 0.0))
    etykieta(vp, placer, (xs[len(xs) // 2] if xs else (x0 + x1) / 2, (y0 + y1) / 2), (1, 0),
             f"{pr['strz'].n if False else len(xs)} Ø{B.strz[0]} co {B.strz[1] / 10:g} l={pr['strz'].L_mm / 10:g}",
             pr["strz"].nr, h_txt, offs=(0.0,), ts=(0.0, 0.25 * L, -0.25 * L))
    # wymiary
    dims.dim_h(vp, sorted({x0, X0, X0 + B.L, x1}), y0 - 0.45 - 6 * k, None, layer="K-WYMIARY")
    dims.dim_v(vp, [y0, y1], x0 - 6 * k, None, layer="K-WYMIARY")
    # przekrój poprzeczny
    sx = x1 + 0.35 + 12 * k
    gs = box(sx, y0, sx + B.b, y1)
    H.hatch(vp, gs, "ZELBET")
    vp.geom(gs, L_OBR, pen="gruba")
    fs = B.strz[0] / 1000.0
    vp.rect(sx + c + fs / 2, y0 + c + fs / 2, sx + B.b - c - fs / 2, y1 - c - fs / 2, L_ZBR, pen=0.35)
    for n_, fi, zz in ((B.dol[0], fd, zd), (B.gora[0], fg, zg)):
        xx = np.linspace(sx + cm + fi / 2, sx + B.b - cm - fi / 2, max(n_, 2)) if n_ > 1 else [sx + B.b / 2]
        for q in xx:
            vp.fill(Point(q, zz).buffer(max(fi / 2, 0.45 * k), 16), L_ZBR, "#000000")
    dims.dim_h(vp, [sx, sx + B.b], y0 - 6 * k, None, layer="K-WYMIARY")
    vp.text((sx + B.b / 2, y1 + 4 * k), "A-A", 3.5, 0, "center", "baseline", L_OPS, style="bold")
    placer.add(gs.buffer(8 * k), "area", 1.0)
    # tytuł elementu
    ty = y1 + 9 * k
    vp.text((x0, ty), tytul or f"{B.id}", 3.5, 0, "left", "baseline", L_OPS, style="bold")
    placer.add(box(x0, ty - k, x0 + len(tytul or B.id) * 2.4 * k, ty + 4 * k), "text", 1.0)
    # wyciąg prętów (kształty z wymiarami) pod widokiem
    yw = y0 - 0.45 - 18 * k
    xw = x0
    for key in ("dol", "gora", "strz"):
        p = pr[key]
        if p.ksztalt == "21":
            a_, b_, c_ = (v / 1000.0 for v in p.wym)
            vp.polyline([(xw, yw + a_), (xw, yw), (xw + b_, yw), (xw + b_, yw + c_)], L_ZBR, pen=0.5)
            vp.text((xw + b_ / 2, yw - 4 * k), f"{b_ * 100:.0f}", 2.5, 0, "center", "baseline", L_OPI)
            vp.text((xw - 1.2 * k, yw + a_ / 2), f"{a_ * 100:.0f}", 2.5, 90, "center", "bottom", L_OPI)
            _nr(vp, (xw + b_ / 2 - 12 * k, yw + 4 * k), p.nr)
            vp.text((xw + b_ / 2 - 8 * k, yw + 4 * k), f"Ø{p.fi} l={p.L_mm / 10:g}", 2.5, 0, "left", "middle", L_OPI)
            yw -= max(a_, 0.1) + 12 * k
        elif p.ksztalt == "51":
            a_, b_ = (v / 1000.0 for v in p.wym)
            vp.rect(xw, yw - b_, xw + a_, yw, L_ZBR, pen=0.5)
            vp.text((xw + a_ / 2, yw - b_ - 4 * k), f"{a_ * 100:.0f}", 2.5, 0, "center", "baseline", L_OPI)
            vp.text((xw + a_ + 1.2 * k, yw - b_ / 2), f"{b_ * 100:.0f}", 2.5, 90, "center", "top", L_OPI)
            _nr(vp, (xw + a_ + 10 * k, yw - b_ / 2), p.nr)
            vp.text((xw + a_ + 14 * k, yw - b_ / 2), f"Ø{p.fi} l={p.L_mm / 10:g}", 2.5, 0, "left", "middle", L_OPI)
            yw -= b_ + 10 * k
    return (x0 - 12 * k, yw, sx + B.b + 20 * k, ty + 6 * k)


def podpory_belki(m, B: KD.BelkaZ) -> list:
    """Podpory belki z modelu: ściany nośne i słupy pod osią (s — odległość od początku osi) [(s, typ)]."""
    ln = LineString([B.p0, B.p1])
    out = []
    if B.rodzaj == "nadproze":
        return [(B.oparcie / 2, "sciana"), (B.L - B.oparcie / 2, "sciana")]
    for w in m.sciany():
        if w.typ not in ("sciana_zewn", "sciana_wewn_nosna") or abs(w.z_do - B.spod) > 0.1:
            continue
        X = w.axis_line().intersection(ln.buffer(0.01))
        if X.is_empty:
            continue
        for p in (Point(*B.p0), Point(*B.p1)):
            if w.axis_line().distance(p) < 0.15:
                out.append((ln.project(p), "sciana"))
        if abs(float(w.u @ (np.subtract(B.p1, B.p0) / max(B.L, 1e-9)))) < 0.1:
            c = w.axis_line().intersection(ln)
            if not c.is_empty and c.geom_type == "Point":
                out.append((ln.project(c), "sciana"))
    for c in m.slupy():
        if abs(float(c["z_do"]) - B.spod) < 0.1 and ln.distance(Point(*c["xy"])) < 0.15:
            out.append((ln.project(Point(*c["xy"])), "slup"))
    uniq = {}
    for s, t in out:
        uniq[round(s, 2)] = (s, t)
    return sorted(uniq.values())


def kontrola_belki(D, B: KD.BelkaZ, pr: dict, arkusz: str):
    from ..obliczenia.konstrukcja.materialy import pole_preta
    As_d = B.dol[0] * pole_preta(B.dol[1])
    As_g = B.gora[0] * pole_preta(B.gora[1])
    smin = max(B.dol[1], 16 + 5, 20)
    miesci = B.dol[0] * B.dol[1] + (B.dol[0] - 1) * smin <= B.b * 1000 - 2 * pr["cm"] * 1000 + 1e-6
    uw = "; ".join(B.niesp[:2])
    if not miesci:
        uw = (uw + "; " if uw else "") + (f"{B.dol[0]}Ø{B.dol[1]} nie mieści się w jednej warstwie przy b = "
                                          f"{B.b * 100:.0f} cm (odstęp w świetle ≥ {smin} mm — 8.2(2))")
    KD.rejestruj(D, B.id, "dołem (przęsło)", B.poz, B.As_dol[0], B.As_dol[1], As_d, f"{B.dol[0]}Ø{B.dol[1]}", jedn="mm²",
                 As_max=0.04 * B.b * B.h * 1e6, arkusz=arkusz, uwagi=uw, wymuszone_ok=miesci and not B.niesp)
    KD.rejestruj(D, B.id, "górą (podpory; ≥ 0,15·A_s,dół — 9.2.1.2(1))", B.poz, max(B.As_gora[0], 0.15 * As_d), 0.0,
                 As_g, f"{B.gora[0]}Ø{B.gora[1]}", jedn="mm²", arkusz=arkusz)
