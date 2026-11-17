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
    R["SWD.06"] = box(1.85, 23.30, 4.90, 27.40)               # szatnia: lada 4,1 m + wieszaki, 1,35 m od okna zach.
    STAIR = box(5.10, 24.60, 12.30, 26.60)                    # schody reprezentacyjne S → ANT: bieg 2,0 m, 2 × (10+11 st.) + spocznik
    R["SWD.15"] = box(5.10, 24.60, 8.10, 26.60)               # magazyn podręczny pod wyższą częścią biegu (h 1,8–3,3 m)
    R["KW.S.04"] = box(8.10, 24.60, 12.30, 26.60)             # niższa część biegu (otwarta, stopa schodów od holu dźwigów)
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
    west = unary_union([box(1.85, 12.50, 8.30, 23.30), box(1.85, 23.30, 5.10, 26.60)])   # + podest górny schodów
    lobby = box(8.30, 20.85, 12.45, 27.85)
    north = box(12.45, 22.65, 21.70, 27.85)
    band = box(12.45, 20.85, 15.30, 22.65)
    antw = unary_union([west, lobby, north, band])
    A["SWD.05"] = box(15.30, 22.85, 21.70, 27.85)                      # bar / przestrzeń socjalno-gastronomiczna
    A["SWD.03"] = box(1.85, 12.50, 6.30, 20.10)                        # strefa multimedialna / poczekalnia gości
    A["KW.A.03"] = box(6.30, 12.50, 8.30, 15.50)                       # przedsionek ppoż. A' (wejście do klatki A od zach.)
    A["SWD.02g"] = antw.difference(A["SWD.05"]).difference(A["SWD.03"]).difference(A["KW.A.03"]) \
        .difference(box(15.30, 22.65, 21.70, 22.85))                   # pas ściany galeria/bar
    return A


VOID_HALL = (box(0.50, 23.30, 8.30, 29.20).union(box(8.30, 27.85, 12.45, 29.20))
             .difference(box(1.85, 23.30, 5.10, 26.60)))      # pustka holu (2 kond.) z otworem biegu schodów

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
    ("SWD.01", "KUL", (22.70, 12.45), 1.2),        # wyjście SW (przy przejściu zach.) – do klatki A
    ("SWD.01", "KUL", (32.6, 12.45), 1.6),         # wyjście SE – do klatki B
    ("SWD.01", "KUL", (28.0, 12.45), 1.0),         # drzwi prezydium (za stołem prezydialnym)
    ("SWD.15", "SWD.02", (6.6, 24.6), 0.9),
    ("przedsionek_A", "KUL", (13.7, 12.45), 1.2), ("przedsionek_A", "KW.S.03", (15.5, 16.6), 1.2),
    ("przedsionek_B", "KUL", (27.0, 9.9), 1.2),
]
DOORS_ANT = [
    ("KW.A.01", "KW.A.02", (32.9, 10.1), 1.6),
    ("PHS.05c", "KW.A.01", (34.8, 5.3), 1.0),
    ("SWD.01g", "KW.A.02", (17.5, 12.45), 1.6),    # wejście na galerię (drzwi EI 30 S, otwarte przy sesji)
    ("przedsionek_A", "SWD.01g", (15.5, 15.6), 1.2),   # 2. droga z galerii → klatka A
    ("przedsionek_B", "KW.A.02", (27.0, 9.9), 1.2),    # 1. droga z galerii → klatka B
    ("KW.A.03", "SWD.02g", (7.3, 15.5), 1.2),          # przedsionek A' – 2. droga z górnego holu
    ("klatka_A", "KW.A.03", (8.43, 13.6), 1.2),
]

# ------------------------------------------------------------------------------------------------
# Sala obrad – ognisko, prezydium, rzędy (kontrole: _s2_sala.py)
# ------------------------------------------------------------------------------------------------
F = (27.50, 15.20)                # ognisko rzędów = mównica (mówca twarzą na pn., do radnych i galerii)
ROW_R = [4.50, 6.30, 8.10, 9.90]  # promień krawędzi pulpitów (od strony prezydium)
PITCH = 1.80
RISE = 0.09                       # przewyższenie rzędu = 5 % × 1,80 m → przejścia-pochylnie promieniowe 5 %
ROW_Z = [0.00, 0.09, 0.18, 0.27]  # podesty rzędów (wzgl. posadzki sali +27,30)
BAND_IN, BAND_OUT = -0.05, 1.45   # pas rzędu: pulpit 0,60 + siedzisko i przejście za oparciami 0,85
CHAIR_OFF = 0.90                  # linia siedzisk/oczu radnego od krawędzi pulpitu
EYE = 1.20                        # wysokość oczu siedzącego
DESK_W = 1.00                     # moduł stanowiska na linii siedzisk [m]
WC_W = 1.50                       # moduł stanowiska dla wózka (0,9 × 1,4 + przestrzeń przy przejściu)
AISLE_W = 1.30                    # przejścia-pochylnie (1,20 m w świetle poręczy)
U_FLAT = (22.00, 23.10)           # przejście płaskie przy ścianie zach. sali (drzwi z holu ↔ drzwi SW)
U_RAMP = (23.10, 24.40)           # przejście-pochylnia zach. (wzdłuż ściany), rzędy kończą się na u 24,40
GLASS_OFF = 0.60                  # odsunięcie stanowisk od szkła/ściany zewn.
PRES = box(F[0] - 3.0, 12.70, F[0] + 3.0, 14.25)       # stół prezydialny 6,0 m (4 os.) z krzesłami
LECTERN = box(F[0] - 0.6, F[1] - 0.30, F[0] + 0.6, F[1] + 0.30)   # mównica z blatem regulowanym 0,75–1,20 m


def sector(F_, r0, r1, a0, a1, n=48):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((F_[0] + r0 * math.cos(a), F_[1] + r0 * math.sin(a)))
    for i in range(n, -1, -1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((F_[0] + r1 * math.cos(a), F_[1] + r1 * math.sin(a)))
    return Polygon(pts)


def radial_strip(F_, phi, r0, r1, w):
    a = math.radians(phi)
    d = (math.cos(a), math.sin(a))
    n = (-d[1], d[0])
    p = lambda r, o: (F_[0] + r * d[0] + o * n[0], F_[1] + r * d[1] + o * n[1])
    return Polygon([p(r0, -w / 2), p(r1, -w / 2), p(r1, w / 2), p(r0, w / 2)])


def sala_zone():
    z = INNER.intersection(SALA_BOX).difference(SWD04_BOX.buffer(0.20, join_style=2))
    z = z.difference(box(F[0] - 4.6, 12.6, F[0] + 4.6, 14.85))          # prezydium + obsługa
    z = z.difference(box(F[0] - 3.6, 12.6, F[0] + 3.6, F[1] + 0.6))     # mównica + PJM
    z = z.difference(INNER.difference(INNER.buffer(-GLASS_OFF)))
    return z


def build_rows():
    """4 łukowe rzędy wokół F między dwoma przejściami-pochylniami (≤ 5 %):
    wsch. – promieniowe (szer. 1,30), zach. – wzdłuż ściany sali (u 23,10–24,40).
    Na końcu zach. każdego rzędu stanowisko dla wózka przy punkcie zrównania z pochylnią."""
    zone = sala_zone()
    zone_rows = zone.difference(box(22.0, 12.6, U_RAMP[1], 29.2))
    rmin, rmax = ROW_R[0] - 0.60, ROW_R[-1] + BAND_OUT
    phe = None
    for p10 in range(0, 900):
        ph = p10 / 10
        if radial_strip(F, ph, rmin, ROW_R[-1] + 0.70 + 0.75, AISLE_W).within(zone):
            phe = ph
            break
    east = radial_strip(F, phe, rmin, ROW_R[-1] + 0.70 + 0.75, AISLE_W)
    rows = []
    for k, (R, z) in enumerate(zip(ROW_R, ROW_Z)):
        r0, r1, rc = R + BAND_IN, R + BAND_OUT, R + CHAIR_OFF
        a0 = None
        for p10 in range(int(phe * 10), 1800):
            a = p10 / 10
            if not sector(F, r0, r1, a, a + 0.3, 3).intersects(east.buffer(-0.001)):
                a0 = a
                break
        a1 = None
        for p10 in range(1795, int(a0 * 10), -1):
            a = p10 / 10
            if sector(F, r0, r1, a0, a, 60).within(zone_rows):
                a1 = a
                break
        a_wc0 = a1 - math.degrees(WC_W / rc)
        n = int(math.floor(math.radians(a_wc0 - a0) * rc / DESK_W + 1e-9))
        a_d1 = a0 + math.degrees(n * DESK_W / rc)
        desks = [sector(F, R, R + 0.60, a0 + math.degrees(i * DESK_W / rc), a0 + math.degrees((i + 1) * DESK_W / rc), 6)
                 for i in range(n)]
        seats = [(F[0] + rc * math.cos(math.radians(a0 + math.degrees((i + 0.5) * DESK_W / rc))),
                  F[1] + rc * math.sin(math.radians(a0 + math.degrees((i + 0.5) * DESK_W / rc)))) for i in range(n)]
        am = math.radians((a_wc0 + a1) / 2)
        wc_pt = (F[0] + rc * math.cos(am), F[1] + rc * math.sin(am))
        rows.append(dict(k=k + 1, R=R, z=z, a0=a0, a1=a1, a_desk_end=a_d1, a_wc=(a_wc0, a1), n=n, rc=rc,
                         band=sector(F, r0, r1, a0, a1), desks=desks, seats=seats, wc=sector(F, r0, r1, a_wc0, a1, 8),
                         wc_pt=wc_pt))
    # przejścia
    r4f = ROW_R[-1] + 0.70
    v_hi = F[1] + math.sqrt(max(0.0, (r4f + 0.75) ** 2 - (F[0] - sum(U_RAMP) / 2) ** 2))
    v_lo = F[1] + math.sqrt(max(0.0, (ROW_R[0] + 0.70) ** 2 - (F[0] - sum(U_RAMP) / 2) ** 2)) if (ROW_R[0] + 0.70) > abs(F[0] - sum(U_RAMP) / 2) else F[1] + 0.6
    aisles = dict(east=east, east_phi=phe,
                  west_ramp=box(U_RAMP[0], v_lo - 1.5, U_RAMP[1], v_hi),
                  west_flat=box(U_FLAT[0], 12.60, U_FLAT[1], 29.20 - GLASS_OFF))
    return rows, aisles


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


# ------------------------------------------------------------------------------------------------
# Galeria publiczności (+30,90): 3 rzędy równoległe do ściany sali (u 22,0), stopnie 0,45 m
# ------------------------------------------------------------------------------------------------
GAL_PARAPET_U = (21.90, 22.00)    # balustrada szklana 1,10 m (prześwit ≤ 0,12) na cokole 0,20 m – lico u 22,00
GAL_CURB_H = 0.20                 # cokół pełny
GAL_GLASS_H = 1.10                # wysokość balustrady (WT § 298 ust. 2)
GAL_ROWS = [  # (nr, u oka, podest wzgl. +30,90, v0, v1, układ)
    (1, 21.45, 0.00, 12.85, 22.45, "3 miejsca dla wózków 0,90 × 1,40 + 3 opiekunów + 10 miejsc; kolano przy balustradzie"),
    (2, 20.60, 0.90, 12.85, 22.45, "18 miejsc × 0,52 m na podeście +0,90 (głęb. rzędu 0,85; 6 stopni 0,15 × 0,30 przy końcach)"),
]
GAL_SEAT_W = 0.52
GAL_WC_W = 0.90
GAL_STEPS = [box(18.35, 12.85, 20.15, 13.85), box(18.35, 21.45, 20.15, 22.45)]   # 6 × 0,15 / 0,30 na podest rzędu 2


def gallery_seats():
    """Zwraca listę miejsc (u, v, h_oka nad posadzką sali S, typ)."""
    out = []
    for nr, ue, dz, v0, v1, _ in GAL_ROWS:
        h = (Z_ANT - Z_S) + dz + EYE
        if nr == 1:
            v = v0 + 2.6                         # miejsca dla wózków w pn. części rzędu (lepszy widok na prezydium)
            v = v1 - 3 * (GAL_WC_W + GAL_SEAT_W)
            for i in range(3):                 # wózek + opiekun
                out.append((ue - 0.25, v + GAL_WC_W / 2, h, "wozek"))
                v += GAL_WC_W
                out.append((ue, v + GAL_SEAT_W / 2, h, "opiekun"))
                v += GAL_SEAT_W
            v = v0
            while v + GAL_SEAT_W <= v1 - 3 * (GAL_WC_W + GAL_SEAT_W) + 1e-9:
                out.append((ue, v + GAL_SEAT_W / 2, h, "miejsce"))
                v += GAL_SEAT_W
            continue
        if False:
            v = v0
            for i in range(3):                 # wózek + opiekun
                out.append((ue - 0.25, v + GAL_WC_W / 2, h, "wozek"))
                v += GAL_WC_W
                out.append((ue, v + GAL_SEAT_W / 2, h, "opiekun"))
                v += GAL_SEAT_W
            while v + GAL_SEAT_W <= v1 + 1e-9:
                out.append((ue, v + GAL_SEAT_W / 2, h, "miejsce"))
                v += GAL_SEAT_W
        else:
            n = int((v1 - v0 + 1e-9) // GAL_SEAT_W)
            for i in range(n):
                out.append((ue, v0 + (i + 0.5) * GAL_SEAT_W, h, "miejsce"))
    return out


# Strefy płyty sali poza rzędami (osoby: radni 44 (+3 rezerwy) + prezydium 4 + obsługa 4 + PJM 2 + goście 12 + media 8)
def floor_seats():
    """Miejsca poza rzędami: (u, v, typ). Goście – 2 × 6 w strefie NW za rzędem 4 (przy drzwiach z holu),
    media – 8 na łuku R 11,95 m (φ 58°–80°) za rzędem 4, obsługa kancelaryjna – stół przy prezydium (wsch.),
    tłumacze PJM – przy mównicy (w kadrze kamery)."""
    out = []
    for j, v in enumerate((27.10, 28.10)):
        for i in range(6):
            out.append((23.65 + i * 0.60, v, "gosc"))
    rb = ROW_R[-1] + BAND_OUT + 0.60
    for i in range(8):
        a = math.radians(58.0 + (i + 0.5) * (22.0 / 8))
        out.append((F[0] + rb * math.cos(a), F[1] + rb * math.sin(a), "media"))
    for du in (-4.15, -3.40, 3.40, 4.15):           # obsługa kancelaryjna przy końcach stołu prezydialnego
        out.append((F[0] + du, 13.30, "obsluga"))
    out += [(F[0] - 2.20, 15.20, "PJM"), (F[0] - 1.50, 15.20, "PJM")]
    for i in range(4):
        out.append((F[0] - 2.25 + i * 1.50, 13.25, "prezydium"))
    return out


def floor_zones():
    return {
        "goście (12)": box(23.30, 26.70, 27.30, 28.55),
        "obsługa kancelaryjna (2+2)": box(F[0] - 4.50, 12.70, F[0] - 3.05, 14.25).union(box(F[0] + 3.05, 12.70, F[0] + 4.50, 14.25)),
        "PJM (2)": box(F[0] - 2.60, 14.80, F[0] - 1.10, 15.60),
    }


if __name__ == "__main__":
    S = level_S()
    A = level_ANT()
    rows, aisles = build_rows()
    print("S:", {k: round(v.area, 2) for k, v in S.items()})
    print("ANT:", {k: round(v.area, 2) for k, v in A.items()})
    print("rzędy:", [(r["k"], r["n"]) for r in rows], "wózki:", len(rows))
    print("galeria:", len(gallery_seats()))
