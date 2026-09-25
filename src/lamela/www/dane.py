"""Dane strony www wyliczane WYŁĄCZNIE z modelu (budynek.yaml, dzialka.yaml, wyposazenie.yaml) i modułów obliczeń.

``zbierz(budynek, dzialka, wyposazenie) -> dict`` — słownik ``D`` z wartościami liczbowymi i opisem metody/podstawy;
teksty strony formatują je funkcjami ``fm``/``fm_m2`` (zapis polski, 2 miejsca po przecinku jak w RPB).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from ..ir import build_ir
from ..model import load_model, make_polygon
from ..wskazniki import wskazniki

KLATKI = ("klatka schodowa",)          # jak tools/podglad_modelu.py (bilans W-316)
NBSP = " "


def fm(v, n: int = 2) -> str:
    """Liczba w zapisie polskim: separator tysięcy — wąska spacja niełamiąca, przecinek dziesiętny."""
    if v is None:
        return "—"
    s = f"{float(v):,.{n}f}".replace(",", "X").replace(".", ",").replace("X", NBSP)
    return s.replace("-", "−")


def fm_m2(v, n: int = 2) -> str:
    return f"{fm(v, n)}{NBSP}m²"


# ------------------------------------------------------------------------------------------------ powierzchnie
def powierzchnie(m) -> dict:
    """Zestawienie pomieszczeń i PU wg RPB § 20 / PN-ISO 9836 (rejestr W-316): PU bez klatek schodowych, garażu
    i pomieszczeń technicznych; waga wysokości w świetle ≥ 2,20 → 100 %, 1,40–2,20 → 50 %, < 1,40 → 0 %."""
    wiersze, pu, gar, tech, klat = [], {}, 0.0, 0.0, 0.0
    for r in m.pomieszczenia():
        rodz = str(r.raw.get("rodzaj") or "")
        nm = r.nazwa.lower()
        if any(s in nm for s in KLATKI):
            grupa = "klatka"
            klat += r.pow_netto
        elif rodz == "garaz" or "garaż" in nm:
            grupa = "garaz"
            gar += r.pow_netto
        elif r.kategoria == "techniczna":
            grupa = "techniczne"
            tech += r.pow_netto
        else:
            grupa = "PU"
            pu[r.kond] = pu.get(r.kond, 0.0) + r.pow_zaliczona
        wiersze.append(dict(id=r.id, kond=r.kond, nazwa=r.nazwa, kat=r.kategoria, A=round(r.pow_netto, 2),
                            h=round(r.wysokosc or 0.0, 2), wsp=r.wsp_wysokosci, A_zal=round(r.pow_zaliczona, 2),
                            grupa=grupa, pobyt=bool(r.pobyt_ludzi), rodzaj=rodz))
    return dict(pomieszczenia=wiersze, PU=round(sum(pu.values()), 2), PU_kond={k: round(v, 2) for k, v in pu.items()},
                garaz=round(gar, 2), techniczne=round(tech, 2), klatki=round(klat, 2),
                netto=round(sum(w["A"] for w in wiersze), 2),
                metoda="RPB § 20 ust. 1 pkt 4 / PN-ISO 9836 (W-316): suma pow. netto pomieszczeń z wagą wysokości "
                       "w świetle (≥ 2,20 m — 100 %, 1,40–2,20 m — 50 %, < 1,40 m — 0 %), bez klatek schodowych, "
                       "garażu i pomieszczeń technicznych (wykazane osobno)")


def _poz(w, k):
    v = w.get(k) or {}
    return v.get("wartosc"), v


# ------------------------------------------------------------------------------------------------ WT § 12
def _krawedzie(poly) -> list:
    """Odcinki obrysu z normalną zewnętrzną (obrys CCW → normalna = obrót kierunku o −90°)."""
    from shapely.geometry.polygon import orient
    out = []
    for pg in getattr(poly, "geoms", [poly]):
        c = list(orient(pg, 1.0).exterior.coords)
        for a, b in zip(c[:-1], c[1:]):
            d = np.subtract(b, a)
            L = float(np.hypot(*d))
            if L < 0.05:
                continue
            n = np.array([d[1], -d[0]]) / L
            out.append((np.array(a), np.array(b), n, L))
    return out


def dzialka_minimalna(m) -> dict:
    """Minimalne wymiary prostokątnej działki z gabarytów i odległości od granic wg WT § 12 (rejestr W-001…W-006).

    Metoda: każdy odcinek lica zewnętrznego każdej kondygnacji (płaszczyzna uskoku = odrębna ściana, W-001) dostaje
    wymaganie 4,00 m, gdy ma okna/drzwi (ust. 1 pkt 1), lub 3,00 m bez otworów (ust. 1 pkt 2); płyty wysunięte,
    okapy, daszek wejścia i tarasy — 1,50 m (ust. 6, ostrożnie także tarasy naziemne). Od strony drogi odległości
    § 12 nie obowiązują (ust. 10) — przyjęto odległość linii zabudowy z modelu działki (MPZP). Wynik: najmniejszy
    prostokąt granic spełniający wszystkie wymagania przy orientacji budynku jak w modelu."""
    lim = {"W": [], "E": [], "S": [], "N": []}

    def dodaj(strona, wart, opis, d):
        lim[strona].append((wart, opis, d))
    for k in m.kondygnacje:
        ob = m.obrys_kondygnacji(k.id)
        if ob.is_empty:
            continue
        otw = [o for o in m.otwory(kond=k.id) if o.kierunek_zewn is not None and o.sciana.typ == "sciana_zewn"
               and o.typ not in ("otwor",)]
        for a, b, n, L in _krawedzie(ob):
            seg = LineString([tuple(a), tuple(b)])
            ma = any(float(np.dot(o.kierunek_zewn, n)) > 0.9 and
                     seg.distance(Point(*(o.srodek[:2] + o.kierunek_zewn * (abs(o.sciana.face_t(o.sciana.ext_side)) + 0.01)))) < 0.6
                     for o in otw)
            d = 4.0 if ma else 3.0
            opis = f"lico {k.id} {'z oknami/drzwiami' if ma else 'bez otworów'}"
            for strona, ok, wsp in (("W", n[0] < -0.9, min(a[0], b[0])), ("E", n[0] > 0.9, max(a[0], b[0])),
                                    ("S", n[1] < -0.9, min(a[1], b[1])), ("N", n[1] > 0.9, max(a[1], b[1]))):
                if ok:
                    dodaj(strona, wsp, opis, d)
    inne = [(w.get("id"), w.get("obrys"), "płyta/okap") for w in m.wsporniki()]
    inne += [(t.get("id"), t.get("obrys"), "taras") for t in m.tarasy()]
    inne += [(d.get("id"), d.get("obrys"), "dach/okap") for d in m.dachy()]
    for i, ob, rodz in inne:
        try:
            g = make_polygon(ob)
        except Exception:  # noqa: BLE001
            continue
        x0, y0, x1, y1 = g.bounds
        for strona, wsp in (("W", x0), ("E", x1), ("S", y0), ("N", y1)):
            dodaj(strona, wsp, f"{rodz} {i}", 1.5)
    return _prostokat(m, lim)
