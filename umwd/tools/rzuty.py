#!/usr/bin/env python
"""Rzuty wszystkich kondygnacji 1:200 (SVG + PNG podglądowe) z modelu pomieszczeń model/budynek.json.

Styl konkursowy: białe tło, monochromia, jeden akcent terakotowy #a8483a (strefy publiczne i Sejmik), poché ścian #1f1d1a,
meble szarością, napisy Inter ≥ 1,6 mm na papierze. Osie konstrukcyjne (wieża 1–6 / A–D, skrzydło a–o), łańcuchy wymiarowe,
rzędne, przekroje A-A (u = 29,4, widok na zach.) i B-B (v = 19,6, widok na pn.), strzałka północy, podziałka, legenda
pomieszczeń obok rzutu (nr – nazwa – m²), numer i powierzchnia każdego pomieszczenia na rzucie.
Parter z otoczeniem (nawierzchnie z opisem materiału, mała architektura, latarnie, drzewa istniejące i nowe, skwer 9/2 ze
śladem pierzei 1934 r., ogród). Rzut dachu: BIPV, taras zielony, attyki, spadki, wpusty.

Wyniki: build/rzuty/rzut_<kond>_1-200.svg (+ .html, .png) oraz docs/70_rysunki/podglady/rzut_<kond>_1-200.png (≤ 1,5 MB).
Uruchom: /home/user/aihouse/.venv-render/bin/python -I tools/rzuty.py [kondygnacje…]
"""
from __future__ import annotations
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

from umwd.svg import (Svg, model_rings, north_arrow, scale_bar, FONT, esc, dim_chain, axis_bubble, level_mark, arrow,  # noqa: E402
                      icon_wheelchair, icon_loop, icon_moe, icon_tyflo, halo_extra)
from umwd.frames import Frame  # noqa: E402

BUD = json.loads((ROOT / "model" / "budynek.json").read_text(encoding="utf-8"))
SPEC = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
SITE = json.loads((ROOT / "model" / "site.json").read_text(encoding="utf-8"))
OUT = ROOT / "build" / "rzuty"
PREV = ROOT / "docs" / "70_rysunki" / "podglady"
SC = 200.0
K = 1000.0 / SC            # mm papieru na metr

INK = "#1f1d1a"
GREY = "#4a4641"
HAIR = "#a9a39b"
ACC = "#a8483a"
ACC_F = "#f3e4dd"          # tło stref publicznych (akcent rozjaśniony)
F_OFF = "#f6f4f0"
F_SN = "#efece6"
F_PHS = "#ebedee"
F_TECH = "#e7e5e1"
F_CORE = "#ffffff"
F_GAR = "#f8f7f4"
PUBLIC = {"SW", "SK", "SWD"}

T = Frame(tuple(BUD["uklady"]["T"]["o"]), tuple(BUD["uklady"]["T"]["ex"]), tuple(BUD["uklady"]["T"]["ey"]))
WF = Frame(tuple(BUD["uklady"]["W"]["o"]), tuple(BUD["uklady"]["W"]["ex"]), tuple(BUD["uklady"]["W"]["ey"]))
SIATKA = BUD["siatka"]
LV = {k["id"]: k for k in BUD["kondygnacje"]}
KOND = {k["kondygnacja"]: k for k in SPEC["kondygnacje"]}
Z0 = SPEC["meta"]["zero"]["wzgl_0_00_m_npm"]

# przekroje (od koordynatora): A-A wzdłuż u = 29,4 (v −40…46), widok na zach.; B-B wzdłuż v = 19,6 (u −24…52), widok na pn.
SECTIONS = [dict(id="A", a=(29.4, -40.0), b=(29.4, 46.0), view=(-1.0, 0.0)),
            dict(id="B", a=(-24.0, 19.6), b=(52.0, 19.6), view=(0.0, 1.0))]

TITLES = {"-2": "KONDYGNACJA −2 · GARAŻ, UKRYCIE, TECHNIKA", "-1": "KONDYGNACJA −1 · GARAŻ (MDS), DOSTAWY, TECHNIKA",
          "P": "PARTER · HALA OBYWATELSKA, CENTRUM KONFERENCYJNE · Z OTOCZENIEM", "1": "KONDYGNACJA 1", "2": "KONDYGNACJA 2",
          "3": "KONDYGNACJA 3", "4": "KONDYGNACJA 4", "5": "KONDYGNACJA 5 · WYJŚCIE NA TARAS NAD OŁAWĄ", "6": "KONDYGNACJA 6 · KANCELARIA SEJMIKU",
          "S": "KONDYGNACJA SEJMIKU (S)", "ANT": "ANTRESOLA KONDYGNACJI SEJMIKU", "D": "RZUT DACHU"}
FILE_ID = {"-2": "m2", "-1": "m1", "P": "P", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "S": "S", "ANT": "S_antresola", "D": "dach"}
DEPT_NAMES = {}
for b in __import__("yaml").safe_load((ROOT / "docs" / "20_program" / "program.yaml").read_text(encoding="utf-8"))["bloki"]:
    DEPT_NAMES[b["kod"]] = b["nazwa"]


CFG = {"tight": False, "bounds": None, "s1": 1.75, "s2": 1.6}


def in_bounds(bx):
    b = CFG.get("bounds")
    if not b:
        return True
    return bx[0] >= b[0] and bx[1] >= b[1] and bx[2] <= b[2] and bx[3] <= b[3]


def fnum(x, nd=1):
    return f"{x:.{nd}f}".replace(".", ",")


def fz(z):
    if z is None:
        return ""
    if abs(z) < 0.005:
        return "±0,00"
    return ("+" if z > 0 else "−") + fnum(abs(z), 2)


def mp(rings_list):
    out = []
    for poly in rings_list or []:
        if poly and len(poly[0]) >= 3:
            try:
                out.append(Polygon(poly[0], poly[1:]).buffer(0))
            except Exception:
                pass
    return unary_union(out) if out else Polygon()


def polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    return [p for p in getattr(g, "geoms", []) if isinstance(p, Polygon) and not p.is_empty]


# ----------------------------------------------------------------------------------------------------------------
class UVView:
    """Rzut zorientowany wg osi wieży: u w prawo, v w górę (północ obrócona – strzałka)."""

    def __init__(self, u0, u1, v0, v1, ox, oy):
        self.u0, self.u1, self.v0, self.v1 = u0, u1, v0, v1
        self.ox, self.oy = ox, oy

    @property
    def w_mm(self):
        return (self.u1 - self.u0) * K

    @property
    def h_mm(self):
        return (self.v1 - self.v0) * K

    def pu(self, u, v):
        return (self.ox + (u - self.u0) * K, self.oy + (self.v1 - v) * K)

    def p(self, e, n):
        u, v = T.loc(e, n)
        return self.pu(u, v)

    def mm(self, m):
        return m * K

    def dir(self, vec_en):
        """Wektor en → kierunek na papierze (jednostkowy)."""
        du = vec_en[0] * T.ex[0] + vec_en[1] * T.ex[1]
        dv = vec_en[0] * T.ey[0] + vec_en[1] * T.ey[1]
        L = math.hypot(du, dv) or 1
        return (du / L, -dv / L)


def north_rot():
    """Kąt obrotu strzałki północy na rzucie (stopnie, zgodnie z ruchem wskazówek na papierze)."""
    # kierunek n (0,1) w układzie papieru
    du, dv = T.ex[1], T.ey[1]
    return math.degrees(math.atan2(du, dv))


# ----------------------------------------------------------------------------------------------------------------
class Labels:
    """Prosty rozmieszczacz etykiet z unikaniem kolizji (prostokąty na papierze)."""

    def __init__(self):
        self.boxes = []

    @staticmethod
    def tw(s, size, bold=False):
        return len(s) * size * (0.60 if bold else 0.55)

    def free(self, bx):
        x0, y0, x1, y1 = bx
        for (a0, b0, a1, b1) in self.boxes:
            if x0 < a1 and x1 > a0 and y0 < b1 and y1 > b0:
                return False
        return True

    def add(self, bx):
        self.boxes.append(bx)


def poly_paper(v: UVView, g):
    if isinstance(g, Polygon):
        return Polygon([v.p(*c) for c in g.exterior.coords], [[v.p(*c) for c in r.coords] for r in g.interiors])
    return unary_union([poly_paper(v, p) for p in polys(g)])


# ----------------------------------------------------------------------------------------------------------------
def room_fill(r):
    k, kind = r["kod_grupy"], r["kind"]
    if kind in ("corridor",):
        return "#ffffff"
    if kind in ("core_stair", "core_lift", "core_lobby"):
        return F_CORE
    if kind == "shaft":
        return "#d9d6d1"
    if kind in ("garage",):
        return F_GAR
    if kind == "ramp":
        return "#efede9"
    if k in PUBLIC or "public" in r.get("tags", []) or "sejmik" in r.get("tags", []):
        return ACC_F
    if k == "KS":
        return "#f6ece7"
    if k == "SN":
        return F_SN
    if k == "PHS":
        return F_PHS
    if k in ("IT", "PPT", "PPM"):
        return F_TECH
    if k in ("PP", "PS", "PR"):
        return "#f1efea"
    return F_OFF


def draw_furniture(svg, v, r, g):
    f = r.get("furn")
    if not f or g.is_empty:
        return
    st = dict(stroke=HAIR, sw=0.09)
    mrr = g.minimum_rotated_rectangle
    cs = list(mrr.exterior.coords)[:4]
    e1 = (cs[1][0] - cs[0][0], cs[1][1] - cs[0][1])
    e2 = (cs[2][0] - cs[1][0], cs[2][1] - cs[1][1])
    L1, L2 = math.hypot(*e1), math.hypot(*e2)
    cx, cy = g.centroid.x, g.centroid.y
    fd = r.get("facade_dir")
    if L1 < 0.5 or L2 < 0.5:
        return
    # oś a – długa, b – krótka
    if L1 >= L2:
        a, La, b, Lb = (e1[0] / L1, e1[1] / L1), L1, (e2[0] / L2, e2[1] / L2), L2
    else:
        a, La, b, Lb = (e2[0] / L2, e2[1] / L2), L2, (e1[0] / L1, e1[1] / L1), L1

    def P_(s, t):
        return v.p(cx + a[0] * s + b[0] * t, cy + a[1] * s + b[1] * t)

    def rect(s0, s1, t0, t1, **kw):
        svg.poly([P_(s0, t0), P_(s1, t0), P_(s1, t1), P_(s0, t1)], fill="none", **(kw or st))
    if f in ("office3", "office4", "office1"):
        n = {"office3": 3, "office4": 4, "office1": 1}[f]
        # biurka przy oknie: oś a = głębokość (prostopadle do elewacji), jeśli facade_dir podany
        if fd:
            dot_a = fd[0] * a[0] + fd[1] * a[1]
            dot_b = fd[0] * b[0] + fd[1] * b[1]
            if abs(dot_b) > abs(dot_a):        # elewacja wzdłuż a – zamiana osi
                a, b, La, Lb = b, a, Lb, La
                dot_a = dot_b
            sgn = 1 if dot_a > 0 else -1
        else:
            sgn = 1
        s_win = sgn * (La / 2 - 0.55)
        dw, dd = 1.6, 0.8
        if n == 1:
            rect(s_win - sgn * dd, s_win, -0.8, 0.8)
            svg.circle(P_(s_win - sgn * (dd + 0.45), 0), v.mm(0.25), fill="none", stroke=HAIR, sw=0.08)
            # stolik spotkań
            svg.circle(P_(-sgn * (La / 2 - 1.5), 0), v.mm(0.55), fill="none", stroke=HAIR, sw=0.08)
            return
        if n * dw <= Lb - 0.2:
            gap = (Lb - n * dw) / (n + 1)
            for i in range(n):
                t0 = -Lb / 2 + gap + i * (dw + gap)
                rect(s_win - sgn * dd, s_win, t0, t0 + dw)
                svg.circle(P_(s_win - sgn * (dd + 0.45), t0 + dw / 2), v.mm(0.24), fill="none", stroke=HAIR, sw=0.08)
        else:
            for i in range(n):
                row, col = divmod(i, 2)
                t0 = -Lb / 2 + 0.15 + col * (Lb / 2 - 0.1)
                s0 = s_win - sgn * (row * 2.3)
                rect(s0 - sgn * dd, s0, t0, t0 + min(1.5, Lb / 2 - 0.3))
    elif f == "table":
        seats = max(6, r.get("seats") or 10)
        per = math.ceil(seats / 2)
        tl = min(La - 2.2, per * 0.75)
        tw_ = min(1.4, Lb - 2.4)
        if tl > 1 and tw_ > 0.6:
            rect(-tl / 2, tl / 2, -tw_ / 2, tw_ / 2)
            for i in range(per):
                s = -tl / 2 + (i + 0.5) * tl / per
                for t in (-tw_ / 2 - 0.38, tw_ / 2 + 0.38):
                    svg.circle(P_(s, t), v.mm(0.21), fill="none", stroke=HAIR, sw=0.08)
    elif f == "kitchen":
        rect(-La / 2 + 0.05, La / 2 - 0.05, -Lb / 2 + 0.05, -Lb / 2 + 0.65)
        svg.circle(P_(0, Lb / 4), v.mm(0.6), fill="none", stroke=HAIR, sw=0.08)
    elif f == "shelves":
        for t in (-Lb / 2 + 0.05, Lb / 2 - 0.45):
            rect(-La / 2 + 0.2, La / 2 - 0.2, t, t + 0.4)
    elif f == "wc":
        # rząd kabin wzdłuż dłuższej ściany + umywalki
        n = max(1, int((La - 0.4) / 1.0))
        for i in range(min(n, 6)):
            s0 = -La / 2 + 0.2 + i * 1.0
            svg.poly([P_(s0 + 0.3, -Lb / 2 + 0.1), P_(s0 + 0.7, -Lb / 2 + 0.1), P_(s0 + 0.7, -Lb / 2 + 0.7), P_(s0 + 0.3, -Lb / 2 + 0.7)],
                     fill="none", stroke=HAIR, sw=0.08)
    elif f in ("chairs", "gallery"):
        step = 0.9 if f == "chairs" else 0.8
        s = -La / 2 + 1.2
        while s < La / 2 - 1.0:
            t = -Lb / 2 + 1.0
            while t < Lb / 2 - 0.8:
                svg.poly([P_(s - 0.22, t - 0.22), P_(s + 0.22, t - 0.22), P_(s + 0.22, t + 0.22), P_(s - 0.22, t + 0.22)], fill="none", stroke=HAIR, sw=0.07)
                t += 0.6
            s += step
    elif f == "cafe":
        s = -La / 2 + 1.5
        while s < La / 2 - 1.0:
            t = -Lb / 2 + 1.5
            while t < Lb / 2 - 1.0:
                svg.circle(P_(s, t), v.mm(0.4), fill="none", stroke=HAIR, sw=0.08)
                t += 2.2
            s += 2.2
    elif f == "bikes":
        s = -La / 2 + 0.6
        while s < La / 2 - 0.4:
            svg.line(P_(s, -Lb / 2 + 0.3), P_(s, -Lb / 2 + 2.1), stroke=HAIR, sw=0.08)
            svg.line(P_(s, Lb / 2 - 2.1), P_(s, Lb / 2 - 0.3), stroke=HAIR, sw=0.08)
            s += 0.7
    elif f == "counter":
        rect(-La / 2 + 0.6, La / 2 - 0.6, Lb / 2 - 1.2, Lb / 2 - 0.6)


def draw_sejmik_seats(svg, v):
    sala = SPEC["kondygnacja_sejmiku"]["sala"]
    fu, fv = sala["ognisko_rzedow_uv"]
    for rz in sala["rzedy"]:
        R = rz["R"]
        n = rz["miejsc"]
        a0, a1 = 25.0, 155.0
        pts = [v.pu(fu + R * math.cos(math.radians(a)), fv + R * math.sin(math.radians(a))) for a in [a0 + (a1 - a0) * i / 30 for i in range(31)]]
        svg.poly(pts, fill="none", stroke=HAIR, sw=0.25, close=False)
        for i in range(n):
            a = math.radians(a0 + 4 + (a1 - a0 - 8) * (i + 0.5) / n)
            c = v.pu(fu + (R + 0.5) * math.cos(a), fv + (R + 0.5) * math.sin(a))
            svg.circle(c, v.mm(0.24), fill="none", stroke=HAIR, sw=0.08)
    # prezydium i mównica przy ścianie pd.
    svg.poly([v.pu(fu - 2.6, fv - 3.4), v.pu(fu + 2.6, fv - 3.4), v.pu(fu + 2.6, fv - 2.6), v.pu(fu - 2.6, fv - 2.6)], fill="none", stroke=HAIR, sw=0.12)
    svg.text(v.pu(fu, fv - 3.95), "prezydium · mównica", size=1.6, anchor="middle", fill=GREY)


# ----------------------------------------------------------------------------------------------------------------
def draw_stair(svg, v, g):
    mrr = g.minimum_rotated_rectangle
    cs = list(mrr.exterior.coords)[:4]
    e1 = (cs[1][0] - cs[0][0], cs[1][1] - cs[0][1])
    e2 = (cs[3][0] - cs[0][0], cs[3][1] - cs[0][1])
    L1, L2 = math.hypot(*e1), math.hypot(*e2)
    o = cs[0]
    if L1 < L2:
        e1, e2, L1, L2 = e2, e1, L2, L1
    a = (e1[0] / L1, e1[1] / L1)
    b = (e2[0] / L2, e2[1] / L2)

    def P_(s, t):
        return v.p(o[0] + a[0] * s + b[0] * t, o[1] + a[1] * s + b[1] * t)
    land = min(1.5, L1 * 0.22)
    s = land
    while s < L1 - land + 1e-6:
        svg.line(P_(s, 0.05), P_(s, L2 - 0.05), stroke=INK, sw=0.07)
        s += 0.30
    svg.line(P_(land, L2 / 2), P_(L1 - land, L2 / 2), stroke=INK, sw=0.12)
    arrow(svg, P_(L1 - land, L2 * 0.25), P_(land + 0.4, L2 * 0.25), sw=0.1, head=1.0)


def draw_lift(svg, v, g, tag=""):
    cs = list(g.minimum_rotated_rectangle.exterior.coords)[:4]
    svg.line(v.p(*cs[0]), v.p(*cs[2]), stroke=INK, sw=0.08)
    svg.line(v.p(*cs[1]), v.p(*cs[3]), stroke=INK, sw=0.08)
    if tag:
        c = v.p(g.centroid.x, g.centroid.y)
        dy = -2.4 if CFG["tight"] else 0.6
        svg.text((c[0], c[1] + dy), tag, size=1.9 if CFG["tight"] else 1.7, anchor="middle", weight=700, fill=INK, extra=halo_extra(0.5))


def draw_door(svg, v, d):
    p0, p1, n, w = d["p0"], d["p1"], d["n"], d["w"]
    # wycięcie w ścianie (od strony przeciwnej do n)
    t = 0.30
    q0 = (p0[0] - n[0] * t, p0[1] - n[1] * t)
    q1 = (p1[0] - n[0] * t, p1[1] - n[1] * t)
    svg.poly([v.p(*p0), v.p(*p1), v.p(*q1), v.p(*q0)], fill="#ffffff", stroke="none")
    svg.line(v.p(*p0), v.p(*q0), stroke=INK, sw=0.12)
    svg.line(v.p(*p1), v.p(*q1), stroke=INK, sw=0.12)
    # skrzydło (zawias w p0) i łuk
    leaf = (p0[0] + n[0] * w, p0[1] + n[1] * w)
    svg.line(v.p(*p0), v.p(*leaf), stroke=GREY, sw=0.13)
    r = v.mm(w)
    a, b = v.p(*leaf), v.p(*p1)
    # kierunek łuku: sprawdź znak iloczynu
    cr = (a[0] - v.p(*p0)[0]) * (b[1] - v.p(*p0)[1]) - (a[1] - v.p(*p0)[1]) * (b[0] - v.p(*p0)[0])
    sweep = 1 if cr > 0 else 0
    svg.add(f'<path d="M{a[0]:.3f},{a[1]:.3f} A{r:.3f},{r:.3f} 0 0 {sweep} {b[0]:.3f},{b[1]:.3f}" fill="none" stroke="{HAIR}" stroke-width="0.08" stroke-dasharray="0.5,0.35"/>')


def draw_window(svg, v, w):
    if "pts" in w:
        pts = w["pts"]
        cc = BUD["luk"]["srodek_uv"]
        t = w.get("t", 0.5)
        def off(p, d):
            u, vv = T.loc(*p)
            du, dv = u - cc[0], vv - cc[1]
            L = math.hypot(du, dv)
            return v.pu(cc[0] + du * (L - d) / L, cc[1] + dv * (L - d) / L)
        mid = [off(p, t / 2) for p in pts]
        svg.poly(mid, fill="none", stroke="#ffffff", sw=v.mm(t) * 0.92, close=False)
        for d in (t * 0.35, t * 0.65):
            svg.poly([off(p, d) for p in pts], fill="none", stroke=INK, sw=0.07, close=False)
        return
    a, b, n, t = w["a"], w["b"], w["n"], w.get("t", 0.5)
    q = [a, b, (b[0] + n[0] * t, b[1] + n[1] * t), (a[0] + n[0] * t, a[1] + n[1] * t)]
    svg.poly([v.p(*p) for p in q], fill="#ffffff", stroke="none")
    for f in (0.35, 0.65):
        svg.line(v.p(a[0] + n[0] * t * f, a[1] + n[1] * t * f), v.p(b[0] + n[0] * t * f, b[1] + n[1] * t * f), stroke=INK, sw=0.07)
    svg.line(v.p(*a), v.p(*q[3]), stroke=INK, sw=0.12)
    svg.line(v.p(*b), v.p(*q[2]), stroke=INK, sw=0.12)


# ----------------------------------------------------------------------------------------------------------------
def draw_axes(svg, v, lid, bbox_uv, wing=True):
    u_axes = SIATKA["wieza"]["osie_u"]
    v_axes = SIATKA["wieza"]["osie_v"]
    u0, v0, u1, v1 = bbox_uv
    dash = 'stroke-dasharray="4,0.8,0.6,0.8"'
    labels_u = [str(i + 1) for i in range(len(u_axes))]
    labels_v = [chr(ord("A") + i) for i in range(len(v_axes))]
    top, bot = v1 + 5.5, v0 - 5.5
    left, right = u0 - 5.5, u1 + 5.5
    for u, lab in zip(u_axes, labels_u):
        svg.line(v.pu(u, bot + 1.6), v.pu(u, top - 1.6), stroke=GREY, sw=0.1, extra=dash)
        axis_bubble(svg, v.pu(u, top), lab, r=2.6, size=2.4)
        axis_bubble(svg, v.pu(u, bot), lab, r=2.6, size=2.4)
    for vv, lab in zip(v_axes, labels_v):
        svg.line(v.pu(left + 1.6, vv), v.pu(right - 1.6, vv), stroke=GREY, sw=0.1, extra=dash)
        axis_bubble(svg, v.pu(left, vv), lab, r=2.6, size=2.4)
        axis_bubble(svg, v.pu(right, vv), lab, r=2.6, size=2.4)
    if wing and lid in ("P", "1", "2", "3", "4", "-1"):
        step = SPEC["siatka"]["skrzydlo"].get("modul_m", 1.35) * 3
        n = int(57.0 / step) + 1
        for i in range(n):
            s = i * step
            a = WF.en(s, -4.0)
            b = WF.en(s, 15.6)
            svg.line(v.p(*a), v.p(*b), stroke=GREY, sw=0.08, extra=dash)
            axis_bubble(svg, v.p(*WF.en(s, -6.6)), chr(ord("a") + i), r=2.2, size=2.0)


def draw_dims(svg, v, lid):
    u_axes = SIATKA["wieza"]["osie_u"]
    v_axes = SIATKA["wieza"]["osie_v"]
    U, V = u_axes[-1], v_axes[-1]
    lab = lambda a, b: fnum(b - a, 2)
    # pn. (nad wieżą)
    y1, y2 = V + 9.5, V + 12.0
    t_u = [(x - u_axes[0]) / (U - u_axes[0]) for x in u_axes]
    dim_chain(svg, v.pu(u_axes[0], y1), v.pu(U, y1), t_u, (0, -1), [lab(a, b) for a, b in zip(u_axes[:-1], u_axes[1:])], size=1.8)
    dim_chain(svg, v.pu(u_axes[0], y2), v.pu(U, y2), [0, 1], (0, -1), [fnum(U - u_axes[0], 2)], size=1.9)
    # wsch.
    x1, x2 = U + 9.5, U + 12.0
    vmin = v_axes[0]
    pts = list(v_axes)
    if lid in ("P", "1", "2", "3", "4", "-1", "-2", "5", "D"):
        seg = [T.loc(*p) for p in SPEC["bryly"][2]["obrys_ccw"]]
        vs = min(vv for u, vv in seg if u > U - 0.1)
        pts = [vs] + pts
    t_v = [(x - pts[0]) / (pts[-1] - pts[0]) for x in pts]
    dim_chain(svg, v.pu(x1, pts[0]), v.pu(x1, pts[-1]), t_v, (1, 0), [lab(a, b) for a, b in zip(pts[:-1], pts[1:])], size=1.8)
    dim_chain(svg, v.pu(x2, pts[0]), v.pu(x2, pts[-1]), [0, 1], (1, 0), [fnum(pts[-1] - pts[0], 2)], size=1.9)
    # skrzydło – posesje wzdłuż ulicy
    if lid in ("P", "1", "2", "3", "4", "-1", "D"):
        seg = SPEC["elewacje"]["skrzydlo"]["segmenty_m"]
        ss = [0.0]
        for kk in ("M1", "M2", "M3", "M4"):
            ss.append(ss[-1] + seg[kk])
        street_len = WF.loc(*SPEC["bryly"][1]["obrys_ccw"][-5])[0] if False else 57.72
        ss.append(street_len)
        d1, d2 = -9.0, -11.5
        a, b = v.p(*WF.en(0, d1)), v.p(*WF.en(ss[-1], d1))
        o = v.dir((-WF.ey[0], -WF.ey[1]))
        dim_chain(svg, a, b, [x / ss[-1] for x in ss], o, ["M1 " + fnum(seg["M1"], 2), "M2 " + fnum(seg["M2"], 2), "M3 " + fnum(seg["M3"], 2),
                                                          "M4 " + fnum(seg["M4"], 2), fnum(ss[-1] - ss[-2], 2)], size=1.7)
        a, b = v.p(*WF.en(0, d2)), v.p(*WF.en(ss[-1], d2))
        dim_chain(svg, a, b, [0, 1], o, [fnum(ss[-1], 2)], size=1.9)
        # szerokość traktu skrzydła
        a, b = v.p(*WF.en(-3.0, 0)), v.p(*WF.en(-3.0, 15.0))
        dim_chain(svg, a, b, [0, 1], v.dir((-WF.ex[0], -WF.ex[1])), [fnum(15.0, 2)], size=1.8)


def draw_sections(svg, v, lab: Labels):
    for s in SECTIONS:
        a, b = v.pu(*s["a"]), v.pu(*s["b"])
        svg.line(a, b, stroke=INK, sw=0.18, extra='stroke-dasharray="6,1.2,1,1.2"')
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        vw = (s["view"][0], -s["view"][1])
        for p, sg in ((a, 1), (b, -1)):
            q = (p[0] + ux * sg * 7.0, p[1] + uy * sg * 7.0)
            svg.line(p, q, stroke=INK, sw=0.7)
            arrow(svg, (q[0], q[1]), (q[0] + vw[0] * 5.0, q[1] + vw[1] * 5.0), sw=0.35, head=1.8)
            tp = (q[0] + vw[0] * 7.5, q[1] + vw[1] * 7.5 + 1.4)
            svg.text(tp, s["id"], size=4.0, weight=700, anchor="middle", fill=INK, extra=halo_extra(0.8))


def level_title(lid):
    if lid == "ANT":
        z = SPEC["kondygnacja_sejmiku"]["antresola"]["wzgl"]
    elif lid == "D":
        return TITLES["D"], "attyka wieży " + fz(SPEC["bryly"][0]["dach"]["attyka"]["wzgl"]) + f" ({fnum(SPEC['bryly'][0]['dach']['attyka']['npm'], 2)} m n.p.m.)"
    else:
        z = KOND[lid]["posadzka_wzgl"]
    return TITLES.get(lid, lid), f"posadzka {fz(z)} = {fnum(Z0 + z, 2)} m n.p.m."


# ----------------------------------------------------------------------------------------------------------------
def natural(n):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", n or "")]


def legend_rows(rooms):
    only_roof = all(r["kind"] == "roof" for r in rooms)
    rs = [r for r in rooms if (only_roof or r["kind"] not in ("roof",)) and r["numer"]]
    rs.sort(key=lambda r: natural(r["numer"]))
    rows = []
    for r in rs:
        nm = r["nazwa"]
        if rows and rows[-1]["nazwa"] == nm and rows[-1]["kod"] == r["kod_grupy"] and r["kind"] not in ("corridor",):
            rows[-1]["nums"].append(r["numer"])
            rows[-1]["areas"].append(r["powierzchnia"])
        else:
            rows.append(dict(nazwa=nm, kod=r["kod_grupy"], nums=[r["numer"]], areas=[r["powierzchnia"]]))
    out = []
    for row in rows:
        n = row["nums"]
        num = n[0] if len(n) == 1 else f"{n[0]}–{n[-1].split('.')[-1]}" if n[0].rsplit(".", 1)[0] == n[-1].rsplit(".", 1)[0] else f"{n[0]}…{n[-1]}"
        if len(n) == 1:
            ar = fnum(row["areas"][0])
        else:
            ar = f"{len(n)} × " + (fnum(row["areas"][0]) if max(row["areas"]) - min(row["areas"]) < 0.15 else fnum(sum(row["areas"]) / len(n))) + f" = {fnum(sum(row['areas']))}"
        out.append((num, row["nazwa"], ar, row["kod"]))
    return out


def wrap(s, n):
    words = s.split()
    lines, cur = [], ""
    for w_ in words:
        if len(cur) + len(w_) + 1 > n and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    if cur:
        lines.append(cur)
    return lines


def draw_legend(svg, x0, y0, wcol, lv, extra_blocks=()):
    rows = legend_rows(lv["pomieszczenia"])
    y = y0
    svg.text((x0, y), "LEGENDA POMIESZCZEŃ", size=2.8, weight=700, fill=INK, ls=0.15)
    y += 2.2
    svg.text((x0, y + 1.6), "nr  ·  nazwa (komórka wg tabeli 1 M.01)  ·  pow. netto m² (PN-ISO 9836)", size=1.6, fill=GREY)
    y += 4.2
    sz = 1.7
    lh = 2.45
    col_w = wcol
    cols = 2 if len(rows) > 46 else 1
    cw = col_w / cols
    nchar = int((cw - 34) / (sz * 0.52))
    per_col = math.ceil(sum(len(wrap(r[1], nchar)) for r in rows) / cols) + 1
    cx, cy, cnt = x0, y, 0
    ymax = y
    for num, nm, ar, kod in rows:
        lines = wrap(nm, nchar)
        if cnt + len(lines) > per_col and cols > 1 and cx == x0:
            cx, cy, cnt = x0 + cw, y, 0
        col = ACC if kod in PUBLIC else INK
        svg.text((cx, cy + sz), num, size=sz, weight=600, fill=col)
        for i, ln in enumerate(lines):
            svg.text((cx + 15.5, cy + sz + i * lh), ln, size=sz, fill=INK)
        svg.text((cx + cw - 2.0, cy + sz), ar, size=sz, anchor="end", fill=GREY)
        cy += lh * len(lines) + 0.25
        cnt += len(lines)
        ymax = max(ymax, cy)
    y = ymax + 3.0
    # bilans kondygnacji wg kodów
    sums = {}
    only_roof = all(r["kind"] == "roof" for r in lv["pomieszczenia"])
    for r in lv["pomieszczenia"]:
        if r["kind"] in ("roof",) and not only_roof:
            continue
        sums[r["kod_grupy"]] = sums.get(r["kod_grupy"], 0) + r["powierzchnia"]
    svg.text((x0, y + 2.0), "BILANS KONDYGNACJI (pow. netto wg kodów grup)", size=2.2, weight=700, fill=INK)
    y += 4.5
    items = sorted(sums.items(), key=lambda kv: -kv[1])
    ncol = 4
    for i, (k, a) in enumerate(items):
        c, rr = i % ncol, i // ncol
        svg.text((x0 + c * (col_w / ncol), y + rr * 2.6 + 1.7), f"{k}  {fnum(a)}", size=1.7, fill=ACC if k in PUBLIC else INK)
    y += (len(items) + ncol - 1) // ncol * 2.6 + 1.0
    tot = sum(sums.values())
    svg.text((x0, y + 2.0), (f"Razem pola dachowe w obrysie attyk: {fnum(tot)} m²" if only_roof else f"Razem powierzchnia netto kondygnacji: {fnum(tot)} m²"),
             size=1.9, weight=600, fill=INK)
    y += 5.0
    for blk in extra_blocks:
        y = blk(svg, x0, y, col_w)
    return y


def symbols_block(lid):
    def f(svg, x0, y, w):
        svg.text((x0, y + 2.0), "OZNACZENIA", size=2.2, weight=700, fill=INK)
        y += 4.6
        items = []
        items.append(("wc", "WC z kabiną / toaletą dostępną dla OzN" + (", komfortka" if lid == "P" else "")))
        items.append(("moe", "miejsce oczekiwania na ewakuację (MOE) w przedsionku ppoż.: krzesło ewakuacyjne, interkom EVCS"))
        items.append(("loop", "pętla indukcyjna"))
        if lid == "P":
            items.append(("tyflo", "tyflomapa przy wejściu"))
            items.append(("fon", "ścieżka dotykowa (FON) od wejść i przystanków do informacji, kancelarii i dźwigów"))
            items.append(("ent", "wejście (wszystkie w poziomie chodnika, bez stopni i pochylni)"))
        if lid in ("-1", "-2"):
            items.append(("ozn", "stanowisko dla OzN 3,6 × 5,0 m (z pasem manewrowym)"))
        items.append(("lvl", "rzędna posadzki (wzgl. ±0,00 = " + fnum(Z0, 2) + " m n.p.m.)"))
        items.append(("sec", "przekrój A-A / B-B (kierunek widoku)"))
        for kind, txt in items:
            c = (x0 + 1.6, y + 0.4)
            if kind == "wc":
                icon_wheelchair(svg, c, 2.4)
            elif kind == "moe":
                icon_moe(svg, c, 2.6)
            elif kind == "loop":
                icon_loop(svg, c, 2.4)
            elif kind == "tyflo":
                icon_tyflo(svg, c, 2.4)
            elif kind == "ozn":
                icon_wheelchair(svg, c, 2.4, color="#2b5b84")
            elif kind == "fon":
                svg.line((x0, y + 0.4), (x0 + 3.2, y + 0.4), stroke=INK, sw=0.5, extra='stroke-dasharray="0.6,0.4"')
            elif kind == "ent":
                svg.circle((x0 + 1.6, y + 0.4), 1.5, fill=ACC, stroke="none")
                svg.text((x0 + 1.6, y + 1.0), "1", size=1.7, anchor="middle", weight=700, fill="#ffffff")
            elif kind == "lvl":
                level_mark(svg, (x0 + 1.4, y + 0.4), "")
            elif kind == "sec":
                svg.text((x0 + 1.6, y + 1.3), "A", size=3.0, weight=700, anchor="middle")
            for i, ln in enumerate(wrap(txt, int((w - 8) / 0.92))):
                svg.text((x0 + 5.0, y + 1.0 + i * 2.4), ln, size=1.7, fill=INK)
            y += 3.6 + 2.4 * (len(wrap(txt, int((w - 8) / 0.92))) - 1)
        return y + 1.0
    return f


# ----------------------------------------------------------------------------------------------------------------
def label_rooms(svg, v, lv, lab: Labels, big_names=True):
    for r in lv["pomieszczenia"]:
        if r["kind"] in ("roof",) or not r["numer"]:
            continue
        g = mp(r["poligon"])
        if g.is_empty:
            continue
        if r["kind"] in ("core_lift",) and not CFG["tight"]:
            continue
        pg = poly_paper(v, g)
        if pg.is_empty:
            continue
        rp = pg.representative_point()
        num = r["numer"]
        ar = fnum(r["powierzchnia"]) + " m²"
        s1, s2 = CFG["s1"], CFG["s2"]
        name = None
        w1 = Labels.tw(num, s1, True)
        w2 = Labels.tw(ar, s2)
        only_num = CFG["tight"] and (r["kind"] in ("core_lift", "shaft") or (r["powierzchnia"] < 6.5 and not pg.buffer(-0.3).contains(box(rp.x - max(w1, w2) / 2, rp.y - 2.6, rp.x + max(w1, w2) / 2, rp.y + 2.6))))
        if only_num:
            w2 = 0
        if big_names and r["powierzchnia"] > 70 and r["kind"] in ("room", "garage", "corridor") and r["kod_grupy"] not in ("KW",):
            name = short_name(r["nazwa"])
        h = (s1 + 0.6 + (0 if only_num else s2 + 0.4)) + (2.6 if name else 0)
        if r["kind"] == "core_lift":
            rp = Point(rp.x, rp.y + 2.4)
        w = max(w1, w2, Labels.tw(name, 2.0, True) if name else 0) + 0.8
        placed = None
        cands = [(rp.x, rp.y)]
        b = pg.bounds
        for fx in (0.5, 0.3, 0.7):
            for fy in (0.5, 0.3, 0.7, 0.2, 0.8):
                cands.append((b[0] + (b[2] - b[0]) * fx, b[1] + (b[3] - b[1]) * fy))
        inner = pg.buffer(-0.3)
        if r["kind"] == "core_lift":
            cands = [(rp.x, rp.y)]
        for (x, y) in cands:
            bx = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if (inner.contains(box(*bx)) or r["kind"] == "core_lift") and lab.free(bx):
                placed = (x, y, False)
                break
        if placed is None:
            # na zewnątrz z odnośnikiem
            for dist in (6, 9, 12, 15):
                for ang in range(0, 360, 30):
                    x = rp.x + dist * math.cos(math.radians(ang))
                    y = rp.y + dist * math.sin(math.radians(ang))
                    bx = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    if lab.free(bx) and in_bounds(bx):
                        placed = (x, y, True)
                        break
                if placed:
                    break
        if placed is None:
            placed = (rp.x, rp.y, False)
        x, y, leader = placed
        lab.add((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
        col = ACC if (r["kod_grupy"] in PUBLIC) else INK
        if leader:
            svg.line((rp.x, rp.y), (x, y + (1.0 if y > rp.y else -1.0)), stroke=GREY, sw=0.07)
            svg.circle((rp.x, rp.y), 0.3, fill=GREY, stroke="none")
        yy = y - h / 2 + s1 + 0.1
        if name:
            svg.text((x, yy), name, size=2.0, anchor="middle", weight=600, fill=col, extra=halo_extra(0.6))
            yy += 2.6
        svg.text((x, yy), num, size=s1, anchor="middle", weight=600, fill=col, extra=halo_extra(0.55))
        if not only_num:
            svg.text((x, yy + s2 + 0.45), ar, size=s2, anchor="middle", fill=GREY, extra=halo_extra(0.55))


SHORT = [("Hol główny", "HALA OBYWATELSKA"), ("Sala konferencyjna 200", "SALA 200 OS."), ("Sala konferencyjna 80", "SALA 80 OS."),
         ("Garaż", "GARAŻ · MDS"), ("Sala obrad", "SALA OBRAD SEJMIKU"), ("Hol reprezentacyjny", "HOL SEJMIKU"),
         ("Foyer / kuluary", "FOYER"), ("Bistro – sala", "BISTRO"), ("Wejście Obywatelskie", "WEJŚCIE OBYWATELSKIE"),
         ("Parking rowerowy", "ROWEROWNIA"), ("Łącznik", "ŁĄCZNIK"), ("Galeria kuluarowa", "KULUAR"), ("Rampa", "RAMPA"),
         ("Korytarz", "KORYTARZ"), ("Sala narad", "SALA NARAD"), ("Archiwum", "ARCHIWUM GW"), ("Serwerownia", "SERWEROWNIA"),
         ("Maszynownia", "MASZYNOWNIA GPC"), ("Centrale", "CENTRALE"), ("Sala spotkań", "SALA SPOTKAŃ"), ("Sala komisji", "SALA KOMISJI")]


def short_name(n):
    for k, s in SHORT:
        if n.startswith(k):
            return s
    return None


def block_names(svg, v, lv, lab: Labels):
    """Nazwy bloków funkcjonalnych (działów) – przy grupie pokoi, w korytarzu lub przy elewacji."""
    groups = {}
    for r in lv["pomieszczenia"]:
        if r["kind"] == "office" and r["kod_grupy"] not in ("KW",):
            groups.setdefault(r["kod_grupy"], []).append(mp(r["poligon"]))
    for code, gs in groups.items():
        u = unary_union([g.buffer(0.3) for g in gs])
        for part in sorted(polys(u), key=lambda p: -p.area)[:3 if code not in ("KS",) else 2]:
            if part.area < 40:
                continue
            c = part.centroid
            # kierunek na zewnątrz: od środka budynku
            plate = mp(lv["plyta"])
            pc = plate.centroid
            dx, dy = c.x - pc.x, c.y - pc.y
            L = math.hypot(dx, dy) or 1
            # punkt poza elewacją: dalej od centrum aż wyjdziemy z płyty + 2,5 m
            q = Point(c.x, c.y)
            for k_ in range(1, 80):
                q = Point(c.x + dx / L * k_ * 0.5, c.y + dy / L * k_ * 0.5)
                if not plate.buffer(1.2).contains(q):
                    break
            txt = f"{code} – {DEPT_NAMES.get(code, code).upper()}"
            p = v.p(q.x, q.y)
            w = Labels.tw(txt, 2.1, True)
            bx = (p[0] - w / 2, p[1] - 1.5, p[0] + w / 2, p[1] + 1.0)
            if not lab.free(bx):
                continue
            lab.add(bx)
            svg.text(p, txt, size=2.1, anchor="middle", weight=700, fill=ACC if code in ("KS",) else INK, ls=0.12, extra=halo_extra(0.9))


# ----------------------------------------------------------------------------------------------------------------
def draw_plan(svg, v, lid, lab: Labels):
    lv = LV[lid]
    plate = mp(lv["plyta"])
    rooms = lv["pomieszczenia"]
    # tło pomieszczeń
    for r in rooms:
        g = mp(r["poligon"])
        if g.is_empty:
            continue
        model_rings(svg, v, g, fill=room_fill(r), stroke="none", sw=0)
    # rampa: kreskowanie
    for rp in lv.get("rampy", []):
        g = mp(rp["poligon"])
        model_rings(svg, v, g, fill=svg.hatch("ramp", 1.2, 45, HAIR, 0.08), stroke=GREY, sw=0.1)
    # meble
    for r in rooms:
        g = mp(r["poligon"])
        if r.get("furn") == "sejmik":
            continue
        draw_furniture(svg, v, r, g)
    if lid == "S":
        draw_sejmik_seats(svg, v)
    # stanowiska postojowe
    for i, st in enumerate(lv.get("miejsca_postojowe", [])):
        g = mp(st["poligon"])
        model_rings(svg, v, g, fill="#ffffff" if not st["ozn"] else "#eef2f6", stroke=GREY, sw=0.1)
        c = v.p(g.centroid.x, g.centroid.y)
        if st["ozn"]:
            icon_wheelchair(svg, c, 2.2, color="#2b5b84")
        else:
            svg.text((c[0], c[1] + 0.6), str(i + 1), size=1.6, anchor="middle", fill=GREY)
    for a in lv.get("drogi", []):
        g = mp(a)
        if g.is_empty:
            continue
        mrr = g.minimum_rotated_rectangle
        cs = list(mrr.exterior.coords)[:4]
        e1 = (cs[1][0] - cs[0][0], cs[1][1] - cs[0][1])
        e2 = (cs[2][0] - cs[1][0], cs[2][1] - cs[1][1])
        if math.hypot(*e1) < math.hypot(*e2):
            p0 = ((cs[0][0] + cs[1][0]) / 2, (cs[0][1] + cs[1][1]) / 2)
            p1 = ((cs[2][0] + cs[3][0]) / 2, (cs[2][1] + cs[3][1]) / 2)
        else:
            p0 = ((cs[1][0] + cs[2][0]) / 2, (cs[1][1] + cs[2][1]) / 2)
            p1 = ((cs[3][0] + cs[0][0]) / 2, (cs[3][1] + cs[0][1]) / 2)
        svg.line(v.p(*p0), v.p(*p1), stroke=HAIR, sw=0.1, extra='stroke-dasharray="2,1.5"')
    # rdzenie: schody, dźwigi, MOE
    for r in rooms:
        g = mp(r["poligon"])
        if r["kind"] == "core_stair":
            draw_stair(svg, v, g)
        elif r["kind"] == "core_lift":
            tag = ""
            m = re.search(r"\b([A-Z]\d?)\b", r["nazwa"].replace("Dźwig", ""))
            if m:
                tag = m.group(1)
            draw_lift(svg, v, g, tag)
    # ściany
    for key in ("zewnetrzne", "wewnetrzne", "trzony"):
        g = mp(lv["sciany"].get(key))
        model_rings(svg, v, g, fill=INK, stroke="none", sw=0)
    # słupy
    for c in lv.get("slupy", []):
        x, y = v.p(*c)
        s = v.mm(0.45)
        svg.poly([(x - s / 2, y - s / 2), (x + s / 2, y - s / 2), (x + s / 2, y + s / 2), (x - s / 2, y + s / 2)], fill=INK, stroke="none")
    # okna
    for w in lv.get("okna", []):
        draw_window(svg, v, w)
    # drzwi
    for d in lv.get("drzwi", []):
        draw_door(svg, v, d)
    # obrys
    model_rings(svg, v, plate, fill="none", stroke=INK, sw=0.35)
    # symbole dostępności
    for r in rooms:
        g = mp(r["poligon"])
        if g.is_empty:
            continue
        tags = set(r.get("tags", []))
        c = v.p(g.centroid.x, g.centroid.y)
        b = poly_paper(v, g).bounds
        if "wc_ozn" in tags or "komfortka" in tags:
            icon_wheelchair(svg, (b[2] - 2.2, b[1] + 2.2), 2.2)
        if "moe" in tags:
            icon_moe(svg, (b[0] + 2.0, b[1] + 2.0), 2.4)
        if "loop" in tags:
            icon_loop(svg, (b[2] - 2.2, b[3] - 2.2), 2.2)
        for bb in [(b[2] - 3.4, b[1] + 1.0, b[2] - 1.0, b[1] + 3.4), (b[0] + 0.8, b[1] + 0.8, b[0] + 3.2, b[1] + 3.2), (b[2] - 3.4, b[3] - 3.4, b[2] - 1.0, b[3] - 1.0)]:
            pass
    # pustka (antresola)
    if lid == "ANT":
        g = mp(lv["extra"].get("void"))
        model_rings(svg, v, g, fill="none", stroke=GREY, sw=0.12)
        for pg in polys(g):
            cs = list(pg.minimum_rotated_rectangle.exterior.coords)
            svg.line(v.p(*cs[0]), v.p(*cs[2]), stroke=HAIR, sw=0.1)
            svg.line(v.p(*cs[1]), v.p(*cs[3]), stroke=HAIR, sw=0.1)
        cc = v.p(g.centroid.x, g.centroid.y) if not g.is_empty else None
        if cc:
            svg.text(cc, "PUSTKA NAD SALĄ OBRAD, KULUAREM I HOLEM", size=2.2, anchor="middle", weight=600, fill=GREY, extra=halo_extra(0.8))


# ----------------------------------------------------------------------------------------------------------------
def level_marks(svg, v, lid, lab):
    lv = LV[lid]
    if lid in ("D",):
        return
    z = KOND[lid]["posadzka_wzgl"] if lid != "ANT" else SPEC["kondygnacja_sejmiku"]["antresola"]["wzgl"]
    cands = sorted([r for r in lv["pomieszczenia"] if r["kind"] in ("corridor", "garage") or "hall" in r.get("tags", [])],
                   key=lambda r: -r["powierzchnia"])
    for r in cands[:1]:
        g = mp(r["poligon"])
        pg = poly_paper(v, g)
        for fx, fy in ((0.25, 0.3), (0.6, 0.5), (0.4, 0.7)):
            b = pg.bounds
            x, y = b[0] + (b[2] - b[0]) * fx, b[1] + (b[3] - b[1]) * fy
            bx = (x - 1.5, y - 2.5, x + 22, y + 2.5)
            if pg.buffer(-0.5).contains(Point(x, y)) and lab.free(bx):
                lab.add(bx)
                level_mark(svg, (x, y), fz(z), f"{fnum(Z0 + z, 2)} m n.p.m.")
                break


# ----------------------------------------------------------------------------------------------------------------
# OTOCZENIE PARTERU
def site_context(svg, v, lab):
    u = SITE["ulice_i_sytuacja"]
    clip_uv = (v.u0, v.v0, v.u1, v.v1)

    def ppoly(pts):
        try:
            g = Polygon(pts).buffer(0)
        except Exception:
            return None
        return g if g.area > 0.05 else None
    win = Polygon([T.en(clip_uv[0], clip_uv[1]), T.en(clip_uv[2], clip_uv[1]), T.en(clip_uv[2], clip_uv[3]), T.en(clip_uv[0], clip_uv[3])])
    for key, col in (("jezdnie", "#ecebe8"), ("chodniki", "#f7f6f3"), ("trawniki", "#eef0ea")):
        for it in u[key]:
            if it.get("zamknieta", True) and len(it["pts"]) >= 3:
                g = ppoly(it["pts"])
                if g is not None:
                    g = g.intersection(win)
                    if not g.is_empty:
                        model_rings(svg, v, g, fill=col, stroke="none")
    for it in u["krawezniki"]:
        ln = LineString(it["pts"]).intersection(win) if len(it["pts"]) > 1 else None
        if ln is not None and not ln.is_empty:
            for g in ([ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))):
                if g.geom_type == "LineString":
                    svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#b8b3ac", sw=0.1, close=False)
    for it in u["tory_tramwajowe"]:
        ln = LineString(it["pts"]).intersection(win)
        for g in ([ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))):
            if g.geom_type == "LineString":
                svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#8c877f", sw=0.12, close=False, extra='stroke-dasharray="1.6,0.8"')
    for w in SITE["woda"]["linia_brzegu"]:
        ln = LineString(w["pts"]).intersection(win)
        for g in ([ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))):
            if g.geom_type == "LineString":
                svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#7d98a3", sw=0.25, close=False)
    # budynki istniejące
    for b in SITE["budynki"]["items"]:
        g = ppoly(b["pts"])
        if g is None:
            continue
        g = g.intersection(win)
        if g.is_empty:
            continue
        model_rings(svg, v, g, fill=svg.hatch("bld", 1.0, 45, "#9c968e", 0.07, bg="#efede9"), stroke="#6f6a63", sw=0.2)
        c = g.representative_point()
        nm = b.get("ulica") or ""
        nr = b.get("adres_nr") or ""
        lab_t = f"{nm} {nr}".strip() or (b.get("etykieta") or "")
        if lab_t and g.area > 60:
            p = v.p(c.x, c.y)
            svg.text(p, lab_t, size=1.9, anchor="middle", fill=GREY, extra=halo_extra(0.6))
    for t in u.get("nazwy_ulic", []):
        if win.contains(Point(t["e"], t["n"])):
            p = v.p(t["e"], t["n"])
            ang = -(t.get("rot_deg", 0) - math.degrees(math.atan2(T.ex[1], T.ex[0])))
            if ang > 90:
                ang -= 180
            if ang < -90:
                ang += 180
            svg.text(p, t["tekst"].upper(), size=2.6, anchor="middle", weight=600, fill=GREY, rot=ang, ls=0.4, extra=halo_extra(0.8))


# Geometria elementów zagospodarowania – spójna z tools/zagospodarowanie.py (rysunek 1:500).
Z_PATHS = [[(84.32, 43.12), (83.0, 34.0), (80.6, 20.0), (77.5, 6.0), (76.0, -4.0)],
           [(59.4, 23.6), (70.0, 22.5), (80.6, 20.0), (95.0, 27.0), (99.0, 36.0)],
           [(83.0, 34.0), (97.5, 37.0)]]
Z_RAIN = [(84.5, 2.0), (94.0, 2.4), (93.4, 16.6), (84.6, 16.0)]
Z_PLAY = [(87.5, -5.5), (95.5, -5.2), (95.5, 0.8), (87.5, 0.6)]
Z_PERGOLA = [((95.2, 5 + k * 3.2), (95.2, 7.2 + k * 3.2)) for k in range(8)]
Z_BENCH_BUL = [(98.5, 38.0), (104.0, 38.3), (104.0, 38.9), (98.5, 38.6)]
Z_TRACE = [(63.4, 79.6), (75.0, 81.0), (86.0, 81.9), (93.5, 81.6), (98.6, 79.6)]
Z_ROUND_BENCH = (104.0, 73.5)
Z_NEW_TREES = [(66.0, 79.4), (71.5, 80.3), (77.0, 81.0), (82.5, 81.6), (99.8, 37.2), (103.8, 37.6),
               (64.5, 30.0), (70.5, 33.5), (89.0, 25.0), (93.0, 31.0), (73.0, 11.0), (90.5, 9.0)]
Z_ENTR = [((103.2, 73.5), "1", "Brama Mostowa – wejście główne"), ((91.0, 76.6), "2", "wejście od skweru (podcień)"),
          ((114.6, 46.2), "3", "Wejście Obywatelskie"), ((62.6, 69.8), "4", "wejście konferencyjne / bistro"),
          ((84.3, 42.6), "5", "wejście ogrodowe"), ((77.6, 41.5), "6", "rowerownia"),
          ((51.8, 23.6), "7", "brama ogrodowa"), ((114.6, 47.9), "8", "garaż, dostawy")]


def site_design(svg, v, lab):
    """Projekt otoczenia (R-105): nawierzchnie z materiałem, mała architektura, oświetlenie, zieleń, ślad pierzei 1934, ogród."""
    g_ = SITE["granice"]
    oi = Polygon(g_["obszar_inwestycji"]["pts"]).buffer(0)
    comp = Polygon(g_["granica_opracowania_konkursowego"]["pts"]).buffer(0)
    skwer = Polygon(g_["teren_uzyczony_dz_9_2"]["pts"]).buffer(0)
    ogrodki = Polygon(g_["ogrodki_przydomowe"]["pts"]).buffer(0)
    bld = unary_union([Polygon(b["obrys_ccw"]).buffer(0) for b in SPEC["bryly"]])
    garden = oi.difference(bld.buffer(0.05))
    podc = Polygon(SPEC["cofniecia_wneki"]["podcien_Brama_Mostowa"]["obrys_ccw"]).buffer(0)
    brama = Polygon(SPEC["cofniecia_wneki"]["brama_ogrodowa"]["obrys_ccw"]).buffer(0)
    # granit strzegomski: skwer + przedpola w obszarze inwestycji (jak w zagospodarowanie.py), podcień, brama
    granit = unary_union([skwer.union(oi.difference(bld)).intersection(comp), podc, brama])
    model_rings(svg, v, granit, fill=svg.hatch("granit", 1.5, 0, "#d8d4ce", 0.06, bg="#f6f5f2"), stroke="none")
    gard = garden.intersection(Polygon([(60, -10), (100, -10), (100, 40), (60, 40)]))
    model_rings(svg, v, gard, fill=svg.hatch("lawn", 0.9, 30, "#d9ddd2", 0.05, bg="#fbfbf9"), stroke="none")
    model_rings(svg, v, ogrodki.intersection(oi), fill=svg.hatch("ogr", 1.1, -30, "#cfd3c8", 0.06, bg="#f6f7f3"), stroke="#8d8a83", sw=0.12,
                extra='stroke-dasharray="1.2,0.8"')
    rain = Polygon(Z_RAIN).intersection(gard)
    model_rings(svg, v, rain, fill=svg.hatch("rain", 0.7, 0, "#b9c4c6", 0.06, bg="#f1f4f4"), stroke="#7d98a3", sw=0.15)
    paths = unary_union([LineString(pp).buffer(1.1, cap_style=2) for pp in Z_PATHS]).intersection(garden)
    model_rings(svg, v, paths, fill=svg.hatch("brick", 0.8, 90, "#c9bfb4", 0.07, bg="#f3efea"), stroke="#a69c91", sw=0.1)
    play = Polygon(Z_PLAY)
    model_rings(svg, v, play, fill="#efefec", stroke=GREY, sw=0.12)
    for a, b in Z_PERGOLA:
        svg.line(v.p(*a), v.p(*b), stroke=INK, sw=0.35)
    svg.poly([v.p(*q) for q in Z_BENCH_BUL], fill="#ffffff", stroke=INK, sw=0.12)
    # ślad pierzei 1934 + okrągła ława
    tr = [v.p(*q) for q in Z_TRACE]
    svg.poly(tr, fill="none", stroke=ACC, sw=v.mm(0.5), close=False)
    svg.poly(tr, fill="none", stroke="#ffffff", sw=0.12, close=False)
    svg.circle(v.p(*Z_ROUND_BENCH), v.mm(2.2), fill="none", stroke=INK, sw=0.22)
    svg.circle(v.p(*Z_ROUND_BENCH), v.mm(1.6), fill="none", stroke=INK, sw=0.12)
    # opisy elementów (z odnośnikami)
    notes = [(Polygon(Z_RAIN).centroid.coords[0], "ogród deszczowy (retencja)"), (play.centroid.coords[0], "plac zabaw – EPDM"),
             (LineString(Z_TRACE).interpolate(0.55, normalized=True).coords[0], "ślad pierzei 1934 r. – granit z listwą z brązu"),
             (Z_ROUND_BENCH, "okrągła ława granitowa"), ((96.0, 12.0), "pergola przy murze"), ((101.2, 38.4), "ława granitowa")]
    for (e, n), t in notes:
        p = v.p(e, n)
        w = Labels.tw(t, 1.7)
        bx = (p[0] - w / 2, p[1] - 3.6, p[0] + w / 2, p[1] - 1.2)
        if lab.free(bx):
            lab.add(bx)
            svg.text((p[0], p[1] - 1.6), t, size=1.7, anchor="middle", fill=ACC if "1934" in t else GREY, extra=halo_extra(0.6))
    # stojaki rowerowe: 20 na skwerze (zach. część), 10 przy bramie ogrodowej
    def racks(p0, dirv, n):
        for i in range(n):
            q = (p0[0] + dirv[0] * 0.8 * i, p0[1] + dirv[1] * 0.8 * i)
            a = (q[0] - dirv[1] * 0.9, q[1] + dirv[0] * 0.9)
            b = (q[0] + dirv[1] * 0.9, q[1] - dirv[0] * 0.9)
            svg.line(v.p(*a), v.p(*b), stroke=INK, sw=0.14)
    racks(T.en(4.0, 31.6), T.ex, 10)
    racks(T.en(4.0, 33.6), T.ex, 10)
    racks(WF.en(17.0, 17.3), WF.ex, 10)
    # latarnie: słupki ogrodowe wzdłuż ścieżek co ~9 m, latarnie parkowe h 4 m na skwerze i przy bulwarze
    lamps = []
    for pp in Z_PATHS:
        ln = LineString(pp)
        k = 1.5
        while k <= ln.length:
            q = ln.interpolate(k)
            if garden.contains(q):
                lamps.append((q.x + 1.6, q.y, "b"))
            k += 9.0
    for q in LineString(Z_TRACE).parallel_offset(3.5, "right").coords[::1]:
        lamps.append((q[0], q[1], "l"))
    for (x, y, kind) in lamps:
        if not comp.contains(Point(x, y)):
            continue
        p = v.p(x, y)
        r = 0.9 if kind == "l" else 0.6
        svg.circle(p, r, fill="#ffffff", stroke=INK, sw=0.15)
        svg.line((p[0] - r, p[1]), (p[0] + r, p[1]), stroke=INK, sw=0.1)
        svg.line((p[0], p[1] - r), (p[0], p[1] + r), stroke=INK, sw=0.1)
    NEW_TREES.extend([(q, "") for q in Z_NEW_TREES])
    # drzewa od strony rzeki (jak w zagospodarowanie.py: 1,4 m od krawężnika wsch.)
    kerbs = unary_union([LineString(it["pts"]) for it in SITE["ulice_i_sytuacja"]["krawezniki"] if len(it["pts"]) > 1])
    for nn in (16.0, 24.0, 32.0, 40.0, 48.0, 56.0):
        x = kerbs.intersection(LineString([(123.5, nn), (131.6, nn)]))
        if not x.is_empty:
            NEW_TREES.append(((x.bounds[2] + 1.4, nn), "river"))


NEW_TREES = []


def TOWER_V_():
    return SIATKA["wieza"]["osie_v"][-1]


def TOWER_U_():
    return SIATKA["wieza"]["osie_u"][-1]


def draw_trees(svg, v, win):
    removed = set(SPEC["zagospodarowanie"]["drzewa_usuniete"])
    for t in SITE["zielen"]["drzewa"]:
        q = Point(t["e"], t["n"])
        if not win.contains(q):
            continue
        p = v.p(t["e"], t["n"])
        r = v.mm(3.0 if t.get("typ") == "lisciaste" else 2.0)
        if t["nr"] in removed:
            svg.circle(p, r, fill="none", stroke="#a9a39b", sw=0.12, extra='stroke-dasharray="0.6,0.5"')
            svg.line((p[0] - r * 0.5, p[1] - r * 0.5), (p[0] + r * 0.5, p[1] + r * 0.5), stroke=ACC, sw=0.15)
            svg.line((p[0] - r * 0.5, p[1] + r * 0.5), (p[0] + r * 0.5, p[1] - r * 0.5), stroke=ACC, sw=0.15)
        else:
            svg.circle(p, r, fill="#ffffff", stroke="#6f6a63", sw=0.13, extra='fill-opacity="0.55"')
            svg.circle(p, 0.35, fill="#6f6a63", stroke="none")
        svg.text((p[0], p[1] + r + 1.7), t["nr"], size=1.6, anchor="middle", fill=GREY, extra=halo_extra(0.4))
    for (q, nm) in NEW_TREES:
        if not win.contains(Point(q)):
            continue
        p = v.p(*q)
        r = v.mm(2.4)
        svg.circle(p, r, fill="none", stroke=INK, sw=0.18)
        svg.circle(p, r * 0.55, fill="none", stroke=INK, sw=0.08, extra='stroke-dasharray="0.5,0.4"')
        svg.circle(p, 0.35, fill=INK, stroke="none")


def entrances(svg, v):
    """Wejścia 1–8 (spec. rozdz. 9), położenie jak w tools/zagospodarowanie.py; wszystkie w poziomie chodnika."""
    for (e, n), k, _ in Z_ENTR:
        x, y = v.p(e, n)
        svg.circle((x, y), 2.1, fill=ACC, stroke="#ffffff", sw=0.25)
        svg.text((x, y + 0.75), k, size=2.1, anchor="middle", weight=700, fill="#ffffff")


def fon_paths(svg, v):
    """Ścieżki dotykowe (FON) w hali: od wejść do informacji, kancelarii i dźwigów."""
    cc = BUD["luk"]["srodek_uv"]
    d_arc = (cc[0] + 10.6 * math.cos(math.radians(45)), cc[1] + 10.6 * math.sin(math.radians(45)))
    info = (cc[0] + 6.5 * math.cos(math.radians(225)) + 2, cc[1] + 6.5 * math.sin(math.radians(225)) + 2)
    lifts_A = (11.9, 11.2)
    kanc = (27.0, 14.0)
    pp = (32.6, 6.0)
    ent_ob = (38.6, 4.1)
    garden = (10.0, 1.0)
    lines = [[d_arc, info, kanc], [info, (18.0, 12.5), lifts_A], [ent_ob, pp], [garden, (12.0, 6.5), lifts_A]]
    for ln in lines:
        pts = [v.pu(*p) for p in ln]
        svg.poly(pts, fill="none", stroke="#8f8981", sw=0.55, close=False, extra='stroke-dasharray="0.35,0.3"')
    # informacja i tyflomapy
    p = v.pu(*info)
    svg.poly([(p[0] - 3.5, p[1] - 1.2), (p[0] + 3.5, p[1] - 1.2), (p[0] + 3.5, p[1] + 1.2), (p[0] - 3.5, p[1] + 1.2)], fill="#ffffff", stroke=INK, sw=0.15)
    svg.text((p[0], p[1] + 0.6), "informacja", size=1.6, anchor="middle", fill=INK)
    for q in (d_arc, ent_ob, garden):
        pq = v.pu(*q)
        icon_tyflo(svg, (pq[0] + 2.5, pq[1] - 2.5), 2.2)


# ----------------------------------------------------------------------------------------------------------------
def roof_plan(svg, v, lab):
    lv = LV["D"]
    for d in lv.get("dachy", []):
        g = mp(d["poligon"])
        model_rings(svg, v, g, fill="#ffffff", stroke=INK, sw=0.35)
        att = g.difference(g.buffer(-0.6, join_style=2))
        model_rings(svg, v, att, fill=svg.hatch("att", 0.6, 45, INK, 0.08, bg="#e6e3de"), stroke=INK, sw=0.15)
    for r in lv["pomieszczenia"]:
        g = mp(r["poligon"])
        if g.is_empty:
            continue
        if "green" in r.get("tags", []):
            model_rings(svg, v, g, fill=svg.hatch("green", 0.8, 60, "#9aa58e", 0.08, bg="#f2f4ef"), stroke=GREY, sw=0.12)
            # donice, balustrada cofnięta 1,5 m
            inner = g.buffer(-1.5, join_style=2)
            model_rings(svg, v, inner, fill="none", stroke=GREY, sw=0.15, extra='stroke-dasharray="1.5,0.6"')
        else:
            # BIPV – moduły w rzędach (co 1,10 m) w kierunku spadku
            model_rings(svg, v, g, fill="#f4f3f1", stroke=GREY, sw=0.12)
            fr = T if r["nazwa"].startswith("Dach wieży") else WF
            lb = fr.to_local_geom(g).bounds
            x = lb[0] + 0.6
            while x < lb[2]:
                ln = fr.line([(x, lb[1] - 1), (x, lb[3] + 1)]).intersection(g)
                for seg in ([ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))):
                    if seg.geom_type == "LineString" and seg.length > 0.5:
                        svg.poly([v.p(*c) for c in seg.coords], fill="none", stroke="#bdb8b0", sw=0.06, close=False)
                x += 1.10
            y = lb[1] + 1.0
            while y < lb[3]:
                ln = fr.line([(lb[0] - 1, y), (lb[2] + 1, y)]).intersection(g)
                for seg in ([ln] if ln.geom_type == "LineString" else list(getattr(ln, "geoms", []))):
                    if seg.geom_type == "LineString" and seg.length > 0.5:
                        svg.poly([v.p(*c) for c in seg.coords], fill="none", stroke="#d3cfc8", sw=0.05, close=False)
                y += 2.0
    # spadki i wpusty
    spadki = [(T, [(9.0, 22.0), (9.0, 8.0), (20.0, 22.0), (20.0, 8.0), (30.0, 6.0)], (0, -1)),
              (WF, [(10.0, 4.0), (25.0, 4.0), (40.0, 4.0), (10.0, 11.0), (25.0, 11.0)], (0, 1))]
    for fr, pts, d in spadki:
        for (x, y) in pts:
            a = v.p(*fr.en(x, y))
            b = v.p(*fr.en(x + d[0] * 3.0, y + d[1] * 3.0))
            arrow(svg, a, b, sw=0.15, head=1.2)
            svg.text(((a[0] + b[0]) / 2 + 1.2, (a[1] + b[1]) / 2), "1,5 %", size=1.6, fill=INK, extra=halo_extra(0.5))
    wp = [T.en(5.0, 2.5), T.en(15.0, 2.5), T.en(25.0, 2.5), T.en(35.0, 2.5), WF.en(8.0, 13.0), WF.en(22.0, 13.0), WF.en(36.0, 13.0), WF.en(48.0, 10.5)]
    for q in wp:
        p = v.p(*q)
        svg.circle(p, 0.9, fill="#ffffff", stroke=INK, sw=0.15)
        svg.circle(p, 0.35, fill=INK, stroke="none")
    # rzędne
    for d in lv.get("dachy", []):
        g = mp(d["poligon"])
        c = g.representative_point()
        p = v.p(c.x, c.y)
        nm = {"W": "DACH WIEŻY", "M": "DACH SKRZYDŁA", "S": "TARAS NAD OŁAWĄ"}.get(d["id"], d["id"])
        t1 = f"attyka {fz(d['attyka'])} ({fnum(d['attyka_npm'], 2)})" if d.get("attyka") is not None else ""
        t2 = f"pokrycie {fz(d['min'])}…{fz(d['max'])}" if d.get("max") else (f"taras {fz(d['min'])} ({fnum(d['min_npm'], 2)})" if d.get("min") else "")
        w = max(Labels.tw(nm, 2.4, True), Labels.tw(t1, 1.8), Labels.tw(t2, 1.8)) + 2
        bx = (p[0] - w / 2, p[1] - 4, p[0] + w / 2, p[1] + 5)
        lab.add(bx)
        svg.poly([(bx[0], bx[1]), (bx[2], bx[1]), (bx[2], bx[3]), (bx[0], bx[3])], fill="#ffffff", stroke="none", extra='fill-opacity="0.85"')
        svg.text((p[0], p[1] - 1.4), nm, size=2.4, anchor="middle", weight=700, fill=INK, ls=0.15)
        svg.text((p[0], p[1] + 1.3), t1, size=1.8, anchor="middle", fill=INK)
        svg.text((p[0], p[1] + 3.6), t2, size=1.8, anchor="middle", fill=GREY)
        level_mark(svg, (p[0] - w / 2 - 2.5, p[1] + 1.0), "")
    # lamele korony (rzut z góry – linia łuku)
    cc = BUD["luk"]["srodek_uv"]
    pts = [v.pu(cc[0] + 13.7 * math.cos(math.radians(a)), cc[1] + 13.7 * math.sin(math.radians(a))) for a in range(0, 91, 3)]
    svg.poly(pts, fill="none", stroke=GREY, sw=0.12, close=False, extra='stroke-dasharray="0.4,0.4"')
    note = ["Dachy bez urządzeń technicznych, masztów i stelaży – BIPV szkło-szkło jako pokrycie za attyką",
            f"(wieża i skrzydło razem {SPEC['elewacje']['PV']['BIPV_dach_kWp']} kWp; elewacje {SPEC['elewacje']['PV']['BIPV_elewacje_kWp']} kWp); "
            "wyrzutnie wentylacji w lamelach korony od pd., czerpnia w płycinach kond. 1."]
    return note


# ----------------------------------------------------------------------------------------------------------------
WINDOWS = {
    "P": (-50.0, 62.0, -44.0, 52.0),
    "full": (-41.0, 54.0, -40.0, 46.0),
    "tower": (-14.0, 56.0, -22.0, 46.0),
}


def draw_drawing(svg, v, lid, lab, clip_rect, site_clip=None, sec_ext=None):
    """Treść rysunku (bez legendy i ramki): otoczenie (P), rzut / dach, osie, wymiary, przekroje, etykiety."""
    lv = LV[lid]
    u0, u1, v0, v1 = v.u0, v.u1, v.v0, v.v1
    win = Polygon([T.en(u0, v0), T.en(u1, v0), T.en(u1, v1), T.en(u0, v1)])
    clip_id = svg.uid("clip")
    x, y, w, h = clip_rect
    svg.defs.append(f'<clipPath id="{clip_id}"><rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/></clipPath>')
    svg.add(f'<g clip-path="url(#{clip_id})">')
    if lid == "P" and site_clip is not None:
        cid2 = svg.uid("clip")
        pts = " ".join(f"{a:.2f},{b:.2f}" for a, b in [v.p(*c) for c in site_clip.exterior.coords])
        svg.defs.append(f'<clipPath id="{cid2}"><polygon points="{pts}"/></clipPath>')
        svg.add(f'<g clip-path="url(#{cid2})">')
    if lid == "P":
        NEW_TREES.clear()
        site_context(svg, v, lab)
        site_design(svg, v, lab)
        draw_trees(svg, v, win)
        if site_clip is not None:
            svg.add("</g>")
            model_rings(svg, v, site_clip, fill="none", stroke="#2f6f8f", sw=0.3, extra='stroke-dasharray="3,1.2"')
    if lid == "D":
        note = roof_plan(svg, v, lab)
    else:
        draw_plan(svg, v, lid, lab)
        note = None
    if lid == "P":
        fon_paths(svg, v)
        entrances(svg, v)
    # osie, wymiary, przekroje
    bbox = T.to_local_geom(W_poly()).bounds
    if CFG["tight"]:
        draw_axes_dims_tight(svg, v, lid)
        draw_sections_tight(svg, v, lid)
    else:
        draw_axes(svg, v, lid, (bbox[0], bbox[1], bbox[2], bbox[3]))
        draw_dims(svg, v, lid)
        if sec_ext is None:
            draw_sections(svg, v, lab)
        else:
            draw_sections_crop(svg, v, sec_ext)
    svg.add("</g>")
    # etykiety
    if lid != "D":
        label_rooms(svg, v, lv, lab)
        if CFG["tight"]:
            block_names_inside(svg, v, lv, lab)
        else:
            block_names(svg, v, lv, lab)
        level_marks(svg, v, lid, lab)
    else:
        for r in lv["pomieszczenia"]:
            g = mp(r["poligon"])
            if g.is_empty:
                continue
            pg = poly_paper(v, g)
            b = pg.bounds
            for fx, fy in ((0.5, 0.25), (0.5, 0.75), (0.3, 0.5), (0.7, 0.5)):
                x, y = b[0] + (b[2] - b[0]) * fx, b[1] + (b[3] - b[1]) * fy
                bx = (x - 6, y - 2.5, x + 6, y + 2.5)
                if pg.buffer(-1).contains(Point(x, y)) and lab.free(bx):
                    lab.add(bx)
                    svg.text((x, y), r["numer"], size=1.8, anchor="middle", weight=600, fill=INK, extra=halo_extra(0.6))
                    svg.text((x, y + 2.2), fnum(r["powierzchnia"]) + " m²", size=1.6, anchor="middle", fill=GREY, extra=halo_extra(0.6))
                    break
    if lid == "P":
        terrain_marks(svg, v, lab)
        material_labels(svg, v, lab)
    return note


def page(lid):
    lv = LV[lid]
    plate = mp(lv["plyta"])
    if lid == "P":
        u0, u1, v0, v1 = WINDOWS["P"]
    elif lid in ("1", "2", "3", "4", "-1", "D"):
        u0, u1, v0, v1 = WINDOWS["full"]
    else:
        u0, u1, v0, v1 = WINDOWS["tower"]
    M = 10.0
    TITLE_H = 22.0
    LEG_W = 168.0
    plan_w = (u1 - u0) * K
    plan_h = (v1 - v0) * K
    W = M + plan_w + 8 + LEG_W + M
    H = M + TITLE_H + plan_h + M
    svg = Svg(W, H)
    svg.add(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>')
    v = UVView(u0, u1, v0, v1, M, M + TITLE_H)
    lab = Labels()
    note = draw_drawing(svg, v, lid, lab, (v.ox, v.oy, plan_w, plan_h))
    # rama planu
    svg.poly([(v.ox, v.oy), (v.ox + plan_w, v.oy), (v.ox + plan_w, v.oy + plan_h), (v.ox, v.oy + plan_h)], fill="none", stroke="#d0ccc5", sw=0.2)
    # tytuł
    t1, t2 = level_title(lid)
    svg.text((M, M + 7.5), t1, size=5.2, weight=700, fill=INK, ls=0.2)
    svg.text((M, M + 14.0), f"{t2}  ·  skala 1:200  ·  BRAMA I LATARNIA – siedziba UMWD i Sejmiku Województwa Dolnośląskiego", size=2.6, fill=GREY)
    north_arrow(svg, (M + plan_w - 12, M + TITLE_H + 14), size=14, rot_deg=north_rot())
    scale_bar(svg, (M + plan_w - 72, M + TITLE_H + plan_h - 9), SC, metres=(0, 5, 10, 20), h=1.4)
    # legenda
    lx = M + plan_w + 8
    blocks = [symbols_block(lid)]
    if lid == "P":
        blocks.insert(0, materials_block)
    if note:
        def nb(svg, x0, y, w, note=note):
            svg.text((x0, y + 2.0), "UWAGI", size=2.2, weight=700, fill=INK)
            y += 4.6
            for ln in note:
                for l2 in wrap(ln, int(w / 0.95)):
                    svg.text((x0, y + 1.7), l2, size=1.75, fill=INK)
                    y += 2.5
            return y
        blocks.insert(0, nb)
    if lid in ("-1", "-2"):
        blocks.insert(0, parking_block(lid))
    y_end = draw_legend(svg, lx, M + TITLE_H + 2, LEG_W, lv, blocks)
    if y_end > H - M:
        svg.h_mm = y_end + M
        H = svg.h_mm
        svg.parts[0] = f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>'
    return svg


def W_poly():
    return Polygon(SPEC["bryly"][0]["obrys_ccw"])


def parking_block(lid):
    def f(svg, x0, y, w):
        lv = LV[lid]
        n = len(lv.get("miejsca_postojowe", []))
        oz = sum(1 for s in lv.get("miejsca_postojowe", []) if s["ozn"])
        tgt = SPEC["podziemie"][lid]["miejsca"]
        svg.text((x0, y + 2.0), "MIEJSCA POSTOJOWE", size=2.2, weight=700, fill=INK)
        y += 4.6
        for ln in [f"w układzie rysunku: {n} (w tym OzN {oz}); specyfikacja: {tgt}",
                   "stanowiska 2,5 × 5,0 m, OzN 3,6 × 5,0 m, drogi manewrowe 6,0 m; MDS w całym garażu",
                   "rozbieżność ze specyfikacją – patrz docs/70_rysunki/rzuty_raport.md"]:
            for l2 in wrap(ln, int(w / 0.95)):
                svg.text((x0, y + 1.7), l2, size=1.75, fill=ACC if ln.startswith("w układzie") and n < tgt else INK)
                y += 2.5
        return y + 1.5
    return f


def materials_block(svg, x0, y, w):
    svg.text((x0, y + 2.0), "NAWIERZCHNIE I MAŁA ARCHITEKTURA", size=2.2, weight=700, fill=INK)
    y += 4.6
    items = [("granit", "granit strzegomski płomieniowany – skwer, podcień, brama ogrodowa"),
             ("brick", "ścieżki ogrodu: cegła i gruz z wykopu na podbudowie przepuszczalnej"),
             ("lawn", "trawnik, łąka kwietna"), ("ogr", "ogródki przydomowe – zachowane, nieogrodzone"),
             ("rain", "ogród deszczowy (retencja)"), ("acc", "ślad pierzei pn. z 1934 r. – pas granitu z listwą z brązu"),
             ("tree_n", "drzewo projektowane (lipa drobnolistna, klon polny, grab)"), ("tree_e", "drzewo istniejące zachowane (nr wg M.06)"),
             ("tree_x", "drzewo do usunięcia"), ("lamp", "latarnia h 4 m / słupek oświetleniowy 0,9 m"), ("rack", "stojaki rowerowe U (30 dla gości)"),
             ("bench", "ławki, okrągła ława granitowa przy łuku")]
    for kind, txt in items:
        x, yy = x0, y
        if kind in ("granit", "brick", "lawn", "ogr", "rain"):
            pat = {"granit": "granit", "brick": "brick", "lawn": "lawn", "ogr": "ogr", "rain": "rain"}[kind]
            svg.poly([(x, yy - 1.0), (x + 3.4, yy - 1.0), (x + 3.4, yy + 1.4), (x, yy + 1.4)], fill=f"url(#h_{pat})", stroke=GREY, sw=0.1)
        elif kind == "acc":
            svg.line((x, yy + 0.2), (x + 3.4, yy + 0.2), stroke=ACC, sw=1.0)
        elif kind == "tree_n":
            svg.circle((x + 1.7, yy + 0.2), 1.4, fill="none", stroke=INK, sw=0.18)
        elif kind == "tree_e":
            svg.circle((x + 1.7, yy + 0.2), 1.4, fill="#ffffff", stroke="#6f6a63", sw=0.13)
        elif kind == "tree_x":
            svg.circle((x + 1.7, yy + 0.2), 1.4, fill="none", stroke="#a9a39b", sw=0.12)
            svg.line((x + 1.0, yy - 0.5), (x + 2.4, yy + 0.9), stroke=ACC, sw=0.15)
        elif kind == "lamp":
            svg.circle((x + 1.7, yy + 0.2), 0.9, fill="#ffffff", stroke=INK, sw=0.15)
        elif kind == "rack":
            for i in range(3):
                svg.line((x + 0.6 + i * 1.0, yy - 0.8), (x + 0.6 + i * 1.0, yy + 1.2), stroke=INK, sw=0.14)
        elif kind == "bench":
            svg.poly([(x + 0.3, yy - 0.3), (x + 3.1, yy - 0.3), (x + 3.1, yy + 0.7), (x + 0.3, yy + 0.7)], fill="#ffffff", stroke=INK, sw=0.12)
        svg.text((x + 5.0, yy + 1.0), txt, size=1.7, fill=INK)
        y += 3.4
    return y + 1.0


def terrain_marks(svg, v, lab):
    marks = [((-10.0, 36.0), "skwer 9/2", "119,30–119,49"), ((47.0, 20.0), "Wybrzeże J. Słowackiego", "119,16–119,26"),
             (T.loc(*WF.en(14.2, -3.0)), "brama ogrodowa (chodnik)", "118,70 → 118,90"), ((8.0, -6.0), "dziedziniec przy drzwiach", "119,25, spadek ≤ 4 %")]
    for (u, vv), t1, t2 in marks:
        p = v.pu(u, vv)
        bx = (p[0] - 1.5, p[1] - 2.5, p[0] + 30, p[1] + 3.5)
        if not lab.free(bx):
            continue
        lab.add(bx)
        level_mark(svg, p, t2, t1)


def material_labels(svg, v, lab):
    items = [((-14.0, 38.5), "granit strzegomski płomieniowany"), ((6.0, -24.0), "trawnik · ścieżki z cegły z wykopu"),
             ((-12.0, -10.0), "ogródki przydomowe – zachowane z drzewami")]
    for (u, vv), t in items:
        p = v.pu(u, vv)
        w = Labels.tw(t, 1.8)
        bx = (p[0] - w / 2, p[1] - 2, p[0] + w / 2, p[1] + 1)
        if not lab.free(bx):
            continue
        lab.add(bx)
        svg.text(p, t, size=1.8, anchor="middle", fill=GREY, extra=halo_extra(0.7))


# ----------------------------------------------------------------------------------------------------------------
# ================================================================================================================
# EKSPORT POD PLANSZE (rysunki przycięte 1:1 w 1:200 + wspólne legendy P3/P4/P5)
# ================================================================================================================
PLANSZA = OUT / "plansza"
GROUP = {"1": "low", "2": "low", "3": "low", "4": "low", "D": "low", "5": "tower", "6": "tower", "S": "tower", "ANT": "tower",
         "-1": "m1", "-2": "m2", "P": "P"}
BOARDS = {"P3": ("P", "-1", "-2"), "P4": ("1", "2", "3", "4"), "P5": ("5", "6", "S", "ANT", "D")}
CROP_M = 6.0        # margines [mm]
CROP_T = 9.0        # pas na etykietę kondygnacji [mm]
SEC_PAD = 3.0       # wysunięcie oznaczeń przekrojów poza treść [m]


def draw_sections_crop(svg, v, ext):
    """Przekroje A-A / B-B przycięte do zakresu rysunku (ext = u0, v0, u1, v1 w metrach)."""
    u0, v0, u1, v1 = ext
    for s_ in SECTIONS:
        if s_["a"][0] == s_["b"][0]:            # linia stałego u
            a, b = v.pu(s_["a"][0], v0), v.pu(s_["a"][0], v1)
        else:
            a, b = v.pu(u0, s_["a"][1]), v.pu(u1, s_["a"][1])
        svg.line(a, b, stroke=INK, sw=0.15, extra='stroke-dasharray="6,1.2,1,1.2"')
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        vw = (s_["view"][0], -s_["view"][1])
        for p_, sg in ((a, 1), (b, -1)):
            q = (p_[0] + ux * sg * 6.0, p_[1] + uy * sg * 6.0)
            svg.line(p_, q, stroke=INK, sw=0.7)
            arrow(svg, p_, (p_[0] + vw[0] * 4.5, p_[1] + vw[1] * 4.5), sw=0.35, head=1.6)
            tp = (p_[0] + vw[0] * 6.8 + ux * sg * 2.0, p_[1] + vw[1] * 6.8 + uy * sg * 2.0 + 1.4)
            svg.text(tp, s_["id"], size=3.6, weight=700, anchor="middle", fill=INK, extra=halo_extra(0.8))


def content_bbox_uv(lids):
    """Zakres treści (rzut + osie z bąblami + łańcuchy wymiarowe + skrzydło) w (u, v) dla grupy kondygnacji."""
    pts = []
    for lid in lids:
        g = mp(LV[lid]["plyta"])
        if lid == "D":
            g = unary_union([mp(d["poligon"]) for d in LV["D"].get("dachy", [])])
        b = T.to_local_geom(g).bounds
        pts += [(b[0], b[1]), (b[2], b[3])]
    ua, va = SIATKA["wieza"]["osie_u"], SIATKA["wieza"]["osie_v"]
    U, V = ua[-1], va[-1]
    r = 2.6 / K
    pts += [(ua[0] - 5.5 - r, va[0]), (U + 12.0 + 0.9, va[0]), (ua[0], V + 12.0 + 0.8), (ua[0], -5.5 - r)]
    seg = [T.loc(*p_) for p_ in SPEC["bryly"][2]["obrys_ccw"]]
    pts.append((U, min(vv for u, vv in seg)))
    wing = any(l in ("P", "1", "2", "3", "4", "-1", "D") for l in lids)
    if wing:
        for s_ in (0.0, 57.72):
            for d in (-12.4, 15.6):
                pts.append(T.loc(*WF.en(s_, d)))
        pts += [T.loc(*WF.en(-3.9, 0.0)), T.loc(*WF.en(-3.9, 15.0)), T.loc(*WF.en(0.0, -7.2)), T.loc(*WF.en(57.0, -7.2))]
    us, vs = [p_[0] for p_ in pts], [p_[1] for p_ in pts]
    return (min(us) - SEC_PAD, min(vs) - SEC_PAD, max(us) + SEC_PAD, max(vs) + SEC_PAD)


def group_extent(grp):
    lids = [k for k, g in GROUP.items() if g == grp and k in LV]
    if grp == "P":
        comp = Polygon(SITE["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0)
        b = T.to_local_geom(comp).bounds
        c = content_bbox_uv(["P"])
        return (min(b[0], c[0]), min(b[1], c[1]), max(b[2], c[2]), max(b[3], c[3]))
    return content_bbox_uv(lids)


def short_title(lid):
    if lid == "D":
        return "DACH · attyka wieży " + fz(SPEC["bryly"][0]["dach"]["attyka"]["wzgl"]) + " · skrzydła " + fz(SPEC["bryly"][1]["dach"]["gzyms_attyka"]["wzgl"])
    if lid == "ANT":
        z = SPEC["kondygnacja_sejmiku"]["antresola"]["wzgl"]
        return f"ANTRESOLA KONDYGNACJI SEJMIKU · {fz(z)}"
    z = KOND[lid]["posadzka_wzgl"]
    nm = {"-2": "KONDYGNACJA −2", "-1": "KONDYGNACJA −1", "P": "PARTER Z OTOCZENIEM", "S": "KONDYGNACJA SEJMIKU (S)"}.get(lid, f"KONDYGNACJA {lid}")
    return f"{nm} · {fz(z)} ({fnum(Z0 + z, 2)} m n.p.m.)"


def crop_sheet(lid):
    u0, v0, u1, v1 = group_extent(GROUP[lid])
    W = (u1 - u0) * K + 2 * CROP_M
    H = (v1 - v0) * K + 2 * CROP_M + CROP_T
    svg = Svg(W, H)
    svg.add(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>')
    v = UVView(u0, u1, v0, v1, CROP_M, CROP_M + CROP_T)
    lab = Labels()
    site_clip = Polygon(SITE["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0) if lid == "P" else None
    draw_drawing(svg, v, lid, lab, (0, CROP_T, W, H - CROP_T), site_clip=site_clip,
                 sec_ext=(u0 + SEC_PAD * 0.35, v0 + SEC_PAD * 0.35, u1 - SEC_PAD * 0.35, v1 - SEC_PAD * 0.35))
    svg.text((CROP_M, CROP_M + 4.0), short_title(lid), size=4.0, weight=700, fill=INK, ls=0.15)
    north_arrow(svg, (W - CROP_M - 6.0, CROP_M + 6.5), size=9, rot_deg=north_rot())
    return svg


# ---- legendy wspólne ------------------------------------------------------------------------------------------
LG_W = 290.0
LG_T = 2.0          # wysokość pisma [mm]


def compress_numbers(nums):
    """['DOS.01','DOS.02','DOS.03','DOS.07'] → 'DOS.01–03, 07'."""
    def key(n):
        m = re.match(r"^(.*?)(\d+)([a-z]?)$", n)
        return (m.group(1), int(m.group(2)), m.group(3)) if m else (n, 0, "")
    items = sorted(set(nums), key=lambda n: natural(n))
    out = []
    run = []

    def flush():
        if not run:
            return
        a, b = run[0], run[-1]
        out.append(a if a == b else f"{a}–{re.sub(r'^.*?([0-9]+[a-z]?)$', lambda m: m.group(1), b) if key(a)[0] == key(b)[0] else b}")
    for n in items:
        if run:
            pa, pb = key(run[-1]), key(n)
            cont = False
            if pa[0] == pb[0] and pa[2] == "" and pb[2] == "" and pb[1] == pa[1] + 1:
                cont = True
            if pa[0] == pb[0] and pa[1] == pb[1] and pa[2] and pb[2] and ord(pb[2]) == ord(pa[2]) + 1:
                cont = True
            if not cont:
                flush()
                run = []
        run.append(n)
    flush()
    return ", ".join(out)


def norm_name(nm):
    nm = re.sub(r"\s+–\s+(DOS|DSS|DST|DRA|DGP|DI|CZ|DKD|DZ|GW|KS|DK|DW)$", "", nm)
    nm = re.sub(r"\s+\((skrzydło|głęboki)\)", "", nm)
    nm = re.sub(r"^Podręczny magazyn dokumentacji.*$", "Podręczny magazyn dokumentacji przy elewacji (konwertowalny na pokój)", nm)
    nm = re.sub(r"^WC (damskie|męskie) z kabiną dostępną.*$", "Zespół WC (damskie / męskie) z kabiną dostępną dla OzN", nm)
    nm = re.sub(r"^Dźwig .*$", "Szyb dźwigu (A1, A2 – 1 600 kg; R – ratowniczy/ewakuacyjny; P1, P2 – publiczne; T – os.-tow.; C1)", nm)
    nm = re.sub(r"^Klatka schodowa.*$", "Klatka schodowa obudowana (A, B, C)", nm)
    nm = re.sub(r"^Przedsionek ppoż.*$", "Przedsionek ppoż. z MOE (krzesło ewakuacyjne, interkom EVCS)", nm)
    nm = re.sub(r"^Korytarz.*$", "Korytarz / hol windowy", nm)
    nm = re.sub(r"^Strefa pracy wspólnej.*$", "Strefa pracy wspólnej / budki do rozmów", nm)
    nm = re.sub(r"^Miejsce oczekiwania gości \((\w+)\)$", "Miejsce oczekiwania gości przy gabinetach", nm)
    return nm


def board_entries(lids):
    """Wiersze legendy: (kod, nagłówek bloku, [(numery, opis, m²)])."""
    rooms = [(lid, r) for lid in lids for r in LV[lid]["pomieszczenia"] if r["numer"] and (r["kind"] != "roof" or lid == "D")]
    blocks = {}
    for lid, r in rooms:
        k = r["kod_grupy"]
        blocks.setdefault(k, []).append((lid, r))
    order = ["SWD", "SW", "SK", "KS", "DK", "DW", "DOS", "DI", "DST", "DGP", "GW", "CZ", "DKD", "DZ", "DSS", "DRA",
             "SN", "PS", "PP", "PHS", "PR", "PPT", "IT", "PPM", "KW", "DACH"]
    out = []
    for k in sorted(blocks, key=lambda c: order.index(c) if c in order else 99):
        lst = blocks[k]
        head = DEPT_NAMES.get(k, {"KW": "Komunikacja wewnętrzna", "DACH": "Dach"}.get(k, k))
        rows = {}
        if k in ("DOS", "DI", "DST", "DGP", "GW", "CZ", "DKD", "DZ", "DSS", "DRA", "DK", "DW", "KS"):
            for lid, r in lst:
                if r["kind"] == "office" and r.get("komorka"):
                    key = ("office", r["komorka"])
                    kom = re.sub(r"^[^–]*–\s*", "", r["nazwa"])
                    rows.setdefault(key, [kom, [], [], []])
                    typ = r["nazwa"].split(" – ")[0].replace(" (3 st.)", " 3-os.").replace(" (4 st.)", " 4-os.")
                    if typ not in rows[key][3]:
                        rows[key][3].append(typ)
                else:
                    key = ("x", norm_name(r["nazwa"]))
                    rows.setdefault(key, [norm_name(r["nazwa"]), [], [], []])
                rows[key][1].append(r["numer"])
                rows[key][2].append(r["powierzchnia"])
        else:
            for lid, r in lst:
                nm = norm_name(r["nazwa"])
                key = ("x", nm)
                rows.setdefault(key, [nm, [], [], []])
                rows[key][1].append(r["numer"])
                rows[key][2].append(r["powierzchnia"])
        ent = []
        for key, (nm, nums, ars, typs) in rows.items():
            if k == "KW":
                nums_s = compress_numbers(nums) if len(nums) < 6 else f"KW.<kond.>.nn ({len(nums)} poz.)"
            else:
                nums_s = compress_numbers(nums)
            if key[0] == "office":
                tt = ", ".join(t_[0].lower() + t_[1:] for t_ in typs if t_)
                desc = f"{nm}: {tt}" if tt else nm
            else:
                desc = nm
            if len(ars) == 1:
                ar = fnum(ars[0])
            elif max(ars) - min(ars) < 0.6:
                ar = f"{len(ars)} × {fnum(sum(ars) / len(ars))}"
            else:
                ar = f"Σ {fnum(sum(ars))}"
            ent.append((nums_s, desc, ar))
        ent.sort(key=lambda e: natural(e[0]))
        out.append((k, head, ent))
    return out


def legend_board(name, lids):
    entries = board_entries(lids)
    t = LG_T
    lh = t * 1.32
    col_gap = 6.0
    ncol = 2
    cw = (LG_W - (ncol - 1) * col_gap) / ncol
    num_w = 30.0
    ar_w = 17.0
    nchar = int((cw - num_w - ar_w) / (t * 0.53))
    # wysokość bloków
    blocks = []
    for k, head, ent in entries:
        lines = [("head", f"{k} – {head}")]
        for nums, desc, ar in ent:
            dl = wrap(desc, nchar)
            nl = wrap(nums, int(num_w / (t * 0.56)))
            for i in range(max(len(dl), len(nl))):
                lines.append(("row", nl[i] if i < len(nl) else "", dl[i] if i < len(dl) else "", ar if i == 0 else ""))
        blocks.append(lines)
    total_lines = sum(len(b) + 0.6 for b in blocks)
    per_col = total_lines / ncol
    svg = Svg(LG_W, 2000)
    svg.add('<rect x="0" y="0" width="100%" height="100%" fill="#ffffff"/>')
    y0 = 6.0
    titles = {"P3": "PLANSZA P3 · PARTER Z OTOCZENIEM, KONDYGNACJE −1 I −2", "P4": "PLANSZA P4 · KONDYGNACJE 1–4",
              "P5": "PLANSZA P5 · KONDYGNACJE 5, 6, SEJMIKU, ANTRESOLA, DACH"}
    svg.text((0, y0), "LEGENDA – " + titles.get(name, name), size=3.2, weight=700, fill=INK, ls=0.15)
    svg.text((0, y0 + 4.6), "numer pomieszczenia = kod grupy (Wyj. 20 odp. 73) + nr kolejny; na rzutach numer i pow. netto [m²] wg PN-ISO 9836; "
             "przy pokojach biurowych nr komórki z tabeli 1 M.01", size=t, fill=GREY)
    y = y0 + 9.5
    col, cy = 0, y
    used = 0
    ymax = y
    for lines in blocks:
        if used + len(lines) * 0.5 > per_col and col < ncol - 1:
            col += 1
            cy = y
            used = 0
        x = col * (cw + col_gap)
        for ln in lines:
            if ln[0] == "head":
                cy += 1.0
                svg.text((x, cy + t), ln[1].upper(), size=t, weight=700, fill=ACC if ln[1].split()[0] in PUBLIC else INK, ls=0.08)
                cy += lh + 0.3
            else:
                _, nums, desc, ar = ln
                svg.text((x, cy + t), nums, size=t, weight=600, fill=INK)
                svg.text((x + num_w, cy + t), desc, size=t, fill=INK)
                svg.text((x + cw, cy + t), ar, size=t, anchor="end", fill=GREY)
                cy += lh
        used += len(lines) + 0.6
        ymax = max(ymax, cy)
    y = ymax + 5.0
    # oznaczenia
    svg.text((0, y + t), "OZNACZENIA", size=2.4, weight=700, fill=INK)
    y += 5.0
    sym = [("wc", "WC z kabiną / toaletą dostępną dla OzN; komfortka (parter)"), ("moe", "miejsce oczekiwania na ewakuację w przedsionku ppoż."),
           ("loop", "pętla indukcyjna"), ("lvl", f"rzędna posadzki (±0,00 = {fnum(Z0, 2)} m n.p.m.)"), ("sec", "przekrój i kierunek widoku")]
    if "P" in lids:
        sym += [("tyflo", "tyflomapa"), ("fon", "ścieżka dotykowa (FON)"), ("ent", "wejście (w poziomie chodnika)"),
                ("tree_n", "drzewo projektowane"), ("tree_e", "drzewo istniejące / usuwane (×)"), ("lamp", "latarnia / słupek oświetleniowy"),
                ("rack", "stojaki rowerowe"), ("bound", "granica opracowania konkursowego")]
    if "-1" in lids or "-2" in lids:
        sym += [("ozn", "stanowisko OzN 3,6 × 5,0 m"), ("stall", "stanowisko 2,5 × 5,0 m (nr), droga manewrowa 6,0 m"), ("ramp", "rampa (spadek ≤ 18 %)")]
    if "D" in lids:
        sym += [("bipv", "BIPV szkło-szkło jako pokrycie"), ("green", "taras – dach zielony"), ("drain", "wpust dachowy, spadek 1,5 %")]
    if "P" in lids:
        sym += [("granit", "granit strzegomski płomieniowany"), ("brick", "ścieżki z cegły i gruzu z wykopu"), ("lawn", "trawnik"),
                ("rain", "ogród deszczowy (retencja)"), ("acc", "ślad pierzei 1934 r. (granit + brąz)")]
    per = 3
    cwid = LG_W / per
    for i, (kind, txt) in enumerate(sym):
        cx, cyy = (i % per) * cwid, y + (i // per) * 4.4
        c = (cx + 1.8, cyy + 0.6)
        if kind == "wc":
            icon_wheelchair(svg, c, 2.6)
        elif kind == "moe":
            icon_moe(svg, c, 2.8)
        elif kind == "loop":
            icon_loop(svg, c, 2.6)
        elif kind == "tyflo":
            icon_tyflo(svg, c, 2.6)
        elif kind == "ozn":
            icon_wheelchair(svg, c, 2.6, color="#2b5b84")
        elif kind == "lvl":
            level_mark(svg, c, "")
        elif kind == "sec":
            svg.text((c[0], c[1] + 1.2), "A", size=3.2, weight=700, anchor="middle")
        elif kind == "fon":
            svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke="#6f6a63", sw=0.6, extra='stroke-dasharray="0.35,0.35"')
        elif kind == "ent":
            svg.circle(c, 1.6, fill=ACC, stroke="none")
        elif kind == "tree_n":
            svg.circle(c, 1.5, fill="none", stroke=INK, sw=0.18)
        elif kind == "tree_e":
            svg.circle(c, 1.5, fill="#ffffff", stroke="#6f6a63", sw=0.13)
        elif kind == "lamp":
            svg.circle(c, 0.9, fill="#ffffff", stroke=INK, sw=0.15)
            svg.line((c[0] - 0.9, c[1]), (c[0] + 0.9, c[1]), stroke=INK, sw=0.1)
        elif kind == "rack":
            for j in range(3):
                svg.line((cx + 0.6 + j, c[1] - 1.0), (cx + 0.6 + j, c[1] + 1.0), stroke=INK, sw=0.14)
        elif kind == "bound":
            svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke="#2f6f8f", sw=0.3, extra='stroke-dasharray="1.6,0.6"')
        elif kind == "stall":
            svg.poly([(cx + 0.4, c[1] - 1.2), (cx + 3.0, c[1] - 1.2), (cx + 3.0, c[1] + 1.2), (cx + 0.4, c[1] + 1.2)], fill="#ffffff", stroke=GREY, sw=0.1)
        elif kind in ("ramp", "granit", "brick", "lawn", "rain", "bipv", "green"):
            pat = {"ramp": svg.hatch("ramp", 1.2, 45, HAIR, 0.08), "granit": svg.hatch("granit", 1.5, 0, "#d8d4ce", 0.06, bg="#f6f5f2"),
                   "brick": svg.hatch("brick", 0.8, 90, "#c9bfb4", 0.07, bg="#f3efea"), "lawn": svg.hatch("lawn", 0.9, 30, "#d9ddd2", 0.05, bg="#fbfbf9"),
                   "rain": svg.hatch("rain", 0.7, 0, "#b9c4c6", 0.06, bg="#f1f4f4"), "bipv": "#f4f3f1",
                   "green": svg.hatch("green", 0.8, 60, "#9aa58e", 0.08, bg="#f2f4ef")}[kind]
            svg.poly([(cx, c[1] - 1.2), (cx + 3.6, c[1] - 1.2), (cx + 3.6, c[1] + 1.2), (cx, c[1] + 1.2)], fill=pat, stroke=GREY, sw=0.1)
        elif kind == "acc":
            svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke=ACC, sw=1.0)
        elif kind == "drain":
            svg.circle(c, 0.9, fill="#ffffff", stroke=INK, sw=0.15)
            svg.circle(c, 0.35, fill=INK, stroke="none")
        svg.text((cx + 5.2, cyy + 1.3), txt, size=t, fill=INK)
    y += ((len(sym) + per - 1) // per) * 4.4 + 4.0
    # bilans powierzchni per kondygnacja wg kodów
    svg.text((0, y + t), "BILANS POWIERZCHNI NETTO WG KODÓW GRUP [m²]", size=2.4, weight=700, fill=INK)
    y += 5.0
    codes = {}
    for lid in lids:
        for r in LV[lid]["pomieszczenia"]:
            if r["kind"] == "roof" and lid != "D":
                continue
            codes.setdefault(r["kod_grupy"], {}).setdefault(lid, 0.0)
            codes[r["kod_grupy"]][lid] += r["powierzchnia"]
    order = ["SWD", "SW", "SK", "KS", "DK", "DW", "DOS", "DI", "DST", "DGP", "GW", "CZ", "DKD", "DZ", "DSS", "DRA",
             "SN", "PS", "PP", "PHS", "PR", "PPT", "IT", "PPM", "KW", "DACH"]
    cl = sorted(codes, key=lambda c: order.index(c) if c in order else 99)
    hdr = {"-2": "−2", "-1": "−1", "P": "P", "ANT": "antr.", "D": "dach"}
    colw = min(28.0, (LG_W - 24) / (len(lids) + 1))
    svg.text((0, y + t), "kod", size=t, weight=700, fill=INK)
    for j, lid in enumerate(lids):
        svg.text((24 + (j + 1) * colw, y + t), hdr.get(lid, lid), size=t, weight=700, anchor="end", fill=INK)
    svg.text((24 + (len(lids) + 1) * colw, y + t), "razem", size=t, weight=700, anchor="end", fill=INK)
    y += lh + 0.4
    svg.line((0, y), (24 + (len(lids) + 1) * colw, y), stroke=GREY, sw=0.12)
    y += 0.6
    tots = {lid: 0.0 for lid in lids}
    for c in cl:
        svg.text((0, y + t), c, size=t, weight=600, fill=ACC if c in PUBLIC else INK)
        rs = 0.0
        for j, lid in enumerate(lids):
            a = codes[c].get(lid, 0.0)
            tots[lid] += a
            rs += a
            if a:
                svg.text((24 + (j + 1) * colw, y + t), fnum(a), size=t, anchor="end", fill=INK)
        svg.text((24 + (len(lids) + 1) * colw, y + t), fnum(rs), size=t, anchor="end", fill=GREY)
        y += lh
    svg.line((0, y + 0.2), (24 + (len(lids) + 1) * colw, y + 0.2), stroke=GREY, sw=0.12)
    y += 0.8
    svg.text((0, y + t), "razem", size=t, weight=700, fill=INK)
    for j, lid in enumerate(lids):
        svg.text((24 + (j + 1) * colw, y + t), fnum(tots[lid]), size=t, weight=700, anchor="end", fill=INK)
    svg.text((24 + (len(lids) + 1) * colw, y + t), fnum(sum(tots.values())), size=t, weight=700, anchor="end", fill=INK)
    y += lh + 3.0
    svg.h_mm = y
    return svg


def export_boards(ids=None):
    PLANSZA.mkdir(parents=True, exist_ok=True)
    order = ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT", "D"]
    sizes = []
    for lid in (ids or order):
        if lid not in LV:
            continue
        svg = crop_sheet(lid)
        fn = PLANSZA / f"rzut_{FILE_ID[lid]}_1-200_crop.svg"
        fn.write_text(svg.render(), encoding="utf-8")
        sizes.append((fn.name, svg.w_mm, svg.h_mm))
        print(f"{fn.relative_to(ROOT)}  {svg.w_mm:.1f} × {svg.h_mm:.1f} mm", flush=True)
    for name, lids in BOARDS.items():
        if ids and not any(l in ids for l in lids):
            continue
        svg = legend_board(name, [l for l in lids if l in LV])
        fn = PLANSZA / f"legenda_{name}.svg"
        fn.write_text(svg.render(), encoding="utf-8")
        sizes.append((fn.name, svg.w_mm, svg.h_mm))
        print(f"{fn.relative_to(ROOT)}  {svg.w_mm:.1f} × {svg.h_mm:.1f} mm", flush=True)
    (PLANSZA / "rozmiary.json").write_text(json.dumps([dict(plik=a, szer_mm=round(b, 1), wys_mm=round(c, 1)) for a, b, c in sizes],
                                                     ensure_ascii=False, indent=1), encoding="utf-8")
    return sizes


# ================================================================================================================
# WARIANT CIASNY POD PLANSZE (--plansza-ciasna): osie i łańcuchy tylko u góry i z lewej, margines 2 mm
# ================================================================================================================
TB = 5.5            # pas osi/łańcucha [mm] od obrysu
TM = 2.0            # margines [mm]
SEC_T = 1.5         # wysunięcie przekroju poza obrys [m]
LIMITS = {"low": (376, 316), "tower": (216, 166), "m2": (255, 255), "P": (530, 520), "m1": (376, 316)}
GROUP_T = {"1": "low", "2": "low", "3": "low", "4": "low", "D": "low", "-1": "low", "5": "tower", "6": "tower", "S": "tower",
           "ANT": "tower", "-2": "m2", "P": "P"}


def plate_uv(lid):
    if lid == "D":
        return T.to_local_geom(unary_union([mp(d["poligon"]) for d in LV["D"].get("dachy", [])]))
    return T.to_local_geom(mp(LV[lid]["plyta"]))


def has_segment(lid):
    pu = plate_uv(lid)
    return pu.bounds[1] < -3.0


def chain_v_points(lid):
    pts = list(SIATKA["wieza"]["osie_v"])
    if has_segment(lid):
        seg = [T.loc(*p_) for p_ in SPEC["bryly"][2]["obrys_ccw"]]
        pts = [min(vv for u, vv in seg)] + pts
    return pts


def left_chain_u(lids):
    """Położenie lewego łańcucha (u, m): na lewo od obrysu w całym zakresie v łańcucha."""
    vmin = min(chain_v_points(l)[0] for l in lids)
    vmax = SIATKA["wieza"]["osie_v"][-1]
    xs = []
    for l in lids:
        pu = plate_uv(l)
        for k in range(41):
            vv = vmin + (vmax - vmin) * k / 40
            ln = LineString([(-80, vv), (80, vv)]).intersection(pu)
            if not ln.is_empty:
                xs.append(ln.bounds[0])
    return (min(xs) if xs else 0.0) - 1.0 / K


def section_ends(lid, s_):
    """Końce linii przekroju: 1,5 m poza obrysem, ale nie dalej niż pasy osi (lewy / górny)."""
    pu = plate_uv(lid)
    grp = GROUP_T[lid]
    lids = [k for k, g in GROUP_T.items() if g == grp and k in LV]
    u_lim = left_chain_u(lids) - (TB - 1.0) / K
    v_lim = SIATKA["wieza"]["osie_v"][-1] + TB / K
    if s_["a"][0] == s_["b"][0]:
        ln = LineString([(s_["a"][0], -80), (s_["a"][0], 80)]).intersection(pu)
        b = ln.bounds
        return (s_["a"][0], b[1] - SEC_T), (s_["a"][0], min(b[3] + SEC_T, v_lim))
    ln = LineString([(-80, s_["a"][1]), (80, s_["a"][1])]).intersection(pu)
    b = ln.bounds
    return (max(b[0] - SEC_T, u_lim), s_["a"][1]), (b[2] + SEC_T, s_["a"][1])


def tight_extent(grp):
    lids = [k for k, g in GROUP_T.items() if g == grp and k in LV]
    us, vs = [], []
    for l in lids:
        b = plate_uv(l).bounds
        us += [b[0], b[2]]
        vs += [b[1], b[3]]
        for s_ in SECTIONS:
            a, c = section_ends(l, s_)
            us += [a[0], c[0]]
            vs += [a[1], c[1]]
    ua = SIATKA["wieza"]["osie_u"]
    vtop = SIATKA["wieza"]["osie_v"][-1]
    vs.append(vtop + TB / K)
    uc = left_chain_u(lids)
    us.append(uc - (TB - 1.0) / K)
    if grp == "P":
        comp = T.to_local_geom(Polygon(SITE["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0)).bounds
        us += [comp[0], comp[2]]
        vs += [comp[1], comp[3]]
    return (min(us), min(vs), max(us), max(vs))


def draw_axes_dims_tight(svg, v, lid):
    grp = GROUP_T[lid]
    lids = [k for k, g in GROUP_T.items() if g == grp and k in LV]
    ua = SIATKA["wieza"]["osie_u"]
    va = SIATKA["wieza"]["osie_v"]
    vtop = va[-1]
    dash = 'stroke-dasharray="3,0.7,0.5,0.7"'
    rb = 1.3
    # --- góra: łańcuch osi u + bąble
    y_line = v.pu(0, vtop)[1] - 1.0
    y_bub = v.pu(0, vtop)[1] - (TB - rb)
    pu = plate_uv(lid)
    for u in ua:
        ln = LineString([(u, -80), (u, 80)]).intersection(pu)
        vb = ln.bounds[1] if not ln.is_empty else 0.0
        svg.line(v.pu(u, vb - 0.8), (v.pu(u, 0)[0], y_bub + rb), stroke=GREY, sw=0.08, extra=dash)
        axis_bubble(svg, (v.pu(u, 0)[0], y_bub), str(ua.index(u) + 1), r=rb, size=1.9, sw=0.15)
    x0, x1 = v.pu(ua[0], 0)[0], v.pu(ua[-1], 0)[0]
    labels = [fnum(b - a, 2) for a, b in zip(ua[:-1], ua[1:])]
    labels[-1] = labels[-1] + " · Σ " + fnum(ua[-1] - ua[0], 2)
    dim_chain(svg, (x0, y_line), (x1, y_line), [(x - ua[0]) / (ua[-1] - ua[0]) for x in ua], (0, -1), labels, size=1.8, ext=0.6)
    # --- lewo: łańcuch osi v (+ lico pd. segmentu) + bąble
    uc = left_chain_u(lids)
    x_line = v.pu(uc, 0)[0]
    x_bub = x_line - (TB - 1.0 - rb)
    pts = chain_v_points(lid)
    for vv in va:
        ln = LineString([(-80, vv), (80, vv)]).intersection(pu)
        ub = ln.bounds[2] if not ln.is_empty else ua[-1]
        ul = ln.bounds[0] if not ln.is_empty else 0.0
        svg.line((x_bub + rb, v.pu(0, vv)[1]), v.pu(ul - 0.3, vv), stroke=GREY, sw=0.08, extra=dash)
        svg.line(v.pu(max(ul, ua[0]) - 0.3, vv), v.pu(ub + 0.8, vv), stroke=GREY, sw=0.08, extra=dash)
        axis_bubble(svg, (x_bub, v.pu(0, vv)[1]), chr(ord("A") + va.index(vv)), r=rb, size=1.9, sw=0.15)
    y0, y1 = v.pu(0, pts[0])[1], v.pu(0, pts[-1])[1]
    labs = [fnum(b - a, 2) for a, b in zip(pts[:-1], pts[1:])]
    labs[-1] = labs[-1] + " · Σ " + fnum(pts[-1] - pts[0], 2)
    dim_chain(svg, (x_line, y0), (x_line, y1), [(x - pts[0]) / (pts[-1] - pts[0]) for x in pts], (-1, 0), labs, size=1.8, ext=0.6)
    if pts[0] < va[0] - 0.5:
        # linia odniesienia lica pd. segmentu
        ln = LineString([(-80, pts[0] + 0.05), (80, pts[0] + 0.05)]).intersection(pu)
        if not ln.is_empty:
            svg.line((x_line - 0.6, y0), v.pu(ln.bounds[0], pts[0]), stroke=HAIR, sw=0.06, extra='stroke-dasharray="0.6,0.6"')


def draw_sections_tight(svg, v, lid):
    for s_ in SECTIONS:
        a, b = section_ends(lid, s_)
        pa, pb = v.pu(*a), v.pu(*b)
        svg.line(pa, pb, stroke=INK, sw=0.13, extra='stroke-dasharray="5,1,0.8,1"')
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        vw = (s_["view"][0], -s_["view"][1])
        for p_, sg in ((pa, 1), (pb, -1)):
            q = (p_[0] + ux * sg * 4.0, p_[1] + uy * sg * 4.0)
            svg.line(p_, q, stroke=INK, sw=0.6)
            o = (p_[0] + ux * sg * 0.7, p_[1] + uy * sg * 0.7)
            arrow(svg, o, (o[0] + vw[0] * 3.2, o[1] + vw[1] * 3.2), sw=0.3, head=1.3)
            tp = (p_[0] + ux * sg * 3.0 + vw[0] * 2.2, p_[1] + uy * sg * 3.0 + vw[1] * 2.2 + 1.1)
            svg.text(tp, s_["id"], size=3.0, weight=700, anchor="middle", fill=INK, extra=halo_extra(0.7))


def block_names_inside(svg, v, lv, lab):
    """Nazwy bloków (działów) w korytarzu przy grupie pokoi – tekst wzdłuż korytarza."""
    corr = unary_union([mp(r["poligon"]) for r in lv["pomieszczenia"] if r["kind"] == "corridor"])
    groups = {}
    for r in lv["pomieszczenia"]:
        if r["kind"] == "office" and r["kod_grupy"] not in ("KW",):
            groups.setdefault(r["kod_grupy"], []).append(mp(r["poligon"]))
    for code, gs in groups.items():
        zone = corr.intersection(unary_union(gs).buffer(2.6))
        parts = sorted(polys(zone), key=lambda p_: -p_.area)
        txt = f"{code} – {DEPT_NAMES.get(code, code).upper()}"
        for part in parts[:3]:
            mrr = part.minimum_rotated_rectangle
            cs = list(mrr.exterior.coords)[:4]
            e1 = (cs[1][0] - cs[0][0], cs[1][1] - cs[0][1])
            e2 = (cs[2][0] - cs[1][0], cs[2][1] - cs[1][1])
            ax_ = e1 if math.hypot(*e1) >= math.hypot(*e2) else e2
            Lm = max(math.hypot(*e1), math.hypot(*e2))
            wtxt = Labels.tw(txt, 1.9, True) + 1.0
            if Lm * K < wtxt:
                continue
            c = part.representative_point()
            p_ = v.p(c.x, c.y)
            d = v.dir(ax_)
            ang = math.degrees(math.atan2(d[1], d[0]))
            if ang > 90:
                ang -= 180
            if ang < -90:
                ang += 180
            hw = abs(math.cos(math.radians(ang))) * wtxt / 2 + 1.2
            hh = abs(math.sin(math.radians(ang))) * wtxt / 2 + 1.2
            bx = (p_[0] - hw, p_[1] - hh, p_[0] + hw, p_[1] + hh)
            if not lab.free(bx) and abs(ang) > 10 and abs(ang) < 80:
                continue
            if not lab.free(bx) and (abs(ang) <= 10 or abs(ang) >= 80):
                continue
            lab.add(bx)
            svg.text((p_[0], p_[1] + 0.7), txt, size=1.9, anchor="middle", weight=700, fill=ACC if code == "KS" else INK, rot=ang, ls=0.1,
                     extra=halo_extra(0.8))
            break


def tight_sheet(lid):
    grp = GROUP_T[lid]
    u0, v0, u1, v1 = tight_extent(grp)
    W = (u1 - u0) * K + 2 * TM
    H = (v1 - v0) * K + 2 * TM
    svg = Svg(W, H)
    svg.add(f'<rect x="0" y="0" width="{W:.2f}" height="{H:.2f}" fill="#ffffff"/>')
    v = UVView(u0, u1, v0, v1, TM, TM)
    lab = Labels()
    CFG.update(tight=True, bounds=(0.5, 0.5, W - 0.5, H - 0.5), s1=2.0, s2=2.0)
    site_clip = Polygon(SITE["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0) if lid == "P" else None
    try:
        draw_drawing(svg, v, lid, lab, (0, 0, W, H), site_clip=site_clip)
    finally:
        CFG.update(tight=False, bounds=None, s1=1.75, s2=1.6)
    # etykieta kondygnacji i strzałka północy w wolnych narożnikach
    t = short_title(lid)
    vtop = SIATKA["wieza"]["osie_v"][-1]
    if grp in ("low", "P"):
        svg.text((TM + 0.5, TM + 3.4), t, size=3.0, weight=700, fill=INK, ls=0.1, extra=halo_extra(0.8))
        if grp == "P":
            north_arrow(svg, (W - TM - 4.5, TM + 5.0), size=7.5, rot_deg=north_rot())
        else:
            north_arrow(svg, v.pu(36.4, 28.2), size=6.0, rot_deg=north_rot())
    else:
        a, b = t.split(" · ", 1) if " · " in t else (t, "")
        p0 = v.pu(34.0, vtop - 0.55)
        svg.text(p0, a, size=2.4, weight=700, fill=INK, extra=halo_extra(0.8))
        svg.text((p0[0], p0[1] + 2.9), b, size=2.0, fill=INK, extra=halo_extra(0.8))
        north_arrow(svg, v.pu(38.3, 24.6), size=5.6, rot_deg=north_rot())
    return svg


# ---- legendy: układ przepływowy (wąska P4, pas P3) ------------------------------------------------------------
def legend_flow(name, lids, width, t_head=2.0, t_row=1.8, max_h=None, ncol_try=(1,), title_sz=2.6):
    entries = board_entries(lids)
    lh = t_row * 1.30
    gap = 4.0
    best = None
    for ncol in ncol_try:
        cw = (width - (ncol - 1) * gap) / ncol
        num_w = min(30.0, max(22.0, cw * 0.18))
        ar_w = 15.0
        nchar = max(20, int((cw - num_w - ar_w) / (t_row * 0.53)))
        blocks = []
        for k, head, ent in entries:
            lines = [("head", f"{k} – {head}", t_head * 1.4 + 0.6)]
            for nums, desc, ar in ent:
                dl = wrap(desc, nchar)
                nl = wrap(nums, int(num_w / (t_row * 0.57)))
                for i in range(max(len(dl), len(nl))):
                    lines.append(("row", (nl[i] if i < len(nl) else "", dl[i] if i < len(dl) else "", ar if i == 0 else ""), lh))
            blocks.append(lines)
        # oznaczenia
        sym = symbol_list(lids)
        sl = [("head", "OZNACZENIA", t_head * 1.4 + 0.6)] + [("sym", sy, max(lh, 3.0) * (len(wrap(sy[1], nchar + 8)))) for sy in sym]
        blocks.append(sl)
        # bilans
        tl = [("head", "BILANS POW. NETTO [m²]", t_head * 1.4 + 0.6), ("thead", None, lh + 0.6)]
        codes = balance(lids)
        for c in codes:
            tl.append(("trow", c, lh))
        tl.append(("ttot", None, lh + 0.8))
        blocks.append(tl)
        # rozkład w kolumnach (przepływ wierszami; nagłówek nie zostaje sam na dole kolumny)
        top = title_sz * 1.4 + 4.5
        cols = [[] for _ in range(ncol)]
        hcol = [0.0] * ncol
        total = sum(sum(x[2] for x in b) + 1.2 for b in blocks)
        cap = (max_h - top - 2.0) if (max_h and ncol > 1) else total / ncol * 1.02
        ci = 0
        for b in blocks:
            cur = []
            keep = b[0][1] in ("OZNACZENIA", "BILANS POW. NETTO [m²]")
            hb = sum(x[2] for x in b)
            if keep and hcol[ci] > 0 and hcol[ci] + hb > cap and ci < ncol - 1:
                ci += 1
            for li, ln in enumerate(b):
                if keep:
                    cur.append(ln)
                    hcol[ci] += ln[2]
                    continue
                nxt = b[li + 1][2] if (ln[0] == "head" and li + 1 < len(b)) else 0.0
                if hcol[ci] + ln[2] + nxt > cap and ci < ncol - 1 and hcol[ci] > 0:
                    if cur:
                        cols[ci].append(cur)
                    cur = []
                    ci += 1
                cur.append(ln)
                hcol[ci] += ln[2]
            if cur:
                cols[ci].append(cur)
            hcol[ci] += 1.2
        H = top + max(hcol) + 2.0
        if best is None or (max_h and best[0] > max_h and H < best[0]) or (max_h and H <= max_h and best[0] > max_h):
            best = (H, ncol, cols, cw, num_w, ar_w, nchar, top)
        if max_h is None or H <= max_h:
            best = (H, ncol, cols, cw, num_w, ar_w, nchar, top)
            break
    H, ncol, cols, cw, num_w, ar_w, nchar, top = best
    svg = Svg(width, H)
    svg.add(f'<rect x="0" y="0" width="{width:.2f}" height="{H:.2f}" fill="#ffffff"/>')
    titles = {"P3": "LEGENDA – PLANSZA P3 · PARTER Z OTOCZENIEM, KONDYGNACJE −1 I −2", "P4": "LEGENDA – PLANSZA P4 · KONDYGNACJE 1–4",
              "P5": "LEGENDA – PLANSZA P5 · 5, 6, S, ANTRESOLA, DACH"}
    svg.text((0, title_sz + 0.4), titles.get(name, name), size=title_sz, weight=700, fill=INK, ls=0.1)
    svg.text((0, title_sz + 3.6), "nr = kod grupy (Wyj. 20 odp. 73) + nr kolejny; na rzutach nr i pow. netto [m²] (PN-ISO 9836); biura z nr komórki (tab. 1 M.01)",
             size=t_row, fill=GREY)
    hdr = {"-2": "−2", "-1": "−1", "P": "P", "ANT": "antr.", "D": "dach"}
    codes = balance(lids)
    for ci, col in enumerate(cols):
        x = ci * (cw + gap)
        y = top
        for b in col:
            for kind, data, hgt in b:
                if kind == "head":
                    svg.text((x, y + t_head + 0.5), data.upper(), size=t_head, weight=700, fill=ACC if data.split()[0] in PUBLIC else INK, ls=0.06)
                elif kind == "row":
                    nums, desc, ar = data
                    svg.text((x, y + t_row), nums, size=t_row, weight=600, fill=INK)
                    svg.text((x + num_w, y + t_row), desc, size=t_row, fill=INK)
                    svg.text((x + cw, y + t_row), ar, size=t_row, anchor="end", fill=GREY)
                elif kind == "sym":
                    draw_symbol(svg, (x + 1.8, y + 1.2), data[0])
                    for i, ln in enumerate(wrap(data[1], nchar + 8)):
                        svg.text((x + 5.0, y + t_row + 0.3 + i * lh), ln, size=t_row, fill=INK)
                elif kind in ("thead", "trow", "ttot"):
                    cwid = min(15.0, (cw - 12) / (len(lids) + 1))
                    if kind == "thead":
                        svg.text((x, y + t_row), "kod", size=t_row, weight=700)
                        for j, l in enumerate(lids):
                            svg.text((x + 12 + (j + 1) * cwid, y + t_row), hdr.get(l, l), size=t_row, weight=700, anchor="end")
                        svg.text((x + 12 + (len(lids) + 1) * cwid, y + t_row), "razem", size=t_row, weight=700, anchor="end")
                        svg.line((x, y + hgt - 0.2), (x + 12 + (len(lids) + 1) * cwid, y + hgt - 0.2), stroke=GREY, sw=0.1)
                    elif kind == "trow":
                        c = data
                        svg.text((x, y + t_row), c, size=t_row, weight=600, fill=ACC if c in PUBLIC else INK)
                        rs = 0.0
                        for j, l in enumerate(lids):
                            a = codes[c].get(l, 0.0)
                            rs += a
                            if a:
                                svg.text((x + 12 + (j + 1) * cwid, y + t_row), fnum(a), size=t_row, anchor="end")
                        svg.text((x + 12 + (len(lids) + 1) * cwid, y + t_row), fnum(rs), size=t_row, anchor="end", fill=GREY)
                    else:
                        svg.line((x, y + 0.2), (x + 12 + (len(lids) + 1) * cwid, y + 0.2), stroke=GREY, sw=0.1)
                        svg.text((x, y + t_row + 0.6), "razem", size=t_row, weight=700)
                        tt = 0.0
                        for j, l in enumerate(lids):
                            a = sum(codes[c].get(l, 0.0) for c in codes)
                            tt += a
                            svg.text((x + 12 + (j + 1) * cwid, y + t_row + 0.6), fnum(a), size=t_row, weight=700, anchor="end")
                        svg.text((x + 12 + (len(lids) + 1) * cwid, y + t_row + 0.6), fnum(tt), size=t_row, weight=700, anchor="end")
                y += hgt
            y += 1.2
    return svg


def balance(lids):
    codes = {}
    for lid in lids:
        for r in LV[lid]["pomieszczenia"]:
            if r["kind"] == "roof" and lid != "D":
                continue
            codes.setdefault(r["kod_grupy"], {}).setdefault(lid, 0.0)
            codes[r["kod_grupy"]][lid] += r["powierzchnia"]
    order = ["SWD", "SW", "SK", "KS", "DK", "DW", "DOS", "DI", "DST", "DGP", "GW", "CZ", "DKD", "DZ", "DSS", "DRA",
             "SN", "PS", "PP", "PHS", "PR", "PPT", "IT", "PPM", "KW", "DACH"]
    return {c: codes[c] for c in sorted(codes, key=lambda c: order.index(c) if c in order else 99)}


def symbol_list(lids):
    sym = [("wc", "WC z kabiną / toaletą dostępną dla OzN; komfortka (parter)"), ("moe", "miejsce oczekiwania na ewakuację (MOE) w przedsionku ppoż."),
           ("loop", "pętla indukcyjna"), ("lvl", f"rzędna posadzki (±0,00 = {fnum(Z0, 2)} m n.p.m.)"), ("sec", "przekrój i kierunek widoku")]
    if "P" in lids:
        sym += [("tyflo", "tyflomapa"), ("fon", "ścieżka dotykowa (FON)"), ("ent", "wejście (w poziomie chodnika)"),
                ("tree_n", "drzewo projektowane"), ("tree_e", "drzewo istniejące (nr wg M.06); × – do usunięcia"),
                ("lamp", "latarnia / słupek oświetleniowy"), ("rack", "stojaki rowerowe"), ("bound", "granica opracowania konkursowego"),
                ("granit", "granit strzegomski płomieniowany"), ("brick", "ścieżki z cegły i gruzu z wykopu"), ("lawn", "trawnik"),
                ("rain", "ogród deszczowy (retencja)"), ("acc", "ślad pierzei 1934 r. (granit + listwa z brązu)")]
    if "-1" in lids or "-2" in lids:
        sym += [("ozn", "stanowisko OzN 3,6 × 5,0 m"), ("stall", "stanowisko 2,5 × 5,0 m (nr), droga 6,0 m"), ("ramp", "rampa (≤ 18 %)")]
    if "D" in lids:
        sym += [("bipv", "BIPV szkło-szkło jako pokrycie"), ("green", "taras – dach zielony"), ("drain", "wpust dachowy, spadek 1,5 %")]
    return sym


def draw_symbol(svg, c, kind):
    cx = c[0] - 1.8
    if kind == "wc":
        icon_wheelchair(svg, c, 2.4)
    elif kind == "moe":
        icon_moe(svg, c, 2.6)
    elif kind == "loop":
        icon_loop(svg, c, 2.4)
    elif kind == "tyflo":
        icon_tyflo(svg, c, 2.4)
    elif kind == "ozn":
        icon_wheelchair(svg, c, 2.4, color="#2b5b84")
    elif kind == "lvl":
        level_mark(svg, c, "")
    elif kind == "sec":
        svg.text((c[0], c[1] + 1.1), "A", size=3.0, weight=700, anchor="middle")
    elif kind == "fon":
        svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke="#8f8981", sw=0.55, extra='stroke-dasharray="0.35,0.3"')
    elif kind == "ent":
        svg.circle(c, 1.5, fill=ACC, stroke="none")
    elif kind == "tree_n":
        svg.circle(c, 1.4, fill="none", stroke=INK, sw=0.18)
    elif kind == "tree_e":
        svg.circle(c, 1.4, fill="#ffffff", stroke="#6f6a63", sw=0.13)
    elif kind == "lamp":
        svg.circle(c, 0.9, fill="#ffffff", stroke=INK, sw=0.15)
        svg.line((c[0] - 0.9, c[1]), (c[0] + 0.9, c[1]), stroke=INK, sw=0.1)
    elif kind == "rack":
        for j in range(3):
            svg.line((cx + 0.6 + j, c[1] - 1.0), (cx + 0.6 + j, c[1] + 1.0), stroke=INK, sw=0.14)
    elif kind == "bound":
        svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke="#2f6f8f", sw=0.3, extra='stroke-dasharray="1.6,0.6"')
    elif kind == "stall":
        svg.poly([(cx + 0.4, c[1] - 1.1), (cx + 3.0, c[1] - 1.1), (cx + 3.0, c[1] + 1.1), (cx + 0.4, c[1] + 1.1)], fill="#ffffff", stroke=GREY, sw=0.1)
    elif kind in ("ramp", "granit", "brick", "lawn", "rain", "bipv", "green"):
        pat = {"ramp": svg.hatch("ramp", 1.2, 45, HAIR, 0.08), "granit": svg.hatch("granit", 1.5, 0, "#d8d4ce", 0.06, bg="#f6f5f2"),
               "brick": svg.hatch("brick", 0.8, 90, "#c9bfb4", 0.07, bg="#f3efea"), "lawn": svg.hatch("lawn", 0.9, 30, "#d9ddd2", 0.05, bg="#fbfbf9"),
               "rain": svg.hatch("rain", 0.7, 0, "#b9c4c6", 0.06, bg="#f1f4f4"), "bipv": "#f4f3f1",
               "green": svg.hatch("green", 0.8, 60, "#9aa58e", 0.08, bg="#f2f4ef")}[kind]
        svg.poly([(cx, c[1] - 1.1), (cx + 3.6, c[1] - 1.1), (cx + 3.6, c[1] + 1.1), (cx, c[1] + 1.1)], fill=pat, stroke=GREY, sw=0.1)
    elif kind == "acc":
        svg.line((cx, c[1]), (cx + 3.6, c[1]), stroke=ACC, sw=1.0)
    elif kind == "drain":
        svg.circle(c, 0.9, fill="#ffffff", stroke=INK, sw=0.15)
        svg.circle(c, 0.35, fill=INK, stroke="none")


def export_tight(ids=None):
    PLANSZA.mkdir(parents=True, exist_ok=True)
    order = ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT", "D"]
    sizes = []
    for lid in (ids or order):
        if lid not in LV:
            continue
        svg = tight_sheet(lid)
        fn = PLANSZA / f"rzut_{FILE_ID[lid]}_1-200_tight.svg"
        fn.write_text(svg.render(), encoding="utf-8")
        lim = LIMITS[GROUP_T[lid]]
        ok = svg.w_mm <= lim[0] + 1e-6 and svg.h_mm <= lim[1] + 1e-6
        sizes.append(dict(plik=fn.name, szer_mm=round(svg.w_mm, 1), wys_mm=round(svg.h_mm, 1), limit=list(lim), ok=ok))
        print(f"{fn.relative_to(ROOT)}  {svg.w_mm:.1f} × {svg.h_mm:.1f} mm  (limit {lim[0]} × {lim[1]}) {'OK' if ok else 'PRZEKROCZONY'}", flush=True)
    if not ids:
        lw = legend_flow("P4", ["1", "2", "3", "4"], 190.0, t_head=2.0, t_row=1.8, max_h=600, ncol_try=(1,))
        fn = PLANSZA / "legenda_P4_waska.svg"
        fn.write_text(lw.render(), encoding="utf-8")
        sizes.append(dict(plik=fn.name, szer_mm=round(lw.w_mm, 1), wys_mm=round(lw.h_mm, 1), limit=[190, 600], ok=lw.h_mm <= 600))
        print(f"{fn.relative_to(ROOT)}  {lw.w_mm:.1f} × {lw.h_mm:.1f} mm", flush=True)
        lp = legend_flow("P3", ["P", "-1", "-2"], 525.0, t_head=1.9, t_row=1.8, max_h=105, ncol_try=(4, 5, 6, 7, 8), title_sz=2.4)
        fn = PLANSZA / "legenda_P3_pas.svg"
        fn.write_text(lp.render(), encoding="utf-8")
        sizes.append(dict(plik=fn.name, szer_mm=round(lp.w_mm, 1), wys_mm=round(lp.h_mm, 1), limit=[525, 105], ok=lp.h_mm <= 105))
        print(f"{fn.relative_to(ROOT)}  {lp.w_mm:.1f} × {lp.h_mm:.1f} mm", flush=True)
        (PLANSZA / "rozmiary_tight.json").write_text(json.dumps(sizes, ensure_ascii=False, indent=1), encoding="utf-8")
    return sizes


def to_png(svg_path: Path, w_mm, h_mm):
    html = svg_path.with_suffix(".html")
    body = svg_path.read_text(encoding="utf-8")
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{w_mm:.1f}mm {h_mm:.1f}mm;margin:0}}'
                    f'html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}</style></head><body>{body}</body></html>', encoding="utf-8")
    pdf = svg_path.with_suffix(".pdf")
    png = svg_path.with_suffix(".png")
    cmd = ["node", str(ROOT / "tools" / "plansze" / "html2pdf.js"), str(html), str(pdf), f"{w_mm:.1f}", f"{h_mm:.1f}", "--png", str(png), "--pngw", "2400"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if r.returncode != 0:
        print("PNG błąd:", r.stderr[-400:])
        return None
    # podgląd ≤ 1,5 MB
    PREV.mkdir(parents=True, exist_ok=True)
    dst = PREV / png.name
    try:
        from PIL import Image
        im = Image.open(png).convert("RGB")
        im.save(dst, optimize=True)
        if dst.stat().st_size > 1_450_000:
            im.quantize(colors=64, method=Image.Quantize.MEDIANCUT).save(dst, optimize=True)
        if dst.stat().st_size > 1_450_000:
            im2 = im.resize((int(im.width * 0.8), int(im.height * 0.8)), Image.LANCZOS)
            im2.quantize(colors=48).save(dst, optimize=True)
    except Exception as e:
        print("PIL:", e)
        dst.write_bytes(png.read_bytes())
    return dst


def main(ids=None):
    OUT.mkdir(parents=True, exist_ok=True)
    order = ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT", "D"]
    ids = ids or order
    for lid in ids:
        if lid not in LV:
            continue
        svg = page(lid)
        fn = OUT / f"rzut_{FILE_ID[lid]}_1-200.svg"
        fn.write_text(svg.render(), encoding="utf-8")
        dst = to_png(fn, svg.w_mm, svg.h_mm)
        print(f"{lid}: {fn.relative_to(ROOT)}  {svg.w_mm:.0f}×{svg.h_mm:.0f} mm  → {dst.relative_to(ROOT) if dst else '-'}"
              f" {dst.stat().st_size // 1024 if dst else 0} kB")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--plansza":
        export_boards(args[1:] or None)
    elif args and args[0] == "--plansza-ciasna":
        export_tight(args[1:] or None)
    elif args and args[0] == "--wszystko":
        main(None)
        export_boards(None)
        export_tight(None)
    else:
        main(args or None)
