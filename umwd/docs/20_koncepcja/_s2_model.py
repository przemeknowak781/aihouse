# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 (+27,30) z antresolą (+30,90) – model geometryczny (wariant S-3 „hol z galerią”).

Jedno źródło geometrii dla skryptów _s2_*.py. Uruchomienie z katalogu umwd/:
    python3 docs/20_koncepcja/_s2_model.py        → zapisuje docs/20_koncepcja/kondygnacja_S2.json i drukuje kontrole

Układ (u, v) wieży wg model/koncepcja.json:
    e = 74,606 + 0,97155·u − 0,23684·v ;  n = 40,756 + 0,23684·u + 0,97155·v
    prostokąt u 0–40 × v 0–29,7 + łuk R 14,0 (środek u 26,0; v 15,7) w narożu NE; lico wewnętrzne ścian zewn. 0,50 m.
Trzony (obrysy stałe): A u 8,30–15,50 × v 12,45–20,85; B u 24,85–31,10 × v 0,50–9,90.
Źródła: koncepcja.json (bryly[W], rdzenie, kondygnacja_sejmiku), program.yaml (SWD, PHS.05, PP.06, IT.02),
weryfikacja_program.md (K1–K3, I1, I4, D1, D9, D13, D14). Nie korzystano z informacji o pracach ani wynikach konkursu.
"""
import json
import math
import os

from shapely.geometry import Polygon, Point, box, LineString, mapping
from shapely.ops import unary_union

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
K = json.load(open(os.path.join(ROOT, "model", "koncepcja.json"), encoding="utf-8"))

CU, SU = 0.97155, 0.23684
E0, N0 = 74.606, 40.756


def uv2en(u, v):
    return (E0 + CU * u - SU * v, N0 + SU * u + CU * v)


def en2uv(e, n):
    de, dn = e - E0, n - N0
    return (CU * de + SU * dn, -SU * de + CU * dn)


# ------------------------------------------------------------------------------------------------
# Bryła wieży i lico wewnętrzne
# ------------------------------------------------------------------------------------------------
W_EN = Polygon(K["bryly"][0]["obrys_ccw"])
W_UV = Polygon([en2uv(*p) for p in K["bryly"][0]["obrys_ccw"]])
C_ARC = (26.0, 15.7)            # środek łuku (u, v)
R_ARC_IN = 13.5                 # lico wewnętrzne / szkło korony


def _inner():
    rect = box(0.5, 0.5, 39.5, 29.2)
    quad = box(26.0, 15.7, 40.0, 30.0)
    disk = Point(C_ARC).buffer(R_ARC_IN, resolution=256)
    return rect.difference(quad.difference(disk))


INNER = _inner()                # wnętrze kondygnacji (od lica wewnętrznego), ≈ 1 080,1 m²

CORE_A = box(8.30, 12.45, 15.50, 20.85)
CORE_B = box(24.85, 0.50, 31.10, 9.90)

# Rzędne
Z_S = 27.30
Z_ANT = 30.90
Z_SPOD_DACHU = 34.15            # spód kratownic (pas dolny) = 6,85 m nad S
H_SALA = Z_SPOD_DACHU - Z_S

# ------------------------------------------------------------------------------------------------
# Trzony – proponowany układ wewnętrzny (założenie do scalenia z I5; obrysy bez zmian)
# ------------------------------------------------------------------------------------------------
CORE_A_CELLS = {
    "A1": box(8.55, 18.05, 10.80, 20.60),      # szyb 2,25 × 2,55 (kabina 1,5 × 2,1; 1 600 kg), drzwi N
    "A2": box(11.00, 18.05, 13.25, 20.60),     # jw.
    "R": box(13.45, 18.05, 15.25, 20.60),      # szyb 1,80 × 2,55 (kabina 1,1 × 2,1; 1 000 kg), drzwi S do przedsionka
    "klatka_A": box(8.55, 12.70, 11.95, 17.85),
    "przedsionek_A": box(12.15, 12.70, 15.25, 17.85),
}
CORE_B_CELLS = {
    "klatka_B": box(25.10, 0.75, 28.50, 7.10),
    "przedsionek_B": box(25.10, 7.30, 28.50, 9.65),
    "szachty_B": box(28.70, 0.75, 30.85, 3.95),   # po przeniesieniu dźwigu T do segmentu (I5): wyrzutnia/czerpnia D8
    "P1": box(28.70, 4.15, 30.85, 6.80),        # szyb 2,15 × 2,65 (kabina 1,5 × 2,1 drzwiami na boku 2,1; 1 600 kg), drzwi E
    "P2": box(28.70, 7.00, 30.85, 9.65),        # jw.
}
# drzwi dźwigów: (szyb, punkt środka drzwi na licu trzonu, kierunek wyjścia, kondygnacje)
LIFT_DOORS = [
    ("A1", (9.60, 20.85), (0, 1), ["S", "ANT"]),
    ("A2", (11.85, 20.85), (0, 1), ["S", "ANT"]),
    ("P1", (31.10, 5.475), (1, 0), ["ANT"]),          # na S bez przystanku (strefa radnych)
    ("P2", (31.10, 8.325), (1, 0), ["S*", "ANT"]),    # S* – przystanek służbowy (klucz), zaplecze baru / dostawy
]
DOOR_W_LIFT = 1.10

# ------------------------------------------------------------------------------------------------
# Poziom główny S (+27,30)
# ------------------------------------------------------------------------------------------------
SALA_BOX = box(22.00, 12.60, 39.50, 29.20)
SWD04_BOX = box(33.80, 12.60, 39.50, 16.00)      # reżyserka ze ścianami od strony sali


def level_S():
    R = {}
    # pas pd. – komisje (okna pd.)
    R["SWD.08"] = box(0.50, 0.50, 11.20, 9.90).difference(box(9.10, 5.10, 11.20, 9.90))
    R["SWD.10a"] = box(9.30, 5.30, 11.20, 9.90)
    R["SWD.10b"] = box(11.40, 5.30, 13.30, 9.90)
    R["IT.02"] = box(13.50, 7.40, 15.40, 9.90)
    R["SWD.09"] = (box(11.40, 0.50, 18.85, 9.90)
                   .difference(box(11.40, 5.10, 13.50, 9.90))
                   .difference(box(13.50, 7.20, 15.60, 9.90)))
    R["SWD.11a"] = box(19.05, 0.50, 24.85, 9.90)
    # naroże SE (okna pd. i wsch.)
    R["SWD.11b"] = box(31.10, 0.50, 39.50, 7.10)
    R["KW.S.02"] = box(31.10, 7.30, 32.70, 9.90)      # dojście do SWD.11b i przystanek służbowy P2
    R["SWD.07"] = box(32.90, 7.30, 37.20, 9.90)
    R["PP.06"] = box(37.40, 7.30, 39.50, 9.90)
    # kuluar (droga ewakuacyjna, EI 30, oddymiany)
    R["KUL"] = unary_union([box(0.50, 10.10, 39.50, 12.30),
                            box(8.30, 12.30, 15.50, 12.45),     # przed przedsionkiem A
                            box(24.85, 9.90, 31.10, 10.10)])    # przed przedsionkiem B
    # pas zach. – kluby 15 os. (okna zach.) + pasaż przy trzonie A
    R["SWD.12a"] = box(0.50, 12.50, 6.30, 17.70)
    R["SWD.12b"] = box(0.50, 17.90, 6.30, 23.10)
    R["KW.S.01"] = box(6.50, 12.30, 8.30, 20.85)      # pasaż zach.: kuluar ↔ hol
    # pas między trzonem A a salą: łącznik + WC
    R["KW.S.03"] = box(15.50, 12.30, 16.90, 20.85)    # łącznik wsch.: kuluar ↔ hol, drzwi przedsionka A
    R["PHS.05a"] = box(17.10, 12.50, 19.30, 20.85)    # WC damskie z kabiną dostępną
    R["PHS.05b"] = box(19.50, 12.50, 21.70, 20.85)    # WC męskie z kabiną dostępną
    # pas pn. (okna pn. 1,65 × 5,0)
    R["SWD.14"] = box(12.65, 22.85, 15.80, 29.20)
    R["SWD.13"] = box(16.00, 22.85, 21.70, 29.20)
    # hol reprezentacyjny – część dolna
    hall = unary_union([box(6.50, 20.85, 21.70, 22.65),
                        box(6.50, 22.65, 12.45, 23.30),
                        box(0.50, 23.30, 12.45, 29.20)])
    R["SWD.06"] = box(1.85, 23.30, 6.65, 25.85)               # szatnia: lada 4,8 m + wieszaki, 1,35 m od okna zach.
    STAIR = box(1.10, 26.05, 8.30, 27.85)                     # schody reprezentacyjne S → ANT (bieg 1,80 × 7,20)
    R["SWD.15"] = box(4.90, 26.05, 8.30, 27.85)               # magazyn podręczny pod wyższą częścią biegu (h ≥ 1,9 m)
    R["KW.S.04"] = box(1.10, 26.05, 4.90, 27.85)              # niższa część biegu (otwarta)
    R["SWD.02"] = hall.difference(R["SWD.06"]).difference(STAIR)
    # sala obrad + reżyserka
    R["SWD.04"] = box(34.00, 12.60, 39.50, 15.80)
    R["SWD.01"] = INNER.intersection(SALA_BOX).difference(SWD04_BOX)
    return R


# ------------------------------------------------------------------------------------------------
# Antresola +30,90
# ------------------------------------------------------------------------------------------------
def level_ANT():
    A = {}
    # strefa publiczna (wejście P1/P2 – Wejście Obywatelskie na parterze)
    A["KW.A.01"] = box(31.10, 4.00, 34.70, 10.10)                      # hol dźwigów P1/P2 (3,6 m)
    A["PHS.05c"] = box(34.90, 4.00, 37.10, 6.60)                       # toaleta dostępna publiczności
    A["KW.A.02"] = unary_union([box(15.50, 10.10, 34.70, 12.30),       # korytarz publiczny nad kuluarem (EI 30)
                                box(24.85, 9.90, 31.10, 10.10)])        # przed przedsionkiem B (+30,90)
    gal = box(15.50, 12.60, 22.00, 22.65)
    A["SWD.01g"] = gal                                                 # galeria publiczności (część SWD.01)
    # strefa radnych – górny hol (antresola holu), wycofana 1,35 m od elewacji zach. i pn.
    west = box(1.85, 12.50, 8.30, 23.30)
    lobby = box(8.30, 20.85, 12.45, 27.85)
    north = box(12.45, 22.65, 21.70, 27.85)
    band = box(12.45, 20.85, 15.30, 22.65)
    antw = unary_union([west, lobby, north, band])
    A["SWD.05"] = box(15.30, 22.85, 21.70, 27.85)                      # bar / przestrzeń socjalno-gastronomiczna
    A["SWD.03"] = box(1.85, 12.50, 6.30, 20.10)                        # strefa multimedialna / poczekalnia gości
    A["KW.A.03"] = box(6.30, 13.00, 8.30, 16.00)                       # przedsionek ppoż. A' (wejście do klatki A od zach.)
    A["SWD.02g"] = antw.difference(A["SWD.05"]).difference(A["SWD.03"]).difference(A["KW.A.03"]) \
        .difference(box(15.30, 22.65, 21.70, 22.85))                   # pas ściany galeria/bar
    return A


VOID_HALL = box(0.50, 23.30, 8.30, 29.20).union(box(8.30, 27.85, 12.45, 29.20))   # pustka holu (2 kond.)

# ------------------------------------------------------------------------------------------------
# Drzwi (u, v, szerokość, pomieszczenie → komunikacja). Punkt = środek otworu na osi ściany.
# ------------------------------------------------------------------------------------------------
DOORS_S = [
    ("SWD.08", "KUL", (4.0, 10.0), 1.6), ("SWD.08", "KUL", (8.0, 10.0), 1.0),
    ("SWD.10a", "KUL", (10.25, 10.0), 0.9), ("SWD.10b", "KUL", (12.35, 10.0), 0.9),
    ("IT.02", "KUL", (14.45, 10.0), 0.9), ("SWD.09", "KUL", (17.0, 10.0), 1.0),
    ("SWD.11a", "KUL", (21.0, 10.0), 1.0), ("SWD.11a", "KUL", (24.0, 10.0), 1.0),
    ("SWD.11b", "KW.S.02", (31.9, 7.2), 1.0), ("KW.S.02", "KUL", (31.9, 10.0), 1.2),
    ("SWD.07", "KUL", (35.0, 10.0), 0.9), ("PP.06", "KUL", (38.4, 10.0), 0.9),
    ("SWD.12a", "KUL", (3.4, 12.4), 1.0), ("SWD.12b", "KW.S.01", (6.4, 20.3), 1.0),
    ("KW.S.01", "KUL", (7.4, 12.3), 1.6), ("KW.S.01", "SWD.02", (7.4, 20.85), 1.6),
    ("KW.S.03", "KUL", (16.2, 12.3), 1.2), ("KW.S.03", "SWD.02", (16.2, 20.85), 1.2),
    ("PHS.05a", "SWD.02", (18.2, 20.85), 1.0), ("PHS.05b", "SWD.02", (20.6, 20.85), 1.0),
    ("SWD.14", "SWD.02", (14.2, 22.75), 1.0), ("SWD.13", "SWD.02", (17.2, 22.75), 1.0),
    ("SWD.04", "KUL", (35.0, 12.45), 1.0),
    ("SWD.01", "SWD.02", (21.85, 21.75), 1.6),     # wejście główne radnych i gości z holu (NW)
    ("SWD.01", "KUL", (24.2, 12.45), 1.6),         # wyjście SW (pod galerią) – do klatki A
    ("SWD.01", "KUL", (32.6, 12.45), 1.6),         # wyjście SE – do klatki B
    ("SWD.01", "KUL", (28.0, 12.45), 1.0),         # drzwi prezydium (za stołem prezydialnym)
    ("SWD.15", "SWD.02", (6.6, 25.95), 0.9),
    ("przedsionek_A", "KUL", (13.7, 12.45), 1.2), ("przedsionek_A", "KW.S.03", (15.5, 16.6), 1.2),
    ("przedsionek_B", "KUL", (27.0, 9.9), 1.2),
]
DOORS_ANT = [
    ("KW.A.01", "KW.A.02", (32.9, 10.1), 1.6),
    ("PHS.05c", "KW.A.01", (34.8, 5.3), 1.0),
    ("SWD.01g", "KW.A.02", (17.5, 12.45), 1.6),    # wejście na galerię (drzwi EI 30 S, otwarte przy sesji)
    ("przedsionek_A", "SWD.01g", (15.5, 15.6), 1.2),   # 2. droga z galerii → klatka A
    ("przedsionek_B", "KW.A.02", (27.0, 9.9), 1.2),    # 1. droga z galerii → klatka B
    ("KW.A.03", "SWD.02g", (6.3, 14.5), 1.2),          # przedsionek A' – 2. droga z górnego holu
    ("klatka_A", "KW.A.03", (8.43, 14.5), 1.2),
]

# ------------------------------------------------------------------------------------------------
# Sala obrad – ognisko, prezydium, rzędy (wynik _s2_sala.py: optymalizacja i kontrola)
# ------------------------------------------------------------------------------------------------
F = (29.0, 14.60)                # ognisko rzędów = mównica (mówca twarzą na pn.)
ROW_R = [4.40, 6.20, 8.00, 9.80]  # promień krawędzi pulpitów (od strony prezydium)
ROW_Z = [0.00, 0.12, 0.24, 0.36]  # poziom podestów rzędów (wzgl. posadzki sali +27,30)
BAND_IN, BAND_OUT = -0.05, 1.45   # pas rzędu: pulpit 0,60 + siedzisko/przejście 0,85 (+0,05)
CHAIR_OFF = 0.90                  # linia oparć/oczu radnego od krawędzi pulpitu
DESK_W = 1.00                     # moduł stanowiska na linii siedzisk [m]
WC_W = 1.50                       # moduł stanowiska dla wózka (0,9 × 1,4 + pole manewru wspólne z podestem)
LAND = 1.50                       # podest pochylni (WT § 71)
RAMP_RISE = 0.12
RAMP_SLOPE = 0.05
RAMP_L = RAMP_RISE / RAMP_SLOPE   # 2,40 m
STEP_W = 0.90                     # schody w przejściu wsch. (stopień 0,12)
PRES = box(F[0] - 3.0, 12.70, F[0] + 3.0, 14.20)       # stół prezydialny 6,0 m (4 os.) z krzesłami
LECTERN = box(F[0] - 0.6, F[1] - 0.25, F[0] + 0.6, F[1] + 0.35)   # mównica regulowana 0,75–1,20 m


def sector(F_, r0, r1, a0, a1, n=48):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((F_[0] + r0 * math.cos(a), F_[1] + r0 * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((F_[0] + r1 * math.cos(a), F_[1] + r1 * math.sin(a)))
    return Polygon(pts)


def row_zone():
    """Obszar dopuszczalny dla rzędów: sala minus strefa prezydium/mównicy, przejście zach. 1,2 m, reżyserka."""
    z = INNER.intersection(SALA_BOX).difference(SWD04_BOX.buffer(0.20, join_style=2))
    z = z.difference(box(F[0] - 3.6, 12.6, F[0] + 3.6, F[1] + 0.6))
    z = z.difference(box(22.0, 12.6, 23.2, 29.2))           # przejście zach. przy ścianie sali (wejście z holu)
    z = z.difference(INNER.difference(INNER.buffer(-0.6)))   # 0,6 m od szkła i ścian zewn.
    return z


def build_rows():
    """Rzędy: na końcach wsch. schodki (przejście wsch.), na końcach zach. sekwencja
    [stanowiska | miejsce dla wózka | podest | pochylnia 5 % | podest niższy] – podest niższy rzędu k
    leży promieniowo przy podeście górnym rzędu k−1 (ciąg pochylni bez stopni od posadzki sali do rzędu 4)."""
    zone = row_zone()
    rows = []
    prev_top = None
    for k, (R, z) in enumerate(zip(ROW_R, ROW_Z)):
        r0, r1 = R + BAND_IN, R + BAND_OUT
        rm = R + 0.70                 # promień osi pochylni/podestu
        rc = R + CHAIR_OFF            # linia siedzisk
        # granica wsch. – kąt minimalny, przy którym pas mieści się w strefie (+ schodki STEP_W)
        a_e = None
        for a10 in range(60, 900):
            a = a10 / 10
            if sector(F, r0, r1, a, a + 0.5, 4).within(zone):
                a_e = a
                break
        a_e_desk = a_e + math.degrees(STEP_W / rc)
        # granica zach. – kąt maksymalny w strefie
        a_w = None
        for a10 in range(1790, 600, -1):
            a = a10 / 10
            if sector(F, r0, r1, a - 0.5, a, 4).within(zone):
                a_w = a
                break
        if k == 0:
            a_wc_end = a_w                          # rząd 1 na posadzce: miejsce dla wózka na końcu zach.
        else:
            # podest niższy tego rzędu ma się pokrywać kątowo z podestem górnym rzędu poprzedniego
            a_bottom_end = min(a_w, prev_top[1])
            a_ramp_end = a_bottom_end - math.degrees(LAND / rm)
            a_ramp_start = a_ramp_end - math.degrees(RAMP_L / rm)
            a_top_start = a_ramp_start - math.degrees(LAND / rm)
            a_wc_end = a_top_start
        a_wc_start = a_wc_end - math.degrees(WC_W / rc)
        n = int(math.floor((math.radians(a_wc_start - a_e_desk) * rc) / DESK_W + 1e-9))
        a_desk_end = a_e_desk + math.degrees(n * DESK_W / rc)
        row = dict(k=k + 1, R=R, z=z, a_east=a_e, a_desk0=a_e_desk, a_desk1=a_desk_end,
                   a_wc=(a_wc_start, a_wc_end), n_desks=n, rc=rc)
        row["band"] = sector(F, r0, r1, a_e, a_wc_end if k == 0 else a_bottom_end)
        row["wc"] = sector(F, r0, r1, a_wc_start, a_wc_end)
        row["desks"] = sector(F, R, R + 0.60, a_e_desk, a_desk_end)
        if k == 0:
            row["top_landing"] = (a_wc_start, a_wc_end)   # miejsce dla wózka = podest (poziom posadzki)
            row["ramp"] = None
        else:
            row["top_landing"] = (a_top_start, a_ramp_start)
            row["ramp"] = sector(F, r0 + 0.10, r0 + 1.30, a_ramp_start, a_ramp_end)
            row["ramp_angles"] = (a_ramp_start, a_ramp_end)
            row["bottom_landing"] = (a_ramp_end, a_bottom_end)
            row["ramp_len"] = math.radians(a_ramp_end - a_ramp_start) * rm
        prev_top = row["top_landing"]
        rows.append(row)
    return rows


# ------------------------------------------------------------------------------------------------
# Program (program.yaml) i opis pomieszczeń
# ------------------------------------------------------------------------------------------------
PROG = {   # kod: (nazwa, kategoria, program_m2, zakres)
    "SWD.01": ("Sala obrad – płyta (44 stałe stanowiska + prezydium + mównica, media, goście, obsługa, PJM)", "sala", 320, (280, 380)),
    "SWD.01g": ("Galeria publiczności (część SWD.01): 3 rzędy, 31 miejsc + 3 dla wózków", "sala", None, None),
    "SWD.02": ("Hol reprezentacyjny – poziom dolny (pustka 2-kond. NW, okna pn. i zach., hol dźwigów A1/A2)", "hol", 150, (120, 220)),
    "SWD.02g": ("Hol reprezentacyjny – poziom górny (antresola holu nad klubami i pasem pn.)", "hol", None, None),
    "SWD.03": ("Sala multimedialna / poczekalnia gości – strefa otwarta na antresoli holu (ekran, głośniki kierunkowe, pętla)", "antresola", 40, (30, 60)),
    "SWD.04": ("Reżyserka – nagrywanie i transmisja (przeszklenie na prezydium i rzędy)", "zamk", 20, (15, 30)),
    "SWD.05": ("Przestrzeń socjalno-gastronomiczna (bar z przyłączami) na antresoli holu", "antresola", 40, (30, 60)),
    "SWD.06": ("Szatnia strefy Sejmiku – lada 4,8 m + wieszaki", "hol", 15, (12, 20)),
    "SWD.07": ("Pokój matki z dzieckiem", "zamk", 10, (8, 12)),
    "SWD.08": ("Sala komisji 50 os.", "zamk", 100, (90, 120)),
    "SWD.09": ("Sala komisji 30 os.", "zamk", 60, (54, 72)),
    "SWD.10a": ("Zaplecze nagrań komisji 50 os. (okno do SWD.08)", "zamk", 10, (8, 12)),
    "SWD.10b": ("Zaplecze nagrań komisji 30 os. (okno do SWD.09)", "zamk", 10, (8, 12)),
    "SWD.11a": ("Sala klubu radnych 30 os. (1)", "zamk", 60, (54, 72)),
    "SWD.11b": ("Sala klubu radnych 30 os. (2)", "zamk", 60, (54, 72)),
    "SWD.12a": ("Sala klubu radnych 15 os. (1)", "zamk", 36, (30, 40)),
    "SWD.12b": ("Sala klubu radnych 15 os. (2)", "zamk", 36, (30, 40)),
    "SWD.13": ("Wspólna sala radnych (okno pn. – Ostrów Tumski)", "zamk", 48, (36, 60)),
    "SWD.14": ("Pokój socjalny radnych (aneks kuchenny)", "zamk", 24, (20, 30)),
    "SWD.15": ("Magazyn podręczny strefy Sejmiku (pod biegiem schodów)", "zamk", 10, (6, 15)),
    "PHS.05a": ("WC damskie: kabina dostępna 2,2 × 2,5 m + 2 kabiny + umywalki", "zamk", None, None),
    "PHS.05b": ("WC męskie: kabina dostępna 2,2 × 2,5 m + kabina + 2 pisuary + umywalki", "zamk", None, None),
    "PHS.05c": ("Toaleta dostępna publiczności galerii (antresola, przy dźwigach P1/P2)", "zamk", None, None),
    "PP.06": ("Pomieszczenie porządkowe (woda, zlew)", "zamk", 6, (4, 8)),
    "IT.02": ("Punkt dystrybucyjny IT (PD) – przy zapleczach nagrań", "zamk", 6, (4, 10)),
    "KUL": ("Kuluar – korytarz Sejmiku (droga ewakuacyjna EI 30, oddymiany; okna W i E)", "kom", None, None),
    "KW.S.01": ("Pasaż zachodni: kuluar ↔ hol", "kom", None, None),
    "KW.S.02": ("Dojście do SWD.11b, przystanek służbowy P2", "kom", None, None),
    "KW.S.03": ("Łącznik wschodni: kuluar ↔ hol, drzwi przedsionka A", "kom", None, None),
    "KW.S.04": ("Schody reprezentacyjne S → antresola (niższa część biegu)", "kom", None, None),
    "KW.A.01": ("Hol dźwigów publicznych P1/P2 (antresola)", "kom", None, None),
    "KW.A.02": ("Korytarz publiczny nad kuluarem (EI 30) – dojście z P1/P2 na galerię, do klatek A i B", "kom", None, None),
    "KW.A.03": ("Przedsionek ppoż. A' klatki A (antresola zach.) z MOE 1,5 × 1,5", "kom", None, None),
}
PHS05_PROG = (45, (35, 60))


def poly_list_uv(g, nd=3):
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    out = []
    for p in gs:
        p = p.simplify(0.0005)
        out.append([[round(x, nd), round(y, nd)] for x, y in list(p.exterior.coords)[:-1]])
    return out


def poly_list_en(g, nd=3):
    return [[[round(c, nd) for c in uv2en(x, y)] for x, y in ring] for ring in poly_list_uv(g, 6)]


if __name__ == "__main__":
    import _s2_export  # noqa: F401  (eksport i kontrole w osobnym module)
