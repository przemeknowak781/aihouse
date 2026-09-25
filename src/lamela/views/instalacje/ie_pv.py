"""IE-PV — instalacja fotowoltaiczna (moduły na dachu, łańcuchy, trasa DC, falownik, SPD) i IE-U — uziom,
połączenia wyrównawcze, ochrona odgromowa (decyzja z analizy ryzyka PN-EN IEC 62305-2 — obliczenia).

Dane: ``lamela.obliczenia.elektryka.pv`` (liczba modułów, moc, wariant EW/S, łańcuchy, DC, SPD) i
``lamela.obliczenia.elektryka.odgromowa`` (uziom, LPS, wyrównania). Rozmieszczenie modułów wyznaczane
algorytmicznie w polu użytkowym dachu (odsunięcie od krawędzi z obliczeń, bez otworów, wpustów, czerpni/wyrzutni
i wywiewek z odstępem 1,0 m)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ...draft import fmt, symbols as S
from ...draft.geom import polygons_of
from .baza import Rysunek
from .ie_rzut import RysE, _box
from .wspolne import BRAK, H_S, num, table_block


def uklad_modulow(pole, n, dl, sz, wariant="EW10", przerwa=0.60):
    """Rozmieszczenie n modułów w wieloboku ``pole``. EW: pary wschód–zachód (grzbiet N–S), rzędy ciągłe N–S,
    przejścia serwisowe ``przerwa`` między blokami; S: rzędy z odstępem przeciwcieniowym. Zwraca listę
    (prostokąt, strona 'E'|'W'|'S')."""
    if n <= 0 or pole.is_empty:
        return []
    ew = str(wariant).upper().startswith("EW")
    tilt = math.radians(10.0 if ew else 15.0)
    L = dl * math.cos(tilt)
    pw = 2 * L + 0.05 if ew else sz
    ph = sz + 0.02 if ew else L + 0.9
    x0, y0, x1, y1 = pole.bounds
    best = []
    for ox in np.linspace(0, pw + przerwa, 6, endpoint=False):
        for oy in np.linspace(0, ph, 4, endpoint=False):
            mods = []
            x = x0 + ox
            while x + pw <= x1 + 1e-9 and len(mods) < n:
                y = y0 + oy
                while y + ph <= y1 + 1e-9 and len(mods) < n:
                    if ew:
                        for side, xa in (("W", x), ("E", x + L + 0.05)):
                            r = box(xa, y, xa + L, y + sz)
                            if pole.contains(r) and len(mods) < n:
                                mods.append((r, side))
                    else:
                        r = box(x, y, x + sz, y + L)
                        if pole.contains(r):
                            mods.append((r, "S"))
                    y += ph
                x += pw + przerwa
            if len(mods) > len(best):
                best = mods
            if len(best) >= n:
                return best[:n]
    return best[:n]


class RysPV(RysE):
    br = "IE"
    kod = "IE-PV"

    def run(self):
        if self.dach:
            self.podklad()
            self.siatka(extra_pts=[], sciany=0.0, przy_scianie=1.0, poza=0.0)
            self.obw = self.W.obwody.obwody
            self.circuits_used = set()
            self.dach_pv()
        else:
            self.prepare()
            self.parter_pv()
        self.opisy()
        return self.finish(rooms=not self.dach)

    def _pole(self):
        pv = self.W.pv
        did = (pv.dach or {}).get("id", "D1")
        d = next((d for d in self.m.dachy() if str(d.get("id")) == did), None)
        if d is None:
            return None, None
        poly = Polygon(d["obrys"])
        at = float((d.get("attyka") or {}).get("szer", 0.25))
        pole = poly.buffer(-(at + float(pv.par.odstep_od_krawedzi)), join_style=2)
        obst = [Polygon(o).buffer(0.5, join_style=2) for o in (d.get("otwory") or [])]
        lok = self.W.dane.inst.get("lokalizacje") or {}
        for key in ("czerpnia", "wyrzutnia"):
            if lok.get(key):
                obst.append(Point(lok[key][:2]).buffer(1.0))
        ew = self.W.energia_went
        for xy in (getattr(getattr(ew, "centrala", None), "get", lambda *_: None)("wywiewki") or []):
            obst.append(Point(xy[:2]).buffer(1.0))
        for w in (self.W.dane.inst.get("piony") or []):
            if "wywiewk" in str(w.get("opis", "")).lower() or "ponad dach" in str(w.get("opis", "")).lower():
                obst.append(Point(w["xy"][:2]).buffer(1.0))
        for w in d.get("wpusty") or []:
            xy = w.get("xy") if isinstance(w, dict) else w
            obst.append(Point(xy).buffer(0.6))
        if obst:
            pole = pole.difference(unary_union(obst))
        return d, pole
