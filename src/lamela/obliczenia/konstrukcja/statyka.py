"""Statyka prętowa: belki swobodnie podparte, ciągłe, wspornikowe (MES — elementy belkowe Eulera–Bernoulliego z
konsystentnym wektorem obciążeń; w węzłach rozwiązanie ścisłe) oraz obwiednie układów obciążeń zmiennych.

Konwencja: oś x wzdłuż belki [m], obciążenia skierowane w dół dodatnie (q [kN/m], P [kN]), ugięcie w dodatnie w dół,
moment M dodatni — rozciąganie włókien dolnych (przęsło), ujemny — nad podporą/utwierdzeniem. Reakcje dodatnie w górę.

Momenty i siły poprzeczne liczone są z równowagi (reakcje z MES), więc są ścisłe także pomiędzy węzłami siatki.
Obwiednie: dla przęseł belek ciągłych — wszystkie kombinacje obciążenia zmiennego przęsłami (2^n, n ≤ 12), co zawiera
układy „szachownicowe” PN-EN 1992-1-1 p. 5.1.3 (przęsła naprzemienne / dwa sąsiednie).
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np

from .wspolne import BladDanych, Parametry


@dataclass
class Podpora:
    x: float
    typ: str = "przegub"          # przegub | utwierdzenie | sprezyna
    k: float = 0.0                # sztywność sprężyny [kN/m] (typ 'sprezyna')
    nazwa: str = ""


@dataclass
class ObcQ:
    """Obciążenie ciągłe (liniowo zmienne) q0 → q1 [kN/m] na odcinku x0…x1 (None = cała belka)."""
    q0: float
    x0: float | None = None
    x1: float | None = None
    q1: float | None = None


@dataclass
class ObcP:
    """Siła skupiona P [kN] w punkcie x."""
    P: float
    x: float


@dataclass
class Rozwiazanie:
    """Wyniki dla jednego przypadku/kombinacji: siatka x, M(x), V_l(x), V_p(x) (tuż z lewej/prawej), w(x), reakcje."""
    x: np.ndarray
    M: np.ndarray
    Vl: np.ndarray
    Vp: np.ndarray
    w: np.ndarray
    R: np.ndarray                 # reakcje pionowe w kolejności podpór
    Mr: np.ndarray                # momenty utwierdzenia (przeciwnie do ruchu wskazówek zegara dodatnie)

    def __add__(self, o: "Rozwiazanie") -> "Rozwiazanie":
        return Rozwiazanie(self.x, self.M + o.M, self.Vl + o.Vl, self.Vp + o.Vp, self.w + o.w, self.R + o.R, self.Mr + o.Mr)

    def __mul__(self, a: float) -> "Rozwiazanie":
        return Rozwiazanie(self.x, self.M * a, self.Vl * a, self.Vp * a, self.w * a, self.R * a, self.Mr * a)

    __rmul__ = __mul__

    @staticmethod
    def zero_like(r: "Rozwiazanie") -> "Rozwiazanie":
        return r * 0.0

    def V_abs_max(self) -> float:
        return float(max(np.abs(self.Vl).max(), np.abs(self.Vp).max()))

    def w_max(self) -> float:
        return float(np.abs(self.w).max())


class Belka:
    """Belka na podporach punktowych (przegub/utwierdzenie/sprężyna), długość 0…L, sztywność EI [kNm²] stała."""

    def __init__(self, L: float, podpory: list[Podpora], EI: float = 1.0, dx: float = 0.05, punkty: tuple = ()):
        if L <= 0:
            raise BladDanych("długość belki ≤ 0")
        if not podpory:
            raise BladDanych("belka bez podpór")
        self.L = float(L)
        self.podpory = sorted(podpory, key=lambda p: p.x)
        for p in self.podpory:
            if p.x < -1e-9 or p.x > L + 1e-9:
                raise BladDanych(f"podpora poza belką: x = {p.x}")
        self.EI = float(EI)
        n = max(int(np.ceil(L / dx)), 4)
        xs = list(np.linspace(0.0, L, n + 1)) + [p.x for p in self.podpory] + [float(t) for t in punkty if 0 <= t <= L]
        self.x = np.unique(np.round(np.asarray(xs), 9))
        self._K = None
        # sprawdzenie geometrycznej niezmienności
        nw = sum(1 for p in self.podpory if p.typ in ("przegub", "sprezyna"))
        nu = sum(1 for p in self.podpory if p.typ == "utwierdzenie")
        if nu == 0 and nw < 2:
            raise BladDanych("belka geometrycznie zmienna (za mało podpór)")

    # ---- przęsła (do obwiedni) ----
    def przesla(self) -> list[tuple[float, float]]:
        xs = [p.x for p in self.podpory]
        out = []
        if xs[0] > 1e-6:
            out.append((0.0, xs[0]))
        out += [(a, b) for a, b in zip(xs[:-1], xs[1:]) if b - a > 1e-6]
        if self.L - xs[-1] > 1e-6:
            out.append((xs[-1], self.L))
        return out

    def dodaj_punkty(self, pts):
        self.x = np.unique(np.round(np.concatenate([self.x, np.asarray(pts, float)]), 9))
        self._K = None

    # ---- MES ----
    def _macierz(self):
        x = self.x
        n = len(x)
        K = np.zeros((2 * n, 2 * n))
        for e in range(n - 1):
            l = x[e + 1] - x[e]
            k = self.EI / l ** 3 * np.array([[12, 6 * l, -12, 6 * l], [6 * l, 4 * l * l, -6 * l, 2 * l * l],
                                              [-12, -6 * l, 12, -6 * l], [6 * l, 2 * l * l, -6 * l, 4 * l * l]])
            idx = [2 * e, 2 * e + 1, 2 * e + 2, 2 * e + 3]
            K[np.ix_(idx, idx)] += k
        fixed = []
        self._sup_idx = []
        for p in self.podpory:
            i = int(np.argmin(np.abs(x - p.x)))
            self._sup_idx.append(i)
            if p.typ == "sprezyna":
                K[2 * i, 2 * i] += p.k
            else:
                fixed.append(2 * i)
                if p.typ == "utwierdzenie":
                    fixed.append(2 * i + 1)
        self._fixed = sorted(set(fixed))
        self._free = [d for d in range(2 * n) if d not in set(self._fixed)]
        self._Kfull = K
        self._K = K[np.ix_(self._free, self._free)]

    def _q_na_elementach(self, obc: list) -> tuple[np.ndarray, np.ndarray]:
        """Obciążenie ciągłe na końcach elementów (q_i, q_j) — suma składników (przedziały dociągnięte do węzłów)."""
        x = self.x
        qi = np.zeros(len(x) - 1)
        qj = np.zeros(len(x) - 1)
        for o in obc:
            if not isinstance(o, ObcQ):
                continue
            x0 = 0.0 if o.x0 is None else float(o.x0)
            x1 = self.L if o.x1 is None else float(o.x1)
            q1 = o.q0 if o.q1 is None else o.q1
            if x1 - x0 <= 1e-12:
                continue

            def qat(t):
                return o.q0 + (q1 - o.q0) * (t - x0) / (x1 - x0)
            a, b = x[:-1], x[1:]
            m = (a >= x0 - 1e-9) & (b <= x1 + 1e-9)
            qi[m] += qat(a[m])
            qj[m] += qat(b[m])
        return qi, qj

    def rozwiaz(self, obc: list) -> Rozwiazanie:
        # węzły w punktach nieciągłości obciążeń
        extra = []
        for o in obc:
            if isinstance(o, ObcP):
                extra.append(o.x)
            elif isinstance(o, ObcQ):
                extra += [t for t in (o.x0, o.x1) if t is not None]
        if extra and not all(np.any(np.abs(self.x - t) < 1e-9) for t in extra):
            self.dodaj_punkty(extra)
        if self._K is None:
            self._macierz()
        x = self.x
        n = len(x)
        f = np.zeros(2 * n)
        qi, qj = self._q_na_elementach(obc)
        for e in range(n - 1):
            l = x[e + 1] - x[e]
            a, b = qi[e], qj[e]
            if a == 0 and b == 0:
                continue
            fe = -np.array([l * (7 * a + 3 * b) / 20, l * l * (3 * a + 2 * b) / 60,
                            l * (3 * a + 7 * b) / 20, -l * l * (2 * a + 3 * b) / 60])
            f[2 * e:2 * e + 4] += fe
        for o in obc:
            if isinstance(o, ObcP):
                i = int(np.argmin(np.abs(x - o.x)))
                f[2 * i] -= o.P
        u = np.zeros(2 * n)
        u[self._free] = np.linalg.solve(self._K, f[self._free])
        r = self._Kfull @ u - f
        R = np.zeros(len(self.podpory))
        Mr = np.zeros(len(self.podpory))
        for k, (p, i) in enumerate(zip(self.podpory, self._sup_idx)):
            if p.typ == "sprezyna":
                R[k] = p.k * (-u[2 * i])
            else:
                R[k] = r[2 * i]
                if p.typ == "utwierdzenie":
                    Mr[k] = r[2 * i + 1]
        # siły wewnętrzne z równowagi (od lewego końca)
        M = np.zeros(n)
        Vl = np.zeros(n)
        Vp = np.zeros(n)
        # obciążenie ciągłe: całki na elementach (liniowe) — skumulowane
        seg_F = (qi + qj) / 2 * np.diff(x)                         # wypadkowa na elemencie
        seg_c = np.where(qi + qj != 0, np.diff(x) * (qi + 2 * qj) / (3 * np.where(qi + qj != 0, qi + qj, 1)), 0)
        cumF = np.concatenate([[0.0], np.cumsum(seg_F)])
        cumFx = np.concatenate([[0.0], np.cumsum(seg_F * (x[:-1] + seg_c))])   # Σ F·x_c
        sup_x = np.array([p.x for p in self.podpory])
        P_list = [(o.x, o.P) for o in obc if isinstance(o, ObcP)]
        for i, xi in enumerate(x):
            m = cumF[i] * xi - cumFx[i]                           # ∫q(t)(x−t)dt
            v = cumF[i]
            Mi = -m
            Vi = -v
            for k, xs in enumerate(sup_x):
                if xs < xi - 1e-9:
                    Mi += R[k] * (xi - xs) - Mr[k]
                    Vi += R[k]
                elif abs(xs - xi) <= 1e-9 and xi <= 1e-9:
                    Mi -= Mr[k]              # utwierdzenie na lewym końcu: M(0⁺) = −M_r
            for xp, P in P_list:
                if xp < xi - 1e-9:
                    Mi -= P * (xi - xp)
                    Vi -= P
            M[i] = Mi
            Vl[i] = Vi
            vp = Vi
            for k, xs in enumerate(sup_x):
                if abs(xs - xi) <= 1e-9:
                    vp += R[k]
            for xp, P in P_list:
                if abs(xp - xi) <= 1e-9:
                    vp -= P
            Vp[i] = vp
        w = -u[0::2]
        return Rozwiazanie(x.copy(), M, Vl, Vp, w, R, Mr)


# ==================================================================================================
# Obwiednie kombinacji (PN-EN 1990 6.10a/6.10b; PN-EN 1992-1-1 5.1.3 — układy przęsłowe)
# ==================================================================================================
@dataclass
class Obwiednia:
    x: np.ndarray
    M_max: np.ndarray
    M_min: np.ndarray
    V_max: np.ndarray
    V_min: np.ndarray
    R_max: np.ndarray
    R_min: np.ndarray
    kombinacje: int = 0
    opis: str = ""
    przesla: list = field(default_factory=list)

    @property
    def M_przeslo(self) -> float:
        return float(self.M_max.max())

    @property
    def M_podpora(self) -> float:
        return float(self.M_min.min())

    @property
    def V_Ed(self) -> float:
        return float(max(np.abs(self.V_max).max(), np.abs(self.V_min).max()))


def obwiednia_ULS(belka: Belka, G: list, Q_przesla: list[list] | None, p: Parametry | None = None,
                  psi0: float = 0.7, Q_inne: list | None = None) -> tuple[Obwiednia, dict]:
    """Obwiednia STR: max z 6.10a (γ_G·G + γ_Q·ψ0·Q) i 6.10b (ξ·γ_G·G + γ_Q·Q) dla wszystkich układów obciążenia
    zmiennego przęsłami (Q_przesla[i] — lista obciążeń przęsła i). G zawsze z γ_G,sup na wszystkich przęsłach
    (PN-EN 1992-1-1 5.1.3(1)P, uwaga). Q_inne — obciążenie zmienne działające zawsze (np. w całości).

    Zwraca (obwiednia, rozwiązania bazowe {'G': …, 'Q': [...]}) — do kombinacji SLS.
    """
    p = p or Parametry()
    rG = belka.rozwiaz(G)
    rQ = [belka.rozwiaz(q) for q in (Q_przesla or [])]
    rQi = belka.rozwiaz(Q_inne) if Q_inne else None
    wsp = [(p.gG_sup, p.gQ * psi0), (p.xi * p.gG_sup, p.gQ)]
    n = len(rQ)
    if n > 12:
        raise BladDanych("za dużo przęseł do pełnej obwiedni (> 12)")
    combos = []
    for aG, aQ in wsp:
        for mask in itertools.product((0, 1), repeat=n) if n else [()]:
            r = rG * aG
            for k, on in enumerate(mask):
                if on:
                    r = r + rQ[k] * aQ
            if rQi is not None:
                r = r + rQi * aQ
            combos.append(r)
    Ms = np.array([c.M for c in combos])
    Vl = np.array([c.Vl for c in combos])
    Vp = np.array([c.Vp for c in combos])
    Rs = np.array([c.R for c in combos])
    V_all_max = np.maximum(Vl.max(0), Vp.max(0))
    V_all_min = np.minimum(Vl.min(0), Vp.min(0))
    ob = Obwiednia(rG.x, Ms.max(0), Ms.min(0), V_all_max, V_all_min, Rs.max(0), Rs.min(0), len(combos),
                   "6.10a/6.10b × układy przęsłowe", belka.przesla())
    return ob, {"G": rG, "Q": rQ, "Qi": rQi}


def kombinacja_SLS(baz: dict, psi: float = 1.0) -> Rozwiazanie:
    """SLS: G + ψ·ΣQ (ψ = 1 — charakterystyczna, ψ2 — quasi-stała), wszystkie przęsła obciążone zmiennym."""
    r = baz["G"] * 1.0
    for q in baz["Q"]:
        r = r + q * psi
    if baz.get("Qi") is not None:
        r = r + baz["Qi"] * psi
    return r


# ==================================================================================================
# Wzory zamknięte (do sprawdzeń ręcznych w raportach i testach)
# ==================================================================================================
def M_przeslo_swob(q: float, l: float) -> float:
    """M = q·l²/8 (belka swobodnie podparta, obciążenie równomierne)."""
    return q * l * l / 8.0


def w_swob(q: float, l: float, EI: float) -> float:
    """w = 5·q·l⁴/(384·EI)."""
    return 5.0 * q * l ** 4 / (384.0 * EI)


def M_wspornik(q: float, l: float, P: float = 0.0) -> float:
    """M = −(q·l²/2 + P·l) (wspornik)."""
    return -(q * l * l / 2.0 + P * l)
