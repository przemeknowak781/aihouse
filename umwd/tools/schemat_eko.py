#!/usr/bin/env python3
"""Schemat proekologiczny na przekroju przez Ogród Województwa i wieżę (oś u = 10 m, widok na zachód).
Liczby: koncepcja_wybrana.md v1.1 rozdz. 9–10 (bilans energii z `_bilans_energii.py` przez `_rewizja_pv_ep.py`) i koncepcja.json
(elewacje.PV, bilans, zagospodarowanie, siatka.posadowienie, podziemie).
W płaszczyźnie przekroju: zadaszenie BIPV tarasu ogrodowego przy elewacji pd. wieży (u 0,5–20,5, głęb. 4,0 m), niecki ogrodu
deszczowego (przecięcie z obrysem z tools/zagospodarowanie.py), sondy GPC pod płytą −2, ściany szczelinowe i pale energetyczne.
Schematycznie (poza płaszczyzną): zbiornik deszczówki 50 m³ na −2 przy łuku, skrzynki rozsączające w pasie pd. od segmentu.
Wynik: build/rysunki/schemat_eko_1-{UMWD_SCALE}.svg + docs/70_rysunki/podglady/schemat_eko.html (.png)
"""
import sys, json, math, copy
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from shapely.geometry import Polygon, LineString
from shapely.ops import unary_union
from umwd.svg import halo_extra
import przekroje as PR

K = PR.K


# ------------------------------------------------------------------ podziemie v1.1 w przekroju bazowym
# Rejestr G-I-2: pas −1/−2 pod dziedzińcem 7,0 → 5,0 m (lico v = −5,0). Model pomieszczeń budynek.json jest jeszcze w układzie
# v1.0 (płyty i ściany zewnętrzne −1/−2 do v = −7,0), a przekroje.section rysuje z niego płyty kondygnacji podziemnych, zaś ściany
# szczelinowe z obrysu koncepcja.json – na rysunku powstawały dwie ściany 2 m od siebie. Doraźnie (do czasu przeliczenia modelu
# pomieszczeń / przycięcia w przekroje.section) geometrię kondygnacji −1 i −2 przycinamy w pamięci do obrysów podziemia v1.1
# (koncepcja.json podziemie[−1], podziemie[−2]); pliki modelu nie są zmieniane. Operacja jest idempotentna.
def _rings(geom):
    """shapely → format budynek.json [[pierścień, otwory...], ...]."""
    out = []
    for g in getattr(geom, "geoms", [geom]):
        if g.geom_type == "Polygon" and not g.is_empty and g.area > 1e-4:
            out.append([[list(c) for c in g.exterior.coords]] + [[list(c) for c in r.coords] for r in g.interiors])
    return out


def _bm_podziemie_v11(bm):
    pod = K.get("podziemie", {})
    out = copy.deepcopy(bm)
    for lv in out["kondygnacje"]:
        lid = lv["id"]
        if lid not in ("-1", "-2") or not isinstance(pod.get(lid), dict) or "obrys_ccw" not in pod[lid]:
            continue
        obrys = Polygon(pod[lid]["obrys_ccw"]).buffer(0)
        lv["plyta"] = _rings(PR.mp(lv.get("plyta")).intersection(obrys))
        sc = lv.get("sciany") or {}
        for key in ("zewnetrzne", "wewnetrzne", "trzony"):
            if sc.get(key):
                sc[key] = _rings(PR.mp(sc[key]).intersection(obrys))
    return out


PR.BM = _bm_podziemie_v11(PR.BM)
Z = K["zagospodarowanie"]
EL = K["elewacje"]["PV"]
BIL = K["bilans"]
SUN, RAIN, HEAT, COOL, AIR, GREEN, INK = "#d99a2b", "#3f74a0", "#c0392b", "#2f6f9f", "#5e8f6b", "#5f8050", "#1f1d1a"
Z0 = PR.Z0

U0 = 10.0
V0, V1 = -46.0, 40.0
p0, p1 = PR.uv(U0, V0), PR.uv(U0, V1)
# teren v1.1: dziedziniec przy drzwiach ogrodowych 119,25, łagodnie (≤ 4 %) ku ogrodom (rozdz. 11)
GROUND = [(V0, 118.6), (-30.0, 118.75), (-12.0, 118.95), (-5.0, 119.2), (0.0, 119.25), (31.0, 119.4), (V1, 119.45)]
svg = PR.section("ECO", "SCHEMAT PROEKOLOGICZNY", "przekrój przez Ogród Województwa i wieżę (u = 10 m) · budynek bezemisyjny bez spalania na działce · stan v1.1",
                 p0, p1, [(*PR.uv(U0, vv), zz) for vv, zz in GROUND],
                 neighbours=[], beyond_names=("Mazowiecka 19",), notes=(), mode="eco", z_lo=-24.0, z_hi=46.0, pad=(40, 108, 24, 16))
P = svg.P
LINE = LineString([p0, p1])
u_t0, u_t1 = -V0, -V0 + 29.7          # wieża od v = 0 … 29,7  (u przekroju = v + 46)


def zg(su):
    """Rzędna terenu (wzgl. ±0,00) w punkcie przekroju su = v + 46."""
    vv = su + V0
    for (va, za), (vb, zb) in zip(GROUND, GROUND[1:]):
        if va <= vv <= vb:
            return (za + (zb - za) * (vv - va) / (vb - va)) - Z0
    return GROUND[-1][1] - Z0


def arrow(a, b, col, sw=0.5, dash=None, head=1.6):
    svg.line(a, b, stroke=col, sw=sw, dash=dash)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    l, r = ang + math.radians(150), ang - math.radians(150)
    svg.poly([b, (b[0] + head * math.cos(l), b[1] + head * math.sin(l)), (b[0] + head * math.cos(r), b[1] + head * math.sin(r))], fill=col, stroke="none")


def tag(xy, n, col):
    svg.circle(xy, 2.6, fill=col, stroke="#ffffff", sw=0.3)
    svg.text((xy[0], xy[1] + 0.95), str(n), size=2.6, anchor="middle", weight=700, fill="#ffffff")


def note(xy, t, col=INK, anchor="start", size=1.7, w=400):
    svg.text(xy, t, size=size, anchor=anchor, fill=col, weight=w, extra=halo_extra(0.6))


def cut(geom):
    """Przedziały przekroju (u przekroju) dla geometrii w układzie (e, n)."""
    return PR.intervals(geom, LINE, svg.U)


# ------------------------------------------------------------------ strop nad −1 w pasie dziedzińca (pod tarasem ogrodowym)
# Przekrój bazowy rysuje stropy tylko pod obrysem parteru z modelu pomieszczeń; w pasie −1 poza parterem (v −5,0 … lico parteru)
# brakowało stropu, na którym leży taras. Wierzch −0,15 wg koncepcja.json kondygnacje[−1].strop_nad; spód jak pod wieżą (−0,55),
# bo koncepcja.json nie podaje osobnej grubości dla pasa dziedzińca; na nim oczep ścian szczelinowych (Z_DW_TOP).
_SN = getattr(PR, "KOND", {}).get("-1", {}).get("strop_nad")
if _SN and getattr(PR, "UG_K", None) is not None:
    z_sn_top = float(_SN["wierzch"])
    z_sn_bot = float(_SN.get("spod_dziedziniec", _SN.get("spod_wieza", z_sn_top - 0.40)))
    _lvP = next((lv for lv in PR.BM["kondygnacje"] if lv["id"] == "P"), None)
    _parter = PR.mp(_lvP.get("plyta")) if _lvP else Polygon()
    for a, b in cut(PR.UG_K.difference(_parter)):
        if b - a > 0.3:
            svg.poly([P(a, z_sn_bot), P(b, z_sn_bot), P(b, z_sn_top), P(a, z_sn_top)], fill=PR.POCHE, stroke="none")


# ------------------------------------------------------------------ 1 słońce + BIPV dachów
sx, sy = P(8.0, 43.0)
svg.circle((sx, sy), 4.2, fill=SUN, stroke="none", extra='fill-opacity="0.9"')
for kk in range(12):
    a = math.radians(kk * 30)
    svg.line((sx + 5.2 * math.cos(a), sy + 5.2 * math.sin(a)), (sx + 7.2 * math.cos(a), sy + 7.2 * math.sin(a)), stroke=SUN, sw=0.4)
for t in (0.2, 0.5, 0.8):
    arrow((sx + 6, sy + 3), P(u_t0 + 29.7 * t, 36.6), SUN, sw=0.35, dash="1.4,0.9")
svg.poly([P(u_t0 + 0.6, 36.47), P(u_t1 - 0.6, 36.47), P(u_t1 - 0.6, 36.75), P(u_t0 + 0.6, 36.75)], fill="#2e3a48", stroke="none")
tag(P(u_t0 + 15, 39.6), 1, SUN)
# ------------------------------------------------------------------ 2 BIPV ≤ 25 m: płyciny wieży od dziedzińca + zadaszenie tarasu ogrodowego
tag(P(u_t0 - 3.2, 14.0), 2, SUN)
# zadaszenie BIPV (v −4,0…0 → u przekroju 42…46), h ≈ 4,0 m nad tarasem, wspornikowe z cięgnami do elewacji
z_ter = zg(u_t0 - 2.0)
zc0, zc1 = z_ter + 4.0, z_ter + 4.3
svg.poly([P(u_t0 - 4.0, zc0), P(u_t0, zc0), P(u_t0, zc1), P(u_t0 - 4.0, zc1)], fill="#2e3a48", stroke=INK, sw=0.12)
svg.line(P(u_t0 - 3.9, zc1), P(u_t0, zc1 + 2.4), stroke="#5b5651", sw=0.18)                       # cięgno
arrow((sx + 6, sy + 3), P(u_t0 - 2.0, zc1 + 0.15), SUN, sw=0.35, dash="1.4,0.9")
tag(P(u_t0 - 7.4, zc0 + 0.6), 2, SUN)
note((P(u_t0 - 4.2, zc0)[0], P(0, zc0 - 1.6)[1]), f"zadaszenie BIPV tarasu ogrodowego {EL['BIPV_zadaszenie_kWp']} kWp", anchor="end")
# taras ogrodowy na stropie pasa −1 (nawierzchnia, bez nasadzeń)
note((P(u_t0 - 2.5, 0)[0], P(0, z_ter + 0.5)[1]), "taras", anchor="middle", size=1.5)

# ------------------------------------------------------------------ 3 woda deszczowa: dach → zbiornik 50 m³ (−2, przy łuku – schematycznie)
for uu in (u_t0 + 5, u_t0 + 15, u_t0 + 25, 20.0, 30.0):
    zt = 44.5
    for q in range(3):
        a = P(uu - 1.0 + q * 1.0, zt - q * 0.8)
        svg.line(a, (a[0] - 0.8, a[1] + 2.4), stroke=RAIN, sw=0.3)
LV = {lv["id"]: lv for lv in PR.BM["kondygnacje"]}
# rzędne jak w przekroju bazowym (przekroje.py v1.1: koncepcja.json; starsza wersja: model pomieszczeń)
_ZK = getattr(PR, "Z_K", {})
z_m2 = float(_ZK.get("-2", LV["-2"]["rzedna"]))     # posadzka −2 (v1.1: −7,20)
z_m1 = float(_ZK.get("-1", LV["-1"]["rzedna"]))     # posadzka −1 (v1.1: −4,20)
t0_, t1_ = u_t0 + 0.9, u_t0 + 6.4
tz0, tz1 = z_m2 + 0.15, z_m1 - 0.75
svg.line(P(u_t0 + 1.0, 36.2), P(u_t0 + 1.0, tz1 + 0.05), stroke=RAIN, sw=0.45, dash="1.2,0.6")
svg.poly([P(t0_, tz0), P(t1_, tz0), P(t1_, tz1), P(t0_, tz1)], fill=RAIN, stroke=INK, sw=0.25, extra='fill-opacity="0.35"')
note(((P(t0_, 0)[0] + P(t1_, 0)[0]) / 2, P(0, (tz0 + tz1) / 2)[1] + 0.6), "zbiornik 50 m³", anchor="middle", size=1.6, w=600)
tag(P(u_t0 - 3.0, (tz0 + tz1) / 2), 3, RAIN)
# rezerwa 20 m³ opróżniana pompą do skrzynek rozsączających (pas pd. od segmentu) – kierunek schematyczny
arrow(P(t0_, tz0 + 0.6), P(u_t0 - 9.0, zg(u_t0 - 9.0) - 1.3), RAIN, sw=0.35, dash="0.9,0.6")
note((P(u_t0 - 9.4, 0)[0], P(0, zg(u_t0 - 9.0) - 2.6)[1]), "rezerwa 20 m³ pompą do skrzynek rozsączających (pas pd. od segmentu)",
     anchor="end", col=RAIN, size=1.6)

# ------------------------------------------------------------------ 4 ogród deszczowy – niecki w płaszczyźnie przekroju (obrys z PZT)
# obrys niecek jak RAIN w tools/zagospodarowanie.py (140 m²)
RAIN_POLYS = [[(87.14, 17.46), (87.26, 17.98), (87.71, 18.26), (89.6, 17.93), (91.16, 18.24), (92.2, 18.85), (93.18, 19.95), (94.38, 20.8),
                   (94.92, 20.86), (95.36, 20.49), (96.14, 0.63), (95.85, 0.04), (90.93, 0.01), (90.59, 0.28), (90.4, 2.12), (89.97, 3.81),
                   (91.56, 5.43), (92.48, 6.97), (92.93, 8.76), (92.84, 10.57), (92.22, 12.28), (91.13, 13.75), (89.67, 14.82), (87.47, 15.68)],
                  [(89.0, 32.75), (89.21, 31.47), (89.58, 30.57), (90.12, 29.98), (90.98, 29.52), (91.77, 29.4), (92.73, 29.59), (94.22, 30.68),
                   (94.94, 30.4), (95.29, 24.04), (94.98, 23.44), (94.21, 23.43), (93.18, 24.11), (92.2, 25.21), (91.16, 25.82), (89.99, 26.11),
                   (88.05, 26.03), (87.21, 27.13), (87.1, 28.24), (87.36, 29.73), (87.12, 31.2), (87.23, 32.54), (87.67, 32.96), (88.55, 32.99)]]
rain_iv = cut(unary_union([Polygon(r) for r in RAIN_POLYS]))
for a, b in rain_iv:
    if b - a < 0.8:
        continue
    d = min(0.6, (b - a) / 4)
    svg.poly([P(a, zg(a) + 0.02), P(a + d, zg(a + d) - 0.35), P(b - d, zg(b - d) - 0.35), P(b, zg(b) + 0.02)], fill=RAIN, stroke=RAIN, sw=0.2,
             extra='fill-opacity="0.45"')
if rain_iv:
    a, b = max(rain_iv, key=lambda ab: ab[1] - ab[0])
    tag(P((a + b) / 2, zg((a + b) / 2) + 3.6), 4, RAIN)
    note((P((a + b) / 2, 0)[0], P(0, zg((a + b) / 2) - 1.6)[1]), "ogród deszczowy", anchor="middle", col=RAIN, size=1.6)
    a2, b2 = min(rain_iv, key=lambda ab: abs((ab[0] + ab[1]) / 2 - (u_t0 - 14)))
    arrow(P(u_t0 - 4.4, zg(u_t0 - 4.4) + 0.25), P(b2 - 0.3, zg(b2) - 0.15), RAIN, sw=0.35, dash="0.9,0.6")   # spływ z tarasu do niecki

# ------------------------------------------------------------------ 5 GPC: sondy pod płytą −2, ściany szczelinowe i pale energetyczne
_PD = getattr(PR, "PD", None)
z_slab = float(_PD["spod"]) if _PD else z_m2 - 1.2    # spód płyty dennej (v1.1: −8,40 pod wieżą)
plate2 = (Polygon(K["podziemie"]["-2"]["obrys_ccw"]).buffer(0) if "-2" in K.get("podziemie", {}) else PR.mp(LV["-2"].get("plyta")))
D_PAL, L_PAL = getattr(PR, "D_PAL", 0.8), getattr(PR, "L_PAL", 14.0)
T_DW, H_DW, Z_DW_TOP = getattr(PR, "T_DW", 0.8), getattr(PR, "H_DW", 17.0), getattr(PR, "Z_DW_TOP", -1.0)
piles = []
for a, b in cut(PR.TOWER):
    x = a + 2.0
    while x < b - 1.5:
        piles.append(x)
        x += 4.05
holes = []
for a, b in cut(plate2):
    x = a + 2.0
    while x < b - 1.0:
        xx = x + (0.9 if any(abs(x - p_) < 0.7 for p_ in piles) else 0.0)
        holes.append(xx)
        x += 6.0
z_br = -24.0 + 2.2
for uu in holes:
    svg.line(P(uu, z_slab - 0.05), P(uu, z_br), stroke=HEAT, sw=0.35)
    svg.line(P(uu + 0.35, z_slab - 0.05), P(uu + 0.35, z_br), stroke=COOL, sw=0.35)
    xa, ya = P(uu - 0.5, z_br)
    xb, yb = P(uu + 0.85, z_br)
    svg.poly([(xa, ya), ((xa + xb) / 2 - 0.4, ya - 0.8), ((xa + xb) / 2 + 0.4, ya + 0.8), (xb, yb)], fill="none", stroke=INK, sw=0.18, close=False)
    svg.line(P(uu + 0.17, z_br - 0.6), P(uu + 0.17, -23.6), stroke="#8d877f", sw=0.2, dash="0.5,0.5")
if holes:
    note((P(holes[0] - 0.8, 0)[0], P(0, z_br - 1.4)[1]),
         "58 sond × 91 m pod płytą −2 (siatka 6 × 6 m) → dno 19,9 m n.p.m. (≤ 99,5 m p.p.t.)", anchor="end", size=1.7, w=600)
    tag(P((holes[len(holes) // 2] + holes[len(holes) // 2 - 1]) / 2 + 0.2 if len(holes) > 1 else holes[0] + 2, -14.0), 5, HEAT)
# pale energetyczne (36 × CFA Ø 0,8, L ≈ 14 m) – absorbery w palach rysowanych w przekroju bazowym
z_pb = max(z_slab - L_PAL, -24.0) + 0.4
for x in piles:
    svg.line(P(x + D_PAL * 0.3, z_slab - 0.4), P(x + D_PAL * 0.3, z_pb), stroke=HEAT, sw=0.18)
    svg.line(P(x + D_PAL * 0.7, z_slab - 0.4), P(x + D_PAL * 0.7, z_pb), stroke=COOL, sw=0.18)
# ściany szczelinowe energetyczne (0,60 m, 19 m) – absorbery w ścianach obwodowych podziemia
ug = getattr(PR, "UG_K", None) or unary_union([PR.mp(lv.get("plyta")) for lv in PR.BM["kondygnacje"] if lv["id"] in ("-1", "-2")])
walls = []
for a, b in cut(ug):
    walls += [a, b - T_DW]
z_wb = max(Z_DW_TOP - H_DW, -24.0) + 0.5
for x in walls:
    svg.line(P(x + T_DW * 0.3, Z_DW_TOP - 0.5), P(x + T_DW * 0.3, z_wb), stroke=HEAT, sw=0.18, dash="1.0,0.5")
    svg.line(P(x + T_DW * 0.7, Z_DW_TOP - 0.5), P(x + T_DW * 0.7, z_wb), stroke=COOL, sw=0.18, dash="1.0,0.5")
if walls:
    note((P(walls[0] - 0.6, 0)[0], P(0, -10.5)[1]), "ściana szczelinowa", anchor="end", col=HEAT, size=1.6)
    note((P(walls[0] - 0.6, 0)[0], P(0, -10.5)[1] + 2.2), "energetyczna (63 kW)", anchor="end", col=HEAT, size=1.6)
if piles:
    note((P(piles[-1] + 1.4, 0)[0], P(0, max(z_slab - L_PAL, -23.0) + 2.0)[1]), "pale energetyczne (20 kW)", anchor="start", col=HEAT, size=1.6)

# ------------------------------------------------------------------ 6 TABS w stropach
for zf in (8.55, 12.3, 16.05):
    a, b = P(u_t0 + 1.2, zf - 0.30), P(u_t1 - 1.2, zf - 0.30)
    pts = []
    n = 60
    for q in range(n + 1):
        x = a[0] + (b[0] - a[0]) * q / n
        pts.append((x, a[1] + 0.35 * math.sin(q * 1.3)))
    svg.poly(pts, fill="none", stroke=HEAT if zf < 12 else COOL, sw=0.3, close=False)
tag(P(u_t0 + 15, 10.4), 6, HEAT)
# ------------------------------------------------------------------ 7 wentylacja: czerpnia zbiorcza w płycinach P/1 i 1/2 elewacji pd. wieży, wyrzutnia w lamelach korony od pd.
z_in = 8.4
arrow(P(u_t0 - 7.0, z_in), P(u_t0 - 0.4, z_in), AIR, sw=0.7, head=2.0)
arrow(P(u_t0 - 0.4, 34.0), P(u_t0 - 7.0, 34.0), "#8d877f", sw=0.7, head=2.0)
svg.line(P(u_t0 + 3.0, z_in + 0.4), P(u_t0 + 3.0, 33.6), stroke=AIR, sw=0.3, dash="1.0,0.8")
tag(P(u_t0 - 9.8, z_in), 7, AIR)
tag(P(u_t0 - 9.8, 34.0), 7, "#8d877f")
# ------------------------------------------------------------------ 8 bioróżnorodność: budki dla jerzyków, drzewa
for zz in (9.6, 13.4, 17.2):
    svg.poly([P(u_t0 - 0.05, zz), P(u_t0 + 0.0, zz), P(u_t0 + 0.0, zz + 0.45), P(u_t0 - 0.05, zz + 0.45)], fill=INK, stroke="none")
    svg.poly([P(u_t0 - 0.45, zz), P(u_t0 - 0.05, zz), P(u_t0 - 0.05, zz + 0.45), P(u_t0 - 0.45, zz + 0.45)], fill="#6b5a46", stroke=INK, sw=0.12)
tag(P(u_t0 - 3.2, 19.6), 8, GREEN)
for uu, h, r in ((15.0, 12.0, 3.4), (33.0, 10.5, 3.0), (3.0, 13.0, 3.8)):
    PR.tree(svg, P, uu, zg(uu), h=h, r=r, op=0.55)
# ------------------------------------------------------------------ 9 osłony ZIP, ościeża
tag(P(u_t0 - 3.2, 26.4), 9, "#7a6a3a")

# ------------------------------------------------------------------ legenda (prawa kolumna)
KWP_W = round(EL["pola"]["dach_wiezy_m2"] * EL["gestosc_dach_kWp_m2"])       # 204
KWP_M = round(EL["pola"]["dach_skrzydla_m2"] * EL["gestosc_dach_kWp_m2"])    # 147
KWP_PLYC, KWP_SCIANA = 11, 41      # płyciny wieży 82 m² × 0,13; ściana pd. segmentu 295 m² (rozdz. 10, E-K-2)
if KWP_PLYC + KWP_SCIANA != EL["BIPV_elewacje_kWp"] or KWP_W + KWP_M != EL["BIPV_dach_kWp"]:
    print("UWAGA: rozbicie PV ≠ koncepcja.json elewacje.PV", KWP_W, KWP_M, KWP_PLYC, KWP_SCIANA, EL)
# PV/EPB 111 %, PV/całość 51 % – rozdz. 10 (zużycie EPB ≈ 297 MWh/rok, całkowite ≈ 645 MWh/rok; _bilans_energii.py)
f1 = lambda x: f"{x:.1f}".replace(".", ",")
x0 = svg.w_mm - 104
y = 30
items = [
    (1, SUN, f"BIPV jako pokrycie dachów (bez stelaży): wieża {KWP_W} kWp, skrzydło {KWP_M} kWp = {EL['BIPV_dach_kWp']} kWp"),
    (None, None, f"({str(EL['gestosc_dach_kWp_m2']).replace('.', ',')} kWp/m², moduły η ≥ 22,5 %); falowniki i rozdzielnice DC – kond. 2 segmentu"),
    (2, SUN, f"BIPV ≤ 25 m od dziedzińca i dz. 10/2: płyciny wieży {KWP_PLYC} kWp, ściana pd. segmentu {KWP_SCIANA} kWp,"),
    (None, None, f"zadaszenie tarasu ogrodowego {EL['BIPV_zadaszenie_kWp']} kWp ({EL['pola']['zadaszenie_tarasu_ogrodowego_m2']} m², w przekroju); od ulic – brak"),
    (None, None, f"razem {EL['razem_kWp']} kWp · {EL['MWh_rok']} MWh/rok = 111 % energii EPB (51 % całości) · magazyn energii 150 kWh"),
    (3, RAIN, f"retencja {Z['retencja_m3']} m³ = 2,2 × V60 ({Z['V60_C10_m3']} m³): skrzynki rozsączające 66 + rezerwa zbiornika 20"),
    (None, None, "+ ogród deszczowy 42 + dach niebieski 10 + podbudowa 19 – zero odpływu (przy k ≥ 1·10⁻⁶ m/s);"),
    (None, None, "zbiornik deszczówki 50 m³ na −2 przy łuku (schemat.); woda szara 804 + deszczowa 848 m³/rok"),
    (None, None, "→ ≈ 100 % spłukiwania, −47 % wody wodociągowej (1 600 m³/rok)"),
    (4, RAIN, "ogród deszczowy 140 m² (niecki w przekroju), nawierzchnie przepuszczalne, taras zielony 135 m²"),
    (5, HEAT, "GPC: 58 sond × 91 m pod płytą −2 (238 kW) + ściany szczelinowe energetyczne (63 kW)"),
    (None, None, "+ 36 pali energetycznych (20 kW) = 321 kW → 430 kW grzania / 330 kW chłodu + free cooling;"),
    (None, None, "szczyt chłodu ≈ 600 kW: + dry-cooler hybrydowy 2 × 150 kW (kond. 4 segmentu) + TABS;"),
    (None, None, "sieć ciepłownicza tylko rezerwą/szczytem (≈ 0,3 MW); odzysk ciepła do c.w.u."),
    (6, HEAT, "stropy aktywowane termicznie (TABS) — niskotemperaturowe grzanie i chłodzenie"),
    (7, AIR, "czerpnia zbiorcza w płycinach elewacji pd. wieży (P/1, 1/2; 17 m²), wyrzutnia w lamelach korony"),
    (None, None, "od pd.; nic na dachu i na elewacjach od ulic; 5 central piętrowych, rekuperacja ≥ 80 %, CO₂"),
    (8, GREEN, "24 budki dla jerzyków, pnącza przy ścianie segmentu, nadruk ochronny na szkle korony;"),
    (None, None, f"drzewa M.06: {Z['zachowane_numery']} z {Z['drzewa_w_OI_numery']} zachowanych ({Z['zachowane_po_usunieciach_sanitarnych']} po usunięciach sanitarnych U)"
     f" + {Z['nowe_nasadzenia']} nowych"),
    (9, "#7a6a3a", "osłony ZIP (E, S, W), ościeża 0,45 m, WWR 37–40 %, A/V 0,18; U ściany 0,144–0,147, dachu ≤ 0,12"),
]
svg.text((x0, y - 6), "ROZWIĄZANIA", size=3.0, weight=600)
for n, col, t in items:
    if n:
        svg.circle((x0 + 2.2, y - 0.8), 2.0, fill=col, stroke="none")
        svg.text((x0 + 2.2, y), str(n), size=2.2, anchor="middle", weight=700, fill="#ffffff")
    svg.text((x0 + 6.0, y), t, size=1.9, fill=INK)
    y += 3.3
y += 5
svg.text((x0, y), "WSKAŹNIKI", size=3.0, weight=600); y += 5
for big, small in ((f"EP ≈ {BIL['EP_kWh_m2']:.0f} kWh/(m²·rok)", f"bez PV 60; zużycie EPB {f1(BIL['EPB_kWh_m2'])} kWh/(m²·rok); próg ZEB 85, EPmax 95"),
                   ("6,7 kg CO₂/(m²·rok)", "emisje operacyjne EPB (próg ZEB 31,4)"),
                   (f"PV {EL['razem_kWp']} kWp · {EL['MWh_rok']} MWh/rok", "111 % EPB, 51 % całości; resztę daje społeczność energetyczna OZE Województwa"),
                   ("GWP ≤ 500 kg CO₂e/m²", "cel A1–A5 (szacunek ≈ 490 ± 120): CEM III/B, stropy sprężone, granit ≈ 60 km, Al ≥ 75 % z recyklingu"),
                   ("BREEAM Excellent", "cel certyfikacji; budynek bezemisyjny wg EPBD 2024/1275 od 2028 r.")):
    svg.text((x0, y), big, size=3.2, weight=700, fill="#a8483a")
    svg.text((x0, y + 3.3), small, size=1.85, fill="#4d4842")
    y += 9.0

out = PR.ROOT / "build" / "rysunki" / f"schemat_eko_1-{PR.SCALE}.svg"
out.write_text(svg.render(), encoding="utf-8")
html = PR.ROOT / "docs" / "70_rysunki" / "podglady" / "schemat_eko.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm + 10:.0f}mm {svg.h_mm + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{svg.w_mm + 10:.0f} {svg.h_mm + 10:.0f}")
