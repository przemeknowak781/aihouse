"""Dane PAB pobierane przy każdym uruchomieniu z JEDYNYCH źródeł projektu (żadnych liczb wpisanych ręcznie):

* ``model/budynek.yaml`` + ``dzialka.yaml`` + ``instalacje.yaml`` + ``wyposazenie.yaml`` — ``lamela.model`` / YAML;
* ``lamela.wskazniki`` — wskaźniki MPZP, wysokość zabudowy (upzp art. 2 pkt 30) i wysokość wg WT § 6;
* ``tools/audyt_wt.py`` (A1) — powierzchnie pomieszczeń ze strefami wysokości, PU wg W-316, odległości od granic;
* ``lamela.obliczenia`` — fizyka i EP (``fizyka_energia``), instalacje (woda, kanalizacja, deszczowa, drenaż, PC, PV,
  bilans mocy, ochrona odgromowa); ``projekt/08_obliczenia/mostki`` — ψ z symulacji PN-EN ISO 10211;
* ``docs/10_podstawy_prawne/wymagania.yaml`` — wartości normatywne z podstawą (``zrodlo``) i id rejestru (W-xxx);
* ``projekt/03_PAB/rysunki/raport_widokow.json`` (komplet AR — inny zespół) albo ``model/arkusze.yaml`` (plan arkuszy).
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import yaml
from shapely.geometry import Point
from shapely.ops import unary_union

REPO = Path(__file__).resolve().parents[2]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from lamela import wskazniki as WS  # noqa: E402
from lamela.ir import build_ir  # noqa: E402
from lamela.model import load_model, make_polygon  # noqa: E402

P_WYM = REPO / "docs/10_podstawy_prawne/wymagania.yaml"
P_MOSTKI = REPO / "projekt/08_obliczenia/mostki/wyniki_mostki.json"
KAT_RYS = [REPO / "projekt/03_PAB/rysunki", REPO / "projekt/03_PAB/widoki", REPO / "projekt/03_PAB"]


def _yaml(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


class DanePAB:
    """Komplet danych PAB. Atrybuty: ``m`` (model), ``B``/``Dz``/``I``/``Wy`` (surowe YAML), ``wym`` (rejestr),
    ``audyt`` (A1), ``pom`` (wiersze pomieszczeń), ``pu`` (PU wg W-316), ``w`` (wskaźniki), ``R`` (fizyka/EP),
    ``W`` (instalacje), ``mostki``, ``kub``, ``arkusze_cfg``/``raport_rys``, ``otwarte`` (sprawy do zamknięcia)."""

    def __init__(self, repo: Path = REPO, *, log=print):
        t0 = time.time()
        self.repo = repo
        self.p_bud, self.p_dz = repo / "model/budynek.yaml", repo / "model/dzialka.yaml"
        self.p_inst, self.p_wyp = repo / "model/instalacje.yaml", repo / "model/wyposazenie.yaml"
        self.B, self.Dz = _yaml(self.p_bud), _yaml(self.p_dz)
        self.I = (_yaml(self.p_inst) or {}).get("instalacje") or {}
        self.Wy = (_yaml(self.p_wyp) or {}).get("wyposazenie") or []
        self.wym = _yaml(P_WYM)
        self.otwarte: list[str] = []
        self.m = load_model(self.p_bud, self.p_dz, strict=False)
        log(f"  model: {len(self.m.pomieszczenia())} pomieszczeń, {len(self.m.kondygnacje)} kondygnacje")
        self._audyt()
        log(f"  audyt A1: {self.audyt_statusy} ({time.time() - t0:.0f} s)")
        self.ir = build_ir(self.m, otoczenie=True, auta=False)
        self.w = WS.wskazniki(self.m, ir=self.ir)
        self.kub = self.m.kubatura_brutto()
        self.kubatura = sum(self.kub["skladniki"].values())
        log(f"  wskaźniki i kubatura ({time.time() - t0:.0f} s)")
        self._energia()
        log(f"  fizyka/EP: EP = {self.ep.EP:.1f} ({time.time() - t0:.0f} s)")
        self._instalacje()
        log(f"  instalacje ({time.time() - t0:.0f} s)")
        self._geometria()
        self._arkusze()
        self._kontrole()

    # ------------------------------------------------------------------ rejestr wymagań
    def v(self, sekcja: str, klucz: str, domyslna=None):
        return ((self.wym.get(sekcja) or {}).get(klucz) or {}).get("wartosc", domyslna)

    def zr(self, sekcja: str, klucz: str) -> str:
        """Podstawa wartości normatywnej z rejestru: „<zrodlo> [W-xxx]”."""
        from redakcja import PODSTAWY, podstawa
        x = (self.wym.get(sekcja) or {}).get(klucz) or {}
        if (sekcja, klucz) in PODSTAWY:
            return PODSTAWY[(sekcja, klucz)].replace("*", "\\*")
        t = podstawa(x.get("zrodlo", "")).replace("*", "\\*")
        return t + (f" [{x['id']}]" if x.get("id") and f"{x['id']}]" not in t and f"{x['id']}," not in t else "")

    # ------------------------------------------------------------------ audyt A1 (PU W-316, odległości)
    def _audyt(self):
        import audyt_wt as AW
        a = AW.AudytWT(self.p_bud, self.p_dz, P_WYM)
        self.audyt = a.run()
        self.audyt_obj = a
        self.pom = self.audyt.tabele.get("pomieszczenia", [])
        self.pu = self.audyt.info.get("PU", {})
        self.odl = self.audyt.tabele.get("odleglosci", [])
        self.audyt_statusy = {s: sum(1 for x in self.audyt.wyniki if x.status == s) for s in AW.STATUSY}
        self.granice = a.granice
        self.uklad = a.U

    # ------------------------------------------------------------------ fizyka, EP, instalacje
    def _energia(self):
        from lamela.obliczenia import fizyka_energia as FE
        from lamela.obliczenia.fizyka import mostki as MB
        self.mostki = json.loads(P_MOSTKI.read_text(encoding="utf-8")) if P_MOSTKI.exists() else {}
        sym = MB.wczytaj_wyniki_symulacji(P_MOSTKI) if P_MOSTKI.exists() else None
        if sym is None:
            self.otwarte.append("Brak wyników symulacji mostków (projekt/08_obliczenia/mostki/wyniki_mostki.json) — "
                                "EP policzono z Ψ domyślnych PN-EN ISO 14683.")
        self.R = FE.oblicz_wszystko(self.m, wyniki_symulacji=sym)
        self.ep = self.R["ep"]
        self.ob = self.R["obudowa"]
        self.obc = self.R["obc"]
        self.went = self.R["went"]

    def _instalacje(self):
        from lamela.obliczenia import instalacje as INS
        self.W = INS.oblicz_wszystko(str(self.p_bud), str(self.p_dz), str(self.p_wyp), str(self.p_inst),
                                     phi_hl=self.obc, wentylacja=self.went, schematy=False)
        self.Wd = {k: self.W[k].do_dict() for k in ("woda", "kanalizacja", "deszczowa", "drenaz", "ogrzewanie", "pv",
                                                   "bilans", "odgromowa")}

    # ------------------------------------------------------------------ geometria: wymiary, odległości
    def _geometria(self):
        g = self.w["_geom"]
        fp = g["footprint"]
        self.fp = fp
        pl = unary_union([fp] + [q for _i, q in g["plyty"]]) if g["plyty"] else fp
        x0, y0, x1, y1 = fp.bounds
        X0, Y0, X1, Y1 = pl.bounds
        self.wymiary = dict(dl=x1 - x0, szer=y1 - y0, dl_calk=X1 - X0, szer_calk=Y1 - Y0)
        self.wym_kond = {}
        for k in self.m.kondygnacje:
            b = self.m.obrys_kondygnacji(k.id).bounds
            self.wym_kond[k.id] = dict(nazwa=k.nazwa, dl=b[2] - b[0], szer=b[3] - b[1], rzedna=float(k.rzedna),
                                       h_kond=float(k.wys_kondygnacji or 0), h_sw=float(k.wys_w_swietle or 0))
        # odległości od granic (audyt A1, WT § 12) — minimum po kierunku i grupie elementów
        grp = {}
        for r in self.odl:
            rz = r["rodzaj"]
            key = ("ściany z otworami" if "z otworami" in rz else "ściany bez otworów" if rz.startswith("ściana")
                   else "tarasy i podesty" if rz.startswith("taras") else "elementy wysunięte (płyty, okapy, lamele)")
            k2 = (r["kier"], key)
            if k2 not in grp or r["d"] < grp[k2]["d"]:
                grp[k2] = dict(kier=r["kier"], grupa=key, d=r["d"], lim=r["lim"], el=r["el"])
        self.odl_min = sorted(grp.values(), key=lambda x: (x["kier"], x["grupa"]))
        # budynki sąsiednie (ppoż., WT § 271) — odległość od ścian i od płyt wysuniętych
        self.sasiedzi = []
        for s in self.Dz.get("sasiedzi") or []:
            zab = s.get("zabudowa") or []
            if len(zab) < 3:
                continue
            q = make_polygon(zab)
            self.sasiedzi.append(dict(nr=str(s.get("nr")), opis=s.get("opis", ""), d=fp.distance(q), d_pl=pl.distance(q)))
        # hydrant i droga
        ob = {o.get("id"): o for o in ((self.Dz.get("uzbrojenie") or {}).get("obiekty") or [])}
        h = ob.get("HYDR")
        self.hydrant = dict(opis=h.get("opis", ""), d=fp.distance(Point(*h["xy"]))) if h else None
        self.droga = self.Dz.get("droga") or {}
        self.nosniki = [(u.get("branza"), u.get("opis", "")) for u in
                        ((self.Dz.get("uzbrojenie") or {}).get("istniejace") or [])]

    # ------------------------------------------------------------------ rysunki PAB
    def _arkusze(self):
        self.arkusze_cfg = (_yaml(self.repo / "model/arkusze.yaml") or {})
        self.raport_rys, self.kat_rys = None, None
        for k in KAT_RYS:
            p = k / "raport_widokow.json"
            if p.exists():
                self.raport_rys, self.kat_rys = json.loads(p.read_text(encoding="utf-8")), k
                break
        if self.raport_rys is None:
            self.otwarte.append("Komplet rysunków PAB (projekt/03_PAB/rysunki/raport_widokow.json) nie jest jeszcze "
                                "wygenerowany — w części rysunkowej arkusze zastępcze wg model/arkusze.yaml.")

    # ------------------------------------------------------------------ kontrole spójności → „otwarte”
    def _kontrole(self):
        for x in self.audyt.wyniki:
            if x.status in ("NIEZGODNE", "UWAGA"):
                self.otwarte.append(f"Audyt A1 — {x.status}: {x.sekcja} / {x.element} / {x.parametr}: {x.wartosc} "
                                    f"(wymóg {x.wymog}; {x.podstawa}).")
        pc = (self.obc.dobor or {}).get("pc") or {}
        if "PRZYK" in str(pc.get("status", "")).upper():
            self.otwarte.append("Pompa ciepła: parametry (moc, SCOP, L_WA) z karty wyrobu przykładowego — do zastąpienia "
                                "DTR wybranego wyrobu (PT-IS); wpływa na EP, hałas na granicy i dobór mocy.")
        buf_mod = [x for x in self.Wy if x.get("typ") == "zasobnik" and "bufor" in str(x.get("opis", "")).lower()]
        buf_obl = self.Wd["ogrzewanie"].get("bufor_l")
        if buf_mod and buf_obl:
            self.otwarte.append(f"Bufor c.o.: w modelu (wyposazenie.yaml) „{buf_mod[0].get('opis')}”, z obliczeń "
                                f"ogrzewania min. {buf_obl} dm³ — ujednolicić w modelu (PT-IS).")
        if not self.B.get("projekt"):
            self.otwarte.append("Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji "
                                "`projekt:` w model/budynek.yaml; pola [DO UZUPEŁNIENIA].")

    # ------------------------------------------------------------------ pomocnicze do tabel
    def nr_iso(self, pid: str, kond: str) -> str:
        """Identyfikator modelu K.NN → numer arkuszy K+1.NN (PN-B-01025, parter = 1.xx; meta.numeracja_pomieszczen)."""
        try:
            return f"{int(kond[1:]) + 1}.{pid.split('.')[1]}"
        except (ValueError, IndexError):
            return pid

    def grupa_pu(self, r: dict) -> str:
        """Grupa zestawienia wg W-316 (ta sama reguła co ``audyt_wt`` — A.info['PU'])."""
        if r["rodzaj"] == "garaz":
            return "garaż"
        if r["kat"] in ("podstawowa", "pomocnicza"):
            return r["kat"]
        if r["kat"] == "techniczna":
            return "techniczna"
        return "klatka schodowa" if "klatka" in r["nazwa"].lower() else "komunikacja"

    def w_pu(self, r: dict) -> bool:
        return self.grupa_pu(r) in ("podstawowa", "pomocnicza", "komunikacja")

    def arkusze_ref(self, typ: str, **kw) -> list[str]:
        """Numery arkuszy PAB danego typu (rzut/dach/przekroj/elewacja) — z konfiguracji arkuszy modelu."""
        out = []
        for a in self.arkusze_cfg.get("arkusze") or []:
            if a.get("typ") == typ and all(a.get(k) == v for k, v in kw.items()):
                out.append(str(a["nr"]))
        return out
