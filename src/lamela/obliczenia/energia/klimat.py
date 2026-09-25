"""Dane klimatyczne do obliczeń energetycznych — typowy rok meteorologiczny, stacja Poznań (WMO 12330).

Źródło (dane urzędowe publikowane w BIP ministra właściwego ds. budownictwa, metodologia Dz.U. 2015 poz. 376
zał. 1 pkt 5.2.3.1.1, 5.2.4.1): Ministerstwo Inwestycji i Rozwoju (archiwum), „Dane do obliczeń energetycznych
budynków” — pliki `wmo123300iso.zip` (dane godzinowe, TMY wg PN-EN ISO 15927-4) i `wmo123300iso_stat.txt`
(statystyki miesięczne), okres 1971–2000; https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow
(pobrano 2026-09-25). Wartości miesięczne w `dane/klimat_poznan_12330.yaml`, godzinowe (podzbiór kolumn)
w `dane/klimat_poznan_12330_godz.csv.gz`.

Azymut: od północy, zgodnie z ruchem wskazówek (E = 90°). Napromieniowanie płaszczyzn pionowych dla azymutu pośredniego
— interpolacja liniowa między 8 kierunkami (co 45°).
"""
from __future__ import annotations

import gzip
from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import yaml

from ..wspolne import DANE, ORIENTACJE

PLIK_MIES = DANE / "klimat_poznan_12330.yaml"
PLIK_GODZ = DANE / "klimat_poznan_12330_godz.csv.gz"
AZ = {o: 45.0 * i for i, o in enumerate(ORIENTACJE)}


def p_sat(theta):
    """Ciśnienie pary nasyconej [Pa] — PN-EN ISO 13788:2013 zał. E (wzory E.7/E.8)."""
    t = np.asarray(theta, float)
    return np.where(t >= 0, 610.5 * np.exp(17.269 * t / (237.3 + t)), 610.5 * np.exp(21.875 * t / (265.5 + t)))


def theta_z_psat(p):
    """Odwrotność p_sat (temperatura punktu rosy dla ciśnienia p) [°C]."""
    p = np.asarray(p, float)
    x = np.log(np.maximum(p, 1e-6) / 610.5)
    return np.where(p >= 610.5, 237.3 * x / (17.269 - x), 265.5 * x / (21.875 - x))


@dataclass
class KlimatMiesieczny:
    meta: dict
    theta_e: np.ndarray        # [°C] 12
    phi_e: np.ndarray          # [-]
    p_e: np.ndarray            # [Pa]
    godziny: np.ndarray        # [h]
    irr: dict                  # klucz → np.ndarray(12) [kWh/m² mies.]

    def I(self, azymut: float | None, nachylenie: float = 90.0) -> np.ndarray:
        """Miesięczne napromieniowanie [kWh/(m²·mies.)] płaszczyzny o azymucie i nachyleniu (0, 30, 45, 60, 90°;
        pośrednie nachylenia — interpolacja liniowa)."""
        if nachylenie <= 1e-6 or azymut is None:
            return self.irr["poziom"].copy()
        tilts = [0, 30, 45, 60, 90]
        if nachylenie in tilts:
            return self._I_az(azymut, int(nachylenie))
        t0 = max(t for t in tilts if t <= nachylenie)
        t1 = min(t for t in tilts if t >= nachylenie)
        a = self._I_az(azymut, t0) if t0 else self.irr["poziom"]
        b = self._I_az(azymut, t1)
        f = (nachylenie - t0) / (t1 - t0)
        return (1 - f) * a + f * b

    def _I_az(self, azymut: float, tilt: int) -> np.ndarray:
        az = azymut % 360.0
        i0 = int(az // 45) % 8
        i1 = (i0 + 1) % 8
        f = (az - 45 * (az // 45)) / 45.0
        a = self.irr[f"{ORIENTACJE[i0]}_{tilt}"]
        b = self.irr[f"{ORIENTACJE[i1]}_{tilt}"]
        return (1 - f) * a + f * b

    @property
    def theta_e_rok(self) -> float:
        return float(np.sum(self.theta_e * self.godziny) / np.sum(self.godziny))


@lru_cache(maxsize=2)
def klimat_miesieczny(plik: str | None = None) -> KlimatMiesieczny:
    d = yaml.safe_load(open(plik or PLIK_MIES, encoding="utf-8"))
    m = d["miesieczne"]
    irr = {k: np.array(v, float) for k, v in d["napromieniowanie_kWh_m2"].items()}
    return KlimatMiesieczny(meta=d["meta"], theta_e=np.array(m["theta_e"], float), phi_e=np.array(m["phi_e"], float),
                            p_e=np.array(m["p_e"], float), godziny=np.array(m["godziny"], float), irr=irr)


@dataclass
class KlimatGodzinowy:
    M: np.ndarray
    D: np.ndarray
    H: np.ndarray
    DBT: np.ndarray
    RH: np.ndarray
    ITH: np.ndarray
    IDH: np.ndarray
    ISH: np.ndarray
    kol: dict                  # np. 'S_90' → np.ndarray [W/m²]

    def I(self, azymut: float, nachylenie: int = 90) -> np.ndarray:
        az = azymut % 360.0
        i0 = int(az // 45) % 8
        i1 = (i0 + 1) % 8
        f = (az - 45 * (az // 45)) / 45.0
        return (1 - f) * self.kol[f"{ORIENTACJE[i0]}_{nachylenie}"] + f * self.kol[f"{ORIENTACJE[i1]}_{nachylenie}"]

    def pozycja_slonca(self):
        """(azymut, wysokość) [°] dla każdej godziny TMY — `lamela.sun` (NOAA).

        Znacznik godziny H pliku TMY zinterpretowano empirycznie: środek przedziału = H + 1:00 czasu standardowego
        (UTC+1) — przy tym przesunięciu tylko 3 z 8760 godzin mają promieniowanie > 0 przy Słońcu pod horyzontem
        (przy H + 0:30 — 71 godzin); sprawdzenie w tools/test_obliczenia_fizyka.py."""
        return _pozycje_slonca(tuple(self.M.tolist()), tuple(self.D.tolist()), tuple(self.H.tolist()))


@lru_cache(maxsize=1)
def _pozycje_slonca(M, D, H):
    from datetime import datetime, timedelta, timezone
    from ...sun import sun_position
    tz = timezone(timedelta(hours=1))
    az = np.zeros(len(M))
    el = np.zeros(len(M))
    for i, (m, d, h) in enumerate(zip(M, D, H)):
        t = datetime(2026, int(m), int(d), int(h), 0, tzinfo=tz) + timedelta(hours=1)
        az[i], el[i] = sun_position(t, refraction=False)
    return az, el


@lru_cache(maxsize=1)
def klimat_godzinowy(plik: str | None = None) -> KlimatGodzinowy:
    with gzip.open(plik or PLIK_GODZ, "rt", encoding="utf-8") as f:
        lines = [l for l in f.read().splitlines() if l and not l.startswith("#")]
    hdr = lines[0].split(",")
    arr = np.array([[float(x) for x in l.split(",")] for l in lines[1:]])
    c = {h: arr[:, i] for i, h in enumerate(hdr)}
    kol = {}
    for o in ORIENTACJE:
        for t in (90, 30):
            k = f"{o}__{t}" if len(o) == 1 else f"{o}_{t}"
            kol[f"{o}_{t}"] = c[k]
    return KlimatGodzinowy(M=c["M"].astype(int), D=c["D"].astype(int), H=c["H"].astype(int), DBT=c["DBT"], RH=c["RH"],
                           ITH=c["ITH"], IDH=c["IDH"], ISH=c["ISH"], kol=kol)


def opis_zrodla() -> str:
    k = klimat_miesieczny()
    m = k.meta
    return (f"{m['typ']}, stacja {m['stacja']} (WMO {m['kod_WMO']}), okres {m['okres_danych']}; {m['zrodlo']} "
            f"(pobrano {m['pobrano']})")
