"""Płyty żelbetowe — statyka.

1. **Tablice współczynników dla płyt prostokątnych** (odpowiednik tablic Czernego/Timoshenki): momenty i ugięcia płyty
   sprężystej (teoria Kirchhoffa) obciążonej równomiernie, krawędzie swobodnie podparte ``S`` lub utwierdzone ``U``.
   Współczynniki generowane metodą różnic skończonych (siatka 80 pól na krótszym boku, schemat 13-punktowy,
   węzły fikcyjne wg warunków brzegowych) i buforowane; zgodność z Timoshenko & Woinowsky-Krieger, *Theory of Plates
   and Shells*, 1959, tabl. 8 i 35 — ≤ 1 % (test). Płyty ciągłe: metoda „obciążeń zastępczych” (szachownicowa):
   M_przęsło = α(warunki rzeczywiste)·(g + q/2)·l² + α(SSSS)·(q/2)·l², M_podpora = β(warunki rzeczywiste)·(g + q)·l²
   (np. Starosolski, *Konstrukcje żelbetowe wg Eurokodu 2*, t. II, PWN 2012 — płyty krzyżowo zbrojone).

2. **MES płytowy** (orientacyjny, „poziom 2”): prostokątny element niekonforemny ACM (Adini–Clough–Melosh, 12 st. swob.:
   w, ∂w/∂x, ∂w/∂y w narożach) na siatce ortogonalnej dopasowanej do osi podpór; dowolny obrys płyty z otworami,
   podpory liniowe (ściany, belki — sztywne), punktowe (słupy), brzegi swobodne, obciążenia powierzchniowe, liniowe
   (ścianki działowe) i skupione. Momenty wymiarujące wg Wood–Armer (rozkład m_x, m_y, m_xy na kierunki zbrojenia).
   Weryfikacja: płyta kwadratowa swobodnie podparta i utwierdzona (Timoshenko) — test.

Konwencja: w dodatnie w dół (zgodnie z obciążeniem), m dodatnie — rozciąganie dołem. Jednostki: kN, m, kPa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from .wspolne import BladDanych


# ==================================================================================================
# 1. Tablice współczynników — metoda różnic skończonych
# ==================================================================================================
def _op1d(n: int, h: float, lewy: str, prawy: str):
    """Operatory 1D na n węzłach wewnętrznych: D2 (druga pochodna, w=0 na brzegu), D4 (czwarta, węzły fikcyjne)."""
    e = np.ones(n)
    D2 = sp.diags([e[:-1], -2 * e, e[:-1]], [-1, 0, 1], shape=(n, n)) / h ** 2
    D4 = sp.diags([e[:-2], -4 * e[:-1], 6 * e, -4 * e[:-1], e[:-2]], [-2, -1, 0, 1, 2], shape=(n, n)).tolil()
    D4[0, 0] += (-1.0 if lewy == "S" else 1.0)      # w_{-1} = ∓w_1 (S: M = 0 → w'' = 0; U: w' = 0)
    D4[n - 1, n - 1] += (-1.0 if prawy == "S" else 1.0)
    return D2.tocsr(), (D4 / h ** 4).tocsr()


@lru_cache(maxsize=512)
def _fd_plyta(lx: float, ly: float, brzegi: str, nu: float, n_krotszy: int = 80):
    """Rozwiązanie FD płyty lx × ly (D = 1, q = 1). brzegi: 4 znaki S/U dla krawędzi x=0, x=lx, y=0, y=ly."""
    lmin = min(lx, ly)
    Nx = max(int(round(n_krotszy * lx / lmin)), 4)
    Ny = max(int(round(n_krotszy * ly / lmin)), 4)
    hx, hy = lx / Nx, ly / Ny
    nx, ny = Nx - 1, Ny - 1
    D2x, D4x = _op1d(nx, hx, brzegi[0], brzegi[1])
    D2y, D4y = _op1d(ny, hy, brzegi[2], brzegi[3])
    Ix, Iy = sp.identity(nx), sp.identity(ny)
    A = sp.kron(Iy, D4x) + 2 * sp.kron(D2y, D2x) + sp.kron(D4y, Ix)
    w = spla.spsolve(A.tocsc(), np.ones(nx * ny))
    Wxx = sp.kron(Iy, D2x) @ w
    Wyy = sp.kron(D2y, Ix) @ w
    mx = -(Wxx + nu * Wyy)
    my = -(Wyy + nu * Wxx)
    W = w.reshape(ny, nx)
    # momenty utwierdzenia (węzły brzegowe): m_n = −w_nn = −2·w_1/h²
    mxe0 = -2 * W[:, 0] / hx ** 2 if brzegi[0] == "U" else np.zeros(ny)
    mxe1 = -2 * W[:, -1] / hx ** 2 if brzegi[1] == "U" else np.zeros(ny)
    mye0 = -2 * W[0, :] / hy ** 2 if brzegi[2] == "U" else np.zeros(nx)
    mye1 = -2 * W[-1, :] / hy ** 2 if brzegi[3] == "U" else np.zeros(nx)
    return {"w": float(w.max()), "mx": float(mx.max()), "my": float(my.max()),
            "mx_podp": (float(mxe0.min()), float(mxe1.min())), "my_podp": (float(mye0.min()), float(mye1.min()))}


@dataclass
class WspolczynnikiPlyty:
    """Współczynniki płyty prostokątnej lx × ly (normowane przez q·l_x² oraz q·l_x⁴/D; l_x — rozpiętość w kierunku x).

    alfa_x, alfa_y — maksymalne momenty przęsłowe m = α·q·l_x²; beta_x = (x=0, x=lx), beta_y = (y=0, y=ly) —
    momenty podporowe (ujemne; 0 dla krawędzi S); k_w — ugięcie w = k_w·q·l_x⁴/D, D = E·h³/(12(1−ν²)).
    """
    lx: float
    ly: float
    brzegi: str
    nu: float
    alfa_x: float
    alfa_y: float
    beta_x: tuple
    beta_y: tuple
    k_w: float

    def momenty(self, q: float) -> dict:
        l2 = q * self.lx ** 2
        return {"mx": self.alfa_x * l2, "my": self.alfa_y * l2, "mx_podp": tuple(b * l2 for b in self.beta_x),
                "my_podp": tuple(b * l2 for b in self.beta_y)}


def wspolczynniki_plyty(lx: float, ly: float, brzegi: str = "SSSS", nu: float = 0.2) -> WspolczynnikiPlyty:
    """Współczynniki płyty prostokątnej (tablice Czernego/Timoshenki — generowane MRS). brzegi: x=0, x=lx, y=0, y=ly."""
    brzegi = brzegi.upper()
    if len(brzegi) != 4 or set(brzegi) - {"S", "U"}:
        raise BladDanych(f"brzegi płyty: 4 znaki S/U, otrzymano {brzegi!r}")
    # normalizacja do lx = 1 (współczynniki zależą tylko od ly/lx)
    r = round(ly / lx, 3)
    res = _fd_plyta(1.0, r, brzegi, round(nu, 3))
    return WspolczynnikiPlyty(lx, ly, brzegi, nu, res["mx"], res["my"], res["mx_podp"], res["my_podp"], res["w"])


@dataclass
class PoleCiagle:
    """Pole płyty ciągłej (metoda tablic, obciążenie szachownicowe)."""
    lx: float
    ly: float
    brzegi: str               # warunki rzeczywiste: S (brzeg zewnętrzny) / U (ciągłość nad podporą)
    g: float                  # obliczeniowe obciążenie stałe [kPa]
    q: float                  # obliczeniowe obciążenie zmienne [kPa]
    mx: float = 0.0
    my: float = 0.0
    mx_podp: tuple = (0.0, 0.0)
    my_podp: tuple = (0.0, 0.0)
    wsp_rzecz: WspolczynnikiPlyty | None = None
    wsp_ssss: WspolczynnikiPlyty | None = None
    nu: float = 0.2

    def __post_init__(self):
        a = wspolczynniki_plyty(self.lx, self.ly, self.brzegi, self.nu)
        s = wspolczynniki_plyty(self.lx, self.ly, "SSSS", self.nu)
        self.wsp_rzecz, self.wsp_ssss = a, s
        l2 = self.lx ** 2
        self.mx = (a.alfa_x * (self.g + self.q / 2) + s.alfa_x * self.q / 2) * l2
        self.my = (a.alfa_y * (self.g + self.q / 2) + s.alfa_y * self.q / 2) * l2
        self.mx_podp = tuple(b * (self.g + self.q) * l2 for b in a.beta_x)
        self.my_podp = tuple(b * (self.g + self.q) * l2 for b in a.beta_y)


def wyrownaj_moment_podporowy(m1: float, m2: float) -> float:
    """Moment nad podporą wspólną dwóch pól: max(średnia, 0,8·max) (praktyka metody tablic) — wartości ujemne."""
    a, b = abs(m1), abs(m2)
    return -max(0.5 * (a + b), 0.8 * max(a, b))


# ==================================================================================================
# 2. MES płytowy — element ACM
# ==================================================================================================
def _P(x, y):
    return np.array([1, x, y, x * x, x * y, y * y, x ** 3, x * x * y, x * y * y, y ** 3, x ** 3 * y, x * y ** 3])


def _Px(x, y):
    return np.array([0, 1, 0, 2 * x, y, 0, 3 * x * x, 2 * x * y, y * y, 0, 3 * x * x * y, y ** 3])


def _Py(x, y):
    return np.array([0, 0, 1, 0, x, 2 * y, 0, x * x, 2 * x * y, 3 * y * y, x ** 3, 3 * x * y * y])


def _Pxx(x, y):
    return np.array([0, 0, 0, 2, 0, 0, 6 * x, 2 * y, 0, 0, 6 * x * y, 0])


def _Pyy(x, y):
    return np.array([0, 0, 0, 0, 0, 2, 0, 0, 2 * x, 6 * y, 0, 6 * x * y])


def _Pxy(x, y):
    return np.array([0, 0, 0, 0, 1, 0, 0, 2 * x, 2 * y, 0, 3 * x * x, 3 * y * y])


_GP3 = (np.array([-math.sqrt(0.6), 0.0, math.sqrt(0.6)]), np.array([5 / 9, 8 / 9, 5 / 9]))


@lru_cache(maxsize=1024)
def _acm(a: float, b: float, nu: float):
    """Macierze elementu ACM a×b (D = 1): Cinv, K (12×12), f_q (12, q = 1). Węzły: (0,0),(a,0),(a,b),(0,b); st. swob. w, w_x, w_y."""
    nodes = [(0, 0), (a, 0), (a, b), (0, b)]
    C = np.zeros((12, 12))
    for k, (x, y) in enumerate(nodes):
        C[3 * k] = _P(x, y)
        C[3 * k + 1] = _Px(x, y)
        C[3 * k + 2] = _Py(x, y)
    Ci = np.linalg.inv(C)
    Dm = np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu) / 2]])
    K = np.zeros((12, 12))
    fq = np.zeros(12)
    gp, gw = _GP3
    for xi, wx in zip(gp, gw):
        for eta, wy in zip(gp, gw):
            x, y = a * (xi + 1) / 2, b * (eta + 1) / 2
            B = np.vstack([_Pxx(x, y), _Pyy(x, y), 2 * _Pxy(x, y)]) @ Ci
            wgt = wx * wy * a * b / 4
            K += B.T @ Dm @ B * wgt
            fq += (_P(x, y) @ Ci) * wgt
    return Ci, K, fq


@dataclass
class PodporaLiniowa:
    id: str
    linia: LineString
    typ: str = "przegub"          # przegub | utwierdzenie
    rodzaj: str = "sciana"        # sciana | belka | krawedz


@dataclass
class PodporaPunktowa:
    id: str
    xy: tuple
    rodzaj: str = "slup"


@dataclass
class WynikMES:
    """Wynik przypadku/kombinacji: ugięcia węzłów w [m] (przy D rzeczywistym), momenty w środkach elementów
    m [n_el × 3] = (m_x, m_y, m_xy) [kNm/m], reakcje węzłowe R [kN] (dodatnie w górę) w węzłach podpartych."""
    w: np.ndarray
    m: np.ndarray
    R: np.ndarray

    def __add__(self, o):
        return WynikMES(self.w + o.w, self.m + o.m, self.R + o.R)

    def __mul__(self, a):
        return WynikMES(self.w * a, self.m * a, self.R * a)

    __rmul__ = __mul__


def wood_armer(m: np.ndarray) -> dict:
    """Momenty wymiarujące Wood–Armer: dół (≥ 0) i góra (≤ 0) w kierunkach x, y. m: [n × 3] (m_x, m_y, m_xy)."""
    mx, my, mxy = m[:, 0], m[:, 1], np.abs(m[:, 2])
    with np.errstate(divide="ignore", invalid="ignore"):
        bx, by = mx + mxy, my + mxy
        c1 = bx < 0
        bx = np.where(c1, 0.0, bx)
        by = np.where(c1, my + np.where(mx != 0, mxy ** 2 / np.abs(mx), 0), by)
        c2 = by < 0
        by = np.where(c2, 0.0, by)
        bx = np.where(c2 & ~c1, mx + np.where(my != 0, mxy ** 2 / np.abs(my), 0), bx)
        tx, ty = mx - mxy, my - mxy
        d1 = tx > 0
        tx = np.where(d1, 0.0, tx)
        ty = np.where(d1, my - np.where(mx != 0, mxy ** 2 / np.abs(mx), 0), ty)
        d2 = ty > 0
        ty = np.where(d2, 0.0, ty)
        tx = np.where(d2 & ~d1, mx - np.where(my != 0, mxy ** 2 / np.abs(my), 0), tx)
    return {"dol_x": np.clip(bx, 0, None), "dol_y": np.clip(by, 0, None),
            "gora_x": np.clip(tx, None, 0), "gora_y": np.clip(ty, None, 0)}


class PlytaMES:
    """Płyta na siatce prostokątnej elementów ACM.

    obrys — wielobok płyty (z otworami); grubosc [m]; E [kPa] (dla ugięć sprężystych; momenty od E niezależne);
    podpory_liniowe / podpory_punktowe; siatka — maks. bok elementu [m]; linie_siatki — dodatkowe współrzędne
    (x_list, y_list), przez które mają przechodzić linie siatki (np. granice pól do obciążeń szachownicowych).
    """

    def __init__(self, obrys: Polygon, grubosc: float, E: float, nu: float = 0.2,
                 podpory_liniowe: list[PodporaLiniowa] | None = None,
                 podpory_punktowe: list[PodporaPunktowa] | None = None, siatka: float = 0.2,
                 linie_siatki: tuple = ((), ()), strefy: list | None = None):
        self.obrys = obrys
        self.h = float(grubosc)
        self.E = float(E)
        self.nu = float(nu)
        self.D = self.E * self.h ** 3 / (12 * (1 - self.nu ** 2))
        self.pl = list(podpory_liniowe or [])
        self.pp = list(podpory_punktowe or [])
        self.uwagi: list[str] = []
        self._siatka(siatka, linie_siatki)
        # strefy o innej grubości/module: [(Polygon, h, E)] — sztywność D elementu wg środka elementu
        self.D_el = np.full(len(self.els), self.D)
        self.h_el = np.full(len(self.els), self.h)
        for g, hh, EE in (strefy or []):
            msk = self.elementy_w(g)
            self.D_el[msk] = EE * hh ** 3 / (12 * (1 - self.nu ** 2))
            self.h_el[msk] = hh
        self._sztywnosc()
        self._warunki()

    # ---------------- siatka ----------------
    def _siatka(self, hmax, linie):
        minx, miny, maxx, maxy = self.obrys.bounds
        xs = {minx, maxx}
        ys = {miny, maxy}

        def add_ring(coords):
            for x, y in coords:
                xs.add(x)
                ys.add(y)
        add_ring(self.obrys.exterior.coords)
        for r in self.obrys.interiors:
            add_ring(r.coords)
        for s in self.pl:
            (x0, y0), (x1, y1) = s.linia.coords[0], s.linia.coords[-1]
            if abs(x1 - x0) < 1e-6:
                xs.add(x0)
                ys.update([y0, y1])
            elif abs(y1 - y0) < 1e-6:
                ys.add(y0)
                xs.update([x0, x1])
        for s in self.pp:
            xs.add(s.xy[0])
            ys.add(s.xy[1])
        xs.update(linie[0])
        ys.update(linie[1])
        xs = sorted(v for v in xs if minx - 1e-9 <= v <= maxx + 1e-9)
        ys = sorted(v for v in ys if miny - 1e-9 <= v <= maxy + 1e-9)

        def dense(v):
            out = [v[0]]
            for a, b in zip(v[:-1], v[1:]):
                if b - a < 0.02:            # scalanie linii bardzo bliskich (< 2 cm)
                    continue
                n = max(int(math.ceil((b - a) / hmax - 1e-9)), 1)
                out += list(np.linspace(a, b, n + 1)[1:])
            return np.array(out)
        self.gx = dense(xs)
        self.gy = dense(ys)
        nx, ny = len(self.gx), len(self.gy)
        # elementy: środek wewnątrz obrysu
        els = []
        for j in range(ny - 1):
            for i in range(nx - 1):
                c = Point((self.gx[i] + self.gx[i + 1]) / 2, (self.gy[j] + self.gy[j + 1]) / 2)
                if self.obrys.contains(c):
                    els.append((i, j))
        if not els:
            raise BladDanych("MES płyty: brak elementów (obrys zbyt mały?)")
        used = sorted({(i + di, j + dj) for i, j in els for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1))})
        self.node_id = {ij: k for k, ij in enumerate(used)}
        self.nodes = np.array([(self.gx[i], self.gy[j]) for i, j in used])
        self.els = els
        self.el_nodes = np.array([[self.node_id[(i, j)], self.node_id[(i + 1, j)], self.node_id[(i + 1, j + 1)],
                                   self.node_id[(i, j + 1)]] for i, j in els])
        self.el_ab = np.array([(self.gx[i + 1] - self.gx[i], self.gy[j + 1] - self.gy[j]) for i, j in els])
        self.el_c = np.array([((self.gx[i] + self.gx[i + 1]) / 2, (self.gy[j] + self.gy[j + 1]) / 2) for i, j in els])
        self.el_x0 = np.array([(self.gx[i], self.gy[j]) for i, j in els])

    def _sztywnosc(self):
        n = len(self.nodes) * 3
        rows, cols, vals = [], [], []
        for e, (nds, (a, b)) in enumerate(zip(self.el_nodes, self.el_ab)):
            _, K, _ = _acm(round(a, 9), round(b, 9), self.nu)
            dof = np.array([[3 * k, 3 * k + 1, 3 * k + 2] for k in nds]).ravel()
            rr, cc = np.meshgrid(dof, dof, indexing="ij")
            rows.append(rr.ravel())
            cols.append(cc.ravel())
            vals.append((K * self.D_el[e]).ravel())
        self.K = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(n, n))

    def _warunki(self):
        """Węzły podparte: na liniach podpór (odcinki równoległe do osi — dokładnie; ukośne — najbliższe węzły)."""
        tol = 1e-6
        self.sup_nodes: dict[str, list[int]] = {}
        fixed = set()
        for s in self.pl:
            (x0, y0), (x1, y1) = s.linia.coords[0], s.linia.coords[-1]
            nd = []
            if abs(x1 - x0) < 1e-6 or abs(y1 - y0) < 1e-6:
                for k, (x, y) in enumerate(self.nodes):
                    if s.linia.distance(Point(x, y)) < tol + 1e-4:
                        nd.append(k)
            else:
                hmax = max(np.diff(self.gx).max(), np.diff(self.gy).max())
                for k, (x, y) in enumerate(self.nodes):
                    if s.linia.distance(Point(x, y)) <= 0.5 * hmax:
                        nd.append(k)
                self.uwagi.append(f"podpora {s.id} ukośna — przybliżona węzłami siatki [UPR]")
            self.sup_nodes[s.id] = nd
            for k in nd:
                fixed.add(3 * k)
                if s.typ == "utwierdzenie":
                    fixed.update([3 * k + 1, 3 * k + 2])
        for s in self.pp:
            k = int(np.argmin(np.hypot(self.nodes[:, 0] - s.xy[0], self.nodes[:, 1] - s.xy[1])))
            if math.hypot(*(self.nodes[k] - np.asarray(s.xy))) > 0.3:
                self.uwagi.append(f"podpora punktowa {s.id} poza płytą (odl. > 0,3 m) — pominięta")
                self.sup_nodes[s.id] = []
                continue
            self.sup_nodes[s.id] = [k]
            fixed.add(3 * k)
        if len(fixed) < 3:
            raise BladDanych("MES płyty: za mało podpór")
        self.fixed = np.array(sorted(fixed))
        n = self.K.shape[0]
        mask = np.ones(n, bool)
        mask[self.fixed] = False
        self.free = np.nonzero(mask)[0]
        Kff = self.K[self.free][:, self.free].tocsc()
        try:
            self._lu = spla.splu(Kff)
        except RuntimeError as e:  # macierz osobliwa — płyta zmienna geometrycznie
            raise BladDanych(f"MES płyty: układ zmienny geometrycznie ({e})") from e

    # ---------------- obciążenia ----------------
    def _element_zawierajacy(self, x, y) -> int | None:
        i = int(np.searchsorted(self.gx, x, side="right") - 1)
        j = int(np.searchsorted(self.gy, y, side="right") - 1)
        i = min(max(i, 0), len(self.gx) - 2)
        j = min(max(j, 0), len(self.gy) - 2)
        try:
            return self.els.index((i, j))
        except ValueError:
            return None

    def wektor(self, q_el: np.ndarray | float = 0.0, linie: list | None = None, punkty: list | None = None) -> np.ndarray:
        """Wektor obciążeń: q_el — obciążenie powierzchniowe na elementach [kPa] (skalar lub tablica n_el);
        linie — [(LineString, q [kN/m])]; punkty — [((x, y), P [kN])]."""
        n = len(self.nodes) * 3
        f = np.zeros(n)
        q_el = np.broadcast_to(np.asarray(q_el, float), (len(self.els),))
        for e, (nds, (a, b)) in enumerate(zip(self.el_nodes, self.el_ab)):
            if q_el[e] == 0:
                continue
            _, _, fq = _acm(round(a, 9), round(b, 9), self.nu)
            dof = np.array([[3 * k, 3 * k + 1, 3 * k + 2] for k in nds]).ravel()
            f[dof] += fq * q_el[e]
        pts = list(punkty or [])
        for ln, q in (linie or []):
            if q == 0 or ln.length == 0:
                continue
            hmin = min(np.diff(self.gx).min(), np.diff(self.gy).min())
            nseg = max(int(math.ceil(ln.length / (hmin / 4))), 1)
            ds = ln.length / nseg
            for k in range(nseg):
                p = ln.interpolate((k + 0.5) * ds)
                pts.append(((p.x, p.y), q * ds))
        for (x, y), P in pts:
            e = self._element_zawierajacy(x, y)
            if e is None:
                self.uwagi.append(f"obciążenie skupione ({x:.2f}, {y:.2f}) poza płytą — pominięte")
                continue
            a, b = self.el_ab[e]
            Ci, _, _ = _acm(round(a, 9), round(b, 9), self.nu)
            N = _P(x - self.el_x0[e][0], y - self.el_x0[e][1]) @ Ci
            dof = np.array([[3 * k, 3 * k + 1, 3 * k + 2] for k in self.el_nodes[e]]).ravel()
            f[dof] += N * P
        return f

    def rozwiaz(self, f: np.ndarray) -> WynikMES:
        u = np.zeros(len(f))
        u[self.free] = self._lu.solve(f[self.free])
        R = f - self.K @ u                                  # reakcje (w górę dodatnie) w węzłach podpartych
        Rn = np.zeros(len(self.nodes))
        Rn[self.fixed[self.fixed % 3 == 0] // 3] = R[self.fixed[self.fixed % 3 == 0]]
        m = np.zeros((len(self.els), 3))
        Dm0 = np.array([[1, self.nu, 0], [self.nu, 1, 0], [0, 0, (1 - self.nu) / 2]])
        for e, (nds, (a, b)) in enumerate(zip(self.el_nodes, self.el_ab)):
            Dm = self.D_el[e] * Dm0
            Ci, _, _ = _acm(round(a, 9), round(b, 9), self.nu)
            dof = np.array([[3 * k, 3 * k + 1, 3 * k + 2] for k in nds]).ravel()
            B = np.vstack([_Pxx(a / 2, b / 2), _Pyy(a / 2, b / 2), 2 * _Pxy(a / 2, b / 2)]) @ Ci
            kap = B @ u[dof]
            mm = -Dm @ kap
            m[e] = (mm[0], mm[1], mm[2])
        return WynikMES(u[0::3].copy(), m, Rn)

    # ---------------- wyniki pomocnicze ----------------
    def reakcja(self, wynik: WynikMES, pid: str) -> float:
        return float(wynik.R[self.sup_nodes.get(pid, [])].sum())

    def reakcje_liniowe(self, wynik: WynikMES, pid: str) -> tuple[np.ndarray, np.ndarray]:
        """Rozkład reakcji wzdłuż podpory liniowej: (s [m] od początku linii, r [kN/m])."""
        s_obj = next(s for s in self.pl if s.id == pid)
        nd = self.sup_nodes.get(pid, [])
        if not nd:
            return np.zeros(0), np.zeros(0)
        ss = np.array([s_obj.linia.project(Point(*self.nodes[k])) for k in nd])
        o = np.argsort(ss)
        ss = ss[o]
        R = wynik.R[np.asarray(nd)[o]]
        # szerokość zbierania każdego węzła
        bnd = np.concatenate([[ss[0]], (ss[:-1] + ss[1:]) / 2, [ss[-1]]])
        wdt = np.diff(bnd)
        wdt[wdt <= 1e-9] = np.nan
        return ss, R / wdt

    def elementy_w(self, g) -> np.ndarray:
        """Maska elementów, których środek leży w geometrii g."""
        return np.array([g.buffer(1e-9).contains(Point(*c)) for c in self.el_c])
