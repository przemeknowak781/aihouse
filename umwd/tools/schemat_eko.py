#!/usr/bin/env python3
"""Schemat proekologiczny na przekroju przez Ogród Województwa i wieżę (oś u = 10 m, widok na zachód).
Liczby z koncepcja_wybrana.md rozdz. 10 (bilans energii) i koncepcja.json (retencja, PV, drzewa).
Wynik: build/rysunki/schemat_eko.svg + docs/70_rysunki/podglady/schemat_eko.png
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
import przekroje as PR

K = PR.K
Z = K["zagospodarowanie"]
EL = K["elewacje"]["PV"]
SUN, RAIN, HEAT, COOL, AIR, GREEN, INK = "#d99a2b", "#3f74a0", "#c0392b", "#2f6f9f", "#5e8f6b", "#5f8050", "#1f1d1a"

U0 = 10.0
p0, p1 = PR.uv(U0, -46.0), PR.uv(U0, 40.0)
svg = PR.section("ECO", "SCHEMAT PROEKOLOGICZNY", "przekrój przez Ogród Województwa i wieżę (u = 10 m) · budynek bezemisyjny bez spalania na działce",
                 p0, p1, [(p0[0], p0[1], 118.6), (*PR.uv(U0, -30), 118.75), (*PR.uv(U0, -8), 118.95), (*PR.uv(U0, 0), 119.0), (*PR.uv(U0, 31), 119.4), (p1[0], p1[1], 119.45)],
                 neighbours=[], beyond_names=("Mazowiecka 19",), notes=(), mode="eco", z_lo=-24.0, z_hi=46.0, pad=(40, 96, 24, 16))
P = svg.P
u_t0, u_t1 = 46.0, 46.0 + 29.7          # tower from v=0 … 29.7  (u = v + 46)


def arrow(a, b, col, sw=0.5, dash=None, head=1.6):
    svg.line(a, b, stroke=col, sw=sw, dash=dash)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    l, r = ang + math.radians(150), ang - math.radians(150)
    svg.poly([b, (b[0] + head * math.cos(l), b[1] + head * math.sin(l)), (b[0] + head * math.cos(r), b[1] + head * math.sin(r))], fill=col, stroke="none")


def tag(xy, n, col):
    svg.circle(xy, 2.6, fill=col, stroke="#ffffff", sw=0.3)
    svg.text((xy[0], xy[1] + 0.95), str(n), size=2.6, anchor="middle", weight=700, fill="#ffffff")


# 1 sun + PV roof
sx, sy = P(8.0, 43.0)
svg.circle((sx, sy), 4.2, fill=SUN, stroke="none", extra='fill-opacity="0.9"')
for k in range(12):
    a = math.radians(k * 30)
    svg.line((sx + 5.2 * math.cos(a), sy + 5.2 * math.sin(a)), (sx + 7.2 * math.cos(a), sy + 7.2 * math.sin(a)), stroke=SUN, sw=0.4)
for t in (0.2, 0.5, 0.8):
    arrow((sx + 6, sy + 3), P(u_t0 + 29.7 * t, 36.6), SUN, sw=0.35, dash="1.4,0.9")
svg.poly([P(u_t0 + 0.6, 36.47), P(u_t1 - 0.6, 36.47), P(u_t1 - 0.6, 36.75), P(u_t0 + 0.6, 36.75)], fill="#2e3a48", stroke="none")
tag(P(u_t0 + 15, 39.6), 1, SUN)
# 2 PV on courtyard façade ≤ 25 m (dark panels) – marker on tower south face
tag(P(u_t0 - 3.2, 14.0), 2, SUN)
# 3 rain → retention tank under the courtyard strip (−1, v 0…−5 → u 41…46)
for uu in (u_t0 + 5, u_t0 + 15, u_t0 + 25, 20.0, 30.0):
    zt = 44.5
    for q in range(3):
        a = P(uu - 1.0 + q * 1.0, zt - q * 0.8)
        svg.line(a, (a[0] - 0.8, a[1] + 2.4), stroke=RAIN, sw=0.3)
svg.line(P(u_t0 + 1.0, 36.2), P(u_t0 + 1.0, -1.2), stroke=RAIN, sw=0.45, dash="1.2,0.6")
tank = [P(41.6, -3.5), P(45.3, -3.5), P(45.3, -1.2), P(41.6, -1.2)]
svg.poly(tank, fill=RAIN, stroke=INK, sw=0.25, extra='fill-opacity="0.35"')
arrow(P(u_t0 + 1.0, -0.4), P(45.0, -1.4), RAIN, sw=0.45)
tag(P(43.4, -6.0), 3, RAIN)
# 4 rain garden (depression in the garden)
svg.poly([P(22.0, -0.05), P(23.2, -0.55), P(28.8, -0.55), P(30.0, -0.05)], fill=RAIN, stroke=RAIN, sw=0.2, extra='fill-opacity="0.45"')
arrow(P(41.4, -2.0), P(29.5, -0.6), RAIN, sw=0.35, dash="0.9,0.6")
tag(P(26.0, 3.6), 4, RAIN)
# 5 ground-source heat pumps: 75 boreholes × 99 m
for uu in (6.0, 10.0, 14.0, 18.0, 32.0, 36.0):
    svg.line(P(uu, -0.4), P(uu, -23.6), stroke=HEAT, sw=0.35)
    svg.line(P(uu + 0.35, -0.4), P(uu + 0.35, -23.6), stroke=COOL, sw=0.35)
    arrow(P(uu + 0.17, -21.5), P(uu + 0.17, -23.9), INK, sw=0.15, head=0.9)
tag(P(12.0, -12.0), 5, HEAT)
# 6 TABS in slabs
for zf in (8.55, 12.3, 16.05):
    a, b = P(u_t0 + 1.2, zf - 0.30), P(u_t1 - 1.2, zf - 0.30)
    pts = []
    n = 60
    for q in range(n + 1):
        x = a[0] + (b[0] - a[0]) * q / n
        pts.append((x, a[1] + 0.35 * math.sin(q * 1.3)))
    svg.poly(pts, fill="none", stroke=HEAT if zf < 12 else COOL, sw=0.3, close=False)
tag(P(u_t0 + 15, 10.4), 6, HEAT)
# 7 ventilation: intake courtyard façade floor 1, exhaust crown south face (≈ 29 m higher)
arrow(P(u_t0 - 7.0, 6.6), P(u_t0 - 0.4, 6.6), AIR, sw=0.7, head=2.0)
arrow(P(u_t0 - 0.4, 34.0), P(u_t0 - 7.0, 34.0), "#8d877f", sw=0.7, head=2.0)
svg.line(P(u_t0 + 3.0, 7.0), P(u_t0 + 3.0, 33.6), stroke=AIR, sw=0.3, dash="1.0,0.8")
tag(P(u_t0 - 9.8, 6.6), 7, AIR)
tag(P(u_t0 - 9.8, 34.0), 7, "#8d877f")
# 8 biodiversity: swift boxes on the courtyard façade, trees, climbers
for zz in (9.6, 13.4, 17.2):
    svg.poly([P(u_t0 - 0.05, zz), P(u_t0 + 0.0, zz), P(u_t0 + 0.0, zz + 0.45), P(u_t0 - 0.05, zz + 0.45)], fill=INK, stroke="none")
    svg.poly([P(u_t0 - 0.45, zz), P(u_t0 - 0.05, zz), P(u_t0 - 0.05, zz + 0.45), P(u_t0 - 0.45, zz + 0.45)], fill="#6b5a46", stroke=INK, sw=0.12)
tag(P(u_t0 - 3.2, 19.6), 8, GREEN)
for uu, h, r in ((15.0, 12.0, 3.4), (33.0, 10.5, 3.0), (3.0, 13.0, 3.8)):
    PR.tree(svg, P, uu, -0.05, h=h, r=r, op=0.55)
# 9 night cooling / daylight / solar shading – ZIP on S façade
tag(P(u_t0 - 3.2, 26.4), 9, "#7a6a3a")

# ------------------------------------------------------------------ legend (right column)
x0 = svg.w_mm - 92
y = 30
n_kept = Z.get("zachowane_numery", 0)
items = [
    (1, SUN, "BIPV jako pokrycie dachów (bez stelaży): wieża 208 kWp, skrzydło 156 kWp"),
    (None, None, f"razem z elewacją {EL['razem_kWp']} kWp · 347 MWh/rok = 117 % energii EPB · magazyn 250 kWh"),
    (2, SUN, "BIPV w płycinach elewacji od dziedzińca ≤ 25 m: 48 kWp (od ulic — brak)"),
    (3, RAIN, f"retencja {Z['retencja_m3']} m³ pod dziedzińcem: zero odpływu deszczu miarodajnego;"),
    (None, None, "woda deszczowa + szara pokrywa 100 % spłukiwania (−47 % wody wodociągowej)"),
    (4, RAIN, "ogród deszczowy 140 m², nawierzchnie przepuszczalne 430 m², taras zielony segmentu"),
    (5, HEAT, "gruntowe pompy ciepła: 75 sond × 99 m, 430 kW ciepła / 330 kW chłodu + free cooling;"),
    (None, None, "ciepłownia miejska tylko rezerwą, odzysk ciepła z serwerowni do c.w.u."),
    (6, HEAT, "stropy aktywowane termicznie (TABS) — niskotemperaturowe grzanie i chłodzenie"),
    (7, AIR, "czerpnia w płycinach od ogrodu (kond. 1), wyrzutnia w koronie od pd.: nic na dachu"),
    (None, None, "i na elewacjach ulicznych; 5 central piętrowych, rekuperacja ≥ 80 %, sterowanie CO₂"),
    (8, GREEN, f"24 budki dla jerzyków, pnącza na ścianie segmentu, nadruk ochronny na szkle korony;"),
    (None, None, "zachowane drzewa ogródków (bilans wg M.06) + 18 nowych; ogród otwarty dla mieszkańców"),
    (9, "#7a6a3a", "osłony ZIP (E, S, W), ościeża 0,60 m, WWR 38–40 %, A/V 0,18; U ściany ≤ 0,15, dachu ≤ 0,12"),
]
svg.text((x0, y - 6), "ROZWIĄZANIA", size=3.0, weight=600)
for n, col, t in items:
    if n:
        svg.circle((x0 + 2.2, y - 0.8), 2.0, fill=col, stroke="none")
        svg.text((x0 + 2.2, y), str(n), size=2.2, anchor="middle", weight=700, fill="#ffffff")
    svg.text((x0 + 6.0, y), t, size=1.9, fill=INK)
    y += 3.6 if n is None else 3.4
y += 5
svg.text((x0, y), "WSKAŹNIKI", size=3.0, weight=600); y += 5
for big, small in (("EP ≈ 26 kWh/(m²·rok)", "bez PV 60; próg ZEB 85, EPmax 95"), ("6,3 kg CO₂/(m²·rok)", "emisje operacyjne EPB (próg ZEB 31,4)"),
                   ("GWP ≤ 500 kg CO₂e/m²", "A1–A5: CEM III, stropy sprężone, granit ≈ 60 km, Al ≥ 75 % z recyklingu, gruz z wykopu w podbudowach"),
                   ("BREEAM Excellent", "cel certyfikacji; budynek bezemisyjny wg EPBD 2024/1275 od 2028 r.")):
    svg.text((x0, y), big, size=3.2, weight=700, fill="#a8483a")
    svg.text((x0, y + 3.3), small, size=1.85, fill="#4d4842")
    y += 9.0

out = PR.ROOT / "build" / "rysunki" / "schemat_eko.svg"
out.write_text(svg.render(), encoding="utf-8")
html = PR.ROOT / "docs" / "70_rysunki" / "podglady" / "schemat_eko.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{svg.w_mm + 10:.0f}mm {svg.h_mm + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{svg.w_mm + 10:.0f} {svg.h_mm + 10:.0f}")
