# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 (+27,30) z antresolą (+30,90) – model geometryczny (wariant S-3 „hol z galerią”).

Jedno źródło geometrii dla skryptów _s2_*.py. Uruchomienie z katalogu umwd/:
    python3 docs/20_koncepcja/_s2_model.py        → zapisuje docs/20_koncepcja/kondygnacja_S2.json i drukuje kontrole

Układ (u, v) wieży wg model/koncepcja.json:
    e = 74,606 + 0,97155·u − 0,23684·v ;  n = 40,756 + 0,23684·u + 0,97155·v
    prostokąt u 0–40 × v 0–29,7 + łuk R 14,0 (środek u 26,0; v 15,7) w narożu NE; lico wewnętrzne ścian zewn. 0,50 m.
Trzony: A u 8,30–15,50 × v 11,85–20,85 (v1.2 – wydłużony o 0,60 m na pd. wg I5: klatka A 3,40 × 5,80 m);
B u 24,85–31,10 × v 0,50–9,90 (obrys bez zmian; v1.2 – klatka B 3,40 × 6,64 m, przedsionek B 3,40 × 2,06 m).
Dowód biegów i wpływu na kondygnacje: _v12_trzony.py.
v1.2 – poprawki po weryfikacji scalenia (17.11.2026): schody reprezentacyjne w całości w pustce (otwór w antresoli nad biegiem,
spocznik 1,50 m, płaskie pole 1,53 m przed stopą), galeria z zatoką +0,00 dla wózków i podestem rzędu 2 z przejściem tylnym,
przedsionek A' 2,50 × 3,00 m, drzwi przedsionka B w u 27,80, korytarz publiczny przedłużony do przedsionka A (2 kierunki na +30,90),
PHS.05c na wsch. końcu korytarza publicznego, PP.06 i SWD.07 zamienione (dojścia ≤ 10 m bez zwiększeń), drzwi SWD.12a w u 5,70.
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

CORE_A = box(8.30, 11.85, 15.50, 20.85)      # v1.2 (I5): ściana pd. trzonu 0,20 m na v 11,85–12,05
CORE_B = box(24.85, 0.50, 31.10, 9.90)

# Rzędne
Z_S = 27.30
Z_ANT = 30.90
Z_SPOD_DACHU = 34.15            # spód kratownic (pas dolny) = 6,85 m nad S
H_SALA = Z_SPOD_DACHU - Z_S
H_POD_ANT = 3.30                # spód płyty antresoli nad posadzką S (płyta 0,30 m)

# ------------------------------------------------------------------------------------------------
# Schody reprezentacyjne S → +30,90 (v1.2-fix): prosty bieg 2,0 m w pustce holu, wznoszący się ku zach.
# 21 st. × 17,14 cm (11 + 10), 19 stopnic × 0,28 + spocznik 1,50 m = 6,82 m; stopa (S) na wsch., wierzch (+30,90) na zach.
# ------------------------------------------------------------------------------------------------
STAIR_V = (24.60, 26.60)
STAIR_STEPS = (11, 10)
STAIR_TREAD = 0.28
STAIR_LAND = 1.50
STAIR_RISE = (Z_ANT - Z_S) / sum(STAIR_STEPS)
STAIR_RUN = (sum(STAIR_STEPS) - 2) * STAIR_TREAD + STAIR_LAND     # 6,82 m
STAIR_TOP_U = 4.10                                                # wierzch biegu = krawędź podestu górnego (+30,90)
STAIR_FOOT_U = round(STAIR_TOP_U + STAIR_RUN, 3)                  # stopa biegu na S (u 10,92)
HALL_E_WALL_U = 12.45                                             # ściana wsch. holu (SWD.14 od u 12,65)
STAIR = box(STAIR_TOP_U, STAIR_V[0], STAIR_FOOT_U, STAIR_V[1])    # rzut całego biegu
STAIR_S = box(5.10, STAIR_V[0], STAIR_FOOT_U, STAIR_V[1])         # rzut części z pomieszczeniami pod biegiem (SWD.15 + KW.S.04)
STAIR_OPEN = box(8.30, STAIR_V[0], STAIR_FOOT_U, 27.85)          # otwór w antresoli nad biegiem (łączy się z pustką holu)
PODEST_ANT = box(1.85, 23.30, 5.10, 26.60).difference(box(STAIR_TOP_U, STAIR_V[0], 5.10, STAIR_V[1]))   # podest górny


def stair_nosing(u):
    """Wysokość linii krawędzi stopni nad posadzką S w punkcie u biegu (None poza biegiem)."""
    x = STAIR_FOOT_U - u
    if x < -1e-9 or x > STAIR_RUN + 1e-9:
        return None
    n1, n2 = STAIR_STEPS
    f1 = (n1 - 1) * STAIR_TREAD
    if x <= f1:
        return STAIR_RISE * (1 + x / STAIR_TREAD)
    if x <= f1 + STAIR_LAND:
        return STAIR_RISE * n1
    return min(STAIR_RISE * (n1 + 1 + (x - f1 - STAIR_LAND) / STAIR_TREAD), STAIR_RISE * (n1 + n2))


def stair_walk_length():
    """Długość drogi po biegu (po pochyleniu biegów + spocznik)."""
    n1, n2 = STAIR_STEPS
    return (math.hypot((n1 - 1) * STAIR_TREAD, n1 * STAIR_RISE) + STAIR_LAND
            + math.hypot((n2 - 1) * STAIR_TREAD, n2 * STAIR_RISE))

# ------------------------------------------------------------------------------------------------
# Trzony – układ wewnętrzny v1.2 (scalenie S-3 z poprawką I5; dowód: _v12_trzony.py)
# ------------------------------------------------------------------------------------------------
CORE_A_CELLS = {
    "A1": box(8.55, 18.05, 10.80, 20.60),      # szyb 2,25 × 2,55 (kabina 1,5 × 2,1; 1 600 kg), drzwi N
    "A2": box(11.00, 18.05, 13.25, 20.60),     # jw.
    "R": box(13.45, 18.05, 15.25, 20.60),      # szyb 1,80 × 2,55 (kabina 1,1 × 2,1; 1 000 kg), drzwi S do przedsionka
    "klatka_A": box(8.55, 12.05, 11.95, 17.85),           # 3,40 × 5,80: 2 biegi 1,60 × 10 st. 0,28 + spoczniki 1,50
    "przedsionek_A": box(12.15, 12.05, 15.25, 17.85),     # 3,10 × 5,80 (MOE 1,5 × 1,5; drzwi R, kuluar/hol, klatka)
}
CORE_B_CELLS = {
    "klatka_B": box(25.10, 0.75, 28.50, 7.39),            # 3,40 × 6,64: 2 biegi na każdej kondygnacji (P: 2 × 14 st.)
    "przedsionek_B": box(25.10, 7.59, 28.50, 9.65),       # 3,40 × 2,06 (MOE 1,5 × 1,5 przy ścianie zach.)
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
    # v1.2-fix: PP.06 i SWD.07 zamienione – drzwi obu przy zach. końcu (u ≤ 35,2): dojście do przedsionka B ≤ 10 m bez zwiększeń
    R["PP.06"] = box(32.90, 7.30, 34.50, 9.90)        # 1,60 × 2,60 (zlew, wózek porządkowy)
    R["SWD.07"] = box(34.70, 7.45, 39.50, 9.90)       # 4,80 × 2,45 (okna wsch.)
    # kuluar (droga ewakuacyjna, EI 30, oddymiany)
    R["KUL"] = unary_union([box(0.50, 10.10, 39.50, 12.30).difference(CORE_A),   # v1.2: przy trzonie A 1,75 m (v 10,10–11,85)
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
    # schody reprezentacyjne S → ANT (STAIR): bieg 2,0 m, 11 + 10 st., spocznik 1,50; górny bieg nad szatnią (prześwit ≥ 2,8 m)
    R["SWD.15"] = box(5.10, STAIR_V[0], 8.10, STAIR_V[1])     # magazyn podręczny pod spocznikiem i górnym biegiem (h 1,7–2,6 m)
    R["KW.S.04"] = box(8.10, STAIR_V[0], STAIR_FOOT_U, STAIR_V[1])   # dolny bieg (otwarty); przed stopą płaskie pole do u 12,45
    R["SWD.02"] = hall.difference(R["SWD.06"]).difference(STAIR_S)
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
    A["PHS.05c"] = box(34.90, 10.10, 37.40, 12.30)                     # v1.2-fix: toaleta dostępna na wsch. końcu korytarza (nad kuluarem)
    A["KW.A.02"] = unary_union([box(15.50, 10.10, 34.70, 12.30),       # korytarz publiczny nad kuluarem (EI 30)
                                box(24.85, 9.90, 31.10, 10.10),         # przed przedsionkiem B (+30,90)
                                box(12.15, 10.10, 15.50, 11.85)])       # v1.2-fix: odcinek zach. do drzwi przedsionka A (+30,90)
    gal = box(15.50, 12.60, 22.00, 22.65)
    A["SWD.01g"] = gal                                                 # galeria publiczności (część SWD.01)
    # strefa radnych – górny hol (antresola holu), wycofana 1,35 m od elewacji zach. i pn.
    west = unary_union([box(1.85, 12.50, 8.30, 23.30), PODEST_ANT])    # + podest górny schodów (do wierzchu biegu u 4,10)
    lobby = box(8.30, 20.85, 12.45, 27.85)
    north = box(12.45, 22.65, 21.70, 27.85)
    band = box(12.45, 20.85, 15.30, 22.65)
    antw = unary_union([west, lobby, north, band]).difference(STAIR_OPEN)   # v1.2-fix: otwór nad biegiem schodów
    A["SWD.05"] = box(15.30, 22.85, 21.70, 27.85)                      # bar / przestrzeń socjalno-gastronomiczna
    A["KW.A.03"] = box(5.80, 12.50, 8.30, 15.50)                       # przedsionek ppoż. A' 2,50 × 3,00 (v1.2-fix: MOE poza torem)
    A["SWD.03"] = box(1.85, 12.50, 6.30, 20.10).difference(A["KW.A.03"])   # strefa multimedialna / poczekalnia gości
    A["SWD.02g"] = antw.difference(A["SWD.05"]).difference(A["SWD.03"]).difference(A["KW.A.03"]) \
        .difference(box(15.30, 22.65, 21.70, 22.85))                   # pas ściany galeria/bar
    return A


VOID_HALL = (box(0.50, 23.30, 8.30, 29.20).union(box(8.30, 27.85, 12.45, 29.20)).union(STAIR_OPEN)
             .difference(PODEST_ANT))                         # pustka holu (2 kond.) z biegiem schodów w całości (v1.2-fix)

# ------------------------------------------------------------------------------------------------
# Drzwi (u, v, szerokość, pomieszczenie → komunikacja). Punkt = środek otworu na osi ściany.
# ------------------------------------------------------------------------------------------------
DOORS_S = [
    ("SWD.08", "KUL", (4.0, 10.0), 1.6), ("SWD.08", "KUL", (8.0, 10.0), 1.0),
    ("SWD.10a", "KUL", (10.25, 10.0), 0.9), ("SWD.10b", "KUL", (12.35, 10.0), 0.9),
    ("IT.02", "KUL", (14.45, 10.0), 0.9), ("SWD.09", "KUL", (17.0, 10.0), 1.0),
    ("SWD.11a", "KUL", (21.0, 10.0), 1.0), ("SWD.11a", "KUL", (24.0, 10.0), 1.0),
    ("SWD.11b", "KW.S.02", (31.9, 7.2), 1.0), ("KW.S.02", "KUL", (31.9, 10.0), 1.2),
    ("PP.06", "KUL", (33.70, 10.0), 0.9), ("SWD.07", "KUL", (35.20, 10.0), 0.9),     # v1.2-fix: zamiana PP.06 ↔ SWD.07
    ("SWD.12a", "KUL", (5.70, 12.4), 1.0), ("SWD.12b", "KW.S.01", (6.4, 20.3), 1.0),  # v1.2-fix: SWD.12a w u 5,70 (było 3,4)
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
    ("przedsionek_A", "KUL", (13.7, 11.85), 1.2), ("przedsionek_A", "KW.S.03", (15.5, 16.6), 1.2),
    ("przedsionek_B", "KUL", (27.80, 9.9), 1.2),   # v1.2-fix: u 27,80 (było 27,0) – MOE poza torem, dojścia z końca wsch. ≤ 10 m
]
DOORS_ANT = [
    ("KW.A.01", "KW.A.02", (32.9, 10.1), 1.6),
    ("PHS.05c", "KW.A.02", (34.80, 11.20), 0.9),       # v1.2-fix: toaleta na wsch. końcu korytarza publicznego
    ("SWD.01g", "KW.A.02", (17.5, 12.45), 1.6),    # wejście na galerię (drzwi EI 30 S, otwarte przy sesji)
    ("przedsionek_A", "SWD.01g", (15.5, 15.6), 1.2),   # droga z galerii → klatka A
    ("przedsionek_A", "KW.A.02", (13.70, 11.85), 1.2),   # v1.2-fix: korytarz publiczny → klatka A (drugi kierunek na +30,90)
    ("przedsionek_B", "KW.A.02", (27.80, 9.9), 1.2),   # korytarz publiczny → klatka B
    ("KW.A.03", "SWD.02g", (7.70, 15.5), 1.2),         # przedsionek A' – 2. droga z górnego holu (v1.2-fix: u 7,70)
    ("klatka_A", "KW.A.03", (8.43, 13.05), 1.0),       # v1.2-fix: 1,0 m w v 12,55–13,55 (spocznik v 12,05–13,55, A' od v 12,50)
]
# Drzwi przedsionków do klatek (ściana wspólna; spocznik kondygnacyjny) – do testu MOE ([E6]) i [G3]
DOORS_KLATKA = {
    "przedsionek_A": ((12.05, 12.80), 1.2),    # ściana klatka A / przedsionek A (u 11,95–12,15), spocznik v 12,05–13,55
    "przedsionek_B": ((27.80, 7.49), 1.2),     # ściana klatka B / przedsionek B (v 7,39–7,59), spocznik przy przedsionku
    "KW.A.03": ((8.43, 13.05), 1.0),           # A' → klatka A (+30,90)
}


def _door_side(room, u, v, tol=0.32):
    """Ściana pomieszczenia z otworem: (orientacja 'h'/'v', współrzędna lica wewn., kierunek do wnętrza ±1)."""
    x0, y0, x1, y1 = room.bounds
    for orient, coord, val, sgn in (("h", y0, v, 1), ("h", y1, v, -1), ("v", x0, u, 1), ("v", x1, u, -1)):
        if abs(val - coord) <= tol and (x0 - 1e-6 <= u <= x1 + 1e-6 if orient == "h" else y0 - 1e-6 <= v <= y1 + 1e-6):
            return orient, coord, sgn
    return None


def moe_search(room, doors_in, door_out, step=0.05, size=1.5, tor_w=1.2):
    """MOE size × size w pomieszczeniu (przedsionku) poza torem ewakuacji tor_w (prosta od drzwi wejściowych do drzwi klatki)
    i poza polem otwierania skrzydeł drzwi wejściowych (skrzydło = szerokość otworu, otwierane do przedsionka – kierunek
    ewakuacji; drzwi do klatki otwierane do klatki). Przeszukuje układy zawiasów; zwraca dict (pozycja MOE, zawiasy, przeszkody)
    albo None."""
    import itertools
    def inner_pt(u, v, w):
        o, c, sg = _door_side(room, u, v)
        return ((u, c) if o == "h" else (c, v)), o, c, sg
    (uo, vo), wo = door_out
    p_out, *_ = inner_pt(uo, vo, wo)
    tors = []
    for (u, v), w in doors_in:
        p_in, *_ = inner_pt(u, v, w)
        tors.append(LineString([p_in, p_out]).buffer(tor_w / 2, cap_style=2).intersection(room))
    tor = unary_union(tors)
    best = None
    for hinges in itertools.product((-1, 1), repeat=len(doors_in)):
        sw = []
        for ((u, v), w), hg in zip(doors_in, hinges):
            _, o, c, sg = inner_pt(u, v, w)
            if o == "h":
                H = (u + hg * w / 2, c)
                quad = box(u - w / 2, min(c, c + sg * w), u + w / 2, max(c, c + sg * w))
            else:
                H = (c, v + hg * w / 2)
                quad = box(min(c, c + sg * w), v - w / 2, max(c, c + sg * w), v + w / 2)
            sw.append(Point(H).buffer(w, resolution=64).intersection(quad))
        obst = unary_union([tor] + sw)
        x0, y0, x1, y1 = room.bounds
        nx, ny = int((x1 - x0 - size) / step + 1e-6) + 1, int((y1 - y0 - size) / step + 1e-6) + 1
        for i in range(max(nx, 0)):
            for j in range(max(ny, 0)):
                sq = box(x0 + i * step, y0 + j * step, x0 + i * step + size, y0 + j * step + size)
                if sq.within(room.buffer(1e-6)) and sq.intersection(obst).area < 1e-6:
                    best = dict(moe=sq, hinges=hinges, tor=tor, swings=unary_union(sw))
                    return best
    return best


def przedsionki():
    """Przedsionki S i +30,90 z drzwiami do testu MOE: {nazwa: (pomieszczenie, [((u, v), szer.) drzwi wejściowe], drzwi do klatki)}."""
    cA, cB = CORE_A_CELLS["przedsionek_A"], CORE_B_CELLS["przedsionek_B"]
    A_ = level_ANT()
    def din(name, doors):
        return [(p, w) for a, b, p, w in doors if name in (a, b) and "klatka" not in (a + b)]
    return {
        "A (S)": (cA, din("przedsionek_A", DOORS_S), DOORS_KLATKA["przedsionek_A"]),
        "A (+30,90)": (cA, din("przedsionek_A", DOORS_ANT), DOORS_KLATKA["przedsionek_A"]),
        "A' (+30,90)": (A_["KW.A.03"], din("KW.A.03", DOORS_ANT), DOORS_KLATKA["KW.A.03"]),
        "B (S)": (cB, din("przedsionek_B", DOORS_S), DOORS_KLATKA["przedsionek_B"]),
        "B (+30,90)": (cB, din("przedsionek_B", DOORS_ANT), DOORS_KLATKA["przedsionek_B"]),
    }

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
AISLE_W = 1.30                    # przejścia-pochylnie: płaszczyzna ruchu 1,20 m między krawężnikami 0,07 m; poręcze 0,75/0,90
AISLE_HANDRAIL = 1.05             # rozstaw poręczy w świetle (WT § 71 ust. 1: 1,0–1,1 m)
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
    "SWD.01": ("Sala obrad – płyta (47 stałych stanowisk = 43 + 4 dla wózków; wymagane 44; prezydium, mównica, media, goście,"
               " obsługa, PJM)", "sala", 320, (280, 380)),
    "SWD.01g": ("Galeria publiczności (część SWD.01) – opis z gallery_layout() niżej", "sala", None, None),
    "SWD.02": ("Hol reprezentacyjny – poziom dolny (pustka 2-kond. NW, okna pn. i zach., hol dźwigów A1/A2)", "hol", 150, (120, 220)),
    "SWD.02g": ("Hol reprezentacyjny – poziom górny (antresola holu nad klubami i pasem pn.)", "hol", None, None),
    "SWD.03": ("Sala multimedialna / poczekalnia gości – strefa otwarta na antresoli holu (ekran, głośniki kierunkowe, pętla)", "antresola", 40, (30, 60)),
    "SWD.04": ("Reżyserka – nagrywanie i transmisja (przeszklenie na prezydium i rzędy)", "zamk", 20, (15, 30)),
    "SWD.05": ("Przestrzeń socjalno-gastronomiczna (bar z przyłączami) na antresoli holu", "antresola", 40, (30, 60)),
    "SWD.06": ("Szatnia strefy Sejmiku – lada 4,1 m + wieszaki (otwarta na hol)", "hol", 15, (12, 20)),
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
    "SWD.15": ("Magazyn podręczny strefy Sejmiku (pod spocznikiem i górnym biegiem schodów, h 1,7–2,6 m)", "zamk", 10, (6, 15)),
    "PHS.05a": ("WC damskie: kabina dostępna 2,2 × 2,5 m + 2 kabiny + umywalki", "zamk", None, None),
    "PHS.05b": ("WC męskie: kabina dostępna 2,2 × 2,5 m + kabina + 2 pisuary + umywalki", "zamk", None, None),
    "PHS.05c": ("Toaleta dostępna publiczności galerii (antresola, wsch. koniec korytarza publicznego, przy holu P1/P2)", "zamk", None, None),
    "PP.06": ("Pomieszczenie porządkowe (woda, zlew)", "zamk", 6, (4, 8)),
    "IT.02": ("Punkt dystrybucyjny IT (PD) – przy zapleczach nagrań", "zamk", 6, (4, 10)),
    "KUL": ("Kuluar – korytarz Sejmiku (droga ewakuacyjna EI 30, oddymiany; okna W i E)", "kom", None, None),
    "KW.S.01": ("Pasaż zachodni: kuluar ↔ hol", "kom", None, None),
    "KW.S.02": ("Dojście do SWD.11b, przystanek służbowy P2", "kom", None, None),
    "KW.S.03": ("Łącznik wschodni: kuluar ↔ hol, drzwi przedsionka A", "kom", None, None),
    "KW.S.04": ("Schody reprezentacyjne S → antresola (dolny bieg; cały bieg w pustce holu)", "kom", None, None),
    "KW.A.01": ("Hol dźwigów publicznych P1/P2 (antresola)", "kom", None, None),
    "KW.A.02": ("Korytarz publiczny nad kuluarem (EI 30) – dojście z P1/P2 na galerię, do przedsionków A i B", "kom", None, None),
    "KW.A.03": ("Przedsionek ppoż. A' klatki A (antresola zach.) 2,50 × 3,00 z MOE 1,5 × 1,5", "kom", None, None),
}
PHS05_PROG = (45, (35, 60))


def _no_holes(p):
    """Wielokąt z otworem (np. hol SWD.02 wokół schodów) → części bez otworów (cięcie pionowe przez otwór); pole bez zmian."""
    from shapely.ops import split
    if not p.interiors:
        return [p]
    hx = Polygon(p.interiors[0]).centroid.x
    mnx, mny, mxx, mxy = p.bounds
    parts = split(p, LineString([(hx, mny - 1.0), (hx, mxy + 1.0)]))
    out = []
    for q in parts.geoms:
        out += _no_holes(q)
    return out


def poly_list_uv(g, nd=3):
    gs = [g] if g.geom_type == "Polygon" else list(g.geoms)
    gs = [q for p in gs for q in _no_holes(p)]          # v1.2: JSON zapisuje tylko pierścienie zewnętrzne – bez otworów
    out = []
    for p in gs:
        p = p.simplify(0.0005)
        out.append([[round(x, nd), round(y, nd)] for x, y in list(p.exterior.coords)[:-1]])
    return out


def poly_list_en(g, nd=3):
    return [[[round(c, nd) for c in uv2en(x, y)] for x, y in ring] for ring in poly_list_uv(g, 6)]


# ------------------------------------------------------------------------------------------------
# Galeria publiczności (+30,90) – v1.2-fix: przekrój 2-rzędowy z zatoką +0,00 dla wózków (pn.) i przejściem tylnym rzędu 2
# ------------------------------------------------------------------------------------------------
# Przekrój (wsch. → zach.): balustrada (lico u 22,00; szkło 21,90–22,00) | rząd 1 +0,00 u 20,90–21,90 (siedzisko 0,50 +
# przejście 0,45 przed kolanami) | podest +0,90 u 19,10–20,90 (miejsca rzędu 2 u 20,10–20,90, przejście tylne 1,00 m) | foyer +0,00.
# Wzdłuż (pd. → pn.): przejście +0,00 do rzędu 1 (0,90) | podest i rząd 1 | zatoka +0,00: 3 × (opiekun + wózek) przy balustradzie.
GAL = box(15.50, 12.60, 22.00, 22.65)
GAL_PARAPET_U = (21.90, 22.00)    # balustrada szklana 1,10 m (prześwit ≤ 0,12) na cokole pełnym 0,20 m – lico u 22,00
GAL_CURB_H = 0.20                 # cokół pełny (dolna część balustrady)
GAL_GLASS_H = 1.10                # wysokość balustrady nad posadzką galerii (WT § 298 ust. 2)
GAL_IN = box(GAL.bounds[0], GAL.bounds[1], GAL_PARAPET_U[0], GAL.bounds[3])   # wnętrze galerii do lica szkła
GAL_SEAT_W = 0.52                 # szerokość miejsca
GAL_SEAT_D = 0.50                 # głębokość siedziska z oparciem
GAL_KNEE = 0.45                   # przejście przed kolanami rzędu 1 (WT § 261 jako zasada przyjęta – odstęp 0,45)
GAL_WC_W, GAL_WC_D = 0.90, 1.40   # miejsce dla wózka (M.13)
GAL_EYE_OFF = 0.30                # oko siedzącego przed linią oparcia
GAL_R1_U = (20.90, 21.90)         # rząd 1 (+0,00)
GAL_R2_U = (20.10, 20.90)         # miejsca rzędu 2 na podeście: siedzisko 0,50 + miejsce na nogi 0,30 do krawędzi
GAL_PODEST_DZ = 0.90
GAL_PODEST = box(19.10, 13.50, 20.90, 18.30)            # podest +0,90 (przejście tylne 1,00 m u 19,10–20,10)
GAL_S_PASS = box(19.10, 12.60, GAL_PARAPET_U[0], 13.50)  # przejście +0,00 foyer → rząd 1 (0,90 m)
GAL_STEPS = [box(17.30, 13.60, 19.10, 14.60)]           # 6 × 0,15 / 0,30 z foyer na przejście tylne podestu
GAL_BAY = box(19.10, 18.30, GAL_PARAPET_U[0], 22.65)    # zatoka +0,00 (z foyer bez stopni)
GAL_BAY_ORDER = ("opiekun", "wozek") * 3                 # od pd. przy balustradzie
GAL_BAY_V0 = 18.35
GAL_ONE_SIDE_MAX = 8              # rząd z dostępem z jednej strony – maks. miejsc (§ 261 – zasada przyjęta)
GAL_PODEST_BAR_H = 0.70           # balustrada szklana na krawędzi podestu przed miejscami rzędu 2 (WT § 298 ust. 7)


def gallery_layout():
    """Miejsca galerii: słownik list {typ: [(u_oka, v_środka, h_oka nad S, prostokąt rzutu)]} + elementy przekroju."""
    h0 = (Z_ANT - Z_S) + EYE
    out = {"rzad1": [], "rzad2": [], "opiekun": [], "wozek": []}
    # zatoka: opiekun + wózek przy balustradzie
    v = GAL_BAY_V0
    for t in GAL_BAY_ORDER:
        w = GAL_WC_W if t == "wozek" else GAL_SEAT_W
        if t == "wozek":
            rect = box(GAL_PARAPET_U[0] - GAL_WC_D, v, GAL_PARAPET_U[0], v + w)
            ue = GAL_PARAPET_U[0] - 0.70
        else:
            rect = box(GAL_R1_U[0], v, GAL_R1_U[0] + GAL_SEAT_D, v + w)
            ue = GAL_R1_U[0] + GAL_EYE_OFF
        out[t].append((ue, v + w / 2, h0, rect))
        v += w
    # rząd 1 (+0,00): od przejścia pd. do zatoki, dostęp tylko od pd. → maks. GAL_ONE_SIDE_MAX
    v0, v1 = GAL_PODEST.bounds[1], GAL_PODEST.bounds[3]
    n1 = min(int((v1 - v0 + 1e-9) // GAL_SEAT_W), GAL_ONE_SIDE_MAX)
    for i in range(n1):
        vc = v0 + (i + 0.5) * GAL_SEAT_W
        out["rzad1"].append((GAL_R1_U[0] + GAL_EYE_OFF, vc, h0,
                             box(GAL_R1_U[0], vc - GAL_SEAT_W / 2, GAL_R1_U[0] + GAL_SEAT_D, vc + GAL_SEAT_W / 2)))
    # rząd 2 (+0,90): każde miejsce z przejścia tylnego
    n2 = int((v1 - v0 + 1e-9) // GAL_SEAT_W)
    for i in range(n2):
        vc = v0 + (i + 0.5) * GAL_SEAT_W
        out["rzad2"].append((GAL_R2_U[0] + GAL_EYE_OFF, vc, h0 + GAL_PODEST_DZ,
                             box(GAL_R2_U[0], vc - GAL_SEAT_W / 2, GAL_R2_U[0] + GAL_SEAT_D, vc + GAL_SEAT_W / 2)))
    return out


def gallery_seats():
    """Zwraca listę miejsc (u oka, v, h oka nad posadzką sali S, typ: miejsce / opiekun / wozek)."""
    L = gallery_layout()
    res = [(u, v, h, "miejsce") for u, v, h, _ in L["rzad1"] + L["rzad2"]]
    res += [(u, v, h, "opiekun") for u, v, h, _ in L["opiekun"]]
    res += [(u, v, h, "wozek") for u, v, h, _ in L["wozek"]]
    return res


_GL = gallery_layout()
GAL_COUNTS = {k: len(v) for k, v in _GL.items()}
GAL_SEATS_N = GAL_COUNTS["rzad1"] + GAL_COUNTS["rzad2"] + GAL_COUNTS["opiekun"]     # miejsca siedzące
GAL_WC_N = GAL_COUNTS["wozek"]
GAL_ROWS = [  # (nr, u oka, podest wzgl. +30,90, v0, v1, układ) – do linii wzroku (_s2_sala.py [S3]) i JSON
    (1, GAL_R1_U[0] + GAL_EYE_OFF, 0.00, GAL_PODEST.bounds[1], GAL_BAY.bounds[3],
     f"+0,00: {GAL_COUNTS['rzad1']} miejsc (dostęp przejściem 0,90 od pd. i przejściem 0,45 przed kolanami) + zatoka pn.:"
     f" {GAL_WC_N} miejsca dla wózków 0,90 × 1,40 z {GAL_COUNTS['opiekun']} miejscami opiekunów"),
    (2, GAL_R2_U[0] + GAL_EYE_OFF, GAL_PODEST_DZ, GAL_PODEST.bounds[1], GAL_PODEST.bounds[3],
     f"podest +0,90: {GAL_COUNTS['rzad2']} miejsc × 0,52 m z przejściem tylnym 1,00 m; 6 stopni 0,15 × 0,30 z foyer;"
     f" krawędzie podestu – balustrady (przód szkło 0,70 m)"),
]
PROG["SWD.01g"] = (f"Galeria publiczności (część SWD.01): rząd 1 +0,00 – {GAL_COUNTS['rzad1']} miejsc, rząd 2 +0,90 –"
                   f" {GAL_COUNTS['rzad2']} miejsc, zatoka +0,00 – {GAL_WC_N} miejsca dla wózków + {GAL_COUNTS['opiekun']} opiekunów"
                   f" ({GAL_SEATS_N} + {GAL_WC_N})", "sala", None, None)


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
