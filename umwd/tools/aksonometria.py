#!/usr/bin/env python3
"""Aksonometria funkcjonalna (rozstrzelone kondygnacje) z modelu pomieszczeń model/budynek.json.

Widok od pn.-wsch. (az. 31,3° – oś łuku Bramy Mostowej), rzut skrócony 0,55, kondygnacje rozsunięte.
Kolory wg kategorii funkcji (Sejmik / obsługa obywateli / biura / sale narad / socjalne+WC / techniczne / komunikacja / garaż).
Wynik: build/rysunki/aksonometria_funkcjonalna.svg + docs/70_rysunki/podglady/aksonometria_funkcjonalna.png
"""
import sys, json, math, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon
from shapely.ops import unary_union
from umwd.svg import Svg

BM = json.loads((ROOT / "model" / "budynek.json").read_text(encoding="utf-8"))
INK = "#1f1d1a"
CAT = {
    "sejmik": ("#a8483a", "Sejmik: sala obrad, komisje, kluby, hol, kuluar"),
    "public": ("#d9a066", "obsługa obywateli: Hala Obywatelska, kancelaria, konferencje, bistro"),
    "office": ("#ece4d6", "biura departamentów (24 / 32 m², moduł 1,35 m)"),
    "lead":   ("#dcb39e", "Prezydium i Kancelaria Sejmiku, Zarząd Województwa"),
    "meet":   ("#c3a27a", "sale narad i spotkań"),
    "social": ("#b7c3ae", "pokoje socjalne, WC"),
    "tech":   ("#cfcac3", "magazyny, IT, technika"),
    "core":   ("#4f4a45", "trzony: klatki, dźwigi, przedsionki z MOE"),
    "corr":   ("#ffffff", "komunikacja pozioma"),
    "garage": ("#c6d0d8", "garaż, rampa, rowerownia"),
}
PUBLIC_WORDS = ("hala", "hol", "kancelaria", "bistro", "foyer", "konferenc", "obywatel", "punkt obsługi", "galeria", "kuluar", "szatnia")


def category(r):
    kind, g, name = r.get("kind", ""), r.get("kod_grupy", ""), r.get("nazwa", "").lower()
    if kind.startswith("core") or kind == "shaft":
        return "core"
    if kind in ("garage", "ramp") or "garaż" in name or "rowerow" in name:
        return "garage"
    if kind == "corridor" or (g == "KW" and "korytarz" in name):
        return "corr"
    if g in ("SWD",) or (g == "PHS" and r.get("numer", "").startswith("PHS.05")):
        return "sejmik"
    if g in ("KS", "CZ"):
        return "lead"
    if g in ("SW", "SK") or any(w in name for w in PUBLIC_WORDS):
        return "public"
    if g == "SN" or "sala narad" in name or "sala spotkań" in name:
        return "meet"
    if g in ("PS", "PHS") or "wc" in name or "socjal" in name:
        return "social"
    if g in ("PP", "PPT", "PPM", "PR", "IT") and kind != "office":
        return "tech"
    if kind == "office" or re.match(r"^D|^GW", g):
        return "office"
    return "tech"


def mp(coords):
    out = []
    for poly in coords or []:
        if poly:
            try:
                out.append(Polygon(poly[0], poly[1:]).buffer(0))
            except Exception:
                pass
    return unary_union(out) if out else Polygon()


# ---------------------------------------------------------------- projection
AZ = 31.3
f = (math.sin(math.radians(AZ)), math.cos(math.radians(AZ)))           # toward the viewer
rgt = (f[1], -f[0])                                                       # screen right
CE, CN = 88.0, 45.0
KSQ, KZ, SC = 0.50, 1.0, 2.2          # plan squash, vertical, mm per metre
LEVELS = ["-1", "P", "1", "2", "3", "4", "5", "6", "S"]
GAP = 28.0                            # diagram metres between storeys

W_MM, H_MM = 420.0, 675.0
svg = Svg(W_MM, H_MM)
OX, OY = 190.0, 125.0 + 8 * 28.0 * 2.2


def Pp(e, n, zlev):
    x = (e - CE) * rgt[0] + (n - CN) * rgt[1]
    y = (e - CE) * f[0] + (n - CN) * f[1]
    return (OX + x * SC, OY + (y * KSQ - zlev) * SC)


def ring(coords, zl):
    return [Pp(x, y, zl) for x, y in coords]


def draw_geom(g, zl, fill, stroke="none", sw=0.1, extra=""):
    for p in ([g] if g.geom_type == "Polygon" else list(getattr(g, "geoms", []))):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        rings = [ring(p.exterior.coords, zl)] + [ring(h.coords, zl) for h in p.interiors]
        svg.multipoly(rings, fill=fill, stroke=stroke, sw=sw, extra=extra)


lv_by = {lv["id"]: lv for lv in BM["kondygnacje"]}
labels = []
for i, lid in enumerate(LEVELS):
    lv = lv_by.get(lid)
    if not lv:
        continue
    zl = i * GAP
    plate = mp(lv.get("plyta"))
    if lid == "S" and "ANT" in lv_by:
        pass
    # slab thickness (dark band visible on front edges) + plate
    draw_geom(plate, zl - 0.9, "#3a3632")
    draw_geom(plate, zl, "#5b5651")
    cats = {}
    for r in lv.get("pomieszczenia", []):
        g = mp(r.get("poligon"))
        if g.is_empty:
            continue
        c = category(r)
        cats.setdefault(c, []).append(g)
        if c in ("sejmik", "public", "lead") and g.area > 34:
            labels.append((g.representative_point(), zl, r["nazwa"].split("(")[0].strip(), c))
    for c in ("corr", "garage", "tech", "social", "office", "lead", "meet", "public", "sejmik", "core"):
        if c in cats:
            draw_geom(unary_union(cats[c]), zl, CAT[c][0], stroke="#ffffff" if c != "core" else "none", sw=0.06)
    # storey tag at left
    bx = min(Pp(x, y, zl)[0] for x, y in plate.exterior.coords) if plate.geom_type == "Polygon" else OX - 120
    by = Pp(CE, CN, zl)[1]
    rz = lv.get("rzedna")
    tag = {"-1": "−1", "P": "P"}.get(lid, lid)
    svg.text((22, by + 1), tag, size=6.0, weight=700, fill=INK)
    svg.text((36, by), f"+{float(rz):.2f}".replace(".", ",").replace("+-", "−"), size=2.4, fill="#4d4842")
    deps = sorted({r.get("kod_grupy") for r in lv.get("pomieszczenia", []) if r.get("kind") == "office"})
    if deps:
        svg.text((36, by + 3.4), "departamenty: " + ", ".join(deps), size=2.0, fill="#6a645d")
    svg.line((60, by - 0.8), (bx - 4, by - 0.8), stroke="#b9b2a6", sw=0.12, dash="0.8,0.8")

# key labels (Sejmik + public spaces), de-duplicated by name per level, spread vertically (min 3.3 mm)
seen, items = set(), []
for pt, zl, name, c in labels:
    if (name, zl) in seen:
        continue
    seen.add((name, zl))
    x, y = Pp(pt.x, pt.y, zl)
    items.append([y, y, x, name, c])
items.sort()
for i in range(1, len(items)):
    if items[i][0] < items[i - 1][0] + 3.3:
        items[i][0] = items[i - 1][0] + 3.3
tx = W_MM - 92
for ty, y, x, name, c in items:
    col = CAT[c][0]
    svg.poly([(x, y), (tx - 12, y), (tx - 6, ty), (tx - 2, ty)], fill="none", stroke=col, sw=0.18, close=False)
    svg.circle((x, y), 0.8, fill=col, stroke="#ffffff", sw=0.2)
    svg.text((tx, ty + 0.8), name if len(name) < 40 else name[:38] + "…", size=2.1, fill=INK)

# legend
lx, ly = 22.0, 30.0
svg.text((lx, 14), "AKSONOMETRIA FUNKCJONALNA", size=4.6, weight=600)
svg.text((lx, 20), "kondygnacje rozsunięte · widok od Mostu Grunwaldzkiego (pn.-wsch.)", size=2.4, fill="#4d4842")
for k, (col, txt) in CAT.items():
    svg.poly([(lx, ly - 2.4), (lx + 6, ly - 2.4), (lx + 6, ly + 0.8), (lx, ly + 0.8)], fill=col, stroke="#8d877f", sw=0.15)
    svg.text((lx + 8.5, ly), txt, size=2.2)
    ly += 4.6

out = ROOT / "build" / "rysunki" / "aksonometria_funkcjonalna.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "aksonometria_funkcjonalna.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W_MM + 10:.0f}mm {H_MM + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{W_MM + 10:.0f} {H_MM + 10:.0f}")
