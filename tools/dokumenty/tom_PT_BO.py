"""Generator tomu PT-2 BO — projekt techniczny, konstrukcja („Dom LAMELA”).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_PT_BO.py [--wyjscie projekt/wydanie] [--przelicz] [--bez-arkuszy]

Wynik:
* ``projekt/wydanie/PT_2_BO_rrrr.mm.dd.pdf`` — tom PT-2 BO (osobny plik, RPB § 5 ust. 3; nazwa wg zał. 1 RPB):
  strona tytułowa (§ 7 ust. 2, „Tom 2 z 4” — § 7 ust. 6), spis treści, oświadczenie projektanta PT
  (PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2), część opisowa (§ 23 pkt 1, 2, 3, 10 RPB):
  stan analiz (pozycje NIEZAMKNIĘTE), opis konstrukcji, schematy statyczne, obciążenia (PN-EN 1991 + NA),
  materiały, klasy ekspozycji, otulenia, podstawowe wyniki, pełne obliczenia statyczne, MES płyty fundamentowej,
  kontrola zbrojenia rysunków, projekt geotechniczny (kat. II), dane ppoż., część rysunkowa (§ 24 pkt 1);
* ``projekt/09_opis_i_zalaczniki/PT_BO/`` — źródło Markdown części opisowej, raport walidatora (txt/json),
  zestawienie stanu analiz (``stan_analiz.json``).

ŹRÓDŁA (odczyt przy każdym uruchomieniu — brak liczb wpisanych na sztywno):
``model/budynek.yaml`` (konstrukcja, geotechnika, fundamenty, elementy), ``lamela.obliczenia.konstrukcja``
(``Parametry.z_wymagan``, ``NORMY``, ``METODY``, ``OGRANICZENIA``), wyniki zespołu BO:
``projekt/04_PT_konstrukcja/obliczenia/{obliczenia_statyczne.md, wyniki.json, plyta_fundamentowa_MES.md, rys/}``,
``projekt/04_PT_konstrukcja/rysunki/{kontrola_zbrojenia.json, kontrola_zbrojenia.md, raport_widokow.json}``,
``projekt/04_PT_konstrukcja/BRAKI_DANYCH.md``. Z ``--przelicz`` obliczenia statyczne są uruchamiane ponownie
(``AnalizaKonstrukcji`` → ``projekt/09_opis_i_zalaczniki/PT_BO/obliczenia/``) — kilka minut.

Analizy niedomknięte (warunki niespełnione, brak kontroli rysunków, uwagi [WYMAGA ANALIZY], brak arkusza) są
wykazywane jawnie jako NIEZAMKNIĘTE (rozdział 1 i podtytuł strony tytułowej); po domknięciu przez zespół BO
i ponownym uruchomieniu generatora status aktualizuje się automatycznie.
Dane osobowe, uprawnienia, podpisy — ``[DO UZUPEŁNIENIA]``; działka/MPZP/grunt — ``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import textwrap
import time
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from lamela.dokumenty import (Arkusz, Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              liczba, do_uzup, DANE_PRZYKLADOWE, zamknij_przegladarke)

KAT_BO = REPO / "projekt/04_PT_konstrukcja"
KAT_OBL = KAT_BO / "obliczenia"
KAT_RYS = KAT_BO / "rysunki"
KAT_ZRODLA = REPO / "projekt/09_opis_i_zalaczniki/PT_BO"
KAT_WYDANIE = REPO / "projekt/wydanie"
PT_TOMY = 4                                  # PT-1 AR, PT-2 BO, PT-3 IS, PT-4 IE (rejestr C.2)
PT_NR = 2
NZ = "NIEZAMKNIĘTE"
FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


# ============================================================================================ pomocnicze
def L(v, n=2, pusty="—"):
    """Liczba w zapisie polskim albo „—”."""
    return pusty if v is None else liczba(v, n)


def pct(eta) -> str:
    return "—" if eta is None else f"{liczba(100 * eta, 0)} %"


def _md_komorka(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, float):
        return liczba(v, 3)
    return re.sub(r"<[^>]+>", "", str(v)).replace("|", "/").replace("\n", " ")


def rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return str(p)


RE_IMG = re.compile(r"^!\[(?P<cap>[^\]]*)\]\((?P<src>[^)]+)\)\s*$", re.M)


class Opis:
    """Zapis równoległy: bloki ``Dokument`` (PDF) i źródło Markdown (``projekt/09_opis_i_zalaczniki/PT_BO``)."""

    def __init__(self, dok: Dokument):
        self.dok = dok
        self.md: list[str] = []
        self.n_tab = 0

    def czesc(self, tytul: str, podstawa: str | None = None):
        self.dok.czesc_opisowa(tytul, podstawa=podstawa)
        self.md.append(f"# {tytul}" + (f" ({podstawa})" if podstawa else ""))

    def rozdzial(self, tytul: str, tresc: str | None = None, *, poziom: int = 1, podstawa: str | None = None,
                 nowa_strona: bool = False):
        tresc = textwrap.dedent(tresc).strip() if tresc else None
        self.dok.rozdzial(tytul, tresc, poziom=poziom, podstawa=podstawa, nowa_strona=nowa_strona)
        self.md.append(f"{'#' * (poziom + 1)} {tytul}" + (f" — {podstawa}" if podstawa else ""))
        if tresc:
            self.md.append(tresc)

    def tekst(self, tresc: str):
        tresc = textwrap.dedent(tresc).strip()
        self.dok.markdown(tresc)
        self.md.append(tresc)

    def wniosek(self, tresc: str, alarm: bool = False):
        self.dok.wniosek(textwrap.dedent(tresc).strip(), alarm=alarm)
        self.md.append("> " + textwrap.dedent(tresc).strip().replace("\n", "\n> "))

    def obraz(self, plik: Path, podpis: str, szerokosc: str | None = None):
        self.dok.obraz(plik, podpis=podpis, szerokosc=szerokosc)
        self.md.append(f"![{podpis}]({rel(plik)})")

    def wykres(self, fig, podpis: str, szerokosc: str = "100%"):
        self.dok.wykres(fig, podpis=podpis, szerokosc=szerokosc)
        self.md.append(f"*[Wykres: {podpis} — w PDF]*")

    def tabela(self, wiersze: list, *, tytul: str, uwagi=None, zrodlo: str | None = None, **kw):
        self.dok.tabela(wiersze, tytul=tytul, uwagi=uwagi, zrodlo=zrodlo, **kw)
        self.n_tab += 1
        kol = [k for k in (next((w for w in wiersze if isinstance(w, dict)), {}) or {}) if not k.startswith("_")]
        out = [f"**Tabela {self.n_tab}. {tytul}**", "", "| " + " | ".join(kol) + " |", "|" + "---|" * len(kol)]
        for w in wiersze:
            if isinstance(w, str):
                out.append(f"| **{w}** |" + " |" * (len(kol) - 1))
            else:
                out.append("| " + " | ".join(_md_komorka(w.get(k)) for k in kol) + " |")
        for u in ([uwagi] if isinstance(uwagi, str) else (uwagi or [])):
            out.append(f"\n{_md_komorka(u)}")
        if zrodlo:
            out.append(f"\n*Źródło: {zrodlo}*")
        self.md.append("\n".join(out))

    def dokument_md(self, tekst: str, katalog: Path, *, przesuniecie: int = 0, md_odeslanie: str | None = None):
        """Wstawia gotowy dokument Markdown (np. obliczenia statyczne biblioteki): nagłówki → rozdziały numerowane,
        obrazy ``![podpis](rys/…)`` → ilustracje numerowane (plik względem ``katalog``); wiersz „*Rys. …*” pomijany.
        Do źródła MD trafia tylko odesłanie (pełny tekst jest w pliku źródłowym zespołu BO)."""
        tekst = re.sub(r"^\*Rys\. [^\n]*\*\s*$", "", tekst, flags=re.M)
        poz = 0
        for m in RE_IMG.finditer(tekst):
            seg = tekst[poz:m.start()]
            if seg.strip():
                self.dok.markdown(seg, przesuniecie=przesuniecie)
            plik = (katalog / m.group("src")).resolve()
            if plik.exists():
                self.dok.obraz(plik, podpis=m.group("cap"), szerokosc="100%")
            else:
                self.dok.wniosek(f"Brak pliku ilustracji `{m.group('src')}` — {NZ} (rysunek do wygenerowania).",
                                 alarm=True)
            poz = m.end()
        if tekst[poz:].strip():
            self.dok.markdown(tekst[poz:], przesuniecie=przesuniecie)
        self.md.append(md_odeslanie or "*[Pełna treść dokumentu — w PDF]*")

    def zapisz(self, plik: Path):
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text("\n\n".join(self.md) + "\n", encoding="utf-8")


# ============================================================================================ dane wejściowe
def _czytaj(p: Path, domyslnie=None):
    if not p.exists():
        return domyslnie
    return json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else p.read_text(encoding="utf-8")


def przelicz_obliczenia(out: Path) -> Path:
    """Ponowne obliczenia statyczne z modelu (jak ``python3 -m lamela.obliczenia.konstrukcja``) do ``out``."""
    from lamela.model import load_model
    from lamela.obliczenia.konstrukcja.pozycje import AnalizaKonstrukcji
    from lamela.obliczenia.konstrukcja.raport import generuj_raport
    from lamela.obliczenia.konstrukcja.wspolne import Parametry
    m = load_model(REPO / "model/budynek.yaml", REPO / "model/dzialka.yaml", strict=False)
    an = AnalizaKonstrukcji(m, Parametry.z_wymagan(), rys_dir=out / "rys").uruchom()
    generuj_raport(an, out, html=False)
    return out


def wczytaj_dane(przelicz: bool = False) -> dict:
    """Model (surowy YAML), parametry obliczeń, wyniki zespołu BO (obliczenia, MES, kontrola, braki, rysunki)."""
    from lamela.obliczenia.konstrukcja.wspolne import Parametry
    from lamela.obliczenia.konstrukcja import raport as RAP
    kat_obl = przelicz_obliczenia(KAT_ZRODLA / "obliczenia") if przelicz else KAT_OBL
    bud = yaml.safe_load((REPO / "model/budynek.yaml").read_text(encoding="utf-8"))
    dz = yaml.safe_load((REPO / "model/dzialka.yaml").read_text(encoding="utf-8"))
    D = dict(bud=bud, dz=dz, p=Parametry.z_wymagan(), RAP=RAP, kat_obl=kat_obl,
             obl_md=_czytaj(kat_obl / "obliczenia_statyczne.md"), wyniki=_czytaj(kat_obl / "wyniki.json"),
             mes_md=_czytaj(KAT_OBL / "plyta_fundamentowa_MES.md"),
             kz=_czytaj(KAT_RYS / "kontrola_zbrojenia.json"), kz_md=_czytaj(KAT_RYS / "kontrola_zbrojenia.md"),
             braki_md=_czytaj(KAT_BO / "BRAKI_DANYCH.md", ""), rap_rys=_czytaj(KAT_RYS / "raport_widokow.json"),
             cfg_rys=yaml.safe_load((REPO / "model/arkusze_bo.yaml").read_text(encoding="utf-8")))
    # aktualność wyników względem modelu (czas modyfikacji plików)
    t_mod = max((REPO / f"model/{f}").stat().st_mtime for f in ("budynek.yaml", "dzialka.yaml"))
    D["aktualnosc"] = {}
    for nazwa, p in (("obliczenia statyczne", kat_obl / "wyniki.json"), ("MES płyty fundamentowej",
                     KAT_OBL / "plyta_fundamentowa_MES.md"), ("kontrola zbrojenia", KAT_RYS / "kontrola_zbrojenia.json")):
        D["aktualnosc"][nazwa] = (p.exists() and p.stat().st_mtime >= t_mod - 1,
                                  dt.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                                  if p.exists() else "brak pliku")
    D["t_modelu"] = dt.datetime.fromtimestamp(t_mod).strftime("%Y-%m-%d %H:%M")
    return D


def tabele_md(tekst: str) -> list[list[dict]]:
    """Tabele Markdown z tekstu → listy słowników (nagłówek = klucze)."""
    out, cur, kol = [], None, None
    for ln in (tekst or "").splitlines():
        if ln.startswith("|"):
            kom = [c.strip() for c in ln.strip().strip("|").split("|")]
            if kol is None:
                kol, cur = kom, []
            elif set("".join(kom)) <= set("-: "):
                continue
            else:
                cur.append(dict(zip(kol, kom)))
        elif kol is not None:
            out.append(cur)
            kol = cur = None
    if kol is not None:
        out.append(cur)
    return out


def wartosc_md(tekst: str, etykieta: str):
    """Wartość pogrubiona z listy „- Etykieta…: … = **wartość**” (dokumenty obliczeń) — pierwsze wystąpienie."""
    m = re.search(rf"^- {re.escape(etykieta)}[^\n]*?\*\*([^*]+)\*\*", tekst or "", flags=re.M)
    return m.group(1).strip() if m else None


def sekcja_md(tekst: str, naglowek: str) -> str:
    """Treść listy punktowanej sekcji „## …” (bez podsekcji) — np. BRAKI_DANYCH.md."""
    m = re.search(rf"^## {re.escape(naglowek)}[^\n]*\n(.*?)(?=^## |\Z)", tekst or "", flags=re.M | re.S)
    return m.group(1).strip() if m else ""
