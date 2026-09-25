"""Wilgotność: temperatura powierzchni (f_Rsi) i kondensacja międzywarstwowa wg PN-EN ISO 13788:2013-05.

Rozdział 5 (krytyczna wilgotność powierzchni — ryzyko pleśni):
  p_e = φ_e·p_sat(θ_e); p_i = p_e + 1,10·Δp (klasa wilgotności, zał. A) albo p_i = φ_i·p_sat(θ_i) (WT: φ_i = 50 %);
  p_sat,min = p_i/0,8 (φ_si ≤ 0,8); θ_si,min = θ(p_sat,min); f_Rsi,min = (θ_si,min − θ_e)/(θ_i − θ_e);
  miesiąc krytyczny — max f_Rsi,min; element: f_Rsi = 1 − U·R_si, R_si = 0,25 m²K/W (0,13 dla oszklenia) (p. 4.3);
  WT zał. 2 pkt 2.2.2 dopuszcza f_Rsi,kryt = 0,72 (rejestr W-248).
Rozdział 6 (kondensacja międzywarstwowa — metoda Glasera miesięczna):
  temperatury na granicach warstw z oporów (R_si/R_se wg PN-EN ISO 6946 — p. 4.3), s_d = μ·d, linia ciśnienia pary
  jako „dolna otoczka wypukła” punktów p_sat (miejsca kondensacji), g_c = δ₀·[(p_{c-1} − p_c)/Δs' − (p_c − p_{c+1})/Δs''],
  δ₀ = 2·10⁻¹⁰ kg/(m·s·Pa); akumulacja M_a miesiąc po miesiącu od miesiąca, w którym kondensacja pojawia się
  po raz pierwszy; odparowanie — ciśnienie w płaszczyźnie z wodą = p_sat; ocena: czy M_a = 0 na koniec cyklu
  (wyschnięcie latem, WT zał. 2 pkt 2.2.5) i max M_a na tle kryteriów materiałowych
  (DIN 4108-3: ≤ 1,0 kg/m², ≤ 0,5 kg/m² na styku z warstwą nienasiąkliwą — kryterium literaturowe [ZAŁ]).
Wymagane s_d paroizolacji: najmniejsze s_d warstwy po ciepłej stronie izolacji, przy którym w żadnym miesiącu nie
występuje kondensacja (bisekcja).
Dane klimatyczne: TMY Poznań (WMO 12330) — średnie miesięczne θ_e i p_e (φ_e) z danych godzinowych ministerstwa.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from ..wspolne import (Zalozenia, fmt, miesiace_pl, naglowek_raportu, ok, tabela_md, wym, GODZINY_MIES)
from ..energia.klimat import klimat_miesieczny, p_sat, theta_z_psat
from .u_przegrody import RSI, RSE, _warstwy_we, r_pustki
from .warstwy import GRUNT_FUNKCJE, funkcja_warstwy, mat_props, sd_warstwy

DELTA0 = 2.0e-10               # kg/(m·s·Pa) — przepuszczalność pary wodnej powietrza (PN-EN ISO 13788 p. 3.?)
KLASY_DP = {1: 270.0, 2: 540.0, 3: 810.0, 4: 1080.0, 5: 1350.0}   # zał. A — Δp przy θ_e ≤ 0 °C [Pa]
KLASY_OPIS = {1: "magazyny", 2: "biura, mieszkania o normalnym zagęszczeniu i wentylacji",
              3: "budynki o nieznanym zagęszczeniu", 4: "hale sportowe, kuchnie, stołówki",
              5: "budynki o bardzo dużej wilgotności (pralnie, baseny)"}


def delta_p(theta_e: float, klasa: int) -> float:
    """PN-EN ISO 13788 zał. A — nadwyżka ciśnienia pary: Δp_max przy θ_e ≤ 0, 0 przy θ_e ≥ 20, liniowo."""
    dmax = KLASY_DP[klasa]
    if theta_e <= 0:
        return dmax
    if theta_e >= 20:
        return 0.0
    return dmax * (1 - theta_e / 20.0)


def warunki_wewn(theta_i: float, theta_e: np.ndarray, p_e: np.ndarray, *, klasa: int | None = None,
                 phi_i: float | None = None, wsp_bezp: float = 1.10) -> np.ndarray:
    """Miesięczne p_i [Pa]: φ_i stałe (WT) albo klasa wilgotności z wsp. bezpieczeństwa 1,10 (p. 4.2.4 / zał. A)."""
    if phi_i is not None:
        return np.full(12, phi_i * float(p_sat(theta_i)))
    return np.array([pe + wsp_bezp * delta_p(te, klasa or 3) for te, pe in zip(theta_e, p_e)])


# --------------------------------------------------------------------------------------------------
# Rozdział 5 — f_Rsi
# --------------------------------------------------------------------------------------------------
@dataclass
class WynikFRsi:
    theta_i: float
    opis_wilg: str
    theta_e: np.ndarray
    phi_e: np.ndarray
    p_e: np.ndarray
    p_i: np.ndarray
    phi_i: np.ndarray
    p_sat_min: np.ndarray
    theta_si_min: np.ndarray
    f_Rsi_min: np.ndarray
    miesiac_kryt: int
    f_Rsi_kryt: float
    f_Rsi_WT: float
    elementy: list[dict] = field(default_factory=list)   # {id, opis, f_Rsi, zrodlo, ok}

    @property
    def f_Rsi_wym(self) -> float:
        """Wartość do sprawdzeń: max(obliczona dla miesiąca krytycznego, 0,72 wg WT) — zachowawczo."""
        return max(self.f_Rsi_kryt, self.f_Rsi_WT)


def f_rsi_min(theta_i: float = 20.0, *, klasa: int | None = None, phi_i: float | None = 0.50,
              phi_si_max: float = 0.80) -> WynikFRsi:
    """Wymagany czynnik temperaturowy f_Rsi,min w miesiącach (PN-EN ISO 13788:2013 rozdz. 5, WT zał. 2 pkt 2.2.2)."""
    k = klimat_miesieczny()
    te, pe = k.theta_e, k.p_e
    pi = warunki_wewn(theta_i, te, pe, klasa=klasa, phi_i=phi_i)
    psm = pi / phi_si_max
    tsm = theta_z_psat(psm)
    f = (tsm - te) / (theta_i - te)
    f = np.where(te < theta_i - 0.5, f, np.nan)
    mk = int(np.nanargmax(f))
    opis = (f"φ_i = {fmt(phi_i * 100, 0)} % przy θ_i = {fmt(theta_i, 0)} °C (WT zał. 2 pkt 2.2.2)" if phi_i is not None
            else f"klasa wilgotności {klasa} ({KLASY_OPIS.get(klasa, '')}), p_i = p_e + 1,10·Δp")
    return WynikFRsi(theta_i=theta_i, opis_wilg=opis, theta_e=te, phi_e=k.phi_e, p_e=pe, p_i=pi,
                     phi_i=pi / p_sat(theta_i), p_sat_min=psm, theta_si_min=tsm, f_Rsi_min=f, miesiac_kryt=mk + 1,
                     f_Rsi_kryt=float(np.nanmax(f)), f_Rsi_WT=float(wym("energia", "fRsi_min", 0.72)))


def f_rsi_przegrody(U: float, Rsi: float = 0.25) -> float:
    """f_Rsi przegrody jednorodnej (poza mostkami): 1 − U·R_si, R_si = 0,25 m²K/W (PN-EN ISO 13788 p. 4.3)."""
    return 1.0 - U * Rsi


# --------------------------------------------------------------------------------------------------
# Rozdział 6 — Glaser
# --------------------------------------------------------------------------------------------------
@dataclass
class WarstwaG:
    kod: str
    nazwa: str
    funkcja: str
    d: float
    R: float
    sd: float
    mu: float | None


@dataclass
class WynikGlaser:
    kod: str
    nazwa: str
    rola: str
    warstwy: list[WarstwaG]
    theta_i: float
    opis_wilg: str
    x_R: np.ndarray                 # opory narastające na granicach (od wnętrza, z R_si) — len n+1
    x_sd: np.ndarray                # s_d narastające — len n+1
    theta: np.ndarray               # [12, n+1] temperatury granic
    psat: np.ndarray                # [12, n+1]
    p: np.ndarray                   # [12, n+1] rzeczywiste ciśnienie pary
    g_c: np.ndarray                 # [12, n+1] strumień kondensacji (+) / odparowania (−) [kg/(m²·mies.)]
    M_a: np.ndarray                 # [12, n+1] akumulacja na koniec miesiąca [kg/m²]
    kolejnosc: list[int]            # kolejność miesięcy obliczeń (0..11)
    kondensacja: bool
    wysycha: bool
    M_a_max: float
    miesiac_max: int | None
    plaszczyzny: list[int]
    sd_par_wym: float | None = None      # wymagane s_d paroizolacji — brak kondensacji (None: > 1500 m)
    sd_par_wym_dop: float | None = None  # wymagane s_d — kondensacja dopuszczalna (wysycha, M_a ≤ kryterium)
    sd_par_ist: float | None = None
    idx_par: int | None = None
    kryterium_kg_m2: float = 0.5
    uwagi: list[str] = field(default_factory=list)

    @property
    def ocena(self) -> str:
        if not self.kondensacja:
            return "brak kondensacji międzywarstwowej"
        if self.wysycha and self.M_a_max <= self.kryterium_kg_m2:
            return (f"kondensacja okresowa, M_a,max = {fmt(self.M_a_max * 1000, 0)} g/m² — wysycha w okresie letnim "
                    "(dopuszczalna wg WT zał. 2 pkt 2.2.5)")
        if self.wysycha:
            return (f"kondensacja okresowa M_a,max = {fmt(self.M_a_max * 1000, 0)} g/m² > "
                    f"{fmt(self.kryterium_kg_m2 * 1000, 0)} g/m² — wysycha, ale przekracza kryterium materiałowe")
        return "kondensacja narastająca — NIE wysycha w cyklu rocznym (niedopuszczalna)"

    @property
    def dopuszczalna(self) -> bool:
        return (not self.kondensacja) or (self.wysycha and self.M_a_max <= self.kryterium_kg_m2)


def _dolna_otoczka(xs: np.ndarray, ys: np.ndarray, stale: dict[int, float] | None = None) -> list[int]:
    """Indeksy punktów dolnej otoczki wypukłej łańcucha (x rosnące) od 0 do n — metoda „napiętej nici”."""
    n = len(xs)
    pts = list(range(n))
    hull: list[int] = []
    for i in pts:
        while len(hull) >= 2:
            a, b = hull[-2], hull[-1]
            # usuń b, gdy leży nad odcinkiem a–i (albo na nim)
            cross = (xs[b] - xs[a]) * (ys[i] - ys[a]) - (ys[b] - ys[a]) * (xs[i] - xs[a])
            if cross <= 1e-12:
                hull.pop()
            else:
                break
        hull.append(i)
    return hull


def _profil(xs, psat_m, p_i, p_e, stale: set[int]) -> tuple[np.ndarray, list[int]]:
    """Profil ciśnienia pary w miesiącu: punkty kotwiczne = otoczka dolna punktów (0, p_i), (s_c, p_sat,c), (s_T, p_e);
    płaszczyzny z wodą (`stale`) — zawsze kotwiczone na p_sat."""
    n = len(xs) - 1
    ys = psat_m.copy()
    ys[0] = p_i
    ys[n] = p_e
    kot = sorted({0, n} | set(stale))
    anchors: list[int] = []
    for a, b in zip(kot[:-1], kot[1:]):
        seg = list(range(a, b + 1))
        # scal punkty o tym samym x (warstwy o zerowym s_d) — minimum p_sat
        h = _dolna_otoczka(xs[seg], ys[seg])
        anchors += [seg[j] for j in h if not anchors or seg[j] != anchors[-1]]
    p = np.interp(xs, xs[anchors], ys[anchors]) if len(set(xs[anchors])) == len(anchors) else _interp_dup(xs, anchors, ys)
    return p, anchors


def _interp_dup(xs, anchors, ys):
    # punkty kotwiczne o równych x (s_d = 0 między nimi) — interpolacja odcinkami
    p = np.empty_like(xs, dtype=float)
    for j in range(len(xs)):
        x = xs[j]
        cand = [(a, b) for a, b in zip(anchors[:-1], anchors[1:]) if xs[a] <= x <= xs[b]]
        if not cand:
            p[j] = ys[anchors[-1]]
            continue
        a, b = cand[0]
        if a <= j <= b:
            for a2, b2 in cand:
                if a2 <= j <= b2:
                    a, b = a2, b2
                    break
        p[j] = ys[a] if xs[b] == xs[a] else ys[a] + (ys[b] - ys[a]) * (x - xs[a]) / (xs[b] - xs[a])
    return p


def warstwy_glaser(warstwy: Sequence[Any], materialy: Any, *, rola: str, kolejnosc_od_wewn: bool | None = None,
                   kierunek: str | None = None, uzyj_d_min_klina: bool = True) -> tuple[list[WarstwaG], float, float]:
    """Warstwy od wnętrza z R i s_d; zwraca (warstwy, R_si, R_se). Warstwy za wentylowaną pustką i grunt pominięte."""
    from .u_przegrody import ROLA_KIERUNEK, ROLA_STRONA
    kier = kierunek or ROLA_KIERUNEK.get(rola, "poziomo")
    strona = ROLA_STRONA.get(rola, "zewn")
    ws = _warstwy_we(warstwy)
    if kolejnosc_od_wewn is None:
        kolejnosc_od_wewn = rola not in ("dach", "strop_nieogrz_gora")
    seq = ws if kolejnosc_od_wewn else ws[::-1]
    Rsi = RSI[kier]
    Rse = RSE if strona == "zewn" else Rsi
    out = []
    for w in seq:
        mp = mat_props(materialy, w.get("mat"))
        fn = funkcja_warstwy(mp, w)
        d = float(w.get("d", 0.0))
        if fn in GRUNT_FUNKCJE:
            continue
        if w.get("pustka") in ("dw", "dobrze_wentylowana"):
            Rse = Rsi
            break
        lam = float(w["lambda"]) if w.get("lambda") is not None else mp.lam
        if fn == "pustka" or w.get("pustka"):
            R = r_pustki(d, kier)
            sd = 0.0 if d > 0 else 0.0
            sd = d * 1.0
        elif w.get("frakcje"):
            lam_eq = 0.0
            for f in w["frakcje"]:
                mpf = mat_props(materialy, f.get("mat"))
                lam_eq += float(f.get("lambda", mpf.lam)) * float(f["udzial"])
            R = d / lam_eq
            sd = sd_warstwy(mp, d)
        else:
            R = float(w["R"]) if w.get("R") is not None else (d / lam if lam else 0.0)
            sd = sd_warstwy(mp, d)
        out.append(WarstwaG(mp.kod, mp.nazwa or mp.kod, fn, d, R, sd, mp.mu))
    return out, Rsi, Rse


def glaser(warstwy: list[WarstwaG], Rsi: float, Rse: float, *, theta_i: float = 20.0, klasa: int | None = 3,
           phi_i: float | None = None, kod: str = "", nazwa: str = "", rola: str = "",
           kryterium_kg_m2: float = 0.5, theta_e: Sequence[float] | None = None, p_e: Sequence[float] | None = None,
           _licz_sd: bool = True) -> WynikGlaser:
    """Metoda Glasera miesięczna (PN-EN ISO 13788:2013 rozdz. 6)."""
    k = klimat_miesieczny()
    te = np.asarray(theta_e if theta_e is not None else k.theta_e, float)
    pe = np.asarray(p_e if p_e is not None else k.p_e, float)
    pi = warunki_wewn(theta_i, te, pe, klasa=klasa, phi_i=phi_i)
    n = len(warstwy)
    R = np.array([w.R for w in warstwy])
    sd = np.array([w.sd for w in warstwy])
    xR = np.concatenate([[Rsi], Rsi + np.cumsum(R)])            # granice: wewn. powierzchnia … zewn. powierzchnia
    RT = xR[-1] + Rse
    xs = np.concatenate([[0.0], np.cumsum(sd)])
    th = np.array([theta_i - (theta_i - t) * xR / RT for t in te])      # [12, n+1]
    ps = p_sat(th)
    t_sec = np.array(GODZINY_MIES, float) * 3600.0
    # miesiąc startowy — pierwszy miesiąc z kondensacją przy suchej przegrodzie, poprzedzony miesiącem bez kondensacji
    kond0 = []
    for m in range(12):
        p, anc = _profil(xs, ps[m], pi[m], pe[m], set())
        kond0.append(any(0 < a < n for a in anc if ps[m][a] < np.interp(xs[a], [0, xs[-1]], [pi[m], pe[m]]) - 1e-9))
    P = np.zeros((12, n + 1))
    G = np.zeros((12, n + 1))
    MA = np.zeros((12, n + 1))
    if not any(kond0):
        for m in range(12):
            P[m] = np.interp(xs, [0, xs[-1]], [pi[m], pe[m]]) if xs[-1] > 0 else pi[m]
        res = WynikGlaser(kod, nazwa, rola, warstwy, theta_i, _opis(klasa, phi_i, theta_i), xR, xs, th, ps, P, G, MA,
                          list(range(12)), False, True, 0.0, None, [], kryterium_kg_m2=kryterium_kg_m2)
        _uzup_par(res, warstwy)
        if _licz_sd:
            res.sd_par_wym = 0.0
            res.sd_par_wym_dop = 0.0
        return res
    start = next((m for m in range(12) if kond0[m] and not kond0[(m - 1) % 12]), 9)   # wszystkie mies. — od X
    kol = [(start + j) % 12 for j in range(12)]
    Ma = np.zeros(n + 1)
    plaszcz = set()
    for m in kol:
        stale = {j for j in range(1, n) if Ma[j] > 1e-12}
        p, anc = _profil(xs, ps[m], pi[m], pe[m], stale)
        g = np.zeros(n + 1)
        for j_i, j in enumerate(anc):
            if j in (0, n):
                continue
            a, b = anc[j_i - 1], anc[j_i + 1]
            dsa = xs[j] - xs[a]
            dsb = xs[b] - xs[j]
            fin = (p[a] - p[j]) / dsa if dsa > 1e-9 else 0.0
            fout = (p[j] - p[b]) / dsb if dsb > 1e-9 else 0.0
            g[j] = DELTA0 * (fin - fout) * t_sec[m]          # kg/m² w miesiącu (+ kondensacja, − odparowanie)
        # kotwice bez wody i z g < 0 (nie powinny wystąpić) — pomiń
        for j in range(1, n):
            if Ma[j] <= 1e-12 and g[j] < 0:
                g[j] = 0.0
        Ma = np.maximum(Ma + g, 0.0)
        plaszcz |= {j for j in range(1, n) if g[j] > 1e-12}
        P[m], G[m], MA[m] = p, g, Ma.copy()
    tot = MA.sum(axis=1)
    koniec = tot[kol[-1]]
    mmax = int(np.argmax(tot))
    res = WynikGlaser(kod, nazwa, rola, warstwy, theta_i, _opis(klasa, phi_i, theta_i), xR, xs, th, ps, P, G, MA, kol,
                      True, koniec <= 1e-9, float(tot.max()), mmax + 1, sorted(plaszcz), kryterium_kg_m2=kryterium_kg_m2)
    _uzup_par(res, warstwy)
    if _licz_sd:
        kw = dict(theta_i=theta_i, klasa=klasa, phi_i=phi_i, theta_e=te, p_e=pe)
        res.sd_par_wym = wymagane_sd_paroizolacji(warstwy, Rsi, Rse, **kw)
        res.sd_par_wym_dop = wymagane_sd_paroizolacji(warstwy, Rsi, Rse, kryterium="dopuszczalna",
                                                      kryterium_kg_m2=kryterium_kg_m2, **kw)
    return res


def _opis(klasa, phi_i, theta_i):
    if phi_i is not None:
        return f"φ_i = {fmt(phi_i * 100, 0)} %, θ_i = {fmt(theta_i, 0)} °C"
    return f"klasa wilgotności {klasa} (PN-EN ISO 13788 zał. A: {KLASY_OPIS.get(klasa, '')}), p_i = p_e + 1,10·Δp"


def _uzup_par(res: WynikGlaser, warstwy: list[WarstwaG]):
    iz = [i for i, w in enumerate(warstwy) if w.funkcja == "izolacja"]
    par = [i for i, w in enumerate(warstwy) if w.funkcja in ("paroizolacja", "szczelnosc")]
    if iz:
        par_c = [i for i in par if i < min(iz)]
        if par_c:
            res.idx_par = par_c[-1]
            res.sd_par_ist = warstwy[res.idx_par].sd


def wymagane_sd_paroizolacji(warstwy: list[WarstwaG], Rsi: float, Rse: float, *, kryterium: str = "brak",
                              kryterium_kg_m2: float = 0.5, **kw) -> float | None:
    """Najmniejsze s_d warstwy paroizolacyjnej po ciepłej stronie izolacji (istniejącej — zastępowane; brak — dodanej
    bez oporu cieplnego) spełniające kryterium: 'brak' — w żadnym miesiącu brak kondensacji międzywarstwowej;
    'dopuszczalna' — kondensat wysycha w cyklu rocznym i M_a,max ≤ kryterium (WT zał. 2 pkt 2.2.5).
    Zwraca s_d [m] (0 — nie wymaga), None — gdy brak izolacji albo nieosiągalne (> 1500 m)."""
    iz = [i for i, w in enumerate(warstwy) if w.funkcja == "izolacja"]
    if not iz:
        return None
    pos = min(iz)
    par = [i for i in range(pos) if warstwy[i].funkcja in ("paroizolacja", "szczelnosc")]

    def test(sd_add):
        ws = list(warstwy)
        if par:
            j = par[-1]
            w0 = ws[j]
            ws[j] = WarstwaG(w0.kod, w0.nazwa, w0.funkcja, w0.d, w0.R, sd_add, w0.mu)
        else:
            ws = ws[:pos] + [WarstwaG("PAR", "paroizolacja (wirtualna)", "paroizolacja", 0.0, 0.0, sd_add, None)] + ws[pos:]
        r = glaser(ws, Rsi, Rse, _licz_sd=False, kryterium_kg_m2=kryterium_kg_m2, **kw)
        return (not r.kondensacja) if kryterium == "brak" else r.dopuszczalna

    if test(0.0 if not par else 1e-3):
        return 0.0
    lo, hi = 0.0, 1500.0
    if not test(hi):
        return None
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if test(mid):
            hi = mid
        else:
            lo = mid
        if hi - lo < 0.05:
            break
    return hi


# --------------------------------------------------------------------------------------------------
# Wykres
# --------------------------------------------------------------------------------------------------
def wykres_glaser(r: WynikGlaser, plik, miesiac: int | None = None) -> str:
    """Wykres Glasera (PNG): (1) temperatura w przekroju (oś — grubość fizyczna od wnętrza),
    (2) ciśnienie pary p i p_sat na osi równoważnej dyfuzyjnie grubości s_d (każda warstwa ma szerokość ∝ s_d,
    ale nie mniejszą niż 4 % całości — odcinki pozostają prostoliniowe, opis osi w [m] s_d narastająco)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = (miesiac - 1) if miesiac else int(np.argmin(klimat_miesieczny().theta_e))
    d = np.array([w.d for w in r.warstwy])
    xd = np.concatenate([[0.0], np.cumsum(d)]) * 100.0
    sd = np.array([w.sd for w in r.warstwy])
    sT = max(float(sd.sum()), 1e-6)
    wid = np.maximum(sd, 0.04 * sT)
    xs = np.concatenate([[0.0], np.cumsum(wid)])
    kol = {"izolacja": "#fde0dd", "paroizolacja": "#c7e9c0", "szczelnosc": "#c7e9c0", "hydroizolacja": "#c6dbef",
           "przeciwwilgociowa": "#c6dbef", "konstrukcja": "#e0e0e0", "tynk": "#f7f7f7"}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=150)
    for ax, xx in ((ax1, xd), (ax2, xs)):
        for i, w in enumerate(r.warstwy):
            ax.axvspan(xx[i], xx[i + 1], color=kol.get(w.funkcja, "#fafafa"), zorder=0, lw=0)
            ax.axvline(xx[i], color="#bbbbbb", lw=0.5, zorder=1)
        ax.axvline(xx[-1], color="#bbbbbb", lw=0.5, zorder=1)
    ax1.plot(xd, r.theta[m], color="#c0392b", marker="o", ms=3, zorder=3)
    ax1.set_xlabel("grubość od strony wewnętrznej [cm]")
    ax1.set_ylabel("temperatura na granicach warstw θ [°C]")
    ax1.set_title(f"Temperatura — miesiąc {miesiace_pl()[m]} (θ_e = {klimat_miesieczny().theta_e[m]:.1f} °C)".replace(".", ","),
                  fontsize=9)
    ax2.plot(xs, r.psat[m], color="#2471a3", marker=".", label="p_sat (nasycenia)", zorder=3)
    ax2.plot(xs, r.p[m], color="#1e8449", ls="--", marker=".", label="p (rzeczywiste)", zorder=3)
    for j in r.plaszczyzny:
        ax2.plot(xs[j], r.psat[m][j], "rx", ms=9, mew=2, zorder=4)
    ax2.set_xticks(xs, [f"{v:.2f}".replace(".", ",") for v in np.concatenate([[0.0], np.cumsum(sd)])], rotation=90,
                   fontsize=6)
    ax2.set_xlabel("s_d narastająco [m] (szerokość warstwy ∝ s_d, min. 4 %)")
    ax2.set_ylabel("ciśnienie pary wodnej [Pa]")
    ax2.set_title(f"Ciśnienie pary — miesiąc {miesiace_pl()[m]}", fontsize=9)
    ax2.legend(fontsize=7, loc="upper right")
    for ax, xx in ((ax1, xd), (ax2, xs)):
        lo, hi = ax.get_ylim()
        for i, w in enumerate(r.warstwy):
            if (xx[i + 1] - xx[i]) > 0.035 * (xx[-1] - xx[0]):
                ax.text(0.5 * (xx[i] + xx[i + 1]), lo + 0.03 * (hi - lo), w.kod, rotation=90, fontsize=6,
                        ha="center", va="bottom", color="#444444", zorder=5)
    fig.suptitle(f"{r.kod} — {r.nazwa[:80]} (PN-EN ISO 13788:2013, TMY Poznań)\n{r.ocena}", fontsize=8)
    fig.tight_layout()
    fig.savefig(plik)
    plt.close(fig)
    return str(plik)


# --------------------------------------------------------------------------------------------------
# Raport
# --------------------------------------------------------------------------------------------------
def raport_frsi(fr: WynikFRsi, zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu("Ryzyko rozwoju pleśni — czynnik temperaturowy f_Rsi (PN-EN ISO 13788:2013 rozdz. 5)",
                          "PN-EN ISO 13788:2013-05 rozdz. 5; WT § 321, zał. 2 pkt 2.2.1–2.2.3 (f_Rsi ≥ f_Rsi,kryt; "
                          "dopuszczalnie 0,72); dane klimatyczne TMY Poznań (MIiR)",
                          [f"Warunki wewnętrzne: {fr.opis_wilg}; kryterium φ_si ≤ 80 %."])]
    rows = []
    for j in range(12):
        rows.append([miesiace_pl()[j], fmt(fr.theta_e[j], 1), fmt(fr.phi_e[j] * 100, 0), fmt(fr.p_e[j], 0),
                     fmt(fr.p_i[j], 0), fmt(fr.p_sat_min[j], 0), fmt(fr.theta_si_min[j], 1),
                     fmt(fr.f_Rsi_min[j], 3) if np.isfinite(fr.f_Rsi_min[j]) else "—"])
    s.append(tabela_md(["Mies.", "θ_e [°C]", "φ_e [%]", "p_e [Pa]", "p_i [Pa]", "p_sat,min [Pa]", "θ_si,min [°C]",
                        "f_Rsi,min"], rows))
    s.append("")
    s.append(f"Miesiąc krytyczny: **{miesiace_pl()[fr.miesiac_kryt - 1]}**, f_Rsi,max = **{fmt(fr.f_Rsi_kryt, 3)}**; "
             f"wartość dopuszczona przez WT: {fmt(fr.f_Rsi_WT, 2)}. Do sprawdzeń przyjęto zachowawczo "
             f"f_Rsi,wym = max(f_Rsi,max; {fmt(fr.f_Rsi_WT, 2)}) = **{fmt(fr.f_Rsi_wym, 3)}**.")
    s.append("")
    if fr.elementy:
        rows = [[e["id"], e["opis"], fmt(e["f_Rsi"], 3) if e.get("f_Rsi") is not None else "—", e.get("zrodlo", ""),
                 ok(e.get("ok"))] for e in fr.elementy]
        s.append(tabela_md(["Element", "Opis", "f_Rsi", "Źródło", f"f_Rsi ≥ {fmt(fr.f_Rsi_wym, 3)}"],
                           rows, "llrll"))
        s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)


def _sd_txt(v):
    if v is None:
        return "> 1500 (nieosiągalne)"
    if v <= 1e-9:
        return "0 (nie wymaga)"
    return fmt(v, 1)


def raport_glaser(wyniki: Sequence[WynikGlaser], wykresy: dict | None = None, zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu("Kondensacja międzywarstwowa — metoda Glasera (PN-EN ISO 13788:2013 rozdz. 6)",
                          "PN-EN ISO 13788:2013-05 rozdz. 6; WT § 321 ust. 2, zał. 2 pkt 2.2.4–2.2.5; "
                          "dane klimatyczne TMY Poznań (MIiR, WMO 12330)",
                          ["s_d = μ·d; g_c = δ₀·[(p_{c−1} − p_c)/Δs' − (p_c − p_{c+1})/Δs''], δ₀ = 2·10⁻¹⁰ kg/(m·s·Pa).",
                           "Wymagane s_d paroizolacji — najmniejsze s_d warstwy po ciepłej stronie izolacji: (1) przy którym "
                           "nie występuje kondensacja w żadnym miesiącu; (2) przy którym kondensat wysycha w cyklu rocznym "
                           "i M_a,max ≤ kryterium (WT zał. 2 pkt 2.2.5) — bisekcja do 1500 m."])]
    rows = []
    for r in wyniki:
        rows.append([r.kod, r.nazwa[:50], r.rola, "tak" if r.kondensacja else "nie",
                     fmt(r.M_a_max * 1000, 0), "tak" if r.wysycha else "NIE",
                     fmt(r.sd_par_ist, 1) if r.sd_par_ist is not None else "brak",
                     _sd_txt(r.sd_par_wym), _sd_txt(r.sd_par_wym_dop), ok(r.dopuszczalna)])
    s.append(tabela_md(["Przegroda", "Nazwa", "Rola", "Kondensacja", "M_a,max [g/m²]", "Wysycha",
                        "s_d paroizol. istn. [m]", "s_d wym. — brak kondensacji [m]",
                        "s_d wym. — kondensacja dopuszczalna [m]", "Ocena"], rows, "lllrrrrrrl"))
    s.append("")
    for r in wyniki:
        s.append(f"### {r.kod} — {r.nazwa}")
        s.append("")
        rows = [[i + 1, w.nazwa[:40], w.funkcja, fmt(w.d * 100, 1), fmt(w.R, 3), fmt(w.mu, 0) if w.mu else "—", fmt(w.sd, 2)]
                for i, w in enumerate(r.warstwy)]
        s.append(tabela_md(["Lp.", "Warstwa (od wnętrza)", "Funkcja", "d [cm]", "R [m²K/W]", "μ", "s_d [m]"], rows,
                           "rllrrrr"))
        s.append("")
        if r.kondensacja:
            rows = []
            for m in r.kolejnosc:
                rows.append([miesiace_pl()[m], fmt(klimat_miesieczny().theta_e[m], 1)] +
                            [fmt(r.g_c[m][j] * 1000, 1) for j in r.plaszczyzny] +
                            [fmt(r.M_a[m][j] * 1000, 1) for j in r.plaszczyzny])
            hd = ["Mies.", "θ_e"] + [f"g_c pł.{j} [g/m²]" for j in r.plaszczyzny] + [f"M_a pł.{j} [g/m²]" for j in r.plaszczyzny]
            s.append(tabela_md(hd, rows))
            s.append("")
            s.append("Płaszczyzny kondensacji (numer granicy za warstwą): " +
                     ", ".join(f"{j} — między „{r.warstwy[j - 1].kod}” a „{r.warstwy[j].kod}”" for j in r.plaszczyzny))
            s.append("")
        s.append(f"**Ocena:** {r.ocena}. Warunki wewnętrzne: {r.opis_wilg}.")
        s.append("")
        s.append(f"Wymagane s_d paroizolacji (po ciepłej stronie izolacji): brak kondensacji — {_sd_txt(r.sd_par_wym)} m; "
                 f"kondensacja dopuszczalna (wysycha, M_a ≤ {fmt(r.kryterium_kg_m2 * 1000, 0)} g/m²) — "
                 f"{_sd_txt(r.sd_par_wym_dop)} m; istniejąca warstwa: "
                 + (f"{r.warstwy[r.idx_par].kod}, s_d = {fmt(r.sd_par_ist, 1)} m "
                    f"({ok(r.sd_par_wym_dop is not None and r.sd_par_ist >= r.sd_par_wym_dop - 1e-6)})"
                    if r.sd_par_ist is not None else "brak") + ".")
        if wykresy and r.kod in wykresy:
            s.append("")
            s.append(f"![Glaser {r.kod}]({wykresy[r.kod]})")
        for u in r.uwagi:
            s.append(f"* {u}")
        s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
