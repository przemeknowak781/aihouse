"""Wspólne dane i geometria rewizji v1.1 koncepcji „BRAMA I LATARNIA”.

Używane przez skrypty docs/20_koncepcja/_rewizja_*.py. Uruchamiać z katalogu umwd/:
    /home/user/aihouse/.venv-render/bin/python -I docs/20_koncepcja/_rewizja_<nazwa>.py
Źródła: model/site.json (granice, NMT, drzewa M.02), model/koncepcja.json (bryły v1.0), tabela 4.1 spec.
Układy pomocnicze (koncepcja.json meta):
    wieża (u, v):    e = 74,606 + 0,97155·u − 0,23684·v ;  n = 40,756 + 0,23684·u + 0,97155·v
    skrzydło (s, d): e = 48,842 + 0,21498·s + 0,97662·d ;  n = 9,683 + 0,97662·s − 0,21498·d
"""
import json
import math
import os

from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITE = json.load(open(os.path.join(ROOT, "model", "site.json"), encoding="utf-8"))
K = json.load(open(os.path.join(ROOT, "model", "koncepcja.json"), encoding="utf-8"))

CU, SU = 0.97155, 0.23684          # cos/sin obrotu układu wieży
CS, SS = 0.21498, 0.97662          # układ skrzydła


def uv2en(u, v):
    return (74.606 + CU * u - SU * v, 40.756 + SU * u + CU * v)


def en2uv(e, n):
    de, dn = e - 74.606, n - 40.756
    return (CU * de + SU * dn, -SU * de + CU * dn)


def sd2en(s, d):
    return (48.842 + CS * s + SS * d, 9.683 + SS * s - CS * d)


def en2sd(e, n):
    de, dn = e - 48.842, n - 9.683
    return (CS * de + SS * dn, SS * de - CS * dn)


def poly_uv(pts):
    return Polygon([uv2en(*p) for p in pts])


def rect_uv(u0, v0, u1, v1):
    return poly_uv([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def rect_sd(s0, d0, s1, d1):
    return Polygon([sd2en(s0, d0), sd2en(s1, d0), sd2en(s1, d1), sd2en(s0, d1)])


def to_uv(g):
    """Geometria (e,n) -> (u,v) (do raportów)."""
    return affinity.affine_transform(g, [CU, SU, -SU, CU, -(CU * 74.606 + SU * 40.756), -(-SU * 74.606 + CU * 40.756)])


# ------------------------------------------------------------------ granice (site.json)
G = SITE["granice"]
OI = Polygon(G["obszar_inwestycji"]["pts"])
A = Polygon(G["wydzielenie_A_mpzp"]["pts"])
OGR = Polygon(G["ogrodki_przydomowe"]["pts"])
D102 = Polygon(G["dojazd_dz_10_2"]["pts"])

# ------------------------------------------------------------------ bryły v1.1
B = {b["id"]: b for b in K["bryly"]}
W = Polygon(B["W"]["obrys_ccw"])
SEG = Polygon(B["S"]["obrys_ccw"])


def wing_tab41(nseg=24):
    """Skrzydło wg tabeli 4.1 spec. (dziób z łukiem R 3,5 krótszą drogą), kolejność CCW."""
    c, R = (64.669, 65.301), 3.5
    p1, p2 = (61.251, 66.053), (63.840, 68.701)
    a0, a1 = math.atan2(p1[1] - c[1], p1[0] - c[0]), math.atan2(p2[1] - c[1], p2[0] - c[0])
    arc = [(round(c[0] + R * math.cos(a0 + (a1 - a0) * i / nseg), 3),
            round(c[1] + R * math.sin(a0 + (a1 - a0) * i / nseg), 3)) for i in range(nseg + 1)]
    arc[0], arc[-1] = p1, p2
    cw = [(48.842, 9.683)] + arc + [(67.494, 69.592), (74.557, 40.744), (70.839, 39.838), (63.498, 6.487)]
    P = Polygon(cw)
    if not P.exterior.is_ccw:
        P = Polygon(list(P.exterior.coords)[::-1])
    return P


M = wing_tab41()

# ------------------------------------------------------------------ podziemie v1.1
DW = 0.60          # grubość ściany szczelinowej v1.1 [m]
OFF_88 = 0.15      # lico zewn. ściany szczelinowej od granicy z dz. 8/8 (tolerancja wykonania + pion 0,5 %)
JG_MAZ19 = 1.20    # pas kolumn iniekcji strumieniowej Ø 1,2 m przy szczycie Maz. 19 (lico zewn. skrzynki −1)
STRIP_V = -5.0     # pas −1 pod dziedzińcem v 0…−5,0 (zalecenie G-I-2)
STRIP_U = (-3.90, 21.0)


def wing_underground(s_min=JG_MAZ19, off_w=OFF_88):
    """Skrzydło w rzucie podziemia: cofnięcie od Maz. 19 (s) i od dz. 8/8 (d)."""
    return M.intersection(rect_sd(s_min, off_w, 80.0, 40.0))


def strip(v=STRIP_V):
    return rect_uv(STRIP_U[0], v, STRIP_U[1], 0.0)


def level_m1():
    g = unary_union([wing_underground(), W, SEG, strip()]).buffer(0.1, join_style=2).buffer(-0.1, join_style=2)
    return g


def level_m2(s_from=12.15, s_to=80.0):
    """−2 v1.1: wieża + segment + pas 5 m + skrzydło od s = s_from (bez M1 przy Maz. 19); s_to – opcjonalne przycięcie dzioba."""
    wing2 = M.intersection(rect_sd(s_from, OFF_88, s_to, 40.0))
    g = unary_union([wing2, W, SEG, strip()]).buffer(0.1, join_style=2).buffer(-0.1, join_style=2)
    return g


def fmt(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")
