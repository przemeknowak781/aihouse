"""Dane projektu zagospodarowania działki (PZT) wyznaczane z modelu (``model/dzialka.yaml`` + ``model/budynek.yaml``).

Wszystko w UKŁADZIE DZIAŁKI (początek = narożnik SW działki, x → wschód, y → północ [m]); geometria budynku
przeliczana transformacją ``dzialka.yaml: uklad`` (``Dzialka.do_dzialki``). Moduł nie rysuje — dostarcza:

* geometrię: działka, sąsiedzi, droga, linia zabudowy, obrys przyziemia i wyższych kondygnacji, płyty/okapy,
  tarasy, utwardzenia, zieleń, ogrodzenie, uzbrojenie istniejące i projektowane, obiekty, retencja, odwodnienia,
* teren: interpolację TIN rzędnych istniejących i projektowanych, warstwice,
* wskaźniki (pow. zabudowy, PBC, intensywność, wysokość zabudowy — upzp art. 2 pkt 28–35, RPB § 14 pkt 4),
* odległości od granic (WT § 12) i koordynację sieci (odległości poziome, skrzyżowania, kolizje),
* listę braków danych (``braki``) — do raportu i ``projekt/02_PZT/BRAKI_DANYCH.md``.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import nearest_points, unary_union

from ..draft.geom import polygons_of

TODO = "[DO UZUPEŁNIENIA]"

# branże uzbrojenia: kod modelu → (litera mapy zasadniczej, nazwa, kolor wydruku)
BRANZE = {
    "woda": ("w", "wodociąg / przyłącze wodociągowe", "#0050c8"),
    "kan_sanit": ("ks", "kanalizacja sanitarna", "#7a4a1a"),
    "kan_deszcz": ("kd", "kanalizacja deszczowa", "#00808a"),
    "en": ("e", "elektroenergetyczna nN (kabel)", "#d00000"),
    "tele": ("t", "telekomunikacyjna (światłowód)", "#e07800"),
    "gaz": ("g", "gazowa", "#a89a00"),
    "cieplo": ("c", "ciepłownicza", "#8000a0"),
}
BRANZA_ALIAS = {"energ": "en", "elektro": "en", "tel": "tele", "kanal": "kan_sanit", "kd": "kan_deszcz",
                "ks": "kan_sanit", "w": "woda", "e": "en", "t": "tele", "g": "gaz"}

# Domyślne minimalne odległości poziome między sieciami [m] (zasady wiedzy technicznej — NIE przepis; WT § 26–28
# nie określają odległości). Nadpisywane w konfiguracji arkuszy: opcje.odleglosci_min.
ODL_MIN_DOMYSLNE = {
    "w-ks": (1.50, "praktyka proj. (COBRTI INSTAL z. 3) [SPRAWDŹ]"),
    "w-kd": (1.50, "praktyka proj. (COBRTI INSTAL z. 3) [SPRAWDŹ]"),
    "w-e": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "w-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "ks-kd": (1.00, "praktyka proj. [SPRAWDŹ]"),
    "e-ks": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "e-kd": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "e-t": (0.50, "N SEP-E-004:2014 (mniej — przy rurach osłonowych) [SPRAWDŹ]"),
    "ks-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "kd-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "g-*": (0.50, "PN-EN 12007-1 / praktyka [SPRAWDŹ]"),
    "drzewo": (2.00, "od pnia: N SEP-E-004 (kable), praktyka (rurociągi) [SPRAWDŹ]"),
}


def ring(v) -> list | None:
    if not isinstance(v, (list, tuple)) or len(v) < 3:
        return None
    try:
        return [(float(p[0]), float(p[1])) for p in v]
    except (TypeError, ValueError, IndexError):
        return None


def poly(v) -> Polygon | None:
    r = ring(v)
    if r is None:
        return None
    g = Polygon(r)
    if not g.is_valid:
        g = shapely.make_valid(g)
        g = unary_union(polygons_of(g))
    return g if not g.is_empty else None


def line(v) -> LineString | None:
    if not isinstance(v, (list, tuple)) or len(v) < 2:
        return None
    try:
        return LineString([(float(p[0]), float(p[1])) for p in v])
    except (TypeError, ValueError, IndexError):
        return None


def branza(code) -> str:
    c = str(code or "").strip()
    return BRANZA_ALIAS.get(c, c)


def lit(code) -> str:
    return BRANZE.get(branza(code), (str(code), str(code), "#000000"))[0]


def num_in(text, pattern, default=None):
    """Liczba z opisu (np. „strefa R290 1,0 m”) — zapasowe źródło, gdy brak pola strukturalnego."""
    m = re.search(pattern, str(text or ""))
    if not m:
        return default
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return default


@dataclass
class Brak:
    pole: str             # ścieżka pola w modelu (np. "dzialka.yaml: retencja.zbiornik.obrys")
    opis: str             # czego brakuje i do czego jest potrzebne
    propozycja: str       # proponowany format pola (SCHEMAT_MODELU.md §3/§6)
    arkusze: str = ""     # których rysunków dotyczy


@dataclass
class Siec:
    branza: str
    geom: LineString
    opis: str
    istn: bool
    dl: float | None = None
    id: str = ""

    @property
    def lit(self) -> str:
        return lit(self.branza)

    @property
    def kolor(self) -> str:
        return BRANZE.get(self.branza, ("", "", "#000000"))[2]


@dataclass
class Obiekt:
    id: str
    xy: np.ndarray
    opis: str
    raw: dict = field(default_factory=dict)
