#!/usr/bin/env python3
"""Schematy idei (plansza 1): cztery aksonometrie bryły w kontekście – 1 pamięć kwartału (ślad 1934), 2 pierzeje
(gzyms w linii kamienic), 3 latarnia (dominanta w strefie A nad przyczółkiem), 4 brama i ogród (oś publiczna most → Hala → ogród).
Rzut aksonometryczny od pn.-wsch. (az. 31,3°, skrót planu 0,5), wysokości rzeczywiste. Dane: koncepcja.json, site.json.
Wynik: build/rysunki/schematy_idei.svg + docs/70_rysunki/podglady/schematy_idei.png
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from umwd.svg import Svg
from umwd.siteplan import load_site, poly_of
from umwd.runs import ccw

S = load_site()
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
Z0 = 119.30
INK, ACC = "#1f1d1a", "#a8483a"
B = {b["id"]: b for b in K["bryly"]}
OURS = [(Polygon(B["W"]["obrys_ccw"]).buffer(0), B["W"]["dach"]["attyka"]["wzgl"], "W"),
        (Polygon(B["M"]["obrys_ccw"]).buffer(0), B["M"]["dach"]["gzyms_attyka"]["wzgl"], "M"),
        (Polygon(B["S"]["obrys_ccw"]).buffer(0), B["S"]["dach"]["attyka"]["wzgl"], "S")]
NB = []
for b in S["budynki"]["items"]:
    pg = poly_of(b)
    if pg is not None and pg.area > 5 and not b.get("czesciowy_przyciety_ramka"):
        NB.append((pg.buffer(0), b.get("gora_szac_H", 120 + b.get("wysokosc_szac_m", 6)) - Z0, b.get("nazwa")))
AZ = 152.0       # viewer from SSE: garden, Wybrzeże frontage and tower visible; arc seen from behind
f = (math.sin(math.radians(AZ)), math.cos(math.radians(AZ)))
rgt = (f[1], -f[0])
CE, CN = 86.0, 40.0
KSQ, KZ, SC = 0.70, 0.75, 0.92   # steep axonometry (≈ 57°): plan squash, height factor, mm/m
PW, PH = 128.0, 118.0        # panel size


def make_P(ox, oy):
    def P(e, n, z):
        x = (e - CE) * rgt[0] + (n - CN) * rgt[1]
        y = (e - CE) * f[0] + (n - CN) * f[1]
        return (ox + x * SC, oy + (y * KSQ - z * KZ) * SC)
    return P


def prism(svg, P, pg, z1, top="#ffffff", side="#e7e2d9", side2="#d6d0c6", stroke=INK, sw=0.18, z0=0.0, op=1.0):
    pts = ccw(list(pg.exterior.coords)[:-1])
    faces = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]
        nx, ny = ty, -tx                         # outward normal (CCW)
        L = math.hypot(nx, ny) or 1
        vis = (nx * f[0] + ny * f[1]) / L
        if vis > 0.02:
            depth = ((a[0] + b[0]) / 2 - CE) * f[0] + ((a[1] + b[1]) / 2 - CN) * f[1]
            light = (nx * rgt[0] + ny * rgt[1]) / L
            faces.append((depth, a, b, light))
    faces.sort(key=lambda t: t[0])
    ex = f'fill-opacity="{op}"' if op < 1 else ""
    for depth, a, b, light in faces:
        col = side if light < 0 else side2
        svg.poly([P(*a, z0), P(*b, z0), P(*b, z1), P(*a, z1)], fill=col, stroke=stroke, sw=sw * 0.7, extra=ex)
    svg.poly([P(x, y, z1) for x, y in pts], fill=top, stroke=stroke, sw=sw, extra=ex)


def ground(svg, P, alpha=1.0):
    u = S["ulice_i_sytuacja"]
    for key, col in (("jezdnie", "#eeece8"), ("chodniki", "#f6f4f0"), ("trawniki", "#e6ebdc")):
        for it in u[key]:
            if it.get("zamknieta", True):
                pg = poly_of(it)
                if pg is not None and pg.intersects(Polygon([(20, -40), (150, -40), (150, 120), (20, 120)])):
                    pg = pg.intersection(Polygon([(20, -40), (150, -40), (150, 120), (20, 120)]))
                    for g in ([pg] if pg.geom_type == "Polygon" else getattr(pg, "geoms", [])):
                        if g.geom_type == "Polygon":
                            svg.poly([P(x, y, 0) for x, y in g.exterior.coords], fill=col, stroke="none")
    for w in S["woda"]["linia_brzegu"]:
        svg.poly([P(x, y, 0) for x, y in w["pts"]], fill="none", stroke="#9fb8c0", sw=0.25, close=False)


def context(svg, P, light=True):
    items = sorted(NB, key=lambda t: -(((t[0].centroid.x - CE) * f[0] + (t[0].centroid.y - CN) * f[1])))
    for pg, h, name in items:
        prism(svg, P, pg, h, top="#f3f1ed", side="#e9e6e1", side2="#dedad3", stroke="#9a948c", sw=0.12)


def ours(svg, P, hl=None, ghost=False):
    order = sorted(OURS, key=lambda t: ((t[0].centroid.x - CE) * f[0] + (t[0].centroid.y - CN) * f[1]))
    for pg, h, k in order:
        if ghost:
            prism(svg, P, pg, h, top="#ffffff", side="#ffffff", side2="#ffffff", stroke="#b8b2a9", sw=0.12, op=0.0)
            continue
        if hl and k in hl:
            prism(svg, P, pg, h, top=hl[k][0], side=hl[k][1], side2=hl[k][2], stroke=INK, sw=0.22)
        else:
            prism(svg, P, pg, h)


W_MM = 4 * PW + 3 * 6 + 20
svg = Svg(W_MM, PH + 40)
titles = [("1", "PAMIĘĆ KWARTAŁU", "Kwartał kamienic zniszczony w 1945 r. i rozebrany po wojnie wraca w swoich liniach: pierzeje Mazowieckiej i Wybrzeża, zaokrąglony narożnik przy moście; ślad pierzei północnej z 1934 r. w posadzce Placu Mostowego."),
          ("2", "PIERZEJE", "Skrzydło i segment domykają ulice w skali kamienic: gzyms 140,15 w linii attyki Mazowieckiej 19, rytm czterech posesji."),
          ("3", "LATARNIA", "Widok od mostu: wieża Sejmiku w strefie A (37,2 m) – jedyna dominanta, zwrócona łukiem do Mostu Grunwaldzkiego; w koronie sala obrad."),
          ("4", "BRAMA I OGRÓD", "Podcień Bramy Mostowej prowadzi przez Halę Obywatelską do otwartego, nieogrodzonego Ogrodu Województwa; drzewa ogródków zostają.")]
for i, (num, t, txt) in enumerate(titles):
    _az = 31.3 if i == 2 else 152.0          # panel 3: view from the bridge (NNE); others from SSE (garden)
    f = (math.sin(math.radians(_az)), math.cos(math.radians(_az)))
    rgt = (f[1], -f[0])
    ox = 10 + i * (PW + 6) + PW * 0.52
    oy = 22 + PH * 0.62
    P = make_P(ox, oy)
    ground(svg, P)
    if i == 0:
        # 1934 block trace (diagram, ±5–10 m after historia.md): north frontage line + rounded bridge corner
        trace = [(61.25, 66.05), (63.4, 79.6), (75.0, 81.0), (86.0, 81.9), (93.5, 81.6), (98.6, 79.6), (106.0, 76.5), (112.0, 70.0), (115.5, 60.0), (118.2, 46.0), (118.2, 28.5)]
        svg.poly([P(x, y, 0) for x, y in trace], fill="none", stroke=ACC, sw=0.5, close=False, extra='stroke-dasharray="1.6,0.9"')
        old = Polygon([(48.8, 9.7), (61.25, 66.05), (63.4, 79.6), (75.0, 81.0), (98.6, 79.6), (112.0, 70.0), (118.2, 46.0), (118.2, 28.5), (102.0, 28.0), (102.6, 10.7), (64.3, 6.3)])
        context(svg, P)
        prism(svg, P, old.difference(unary_union([pg for pg, _, _ in NB]).buffer(0.2)).buffer(0), 21.0, top="#f6e9e4", side="#ead2c9", side2="#e0c3b8", stroke=ACC, sw=0.15, op=0.55)
    elif i == 1:
        context(svg, P)
        ours(svg, P, hl={"M": ("#f3e3d8", "#e6cdbd", "#dbbda9"), "S": ("#f3e3d8", "#e6cdbd", "#dbbda9")})
        # cornice line hint
        a, b = (48.84, 9.68), (61.25, 66.05)
        svg.line(P(*a, 20.85), P(*b, 20.85), stroke=ACC, sw=0.6)
    elif i == 2:
        context(svg, P)
        ours(svg, P, hl={"W": ("#ffffff", "#e9dcc7", "#ddcdb2")})
        # glowing crown band on the arc side
        c, R = (96.148, 62.167), 14.0
        arc = [(c[0] + R * math.cos(math.radians(a)), c[1] + R * math.sin(math.radians(a))) for a in range(14, 104, 4)]
        for z0_, z1_ in ((27.3, 36.2),):
            pts = [P(x, y, z0_) for x, y in arc] + [P(x, y, z1_) for x, y in reversed(arc)]
            svg.poly(pts, fill="#f2c46d", stroke="none", extra='fill-opacity="0.85"')
        for x, y in arc[::2]:
            svg.line(P(x, y, 27.3), P(x, y, 36.2), stroke="#c99a3e", sw=0.12)
    else:
        axis = [(112.0, 92.0), (103.4, 74.0), (101.86, 71.57), (84.32, 43.12), (80.0, 28.0), (78.0, 12.0)]
        gard = Polygon([(66.0, -2.0), (96.0, -2.0), (96.0, 38.0), (72.0, 33.0), (66.0, 30.0)])
        svg.poly([P(x, y, 0) for x, y in gard.exterior.coords], fill="#d7e3c6", stroke="none")
        svg.poly([P(x, y, 0.3) for x, y in axis], fill="none", stroke=ACC, sw=1.0, close=False, extra='stroke-linecap="round"')
        context(svg, P)
        ours(svg, P)
        foot = unary_union([pg for pg, _, _ in OURS])
        inside = LineString(axis).intersection(foot)
        for g in ([inside] if inside.geom_type == "LineString" else getattr(inside, "geoms", [])):
            svg.poly([P(x, y, 0.3) for x, y in g.coords], fill="none", stroke=ACC, sw=0.6, close=False, extra='stroke-dasharray="1.2,0.9"')
        for (x, y) in ((70.0, 20.0), (76.0, 8.0), (86.0, 14.0), (90.0, 2.0), (66.0, 4.0), (82.0, 25.0), (92.0, 24.0), (73.0, 28.0)):
            xx, yy = P(x, y, 0)
            svg.line((xx, yy), (xx, yy - 6.5 * KZ * SC), stroke="#6b7a55", sw=0.2)
            svg.circle((xx, yy - 8.5 * KZ * SC), 2.8 * SC, fill="#9db28a", stroke="#6b7a55", sw=0.12, extra='fill-opacity="0.85"')
        xe, ye = P(*axis[-1], 0.3)
        svg.circle((xe, ye), 1.4, fill=ACC, stroke="none")
    tx = 10 + i * (PW + 6)
    svg.text((tx, 10), num, size=7.0, weight=300, fill=ACC)
    svg.text((tx + 7, 9.2), t, size=3.4, weight=600)
    words, line, lines = txt.split(), "", []
    for w in words:
        if len(line) + len(w) > 62:
            lines.append(line); line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)
    for j, ln in enumerate(lines):
        svg.text((tx, PH + 22 + j * 3.6), ln, size=2.4, fill="#3a3632")

out = ROOT / "build" / "rysunki" / "schematy_idei.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "schematy_idei.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm + 10:.0f}mm {svg.h_mm + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{svg.w_mm + 10:.0f} {svg.h_mm + 10:.0f}")
