"""Geometria przekrojów węzłów (mostki cieplne 2D wg PN-EN ISO 10211:2017).

Przekrój węzła = zbiór wieloboków shapely z materiałami (λ) + strefy brzegowe (powietrze wewnętrzne, zewnętrzne,
pomieszczenie nieogrzewane) z temperaturą i oporem przejmowania R_s. Komórki siatki leżące poza materiałami i poza
strefami są „pustką” — ściany do pustki (płaszczyzny odcięcia, osie symetrii) są adiabatyczne.

Konwencje:
* jednostki: m, W/(m·K), m²·K/W, °C; współrzędne (x, y) przekroju — x poziomo, y pionowo (przekrój pionowy)
  albo x, y w rzucie (przekrój poziomy, `przekroj="poziomy"` — wszystkie powierzchnie są pionowe, R_si „poziomo”);
* kolejność `Wezel.obszary` = priorytet: obszar późniejszy nadpisuje wcześniejszy (np. łącznik termoizolacyjny na płycie,
  budynek na gruncie);
* strefy grupuje pole `grupa` (ta sama temperatura, np. „i” — pomieszczenia ogrzewane nad i pod stropem);
  współczynniki sprzężenia L_2D liczone są między grupami (PN-EN ISO 10211 — więcej niż dwie temperatury brzegowe);
* warstwy przegród jak w modelu (`docs/SCHEMAT_MODELU.md`): ściany od WNĘTRZA do ZEWNĄTRZ, poziome od GÓRY do DOŁU.

Opory przejmowania (PN-EN ISO 6946:2017; PN-EN ISO 10211:2017; PN-EN ISO 13788:2013):
R_se = 0,04; R_si = 0,13 (poziomo), 0,10 (w górę), 0,17 (w dół) — do strumieni i ψ; R_si = 0,25 do oceny temperatury
powierzchni (f_Rsi), 0,13 dla ram i szyb.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

# --------------------------------------------------------------------------------------------------
# Stałe
# --------------------------------------------------------------------------------------------------
RSE = 0.04
RSI_POZIOMO, RSI_GORA, RSI_DOL = 0.13, 0.10, 0.17
RS_ISO6946_WEWN = {"poziomo": RSI_POZIOMO, "gora": RSI_GORA, "dol": RSI_DOL}
RSI_13788 = 0.25            # ocena temperatury powierzchni (przegrody nieprzezroczyste)
RSI_13788_OKNA = 0.13       # ramy i szyby
SIGMA = 5.67e-8             # W/(m²·K⁴)
LAMBDA_GRUNTU = 2.0         # W/(m·K) — PN-EN ISO 13370:2017 (piasek/żwir) / PN-EN ISO 10211:2017 (grunt) [NZW]
B_DOMYSLNE = 8.0            # m — szerokość budynku do modelu gruntu 2D, gdy nieznana (PN-EN ISO 10211 — wymiary obszaru gruntu) [NZW]


# --------------------------------------------------------------------------------------------------
# Materiały, warstwy
# --------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Material:
    kod: str
    lam: float
    nazwa: str = ""
    kolor: str | None = None
    rodzaj: str = "nieprzezroczysty"      # nieprzezroczysty | rama | szyba | grunt | powietrze
    zrodlo: str = ""

    def __post_init__(self):
        if not (self.lam > 0 and math.isfinite(self.lam)):
            raise ValueError(f"Materiał {self.kod}: λ musi być > 0 (jest {self.lam})")


@dataclass
class Warstwa:
    mat: Material
    d: float
    konstrukcyjna: bool = False

    @property
    def R(self) -> float:
        return self.d / self.mat.lam


def R_warstw(warstwy: Sequence[Warstwa]) -> float:
    return sum(w.R for w in warstwy)


def U_warstw(warstwy: Sequence[Warstwa], Rsi: float = RSI_POZIOMO, Rse: float = RSE) -> float:
    """U przegrody jednorodnej warstwowo (1D): 1/(R_si + Σ d/λ + R_se)."""
    return 1.0 / (Rsi + R_warstw(warstwy) + Rse)


def grubosc(warstwy: Sequence[Warstwa]) -> float:
    return sum(w.d for w in warstwy)


def indeks_konstrukcyjnej(warstwy: Sequence[Warstwa]) -> int:
    """Indeks warstwy konstrukcyjnej (pole `konstrukcyjna`, inaczej najgrubsza o λ ≥ 0,1)."""
    for i, w in enumerate(warstwy):
        if w.konstrukcyjna:
            return i
    kand = [(w.d, i) for i, w in enumerate(warstwy) if w.mat.lam >= 0.1]
    if not kand:
        kand = [(w.d, i) for i, w in enumerate(warstwy)]
    return max(kand)[1]


# materiały domyślne (gdy model ich nie zawiera); λ — wartości obliczeniowe typowe (PN-EN ISO 10456 / karty wyrobów)
def _m(kod, lam, nazwa, kolor=None, rodzaj="nieprzezroczysty", zrodlo="PN-EN ISO 10456:2009 tab. 3 / typowe karty wyrobów [NZW]"):
    return Material(kod, lam, nazwa, kolor, rodzaj, zrodlo)


MATERIALY_DOMYSLNE: dict[str, Material] = {m.kod: m for m in [
    _m("GRUNT", LAMBDA_GRUNTU, "Grunt (piasek/żwir) λ = 2,0", "#c8b48a", "grunt",
       "PN-EN ISO 10211:2017 / PN-EN ISO 13370:2017 — grunt jednorodny λ = 2,0 [NZW]"),
    _m("ZB", 2.3, "Żelbet (1 % zbrojenia)", "#b9b6ae", zrodlo="PN-EN ISO 10456:2009 tab. 3"),
    _m("BETON", 2.0, "Beton zwykły", "#c4c1b8", zrodlo="PN-EN ISO 10456:2009 tab. 3"),
    _m("BET_FUND", 1.7, "Bloczek betonowy fundamentowy (pełny)", "#bdb8ad"),
    _m("SIL24", 0.90, "Bloczek wapienno-piaskowy 24 cm (ściana garażu)", "#d9d4ca"),
    _m("XPS", 0.035, "Polistyren ekstrudowany XPS (izolacja obwodowa)", "#9cc7a4"),
    _m("EPS_P", 0.035, "Styropian EPS-P (hydro, cokół)", "#b8c9d6"),
    _m("PIANKA_PU", 0.040, "Pianka PU montażowa (szczelina)", "#efe3a0"),
    _m("HYDRO", 0.23, "Hydroizolacja bitumiczna / KMB", "#3a3a3a"),
    _m("TYNK_CEM", 1.0, "Tynk cementowo-wapienny", "#e8e4dc"),
    _m("BET_KOM_400", 0.11, "Beton komórkowy 400 (blok termiczny)", "#e6e1d6"),
    _m("ALU", 160.0, "Aluminium (stop)", "#9aa3ab"),
    _m("STAL", 50.0, "Stal", "#555a60"),
]}

# łącznik termoizolacyjny płyty wspornikowej — λ_eq modułu izolacyjnego z prętami (DANE PRZYKŁADOWE)
LACZNIK_PRZYKLAD = Material(
    "LACZNIK_80", 0.09, "Łącznik termoizolacyjny 80 mm (moduł izolacyjny + pręty nierdzewne), λ_eq", "#d1495b",
    zrodlo="[DANE PRZYKŁADOWE – FIKCYJNE] λ_eq typowej deklaracji (ETA) łącznika 80 mm do płyt 20–22 cm; "
           "do zastąpienia wartością z ETA wybranego wyrobu (W-272)")


def material_rama(U_f: float, d_f: float, Rsi: float = RSI_POZIOMO, Rse: float = RSE, kod: str = "RAMA",
                  nazwa: str | None = None, zrodlo: str = "") -> Material:
    """Rama okna jako materiał jednorodny o λ_eq = d_f / (1/U_f − R_si − R_se) (uproszczenie; ISO 10077-2 — rama
    szczegółowa). d_f — grubość ramy w kierunku przepływu ciepła."""
    R = 1.0 / U_f - Rsi - Rse
    if R <= 0:
        raise ValueError("U_f zbyt duże dla zadanych R_s")
    return Material(kod, d_f / R, nazwa or f"Rama okna (λ_eq z U_f = {U_f} W/(m²K), d_f = {d_f} m)", "#6b7b8c",
                    "rama", zrodlo or "λ_eq z U_f (PN-EN ISO 10077-2 — wartość deklarowana)")


def material_szyba(U_g: float, d_g: float, Rsi: float = RSI_POZIOMO, Rse: float = RSE, kod: str = "SZYBA",
                   zrodlo: str = "") -> Material:
    """Pakiet szybowy jako płyta zastępcza λ_eq = d_g / (1/U_g − R_si − R_se) (PN-EN ISO 10077-2 — płyta zastępcza szyby)."""
    R = 1.0 / U_g - Rsi - Rse
    return Material(kod, d_g / R, f"Pakiet szybowy (λ_eq z U_g = {U_g} W/(m²K), d = {d_g} m)", "#a8d0e6", "szyba",
                    zrodlo or "PN-EN ISO 10077-2:2017 (płyta zastępcza szyby)")


# --------------------------------------------------------------------------------------------------
# Pustki powietrzne niewentylowane — PN-EN ISO 6946:2017 zał. D
# --------------------------------------------------------------------------------------------------
def h_r0(theta_m: float = 10.0) -> float:
    """Współczynnik promieniowania ciała czarnego h_r0 = 4σT_m³ (ISO 6946 zał. D, tab. D.1: 5,1 przy 10 °C)."""
    return 4.0 * SIGMA * (theta_m + 273.15) ** 3


def h_a_pustki(d: float, kierunek: str = "poziomo", dT: float = 5.0) -> float:
    """Konwekcja/przewodzenie w pustce (ISO 6946 zał. D.2): poziomo max(1,25; 0,025/d); w górę max(1,95; 0,025/d);
    w dół max(0,12·d^−0,44; 0,025/d) [W/(m²K)] (ΔT ≤ 5 K)."""
    cond = 0.025 / d
    if kierunek == "poziomo":
        return max(1.25, cond)
    if kierunek == "gora":
        return max(1.95, cond)
    if kierunek == "dol":
        return max(0.12 * d ** -0.44, cond)
    raise ValueError(kierunek)


def lambda_eq_pustki(d: float, kierunek: str = "poziomo", eps1: float = 0.9, eps2: float = 0.9,
                     theta_m: float = 10.0, b: float | None = None) -> float:
    """λ_eq niewentylowanej warstwy powietrza grubości d (kierunek przepływu ciepła) wg ISO 6946:2017 zał. D:
    R_g = 1/(h_a + h_r); h_r = E·h_r0, E = 1/(1/ε1 + 1/ε2 − 1). Dla małych pustek (szerokość b < 10·d, zał. D.4):
    h_r = h_r0 / (1/ε1 + 1/ε2 − 2 + 2/(1 + √(1 + d²/b²) − d/b)). Zwraca λ_eq = d / R_g."""
    hr0 = h_r0(theta_m)
    if b is not None and b < 10 * d:
        hr = hr0 / (1 / eps1 + 1 / eps2 - 2 + 2 / (1 + math.sqrt(1 + d * d / (b * b)) - d / b))
    else:
        hr = hr0 / (1 / eps1 + 1 / eps2 - 1)
    Rg = 1.0 / (h_a_pustki(d, kierunek) + hr)
    return d / Rg


def material_pustki(d: float, kierunek: str = "poziomo", eps1: float = 0.9, eps2: float = 0.9,
                    b: float | None = None, kod: str = "POWIETRZE") -> Material:
    lam = lambda_eq_pustki(d, kierunek, eps1, eps2, b=b)
    return Material(kod, lam, f"Pustka niewentylowana d = {d * 1000:.0f} mm ({kierunek}), λ_eq = {lam:.3f}", "#ffffff",
                    "powietrze", "PN-EN ISO 6946:2017 zał. D")


# --------------------------------------------------------------------------------------------------
# Obszary, strefy, elementy flankujące, węzeł
# --------------------------------------------------------------------------------------------------
@dataclass
class Obszar:
    wielobok: BaseGeometry
    mat: Material
    nazwa: str = ""


@dataclass
class Strefa:
    """Strefa brzegowa (powietrze) — warunek III rodzaju (Robin): q = (θ − θ_s)/R_s.
    rodzaj: 'wewn' (ogrzewana), 'zewn', 'nieogrz' (pomieszczenie nieogrzewane). Rs: liczba, słownik kierunkowy
    {'poziomo','gora','dol'} (kierunek strumienia wyznaczany z rozwiązania) albo None (domyślnie: zewn → 0,04;
    wewn/nieogrz → R_si wg ISO 6946). Rs = 0 → zadana temperatura powierzchni (warunek I rodzaju)."""
    nazwa: str
    wielobok: BaseGeometry
    theta: float
    rodzaj: str = "wewn"
    grupa: str | None = None
    Rs: float | dict | None = None

    def __post_init__(self):
        if self.grupa is None:
            self.grupa = {"wewn": "i", "zewn": "e", "nieogrz": "u"}.get(self.rodzaj, self.nazwa)
        if self.Rs is None:
            self.Rs = RSE if self.rodzaj == "zewn" else dict(RS_ISO6946_WEWN)


@dataclass
class ElementFlankujacy:
    """Element flankujący do ψ = L_2D − Σ U_j·l_j (PN-EN ISO 10211 / PN-EN ISO 14683).
    U — podane albo liczone z `warstwy` (1D, te same R_s co w modelu 2D); `wezel_ref` — podmodel, którego L_2D
    zastępuje U·l (np. okno bez ściany — ψ osadzenia); długości wg systemów wymiarów (PN-EN ISO 13789 / 14683):
    `l_e` — zewnętrzne, `l_i` — wewnętrzne (bez grubości stropów), `l_oi` — wewnętrzne całkowite (wysokości „od
    podłogi do podłogi”, pod dachem do spodu płyty; długości po licach wewnętrznych; okna w świetle otworu w murze —
    system stosowany w `energia.bryla` / `fizyka.mostki`); None → l_i."""
    nazwa: str
    grupy: tuple[str, str]
    l_e: float
    l_i: float
    U: float | None = None
    warstwy: list[Warstwa] | None = None
    Rsi: float = RSI_POZIOMO
    Rse: float = RSE
    wezel_ref: "Wezel | None" = None
    zrodlo: str = ""
    l_oi: float | None = None

    @property
    def l_oi_(self) -> float:
        return self.l_i if self.l_oi is None else self.l_oi

    def U_obl(self) -> float | None:
        if self.U is not None:
            return self.U
        if self.warstwy:
            return U_warstw(self.warstwy, self.Rsi, self.Rse)
        return None


@dataclass
class Wezel:
    id: str
    nazwa: str
    typ: str
    obszary: list[Obszar]
    strefy: list[Strefa]
    flankujace: list[ElementFlankujacy] = field(default_factory=list)
    przekroj: str = "pionowy"                     # pionowy | poziomy (rzut)
    punkty: dict[str, tuple[float, float]] = field(default_factory=dict)
    siatka: dict = field(default_factory=dict)    # h_min, h_max, r, n_min
    widok: tuple[float, float, float, float] | None = None
    psi_domyslne: str | None = None               # klucz PSI_DOMYSLNE_14683
    psi_deklarowane: dict | None = None           # np. {'psi': 0.15, 'zrodlo': '...'} (deklaracja wyrobu)
    opis: str = ""
    dane: dict = field(default_factory=dict)      # dane wejściowe do raportu
    uwagi: list[str] = field(default_factory=list)
    dopusc_pustki: bool = False                   # True — celowe wcięcia adiabatyczne (wyłącza kontrolę szczelin)

    # ---- pomocnicze
    def materialy(self) -> list[Material]:
        out: dict[str, Material] = {}
        for o in self.obszary:
            out.setdefault(o.mat.kod, o.mat)
        return list(out.values())

    def grupy(self) -> list[str]:
        g: list[str] = []
        for s in self.strefy:
            if s.grupa not in g:
                g.append(s.grupa)
        return g

    def theta_grup(self) -> dict[str, float]:
        return {s.grupa: s.theta for s in self.strefy}

    def bounds(self) -> tuple[float, float, float, float]:
        geoms = [o.wielobok for o in self.obszary] + [s.wielobok for s in self.strefy]
        return unary_union(geoms).bounds


# --------------------------------------------------------------------------------------------------
# Wartości domyślne ψ wg PN-EN ISO 14683 — do porównania (ORIENTACYJNE)
# --------------------------------------------------------------------------------------------------
# UWAGA: tekst normy niedostępny (rejestr wymagań R6-32, D-19). Wartości orientacyjne z pamięci/źródeł wtórnych
# (ISO 14683:2007 tab. A.2 ≈ ISO 14683:2017 zał. C) — status [NZW]; przed wydaniem PT zweryfikować z egzemplarzem normy.
PSI_DOMYSLNE_14683: dict[str, dict[str, Any]] = {
    "B_balkon": {"opis": "płyta balkonowa ciągła przez izolację (B)", "psi_e": 0.95, "psi_i": 0.95,
                 "status": "[NZW]", "zrodlo": "ISO 14683 (streszczenie wtórne, rejestr R6-32)"},
    "IF_strop": {"opis": "strop pośredni, izolacja zewnętrzna ciągła (IF)", "psi_e": 0.00, "psi_i": 0.10,
                 "status": "[NZW]", "zrodlo": "ISO 14683 zał. C — wartość orientacyjna"},
    "C_naroze_zewn": {"opis": "naroże zewnętrzne, izolacja zewnętrzna (C)", "psi_e": -0.10, "psi_i": 0.15,
                      "status": "[NZW]", "zrodlo": "ISO 14683 zał. C — wartość orientacyjna"},
    "R_attyka": {"opis": "dach płaski–ściana z attyką, izolacja ciągła (R)", "psi_e": 0.55, "psi_i": 0.75,
                 "status": "[NZW]", "zrodlo": "ISO 14683 zał. C — wartość orientacyjna"},
    "GF_cokol": {"opis": "ściana–podłoga na gruncie (GF)", "psi_e": 0.60, "psi_i": 0.80,
                 "status": "[NZW]", "zrodlo": "ISO 14683 zał. C — wartość orientacyjna"},
    "W_oscieze": {"opis": "ościeże okna, rama w płaszczyźnie izolacji (W)", "psi_e": 0.10, "psi_i": 0.10,
                  "status": "[NZW]", "zrodlo": "ISO 14683 zał. C — wartość orientacyjna"},
}


# --------------------------------------------------------------------------------------------------
# Pomocnicze do budowy węzłów
# --------------------------------------------------------------------------------------------------
S_STREFY = 0.05     # grubość pasów stref brzegowych [m]


def odl_ciecia(d_elementu: float, minimum: float = 1.0) -> float:
    """Odległość płaszczyzny odcięcia od elementu centralnego: max(1 m, 3·d elementu flankującego)
    (PN-EN ISO 10211:2017 — płaszczyzny odcięcia)."""
    return max(minimum, 3.0 * d_elementu)


def _stos(warstwy: Sequence[Warstwa], start: float, znak: int = +1) -> list[tuple[float, float, Warstwa]]:
    out = []
    p = start
    for w in warstwy:
        q = p + znak * w.d
        out.append((min(p, q), max(p, q), w))
        p = q
    return out


def strefy_z_dopelnienia(obszary: Sequence[Obszar], ramka: Polygon,
                         nasiona: Sequence[tuple[tuple[float, float], dict]]) -> list[Strefa]:
    """Strefy = spójne składowe (ramka − materiały) zawierające punkt-nasiono; pozostałe składowe → pustka.
    nasiona: [((x, y), {nazwa, theta, rodzaj, grupa?, Rs?}), ...]."""
    solid = unary_union([o.wielobok for o in obszary]).buffer(1e-9, join_style="mitre")
    wolne = ramka.difference(solid)
    czesci = list(getattr(wolne, "geoms", [wolne]))
    out: list[Strefa] = []
    for (xy, kw) in nasiona:
        p = Point(xy)
        kand = [c for c in czesci if c.covers(p)]
        if not kand:
            raise ValueError(f"Nasiono strefy {kw.get('nazwa')} {xy} nie leży w wolnej przestrzeni ramki")
        out.append(Strefa(wielobok=kand[0], **kw))
    return out


def dane_warstw(warstwy: Sequence[Warstwa]) -> list[list[Any]]:
    return [[w.mat.kod, w.mat.nazwa, w.d, w.mat.lam, w.R] for w in warstwy]


# --------------------------------------------------------------------------------------------------
# Połączenie z modelem budynku (lamela.model)
# --------------------------------------------------------------------------------------------------
def material_z_modelu(model, kod: str) -> Material:
    if kod in MATERIALY_DOMYSLNE and (model is None or kod not in getattr(model, "materialy", {})):
        return MATERIALY_DOMYSLNE[kod]
    m = model.material(kod)
    nazwa = m.nazwa or kod
    rodzaj = "nieprzezroczysty"
    n = nazwa.lower()
    if bool(getattr(m, "wentylowana", False)) or "wentylowan" in n and "niewentylowan" not in n:
        rodzaj = "powietrze_went"          # warstwa powietrza dobrze wentylowana (ISO 6946) — pomijana w U i w 2D
    elif any(k in n for k in ("pustk", "powietrz", "szczelin")):
        rodzaj = "powietrze"               # niewentylowana — λ_eq z modelu (ISO 6946 zał. D)
    return Material(kod, float(m.lambda_), nazwa, getattr(m, "kolor", None), rodzaj,
                    "model budynku (materialy.*.lambda)")


def warstwy_z_modelu(model, kod_przegrody: str) -> list[Warstwa]:
    """Warstwy przegrody z modelu (`m.przegroda(kod).warstwy`) → lista `Warstwa` (kolejność jak w modelu)."""
    p = model.przegroda(kod_przegrody)
    return [Warstwa(material_z_modelu(model, w.mat), float(w.d), bool(w.konstrukcyjna)) for w in p.warstwy]


def ma_pustke_wentylowana(warstwy: Sequence[Warstwa]) -> bool:
    return any(w.mat.rodzaj == "powietrze_went" for w in warstwy)


def pomin_pustki_wentylowane(warstwy: Sequence[Warstwa], zewn_na_poczatku: bool = True) -> list[Warstwa]:
    """Pustkę dobrze wentylowaną (rodzaj 'powietrze_went') i warstwy za nią (po stronie zewnętrznej) pomija się
    (PN-EN ISO 6946:2017 — warstwy dobrze wentylowane). Warstwy powietrza niewentylowane ('powietrze', λ_eq)
    pozostają — tak samo w U i w modelu 2D.
    zewn_na_poczatku=True — lista od góry (dachy, tarasy: strona zewnętrzna pierwsza); False — ściany (od wnętrza)."""
    lista = list(warstwy) if zewn_na_poczatku else list(reversed(warstwy))
    out: list[Warstwa] = []
    for w in lista:
        if w.mat.rodzaj == "powietrze_went":
            out = []
            continue
        out.append(w)
    return out if zewn_na_poczatku else list(reversed(out))


# ==================================================================================================
# Budowa typowych węzłów (przekroje 2D) z przegród modelu
# ==================================================================================================
def _temperatury(theta_i: float | None, theta_e: float | None) -> tuple[float, float]:
    """θ_i, θ_e: argumenty albo wymagania.yaml (W-150: +20 °C / −18 °C)."""
    ti, te = 20.0, -18.0
    try:
        from ..wspolne import wym
        ti = float(wym("ogrzewanie", "theta_i_pokoj_hol_kuchnia", 20.0))
        te = float(wym("ogrzewanie", "theta_e", -18.0))
    except Exception:   # pragma: no cover — biblioteka wspólna niedostępna
        pass
    return (ti if theta_i is None else theta_i), (te if theta_e is None else theta_e)


def _nas(nazwa: str, theta: float, rodzaj: str, grupa: str | None = None, Rs=None) -> dict:
    d: dict[str, Any] = {"nazwa": nazwa, "theta": theta, "rodzaj": rodzaj}
    if grupa:
        d["grupa"] = grupa
    if Rs is not None:
        d["Rs"] = Rs
    return d


def _obsz(geom, w_or_mat, nazwa: str = "") -> Obszar:
    mat = w_or_mat.mat if isinstance(w_or_mat, Warstwa) else w_or_mat
    return Obszar(geom, mat, nazwa or mat.nazwa)


def _izolacja_najlepsza(warstwy: Sequence[Warstwa]) -> Material:
    return min(warstwy, key=lambda w: w.mat.lam).mat


def wezel_sciana_1d(warstwy: Sequence[Warstwa], H: float = 1.0, theta_i: float | None = None,
                    theta_e: float | None = None, id: str = "SC-1D", nazwa: str | None = None) -> Wezel:
    """Ściana warstwowa (przekrój poziomy, pas wysokości H) — test spójności (ψ ≈ 0)."""
    ti, te = _temperatury(theta_i, theta_e)
    ob = [_obsz(box(a, 0, b, H), w) for a, b, w in _stos(warstwy, 0.0)]
    D = grubosc(warstwy)
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-S, 0, D + S, H),
                                  [((-S / 2, H / 2), _nas("wnętrze", ti, "wewn")),
                                   ((D + S / 2, H / 2), _nas("zewnętrze", te, "zewn"))])
    fl = [ElementFlankujacy("ściana", ("i", "e"), H, H, warstwy=list(warstwy), Rsi=RSI_POZIOMO)]
    return Wezel(id, nazwa or "Ściana warstwowa (1D)", "sciana", ob, strefy, fl, przekroj="poziomy",
                 dane={"warstwy ściany": dane_warstw(warstwy)})


def wezel_naroznik_zewnetrzny(warstwy: Sequence[Warstwa], L: float | None = None, theta_i: float | None = None,
                              theta_e: float | None = None, id: str = "WZ-C1",
                              nazwa: str = "Narożnik zewnętrzny ścian (rzut)") -> Wezel:
    """Naroże zewnętrzne dwóch jednakowych ścian (rzut). Naroże wewnętrzne w (0, 0), wnętrze x < 0, y < 0.
    Warstwy łączone „na kwadrat” (offset Czebyszewa) — ETICS ciągły, konstrukcja w L."""
    ti, te = _temperatury(theta_i, theta_e)
    D = grubosc(warstwy)
    L = L or (odl_ciecia(D) + D)
    ob = []
    for a, b, w in _stos(warstwy, 0.0):
        g = box(-L, -L, b, b).difference(box(-L - 1, -L - 1, a, a))
        ob.append(_obsz(g, w))
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-L, -L, D + S, D + S),
                                  [((-L / 2, -L / 2), _nas("wnętrze", ti, "wewn")),
                                   ((D + S / 2, -L / 2), _nas("zewnętrze", te, "zewn"))])
    fl = [ElementFlankujacy("ściana A (oś x)", ("i", "e"), L + D, L, warstwy=list(warstwy)),
          ElementFlankujacy("ściana B (oś y)", ("i", "e"), L + D, L, warstwy=list(warstwy))]
    return Wezel(id, nazwa, "naroze", ob, strefy, fl, przekroj="poziomy",
                 punkty={"naroże wewn.": (0.0, 0.0), "naroże zewn.": (D, D)},
                 widok=(-min(L, 1.2), -min(L, 1.2), D + 0.1, D + 0.1), psi_domyslne="C_naroze_zewn",
                 opis="Rzut naroża zewnętrznego; płaszczyzny odcięcia adiabatyczne w odległości L od naroża wewn.",
                 dane={"warstwy ściany": dane_warstw(warstwy), "L odcięcia [m]": L})


def wezel_wspornik(warstwy_sciany: Sequence[Warstwa], t_plyty: float = 0.20, mat_plyty: Material | None = None,
                   warstwy_podlogi: Sequence[Warstwa] = (), warstwy_sufitu: Sequence[Warstwa] = (),
                   wysieg: float = 1.5, lacznik: Material | None = LACZNIK_PRZYKLAD, d_lacznika: float = 0.08,
                   H: float | None = None, L_in: float | None = None, theta_i: float | None = None,
                   theta_e: float | None = None, id: str = "WZ-B1", nazwa: str | None = None) -> Wezel:
    """Ściana warstwowa + strop przechodzący przez ścianę (przekrój pionowy). wysieg > 0 — płyta wspornikowa
    (balkon/taras/okap) wysunięta poza lico elewacji, w płaszczyźnie izolacji łącznik termoizolacyjny (λ_eq,
    grubość d_lacznika) albo płyta ciągła (lacznik=None); wysieg = 0 — strop pośredni z wieńcem (izolacja ciągła).
    Wnętrze x < 0 (lico wewn. ściany x = 0), płyta konstrukcyjna y ∈ [0, t_plyty]."""
    ti, te = _temperatury(theta_i, theta_e)
    mat_plyty = mat_plyty or MATERIALY_DOMYSLNE["ZB"]
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    x_s1 = st[ks][1]
    x_out = st[-1][1]
    t = t_plyty
    t_pod, t_suf = grubosc(warstwy_podlogi), grubosc(warstwy_sufitu)
    H = H or odl_ciecia(x_out)
    L_in = L_in or odl_ciecia(t)
    x_end = x_s1 if wysieg <= 0 else x_out + wysieg
    ob: list[Obszar] = []
    for k, (a, b, w) in enumerate(st):
        if k <= ks:
            ob.append(_obsz(box(a, -H, b, 0.0), w))
            ob.append(_obsz(box(a, t, b, t + H), w))
        else:
            ob.append(_obsz(box(a, -H, b, t + H), w))
    for y0, y1, w in _stos(warstwy_podlogi, t + t_pod, -1):
        ob.append(_obsz(box(-L_in, y0, 0.0, y1), w))
    for y0, y1, w in _stos(warstwy_sufitu, 0.0, -1):
        ob.append(_obsz(box(-L_in, y0, 0.0, y1), w))
    ob.append(_obsz(box(-L_in, 0.0, x_end, t), mat_plyty, "płyta stropu" + (" / wspornik" if wysieg > 0 else "")))
    if wysieg > 0 and lacznik is not None:
        ob.append(_obsz(box(x_s1, 0.0, x_s1 + d_lacznika, t), lacznik))
    S = S_STREFY
    ramka = box(-L_in, -H, max(x_end, x_out) + S, t + H)
    strefy = strefy_z_dopelnienia(ob, ramka, [
        ((-L_in / 2, -H / 2), _nas("pomieszczenie dolne", ti, "wewn")),
        ((-L_in / 2, t + t_pod + (H - t_pod) / 2), _nas("pomieszczenie górne", ti, "wewn")),
        ((x_out + S / 2, -H / 2), _nas("zewnętrze", te, "zewn"))])
    # l_oi: wysokości „od podłogi do podłogi” — ściana dolna do poziomu podłogi kondygnacji wyższej (y = t + t_pod)
    fl = [ElementFlankujacy("ściana dolna", ("i", "e"), H + t / 2, H - t_suf, warstwy=list(warstwy_sciany),
                            l_oi=H + t + t_pod),
          ElementFlankujacy("ściana górna", ("i", "e"), H + t / 2, H - t_pod, warstwy=list(warstwy_sciany),
                            l_oi=H - t_pod)]
    if wysieg > 0:
        typ, psi_d = "wspornik", ("B_balkon" if lacznik is None else None)
        nazwa = nazwa or ("Płyta wspornikowa " + ("z łącznikiem termoizolacyjnym" if lacznik else "ciągła (bez przerwy)"))
    else:
        typ, psi_d = "strop_posredni", "IF_strop"
        nazwa = nazwa or "Strop pośredni z wieńcem w ścianie z ETICS"
    psi_dekl = None
    if wysieg > 0 and lacznik is LACZNIK_PRZYKLAD:
        try:
            from ..wspolne import wyrob
            wr = wyrob("laczniki", "wspornik_termiczny")
            if wr:
                psi_dekl = {"psi": wr.get("psi"), "f_Rsi": wr.get("f_Rsi"),
                            "zrodlo": f"{wr.get('status', '')} {wr.get('zrodlo', '')}".strip()}
        except Exception:   # pragma: no cover
            pass
    dane = {"warstwy ściany": dane_warstw(warstwy_sciany), "płyta": f"{mat_plyty.kod}, t = {t} m, wysięg = {wysieg} m",
            "warstwy podłogi": dane_warstw(warstwy_podlogi), "warstwy sufitu": dane_warstw(warstwy_sufitu)}
    if wysieg > 0:
        dane["łącznik"] = (f"{lacznik.nazwa}: λ_eq = {lacznik.lam} W/(m·K), d = {d_lacznika} m — {lacznik.zrodlo}"
                           if lacznik else "brak (płyta ciągła przez izolację)")
    return Wezel(id, nazwa, typ, ob, strefy, fl, przekroj="pionowy",
                 punkty={"naroże sufit": (0.0, -t_suf), "naroże podłoga": (0.0, t + t_pod)},
                 widok=(-min(L_in, 1.0), -min(H, 1.0), max(x_end, x_out) + 0.1, t + min(H, 1.0)),
                 psi_domyslne=psi_d, psi_deklarowane=psi_dekl, dane=dane,
                 opis="Przekrój pionowy; pomieszczenia nad i pod stropem ogrzewane (grupa „i”).")


def wezel_attyka(warstwy_sciany: Sequence[Warstwa], warstwy_dachu: Sequence[Warstwa], h_nad_pokryciem: float = 0.30,
                 izol_attyki: Material | None = None, d_izol_wewn: float = 0.10, d_izol_gora: float = 0.05,
                 mat_attyki: Material | None = None, blok_attyki: tuple[Material, float] | None = None,
                 H: float | None = None, L: float | None = None, theta_i: float | None = None,
                 theta_e: float | None = None, id: str = "WZ-R1",
                 nazwa: str = "Attyka stropodachu — ściana zewnętrzna") -> Wezel:
    """Attyka (przekrój pionowy): ściana warstwowa, płyta stropodachu na ścianie, warstwy dachu nad płytą, attyka
    (konstrukcja ściany ponad płytę) obłożona izolacją od wewnątrz (d_izol_wewn), od góry (d_izol_gora) i od zewnątrz
    (ETICS ściany). blok_attyki — opcjonalny blok termiczny u podstawy attyki (materiał, wysokość)."""
    ti, te = _temperatury(theta_i, theta_e)
    if ma_pustke_wentylowana(warstwy_dachu) or ma_pustke_wentylowana(warstwy_sciany):
        # ISO 6946: przy warstwie dobrze wentylowanej warstwy zewnętrzne pomija się w U I w modelu 2D, a na
        # powierzchni pustki R_se = R_si — ten wariant nie jest obsługiwany (weryfikacja niezależna, uwaga 7)
        raise ValueError(f"Węzeł {id}: przegroda z warstwą powietrza dobrze wentylowaną (dach wentylowany / elewacja "
                         f"wentylowana) — wariant nieobsługiwany w wezel_attyka; zbuduj węzeł z warstw do pustki "
                         f"i strefą zewnętrzną o R_s = R_si")
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    x_s0, x_s1 = st[ks][0], st[ks][1]
    x_out = st[-1][1]
    kd = indeks_konstrukcyjnej(warstwy_dachu)
    nad, plyta, pod = list(warstwy_dachu[:kd]), warstwy_dachu[kd], list(warstwy_dachu[kd + 1:])
    t = plyta.d
    t_suf = grubosc(pod)
    y_top = t + grubosc(nad)
    y_cap = y_top + h_nad_pokryciem
    y_p = y_cap - d_izol_gora
    izol = izol_attyki or (_izolacja_najlepsza(nad) if nad else MATERIALY_DOMYSLNE["XPS"])
    mat_att = mat_attyki or warstwy_sciany[ks].mat
    H = H or odl_ciecia(x_out)
    L = L or odl_ciecia(grubosc(warstwy_dachu))
    ob: list[Obszar] = []
    for k, (a, b, w) in enumerate(st):
        ob.append(_obsz(box(a, -H, b, 0.0 if k <= ks else y_p), w))
    for y0, y1, w in _stos(pod, 0.0, -1):
        ob.append(_obsz(box(-L, y0, 0.0, y1), w))
    ob.append(_obsz(box(-L, 0.0, x_s1, t), plyta, "płyta stropodachu"))
    for y0, y1, w in _stos(list(reversed(nad)), t, +1):
        ob.append(_obsz(box(-L, y0, x_s0 - d_izol_wewn, y1), w))
    ob.append(_obsz(box(x_s0, t, x_s1, y_p), mat_att, "attyka"))
    if blok_attyki:
        ob.append(_obsz(box(x_s0, t, x_s1, t + blok_attyki[1]), blok_attyki[0], "blok termiczny attyki"))
    ob.append(_obsz(box(x_s0 - d_izol_wewn, t, x_s0, y_p), izol, "izolacja attyki (wewn.)"))
    ob.append(_obsz(box(x_s0 - d_izol_wewn, y_p, x_out, y_cap), izol, "izolacja korony attyki"))
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-L, -H, x_out + S, y_cap + S), [
        ((-L / 2, -H / 2), _nas("pomieszczenie", ti, "wewn")),
        ((x_out + S / 2, -H / 2), _nas("zewnętrze", te, "zewn"))])
    fl = [ElementFlankujacy("ściana", ("i", "e"), H + y_top, H - t_suf, warstwy=list(warstwy_sciany), l_oi=H),
          ElementFlankujacy("stropodach", ("i", "e"), L + x_out, L, warstwy=pomin_pustki_wentylowane(warstwy_dachu),
                            Rsi=RSI_GORA, l_oi=L)]
    return Wezel(id, nazwa, "attyka", ob, strefy, fl, przekroj="pionowy",
                 punkty={"naroże sufit–ściana": (0.0, -t_suf)},
                 widok=(-min(L, 1.0), -min(H, 1.0), x_out + 0.1, y_cap + 0.1), psi_domyslne="R_attyka",
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany), "warstwy dachu": dane_warstw(warstwy_dachu),
                       "attyka": f"{mat_att.kod}, wys. nad pokryciem {h_nad_pokryciem} m; izolacja {izol.kod}: "
                                 f"wewn. {d_izol_wewn} m, korona {d_izol_gora} m"
                                 + (f"; blok termiczny {blok_attyki[0].kod} h = {blok_attyki[1]} m" if blok_attyki else "")})


def _okno_model(rama: Obszar, szyba: Obszar, x0: float, x_cut: float, yf0: float, d_f: float, ti: float, te: float,
                id: str) -> Wezel:
    S = S_STREFY
    ob = [rama, szyba]
    strefy = strefy_z_dopelnienia(ob, box(x0, yf0 - S, x_cut, yf0 + d_f + S), [
        ((x_cut - 0.01, yf0 - S / 2), _nas("wnętrze", ti, "wewn")),
        ((x_cut - 0.01, yf0 + d_f + S / 2), _nas("zewnętrze", te, "zewn"))])
    return Wezel(id + "-okno", "Okno bez ściany (rama + szyba) — L_2D odniesienia", "okno", ob, strefy,
                 przekroj="poziomy")


def wezel_oscieze_okna(warstwy_sciany: Sequence[Warstwa], U_f: float = 0.95, b_f: float = 0.115, d_f: float = 0.082,
                       U_g: float = 0.50, d_g: float = 0.044, polozenie: str = "w_izolacji", x0: float | None = None,
                       wsuniecie: float = 0.05, zaklad_izolacji: float = 0.03, szczelina: float = 0.015,
                       L: float | None = None,
                       L_g: float = 0.25, theta_i: float | None = None, theta_e: float | None = None,
                       id: str = "WZ-W1", nazwa: str | None = None, zrodlo_okna: str = "") -> Wezel:
    """Ościeże okna (rzut). Oś x wzdłuż ściany (mur do x = 0, otwór x > 0), oś y w poprzek (lico wewn. y = 0).
    polozenie: 'w_izolacji' — rama przed licem muru w warstwie ocieplenia (ciepły montaż na konsolach, x0 = −0,03
    — rama zachodzi na mur); 'w_murze' — rama w otworze muru, lico zewn. ramy w licu muru, szczelina z pianką;
    'czesciowo' — rama wsunięta w otwór muru na głębokość `wsuniecie`, reszta w warstwie ocieplenia (konwencja
    modelu: 5 cm w murze, 4 cm w izolacji).
    Izolacja ościeża zachodzi na ramę o `zaklad_izolacji`. ψ_inst = L_2D − U_ściany·l − L_2D,okna (okno bez ściany)."""
    ti, te = _temperatury(theta_i, theta_e)
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    y_s1 = st[ks][1]
    D = st[-1][1]
    L = L or odl_ciecia(D)
    m_r = material_rama(U_f, d_f, zrodlo=zrodlo_okna)
    m_g = material_szyba(U_g, d_g, zrodlo=zrodlo_okna)
    ob: list[Obszar] = []
    if polozenie == "w_izolacji":
        wsuniecie = 0.0
    elif polozenie == "w_murze":
        wsuniecie = d_f
    elif polozenie != "czesciowo":
        raise ValueError(polozenie)
    if x0 is None:
        x0 = szczelina if wsuniecie > 0 else -0.03
    yf0 = y_s1 - wsuniecie
    rama_g = box(x0, yf0, x0 + b_f, yf0 + d_f)
    yg0 = yf0 + (d_f - d_g) / 2
    x_cut = x0 + b_f + L_g
    for k, (a, b, w) in enumerate(st):
        if k < ks:
            ob.append(_obsz(box(-L, a, 0.0, b), w))
        elif k == ks:
            ob.append(_obsz(box(-L, a, 0.0, b), w))
        else:
            ob.append(_obsz(box(-L, a, x0 + zaklad_izolacji, b).difference(rama_g), w))
    if ks > 0:   # tynk wewn. na ościeżu
        ob.append(_obsz(box(0.0, 0.0, warstwy_sciany[0].d, yf0), warstwy_sciany[0], "tynk ościeża"))
    if wsuniecie > 0 and x0 > 0:
        ob.append(_obsz(box(0.0, yf0, x0, y_s1), MATERIALY_DOMYSLNE["PIANKA_PU"], "szczelina — pianka PU"))
    rama = _obsz(rama_g, m_r, "rama")
    szyba = _obsz(box(x0 + b_f, yg0, x_cut, yg0 + d_g), m_g, "szyba")
    ob += [rama, szyba]
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-L, -S, x_cut, D + S), [
        ((-L / 2, -S / 2), _nas("wnętrze", ti, "wewn")),
        ((-L / 2, D + S / 2), _nas("zewnętrze", te, "zewn"))])
    okno = _okno_model(rama, szyba, x0, x_cut, yf0, d_f, ti, te, id)
    fl = [ElementFlankujacy("ściana", ("i", "e"), L + x0, L + x0, warstwy=list(warstwy_sciany)),
          ElementFlankujacy("okno (L_2D ramy z szybą, model bez ściany)", ("i", "e"), 1.0, 1.0, wezel_ref=okno)]
    opis_pol = {"w_izolacji": "w warstwie izolacji (ciepły montaż)", "w_murze": "w murze (lico zewn. muru)",
                "czesciowo": f"wsunięta {wsuniecie * 100:.0f} cm w mur, reszta w izolacji"}[polozenie]
    return Wezel(id, nazwa or f"Ościeże okna — rama {opis_pol}",
                 "oscieze", ob, strefy, fl, przekroj="poziomy",
                 punkty={"naroże ościeża (mur)": (0.0, 0.0), "styk rama–ościeże": (max(0.0, x0), yf0)},
                 widok=(-0.6, -0.1, x_cut, D + 0.1), psi_domyslne="W_oscieze",
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany),
                       "okno": f"U_f = {U_f}, b_f = {b_f} m, d_f = {d_f} m (λ_eq ramy = {m_r.lam:.4f}); "
                               f"U_g = {U_g}, d_g = {d_g} m (λ_eq = {m_g.lam:.4f}); położenie: {opis_pol}, "
                               f"x0 = {x0} m, zakład izolacji {zaklad_izolacji} m {zrodlo_okna}"},
                 uwagi=["Rama i szyba jako materiały zastępcze (λ_eq z U_f, U_g); ψ osadzenia liczone względem "
                        "modelu okna bez ściany, więc uproszczenie ramy wpływa na ψ w małym stopniu. Ψ_g ramki "
                        "dystansowej — poza zakresem (U_w wg PN-EN ISO 10077-1)."])


def U_podlogi_13370(B: float, w: float, R_f: float, lam: float = LAMBDA_GRUNTU, Rsi: float = RSI_DOL,
                    Rse: float = RSE) -> tuple[float, float]:
    """U podłogi na gruncie wg PN-EN ISO 13370:2017 (płyta na gruncie) [NZW — wzory poza próbką normy, rejestr R6-30]:
    d_t = w + λ(R_si + R_f + R_se); d_t < B': U = 2λ/(πB' + d_t)·ln(πB'/d_t + 1); d_t ≥ B': U = λ/(0,457B' + d_t)."""
    dt = w + lam * (Rsi + R_f + Rse)
    if dt < B:
        U = 2 * lam / (math.pi * B + dt) * math.log(math.pi * B / dt + 1)
    else:
        U = lam / (0.457 * B + dt)
    return U, dt


def wezel_cokol(warstwy_sciany: Sequence[Warstwa], warstwy_podlogi: Sequence[Warstwa], fundament: str = "lawa",
                lawa: tuple[float, float, float] = (0.60, 0.30, -1.10), mat_lawy: Material | None = None,
                sciana_fund: tuple[Material, float] | None = None, izol_obwodowa: Material | None = None,
                hydro: tuple[Material, float] | None = None, glebokosc_izol: float | None = None,
                y_teren: float = -0.30, h_cokolu: float = 0.30, blok_termiczny: tuple[Material, float] | None = None,
                b: float = B_DOMYSLNE, H: float | None = None, theta_i: float | None = None,
                theta_e: float | None = None, id: str = "WZ-GF1", nazwa: str | None = None) -> Wezel:
    """Cokół: ściana zewnętrzna – podłoga na gruncie – fundament (ława z murem fundamentowym albo płyta fundamentowa)
    z gruntem (λ = 2,0). Przekrój pionowy; lico wewn. ściany x = 0, posadzka ±0,00 = y 0, teren y_teren.
    Obszar gruntu wg ISO 10211 (model 2D z podłogą): wewnątrz 0,5·b od lica zewn., na zewnątrz 2,5·b, w głąb 2,5·b
    poniżej terenu (b — szerokość budynku; 8 m, gdy nieznana) [NZW]; płaszczyzny odcięcia w gruncie adiabatyczne.
    ψ_g = L_2D − U_ściany·h − U_podłogi(ISO 13370, B' = b)·l_podłogi (wymiary zewn.: l = 0,5·b; wewn.: 0,5·b − w)."""
    ti, te = _temperatury(theta_i, theta_e)
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    x_s0, x_s1 = st[ks][0], st[ks][1]
    x_out = st[-1][1]
    fl_st = _stos(warstwy_podlogi, 0.0, -1)
    kf = indeks_konstrukcyjnej(warstwy_podlogi)
    y_w0 = fl_st[kf][1]
    y_fb = fl_st[-1][0]
    H = H or odl_ciecia(x_out)
    mat_lawy = mat_lawy or MATERIALY_DOMYSLNE["ZB"]
    sciana_fund = sciana_fund or (MATERIALY_DOMYSLNE["BET_FUND"], max(0.24, x_s1 - x_s0))
    izol = izol_obwodowa or MATERIALY_DOMYSLNE["XPS"]
    hydro = hydro if hydro is not None else (MATERIALY_DOMYSLNE["HYDRO"], 0.004)
    y_prz = y_teren + h_cokolu
    x_in = x_out - 0.5 * b
    x_pr = x_out + 2.5 * b
    y_dol = y_teren - 2.5 * b
    grunt = MATERIALY_DOMYSLNE["GRUNT"]
    ob: list[Obszar] = [_obsz(box(x_in, y_dol, x_pr, y_teren), grunt, "grunt")]
    if y_fb > y_teren:
        ob.append(_obsz(box(x_in, y_teren, x_s1, y_fb), grunt, "grunt pod podłogą"))
    d_fw = sciana_fund[1]
    if fundament == "lawa":
        b_l, h_l, spod = lawa
        y_lt = spod + h_l
        xc = x_s1 - d_fw / 2
        ob.append(_obsz(box(xc - b_l / 2, spod, xc + b_l / 2, y_lt), mat_lawy, "ława fundamentowa"))
        ob.append(_obsz(box(x_s1 - d_fw, y_lt, x_s1, y_w0), sciana_fund[0], "ściana fundamentowa"))
        x_pod = x_s1 - d_fw
        y_izol_dol = y_lt if glebokosc_izol is None else max(y_lt, y_teren - glebokosc_izol)
        for k, (y0, y1, w) in enumerate(fl_st):
            ob.append(_obsz(box(x_in, y0, x_s0 if k < kf else x_pod, y1), w))
        opis_f = f"ława {b_l}×{h_l} m (spód {spod}), mur fundamentowy {sciana_fund[0].kod} {d_fw} m"
    elif fundament == "plyta":
        for k, (y0, y1, w) in enumerate(fl_st):
            x_k = x_s0 if k < kf else (x_s1 if k == kf else x_out)
            ob.append(_obsz(box(x_in, y0, x_k, y1), w))
        y_izol_dol = fl_st[kf][0]          # spód płyty — izolacja pod płytą (warstwy niżej) sięga do lica zewn.
        spod = y_fb
        opis_f = f"płyta fundamentowa {warstwy_podlogi[kf].mat.kod} {warstwy_podlogi[kf].d} m"
    else:
        raise ValueError(fundament)
    # ściana nad fundamentem
    for k, (a, bb, w) in enumerate(st):
        if k < ks:
            ob.append(_obsz(box(a, 0.0, bb, H), w))
        elif k == ks:
            ob.append(_obsz(box(a, y_w0, bb, H), w))
        else:
            ob.append(_obsz(box(a, y_prz, bb, H), w))
    if blok_termiczny:
        ob.append(_obsz(box(x_s0, y_w0, x_s1, y_w0 + blok_termiczny[1]), blok_termiczny[0], "blok termiczny"))
    # izolacja obwodowa + hydroizolacja (strefa cokołu i poniżej terenu)
    d_h = hydro[1] if hydro else 0.0
    if hydro:
        ob.append(_obsz(box(x_s1, y_izol_dol, x_s1 + d_h, y_prz), hydro[0], "hydroizolacja pionowa"))
    ob.append(_obsz(box(x_s1 + d_h, y_izol_dol, x_out, y_prz), izol, "izolacja obwodowa (cokół)"))
    strefy = strefy_z_dopelnienia(ob, box(x_in, y_dol, x_pr, H), [
        ((-0.5, H / 2), _nas("pomieszczenie", ti, "wewn")),
        ((x_out + 1.0, y_teren + (H - y_teren) / 2), _nas("zewnętrze", te, "zewn"))])
    R_f = R_warstw(warstwy_podlogi)
    U_fl, d_t = U_podlogi_13370(b, x_out, R_f)
    fl = [ElementFlankujacy("ściana (od poziomu posadzki)", ("i", "e"), H, H, warstwy=list(warstwy_sciany)),
          ElementFlankujacy(f"podłoga na gruncie (U wg ISO 13370, B' = {b} m, d_t = {d_t:.2f} m)", ("i", "e"),
                            0.5 * b, 0.5 * b - x_out, U=U_fl, zrodlo="PN-EN ISO 13370:2017 [NZW]")]
    return Wezel(id, nazwa or f"Cokół — ściana / podłoga na gruncie / {'ława' if fundament == 'lawa' else 'płyta'}",
                 "cokol", ob, strefy, fl, przekroj="pionowy",
                 punkty={"naroże ściana–posadzka": (0.0, 0.0)},
                 siatka={"h_min": 0.003, "h_max": 0.40, "r": 1.25},
                 widok=(-1.2, min(spod, y_fb) - 0.4, x_out + 1.0, 1.0), psi_domyslne="GF_cokol",
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany), "warstwy podłogi": dane_warstw(warstwy_podlogi),
                       "fundament": opis_f, "izolacja obwodowa": f"{izol.kod} do rzędnej {y_izol_dol:.2f}, "
                       f"cokół do {y_prz:.2f} (teren {y_teren:.2f})",
                       "grunt": f"λ = {grunt.lam} W/(m·K); obszar: wewn. 0,5·b = {0.5 * b} m od lica zewn., "
                                f"zewn. 2,5·b = {2.5 * b} m, głęb. 2,5·b = {2.5 * b} m (b = {b} m)",
                       "U podłogi (ISO 13370)": f"R_f = {R_f:.3f} m²K/W, d_t = {d_t:.3f} m, U = {U_fl:.4f} W/(m²K)"}
                 | ({"blok termiczny": f"{blok_termiczny[0].kod} h = {blok_termiczny[1]} m"} if blok_termiczny else {}),
                 uwagi=["Ściana liczona od poziomu posadzki (±0,00) w obu systemach wymiarów; podłoga wg PN-EN ISO "
                        "13370 z B' = b (pas nieskończony) [INT]."])


def wezel_garaz(warstwy_sciany: Sequence[Warstwa], warstwy_sciany_garazu: Sequence[Warstwa],
                przerwa_izolacji: bool = False, L: float | None = None, L_g: float | None = None,
                theta_u: float | None = None, b_u: float = 0.8, theta_i: float | None = None,
                theta_e: float | None = None, id: str = "WZ-G1", nazwa: str | None = None) -> Wezel:
    """Połączenie ściany zewnętrznej domu ze ścianą zewnętrzną garażu nieogrzewanego (rzut, 3 temperatury).
    Ściana domu wzdłuż osi x (wnętrze y < 0); ściana garażu prostopadła, lico od garażu x = 0 (garaż x > 0,
    zewnętrze x < −d_g). przerwa_izolacji=False — ściana garażu dochodzi do lica ETICS (izolacja domu ciągła);
    True — konstrukcja ściany garażu wchodzi w warstwę ocieplenia aż do muru domu (mostek).
    θ_u: zadana albo z b_u: θ_u = θ_e + (1 − b_u)(θ_i − θ_e) [ZAŁ]."""
    ti, te = _temperatury(theta_i, theta_e)
    tu = theta_u if theta_u is not None else te + (1 - b_u) * (ti - te)
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    y_s1, y_out = st[ks][1], st[-1][1]
    sg = _stos(warstwy_sciany_garazu, 0.0, -1)
    kg = indeks_konstrukcyjnej(warstwy_sciany_garazu)
    d_g = grubosc(warstwy_sciany_garazu)
    L = L or (odl_ciecia(max(y_out, d_g)) + d_g)
    L_g = L_g or odl_ciecia(y_out)
    ob: list[Obszar] = [_obsz(box(-L, a, L, b), w) for a, b, w in st]
    for k, (a, b, w) in enumerate(sg):
        y0 = y_s1 if (przerwa_izolacji and k == kg) else y_out
        ob.append(_obsz(box(a, y0, b, y_out + L_g), w))
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-L, -S, L, y_out + L_g), [
        ((0.0, -S / 2), _nas("dom (ogrzewany)", ti, "wewn")),
        ((-(L + d_g) / 2, y_out + L_g / 2), _nas("zewnętrze", te, "zewn")),
        (((L) / 2, y_out + L_g / 2), _nas("garaż nieogrzewany", tu, "nieogrz"))])
    fl = [ElementFlankujacy("ściana domu → zewnętrze", ("i", "e"), L - d_g, L - d_g, warstwy=list(warstwy_sciany)),
          ElementFlankujacy("ściana domu → garaż", ("i", "u"), L + d_g, L + d_g, warstwy=list(warstwy_sciany),
                            Rse=RSI_POZIOMO),
          ElementFlankujacy("ściana garażu", ("u", "e"), L_g, L_g, warstwy=list(warstwy_sciany_garazu))]
    return Wezel(id, nazwa or ("Dom – garaż nieogrzewany: ściana garażu " +
                               ("przerywa ocieplenie" if przerwa_izolacji else "dochodzi do lica ETICS")),
                 "garaz", ob, strefy, fl, przekroj="poziomy",
                 punkty={"naroże dom (lico wewn.)": (0.0, 0.0)},
                 widok=(-1.2, -0.3, 1.2, y_out + 1.0),
                 dane={"warstwy ściany domu": dane_warstw(warstwy_sciany),
                       "warstwy ściany garażu (od garażu)": dane_warstw(warstwy_sciany_garazu),
                       "θ_u garażu": f"{tu:.1f} °C" + (" (zadana)" if theta_u is not None
                                                        else f" z b_u = {b_u} [ZAŁ]")},
                 uwagi=["Podział ściany domu na część „do zewnętrza” i „do garażu” w licu zewnętrznym ściany garażu "
                        "(jedyny system wymiarów — strona ogrzewana jest płaska, ψ_e = ψ_i).",
                        "Po stronie garażu R_s = 0,13 (ISO 6946 — przegroda do przestrzeni nieogrzewanej)."])


def wezel_rura_spustowa(warstwy_sciany: Sequence[Warstwa], szer_wneki: float = 0.16, d_pozostala: float = 0.06,
                        L: float | None = None, theta_i: float | None = None, theta_e: float | None = None,
                        id: str = "WZ-RS1", nazwa: str = "Rura spustowa we wnęce ocieplenia (rzut)") -> Wezel:
    """Wnęka w ETICS na rurę spustową (DN100): izolacja zredukowana do d_pozostala na szerokości szer_wneki; wnęka
    otwarta do powietrza zewnętrznego (rura z wodą ~ θ_e). Ocena ryzyka ścienienia izolacji za rurą."""
    ti, te = _temperatury(theta_i, theta_e)
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    y_s1, D = st[ks][1], st[-1][1]
    L = L or odl_ciecia(D)
    wneka = box(-szer_wneki / 2, y_s1 + d_pozostala, szer_wneki / 2, D + 1)
    ob = []
    for k, (a, b, w) in enumerate(st):
        g = box(-L, a, L, b)
        if k > ks:
            g = g.difference(wneka)
        if not g.is_empty:
            ob.append(_obsz(g, w))
    S = S_STREFY
    strefy = strefy_z_dopelnienia(ob, box(-L, -S, L, D + S), [
        ((0.0, -S / 2), _nas("wnętrze", ti, "wewn")),
        ((0.0, D + S / 2), _nas("zewnętrze (z wnęką)", te, "zewn"))])
    fl = [ElementFlankujacy("ściana", ("i", "e"), 2 * L, 2 * L, warstwy=list(warstwy_sciany))]
    return Wezel(id, nazwa, "rura_spustowa", ob, strefy, fl, przekroj="poziomy",
                 punkty={"lico wewn. za wnęką": (0.0, 0.0)}, widok=(-0.6, -0.1, 0.6, D + 0.1),
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany),
                       "wnęka": f"szer. {szer_wneki} m, pozostała izolacja {d_pozostala} m"},
                 uwagi=["Wariant zalecany: rura przed licem ETICS na obejmach dystansowych (bez wnęki) albo "
                        "wewnętrzna w izolowanym szachcie — ψ ≈ 0."])
