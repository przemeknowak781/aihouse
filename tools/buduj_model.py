#!/usr/bin/env python3
"""Parametryczny generator modelu „Dom LAMELA” — KONCEPCJA OSTATECZNA (synteza).

Baza: wariant W2 (ocena J1/J2 — średnia 72,7 pkt; W1 70,7; W3 66,0) + przeszczepy z W1/W3 + WSZYSTKIE poprawki
obowiązkowe sędziów J1–J3 (docs/20_koncepcja/ocena_J*.md). Jedno źródło prawdy: skrypt zapisuje
  model/budynek.yaml, model/dzialka.yaml, model/wyposazenie.yaml, model/instalacje.yaml
(schemat: docs/SCHEMAT_MODELU.md; rdzeń: src/lamela/model.py). Liczby w opisie koncepcji pochodzą z modelu
(tools/podglad_modelu.py → docs/20_koncepcja/final/bilans.md).

Uruchomienie:  python3 tools/buduj_model.py   (potem: PYTHONPATH=src python3 -m lamela.model model/budynek.yaml model/dzialka.yaml)

Układ: x → wschód, y → północ, z → góra; (0,0) = przecięcie osi A i 1; ±0,00 = posadzka P0 = 101,65 m n.p.m.
Moduł wymiarowy osi: 0,125 m (bloczki silikatowe 1/8-modułowe); otwory w wielokrotnościach 0,05 m (tam, gdzie możliwe);
współrzędne zaokrąglane do 0,005 m.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model"

# =====================================================================================================================
# 1. PARAMETRY — osie, poziomy, grubości (wszystkie wymiary w m)
# =====================================================================================================================
X = {"A'": -1.000, "A": 0.000, "B": 3.875, "C": 5.875, "M": 7.190, "D": 8.500, "D'": 9.875, "E": 12.000,
     "P": 14.875, "F": 18.375}
Y = {"1": 0.000, "2": 2.875, "H": 3.750, "3": 5.125, "4": 8.750, "5": 9.375}

ZERO_ABS = 101.65                      # ±0,00 = posadzka P0 [m n.p.m., PL-EVRF2007-NH]
H_KOND = 3.15                          # wysokość kondygnacji P0, P1
PODL = 0.15                            # warstwy podłogi nad płytą (z ogrzewaniem podłogowym)
T_STR = 0.22                           # grubość stropów ST1, ST2 i płyty stropodachu P2
Z_P1, Z_P2 = 3.15, 6.30                # rzędne posadzek
Z_ST1, Z_ST2, Z_ST3 = Z_P1 - PODL, Z_P2 - PODL, 9.30   # wierzch płyt konstrukcyjnych
Z_DG = 3.00                            # wierzch płyty dachu garażu / pasa gospodarczego (= ST1)
T_DG = 0.24                            # grubość płyty dachu garażu (dwukierunkowa 6,375 × 6,50 m)
Z_PLYTA_F = -PODL                      # wierzch płyty fundamentowej (−0,15)
T_PLYTA_F = 0.25

# połowa grubości ścian od osi (warstwa konstrukcyjna 0,18 m + wykończenia)
KZ = 0.09          # połowa warstwy konstrukcyjnej 18 cm
EXT = 0.30         # lico zewnętrzne SZ1/SZ2 od osi: 0,09 + 0,20 + 0,01
INT = 0.105        # lico wewnętrzne ściany 18 cm od osi (0,09 + tynk 0,015)
FD = 0.075         # lico ścianki działowej 12 cm (0,06 + 0,015)
GAR = 0.22         # lico ściany dom–garaż od strony garażu (0,09 + wełna 0,12 + tynk 0,01)

# lica wykończone używane w rzutach / pomieszczeniach
XA_i, XE_i = X["A"] + INT, X["E"] - INT                      # 0,105 / 11,895
Y1_i, Y3_s, Y3_n, Y4_i = Y["1"] + INT, Y["3"] - INT, Y["3"] + INT, Y["4"] - INT   # 0,105 / 5,02 / 5,23 / 8,645
XC_w, XC_e = X["C"] - INT, X["C"] + INT                      # 5,77 / 5,98
XD_w, XD_e = X["D"] - INT, X["D"] + INT                      # 8,395 / 8,605
XM_w, XM_e = X["M"] - 0.06, X["M"] + 0.06                    # 7,13 / 7,25 (ścianka środkowa 12 cm, bez tynku — silikat licowy)

# schody (identyczne SCH1 i SCH2, jedne nad drugimi) — WT §68–69, W-090/W-091
H_ST, S_ST, N_BIEG = 0.175, 0.28, 9                       # h, s, liczba podnóżków w biegu
Y_SCH0 = Y3_n                                              # pierwszy podnóżek (lico ściany osi 3 od pn.)
Y_SPOCZ = round(Y_SCH0 + (N_BIEG - 1) * S_ST, 4)          # krawędź spocznika (7,47)
B1_X0, B1_X1 = XC_e, XM_w                                  # bieg 1 (pas zachodni) 5,98–7,13 = 1,15 m
B2_X0, B2_X1 = XM_e, XD_w                                  # bieg 2 (pas wschodni) 7,25–8,395 = 1,145 m

# szacht instalacyjny SI (pion K1 Ø110, RS1/RS2 DN100, kanały reku) — w świetle 0,40 × 1,12 m
SI = (5.370, Y3_n, 5.770, 6.350)

# poziomy elementów zewnętrznych (krawędzie płyt — „warstwy” sylwety S)
Z_OKAP_E = (2.75, 3.05)        # okap E (ST1) — płyta pogrubiona 30 cm
Z_RAMA_D = (3.65, 3.85)        # linia D: dolny pas ramy C = wierzch attyki garażu +3,85
Z_RAMA_G = (5.35, 5.55)        # górny pas ramy C
Z_OKAP_2 = (5.95, 6.25)        # krawędź ST2 (spód bryły A)
Z_OKAP_3 = (9.08, 9.40)        # krawędź ST3 (stropodach bryły A)


def r(v: float, n: int = 4) -> float:
    v = round(float(v), n)
    return 0.0 if v == 0 else v


def P(*pts) -> list:
    """Wielobok CCW z zaokrągleniem."""
    poly = orient(Polygon(pts), 1.0)
    c = list(poly.exterior.coords)[:-1]
    return [[r(x), r(y)] for x, y in c]


def R(x0, y0, x1, y1) -> list:
    return P((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def seg_len(p1, p2) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])
