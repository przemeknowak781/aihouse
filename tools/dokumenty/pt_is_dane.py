"""Dane tomu PT-3 IS pobierane przy każdym uruchomieniu z JEDYNYCH źródeł projektu (bez liczb wpisanych ręcznie).

* ``model/budynek.yaml`` + ``dzialka.yaml`` + ``instalacje.yaml`` + ``wyposazenie.yaml`` — ``lamela.model`` / YAML;
* ``lamela.obliczenia.fizyka_energia.oblicz_wszystko`` — obudowa (U, H_TB z ``projekt/08_obliczenia/mostki``),
  bilans wentylacji, obciążenie cieplne PN-EN 12831, charakterystyka energetyczna (warianty A, A0 bez PV, B, C);
* ``lamela.obliczenia.instalacje.oblicz_wszystko`` — woda i c.w.u., kanalizacja, wody opadowe i retencja, drenaż,
  ogrzewanie (PC, podłogówka, bufor, naczynia, hałas), bilans mocy (PT-4 IE — tylko odczyt dla § 23 pkt 11 lit. a);
* ``projekt/05_PT_instalacje_sanitarne/rysunki/raport_widokow.json`` i ``BRAKI_DANYCH.md`` — arkusze i braki modelu.
"""
from __future__ import annotations

import json
import pickle
import re
import sys
import textwrap
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
for _p in (REPO / "src", REPO / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from lamela.dokumenty import Arkusz, liczba  # noqa: E402

KAT_IS = REPO / "projekt/05_PT_instalacje_sanitarne"
KAT_RYS = KAT_IS / "rysunki"
KAT_ZRODLA = REPO / "projekt/09_opis_i_zalaczniki/PT_IS"
P_MOSTKI = REPO / "projekt/08_obliczenia/mostki/wyniki_mostki.json"
P_WYM = REPO / "docs/10_podstawy_prawne/wymagania.yaml"
MODULY = ("woda", "kanalizacja", "deszczowa", "drenaz", "ogrzewanie")


def L(v, n=2, pusty="—"):
    """Liczba w zapisie polskim albo „—”."""
    return pusty if v is None else liczba(v, n)


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def _yaml(p: Path) -> dict:
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.exists() else {}


class DanePTIS:
    """Komplet danych PT-3 IS. Atrybuty: ``m`` (model), ``B``/``Dz``/``I``/``Wy`` (surowe YAML), ``wym`` (rejestr),
    ``R`` (fizyka/energia), ``W`` (instalacje), ``Wd`` (``do_dict`` modułów), ``ep``/``ep0`` (EP z PV / bez PV),
    ``arkusze``, ``ark_braki``, ``ark_info``, ``braki_md``, ``otwarte`` (sprawy do zamknięcia)."""

    def __init__(self, *, cache: Path | None = None, bez_arkuszy: bool = False, log=print):
        t0 = time.time()
        self.p_bud, self.p_dz = REPO / "model/budynek.yaml", REPO / "model/dzialka.yaml"
        self.p_inst, self.p_wyp = REPO / "model/instalacje.yaml", REPO / "model/wyposazenie.yaml"
        self.B, self.Dz = _yaml(self.p_bud), _yaml(self.p_dz)
        self.I = _yaml(self.p_inst).get("instalacje") or {}
        self.Wy = _yaml(self.p_wyp).get("wyposazenie") or []
        self.wym = _yaml(P_WYM)
        self.otwarte: list[str] = []
        self.t_modelu = time.strftime("%Y-%m-%d %H:%M", time.localtime(max(
            p.stat().st_mtime for p in (self.p_bud, self.p_dz, self.p_inst, self.p_wyp) if p.exists())))
        from lamela.model import load_model
        self.m = load_model(self.p_bud, self.p_dz, strict=False)
        if cache and Path(cache).exists():                    # tylko podgląd układu — nie do wydania
            self.R, self.W = pickle.loads(Path(cache).read_bytes())
            self.z_cache = True
            log(f"  obliczenia z pamięci podręcznej {cache} (PODGLĄD)")
        else:
            self._oblicz(log)
            self.z_cache = False
            if cache:
                Path(cache).write_bytes(pickle.dumps((self.R, self.W)))
        log(f"  obliczenia: {time.time() - t0:.0f} s")
        self.Wd = {k: self.W[k].do_dict() for k in MODULY + ("bilans",)}
        self.ep = self.R["ep"]
        self.ep0 = next((w for w in self.R["ep_alt"] if w.system.pv is None and "bez PV" in w.system.nazwa), None)
        self.obc, self.went, self.og = self.R["obc"], self.R["went"], self.W["ogrzewanie"]
        self.braki_md = (KAT_IS / "BRAKI_DANYCH.md").read_text(encoding="utf-8") \
            if (KAT_IS / "BRAKI_DANYCH.md").exists() else ""
        self._arkusze(bez_arkuszy)
        self._kontrole()

    # ------------------------------------------------------------------ obliczenia
    def _oblicz(self, log):
        from lamela.obliczenia import fizyka_energia as FE
        from lamela.obliczenia import instalacje as INS
        from lamela.obliczenia.fizyka import mostki as MB
        sym = MB.wczytaj_wyniki_symulacji(P_MOSTKI) if P_MOSTKI.exists() else None
        if sym is None:
            self.otwarte.append("Brak wyników symulacji mostków (projekt/08_obliczenia/mostki/wyniki_mostki.json) — "
                                "H_TB i EP policzono z Ψ domyślnych PN-EN ISO 14683.")
        self.R = FE.oblicz_wszystko(self.m, wyniki_symulacji=sym)
        log(f"  fizyka/EP: EP = {self.R['ep'].EP:.1f} kWh/(m²·rok)")
        self.W = INS.oblicz_wszystko(str(self.p_bud), str(self.p_dz), str(self.p_wyp), str(self.p_inst),
                                     phi_hl=self.R["obc"], wentylacja=self.R["went"], schematy=False)

    # ------------------------------------------------------------------ rejestr wymagań
    def v(self, sekcja: str, klucz: str, domyslna=None):
        return ((self.wym.get(sekcja) or {}).get(klucz) or {}).get("wartosc", domyslna)

    # ------------------------------------------------------------------ arkusze
    def _arkusze(self, bez: bool):
        p = KAT_RYS / "raport_widokow.json"
        rap = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"arkusze": []}
        cfg = _yaml(REPO / "model/arkusze_is.yaml")
        self.raport_rys = rap
        self.arkusze, self.ark_braki = [], []
        self.ark_info = [str(x).strip() for x in rap.get("problemy", [])]
        w_rap = {a["nr"] for a in rap.get("arkusze", [])}
        lista = list(rap.get("arkusze", [])) + [
            dict(nr=c["nr"], tytul=c.get("tytul", c["nr"]), skala=f"1:{c.get('skala', 50)}", pliki={})
            for c in (cfg.get("arkusze") or []) if c.get("nr") and c["nr"] not in w_rap]
        if not lista:
            self.otwarte.append("Brak raportu arkuszy IS (raport_widokow.json) — część rysunkowa niekompletna.")
        for a in lista:
            pdf = Path((a.get("pliki") or {}).get("pdf") or "")
            pdf = pdf if pdf.is_absolute() else REPO / pdf
            if bez or not (a.get("pliki") or {}).get("pdf") or not pdf.exists():
                self.arkusze.append(Arkusz.planowany(a["nr"], a["tytul"], a.get("skala") or "—", a.get("format") or "A3"))
                if not bez:
                    self.ark_braki.append(f"{a['nr']}: brak pliku PDF arkusza „{a['tytul']}” — strona zastępcza")
                continue
            if not (a.get("qa") or {}).get("ok", True):
                self.ark_braki.append(f"{a['nr']}: kontrola QA arkusza z błędami: {a['qa'].get('errors')}")
            self.arkusze.append(Arkusz.z_pdf(pdf))
        if p.exists() and p.stat().st_mtime < self.p_bud.stat().st_mtime:
            self.otwarte.append("Arkusze IS wygenerowano przed ostatnią zmianą modelu — przed wydaniem wygenerować "
                                "ponownie (tools/generuj_widoki.py --arkusze model/arkusze_is.yaml).")

    def arkusze_nr(self, *slowa) -> str:
        """Numery arkuszy, których tytuł zawiera wszystkie ``slowa`` (bez rozróżniania wielkości liter)."""
        nr = [a.nr for a in self.arkusze if all(s.lower() in (a.tytul or "").lower() for s in slowa)]
        return ", ".join(nr) if nr else "—"
