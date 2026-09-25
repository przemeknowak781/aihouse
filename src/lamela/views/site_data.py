"""Dane projektu zagospodarowania działki (PZT) wyznaczane z modelu (``model/dzialka.yaml`` + ``model/budynek.yaml``).

Wszystko w UKŁADZIE DZIAŁKI (początek = narożnik SW działki, x → wschód, y → północ [m]); geometria budynku
przeliczana transformacją ``dzialka.yaml: uklad`` (``Dzialka.do_dzialki``). Moduł nie rysuje — dostarcza:

* geometrię: działka, sąsiedzi, droga, linia zabudowy, obrys przyziemia i wyższych kondygnacji, płyty/okapy,
  tarasy, utwardzenia, zieleń, ogrodzenie, uzbrojenie istniejące i projektowane, obiekty, retencja, odwodnienia,
* teren: interpolację TIN rzędnych istniejących i projektowanych, warstwice,
* wskaźniki (pow. zabudowy, PBC, intensywność, wysokość zabudowy — upzp art. 2 pkt 28–35, RPB § 14 pkt 4),
* odległości od granic (WT § 12) i koordynację sieci (odległości poziome, skrzyżowania, kolizje),
* listę braków danych (``braki``) — do raportu i ``projekt/02_PZT/BRAKI_DANYCH.md``.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon, box
from shapely.ops import nearest_points, unary_union

from ..draft.geom import polygons_of

TODO = "[DO UZUPEŁNIENIA]"

# branże uzbrojenia: kod modelu → (litera mapy zasadniczej, nazwa, kolor wydruku)
BRANZE = {
    "woda": ("w", "wodociąg / przyłącze wodociągowe", "#0050c8"),
    "kan_sanit": ("ks", "kanalizacja sanitarna", "#7a4a1a"),
    "kan_deszcz": ("kd", "kanalizacja deszczowa", "#00808a"),
    "en": ("e", "elektroenergetyczna nN (kabel)", "#d00000"),
    "tele": ("t", "telekomunikacyjna (światłowód)", "#e07800"),
    "gaz": ("g", "gazowa", "#a89a00"),
    "cieplo": ("c", "ciepłownicza", "#8000a0"),
}
BRANZA_ALIAS = {"energ": "en", "elektro": "en", "tel": "tele", "kanal": "kan_sanit", "kd": "kan_deszcz",
                "ks": "kan_sanit", "w": "woda", "e": "en", "t": "tele", "g": "gaz"}

# Domyślne minimalne odległości poziome między sieciami [m] (zasady wiedzy technicznej — NIE przepis; WT § 26–28
# nie określają odległości). Nadpisywane w konfiguracji arkuszy: opcje.odleglosci_min.
ODL_MIN_DOMYSLNE = {
    "w-ks": (1.50, "praktyka proj. (COBRTI INSTAL z. 3) [SPRAWDŹ]"),
    "w-kd": (1.50, "praktyka proj. (COBRTI INSTAL z. 3) [SPRAWDŹ]"),
    "w-e": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "w-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "ks-kd": (1.00, "praktyka proj. [SPRAWDŹ]"),
    "e-ks": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "e-kd": (0.50, "N SEP-E-004:2014 [SPRAWDŹ]"),
    "e-t": (0.50, "N SEP-E-004:2014 (mniej — przy rurach osłonowych) [SPRAWDŹ]"),
    "ks-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "kd-t": (0.50, "praktyka proj. [SPRAWDŹ]"),
    "g-*": (0.50, "PN-EN 12007-1 / praktyka [SPRAWDŹ]"),
    "drzewo": (2.00, "od pnia: N SEP-E-004 (kable), praktyka (rurociągi) [SPRAWDŹ]"),
}


def ring(v) -> list | None:
    if not isinstance(v, (list, tuple)) or len(v) < 3:
        return None
    try:
        return [(float(p[0]), float(p[1])) for p in v]
    except (TypeError, ValueError, IndexError):
        return None


def poly(v) -> Polygon | None:
    r = ring(v)
    if r is None:
        return None
    g = Polygon(r)
    if not g.is_valid:
        g = shapely.make_valid(g)
        g = unary_union(polygons_of(g))
    return g if not g.is_empty else None


def line(v) -> LineString | None:
    if not isinstance(v, (list, tuple)) or len(v) < 2:
        return None
    try:
        return LineString([(float(p[0]), float(p[1])) for p in v])
    except (TypeError, ValueError, IndexError):
        return None


def branza(code) -> str:
    c = str(code or "").strip()
    return BRANZA_ALIAS.get(c, c)


def lit(code) -> str:
    return BRANZE.get(branza(code), (str(code), str(code), "#000000"))[0]


def num_in(text, pattern, default=None):
    """Liczba z opisu (np. „strefa R290 1,0 m”) — zapasowe źródło, gdy brak pola strukturalnego."""
    m = re.search(pattern, str(text or ""))
    if not m:
        return default
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return default


@dataclass
class Brak:
    pole: str             # ścieżka pola w modelu (np. "dzialka.yaml: retencja.zbiornik.obrys")
    opis: str             # czego brakuje i do czego jest potrzebne
    propozycja: str       # proponowany format pola (SCHEMAT_MODELU.md §3/§6)
    arkusze: str = ""     # których rysunków dotyczy


@dataclass
class Siec:
    branza: str
    geom: LineString
    opis: str
    istn: bool
    dl: float | None = None
    id: str = ""

    @property
    def lit(self) -> str:
        return lit(self.branza)

    @property
    def kolor(self) -> str:
        return BRANZE.get(self.branza, ("", "", "#000000"))[2]


@dataclass
class Obiekt:
    id: str
    xy: np.ndarray
    opis: str
    raw: dict = field(default_factory=dict)


# ================================================================================================ dane PZT
class SiteData:
    """Zagospodarowanie działki w układzie działki — patrz docstring modułu."""

    def __init__(self, ctx, opts: dict | None = None):
        self.ctx = ctx
        self.m = m = ctx.model
        self.opts = dict(opts or {})
        self.dz = m.dz
        self.raw = (self.dz.raw if self.dz is not None else {}) or {}
        self.braki: list[Brak] = []
        self.zero_abs = float(m.zero_abs)
        u = self.raw.get("uklad") or {}
        a = math.radians(float(u.get("obrot") or 0.0))
        t = u.get("przesuniecie") or [0.0, 0.0]
        self._aff = [math.cos(a), -math.sin(a), math.sin(a), math.cos(a), float(t[0]), float(t[1])]
        self._load_plot()
        self._load_building()
        self._load_site()
        self._load_utilities()
        self._load_terrain()

    # ------------------------------------------------------------------ pomocnicze
    def brak(self, pole, opis, propozycja, arkusze="PZT-01…03"):
        if not any(b.pole == pole for b in self.braki):
            self.braki.append(Brak(pole, opis, propozycja, arkusze))

    def P(self, pts) -> np.ndarray:
        """Punkty układu budynku → układ działki."""
        return np.asarray(self.dz.do_dzialki(np.asarray(pts, float)), float)

    def G(self, g):
        """Geometria shapely układu budynku → układ działki."""
        return affinity.affine_transform(g, self._aff)

    # ------------------------------------------------------------------ działka, sąsiedzi, droga
    def _load_plot(self):
        r = self.raw
        d = r.get("dzialka") or {}
        self.dzialka = d
        self.nr = str(d.get("nr", "?"))
        self.plot = poly(d.get("obrys")) or Polygon()
        if self.plot.is_empty:
            self.brak("dzialka.yaml: dzialka.obrys", "brak obrysu działki — rysunek PZT niemożliwy",
                      "obrys: [[x, y], ...]")
        self.plot = shapely.geometry.polygon.orient(self.plot, 1.0) if not self.plot.is_empty else self.plot
        self.corners = np.asarray(self.plot.exterior.coords)[:-1] if not self.plot.is_empty else np.zeros((0, 2))
        self.sasiedzi = []
        for s in r.get("sasiedzi") or []:
            if not isinstance(s, dict):
                continue
            pg = poly(s.get("obrys"))
            zb = poly(s.get("zabudowa")) if s.get("zabudowa") else None
            n = s.get("kondygnacje")
            if n is None and zb is not None:
                n = self._kond_z_opisu(s.get("opis"))
            self.sasiedzi.append(dict(nr=str(s.get("nr", "")), poly=pg, bud=zb, opis=str(s.get("opis") or ""),
                                      wys=s.get("wys"), kond=n, raw=s))
        if any(s["bud"] is not None and s["raw"].get("kondygnacje") is None for s in self.sasiedzi):
            self.brak("dzialka.yaml: sasiedzi[].kondygnacje, sasiedzi[].funkcja",
                      "liczba kondygnacji i funkcja budynków sąsiednich (opis budynku na mapie wg BDOT500: np. „m2”) "
                      "— obecnie odczytywane z tekstu 'opis'", "kondygnacje: 2, funkcja: m   # m — mieszkalny")
        dr = r.get("droga") or {}
        self.droga = dict(symbol=str(dr.get("symbol", "")), nazwa=str(dr.get("nazwa", "")),
                          pas=poly(dr.get("linie_rozgraniczajace")), jezdnia=poly(dr.get("jezdnia")),
                          naw=str(dr.get("nawierzchnia", "")), raw=dr)
        lz = line(r.get("linia_zabudowy"))
        self.linia_zabudowy = lz
        if lz is None:
            self.brak("dzialka.yaml: linia_zabudowy", "brak linii zabudowy MPZP", "linia_zabudowy: [[x, y], [x, y]]")
        # odległość linii zabudowy od linii rozgraniczającej drogi
        self.lz_odl = None
        if lz is not None and self.droga["pas"] is not None:
            self.lz_odl = float(lz.distance(self.droga["pas"].exterior))
        # granice działki: odcinki z opisem strony (N/E/S/W) i informacją, czy graniczą z drogą
        self.granice = []
        if not self.plot.is_empty:
            C = self.corners
            ctr = np.asarray(self.plot.centroid.coords[0])
            for i in range(len(C)):
                a, b = C[i], C[(i + 1) % len(C)]
                seg = LineString([a, b])
                mid = (a + b) / 2
                nrm = mid - ctr
                ang = math.degrees(math.atan2(nrm[1], nrm[0])) % 360
                side = "E" if ang < 45 or ang >= 315 else "N" if ang < 135 else "W" if ang < 225 else "S"
                road = self.droga["pas"] is not None and seg.buffer(0.05).intersection(
                    self.droga["pas"].exterior).length > 0.5 * seg.length
                who = next((s["nr"] for s in self.sasiedzi if s["poly"] is not None
                            and seg.buffer(0.05).intersection(s["poly"].exterior).length > 0.3 * seg.length), None)
                self.granice.append(dict(i=i, seg=seg, a=a, b=b, strona=side, droga=road,
                                         sasiad=self.droga["symbol"] if road else who))

    @staticmethod
    def _kond_z_opisu(txt):
        t = str(txt or "").lower()
        m = re.search(r"(\d+)\s*kondygnac", t)
        if m:
            return int(m.group(1))
        if "parterow" in t and "poddasz" in t:
            return 2
        if "parterow" in t:
            return 1
        return None

    # ------------------------------------------------------------------ budynek
    def _load_building(self):
        from ..model import make_polygon
        from .common import storey_numbers
        m = self.m
        nums = storey_numbers(m)
        self.kond_nadziemne = [k.id for k in m.kondygnacje if nums.get(k.id, 1) >= 1]
        self.storeys = {}
        for kid in self.kond_nadziemne:
            g = m.obrys_kondygnacji(kid)
            if g is not None and not g.is_empty:
                self.storeys[kid] = self.G(g)
        k0 = next((k for k in self.kond_nadziemne if nums.get(k) == 1), None) or \
            (self.kond_nadziemne[0] if self.kond_nadziemne else None)
        self.k0 = k0
        self.p0 = self.storeys.get(k0, Polygon())
        self.footprint = unary_union(list(self.storeys.values())) if self.storeys else Polygon()
        # obrys wyższych kondygnacji poza przyziemiem (linia kreskowa)
        up = [g for k, g in self.storeys.items() if k != k0]
        self.upper = unary_union(up) if up else Polygon()
        self.upper_lines = self.upper.boundary.difference(self.p0.buffer(0.02, join_style=2)) \
            if not self.upper.is_empty else LineString()
        # płyty wspornikowe, okapy, dachy wykraczające poza obrys ścian (linia punktowa)
        slabs = []
        for it in list(m.wsporniki()) + list(m.dachy()):
            r = it.get("obrys")
            if not ring(r):
                continue
            g = self.G(make_polygon(r))
            if g.difference(self.footprint.buffer(0.02, join_style=2)).area < 0.05:
                continue
            slabs.append(dict(id=str(it.get("id", "")), poly=g, raw=it))
        self.slabs = slabs
        U = unary_union([s["poly"] for s in slabs]) if slabs else Polygon()
        self.slab_union = U
        self.slab_lines = U.boundary.difference(self.footprint.buffer(0.02, join_style=2)) if not U.is_empty \
            else LineString()
        # tarasy naziemne i podesty
        self.tarasy = []
        for t in m.tarasy():
            if ring(t.get("obrys")):
                self.tarasy.append(dict(id=str(t.get("id", "")), poly=self.G(make_polygon(t["obrys"])),
                                        naw=str(t.get("nawierzchnia") or ""), rz=t.get("rzedna"), raw=t))
        # wejścia i wjazd
        self.wejscia, self.wjazdy = [], []
        for o in m.otwory():
            w = o.sciana
            if w is None or w.ext_side is None or o.kond != k0:
                continue
            es = w.ext_side
            mid = (o.s0 + o.s1) / 2
            pf = self.P(w.pt(mid, w.face_t(es, "all")))
            dout = self.P(w.pt(mid, w.face_t(es, "all")) + o.kierunek_zewn) - pf
            rec = dict(id=o.id, typ=o.typ, pt=pf, out=dout / (np.hypot(*dout) or 1.0), szer=o.szer, o=o)
            if o.typ == "brama":
                self.wjazdy.append(rec)
            elif o.typ in ("drzwi_zewn", "drzwi_przesuwne_HS", "drzwi"):
                self.wejscia.append(rec)
        furtki = [np.asarray(b["xy"], float) for b in (self.raw.get("bramy") or [])
                  if isinstance(b, dict) and b.get("typ") == "furtka" and b.get("xy") is not None]
        dz_ = [e for e in self.wejscia if e["typ"] == "drzwi_zewn"] or self.wejscia
        ref = furtki[0] if furtki else (np.asarray(self.droga["pas"].centroid.coords[0])
                                        if self.droga["pas"] is not None else None)
        self.wejscie_gl = min(dz_, key=lambda e: float(np.hypot(*(e["pt"] - ref)))) if dz_ and ref is not None \
            else (dz_[0] if dz_ else None)
        # lica ścian zewnętrznych (każda płaszczyzna osobno — WT § 12 ust. 1) z informacją o otworach
        self.lica = []
        for kid, g in self.storeys.items():
            ops = [self.G(o.footprint) for o in m.otwory() if o.kond == kid and o.sciana is not None
                   and o.sciana.ext_side is not None and o.typ != "otwor"]
            for pg in polygons_of(g):
                C = np.asarray(shapely.geometry.polygon.orient(pg, 1.0).exterior.coords)
                for a, b in zip(C[:-1], C[1:]):
                    L = float(np.hypot(*(b - a)))
                    if L < 0.05:
                        continue
                    seg = LineString([a, b])
                    d = (b - a) / L
                    nout = np.array([d[1], -d[0]])          # CCW → na zewnątrz po prawej
                    has = any(o.intersects(seg.buffer(0.03)) for o in ops)
                    self.lica.append(dict(kond=kid, seg=seg, n=nout, otwory=has, L=L))

    # ------------------------------------------------------------------ zagospodarowanie
    def _polys(self, key):
        out = []
        for i, it in enumerate(self.raw.get(key) or []):
            if isinstance(it, dict):
                g = poly(it.get("obrys"))
                if g is not None:
                    out.append(dict(id=str(it.get("id", f"{key}{i + 1}")), poly=g, raw=it))
        return out

    def _load_site(self):
        r = self.raw
        self.utwardzenia = self._polys("utwardzenia")
        self.zielen = self._polys("zielen")
        self.miejsca = self._polys("miejsca_postojowe")
        od = r.get("odpady") or {}
        self.odpady = dict(poly=poly(od.get("obrys")), opis=str(od.get("opis") or "")) if isinstance(od, dict) else None
        self.drzewa = []
        for i, t in enumerate(r.get("drzewa") or []):
            if isinstance(t, dict) and t.get("xy") is not None:
                self.drzewa.append(dict(id=str(t.get("id", f"DR{i + 1}")), xy=np.asarray(t["xy"], float),
                                        d=float(t.get("sr_korony") or 3.0), istn=bool(t.get("istn")),
                                        usun=bool(t.get("do_wyciecia")), gat=str(t.get("gat") or ""),
                                        iglaste=bool(re.search(r"sosn|świerk|jodł|modrzew|cis|tuj|iglast",
                                                               str(t.get("gat") or "").lower())),
                                        wys=t.get("wys"), obwod=t.get("obwod"), raw=t))
        if any(t["istn"] and t["obwod"] is None for t in self.drzewa):
            self.brak("dzialka.yaml: drzewa[].obwod",
                      "obwód pnia drzew istniejących na wys. 5 cm (u.o.p. art. 83f ust. 4 — progi 80/65/50 cm) "
                      "i ewentualne pomniki przyrody (treść mapy do celów projektowych, rozp. 2022/1670 § 32)",
                      "obwod: 95   # cm, na wys. 5 cm; pomnik_przyrody: false")
        self.ogrodzenie = [dict(geom=line(o.get("linia")), wys=o.get("wys"), typ=str(o.get("typ") or ""), raw=o)
                           for o in (r.get("ogrodzenie") or []) if isinstance(o, dict) and line(o.get("linia"))]
        self.bramy = []
        for b in r.get("bramy") or []:
            if isinstance(b, dict) and b.get("xy") is not None:
                d = np.asarray(b.get("kierunek") or [1.0, 0.0], float)
                d = d / (np.hypot(*d) or 1.0)
                self.bramy.append(dict(xy=np.asarray(b["xy"], float), szer=float(b.get("szer") or 1.0),
                                       typ=str(b.get("typ") or ""), kier=d, wys=b.get("wys"), raw=b))
        if any(b["typ"] == "furtka" and b["raw"].get("otwieranie") is None for b in self.bramy):
            self.brak("dzialka.yaml: bramy[].otwieranie",
                      "strona zawiasów i kierunek otwierania furtki (WT § 42 ust. 1 — do wewnątrz działki)",
                      "otwieranie: {zawiasy: lewa|prawa, do: wewnatrz}", "PZT-01, PZT-02")
        # zjazd z drogi (pas drogowy) — brak w modelu → z podjazdu i bramy
        zj = r.get("zjazd") if isinstance(r.get("zjazd"), dict) else None
        self.zjazd = dict(poly=poly(zj.get("obrys")), opis=str(zj.get("opis") or ""), raw=zj) if zj else None
        if self.zjazd is None:
            self.brak("dzialka.yaml: zjazd",
                      "zjazd z drogi 1KDD w pasie drogowym (szerokość, skosy/łuki, nawierzchnia, przepust) — "
                      "wg zezwolenia zarządcy drogi (u.d.p. art. 29 ust. 3a); na rysunku przedłużenie podjazdu do "
                      "krawędzi jezdni w szerokości bramy", "zjazd: {obrys: [[x, y], ...], szer: 5.0, "
                      "promienie: 3.0, nawierzchnia: '...', decyzja: 'nr … z …'}", "PZT-01, PZT-02")
        rt = r.get("retencja") or {}
        zb = rt.get("zbiornik") if isinstance(rt.get("zbiornik"), dict) else None
        self.zbiornik = None
        if zb and zb.get("xy") is not None:
            self.zbiornik = dict(xy=np.asarray(zb["xy"], float), V=zb.get("V"), opis=str(zb.get("opis") or ""),
                                 poly=poly(zb.get("obrys")), sr=zb.get("sr"), raw=zb)
            if self.zbiornik["poly"] is None and not zb.get("sr"):
                self.brak("dzialka.yaml: retencja.zbiornik.{obrys|sr, rzedna_dna, rzedna_wlotu, rzedna_przelewu}",
                          "wymiary rzutu zbiornika retencyjnego i rzędne (dno, wlot, przelew) — rysunek pokazuje "
                          "symbol umowny w punkcie xy", "zbiornik: {xy: [x, y], V: 5.0, sr: 2.0, rzedna_dna: 99.0, "
                          "rzedna_wlotu: 100.6, rzedna_przelewu: 100.4}", "PZT-01, PZT-03")
        rz = rt.get("rozsaczanie") if isinstance(rt.get("rozsaczanie"), dict) else None
        self.rozsaczanie = dict(poly=poly(rz.get("obrys")), V=rz.get("V"), typ=str(rz.get("typ") or ""),
                                gl=rz.get("glebokosc"), opis=str(rz.get("opis") or ""), raw=rz) if rz else None
        self.odwodnienia = []
        for o in r.get("odwodnienia") or []:
            if isinstance(o, dict):
                self.odwodnienia.append(dict(id=str(o.get("id", "")), typ=str(o.get("typ") or ""),
                                             geom=line(o.get("linia")), poly=poly(o.get("obrys")),
                                             pts=o.get("obrys") or o.get("linia"), szer=o.get("szer"),
                                             spadek=o.get("spadek"), odb=str(o.get("odbiornik") or ""),
                                             opis=str(o.get("opis") or ""), raw=o))

    # ------------------------------------------------------------------ uzbrojenie
    def _load_utilities(self):
        u = self.raw.get("uzbrojenie") or {}
        self.sieci: list[Siec] = []
        for istn, key in ((True, "istniejace"), (False, "projektowane")):
            for i, s in enumerate(u.get(key) or []):
                if not isinstance(s, dict):
                    continue
                g = line(s.get("linia"))
                if g is None:
                    continue
                self.sieci.append(Siec(branza(s.get("branza")), g, str(s.get("opis") or ""), istn,
                                       s.get("dl"), str(s.get("id") or f"{'I' if istn else 'P'}{i + 1}")))
        self.obiekty = {}
        for o in u.get("obiekty") or []:
            if isinstance(o, dict) and o.get("xy") is not None:
                self.obiekty[str(o.get("id"))] = Obiekt(str(o.get("id")), np.asarray(o["xy"], float),
                                                       str(o.get("opis") or ""), o)
        kan = [s for s in (u.get("projektowane") or []) if isinstance(s, dict)
               and branza(s.get("branza")) in ("kan_sanit", "kan_deszcz")]
        if kan and not all(("rzedne" in s or "spadek" in s) and "dn" in s for s in kan):
            self.brak("dzialka.yaml: uzbrojenie.projektowane[].{dn, material, spadek, rzedne}",
                      "średnice, spadki i rzędne dna/wierzchu przewodów w punktach załamania i włączenia "
                      "(RPB § 15 ust. 2 pkt 11) — obecnie tylko w tekście 'opis'",
                      "{branza: kan_sanit, linia: [...], dn: 160, material: PVC-U, spadek: 0.02, "
                      "rzedne: [[x, y, H_dna], ...], przykrycie_min: 1.2}", "PZT-02, PZT-03")
        if not any(("studz" in o.opis.lower() or o.id.upper().startswith(("SD", "RD")))
                   and "deszcz" in o.opis.lower() for o in self.obiekty.values()):
            self.brak("dzialka.yaml: uzbrojenie.obiekty (studzienki deszczowe)",
                      "studzienki rewizyjne/połączeniowe na kolektorach deszczowych KD (włączenia rur spustowych, "
                      "załamania trasy, osadnik przed zbiornikiem) — brak obiektów w modelu",
                      "{id: SD1, xy: [x, y], opis: 'studzienka PP Ø315 z osadnikiem', rzedna_wlazu: 101.30, "
                      "rzedna_dna: 100.45}", "PZT-03")
        # rury spustowe (budynek.yaml: dachy[].rury_spustowe) i punkty instalacji w budynku
        self.rury = []
        for d in self.m.dachy():
            for rs in d.get("rury_spustowe") or []:
                if isinstance(rs, dict) and rs.get("xy_pion") is not None:
                    self.rury.append(dict(id=str(rs.get("id", "")), xy=self.P(rs["xy_pion"][:2]),
                                          trasa=str(rs.get("trasa") or ""), dn=rs.get("dn"),
                                          do=str(rs.get("do") or ""), dach=str(d.get("id", ""))))
        self.inst = {}
        try:
            import yaml
            from pathlib import Path
            src = Path(str(self.ctx.src or "model/budynek.yaml")).with_name("instalacje.yaml")
            if src.exists():
                lok = ((yaml.safe_load(src.read_text(encoding="utf-8")) or {}).get("instalacje") or {}) \
                    .get("lokalizacje") or {}
                for k, v in lok.items():
                    xy = v.get("xy") if isinstance(v, dict) else v
                    if isinstance(xy, (list, tuple)) and len(xy) >= 2 and all(isinstance(q, (int, float))
                                                                              for q in xy[:2]):
                        self.inst[k] = self.P([float(xy[0]), float(xy[1])])
        except Exception:  # noqa: BLE001 — dane pomocnicze (opcjonalne)
            pass
        # strefa R290 wokół jednostki zewnętrznej pompy ciepła
        self.pc = None
        pc = next((o for o in self.obiekty.values() if o.id.upper().startswith("PC")), None)
        if pc is not None:
            r290 = pc.raw.get("strefa_r")
            if r290 is None:
                r290 = num_in(pc.opis, r"strefa\s+R\s*290\s+(\d+[,.]?\d*)\s*m")
                self.brak("dzialka.yaml: uzbrojenie.obiekty[PC-JZ].{strefa_r, wym}",
                          "promień strefy bezpieczeństwa czynnika R290 (bez otworów, wpustów, studzienek) i wymiary "
                          "jednostki — obecnie odczytane z tekstu 'opis'" + ("" if r290 else f" — przyjęto 1,0 m {TODO}"),
                          "{id: PC-JZ, xy: [x, y], strefa_r: 1.0, wym: [1.20, 0.45], L_WA_noc: 55}", "PZT-01, PZT-03")
            fund = next((u_["poly"] for u_ in self.utwardzenia if u_["poly"].contains(Point(pc.xy))), None)
            body = fund if fund is not None else Point(pc.xy).buffer(0.5, cap_style=3)
            R = float(r290 or 1.0)
            self.pc = dict(obj=pc, body=body, r=R, strefa=body.buffer(R, join_style=1))
        # ograniczenia MPZP (model: dzialka.mpzp jako słownik; zapasowo — konfiguracja arkuszy)
        mp = self.dzialka.get("mpzp")
        cfg = dict(self.ctx.cfg.get("mpzp") or {})
        cfg.update(self.opts.get("mpzp") or {})
        self.mpzp_zrodlo = "model"
        if isinstance(mp, dict):
            lim = dict(cfg, **mp)
            self.mpzp_txt = str(mp.get("uchwala") or mp.get("opis") or "")
        else:
            lim = cfg
            self.mpzp_txt = str(mp or "")
            self.mpzp_zrodlo = "konfiguracja" if cfg else "brak"
            self.brak("dzialka.yaml: dzialka.mpzp (wskaźniki)",
                      "wskaźniki i parametry MPZP potrzebne do tabeli zgodności PZT (RPB § 14 pkt 4 lit. d) — "
                      "w modelu jest tylko tekst uchwały; wartości wzięto z konfiguracji arkuszy (brief § 3)",
                      "mpzp: {uchwala: '…', teren: 3MN, linia_zabudowy: 6.0, max_udzial_zabudowy: 0.30, "
                      "min_udzial_pbc: 0.50, intensywnosc: [0.05, 0.80], max_wysokosc: 11.0, max_kondygnacji: 3, "
                      "dach: 'płaski ≤ 12° lub 30–45°', min_miejsc_postojowych: 2, ogrodzenie_max_wys: 1.60}",
                      "PZT-01")
        self.mpzp = lim

    # ------------------------------------------------------------------ teren
    def _load_terrain(self):
        t = self.raw.get("teren") or {}
        self.warstwice_co = float(t.get("warstwice_co") or 0.10)
        self.zwg = t.get("ZWG")
        ex = np.asarray([p for p in (t.get("punkty") or []) if isinstance(p, (list, tuple)) and len(p) >= 3],
                        float).reshape(-1, 3)
        pr = np.asarray([p for p in (t.get("punkty_projektowane") or [])
                         if isinstance(p, (list, tuple)) and len(p) >= 3], float).reshape(-1, 3)
        self.pkt_ist = ex
        self.pkt_proj = pr
        if len(ex) < 3:
            self.brak("dzialka.yaml: teren.punkty", "brak rzędnych terenu istniejącego", "punkty: [[x, y, H], ...]")
        if len(pr) == 0:
            self.brak("dzialka.yaml: teren.punkty_projektowane", "brak rzędnych terenu projektowanego",
                      "punkty_projektowane: [[x, y, H], ...]", "PZT-02")
        self._h_ist = _tin(ex) if len(ex) >= 3 else None
        # teren projektowany: punkty projektowane + istniejące poza strefą zmian (≥ 2,5 m od punktów projektowanych
        # i poza obrysem budynku)
        if len(pr):
            zone = unary_union([Point(p[:2]).buffer(2.5) for p in pr] + [self.p0.buffer(0.3)])
            keep = ~shapely.contains_xy(zone, ex[:, 0], ex[:, 1]) if len(ex) else np.zeros(0, bool)
            both = np.vstack([pr, ex[keep]]) if len(ex) else pr
            self.strefa_zmian = unary_union([Point(p[:2]).buffer(1.5) for p in pr])
            self._h_proj = _tin(both) if len(both) >= 3 else self._h_ist
        else:
            self.strefa_zmian = Polygon()
            self._h_proj = self._h_ist

    def H_ist(self, xy):
        return None if self._h_ist is None else self._h_ist(np.asarray(xy, float).reshape(-1, 2))

    def H_proj(self, xy):
        return None if self._h_proj is None else self._h_proj(np.asarray(xy, float).reshape(-1, 2))

    def contours(self, bbox, step=None, projected=False, res=0.5):
        """Warstwice [(łamana Nx2, H)] w prostokącie bbox (x0, y0, x1, y1)."""
        import contourpy
        fn = self._h_proj if projected else self._h_ist
        if fn is None:
            return []
        step = step or self.warstwice_co
        x0, y0, x1, y1 = bbox
        xs = np.arange(x0, x1 + res, res)
        ys = np.arange(y0, y1 + res, res)
        X, Y = np.meshgrid(xs, ys)
        Z = fn(np.column_stack([X.ravel(), Y.ravel()])).reshape(X.shape)
        gen = contourpy.contour_generator(X, Y, Z)
        out = []
        lo = math.ceil(np.nanmin(Z) / step - 1e-9)
        hi = math.floor(np.nanmax(Z) / step + 1e-9)
        for i in range(lo, hi + 1):
            H = round(i * step, 3)
            for a in gen.lines(H):
                if len(a) >= 2:
                    out.append((np.asarray(a), H))
        return out

    def teren_przy_wejsciu(self):
        """Rzędna terenu projektowanego przed wejściem głównym (punkt projektowany ≤ 1,5 m od drzwi lub TIN)."""
        e = self.wejscie_gl
        if e is None:
            return None, None
        q = e["pt"] + e["out"] * 0.6
        if len(self.pkt_proj):
            d = np.hypot(self.pkt_proj[:, 0] - q[0], self.pkt_proj[:, 1] - q[1])
            i = int(np.argmin(d))
            if d[i] <= 1.5:
                return float(self.pkt_proj[i, 2]), "proj"
        h = self.H_proj(q)
        return (float(h[0]), "tin") if h is not None else (None, None)


def _tin(pts: np.ndarray):
    """Interpolacja liniowa TIN z ekstrapolacją płaszczyzną najmniejszych kwadratów poza otoczką."""
    from scipy.interpolate import LinearNDInterpolator
    pts = np.unique(np.round(pts, 4), axis=0)
    lin = LinearNDInterpolator(pts[:, :2], pts[:, 2])
    A = np.c_[pts[:, 0], pts[:, 1], np.ones(len(pts))]
    coef, *_ = np.linalg.lstsq(A, pts[:, 2], rcond=None)

    def f(xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        z = np.asarray(lin(xy), float).reshape(-1)
        bad = ~np.isfinite(z)
        if bad.any():
            z[bad] = coef[0] * xy[bad, 0] + coef[1] * xy[bad, 1] + coef[2]
        return z
    return f
