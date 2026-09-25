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

import math
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


def podzial(a: float, b: float, h_min: float, h_max: float, r: float = 1.25, n_min: int = 2,
            h_b: float | None = None) -> np.ndarray:
    """Krawędzie komórek na odcinku [a, b]: komórka h_min przy końcu a (h_b przy końcu b; domyślnie h_min),
    rosnące geometrycznie (×r) do h_max. Odcinek krótszy niż suma komórek końcowych (cienkie warstwy, membrany) —
    podział równomierny na max(n_min, ⌈L/h⌉) komórek. Wzrost jest ograniczany przed potęgowaniem (brak przepełnienia
    r**k dla długich odcinków i małego h_max — weryfikacja niezależna, uwaga 5)."""
    h_a = float(h_min)
    h_b = float(h_min if h_b is None else h_b)
    h_max = max(float(h_max), h_a, h_b)
    L = b - a
    if L <= 0:
        return np.array([a, b])
    h_lo = min(h_a, h_b)
    if L <= (h_a + h_b) * 1.0000001 or L <= n_min * h_lo * 1.0000001:
        n = max(1, n_min, int(math.ceil(L / h_lo - 1e-9)))
        return np.linspace(a, b, n + 1)

    def k_cap(h0: float) -> int:          # liczba kroków wzrostu do osiągnięcia h_max
        return int(math.ceil(math.log(h_max / h0) / math.log(r))) if h0 < h_max and r > 1 else 0

    ka, kb = k_cap(h_a), k_cap(h_b)
    lewe: list[float] = []
    prawe: list[float] = []
    sl = sp = 0.0
    kl = kp = 0
    while sl + sp < L:
        nl = min(h_a * r ** kl, h_max) if kl < ka else h_max
        np_ = min(h_b * r ** kp, h_max) if kp < kb else h_max
        if nl >= h_max and np_ >= h_max:
            # pozostała część — komórki h_max (bez pętli po tysiącach komórek)
            n = int(math.ceil((L - sl - sp) / h_max - 1e-12))
            lewe += [h_max] * n
            break
        # rozbudowa strony o mniejszej kolejnej komórce (przy równych — lewej): ciągi symetryczne dla h_a = h_b
        if nl <= np_:
            lewe.append(nl)
            sl += nl
            kl += 1
        else:
            prawe.append(np_)
            sp += np_
            kp += 1
    sizes = np.array(lewe + prawe[::-1])
    sizes *= L / sizes.sum()
    if len(sizes) < n_min:
        return np.linspace(a, b, n_min + 1)
    e = a + np.concatenate([[0.0], np.cumsum(sizes)])
    e[-1] = b
    return e


SNAP = 1e-6         # siatka przyciągania współrzędnych wierzchołków [m] (1 µm)
R_GRANICY = 2.0     # maks. iloraz rozmiarów sąsiednich komórek na granicy odcinków (warstw)


def _unikalne(v: np.ndarray, tol: float = 0.5 * SNAP) -> np.ndarray:
    v = np.sort(np.round(np.asarray(v, float) / SNAP) * SNAP)
    out = [v[0]]
    for t in v[1:]:
        if t - out[-1] > tol:
            out.append(t)
    return np.array(out)


def krawedzie(punkty: np.ndarray, h_min: float, h_max: float, r: float, n_min: int,
              r_granicy: float = R_GRANICY) -> np.ndarray:
    """Krawędzie komórek wzdłuż osi: linie siatki przez wszystkie (przyciągnięte do 1 µm) współrzędne wierzchołków,
    zagęszczenie geometryczne przy każdej linii. Rozmiar komórki przy linii granicznej jest ograniczany do
    r_granicy × rozmiar komórki po drugiej stronie linii (cienkie warstwy dobrze przewodzące — blachy, obróbki —
    nie sąsiadują z komórkami 10–40 razy większymi; weryfikacja niezależna, uwaga 4)."""
    p = _unikalne(punkty)
    n = len(p) - 1
    if n < 1:
        return p
    h_pt = np.full(n + 1, float(h_min))
    for _ in range(30):
        czesci = [podzial(p[k], p[k + 1], h_pt[k], h_max, r, n_min, h_b=h_pt[k + 1]) for k in range(n)]
        nowe = h_pt.copy()
        for k in range(n):
            d = np.diff(czesci[k])
            nowe[k] = min(nowe[k], r_granicy * d[0])            # linia k: komórka po prawej (początek odcinka k)
            nowe[k + 1] = min(nowe[k + 1], r_granicy * d[-1])  # linia k+1: komórka po lewej (koniec odcinka k)
        if np.allclose(nowe, h_pt, rtol=1e-9, atol=0.0):
            break
        h_pt = nowe
    return np.concatenate([c[:-1] for c in czesci] + [[p[-1]]])


def grubosc_min_przewodzacych(wezel: Wezel, lam_min: float = 1.0) -> float | None:
    """Najmniejsza grubość obszaru o λ ≥ lam_min (szacowana 2A/P — dla pasa t×L ≈ t; dla prostokąta min. bok)."""
    t = None
    for o in wezel.obszary:
        if o.mat.lam < lam_min:
            continue
        for part in getattr(o.wielobok, "geoms", [o.wielobok]):
            if part.is_empty or part.area <= 0:
                continue
            minx, miny, maxx, maxy = part.bounds
            est = min(2 * part.area / part.length, maxx - minx, maxy - miny) if part.length > 0 else 0.0
            t = est if t is None else min(t, est)
    return t


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
    # cienkie warstwy dobrze przewodzące (λ ≥ 1 — blachy, obróbki, profile): h_min ≤ ich grubość
    t_c = grubosc_min_przewodzacych(wezel)
    if t_c is not None and t_c > 0:
        par["h_min"] = min(par["h_min"], t_c)
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
