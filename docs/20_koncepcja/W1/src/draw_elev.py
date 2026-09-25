# -*- coding: utf-8 -*-
"""Elewacja południowa (ogrodowa) W1 + porównanie ze szkicem."""
import os
import numpy as np
from PIL import Image
from draw_common import *
from model_w1 import *

OUT = '/home/user/aihouse/docs/20_koncepcja/W1'
SK = '/home/user/aihouse/00_wejscie/szkic_koncepcyjny.jpg'
# kalibracja szkicu (px oryginału 2576x1932): lico zach. bryły B = 1059,5 px, skala 45,6 px/m, teren ~1512 px
PX_B, PX_M, PY_G = 1059.5, 45.6, 1512.0
L2X = lambda L: L - 0.30          # L = odległość od lica zach. bryły B -> x układu budynku


def rect(ax, x0, x1, z0, z1, fc, ec='k', lw=0.5, z=3, alpha=1.0, hatch=None):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, hatch=hatch))


def shadow(ax, x0, x1, z0, z1, z=3.5):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, fc='k', ec='none', alpha=0.16, zorder=z))


def draw_elevation(ax, labels=True):
    tz = lambda x: terrain_z(x, -0.30)
    # ---------------- plan dalszy: bryła A (P2), ściana za lamelami
    rect(ax, -1.30, 11.70, 6.15, 9.08, '#55595e', z=2)
    for (a0, a1) in [(-0.30, 2.70), (4.60, 7.60), (8.90, 10.90)]:     # okna P2 za lamelami
        rect(ax, a0, a1, 6.90, 9.00, '#7f98a8', ec='#222', lw=0.4, z=2.1)
    shadow(ax, -1.30, 11.70, 9.08 - 0.80, 9.08, z=2.2)
    # ---------------- bryła B (P1)
    rect(ax, -0.30, 11.70, 3.00, 5.93, C['render'], z=2)
    shadow(ax, -0.30, 11.70, 5.90 - 1.00, 5.93, z=2.2)
    # ---------------- parter E: przeszklenie + narożniki, garaż G
    rect(ax, 0.70, 1.105, 0.0, 2.78, C['render'], z=2)
    rect(ax, 12.495, 18.90, -0.12, 2.78, C['render'], z=2)
    gx0, gx1 = GLAZ_X
    rect(ax, gx0, gx1, 0.0, 2.72, '#6f8fa3', ec=C['frame'], lw=0.8, z=2)
    for i in range(5):
        a, b = MULLIONS[i], MULLIONS[i + 1]
        # refleks
        ax.add_patch(MPoly([(a + 0.3, 0.2), (a + 0.9, 0.2), (a + 1.9, 2.5), (a + 1.3, 2.5)], closed=True,
                           fc='white', alpha=0.10, zorder=2.05))
    for m in MULLIONS:
        rect(ax, m - 0.04, m + 0.04, 0.0, 2.72, C['frame'], ec='none', z=2.1)
    rect(ax, gx0, gx1, 2.66, 2.78, C['frame'], ec='none', z=2.1)                 # kaseta osłony ZIP
    shadow(ax, -1.80, 18.90, 2.70 - 1.00, 2.78, z=2.3)
    # ---------------- boks C (przed licem B, y = -1,30)
    gx = C_BOX['glass_x']
    rect(ax, gx[0], gx[1], C_BOX['z_sill'], C_BOX['z_head'], '#6f8fa3', ec=C['frame'], lw=0.6, z=4)
    for k in range(1, 3):
        mx = gx[0] + k * (gx[1] - gx[0]) / 3
        rect(ax, mx - 0.05, mx + 0.05, C_BOX['z_sill'], C_BOX['z_head'], C['frame'], ec='none', z=4.1)
    for k in range(3):
        a = gx[0] + k * (gx[1] - gx[0]) / 3
        ax.add_patch(MPoly([(a + 0.3, 3.8), (a + 0.8, 3.8), (a + 1.5, 5.1), (a + 1.0, 5.1)], closed=True,
                           fc='white', alpha=0.12, zorder=4.05))
    shadow(ax, gx[0], gx[1], C_BOX['z_head'] - 0.20, C_BOX['z_head'], z=4.2)
    rect(ax, C_BOX['x0'], gx[0], C_BOX['z_sill'], C_BOX['z_top'], C['conc'], z=4.3)
    rect(ax, gx[1], C_BOX['x1'], C_BOX['z_sill'], C_BOX['z_top'], C['conc'], z=4.3)
    rect(ax, C_BOX['x0'], C_BOX['top_frame_x1'], C_BOX['z_head'], C_BOX['z_top'], C['conc'], z=4.3)
    # ---------------- płyty: E (ST1) cienka krawędź, D gruba krawędź, ST2, dach ST3
    rect(ax, -1.80, C_BOX['x0'], EDGE['ST1'][0], EDGE['ST1'][1], C['conc'], z=4.4)
    rect(ax, C_BOX['x0'], 18.90, EDGE['D'][0], EDGE['D'][1], C['conc'], z=4.4)
    ax.plot([C_BOX['x0'], 18.90], [3.05, 3.05], color='#6d6b66', lw=0.4, zorder=4.45)   # styk płyta/pas D
    rect(ax, -2.50, 12.10, EDGE['ST2'][0], EDGE['ST2'][1], C['conc'], z=4.4)
    rect(ax, -2.10, 12.10, EDGE['ST3'][0], EDGE['ST3'][1], C['conc'], z=4.4)
    # ---------------- lamele (przed ścianą A, y = -0,45)
    L = LAMELE
    x = L['x0']
    while x <= L['x1'] + 1e-6:
        rect(ax, x - L['b'] / 2, x + L['b'] / 2, L['z0'] - 0.10, L['z1'] + 0.0, C['wood'], ec='#6e4f2f', lw=0.25, z=3)
        x += L['step']
    shadow(ax, -1.30, 11.70, 9.05 - 0.65, 9.05, z=3.2)
    # ---------------- jednostka PC (za narożem garażu, od wschodu)
    rect(ax, 20.20, 21.30, tz(20.7) + 0.15, tz(20.7) + 1.45, '#c9c9c9', z=1.5)
    # ---------------- taras, teren
    xs = np.linspace(-8.5, 26.0, 60)
    ax.fill_between(xs, [terrain_z(x, -4.30) for x in xs], -1.6, color='#e7e1d5', zorder=5)
    ax.plot(xs, [terrain_z(x, -4.30) for x in xs], color='#5b4a33', lw=1.2, zorder=5.1)
    rect(ax, -1.80, 12.90, terrain_z(0, -4.3), -0.02, '#c9b89b', ec='#6e5a3c', lw=0.5, z=5.2)
    # granice działki
    for xb, lab in [(-7.30, 'granica działki (W)'), (24.70, 'granica działki (E)')]:
        ax.plot([xb, xb], [-1.5, 7.5], color='#999', lw=0.7, ls=(0, (6, 3)), zorder=1)
        ax.text(xb + 0.15, 7.4, lab, fontsize=6, ha='left', va='top', color='#777', rotation=90)
    # drzewa (skala)
    for tx, r, h in [(-5.0, 1.9, 5.8), (21.9, 1.3, 4.6)]:
        rect(ax, tx - 0.12, tx + 0.12, terrain_z(tx, -4.3), h - r, '#6b5a45', ec='none', z=0.9)
        ax.add_patch(Circle((tx, h), r, fc='#9dbb86', ec='#6f8f58', lw=0.5, alpha=0.55, zorder=0.95))
    # człowiek 1,75 m
    px = 14.3
    ax.add_patch(Circle((px, -0.02 + 1.62), 0.11, fc='#444', zorder=6))
    rect(ax, px - 0.18, px + 0.18, terrain_z(px, -4.3), -0.02 + 1.50, '#444', ec='none', z=6)


def elevation_figure():
    fig = plt.figure(figsize=(17, 13.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.08], hspace=0.08)
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    XMIN, XMAX = -8.6, 27.5
    # ---------------- szkic
    im = Image.open(SK).convert('L')
    x0p, x1p, y0p, y1p = 700, 2010, 880, 1545
    crop = np.asarray(im.crop((x0p, y0p, x1p, y1p)))
    ext = [L2X((x0p - PX_B) / PX_M), L2X((x1p - PX_B) / PX_M), (PY_G - y1p) / PX_M, (PY_G - y0p) / PX_M]
    ax0.imshow(crop, cmap='gray', extent=ext, aspect='equal', zorder=0, alpha=0.95)
    ax0.set_xlim(XMIN, XMAX)
    ax0.set_ylim(ext[2], ext[3])
    ax0.axis('off')
    ax0.set_title('SZKIC (serwetka) — skalibrowany w poziomie: lico zach. bryły B = 12,00 m;  czerwone linie = położenia '
                  'krawędzi w projekcie W1', fontsize=9, loc='left')
    # ---------------- elewacja
    draw_elevation(ax1)
    ax1.set_xlim(XMIN, XMAX)
    ax1.set_ylim(-2.2, 12.4)
    ax1.set_aspect('equal')
    ax1.axis('off')
    # linie porównawcze (x) na obu panelach
    keys = [(-2.50, 'ST2'), (-1.80, 'E pł.'), (-1.30, 'A'), (-0.30, 'B'), (0.70, 'E'), (C_BOX['x0'], 'C'),
            (11.70, 'B/A'), (12.90, 'E/G'), (C_BOX['top_frame_x1'], 'rama C'), (18.90, 'D/G')]
    for xk, lab in keys:
        for a in (ax0, ax1):
            a.axvline(xk, color='#c0392b', lw=0.6, ls=(0, (4, 3)), alpha=0.75, zorder=10)
        ax0.text(xk, ext[3] - 0.2, lab, fontsize=6.5, color='#c0392b', ha='center', va='top', rotation=90,
                 bbox=dict(fc='white', ec='none', alpha=0.7, pad=0.3), zorder=11)
    # rzędne
    xr = 13.9
    for txt, z, _ in [('±0,00', 0.0, ''), ('+3,15', 3.15, ''), ('+3,70 (linia D)', D_TOP, ''), ('+6,30', 6.30, ''),
                      ('+9,85 attyka', ATTIC_TOP, '')]:
        level_mark(ax1, 23.8, z, txt, side='right', fs=6.5)
        ax1.plot([19.2, 23.3], [z, z], color='#999', lw=0.3, ls=':', zorder=1)
    level_mark(ax1, 23.8, terrain_z(24.0, -0.30) - 0.35, f'teren {fmt(terrain_z(24.0, -0.30))}', side='right', fs=6.0)
    # wymiary poziome względem lica zach. B (jak odczyt szkicu)
    dim_h(ax1, [-2.50, -1.80, -1.30, -0.30, 0.70, C_BOX['x0'], 11.70, 12.90, C_BOX['top_frame_x1'], 18.90], -0.95,
          fs=5.8)
    dim_h(ax1, [-2.50, 18.90], -1.75, fs=6.5)
    ax1.text(-8.4, -1.0, 'wymiary w cm', fontsize=6, color=C['dim'])
    ax1.text(-8.4, 12.2, 'ELEWACJA POŁUDNIOWA (OGRODOWA) — WARIANT W1', fontsize=12, fontweight='bold', va='top')
    ax1.text(-8.4, 11.55,
             'A — II piętro w lamelach, wspornik 1,00 m na zachód poza lico B, płyta ST2 wysunięta 1,20 m (zach.) / 1,00 m (płd.)\n'
             'B — I piętro, bryła pełna 12,00 m;  C — przeszklony boks w ramie, 3 kwatery 7,10 m, rama wysunięta 1,00 m, rama górna do 13,45\n'
             'D — linia krawędzi stropu nad parterem, biegnie na wschód nad garażem do narożnika G (19,20 m od lica B) — BEZ TARASU (dach zielony)\n'
             'E — parter: ciągłe przeszklenie 5 kwater (11,39 m), płyta ST1 wysunięta 1,50 m na zachód i 1,00 m na południe (okap)',
             fontsize=6.8, va='top', linespacing=1.35)
    for lab, xx, zz in [('A', 5.2, 7.6), ('B', 1.8, 4.3), ('C', 7.7, 4.45), ('D', 16.5, 3.2), ('E', 6.8, 1.2),
                        ('G', 15.9, 1.3)]:
        ax1.text(xx, zz, lab, fontsize=13, fontweight='bold', color='#c0392b', ha='center', va='center', zorder=12,
                 bbox=dict(boxstyle='circle,pad=0.25', fc='white', ec='#c0392b', lw=1.0, alpha=0.9))
    # „S” — rytm przesunięć
    sx = [5.0, -0.8, -0.8, 13.0, 13.0, 18.3, 18.3, 1.5]
    sz = [8.9, 8.9, 5.6, 5.6, 3.4, 3.4, 0.5, 0.5]
    ax1.plot([-1.9, 11.0], [8.7, 8.7], color='#f1c40f', lw=0, zorder=0)
    ax1.annotate('', xy=(-1.9, 7.1), xytext=(6.5, 7.1), arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2.0),
                 zorder=12)
    ax1.annotate('', xy=(18.2, 4.2), xytext=(8.5, 4.2), arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2.0),
                 zorder=12)
    ax1.annotate('', xy=(-1.7, 1.6), xytext=(9.0, 1.6), arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2.0),
                 zorder=12)
    ax1.text(2.6, 7.35, 'zachód', fontsize=6.5, color='#b9570f', zorder=12, ha='center', bbox=dict(fc='white', ec='none', pad=0.2))
    ax1.text(15.4, 4.45, 'wschód', fontsize=6.5, color='#b9570f', zorder=12, ha='center')
    ax1.text(3.8, 1.85, 'zachód', fontsize=6.5, color='#b9570f', zorder=12, ha='center', bbox=dict(fc='white', ec='none', pad=0.2))
    ax1.text(19.4, 9.3, 'Rytm przesunięć brył\nZACHÓD – WSCHÓD – ZACHÓD\n= sylweta „S”',
             fontsize=7.5, color='#b9570f', ha='left', va='top', zorder=12)
    fig.savefig(os.path.join(OUT, 'elewacja_S.png'), dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)


if __name__ == '__main__':
    elevation_figure()
    print('ok')
