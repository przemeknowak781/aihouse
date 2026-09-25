"""Budowniczy detali PT (architektura) — geometria z przegród i elementów `model/budynek.yaml`.

Każdy budowniczy: fn(model, opts) -> `Detal` (układ lokalny: x w prawo = na zewnątrz, wnętrze x < 0 — o ile opis nie
mówi inaczej; y w górę; `Detal.z0` — rzędna poziomu y = 0 względem ±0,00). Grubości warstw zawsze z modelu
(`Detal.stos_v/stos_h`); elementy wykonawcze spoza modelu (obróbki, taśmy, profile, rynny) — wymiary typowe [ZAŁ]
opisane na rysunku. Konwencja płyt wg audytu A2 (K-1): stropy do lica konstrukcji, wierzch płyt wspornikowych
zrównany ze stropem, łącznik termoizolacyjny w strefie izolacji.

`RODZAJE` — rodzaj → budowniczy; `WEZEL_RODZAJ` — id węzła sekcji `wezly` → rodzaj detalu.
"""
from __future__ import annotations

import numpy as np

from .detale_geom import Detal, mm, skrot_nazwy

RODZAJE: dict = {}
WEZEL_RODZAJ: dict = {}


def rodzaj(nazwa: str, *wezly: str):
    def dec(fn):
        RODZAJE[nazwa] = fn
        for w in wezly:
            WEZEL_RODZAJ.setdefault(w, nazwa)
        return fn
    return dec


# ---------------------------------------------------------------------------------------------- pomocnicze
def wpis(m, wid: str) -> dict:
    return next((e for e in (m.raw.get("wezly") or []) if str(e.get("id")) == wid), {})


def przegroda_typu(m, wid: str, typ: str, domyslna: str | None = None) -> str | None:
    for k in wpis(m, wid).get("przegrody") or []:
        p = m.przegroda(k)
        if p is not None and p.typ == typ:
            return k
    if domyslna and m.przegroda(domyslna) is not None:
        return domyslna
    return next((k for k, p in m.przegrody.items() if p.typ == typ), None)


def grubosc(m, kod: str) -> float:
    return float(sum(w.d for w in m.przegroda(kod).warstwy))


def teren(m) -> float:
    """Rzędna terenu przy budynku [m wzgl. ±0,00] — z modelu (energia.wentylacja.rzedna_terenu), inaczej −0,30."""
    e = (m.raw.get("energia") or {}).get("wentylacja") or {}
    try:
        return float(e.get("rzedna_terenu", -0.30))
    except (TypeError, ValueError):
        return -0.30


def x_konstr(stos) -> tuple[float, float]:
    """(lico wewn., lico zewn.) warstwy konstrukcyjnej ze stosu stos_v."""
    for a, b, w in stos:
        if w["konstr"]:
            return a, b
    return stos[0][0], stos[-1][1]


def x_izol(stos) -> tuple[float, float]:
    """(lico wewn., lico zewn.) warstwy izolacji cieplnej ściany (pierwsza warstwa λ ≤ 0,06 za konstrukcją)."""
    k = next(i for i, (_a, _b, w) in enumerate(stos) if w["konstr"])
    for a, b, w in stos[k + 1:]:
        if w["mat"] in ("EPS031", "WELNA_FAS", "XPS300", "WELNA_035", "PIR022") or "izol" in w.get("funkcja", ""):
            return a, b
    return stos[k][1], stos[-1][1]


def fundament_pod(m, x_os: float = 0.0) -> dict:
    """Płyta fundamentowa i żebro pod ścianą zewnętrzną (pierwsze pogrubienie) z modelu."""
    f = m.fundamenty() or {}
    el = f.get("elementy") or []
    plyta = next((e for e in el if "obrys" in e), {})
    zebro = next((e for e in el if "os" in e and float(e.get("b", 0)) >= 0.5), {})
    return {"plyta": plyta, "zebro": zebro, "obwodowa": f.get("izolacja_obwodowa") or {}}


def tekst(det: Detal, mat: str, d: float | None = None, dopisek: str = "") -> str:
    n, _l, _k = det.mat_info(mat)
    s = skrot_nazwy(n)
    return s + (f" — {mm(d)} mm" if d else "") + (f" {dopisek}" if dopisek else "")
