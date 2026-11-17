#!/usr/bin/env python3
"""Przekrój elewacyjny 1:50 z fragmentem elewacji (Etap II): korona wieży od strony Placu Mostowego (elewacja pn., hol
reprezentacyjny Sejmiku), z +19,30 do +37,60: kondygnacja 5 z kordonem kwartału, kondygnacja cienia (6), korona S
z oknem 1,65 × 5,00, kratownica dachu, dach BIPV, attyka. Warstwy wg koncepcji (rozdz. 8, tabela przegród).

Wynik: build/rysunki/przekroj_elewacyjny_1-50.svg + docs/70_rysunki/podglady/przekroj_elewacyjny_1-50.png
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.svg import Svg

INK = "#1f1d1a"
SC = 20.0                         # 1:50 → 20 mm per metre
ZB, ZT = 19.10, 37.70
GRAN, GRAN_H = "#ddd8cf", "#b9b2a6"
INS = "#f1e9cf"
MET = "#4a4541"
GLASS = "#4a6a85"
CONC = "#e4e2de"

W_MM, H_MM = 480.0, 18.6 * SC + 60
svg = Svg(W_MM, H_MM)
OX, OY = 178.0, 30.0 + (ZT - ZB) * SC        # section: façade plane X=0 at paper x=OX


def P(X, Z):
    return (OX + X * SC, OY - (Z - ZB) * SC)


def rect(x0, z0, x1, z1, fill="none", stroke=INK, sw=0.18, extra=""):
    svg.poly([P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)


hc = svg.hatch("beton", spacing=0.9, angle=45, stroke="#9c978f", sw=0.08, bg=CONC)
hg = svg.hatch("granit", spacing=0.6, angle=-30, stroke=GRAN_H, sw=0.08, bg=GRAN)
hi = svg.hatch("welna", spacing=0.7, angle=90, stroke="#d9cfa9", sw=0.1, bg=INS)

X_IN = -4.6        # interior break line
callouts = []


def call(n, X, Z, dx=0.0):
    callouts.append((n, X, Z, dx))


# ------------------------------------------------------------------ storeys
F5, F6, FS = 19.80, 23.55, 27.30
SLAB, FLOOR = 0.28, 0.15
for zf in (F5, F6, FS):
    st, sb = zf - FLOOR, zf - FLOOR - SLAB
    rect(X_IN, sb, -0.243, st, fill=hc, sw=0.25)                        # strop sprężony 280 (TABS)
    rect(X_IN, st, -0.70, zf, fill="#ffffff", sw=0.12)                  # podłoga podniesiona 150
    for q in range(1, 12):
        x = X_IN + q * 0.35
        if x < -0.75:
            svg.line(P(x, st), P(x, zf - 0.03), stroke="#8a857e", sw=0.08)
    # TABS pipes
    for q in range(1, 22):
        x = X_IN + q * 0.18
        if x < -0.4:
            svg.circle(P(x, sb + 0.07), 0.35, fill="none", stroke="#a8483a", sw=0.08)
call(7, -2.4, F6 - 0.3)
call(8, -3.6, F6 - 0.07)

# ------------------------------------------------------------------ storey 5 (kordon) and 6 (shadow storey) façade
def spandrel_flush(z0, z1, cladding="metal"):
    """flush spandrel: cladding X 0..-0.04 / cavity / wool 200 / RC upstand 200."""
    if cladding == "granite":
        rect(-0.04, z0, 0.0, z1, fill=hg, sw=0.2)
    else:
        rect(-0.006, z0, 0.0, z1, fill=MET, stroke=MET, sw=0.1)
    rect(-0.28, z0, -0.08, z1, fill=hi, sw=0.12)


# floor 5: below sill kordon granite (flush) 19.80–20.85; RC upstand behind
rect(-0.48, F5 - FLOOR, -0.28, F5 + 1.05, fill=hc, sw=0.2)
spandrel_flush(F5 - FLOOR - SLAB - 0.80, F5 + 1.05, "granite")      # kordon extends over slab edge (EI 60 belt)
call(9, 0.0, F5 + 0.55, 0.6)
# window floor 5: frame at X = -0.60 … -0.70, sill +1.05, head +3.32
def window(zs, zh, x_out=-0.60, transom=None, zip_box=True, fixed_to=None):
    rect(x_out - 0.10, zs, x_out, zs + 0.08, fill=MET, stroke=MET)          # bottom frame
    rect(x_out - 0.10, zh - 0.08, x_out, zh, fill=MET, stroke=MET)          # head frame
    for k, dx in enumerate((-0.025, -0.05, -0.075)):
        svg.line(P(x_out + dx, zs + 0.08), P(x_out + dx, zh - 0.08), stroke=GLASS, sw=0.22)
    if transom:
        rect(x_out - 0.10, zs + transom - 0.04, x_out, zs + transom + 0.04, fill=MET, stroke=MET)
    if fixed_to:
        rect(x_out - 0.10, fixed_to - 0.04, x_out, fixed_to + 0.04, fill=MET, stroke=MET)
    # external sill (Al, sloped) and internal board
    svg.poly([P(0.04, zs - 0.03), P(x_out, zs + 0.02), P(x_out, zs - 0.02), P(0.04, zs - 0.07)], fill=MET, stroke=MET, sw=0.1)
    rect(x_out - 0.30, zs, x_out - 0.10, zs + 0.03, fill="#cfc8bc", sw=0.08)
    if zip_box:
        rect(x_out + 0.02, zh - 0.18, x_out + 0.18, zh, fill="#6b645e", stroke=INK, sw=0.1)
    # reveal soffit lining (granite on piers' return)
    rect(x_out, zh, 0.0, zh + 0.04, fill=hg, sw=0.12)


window(F5 + 1.05, F5 + 3.32)              # rama dolna 0,08 → szkło od +1,13 (≥ 1,10)
call(5, -0.65, F5 + 2.3, -1.6)
call(6, -0.40, F6 + 1.10, -1.8)
# head spandrel floor5→6: flush metal panel 23.12 … 23.55 + floor 6 is recessed: band 23.55–27.30 at X=-0.40
spandrel_flush(F5 + 3.32, F6 - FLOOR, "metal")
rect(-0.48, F6 - FLOOR - SLAB, -0.28, F6 - FLOOR, fill=hc, sw=0.15)
call(4, 0.0, F5 + 3.6, 0.6)
call(15, -0.15, F6 - 0.5, 0.6)
# floor 6 recessed (0.40 behind pier face): metal spandrel + glass
rect(-0.406, F6 - FLOOR, -0.40, F6 + 0.87, fill=MET, stroke=MET, sw=0.1)
rect(-0.68, F6 - FLOOR, -0.48, F6 + 0.87, fill=hi, sw=0.12)
rect(-0.88, F6, -0.68, F6 + 0.87, fill=hc, sw=0.15)
window(F6 + 0.87, F6 + 3.32, x_out=-0.40, fixed_to=F6 + 1.10, zip_box=True)
call(10, -0.40, F6 + 2.0, 1.0)
# soffit of the recess under floor S slab (granite lined) and S floor slab edge
spandrel_flush(F6 + 3.32, FS + 0.70, "granite")
rect(-0.48, FS - FLOOR, -0.28, FS + 0.70, fill=hc, sw=0.2)
rect(-0.40, F6 + 3.32, 0.0, F6 + 3.36, fill=hg, sw=0.1)

# ------------------------------------------------------------------ crown S: hall window 1.65 × 5.00, transom at +30.50
window(FS + 0.70, FS + 5.70, transom=2.5, zip_box=False)
call(11, -0.65, FS + 4.0, -1.6)
# above window: granite spandrel to the roof + attic
ZR_DECK = 35.80
spandrel_flush(FS + 5.70, 36.20, "granite")
rect(-0.48, FS + 5.70, -0.28, 36.20, fill=hc, sw=0.2)                       # RC ring beam / upstand
call(1, 0.0, 34.6, 0.6)
call(2, -0.18, 33.6, 0.6)
call(3, -0.38, 34.0, 0.6)
# steel truss 1.60 m (34.20–35.80) and acoustic ceiling at 34.15
zt0, zt1 = 34.20, 35.80
svg.line(P(X_IN, zt1 - 0.1), P(-0.5, zt1 - 0.1), stroke=INK, sw=0.5)
svg.line(P(X_IN, zt0 + 0.1), P(-0.5, zt0 + 0.1), stroke=INK, sw=0.5)
x = X_IN
while x < -0.6:
    svg.line(P(x, zt0 + 0.1), P(min(-0.5, x + 0.8), zt1 - 0.1), stroke=INK, sw=0.25)
    svg.line(P(min(-0.5, x + 0.8), zt1 - 0.1), P(min(-0.5, x + 1.6), zt0 + 0.1), stroke=INK, sw=0.25)
    x += 1.6
rect(X_IN, 34.10, -0.70, 34.15, fill="#bdb6ab", sw=0.08)
call(12, -2.6, 35.0)
# roof build-up: composite deck 35.80–35.95, vapour barrier, tapered wool (0.25 → 0.50), membrane, BIPV glass-glass 36.20–36.45
rect(X_IN, ZR_DECK, -0.48, ZR_DECK + 0.15, fill=hc, sw=0.2)
svg.poly([P(X_IN, 36.40 - 0.03), P(-0.48, 36.15), P(-0.48, ZR_DECK + 0.15), P(X_IN, ZR_DECK + 0.15)], fill=hi, stroke=INK, sw=0.15)
svg.poly([P(X_IN, 36.40), P(-0.48, 36.18), P(-0.48, 36.15), P(X_IN, 36.37)], fill=INK, stroke="none")
for q in range(6):
    xa = X_IN + q * 0.7
    if xa < -0.9:
        za = 36.40 - (xa - X_IN) / (-0.48 - X_IN) * 0.22
        svg.poly([P(xa, za + 0.02), P(xa + 0.62, za + 0.02 - 0.62 / 4.1 * 0.22), P(xa + 0.62, za + 0.07 - 0.62 / 4.1 * 0.22), P(xa, za + 0.07)], fill="#2e3a48", stroke=INK, sw=0.08)
call(13, -2.0, 36.35)
# attic: RC upstand, insulation, granite outside, granite cap + Al flashing (0.15)
rect(-0.48, 36.15, -0.28, 37.05, fill=hc, sw=0.2)
rect(-0.28, 36.20, -0.08, 37.05, fill=hi, sw=0.12)
rect(-0.04, 36.20, 0.0, 37.05, fill=hg, sw=0.2)
svg.poly([P(0.05, 37.05), P(-0.62, 37.05), P(-0.62, 37.12), P(0.05, 37.20)], fill=hg, stroke=INK, sw=0.2)
svg.poly([P(0.08, 37.20), P(-0.64, 37.13), P(-0.64, 37.15), P(0.08, 37.22)], fill=MET, stroke=MET, sw=0.1)
call(14, -0.3, 37.25, 0.8)
# view beyond: pier side face (X 0 … -0.60) between window zones
for (z0, z1) in ((F5 + 1.05, F5 + 3.32), (F6 + 0.87, F6 + 3.32), (FS + 0.70, FS + 5.70)):
    svg.line(P(0.0, z0), P(0.0, z1), stroke="#8a857e", sw=0.12)
# break lines
for zz in (ZB + 0.05,):
    svg.line(P(X_IN - 0.1, zz), P(0.4, zz), stroke=INK, sw=0.15, dash="1.5,0.8")
svg.line(P(X_IN, ZB), P(X_IN, ZT - 0.2), stroke=INK, sw=0.15, dash="1.5,0.8")

# ------------------------------------------------------------------ level marks
for z, lab in ((37.20, "+37,20 attyka = 156,50"), (36.45, "+36,45 najwyższy pkt pokrycia"), (36.20, "+36,20 najniższy pkt pokrycia (MPZP ≥ 35,0 m)"),
               (34.15, "+34,15 sufit holu (6,85 m)"), (FS, "+27,30 posadzka S"), (F6, "+23,55 posadzka 6"), (20.85, "+20,85 kordon = gzyms skrzydła"), (F5, "+19,80 posadzka 5")):
    x, y = P(X_IN - 0.4, z)
    svg.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
    svg.line((x - 2.5, y), (x + 4, y), stroke=INK, sw=0.12)
    svg.text((x - 3, y - 0.4), lab, size=2.1, anchor="end")

# ------------------------------------------------------------------ callout bubbles
for n, X, Z, dx in callouts:
    x, y = P(X, Z)
    bx = x + dx * SC
    if dx:
        svg.line((x, y), (bx, y), stroke=INK, sw=0.12)
    svg.circle((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y), 2.2, fill="#ffffff", stroke="#a8483a", sw=0.25)
    svg.text((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y + 0.8), str(n), size=2.2, anchor="middle", weight=700, fill="#a8483a")

# ------------------------------------------------------------------ elevation fragment (2 bays) to the right
EX0 = 2.9      # paper offset (m at 1:50) from section façade plane
def E(u, z):
    return (OX + (EX0 + u) * SC, OY - (z - ZB) * SC)


def erect(u0, z0, u1, z1, fill, stroke=INK, sw=0.15, extra=""):
    svg.poly([E(u0, z0), E(u1, z0), E(u1, z1), E(u0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)


piers = [(0.0, 0.525), (2.175, 3.225), (4.875, 5.4)]
bays = [(0.525, 2.175), (3.225, 4.875)]
erect(0, ZB, 5.4, 36.20, MET, stroke="none")
for a, b in bays:
    # floor 5
    erect(a, F5 - 0.80, b, F5 + 1.05, hg)
    erect(a, F5 + 1.05, b, F5 + 3.32, "#7b8792", sw=0.12)
    svg.line(E((a + b) / 2, F5 + 1.05), E((a + b) / 2, F5 + 3.32), stroke=MET, sw=0.35)
    erect(a, F5 + 1.06, b, F5 + 1.14, MET, stroke="none")
    erect(a, F5 + 3.10, b, F5 + 3.32, "#1f1d1a", stroke="none", extra='fill-opacity="0.35"')
    # floor 6 (recessed, darker)
    erect(a, F6 - 0.43, b, FS - 0.43, "#2e2b29", stroke="none")
    erect(a + 0.05, F6 + 0.87, b - 0.05, F6 + 3.32, "#3d434a", stroke="#5d646b", sw=0.1)
    svg.line(E((a + b) / 2, F6 + 0.87), E((a + b) / 2, F6 + 3.32), stroke=MET, sw=0.3)
    erect(a, FS - 0.80, b, FS - 0.43, "#1f1d1a", stroke="none", extra='fill-opacity="0.5"')
    # crown hall window
    erect(a, FS - 0.43, b, FS + 0.70, hg)
    erect(a, FS + 0.70, b, FS + 5.70, "#7b8792", sw=0.12)
    erect(a, FS + 3.16, b, FS + 3.24, MET, stroke="none")
    svg.line(E((a + b) / 2, FS + 0.70), E((a + b) / 2, FS + 5.70), stroke=MET, sw=0.35)
    erect(a, FS + 5.30, b, FS + 5.70, "#1f1d1a", stroke="none", extra='fill-opacity="0.35"')
    erect(a, FS + 5.70, b, 36.20, hg)
    # bird-safe dot pattern on crown glass (light)
    for qz in range(12):
        for qu in range(7):
            svg.circle(E(a + 0.12 + qu * 0.24, FS + 0.9 + qz * 0.38), 0.18, fill="#ffffff", stroke="none", extra='fill-opacity="0.35"')
for a, b in piers:
    erect(a, ZB, b, 36.20, hg, sw=0.2)
    zj = ZB + 0.6
    while zj < 36.2:
        svg.line(E(a, zj), E(b, zj), stroke=GRAN_H, sw=0.1)
        zj += 1.25
    svg.line(E(b, ZB), E(b, 36.2), stroke=INK, sw=0.1)
    erect(b, ZB, min(5.4, b + 0.12), 36.2, "#1f1d1a", stroke="none", extra='fill-opacity="0.12"')
erect(0, 36.20, 5.4, 37.05, hg, sw=0.2)
erect(-0.05, 37.05, 5.45, 37.20, MET, stroke=MET, sw=0.1)
svg.text((E(2.7, 0)[0], E(0, ZT)[1] - 2), "FRAGMENT ELEWACJI PÓŁNOCNEJ (2 przęsła)", size=2.6, anchor="middle", weight=600)
svg.text((P(-2.3, 0)[0], P(0, ZT)[1] - 2), "PRZEKRÓJ PRZEZ OŚ OKNA", size=2.6, anchor="middle", weight=600)
# dimensions (bottom of elevation)
yd = E(0, ZB)[1] + 7
for u0, u1, t in ((0.525, 2.175, "1,65"), (2.175, 3.225, "1,05"), (3.225, 4.875, "1,65"), (0.0, 0.525, ""), (4.875, 5.4, "")):
    x0, x1 = E(u0, 0)[0], E(u1, 0)[0]
    svg.line((x0, yd), (x1, yd), stroke=INK, sw=0.12)
    for x in (x0, x1):
        svg.line((x - 0.8, yd + 0.8), (x + 0.8, yd - 0.8), stroke=INK, sw=0.2)
    if t:
        svg.text(((x0 + x1) / 2, yd - 1.0), t, size=2.0, anchor="middle")
x0, x1 = E(1.35, 0)[0], E(4.05, 0)[0]
svg.line((x0, yd + 5), (x1, yd + 5), stroke=INK, sw=0.12)
svg.text(((x0 + x1) / 2, yd + 4), "oś przęsła 2,70 (2 moduły 1,35)", size=2.0, anchor="middle")

# ------------------------------------------------------------------ legend (layers)
LEG = [
    "1  okładzina: granit strzegomski płomieniowany 40 mm, kotwy nierdzewne (nieodpadające ≥ 60 min)",
    "2  pustka wentylowana 40 / wełna mineralna λ 0,033 – 200 mm; U = 0,15 W/(m²K), A1",
    "3  słup / podciąg obwodowy żelbetowy 300 / attyka żelbetowa 200",
    "4  płycina: aluminium anodowane grafitowy brąz (RAL 8019) 3 mm, A1",
    "5  okno Al z przekładką, pakiet 3-szybowy 54 mm, Uw ≤ 0,80; g = 0,33; roleta ZIP w nadprożu",
    "6  dolna kwatera stała ze szkła bezpiecznego do +1,10 m nad posadzką",
    "7  strop sprężony 280 z aktywacją termiczną (TABS), sufit odsłonięty + baffle",
    "8  podłoga podniesiona 150 (instalacje elektryczne i teletechniczne)",
    "9  kordon kwartału: granit +19,80–20,85 w linii gzymsu skrzydła i attyki Maz. 19",
    "10 kondygnacja cienia: szkło i metal 0,40 m za licem filarów",
    "11 okno holu Sejmiku 1,65 × 5,00 m, g = 0,27, R ≤ 12 %, nadruk punktowy (ochrona ptaków)",
    "12 kratownice stalowe h = 1,60 m, rozpiętość 19,5 m; sufit akustyczny +34,15",
    "13 dach: BIPV szkło-szkło BROOF(t1) / membrana / spadki / wełna 250–500 / paroizolacja /",
    "    płyta zespolona; U ≤ 0,12; bez urządzeń na dachu",
    "14 attyka 1,00 m: czapa granitowa, obróbka Al 0,15 m (górna krawędź +37,20 = 156,50)",
    "15 pas międzykondygnacyjny EI 60 ≥ 0,80 m; powyżej 25 m wszystkie warstwy niepalne",
]
lx, ly = 20.0, 26.0
svg.text((20.0, 12.0), "PRZEKRÓJ ELEWACYJNY I FRAGMENT ELEWACJI", size=4.4, weight=600)
svg.text((20.0, 18.0), "korona wieży od Placu Mostowego (elewacja pn., hol reprezentacyjny Sejmiku) · 1:50", size=2.4, fill="#4d4842")
yy = OY - (ZT - ZB) * SC + 2
for i, t in enumerate(LEG):
    svg.text((W_MM - 130, 40 + i * 3.6), t, size=2.0, fill="#2f2b28")
svg.text((W_MM - 130, 34), "WARSTWY (od zewnątrz)", size=2.4, weight=600)
# scale bar 0–2 m
sx, sy = 20.0, H_MM - 8
for i in range(4):
    svg.poly([(sx + i * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy + 1.2), (sx + i * 0.5 * SC, sy + 1.2)], fill=INK if i % 2 == 0 else "#fff", stroke=INK, sw=0.12)
svg.text((sx + 2 * SC + 4, sy + 1.2), "0–2 m · 1:50", size=2.2, weight=600)

out = ROOT / "build" / "rysunki" / "przekroj_elewacyjny_1-50.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / "przekroj_elewacyjny_1-50.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W_MM + 10:.0f}mm {H_MM + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{W_MM + 10:.0f} {H_MM + 10:.0f}")
