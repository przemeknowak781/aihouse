"""MES płaskiego stanu naprężenia dla ścian-tarcz żelbetowych (belki-ściany, tarcze wspornikowe, tarcze z otworami).

Element: **prostokątny czterowęzłowy z modami niekonforemnymi QM6** (Wilson, Taylor, Doherty, Ghaboussi 1973; Taylor,
Beresford, Wilson 1976): przemieszczenia biliniowe + 4 wewnętrzne mody (1 − ξ²), (1 − η²) dla u i v, eliminowane
kondensacją statyczną na poziomie elementu. Uzasadnienie wyboru (zamiast CST / Q4 / Q8):

* CST (stałe odkształcenie) — w strefach zginania (pasy tarczy, nadproża nad otworami) wymaga bardzo gęstej siatki,
  naprężenia stałe w elemencie dają „schodkowe” mapy i zawyżoną sztywność;
* Q4 (biliniowy) — pasożytnicze ścinanie (shear locking) przy zginaniu: dla wspornika l/h = 10 i jednego elementu na
  wysokości ugięcie zaniżone o ~ 70 %;
* Q8 (serendipity) — dokładny, ale węzły środkowe komplikują podpory sprężyste, obciążenia i wyprowadzanie wyników;
* **QM6 na siatce prostokątnej** odtwarza **dokładnie czyste zginanie** (test łatki spełniony dla prostokątów i
  równoległoboków), ma 2 st. swobody na węzeł, a naprężenia w środku elementu są superzbieżne. Obrys ścian i otwory
  są prostokątne (siatka ortogonalna dopasowana do wszystkich krawędzi, podpór i punktów przyłożenia obciążeń) — obrys
  nieprostokątny (np. skos) jest aproksymowany schodkowo (element należy do tarczy, gdy jego środek leży w obrysie)
  z ostrzeżeniem [UPR].

Wektor obciążeń dla modów niekonforemnych pomijany (praktyka QM6 — zachowanie testu łatki). Całki 2×2 Gaussa są
dokładne dla prostokątów. Naprężenia wzdłuż przekroju pionowego/poziomego elementu są liniowe → całkowanie wypadkowych
(N, V, M, wypadkowa części rozciąganej i jej środek) jest dokładne w obrębie elementu.

Podpory: liniowe/punktowe, sztywne lub sprężyste (moduł podłoża k [kN/m²] dla linii = E·t/h ściany poniżej; [kN/m]
dla punktu), opcjonalnie tylko na docisk (iteracja zbioru aktywnego — reakcje rozciągające odłączane). Poziomo tarcza
jest zablokowana w jednym węźle (tarcza stropowa) lub wzdłuż podpór z ``kx=True``.

Stan zarysowany (SLS): ortotropowa macierz sprężystości elementu wg koncepcji rys rozmytych („smeared rotating crack”)
— beton bez sztywności w kierunku głównego rozciągania, zbrojenie rozmyte ρ_x·E_s, ρ_y·E_s, sztywność ścinania
β_G·G; interpolacja podatności między stanem I i II współczynnikiem ζ = 1 − β·(f_ctm/σ₁)² (analogicznie do
PN-EN 1992-1-1 (7.18)–(7.19)) [UPR].

Jednostki: długości [m], siły [kN], naprężenia i moduły [kPa] (= kN/m²; w raportach MPa), grubość t [m].
Oś x — wzdłuż ściany (s modelu), oś z — pionowo w górę. Obciążenia pionowe dodatnie w dół, reakcje dodatnie w górę.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import shapely
from shapely.geometry import LineString, Point, Polygon

from .wspolne import BladDanych

_GP = np.array([-1.0, 1.0]) / math.sqrt(3.0)
_XI_N = np.array([-1.0, 1.0, 1.0, -1.0])     # węzły: (x0,z0), (x1,z0), (x1,z1), (x0,z1)
_ETA_N = np.array([-1.0, -1.0, 1.0, 1.0])


# ==================================================================================================
# Dane wejściowe
# ==================================================================================================
@dataclass
class PodporaT:
    """Podpora tarczy na poziomie z, na odcinku s0…s1 (s0 == s1 — punktowa). k — sztywność sprężyny: [kN/m²]
    (na 1 m linii) dla podpory liniowej, [kN/m] dla punktowej; None — podpora sztywna. kx — blokada przesuwu poziomego;
    tylko_docisk — podpora jednostronna (reakcje rozciągające odłączane iteracyjnie)."""
    id: str
    s0: float
    s1: float
    z: float = 0.0
    k: float | None = None
    kx: bool = False
    tylko_docisk: bool = True
    opis: str = ""
    sciana: str = ""            # id ściany/elementu poniżej (bilans ścieżki obciążeń)
    z1: float | None = None     # podpora pionowa (utwierdzenie w ścianie poprzecznej): x = s0, z…z1 (u_z; u_x gdy kx)

    @property
    def dl(self) -> float:
        return max(self.s1 - self.s0, 0.0)

    @property
    def pionowa(self) -> bool:
        return self.z1 is not None


@dataclass
class ObcLiniowe:
    """Obciążenie liniowe pionowe q [kN/m] (dodatnie w dół) na poziomie z, odcinek s0…s1 (liniowo q0 → q1)."""
    przypadek: str
    s0: float
    s1: float
    z: float
    q0: float
    q1: float | None = None
    opis: str = ""

    def q(self, s):
        q1 = self.q0 if self.q1 is None else self.q1
        L = max(self.s1 - self.s0, 1e-12)
        return self.q0 + (q1 - self.q0) * (np.asarray(s) - self.s0) / L

    @property
    def wypadkowa(self) -> float:
        q1 = self.q0 if self.q1 is None else self.q1
        return 0.5 * (self.q0 + q1) * (self.s1 - self.s0)


@dataclass
class ObcProfil:
    """Obciążenie liniowe pionowe o dowolnym rozkładzie q(s) [kN/m] (dodatnie w dół) na poziomie z — punkty (s, q)
    z interpolacją liniową (np. profil reakcji płyty z MES płytowego); nie zagęszcza siatki w kierunku x."""
    przypadek: str
    s: np.ndarray
    q: np.ndarray
    z: float
    opis: str = ""

    def __post_init__(self):
        self.s = np.asarray(self.s, float)
        self.q = np.asarray(self.q, float)
        o = np.argsort(self.s)
        self.s, self.q = self.s[o], self.q[o]

    @property
    def s0(self) -> float:
        return float(self.s[0])

    @property
    def s1(self) -> float:
        return float(self.s[-1])

    def qf(self, x):
        return np.interp(x, self.s, self.q, left=0.0, right=0.0)

    @property
    def wypadkowa(self) -> float:
        return float(np.trapezoid(self.q, self.s))


@dataclass
class ObcSkupione:
    """Siła skupiona P [kN] (dodatnia w dół) i pozioma Px [kN] (dodatnia w +x) w punkcie (s, z)."""
    przypadek: str
    s: float
    z: float
    P: float
    Px: float = 0.0
    opis: str = ""
    dl_docisku: float = 0.20     # długość strefy docisku [m] (sprawdzenie węzła STM)


@dataclass
class WynikT:
    """Wynik MES tarczy dla jednej kombinacji: u [2n] (m), naprężenia w środkach elementów sig [ne × 3] (σ_x, σ_z, τ)
    [kPa], alfa — mody wewnętrzne [ne × 4], R — reakcje węzłowe [2n] (kN, dodatnie w +x / w górę)."""
    u: np.ndarray
    sig: np.ndarray
    alfa: np.ndarray
    R: np.ndarray
    f: np.ndarray
    opis: str = ""
    odlaczone: list = field(default_factory=list)   # węzły podpór jednostronnych odłączone (odrywanie)
    iteracje: int = 1
    D_el: np.ndarray | None = None
    aktywne: dict | None = field(default=None, repr=False)
    _nar: np.ndarray | None = field(default=None, repr=False)

    @property
    def ux(self) -> np.ndarray:
        return self.u[0::2]

    @property
    def uz(self) -> np.ndarray:
        return self.u[1::2]


def glowne(sig: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Naprężenia główne: (σ₁ ≥ σ₂, kąt θ kierunku σ₁ od osi x [rad]) dla tablicy [n × 3] (σ_x, σ_z, τ)."""
    sx, sz, t = sig[..., 0], sig[..., 1], sig[..., 2]
    c = 0.5 * (sx + sz)
    r = np.sqrt((0.5 * (sx - sz)) ** 2 + t ** 2)
    th = 0.5 * np.arctan2(2 * t, sx - sz)
    return c + r, c - r, th


def D_izo(E: float, nu: float) -> np.ndarray:
    """Macierz sprężystości płaskiego stanu naprężenia (E w kPa)."""
    return E / (1 - nu * nu) * np.array([[1.0, nu, 0.0], [nu, 1.0, 0.0], [0.0, 0.0, (1 - nu) / 2]])


def _T_rot(th):
    """Macierz transformacji odkształceń (inżynierskich) z układu globalnego do obróconego o θ (tablica kątów)."""
    c, s = np.cos(th), np.sin(th)
    T = np.zeros(np.shape(th) + (3, 3))
    T[..., 0, 0], T[..., 0, 1], T[..., 0, 2] = c * c, s * s, c * s
    T[..., 1, 0], T[..., 1, 1], T[..., 1, 2] = s * s, c * c, -c * s
    T[..., 2, 0], T[..., 2, 1], T[..., 2, 2] = -2 * c * s, 2 * c * s, c * c - s * s
    return T


def D_zarysowany(E_c: float, nu: float, th: np.ndarray, rho_x: np.ndarray, rho_z: np.ndarray, E_s: float, zeta: np.ndarray,
                 beta_G: float = 0.2) -> np.ndarray:
    """Efektywna macierz sprężystości elementów zarysowanych (rysy rozmyte, obrotowe) z usztywnieniem przez beton
    między rysami: C_eff = (1 − ζ)·C_I + ζ·C_II (interpolacja podatności — analogia (7.18)). Stan I: beton izotropowy +
    zbrojenie rozmyte; stan II: beton w osiach głównych diag(0, E_c, β_G·G) + zbrojenie rozmyte diag(ρ_x·E_s, ρ_z·E_s, 0)."""
    n = len(th)
    DI = D_izo(E_c, nu)
    G = E_c / (2 * (1 + nu))
    Dl = np.zeros((n, 3, 3))
    Dl[:, 1, 1] = E_c
    Dl[:, 2, 2] = beta_G * G
    T = _T_rot(th)
    DII = np.einsum("nji,njk,nkl->nil", T, Dl, T)
    DII[:, 0, 0] += rho_x * E_s
    DII[:, 1, 1] += rho_z * E_s
    DIs = np.repeat(DI[None], n, axis=0)
    DIs[:, 0, 0] += rho_x * E_s
    DIs[:, 1, 1] += rho_z * E_s
    CI = np.linalg.inv(DIs)
    CII = np.linalg.inv(DII + np.eye(3) * 1e-9 * E_c)
    Ceff = (1 - zeta)[:, None, None] * CI + zeta[:, None, None] * CII
    return np.linalg.inv(Ceff)


# ==================================================================================================
# Element QM6 (prostokąt a × b)
# ==================================================================================================
def _B_prostokat(a: float, b: float, xi: float, eta: float) -> np.ndarray:
    """Macierz B [3 × 12] (8 st. swobody węzłowych + 4 mody wewnętrzne) w punkcie (ξ, η) prostokąta a × b."""
    dNdx = _XI_N * (1 + _ETA_N * eta) / 4 * (2 / a)
    dNdz = _ETA_N * (1 + _XI_N * xi) / 4 * (2 / b)
    B = np.zeros((3, 12))
    B[0, 0:8:2] = dNdx
    B[1, 1:8:2] = dNdz
    B[2, 0:8:2] = dNdz
    B[2, 1:8:2] = dNdx
    # mody: α1·(1−ξ²) i α2·(1−η²) dla u; α3·(1−ξ²) i α4·(1−η²) dla v
    B[0, 8] = -4 * xi / a
    B[2, 9] = -4 * eta / b
    B[2, 10] = -4 * xi / a
    B[1, 11] = -4 * eta / b
    return B


class TarczaMES:
    """Tarcza w płaskim stanie naprężenia na siatce prostokątnej elementów QM6.

    obrys — wielobok ściany w układzie (x = s wzdłuż ściany, z — rzędna) z otworami (interiors); t — grubość [m];
    E — moduł [kPa]; gamma — ciężar objętościowy [kN/m³]; g_dod — dodatkowy ciężar warstw na 1 m² lica [kN/m²];
    podpory / obciazenia — listy :class:`PodporaT`, :class:`ObcLiniowe`, :class:`ObcSkupione`; siatka — maks. bok
    elementu [m]; strefy — [(Polygon, t, E)] strefy o innej grubości (np. półka płyty) lub module; przypadek_cw — nazwa
    przypadku ciężaru własnego ("G")."""

    def __init__(self, obrys: Polygon, t: float, E: float, nu: float = 0.2, gamma: float = 25.0, g_dod: float = 0.0,
                 podpory: list[PodporaT] | None = None, obciazenia: list | None = None, siatka: float = 0.10,
                 strefy: list | None = None, linie: tuple = ((), ()), przypadek_cw: str = "G"):
        if not isinstance(obrys, Polygon) or obrys.is_empty or obrys.area <= 0:
            raise BladDanych("MES tarczy: obrys musi być niepustym wielobokiem")
        self.obrys = obrys
        self.t = float(t)
        self.E = float(E)
        self.nu = float(nu)
        self.gamma = float(gamma)
        self.g_dod = float(g_dod)
        self.podpory = list(podpory or [])
        self.obciazenia = list(obciazenia or [])
        self.h = float(siatka)
        self.przypadek_cw = przypadek_cw
        self.uwagi: list[str] = []
        if not self.podpory:
            raise BladDanych("MES tarczy: brak podpór")
        self._siatka(linie)
        self.t_el = np.full(self.ne, self.t)
        self.E_el = np.full(self.ne, self.E)
        for g, tt, EE in (strefy or []):
            msk = shapely.contains_xy(g.buffer(1e-9), self.el_c[:, 0], self.el_c[:, 1])
            self.t_el[msk] = tt
            if EE is not None:
                self.E_el[msk] = EE
        self._B_cache: dict = {}
        self._rozmiary()
        self._podpory_wezly()
        self.K0 = self.sztywnosc()
        self._Rm_iso, self._D_iso = self._Rm, self._D_akt
        self._lu_cache: dict = {}

    # ---------------------------------------------------------------------------------------------
    # Siatka
    # ---------------------------------------------------------------------------------------------
    def _siatka(self, linie):
        P = self.obrys
        xs, zs = set(), set()
        for ring in [P.exterior] + list(P.interiors):
            for x, z in ring.coords:
                xs.add(round(x, 6))
                zs.add(round(z, 6))
        for s in self.podpory:
            xs.update([round(s.s0, 6), round(s.s1, 6)])
            zs.add(round(s.z, 6))
            if s.z1 is not None:
                zs.add(round(s.z1, 6))
        for o in self.obciazenia:
            if isinstance(o, ObcLiniowe):
                xs.update([round(o.s0, 6), round(o.s1, 6)])
                zs.add(round(o.z, 6))
            elif isinstance(o, ObcProfil):
                zs.add(round(o.z, 6))
            elif isinstance(o, ObcSkupione):
                xs.add(round(o.s, 6))
                zs.add(round(o.z, 6))
        xs.update(round(v, 6) for v in linie[0])
        zs.update(round(v, 6) for v in linie[1])
        x0, z0, x1, z1 = P.bounds
        xs = sorted(v for v in xs if x0 - 1e-9 <= v <= x1 + 1e-9)
        zs = sorted(v for v in zs if z0 - 1e-9 <= v <= z1 + 1e-9)

        def dense(v):
            v2 = [v[0]]
            for a in v[1:]:
                if a - v2[-1] > 0.004:
                    v2.append(a)
            v2[-1] = v[-1]
            out = [v2[0]]
            for a, b in zip(v2[:-1], v2[1:]):
                n = max(int(math.ceil((b - a) / self.h - 1e-9)), 1)
                out += list(np.linspace(a, b, n + 1)[1:])
            return np.array(out)
        self.gx, self.gz = dense(xs), dense(zs)
        nx, nz = len(self.gx), len(self.gz)
        cx = 0.5 * (self.gx[:-1] + self.gx[1:])
        cz = 0.5 * (self.gz[:-1] + self.gz[1:])
        CX, CZ = np.meshgrid(cx, cz)
        inside = shapely.contains_xy(P, CX.ravel(), CZ.ravel()).reshape(CX.shape)
        jj, ii = np.nonzero(inside)
        if len(ii) == 0:
            raise BladDanych("MES tarczy: brak elementów (obrys zbyt mały?)")
        self.el_ij = np.stack([ii, jj], axis=1)
        used = np.zeros((nz, nx), bool)
        for di, dj in ((0, 0), (1, 0), (1, 1), (0, 1)):
            used[jj + dj, ii + di] = True
        nid = -np.ones((nz, nx), int)
        uj, ui = np.nonzero(used)
        nid[uj, ui] = np.arange(len(ui))
        self.node_grid = nid
        self.nodes = np.stack([self.gx[ui], self.gz[uj]], axis=1)
        self.nn = len(self.nodes)
        self.els = np.stack([nid[jj, ii], nid[jj, ii + 1], nid[jj + 1, ii + 1], nid[jj + 1, ii]], axis=1)
        self.ne = len(self.els)
        self.el_x0 = np.stack([self.gx[ii], self.gz[jj]], axis=1)
        self.el_ab = np.stack([self.gx[ii + 1] - self.gx[ii], self.gz[jj + 1] - self.gz[jj]], axis=1)
        self.el_c = self.el_x0 + self.el_ab / 2
        self.el_grid = -np.ones((nz - 1, nx - 1), int)
        self.el_grid[jj, ii] = np.arange(self.ne)
        A_mes = float((self.el_ab[:, 0] * self.el_ab[:, 1]).sum())
        if abs(A_mes - P.area) > 0.005 * P.area:
            self.uwagi.append(f"Obrys nieprostokątny aproksymowany schodkowo: pole siatki {A_mes:.3f} m² vs obrys {P.area:.3f} m² [UPR]")
        self.dof = np.stack([2 * self.els, 2 * self.els + 1], axis=2).reshape(self.ne, 8)

    def _rozmiary(self):
        """Grupy elementów o jednakowych wymiarach (a, b) — macierze B w punktach Gaussa liczone raz."""
        key = np.round(self.el_ab, 7)
        uniq, inv = np.unique(key, axis=0, return_inverse=True)
        self.el_typ = inv.ravel()
        self.typy_ab = uniq
        self.B_gp = np.zeros((len(uniq), 4, 3, 12))
        self.B_c0 = np.zeros((len(uniq), 3, 12))
        for k, (a, b) in enumerate(uniq):
            g = 0
            for eta in _GP:
                for xi in _GP:
                    self.B_gp[k, g] = _B_prostokat(a, b, xi, eta)
                    g += 1
            self.B_c0[k] = _B_prostokat(a, b, 0.0, 0.0)

    def D_domyslne(self, E_el: np.ndarray | None = None) -> np.ndarray:
        E_el = self.E_el if E_el is None else E_el
        return E_el[:, None, None] * D_izo(1.0, self.nu)[None]

    def sztywnosc(self, D_el: np.ndarray | None = None) -> sp.csr_matrix:
        """Macierz sztywności (bez podpór); D_el — [ne × 3 × 3] (domyślnie izotropowa E_el, ν)."""
        D = self.D_domyslne() if D_el is None else D_el
        detJ = self.el_ab[:, 0] * self.el_ab[:, 1] / 4
        Bg = self.B_gp[self.el_typ]                                  # ne × 4 × 3 × 12
        Kf = np.einsum("egki,ekl,eglj->eij", Bg, D, Bg) * (self.t_el * detJ)[:, None, None]
        Kcc, Kci, Kii = Kf[:, :8, :8], Kf[:, :8, 8:], Kf[:, 8:, 8:]
        Rm = np.linalg.solve(Kii, np.transpose(Kci, (0, 2, 1)))    # ne × 4 × 8  (K_ii⁻¹·K_ic)
        Ke = Kcc - np.einsum("eij,ejk->eik", Kci, Rm)
        self._Rm = Rm
        self._D_akt = D
        rows = np.repeat(self.dof, 8, axis=1).ravel()
        cols = np.tile(self.dof, (1, 8)).ravel()
        n = 2 * self.nn
        K = sp.csr_matrix((Ke.ravel(), (rows, cols)), shape=(n, n))
        return K

    # ---------------------------------------------------------------------------------------------
    # Podpory
    # ---------------------------------------------------------------------------------------------
    def _wezly_na_linii(self, z: float, s0: float, s1: float) -> np.ndarray:
        tol = 1e-6
        m = (np.abs(self.nodes[:, 1] - z) < tol) & (self.nodes[:, 0] >= s0 - tol) & (self.nodes[:, 0] <= s1 + tol)
        return np.nonzero(m)[0]

    def _podpory_wezly(self):
        self.pod_wezly: dict[str, np.ndarray] = {}
        self.pod_k: dict[str, np.ndarray] = {}        # sztywność sprężyn węzłowych (None → sztywna)
        self.pod_trib: dict[str, np.ndarray] = {}
        for s in self.podpory:
            if s.z1 is not None:
                tol = 1e-6
                nd = np.nonzero((np.abs(self.nodes[:, 0] - s.s0) < tol) & (self.nodes[:, 1] >= min(s.z, s.z1) - tol)
                                & (self.nodes[:, 1] <= max(s.z, s.z1) + tol))[0]
                if len(nd) < 2:
                    raise BladDanych(f"MES tarczy: podpora pionowa {s.id} nie leży na krawędzi tarczy")
                nd = nd[np.argsort(self.nodes[nd, 1])]
                zz = self.nodes[nd, 1]
                bnd = np.concatenate([[zz[0]], 0.5 * (zz[:-1] + zz[1:]), [zz[-1]]])
                self.pod_wezly[s.id] = nd
                self.pod_trib[s.id] = np.diff(bnd)
                self.pod_k[s.id] = None if s.k is None else s.k * np.diff(bnd)
                continue
            if s.s1 - s.s0 < 1e-9:
                d = np.hypot(self.nodes[:, 0] - s.s0, self.nodes[:, 1] - s.z)
                k = int(np.argmin(d))
                if d[k] > 0.05:
                    raise BladDanych(f"MES tarczy: podpora punktowa {s.id} poza tarczą")
                nd = np.array([k])
                trib = np.array([1.0])
            else:
                nd = self._wezly_na_linii(s.z, s.s0, s.s1)
                if len(nd) < 2:
                    raise BladDanych(f"MES tarczy: podpora {s.id} ({s.s0:.2f}…{s.s1:.2f} m, z = {s.z:.2f}) nie leży na krawędzi tarczy")
                nd = nd[np.argsort(self.nodes[nd, 0])]
                x = self.nodes[nd, 0]
                bnd = np.concatenate([[x[0]], 0.5 * (x[:-1] + x[1:]), [x[-1]]])
                trib = np.diff(bnd)
            self.pod_wezly[s.id] = nd
            self.pod_trib[s.id] = trib
            self.pod_k[s.id] = None if s.k is None else (s.k * trib if s.s1 - s.s0 >= 1e-9 else np.array([s.k]))
        if not any(s.kx for s in self.podpory):
            # blokada przesuwu poziomego w jednym węźle (tarcza stropowa) — środek najdłuższej podpory
            s = max(self.podpory, key=lambda q: q.dl)
            nd = self.pod_wezly[s.id]
            self.kx_wezly = np.array([nd[len(nd) // 2]])
        else:
            self.kx_wezly = np.concatenate([self.pod_wezly[s.id] for s in self.podpory if s.kx])

    # ---------------------------------------------------------------------------------------------
    # Obciążenia
    # ---------------------------------------------------------------------------------------------
    def przypadki(self) -> list[str]:
        out = [self.przypadek_cw]
        for o in self.obciazenia:
            if o.przypadek not in out:
                out.append(o.przypadek)
        return out

    def _krawedzie_linii(self, z: float) -> np.ndarray:
        """Maska odcinków siatki na linii z (między gx[i], gx[i+1]), które są krawędzią istniejącego elementu."""
        j = int(np.argmin(np.abs(self.gz - z)))
        if abs(self.gz[j] - z) > 1e-6:
            return np.zeros(len(self.gx) - 1, bool)
        m = np.zeros(len(self.gx) - 1, bool)
        if j < len(self.gz) - 1:
            m |= self.el_grid[j] >= 0
        if j > 0:
            m |= self.el_grid[j - 1] >= 0
        return m

    def wektor(self, wsp: dict[str, float]) -> np.ndarray:
        """Wektor obciążeń kombinacji {przypadek: współczynnik} (ciężar własny — przypadek ``przypadek_cw``)."""
        f = np.zeros(2 * self.nn)
        a_cw = wsp.get(self.przypadek_cw, 0.0)
        if a_cw:
            W = (self.gamma * self.t_el + self.g_dod) * self.el_ab[:, 0] * self.el_ab[:, 1] * a_cw
            np.add.at(f, 2 * self.els + 1, -(W / 4)[:, None] * np.ones((1, 4)))
        for o in self.obciazenia:
            a = wsp.get(o.przypadek, 0.0)
            if not a:
                continue
            if isinstance(o, ObcSkupione):
                d = np.hypot(self.nodes[:, 0] - o.s, self.nodes[:, 1] - o.z)
                k = int(np.argmin(d))
                if d[k] > 1e-4:
                    raise BladDanych(f"MES tarczy: siła skupiona ({o.s:.2f}, {o.z:.2f}) poza tarczą")
                f[2 * k + 1] -= a * o.P
                f[2 * k] += a * o.Px
            else:
                self._linia_do_wektora(f, o, a)
        return f

    def _linia_do_wektora(self, f: np.ndarray, o, a: float):
        qfun = o.qf if isinstance(o, ObcProfil) else o.q
        edg = self._krawedzie_linii(o.z)
        j = int(np.argmin(np.abs(self.gz - o.z)))
        gxs = self.gx
        braki = []   # (s0, s1) odcinków bez tarczy (otwory)
        for i in range(len(gxs) - 1):
            xa, xb = max(gxs[i], o.s0), min(gxs[i + 1], o.s1)
            if xb - xa < 1e-9:
                continue
            if not edg[i]:
                braki.append((xa, xb))
                continue
            na, nb = self.node_grid[j, i], self.node_grid[j, i + 1]
            L = gxs[i + 1] - gxs[i]
            ngp = _GP if not isinstance(o, ObcProfil) else np.array([-0.8, -0.4, 0.0, 0.4, 0.8])   # reguła punktów środkowych
            wgp = 1.0 if not isinstance(o, ObcProfil) else 2.0 / len(ngp)
            for gp in ngp:
                x = 0.5 * (xa + xb) + 0.5 * (xb - xa) * gp
                q = float(qfun(x)) * a * 0.5 * (xb - xa) * wgp
                Na = (gxs[i + 1] - x) / L
                f[2 * na + 1] -= q * Na
                f[2 * nb + 1] -= q * (1 - Na)
        if braki:
            # obciążenie nad otworem → na krawędzie otworu (zachowanie wypadkowej i momentu) [UPR]
            grp = []
            for s0, s1 in braki:
                if grp and abs(grp[-1][1] - s0) < 1e-9:
                    grp[-1][1] = s1
                else:
                    grp.append([s0, s1])
            for s0, s1 in grp:
                xs_ = np.linspace(s0, s1, 41)
                qq = qfun(xs_) * a
                R = float(np.trapezoid(qq, xs_))
                if abs(R) < 1e-12:
                    continue
                xR = float(np.trapezoid(qq * xs_, xs_)) / R
                on = np.nonzero(np.abs(self.nodes[:, 1] - o.z) < 1e-6)[0]
                if len(on) == 0:
                    on = np.arange(self.nn)
                ka = on[np.argmin(np.abs(self.nodes[on, 0] - s0) + 10 * np.abs(self.nodes[on, 1] - o.z))]
                kb = on[np.argmin(np.abs(self.nodes[on, 0] - s1) + 10 * np.abs(self.nodes[on, 1] - o.z))]
                xa, xb = self.nodes[ka, 0], self.nodes[kb, 0]
                if abs(xb - xa) < 1e-9:
                    f[2 * ka + 1] -= R
                else:
                    f[2 * ka + 1] -= R * (xb - xR) / (xb - xa)
                    f[2 * kb + 1] -= R * (xR - xa) / (xb - xa)
                msg = (f"Obciążenie „{o.opis or o.przypadek}” na odcinku {s0:.2f}…{s1:.2f} m (z = {o.z:.2f}) nie trafia w tarczę "
                       "(otwór) — przeniesione na krawędzie otworu [UPR]")
                if msg not in self.uwagi:
                    self.uwagi.append(msg)

    # ---------------------------------------------------------------------------------------------
    # Rozwiązanie
    # ---------------------------------------------------------------------------------------------
    def _uklad(self, K0, aktywne: dict):
        """(K z podporami, maska stopni swobody wolnych) dla zbioru aktywnych węzłów podpór."""
        n = 2 * self.nn
        fixed = np.zeros(n, bool)
        fixed[2 * self.kx_wezly] = True
        kdiag = np.zeros(n)
        for s in self.podpory:
            nd = self.pod_wezly[s.id]
            akt = aktywne[s.id]
            if self.pod_k[s.id] is None:
                fixed[2 * nd[akt] + 1] = True
            else:
                np.add.at(kdiag, 2 * nd[akt] + 1, self.pod_k[s.id][akt])
        K = K0 + sp.diags(kdiag)
        return K.tocsc(), ~fixed

    def rozwiaz(self, f: np.ndarray, D_el: np.ndarray | None = None, opis: str = "", maks_iter: int = 40,
                aktywne: dict | None = None) -> WynikT:
        """Rozwiązanie K·u = f (kombinacja); podpory jednostronne — iteracja zbioru aktywnego. ``aktywne`` — ustalony
        zbiór węzłów w kontakcie {id podpory: maska} (rozwiązanie liniowe, np. przypadki do superpozycji)."""
        if D_el is None:
            K0 = self.K0
            Rm, D = self._Rm_iso, self._D_iso
            key0 = "iso"
        else:
            K0 = self.sztywnosc(D_el)
            Rm, D = self._Rm, D_el
            key0 = None
        staly = aktywne is not None
        aktywne = ({k: v.copy() for k, v in aktywne.items()} if staly
                   else {s.id: np.ones(len(self.pod_wezly[s.id]), bool) for s in self.podpory})
        odl = []
        it = 0
        while True:
            it += 1
            key = (key0, tuple((k, v.tobytes()) for k, v in sorted(aktywne.items()))) if key0 else None
            if key is not None and key in self._lu_cache:
                lu, free = self._lu_cache[key]
            else:
                K, free = self._uklad(K0, aktywne)
                Kff = K[free][:, free]
                try:
                    lu = spla.splu(Kff.tocsc())
                except RuntimeError as e:
                    raise BladDanych(f"MES tarczy: układ zmienny geometrycznie ({e})") from e
                if key is not None:
                    if len(self._lu_cache) > 24:
                        self._lu_cache.clear()
                    self._lu_cache[key] = (lu, free)
            u = np.zeros_like(f)
            u[free] = lu.solve(f[free])
            R = K0 @ u - f
            zmiana = False
            for s in self.podpory:
                if not s.tylko_docisk or s.z1 is not None or staly:
                    continue
                nd = self.pod_wezly[s.id]
                akt = aktywne[s.id]
                Rz = R[2 * nd + 1]
                uz = u[2 * nd + 1]
                odrywane = akt & (Rz < -1e-6)
                docisk = (~akt) & (uz < -1e-9)
                if odrywane.any():
                    # odłączany węzeł o największym rozciąganiu (stabilna zbieżność) + wszystkie z R < 25 % maks.
                    rmin = Rz[odrywane].min()
                    sel = odrywane & (Rz <= 0.25 * rmin)
                    akt[sel] = False
                    zmiana = True
                if docisk.any():
                    akt[docisk] = True
                    zmiana = True
                if akt.sum() == 0:
                    raise BladDanych(f"MES tarczy: podpora {s.id} całkowicie oderwana — tarcza niestateczna (EQU)")
            if not zmiana or it >= maks_iter:
                break
        for s in self.podpory:
            nd = self.pod_wezly[s.id]
            odl += [int(k) for k in nd[~aktywne[s.id]]]
        ue = u[self.dof]
        alfa = -np.einsum("eij,ej->ei", Rm, ue)
        B0 = self.B_c0[self.el_typ]
        eps = np.einsum("eij,ej->ei", B0[:, :, :8], ue)
        sig = np.einsum("eij,ej->ei", D, eps)
        if it >= maks_iter:
            self.uwagi.append("Iteracja podpór jednostronnych nie zbiegła się w limicie iteracji — wynik przybliżony")
        return WynikT(u, sig, alfa, R, f, opis, odl, it, D if D_el is not None else None, aktywne)

    def rozwiaz_kombinacje(self, wsp: dict[str, float], opis: str = "", D_el=None) -> WynikT:
        return self.rozwiaz(self.wektor(wsp), D_el=D_el, opis=opis)

    # ---------------------------------------------------------------------------------------------
    # Wyniki
    # ---------------------------------------------------------------------------------------------
    def naprezenia_pkt(self, wyn: WynikT, e: int, xi, eta) -> np.ndarray:
        """σ (σ_x, σ_z, τ) [kPa] w punkcie (ξ, η) elementu e (z modami wewnętrznymi)."""
        a, b = self.el_ab[e]
        B = _B_prostokat(a, b, xi, eta)
        ue = np.concatenate([wyn.u[self.dof[e]], wyn.alfa[e]])
        D = wyn.D_el[e] if wyn.D_el is not None else self.E_el[e] * D_izo(1.0, self.nu)
        return D @ (B @ ue)

    def element_w(self, x: float, z: float) -> int | None:
        i = int(np.searchsorted(self.gx, x, side="right") - 1)
        j = int(np.searchsorted(self.gz, z, side="right") - 1)
        i = min(max(i, 0), len(self.gx) - 2)
        j = min(max(j, 0), len(self.gz) - 2)
        e = int(self.el_grid[j, i])
        return e if e >= 0 else None

    def naprezenia_xy(self, wyn: WynikT, x: float, z: float) -> np.ndarray | None:
        e = self.element_w(x, z)
        if e is None:
            return None
        a, b = self.el_ab[e]
        xi = 2 * (x - self.el_x0[e, 0]) / a - 1
        eta = 2 * (z - self.el_x0[e, 1]) / b - 1
        return self.naprezenia_pkt(wyn, e, xi, eta)

    def przemieszczenie(self, wyn: WynikT, x: float, z: float) -> tuple[float, float]:
        """(u_x, u_z) [m] w punkcie (interpolacja biliniowa w elemencie; bez modów wewnętrznych na brzegu)."""
        e = self.element_w(x, z)
        if e is None:
            d = np.hypot(self.nodes[:, 0] - x, self.nodes[:, 1] - z)
            k = int(np.argmin(d))
            return float(wyn.u[2 * k]), float(wyn.u[2 * k + 1])
        a, b = self.el_ab[e]
        xi = 2 * (x - self.el_x0[e, 0]) / a - 1
        eta = 2 * (z - self.el_x0[e, 1]) / b - 1
        N = (1 + _XI_N * xi) * (1 + _ETA_N * eta) / 4
        ue = wyn.u[self.dof[e]]
        return float(N @ ue[0::2]), float(N @ ue[1::2])

    def wartosci_wezlowe(self, val_el: np.ndarray) -> np.ndarray:
        """Uśrednienie wartości elementowych (środki) do węzłów (mapy wygładzone)."""
        s = np.zeros(self.nn)
        c = np.zeros(self.nn)
        for k in range(4):
            np.add.at(s, self.els[:, k], val_el)
            np.add.at(c, self.els[:, k], 1.0)
        return s / np.maximum(c, 1)

    def reakcje(self, wyn: WynikT) -> dict[str, dict]:
        """Reakcje podpór: {id: {"R": ΣR_z [kN], "Rx": ΣR_x, "x": s węzłów, "r": rozkład [kN/m] (linia) , "xR": środek}}."""
        out = {}
        for s in self.podpory:
            nd = self.pod_wezly[s.id]
            Rz = wyn.R[2 * nd + 1]
            Rx = wyn.R[2 * nd]
            x = self.nodes[nd, 0]
            tot = float(Rz.sum())
            xR = float((Rz * x).sum() / tot) if abs(tot) > 1e-9 else float(x.mean())
            r = Rz / self.pod_trib[s.id] if len(nd) > 1 else Rz
            out[s.id] = {"R": tot, "Rx": float(Rx.sum()), "x": x, "Rw": Rz, "r": r, "xR": xR,
                         "Rmin_w": float(Rz.min()), "odl": int(sum(1 for k in nd if k in set(wyn.odlaczone)))}
        return out

    # ---------------------------------------------------------------------------------------------
    # Przekroje (całkowanie naprężeń)
    # ---------------------------------------------------------------------------------------------
    def naprezenia_narozniki(self, wyn: WynikT) -> np.ndarray:
        """σ w narożach elementów [ne × 4 × 3] (kolejność węzłów elementu; z modami wewnętrznymi) — buforowane.
        Przy stałym η naprężenie jest liniowe w ξ (i odwrotnie), więc wartości w dowolnym punkcie krawędzi
        przekroju pionowego/poziomego wynikają z interpolacji liniowej naroży."""
        if getattr(wyn, "_nar", None) is not None:
            return wyn._nar
        a = self.el_ab[:, 0][:, None]
        b = self.el_ab[:, 1][:, None]
        ue = wyn.u[self.dof]
        ux, uz = ue[:, 0::2], ue[:, 1::2]
        al = wyn.alfa
        D = wyn.D_el if wyn.D_el is not None else self._D_iso
        out = np.zeros((self.ne, 4, 3))
        for k in range(4):
            xi, eta = _XI_N[k], _ETA_N[k]
            dNdx = (_XI_N * (1 + _ETA_N * eta) / 4)[None, :] * (2 / a)
            dNdz = (_ETA_N * (1 + _XI_N * xi) / 4)[None, :] * (2 / b)
            ex = (dNdx * ux).sum(1) + al[:, 0] * (-4 * xi / a[:, 0])
            ez = (dNdz * uz).sum(1) + al[:, 3] * (-4 * eta / b[:, 0])
            g = (dNdz * ux + dNdx * uz).sum(1) + al[:, 1] * (-4 * eta / b[:, 0]) + al[:, 2] * (-4 * xi / a[:, 0])
            eps = np.stack([ex, ez, g], axis=1)
            out[:, k] = np.einsum("eij,ej->ei", D, eps)
        wyn._nar = out
        return out

    def przekroj_pionowy(self, wyn: WynikT, x: float) -> dict:
        """Siły w przekroju pionowym x (lewa część działa na prawą): N = ∫σ_x·t dz [kN], V = ∫τ·t dz [kN],
        M = ∫σ_x·t·z dz [kNm] (względem z = 0), odcinki pełne [z0, z1] i profil liniowy w elementach
        prof = [(z0, z1, t, σx0, σx1, τ0, τ1)]."""
        nar = self.naprezenia_narozniki(wyn)
        i = int(np.searchsorted(self.gx, x, side="right") - 1)
        i = min(max(i, 0), len(self.gx) - 2)
        r = (x - self.gx[i]) / (self.gx[i + 1] - self.gx[i])
        col = self.el_grid[:, i]
        es = col[col >= 0]
        segs, prof = [], []
        N = V = M = 0.0
        for e in es:
            z0 = self.el_x0[e, 1]
            z1 = z0 + self.el_ab[e, 1]
            s0 = (1 - r) * nar[e, 0] + r * nar[e, 1]      # η = −1
            s1 = (1 - r) * nar[e, 3] + r * nar[e, 2]      # η = +1
            t = self.t_el[e]
            prof.append((z0, z1, t, s0[0], s1[0], s0[2], s1[2]))
            L = z1 - z0
            N += t * L * (s0[0] + s1[0]) / 2
            V += t * L * (s0[2] + s1[2]) / 2
            M += t * L * ((s0[0] * (2 * z0 + z1) + s1[0] * (z0 + 2 * z1)) / 6)
            if segs and abs(segs[-1][1] - z0) < 1e-9:
                segs[-1][1] = z1
            else:
                segs.append([z0, z1])
        return {"x": x, "N": N, "V": V, "M": M, "prof": prof, "odcinki": segs}

    def przekroj_poziomy(self, wyn: WynikT, z: float) -> dict:
        """Siły w przekroju poziomym z: N_z = ∫σ_z·t dx, V = ∫τ·t dx, M = ∫σ_z·t·x dx; prof = [(x0, x1, t, σz0, σz1, τ0, τ1)]."""
        nar = self.naprezenia_narozniki(wyn)
        j = int(np.searchsorted(self.gz, z, side="right") - 1)
        j = min(max(j, 0), len(self.gz) - 2)
        r = (z - self.gz[j]) / (self.gz[j + 1] - self.gz[j])
        row = self.el_grid[j, :]
        es = row[row >= 0]
        segs, prof = [], []
        N = V = M = 0.0
        for e in es:
            x0 = self.el_x0[e, 0]
            x1 = x0 + self.el_ab[e, 0]
            s0 = (1 - r) * nar[e, 0] + r * nar[e, 3]      # ξ = −1
            s1 = (1 - r) * nar[e, 1] + r * nar[e, 2]      # ξ = +1
            t = self.t_el[e]
            prof.append((x0, x1, t, s0[1], s1[1], s0[2], s1[2]))
            L = x1 - x0
            N += t * L * (s0[1] + s1[1]) / 2
            V += t * L * (s0[2] + s1[2]) / 2
            M += t * L * ((s0[1] * (2 * x0 + x1) + s1[1] * (x0 + 2 * x1)) / 6)
            if segs and abs(segs[-1][1] - x0) < 1e-9:
                segs[-1][1] = x1
            else:
                segs.append([x0, x1])
        return {"z": z, "N": N, "V": V, "M": M, "prof": prof, "odcinki": segs}

    def przekroj_linia(self, wyn: WynikT, p0, p1, n: int = 60) -> dict:
        """Przekrój wzdłuż dowolnego odcinka p0 → p1: trakcja normalna σ_nn (n — normalna lewa kierunku odcinka) i
        wypadkowa części rozciąganej F_t = ∫max(σ_nn, 0)·t ds [kN] (całkowanie trapezami na n punktach)."""
        p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
        d = p1 - p0
        L = float(np.hypot(*d))
        e_ = d / L
        nrm = np.array([-e_[1], e_[0]])
        ss = np.linspace(0, L, n + 1)
        snn = np.full(n + 1, np.nan)
        tt = np.zeros(n + 1)
        for k, s in enumerate(ss):
            p = p0 + s * e_
            e = self.element_w(*p)
            if e is None or not self.obrys.buffer(1e-9).contains(Point(*p)):
                continue
            sg = self.naprezenia_xy(wyn, *p)
            S = np.array([[sg[0], sg[2]], [sg[2], sg[1]]])
            snn[k] = nrm @ S @ nrm
            tt[k] = self.t_el[e]
        ok = ~np.isnan(snn)
        v = np.where(ok, snn, 0.0) * tt
        Ft = float(np.trapezoid(np.clip(v, 0, None), ss))
        return {"s": ss, "snn": snn, "Ft": Ft, "n": nrm, "L": L}


# ==================================================================================================
# Całkowanie bloków naprężeń przy krawędziach (pasy)
# ==================================================================================================
def blok_przy_krawedzi(prof: list, z_kraw: float, od_dolu: bool, kol: int = 3) -> dict:
    """Blok naprężeń jednego znaku przylegający do krawędzi z_kraw (profil liniowy w elementach z przekroju):
    zwraca {"F": wypadkowa [kN] (znak σ), "e": odległość środka bloku od krawędzi [m], "h": głębokość bloku [m]}.
    kol = 3 → σ normalne (σ_x w przekroju pionowym / σ_z w poziomym)."""
    segs = sorted(prof, key=lambda p: p[0], reverse=not od_dolu)
    if not segs:
        return {"F": 0.0, "e": 0.0, "h": 0.0, "s0": 0.0}
    first = segs[0]
    v0 = first[kol] if od_dolu else first[kol + 1]
    if abs(v0) < 1e-9:
        v0 = first[kol + 1] if od_dolu else first[kol]
    znak = 1.0 if v0 >= 0 else -1.0
    F = S = 0.0
    h = 0.0
    prev_end = None
    for (a, b, t, s_a, s_b, *_r) in segs:
        if prev_end is not None and abs((a if od_dolu else b) - prev_end) > 1e-9:
            break           # przerwa (otwór) — koniec bloku przy tej krawędzi
        # wartości od strony krawędzi (p) do strony dalszej (q)
        if od_dolu:
            zp, zq, vp, vq = a, b, s_a * znak, s_b * znak
        else:
            zp, zq, vp, vq = b, a, s_b * znak, s_a * znak
        Lg = abs(zq - zp)
        stop = False
        if vp >= 0 and vq >= 0:
            lz = Lg
        elif vp > 0 > vq:
            lz = Lg * vp / (vp - vq)
            vq = 0.0
            stop = True
        else:
            break
        # trapez od vp do vq na długości lz (odległość od krawędzi: d0 → d0 + lz)
        d0 = abs(zp - z_kraw)
        Fi = t * lz * (vp + vq) / 2
        Si = t * lz * (vp * (3 * d0 + lz) + vq * (3 * d0 + 2 * lz)) / 6     # ∫σ·d dd
        F += Fi
        S += Si
        h = d0 + lz
        prev_end = b if od_dolu else a
        if stop:
            break
    e = S / F if F > 1e-12 else 0.0
    s_kr = (first[kol] if od_dolu else first[kol + 1])
    return {"F": znak * F, "e": e, "h": h, "s0": float(s_kr)}


def wypadkowa_rozciagania(prof: list, kol: int = 3) -> tuple[float, float]:
    """Wypadkowa części rozciąganej σ w całym przekroju (profil liniowy w elementach): (F_t [kN], środek z_t)."""
    F = S = 0.0
    for (a, b, t, s_a, s_b, *_r) in prof:
        L = b - a
        if s_a >= 0 and s_b >= 0:
            Fi = t * L * (s_a + s_b) / 2
            Si = t * L * (s_a * (2 * a + b) + s_b * (a + 2 * b)) / 6
        elif s_a > 0 or s_b > 0:
            zc = a + L * s_a / (s_a - s_b)
            if s_a > 0:
                Fi = t * (zc - a) * s_a / 2
                Si = Fi * (a + (zc - a) / 3)
            else:
                Fi = t * (b - zc) * s_b / 2
                Si = Fi * (b - (b - zc) / 3)
        else:
            continue
        F += Fi
        S += Si
    return F, (S / F if F > 1e-12 else 0.0)
