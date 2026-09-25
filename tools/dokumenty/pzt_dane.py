"""Dane PZT/ZL pobierane przy każdym uruchomieniu z JEDYNYCH źródeł projektu (żadnych liczb wpisanych ręcznie):

* ``model/budynek.yaml`` + ``model/dzialka.yaml`` (+ ``instalacje.yaml``, ``wyposazenie.yaml``) — ``lamela.model``;
* ``lamela.wskazniki`` — wskaźniki MPZP, wysokości, bilans terenu (definicje upzp art. 2 pkt 28–35);
* ``tools/audyt_wt.py`` (A1) — odległości od granic (WT § 12), linia zabudowy, lokalizacja PC, retencji, pojemników;
* ``lamela.obliczenia`` — deszczowa/retencja (Aquanet 2024), hałas PC, przykanalik;
* ``docs/10_podstawy_prawne/wymagania.yaml`` — wartości normatywne z podstawą (``zrodlo``) i id rejestru (W-xxx).
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import LineString, Point, Polygon

REPO = Path(__file__).resolve().parents[2]
for p in (REPO / "src", REPO / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from lamela import wskazniki as WS  # noqa: E402
from lamela.ir import build_ir  # noqa: E402
from lamela.model import load_model, make_polygon  # noqa: E402


def _poly(r):
    return make_polygon(r) if r and len(r) >= 3 else None


class DaneZag:
    """Komplet danych zagospodarowania; wszystkie wartości liczbowe wyliczane z modelu i obliczeń."""

    def __init__(self, repo: Path = REPO, *, z_obliczeniami: bool = True):
        self.repo = repo
        self.p_bud, self.p_dz = repo / "model/budynek.yaml", repo / "model/dzialka.yaml"
        self.m = load_model(self.p_bud, self.p_dz, strict=False)
        self.ir = build_ir(self.m, otoczenie=True, auta=False)
        self.W = WS.wskazniki(self.m, ir=self.ir)
        self.G = self.W["_geom"]
        self.dz = self.m.raw_dz or {}
        self.bud = self.m.raw or {}
        self.WYM = yaml.safe_load(open(repo / "docs/10_podstawy_prawne/wymagania.yaml", encoding="utf-8"))
        self.zero = float((self.bud.get("uklad") or {}).get("zero_abs", self.WYM["meta"]["zero_abs_m_npm"]))
        self.plot = self.G["plot"]
        self.fp = self.G["footprint"]          # rzut ścian zewnętrznych wszystkich kondygnacji (układ działki)
        self.p0 = self.G["p0"]
        self._audyt()
        self.inst = self._instalacje() if z_obliczeniami else {}

    # ------------------------------------------------------------------ wymagania.yaml
    def wym(self, sekcja: str, klucz: str):
        w = self.WYM[sekcja][klucz]
        return w["wartosc"], w["zrodlo"], w.get("id") or ""

    def w(self, klucz: str):
        """Wartość wskaźnika z ``lamela.wskazniki``."""
        return self.W[klucz]["wartosc"]

    # ------------------------------------------------------------------ audyt A1 (tylko odległości i PZT — ~3 s)
    def _audyt(self):
        import audyt_wt as AW
        a = AW.AudytWT(self.p_bud.resolve(), self.p_dz.resolve(), self.repo / "docs/10_podstawy_prawne/wymagania.yaml")
        a.odleglosci()
        a._pc_i_pzt()
        self.audyt = a
        self.odl_rows = a.A.tabele.get("odleglosci", [])
        self.lz_rezerwa = float(a.A.info.get("linia_zabudowy_rezerwa", float("nan")))
        self.granice = a.granice          # [{kier, line, n, drogowa}] — układ działki

    def odl_min(self, kier: str, rodzaj_prefiks: str, z_otworami: bool | None = None):
        """Minimalna odległość elementów danego rodzaju od granicy ``kier`` (N/E/S/W) — (d, element) albo None."""
        rows = [r for r in self.odl_rows if r["kier"] == kier and r["rodzaj"].startswith(rodzaj_prefiks)
                and (z_otworami is None or (("z otworami" in r["rodzaj"]) == z_otworami))]
        if not rows:
            return None
        r = min(rows, key=lambda r: r["d"])
        return r["d"], r["el"], r["lim"]

    def wyniki_audytu(self, sekcja: str) -> list:
        return [x for x in self.audyt.A.wyniki if x.sekcja == sekcja]

    # ------------------------------------------------------------------ obliczenia instalacyjne
    def _instalacje(self) -> dict:
        from lamela.obliczenia.inst_wspolne import dane_z_modelu
        from lamela.obliczenia.sanitarne.deszczowa import oblicz_deszczowa
        from lamela.obliczenia.sanitarne.kanalizacja import ParametryKan, oblicz_kanalizacje
        from lamela.obliczenia.sanitarne.ogrzewanie import oblicz_ogrzewanie
        from lamela.obliczenia.sanitarne.woda import ParametryWoda, oblicz_wode
        r = self.repo / "model"
        dane = dane_z_modelu(r / "budynek.yaml", r / "dzialka.yaml", r / "wyposazenie.yaml", r / "instalacje.yaml")
        woda0 = oblicz_wode(dane, ParametryWoda())
        return dict(dane=dane, deszczowa=oblicz_deszczowa(dane), kanalizacja=oblicz_kanalizacje(dane),
                    ogrzewanie=oblicz_ogrzewanie(dane, cwu=woda0.cwu), par_kan=ParametryKan())

    # ------------------------------------------------------------------ teren
    def teren_istn(self) -> dict:
        """Rzędne terenu istniejącego w granicach działki, spadek płaszczyzny MNK (kierunek i wartość)."""
        pts = np.asarray([p for p in (self.dz.get("teren") or {}).get("punkty") or []], float)
        ins = np.array([self.plot.buffer(0.01).contains(Point(x, y)) for x, y, _ in pts]) if len(pts) else []
        q = pts[ins] if len(pts) else pts
        A = np.c_[q[:, :2], np.ones(len(q))]
        a, b, _c = np.linalg.lstsq(A, q[:, 2], rcond=None)[0]
        kier = {(1, 1): "północny wschód", (1, -1): "południowy wschód", (-1, 1): "północny zachód",
                (-1, -1): "południowy zachód"}
        spad_x, spad_y = abs(a) * 100, abs(b) * 100
        return dict(z_min=float(q[:, 2].min()), z_max=float(q[:, 2].max()), n=len(q),
                    spadek_y=spad_y, ku_y="południu" if b > 0 else "północy",
                    spadek_x=spad_x, ku_x="zachodowi" if a > 0 else "wschodowi",
                    wzrost_ku=kier.get((int(np.sign(a) or 1), int(np.sign(b) or 1)), "—"))

    def teren_proj(self) -> dict:
        pp = np.asarray((self.dz.get("teren") or {}).get("punkty_projektowane") or [], float)
        return dict(z_min=float(pp[:, 2].min()), z_max=float(pp[:, 2].max()), n=len(pp)) if len(pp) else {}

    def wymiary_dzialki(self) -> tuple[float, float]:
        x0, y0, x1, y1 = self.plot.bounds
        return x1 - x0, y1 - y0

    # ------------------------------------------------------------------ otoczenie
    def sasiedzi(self) -> list[dict]:
        out = []
        for s in self.dz.get("sasiedzi") or []:
            zab = _poly(s.get("zabudowa"))
            obr = _poly(s.get("obrys"))
            out.append(dict(nr=str(s.get("nr")), opis=s.get("opis", ""), wys=s.get("wys"),
                            odl_bud=float(self.fp.distance(zab)) if zab is not None else None,
                            odl_granicy=float(zab.distance(self.plot)) if zab is not None else None,
                            przylega=bool(obr is not None and obr.distance(self.plot) < 0.01)))
        return out

    def droga(self) -> dict:
        d = self.dz.get("droga") or {}
        lr, jz = _poly(d.get("linie_rozgraniczajace")), _poly(d.get("jezdnia"))
        szer_lr = (lr.bounds[3] - lr.bounds[1]) if lr is not None else None
        return dict(symbol=d.get("symbol", "—"), nazwa=d.get("nazwa", "—"), nawierzchnia=d.get("nawierzchnia", "—"),
                    szer_lr=szer_lr, szer_jezdni=(jz.bounds[3] - jz.bounds[1]) if jz is not None else None,
                    odl_bud_jezdnia=float(self.fp.distance(jz)) if jz is not None else None,
                    odl_bud_lr=float(self.fp.distance(lr)) if lr is not None else None)

    def obiekt(self, oid: str) -> dict | None:
        return next((o for o in (self.dz.get("uzbrojenie") or {}).get("obiekty") or [] if o.get("id") == oid), None)

    def odl_hydrantu(self):
        h = self.obiekt("HYDR")
        return (float(Point(*h["xy"]).distance(self.fp)), h) if h else (None, None)

    def drzewa(self) -> list[dict]:
        return list(self.dz.get("drzewa") or [])

    def zielen_pow(self) -> dict:
        """Powierzchnie typów zieleni (rzut — informacyjnie; PBC netto z ``lamela.wskazniki``)."""
        out = {}
        for z in self.dz.get("zielen") or []:
            g = _poly(z.get("obrys"))
            if g is not None and z.get("typ") != "trawnik":
                out[z["typ"]] = out.get(z["typ"], 0.0) + g.area
        return out

    def ogrodzenie_od_drogi(self) -> list[dict]:
        lr = _poly((self.dz.get("droga") or {}).get("linie_rozgraniczajace"))
        out = []
        for o in self.dz.get("ogrodzenie") or []:
            ln = LineString(o["linia"])
            out.append(dict(o, od_drogi=bool(lr is not None and ln.distance(lr) < 0.01 and ln.length > 0
                                              and all(Point(p).distance(lr) < 0.01 for p in o["linia"])),
                            dl=ln.length))
        return out

    def mp_odleglosci(self) -> list[tuple]:
        """(id, typ, wymiary, min odl. od granic niedrogowych, odl. od okien P0) — WT § 19, § 21."""
        out = []
        for mp in self.dz.get("miejsca_postojowe") or []:
            g = _poly(mp["obrys"])
            x0, y0, x1, y1 = g.bounds
            d = min(g.distance(gr["line"]) for gr in self.granice if not gr["drogowa"])
            out.append((mp["id"], mp.get("typ"), (min(x1 - x0, y1 - y0), max(x1 - x0, y1 - y0)), d))
        return out
