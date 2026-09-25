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
        "C — boks (przeszklenie)": otw(["O1-01"]),
        "C — rama górna": xr(ws["PL-C2"]),
        "D — linia pozioma": (xr(ws["PL-C1"])[0], xr(dg["D4"])[1]),
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
        ax.text(ax.get_xlim()[0], k.rzedna, f" {k.id} {k.rzedna:+.3f}", fontsize=6, color="#c0392b", va="bottom")
    osie_ = m.raw["osie"]["y" if os_ == "x" else "x"]
    for n_, v in osie_.items():
        ax.axvline(U(v), color="#c0392b", lw=0.3, ls=(0, (8, 3, 1, 3)), zorder=0.8)
        ax.text(U(v), 10.6, n_, ha="center", fontsize=7, color="#c0392b", bbox=dict(boxstyle="circle,pad=0.2", fc="w", ec="#c0392b", lw=0.5))
    lo, hi = (-12.0, 5.0) if os_ == "x" else (-4.0, 21.0)
    ax.set_xlim(lo, hi)
    ax.set_ylim(-1.6, 11.3)
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
    ax.set_title(f"{nazwa}: płaszczyzna {os_} = {fmt(c)} m — elementy przecięte (kolor materiału), widok (szary), teren; "
                 f"najwyższy punkt attyki {top:+.3f}", fontsize=9, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
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
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return wyn
