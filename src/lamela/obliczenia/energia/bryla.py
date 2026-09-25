"""Geometria cieplna budynku z modelu `lamela.model` — elementy przegród pomieszczeń (strefa ogrzewana).

System wymiarów: **wewnętrzne całkowite** (PN-EN ISO 13789:2017 p. 5.? — „overall internal”; PN-EN ISO 14683 Ψ_oi):
* ściany: długość krawędzi wieloboku pomieszczenia (lica wykończone) × wysokość kondygnacji „od podłogi do podłogi”
  (kondygnacja najwyższa / pod dachem: do spodu płyty dachu);
* podłogi i stropy: pole wieloboku podłogi pomieszczenia (lica wykończone);
* okna i drzwi: wymiary otworu w świetle muru (metodologia wzór (59): „pole … w świetle otworu w przegrodzie”);
* mostki: Ψ_oi (węzły liniowe) — `fizyka.mostki`.
Rozpoznanie sąsiedztwa krawędzi pomieszczenia: próbkowanie krawędzi co ≤ 2 cm, dopasowanie do lica ściany
(odległość < 2 cm, kierunek równoległy), po drugiej stronie ściany — pomieszczenie (ta sama kondygnacja) albo
powietrze zewnętrzne; krawędzie bez ściany — granica „wirtualna” (otwarta przestrzeń) albo ostrzeżenie.
Podłogi: najniższa kondygnacja — grunt; wyżej — części nad pomieszczeniami niższej kondygnacji (ogrzewanymi /
nieogrzewanymi) i poza obrysem niższej kondygnacji (strop nad powietrzem zewnętrznym). Stropy/dachy: część nad
pomieszczeniem poza obrysem kondygnacji wyższej, przykryta elementem `dachy` (lub płytą wspornikową typu taras/stropodach).
Pomieszczenie ogrzewane: `temp` ≥ 8 °C i brak `ogrzewane: false`; pozostałe (garaż nieogrzewany) — przestrzenie
nieogrzewane (b_u z bilansu wg PN-EN ISO 13789 p. 6.4 / PN-EN 12831-1).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from ..fizyka.okna import Lamele, Okap
from ..fizyka.u_przegrody import warstwy_przegrody, warstwy_stropu

TOL_LICO = 0.02
KROK = 0.02


@dataclass
class Element:
    id: str
    rodzaj: str               # sciana | okno | drzwi | brama | podloga | strop | dach
    rola: str                 # sciana_zewn | sciana_nieogrz | sciana_wewn | dach | strop_zewn | strop_nieogrz | strop_nieogrz_gora | strop_wewn | podloga_grunt | okno | drzwi | brama
    pom: str
    sasiad: str               # 'zewn' | 'grunt' | id pomieszczenia
    A: float
    azymut: float | None = None
    nachylenie: float = 90.0
    przegroda: str | None = None       # kod przegrody (nieprzezroczyste) / symbol (otwory)
    uklad: str | None = None           # klucz układu warstw (cache U)
    warstwy: list | None = None        # pełny układ warstw (stropy złożone)
    otwor: Any = None
    sciana: str | None = None
    dlugosc: float = 0.0
    wysokosc: float = 0.0
    zacienienie: dict | None = None    # {"okap": Okap, "lamele": Lamele}
    dach: dict | None = None
    uwagi: str = ""


@dataclass
class PomE:
    id: str
    nazwa: str
    kond: str
    theta: float | None
    ogrzewane: bool
    A: float
    V: float
    h: float
    kategoria: str
    pobyt: bool
    went: dict | None
    raw: dict
    elementy: list[Element] = field(default_factory=list)
    krawedzie: list[dict] = field(default_factory=list)   # {dl, sasiad, sciana, zewn, p, q}

    @property
    def okna(self):
        return [e for e in self.elementy if e.rodzaj == "okno"]


@dataclass
class Bryla:
    model: Any
    pomieszczenia: dict[str, PomE]
    elementy: list[Element]
    wezly_auto: list[dict]
    ostrzezenia: list[str]
    azymut_osi_y: float
    grunt: dict                       # {"A", "P", "w", "przegroda"} — podłoga na gruncie strefy ogrzewanej
    grunt_nieogrz: dict               # to samo dla pomieszczeń nieogrzewanych (garaż)

    @property
    def ogrzewane(self) -> list[PomE]:
        return [p for p in self.pomieszczenia.values() if p.ogrzewane]

    @property
    def nieogrzewane(self) -> list[PomE]:
        return [p for p in self.pomieszczenia.values() if not p.ogrzewane]

    @property
    def A_f(self) -> float:
        return sum(p.A for p in self.ogrzewane)

    @property
    def V_netto(self) -> float:
        return sum(p.V for p in self.ogrzewane)

    def theta_srednia(self) -> float:
        V = sum(p.V for p in self.ogrzewane)
        return sum((p.theta or 20.0) * p.V for p in self.ogrzewane) / V if V else 20.0

    def elementy_obudowy(self, rola: str | None = None) -> list[Element]:
        """Elementy pomieszczeń ogrzewanych do zewnątrz / gruntu / przestrzeni nieogrzewanych."""
        out = []
        for e in self.elementy:
            pm = self.pomieszczenia[e.pom]
            if not pm.ogrzewane:
                continue
            if e.sasiad in ("zewn", "grunt") or (e.sasiad in self.pomieszczenia and not self.pomieszczenia[e.sasiad].ogrzewane):
                if rola is None or e.rola == rola:
                    out.append(e)
        return out


def _az(nx: float, ny: float, azymut_osi_y: float) -> float:
    return (math.degrees(math.atan2(nx, ny)) + azymut_osi_y) % 360.0


def _polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [x for x in getattr(g, "geoms", []) if x.geom_type == "Polygon"]


def czy_ogrzewane(raw: dict) -> bool:
    if raw.get("ogrzewane") is False:
        return False
    t = raw.get("temp")
    return t is not None and float(t) >= 8.0


def buduj_bryle(m) -> Bryla:
    """Elementy przegród wszystkich pomieszczeń modelu (ogrzewanych i nieogrzewanych)."""
    azy = float(getattr(m, "azymut_osi_y", 0.0) or 0.0)
    ostrz: list[str] = []
    P: dict[str, PomE] = {}
    for r in m.pomieszczenia():
        if r.polygon is None or r.polygon.is_empty:
            ostrz.append(f"pomieszczenie {r.id}: brak wieloboku — pominięte")
            continue
        og = czy_ogrzewane(r.raw)
        h = r.wysokosc or 2.5
        P[r.id] = PomE(r.id, r.nazwa, r.kond, float(r.temp) if r.temp is not None else None, og, r.pow_netto,
                       r.pow_netto * h, h, r.kategoria, r.pobyt_ludzi, r.went, r.raw)
    polys = {r.id: orient(r.polygon, 1.0) for r in m.pomieszczenia() if r.id in P}
    kond_ids = [k.id for k in m.kondygnacje]
    elems: list[Element] = []
    wezly: dict[str, float] = {}
    wezly_opis: dict[str, str] = {}
    n_el = [0]

    def eid(prefix):
        n_el[0] += 1
        return f"{prefix}{n_el[0]:03d}"

    def add_w(typ, dl, opis):
        wezly[typ] = wezly.get(typ, 0.0) + dl
        wezly_opis.setdefault(typ, opis)

    def pom_w(kid, pt, exclude=None):
        pnt = Point(pt)
        for rid, pg in polys.items():
            if rid != exclude and P[rid].kond == kid and pg.buffer(1e-3).contains(pnt):
                return rid
        return None

    outline = {k: m.obrys_kondygnacji(k, "zewn") for k in kond_ids}
    plyty = m.plyty()

    def h_kond(pm: PomE, kid: str) -> float:
        """Wysokość „od podłogi do podłogi” (wymiary wewnętrzne całkowite); pod dachem — do spodu płyty."""
        k = m.kondygnacja(kid)
        i = kond_ids.index(kid)
        nxt = m.kondygnacja(kond_ids[i + 1]) if i + 1 < len(kond_ids) else None
        c = polys[pm.id].representative_point()
        # płyta bezpośrednio nad pomieszczeniem
        best = None
        for sl in plyty:
            if sl["typ"] == "strop" and sl["nad"] != kid:
                continue
            if sl["spod"] <= k.rzedna + 1.0:
                continue
            if sl["poly_full"].buffer(0.02).contains(c) and (best is None or sl["spod"] < best["spod"]):
                best = sl
        if best is not None and best["typ"] == "strop" and nxt is not None:
            return nxt.rzedna - k.rzedna
        if best is not None:
            return best["spod"] - k.rzedna
        return nxt.rzedna - k.rzedna if nxt else pm.h

    for pm in P.values():
        pg = polys[pm.id]
        kid = pm.kond
        k = m.kondygnacja(kid)
        H = h_kond(pm, kid)
        walls = m.sciany(kid)
        coords = list(pg.exterior.coords)
        # --- krawędzie / ściany ---
        for a, b in zip(coords[:-1], coords[1:]):
            p = np.array(a)
            q = np.array(b)
            L = float(np.hypot(*(q - p)))
            if L < 0.02:
                continue
            u = (q - p) / L
            nout = np.array([u[1], -u[0]])            # CCW → na prawo = na zewnątrz pomieszczenia
            ns = max(2, int(math.ceil(L / KROK)))
            klas = []
            for j in range(ns):
                x = p + u * ((j + 0.5) / ns * L)
                hit = None
                for w in walls:
                    if abs(u[0] * w.u[1] - u[1] * w.u[0]) > 0.02:
                        continue
                    s, t = w.st(x)
                    if s < -TOL_LICO or s > w.L + TOL_LICO:
                        continue
                    if abs(t - w.t_max) < TOL_LICO:
                        hit = (w.id, +1)
                        break
                    if abs(t - w.t_min) < TOL_LICO:
                        hit = (w.id, -1)
                        break
                klas.append(hit)
            # grupowanie
            j = 0
            while j < ns:
                j2 = j
                while j2 + 1 < ns and klas[j2 + 1] == klas[j]:
                    j2 += 1
                dl = (j2 - j + 1) / ns * L
                xa = p + u * (j / ns * L)
                xb = p + u * ((j2 + 1) / ns * L)
                xm = 0.5 * (xa + xb)
                hit = klas[j]
                if hit is None:
                    nb = pom_w(kid, xm + nout * 0.05, exclude=pm.id)
                    if nb is None:
                        ostrz.append(f"{pm.id}: krawędź {dl:.2f} m bez ściany i bez sąsiedniego pomieszczenia "
                                     f"(x={xm[0]:.2f}, y={xm[1]:.2f}) — pominięta")
                    pm.krawedzie.append({"dl": dl, "sasiad": nb or "?", "sciana": None, "zewn": False, "a": xa, "b": xb,
                                         "wirtualna": True})
                    j = j2 + 1
                    continue
                w = m.sciana(hit[0])
                side = hit[1]
                t_other = (w.t_min - 0.08) if side > 0 else (w.t_max + 0.08)
                s_m, _ = w.st(xm)
                probe = w.pt(s_m, t_other)
                nb = pom_w(kid, probe)
                if nb is None:
                    inside_out = outline[kid].buffer(-0.01).contains(Point(probe))
                    sas = "zewn"
                    if inside_out:
                        ostrz.append(f"{pm.id}: po drugiej stronie ściany {w.id} brak pomieszczenia w obrysie "
                                     f"kondygnacji — przyjęto powietrze zewnętrzne")
                else:
                    sas = nb
                if sas == "zewn":
                    rola = "sciana_zewn"
                elif not P[nb].ogrzewane:
                    rola = "sciana_nieogrz"
                else:
                    rola = "sciana_wewn"
                sa, _ = w.st(xa)
                sb, _ = w.st(xb)
                s0, s1 = min(sa, sb), max(sa, sb)
                az = _az(nout[0], nout[1], azy) if sas == "zewn" else None
                A_wall = dl * H
                # otwory
                for o in w.otwory:
                    ov = min(o.s1, s1) - max(o.s0, s0)
                    if ov < 0.5 * (o.s1 - o.s0):
                        continue
                    if o.typ == "otwor":
                        continue
                    Ao = o.szer * o.wys
                    A_wall -= Ao
                    if o.typ in ("okno", "fix", "drzwi_przesuwne_HS"):
                        rodz, rol = "okno", "okno"
                    elif o.typ == "brama":
                        rodz, rol = "brama", "brama"
                    else:
                        rodz, rol = "drzwi", "drzwi"
                    if sas != "zewn" and P.get(sas) is not None and P[sas].ogrzewane and pm.ogrzewane:
                        continue                               # drzwi wewnętrzne między pom. ogrzewanymi
                    el = Element(o.id, rodz, rol, pm.id, sas, Ao, az, 90.0, o.symbol or o.typ, None, None, o, w.id,
                                 o.szer, o.wys)
                    if sas == "zewn" and rodz == "okno":
                        el.zacienienie = _zacienienie_okna(m, w, o, plyty)
                    elems.append(el)
                    pm.elementy.append(el)
                    if sas == "zewn" or not (P.get(sas) and P[sas].ogrzewane):
                        add_w("oscieze", 2 * (o.szer + o.wys), "ościeża, nadproża i progi/parapety otworów (obwód otworu)")
                if A_wall < -1e-6:
                    ostrz.append(f"{pm.id}/{w.id}: pole otworów większe od pola ściany")
                el = Element(eid("W"), "sciana", rola, pm.id, sas, max(A_wall, 0.0), az, 90.0, w.przegroda_kod,
                             w.przegroda_kod, None, None, w.id, dl, H)
                elems.append(el)
                pm.elementy.append(el)
                pm.krawedzie.append({"dl": dl, "sasiad": sas, "sciana": w.id, "zewn": sas == "zewn", "a": xa, "b": xb,
                                     "rola": rola, "grubosc": w.grubosc})
                j = j2 + 1
        # narożniki pionowe (krawędzie zewnętrzne sąsiadujące)
        kz = [kr for kr in pm.krawedzie if kr.get("zewn")]
        for k1 in kz:
            for k2 in kz:
                if k1 is k2 or np.hypot(*(k1["b"] - k2["a"])) > 0.03:
                    continue
                d1 = (k1["b"] - k1["a"]) / max(np.hypot(*(k1["b"] - k1["a"])), 1e-9)
                d2 = (k2["b"] - k2["a"]) / max(np.hypot(*(k2["b"] - k2["a"])), 1e-9)
                cr = d1[0] * d2[1] - d1[1] * d2[0]
                if abs(cr) < 0.05:
                    continue
                if cr > 0:
                    add_w("naroznik_wypukly", H, "narożnik zewnętrzny (wypukły) ścian zewnętrznych")
                else:
                    add_w("naroznik_wklesly", H, "narożnik wewnętrzny (wklęsły) ścian zewnętrznych")
        # --- podłoga ---
        pod = pm.raw.get("podloga") or k.podloga
        fpoly = pm.raw and (m.pomieszczenie(pm.id).polygon_podlogi or pg)
        i = kond_ids.index(kid)
        dl_zewn = sum(kr["dl"] for kr in pm.krawedzie if kr.get("zewn") or kr.get("rola") == "sciana_nieogrz")
        if i == 0:
            pp = m.przegroda(pod) if pod else None
            rola = "podloga_grunt" if (pp is None or pp.typ in ("podloga_na_gruncie", "plyta_fund")) else "strop_zewn"
            el = Element(eid("F"), "podloga", rola, pm.id, "grunt" if rola == "podloga_grunt" else "zewn",
                         fpoly.area, None, 0.0, pod, pod)
            elems.append(el)
            pm.elementy.append(el)
            if pm.ogrzewane:
                add_w("sciana_grunt", sum(kr["dl"] for kr in pm.krawedzie if kr.get("zewn")),
                      "połączenie ściana zewnętrzna – podłoga na gruncie / płyta fundamentowa (cokół)")
        else:
            below = kond_ids[i - 1]
            pozost = fpoly
            for rid, pg2 in polys.items():
                if P[rid].kond != below:
                    continue
                inter = fpoly.intersection(pg2)
                if inter.area < 0.05:
                    continue
                pozost = pozost.difference(pg2)
                og2 = P[rid].ogrzewane
                if og2 and pm.ogrzewane and abs((P[rid].theta or 20) - (pm.theta or 20)) < 0.5:
                    continue
                st = _strop_pod(m, below, inter)
                ws, op = warstwy_stropu(m, st or {"grubosc": 0.2}, kid) if st else (None, "")
                rola = ("strop_nieogrz" if not og2 else "strop_wewn")
                el = Element(eid("F"), "strop", rola, pm.id, rid, inter.area, None, 0.0,
                             st.get("id") if st else None, f"{st.get('id') if st else '?'}|{kid}|dol", ws)
                el.uwagi = op
                elems.append(el)
                pm.elementy.append(el)
            ext = fpoly.difference(outline[below].buffer(0.01))
            if ext.area > 0.05:
                st = _strop_pod(m, below, ext)
                ws, op = warstwy_stropu(m, st or {"grubosc": 0.2}, kid) if st else (None, "")
                el = Element(eid("F"), "strop", "strop_zewn", pm.id, "zewn", ext.area, None, 0.0,
                             st.get("id") if st else None, f"{st.get('id') if st else '?'}|{kid}|zewn", ws)
                el.uwagi = op
                if st is None:
                    ostrz.append(f"{pm.id}: podłoga nad powietrzem zewnętrznym ({ext.area:.2f} m²) bez elementu "
                                 "`stropy` — brak układu warstw")
                elems.append(el)
                pm.elementy.append(el)
                if pm.ogrzewane:
                    add_w("strop_zewn_krawedz", ext.boundary.length * 0.5,
                          "krawędź stropu nad powietrzem zewnętrznym (wspornik bryły) — połączenie ze ścianą")
        # --- strop / dach nad ---
        top = kond_ids[i + 1] if i + 1 < len(kond_ids) else None
        pozost = pg
        if top is not None:
            for rid, pg2 in polys.items():
                if P[rid].kond != top:
                    continue
                inter = pg.intersection(pg2)
                if inter.area < 0.05:
                    continue
                if pm.ogrzewane and not P[rid].ogrzewane:
                    st = _strop_pod(m, kid, inter)
                    ws, op = warstwy_stropu(m, st or {"grubosc": 0.2}, top) if st else (None, "")
                    el = Element(eid("C"), "strop", "strop_nieogrz_gora", pm.id, rid, inter.area, None, 0.0,
                                 st.get("id") if st else None, f"{st.get('id') if st else '?'}|{top}|gora", ws)
                    elems.append(el)
                    pm.elementy.append(el)
                elif pm.ogrzewane is False and P[rid].ogrzewane:
                    pass
                elif abs((P[rid].theta or 20) - (pm.theta or 20)) >= 0.5 and pm.ogrzewane and P[rid].ogrzewane:
                    st = _strop_pod(m, kid, inter)
                    ws, op = warstwy_stropu(m, st or {"grubosc": 0.2}, top) if st else (None, "")
                    el = Element(eid("C"), "strop", "strop_wewn", pm.id, rid, inter.area, None, 0.0,
                                 st.get("id") if st else None, f"{st.get('id') if st else '?'}|{top}|gora", ws)
                    elems.append(el)
                    pm.elementy.append(el)
            pozost = pg.difference(outline[top].buffer(0.01))
        z_top = k.rzedna + 0.5
        dachy_pom = 0.0
        for sl in plyty:
            if sl["typ"] == "strop":
                continue
            raw = sl["raw"]
            prz = raw.get("przegroda")
            pp = m.przegroda(prz) if prz else None
            if sl["typ"] == "wspornik" and (pp is None or pp.typ not in ("taras", "stropodach")):
                continue
            if sl["spod"] < z_top:
                continue
            if top is not None and sl["spod"] > m.kondygnacja(top).rzedna + 1.0:
                continue
            inter = pozost.intersection(sl["poly_full"])
            if inter.area < 0.05:
                continue
            el = Element(eid("R"), "dach", "dach", pm.id, "zewn", inter.area, None, 0.0, prz, prz)
            el.dach = raw if sl["typ"] == "dach" else None
            elems.append(el)
            pm.elementy.append(el)
            dachy_pom += inter.area
            if pm.ogrzewane:
                # attyka / krawędź dachu wzdłuż ścian zewnętrznych pomieszczenia
                for kr in pm.krawedzie:
                    if not kr.get("zewn"):
                        continue
                    seg = LineString([tuple(kr["a"]), tuple(kr["b"])])
                    if sl["poly_full"].buffer(0.3).intersection(seg).length > 0.5 * seg.length:
                        add_w("attyka", kr["dl"], "połączenie stropodachu ze ścianą zewnętrzną (attyka / okap)")
        if pozost.area - dachy_pom > 0.5 and pm.ogrzewane:
            ostrz.append(f"{pm.id}: {pozost.area - dachy_pom:.2f} m² sufitu bez rozpoznanego elementu nad "
                         "(dach/strop) — sprawdzić model (konwencja: odsłonięte stropy jako `dachy`)")
        # strop pośredni (ściana zewn. na wysokości stropu nad pomieszczeniem pod pomieszczeniem ogrzewanym)
        if top is not None and pm.ogrzewane:
            for kr in pm.krawedzie:
                if not kr.get("zewn"):
                    continue
                seg = LineString([tuple(kr["a"]), tuple(kr["b"])])
                cov = outline[top].buffer(0.05).intersection(seg.buffer(0.3)).area / max(seg.length * 0.6, 1e-9)
                if cov > 0.5:
                    add_w("strop_posredni", kr["dl"], "połączenie ściany zewnętrznej ze stropem pośrednim")
    # płyty wspornikowe z łącznikiem termicznym / bez
    for sl in plyty:
        if sl["typ"] != "wspornik":
            continue
        raw = sl["raw"]
        prz = raw.get("przegroda")
        pp = m.przegroda(prz) if prz else None
        if pp is not None and pp.typ in ("taras", "stropodach") and False:
            pass
        dl = 0.0
        for kid in kond_ids:
            o = outline[kid]
            if o.is_empty:
                continue
            dl = max(dl, sl["poly_full"].buffer(0.02).intersection(o.exterior).length)
        if dl > 0.1:
            typ = "plyta_wspornikowa_lacznik" if raw.get("lacznik_termiczny") else "plyta_wspornikowa"
            add_w(typ, dl, "płyta wspornikowa przechodząca przez ścianę zewnętrzną" +
                  (" — łącznik termoizolacyjny" if raw.get("lacznik_termiczny") else " — bez łącznika"))
    # połączenia z garażem (ściana dom–garaż do ścian zewnętrznych) — pionowe
    for pm in P.values():
        if not pm.ogrzewane:
            continue
        for kr in pm.krawedzie:
            if kr.get("rola") == "sciana_nieogrz":
                add_w("polaczenie_nieogrz", 0.0, "połączenia przegród dom–garaż (nieogrzewany)")
    # grunt — strefa ogrzewana i nieogrzewana
    def grunt_dane(og: bool) -> dict:
        A = Pp = 0.0
        ww = []
        przs = set()
        for pm in P.values():
            if pm.ogrzewane != og:
                continue
            for e in pm.elementy:
                if e.rola == "podloga_grunt":
                    A += e.A
                    przs.add(e.przegroda)
            if any(e.rola == "podloga_grunt" for e in pm.elementy):
                for kr in pm.krawedzie:
                    sas = kr["sasiad"]
                    eksp = kr.get("zewn") or (og and sas in P and not P[sas].ogrzewane) or \
                        (not og and sas in P and P[sas].ogrzewane)
                    if eksp and kr.get("sciana"):
                        Pp += kr["dl"]
                        ww.append(kr.get("grubosc", 0.4))
        return {"A": A, "P": Pp, "w": float(np.median(ww)) if ww else 0.4, "przegrody": sorted(x for x in przs if x)}
    wezly_l = [{"typ": t, "dlugosc": round(v, 3), "opis": wezly_opis[t], "zrodlo_geometrii": "auto (bryla.py)"}
               for t, v in wezly.items() if v > 0 or t == "polaczenie_nieogrz"]
    return Bryla(m, P, elems, wezly_l, ostrz, azy, grunt_dane(True), grunt_dane(False))


def _strop_pod(m, kid_below: str, region) -> dict | None:
    """Element `stropy` nad kondygnacją `kid_below` pokrywający region (największe przecięcie)."""
    best, ba = None, 0.0
    for st in m.stropy():
        if str(st.get("nad")) != kid_below:
            continue
        from lamela.model import make_polygon
        try:
            P = make_polygon(st["obrys"])
        except Exception:  # noqa: BLE001
            continue
        a = P.intersection(region).area
        if a > ba:
            best, ba = st, a
    if best is None:
        # wspornik pod pomieszczeniem (płyta wspornikowa jako podłoga)
        for w in m.wsporniki():
            from lamela.model import make_polygon
            P = make_polygon(w["obrys"])
            a = P.intersection(region).area
            if a > ba:
                best, ba = {"id": w.get("id"), "grubosc": w.get("grubosc"), "mat": w.get("mat"), "sufit": w.get("sufit")}, a
    return best


def _zacienienie_okna(m, w, o, plyty) -> dict | None:
    """Okap (płyta nad oknem wysunięta przed lico) i lamele przed oknem — parametry do `fizyka.okna`."""
    es = w.ext_side
    if es is None:
        return None
    t_face = w.face_t(es, "all")
    t0, t1 = o.rama_t
    t_glass = 0.5 * (t0 + t1)
    sm = 0.5 * (o.s0 + o.s1)
    nvec = es * w.n
    wynik = {}
    best = None
    for sl in plyty:
        if sl["spod"] < o.z1 - 0.05 or sl["spod"] > o.z1 + 3.5:
            continue
        # promień od lica na zewnątrz
        p_face = w.pt(sm, t_face + es * 0.02)
        if not sl["poly_full"].contains(Point(p_face)):
            continue
        ray = LineString([tuple(p_face), tuple(p_face + nvec * 20.0)])
        seg = sl["poly_full"].intersection(ray)
        dl = seg.length if not seg.is_empty else 0.0
        if dl < 0.05:
            continue
        P = dl + abs(t_face - t_glass) + 0.02
        G = sl["spod"] - o.z1
        # przedłużenia boczne wzdłuż ściany (oś s): przecięcie z linią równoległą w połowie wysięgu
        tl = t_face + es * (0.02 + dl / 2)
        line = LineString([tuple(w.pt(-50, tl)), tuple(w.pt(w.L + 50, tl))])
        cut = sl["poly_full"].intersection(line)
        if cut.is_empty:
            continue
        ss = [w.st(c)[0] for g in (getattr(cut, "geoms", None) or [cut]) for c in g.coords]
        sa, sb = min(ss), max(ss)
        # oś x zacienienia: e_x = (cos a, −sin a) względem normalnej zewn. — zgodność z kierunkiem u ściany
        ax = math.atan2(nvec[0], nvec[1])
        ex = np.array([math.cos(ax), -math.sin(ax)])
        zgodny = float(ex @ w.u) > 0
        ext_s0 = max(0.0, o.s0 - sa)
        ext_s1 = max(0.0, sb - o.s1)
        ok_ = Okap(wysieg=P, odstep=max(G, 0.0), ext_lewa=ext_s0 if zgodny else ext_s1,
                   ext_prawa=ext_s1 if zgodny else ext_s0)
        if best is None or G < best[0]:
            best = (G, ok_, sl.get("id"))
    if best:
        wynik["okap"] = best[1]
        wynik["okap_zrodlo"] = best[2]
    for lm in m.lamele():
        a = np.array(lm["linia"][0], float)
        b = np.array(lm["linia"][1], float)
        d = b - a
        Ld = float(np.hypot(*d))
        if Ld < 0.1:
            continue
        if abs(d[0] * w.u[1] - d[1] * w.u[0]) / Ld > 0.05:
            continue
        sa, ta = w.st(a)
        sb, tb = w.st(b)
        tt = 0.5 * (ta + tb)
        if (tt - t_face) * es < -0.01 or abs(tt - t_face) > 1.5:
            continue
        lo, hi = min(sa, sb), max(sa, sb)
        ov_s = max(0.0, min(hi, o.s1) - max(lo, o.s0)) / max(o.s1 - o.s0, 1e-9)
        ov_z = max(0.0, min(lm["z_do"], o.z1) - max(lm["z_od"], o.z0)) / max(o.z1 - o.z0, 1e-9)
        if ov_s > 0.5 and ov_z > 0.5:
            wynik["lamele"] = Lamele(rozstaw=float(lm["rozstaw"]), b=float(lm["b"]), h=float(lm["h"]),
                                     opis=f"{lm.get('id')} (pokrycie {ov_s * ov_z * 100:.0f} %)")
    return wynik or None
