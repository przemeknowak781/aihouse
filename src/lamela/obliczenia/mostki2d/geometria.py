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

from shapely.affinity import affine_transform
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
    _m("PARAPET_WEWN", 0.18, "Parapet wewnętrzny (MDF / drewno)", "#caa472", zrodlo="PN-EN ISO 10456:2009 [ZAŁ]"),
    _m("PROG_TERM", 0.05, "Podwalina / profil progowy termiczny (twarda pianka PUR / kompozyt)", "#e3b04b",
       zrodlo="[DANE PRZYKŁADOWE – FIKCYJNE] λ typowego profilu progowego do ciepłego montażu (do zastąpienia DoP)"),
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
    # warstwy cienkie i elementy odprowadzenia wody — TYLKO do rysunku (zasada „4 linii”, brief pkt 9.1): pomijalne
    # cieplnie (membrany, taśmy, obróbki) albo poza modelem (drenaż, rura spustowa); [{rodzaj, xy, opis}], rodzaj
    # z `RODZAJE_LINII`
    linie: list[dict] = field(default_factory=list)

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


# rodzaje linii schematycznych (`Wezel.linie`) — kolory zasady „4 linii” (brief sekcja 9 pkt 1)
RODZAJE_LINII = {
    "hydro": "hydroizolacja / izolacja przeciwwodna",
    "przeciwwilg": "izolacja przeciwwilgociowa (pozioma)",
    "paro": "paroizolacja / warstwa szczelności powietrznej",
    "tasma_wewn": "taśma paroszczelna (wewn.)",
    "tasma_zewn": "taśma paroprzepuszczalna / uszczelnienie zewn.",
    "obrobka": "obróbka blacharska / parapet z okapnikiem",
    "woda": "kierunek spływu wody (spadek)",
    "drenaz": "drenaż opaskowy / opaska żwirowa",
    "rura": "rura spustowa",
}


def _ln(rodzaj: str, xy, opis: str = "") -> dict:
    if rodzaj not in RODZAJE_LINII:
        raise ValueError(rodzaj)
    return {"rodzaj": rodzaj, "xy": [(float(a), float(b)) for a, b in xy], "opis": opis}


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
    linie = []
    if wysieg > 0:
        h_w = 0.15 + 0.07     # wywinięcie ≥ 15 cm ponad nawierzchnię tarasu (nawierzchnia ~7 cm) [ZAŁ]
        linie = [_ln("hydro", [(x_end, t + 0.004), (x_out + 0.004, t + 0.004), (x_out + 0.004, t + h_w)],
                     "hydroizolacja płyty wywinięta na ścianę ≥ 15 cm ponad nawierzchnię (pod cokolik XPS)"),
                 _ln("obrobka", [(x_end - 0.10, t + 0.006), (x_end + 0.03, t + 0.006), (x_end + 0.03, t - 0.05),
                                 (x_end + 0.045, t - 0.065)], "obróbka czoła płyty z okapnikiem ≥ 3 cm"),
                 _ln("woda", [(x_out + 0.12, t + 0.05), (x_out + max(0.25, min(0.9, wysieg - 0.1)), t + 0.05)],
                     "spadek płyty ≥ 1,5–2 % od budynku")]
    return Wezel(id, nazwa, typ, ob, strefy, fl, przekroj="pionowy", linie=linie,
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
    x_iw = x_s0 - d_izol_wewn
    paro = next((w.mat.kod for w in nad if "paroiz" in w.mat.nazwa.lower() or "paroiz" in w.mat.kod.lower()), None)
    hyd = next((w.mat.kod for w in nad if any(k in f"{w.mat.kod} {w.mat.nazwa}".lower()
                                             for k in ("epdm", "hydro", "papa", "pap ", "tpo", "pvc", "membran"))),
               None)
    wz_h = h_nad_pokryciem >= 0.15
    r_k = 0.05 * (x_out + 0.035 - (x_iw - 0.03))       # spadek korony 5 % do dachu
    linie = [
        _ln("paro", [(-L, t + 0.001), (x_s0 - 0.002, t + 0.001), (x_s0 - 0.002, y_top + 0.05)],
            f"paroizolacja na płycie ({paro or 'BRAK w przegrodzie modelu'}) wywinięta na attykę ponad izolację "
            f"dachu, połączona z płytą ŻB (szczelność)"),
        _ln("hydro", [(-L, y_top), (x_iw, y_top), (x_iw, y_cap), (x_out, y_cap), (x_out, y_cap - 0.06)],
            f"hydroizolacja ({hyd or 'BRAK w przegrodzie modelu'}) wywinięta na attykę i koronę — "
            f"{h_nad_pokryciem * 100:.0f} cm ponad pokrycie ({'≥' if wz_h else '< WYMAGANE'} 15 cm)"),
        _ln("obrobka", [(x_iw - 0.03, y_cap - 0.07), (x_iw - 0.03, y_cap + 0.01), (x_out + 0.035, y_cap + 0.01 + r_k),
                        (x_out + 0.035, y_cap - 0.05), (x_out + 0.05, y_cap - 0.065)],
            "obróbka korony attyki: spadek ≥ 5 % do dachu, okapniki ≥ 3 cm od lic"),
        _ln("woda", [(x_iw - 0.08, y_top + 0.04), (x_iw - min(0.6, 0.8 * L), y_top + 0.04)],
            "spadek dachu ≥ 2 % do wpustów; przelew awaryjny w attyce (mostek punktowy χ)"),
    ]
    return Wezel(id, nazwa, "attyka", ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"naroże sufit–ściana": (0.0, -t_suf)},
                 widok=(-min(L, 1.0), -min(H, 1.0), x_out + 0.1, y_cap + 0.1), psi_domyslne="R_attyka",
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany), "warstwy dachu": dane_warstw(warstwy_dachu),
                       "attyka": f"{mat_att.kod}, wys. nad pokryciem {h_nad_pokryciem} m; izolacja {izol.kod}: "
                                 f"wewn. {d_izol_wewn} m, korona {d_izol_gora} m"
                                 + (f"; blok termiczny {blok_attyki[0].kod} h = {blok_attyki[1]} m" if blok_attyki else "")})


# ---- krawędzie otworów okiennych: ościeże (rzut), nadproże i podokiennik (przekroje pionowe) -------------------
# Geometria budowana w układzie lokalnym (s, n): s — wzdłuż ściany (mur s < 0, otwór s > 0, krawędź otworu w murze
# s = 0), n — w poprzek ściany (lico wewn. n = 0, wnętrze n < 0, lico zewn. n = D). Przekształcenie do układu węzła:
_TRANSFORMACJE = {
    "oscieze": (1.0, 0.0, 0.0, 1.0),      # rzut: x = s, y = n
    "nadproze": (0.0, 1.0, -1.0, 0.0),    # przekrój pionowy: x = n (wnętrze x < 0), y = −s (mur nad otworem)
    "podokiennik": (0.0, 1.0, 1.0, 0.0),  # przekrój pionowy: x = n, y = s (mur pod otworem)
}


def _tr(rodzaj: str):
    a, b, d, e = _TRANSFORMACJE[rodzaj]

    def f(obj):
        if isinstance(obj, tuple):
            s_, n_ = obj
            return (a * s_ + b * n_, d * s_ + e * n_)
        return affine_transform(obj, [a, b, d, e, 0.0, 0.0])
    return f


def U_w_okna(U_f: float, U_g: float, b_f: float, psi_g: float = 0.0, B: float = 1.23, H: float = 1.48) -> float:
    """U_w okna jednodzielnego wg PN-EN ISO 10077-1 (okno referencyjne 1,23 × 1,48 m):
    U_w = (A_g·U_g + A_f·U_f + l_g·ψ_g)/A_w."""
    A_w = B * H
    bg, hg = B - 2 * b_f, H - 2 * b_f
    A_g = bg * hg
    return (A_g * U_g + (A_w - A_g) * U_f + 2 * (bg + hg) * psi_g) / A_w


def _okno_model(rama: Obszar, szyba: Obszar, ti: float, te: float, id: str, rodzaj: str = "oscieze",
                S: float = S_STREFY) -> Wezel:
    """Podmodel „okno bez ściany” (rama + szyba) — L_2D odniesienia ψ osadzenia. Rama i szyba podane w układzie
    węzła; ramka obejmuje je w kierunku „w poprzek ściany” (±S), a w kierunku wzdłuż ściany kończy się na krawędzi
    ramy (płaszczyzna adiabatyczna — odpowiednik krawędzi okna) i na cięciu szyby."""
    ob = [rama, szyba]
    minx, miny, maxx, maxy = unary_union([rama.wielobok, szyba.wielobok]).bounds
    if rodzaj == "oscieze":        # wzdłuż x, w poprzek y
        ramka = box(minx, miny - S, maxx, maxy + S)
        nas_i, nas_e = (maxx - 0.01, miny - S / 2), (maxx - 0.01, maxy + S / 2)
        przekroj = "poziomy"
    else:                          # przekroje pionowe: wzdłuż y, w poprzek x
        ramka = box(minx - S, miny, maxx + S, maxy)
        yk = maxy - 0.01 if rodzaj == "podokiennik" else miny + 0.01
        nas_i, nas_e = (minx - S / 2, yk), (maxx + S / 2, yk)
        przekroj = "pionowy"
    strefy = strefy_z_dopelnienia(ob, ramka, [(nas_i, _nas("wnętrze", ti, "wewn")), (nas_e, _nas("zewnętrze", te, "zewn"))])
    return Wezel(id + "-okno", "Okno bez ściany (rama + szyba) — L_2D odniesienia", "okno", ob, strefy,
                 przekroj=przekroj)


def _wezel_krawedz_okna(rodzaj: str, warstwy_sciany: Sequence[Warstwa], U_f: float, b_f: float, d_f: float,
                        U_g: float, d_g: float, polozenie: str, x0: float | None, wsuniecie: float,
                        zaklad_izolacji: float, szczelina: float, L: float | None, L_g: float,
                        theta_i: float | None, theta_e: float | None, id: str, nazwa: str | None, zrodlo_okna: str,
                        U_w: float | None, psi_g: float, nadproze: tuple[Material, float] | None = None,
                        kaseta: tuple[float, float] | None = None,
                        parapet_wewn: tuple[Material, float, float] | None = None,
                        parapet_zewn: tuple[Material, float, float] | None = None) -> Wezel:
    ti, te = _temperatury(theta_i, theta_e)
    T = _tr(rodzaj)
    st = _stos(warstwy_sciany, 0.0)
    ks = indeks_konstrukcyjnej(warstwy_sciany)
    y_s1 = st[ks][1]
    D = st[-1][1]
    L = L or odl_ciecia(D)
    m_r = material_rama(U_f, d_f, zrodlo=zrodlo_okna)
    m_g = material_szyba(U_g, d_g, zrodlo=zrodlo_okna)
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
    s_izol = x0 + zaklad_izolacji          # zasięg izolacji ościeża (zakład na ramę)
    d_t0 = warstwy_sciany[0].d if ks > 0 else 0.0
    ob: list[Obszar] = []
    wneka = None
    if kaseta is not None:                 # kaseta osłony (żaluzja/screen) w warstwie ocieplenia nad oknem
        h_k, gl_k = kaseta
        n_k = max(y_s1 + 0.01, D - gl_k)
        wneka = box(-h_k, n_k, s_izol, D + 1.0)
    for k, (a, b, w) in enumerate(st):
        if k <= ks:
            ob.append(_obsz(box(-L, a, 0.0, b), w))
        else:
            g = box(-L, a, s_izol, b).difference(rama_g)
            if wneka is not None:
                g = g.difference(wneka)
            ob.append(_obsz(g, w))
    if nadproze is not None:
        a, b, w = st[ks]
        ob.append(_obsz(box(-min(nadproze[1], L), a, 0.0, b), nadproze[0], "nadproże"))
    if parapet_wewn is not None:           # parapet wewnętrzny zamiast tynku ościeża
        mat_pw, d_pw, wys_pw = parapet_wewn
        ob.append(_obsz(box(0.0, -wys_pw, d_pw, yf0), mat_pw, "parapet wewnętrzny"))
    elif ks > 0:   # tynk wewn. na ościeżu
        ob.append(_obsz(box(0.0, 0.0, d_t0, yf0), warstwy_sciany[0], "tynk ościeża"))
    if wsuniecie > 0 and x0 > 0:
        ob.append(_obsz(box(0.0, yf0, x0, y_s1), MATERIALY_DOMYSLNE["PIANKA_PU"], "szczelina — pianka PU"))
    rama = _obsz(rama_g, m_r, "rama")
    szyba = _obsz(box(x0 + b_f, yg0, x_cut, yg0 + d_g), m_g, "szyba")
    ob += [rama, szyba]
    if parapet_zewn is not None:           # parapet zewnętrzny (obróbka) na izolacji, wysunięty poza lico elewacji
        mat_pz, d_pz, wys_pz = parapet_zewn
        ob.append(_obsz(box(s_izol, yf0 + d_f, s_izol + d_pz, D + wys_pz), mat_pz, "parapet zewnętrzny"))
    S = S_STREFY
    ob_t = [Obszar(T(o.wielobok), o.mat, o.nazwa) for o in ob]
    ramka = T(box(-L, -S, x_cut, D + S))
    strefy = strefy_z_dopelnienia(ob_t, ramka, [
        (T((-L / 2, -S / 2)), _nas("wnętrze", ti, "wewn")),
        (T((-L / 2, D + S / 2)), _nas("zewnętrze", te, "zewn"))])
    okno = _okno_model(ob_t[-2 if parapet_zewn is None else -3], ob_t[-1 if parapet_zewn is None else -2], ti, te, id,
                       rodzaj)
    Uw = U_w if U_w is not None else U_w_okna(U_f, U_g, b_f, psi_g)
    # ψ_e/ψ_i: ściana do krawędzi ramy (x0), okno = L_2D ramy z szybą (ISO 14683/10077 — wymiary okna po ramie);
    # ψ_oi (energia.bryla — pole okna w świetle otworu w murze): ściana do krawędzi otworu s = 0, a pas okna między
    # krawędzią ramy a krawędzią otworu (x0 > 0: szczelina; x0 < 0: rama za murem) — korekta U_w·x0.
    fl = [ElementFlankujacy("ściana", ("i", "e"), L + x0, L + x0, warstwy=list(warstwy_sciany), l_oi=L),
          ElementFlankujacy("okno (L_2D ramy z szybą, model bez ściany)", ("i", "e"), 1.0, 1.0, wezel_ref=okno),
          ElementFlankujacy("okno — pas krawędź ramy ↔ krawędź otworu w murze (tylko system oi, U_w)", ("i", "e"),
                            0.0, 0.0, U=Uw, l_oi=x0, zrodlo="PN-EN ISO 10077-1 (U_w okna referencyjnego)")]
    opis_pol = {"w_izolacji": "w warstwie izolacji (ciepły montaż)", "w_murze": "w murze (lico zewn. muru)",
                "czesciowo": f"wsunięta {wsuniecie * 100:.0f} cm w mur, reszta w izolacji"}[polozenie]
    dane = {"warstwy ściany": dane_warstw(warstwy_sciany),
            "okno": f"U_f = {U_f}, b_f = {b_f} m, d_f = {d_f} m (λ_eq ramy = {m_r.lam:.4f}); "
                    f"U_g = {U_g}, d_g = {d_g} m (λ_eq = {m_g.lam:.4f}); U_w = {Uw:.3f} (ISO 10077-1, okno 1,23×1,48); "
                    f"położenie: {opis_pol}, x0 = {x0} m, zakład izolacji {zaklad_izolacji} m {zrodlo_okna}"}
    uwagi = ["Rama i szyba jako materiały zastępcze (λ_eq z U_f, U_g); ψ osadzenia liczone względem modelu okna bez "
             "ściany, więc uproszczenie ramy wpływa na ψ w małym stopniu. Ψ_g ramki dystansowej — poza zakresem "
             "(U_w wg PN-EN ISO 10077-1)."]
    punkty = {"naroże ościeża (mur)": T((0.0, 0.0)), "styk rama–ościeże": T((max(x0, d_t0), yf0))}
    typ, psi_d = "oscieze", "W_oscieze"
    if rodzaj == "nadproze":
        typ = "nadproze"
        nz = nazwa or f"Nadproże okna — rama {opis_pol}" + (" + kaseta osłony w ociepleniu" if kaseta else "")
        if nadproze is not None:
            dane["nadproże"] = f"{nadproze[0].kod} (λ = {nadproze[0].lam}), h = {nadproze[1]} m [ZAŁ]"
        if kaseta is not None:
            dane["kaseta osłony"] = (f"wys. {kaseta[0]} m, głęb. w ociepleniu {kaseta[1]} m — wnętrze kasety "
                                     f"(szczelina prowadnicy) jako powietrze zewnętrzne [ZAŁ]")
            uwagi.append("Kaseta żaluzji/screenu podtynkowa: izolacja za kasetą zmniejszona do "
                         f"{max(0.01, D - kaseta[1] - y_s1):.2f} m; wariant zalecany — kaseta natynkowa albo "
                         "kaseta systemowa z izolacją (deklarowane ψ/f_Rsi producenta).")
        uwagi.append("Przekrój pionowy przez nadproże: sufit ościeża (podsufitka) — R_si wg kierunku strumienia "
                     "(ISO 6946: 0,10 strumień w górę).")
    elif rodzaj == "podokiennik":
        typ = "podokiennik"
        nz = nazwa or f"Podokiennik — rama {opis_pol}, parapet wewn. i zewn."
        if parapet_wewn is not None:
            dane["parapet wewnętrzny"] = (f"{parapet_wewn[0].kod} (λ = {parapet_wewn[0].lam}), d = {parapet_wewn[1]} m, "
                                          f"wysięg do wnętrza {parapet_wewn[2]} m [ZAŁ]")
        if parapet_zewn is not None:
            dane["parapet zewnętrzny"] = (f"{parapet_zewn[0].kod} (λ = {parapet_zewn[0].lam}), d = {parapet_zewn[1]} m, "
                                          f"okapnik {parapet_zewn[2]} m przed licem [ZAŁ]; spadek pominięty")
            uwagi.append("Parapet zewnętrzny (odprowadzenie wody): obróbka na izolacji podparapetowej, wsunięta pod "
                         "profil podparapetowy ramy, okapnik ≥ 3–4 cm przed licem elewacji, spadek ≥ 5 %, zaślepki "
                         "boczne w ościeżach; izolacja pod parapetem ciągła do ramy (brak mostka).")
        uwagi.append("Przekrój pionowy przez podokiennik; parapet wewnętrzny o małym λ (drewno/MDF) — wariant "
                     "ostrożny dla f_Rsi (ogranicza dopływ ciepła do naroża pod parapetem).")
    else:
        nz = nazwa or f"Ościeże okna — rama {opis_pol}"
    # linie schematyczne (układ lokalny s, n → T): taśmy montażu warstwowego, obróbki, spływ wody
    s_t = max(x0, d_t0)
    nf1 = yf0 + d_f
    lin = [("tasma_wewn", [(s_t - 0.012, yf0 - 0.004), (x0 + 0.03, yf0 - 0.004)],
            "taśma paroszczelna od wewnątrz (rama ↔ tynk ościeża)"),
           ("tasma_zewn", [(x0 - 0.035, nf1 + 0.004), (x0 + 0.02, nf1 + 0.004)],
            "taśma paroprzepuszczalna od zewnątrz (pod izolacją ościeża)")]
    if rodzaj == "nadproze":
        lin.append(("obrobka", [(s_izol - 0.06, D + 0.002), (s_izol + 0.002, D + 0.002), (s_izol + 0.014, D + 0.014)],
                    "profil narożny z okapnikiem w ETICS nad oknem"))
    if rodzaj == "podokiennik" and parapet_zewn is not None:
        lin += [("tasma_zewn", [(s_izol - 0.004, nf1 - 0.01), (s_izol - 0.004, D - 0.01)],
                 "taśma / membrana pod parapetem (2. poziom uszczelnienia), wywinięta na ramę"),
                ("obrobka", [(s_izol + parapet_zewn[1], D + parapet_zewn[2]), (s_izol - 0.03, D + parapet_zewn[2]),
                             (s_izol - 0.04, D + parapet_zewn[2] - 0.01)],
                 f"okapnik parapetu {parapet_zewn[2] * 100:.0f} cm przed licem, zaślepki boczne"),
                ("woda", [(s_izol + 0.035, nf1 + 0.03), (s_izol + 0.02, D + parapet_zewn[2] + 0.02)],
                 "spadek parapetu ≥ 5 % na zewnątrz")]
    linie = [_ln(r_, [T(p_) for p_ in xy_], o_) for r_, xy_, o_ in lin]
    wid = T(box(-0.6, -0.1, x_cut, D + 0.1)).bounds
    return Wezel(id, nz, typ, ob_t, strefy, fl, przekroj="poziomy" if rodzaj == "oscieze" else "pionowy",
                 punkty=punkty, widok=wid, psi_domyslne=psi_d, dane=dane, uwagi=uwagi, linie=linie)


def wezel_oscieze_okna(warstwy_sciany: Sequence[Warstwa], U_f: float = 0.95, b_f: float = 0.115, d_f: float = 0.082,
                       U_g: float = 0.50, d_g: float = 0.044, polozenie: str = "w_izolacji", x0: float | None = None,
                       wsuniecie: float = 0.05, zaklad_izolacji: float = 0.03, szczelina: float = 0.015,
                       L: float | None = None,
                       L_g: float = 0.25, theta_i: float | None = None, theta_e: float | None = None,
                       id: str = "WZ-W1", nazwa: str | None = None, zrodlo_okna: str = "",
                       U_w: float | None = None, psi_g: float = 0.0) -> Wezel:
    """Ościeże okna (rzut). Oś x wzdłuż ściany (mur do x = 0, otwór x > 0), oś y w poprzek (lico wewn. y = 0).
    polozenie: 'w_izolacji' — rama przed licem muru w warstwie ocieplenia (ciepły montaż na konsolach, x0 = −0,03
    — rama zachodzi na mur); 'w_murze' — rama w otworze muru, lico zewn. ramy w licu muru, szczelina z pianką;
    'czesciowo' — rama wsunięta w otwór muru na głębokość `wsuniecie`, reszta w warstwie ocieplenia (konwencja
    modelu: 5 cm w murze, 4 cm w izolacji).
    Izolacja ościeża zachodzi na ramę o `zaklad_izolacji`. ψ_inst = L_2D − U_ściany·l − L_2D,okna (okno bez ściany);
    ψ_oi — z korektą U_w·x0 (pole okna w świetle otworu w murze, jak w `energia.bryla`)."""
    return _wezel_krawedz_okna("oscieze", warstwy_sciany, U_f, b_f, d_f, U_g, d_g, polozenie, x0, wsuniecie,
                               zaklad_izolacji, szczelina, L, L_g, theta_i, theta_e, id, nazwa, zrodlo_okna, U_w, psi_g)


def wezel_nadproze(warstwy_sciany: Sequence[Warstwa], U_f: float = 0.95, b_f: float = 0.115, d_f: float = 0.082,
                   U_g: float = 0.50, d_g: float = 0.044, polozenie: str = "czesciowo", x0: float | None = None,
                   wsuniecie: float = 0.05, zaklad_izolacji: float = 0.03, szczelina: float = 0.015,
                   nadproze: tuple[Material, float] | None = None, kaseta: tuple[float, float] | None = None,
                   L: float | None = None, L_g: float = 0.25, theta_i: float | None = None,
                   theta_e: float | None = None, id: str = "WZ-N1", nazwa: str | None = None, zrodlo_okna: str = "",
                   U_w: float | None = None, psi_g: float = 0.0) -> Wezel:
    """Nadproże okna (przekrój pionowy): mur nad otworem z nadprożem (materiał, wysokość; domyślnie żelbet 0,24 m
    [ZAŁ]) w warstwie konstrukcyjnej, izolacja ościeża górnego z zakładem na ramę; opcjonalnie kaseta osłony
    zewnętrznej (żaluzja/screen) w warstwie ocieplenia: (wysokość, głębokość) — izolacja za kasetą zmniejszona."""
    if nadproze is None:
        nadproze = (MATERIALY_DOMYSLNE["ZB"], 0.24)
    return _wezel_krawedz_okna("nadproze", warstwy_sciany, U_f, b_f, d_f, U_g, d_g, polozenie, x0, wsuniecie,
                               zaklad_izolacji, szczelina, L, L_g, theta_i, theta_e, id, nazwa, zrodlo_okna, U_w, psi_g,
                               nadproze=nadproze, kaseta=kaseta)


def wezel_podokiennik(warstwy_sciany: Sequence[Warstwa], U_f: float = 0.95, b_f: float = 0.115, d_f: float = 0.082,
                      U_g: float = 0.50, d_g: float = 0.044, polozenie: str = "czesciowo", x0: float | None = None,
                      wsuniecie: float = 0.05, zaklad_izolacji: float = 0.03, szczelina: float = 0.015,
                      parapet_wewn: tuple[Material, float, float] | None = None,
                      parapet_zewn: tuple[Material, float, float] | None = None,
                      L: float | None = None, L_g: float = 0.25, theta_i: float | None = None,
                      theta_e: float | None = None, id: str = "WZ-P1", nazwa: str | None = None, zrodlo_okna: str = "",
                      U_w: float | None = None, psi_g: float = 0.0) -> Wezel:
    """Podokiennik (przekrój pionowy): mur pod otworem, rama na podkładce/piance, parapet wewnętrzny (materiał,
    grubość, wysięg do wnętrza; domyślnie MDF/drewno 0,025 m, 0,03 m [ZAŁ]) i parapet zewnętrzny — obróbka blacharska
    (domyślnie aluminium 1,5 mm, okapnik 0,04 m przed licem [ZAŁ]) na izolacji podparapetowej."""
    if parapet_wewn is None:
        parapet_wewn = (MATERIALY_DOMYSLNE["PARAPET_WEWN"], 0.025, 0.03)
    if parapet_zewn is None:
        parapet_zewn = (MATERIALY_DOMYSLNE["ALU"], 0.0015, 0.04)
    return _wezel_krawedz_okna("podokiennik", warstwy_sciany, U_f, b_f, d_f, U_g, d_g, polozenie, x0, wsuniecie,
                               zaklad_izolacji, szczelina, L, L_g, theta_i, theta_e, id, nazwa, zrodlo_okna, U_w, psi_g,
                               parapet_wewn=parapet_wewn, parapet_zewn=parapet_zewn)


# ---- progi drzwi / okien do podłogi -------------------------------------------------------------------------
def _param_progu(prog: dict) -> dict:
    """Parametry progu: U_f, b_f, d_f, U_g, d_g, wsuniecie (głębokość ramy w murze od lica zewn. konstrukcji),
    L_g (długość szyby w modelu), mat (podwalina progowa), U_w, psi_g, zrodlo."""
    p = {"U_f": 1.40, "b_f": 0.13, "d_f": 0.09, "U_g": 0.50, "d_g": 0.044, "wsuniecie": 0.05, "L_g": 0.25,
         "mat": MATERIALY_DOMYSLNE["PROG_TERM"], "U_w": None, "psi_g": 0.0, "zrodlo": ""}
    p.update({k: v for k, v in (prog or {}).items() if v is not None})
    if p["U_w"] is None:
        p["U_w"] = U_w_okna(p["U_f"], p["U_g"], p["b_f"], p["psi_g"])
    return p


def _rama_progu(p: dict, x_f0: float, y_f: float, ti: float, te: float, id: str) -> tuple[Obszar, Obszar, Wezel]:
    """Rama (dolny profil) na poziomie y_f i szyba nad nią (przekrój pionowy) + podmodel „drzwi bez ściany”."""
    m_r = material_rama(p["U_f"], p["d_f"], zrodlo=p["zrodlo"])
    m_g = material_szyba(p["U_g"], p["d_g"], zrodlo=p["zrodlo"])
    rama = _obsz(box(x_f0, y_f, x_f0 + p["d_f"], y_f + p["b_f"]), m_r, "rama (próg)")
    xg0 = x_f0 + (p["d_f"] - p["d_g"]) / 2
    szyba = _obsz(box(xg0, y_f + p["b_f"], xg0 + p["d_g"], y_f + p["b_f"] + p["L_g"]), m_g, "szyba")
    return rama, szyba, _okno_model(rama, szyba, ti, te, id, "podokiennik")


def _opis_progu(p: dict, x_f0: float, y_pod: float) -> str:
    return (f"rama U_f = {p['U_f']}, b_f = {p['b_f']} m, d_f = {p['d_f']} m, lico wewn. ramy x = {x_f0:.3f} m "
            f"(wsunięcie w mur {p['wsuniecie']} m); U_g = {p['U_g']}; U_w = {p['U_w']:.3f}; podwalina "
            f"{p['mat'].kod} (λ = {p['mat'].lam}) od y = {y_pod:.3f} m do poziomu posadzki {p['zrodlo']}")


def wezel_prog_strop(warstwy_sciany: Sequence[Warstwa], t_plyty: float = 0.20, mat_plyty: Material | None = None,
                     warstwy_podlogi: Sequence[Warstwa] = (), warstwy_sufitu: Sequence[Warstwa] = (),
                     wysieg: float = 0.0, lacznik: Material | None = LACZNIK_PRZYKLAD, d_lacznika: float = 0.08,
                     prog: dict | None = None, H: float | None = None, L_in: float | None = None,
                     theta_i: float | None = None, theta_e: float | None = None, id: str = "WZ-T2",
                     nazwa: str | None = None) -> Wezel:
    """Próg drzwi / okna do podłogi na kondygnacji powyżej parteru (przekrój pionowy): ściana dolna, strop z wieńcem
    (wysieg = 0) albo płyta wspornikowa balkonu/tarasu z łącznikiem termoizolacyjnym (wysieg > 0), warstwy podłogi
    do lica wewn. ramy, rama na podwalinie progowej, szyba; ocieplenie ściany do spodu ramy (cokolik izolacji nad
    płytą). Układ jak `wezel_wspornik` (wnętrze x < 0, płyta y ∈ [0, t]).
    ψ = L_2D − U_ściany·l − L_2D,drzwi; l_oi = l_e — ściana dolna do poziomu podłogi (= spód ramy)."""
    ti, te = _temperatury(theta_i, theta_e)
    p = _param_progu(prog or {})
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
    x_f0 = x_s1 - p["wsuniecie"]
    x_f1 = x_f0 + p["d_f"]
    y_f = t + t_pod
    y_top = y_f + p["b_f"] + p["L_g"]
    ob: list[Obszar] = []
    for k, (a, b, w) in enumerate(st):
        ob.append(_obsz(box(a, -H, b, 0.0 if k <= ks else y_f), w))
    for y0, y1, w in _stos(warstwy_podlogi, y_f, -1):
        ob.append(_obsz(box(-L_in, y0, x_f0, y1), w))
    for y0, y1, w in _stos(warstwy_sufitu, 0.0, -1):
        ob.append(_obsz(box(-L_in, y0, 0.0, y1), w))
    ob.append(_obsz(box(-L_in, 0.0, x_end, t), mat_plyty, "płyta stropu" + (" / wspornik" if wysieg > 0 else "")))
    if wysieg > 0 and lacznik is not None:
        ob.append(_obsz(box(x_s1, 0.0, x_s1 + d_lacznika, t), lacznik))
    if t_pod > 0:
        ob.append(_obsz(box(x_f0, t, x_f1, y_f), p["mat"], "podwalina progowa (ciepły montaż)"))
    rama, szyba, okno = _rama_progu(p, x_f0, y_f, ti, te, id)
    ob += [rama, szyba]
    S = S_STREFY
    ramka = box(-L_in, -H, max(x_end, x_out) + S, y_top)
    strefy = strefy_z_dopelnienia(ob, ramka, [
        ((-L_in / 2, -H / 2), _nas("pomieszczenie dolne", ti, "wewn")),
        ((-L_in / 2, y_f + (y_top - y_f) / 2), _nas("pomieszczenie górne", ti, "wewn")),
        ((x_out + S / 2, -H / 2), _nas("zewnętrze", te, "zewn"))])
    fl = [ElementFlankujacy("ściana dolna (do poziomu podłogi / spodu ramy)", ("i", "e"), H + y_f, H - t_suf,
                            warstwy=list(warstwy_sciany), l_oi=H + y_f),
          ElementFlankujacy("drzwi (L_2D ramy z szybą, model bez ściany)", ("i", "e"), 1.0, 1.0, wezel_ref=okno)]
    if wysieg > 0:
        nz = nazwa or ("Próg drzwi na płycie wspornikowej (balkon/taras) — " +
                       ("łącznik termoizolacyjny" if lacznik else "płyta ciągła"))
    else:
        nz = nazwa or "Próg okna/drzwi do podłogi na stropie pośrednim (wieniec)"
    dane = {"warstwy ściany": dane_warstw(warstwy_sciany), "płyta": f"{mat_plyty.kod}, t = {t} m, wysięg = {wysieg} m",
            "warstwy podłogi": dane_warstw(warstwy_podlogi), "warstwy sufitu": dane_warstw(warstwy_sufitu),
            "próg": _opis_progu(p, x_f0, t)}
    if wysieg > 0:
        dane["łącznik"] = (f"{lacznik.nazwa}: λ_eq = {lacznik.lam} W/(m·K), d = {d_lacznika} m — {lacznik.zrodlo}"
                           if lacznik else "brak (płyta ciągła przez izolację)")
    uw = ["Ocieplenie ściany prowadzone do spodu ramy (cokolik izolacji XPS nad płytą) — ciągłość izolacji w "
          "płaszczyźnie ramy; hydroizolacja tarasu/balkonu wywinięta ≥ 15 cm lub pod próg (taśma EPDM do ramy), "
          "spadek płyty ≥ 1,5–2 % od budynku, odwodnienie liniowe/rynna przy progu bezbarierowym."]
    linie = [_ln("hydro", [(x_end, t + 0.004), (x_out + 0.004, t + 0.004), (x_out + 0.004, y_f - 0.004),
                           (x_f1 - 0.01, y_f - 0.004)],
                 "hydroizolacja płyty wprowadzona pod próg / taśma EPDM do ramy"),
             _ln("tasma_wewn", [(x_f0 - 0.04, y_f + 0.004), (x_f0 + 0.01, y_f + 0.004)],
                 "taśma paroszczelna rama ↔ posadzka/strop")]
    if wysieg > 0:
        linie.append(_ln("woda", [(x_out + 0.12, t + 0.05), (x_out + max(0.25, min(0.9, wysieg - 0.1)), t + 0.05)],
                         "spadek ≥ 1,5–2 % od budynku; odwodnienie liniowe przy progu"))
    return Wezel(id, nz, "prog", ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"styk podłoga–rama": (x_f0, y_f), "naroże sufit": (0.0, -t_suf)},
                 widok=(-min(L_in, 1.0), -min(H, 1.0), max(x_end, x_out) + 0.1, y_top),
                 dane=dane, uwagi=uw,
                 opis="Przekrój pionowy przez próg; pomieszczenia nad i pod stropem ogrzewane (grupa „i”).")


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
                theta_e: float | None = None, id: str = "WZ-GF1", nazwa: str | None = None,
                prog: dict | None = None) -> Wezel:
    """Cokół: ściana zewnętrzna – podłoga na gruncie – fundament (ława z murem fundamentowym albo płyta fundamentowa)
    z gruntem (λ = 2,0). Przekrój pionowy; lico wewn. ściany x = 0, posadzka ±0,00 = y 0, teren y_teren.
    prog — przekrój przez PRÓG drzwi (HS / wejściowe) w poziomie posadzki zamiast ściany nad posadzką: słownik
    parametrów stolarki (`_param_progu`): rama (U_f, b_f, d_f, wsunięcie w mur) na podwalinie progowej (materiał
    `mat`, od wierzchu płyty konstrukcyjnej do poziomu posadzki), warstwy posadzki do lica wewn. ramy, ocieplenie
    ściany fundamentowej do spodu ramy; ψ_prog = L_2D − U_podłogi·l − L_2D,drzwi (model ramy z szybą).
    Obszar gruntu wg ISO 10211 (model 2D z podłogą): wewnątrz 0,5·b od lica zewn., na zewnątrz 2,5·b, w głąb 2,5·b
    poniżej terenu (b — wymiar charakterystyczny B' = A/(0,5·P) z modelu, `katalog_z_modelu`; 8 m, gdy nieznany) [NZW];
    płaszczyzny odcięcia w gruncie adiabatyczne. ψ_g = L_2D − U_ściany·h − U_podłogi(ISO 13370, B' = b)·l_podłogi
    (wymiary zewn.: l = 0,5·b; wewn. i wewn. całkowite: 0,5·b − w)."""
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
    if prog is not None:
        prog = _param_progu(prog)
        x_f0 = x_s1 - prog["wsuniecie"]
        x_f1 = x_f0 + prog["d_f"]
        H = prog["b_f"] + prog["L_g"]
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
            ob.append(_obsz(box(x_in, y0, (x_s0 if prog is None else x_f0) if k < kf else x_pod, y1), w))
        opis_f = f"ława {b_l}×{h_l} m (spód {spod}), mur fundamentowy {sciana_fund[0].kod} {d_fw} m"
    elif fundament == "plyta":
        for k, (y0, y1, w) in enumerate(fl_st):
            x_k = (x_s0 if prog is None else x_f0) if k < kf else (x_s1 if k == kf else x_out)
            ob.append(_obsz(box(x_in, y0, x_k, y1), w))
        y_izol_dol = fl_st[kf][0]          # spód płyty — izolacja pod płytą (warstwy niżej) sięga do lica zewn.
        spod = y_fb
        opis_f = f"płyta fundamentowa {warstwy_podlogi[kf].mat.kod} {warstwy_podlogi[kf].d} m"
    else:
        raise ValueError(fundament)
    # ściana nad fundamentem (przy progu — tylko do poziomu posadzki; nad posadzką drzwi)
    y_sc = H if prog is None else 0.0
    for k, (a, bb, w) in enumerate(st):
        if k < ks:
            if prog is None:
                ob.append(_obsz(box(a, 0.0, bb, H), w))
        elif k == ks:
            ob.append(_obsz(box(a, y_w0, bb, y_sc), w))
        elif y_prz < y_sc:
            ob.append(_obsz(box(a, y_prz, bb, y_sc), w))
    if blok_termiczny and prog is None:
        ob.append(_obsz(box(x_s0, y_w0, x_s1, y_w0 + blok_termiczny[1]), blok_termiczny[0], "blok termiczny"))
    # izolacja obwodowa + hydroizolacja (strefa cokołu i poniżej terenu)
    d_h = hydro[1] if hydro else 0.0
    if hydro:
        ob.append(_obsz(box(x_s1, y_izol_dol, x_s1 + d_h, y_prz), hydro[0], "hydroizolacja pionowa"))
    if prog is not None and y_prz < 0.0 and hydro:
        ob.append(_obsz(box(x_s1, y_prz, x_s1 + d_h, 0.0), hydro[0], "hydroizolacja pod progiem"))
    ob.append(_obsz(box(x_s1 + d_h, y_izol_dol, x_out, y_prz), izol, "izolacja obwodowa (cokół)"))
    okno = None
    if prog is not None:
        rama, szyba, okno = _rama_progu(prog, x_f0, 0.0, ti, te, id)
        ob.append(_obsz(box(x_f0, y_w0, x_f1, 0.0), prog["mat"], "podwalina progowa (ciepły montaż)"))
        ob += [rama, szyba]
    strefy = strefy_z_dopelnienia(ob, box(x_in, y_dol, x_pr, H), [
        ((-0.5, H / 2), _nas("pomieszczenie", ti, "wewn")),
        ((x_out + 1.0, y_teren + (H - y_teren) / 2), _nas("zewnętrze", te, "zewn"))])
    R_f = R_warstw(warstwy_podlogi)
    U_fl, d_t = U_podlogi_13370(b, x_out, R_f)
    fl_pod = ElementFlankujacy(f"podłoga na gruncie (U wg ISO 13370, B' = {b:.2f} m, d_t = {d_t:.2f} m)", ("i", "e"),
                               0.5 * b, 0.5 * b - x_out, U=U_fl, zrodlo="PN-EN ISO 13370:2017 [NZW]")
    if prog is None:
        fl = [ElementFlankujacy("ściana (od poziomu posadzki)", ("i", "e"), H, H, warstwy=list(warstwy_sciany)), fl_pod]
    else:
        fl = [fl_pod, ElementFlankujacy("drzwi (L_2D ramy z szybą, model bez ściany)", ("i", "e"), 1.0, 1.0,
                                        wezel_ref=okno)]
    wz_nazwa = nazwa or (f"Cokół — ściana / podłoga na gruncie / {'ława' if fundament == 'lawa' else 'płyta'}"
                         if prog is None else "Próg drzwi (HS / wejściowe) na płycie parteru — grunt")
    dane_prog = {}
    if prog is not None:
        dane_prog = {"próg": _opis_progu(prog, x_f0, y_w0)}
    # linie schematyczne: izolacje przeciwwilgociowe/przeciwwodne, strefa cokołu, drenaż, spływ wody
    x_hd = x_s1 + d_h / 2
    linie = []
    if fundament == "lawa":
        linie += [_ln("przeciwwilg", [(x_in, y_w0 + 0.002), (x_s0, y_w0 + 0.002), (x_hd, y_w0 + 0.002)],
                      "izolacja przeciwwilgociowa podłogi (na płycie podkładowej) połączona z poziomą pod murem"),
                  _ln("przeciwwilg", [(xc - b_l / 2, y_lt + 0.002), (xc + b_l / 2, y_lt + 0.002)],
                      "izolacja pozioma na ławie"),
                  _ln("hydro", [(x_hd, y_lt), (x_hd, y_prz)],
                      "izolacja pionowa ściany fundamentowej (KMB / masa bitumiczna) do spodu ETICS")]
        x_dr, y_dr = xc + b_l / 2 + 0.12, spod + 0.08
    else:
        linie += [_ln("hydro", [(x_in, y_izol_dol - 0.002), (x_hd, y_izol_dol - 0.002), (x_hd, y_prz)],
                      "hydroizolacja pod płytą (na XPS) wywinięta na krawędź płyty — ciągła do strefy cokołu")]
        x_dr, y_dr = x_out + 0.30, y_fb + 0.08
    linie += [_ln("hydro", [(x_out + 0.003, y_teren - 0.15), (x_out + 0.003, y_prz + 0.05)],
                  f"uszczelnienie strefy cokołu (masa/tynk mozaikowy) do {h_cokolu * 100:.0f} cm nad terenem"
                  f" ({'≥' if h_cokolu >= 0.30 - 1e-9 else '< WYMAGANE'} 30 cm)"),
              _ln("drenaz", [(x_out + 0.01, y_teren), (x_out + 0.50, y_teren), (x_out + 0.50, y_teren - 0.20),
                             (x_out + 0.01, y_teren - 0.20)], "opaska żwirowa ≥ 50 cm"),
              _ln("drenaz", [(x_dr + 0.05 * math.cos(a_), y_dr + 0.05 * math.sin(a_))
                             for a_ in [k_ * math.pi / 8 for k_ in range(17)]],
                  "drenaż opaskowy DN100 w obsypce żwirowej — decyzja wg badań gruntu / ZWG"),
              _ln("woda", [(x_out + 0.55, y_teren + 0.04), (x_out + 0.98, y_teren + 0.03)],
                  "spadek terenu ≥ 2 % od budynku na ≥ 1,5–2 m")]
    if prog is not None:
        linie.append(_ln("tasma_zewn", [(x_f1 + 0.01, 0.003), (x_out + 0.02, 0.003)],
                         "odwodnienie liniowe przed progiem (próg bezbarierowy)"))
    return Wezel(id, wz_nazwa,
                 "cokol" if prog is None else "prog", ob, strefy, fl, przekroj="pionowy", linie=linie,
                 punkty={"naroże ściana–posadzka": (0.0, 0.0)} if prog is None else
                 {"styk posadzka–rama": (x_f0, 0.0)},
                 siatka={"h_min": 0.003, "h_max": 0.40, "r": 1.25},
                 widok=(-1.2, min(spod, y_fb) - 0.4, x_out + 1.0, 1.0 if prog is None else H),
                 psi_domyslne="GF_cokol" if prog is None else None,
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany), "warstwy podłogi": dane_warstw(warstwy_podlogi),
                       "fundament": opis_f, "izolacja obwodowa": f"{izol.kod} do rzędnej {y_izol_dol:.2f}, "
                       f"cokół do {y_prz:.2f} (teren {y_teren:.2f})",
                       "grunt": f"λ = {grunt.lam} W/(m·K); obszar: wewn. 0,5·b = {0.5 * b} m od lica zewn., "
                                f"zewn. 2,5·b = {2.5 * b} m, głęb. 2,5·b = {2.5 * b} m (b = {b} m)",
                       "U podłogi (ISO 13370)": f"R_f = {R_f:.3f} m²K/W, d_t = {d_t:.3f} m, U = {U_fl:.4f} W/(m²K)"}
                 | ({"blok termiczny": f"{blok_termiczny[0].kod} h = {blok_termiczny[1]} m"} if blok_termiczny else {})
                 | dane_prog,
                 uwagi=["Ściana liczona od poziomu posadzki (±0,00) we wszystkich systemach wymiarów (ψ_oi = ψ_i); "
                        "podłoga wg PN-EN ISO 13370 z B' = b [INT]; b = B' = A/(0,5·P) budynku, gdy podane z modelu.",
                        "Hydroizolacja pionowa ściany fundamentowej (bitumiczna/KMB) i izolacja obwodowa XPS "
                        "(odporna na wodę) do spodu ławy; drenaż opaskowy i odprowadzenie wody opadowej od cokołu "
                        "— poza zakresem cieplnym (wpływ na λ gruntu pominięty, λ = 2,0)."]
                 + (["Próg: wierzch podwaliny = poziom posadzki; uszczelnienie progu taśmą EPDM / hydroizolacją "
                     "wywiniętą na podwalinę; odwodnienie liniowe przed drzwiami HS zalecane (brak spadku przy "
                     "progu bezbarierowym)."] if prog is not None else []))


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
                 linie=[_ln("paro", [(-L, -0.002), (L, -0.002)],
                            "tynk wewnętrzny ciągły — szczelność powietrzna (i gazowa od garażu, WT § 106)"),
                        _ln("tasma_zewn", [(-d_g - 0.01, y_out + 0.004), (0.01, y_out + 0.004)],
                            "styk ściana garażu ↔ ETICS: taśma rozprężna / dylatacja")]
                 if not przerwa_izolacji else
                 [_ln("paro", [(-L, -0.002), (L, -0.002)],
                      "tynk wewnętrzny ciągły — szczelność powietrzna (i gazowa od garażu, WT § 106)")],
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
    r_r = 0.05
    yc_w = y_s1 + d_pozostala + r_r + 0.005
    okrag = lambda xc_, yc_: [(xc_ + r_r * math.cos(k_ * math.pi / 12), yc_ + r_r * math.sin(k_ * math.pi / 12))
                              for k_ in range(25)]
    linie = [_ln("rura", okrag(0.0, yc_w), "rura spustowa DN100 we wnęce ETICS (wariant obliczony)"),
             dict(_ln("rura", okrag(szer_wneki / 2 + 0.25, D + 0.04 + r_r),
                      "wariant zalecany: rura przed licem na obejmach dystansowych (bez wnęki, ψ ≈ 0)"), alt=True)]
    return Wezel(id, nazwa, "rura_spustowa", ob, strefy, fl, przekroj="poziomy", linie=linie,
                 punkty={"lico wewn. za wnęką": (0.0, 0.0)}, widok=(-0.6, -0.1, 0.6, D + 0.25),
                 dane={"warstwy ściany": dane_warstw(warstwy_sciany),
                       "wnęka": f"szer. {szer_wneki} m, pozostała izolacja {d_pozostala} m"},
                 uwagi=["Wariant zalecany: rura przed licem ETICS na obejmach dystansowych (bez wnęki) albo "
                        "wewnętrzna w izolowanym szachcie — ψ ≈ 0."])
