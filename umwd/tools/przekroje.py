#!/usr/bin/env python3
"""Przekroje 1:200 (Etap II, R.VII ust.2 pkt2 lit.b) — z modelu pomieszczeń (model/budynek.json, czytany na bieżąco),
koncepcji (koncepcja.json: kondygnacje, posadowienie, sala Sejmiku) i sąsiadów.

A-A: wzdłuż osi u = 30 m wieży (pd.→pn.): kamienica Wybrzeże J. Słowackiego 5 – dz. 10/2 – segment – wieża (sala obrad,
     amfiteatr, kratownica dachu, galeria) – łuk Bramy Mostowej – Plac Mostowy. Widok na zachód (w tle ogród i skrzydło).
B-B: wzdłuż v = 19 m (zach.→wsch.): ul. Mazowiecka – skrzydło – wieża (Hala Obywatelska, trzon A, sala obrad) – Wybrzeże – mur
     bulwaru. Widok na północ.
Wynik: build/rysunki/przekroj_{AA,BB}_1-200.svg + docs/70_rysunki/podglady/przekroje_1-200.png
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from shapely.geometry import Polygon, MultiPolygon, LineString, Point
from shapely.ops import unary_union
from umwd.svg import Svg
from umwd.facade_elev import draw_faces, frame, INK
from umwd.siteplan import load_site, poly_of
import elewacje as EL

K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
BM = json.loads((ROOT / "model" / "budynek.json").read_text(encoding="utf-8"))
S = load_site()
Z0 = 119.30
import os
SCALE = int(os.environ.get('UMWD_SCALE', '200'))
k = 1000.0 / SCALE
ACC = "#a8483a"
POCHE = "#1f1d1a"
B = {b["id"]: b for b in K["bryly"]}
TOWER = Polygon(B["W"]["obrys_ccw"]).buffer(0)
WING = Polygon(B["M"]["obrys_ccw"]).buffer(0)
SEG = Polygon(B["S"]["obrys_ccw"]).buffer(0)


def uv(u, v):
    return (74.606 + 0.97155 * u - 0.23684 * v, 40.756 + 0.23684 * u + 0.97155 * v)


def mp(coords):
    """budynek.json multipolygon [[ring, hole...], ...] → shapely."""
    if not coords:
        return Polygon()
    out = []
    for poly in coords:
        if not poly:
            continue
        try:
            out.append(Polygon(poly[0], poly[1:]).buffer(0))
        except Exception:
            pass
    return unary_union(out) if out else Polygon()


def intervals(geom, line, U):
    x = geom.intersection(line)
    segs = []
    for g in ([x] if x.geom_type in ("LineString",) else list(getattr(x, "geoms", []))):
        if g.geom_type == "LineString" and g.length > 0.02:
            us = [U(*c) for c in g.coords]
            segs.append((min(us), max(us)))
    return sorted(segs)


def slab_t(e, n):
    p = Point(e, n)
    if TOWER.buffer(0.3).contains(p):
        return 0.43
    return 0.55


def person(svg, P, u, z, h=1.75, flip=False):
    x, y = P(u, z)
    s = h * k / 1.75
    svg.circle((x, y - 1.62 * s), 0.12 * s * 1.3, fill=INK, stroke="none")
    svg.poly([(x - 0.2 * s, y - 1.45 * s), (x + 0.2 * s, y - 1.45 * s), (x + 0.16 * s, y - 0.8 * s), (x + 0.1 * s, y), (x - 0.1 * s, y), (x - 0.16 * s, y - 0.8 * s)],
             fill=INK, stroke="none", extra='fill-opacity="0.75"')


def tree(svg, P, u, zg, h=11.0, r=3.2, op=0.22):
    x, y = P(u, zg)
    svg.line((x, y), (x, y - (h - r * 1.2) * k), stroke="#6b6157", sw=0.18)
    svg.circle((x, y - (h - r) * k), r * k, fill="#9db28a", stroke="#7d8f6a", sw=0.12, extra=f'fill-opacity="{op}"')


def section(name, title, sub, p0, p1, ground_pts, neighbours=(), beyond_names=(), notes=(), u_rng=None, z_lo=-24.0, z_hi=40.0, places=(), mode="full", pad=(40, 70, 24, 16)):
    ex, ey = p1[0] - p0[0], p1[1] - p0[1]
    Ln = math.hypot(ex, ey)
    r = (ex / Ln, ey / Ln)
    d = (-r[1], r[0])
    view_az = math.degrees(math.atan2(d[0], d[1])) % 360
    U = lambda e, n: (e - p0[0]) * r[0] + (n - p0[1]) * r[1]
    cut = p0[0] * d[0] + p0[1] * d[1]
    line = LineString([p0, p1])
    u0, u1 = (u_rng if u_rng else (0.0, Ln))
    pad_l, pad_r, pad_t, pad_b = pad
    W = pad_l + (u1 - u0) * k + pad_r
    H = pad_t + (z_hi - z_lo) * k + pad_b
    svg = Svg(W, H)
    oy = pad_t + z_hi * k

    def P(u, z):
        return (pad_l + (u - u0) * k, oy - z * k)

    # ---- soil below terrain (drawn first, everything else on top)
    gp = sorted((U(e, n), z - Z0) for e, n, z in ground_pts)
    gp = [(u0, gp[0][1])] + gp + [(u1, gp[-1][1])]
    soil = [P(u, z) for u, z in gp] + [P(u1, z_lo), P(u0, z_lo)]
    svg.poly(soil, fill="#f4f1ec", stroke="none")
    hp = svg.hatch("soil", spacing=2.2, angle=45, stroke="#ddd6cb", sw=0.06)
    svg.poly(soil, fill=hp, stroke="none")
    # geology: top of glacial till QpB ≈ 102,6 m n.p.m. (101,8–103,4)
    svg.line(P(u0, 102.6 - Z0), P(u1, 102.6 - Z0), stroke="#b9ab97", sw=0.15, dash="0.6,0.8")
    svg.text((P(u1, 102.6 - Z0)[0] + 2, P(u1, 102.6 - Z0)[1] + 0.7), "strop glin zwałowych QpB ≈ 102,6", size=1.7, fill="#7d7266")

    # ---- elevation beyond the plane (our façades + neighbours)
    faces = EL.tower_faces() + [EL.wing_west()] + EL.wing_east() + EL.segment_faces() + EL.neighbour_faces(set(beyond_names))
    for f in faces:   # mute the beyond-view: everything is drawn, then washed with a white veil
        pass
    draw_faces(svg, faces, view_az, P, cut=cut + 0.3)
    svg.poly([P(u0, z_hi), P(u1, z_hi), P(u1, -0.5), P(u0, -0.5)], fill="#ffffff", stroke="none", extra='fill-opacity="%s"' % ("0.45" if mode == "full" else "0.75"))
    # trees beyond (garden), light
    for t in S["zielen"]["drzewa"]:
        if t["nr"] in set(K["zagospodarowanie"]["drzewa_usuniete"]):
            continue
        dep = t["e"] * d[0] + t["n"] * d[1] - cut
        if 0.5 < dep < 45:
            u = U(t["e"], t["n"])
            if u0 + 2 < u < u1 - 2 and not TOWER.contains(Point(t["e"], t["n"])):
                zg = min(gp, key=lambda q: abs(q[0] - u))[1]
                tree(svg, P, u, zg, h=9.0 + (hash(t["nr"]) % 5), r=2.6 + (hash(t["nr"]) % 3) * 0.4, op=0.18)

    # ---- the building cut
    levels = BM["kondygnacje"]
    ids = [lv["id"] for lv in levels]
    z_of = {lv["id"]: (float(lv["rzedna"]) if lv.get("rzedna") not in (None, "None") else None) for lv in levels}
    nxt = {"-2": -3.75, "-1": 0.0, "P": 4.8, "1": 8.55, "2": 12.3, "3": 16.05, "4": 19.8, "5": 23.55, "6": 27.3, "S": 36.2, "ANT": 36.2}
    room_labels = []
    for lv in levels:
        lid = lv["id"]
        if lid == "D":
            continue
        z = z_of[lid]
        plate = mp(lv.get("plyta"))
        if lid == "ANT":
            plate = plate.difference(mp((lv.get("extra") or {}).get("void", [])))
        top0 = {"-2": -3.75, "-1": 0.0, "P": 4.8, "1": 8.55, "2": 12.3, "3": 16.05, "4": 19.8, "5": 23.55, "6": 27.3, "S": 36.2, "ANT": 36.2}.get(lid, z + 3.75)
        if lid != "ANT":
            for a, b in intervals(plate, line, U):
                svg.poly([P(a, z), P(b, z), P(b, top0), P(a, top0)], fill="#ffffff", stroke="none")
        for a, b in intervals(plate, line, U):
            mid = (a + b) / 2
            e, n = p0[0] + r[0] * mid, p0[1] + r[1] * mid
            t = slab_t(e, n)
            if lid in ("-2",):
                svg.poly([P(a, z - 1.2), P(b, z - 1.2), P(b, z), P(a, z)], fill=POCHE, stroke="none")      # płyta fund. 1,10 + posadzka
            elif lid == "-1" and not TOWER.contains(Point(e, n)) and not SEG.contains(Point(e, n)):
                svg.poly([P(a, z - 1.0), P(b, z - 1.0), P(b, z), P(a, z)], fill=POCHE, stroke="none")
            else:
                svg.poly([P(a, z - t), P(b, z - t), P(b, z), P(a, z)], fill=POCHE, stroke="none")
        top = nxt.get(lid, z + 3.75)
        sc = lv.get("sciany", {})
        wall_top = top
        # walls: external (poché with windows), cores (poché), internal partitions (grey)
        ext = mp(sc.get("zewnetrzne", []))
        cores = mp(sc.get("trzony", []))
        inner = mp(sc.get("wewnetrzne", []))
        if lid == "ANT":
            ext = Polygon(); inner = Polygon(); cores = Polygon()
        okna = [(LineString(o["pts"]) if "pts" in o else LineString([o["a"], o["b"]]), o.get("kind", "okno")) for o in lv.get("okna", [])]
        for a, b in intervals(ext, line, U):
            if b - a > 1.4:
                continue
            mid = (a + b) / 2
            e, n = p0[0] + r[0] * mid, p0[1] + r[1] * mid
            pt = Point(e, n)
            t = slab_t(e, n)
            ztop = wall_top - (t if lid not in ("S",) else 0.3)
            hits = [kd for o, kd in okna if o.distance(pt) < max(0.35, (b - a))]
            is_win = bool(hits)
            ribbon = "wstega" in hits
            if lid in ("-1", "-2"):
                svg.poly([P(a, z - 1.1), P(b, z - 1.1), P(b, ztop), P(a, ztop)], fill=POCHE, stroke="none")
                continue
            if is_win:
                if ribbon:
                    sill, head = ((0.3, 8.55) if lid == "S" else (1.30, ztop - z - 0.02))
                else:
                    sill = 0.0 if lid == "P" else (0.7 if lid == "S" else 0.9)
                    head = (4.4 if lid == "P" else (5.7 if lid == "S" else sill + 2.45))
                svg.poly([P(a, z), P(b, z), P(b, z + sill), P(a, z + sill)], fill=POCHE, stroke="none")
                svg.poly([P(a, z + head), P(b, z + head), P(b, ztop), P(a, ztop)], fill=POCHE, stroke="none")
                gx = P((a + b) / 2, 0)[0]
                svg.line((gx - 0.25, P(0, z + sill)[1]), (gx - 0.25, P(0, z + head)[1]), stroke="#4a6a85", sw=0.18)
                svg.line((gx + 0.25, P(0, z + sill)[1]), (gx + 0.25, P(0, z + head)[1]), stroke="#4a6a85", sw=0.18)
            else:
                svg.poly([P(a, z), P(b, z), P(b, ztop), P(a, ztop)], fill=POCHE, stroke="none")
        for a, b in intervals(cores, line, U):
            if b - a > 0.9:
                continue
            svg.poly([P(a, z), P(b, z), P(b, wall_top - 0.43), P(a, wall_top - 0.43)], fill=POCHE, stroke="none")
        for a, b in intervals(inner, line, U):
            if b - a > 0.6:
                continue
            svg.poly([P(a, z), P(b, z), P(b, wall_top - 0.43), P(a, wall_top - 0.43)], fill="#5b5651", stroke="none")
        # rooms → labels
        for rm in lv.get("pomieszczenia", []):
            g = mp(rm.get("poligon"))
            for a, b in intervals(g, line, U):
                if b - a > 3.2 and rm.get("kind") not in ("core_lift",):
                    room_labels.append(((a + b) / 2, z + min(1.6, (top - z) / 2), rm["nazwa"], b - a, rm.get("numer", "")))

    # ---- Sejmik hall: tiers, gallery balustrade, roof truss
    fu, fv = K["kondygnacja_sejmiku"]["sala"]["ognisko_rzedow_uv"]
    fe, fn = uv(fu, fv)
    hall = None
    for lv in levels:
        if lv["id"] == "S":
            for rm in lv["pomieszczenia"]:
                if rm["numer"].startswith("SWD.01"):
                    hall = mp(rm["poligon"])
    if hall is not None:
        for a, b in intervals(hall, line, U):
            uu = a
            while uu < b:
                e, n = p0[0] + r[0] * uu, p0[1] + r[1] * uu
                rr = math.hypot(e - fe, n - fn)
                lift = 0.45 if rr >= 9.0 else 0.30 if rr >= 6.9 else 0.15 if rr >= 4.8 else 0.0
                if lift:
                    svg.poly([P(uu, 27.3), P(min(b, uu + 0.25), 27.3), P(min(b, uu + 0.25), 27.3 + lift), P(uu, 27.3 + lift)], fill=POCHE, stroke="none")
                uu += 0.25
            # people seated + presidium figure
            for q in range(1, int((b - a) / 2.2)):
                person(svg, P, a + q * 2.2, 27.75, h=1.25)
            # roof truss 1,60 m over the hall
            zt, zb = 36.0, 34.4
            svg.line(P(a, zt), P(b, zt), stroke=POCHE, sw=0.35)
            svg.line(P(a, zb), P(b, zb), stroke=POCHE, sw=0.35)
            nseg = max(2, int((b - a) / 2.7))
            for q in range(nseg):
                x0 = a + (b - a) * q / nseg; x1 = a + (b - a) * (q + 1) / nseg
                svg.line(P(x0, zb), P((x0 + x1) / 2, zt), stroke=POCHE, sw=0.18)
                svg.line(P((x0 + x1) / 2, zt), P(x1, zb), stroke=POCHE, sw=0.18)
    # roof slabs + attics
    roofs = [(TOWER, 36.2, 36.45, 37.2), (WING, 19.8, 20.4, 20.85), (SEG, 19.5, 19.8, 20.85)]
    for g, zs, zr, za in roofs:
        for a, b in intervals(g, line, U):
            svg.poly([P(a, zs - 0.3), P(b, zs - 0.3), P(b, zr), P(a, zr)], fill=POCHE, stroke="none")
            for x in (a, b - 0.5):
                svg.poly([P(x, zr), P(x + 0.5, zr), P(x + 0.5, za), P(x, za)], fill=POCHE, stroke="none")
            if g is SEG:   # set-back glass balustrade 1,10 m (D.03)
                for x in (a + 1.5, b - 1.5):
                    svg.line(P(x, zr), P(x, zr + 1.1), stroke="#4a6a85", sw=0.25)
    # diaphragm walls 0,80 to ≈ −18 m and tower piles
    ug = unary_union([mp(lv.get("plyta")) for lv in levels if lv["id"] in ("-1", "-2")])
    for a, b in intervals(ug, line, U):
        for x in (a, b - 0.8):
            svg.poly([P(x, -1.0), P(x + 0.8, -1.0), P(x + 0.8, -18.0), P(x, -18.0)], fill="#3a3632", stroke="none")
    for a, b in intervals(TOWER, line, U):
        x = a + 2.0
        while x < b - 1.5:
            svg.poly([P(x, -8.2), P(x + 0.8, -8.2), P(x + 0.8, -22.2), P(x, -22.2)], fill="#ffffff", stroke="#3a3632", sw=0.15, extra='stroke-dasharray="0.8,0.5"')
            x += 4.05
    # groundwater
    for zabs, lab, col in ((117.0, "poziom obliczeniowy wód 117,00", "#3f74a0"), (116.45, "ZWG maks. 116,45", "#5b8db5"), (115.5, "ZWG średnie 115,50", "#8fb3cf")):
        y = P(0, zabs - Z0)[1]
        svg.line((P(u0, 0)[0], y), (P(u1, 0)[0], y), stroke=col, sw=0.22, dash="2.4,1.0")
        svg.text((P(u1, 0)[0] + 2, y + 0.7), lab, size=1.7, fill=col)
    # neighbour cuts (light poché + floors)
    for nb in neighbours:
        g = Polygon(nb["pts"]).buffer(0)
        for a, b in intervals(g, line, U):
            zg, zt = nb["zg"], nb["zt"]
            svg.poly([P(a, zg), P(b, zg), P(b, zt), P(a, zt)], fill="#e9e6e1", stroke="#8d877f", sw=0.3)
            for zf in nb["floors"]:
                svg.poly([P(a, zf - 0.35), P(b, zf - 0.35), P(b, zf), P(a, zf)], fill="#b7b1a8", stroke="none")
            svg.text(((P(a, 0)[0] + P(b, 0)[0]) / 2, P(0, zt + 1.2)[1]), nb["label"], size=2.0, anchor="middle", fill="#6f6a63")
            for (zw0, zw1, side, lab) in nb.get("windows", []):
                x = a if side == "a" else b
                svg.poly([P(x - 0.3, zw0), P(x + 0.3, zw0), P(x + 0.3, zw1), P(x - 0.3, zw1)], fill="#ffffff", stroke=ACC, sw=0.25)
                svg.text((P(x, 0)[0] + (2 if side == "b" else -2), P(0, zw1 + 0.6)[1]), lab, size=1.7, fill=ACC, anchor="start" if side == "b" else "end")
    # ground line
    svg.poly([P(u, z) for u, z in gp], fill="none", stroke=INK, sw=0.5, close=False)
    # people on the ground for scale
    for (u, z) in [(gp[1][0] + 4, gp[1][1])]:
        person(svg, P, u, z)
    # room labels
    for (u, z, txt, w, num) in (room_labels if mode == "full" else []):
        short = txt.split("(")[0].strip()
        if len(short) > 26:
            short = short[:24].rstrip() + "…"
        svg.text(P(u, z), short, size=1.55, anchor="middle", fill="#3a3632")
    svg.poly([(0, 0), (pad_l - 1, 0), (pad_l - 1, H), (0, H)], fill="#ffffff", stroke="none")
    svg.poly([(W - pad_r + 1, 0), (W, 0), (W, H), (W - pad_r + 1, H)], fill="#ffffff", stroke="none")
    for (pu, pz, lab) in places:
        svg.text(P(pu, pz), lab, size=2.0, anchor="middle", fill="#4d4842", weight=600)
    # level marks (left)
    x = pad_l - 8
    for z, lab in [(37.2, "+37,20"), (36.2, "+36,20"), (30.9, "+30,90 galeria"), (27.3, "+27,30 S"), (23.55, "+23,55 (6)"), (19.8, "+19,80 (5)"),
                   (16.05, "+16,05 (4)"), (12.3, "+12,30 (3)"), (8.55, "+8,55 (2)"), (4.8, "+4,80 (1)"), (0.0, "±0,00 = 119,30 (P)"), (-3.75, "−3,75 (−1)"), (-7.0, "−7,00 (−2)")]:
        y = P(0, z)[1]
        svg.poly([(x, y), (x - 1.2, y - 1.4), (x + 1.2, y - 1.4)], fill=INK, stroke="none")
        svg.line((x - 2, y), (pad_l - 2, y), stroke=INK, sw=0.1)
        svg.text((x - 2.4, y - 0.4), lab, size=1.75, anchor="end")
    # notes (right column)
    yy = pad_t + 6
    for t in notes:
        svg.text((W - pad_r + 6, yy), t, size=1.9, fill="#3a3632"); yy += 3.3
    svg.text((pad_l, 9), title, size=4.2, weight=600)
    svg.text((pad_l, 14.5), sub, size=2.3, fill="#4d4842")
    sx, sy = pad_l, H - 8
    for i in range(5):
        svg.poly([(sx + i * 2 * k, sy), (sx + (i + 1) * 2 * k, sy), (sx + (i + 1) * 2 * k, sy + 1.2), (sx + i * 2 * k, sy + 1.2)], fill=INK if i % 2 == 0 else "#fff", stroke=INK, sw=0.12)
    svg.text((sx + 10 * k + 6, sy + 1.2), f"0–10 m · 1:{SCALE}", size=2.0, weight=600)
    svg.P, svg.U, svg.uv_range = P, U, (u0, u1)
    if mode == "full":
        out = ROOT / "build" / "rysunki" / f"przekroj_{name}_1-{SCALE}.svg"
        out.write_text(svg.render(), encoding="utf-8")
    return svg


def ws5():
    b = [x for x in S["budynki"]["items"] if x.get("nazwa") == "Wybrzeze J. Slowackiego 5"][0]
    pg = poly_of(b)
    lv = SAS_WS5["poziomy_szac_m_npm"]
    return {"pts": list(pg.exterior.coords), "zg": b["teren_wokol_H"]["min"] - Z0, "zt": b["gora_szac_H"] - Z0,
            "floors": [lv[k] - Z0 for k in ("parter", "I_p", "II_p", "III_p", "poddasze")], "label": "Wybrzeże J. Słowackiego 5",
            "windows": [(lv["I_p"] - Z0 + 0.9, lv["I_p"] - Z0 + 2.9, "b", "okno w szczycie (zachowane, § 13 WT)")]}


def maz19():
    m = SAS["budynki"][0]
    base = m["poziom_0_00_m_npm"]["wartosc"]
    rz = {"parter": 0.0, "I_p": 3.69, "II_p": 7.46, "III_p": 11.27, "IV_p": 14.97, "poddasze": 18.3}
    return {"pts": m["obrys_egib_en"], "zg": base - 0.73 - Z0, "zt": m.get("attyka_szac_H", 140.24) - Z0 if False else 140.24 - Z0,
            "floors": [base + v - Z0 for v in rz.values()], "label": "Mazowiecka 19"}


SAS = json.loads((ROOT / "model" / "sasiedzi.json").read_text(encoding="utf-8"))
SAS_WS5 = SAS["budynki"][1]


def main():
    res = []
    UA = 29.4
    pA0, pA1 = uv(UA, -40.0), uv(UA, 46.0)
    res.append(section("AA", "PRZEKRÓJ A-A", "oś u = 29,4 m wieży: Wybrzeże J. Słowackiego 5 – segment – sala obrad Sejmiku – Brama Mostowa – Plac Mostowy · widok na zachód",
                       pA0, pA1,
                       [(pA0[0], pA0[1], 118.95), (*uv(UA, -21), 118.95), (*uv(UA, -10.6), 119.0), (*uv(UA, 31), 119.40), (*uv(UA, 40), 119.40), (pA1[0], pA1[1], 119.45)],
                       places=[(24.5, -1.4, "dz. 10/2"), (80.0, -1.4, "PLAC MOSTOWY"), (67.6, 2.2, "podcień")],
                       neighbours=[ws5()], beyond_names=("Mazowiecka 19",),
                       notes=["Wieża P+6+S: attyka +37,20 = 156,50 m n.p.m.;",
                              "najniższy punkt pokrycia +36,20 (MPZP strefa A: 35–45 m).",
                              "Sala obrad 6,85 m w świetle, amfiteatr 3 rzędy +0,15/0,30/0,45,",
                              "galeria publiczności +30,90, kratownice stalowe 1,60 m / 19,5 m.",
                              "Segment P+4 z tarasem zielonym +19,80, balustrada szklana",
                              "1,10 m cofnięta 1,5 m od attyki (WT § 298).",
                              "Odległość segment – szczyt WS 5: 10,58 m; okno w szczycie",
                              "zachowane (§ 13 WT – analiza nasłonecznienia na planszy 2).",
                              "Podziemie: −1 / −2 w ścianach szczelinowych 0,80 m (≈ 18 m,",
                              "wcięte w gliny QpB), biała wanna, płyta 1,10 m na palach CFA",
                              "Ø 0,8 m L ≈ 14 m; poziom obliczeniowy wód 117,00 m n.p.m."]))
    VB = 19.6
    pB0, pB1 = uv(-24.0, VB), uv(52.0, VB)
    res.append(section("BB", "PRZEKRÓJ B-B", "v = 19,6 m: ul. Mazowiecka – skrzydło – Hala Obywatelska i sala obrad – ul. Wybrzeże J. Słowackiego · widok na północ",
                       pB0, pB1,
                       [(pB0[0], pB0[1], 119.30), (*uv(-14.5, VB), 119.35), (*uv(0, VB), 119.38), (*uv(40, VB), 119.30), (*uv(46, VB), 119.25), (pB1[0], pB1[1], 119.20)],
                       places=[(5.0, -1.4, "ul. Mazowiecka"), (69.0, -1.4, "ul. Wybrzeże J. Słowackiego")],
                       neighbours=[], beyond_names=(),
                       notes=["Skrzydło P+4: gzyms +20,85 = 140,15 m n.p.m. w linii attyki",
                              "kamienicy Mazowiecka 19 (140,24); biura 3,20 m w świetle.",
                              "Wieża: biura 3,32 m w świetle (TABS, płyta 0,28 m),",
                              "parter 4,37 m; kondygnacja cienia (6) cofnięta 0,40 m.",
                              "Hala Obywatelska na osi most – ogród (przejście publiczne)."]))
    total_h = sum(s.h_mm for s in res) + 12
    max_w = max(s.w_mm for s in res)
    body = "".join(f'<div style="margin:0 0 4mm 0">{s.render()}</div>' for s in res)
    html = ROOT / "docs" / "70_rysunki" / "podglady" / f"przekroje_1-{SCALE}.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{max_w+10:.0f}mm {total_h+10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{body}</body></html>', encoding="utf-8")
    print(f"{max_w + 10:.0f} {total_h + 10:.0f}")


if __name__ == "__main__":
    main()
