# -*- coding: utf-8 -*-
"""Zagospodarowanie działki — wariant W1."""
import os
import numpy as np
from shapely.geometry import box, Point, LineString
from shapely.ops import unary_union
from draw_common import *
from model_w1 import *

OUT = '/home/user/aihouse/docs/20_koncepcja/W1'

EXTRA_PAVED = dict(
    east_path=box(18.90, -1.60, 20.10, 2.20),
    south_strip=box(12.90, -1.60, 20.10, -0.30),
    west_side=SITE['path_side'],
)


def site_metrics():
    P0 = OUTLINE['P0']
    enclosed = unary_union([OUTLINE['P0'], OUTLINE['P1'], OUTLINE['P2'],
                            box(C_BOX['x0'], C_BOX['y0'], C_BOX['x1'], C_BOX['y1'])])
    all_proj = unary_union([enclosed, ST1_POLY, ST2_POLY, ST3_POLY,
                            box(11.70, C_BOX['y0'], C_BOX['top_frame_x1'], C_BOX['y1'])])
    paved = unary_union([SITE['driveway'], SITE['path'], SITE['terrace_S'], SITE['terrace_W'], SITE['bins'],
                         SITE['hp_pad']] + list(EXTRA_PAVED.values())).difference(P0)
    pbc = PLOT.area - P0.area - paved.area
    green_roof = unary_union([ST1_POLY.difference(OUTLINE['P1']).difference(CANOPY_N)]).difference(
        box(-1.80, -1.30, 0.70, 7.60)).difference(box(-1.80, -1.30, 18.90, -0.30))
    gfa = OUTLINE['P0'].area + OUTLINE['P1'].area + C_BOX_area() + OUTLINE['P2'].area
    return dict(P0=P0.area, enclosed=enclosed.area, all_proj=all_proj.area, paved=paved.area, pbc=pbc,
                green_roof=green_roof.area, gfa=gfa, intens=gfa / PLOT.area, plot=PLOT.area)


def C_BOX_area():
    return (C_BOX['x1'] - C_BOX['x0']) * (C_BOX['y1'] - C_BOX['y0'])


def dist_label(ax, p0, p1, txt, color='#b03a2e', fs=6.5, off=(0, 0.25), rot=0):
    ax.annotate('', xy=p1, xytext=p0, arrowprops=dict(arrowstyle='<->', color=color, lw=0.8), zorder=12)
    ax.text((p0[0] + p1[0]) / 2 + off[0], (p0[1] + p1[1]) / 2 + off[1], txt, fontsize=fs, color=color, ha='center',
            va='bottom', rotation=rot, zorder=12, bbox=dict(fc='white', ec='none', alpha=0.8, pad=0.4))


def site_figure():
    m = site_metrics()
    fig, ax = plt.subplots(figsize=(15.5, 17.5))
    ax.set_xlim(-12.5, 36.0)
    ax.set_ylim(-35.5, 31.5)
    ax.set_aspect('equal')
    ax.axis('off')
    # działka, zieleń
    draw_geom(ax, PLOT, fc='#e6f0dc', ec='none', z=0.5)
    # droga
    draw_geom(ax, ROAD, fc='#eeeeee', ec='none', z=0.4)
    draw_geom(ax, CARRIAGEWAY, fc='#bdbdbd', ec='#888', lw=0.5, z=0.45)
    ax.plot([-12, 30], [29.0, 29.0], color='#666', lw=0.8, ls=(0, (10, 3, 2, 3)))
    ax.text(9.0, 24.0, 'ul. Lipowa (fikc.) — droga gminna kl. D, 1KDD, w liniach rozgraniczających 10,0 m',
            fontsize=7.5, ha='center', va='center', color='#333')
    ax.text(9.0, 20.0, 'pobocze / chodnik', fontsize=6, ha='center', color='#666')
    # zjazd
    draw_geom(ax, box(12.9, 19.0, 18.9, 21.5), fc='#d6d6d6', ec='#888', lw=0.4, z=0.6)
    draw_geom(ax, box(7.05, 19.0, 8.55, 21.5), fc='#dcdcdc', ec='#888', lw=0.4, z=0.6)
    ax.text(15.9, 20.25, 'zjazd 6,0 m', fontsize=6, ha='center', zorder=3)
    # linia zabudowy
    ax.plot([-7.3, 24.7], [BUILD_LINE_Y] * 2, color='#c0392b', lw=1.2, ls=(0, (8, 4)), zorder=6)
    ax.text(-7.0, BUILD_LINE_Y + 0.25, 'nieprzekraczalna linia zabudowy (6,00 m od linii rozgraniczającej 1KDD)',
            fontsize=6.5, color='#c0392b', zorder=6)
    # zieleń izolacyjna (żywopłoty) wzdłuż granic bocznych i tylnej
    for g in [box(-7.3, -31.0, -6.3, 17.5), box(23.7, -31.0, 24.7, 17.5), box(-6.3, -31.0, 23.7, -30.0)]:
        draw_geom(ax, g, fc='#a9cf8f', ec='#6f9a55', lw=0.3, z=0.8)
    for (tx, ty, r) in [(-3.5, -12, 2.4), (3.5, -20, 2.8), (12, -25, 2.6), (20, -19, 2.4), (-3.8, -25.5, 2.2),
                        (21.0, 13.8, 1.6), (-4.5, 14.5, 1.8), (1.5, 15.3, 1.3)]:
        ax.add_patch(Circle((tx, ty), r, fc='#8fbf73', ec='#5d8a44', lw=0.5, alpha=0.6, zorder=0.9))
    # utwardzenia
    for g, lab in [(SITE['driveway'], ''), (SITE['path'], ''), (EXTRA_PAVED['east_path'], ''),
                   (EXTRA_PAVED['south_strip'], ''), (EXTRA_PAVED['west_side'], '')]:
        draw_geom(ax, g, fc='#d9d9d9', ec='#888', lw=0.4, z=1)
    for g in SITE['guest_parking']:
        draw_geom(ax, g, fc='none', ec='#555', lw=0.6, ls=(0, (3, 2)), z=2)
    ax.text(15.9, 13.9, 'P1  P2\nmiejsca gościnne\n2 × 2,50×5,00', fontsize=6, ha='center', va='center', zorder=3)
    draw_geom(ax, SITE['terrace_S'].union(SITE['terrace_W']), fc='#e3d6bf', ec='#8a7a60', lw=0.5, z=1)
    ax.text(5.5, -2.6, f"taras ogrodowy ±0,00 ({fmt(SITE['terrace_S'].union(SITE['terrace_W']).area, 1)} m²)", fontsize=6.5, ha='center', zorder=3)
    # budynek
    draw_geom(ax, OUTLINE['P0'], fc='#9a9a9a', ec='k', lw=1.2, z=4)
    draw_geom(ax, ST1_POLY.difference(OUTLINE['P0']), fc='none', ec='#333', lw=0.5, ls=(0, (4, 2)), z=5)
    outline(ax, OUTLINE['P1'], ec='#7d3c98', lw=0.9, ls=(0, (3, 2)), z=5)
    outline(ax, OUTLINE['P2'], ec='#1f618d', lw=0.9, ls=(0, (1, 1.5)), z=5)
    outline(ax, ST2_POLY, ec='#1f618d', lw=0.5, ls=(0, (6, 3)), z=5)
    draw_geom(ax, box(C_BOX['x0'], C_BOX['y0'], C_BOX['x1'], C_BOX['y1']), fc='none', ec='#7d3c98', lw=0.8, z=5)
    ax.text(5.2, 4.2, 'DOM JEDNORODZINNY\n3 kond. nadz. (P0+P1+P2)\nstropodachy, h = ' + fmt(building_height()[0]) + ' m\n±0,00 = 101,65 m n.p.m.',
            fontsize=7, ha='center', va='center', color='white', fontweight='bold', zorder=6)
    ax.text(15.75, 7.2, 'GARAŻ\n2-stan.', fontsize=7, ha='center', va='center', color='white', fontweight='bold',
            zorder=6)
    ax.text(15.75, 1.8, 'pom. gosp.', fontsize=6, ha='center', va='center', color='white', zorder=6)
    ax.annotate('wejście', xy=(7.8, 10.85), xytext=(4.5, 12.4), fontsize=6.5, zorder=7,
                arrowprops=dict(arrowstyle='->', lw=0.7))
    ax.annotate('brama garażowa', xy=(15.7, 10.85), xytext=(19.5, 12.2), fontsize=6.5, zorder=7,
                arrowprops=dict(arrowstyle='->', lw=0.7))
    # ogrodzenie, brama, furtka
    ax.plot([-7.3, 7.30], [19.0, 19.0], color='k', lw=2.0, zorder=7)
    ax.plot([8.30, 13.30], [19.0, 19.0], color='k', lw=2.0, zorder=7)
    ax.plot([18.30, 24.7], [19.0, 19.0], color='k', lw=2.0, zorder=7)
    ax.plot([13.30, 18.30], [19.0, 19.0], color='k', lw=1.0, ls=(0, (2, 1)), zorder=7)
    ax.plot([18.30, 23.60], [18.8, 18.8], color='#555', lw=0.8, ls=(0, (1, 1)), zorder=7)
    ax.text(21.0, 18.35, 'odjazd bramy', fontsize=5.5, ha='center', va='top')
    ax.text(15.8, 19.2, 'brama przesuwna 5,00 m', fontsize=5.8, ha='center', va='bottom', zorder=8)
    ax.text(7.8, 19.2, 'furtka 1,00', fontsize=5.8, ha='center', va='bottom', zorder=8)
    for seg in [[(-7.3, 19.0), (-7.3, -31.0)], [(-7.3, -31.0), (24.7, -31.0)], [(24.7, -31.0), (24.7, 19.0)]]:
        ax.plot(*zip(*seg), color='#333', lw=1.0, ls=(0, (1, 0)), zorder=7)
    ax.text(0.5, 19.8, 'ogrodzenie od drogi: ażurowe, h = 1,50 m (≤ 1,60), bez prefabrykatów betonowych', fontsize=5.8,
            color='#222', zorder=8)
    ax.text(-8.0, -6.0, 'ogrodzenie panelowe h = 1,50 m', fontsize=5.8, rotation=90, ha='center', va='center')
    # obrys działki
    outline(ax, PLOT, ec='#b03a2e', lw=1.6, ls=(0, (12, 3, 2, 3)), z=8)
    # śmietnik, PC, ZK, retencja
    draw_geom(ax, SITE['bins'], fc='#7f8c8d', ec='k', lw=0.6, z=6)
    ax.text(10.6, 15.25, 'osłona\npojemników', fontsize=5.3, ha='center', va='center', color='white', zorder=7)
    draw_geom(ax, SITE['hp_pad'], fc='#d0d0d0', ec='k', lw=0.4, z=6)
    draw_geom(ax, SITE['hp_unit'], fc='#555', ec='k', lw=0.5, z=6)
    ax.text(21.9, 6.6, 'PC\n(jedn. zewn.)', fontsize=5.8, va='bottom', zorder=7)
    draw_geom(ax, SITE['zk'], fc='#c0392b', ec='k', lw=0.5, z=8)
    ax.text(11.6, 17.6, 'ZK', fontsize=6, color='#c0392b', ha='center', zorder=8)
    draw_geom(ax, SITE['tank'], fc='#aed6f1', ec='#1f618d', lw=0.8, z=6)
    ax.text(15.3, -6.6, 'Zb\n6 m³', fontsize=5.8, ha='center', va='center', zorder=7)
    draw_geom(ax, SITE['infiltr'], fc='#d6eaf8', ec='#1f618d', lw=0.8, hatch='|||', z=6)
    ax.text(16.2, -13.0, 'skrzynki rozsączające ~5 m³', fontsize=5.8, ha='center', va='top', zorder=7)
    draw_geom(ax, SITE['well_san'], fc='#a0522d', ec='k', lw=0.5, z=8)
    # przyłącza
    lines = [
        ('woda PE 40 (z sieci PE 110)', '#1f77b4', [(11.2, 24.0), (11.2, 10.8), (11.2, 7.3)]),
        ('kan. sanit. PVC 160 → sieć PVC 200', '#8c564b', [(9.0, 10.8), (9.0, 17.6), (9.0, 24.4)]),
        ('kabel nN YKY 5×16 (ZK → RG w 0.11)', '#d62728', [(12.4, 19.0), (12.4, 10.8)]),
        ('światłowód', '#ff7f0e', [(11.8, 23.0), (11.8, 10.8)]),
        ('wody opadowe → Zb → rozsączanie', '#17becf', [(12.1, -1.3), (13.5, -5.5), (15.3, -6.6), (16.2, -10.2)]),
    ]
    for lab, col, pts in lines:
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=col, lw=1.2, zorder=6.5, ls=(0, (5, 2)))
    ax.plot([3.40, 3.40, 11.2, 11.2], [7.05, 10.2, 10.2, 6.25], color='#8c564b', lw=0.9, ls=(0, (1, 1.5)), zorder=6.6)
    ax.plot([-2.1, -2.1, 13.5], [-1.1, -5.5, -5.5], color='#17becf', lw=1.0, ls=(0, (5, 2)), zorder=6.5)
    # odległości (WT § 12 — ściany z otworami ≥ 4,0 m; okapy/płyty — przyjęto również ≥ 4,0 m)
    dist_label(ax, (-7.3, 5.8), (-2.50, 5.8), '4,80\n(płyta ST2)', fs=6)
    dist_label(ax, (-7.3, 1.6), (-1.30, 1.6), '6,00 (ściana P2 z oknami)', fs=6)
    dist_label(ax, (-7.3, -2.2), (-1.80, -2.2), '5,50 (płyta ST1)', fs=6)
    dist_label(ax, (-7.3, 9.3), (0.70, 9.3), '8,00 (ściana P0)', fs=6)
    dist_label(ax, (18.90, 8.8), (24.70, 8.8), '5,80 (ściana garażu z otworami)', fs=6)
    dist_label(ax, (21.30, 4.9), (24.70, 4.9), '3,40', fs=6)
    dist_label(ax, (3.0, 10.80), (3.0, 19.0), '8,20', fs=6.5, off=(0.8, -0.3))
    dist_label(ax, (8.9, 12.30), (8.9, 19.0), '6,70 (daszek)', fs=6, off=(1.4, 0.8))
    dist_label(ax, (8.0, -31.0), (8.0, -4.30), '26,70 (taras) / 30,70 (budynek)', fs=6.5, off=(0.0, 0.0), rot=90)
    # wymiary działki
    dim_h(ax, [-7.3, 24.7], -34.3, unit='m', fs=7)
    dim_v(ax, [-31.0, 19.0], -10.3, unit='m', fs=7)
    dim_h(ax, [-7.3, -2.50, -1.30, 0.70, 12.90, 18.90, 24.7], -32.6, unit='m', fs=6)
    # rzędne terenu
    for (x, y) in [(-7.3, -31.0), (24.7, -31.0), (24.7, 19.0), (-7.3, 19.0), (0.70, -0.30), (18.90, -0.30),
                   (18.90, 10.80), (0.70, 10.80)]:
        H = terrain_H(x, y)
        ax.plot(x, y, marker='+', color='#5b4a33', ms=6, zorder=9)
        ax.text(x + 0.25, y + 0.25, f"{H:.2f}".replace('.', ','), fontsize=5.5, color='#5b4a33', zorder=9)
    # tabela wskaźników
    tx, ty = 25.8, 17.5
    rows = [
        ('WSKAŹNIKI (MPZP 3MN)', 'projekt', 'wymóg'),
        ('pow. działki', f"{fmt(m['plot'], 0)} m²", ''),
        ('pow. zabudowy (obrys brył zamkn.)', f"{fmt(m['enclosed'], 1)} m² ({fmt(100 * m['enclosed'] / m['plot'], 1)} %)",
         '≤ 30 %'),
        ('  zachowawczo z płytami/okapami', f"{fmt(m['all_proj'], 1)} m² ({fmt(100 * m['all_proj'] / m['plot'], 1)} %)",
         '≤ 30 %'),
        ('pow. biologicznie czynna', f"{fmt(m['pbc'], 0)} m² ({fmt(100 * m['pbc'] / m['plot'], 1)} %)", '≥ 50 %'),
        ('  + 50 % dachów zielonych', f"+{fmt(0.5 * m['green_roof'], 0)} m² (nie wliczono)", ''),
        ('intensywność zabudowy', f"{fmt(m['intens'], 2)}", '0,05–0,80'),
        ('wysokość budynku', f'{fmt(building_height()[0])} m', '≤ 11,0 m'),
        ('kondygnacje nadziemne', '3', '≤ 3'),
        ('miejsca postojowe', '2 w garażu + 2 goście', '≥ 2'),
        ('dach', 'płaski, spadek 2 %', '≤ 12°'),
    ]
    for i, (a, b, c) in enumerate(rows):
        fw = 'bold' if i == 0 else 'normal'
        ax.text(tx, ty - i * 1.25, a, fontsize=6.3, fontweight=fw, va='top')
        ax.text(tx, ty - i * 1.25 - 0.55, f"   {b}   [{c}]" if c else f"   {b}", fontsize=6.0, va='top', color='#1f4e79')
    # legenda przyłączy
    ly = -2.0
    ax.text(tx, ly, 'PRZYŁĄCZA / SIECI', fontsize=6.5, fontweight='bold', va='top')
    for i, (lab, col, _) in enumerate(lines):
        ax.plot([tx, tx + 1.2], [ly - 1.0 - i * 0.9] * 2, color=col, lw=1.4, ls=(0, (5, 2)))
        ax.text(tx + 1.4, ly - 1.0 - i * 0.9, lab, fontsize=5.6, va='center')
    ax.text(tx, ly - 6.2, 'ZK — złącze kablowo-pomiarowe w linii ogrodzenia\n'
            '● studzienka rewizyjna kan. sanit. Ø425 (1,4 m od granicy)\n'
            'wodomierz w pom. techn. 0.11 (budynek ≤ 15 m od granicy)\n'
            'gaz — sieć w drodze, NIE przyłączany (dom all-electric)', fontsize=5.6, va='top')
    ax.text(-12.3, 31.2, 'ZAGOSPODAROWANIE DZIAŁKI nr 123/4 (obręb 0005 Przykładowo) — WARIANT W1', fontsize=12,
            fontweight='bold', va='top')
    ax.text(-12.3, 30.1, 'układ współrzędnych budynku: x→wsch., y→płn., (0,0) = przecięcie osi A i 1; '
            'narożnik SW działki = (−7,30; −31,00); rzędne terenu [m n.p.m.] PL-EVRF2007-NH', fontsize=6.5, va='top')
    north_arrow(ax, 33.5, 27.0, 1.2)
    scale_bar(ax, 25.8, -31.5, 10)
    fig.savefig(os.path.join(OUT, 'zagospodarowanie.png'), dpi=140, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return m


if __name__ == '__main__':
    m = site_figure()
    for k, v in m.items():
        print(k, round(v, 2))
