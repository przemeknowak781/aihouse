"""Siatka prostokątna niejednorodna (metoda objętości skończonych, komórki centrowane).

Wybór metody (uzasadnienie): węzły budowlane to prawie wyłącznie warstwy prostokątne. Siatka prostokątna, której
linie przechodzą przez WSZYSTKIE współrzędne wierzchołków wieloboków, odwzorowuje granice materiałów dokładnie
(bez rozmywania λ w komórce), a zagęszczenie geometryczne przy granicach (h_min → h_max, iloraz r) daje dużą
rozdzielczość tam, gdzie gradienty są największe. MOS jest lokalnie konserwatywna (bilans energii domyka się do
dokładności maszynowej), a podwajanie podziałów (każda komórka → 2) jest trywialne — kryterium PN-EN ISO 10211:2017
(zmiana strumienia < 1 % przy podwojeniu liczby podziałów) sprawdzane jest wprost. Krawędzie ukośne
(rzadkie w węzłach) są aproksymowane schodkowo — ograniczenie opisane w raporcie.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import shapely

from .geometria import Wezel

DOMYSLNE = {"h_min": 0.002, "h_max": 0.10, "r": 1.25, "n_min": 2}


@dataclass
class Siatka:
    x: np.ndarray       # krawędzie komórek (nx+1)
    y: np.ndarray       # (ny+1)

    @property
    def nx(self) -> int:
        return len(self.x) - 1

    @property
    def ny(self) -> int:
        return len(self.y) - 1

    @property
    def xc(self) -> np.ndarray:
        return 0.5 * (self.x[1:] + self.x[:-1])

    @property
    def yc(self) -> np.ndarray:
        return 0.5 * (self.y[1:] + self.y[:-1])

    @property
    def dx(self) -> np.ndarray:
        return np.diff(self.x)

    @property
    def dy(self) -> np.ndarray:
        return np.diff(self.y)

    @property
    def n(self) -> int:
        return self.nx * self.ny

    def podwojona(self) -> "Siatka":
        """Każda komórka dzielona na 2 w obu kierunkach (podwojenie liczby podziałów, ISO 10211)."""
        return Siatka(_podwoj(self.x), _podwoj(self.y))

    def opis(self) -> str:
        return (f"{self.nx} × {self.ny} = {self.n} komórek; Δx ∈ [{self.dx.min() * 1000:.3g}; {self.dx.max() * 1000:.4g}] mm, "
                f"Δy ∈ [{self.dy.min() * 1000:.3g}; {self.dy.max() * 1000:.4g}] mm")


def _podwoj(e: np.ndarray) -> np.ndarray:
    mid = 0.5 * (e[1:] + e[:-1])
    out = np.empty(2 * len(e) - 1)
    out[0::2] = e
    out[1::2] = mid
    return out


def podzial(a: float, b: float, h_min: float, h_max: float, r: float = 1.25, n_min: int = 2) -> np.ndarray:
    """Krawędzie komórek na odcinku [a, b]: komórki h_min przy obu końcach, rosnące geometrycznie (×r) do h_max."""
    L = b - a
    if L <= 0:
        return np.array([a, b])
    if L <= n_min * h_min * 1.0000001 or L <= 2 * h_min:
        return np.linspace(a, b, max(1, n_min) + 1)     # cienkie warstwy (membrany): n_min komórek
    pol = []
    acc = 0.0
    k = 0
    while acc < L / 2:
        s = min(h_min * r ** k, h_max)
        pol.append(s)
        acc += s
        k += 1
    # dwa warianty: parzysta (pol + odwr(pol)) lub nieparzysta (środkowa komórka wspólna)
    war1 = pol + pol[::-1]
    war2 = pol + pol[-2::-1]
    s1, s2 = sum(war1), sum(war2)
    sizes = war2 if (s2 >= L) else war1
    tot = sum(sizes)
    sizes = np.array(sizes) * (L / tot)
    if len(sizes) < n_min:
        return np.linspace(a, b, n_min + 1)
    e = a + np.concatenate([[0.0], np.cumsum(sizes)])
    e[-1] = b
    return e


def _unikalne(v: np.ndarray, tol: float = 1e-7) -> np.ndarray:
    v = np.sort(np.asarray(v, float))
    out = [v[0]]
    for t in v[1:]:
        if t - out[-1] > tol:
            out.append(t)
    return np.array(out)


def krawedzie(punkty: np.ndarray, h_min: float, h_max: float, r: float, n_min: int) -> np.ndarray:
    p = _unikalne(punkty)
    czesci = [podzial(p[i], p[i + 1], h_min, h_max, r, n_min)[:-1] for i in range(len(p) - 1)]
    return np.concatenate(czesci + [[p[-1]]])


def wspolrzedne_wierzcholkow(geoms) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for g in geoms:
        for part in getattr(g, "geoms", [g]):
            if part.is_empty:
                continue
            rings = [part.exterior] + list(part.interiors) if hasattr(part, "exterior") else [part]
            for rg in rings:
                c = np.asarray(rg.coords)
                xs.append(c[:, 0])
                ys.append(c[:, 1])
    return np.concatenate(xs), np.concatenate(ys)


def siatka_dla_wezla(wezel: Wezel, h_min: float | None = None, h_max: float | None = None, r: float | None = None,
                     n_min: int | None = None) -> Siatka:
    """Siatka, której linie przechodzą przez wszystkie wierzchołki obszarów i stref (granice materiałów dokładne),
    zagęszczana geometrycznie przy tych liniach. Parametry: argumenty > `wezel.siatka` > DOMYSLNE."""
    par = dict(DOMYSLNE)
    par.update(wezel.siatka or {})
    for k, v in (("h_min", h_min), ("h_max", h_max), ("r", r), ("n_min", n_min)):
        if v is not None:
            par[k] = v
    geoms = [o.wielobok for o in wezel.obszary] + [s.wielobok for s in wezel.strefy]
    xs, ys = wspolrzedne_wierzcholkow(geoms)
    minx, miny, maxx, maxy = wezel.bounds()
    xs = np.concatenate([xs, [minx, maxx]])
    ys = np.concatenate([ys, [miny, maxy]])
    xs = xs[(xs >= minx - 1e-12) & (xs <= maxx + 1e-12)]
    ys = ys[(ys >= miny - 1e-12) & (ys <= maxy + 1e-12)]
    return Siatka(krawedzie(xs, par["h_min"], par["h_max"], par["r"], par["n_min"]),
                  krawedzie(ys, par["h_min"], par["h_max"], par["r"], par["n_min"]))


# --------------------------------------------------------------------------------------------------
# Klasyfikacja komórek
# --------------------------------------------------------------------------------------------------
@dataclass
class Klasyfikacja:
    mat_id: np.ndarray      # (ny, nx) indeks w `materialy` albo −1
    strefa_id: np.ndarray   # (ny, nx) indeks w wezel.strefy albo −1
    materialy: list         # lista Material
    lam: np.ndarray         # (ny, nx) λ (nan poza materiałem)


def klasyfikuj(wezel: Wezel, s: Siatka) -> Klasyfikacja:
    xc, yc = s.xc, s.yc
    mat_id = np.full((s.ny, s.nx), -1, dtype=np.int32)
    strefa_id = np.full((s.ny, s.nx), -1, dtype=np.int32)
    mats = wezel.materialy()
    idx = {m.kod: i for i, m in enumerate(mats)}

    def maska(geom):
        minx, miny, maxx, maxy = geom.bounds
        i0, i1 = np.searchsorted(xc, minx), np.searchsorted(xc, maxx, side="right")
        j0, j1 = np.searchsorted(yc, miny), np.searchsorted(yc, maxy, side="right")
        if i1 <= i0 or j1 <= j0:
            return None
        X, Y = np.meshgrid(xc[i0:i1], yc[j0:j1])
        shapely.prepare(geom)
        m = shapely.contains_xy(geom, X, Y)
        return (slice(j0, j1), slice(i0, i1)), m

    for o in wezel.obszary:
        r = maska(o.wielobok)
        if r is None:
            continue
        sl, m = r
        blok = mat_id[sl]
        blok[m] = idx[o.mat.kod]
    for k, st in enumerate(wezel.strefy):
        r = maska(st.wielobok)
        if r is None:
            continue
        sl, m = r
        blok = strefa_id[sl]
        wolne = mat_id[sl] < 0
        blok[m & wolne] = k
    lamv = np.array([m.lam for m in mats] + [np.nan])
    lam = lamv[mat_id]           # −1 → ostatni (nan)
    return Klasyfikacja(mat_id, strefa_id, mats, lam)
