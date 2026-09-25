"""Generator tomu PT-1 AR — projekt techniczny, architektura („Dom LAMELA”).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_PT_AR.py [--wyjscie projekt/wydanie] [--bez-arkuszy]

Wynik:
* ``projekt/wydanie/PT_1_AR_rrrr.mm.dd.pdf`` — tom PT-1 AR (osobny plik, RPB § 5 ust. 3; nazwa wg zał. 1 RPB):
  strona tytułowa (§ 7 ust. 2, „Tom 1 z 4” — § 7 ust. 6), spis treści, oświadczenie projektanta PT
  (PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2), część opisowa (§ 23 pkt 4, 4a, 10 RPB),
  obliczenia (U — PN-EN ISO 6946, ψ/f_Rsi — PN-EN ISO 10211 i 13788, kondensacja — PN-EN ISO 13788, g — WT zał. 2),
  zestawienia (przegrody, stolarka — W-317, wykończenia), zasada „4 linii” i odwodnienie, część rysunkowa
  (§ 24 pkt 1–2: rzuty, przekroje, elewacje AR + detale PT-AR-D);
* ``projekt/09_opis_i_zalaczniki/PT_AR/`` — źródło Markdown części opisowej i raport walidatora (txt/json).

ŹRÓDŁA LICZB (odczyt przy każdym uruchomieniu — brak wartości wpisanych na sztywno):
``model/budynek.yaml`` + ``model/dzialka.yaml`` (lamela.model), ``lamela.obliczenia.fizyka_energia.oblicz_wszystko``
(U, grunt, okna, g, f_Rsi, Glaser, H_TB), ``projekt/08_obliczenia/mostki/zestawienie_mostkow.json`` (karty mostków
PN-EN ISO 10211: ψ, f_Rsi, „4 linie”), ``docs/10_podstawy_prawne/wymagania.yaml`` (wymagania z podstawą),
``lamela.wskazniki`` (kondygnacje, wysokość wg WT § 6), ``raport_widokow.json`` katalogów rysunków,
``projekt/10_PT_architektura/detale/raport_detali.md`` (przypisanie detali do węzłów).
Dane osobowe, uprawnienia, podpisy — ``[DO UZUPEŁNIENIA]``; działka/MPZP/grunt — ``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import time
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from lamela.dokumenty import (Arkusz, Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              liczba, do_uzup, DANE_PRZYKLADOWE, ZAL, NZW, zamknij_przegladarke)
from lamela.obliczenia.wspolne import wymaganie, orientacja  # noqa: E402

KAT_MOSTKI = REPO / "projekt/08_obliczenia/mostki"
KAT_DETALE = REPO / "projekt/10_PT_architektura/detale"
KAT_AR = [REPO / "projekt/03_PAB/rysunki", REPO / "projekt/01_koncepcja/widoki"]   # pierwszy istniejący
KAT_ZRODLA = REPO / "projekt/09_opis_i_zalaczniki/PT_AR"
KAT_WYDANIE = REPO / "projekt/wydanie"
PT_TOMY = 4                                  # PT-1 AR, PT-2 BO, PT-3 IS, PT-4 IE (rejestr C.2)
ROLE_WEWN = ("sciana_wewn", "strop_wewn")


# ============================================================================================ pomocnicze
def L(v, n=2, pusty="—"):
    """Liczba w zapisie polskim albo „—”."""
    return pusty if v is None else liczba(v, n)


def nr_iso(pid: str, kond: str) -> str:
    """Identyfikator modelu „0.01” → numer na arkuszach wg PN-B-01025 (parter = 1): „1.01” (W-314)."""
    try:
        return f"{int(kond[1:]) + 1}.{pid.split('.')[1]}"
    except Exception:
        return pid


def wym(sekcja: str, klucz: str):
    """Wymaganie z docs/10_podstawy_prawne/wymagania.yaml → (wartość, 'źródło; W-xxx')."""
    w = wymaganie(sekcja, klucz)
    return w.wartosc, f"{w.zrodlo}; {w.id}" if w.id else w.zrodlo


def _md_komorka(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, float):
        return liczba(v, 3)
    return re.sub(r"<[^>]+>", "", str(v)).replace("|", "/").replace("\n", " ")


class Opis:
    """Zapis równoległy: bloki ``Dokument`` (PDF) i źródło Markdown (``projekt/09_opis_i_zalaczniki/PT_AR``)."""

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

    def tabela(self, wiersze: list, *, tytul: str, uwagi=None, zrodlo: str | None = None, **kw):
        self.dok.tabela(wiersze, tytul=tytul, uwagi=uwagi, zrodlo=zrodlo, **kw)
        self.n_tab += 1
        kol = [k for k in (next((w for w in wiersze if isinstance(w, dict)), {}) or {}) if not k.startswith("_")]
        out = [f"**Tabela {self.n_tab}. {tytul}**", "", "| " + " | ".join(kol) + " |",
               "|" + "---|" * len(kol)]
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

    def zapisz(self, plik: Path):
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text("\n\n".join(self.md) + "\n", encoding="utf-8")
