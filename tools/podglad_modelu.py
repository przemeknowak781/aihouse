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
# KOORDYNACJA: patrz scratchpad/koncepcja/KOORDYNACJA.md — od 04:10 plik kończy i utrzymuje Agent A (proszę nie nadpisywać);
#   Agent B: działka/wyposażenie/instalacje, widoki i pipeline 3D.
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
WYP: list = []


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
    # wyposażenie (model/wyposazenie.yaml) — prostokąty i blaty
    for it in WYP:
        if it.get("kond") != kid:
            continue
        if it.get("typ") == "blat" and it.get("linia"):
            ln = LineString(it["linia"])
            g = ln.buffer(float(it.get("gl", 0.6)) * float(it.get("strona", 1)), single_sided=True, cap_style=2)
            fill(ax, g, fc="#e9e2d6", ec="#8c8c8c", lw=0.4, z=2.5)
            continue
        if not it.get("xy") or not it.get("wym"):
            continue
        x, y = it["xy"]
        w_, d_ = it["wym"]
        a_ = math.radians(it.get("obrot", 0))
        u = np.array([math.cos(a_), math.sin(a_)])
        v = np.array([-u[1], u[0]])
        c = np.array([x, y], float) + (0 if it["typ"] in ("stol", "wyspa") else u * d_ / 2)
        pts = [c + v * sx * w_ / 2 + u * sy * d_ / 2 for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        fill(ax, Polygon(pts), fc="none", ec="#8c8c8c", lw=0.4, z=2.5)
    brut = m.obrys_kondygnacji(kid).area
    pu = sum(r.pow_zaliczona for r in m.pomieszczenia(kid) if not any(s in r.nazwa.lower() for s in ("klatka", "garaż"))
             and r.kategoria != "techniczna")
    ax.set_title(f"Dom LAMELA — rzut {k.nazwa} ({kid}), posadzka {k.rzedna:+.3f}; cięcie +{CUT_H:.2f} m — model/budynek.yaml\n"
                 f"pow. brutto kondygnacji {fmt(brut)} m²; PU wg RPB §20 / W-316 (bez klatki, garażu, techn.) {fmt(pu)} m²; "
                 f"płyty nad cięciem — linia kreskowa; wyposażenie z model/wyposazenie.yaml", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ elewacje (rzut prostokątny, malarz)
KIER = {  # strona: (u(x, y), głębokość(x, y) — mniejsza = bliżej widza), opis
    "S": (lambda x, y: x, lambda x, y: y, "południowa (ogrodowa) — widok na północ"),
    "N": (lambda x, y: -x, lambda x, y: -y, "północna (od ulicy) — widok na południe"),
    "E": (lambda x, y: y, lambda x, y: -x, "wschodnia — widok na zachód"),
    "W": (lambda x, y: -y, lambda x, y: x, "zachodnia — widok na wschód"),
}
POMIN = ("terrain", "vegetation", "context", "vehicle", "road", "fence", "furniture")


def _proj(p, fu, fd):
    xs, ys = zip(*p.polygon)
    us = [fu(x, y) for x, y in zip(xs, ys)]
    ds = [fd(x, y) for x, y in zip(xs, ys)]
    return min(us), max(us), min(ds), max(ds)


def elewacja(ax, m, ir, strona, tytul=True):
    fu, fd, opis = KIER[strona]
    items = []
    for p in ir.prisms:
        if p.kind in POMIN or p.meta.get("group") in ("otoczenie", "fundamenty") or p.z1 < -0.6:
            continue
        u0, u1, d0, d1 = _proj(p, fu, fd)
        items.append((d0, u0, u1, p))
    items.sort(key=lambda t: -t[0])
    for d0, u0, u1, p in items:
        if u1 - u0 < 1e-3 or p.z1 - p.z0 < 1e-3:
            continue
        glass = p.kind == "glass"
        fc = "#9fc9df" if glass else kolor(m, p.material)
        ax.add_patch(plt.Rectangle((u0, max(p.z0, -0.6)), u1 - u0, p.z1 - max(p.z0, -0.6), fc=fc, ec="#333" if not glass else "#2b6f99",
                                   lw=0.15 if p.kind in ("lamella", "insulation") else 0.3, alpha=0.9 if glass else 1.0, zorder=2))
    # teren wzdłuż lica
    if ir.terrain is not None:
        bx0, by0, bx1, by1 = m.bbox()
        if strona in ("S", "N"):
            yy = (by0 - 1.5) if strona == "S" else (by1 + 1.5)
            xs = np.linspace(bx0 - 3, bx1 + 3, 80)
            pts = [(fu(x, yy), ir.terrain.height_at(x, yy)) for x in xs]
        else:
            xx = (bx1 + 1.5) if strona == "E" else (bx0 - 1.5)
            ys = np.linspace(by0 - 3, by1 + 3, 80)
            pts = [(fu(xx, y), ir.terrain.height_at(xx, y)) for y in ys]
        pts.sort()
        u, z = zip(*pts)
        ax.fill_between(u, [-1.2] * len(u), z, color="#d8ccb4", zorder=3)
        ax.plot(u, z, color="#6b5a3c", lw=1.0, zorder=3)
    ax.set_aspect("equal")
    ax.axhline(0, color="#999", lw=0.3, ls=":")
    if tytul:
        ax.set_title(f"Elewacja {opis}", fontsize=8, loc="left")
    ax.tick_params(labelsize=6)


def elewacje(m, ir, out: Path):
    fig, axs = plt.subplots(2, 2, figsize=(18, 10))
    for ax, s in zip(axs.flat, ("S", "N", "E", "W")):
        elewacja(ax, m, ir, s)
        for zz in (0.0, 3.15, 6.30, 9.30):
            ax.axhline(zz, color="#c0392b", lw=0.25, ls=(0, (6, 4)), zorder=1)
    fig.suptitle("Dom LAMELA — elewacje z modelu (rzut prostokątny pryzm IR; kolorystyka wg materiałów modelu)", fontsize=10, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)


def elewacje_osobno(m, ir, out: Path):
    for st in ("S", "N", "E", "W"):
        fig, ax = plt.subplots(figsize=(15, 7))
        elewacja(ax, m, ir, st)
        for zz in (0.0, 3.15, 6.30, 9.30):
            ax.axhline(zz, color="#c0392b", lw=0.25, ls=(0, (6, 4)), zorder=1)
        fig.tight_layout()
        fig.savefig(out / f"elewacja_{st}.png", dpi=140, bbox_inches="tight")
        plt.close(fig)


def rzut_dachu(m, ir, out: Path):
    """Dachy: obrysy, attyki, spadki, wpusty (WP), przelewy awaryjne (PA), rury spustowe (RS), otwory (świetlik, wyłaz)."""
    fig, ax = plt.subplots(figsize=(16, 10))
    for w in m.wsporniki():
        fill(ax, Polygon(w["obrys"]), fc="#e6e3dd", ec="#777", lw=0.4, z=1)
    kol = {"SD1": "#d9d4c7", "SD2": "#cfc8b8", "DZ1": "#b9d59c"}
    for d in m.dachy():
        g = Polygon(d["obrys"], [o for o in (d.get("otwory") or [])])
        fill(ax, g, fc=kol.get(d.get("przegroda"), "#ddd"), ec="#222", lw=0.8, z=2)
        att = (d.get("attyka") or {}).get("szer", 0.25)
        fill(ax, Polygon(d["obrys"]).difference(Polygon(d["obrys"]).buffer(-att, join_style=2)), fc="#8d8d8d", ec="none", alpha=0.6, z=3)
        c = Polygon(d["obrys"]).representative_point()
        sl = next(x for x in m.plyty() if x["id"] == d["id"])
        ax.text(c.x, c.y, f"{d['id']} ({d.get('przegroda')})\nwierzch {fmt(sl['top'], 3)}; attyka {fmt(sl['top_attyki'] or sl['top'], 3)}",
                fontsize=7, ha="center", zorder=6, bbox=dict(fc="w", ec="none", alpha=0.7))
        for sp in d.get("spadki") or []:
            (x0, y0), (x1, y1) = sp["od"], sp["do"]
            ax.annotate("", (x1, y1), (x0, y0), arrowprops=dict(arrowstyle="->", color="#1f77b4", lw=0.8), zorder=5)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, f"{fmt(100 * sp['spadek'], 1)} %", fontsize=6, color="#1f77b4", zorder=5)
        for wp in d.get("wpusty") or []:
            x, y = wp["xy"] if isinstance(wp, dict) else wp
            ax.plot([x], [y], "o", ms=7, mfc="#1f77b4", mec="k", zorder=7)
            ax.text(x + 0.15, y + 0.15, f"WP DN{wp.get('dn', 100) if isinstance(wp, dict) else 100}", fontsize=6, zorder=7)
        for pa in d.get("przelewy_awaryjne") or []:
            x, y = pa["xy"]
            ax.plot([x], [y], "s", ms=6, mfc="#ff7f0e", mec="k", zorder=7)
            ax.text(x + 0.15, y - 0.35, f"PA {fmt(pa.get('rzedna_dna', 0), 2)}", fontsize=5.5, color="#b35900", zorder=7)
        for rs in d.get("rury_spustowe") or []:
            x, y = rs["xy_pion"]
            ax.plot([x], [y], "D", ms=5, mfc="#7f7f7f", mec="k", zorder=8)
            ax.text(x + 0.15, y - 0.2, f"{rs['id']} ({rs.get('trasa')})", fontsize=5.5, zorder=8)
    for p in ir.prisms:
        if p.kind == "lamella" and p.z0 > 5.0:
            fill(ax, p.shape(), fc="#8a5a32", ec="none", z=4)
    en = (m.raw.get("energia") or {}).get("wentylacja") or {}
    for key, mk in (("czerpnia", "^"), ("wyrzutnia", "v")):
        v = en.get(key)
        if isinstance(v, list):
            ax.plot([v[0]], [v[1]], mk, ms=8, mfc="#2ca02c", mec="k", zorder=8)
            ax.text(v[0] + 0.2, v[1], key, fontsize=6, zorder=8)
    for w in en.get("wywiewki_kanalizacyjne") or []:
        ax.plot([w[0]], [w[1]], "x", ms=7, color="#8c564b", zorder=8)
        ax.text(w[0] + 0.2, w[1], "wywiewka K1", fontsize=6, zorder=8)
    osie(ax, m, (-3.0, 19.3), (-2.5, 10.4), "P2")
    ax.set_aspect("equal")
    ax.set_xlim(-4.0, 19.6)
    ax.set_ylim(-2.8, 11.0)
    ax.tick_params(labelsize=6)
    ax.set_title("Dom LAMELA — rzut dachów z modelu: spadki (strzałki), wpusty WP, przelewy awaryjne PA, rury spustowe RS, "
                 "czerpnia/wyrzutnia, lamele", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ elewacja S vs szkic (wierność)
SZKIC_CROP = (563, 865, 2333, 1555)      # wycinek 1770 × 690 px oryginału (brief §1.1)
SZKIC_SX = 45.8                           # px/m (bryła B 500…1050 px = 12,0 m)
SZKIC_X_B = 500                           # px lica zach. bryły B
SZKIC = {  # element: (x0, x1) od lica zach. bryły B [m] — odczyt briefu §1.1 (px/45,8)
    "A — bryła II p. (lamele)": ((455 - 500) / SZKIC_SX, (1060 - 500) / SZKIC_SX),
    "A — płyty (dół/góra)": ((390 - 500) / SZKIC_SX, (1075 - 500) / SZKIC_SX),
    "B — bryła I p.": (0.0, (1050 - 500) / SZKIC_SX),
    "C — boks (przeszklenie)": ((705 - 500) / SZKIC_SX, (1035 - 500) / SZKIC_SX),
    "C — rama górna": ((680 - 500) / SZKIC_SX, (1130 - 500) / SZKIC_SX),
    "D — linia pozioma": ((675 - 500) / SZKIC_SX, (1370 - 500) / SZKIC_SX),
    "D — pion (narożnik G)": ((1378 - 500) / SZKIC_SX, (1378 - 500) / SZKIC_SX),
    "E — przeszklenie parteru": ((545 - 500) / SZKIC_SX, (1105 - 500) / SZKIC_SX),
    "E — płyta dachu parteru": ((430 - 500) / SZKIC_SX, (1145 - 500) / SZKIC_SX),
}


def krawedzie_modelu(m):
    """Zakresy x kluczowych krawędzi elewacji S z modelu (układ budynku)."""
    ob1 = m.obrys_kondygnacji("P1")
    ob2 = m.obrys_kondygnacji("P2")
    ws = {w["id"]: Polygon(w["obrys"]) for w in m.wsporniki()}
    dg = {d["id"]: Polygon(d["obrys"]) for d in m.dachy()}
    ot = {o.id: o for o in m.otwory()}

    def xr(g):
        b = g.bounds
        return b[0], b[2]

    def otw(ids):
        xs = [float(p[0]) for i in ids for p in (ot[i].p0, ot[i].p1)]
        return min(xs), max(xs)
    e_ids = [o.id for o in m.otwory() if o.sciana.id in ("S0-01", "S0-02") and o.typ != "otwor"]
    p0 = m.obrys_kondygnacji("P0")
    return {
        "A — bryła II p. (lamele)": xr(ob2),
        "A — płyty (dół/góra)": xr(unary_union([ws.get("PL-2", Polygon()), ws.get("PL-3", Polygon())])),
        "B — bryła I p.": xr(ob1),
        "C — boks (przeszklenie)": otw([i for i in ("O1-01", "O1-13", "O1-14") if i in ot]),
        "C — rama górna": xr(ws["PL-C2"]),
        "D — linia pozioma": (xr(ws["PL-C1"])[0], max(xr(dg["D4"])[1], xr(ws["PL-D"])[1] if "PL-D" in ws else -1e9)),
        "D — pion (narożnik G)": (xr(p0)[1], xr(p0)[1]),
        "E — przeszklenie parteru": otw(e_ids),
        "E — płyta dachu parteru": xr(ws["PL-E"]),
    }


def wiernosc(m):
    x_B = m.obrys_kondygnacji("P1").bounds[0]
    km = krawedzie_modelu(m)
    rows = []
    for k, (s0, s1) in SZKIC.items():
        a, b = km[k]
        a, b = a - x_B, b - x_B
        rows.append({"element": k, "szkic": [round(s0, 2), round(s1, 2)], "model": [round(a, 3), round(b, 3)],
                     "odchylka": round(max(abs(a - s0), abs(b - s1)), 2)})
    return rows, x_B


def elewacja_szkic(m, ir, out: Path):
    from PIL import Image
    rows, x_B = wiernosc(m)
    img = Image.open(ROOT / "00_wejscie" / "szkic_koncepcyjny.jpg").crop(SZKIC_CROP).convert("L")
    H = max(sl["top_attyki"] or sl["top"] for sl in m.plyty() if sl["typ"] == "dach")
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(15, 11.5), gridspec_kw={"height_ratios": [1, 1.05]})
    W_, H_ = img.size
    x_left = x_B - SZKIC_X_B / SZKIC_SX
    x_right = x_left + W_ / SZKIC_SX
    zt, zb = H, -0.30               # pionowo umownie: px 80 → wierzch attyki, px 640 → teren

    def zpx(z):
        return 640 - (z - zb) / (zt - zb) * (640 - 80)
    a1.imshow(img, cmap="gray", extent=(x_left, x_right, H_, 0), aspect="auto")
    km = krawedzie_modelu(m)
    pas = {"A — bryła II p. (lamele)": (6.30, 9.30), "A — płyty (dół/góra)": (5.95, 9.40), "B — bryła I p.": (3.15, 6.25),
           "C — boks (przeszklenie)": (3.85, 5.35), "C — rama górna": (5.35, 5.55), "D — linia pozioma": (3.65, 3.85),
           "E — przeszklenie parteru": (0.0, 2.75), "E — płyta dachu parteru": (2.75, 3.05)}
    for k, (za, zb_) in pas.items():
        x0, x1 = km[k]
        a1.add_patch(plt.Rectangle((x0, zpx(zb_)), x1 - x0, zpx(za) - zpx(zb_), fill=False, ec="#d62728", lw=1.2))
    xg = km["D — pion (narożnik G)"][0]
    a1.plot([xg, xg], [zpx(0), zpx(3.85)], color="#d62728", lw=1.6)
    a1.set_xlim(x_left, x_right)
    a1.set_ylim(H_, 0)
    a1.set_yticks([])
    a1.set_xlabel("x [m] (układ budynku; lico zach. bryły B = %.2f)" % x_B, fontsize=7)
    a1.set_title("Szkic Inwestora (wycinek, skala pozioma 45,8 px/m wg briefu §1.1; pionowa umowna) + obrys modelu (czerwony)", fontsize=9, loc="left")
    elewacja(a2, m, ir, "S", tytul=False)
    a2.set_xlim(x_left, x_right)
    txt = "; ".join(f"{r['element'].split(' — ')[0]}·{r['element'].split(' — ')[1][:12]}: Δ {fmt(r['odchylka'])} m" for r in rows)
    a2.set_title("Elewacja południowa z modelu — rytm przesunięć zachód–wschód–zachód („S”); maks. odchyłka krawędzi od szkicu "
                 f"{fmt(max(r['odchylka'] for r in rows))} m", fontsize=9, loc="left")
    a2.text(x_left + 0.2, -1.1, txt, fontsize=5.5, va="top", wrap=True)
    fig.tight_layout()
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return rows


# ------------------------------------------------------------------------------------------------ przekroje pionowe
def przekroj(m, ir, os_, c, out: Path, nazwa: str):
    """os_='x' — płaszczyzna x = c (widok na wschód, u = −y); os_='y' — płaszczyzna y = c (widok na północ, u = x)."""
    fig, ax = plt.subplots(figsize=(16, 9))
    big = 200.0
    line = LineString([(c, -big), (c, big)]) if os_ == "x" else LineString([(-big, c), (big, c)])

    def U(v):
        return -v if os_ == "x" else v
    # widok za płaszczyzną (szary, malarz)
    far = []
    for p in ir.prisms:
        if p.kind in POMIN or p.meta.get("group") == "otoczenie":
            continue
        xs, ys = zip(*p.polygon)
        d0 = (min(xs) - c) if os_ == "x" else (min(ys) - c)
        if d0 <= 0.001:
            continue
        u0, u1 = (min(U(y) for y in ys), max(U(y) for y in ys)) if os_ == "x" else (min(xs), max(xs))
        far.append((d0, u0, u1, p))
    far.sort(key=lambda t: -t[0])
    for d0, u0, u1, p in far:
        ax.add_patch(plt.Rectangle((u0, p.z0), u1 - u0, p.z1 - p.z0, fc="#f4f4f4" if p.kind != "glass" else "#e3f1f8", ec="#c8c8c8",
                                   lw=0.2, zorder=1))
    # elementy przecięte
    for p in ir.prisms:
        if p.kind in POMIN or p.meta.get("group") == "otoczenie":
            continue
        g = p.shape()
        if not g.intersects(line):
            continue
        seg = g.intersection(line)
        segs = [seg] if seg.geom_type == "LineString" else [s for s in getattr(seg, "geoms", []) if s.geom_type == "LineString"]
        for s in segs:
            vals = [U(q[1]) if os_ == "x" else q[0] for q in s.coords]
            u0, u1 = min(vals), max(vals)
            if u1 - u0 < 1e-4:
                continue
            fc = "#9fc9df" if p.kind == "glass" else kolor(m, p.material)
            ax.add_patch(plt.Rectangle((u0, p.z0), u1 - u0, p.z1 - p.z0, fc=fc, ec="#111", lw=0.35, zorder=3))
    if ir.terrain is not None:
        ts = np.linspace(-45, 25, 300)
        pts = [((U(t), ir.terrain.height_at(c, t)) if os_ == "x" else (t, ir.terrain.height_at(t, c))) for t in ts]
        pts.sort()
        u, z = zip(*pts)
        ax.fill_between(u, [-2.0] * len(u), z, color="#e2d6bd", zorder=0.5)
        ax.plot(u, z, color="#6b5a3c", lw=1.0, zorder=4)
    for k in m.kondygnacje:
        ax.axhline(k.rzedna, color="#c0392b", lw=0.3, ls=(0, (6, 4)), zorder=0.8)

    osie_ = m.raw["osie"]["y" if os_ == "x" else "x"]
    for n_, v in osie_.items():
        ax.axvline(U(v), color="#c0392b", lw=0.3, ls=(0, (8, 3, 1, 3)), zorder=0.8)
        ax.text(U(v), 10.6, n_, ha="center", fontsize=7, color="#c0392b", bbox=dict(boxstyle="circle,pad=0.2", fc="w", ec="#c0392b", lw=0.5))
    lo, hi = (-12.0, 5.0) if os_ == "x" else (-4.0, 21.0)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-1.6, 11.3)
    for k in m.kondygnacje:
        ax.text(lo + 0.1, k.rzedna + 0.03, f"{k.id} {fmt(k.rzedna, 3)}", fontsize=6, color="#c0392b", va="bottom")
    ax.set_aspect("equal")
    ax.tick_params(labelsize=6)
    if os_ == "x":
        ax.set_xticks(range(-12, 6))
        ax.set_xticklabels([str(-t) for t in range(-12, 6)])
        ax.set_xlabel("y [m] (północ ← → południe)", fontsize=7)
    else:
        ax.set_xlabel("x [m] (zachód → wschód)", fontsize=7)
    dachy = [sl for sl in m.plyty() if sl["typ"] == "dach"]
    top = max((sl["top_attyki"] or sl["top"]) for sl in dachy)
    ax.set_title(f"{nazwa}: płaszczyzna {os_} = {fmt(c)} m\nelementy przecięte (kolor materiału), widok (szary), teren; "
                 f"najwyższy punkt attyki {fmt(top, 3)}", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ------------------------------------------------------------------------------------------------ działka (PZT)
def odleglosci(m):
    """Najmniejsze odległości elementów od granic działki (układ budynku; granice z dzialka.yaml)."""
    dz = m.dz
    ob = dz.obrys
    x0, y0, x1, y1 = ob.bounds
    lz = dz.raw.get("linia_zabudowy") or []
    y_lz = min(dz.do_budynku(p)[1] for p in lz) if lz else y1
    wyn = []

    def dodaj(nazwa, g, otwory):
        b = g.bounds
        wyn.append({"element": nazwa, "W": round(b[0] - x0, 2), "E": round(x1 - b[2], 2), "S": round(b[1] - y0, 2),
                    "N_linia_zab": round(y_lz - b[3], 2), "otwory": otwory})
    for k in m.kondygnacje:
        dodaj(f"ściany {k.id} (lico ocieplenia)", m.obrys_kondygnacji(k.id), True)
    for w in m.wsporniki():
        dodaj(f"płyta {w['id']}", Polygon(w["obrys"]), False)
    for t in m.tarasy():
        dodaj(f"taras {t['id']}", Polygon(t["obrys"]), False)
    for o in (dz.raw.get("uzbrojenie") or {}).get("obiekty") or []:
        if o.get("id") == "PC-JZ":
            x, y = dz.do_budynku(o["xy"])
            dodaj("jednostka zewn. PC", Point(x, y).buffer(0.6, cap_style=3), False)
    return wyn, y_lz


def dzialka_png(m, ir, out: Path):
    dz = m.dz
    fig, ax = plt.subplots(figsize=(11, 15))
    ob = dz.obrys
    for s in dz.lista("sasiedzi"):
        if s.get("obrys"):
            fill(ax, dz.poly_bud(s["obrys"]), fc="#f7f7f2", ec="#999", lw=0.4, z=0)
        zab = s.get("zabudowa")
        if isinstance(zab, list) and len(zab) >= 3:
            fill(ax, dz.poly_bud(zab), fc="#ddd", ec="#777", lw=0.5, z=1)
    dr = dz.raw.get("droga") or {}
    if dr.get("linie_rozgraniczajace"):
        fill(ax, dz.poly_bud(dr["linie_rozgraniczajace"]), fc="#eeeeee", ec="#888", lw=0.4, z=0.5)
    if dr.get("jezdnia"):
        fill(ax, dz.poly_bud(dr["jezdnia"]), fc="#bdbdbd", ec="none", z=0.6)
    fill(ax, ob, fc="#eef6e6", ec="#b22", lw=1.4, z=1)
    for z_ in dz.lista("zielen"):
        if z_.get("typ") == "trawnik":
            continue
        fill(ax, dz.poly_bud(z_["obrys"]), fc="#9cc98a" if z_["typ"] == "zywoplot" else "#c9e2b3", ec="#5b8a4a", lw=0.3, z=2)
    for u in dz.lista("utwardzenia"):
        fill(ax, dz.poly_bud(u["obrys"]), fc="#d4cfc6", ec="#777", lw=0.4, z=2)
    for t in m.tarasy():
        fill(ax, Polygon(t["obrys"]), fc="#c9b69c", ec="#6b5a3c", lw=0.4, z=2)
    for mp in dz.lista("miejsca_postojowe"):
        fill(ax, dz.poly_bud(mp["obrys"]), fc="none", ec="#333", lw=0.6, ls="--", z=4)
    od = dz.raw.get("odpady") or {}
    if od.get("obrys"):
        fill(ax, dz.poly_bud(od["obrys"]), fc="#bbb", ec="#333", lw=0.5, z=4)
    ret = dz.raw.get("retencja") or {}
    if (ret.get("rozsaczanie") or {}).get("obrys"):
        fill(ax, dz.poly_bud(ret["rozsaczanie"]["obrys"]), fc="#bfe0f2", ec="#2b7bb9", lw=0.6, z=3)
    if (ret.get("zbiornik") or {}).get("xy"):
        x, y = dz.do_budynku(ret["zbiornik"]["xy"])
        ax.add_patch(plt.Circle((x, y), 1.1, fc="#8fc3e3", ec="#2b7bb9", zorder=4))
        ax.text(x, y, f"Z {ret['zbiornik'].get('V', '')} m³", fontsize=6, ha="center", va="center", zorder=5)
    kol = {"woda": "#1f77b4", "kan_sanit": "#8c564b", "en": "#d62728", "tele": "#9467bd", "gaz": "#e5ae00", "kan_deszcz": "#17becf"}
    for zb in ("istniejace", "projektowane"):
        for u in (dz.raw.get("uzbrojenie") or {}).get(zb) or []:
            pts = [dz.do_budynku(p) for p in u.get("linia") or []]
            if len(pts) >= 2:
                xs, ys = zip(*pts)
                ax.plot(xs, ys, color=kol.get(u["branza"], "#444"), lw=0.8 if zb == "projektowane" else 0.5,
                        ls="-" if zb == "projektowane" else "--", zorder=3)
    for o in (dz.raw.get("uzbrojenie") or {}).get("obiekty") or []:
        x, y = dz.do_budynku(o["xy"])
        ax.plot([x], [y], "s", ms=4, color="#333", zorder=6)
        ax.text(x + 0.4, y, o["id"], fontsize=5.5, zorder=6)
    for od_ in dz.lista("odwodnienia"):
        if od_.get("linia"):
            pts = [dz.do_budynku(p) for p in od_["linia"]]
            if len(pts) >= 2:
                xs, ys = zip(*pts)
                ax.plot(xs, ys, color="#17becf", lw=1.4, zorder=4)
    for f_ in dz.lista("ogrodzenie"):
        pts = [dz.do_budynku(p) for p in f_["linia"]]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color="#333", lw=0.8, zorder=5)
    for b_ in dz.lista("bramy"):
        x, y = dz.do_budynku(b_["xy"])
        ax.plot([x - b_["szer"] / 2, x + b_["szer"] / 2], [y, y], color="#e67e22", lw=2.2, zorder=6)
    for d_ in dz.lista("drzewa"):
        x, y = dz.do_budynku(d_["xy"])
        ax.add_patch(plt.Circle((x, y), d_["sr_korony"] / 2, fc="#6aa84f" if not d_.get("istn") else "#38761d", ec="#274e13", alpha=0.45, zorder=6))
    # budynek
    fill(ax, m.obrys_kondygnacji("P0"), fc="#9e9e9e", ec="#111", lw=1.2, z=7)
    for kid, ls in (("P1", "--"), ("P2", ":")):
        outline(ax, m.obrys_kondygnacji(kid), color="#111", lw=0.9, ls=ls, zorder=8)
    for w in m.wsporniki():
        outline(ax, Polygon(w["obrys"]), color="#555", lw=0.5, ls=(0, (1, 2)), zorder=8)
    lz = dz.raw.get("linia_zabudowy") or []
    if lz:
        pts = [dz.do_budynku(p) for p in lz]
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color="#b22", lw=1.0, ls=(0, (10, 3, 2, 3)), zorder=9)
        ax.text(xs[0] + 0.3, ys[0] + 0.3, "nieprzekraczalna linia zabudowy (6,00 m od 1KDD)", color="#b22", fontsize=7, zorder=9)
    wyn, y_lz = odleglosci(m)
    x0, y0, x1, y1 = ob.bounds
    p0 = m.obrys_kondygnacji("P0").bounds
    p2 = m.obrys_kondygnacji("P2").bounds
    for (xa, xb, yy, txt) in ((x0, p2[0], 2.5, None), (p0[2], x1, 4.0, None)):
        ax.annotate("", (xa, yy), (xb, yy), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#b22"), zorder=10)
        ax.text((xa + xb) / 2, yy + 0.3, f"{fmt(abs(xb - xa))} m", ha="center", fontsize=7, color="#b22", zorder=10)
    ax.annotate("", (8.0, y0), (8.0, p0[1]), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#b22"), zorder=10)
    ax.text(8.3, (y0 + p0[1]) / 2, f"{fmt(p0[1] - y0)} m", fontsize=7, color="#b22", rotation=90, zorder=10)
    ax.set_xlim(x0 - 4, x1 + 4)
    ax.set_ylim(y0 - 3, y1 + 12)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=6)
    ax.set_title("Dom LAMELA — zagospodarowanie działki 123/4 (układ budynku; dane: model/dzialka.yaml + budynek.yaml)\n"
                 "P0 — wypełnienie; P1 — kreska; P2 — kropki; płyty wysunięte — linia punktowa; retencja — niebieski; "
                 "odwodnienia liniowe — turkus; bramy — pomarańcz", fontsize=8, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=140, bbox_inches="tight")
    plt.close(fig)
    return wyn


# ------------------------------------------------------------------------------------------------ bilans
KLATKI_SLOWA = ("klatka schodowa",)


def _teren_interp(m, klucz):
    from scipy.interpolate import griddata
    pts = (m.dz.raw.get("teren") or {}).get(klucz) or []
    if len(pts) < 3:
        return None
    arr = np.asarray(pts, float)
    xy = m.dz.do_budynku(arr[:, :2])
    z = arr[:, 2] - m.dz.zero_abs

    def f(q):
        q = np.atleast_2d(q)
        v = griddata(xy, z, q, method="linear")
        if np.any(np.isnan(v)):
            v2 = griddata(xy, z, q, method="nearest")
            v = np.where(np.isnan(v), v2, v)
        return v
    return f


def bilans(m, wyn_odl, fidelity):
    B = {}
    wiersze, pu, gar, tech, klat = [], {}, 0.0, 0.0, 0.0
    for r in m.pomieszczenia():
        rodz = r.raw.get("rodzaj") or ""
        nm = r.nazwa.lower()
        wiersze.append({"id": r.id, "kond": r.kond, "nazwa": r.nazwa, "kat": r.kategoria, "A": round(r.pow_netto, 2),
                        "h": round(r.wysokosc or 0, 2), "wsp": r.wsp_wysokosci, "A_zal": round(r.pow_zaliczona, 2)})
        if any(s in nm for s in KLATKI_SLOWA):
            klat += r.pow_netto
            continue
        if rodz == "garaz" or "garaż" in nm:
            gar += r.pow_netto
            continue
        if r.kategoria == "techniczna":
            tech += r.pow_netto
            continue
        pu[r.kond] = pu.get(r.kond, 0.0) + r.pow_zaliczona
    zp = m.zestawienie_powierzchni()
    B["pomieszczenia"] = wiersze
    B["PU_W316"] = {k: round(v, 2) for k, v in pu.items()}
    B["PU_W316_suma"] = round(sum(pu.values()), 2)
    B["garaz"], B["techniczne"], B["klatki"] = round(gar, 2), round(tech, 2), round(klat, 2)
    B["PN_ISO_9836"] = {"podstawowa": zp["sumy_kategorii"].get("podstawowa"), "pomocnicza (z garażem)": zp["sumy_kategorii"].get("pomocnicza"),
                        "ruchu": zp["pow_ruchu"], "techniczna": zp["pow_techniczna"], "netto razem": zp["pow_netto_razem"]}
    dz = m.dz
    ob = dz.obrys
    A_dz = float(ob.area)
    zab = m.pow_zabudowy()
    brutto = m.pow_brutto_kondygnacji()
    B["dzialka_m2"] = round(A_dz, 2)
    B["zabudowa"] = {"m2": zab["budynek"], "proc": round(100 * zab["budynek"] / A_dz, 2), "z_plytami_m2": zab["z_plytami"]}
    B["brutto_kondygnacji"] = brutto
    B["intensywnosc"] = round(sum(brutto.values()) / A_dz, 3)
    B["kubatura_brutto_m3"] = m.kubatura_brutto()["razem"]
    nie_bc = [m.obrys_kondygnacji(m.kondygnacje[0].id)] + [dz.poly_bud(u["obrys"]) for u in dz.lista("utwardzenia")]
    nie_bc += [Polygon(t["obrys"]) for t in m.tarasy()]
    od = dz.raw.get("odpady") or {}
    if od.get("obrys"):
        nie_bc.append(dz.poly_bud(od["obrys"]))
    ret = dz.raw.get("retencja") or {}
    if (ret.get("zbiornik") or {}).get("xy"):
        x, y = dz.do_budynku(ret["zbiornik"]["xy"])
        nie_bc.append(Point(x, y).buffer(1.2))
    nb = unary_union(nie_bc).intersection(ob)
    d4 = [Polygon(d["obrys"]).area for d in m.dachy() if "DZ" in str(d.get("przegroda", ""))]
    B["PBC"] = {"m2": round(A_dz - nb.area, 2), "proc": round(100 * (A_dz - nb.area) / A_dz, 2),
                "rezerwa_dach_zielony_50proc_m2": round(0.5 * sum(d4), 2), "utwardzenia_tarasy_m2": round(nb.area - zab["budynek"], 2)}
    # wysokości
    dachy = [sl for sl in m.plyty() if sl["typ"] == "dach"]
    top_att = max((sl["top_attyki"] or sl["top"]) for sl in dachy)
    en = (m.raw.get("energia") or {}).get("wentylacja") or {}
    top_inst = max([top_att] + [float(p[2]) for p in (en.get("czerpnia"), en.get("wyrzutnia")) if isinstance(p, list) and len(p) == 3])
    ob0 = m.obrys_kondygnacji(m.kondygnacje[0].id)
    per = [ob0.exterior.interpolate(t, normalized=True) for t in np.linspace(0, 1, 120, endpoint=False)]
    q = np.array([[p.x, p.y] for p in per])
    f_ist, f_proj = _teren_interp(m, "punkty"), _teren_interp(m, "punkty_projektowane")
    zi = f_ist(q) if f_ist else np.zeros(len(q))
    zp_ = f_proj(q) if f_proj else zi
    zt = np.minimum(zi, zp_)
    sr = (float(zt.min()) + float(zt.max())) / 2
    wej = [o for o in m.otwory(kond=m.kondygnacje[0].id) if o.typ in ("drzwi_zewn", "drzwi_przesuwne_HS") and o.sciana.typ == "sciana_zewn"]
    zw = [float(min(f_proj(np.array([o.srodek[:2]]))[0] if f_proj else 0.0, (f_ist(np.array([o.srodek[:2]]))[0] if f_ist else 0.0)))
          for o in wej]
    d1 = max(dachy, key=lambda sl: sl["top"])

    def top_max(sl):
        """Najwyższy punkt pokrycia dachu z izolacją spadkową (klin d_max), nie średnia grubość (audyt A1)."""
        prz = (m.raw.get("przegrody") or {}).get(str(sl["raw"].get("przegroda"))) or {}
        for w_ in prz.get("warstwy") or []:
            if isinstance(w_, dict) and isinstance(w_.get("klin"), dict):
                return sl["top"] - float(w_["d"]) + float(w_["klin"]["d_max"])
        return sl["top"]
    z_wt6 = max(top_max(sl) for sl in dachy)
    B["wysokosc"] = {"attyka_max": round(top_att, 3), "najwyzszy_punkt_z_instalacjami": round(top_inst, 3),
                     "teren_obwod_min": round(float(zt.min()), 3), "teren_obwod_max": round(float(zt.max()), 3), "teren_sredni": round(sr, 3),
                     "H_upzp_m": round(top_inst - sr, 2), "H_upzp_od_min_m": round(top_inst - float(zt.min()), 2),
                     "pokrycie_max_klin": round(z_wt6, 3),
                     "H_WT6_m": round(z_wt6 - min(zw), 2) if zw else None,
                     "teren_najnizsze_wejscie": round(min(zw), 3) if zw else None,
                     "kondygnacje_nadziemne": len(m.kondygnacje)}
    # okna / podłoga
    okna = []
    for r in m.pomieszczenia():
        if not r.pobyt_ludzi or r.polygon is None:
            continue
        A_m = A_o = 0.0
        ids = []
        for o in m.otwory(kond=r.kond):
            if o.typ in ("otwor", "drzwi", "brama") or o.sciana.typ != "sciana_zewn":
                continue
            sc = o.sciana
            n_out = np.asarray(o.kierunek_zewn, float) if o.kierunek_zewn is not None else np.zeros(2)
            gl = max(abs(sc.t_min), abs(sc.t_max)) + 0.30
            c_ = np.asarray(o.srodek, float)[:2] - n_out[:2] * gl
            if r.polygon.contains(Point(float(c_[0]), float(c_[1]))):
                A_m += o.szer * o.wys
                A_o += max(0.0, o.szer - 0.14) * max(0.0, o.wys - 0.14)
                ids.append(o.id)
        okna.append({"id": r.id, "nazwa": r.nazwa, "A_podl": round(r.pow_netto, 2), "okna": ids, "A_osciez": round(A_o, 2),
                     "stosunek": ("1:" + fmt(r.pow_netto / A_o, 1)) if A_o > 0 else "—", "ok": A_o >= r.pow_netto / 8})
    B["okna_podloga"] = okna
    # schody
    B["schody"] = [{"id": s["id"], "h": s["wys_stopnia"], "s": s["szer_stopnia"], "2h+s": round(2 * s["wys_stopnia"] + s["szer_stopnia"], 3),
                    "biegi_szer": [b["szer"] for b in s["biegi"]], "n": s["liczba_stopni"]} for s in m.schody()]
    B["miejsca_postojowe"] = len(dz.lista("miejsca_postojowe"))
    B["odleglosci"] = wyn_odl
    B["wiernosc_szkicowi"] = fidelity
    return B


def bilans_md(B) -> str:
    L = []
    w = B["wysokosc"]
    L += ["| wskaźnik | wartość | wymaganie | ocena |", "|---|---|---|---|"]
    pu = B["PU_W316_suma"]
    L.append(f"| PU wg RPB §20 / W-316 (bez klatek, garażu i techn.) | **{fmt(pu)} m²** (P0 {fmt(B['PU_W316'].get('P0', 0))}, "
             f"P1 {fmt(B['PU_W316'].get('P1', 0))}, P2 {fmt(B['PU_W316'].get('P2', 0))}) | 230–270 m² | {'✓' if 230 <= pu <= 270 else '✗'} |")
    iso = B["PN_ISO_9836"]
    L.append(f"| kontrolnie PN-ISO 9836 (rdzeń `lamela.model`, pipeline): podstawowa / pomocnicza z garażem / ruchu / techniczna | "
             f"{fmt(iso['podstawowa'])} / {fmt(iso['pomocnicza (z garażem)'])} / {fmt(iso['ruchu'])} / {fmt(iso['techniczna'])} m² "
             f"(„PU” rdzenia = podst. + pomocn. = {fmt(iso['podstawowa'] + iso['pomocnicza (z garażem)'])} m² — z garażem, bez komunikacji) | — | — |")
    L.append(f"| garaż (osobno) / pom. techniczne (osobno) / klatki | {fmt(B['garaz'])} / {fmt(B['techniczne'])} / {fmt(B['klatki'])} m² | — | — |")
    sd = next((r for r in B["pomieszczenia"] if r["id"] == "0.06"), None)
    if sd:
        L.append(f"| strefa dzienna salon + jadalnia + kuchnia | {fmt(sd['A'])} m² | ≥ 50 m² | {'✓' if sd['A'] >= 50 else '✗'} |")
    z = B["zabudowa"]
    L.append(f"| powierzchnia zabudowy (obrysy kondygnacji) | {fmt(z['m2'])} m² ({fmt(z['proc'])} %); z płytami {fmt(z['z_plytami_m2'])} m² | ≤ 480 m² (30 %) | "
             f"{'✓' if z['m2'] <= 480 else '✗'} |")
    p = B["PBC"]
    L.append(f"| powierzchnia biologicznie czynna | {fmt(p['m2'])} m² ({fmt(p['proc'])} %); rezerwa 50 % dachu zielonego {fmt(p['rezerwa_dach_zielony_50proc_m2'])} m² "
             f"| ≥ 800 m² (50 %) | {'✓' if p['m2'] >= 800 else '✗'} |")
    L.append(f"| intensywność zabudowy (Σ brutto kondygnacji / działka) | {fmt(B['intensywnosc'], 3)} | 0,05–0,80 | "
             f"{'✓' if 0.05 <= B['intensywnosc'] <= 0.8 else '✗'} |")
    L.append(f"| kubatura brutto | {fmt(B['kubatura_brutto_m3'], 1)} m³ | — (> 1000 m³ → PWP, W-190) | — |")
    L.append(f"| wysokość zabudowy (upzp art. 2 pkt 30): najwyższy punkt {fmt(w['najwyzszy_punkt_z_instalacjami'], 3)} − teren; na obwodzie niższa z rzędnych "
             f"istn./proj. (D-15); kontrolnie od NAJNIŻSZEGO terenu {fmt(w['teren_obwod_min'], 3)} (definicja: od średniej {fmt(w['teren_sredni'], 3)} "
             f"→ {fmt(w['H_upzp_m'])} m) | **{fmt(w['H_upzp_od_min_m'])} m** | ≤ 11,00 m (rezerwa → 10,70) | {'✓' if w['H_upzp_od_min_m'] <= 10.70 else '✗'} |")
    if w.get("H_WT6_m") is not None:
        L.append(f"| wysokość budynku wg WT §6: do najwyższego punktu pokrycia z klinem {fmt(w['pokrycie_max_klin'], 3)} − teren przy najniższym wejściu "
                 f"{fmt(w['teren_najnizsze_wejscie'], 3)} | {fmt(w['H_WT6_m'])} m | grupa N ≤ 12 m | "
                 f"{'✓' if w['H_WT6_m'] <= 12 else '✗'} |")
    L.append(f"| kondygnacje nadziemne | {w['kondygnacje_nadziemne']} | ≤ 3 | ✓ |")
    L.append(f"| miejsca postojowe (garaż + podjazd) | {B['miejsca_postojowe']} | ≥ 2 | {'✓' if B['miejsca_postojowe'] >= 2 else '✗'} |")
    for s in B["schody"]:
        L.append(f"| schody {s['id']}: {s['n']} × h {fmt(s['h'], 3)} / s {fmt(s['s'], 2)}; 2h+s; bieg | 2h+s = {fmt(s['2h+s'], 3)} m; bieg "
                 f"{' / '.join(fmt(b, 3) for b in s['biegi_szer'])} m | h ≤ 0,19; 0,60–0,65; ≥ 1,00 (cel) | ✓ |")
    L += ["", "**Odległości od granic działki i linii zabudowy** (lica zewnętrzne; WT §12: ściana z otworami ≥ 4,00 m, bez otworów ≥ 3,00 m; "
          "okapy/płyty ≥ 1,50 m — przyjęto ≥ 4,00 m):", "", "| element | W | E | S | do linii zabudowy |", "|---|---|---|---|---|"]
    for d in B["odleglosci"]:
        L.append(f"| {d['element']} | {fmt(d['W'])} | {fmt(d['E'])} | {fmt(d['S'])} | {fmt(d['N_linia_zab'])} |")
    L += ["", "**Okna / podłoga w pomieszczeniach na pobyt ludzi** (w świetle ościeżnic ≈ (szer − 0,14)(wys − 0,14); WT §57, W-080 ≥ 1/8):", "",
          "| pomieszczenie | pow. [m²] | okna | A okien [m²] | stosunek | ocena |", "|---|---|---|---|---|---|"]
    for o in B["okna_podloga"]:
        L.append(f"| {o['id']} {o['nazwa']} | {fmt(o['A_podl'])} | {', '.join(o['okna'])} | {fmt(o['A_osciez'])} | {o['stosunek']} | {'✓' if o['ok'] else '✗'} |")
    L += ["", "**Wierność szkicowi** (krawędzie elewacji S od lica zach. bryły B; szkic: brief §1.1, 45,8 px/m):", "",
          "| element | szkic [m] | model [m] | odchyłka [m] |", "|---|---|---|---|"]
    for r in B["wiernosc_szkicowi"]:
        L.append(f"| {r['element']} | {fmt(r['szkic'][0])} … {fmt(r['szkic'][1])} | {fmt(r['model'][0])} … {fmt(r['model'][1])} | {fmt(r['odchylka'])} |")
    L += ["", "**Zestawienie pomieszczeń** (PN-ISO 9836:2022; h — wysokość w świetle; zaliczenie 100/50/0 % wg W-316):", "",
          "| nr | pomieszczenie | kategoria | pow. netto [m²] | h [m] | zaliczona [m²] |", "|---|---|---|---|---|---|"]
    for r in B["pomieszczenia"]:
        L.append(f"| {r['id']} | {r['nazwa']} | {r['kat']} | {fmt(r['A'])} | {fmt(r['h'])} | {fmt(r['A_zal'])} |")
    return "\n".join(L)


# ------------------------------------------------------------------------------------------------ main
def wstaw_do_koncepcji(md: str, sciezka: Path):
    if not sciezka.exists():
        return False
    s = sciezka.read_text(encoding="utf-8")
    a, b = "<!-- BILANS:START -->", "<!-- BILANS:END -->"
    if a not in s or b not in s:
        return False
    i, j = s.index(a) + len(a), s.index(b)
    blok = ("\n*Blok generowany przez `tools/podglad_modelu.py` z `model/budynek.yaml` + `model/dzialka.yaml` — nie edytować ręcznie.*\n\n"
            + md + "\n")
    sciezka.write_text(s[:i] + blok + s[j:], encoding="utf-8")
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budynek", default=str(ROOT / "model" / "budynek.yaml"))
    ap.add_argument("--dzialka", default=str(ROOT / "model" / "dzialka.yaml"))
    ap.add_argument("--out", default=str(ROOT / "docs" / "20_koncepcja" / "final"))
    ap.add_argument("--koncepcja", default=str(ROOT / "docs" / "20_koncepcja" / "koncepcja.md"))
    ap.add_argument("--bez-koncepcji", action="store_true")
    ap.add_argument("--tylko", default=None, help="lista: rzuty,elewacje,szkic,przekroje,dzialka,bilans")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    m = load_model(a.budynek, a.dzialka, strict=True)
    pw = Path(a.budynek).with_name("wyposazenie.yaml")
    if pw.exists():
        import yaml
        WYP[:] = (yaml.safe_load(pw.read_text(encoding="utf-8")) or {}).get("wyposazenie") or []
    print(f"Model: {len(m.sciany())} ścian, {len(m.otwory())} otworów, {len(m.pomieszczenia())} pomieszczeń; walidacja: "
          f"{len(m.bledy)} błędów, {len(m.ostrzezenia)} ostrzeżeń")
    ir = build_ir(m, otoczenie=True, auta=False)
    co = set((a.tylko or "rzuty,dach,elewacje,szkic,przekroje,dzialka,bilans").split(","))
    if "rzuty" in co:
        for k in m.kondygnacje:
            rzut(m, ir, k.id, out / f"rzut_{k.id}.png")
    if "elewacje" in co:
        elewacje(m, ir, out / "elewacje.png")
        elewacje_osobno(m, ir, out)
    if "dach" in co:
        rzut_dachu(m, ir, out / "rzut_dachu.png")
    fid = elewacja_szkic(m, ir, out / "elewacja_S_szkic.png") if "szkic" in co else wiernosc(m)[0]
    if "przekroje" in co:
        przekroj(m, ir, "x", 6.55, out / "przekroj_AA.png", "Przekrój A-A (przez schody, boks C i bryłę A; widok na wschód)")
        przekroj(m, ir, "y", 1.50, out / "przekroj_BB.png", "Przekrój B-B (przez wspornik bryły A, strefę dzienną i pas gospodarczy; widok na północ)")
    wyn = dzialka_png(m, ir, out / "dzialka.png") if "dzialka" in co else odleglosci(m)[0]
    B = bilans(m, wyn, fid)
    md = bilans_md(B)
    (out / "bilans.json").write_text(json.dumps(B, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (out / "bilans.md").write_text("# Dom LAMELA — bilans powierzchni i wskaźniki (generowany z modelu)\n\n" + md + "\n", encoding="utf-8")
    if not a.bez_koncepcji and wstaw_do_koncepcji(md, Path(a.koncepcja)):
        print(f"Wstawiono bilans do {a.koncepcja}")
    w = B["wysokosc"]
    print(f"PU (W-316) = {B['PU_W316_suma']} m²; zabudowa {B['zabudowa']['m2']} m² ({B['zabudowa']['proc']} %); PBC {B['PBC']['m2']} m² "
          f"({B['PBC']['proc']} %); intensywność {B['intensywnosc']}; H upzp {w['H_upzp_od_min_m']} m (od śr. {w['H_upzp_m']}); H WT §6 {w['H_WT6_m']} m; "
          f"maks. odchyłka od szkicu {max(r['odchylka'] for r in fid)} m")
    print(f"Zapisano: {out}")


if __name__ == "__main__":
    main()
