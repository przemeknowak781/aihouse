#!/usr/bin/env python3
"""Rzuty kondygnacji 1:500 z podziałem na bloki funkcjonalne (Etap I, R-061): bloki = pomieszczenia scalone wg kategorii
funkcji (jak w aksonometrii), nazwy bloków i ich powierzchnie netto w legendzie przy rzucie; kondygnacje 1–4 (typowe)
na jednym rzucie z tabelą rozmieszczenia departamentów. Dane: model/budynek.json.
Wynik: build/rysunki/rzut_bloki_{id}_1-500.svg + docs/70_rysunki/podglady/rzuty_bloki_1-500.png
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from shapely.geometry import Polygon
from shapely.ops import unary_union
from umwd.svg import Svg, View, model_rings
import aksonometria as AX   # category(), CAT, mp()

BM = AX.BM
LV = {lv["id"]: lv for lv in BM["kondygnacje"]}
INK = "#1f1d1a"
SC = 500
NAMES = {"sejmik": "Sejmik", "public": "strefa wejściowa i konferencyjna", "office": "departamenty – pokoje biurowe", "lead": "Prezydium, Kancelaria Sejmiku, Zarząd",
         "meet": "sale narad", "social": "socjalne i WC", "tech": "magazyny, technika, IT", "core": "trzony", "corr": "komunikacja", "garage": "garaż, rampa, rowery"}
GROUPS = [("-2", "−2 · −7,00"), ("-1", "−1 · −3,75"), ("P", "PARTER · ±0,00"), ("1", "KONDYGNACJE 1–4 · +4,80 … +16,05 (typowe)"),
          ("5", "5 · +19,80"), ("6", "6 · +23,55"), ("S", "S · +27,30 — SEJMIK (+ galeria +30,90)")]


def draw_level(lid, title, below=True):
    lv = LV[lid]
    plate = AX.mp(lv.get("plyta"))
    allb = unary_union([AX.mp(LV[k].get("plyta")) for k in ("-1", "P", "1")])
    minx, miny, maxx, maxy = allb.bounds
    v = View(minx - 2, miny - 2, maxx + 2, maxy + 2, SC)
    LEGW = 62
    svg = Svg(v.w_mm + (0 if below else LEGW), (v.h_mm + 44) if below else (max(v.h_mm, 60) + 10))
    model_rings(svg, v, plate, fill="#5b5651", stroke=INK, sw=0.3)
    cats, areas = {}, {}
    for r in lv.get("pomieszczenia", []):
        g = AX.mp(r.get("poligon"))
        if g.is_empty:
            continue
        c = AX.category(r)
        cats.setdefault(c, []).append(g)
        areas[c] = areas.get(c, 0.0) + float(r.get("powierzchnia") or g.area)
    if lid == "S" and "ANT" in LV:
        for r in LV["ANT"].get("pomieszczenia", []):
            c = AX.category(r)
            areas["sejmik" if c == "sejmik" else c] = areas.get(c, 0.0) + float(r.get("powierzchnia") or 0)
    for c in ("corr", "garage", "tech", "social", "office", "lead", "meet", "public", "sejmik", "core"):
        if c in cats:
            model_rings(svg, v, unary_union(cats[c]), fill=AX.CAT[c][0], stroke="#ffffff", sw=0.05)
    # legend: blocks with areas
    plate_bottom = max(v.p(x, yy)[1] for g in ([plate] if plate.geom_type == "Polygon" else plate.geoms) for x, yy in g.exterior.coords)
    lx, y = (2.0, plate_bottom + 5.0) if below else (v.w_mm + 3, 4.0)
    if below:
        LEGW = v.w_mm - 2
    svg.text((lx, y), title, size=2.6, weight=600); y += 4.2
    tot = 0.0
    for c in ("sejmik", "lead", "public", "office", "meet", "social", "tech", "garage", "corr", "core"):
        if c in areas:
            svg.poly([(lx, y - 2.0), (lx + 4, y - 2.0), (lx + 4, y + 0.5), (lx, y + 0.5)], fill=AX.CAT[c][0], stroke="#8d877f", sw=0.1)
            svg.text((lx + 5.5, y), NAMES[c], size=1.75)
            svg.text((lx + LEGW - 4, y), f"{areas[c]:,.0f} m²".replace(",", " "), size=1.75, anchor="end")
            tot += areas[c]
            y += 3.0
    svg.line((lx, y - 1.6), (lx + LEGW - 4, y - 1.6), stroke=INK, sw=0.12)
    svg.text((lx + 5.5, y + 0.6), "razem (netto)", size=1.8, weight=600)
    svg.text((lx + LEGW - 4, y + 0.6), f"{tot:,.0f} m²".replace(",", " "), size=1.8, anchor="end", weight=600)
    y += 4.5
    if lid == "1":
        svg.text((lx, y), "departamenty na kondygnacjach:", size=1.8, weight=600); y += 3.0
        for k in ("1", "2", "3", "4"):
            deps = sorted({r.get("kod_grupy") for r in LV[k].get("pomieszczenia", []) if r.get("kind") == "office"})
            svg.text((lx, y), f"{k}:  " + ", ".join(deps), size=1.75); y += 2.7
    return svg


def main():
    out = []
    for lid, title in GROUPS:
        if lid not in LV:
            continue
        svg = draw_level(lid, title)
        (ROOT / "build" / "rysunki" / f"rzut_bloki_{lid}_1-500.svg").write_text(svg.render(), encoding="utf-8")
        out.append(svg)
    W = max(s.w_mm for s in out) * 2 + 10
    body = '<div style="display:flex;flex-wrap:wrap;gap:4mm;width:%dmm">' % W + "".join(f"<div>{s.render()}</div>" for s in out) + "</div>"
    H = sum(s.h_mm for s in out) / 2 + 60
    html = ROOT / "docs" / "70_rysunki" / "podglady" / "rzuty_bloki_1-500.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W + 10:.0f}mm {H:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{body}</body></html>', encoding="utf-8")
    print(f"{W + 10:.0f} {H:.0f}")


if __name__ == "__main__":
    main()
