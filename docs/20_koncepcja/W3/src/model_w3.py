# -*- coding: utf-8 -*-
"""Wariant W3 - model zbiorczy (jedno zrodlo prawdy dla rysunkow i opisu). Laczy base_w3, geo_p0/p1/p2, geo_ext."""
import math
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from base_w3 import *            # noqa: F401,F403  (OSIE_X, OSIE_Y, TYPY, POZ, SZACHT_*, SCH_*)
from geo_p0 import SCIANY_P0, OTWORY_P0, POM_P0, OKNA_POM_P0
from geo_p1 import SCIANY_P1, OTWORY_P1, POM_P1, OKNA_POM_P1, PUSTKA, BOKS_UDZIAL
from geo_p2 import SCIANY_P2, OTWORY_P2, POM_P2, OKNA_POM_P2
from geo_ext import *            # noqa: F401,F403

SCIANY = SCIANY_P0 + SCIANY_P1 + SCIANY_P2
OTWORY = OTWORY_P0 + OTWORY_P1 + OTWORY_P2
POMIESZCZENIA = POM_P0 + POM_P1 + POM_P2
OKNA_POM = {**OKNA_POM_P0, **OKNA_POM_P1, **OKNA_POM_P2}
KONDY = ("P0", "P1", "P2")


def teren(x, y):
    """Rzedna istniejacego terenu (interpolacja dwuliniowa narożników dzialki), m n.p.m."""
    fx = (x - DZ["xw"]) / (DZ["xe"] - DZ["xw"])
    fy = (y - DZ["ys"]) / (DZ["yn"] - DZ["ys"])
    s = H_NAROZ["SW"] + fx * (H_NAROZ["SE"] - H_NAROZ["SW"])
    n = H_NAROZ["NW"] + fx * (H_NAROZ["NE"] - H_NAROZ["NW"])
    return s + fy * (n - s)


def teren_wzgl(x, y):
    return teren(x, y) - POZ["zero_abs"]


def wall_poly(w, ext=True):
    t = TYPY[w["typ"]]
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux
    e1, e2 = w["ext"] if ext else (0, 0)
    ax, ay = x1 - ux * e1, y1 - uy * e1
    bx, by = x2 + ux * e2, y2 + uy * e2
    return Polygon([(ax + nx * t["L"], ay + ny * t["L"]), (bx + nx * t["L"], by + ny * t["L"]),
                    (bx - nx * t["R"], by - ny * t["R"]), (ax - nx * t["R"], ay - ny * t["R"])])


def wall_by_id(i):
    return next(w for w in SCIANY if w["id"] == i)


def otwor(i):
    return next(o for o in OTWORY if o["id"] == i)


def opening_cut(o, margin=0.6):
    w = wall_by_id(o["sciana"])
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    if abs(y2 - y1) < 1e-9:
        return box(o["a"], y1 - margin, o["b"], y1 + margin)
    return box(x1 - margin, o["a"], x1 + margin, o["b"])


def outline(kond):
    """Obrys zewnetrzny kondygnacji (lica zewn. scian)."""
    polys = [wall_poly(w) for w in SCIANY if w["kond"] == kond and w["typ"] in ("SZ1", "SZL", "SWG", "SW18")]
    u = unary_union(polys)
    ext = Polygon(u.exterior) if u.geom_type == "Polygon" else Polygon(max(u.geoms, key=lambda g: g.area).exterior)
    return ext.simplify(0.001)


def room_area(r):
    return round(r["poly"].area, 2)


def okno_w_swietle(o, a=None, b=None):
    """Pow. okna w swietle oscieznic: otwor minus oscieznica 7 cm z kazdej strony i slupki 10 cm (opcjonalnie wycinek a..b)."""
    a = o["a"] if a is None else a
    b = o["b"] if b is None else b
    n_sl = len([p for p in o["podz"] if a < p < b]) if o["podz"] else (o["kw"] - 1 if (a, b) == (o["a"], o["b"]) else 0)
    return max(0.0, (b - a - 0.14) * (o["wys"] - 0.14) - n_sl * 0.10 * (o["wys"] - 0.14))


def okna_pomieszczenia(rid):
    tot = 0.0
    for oid in OKNA_POM.get(rid, []):
        o = otwor(oid)
        if o["typ"] == "boks" and rid in BOKS_UDZIAL:
            tot += okno_w_swietle(o, *BOKS_UDZIAL[rid])
        else:
            tot += okno_w_swietle(o)
    return tot


def pu(kond=None):
    return round(sum(room_area(r) for r in POMIESZCZENIA if r["kat"] not in ("garaż", "pustka") and (kond is None or r["kond"] == kond)), 2)


def pow_zabudowy():
    """Rzut po zewn. obrysie scian P0 + wystajace poza P0 czesci wyzszych kondygnacji (wspornik P2)."""
    base = outline("P0")
    up = unary_union([outline("P1"), outline("P2")])
    return base, unary_union([base, up])


if __name__ == "__main__":
    for k in KONDY:
        print(k, "PU", pu(k), "obrys", round(outline(k).area, 2), [round(v, 2) for v in outline(k).bounds])
    print("PU razem", pu())
    b, z = pow_zabudowy()
    print("pow. zabudowy", round(z.area, 2))
    for r in POMIESZCZENIA:
        w = okna_pomieszczenia(r["id"])
        print(r["id"], r["nazwa"], room_area(r), ("okna %.2f  1/8=%.2f" % (w, r["poly"].area / 8)) if r["pobyt"] else "")
