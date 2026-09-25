"""Formatowanie liczb wg polskiej praktyki rysunkowej (PN-B-01029:2000, PN-B-01025:2004).

* separator dziesiętny: przecinek,
* wymiary liniowe na rysunkach architektoniczno-budowlanych: centymetry, milimetry w indeksie górnym (np. 24⁵),
* rzędne wysokościowe: metry, 3 miejsca po przecinku (PN-B-01025 pkt 3.5; PZT — 2 miejsca), znak ±/+/−,
* powierzchnie: m² z 2 miejscami po przecinku.
"""
from __future__ import annotations

import math

MINUS = "−"  # znak minus (typograficzny) — obecny w Liberation Sans / DejaVu Sans
PLUSMINUS = "±"

# Liczba miejsc po przecinku rzędnych: PN-B-01025 pkt 3.5 — 3 miejsca (R4 pkt 3.6: rysunki arch.-bud. i konstrukcyjne);
# PZT — 2 miejsca (PN-B-01027). Zmiana globalna: fmt.LEVEL_DECIMALS = 2.
LEVEL_DECIMALS = 3
LEVEL_DECIMALS_PZT = 2


def num(x: float, nd: int = 2, minus: str = MINUS, strip: bool = False) -> str:
    """Liczba z przecinkiem dziesiętnym, np. num(12.345) -> '12,35'."""
    if nd <= 0:
        s = f"{round(x):d}"
    else:
        s = f"{x:.{nd}f}"
    if strip and "." in s:
        s = s.rstrip("0").rstrip(".")
    s = s.replace(".", ",")
    if s.startswith("-"):
        body = s[1:]
        if set(body) <= set("0,"):
            return body  # -0,00 -> 0,00
        s = minus + body
    return s


def round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5)) if x >= 0 else -int(math.floor(-x + 0.5))


def dim_parts(length_m: float, unit: str = "cm") -> tuple[str, str]:
    """Liczba wymiarowa jako (część główna, indeks górny).

    unit='cm'  : 0.245 -> ('24', '5');  1.00 -> ('100', '');  0.012 -> ('1', '2')
    unit='mm'  : 0.245 -> ('245', '')      (rysunki konstrukcji stalowych, detale)
    unit='m'   : 12.5  -> ('12,50', '')    (PZT)
    """
    L = abs(length_m)
    if unit == "mm":
        return f"{round_half_up(L * 1000):d}", ""
    if unit == "m":
        return num(L, 2), ""
    mm = round_half_up(L * 1000)
    cm, rest = divmod(mm, 10)
    return f"{cm:d}", (f"{rest:d}" if rest else "")


def dim_text(length_m: float, unit: str = "cm") -> str:
    """Wymiar jako zwykły napis (indeks górny zapisany znakiem Unicode — tylko do podglądu/testów)."""
    main, sup = dim_parts(length_m, unit)
    sup_map = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return main + sup.translate(sup_map)


def level(z: float, nd: int | None = None) -> str:
    """Rzędna wysokościowa: ±0,000 / +3,150 / −1,200 (PN-B-01025:2004 pkt 3.5; nd domyślnie LEVEL_DECIMALS)."""
    nd = LEVEL_DECIMALS if nd is None else nd
    q = 10 ** nd
    if round_half_up(abs(z) * q) == 0:
        return PLUSMINUS + num(0.0, nd)
    return ("+" if z > 0 else MINUS) + num(abs(z), nd)


def level_abs(h: float, nd: int | None = None) -> str:
    """Rzędna bezwzględna (m n.p.m.), bez znaku: 101,650."""
    return num(h, LEVEL_DECIMALS if nd is None else nd)


def area(a_m2: float, nd: int = 2, unit: bool = True) -> str:
    return num(a_m2, nd) + (" m²" if unit else "")


def percent(p: float, nd: int = 1) -> str:
    return num(p, nd, strip=False) + "%"


def scale_str(scale: float) -> str:
    """Oznaczenie podziałki wg PN-EN ISO 5455: '1:50', '1:100', '2:1'."""
    if scale >= 1:
        return f"1:{scale:g}"
    return f"{1 / scale:g}:1"
