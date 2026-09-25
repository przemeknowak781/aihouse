"""Płyta fundamentowa z żebrami na podłożu sprężystym (Winkler) — MES płytowy z kontaktem jednostronnym.

Model:
  * płyta — elementy ACM biblioteki (:class:`plyty.PlytaMES`), siatka ortogonalna ≤ 0,25 m dopasowana do krawędzi
    żeber, osi ścian i słupów; ŻEBRA i POGRUBIENIA pod słupami — strefy o zwiększonej grubości h = h_płyty + h_żebra
    (pasma o zwiększonej sztywności D = E·h³/12(1−ν²), ciężar 25·h) [ZAŁ: mimośród osi żebra względem płaszczyzny
    środkowej płyty pominięty — sztywność na zginanie żebra z płytą ≈ sztywność pasma pełnej wysokości; błąd po stronie
    mniejszej sztywności teowej dla żeber wystających w dół — przyjęcie typowe dla płyt z żebrami na podłożu];
  * podłoże — sprężyny Winklera skupione w węzłach (k_s·A_węzła), KONTAKT JEDNOSTRONNY: elementy, których ugięcie
    średnie jest skierowane w górę (odrywanie), tracą sprężyny; iteracja do ustalenia strefy kontaktu;
  * k_s z danych geotechniki modelu (moduł edometryczny M₀, ν) i wymiarów płyty — osiadanie sprężyste płyty wiotkiej
    na półprzestrzeni (Schleicher/Steinbrenner — Bowles, *Foundation Analysis and Design*, 5th ed., 1996, rozdz. 5.6,
    wzór (5-16a), tabl. 5-2; PN-EN 1997-1 zał. F.2: s = p·b·f/E_m): k_s = E_s/(α·B·(1−ν²)·I_c), E_s = M₀·(1+ν)(1−2ν)/(1−ν);
    rozrzut ×0,5 / ×2 — obwiednia wyników (zalecenie praktyki dla modelu Winklera, np. Bowles 9.7);
  * obciążenia z :class:`pozycje.AnalizaKonstrukcji`: profile obciążeń liniowych ścian parteru (przypadki G, Q…),
    siły w słupach, ciężar płyty i warstw podłogi (przegroda kondygnacji), obciążenie użytkowe posadzki;
  * kombinacje PN-EN 1990 + NA (6.10a/b, char.), obwiednia po wariantach k_s.
Weryfikacja: belka nieskończona na podłożu sprężystym obciążona siłą skupioną (Hetényi, *Beams on Elastic
Foundation*, 1946, rozdz. II): w₀ = P·λ/(2k·b), M₀ = P/(4λ), λ = ⁴√(k·b/(4EI)) — funkcja :func:`weryfikacja_hetenyi`
(test: błąd ≤ 3 % przy siatce 0,1 m).
Sprawdzenia: docisk do podłoża p_d ≤ q_Rd (PN-EN 1997-1 zał. D, DA2*), odrywanie, przebicie pod słupami (PN-EN 1992-1-1
6.4.4(2)), zginanie (Wood–Armer) → A_s,req na elementach → dobór siatek i dozbrojeń (moduł rysunków).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from .materialy import Beton, StalZbrojeniowa
from .plyty import PlytaMES, WynikMES, wood_armer
from .wspolne import BladDanych, Parametry, Wynik, f


# ==================================================================================================
# Współczynnik podatności podłoża
# ==================================================================================================
@dataclass
class Podloze(Wynik):
    k_s: float = 0.0            # kN/m³
    k_min: float = 0.0
    k_max: float = 0.0
    E_s: float = 0.0            # kPa
    I_c: float = 0.0


def wsp_wplywu_prostokata(m: float) -> float:
    """Współczynnik wpływu osiadania środka prostokąta wiotkiego na półprzestrzeni (Schleicher):
    I_c = (2/π)·[m·ln((1 + √(1+m²))/m) + ln(m + √(1+m²))], m = L/B ≥ 1 (Bowles 1996, (5-16a) — dla środka
    I_c = 4·I_narożnika, ν uwzględnione osobno)."""
    m = max(m, 1.0)
    r = math.sqrt(1 + m * m)
    return 2 / math.pi * (m * math.log((1 + r) / m) + math.log(m + r))


def k_s_z_geotechniki(B: float, L: float, M0: float, nu: float = 0.3, alfa: float = 0.85,
                      rozrzut: float = 2.0) -> Podloze:
    """k_s = E_s/(α·B·(1−ν²)·I_c) [kN/m³]; B ≤ L — wymiary płyty [m]; M₀ — moduł edometryczny [kPa];
    α = 0,85 — stosunek osiadania średniego do osiadania środka płyty wiotkiej."""
    B, L = sorted((B, L))
    w = Podloze(nazwa="Współczynnik podatności podłoża (Winkler) z parametrów geotechnicznych")
    Es = M0 * (1 + nu) * (1 - 2 * nu) / (1 - nu)
    w.krok("Moduł sprężystości gruntu z modułu edometrycznego", "E_s = M₀·(1+ν)(1−2ν)/(1−ν)",
           f"{f(M0, 0)}·(1+{f(nu, 2)})(1−2·{f(nu, 2)})/(1−{f(nu, 2)})", Es, "kPa", nd=0,
           zrodlo="teoria sprężystości (jednoosiowy stan odkształcenia); PN-EN 1997-2 zał. K")
    Ic = wsp_wplywu_prostokata(L / B)
    w.krok("Współczynnik wpływu (środek prostokąta, m = L/B)", "I_c", f"m = {f(L / B, 3)}", Ic, nd=3,
           zrodlo="Bowles (1996) (5-16a); PN-EN 1997-1 zał. F.2")
    k = Es / (alfa * B * (1 - nu ** 2) * Ic)
    w.krok("Współczynnik podatności (osiadanie średnie α·s_c)", "k_s = E_s/(α·B·(1−ν²)·I_c)",
           f"{f(Es, 0)}/({f(alfa, 2)}·{f(B, 2)}·(1−{f(nu, 2)}²)·{f(Ic, 3)})", k, "kN/m³", nd=0)
    w.krok("Obwiednia wariantów (niepewność modelu Winklera)", "k_s,min; k_s,max = k_s/r; k_s·r",
           f"r = {f(rozrzut, 1)}", f"{f(k / rozrzut, 0)}; {f(k * rozrzut, 0)}", "kN/m³", zrodlo="[ZAŁ] Bowles 9.7")
    w.k_s, w.k_min, w.k_max, w.E_s, w.I_c = k, k / rozrzut, k * rozrzut, Es, Ic
    return w


# ==================================================================================================
# Płyta na podłożu Winklera — kontakt jednostronny
# ==================================================================================================
@dataclass
class WynikKontakt:
    wynik: WynikMES             # ugięcia, momenty (m_x, m_y, m_xy) w środkach elementów
    p: np.ndarray               # nacisk na podłoże w elementach [kPa] (≥ 0)
    aktywne: np.ndarray         # maska elementów w kontakcie
    iteracje: int


class PlytaWinkler(PlytaMES):
    """Płyta ACM na sprężynach Winklera (skupionych w węzłach) bez podpór sztywnych; kontakt jednostronny."""

    def __init__(self, obrys: Polygon, grubosc: float, E: float, k_s: float, nu: float = 0.2, siatka: float = 0.25,
                 linie_siatki: tuple = ((), ()), strefy: list | None = None):
        self.k_s = float(k_s)
        super().__init__(obrys, grubosc, E, nu, [], [], siatka, linie_siatki, strefy)

    def _warunki(self):
        self.sup_nodes = {}
        self.fixed = np.array([], dtype=int)
        n = self.K.shape[0]
        self.free = np.arange(n)
        self.udzial = np.ones(len(self.nodes))
        self.A_el = self.el_ab[:, 0] * self.el_ab[:, 1]
        self.aktywne = np.ones(len(self.els), bool)
        self._faktoryzuj()

    def _sprezyny(self) -> np.ndarray:
        kn = np.zeros(len(self.nodes))
        for e in np.nonzero(self.aktywne)[0]:
            kn[self.el_nodes[e]] += self.k_s * self.A_el[e] / 4.0
        return kn

    def _faktoryzuj(self):
        kn = self._sprezyny()
        n = self.K.shape[0]
        d = np.zeros(n)
        d[0::3] = kn
        Kt = (self.K + sp.diags(d)).tocsc()
        try:
            self._lu = spla.splu(Kt)
        except RuntimeError as e:
            raise BladDanych(f"Płyta na podłożu: układ osobliwy (za mała strefa kontaktu?) ({e})") from e
        self._kn = kn

    def rozwiaz_kontakt(self, f: np.ndarray, maks_iter: int = 30, jednostronny: bool = True) -> WynikKontakt:
        """Rozwiązanie z kontaktem jednostronnym: elementy o średnim ugięciu < 0 (w górę) bez sprężyn — iteracja.
        jednostronny=False — sprężyny dwustronne (model klasyczny Winklera, do weryfikacji analitycznej)."""
        self.aktywne = np.ones(len(self.els), bool)
        self._faktoryzuj()
        it = 0
        while True:
            it += 1
            wyn = self.rozwiaz(f)
            w_el = wyn.w[self.el_nodes].mean(axis=1)
            if not jednostronny:
                break
            nowe = w_el > 0.0
            if np.array_equal(nowe, self.aktywne) or it >= maks_iter or not nowe.any():
                break
            self.aktywne = nowe
            self._faktoryzuj()
        p = np.where(self.aktywne, self.k_s * np.clip(w_el, 0.0, None), 0.0)
        return WynikKontakt(wyn, p, self.aktywne.copy(), it)


def weryfikacja_hetenyi(L: float = 24.0, b: float = 1.0, h: float = 0.25, E: float = 31e6, k: float = 20000.0,
                        P: float = 100.0, siatka: float = 0.1) -> dict:
    """Porównanie MES (pasmo płyty L × b na sprężynach, siła liniowa P [kN/m] na całej szerokości w środku długości)
    z rozwiązaniem belki nieskończonej na podłożu sprężystym (Hetényi 1946): w₀ = P·λ/(2k), M₀ = P/(4λ) na 1 m
    szerokości, λ = ⁴√(k/(4·E·I)), I = h³/12 (pasmo b = 1 m; ν = 0 — stan belkowy)."""
    pl = PlytaWinkler(box(0.0, 0.0, L, b), h, E, k, nu=0.0, siatka=siatka, linie_siatki=((L / 2,), ()))
    fv = pl.wektor(0.0, linie=[(LineString([(L / 2, 0.0), (L / 2, b)]), P)])
    r = pl.rozwiaz_kontakt(fv, jednostronny=False)
    EI = E * h ** 3 / 12
    lam = (k / (4 * EI)) ** 0.25
    w0 = P * lam / (2 * k)
    M0 = P / (4 * lam)
    w_mes = float(r.wynik.w.max())
    M_mes = float(r.wynik.m[:, 0].max())
    # moment MES — w środku elementu (a = siatka/2 od linii obciążenia): M(a) = M₀·e^(−λa)·(cos λa − sin λa)
    a = float(min(abs(pl.el_c[:, 0] - L / 2)))
    M_a = M0 * math.exp(-lam * a) * (math.cos(lam * a) - math.sin(lam * a))
    return {"lambda": lam, "w0": w0, "M0": M0, "M_a": M_a, "a": a, "w_mes": w_mes, "M_mes": M_mes,
            "blad_w": abs(w_mes / w0 - 1.0), "blad_M": abs(M_mes / M_a - 1.0), "L_lambda": L * lam}


# ==================================================================================================
# Analiza płyty fundamentowej budynku (dane z modelu i z AnalizaKonstrukcji)
# ==================================================================================================
@dataclass
class WynikPlytyFund:
    id: str
    obrys: Polygon
    h: float
    spod: float
    beton: Beton
    podloze: Podloze
    el_c: np.ndarray
    el_ab: np.ndarray
    h_el: np.ndarray
    strefa_el: list                      # id strefy (żebro/pogrubienie) elementu lub ""
    M: dict                              # dol_x, dol_y, gora_x, gora_y → obwiednia ULS [kNm/m] (dół ≥ 0, góra ≤ 0)
    As: dict                             # jw. → A_s,req [mm²/m]
    As_min: np.ndarray                   # A_s,min elementu [mm²/m]
    mu_przekr: np.ndarray                # maska: μ > μ_lim (przekrój podwójnie zbrojony)
    p_d_max: float
    p_k_max: float
    w_k_max: float
    oderwanie: float                     # udział powierzchni bez kontaktu (maks. po kombinacjach)
    q_Rd: float
    c_dol: float
    c_gora: float
    wyniki: list = field(default_factory=list)
    kombinacje: int = 0


def _klasa(model, mat, p):
    from .materialy import klasa_betonu_z_nazwy
    m = model.material(str(mat)) if mat else None
    return klasa_betonu_z_nazwy(m.nazwa if m else str(mat)) or p.beton_dla("fundament")[1]


def analiza_plyty_fundamentowej(an, siatka: float = 0.25, c_dol: float = 50.0, c_gora: float = 35.0,
                                fi_zal: int = 12) -> WynikPlytyFund | None:
    """MES płyty fundamentowej z żebrami/pogrubieniami na podłożu Winklera (kontakt jednostronny, obwiednia k_s)."""
    from .obciazenia import Oddz, kombinacje, obciazenie_uzytkowe, zestawienie_przegrody
    from . import fundamenty as fund
    m, p = an.m, an.p
    fu = m.fundamenty()
    els = fu.get("elementy") or []
    pl_el = [e for e in els if "obrys" in e]
    if not pl_el:
        return None
    e0 = pl_el[0]
    P = Polygon(e0["obrys"]).buffer(0)
    h = float(e0.get("h", 0.25))
    spod = float(e0.get("spod", -0.4))
    beton = Beton.z_parametrow(_klasa(m, e0.get("mat"), p), p)
    E = beton.E_cm * 1000.0
    strefy, lx, ly, nazwy = [], set(), set(), []
    for e in els:
        if "os" not in e:
            continue
        ln = LineString(e["os"])
        B = float(e.get("b", 0.6))
        g = (ln.buffer(B / 2, cap_style=3) if ln.length < B else ln.buffer(B / 2, cap_style=2)).intersection(P)
        if g.is_empty:
            continue
        hz = h + float(e.get("h", 0.3))
        strefy.append((g, hz, E))
        nazwy.append(str(e["id"]))
        x0, y0, x1, y1 = g.bounds
        lx.update([x0, x1])
        ly.update([y0, y1])
    k0 = m.kondygnacje[0].id
    for w in m.sciany(k0):
        (xa, ya), (xb, yb) = w.p1, w.p2
        if abs(xa - xb) < 1e-6:
            lx.add(xa)
        elif abs(ya - yb) < 1e-6:
            ly.add(ya)
    for c in m.slupy():
        if float(c["z_od"]) < spod + h + 0.5 and P.contains(Point(*c["xy"])):
            lx.add(c["xy"][0])
            ly.add(c["xy"][1])
    x0, y0, x1, y1 = P.bounds
    geo = m.raw.get("geotechnika") or {}
    M0 = float((geo.get("grunt") or {}).get("M0") or 60000.0)
    pod = k_s_z_geotechniki(x1 - x0, y1 - y0, M0)
    plyty = {kk: PlytaWinkler(P, h, E, kk, nu=p.nu_beton, siatka=siatka, linie_siatki=(tuple(lx), tuple(ly)),
                              strefy=strefy) for kk in (pod.k_s, pod.k_min, pod.k_max)}
    pl0 = plyty[pod.k_s]
    h_el = pl0.h_el.copy()
    strefa_el = [""] * len(pl0.els)
    for nm, (g, hz, _E) in zip(nazwy, strefy):
        for i in np.nonzero(pl0.elementy_w(g))[0]:
            strefa_el[i] = nm
    # obciążenia (przypadki)
    kd = m.kondygnacja(k0)
    g_pod = 0.0
    if getattr(kd, "podloga", None):
        try:
            g_pod = zestawienie_przegrody(m, kd.podloga, p, tylko="nad").g_k
        except Exception:  # noqa: BLE001
            g_pod = 1.5
    q_uz = obciazenie_uzytkowe("strop", p).q_k
    case_q = {"G": p.ciezar_zelbetu * h_el + g_pod, "QA": np.full(len(h_el), q_uz)}
    case_pts: dict = {}
    for w in m.sciany(k0):
        pr = an.prof.get(w.id)
        if not pr or "dol" not in pr:
            continue
        dol = pr["dol"]
        ds = float(dol.s[1] - dol.s[0])
        for cs in dol.przypadki():
            if cs in ("QA_pA", "QA_pB"):
                continue
            q = dol.get(cs)
            for s_, qq in zip(dol.s, q):
                if abs(qq) > 1e-9:
                    wgt = ds / 2 if (s_ <= 1e-9 or s_ >= dol.L - 1e-9) else ds
                    case_pts.setdefault(cs, []).append((tuple(w.pt(s_, 0.0)), qq * wgt))
    for c in m.slupy():
        if float(c["z_od"]) < spod + h + 0.5 and P.contains(Point(*c["xy"])):
            for cs, N in (an.slupy_N.get(str(c["id"])) or {}).items():
                if cs in ("QA_pA", "QA_pB"):
                    continue
                case_pts.setdefault(cs, []).append((tuple(c["xy"]), N))
    cases = sorted(set(case_q) | set(case_pts))
    fvec = {cs: pl0.wektor(case_q.get(cs, 0.0), punkty=case_pts.get(cs, [])) for cs in cases}
    odz = [Oddz("G", "G")]
    for cs in cases:
        if cs == "G":
            continue
        if cs == "SB2":
            odz.append(Oddz(cs, "A", "S", "dach"))
        else:
            odz.append(Oddz(cs, "Q", {"QA": "A", "H": "H", "S1": "S", "S2": "S"}.get(cs, "A"),
                            "QA" if cs.startswith("QA") else ("dach" if cs in ("H", "S1", "S2") else "")))
    kb_uls = kombinacje(odz, p, "STR")
    kb_chr = kombinacje(odz, p, "char")
    return _obwiednia(pl0, plyty, pod, fvec, kb_uls, kb_chr, e0, P, h, spod, beton, h_el, strefa_el, c_dol, c_gora,
                      fi_zal, an)
