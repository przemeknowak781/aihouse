"""Dane tomu PT-4 IE pobierane przy każdym uruchomieniu z JEDYNYCH źródeł projektu (bez liczb wpisanych ręcznie).

* ``model/budynek.yaml`` + ``dzialka.yaml`` + ``instalacje.yaml`` + ``wyposazenie.yaml`` — ``lamela.model`` / YAML
  (kubatura brutto, uzbrojenie terenu: ZKP, WLZ, kanalizacja teletechniczna, miejsca postojowe);
* ``lamela.obliczenia.fizyka_energia.oblicz_wszystko`` — Φ_HL i strumienie powietrza (moc PC i centrali w bilansie
  mocy), charakterystyka energetyczna (udział PV — odsyłacz do PT-3 IS);
* ``lamela.obliczenia.instalacje.oblicz_wszystko`` — moduły ``elektryka``: bilans mocy, obwody (WLZ, dobór przewodów
  i zabezpieczeń, ∆U, Z_s, SPD, PWP), fotowoltaika, ocena ryzyka piorunowego i uziom;
* ``projekt/06_PT_instalacje_elektryczne/rysunki/raport_widokow.json`` i ``BRAKI_DANYCH.md`` — arkusze i braki modelu;
  kontrola aktualności arkuszy wobec bieżących obliczeń (schemat RG, model PC, strumień centrali).
"""
from __future__ import annotations

import json
import math
import pickle
import re
import time
from pathlib import Path

from pt_is_dane import REPO, L, Opis, _yaml, rel  # noqa: F401 — wspólne narzędzia tomów PT

from lamela.dokumenty import Arkusz

KAT_IE = REPO / "projekt/06_PT_instalacje_elektryczne"
KAT_RYS = KAT_IE / "rysunki"
KAT_ZRODLA = REPO / "projekt/09_opis_i_zalaczniki/PT_IE"
P_MOSTKI = REPO / "projekt/08_obliczenia/mostki/wyniki_mostki.json"
P_WYM = REPO / "docs/10_podstawy_prawne/wymagania.yaml"
MODULY = ("bilans", "obwody", "pv", "odgromowa")
NAZWY_MOD = {"bilans": "Bilans mocy, moc przyłączeniowa, podział na fazy",
             "obwody": "WLZ, obwody, zabezpieczenia, ∆U, samoczynne wyłączenie, SPD, PWP",
             "pv": "Instalacja fotowoltaiczna (≤ 6,5 kWp)",
             "odgromowa": "Ocena ryzyka piorunowego, uziom, połączenia wyrównawcze"}
SZEREG_S = (1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0, 50.0)       # mm² — szereg przekrojów znamionowych


class DanePTIE:
    """Komplet danych PT-4 IE. Atrybuty: ``m`` (model), ``B``/``Dz``/``I``/``Wy`` (surowe YAML), ``wym`` (rejestr),
    ``R`` (fizyka/energia), ``W`` (instalacje), ``Wd`` (``do_dict`` modułów), ``bil``/``obw``/``pv``/``odg``,
    ``kubatura``, ``arkusze``, ``ark_braki``, ``ark_info``, ``braki_md``, ``otwarte`` (sprawy do zamknięcia),
    ``propozycje`` (warunek niespełniony → rozwiązanie wyznaczone z wyniku obliczeń)."""

    def __init__(self, *, cache: Path | None = None, bez_arkuszy: bool = False, log=print):
        t0 = time.time()
        self.p_bud, self.p_dz = REPO / "model/budynek.yaml", REPO / "model/dzialka.yaml"
        self.p_inst, self.p_wyp = REPO / "model/instalacje.yaml", REPO / "model/wyposazenie.yaml"
        self.B, self.Dz = _yaml(self.p_bud), _yaml(self.p_dz)
        self.I = _yaml(self.p_inst).get("instalacje") or {}
        self.Wy = _yaml(self.p_wyp).get("wyposazenie") or []
        self.wym = _yaml(P_WYM)
        self.otwarte: list[str] = []
        self.propozycje: list[dict] = []
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
        self.Wd = {k: self.W[k].do_dict() for k in MODULY}
        self.bil, self.obw, self.pv, self.odg = (self.W[k] for k in MODULY)
        self.ep = self.R["ep"]
        self.ep0 = next((w for w in self.R["ep_alt"] if w.system.pv is None and "bez PV" in w.system.nazwa), None)
        kb = self.m.kubatura_brutto()
        self.kubatura, self.kubatura_skl = float(kb["razem"]), kb.get("skladniki") or {}
        self.braki_md = (KAT_IE / "BRAKI_DANYCH.md").read_text(encoding="utf-8") \
            if (KAT_IE / "BRAKI_DANYCH.md").exists() else ""
        self._arkusze(bez_arkuszy)
        self._kontrole()

    # ------------------------------------------------------------------ obliczenia
    def _oblicz(self, log):
        from lamela.obliczenia import fizyka_energia as FE
        from lamela.obliczenia import instalacje as INS
        from lamela.obliczenia.fizyka import mostki as MB
        sym = MB.wczytaj_wyniki_symulacji(P_MOSTKI) if P_MOSTKI.exists() else None
        self.R = FE.oblicz_wszystko(self.m, wyniki_symulacji=sym)
        log(f"  fizyka/EP: EP = {self.R['ep'].EP:.1f} kWh/(m²·rok)")
        self.W = INS.oblicz_wszystko(str(self.p_bud), str(self.p_dz), str(self.p_wyp), str(self.p_inst),
                                     phi_hl=self.R["obc"], wentylacja=self.R["went"], schematy=False)

    # ------------------------------------------------------------------ dostęp do wyników
    def v(self, sekcja: str, klucz: str, domyslna=None):
        return ((self.wym.get(sekcja) or {}).get(klucz) or {}).get("wartosc", domyslna)

    def warunki(self, modul: str) -> list:
        return list(getattr(self.W[modul], "warunki", []) or [])

    def niespelnione(self) -> list[tuple[str, object]]:
        return [(k, x) for k in MODULY for x in self.warunki(k) if x.ok is False]

    def obwod(self, ident: str):
        return next((o for o in self.obw.obwody if o.odb.id == ident), None)

    def obwody_grupy(self, *grupy) -> list:
        return [o for o in self.obw.obwody if o.odb.grupa in grupy]

    def uzbrojenie(self, branza: str) -> dict:
        return next((x for x in ((self.Dz.get("uzbrojenie") or {}).get("projektowane") or [])
                     if x.get("branza") == branza), {})

    def obiekt(self, ident: str) -> dict:
        return next((x for x in ((self.Dz.get("uzbrojenie") or {}).get("obiekty") or []) if x.get("id") == ident), {})

    @property
    def miejsca_postojowe(self) -> list[dict]:
        return list(self.Dz.get("miejsca_postojowe") or [])

    @property
    def kategoria_rcd(self) -> dict:
        """Liczba obwodów wg rodzaju ochrony różnicowoprądowej (tekst z obliczeń)."""
        out: dict = {}
        for o in self.obw.obwody:
            out.setdefault(o.odb.rcd, []).append(o.odb.id)
        return out

    # ------------------------------------------------------------------ arkusze
    def _arkusze(self, bez: bool):
        p = KAT_RYS / "raport_widokow.json"
        rap = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"arkusze": []}
        cfg = _yaml(REPO / "model/arkusze_ie.yaml")
        self.raport_rys = rap
        self.arkusze, self.ark_braki = [], []
        self.ark_info = [str(x).strip() for x in rap.get("problemy", [])]
        w_rap = {a["nr"] for a in rap.get("arkusze", [])}
        lista = list(rap.get("arkusze", [])) + [
            dict(nr=c["nr"], tytul=c.get("tytul", c["nr"]), skala=f"1:{c.get('skala', 50)}", pliki={})
            for c in (cfg.get("arkusze") or []) if c.get("nr") and c["nr"] not in w_rap]
        if not lista:
            self.otwarte.append("Brak raportu arkuszy IE (raport_widokow.json) — część rysunkowa niekompletna.")
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
        self.rozb_rys: list[str] = []
        if not bez:
            self._aktualnosc_rysunkow()
        if p.exists() and p.stat().st_mtime < self.p_bud.stat().st_mtime:
            self.otwarte.append("Arkusze IE wygenerowano przed ostatnią zmianą modelu — przed wydaniem wygenerować "
                                "ponownie (tools/generuj_widoki.py --arkusze model/arkusze_ie.yaml).")

    def arkusze_nr(self, *slowa) -> str:
        """Numery arkuszy, których tytuł zawiera wszystkie ``slowa`` (bez rozróżniania wielkości liter)."""
        nr = [a.nr for a in self.arkusze if all(s.lower() in (a.tytul or "").lower() for s in slowa)]
        return ", ".join(nr) if nr else "—"
