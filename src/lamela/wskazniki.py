"""Wskaźniki zagospodarowania działki (MPZP, PZT) — JEDYNE źródło wartości w projekcie „Dom LAMELA”.

``wskazniki(model, ir=None, opcje=None) -> dict`` — każda pozycja to słownik
``{"wartosc", "jedn", "podstawa", "metoda", ...szczegóły}``; klucze: ``pow_dzialki``, ``pow_zabudowy``,
``pow_zabudowy_kontrolna``, ``udzial_zabudowy``, ``udzial_zabudowy_kontrolny``, ``pow_utwardzona``, ``pow_tarasow``,
``pow_opaski``, ``pbc``, ``pbc_rezerwa_dach``, ``udzial_pbc``, ``udzial_pbc_z_rezerwa``, ``pow_kondygnacji``,
``suma_pow_kondygnacji``, ``suma_pow_kondygnacji_nadziemnych``, ``intensywnosc``, ``intensywnosc_nadziemna``,
``wysokosc_zabudowy``, ``wysokosc_WT6``, ``kondygnacje_nadziemne``, ``miejsca_postojowe``, ``kat_dachu``;
pod kluczem ``_geom`` — geometrie shapely (układ działki) do rysunków (pokrycie terenu, PBC, obrysy).

Definicje (cytaty dosłowne: ``docs/10_podstawy_prawne/weryfikacja_upzp_art2_definicje.md``): ustawa o planowaniu
i zagospodarowaniu przestrzennym, t.j. Dz.U. 2026 poz. 538, art. 2 pkt 28–35; RPB § 14 pkt 4 (t.j. Dz.U. 2022
poz. 1679 ze zm.) — zestawienie powierzchni w PZT; WT § 6 (wysokość budynku) i § 3 pkt 15 (poziom terenu = przyjęta
w projekcie rzędna terenu).

Metoda wysokości zabudowy (upzp art. 2 pkt 30 lit. a): ``H = z_top − t_śr``, gdzie ``z_top`` — najwyżej położony
punkt budynku na dachu, ścianie lub attyce (wyłączenia ZAMKNIĘTE: komin, nadbudówka maszynowni dźwigu lub innego
pomieszczenia technicznego, wyjście z klatki schodowej — czerpnia, wyrzutnia, wywiewka, PV, wyłaz, świetlik są
WLICZANE), ``t_śr = (t_min + t_max) / 2`` — średnia z najniższego i najwyższego poziomu terenu na obwodzie rzutu
poziomego ścian zewnętrznych budynku; w każdym punkcie obwodu przyjmuje się NIŻSZĄ z rzędnych: terenu istniejącego
(interpolacja liniowa TIN) i projektowanego (TIN punktów projektowanych w zasięgu ≤ 2,0 m od najbliższego punktu).

Porównanie z ``tools/audyt_wt.py`` (audytor A1, wersja z 25.09.2026): audyt podaje wysokość zabudowy liczoną od
``t_min`` (najniższego punktu terenu) — to BŁĄD METODY względem pkt 30 lit. a (odniesieniem jest średnia z min. i maks.);
wartość „od średniej” audyt podaje pomocniczo, ale z ``t_śr = (min(dolnych) + min(górnych)) / 2`` (inna agregacja
istn./proj.). Ten moduł liczy wg definicji; różnice raportuje ``tools/test_wskazniki.py`` (audyt NIE jest poprawiany).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

UPZP = "upzp (t.j. Dz.U. 2026 poz. 538)"
POD = {
    "28": f"{UPZP} art. 2 pkt 28",
    "29": f"{UPZP} art. 2 pkt 29 lit. a",
    "30": f"{UPZP} art. 2 pkt 30 lit. a",
    "31": f"{UPZP} art. 2 pkt 31 lit. a",
    "32": f"{UPZP} art. 2 pkt 32 lit. a",
    "33": f"{UPZP} art. 2 pkt 33",
    "34": f"{UPZP} art. 2 pkt 34",
    "35": f"{UPZP} art. 2 pkt 35 lit. a",
    "RPB14": "RPB § 14 pkt 4 (t.j. Dz.U. 2022 poz. 1679, zm. Dz.U. 2023 poz. 2405)",
    "WT6": "WT § 6, § 3 pkt 15, § 8 pkt 1 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB)",
    "WT18": "WT § 18, § 21 ust. 1; MPZP",
}
TYPY_WEJSC = ("drzwi_zewn", "drzwi_przesuwne_HS", "brama")
PROMIEN_PROJ = 2.0     # [m] zasięg rzędnych projektowanych od najbliższego punktu projektowanego
WYWIEWKA_NAD_POKR = 0.50   # [m] założenie, gdy w modelu brak rzędnej wylotu wywiewki (PN-EN 12056-2 — praktyka)


def _poz(wartosc, jedn, podstawa, metoda, **kw) -> dict:
    d = dict(wartosc=wartosc, jedn=jedn, podstawa=podstawa, metoda=metoda)
    d.update(kw)
    return d


def _ring(v):
    try:
        return [(float(p[0]), float(p[1])) for p in v] if isinstance(v, (list, tuple)) and len(v) >= 3 else None
    except (TypeError, ValueError, IndexError):
        return None


def _poly(v):
    r = _ring(v)
    if r is None:
        return None
    g = Polygon(r)
    return g if g.is_valid else shapely.make_valid(g)


class Teren:
    """Rzędne terenu [m n.p.m.] w układzie działki: istniejący (TIN liniowy, poza otoczką — płaszczyzna MNK),
    projektowany (TIN punktów projektowanych, tylko ≤ ``PROMIEN_PROJ`` od najbliższego punktu), ``nizsza``."""

    def __init__(self, teren: dict):
        from scipy.interpolate import LinearNDInterpolator
        t = teren or {}
        self.ist = np.asarray([p for p in (t.get("punkty") or []) if len(p) >= 3], float).reshape(-1, 3)
        self.proj = np.asarray([p for p in (t.get("punkty_projektowane") or []) if len(p) >= 3], float).reshape(-1, 3)
        self._fi = self._fp = None
        if len(self.ist) >= 3:
            self._fi = LinearNDInterpolator(self.ist[:, :2], self.ist[:, 2])
            A = np.c_[self.ist[:, :2], np.ones(len(self.ist))]
            self._ci = np.linalg.lstsq(A, self.ist[:, 2], rcond=None)[0]
        if len(self.proj) >= 3:
            self._fp = LinearNDInterpolator(self.proj[:, :2], self.proj[:, 2])

    def istn(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        if self._fi is None:
            return np.full(len(xy), np.nan)
        z = np.asarray(self._fi(xy), float).reshape(-1)
        bad = ~np.isfinite(z)
        z[bad] = self._ci[0] * xy[bad, 0] + self._ci[1] * xy[bad, 1] + self._ci[2]
        return z

    def projekt(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        if len(self.proj) == 0:
            return np.full(len(xy), np.nan)
        d = np.min(np.hypot(xy[:, None, 0] - self.proj[None, :, 0], xy[:, None, 1] - self.proj[None, :, 1]), axis=1)
        if self._fp is not None:
            z = np.asarray(self._fp(xy), float).reshape(-1)
        else:
            z = np.full(len(xy), np.nan)
        nn = np.argmin(np.hypot(xy[:, None, 0] - self.proj[None, :, 0], xy[:, None, 1] - self.proj[None, :, 1]), axis=1)
        z = np.where(np.isfinite(z), z, self.proj[nn, 2])
        return np.where(d <= PROMIEN_PROJ, z, np.nan)

    def nizsza(self, xy):
        a, b = self.istn(xy), self.projekt(xy)
        return np.where(np.isfinite(b), np.minimum(a, b), a), a, b
