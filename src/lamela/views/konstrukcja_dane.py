"""Dane do rysunków konstrukcyjnych PT-BO z obliczeń ``lamela.obliczenia.konstrukcja``.

Moduł pomocniczy generatora ``lamela.views.konstrukcja``:
  * analiza konstrukcji uruchamiana raz na kontekst widoków (``analiza(ctx)``; opcjonalny cache pickle —
    zmienna środowiskowa ``LAMELA_KONSTR_CACHE`` = katalog; klucz = skrót plików modelu i biblioteki),
  * ekstrakcja zbrojenia WYNIKAJĄCEGO Z OBLICZEŃ (``dane(ctx)``): pola płyt (φ/s dołem i górą z wymiarowania MES
    biblioteki), belki/nadproża (n·φ, strzemiona), wieńce, schody, fundamenty (żebra/ławy, pogrubienia pod słupami,
    płyta — biblioteka zwraca tylko A_s,req pasma Winklera → dobór prętów ``dobierz_siatke`` tego modułu),
  * kształty i długości prętów wg PN-EN ISO 3766 (kody 00, 11, 21, 51) z odliczeniem gięcia (trzpień wg
    PN-EN 1992-1-1 tabl. 8.1N), zestawienie stali z numeracją pozycji i masami (ρ = 7850 kg/m³),
  * kontrola A_s,prov ≥ max(A_s,req; A_s,min), A_s ≤ A_s,max, s ≤ s_max (PN-EN 1992-1-1 9.2.1.1, 9.3.1.1)
    — raport ``kontrola_zbrojenia.md/json`` i lista braków danych ``BRAKI_DANYCH.md``.
Wszystkie wartości geometryczne pochodzą z modelu (``ctx.model``), zbrojenie — z obiektów wyników biblioteki.
"""
from __future__ import annotations

import hashlib
import math
import os
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..obliczenia.konstrukcja.materialy import masa_preta, pole_preta

GATUNEK = "B500SP"
SREDNICE_PL = (8, 10, 12, 14, 16, 20)
KODY_ISO3766 = {"00": "prosty", "11": "jedno odgięcie 90°", "21": "dwa odgięcia 90° (U)", "51": "strzemię zamknięte",
                "26": "odgięty (bieg schodów)"}


# ================================================================================================ analiza (cache)
def _skrot_plikow(paths) -> str:
    h = hashlib.sha1()
    for p in paths:
        try:
            h.update(Path(p).read_bytes())
        except OSError:
            h.update(str(p).encode())
    return h.hexdigest()[:16]


def analiza(ctx):
    """AnalizaKonstrukcji dla modelu kontekstu (raz na kontekst). Błędy etapów trafiają do ``an.uwagi``."""
    an = getattr(ctx, "_konstr_an", None)
    if an is not None:
        return an
    from ..obliczenia.konstrukcja import AnalizaKonstrukcji, Parametry
    cache_dir = os.environ.get("LAMELA_KONSTR_CACHE")
    pk = None
    if cache_dir:
        lib = Path(__file__).resolve().parents[1] / "obliczenia" / "konstrukcja"
        src = [ctx.src] + sorted(str(p) for p in lib.glob("*.py"))
        dz = getattr(getattr(ctx.model, "dz", None), "raw", None)
        key = _skrot_plikow(src) + hashlib.sha1(repr(dz).encode()).hexdigest()[:8]
        pk = Path(cache_dir) / f"analiza_{key}.pkl"
        if pk.exists():
            try:
                an = pickle.loads(pk.read_bytes())
                an.m = ctx.model
                ctx._konstr_an = an
                return an
            except Exception:  # noqa: BLE001 — cache uszkodzony: liczymy od nowa
                an = None
    an = AnalizaKonstrukcji(ctx.model, Parametry.z_wymagan()).uruchom()
    if pk is not None:
        try:
            pk.parent.mkdir(parents=True, exist_ok=True)
            pk.write_bytes(pickle.dumps(an))
        except Exception:  # noqa: BLE001
            pass
    ctx._konstr_an = an
    return an


# ================================================================================================ pręty (ISO 3766)
def trzpien(fi: float) -> float:
    """Minimalna średnica trzpienia φ_m,min [mm] — PN-EN 1992-1-1 tabl. 8.1N (φ ≤ 16: 4φ; φ > 16: 7φ)."""
    return 4.0 * fi if fi <= 16 else 7.0 * fi


def odgiecie(fi: float) -> float:
    """Odliczenie długości na jedno gięcie 90° przy wymiarach zewnętrznych [mm]: Δ = 0,5·r + φ, r = φ_m/2
    (PN-EN ISO 3766 — wymiary zewnętrzne; reguła jak BS 8666 tabl. 3)."""
    return 0.5 * trzpien(fi) / 2.0 + fi


def hak_strzemienia(fi: float) -> float:
    """Zakończenie strzemienia hakiem 135° z prostym odcinkiem ≥ max(10φ; 70 mm) — PN-EN 1992-1-1 rys. 8.5."""
    return max(10.0 * fi, 70.0) + 0.5 * math.pi * (trzpien(fi) / 2.0 + fi / 2.0) * 0.75


def dlugosc_preta(fi: float, ksztalt: str, wym) -> float:
    """Długość rozwinięcia pręta [mm] dla kodu kształtu ISO 3766 i wymiarów zewnętrznych ``wym`` [mm]."""
    w = [float(x) for x in wym]
    if ksztalt == "00":
        return w[0]
    if ksztalt == "11":                       # L: a, b
        return w[0] + w[1] - odgiecie(fi)
    if ksztalt == "21":                       # U: a (ramię), b (grzbiet), c (ramię)
        return w[0] + w[1] + w[2] - 2 * odgiecie(fi)
    if ksztalt == "26":                       # łamany (bieg–spocznik): suma odcinków, gięcia rozwarte ≈ 0
        return sum(w)
    if ksztalt == "51":                       # strzemię zamknięte a × b (zewn.) z dwoma hakami 135°
        return 2 * (w[0] + w[1]) - 3 * odgiecie(fi) + 2 * hak_strzemienia(fi)
    return sum(w)


@dataclass
class Pret:
    """Pręt (pozycja zestawienia): kod kształtu PN-EN ISO 3766, wymiary odcinków [mm], liczba sztuk, element."""
    fi: int
    ksztalt: str
    wym: tuple
    n: int
    element: str
    opis: str = ""
    nr: int = 0
    gatunek: str = GATUNEK

    def __post_init__(self):
        self.wym = tuple(int(round(float(x) / 10.0) * 10) for x in self.wym)   # wymiary co 10 mm
        self.n = int(self.n)

    @property
    def L_mm(self) -> float:
        return math.ceil(dlugosc_preta(self.fi, self.ksztalt, self.wym) / 10.0) * 10.0   # w górę do 10 mm

    @property
    def dl(self) -> float:
        return self.L_mm / 1000.0

    @property
    def dl_calk(self) -> float:
        return self.dl * self.n

    @property
    def masa(self) -> float:
        return self.dl_calk * masa_preta(self.fi)

    def klucz(self) -> tuple:
        return (self.fi, self.ksztalt, self.wym, self.gatunek)

    def etykieta(self, s_mm: float | None = None) -> str:
        """Oznaczenie pręta na rysunku (PN-EN ISO 3766 p. 5): liczba, nr pozycji, φ, rozstaw, długość."""
        t = f"{self.n} ⌀{self.fi}"
        if s_mm:
            t += f" co {s_mm / 10:g}"
        return t + f" l={self.L_mm / 10:g}"


class Zestawienie:
    """Zestawienie stali (wykaz prętów) z numeracją pozycji: identyczne pręty (φ, kształt, wymiary) mają
    wspólny numer (liczby sztuk sumowane)."""

    def __init__(self, start: int = 1):
        self.prety: list[Pret] = []
        self._nr = start - 1
        self._idx: dict = {}

    def dodaj(self, p: Pret) -> Pret:
        """Dodaje pręt; zwraca pozycję zestawienia (istniejącą przy identycznym kształcie) z nadanym numerem."""
        if p.n <= 0:
            return p
        k = p.klucz()
        if k in self._idx:
            q = self._idx[k]
            q.n += p.n
            if p.element not in q.element.split(", "):
                q.element = (q.element + ", " + p.element)[:60]
            return q
        self._nr += 1
        p.nr = self._nr
        self.prety.append(p)
        self._idx[k] = p
        return p

    def srednice(self) -> list[int]:
        return sorted({p.fi for p in self.prety})

    def dl_wg_srednic(self) -> dict:
        return {d: sum(p.dl_calk for p in self.prety if p.fi == d) for d in self.srednice()}

    def masy(self) -> dict:
        return {d: L * masa_preta(d) for d, L in self.dl_wg_srednic().items()}

    @property
    def masa(self) -> float:
        return sum(self.masy().values())
