#!/usr/bin/env python3
"""Przekroje 1:200 (Etap II, R.VII ust.2 pkt2 lit.b) — z modelu pomieszczeń (model/budynek.json, czytany na bieżąco),
koncepcji (koncepcja.json: kondygnacje, posadowienie, sala Sejmiku) i sąsiadów.

A-A: wzdłuż osi u = 30 m wieży (pd.→pn.): kamienica Wybrzeże J. Słowackiego 5 – dz. 10/2 – segment – wieża (sala obrad,
     amfiteatr, kratownica dachu, galeria) – łuk Bramy Mostowej – Plac Mostowy. Widok na zachód (w tle ogród i skrzydło).
B-B: wzdłuż v = 19 m (zach.→wsch.): ul. Mazowiecka – skrzydło – wieża (Hala Obywatelska, trzon A, sala obrad) – Wybrzeże – mur
     bulwaru. Widok na północ.
Wynik: build/rysunki/przekroj_{AA,BB}_1-200.svg + docs/70_rysunki/podglady/przekroje_1-200.png
"""
import sys, json, math, re
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
SEG_S_FACE = LineString(B["S"]["obrys_ccw"][:2])           # lico pd. segmentu (od dz. 10/2)

# ---- rzędne i przegrody z koncepcja.json (v1.1) – bez wartości zakodowanych na sztywno
KOND = {kd["kondygnacja"]: kd for kd in K["kondygnacje"]}
K_IDS = [kd["kondygnacja"] for kd in K["kondygnacje"]]    # od dołu: −2, −1, P, 1 … 6, S
Z_K = {kid: float(kd["posadzka_wzgl"]) for kid, kd in KOND.items()}
Z_K["ANT"] = float(KOND["S"]["antresola_posadzka"])
DW_, DM_, DS_ = B["W"]["dach"], B["M"]["dach"], B["S"]["dach"]
Z_ROOF_W = float(DW_["najnizszy_pkt_pokrycia"]["wzgl"])                # +36,20
Z_ROOF_W_MAX = float(DW_["najwyzszy_pkt_pokrycia"]["wzgl"])            # +36,45
Z_ATT_W = float(DW_["attyka"]["wzgl"])                                 # +37,20
Z_SUF_S = float(KOND["S"]["dach"]["rusz_spod"])                        # +34,15 – spód rusztu / sufit sali
H_TRUSS = 1.60                                                         # kratownice 1,60 m (siatka.wieza.dach_S)
Z_DECK_W = Z_SUF_S + 0.05 + H_TRUSS                                    # +35,80 – płyta zespolona dachu
STR4 = KOND["4"]["strop_nad"]
Z_ROOF_M, Z_ROOF_M_SP = float(DM_["strop_wierzch"]), float(STR4["dach_skrzydla_spod"])          # +19,80 / +19,40
Z_ROOF_M_MAX, Z_GZ = float(DM_["najwyzszy_pkt_pokrycia"]["wzgl"]), float(DM_["gzyms_attyka"]["wzgl"])   # +20,40 / +20,85
Z_ROOF_S, Z_ROOF_S_SP = float(DS_["strop_wierzch"]), float(STR4["dach_segmentu_spod"])          # +19,10 / +18,82
Z_TARAS = float(DS_["taras_wykonczenie"]["wzgl"])                                               # +19,80 (139,10)
Z_ATT_S = float(DS_["attyka"]["wzgl"])                                                          # +20,85 (lica wsch., zach.)
Z_ATT_SPD = float(DS_["attyka"]["sciana_pd_npm"]) - Z0                                          # 139,10 – attyka ściany pd.
BAL_H, BAL_COF = 1.10, 1.5                                 # balustrada szklana 1,10 m cofnięta 1,5 m od lica pd. (140,20)
PD = KOND["-2"]["plyta_denna"]                             # płyta denna: wierzch −7,30, spód −8,40 (wieża 1,10 / poza 0,90)
POS = K["siatka"]["posadowienie"]


def _num(txt, pat, dflt):
    m = re.search(pat, txt or "")
    return float(m.group(1).replace(",", ".")) if m else dflt


T_DW = _num(POS.get("obudowa"), r"ściany szczelinowe\s+(\d+[,.]\d+)\s*m", 0.60)    # grubość ścian szczelinowych
H_DW = _num(POS.get("obudowa"), r"×\s*(\d+(?:[,.]\d+)?)\s*m\b", 19.0)             # wysokość (głębokość) ścian
L_PAL = _num(POS.get("wieza"), r"L\s*≈\s*(\d+(?:[,.]\d+)?)\s*m", 14.0)           # pale CFA pod wieżą
D_PAL = _num(POS.get("wieza"), r"Ø\s*(\d+[,.]\d+)\s*m", 0.8)
Z_DW_TOP = float(KOND["-1"]["strop_nad"]["spod_wieza"])    # oczep ścian szczelinowych pod stropem nad −1
UG_K = unary_union([Polygon(K["podziemie"][i]["obrys_ccw"]).buffer(0) for i in ("-1", "-2") if i in K["podziemie"]])
EWI, ESK = K["elewacje"]["wieza"], K["elewacje"]["skrzydlo"]
Z_KORDON = float(ESK["linie"]["attyka_npm"]) - Z0          # kordon wieży do +20,85 (parapet kond. 5)
# nazwy kondygnacji „następnej” – wierzch ścian / tło białe kondygnacji
NXT = {K_IDS[i]: Z_K[K_IDS[i + 1]] for i in range(len(K_IDS) - 1)}
NXT["S"] = Z_ROOF_W
NXT["ANT"] = Z_ROOF_W


def fz(z):
    if abs(z) < 0.005:
        return "±0,00"
    return ("+" if z > 0 else "−") + f"{abs(z):.2f}".replace(".", ",")


def slab_under(lid, e, n):
    """Strop (konstrukcja + warstwy) pod posadzką kondygnacji lid: posadzka − spód stropu nad kondygnacją niższą
    (wieża / segment – płyta 0,28 + podłoga; skrzydło – płyta 0,40 + podłoga; garaż – bez warstw; nad kond. 4 skrzydła
    i segmentu – dach / taras: spód +19,40 / +18,82)."""
    if lid not in K_IDS or K_IDS.index(lid) == 0:
        return 0.43
    sn = KOND[K_IDS[K_IDS.index(lid) - 1]]["strop_nad"]
    tw = sn.get("spod_wieza", sn.get("wieza_spod"))
    pt = Point(e, n)
    in_tw = TOWER.buffer(0.3).contains(pt)
    if not in_tw and WING.contains(pt):
        sp = sn.get("spod_skrzydlo", sn.get("dach_skrzydla_spod", tw))
    elif not in_tw and SEG.contains(pt):
        sp = sn.get("dach_segmentu_spod", tw)
    else:
        sp = tw
    return Z_K[lid] - float(sp)


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


def slab_t(e, n, lid="1"):
    """Zachowane API: grubość stropu pod posadzką kondygnacji (domyślnie typowej) w punkcie (e, n)."""
    return slab_under(lid, e, n)


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


def section(name, title, sub, p0, p1, ground_pts, neighbours=(), beyond_names=(), notes=(), u_rng=None, z_lo=-13.0, z_hi=40.0, places=(), mode="full", pad=(40, 70, 24, 16)):
    """z_lo default −13: diaphragm walls and piles are cut by the frame (break line)."""
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
    z_bm = {lv["id"]: (float(lv["rzedna"]) if lv.get("rzedna") not in (None, "None") else None) for lv in levels}
    # rzędne z koncepcja.json (v1.1); budynek.json dostarcza tylko geometrię rzutów
    z_of = {lid: Z_K.get(lid, z_bm[lid]) for lid in ids}
    for lid in ids:
        if lid in Z_K and z_bm[lid] is not None and abs(z_bm[lid] - Z_K[lid]) > 0.01 and not _WARNED:
            print(f"  [przekroje] uwaga: budynek.json kond. {lid} rzędna {z_bm[lid]:+.2f} ≠ koncepcja.json {Z_K[lid]:+.2f} "
                  f"– rysuję wg koncepcja.json (model pomieszczeń do przeliczenia)", file=sys.stderr)
    _WARNED.add(name)
    ug_bm2 = mp(next((lv.get("plyta") for lv in levels if lv["id"] == "-2"), None))
    room_labels = []
    for lv in levels:
        lid = lv["id"]
        if lid == "D":
            continue
        z = z_of[lid]
        plate = mp(lv.get("plyta"))
        if lid == "ANT":
            plate = plate.difference(mp((lv.get("extra") or {}).get("void", [])))
        top0 = NXT.get(lid, z + 3.75)
        if lid != "ANT":
            for a, b in intervals(plate, line, U):
                svg.poly([P(a, z), P(b, z), P(b, top0), P(a, top0)], fill="#ffffff", stroke="none")
        for a, b in intervals(plate, line, U):
            mid = (a + b) / 2
            e, n = p0[0] + r[0] * mid, p0[1] + r[1] * mid
            t = slab_under(lid, e, n)
            if lid in ("-2",):          # płyta denna: wieża 1,10 (spód −8,40), poza wieżą 0,90; + posadzka
                spod = float(PD["spod"]) if TOWER.contains(Point(e, n)) else float(PD["wierzch"]) - float(PD["grubosc_poza_wieza_m"])
                svg.poly([P(a, spod), P(b, spod), P(b, z), P(a, z)], fill=POCHE, stroke="none")
            elif lid == "-1" and not ug_bm2.buffer(0.05).contains(Point(e, n)):     # −1 bez −2 pod spodem (M1) – płyta denna
                t_pd = (Z_K["-2"] - float(PD["wierzch"])) + float(PD["grubosc_poza_wieza_m"])
                svg.poly([P(a, z - t_pd), P(b, z - t_pd), P(b, z), P(a, z)], fill=POCHE, stroke="none")
            else:
                svg.poly([P(a, z - t), P(b, z - t), P(b, z), P(a, z)], fill=POCHE, stroke="none")
        top = NXT.get(lid, z + 3.75)
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
            nx_id = K_IDS[K_IDS.index(lid) + 1] if lid in K_IDS[:-1] else None
            t = slab_under(nx_id, e, n) if nx_id else 0.3
            ztop = wall_top - (t if lid not in ("S",) else 0.3)
            hits = [kd for o, kd in okna if o.distance(pt) < max(0.35, (b - a))]
            is_win = bool(hits)
            ribbon = "wstega" in hits
            if lid in ("-1", "-2"):
                svg.poly([P(a, z - 1.1), P(b, z - 1.1), P(b, ztop), P(a, ztop)], fill=POCHE, stroke="none")
                continue
            if is_win:
                in_tw = TOWER.buffer(0.3).contains(pt)
                if ribbon:
                    sill, head = ((0.3, 8.55) if lid == "S" else (1.30, ztop - z - 0.02))
                elif lid == "P":
                    sill, head = 0.0, 4.4
                elif lid == "S":
                    sill, head = 0.7, 5.7
                elif in_tw:             # wieża: parapet 0,55 / nadproże 3,00; kond. 5 nad kordonem (+20,85)
                    sill, head = (Z_KORDON - z if lid == "5" else float(EWI["parapet_m"])), float(EWI["nadproze_m"])
                else:                   # skrzydło i segment: parapet 0,60 / nadproże 2,95
                    sill, head = float(ESK["parapet_m"]), float(ESK["nadproze_m"])
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
                    zS = Z_K["S"]
                    svg.poly([P(uu, zS), P(min(b, uu + 0.25), zS), P(min(b, uu + 0.25), zS + lift), P(uu, zS + lift)], fill=POCHE, stroke="none")
                uu += 0.25
            # people seated + presidium figure
            for q in range(1, int((b - a) / 2.2)):
                person(svg, P, a + q * 2.2, Z_K["S"] + 0.45, h=1.25)
            # kratownice dachu 1,60 m nad salą (spód rusztu +34,15 → płyta +35,80)
            zt, zb = Z_DECK_W, Z_DECK_W - H_TRUSS
            svg.line(P(a, zt), P(b, zt), stroke=POCHE, sw=0.35)
            svg.line(P(a, zb), P(b, zb), stroke=POCHE, sw=0.35)
            nseg = max(2, int((b - a) / 2.7))
            for q in range(nseg):
                x0 = a + (b - a) * q / nseg; x1 = a + (b - a) * (q + 1) / nseg
                svg.line(P(x0, zb), P((x0 + x1) / 2, zt), stroke=POCHE, sw=0.18)
                svg.line(P((x0 + x1) / 2, zt), P(x1, zb), stroke=POCHE, sw=0.18)
    # roof slabs + attics
    # (bryła, spód płyty dachu, wierzch pokrycia/tarasu, attyka) z koncepcja.json
    roofs = [(TOWER, Z_DECK_W, Z_ROOF_W_MAX, Z_ATT_W), (WING, Z_ROOF_M_SP, Z_ROOF_M_MAX, Z_GZ), (SEG, Z_ROOF_S_SP, Z_TARAS, Z_ATT_S)]
    for g, zs, zr, za in roofs:
        for a, b in intervals(g, line, U):
            svg.poly([P(a, zs), P(b, zs), P(b, zr), P(a, zr)], fill=POCHE, stroke="none")
            for x, inward in ((a, 1.0), (b - 0.5, -1.0)):
                xe = x + (0.0 if inward > 0 else 0.5)                 # krawędź zewnętrzna na licu
                ee, nn = p0[0] + r[0] * xe, p0[1] + r[1] * xe
                pt = Point(ee, nn)
                if g is not TOWER and TOWER.buffer(0.4).contains(pt):
                    continue                                           # styk z wieżą – bez attyki (obróbka, G-D-3)
                if g is SEG and SEG_S_FACE.distance(pt) < 0.6:         # ściana pd. segmentu: attyka 139,10 = taras
                    za_ = Z_ATT_SPD
                else:
                    za_ = za
                if za_ > zr + 0.01:
                    svg.poly([P(x, zr), P(x + 0.5, zr), P(x + 0.5, za_), P(x, za_)], fill=POCHE, stroke="none")
                if g is SEG:   # balustrada szklana 1,10 m cofnięta 1,5 m od lica (WT § 298)
                    xb = xe + inward * BAL_COF
                    svg.line(P(xb, zr), P(xb, zr + BAL_H), stroke="#4a6a85", sw=0.25)
    # ściany szczelinowe (v1.1: grubość i głębokość z siatka.posadowienie, obrys −1/−2 z koncepcja.json) i pale pod wieżą
    for a, b in intervals(UG_K, line, U):
        for x in (a, b - T_DW):
            svg.poly([P(x, Z_DW_TOP), P(x + T_DW, Z_DW_TOP), P(x + T_DW, Z_DW_TOP - H_DW), P(x, Z_DW_TOP - H_DW)], fill="#3a3632", stroke="none")
    z_pal = float(PD["spod"])
    for a, b in intervals(TOWER, line, U):
        x = a + 2.0
        while x < b - 1.5:
            svg.poly([P(x, z_pal), P(x + D_PAL, z_pal), P(x + D_PAL, z_pal - L_PAL), P(x, z_pal - L_PAL)], fill="#ffffff", stroke="#3a3632", sw=0.15, extra='stroke-dasharray="0.8,0.5"')
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
    marks = [(Z_ATT_W, fz(Z_ATT_W)), (Z_ROOF_W, fz(Z_ROOF_W)), (Z_K["ANT"], f"{fz(Z_K['ANT'])} galeria")]
    for kid in reversed(K_IDS):
        zk = Z_K[kid]
        if kid == "P":
            marks.append((zk, f"±0,00 = {Z0:.2f} (P)".replace(".", ",")))
        elif kid == "S":
            marks.append((zk, f"{fz(zk)} S"))
        else:
            marks.append((zk, f"{fz(zk)} ({kid.replace('-', '−')})"))
    for z, lab in marks:
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
_WARNED = set()
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
                              f"Segment P+4 z tarasem zielonym {fz(Z_TARAS)} (attyka pd. {Z_ATT_SPD + Z0:.2f}),".replace(".", ",", 1),
                              "balustrada szklana 1,10 m cofnięta 1,5 m od lica pd. (WT § 298).",
                              "Odległość segment – szczyt WS 5: 10,58 m; okno w szczycie",
                              "zachowane (§ 13 WT – analiza nasłonecznienia na planszy 2).",
                              f"Podziemie: −1 ({fz(Z_K['-1'])}) / −2 ({fz(Z_K['-2'])}) w ścianach szczelinowych",
                              f"{T_DW:.2f} m × {H_DW:.0f} m (wcięte w gliny QpB), biała wanna, płyta".replace(".", ",", 1),
                              f"{float(PD['grubosc_wieza_m']):.2f} m na palach CFA Ø {D_PAL:.1f} m L ≈ {L_PAL:.0f} m; poziom".replace(".", ","),
                              "obliczeniowy wód 117,00 m n.p.m."]))
    VB = 19.6
    pB0, pB1 = uv(-24.0, VB), uv(52.0, VB)
    res.append(section("BB", "PRZEKRÓJ B-B", "v = 19,6 m: ul. Mazowiecka – skrzydło – Hala Obywatelska i sala obrad – ul. Wybrzeże J. Słowackiego · widok na północ",
                       pB0, pB1,
                       [(pB0[0], pB0[1], 119.30), (*uv(-14.5, VB), 119.35), (*uv(0, VB), 119.38), (*uv(40, VB), 119.30), (*uv(46, VB), 119.25), (pB1[0], pB1[1], 119.20)],
                       places=[(5.0, -1.4, "ul. Mazowiecka"), (69.0, -1.4, "ul. Wybrzeże J. Słowackiego")],
                       neighbours=[], beyond_names=(),
                       notes=["Skrzydło P+4: gzyms +20,85 = 140,15 m n.p.m. w linii attyki",
                              f"kamienicy Mazowiecka 19 (140,24); biura {K['wysokosci_w_swietle']['biura_skrzydlo']:.2f} m w świetle.".replace(".", ",", 1),
                              f"Wieża: biura {K['wysokosci_w_swietle']['biura_wieza']:.2f} m w świetle (TABS, płyta 0,28 m),".replace(".", ","),
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
