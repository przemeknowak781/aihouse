#!/usr/bin/env python3
"""Schemat dostępności (R.III ust.1 pkt 8, M.13): parter z otoczeniem 1:400 – wejścia w poziomie chodnika, ścieżki
dotykowe, tyflomapy, komfortka, WC dostępne, pętle indukcyjne, dźwigi publiczne, MOE; macierz kondygnacji liczona
z modelu pomieszczeń (model/budynek.json) – jednocześnie kontrola kompletności (brak = czerwony).
Teksty i parametry wg koncepcja_wybrana.md v1.1 rozdz. 11 oraz koncepcja.json (rdzenie: P1/P2 1 600 kg, kabiny 1,5 × 2,1 m;
dźwig T 2 000 kg w narożniku SE segmentu – rysowany z koncepcja.json, bo model pomieszczeń może mieć jeszcze układ v1.0).
Wynik: build/rysunki/schemat_dostepnosci.svg, docs/70_rysunki/podglady/schemat_dostepnosci.png
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from umwd.svg import Svg, View, model_rings, north_arrow, scale_bar
from umwd.siteplan import load_site, poly_of

S = load_site()
BM = json.loads((ROOT / "model" / "budynek.json").read_text(encoding="utf-8"))
KC = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
RDZ = KC["rdzenie"]
INK, ACC = "#1f1d1a", "#a8483a"
YEL, BLUE, GREEN = "#e3b505", "#2f6f9f", "#3c8d5a"
LV = {lv["id"]: lv for lv in BM["kondygnacje"]}
# wejścia – jak w tools/zagospodarowanie.py, ale 1 i 2 w linii szklenia pod podcieniem (R 11 m; v 26,70);
# 3 – Wejście Obywatelskie w elewacji wsch. wieży (wnęka v 1,4–6,8), 8 – portal obsługi w segmencie (brama garażu v −0,40…−4,40)
ENTR = [((101.98, 71.5), "1"), ((90.14, 72.03), "2"), ((113.08, 54.36), "3"), ((62.6, 69.8), "4"), ((84.3, 42.6), "5"),
        ((77.6, 41.5), "6"), ((51.8, 23.6), "7"), ((114.6, 47.9), "8")]


def mp(coords):
    out = []
    for poly in coords or []:
        if poly:
            try:
                out.append(Polygon(poly[0], poly[1:]).buffer(0))
            except Exception:
                pass
    return unary_union(out) if out else Polygon()


def rooms(lid):
    return LV[lid].get("pomieszczenia", []) if lid in LV else []


def find(lid, *words, kind=None):
    out = []
    for r in rooms(lid):
        n = r["nazwa"].lower()
        if all(w in n for w in words) and (kind is None or r.get("kind") == kind):
            out.append(r)
    return out


def cen(r):
    g = mp(r["poligon"])
    c = g.representative_point()
    return (c.x, c.y)


import os
SCALE_D = int(os.environ.get("UMWD_SCALE", "400"))
v = View(40, 10, 130, 92, SCALE_D)
RIGHT = 150
svg = Svg(v.w_mm + RIGHT, max(v.h_mm, 225) + 16)
u = S["ulice_i_sytuacja"]
for key, col in (("jezdnie", "#efeeea"), ("chodniki", "#f7f5f1"), ("trawniki", "#e9eee0")):
    for it in u[key]:
        if it.get("zamknieta", True):
            pg = poly_of(it)
            if pg is not None:
                model_rings(svg, v, pg, fill=col, stroke="none")
for it in u["krawezniki"]:
    svg.poly([v.p(*p) for p in it["pts"]], fill="none", stroke="#b8b2a9", sw=0.12, close=False)
for b in S["budynki"]["items"]:
    pg = poly_of(b)
    if pg is not None:
        model_rings(svg, v, pg, fill="#e1ddd6", stroke="#8d877f", sw=0.15)

P = LV["P"]
model_rings(svg, v, mp(P["plyta"]), fill="#5b5651", stroke=INK, sw=0.3)
HL = {}
for r in rooms("P"):
    g = mp(r["poligon"])
    n = r["nazwa"].lower()
    col = "#f4f1ec"
    if r["kind"].startswith("core"):
        col = "#9a948c"
    if r["kind"] == "core_lift" and ("publiczny" in n):
        col = BLUE; HL.setdefault("lift", []).append(r)
    elif r["kind"] == "core_lift" and ("ewakuac" in n):
        col = "#6f8fae"
    elif "komfortka" in n:
        col = ACC; HL.setdefault("komf", []).append(r)
    elif "dostępna" in n or "dostępną" in n:
        col = "#e2a49a"; HL.setdefault("wc", []).append(r)
    elif "moe" in n:
        col = "#c9b26a"; HL.setdefault("moe", []).append(r)
    elif any(w in n for w in ("hala obywatelska", "lobby", "łącznik holu", "foyer")):
        col = "#f3e3c8"
    elif any(w in n for w in ("kancelaria ogólna", "sala konferencyjna")):
        col = "#d8c7e3"; HL.setdefault("loop", []).append(r)
    elif "pokój cichy" in n:
        col = "#d6e4dc"; HL.setdefault("quiet", []).append(r)
    model_rings(svg, v, g, fill=col, stroke="#ffffff", sw=0.08)

# tactile guidance paths (yellow): entrances → information/tyflomap → public lifts; garage lifts → hall
hall = find("P", "hala obywatelska")
lob = find("P", "wejście obywatelskie")
foyer = find("P", "foyer")
lift_pub = HL.get("lift", [])
lift_c = [cen(r) for r in lift_pub]
liftP = (sum(c[0] for c in lift_c) / len(lift_c), sum(c[1] for c in lift_c) / len(lift_c)) if lift_c else None
info = cen(hall[0]) if hall else None
routes = []
if info and liftP:
    routes += [[(108.5, 84.0), (103.4, 74.0), (101.98, 71.5), info, liftP],           # przystanek / most → wejście 1 → informacja → dźwigi
               [(119.3, 55.6), (113.08, 54.36), cen(lob[0]) if lob else (110.5, 53.5), liftP],
               [(84.3, 40.4), (84.3, 42.6), info]]
if foyer:
    routes.append([(58.5, 71.0), (62.6, 69.8), cen(foyer[0])])
for rt in routes:
    svg.poly([v.p(*p) for p in rt], fill="none", stroke=YEL, sw=1.1, close=False, extra='stroke-linejoin="round" stroke-linecap="round"')
    svg.poly([v.p(*p) for p in rt], fill="none", stroke="#8a6d00", sw=0.15, close=False, extra='stroke-dasharray="0.5,0.5"')
# tyflomaps at entrances 1, 3, 4 and at the information desk
for (e, n) in ((102.0, 72.2), (111.3, 53.6), (63.8, 69.0)) + ((info,) if info else ()):
    x, y = v.p(e, n)
    svg.poly([(x - 1.3, y - 1.3), (x + 1.3, y - 1.3), (x + 1.3, y + 1.3), (x - 1.3, y + 1.3)], fill=YEL, stroke=INK, sw=0.2)
    svg.text((x, y + 0.75), "T", size=2.0, anchor="middle", weight=700)
# entrances
for (e, n), k in ENTR:
    x, y = v.p(e, n)
    svg.circle((x, y), 2.0, fill=GREEN, stroke="#ffffff", sw=0.3)
    svg.text((x, y + 0.75), k, size=2.0, anchor="middle", weight=700, fill="#ffffff")


def mark(r, letter, col):
    x, y = v.p(*cen(r))
    svg.circle((x, y), 1.9, fill="#ffffff", stroke=col, sw=0.35)
    svg.text((x, y + 0.7), letter, size=1.9, anchor="middle", weight=700, fill=col)


for r in HL.get("komf", []):
    mark(r, "K", ACC)
for r in HL.get("wc", []):
    mark(r, "W", "#b5534a")
for r in HL.get("moe", []):
    mark(r, "M", "#8a6d00")
for r in HL.get("loop", []):
    mark(r, "P", "#6a4f86")
for r in HL.get("lift", []):
    mark(r, "D", BLUE)
# dźwig T (osobowo-towarowy 2 000 kg, kabina 1,5 × 2,7 m) – narożnik SE segmentu wg koncepcja.json (v1.1, P-I5)
if "T" in RDZ:
    gT = Polygon(RDZ["T"]["obrys_en"]).buffer(0)
    model_rings(svg, v, gT, fill="#8a7a66", stroke=INK, sw=0.2)
    x, y = v.p(gT.centroid.x, gT.centroid.y)
    svg.circle((x, y), 1.9, fill="#ffffff", stroke="#6b5a46", sw=0.35)
    svg.text((x, y + 0.7), "T", size=1.9, anchor="middle", weight=700, fill="#6b5a46")
north_arrow(svg, (v.w_mm - 10, 12), 9)
scale_bar(svg, (8, v.h_mm + 8), SCALE_D, (0, 5, 10, 20))

# ---------------------------------------------------------------- right panel: legend + storey matrix (from model)
lx = v.w_mm + 8
y = 10
svg.text((lx, y), "SCHEMAT DOSTĘPNOŚCI", size=3.8, weight=600); y += 5
svg.text((lx, y), f"parter z otoczeniem 1:{SCALE_D} · wszystkie wejścia w poziomie chodnika (±0,00 = 119,30)", size=2.0, fill="#4d4842"); y += 7
leg = [("circle", GREEN, "1–8", "wejścia bezprogowe, drzwi automatyczne"), ("line", YEL, "", "ścieżki dotykowe: przystanki na przyczółku, wejścia, garaż → informacja → dźwigi"),
       ("sq", YEL, "T", "tyflomapy przy wejściach i informacji; niski blat informacji i kancelarii"),
       ("mk", ACC, "K", "komfortka 12 m² (3,0 × 4,0 m), 14 m od wejścia głównego (WT § 85a)"),
       ("mk", "#b5534a", "W", "WC dostępne w każdej strefie i na każdej kondygnacji, także na −1 (MDS)"),
       ("mk", "#6a4f86", "P", "pętle indukcyjne: kancelaria, sale konferencyjne, sala obrad, komisje, kluby"),
       ("mk", BLUE, "D", "2 dźwigi publiczne P1, P2: 1 600 kg, kabiny 1,5 × 2,1 m (M.13), redundancja, głos + obraz"),
       ("mk", "#6b5a46", "T", "dźwig T 2 000 kg (kabina 1,5 × 2,7 m) w narożniku SE segmentu – dostawy, odpady"),
       ("mk", "#8a6d00", "M", "MOE 1,5 × 1,5 m poza biegiem na podestach klatek A, B, C: krzesło ewak., interkom"),
       ("rect", "#d6e4dc", "", "pokój cichy 16 m² przy Hali Obywatelskiej")]
for kind, col, t, txt in leg:
    if kind == "circle":
        svg.circle((lx + 2.5, y - 0.8), 2.0, fill=col, stroke="none"); svg.text((lx + 2.5, y), t, size=1.5, anchor="middle", weight=700, fill="#fff")
    elif kind == "line":
        svg.line((lx, y - 0.8), (lx + 5, y - 0.8), stroke=col, sw=1.1)
    elif kind == "sq":
        svg.poly([(lx + 1, y - 2.1), (lx + 3.8, y - 2.1), (lx + 3.8, y + 0.6), (lx + 1, y + 0.6)], fill=col, stroke=INK, sw=0.2); svg.text((lx + 2.4, y), t, size=1.8, anchor="middle", weight=700)
    elif kind == "mk":
        svg.circle((lx + 2.5, y - 0.8), 1.9, fill="#fff", stroke=col, sw=0.35); svg.text((lx + 2.5, y), t, size=1.8, anchor="middle", weight=700, fill=col)
    else:
        svg.poly([(lx, y - 2.1), (lx + 5, y - 2.1), (lx + 5, y + 0.6), (lx, y + 0.6)], fill=col, stroke="#8d877f", sw=0.15)
    svg.text((lx + 7.5, y), txt, size=1.95)
    y += 4.2
y += 4
svg.text((lx, y), "KONDYGNACJE – STAN MODELU (liczone z rzutów)", size=2.6, weight=600); y += 4.6
cols = ["kond.", "WC dostępne", "MOE (klatki)", "dźwigi publ./ewak.", "pętla indukcyjna"]
cx = [lx, lx + 16, lx + 44, lx + 72, lx + 104]
for x, c in zip(cx, cols):
    svg.text((x, y), c, size=1.85, weight=600)
y += 1.3
svg.line((lx, y), (lx + RIGHT - 14, y), stroke=INK, sw=0.15); y += 3.4
issues = []
for lid in ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT"]:
    if lid not in LV:
        continue
    rs = rooms(lid)
    wc = [r for r in rs if ("dostępn" in r["nazwa"].lower() or "komfortka" in r["nazwa"].lower())]
    moe = [r for r in rs if "moe" in r["nazwa"].lower()]
    lifts = [r for r in rs if r["kind"] == "core_lift" and ("publiczny" in r["nazwa"].lower() or "ewakuac" in r["nazwa"].lower())]
    loop = [r for r in rs if any(w in r["nazwa"].lower() for w in ("sala obrad", "sala komisji", "klubu", "konferencyjna", "kancelaria ogólna"))]
    need_wc = lid not in ("ANT",)
    vals = [(len(wc), need_wc), (len(moe), lid not in ("ANT",)), (len(lifts), True), (len(loop), False)]
    svg.text((cx[0], y), {"-2": "−2", "-1": "−1"}.get(lid, lid), size=1.95, weight=600)
    for x, (n, req) in zip(cx[1:], vals):
        ok = n > 0 or not req
        svg.text((x, y), str(n) if n else ("—" if not req else "brak"), size=1.95, fill=(GREEN if n else ("#8d877f" if not req else "#c0392b")), weight=600 if not ok else 400)
        if not ok:
            issues.append((lid, cols[cx.index(x)]))
    y += 3.3
y += 2
if issues:
    svg.text((lx, y), "Do uzupełnienia w rzutach: " + "; ".join(f"{a} – {b}" for a, b in issues), size=1.9, fill="#c0392b"); y += 3.3
for t in ["Wszystkie wejścia bez schodów i pochylni (±0,00 = 119,30 = poziom skweru i Wybrzeża, chodnik ≤ 2 %).",
          "Sala obrad: prezydium i mównica na poziomie podłogi, pochylnie ≤ 5 % do każdego rzędu,",
          "stanowisko dla wózka w każdym rzędzie, 3 miejsca na galerii (P1/P2 bez stopni) + 2 wśród gości,",
          "tłumacz PJM w kadrze transmisji, napisy na żywo. Ewakuacja OzN: MOE, dźwig ewakuacyjny R",
          "(PN-EN 81-76), sygnalizatory optyczne alarmu w WC i przestrzeniach ogólnodostępnych.",
          "Garaż: 6 miejsc OzN 3,6 × 5,0 m przy trzonach A i B na −1, na posadzce (nie w stackerach);",
          "WC dostępne na −1. Pokój matki z dzieckiem na kondygnacji S, przewijaki w WC holu i konferencji.",
          "Ogród Województwa bez barier (≤ 4 %, poza strefami korzeni), brama ogrodowa w poziomie chodnika (≤ 2 %)."]:
    svg.text((lx, y), t, size=1.9, fill="#3a3632"); y += 3.1

out = ROOT / "build" / "rysunki" / f"schemat_dostepnosci_1-{SCALE_D}.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "schemat_dostepnosci.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm + 10:.0f}mm {svg.h_mm + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{svg.w_mm + 10:.0f} {svg.h_mm + 10:.0f}")
print("ISSUES", issues)
