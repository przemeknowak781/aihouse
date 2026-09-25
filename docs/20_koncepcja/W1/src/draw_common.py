# -*- coding: utf-8 -*-
"""Wspólne narzędzia rysunkowe (matplotlib) dla wariantu W1."""
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Arc, Circle, FancyArrowPatch, Rectangle
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection, box

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['hatch.linewidth'] = 0.5

C = dict(sil='#9c9c9c', rc='#505050', ins='#f0e4b8', part='#b9b9b9', line='#222222', dim='#1f4e79',
         axis='#b03a2e', glass='#8fb3c9', frame='#3a3d40', wood='#b8895a', conc='#9a9893', render='#f5f4f0',
         dark='#4b4f54', green='#cfe3c0', shadow='#000000')
ROOM_FILL = dict(M='#fbf5e6', P='#e8f1f8', K='#f2f2f2', T='#f5e6e6', S='#ececec', G='#ebebeb')


def fmt(v, nd=2):
    return f"{v:.{nd}f}".replace('.', ',')


def polys(geom):
    if geom.is_empty:
        return []
    if isinstance(geom, Polygon):
        return [geom]
    if isinstance(geom, (MultiPolygon, GeometryCollection)):
        out = []
        for g in geom.geoms:
            out += polys(g)
        return out
    return []


def draw_geom(ax, geom, fc='none', ec='k', lw=0.6, hatch=None, alpha=1.0, z=2, ls='-'):
    for p in polys(geom):
        ax.add_patch(MPoly(list(p.exterior.coords), closed=True, fc=fc, ec=ec, lw=lw, hatch=hatch, alpha=alpha,
                           zorder=z, ls=ls))
        for hole in p.interiors:
            ax.add_patch(MPoly(list(hole.coords), closed=True, fc='white' if fc != 'none' else 'none', ec=ec, lw=lw,
                               zorder=z + 0.01))


def outline(ax, geom, ec='k', lw=0.8, ls='-', z=3, alpha=1.0):
    for p in polys(geom):
        xs, ys = p.exterior.xy
        ax.plot(xs, ys, color=ec, lw=lw, ls=ls, zorder=z, alpha=alpha)


def arc_between(ax, center, r, a, b, **kw):
    """Łuk 90° między kątami a i b (stopnie)."""
    if (b - a) % 360 == 90:
        t1, t2 = a, b
    else:
        t1, t2 = b, a
    ax.add_patch(Arc(center, 2 * r, 2 * r, theta1=t1, theta2=t2, **kw))


def dim_h(ax, xs, y, off_text=0.18, fs=6.5, color=None, ext_to=None, unit='cm', show_total=False):
    """Łańcuch wymiarowy poziomy (wymiary w cm)."""
    color = color or C['dim']
    xs = list(xs)
    ax.plot([xs[0], xs[-1]], [y, y], color=color, lw=0.5, zorder=6)
    for x in xs:
        ax.plot([x - 0.09, x + 0.09], [y - 0.09, y + 0.09], color=color, lw=0.8, zorder=6)
        if ext_to is not None:
            ax.plot([x, x], [y, ext_to], color=color, lw=0.25, zorder=5, alpha=0.6)
    for a, b in zip(xs[:-1], xs[1:]):
        L = b - a
        if L < 0.05:
            continue
        txt = f"{round(L * 100):d}" if unit == 'cm' else fmt(L)
        ax.text((a + b) / 2, y + off_text, txt, ha='center', va='bottom', fontsize=fs, color=color, zorder=7)


def dim_v(ax, ys, x, off_text=0.18, fs=6.5, color=None, ext_to=None, unit='cm'):
    color = color or C['dim']
    ys = list(ys)
    ax.plot([x, x], [ys[0], ys[-1]], color=color, lw=0.5, zorder=6)
    for y in ys:
        ax.plot([x - 0.09, x + 0.09], [y - 0.09, y + 0.09], color=color, lw=0.8, zorder=6)
        if ext_to is not None:
            ax.plot([x, ext_to], [y, y], color=color, lw=0.25, zorder=5, alpha=0.6)
    for a, b in zip(ys[:-1], ys[1:]):
        L = b - a
        if L < 0.05:
            continue
        txt = f"{round(L * 100):d}" if unit == 'cm' else fmt(L)
        ax.text(x - off_text, (a + b) / 2, txt, ha='right', va='center', fontsize=fs, color=color, rotation=90,
                zorder=7)


def axis_bubble(ax, x, y, label, r=0.32, fs=7):
    ax.add_patch(Circle((x, y), r, fc='white', ec=C['axis'], lw=0.8, zorder=8))
    ax.text(x, y, label, ha='center', va='center', fontsize=fs, color=C['axis'], zorder=9, fontweight='bold')


def north_arrow(ax, x, y, s=1.0):
    ax.add_patch(MPoly([(x, y + s), (x - 0.35 * s, y - 0.5 * s), (x, y - 0.25 * s)], closed=True, fc='k', ec='k',
                       zorder=9))
    ax.add_patch(MPoly([(x, y + s), (x + 0.35 * s, y - 0.5 * s), (x, y - 0.25 * s)], closed=True, fc='white', ec='k',
                       zorder=9))
    ax.text(x, y + s + 0.25, 'N', ha='center', va='bottom', fontsize=9, fontweight='bold', zorder=9)


def scale_bar(ax, x, y, L=5.0):
    for i in range(int(L)):
        ax.add_patch(Rectangle((x + i, y), 1, 0.15, fc='k' if i % 2 == 0 else 'white', ec='k', lw=0.5, zorder=9))
    ax.text(x, y - 0.25, '0', fontsize=6, ha='center', va='top')
    ax.text(x + L, y - 0.25, f'{int(L)} m', fontsize=6, ha='center', va='top')


def level_mark(ax, x, z, text, side='right', fs=6.5, color='k'):
    """Znacznik rzędnej (trójkąt + opis)."""
    s = 0.18
    ax.add_patch(MPoly([(x, z), (x - s, z + s * 1.2), (x + s, z + s * 1.2)], closed=True, fc='white', ec=color, lw=0.7,
                       zorder=9))
    ax.plot([x - 0.5, x + 0.5], [z, z], color=color, lw=0.5, zorder=9)
    if side == 'right':
        ax.text(x + 0.35, z + 0.08, text, fontsize=fs, va='bottom', ha='left', color=color, zorder=9)
    else:
        ax.text(x - 0.35, z + 0.08, text, fontsize=fs, va='bottom', ha='right', color=color, zorder=9)
