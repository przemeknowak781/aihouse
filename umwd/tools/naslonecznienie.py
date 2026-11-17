#!/usr/bin/env python3
"""Analiza zacieniania i czasu nasłonecznienia w dniach równonocy (Etap I – schemat; Etap II – dowód WT § 13 / § 60).

* plan 1:750: cienie projektowanej zabudowy co 1 h (7:00–17:00 czasu urzędowego) 20 marca 2027 (CET) – kontury,
  zabudowa sąsiednia i jej okna chronione;
* tabela: czas nasłonecznienia okien chronionych (Wybrzeże J. Słowackiego 5, Mazowiecka 19) – suma i najdłuższy
  ciągły okres, oba dni równonocy (20.03 CET, 23.09 CEST), krok 5 min, zabudowa projektowana + istniejąca.
Wynik: build/rysunki/naslonecznienie.svg, docs/70_rysunki/podglady/naslonecznienie.png, docs/70_rysunki/naslonecznienie.json
"""
import sys, json, math, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from umwd import shadow as SH
from umwd.sun import TZ
from umwd.svg import Svg, View, model_rings, north_arrow, scale_bar
from umwd.siteplan import load_site, poly_of

S = load_site()
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
SAS = json.loads((ROOT / "model" / "sasiedzi.json").read_text(encoding="utf-8"))
Z0 = 119.30
B = {b["id"]: b for b in K["bryly"]}
OURS = [(Polygon(B["W"]["obrys_ccw"]).buffer(0), 0.0, B["W"]["dach"]["attyka"]["wzgl"]),
        (Polygon(B["M"]["obrys_ccw"]).buffer(0), 0.0, B["M"]["dach"]["gzyms_attyka"]["wzgl"]),
        (Polygon(B["S"]["obrys_ccw"]).buffer(0), 0.0, B["S"]["dach"]["attyka"]["wzgl"])]
NB = []
for b in S["budynki"]["items"]:
    pg = poly_of(b)
    if pg is not None and pg.area > 5:
        top = b.get("gora_szac_H", b["teren_wokol_H"]["min"] + b.get("wysokosc_szac_m", 6)) - Z0
        NB.append((pg, b["teren_wokol_H"]["min"] - Z0, top, b.get("nazwa")))
PRISMS = OURS + [(pg, z0, z1) for pg, z0, z1, _ in NB]

# protected windows: (label, point just outside façade, sill z rel., façade normal azimuth (grid))
ws5 = SAS["budynki"][1]["poziomy_szac_m_npm"]
m19 = SAS["budynki"][0]["poziom_0_00_m_npm"]["wartosc"]
WIN = []
for i, n in enumerate((13.0, 16.5, 20.0, 23.5)):
    WIN.append((f"WS 5 – front od Wybrzeża, parter, oś {i + 1}", (118.75, n), ws5["parter"] + 0.9 - Z0, 88.6))
    WIN.append((f"WS 5 – front od Wybrzeża, I p., oś {i + 1}", (118.75, n), ws5["I_p"] + 0.9 - Z0, 88.6))
for i, n in enumerate((12.5, 16.0, 19.5, 23.0)):
    WIN.append((f"WS 5 – oficyna od ogrodu, parter, oś {i + 1}", (101.85, n), ws5["parter"] + 0.9 - Z0, 267.9))
    WIN.append((f"WS 5 – oficyna od ogrodu, I p., oś {i + 1}", (101.85, n), ws5["I_p"] + 0.9 - Z0, 267.9))
for i, t in enumerate((0.2, 0.45, 0.7, 0.92)):
    a, b = (60.5, -7.93), (64.09, 5.7)
    p = (a[0] + (b[0] - a[0]) * t + 0.35, a[1] + (b[1] - a[1]) * t - 0.09)
    WIN.append((f"Maz. 19 – od podwórza, parter, oś {i + 1}", p, m19 - 1.15 + 0.9 - Z0 + 1.0, 104.8))
    WIN.append((f"Maz. 19 – od podwórza, I p., oś {i + 1}", p, m19 + 3.69 + 0.9 - Z0, 104.8))


def own_excluded(pt):
    P = Point(pt)
    return [pr for pr in PRISMS if not pr[0].buffer(0.6).contains(P)]


def analyse():
    rows = []
    days = SH.equinox_dates(2027)
    for lab, pt, z, naz in WIN:
        rec = {"okno": lab, "e": pt[0], "n": pt[1], "z_parapet_wzgl": round(z, 2), "azymut_normalnej": naz}
        for d in days:
            tot, best = SH.sunlight_minutes(pt, z, naz, own_excluded(pt), d)
            tot0, best0 = SH.sunlight_minutes(pt, z, naz, [pr for pr in own_excluded(pt) if pr not in OURS], d)
            rec[d.isoformat()] = {"suma_min": tot, "najdluzszy_ciagly_min": best, "bez_projektu_suma_min": tot0}
        rows.append(rec)
    return rows, days


def draw(rows, days):
    v = View(30, -25, 150, 105, 750)
    LEG = 142
    from shapely.geometry import box as _box
    VB = _box(30, -25, 150, 105)
    svg = Svg(v.w_mm + LEG, max(v.h_mm, 200) + 18)
    u = S["ulice_i_sytuacja"]
    for key, col in (("jezdnie", "#efeeea"), ("chodniki", "#f7f5f1"), ("trawniki", "#e9eee0")):
        for it in u[key]:
            if it.get("zamknieta", True):
                pg = poly_of(it)
                if pg is not None:
                    model_rings(svg, v, pg, fill=col, stroke="none")
    for w in S["woda"]["linia_brzegu"]:
        svg.poly([v.p(*p) for p in w["pts"]], fill="none", stroke="#9fb8c0", sw=0.3, close=False)
    d0 = days[0]
    # ---- heat map: hours in shadow of the PROPOSED buildings (7:00–17:00, step 10 min), 0.5 m grid
    import numpy as np, base64, io
    import shapely
    from PIL import Image
    E0, E1, N0, N1, STEP = 30.0, 150.0, -25.0, 105.0, 0.5
    xs_ = np.arange(E0 + STEP / 2, E1, STEP); ys_ = np.arange(N0 + STEP / 2, N1, STEP)
    gx, gy = np.meshgrid(xs_, ys_)
    cnt = np.zeros(gx.shape)
    foot = unary_union([p for p, _, _ in OURS])
    nsteps = 0
    for t in SH.times(d0, "07:00", "17:00", 10):
        az, el = SH.sun_grid(t)
        if el <= 0.5:
            continue
        sh = unary_union([SH.shadow_of_prism(fp, z0, z1, az, el) for fp, z0, z1 in OURS]).difference(foot)
        shapely.prepare(sh)
        cnt += shapely.contains_xy(sh, gx, gy)
        nsteps += 1
    hrs = cnt * 10 / 60.0
    classes = [(0.0, None), (0.5, (233, 238, 244)), (1.5, (205, 219, 233)), (3.0, (164, 189, 214)), (5.0, (113, 148, 186)), (7.0, (66, 103, 150))]
    img = np.full(gx.shape + (4,), 0, dtype=np.uint8)
    for th, col in classes:
        if col:
            m = hrs >= th
            img[m] = (*col, 235)
    img = img[::-1]
    buf = io.BytesIO(); Image.fromarray(img, "RGBA").save(buf, "PNG")
    x0, y0 = v.p(E0, N1); x1, y1 = v.p(E1, N0)
    svg.image((x0, y0), x1 - x0, y1 - y0, "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode(), extra='preserveAspectRatio="none"')
    # orientation contours at 9, 12, 15 h
    for hh, col in ((9, "#2c4f7c"), (12, "#7a6a3a"), (15, "#a8483a")):
        t = datetime.datetime(d0.year, d0.month, d0.day, hh, 0, tzinfo=TZ)
        az, el = SH.sun_grid(t)
        sh = unary_union([SH.shadow_of_prism(fp, z0, z1, az, el) for fp, z0, z1 in OURS]).difference(foot).intersection(VB)
        model_rings(svg, v, sh, fill="none", stroke=col, sw=0.3, extra='stroke-dasharray="1.6,0.8"')
        far = max([c for g in ([sh] if sh.geom_type == "Polygon" else sh.geoms) if g.geom_type == "Polygon" for c in g.exterior.coords],
                  key=lambda c: (c[0] - 96) * math.sin(math.radians(az + 180)) + (c[1] - 55) * math.cos(math.radians(az + 180)))
        x, y = v.p(*far)
        svg.text((x + 1, y - 1), f"cień {hh}:00", size=2.0, fill=col, weight=600)
    svg.poly([(v.w_mm, 0), (v.w_mm + LEG, 0), (v.w_mm + LEG, svg.h_mm), (v.w_mm, svg.h_mm)], fill="#ffffff", stroke="none")
    self_legend = [(0.5, (233, 238, 244), "0,5–1,5 h"), (1.5, (205, 219, 233), "1,5–3 h"), (3.0, (164, 189, 214), "3–5 h"), (5.0, (113, 148, 186), "5–7 h"), (7.0, (66, 103, 150), "> 7 h")]
    for pg, z0, z1, name in NB:
        model_rings(svg, v, pg, fill="#dcd8d1", stroke="#6f6a63", sw=0.2)
    for fp, z0, z1 in OURS:
        model_rings(svg, v, fp, fill="#ffffff", stroke="#1f1d1a", sw=0.45)
    # protected windows markers (ground floor only to keep it legible)
    for r in rows:
        if "parter" in r["okno"]:
            ok = min(r[d.isoformat()]["suma_min"] for d in days) >= 90
            svg.circle(v.p(r["e"], r["n"]), 1.0, fill="#3c8d5a" if ok else "#c0392b", stroke="#ffffff", sw=0.2)
    for (e, n, t) in [(110.0, 19.0, "WS 5"), (54.5, -1.0, "MAZ. 19"), (90.0, 58.0, "WIEŻA"), (62.0, 38.0, "SKRZYDŁO")]:
        svg.text(v.p(e, n), t, size=2.2, anchor="middle", weight=600, fill="#3a3632")
    north_arrow(svg, (v.w_mm - 10, 12), 9)
    scale_bar(svg, (8, v.h_mm + 8), 750, (0, 10, 20, 50))
    # legend + table
    lx = v.w_mm + 6
    y = 9
    svg.text((lx, y), "ZACIENIENIE W DNIU RÓWNONOCY", size=3.6, weight=600); y += 5
    svg.text((lx, y), "20 marca 2027 — mapa czasu zacienienia przez zabudowę projektowaną (krok 10 min), czas urzędowy", size=2.1, fill="#4d4842"); y += 3.4
    svg.text((lx, y), "kontury cienia o 9, 12, 15; 23.09 (CEST) – wynik w tabeli. Słońce: algorytm NOAA, 51,11° N / 17,05° E.", size=2.1, fill="#4d4842"); y += 6
    svg.text((lx, y), "CZAS NASŁONECZNIENIA OKIEN CHRONIONYCH (7:00–17:00, krok 5 min)", size=2.4, weight=600); y += 4.2
    hdr = ["okno", "20.03 suma / ciągły", "23.09 suma / ciągły", "bez projektu (20.03)"]
    xs = [lx, lx + 60, lx + 88, lx + 116]
    for xx, h in zip(xs, hdr):
        svg.text((xx, y), h, size=1.8, weight=600, fill="#3a3632")
    y += 1.2
    svg.line((lx, y), (lx + LEG - 8, y), stroke="#1f1d1a", sw=0.15); y += 3.2
    for r in rows:
        a, b = (r[d.isoformat()] for d in days)
        ok = min(a["suma_min"], b["suma_min"]) >= 90
        svg.text((xs[0], y), r["okno"], size=1.75)
        svg.text((xs[1], y), f"{a['suma_min'] / 60:.1f} h / {a['najdluzszy_ciagly_min'] / 60:.1f} h", size=1.75, fill="#1f6b3d" if ok else "#c0392b")
        svg.text((xs[2], y), f"{b['suma_min'] / 60:.1f} h / {b['najdluzszy_ciagly_min'] / 60:.1f} h", size=1.75, fill="#1f6b3d" if ok else "#c0392b")
        svg.text((xs[3], y), f"{a['bez_projektu_suma_min'] / 60:.1f} h", size=1.75, fill="#6f6a63")
        y += 2.9
    y += 2
    for t in ["Wymóg (zabudowa śródmiejska): ≥ 1,5 h w dniach równonocy, 7:00–17:00, dla co najmniej",
              "jednego pokoju mieszkania; liczony czas, gdy Słońce jest nad horyzontem i przed licem okna.",
              "Zielony = spełnione dla obu dat. Okno w szczycie WS 5 (pn.) jest poza zasięgiem Słońca",
              "w dniach równonocy niezależnie od projektu — pokoje mieszkania 6/6A od wsch. w tabeli.",
              "Podstawa prawna: § 60 i § 13 rozporządzenia w sprawie warunków technicznych (przepisy",
              "przejściowe – art. 102a Prawa budowlanego); weryfikacja w części opisowej."]:
        svg.text((lx, y), t, size=1.8, fill="#3a3632"); y += 2.9
    y += 3
    svg.text((lx, y), "Liczba godzin w cieniu projektowanej zabudowy (20.03, 7:00–17:00):", size=2.0, weight=600); y += 3.6
    for th, col, lab in self_legend:
        svg.poly([(lx, y - 2.2), (lx + 7, y - 2.2), (lx + 7, y + 0.6), (lx, y + 0.6)], fill="rgb(%d,%d,%d)" % col, stroke="#8d877f", sw=0.12)
        svg.text((lx + 9, y), lab, size=1.9); lx += 26
    return svg


def main():
    rows, days = analyse()
    (ROOT / "docs" / "70_rysunki" / "naslonecznienie.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    svg = draw(rows, days)
    (ROOT / "build" / "rysunki" / "naslonecznienie.svg").write_text(svg.render(), encoding="utf-8")
    html = ROOT / "docs" / "70_rysunki" / "podglady" / "naslonecznienie.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm + 10:.0f}mm {svg.h_mm + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
    worst = min(min(r[d.isoformat()]["suma_min"] for d in days) for r in rows)
    print(f"{svg.w_mm + 10:.0f} {svg.h_mm + 10:.0f} worst={worst}")
    for r in rows:
        print(r["okno"], [r[d.isoformat()]["suma_min"] for d in days], [r[d.isoformat()]["najdluzszy_ciagly_min"] for d in days])


if __name__ == "__main__":
    main()
