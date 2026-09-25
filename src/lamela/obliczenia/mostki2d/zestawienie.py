"""Zestawienie mostków cieplnych budynku (sekcja `wezly` modelu + węzły wykryte w geometrii):

* `dlugosci_geometryczne(model, wezly)` — długości liniowych mostków policzone z GEOMETRII modelu (obrysy
  kondygnacji, dachy, płyty wspornikowe, stropy, ściany, otwory, pomieszczenia) — niezależnie od pola `dlugosc`
  sekcji `wezly`; każdy odcinek krawędzi obudowy przypisany do jednego węzła (bez podwójnego liczenia);
* `mostki_punktowe(model)` — χ i liczby mostków punktowych (konsole lamel, kotwy, przejścia instalacji);
* `ocena_4_linii(...)` — ciągłość „4 linii” (izolacja cieplna, hydroizolacja, szczelność powietrzna, paroizolacja
  / kontrola pary) dla karty węzła;
* `raport_zestawienia(...)` — Markdown: tabela węzłów, porównanie długości model ↔ geometria, H_TB.

System wymiarów: wewnętrzne całkowite (ψ_oi, `energia.bryla`); długości po krawędziach obrysu zewnętrznego
(przyjęcie [INT] — różnica ≤ grubość ściany na narożach, pomijalna wobec dokładności ψ).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from .katalog_dod import (TOL_Z, _krawedzie, _max, _pom_pod, kond_przy, krawedzie_stropu_zewn, nieogrzewane,
                          sciany_wzdluz, wspornik_z_nazwy)

KROK = 0.125     # [m] krok próbkowania krawędzi obrysów


def _probki(ed: LineString, krok: float = KROK):
    """Odcinki krawędzi (s0, s1, punkt środkowy, wersor, normalna) co `krok`."""
    c = np.asarray(ed.coords)
    u = (c[-1] - c[0]) / ed.length
    n = np.array([-u[1], u[0]])
    N = max(1, int(round(ed.length / krok)))
    for k in range(N):
        s0, s1 = k * ed.length / N, (k + 1) * ed.length / N
        yield s0, s1, c[0] + u * (s0 + s1) / 2, u, n


def _do_wnetrza(P: Polygon, pm, n) -> np.ndarray:
    return n if P.buffer(1e-6).contains(Point(pm + n * 0.2)) else -n


def _ogrzewane_pod(model, xy, z: float) -> bool | None:
    """Czy pod płytą (wierzch z) w punkcie rzutu jest pomieszczenie ogrzewane (None — brak pomieszczenia)."""
    rs = [_pom_pod(model, xy + np.array(d), z) for d in ((0, 0), (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3))]
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    return not (sum(map(nieogrzewane, rs)) * 2 >= len(rs))


def _ogrzewane_w(model, kid: str, xy) -> bool | None:
    for r in model.pomieszczenia(kid):
        g = getattr(r, "polygon", None)
        if g is not None and g.buffer(0.05).contains(Point(xy)):
            return not nieogrzewane(r)
    return None


def _wsporniki_lacznik(model, z: float) -> list[Polygon]:
    return [Polygon(w["obrys"]) for w in model.wsporniki()
            if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]


def _blisko(pt, polys, tol=0.06) -> bool:
    p = Point(pt)
    return any(P.distance(p) <= tol for P in polys)


def _pokrycie(model, ed: LineString, kondy, typy=("sciana_zewn",), tol=0.35) -> list[tuple[float, float, str]]:
    """Przedziały [s0, s1] krawędzi `ed` pokryte osiami ścian równoległych (kondygnacje `kondy`)."""
    c = np.asarray(ed.coords)
    u = (c[-1] - c[0]) / ed.length
    out = []
    for s in model.sciany():
        if s.kond not in kondy or (typy and s.typ not in typy):
            continue
        if abs(u[0] * s.u[1] - u[1] * s.u[0]) > 0.17:
            continue
        ax = LineString([tuple(s.p1), tuple(s.p2)])
        if ax.distance(ed) > tol:
            continue
        a, b = sorted([float(np.dot(s.p1 - c[0], u)), float(np.dot(s.p2 - c[0], u))])
        a, b = max(a, 0.0), min(b, ed.length)
        if b - a > 0.05:
            out.append((a - tol, b + tol, s.przegroda_kod))   # przedłużenie o grubość — naroża
    return out


def _w(przedz, s) -> str | None:
    for a, b, k in przedz:
        if a - 1e-9 <= s <= b + 1e-9:
            return k
    return None


def klasyfikuj_obwod(model) -> dict[tuple, float]:
    """Długości odcinków obudowy wg kategorii: ('attyka', dach) | ('wsp', id płyty) | ('dach_sciana', dach) |
    ('strop_posredni', strop) | ('cokol',) | ('prog',). Próbkowanie krawędzi co KROK [INT]."""
    L: dict[tuple, float] = {}
    add = lambda k, v: L.__setitem__(k, L.get(k, 0.0) + v)
    # --- A. krawędzie dachów
    for d in model.dachy():
        pl = d.get("plyta") or {}
        if not pl:
            continue
        z = float(pl["wierzch"])
        P = Polygon(d["obrys"])
        wsp = [(w["id"], Polygon(w["obrys"])) for w in model.wsporniki()
               if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]
        for ed in _krawedzie(P):
            gora = _pokrycie(model, ed, kond_przy(model, z, "gora"))
            for s0, s1, pm, u, n in _probki(ed):
                n_in = _do_wnetrza(P, pm, n)
                ogrz = _ogrzewane_pod(model, pm + n_in * 0.6, z)
                if not ogrz:
                    continue
                if _w(gora, (s0 + s1) / 2):
                    add(("dach_sciana", d["id"]), s1 - s0)
                    continue
                wid = next((i for i, W in wsp if W.distance(Point(pm)) <= 0.06), None)
                add(("wsp", wid) if wid else ("attyka", d["id"]), s1 - s0)
    # --- B. krawędzie stropów pośrednich (obrys kondygnacji nad stropem)
    for st in model.stropy():
        z = float(st["wierzch"])
        if st.get("sufit") in model.przegrody:          # strop nad powietrzem — węzły WZ-07/16 (katalog_dod)
            continue
        k_g, k_d = kond_przy(model, z, "gora"), kond_przy(model, z, "dol")
        if not k_g or not k_d:
            continue
        obr = model.obrys_kondygnacji(k_g[0], lico="zewn")
        Q = Polygon(st["obrys"]).buffer(0.05)
        dachy = [Polygon(d_["obrys"]) for d_ in model.dachy()
                 if d_.get("plyta") and abs(float(d_["plyta"]["wierzch"]) - z) <= TOL_Z]
        wsp = [(w["id"], Polygon(w["obrys"])) for w in model.wsporniki()
               if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]
        for ed in _krawedzie(obr):
            if not Q.contains(ed.interpolate(0.5, normalized=True)):
                continue
            dol = _pokrycie(model, ed, k_d)
            for s0, s1, pm, u, n in _probki(ed):
                if not _w(dol, (s0 + s1) / 2):
                    continue
                n_in = _do_wnetrza(obr, pm, n)
                if _ogrzewane_pod(model, pm + n_in * 0.6, z) is False:
                    continue
                wid = next((i for i, W in wsp if W.distance(Point(pm)) <= 0.06), None)
                if wid:
                    add(("wsp", wid), s1 - s0)
                elif _blisko(pm, dachy):
                    continue                                   # dach – ściana (część A)
                else:
                    add(("strop_posredni", st["id"]), s1 - s0)
    # --- C. obwód parteru (cokół / progi)
    k0 = min(model.kondygnacje, key=lambda k: k.rzedna)
    obr0 = model.obrys_kondygnacji(k0.id, lico="zewn")
    progi = []
    for o in model.otwory(kond=k0.id):
        sc = o.sciana
        if sc is None or sc.typ != "sciana_zewn" or o.typ in ("otwor", "brama") or (o.parapet or 0.0) > 0.05:
            continue
        c_ = np.asarray(o.srodek)
        if _ogrzewane_w(model, k0.id, c_ + sc.n * sc.sgn_int * 0.6) is False:
            continue
        progi.append((c_, float(o.szer), sc.u))
    for ed in _krawedzie(obr0):
        for s0, s1, pm, u, n in _probki(ed):
            n_in = _do_wnetrza(obr0, pm, n)
            ogrz = [_ogrzewane_w(model, k0.id, pm + n_in * a) for a in (0.5, 0.8)]
            ogrz = [x for x in ogrz if x is not None]
            if not ogrz or not ogrz[0]:
                continue
            jest_prog = any(abs(float(np.dot(pm - c_, uu))) <= w / 2 and
                            abs(float(np.dot(pm - c_, np.array([-uu[1], uu[0]])))) <= 0.45 for c_, w, uu in progi)
            add(("prog",) if jest_prog else ("cokol",), s1 - s0)
    return L
