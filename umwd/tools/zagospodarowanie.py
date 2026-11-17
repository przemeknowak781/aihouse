#!/usr/bin/env python3
"""Koncepcja zagospodarowania terenu 1:500 (Etap II, Reg. R.VII ust.2 pkt2 lit.a) — z mapy (site.json) i specyfikacji (koncepcja.json).

Zawartość: rzut dachów z rzędnymi i liczbą kondygnacji, komunikacja (wejścia, zjazd, dostawy, drogi pożarowe, ruch pieszy
i rowerowy, parkowanie rowerów), zieleń istniejąca/usuwana/nowa, nawierzchnie, mała architektura, cienie przy Słońcu z SW pod 45°.
Wynik: build/rysunki/zagospodarowanie_1-500.svg (+ .html/.png podgląd w docs/70_rysunki/podglady/).
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import affinity
from umwd.svg import Svg, View, model_rings, model_poly, north_arrow, scale_bar
from umwd.siteplan import load_site, poly_of, shadow_poly, C

S = load_site()
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
Z0 = K["meta"]["zero"]["wzgl_0_00_m_npm"]
INK, ACC = "#1f1d1a", "#a8483a"
B = {b["id"]: b for b in K["bryly"]}
tower, wing, seg = (Polygon(B[k]["obrys_ccw"]).buffer(0) for k in ("W", "M", "S"))
inv = Polygon(S["granice"]["obszar_inwestycji"]["pts"]).buffer(0)
comp = Polygon(S["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0)
skwer = Polygon(S["granice"]["teren_uzyczony_dz_9_2"]["pts"]).buffer(0)
ogrodki = Polygon(S["granice"]["ogrodki_przydomowe"]["pts"]).buffer(0)
bld = unary_union([tower, wing, seg])
garden = inv.difference(bld.buffer(0.05))
H = {"W": B["W"]["dach"]["attyka"]["wzgl"], "M": B["M"]["dach"]["gzyms_attyka"]["wzgl"], "S": B["S"]["dach"]["attyka"]["wzgl"]}

v = View(22, -38, 152, 112, 500)
LEG = 92
svg = Svg(v.w_mm + LEG, v.h_mm + 14)
u = S["ulice_i_sytuacja"]

# ---------------- base: streets, lawns, water
for key, col in (("jezdnie", "#ecebe7"), ("chodniki", "#f6f4f0"), ("trawniki", "#e6ebdc")):
    for it in u[key]:
        if it.get("zamknieta", True):
            pg = poly_of(it)
            if pg is not None and not pg.intersects(inv.buffer(-0.5)):
                model_rings(svg, v, pg, fill=col, stroke="none")
for w in S["woda"]["linia_brzegu"]:
    svg.poly([v.p(*p) for p in w["pts"]], fill="none", stroke="#9fb8c0", sw=0.3, close=False)
for it in u["krawezniki"]:
    ln = LineString(it["pts"])
    if not ln.within(inv.buffer(-0.3)):
        svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke="#a8a39b", sw=0.12, close=False)
for it in u["tory_tramwajowe"]:
    svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke="#8c877f", sw=0.15, close=False, extra='stroke-dasharray="1.2,0.6"')
for it in u["mury"]:
    svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke="#6f6a63", sw=0.25, close=False)

# ---------------- proposal ground surfaces
GRANIT, CEGLA, TRAWA, DESZCZ = "#ece8e1", "#d9b9a3", "#dfe8d2", "#cfe0e1"
model_rings(svg, v, skwer.union(inv.difference(bld)).intersection(comp), fill=GRANIT, stroke="none")
# fine granite grid on the bridge square
gx = svg.hatch("granit", spacing=0.9, angle=76.3, stroke="#d8d2c8", sw=0.06)
model_rings(svg, v, skwer, fill=gx, stroke="none")
# garden: lawn, rain garden, paths
gard = garden.intersection(Polygon([(60, -10), (100, -10), (100, 40), (60, 40)]))
model_rings(svg, v, gard, fill=TRAWA, stroke="none")
model_rings(svg, v, ogrodki.intersection(inv), fill="#d6e2c6", stroke="#9fb07f", sw=0.12, extra='stroke-dasharray="0.8,0.6"')
rain = Polygon([(84.5, 2.0), (94.0, 2.4), (93.4, 16.6), (84.6, 16.0)]).intersection(gard)
model_rings(svg, v, rain, fill=DESZCZ, stroke="#7ea7ad", sw=0.15)
paths = [LineString([(84.32, 43.12), (83.0, 34.0), (80.6, 20.0), (77.5, 6.0), (76.0, -4.0)]),
         LineString([(59.4, 23.6), (70.0, 22.5), (80.6, 20.0), (95.0, 27.0), (99.0, 36.0)]),
         LineString([(83.0, 34.0), (97.5, 37.0)])]
for pth in paths:
    model_rings(svg, v, pth.buffer(1.1, cap_style=2).intersection(garden), fill=CEGLA, stroke="none")
# playground & pergola
play = Polygon([(87.5, -5.5), (95.5, -5.2), (95.5, 0.8), (87.5, 0.6)])
model_rings(svg, v, play, fill="#efe2c4", stroke="#b9a072", sw=0.15)
for k in range(8):
    y0 = 5 + k * 3.2
    svg.line(v.p(95.2, y0), v.p(95.2, y0 + 2.2), stroke="#8a6d4c", sw=0.35)
# entry strip from boulevard: bench
model_poly(svg, v, [(98.5, 38.0), (104.0, 38.3), (104.0, 38.9), (98.5, 38.6)], fill="#bdb6ab", stroke=INK, sw=0.1)

# ---------------- 1934 frontage trace on the square + round bench
trace = LineString([(63.4, 79.6), (75.0, 81.0), (86.0, 81.9), (93.5, 81.6), (98.6, 79.6)])
svg.poly([v.p(*c) for c in trace.coords], fill="none", stroke="#8b6a3e", sw=0.55, close=False)
svg.poly([v.p(*c) for c in trace.coords], fill="none", stroke="#f6efe2", sw=0.18, close=False)
bench_c = (105.54, 75.73)   # R 16,5 m od środka łuku (poza podcieniem R 11–14), ten sam kierunek
svg.circle(v.p(*bench_c), v.mm(2.2), fill="none", stroke="#6f6a63", sw=0.35)

# ---------------- shadows (sun from SW, 45°): existing + new
prisms = [(tower, H["W"]), (wing, H["M"]), (seg, H["S"])]
for b in S["budynki"]["items"]:
    pg = poly_of(b)
    if pg is not None:
        prisms.append((pg, b.get("wysokosc_szac_m", 6.0)))
sh = unary_union([shadow_poly(fp, h, 225.0, 45.0) for fp, h in prisms]).difference(unary_union([p for p, _ in prisms]))
model_rings(svg, v, sh, fill="#1f1d1a", stroke="none", extra='fill-opacity="0.085"')

# ---------------- existing neighbours
for b in S["budynki"]["items"]:
    pg = poly_of(b)
    if pg is None:
        continue
    model_rings(svg, v, pg, fill="#dcd8d1", stroke="#6f6a63", sw=0.2)
    c = pg.representative_point()
    svg.text(v.p(c.x, c.y), (b.get("etykieta") or "").lower(), size=1.9, anchor="middle", fill="#5a554e")

# ---------------- roofs of the proposal
def roof(pg, label_lines, at, bipv=True, green=False):
    model_rings(svg, v, pg, fill="#ffffff", stroke=INK, sw=0.5)
    inner = pg.buffer(-0.8, join_style=2)
    model_rings(svg, v, inner, fill="none", stroke=INK, sw=0.12)
    if bipv:
        hp = svg.hatch("bipv", spacing=1.4, angle=76.3 + 90, stroke="#7c7f86", sw=0.12)
        model_rings(svg, v, inner.buffer(-1.5, join_style=2), fill=hp, stroke="#7c7f86", sw=0.1)
    if green:
        model_rings(svg, v, inner, fill="#dfe8d2", stroke="none")
    x, y = v.p(*at)
    for i, (t, sz, w) in enumerate(label_lines):
        svg.text((x, y + i * 3.0), t, size=sz, anchor="middle", weight=w)

wz = B["W"]["dach"]["attyka"]
roof(tower, [("WIEŻA SEJMIKU", 2.4, 600), ("P+6+S · attyka +" + f"{wz['wzgl']:.2f} = {wz['npm']:.2f}".replace('.', ',') + " m n.p.m.", 1.9, 400),
             ("pokrycie min. +" + f"{B['W']['dach']['najnizszy_pkt_pokrycia']['wzgl']:.2f}".replace('.', ',') + " (MPZP: 35–45 m)", 1.8, 400),
             ("dach: BIPV 208 kWp, bez urządzeń", 1.8, 400)], (93.0, 64.5))
mz = B["M"]["dach"]["gzyms_attyka"]
roof(wing, [("SKRZYDŁO", 2.1, 600), ("P+4", 1.9, 400), (f"attyka +{mz['wzgl']:.2f}".replace('.', ','), 1.8, 400), (f"= {mz['npm']:.2f}".replace('.', ','), 1.8, 400)], (60.2, 40.0))
tz = B['S']['dach']['taras_wykonczenie']
roof(seg.buffer(-0.01), [("TARAS ZIELONY", 1.7, 600), (f"P+4 · taras +{tz['wzgl']:.2f}".replace('.', ','), 1.6, 400)], (105.0, 44.2), bipv=False, green=True)

# ---------------- trees: existing kept / removed / new
rem = set(K["zagospodarowanie"]["drzewa_usuniete"])
N_KEPT_OI = sum(1 for t in S["zielen"]["drzewa"] if t["nr"] not in rem and inv.contains(Point(t["e"], t["n"])) and not bld.buffer(0.3).contains(Point(t["e"], t["n"])))
N_KEPT = sum(1 for t in S["zielen"]["drzewa"] if t["nr"] not in rem and not bld.buffer(0.3).contains(Point(t["e"], t["n"])))
for t in S["zielen"]["drzewa"]:
    p = (t["e"], t["n"])
    r = 3.2 if t.get("typ") == "lisciaste" else 2.0
    if t["nr"] in rem:
        x, y = v.p(*p); rr = v.mm(r)
        svg.circle((x, y), rr, fill="none", stroke="#b5aea4", sw=0.1, extra='stroke-dasharray="0.6,0.5"')
        svg.line((x - rr * .55, y - rr * .55), (x + rr * .55, y + rr * .55), stroke="#a39c92", sw=0.15)
        svg.line((x - rr * .55, y + rr * .55), (x + rr * .55, y - rr * .55), stroke="#a39c92", sw=0.15)
        continue
    if bld.buffer(0.3).contains(Point(p)):
        continue
    svg.circle(v.p(*p), v.mm(r), fill="#93a77c", stroke="#ffffff", sw=0.12, extra='fill-opacity="0.55"')
    svg.circle(v.p(*p), v.mm(0.22), fill="#3d4a33", stroke="none")
new_trees = [(66.0, 79.4), (71.5, 80.3), (77.0, 81.0), (82.5, 81.6),          # 4 lindens along the 1934 trace
             (99.8, 37.2), (103.8, 37.6),                                    # boulevard entry strip
             (64.5, 30.0), (70.5, 33.5), (89.0, 25.0), (93.0, 31.0), (73.0, 11.0), (90.5, 9.0),   # garden
             ]
# 6 trees on the river-side pavement of Wybrzeże (spec §9): 1.4 m inside the east kerb, outside the fire-lane working strip
_kerbs = unary_union([LineString(it["pts"]) for it in u["krawezniki"]])
river_trees = []
for nn in (16.0, 24.0, 32.0, 40.0, 48.0, 56.0):
    _x = _kerbs.intersection(LineString([(123.5, nn), (131.6, nn)]))
    if not _x.is_empty:
        river_trees.append((_x.bounds[2] + 1.4, nn))
print("river trees", river_trees)
for p in new_trees:
    svg.circle(v.p(*p), v.mm(2.6), fill="#5f8050", stroke="#2f4227", sw=0.2, extra='fill-opacity="0.7"')
    svg.circle(v.p(*p), v.mm(0.25), fill="#1f2a18", stroke="none")
for p in river_trees:
    svg.circle(v.p(*p), v.mm(2.4), fill="#5f8050", stroke="#2f4227", sw=0.2, extra='fill-opacity="0.35" stroke-dasharray="0.8,0.5"')
    svg.circle(v.p(*p), v.mm(0.25), fill="#1f2a18", stroke="none")
N_NEW = len(new_trees) + len(river_trees)

# ---------------- entrances (8) and service
ENTR = [((103.2, 73.5), "1", "Brama Mostowa – wejście główne"), ((91.0, 76.6), "2", "wejście od skweru (podcień)"),
        ((114.6, 46.2), "3", "Wejście Obywatelskie (galeria Sejmiku)"), ((62.6, 69.8), "4", "wejście konferencyjne / bistro"),
        ((84.3, 42.6), "5", "wejście ogrodowe"), ((77.6, 41.5), "6", "rowerownia (50 st.)"),
        ((51.8, 23.6), "7", "brama ogrodowa (przejście publiczne)"), ((114.6, 47.9), "8", "zjazd do garażu (brama 4,0 m, rampa jednopasowa), dostawy")]
for (e, n), k, _ in ENTR:
    x, y = v.p(e, n)
    svg.circle((x, y), 2.1, fill=ACC, stroke="#ffffff", sw=0.25)
    svg.text((x, y + 0.75), k, size=2.1, anchor="middle", weight=700, fill="#ffffff")
# ramp arrow from Wybrzeże into segment
svg.line(v.p(123.0, 48.4), v.p(116.3, 48.0), stroke=INK, sw=0.35)
svg.poly([v.p(116.3, 48.0), v.p(117.7, 48.8), v.p(117.7, 47.2)], fill=INK, stroke="none")
# fire access lines along streets (far lane)
for ln in ([(36.0, -20.0), (49.0, 40.0), (55.0, 66.0)], [(122.0, 30.0), (119.5, 50.0), (115.0, 66.0), (110.0, 80.0)]):
    svg.poly([v.p(*p) for p in ln], fill="none", stroke="#c0392b", sw=0.45, close=False, extra='stroke-dasharray="2.2,1.2" stroke-opacity="0.8"')

# ---------------- access to plot 10/2 (kept, R-214): parcel outline + arrow from Wybrzeże
for it in S["dzialki"]["items"]:
    if it.get("nr") == "10/2":
        pg10 = Polygon(it["pts"]).buffer(0)
        model_rings(svg, v, pg10, fill="none", stroke="#6f6a63", sw=0.25, extra='stroke-dasharray="1.0,0.6"')
        c10 = pg10.centroid
        svg.line(v.p(c10.x + 8.5, c10.y), v.p(c10.x - 4.0, c10.y), stroke="#3a3632", sw=0.3)
        svg.poly([v.p(c10.x - 4.0, c10.y), v.p(c10.x - 2.6, c10.y + 0.8), v.p(c10.x - 2.6, c10.y - 0.8)], fill="#3a3632", stroke="none")
        svg.text(v.p(c10.x + 9.0, c10.y - 2.4), "dojazd do dz. 10/2 zachowany", size=1.8, anchor="end", fill="#3a3632")

# ---------------- boundaries
model_rings(svg, v, comp, fill="none", stroke="#2f6f8f", sw=0.35, extra='stroke-dasharray="3,1.2"')
model_rings(svg, v, inv, fill="none", stroke=ACC, sw=0.45, extra='stroke-dasharray="4,1,0.8,1"')

# ---------------- level spots (terrain, m n.p.m.)
for (e, n, t) in [(104.5, 80.0, "119,30"), (80.0, 84.0, "119,45"), (120.5, 45.0, "119,10"), (45.5, 30.0, "118,55"), (82.0, 18.0, "118,95"), (101.0, 34.0, "119,00")]:
    x, y = v.p(e, n)
    svg.poly([(x - 1.0, y), (x + 1.0, y), (x, y + 1.3)], fill=INK, stroke="none")
    svg.text((x + 1.5, y + 0.6), t, size=1.7)

# ---------------- street names & labels
for (e, n, t, rot) in [(42.0, 34.0, "ul. Mazowiecka", -77.6), (124.6, 58.0, "ul. Wybrzeże J. Słowackiego", -77.0), (84.0, 86.6, "PLAC MOSTOWY", -4.0),
                       (78.0, 112.0, "przyczółek Mostu Grunwaldzkiego", -19.6), (80.0, 6.5, "OGRÓD WOJEWÓDZTWA", 0), (89.2, 9.2, "ogród deszczowy", 0)]:
    svg.text(v.p(e, n), t, size=2.2 if t.isupper() else 2.0, anchor="middle", weight=600 if t.isupper() else 400, rot=rot, fill="#3a3632")

# ---------------- legend
lx = v.w_mm + 6
y = 8
svg.text((lx, y), "KONCEPCJA ZAGOSPODAROWANIA TERENU", size=3.4, weight=600); y += 4.6
svg.text((lx, y), "skala 1:500 · cienie: promienie z SW pod kątem 45°", size=2.2, fill="#4d4842"); y += 7
items = [("rect", "#ffffff", INK, "rzut dachów projektowanych (rzędne, liczba kondygnacji)"), ("rect", "#dcd8d1", "#6f6a63", "budynki istniejące"),
         ("hatch", "#7c7f86", None, "pokrycie dachu BIPV (fotowoltaika jako pokrycie)"), ("rect", GRANIT, None, "nawierzchnia z granitu strzegomskiego"),
         ("rect", CEGLA, None, "ścieżki z cegły i gruzu z wykopu (przepuszczalne)"), ("rect", TRAWA, None, "trawnik, zieleń urządzona"),
         ("rect", "#d6e2c6", "#9fb07f", "zachowane ogródki z drzewami (29/29)"), ("rect", DESZCZ, "#7ea7ad", "ogród deszczowy (retencja, zero odpływu)"),
         ("rect", "#efe2c4", "#b9a072", "plac zabaw"), ("tree_old", None, None, f"drzewa istniejące zachowane (w obszarze inwestycji: {N_KEPT_OI})"), ("tree_rem", None, None, "drzewa usuwane (6)"),
         ("tree_new", None, None, f"drzewa projektowane w granicy opracowania ({len(new_trees)})"),
         ("tree_prop", None, None, f"drzewa proponowane poza granicą — chodnik od rzeki ({len(river_trees)})"), ("line_trace", None, None, "ślad pierzei kwartału z 1934 r. (granit + brąz)"),
         ("line_fire", None, None, "drogi pożarowe (jezdnie ulic)"), 
         ("ent", None, None, "wejścia 1–8 (opis niżej)"), ("rect", "none", ACC, "obszar inwestycji"), ("rect", "none", "#2f6f8f", "granica opracowania konkursowego")]
for kind, f, s, t in items:
    if kind == "rect":
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=f, stroke=s or "none", sw=0.25)
    elif kind == "hatch":
        hp = svg.hatch("bipv_leg", spacing=1.0, angle=45, stroke=f, sw=0.12)
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=hp, stroke=f, sw=0.15)
    elif kind == "tree_old":
        svg.circle((lx + 3, y - 0.7), 1.5, fill="#93a77c", stroke="#fff", sw=0.1, extra='fill-opacity="0.6"')
    elif kind == "tree_rem":
        svg.circle((lx + 3, y - 0.7), 1.5, fill="none", stroke="#a39c92", sw=0.15, extra='stroke-dasharray="0.6,0.5"')
        svg.line((lx + 2, y - 1.7), (lx + 4, y + 0.3), stroke="#a39c92", sw=0.15)
    elif kind == "tree_new":
        svg.circle((lx + 3, y - 0.7), 1.5, fill="#5f8050", stroke="#2f4227", sw=0.15, extra='fill-opacity="0.7"')
    elif kind == "tree_prop":
        svg.circle((lx + 3, y - 0.7), 1.5, fill="#5f8050", stroke="#2f4227", sw=0.15, extra='fill-opacity="0.35" stroke-dasharray="0.8,0.5"')
    elif kind == "line_trace":
        svg.line((lx, y - 0.7), (lx + 6, y - 0.7), stroke="#8b6a3e", sw=0.55)
    elif kind == "line_fire":
        svg.line((lx, y - 0.7), (lx + 6, y - 0.7), stroke="#c0392b", sw=0.45, dash="2.2,1.2")
    elif kind == "line_axis":
        svg.line((lx, y - 0.7), (lx + 6, y - 0.7), stroke=ACC, sw=0.35, dash="0.8,1.0")
    elif kind == "ent":
        svg.circle((lx + 3, y - 0.7), 1.6, fill=ACC, stroke="none")
    svg.text((lx + 8.5, y), t, size=2.15)
    y += 4.4
y += 2
for (_, k, t) in ENTR:
    svg.text((lx, y), f"{k}", size=2.1, weight=700, fill=ACC); svg.text((lx + 4.5, y), t, size=2.1); y += 3.8
y += 3
for t in ["Zjazd do garażu (109 m.p., 55 EV) wyłącznie z Wybrzeża Słowackiego (6KDB/2);",
          "brak wjazdów z przyczółka (1KDG) i z ul. Mazowieckiej (MPZP §26 ust. 3).",
          "Rowery: 50 st. w parterze (wjazd od dziedzińca) + 20 na skwerze + 10 przy bramie.",
          "Retencja 151 m³ — zero odpływu deszczu miarodajnego do kanalizacji."]:
    svg.text((lx, y), t, size=2.0, fill="#3a3632"); y += 3.4
north_arrow(svg, (v.w_mm - 10, 12), 10)
scale_bar(svg, (8, v.h_mm + 7), 500, (0, 5, 10, 25, 50))

out = ROOT / "build" / "rysunki" / "zagospodarowanie_1-500.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "zagospodarowanie_1-500.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm+10:.0f}mm {svg.h_mm+10:.0f}mm;margin:0}}body{{margin:0}}</style></head><body><div style="padding:5mm">{svg.render()}</div></body></html>', encoding="utf-8")
print(out, round(svg.w_mm), round(svg.h_mm))
