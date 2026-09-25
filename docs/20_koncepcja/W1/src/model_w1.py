# -*- coding: utf-8 -*-
"""Wariant W1 koncepcji „Dom LAMELA” — parametryczny model geometryczny (jedno źródło prawdy wariantu).
Układ: x -> wschód, y -> północ, z -> góra; (0,0) = przecięcie osi A i 1; +-0,00 = posadzka parteru = 101,65 m n.p.m.
Wszystkie rysunki i tabele W1 są generowane z tego modułu."""
from shapely.geometry import box, Polygon, Point, LineString
from shapely.ops import unary_union

# ------------------------------------------------------------------ osie
AX = {"A'": -1.00, 'A': 0.00, 'B': 1.00, 'C': 3.70, 'D': 8.50, 'E': 11.40, 'F': 12.60, 'G': 18.60}
AY = {'1': 0.00, '2': 4.80, '3': 7.30, '4': 10.50}
Y_GAR = 3.80          # ściana garaż | pom. gospodarcze (oś pomocnicza 1a)

# ------------------------------------------------------------------ przegrody (odległości lic od osi warstwy konstr.)
EXT_OUT = 0.30        # SZ1: tynk 0,015 + SIL18 (lub ŻB18) + EPS/MW 0,20 + tynk 0,01 -> lico zewn. = oś + 0,30
EXT_IN = 0.105        # lico wewn. = oś - 0,105
STR = 0.09            # połowa warstwy konstrukcyjnej 18 cm
H_BEAR = 0.105        # ściana wewn. nośna SIL18/ŻB18 + 2x tynk
H_PART = 0.075        # ścianka działowa SIL12 + 2x tynk
GAR_IN = 0.22         # ściana F od strony garażu: SIL18 + MW 12 cm + wypr.

# ------------------------------------------------------------------ poziomy
ZERO_ABS = 101.65
FFL = {'P0': 0.00, 'P1': 3.15, 'P2': 6.30}
H_KOND = 3.15
FLOOR_LAYERS = 0.15
SLABS = {  # id: (spód, wierzch)
    'ST1': (2.78, 3.00), 'ST2': (5.93, 6.15), 'ST3': (9.08, 9.30)}
ROOF_TOP = 9.62          # wierzch pokrycia dachu P2 (śr., spadek 2 %)
ATTIC_TOP = 9.85         # wierzch attyki/okapu dachu P2
GREEN_TOP = 3.45         # wierzch dachu zielonego nad P0/garażem
D_TOP = 3.70             # linia D (wierzch pasa krawędziowego / dolna rama boksu C)
EDGE = {  # wizualne pasy krawędziowe płyt wysuniętych (dół, góra)
    'ST1': (2.70, 3.05), 'D': (2.70, 3.70), 'ST2': (5.90, 6.25), 'ST3': (9.05, ATTIC_TOP)}

# ------------------------------------------------------------------ obrysy (osie warstwy konstrukcyjnej ścian zewn.)
AXIS_POLY = {
    'P0': box(AX['B'], AY['1'], AX['G'], AY['4']),
    'P1': box(AX['A'], AY['1'], AX['E'], AY['3']),
    'P2': box(AX["A'"], AY['1'], AX['E'], AY['3']),
}
OUTLINE = {k: v.buffer(EXT_OUT, join_style=2) for k, v in AXIS_POLY.items()}

# ------------------------------------------------------------------ płyty (obrysy zewnętrzne)
ST1_POLY = Polygon([(-1.80, -1.30), (18.90, -1.30), (18.90, 10.80), (10.00, 10.80), (10.00, 12.30),
                    (6.60, 12.30), (6.60, 10.80), (0.70, 10.80), (0.70, 7.60), (-1.80, 7.60)])
ST2_POLY = box(-2.50, -1.30, 12.10, 7.60)
ST3_POLY = box(-2.10, -1.10, 12.10, 7.60)
CANOPY_N = box(6.60, 10.80, 10.00, 12.30)            # daszek nad wejściem (część ST1)
STAIR_HOLE = box(3.805, 4.905, 7.095, 7.195)         # otwór w ST1 i ST2
SKYLIGHT = box(4.20, 5.10, 6.80, 6.90)               # świetlik w ST3 nad pustką klatki

# boks C (I piętro) — rama wysunięta 1,0 m przed lico bryły B
C_BOX = dict(x0=3.95, x1=11.70, y0=-1.30, y1=-0.30, z_bottom=3.00, z_sill=3.70, z_head=5.20, z_top=5.45,
             glass_x=(4.20, 11.30), glass_y=-1.10, top_frame_x1=13.45)
# lamele bryły A (P2): pionowe, drewno termo / alu w kolorze drewna
LAMELE = dict(y=-0.45, x0=-1.25, x1=11.65, step=0.30, b=0.06, d=0.20, z0=6.25, z1=9.05,
              west_x=-1.45, west_y0=-0.45, west_y1=7.55)

# ------------------------------------------------------------------ schody (U, stos 3 kondygnacji)
STAIR = dict(x0=3.805, x1=8.395, y0=4.905, y1=7.195,
             lane_S=(4.905, 5.995), lane_N=(6.105, 7.195),
             int_landing=(3.805, 4.855), flights=(4.855, 7.095), floor_landing=(7.095, 8.395),
             n_risers=18, h=0.175, s=0.28, per_flight=9)

# ------------------------------------------------------------------ słupy parteru w osi 1 (za słupkami przeszklenia E)
GLAZ_X = (1.105, 12.495)
MULLIONS = [GLAZ_X[0] + i * (GLAZ_X[1] - GLAZ_X[0]) / 5 for i in range(6)]
COLUMNS = [(round(x, 3), 0.0) for x in MULLIONS[1:5]]

# ------------------------------------------------------------------ ściany wewnętrzne (prostokąty w licach), typ
def wall_x(y, x0, x1, half, kind, fl):   # ściana biegnąca wzdłuż x w osi y
    return dict(fl=fl, kind=kind, poly=box(x0, y - half, x1, y + half), o='x', ax=y, span=(x0, x1))


def wall_y(x, y0, y1, half, kind, fl):
    return dict(fl=fl, kind=kind, poly=box(x - half, y0, x + half, y1), o='y', ax=x, span=(y0, y1))


IWALLS = []
for fl in ('P0', 'P1', 'P2'):
    # trzon schodowy — żelbet 18 cm na wszystkich kondygnacjach
    IWALLS += [wall_y(AX['C'], 4.695, 7.405, H_BEAR, 'RC', fl), wall_y(AX['D'], 4.695, 7.405, H_BEAR, 'RC', fl),
               wall_x(AY['2'], 3.595, 8.605, H_BEAR, 'RC', fl)]
# P0
IWALLS += [
    wall_x(AY['2'], AX['B'], 3.60, H_BEAR, 'BEAR', 'P0'), wall_x(AY['2'], 8.60, AX['F'], H_BEAR, 'BEAR', 'P0'),
    wall_x(AY['3'], AX['B'], 3.60, H_BEAR, 'BEAR', 'P0'), wall_x(AY['3'], 3.595, 8.605, H_BEAR, 'RC', 'P0'),
    wall_x(AY['3'], 8.60, AX['F'], H_BEAR, 'BEAR', 'P0'),
    wall_y(9.75, 4.905, 7.195, H_PART, 'PART', 'P0'),                       # spiżarnia | techniczne
    dict(fl='P0', kind='GAR', poly=box(AX['F'] - EXT_IN, -0.09, AX['F'] + GAR_IN, AY['4'] + 0.09), o='y', ax=AX['F'], span=(0, AY['4'])),
    wall_x(Y_GAR, AX['F'] + GAR_IN, AX['G'] - EXT_IN, H_BEAR, 'BEAR', 'P0'),  # garaż | pom. gosp.
    wall_y(4.80, 7.405, 10.395, H_PART, 'PART', 'P0'),                       # pokój gośc. | hol
    wall_x(8.80, 4.875, 12.495, H_PART, 'PART', 'P0'),                       # hol/sień | garderoba, wiatrołap, WC, schowek
    wall_y(6.80, 8.875, 10.395, H_PART, 'PART', 'P0'),
    wall_y(9.40, 8.875, 10.395, H_PART, 'PART', 'P0'),
    wall_y(11.00, 8.875, 10.395, H_PART, 'PART', 'P0'),
]
# P1
IWALLS += [
    wall_x(AY['2'], 8.60, AX['E'], H_BEAR, 'BEAR', 'P1'),                    # pralnia | łazienka (nośna, w pionie z P0/P2)
    wall_y(AX['C'], 0.105, 4.695, H_PART, 'PART', 'P1'),
    wall_x(3.60, 0.105, 3.625, H_PART, 'PART', 'P1'),
    wall_x(2.80, 8.425, 11.295, H_PART, 'PART', 'P1'),
    wall_y(AX['D'], 2.725, 4.695, H_PART, 'PART', 'P1'),
]
# P2
IWALLS += [
    wall_x(AY['2'], 8.60, AX['E'], H_BEAR, 'BEAR', 'P2'),
    wall_y(AX['C'], 0.105, 4.695, H_PART, 'PART', 'P2'),
    wall_x(4.20, -0.895, 3.625, H_PART, 'PART', 'P2'),
    wall_y(1.30, 4.275, 7.195, H_PART, 'PART', 'P2'),
    wall_x(3.00, 3.775, 8.425, H_PART, 'PART', 'P2'),
    wall_y(AX['D'], 0.105, 4.695, H_PART, 'PART', 'P2'),
]
# strefy żelbetowe ścian zewnętrznych (tarcze wspornikowe, ściana-tarcza wsch. P1/P2, ściana zach. P0)
RC_ZONES = {
    'P0': [box(0.70, -0.30, 1.105, AY['4'] + 0.30)],
    'P1': [box(-0.30, -0.30, 0.105, 7.60), box(-0.30, -0.30, 4.20, 0.105), box(-0.30, 7.195, 3.70, 7.60),
           box(11.295, -0.30, 11.70, 7.60)],
    'P2': [box(-1.30, -0.30, -0.895, 7.60), box(-1.30, -0.30, 11.70, 0.105), box(-1.30, 7.195, 3.70, 7.60),
           box(11.295, -0.30, 11.70, 7.60)],
}

# ------------------------------------------------------------------ otwory
# o: 'x' ściana wzdłuż x (N/S), 'y' wzdłuż y (W/E); band = zakres grubości; swing +1/-1 (w stronę +y/+x lub -y/-x)
def ext_open(id_, fl, side, a0, a1, kind, sill, h, symbol, hinge='a0', swing=None, note=''):
    axis = {'S': AY['1'], 'N': AY['3'] if fl != 'P0' else AY['4'],
            'W': {'P0': AX['B'], 'P1': AX['A'], 'P2': AX["A'"]}[fl],
            'E': AX['G'] if fl == 'P0' else AX['E']}[side]
    if side == 'S':
        o, band, inside = 'x', (axis - EXT_OUT, axis + EXT_IN), +1
    elif side == 'N':
        o, band, inside = 'x', (axis - EXT_IN, axis + EXT_OUT), -1
    elif side == 'W':
        o, band, inside = 'y', (axis - EXT_OUT, axis + EXT_IN), +1
    else:
        o, band, inside = 'y', (axis - EXT_IN, axis + EXT_OUT), -1
    return dict(id=id_, fl=fl, side=side, o=o, ax=axis, band=band, a0=a0, a1=a1, kind=kind, sill=sill, h=h,
                symbol=symbol, hinge=hinge, swing=inside if swing is None else swing, ext=True, note=note)


def int_open(id_, fl, o, axis, half, a0, a1, kind, swing=+1, hinge='a0', h=2.05, note=''):
    return dict(id=id_, fl=fl, side='int', o=o, ax=axis, band=(axis - half, axis + half), a0=a0, a1=a1, kind=kind,
                sill=0.0, h=h, symbol='', hinge=hinge, swing=swing, ext=False, note=note)


OPENINGS = [
    # ---------------- P0 zewnętrzne
    ext_open('O0-01', 'P0', 'W', 0.80, 3.20, 'hs', 0.00, 2.60, 'HS1', note='drzwi przesuwne na taras zach.'),
    ext_open('O0-02', 'P0', 'W', 5.50, 6.40, 'win', 1.50, 0.80, 'OK3'),
    ext_open('O0-03', 'P0', 'W', 8.20, 9.80, 'win', 0.85, 1.50, 'OK1'),
    ext_open('O0-04', 'P0', 'N', 7.30, 8.30, 'door_ext', 0.00, 2.20, 'DZ1', hinge='a0', swing=-1, note='drzwi wejściowe'),
    ext_open('O0-05', 'P0', 'N', 8.40, 8.90, 'fix', 0.00, 2.20, 'FX1', note='doświetle boczne'),
    ext_open('O0-06', 'P0', 'N', 9.90, 10.50, 'win', 1.50, 0.80, 'OK4'),
    ext_open('O0-07', 'P0', 'N', 13.16, 18.16, 'gate', 0.00, 2.25, 'BG1', note='brama segmentowa 500x225'),
    ext_open('O0-08', 'P0', 'E', 0.80, 1.80, 'door_ext', 0.00, 2.10, 'DZ2', hinge='a0', swing=-1, note='drzwi do ogrodu (pom. gosp.)'),
    ext_open('O0-09', 'P0', 'E', 6.00, 7.50, 'win', 1.40, 0.80, 'OK5'),
    # ---------------- P0 wewnętrzne
    int_open('D0-01', 'P0', 'x', AY['2'], H_BEAR, 7.15, 8.35, 'open', note='przejście spocznik -> jadalnia'),
    int_open('D0-02', 'P0', 'x', AY['2'], H_BEAR, 8.72, 9.52, 'door', swing=-1, hinge='a1', note='otwierane na zewnątrz (półki)'),
    int_open('D0-03', 'P0', 'x', AY['2'], H_BEAR, 5.95, 6.75, 'door', swing=-1, hinge='a0', h=1.80, note='schowek pod schodami'),
    int_open('D0-04', 'P0', 'x', AY['3'], H_BEAR, 1.95, 2.85, 'door', swing=-1, hinge='a0', note='90 cm (senior)'),
    int_open('D0-05', 'P0', 'x', AY['3'], H_BEAR, 7.15, 8.35, 'open'),
    int_open('D0-06', 'P0', 'x', AY['3'], H_BEAR, 10.40, 11.20, 'door', swing=-1, hinge='a1'),
    int_open('D0-07', 'P0', 'y', 4.80, H_PART, 7.55, 8.45, 'door', swing=-1, hinge='a1'),
    int_open('D0-08', 'P0', 'x', 8.80, H_PART, 5.40, 6.20, 'door', swing=+1, hinge='a0'),
    int_open('D0-09', 'P0', 'x', 8.80, H_PART, 7.30, 8.20, 'door', swing=-1, hinge='a0', note='drzwi szklane wiatrołapu'),
    int_open('D0-10', 'P0', 'x', 8.80, H_PART, 9.80, 10.60, 'door', swing=-1, hinge='a1'),
    int_open('D0-11', 'P0', 'x', 8.80, H_PART, 11.40, 12.20, 'door', swing=-1, hinge='a1'),
    int_open('D0-12', 'P0', 'y', AX['F'], 0.0, 7.55, 8.45, 'door', swing=-1, hinge='a1', note='EI30 samozamykające'),
    int_open('D0-13', 'P0', 'x', Y_GAR, H_BEAR, 16.50, 17.40, 'door', swing=-1, hinge='a0'),
    # ---------------- P1 zewnętrzne
    ext_open('O1-01', 'P1', 'W', 0.90, 2.70, 'win', 0.85, 1.60, 'OK2'),
    ext_open('O1-02', 'P1', 'W', 4.60, 6.40, 'win', 0.85, 1.60, 'OK2'),
    ext_open('O1-03', 'P1', 'E', 3.30, 4.30, 'win', 1.00, 1.20, 'OK6'),
    ext_open('O1-04', 'P1', 'E', 5.60, 6.60, 'win', 1.40, 0.80, 'OK4'),
    ext_open('O1-05', 'P1', 'N', 7.35, 8.15, 'win', 0.90, 1.50, 'OK7', note='okno klatki (nad dachem P0)'),
    ext_open('O1-06', 'P1', 'S', 4.20, 11.30, 'bay', 0.55, 1.50, 'C', note='otwór do boksu C (siedzisko h=0,55)'),
    # ---------------- P1 wewnętrzne
    int_open('D1-01', 'P1', 'y', AX['C'], H_PART, 2.60, 3.40, 'door', swing=-1, hinge='a1'),
    int_open('D1-02', 'P1', 'y', AX['C'], H_PART, 3.80, 4.60, 'door', swing=-1, hinge='a0'),
    int_open('D1-03', 'P1', 'y', AX['D'], H_PART, 3.10, 3.90, 'door', swing=+1, hinge='a0'),
    int_open('D1-04', 'P1', 'y', AX['D'], H_BEAR, 5.20, 6.00, 'door', swing=+1, hinge='a0'),
    int_open('D1-05', 'P1', 'x', AY['2'], H_BEAR, 7.15, 8.35, 'open'),
    # ---------------- P2 zewnętrzne
    ext_open('O2-01', 'P2', 'S', -0.30, 2.70, 'win', 0.60, 2.10, 'OK8', note='za lamelami, dolna kwatera VSG do 1,10'),
    ext_open('O2-02', 'P2', 'S', 4.60, 7.60, 'win', 0.60, 2.10, 'OK8'),
    ext_open('O2-03', 'P2', 'S', 8.90, 10.90, 'win', 0.60, 2.10, 'OK9'),
    ext_open('O2-04', 'P2', 'W', 1.20, 3.00, 'win', 0.90, 1.60, 'OK2'),
    ext_open('O2-05', 'P2', 'W', 5.40, 6.40, 'win', 1.50, 0.80, 'OK3'),
    ext_open('O2-06', 'P2', 'E', 1.60, 3.20, 'win', 0.90, 1.60, 'OK10'),
    ext_open('O2-07', 'P2', 'N', 1.90, 2.90, 'win', 1.50, 0.80, 'OK4'),
    # ---------------- P2 wewnętrzne
    int_open('D2-01', 'P2', 'y', AX['C'], H_PART, 3.20, 4.00, 'door', swing=-1, hinge='a1'),
    int_open('D2-02', 'P2', 'x', 4.20, H_PART, 2.50, 3.30, 'door', swing=+1, hinge='a1', note='łazienka'),
    int_open('D2-03', 'P2', 'x', 4.20, H_PART, -0.30, 0.50, 'door', swing=+1, hinge='a0', note='garderoba'),
    int_open('D2-04', 'P2', 'x', 3.00, H_PART, 4.40, 5.20, 'door', swing=-1, hinge='a0'),
    int_open('D2-05', 'P2', 'y', AX['D'], H_PART, 3.85, 4.65, 'door', swing=+1, hinge='a1'),
    int_open('D2-06', 'P2', 'y', AX['D'], H_BEAR, 5.30, 6.10, 'door', swing=+1, hinge='a0'),
    int_open('D2-07', 'P2', 'x', AY['2'], H_BEAR, 7.15, 8.35, 'open'),
]

# ------------------------------------------------------------------ pomieszczenia (wieloboki netto w licach wykończonych)
# kat: M = mieszkalne/pobyt ludzi, P = pomocnicze, K = komunikacja, T = techniczne, S = schody (poza PU), G = garaż/gosp.
def R(id_, fl, name, geom, kat, pobyt=False, lab=None, min_area=None, note=''):
    return dict(id=id_, fl=fl, name=name, poly=geom, kat=kat, pobyt=pobyt, lab=lab, min_area=min_area, note=note)


ROOMS = [
    R('0.01', 'P0', 'Wiatrołap', box(6.875, 8.875, 9.325, 10.395), 'K'),
    R('0.02', 'P0', 'Hol', box(4.875, 7.405, 9.40, 8.725), 'K', lab=(6.1, 8.05)),
    R('0.03', 'P0', 'Garderoba', box(4.875, 8.875, 6.725, 10.395), 'P'),
    R('0.04', 'P0', 'WC', box(9.475, 8.875, 10.925, 10.395), 'P'),
    R('0.05', 'P0', 'Schowek gosp.', box(11.075, 8.875, 12.495, 10.395), 'P'),
    R('0.06', 'P0', 'Sień gospodarcza', box(9.40, 7.405, 12.495, 8.725), 'K', lab=(11.3, 8.05)),
    R('0.07', 'P0', 'Pokój gościnny / gabinet', box(1.105, 7.405, 4.725, 10.395), 'M', True, min_area=8.0),
    R('0.08', 'P0', 'Łazienka (prysznic)', box(1.105, 4.905, 3.595, 7.195), 'P'),
    R('0.09', 'P0', 'Schody', box(3.805, 4.905, 8.395, 7.195), 'S'),
    R('0.10', 'P0', 'Spiżarnia', box(8.605, 4.905, 9.675, 7.195), 'P'),
    R('0.11', 'P0', 'Pom. techniczne', box(9.825, 4.905, 12.495, 7.195), 'T', min_area=6.0),
    R('0.12', 'P0', 'Salon + jadalnia + kuchnia', box(1.105, -0.10, 12.495, 4.695), 'M', True, min_area=50.0, lab=(6.8, 3.55)),
    R('0.13', 'P0', 'Garaż 2-stanowiskowy', box(AX['F'] + GAR_IN, Y_GAR + H_BEAR, AX['G'] - EXT_IN, AY['4'] - EXT_IN), 'G'),
    R('0.14', 'P0', 'Pom. gosp. (rowery, ogród)', box(AX['F'] + GAR_IN, 0.105, AX['G'] - EXT_IN, Y_GAR - H_BEAR), 'G'),
    # P1
    R('1.01', 'P1', 'Pokój dziecka 1', box(0.105, 0.105, 3.625, 3.525), 'M', True, min_area=12.0),
    R('1.02', 'P1', 'Pokój dziecka 2', box(0.105, 3.675, 3.595, 7.195), 'M', True, min_area=12.0),
    R('1.03', 'P1', 'Pokój rodzinny / biblioteka + hol',
      Polygon([(3.775, 0.105), (11.295, 0.105), (11.295, 2.725), (8.425, 2.725), (8.425, 4.695), (3.775, 4.695)]),
      'M', True, lab=(6.0, 1.55)),
    R('1.04', 'P1', 'Pralnia', box(8.575, 2.875, 11.295, 4.695), 'P'),
    R('1.05', 'P1', 'Łazienka', box(8.605, 4.905, 11.295, 7.195), 'P'),
    R('1.06', 'P1', 'Schody', box(3.805, 4.905, 8.395, 7.195), 'S'),
    # P2
    R('2.01', 'P2', 'Sypialnia rodziców', box(-0.895, 0.105, 3.625, 4.125), 'M', True, min_area=14.0),
    R('2.02', 'P2', 'Garderoba', box(-0.895, 4.275, 1.225, 7.195), 'P'),
    R('2.03', 'P2', 'Łazienka rodziców', box(1.375, 4.275, 3.595, 7.195), 'P'),
    R('2.04', 'P2', 'Gabinet', box(3.775, 0.105, 8.425, 2.925), 'M', True, min_area=8.0),
    R('2.05', 'P2', 'Hol', box(3.775, 3.075, 8.425, 4.695), 'K'),
    R('2.06', 'P2', 'Pokój (5. osoba / hobby)', box(8.575, 0.105, 11.295, 4.695), 'M', True, min_area=8.0),
    R('2.07', 'P2', 'Pom. techn. (rekuperator, wyłaz)', box(8.605, 4.905, 11.295, 7.195), 'T'),
    R('2.08', 'P2', 'Spocznik (pustka nad schodami)', box(7.095, 4.905, 8.395, 7.195), 'S'),
]

# piony instalacyjne (xy) — w jednej osi przez kondygnacje
PIONY = [dict(id='K1', xy=(11.20, 6.25), opis='kan. + woda: łaz. P1, pralnia P1, skropliny rekuperatora P2 -> pom. techn. P0'),
         dict(id='K2', xy=(3.40, 7.05), opis='kan. + woda: łaz. P2 -> szacht 30x30 w narożu pok. 1.02 (przy trzonie) -> łaz. P0'),
         dict(id='W1', xy=(8.80, 7.00), opis='kanały wentylacji mech. (rekuperator P2) -> łaz. P1 -> spiżarnia/kuchnia P0')]

# ------------------------------------------------------------------ działka (współrzędne budynku)
PLOT = box(-7.30, -31.00, 24.70, 19.00)            # 32,00 x 50,00
ROAD = box(-12.0, 19.00, 30.0, 29.00)                # linie rozgraniczające 1KDD (10 m)
CARRIAGEWAY = box(-12.0, 21.50, 30.0, 26.50)
BUILD_LINE_Y = 19.00 - 6.00


def terrain_H(x, y):
    """Rzędna terenu [m n.p.m.] — interpolacja dwuliniowa z narożników działki."""
    u, v = x + 7.30, y + 31.00
    return 101.10 + 0.30 * v / 50.0 + 0.15 * u / 32.0


def terrain_z(x, y):
    return terrain_H(x, y) - ZERO_ABS


SITE = dict(
    driveway=box(12.90, 10.80, 18.90, 19.00),
    guest_parking=[box(13.30, 11.40, 15.80, 16.40), box(16.00, 11.40, 18.50, 16.40)],
    path=box(7.05, 10.80, 8.55, 19.00),
    path_side=box(-1.80, 7.60, 0.70, 10.80),            # dojście boczne do ogrodu (płyty)
    terrace_S=box(-1.80, -4.30, 12.90, -0.30),
    terrace_W=box(-1.80, -0.30, 0.70, 4.20),
    bins=box(9.30, 14.60, 11.90, 15.90),
    hp_unit=box(20.20, 5.60, 21.30, 6.20),
    hp_pad=box(19.90, 5.30, 21.60, 6.50),
    tank=Point(15.3, -6.6).buffer(1.10),
    infiltr=box(14.00, -12.40, 18.40, -10.20),
    zk=box(12.05, 18.75, 12.75, 19.05),
    gate=(13.30, 18.30), wicket=(7.30, 8.30),
    well_san=Point(9.0, 17.6).buffer(0.35),
    water_meter_note='wodomierz w pom. techn. 0.11',
)

ENTRANCES = {'drzwi wejściowe (N)': (7.80, 10.80), 'brama garażu (N)': (15.66, 10.80),
             'HS salonu (W)': (0.70, 2.00), 'HS E2 (S)': (4.52, -0.30), 'HS E4 (S)': (9.08, -0.30),
             'drzwi pom. gosp. (E)': (18.90, 1.30)}


def building_height():
    zmin = min(terrain_z(*v) for v in ENTRANCES.values())
    return ATTIC_TOP - zmin, zmin


LEVELS = [('±0,00', 0.00, 'posadzka P0'), ('+2,78', 2.78, 'spód ST1'), ('+3,15', 3.15, 'posadzka P1'),
          ('+5,93', 5.93, 'spód ST2'), ('+6,30', 6.30, 'posadzka P2'), ('+9,08', 9.08, 'spód ST3'),
          ('+9,30', 9.30, 'wierzch płyty dachu'), ('+9,85', ATTIC_TOP, 'attyka')]
