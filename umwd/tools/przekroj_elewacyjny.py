#!/usr/bin/env python3
"""Przekrój elewacyjny 1:50 z fragmentem elewacji (Etap II): korona wieży od strony Placu Mostowego (elewacja pn., hol
reprezentacyjny Sejmiku), z +19,10 (wariant pełny) lub +22,90 (UMWD_ZB=22.9 – wariant „korona”) do +37,70: kondygnacja 5
z kordonem kwartału, kondygnacja cienia (6), korona S z oknem 1,65 × 5,00, kratownica dachu, dach BIPV, attyka.
Warstwy wg koncepcji v1.1 (rozdz. 8, tabela przegród 1:50; JSON `elewacje.wieza`, `elewacje.U_scian`, `kondygnacje`):
filar – granit 40 / pustka 40 / wełna 260 λ 0,033 / żelbet; płycina – Al 3 / pustka 40 / wełna 260 / żelbet 200; konsole
nierdzewne z przekładką (U 0,147); ościeża 0,45 m z blachy Al (granit wyłącznie na licu filara); okna z parapetem 0,55
i nadprożem 3,00 (kaseta ZIP do +3,18 pod stropem +3,32); bez jakiegokolwiek wysięgu poza lico (czapa attyki, obróbki, parapety).

Wynik: build/rysunki/przekroj_elewacyjny_1-50[_korona].svg + docs/70_rysunki/podglady/przekroj_elewacyjny_1-50[_korona].html
"""
import sys, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.svg import Svg

K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
INK = "#1f1d1a"
SC = 20.0                         # 1:50 → 20 mm per metre
import os
ZB, ZT = float(os.environ.get("UMWD_ZB", "19.10")), 37.70
GRAN, GRAN_H = "#ddd8cf", "#b9b2a6"
INS = "#f1e9cf"
MET = "#4a4541"
MET_V = "#8f877f"                 # blacha Al ościeża widziana w głębi (za płaszczyzną przekroju)
GLASS = "#4a6a85"
CONC = "#e4e2de"

# ------------------------------------------------------------------ dane (koncepcja.json v1.1)
Z0 = float(K["meta"]["zero"]["wzgl_0_00_m_npm"])
KOND = {kd["kondygnacja"]: kd for kd in K["kondygnacje"]}
F4, F5, F6, FS = (float(KOND[i]["posadzka_wzgl"]) for i in ("4", "5", "6", "S"))
FLOOR = round(F6 - float(KOND["5"]["strop_nad"]["wierzch"]), 3)                                 # podłoga podniesiona 0,15
SLAB = round(float(KOND["5"]["strop_nad"]["wierzch"]) - float(KOND["5"]["strop_nad"]["spod_wieza"]), 3)   # płyta 0,28
EWI = K["elewacje"]["wieza"]
PAR, NADPR, OSC = float(EWI["parapet_m"]), float(EWI["nadproze_m"]), float(EWI["osciez_m"])     # 0,55 / 3,00 / 0,45
WIN_W = float(EWI["okno_m"][0])                                                                   # 1,65
KW = 1.10                                                    # kwatera stała do +1,10 nad posadzką (WT § 301)
ZIP = 0.18                                                   # kaseta ZIP nad nadprożem (do +3,18 ≤ spód stropu +3,32)
U_W = float(K["elewacje"]["U_scian"]["wieza"])               # 0,147
_m = re.search(r"wełna\s+(\d+)", K["elewacje"]["U_scian"].get("opis", ""))
WOOL = (int(_m.group(1)) if _m else 260) / 1000.0            # 0,26
DACH = {b["id"]: b for b in K["bryly"]}["W"]["dach"]
Z_ROOF, Z_ROOF_MAX, Z_ATT = (float(DACH["najnizszy_pkt_pokrycia"]["wzgl"]), float(DACH["najwyzszy_pkt_pokrycia"]["wzgl"]),
                             float(DACH["attyka"]["wzgl"]))  # +36,20 / +36,45 / +37,20
Z_SUF = float(KOND["S"]["dach"]["rusz_spod"])                # +34,15
Z_KORD = float(K["elewacje"]["skrzydlo"]["linie"]["attyka_npm"]) - Z0          # kordon do +20,85 (= gzyms skrzydła 140,15)
Z6_0 = float(KOND["5"]["strop_nad"]["wierzch"])             # +23,40 – początek cofnięcia kond. 6
Z6_1 = float(KOND["6"]["strop_nad"]["spod_wieza"])          # +26,87 – spód stropu S (podniebienie wnęki)
# układ warstw ściany od lica (X = 0, lico filarów = obrys; X < 0 do wnętrza)
X_CL, X_CAV = 0.04, 0.08                                     # okładzina 40 / pustka 40
X_INS = X_CAV + WOOL                                         # wełna 260 → −0,34
X_RC = X_INS + 0.20                                          # żelbet płyciny 200 → −0,54
REC6 = 0.40                                                  # kond. 6: szkło i metal 0,40 m za licem filarów
X6_INS, X6_RC = REC6 + 0.04 + WOOL, REC6 + 0.04 + WOOL + 0.20


def fz(z):
    return ("+" if z >= 0 else "−") + f"{abs(z):.2f}".replace(".", ",")


W_MM, H_MM = 480.0, (ZT - ZB) * SC + 60
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


# ------------------------------------------------------------------ stropy
for zf in (F5, F6, FS):
    st, sb = zf - FLOOR, zf - FLOOR - SLAB
    x_pp = -((X6_RC if zf == F6 else X_RC) + 0.16)                    # podłoga kończy się 0,16 m przed attyką podokienną
    rect(X_IN, sb, -X_INS, st, fill=hc, sw=0.25)                       # strop sprężony 280 (TABS) do lica wełny
    rect(X_IN, st, x_pp, zf, fill="#ffffff", sw=0.12)                  # podłoga podniesiona 150
    for q in range(1, 12):
        x = X_IN + q * 0.35
        if x < x_pp - 0.05:
            svg.line(P(x, st), P(x, zf - 0.03), stroke="#8a857e", sw=0.08)
    for q in range(1, 22):                                             # rury TABS
        x = X_IN + q * 0.18
        if x < -(X_INS + 0.08):
            svg.circle(P(x, sb + 0.07), 0.35, fill="none", stroke="#a8483a", sw=0.08)
call(7, -2.4, F6 - 0.3)
call(8, -3.6, F6 - 0.07)


def spandrel_flush(z0, z1, cladding="metal"):
    """Pas w licu: okładzina X 0…−0,04 (granit) lub 0…−0,006 (Al 3 mm) / pustka 40 / wełna 260 (X −0,08…−0,34)."""
    if z1 - z0 < 0.005:
        return
    if cladding == "granite":
        rect(-X_CL, z0, 0.0, z1, fill=hg, sw=0.2)
    else:
        rect(-0.006, z0, 0.0, z1, fill=MET, stroke=MET, sw=0.1)
    rect(-X_INS, z0, -X_CAV, z1, fill=hi, sw=0.12)


def reveal_beyond(z0, z1, x_out):
    """Ościeże 0,45 m z blachy Al widziane w głębi (bok filara między licem a ramą okna)."""
    rect(x_out, z0, 0.0, z1, fill=MET_V, stroke="#6b645e", sw=0.1, extra='fill-opacity="0.38"')
    svg.line(P(0.0, z0), P(0.0, z1), stroke="#6b645e", sw=0.14)


def window(zs, zh, x_out=-OSC, transom=None, zip_box=True, fixed_to=None, soffit=True):
    """Okno Al: rama w X = x_out … x_out − 0,10; parapet zewn. Al z kapinosem w licu (bez wysięgu poza X = 0);
    kaseta ZIP nad nadprożem (zh … zh + 0,18); podniebienie ościeża z blachy Al."""
    rect(x_out - 0.10, zs, x_out, zs + 0.08, fill=MET, stroke=MET)          # rama dolna
    rect(x_out - 0.10, zh - 0.08, x_out, zh, fill=MET, stroke=MET)          # rama górna
    for dx in (-0.025, -0.05, -0.075):
        svg.line(P(x_out + dx, zs + 0.08), P(x_out + dx, zh - 0.08), stroke=GLASS, sw=0.22)
    if transom:
        rect(x_out - 0.10, zs + transom - 0.04, x_out, zs + transom + 0.04, fill=MET, stroke=MET)
    if fixed_to:
        rect(x_out - 0.10, fixed_to - 0.04, x_out, fixed_to + 0.04, fill=MET, stroke=MET)
    # parapet zewnętrzny Al ze spadkiem, kapinos w licu (X ≤ 0) i podokiennik wewnętrzny
    svg.poly([P(-0.004, zs - 0.035), P(x_out, zs + 0.015), P(x_out, zs - 0.015), P(-0.004, zs - 0.065)], fill=MET, stroke=MET, sw=0.1)
    rect(-0.012, zs - 0.10, -0.004, zs - 0.035, fill=MET, stroke=MET, sw=0.08)
    rect(x_out - 0.30, zs, x_out - 0.10, zs + 0.03, fill="#cfc8bc", sw=0.08)
    if zip_box:
        rect(x_out + 0.015, zh, x_out + 0.165, zh + ZIP, fill="#6b645e", stroke=INK, sw=0.1)
    if soffit:
        rect(x_out, zh - 0.012, 0.0, zh, fill=MET, stroke=MET, sw=0.08)     # podniebienie ościeża: blacha Al


# ------------------------------------------------------------------ kond. 4 (nadproże, częściowo – maskowane poniżej ZB)
window(F4 + PAR, F4 + NADPR, fixed_to=F4 + KW)
reveal_beyond(F4 + PAR, F4 + NADPR, -OSC)
rect(-X_RC, F4 + NADPR + ZIP, -X_INS, F5 - FLOOR - SLAB, fill=hc, sw=0.2)    # nadproże żelbetowe
spandrel_flush(F4 + NADPR, F5, "metal")                                      # płycina 4/5 pod kordonem

# ------------------------------------------------------------------ kond. 5: kordon granitowy +19,80–20,85 (w licu), okno
rect(-X_RC, F5 - FLOOR, -X_INS, Z_KORD, fill=hc, sw=0.2)                     # attyka podokienna żelbetowa
spandrel_flush(F5, Z_KORD, "granite")
call(9, 0.0, F5 + 0.55, 0.6)
window(Z_KORD, F5 + NADPR)                 # rama dolna 0,08 → szkło od +1,13 nad posadzką (≥ 1,10)
reveal_beyond(Z_KORD, F5 + NADPR, -OSC)
call(5, -OSC - 0.05, F5 + 2.3, -1.6)
call(16, -OSC / 2, F5 + 1.6, 1.25)
call(17, -0.02, Z_KORD - 0.05, 0.9)
# płycina 5/6 w licu (Al) do wierzchu stropu kond. 6; nadproże żelbetowe
spandrel_flush(F5 + NADPR, Z6_0, "metal")
rect(-X_RC, F5 + NADPR + ZIP, -X_INS, F6 - FLOOR - SLAB, fill=hc, sw=0.15)
call(4, 0.0, Z6_0 - 0.12, 0.6)
call(15, -0.20, F5 + NADPR + 0.12, 1.5)
# obróbka Al nad pasem płycin (na wierzchu stropu, ze spadkiem na zewnątrz, kapinos w licu)
svg.poly([P(0.0, Z6_0 + 0.005), P(-REC6, Z6_0 + 0.035), P(-REC6, Z6_0 + 0.055), P(0.0, Z6_0 + 0.025)], fill=MET, stroke=MET, sw=0.1)
# ------------------------------------------------------------------ kond. 6 – cofnięta 0,40 m: płycina Al + okno
rect(-(REC6 + 0.006), Z6_0 + 0.05, -REC6, F6 + PAR, fill=MET, stroke=MET, sw=0.1)
rect(-X6_INS, Z6_0, -(REC6 + 0.04), F6 + PAR, fill=hi, sw=0.12)
rect(-X6_RC, F6 - FLOOR, -X6_INS, F6 + PAR, fill=hc, sw=0.15)
rect(-REC6, Z6_0 + 0.05, 0.0, Z6_1, fill=MET_V, stroke="#6b645e", sw=0.1, extra='fill-opacity="0.30"')   # bok filara w głębi (Al)
window(F6 + PAR, F6 + NADPR, x_out=-REC6, fixed_to=F6 + KW, zip_box=True, soffit=False)
rect(-(REC6 + 0.006), F6 + NADPR + ZIP, -REC6, Z6_1, fill=MET, stroke=MET, sw=0.1)       # panel Al nad kasetą
call(10, -REC6, F6 + 2.0, 1.0)
call(6, -REC6 - 0.05, F6 + PAR + 0.25, -1.75)
# podniebienie wnęki (blacha Al) i lico granitowe korony od spodu stropu S
rect(-REC6, Z6_1 - 0.012, 0.0, Z6_1, fill=MET, stroke=MET, sw=0.08)
spandrel_flush(Z6_1, FS + 0.70, "granite")
rect(-X_RC, FS - FLOOR, -X_INS, FS + 0.70, fill=hc, sw=0.2)

# ------------------------------------------------------------------ korona S: okno holu 1,65 × 5,00, poprzeczka na +30,50
window(FS + 0.70, FS + 5.70, transom=2.5, zip_box=False)
reveal_beyond(FS + 0.70, FS + 5.70, -OSC)
call(11, -OSC - 0.05, FS + 4.0, -1.6)
ZR_DECK = 35.80
spandrel_flush(FS + 5.70, Z_ROOF, "granite")
rect(-X_RC, FS + 5.70, -X_INS, Z_ROOF, fill=hc, sw=0.2)                     # wieniec / attyka żelbetowa
call(1, 0.0, 34.6, 0.6)
call(2, -0.20, 33.6, 0.6)
call(3, -(X_INS + X_RC) / 2, 34.0, 0.6)
# kratownice stalowe 1,60 m (34,20–35,80), sufit akustyczny +34,15
zt0, zt1 = Z_SUF + 0.05, ZR_DECK
svg.line(P(X_IN, zt1 - 0.1), P(-X_RC, zt1 - 0.1), stroke=INK, sw=0.5)
svg.line(P(X_IN, zt0 + 0.1), P(-X_RC, zt0 + 0.1), stroke=INK, sw=0.5)
x = X_IN
while x < -(X_RC + 0.1):
    svg.line(P(x, zt0 + 0.1), P(min(-X_RC, x + 0.8), zt1 - 0.1), stroke=INK, sw=0.25)
    svg.line(P(min(-X_RC, x + 0.8), zt1 - 0.1), P(min(-X_RC, x + 1.6), zt0 + 0.1), stroke=INK, sw=0.25)
    x += 1.6
rect(X_IN, Z_SUF - 0.05, -(X_RC + 0.16), Z_SUF, fill="#bdb6ab", sw=0.08)
call(12, -2.6, 35.0)
# dach: płyta zespolona 35,80–35,95, paroizolacja, wełna w spadku, membrana, BIPV szkło-szkło (+36,20 … +36,45)
xr = -X_RC
rect(X_IN, ZR_DECK, xr, ZR_DECK + 0.15, fill=hc, sw=0.2)
svg.poly([P(X_IN, Z_ROOF_MAX - 0.08), P(xr, Z_ROOF - 0.05), P(xr, ZR_DECK + 0.15), P(X_IN, ZR_DECK + 0.15)], fill=hi, stroke=INK, sw=0.15)
svg.poly([P(X_IN, Z_ROOF_MAX - 0.05), P(xr, Z_ROOF - 0.02), P(xr, Z_ROOF - 0.05), P(X_IN, Z_ROOF_MAX - 0.08)], fill=INK, stroke="none")
dz = (Z_ROOF_MAX - Z_ROOF) - 0.03
for q in range(6):
    xa = X_IN + q * 0.7
    if xa < -0.9:
        za = Z_ROOF_MAX - 0.05 - (xa - X_IN) / (xr - X_IN) * dz
        svg.poly([P(xa, za + 0.02), P(xa + 0.62, za + 0.02 - 0.62 / (xr - X_IN) * dz), P(xa + 0.62, za + 0.07 - 0.62 / (xr - X_IN) * dz),
                  P(xa, za + 0.07)], fill="#2e3a48", stroke=INK, sw=0.08)
call(13, -2.0, 36.35)
# attyka: żelbet 200, wełna 260, granit 40; czapa granitowa i obróbka Al – wszystko w obrysie (X ≤ 0)
rect(-X_RC, Z_ROOF - 0.05, -X_INS, Z_ATT - 0.15, fill=hc, sw=0.2)
rect(-X_INS, Z_ROOF, -X_CAV, Z_ATT - 0.15, fill=hi, sw=0.12)
rect(-X_CL, Z_ROOF, 0.0, Z_ATT - 0.15, fill=hg, sw=0.2)
svg.poly([P(0.0, Z_ATT - 0.15), P(-(X_RC + 0.08), Z_ATT - 0.15), P(-(X_RC + 0.08), Z_ATT - 0.10), P(0.0, Z_ATT - 0.04)], fill=hg, stroke=INK, sw=0.2)
svg.poly([P(0.0, Z_ATT - 0.04), P(-(X_RC + 0.10), Z_ATT - 0.10), P(-(X_RC + 0.10), Z_ATT - 0.065), P(0.0, Z_ATT)], fill=MET, stroke=MET, sw=0.1)
rect(-(X_RC + 0.10), Z_ATT - 0.30, -(X_RC + 0.08), Z_ATT - 0.065, fill=MET, stroke=MET, sw=0.08)   # obróbka od strony dachu
call(14, -0.3, Z_ATT + 0.05, 0.8)
# break lines
svg.line(P(X_IN - 0.1, ZB + 0.05), P(0.4, ZB + 0.05), stroke=INK, sw=0.15, dash="1.5,0.8")
svg.line(P(X_IN, ZB), P(X_IN, ZT - 0.2), stroke=INK, sw=0.15, dash="1.5,0.8")

# ------------------------------------------------------------------ rzędne
for z, lab in ((Z_ATT, f"{fz(Z_ATT)} attyka = {Z_ATT + Z0:.2f}".replace(".", ",")),
               (Z_ROOF_MAX, f"{fz(Z_ROOF_MAX)} najwyższy pkt pokrycia"),
               (Z_ROOF, f"{fz(Z_ROOF)} najniższy pkt pokrycia (MPZP ≥ 35,0 m)"),
               (Z_SUF, f"{fz(Z_SUF)} sufit holu ({Z_SUF - FS:.2f} m)".replace(".", ",")), (FS, f"{fz(FS)} posadzka S"),
               (F6, f"{fz(F6)} posadzka 6"), (Z_KORD, f"{fz(Z_KORD)} kordon = gzyms skrzydła"), (F5, f"{fz(F5)} posadzka 5")):
    if z < ZB + 0.2:
        continue
    x, y = P(X_IN - 0.4, z)
    svg.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
    svg.line((x - 2.5, y), (x + 4, y), stroke=INK, sw=0.12)
    svg.text((x - 3, y - 0.4), lab, size=2.1, anchor="end")

# ------------------------------------------------------------------ odnośniki
for n, X, Z, dx in callouts:
    if Z < ZB + 0.1:
        continue
    x, y = P(X, Z)
    bx = x + dx * SC
    if dx:
        svg.line((x, y), (bx, y), stroke=INK, sw=0.12)
    svg.circle((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y), 2.2, fill="#ffffff", stroke="#a8483a", sw=0.25)
    svg.text((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y + 0.8), str(n), size=2.2, anchor="middle", weight=700, fill="#a8483a")

# ------------------------------------------------------------------ fragment elewacji (2 przęsła) po prawej
EX0 = 2.9      # paper offset (m at 1:50) from section façade plane


def E(u, z):
    return (OX + (EX0 + u) * SC, OY - (z - ZB) * SC)


def erect(u0, z0, u1, z1, fill, stroke=INK, sw=0.15, extra=""):
    svg.poly([E(u0, z0), E(u1, z0), E(u1, z1), E(u0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)


def ewin(a, b, z0, z1, fill="#7b8792", mull=True, transom=None, osc=OSC):
    """Okno w elewacji z cieniem nadproża i ościeża 0,45 m (światło z lewej góry)."""
    erect(a, z0, b, z1, fill, sw=0.12)
    if mull:
        svg.line(E((a + b) / 2, z0), E((a + b) / 2, z1), stroke=MET, sw=0.35)
    if transom:
        erect(a, z0 + transom - 0.04, b, z0 + transom + 0.04, MET, stroke="none")
    sh = min(osc * 0.75, (z1 - z0) * 0.3)
    erect(a, z1 - sh, b, z1, "#1f1d1a", stroke="none", extra='fill-opacity="0.32"')
    erect(a, z0, a + osc * 0.6, z1 - sh, "#1f1d1a", stroke="none", extra='fill-opacity="0.24"')


piers = [(0.0, 0.525), (2.175, 3.225), (4.875, 5.4)]
bays = [(0.525, 2.175), (3.225, 4.875)]
erect(0, ZB, 5.4, Z_ROOF, MET, stroke="none")
for a, b in bays:
    ewin(a, b, F4 + PAR, F4 + NADPR, transom=KW - PAR)                          # kond. 4 (maskowana poniżej ZB)
    erect(a, F5, b, Z_KORD, hg)                                                 # kordon
    ewin(a, b, Z_KORD, F5 + NADPR)                                              # kond. 5
    # kond. 6 (cofnięta 0,40, ciemniejsza)
    erect(a, Z6_0, b, Z6_1, "#2e2b29", stroke="none")
    erect(a + 0.05, F6 + PAR, b - 0.05, F6 + NADPR, "#3d434a", stroke="#5d646b", sw=0.1)
    svg.line(E((a + b) / 2, F6 + PAR), E((a + b) / 2, F6 + NADPR), stroke=MET, sw=0.3)
    erect(a + 0.05, F6 + KW - 0.03, b - 0.05, F6 + KW + 0.03, MET, stroke="none")
    erect(a, Z6_1 - 0.45, b, Z6_1, "#1f1d1a", stroke="none", extra='fill-opacity="0.5"')
    # okno holu w koronie
    erect(a, Z6_1, b, FS + 0.70, hg)
    ewin(a, b, FS + 0.70, FS + 5.70, transom=2.5)
    erect(a, FS + 5.70, b, Z_ROOF, hg)
    for qz in range(12):          # nadruk punktowy na szkle korony (ochrona ptaków)
        for qu in range(7):
            svg.circle(E(a + 0.12 + qu * 0.24, FS + 0.9 + qz * 0.38), 0.18, fill="#ffffff", stroke="none", extra='fill-opacity="0.35"')
for a, b in piers:
    erect(a, ZB, b, Z_ROOF, hg, sw=0.2)
    zj = ZB + 0.6
    while zj < Z_ROOF:
        svg.line(E(a, zj), E(b, zj), stroke=GRAN_H, sw=0.1)
        zj += 1.25
    svg.line(E(b, ZB), E(b, Z_ROOF), stroke=INK, sw=0.1)
    erect(b, ZB, min(5.4, b + 0.12), Z_ROOF, "#1f1d1a", stroke="none", extra='fill-opacity="0.12"')
erect(0, Z_ROOF, 5.4, Z_ATT - 0.06, hg, sw=0.2)
erect(0, Z_ATT - 0.06, 5.4, Z_ATT, MET, stroke=MET, sw=0.1)                  # obróbka attyki w licu (bez wysięgu)
svg.text((E(2.7, 0)[0], E(0, ZT)[1] - 2), "FRAGMENT ELEWACJI PÓŁNOCNEJ (2 przęsła)", size=2.6, anchor="middle", weight=600)
svg.text((P(-2.3, 0)[0], P(0, ZT)[1] - 2), "PRZEKRÓJ PRZEZ OŚ OKNA", size=2.6, anchor="middle", weight=600)
# maska poniżej podstawy fragmentu (wariant korony) – biały pas od ZB w dół
svg.poly([(0, OY + 0.3), (W_MM, OY + 0.3), (W_MM, H_MM + 120), (0, H_MM + 120)], fill="#ffffff", stroke="none")
svg.line((OX + (X_IN - 0.2) * SC, OY + 0.3), (OX + 0.5 * SC, OY + 0.3), stroke=INK, sw=0.15, dash="1.5,0.8")
# wymiary (pod fragmentem elewacji)
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

# ------------------------------------------------------------------ legenda warstw (v1.1, tabela przegród 1:50)
u_txt = f"{U_W:.3f}".replace(".", ",")
w_mm = int(round(WOOL * 1000))
o_txt = f"{OSC:.2f}".replace(".", ",")
LEG = [
    "1  lico filarów: granit strzegomski płomieniowany 40 mm (S 1502-Y), kotwy nierdzewne",
    "    (okładzina nieodpadająca ≥ 60 min); ościeża i węgary bez granitu",
    f"2  pustka wentylowana 40 / wełna mineralna λ 0,033 – {w_mm} mm; konsole ze stali nierdzewnej",
    f"    z przekładką termiczną (ΔU 0,025) → U = {u_txt} W/(m²K); całość A1 (NRO)",
    "3  ściana-słup żelbetowy filara 300 / płycina i wieniec żelbet 200 / attyka żelbetowa 200",
    "4  płycina: aluminium anodowane grafitowy brąz RAL 8019, 3 mm, A1",
    "    (od dziedzińca ≤ 25 m: BIPV szkło-szkło 10 mm w tym kolorze, ≥ B-s1,d0)",
    "5  okno Al z przekładką, pakiet 3-szybowy 54 mm, Uw ≤ 0,80, g = 0,33; parapet 0,55,",
    f"    nadproże 3,00; kaseta ZIP do +3,18 (pod stropem +3,32), > 25 m tkanina szklano-silikonowa A2",
    f"6  dolna kwatera stała ze szkła bezpiecznego do +{KW:.2f} m nad posadzką (WT § 301)".replace(".", ","),
    "7  strop sprężony 280 z aktywacją termiczną (TABS), sufit odsłonięty + baffle",
    "8  podłoga podniesiona 150 (instalacje elektryczne i teletechniczne)",
    "9  kordon kwartału: granit +19,80–20,85 w linii gzymsu skrzydła (140,15) i attyki Maz. 19",
    "10 kondygnacja cienia: szkło i metal 0,40 m za licem filarów; obróbka Al nad pasem płycin",
    "11 okno holu Sejmiku 1,65 × 5,00 m, g = 0,27, R ≤ 12 %, nadruk punktowy (ochrona ptaków)",
    "12 kratownice stalowe h = 1,60 m, rozpiętość 19,5 m; sufit akustyczny +34,15",
    "13 dach: BIPV szkło-szkło BROOF(t1) / membrana / spadki / wełna mineralna 300 / paroizolacja /",
    "    płyta zespolona; U ≤ 0,12; bez urządzeń na dachu (zwody ≤ korony attyki)",
    "14 attyka 1,00 m: czapa granitowa i obróbka Al RAL 8019 w obrysie, bez wysięgu (+37,20 = 156,50)",
    "15 pas międzykondygnacyjny EI 60 ≥ 0,80 m; powyżej 25 m wszystkie warstwy i mocowania niepalne",
    f"16 ościeże {o_txt} m: blacha Al lakierowana proszkowo RAL 8019 na wełnie (granit tylko na licu filara)",
    "17 parapet zewnętrzny Al ze spadkiem, kapinos w licu – bez wysięgu poza obrys (lico wieży)",
]
svg.text((20.0, 12.0), "PRZEKRÓJ ELEWACYJNY I FRAGMENT ELEWACJI", size=4.4, weight=600)
svg.text((20.0, 18.0), "korona wieży od Placu Mostowego (elewacja pn., hol reprezentacyjny Sejmiku) · 1:50", size=2.4, fill="#4d4842")
LX = W_MM - 128
for i, t in enumerate(LEG):
    t = ("\u00a0" * 6 + t.lstrip()) if t.startswith("    ") else t      # wcięcie wiersza kontynuacji
    svg.text((LX, 40 + i * 3.6), t, size=2.0, fill="#2f2b28")
svg.text((LX, 34), "WARSTWY (od zewnątrz)", size=2.4, weight=600)
# podziałka 0–2 m
sx, sy = 20.0, H_MM - 8
for i in range(4):
    svg.poly([(sx + i * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy + 1.2), (sx + i * 0.5 * SC, sy + 1.2)], fill=INK if i % 2 == 0 else "#fff", stroke=INK, sw=0.12)
svg.text((sx + 2 * SC + 4, sy + 1.2), "0–2 m · 1:50", size=2.2, weight=600)

SUF = "_korona" if ZB > 20 else ""
out = ROOT / "build" / "rysunki" / f"przekroj_elewacyjny_1-50{SUF}.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / f"przekroj_elewacyjny_1-50{SUF}.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W_MM + 10:.0f}mm {H_MM + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{W_MM + 10:.0f} {H_MM + 10:.0f}")
