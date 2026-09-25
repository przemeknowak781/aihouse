"""Solver ustalonego przewodzenia ciepła 2D — metoda objętości skończonych (MOS), scipy.sparse.

Równanie: ∇·(λ∇θ) = 0 w materiałach; na granicy materiał–strefa warunek Robina q = (θ_strefy − θ_s)/R_s
(h = 1/R_s; R_s = 0 → zadana temperatura powierzchni); na granicy materiał–pustka i na brzegu siatki — adiabatycznie
(płaszczyzny odcięcia, osie symetrii — PN-EN ISO 10211:2017).

Dyskretyzacja (komórki centrowane): przewodność między komórkami P i Q przez ścianę o długości A:
  G_PQ = A / (Δ_P/(2λ_P) + Δ_Q/(2λ_Q))           (średnia harmoniczna — ciągłość strumienia na granicy materiałów),
  G_Pz = A / (Δ_P/(2λ_P) + R_s)                  (ściana komórki przy strefie z).
Układ Σ_Q G_PQ(θ_P − θ_Q) + Σ_z G_Pz(θ_P − θ_z) = 0 jest symetryczny, dodatnio określony; rozwiązanie bezpośrednie
(SuperLU, `scipy.sparse.linalg.splu`) — bilans energii domyka się do dokładności maszynowej. Faktoryzacja jest
ponownie używana do rozwiązań jednostkowych (superpozycja → macierz współczynników sprzężenia L_2D).

Kierunek strumienia dla R_si wg ISO 6946 (0,10 w górę / 0,17 w dół / 0,13 poziomo) wyznaczany iteracyjnie z rozwiązania.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from .geometria import RSI_13788, RSI_13788_OKNA, Wezel
from .siatka import Klasyfikacja, Siatka, klasyfikuj


@dataclass
class Brzeg:
    """Ściany komórek materiału przylegające do stref (powierzchnie z warunkiem Robina)."""
    kom: np.ndarray       # numer niewiadomej (komórki materiału)
    jj: np.ndarray
    ii: np.ndarray
    strefa: np.ndarray    # indeks strefy
    orient: np.ndarray    # 0 — ściana ⟂ x (pionowa), 1 — ściana ⟂ y (pozioma)
    strona: np.ndarray    # +1 — strefa po stronie +x/+y komórki; −1 — po stronie −x/−y
    dl: np.ndarray        # długość ściany [m]
    g: np.ndarray         # przewodność pół-komórki na m²: 2λ/Δ
    x0: np.ndarray
    y0: np.ndarray
    x1: np.ndarray
    y1: np.ndarray
    rodzaj_mat: np.ndarray  # rodzaj materiału komórki (str)

    @property
    def n(self) -> int:
        return len(self.kom)

    @property
    def xm(self):
        return 0.5 * (self.x0 + self.x1)

    @property
    def ym(self):
        return 0.5 * (self.y0 + self.y1)


class ModelMOS:
    """Model dyskretny węzła na zadanej siatce. tryb: 'psi' (R_s wg ISO 6946) lub 'fRsi' (R_si = 0,25 / 0,13)."""

    def __init__(self, wezel: Wezel, siatka: Siatka, tryb: str = "psi"):
        self.wezel = wezel
        self.s = siatka
        self.tryb = tryb
        self.kl: Klasyfikacja = klasyfikuj(wezel, siatka)
        mat_id = self.kl.mat_id
        self.solid = mat_id >= 0
        self.N = int(self.solid.sum())
        if self.N == 0:
            raise ValueError(f"Węzeł {wezel.id}: brak komórek materiału na siatce")
        self.num = np.full(mat_id.shape, -1, dtype=np.int64)
        self.num[self.solid] = np.arange(self.N)
        self._zloz_wnetrze()
        self._zloz_brzeg()
        self.theta_stref = np.array([st.theta for st in wezel.strefy], float)
        self.Rs = self._ustal_Rs(None)
        self._lu = None

    # ------------------------------------------------------------------ składanie
    def _zloz_wnetrze(self):
        s, lam, sol = self.s, self.kl.lam, self.solid
        dx, dy = s.dx, s.dy
        rows, cols, vals = [], [], []
        # ściany ⟂ x
        m = sol[:, :-1] & sol[:, 1:]
        j, i = np.nonzero(m)
        G = dy[j] / (dx[i] / (2 * lam[j, i]) + dx[i + 1] / (2 * lam[j, i + 1]))
        self._gx = (j, i, G)
        rows += [self.num[j, i], self.num[j, i + 1]]
        cols += [self.num[j, i + 1], self.num[j, i]]
        vals += [-G, -G]
        diagv = np.zeros(self.N)
        np.add.at(diagv, self.num[j, i], G)
        np.add.at(diagv, self.num[j, i + 1], G)
        # ściany ⟂ y
        m = sol[:-1, :] & sol[1:, :]
        j, i = np.nonzero(m)
        G = dx[i] / (dy[j] / (2 * lam[j, i]) + dy[j + 1] / (2 * lam[j + 1, i]))
        self._gy = (j, i, G)
        rows += [self.num[j, i], self.num[j + 1, i]]
        cols += [self.num[j + 1, i], self.num[j, i]]
        vals += [-G, -G]
        np.add.at(diagv, self.num[j, i], G)
        np.add.at(diagv, self.num[j + 1, i], G)
        self._Aint = sp.coo_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))),
                                   shape=(self.N, self.N)).tocsr()
        self._diag_int = diagv

    def _zloz_brzeg(self):
        s, lam, sol, sid = self.s, self.kl.lam, self.solid, self.kl.strefa_id
        x, y, dx, dy = s.x, s.y, s.dx, s.dy
        mats = self.kl.materialy
        parts = []
        # ⟂ x: materiał (j,i) | strefa (j,i+1)
        for (msk, js, is_, iz, strona) in (
            (sol[:, :-1] & (sid[:, 1:] >= 0), 0, 0, 1, +1),
            (sol[:, 1:] & (sid[:, :-1] >= 0), 0, 1, 0, -1),
        ):
            j, i = np.nonzero(msk)
            ic = i + is_
            iz_ = i + iz
            xf = x[i + 1]
            parts.append(dict(jj=j, ii=ic, strefa=sid[j, iz_], orient=np.zeros_like(j), strona=np.full_like(j, strona),
                              dl=dy[j], g=2 * lam[j, ic] / dx[ic], x0=xf, y0=y[j], x1=xf, y1=y[j + 1]))
        # ⟂ y: materiał (j,i) | strefa (j+1,i)
        for (msk, js, jz, strona) in (
            (sol[:-1, :] & (sid[1:, :] >= 0), 0, 1, +1),
            (sol[1:, :] & (sid[:-1, :] >= 0), 1, 0, -1),
        ):
            j, i = np.nonzero(msk)
            jc = j + js
            jz_ = j + jz
            yf = y[j + 1]
            parts.append(dict(jj=jc, ii=i, strefa=sid[jz_, i], orient=np.ones_like(j), strona=np.full_like(j, strona),
                              dl=dx[i], g=2 * lam[jc, i] / dy[jc], x0=x[i], y0=yf, x1=x[i + 1], y1=yf))
        d = {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}
        rodz = np.array([m.rodzaj for m in mats] + ["-"], dtype=object)
        self.b = Brzeg(kom=self.num[d["jj"], d["ii"]], rodzaj_mat=rodz[self.kl.mat_id[d["jj"], d["ii"]]], **d)
        if self.b.n == 0:
            raise ValueError(f"Węzeł {self.wezel.id}: materiał nie styka się z żadną strefą")

    # ------------------------------------------------------------------ R_s
    def _ustal_Rs(self, T: np.ndarray | None) -> np.ndarray:
        b = self.b
        strefy = self.wezel.strefy
        th = np.array([st.theta for st in strefy])
        th_ref = 0.5 * (th.max() + th.min())
        Rs = np.empty(b.n)
        for k, st in enumerate(strefy):
            m = b.strefa == k
            if not m.any():
                continue
            if self.tryb == "fRsi" and st.rodzaj == "wewn":
                okn = np.isin(b.rodzaj_mat[m], ["rama", "szyba"])
                Rs[m] = np.where(okn, RSI_13788_OKNA, RSI_13788)
                continue
            spec = st.Rs
            if not isinstance(spec, dict):
                Rs[m] = float(spec)
                continue
            if T is None:
                cieplejsza = np.full(m.sum(), st.theta > th_ref)
            else:
                cieplejsza = st.theta > T[b.kom[m]]
            orient, strona = b.orient[m], b.strona[m]
            if self.wezel.przekroj == "poziomy":
                r = np.full(m.sum(), spec["poziomo"])
            else:
                # strefa nad komórką (strona +1, ściana ⟂ y): strumień w dół, gdy strefa cieplejsza
                w_dol = np.where(strona > 0, cieplejsza, ~cieplejsza)
                r = np.where(orient == 0, spec["poziomo"], np.where(w_dol, spec["dol"], spec["gora"]))
            Rs[m] = r
        return Rs

    def _Gb(self, Rs=None) -> np.ndarray:
        Rs = self.Rs if Rs is None else Rs
        return self.b.dl / (1.0 / self.b.g + Rs)

    def macierz(self) -> sp.csc_matrix:
        Gb = self._Gb()
        diag = self._diag_int.copy()
        np.add.at(diag, self.b.kom, Gb)
        return (self._Aint + sp.diags(diag)).tocsc()

    def _faktoryzacja(self):
        if self._lu is None:
            self._lu = spla.splu(self.macierz(), permc_spec="COLAMD")
        return self._lu

    def _rozwiaz_T(self, theta_stref: np.ndarray) -> np.ndarray:
        Gb = self._Gb()
        rhs = np.zeros(self.N)
        np.add.at(rhs, self.b.kom, Gb * theta_stref[self.b.strefa])
        return self._faktoryzacja().solve(rhs)

    # ------------------------------------------------------------------ rozwiązanie
    def rozwiaz(self, theta_stref: np.ndarray | None = None, iteruj_Rs: bool = True, max_iter: int = 6) -> "Rozwiazanie":
        th = self.theta_stref if theta_stref is None else np.asarray(theta_stref, float)
        T = self._rozwiaz_T(th)
        if iteruj_Rs:
            for _ in range(max_iter):
                Rs_new = self._ustal_Rs(T)
                if np.allclose(Rs_new, self.Rs):
                    break
                self.Rs = Rs_new
                self._lu = None
                T = self._rozwiaz_T(th)
        return Rozwiazanie(self, T, th)

    def rozwiaz_jednostkowe(self, grupy: list[str]) -> dict[str, "Rozwiazanie"]:
        """θ = 1 dla stref grupy g, 0 dla pozostałych (R_s zamrożone) — do superpozycji."""
        out = {}
        for g in grupy:
            th = np.array([1.0 if st.grupa == g else 0.0 for st in self.wezel.strefy])
            out[g] = Rozwiazanie(self, self._rozwiaz_T(th), th)
        return out


@dataclass
class Rozwiazanie:
    model: ModelMOS
    Tv: np.ndarray               # temperatury niewiadomych
    theta_stref: np.ndarray
    _cache: dict = field(default_factory=dict)

    # ---- pola
    @property
    def T(self) -> np.ndarray:
        if "T" not in self._cache:
            T = np.full(self.model.solid.shape, np.nan)
            T[self.model.solid] = self.Tv
            self._cache["T"] = T
        return self._cache["T"]

    @property
    def q_brzeg(self) -> np.ndarray:
        """Strumień przez ścianę brzegową [W/m], dodatni ze strefy do materiału."""
        b = self.model.b
        return self.model._Gb() * (self.theta_stref[b.strefa] - self.Tv[b.kom])

    @property
    def theta_pow(self) -> np.ndarray:
        """Temperatura powierzchni na ścianach brzegowych: θ_s = θ_z − q''·R_s."""
        b = self.model.b
        return self.theta_stref[b.strefa] - self.q_brzeg / b.dl * self.model.Rs

    def Phi_stref(self) -> np.ndarray:
        out = np.zeros(len(self.model.wezel.strefy))
        np.add.at(out, self.model.b.strefa, self.q_brzeg)
        return out

    def Phi_grup(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for st, f in zip(self.model.wezel.strefy, self.Phi_stref()):
            out[st.grupa] = out.get(st.grupa, 0.0) + float(f)
        return out

    def bilans(self) -> float:
        """Σ strumieni / (½ Σ |strumieni|) — kryterium bilansu (ISO 10211: < 10⁻⁴)."""
        f = self.Phi_stref()
        den = 0.5 * np.abs(f).sum()
        return float(abs(f.sum()) / den) if den > 0 else 0.0

    def Phi_calk(self) -> float:
        return float(0.5 * np.abs(self.Phi_stref()).sum())

    # ---- temperatury ścian komórek (do interpolacji)
    def _temp_scian(self):
        if "tf" in self._cache:
            return self._cache["tf"]
        m, s = self.model, self.model.s
        T, lam, sol = self.T, m.kl.lam, m.solid
        ny, nx = sol.shape
        # domyślnie (ściana do pustki / brzeg siatki — adiabatycznie): temperatura jedynej przyległej komórki
        # ściany zachodnie komórek materiału (jeśli sąsiad zach. nie jest materiałem)
        Tw = np.full((ny, nx + 1), np.nan)
        Te = np.full((ny, nx + 1), np.nan)
        Tw[:, 1:] = np.where(sol, T, np.nan)      # wartość z komórki leżącej na wschód od ściany
        Te[:, :-1] = np.where(sol, T, np.nan)     # z komórki na zachód od ściany
        Tfx = np.where(np.isnan(Te), Tw, np.where(np.isnan(Tw), Te, np.nan))
        Ts = np.full((ny + 1, nx), np.nan)
        Tn = np.full((ny + 1, nx), np.nan)
        Ts[1:, :] = np.where(sol, T, np.nan)
        Tn[:-1, :] = np.where(sol, T, np.nan)
        Tfy = np.where(np.isnan(Tn), Ts, np.where(np.isnan(Ts), Tn, np.nan))
        # materiał–materiał: średnia ważona przewodnościami pół-komórek
        j, i, _ = m._gx
        g1 = 2 * lam[j, i] / s.dx[i]
        g2 = 2 * lam[j, i + 1] / s.dx[i + 1]
        Tfx[j, i + 1] = (g1 * T[j, i] + g2 * T[j, i + 1]) / (g1 + g2)
        j, i, _ = m._gy
        g1 = 2 * lam[j, i] / s.dy[j]
        g2 = 2 * lam[j + 1, i] / s.dy[j + 1]
        Tfy[j + 1, i] = (g1 * T[j, i] + g2 * T[j + 1, i]) / (g1 + g2)
        # materiał–strefa: temperatura powierzchni
        b = m.b
        tp = self.theta_pow
        ox = b.orient == 0
        Tfx[b.jj[ox], b.ii[ox] + (b.strona[ox] > 0)] = tp[ox]
        oy = ~ox
        Tfy[b.jj[oy] + (b.strona[oy] > 0), b.ii[oy]] = tp[oy]
        self._cache["tf"] = (Tfx, Tfy)
        return Tfx, Tfy

    def temperatura(self, x: float, y: float, tol: float = 1e-9) -> float:
        """Temperatura w punkcie (rekonstrukcja liniowa w komórce między środkiem a ścianami; punkty na
        powierzchni → temperatura powierzchni). nan poza materiałem."""
        s, sol = self.model.s, self.model.solid
        Tfx, Tfy = self._temp_scian()
        ic = [i for i in range(max(0, np.searchsorted(s.x, x - tol) - 1), min(s.nx, np.searchsorted(s.x, x + tol) + 1))
              if s.x[i] - tol <= x <= s.x[i + 1] + tol]
        jc = [j for j in range(max(0, np.searchsorted(s.y, y - tol) - 1), min(s.ny, np.searchsorted(s.y, y + tol) + 1))
              if s.y[j] - tol <= y <= s.y[j + 1] + tol]
        vals = []
        T = self.T
        for j in jc:
            for i in ic:
                if not sol[j, i]:
                    continue
                Tc = T[j, i]
                xc, yc = s.xc[i], s.yc[j]
                if x <= xc:
                    tx = Tfx[j, i] + (Tc - Tfx[j, i]) * (x - s.x[i]) / (xc - s.x[i])
                else:
                    tx = Tc + (Tfx[j, i + 1] - Tc) * (x - xc) / (s.x[i + 1] - xc)
                if y <= yc:
                    ty = Tfy[j, i] + (Tc - Tfy[j, i]) * (y - s.y[j]) / (yc - s.y[j])
                else:
                    ty = Tc + (Tfy[j + 1, i] - Tc) * (y - yc) / (s.y[j + 1] - yc)
                vals.append(tx + ty - Tc)
        return float(np.mean(vals)) if vals else float("nan")

    # ---- strumienie w komórkach (wizualizacja)
    def strumien_komorek(self) -> tuple[np.ndarray, np.ndarray]:
        """Gęstość strumienia [W/m²] w środkach komórek (średnia ze ścian) — q_x, q_y."""
        m, s, T = self.model, self.model.s, self.T
        ny, nx = m.solid.shape
        qfx = np.zeros((ny, nx + 1))
        qfy = np.zeros((ny + 1, nx))
        j, i, G = m._gx
        qfx[j, i + 1] = G * (T[j, i] - T[j, i + 1]) / s.dy[j]
        j, i, G = m._gy
        qfy[j + 1, i] = G * (T[j, i] - T[j + 1, i]) / s.dx[i]
        b = m.b
        q = self.q_brzeg / b.dl       # dodatni do materiału
        ox = b.orient == 0
        # strefa po stronie +x: strumień do materiału = w kierunku −x
        qfx[b.jj[ox], b.ii[ox] + (b.strona[ox] > 0)] = -b.strona[ox] * q[ox]
        oy = ~ox
        qfy[b.jj[oy] + (b.strona[oy] > 0), b.ii[oy]] = -b.strona[oy] * q[oy]
        qx = 0.5 * (qfx[:, :-1] + qfx[:, 1:])
        qy = 0.5 * (qfy[:-1, :] + qfy[1:, :])
        qx[~m.solid] = np.nan
        qy[~m.solid] = np.nan
        return qx, qy

    # ---- powierzchnie
    def powierzchnie(self, rodzaj: str | None = "wewn", grupa: str | None = None, bez_okien: bool = False):
        """Maska ścian brzegowych stref danego rodzaju/grupy."""
        b = self.model.b
        strefy = self.model.wezel.strefy
        m = np.array([(rodzaj is None or strefy[k].rodzaj == rodzaj) and (grupa is None or strefy[k].grupa == grupa)
                      for k in b.strefa], dtype=bool) if b.n else np.zeros(0, bool)
        if bez_okien:
            m &= ~np.isin(b.rodzaj_mat, ["rama", "szyba"])
        return m

    def theta_si_min(self, rodzaj: str = "wewn", bez_okien: bool = True) -> tuple[float, float, float, int]:
        m = self.powierzchnie(rodzaj, bez_okien=bez_okien)
        if not m.any():
            m = self.powierzchnie(rodzaj, bez_okien=False)
        tp = np.where(m, self.theta_pow, np.inf)
        k = int(np.argmin(tp))
        b = self.model.b
        return float(tp[k]), float(b.xm[k]), float(b.ym[k]), k
