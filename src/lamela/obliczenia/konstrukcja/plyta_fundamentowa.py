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
    w.krok("Współczynnik wpływu (środek prostokąta, m = L/B)", "I_c(m), m = L/B", f"I_c({f(L / B, 3)})", Ic, nd=3,
           zrodlo="Bowles (1996) (5-16a); PN-EN 1997-1 zał. F.2")
    k = Es / (alfa * B * (1 - nu ** 2) * Ic)
    w.krok("Współczynnik podatności (osiadanie średnie α·s_c)", "k_s = E_s/(α·B·(1−ν²)·I_c)",
           f"{f(Es, 0)}/({f(alfa, 2)}·{f(B, 2)}·(1−{f(nu, 2)}²)·{f(Ic, 3)})", k, "kN/m³", nd=0)
    w.krok("Obwiednia wariantów (niepewność modelu Winklera)", "k_s,min = k_s/r; k_s,max = k_s·r",
           f"{f(k, 0)}/{f(rozrzut, 1)}; {f(k, 0)}·{f(rozrzut, 1)}", f"{f(k / rozrzut, 0)}; {f(k * rozrzut, 0)}", "kN/m³", zrodlo="[ZAŁ] Bowles 9.7")
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
    mu_przekr: np.ndarray                # maska: μ > μ_lim — przekrój podwójnie zbrojony (A_s2 w As warstwy przeciwnej)
    p_d_max: float
    p_k_max: float
    w_k_max: float
    oderwanie: float                     # udział powierzchni bez kontaktu (maks. po kombinacjach)
    q_Rd: float
    c_dol: float
    c_gora: float
    wyniki: list = field(default_factory=list)
    kombinacje: int = 0
    As_sc: dict = field(default_factory=dict)   # A_s2 — zbrojenie ściskane (warstwa przeciwna) dla μ > μ_lim [mm²/m]
    p_d_el: np.ndarray | None = None             # obwiednia docisku obliczeniowego w elementach [kPa]
    w_k_el: np.ndarray | None = None             # obwiednia osiadania charakterystycznego w elementach [m] (k_s nominalne)
    V_zeber: dict = field(default_factory=dict)  # id żebra → maks. siła poprzeczna pasma żebra V_Ed [kN] (z dM/ds, ULS)
    M_zeber: dict = field(default_factory=dict)  # id żebra → (M_dół,max; M_góra,min) pasma żebra [kNm]
    q_Rd_lok: float = 0.0
    b_lok: float = 0.0


OKNO_SCIANY = 2.0     # [m] rozdział obciążeń ścian na płytę (średnia krocząca)


def _klasa(model, mat, p):
    from .materialy import klasa_betonu_z_nazwy
    m = model.material(str(mat)) if mat else None
    return klasa_betonu_z_nazwy(m.nazwa if m else str(mat)) or p.beton_dla("fundament")[1]


def _punkty_slupa(an, c) -> list:
    """Punkty przyłożenia siły słupa: słup stalowy — oś; słup/filarek żelbetowy (trzpień) — punkty co ≤ 0,15 m wzdłuż
    dłuższego boku obrysu (siła rozłożona na długości trzpienia) [ZAŁ]."""
    x, y = c["xy"]
    try:
        if not an._slup_zelbetowy(c):
            return [(x, y)]
        from .pozycje import _wymiary_slupa
        a, b = _wymiary_slupa(str(c.get("przekroj")))
    except Exception:  # noqa: BLE001
        return [(x, y)]
    L = max(a, b)
    n = max(int(math.ceil(L / 0.15)), 1)
    ts = [(-L / 2 + (k + 0.5) * L / n) for k in range(n)]
    return [(x + t, y) for t in ts] if a >= b else [(x, y + t) for t in ts]


def _geometria_zeber(pl0, strefa_el, els) -> dict:
    """Pasma żeber (elementy MES strefy żebra) pogrupowane w przekroje poprzeczne wzdłuż osi żebra:
    {id: (kierunek 'x'|'y', współrzędne przekrojów [m], [indeksy elementów przekroju])} — do sił w pasmie żebra."""
    out = {}
    for e in els:
        if "os" not in e:
            continue
        (x0, y0), (x1, y1) = e["os"][0], e["os"][1]
        if math.hypot(x1 - x0, y1 - y0) < float(e.get("b", 0.6)):
            continue                                       # pogrubienie punktowe (stopa) — przebicie, nie ścinanie belkowe
        nm = str(e["id"])
        idx = np.array([i for i, s_ in enumerate(strefa_el) if s_ == nm], int)
        if len(idx) < 4:
            continue
        kier = "x" if abs(x1 - x0) >= abs(y1 - y0) else "y"
        st = np.round(pl0.el_c[idx, 0 if kier == "x" else 1], 4)
        uq = np.unique(st)
        out[nm] = (kier, uq, [idx[st == u] for u in uq])
    return out


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
    # kilka płyt (np. dom + garaż obniżony o uskok nad żebrem): jeden model MES na sumie obrysów — różnica poziomów
    # pominięta w zginaniu płyty (uskok w żebrze) [ZAŁ]; grubość = najmniejsza, grubsze płyty jako strefy; spód do
    # nośności podłoża — najpłytszy (zachowawczo)
    e0 = max(pl_el, key=lambda e_: Polygon(e_["obrys"]).area)
    P = unary_union([Polygon(e_["obrys"]).buffer(0) for e_ in pl_el]).buffer(1e-4, join_style=2).buffer(-1e-4,
                                                                                                        join_style=2)
    if P.geom_type != "Polygon":
        P = max(P.geoms, key=lambda q: q.area)
    h = min(float(e_.get("h", 0.25)) for e_ in pl_el)
    spod = max(float(e_.get("spod", -0.4)) for e_ in pl_el)
    e0 = dict(e0, id="+".join(str(e_.get("id")) for e_ in pl_el))
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
    for e in pl_el:                              # płyty składowe grubsze od najcieńszej — strefy grubości
        if float(e.get("h", h)) > h + 1e-6:
            g = Polygon(e["obrys"]).buffer(0).intersection(P)
            if not g.is_empty:
                strefy.insert(0, (g, float(e["h"]), E))
                nazwy.insert(0, "")          # nie żebro — elementy płyty (siatki), tylko grubość
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
            q0 = dol.get(cs)
            # rozdział obciążenia skupionego przez ścianę i żebro — średnia krocząca OKNO_SCIANY z zachowaniem wypadkowej
            # [UPR — jak w bibliotece dla ław: 2,0 m] — piki profilu (oparcia belek, filarki) nie są osobliwościami
            q = dol.srednia_ruchoma(q0, OKNO_SCIANY) if dol.L > OKNO_SCIANY else np.full_like(q0, q0.mean())
            I0, I1 = float(np.trapezoid(q0, dol.s)), float(np.trapezoid(q, dol.s))
            if abs(I1) > 1e-9:
                q = q * I0 / I1
            for s_, qq in zip(dol.s, q):
                if abs(qq) > 1e-9:
                    wgt = ds / 2 if (s_ <= 1e-9 or s_ >= dol.L - 1e-9) else ds
                    case_pts.setdefault(cs, []).append((tuple(w.pt(s_, 0.0)), qq * wgt))
    for c in m.slupy():
        if float(c["z_od"]) < spod + h + 0.5 and P.contains(Point(*c["xy"])):
            pts = _punkty_slupa(an, c)
            for cs, N in (an.slupy_N.get(str(c["id"])) or {}).items():
                if cs in ("QA_pA", "QA_pB"):
                    continue
                case_pts.setdefault(cs, []).extend((pt, N / len(pts)) for pt in pts)
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


def _obwiednia(pl0, plyty, pod, fvec, kb_uls, kb_chr, e0, P, h, spod, beton, h_el, strefa_el, c_dol, c_gora, fi_zal,
               an) -> WynikPlytyFund:
    from . import fundamenty as fund
    p = an.p
    n = len(pl0.els)
    env = {"dol_x": np.zeros(n), "dol_y": np.zeros(n), "gora_x": np.zeros(n), "gora_y": np.zeros(n)}
    p_d = p_k = w_k = odr = 0.0
    V_d = V_k = 0.0
    p_el = np.zeros(n)
    w_el = np.zeros(n)
    zeb = _geometria_zeber(pl0, strefa_el, an.m.fundamenty().get("elementy") or [])
    V_z = {k: 0.0 for k in zeb}
    M_z = {k: [0.0, 0.0] for k in zeb}
    for kk, pl in plyty.items():
        for kb in kb_uls:
            f_ = sum(a * fvec[c] for c, a in kb.wsp.items() if c in fvec and a)
            r = pl.rozwiaz_kontakt(f_)
            wa = wood_armer(r.wynik.m)
            for key in env:
                env[key] = np.maximum(env[key], wa[key]) if key.startswith("dol") else np.minimum(env[key], wa[key])
            p_d = max(p_d, float(r.p.max()))
            p_el = np.maximum(p_el, r.p)
            odr = max(odr, 1.0 - float((pl.A_el * r.aktywne).sum() / pl.A_el.sum()))
            V_d = max(V_d, float(f_[0::3].sum()))
            for nm, (kier, uq, grp) in zeb.items():
                # pasmo żebra: M(u) = Σ m·szer.; V = |ΔM/Δu| na bazie Δu = d żebra (siła poprzeczna średnia na odcinku d —
                # miarodajna w odległości ≥ d od lica obciążenia skupionego, PN-EN 1992-1-1 6.2.1(8)) [UPR]
                j = 0 if kier == "x" else 1
                Mu = np.array([float((r.wynik.m[g_, j] * pl.el_ab[g_, 1 - j]).sum()) for g_ in grp])
                if len(uq) > 1:
                    dz = max(float(h_el[grp[0]].max()) - c_dol / 1000.0 - 0.02, 0.2)
                    if uq[-1] - uq[0] > dz:
                        ua = np.arange(uq[0], uq[-1] - dz + 1e-9, 0.05)
                        V_z[nm] = max(V_z[nm], float(np.abs(np.interp(ua + dz, uq, Mu) - np.interp(ua, uq, Mu)).max() / dz))
                    else:
                        V_z[nm] = max(V_z[nm], float(np.abs(np.diff(Mu) / np.diff(uq)).max()))
                M_z[nm] = [max(M_z[nm][0], float(Mu.max())), min(M_z[nm][1], float(Mu.min()))]
        for kb in kb_chr:
            f_ = sum(a * fvec[c] for c, a in kb.wsp.items() if c in fvec and a)
            r = pl.rozwiaz_kontakt(f_)
            p_k = max(p_k, float(r.p.max()))
            if abs(kk - pod.k_s) < 1e-6:            # osiadanie — dla k_s nominalnego (warianty — obwiednia sił)
                w_k = max(w_k, float(r.wynik.w.max()))
                w_el = np.maximum(w_el, r.wynik.w[pl.el_nodes].mean(axis=1))
            V_k = max(V_k, float(f_[0::3].sum()))
    # wymiarowanie na zginanie (pasmo b = 1 m, d wg grubości elementu)
    fcd, fyd = beton.f_cd, StalZbrojeniowa(f_yk=p.f_yk, gamma_s=p.gamma_s).f_yd
    xl = StalZbrojeniowa(f_yk=p.f_yk, gamma_s=p.gamma_s).xi_eff_lim(beton)
    mul = xl * (1 - 0.5 * xl)
    # μ > μ_lim → przekrój podwójnie zbrojony: M_lim = μ_lim·b·d²·η·f_cd, ΔM = M − M_lim przenosi para A_s2 (strefa
    # ściskana, warstwa przeciwna) i dodatkowe A_s1; σ_s2 = min(f_yd; E_s·ε_cu3·(1 − a₂/x_lim)), x_lim = ξ_eff,lim·d/λ.
    As, mu_x, As_sc = {}, np.zeros(n, bool), {}
    d_min = None
    Es_st = 200000.0
    for key, M in env.items():
        c = (c_dol if key.startswith("dol") else c_gora) / 1000.0
        c2 = (c_gora if key.startswith("dol") else c_dol) / 1000.0
        d = h_el - c - fi_zal / 2000.0 - (fi_zal / 1000.0 if key.endswith("y") else 0.0)
        a2 = c2 + fi_zal / 2000.0 + (fi_zal / 1000.0 if key.endswith("y") else 0.0)
        mu = np.abs(M) / (1.0 * d ** 2 * beton.eta * fcd * 1000.0)
        mu_x |= mu > mul
        xi = 1 - np.sqrt(np.clip(1 - 2 * np.minimum(mu, mul), 0.0, None))
        dM = np.maximum(np.abs(M) - mul * d ** 2 * beton.eta * fcd * 1000.0, 0.0)          # [kNm/m]
        x_lim = xl * d / beton.lam
        sig2 = np.minimum(fyd, Es_st * beton.eps_cu3 * np.clip(1.0 - a2 / x_lim, 0.0, None))
        As2 = np.where(dM > 0, dM * 1000.0 / (np.maximum(sig2, 1.0) * np.maximum(d - a2, 1e-3)), 0.0)
        As[key] = xi * 1000.0 * d * 1000.0 * beton.eta * fcd / fyd + As2 * sig2 / fyd
        As_sc[key] = As2
        d_min = d if d_min is None else np.minimum(d_min, d)
    for key in list(As):                    # warstwa przeciwna: max(rozciąganie od M przeciwnego znaku; A_s2)
        wa, kk_ = key.split("_")
        op = ("gora" if wa == "dol" else "dol") + "_" + kk_
        if op in As:
            As[op] = np.maximum(As[op], As_sc[key])
    As_min = np.maximum(0.26 * beton.f_ctm / p.f_yk, 0.0013) * 1000.0 * d_min * 1000.0
    x0, y0, x1, y1 = P.bounds
    # nośność podłoża (DA2*): całość płyty + lokalnie pod żebrem (pasmo b_ż + 2h)
    try:
        zt = min(float(an._teren_przy((x, y))) for x, y in list(P.exterior.coords)[:-1])
    except Exception:  # noqa: BLE001
        zt = 0.0
    Dz = max(zt - spod, 0.3)
    wyniki = [pod]
    nos = fund.nosnosc_podloza(x1 - x0, Dz, V_k, V_d, p.grunt, p, L=y1 - y0,
                               nazwa="Nośność podłoża pod płytą fundamentową (PN-EN 1997-1 zał. D, DA2*)")
    wyniki.append(nos)
    q_Rd = nos.R_d / max(nos.B_ef * nos.L_ef, 1e-9)
    b_loc = min((e_.get("b", 0.6) for e_ in (an.m.fundamenty().get("elementy") or []) if "os" in e_), default=0.6) + 2 * h
    loc = fund.nosnosc_podloza(b_loc, Dz, p_d * b_loc, p_d * b_loc, p.grunt, p,
                               nazwa=f"Nacisk lokalny — maks. docisk MES p_d pod pasmem b = {f(b_loc)} m (żebro + 2h)")
    loc.warunki.clear()
    q_Rd_loc = loc.R_d / b_loc
    loc.krok("Maks. docisk obliczeniowy z MES (obwiednia k_s, kombinacje STR/GEO)", "p_d,max", "", p_d, "kPa", nd=1)
    loc.warunek("Docisk lokalny do podłoża (pasmo pod żebrem)", p_d, q_Rd_loc, "kPa", "PN-EN 1997-1 6.5.2, zał. D",
                nd=1, symbol_E="p_d,max", symbol_R="q_Rd")
    wyniki.append(loc)
    wo = Wynik(nazwa="Odrywanie płyty od podłoża i osiadanie (MES, kontakt jednostronny)")
    wo.krok("Udział powierzchni bez kontaktu (maks. po kombinacjach ULS i wariantach k_s)", "A_oder/A", "", odr * 100, "%",
            nd=1)
    wo.krok("Maks. docisk charakterystyczny (SLS)", "p_k,max", "", p_k, "kPa", nd=1)
    wo.krok("Maks. osiadanie sprężyste (SLS, k_s nominalne)", "w_k,max", "", w_k * 1000, "mm", nd=1)
    wo.warunek("Osiadanie (PN-EN 1997-1 zał. H: s ≤ 50 mm dla fundamentów bezpośrednich)", w_k * 1000, 50.0, "mm",
               "PN-EN 1997-1 zał. H", nd=1, symbol_E="w_k", symbol_R="s_dop")
    wyniki.append(wo)
    W = WynikPlytyFund(str(e0.get("id")), P, h, spod, beton, pod, pl0.el_c.copy(), pl0.el_ab.copy(), h_el, strefa_el, env,
                       As, As_min, mu_x, p_d, p_k, w_k, odr, q_Rd, c_dol, c_gora, wyniki, len(kb_uls) * len(plyty))
    W.As_sc = As_sc
    W.p_d_el, W.w_k_el, W.V_zeber, W.M_zeber = p_el, w_el, V_z, {k: tuple(v) for k, v in M_z.items()}
    W.q_Rd_lok, W.b_lok = q_Rd_loc, b_loc
    W.wyniki += przebicie_slupow(an, W, plyty, fvec, kb_uls)
    return W


def przebicie_slupow(an, W: WynikPlytyFund, plyty, fvec, kb_uls) -> list:
    """Przebicie płyty/pogrubienia pod słupami (PN-EN 1992-1-1 6.4.4(2)): v_Ed = V_Ed,red/(u·d) ≤ v_Rd = C_Rd,c·k·
    (100ρf_ck)^(1/3)·2d/a ≥ v_min·2d/a; V_Ed,red = V_Ed − p·A(a); a ∈ (0; 2d] — wartość miarodajna (min v_Rd/v_Ed)."""
    from .materialy import pole_preta
    m, p = an.m, an.p
    out = []
    bt = W.beton
    for c in m.slupy():
        xy = c["xy"]
        if not (float(c["z_od"]) < W.spod + W.h + 0.5 and W.obrys.contains(Point(*xy))):
            continue
        N = an.slupy_N.get(str(c["id"])) or {}
        V = max((sum(a * N.get(cs, 0.0) for cs, a in kb.wsp.items()) for kb in kb_uls), default=0.0)
        i = int(np.argmin(np.hypot(W.el_c[:, 0] - xy[0], W.el_c[:, 1] - xy[1])))
        ht = float(W.h_el[i])
        d = ht - W.c_dol / 1000.0 - 0.012
        c1 = c2 = 0.12 + 2 * 0.05                  # słup stalowy: przekrój + blacha podstawy (wysięg 5 cm) [ZAŁ]
        bl = c.get("blacha_dolna")
        if isinstance(bl, dict):
            c1, c2 = float(bl.get("a", c1)), float(bl.get("b", c2))
        if an._slup_zelbetowy(c):
            from .pozycje import _wymiary_slupa
            c1, c2 = _wymiary_slupa(str(c.get("przekroj")))
            c2 = min(c2, 3 * c1) if c2 > c1 else c2  # wydłużony trzpień: długość czynna ≤ 3·grubość [ZAŁ, por. 6.4.2(3)]
            c1 = min(c1, 3 * c2) if c1 > c2 else c1
        rho = 0.002
        k = min(1 + math.sqrt(200 / (d * 1000)), 2.0)
        vmin = 0.035 * k ** 1.5 * math.sqrt(bt.f_ck)
        pmin = 0.0                                 # bezpiecznie: bez redukcji odporem gruntu przy braku docisku
        best = None
        for a in np.linspace(0.1 * d, 2 * d, 20):
            u = 2 * (c1 + c2) + 2 * math.pi * a
            A = c1 * c2 + 2 * (c1 + c2) * a + math.pi * a * a
            Vr = max(V - pmin * A, 0.0)
            vEd = Vr / (u * d) / 1000.0
            vRd = max(0.18 / bt.gamma_c * k * (100 * rho * bt.f_ck) ** (1 / 3), vmin) * 2 * d / a
            eta = vEd / vRd if vRd > 0 else 0.0
            if best is None or eta > best[0]:
                best = (eta, a, vEd, vRd, u)
        w = Wynik(nazwa=f"Przebicie płyty pod słupem {c['id']} (6.4.4(2))")
        w.krok("Siła od słupa (obwiednia ULS)", "V_Ed", "", V, "kN", nd=1)
        w.krok("Wysokość użyteczna w strefie słupa", "d", f"h = {f(ht, 2)} m", d * 1000, "mm", nd=0)
        w.krok("Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem)", "a; u", "",
               f"{f(best[1], 3)} m; {f(best[4], 3)} m")
        w.warunek("Przebicie — fundament (6.4.4(2), (6.51)–(6.53))", best[2], best[3], "MPa", "PN-EN 1992-1-1 6.4.4",
                  nd=3, symbol_E="v_Ed", symbol_R="v_Rd")
        out.append(w)
    return out
