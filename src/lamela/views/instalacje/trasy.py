"""Wyznaczanie tras przewodów (gdy model nie zawiera przebiegów): trasy ORTOGONALNE na siatce 0,10 m.

Metoda (opisywana w uwagach arkuszy): koszt komórki siatki = 1 (wnętrze pomieszczeń), × 0,5 w pasie 0,05–0,25 m
od lica ścian (prowadzenie przy ścianach), + 8 w obrębie ścian przeciętych (przejście przez ścianę — tylko gdy objazd
przez drzwi jest dłuższy o > ok. 0,8 m), + 6 poza obrysem kondygnacji, × 0,4 w szachtach instalacyjnych; kara za
załamanie trasy (0,3 m); komórki zajęte przez inne media + 4 (rozsunięcie przewodów), zajęte przez to samo medium
× 0,35 (łączenie w pnie — rozgałęzienia trójnikowe). Najtańsza droga: algorytm Dijkstry na grafie dwuwarstwowym
(ruch poziomy / pionowy, przejście między warstwami = załamanie) — ``scipy.sparse.csgraph.dijkstra``.
"""
from __future__ import annotations

import numpy as np
import shapely
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
from shapely.geometry import Polygon

CELL = 0.10


class Siatka:
    def __init__(self, bounds, cell: float = CELL):
        x0, y0, x1, y1 = bounds
        self.cell = cell
        self.x0 = np.floor(x0 / cell) * cell
        self.y0 = np.floor(y0 / cell) * cell
        self.nx = int(np.ceil((x1 - self.x0) / cell)) + 1
        self.ny = int(np.ceil((y1 - self.y0) / cell)) + 1
        self.cost = np.ones((self.ny, self.nx), float)
        self.occ: dict[str, np.ndarray] = {}
        xs = self.x0 + (np.arange(self.nx) + 0.5) * cell
        ys = self.y0 + (np.arange(self.ny) + 0.5) * cell
        self.X, self.Y = np.meshgrid(xs, ys)

    # --------------------------------------------------------------------------------------------- geometria
    def mask(self, geom) -> np.ndarray:
        if geom is None or geom.is_empty:
            return np.zeros((self.ny, self.nx), bool)
        return shapely.contains_xy(geom, self.X, self.Y)

    def add(self, geom, add: float = 0.0, mul: float = 1.0, set_: float | None = None):
        m = self.mask(geom)
        if set_ is not None:
            self.cost[m] = set_
        else:
            self.cost[m] = self.cost[m] * mul + add

    def ij(self, p):
        j = int(np.clip(np.floor((p[0] - self.x0) / self.cell), 0, self.nx - 1))
        i = int(np.clip(np.floor((p[1] - self.y0) / self.cell), 0, self.ny - 1))
        return i, j

    def xy(self, i, j):
        return np.array([self.x0 + (j + 0.5) * self.cell, self.y0 + (i + 0.5) * self.cell])

    def mark(self, path, medium: str, width: int = 0):
        occ = self.occ.setdefault(medium, np.zeros((self.ny, self.nx), bool))
        P = np.asarray(path, float)
        for a, b in zip(P[:-1], P[1:]):
            n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1])) / (self.cell * 0.5)) + 1
            for t in np.linspace(0, 1, n + 1):
                i, j = self.ij(a + (b - a) * t)
                occ[max(0, i - width):i + width + 1, max(0, j - width):j + width + 1] = True

    # --------------------------------------------------------------------------------------------- trasa
    def route(self, a, b, medium: str = "", reuse: float = 0.35, other: float = 4.0, turn: float = 0.3,
              margin: float = 3.0, targets=None, companion: str | None = None, ignore=()):
        """Trasa ortogonalna a → b (albo a → najbliższa komórka ``targets``: maska istniejącej sieci). Zwraca
        łamaną [(x, y), …] z dokładnymi punktami końcowymi."""
        a = np.asarray(a, float)
        pts = [a] + ([np.asarray(b, float)] if b is not None else [])
        if targets is not None:
            ii, jj = np.nonzero(targets)
            if len(ii):
                pts += [self.xy(ii.min(), jj.min()), self.xy(ii.max(), jj.max())]
        P = np.array(pts)
        lo = P.min(axis=0) - margin
        hi = P.max(axis=0) + margin
        i0, j0 = self.ij(lo)
        i1, j1 = self.ij(hi)
        sub = (slice(i0, i1 + 1), slice(j0, j1 + 1))
        eff = self.cost[sub].copy()
        for med, occ in self.occ.items():
            o = occ[sub]
            if med == medium:
                eff[o] *= reuse
            elif med == companion:
                near = _dilate(o) & ~o
                eff[near] *= 0.55
                eff[o] += other
            elif med not in ignore:
                eff[o] += other
        ny, nx = eff.shape
        ia, ja = self.ij(a)
        src = (ia - i0) * nx + (ja - j0)
        dist, pred = _solve(eff, self.cell, turn, src)
        N = ny * nx
        if targets is not None:
            t = targets[sub].ravel()
            cand = np.nonzero(t)[0]
            if not len(cand):
                return self.route(a, b, medium, reuse, other, turn, margin, None, companion, ignore)
            d2 = np.minimum(dist[cand], dist[cand + N])
            tgt = int(cand[np.argmin(d2)])
            end = None
        else:
            ib, jb = self.ij(b)
            tgt = (ib - i0) * nx + (jb - j0)
            end = np.asarray(b, float)
        node = tgt if dist[tgt] <= dist[tgt + N] else tgt + N
        cells = []
        while node >= 0:
            c = node % N
            if not cells or cells[-1] != c:
                cells.append(c)
            node = pred[node]
            if node < 0 or node == -9999:
                break
        cells.reverse()
        path = [self.xy(i0 + c // nx, j0 + c % nx) for c in cells]
        if end is None:
            end = path[-1]
        return _snap(_simplify(path), a, end)


def _dilate(m):
    o = m.copy()
    o[1:, :] |= m[:-1, :]
    o[:-1, :] |= m[1:, :]
    o[:, 1:] |= m[:, :-1]
    o[:, :-1] |= m[:, 1:]
    return o


def _solve(eff, cell, turn, src):
    ny, nx = eff.shape
    N = ny * nx
    idx = np.arange(N).reshape(ny, nx)
    w = np.maximum(eff.ravel(), 1e-3) * cell
    a, b = idx[:, :-1].ravel(), idx[:, 1:].ravel()
    a2, b2 = idx[:-1, :].ravel(), idx[1:, :].ravel()
    al = idx.ravel()
    rows = np.concatenate([a, b, a2 + N, b2 + N, al, al + N])
    cols = np.concatenate([b, a, b2 + N, a2 + N, al + N, al])
    wt = np.concatenate([w[b], w[a], w[b2], w[a2], np.full(N, turn), np.full(N, turn)])
    G = csr_matrix((wt, (rows, cols)), shape=(2 * N, 2 * N))
    dist, pred = dijkstra(G, directed=True, indices=[src, src + N], return_predecessors=True, min_only=True)
    return dist, pred


def _simplify(path):
    P = [np.asarray(p, float) for p in path]
    if len(P) < 3:
        return P
    out = [P[0]]
    for i in range(1, len(P) - 1):
        d1 = P[i] - out[-1]
        d2 = P[i + 1] - P[i]
        if abs(d1[0] * d2[1] - d1[1] * d2[0]) < 1e-9:
            continue
        out.append(P[i])
    out.append(P[-1])
    return out


def _snap(P, a, b):
    """Dokładne punkty końcowe z zachowaniem ortogonalności (przesunięcie sąsiedniego wierzchołka)."""
    P = [np.array(p, float) for p in P]
    if len(P) == 1:
        P = [P[0], P[0].copy()]
    for end, pt, nb in ((0, a, 1), (-1, b, -2)):
        q = P[end]
        n = P[nb]
        horiz = abs(n[1] - q[1]) < 1e-9 and abs(n[0] - q[0]) > 1e-9
        if len(P) == 2:
            horiz = abs(b[1] - a[1]) < abs(b[0] - a[0])
        P[end] = np.array(pt, float)
        if len(P) > 2:
            if horiz:
                P[nb][1] = pt[1]
            else:
                P[nb][0] = pt[0]
    if len(P) == 2 and abs(P[0][0] - P[1][0]) > 1e-6 and abs(P[0][1] - P[1][1]) > 1e-6:
        P = [P[0], np.array([P[1][0], P[0][1]]), P[1]]
    return [p for i, p in enumerate(P) if i == 0 or float(np.hypot(*(p - P[i - 1]))) > 1e-6]


def siatka_kondygnacji(pod, extra_bounds=None, szachty=(), poza: float = 6.0, sciany: float = 8.0,
                       przy_scianie: float = 0.5, cell: float = CELL) -> Siatka:
    """Siatka kosztów dla rzutu kondygnacji (podkład ``pod``)."""
    e = pod.outline.bounds if pod.outline is not None and not pod.outline.is_empty else pod.extent
    x0, y0, x1, y1 = e
    if extra_bounds:
        x0, y0 = min(x0, extra_bounds[0]), min(y0, extra_bounds[1])
        x1, y1 = max(x1, extra_bounds[2]), max(y1, extra_bounds[3])
    g = Siatka((x0 - 3.0, y0 - 3.0, x1 + 3.0, y1 + 3.0), cell)
    inside = g.mask(pod.outline) if pod.outline is not None else np.ones_like(g.cost, bool)
    g.cost[~inside] += poza
    cut = pod.cut_region if pod.cut_region is not None else Polygon()
    if not cut.is_empty:
        band = cut.buffer(0.25, join_style=2).difference(cut.buffer(0.05, join_style=2))
        g.add(band.intersection(pod.outline) if pod.outline is not None else band, mul=przy_scianie)
        g.add(cut, add=sciany)
    for sz in szachty:
        g.add(sz, mul=0.4)
    return g
