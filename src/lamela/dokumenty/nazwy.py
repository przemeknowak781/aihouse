"""Nazwy plików projektu w postaci elektronicznej wg załącznika nr 1 do RPB
(rozp. w sprawie szczegółowego zakresu i formy projektu budowlanego, t.j. Dz.U. 2022 poz. 1679 ze zm., § 2b ust. 4).

| poz. | elementy                         | jeden plik     | więcej plików |
|------|----------------------------------|----------------|---------------|
| 1    | PZT                              | ``PZT_z``      | ``PZT_x_z``   |
| 2    | PAB                              | ``PAB_z``      | ``PAB_x_z``   |
| 3    | PT                               | ``PT_z``       | ``PT_x_y_z``  |
| 4    | ZL (załączniki)                  | ``ZL_z``       | ``ZL_x_z``    |
| 5–8  | łączne: PZT+PAB, PZT+PAB+ZL, PZT+ZL, PAB+ZL | ``PZT_PAB_z``, ``PZT_PAB_ZL_z``, ``PZT_ZL_z``, ``PAB_ZL_z`` | — |

x — kolejny numer pliku; y — symbol specjalności tomu PT (AR, BO, BM, BD, BK, BH, BW, BT, IS, IE, IN, WB);
z — data sporządzenia pliku ``rrrr.mm.dd``. Rozszerzenie ``.pdf`` (§ 2b ust. 1).
"""
from __future__ import annotations

import re

from .formaty import data_pliku

SYMBOLE_Y = ("AR", "BO", "BM", "BD", "BK", "BH", "BW", "BT", "IS", "IE", "IN", "WB")
RODZAJE_POJEDYNCZE = ("PZT", "PAB", "PT", "ZL")
RODZAJE_LACZNE = ("PZT_PAB", "PZT_PAB_ZL", "PZT_ZL", "PAB_ZL")

_D = r"\d{4}\.(0[1-9]|1[0-2])\.(0[1-9]|[12]\d|3[01])"
WZORCE = {
    "PZT": rf"^PZT(_\d+)?_{_D}\.pdf$",
    "PAB": rf"^PAB(_\d+)?_{_D}\.pdf$",
    "ZL": rf"^ZL(_\d+)?_{_D}\.pdf$",
    "PT": rf"^PT(_\d+_({'|'.join(SYMBOLE_Y)}))?_{_D}\.pdf$",
    "PZT_PAB": rf"^PZT_PAB_{_D}\.pdf$",
    "PZT_PAB_ZL": rf"^PZT_PAB_ZL_{_D}\.pdf$",
    "PZT_ZL": rf"^PZT_ZL_{_D}\.pdf$",
    "PAB_ZL": rf"^PAB_ZL_{_D}\.pdf$",
}


def nazwa_pliku(rodzaj: str, data=None, *, nr: int | None = None, symbol: str | None = None) -> str:
    """Nazwa pliku wg zał. 1 RPB.

    >>> nazwa_pliku("PZT_PAB_ZL", "2026-09-25")
    'PZT_PAB_ZL_2026.09.25.pdf'
    >>> nazwa_pliku("PT", "2026-09-25", nr=2, symbol="BO")
    'PT_2_BO_2026.09.25.pdf'
    """
    r = rodzaj.upper().replace("+", "_").replace("-", "_")
    z = data_pliku(data)
    if r in RODZAJE_LACZNE:
        if nr is not None or symbol:
            raise ValueError(f"Plik łączny {r} nie ma numeru ani symbolu specjalności (zał. 1 RPB poz. 5–8)")
        return f"{r}_{z}.pdf"
    if r == "PT":
        if nr is None and symbol is None:
            return f"PT_{z}.pdf"
        if nr is None or not symbol:
            raise ValueError("Tom PT w wielu plikach wymaga numeru pliku x i symbolu specjalności y (PT_x_y_z)")
        s = symbol.upper()
        if s not in SYMBOLE_Y:
            raise ValueError(f"Nieznany symbol specjalności {symbol!r}; dopuszczalne: {', '.join(SYMBOLE_Y)}")
        return f"PT_{int(nr)}_{s}_{z}.pdf"
    if r in ("PZT", "PAB", "ZL"):
        if symbol:
            raise ValueError(f"Symbol specjalności dotyczy tylko tomów PT, nie {r}")
        return f"{r}_{int(nr)}_{z}.pdf" if nr is not None else f"{r}_{z}.pdf"
    raise ValueError(f"Nieznany rodzaj pliku {rodzaj!r}; dopuszczalne: "
                     f"{', '.join(RODZAJE_POJEDYNCZE + RODZAJE_LACZNE)}")


def sprawdz_nazwe(nazwa: str, rodzaj: str | None = None) -> tuple[bool, str]:
    """(zgodna, opis). ``rodzaj=None`` — dopasowanie do dowolnego wzorca zał. 1."""
    wz = {rodzaj.upper(): WZORCE[rodzaj.upper()]} if rodzaj else WZORCE
    for r, w in wz.items():
        if re.match(w, nazwa):
            return True, f"nazwa zgodna z zał. 1 RPB ({r})"
    oczek = ", ".join(sorted(wz)) if rodzaj is None else wz[rodzaj.upper()]
    return False, f"nazwa „{nazwa}” niezgodna z zał. 1 RPB (oczekiwano: {oczek})"


def rodzaj_z_nazwy(nazwa: str) -> str | None:
    for r in ("PZT_PAB_ZL", "PZT_PAB", "PZT_ZL", "PAB_ZL", "PZT", "PAB", "PT", "ZL"):
        if re.match(WZORCE[r], nazwa):
            return r
    return None
