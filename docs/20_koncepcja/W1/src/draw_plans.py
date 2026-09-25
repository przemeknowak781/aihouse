# -*- coding: utf-8 -*-
"""Rzuty kondygnacji P0, P1, P2 — wariant W1."""
import os
import textwrap
from shapely.geometry import box, Polygon, Point
from shapely.ops import unary_union
from draw_common import *
from model_w1 import *

OUT = '/home/user/aihouse/docs/20_koncepcja/W1'


def wall_shell(fl):
    ap = AXIS_POLY[fl]
    struct = ap.buffer(STR, join_style=2).difference(ap.buffer(-EXT_IN, join_style=2))
    ins = ap.buffer(EXT_OUT, join_style=2).difference(ap.buffer(STR, join_style=2))
    if fl == 'P0':   # ciągłe przeszklenie strefy dziennej w osi 1
        cut = box(GLAZ_X[0], -0.40, GLAZ_X[1], 0.20)
        struct, ins = struct.difference(cut), ins.difference(cut)
    return struct, ins


def op_band(op):
    if op['id'] == 'D0-12':
        return (AX['F'] - EXT_IN, AX['F'] + GAR_IN)
    return op['band']


def op_box(op, grow=0.005):
    b0, b1 = op_band(op)
    if op['o'] == 'x':
        return box(op['a0'], b0 - grow, op['a1'], b1 + grow)
    return box(b0 - grow, op['a0'], b1 + grow, op['a1'])


def draw_door(ax, op, lw=0.6):
    o, a0, a1, sw = op['o'], op['a0'], op['a1'], op['swing']
    b0, b1 = op_band(op)
    w = a1 - a0
    col = '#333333'
    if o == 'x':
        face = b1 if sw > 0 else b0
        h = a0 if op['hinge'] == 'a0' else a1
        other = a1 if op['hinge'] == 'a0' else a0
        ax.plot([h, h], [face, face + sw * w], color=col, lw=lw + 0.3, zorder=6)
        a = 90 if sw > 0 else 270
        b = 0 if other > h else 180
        arc_between(ax, (h, face), w, a, b, color=col, lw=0.4, zorder=6, ls='-')
    else:
        face = b1 if sw > 0 else b0
        h = a0 if op['hinge'] == 'a0' else a1
        other = a1 if op['hinge'] == 'a0' else a0
        ax.plot([face, face + sw * w], [h, h], color=col, lw=lw + 0.3, zorder=6)
        a = 0 if sw > 0 else 180
        b = 90 if other > h else 270
        arc_between(ax, (face, h), w, a, b, color=col, lw=0.4, zorder=6)


def draw_window(ax, op):
    o, a0, a1 = op['o'], op['a0'], op['a1']
    b0, b1 = op_band(op)
    m = (b0 + b1) / 2
    kind = op['kind']
    if o == 'x':
        ax.add_patch(Rectangle((a0, b0), a1 - a0, b1 - b0, fc='white', ec='k', lw=0.5, zorder=5))
        if kind in ('win', 'fix'):
            ax.plot([a0, a1], [m - 0.03, m - 0.03], color='k', lw=0.4, zorder=6)
            ax.plot([a0, a1], [m + 0.03, m + 0.03], color='k', lw=0.4, zorder=6)
        elif kind == 'hs':
            mid = (a0 + a1) / 2
            ax.plot([a0, mid + 0.1], [m - 0.04, m - 0.04], color='k', lw=0.6, zorder=6)
            ax.plot([mid - 0.1, a1], [m + 0.04, m + 0.04], color='k', lw=0.6, zorder=6)
    else:
        ax.add_patch(Rectangle((b0, a0), b1 - b0, a1 - a0, fc='white', ec='k', lw=0.5, zorder=5))
        if kind in ('win', 'fix'):
            ax.plot([m - 0.03, m - 0.03], [a0, a1], color='k', lw=0.4, zorder=6)
            ax.plot([m + 0.03, m + 0.03], [a0, a1], color='k', lw=0.4, zorder=6)
        elif kind == 'hs':
            mid = (a0 + a1) / 2
            ax.plot([m - 0.04, m - 0.04], [a0, mid + 0.1], color='k', lw=0.6, zorder=6)
            ax.plot([m + 0.04, m + 0.04], [mid - 0.1, a1], color='k', lw=0.6, zorder=6)
    # symbol
    if op.get('symbol') and kind not in ('bay',):
        if o == 'x':
            ty = b1 + 0.22 if op['side'] == 'N' else b0 - 0.22
            ax.text((a0 + a1) / 2, ty, op['symbol'], fontsize=5.2, ha='center', va='center', color='#7a4b00', zorder=7)
        else:
            tx = b0 - 0.25 if op['side'] == 'W' else b1 + 0.25
            ax.text(tx, (a0 + a1) / 2, op['symbol'], fontsize=5.2, ha='center', va='center', color='#7a4b00',
                    rotation=90, zorder=7)


def furniture(fl):
    """Wyposażenie orientacyjne (prostokąty/koła) — sprawdzone względem zasięgu skrzydeł drzwi."""
    F = []
    R_ = lambda x0, y0, x1, y1, t='': F.append(('r', (x0, y0, x1, y1), t))
    Ci = lambda x, y, r, t='': F.append(('c', (x, y, r), t))
    if fl == 'P0':
        R_(1.75, 3.35, 4.55, 4.25, 'sofa'); R_(2.55, 2.00, 3.75, 2.80)                 # salon
        R_(5.95, 1.45, 7.95, 2.45, 'stół'); [Ci(x, y, 0.2) for x in (6.3, 6.95, 7.6) for y in (1.15, 2.75)]
        R_(11.85, 0.90, 12.495, 4.695, 'blat'); R_(9.85, 4.05, 11.85, 4.695, 'zabudowa')  # kuchnia
        R_(9.30, 1.85, 11.30, 2.85, 'wyspa')
        R_(1.95, 8.395, 3.35, 10.395, 'łóżko'); R_(1.105, 7.405, 2.9, 7.95, 'biurko')     # gość
        R_(1.105, 4.905, 2.30, 6.10, 'natrysk'); R_(3.0, 6.40, 3.595, 7.195, 'wc'); R_(2.60, 4.905, 3.595, 5.45, 'umyw.')
        R_(9.325, 4.905, 9.675, 7.195); R_(8.605, 6.85, 9.675, 7.195)                    # spiżarnia półki
        Ci(10.30, 5.35, 0.36, 'CWU'); R_(11.50, 4.905, 12.10, 5.405, 'PC'); R_(12.20, 5.90, 12.495, 6.90, 'RG')
        R_(11.80, 6.80, 12.40, 7.195, 'wod.')
        R_(9.475, 9.60, 10.2, 10.395, 'wc')                                               # WC
        R_(4.875, 9.85, 6.725, 10.395, 'szafy'); R_(6.95, 9.95, 7.20, 10.39)              # garderoba
        R_(13.40, 5.20, 15.25, 9.90, 'auto'); R_(16.10, 5.20, 17.95, 9.90, 'auto')        # garaż
        for i in range(4):
            R_(13.1 + i * 0.75, 0.45, 13.6 + i * 0.75, 2.25)                                  # rowery
        R_(16.4, 0.105, 17.4, 0.70, 'regał')
    if fl == 'P1':
        R_(0.35, 0.40, 1.35, 2.45, 'łóżko'); R_(2.2, 0.105, 3.625, 0.75, 'biurko'); R_(0.105, 2.9, 1.9, 3.525, 'szafa')
        R_(0.35, 5.00, 1.35, 7.05, 'łóżko'); R_(1.6, 6.55, 3.2, 7.195, 'biurko'); R_(0.105, 3.675, 1.9, 4.30, 'szafa')
        R_(4.00, 4.20, 7.00, 4.695, 'regały'); R_(5.0, 1.8, 7.4, 2.7, 'sofa')
        R_(8.575, 4.10, 10.4, 4.695, 'pralka/susz.')
        R_(9.50, 6.445, 11.20, 7.195, 'wanna'); R_(10.395, 4.905, 11.295, 5.805, 'natrysk')
        R_(9.55, 4.905, 10.15, 5.55, 'wc'); R_(8.605, 5.95, 9.10, 6.40, 'um.')
    if fl == 'P2':
        R_(0.20, 1.20, 2.00, 3.20, 'łóżko 180'); R_(2.8, 0.105, 3.625, 1.6)
        R_(-0.895, 4.275, -0.35, 7.195, 'szafy'); R_(-0.895, 6.65, 1.225, 7.195); R_(0.70, 4.275, 1.225, 6.0)
        R_(1.375, 4.275, 2.475, 5.575, 'natrysk'); R_(1.375, 5.80, 1.925, 7.195, 'um. x2'); R_(2.85, 6.50, 3.30, 7.195, 'wc')
        R_(4.0, 0.105, 6.6, 0.75, 'biurko'); R_(7.8, 0.3, 8.425, 2.7, 'regał')
        R_(10.295, 2.40, 11.295, 4.40, 'łóżko'); R_(8.575, 0.105, 9.8, 0.75, 'biurko')
        R_(9.1, 6.3, 10.4, 7.195, 'rekuperator')
    return F


def draw_stairs(ax, fl):
    s = STAIR
    x0, x1 = s['flights']
    lnS, lnN = s['lane_S'], s['lane_N']
    treads = [x1 - k * s['s'] for k in range(9)]
    # obrys biegu i spoczników
    solid = dict(color='k', lw=0.45, zorder=5)
    dash = dict(color='k', lw=0.45, ls=(0, (3, 2)), zorder=5)
    # przegroda między biegami (duszek 11 cm: balustrada/ścianka)
    ax.add_patch(Rectangle((x0, lnS[1]), x1 - x0, lnN[0] - lnS[1], fc='#777777', ec='k', lw=0.4, zorder=5))
    cutx = x1 - 5.5 * s['s']
    if fl == 'P0':
        # bieg 1 (pasmo N, w górę na zachód): do linii cięcia ciągły, dalej przerywany; bieg 2 (pasmo S) nad cięciem
        for t in treads:
            ax.plot([t, t], lnN, **(solid if t >= cutx else dash))
            ax.plot([t, t], lnS, **dash)
        ax.plot([cutx + 0.25, cutx - 0.25], [lnN[1], lnN[0]], color='k', lw=0.7, zorder=6)
        ax.annotate('', xy=(4.95, (lnN[0] + lnN[1]) / 2), xytext=(8.1, (lnN[0] + lnN[1]) / 2),
                    arrowprops=dict(arrowstyle='->', lw=0.7), zorder=7)
        ax.text(6.0, lnN[1] - 0.05, '18 × 17,5/28', fontsize=5.5, ha='center', va='top', zorder=7)
        ax.text(4.33, (lnS[0] + lnN[1]) / 2, 'spocznik\n+1,575', fontsize=5, ha='center', va='center', zorder=7)
    elif fl == 'P1':
        for t in treads:
            ax.plot([t, t], lnS, **solid)           # bieg z dołu (widoczny)
            ax.plot([t, t], lnN, **(solid if t >= cutx else dash))
        ax.plot([cutx + 0.25, cutx - 0.25], [lnN[1], lnN[0]], color='k', lw=0.7, zorder=6)
        ax.annotate('', xy=(4.95, (lnN[0] + lnN[1]) / 2), xytext=(8.1, (lnN[0] + lnN[1]) / 2),
                    arrowprops=dict(arrowstyle='->', lw=0.7), zorder=7)
        ax.annotate('', xy=(8.1, (lnS[0] + lnS[1]) / 2), xytext=(5.0, (lnS[0] + lnS[1]) / 2),
                    arrowprops=dict(arrowstyle='<-', lw=0.7, ls='--'), zorder=7)
        ax.text(6.0, lnN[1] - 0.05, 'w górę 18 × 17,5/28', fontsize=5.3, ha='center', va='top', zorder=7)
        ax.text(6.0, lnS[0] + 0.05, 'w dół', fontsize=5.3, ha='center', va='bottom', zorder=7)
        ax.text(4.33, (lnS[0] + lnN[1]) / 2, 'spocznik\n+4,725', fontsize=5, ha='center', va='center', zorder=7)
    else:
        for t in treads:
            ax.plot([t, t], lnS, **solid)
            ax.plot([t, t], lnN, color='#777', lw=0.4, zorder=5)
        # pustka nad biegiem N i spocznikiem międzykondygnacyjnym
        void = box(s['x0'], s['y0'], s['floor_landing'][0], s['y1']).difference(box(x0, lnS[0], x1, lnS[1]))
        draw_geom(ax, void, fc='none', ec='#555', lw=0.3, hatch='xx', alpha=0.35, z=4)
        ax.annotate('', xy=(8.1, (lnS[0] + lnS[1]) / 2), xytext=(5.0, (lnS[0] + lnS[1]) / 2),
                    arrowprops=dict(arrowstyle='<-', lw=0.7, ls='--'), zorder=7)
        ax.text(5.9, (lnN[0] + lnN[1]) / 2, 'PUSTKA — świetlik w dachu', fontsize=5.5, ha='center', va='center',
                zorder=7, bbox=dict(fc='white', ec='none', pad=0.5))
        # balustrada 1,10 m na krawędzi spocznika P2 i wzdłuż biegu
        ax.plot([x1, x1], [lnN[0], lnN[1]], color='#1a5276', lw=1.6, zorder=7)
        ax.plot([x0, x1], [lnS[1] + 0.02, lnS[1] + 0.02], color='#1a5276', lw=1.6, zorder=7)
        ax.text(x1 + 0.08, lnN[1] - 0.15, 'bal. h=1,10', fontsize=4.8, color='#1a5276', zorder=7, va='top')
    # spocznik piętrowy (wschód)
    fx0, fx1 = s['floor_landing']
    ax.text((fx0 + fx1) / 2, s['y0'] + 0.12, 'spocznik\nkond.', fontsize=4.8, ha='center', va='bottom', zorder=7,
            color='#333')


def plan(fl, title, fname):
    fig, ax = plt.subplots(figsize=(17, 11.6))
    XMIN, XMAX, YMIN, YMAX = -7.2, 22.6, -8.2, 16.4
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(YMIN, YMAX)
    ax.set_aspect('equal')
    ax.axis('off')

    # ---------- elementy poniżej / powyżej płaszczyzny cięcia
    if fl == 'P0':
        outline(ax, ST1_POLY, ec='#555', lw=0.7, ls=(0, (6, 3)), z=3)
        ax.text(-1.7, -1.75, 'obrys płyty ST1 (dach P0 / strop P1) — wysunięcia: zach. 1,50 m poza lico B, płd. 1,00 m',
                fontsize=5.8, color='#555', va='bottom')
        outline(ax, OUTLINE['P1'], ec='#7d3c98', lw=0.8, ls=(0, (2, 2)), z=3)
        outline(ax, OUTLINE['P2'], ec='#1f618d', lw=0.8, ls=(0, (1, 2)), z=3)
        # teren: tarasy
        draw_geom(ax, SITE['terrace_S'].union(SITE['terrace_W']), fc='#efe7da', ec='#8a7a60', lw=0.4, z=1)
        for xx in [x * 0.5 for x in range(-3, 26)]:
            ax.plot([xx, xx], [-4.3, -0.30], color='#d8ccb8', lw=0.3, zorder=1.1)
        ax.text(5.5, -3.7, 'TARAS OGRODOWY ±0,00 (deska kompozytowa)  —  pod okapem ST1', fontsize=6.5, ha='center',
                color='#6e5a3c')
        ax.text(-0.55, 2.0, 'taras zach.\npod okapem', fontsize=5.5, ha='center', color='#6e5a3c', rotation=90)
        draw_geom(ax, SITE['path'].intersection(box(-10, 10.80, 30, 13.9)), fc='#e4e4e4', ec='#999', lw=0.4, z=1)
        draw_geom(ax, SITE['driveway'].intersection(box(-10, 10.80, 30, 13.9)), fc='#e4e4e4', ec='#999', lw=0.4, z=1)
        ax.text(7.8, 12.9, 'dojście ↓', fontsize=6, ha='center', color='#555', zorder=4)
        ax.annotate('WEJŚCIE', xy=(7.8, 10.55), xytext=(7.8, 11.35), fontsize=6.5, ha='center', fontweight='bold', zorder=8, arrowprops=dict(arrowstyle='->', lw=1.0))
        ax.text(15.9, 13.3, 'podjazd / 2 miejsca gościnne ↓', fontsize=6, ha='center', color='#555', zorder=4)
        ax.text(8.3, 11.95, 'daszek nad wejściem (ST1, 1,50 m)', fontsize=5.5, ha='center', color='#555', zorder=4)
        draw_geom(ax, SITE['hp_pad'], fc='#e0e0e0', ec='#777', lw=0.4, z=2)
        draw_geom(ax, SITE['hp_unit'], fc='#bbbbbb', ec='k', lw=0.5, z=3)
        ax.text(21.75, 5.9, 'PC — jedn. zewn.\n(3,40 m od granicy)', fontsize=5.5, va='center', zorder=4)
    if fl == 'P1':
        roof_below = ST1_POLY.difference(OUTLINE['P1'])
        draw_geom(ax, roof_below, fc='#eef4e8', ec='#6b8e23', lw=0.6, z=1)
        green = box(0.70, 7.60, 18.90, 10.80).union(box(11.70, -0.30, 18.90, 10.80)).difference(OUTLINE['P1'])
        draw_geom(ax, green, fc='none', ec='#8fbc8f', lw=0.0, hatch='..', alpha=0.6, z=1.2)
        ax.text(15.8, 5.0, 'DACH ZIELONY EKSTENSYWNY\nnad garażem i parterem\n(nieużytkowy, bez tarasu)\nwierzch ok. +3,45',
                fontsize=6.5, ha='center', va='center', color='#3d5c1f', zorder=4)
        ax.text(4.5, 9.2, 'dach zielony nad P0 (skrzydło płn.) — nieużytkowy', fontsize=6, ha='center',
                color='#3d5c1f', zorder=4)
        ax.text(-1.05, 3.5, 'płyta ST1\nwysunięta\n1,50 m', fontsize=5.5, ha='center', va='center', color='#555',
                rotation=90, zorder=4)
        outline(ax, ST2_POLY, ec='#555', lw=0.7, ls=(0, (6, 3)), z=3)
        ax.text(-2.4, -1.22, 'obrys ST2 (strop P2) nad', fontsize=5.5, color='#555', va='bottom')
        outline(ax, OUTLINE['P2'], ec='#1f618d', lw=0.8, ls=(0, (1, 2)), z=3)
        # linia D — pas krawędziowy (wierzch +3,70) i rama górna boksu C wysunięta na wschód
        dband = box(C_BOX['x0'], -1.30, 18.90, -1.05)
        draw_geom(ax, dband, fc='#9a9893', ec='k', lw=0.5, z=3)
        ax.text(15.5, -1.55, 'linia D: pas krawędziowy stropu nad parterem/garażem, wierzch +3,70 (bez tarasu)',
                fontsize=5.8, ha='center', va='top', color='#333', zorder=4)
        # boks C
        cb = box(C_BOX['x0'], C_BOX['y0'], C_BOX['x1'], C_BOX['y1'])
        inner = box(C_BOX['glass_x'][0], C_BOX['glass_y'], C_BOX['glass_x'][1], C_BOX['y1'])
        draw_geom(ax, cb.difference(inner), fc='#7f7f7a', ec='k', lw=0.6, z=5)
        draw_geom(ax, inner, fc='#f6f1e4', ec='k', lw=0.4, z=4)
        ax.plot([C_BOX['glass_x'][0], C_BOX['glass_x'][1]], [C_BOX['glass_y'] - 0.03] * 2, color='k', lw=0.8, zorder=6)
        for k in range(1, 3):
            gx = C_BOX['glass_x'][0] + k * (C_BOX['glass_x'][1] - C_BOX['glass_x'][0]) / 3
            ax.add_patch(Rectangle((gx - 0.04, C_BOX['glass_y'] - 0.08), 0.08, 0.1, fc='k', zorder=6))
        ax.text(7.75, -0.72, 'BOKS C — przeszklony wykusz w ramie (3 kwatery), siedzisko/czytelnia h=0,55',
                fontsize=5.8, ha='center', va='center', zorder=7)
        outline(ax, box(11.70, -1.30, C_BOX['top_frame_x1'], -0.30), ec='#333', lw=0.6, ls=(0, (4, 2)), z=4)
        ax.text(12.6, -0.8, 'rama górna C\n(nad, do +5,45)', fontsize=5, ha='center', va='center', color='#333', zorder=4)
    if fl == 'P2':
        draw_geom(ax, ST1_POLY.difference(OUTLINE['P2']).difference(ST2_POLY), fc='#f1f5ec', ec='#9ab77f', lw=0.4,
                  z=1)
        draw_geom(ax, ST2_POLY.difference(OUTLINE['P2']), fc='#e7e6e2', ec='#666', lw=0.6, z=1.5)
        ax.text(-1.95, 3.2, 'płyta ST2\nwysunięta 1,20 m', fontsize=5.5, ha='center', va='center', color='#444',
                rotation=90, zorder=4)
        ax.text(5.0, -1.05, 'płyta ST2 wysunięta 1,00 m (okap nad boksem C)', fontsize=5.8, ha='center', color='#444',
                zorder=4)
        outline(ax, ST3_POLY, ec='#555', lw=0.7, ls=(0, (6, 3)), z=3)
        ax.text(12.2, 7.2, 'obrys dachu ST3\n(wysunięcia 0,80 / 0,40)', fontsize=5.5, color='#555', va='top')
        # lamele
        L = LAMELE
        x = L['x0']
        while x <= L['x1'] + 1e-6:
            ax.add_patch(Rectangle((x - L['b'] / 2, L['y'] - L['d'] / 2), L['b'], L['d'], fc=C['wood'], ec='#6e4f2f',
                                   lw=0.2, zorder=6))
            x += L['step']
        y = L['west_y0']
        while y <= L['west_y1'] + 1e-6:
            ax.add_patch(Rectangle((L['west_x'] - L['d'] / 2, y - L['b'] / 2), L['d'], L['b'], fc=C['wood'],
                                   ec='#6e4f2f', lw=0.2, zorder=6))
            y += L['step']
        ax.text(5.2, -0.62, 'LAMELE pionowe 6×20 cm co 30 cm (drewno termo), 15 cm przed licem', fontsize=5.5,
                ha='center', va='center', color='#6e4f2f', zorder=7, bbox=dict(fc='white', ec='none', pad=0.3))
        draw_geom(ax, SKYLIGHT, fc='none', ec='#1f618d', lw=0.6, ls=(0, (2, 2)), z=7)
        draw_geom(ax, box(9.5, 5.4, 10.4, 6.6), fc='none', ec='k', lw=0.6, ls=(0, (2, 2)), z=7)
        ax.text(9.95, 5.2, 'wyłaz 90×120', fontsize=4.8, ha='center', va='top', zorder=7)

    # ---------- pomieszczenia (wypełnienie)
    rooms = [r for r in ROOMS if r['fl'] == fl]
    for r in rooms:
        draw_geom(ax, r['poly'], fc=ROOM_FILL[r['kat']], ec='none', lw=0, z=1.5)

    # ---------- ściany
    struct, ins = wall_shell(fl)
    iw = unary_union([w['poly'] for w in IWALLS if w['fl'] == fl and w['kind'] in ('BEAR', 'RC', 'GAR')])
    pw = unary_union([w['poly'] for w in IWALLS if w['fl'] == fl and w['kind'] == 'PART'])
    rcw = unary_union([w['poly'] for w in IWALLS if w['fl'] == fl and w['kind'] == 'RC'] +
                      [z.intersection(struct) for z in RC_ZONES[fl]])
    ops = [o for o in OPENINGS if o['fl'] == fl]
    cut = unary_union([op_box(o) for o in ops])
    struct_c = struct.union(iw).difference(cut)
    ins_c = ins.difference(cut)
    if fl == 'P0':
        ins_c = ins_c.union(box(AX['F'] + STR, 0.105, AX['F'] + GAR_IN, AY['4'] - EXT_IN).difference(cut))
    draw_geom(ax, ins_c, fc=C['ins'], ec='k', lw=0.35, z=4)
    draw_geom(ax, struct_c, fc=C['sil'], ec='k', lw=0.55, z=4)
    draw_geom(ax, rcw.difference(cut), fc=C['rc'], ec='k', lw=0.55, hatch='////', z=4.2)
    draw_geom(ax, pw.difference(cut), fc=C['part'], ec='k', lw=0.45, z=4)
    # otwory
    for o in ops:
        if o['kind'] in ('win', 'fix', 'hs'):
            draw_window(ax, o)
        elif o['kind'] in ('door', 'door_ext'):
            draw_door(ax, o)
        elif o['kind'] == 'gate':
            b0, b1 = op_band(o)
            ax.plot([o['a0'], o['a1']], [b1 - 0.05, b1 - 0.05], color='k', lw=0.6, ls=(0, (4, 2)), zorder=6)
            ax.text((o['a0'] + o['a1']) / 2, b1 + 0.25, 'BG1 brama segmentowa 500×225', fontsize=5.5, ha='center',
                    va='bottom', color='#7a4b00', zorder=7)
        elif o['kind'] == 'bay':
            b0, b1 = op_band(o)
            ax.add_patch(Rectangle((o['a0'], b0), o['a1'] - o['a0'], b1 - b0, fc='#dcdcdc', ec='k', lw=0.4, zorder=5))
            ax.text((o['a0'] + o['a1']) / 2, (b0 + b1) / 2, 'parapet/siedzisko h=0,55 — otwór 3,70–5,20', fontsize=4.6,
                    ha='center', va='center', zorder=6)
    # przeszklenie strefy dziennej P0
    if fl == 'P0':
        gx0, gx1 = GLAZ_X
        ax.add_patch(Rectangle((gx0, -0.25), gx1 - gx0, 0.15, fc='white', ec='k', lw=0.5, zorder=5))
        ax.plot([gx0, gx1], [-0.175, -0.175], color='k', lw=0.4, zorder=6)
        for i, mx in enumerate(MULLIONS):
            ax.add_patch(Rectangle((mx - 0.03, -0.27), 0.06, 0.19, fc='k', zorder=6))
        for i in range(5):
            a, b = MULLIONS[i], MULLIONS[i + 1]
            lab = 'HS' if i in (1, 3) else 'FIX'
            ax.text((a + b) / 2, -0.52, f'E{i + 1} {lab} {round((b - a) * 100)}×270', fontsize=5.2, ha='center',
                    va='center', color='#7a4b00', zorder=7)
            if lab == 'HS':
                ax.annotate('', xy=(b - 0.3, -0.175), xytext=(a + 0.3, -0.175),
                            arrowprops=dict(arrowstyle='<->', lw=0.5), zorder=7)
        for (cx, cy) in COLUMNS:
            ax.add_patch(Rectangle((cx - 0.06, cy - 0.06), 0.12, 0.12, fc='#1b2631', ec='k', lw=0.3, zorder=7))
        ax.text(COLUMNS[0][0] + 0.1, 0.18, 'SL1', fontsize=5, zorder=7)
        ax.text(COLUMNS[-1][0] + 0.1, 0.18, 'SL4', fontsize=5, zorder=7)
        ax.text(6.8, -0.95, 'słupy stalowe RK 120×120×8 za słupkami fasady (SL1–SL4), belka ukryta w ST1',
                fontsize=5.2, ha='center', va='center', color='#1b2631', zorder=7)
    draw_stairs(ax, fl)
    # wyposażenie
    for kind, g, t in furniture(fl):
        if kind == 'r':
            x0, y0, x1, y1 = g
            ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fc='none', ec='#8c8c8c', lw=0.4, zorder=3))
        else:
            ax.add_patch(Circle(g[:2], g[2], fc='none', ec='#8c8c8c', lw=0.4, zorder=3))
            if t:
                ax.text(g[0], g[1], t, fontsize=4, ha='center', va='center', color='#777', zorder=3)
    # piony
    for p in PIONY:
        x, y = p['xy']
        ax.add_patch(Circle((x, y), 0.09, fc='#1a5276', ec='k', lw=0.3, zorder=8))
        ax.text(x + 0.13, y + 0.02, p['id'], fontsize=5, color='#1a5276', zorder=8)
    if fl == 'P1':
        ax.add_patch(Rectangle((3.265, 6.87), 0.33, 0.325, fc='none', ec='#1a5276', lw=0.5, hatch='////', zorder=7))
        ax.text(3.2, 6.80, 'szacht', fontsize=4.5, ha='right', va='top', color='#1a5276', zorder=7)

    # ---------- opisy pomieszczeń
    for r in rooms:
        p = r['poly']
        if r['lab']:
            cx, cy = r['lab']
        else:
            c = p.representative_point() if not p.centroid.within(p) else p.centroid
            cx, cy = c.x, c.y
        if r['id'] in ('0.09', '1.06', '2.08'):
            continue
        name = r['name']
        wmax = 18 if (p.bounds[2] - p.bounds[0]) > 2.3 else 11
        name = '\n'.join(textwrap.wrap(name, wmax))
        fs = 6.8 if r['kat'] == 'M' else 6.0
        ax.text(cx, cy, f"{r['id']}\n{name}\n{fmt(p.area)} m²", fontsize=fs, ha='center', va='center', zorder=9,
                linespacing=1.1, bbox=dict(fc='white', ec='none', alpha=0.72, pad=0.6))
    if fl == 'P0':
        ax.text(3.0, 1.35, 'SALON', fontsize=7, ha='center', color='#7a5c2e', zorder=9, fontweight='bold')
        ax.text(6.95, 0.55, 'JADALNIA', fontsize=7, ha='center', color='#7a5c2e', zorder=9, fontweight='bold')
        ax.text(10.3, 0.55, 'KUCHNIA', fontsize=7, ha='center', color='#7a5c2e', zorder=9, fontweight='bold')

    # ---------- osie
    ymax_axis = {'P0': 13.3, 'P1': 13.3, 'P2': 13.3}[fl]
    xs_axes = {'P0': ['B', 'C', 'D', 'E', 'F', 'G'], 'P1': ['A', 'C', 'D', 'E'], 'P2': ["A'", 'A', 'C', 'D', 'E']}[fl]
    ys_axes = {'P0': ['1', '2', '3', '4'], 'P1': ['1', '2', '3'], 'P2': ['1', '2', '3']}[fl]
    ybot = -7.55
    for k in xs_axes:
        x = AX[k]
        ax.plot([x, x], [ybot + 0.32, ymax_axis], color=C['axis'], lw=0.35, ls=(0, (8, 3, 1, 3)), zorder=2.5)
        axis_bubble(ax, x, ybot, k)
    xl = -6.6
    for k in ys_axes:
        y = AY[k]
        ax.plot([xl + 0.32, 21.2], [y, y], color=C['axis'], lw=0.35, ls=(0, (8, 3, 1, 3)), zorder=2.5)
        axis_bubble(ax, xl, y, k)
    if fl == 'P0':
        ax.plot([12.8, 19.4], [Y_GAR, Y_GAR], color=C['axis'], lw=0.3, ls=(0, (8, 3, 1, 3)), zorder=2.5)
        ax.text(19.5, Y_GAR, '1a', fontsize=6, color=C['axis'], va='center')

    # ---------- wymiary
    ol = OUTLINE[fl]
    bx0, by0, bx1, by1 = ol.bounds
    if fl == 'P0':
        dim_h(ax, [-1.80, -0.30, 0.70] + [round(m, 3) for m in MULLIONS[1:5]] + [12.90, 18.90], -4.95, fs=5.5)
        dim_h(ax, [0.70, 12.90, 18.90], -5.85)
        dim_h(ax, [AX[k] for k in xs_axes], -6.7)
        dim_v(ax, [-0.30, 10.80], -4.6)
        dim_v(ax, [AY[k] for k in ys_axes], -5.4)
    else:
        xs_out = [bx0, bx1]
        dim_h(ax, xs_out, -5.85)
        dim_h(ax, [AX[k] for k in xs_axes], -6.7)
        dim_v(ax, [-0.30, 7.60], -4.6)
        dim_v(ax, [AY[k] for k in ys_axes], -5.4)
        if fl == 'P1':
            dim_h(ax, [-1.80, -0.30, C_BOX['x0'], C_BOX['x1'], C_BOX['top_frame_x1'], 18.90], -4.95, fs=5.5)
            dim_v(ax, [-1.30, -0.30, 0.0], 20.0, fs=5.5)
        if fl == 'P2':
            dim_h(ax, [-2.50, -1.30, -0.30, 11.70, 12.10], -4.95, fs=5.5)
            ax.text(-0.8, -4.45, 'wspornik A', fontsize=5, ha='center', color=C['dim'])

    # ---------- tabelka i legenda
    tot_pu = sum(r['poly'].area for r in rooms if r['kat'] in ('M', 'P', 'K'))
    tot_t = sum(r['poly'].area for r in rooms if r['kat'] == 'T')
    tot_g = sum(r['poly'].area for r in rooms if r['kat'] == 'G')
    tot_s = sum(r['poly'].area for r in rooms if r['kat'] == 'S')
    ax.text(XMIN + 0.2, YMAX - 0.2, title, fontsize=12, fontweight='bold', va='top')
    info = (f"Wariant W1 — „wierność szkicowi, zwartość”   |   rzędna posadzki {fmt(FFL[fl])} m "
            f"(= {fmt(ZERO_ABS + FFL[fl])} m n.p.m.)   |   wys. w świetle 2,78 m\n"
            f"PU (mieszk.+pomocn.+komunik.): {fmt(tot_pu)} m²   |   pom. techniczne: {fmt(tot_t)} m²"
            + (f"   |   garaż + pom. gosp.: {fmt(tot_g)} m²" if tot_g else '')
            + f"   |   schody/spoczniki (poza PU): {fmt(tot_s)} m²")
    ax.text(XMIN + 0.2, YMAX - 0.85, info, fontsize=7, va='top')
    leg_y = YMAX - 2.0
    items = [(C['rc'], '////', 'żelbet (trzon, tarcze, ściany-tarcze)'), (C['sil'], None, 'mur silikat 18 cm (nośny)'),
             (C['part'], None, 'ścianka działowa 12 cm'), (C['ins'], None, 'ocieplenie 20 cm (ETICS)')]
    for i, (fc, h, t) in enumerate(items):
        ax.add_patch(Rectangle((XMIN + 0.2 + i * 5.2, leg_y), 0.5, 0.25, fc=fc, ec='k', lw=0.4, hatch=h, zorder=9))
        ax.text(XMIN + 0.85 + i * 5.2, leg_y + 0.12, t, fontsize=6, va='center', zorder=9)
    if fl in ('P0', 'P1'):
        yy = leg_y - 0.55
        if fl == 'P0':
            ax.plot([XMIN + 0.2, XMIN + 0.7], [yy + 0.12] * 2, color='#7d3c98', lw=0.9, ls=(0, (2, 2)))
            ax.text(XMIN + 0.85, yy + 0.12, 'obrys bryły B (P1) nad', fontsize=6, va='center')
        ax.plot([XMIN + 5.4, XMIN + 5.9], [yy + 0.12] * 2, color='#1f618d', lw=0.9, ls=(0, (1, 2)))
        ax.text(XMIN + 6.05, yy + 0.12, 'obrys bryły A (P2) nad', fontsize=6, va='center')
        ax.plot([XMIN + 10.6, XMIN + 11.1], [yy + 0.12] * 2, color='#555', lw=0.7, ls=(0, (6, 3)))
        ax.text(XMIN + 11.25, yy + 0.12, 'krawędź płyty stropu/dachu nad', fontsize=6, va='center')
    north_arrow(ax, 21.6, 12.6, 0.8)
    scale_bar(ax, -3.5, -7.9, 5)
    ax.text(22.5, -8.15, 'wymiary w cm', fontsize=6, ha='right', va='bottom', color=C['dim'])
    fig.savefig(os.path.join(OUT, fname), dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    plan('P0', 'RZUT PARTERU (P0)', 'rzut_P0.png')
    plan('P1', 'RZUT I PIĘTRA (P1)', 'rzut_P1.png')
    plan('P2', 'RZUT II PIĘTRA (P2)', 'rzut_P2.png')
    print('ok')
