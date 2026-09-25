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

OPS = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "==": "="}

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

    def trasa_wlz(self) -> str:
        """Opis trasy WLZ z modelu (uzbrojenie „en”) z przekrojem kabla wg bieżących obliczeń (opis w modelu może
        zawierać przekrój z wcześniejszej wersji — rozbieżność wykazywana w sprawach otwartych)."""
        t = str(self.uzbrojenie("en").get("opis") or "—")
        return re.sub(r"YKY \d×\d+", self.obw.wlz["przewod"], t)

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

    # ------------------------------------------------------------------ aktualność arkuszy wobec obliczeń
    def _tekst_arkusza(self, a) -> str:
        import pymupdf
        with pymupdf.open(a.plik) as doc:
            return " | ".join(ln for pg in doc for ln in pg.get_text().split("\n") if ln.strip())

    def _aktualnosc_rysunkow(self):
        """Porównanie treści arkuszy z bieżącymi obliczeniami: obwody na schemacie RG (zabezpieczenie, przewód, faza),
        WLZ, model PC, strumień centrali wentylacyjnej, moc PV. Rozbieżności → ``otwarte`` i ``rozb_rys``."""
        tx = {a.nr: self._tekst_arkusza(a) for a in self.arkusze if a.istnieje}
        pc = next((o.odb.nazwa for o in self.obw.obwody if o.odb.grupa == "pc"), "")
        pc_id = (re.search(r"PC-R290-\d+", pc) or [None])[0]
        went = next((o.odb.nazwa for o in self.obw.obwody if o.odb.grupa == "went"), "")
        V_obl = (re.search(r"V ≈ (\d+) m³/h", went) or [None, None])[1]
        inne: dict = {}
        for nr, t in tx.items():
            for m in set(re.findall(r"PC-R290-\d+", t)):
                if pc_id and m != pc_id:
                    inne.setdefault(f"model PC {m} (obliczenia: {pc_id})", []).append(nr)
            for m in set(re.findall(r"V ≈ (\d+) m³/h", t)):
                if V_obl and m != V_obl:
                    inne.setdefault(f"strumień centrali {m} m³/h (obliczenia: {V_obl} m³/h)", []).append(nr)
            for m in set(re.findall(r"WLZ (YKY \d×\d+)", t)):
                if m != self.obw.wlz["przewod"]:
                    inne.setdefault(f"WLZ {m} (obliczenia: {self.obw.wlz['przewod']})", []).append(nr)
        for opis, nr in inne.items():
            self.rozb_rys.append(f"{', '.join(sorted(set(nr)))}: {opis}")
        schemat = next((nr for nr, t in tx.items() if "SCHEMAT IDEOWY ROZDZIELNICY" in t.upper()), None)
        if schemat:
            wz = re.compile(r"((?:3P )?[BCD]\d+) \| 30mA \w+ \| (\S+ \d×[\d,]+)\s+L=\d+ m \| ∆U=[\d,]+% \| "
                            r"([LGD]\d+) \| (L[123]|3f)")
            rys = {m.group(3): (m.group(1), m.group(2), m.group(4)) for m in wz.finditer(tx[schemat])}
            rozn = []
            for o in self.obw.obwody:
                obl = (o.zab, o.przewod, "3f" if o.odb.fazy == 3 else o.odb.faza)
                r = rys.get(o.odb.id)
                if r is None:
                    rozn.append(f"{o.odb.id} brak na schemacie")
                elif r != obl:
                    rozn.append(f"{o.odb.id}: rysunek {' / '.join(r)}, obliczenia {' / '.join(obl)}")
            rozn += [f"{k} na schemacie, brak w obliczeniach" for k in rys if self.obwod(k) is None]
            if rozn:
                self.rozb_rys.append(f"{schemat} (schemat RG) — {len(rozn)} "
                                     f"{'obwód niezgodny' if len(rozn) == 1 else 'obwody niezgodne' if len(rozn) < 5 else 'obwodów niezgodnych'}"
                                     f" z bieżącymi obliczeniami (zabezpieczenie / przewód / faza): " + "; ".join(rozn))
        if self.rozb_rys:
            self.otwarte.append("Arkusze nieaktualne wobec bieżących obliczeń — przed wydaniem wygenerować ponownie "
                                "(rozdz. „Braki danych i zgodność części rysunkowej”): "
                                + ", ".join(sorted({n for r in self.rozb_rys for n in re.findall(r"PT-IE-\d+", r)}))
                                + f" ({len(self.rozb_rys)} {'rozbieżność' if len(self.rozb_rys) == 1 else 'rozbieżności'}).")

    # ------------------------------------------------------------------ kontrole spójności → „otwarte”
    def _przekroj(self, dU: float, s: float, lim: float) -> tuple[float, float] | None:
        """Najmniejszy przekrój z szeregu, przy którym ∆U ∝ 1/s spełnia limit (rezystancja żył odwrotnie
        proporcjonalna do przekroju; reaktancja pominięta — dla s ≤ 50 mm² Cu/Al pomijalna)."""
        for s2 in SZEREG_S:
            if s2 > s and dU * s / s2 <= lim:
                return s2, dU * s / s2
        return None

    def _kontrole(self):
        for mod, x in self.niespelnione():
            prop = None
            if mod == "obwody" and x.opis.startswith("WLZ: spadek"):
                prop = self._przekroj(x.wartosc, self.obw.par.WLZ_przekroj, x.limit)
                co = f"WLZ YKY {self.obw.par.WLZ_zyly}×{{s}} mm²"
            elif mod == "pv" and "DC" in x.opis and "Spadek" in x.opis:
                prop = self._przekroj(x.wartosc, self.pv.par.s_DC, x.limit)
                co = "przewody DC H1Z2Z2-K {s} mm²"
            opis = (f"Obliczenia ({NAZWY_MOD[mod]}) — warunek niespełniony: {x.opis}: {L(x.wartosc, 2)} {x.jedn} "
                    f"(wymaganie {OPS.get(x.op, x.op)} {L(x.limit, 2)} {x.jedn}; {x.podstawa})")
            if prop:
                s2, dU2 = prop
                roz = co.format(s=L(s2, 0))
                self.propozycje.append(dict(warunek=x.opis, modul=mod, wartosc=x.wartosc, limit=x.limit, jedn=x.jedn,
                                            rozwiazanie=roz, wartosc_po=dU2))
                opis += (f" — rozwiązanie: {roz} (∆U ≈ {L(dU2, 2)} {x.jedn} ≤ {L(x.limit, 2)} {x.jedn}; przeliczenie "
                         "proporcjonalne do przekroju); zmienić w parametrach obliczeń i przeliczyć")
            self.otwarte.append(opis + ".")
        t_en = str(self.uzbrojenie("en").get("opis") or "")
        for m in sorted(set(re.findall(r"YKY \d×\d+", t_en))):
            if m != self.obw.wlz["przewod"]:
                self.otwarte.append(f"Opis trasy WLZ w modelu działki (uzbrojenie projektowane „en”) podaje {m}, obliczenia "
                                    f"— {self.obw.wlz['przewod']}; w tomie obowiązuje przekrój z obliczeń — poprawić opis "
                                    "w modelu i ponownie wygenerować rysunki PZT (tom I).")
        if not (self.I.get("wyroby") or {}):
            self.otwarte.append("`instalacje.wyroby` w modelu puste — moduł PV, falownik, pompa ciepła i aparatura przyjęte "
                                "z danych przykładowych bibliotek [DANE PRZYKŁADOWE – FIKCYJNE]; zastąpić danymi DTR/DWU wyrobów "
                                "wybranych przez wykonawcę (wyroby równoważne spełniające parametry wymagane — rozdz. „Wyroby”).")
        if not self.B.get("projekt"):
            self.otwarte.append("Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji "
                                "`projekt:` w model/budynek.yaml; pola oznaczone jako do uzupełnienia (strona tytułowa, oświadczenie).")
        self.otwarte.append("Warunki przyłączenia OSD (E-05) — nieuzyskane; moc przyłączeniowa, typ zabezpieczenia "
                            "przedlicznikowego, impedancja pętli zwarcia Z_Q i prąd zwarciowy w ZKP, rozdział PEN "
                            "przyjęte jako [ZAŁ]; po otrzymaniu warunków przeliczyć obwody (D-12, W-192, E-05).")
        self.otwarte += self.ark_braki

    # ------------------------------------------------------------------ BRAKI_DANYCH.md (tabela)
    def braki_tabela(self) -> list[dict]:
        wiersze = []
        for ln in self.braki_md.splitlines():
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 5 and c[0].isdigit():
                wiersze.append({"Lp.": int(c[0]), "Element": c[1].replace("`", ""),
                                "Brak / stan w modelu": c[2].replace("`", ""), "Arkusze": c[-1]})
        return wiersze


def sqrt3() -> float:
    return math.sqrt(3.0)
