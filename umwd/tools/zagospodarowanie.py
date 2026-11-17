#!/usr/bin/env python3
"""Koncepcja zagospodarowania terenu 1:500 (Etap II, Reg. R.VII ust.2 pkt2 lit.a) — z mapy (site.json) i specyfikacji (koncepcja.json).

Zawartość: rzut dachów z rzędnymi i liczbą kondygnacji (z zadaszeniem BIPV tarasu ogrodowego), komunikacja (wejścia, zjazd,
dostawy, drogi pożarowe, ruch pieszy i rowerowy, parkowanie rowerów), zieleń istniejąca/usuwana/przesadzana/nowa,
nawierzchnie, retencja, mała architektura, cienie przy Słońcu z SW pod 45°.
Stan v1.1 (po weryfikacji): drzewa w obszarze inwestycji wg numeracji i położeń operatu M.06 (`_rewizja_drzewa.py` →
`docs/20_koncepcja/_rewizja_drzewa_wynik.json`, ±0,5–1 m), decyzje z koncepcja.json `zagospodarowanie.*_M06`;
poza obszarem inwestycji – drzewa z mapy M.02 (site.json). Ścieżki ogrodu poza poligonem ogródków (KOORD-3).
Wynik: build/rysunki/zagospodarowanie_1-500.svg (+ .html/.png podgląd w docs/70_rysunki/podglady/).
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from umwd.svg import Svg, View, model_rings, model_poly, north_arrow, scale_bar
from umwd.siteplan import load_site, poly_of, shadow_poly, C

S = load_site()
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
Z = K["zagospodarowanie"]
Z0 = K["meta"]["zero"]["wzgl_0_00_m_npm"]
INK, ACC = "#1f1d1a", "#a8483a"
B = {b["id"]: b for b in K["bryly"]}
tower, wing, seg = (Polygon(B[k]["obrys_ccw"]).buffer(0) for k in ("W", "M", "S"))
inv = Polygon(S["granice"]["obszar_inwestycji"]["pts"]).buffer(0)
comp = Polygon(S["granice"]["granica_opracowania_konkursowego"]["pts"]).buffer(0)
skwer = Polygon(S["granice"]["teren_uzyczony_dz_9_2"]["pts"]).buffer(0)
ogrodki = Polygon(S["granice"]["ogrodki_przydomowe"]["pts"]).buffer(0)
d102 = Polygon(S["granice"]["dojazd_dz_10_2"]["pts"]).buffer(0)
L1 = Polygon(K["podziemie"]["-1"]["obrys_ccw"]).buffer(0)          # obrys kondygnacji −1 (strop garażu pod dziedzińcem)
bld = unary_union([tower, wing, seg])
garden = inv.difference(bld.buffer(0.05))
H = {"W": B["W"]["dach"]["attyka"]["wzgl"], "M": B["M"]["dach"]["gzyms_attyka"]["wzgl"], "S": B["S"]["dach"]["attyka"]["wzgl"]}
PV = K["elewacje"]["PV"]


def uv2en(u, v):
    """Układ wieży (u, v) → (e, n) – jak koncepcja.json meta / _rewizja_wspolne.py."""
    return (74.606 + 0.97155 * u - 0.23684 * v, 40.756 + 0.23684 * u + 0.97155 * v)


def rect_uv(u0, v0, u1, v1):
    return Polygon([uv2en(u0, v0), uv2en(u1, v0), uv2en(u1, v1), uv2en(u0, v1)])


def fmt(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


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

# ---------------- elementy projektu v1.1 (geometria)
# taras ogrodowy na stropie pasa −1 (v 0…−5,0; u −3,90…21,0) – nawierzchnia, bez nasadzeń
terrace = rect_uv(-3.90, -5.0, 21.0, 0.0).intersection(garden)
# zadaszenie BIPV tarasu ogrodowego wzdłuż elewacji pd. wieży (u 0,5–20,5, głęb. 4,0 m, h ≈ 4,0 m) – rozdz. 4.4 spec.
canopy = rect_uv(0.5, -4.0, 20.5, 0.0)
# pas 4,6 m pd. od segmentu (wejście od bulwaru) i skrzynki rozsączające −0,6 m od krawędzi (jak _rewizja_geometria.py pkt 7)
_sw = LineString([(96.694, 38.813), (115.979, 39.930)])
strip46 = inv.intersection(_sw.buffer(4.6, single_sided=True).union(_sw.buffer(-4.6, single_sided=True))).difference(seg).difference(d102)
strip46 = strip46.intersection(Polygon([(96.0, 25.0), (118.0, 25.0), (118.0, 39.9), (96.0, 38.8)]))
crates = strip46.buffer(-0.6, join_style=2)
# ogród deszczowy 140 m² – dwie płytkie niecki przy wsch. granicy ogrodu, na gruncie rodzimym; poza strefami drzew M.06
# (Z1/Z2 pełne, Z3 −1,0 m), poza ogródkami, ścieżką, szybem i tunelem MDS, ≥ 0,8 m od granicy (wyznaczone w shapely)
RAIN = [[(87.14, 17.46), (87.26, 17.98), (87.71, 18.26), (89.6, 17.93), (91.16, 18.24), (92.2, 18.85), (93.18, 19.95), (94.38, 20.8),
         (94.92, 20.86), (95.36, 20.49), (96.14, 0.63), (95.85, 0.04), (90.93, 0.01), (90.59, 0.28), (90.4, 2.12), (89.97, 3.81),
         (91.56, 5.43), (92.48, 6.97), (92.93, 8.76), (92.84, 10.57), (92.22, 12.28), (91.13, 13.75), (89.67, 14.82), (87.47, 15.68)],
        [(89.0, 32.75), (89.21, 31.47), (89.58, 30.57), (90.12, 29.98), (90.98, 29.52), (91.77, 29.4), (92.73, 29.59), (94.22, 30.68),
         (94.94, 30.4), (95.29, 24.04), (94.98, 23.44), (94.21, 23.43), (93.18, 24.11), (92.2, 25.21), (91.16, 25.82), (89.99, 26.11),
         (88.05, 26.03), (87.21, 27.13), (87.1, 28.24), (87.36, 29.73), (87.12, 31.2), (87.23, 32.54), (87.67, 32.96), (88.55, 32.99)]]
rain = unary_union([Polygon(r) for r in RAIN]).intersection(garden)
# ścieżki ogrodu – obrzeżem, poza poligonem ogródków (KOORD-3); w ogródkach tylko istniejące ścieżki i trawnik
PATHS = [[(86.4, 38.6), (85.9, 31.0), (85.9, 24.0), (84.2, 19.5), (83.9, 14.0), (83.7, 9.0), (86.2, 4.0), (86.9, -1.0),
          (85.8, -4.7), (79.7, -4.75), (75.9, -4.2), (70.4, -3.4)],                 # wsch. i pd. obrzeże ogródków
         [(86.9, -1.0), (90.6, -2.6)],                                              # do placu zabaw
         [(66.95, 20.3), (70.15, 34.6)],                                            # od bramy ogrodowej wzdłuż lica wsch. skrzydła
         [(97.6, 36.9), (95.6, 37.6), (95.2, 40.6)]]                                # wylot pasa od bulwaru → taras
paths = unary_union([LineString(p).buffer(0.9, cap_style=2, join_style=2) for p in PATHS])
paths = paths.difference(ogrodki).intersection(garden).difference(terrace).difference(strip46)
# mały plac zabaw (poza ogródkami i strefami drzew)
play = Polygon([(90.6, -6.0), (96.3, -5.8), (96.3, -0.6), (90.6, -0.6)]).intersection(garden)
# szyb wyjścia zapasowego MDS (91,75; 32,00) – płaska klapa w trawniku (P-I6)
SHAFT = (91.75, 32.00)

# ---------------- proposal ground surfaces
GRANIT, CEGLA, TRAWA, DESZCZ, TARAS, PRZEP = "#ece8e1", "#d9b9a3", "#dfe8d2", "#cfe0e1", "#e3dfd7", "#e8d6c6"
model_rings(svg, v, skwer.union(inv.difference(bld)).intersection(comp), fill=GRANIT, stroke="none")
# fine granite grid on the bridge square
gx = svg.hatch("granit", spacing=0.9, angle=76.3, stroke="#d8d2c8", sw=0.06)
model_rings(svg, v, skwer, fill=gx, stroke="none")
# garden: lawn, kept allotments, terrace, permeable strip with soakaway crates, rain garden, paths
lawn = garden.intersection(box(60, -10, 100, 42)).difference(terrace).difference(strip46)
model_rings(svg, v, lawn, fill=TRAWA, stroke="none")
model_rings(svg, v, ogrodki.intersection(inv), fill="#d6e2c6", stroke="#9fb07f", sw=0.12, extra='stroke-dasharray="0.8,0.6"')
ht = svg.hatch("taras", spacing=0.675, angle=76.3, stroke="#d2ccc2", sw=0.05)
model_rings(svg, v, terrace, fill=TARAS, stroke="none")
model_rings(svg, v, terrace, fill=ht, stroke="none")
model_rings(svg, v, strip46, fill=PRZEP, stroke="none")
model_rings(svg, v, crates, fill="none", stroke="#5b8db5", sw=0.15, extra='stroke-dasharray="0.9,0.5"')
model_rings(svg, v, rain, fill=DESZCZ, stroke="#7ea7ad", sw=0.15)
model_rings(svg, v, paths, fill=CEGLA, stroke="none")
model_rings(svg, v, play, fill="#efe2c4", stroke="#b9a072", sw=0.15)
# ławki przy murze kamienic (pd. granica ogrodu) + ława granitowa w pasie od bulwaru
_a, _b = (69.855, -7.551), (97.2, -6.56)
_L = math.dist(_a, _b)
_t, _nrm = ((_b[0] - _a[0]) / _L, (_b[1] - _a[1]) / _L), (-(_b[1] - _a[1]) / _L, (_b[0] - _a[0]) / _L)
for s0 in (8.6, 13.0):
    q = [(_a[0] + _t[0] * s + _nrm[0] * o, _a[1] + _t[1] * s + _nrm[1] * o) for s, o in ((s0, 0.7), (s0 + 3.6, 0.7), (s0 + 3.6, 1.25), (s0, 1.25))]
    model_poly(svg, v, q, fill="#b9a68c", stroke=INK, sw=0.1)
model_poly(svg, v, [(98.5, 38.0), (104.0, 38.3), (104.0, 38.9), (98.5, 38.6)], fill="#bdb6ab", stroke=INK, sw=0.1)
# obrys kondygnacji −1 pod dziedzińcem (strop garażu) – nasadzenia tylko poza nim
_l1 = LineString(list(L1.exterior.coords)).intersection(garden.buffer(-0.15))
for g in ([_l1] if _l1.geom_type == "LineString" else list(getattr(_l1, "geoms", []))):
    if g.geom_type == "LineString" and g.length > 0.5:
        svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#7d6a9a", sw=0.22, close=False, extra='stroke-dasharray="1.4,0.6,0.3,0.6"')

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
HP_BIPV = svg.hatch("bipv", spacing=1.4, angle=76.3 + 90, stroke="#7c7f86", sw=0.12)


def roof(pg, label_lines, at, bipv=True, green=False, rot=0.0):
    model_rings(svg, v, pg, fill="#ffffff", stroke=INK, sw=0.5)
    inner = pg.buffer(-0.8, join_style=2)
    model_rings(svg, v, inner, fill="none", stroke=INK, sw=0.12)
    if bipv:
        model_rings(svg, v, inner.buffer(-1.5, join_style=2), fill=HP_BIPV, stroke="#7c7f86", sw=0.1)
    if green:
        model_rings(svg, v, inner, fill="#dfe8d2", stroke="none")
    x, y = v.p(*at)
    for i, (t, sz, w) in enumerate(label_lines):
        svg.text((x, y + i * 3.0), t, size=sz, anchor="middle", weight=w)


KWP_W = round(PV["pola"]["dach_wiezy_m2"] * PV["gestosc_dach_kWp_m2"])      # 948 × 0,215 = 204
KWP_M = round(PV["pola"]["dach_skrzydla_m2"] * PV["gestosc_dach_kWp_m2"])   # 685 × 0,215 = 147
wz = B["W"]["dach"]["attyka"]
roof(tower, [("WIEŻA SEJMIKU", 2.4, 600), ("P+6+S · attyka +" + f"{wz['wzgl']:.2f} = {wz['npm']:.2f}".replace('.', ',') + " m n.p.m.", 1.9, 400),
             ("pokrycie min. +" + f"{B['W']['dach']['najnizszy_pkt_pokrycia']['wzgl']:.2f}".replace('.', ',') + " (MPZP: 35–45 m)", 1.8, 400),
             (f"dach: BIPV {KWP_W} kWp, bez urządzeń", 1.8, 400)], (93.0, 64.5))
mz = B["M"]["dach"]["gzyms_attyka"]
roof(wing, [("SKRZYDŁO", 2.1, 600), ("P+4", 1.9, 400), (f"attyka +{mz['wzgl']:.2f}".replace('.', ','), 1.8, 400), (f"= {mz['npm']:.2f}".replace('.', ','), 1.8, 400),
            (f"BIPV {KWP_M} kWp", 1.7, 400)], (60.2, 40.0))
# segment: taras (dach zielony) w attyce; attyka ściany pd. obniżona do poziomu tarasu, balustrada szklana cofnięta 1,5 m
SD = B["S"]["dach"]
tz = SD["taras_wykonczenie"]
model_rings(svg, v, seg, fill="#ffffff", stroke=INK, sw=0.5)
seg_in = seg.buffer(-0.8, join_style=2)
s_face = LineString([(96.694, 38.813), (115.979, 39.930)])          # lico pd. segmentu (od dz. 10/2)
_att_bands = seg.difference(seg_in).difference(s_face.buffer(0.85, cap_style=2))   # attyki lic pn., wsch., zach.
model_rings(svg, v, seg.difference(_att_bands), fill="#dfe8d2", stroke="none")      # taras do lica pd. (attyka = poziom tarasu)
_att = LineString(list(seg_in.exterior.coords)).difference(s_face.buffer(1.0, cap_style=2))
for g in ([_att] if _att.geom_type == "LineString" else list(getattr(_att, "geoms", []))):
    svg.poly([v.p(*c) for c in g.coords], fill="none", stroke=INK, sw=0.12, close=False)
_bal = s_face.parallel_offset(1.5, "left").intersection(seg.buffer(-0.5, join_style=2))
for g in ([_bal] if _bal.geom_type == "LineString" else list(getattr(_bal, "geoms", []))):
    if g.geom_type == "LineString":
        svg.poly([v.p(*c) for c in g.coords], fill="none", stroke="#4a6a85", sw=0.35, close=False)
_xa, _ya = v.p(106.3, 39.78)
svg.text((_xa, _ya), f"attyka pd. {fmt(SD['attyka']['sciana_pd_npm'])} · balustrada szklana cofnięta 1,5 m", size=1.2, anchor="middle",
         fill="#3a3632", rot=-3.3)
x, y = v.p(105.0, 45.0)
for i, (t, sz, w) in enumerate([("TARAS · dach zielony", 1.7, 600), (f"{fmt(SD['taras_pow_m2'], 1)} m² · P+4", 1.5, 400),
                                (f"+{fmt(tz['wzgl'])} = {fmt(tz['npm'])}", 1.5, 400)]):
    svg.text((x, y + i * 2.6), t, size=sz, anchor="middle", weight=w)
# zadaszenie BIPV tarasu ogrodowego (element rzutu dachów, ≈ +4,0 m nad tarasem)
model_rings(svg, v, canopy, fill="#ffffff", stroke="none", extra='fill-opacity="0.55"')
HP_CAN = svg.hatch("bipv_zadaszenie", spacing=1.0, angle=76.3 + 90, stroke="#6f7480", sw=0.1)
model_rings(svg, v, canopy, fill=HP_CAN, stroke=INK, sw=0.3)
x, y = v.p(*uv2en(12.5, -2.75))
svg.text((x, y), f"zadaszenie BIPV · {PV['pola']['zadaszenie_tarasu_ogrodowego_m2']} m² · {PV['BIPV_zadaszenie_kWp']} kWp · h ≈ 4 m",
         size=1.3, anchor="middle", weight=600, rot=-13.7, fill="#2c2f36")

# ---------------- drzewa
# M.06 (obszar inwestycji): położenia z _rewizja_drzewa_wynik.json, decyzje v1.1 z koncepcja.json
W06 = json.loads((ROOT / "docs" / "20_koncepcja" / "_rewizja_drzewa_wynik.json").read_text(encoding="utf-8"))
POS = {int(k): tuple(p) for k, p in W06["polozenia_M06"].items()}
REM06, TRANS06, U06 = set(Z["drzewa_usuniete_M06"]), set(Z["drzewa_przesadzane_M06"]), set(Z["drzewa_U_sanitarnie_M06"])
KEEP06 = sorted(set(POS) - REM06 - TRANS06 - U06)
for kk, cat in (("kolizja", REM06), ("przesadzane", TRANS06), ("sanitarnie", U06)):
    if set(W06["bilans"].get(kk, [])) != cat:
        print(f"UWAGA: koncepcja.json ({sorted(cat)}) ≠ _rewizja_drzewa_wynik.json [{kk}] ({W06['bilans'].get(kk)})")
IGLASTE_M06 = {8, 15, 16, 17, 38, 52, 53, 54, 55, 56, 57, 59, 72, 78}     # świerki, sosny, jodła (dendrologia.md tab. 2)
_m02 = {}
for t in S["zielen"]["drzewa"]:
    _m02.setdefault(t["nr"], []).append((t["e"], t["n"]))


def m06_of(nr02, among):
    """Numer M.06 najbliższy punktowi M.02 (site.json) – parowanie po położeniu (inna numeracja)."""
    p = tuple(sum(c) / len(c) for c in zip(*_m02[nr02]))
    k = min(among, key=lambda n: math.dist(POS[n], p))
    return k, math.dist(POS[k], p)


# usuwane kolizyjnie wg zagospodarowanie.drzewa_usuniete (numeracja M.02) → numery M.06 (kontrola zgodności)
REM_PAIRS = {d: m06_of(d, REM06) for d in Z["drzewa_usuniete"] if d in _m02}
if sorted(k for k, _ in REM_PAIRS.values()) != sorted(REM06) or max(dd for _, dd in REM_PAIRS.values()) > 2.0:
    print("UWAGA: drzewa_usuniete (M.02) nie pokrywają się 1:1 z drzewa_usuniete_M06:", REM_PAIRS)
PROT06 = {m06_of(d, KEEP06)[0]: d for d in Z["drzewa_chronione_palisada"] if d in _m02}   # I881 → nr 78
STREFA_78 = 3.1   # strefa projektowa nr 78 wg M.06 (dendrologia.md tab. 2) – wygrodzenie korona + 1 m


def sym_kept(xy, rr):
    svg.circle(xy, rr, fill="#93a77c", stroke="#ffffff", sw=0.12, extra='fill-opacity="0.55"')
    svg.circle(xy, v.mm(0.22), fill="#3d4a33", stroke="none")


def sym_removed(xy, rr):
    x, y = xy
    svg.circle((x, y), rr, fill="none", stroke="#b5aea4", sw=0.1, extra='stroke-dasharray="0.6,0.5"')
    svg.line((x - rr * .55, y - rr * .55), (x + rr * .55, y + rr * .55), stroke="#a39c92", sw=0.15)
    svg.line((x - rr * .55, y + rr * .55), (x + rr * .55, y - rr * .55), stroke="#a39c92", sw=0.15)


UCOL = "#a8742a"


def sym_u(xy, rr):
    svg.circle(xy, rr, fill="#f3e6cf", stroke=UCOL, sw=0.16, extra='fill-opacity="0.55" stroke-dasharray="0.7,0.45"')
    svg.text((xy[0], xy[1] + 0.5), "U", size=1.4, anchor="middle", weight=700, fill=UCOL)


PCOL = "#3f6f8f"


def sym_trans(xy, rr):
    svg.circle(xy, rr, fill="none", stroke=PCOL, sw=0.18, extra='stroke-dasharray="0.7,0.45"')
    svg.text((xy[0], xy[1] + 0.5), "P", size=1.4, anchor="middle", weight=700, fill=PCOL)


def sym_new(xy, rr, op=0.7, dash=False):
    ex = f'fill-opacity="{op}"' + (' stroke-dasharray="0.8,0.5"' if dash else "")
    svg.circle(xy, rr, fill="#5f8050", stroke="#2f4227", sw=0.2, extra=ex)
    svg.circle(xy, v.mm(0.25), fill="#1f2a18", stroke="none")


def crown(nr):
    return 2.0 if nr in IGLASTE_M06 else 3.2


# poza obszarem inwestycji – drzewa z mapy M.02 (bez zmian)
rem02 = set(Z["drzewa_usuniete"])
for t in S["zielen"]["drzewa"]:
    p = (t["e"], t["n"])
    if inv.contains(Point(p)):
        continue                                   # w obszarze inwestycji obowiązuje inwentaryzacja M.06
    r = 3.2 if t.get("typ") == "lisciaste" else 2.0
    if t["nr"] in rem02:
        sym_removed(v.p(*p), v.mm(r))
        continue
    if bld.buffer(0.3).contains(Point(p)):
        continue
    sym_kept(v.p(*p), v.mm(r))
# w obszarze inwestycji – M.06
for nr in sorted(POS):
    p = POS[nr]
    xy, rr = v.p(*p), v.mm(crown(nr))
    if nr in REM06:
        sym_removed(xy, rr)
        svg.text((xy[0] + rr * 0.75, xy[1] - rr * 0.6), str(nr), size=1.25, fill="#8d877f")
    elif nr in U06:
        sym_u(xy, rr)
    elif nr in TRANS06:
        sym_trans(xy, rr)
    else:
        sym_kept(xy, rr)
        if nr in PROT06:
            svg.circle(xy, v.mm(STREFA_78 + 1.0), fill="none", stroke="#2f5a2c", sw=0.22, extra='stroke-dasharray="0.5,0.4"')
            svg.text((xy[0] + v.mm(STREFA_78 + 1.2), xy[1] + 0.5), f"{nr} ({PROT06[nr]})", size=1.25, fill="#2f5a2c", weight=600)
# nowe nasadzenia v1.1 (26): 4 lipy przy śladzie 1934 + 2 u wylotu pasa od bulwaru + 14 w ogrodzie + 6 na chodniku od rzeki
lindens = [(66.0, 79.4), (71.5, 80.3), (77.0, 81.0), (82.5, 81.6)]                    # szpaler 4 lip drobnolistnych (skwer 9/2)
strip_trees = [(95.9, 35.6), (88.75, 35.5)]           # u wylotu pasa 4,6 m od bulwaru (pas zajmują skrzynki rozsączające)
# 14 w ogrodzie na gruncie rodzimym: poza obrysem −1 (≥ 1,8 m), poza ogródkami, strefami drzew M.06, ścieżkami, placem zabaw,
# szybem i tunelem MDS; rozstaw ≥ 4,5 m (w tym 8 nasadzeń zastępczych)
garden_trees = [(87.25, 31.25), (94.75, 29.75), (87.5, 26.75), (86.5, 19.25), (95.25, 17.25), (91.25, 15.0), (94.75, 7.75),
                (90.0, 3.75), (94.75, -0.25), (88.75, -5.75), (75.75, -6.25), (71.1, -6.2), (80.75, 35.25), (71.5, 33.0)]
TRANS_TO = {72: (65.75, 7.25)}                        # jodła nr 72 – nowe miejsce w ogrodzie (kąt przy Maz. 19)
# 6 drzew na chodniku od rzeki (Wybrzeże, spec §9): 1,4 m za krawężnikiem wsch., poza pasem roboczym drogi pożarowej
_kerbs = unary_union([LineString(it["pts"]) for it in u["krawezniki"]])
river_trees = []
for nn in (16.0, 24.0, 32.0, 40.0, 48.0, 56.0):
    _x = _kerbs.intersection(LineString([(123.5, nn), (131.6, nn)]))
    if not _x.is_empty:
        river_trees.append((_x.bounds[2] + 1.4, nn))
print("river trees", river_trees)
# kontrola położeń nowych drzew w ogrodzie
_allp = strip_trees + garden_trees + list(TRANS_TO.values())
for i, p in enumerate(_allp):
    P_ = Point(p)
    bad = [k for k, ok in (("poza ogrodem", garden.buffer(-0.9).contains(P_)), ("strop −1", P_.distance(L1) >= 1.75),
                           ("ogródki", P_.distance(ogrodki) >= 0.45), ("budynek", P_.distance(bld) >= 1.7),
                           ("ścieżka", P_.distance(paths) >= 0.35), ("skrzynki", not crates.contains(P_)),
                           ("plac zabaw", P_.distance(play) >= 0.25), ("szyb MDS", P_.distance(Point(SHAFT)) >= 3.0)) if not ok]
    bad += [f"rozstaw {math.dist(p, q):.1f} m" for q in _allp[i + 1:] if math.dist(p, q) < 4.45]
    bad += [f"pień M.06 nr {n} {math.dist(p, POS[n]):.1f} m" for n in KEEP06 if math.dist(p, POS[n]) < 3.0]
    if bad:
        print("UWAGA drzewo", p, bad)
for nr, q in TRANS_TO.items():
    a, b = v.p(*POS[nr]), v.p(*q)
    svg.line(a, b, stroke=PCOL, sw=0.18, dash="0.8,0.5")
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    svg.poly([b, (b[0] - 1.3 * math.cos(ang - 0.4), b[1] - 1.3 * math.sin(ang - 0.4)), (b[0] - 1.3 * math.cos(ang + 0.4), b[1] - 1.3 * math.sin(ang + 0.4))],
             fill=PCOL, stroke="none")
    svg.circle(b, v.mm(2.0), fill="#93a77c", stroke=PCOL, sw=0.2, extra='fill-opacity="0.6"')
    svg.text((b[0] + v.mm(2.2), b[1] + 0.5), f"{nr} P", size=1.25, fill=PCOL, weight=600)
for p in lindens + strip_trees + garden_trees:
    sym_new(v.p(*p), v.mm(2.6))
for p in river_trees:
    sym_new(v.p(*p), v.mm(2.4), op=0.35, dash=True)
N_IN = len(lindens) + len(strip_trees) + len(garden_trees)
N_NEW = N_IN + len(river_trees)
if N_NEW != Z["nowe_nasadzenia"]:
    print(f"UWAGA: nowe nasadzenia na rysunku {N_NEW} ≠ koncepcja.json {Z['nowe_nasadzenia']}")
N_KEPT_OI = len(KEEP06)
N_ALL = len(POS)
N_KEEP_ALL = N_KEPT_OI + len(TRANS06) + len(U06)          # 36 – bez usunięć sanitarnych
N_KEEP_SAN = N_KEPT_OI + len(TRANS06)                     # 26 – po usunięciach sanitarnych
if (N_ALL, N_KEEP_ALL, N_KEEP_SAN) != (Z["drzewa_w_OI_numery"], Z["zachowane_numery"], Z["zachowane_po_usunieciach_sanitarnych"]):
    print("UWAGA: bilans drzew ≠ koncepcja.json", N_ALL, N_KEEP_ALL, N_KEEP_SAN)
_og = [n for n in POS if ogrodki.contains(Point(POS[n]))]
OG_KEEP, OG_TR, OG_U, OG_REM = (sum(1 for n in _og if n in s) for s in (set(KEEP06), TRANS06, U06, REM06))
OG_AREA = ogrodki.intersection(inv).area
print(f"drzewa M.06: {N_ALL}; zachowane w miejscu {N_KEPT_OI}; bilans {N_KEEP_ALL}/{N_ALL} i {N_KEEP_SAN}/{N_ALL}; ogródki {len(_og)}: "
      f"{OG_KEEP} w miejscu, {OG_TR} przesadzane, {OG_U} U, {OG_REM} kolizja; ogródki w OI {OG_AREA:.1f} m²; ogród deszczowy {rain.area:.1f} m²; "
      f"ścieżki {paths.area:.0f} m², z czego w ogródkach {paths.intersection(ogrodki).area:.2f} m²")

# szyb wyjścia zapasowego MDS – klapa w trawniku
x, y = v.p(*SHAFT)
svg.poly([(x - 1.6, y - 1.6), (x + 1.6, y - 1.6), (x + 1.6, y + 1.6), (x - 1.6, y + 1.6)], fill="#ffffff", stroke=INK, sw=0.25)
svg.line((x - 1.6, y - 1.6), (x + 1.6, y + 1.6), stroke=INK, sw=0.12)
svg.line((x - 1.6, y + 1.6), (x + 1.6, y - 1.6), stroke=INK, sw=0.12)

# ---------------- boundaries
model_rings(svg, v, comp, fill="none", stroke="#2f6f8f", sw=0.35, extra='stroke-dasharray="3,1.2"')
model_rings(svg, v, inv, fill="none", stroke=ACC, sw=0.45, extra='stroke-dasharray="4,1,0.8,1"')

# ---------------- entrances (8) and service
# wejścia: 3 – elewacja wsch. wieży (v ≈ 4,1; wnęka v 1,4–6,8), 8 – brama garażu w części pn. segmentu (v −0,40…−4,40)
ENTR = [((103.2, 73.5), "1", "Brama Mostowa – wejście główne"), ((91.0, 76.6), "2", "wejście od skweru (podcień)"),
        ((113.08, 54.36), "3", "Wejście Obywatelskie (galeria Sejmiku)"), ((62.6, 69.8), "4", "wejście konferencyjne / bistro"),
        ((84.3, 42.6), "5", "wejście ogrodowe (pod zadaszeniem BIPV)"), ((77.6, 41.5), "6", "rowerownia (50 st.)"),
        ((51.8, 23.6), "7", "brama ogrodowa 4,05 m (przejście publiczne)"), ((114.6, 47.9), "8", "zjazd do garażu (brama 4,0 m, rampa jednopasowa), dostawy")]
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

# ---------------- level spots (terrain, m n.p.m.)
for (e, n, t) in [(104.5, 80.0, "119,30"), (80.0, 84.0, "119,45"), (120.5, 45.0, "119,10"), (45.5, 30.0, "118,55"), (82.0, 18.0, "118,95"), (101.0, 34.0, "119,00")]:
    x, y = v.p(e, n)
    svg.poly([(x - 1.0, y), (x + 1.0, y), (x, y + 1.3)], fill=INK, stroke="none")
    svg.text((x + 1.5, y + 0.6), t, size=1.7)

# ---------------- street names & labels
for (e, n, t, rot) in [(42.0, 34.0, "ul. Mazowiecka", -77.6), (124.6, 58.0, "ul. Wybrzeże J. Słowackiego", -77.0), (84.0, 86.6, "PLAC MOSTOWY", -4.0),
                       (78.0, 112.0, "przyczółek Mostu Grunwaldzkiego", -19.6), (78.0, 4.5, "OGRÓD WOJEWÓDZTWA", 0)]:
    svg.text(v.p(e, n), t, size=2.2 if t.isupper() else 2.0, anchor="middle", weight=600 if t.isupper() else 400, rot=rot, fill="#3a3632")
svg.text(v.p(99.0, 9.5), f"ogród deszczowy {rain.area:.0f} m²", size=1.6, anchor="middle", rot=-87.9, fill="#3d6670")
svg.line(v.p(98.2, 9.5), v.p(95.4, 9.5), stroke="#3d6670", sw=0.12)
svg.text(v.p(93.45, -3.5), "plac zabaw", size=1.45, anchor="middle", fill="#7a6440")
svg.text(v.p(106.5, 35.8), "skrzynki rozsączające pod nawierzchnią", size=1.25, anchor="middle", fill="#3f6f95", rot=-3.3)
svg.text(v.p(92.9, 32.6), "MDS", size=1.2, anchor="start", fill=INK)

# ---------------- legend
lx = v.w_mm + 6
y = 8
svg.text((lx, y), "KONCEPCJA ZAGOSPODAROWANIA TERENU", size=3.4, weight=600); y += 4.6
svg.text((lx, y), "skala 1:500 · cienie: promienie z SW pod kątem 45° · stan v1.1", size=2.2, fill="#4d4842"); y += 6.4
items = [("rect", "#ffffff", INK, ["rzut dachów projektowanych (rzędne, liczba kondygnacji)"]),
         ("rect", "#dcd8d1", "#6f6a63", ["budynki istniejące"]),
         ("hatch", "#7c7f86", None, [f"pokrycie dachów BIPV: wieża {KWP_W} kWp, skrzydło {KWP_M} kWp"]),
         ("canopy", None, None, [f"zadaszenie BIPV tarasu ogrodowego ({PV['pola']['zadaszenie_tarasu_ogrodowego_m2']} m², "
                                 f"{PV['BIPV_zadaszenie_kWp']} kWp), elewacja pd. wieży"]),
         ("rect", "#dfe8d2", INK, [f"taras segmentu – dach zielony {fmt(SD['taras_pow_m2'], 1)} m²; attyka pd. {fmt(SD['attyka']['sciana_pd_npm'])},",
                                    "balustrada szklana cofnięta 1,5 m od lica pd."]),
         ("rect", GRANIT, None, ["nawierzchnia z granitu strzegomskiego (skwer, wejścia)"]),
         ("rect", TARAS, None, ["taras ogrodowy na stropie pasa −1 (płyty, bez nasadzeń)"]),
         ("rect", CEGLA, None, ["ścieżki z cegły i gruzu z wykopu – obrzeżem, poza ogródkami;",
                                "w strefach drzew na gruncie, bez korytowania"]),
         ("crates", None, None, ["nawierzchnia przepuszczalna; skrzynki rozsączające 60 m² × 1,15 m"]),
         ("rect", TRAWA, None, ["trawnik, zieleń urządzona"]),
         ("rect", "#d6e2c6", "#9fb07f", [f"zachowane ogródki ({fmt(OG_AREA, 1)} m² w obszarze inw.): {len(_og)} drzew M.06 –",
                                          f"{OG_KEEP} w miejscu, {OG_TR} przesadzane, {OG_U} U; tylko istniejące ścieżki"]),
         ("rect", DESZCZ, "#7ea7ad", [f"ogród deszczowy {rain.area:.0f} m² (retencja 42 m³)"]),
         ("rect", "#efe2c4", "#b9a072", ["plac zabaw (poza ogródkami); ławki przy murze kamienic"]),
         ("l1", None, None, ["obrys kondygnacji −1 pod dziedzińcem (strop garażu)"]),
         ("shaft", None, None, ["klapa szybu wyjścia zapasowego MDS (tunel 7,6 m do −1)"]),
         ("tree_old", None, None, [f"drzewa zachowane w miejscu (M.06): {N_KEPT_OI}"]),
         ("tree_prot", None, None, [f"nr 78 M.06 (= I881): wygrodzenie korona + 1 m, odkrywki ręczne,", "nadzór arborysty – bez palisady"]),
         ("tree_trans", None, None, [f"drzewo przesadzane (nr {', '.join(map(str, sorted(TRANS06)))} – młoda jodła) w obrębie ogrodu"]),
         ("tree_rem", None, None, [f"drzewa usuwane kolizyjnie ({len(REM06)}): nr {', '.join(map(str, sorted(REM06)))}"]),
         ("tree_u", None, None, [f"U – martwe/zamierające ({len(U06)}): usunięcie sanitarne niezależne",
                                 "od inwestycji – decyzja arborysty"]),
         ("tree_new", None, None, [f"drzewa projektowane w granicy opracowania ({N_IN})"]),
         ("tree_prop", None, None, [f"drzewa proponowane poza granicą — chodnik od rzeki ({len(river_trees)})"]),
         ("line_trace", None, None, ["ślad pierzei kwartału z 1934 r. (granit + brąz)"]),
         ("line_fire", None, None, ["drogi pożarowe (jezdnie ulic)"]),
         ("ent", None, None, ["wejścia 1–8 (opis niżej)"]), ("rect", "none", ACC, ["obszar inwestycji"]),
         ("rect", "none", "#2f6f8f", ["granica opracowania konkursowego"])]
HP_LEG = svg.hatch("bipv_leg", spacing=1.0, angle=45, stroke="#7c7f86", sw=0.12)
HP_LEGC = svg.hatch("bipv_leg_c", spacing=0.7, angle=45, stroke="#6f7480", sw=0.1)
for kind, f, s, tl in items:
    cx, cy = lx + 3, y - 0.7
    if kind == "rect":
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=f, stroke=s or "none", sw=0.25)
    elif kind == "hatch":
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=HP_LEG, stroke=f, sw=0.15)
    elif kind == "canopy":
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=HP_LEGC, stroke=INK, sw=0.3)
    elif kind == "crates":
        svg.poly([(lx, y - 2.2), (lx + 6, y - 2.2), (lx + 6, y + 0.8), (lx, y + 0.8)], fill=PRZEP, stroke="none")
        svg.poly([(lx + 0.6, y - 1.6), (lx + 5.4, y - 1.6), (lx + 5.4, y + 0.2), (lx + 0.6, y + 0.2)], fill="none", stroke="#5b8db5", sw=0.15,
                 extra='stroke-dasharray="0.9,0.5"')
    elif kind == "l1":
        svg.line((lx, cy), (lx + 6, cy), stroke="#7d6a9a", sw=0.22, extra='stroke-dasharray="1.4,0.6,0.3,0.6"')
    elif kind == "shaft":
        svg.poly([(cx - 1.4, cy - 1.4), (cx + 1.4, cy - 1.4), (cx + 1.4, cy + 1.4), (cx - 1.4, cy + 1.4)], fill="#fff", stroke=INK, sw=0.25)
        svg.line((cx - 1.4, cy - 1.4), (cx + 1.4, cy + 1.4), stroke=INK, sw=0.12)
        svg.line((cx - 1.4, cy + 1.4), (cx + 1.4, cy - 1.4), stroke=INK, sw=0.12)
    elif kind == "tree_old":
        sym_kept((cx, cy), 1.5)
    elif kind == "tree_prot":
        sym_kept((cx, cy), 1.3)
        svg.circle((cx, cy), 2.1, fill="none", stroke="#2f5a2c", sw=0.22, extra='stroke-dasharray="0.5,0.4"')
    elif kind == "tree_trans":
        sym_trans((cx, cy), 1.5)
    elif kind == "tree_rem":
        sym_removed((cx, cy), 1.5)
    elif kind == "tree_u":
        sym_u((cx, cy), 1.5)
    elif kind == "tree_new":
        sym_new((cx, cy), 1.5)
    elif kind == "tree_prop":
        sym_new((cx, cy), 1.5, op=0.35, dash=True)
    elif kind == "line_trace":
        svg.line((lx, cy), (lx + 6, cy), stroke="#8b6a3e", sw=0.55)
    elif kind == "line_fire":
        svg.line((lx, cy), (lx + 6, cy), stroke="#c0392b", sw=0.45, dash="2.2,1.2")
    elif kind == "ent":
        svg.circle((cx, cy), 1.6, fill=ACC, stroke="none")
    for j, t in enumerate(tl):
        svg.text((lx + 8.5, y + j * 2.9), t, size=2.05)
    y += 4.3 + 2.9 * (len(tl) - 1)
y += 1.5
for (_, k, t) in ENTR:
    svg.text((lx, y), f"{k}", size=2.05, weight=700, fill=ACC); svg.text((lx + 4.5, y), t, size=2.05); y += 3.6
y += 2.5
_rem_txt = ", ".join(f"{m}={d}" for d, (m, _) in sorted(REM_PAIRS.items(), key=lambda kv: kv[1][0]))
for t, wgt in [("Drzewa w obszarze inwestycji – numeracja i położenia operatu M.06", 600),
               ("(±0,5–1 m; wiąże M.06), poza obszarem – mapa M.02. Usuwane M.06 = M.02:", 400),
               (_rem_txt + ".", 400),
               (f"Bilans: {N_ALL} drzew M.06; zachowane {N_KEEP_ALL} z {N_ALL} ({N_KEEP_ALL / N_ALL:.0%}) bez usunięć sanitarnych,".replace("%", " %"), 400),
               (f"{N_KEEP_SAN} z {N_ALL} ({N_KEEP_SAN / N_ALL:.0%}) po nich ({N_KEPT_OI} w miejscu + nr 72 przesadzony).".replace("%", " %"), 400),
               (f"Nowe nasadzenia {N_NEW}: {len(lindens)} lipy wzdłuż śladu 1934, {len(strip_trees)} u wylotu pasa od bulwaru,", 400),
               (f"{len(garden_trees)} w ogrodzie na gruncie rodzimym poza stropem garażu (w tym 8 zastępczych),", 400),
               (f"{len(river_trees)} – propozycja na chodniku od rzeki (poza granicą opracowania).", 400),
               (f"Zjazd do garażu ({K['podziemie']['razem_miejsc']} m.p., {K['podziemie']['EV_punkty']} EV) wyłącznie z Wybrzeża Słowackiego (6KDB/2):", 400),
               ("brama 4,0 m, rampa jednopasowa 3,50 m z sygnalizacją wahadłową; brak", 400),
               ("wjazdów z przyczółka (1KDG) i z ul. Mazowieckiej (MPZP §26 ust. 3).", 400),
               ("Rowery: 50 st. w parterze (wjazd od dziedzińca) + 20 na skwerze + 10 przy bramie.", 400),
               (f"Retencja {Z['retencja_m3']} m³ (= 2,2 × V60 {Z['V60_C10_m3']} m³): skrzynki 66 + rezerwa zbiornika 20", 400),
               ("+ ogród deszczowy 42 + dach niebieski 10 + podbudowa 19 – zero odpływu", 400),
               ("deszczu miarodajnego (przy k ≥ 1·10⁻⁶ m/s; inaczej dławik ≤ 2 dm³/s).", 400)]:
    svg.text((lx, y), t, size=1.95, fill="#3a3632", weight=wgt); y += 3.2
north_arrow(svg, (v.w_mm - 10, 12), 10)
scale_bar(svg, (8, v.h_mm + 7), 500, (0, 5, 10, 25, 50))

out = ROOT / "build" / "rysunki" / "zagospodarowanie_1-500.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "zagospodarowanie_1-500.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm+10:.0f}mm {svg.h_mm+10:.0f}mm;margin:0}}body{{margin:0}}</style></head><body><div style="padding:5mm">{svg.render()}</div></body></html>', encoding="utf-8")
print(out, round(svg.w_mm), round(svg.h_mm))
