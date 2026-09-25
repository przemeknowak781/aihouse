# -*- coding: utf-8 -*-
"""Przekroje A-A (N-S przez schody i boks C) oraz B-B (W-E przez wsporniki zachodnie i garaż) — W1."""
import os
import numpy as np
from draw_common import *
from model_w1 import *

OUT = '/home/user/aihouse/docs/20_koncepcja/W1'
CUT = dict(fc='#6a6a6a', ec='k', lw=0.6)
RC = dict(fc=C['rc'], ec='k', lw=0.6, hatch='////')
INS = dict(fc=C['ins'], ec='k', lw=0.35)
SCR = dict(fc='#d9d4c7', ec='k', lw=0.35)


def R_(ax, a0, a1, z0, z1, st, z=4):
    ax.add_patch(Rectangle((a0, z0), a1 - a0, z1 - z0, zorder=z, **st))


def glass(ax, a, z0, z1, w=0.10, z=4):
    ax.add_patch(Rectangle((a - w / 2, z0), w, z1 - z0, fc='white', ec='k', lw=0.5, zorder=z))
    ax.plot([a, a], [z0, z1], color='#1f618d', lw=0.9, zorder=z + 0.1)


def floor_ground(ax, a0, a1, zf=0.0):
    R_(ax, a0, a1, zf - 0.10, zf, SCR)
    R_(ax, a0, a1, zf - 0.30, zf - 0.10, INS)
    R_(ax, a0, a1, zf - 0.45, zf - 0.30, RC)


def footing(ax, a, w=0.70, top=-0.45):
    R_(ax, a - w / 2, a + w / 2, -1.10, -0.75, RC)
    R_(ax, a - 0.125, a + 0.125, -0.75, top, RC)


def slab(ax, a0, a1, key, hole=None, buildup=None, bz=None):
    z0, z1 = SLABS[key]
    segs = [(a0, a1)] if hole is None else [(a0, hole[0]), (hole[1], a1)]
    for s0, s1 in segs:
        R_(ax, s0, s1, z0, z1, RC)
    if buildup:
        for (b0, b1, top, kind) in buildup:
            for s0, s1 in segs:
                c0, c1 = max(b0, s0), min(b1, s1)
                if c1 > c0:
                    if kind == 'floor':
                        R_(ax, c0, c1, z1, top, SCR)
                    elif kind == 'roof':
                        R_(ax, c0, c1, z1, top - 0.10, INS)
                        R_(ax, c0, c1, top - 0.10, top, dict(fc='#b7cfa0', ec='k', lw=0.35))
                    elif kind == 'roofP2':
                        R_(ax, c0, c1, z1, top, INS)
                        ax.plot([c0, c1], [top, top], color='k', lw=1.2, zorder=5)


def ext_wall(ax, a_axis, z0, z1, out_side, openings=(), rc=False):
    """Ściana zewn. przecięta: warstwa konstr. 18 cm + tynk; ocieplenie 20 cm po stronie out_side (-1/+1)."""
    st = RC if rc else CUT
    s0, s1 = a_axis - STR, a_axis + STR
    i0, i1 = (a_axis + STR, a_axis + STR + 0.21) if out_side > 0 else (a_axis - STR - 0.21, a_axis - STR)
    zs = [z0] + [v for o in openings for v in o] + [z1]
    for k in range(0, len(zs), 2):
        if zs[k + 1] > zs[k]:
            R_(ax, s0, s1, zs[k], zs[k + 1], st)
            R_(ax, i0, i1, zs[k], zs[k + 1], INS)
    for (o0, o1) in openings:
        glass(ax, a_axis + out_side * 0.05, o0, o1, w=0.12)


def int_wall(ax, a, half, z0, z1, rc=False, openings=()):
    zs = [z0] + [v for o in openings for v in o] + [z1]
    for k in range(0, len(zs), 2):
        if zs[k + 1] > zs[k]:
            R_(ax, a - half, a + half, zs[k], zs[k + 1], RC if rc else CUT)


def terrain(ax, xs, zs, a_from=None, a_to=None):
    ax.fill_between(xs, zs, -1.6, color='#e9e3d6', zorder=0.5)
    ax.plot(xs, zs, color='#5b4a33', lw=1.2, zorder=1)


def levels(ax, x, items, side='right'):
    for txt, z in items:
        level_mark(ax, x, z, txt, side=side, fs=6.3)


def section_AA(ax):
    """Przekrój A-A w x = 5,80, widok na zachód; oś pozioma = y (południe z lewej)."""
    X = 5.80
    ys = np.linspace(-9.0, 20.0, 80)
    terrain(ax, ys, [terrain_z(X, y) for y in ys])
    # taras
    R_(ax, -4.30, -0.30, terrain_z(X, -4.3), -0.02, dict(fc='#c9b89b', ec='#6e5a3c', lw=0.5), z=2)
    # fundamenty i płyta na gruncie
    for a in (0.0, AY['2'], AY['3'], AY['4']):
        footing(ax, a)
    floor_ground(ax, -0.25, 10.80)
    R_(ax, -0.35, -0.25, -1.10, 0.0, INS)                   # ocieplenie cokołu
    R_(ax, 10.80, 10.90, -1.10, 0.0, INS)
    # P0
    glass(ax, -0.18, 0.0, 2.72, w=0.15)
    R_(ax, -0.30, 0.10, 2.72, 2.78, dict(fc=C['frame'], ec='k', lw=0.3))
    int_wall(ax, AY['2'], H_BEAR, 0.0, 2.78, rc=True)
    int_wall(ax, AY['3'], H_BEAR, 0.0, 2.78, rc=True)
    int_wall(ax, 8.80, H_PART, 0.0, 2.78)
    ext_wall(ax, AY['4'], 0.0, 2.78, +1)
    # schody (przekroje poprzeczne biegów w x = 5,80) — pasmo N: bieg w górę na zach.; pasmo S: bieg na wsch.
    s = STAIR
    for base in (0.0, H_KOND):
        zN = base + (int((s['flights'][1] - X) / s['s']) + 1) * s['h']
        zS = base + 1.575 + (int((X - s['flights'][0]) / s['s']) + 1) * s['h']
        R_(ax, s['lane_N'][0], s['lane_N'][1], zN - 0.36, zN, dict(fc='#8d8d8d', ec='k', lw=0.5))
        R_(ax, s['lane_S'][0], s['lane_S'][1], zS - 0.36, zS, dict(fc='#8d8d8d', ec='k', lw=0.5))
        ax.plot([s['lane_S'][1] + 0.05] * 2, [zS, zS + 0.95], color='#1a5276', lw=1.0, zorder=5)
    # spoczniki międzykondygnacyjne widoczne za płaszczyzną (x 3,8–4,86)
    for zl in (1.575, 1.575 + H_KOND):
        ax.add_patch(Rectangle((s['y0'], zl - 0.20), s['y1'] - s['y0'], 0.20, fc='none', ec='#777', lw=0.5, ls='--',
                               zorder=3))
    # ST1 z otworem na schody
    slab(ax, -1.30, 10.80, 'ST1', hole=(s['y0'], s['y1']),
         buildup=[(-0.30, 7.60, 3.15, 'floor'), (7.60, 10.50, GREEN_TOP, 'roof')])
    R_(ax, -1.30, -1.05, EDGE['ST1'][0], 3.00, dict(fc=C['conc'], ec='k', lw=0.5))
    R_(ax, 10.50, 10.80, 3.00, D_TOP, CUT)                  # attyka dachu zielonego
    # boks C (x = 5,80 w obrębie boksu)
    R_(ax, -1.30, -0.30, 3.00, C_BOX['z_sill'], dict(fc=C['ins'], ec='k', lw=0.5))
    R_(ax, -1.30, -1.20, 3.00, C_BOX['z_sill'], dict(fc=C['conc'], ec='k', lw=0.4))
    glass(ax, C_BOX['glass_y'], C_BOX['z_sill'], C_BOX['z_head'], w=0.12)
    R_(ax, -1.30, -0.30, C_BOX['z_head'], C_BOX['z_top'], dict(fc=C['conc'], ec='k', lw=0.5))
    ext_wall(ax, AY['1'], 3.00, 5.93, -1, openings=[(C_BOX['z_sill'], C_BOX['z_head'])], rc=True)
    ax.text(-0.8, 3.35, 'siedzisko\n+3,70', fontsize=5, ha='center', va='center', zorder=6)
    # P1
    int_wall(ax, AY['2'], H_BEAR, 3.00, 5.93, rc=True)
    ext_wall(ax, AY['3'], 3.00, 5.93, +1, rc=True)
    # ST2
    slab(ax, -1.30, 7.60, 'ST2', hole=(s['y0'], s['y1']), buildup=[(-0.30, 7.60, 6.30, 'floor')])
    R_(ax, -1.30, -1.05, EDGE['ST2'][0], EDGE['ST2'][1], dict(fc=C['conc'], ec='k', lw=0.5))
    # P2
    ext_wall(ax, AY['1'], 6.15, 9.08, -1, openings=[(6.90, 9.00)], rc=True)
    ax.add_patch(Rectangle((LAMELE['y'] - 0.10, LAMELE['z0']), 0.20, LAMELE['z1'] - LAMELE['z0'], fc=C['wood'],
                           ec='#6e4f2f', lw=0.4, zorder=4))
    int_wall(ax, 3.00, H_PART, 6.30, 9.08)
    int_wall(ax, AY['2'], H_BEAR, 6.15, 9.08, rc=True)
    ext_wall(ax, AY['3'], 6.15, 9.08, +1, rc=True)
    # balustrada pustki P2 (widok)
    ax.plot([s['y0'], s['y1']], [6.30 + 1.10, 6.30 + 1.10], color='#1a5276', lw=0.8, ls='--', zorder=5)
    # ST3 + dach + świetlik
    slab(ax, -1.10, 7.60, 'ST3', hole=(SKYLIGHT.bounds[1], SKYLIGHT.bounds[3]),
         buildup=[(-0.30, 7.30, ROOF_TOP, 'roofP2')])
    R_(ax, -1.10, -0.85, EDGE['ST3'][0], ATTIC_TOP, dict(fc=C['conc'], ec='k', lw=0.5))
    R_(ax, 7.30, 7.60, 9.30, ATTIC_TOP, CUT)
    R_(ax, SKYLIGHT.bounds[1] - 0.15, SKYLIGHT.bounds[1], 9.30, 9.95, CUT)
    R_(ax, SKYLIGHT.bounds[3], SKYLIGHT.bounds[3] + 0.15, 9.30, 9.95, CUT)
    ax.plot([SKYLIGHT.bounds[1] - 0.15, SKYLIGHT.bounds[3] + 0.15], [9.97, 9.97], color='#1f618d', lw=2.0, zorder=5)
    # opisy
    for txt, yy, zz in [('JADALNIA', 2.4, 1.3), ('schody\n18×17,5/28', 6.05, 2.9), ('HOL', 8.05, 1.3),
                        ('GARD.', 9.65, 1.3), ('POKÓJ RODZINNY\n/ BIBLIOTEKA', 2.4, 4.6), ('GABINET', 1.5, 7.7),
                        ('HOL', 3.9, 7.7), ('pustka\nklatki', 6.05, 7.8), ('dach zielony', 9.0, 3.65),
                        ('BOKS C', -0.8, 4.5)]:
        ax.text(yy, zz, txt, fontsize=6.3, ha='center', va='center', zorder=6, color='#333')
    for yy, z0, z1 in [(2.4, 0.0, 2.78), (2.4 + 0.9, 3.15, 5.93), (1.5 + 0.9, 6.30, 9.08)]:
        ax.annotate('', xy=(yy, z1), xytext=(yy, z0), arrowprops=dict(arrowstyle='<->', lw=0.5, color=C['dim']),
                    zorder=6)
        ax.text(yy + 0.12, (z0 + z1) / 2 - 0.35, 'h=2,78', fontsize=5.5, color=C['dim'], rotation=90, zorder=6)
    ax.text(-8.8, 11.2, 'PRZEKRÓJ A-A  (x = 5,80, widok na zachód)', fontsize=10.5, fontweight='bold', va='top')
    ax.text(-8.8, 10.55, 'płd. ←                                                              → płn.', fontsize=7,
            va='top')
    levels(ax, 13.8, [('±0,00 = 101,65', 0.0), ('+2,78', 2.78), ('+3,15', 3.15), ('+3,70 linia D', D_TOP),
                      ('+5,93', 5.93), ('+6,30', 6.30), ('+9,08', 9.08), ('+9,30', 9.30), ('+9,85', ATTIC_TOP),
                      ('-1,10 spód ław', -1.10)])
    zt = terrain_z(X, 10.8)
    level_mark(ax, 12.2, zt, f'teren {fmt(zt)}', fs=6)
    zmin = terrain_z(0.70, 2.00)
    ax.annotate('', xy=(16.2, ATTIC_TOP), xytext=(16.2, zmin), arrowprops=dict(arrowstyle='<->', lw=0.8, color='#c0392b'),
                zorder=7)
    ax.text(16.35, 4.6, f'wysokość budynku wg § 6 WT\n(od terenu przy najniżej\npołożonym wejściu {fmt(zmin)})\n'
            f'H = {fmt(ATTIC_TOP - zmin)} m ≤ 11,00 m', fontsize=6.3, color='#c0392b', va='center', zorder=7)
    dim_h(ax, [-1.30, -0.30, AY['2'], AY['3'], AY['4'], 10.80], -2.0, fs=6)
    dim_v(ax, [0.0, 3.15, 6.30, 9.30, ATTIC_TOP], -6.0, fs=6)
    ax.set_xlim(-9.0, 19.8)
    ax.set_ylim(-2.6, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')


def section_BB(ax):
    """Przekrój B-B w y = 2,00, widok na północ; oś pozioma = x."""
    Y = 2.00
    xs = np.linspace(-8.0, 26.0, 80)
    terrain(ax, xs, [terrain_z(x, Y) for x in xs])
    R_(ax, -1.80, 0.70, terrain_z(-1.8, Y), -0.02, dict(fc='#c9b89b', ec='#6e5a3c', lw=0.5), z=2)
    for a in (AX['B'], AX['F'], AX['G']):
        footing(ax, a)
    floor_ground(ax, 0.75, 18.85)
    R_(ax, 0.60, 0.70, -1.10, 0.0, INS)
    R_(ax, 18.90, 19.00, -1.10, 0.0, INS)
    # P0: ściana zach. (ŻB) z otworem HS, F, G
    ext_wall(ax, AX['B'], 0.0, 2.78, -1, openings=[(0.0, 2.60)], rc=True)
    int_wall(ax, AX['F'], 0.105, 0.0, 2.78)
    R_(ax, AX['F'] + STR, AX['F'] + GAR_IN, 0.0, 2.78, INS)
    ext_wall(ax, AX['G'], 0.0, 2.78, +1)
    # ST1
    slab(ax, -1.80, 18.90, 'ST1', buildup=[(-0.30, 11.70, 3.15, 'floor'), (11.70, 18.60, GREEN_TOP, 'roof')])
    R_(ax, -0.30, 0.70, 2.58, 2.78, INS)                    # ocieplenie spodu stropu nad powietrzem zewn.
    R_(ax, -1.80, -1.55, EDGE['ST1'][0], 3.05, dict(fc=C['conc'], ec='k', lw=0.5))
    R_(ax, 18.60, 18.90, 3.00, D_TOP, CUT)
    ax.plot([-0.30, -0.30], [2.78, 3.00], color='#c0392b', lw=2.5, zorder=6)      # łącznik termoizolacyjny
    # P1: ściana zach. (ŻB) z oknem pok. 1.01, ścianka x=3,70, ściana wsch. (ŻB)
    ext_wall(ax, AX['A'], 3.00, 5.93, -1, openings=[(4.00, 5.60)], rc=True)
    int_wall(ax, AX['C'], H_PART, 3.15, 5.93)
    ext_wall(ax, AX['E'], 3.00, 5.93, +1, rc=True)
    # ST2
    slab(ax, -2.50, 12.10, 'ST2', buildup=[(-1.30, 11.70, 6.30, 'floor')])
    R_(ax, -1.30, -0.30, 5.73, 5.93, INS)
    R_(ax, -2.50, -2.25, EDGE['ST2'][0], EDGE['ST2'][1], dict(fc=C['conc'], ec='k', lw=0.5))
    ax.plot([-1.30, -1.30], [5.93, 6.15], color='#c0392b', lw=2.5, zorder=6)
    ax.plot([11.70, 11.70], [5.93, 6.15], color='#c0392b', lw=2.5, zorder=6)
    # P2
    ext_wall(ax, AX["A'"], 6.15, 9.08, -1, openings=[(7.20, 8.80)], rc=True)
    for zz in np.arange(6.3, 9.06, 0.001)[:1]:
        pass
    ax.add_patch(Rectangle((LAMELE['west_x'] - 0.10, LAMELE['z0']), 0.20, LAMELE['z1'] - LAMELE['z0'], fc=C['wood'],
                           ec='#6e4f2f', lw=0.4, zorder=4))
    int_wall(ax, AX['C'], H_PART, 6.30, 9.08)
    int_wall(ax, AX['D'], H_PART, 6.30, 9.08)
    ext_wall(ax, AX['E'], 6.15, 9.08, +1, openings=[(7.20, 8.80)], rc=True)
    # ST3
    slab(ax, -2.10, 12.10, 'ST3', buildup=[(-1.00, 11.40, ROOF_TOP, 'roofP2')])
    R_(ax, -2.10, -1.85, EDGE['ST3'][0], ATTIC_TOP, dict(fc=C['conc'], ec='k', lw=0.5))
    R_(ax, 11.85, 12.10, EDGE['ST3'][0], ATTIC_TOP, dict(fc=C['conc'], ec='k', lw=0.5))
    ax.plot([-1.30, -1.30], [9.08, 9.30], color='#c0392b', lw=2.5, zorder=6)
    ax.plot([11.70, 11.70], [9.08, 9.30], color='#c0392b', lw=2.5, zorder=6)
    # tarcze — schemat ścieżki obciążeń strefy zachodniej
    path = [(AX["A'"] + 0.35, 8.6), (AX["A'"] + 0.35, 6.45), (AX['A'] + 0.35, 6.45), (AX['A'] + 0.35, 3.35),
            (AX['B'] + 0.35, 3.35), (AX['B'] + 0.35, -0.6)]
    for p0, p1 in zip(path[:-1], path[1:]):
        ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='->', color='#c0392b', lw=1.3), zorder=7)
    ax.text(-4.0, 6.8, 'ściany-tarcze ŻB\nN i S (P1, P2)\nwspornik 1,00 + 1,00 m\n→ ściana ŻB osi B\n→ ława', fontsize=6,
            color='#c0392b', ha='center', va='center', zorder=7)
    for txt, xx, zz in [('SALON', 3.0, 1.3), ('JADALNIA', 7.0, 1.3), ('KUCHNIA', 10.2, 1.3), ('POM. GOSP.', 15.7, 1.3),
                        ('POKÓJ 1.01', 1.8, 4.5), ('POKÓJ RODZINNY', 7.5, 4.5), ('SYPIALNIA', 1.3, 7.7),
                        ('GABINET', 6.1, 7.7), ('POKÓJ 2.06', 9.95, 7.7), ('dach zielony (garaż)', 15.3, 3.7),
                        ('taras zach.\npod okapem', -0.6, 1.2)]:
        ax.text(xx, zz, txt, fontsize=6.3, ha='center', va='center', zorder=6, color='#333')
    ax.text(-7.8, 11.2, 'PRZEKRÓJ B-B  (y = 2,00, widok na północ)', fontsize=10.5, fontweight='bold', va='top')
    ax.text(-7.8, 10.55, 'zach. ←                                                                  → wsch.',
            fontsize=7, va='top')
    ax.text(3.0, -2.35, 'czerwone kreski = łączniki termoizolacyjne płyt wspornikowych (np. typu KXT) w linii ocieplenia',
            fontsize=6, color='#c0392b')
    levels(ax, 22.8, [('±0,00', 0.0), ('+2,78', 2.78), ('+3,15', 3.15), ('+5,93', 5.93), ('+6,30', 6.30),
                      ('+9,08', 9.08), ('+9,85', ATTIC_TOP)])
    dim_h(ax, [-2.50, -1.80, -1.30, -0.30, 0.70, AX['C'], 11.70, 12.90, 18.90], -1.75, fs=5.8)
    ax.set_xlim(-8.0, 26.5)
    ax.set_ylim(-2.6, 11.5)
    ax.set_aspect('equal')
    ax.axis('off')


def sections_figure():
    fig = plt.figure(figsize=(17, 14.5))
    gs = fig.add_gridspec(2, 1, hspace=0.05)
    section_AA(fig.add_subplot(gs[0]))
    section_BB(fig.add_subplot(gs[1]))
    fig.savefig(os.path.join(OUT, 'przekroj.png'), dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    sections_figure()
    print('ok')
