"""Metryka pisma: pomiar szerokości napisów i konwersja wysokości wielkich liter (h wg ISO 3098) na rozmiar czcionki.

Wszystkie wysokości ``h`` w silniku oznaczają wysokość WIELKICH LITER w mm na arkuszu (tak jak w PN-EN ISO 3098
i jak interpretują wysokość tekstu TrueType programy CAD).
"""
from __future__ import annotations

import os
from functools import lru_cache

from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath, TextToPath

from .styles import FONT_FILES

_T2P = TextToPath()
_REF = 100.0  # rozmiar referencyjny (pt) do pomiarów


@lru_cache(maxsize=None)
def font_file(style: str = "normal") -> str:
    for f in FONT_FILES.get(style, FONT_FILES["normal"]):
        if os.path.exists(f):
            return f
    raise FileNotFoundError(f"Brak czcionki dla stylu {style!r}")


@lru_cache(maxsize=None)
def font_props(style: str = "normal") -> FontProperties:
    return FontProperties(fname=font_file(style), size=_REF)


@lru_cache(maxsize=None)
def cap_ratio(style: str = "normal") -> float:
    """Stosunek wysokości wielkiej litery do rozmiaru em."""
    p = TextPath((0, 0), "H", size=_REF, prop=font_props(style))
    return p.get_extents().y1 / _REF


@lru_cache(maxsize=None)
def descent_ratio(style: str = "normal") -> float:
    p = TextPath((0, 0), "gjpqy", size=_REF, prop=font_props(style))
    return -p.get_extents().y0 / _REF


def em_mm(h_cap: float, style: str = "normal") -> float:
    """Rozmiar em [mm] odpowiadający wysokości wielkich liter h_cap [mm]."""
    return h_cap / cap_ratio(style)


@lru_cache(maxsize=65536)
def _width_ref(s: str, style: str) -> float:
    if not s:
        return 0.0
    w, _h, _d = _T2P.get_text_width_height_descent(s, font_props(style), ismath=False)
    return w / _REF  # w jednostkach em


def width(s: str, h_cap: float, style: str = "normal") -> float:
    """Szerokość napisu [mm] przy wysokości wielkich liter h_cap [mm]."""
    return _width_ref(s, style) * em_mm(h_cap, style)


# ---------------------------------------------------------------------------------------- napisy złożone
# Napis może składać się z "przebiegów" (runs): (tekst, względna wysokość, względne podniesienie linii bazowej).
# Służy to np. do zapisu wymiaru 24⁵ (mm w indeksie górnym) jako dwóch zwykłych napisów — tak samo w PDF i DXF.
SUP_SIZE = 0.72   # wysokość indeksu górnego względem h (2,5 → 1,8 mm — najmniejsza z szeregu ISO 3098)
SUP_RAISE = 0.50  # podniesienie linii bazowej indeksu względem h


_SERIES = (1.8, 2.5, 3.5, 5.0, 7.0, 10.0, 14.0, 20.0)


def run_h(h_cap: float, f: float) -> float:
    """Wysokość przebiegu: indeks górny (f == SUP_SIZE) = poprzednia wartość szeregu ISO 3098 (min. 1,8 mm)."""
    if abs(f - SUP_SIZE) < 1e-9:
        below = [x for x in _SERIES if x < h_cap - 1e-6]
        return below[-1] if below else _SERIES[0]
    return h_cap * f


def runs_width(runs, h_cap: float, style: str = "normal") -> float:
    w = 0.0
    for i, (s, f, _r) in enumerate(runs):
        w += width(s, run_h(h_cap, f), style)
        if i and f != runs[i - 1][1]:
            w += 0.06 * h_cap
    return w


def layout_runs(runs, h_cap: float, style: str = "normal", ha: str = "left", va: str = "baseline"):
    """Pozycje przebiegów w układzie lokalnym napisu (mm, oś x wzdłuż napisu, y w górę).

    Zwraca listę (x, y, tekst, h) — x,y to początek linii bazowej przebiegu — oraz (szer., wys. wielkich liter).
    ha: 'left' | 'center' | 'right'; va: 'baseline' | 'bottom' | 'middle' | 'top'.
    """
    W = runs_width(runs, h_cap, style)
    x0 = {"left": 0.0, "center": -W / 2.0, "right": -W}[ha]
    top = max((run_h(h_cap, f) / h_cap + r) for (_s, f, r) in runs) * h_cap
    if va == "baseline":
        y0 = 0.0
    elif va == "middle":
        y0 = -h_cap / 2.0
    elif va == "top":
        y0 = -top
    elif va == "bottom":
        y0 = descent_ratio(style) * em_mm(h_cap, style)
    else:
        raise ValueError(va)
    out = []
    x = x0
    for i, (s, f, r) in enumerate(runs):
        if i and f != runs[i - 1][1]:
            x += 0.06 * h_cap
        hh = run_h(h_cap, f)
        out.append((x, y0 + r * h_cap, s, hh))
        x += width(s, hh, style)
    return out, (W, top)
