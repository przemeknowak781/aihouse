#!/usr/bin/env python3
"""audyt_wt.py — audyt zgodności modelu „Dom LAMELA” z WT i MPZP (audytor A1).

Wczytuje model (model/budynek.yaml + model/dzialka.yaml) oraz rejestr wartości wymagań
(docs/10_podstawy_prawne/wymagania.yaml) i LICZY niezależnie:
  * powierzchnie pomieszczeń (shapely — lica ścian wykończonych), strefy wysokości pod schodami, PU;
  * stosunek powierzchni okien do podłogi (w świetle muru i szacunkowo w świetle ościeżnic);
  * wysokości w świetle (płyta nad pomieszczeniem − sufit; belki/podciągi obniżające);
  * geometrię schodów (h, s, 2h+s, Σh, szerokości w świetle ścian, spoczniki, prześwit nad biegiem);
  * odległości każdego elementu budynku od granic działki (WT §12) i od linii zabudowy (MPZP);
  * wskaźniki MPZP: powierzchnia zabudowy, PBC, intensywność, wysokość (upzp art. 2 pkt 30) i wysokość wg WT §6;
  * wybrane wymagania WT (garaż, daszek, drzwi, podokienniki, czerpnia/wyrzutnia §152, parking §19, PC).
Model NIE jest modyfikowany. Wynik: raport Markdown (+ opcjonalnie JSON).

Użycie:
  python3 tools/audyt_wt.py                                  # raport → docs/20_koncepcja/audyt_A1.md
  python3 tools/audyt_wt.py --raport /tmp/a.md --json /tmp/a.json
  python3 tools/audyt_wt.py --budynek model/test/budynek.yaml --dzialka model/test/dzialka.yaml
Kod wyjścia: 0 — brak niezgodności, 1 — są niezgodności (NIEZGODNE), 2 — błąd wczytania modelu.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lamela.model import load_model, make_polygon, parse_przekroj  # noqa: E402

# ------------------------------------------------------------------------------------------------
# Założenia audytu (jawne — zmieniać tylko z uzasadnieniem)
# ------------------------------------------------------------------------------------------------
RAMA_OSCIEZNICY = 0.08       # [m] szac. szerokość widoczna ramy na stronę (światło ościeżnicy = światło muru − 2·0,08)
SUFIT_PODWIESZANY = 0.25     # [m] obniżenie sufitu podwieszanego (SUF_GK) poniżej spodu płyty — założenie audytu
ODL_OKAP_PROJEKT = 4.0       # [m] założenie projektowe (TWARDE ZAŁOŻENIA): wsporniki/okapy ≥ 4,0 m od granic
ODL_BEZ_OTWOROW_GARAZ = 3.0  # [m] ściana garażu bez otworów
KROK = 0.05                  # [m] siatka próbkowania (strefy wysokości, prześwity)
TYPY_SZKLONE = ("okno", "fix", "drzwi_przesuwne_HS")
TYPY_WEJSC = ("drzwi_zewn", "drzwi_przesuwne_HS", "brama")
STATUSY = ("NIEZGODNE", "UWAGA", "OK", "INFO")


# ------------------------------------------------------------------------------------------------
# Rejestr wymagań
# ------------------------------------------------------------------------------------------------
class Wymagania:
    """Płaski dostęp do docs/10_podstawy_prawne/wymagania.yaml (klucz → wpis); wartości domyślne gdy brak pliku."""

    def __init__(self, path: Path | None):
        self.w: dict[str, dict] = {}
        self.path = path
        if path and path.exists():
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            for grupa, d in raw.items():
                if not isinstance(d, dict):
                    continue
                for k, v in d.items():
                    if isinstance(v, dict) and "wartosc" in v:
                        self.w[k] = v

    def v(self, key: str, default):
        e = self.w.get(key)
        return e["wartosc"] if e else default

    def zr(self, key: str, fallback: str = "") -> str:
        e = self.w.get(key)
        if not e:
            return fallback
        wid = e.get("id")
        return f"{e.get('zrodlo', '')}" + (f" [{wid}]" if wid else "")


# ------------------------------------------------------------------------------------------------
# Wyniki
# ------------------------------------------------------------------------------------------------
@dataclass
class Wynik:
    sekcja: str
    element: str
    parametr: str
    wartosc: str
    wymog: str
    status: str
    podstawa: str = ""
    poprawka: str = ""
    miejsce: str = ""


@dataclass
class Audyt:
    wyniki: list[Wynik] = field(default_factory=list)
    tabele: dict[str, list] = field(default_factory=dict)
    info: dict = field(default_factory=dict)

    def add(self, *a, **k):
        w = Wynik(*a, **k)
        self.wyniki.append(w)
        return w


def f2(x, n=2):
    return "—" if x is None else (f"{x:.{n}f}".replace(".", ","))


def chk(ok: bool, soft: bool = False) -> str:
    return "OK" if ok else ("UWAGA" if soft else "NIEZGODNE")


# ------------------------------------------------------------------------------------------------
# Geometria pomocnicza
# ------------------------------------------------------------------------------------------------
def polys(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, MultiPolygon):
        return list(g.geoms)
    return [x for x in getattr(g, "geoms", []) if isinstance(x, Polygon)]


def slab_poly(item: dict):
    P = make_polygon(item["obrys"])
    for h in item.get("otwory") or []:
        P = P.difference(make_polygon(h))
    return P


class Uklad:
    """Transformacja budynek → działka."""

    def __init__(self, dz: dict):
        u = dz.get("uklad") or {}
        self.dx, self.dy = (u.get("przesuniecie") or [0.0, 0.0])
        self.rot = math.radians(float(u.get("obrot") or 0.0))

    def p(self, xy):
        x, y = float(xy[0]), float(xy[1])
        c, s = math.cos(self.rot), math.sin(self.rot)
        return (c * x - s * y + self.dx, s * x + c * y + self.dy)

    def g(self, geom):
        from shapely import affinity
        g = affinity.rotate(geom, math.degrees(self.rot), origin=(0, 0))
        return affinity.translate(g, self.dx, self.dy)


class Teren:
    """Rzędne terenu: istniejący (interpolacja liniowa TIN) i projektowany (najbliższy punkt ≤ 1,5 m, inaczej istniejący)."""

    def __init__(self, dz: dict):
        import matplotlib.tri as mtri
        t = dz.get("teren") or {}
        P = np.array(t.get("punkty") or [], float)
        self.ok = len(P) >= 3
        if self.ok:
            tri = mtri.Triangulation(P[:, 0], P[:, 1])
            self._f = mtri.LinearTriInterpolator(tri, P[:, 2])
        self.proj = np.array(t.get("punkty_projektowane") or [], float).reshape(-1, 3)

    def istn(self, x, y):
        if not self.ok:
            return None
        v = self._f(x, y)
        return None if np.ma.is_masked(v) else float(v)

    def proj_(self, x, y, r=1.5):
        if len(self.proj) == 0:
            return None
        d = np.hypot(self.proj[:, 0] - x, self.proj[:, 1] - y)
        i = int(np.argmin(d))
        return float(self.proj[i, 2]) if d[i] <= r else None

    def nizsza(self, x, y):
        a, b = self.istn(x, y), self.proj_(x, y)
        vals = [v for v in (a, b) if v is not None]
        return min(vals) if vals else None


# ------------------------------------------------------------------------------------------------
# Audyt
# ------------------------------------------------------------------------------------------------
class AudytWT:
    def __init__(self, bud: Path, dzp: Path, wym: Path | None):
        self.bud_path, self.dz_path = bud, dzp
        self.m = load_model(bud, dzp, strict=False)
        self.B = yaml.safe_load(bud.read_text(encoding="utf-8"))
        self.D = yaml.safe_load(dzp.read_text(encoding="utf-8"))
        self.R = Wymagania(wym)
        self.A = Audyt()
        self.U = Uklad(self.D)
        self.T = Teren(self.D)
        self.kond = {k.id: k for k in self.m.kondygnacje}
        self.op_by_wall: dict[str, list] = {}
        for o in self.m.otwory():
            self.op_by_wall.setdefault(o.sciana_id, []).append(o)
        self.plot = make_polygon(self.D["dzialka"]["obrys"])
        self._granice()
        self._plyty = self.plyty()

    # ------------------------------------------------------------------ granice działki
    def _granice(self):
        ring = list(self.plot.exterior.coords)[:-1]
        cx, cy = self.plot.centroid.x, self.plot.centroid.y
        road = None
        dr = self.D.get("droga") or {}
        if dr.get("linie_rozgraniczajace"):
            road = make_polygon(dr["linie_rozgraniczajace"])
        self.granice = []
        for i in range(len(ring)):
            a, b = np.array(ring[i]), np.array(ring[(i + 1) % len(ring)])
            v = b - a
            nrm = np.array([v[1], -v[0]]) / np.hypot(*v)
            mid = (a + b) / 2
            if (mid - [cx, cy]) @ nrm < 0:
                nrm = -nrm
            ang = math.degrees(math.atan2(nrm[1], nrm[0]))
            kier = {0: "E", 90: "N", 180: "W", -180: "W", -90: "S"}.get(int(round(ang / 90.0)) * 90, f"{ang:.0f}°")
            line = LineString([tuple(a), tuple(b)])
            drogowa = road is not None and line.intersection(road.buffer(0.05)).length > 0.5 * line.length
            self.granice.append({"kier": kier, "line": line, "n": nrm, "drogowa": drogowa})

    # ------------------------------------------------------------------ narzędzia
    def rz_podlogi(self, kid: str, podloga: str | None = None) -> float:
        k = self.kond[kid]
        if podloga and k.podloga and podloga != k.podloga:
            p, p0 = self.m.przegroda(podloga), self.m.przegroda(k.podloga)
            if p is not None and p0 is not None and p.ma_oznaczona_konstr and p0.ma_oznaczona_konstr:
                return k.rzedna + p.d_nad_konstr() - p0.d_nad_konstr()
        return k.rzedna

    def plyty(self):
        """Płyty poziome (stropy + dachy) jako (id, poly_z_otworami, spod, wierzch)."""
        out = []
        for st in self.m.stropy():
            out.append((st["id"], slab_poly(st), st["wierzch"] - st["grubosc"], st["wierzch"]))
        for d in self.m.dachy():
            pl = d["plyta"]
            out.append((d["id"], slab_poly(d), pl["wierzch"] - pl["grubosc"], pl["wierzch"]))
        return out

    def sufit_d(self, kod) -> float:
        if kod is None:
            return 0.01
        p = self.m.przegroda(str(kod))
        if p is not None:
            return p.grubosc
        if str(kod).startswith("SUF_GK"):
            return SUFIT_PODWIESZANY
        return 0.01

    # ------------------------------------------------------------------ schody (geometria)
    def biegi(self):
        """Lista biegów: dict(id, i, footprint, z0, n, h, s, d, szer, start, fn_soffit, fn_nosing)."""
        out = []
        for sch in self.m.schody():
            h, s = float(sch["wys_stopnia"]), float(sch["szer_stopnia"])
            t = float((sch.get("plyta") or {}).get("grubosc", 0.18))
            z = self.kond[str(sch["z_kond"])].rzedna
            cosa = s / math.hypot(h, s)
            for i, b in enumerate(sch["biegi"]):
                n = int(b["stopni"])
                d = np.array(b["kierunek"], float)
                d = d / np.hypot(*d)
                w = float(b["szer"])
                p0 = np.array(b["start"], float)
                L = (n - 1) * s
                nn = np.array([-d[1], d[0]])
                fp = Polygon([tuple(p0 - nn * w / 2), tuple(p0 + nn * w / 2), tuple(p0 + nn * w / 2 + d * L),
                              tuple(p0 - nn * w / 2 + d * L)])
                out.append(dict(id=f"{sch['id']}/bieg{i + 1}", sch=sch["id"], footprint=fp, z0=z, n=n, h=h, s=s, d=d,
                                nn=nn, szer=w, start=p0, L=L, t=t, cosa=cosa, z_kond=str(sch["z_kond"]),
                                na_kond=str(sch["na_kond"])))
                z += n * h
        return out

    def spoczniki(self):
        out = []
        for sch in self.m.schody():
            t = float((sch.get("plyta") or {}).get("grubosc", 0.18))
            for j, sp in enumerate(sch.get("spoczniki") or []):
                out.append(dict(id=f"{sch['id']}/spocznik{j + 1}", poly=make_polygon(sp["obrys"]),
                                z=float(sp["rzedna"]), t=t))
        return out

    @staticmethod
    def _u(b, x, y):
        return (np.array([x, y]) - b["start"]) @ b["d"]

    def soffit_z(self, b, x, y):
        u = self._u(b, x, y)
        return b["z0"] + u * b["h"] / b["s"] - b["t"] / b["cosa"]

    def nosing_z(self, b, x, y):
        u = self._u(b, x, y)
        return b["z0"] + b["h"] + u * b["h"] / b["s"]

    def nad_punktem(self, x, y, z_min, pomin=(), tylko_plyty=False):
        """Najniższy element konstrukcyjny nad punktem (x, y) powyżej z_min: (z_spodu, id)."""
        best = (math.inf, None)
        P = Point(x, y)
        for pid, poly, spod, _ in self._plyty:
            if spod > z_min + 1e-6 and poly.buffer(1e-6).contains(P):
                best = min(best, (spod, pid))
        if tylko_plyty:
            return best
        for b in self.biegi():
            if b["id"] in pomin:
                continue
            if b["footprint"].buffer(1e-6).contains(P):
                zs = self.soffit_z(b, x, y)
                if zs > z_min + 1e-6:
                    best = min(best, (zs, b["id"]))
        for sp in self.spoczniki():
            if sp["id"] in pomin:
                continue
            if sp["poly"].buffer(1e-6).contains(P):
                zs = sp["z"] - sp["t"]
                if zs > z_min + 1e-6:
                    best = min(best, (zs, sp["id"]))
        for be in self.m.belki():
            a, c = np.array(be["os"][0], float), np.array(be["os"][1], float)
            g = LineString([tuple(a), tuple(c)]).buffer(be["b"] / 2, cap_style=2)
            if be["spod"] > z_min + 1e-6 and g.contains(P):
                best = min(best, (float(be["spod"]), be["id"]))
        return best

    # ================================================================== 1. POMIESZCZENIA
    def pomieszczenia(self):
        R, A = self.R, self.A
        rows = []
        biegi = self.biegi()
        spocz = self.spoczniki()
        for r in self.m.pomieszczenia():
            poly = r.polygon_podlogi if r.polygon_podlogi is not None else r.polygon
            if poly is None or poly.is_empty:
                if r.polygon is not None and not r.polygon.is_empty:
                    A.add("Pomieszczenia", f"{r.id} {r.nazwa}", "podłoga", "cały rzut = otwór w stropie (pustka klatki)",
                          "—", "INFO", "PN-ISO 9836 / RPB §20 (klatka poza PU)")
                    continue
                A.add("Pomieszczenia", r.id, "geometria", "brak zamkniętego wieloboku", "wielobok zamknięty", "NIEZGODNE",
                      "SCHEMAT_MODELU §2", "uzupełnić ściany lub 'wielobok'")
                continue
            z_pod = self.rz_podlogi(r.kond, r.raw.get("podloga"))
            mnx, mny, mxx, mxy = poly.bounds
            probki = []
            for x in np.arange(mnx + 0.125, mxx, 0.25):
                for y in np.arange(mny + 0.125, mxy, 0.25):
                    if poly.contains(Point(x, y)):
                        zz, pid = self.nad_punktem(x, y, z_pod + 0.5, tylko_plyty=True)
                        if zz != math.inf:
                            probki.append((zz, pid))
            if not probki:
                rp = poly.representative_point()
                probki = [self.nad_punktem(rp.x, rp.y, z_pod + 0.5, tylko_plyty=True)]
            probki.sort()
            spod, sid = probki[len(probki) // 2]
            h_sw = None if spod == math.inf else spod - self.sufit_d(r.sufit) - z_pod
            # strefy wysokości (stopnie/spoczniki nad pomieszczeniem, belki)
            strefy = {"≥2,20": 0.0, "1,40–2,20": 0.0, "<1,40": 0.0}
            h_min = h_sw
            nad_schodami = any(poly.intersects(b["footprint"]) and b["z0"] >= z_pod - 0.01 and
                               b["z0"] + b["n"] * b["h"] > z_pod + 1.0 for b in biegi) or \
                any(poly.intersects(sp["poly"]) and sp["z"] > z_pod + 0.5 for sp in spocz)
            if "klatka" in r.nazwa.lower():
                nad_schodami = False
            h_max = h_sw
            if nad_schodami and h_sw is not None:
                minx, miny, maxx, maxy = poly.bounds
                xs = np.arange(minx + KROK / 2, maxx, KROK)
                ys = np.arange(miny + KROK / 2, maxy, KROK)
                a_cell = KROK * KROK
                for x in xs:
                    for y in ys:
                        if not poly.contains(Point(x, y)):
                            continue
                        # czy punkt leży na biegu wychodzącym z tej kondygnacji (to schody, nie przestrzeń pod nimi)
                        na_biegu = False
                        for b in biegi:
                            if b["footprint"].contains(Point(x, y)) and abs(b["z0"] - z_pod) < 0.2:
                                na_biegu = True
                        if na_biegu:
                            continue
                        zz, _ = self.nad_punktem(x, y, z_pod + 0.01)
                        hh = min(zz - z_pod, h_sw + self.sufit_d(r.sufit)) if zz != math.inf else h_sw
                        key = "≥2,20" if hh >= 2.20 - 1e-9 else ("1,40–2,20" if hh >= 1.40 - 1e-9 else "<1,40")
                        strefy[key] += a_cell
                        h_min = min(h_min, hh)
                        h_max = hh if h_max == h_sw else max(h_max, hh)
                pow_zal = strefy["≥2,20"] + 0.5 * strefy["1,40–2,20"]
                pow_net = sum(strefy.values())
            else:
                pow_net = poly.area
                pow_zal = pow_net if (h_sw or 0) >= 2.2 else (0.5 * pow_net if (h_sw or 0) >= 1.4 else 0.0)
            # belki obniżające
            h_belka, b_id = None, None
            walls_k = unary_union([w.polygon for w in self.m.sciany(r.kond)])
            for be in self.m.belki():
                a, c = np.array(be["os"][0], float), np.array(be["os"][1], float)
                g = LineString([tuple(a), tuple(c)]).buffer(be["b"] / 2, cap_style=2).difference(walls_k.buffer(0.02))
                if spod != math.inf and z_pod + 1.0 < be["spod"] < spod - 0.02 and g.intersection(poly).area > 0.05:
                    hb = be["spod"] - z_pod
                    if h_belka is None or hb < h_belka:
                        h_belka, b_id = hb, be["id"]
            row = dict(id=r.id, kond=r.kond, nazwa=r.nazwa, kat=r.kategoria, pobyt=r.pobyt_ludzi,
                       rodzaj=r.raw.get("rodzaj"), pow_model=round(r.pow_netto, 2), pow=round(pow_net, 2),
                       pow_zal=round(pow_zal, 2), h=None if h_sw is None else round(h_sw, 3),
                       h_min=None if h_min is None else round(h_min, 3), plyta=sid,
                       h_max=None if h_max is None else round(h_max, 3), strefy=strefy, schody=nad_schodami,
                       h_belka=h_belka, belka=b_id, poly=poly, poly_full=r.polygon, z_pod=z_pod)
            rows.append(row)
        self.rooms = {r["id"]: r for r in rows}

        # --- wymagania: powierzchnie i wysokości
        h_pok = R.v("wys_pokoj_min", 2.50)
        h_pom = 2.20  # brief §5: pomieszczenia pomocnicze ≥ 2,20 (WT §72 ust. 1 czasowy pobyt; §77 ust. 3)
        h_tech = R.v("wys_techniczne_gospodarcze_min", 2.00)
        for r in rows:
            nm = f"{r['id']} {r['nazwa']}"
            if r["h"] is None:
                A.add("Wysokości", nm, "h w świetle", "brak płyty nad", "—", "UWAGA", "", "sprawdzić model płyt")
                continue
            if r["pobyt"]:
                A.add("Wysokości", nm, "h w świetle", f2(r["h"]), f"≥ {f2(h_pok)} (cel 2,70–2,80)",
                      chk(r["h"] >= h_pok - 1e-6), R.zr("wys_pokoj_min", "WT §72 ust. 1"), "")
            elif r["kat"] == "techniczna" or r["rodzaj"] in ("garaz",):
                lim = R.v("wys_swiatlo_min", 2.20) if r["rodzaj"] == "garaz" else h_tech
                A.add("Wysokości", nm, "h w świetle", f2(r["h"]), f"≥ {f2(lim)}", chk(r["h"] >= lim - 1e-6),
                      "WT §102 pkt 1 [W-110]" if r["rodzaj"] == "garaz" else R.zr("wys_techniczne_gospodarcze_min"))
            elif r["kat"] != "ruchu" or r["rodzaj"] in ("lazienka", "wc"):
                ok = r["h"] >= h_pom - 1e-6
                if r["schody"]:
                    st = r["strefy"]
                    A.add("Wysokości", nm, "strefy h pod schodami",
                          f"≥2,20: {f2(st['≥2,20'])} m²; 1,40–2,20: {f2(st['1,40–2,20'])} m²; <1,40: {f2(st['<1,40'])} m²; "
                          f"h_min {f2(r['h_min'])}", f"pomocnicze ≥ {f2(h_pom)} (brief §5); gospodarcze ≥ {f2(h_tech)} (WT §97)",
                          "UWAGA" if (r["h_min"] or 0) < h_tech else "OK",
                          "brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316]",
                          "część o h < 2,00 m opisać jako schowek pod schodami (nie pomieszczenie); w PU liczyć strefami "
                          f"(100/50/0 %) — wg audytu {f2(r['pow_zal'])} m² zamiast {f2(0.5 * r['pow_model'])} m² z 'wys: 1,90'")
                else:
                    A.add("Wysokości", nm, "h w świetle", f2(r["h"]),
                          f"≥ {f2(h_pom)}" + (" (went. mech.)" if r["rodzaj"] in ("lazienka", "wc") else ""), chk(ok),
                          "WT §77 ust. 3 [W-052]" if r["rodzaj"] in ("lazienka", "wc") else "brief §5")
            if r["h_belka"] is not None:
                lim = h_pok if r["pobyt"] else 2.20
                A.add("Wysokości", nm, f"h pod belką {r['belka']}", f2(r["h_belka"]), f"≥ {f2(lim)} (lokalnie)",
                      chk(r["h_belka"] >= lim - 1e-6, soft=True), "WT §72 (lokalne obniżenie)")

        # --- powierzchnie minimalne (program)
        prog = {"pokoj": R.v("pokoj_pow_min_program", 8.0)}
        for r in rows:
            nm = f"{r['id']} {r['nazwa']}"
            if not r["pobyt"]:
                continue
            nzw = r["nazwa"].lower()
            if "dziecka" in nzw:
                lim, src = R.v("pokoj_dziecka_pow_min_program", 12.0), R.zr("pokoj_dziecka_pow_min_program", "brief §4")
            elif "sypialnia rodzic" in nzw:
                lim, src = 14.0, "brief §4 / założenie (sypialnia rodziców ≥ 14 m²)"
            elif "salon" in nzw:
                lim, src = 50.0, "brief §4 / założenie (salon+jadalnia+kuchnia ≥ 50 m²; pokój dzienny ≥ 16 m²)"
            else:
                lim, src = prog["pokoj"], R.zr("pokoj_pow_min_program", "brief §5")
            A.add("Powierzchnie", nm, "pow. netto", f"{f2(r['pow'])} m²", f"≥ {f2(lim, 1)} m²", chk(r["pow"] >= lim - 1e-6),
                  src)
            if abs(r["pow"] - r["pow_model"]) > 0.05 and not r["schody"]:
                A.add("Powierzchnie", nm, "zgodność z biblioteką", f"audyt {f2(r['pow'])} / lamela {f2(r['pow_model'])}",
                      "różnica ≤ 0,05 m²", "UWAGA", "kontrola wewnętrzna")

        # --- PU
        pu = {"podstawowa": 0.0, "pomocnicza_bez_garazu": 0.0, "garaz": 0.0, "ruchu_bez_klatek": 0.0, "klatki": 0.0,
              "techniczna": 0.0}
        for r in rows:
            if r["rodzaj"] == "garaz":
                pu["garaz"] += r["pow_zal"]
            elif r["kat"] == "podstawowa":
                pu["podstawowa"] += r["pow_zal"]
            elif r["kat"] == "pomocnicza":
                pu["pomocnicza_bez_garazu"] += r["pow_zal"]
            elif r["kat"] == "techniczna":
                pu["techniczna"] += r["pow_zal"]
            elif "klatka" in r["nazwa"].lower():
                pu["klatki"] += r["pow"]
            else:
                pu["ruchu_bez_klatek"] += r["pow_zal"]
        pu_mieszk = pu["podstawowa"] + pu["pomocnicza_bez_garazu"] + pu["ruchu_bez_klatek"]
        pu_iso = pu["podstawowa"] + pu["pomocnicza_bez_garazu"]
        lo, hi = R.v("PU_docelowa_program", [230.0, 270.0])
        A.info["PU"] = dict(pu, PU_mieszkalna=pu_mieszk, PU_ISO_podst_pomocn=pu_iso)
        A.add("Powierzchnie", "budynek", "PU mieszkalna (podst.+pomocn.+komunikacja, bez klatek, garażu, techn.)",
              f"{f2(pu_mieszk)} m²", f"{f2(lo, 0)}–{f2(hi, 0)} m²", chk(lo <= pu_mieszk <= hi, soft=True),
              R.zr("PU_docelowa_program", "brief §4") + "; RPB §20 / PN-ISO 9836 [W-316]")
        # otwarta strefa dzienna
        dz = [r for r in rows if r["pobyt"] and "salon" in r["nazwa"].lower()]
        if dz:
            A.add("Powierzchnie", dz[0]["id"], "strefa dzienna otwarta (salon+jadalnia+kuchnia)", f"{f2(dz[0]['pow'])} m²",
                  "≥ 50,0 m²", chk(dz[0]["pow"] >= 50.0), "brief §4 (TWARDE ZAŁOŻENIA)")
        self.A.tabele["pomieszczenia"] = rows

    # ================================================================== 2. OKNA
    def okna(self):
        R, A = self.R, self.A
        lim = R.v("okno_do_podlogi_pobyt_ludzi_min", 0.125)
        per_room: dict[str, list] = {}
        for o in self.m.otwory():
            w = o.sciana
            if o.typ not in TYPY_SZKLONE or w is None or w.ext_side is None:
                continue
            nin = -np.array(o.kierunek_zewn)
            c = o.srodek + nin * (abs(w.face_t(-w.ext_side)) + 0.10)
            hit = None
            for r in self.rooms.values():
                if r["kond"] == o.kond and r["poly_full"].buffer(0.02).contains(Point(*c)):
                    hit = r["id"]
                    break
            a_mur = o.szer * o.wys
            a_osc = max(o.szer - 2 * RAMA_OSCIEZNICY, 0) * max(o.wys - 2 * RAMA_OSCIEZNICY, 0)
            per_room.setdefault(hit or "?", []).append((o.id, o.symbol, a_mur, a_osc))
        rows = []
        for rid, r in self.rooms.items():
            ops = per_room.get(rid, [])
            a_m = sum(x[2] for x in ops)
            a_o = sum(x[3] for x in ops)
            ratio_m = a_m / r["pow"] if r["pow"] else 0
            ratio_o = a_o / r["pow"] if r["pow"] else 0
            rows.append(dict(id=rid, nazwa=r["nazwa"], pobyt=r["pobyt"], pow=r["pow"], okna=", ".join(x[0] for x in ops),
                             a_mur=a_m, a_osc=a_o, k_mur=ratio_m, k_osc=ratio_o))
            if r["pobyt"]:
                A.add("Oświetlenie", f"{rid} {r['nazwa']}", "A_okien/A_podłogi (w świetle ościeżnic, szac.)",
                      f"{f2(ratio_o, 3)} (mur: {f2(ratio_m, 3)}; {', '.join(x[0] for x in ops) or 'brak okien'})",
                      f"≥ {f2(lim, 3)}", chk(ratio_o >= lim), R.zr("okno_do_podlogi_pobyt_ludzi_min", "WT §57 ust. 2"),
                      "" if ratio_o >= lim else f"powiększyć okna do ≥ {f2(lim * r['pow'] + 0.0)} m² w świetle ościeżnic")
            if r["rodzaj"] == "kuchnia" and not ops:
                A.add("Oświetlenie", f"{rid} {r['nazwa']}", "kuchnia z oknem", "brak okna", "okno", "NIEZGODNE",
                      "brief §5 / WT §57", "dodać okno")
        if "?" in per_room:
            A.add("Oświetlenie", "otwory", "przypisanie do pomieszczeń", ", ".join(x[0] for x in per_room["?"]),
                  "każde okno w pomieszczeniu", "UWAGA", "kontrola wewnętrzna")
        self.A.tabele["okna"] = rows

    # ================================================================== 3. SCHODY
    def schody(self):
        R, A = self.R, self.A
        biegi, spocz = self.biegi(), self.spoczniki()
        rows = []
        for sch in self.m.schody():
            h, s = float(sch["wys_stopnia"]), float(sch["szer_stopnia"])
            n = int(sch["liczba_stopni"])
            dz = self.kond[str(sch["na_kond"])].rzedna - self.kond[str(sch["z_kond"])].rzedna
            A.add("Schody", sch["id"], "wysokość stopnia h", f2(h, 3), f"≤ {f2(R.v('h_max', 0.19), 3)} (projekt ≈ 0,175)",
                  chk(h <= R.v("h_max", 0.19) + 1e-9), R.zr("h_max", "WT §68 ust. 1"))
            v = 2 * h + s
            lo, hi = R.v("dwa_h_plus_s", [0.60, 0.65])
            A.add("Schody", sch["id"], "2h+s", f2(v, 3), f"{f2(lo)}–{f2(hi)}", chk(lo - 1e-9 <= v <= hi + 1e-9),
                  R.zr("dwa_h_plus_s", "WT §69 ust. 4"))
            A.add("Schody", sch["id"], "Σ podnóżków × h = Δ kondygnacji", f"{n} × {f2(h, 3)} = {f2(n * h, 3)} vs {f2(dz, 3)}",
                  "równe", chk(abs(n * h - dz) < 0.005), "geometria")
            nb = sum(int(b["stopni"]) for b in sch["biegi"])
            if nb != n:
                A.add("Schody", sch["id"], "Σ stopni w biegach", str(nb), f"= {n}", "NIEZGODNE", "spójność modelu")
        # szerokości biegów w świetle ścian
        for b in biegi:
            kid = b["z_kond"]
            walls = unary_union([w.polygon for w in self.m.sciany(kid)])
            mid = b["start"] + b["d"] * b["L"] / 2
            wid = []
            for sgn in (1, -1):
                ray = LineString([tuple(mid), tuple(mid + sgn * b["nn"] * 3.0)])
                inter = ray.intersection(walls)
                dist = Point(*mid).distance(inter) if not inter.is_empty else math.inf
                wid.append(dist)
            clear = sum(wid)
            lim = R.v("bieg_szer_projekt", 1.00)
            A.add("Schody", b["id"], "szerokość biegu w świetle ścian", f2(clear, 3) + f" (model: {f2(b['szer'], 3)})",
                  f"≥ {f2(lim)} (WT ≥ {f2(R.v('bieg_szer_min', 0.80))})", chk(clear >= lim - 1e-6),
                  R.zr("bieg_szer_projekt", "brief §5") + "; " + R.zr("bieg_szer_min", "WT §68"),
                  "" if clear >= lim else "poszerzyć klatkę")
            # prześwit nad biegiem (od linii krawędzi stopni, pionowo)
            h_min, el = math.inf, None
            for uu in np.arange(0.0, b["L"] + 1e-9, KROK):
                for vv in np.linspace(-b["szer"] / 2 + 0.05, b["szer"] / 2 - 0.05, 5):
                    p = b["start"] + b["d"] * uu + b["nn"] * vv
                    zn = self.nosing_z(b, *p)
                    zz, eid = self.nad_punktem(p[0], p[1], zn, pomin=(b["id"],))
                    if zz - zn < h_min:
                        h_min, el = zz - zn, eid
            # pierwszy stopień: także przed biegiem (0,3 m) — belki nad wejściem
            lim = R.v("przeswit_nad_biegiem_min", 2.00)
            A.add("Schody", b["id"], "prześwit nad biegiem (min.)", f"{f2(h_min, 3)} (element: {el})", f"≥ {f2(lim)}",
                  chk(h_min >= lim - 1e-6), R.zr("przeswit_nad_biegiem_min", "R3 K-22 (dobra praktyka)"))
            rows.append(dict(id=b["id"], z0=b["z0"], n=b["n"], szer=b["szer"], clear=clear, L=b["L"], przeswit=h_min, el=el))
        for sp in spocz:
            sch_b = [b for b in biegi if b["sch"] == sp["id"].split("/")[0]]
            w_max = max(b["szer"] for b in sch_b)
            d = sch_b[0]["d"]
            mnx, mny, mxx, mxy = sp["poly"].bounds
            glab = (mxy - mny) if abs(d[1]) > abs(d[0]) else (mxx - mnx)
            A.add("Schody", sp["id"], "głębokość spocznika", f2(glab, 3), f"≥ szer. biegu {f2(w_max, 3)}",
                  chk(glab >= w_max - 1e-6), R.zr("spocznik_szer_min", "WT §68 ust. 1") + "; brief §5")
            zz, eid = math.inf, "świetlik/otwarta przestrzeń"
            mnx, mny, mxx, mxy = sp["poly"].bounds
            for x in np.arange(mnx + 0.05, mxx, 0.10):
                for y in np.arange(mny + 0.05, mxy, 0.10):
                    z1, e1 = self.nad_punktem(x, y, sp["z"] + 0.01)
                    if z1 < zz:
                        zz, eid = z1, e1
            A.add("Schody", sp["id"], "prześwit nad spocznikiem (min.)", f"{f2(zz - sp['z'], 3)} ({eid})", "≥ 2,00",
                  chk(zz - sp["z"] >= 2.0), "R3 K-22")
            # spójność: koniec biegu = krawędź spocznika
            for b in sch_b:
                zend = b["z0"] + b["n"] * b["h"]
                if abs(zend - sp["z"]) < 0.01:
                    pend = b["start"] + b["d"] * b["L"]
                    dd = sp["poly"].exterior.distance(Point(*pend))
                    if dd > 0.02:
                        A.add("Schody", b["id"], "koniec biegu przy krawędzi spocznika", f"odchyłka {f2(dd, 3)} m",
                              "≤ 0,02", "UWAGA", "spójność geometrii")
        # balustrady / pochwyty
        for bl in self.m.balustrady():
            lim = R.v("balustrada_wys_min", 0.90)
            A.add("Schody", bl["id"], "wysokość balustrady/pochwytu", f2(bl["wys"]), f"≥ {f2(lim)}", chk(bl["wys"] >= lim - 1e-6),
                  R.zr("balustrada_wys_min", "WT §298"))
        self.A.tabele["schody"] = rows

    # ================================================================== 4. ODLEGŁOŚCI
    def _dist(self, geom_bud):
        g = self.U.g(geom_bud)
        return {gr["kier"]: g.distance(gr["line"]) for gr in self.granice}, g

    def odleglosci(self):
        R, A = self.R, self.A
        l_otw, l_bez = R.v("odl_granica_z_otworami", 4.0), R.v("odl_granica_bez_otworow", 3.0)
        l_okap = R.v("odl_granica_okap_gzyms_balkon_schody", 1.5)
        rows = []
        # ściany zewnętrzne (każda płaszczyzna uskoku osobno — W-001)
        for w in self.m.sciany():
            if w.typ != "sciana_zewn" or w.ext_side is None:
                continue
            face = w.band(t0=w.face_t(w.ext_side) - 0.001 * w.ext_side, t1=w.face_t(w.ext_side)) \
                if w.ext_side > 0 else w.band(t0=w.face_t(w.ext_side), t1=w.face_t(w.ext_side) + 0.001)
            nz = w.ext_side * w.n
            ds, g = self._dist(face)
            otw = [o for o in self.op_by_wall.get(w.id, []) if o.typ != "otwor"]
            for gr in self.granice:
                if gr["drogowa"]:
                    continue
                if float(np.dot(nz, gr["n"])) > 0.7:
                    d = ds[gr["kier"]]
                    garaz = w.kond == "P0" and not otw
                    lim = l_otw if otw else (ODL_BEZ_OTWOROW_GARAZ if garaz else l_bez)
                    rows.append(dict(el=w.id, rodzaj=f"ściana zewn. {w.kond} ({'z otworami' if otw else 'bez otworów'})",
                                     kier=gr["kier"], d=d, lim=lim))
                    A.add("Odległości", w.id, f"lico zewn. → granica {gr['kier']}", f"{f2(d)} m",
                          f"≥ {f2(lim)} ({'okna/drzwi' if otw else 'bez otworów'})", chk(d >= lim - 1e-6),
                          R.zr("odl_granica_z_otworami" if otw else "odl_granica_bez_otworow", "WT §12 ust. 1"),
                          "" if d >= lim else f"przesunąć/cofnąć lico o ≥ {f2(lim - d)} m", miejsce=f"{w.raw['os']}")
        # elementy wysunięte i pozostałe
        elems = []
        for x in self.m.wsporniki():
            elems.append((x["id"], "płyta wysunięta/okap/daszek", make_polygon(x["obrys"])))
        for x in self.m.dachy():
            att = (x.get("attyka") or {}).get("szer", 0.0)
            elems.append((x["id"], "dach z attyką", make_polygon(x["obrys"])))
        for x in self.m.tarasy():
            elems.append((x["id"], "taras naziemny/podest", make_polygon(x["obrys"])))
        for lm in self.m.lamele():
            a, b = np.array(lm["linia"][0], float), np.array(lm["linia"][1], float)
            nrm = {"S": (0, -1), "N": (0, 1), "E": (1, 0), "W": (-1, 0)}.get(lm["elewacja"], (0, 0))
            off = lm["odsuniecie"] + lm["h"]
            if lm["z_od"] > 0.5 or lm["elewacja"] in ("E", "W"):
                line = LineString([tuple(a), tuple(b)])
                g = line.buffer(0.001).union(LineString([tuple(a + np.array(nrm) * off), tuple(b + np.array(nrm) * off)]).buffer(0.001))
                elems.append((lm["id"], "lamele (osłona elewacji)", g.convex_hull))
        for sl in self.m.slupy():
            a, b = parse_przekroj(str(sl["przekroj"]))
            x, y = sl["xy"]
            elems.append((sl["id"], "słup", box(x - a / 2, y - b / 2, x + a / 2, y + b / 2)))
        for d in self.m.dachy():
            for rs in d.get("rury_spustowe") or []:
                if rs.get("trasa") == "zewn":
                    elems.append((rs["id"], "rura spustowa zewn.", Point(*rs["xy_pion"]).buffer(0.06)))
            for pa in d.get("przelewy_awaryjne") or []:
                elems.append((f"{d['id']}/przelew@{pa['xy']}", "przelew awaryjny (rzygacz ~0,15 m)", Point(*pa["xy"]).buffer(0.15)))
        for eid, rodz, g in elems:
            ds, gp = self._dist(g)
            for gr in self.granice:
                if gr["drogowa"]:
                    continue
                d = ds[gr["kier"]]
                if d > 12.0:
                    continue
                lim_proj = l_okap if rodz.startswith("taras") else ODL_OKAP_PROJEKT
                st = "OK" if d >= lim_proj - 1e-6 else ("UWAGA" if d >= l_okap else "NIEZGODNE")
                rows.append(dict(el=eid, rodzaj=rodz, kier=gr["kier"], d=d, lim=lim_proj))
                A.add("Odległości", eid, f"{rodz} → granica {gr['kier']}", f"{f2(d)} m",
                      f"≥ {f2(lim_proj)} (założenie proj.); WT ≥ {f2(l_okap)}", st,
                      R.zr("odl_granica_okap_gzyms_balkon_schody", "WT §12 ust. 6") + "; TWARDE ZAŁOŻENIA",
                      "" if st == "OK" else f"skrócić wysięg o ≥ {f2(lim_proj - d)} m")
        # linia zabudowy
        lz = self.D.get("linia_zabudowy")
        if lz:
            L = LineString([tuple(p) for p in lz])
            road = make_polygon(self.D["droga"]["linie_rozgraniczajace"]) if (self.D.get("droga") or {}).get(
                "linie_rozgraniczajace") else None
            # strona zakazana = strona drogi
            a, b = np.array(lz[0], float), np.array(lz[-1], float)
            nrm = np.array([-(b - a)[1], (b - a)[0]])
            nrm /= np.hypot(*nrm)
            if road is not None and (np.array(road.centroid.coords[0]) - a) @ nrm < 0:
                nrm = -nrm
            wszystkie = [(w.id, w.polygon) for w in self.m.sciany()] + [(e[0], e[2]) for e in elems]
            worst = (-math.inf, None)
            for eid, g in wszystkie:
                gp = self.U.g(g)
                for p in polys(gp.buffer(0)) or [gp.buffer(0.001)]:
                    for q in p.exterior.coords:
                        dd = (np.array(q) - a) @ nrm
                        worst = max(worst, (dd, eid))
            A.add("MPZP", "linia zabudowy", "najdalej wysunięty element (+ = przekroczenie)", f"{f2(worst[0])} m ({worst[1]})",
                  "≤ 0,00", chk(worst[0] <= 1e-6), R.zr("linia_zabudowy_od_linii_rozgraniczajacej", "MPZP 3MN"),
                  "" if worst[0] <= 0 else f"cofnąć {worst[1]} o ≥ {f2(worst[0])} m")
            self.A.info["linia_zabudowy_rezerwa"] = -worst[0]
        self.A.tabele["odleglosci"] = rows

    # ================================================================== 5. WSKAŹNIKI MPZP
    def mpzp(self):
        R, A, m = self.R, self.A, self.m
        plot_area = self.plot.area
        outl = {k: m.obrys_kondygnacji(k) for k in self.kond}
        zab = unary_union([g for g in outl.values() if not g.is_empty])
        ext = [make_polygon(w["obrys"]) for w in m.wsporniki() if w.get("wierzch", 0) < 9.5 and w["id"].startswith("PL")]
        ext += [make_polygon(d["obrys"]) for d in m.dachy()]
        zab_pl = unary_union([zab] + ext)
        lim = R.v("pow_zabudowy_max", 0.30 * plot_area)
        A.add("MPZP", "pow. zabudowy (1) obrys ścian zewn. wszystkich kondygnacji", "A_z", f"{f2(zab.area)} m² ({f2(100 * zab.area / plot_area, 1)} %)",
              f"≤ {f2(lim)} m²", chk(zab.area <= lim), R.zr("pow_zabudowy_max", "MPZP"))
        A.add("MPZP", "pow. zabudowy (2) kontrolnie z płytami wysuniętymi", "A_z+", f"{f2(zab_pl.area)} m² ({f2(100 * zab_pl.area / plot_area, 1)} %)",
              f"≤ {f2(lim)} m²", chk(zab_pl.area <= lim), "rejestr D-06")
        # intensywność (nadziemna)
        suma = sum(g.area for g in outl.values())
        lo, hi = R.v("intensywnosc_zakres", [0.05, 0.80])
        A.add("MPZP", "intensywność zabudowy", "Σ pow. kondygnacji nadziemnych / pow. działki",
              f"{f2(suma)} / {f2(plot_area)} = {f2(suma / plot_area, 3)}", f"{f2(lo)}–{f2(hi)}", chk(lo <= suma / plot_area <= hi),
              R.zr("intensywnosc_zakres", "MPZP"))
        self.A.info["pow_kondygnacji"] = {k: round(g.area, 2) for k, g in outl.items()}
        # PBC
        dz = self.D
        uszcz = [self.U.g(outl[min(self.kond, key=lambda k: self.kond[k].rzedna)])]
        opis = []
        for t in m.tarasy():
            uszcz.append(self.U.g(make_polygon(t["obrys"])))
        for u in dz.get("utwardzenia") or []:
            uszcz.append(make_polygon(u["obrys"]))
        if (dz.get("odpady") or {}).get("obrys"):
            uszcz.append(make_polygon(dz["odpady"]["obrys"]))
        for od in dz.get("odwodnienia") or []:
            if od.get("typ") == "opaska_zwirowa" and od.get("obrys"):
                uszcz.append(make_polygon(od["obrys"]))  # obrys zewnętrzny opaski (budynek w środku i tak wyłączony)
                opis.append("opaska żwirowa wyłączona z PBC (ostrożnie)")
        zb = (dz.get("retencja") or {}).get("zbiornik")
        if zb and zb.get("xy"):
            V = float(zb.get("V", 5.0))
            a = max(2.0, V / 1.6)  # ~ rzut zbiornika + 0,3 m obrzeża; założenie audytu
            uszcz.append(Point(*zb["xy"]).buffer(math.sqrt(a / math.pi)))
            opis.append(f"teren nad zbiornikiem ≈ {f2(a, 1)} m² wyłączony (W-031)")
        U = unary_union(uszcz).intersection(self.plot)
        pbc = self.plot.area - U.area
        dach_ziel = sum(make_polygon(d["obrys"]).area for d in m.dachy()
                        if "ziel" in str(d.get("uwagi", "")).lower() or d.get("przegroda") == "DZ1")
        lim = R.v("PBC_min", 0.5 * plot_area)
        A.add("MPZP", "pow. biologicznie czynna (teren)", "PBC", f"{f2(pbc)} m² ({f2(100 * pbc / plot_area, 1)} %)",
              f"≥ {f2(lim)} m²", chk(pbc >= lim), R.zr("PBC_min", "MPZP") + "; " + "; ".join(opis))
        A.info["PBC"] = dict(teren=pbc, uszczelnione=U.area, dach_zielony_50=0.5 * dach_ziel)
        # miejsca postojowe
        mp = dz.get("miejsca_postojowe") or []
        lim = R.v("miejsca_postojowe_na_lokal_min", 2)
        A.add("MPZP", "miejsca postojowe", "liczba (garaż + zewn.)",
              f"{len(mp)} ({sum(1 for x in mp if x['typ'] == 'garaz')} w garażu)", f"≥ {lim}", chk(len(mp) >= lim),
              R.zr("miejsca_postojowe_na_lokal_min", "MPZP"))
        # kondygnacje
        n = len(self.kond)
        A.add("MPZP", "kondygnacje nadziemne", "liczba", str(n), f"≤ {R.v('kondygnacje_nadziemne_max', 3)}",
              chk(n <= R.v("kondygnacje_nadziemne_max", 3)), R.zr("kondygnacje_nadziemne_max", "MPZP"))
        # dachy — spadek
        for d in m.dachy():
            sp = float(d.get("spadek") or 0) * 100
            A.add("MPZP", d["id"], "spadek dachu", f"{f2(sp, 1)} % ({f2(math.degrees(math.atan(sp / 100)), 1)}°)",
                  f"≤ {R.v('dach_plaski_spadek_max', 12)}°", chk(math.degrees(math.atan(sp / 100)) <= R.v("dach_plaski_spadek_max", 12)),
                  R.zr("dach_plaski_spadek_max", "MPZP"))
        # ogrodzenie od drogi
        for og in dz.get("ogrodzenie") or []:
            L = LineString([tuple(p) for p in og["linia"]])
            road_side = any(gr["drogowa"] and L.distance(gr["line"]) < 0.05 and L.length > 0 and
                            L.intersection(gr["line"].buffer(0.05)).length > 0.5 * L.length for gr in self.granice)
            if road_side:
                lim = R.v("ogrodzenie_od_drogi_wys_max", 1.6)
                A.add("MPZP", f"ogrodzenie {og['linia'][0]}→{og['linia'][-1]}", "wysokość (od drogi)", f2(og["wys"]),
                      f"≤ {f2(lim)}; ażurowe", chk(og["wys"] <= lim + 1e-9 and "ażur" in str(og.get("typ", ""))),
                      R.zr("ogrodzenie_od_drogi_wys_max", "MPZP"))
        for br in dz.get("bramy") or []:
            lim = R.v("brama_wjazdowa_szer_min", 2.4) if br["typ"] != "furtka" else R.v("furtka_szer_min", 0.9)
            A.add("Zagospodarowanie", f"{br['typ']} @ {br['xy']}", "szerokość w świetle", f2(br["szer"]), f"≥ {f2(lim)}",
                  chk(br["szer"] >= lim), R.zr("brama_wjazdowa_szer_min" if br["typ"] != "furtka" else "furtka_szer_min", "WT §43"))

    # ================================================================== 6. WYSOKOŚĆ
    def _pokrycie(self, d: dict):
        """(z_min, z_śr, z_max) wierzchu pokrycia dachu z uwzględnieniem klina izolacji spadkowej."""
        p = self.m.przegroda(str(d.get("przegroda")))
        w = d["plyta"]["wierzch"]
        if p is None or not p.ma_oznaczona_konstr:
            return (w, w, w)
        nad = p.d_nad_konstr()
        raw = (self.B.get("przegrody") or {}).get(str(d.get("przegroda")), {})
        dmin = dmax = None
        for war in raw.get("warstwy") or []:
            if isinstance(war, dict) and war.get("klin"):
                dmin, dmax, dd = war["klin"]["d_min"], war["klin"]["d_max"], war["d"]
        if dmin is None:
            return (w + nad, w + nad, w + nad)
        return (w + nad - dd + dmin, w + nad, w + nad - dd + dmax)

    def pokrycie_lokalne(self, d: dict, x, y):
        zmin, _, zmax = self._pokrycie(d)
        wp = [np.array(v["xy"], float) for v in d.get("wpusty") or []]
        if not wp:
            return zmin
        dist = min(np.hypot(*(np.array([x, y]) - p)) for p in wp)
        return min(zmin + float(d.get("spadek") or 0.02) * dist, zmax)

    def wysokosc(self):
        R, A, m = self.R, self.A, self.m
        z0 = m.zero_abs
        # --- obwód ścian parteru (teren przy licu)
        p0 = m.obrys_kondygnacji(min(self.kond, key=lambda k: self.kond[k].rzedna))
        ring = LineString(p0.exterior.coords)
        vals_i, vals_p = [], []
        for s in np.arange(0, ring.length, 0.25):
            q = ring.interpolate(s)
            # punkt 0,3 m na zewnątrz lica
            q2 = ring.interpolate(min(s + 0.01, ring.length))
            t = np.array([q2.x - q.x, q2.y - q.y])
            if np.hypot(*t) == 0:
                continue
            t /= np.hypot(*t)
            nrm = np.array([t[1], -t[0]])
            pt = np.array([q.x, q.y]) + nrm * 0.30
            if p0.contains(Point(*pt)):
                pt = np.array([q.x, q.y]) - nrm * 0.30
            X, Y = self.U.p(pt)
            a, b = self.T.istn(X, Y), self.T.proj_(X, Y, r=2.0)
            if a is not None:
                vals_i.append(a)
            if b is not None:
                vals_p.append(b)
        t_i = (min(vals_i), max(vals_i)) if vals_i else (None, None)
        t_p = (min(vals_p), max(vals_p)) if vals_p else (None, None)
        lows = [v for v in (t_i[0], t_p[0]) if v is not None]
        highs = [v for v in (t_i[1], t_p[1]) if v is not None]
        t_min = min(lows)
        t_sr = (min(lows) + min(highs)) / 2
        # --- najwyższe punkty
        top = []
        for d in m.dachy():
            zmin, zsr, zmax = self._pokrycie(d)
            att = d.get("attyka") or {}
            top.append((zsr + float(att.get("wys_nad_pokryciem", 0)), f"attyka {d['id']}"))
            top.append((zmax, f"pokrycie {d['id']} (max, klin)"))
        for w in m.wsporniki():
            top.append((float(w["wierzch"]), w["id"]))
        for lm in m.lamele():
            top.append((float(lm["z_do"]), lm["id"]))
        went = ((self.B.get("energia") or {}).get("wentylacja") or {})
        for k in ("czerpnia", "wyrzutnia"):
            if went.get(k) and len(went[k]) >= 3:
                top.append((float(went[k][2]), k))
        z_top, el_top = max(top)
        H_upzp_min = z0 + z_top - t_min
        H_upzp_sr = z0 + z_top - t_sr
        lim, rez = R.v("wys_zabudowy_max", 11.0), R.v("wys_zabudowy_rezerwa", 0.30)
        A.add("MPZP", "wysokość zabudowy (upzp art. 2 pkt 30)", f"od najniższego terenu {f2(t_min)} do {el_top} (+{f2(z_top, 3)})",
              f"{f2(H_upzp_min)} m (od średniej {f2(t_sr)}: {f2(H_upzp_sr)} m)", f"≤ {f2(lim)} (z rezerwą ≤ {f2(lim - rez)})",
              "OK" if H_upzp_min <= lim - rez else ("UWAGA" if H_upzp_min <= lim else "NIEZGODNE"),
              R.zr("wys_zabudowy_max", "MPZP") + "; rejestr D-15")
        # --- WT §6: teren przy najniżej położonym wejściu → najwyższy punkt stropodachu nad pomieszczeniami
        wejscia = []
        for o in m.otwory():
            if o.typ not in TYPY_WEJSC or o.kierunek_zewn is None:
                continue
            c = o.srodek + np.array(o.kierunek_zewn) * (abs(o.sciana.face_t(o.sciana.ext_side)) + 0.6)
            X, Y = self.U.p(c)
            wejscia.append((self.T.nizsza(X, Y), o.id))
        t_we, o_we = min(w for w in wejscia if w[0] is not None)
        z_str = []
        for d in m.dachy():
            zmin, zsr, zmax = self._pokrycie(d)
            z_str.append((zmax, d["id"]))
        z_s, d_s = max(z_str)
        H_wt = z0 + z_s - t_we
        A.add("WT", "wysokość budynku wg WT §6", f"teren przy wejściu {o_we}: {f2(t_we)} → wierzch {d_s} z izol. (+{f2(z_s, 3)})",
              f"{f2(H_wt)} m", f"≤ {f2(R.v('wys_budynku_grupa_N_max', 12.0))} (N); ≤ {f2(lim)} (MPZP)",
              chk(H_wt <= min(lim, R.v("wys_budynku_grupa_N_max", 12.0))), R.zr("wys_budynku_grupa_N_max", "WT §6, §8") + "; [W-063]")
        A.info["wysokosc"] = dict(teren_istn=t_i, teren_proj=t_p, t_min=t_min, t_sr=t_sr, z_top=z_top, el_top=el_top,
                                  H_upzp=H_upzp_min, H_upzp_sr=H_upzp_sr, H_WT=H_wt, wejscie=o_we, t_wejscia=t_we,
                                  wejscia=wejscia)

    # ================================================================== 7. INNE WYMAGANIA WT / PZT
    def inne(self):
        R, A, m, D = self.R, self.A, self.m, self.D
        # --- garaż
        gar = [r for r in self.rooms.values() if r["rodzaj"] == "garaz"]
        if gar:
            g = gar[0]
            mnx, mny, mxx, mxy = g["poly"].bounds
            # wymiary w świetle — największy prostokąt osiowy w wieloboku (przybliżenie: bounds po odcięciu wnęk < 0,5 m)
            core = g["poly"].buffer(-0.3, join_style=2).buffer(0.3, join_style=2)
            bx = core.bounds
            szer, gl = bx[2] - bx[0], bx[3] - bx[1]
            A.add("Garaż", g["id"], "wymiary w świetle", f"{f2(szer)} × {f2(gl)} m",
                  f"≥ {f2(R.v('szer_swiatlo_min', 5.6))} × {f2(R.v('gl_swiatlo_min', 6.0))}",
                  chk(szer >= R.v("szer_swiatlo_min", 5.6) - 1e-6 and gl >= R.v("gl_swiatlo_min", 6.0) - 1e-6),
                  R.zr("szer_swiatlo_min", "WT §104") + "; brief §4")
            for o in m.otwory():
                if o.typ == "brama":
                    ok = o.szer >= R.v("brama_szer_min", 2.3) and o.wys >= R.v("brama_wys_min", 2.0)
                    A.add("Garaż", o.id, "brama w świetle", f"{f2(o.szer)} × {f2(o.wys)}", "≥ 2,30 × 2,00", chk(ok),
                          R.zr("brama_szer_min", "WT §102 pkt 2"))
            # stanowiska w garażu (z PZT)
            walls = unary_union([w.polygon for w in m.sciany("P0")])
            for mp in D.get("miejsca_postojowe") or []:
                P = make_polygon(mp["obrys"])
                from shapely import affinity
                Pb = affinity.translate(P, -self.U.dx, -self.U.dy)
                b = Pb.bounds
                w_, l_ = sorted((b[2] - b[0], b[3] - b[1]))
                A.add("Garaż" if mp["typ"] == "garaz" else "Zagospodarowanie", mp.get("id", "MP"), "stanowisko",
                      f"{f2(w_)} × {f2(l_)} m", f"≥ {f2(R.v('stanowisko_szer', 2.5))} × {f2(R.v('stanowisko_dl', 5.0))}",
                      chk(w_ >= R.v("stanowisko_szer", 2.5) - 1e-6 and l_ >= R.v("stanowisko_dl", 5.0) - 1e-6),
                      R.zr("stanowisko_szer", "WT §21"))
                if mp["typ"] == "garaz":
                    # dłuższe krawędzie
                    if (b[2] - b[0]) < (b[3] - b[1]):
                        edges = [LineString([(b[0], b[1]), (b[0], b[3])]), LineString([(b[2], b[1]), (b[2], b[3])])]
                    else:
                        edges = [LineString([(b[0], b[1]), (b[2], b[1])]), LineString([(b[0], b[3]), (b[2], b[3])])]
                    edges = [LineString([e.interpolate(0.5), e.interpolate(e.length - 0.5)]) for e in edges]
                    dmin = min(e.distance(walls) for e in edges)
                    lim = R.v("odl_stanowisko_sciana_min", 0.30)
                    A.add("Garaż", mp.get("id", "MP"), "dłuższa krawędź stanowiska → lico ściany", f"{f2(dmin)} m",
                          f"≥ {f2(lim)}", chk(dmin >= lim - 1e-6), R.zr("odl_stanowisko_sciana_min", "WT §104 ust. 1 pkt 1"),
                          "" if dmin >= lim else "rozmieścić stanowiska: 0,30 + 2,50 + (odstęp) + 2,50 + 0,30 w świetle "
                          f"{f2(szer)} m (np. x = {f2(bx[0] + 0.30)}…{f2(bx[0] + 2.80)} i {f2(bx[2] - 2.80)}…{f2(bx[2] - 0.30)} w ukł. budynku)",
                          miejsce=f"PZT {mp['obrys'][0]}…{mp['obrys'][2]}")
                else:
                    ds = {gr["kier"]: P.distance(gr["line"]) for gr in self.granice if not gr["drogowa"]}
                    dmin = min(ds.values())
                    lim = R.v("parking_odl_granica_min", 3.0)
                    A.add("Zagospodarowanie", mp.get("id", "MP"), "odl. od granic bocznych/tylnej", f"{f2(dmin)} m",
                          f"≥ {f2(lim)} (granica z drogą — bez wymogu)", chk(dmin >= lim), R.zr("parking_odl_granica_min", "WT §19"))
            # posadzka garażu / próg przy drzwiach do domu
            txt = str(g.get("rodzaj")) + " " + str(next((r.raw.get("uwagi", "") for r in m.pomieszczenia() if r.id == g["id"]), ""))
            msp = re.search(r"spadek\s*([\d,\.]+)\s*%", txt)
            br = [o for o in m.otwory() if o.typ == "brama"]
            dg = [o for o in m.otwory() if o.sciana is not None and o.sciana.przegroda_kod == "SWG" and o.typ == "drzwi"]
            if msp and br and dg:
                sp = float(msp.group(1).replace(",", ".")) / 100
                zb = br[0].parapet
                dist = abs((np.array(dg[0].srodek) - np.array(br[0].srodek)) @ (-np.array(br[0].kierunek_zewn))) - 0.4
                z_dg = zb + sp * dist
                prog = 0.0 - z_dg
                lim = R.v("prog_posadzki", 30) / 1000
                A.add("Garaż", f"{dg[0].id} (drzwi garaż–dom)", "różnica posadzek dom − garaż przy drzwiach",
                      f"{f2(prog, 3)} m (posadzka przy bramie {f2(zb, 2)}, spadek {f2(sp * 100, 1)} % na {f2(dist)} m)",
                      f"≥ {f2(lim, 3)} (próg)", chk(prog >= lim - 1e-6, soft=True), R.zr("prog_posadzki", "WT §107 ust. 2"),
                      "" if prog >= lim else f"obniżyć płytę/posadzkę garażu o ≥ {f2(lim - prog + 0.02, 2)} m (posadzka przy bramie ≤ "
                      f"{f2(zb - (lim - prog + 0.02), 2)}, przy drzwiach ≤ −0,05) i teren/odwodnienie liniowe przed bramą ≥ 0,02 m niżej niż próg bramy",
                      miejsce=f"S0-17 / {dg[0].id}")
        # --- drzwi wejściowe i daszek (W-055, W-057)
        for o in m.otwory():
            if o.typ == "drzwi_zewn" and o.sciana.kond == "P0" and o.symbol and "wej" in str(o.raw.get("uwagi", "")).lower():
                sw = o.szer - 2 * 0.07
                A.add("WT", o.id, "drzwi wejściowe (światło ościeżnicy, szac.)", f"{f2(sw)} × {f2(o.wys - 0.07)}",
                      "≥ 0,90 × 2,00", chk(sw >= 0.9 and o.wys - 0.07 >= 2.0), R.zr("drzwi_wejsciowe_szer_min", "WT §62"))
                nz = np.array(o.kierunek_zewn)
                best = None
                for w in m.wsporniki():
                    P = make_polygon(w["obrys"])
                    face = o.srodek + nz * abs(o.sciana.face_t(o.sciana.ext_side))
                    if P.distance(Point(*(face + nz * 0.3))) < 0.01:
                        pts = np.array(P.exterior.coords)
                        wys = float(max((pts - face) @ nz))
                        tang = np.array([-nz[1], nz[0]])
                        sz = float(np.ptp(pts @ tang))
                        best = (w["id"], wys, sz)
                if best:
                    ok = best[1] >= 1.0 - 1e-6 and best[2] >= o.szer + 1.0 - 1e-6
                    A.add("WT", best[0], "daszek nad wejściem: wysięg / szerokość", f"{f2(best[1])} / {f2(best[2])} m",
                          f"≥ 1,00 / ≥ {f2(o.szer + 1.0)}", chk(ok), R.zr("daszek_wejscie_wysieg_min", "WT §292"))
                else:
                    A.add("WT", o.id, "daszek nad wejściem", "brak", "wymagany (> 2 kondygnacje)", "NIEZGODNE", "WT §292 [W-057]")
        # --- podokienniki P1/P2 (W-097) i otwieranie P2 (W-098)
        stol = self.B.get("stolarka") or {}
        for o in m.otwory():
            if o.typ not in ("okno", "fix", "drzwi_przesuwne_HS") or o.sciana.kond == "P0":
                continue
            opis = str((stol.get(o.symbol) or {}).get("opis", "")) + " " + str(o.raw.get("uwagi", ""))
            if o.parapet < R.v("podokiennik_min", 0.85) - 1e-6:
                zab = bool(re.search(r"stał\w*\s+VSG|VSG\s+do\s+0,85|dolna część stała", opis))
                A.add("WT", o.id, "podokiennik", f"{f2(o.parapet)} m" + (" + dolna część stała VSG" if zab else ""),
                      "≥ 0,85 albo zabezpieczenie", chk(zab), R.zr("podokiennik_min", "WT §301"),
                      "" if zab else "dolna szyba stała VSG do 0,85 m lub balustrada ≥ 0,90 m")
            if o.sciana.kond == "P2":
                kier = (o.raw.get("otwieranie") or {}).get("kierunek")
                A.add("WT", o.id, "otwieranie okna P2", str(kier), "do wewnątrz", chk(kier in (None, "do_wewn")),
                      R.zr("okno_wychylenie_na_zewn_max", "WT §299"))
        # --- wyłaz dachowy (W-065)
        for w in m.wsporniki():
            if "wyłaz" in str(w.get("uwagi", "")).lower() or w["id"].startswith("WYL"):
                mm = re.search(r"([\d,]+)\s*×\s*([\d,]+)\s*m\s*w\s*świetle", str(w.get("uwagi", "")))
                if mm:
                    a, b = (float(x.replace(",", ".")) for x in mm.groups())
                    A.add("WT", w["id"], "wyłaz dachowy w świetle", f"{f2(a)} × {f2(b)}", "≥ 0,80 × 0,80",
                          chk(min(a, b) >= 0.8), R.zr("klapa_dach_wymiar_min", "WT §308 ust. 3"))
        # --- czerpnia / wyrzutnia (WT §152)
        self._wentylacja()
        # --- pompa ciepła, pojemniki, retencja
        self._pc_i_pzt()
        # --- sąsiedzi (ppoż. §271, przesłanianie §13)
        hb = self.A.info.get("wysokosc", {}).get("H_upzp", 11.0)
        bud = self.U.g(unary_union([m.obrys_kondygnacji(k) for k in self.kond]))
        for s in D.get("sasiedzi") or []:
            zb = s.get("zabudowa")
            if not zb:
                continue
            d = bud.distance(make_polygon(zb))
            A.add("Sąsiedztwo", f"dz. {s['nr']}", "odl. budynek–budynek sąsiedni", f"{f2(d)} m",
                  f"≥ {f2(R.v('odl_ppoz_ZL_ZL', 8.0))} (ppoż.); ≥ H = {f2(hb)} (przesłanianie, uproszcz.)",
                  chk(d >= R.v("odl_ppoz_ZL_ZL", 8.0) and d >= hb), R.zr("odl_ppoz_ZL_ZL", "WT §271") + "; WT §13, §60")

    def _wentylacja(self):
        R, A, m = self.R, self.A, self.m
        went = ((self.B.get("energia") or {}).get("wentylacja") or {})
        cz, wy = went.get("czerpnia"), went.get("wyrzutnia")
        if not cz or not wy:
            return
        D1 = next((d for d in m.dachy() if make_polygon(d["obrys"]).contains(Point(*cz[:2]))), None)
        if D1 is None:
            return
        wyw = [(p[0], p[1]) for p in (went.get("wywiewki_kanalizacyjne") or [])]
        z_cz_roof = self.pokrycie_lokalne(D1, *cz[:2])
        z_wy_roof = self.pokrycie_lokalne(D1, *wy[:2])
        A.add("Wentylacja", "czerpnia dachowa", "wysokość nad pokryciem (lokalnie, klin)",
              f"{f2(cz[2] - z_cz_roof, 3)} m (pokrycie ≈ +{f2(z_cz_roof, 3)})", "≥ 0,40",
              chk(cz[2] - z_cz_roof >= 0.4 - 1e-6, soft=True), R.zr("czerpnia_dachowa_nad_powierzchnia_min", "WT §152 ust. 4"),
              "" if cz[2] - z_cz_roof >= 0.4 else f"dolna krawędź otworu czerpni ≥ +{f2(z_cz_roof + 0.40, 2)}",
              miejsce=f"{cz}")
        A.add("Wentylacja", "wyrzutnia dachowa", "wysokość nad pokryciem (lokalnie, klin)",
              f"{f2(wy[2] - z_wy_roof, 3)} m", "≥ 0,40", chk(wy[2] - z_wy_roof >= 0.4 - 1e-6, soft=True),
              R.zr("wyrzutnia_dachowa_nad_powierzchnia_min", "WT §152 ust. 7"), miejsce=f"{wy}")
        for p in wyw:
            d = math.hypot(cz[0] - p[0], cz[1] - p[1])
            A.add("Wentylacja", "czerpnia ↔ wywiewka kanalizacyjna", "odległość", f"{f2(d)} m", "≥ 6,00",
                  chk(d >= R.v("czerpnia_dachowa_odl_wywiewki_min", 6.0)), R.zr("czerpnia_dachowa_odl_wywiewki_min", "WT §152 ust. 4"))
        d = math.hypot(cz[0] - wy[0], cz[1] - wy[1])
        dz = wy[2] - cz[2]
        l10 = R.v("czerpnia_wyrzutnia_dach_wyrzut_poziomy_min", 10.0)
        l6 = R.v("czerpnia_wyrzutnia_dach_wyrzut_pionowy_min", 6.0)
        dzl = R.v("wyrzutnia_ponad_czerpnia_min", 1.0)
        ok = d >= l10 - 1e-6 or (d >= l6 and dz >= dzl - 1e-6) or bool(went.get("zestaw_zblokowany"))
        # propozycja położeń: wyrzutnia ≥ 3 m od krawędzi dachu nad oknami, czerpnia ≥ 6 m od wywiewek, odl. ≥ 10 m
        prop = self._propozycja_went(D1, cz, wy, wyw) if not ok else None
        A.add("Wentylacja", "czerpnia ↔ wyrzutnia (dach)", "odległość / wyrzutnia wyżej o",
              f"{f2(d)} m / {f2(dz, 2)} m", f"≥ {f2(l10)} m, albo ≥ {f2(l6)} m przy wyrzutni ≥ {f2(dzl)} m wyżej (lub zestaw zblokowany)",
              chk(ok), R.zr("czerpnia_wyrzutnia_dach_wyrzut_poziomy_min", "WT §152 ust. 10") + "; R6-43",
              "" if ok else (f"rozsunąć na ≥ {f2(l10)} m, np. czerpnia ({f2(prop[0][0])}; {f2(prop[0][1])}), wyrzutnia "
                             f"({f2(prop[1][0])}; {f2(prop[1][1])}) → {f2(prop[2])} m (wyrzutnia {f2(prop[3])} m od krawędzi dachu nad oknami; "
                             f"czerpnia {f2(prop[4])} m od wywiewki); rzędne wylotów ≥ pokrycie lokalne + 0,40; "
                             "alternatywnie podnieść wyrzutnię ≥ 1,0 m ponad czerpnię (sprawdzić wys. zabudowy) albo zestaw zblokowany"
                             if prop else "rozsunąć na ≥ 10 m lub podnieść wyrzutnię ≥ 1,0 m ponad czerpnię"),
              miejsce=f"energia.wentylacja: czerpnia {cz}, wyrzutnia {wy}")
        # wyrzutnia od krawędzi dachu nad oknami
        ed = self._krawedzie_nad_oknami(D1)
        if ed:
            dmin = min(e.distance(Point(*wy[:2])) for e in ed)
            A.add("Wentylacja", "wyrzutnia ↔ krawędź dachu nad oknami", "odległość", f"{f2(dmin)} m", "≥ 3,00",
                  chk(dmin >= R.v("wyrzutnia_odl_krawedz_dachu_z_oknami_min", 3.0) - 1e-6),
                  R.zr("wyrzutnia_odl_krawedz_dachu_z_oknami_min", "WT §152 ust. 12"))

    def _krawedzie_nad_oknami(self, D):
        P = make_polygon(D["obrys"])
        ring = list(P.exterior.coords)
        z_pl = D["plyta"]["wierzch"]
        out = []
        for i in range(len(ring) - 1):
            e = LineString([ring[i], ring[i + 1]])
            for o in self.m.otwory():
                if o.sciana is None or o.sciana.ext_side is None or o.typ not in TYPY_SZKLONE + ("okno",):
                    continue
                if o.z1 > z_pl or o.z1 < z_pl - 3.3:
                    continue
                c0 = np.array(o.p0) + np.array(o.kierunek_zewn) * abs(o.sciana.face_t(o.sciana.ext_side))
                c1 = np.array(o.p1) + np.array(o.kierunek_zewn) * abs(o.sciana.face_t(o.sciana.ext_side))
                seg = LineString([tuple(c0), tuple(c1)])
                ev = np.array(e.coords[1]) - np.array(e.coords[0])
                evn = ev / np.hypot(*ev)
                par = abs(evn[0] * o.sciana.u[1] - evn[1] * o.sciana.u[0]) < 0.05
                if par and e.distance(seg) < 0.7 and e.buffer(0.7).intersection(seg).length > 0.1:
                    out.append(e)
                    break
        return out

    def _propozycja_went(self, D, cz, wy, wyw):
        P = make_polygon(D["obrys"])
        att = float((D.get("attyka") or {}).get("szer", 0.25))
        inner = P.buffer(-(att + 0.30), join_style=2)
        ed = self._krawedzie_nad_oknami(D)
        xs = np.arange(P.bounds[0], P.bounds[2], 0.1)
        ys = np.arange(P.bounds[1], P.bounds[3], 0.1)
        cand_w, cand_c = [], []
        for x in xs:
            for y in ys:
                q = Point(x, y)
                if not inner.contains(q):
                    continue
                if all(e.distance(q) >= 3.0 for e in ed):
                    cand_w.append((x, y))
                if all(math.hypot(x - p[0], y - p[1]) >= 6.0 for p in wyw):
                    cand_c.append((x, y))
        best = None
        cw = np.array(cand_w)
        cc = np.array(cand_c)
        if len(cw) == 0 or len(cc) == 0:
            return None
        for c in cc[:: max(1, len(cc) // 1500)]:
            d = np.hypot(cw[:, 0] - c[0], cw[:, 1] - c[1])
            ok = d >= 10.05
            if not ok.any():
                continue
            mv = np.hypot(cw[:, 0] - wy[0], cw[:, 1] - wy[1]) + math.hypot(c[0] - cz[0], c[1] - cz[1])
            mv = np.where(ok, mv, np.inf)
            i = int(np.argmin(mv))
            if best is None or mv[i] < best[0]:
                best = (mv[i], tuple(c), tuple(cw[i]), float(d[i]))
        if best is None:
            return None
        c, w = best[1], best[2]
        return (c, w, best[3], min(e.distance(Point(*w)) for e in ed) if ed else math.inf,
                min((math.hypot(c[0] - p[0], c[1] - p[1]) for p in wyw), default=math.inf))

    def _pc_i_pzt(self):
        R, A, D = self.R, self.A, self.D
        obj = {o["id"]: o for o in ((D.get("uzbrojenie") or {}).get("obiekty") or [])}
        pc = obj.get("PC-JZ")
        if pc:
            x, y = pc["xy"]
            ds = {gr["kier"]: Point(x, y).distance(gr["line"]) for gr in self.granice}
            A.add("Zagospodarowanie", "PC-JZ (jedn. zewn. PC)", "odl. od granic", ", ".join(f"{k} {f2(v)}" for k, v in ds.items()),
                  "≥ 3,0 (założenie); E ≥ 6,0", chk(min(ds.values()) >= 3.0 and ds.get("E", 99) >= R.v("pc_odl_granica_E_min", 6.0)),
                  R.zr("pc_odl_granica_E_min", "R8 3.4"))
            # strona elewacji
            bud = self.U.g(unary_union([self.m.obrys_kondygnacji(k) for k in self.kond]))
            c = bud.centroid
            mnx, mny, mxx, mxy = bud.bounds
            strona = "S" if y < mny else ("N" if y > mxy else ("W" if x < mnx else ("E" if x > mxx else "?")))
            A.add("Zagospodarowanie", "PC-JZ (jedn. zewn. PC)", "elewacja, przy której stoi jednostka",
                  f"{strona} (x {f2(x)}, y {f2(y)} w ukł. działki; {f2(mny - y if strona == 'S' else 0)} m od lica)",
                  "N lub E (TWARDE ZAŁOŻENIA)", "OK" if strona in ("N", "E") else "UWAGA",
                  "TWARDE ZAŁOŻENIA (energia i światło); W-024 (hałas)",
                  "" if strona in ("N", "E") else
                  "wariant E: przy ścianie wsch. pom. techn. 0.12 / garażu (jednostka gł. ≈ 0,6 m, 0,3 m od lica ⇒ x_dz ≈ 26,6–27,2, "
                  "≈ 4,8 m od granicy E: ≥ 3,0 wg założeń, lecz < 6,0 wg W-024 — wymaga obliczenia hałasu L_Aeq,N ≤ 40 dB); "
                  "elewacja N zajęta przez podjazd i wejście. Jeśli jednostka zostaje od S — wpisać do koncepcji uzasadnienie "
                  "odstępstwa (W-024: ≥ 6,0 m od granicy E; krótkie przewody do 0.12), ekran akustyczny od tarasu T1/T3 "
                  "i obliczenie hałasu na tarasie i granicy E")
            # strefa R290 1,0 m — otwory w ścianach
            U5 = next((make_polygon(u["obrys"]) for u in D.get("utwardzenia") or [] if "PC" in str(u.get("nawierzchnia", ""))), None)
            if U5 is not None:
                z = U5.buffer(R.v("pc_R290_strefa_bezp", 1.0))
                kol = []
                for o in self.m.otwory():
                    if o.sciana.kond != "P0" or o.kierunek_zewn is None:
                        continue
                    seg = self.U.g(LineString([tuple(o.p0), tuple(o.p1)]))
                    if seg.distance(z) < 0.35:
                        kol.append(o.id)
                for od in D.get("odwodnienia") or []:
                    if od.get("typ") in ("opaska_zwirowa", "drenaz_opaskowy"):
                        continue
                    geo = od.get("linia") or od.get("obrys")
                    if geo and len(geo) >= 2:
                        g = LineString([tuple(p) for p in geo]) if od.get("linia") else make_polygon(geo).exterior
                        if g.distance(U5) < R.v("pc_R290_strefa_bezp", 1.0):
                            kol.append(od["id"])
                for oid, o in obj.items():
                    if oid != "PC-JZ" and Point(*o["xy"]).distance(U5) < R.v("pc_R290_strefa_bezp", 1.0):
                        kol.append(oid)
                A.add("Zagospodarowanie", "PC-JZ strefa R290", "otwory/wpusty/studzienki w strefie 1,0 m", ", ".join(kol) or "brak",
                      "brak", chk(not kol, soft=True), R.zr("pc_R290_strefa_bezp", "PN-EN 378-1; DTR"))
        ret = D.get("retencja") or {}
        for k in ("zbiornik", "rozsaczanie"):
            v = ret.get(k)
            if not v:
                continue
            g = Point(*v["xy"]).buffer(1.0) if "xy" in v else make_polygon(v["obrys"])
            ds = {gr["kier"]: g.distance(gr["line"]) for gr in self.granice}
            bud = self.U.g(self.m.obrys_kondygnacji("P0"))
            db = g.distance(bud)
            A.add("Zagospodarowanie", f"retencja/{k}", "odl. od granic / od budynku",
                  f"min {f2(min(ds.values()))} / {f2(db)} m", "≥ 2,0 / ≥ 3,0", chk(min(ds.values()) >= 2.0 and db >= 3.0, soft=True),
                  R.zr("rozsaczanie_odl_granica_min", "R8 3.5") + " [W-144, W-145]")
        od = D.get("odpady") or {}
        if od.get("obrys"):
            g = make_polygon(od["obrys"])
            ds = {gr["kier"]: g.distance(gr["line"]) for gr in self.granice}
            A.add("Zagospodarowanie", "miejsce na pojemniki", "odl. od granic", ", ".join(f"{k} {f2(v)}" for k, v in ds.items()),
                  "zabudowa jednorodzinna — odległości nieustalone (WT §23 ust. 4)", "INFO", "WT §22, §23 ust. 4 [W-016]")

    # ================================================================== uruchomienie
    def run(self):
        self.pomieszczenia()
        self.okna()
        self.schody()
        self.odleglosci()
        self.mpzp()
        self.wysokosc()
        self.inne()
        kub = self.m.kubatura_brutto()["razem"]
        self.A.add("WT", "kubatura brutto (lamela, PN-ISO 9836)", "V", f"{f2(kub, 1)} m³", "> 1000 m³ ⇒ PWP (W-190); uprawnienia bez ogr.",
                   "INFO", "WT §3 pkt 24; PB art. 15a [W-069]")
        return self.A


# ------------------------------------------------------------------------------------------------
# Raport Markdown
# ------------------------------------------------------------------------------------------------
def raport_md(a: AudytWT, A: Audyt, extra: str = "") -> str:
    ts = _dt.date.today().isoformat()
    L = []
    L.append("# Audyt A1 — zgodność koncepcji ostatecznej z WT i MPZP (obliczenia z modelu)\n")
    L.append(f"Wygenerowano: {ts} skryptem `tools/audyt_wt.py` (uruchomienie: `python3 tools/audyt_wt.py`). "
             f"Model: `{a.bud_path.relative_to(ROOT) if a.bud_path.is_relative_to(ROOT) else a.bud_path}` "
             f"(wersja {a.B.get('meta', {}).get('wersja', '?')}, stadium: {a.B.get('meta', {}).get('stadium', '?')}), "
             f"`{a.dz_path.relative_to(ROOT) if a.dz_path.is_relative_to(ROOT) else a.dz_path}`; wartości progowe z "
             f"`docs/10_podstawy_prawne/wymagania.yaml` ({len(a.R.w)} wpisów). Model nie był modyfikowany.\n")
    cnt = {s: sum(1 for w in A.wyniki if w.status == s) for s in STATUSY}
    L.append(f"**Wynik kontroli automatycznych:** {cnt['NIEZGODNE']} × NIEZGODNE, {cnt['UWAGA']} × UWAGA, {cnt['OK']} × OK, "
             f"{cnt['INFO']} × INFO.\n")
    if extra:
        L.append(extra)
    # zestawienie problemów
    L.append("\n## 1. Niezgodności i uwagi (z kontroli automatycznych)\n")
    L.append("| # | Status | Sekcja | Element / miejsce | Parametr | Wartość | Wymóg | Podstawa | Proponowana poprawka |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    i = 0
    for s in ("NIEZGODNE", "UWAGA"):
        for w in A.wyniki:
            if w.status != s:
                continue
            i += 1
            el = w.element + (f" — {w.miejsce}" if w.miejsce else "")
            L.append(f"| {i} | **{w.status}** | {w.sekcja} | {el} | {w.parametr} | {w.wartosc} | {w.wymog} | {w.podstawa} | "
                     f"{w.poprawka or '—'} |")
    if i == 0:
        L.append("| — | — | — | — | — | — | — | — | — |")
    # wskaźniki
    inf = A.info
    L.append("\n## 2. Wskaźniki MPZP i wysokość\n")
    L.append("| Wskaźnik | Wartość | Wymóg | Status |")
    L.append("|---|---|---|---|")
    for w in A.wyniki:
        if w.sekcja == "MPZP" or (w.sekcja == "WT" and "wysokość" in w.element):
            L.append(f"| {w.element} — {w.parametr} | {w.wartosc} | {w.wymog} | {w.status} |")
    pk = inf.get("pow_kondygnacji", {})
    L.append(f"\nPowierzchnie kondygnacji (obrys zewnętrzny): " + ", ".join(f"{k} {f2(v)} m²" for k, v in pk.items()) + ".")
    pb = inf.get("PBC", {})
    if pb:
        L.append(f"PBC: teren {f2(pb['teren'])} m²; powierzchnie wyłączone {f2(pb['uszczelnione'])} m²; rezerwa — dach zielony "
                 f"(50 %) {f2(pb['dach_zielony_50'])} m² (nie wliczona).")
    wy = inf.get("wysokosc", {})
    if wy:
        L.append(f"Teren przy obwodzie parteru: istniejący {f2(wy['teren_istn'][0])}…{f2(wy['teren_istn'][1])}, projektowany "
                 f"{f2(wy['teren_proj'][0])}…{f2(wy['teren_proj'][1])} m n.p.m.; ±0,00 = {f2(a.m.zero_abs)} m n.p.m. "
                 f"Wejścia (teren niższy z istn./proj.): " + ", ".join(f"{o} {f2(t)}" for t, o in wy["wejscia"] if t is not None) + ".")
    # pomieszczenia
    L.append("\n## 3. Pomieszczenia — powierzchnie, wysokości, oświetlenie\n")
    L.append("| Nr | Nazwa | Kat. | Pobyt | Pow. netto [m²] | Pow. do PU [m²] | h w świetle [m] | h min / pod belką | Okna | A_ok/A_p (ościeżn.) |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    ok_by = {r["id"]: r for r in A.tabele.get("okna", [])}
    for r in A.tabele.get("pomieszczenia", []):
        o = ok_by.get(r["id"], {})
        hb = (f"{f2(r['h_min'])}" if r["schody"] else "") + (f" / {f2(r['h_belka'])} ({r['belka']})" if r["h_belka"] else "")
        hs = f"zmienna {f2(r['h_min'])}…{f2(r['h_max'])}" if r["schody"] else ("otwarta (pustka)" if "klatka" in r["nazwa"].lower() else f2(r["h"]))
        L.append(f"| {r['id']} | {r['nazwa']} | {r['kat']} | {'tak' if r['pobyt'] else '—'} | {f2(r['pow'])} | {f2(r['pow_zal'])} | "
                 f"{hs} | {hb or '—'} | {o.get('okna') or '—'} | {f2(o.get('k_osc'), 3) if o.get('okna') else '—'} |")
    pu = inf.get("PU", {})
    if pu:
        L.append(f"\nPU mieszkalna (podstawowa {f2(pu['podstawowa'])} + pomocnicza bez garażu {f2(pu['pomocnicza_bez_garazu'])} + "
                 f"komunikacja bez klatek {f2(pu['ruchu_bez_klatek'])}) = **{f2(pu['PU_mieszkalna'])} m²**; PU wg PN-ISO 9836 "
                 f"(podstawowa + pomocnicza, bez garażu) = {f2(pu['PU_ISO_podst_pomocn'])} m²; garaż {f2(pu['garaz'])} m²; "
                 f"techniczna {f2(pu['techniczna'])} m²; klatki schodowe (wyłączone) {f2(pu['klatki'])} m². Założenia: światło "
                 f"ościeżnicy = światło muru − 2 × {f2(RAMA_OSCIEZNICY)} m; sufit podwieszany SUF_GK obniża o {f2(SUFIT_PODWIESZANY)} m.")
    # schody
    L.append("\n## 4. Schody\n")
    L.append("| Bieg | z0 [m] | stopni | szer. model / w świetle ścian [m] | długość [m] | prześwit min [m] (element) |")
    L.append("|---|---|---|---|---|---|")
    for r in A.tabele.get("schody", []):
        L.append(f"| {r['id']} | {f2(r['z0'], 3)} | {r['n']} | {f2(r['szer'], 3)} / {f2(r['clear'], 3)} | {f2(r['L'])} | "
                 f"{f2(r['przeswit'], 3)} ({r['el']}) |")
    # odległości
    L.append("\n## 5. Odległości od granic działki (WT §12) — wartości minimalne na element\n")
    L.append("| Element | Rodzaj | Granica | Odległość [m] | Wymóg [m] |")
    L.append("|---|---|---|---|---|")
    best = {}
    for r in A.tabele.get("odleglosci", []):
        k = (r["el"], r["kier"])
        if k not in best or r["d"] < best[k]["d"]:
            best[k] = r
    for r in sorted(best.values(), key=lambda r: (r["kier"], r["d"])):
        L.append(f"| {r['el']} | {r['rodzaj']} | {r['kier']} | {f2(r['d'])} | {f2(r['lim'])} |")
    if "linia_zabudowy_rezerwa" in inf:
        L.append(f"\nNajbardziej wysunięty ku drodze element budynku leży {f2(inf['linia_zabudowy_rezerwa'])} m przed "
                 "nieprzekraczalną linią zabudowy (po stronie działki).")
    # pełna lista
    L.append("\n## 6. Pełna lista kontroli\n")
    L.append("| Sekcja | Element | Parametr | Wartość | Wymóg | Status | Podstawa |")
    L.append("|---|---|---|---|---|---|---|")
    for w in A.wyniki:
        L.append(f"| {w.sekcja} | {w.element} | {w.parametr} | {w.wartosc} | {w.wymog} | {w.status} | {w.podstawa} |")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budynek", default=str(ROOT / "model/budynek.yaml"))
    ap.add_argument("--dzialka", default=str(ROOT / "model/dzialka.yaml"))
    ap.add_argument("--wymagania", default=str(ROOT / "docs/10_podstawy_prawne/wymagania.yaml"))
    ap.add_argument("--raport", default=str(ROOT / "docs/20_koncepcja/audyt_A1.md"))
    ap.add_argument("--wstep", default=None, help="plik Markdown z oceną audytora wstawiany do raportu (opcjonalnie)")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    try:
        a = AudytWT(Path(args.budynek).resolve(), Path(args.dzialka).resolve(), Path(args.wymagania))
    except Exception as e:  # noqa: BLE001
        print(f"Błąd wczytania modelu: {e}", file=sys.stderr)
        return 2
    A = a.run()
    extra = Path(args.wstep).read_text(encoding="utf-8") if args.wstep else ""
    Path(args.raport).write_text(raport_md(a, A, extra), encoding="utf-8")
    if args.json:
        Path(args.json).write_text(json.dumps([asdict(w) for w in A.wyniki], ensure_ascii=False, indent=1), encoding="utf-8")
    cnt = {s: sum(1 for w in A.wyniki if w.status == s) for s in STATUSY}
    print(f"Audyt A1: {cnt} → {args.raport}")
    for w in A.wyniki:
        if w.status in ("NIEZGODNE", "UWAGA"):
            print(f"  [{w.status}] {w.sekcja} | {w.element} | {w.parametr}: {w.wartosc} (wymóg {w.wymog})")
    return 1 if cnt["NIEZGODNE"] else 0


if __name__ == "__main__":
    sys.exit(main())
