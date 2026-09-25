# -*- coding: utf-8 -*-
"""Tabele i sprawdzenia W1 generowane z modelu (dla opis.md)."""
import json
from shapely.geometry import box
from model_w1 import *
from draw_site import site_metrics
from draw_common import fmt

KAT = dict(M='mieszk./pobyt', P='pomocnicze', K='komunikacja', T='techniczne', S='schody (poza PU)',
           G='garaż / gosp.')
WIN_MAP = {'0.07': ['O0-03'], '0.12': ['E1', 'E2', 'E3', 'E4', 'E5', 'O0-01'], '1.01': ['O1-01'],
           '1.02': ['O1-02'], '1.03': ['O1-06'], '2.01': ['O2-01', 'O2-04'], '2.04': ['O2-02'],
           '2.06': ['O2-03', 'O2-06']}
FR = 0.06   # redukcja na ościeżnicę (z każdej strony) -> „w świetle ościeżnic”


def ops_by_id():
    d = {o['id']: o for o in OPENINGS}
    for i in range(5):
        a, b = MULLIONS[i], MULLIONS[i + 1]
        d[f'E{i + 1}'] = dict(id=f'E{i + 1}', a0=a, a1=b, h=2.72, sill=0.0, kind='hs' if i in (1, 3) else 'fix',
                              symbol='HS2' if i in (1, 3) else 'FX2', fl='P0', side='S')
    return d


def win_area(o):
    w = (o['a1'] - o['a0'])
    h = o['h']
    if o['id'] == 'O1-06':          # boks C — szklenie w ramie
        w = C_BOX['glass_x'][1] - C_BOX['glass_x'][0]
        h = C_BOX['z_head'] - C_BOX['z_sill']
    return max(w - 2 * FR, 0) * max(h - 2 * FR, 0)


def room_table(fl):
    rows = []
    for r in ROOMS:
        if r['fl'] != fl:
            continue
        b = r['poly'].bounds
        dims = f"{fmt(b[2] - b[0])} × {fmt(b[3] - b[1])}" if r['poly'].area > 0.999 * (b[2] - b[0]) * (b[3] - b[1]) \
            else 'wielobok'
        rows.append((r['id'], r['name'], KAT[r['kat']], dims, r['poly'].area, r))
    return rows


def md_rooms(fl):
    s = "| nr | pomieszczenie | kategoria | wymiary netto [m] (x × y) | pow. netto [m²] | wielobok (x,y) |\n|---|---|---|---|---|---|\n"
    for (i, n, k, d, a, r) in room_table(fl):
        coords = '; '.join(f"({fmt(x, 3)}, {fmt(y, 3)})" for x, y in list(r['poly'].exterior.coords)[:-1])
        s += f"| {i} | {n} | {k} | {d} | **{fmt(a)}** | {coords} |\n"
    return s


def totals():
    t = {}
    for fl in ('P0', 'P1', 'P2'):
        rs = [r for r in ROOMS if r['fl'] == fl]
        t[fl] = dict(PU=sum(r['poly'].area for r in rs if r['kat'] in 'MPK'),
                     T=sum(r['poly'].area for r in rs if r['kat'] == 'T'),
                     S=sum(r['poly'].area for r in rs if r['kat'] == 'S'),
                     G=sum(r['poly'].area for r in rs if r['kat'] == 'G'))
    tot = {k: sum(t[f][k] for f in t) for k in ('PU', 'T', 'S', 'G')}
    return t, tot


def md_windows():
    d = ops_by_id()
    s = ("| pom. | pow. podłogi [m²] | okna (symbol) | pow. okien w świetle ościeżnic [m²] | stosunek | wymóg ≥ 1:8 |\n"
         "|---|---|---|---|---|---|\n")
    out = []
    for rid, wins in WIN_MAP.items():
        r = next(x for x in ROOMS if x['id'] == rid)
        A = r['poly'].area
        W = sum(win_area(d[w]) for w in wins)
        ok = W / A >= 1 / 8
        out.append((rid, A, W))
        s += (f"| {rid} {r['name']} | {fmt(A)} | {', '.join(d[w].get('symbol') or w for w in wins)} | {fmt(W)} | "
              f"1:{fmt(A / W, 1)} | {'✔' if ok else '✘'} |\n")
    return s, out


def md_openings(fl):
    s = ("| id | ściana / położenie | typ | szer. × wys. [m] | parapet [m] | symbol / uwagi |\n"
         "|---|---|---|---|---|---|\n")
    for o in OPENINGS:
        if o['fl'] != fl:
            continue
        if o['ext']:
            where = {'S': 'płd. (oś 1)', 'N': 'płn. (oś ' + ('4' if fl == 'P0' else '3') + ')',
                     'W': 'zach. (oś ' + {'P0': 'B', 'P1': 'A', 'P2': "A'"}[fl] + ')',
                     'E': 'wsch. (oś ' + ('G' if fl == 'P0' else 'E') + ')'}[o['side']]
        else:
            where = ('ściana ' + ('y' if o['o'] == 'x' else 'x') + f"={fmt(o['ax'])}")
        rng = ('x' if o['o'] == 'x' else 'y') + f" {fmt(o['a0'])}–{fmt(o['a1'])}"
        typ = dict(win='okno', fix='fix', hs='drzwi HS', door='drzwi', door_ext='drzwi zewn.', gate='brama',
                   open='przejście', bay='otwór do boksu')[o['kind']]
        s += (f"| {o['id']} | {where}, {rng} | {typ} | {fmt(o['a1'] - o['a0'])} × {fmt(o['h'])} | {fmt(o['sill'])} | "
              f"{o['symbol']} {o['note']} |\n")
    if fl == 'P0':
        for i in range(5):
            a, b = MULLIONS[i], MULLIONS[i + 1]
            s += (f"| E{i + 1} | płd. (oś 1), x {fmt(a)}–{fmt(b)} | {'drzwi HS' if i in (1, 3) else 'fix'} | "
                  f"{fmt(b - a)} × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |\n")
    return s


def md_walls(fl):
    s = "| typ | położenie (oś warstwy konstr.) | od–do | grubość / przegroda |\n|---|---|---|---|\n"
    ap = AXIS_POLY[fl]
    x0, y0, x1, y1 = ap.bounds
    rcz = {'P0': 'oś B: ŻB 18 (podpora wsporników)', 'P1': 'osie A, E oraz N/S w strefie x ≤ 3,70–4,20: ŻB 18 (tarcze)',
           'P2': "osie A', E, S (cała) i N (x ≤ 3,70): ŻB 18 (tarcze)"}[fl]
    s += (f"| zewn. SZ1 | prostokąt osi x {fmt(x0)}–{fmt(x1)}, y {fmt(y0)}–{fmt(y1)} | obwód"
          f"{' (bez przeszklenia E x 1,105–12,495 w osi 1)' if fl == 'P0' else ''} | 18 cm SIL/ŻB + 20 cm EPS/MW + tynki = 40,5 cm; {rcz} |\n")
    for w in IWALLS:
        if w['fl'] != fl:
            continue
        kind = dict(RC='ŻB 18 (trzon)', BEAR='SIL 18 nośna', PART='SIL 12 działowa',
                    GAR='SIL 18 + MW 12 od garażu (EI 60)')[w['kind']]
        ax_ = 'y' if w['o'] == 'x' else 'x'
        rng = ('x' if w['o'] == 'x' else 'y')
        s += f"| wewn. | {ax_} = {fmt(w['ax'])} | {rng} {fmt(w['span'][0])}–{fmt(w['span'][1])} | {kind} |\n"
    return s


def dist_checks():
    xw, xe, yn, ys = -7.30, 24.70, 19.00, -31.00
    rows = [
        ('ściana zach. P2 z oknami (lico)', -1.30 - xw, 4.0),
        ('ściana zach. P1 z oknami (lico)', -0.30 - xw, 4.0),
        ('ściana zach. P0 z oknami/drzwiami (lico)', 0.70 - xw, 4.0),
        ('płyta ST2 wysunięta na zach. (krawędź)', -2.50 - xw, 4.0),
        ('płyta dachu ST3 (krawędź)', -2.10 - xw, 4.0),
        ('płyta ST1 wysunięta 1,50 m (krawędź)', -1.80 - xw, 4.0),
        ('ściana wsch. garażu z drzwiami i oknem (lico)', xe - 18.90, 4.0),
        ('ściany wsch. P1/P2 z oknami (lico)', xe - 11.70, 4.0),
        ('jednostka zewn. PC', xe - 21.30, 3.0),
        ('elewacja płn. P0 od granicy z drogą', yn - 10.80, 6.0),
        ('daszek nad wejściem od granicy z drogą', yn - 12.30, 6.0),
        ('elewacja płd. / boks C od granicy tylnej', -1.30 - ys, 4.0),
        ('osłona pojemników od granicy z drogą', yn - SITE['bins'].bounds[3], 3.0),
    ]
    return rows


def lowest_entrance():
    pts = {'drzwi wejściowe (N)': (7.80, 10.80), 'brama garażu (N)': (15.66, 10.80),
           'HS salonu (W)': (0.70, 2.00), 'HS E2 (S)': (4.52, -0.30), 'HS E4 (S)': (9.08, -0.30),
           'drzwi pom. gosp. (E)': (18.90, 1.30)}
    return {k: terrain_z(*v) for k, v in pts.items()}


if __name__ == '__main__':
    t, tot = totals()
    print(t, tot)
    print(md_windows()[0])
    print(lowest_entrance())
    for r in dist_checks():
        print(r)
