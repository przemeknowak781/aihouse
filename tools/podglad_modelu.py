#!/usr/bin/env python3
"""Podgląd koncepcji „Dom LAMELA” z modelu — WERYFIKACJA SPÓJNOŚCI (czyta WYŁĄCZNIE model/budynek.yaml + model/dzialka.yaml).

Generuje do docs/20_koncepcja/final/:
  rzut_P0.png, rzut_P1.png, rzut_P2.png — przekrój poziomy IR na +1,10 nad posadzką (ściany z warstwami, stolarka, schody,
      pomieszczenia z numerem/nazwą/pow. netto, osie, płyty nad płaszczyzną cięcia — linia kreskowa);
  elewacje.png (S, N, E, W — rzut prostokątny pryzm IR, malarz), elewacja_S_szkic.png (kontrola wierności szkicowi v2),
  przekroj_AA.png, przekroj_BB.png (cięcie pryzm IR płaszczyzną pionową), dzialka.png (PZT: granice, linia zabudowy, odległości),
  bilans.json + bilans.md (powierzchnie PN-ISO 9836 / W-316, wskaźniki MPZP, wysokości, odległości od granic) oraz wstawia
  tabelę bilansu do docs/20_koncepcja/koncepcja.md między znacznikami <!-- BILANS:START --> … <!-- BILANS:END -->.

Uruchomienie: PYTHONPATH=src python3 tools/podglad_modelu.py [--out docs/20_koncepcja/final] [--bez-koncepcji]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lamela.ir import build_ir  # noqa: E402
from lamela.model import load_model  # noqa: E402
from lamela.views.common import material_color  # noqa: E402

KAT_KOLOR = {"podstawowa": "#fff4d6", "pomocnicza": "#e3f0fa", "ruchu": "#eeeeee", "techniczna": "#f3e3f0"}
CUT_H = 1.10


# ------------------------------------------------------------------------------------------------ rysowanie shapely
def _polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon)]


def fill(ax, g, fc="none", ec="k", lw=0.4, ls="-", alpha=1.0, z=1, hatch=None):
    for p in _polys(g):
        verts, codes = [], []
        for ring in [p.exterior] + list(p.interiors):
            c = list(ring.coords)
            verts += c
            codes += [MPath.MOVETO] + [MPath.LINETO] * (len(c) - 2) + [MPath.CLOSEPOLY]
        ax.add_patch(PathPatch(MPath(verts, codes), fc=fc, ec=ec, lw=lw, ls=ls, alpha=alpha, zorder=z, hatch=hatch))


def outline(ax, g, **kw):
    kw.setdefault("color", "k")
    for p in _polys(g):
        x, y = p.exterior.xy
        ax.plot(x, y, **kw)


def fmt(v, n=2):
    return f"{v:,.{n}f}".replace(",", " ").replace(".", ",")


def kolor(m, mat):
    try:
        return material_color(m, mat)
    except Exception:
        return "#cccccc"


def osie(ax, m, xr, yr, kond=None):
    ox, oy = m.raw["osie"]["x"], m.raw["osie"]["y"]
    for k, x in ox.items():
        if kond != "P2" and k == "A'":
            continue
        ax.plot([x, x], [yr[0], yr[1]], color="#c0392b", lw=0.35, ls=(0, (8, 3, 1, 3)), zorder=0)
        ax.text(x, yr[1] + 0.35, k, ha="center", va="center", fontsize=6.5, color="#c0392b",
                bbox=dict(boxstyle="circle,pad=0.25", fc="w", ec="#c0392b", lw=0.5))
    for k, y in oy.items():
        ax.plot([xr[0], xr[1]], [y, y], color="#c0392b", lw=0.35, ls=(0, (8, 3, 1, 3)), zorder=0)
        ax.text(xr[0] - 0.4, y, k, ha="center", va="center", fontsize=6.5, color="#c0392b",
                bbox=dict(boxstyle="circle,pad=0.25", fc="w", ec="#c0392b", lw=0.5))


# ------------------------------------------------------------------------------------------------ rzuty
def rzut(m, ir, kid, out: Path):
    k = m.kondygnacja(kid)
    zc = k.rzedna + CUT_H
    fig, ax = plt.subplots(figsize=(16.5, 10.5))
    x0, y0, x1, y1 = -3.6, -3.6, 19.6, 11.2
    # elementy poniżej płaszczyzny cięcia (widok z góry): tarasy, schody, posadzki
    for p in ir.prisms:
        if p.level != kid and not (p.kind in ("terrace", "pavement") and kid == "P0"):
            continue
        if p.z1 < zc and p.z1 > k.rzedna - 0.35 and p.kind in ("stair_step", "landing", "terrace", "railing", "furniture"):
            fill(ax, p.shape(), fc="#f7f7f7" if p.kind != "terrace" else "#efe6d8", ec="#777", lw=0.3, z=1)
    # przekrój poziomy
    for p, g in ir.section(zc):
        if p.kind in ("terrain", "vegetation", "context", "vehicle", "road", "pavement", "fence"):
            continue
        if p.meta.get("group") == "otoczenie":
            continue
        kind = p.kind
        if kind == "glass":
            fill(ax, g, fc="#bfe3f5", ec="#2b7bb9", lw=0.4, z=4)
        elif kind in ("frame", "door_leaf"):
            fill(ax, g, fc="#555", ec="#333", lw=0.3, z=4)
        elif kind in ("wall", "insulation", "column", "parapet", "lamella", "railing", "beam"):
            fill(ax, g, fc=kolor(m, p.material), ec="#222", lw=0.35, z=3)
        elif kind == "stair_step":
            fill(ax, g, fc="#e8e0d0", ec="#555", lw=0.3, z=2)
    # pomieszczenia
    for r in m.pomieszczenia(kid):
        if r.polygon is None:
            continue
        fill(ax, r.polygon, fc=KAT_KOLOR.get(r.kategoria, "#fff"), ec="none", alpha=0.55, z=0.5)
        c = r.polygon.representative_point()
        pt = r.raw.get("punkt")
        if pt and r.polygon.buffer(-0.2).contains(Point(pt)):
            c = Point(pt)
        ax.text(c.x, c.y, f"{r.id}\n{r.nazwa}\n{fmt(r.pow_netto)} m²", ha="center", va="center", fontsize=5.6, zorder=6,
                bbox=dict(fc="w", ec="none", alpha=0.7, pad=0.6))
    # płyty nad płaszczyzną cięcia (obrysy kreskowe)
    for sl in m.plyty():
        if k.rzedna + 1.2 < sl["spod"] < k.rzedna + k.wys_kondygnacji + 0.4 and sl["typ"] in ("wspornik", "dach", "strop"):
            outline(ax, sl["poly_full"], color="#666", lw=0.5, ls=(0, (4, 3)), zorder=5)
    osie(ax, m, (x0 + 0.8, x1 - 0.3), (y0 + 0.3, y1 - 0.8), kid)
    ax.set_xlim(x0 - 0.8, x1)
    ax.set_ylim(y0, y1 + 0.3)
    ax.set_aspect("equal")
    ax.set_xticks(range(-3, 20))
    ax.set_yticks(range(-3, 12))
    ax.tick_params(labelsize=6)
    ax.grid(color="#eee", lw=0.3)
    ax.arrow(x1 - 1.0, y1 - 3.0, 0, 1.2, width=0.05, color="k")
    ax.text(x1 - 1.0, y1 - 1.5, "N", ha="center", fontsize=10, weight="bold")
    brut = m.obrys_kondygnacji(kid).area
    pu = sum(r.pow_zaliczona for r in m.pomieszczenia(kid) if r.kategoria in ("podstawowa", "pomocnicza"))
    ax.set_title(f"Dom LAMELA — rzut {k.nazwa} ({kid}), posadzka {k.rzedna:+.3f}; cięcie +{CUT_H:.2f} m — model/budynek.yaml\n"
                 f"pow. brutto kondygnacji {fmt(brut)} m²; PU (podst.+pomocn., PN-ISO 9836) {fmt(pu)} m²; płyty nad cięciem — linia kreskowa",
                 fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
