"""Rdzeń modelu budynku „Dom LAMELA” — wczytanie, walidacja i geometria pochodna.

Jedno źródło prawdy: ``model/budynek.yaml`` + ``model/dzialka.yaml`` (kontrakt: ``docs/SCHEMAT_MODELU.md``).

Użycie::

    from lamela.model import load_model
    m = load_model("model/budynek.yaml", "model/dzialka.yaml")      # strict=True -> wyjątek przy BŁĘDACH
    for s in m.sciany("P0"):
        for w in s.warstwy:            # wieloboki warstw po połączeniu naroży (shapely)
            print(s.id, w.mat, w.polygon.area)
    m.pomieszczenia("P1")[0].pow_netto
    m.pow_zabudowy(), m.kubatura_brutto(), m.zestawienie_powierzchni()

CLI::

    PYTHONPATH=src python -m lamela.model model/budynek.yaml model/dzialka.yaml

Szczegóły konwencji (łączenie naroży, obrysy, PN-ISO 9836) — ``src/lamela/README_model.md``.
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import shapely
import yaml
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

# --------------------------------------------------------------------------------------------------
# Stałe
# --------------------------------------------------------------------------------------------------
JOIN_TOL = 0.02          # [m] tolerancja wykrywania połączeń osi ścian
GEOM_TOL = 1e-6          # [m] tolerancja numeryczna
SLIVER_AREA = 2e-5       # [m²] odrzucane drzazgi po operacjach boolowskich
Z_TOL = 0.05             # [m] tolerancja dopasowania rzędnych (płyta ↔ ściana)
SUFIT_D_DOMYSLNA = 0.01  # [m] grubość wykończenia sufitu, gdy podano sam kod materiału

TYPY_PRZEGROD = ("sciana_zewn", "sciana_wewn_nosna", "scianka_dzialowa", "strop", "stropodach",
                 "podloga_na_gruncie", "plyta_fund", "taras", "attyka")
TYPY_SCIAN = ("sciana_zewn", "sciana_wewn_nosna", "scianka_dzialowa", "attyka")
TYPY_OTWOROW = ("okno", "fix", "drzwi", "drzwi_przesuwne_HS", "drzwi_zewn", "brama", "otwor")
KATEGORIE_POM = ("podstawowa", "pomocnicza", "ruchu", "techniczna")
WNETRZE = ("lewa", "prawa", "srodek")

# współczynniki zaliczania powierzchni wg wysokości w świetle (PN-ISO 9836 — praktyka krajowa, patrz README)
PROG_WYS_PELNA = 2.20
PROG_WYS_POLOWA = 1.40


# --------------------------------------------------------------------------------------------------
# Problemy walidacji
# --------------------------------------------------------------------------------------------------
@dataclass
class Problem:
    poziom: str      # "BLAD" | "OSTRZEZENIE" | "INFO"
    miejsce: str     # np. "budynek.yaml: otwory[3] (O0-05)"
    opis: str

    def __str__(self) -> str:
        return f"[{self.poziom}] {self.miejsce}: {self.opis}"


class ModelValidationError(Exception):
    """Model niezgodny ze schematem — lista wszystkich BŁĘDÓW w ``problemy``."""

    def __init__(self, problemy: list[Problem]):
        self.problemy = problemy
        bl = [p for p in problemy if p.poziom == "BLAD"]
        txt = "\n".join(f"  - {p}" for p in bl)
        super().__init__(f"Model zawiera {len(bl)} błąd(ów) zgodności ze schematem:\n{txt}")


# --------------------------------------------------------------------------------------------------
# Pomocnicze funkcje geometryczne
# --------------------------------------------------------------------------------------------------
def _is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)


def _is_pt(v, dim=2) -> bool:
    return isinstance(v, (list, tuple)) and len(v) == dim and all(_is_num(c) for c in v)


def _is_ring(v, dim=2) -> bool:
    return isinstance(v, (list, tuple)) and len(v) >= 3 and all(_is_pt(p, dim) for p in v)


def _is_ring_list(v) -> bool:
    return isinstance(v, (list, tuple)) and all(_is_ring(r) for r in v)


def signed_area(ring) -> float:
    a = 0.0
    n = len(ring)
    for i in range(n):
        x1, y1 = ring[i][0], ring[i][1]
        x2, y2 = ring[(i + 1) % n][0], ring[(i + 1) % n][1]
        a += x1 * y2 - x2 * y1
    return a / 2.0


def make_polygon(ring, holes=None) -> Polygon:
    """Wielobok shapely o orientacji CCW (otwory CW); poprawia nieprawidłowe."""
    p = Polygon([tuple(map(float, q[:2])) for q in ring],
                [[tuple(map(float, q[:2])) for q in h] for h in (holes or [])])
    if not p.is_valid:
        p = shapely.make_valid(p)
        p = unary_union([g for g in _iter_polys(p)])
    if isinstance(p, Polygon):
        return orient(p, 1.0)
    return p


def _iter_polys(g) -> list[Polygon]:
    """Lista wieloboków z dowolnej geometrii (odrzuca linie/punkty)."""
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    if hasattr(g, "geoms"):
        out = []
        for h in g.geoms:
            out.extend(_iter_polys(h))
        return out
    return []


iter_polys = _iter_polys


def clean_geom(g, min_area=SLIVER_AREA):
    """Usuwa drzazgi i części zdegenerowane; zwraca Polygon/MultiPolygon lub pusty Polygon."""
    ps = [orient(p, 1.0) for p in _iter_polys(g) if p.area > min_area]
    if not ps:
        return Polygon()
    if len(ps) == 1:
        return ps[0]
    return MultiPolygon(ps)


def snap(g, grid: float = 1e-6):
    """Przyciąga współrzędne do siatki (usuwa rozbieżności numeryczne na stykach); model precyzji — zmiennoprzecinkowy."""
    if g is None or g.is_empty:
        return g
    return shapely.set_precision(shapely.set_precision(g, grid), 0.0)


def _unit(v):
    v = np.asarray(v, float)
    n = float(np.hypot(v[0], v[1]))
    return v / n if n > 0 else v


def _cross(a, b) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def line_intersection(p, d, q, e):
    """Punkt przecięcia prostych p + a·d oraz q + b·e (None gdy równoległe)."""
    den = _cross(d, e)
    if abs(den) < 1e-12:
        return None
    a = _cross(np.asarray(q) - np.asarray(p), e) / den
    return np.asarray(p, float) + a * np.asarray(d, float)


def half_plane(c, d, keep_pt, big=1e4) -> Polygon:
    """Półpłaszczyzna ograniczona prostą (c, d), zawierająca punkt keep_pt (duży prostokąt)."""
    c = np.asarray(c, float)
    d = _unit(d)
    nrm = np.array([-d[1], d[0]])
    if np.dot(np.asarray(keep_pt) - c, nrm) < 0:
        nrm = -nrm
    a = c - d * big
    b = c + d * big
    return Polygon([tuple(a), tuple(b), tuple(b + nrm * big), tuple(a + nrm * big)])


# --------------------------------------------------------------------------------------------------
# Encje
# --------------------------------------------------------------------------------------------------
@dataclass
class Material:
    kod: str
    nazwa: str = ""
    lambda_: float | None = None
    rho: float | None = None
    cp: float | None = None
    mu: float | None = None
    kreskowanie: str | None = None
    kolor: str | None = None
    raw: dict = field(default_factory=dict)


@dataclass
class Warstwa:
    mat: str
    d: float
    konstrukcyjna: bool = False


@dataclass
class Przegroda:
    kod: str
    nazwa: str
    typ: str
    warstwy: list[Warstwa]
    raw: dict = field(default_factory=dict)

    @property
    def grubosc(self) -> float:
        return sum(w.d for w in self.warstwy)

    @property
    def idx_konstr(self) -> int | None:
        """Indeks warstwy konstrukcyjnej (gdy brak oznaczenia — najgrubsza warstwa)."""
        for i, w in enumerate(self.warstwy):
            if w.konstrukcyjna:
                return i
        if not self.warstwy:
            return None
        return max(range(len(self.warstwy)), key=lambda i: self.warstwy[i].d)

    @property
    def ma_oznaczona_konstr(self) -> bool:
        return any(w.konstrukcyjna for w in self.warstwy)

    def d_nad_konstr(self) -> float:
        """Przegrody poziome (warstwy od góry): grubość warstw nad warstwą konstrukcyjną.
        Gdy brak oznaczonej warstwy konstrukcyjnej — cała przegroda leży nad płytą."""
        if not self.ma_oznaczona_konstr:
            return self.grubosc
        k = self.idx_konstr
        return sum(w.d for w in self.warstwy[:k])

    def d_pod_konstr(self) -> float:
        if not self.ma_oznaczona_konstr:
            return 0.0
        k = self.idx_konstr
        return sum(w.d for w in self.warstwy[k + 1:])

    def warstwy_nad_konstr(self) -> list[Warstwa]:
        if not self.ma_oznaczona_konstr:
            return list(self.warstwy)
        return self.warstwy[: self.idx_konstr]

    def warstwy_pod_konstr(self) -> list[Warstwa]:
        if not self.ma_oznaczona_konstr:
            return []
        return self.warstwy[self.idx_konstr + 1:]


@dataclass
class Kondygnacja:
    id: str
    nazwa: str
    rzedna: float
    wys_kondygnacji: float
    wys_w_swietle: float | None
    podloga: str | None
    idx: int = 0
    raw: dict = field(default_factory=dict)


@dataclass
class WarstwaSciany:
    """Warstwa ściany po połączeniu naroży. t0 < t1 — odsunięcia wzdłuż normalnej lewej osi."""
    idx: int
    mat: str
    d: float
    t0: float
    t1: float
    konstrukcyjna: bool
    strona: int            # 0 — konstrukcja; +1 — strona wnętrza (dla 'srodek': lewa); -1 — zewnętrze (prawa)
    ranga: int             # 0 — konstrukcja, 1 — przylegająca, 2 — następna...
    klasa: str             # konstrukcja | izolacja | wykonczenie | inna
    polygon: Any = None    # shapely Polygon/MultiPolygon (rzut)
    z0: float = 0.0
    z1: float = 0.0


class Sciana:
    """Ściana: oś (środek warstwy konstrukcyjnej), warstwy, wieloboki warstw po łączeniu naroży."""

    def __init__(self, raw: dict, idx: int, przegroda: Przegroda):
        self.raw = raw
        self.idx = idx
        self.id = str(raw["id"])
        self.kond = str(raw["kond"])
        self.przegroda_kod = str(raw["przegroda"])
        self.przegroda = przegroda
        self.p1 = np.array(raw["os"][0], float)
        self.p2 = np.array(raw["os"][1], float)
        v = self.p2 - self.p1
        self.L = float(np.hypot(*v))
        self.u = v / self.L
        self.n = np.array([-self.u[1], self.u[0]])     # normalna lewa
        self.wnetrze = raw.get("wnetrze", "srodek")
        self.sgn_int = -1 if self.wnetrze == "prawa" else 1
        self.z_od_raw = raw.get("z_od")
        self.z_do_raw = raw.get("z_do")
        self.z_od = 0.0
        self.z_do = 0.0
        self.warstwy: list[WarstwaSciany] = []
        self._build_layers()
        self.otwory: list[Otwor] = []
        self.polaczenia: dict[int, dict] = {}

    # --- geometria lokalna ---
    def pt(self, s: float, t: float) -> np.ndarray:
        return self.p1 + s * self.u + t * self.n

    def st(self, p) -> tuple[float, float]:
        d = np.asarray(p, float) - self.p1
        return float(d @ self.u), float(d @ self.n)

    @property
    def typ(self) -> str:
        return self.przegroda.typ

    @property
    def ext_side(self) -> int | None:
        """Strona zewnętrzna jako znak odsunięcia t (None dla ścian 'srodek')."""
        if self.wnetrze == "srodek":
            return None
        return -self.sgn_int

    @property
    def t_min(self) -> float:
        return min(w.t0 for w in self.warstwy)

    @property
    def t_max(self) -> float:
        return max(w.t1 for w in self.warstwy)

    @property
    def grubosc(self) -> float:
        return self.t_max - self.t_min

    @property
    def warstwa_konstr(self) -> WarstwaSciany:
        return next(w for w in self.warstwy if w.konstrukcyjna)

    def face_t(self, side: int, kind: str = "all") -> float:
        """Odsunięcie lica: side=+1/-1 (strona n), kind='k' (konstrukcja) lub 'all' (wykończone)."""
        if kind == "k":
            k = self.warstwa_konstr
            return k.t1 if side > 0 else k.t0
        return self.t_max if side > 0 else self.t_min

    def prio(self) -> tuple:
        rank = {"sciana_zewn": 3, "sciana_wewn_nosna": 2, "attyka": 2, "scianka_dzialowa": 1}.get(self.typ, 0)
        return (round(self.warstwa_konstr.d, 4), rank, round(self.L, 3), -self.idx)

    def _build_layers(self):
        ws = self.przegroda.warstwy
        k = self.przegroda.idx_konstr
        dk = ws[k].d
        e = {k: (-dk / 2, dk / 2)}
        pos = -dk / 2
        for i in range(k - 1, -1, -1):
            e[i] = (pos - ws[i].d, pos)
            pos -= ws[i].d
        pos = dk / 2
        for i in range(k + 1, len(ws)):
            e[i] = (pos, pos + ws[i].d)
            pos += ws[i].d
        for i, w in enumerate(ws):
            a, b = sorted((-self.sgn_int * e[i][0], -self.sgn_int * e[i][1]))
            strona = 0 if i == k else (1 if i < k else -1)
            self.warstwy.append(WarstwaSciany(idx=i, mat=w.mat, d=w.d, t0=a, t1=b, konstrukcyjna=(i == k),
                                              strona=strona, ranga=abs(i - k), klasa="inna"))

    def axis_line(self) -> LineString:
        return LineString([tuple(self.p1), tuple(self.p2)])

    def band(self, t0=None, t1=None, s0=0.0, s1=None) -> Polygon:
        t0 = self.t_min if t0 is None else t0
        t1 = self.t_max if t1 is None else t1
        s1 = self.L if s1 is None else s1
        pts = [self.pt(s0, t0), self.pt(s1, t0), self.pt(s1, t1), self.pt(s0, t1)]
        return Polygon([tuple(p) for p in pts])

    @property
    def polygon(self):
        """Rzut całej ściany (suma warstw po połączeniu naroży)."""
        return unary_union([w.polygon for w in self.warstwy if w.polygon is not None and not w.polygon.is_empty])

    def __repr__(self):
        return f"Sciana({self.id}, {self.kond}, {self.przegroda_kod}, L={self.L:.3f})"


@dataclass
class Otwor:
    raw: dict
    id: str
    sciana_id: str
    symbol: str | None
    typ: str
    odl: float
    szer: float
    wys: float
    parapet: float
    otwieranie: dict | None
    oslona: str | None
    sciana: Sciana | None = None
    kond: str | None = None
    # pochodne
    s0: float = 0.0
    s1: float = 0.0
    z0: float = 0.0
    z1: float = 0.0

    @property
    def p0(self) -> np.ndarray:
        return self.sciana.pt(self.s0, 0.0)

    @property
    def p1(self) -> np.ndarray:
        return self.sciana.pt(self.s1, 0.0)

    @property
    def srodek(self) -> np.ndarray:
        return self.sciana.pt((self.s0 + self.s1) / 2, 0.0)

    @property
    def kierunek_zewn(self) -> np.ndarray | None:
        """Wersor ku zewnątrz (None dla ścian wewnętrznych 'srodek')."""
        es = self.sciana.ext_side
        return None if es is None else es * self.sciana.n

    @property
    def oscieze(self) -> tuple[float, float]:
        """Zakres ościeża w poprzek ściany (t_min, t_max) — pełna grubość przegrody."""
        return self.sciana.t_min, self.sciana.t_max

    @property
    def footprint(self) -> Polygon:
        """Rzut otworu przez całą grubość ściany (układ globalny)."""
        return self.sciana.band(s0=self.s0, s1=self.s1)

    def narozniki_3d(self, t: float = 0.0) -> list[tuple[float, float, float]]:
        """Narożniki otworu w świetle muru w płaszczyźnie odsuniętej o t od osi (CCW patrząc od strony +n)."""
        a = self.sciana.pt(self.s0, t)
        b = self.sciana.pt(self.s1, t)
        return [(a[0], a[1], self.z0), (b[0], b[1], self.z0), (b[0], b[1], self.z1), (a[0], a[1], self.z1)]

    @property
    def rama_t(self) -> tuple[float, float]:
        """Położenie ramy w poprzek ściany (t0, t1): przy licu zewn. warstwy konstrukcyjnej (montaż w warstwie
        izolacji, głęb. 9 cm, wysunięta 4 cm w izolację); dla ścian wewnętrznych — w osi."""
        w = self.sciana
        es = w.ext_side
        if es is None:
            k = w.warstwa_konstr
            gl = min(0.10, max(0.06, k.d * 0.6))
            return (-gl / 2, gl / 2)
        tf = w.face_t(es, "k")
        a, b = tf - es * 0.05, tf + es * 0.04
        return (min(a, b), max(a, b))


@dataclass
class Pomieszczenie:
    raw: dict
    id: str
    kond: str
    nazwa: str
    punkt: tuple | None
    wielobok: list | None
    kategoria: str
    pobyt_ludzi: bool
    posadzka: str | None
    sciany_wyk: str | None
    sufit: str | None
    temp: float | None
    went: dict | None
    # pochodne
    polygon: Any = None            # z lic ścian wykończonych
    polygon_podlogi: Any = None    # polygon minus otwory w stropie (np. nad klatką schodową)
    wysokosc: float | None = None  # wysokość w świetle [m]
    zrodlo: str = ""               # 'punkt' | 'wielobok' | 'brak'

    @property
    def pow_netto(self) -> float:
        g = self.polygon_podlogi if self.polygon_podlogi is not None else self.polygon
        return float(g.area) if g is not None else 0.0

    @property
    def obwod(self) -> float:
        if self.polygon is None:
            return 0.0
        return float(sum(p.exterior.length + sum(i.length for i in p.interiors) for p in _iter_polys(self.polygon)))

    @property
    def wsp_wysokosci(self) -> float:
        return wsp_wysokosci(self.wysokosc)

    @property
    def pow_zaliczona(self) -> float:
        """Powierzchnia netto z uwzględnieniem wysokości w świetle (100/50/0 %)."""
        return self.pow_netto * self.wsp_wysokosci

    @property
    def kubatura_netto(self) -> float:
        return self.pow_netto * (self.wysokosc or 0.0)


def wsp_wysokosci(h: float | None) -> float:
    """Zaliczanie powierzchni wg wysokości w świetle: ≥2,20 m — 100 %, 1,40–2,20 m — 50 %, <1,40 m — 0 %."""
    if h is None:
        return 1.0
    if h >= PROG_WYS_PELNA - 1e-9:
        return 1.0
    if h >= PROG_WYS_POLOWA - 1e-9:
        return 0.5
    return 0.0


# --------------------------------------------------------------------------------------------------
# Specyfikacja pól (walidacja zgodności ze schematem)
# --------------------------------------------------------------------------------------------------
# typy: str, num, num?, bool, dict, dict?, list, pt, pt3, seg, ring, ring?, rings, polyline3, enum:<a,b>, any
TYPY_ELEMENTOW_ZEWN = ("kratownica_pnacza", "oslona_lamelowa")
F = {
    "kondygnacje": {"id": (1, "str"), "nazwa": (0, "str"), "rzedna": (1, "num"), "wys_kondygnacji": (1, "num"),
                    "wys_w_swietle": (0, "num"), "podloga": (0, "str?")},
    "sciany": {"id": (1, "str"), "kond": (1, "str"), "przegroda": (1, "str"), "os": (1, "seg"),
               "wnetrze": (1, "enum:" + ",".join(WNETRZE)), "z_od": (0, "num?"), "z_do": (0, "num?"),
               "tarcza": (0, "any")},   # obliczenia konstrukcyjne: ściana-tarcza żelbetowa (bool lub słownik opcji)
    "otwory": {"id": (1, "str"), "sciana": (1, "str"), "symbol": (0, "str?"), "typ": (1, "enum:" + ",".join(TYPY_OTWOROW)),
               "odl": (1, "num"), "szer": (1, "num"), "wys": (1, "num"), "parapet": (1, "num"),
               "otwieranie": (0, "dict?"), "oslona": (0, "str?"), "kwatery": (0, "num?")},
    "pomieszczenia": {"id": (1, "str"), "kond": (1, "str"), "nazwa": (1, "str"), "punkt": (0, "pt?"),
                      "wielobok": (0, "ring?"), "kategoria": (1, "enum:" + ",".join(KATEGORIE_POM)),
                      "pobyt_ludzi": (0, "bool"), "posadzka": (0, "str?"), "sciany_wyk": (0, "str?"),
                      "sufit": (0, "str?"), "temp": (0, "num?"), "went": (0, "dict?"), "wys": (0, "num?")},
    "stropy": {"id": (1, "str"), "nad": (1, "str"), "wierzch": (1, "num"), "grubosc": (1, "num"),
               "obrys": (1, "ring"), "otwory": (0, "rings?"), "podloga": (0, "str?"), "sufit": (0, "str?"),
               "mat": (0, "str?")},
    "dachy": {"id": (1, "str"), "obrys": (1, "ring"), "plyta": (1, "dict"), "przegroda": (1, "str"),
              "spadek": (0, "num?"), "attyka": (0, "dict?"), "wpusty": (0, "list?"), "rzygacze": (0, "list?"),
              "otwory": (0, "rings?"), "mat": (0, "str?")},
    "wsporniki_plyty": {"id": (1, "str"), "obrys": (1, "ring"), "wierzch": (1, "num"), "grubosc": (1, "num"),
                        "przegroda": (0, "str?"), "lacznik_termiczny": (0, "bool"), "mat": (0, "str?"),
                        "attyka": (0, "dict?")},
    "slupy": {"id": (1, "str"), "xy": (1, "pt"), "przekroj": (1, "str"), "mat": (1, "str"), "z_od": (1, "num"),
              "z_do": (1, "num")},
    "belki": {"id": (1, "str"), "os": (1, "seg"), "b": (1, "num"), "h": (1, "num"), "spod": (1, "num"),
              "mat": (1, "str")},
    "schody": {"id": (1, "str"), "z_kond": (1, "str"), "na_kond": (1, "str"), "liczba_stopni": (1, "num"),
               "wys_stopnia": (1, "num"), "szer_stopnia": (1, "num"), "biegi": (1, "list"),
               "spoczniki": (0, "list?"), "mat": (0, "str?")},
    "balustrady": {"id": (1, "str"), "polilinia": (1, "polyline3"), "wys": (1, "num"), "typ": (0, "str?")},
    "lamele": {"id": (1, "str"), "elewacja": (1, "str"), "linia": (1, "seg"), "z_od": (1, "num"), "z_do": (1, "num"),
               "rozstaw": (1, "num"), "b": (1, "num"), "h": (1, "num"), "odsuniecie": (1, "num"), "mat": (1, "str")},
    "tarasy": {"id": (1, "str"), "obrys": (1, "ring"), "rzedna": (1, "num"), "nawierzchnia": (0, "str?"),
               "grubosc": (0, "num?")},
    # wyposażenie zewnętrzne elewacji (wydanie, decyzja Inwestora K-13): kratownica na pnącza na konsolach, osłona lamelowa urządzenia
    "elementy_zewn": {"id": (1, "str"), "typ": (1, "enum:" + ",".join(TYPY_ELEMENTOW_ZEWN)), "linia": (1, "polyline"),
                      "z_od": (1, "num"), "z_do": (1, "num"), "mat": (1, "str"), "elewacja": (0, "str?"), "sciana": (0, "str?"),
                      "odsuniecie": (0, "num?"), "oczko": (0, "num?"), "pret": (0, "num?"), "rama": (0, "num?"),
                      "rozstaw": (0, "num?"), "b": (0, "num?"), "h": (0, "num?"), "konsole": (0, "dict?"),
                      "pnacza": (0, "dict?"), "urzadzenie": (0, "dict?"), "obiekt": (0, "str?"), "uwagi": (0, "str?")},
}
SEKCJE_BUDYNEK = {"meta": "dict", "uklad": "dict", "osie": "dict", "kondygnacje": "list", "materialy": "dict",
                  "przegrody": "dict", "sciany": "list", "otwory": "list", "pomieszczenia": "list", "stropy": "list",
                  "dachy": "list", "wsporniki_plyty": "list", "slupy": "list", "belki": "list", "fundamenty": "dict",
                  "schody": "list", "balustrady": "list", "lamele": "list", "tarasy": "list", "elementy_zewn": "list"}
WYMAGANE_BUDYNEK = ("uklad", "kondygnacje", "materialy", "przegrody", "sciany")
ID_WZORCE = {"sciany": r"^S\d+-\d+[A-Za-z]?$", "otwory": r"^O\d+-\d+[A-Za-z]?$", "pomieszczenia": r"^\d+\.\d+[A-Za-z]?$",
             "stropy": r"^ST\d+", "dachy": r"^D\d+", "slupy": r"^SL\d+", "belki": r"^(B|N|W)\d+", "schody": r"^SCH\d+"}

SEKCJE_DZIALKA = {"uklad": "dict", "dzialka": "dict", "sasiedzi": "list", "droga": "dict", "linia_zabudowy": "list",
                  "teren": "dict", "utwardzenia": "list", "zielen": "list", "drzewa": "list", "ogrodzenie": "list",
                  "bramy": "list", "miejsca_postojowe": "list", "odpady": "dict", "uzbrojenie": "dict",
                  "retencja": "dict", "obszar_oddzialywania": "dict"}
WYMAGANE_DZIALKA = ("uklad", "dzialka", "teren")
F_DZ = {
    "sasiedzi": {"nr": (0, "str"), "obrys": (0, "ring?"), "zabudowa": (0, "any"), "opis": (0, "str?"),
                 "wys": (0, "num?"), "dach": (0, "str?")},
    "utwardzenia": {"id": (0, "str"), "obrys": (1, "ring"), "nawierzchnia": (0, "str?"), "spadek": (0, "num?")},
    "zielen": {"id": (0, "str"), "obrys": (1, "ring"), "typ": (1, "enum:trawnik,rabata,zywoplot"),
               "wys": (0, "num?")},
    "drzewa": {"xy": (1, "pt"), "gat": (0, "str?"), "sr_korony": (1, "num"), "istn": (0, "bool"),
               "do_wyciecia": (0, "bool"), "wys": (0, "num?"), "id": (0, "str")},
    "ogrodzenie": {"linia": (1, "polyline"), "wys": (1, "num"), "typ": (0, "str?")},
    "bramy": {"xy": (1, "pt"), "szer": (1, "num"), "typ": (1, "enum:przesuwna,furtka,skrzydlowa,dwuskrzydlowa"),
              "kierunek": (0, "pt?"), "wys": (0, "num?")},
    "miejsca_postojowe": {"obrys": (1, "ring"), "typ": (1, "enum:wiata,zewn,garaz"), "id": (0, "str"),
                          "auto": (0, "bool")},
}


def _fmt_id(v) -> str:
    return str(v)


def _check_type(val, typ: str) -> bool:
    opt = typ.endswith("?")
    t = typ.rstrip("?")
    if val is None:
        return opt
    if t == "any":
        return True
    if t == "str":
        return isinstance(val, (str, int, float)) and not isinstance(val, bool)
    if t == "num":
        return _is_num(val)
    if t == "bool":
        return isinstance(val, bool)
    if t == "dict":
        return isinstance(val, dict)
    if t == "list":
        return isinstance(val, list)
    if t == "pt":
        return _is_pt(val)
    if t == "seg":
        return isinstance(val, (list, tuple)) and len(val) == 2 and all(_is_pt(p) for p in val)
    if t == "ring":
        return _is_ring(val)
    if t == "rings":
        return _is_ring_list(val)
    if t == "polyline":
        return isinstance(val, (list, tuple)) and len(val) >= 2 and all(_is_pt(p) for p in val)
    if t == "polyline3":
        return isinstance(val, (list, tuple)) and len(val) >= 2 and all(_is_pt(p, 3) for p in val)
    if t.startswith("enum:"):
        return val in t[5:].split(",")
    return True


_TYP_OPIS = {"str": "tekst", "num": "liczba", "bool": "true/false", "dict": "słownik", "list": "lista",
             "pt": "punkt [x, y]", "seg": "odcinek [[x1, y1], [x2, y2]]", "ring": "wielobok [[x, y], ...] (≥3 pkt)",
             "rings": "lista wieloboków", "polyline": "polilinia [[x, y], ...]",
             "polyline3": "polilinia 3D [[x, y, z], ...]", "any": "dowolny"}


def _typ_opis(typ: str) -> str:
    t = typ.rstrip("?")
    if t.startswith("enum:"):
        return "jedna z wartości: " + ", ".join(t[5:].split(","))
    s = _TYP_OPIS.get(t, t)
    return s + (" lub null" if typ.endswith("?") else "")


# --------------------------------------------------------------------------------------------------
# Działka
# --------------------------------------------------------------------------------------------------
class Dzialka:
    """Dane działki (``dzialka.yaml``) z transformacją do układu budynku."""

    def __init__(self, raw: dict, zero_abs: float):
        self.raw = raw or {}
        u = self.raw.get("uklad") or {}
        self.przes = np.array(u.get("przesuniecie") or [0.0, 0.0], float)
        self.obrot = float(u.get("obrot") or 0.0)
        self.zero_abs = float(zero_abs)
        a = math.radians(self.obrot)
        self._R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])

    # budynek → działka: p_d = R·p_b + t
    def do_dzialki(self, xy) -> np.ndarray:
        p = np.asarray(xy, float)
        return (self._R @ p[..., :2].T).T + self.przes

    def do_budynku(self, xy) -> np.ndarray:
        p = np.asarray(xy, float)
        return (self._R.T @ (p[..., :2] - self.przes).T).T

    def ring_bud(self, ring) -> list[tuple[float, float]]:
        if ring is None:
            return []
        arr = self.do_budynku(np.asarray([q[:2] for q in ring], float))
        return [tuple(map(float, q)) for q in arr]

    def poly_bud(self, ring) -> Polygon:
        return make_polygon(self.ring_bud(ring))

    def z_wzgl(self, H: float) -> float:
        """Rzędna bezwzględna [m n.p.m.] → względna (±0,00 budynku)."""
        return float(H) - self.zero_abs

    @property
    def obrys(self) -> Polygon | None:
        d = self.raw.get("dzialka") or {}
        return self.poly_bud(d["obrys"]) if d.get("obrys") else None

    def teren_punkty(self) -> np.ndarray:
        """Punkty wysokościowe w układzie budynku: kolumny x, y, z (z względne)."""
        pts = (self.raw.get("teren") or {}).get("punkty") or []
        if not pts:
            return np.zeros((0, 3))
        arr = np.asarray(pts, float)
        xy = self.do_budynku(arr[:, :2])
        return np.column_stack([xy, arr[:, 2] - self.zero_abs])

    def lista(self, klucz: str) -> list:
        v = self.raw.get(klucz)
        return v if isinstance(v, list) else []


# --------------------------------------------------------------------------------------------------
# Model
# --------------------------------------------------------------------------------------------------
class Model:
    """Model budynku (+ działki) z walidacją i geometrią pochodną. Tworzyć przez :func:`load_model`."""

    def __init__(self, budynek: dict, dzialka: dict | None = None, *, src_budynek: str = "budynek.yaml",
                 src_dzialka: str = "dzialka.yaml"):
        self.raw = budynek if isinstance(budynek, dict) else {}
        self.raw_dz = dzialka if isinstance(dzialka, dict) else None
        self.src_b = src_budynek
        self.src_d = src_dzialka
        self.problemy: list[Problem] = []
        self._kond: dict[str, Kondygnacja] = {}
        self._mat: dict[str, Material] = {}
        self._prz: dict[str, Przegroda] = {}
        self._sciany: list[Sciana] = []
        self._otwory: list[Otwor] = []
        self._pom: list[Pomieszczenie] = []
        self._free_cache: dict[str, Any] = {}
        self.dz: Dzialka | None = None
        if not isinstance(budynek, dict):
            self._err(self.src_b, "plik nie zawiera słownika YAML (sekcji najwyższego poziomu)")
            return
        self._validate_raw()
        self._build()

    # ---------------- problemy ----------------
    def _add(self, poziom, miejsce, opis):
        self.problemy.append(Problem(poziom, miejsce, opis))

    def _err(self, miejsce, opis):
        self._add("BLAD", miejsce, opis)

    def _warn(self, miejsce, opis):
        self._add("OSTRZEZENIE", miejsce, opis)

    def _info(self, miejsce, opis):
        self._add("INFO", miejsce, opis)

    @property
    def bledy(self) -> list[Problem]:
        return [p for p in self.problemy if p.poziom == "BLAD"]

    @property
    def ostrzezenia(self) -> list[Problem]:
        return [p for p in self.problemy if p.poziom == "OSTRZEZENIE"]

    def raport_walidacji(self) -> str:
        if not self.problemy:
            return "Walidacja: brak uwag."
        lines = [f"Walidacja: {len(self.bledy)} błędów, {len(self.ostrzezenia)} ostrzeżeń, "
                 f"{len(self.problemy) - len(self.bledy) - len(self.ostrzezenia)} informacji"]
        for poz in ("BLAD", "OSTRZEZENIE", "INFO"):
            for p in self.problemy:
                if p.poziom == poz:
                    lines.append(f"  {p}")
        return "\n".join(lines)

    # ---------------- walidacja surowych danych ----------------
    def _loc(self, sek, i, item) -> str:
        ident = item.get("id") if isinstance(item, dict) else None
        return f"{self.src_b}: {sek}[{i}]" + (f" ({ident})" if ident is not None else "")

    def _check_fields(self, sek: str, i: int, item, spec: dict, src: str | None = None, loc: str | None = None):
        loc = loc or (f"{src}: {sek}[{i}]" if src else self._loc(sek, i, item))
        if not isinstance(item, dict):
            self._err(loc, "element musi być słownikiem {pole: wartość}")
            return False
        ok = True
        for pole, (wym, typ) in spec.items():
            if pole not in item:
                if wym:
                    self._err(loc, f"brak wymaganego pola '{pole}' ({_typ_opis(typ)})")
                    ok = False
                continue
            if not _check_type(item[pole], typ):
                if item[pole] is None and wym:
                    self._err(loc, f"pole '{pole}' nie może być puste ({_typ_opis(typ)})")
                else:
                    self._err(loc, f"pole '{pole}' ma nieprawidłową wartość {item[pole]!r} — oczekiwano: {_typ_opis(typ)}")
                ok = False
        for pole in item:
            if pole not in spec:
                self._info(loc, f"pole '{pole}' spoza schematu — ignorowane przez rdzeń modelu")
        return ok

    def _validate_raw(self):
        r = self.raw
        src = self.src_b
        for sek in WYMAGANE_BUDYNEK:
            if sek not in r or r[sek] in (None, [], {}):
                self._err(src, f"brak wymaganej sekcji '{sek}'")
        for sek, typ in SEKCJE_BUDYNEK.items():
            if sek in r and r[sek] is not None and not _check_type(r[sek], typ):
                self._err(f"{src}: {sek}", f"sekcja musi być typu: {_TYP_OPIS[typ]}")
        for sek in r:
            if sek not in SEKCJE_BUDYNEK:
                self._info(f"{src}: {sek}", "sekcja spoza schematu — ignorowana przez rdzeń modelu")
        u = r.get("uklad") or {}
        if isinstance(u, dict):
            if not _is_num(u.get("zero_abs")):
                self._err(f"{src}: uklad", "brak lub nieprawidłowe pole 'zero_abs' (rzędna bezwzględna ±0,00, m n.p.m.)")
            if "azymut_osi_y" in u and not _is_num(u.get("azymut_osi_y")):
                self._err(f"{src}: uklad", "pole 'azymut_osi_y' musi być liczbą [°]")
        # identyfikatory: unikalność, format, pomieszczenia jako tekst
        seen: dict[str, str] = {}
        for sek in F:
            lst = r.get(sek)
            if not isinstance(lst, list):
                continue
            for i, it in enumerate(lst):
                if not isinstance(it, dict) or "id" not in it:
                    continue
                v = it["id"]
                if sek == "pomieszczenia" and isinstance(v, float):
                    self._warn(self._loc(sek, i, it), f"identyfikator pomieszczenia zapisany jako liczba ({v!r}) — "
                                                      "ujmij w cudzysłów, np. \"0.10\" (YAML gubi końcowe zera)")
                    it["id"] = f"{v:.2f}"
                v = _fmt_id(it["id"])
                it["id"] = v
                if v in seen:
                    self._err(self._loc(sek, i, it), f"zdublowany identyfikator '{v}' (wcześniej w sekcji {seen[v]})")
                seen[v] = sek
                pat = ID_WZORCE.get(sek)
                if pat and not re.match(pat, v):
                    self._warn(self._loc(sek, i, it), f"identyfikator '{v}' nie odpowiada konwencji schematu ({pat})")

    # ---------------- budowa ----------------
    def _build(self):
        r = self.raw
        src = self.src_b
        # układ
        u = r.get("uklad") if isinstance(r.get("uklad"), dict) else {}
        self.zero_abs = float(u.get("zero_abs")) if _is_num(u.get("zero_abs")) else 0.0
        self.azymut_osi_y = float(u.get("azymut_osi_y") or 0.0) if _is_num(u.get("azymut_osi_y") or 0.0) else 0.0
        self.meta = r.get("meta") if isinstance(r.get("meta"), dict) else {}
        self.osie = r.get("osie") if isinstance(r.get("osie"), dict) else {}

        # materiały
        mats = r.get("materialy") if isinstance(r.get("materialy"), dict) else {}
        for kod, m in mats.items():
            kod = str(kod)
            if not isinstance(m, dict):
                self._err(f"{src}: materialy.{kod}", "definicja materiału musi być słownikiem")
                continue
            for pole in ("nazwa", "lambda"):
                if pole not in m:
                    self._warn(f"{src}: materialy.{kod}", f"brak pola '{pole}'")
            if "kolor" in m and not (isinstance(m["kolor"], str) and re.match(r"^#[0-9a-fA-F]{6}$", m["kolor"])):
                self._warn(f"{src}: materialy.{kod}", f"kolor {m['kolor']!r} nie jest w formacie #rrggbb")
            self._mat[kod] = Material(kod=kod, nazwa=str(m.get("nazwa", "")), lambda_=m.get("lambda"), rho=m.get("rho"),
                                      cp=m.get("cp"), mu=m.get("mu"), kreskowanie=m.get("kreskowanie"),
                                      kolor=m.get("kolor"), raw=m)

        # przegrody
        prz = r.get("przegrody") if isinstance(r.get("przegrody"), dict) else {}
        for kod, p in prz.items():
            kod = str(kod)
            loc = f"{src}: przegrody.{kod}"
            if not isinstance(p, dict):
                self._err(loc, "definicja przegrody musi być słownikiem")
                continue
            typ = p.get("typ")
            if typ not in TYPY_PRZEGROD:
                self._err(loc, f"nieprawidłowy typ {typ!r} — dozwolone: {', '.join(TYPY_PRZEGROD)}")
            wars = p.get("warstwy")
            if not isinstance(wars, list) or not wars:
                self._err(loc, "brak listy 'warstwy'")
                continue
            ws = []
            ok = True
            for j, w in enumerate(wars):
                if not isinstance(w, dict) or "mat" not in w or not _is_num(w.get("d")):
                    self._err(f"{loc}.warstwy[{j}]", "warstwa wymaga pól 'mat' (kod materiału) i 'd' (grubość, m)")
                    ok = False
                    continue
                if str(w["mat"]) not in self._mat:
                    self._err(f"{loc}.warstwy[{j}]", f"odwołanie do nieistniejącego materiału '{w['mat']}'")
                if w["d"] <= 0:
                    self._err(f"{loc}.warstwy[{j}]", f"grubość warstwy musi być > 0 (jest {w['d']})")
                    ok = False
                ws.append(Warstwa(mat=str(w["mat"]), d=float(w["d"]), konstrukcyjna=bool(w.get("konstrukcyjna", False))))
            if not ok or not ws:
                continue
            nk = sum(1 for w in ws if w.konstrukcyjna)
            if nk > 1:
                self._err(loc, f"więcej niż jedna warstwa oznaczona 'konstrukcyjna: true' ({nk})")
            if nk == 0 and typ in TYPY_SCIAN:
                self._warn(loc, "brak warstwy 'konstrukcyjna: true' — jako konstrukcyjną przyjęto najgrubszą warstwę")
            self._prz[kod] = Przegroda(kod=kod, nazwa=str(p.get("nazwa", "")), typ=str(typ), warstwy=ws, raw=p)

        # kondygnacje
        for i, k in enumerate(r.get("kondygnacje") or []):
            if not self._check_fields("kondygnacje", i, k, F["kondygnacje"]):
                continue
            kid = str(k["id"])
            pod = k.get("podloga")
            if pod is not None and str(pod) not in self._prz:
                self._err(self._loc("kondygnacje", i, k), f"odwołanie do nieistniejącej przegrody podłogi '{pod}'")
            self._kond[kid] = Kondygnacja(id=kid, nazwa=str(k.get("nazwa", kid)), rzedna=float(k["rzedna"]),
                                          wys_kondygnacji=float(k["wys_kondygnacji"]),
                                          wys_w_swietle=k.get("wys_w_swietle"), podloga=str(pod) if pod else None,
                                          raw=k)
        ks = sorted(self._kond.values(), key=lambda k: k.rzedna)
        for i, k in enumerate(ks):
            k.idx = i
        self._kond = {k.id: k for k in ks}

        # pozostałe sekcje — walidacja pól i odwołań
        for sek in ("stropy", "dachy", "wsporniki_plyty", "slupy", "belki", "schody", "balustrady", "lamele", "tarasy",
                    "elementy_zewn"):
            lst = r.get(sek) or []
            if not isinstance(lst, list):
                continue
            for i, it in enumerate(lst):
                self._check_fields(sek, i, it, F[sek])
        self._validate_refs()

        # ściany
        for i, s in enumerate(r.get("sciany") or []):
            if not self._check_fields("sciany", i, s, F["sciany"]):
                continue
            loc = self._loc("sciany", i, s)
            if str(s["kond"]) not in self._kond:
                self._err(loc, f"odwołanie do nieistniejącej kondygnacji '{s['kond']}'")
                continue
            pk = str(s["przegroda"])
            if pk not in self._prz:
                self._err(loc, f"odwołanie do nieistniejącej przegrody '{pk}'")
                continue
            if self._prz[pk].typ not in TYPY_SCIAN:
                self._err(loc, f"przegroda '{pk}' ma typ '{self._prz[pk].typ}', a ściana wymaga typu ściennego "
                               f"({', '.join(TYPY_SCIAN)})")
                continue
            p1, p2 = s["os"]
            if math.hypot(p2[0] - p1[0], p2[1] - p1[1]) < 0.01:
                self._err(loc, "oś ściany ma zerową długość")
                continue
            if self._prz[pk].typ == "sciana_zewn" and s["wnetrze"] == "srodek":
                self._warn(loc, "ściana zewnętrzna z 'wnetrze: srodek' — warstwy rozłożone symetrycznie od listy")
            self._sciany.append(Sciana(s, i, self._prz[pk]))
        self._sc_by_id = {s.id: s for s in self._sciany}

        # rzędne ścian (null → wartości domyślne)
        for s in self._sciany:
            self._resolve_wall_z(s)
        self._check_wall_overlaps()

        # łączenie naroży
        for kid in self._kond:
            self._join_walls([s for s in self._sciany if s.kond == kid])
        for s in self._sciany:
            self._layer_classes(s)
            self._layer_z(s)
        self._harmonize_ext_bottoms()

        # otwory
        self._build_openings()
        # pomieszczenia
        self._build_rooms()
        # spójność rzędnych, kolizje płyt
        self._check_levels()
        self._check_slab_overlaps()
        # działka
        if self.raw_dz is not None:
            self._validate_dzialka()
            self.dz = Dzialka(self.raw_dz, self.zero_abs)
            self._check_on_plot()

    def _validate_refs(self):
        r = self.raw
        mats = self._mat
        for i, st in enumerate(r.get("stropy") or []):
            if not isinstance(st, dict):
                continue
            loc = self._loc("stropy", i, st)
            if "nad" in st and str(st["nad"]) not in self._kond:
                self._err(loc, f"odwołanie do nieistniejącej kondygnacji 'nad: {st['nad']}'")
            if st.get("podloga") and str(st["podloga"]) not in self._prz:
                self._err(loc, f"odwołanie do nieistniejącej przegrody podłogi '{st['podloga']}'")
            if st.get("sufit") and str(st["sufit"]) not in mats and str(st["sufit"]) not in self._prz:
                self._warn(loc, f"wykończenie sufitu '{st['sufit']}' nie jest kodem materiału ani przegrody")
            self._check_poly(loc, "obrys", st.get("obrys"))
            for j, h in enumerate(st.get("otwory") or []):
                self._check_poly(loc, f"otwory[{j}]", h)
                if _is_ring(h) and _is_ring(st.get("obrys")):
                    if not make_polygon(st["obrys"]).buffer(1e-6).contains(make_polygon(h)):
                        self._err(loc, f"otwór w stropie otwory[{j}] wychodzi poza obrys płyty")
        for i, d in enumerate(r.get("dachy") or []):
            if not isinstance(d, dict):
                continue
            loc = self._loc("dachy", i, d)
            if d.get("przegroda") and str(d["przegroda"]) not in self._prz:
                self._err(loc, f"odwołanie do nieistniejącej przegrody '{d['przegroda']}'")
            pl = d.get("plyta")
            if isinstance(pl, dict):
                for pole in ("wierzch", "grubosc"):
                    if not _is_num(pl.get(pole)):
                        self._err(loc, f"brak lub nieprawidłowe pole 'plyta.{pole}'")
                p = self._prz.get(str(d.get("przegroda")))
                if p is not None and p.ma_oznaczona_konstr and _is_num(pl.get("grubosc")):
                    dk = p.warstwy[p.idx_konstr].d
                    if abs(dk - pl["grubosc"]) > 0.005:
                        self._warn(loc, f"grubość płyty {pl['grubosc']:.3f} ≠ warstwa konstrukcyjna przegrody "
                                        f"{p.kod} ({dk:.3f})")
            at = d.get("attyka")
            if isinstance(at, dict):
                for pole in ("wys_nad_pokryciem", "szer"):
                    if not _is_num(at.get(pole)):
                        self._err(loc, f"brak lub nieprawidłowe pole 'attyka.{pole}'")
            self._check_poly(loc, "obrys", d.get("obrys"))
            for j, w in enumerate(d.get("wpusty") or []):
                if isinstance(w, dict):          # SCHEMAT p. 6: {xy: [x, y], dn, podgrzewany}
                    w = w.get("xy")
                if not _is_pt(w):
                    self._err(loc, f"wpusty[{j}] musi być punktem [x, y] lub {{xy: [x, y], dn, podgrzewany}}")
                elif _is_ring(d.get("obrys")) and not make_polygon(d["obrys"]).buffer(1e-6).contains(Point(w)):
                    self._warn(loc, f"wpust wpusty[{j}] {w} leży poza obrysem dachu")
        for i, w in enumerate(r.get("wsporniki_plyty") or []):
            if not isinstance(w, dict):
                continue
            loc = self._loc("wsporniki_plyty", i, w)
            if w.get("przegroda") and str(w["przegroda"]) not in self._prz:
                self._err(loc, f"odwołanie do nieistniejącej przegrody '{w['przegroda']}'")
            if w.get("mat") and str(w["mat"]) not in mats:
                self._err(loc, f"odwołanie do nieistniejącego materiału '{w['mat']}'")
            self._check_poly(loc, "obrys", w.get("obrys"))
        for sek in ("slupy", "belki", "lamele", "elementy_zewn"):
            for i, it in enumerate(r.get(sek) or []):
                if isinstance(it, dict) and it.get("mat") is not None and str(it["mat"]) not in mats:
                    self._err(self._loc(sek, i, it), f"odwołanie do nieistniejącego materiału '{it['mat']}'")
        sc_ids = {str(w.get("id")) for w in (r.get("sciany") or []) if isinstance(w, dict)}
        for i, it in enumerate(r.get("elementy_zewn") or []):
            if not isinstance(it, dict):
                continue
            loc = self._loc("elementy_zewn", i, it)
            if _is_num(it.get("z_od")) and _is_num(it.get("z_do")) and it["z_do"] <= it["z_od"]:
                self._err(loc, "z_do musi być większe od z_od")
            if it.get("sciana") is not None and str(it["sciana"]) not in sc_ids:
                self._err(loc, f"odwołanie do nieistniejącej ściany '{it['sciana']}'")
            if it.get("typ") == "kratownica_pnacza" and not (_is_num(it.get("odsuniecie")) and it["odsuniecie"] > 0):
                self._err(loc, "kratownica_pnacza: wymagane 'odsuniecie' > 0 (od lica ocieplenia — bez styku z ETICS)")
            if it.get("typ") == "oslona_lamelowa" and _is_num(it.get("rozstaw")) and _is_num(it.get("b")) \
                    and it["rozstaw"] <= it["b"]:
                self._err(loc, "oslona_lamelowa: rozstaw ≤ b — osłona pełna (wymagana ażurowa: przepływ powietrza, R290)")
        for i, it in enumerate(r.get("slupy") or []):
            if isinstance(it, dict) and _is_num(it.get("z_od")) and _is_num(it.get("z_do")) and it["z_do"] <= it["z_od"]:
                self._err(self._loc("slupy", i, it), "z_do musi być większe od z_od")
        for i, sch in enumerate(r.get("schody") or []):
            if not isinstance(sch, dict):
                continue
            loc = self._loc("schody", i, sch)
            for pole in ("z_kond", "na_kond"):
                if pole in sch and str(sch[pole]) not in self._kond:
                    self._err(loc, f"odwołanie do nieistniejącej kondygnacji '{pole}: {sch[pole]}'")
            biegi = sch.get("biegi") if isinstance(sch.get("biegi"), list) else []
            n_st = 0
            for j, b in enumerate(biegi):
                if not isinstance(b, dict):
                    self._err(f"{loc}.biegi[{j}]", "bieg musi być słownikiem")
                    continue
                for pole, typ in (("start", "pt"), ("kierunek", "pt"), ("szer", "num"), ("stopni", "num")):
                    if not _check_type(b.get(pole), typ):
                        self._err(f"{loc}.biegi[{j}]", f"brak lub nieprawidłowe pole '{pole}' ({_typ_opis(typ)})")
                if _is_pt(b.get("kierunek")) and math.hypot(*b["kierunek"]) < 1e-9:
                    self._err(f"{loc}.biegi[{j}]", "kierunek biegu ma zerową długość")
                if _is_num(b.get("stopni")):
                    n_st += int(b["stopni"])
            if biegi and _is_num(sch.get("liczba_stopni")) and n_st != int(sch["liczba_stopni"]):
                self._warn(loc, f"suma stopni w biegach ({n_st}) ≠ liczba_stopni ({sch['liczba_stopni']})")
            for j, sp in enumerate(sch.get("spoczniki") or []):
                if not isinstance(sp, dict) or not _is_ring(sp.get("obrys")) or not _is_num(sp.get("rzedna")):
                    self._err(f"{loc}.spoczniki[{j}]", "spocznik wymaga pól 'obrys' (wielobok) i 'rzedna' (liczba)")
            zk, nk = self._kond.get(str(sch.get("z_kond"))), self._kond.get(str(sch.get("na_kond")))
            if zk and nk and _is_num(sch.get("liczba_stopni")) and _is_num(sch.get("wys_stopnia")):
                dh = nk.rzedna - zk.rzedna
                hh = sch["liczba_stopni"] * sch["wys_stopnia"]
                if abs(dh - hh) > 0.01:
                    self._warn(loc, f"liczba_stopni × wys_stopnia = {hh:.3f} m ≠ różnica rzędnych kondygnacji "
                                    f"{zk.id}→{nk.id} = {dh:.3f} m")
        for i, t in enumerate(r.get("tarasy") or []):
            if isinstance(t, dict):
                self._check_poly(self._loc("tarasy", i, t), "obrys", t.get("obrys"))
        for i, lam in enumerate(r.get("lamele") or []):
            if isinstance(lam, dict) and _is_num(lam.get("rozstaw")) and _is_num(lam.get("b")):
                if lam["rozstaw"] <= lam["b"]:
                    self._err(self._loc("lamele", i, lam), f"rozstaw lameli ({lam['rozstaw']}) ≤ szerokość lameli "
                                                           f"b ({lam['b']}) — lamele nachodzą na siebie")
        fu = r.get("fundamenty")
        if isinstance(fu, dict):
            if fu.get("typ") not in ("lawy", "plyta", None):
                self._err(f"{self.src_b}: fundamenty", f"typ {fu.get('typ')!r} — dozwolone: lawy | plyta")
            for i, e in enumerate(fu.get("elementy") or []):
                loc = f"{self.src_b}: fundamenty.elementy[{i}]" + (f" ({e.get('id')})" if isinstance(e, dict) else "")
                if not isinstance(e, dict):
                    self._err(loc, "element musi być słownikiem")
                    continue
                if "os" in e:
                    for pole, typ in (("os", "seg"), ("b", "num"), ("h", "num"), ("spod", "num")):
                        if not _check_type(e.get(pole), typ):
                            self._err(loc, f"brak lub nieprawidłowe pole '{pole}' ({_typ_opis(typ)})")
                elif "obrys" in e:
                    for pole, typ in (("obrys", "ring"), ("h", "num"), ("spod", "num")):
                        if not _check_type(e.get(pole), typ):
                            self._err(loc, f"brak lub nieprawidłowe pole '{pole}' ({_typ_opis(typ)})")
                else:
                    self._err(loc, "element fundamentu wymaga 'os' (ława/stopa) lub 'obrys' (płyta)")

    def _check_poly(self, loc, pole, ring):
        if not _is_ring(ring):
            return
        if signed_area(ring) < 0:
            self._warn(loc, f"wielobok '{pole}' ma obieg zgodny z ruchem wskazówek zegara (CW) — schemat wymaga CCW; "
                            "orientacja poprawiona automatycznie")
        p = Polygon([tuple(q[:2]) for q in ring])
        if not p.is_valid:
            self._err(loc, f"wielobok '{pole}' jest nieprawidłowy (samoprzecięcia): {shapely.is_valid_reason(p)}")
        if len(ring) >= 2 and tuple(ring[0]) == tuple(ring[-1]):
            self._warn(loc, f"wielobok '{pole}' powtarza pierwszy punkt na końcu (schemat: bez powtórzenia)")

    # ---------------- rzędne ścian ----------------
    def _slab_elems(self):
        """Lista płyt (typ, id, wielobok, spód, wierzch konstr., wierzch wykończony, dane)."""
        out = []
        for st in self.raw.get("stropy") or []:
            if isinstance(st, dict) and _is_ring(st.get("obrys")) and _is_num(st.get("wierzch")) and _is_num(st.get("grubosc")):
                out.append(dict(typ="strop", id=st.get("id"), poly=make_polygon(st["obrys"], st.get("otwory") or []),
                                poly_full=make_polygon(st["obrys"]), spod=st["wierzch"] - st["grubosc"],
                                wierzch=st["wierzch"], top=st["wierzch"], raw=st, nad=str(st.get("nad"))))
        for d in self.raw.get("dachy") or []:
            if isinstance(d, dict) and _is_ring(d.get("obrys")) and isinstance(d.get("plyta"), dict):
                pl = d["plyta"]
                if not (_is_num(pl.get("wierzch")) and _is_num(pl.get("grubosc"))):
                    continue
                p = self._prz.get(str(d.get("przegroda")))
                d_nad = p.d_nad_konstr() if p is not None and p.ma_oznaczona_konstr else 0.25
                top = pl["wierzch"] + d_nad
                at = d.get("attyka") if isinstance(d.get("attyka"), dict) else None
                top_at = top + float(at.get("wys_nad_pokryciem", 0)) if at else None
                out.append(dict(typ="dach", id=d.get("id"), poly=make_polygon(d["obrys"], d.get("otwory") or []),
                                poly_full=make_polygon(d["obrys"]), spod=pl["wierzch"] - pl["grubosc"],
                                wierzch=pl["wierzch"], top=top, top_attyki=top_at, raw=d))
        for w in self.raw.get("wsporniki_plyty") or []:
            if isinstance(w, dict) and _is_ring(w.get("obrys")) and _is_num(w.get("wierzch")) and _is_num(w.get("grubosc")):
                out.append(dict(typ="wspornik", id=w.get("id"), poly=make_polygon(w["obrys"]),
                                poly_full=make_polygon(w["obrys"]), spod=w["wierzch"] - w["grubosc"],
                                wierzch=w["wierzch"], top=w["wierzch"], raw=w))
        return out

    def kond_z_od(self, kid: str) -> float:
        """Domyślna rzędna spodu ścian kondygnacji = wierzch płyty konstrukcyjnej pod kondygnacją."""
        k = self._kond[kid]
        prev = self._kond_prev(kid)
        if prev is not None:
            for st in self.raw.get("stropy") or []:
                if isinstance(st, dict) and str(st.get("nad")) == prev.id and _is_num(st.get("wierzch")):
                    return float(st["wierzch"])
        p = self._prz.get(k.podloga) if k.podloga else None
        if p is not None:
            return k.rzedna - p.d_nad_konstr()
        return k.rzedna

    def _kond_prev(self, kid):
        ks = list(self._kond.values())
        i = [k.id for k in ks].index(kid)
        return ks[i - 1] if i > 0 else None

    def _kond_next(self, kid):
        ks = list(self._kond.values())
        i = [k.id for k in ks].index(kid)
        return ks[i + 1] if i + 1 < len(ks) else None

    def _slab_above(self, kid: str, pt, z_min: float) -> dict | None:
        """Najniższa płyta nad punktem (stropy nad kondygnacją, dachy, wsporniki) ze spodem > z_min."""
        best = None
        P = Point(tuple(pt))
        for sl in self._slab_elems():
            if sl["typ"] == "strop" and sl["nad"] != kid:
                continue
            if sl["spod"] <= z_min + 0.3:
                continue
            if sl["poly_full"].buffer(0.02).contains(P):
                if best is None or sl["spod"] < best["spod"]:
                    best = sl
        return best

    def _resolve_wall_z(self, s: Sciana):
        k = self._kond[s.kond]
        s.z_od = float(s.z_od_raw) if _is_num(s.z_od_raw) else self.kond_z_od(s.kond)
        if _is_num(s.z_do_raw):
            s.z_do = float(s.z_do_raw)
        else:
            mid = s.pt(s.L / 2, 0.0)
            sl = self._slab_above(s.kond, mid, s.z_od)
            if sl is None:
                # szukaj w kilku punktach wzdłuż osi
                for f in (0.1, 0.3, 0.7, 0.9):
                    sl = self._slab_above(s.kond, s.pt(s.L * f, 0.0), s.z_od)
                    if sl:
                        break
            if sl is not None:
                s.z_do = float(sl["spod"])
            else:
                s.z_do = k.rzedna + k.wys_kondygnacji - 0.20
                self._warn(f"{self.src_b}: sciany ({s.id})", "nie znaleziono płyty nad ścianą — przyjęto "
                                                             f"z_do = rzędna + wys_kondygnacji − 0,20 = {s.z_do:.2f}")
        if s.z_do <= s.z_od:
            self._err(f"{self.src_b}: sciany ({s.id})", f"z_do ({s.z_do:.3f}) ≤ z_od ({s.z_od:.3f})")

    def _check_wall_overlaps(self):
        for a, b in combinations(self._sciany, 2):
            if a.kond != b.kond or abs(_cross(a.u, b.u)) > 1e-3:
                continue
            # równoległe — sprawdź współliniowość i nakładanie zakresów
            sa, ta = a.st(b.p1)
            sb, tb = a.st(b.p2)
            if abs(ta) > JOIN_TOL or abs(tb) > JOIN_TOL:
                continue
            lo, hi = sorted((sa, sb))
            ov = min(hi, a.L) - max(lo, 0.0)
            if ov > JOIN_TOL:
                self._err(f"{self.src_b}: sciany ({a.id}, {b.id})",
                          f"osie ścian nakładają się na długości {ov:.3f} m (ściany współliniowe)")

    # ---------------- łączenie naroży ----------------
    def _join_walls(self, walls: list[Sciana]):
        if not walls:
            return
        cuts: dict[tuple[int, int], tuple] = {}
        for w in walls:
            for end in (0, 1):
                cuts[(w.idx, end)] = self._joint_for(w, end, walls)
        # wieloboki warstw
        for w in walls:
            for lay in w.warstwy:
                cs = cuts[(w.idx, 0)][0 if lay.konstrukcyjna else 1]
                ce = cuts[(w.idx, 1)][0 if lay.konstrukcyjna else 1]
                lay.polygon = self._layer_quad(w, lay.t0, lay.t1, cs, ce)
        # porządkowanie: priorytet warstwa konstr. > przyległe > dalsze; w klasie — priorytet ściany
        items = []
        for w in walls:
            for lay in w.warstwy:
                items.append((lay.ranga, tuple(-x for x in w.prio()), w.idx, lay.idx, w, lay))
        items.sort(key=lambda t: t[:4])
        occ = None
        for *_, w, lay in items:
            g = lay.polygon
            if g is None or g.is_empty:
                continue
            g = snap(g)
            if occ is not None and g.intersects(occ):
                g = clean_geom(g.difference(occ))
            else:
                g = clean_geom(g)
            lay.polygon = g
            if not g.is_empty:
                occ = g if occ is None else unary_union([occ, g])

    def _cut_perp(self, s_val):
        return ("perp", float(s_val))

    def _cut_face(self, other: Sciana, t_face: float):
        c = other.pt(0.0, t_face)
        return ("line", c, other.u.copy())

    def _joint_for(self, w: Sciana, end: int, walls: list[Sciana]):
        """Zwraca (cięcie_konstr, cięcie_pozostałe) dla końca 'end' ściany w."""
        J = w.p1 if end == 0 else w.p2
        ub = w.u if end == 0 else -w.u
        s_end = 0.0 if end == 0 else w.L
        perp = self._cut_perp(s_end)
        tol = JOIN_TOL
        partners_end: list[tuple[Sciana, int]] = []
        partners_T: list[Sciana] = []
        for v in walls:
            if v is w:
                continue
            if min(w.z_do, v.z_do) - max(w.z_od, v.z_od) <= 0.01:
                continue
            matched = False
            for vend in (0, 1):
                Jv = v.p1 if vend == 0 else v.p2
                if np.hypot(*(Jv - J)) < tol:
                    partners_end.append((v, vend))
                    matched = True
                    break
            if matched:
                continue
            s, t = v.st(J)
            if v.t_min - tol <= t <= v.t_max + tol and -tol <= s <= v.L + tol:
                near = None
                for vend in (0, 1):
                    Jv = v.p1 if vend == 0 else v.p2
                    sw, tw = w.st(Jv)
                    if (w.t_min - tol <= tw <= w.t_max + tol and -tol - w.grubosc <= sw <= w.L + tol + w.grubosc
                            and np.hypot(*(Jv - J)) < max(w.grubosc, v.grubosc) + tol):
                        near = vend
                if near is not None:
                    partners_end.append((v, near))
                elif tol < s < v.L - tol:
                    partners_T.append(v)
        info = {"J": tuple(J), "typ": "wolny", "z": []}
        w.polaczenia[end] = info
        if partners_T:
            M = max(partners_T, key=lambda m: m.prio())
            side = 1 if float(M.n @ ub) > 0 else -1
            info.update(typ="T", z=[M.id])
            return (self._cut_face(M, M.face_t(side, "k")), self._cut_face(M, M.face_t(side, "all")))
        if not partners_end:
            return (perp, perp)
        if len(partners_end) == 1:
            v, vend = partners_end[0]
            ubv = v.u if vend == 0 else -v.u
            cosang = float(ub @ ubv)
            if cosang < -0.999:
                info.update(typ="ciagla", z=[v.id])
                return (perp, perp)
            if cosang > 0.999:
                self._warn(f"{self.src_b}: sciany ({w.id}, {v.id})", "ściany zbiegają się pod kątem 0° (nakładanie)")
                return (perp, perp)
            X = line_intersection(w.p1, w.u, v.p1, v.u)
            if X is None:
                X = J
            info.update(typ="L", z=[v.id])
            H = w if w.prio() >= v.prio() else v
            # zgodność stron zewnętrznych (izolacja z izolacją)
            conv_w = -1 if float(w.n @ ubv) > 0 else 1
            conv_v = -1 if float(v.n @ ub) > 0 else 1
            ew, ev = w.ext_side, v.ext_side
            compatible = (ew is None and ev is None) or (ew is not None and ev is not None and
                                                         ((ew == conv_w) == (ev == conv_v)))
            far_side_v = -1 if float(v.n @ ub) > 0 else 1   # strona v odległa od korpusu w
            if compatible:
                miter = ("line", X, _unit(ub + ubv))
                if H is w:
                    ck = self._cut_face(v, v.face_t(far_side_v, "k"))
                else:
                    side = 1 if float(v.n @ ub) > 0 else -1
                    ck = self._cut_face(v, v.face_t(side, "k"))
                return (ck, miter)
            info["typ"] = "L-doczołowe"
            if H is w:
                cf = self._cut_face(v, v.face_t(far_side_v, "all"))
                return (cf, cf)
            side = 1 if float(v.n @ ub) > 0 else -1
            return (self._cut_face(v, v.face_t(side, "k")), self._cut_face(v, v.face_t(side, "all")))
        # ≥ 3 ściany w węźle
        group = [(w, end)] + partners_end

        def ubd(item):
            ww, ee = item
            return ww.u if ee == 0 else -ww.u

        pairs = [(a, b) for a, b in combinations(group, 2) if float(ubd(a) @ ubd(b)) < -0.999]
        info.update(typ="wezel", z=[v.id for v, _ in partners_end])
        if pairs:
            A, B = max(pairs, key=lambda pr: min(pr[0][0].prio(), pr[1][0].prio()))
            if w is A[0] or w is B[0]:
                return (perp, perp)
            M = A[0] if A[0].prio() >= B[0].prio() else B[0]
            side = 1 if float(M.n @ ub) > 0 else -1
            return (self._cut_face(M, M.face_t(side, "k")), self._cut_face(M, M.face_t(side, "all")))
        H = max(group, key=lambda it: it[0].prio())[0]
        if H is w:
            ext = max(max(abs(v.t_min), abs(v.t_max)) for v, _ in partners_end)
            c = self._cut_perp(-ext if end == 0 else w.L + ext)
            return (c, c)
        side = 1 if float(H.n @ ub) > 0 else -1
        return (self._cut_face(H, H.face_t(side, "k")), self._cut_face(H, H.face_t(side, "all")))

    def _s_on_cut(self, w: Sciana, t: float, cut) -> float:
        if cut[0] == "perp":
            return cut[1]
        _, c, d = cut
        den = _cross(w.u, d)
        if abs(den) < 1e-9:
            return None
        q = w.p1 + t * w.n
        return -_cross(q - c, d) / den

    def _layer_quad(self, w: Sciana, t0: float, t1: float, cs, ce):
        sa0, sa1 = self._s_on_cut(w, t0, cs), self._s_on_cut(w, t1, cs)
        sb0, sb1 = self._s_on_cut(w, t0, ce), self._s_on_cut(w, t1, ce)
        if sa0 is None or sa1 is None:
            sa0 = sa1 = 0.0
        if sb0 is None or sb1 is None:
            sb0 = sb1 = w.L
        pts = [w.pt(sa0, t0), w.pt(sb0, t0), w.pt(sb1, t1), w.pt(sa1, t1)]
        p = Polygon([tuple(q) for q in pts])
        if not p.is_valid or p.area < SLIVER_AREA:
            p = clean_geom(shapely.make_valid(p))
        return orient(p, 1.0) if isinstance(p, Polygon) and not p.is_empty else p

    # ---------------- klasy i rzędne warstw ----------------
    def _klasa_mat(self, kod: str) -> str:
        m = self._mat.get(kod)
        naz = (m.nazwa if m else "").lower()
        k = kod.upper()
        lam = m.lambda_ if m and _is_num(m.lambda_) else None
        if re.search(r"EPS|XPS|PIR|PUR|WELN|WEŁN|MW\d|IZOL|STYRO|WOOL|PUSTKA", k) or \
                re.search(r"styropian|wełn|weln|polistyren|pianka|izolac", naz) or (lam is not None and lam < 0.06):
            return "izolacja"
        if re.search(r"TYNK|FARB|GLAD|GŁAD|OKLAD|OKŁAD|PLYT|GK", k) or re.search(r"tynk|okładz|farb", naz):
            return "wykonczenie"
        return "inna"

    def _layer_classes(self, s: Sciana):
        for lay in s.warstwy:
            lay.klasa = "konstrukcja" if lay.konstrukcyjna else self._klasa_mat(lay.mat)

    def _layer_z(self, s: Sciana):
        """Zakresy z warstw: warstwy zewnętrzne (ETICS) przedłużane na czoła płyt i attyki."""
        es = s.ext_side
        for lay in s.warstwy:
            lay.z0, lay.z1 = s.z_od, s.z_do
        if es is None or s.typ != "sciana_zewn":
            return
        z_top, z_bot = s.z_do, s.z_od
        tk = s.face_t(es, "k")
        tout = s.face_t(es, "all")
        probe_out = s.pt(s.L / 2, tout + es * 0.05)
        probe_in = s.pt(s.L / 2, tk - es * 0.01)
        slabs = self._slab_elems()
        p_out = Point(tuple(probe_out))

        def ciagla_na_zewnatrz(sl) -> bool:
            """Płyta przechodzi przed licem ściany w inną płytę/dach na tym samym poziomie (wspornik stropu, dach przy
            uskoku bryły) — czoła płyty nie ma, więc warstw zewnętrznych ściany nie przedłuża się na jej wysokość."""
            return any(o is not sl and o["typ"] in ("strop", "dach") and abs(o["wierzch"] - sl["wierzch"]) <= Z_TOL
                       and o["poly_full"].contains(p_out) for o in slabs)

        for sl in slabs:
            if abs(sl["spod"] - s.z_do) > Z_TOL:
                continue
            if sl["typ"] == "strop" and sl["nad"] != s.kond:
                continue
            P = sl["poly_full"]
            if P.buffer(0.02).contains(Point(tuple(probe_in))) and not P.contains(p_out) and not ciagla_na_zewnatrz(sl):
                if sl["typ"] == "dach":
                    z_top = max(z_top, sl.get("top_attyki") or sl["top"])
                else:
                    z_top = max(z_top, sl["wierzch"])
        prev = self._kond_prev(s.kond)
        s._ext_dol_wolne = True     # czy warstwy zewnętrzne można obniżyć w narożu (harmonizacja) — nie, gdy pod nimi jest
        #                             ocieplenie ściany niższej (lico w linii) albo płyta ciągła przed licem (uskok bryły)
        if prev is None:
            # najniższa kondygnacja: ocieplenie cokołu do spodu płyty fundamentowej pod ścianą (fundamenty typu „plyta”; wydanie —
            # weryfikacja V1-06: dół izolacji = wierzch żebra, bez kolizji z żebrem), inaczej 0,30 m poniżej wierzchu konstrukcji
            z_bot = s.z_od - 0.30
            fu = self.raw.get("fundamenty") if isinstance(self.raw.get("fundamenty"), dict) else {}
            if fu.get("typ") == "plyta":
                for e in fu.get("elementy") or []:
                    if isinstance(e, dict) and _is_ring(e.get("obrys")) and _is_num(e.get("spod")) and _is_num(e.get("h")) \
                            and abs(float(e["spod"]) + float(e["h"]) - s.z_od) <= 0.20 \
                            and make_polygon(e["obrys"]).buffer(0.05).contains(Point(tuple(probe_in))):
                        z_bot = float(e["spod"])
                        break
        else:
            below = [x for x in self._sciany if x.kond == prev.id and x.ext_side is not None]
            aligned = False
            for x in below:
                g = x.polygon
                if g is not None and not g.is_empty and g.buffer(0.01).contains(Point(tuple(s.pt(s.L / 2, tout - es * 0.03)))):
                    aligned = True
                    break
            if not aligned:
                for sl in slabs:
                    if abs(sl["wierzch"] - s.z_od) > Z_TOL:
                        continue
                    P = sl["poly_full"]
                    if P.buffer(0.02).contains(Point(tuple(probe_in))) and not P.contains(p_out) and not ciagla_na_zewnatrz(sl):
                        z_bot = min(z_bot, sl["spod"])
            s._ext_dol_wolne = z_bot < s.z_od - 1e-6
        for lay in s.warstwy:
            if lay.strona == es:
                lay.z0, lay.z1 = z_bot, z_top

    def _harmonize_ext_bottoms(self):
        """Naroża L: warstwy zewnętrzne obu ścian schodzą do tej samej rzędnej (brak odsłoniętych czół izolacji).
        Przedłużenie w dół chowa się w płycie/cokole — bez wpływu na widoczną geometrię."""
        for _ in range(3):
            changed = False
            for s in self._sciany:
                if s.ext_side is None or s.typ != "sciana_zewn":
                    continue
                for end in (0, 1):
                    inf = s.polaczenia.get(end) or {}
                    if inf.get("typ") != "L" or not inf.get("z"):
                        continue
                    v = self._sc_by_id.get(inf["z"][0])
                    if v is None or v.ext_side is None or v.typ != "sciana_zewn":
                        continue
                    es = [l for l in s.warstwy if l.strona == s.ext_side]
                    ev = [l for l in v.warstwy if l.strona == v.ext_side]
                    if not es or not ev:
                        continue
                    z0 = min(min(l.z0 for l in es), min(l.z0 for l in ev))
                    wolne = ([] if not getattr(s, "_ext_dol_wolne", True) else es) + \
                            ([] if not getattr(v, "_ext_dol_wolne", True) else ev)
                    for l in wolne:
                        if l.z0 > z0 + 1e-6:
                            l.z0 = z0
                            changed = True
            if not changed:
                break

    # ---------------- otwory ----------------
    def _build_openings(self):
        by_wall: dict[str, list[Otwor]] = {}
        for i, o in enumerate(self.raw.get("otwory") or []):
            if not self._check_fields("otwory", i, o, F["otwory"]):
                continue
            loc = self._loc("otwory", i, o)
            sid = str(o["sciana"])
            w = self._sc_by_id.get(sid)
            if w is None:
                self._err(loc, f"odwołanie do nieistniejącej ściany '{sid}'")
                continue
            if o["szer"] <= 0 or o["wys"] <= 0:
                self._err(loc, "szerokość i wysokość otworu muszą być > 0")
                continue
            ot = Otwor(raw=o, id=str(o["id"]), sciana_id=sid, symbol=o.get("symbol"), typ=o["typ"], odl=float(o["odl"]),
                       szer=float(o["szer"]), wys=float(o["wys"]), parapet=float(o["parapet"]),
                       otwieranie=o.get("otwieranie"), oslona=o.get("oslona"), sciana=w, kond=w.kond)
            rz = self._kond[w.kond].rzedna
            ot.s0, ot.s1 = ot.odl, ot.odl + ot.szer
            ot.z0, ot.z1 = rz + ot.parapet, rz + ot.parapet + ot.wys
            if ot.s0 < -GEOM_TOL or ot.s1 > w.L + GEOM_TOL:
                self._err(loc, f"otwór wychodzi poza ścianę {w.id} w poziomie: zakres {ot.s0:.3f}–{ot.s1:.3f} m, "
                               f"długość osi ściany {w.L:.3f} m")
            if ot.z0 < w.z_od - GEOM_TOL or ot.z1 > w.z_do + GEOM_TOL:
                self._err(loc, f"otwór wychodzi poza ścianę {w.id} w pionie: rzędne {ot.z0:.3f}–{ot.z1:.3f}, "
                               f"ściana {w.z_od:.3f}–{w.z_do:.3f}")
            # kolizja z przyłączoną ścianą (T/L) — otwór w strefie węzła
            for v in self._sciany:
                if v.kond != w.kond or v is w:
                    continue
                for end in (0, 1):
                    inf = v.polaczenia.get(end) or {}
                    if w.id in inf.get("z", []):
                        s_j, _ = w.st(np.array(inf["J"]))
                        half = max(abs(v.t_min), abs(v.t_max))
                        if ot.s0 < s_j + half - GEOM_TOL and ot.s1 > s_j - half + GEOM_TOL and \
                                min(ot.z1, v.z_do) - max(ot.z0, v.z_od) > 0.01:
                            self._warn(loc, f"otwór koliduje z połączeniem ściany {v.id} (węzeł w s={s_j:.2f} m)")
            by_wall.setdefault(sid, []).append(ot)
            self._otwory.append(ot)
            w.otwory.append(ot)
        for sid, lst in by_wall.items():
            lst.sort(key=lambda o: o.s0)
            for a, b in combinations(lst, 2):
                ds = min(a.s1, b.s1) - max(a.s0, b.s0)
                dz = min(a.z1, b.z1) - max(a.z0, b.z0)
                if ds > GEOM_TOL and dz > GEOM_TOL:
                    self._err(f"{self.src_b}: otwory ({a.id}, {b.id})",
                              f"otwory nakładają się w ścianie {sid}: s {a.s0:.2f}–{a.s1:.2f} / {b.s0:.2f}–{b.s1:.2f} m, "
                              f"z {a.z0:.2f}–{a.z1:.2f} / {b.z0:.2f}–{b.z1:.2f}")
        self._ot_by_id = {o.id: o for o in self._otwory}

    # ---------------- pomieszczenia ----------------
    def wolna_przestrzen(self, kid: str):
        """Zamknięte obszary wolne kondygnacji (między licami ścian wykończonych) — lista wieloboków."""
        if kid in self._free_cache:
            return self._free_cache[kid]
        geoms = [s.polygon for s in self._sciany if s.kond == kid]
        k = self._kond[kid]
        for sl in self.raw.get("slupy") or []:
            if isinstance(sl, dict) and _is_pt(sl.get("xy")) and _is_num(sl.get("z_od")) and _is_num(sl.get("z_do")):
                if sl["z_od"] <= k.rzedna + 1.0 <= sl["z_do"]:
                    a, b = parse_przekroj(str(sl.get("przekroj", "")))
                    x, y = sl["xy"]
                    geoms.append(box(x - a / 2, y - b / 2, x + a / 2, y + b / 2))
        geoms = [g for g in geoms if g is not None and not g.is_empty]
        if not geoms:
            self._free_cache[kid] = []
            return []
        U = unary_union([snap(g) for g in geoms])
        env = box(*U.bounds).buffer(5.0)
        free = env.difference(U)
        regs = []
        for p in _iter_polys(free):
            if p.area <= 0.05 or p.exterior.intersects(env.exterior):
                continue
            # usunięcie zerowej szerokości „kolców” (styki skosów tynku) — otwarcie morfologiczne
            q = p.buffer(-1e-5, join_style=2).buffer(1e-5, join_style=2)
            q = clean_geom(snap(q))
            regs.extend(orient(x, 1.0) for x in _iter_polys(q))
        self._free_cache[kid] = regs
        return regs

    def _build_rooms(self):
        for i, p in enumerate(self.raw.get("pomieszczenia") or []):
            if not self._check_fields("pomieszczenia", i, p, F["pomieszczenia"]):
                continue
            loc = self._loc("pomieszczenia", i, p)
            kid = str(p["kond"])
            if kid not in self._kond:
                self._err(loc, f"odwołanie do nieistniejącej kondygnacji '{kid}'")
                continue
            for pole in ("posadzka", "sciany_wyk", "sufit"):
                v = p.get(pole)
                if v is not None and str(v) not in self._mat and str(v) not in self._prz:
                    self._warn(loc, f"'{pole}: {v}' nie jest kodem materiału ani przegrody")
            if p.get("punkt") is None and p.get("wielobok") is None:
                self._err(loc, "pomieszczenie wymaga 'punkt' (punkt wewnątrz) lub 'wielobok'")
                continue
            rm = Pomieszczenie(raw=p, id=str(p["id"]), kond=kid, nazwa=str(p["nazwa"]),
                               punkt=tuple(p["punkt"]) if p.get("punkt") else None, wielobok=p.get("wielobok"),
                               kategoria=p["kategoria"], pobyt_ludzi=bool(p.get("pobyt_ludzi", False)),
                               posadzka=p.get("posadzka"), sciany_wyk=p.get("sciany_wyk"), sufit=p.get("sufit"),
                               temp=p.get("temp"), went=p.get("went"))
            regs = self.wolna_przestrzen(kid)
            if rm.wielobok is not None:
                self._check_poly(loc, "wielobok", rm.wielobok)
                W = make_polygon(rm.wielobok)
                clip = clean_geom(W.intersection(unary_union(regs))) if regs else Polygon()
                if clip.is_empty:
                    self._warn(loc, "jawny 'wielobok' nie pokrywa się z żadnym zamkniętym obszarem kondygnacji — "
                                    "przyjęto wielobok bez przycięcia do lic ścian")
                    clip = W
                rm.polygon, rm.zrodlo = clip, "wielobok"
                if rm.punkt is not None and not W.buffer(1e-6).contains(Point(rm.punkt)):
                    self._warn(loc, f"'punkt' {list(rm.punkt)} leży poza jawnym wielobokiem")
            else:
                P = Point(rm.punkt)
                hit = [g for g in regs if g.distance(P) < 1e-9]
                if hit:
                    rm.polygon, rm.zrodlo = hit[0], "punkt"
                else:
                    walls_here = unary_union([s.polygon for s in self._sciany if s.kond == kid])
                    if not walls_here.is_empty and walls_here.contains(P):
                        self._err(loc, f"punkt {list(rm.punkt)} leży wewnątrz ściany — wskaż punkt w pomieszczeniu")
                    else:
                        self._err(loc, f"punkt {list(rm.punkt)} nie leży w zamkniętym obszarze kondygnacji {kid} "
                                       "(ściany nie tworzą zamkniętego obrysu) — uzupełnij ściany lub podaj 'wielobok'")
                    rm.polygon, rm.zrodlo = Polygon(), "brak"
            # otwory w stropie pod pomieszczeniem (klatka schodowa)
            voids = self._voids_under(kid)
            rm.polygon_podlogi = clean_geom(rm.polygon.difference(voids)) if (voids is not None and not rm.polygon.is_empty) else rm.polygon
            rm.wysokosc = self._room_height(rm)
            self._pom.append(rm)
        # wspólne obszary i nakładanie
        for a, b in combinations(self._pom, 2):
            if a.kond != b.kond or a.polygon is None or b.polygon is None or a.polygon.is_empty or b.polygon.is_empty:
                continue
            ov = a.polygon.intersection(b.polygon).area
            if ov > 0.01:
                self._warn(f"{self.src_b}: pomieszczenia ({a.id}, {b.id})",
                           f"pomieszczenia nakładają się ({ov:.2f} m²) — podziel otwartą przestrzeń jawnymi 'wielobok'")
        self._pom_by_id = {p.id: p for p in self._pom}

    def _voids_under(self, kid: str):
        prev = self._kond_prev(kid)
        if prev is None:
            return None
        hs = []
        for st in self.raw.get("stropy") or []:
            if isinstance(st, dict) and str(st.get("nad")) == prev.id:
                for h in st.get("otwory") or []:
                    if _is_ring(h):
                        hs.append(make_polygon(h))
        return unary_union(hs) if hs else None

    def _room_height(self, rm: Pomieszczenie) -> float | None:
        if _is_num(rm.raw.get("wys")):
            return float(rm.raw["wys"])
        k = self._kond[rm.kond]
        if rm.polygon is None or rm.polygon.is_empty:
            return k.wys_w_swietle
        rp = rm.polygon.representative_point()
        sl = self._slab_above(rm.kond, (rp.x, rp.y), k.rzedna)
        if sl is None:
            return k.wys_w_swietle
        d_suf = SUFIT_D_DOMYSLNA
        suf = rm.sufit
        if sl["typ"] == "dach":
            p = self._prz.get(str(sl["raw"].get("przegroda")))
            if p is not None and p.ma_oznaczona_konstr:
                d_suf = p.d_pod_konstr()
        elif suf and str(suf) in self._prz:
            d_suf = self._prz[str(suf)].grubosc
        return round(sl["spod"] - d_suf - k.rzedna, 4)

    def _check_levels(self):
        for kid, k in self._kond.items():
            prev = self._kond_prev(kid)
            if prev is not None:
                for st in self.raw.get("stropy") or []:
                    if isinstance(st, dict) and str(st.get("nad")) == prev.id and _is_num(st.get("wierzch")):
                        pk = st.get("podloga") or k.podloga
                        p = self._prz.get(str(pk)) if pk else None
                        if p is not None:
                            z = st["wierzch"] + p.d_nad_konstr()
                            if abs(z - k.rzedna) > 0.01:
                                self._warn(f"{self.src_b}: stropy ({st.get('id')})",
                                           f"wierzch płyty {st['wierzch']:.3f} + warstwy podłogi {p.kod} "
                                           f"({p.d_nad_konstr():.3f}) = {z:.3f} ≠ rzędna {kid} {k.rzedna:.3f}")
            if _is_num(k.wys_w_swietle):
                hs = [r.wysokosc for r in self._pom if r.kond == kid and r.wysokosc is not None]
                if hs:
                    h = float(np.median(hs))
                    if abs(h - float(k.wys_w_swietle)) > 0.02:
                        self._warn(f"{self.src_b}: kondygnacje ({kid})",
                                   f"wys_w_swietle {k.wys_w_swietle:.2f} ≠ wysokość wyliczona z płyt {h:.2f} m")

    def _check_slab_overlaps(self):
        sl = self._slab_elems()
        for a, b in combinations(sl, 2):
            dz = min(a["wierzch"], b["wierzch"]) - max(a["spod"], b["spod"])
            if dz <= 0.01:
                continue
            ov = a["poly"].intersection(b["poly"]).area
            if ov > 0.05:
                self._warn(f"{self.src_b}: {a['typ']} {a['id']} / {b['typ']} {b['id']}",
                           f"płyty nakładają się w rzucie ({ov:.2f} m²) w tym samym zakresie rzędnych — zdublowana "
                           "geometria (np. strop i dach nad tą samą częścią); rozdziel obrysy")

    def _check_on_plot(self):
        try:
            plot = self.dz.obrys
        except Exception:  # noqa: BLE001
            return
        if plot is None or plot.is_empty:
            return
        geoms = [self.obrys_kondygnacji(k) for k in self._kond]
        geoms += [make_polygon(x["obrys"]) for x in self.dachy() + self.wsporniki() + self.tarasy()
                  if _is_ring(x.get("obrys"))]
        geoms = [g for g in geoms if g is not None and not g.is_empty]
        if not geoms:
            return
        U = unary_union(geoms)
        out = U.difference(plot.buffer(1e-3)).area
        if out > 0.01:
            self._err(f"{self.src_d}: uklad", f"budynek wychodzi poza granice działki ({out:.2f} m² poza obrysem) — "
                                              "sprawdź 'uklad.przesuniecie/obrot'")

    # ---------------- działka ----------------
    def _validate_dzialka(self):
        r = self.raw_dz
        src = self.src_d
        for sek in WYMAGANE_DZIALKA:
            if sek not in r or r[sek] in (None, [], {}):
                self._err(src, f"brak wymaganej sekcji '{sek}'")
        for sek, typ in SEKCJE_DZIALKA.items():
            if sek in r and r[sek] is not None and not _check_type(r[sek], typ):
                self._err(f"{src}: {sek}", f"sekcja musi być typu: {_TYP_OPIS[typ]}")
        for sek in r:
            if sek not in SEKCJE_DZIALKA:
                self._info(f"{src}: {sek}", "sekcja spoza schematu — ignorowana przez rdzeń modelu")
        u = r.get("uklad") or {}
        if isinstance(u, dict):
            if not _is_pt(u.get("przesuniecie")):
                self._err(f"{src}: uklad", "brak lub nieprawidłowe pole 'przesuniecie' [dx, dy]")
            if "obrot" in u and not _is_num(u.get("obrot")):
                self._err(f"{src}: uklad", "pole 'obrot' musi być liczbą [°]")
        d = r.get("dzialka") or {}
        if isinstance(d, dict):
            if not _is_ring(d.get("obrys")):
                self._err(f"{src}: dzialka", "brak lub nieprawidłowy 'obrys' działki")
            else:
                self._check_poly(f"{src}: dzialka", "obrys", d["obrys"])
                if _is_num(d.get("pow")):
                    a = abs(signed_area(d["obrys"]))
                    if abs(a - d["pow"]) > max(1.0, 0.005 * d["pow"]):
                        self._warn(f"{src}: dzialka", f"pole 'pow' = {d['pow']} m² ≠ pole obrysu {a:.1f} m²")
        t = r.get("teren") or {}
        if isinstance(t, dict):
            pts = t.get("punkty")
            if not isinstance(pts, list) or len(pts) < 3 or not all(_is_pt(p, 3) for p in pts):
                self._err(f"{src}: teren", "'punkty' wymaga ≥ 3 punktów [x, y, H] (H — m n.p.m.)")
            else:
                Hs = [p[2] for p in pts]
                if max(abs(h - self.zero_abs) for h in Hs) > 30:
                    self._warn(f"{src}: teren", "rzędne terenu odbiegają o > 30 m od zero_abs — sprawdź układ wysokości")
        for sek, spec in F_DZ.items():
            lst = r.get(sek)
            if not isinstance(lst, list):
                continue
            for i, it in enumerate(lst):
                self._check_fields(sek, i, it, spec, loc=f"{src}: {sek}[{i}]")
        for sek in ("utwardzenia", "zielen", "miejsca_postojowe"):
            for i, it in enumerate(r.get(sek) or []):
                if isinstance(it, dict) and _is_ring(it.get("obrys")):
                    self._check_poly(f"{src}: {sek}[{i}]", "obrys", it["obrys"])
        dr = r.get("droga")
        if isinstance(dr, dict) and dr.get("jezdnia") is not None and not _is_ring(dr.get("jezdnia")):
            self._err(f"{src}: droga", "'jezdnia' musi być wielobokiem [[x, y], ...]")

    # ==================================================================================================
    # API zapytań
    # ==================================================================================================
    @property
    def kondygnacje(self) -> list[Kondygnacja]:
        return list(self._kond.values())

    def kondygnacja(self, kid: str) -> Kondygnacja:
        return self._kond[kid]

    @property
    def materialy(self) -> dict[str, Material]:
        return dict(self._mat)

    def material(self, kod: str) -> Material | None:
        return self._mat.get(kod)

    @property
    def przegrody(self) -> dict[str, Przegroda]:
        return dict(self._prz)

    def przegroda(self, kod: str) -> Przegroda | None:
        return self._prz.get(kod)

    def sciany(self, kond: str | None = None) -> list[Sciana]:
        return [s for s in self._sciany if kond is None or s.kond == kond]

    def sciana(self, sid: str) -> Sciana | None:
        return self._sc_by_id.get(sid)

    def otwory(self, sciana: str | None = None, kond: str | None = None) -> list[Otwor]:
        return [o for o in self._otwory if (sciana is None or o.sciana_id == sciana) and (kond is None or o.kond == kond)]

    def otwor(self, oid: str) -> Otwor | None:
        return self._ot_by_id.get(oid)

    def pomieszczenia(self, kond: str | None = None) -> list[Pomieszczenie]:
        return [p for p in self._pom if kond is None or p.kond == kond]

    def pomieszczenie(self, pid: str) -> Pomieszczenie | None:
        return self._pom_by_id.get(pid)

    def _lst(self, sek) -> list[dict]:
        v = self.raw.get(sek)
        return [x for x in v if isinstance(x, dict)] if isinstance(v, list) else []

    def stropy(self) -> list[dict]:
        return self._lst("stropy")

    def dachy(self) -> list[dict]:
        return self._lst("dachy")

    def wsporniki(self) -> list[dict]:
        return self._lst("wsporniki_plyty")

    def slupy(self) -> list[dict]:
        return self._lst("slupy")

    def belki(self) -> list[dict]:
        return self._lst("belki")

    def fundamenty(self) -> dict:
        v = self.raw.get("fundamenty")
        return v if isinstance(v, dict) else {}

    def schody(self) -> list[dict]:
        return self._lst("schody")

    def balustrady(self) -> list[dict]:
        return self._lst("balustrady")

    def lamele(self) -> list[dict]:
        return self._lst("lamele")

    def tarasy(self) -> list[dict]:
        return self._lst("tarasy")

    def elementy_zewn(self) -> list[dict]:
        """Wyposażenie zewnętrzne elewacji (kratownice na pnącza, osłony lamelowe urządzeń) — SCHEMAT §2."""
        return self._lst("elementy_zewn")

    def plyty(self) -> list[dict]:
        """Wszystkie płyty (stropy/dachy/wsporniki) z wyliczonym spodem i wierzchem."""
        return self._slab_elems()

    def kond_poziomu(self, z: float) -> str | None:
        """Kondygnacja, do której należy rzędna z (rzędna ≤ z < rzędna następnej, z tolerancją 0,3 m)."""
        best = None
        for k in self._kond.values():
            if z >= k.rzedna - 0.30:
                best = k.id
        return best or (self.kondygnacje[0].id if self._kond else None)

    # ---------------- wskaźniki ----------------
    def obrys_kondygnacji(self, kid: str, lico: str = "zewn"):
        """Obrys kondygnacji: 'zewn' — po licach zewnętrznych ścian (wypełniony), 'konstr' — po warstwie konstrukcyjnej."""
        if lico == "konstr":
            geoms = [l.polygon for s in self._sciany if s.kond == kid for l in s.warstwy if l.konstrukcyjna]
        else:
            geoms = [s.polygon for s in self._sciany if s.kond == kid]
        geoms = [g for g in geoms if g is not None and not g.is_empty]
        if not geoms:
            return Polygon()
        U = unary_union(geoms)
        return clean_geom(unary_union([Polygon(p.exterior) for p in _iter_polys(U)]), min_area=0.5)

    def pow_zabudowy(self) -> dict:
        """Powierzchnia zabudowy (rzut zewnętrznych krawędzi budynku na teren; PN-ISO 9836:2015 p. 5.1.1).

        'budynek' — suma rzutów obrysów kondygnacji nadziemnych (bez daszków, okapów, schodów zewnętrznych);
        'z_plytami' — dodatkowo rzuty płyt wspornikowych i dachów wykraczających poza obrys (wariant informacyjny,
        np. gdy MPZP wlicza zadaszenia/wiaty)."""
        rz = [self.obrys_kondygnacji(k) for k in self._kond]
        rz = [g for g in rz if not g.is_empty]
        A = unary_union(rz) if rz else Polygon()
        extra = [make_polygon(w["obrys"]) for w in self.wsporniki() if _is_ring(w.get("obrys"))]
        extra += [make_polygon(d["obrys"]) for d in self.dachy() if _is_ring(d.get("obrys"))]
        B = unary_union([A] + extra) if extra else A
        return {"budynek": round(float(A.area), 2), "z_plytami": round(float(B.area), 2), "wielobok": A}

    def kubatura_brutto(self) -> dict:
        """Kubatura brutto (PN-ISO 9836:2015 p. 5.2.1 — objętość ograniczona zewnętrznymi powierzchniami przegród,
        od spodu warstwy konstrukcyjnej podłogi najniższej kondygnacji do wierzchu pokrycia dachu, bez attyk).
        Liczona warstwowo: przestrzenie kondygnacji + płyty stropów/dachów w obrębie obrysów."""
        per = {}
        total = 0.0
        outl = {k: self.obrys_kondygnacji(k) for k in self._kond}
        for kid, k in self._kond.items():
            R = outl[kid]
            walls = self.sciany(kid)
            if not walls or R.is_empty:
                continue
            z_od = float(np.median([s.z_od for s in walls]))
            z_do = float(np.median([s.z_do for s in walls]))
            v = R.area * (z_do - z_od)
            if k.idx == 0:
                p = self._prz.get(k.podloga) if k.podloga else None
                if p is not None and p.ma_oznaczona_konstr:
                    v += R.area * p.warstwy[p.idx_konstr].d
            per[kid] = v
            total += v
        for sl in self._slab_elems():
            if sl["typ"] == "wspornik":
                continue
            if sl["typ"] == "strop":
                kid = sl["nad"]
                R = outl.get(kid)
                nxt = self._kond_next(kid) if kid in self._kond else None
                if nxt is not None and not outl[nxt.id].is_empty:
                    R = unary_union([R, outl[nxt.id]]) if R is not None else outl[nxt.id]
                if R is None or R.is_empty:
                    continue
                a = sl["poly_full"].buffer(0.40, join_style=2).intersection(R).area
                v = a * (sl["wierzch"] - sl["spod"])
            else:
                # dach: w obrysie kondygnacji bezpośrednio pod płytą (okapy poza obrysem — nie wliczane)
                below = None
                for k in reversed(list(self._kond.values())):
                    if self.kond_z_od(k.id) < sl["wierzch"] - 0.5:
                        below = k.id
                        break
                R = outl.get(below) if below else Polygon()
                if R is None or R.is_empty:
                    continue
                a = sl["poly_full"].buffer(0.40, join_style=2).intersection(R).area
                p = self._prz.get(str(sl["raw"].get("przegroda")))
                d_pod = p.d_pod_konstr() if p is not None else 0.0
                v = a * (sl["top"] - sl["spod"] + d_pod)
            key = f"plyta {sl['id']}"
            per[key] = v
            total += v
        return {"razem": round(total, 1), "skladniki": {k: round(v, 2) for k, v in per.items()}}

    def zestawienie_powierzchni(self) -> dict:
        """Zestawienie powierzchni netto pomieszczeń wg PN-ISO 9836:2015 (kategorie z modelu)."""
        wiersze = []
        sumy = {k: 0.0 for k in KATEGORIE_POM}
        per_kond: dict[str, float] = {}
        for r in self._pom:
            wiersze.append({"id": r.id, "kond": r.kond, "nazwa": r.nazwa, "kategoria": r.kategoria,
                            "pow_netto": round(r.pow_netto, 2), "wysokosc": r.wysokosc,
                            "wsp": r.wsp_wysokosci, "pow_zaliczona": round(r.pow_zaliczona, 2),
                            "obwod": round(r.obwod, 2), "pobyt_ludzi": r.pobyt_ludzi})
            sumy[r.kategoria] = sumy.get(r.kategoria, 0.0) + r.pow_zaliczona
            per_kond[r.kond] = per_kond.get(r.kond, 0.0) + r.pow_zaliczona
        pu = sumy.get("podstawowa", 0) + sumy.get("pomocnicza", 0)
        return {"pomieszczenia": wiersze,
                "sumy_kategorii": {k: round(v, 2) for k, v in sumy.items()},
                "pow_uzytkowa_PU": round(pu, 2),
                "pow_ruchu": round(sumy.get("ruchu", 0), 2),
                "pow_techniczna": round(sumy.get("techniczna", 0), 2),
                "pow_netto_razem": round(sum(sumy.values()), 2),
                "per_kondygnacja": {k: round(v, 2) for k, v in per_kond.items()}}

    def pow_brutto_kondygnacji(self) -> dict:
        return {k: round(self.obrys_kondygnacji(k).area, 2) for k in self._kond}

    def bbox(self) -> tuple[float, float, float, float]:
        geoms = [s.polygon for s in self._sciany]
        geoms += [make_polygon(x["obrys"]) for x in self.dachy() + self.wsporniki() + self.stropy() if _is_ring(x.get("obrys"))]
        U = unary_union([g for g in geoms if g is not None and not g.is_empty])
        return U.bounds


# --------------------------------------------------------------------------------------------------
# Pomocnicze — przekroje profili
# --------------------------------------------------------------------------------------------------
def parse_przekroj(txt: str) -> tuple[float, float]:
    """'RK 120x120x8' → (0.12, 0.12); 'HEB 160' → (0.16, 0.16); 'fi 200'/'Ø200'/'RO 168,3x8' → (0.2, 0.2);
    '300x400' → (0.30, 0.40). Jednostki: mm gdy wartości > 5, inaczej m."""
    t = txt.replace(",", ".")
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", t)]
    if not nums:
        return (0.2, 0.2)

    def conv(v):
        return v / 1000.0 if v > 5 else v
    if re.search(r"(fi|ø|Ø|RO|RUR)", t, re.I) or len(nums) == 1:
        a = conv(nums[0])
        return (a, a)
    return (conv(nums[0]), conv(nums[1]))


def is_circular(txt: str) -> bool:
    return bool(re.search(r"(fi|ø|Ø|\bRO\b|RUR)", txt, re.I))


# --------------------------------------------------------------------------------------------------
# Wczytanie
# --------------------------------------------------------------------------------------------------
def _read_yaml(path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_model(budynek_path, dzialka_path=None, *, strict: bool = True) -> Model:
    """Wczytuje i waliduje model. strict=True → ModelValidationError przy błędach zgodności ze schematem."""
    bp = Path(budynek_path)
    try:
        raw_b = _read_yaml(bp)
    except yaml.YAMLError as e:
        m = Model({}, None, src_budynek=bp.name)
        m.problemy = [Problem("BLAD", bp.name, f"błąd składni YAML: {e}")]
        if strict:
            raise ModelValidationError(m.problemy)
        return m
    raw_d = None
    dname = "dzialka.yaml"
    if dzialka_path is not None:
        dp = Path(dzialka_path)
        dname = dp.name
        try:
            raw_d = _read_yaml(dp)
        except yaml.YAMLError as e:
            raise ModelValidationError([Problem("BLAD", dp.name, f"błąd składni YAML: {e}")])
    m = Model(raw_b, raw_d, src_budynek=bp.name, src_dzialka=dname)
    if strict and m.bledy:
        raise ModelValidationError(m.problemy)
    return m


def _main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Walidacja i wskaźniki modelu budynku (Dom LAMELA)")
    ap.add_argument("budynek")
    ap.add_argument("dzialka", nargs="?")
    a = ap.parse_args(argv)
    m = load_model(a.budynek, a.dzialka, strict=False)
    print(m.raport_walidacji())
    if m.bledy and not m.sciany():
        return 1
    print("\nKondygnacje:", ", ".join(f"{k.id} ({k.rzedna:+.2f})" for k in m.kondygnacje))
    print(f"Ściany: {len(m.sciany())}, otwory: {len(m.otwory())}, pomieszczenia: {len(m.pomieszczenia())}")
    zp = m.pow_zabudowy()
    print(f"Powierzchnia zabudowy: {zp['budynek']:.2f} m² (z płytami/zadaszeniami: {zp['z_plytami']:.2f} m²)")
    print(f"Kubatura brutto: {m.kubatura_brutto()['razem']:.1f} m³")
    print("Powierzchnie brutto kondygnacji:", m.pow_brutto_kondygnacji())
    zs = m.zestawienie_powierzchni()
    print("\nPomieszczenia (PN-ISO 9836:2015):")
    for w in zs["pomieszczenia"]:
        h = f"{w['wysokosc']:.2f}" if w["wysokosc"] is not None else "—"
        print(f"  {w['id']:>6} {w['nazwa']:<28} {w['kategoria']:<11} {w['pow_netto']:8.2f} m²  h={h}  "
              f"obw={w['obwod']:.2f} m")
    print(f"  Pow. użytkowa (podst.+pomocn.): {zs['pow_uzytkowa_PU']:.2f} m²; ruchu: {zs['pow_ruchu']:.2f} m²; "
          f"techniczna: {zs['pow_techniczna']:.2f} m²; netto razem: {zs['pow_netto_razem']:.2f} m²")
    return 1 if m.bledy else 0


if __name__ == "__main__":
    sys.exit(_main())
