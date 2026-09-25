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
RE_POM = re.compile(r"(?<![\w.,/=`-])(\d\.\d\d[a-z]?)(?![\d,.]\d|\w)")
ZNACZNIK_NIEAKTUALNE = "ARKUSZE NIEAKTUALNE"      # walidator (C2-IS-07): BRAK, gdy znacznik jest w tomie


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
        from lamela.obliczenia import fizyka_energia as FE
        from lamela.obliczenia.fizyka import mostki as MB
        sym = MB.wczytaj_wyniki_symulacji(P_MOSTKI) if P_MOSTKI.exists() else None
        self.ep_uwagi = FE.przelicz_ep_wyroby(self.R, self.W, self.m, sym)   # EP dla PC i zasobnika z projektu
        log(f"  obliczenia: {time.time() - t0:.0f} s; EP na wyrobach zaprojektowanych: {self.R['ep'].EP:.1f}")
        self.Wd = {k: self.W[k].do_dict() for k in MODULY + ("bilans",)}
        from lamela.views.common import room_label           # numer arkusza (K+1).NN — jak PT-1 AR i rysunki (W-314)
        self.nr_pom = {p.id: room_label(self.m, p.id, "iso") for p in self.m.pomieszczenia()}
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
        self._aktualnosc_rysunkow(p)

    def _aktualnosc_rysunkow(self, p_rap: Path):
        """Arkusze nieaktualne wobec modelu i bieżących obliczeń → ``ark_nieaktualne`` [(nr, powód)]: czas generowania
        starszy niż model, inny model PC, „SPRAWDZENIE NIESPEŁNIONE” przy braku warunków niespełnionych, wyniki
        retencji/odwodnienia dachów na arkuszu różne od obliczeń. Lista niepusta → znacznik w tomie (walidator: BRAK)."""
        import pymupdf
        self.ark_nieaktualne: list[tuple[str, str]] = []
        zrodla = [self.p_bud, self.p_dz, self.p_inst, self.p_wyp, REPO / "model/arkusze_is.yaml"]
        t_mod = max(x.stat().st_mtime for x in zrodla if x.exists())
        if p_rap.exists() and p_rap.stat().st_mtime < t_mod:
            self.ark_nieaktualne.append(("wszystkie", "wygenerowane przed ostatnią zmianą modelu"))
        pc = (self.W["ogrzewanie"].pc or {}).get("model", "")
        pc_id = (re.search(r"PC-R290-\d+", pc) or [None])[0] if pc else None
        n_nok = sum(1 for k in MODULY for x in self.warunki(k) if x.ok is False)
        Dd = self.W["deszczowa"].do_dict()
        oczek = {"niecka": f"niecka {L(Dd['niecka_A_m2'], 1)} m²", "Q = ": f"Q = {L(Dd['Q_dachy_l_s'], 2)} l/s"}
        for a in self.arkusze:
            if not a.istnieje:
                continue
            with pymupdf.open(a.plik) as doc:
                tx = re.sub(r"\s+", " ", " ".join(pg.get_text() for pg in doc))
            for m in sorted(set(re.findall(r"PC-R290-\d+", tx))):
                if pc_id and m != pc_id:
                    self.ark_nieaktualne.append((a.nr, f"pompa ciepła {m}, a w obliczeniach {pc}"))
            if "NIESPEŁNIONE" in tx.upper() and n_nok == 0:
                self.ark_nieaktualne.append((a.nr, "uwaga „SPRAWDZENIE NIESPEŁNIONE” z poprzedniej wersji obliczeń"))
            if "ODWODNIENIE DACH" in (a.tytul or "").upper():
                for klucz, wz in oczek.items():
                    if re.search(re.escape(klucz.strip()) + r"\s", tx) and wz not in tx:
                        self.ark_nieaktualne.append((a.nr, f"wynik inny niż w obliczeniach (oczekiwano „{wz}”)"))
        for nr, powod in self.ark_nieaktualne:
            self.otwarte.append(f"{ZNACZNIK_NIEAKTUALNE}: {nr} — {powod}; wygenerować ponownie "
                                "(tools/generuj_widoki.py --arkusze model/arkusze_is.yaml).")

    def nr(self, pid: str) -> str:
        """Identyfikator pomieszczenia modelu (parter 0.NN) → numer z arkuszy i PT-1 AR (parter 1.NN)."""
        return self.nr_pom.get(str(pid), str(pid))

    def renum(self, tekst):
        """Zamiana identyfikatorów pomieszczeń modelu w tekście na numery z arkuszy (W-314); identyfikatory
        elementów (np. SG-0.03), liczby dziesiętne i ułamki pozostają bez zmian."""
        if not isinstance(tekst, str) or not self.nr_pom:
            return tekst
        return RE_POM.sub(lambda m: self.nr_pom.get(m.group(1), m.group(1)), tekst)

    @property
    def wodomierz(self) -> str:
        w = self.W["woda"].wodomierz or {}
        return f"DN{w.get('DN')}, Q3 = {L(w.get('Q3'), 1)} m³/h" if w else str(self.Wd["woda"].get("wodomierz"))

    def arkusze_nr(self, *slowa) -> str:
        """Numery arkuszy, których tytuł zawiera wszystkie ``slowa`` (bez rozróżniania wielkości liter)."""
        nr = [a.nr for a in self.arkusze if all(s.lower() in (a.tytul or "").lower() for s in slowa)]
        return ", ".join(nr) if nr else "—"

    # ------------------------------------------------------------------ kontrole spójności → „otwarte”
    def warunki(self, modul: str) -> list:
        return list(getattr(self.W[modul], "warunki", []) or [])

    def niespelnione(self) -> list[tuple[str, object]]:
        out = [(k, x) for k in MODULY for x in self.warunki(k) if x.ok is False]
        out += [("wentylacja", s) for s in self.went.sprawdzenia if s[2] is False]
        return out

    def _kontrole(self):
        for mod, x in self.niespelnione():
            opis = x.opis if hasattr(x, "opis") else x[0]
            self.otwarte.append(f"Obliczenia ({mod}) — warunek niespełniony: {opis}.")
        pc_e = (self.obc.dobor or {}).get("pc") or {}
        pc_o = self.og.pc or {}
        P7_o = dict(zip(pc_o.get("T", []), pc_o.get("P", []))).get(-7)
        if pc_e and pc_o and (abs((pc_e.get("SCOP_35") or 0) - (pc_o.get("SCOP_35") or 0)) > 0.05
                              or (P7_o is not None and abs((pc_e.get("P_Am7W35_kW") or 0) - P7_o) > 0.05)):
            self.otwarte.append(
                f"Pompa ciepła — dwa różne zestawy danych przykładowych: moduł energii (dobór, EP) P(A−7/W35) = "
                f"{L(pc_e.get('P_Am7W35_kW'), 1)} kW, SCOP₃₅ = {L(pc_e.get('SCOP_35'), 2)}; moduł ogrzewania "
                f"({pc_o.get('model')}) P(A−7/W35) = {L(P7_o, 1)} kW, SCOP₃₅ = {L(pc_o.get('SCOP_35'), 2)}, "
                f"L_WA = {L(pc_o.get('L_WA'), 0)} dB — ujednolicić w `instalacje.wyroby.PC` (DTR/DWU wybranego wyrobu) "
                "i przeliczyć EP, punkt biwalentny i hałas.")
        if not (self.I.get("wyroby") or {}):
            self.otwarte.append("`instalacje.wyroby` w modelu puste — obliczenia na danych przykładowych bibliotek "
                                "(PC, centrala wentylacyjna, wodomierz Δp(Q3), zawór EA k_v, wpusty) [DANE PRZYKŁADOWE – "
                                "FIKCYJNE]; zastąpić danymi DTR/DWU wyrobów wybranych przez wykonawcę (wyroby równoważne).")
        zas_m = [x for x in self.Wy if x.get("typ") == "zasobnik" and "bufor" not in str(x.get("opis", "")).lower()]
        V_obl = self.Wd["woda"].get("zasobnik_l")
        V_mod = next((x.get("V_dm3") or x.get("V") for x in zas_m if (x.get("V_dm3") or x.get("V"))), None)
        if V_mod is None:
            m = next((re.search(r"(\d{3})\s*(?:dm³|l\b|dm3)", str(x.get("opis", ""))) for x in zas_m), None)
            V_mod = int(m.group(1)) if m else None
        if V_mod and V_obl and abs(float(V_mod) - float(V_obl)) > 1:
            self.otwarte.append(f"Zasobnik c.w.u.: w modelu (wyposazenie.yaml) {L(V_mod, 0)} dm³, z obliczeń "
                                f"{L(V_obl, 0)} dm³ — ujednolicić w modelu (na rysunkach przyjęto wartość z obliczeń).")
        buf_m = [x for x in self.Wy if "bufor" in str(x.get("opis", "")).lower()]
        buf_o = self.Wd["ogrzewanie"].get("bufor_l")
        if buf_m and buf_o:
            m = re.search(r"(\d{2,4})\s*(?:dm³|l\b|dm3)", str(buf_m[0].get("opis", "")))
            if m and int(m.group(1)) < buf_o - 1:
                self.otwarte.append(f"Bufor c.o.: w modelu „{buf_m[0].get('opis')}” < wymagane z obliczeń {buf_o} dm³ — "
                                    "zwiększyć w modelu.")
        rozb = [p for p in self.went.pomieszczenia
                if (p.naw_model or p.wyw_model) and (abs(p.naw_model - p.naw) > 1 or abs(p.wyw_model - p.wyw) > 1)]
        if rozb:
            self.otwarte.append(
                f"Strumienie powietrza w modelu (`pomieszczenia[].went`) różnią się od bilansu wentylacji w "
                f"{len(rozb)} pomieszczeniach ({', '.join(p.id for p in rozb[:8])}{'…' if len(rozb) > 8 else ''}) — "
                "przyjęto wartości z bilansu (PN-83/B-03430/Az3); zaktualizować model.")
        if not self.B.get("projekt"):
            self.otwarte.append("Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji "
                                "`projekt:` w model/budynek.yaml; pola oznaczone jako do uzupełnienia (strona tytułowa, oświadczenie).")
        self.otwarte += self.ark_braki

    # ------------------------------------------------------------------ BRAKI_DANYCH.md (tabela)
    def braki_tabela(self) -> list[dict]:
        wiersze = []
        for ln in self.braki_md.splitlines():
            c = [x.strip() for x in ln.strip().strip("|").split("|")]
            if len(c) >= 5 and c[0].isdigit():
                wiersze.append({"Lp.": int(c[0]), "Element": c[1].replace("`", ""),
                                "Brak / stan w modelu": c[2].replace("`", ""), "Arkusze": _zakresy(c[-1])})
        return wiersze


def _zakresy(tekst: str) -> str:
    """„PT-IS-01, PT-IS-02, PT-IS-03, PT-IS-05” → „PT-IS-01…03, 05”."""
    m = re.findall(r"([A-Z]+-[A-Z]+-)(\d+)", tekst)
    if len(m) < 3 or len({p for p, _ in m}) != 1:
        return tekst
    pre, nr = m[0][0], sorted(int(n) for _, n in m)
    grupy, start, prev = [], nr[0], nr[0]
    for n in nr[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        grupy.append(f"{start:02d}…{prev:02d}" if prev - start >= 2 else
                     ", ".join(f"{k:02d}" for k in range(start, prev + 1)))
        if n is not None:
            start = prev = n
    return pre + ", ".join(grupy)


class Opis:
    """Zapis równoległy: bloki ``Dokument`` (PDF) i źródło Markdown (``projekt/09_opis_i_zalaczniki/PT_IS``)."""

    def __init__(self, dok, renum=None):
        self.dok = dok
        self.md: list[str] = []
        self.n_tab = 0
        self.renum = renum or (lambda t: t)     # numeracja pomieszczeń z arkuszy (DanePTIS.renum)

    def _r(self, v):
        if isinstance(v, str):
            return self.renum(v)
        if isinstance(v, dict):
            return {k: self._r(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return type(v)(self._r(x) for x in v)
        return v

    def czesc(self, tytul: str, podstawa: str | None = None):
        self.dok.czesc_opisowa(tytul, podstawa=podstawa)
        self.md.append(f"# {tytul}" + (f" ({podstawa})" if podstawa else ""))

    def rozdzial(self, tytul, tresc=None, *, poziom=1, podstawa=None, nowa_strona=False):
        tresc = self.renum(textwrap.dedent(tresc).strip()) if tresc else None
        tytul = self.renum(tytul)
        self.dok.rozdzial(tytul, tresc, poziom=poziom, podstawa=podstawa, nowa_strona=nowa_strona)
        self.md.append(f"{'#' * (poziom + 1)} {tytul}" + (f" — {podstawa}" if podstawa else ""))
        if tresc:
            self.md.append(tresc)

    def tekst(self, tresc: str):
        tresc = self.renum(textwrap.dedent(tresc).strip())
        self.dok.markdown(tresc)
        self.md.append(tresc)

    def wniosek(self, tresc: str, alarm: bool = False):
        t = self.renum(textwrap.dedent(tresc).strip())
        self.dok.wniosek(t, alarm=alarm)
        self.md.append("> " + t.replace("\n", "\n> "))

    def obraz(self, plik: Path, podpis: str, szerokosc: str | None = None):
        self.dok.obraz(plik, podpis=podpis, szerokosc=szerokosc)
        self.md.append(f"![{podpis}]({rel(plik)})")

    def tabela(self, wiersze: list, *, tytul: str, uwagi=None, zrodlo: str | None = None, **kw):
        wiersze, uwagi, tytul = self._r(list(wiersze)), self._r(uwagi), self.renum(tytul)
        self.dok.tabela(wiersze, tytul=tytul, uwagi=uwagi, zrodlo=zrodlo, **kw)
        self.n_tab += 1
        kol = [k for k in (next((w for w in wiersze if isinstance(w, dict)), {}) or {}) if not k.startswith("_")]
        out = [f"**Tabela {self.n_tab}. {tytul}**", "", "| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
        for w in wiersze:
            if isinstance(w, str):
                out.append(f"| **{w}** |" + " |" * (len(kol) - 1))
            else:
                out.append("| " + " | ".join(_komorka(w.get(k)) for k in kol) + " |")
        for u in ([uwagi] if isinstance(uwagi, str) else (uwagi or [])):
            out.append(f"\n{_komorka(u)}")
        if zrodlo:
            out.append(f"\n*Źródło: {zrodlo}*")
        self.md.append("\n".join(out))

    def zapisz(self, plik: Path):
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text("\n\n".join(self.md) + "\n", encoding="utf-8")


def _komorka(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, float):
        return liczba(v, 2)
    return re.sub(r"<[^>]+>", "", str(v)).replace("|", "/").replace("\n", " ")
