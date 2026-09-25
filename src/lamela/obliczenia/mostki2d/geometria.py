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
  współczynniki sprzężenia L_2D liczone są między grupami (PN-EN ISO 10211 p. 10.4 — więcej niż dwie temperatury);
* warstwy przegród jak w modelu (`docs/SCHEMAT_MODELU.md`): ściany od WNĘTRZA do ZEWNĄTRZ, poziome od GÓRY do DOŁU.

Opory przejmowania (PN-EN ISO 6946:2017 tab. 7; PN-EN ISO 10211:2017 p. 7.3; PN-EN ISO 13788:2013 p. 4.2.2):
R_se = 0,04; R_si = 0,13 (poziomo), 0,10 (w górę), 0,17 (w dół) — do strumieni i ψ; R_si = 0,25 do oceny temperatury
powierzchni (f_Rsi), 0,13 dla ram i szyb.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

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
LAMBDA_GRUNTU = 2.0         # W/(m·K) — PN-EN ISO 13370:2017 tab. 7 (piasek/żwir) / PN-EN ISO 10211:2017 p. 5.2.4 [NZW]
B_DOMYSLNE = 8.0            # m — szerokość budynku do modelu gruntu 2D, gdy nieznana (ISO 10211 tab. 2) [NZW]


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
       "PN-EN ISO 10211:2017 p. 5.2.4 / PN-EN ISO 13370:2017 tab. 7 [NZW]"),
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
    "LACZNIK_80", 0.13, "Łącznik termoizolacyjny 80 mm (moduł izolacyjny + pręty nierdzewne), λ_eq", "#d1495b",
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
    """Pakiet szybowy jako płyta zastępcza λ_eq = d_g / (1/U_g − R_si − R_se) (PN-EN ISO 10077-2 p. 6.2)."""
    R = 1.0 / U_g - Rsi - Rse
    return Material(kod, d_g / R, f"Pakiet szybowy (λ_eq z U_g = {U_g} W/(m²K), d = {d_g} m)", "#a8d0e6", "szyba",
                    zrodlo or "PN-EN ISO 10077-2:2017 p. 6.2 (płyta zastępcza szyby)")


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
    """Element flankujący do ψ = L_2D − Σ U_j·l_j (ISO 10211 wz. 13 / ISO 14683 p. 5.3).
    U — podane albo liczone z `warstwy` (1D, te same R_s co w modelu 2D); `wezel_ref` — podmodel, którego L_2D
    zastępuje U·l (np. okno bez ściany — ψ osadzenia); `l_e`, `l_i` — długości wg wymiarów zewnętrznych/wewnętrznych."""
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
    (PN-EN ISO 10211:2017 p. 5.2.2)."""
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
    if any(s in nazwa.lower() for s in ("pustk", "powietrz", "legar", "szczelin")):
        rodzaj = "powietrze"
    return Material(kod, float(m.lambda_), nazwa, getattr(m, "kolor", None), rodzaj,
                    "model budynku (materialy.*.lambda)")


def warstwy_z_modelu(model, kod_przegrody: str) -> list[Warstwa]:
    """Warstwy przegrody z modelu (`m.przegroda(kod).warstwy`) → lista `Warstwa` (kolejność jak w modelu)."""
    p = model.przegroda(kod_przegrody)
    return [Warstwa(material_z_modelu(model, w.mat), float(w.d), bool(w.konstrukcyjna)) for w in p.warstwy]


def pomin_pustki_wentylowane(warstwy: Sequence[Warstwa], zewn_na_poczatku: bool = True) -> list[Warstwa]:
    """Pustkę wentylowaną i warstwy za nią (po stronie zewnętrznej) pomija się (ISO 6946:2017 p. 6.9.4).
    zewn_na_poczatku=True — lista od góry (dachy, tarasy: strona zewnętrzna pierwsza); False — ściany (od wnętrza)."""
    lista = list(warstwy) if zewn_na_poczatku else list(reversed(warstwy))
    out: list[Warstwa] = []
    for w in lista:
        if w.mat.rodzaj == "powietrze":
            out = []
            continue
        out.append(w)
    return out if zewn_na_poczatku else list(reversed(out))
