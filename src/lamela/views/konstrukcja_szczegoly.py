"""Przekroje i szczegóły konstrukcyjne 1:20–1:10 (typ widoku ``k_przekroj`` — rejestracja w ``konstrukcja``).

Szczegóły (``detal``): ``zebro`` (przekrój żebra płyty fundamentowej — ``przekroj: "1"|"2"`` z rzutu fundamentów albo
``element: ZF…``), ``stopa`` (pogrubienie płyty pod słupem), ``wspornik`` (węzeł płyty wspornikowej z łącznikiem
termoizolacyjnym — ``element: PL-…``), ``wieniec`` (wieniec ściany zewnętrznej pod krawędzią stropu — ``poziom``),
``oparcie`` (strop ciągły nad ścianą wewnętrzną z muru silikatowego — ``poziom``).

Układ lokalny szczegółu: oś x — normalna do linii elementu (żebro, ściana, linia zamocowania wspornika) skierowana
na zewnątrz / w stronę wspornika, x = 0 w osi elementu; oś z — rzędna bezwzględna modelu [m]. Warstwy, grubości,
rzędne i materiały — z modelu; pręty (φ, rozstaw, liczba, numer pozycji) — z generatora zbrojenia (obliczenia).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, elements as E, fmt, hatch as H, symbols as S
from ..draft.core import Viewport
from . import konstrukcja_dane as KD
from .common import Placer, cut_kind, hatch_code, klasa_mat, material_name

L_ZBR = "K-ZBROJENIE"
L_OPI = "K-ZBROJENIE-OPIS"
L_OPS = "A-OPISY"
KOL_UZ = "#b0006a"


@dataclass
class Rama:
    """Układ lokalny szczegółu: punkt Q (x = 0), normalna n (kierunek +x)."""
    Q: np.ndarray
    n: np.ndarray

    def x(self, p) -> float:
        return float((np.asarray(p, float) - self.Q) @ self.n)


def warstwy_sciany(w, R: Rama) -> list:
    """Warstwy ściany w układzie lokalnym: [(x0, x1, kod materiału, konstrukcyjna, klasa)] (x rośnie wzdłuż R.n)."""
    s = float(w.n @ R.n)
    x_os = R.x(w.p1) if abs(float(w.u @ R.n)) < 1e-6 else R.x(w.pt(w.st(R.Q)[0], 0.0))
    out = []
    for ly in w.warstwy:
        a, b = sorted((x_os + ly.t0 * s, x_os + ly.t1 * s))
        out.append((a, b, ly.mat, ly.konstrukcyjna, ly.klasa))
    return out


def dodaj_warstwy_pionowe(cs, model, warstwy, z0: float, z1: float, typ: str = "sciana_zewn"):
    for a, b, mat, konstr, klasa in warstwy:
        hc = hatch_code(model, mat)
        cs.add(box(a, z0, b, z1), hc, cut_kind(hc, klasa_mat(model, mat), konstr, typ))


def dodaj_warstwy_poziome(cs, model, przegroda, x0: float, x1: float, z_top_konstr: float, gora: bool = True,
                          pomin_konstr: bool = True) -> list:
    """Warstwy przegrody poziomej nad (gora=True) lub pod warstwą konstrukcyjną; zwraca [(z0, z1, mat)]."""
    out = []
    if przegroda is None:
        return out
    ws = przegroda.warstwy
    k = przegroda.idx_konstr
    if gora:
        z = z_top_konstr
        for w in reversed(ws[:k]):
            out.append((z, z + w.d, w.mat))
            z += w.d
    else:
        z = z_top_konstr
        for w in ws[k + 1:]:
            out.append((z - w.d, z, w.mat))
            z -= w.d
    for z0, z1, mat in out:
        if z1 - z0 < 1e-5:
            continue
        hc = hatch_code(model, mat)
        cs.add(box(x0, z0, x1, z1), hc, cut_kind(hc, klasa_mat(model, mat)))
    return out


# ------------------------------------------------------------------------------------------------ zbrojenie
def pret_kropka(vp, x, z, fi):
    """Pręt prostopadły do płaszczyzny rysunku — kółko zaczernione średnicy φ (min. 0,9 mm na papierze)."""
    r = max(fi / 2000.0, 0.45 * vp.k)
    vp.fill(Point(x, z).buffer(r, 16), L_ZBR, "#000000", z=30)


def pret_linia(vp, pts, pen=0.5):
    vp.polyline(pts, L_ZBR, pen=pen, z=30)


def strzemie(vp, x0, z0, x1, z1, fi):
    """Strzemię zamknięte (oś pręta) z hakami 135° w narożu górnym lewym."""
    vp.rect(x0, z0, x1, z1, L_ZBR, pen=0.35, z=30)
    d = max(0.04, 3 * vp.k)
    vp.line((x0, z1), (x0 + d, z1 - d), L_ZBR, pen=0.35, z=30)
    vp.line((x0, z1 - 0.004), (x0 + d * 0.9, z1 - d * 1.1), L_ZBR, pen=0.35, z=30)


def rzad_kropek(vp, x0, x1, z, fi, s_mm):
    """Pręty rozdzielcze / siatki prostopadłe do rysunku co s w przedziale [x0, x1]."""
    n = max(int(math.floor((x1 - x0) / (s_mm / 1000.0))), 0) + 1
    if n <= 1:
        pret_kropka(vp, (x0 + x1) / 2, z, fi)
        return
    dx = (x1 - x0) / (n - 1)
    for i in range(n):
        pret_kropka(vp, x0 + i * dx, z, fi)


def opis(vp, placer: Placer, pt, tekst: str, nr: int | None = None, kier: str = "prawo", dz_mm: float = 8.0,
         h: float = 2.5, ts=None):
    """Odnośnik (kropka na elemencie) + półka z opisem; numer pozycji pręta w okręgu przed tekstem."""
    from .konstrukcja import _nr_poz
    from ..draft.text import width as tw
    k = vp.k
    P = np.asarray(pt, float)
    wt = tw(tekst, h) + (7.0 if nr is not None else 0.0)
    cands = []
    for dz in (dz_mm, -dz_mm, 1.5 * dz_mm, -1.5 * dz_mm, 2.2 * dz_mm, -2.2 * dz_mm):
        for dx in ((12.0, 22.0, 34.0) if kier == "prawo" else (-12.0, -22.0, -34.0)):
            cands.append((dx, dz))

    def draw(c, cand):
        dx, dz = cand
        B = P + np.array([dx * k, dz * k])
        sg = 1.0 if dx > 0 else -1.0
        c.line(P, B, L_OPI, pen="cienka")
        c.dot(P, 0.8, L_OPI)
        E_ = B + np.array([sg * wt * k, 0.0])
        c.line(B, E_, L_OPI, pen="cienka")
        x = B[0] + (0.8 * k if sg > 0 else -wt * k + 0.8 * k)
        if nr is not None:
            _nr_poz(c, (x + 2.6 * k, B[1] + 2.9 * k), nr, 2.5, L_OPI)
            x += 6.4 * k
        c.text((x, B[1] + 0.9 * k), tekst, h, 0.0, "left", "baseline", L_OPI)
    placer.place(vp, draw, cands, penalty_step=0.15)


def urwanie(vp, p0, p1):
    """Linia urwania (zygzak) między punktami p0, p1."""
    k = vp.k
    a, b = np.asarray(p0, float), np.asarray(p1, float)
    m = (a + b) / 2
    d = b - a
    L = float(np.hypot(*d))
    u = d / L
    nn = np.array([-u[1], u[0]])
    z = 2.0 * k
    pts = [a - u * 2 * k, m - u * z * 0.6, m + nn * z - u * z * 0.2, m - nn * z + u * z * 0.2, m + u * z * 0.6,
           b + u * 2 * k]
    vp.polyline(pts, "A-OPISY", pen="cienka")
