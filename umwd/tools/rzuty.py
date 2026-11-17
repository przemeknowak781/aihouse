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
        svg.text((c[0], c[1] + 0.6), tag, size=1.7, anchor="middle", weight=600, fill=INK, extra=halo_extra(0.5))


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
                svg.poly([(x0 + 0.2, y - 0.8), (x0 + 3.0, y + 0.4), (x0 + 0.2, y + 1.6)], fill=ACC, stroke="none")
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
        if r["kind"] in ("core_lift",):
            continue
        pg = poly_paper(v, g)
        if pg.is_empty:
            continue
        rp = pg.representative_point()
        num = r["numer"]
        ar = fnum(r["powierzchnia"]) + " m²"
        s1, s2 = 1.75, 1.6
        name = None
        w1 = Labels.tw(num, s1, True)
        w2 = Labels.tw(ar, s2)
        if big_names and r["powierzchnia"] > 70 and r["kind"] in ("room", "garage", "corridor") and r["kod_grupy"] not in ("KW",):
            name = short_name(r["nazwa"])
        h = 4.2 + (2.6 if name else 0)
        w = max(w1, w2, Labels.tw(name, 2.0, True) if name else 0) + 0.8
        placed = None
        cands = [(rp.x, rp.y)]
        b = pg.bounds
        for fx in (0.5, 0.3, 0.7):
            for fy in (0.5, 0.3, 0.7, 0.2, 0.8):
                cands.append((b[0] + (b[2] - b[0]) * fx, b[1] + (b[3] - b[1]) * fy))
        inner = pg.buffer(-0.3)
        for (x, y) in cands:
            bx = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            if inner.contains(box(*bx)) and lab.free(bx):
                placed = (x, y, False)
                break
        if placed is None:
            # na zewnątrz z odnośnikiem
            for dist in (6, 9, 12, 15):
                for ang in range(0, 360, 30):
                    x = rp.x + dist * math.cos(math.radians(ang))
                    y = rp.y + dist * math.sin(math.radians(ang))
                    bx = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
                    if lab.free(bx):
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
        yy = y - h / 2 + 1.9
        if name:
            svg.text((x, yy), name, size=2.0, anchor="middle", weight=600, fill=col, extra=halo_extra(0.6))
            yy += 2.6
        svg.text((x, yy), num, size=s1, anchor="middle", weight=600, fill=col, extra=halo_extra(0.55))
        svg.text((x, yy + 2.1), ar, size=s2, anchor="middle", fill=GREY, extra=halo_extra(0.55))


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


def site_design(svg, v, lab):
    """Projekt otoczenia: nawierzchnie, mała architektura, oświetlenie, zieleń, ślad pierzei 1934, ogród."""
    g_ = SITE["granice"]
    oi = Polygon(g_["obszar_inwestycji"]["pts"]).buffer(0)
    skwer = Polygon(g_["teren_uzyczony_dz_9_2"]["pts"]).buffer(0)
    ogrodki = Polygon(g_["ogrodki_przydomowe"]["pts"]).buffer(0)
    bld = unary_union([Polygon(b["obrys_ccw"]).buffer(0) for b in SPEC["bryly"]]).buffer(0.05)
    podc = Polygon(SPEC["cofniecia_wneki"]["podcien_Brama_Mostowa"]["obrys_ccw"]).buffer(0)
    brama = Polygon(SPEC["cofniecia_wneki"]["brama_ogrodowa"]["obrys_ccw"]).buffer(0)
    court = oi.difference(bld).difference(skwer)
    # granit: skwer, podcień, brama ogrodowa, pas przed wejściami
    granit = unary_union([skwer.difference(bld), podc, brama])
    model_rings(svg, v, granit, fill=svg.hatch("granit", 1.5, 0, "#d8d4ce", 0.06, bg="#f6f5f2"), stroke="none")
    # ogród: trawnik + ogródki istniejące
    lawn = court.difference(ogrodki.buffer(0.3))
    model_rings(svg, v, lawn, fill=svg.hatch("lawn", 0.9, 30, "#d9ddd2", 0.05, bg="#fbfbf9"), stroke="none")
    model_rings(svg, v, ogrodki.intersection(oi), fill=svg.hatch("ogr", 1.1, -30, "#cfd3c8", 0.06, bg="#f6f7f3"), stroke="#8d8a83", sw=0.12,
                extra='stroke-dasharray="1.2,0.8"')
    # ścieżki (cegła z wykopu): od wejścia ogrodowego do bramy ogrodowej i do pasa od bulwaru
    def door_uv(spec_txt):
        m = re.search(r"u\s*([\d,]+)\s*[–-]\s*([\d,]+)", spec_txt)
        return (float(m.group(1).replace(",", ".")) + float(m.group(2).replace(",", "."))) / 2 if m else 10.0
    ud = door_uv(SPEC["cofniecia_wneki"]["wneka_wejscia_ogrodowego"]["elewacja"])
    p_door = T.en(ud, -1.0)
    p_brama = ((brama.centroid.x * 0.5 + Polygon(SPEC["cofniecia_wneki"]["brama_ogrodowa"]["obrys_ccw"]).exterior.coords[3][0] * 0.5),
               (brama.centroid.y * 0.5 + Polygon(SPEC["cofniecia_wneki"]["brama_ogrodowa"]["obrys_ccw"]).exterior.coords[3][1] * 0.5))
    p_brama = WF.en(14.2, 17.0)
    seg = SPEC["bryly"][2]["obrys_ccw"]
    p_bul = ((seg[0][0] + seg[1][0]) / 2 + 0.0, (seg[0][1] + seg[1][1]) / 2 - 2.6)
    mid = T.en(ud - 2.0, -9.0)
    paths = unary_union([LineString([p_door, mid, p_brama]).buffer(1.1, cap_style=2, join_style=2),
                         LineString([mid, T.en(16.0, -10.5), p_bul, (p_bul[0] + 10.0, p_bul[1] - 0.6)]).buffer(1.0, cap_style=2, join_style=2)])
    paths = paths.intersection(oi.difference(bld)).difference(ogrodki)
    model_rings(svg, v, paths, fill=svg.hatch("brick", 0.8, 90, "#c9bfb4", 0.07, bg="#f3efea"), stroke="#a69c91", sw=0.1)
    # ogród deszczowy 140 m² (przy elewacji pd. wieży, poza ogródkami)
    rg = T.rect(-1.0, 7.5, -10.0, -2.5).intersection(court).difference(paths.buffer(0.3)).difference(ogrodki.buffer(1.0))
    rg = max(polys(rg), key=lambda p: p.area) if polys(rg) else Polygon()
    if not rg.is_empty:
        model_rings(svg, v, rg, fill=svg.hatch("rain", 0.7, 0, "#b9c4c6", 0.06, bg="#f1f4f4"), stroke="#7d98a3", sw=0.12, extra='stroke-dasharray="0.8,0.5"')
        c = v.p(rg.centroid.x, rg.centroid.y)
        svg.text(c, f"ogród deszczowy {fnum(rg.area, 0)} m²", size=1.7, anchor="middle", fill=GREY, extra=halo_extra(0.6))
    # plac zabaw (nawierzchnia bezpieczna)
    pz = T.rect(13.0, 19.0, -16.0, -11.5).intersection(court).difference(paths.buffer(0.3)).difference(ogrodki.buffer(0.5))
    for p in polys(pz)[:1]:
        model_rings(svg, v, p, fill="#efefec", stroke=GREY, sw=0.1)
        svg.text(v.p(p.centroid.x, p.centroid.y), "plac zabaw – EPDM", size=1.6, anchor="middle", fill=GREY, extra=halo_extra(0.5))
    # ślad pierzei 1934 – pas granitu z listwą z brązu (wg nakładki planu 1934, ±5 m)
    off = 12.0
    trace = LineString([T.en(-30.0, TOWER_V_() + off - 2.5), T.en(10.0, TOWER_V_() + off), T.en(30.0, TOWER_V_() + off - 1.5)])
    tr = trace.intersection(skwer.buffer(-0.5))
    for g in ([tr] if tr.geom_type == "LineString" else list(getattr(tr, "geoms", []))):
        if g.geom_type == "LineString" and g.length > 2:
            svg.poly([v.p(*c) for c in g.coords], fill="none", stroke=ACC, sw=v.mm(0.5), close=False)
            svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#ffffff", sw=0.12, close=False)
            mpnt = g.interpolate(0.5, normalized=True)
            p = v.p(mpnt.x, mpnt.y)
            svg.text((p[0], p[1] + 3.2), "ślad pierzei 1934 r. – pas granitu z listwą z brązu", size=1.7, anchor="middle", fill=ACC, extra=halo_extra(0.7))
            # 4 lipy drobnolistne wzdłuż śladu w zach. części skweru
            for k in range(4):
                q = g.interpolate(min(g.length, 2.0 + 6.5 * k))
                q2 = (q.x + T.ey[0] * 2.2, q.y + T.ey[1] * 2.2)
                NEW_TREES.append((q2, "lipa drobnolistna"))
    # okrągła ława przy łuku
    cc = BUD["luk"]["srodek_uv"]
    R = BUD["luk"]["R"]
    bench_c = T.en(cc[0] + (R + 5.0) * math.cos(math.radians(55)), cc[1] + (R + 5.0) * math.sin(math.radians(55)))
    svg.circle(v.p(*bench_c), v.mm(2.0), fill="none", stroke=INK, sw=0.2)
    svg.circle(v.p(*bench_c), v.mm(1.45), fill="none", stroke=INK, sw=0.12)
    svg.text((v.p(*bench_c)[0], v.p(*bench_c)[1] + v.mm(2.0) + 2.2), "okrągła ława (granit)", size=1.6, anchor="middle", fill=GREY, extra=halo_extra(0.5))
    # taras bistro (stoliki) w zach. części skweru
    for i in range(3):
        for j in range(2):
            q = WF.en(57.0 - i * 2.4, -1.8 - j * 2.4) if False else T.en(-6.5 + i * 2.4, 32.0 + j * 2.4)
            if skwer.contains(Point(q)):
                svg.circle(v.p(*q), v.mm(0.45), fill="none", stroke=HAIR, sw=0.1)
    # stojaki rowerowe: 20 na skwerze, 10 przy bramie ogrodowej
    def racks(p0, dirv, n):
        for i in range(n):
            q = (p0[0] + dirv[0] * 0.8 * i, p0[1] + dirv[1] * 0.8 * i)
            a = (q[0] - dirv[1] * 0.9, q[1] + dirv[0] * 0.9)
            b = (q[0] + dirv[1] * 0.9, q[1] - dirv[0] * 0.9)
            svg.line(v.p(*a), v.p(*b), stroke=INK, sw=0.14)
    racks(T.en(4.0, 31.6), T.ex, 10)
    racks(T.en(4.0, 33.6), T.ex, 10)
    racks(WF.en(12.6, -2.2), WF.ex, 10) if False else racks(WF.en(17.0, 17.3), WF.ex, 10)
    # ławki przy ścieżkach i pergola przy murze kamienic
    for q, d in ((T.en(ud - 6.0, -6.0), T.ex), (T.en(16.5, -13.5), T.ey), (WF.en(22.0, 18.5), WF.ex)):
        a = (q[0] - d[0] * 0.9, q[1] - d[1] * 0.9)
        b = (q[0] + d[0] * 0.9, q[1] + d[1] * 0.9)
        svg.poly([v.p(a[0], a[1]), v.p(b[0], b[1]), v.p(b[0] + d[1] * 0.5, b[1] - d[0] * 0.5), v.p(a[0] + d[1] * 0.5, a[1] - d[0] * 0.5)], fill="#ffffff", stroke=INK, sw=0.12)
    # latarnie (słupki oświetleniowe h 4 m, w ogrodzie bollardy 0,9 m)
    lamps = []
    for ln, step in ((LineString([p_door, mid, p_brama]), 9.0), (LineString([mid, T.en(16.0, -10.5), p_bul]), 9.0)):
        k = 0.0
        while k <= ln.length:
            q = ln.interpolate(k)
            lamps.append((q.x + 1.6 * T.ex[0], q.y + 1.6 * T.ex[1], "b"))
            k += step
    for k in range(5):
        q = T.en(-14.0 + k * 9.0, 30.6 + (1.0 if k % 2 else 0.0))
        if skwer.buffer(0.5).contains(Point(q)):
            lamps.append((q[0], q[1], "l"))
    for (x, y, kind) in lamps:
        p = v.p(x, y)
        r = 0.9 if kind == "l" else 0.6
        svg.circle(p, r, fill="#ffffff", stroke=INK, sw=0.15)
        svg.line((p[0] - r, p[1]), (p[0] + r, p[1]), stroke=INK, sw=0.1)
        svg.line((p[0], p[1] - r), (p[0], p[1] + r), stroke=INK, sw=0.1)
    # nowe drzewa: 2 przy pasie od bulwaru, 6 w ogrodzie (klon polny, grab), 6 po stronie rzeki na Wybrzeżu
    NEW_TREES.extend([((p_bul[0] + 3.0, p_bul[1] - 2.0), "klon polny"), ((p_bul[0] + 8.0, p_bul[1] - 2.6), "klon polny")])
    for k, (uu, vv) in enumerate([(-2.0, -14.0), (6.0, -17.5), (12.0, -20.0), (24.0, -14.0), (-6.0, -19.0), (19.0, -21.0)]):
        q = T.en(uu, vv)
        if court.contains(Point(q)):
            NEW_TREES.append((q, "grab / klon polny"))
    for k in range(6):
        q = T.en(TOWER_U_() + 14.5, -8.0 + k * 9.5)
        NEW_TREES.append((q, "lipa"))


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
    """Wejścia 1–8 (spec. rozdz. 9) – trójkąty w kolorze akcentu."""
    cw = SPEC["cofniecia_wneki"]
    cc = BUD["luk"]["srodek_uv"]
    R = BUD["luk"]["R"]
    def num(t):
        return float(t.replace(",", "."))
    pts = []
    pts.append((1, T.pu if False else (cc[0] + R * math.cos(math.radians(45)), cc[1] + R * math.sin(math.radians(45))), (-1, -1), "Brama Mostowa"))
    pts.append((2, (22.5, TOWER_V_() + 0.2), (0, -1), "od skweru"))
    m = re.search(r"v\s*([\d,]+)\s*[–-]\s*([\d,]+)", cw["wneka_wejscia_obywatelskiego"]["elewacja"])
    pts.append((3, (TOWER_U_() + 0.2, (num(m.group(1)) + num(m.group(2))) / 2), (-1, 0), "Wejście Obywatelskie"))
    pts.append((4, T.loc(*WF.en(56.4, -0.2)), None, "konferencyjne"))
    m = re.search(r"u\s*([\d,]+)\s*[–-]\s*([\d,]+)", cw["wneka_wejscia_ogrodowego"]["elewacja"])
    pts.append((5, ((num(m.group(1)) + num(m.group(2))) / 2, -0.2), (0, 1), "ogrodowe"))
    pts.append((6, (4.3, -0.2), (0, 1), "rowerownia"))
    pts.append((7, T.loc(*WF.en(14.2, -0.3)), None, "brama ogrodowa"))
    seg = [T.loc(*p) for p in SPEC["bryly"][2]["obrys_ccw"]]
    rs = SPEC["podziemie"]["rampa"]["wjazd"]
    mm_ = re.search(r"v\s*([−-]?[\d,]+)\s*…\s*([−-]?[\d,]+)", rs)
    vg = (num(mm_.group(1).replace("−", "-")) + num(mm_.group(2).replace("−", "-"))) / 2 if mm_ else -7.0
    pts.append((8, (TOWER_U_() + 0.2, vg), (-1, 0), "garaż, dostawy"))
    for n, (u, vv), d, nm in pts:
        p = v.pu(u, vv)
        if d is None:
            dd = v.dir((WF.ey[0], WF.ey[1]))
        else:
            L = math.hypot(*d)
            dd = (d[0] / L, -d[1] / L)
        a = (p[0] - dd[0] * 4.2, p[1] - dd[1] * 4.2)
        nx, ny = -dd[1], dd[0]
        svg.poly([(p[0] - dd[0] * 0.8, p[1] - dd[1] * 0.8), (a[0] + nx * 1.6, a[1] + ny * 1.6), (a[0] - nx * 1.6, a[1] - ny * 1.6)], fill=ACC, stroke="none")
        svg.text((a[0] - dd[0] * 2.4, a[1] - dd[1] * 2.4 + 1.0), str(n), size=2.6, anchor="middle", weight=700, fill=ACC, extra=halo_extra(0.6))


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
        svg.poly(pts, fill="none", stroke="#6f6a63", sw=v.mm(0.30), close=False, extra='stroke-dasharray="0.35,0.35"')
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
    win = Polygon([T.en(u0, v0), T.en(u1, v0), T.en(u1, v1), T.en(u0, v1)])
    # clip planu
    clip_id = svg.uid("clip")
    svg.defs.append(f'<clipPath id="{clip_id}"><rect x="{v.ox:.2f}" y="{v.oy:.2f}" width="{plan_w:.2f}" height="{plan_h:.2f}"/></clipPath>')
    svg.add(f'<g clip-path="url(#{clip_id})">')
    if lid == "P":
        NEW_TREES.clear()
        site_context(svg, v, lab)
        site_design(svg, v, lab)
        draw_trees(svg, v, win)
    elif lid in ("-1", "-2"):
        pass
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
    draw_axes(svg, v, lid, (bbox[0], bbox[1], bbox[2], bbox[3]))
    draw_dims(svg, v, lid)
    draw_sections(svg, v, lab)
    svg.add("</g>")
    # etykiety
    if lid != "D":
        label_rooms(svg, v, lv, lab)
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
    main(sys.argv[1:] or None)
