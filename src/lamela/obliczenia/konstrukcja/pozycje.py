"""Pozycje obliczeniowe z modelu budynku — ścieżka obciążeń od dachu do fundamentów.

Kolejność (malejąco po rzędnej): grupy płyt (dach, stropy, wsporniki połączone na tym samym poziomie — jeden model MES)
→ belki podpierające płyty → ściany pod płytami (profile obciążeń wzdłuż osi, przekazanie przez otwory na filarki)
→ … → słupy → fundamenty. Schody liczone na początku (reakcje przekazywane na krawędź stropu i ścianę spocznika).

Dane z modelu (``lamela.model.Model``): stropy/dachy/wsporniki (obrys, otwory, grubość, rzędne, przegrody/podłogi →
ciężary warstw ρ·g·d), ściany (oś, przegroda → grubość i materiał warstwy konstrukcyjnej, z_od/z_do, otwory),
belki (oś, b, h, spod, mat), słupy (xy, przekrój, mat, z_od/z_do), fundamenty (oś/obrys, b, h, spod), schody (biegi,
spoczniki), attyki dachów (zaspy), działka (teren → głębokość posadowienia). Szczegóły i ograniczenia: README.md pakietu.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.ops import unary_union

from . import fundamenty as fund
from . import mur as murm
from . import schody as schm
from . import stal as stalm
from . import zelbet
from .materialy import (TABL_BETON, Beton, Mur, StalKonstr, StalZbrojeniowa, klasa_betonu_z_nazwy, klasa_muru_z_nazwy,
                        pole_preta, przekroj)
from .obciazenia import (Oddz, ZestawienieStale, ciezar_materialu, kombinacje, obciazenie_uzytkowe, snieg_attyka,
                         snieg_B2_attyka, snieg_B2_uskok, snieg_dach_plaski, snieg_uskok, wiatr_dach_plaski, wiatr_qp,
                         wiatr_sciany, zastepcze_dzialowe, zestawienie_przegrody)
from .plyty import PlytaMES, PodporaLiniowa, PodporaPunktowa, PoleCiagle, WynikMES, wood_armer, wyrownaj_moment_podporowy
from .statyka import Belka, ObcP, ObcQ, Podpora
from .wspolne import BladDanych, Krok, Parametry, Warunek, Wynik, f, tabela

TOL_Z = 0.06
TYPY_NOSNE = ("sciana_zewn", "sciana_wewn_nosna")
PRZYPADKI = ("G", "QA", "QA_pA", "QA_pB", "H", "S1", "S2", "SB2")


# ==================================================================================================
# Struktury wyników
# ==================================================================================================
@dataclass
class Pozycja:
    """Pozycja „Obliczeń statycznych”: schemat, obciążenia, wyniki (z wykorzystaniem nośności), wnioski."""
    nr: str
    ident: str
    tytul: str
    rodzaj: str
    opis: list = field(default_factory=list)
    obciazenia: list = field(default_factory=list)
    wyniki: list = field(default_factory=list)
    tabele: list = field(default_factory=list)
    rysunki: list = field(default_factory=list)
    przyjeto: list = field(default_factory=list)
    uwagi: list = field(default_factory=list)
    prety: list = field(default_factory=list)
    dane: dict = field(default_factory=dict)
    podpozycje: list = field(default_factory=list)

    @property
    def warunki(self) -> list:
        out = [w for r in self.wyniki for w in r.warunki]
        for sp in self.podpozycje:
            out += sp.warunki
        return out

    @property
    def wykorzystanie(self) -> float:
        v = [w.eta for w in self.warunki if w.eta == w.eta]
        return max(v) if v else 0.0

    @property
    def ok(self) -> bool:
        return all(w.ok for w in self.warunki)


class Profil:
    """Obciążenie liniowe wzdłuż osi elementu (ściany/ławy): siatka s ∈ [0, L], przypadki → q(s) [kN/m]."""

    def __init__(self, L: float, ds: float = 0.05):
        n = max(int(round(L / ds)), 2)
        self.L = L
        self.s = np.linspace(0.0, L, n + 1)
        self.q: dict[str, np.ndarray] = {}

    def get(self, c: str) -> np.ndarray:
        return self.q.get(c, np.zeros_like(self.s))

    def dodaj(self, c: str, s_pts, q_pts):
        s_pts, q_pts = np.asarray(s_pts, float), np.asarray(q_pts, float)
        if len(s_pts) == 0:
            return
        o = np.argsort(s_pts)
        s_pts, q_pts = s_pts[o], q_pts[o]
        val = np.interp(self.s, s_pts, np.nan_to_num(q_pts), left=0.0, right=0.0)
        inside = (self.s >= s_pts[0] - 1e-6) & (self.s <= s_pts[-1] + 1e-6)
        self.q[c] = self.get(c) + np.where(inside, val, 0.0)

    def dodaj_stale(self, c: str, val: float, s0: float = 0.0, s1: float | None = None):
        s1 = self.L if s1 is None else s1
        self.q[c] = self.get(c) + np.where((self.s >= s0 - 1e-9) & (self.s <= s1 + 1e-9), val, 0.0)

    def dodaj_skupiona(self, c: str, P: float, s_c: float, szer: float = 0.25):
        s0, s1 = max(s_c - szer / 2, 0.0), min(s_c + szer / 2, self.L)
        if s1 - s0 < 1e-6:
            s0, s1 = max(0.0, self.L - szer), self.L
        self.dodaj_stale(c, P / (s1 - s0), s0, s1)

    def calka(self, c: str, s0: float = 0.0, s1: float | None = None) -> float:
        s1 = self.L if s1 is None else s1
        m = (self.s >= s0 - 1e-9) & (self.s <= s1 + 1e-9)
        if m.sum() < 2:
            return 0.0
        return float(np.trapezoid(self.get(c)[m], self.s[m]))

    def kombinacja(self, wsp: dict) -> np.ndarray:
        out = np.zeros_like(self.s)
        for c, a in wsp.items():
            out = out + a * self.get(c)
        return out

    def srednia_ruchoma(self, arr: np.ndarray, okno: float = 1.0) -> np.ndarray:
        ds = self.s[1] - self.s[0]
        n = max(int(round(okno / ds)), 1)
        if n >= len(arr):
            return np.full_like(arr, arr.mean())
        k = np.ones(n) / n
        return np.convolve(arr, k, mode="same")

    def przypadki(self) -> list[str]:
        return list(self.q)


@dataclass
class ElementPlyty:
    typ: str
    id: str
    poly: Polygon
    poly_full: Polygon
    spod: float
    wierzch: float
    top: float
    h: float
    raw: dict
    rola: str = "strop"
    kat_q: str = "strop"
    odsloniety: bool = False
    beton: Beton | None = None
    ekspozycja: str = "XC1"
    zest: ZestawienieStale | None = None
    top_attyki: float | None = None


@dataclass
class Grupa:
    idx: int
    el: list
    poly: Polygon = None
    wierzch: float = 0.0
    fe: PlytaMES | None = None
    res: dict = field(default_factory=dict)
    podp_l: list = field(default_factory=list)
    podp_p: list = field(default_factory=list)
    komorki: list = field(default_factory=list)
    xl: list = field(default_factory=list)
    yl: list = field(default_factory=list)
    linie: list = field(default_factory=list)       # (LineString, przypadek, q)
    punkty: list = field(default_factory=list)      # ((x, y), przypadek, P)
    snieg: list = field(default_factory=list)
    env: dict = field(default_factory=dict)

    @property
    def nazwa(self) -> str:
        return " + ".join(e.id for e in self.el)


# ==================================================================================================
# Analiza
# ==================================================================================================
class AnalizaKonstrukcji:
    """Obliczenia statyczne budynku z modelu. ``uruchom()`` tworzy listę :attr:`pozycje`."""

    def __init__(self, model, p: Parametry | None = None, rys_dir: str | Path | None = None):
        self.m = model
        self.p = p or Parametry.z_wymagan()
        self.p.z_modelu(model.raw)
        self.rys_dir = Path(rys_dir) if rys_dir else None
        if self.rys_dir:
            self.rys_dir.mkdir(parents=True, exist_ok=True)
        self.stal = StalZbrojeniowa(f_yk=self.p.f_yk, gamma_s=self.p.gamma_s, E_s=self.p.E_s)
        self.pozycje: list[Pozycja] = []
        self.ogolne: list = []
        self.uwagi: list[str] = []
        self.brak_danych: list[str] = []
        self.grupy: list[Grupa] = []
        self.prof: dict[str, dict] = {}         # id ściany → {"top_s": Profil, "top_a": Profil, "dol": Profil, ...}
        self.slupy_N: dict[str, dict] = {}      # id słupa → {przypadek: N [kN]}
        self.pending_sciany: dict[str, list] = {}   # id ściany → [(przypadek, P, s_c, szer)]
        self.pos_plyty: list[Pozycja] = []
        self.pos_schody: list[Pozycja] = []
        self.pos_belki: list[Pozycja] = []
        self.pos_sciany: list[Pozycja] = []
        self.pos_nadproza: list[Pozycja] = []
        self.pos_slupy: list[Pozycja] = []
        self.pos_fund: list[Pozycja] = []
        self.pos_wience: list[Pozycja] = []
        self.pos_obc: Pozycja | None = None
        self.q_p = None
        self.wiatr_sc = None

    # --------------------------------------------------------------------------------------------
    def log(self, tekst: str):
        if tekst not in self.uwagi:
            self.uwagi.append(tekst)

    def brak(self, tekst: str):
        if tekst not in self.brak_danych:
            self.brak_danych.append(tekst)

    def rys(self, nazwa: str) -> Path | None:
        return (self.rys_dir / nazwa) if self.rys_dir else None

    def uruchom(self) -> "AnalizaKonstrukcji":
        self._ogolne()
        self._grupy_plyt()
        self._schody()
        zdarz = [(g.wierzch + 0.001, "g", g) for g in self.grupy]
        zdarz += [(w.z_do, "s", w) for w in self.m.sciany() if w.typ in TYPY_NOSNE]
        zdarz.sort(key=lambda t: -t[0])
        for _, typ, ob in zdarz:
            if typ == "g":
                self._obc_na_grupie(ob)
                self._analiza_grupy(ob)
                self._belki_grupy(ob)
                self._slupy_pod_grupa(ob)
            else:
                self._sciana(ob)
        self._nadproza()
        self._wience()
        self._slupy()
        self._fundamenty()
        self._numeruj()
        return self

    # ============================================================================================
    # 0. Obciążenia ogólne
    # ============================================================================================
    def _ogolne(self):
        p, m = self.p, self.m
        poz = Pozycja("0", "OBC", "Zestawienie obciążeń ogólnych i założenia materiałowe", "obciazenia")
        # wysokość budynku
        tops = [pl["top_attyki"] or pl["top"] for pl in m.plyty() if pl["typ"] == "dach"] or [pl["top"] for pl in m.plyty()] or [6.0]
        H = max(tops) - min((k.rzedna for k in m.kondygnacje), default=0.0) + max(-self.p.teren_domyslny, 0)
        try:
            x0, y0, x1, y1 = m.bbox()
        except Exception:  # noqa: BLE001
            U = unary_union([pl["poly_full"] for pl in m.plyty()])
            x0, y0, x1, y1 = U.bounds
        self.H_bud = H
        self.wym = (x1 - x0, y1 - y0)
        sn = snieg_dach_plaski(p)
        poz.wyniki.append(sn)
        self.snieg_rown = sn
        wq = wiatr_qp(H, p)
        poz.wyniki.append(wq)
        self.q_p = wq.q_p
        b, d = max(self.wym), min(self.wym)
        ws = wiatr_sciany(H, b, d, wq.q_p, p)
        ws2 = wiatr_sciany(H, d, b, wq.q_p, p)
        ws2.nazwa += " — kierunek prostopadły"
        poz.wyniki += [ws, ws2]
        self.wiatr_sc = max(ws, ws2, key=lambda w: max(abs(w.w_max_parcie), abs(w.w_max_ssanie)))
        dachy = [d_ for d_ in m.dachy() if isinstance(d_.get("attyka"), dict)]
        if dachy:
            hp = max(float(d_["attyka"].get("wys_nad_pokryciem", 0)) for d_ in dachy)
            poz.wyniki.append(wiatr_dach_plaski(H, hp, b, wq.q_p, p))
        # użytkowe
        rows = []
        for r in ("strop", "schody", "taras", "dach"):
            u = obciazenie_uzytkowe(r, p)
            rows.append([u.opis, (u.q_k, 2), (u.Q_k, 1), "/".join(f(x, 1) for x in u.psi), u.zrodlo])
        poz.tabele.append("**Obciążenia użytkowe (R5 3.3, W-263)**\n\n" + tabela(
            ["Powierzchnia", "q_k [kN/m²]", "Q_k [kN]", "ψ₀/ψ₁/ψ₂", "Podstawa"], rows))
        # materiały i otuliny
        rows = []
        for rola, opis in (("strop", "stropy, wieńce, belki wewnętrzne"), ("dach", "płyty stropodachów"),
                           ("wspornik", "płyty wysunięte na zewnątrz (taras, okapy)"), ("fundament", "ławy, stopy, płyta fund.")):
            ex, kl = p.beton_dla(rola)
            ot = zelbet.otulina(ex, 12, p, na_gruncie="podbeton" if rola == "fundament" else None)
            rows.append([opis, ex, kl, (ot.c_min_dur, 0), (ot.c_nom, 0), f(p.w_max.get(ex, 0.3), 1)])
        poz.tabele.append("**Beton, klasy ekspozycji i otulenia (PN-EN 1992-1-1 4.4.1, R5 3.6, W-266)**\n\n" + tabela(
            ["Element", "Ekspozycja", "Beton (min.)", "c_min,dur [mm]", "c_nom [mm] (φ12)", "w_max [mm]"], rows))
        mr = Mur.z_parametrow(p)
        poz.opis.append(
            f"Stal zbrojeniowa {p.stal_zbr} (klasa C): f_yk = {f(p.f_yk, 0)} MPa, f_yd = {f(p.f_yd, 1)} MPa; γ_c = {f(p.gamma_c, 1)}, "
            f"γ_s = {f(p.gamma_s, 2)} (NA). Mur: {mr.nazwa}: f_k = {f(mr.f_k, 2)} MPa, γ_M = {f(mr.gamma_M, 1)}, f_d = {f(mr.f_d, 2)} MPa. "
            f"Stal konstrukcyjna {p.stal_konstr}: γ_M0 = γ_M1 = {f(p.gM0, 1)}, γ_M2 = {f(p.gM2, 2)}. "
            f"Klasa konsekwencji {p.klasa_konsekwencji}, K_FI = {f(p.K_FI, 1)}; okres użytkowania 50 lat (S4).")
        poz.opis.append(
            "Kombinacje (PN-EN 1990 + NA): STR/GEO — mniej korzystne z 6.10a: Σ1,35·G_k + 1,5·ψ₀·Q_k i 6.10b: Σ0,85·1,35·G_k + "
            "1,5·Q_k,1 + 1,5·Σψ₀·Q_k,i; EQU: 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb; wyjątkowa 6.11b: G + A_d + ψ₁·Q₁ + ψ₂·Q_i; "
            "SLS: charakterystyczna G + Q₁ + ψ₀Q_i, quasi-stała G + ψ₂Q. Obciążenia użytkowe dachu (kat. H) nie są łączone ze śniegiem.")
        self.pos_obc = poz

    # ============================================================================================
    # 1. Płyty — grupy, obciążenia, MES, wymiarowanie
    # ============================================================================================
    def _element_plyty(self, pl: dict) -> ElementPlyty:
        m, p = self.m, self.p
        raw = pl["raw"]
        if pl["typ"] == "dach":
            h = float(raw["plyta"]["grubosc"])
        else:
            h = float(raw["grubosc"])
        e = ElementPlyty(pl["typ"], str(pl["id"]), pl["poly"], pl["poly_full"], pl["spod"], pl["wierzch"], pl["top"], h, raw,
                         top_attyki=pl.get("top_attyki"))
        prz = m.przegroda(str(raw.get("przegroda"))) if raw.get("przegroda") else None
        # zestawienie ciężarów
        if e.typ == "strop":
            z = ZestawienieStale(f"{e.id} — strop (podłoga {raw.get('podloga')}, sufit {raw.get('sufit')})")
            if raw.get("podloga") and m.przegroda(str(raw["podloga"])):
                zp = zestawienie_przegrody(m, str(raw["podloga"]), p, tylko="nad")
                z.warstwy += zp.warstwy
            else:
                self.brak(f"{e.id}: brak przegrody podłogi (podloga) — przyjęto tylko płytę")
            z.dodaj("Płyta żelbetowa", "ZB", h, p.ciezar_zelbetu, "warstwa konstrukcyjna")
            suf = raw.get("sufit")
            if suf and m.przegroda(str(suf)):
                z.warstwy += zestawienie_przegrody(m, str(suf), p).warstwy
            elif suf and m.material(str(suf)):
                mat = m.material(str(suf))
                z.dodaj(mat.nazwa, str(suf), 0.01, ciezar_materialu(mat, p)[0], "sufit (1 cm — konwencja modelu)")
            e.zest = z
        else:
            if prz is None:
                self.brak(f"{e.id}: brak przegrody — przyjęto płytę bez warstw")
                z = ZestawienieStale(f"{e.id}")
                z.dodaj("Płyta żelbetowa", "ZB", h, p.ciezar_zelbetu)
            else:
                z = zestawienie_przegrody(m, prz.kod, p, grubosc_konstr=h, tytul=f"{e.id} — {prz.nazwa}")
                if not prz.ma_oznaczona_konstr:
                    z.dodaj("Płyta żelbetowa", "ZB", h, p.ciezar_zelbetu)
            e.zest = z
        # beton
        kl = None
        if raw.get("mat"):
            mt = m.material(str(raw["mat"]))
            kl = klasa_betonu_z_nazwy(mt.nazwa if mt else None) or klasa_betonu_z_nazwy(str(raw["mat"]))
        if not kl and prz is not None and prz.ma_oznaczona_konstr:
            mt = m.material(prz.warstwy[prz.idx_konstr].mat)
            kl = klasa_betonu_z_nazwy(mt.nazwa if mt else None) or klasa_betonu_z_nazwy(prz.warstwy[prz.idx_konstr].mat)
        # rola, kategoria, odsłonięcie
        if e.typ == "strop":
            e.rola, e.kat_q = "strop", "strop"
        elif e.typ == "dach":
            e.rola, e.kat_q = "dach", ("taras" if prz is not None and prz.typ == "taras" else "dach")
        else:
            e.kat_q = "taras" if (prz is not None and prz.typ == "taras") else "dach"
        e.odsloniety = e.typ != "strop" and not self._przykryty(e)
        if e.typ == "wspornik":
            e.rola = "wspornik" if e.odsloniety else "wspornik_oslon"
        if e.rola == "wspornik_oslon":
            ex, kl_def = "XC3", p.beton_ekspozycja.get("XC3", "C30/37")
        else:
            ex, kl_def = p.beton_dla(e.rola)
        if not kl:
            kl = kl_def
            self.brak(f"{e.id}: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto {kl} ({ex})")
        order = list(TABL_BETON)
        if order.index(kl) < order.index(p.beton_ekspozycja.get(ex, "C20/25")):
            self.log(f"{e.id}: beton {kl} niższy niż wskazany dla ekspozycji {ex} ({p.beton_ekspozycja.get(ex)}) — PN-EN 1992-1-1 zał. E")
        e.beton = Beton.z_parametrow(kl, p)
        e.ekspozycja = ex
        return e

    def _ma_wlasne_podpory(self, e: ElementPlyty) -> bool:
        """Czy płyta ma podpory we własnym obrysie (belki, słupy, ściany pod wnętrzem płyty)."""
        wn = e.poly_full.buffer(-0.1)
        for b in self.m.belki():
            if abs(float(b["spod"]) + float(b["h"]) - e.spod) < TOL_Z and LineString([tuple(b["os"][0]), tuple(b["os"][1])]).intersects(wn):
                return True
        for c in self.m.slupy():
            if abs(float(c["z_do"]) - e.spod) < TOL_Z and e.poly_full.buffer(0.05).contains(Point(*c["xy"])):
                return True
        for w in self.m.sciany():
            if w.typ in TYPY_NOSNE and abs(w.z_do - e.spod) < TOL_Z and LineString([tuple(w.p1), tuple(w.p2)]).intersects(wn):
                return True
        return False

    def _przykryty(self, e: ElementPlyty) -> bool:
        c = e.poly_full.representative_point()
        for pl in self.m.plyty():
            if str(pl["id"]) == e.id:
                continue
            if pl["spod"] > e.top + 0.3 and pl["poly_full"].buffer(0.05).contains(c):
                return True
        return False

    def _grupy_plyt(self):
        els = [self._element_plyty(pl) for pl in self.m.plyty()]
        n = len(els)
        par = list(range(n))

        def fnd(i):
            while par[i] != i:
                par[i] = par[par[i]]
                i = par[i]
            return i
        oddzielne = {i for i, e in enumerate(els) if e.typ == "wspornik" and e.raw.get("lacznik_termiczny")
                     and self._ma_wlasne_podpory(e)}
        for i in range(n):
            for j in range(i + 1, n):
                if i in oddzielne or j in oddzielne:
                    continue
                if abs(els[i].wierzch - els[j].wierzch) < 0.03 and els[i].poly_full.distance(els[j].poly_full) < 0.05:
                    par[fnd(i)] = fnd(j)
        for i in oddzielne:
            self.log(f"{els[i].id}: płyta z łącznikiem termoizolacyjnym i własnymi podporami (belki/słupy) — łącznik przyjęto "
                     "jako przegubowy (przenoszący siłę poprzeczną, typ „Q”), płyta liczona osobno, podparta na krawędzi przy ścianie [ZAŁ].")
        grp = {}
        for i in range(n):
            grp.setdefault(fnd(i), []).append(els[i])
        for k, el in enumerate(sorted(grp.values(), key=lambda L: -L[0].wierzch)):
            g = Grupa(k, el)
            g.poly = unary_union([e.poly for e in el]).buffer(0)
            if not isinstance(g.poly, Polygon):
                g.poly = max(g.poly.geoms, key=lambda q: q.area)
                self.log(f"Grupa płyt {g.nazwa}: obszar niespójny — analizowana największa część")
            g.wierzch = float(np.mean([e.wierzch for e in el]))
            self.grupy.append(g)

    def _snap_linia(self, ln: LineString, poly: Polygon) -> list[LineString]:
        """Linia podpory przycięta do płyty; gdy leży poza płytą (oparcie na krawędzi) — przesunięta na krawędź."""
        out = []
        pieces = ln.intersection(poly.buffer(0.3))
        geoms = [pieces] if isinstance(pieces, LineString) else list(getattr(pieces, "geoms", []))
        for g in geoms:
            if not isinstance(g, LineString) or g.length < 0.15:
                continue
            mid = g.interpolate(0.5, normalized=True)
            if not poly.buffer(1e-6).contains(mid):
                (x0, y0), (x1, y1) = g.coords[0], g.coords[-1]
                L = math.hypot(x1 - x0, y1 - y0)
                nx, ny = -(y1 - y0) / L, (x1 - x0) / L
                d = poly.exterior.distance(mid)
                cand = []
                for sg in (1, -1):
                    gg = LineString([(x0 + sg * nx * d, y0 + sg * ny * d), (x1 + sg * nx * d, y1 + sg * ny * d)])
                    cand.append(gg)
                g = max(cand, key=lambda q: q.intersection(poly.buffer(1e-6)).length)
            cut = g.intersection(poly.buffer(1e-6))
            for c in ([cut] if isinstance(cut, LineString) else list(getattr(cut, "geoms", []))):
                if isinstance(c, LineString) and c.length >= 0.15:
                    out.append(c)
        return out

    def _podpory_grupy(self, g: Grupa):
        m = self.m
        spody = [e.spod for e in g.el]
        tops = [e.wierzch for e in g.el]
        g.podp_l, g.podp_p = [], []
        g.sciany_pod = []
        for w in m.sciany():
            if w.typ not in TYPY_NOSNE:
                continue
            if not any(abs(w.z_do - s) < TOL_Z for s in spody):
                continue
            t = w.warstwa_konstr.d if hasattr(w.warstwa_konstr, "d") else 0.2
            ln = LineString([tuple(w.p1), tuple(w.p2)])
            if ln.distance(g.poly) > t / 2 + 0.02:
                continue
            for k, piece in enumerate(self._snap_linia(ln, g.poly)):
                sid = w.id if k == 0 else f"{w.id}#{k + 1}"
                g.podp_l.append(PodporaLiniowa(sid, piece, "przegub", "sciana"))
                g.sciany_pod.append((sid, w))
        g.belki = []
        linie_scian = [(sp.linia, ww.warstwa_konstr.d) for (sid_, ww), sp in zip(g.sciany_pod, g.podp_l)]
        for b in m.belki():
            top = float(b["spod"]) + float(b["h"])
            if not (any(abs(top - s) < TOL_Z for s in spody) or any(abs(top - t) < TOL_Z for t in tops)):
                continue
            ln = LineString([tuple(b["os"][0]), tuple(b["os"][1])])
            if ln.distance(g.poly) > float(b["b"]) / 2 + 0.02:
                continue
            for k, piece in enumerate(self._snap_linia(ln, g.poly)):
                piece = self._dociagnij_do_scian(piece, linie_scian)
                sid = str(b["id"]) if k == 0 else f"{b['id']}#{k + 1}"
                g.podp_l.append(PodporaLiniowa(sid, piece, "przegub", "belka"))
                g.belki.append((sid, b))
        for c in m.slupy():
            if any(abs(float(c["z_do"]) - s) < TOL_Z for s in spody) and g.poly.buffer(0.05).contains(Point(*c["xy"])):
                g.podp_p.append(PodporaPunktowa(str(c["id"]), tuple(c["xy"])))

    @staticmethod
    def _dociagnij_do_scian(piece: LineString, linie_scian: list) -> LineString:
        """Koniec linii belki leżący przy ścianie (≤ t/2 + 0,25 m) przedłużony/skrócony do osi ściany — belka oparta na
        ścianie (unika sztucznej pary reakcji dwóch bliskich podpór sztywnych w MES)."""
        (x0, y0), (x1, y1) = piece.coords[0], piece.coords[-1]
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        pts = [np.array([x0, y0]), np.array([x1, y1])]
        for k in (0, 1):
            for lw, t in linie_scian:
                if lw.distance(Point(*pts[k])) > t / 2 + 0.25:
                    continue
                (a0, b0), (a1, b1) = lw.coords[0], lw.coords[-1]
                dwx, dwy = a1 - a0, b1 - b0
                den = ux * dwy - uy * dwx
                if abs(den) < 1e-9:
                    continue
                tpar = ((a0 - pts[k][0]) * dwy - (b0 - pts[k][1]) * dwx) / den
                pts[k] = pts[k] + tpar * np.array([ux, uy])
                break
        return LineString([tuple(pts[0]), tuple(pts[1])])

    def _komorki(self, g: Grupa):
        """Pola płyty (komórki siatki linii podpór) z klasyfikacją krawędzi S/U/W."""
        xs, ys = set(), set()
        for s in g.podp_l:
            (x0, y0), (x1, y1) = s.linia.coords[0], s.linia.coords[-1]
            if abs(x1 - x0) < 1e-3:
                xs.add(round(x0, 4))
            elif abs(y1 - y0) < 1e-3:
                ys.add(round(y0, 4))
        minx, miny, maxx, maxy = g.poly.bounds
        xs |= {minx, maxx}
        ys |= {miny, maxy}

        def merge(v):
            v = sorted(v)
            out = [v[0]]
            for a in v[1:]:
                if a - out[-1] > 0.05:
                    out.append(a)
            return out
        xs, ys = merge(xs), merge(ys)
        g.xl, g.yl = xs, ys
        sup_u = unary_union([s.linia for s in g.podp_l]).buffer(0.03) if g.podp_l else Polygon()
        cells = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                r = box(xs[i], ys[j], xs[i + 1], ys[j + 1])
                a = r.intersection(g.poly).area
                ok = a >= 0.8 and min(xs[i + 1] - xs[i], ys[j + 1] - ys[j]) >= 0.5
                cells.append({"i": i, "j": j, "rect": r, "x0": xs[i], "x1": xs[i + 1], "y0": ys[j], "y1": ys[j + 1],
                              "lx": xs[i + 1] - xs[i], "ly": ys[j + 1] - ys[j], "wazna": ok, "pelna": a / r.area if r.area else 0})
        valid = {(c["i"], c["j"]): c for c in cells if c["wazna"]}
        # scalanie komórek, między którymi brak podpory (< 20 % długości wspólnej krawędzi) → pola płyty
        par = {k: k for k in valid}

        def fnd(k):
            while par[k] != k:
                par[k] = par[par[k]]
                k = par[k]
            return k
        for (i, j), c in valid.items():
            for di, dj in ((1, 0), (0, 1)):
                nb = valid.get((i + di, j + dj))
                if nb is None:
                    continue
                e = LineString([(c["x1"], c["y0"]), (c["x1"], c["y1"])]) if di else LineString([(c["x0"], c["y1"]), (c["x1"], c["y1"])])
                cov = e.intersection(sup_u).length / e.length if e.length else 0
                if cov < 0.2:
                    par[fnd((i, j))] = fnd((i + di, j + dj))
        grupy_k = {}
        for k in valid:
            grupy_k.setdefault(fnd(k), []).append(valid[k])
        pola = []
        for lst in grupy_k.values():
            rect = unary_union([c["rect"] for c in lst])
            x0, y0, x1, y1 = rect.bounds
            pc = {"i": min(c["i"] for c in lst), "j": min(c["j"] for c in lst), "rect": rect, "x0": x0, "x1": x1, "y0": y0,
                  "y1": y1, "lx": x1 - x0, "ly": y1 - y0, "wazna": True,
                  "pelna": rect.intersection(g.poly).area / box(x0, y0, x1, y1).area,
                  "prostokat": abs(rect.area - (x1 - x0) * (y1 - y0)) < 1e-6, "n_kom": len(lst)}
            pola.append(pc)
        pmap = {}
        for pc in pola:
            for i in range(len(xs) - 1):
                for j in range(len(ys) - 1):
                    if (i, j) in valid and pc["rect"].buffer(-1e-6).contains(valid[(i, j)]["rect"].centroid):
                        pmap[(i, j)] = pc
        for c in pola:
            br = ""
            for (a, b_), side in ((((c["x0"], c["y0"]), (c["x0"], c["y1"])), "L"), (((c["x1"], c["y0"]), (c["x1"], c["y1"])), "P"),
                                  (((c["x0"], c["y0"]), (c["x1"], c["y0"])), "D"), (((c["x0"], c["y1"]), (c["x1"], c["y1"])), "G")):
                e = LineString([a, b_])
                cov = e.intersection(sup_u).length / e.length if e.length else 0
                off = {"L": (-0.2, 0), "P": (0.2, 0), "D": (0, -0.2), "G": (0, 0.2)}[side]
                probe = e.interpolate(0.5, normalized=True)
                q = Point(probe.x + off[0], probe.y + off[1])
                nb = any(o is not c and o["rect"].buffer(0.01).contains(q) for o in pola)
                if cov >= 0.8:
                    br += "U" if nb else "S"
                else:
                    br += "W"
            c["brzegi"] = br
            c["tablice"] = ("W" not in br) and c["pelna"] >= 0.97 and c["prostokat"]
        pola.sort(key=lambda c: (c["j"], c["i"]))
        for k, c in enumerate(pola):
            c["id"] = f"P{k + 1}"
            c["parzystosc"] = (c["i"] + c["j"]) % 2
        valid = {k: c for k, c in enumerate(pola)}
        g.komorki = [valid[k] for k in sorted(valid)]

    # ---------------- obciążenia na grupie ----------------
    def _obc_na_grupie(self, g: Grupa):
        """Ścianki działowe i ściany nośne bez podparcia poniżej, słupy stojące na płycie — obciążenia grupy."""
        m, p = self.m, self.p
        self._podpory_grupy(g)
        for w in m.sciany():
            if abs(w.z_od - g.wierzch) > TOL_Z:
                continue
            ln = LineString([tuple(w.p1), tuple(w.p2)])
            if ln.distance(g.poly) > 0.05:
                continue
            gm2, _ = self._ciezar_sciany(w)
            h = w.z_do - w.z_od
            A_otw = sum(o.szer * max(min(o.z1, w.z_do) - max(o.z0, w.z_od), 0) for o in m.otwory(sciana=w.id))
            gl = gm2 * (w.L * h - A_otw) / w.L
            if w.typ == "scianka_dzialowa":
                eq = zastepcze_dzialowe(gl)
                if eq is None:
                    g.linie.append((ln, "G", gl, f"ścianka działowa {w.id}: {f(gl, 2)} kN/m (> 3 kN/m — obciążenie liniowe, 6.3.1.2(9))"))
                else:
                    g.linie.append((None, "QA", eq, f"ścianka działowa {w.id}: {f(gl, 2)} kN/m → zastępcze {f(eq, 1)} kN/m² (6.3.1.2(8))"))
            else:
                below = self._sciana_ponizej(w)
                if below is None:
                    pr = self.prof.get(w.id)
                    if pr is not None:
                        for c in pr["dol"].przypadki():
                            q = pr["dol"].calka(c) / w.L
                            if abs(q) > 1e-9:
                                g.linie.append((ln, c, q, f"ściana nośna {w.id} bez podparcia poniżej — średnio {f(q, 2)} kN/m ({c})"))
                    self.log(f"Ściana nośna {w.id} stoi na płycie {g.nazwa} bez ściany poniżej — obciążenie liniowe płyty; "
                             "sprawdzić podciąg/żebro [WYMAGA ANALIZY].")
        for z, ln, RG, RQ, opis in getattr(self, "_pend_linie", []):
            if abs(z - g.wierzch) < 0.35 and ln.distance(g.poly) < 0.05:
                g.linie.append((ln, "G", RG, f"{opis}: {f(RG, 2)} kN/m (G)"))
                g.linie.append((ln, "QA", RQ, f"{opis}: {f(RQ, 2)} kN/m (Q)"))
        for sid, N in self.slupy_N.items():
            c = next((c for c in m.slupy() if str(c["id"]) == sid), None)
            if c is None or abs(float(c["z_od"]) - g.wierzch) > TOL_Z or not g.poly.contains(Point(*c["xy"])):
                continue
            for cs, v in N.items():
                g.punkty.append((tuple(c["xy"]), cs, v, f"słup {sid}"))

    def _sciana_ponizej(self, w):
        for v in self.m.sciany():
            if v.typ not in TYPY_NOSNE or v.id == w.id or v.z_do > w.z_od + TOL_Z or v.z_do < w.z_od - 0.6:
                continue
            if self._wspolliniowe(w, v) > 0.5 * w.L:
                return v
        return None

    @staticmethod
    def _wspolliniowe(a, b, tol: float = 0.06) -> float:
        """Długość wspólnego odcinka osi (gdy współliniowe), 0 w przeciwnym razie."""
        la = LineString([tuple(a.p1), tuple(a.p2)])
        if la.distance(Point(*b.p1)) > tol or la.distance(Point(*b.p2)) > tol:
            lb = LineString([tuple(b.p1), tuple(b.p2)])
            if lb.distance(Point(*a.p1)) > tol or lb.distance(Point(*a.p2)) > tol:
                return 0.0
        s = sorted([a.st(b.p1)[0], a.st(b.p2)[0]])
        return max(0.0, min(s[1], a.L) - max(s[0], 0.0))

    def _ciezar_sciany(self, w) -> tuple[float, ZestawienieStale]:
        kod = w.przegroda.kod if hasattr(w, "przegroda") and hasattr(w.przegroda, "kod") else None
        if kod is None:
            kod = getattr(w, "raw", {}).get("przegroda")
        z = zestawienie_przegrody(self.m, kod, self.p)
        return z.g_k, z

    # ---------------- śnieg ----------------
    def _snieg_grupy(self, g: Grupa, fe: PlytaMES) -> tuple[np.ndarray, np.ndarray, np.ndarray, list]:
        p, m = self.p, self.m
        n = len(fe.els)
        s1 = np.zeros(n)
        s2 = np.zeros(n)
        sb = np.zeros(n)
        wyn = []
        for e in g.el:
            if not e.odsloniety:
                continue
            msk = fe.elementy_w(e.poly_full)
            s1[msk] = self.snieg_rown.s1
            s2[msk] = np.maximum(s2[msk], self.snieg_rown.s1)
            pts = fe.el_c[msk]
            idx = np.nonzero(msk)[0]
            # attyka
            at = e.raw.get("attyka") if isinstance(e.raw.get("attyka"), dict) else None
            if at and float(at.get("wys_nad_pokryciem", 0)) > 0:
                ha = float(at["wys_nad_pokryciem"])
                sa = snieg_attyka(ha, p)
                sa.nazwa += f" — {e.id}"
                wyn.append(sa)
                dist = np.array([e.poly_full.exterior.distance(Point(*c)) for c in pts])
                s2[idx] = np.maximum(s2[idx], sa.profil(dist))
                b2 = snieg_B2_attyka(ha, p)
                if b2 is not None:
                    wyn.append(b2)
                    sb[idx] = np.maximum(sb[idx], b2.profil(dist))
            # uskoki: ściany wyższych części przy krawędzi
            for w in m.sciany():
                if w.z_od > e.top + 0.3 or w.z_do < e.top + 1.0:
                    continue
                ln = LineString([tuple(w.p1), tuple(w.p2)])
                t = w.grubosc if hasattr(w, "grubosc") else 0.3
                if ln.distance(e.poly_full) > t / 2 + 0.35 or e.poly_full.buffer(-0.05).intersects(ln):
                    continue
                gora = [pl for pl in m.plyty() if pl["spod"] >= w.z_do - TOL_Z and pl["poly_full"].buffer(t).intersects(ln)]
                if not gora:
                    continue
                gp = max(gora, key=lambda q: q.get("top_attyki") or q["top"])
                h = (gp.get("top_attyki") or gp["top"]) - e.top
                if h < 0.5:
                    continue
                mid = ln.interpolate(0.5, normalized=True)
                (x0, y0), (x1, y1) = w.p1, w.p2
                L = math.hypot(x1 - x0, y1 - y0)
                nx, ny = -(y1 - y0) / L, (x1 - x0) / L
                c_low = e.poly_full.centroid
                sg = 1 if (c_low.x - mid.x) * nx + (c_low.y - mid.y) * ny > 0 else -1

                def zasieg(poly, kier):
                    ray = LineString([(mid.x, mid.y), (mid.x + kier * nx * 50, mid.y + kier * ny * 50)])
                    it = ray.intersection(poly.buffer(0.02))
                    return it.length if not it.is_empty else 0.0
                b2 = zasieg(e.poly_full, sg)
                b1 = zasieg(gp["poly_full"], -sg)
                if b2 < 0.3 or b1 < 0.3:
                    continue
                su = snieg_uskok(h, b1, b2, p)
                su.nazwa += f" — {e.id} przy ścianie {w.id}"
                wyn.append(su)
                dist = np.maximum(np.array([ln.distance(Point(*c)) for c in pts]) - t / 2, 0.0)
                s2[idx] = np.maximum(s2[idx], su.profil(dist))
                if p.snieg_B2:
                    bb = snieg_B2_uskok(h, b1, b2, p)
                    bb.nazwa += f" — {e.id} przy ścianie {w.id}"
                    wyn.append(bb)
                    sb[idx] = np.maximum(sb[idx], bb.profil(dist))
        return s1, s2, sb, wyn

    # ---------------- MES grupy ----------------
    def _analiza_grupy(self, g: Grupa):
        p, m = self.p, self.m
        self._komorki(g)
        e0 = max(g.el, key=lambda e: e.poly.area)
        E0 = e0.beton.E_cm * 1000
        strefy = [(e.poly_full, e.h, e.beton.E_cm * 1000) for e in g.el]
        try:
            fe = PlytaMES(g.poly, e0.h, E0, p.nu_beton, g.podp_l, g.podp_p, siatka=p.siatka_mes,
                          linie_siatki=(g.xl, g.yl), strefy=strefy)
        except BladDanych as ex:
            self.log(f"Grupa płyt {g.nazwa}: MES niewykonalny ({ex}) — pominięto")
            return
        g.fe = fe
        for u in fe.uwagi:
            self.log(f"{g.nazwa}: {u}")
        n = len(fe.els)
        qG = np.zeros(n)
        qA = np.zeros(n)
        qH = np.zeros(n)
        for e in g.el:
            msk = fe.elementy_w(e.poly_full)
            qG[msk] = e.zest.g_k
            if e.kat_q in ("strop", "taras"):
                qA[msk] = obciazenie_uzytkowe(e.kat_q, p).q_k
            else:
                qH[msk] = obciazenie_uzytkowe("dach", p).q_k
        # zastępcze od ścianek lekkich (QA) — na elementy stropów
        for ln, cs, q, opis in g.linie:
            if ln is None and cs == "QA":
                for e in g.el:
                    if e.kat_q == "strop":
                        qA[fe.elementy_w(e.poly_full)] = obciazenie_uzytkowe("strop", p).q_k + q
        s1, s2, sb, sn_wyn = self._snieg_grupy(g, fe)
        g.snieg = sn_wyn
        # komórki elementów
        cell_of = np.full(n, -1)
        for k, c in enumerate(g.komorki):
            r = c["rect"].buffer(1e-9)
            for ei, cc in enumerate(fe.el_c):
                if cell_of[ei] < 0 and r.contains(Point(*cc)):
                    cell_of[ei] = k
        if g.komorki:
            cent = np.array([[c["rect"].centroid.x, c["rect"].centroid.y] for c in g.komorki])
            for ei in np.nonzero(cell_of < 0)[0]:
                cell_of[ei] = int(np.argmin(np.hypot(*(cent - fe.el_c[ei]).T)))
        g.cell_of = cell_of
        par = np.array([g.komorki[k]["parzystosc"] if k >= 0 else 0 for k in cell_of])

        def lin(cs, mask_par=None):
            out = []
            for ln, c, q, _ in g.linie:
                if ln is None or c != cs:
                    continue
                if mask_par is not None:
                    mid = ln.interpolate(0.5, normalized=True)
                    k = self._komorka_punktu(g, (mid.x, mid.y))
                    if k is not None and g.komorki[k]["parzystosc"] != mask_par:
                        continue
                out.append((ln, q))
            return out

        def pkt(cs):
            return [(xy, P) for xy, c, P, _ in g.punkty if c == cs]
        cases = {"G": fe.wektor(qG, lin("G"), pkt("G"))}
        if qA.any() or lin("QA") or pkt("QA"):
            cases["QA"] = fe.wektor(qA, lin("QA"), pkt("QA"))
            if len(g.komorki) > 1:
                cases["QA_pA"] = fe.wektor(np.where(par == 0, qA, 0), lin("QA", 0))
                cases["QA_pB"] = fe.wektor(np.where(par == 1, qA, 0), lin("QA", 1))
        for cs in ("H", "S1", "S2", "SB2"):
            arr = {"H": qH, "S1": s1, "S2": s2, "SB2": sb}[cs]
            if arr.any() or lin(cs) or pkt(cs):
                cases[cs] = fe.wektor(arr, lin(cs), pkt(cs))
        g.res = {c: fe.rozwiaz(v) for c, v in cases.items()}
        g.q_el = {"G": qG, "QA": qA, "H": qH, "S1": s1, "S2": s2, "SB2": sb}
        # kombinacje
        odz = [Oddz("G", "G")]
        for c in g.res:
            if c.startswith("QA"):
                odz.append(Oddz(c, "Q", "A", "QA"))
            elif c == "H":
                odz.append(Oddz("H", "Q", "H", "dach"))
            elif c in ("S1", "S2"):
                odz.append(Oddz(c, "Q", "S", "dach"))
            elif c == "SB2":
                odz.append(Oddz("SB2", "A", "S", "dach"))
        kombs = kombinacje(odz, p, "STR") + kombinacje(odz, p, "wyj")
        env = {"dol_x": np.zeros(n), "dol_y": np.zeros(n), "gora_x": np.zeros(n), "gora_y": np.zeros(n)}
        for kb in kombs:
            mm = sum(a * g.res[c].m for c, a in kb.wsp.items() if c in g.res)
            wa = wood_armer(mm)
            env["dol_x"] = np.maximum(env["dol_x"], wa["dol_x"])
            env["dol_y"] = np.maximum(env["dol_y"], wa["dol_y"])
            env["gora_x"] = np.minimum(env["gora_x"], wa["gora_x"])
            env["gora_y"] = np.minimum(env["gora_y"], wa["gora_y"])
        psiA = p.psi_of("A")[2]
        qp = g.res["G"] * 1.0
        if "QA" in g.res:
            qp = qp + g.res["QA"] * psiA
        env["qp"] = qp
        env["kombinacje"] = kombs
        rmax = {}
        for sp in g.podp_l:
            best = 0.0
            for kb in kombs:
                rr = sum(a * g.res[c].R for c, a in kb.wsp.items() if c in g.res)
                best = max(best, fe.reakcja_max(WynikMES(None, None, rr), sp.id, 0.5))
            rmax[sp.id] = best
        env["rmax"] = rmax
        g.env = env
        g.odz = odz
        self._pozycje_plyt(g)

    def _komorka_punktu(self, g: Grupa, xy) -> int | None:
        for k, c in enumerate(g.komorki):
            if c["rect"].buffer(1e-6).contains(Point(*xy)):
                return k
        return None

    # ---------------- wymiarowanie płyt ----------------
    def _pozycje_plyt(self, g: Grupa):
        p, fe, env = self.p, g.fe, g.env
        wa_qp = wood_armer(env["qp"].m)
        rys_plan = None
        if self.rys_dir:
            from . import rysunki
            rys_plan = rysunki.rys_plyta(self, g, self.rys(f"plyta_{g.idx}_{_slug(g.nazwa)}.png"))
        for e in g.el:
            poz = Pozycja("", e.id, {"strop": "Strop", "dach": "Stropodach / dach", "wspornik": "Płyta wspornikowa"}[e.typ]
                          + f" {e.id}", "plyta")
            poz.dane["grupa"] = g.nazwa
            poz.opis.append(
                f"Płyta żelbetowa monolityczna gr. h = {f(e.h * 100, 0)} cm, wierzch konstrukcji {f(e.wierzch, 3)} m, "
                f"beton {e.beton.klasa} (ekspozycja {e.ekspozycja}), stal {p.stal_zbr}. Pole płyty {f(e.poly.area, 2)} m². "
                + (f"Analiza wspólna z: {g.nazwa} (płyty połączone na jednym poziomie — ciągłość nad podporami/łącznikami). "
                   if len(g.el) > 1 else "")
                + "Schemat: płyta na podporach liniowych (ściany, belki — podpory sztywne, przegubowe) i punktowych (słupy); "
                  "statyka — MES płytowy (elementy ACM, siatka " + f(p.siatka_mes * 100, 0) + " cm, obwiednia kombinacji "
                  "6.10a/6.10b i obciążeń szachownicowych pól), sprawdzenie pól prostokątnych metodą tablic (współczynniki MRS).")
            sup = [s for s in g.podp_l if s.linia.distance(e.poly_full) < 0.05]
            poz.opis.append("Podpory: " + ", ".join(
                f"{s.id} ({'ściana' if s.rodzaj == 'sciana' else 'belka'})" for s in sup) +
                (", słupy: " + ", ".join(s.id for s in g.podp_p if e.poly_full.buffer(0.05).contains(Point(*s.xy))) if g.podp_p else ""))
            if e.raw.get("lacznik_termiczny"):
                poz.uwagi.append("Połączenie z płytą stropu przez łącznik termoizolacyjny (ETA) — dobór łącznika na siły "
                                 "m_Ed, v_Ed z niniejszej pozycji wg dokumentu producenta (W-272).")
            poz.obciazenia.append(f"**Obciążenia stałe — {e.zest.tytul}**\n\n" + e.zest.md(p))
            uz = obciazenie_uzytkowe(e.kat_q, p)
            txt = [f"Obciążenie użytkowe: {uz.opis}: q_k = {f(uz.q_k, 2)} kN/m², Q_k = {f(uz.Q_k, 1)} kN, ψ₀/ψ₁/ψ₂ = "
                   f"{'/'.join(f(x, 1) for x in uz.psi)} ({uz.zrodlo})."]
            for ln, cs, q, opis in g.linie:
                if ln is None or ln.distance(e.poly_full) < 0.05:
                    txt.append(f"Obciążenie dodatkowe ({cs}): {opis}.")
            for xy, cs, P, opis in g.punkty:
                if e.poly_full.buffer(0.05).contains(Point(*xy)):
                    txt.append(f"Siła skupiona ({cs}): {opis} — {f(P, 2)} kN.")
            if e.odsloniety:
                txt.append(f"Śnieg: s = {f(self.snieg_rown.s1, 3)} kN/m² (przypadek równomierny) oraz zaspy (poniżej).")
            poz.obciazenia.append("\n".join(f"- {t}" for t in txt))
            sn_e = [sn for sn in g.snieg if e.id in sn.nazwa]
            poz.wyniki += sn_e
            if sn_e and self.rys_dir:
                from . import rysunki
                poz.rysunki += rysunki.rys_zaspy(sn_e, self.rys(f"zaspy_{_slug(e.id)}.png"))
            if rys_plan:
                poz.rysunki += rys_plan
            # komórki elementu
            cells = [k for k, c in enumerate(g.komorki) if e.poly_full.buffer(-0.01).contains(c["rect"].centroid)
                     or (e.poly_full.intersection(c["rect"]).area > 0.5 * c["rect"].intersection(g.poly).area)]
            if not cells:
                cells = sorted({int(g.cell_of[i]) for i in np.nonzero(fe.elementy_w(e.poly_full))[0]})
            rows = []
            best = None
            prety = []
            c_nom = zelbet.otulina(e.ekspozycja, 10, p).c_nom
            for k in cells:
                c = g.komorki[k]
                msk = (g.cell_of == k) & fe.elementy_w(e.poly_full.buffer(0.01))
                if not msk.any():
                    continue
                r = self._wymiaruj_pole(g, e, c, msk, c_nom, wa_qp)
                rows.append(r["wiersz"])
                prety += r["prety"]
                poz.dane.setdefault("pola", []).append(r["dane"])
                if best is None or r["M_max"] > best["M_max"]:
                    best = r
                poz.podpozycje.append(Pozycja(f"{c['id']}", c["id"], f"Pole {c['id']}", "pole", wyniki=r["wyniki"]))
            if best is not None:
                poz.wyniki.extend(best["wyniki_pelne"])
                poz.dane["pole_miarodajne"] = best["dane"]["pole"]
            poz.tabele.append("**Zestawienie wymiarowania pól płyty** (M [kNm/m] — obwiednia ULS, Wood–Armer, poza strefami "
                              "narożnymi; „tabl.” — metoda tablic, jeżeli stosowalna; góra — nad podporami; naroża — strefy "
                              "0,2·l_min × 0,2·l_min przy narożach podpartych, zbrojenie górą i dołem na moment skręcający)\n\n" + tabela(
                ["Pole", "l_x × l_y [m]", "Brzegi", "M_x,dół [kNm/m] MES / tabl.", "Zbroj. x dół", "M_y,dół MES / tabl.",
                 "Zbroj. y dół", "M_x,góra", "Zbroj. x góra", "M_y,góra", "Zbroj. y góra", "Naroża M / zbroj.",
                 "w / w_lim [mm]", "η_max"], rows))
            # EQU wsporników
            if e.typ == "wspornik":
                self._equ_wspornika(g, e, poz)
            # reakcje na podporach (dla łączników/ścian)
            rr = []
            for s in sup:
                Rk = {c: fe.reakcja(g.res[c], s.id) for c in g.res}
                ss, rG = fe.reakcje_liniowe(g.res["G"], s.id)
                rQ = fe.reakcje_liniowe(g.res["QA"], s.id)[1] if "QA" in g.res else np.zeros_like(rG)
                rows_r = [s.id, (s.linia.length, 2), (Rk.get("G", 0), 1), (sum(v for c, v in Rk.items() if c in ("QA",)), 1),
                          (float(np.nanmax(rG)) if len(rG) else 0, 2), (float(np.nanmax(rQ)) if len(rQ) else 0, 2)]
                rr.append(rows_r)
            if rr:
                poz.tabele.append("**Reakcje podporowe (charakterystyczne, cała grupa płyt)**\n\n" + tabela(
                    ["Podpora", "Długość [m]", "ΣR_G [kN]", "ΣR_Q [kN]", "max r_G [kN/m]", "max r_Q [kN/m]"], rr))
            poz.prety = prety
            wmax = max((d["w"] for d in poz.dane.get("pola", [])), default=0)
            poz.przyjeto.append(f"Płyta gr. {f(e.h * 100, 0)} cm z betonu {e.beton.klasa}, stal {p.stal_zbr}, otulenie c_nom = "
                                f"{f(c_nom, 0)} mm; zbrojenie wg zestawienia pól (dołem siatka w obu kierunkach, górą nad podporami).")
            poz.przyjeto.append(f"Maks. ugięcie długotrwałe ≈ {f(wmax, 1)} mm.")
            self.pos_plyty.append(poz)

    def _wymiaruj_pole(self, g: Grupa, e: ElementPlyty, c: dict, msk: np.ndarray, c_nom: float, wa_qp: dict) -> dict:
        p, fe, env = self.p, g.fe, g.env
        h = e.h
        beton = e.beton
        fi0 = 10
        dx = h - c_nom / 1000 - fi0 / 2000
        dy = dx - fi0 / 1000
        # strefy narożne (0,2·l_min przy narożach pola między dwiema krawędziami podpartymi) — moment skręcający
        a_n = 0.2 * min(c["lx"], c["ly"])
        br0 = c.get("brzegi", "WWWW")
        naroza = []
        for (xx, bx_), (yy, by_) in (((c["x0"], br0[0]), (c["y0"], br0[2])), ((c["x1"], br0[1]), (c["y0"], br0[2])),
                                     ((c["x1"], br0[1]), (c["y1"], br0[3])), ((c["x0"], br0[0]), (c["y1"], br0[3]))):
            if bx_ in "SU" and by_ in "SU":
                naroza.append(box(xx - a_n, yy - a_n, xx + a_n, yy + a_n))
        nz = np.zeros(len(fe.els), bool)
        if naroza:
            U = unary_union(naroza)
            nz = np.array([U.contains(Point(*cc)) for cc in fe.el_c])
        mg = msk & ~nz if (msk & ~nz).any() else msk
        Mx = float(env["dol_x"][mg].max())
        My = float(env["dol_y"][mg].max())
        Mgx = float(env["gora_x"][mg].min())
        Mgy = float(env["gora_y"][mg].min())
        mn = msk & nz
        M_nar = float(max(np.maximum(env["dol_x"][mn], env["dol_y"][mn]).max(),
                          (-np.minimum(env["gora_x"][mn], env["gora_y"][mn])).max())) if mn.any() else 0.0
        Mx_t = My_t = None
        tab_wyn = None
        if c["tablice"]:
            gk = float(np.mean(g.q_el["G"][msk]))
            # ścianki działowe (obciążenia liniowe G) jako obciążenie zastępcze równomierne pola — tylko do porównania
            gl = sum(ln.intersection(c["rect"]).length * q for ln, cs_, q, _ in g.linie if ln is not None and cs_ == "G")
            g_dz = gl / c["rect"].intersection(g.poly).area if gl else 0.0
            gk += g_dz
            qk = float(np.mean(g.q_el["QA"][msk])) + float(np.mean(np.maximum(g.q_el["H"][msk], g.q_el["S2"][msk])))
            psi0 = 0.7
            a = (p.gG_sup * gk, p.gQ * psi0 * qk)
            b = (p.xi * p.gG_sup * gk, p.gQ * qk)
            gd, qd = a if sum(a) >= sum(b) else b
            pc = PoleCiagle(c["lx"], c["ly"], c["brzegi"], gd, qd, p.nu_beton)
            Mx_t, My_t = pc.mx, pc.my
            tab_wyn = Wynik(nazwa=f"Sprawdzenie metodą tablic — pole {c['id']} ({f(c['lx'])} × {f(c['ly'])} m, brzegi {c['brzegi']})")
            if g_dz:
                tab_wyn.krok("Obciążenie liniowe ścianek na polu jako równomierne zastępcze [UPR — tylko porównanie]",
                             "g_dz = Σ(g_l·l)/A", "", g_dz, "kN/m²", nd=3)
            tab_wyn.krok("Obciążenia obliczeniowe (miarodajne z 6.10a/6.10b)", "g_d; q_d", f"g_k = {f(gk, 3)}, q_k = {f(qk, 3)} kN/m²",
                         f"{f(gd, 3)}; {f(qd, 3)}", "kN/m²")
            ar, ss = pc.wsp_rzecz, pc.wsp_ssss
            tab_wyn.krok(f"Współczynniki (brzegi {c['brzegi']}; x=0, x=l_x, y=0, y=l_y; S — podparta, U — utwierdzona)",
                         "α_x; α_y; β_x; β_y", "", f"{f(ar.alfa_x, 4)}; {f(ar.alfa_y, 4)}; {f(min(ar.beta_x), 4)}; {f(min(ar.beta_y), 4)}",
                         zrodlo="MRS (odpowiednik tablic Czernego), ν = " + f(p.nu_beton, 1))
            tab_wyn.krok("Współczynniki płyty swobodnie podpartej (SSSS)", "α_x⁰; α_y⁰", "", f"{f(ss.alfa_x, 4)}; {f(ss.alfa_y, 4)}")
            tab_wyn.krok("Moment przęsłowy x", "M_x = [α_x·(g_d + q_d/2) + α_x⁰·q_d/2]·l_x²",
                         f"[{f(ar.alfa_x, 4)}·{f(gd + qd / 2, 3)} + {f(ss.alfa_x, 4)}·{f(qd / 2, 3)}]·{f(c['lx'])}²", Mx_t, "kNm/m")
            tab_wyn.krok("Moment przęsłowy y", "M_y = [α_y·(g_d + q_d/2) + α_y⁰·q_d/2]·l_x²",
                         f"[{f(ar.alfa_y, 4)}·{f(gd + qd / 2, 3)} + {f(ss.alfa_y, 4)}·{f(qd / 2, 3)}]·{f(c['lx'])}²", My_t, "kNm/m")
            mxp = min(pc.mx_podp)
            myp = min(pc.my_podp)
            if mxp < 0 or myp < 0:
                tab_wyn.krok("Momenty podporowe (utwierdzenie, g_d + q_d)", "M_x,p; M_y,p", "", f"{f(mxp, 2)}; {f(myp, 2)}", "kNm/m")
            tab_wyn.krok("Porównanie z MES (M_x; M_y dół, poza narożami)", "M_MES/M_tabl", "",
                         f"{f(Mx / Mx_t if Mx_t else 0, 2)}; {f(My / My_t if My_t else 0, 2)}")
            tab_wyn.krok("Przyjęto do wymiarowania", "M_Ed = max(M_MES; M_tabl)", "", f"{f(max(Mx, Mx_t), 2)}; {f(max(My, My_t), 2)}", "kNm/m")
            Mgx = min(Mgx, mxp)
            Mgy = min(Mgy, myp)
        MxD = max(Mx, Mx_t or 0)
        MyD = max(My, My_t or 0)
        smax = zelbet.smax_plyta(h, True, True)
        zx, fx, sx, Ax = zelbet.wymiaruj_plyte(MxD, h, dx, beton, self.stal, smax, nazwa=f"Pole {c['id']} — zginanie dół, kierunek x")
        zy, fy, sy, Ay = zelbet.wymiaruj_plyte(MyD, h, dy, beton, self.stal, smax, nazwa=f"Pole {c['id']} — zginanie dół, kierunek y")
        # góra: gdy brak momentu ujemnego przy krawędzi swobodnie podpartej — min. 25 % przęsła (9.3.1.2(2))
        Mgx_d = min(Mgx, -0.25 * MxD if "S" in c["brzegi"][:2] else 0.0)
        Mgy_d = min(Mgy, -0.25 * MyD if "S" in c["brzegi"][2:] else 0.0)
        zgx, fgx, sgx, Agx = zelbet.wymiaruj_plyte(abs(Mgx_d), h, dx, beton, self.stal, smax, nazwa=f"Pole {c['id']} — zginanie góra, x")
        zgy, fgy, sgy, Agy = zelbet.wymiaruj_plyte(abs(Mgy_d), h, dy, beton, self.stal, smax, nazwa=f"Pole {c['id']} — zginanie góra, y")
        zn = None
        if M_nar > 0:
            zn, fn, sn_, An = zelbet.wymiaruj_plyte(M_nar, h, dy, beton, self.stal, smax,
                                                    nazwa=f"Pole {c['id']} — zbrojenie narożne (góra i dół, strefy {f(a_n)} × {f(a_n)} m)")
        # ścinanie — maks. reakcja podpór przyległych
        vmax = 0.0
        for s in g.podp_l:
            if s.linia.distance(c["rect"]) > 0.05:
                continue
            both = sum(1 for cc in g.komorki if s.linia.distance(cc["rect"]) < 0.05 and cc is not c) > 0
            vmax = max(vmax, g.env["rmax"].get(s.id, 0.0) * (0.6 if both else 1.0))
        for s in g.podp_p:
            if c["rect"].buffer(0.05).contains(Point(*s.xy)):
                self.log(f"{e.id}: podpora punktowa {s.id} w polu {c['id']} — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]")
        sc = zelbet.scinanie_bez_zbrojenia(vmax, 1.0, dx, min(Ax, Agx if Agx > 0 else Ax), beton,
                                           nazwa=f"Pole {c['id']} — ścinanie (maks. reakcja podpory, [UPR] 0,6·r przy podporze pośredniej)")
        # ugięcie
        wq = float(env["qp"].w[np.unique(fe.el_nodes[msk].ravel())].max())
        EI = e.beton.E_cm * 1000 * h ** 3 / 12
        lmin = min(c["lx"], c["ly"])
        kier = "x" if c["lx"] <= c["ly"] else "y"
        Mqp = float(wa_qp["dol_" + kier][msk].max())
        As_k = Ax if kier == "x" else Ay
        Asr_k = zx.As_req if kier == "x" else zy.As_req
        dk = dx if kier == "x" else dy
        br = c["brzegi"]
        kb_ = br[:2] if kier == "x" else br[2:]
        wsp = e.typ == "wspornik" and "W" in br and not self._ma_wlasne_podpory(e)
        if wsp:
            K, L_ref, ksk = 0.4, p.wspornik_L_mnoznik * lmin, 0.5
        else:
            nU = kb_.count("U")
            K = {0: 1.0, 1: 1.3, 2: 1.5}[nU]
            L_ref, ksk = lmin, 0.125
        ug = zelbet.ugiecie_komplet(lmin, K, h, dk, max(Asr_k, 1.0), As_k, beton, Mqp, wq * EI, p, k_skurcz=ksk, L_ref=L_ref,
                                    stal=self.stal, nazwa=f"Pole {c['id']} — ugięcie (l = {f(lmin)} m, K = {f(K, 1)})")
        ry = zelbet.rysy_bez_obliczen(Mqp, 1.0, h, dk, As_k, fx if kier == "x" else fy, sx if kier == "x" else sy, beton,
                                      p.w_max.get(e.ekspozycja, 0.3), nazwa=f"Pole {c['id']} — rysy")
        wyniki = [zx, zy, zgx, zgy] + ([zn] if zn is not None else []) + [sc, ug, ry]
        warunki = [w for r in wyniki for w in r.warunki]
        eta = max((w.eta for w in warunki), default=0)
        wobl = ug.obl.w if hasattr(ug, "obl") else 0
        wiersz = [c["id"], f"{f(c['lx'])} × {f(c['ly'])}", br, f"{f(Mx)} / {f(Mx_t) if Mx_t is not None else '—'}", zx.zbrojenie,
                  f"{f(My)} / {f(My_t) if My_t is not None else '—'}", zy.zbrojenie, (Mgx_d, 2), zgx.zbrojenie, (Mgy_d, 2),
                  zgy.zbrojenie, (f"{f(M_nar)} / {zn.zbrojenie}" if zn is not None else "—"),
                  f"{f(wobl, 1)} / {f(ug.obl.w_dop, 1)}", f"{f(eta * 100, 0)}%" + ("" if eta <= 1 else " ✗")]
        # pręty (orientacyjnie)
        pr = []
        for (fi, s, L1, L2, nr, opis) in ((fx, sx, c["lx"], c["ly"], 1, "dół x"), (fy, sy, c["ly"], c["lx"], 2, "dół y"),
                                            (fgx, sgx, 0.3 * c["lx"] * 2, c["ly"], 3, "góra x (nad podporami)"),
                                            (fgy, sgy, 0.3 * c["ly"] * 2, c["lx"], 4, "góra y (nad podporami)")):
            n = int(L2 / (s / 1000)) + 1
            pr.append(zelbet.Pret(f"{e.id}/{c['id']}", nr, fi, round(L1 + 0.3, 2), n, "00", opis))
        if zn is not None:
            nn = int(a_n / (sn_ / 1000)) + 1
            pr.append(zelbet.Pret(f"{e.id}/{c['id']}", 5, fn, round(a_n + 0.4, 2), 4 * len(naroza) * nn, "00",
                                  "narożne góra i dół, 2 kierunki"))
        wyniki_pelne = [r for r in (tab_wyn,) if r is not None] + wyniki
        return {"wiersz": wiersz, "M_max": max(MxD, MyD), "warunki": warunki, "wyniki": wyniki, "wyniki_pelne": wyniki_pelne,
                "prety": pr, "dane": {"pole": c["id"], "Mx": Mx, "My": My, "Mx_tabl": Mx_t, "My_tabl": My_t, "Mgx": Mgx_d,
                                      "M_naroze": M_nar,
                                      "Mgy": Mgy_d, "Ax": Ax, "Ay": Ay, "w": wobl, "eta": eta, "lx": c["lx"], "ly": c["ly"],
                                      "brzegi": br, "V": vmax}}

    def _equ_wspornika(self, g: Grupa, e: ElementPlyty, poz: Pozycja):
        """EQU wspornika (PN-EN 1990 tabl. A1.2(A)): 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb (przęsło zaplecza)."""
        p = self.p
        inne = [s for s in g.podp_l if e.poly_full.buffer(-0.05).intersects(s.linia)]
        pkt = [s for s in g.podp_p if e.poly_full.buffer(0.05).contains(Point(*s.xy))]
        w = Wynik(nazwa=f"Równowaga statyczna (EQU) — {e.id}")
        if inne or pkt:
            w.krok("Płyta podparta poza krawędzią zamocowania", "", "", "podpory: " + ", ".join([s.id for s in inne] + [s.id for s in pkt]))
            w.uwaga("Płyta nie jest wspornikiem swobodnym — EQU (przewrócenie) nie decyduje.")
            poz.wyniki.append(w)
            return
        root = [s for s in g.podp_l if s.linia.distance(e.poly_full) < 0.15]
        if not root:
            w.uwaga("Brak podpory przy krawędzi zamocowania — sprawdzić model (wspornik bez podparcia).")
            poz.wyniki.append(w)
            return
        r = root[0].linia
        lc = max(r.distance(Point(*xy)) for xy in e.poly_full.exterior.coords)
        par = [s for s in g.podp_l if s is not root[0] and abs(_kat(s.linia) - _kat(r)) < 1e-3 and s.linia.distance(e.poly_full) > 0.2]
        lb = min((s.linia.distance(r) for s in par), default=None)
        gc = e.zest.g_k
        qc = obciazenie_uzytkowe(e.kat_q, p).q_k
        other = [x for x in g.el if x is not e]
        gb = min((x.zest.g_k for x in other), default=gc)
        w.krok("Wysięg wspornika", "l_c", "", lc, "m")
        Md = (p.EQU_gG_dst * gc + p.EQU_gQ * qc) * lc * lc / 2
        w.krok("Moment destabilizujący", "M_dst = (1,10·g_k + 1,5·q_k)·l_c²/2", f"(1,10·{f(gc, 3)} + 1,5·{f(qc, 2)})·{f(lc)}²/2", Md, "kNm/m")
        if lb is None:
            w.uwaga("Nie znaleziono przęsła zaplecza równoległego — EQU do sprawdzenia indywidualnie.")
            poz.wyniki.append(w)
            return
        Ms = p.EQU_gG_stb * gb * lb * lb / 2
        w.krok("Przęsło zaplecza", "l_b", "", lb, "m")
        w.krok("Moment stabilizujący (bez obciążenia zmiennego na zapleczu)", "M_stb = 0,90·g_k,b·l_b²/2",
               f"0,90·{f(gb, 3)}·{f(lb)}²/2", Ms, "kNm/m", zrodlo="R5 3.2")
        w.warunek("EQU — brak odrywania podpory zaplecza", Md, Ms, "kNm/m", "PN-EN 1990 tabl. A1.2(A)", symbol_E="M_dst", symbol_R="M_stb")
        poz.wyniki.append(w)

    # ============================================================================================
    # 2. Schody
    # ============================================================================================
    def _schody(self):
        m, p = self.m, self.p
        for sch in m.schody():
            sid = str(sch["id"])
            try:
                k0 = m.kondygnacja(str(sch["z_kond"]))
                k1 = m.kondygnacja(str(sch["na_kond"]))
            except KeyError:
                continue
            hs, ss = float(sch["wys_stopnia"]), float(sch["szer_stopnia"])
            hpl = None
            if isinstance(sch.get("plyta"), dict) and sch["plyta"].get("grubosc"):
                hpl = float(sch["plyta"]["grubosc"])
            elif sch.get("grubosc_plyty"):
                hpl = float(sch["grubosc_plyty"])
            if hpl is None:
                hpl = 0.15
                self.brak(f"{sid}: brak grubości płyty schodowej (pole schody[].plyta.grubosc) — przyjęto 0,15 m")
            kl = klasa_betonu_z_nazwy(str(sch.get("mat") or "")) or p.beton_dla("schody")[1]
            beton = Beton.z_parametrow(kl, p)
            z = k0.rzedna
            spoczniki = sch.get("spoczniki") or []
            poz = Pozycja("", sid, f"Schody {sid} ({k0.id} → {k1.id})", "schody")
            for bi, bg in enumerate(sch.get("biegi") or []):
                u = np.asarray(bg["kierunek"], float)
                u = u / np.linalg.norm(u)
                S = np.asarray(bg["start"], float)
                nst = int(bg["stopni"])
                Lb = (nst - 1) * ss
                E = S + u * Lb
                z_end = z + nst * hs
                # podpora dolna
                x_start = 0.0
                odc = []
                pods_opis = []
                land_s = self._spocznik_przy(spoczniki, S, z, u)
                if land_s is not None:
                    lp, (dmin, dmax) = land_s
                    back = -dmin                     # zasięg spocznika wstecz od S (wzdłuż −u)
                    wall = self._sciana_przy_krawedzi(lp, S - u * back, u, z)
                    x_start = back + (wall[1] if wall else 0.0)
                    odc.append(schm.OdcinekSchodow(0.0, x_start, "spocznik"))
                    pods_opis.append(f"dół: {'ściana ' + wall[0].id if wall else 'krawędź spocznika'}")
                    sup_low = ("sciana", wall[0], S - u * x_start) if wall else ("brak", None, S - u * x_start)
                else:
                    pods_opis.append(f"dół: posadzka/strop kondygnacji {k0.id}")
                    sup_low = ("posadzka", None, S)
                odc.append(schm.OdcinekSchodow(x_start, x_start + Lb, "bieg"))
                x_end = x_start + Lb
                land_e = self._spocznik_przy(spoczniki, E, z_end, u)
                if land_e is not None:
                    lp, (dmin, dmax) = land_e
                    fwd = dmax
                    wall = self._sciana_przy_krawedzi(lp, E + u * fwd, -u, z_end)
                    odc.append(schm.OdcinekSchodow(x_end, x_end + fwd + (wall[1] if wall else 0.0), "spocznik"))
                    pods_opis.append(f"góra: {'ściana ' + wall[0].id if wall else 'krawędź spocznika'}")
                    x_end = odc[-1].x1
                    sup_high = ("sciana", wall[0], S + u * (x_end - x_start)) if wall else ("brak", None, S + u * (x_end - x_start))
                else:
                    pods_opis.append(f"góra: krawędź stropu na poziomie {f(z_end, 2)} m")
                    sup_high = ("strop", None, E)
                wyn = schm.plyta_schodowa(f"{sid} — bieg {bi + 1}", odc, hpl, hs, ss, float(bg["szer"]), beton, p,
                                          stal=self.stal, ekspozycja=p.ekspozycja.get("schody", "XC1"))
                poz.dane.setdefault("biegi", []).append((odc, hs, ss, float(bg["szer"]), beton))
                poz.wyniki.append(wyn)
                poz.opis.append(f"Bieg {bi + 1}: {nst} podnóżków {f(hs * 100, 1)}/{f(ss * 100, 1)} cm, szer. {f(bg['szer'])} m, "
                                f"rozpiętość w rzucie L = {f(wyn.L, 3)} m; podpory — {'; '.join(pods_opis)}.")
                poz.prety += wyn.prety
                if self.rys_dir:
                    from . import rysunki
                    poz.rysunki += rysunki.rys_schody(wyn, odc, self.rys(f"schody_{_slug(sid)}_{bi + 1}.png"))
                # reakcje → strop / ściany
                szer = float(bg["szer"])
                for (typ, obj, pt), RG, RQ in ((sup_low, wyn.R_G[0], wyn.R_Q[0]), (sup_high, wyn.R_G[-1], wyn.R_Q[-1])):
                    if typ == "strop":
                        nrm = np.array([-u[1], u[0]])
                        ln = LineString([tuple(pt - nrm * szer / 2), tuple(pt + nrm * szer / 2)])
                        self._pending_linia(z_end, ln, RG, RQ, f"reakcja schodów {sid}")
                    elif typ == "sciana":
                        s_c = obj.st(pt)[0]
                        self.pending_sciany.setdefault(obj.id, []).append(("G", RG * szer, s_c, szer))
                        self.pending_sciany.setdefault(obj.id, []).append(("QA", RQ * szer, s_c, szer))
                z = z_end
            poz.przyjeto.append(f"Płyta schodowa gr. {f(hpl * 100, 0)} cm, beton {beton.klasa}; zbrojenie wg wyników biegów.")
            if not all(w.ok for r in poz.wyniki for w in r.warunki):
                hmin = self._min_grubosc_schodow(poz)
                if hmin:
                    poz.przyjeto.append(f"**Grubość z modelu niewystarczająca — wymagana h ≥ {f(hmin * 100, 0)} cm** (ugięcie/nośność).")
            self.pos_schody.append(poz)

    def _min_grubosc_schodow(self, poz: Pozycja) -> float | None:
        """Najmniejsza grubość płyty (co 1 cm, do 30 cm), przy której wszystkie biegi spełniają warunki."""
        p = self.p
        for hcm in range(10, 31):
            h = hcm / 100
            ok = True
            for odc, hs, ss, szer, beton in poz.dane.get("biegi", []):
                r = schm.plyta_schodowa("x", odc, h, hs, ss, szer, beton, p, stal=self.stal)
                if not r.ok:
                    ok = False
                    break
            if ok and h > min(w.h for w in poz.wyniki if hasattr(w, "h")) - 1e-9:
                poz.dane["hmin"] = h
                return h
        return None

    def _spocznik_przy(self, spoczniki, pt, z, u):
        """Spocznik na rzędnej z zawierający punkt pt: (wielobok, (t_min, t_max)) — zasięg wzdłuż kierunku u od pt."""
        for sp in spoczniki:
            if abs(float(sp["rzedna"]) - z) > 0.05:
                continue
            P = Polygon(sp["obrys"])
            if P.buffer(0.1).contains(Point(*pt)):
                ts = [float((np.asarray(v) - np.asarray(pt)) @ u) for v in P.exterior.coords]
                return P, (min(ts), max(ts))
        return None

    def _sciana_przy_krawedzi(self, P: Polygon, pt, u, z):
        """Ściana nośna przy krawędzi spocznika (w kierunku u od punktu pt): (ściana, odległość do osi)."""
        best = None
        for w in self.m.sciany():
            if w.typ not in TYPY_NOSNE or not (w.z_od - 0.1 <= z <= w.z_do + 0.1):
                continue
            ln = LineString([tuple(w.p1), tuple(w.p2)])
            d = ln.distance(Point(*pt))
            if d < 0.35 and ln.distance(P) < 0.3:
                if best is None or d < best[1]:
                    best = (w, d)
        return best

    def _pending_linia(self, z, ln, RG, RQ, opis):
        self._pend_linie = getattr(self, "_pend_linie", [])
        self._pend_linie.append((z, ln, RG, RQ, opis))

    # ============================================================================================
    # 3. Belki
    # ============================================================================================
    def _belki_grupy(self, g: Grupa):
        if g.fe is None:
            return
        p, m, fe = self.p, self.m, g.fe
        for sid, b in g.belki:
            if "#" in sid:
                continue
            bid = str(b["id"])
            (x0, y0), (x1, y1) = b["os"][0], b["os"][1]
            L = math.hypot(x1 - x0, y1 - y0)
            ux, uy = (x1 - x0) / L, (y1 - y0) / L
            bw, hb, spod = float(b["b"]), float(b["h"]), float(b["spod"])
            mat = m.material(str(b.get("mat"))) if b.get("mat") else None
            stalowa = mat is not None and ((mat.kreskowanie or "").upper() == "STAL" or "STAL" in str(b.get("mat")).upper())
            # podpory belki
            pods = []
            for w in m.sciany():
                if w.typ not in TYPY_NOSNE or not (w.z_od < spod + 0.05 <= w.z_do + TOL_Z):
                    continue
                ln = LineString([tuple(w.p1), tuple(w.p2)])
                t = w.grubosc
                for xe, xi in (((x0, y0), 0.0), ((x1, y1), L)):
                    if ln.distance(Point(*xe)) <= t / 2 + 0.12:
                        pods.append((xi, "sciana", w))
            for c in m.slupy():
                if abs(float(c["z_do"]) - spod) > TOL_Z:
                    continue
                cx, cy = c["xy"]
                s = (cx - x0) * ux + (cy - y0) * uy
                dperp = abs(-(cx - x0) * uy + (cy - y0) * ux)
                if -0.2 <= s <= L + 0.2 and dperp <= bw / 2 + 0.1:
                    pods.append((min(max(s, 0.0), L), "slup", c))
            pods = sorted({round(s, 3): (s, t, o) for s, t, o in pods}.values(), key=lambda q: q[0])
            poz = Pozycja("", bid, f"Belka {bid}", "belka")
            if len(pods) < 2:
                poz.uwagi.append(f"Belka {bid}: znaleziono {len(pods)} podpór — schemat niewyznaczalny automatycznie [WYMAGA ANALIZY].")
                self.log(f"Belka {bid}: brak dwóch podpór w modelu — pominięto wymiarowanie")
                self.pos_belki.append(poz)
                continue
            belka = Belka(L, [Podpora(s, "przegub", nazwa=(o.id if t == "sciana" else str(o["id"]))) for s, t, o in pods], EI=1.0, dx=0.05)
            # obciążenia z MES (reakcje liniowe wzdłuż linii belki)
            obc = {}
            for cs, r in g.res.items():
                ss, rr = fe.reakcje_liniowe(r, sid)
                if not len(ss):
                    continue
                s0 = LineString([(x0, y0), (x1, y1)]).project(Point(*next(sp for sp in g.podp_l if sp.id == sid).linia.coords[0]))
                lst = []
                for k in range(len(ss) - 1):
                    a, bb = ss[k] + s0, ss[k + 1] + s0
                    q0, q1 = max(np.nan_to_num(rr[k]), 0.0), max(np.nan_to_num(rr[k + 1]), 0.0)   # [UPR] bez odrywania
                    lst.append(ObcQ(float(q0), float(min(max(a, 0), L)), float(min(max(bb, 0), L)), float(q1)))
                obc[cs] = lst
            h_pl = next((e.h for e in g.el if abs(spod + hb - e.spod) < TOL_Z), 0.0)
            gw = bw * hb * p.ciezar_zelbetu if not stalowa else 0.0
            obc["G"] = obc.get("G", []) + [ObcQ(gw)]
            rozw = {cs: belka.rozwiaz(v) for cs, v in obc.items()}
            kombs = [k for k in kombinacje(g.odz, p, "STR") + kombinacje(g.odz, p, "wyj")]
            Ms = np.array([sum(a * rozw[c].M for c, a in kb.wsp.items() if c in rozw) for kb in kombs])
            Vs = np.array([np.maximum(np.abs(sum(a * rozw[c].Vl for c, a in kb.wsp.items() if c in rozw)),
                                      np.abs(sum(a * rozw[c].Vp for c, a in kb.wsp.items() if c in rozw))) for kb in kombs])
            MEd, MEd_m, VEd = float(Ms.max()), float(Ms.min()), float(Vs.max())
            qp = rozw["G"] * 1.0 + (rozw["QA"] * p.psi_of("A")[2] if "QA" in rozw else rozw["G"] * 0)
            poz.opis.append(f"Belka {'stalowa' if stalowa else 'żelbetowa'} b × h = {f(bw * 100, 0)} × {f(hb * 100, 0)} cm, "
                            f"oś ({f(x0)}, {f(y0)}) → ({f(x1)}, {f(y1)}), L = {f(L, 3)} m; podpory: "
                            + ", ".join(f"{('ściana ' + o.id) if t == 'sciana' else ('słup ' + str(o['id']))} (x = {f(s, 2)} m)"
                                        for s, t, o in pods) + ". Obciążenie: reakcje płyty z MES (rozkład wzdłuż belki) + ciężar własny.")
            rows = [[cs, (sum(q.q0 * ((q.x1 or L) - (q.x0 or 0)) for q in v if isinstance(q, ObcQ)), 1)] for cs, v in obc.items()]
            poz.obciazenia.append("**Obciążenia belki (charakterystyczne, wypadkowe przypadków)**\n\n" +
                                  tabela(["Przypadek", "Σq·l ≈ [kN]"], rows))
            w0 = Wynik(nazwa=f"Siły wewnętrzne — {bid} (obwiednia kombinacji)")
            w0.krok("Moment przęsłowy maks.", "M_Ed,max", "", MEd, "kNm")
            w0.krok("Moment podporowy (min.)", "M_Ed,min", "", MEd_m, "kNm")
            w0.krok("Siła poprzeczna maks.", "V_Ed", "", VEd, "kN")
            poz.wyniki.append(w0)
            if stalowa:
                prz = przekroj(str(b.get("przekroj") or f"PROST {bw * 1000:g}x{hb * 1000:g}"))
                st = StalKonstr(str(b.get("mat")) if "S" in str(b.get("mat")) else p.stal_konstr)
                wk = float(max(np.abs(rozw["G"].w + sum(rozw[c].w for c in rozw if c != "G")))) / (st.E * prz.I_y * 1e-9) * 1000
                poz.wyniki.append(stalm.belka_stalowa(prz, st, L, MEd, VEd, w_k=wk, p=p, nazwa=f"{bid} — nośność"))
            else:
                kl = klasa_betonu_z_nazwy(mat.nazwa if mat else None) or p.beton_dla("belka")[1]
                beton = Beton.z_parametrow(kl, p)
                ex = p.ekspozycja.get("belka", "XC1")
                c = zelbet.otulina(ex, 16, p, fi_strzemion=8).c_nom
                h_tot = hb + h_pl
                d = h_tot - c / 1000 - 0.008
                b_eff = min(bw + 0.2 * 0.85 * L, bw + 2 * 0.1 * L + (0.2 * L if h_pl else 0), bw + 1.0) if h_pl else bw
                if h_pl:
                    zg = zelbet.zginanie_teowy(MEd, b_eff, bw, h_tot, h_pl, d, beton, self.stal, nazwa=f"{bid} — zginanie w przęśle (przekrój teowy)")
                else:
                    zg = zelbet.zginanie_prostokat(MEd, bw, h_tot, d, beton, self.stal, nazwa=f"{bid} — zginanie w przęśle")
                n, fi, rows_, As = zelbet.dobierz_belka(max(zg.As_req, zg.As_min), bw, c, 8)
                zg.krok("Przyjęto dołem", f"{n}φ{fi}" + (f" ({rows_} warstwy)" if rows_ > 1 else ""), "", As / 100, "cm²", nd=2)
                zg.warunek("Zbrojenie dolne", max(zg.As_req, zg.As_min), As, "mm²", "6.1", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
                poz.wyniki.append(zg)
                if MEd_m < -1e-3:
                    zt = zelbet.zginanie_prostokat(abs(MEd_m), bw, h_tot, d, beton, self.stal, nazwa=f"{bid} — zginanie nad podporą")
                    nt, fit, _, Ast = zelbet.dobierz_belka(max(zt.As_req, zt.As_min), bw, c, 8)
                    zt.warunek("Zbrojenie górne", max(zt.As_req, zt.As_min), Ast, "mm²", "6.1", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
                    poz.wyniki.append(zt)
                else:
                    nt, fit = 2, 12
                sc = zelbet.scinanie_strzemiona(VEd, bw, d, As, beton, self.stal, 8, 2, nazwa=f"{bid} — ścinanie")
                poz.wyniki.append(sc)
                Mqp = float(qp.M.max())
                EI = 1.0
                ug = zelbet.ugiecie_komplet(L, 1.0, h_tot, d, zg.As_req, As, beton, Mqp, qp.w_max(), p, b=bw, stal=self.stal,
                                            teowy=bool(h_pl) and b_eff / bw > 3, nazwa=f"{bid} — ugięcie")
                poz.wyniki.append(ug)
                poz.wyniki.append(zelbet.rysy_bez_obliczen(Mqp, bw, h_tot, d, As, fi, (bw * 1000 - 2 * c) / max(n - 1, 1), beton,
                                                           p.w_max.get(ex, 0.4), nazwa=f"{bid} — rysy"))
                poz.przyjeto.append(f"Belka {bid}: {f(bw * 100, 0)}×{f(h_tot * 100, 0)} cm" + (" (z płytą)" if h_pl else "")
                                    + f", {beton.klasa}; dołem {n}φ{fi}, górą {nt}φ{fit}, strzemiona {sc.strzemiona}.")
                ns = int(L / (sc.s / 1000)) + 1
                poz.prety = [zelbet.Pret(bid, 1, fi, round(L + 0.4, 2), n, "00", "dołem"),
                             zelbet.Pret(bid, 2, fit, round(L + 0.4, 2), nt, "00", "górą"),
                             zelbet.Pret(bid, 3, 8, round(2 * (bw - 0.06) + 2 * (h_tot - 0.06) + 0.2, 2), ns, "51",
                                         f"{f((bw - 0.06) * 100, 0)}×{f((h_tot - 0.06) * 100, 0)} cm")]
            if self.rys_dir:
                from . import rysunki
                poz.rysunki += rysunki.rys_belka(belka, pods, rozw, Ms, Vs, bid, self.rys(f"belka_{_slug(bid)}.png"))
            # reakcje → ściany / słupy
            for k, (s, t, o) in enumerate(pods):
                for cs, r in rozw.items():
                    R = float(r.R[k])
                    if t == "sciana":
                        self.pending_sciany.setdefault(o.id, []).append((cs, R, o.st((x0 + ux * s, y0 + uy * s))[0], 0.25))
                    else:
                        d_ = self.slupy_N.setdefault(str(o["id"]), {})
                        d_[cs] = d_.get(cs, 0.0) + R
            poz.dane["reakcje"] = {(o.id if t == "sciana" else str(o["id"])): {cs: float(r.R[k]) for cs, r in rozw.items()}
                                   for k, (s, t, o) in enumerate(pods)}
            self.pos_belki.append(poz)

    def _slupy_pod_grupa(self, g: Grupa):
        if g.fe is None:
            return
        for s in g.podp_p:
            d_ = self.slupy_N.setdefault(s.id, {})
            for cs, r in g.res.items():
                d_[cs] = d_.get(cs, 0.0) + g.fe.reakcja(r, s.id)

    # ============================================================================================
    # 4. Ściany murowe
    # ============================================================================================
    def _sciana(self, w):
        m, p = self.m, self.p
        pr = self.prof.setdefault(w.id, {"top_s": Profil(w.L), "top_a": Profil(w.L), "dol": Profil(w.L), "otw": []})
        # reakcje płyt
        for g in self.grupy:
            if g.fe is None:
                continue
            for sid, ww in getattr(g, "sciany_pod", []):
                if ww.id != w.id:
                    continue
                ln = next(sp.linia for sp in g.podp_l if sp.id == sid)
                for cs, r in g.res.items():
                    ss, rr = g.fe.reakcje_liniowe(r, sid)
                    if len(ss):
                        sw = [w.st(ln.interpolate(s_).coords[0])[0] for s_ in ss]
                        # reakcje ujemne (odrywanie naroży płyty) pominięte — bezpiecznie dla ścian ściskanych [UPR]
                        pr["top_s"].dodaj(cs, sw, np.maximum(np.nan_to_num(rr), 0.0) if cs != "G" or True else rr)
        # obciążenia skupione (belki, schody)
        for cs, P, s_c, szer in self.pending_sciany.get(w.id, []):
            pr["top_s"].dodaj_skupiona(cs, P, s_c, szer)
        # ściany powyżej
        for v in m.sciany():
            if v.id == w.id or v.id not in self.prof or v.typ not in TYPY_NOSNE:
                continue
            if abs(v.z_od - w.z_do) > 0.6 or v.z_od < w.z_do - TOL_Z:
                continue
            ov = self._wspolliniowe(w, v)
            if ov < 0.3:
                continue
            pv = self.prof[v.id]["dol"]
            for cs in pv.przypadki():
                sw = [w.st(v.pt(s_, 0.0))[0] for s_ in pv.s]
                pr["top_a"].dodaj(cs, sw, pv.get(cs))
        # ciężar własny i przekazanie przez otwory → profil dolny
        gm2, zest = self._ciezar_sciany(w)
        h = w.z_do - w.z_od
        dol = pr["dol"]
        for cs in set(pr["top_s"].przypadki()) | set(pr["top_a"].przypadki()) | {"G"}:
            top = pr["top_s"].get(cs) + pr["top_a"].get(cs)
            base = top.copy()
            if cs == "G":
                base = base + gm2 * h
            dol.q[cs] = base
        otw = sorted(m.otwory(sciana=w.id), key=lambda o: o.s0)
        for o in otw:
            s0, s1 = max(o.s0, 0.0), min(o.s1, w.L)
            msk = (dol.s >= s0) & (dol.s <= s1)
            for cs in list(dol.q):
                arr = dol.q[cs]
                above = pr["top_s"].get(cs) + pr["top_a"].get(cs) + (gm2 * max(w.z_do - o.z1, 0) if cs == "G" else 0.0)
                T = float(np.trapezoid(np.where(msk, above, 0.0), dol.s))
                para = gm2 * max(o.z0 - w.z_od, 0) if cs == "G" else 0.0
                arr = np.where(msk, para, arr)
                for strona in (-1, 1):
                    if strona < 0:
                        a0, a1 = max(s0 - 0.5, 0.0), s0
                    else:
                        a0, a1 = s1, min(s1 + 0.5, w.L)
                    if a1 - a0 < 0.05:
                        continue
                    mm = (dol.s >= a0) & (dol.s < a1) if strona < 0 else (dol.s > a1 - (a1 - a0)) & (dol.s <= a1)
                    arr = arr + np.where(mm, T / 2 / (a1 - a0), 0.0)
                dol.q[cs] = arr
            pr["otw"].append(o)
        pr["gm2"], pr["zest"], pr["h"] = gm2, zest, h
        self._sprawdz_sciane(w, pr)

    def _mur_sciany(self, w) -> Mur | None:
        kl = w.warstwa_konstr
        mat = self.m.material(kl.mat)
        if mat is None:
            return None
        kr = (mat.kreskowanie or "").upper()
        if kr.startswith("MUR") or "MUR" in kr:
            fb = klasa_muru_z_nazwy(mat.nazwa) or self.p.mur_f_b
            if klasa_muru_z_nazwy(mat.nazwa) is None:
                self.brak(f"{w.id}: klasa elementów murowych nie wynika z nazwy materiału {kl.mat} — przyjęto {f(fb, 0)}")
            return Mur.z_parametrow(self.p, f_b=fb, nazwa=mat.nazwa)
        return None

    def _sprawdz_sciane(self, w, pr):
        p, m = self.p, self.m
        mur = self._mur_sciany(w)
        t = w.warstwa_konstr.d
        poz = Pozycja("", w.id, f"Ściana {w.id} ({w.kond}, {'zewnętrzna' if w.typ == 'sciana_zewn' else 'wewnętrzna'} nośna)", "sciana")
        poz.opis.append(f"Ściana gr. konstrukcyjnej t = {f(t * 100, 0)} cm, długość osi {f(w.L, 2)} m, wysokość h = "
                        f"{f(pr['h'], 3)} m (z {f(w.z_od, 3)} do {f(w.z_do, 3)}); materiał: "
                        f"{m.material(w.warstwa_konstr.mat).nazwa if m.material(w.warstwa_konstr.mat) else w.warstwa_konstr.mat}. "
                        f"Otwory: {', '.join(o.id + ' (' + f(o.szer) + ' m)' for o in pr['otw']) or 'brak'}.")
        poz.obciazenia.append(f"**Ciężar ściany — {pr['zest'].tytul}**\n\n" + pr["zest"].md(p))
        top, dol = pr["top_s"], pr["dol"]
        cases = sorted(set(top.przypadki()) | set(pr["top_a"].przypadki()) | set(dol.przypadki()))
        rows = [[cs, (float((top.get(cs) + pr["top_a"].get(cs)).max()), 2), (dol.calka(cs) / w.L, 2), (float(dol.get(cs).max()), 2)]
                for cs in cases]
        poz.obciazenia.append("**Obciążenia ściany (charakterystyczne)** — góra: z płyt i ścian wyżej; dół: po przekazaniu "
                              "obciążeń znad otworów na filarki\n\n" + tabela(
                                  ["Przypadek", "max q_góra [kN/m]", "średnio q_dół [kN/m]", "max q_dół [kN/m]"], rows))
        if mur is None:
            poz.uwagi.append("Warstwa konstrukcyjna nie jest murem (np. żelbet) — ściana żelbetowa: sprawdzenie wg PN-EN 1992-1-1 "
                             "(ściany 9.6, smukłość 5.8) — poza zakresem automatycznym [WYMAGA ANALIZY].")
            self.pos_sciany.append(poz)
            return
        odz = [Oddz("G", "G")] + [Oddz(c, "Q", {"QA": "A", "H": "H", "S1": "S", "S2": "S"}.get(c, "A"),
                                       "QA" if c.startswith("QA") else ("dach" if c in ("H", "S1", "S2") else ""))
                                  for c in cases if c != "G" and c != "SB2"]
        zewn = w.typ == "sciana_zewn"
        if zewn:
            odz.append(Oddz("W", "Q", "W"))
        kombs = kombinacje(odz, p, "STR", G_korzystne=True)
        wk = max(abs(self.wiatr_sc.w_max_parcie), abs(self.wiatr_sc.w_max_ssanie)) if (zewn and self.wiatr_sc) else 0.0
        h = pr["h"]
        # mimośród stropu: zewn. — jednostronnie t/6; wewn. — różnica
        best = None
        segs = self._segmenty(w, pr)
        for kb in kombs:
            ctop = top.kombinacja({c: a for c, a in kb.wsp.items() if c != "W"})
            atop = pr["top_a"].kombinacja({c: a for c, a in kb.wsp.items() if c != "W"})
            cdol = dol.kombinacja({c: a for c, a in kb.wsp.items() if c != "W"})
            Mw = kb.wsp.get("W", 0.0) * wk * h * h / 8
            for sg in segs:
                msk = (dol.s >= sg[0] - 1e-9) & (dol.s <= sg[1] + 1e-9)
                b = sg[1] - sg[0]
                if b < 0.05:
                    continue
                if sg[2] == "sciana":
                    ns = top.srednia_ruchoma(ctop, 1.0)[msk].max() if msk.any() else 0
                    na = top.srednia_ruchoma(atop, 1.0)[msk].max() if msk.any() else 0
                    Nd = float(top.srednia_ruchoma(cdol, 1.0)[msk].max())
                    Ng = float(ns + na)
                    Ms = ns * t / 6 if zewn else ns * t / 6 * 0.3
                    r = murm.sciana_nosnosc(max(Ng, 1e-3), max(0.5 * (Ng + Nd), 1e-3), max(Nd, 1e-3), t, h, mur, M_g=Ms, M_w=Mw, p=p,
                                            nazwa=f"{w.id} — ściana (odcinek {f(sg[0])}–{f(sg[1])} m), {kb.nazwa}")
                else:
                    Ng = float(np.trapezoid(np.where(msk, ctop + atop, 0), dol.s))
                    Nd = float(np.trapezoid(np.where(msk, cdol, 0), dol.s))
                    Nss = float(np.trapezoid(np.where(msk, ctop, 0), dol.s))
                    r = murm.filarek(max(Ng, 1e-3), max(Nd, 1e-3), b, t, h, mur, M_g=Nss * t / 6 * (1 if zewn else 0.3), p=p,
                                     nazwa=f"{w.id} — filarek {f(sg[0])}–{f(sg[1])} m (b = {f(b)} m), {kb.nazwa}")
                if best is None or r.wykorzystanie > best.wykorzystanie:
                    best = r
        if best is not None:
            poz.wyniki.append(best)
            poz.opis.append(f"Sprawdzono {len(segs)} odcinków (filarki między otworami i pasma ściany) dla {len(kombs)} kombinacji; "
                            "poniżej przypadek miarodajny. Mimośród reakcji stropu e = t/6 (zewn.) / 0,3·t/6 (wewn., niesymetria) [UPR]; "
                            "wiatr jako moment w połowie wysokości w·h²/8.")
        if zewn and wk:
            nmin = float(np.mean(top.get("G") + pr["top_a"].get("G"))) + pr["gm2"] * h / 2   # średnio [UPR]
            sig = max(nmin, 0) / t / 1000 * p.gG_inf
            rw = murm.sciana_wiatr(p.gQ * wk, h, t, mur, sigma_d=sig, p=p, nazwa=f"{w.id} — zginanie z płaszczyzny (wiatr)")
            if nmin > 5.0:
                # ściana obciążona pionowo — miarodajne sprawdzenie 6.1.2 z mimośrodem od wiatru e_hm (wyżej); pasmo
                # zginane bez udziału ściskania — informacyjnie (PN-EN 1996-1-1 6.3.1(3)–(4)) [UPR]
                for wv in rw.warunki:
                    rw.uwaga(f"Informacyjnie (dolne oszacowanie, bez efektu przesklepienia 6.3.2): {wv.opis}: M_Ed = "
                             f"{f(wv.E, 3)} ≤? M_Rd = {f(wv.R, 3)} kNm/m (η = {f(wv.eta * 100, 0)}%). Ściana obciążona pionowo — "
                             "miarodajne sprawdzenie 6.1.2 z mimośrodem e_hm od wiatru.")
                rw.warunki = []
            poz.wyniki.append(rw)
        # docisk pod belkami i schodami
        for cs, P, s_c, szer in self.pending_sciany.get(w.id, []):
            if cs != "G" or szer > 0.5:
                continue
            PQ = sum(q[1] for q in self.pending_sciany.get(w.id, []) if abs(q[2] - s_c) < 1e-6 and q[0] != "G")
            N = p.gG_sup * P + p.gQ * PQ
            a1 = min(s_c, w.L - s_c) - szer / 2
            poz.wyniki.append(murm.docisk(N, max(a1, 0.0), szer, t, h, mur, nazwa=f"{w.id} — docisk pod oparciem belki (s = {f(s_c)} m)"))
        if self.rys_dir:
            from . import rysunki
            poz.rysunki += rysunki.rys_sciana(w, pr, self.rys(f"sciana_{_slug(w.id)}.png"))
        poz.przyjeto.append(f"Mur: {mur.nazwa}, f_d = {f(mur.f_d, 2)} MPa (klasa wykonania A, γ_M = {f(mur.gamma_M, 1)}).")
        self.pos_sciany.append(poz)

    def _segmenty(self, w, pr) -> list:
        """Odcinki ściany: filarki między otworami ('filarek') lub pasma bez otworów ('sciana')."""
        otw = sorted(pr["otw"], key=lambda o: o.s0)
        if not otw:
            return [(0.0, w.L, "sciana")]
        out = []
        prev = 0.0
        for o in otw:
            if o.s0 - prev > 0.05:
                out.append((prev, o.s0, "filarek"))
            prev = max(prev, o.s1)
        if w.L - prev > 0.05:
            out.append((prev, w.L, "filarek"))
        return out

    # ============================================================================================
    # 5. Nadproża i wieńce
    # ============================================================================================
    def _nadproza(self):
        p, m = self.p, self.m
        wyniki = []
        for w in m.sciany():
            if w.typ not in TYPY_NOSNE or w.id not in self.prof:
                continue
            pr = self.prof[w.id]
            t = w.warstwa_konstr.d
            gm2 = pr["gm2"]
            for o in pr["otw"]:
                gap = w.z_do - o.z1
                slab = None
                for g in self.grupy:
                    for e in g.el:
                        if abs(e.spod - w.z_do) < TOL_Z and e.poly_full.buffer(t).intersects(LineString([tuple(o.p0), tuple(o.p1)])):
                            slab = e
                zint = gap <= 0.35 and slab is not None
                if zint:
                    hn = gap + slab.h
                else:
                    hn = min(max(gap, 0.12), 0.25)     # nadproże 25 cm, powyżej mur do wieńca [ZAŁ]
                    if gap < 0.12:
                        self.log(f"N-{o.id}: nad otworem tylko {f(gap * 100, 0)} cm muru bez płyty — sprawdzić rozwiązanie nadproża")
                a = 0.25 if o.szer > 1.5 else 0.20
                Lef = o.szer + min(a, hn)
                s0, s1 = max(o.s0 - a, 0.0), min(o.s1 + a, w.L)
                top = pr["top_s"]
                q = {}
                for cs in set(top.przypadki()) | set(pr["top_a"].przypadki()) | {"G"}:
                    arr = top.get(cs) + pr["top_a"].get(cs)
                    msk = (top.s >= o.s0) & (top.s <= o.s1)
                    q[cs] = float(arr[msk].mean()) if msk.any() else 0.0
                q["G"] = q.get("G", 0.0) + gm2 * max(gap, 0) + t * hn * p.ciezar_zelbetu
                qd = max(p.gG_sup * q["G"] + p.gQ * 0.7 * sum(v for c, v in q.items() if c in ("QA", "S2", "H")),
                         p.xi * p.gG_sup * q["G"] + p.gQ * max([v for c, v in q.items() if c in ("QA", "S2", "H")] or [0])
                         + p.gQ * 0.7 * 0)
                qqp = q["G"] + p.psi_of("A")[2] * q.get("QA", 0.0)
                kl = p.beton_dla("nadproze")[1]
                beton = Beton.z_parametrow(kl, p)
                c = zelbet.otulina(p.ekspozycja.get("nadproze", "XC1"), 12, p, fi_strzemion=6).c_nom
                d = hn - c / 1000 - 0.006
                nid = f"N-{o.id}"
                poz = Pozycja("", nid, f"Nadproże {nid} nad otworem {o.id} w ścianie {w.id} (światło {f(o.szer)} m)", "nadproze")
                MEd = qd * Lef ** 2 / 8
                VEd = qd * o.szer / 2
                w0 = Wynik(nazwa=f"{nid} — schemat i obciążenie")
                w0.krok("Rozpiętość obliczeniowa", "l_eff = l_n + min(a; h)", f"{f(o.szer)} + {f(min(a, hn))}", Lef, "m", zrodlo="5.3.2.2")
                w0.krok("Przekrój", "b × h", "", f"{f(t * 100, 0)} × {f(hn * 100, 0)} cm" + (" (zespolone z płytą stropu)" if zint else ""))
                w0.krok("Obciążenie (średnio nad otworem; bez efektu przesklepienia [UPR])", "g_k; q_k",
                        "", f"{f(q['G'], 2)}; {f(sum(v for c_, v in q.items() if c_ != 'G'), 2)}", "kN/m")
                w0.krok("Obciążenie obliczeniowe", "q_d", "", qd, "kN/m")
                w0.krok("Moment", "M_Ed = q_d·l_eff²/8", f"{f(qd)}·{f(Lef, 3)}²/8", MEd, "kNm")
                w0.krok("Siła poprzeczna", "V_Ed = q_d·l_n/2", f"{f(qd)}·{f(o.szer)}/2", VEd, "kN")
                poz.wyniki.append(w0)
                zg = zelbet.zginanie_prostokat(MEd, t, hn, d, beton, self.stal, nazwa=f"{nid} — zginanie")
                n, fi, _, As = zelbet.dobierz_belka(max(zg.As_req, zg.As_min), t, c, 6, srednice=(10, 12, 14, 16, 20))
                zg.warunek("Zbrojenie dolne", max(zg.As_req, zg.As_min), As, "mm²", "6.1", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
                poz.wyniki.append(zg)
                sc = zelbet.scinanie_strzemiona(VEd, t, d, As, beton, self.stal, 6, 2, nazwa=f"{nid} — ścinanie")
                poz.wyniki.append(sc)
                wel = 5 * qqp * Lef ** 4 / 384
                poz.wyniki.append(zelbet.ugiecie_komplet(Lef, 1.0, hn, d, zg.As_req, As, beton, qqp * Lef ** 2 / 8, wel, p, b=t,
                                                         stal=self.stal, nazwa=f"{nid} — ugięcie"))
                mur = self._mur_sciany(w)
                if mur is not None:
                    R = qd * Lef / 2
                    a1 = min(s0, w.L - s1)
                    poz.wyniki.append(murm.docisk(R, max(a1, 0.0), a, t, max(w.z_do - w.z_od, 0.5), mur,
                                                  nazwa=f"{nid} — docisk na murze (oparcie {f(a * 100, 0)} cm)"))
                poz.przyjeto.append(f"{nid}: {'nadproże zespolone z płytą' if zint else 'nadproże żelbetowe'} "
                                    f"{f(t * 100, 0)}×{f(hn * 100, 0)} cm, {beton.klasa}, dołem {n}φ{fi}, strzemiona {sc.strzemiona}, "
                                    f"oparcie ≥ {f(a * 100, 0)} cm.")
                poz.prety = [zelbet.Pret(nid, 1, fi, round(o.szer + 2 * a + 0.2, 2), n, "00", "dołem"),
                             zelbet.Pret(nid, 2, 10, round(o.szer + 2 * a + 0.2, 2), 2, "00", "górą montażowe"),
                             zelbet.Pret(nid, 3, 6, round(2 * (t - 0.05) + 2 * (hn - 0.05) + 0.15, 2), int((o.szer + 2 * a) / (sc.s / 1000)) + 1,
                                         "51", "")]
                poz.dane.update({"L": Lef, "M": MEd, "q_d": qd})
                wyniki.append(poz)
        self.pos_nadproza = sorted(wyniki, key=lambda q: q.ident)

    def _wience(self):
        p = self.p
        for g in self.grupy:
            if g.fe is None or not getattr(g, "sciany_pod", None):
                continue
            Ls = sum(next(sp.linia.length for sp in g.podp_l if sp.id == sid) for sid, _ in g.sciany_pod)
            li = max((max(c["lx"], c["ly"]) for c in g.komorki), default=6.0)
            beton = Beton.z_parametrow(p.beton_dla("wieniec")[1], p)
            poz = Pozycja("", f"W-{_slug(g.nazwa)}", f"Wieńce pod płytą {g.nazwa} (poziom {f(g.wierzch, 3)} m)", "wieniec")
            poz.wyniki.append(zelbet.wieniec(li, beton, self.stal, nazwa=f"Wieniec — ściąg obwodowy (l_i = {f(li)} m)"))
            poz.opis.append(f"Wieńce żelbetowe na wszystkich ścianach nośnych pod płytą (łączna długość ≈ {f(Ls, 1)} m), "
                            "szerokość = grubość muru, wysokość = grubość płyty; ciągłość zbrojenia w narożach (pręty narożne "
                            "L, zakład l₀).")
            zk = zelbet.zakotwienie(12, beton, self.stal)
            poz.wyniki.append(zk)
            poz.przyjeto.append(f"Wieniec: 4φ12 (B500SP), strzemiona φ6 co 25 cm, zakłady l₀ = {f(zk.l_0, 0)} mm, beton {beton.klasa}.")
            poz.prety = [zelbet.Pret(poz.ident, 1, 12, round(Ls, 1), 4, "00", "(łącznie, + zakłady)"),
                         zelbet.Pret(poz.ident, 2, 6, 0.8, int(Ls / 0.25) + 1, "51", "")]
            self.pos_wience.append(poz)

    # ============================================================================================
    # 6. Słupy
    # ============================================================================================
    def _slupy(self):
        p, m = self.p, self.m
        for c in m.slupy():
            cid = str(c["id"])
            N = self.slupy_N.get(cid, {})
            L = float(c["z_do"]) - float(c["z_od"])
            mat = m.material(str(c.get("mat"))) if c.get("mat") else None
            poz = Pozycja("", cid, f"Słup {cid} ({c.get('przekroj')}, L = {f(L, 2)} m)", "slup")
            if not N:
                poz.uwagi.append("Brak obciążeń przypisanych do słupa (nie podpiera płyty ani belki w modelu).")
            stalowy = mat is not None and ((mat.kreskowanie or "").upper() == "STAL")
            G0 = 0.0
            if stalowy:
                try:
                    prz = przekroj(str(c.get("przekroj")))
                except BladDanych as ex:
                    poz.uwagi.append(str(ex))
                    self.pos_slupy.append(poz)
                    continue
                G0 = prz.masa * 9.81 / 1000 * L
            N = dict(N)
            N["G"] = N.get("G", 0.0) + G0
            self.slupy_N[cid] = N
            odz = [Oddz("G", "G")] + [Oddz(cs, "Q", {"QA": "A", "H": "H", "S1": "S", "S2": "S"}.get(cs, "A"),
                                           "QA" if cs.startswith("QA") else "dach") for cs in N if cs not in ("G", "SB2")]
            NEd = max(sum(a * N.get(cs, 0.0) for cs, a in kb.wsp.items()) for kb in kombinacje(odz, p, "STR"))
            wb = self.q_p * 1.0 * p.gQ * (prz.b / 1000 if stalowy else 0.3)
            Mw = wb * L * L / 8
            poz.opis.append(f"Słup przegubowo zamocowany na obu końcach (układ usztywniony płytą połączoną z budynkiem) — "
                            f"L_cr = L = {f(L, 2)} m [ZAŁ]; siła osiowa z reakcji płyty/belek; wiatr na trzon słupa (c_f ≈ 1,0) "
                            f"jako obciążenie towarzyszące.")
            poz.obciazenia.append(tabela(["Przypadek", "N_k [kN]"], [[cs, (v, 2)] for cs, v in N.items()]))
            if stalowy:
                st = StalKonstr(str(c.get("mat")) if "S" in str(c.get("mat")).upper() else p.stal_konstr)
                r = stalm.slup(prz, st, NEd, L, L, M_y_Ed=Mw * 0.6, wykres="rownomierne", p=p, nazwa=f"{cid} — nośność")
                poz.wyniki.append(r)
                poz.przyjeto.append(f"Słup {prz.nazwa} ze stali {st.gatunek}; N_Ed = {f(NEd, 1)} kN, N_b,Rd = {f(r.N_Rd, 1)} kN.")
                poz.uwagi.append("Połączenia (blacha podstawy, kotwy, głowica) — dobór w projekcie wykonawczym; przemieszczenie "
                                 "poziome ≤ H/150 (R5-71) przy układzie nieusztywnionym.")
            else:
                poz.uwagi.append("Słup żelbetowy/inny — sprawdzenie wg PN-EN 1992-1-1 5.8 (smukłość, efekty II rzędu) "
                                 "[WYMAGA ANALIZY — poza zakresem automatycznym].")
            if self.rys_dir:
                from . import rysunki
                poz.rysunki += rysunki.rys_slup(cid, L, NEd, self.rys(f"slup_{_slug(cid)}.png"))
            poz.dane["N_Ed"] = NEd
            self.pos_slupy.append(poz)

    # ============================================================================================
    # 7. Fundamenty
    # ============================================================================================
    def _teren_przy(self, xy) -> float:
        pts = self.m.dz.teren_punkty() if getattr(self.m, "dz", None) is not None else np.zeros((0, 3))
        proj = (self.m.dz.raw.get("teren") or {}).get("punkty_projektowane") if getattr(self.m, "dz", None) else None
        if proj:
            arr = np.asarray(proj, float)
            xyb = self.m.dz.do_budynku(arr[:, :2])
            pts = np.column_stack([xyb, arr[:, 2] - self.m.dz.zero_abs])
        if len(pts) >= 3:
            from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator
            try:
                v = float(LinearNDInterpolator(pts[:, :2], pts[:, 2])(xy[0], xy[1]))
                if v == v:
                    return v
            except Exception:  # noqa: BLE001
                pass
            return float(NearestNDInterpolator(pts[:, :2], pts[:, 2])(xy[0], xy[1]))
        self.brak("Brak punktów terenu (dzialka.yaml: teren.punkty) — przyjęto rzędną terenu " + f(self.p.teren_domyslny, 2) + " m")
        return self.p.teren_domyslny

    def _fundamenty(self):
        p, m = self.p, self.m
        fu = m.fundamenty()
        k0 = m.kondygnacje[0] if m.kondygnacje else None
        z_posadzki = m.kond_z_od(k0.id) if k0 else 0.0
        obrys0 = m.obrys_kondygnacji(k0.id) if k0 else Polygon()
        rows = []
        for el in fu.get("elementy") or []:
            fid = str(el.get("id"))
            B, hf, spod = float(el.get("b", 0.6)), float(el.get("h", 0.3)), float(el.get("spod", -1.0))
            kl = klasa_betonu_z_nazwy(str(el.get("mat") or "")) or p.beton_dla("fundament")[1]
            beton = Beton.z_parametrow(kl, p)
            if "os" not in el:
                poz = Pozycja("", fid, f"Płyta fundamentowa {fid}", "fundament")
                self._plyta_fund(el, poz, beton)
                self.pos_fund.append(poz)
                continue
            (x0, y0), (x1, y1) = el["os"][0], el["os"][1]
            Lax = math.hypot(x1 - x0, y1 - y0)
            ux, uy = ((x1 - x0) / Lax, (y1 - y0) / Lax) if Lax > 0 else (1.0, 0.0)
            ln = LineString([(x0, y0), (x1, y1)])
            top = spod + hf
            slupy = [c for c in m.slupy() if abs(float(c["z_od"]) - top) < 0.8 and ln.buffer(B / 2 + 0.05).contains(Point(*c["xy"]))]
            mid = ((x0 + x1) / 2, (y0 + y1) / 2)
            nrm = (-uy, ux)
            probe = [(mid[0] + sg * nrm[0] * (B / 2 + 0.8), mid[1] + sg * nrm[1] * (B / 2 + 0.8)) for sg in (1, -1)]
            zewn = any(not obrys0.buffer(0.05).contains(Point(*q)) for q in probe) if not obrys0.is_empty else True
            if zewn:
                zt = min(self._teren_przy(q) for q in probe if obrys0.is_empty or not obrys0.buffer(0.05).contains(Point(*q)))
            else:
                zt = z_posadzki
            D_ext = zt - spod
            D_int = z_posadzki - spod
            D = min(D_ext, D_int) if zewn else D_int
            if Lax <= 1.5 * B and slupy:
                # stopa
                Lf = Lax + B
                N = {}
                for c in slupy:
                    for cs, v in self.slupy_N.get(str(c["id"]), {}).items():
                        N[cs] = N.get(cs, 0.0) + v
                Gk = N.get("G", 0.0)
                Qk = max([N.get(c_, 0.0) for c_ in N if c_ != "G" and c_ != "SB2"] or [0.0])
                poz = Pozycja("", fid, f"Stopa fundamentowa {fid} ({f(B)} × {f(Lf)} × {f(hf)} m) pod słupem "
                              + ", ".join(str(c["id"]) for c in slupy), "fundament")
                poz.opis.append(f"Spód stopy {f(spod, 3)} m, teren {f(zt, 2)} m → zagłębienie D = {f(D_ext, 2)} m.")
                a_sl = 0.12
                try:
                    a_sl = max(przekroj(str(slupy[0].get("przekroj"))).b / 1000, 0.1)
                except Exception:  # noqa: BLE001
                    pass
                r = fund.stopa(fid, B, Lf, hf, a_sl + 0.1, D_ext, Gk, Qk, p.grunt, beton, p, stal=self.stal)
                poz.wyniki.append(r)
                poz.przyjeto.append(f"Stopa {f(B * 100, 0)}×{f(Lf * 100, 0)}×{f(hf * 100, 0)} cm, {beton.klasa}; {r.zbrojenie_poprz}.")
                poz.prety = r.prety
                self.pos_fund.append(poz)
                rows.append([fid, "stopa", f"{f(B)}×{f(Lf)}", (D_ext, 2), (Gk, 1), (Qk, 1), f"{f(r.wykorzystanie * 100, 0)}%"])
                continue
            # ława: ściany na osi
            prof = Profil(Lax)
            sciany = []
            for w in m.sciany():
                if w.typ not in TYPY_NOSNE or w.id not in self.prof:
                    continue
                if w.z_od > top + 1.5:
                    continue
                lw = LineString([tuple(w.p1), tuple(w.p2)])
                if ln.distance(Point(*w.p1)) > 0.1 or ln.distance(Point(*w.p2)) > 0.1:
                    continue
                pv = self.prof[w.id]["dol"]
                for cs in pv.przypadki():
                    sw = [ln.project(Point(*w.pt(s_, 0.0))) for s_ in pv.s]
                    prof.dodaj(cs, sw, pv.get(cs))
                # ściana fundamentowa
                hfw = max(w.z_od - top, 0.0)
                tk = w.warstwa_konstr.d
                s_a, s_b = sorted([ln.project(Point(*w.p1)), ln.project(Point(*w.p2))])
                prof.dodaj_stale("G", tk * hfw * p.ciezar_zelbetu, s_a, s_b)
                sciany.append((w, hfw, tk))
            if not sciany:
                poz = Pozycja("", fid, f"Ława {fid}", "fundament")
                poz.uwagi.append("Nie znaleziono ścian nośnych na osi ławy — obciążenie nieznane.")
                self.pos_fund.append(poz)
                continue
            tw = max(tk for _, _, tk in sciany)
            OKNO = 2.0     # rozdział obciążenia przez ścianę i ławę [UPR]
            G = prof.srednia_ruchoma(prof.get("G"), OKNO)
            i_max = int(np.argmax(G + sum(prof.srednia_ruchoma(prof.get(c), OKNO) for c in prof.przypadki() if c != "G")))
            Gk = float(G[i_max])
            Ql = []
            for cs in prof.przypadki():
                if cs in ("G", "SB2", "QA_pA", "QA_pB"):
                    continue
                v = float(prof.srednia_ruchoma(prof.get(cs), OKNO)[i_max])
                if v > 1e-6:
                    Ql.append((v, p.psi_of({"QA": "A", "H": "H", "S1": "S", "S2": "S"}.get(cs, "A"))[0], cs))
            # śnieg/H — tylko wiodący z grupy dachu (maks.)
            roof = [q for q in Ql if q[2] in ("H", "S1", "S2")]
            Ql = [q for q in Ql if q[2] not in ("H", "S1", "S2")] + ([max(roof)] if roof else [])
            poz = Pozycja("", fid, f"Ława fundamentowa {fid} (B = {f(B)} m, h = {f(hf)} m, L = {f(Lax, 2)} m)", "fundament")
            poz.opis.append(f"Ława pod ścianami: {', '.join(w.id for w, _, _ in sciany)}; ściana fundamentowa h ≈ "
                            f"{f(max(hf_ for _, hf_, _ in sciany), 2)} m, t = {f(tw * 100, 0)} cm (ciężar jak beton 25 kN/m³ [UPR]). "
                            f"Spód ławy {f(spod, 3)} m; {'teren przy ławie ' + f(zt, 2) + ' m' if zewn else 'ława wewnętrzna, posadzka ' + f(z_posadzki, 3) + ' m'}"
                            f" → D = {f(D_ext if zewn else D_int, 2)} m (do nośności D_min = {f(D, 2)} m). "
                            "Obciążenie miarodajne: maks. średnia krocząca na długości 2,0 m wzdłuż ławy (rozdział przez ścianę "
                            "i ławę) [UPR].")
            poz.obciazenia.append(tabela(["Przypadek", "q_k [kN/m] (miarodajne)", "Σ na ławie [kN]"],
                                         [[cs, (float(prof.srednia_ruchoma(prof.get(cs), OKNO)[i_max]), 2), (prof.calka(cs), 1)]
                                          for cs in prof.przypadki()]))
            r = fund.lawa(fid, B, hf, tw, D, Gk, [(q, ps) for q, ps, _ in Ql], p.grunt, beton, p, dlugosc=Lax + B, zewnetrzna=zewn,
                          stal=self.stal)
            if zewn and D_ext < p.D_min_zewn:
                r.uwaga(f"Zagłębienie od terenu D = {f(D_ext, 2)} m < {f(p.D_min_zewn, 2)} m — pogłębić posadowienie (W-284).")
            poz.wyniki.append(r)
            poz.przyjeto.append(f"Ława {f(B * 100, 0)}×{f(hf * 100, 0)} cm, {beton.klasa}; zbrojenie podłużne {r.zbrojenie_podl}; "
                                f"poprzecznie: {r.zbrojenie_poprz}.")
            poz.prety = r.prety
            poz.dane.update({"G_k": Gk, "Q_k": sum(q for q, _, _ in Ql), "D": D, "sigma_d": r.sigma_d})
            if self.rys_dir:
                from . import rysunki
                poz.rysunki += rysunki.rys_lawa(fid, B, hf, tw, D_ext if zewn else D_int, prof, self.rys(f"lawa_{_slug(fid)}.png"))
            self.pos_fund.append(poz)
            rows.append([fid, "ława", f"{f(B)}×{f(hf)}", (D_ext if zewn else D_int, 2), (Gk, 1), (sum(q for q, _, _ in Ql), 1),
                         f"{f(r.wykorzystanie * 100, 0)}%"])
        self.fund_tabela = rows
        if self.rys_dir and fu.get("elementy"):
            from . import rysunki
            self.rys_fund = rysunki.rys_fundamenty(self, self.rys("fundamenty_plan.png"))

    def _plyta_fund(self, el, poz, beton):
        p = self.p
        P = Polygon(el["obrys"])
        hf = float(el.get("h", 0.3))
        N = {}
        qmax = 0.0
        for w in self.m.sciany():
            if w.id in self.prof and w.kond == self.m.kondygnacje[0].id:
                for cs in self.prof[w.id]["dol"].przypadki():
                    N[cs] = N.get(cs, 0.0) + self.prof[w.id]["dol"].calka(cs)
                qmax = max(qmax, float(self.prof[w.id]["dol"].srednia_ruchoma(
                    self.prof[w.id]["dol"].kombinacja({"G": p.gG_sup, "QA": p.gQ * 0.7}), 1.0).max()))
        Gk = N.get("G", 0.0) + P.area * hf * p.ciezar_zelbetu
        Qk = sum(v for c, v in N.items() if c in ("QA", "S2"))
        qk = (Gk + Qk) / P.area
        osi = fund.osiadanie(math.sqrt(P.area), math.sqrt(P.area), 0.5, qk, p.grunt, p, nazwa="Osiadanie płyty (średni nacisk)")
        ks = fund.k_podatnosci(qk, osi.s)
        poz.wyniki.append(osi)
        poz.wyniki.append(fund.plyta_winkler(hf, beton, qmax, ks, krawedz=True, p=p))
        poz.przyjeto.append(f"Płyta gr. {f(hf * 100, 0)} cm, {beton.klasa}; k_s = {f(ks, 0)} kN/m³ (z osiadania średniego) [UPR].")
        poz.uwagi.append("Płyta fundamentowa — model uproszczony (pasmo Winklera). Do PT: MES płyty na podłożu sprężystym.")

    # ============================================================================================
    def _numeruj(self):
        # dołącz zaległe obciążenia schodów do opisu (informacyjnie)
        grupy_poz = []
        order = [("Dachy i stropodachy", [p_ for p_ in self.pos_plyty if p_.tytul.startswith("Stropodach")]),
                 ("Stropy", [p_ for p_ in self.pos_plyty if p_.tytul.startswith("Strop ")]),
                 ("Płyty wspornikowe", [p_ for p_ in self.pos_plyty if p_.tytul.startswith("Płyta wspornikowa")]),
                 ("Schody", self.pos_schody), ("Belki i podciągi", self.pos_belki), ("Nadproża", self.pos_nadproza),
                 ("Wieńce", self.pos_wience), ("Słupy", self.pos_slupy), ("Ściany murowe", self.pos_sciany),
                 ("Fundamenty", self.pos_fund)]
        self.pozycje = []
        nr = 1
        for tytul, lst in order:
            if not lst:
                continue
            gp = Pozycja(str(nr), "", tytul, "grupa")
            for k, pz in enumerate(lst, 1):
                pz.nr = f"{nr}.{k}"
                gp.podpozycje.append(pz)
            self.pozycje.append(gp)
            nr += 1


def _kat(ln: LineString) -> float:
    (x0, y0), (x1, y1) = ln.coords[0], ln.coords[-1]
    return math.atan2(y1 - y0, x1 - x0) % math.pi


def _slug(s: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s)[:40]
