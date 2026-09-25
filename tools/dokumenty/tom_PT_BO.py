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

from lamela.dokumenty.formaty import odmiana  # noqa: E402

from lamela.dokumenty import (Arkusz, Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              liczba, do_uzup, dok_zewn, DANE_PRZYKLADOWE, zamknij_przegladarke)

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


# Opis źródeł zrozumiały dla czytelnika PT (kierownik budowy, organ) — bez ścieżek plików i identyfikatorów kodu
# (weryfikacja PT, D-2). Stosowane do całej treści części opisowej, także do dokumentów zespołu BO wstawianych w tom.
ZRODLA_OPIS = [
    (r"Plik generowany (?:automatycznie )?przez `lamela\.views\.[\w.]+`(?: \([^)]*\))?\s*(?:przy rysowaniu arkuszy)?\.?",
     "Opracowanie generowane automatycznie z modelu budynku."),
    (r"Lista generowana automatycznie przez `lamela\.views\.[\w.]+`", "Lista generowana automatycznie"),
    (r"\s*\(test `tools/[^`]+`\)", " (test kontrolny programu obliczeń)"),
    (r"\(moduł `konstrukcja_dane\.rejestruj`\)\s*", ""),
    (r"`AnalizaKonstrukcji\.brak_danych`", "braki zgłoszone przez program obliczeń"),
    (r"`?lamela\.views\.[\w.]+`?", "program rysunkowy projektu"),
    (r"(?:biblioteki |biblioteka |moduł obliczeń |moduł )?`?lamela\.obliczenia\.[\w.]+`?(?: 1\.0)?", "program obliczeń konstrukcji"),
    (r"`?tools/[\w/]+\.py`?", "program generujący model"),
    (r"`?(?:projekt/04_PT_konstrukcja/)?REKOMENDACJE_MODEL\.md`?", "zalecenia zmian modelu zespołu konstrukcji"),
    (r"`?(?:projekt/04_PT_konstrukcja/)?BRAKI_DANYCH\.md`?", "wykaz braków danych zespołu konstrukcji"),
    (r"`?(?:[\w/]+/)?wyniki\.json`?(?: — uwagi)?", "wyniki obliczeń statycznych"),
    (r"`?(?:[\w/]+/)?obliczenia_statyczne\.md`?", "obliczenia statyczne (rozdz. 4)"),
    (r"`?(?:[\w/]+/)?plyta_fundamentowa_MES\.md`?", "raport MES płyty fundamentowej (rozdz. 5)"),
    (r"`?(?:[\w/]+/)?kontrola_zbrojenia\.(?:json|md)`?", "kontrola zbrojenia rysunków (rozdz. 6)"),
    (r"`?(?:[\w/]+/)?raport_widokow\.json`?", "raport kontroli arkuszy"),
    (r"`?(?:/[\w/]+/)?(?:model/)?budynek\.yaml`?", "model budynku"),
    (r"`?(?:model/)?dzialka\.yaml`?", "model działki"),
    (r"`?(?:model/)?instalacje\.yaml`?", "model instalacji"),
    (r"`?(?:model/)?arkusze_bo\.yaml`?", "konfiguracja arkuszy konstrukcji"),
    (r"`?Parametry\.z_wymagan`?(?: \(wymagania\.yaml ([^)]*)\))?", lambda m: "parametry obliczeń z rejestru wymagań" + (f" ({m.group(1)})" if m.group(1) else "")),
    (r"`?(?:model/)?wymagania\.yaml`?", "rejestr wymagań"),
    (r"\(konstrukcja\.obciazenia\)", "(obciążenia)"),
    (r"energia\.pv(?:\.pola)?", "model — instalacja PV"),
]
_RE_ZRODLA = [(re.compile(a), b) for a, b in ZRODLA_OPIS]            # b: tekst albo funkcja(m)


def jawne(t):
    """Zastępuje ścieżki i identyfikatory kodu opisem źródła (tekst trafiający do PDF i źródła MD)."""
    if not isinstance(t, str):
        return t
    for rx, zam in _RE_ZRODLA:
        t = rx.sub(zam, t)
    return t


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
        tresc = jawne(textwrap.dedent(tresc).strip()) if tresc else None
        self.dok.rozdzial(tytul, tresc, poziom=poziom, podstawa=podstawa, nowa_strona=nowa_strona)
        self.md.append(f"{'#' * (poziom + 1)} {tytul}" + (f" — {podstawa}" if podstawa else ""))
        if tresc:
            self.md.append(tresc)

    def tekst(self, tresc: str):
        tresc = jawne(textwrap.dedent(tresc).strip())
        self.dok.markdown(tresc)
        self.md.append(tresc)

    def wniosek(self, tresc: str, alarm: bool = False):
        tresc = jawne(textwrap.dedent(tresc).strip())
        self.dok.wniosek(tresc, alarm=alarm)
        self.md.append("> " + tresc.replace("\n", "\n> "))

    def obraz(self, plik: Path, podpis: str, szerokosc: str | None = None):
        self.dok.obraz(plik, podpis=podpis, szerokosc=szerokosc)
        self.md.append(f"![{podpis}]({rel(plik)})")

    def wykres(self, fig, podpis: str, szerokosc: str = "100%"):
        self.dok.wykres(fig, podpis=podpis, szerokosc=szerokosc)
        self.md.append(f"*[Wykres: {podpis} — w PDF]*")

    def tabela(self, wiersze: list, *, tytul: str, uwagi=None, zrodlo: str | None = None, **kw):
        wiersze = [jawne(w) if isinstance(w, str) else {k: jawne(v) for k, v in w.items()} for w in wiersze]
        tytul, zrodlo = jawne(tytul), jawne(zrodlo)
        uwagi = jawne(uwagi) if isinstance(uwagi, str) else [jawne(u) for u in (uwagi or [])] or None
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
        tekst = jawne(re.sub(r"^\*Rys\. [^\n]*\*\s*$", "", tekst, flags=re.M))
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


# ============================================================================================ stan analiz
def pola_scinania(obl_md: str) -> dict:
    """{element: [„Pole P2”, …]} — pola płyt ze zbrojeniem na ścinanie (V_Ed > V_Rd,c) wg obliczeń statycznych."""
    out: dict[str, list[str]] = {}
    for sek in re.split(r"^### Poz\. ", obl_md or "", flags=re.M)[1:]:
        m = re.search(r"Element modelu: `([^`]+)`", sek)
        if not m:
            continue
        pola = re.findall(r"^#{4,6} (Pole [^—\n]+?) — ścinanie: V_Ed > V_Rd,c", sek, flags=re.M)
        if pola:
            out[m.group(1)] = sorted(set(p.strip() for p in pola), key=lambda s: (len(s), s))
    return out


def sekcje_pozycji(obl_md: str) -> dict:
    """{element: (nr, treść sekcji „### Poz. …”)} z obliczeń statycznych."""
    out = {}
    for sek in re.split(r"^### Poz\. ", obl_md or "", flags=re.M)[1:]:
        m, n = re.search(r"Element modelu: `([^`]+)`", sek), re.match(r"([\d.]+)", sek)
        if m and n:
            out[m.group(1)] = (n.group(1), sek)
    return out


def _f(txt) -> float | None:
    try:
        return float(str(txt).replace(" ", "").replace("\u202f", "").replace(",", "."))
    except (TypeError, ValueError):
        return None


def zestawienie_obciazen(sek: str) -> str:
    """Pozycje „#### Zestawienie obciążeń” (wiersze tabel i listy obciążeń, bez nagłówków z nazwą przegrody)."""
    m = re.search(r"^#### Zestawienie obciążeń\s*\n(.*?)(?=^#### |\Z)", sek, flags=re.M | re.S)
    return "\n".join(ln for ln in (m.group(1) if m else "").splitlines() if ln.startswith(("| ", "- ")))


def kontrole_spojnosci(D: dict) -> list[dict]:
    """Sprawdzenia spójności wyników BO z modelem i regułami kombinacji (weryfikacja PT — obliczenia) —
    każda niezgodność → pozycja NIEZAMKNIĘTE. Reguły ogólne: po poprawie modułów i ponownej analizie znikają."""
    W, p, b = [], D["p"], D["bud"]
    obl, mes = D["obl_md"] or "", D["mes_md"] or ""
    sek = sekcje_pozycji(obl)
    # (a) przekrój podwójnie zbrojony: A_s2 > 0 wymaga warunku zbrojenia ściskanego (górnego) w pozycji
    fund = {x["id"] for x in (D["wyniki"] or {}).get("pozycje", []) if x["rodzaj"] == "fundament"}
    for el, (nr, t) in sek.items():
        if el in fund:                   # płyta fundamentowa — miarodajna analiza MES i kontrola zbrojenia (rozdz. 5–6)
            continue
        as2 = [_f(x) for x in re.findall(r"A_s2 = [^\n]*?= \*\*([\d ,]+)\*\* mm²", t)]
        as2 = [x for x in as2 if x]
        if as2 and not re.search(r"^\| Zbrojenie (?:górne|ściskane)", t, flags=re.M):
            W.append(dict(obszar="Obliczenia statyczne", element=f"poz. {nr} {el}", wynik=f"A_s2 = {L(max(as2), 0)} mm²",
                          stan=NZ, opis="przekrój podwójnie zbrojony — brak warunku A_s2 ≤ A_s,prov (górą) w pozycji "
                          "i w kontroli zbrojenia rysunków; wysokość użyteczna d do przyjęcia z liczby warstw zbrojenia "
                          "dolnego — zwiększyć przekrój lub zespolić ze stropem, przeliczyć",
                          zrodlo="obliczenia statyczne; kontrola zbrojenia rysunków"))
    # (b) obciążenie obliczeniowe q_d nie mniejsze niż 6.10b z wypisanych g_k, q_k (q_k jako wiodące)
    zle = []
    for el, (nr, t) in sek.items():
        m = re.search(r"g_k; q_k = \*\*([\d ,]+); ([\d ,]+)\*\* kN/m", t)
        md = re.search(r"Obciążenie obliczeniowe: q_d = \*\*([\d ,]+)\*\* kN/m", t)
        if m and md:
            g, q, qd = _f(m.group(1)), _f(m.group(2)), _f(md.group(1))
            q610b = p.xi * p.gG_sup * g + p.gQ * q
            if qd < 0.99 * q610b:
                zle.append(f"{nr} {el} (q_d = {L(qd)} < {L(q610b)} kN/m)")
    if zle:
        W.append(dict(obszar="Obliczenia statyczne", element=f"nadproża / wieńce ({len(zle)})", wynik="—", stan=NZ,
                      opis="q_d mniejsze niż 6.10b z wypisanych g_k i q_k — zestawienie niesprawdzalne: wypisywać q_k "
                      "tylko z przypadków użytych w kombinacji, 6.10b uzupełnić o Σγ_Q·ψ₀·Q_k,i, nie łączyć kat. H "
                      "ze śniegiem (PN-EN 1991-1-1 p. 3.3.2), przeliczyć — poz. " + "; ".join(zle[:6])
                      + (f" (i {len(zle) - 6} innych)" if len(zle) > 6 else ""), zrodlo="obliczenia statyczne"))
    # (c) dachy z polem PV — ciężar PV w zestawieniu obciążeń; (d) dach zielony — woda retencyjna warstw
    pv = {x.get("dach"): x.get("n") for x in ((b.get("energia") or {}).get("pv") or {}).get("pola", [])}
    for el, (nr, t) in sek.items():
        zo = zestawienie_obciazen(t)
        if not zo:
            continue
        braki = []
        if el in pv and not re.search(r"\bPV\b|fotowolt|moduł|balast", zo, re.I):
            braki.append(f"ciężar pola PV ({pv[el]} modułów, stelaże i balast wg PT-4 IE)")
        if re.search(r"^\| Substrat", zo, flags=re.M) and not re.search(r"\bwod[aąyę]\b|nasycon", zo, re.I):
            braki.append("woda retencyjna substratu i maty drenażowej (stan nasycony)")
        if braki:
            W.append(dict(obszar="Zestawienie obciążeń", element=f"poz. {nr} {el}", wynik=pct(next(
                (x["wykorzystanie"] for x in (D["wyniki"] or {}).get("pozycje", []) if x["id"] == el), None)),
                stan=NZ, opis="brak w obciążeniach stałych: " + "; ".join(braki) + " — uzupełnić i przeliczyć",
                zrodlo="obliczenia statyczne; model (PV, warstwy dachu)"))
    # (e) garaż w MES płyty fundamentowej — kategoria F
    garaz = any("garaż" in str(x.get("nazwa", "")).lower() for x in b.get("pomieszczenia", []))
    if garaz and mes and not re.search(r"kat(?:egori\w*|\.)\s*F\b", mes):
        W.append(dict(obszar="MES płyty fundamentowej", element="strefa garażu", wynik="—", stan=NZ,
                      opis=f"obciążenie użytkowe garażu przyjęte jak kat. A — przypisać kat. F: q_k = {L(p.q_garaz)} "
                      f"kN/m², Q_k = {L(p.Q_garaz, 0)} kN (PN-EN 1991-1-1 tabl. 6.8 + NA) i przeliczyć MES",
                      zrodlo="raport MES płyty fundamentowej"))
    # (f) izolacja przeciwprzemarzaniowa zamiast głębokości posadowienia — obliczenie wg PN-EN ISO 13793
    glebokosc = [f"{x['id']}" for x in (D["wyniki"] or {}).get("pozycje", []) if any(
        w["eta"] > 1.0 and re.search(r"głębokoś|przemarz", w["opis"], re.I) for w in x["warunki"])]
    if glebokosc and not re.search(r"PN-EN ISO 13793[^\n]*(?:F_d|F_n)", obl + mes):
        iz = (b.get("fundamenty") or {}).get("izolacja_obwodowa") or {}
        W.append(dict(obszar="Posadowienie", element=f"{len(glebokosc)} pozycji: {glebokosc[0]}…{glebokosc[-1]}",
                      wynik="—", stan=NZ, opis="głębokość posadowienia mniejsza od h_z zastąpiona izolacją obwodową "
                      f"(D = {L(iz.get('D'))} m, d_n = {L(iz.get('d_n'))} m wg modelu) — brak obliczenia wg PN-EN ISO "
                      "13793 (wskaźnik mrozowy F_d dla lokalizacji)", zrodlo="obliczenia statyczne; model (fundamenty)"))
    # (g) parametry geotechniczne — jedno źródło (model „geotechnika”)
    gr = (b.get("geotechnika") or {}).get("grunt") or {}
    m0_mes = re.search(r"E_s = M₀[^=]*= ([\d ]+)·\(1\+", mes)
    por = [("φ'_k [°]", gr.get("phi"), p.grunt.fi_k, None), ("γ [kN/m³]", gr.get("gamma"), p.grunt.gamma, None),
           ("M₀ [kPa]", gr.get("M0"), p.grunt.M0, _f(m0_mes.group(1)) if m0_mes else None)]
    for nazwa, mod, st, me in por:
        rozb = [f"{k} {L(v, 0 if v and v > 100 else 1)}" for k, v in (("obliczenia statyczne", st), ("MES", me))
                if v is not None and mod is not None and abs(float(v) - float(mod)) > 1e-6]
        if rozb:
            W.append(dict(obszar="Projekt geotechniczny", element=nazwa, wynik=f"model {L(mod, 0 if mod > 100 else 1)}",
                          stan=NZ, opis="parametr niezgodny z modelem geotechnicznym: " + ", ".join(rozb)
                          + " — ujednolicić (jedno źródło: model „geotechnika”) i przeliczyć", zrodlo="model; "
                          "obliczenia statyczne; raport MES płyty fundamentowej"))
    return W


def stan_analiz(D: dict) -> dict:
    """Zestawienie stanu analiz zespołu BO. Wiersz: obszar, element, wynik, stan (NIEZAMKNIĘTE / ZASTĄPIONE /
    zamknięte), opis, źródło. Reguły są ogólne — po domknięciu analiz wiersze znikają lub zmieniają stan."""
    W, ok_obszary = [], OrderedDict()
    wyn = D["wyniki"] or {"pozycje": [], "uwagi": []}
    poz = wyn["pozycje"]
    # 0. aktualność wyników względem modelu
    for nazwa, (akt, kiedy) in D["aktualnosc"].items():
        if not akt:
            W.append(dict(obszar="Aktualność", element=nazwa, wynik=kiedy, stan=NZ,
                          opis=f"wyniki starsze niż model ({D['t_modelu']}) albo brak pliku — ponowić analizę",
                          zrodlo="czas modyfikacji plików"))
    # 1. pozycje obliczeń statycznych z niespełnionymi warunkami
    zast = set(re.findall(r"poz\. ([\d.]+) \S+ \(model ławy/stopy izolowanej[^\n]*ZASTĄPIONE", D["braki_md"]))
    for p in poz:
        if p["ok"]:
            continue
        zle = sorted({w["opis"]: w["eta"] for w in p["warunki"] if w["eta"] > 1.0}.items(), key=lambda x: -x[1])
        opis = "; ".join(f"{o} η = {pct(e)}" for o, e in zle[:4])
        if p["nr"] in zast:
            W.append(dict(obszar="Obliczenia statyczne", element=f"poz. {p['nr']} {p['id']}", wynik=pct(p["wykorzystanie"]),
                          stan="ZASTĄPIONE", opis=f"model ławy izolowanej ({opis}) — nośność i osiadanie: analiza MES "
                          "płyty fundamentowej (rozdz. 5); głębokość posadowienia: płyta na XPS z izolacją obwodową "
                          "(W-284) — sprawdzenie izolacji wg PN-EN ISO 13793 w pozycji „Posadowienie” (rozdz. 1)",
                          zrodlo="wyniki.json; BRAKI_DANYCH.md"))
        else:
            W.append(dict(obszar="Obliczenia statyczne", element=f"poz. {p['nr']} {p['id']}", wynik=pct(p["wykorzystanie"]),
                          stan=NZ, opis=opis + " — wymaga zmiany przekroju / schematu (REKOMENDACJE_MODEL.md)",
                          zrodlo="wyniki.json"))
    ok_obszary["Obliczenia statyczne"] = (sum(p["ok"] for p in poz), len(poz))
    # 2. ścinanie płyt: zbrojenie poprzeczne wymagane obliczeniowo — czy objęte kontrolą rysunków
    kz = (D["kz"] or {}).get("wiersze", [])
    pola = pola_scinania(D["obl_md"])
    for p in poz:
        if p["rodzaj"] != "plyta":
            continue
        ws = [w["eta"] for w in p["warunki"] if w["opis"].startswith("Ścinanie") or "strzemion" in w["opis"]
              or "krzyżulc" in w["opis"]]
        if not ws:
            continue
        strzemiona = any("strzemion" in w["opis"] for w in p["warunki"])
        w_kontroli = any(r["element"] == p["id"] and re.search(r"strzem|ścin", r["miejsce"], re.I) for r in kz)
        if strzemiona and not w_kontroli:
            W.append(dict(obszar="Ścinanie płyt", element=f"poz. {p['nr']} {p['id']}", wynik=f"η_max = {pct(max(ws))}",
                          stan=NZ, opis="V_Ed > V_Rd,c — zbrojenie na ścinanie płyty (PN-EN 1992-1-1 6.2.3, 9.3.2) w polach: "
                          + (", ".join(pola.get(p["id"], [])) or "wg obliczeń") + "; brak w kontroli zbrojenia "
                          "rysunków (A_sw,prov ≥ A_sw,req) — do domknięcia",
                          zrodlo="wyniki.json; obliczenia_statyczne.md; kontrola_zbrojenia.json"))
        elif max(ws) > 1.0:
            W.append(dict(obszar="Ścinanie płyt", element=f"poz. {p['nr']} {p['id']}", wynik=pct(max(ws)), stan=NZ,
                          opis="nośność na ścinanie niewystarczająca", zrodlo="wyniki.json"))
    # 3. MES płyty fundamentowej
    if not D["mes_md"]:
        W.append(dict(obszar="MES płyty fundamentowej", element="PF", wynik="—", stan=NZ,
                      opis="brak raportu MES płyty fundamentowej", zrodlo="plyta_fundamentowa_MES.md"))
    else:
        n = n_ok = 0
        for tab in tabele_md(D["mes_md"]):
            for r in tab:
                if "Stan" not in r:
                    continue
                n += 1
                if "NIESPEŁNION" in r["Stan"].upper():
                    W.append(dict(obszar="MES płyty fundamentowej", element=r.get("Warunek", "—"), wynik=r.get("η", "—"),
                                  stan=NZ, opis=f"{r.get('Efekt', '')} > {r.get('Nośność / limit', '')} "
                                  f"({r.get('Podstawa', '')}) — pogrubienie / zmiana posadowienia (REKOMENDACJE_MODEL.md)",
                                  zrodlo="plyta_fundamentowa_MES.md"))
                else:
                    n_ok += 1
        ok_obszary["MES płyty fundamentowej"] = (n_ok, n)
    # 4. kontrola zbrojenia rysunków
    for r in kz:
        if not r["ok"]:
            W.append(dict(obszar="Kontrola zbrojenia", element=f"{r['element']} — {r['miejsce']}",
                          wynik=f"{L(r['As_prov'], 0)} < {L(max(r['As_req'], r['As_min']), 0)} {r['jedn']}", stan=NZ,
                          opis=re.sub(r"\s*\[WYMAGA ZMIANY MODELU\].*", " [WYMAGA ZMIANY MODELU]", r.get("uwagi") or "—"),
                          zrodlo="kontrola_zbrojenia.json"))
    if D["kz"]:
        ok_obszary["Kontrola zbrojenia rysunków"] = (D["kz"]["ok"], D["kz"]["razem"])
    # 4a. spójność wyników z modelem i regułami kombinacji (weryfikacja PT)
    W += kontrole_spojnosci(D)
    # 5. uwagi biblioteki „[WYMAGA ANALIZY]” (grupowane wg treści)
    grupy: OrderedDict = OrderedDict()
    for u in wyn.get("uwagi", []):
        if "WYMAGA ANALIZY" not in u:
            continue
        m = re.match(r"^(?:Ściana nośna )?([^:\s]+)[: ]\s*(.*)$", u)
        klucz = re.sub(r"\b(SL|S\d-|P)\d+\w*\b", "…", m.group(2) if m else u)
        grupy.setdefault(klucz, []).append(u)
    for klucz, lst in grupy.items():
        W.append(dict(obszar="Uwagi analizy", element=f"{len(lst)} ×", wynik="—", stan=NZ,
                      opis="; ".join(lst[:3]) + (f" (i {len(lst) - 3} podobnych)" if len(lst) > 3 else ""),
                      zrodlo="wyniki.json — uwagi"))
    return dict(wiersze=W, obszary=ok_obszary, n_nz=sum(w["stan"] == NZ for w in W), zast=zast)


# ============================================================================================ rozdziały
def rozdz_stan(o: Opis, D: dict, S: dict, ark_uwagi: list[str]):
    """1. Stan opracowania — analizy zamknięte / NIEZAMKNIĘTE (jawnie, aktualizowane z wyników BO)."""
    o.rozdzial("Stan opracowania i analiz konstrukcji", podstawa="§ 23 pkt 1 RPB; W-274")
    nz = S["n_nz"] + len(ark_uwagi)
    o.tekst(f"""
    Zestawienie generowane automatycznie przy każdym złożeniu tomu z wyników obliczeń konstrukcji (model budynku
    z {D['t_modelu']}). Pozycja niezamknięta to analiza nie domknięta: warunek stanu granicznego niespełniony,
    zbrojenie wymagane obliczeniowo nieujęte w kontroli rysunków, obciążenie lub parametr niezgodny z modelem,
    uwaga programu obliczeń wymagająca analizy, wynik starszy niż model albo arkusz rysunkowy z błędem. Pozycja
    **ZASTĄPIONE** — wynik modelu uproszczonego zastąpiony analizą dokładniejszą (wskazaną w opisie). Po domknięciu
    analiz i ponownym złożeniu tomu wiersze znikają z zestawienia.
    """)
    if nz:
        o.wniosek(f"**PROJEKT KONSTRUKCJI NIEZAMKNIĘTY — {nz} {odmiana(nz, 'pozycja', 'pozycje', 'pozycji')} {NZ}.** "
                  "Tom jest wersją roboczą. Do czasu domknięcia wszystkich pozycji z tabeli poniżej — zmiany modelu "
                  "wg zaleceń zespołu konstrukcji, ponowna analiza (obliczenia statyczne, MES płyty fundamentowej, "
                  "kontrola zbrojenia rysunków) na zamrożonej wersji modelu i ponowne złożenie tomu — **nie podpisywać** "
                  "oświadczenia projektanta PT (art. 41 ust. 4a pkt 2 PB) i nie przekazywać tomu do realizacji robót.",
                  alarm=True)
    else:
        o.wniosek("Wszystkie analizy konstrukcji objęte zestawieniem są domknięte (brak pozycji NIEZAMKNIĘTYCH).")
    ob = [{"Obszar analizy": k, "Warunki spełnione": f"{a} z {b}", "Stan": "zamknięte" if a == b else NZ}
          for k, (a, b) in S["obszary"].items()]
    ob.append({"Obszar analizy": "Część rysunkowa (arkusze i kontrola jakości arkuszy)",
               "Warunki spełnione": "komplet" if not ark_uwagi else f"brak {len(ark_uwagi)}",
               "Stan": "zamknięte" if not ark_uwagi else NZ})
    o.tabela(ob, tytul="Stan analiz według obszarów", wyrownanie={"Obszar analizy": "l"},
             szerokosci=[None, "40mm", "34mm"], zrodlo="wyniki.json, plyta_fundamentowa_MES.md, kontrola_zbrojenia.json")
    kol = ("Obszar", "Element", "Wynik", "Opis", "Źródło")
    rows = [dict(zip(kol, (w["obszar"], w["element"], w["wynik"], w["opis"], w["zrodlo"])))
            for w in S["wiersze"] if w["stan"] == NZ]
    rows += [dict(zip(kol, ("Część rysunkowa", u.split(":")[0], "—", u.split(":", 1)[-1].strip(),
                            "arkusze; raport kontroli arkuszy"))) for u in ark_uwagi]
    if rows:
        o.tabela(rows, tytul=f"Pozycje {NZ} (do domknięcia przez zespół BO przed wydaniem PT)", klasa="zwarta",
                 lp=True, wyrownanie={"Opis": "l", "Element": "l"}, szerokosci=["7mm", "24mm", "26mm", "20mm", None, "28mm"])
    zast = [dict(zip(("Element", "Wynik modelu uproszczonego", "Opis"), (w["element"], w["wynik"], w["opis"])))
            for w in S["wiersze"] if w["stan"] == "ZASTĄPIONE"]
    if zast:
        o.tabela(zast, tytul="Pozycje ZASTĄPIONE analizą dokładniejszą", klasa="zwarta", wyrownanie={"Opis": "l"},
                 szerokosci=["26mm", "26mm", None], zrodlo="BRAKI_DANYCH.md (zespół BO)")


REJESTR = REPO / "docs/10_podstawy_prawne/00_rejestr_wymagan.md"
# Normy stosowane w tomie poza wykazem biblioteki obliczeń (uwagi na arkuszach, specyfikacja wykonania) — numer i zakres;
# wydanie i status odczytywane z rejestru wymagań (A.3); brak w rejestrze → pole do uzupełnienia (bez domysłów).
NORMY_DODATKOWE = [
    ("PN-EN 206+A2:2021-08", "Beton — wymagania, właściwości użytkowe, produkcja i zgodność (specyfikacja betonu)"),
    ("PN-B-06265:2022-08", "Krajowe uzupełnienie PN-EN 206 (specyfikacja betonu)"),
    ("PN-EN 13670", "Wykonywanie konstrukcji z betonu (otulina, pielęgnacja, rozszalowanie — uwagi na arkuszach)"),
    ("PN-EN 10080", "Stal do zbrojenia betonu — spajalna stal zbrojeniowa"),
    ("PN-EN 1090-2", "Wykonanie konstrukcji stalowych (słupy stalowe fasady)"),
    ("PN-EN ISO 13793", "Właściwości cieplne budynków — projektowanie fundamentów chroniących przed wysadziną"),
]


def _rejestr_a3() -> list[list[str]]:
    """Wiersze tabeli A.3 rejestru wymagań (normy, status PKN): [norma, status, zastępcza/uwaga, rola]."""
    t = REJESTR.read_text(encoding="utf-8") if REJESTR.exists() else ""
    m = re.search(r"^### A\.3[^\n]*\n(.*?)(?=^### )", t, flags=re.M | re.S)
    out = []
    for ln in (m.group(1) if m else "").splitlines():
        kom = [c.strip() for c in ln.strip().strip("|").split("|")]
        if ln.startswith("|") and len(kom) >= 4 and not set("".join(kom)) <= set("-: ") and kom[0] != "Norma":
            out.append(kom)
    return out


def _numer_normy(n: str) -> str:
    """Rdzeń oznaczenia normy do wyszukania w rejestrze: „1992-1-1”, „ISO 3766”, „206+A2”, „PN-B-06265”."""
    m = re.match(r"PN-(?:EN )?(?:(ISO|IEC) )?([\dA-Z][\w+-]*?)(?=:|\s|$)", n)
    if not m:
        return n
    rdzen = m.group(2)
    if n.startswith(("PN-B-", "PN-H-")):
        return n.split(":")[0].split(" ")[0]
    return f"{m.group(1)} {rdzen}" if m.group(1) else rdzen


def status_normy(norma: str, a3: list) -> tuple[str, str]:
    """(oznaczenie z wydaniem, status wg rejestru A.3). Wydanie uzupełniane z rejestru, gdy go brak."""
    num = _numer_normy(norma)
    rx = re.compile(rf"(?<![\d.-]){re.escape(num)}(?![\d])")
    wiersz = next((r for r in a3 if rx.search(r[0])), None)
    ozn = norma
    if ":" not in norma.split(" — ")[0]:
        w = re.search(rf"(?<![\d.-]){re.escape(num)}((?:\+A\d+)?:[\d-]+)", wiersz[0]) if wiersz else None
        ozn = norma + w.group(1) if w else f"{norma} {do_uzup('rok wydania — poza rejestrem wymagań A.3')}"
    if not wiersz:
        return ozn, do_uzup("status w katalogu PKN — poza rejestrem wymagań A.3")
    st = re.sub(r"\*\*WYCOF\.\*\*", "wycofana", wiersz[1]).replace("aktualne", "aktualna").strip()
    zast = re.sub(r"\*\*WYCOF\.\*\*", "wycofaną", wiersz[2]).replace("**", "")
    zast = re.sub(r"\s*\([^()]*\)", "", zast).strip()                # bez dopowiedzeń w nawiasach
    if "wycofana" in st and zast not in ("", "—"):
        st += f"; zastępcza: {zast}"
    elif zast not in ("", "—") and "zastąpiła" not in zast:
        st += f" ({zast})"
    return ozn, st


def normy_bo(D: dict) -> list[dict]:
    """Wykaz norm tomu: z biblioteki obliczeń (``NORMY``) + stosowane w uwagach arkuszy; wydanie i status z rejestru."""
    a3, W = _rejestr_a3(), []
    for wpis in D["RAP"].NORMY:
        czesci = [c.strip().partition(" — ") for c in wpis.split("; ")]
        for k, (n, _, tyt) in enumerate(czesci):
            if not n.startswith("PN"):
                continue                              # akty prawne — w podrozdziale „Przepisy”
            tyt = tyt or next((t for _, _, t in czesci[k + 1:] if t), "—")   # „A; B — tytuł” → tytuł wspólny
            if n.startswith("(+") and W:                                    # „(+Ap2…)” — poprawka poprzedniej
                W[-1] = (W[-1][0] + " " + n, W[-1][1])
                continue
            W.append((n, tyt[:1].upper() + tyt[1:]))
    W += NORMY_DODATKOWE
    out = []
    for n, tyt in W:
        ozn, st = status_normy(n, a3)
        out.append({"Norma (wydanie)": ozn, "Zakres": tyt, "Status (rejestr wymagań A.3, PKN)": st})
    return out


def rozdz_podstawa(o: Opis, D: dict):
    """2. Podstawa opracowania: przepisy, normy (wydanie i status), dane wejściowe z datami."""
    o.rozdzial("Podstawa opracowania", podstawa="§ 23 pkt 1 RPB")
    meta = D["bud"].get("meta", {})
    o.tekst(f"""
    ## Przepisy
    * ustawa z dnia 7 lipca 1994 r. — Prawo budowlane (PB, t.j. Dz.U. 2026 poz. 524 ze zm.): art. 34 ust. 3 pkt 3
      lit. a (projektowane rozwiązania konstrukcyjne obiektu wraz z wynikami obliczeń statyczno-wytrzymałościowych)
      i lit. d (geotechniczne warunki posadowienia) — zakres projektu technicznego, art. 41 ust. 4a pkt 2
      (oświadczenie projektanta PT), art. 102a (stosowanie WT w dotychczasowym brzmieniu);
    * rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego (RPB, Dz.U. 2020 poz. 1609,
      t.j. Dz.U. 2022 poz. 1679 ze zm.) — § 23 pkt 1–3 i 10 (część opisowa PT), § 24 pkt 1 (część rysunkowa);
      § 23 pkt 12 (dane dotyczące warunków ochrony ludności, dodany przez Dz.U. 2026 poz. 597) — nie dotyczy:
      PZT i PAB nie przewidują obiektu zbiorowej ochrony ani miejsca doraźnego schronienia (PAB, § 20 ust. 1
      pkt 14 RPB — nie dotyczy);
    * rozporządzenie w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (WT,
      t.j. Dz.U. 2022 poz. 1225 ze zm.) — w brzmieniu stosowanym na podstawie art. 102a PB ({meta.get('uwagi', '—')});
    * rozporządzenie MTBiGM z 25.04.2012 w sprawie ustalania geotechnicznych warunków posadawiania obiektów
      budowlanych (Dz.U. 2012 poz. 463) — § 7 ust. 2 (kat. II: dokumentacja badań podłoża i projekt geotechniczny),
      § 9, § 10.

    ## Normy
    Eurokody 1. generacji z załącznikami krajowymi — bez mieszania z 2. generacją (rejestr wymagań A.3). Wycofanie
    normy nie zakazuje jej stosowania (stanowisko PKN); normy wycofane podano ze statusem i normą zastępczą.
    """)
    o.tabela(normy_bo(D), tytul="Normy stosowane w projekcie konstrukcji — wydanie i status", klasa="zwarta",
             wyrownanie={"Norma (wydanie)": "l", "Zakres": "l", "Status (rejestr wymagań A.3, PKN)": "l"},
             szerokosci=["52mm", None, "58mm"], zrodlo="rejestr wymagań, sekcja A.3 (status PKN)")
    o.tekst("""
    Specyfikacja betonu (klasa wytrzymałości, klasa ekspozycji XC/XF, maksymalny w/c, kruszywo, konsystencja)
    w opisie i w uwagach na arkuszach — wg PN-EN 206+A2:2021-08 i PN-B-06265:2022-08: normy wycofane, stosowane
    jako wiedza techniczna dla spójności z PN-EN 1992-1-1:2008 (rejestr wymagań D-09). Przed wydaniem PT normę
    deklaracji betonu (PN-EN 206-1:2026-09) potwierdzić z wytwórnią betonu.
    """)
    wiersze = [{"Dane wejściowe": "model budynku", "Źródło": f"wersja {meta.get('wersja', '—')}",
                "Stan": D["t_modelu"]}]
    zr = {"obliczenia statyczne": "rozdz. 4", "MES płyty fundamentowej": "rozdz. 5",
          "kontrola zbrojenia": "rozdz. 6"}
    for nazwa, (akt, kiedy) in D["aktualnosc"].items():
        wiersze.append({"Dane wejściowe": nazwa, "Źródło": f"zespół konstrukcji — {zr[nazwa]}",
                        "Stan": f"{kiedy} — {'aktualne względem modelu' if akt else NZ + ' (starsze niż model)'}"})
    o.tabela(wiersze, tytul="Dane wejściowe tomu (odczyt przy każdym złożeniu)", wyrownanie={"Źródło": "l"},
             szerokosci=["46mm", None, "64mm"])


def _zakres_wym(vals, n=2, jedn="m") -> str:
    vals = sorted({round(float(v), 3) for v in vals if v is not None})
    if not vals:
        return "—"
    return f"{L(vals[0], n)} {jedn}" if len(vals) == 1 else f"{L(vals[0], n)}–{L(vals[-1], n)} {jedn}"


def _mat(D, kod) -> str:
    m = (D["bud"].get("materialy") or {}).get(kod) or {}
    return m.get("nazwa", kod or "—")


def elementy_konstrukcji(D: dict) -> list[dict]:
    """Zestawienie elementów nośnych z modelu (identyfikatory, wymiary, materiał) z odesłaniem do pozycji obliczeń."""
    b, wyn = D["bud"], (D["wyniki"] or {}).get("pozycje", [])
    poz = {p["id"]: p["nr"] for p in wyn}

    def nr(ids):
        n = sorted({poz[i] for i in ids if i in poz}, key=lambda s: [int(x) for x in s.split(".")])
        return f"{n[0]}–{n[-1]}" if len(n) > 1 else (n[0] if n else "—")
    fund = b.get("fundamenty", {}).get("elementy", [])
    pf = [e for e in fund if "obrys" in e]
    zf = [e for e in fund if e["id"].startswith("ZF")]
    sf = [e for e in fund if e["id"].startswith("SF")]
    przeg = b.get("przegrody", {})
    nosne = {k for k, v in przeg.items() if v.get("typ") in ("sciana_zewn", "sciana_wewn_nosna")}
    sc = [s for s in b.get("sciany", []) if s.get("przegroda") in nosne]
    mat_sc = sorted({w["mat"] for k in {s["przegroda"] for s in sc} for w in przeg[k].get("warstwy", [])
                     if w.get("konstrukcyjna") and "WELNA" not in w["mat"].upper()})
    wsp = [w for w in b.get("wsporniki_plyty", []) if str(w.get("mat", "")).startswith("ZB")]
    R = [
        dict(e="Płyta fundamentowa", ids=", ".join(e["id"] for e in pf), w="h = " + _zakres_wym([e["h"] for e in pf]),
             m=_mat(D, pf[0]["mat"]) if pf else "—", p="rozdz. 5 (MES)"),
        dict(e="Żebra (pogrubienia) płyty pod ścianami", ids=f"{zf[0]['id']}…{zf[-1]['id']} ({len(zf)} szt.)" if zf else "—",
             w=f"b = {_zakres_wym([e['b'] for e in zf])}, h = {_zakres_wym([e['h'] for e in zf])} (pod płytą)",
             m=_mat(D, zf[0]["mat"]) if zf else "—", p=nr([e["id"] for e in zf])),
        dict(e="Pogrubienia płyty pod słupami", ids=", ".join(e["id"] for e in sf) or "—",
             w=f"{_zakres_wym([e['b'] for e in sf])} × {_zakres_wym([e['b'] for e in sf])}, h = {_zakres_wym([e['h'] for e in sf])}",
             m=_mat(D, sf[0]["mat"]) if sf else "—", p=nr([e["id"] for e in sf])),
        dict(e="Ściany nośne murowe i żelbetowe", ids=f"{len(sc)} ścian (P0–P2)", w="wg przegród "
             + ", ".join(sorted({s['przegroda'] for s in sc})), m="; ".join(_mat(D, k) for k in mat_sc),
             p=nr([s["id"] for s in sc])),
        dict(e="Stropy międzykondygnacyjne (płyty)", ids=", ".join(s["id"] for s in b.get("stropy", [])),
             w="h = " + _zakres_wym([s["grubosc"] for s in b.get("stropy", [])]),
             m=_mat(D, b["stropy"][0]["mat"]) if b.get("stropy") else "—", p=nr([s["id"] for s in b.get("stropy", [])])),
        dict(e="Stropodachy (płyty)", ids=", ".join(s["id"] for s in b.get("dachy", [])),
             w="h = " + _zakres_wym([s["plyta"]["grubosc"] for s in b.get("dachy", []) if s.get("plyta")]),
             m=_mat(D, "ZB_C25"), p=nr([s["id"] for s in b.get("dachy", [])])),
        dict(e="Płyty wspornikowe (okapy, daszki) z łącznikami termoizolacyjnymi", ids=", ".join(w["id"] for w in wsp),
             w="h = " + _zakres_wym([w["grubosc"] for w in wsp]), m=_mat(D, wsp[0]["mat"]) if wsp else "—",
             p=nr([w["id"] for w in wsp])),
        dict(e="Belki, podciągi i nadproża żelbetowe (model)", ids=f"{len(b.get('belki', []))} szt.",
             w=f"b = {_zakres_wym([x['b'] for x in b.get('belki', [])])}, h = {_zakres_wym([x['h'] for x in b.get('belki', [])])}",
             m="; ".join(sorted({_mat(D, x['mat']) for x in b.get('belki', [])})), p=nr([x["id"] for x in b.get("belki", [])])),
        dict(e="Słupy", ids=", ".join(s["id"] for s in b.get("slupy", [])),
             w="; ".join(sorted({str(s.get("przekroj")) for s in b.get("slupy", [])})),
             m="; ".join(sorted({_mat(D, s['mat']) for s in b.get('slupy', [])})), p=nr([s["id"] for s in b.get("slupy", [])])),
        dict(e="Schody (płyty biegów i spoczników)", ids=", ".join(s["id"] for s in b.get("schody", [])),
             w="h = " + _zakres_wym([s.get("plyta", {}).get("grubosc") for s in b.get("schody", [])]),
             m=_mat(D, b["schody"][0]["mat"]) if b.get("schody") else "—", p=nr([s["id"] for s in b.get("schody", [])])),
    ]
    zb = [p for p in wyn if p["rodzaj"] in ("nadproze", "wieniec")]
    if zb:
        R.append(dict(e="Nadproża i wieńce (pozycje obliczeń)", ids=f"{len(zb)} {odmiana(len(zb), 'pozycja', 'pozycje', 'pozycji')}", w="wg obliczeń statycznych",
                      m=_mat(D, "ZB_C25"), p=nr([p["id"] for p in zb])))
    return [{"Element": r["e"], "Identyfikatory (model)": r["ids"], "Wymiary": r["w"], "Materiał": r["m"],
             "Poz. obliczeń": r["p"]} for r in R]


def podsekcja_md(tekst: str, naglowek: str) -> str:
    """Treść podsekcji „### naglowek…” (do następnego „### ” lub „## ”)."""
    m = re.search(rf"^### {re.escape(naglowek)}[^\n]*\n(.*?)(?=^#{{2,3}} |\Z)", tekst or "", flags=re.M | re.S)
    return m.group(1).strip() if m else ""


def substrat_w_obliczeniach(D: dict, zal_modelu) -> str:
    """Ciężar substratu dachu zielonego przyjęty w obliczeniach (wiersz „Substrat…” zestawienia obciążeń) i jego
    porównanie z założeniem modelu (konstrukcja.obciazenia.dach_zielony) — rozbieżność jawnie."""
    out = []
    for el, (nr, t) in sekcje_pozycji(D["obl_md"]).items():
        m = re.search(r"^\| (Substrat[^|]*)\| ([^|]+)\| ([\d,]+) \|", zestawienie_obciazen(t), flags=re.M)
        if m:
            out.append((el, nr, m.group(2).strip(), _f(m.group(3))))
    if not out:
        return ""
    el, nr, obl, gk = out[0]
    txt = (f"; dach zielony w obliczeniach (poz. {', '.join(f'{n} {e}' for e, n, _, _ in out)}): substrat "
           f"g_k = {L(gk, 2)} kN/m² ({obl})")
    m = re.search(r"≈\s*([\d,]+)\s*kN/m²", str(zal_modelu or ""))
    if m and abs(_f(m.group(1)) - gk) > 0.05:
        txt += (f" — mniej niż założenie modelu ({m.group(1)} kN/m², stan nasycony): brak wody retencyjnej, "
                f"pozycja {NZ} (rozdz. 1)")
    return txt


def rozdz_konstrukcja(o: Opis, D: dict):
    """3. Rozwiązania konstrukcyjne, schematy statyczne, założenia i obciążenia, materiały (§ 23 pkt 1 RPB)."""
    b, p, obl = D["bud"], D["p"], D["obl_md"] or ""
    k = b.get("konstrukcja", {})
    kond = b.get("kondygnacje", [])
    fund = b.get("fundamenty", {})
    o.rozdzial("Rozwiązania konstrukcyjne obiektu", podstawa="§ 23 pkt 1 RPB", nowa_strona=True)
    o.tekst(f"""
    ## Układ konstrukcyjny
    Budynek mieszkalny jednorodzinny, {len(kond)} kondygnacje nadziemne ({', '.join(x['nazwa'] for x in kond)}),
    bez podpiwniczenia; wysokości kondygnacji {', '.join(L(x['wys_kondygnacji']) for x in kond)} m. Konstrukcja
    ścianowo-płytowa: ściany nośne murowane ({k.get('mur', '—')}), stropy i stropodachy — płyty żelbetowe
    monolityczne krzyżowo zbrojone, lokalnie podciągi i belki żelbetowe (w tym belki odwrócone w licu ścian),
    płyty wspornikowe (okapy, daszek) z łącznikami termoizolacyjnymi, słupy stalowe fasady. Posadowienie
    bezpośrednie: {'płyta fundamentowa z żebrami pod ścianami nośnymi' if fund.get('typ') == 'plyta' else fund.get('typ', '—')}
    ({fund.get('uwagi', '—')}). Klasa konsekwencji {k.get('klasa_konsekwencji', '—')}, klasa niezawodności
    {k.get('klasa_niezawodnosci', '—')}, projektowy okres użytkowania {k.get('okres_uzytkowania', '—')} lat, klasa
    konstrukcji {k.get('klasa_konstrukcji', '—')} (PN-EN 1990, PN-EN 1992-1-1 tabl. 4.3N). Sztywność przestrzenną
    zapewniają tarcze stropowe współpracujące ze ścianami murowymi w dwóch kierunkach [ZAŁ].

    Ścieżki obciążeń elementów nietypowych (wg modelu): wsporniki — {k.get('wsporniki', '—')}; bryła A —
    {k.get('sciezka_obciazen_wspornika_A', '—')}.
    """)
    o.tabela(elementy_konstrukcji(D), tytul="Zestawienie elementów konstrukcji (generowane z modelu)", klasa="zwarta",
             wyrownanie={"Element": "l", "Identyfikatory (model)": "l", "Wymiary": "l", "Materiał": "l"},
             szerokosci=["34mm", "30mm", "34mm", None, "20mm"], zrodlo="model/budynek.yaml; wyniki.json")
    o.rozdzial("Schematy statyczne i metody obliczeń", poziom=2)
    o.tekst("Zastosowane schematy statyczne (konstrukcyjne) i modele obliczeniowe "
            "programu obliczeń konstrukcji; schemat statyczny każdego elementu podano w jego pozycji obliczeń "
            "(rozdz. 4, podrozdział „Opis i schemat statyczny” z rysunkiem schematu).\n\n"
            + "\n".join(f"* {t}" for t in D["RAP"].METODY))
    o.rozdzial("Założenia do obliczeń i obciążenia", poziom=2, podstawa="PN-EN 1990, PN-EN 1991 + NA")
    obc = k.get("obciazenia", {})
    s_d = wartosc_md(obl, "Obciążenie śniegiem")
    qp = wartosc_md(obl, "Szczytowe ciśnienie prędkości")
    o.tabela([
        {"Oddziaływanie": "śnieg (PN-EN 1991-1-3 + NA)", "Założenie": obc.get("snieg", "—"),
         "Wartość": f"s_k = {L(p.s_k)} kN/m²; C_e = {L(p.C_e)}, C_t = {L(p.C_t)}; s (dach płaski) = {s_d or '—'} kN/m²"},
        {"Oddziaływanie": "wiatr (PN-EN 1991-1-4 + NA)", "Założenie": obc.get("wiatr", "—"),
         "Wartość": f"v_b,0 = {L(p.v_b0, 1)} m/s, teren kat. {p.kategoria_terenu}; q_p = {qp or '—'} kN/m²"},
        {"Oddziaływanie": "użytkowe (PN-EN 1991-1-1 + NA)", "Założenie": obc.get("uzytkowe", "—"),
         "Wartość": f"stropy q_k = {L(p.q_strop)} kN/m² (Q_k = {L(p.Q_strop, 1)} kN); schody {L(p.q_schody)}; "
                    f"tarasy {L(p.q_taras)}; dach H {L(p.q_dach_H)}; garaż kat. F {L(p.q_garaz)} kN/m² (Q_k = {L(p.Q_garaz, 0)} kN)"},
        {"Oddziaływanie": "stałe (ciężar własny, warstwy)", "Założenie": f"dach zielony (model): {obc.get('dach_zielony', '—')}",
         "Wartość": f"żelbet {L(p.ciezar_zelbetu, 1)} kN/m³; warstwy przegród z modelu (materiały, grubości)"
                    + substrat_w_obliczeniach(D, obc.get("dach_zielony"))},
        {"Oddziaływanie": "kombinacje (PN-EN 1990 + NA)", "Założenie": f"{p.klasa_konsekwencji}, K_FI = {L(p.K_FI, 1)}",
         "Wartość": f"STR/GEO 6.10a/6.10b: γ_G = {L(p.gG_sup)}, ξ = {L(p.xi)}, γ_Q = {L(p.gQ)}; EQU: "
                    f"{L(p.EQU_gG_dst)}·G_dst + {L(p.EQU_gQ)}·Q_dst ≤ {L(p.EQU_gG_stb)}·G_stb"},
    ], tytul="Założenia i obciążenia", klasa="zwarta", wyrownanie={"Założenie": "l", "Wartość": "l"},
        szerokosci=["34mm", None, "72mm"],
        zrodlo="model/budynek.yaml (konstrukcja.obciazenia); Parametry.z_wymagan (wymagania.yaml W-261…W-265); "
               "obliczenia statyczne poz. 0.4")
    o.tekst("Wyprowadzenie wartości śniegu (zaspy przy uskokach, sytuacja wyjątkowa B2) i wiatru (strefy ścian "
            "i dachu) — obliczenia statyczne, poz. 0.4 (rozdz. 4).")
    o.rozdzial("Materiały, klasy ekspozycji i otulenia", poziom=2, podstawa="PN-EN 1992-1-1 4.4.1; PN-EN 1996-1-1")
    bet = k.get("beton", {})
    o.tekst(f"""
    * beton: {'; '.join(f'{kk.replace("_", " ")} — {vv}' for kk, vv in bet.items()) or '—'};
    * stal zbrojeniowa {k.get('stal_zbrojeniowa', p.stal_zbr)} (klasa ciągliwości C), f_yk = {L(p.f_yk, 0)} MPa,
      f_yd = {L(p.f_yd, 1)} MPa; stal konstrukcyjna {p.stal_konstr};
    * mur: {k.get('mur', '—')};
    * klasy ekspozycji wg roli elementu: {'; '.join(f'{r} {x} ({p.beton_ekspozycja.get(x, "—")})' for r, x in p.ekspozycja.items())}.
    """)
    tab03 = podsekcja_md(obl, "0.3 Materiały")
    if tab03:
        o.tekst(tab03)
    else:
        o.wniosek(f"Brak podsekcji 0.3 w obliczeniach statycznych — tabela otulin {NZ}.", alarm=True)


def grupy_pozycji(D: dict) -> OrderedDict:
    """{nr grupy: tytuł} ze spisu pozycji obliczeń statycznych."""
    out = OrderedDict()
    for tab in tabele_md(D["obl_md"]):
        if tab and "Poz." in tab[0] and "η_max" in tab[0]:
            for r in tab:
                m = re.match(r"\*\*(\d+)\*\*", r["Poz."])
                if m:
                    out[m.group(1)] = r["Opis"].strip("*")
            break
    return out


def _wykres_eta(poz: list, grupy: OrderedDict, zast: set):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(10, 3.6))
    x = range(len(poz))
    eta = [100 * p["wykorzystanie"] for p in poz]
    cap = 200.0
    ax.bar(x, [min(e, cap) for e in eta], width=0.8,
           color=["#2a78d6" if p["ok"] else "#9a9994" if p["nr"] in zast else "#d03b3b" for p in poz], linewidth=0)
    ax.axhline(100, color="#0b0b0b", lw=0.8, ls="--")
    for i, e in enumerate(eta):
        if e > cap:
            ax.text(i, cap + 2, f"{e:.0f}", ha="center", va="bottom", fontsize=6, rotation=90)
    gr = [p["nr"].split(".")[0] for p in poz]
    starts = [i for i in range(len(gr)) if i == 0 or gr[i] != gr[i - 1]]
    for s in starts[1:]:
        ax.axvline(s - 0.5, color="#dcdbd6", lw=0.8)
    ax.set_xticks([(s + (starts[k + 1] if k + 1 < len(starts) else len(gr))) / 2 - 0.5 for k, s in enumerate(starts)])
    ax.set_xticklabels([gr[s] for s in starts], fontsize=8)
    ax.set_xlim(-1, len(poz))
    ax.set_ylim(0, cap + 30)
    ax.set_ylabel("η_max [%]")
    ax.set_xlabel("grupa pozycji (numer) — " + "; ".join(f"{k} {v.lower()}" for k, v in grupy.items()), fontsize=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout()
    return fig


def rozdz_wyniki(o: Opis, D: dict, S: dict):
    """3.5 Podstawowe wyniki obliczeń; 3.6 pomiary przemieszczeń; 3.7 zakres analiz wymagający osobnych obliczeń."""
    poz = (D["wyniki"] or {}).get("pozycje", [])
    grupy = grupy_pozycji(D)
    o.rozdzial("Podstawowe wyniki obliczeń", poziom=2, podstawa="§ 23 pkt 1 RPB")
    rows = []
    for g, tyt in grupy.items():
        pg = [p for p in poz if p["nr"].split(".")[0] == g]
        if not pg:
            continue
        mx = max(pg, key=lambda p: p["wykorzystanie"])
        zle = [p for p in pg if not p["ok"]]
        rows.append({"Grupa": f"{g}. {tyt}", "Pozycje": len(pg), "η_max": pct(mx["wykorzystanie"]),
                     "Element miarodajny": f"{mx['nr']} {mx['id']}",
                     "Niespełnione": ", ".join(p["id"] + ("*" if p["nr"] in S["zast"] else "") for p in zle) if zle else "—"})
    o.tabela(rows, tytul="Wyniki obliczeń statycznych — zestawienie grup pozycji", klasa="zwarta",
             wyrownanie={"Grupa": "l", "Niespełnione": "l"}, szerokosci=["46mm", "16mm", "16mm", "28mm", None],
             uwagi=["η — maksymalne wykorzystanie nośności / warunku stanu granicznego pozycji (STR, GEO, SLS). "
                    "Szczegóły, warunki i przyjęte zbrojenie — rozdz. 4. * — pozycja ZASTĄPIONA analizą dokładniejszą "
                    "(model ławy izolowanej → MES płyty fundamentowej, rozdz. 1 i 5)."],
             zrodlo="wyniki.json (lamela.obliczenia.konstrukcja)")
    if poz:
        o.wykres(_wykres_eta(poz, grupy, S["zast"]), "Maksymalne wykorzystanie nośności η pozycji obliczeń (czerwone — "
                 "warunki niespełnione, szare — pozycje ZASTĄPIONE; wartości > 200 % opisane liczbą)")
    o.rozdzial("Pomiary przemieszczeń i odkształceń", poziom=2, podstawa="§ 23 pkt 1 RPB; W-274")
    wsp = [p for p in poz if p["nr"].startswith("3.")]
    o.tekst(f"""
    Nie przewiduje się stałego monitoringu geodezyjnego obiektu. Zaleca się kontrolny pomiar ugięć końców płyt
    wspornikowych ({', '.join(p['id'] for p in wsp) or '—'}) po rozdeskowaniu i po wykonaniu warstw wykończeniowych
    (porównanie z ugięciami z obliczeń, rozdz. 4 poz. 3) oraz pomiar osiadań płyty fundamentowej w 4 narożach po
    wykonaniu stanu surowego (porównanie z osiadaniem z MES, rozdz. 5) [ZAŁ].
    """)
    o.rozdzial("Zakres wymagający odrębnych analiz", poziom=2)
    o.tekst("Ograniczenia modeli obliczeniowych biblioteki (do rozstrzygnięcia przez projektanta konstrukcji):\n\n"
            + "\n".join(f"* {t}" for t in D["RAP"].OGRANICZENIA))


def rozdz_obliczenia(o: Opis, D: dict):
    """4. Pełne obliczenia statyczne (dokument biblioteki), 5. MES płyty fundamentowej, 6. kontrola zbrojenia."""
    o.rozdzial("Obliczenia statyczne", podstawa="§ 23 pkt 1 RPB; PN-EN 1990…1997", nowa_strona=True)
    obl = D["obl_md"]
    if not obl:
        o.wniosek(f"Brak pliku obliczeń statycznych — {NZ}.", alarm=True)
    else:
        obl = re.sub(r"\A# [^\n]*\n", "", obl)                          # tytuł dokumentu → rozdział tomu
        o.dokument_md(obl, D["kat_obl"], md_odeslanie=f"*[Pełne obliczenia statyczne — w PDF; źródło: "
                      f"`{rel(D['kat_obl'] / 'obliczenia_statyczne.md')}`]*")
    o.rozdzial("Płyta fundamentowa — analiza MES na podłożu sprężystym", podstawa="PN-EN 1992-1-1; PN-EN 1997-1",
               nowa_strona=True)
    if D["mes_md"]:
        o.dokument_md(re.sub(r"\A# [^\n]*\n", "", D["mes_md"]), KAT_OBL,
                      md_odeslanie=f"*[Raport MES — w PDF; źródło: `{rel(KAT_OBL / 'plyta_fundamentowa_MES.md')}`]*")
    else:
        o.wniosek(f"Brak raportu MES płyty fundamentowej — {NZ}.", alarm=True)
    o.rozdzial("Kontrola zbrojenia rysunków", podstawa="PN-EN 1992-1-1 9.2.1.1, 9.3.1.1; RPB § 24 pkt 1",
               nowa_strona=True)
    if D["kz_md"]:
        o.dokument_md(re.sub(r"\A# [^\n]*\n", "", D["kz_md"]), KAT_RYS,
                      md_odeslanie=f"*[Kontrola zbrojenia — w PDF; źródło: `{rel(KAT_RYS / 'kontrola_zbrojenia.md')}`]*")
    else:
        o.wniosek(f"Brak raportu kontroli zbrojenia rysunków — {NZ}.", alarm=True)


def _odl_sasiadow(D: dict):
    """Najmniejsza odległość obrysu płyty fundamentowej od zabudowy działek sąsiednich [m] (prostokąty obwiedni)."""
    dz, fund = D["dz"], D["bud"].get("fundamenty", {}).get("elementy", [])
    dx, dy = (dz.get("uklad") or {}).get("przesuniecie", [0.0, 0.0])
    pts = [(x + dx, y + dy) for e in fund if "obrys" in e for x, y in e["obrys"]]
    if not pts:
        return None, None
    bx0, bx1 = min(p[0] for p in pts), max(p[0] for p in pts)
    by0, by1 = min(p[1] for p in pts), max(p[1] for p in pts)
    best = (None, None)
    for s in dz.get("sasiedzi", []):
        z = s.get("zabudowa") or []
        if not z:
            continue
        zx0, zx1 = min(p[0] for p in z), max(p[0] for p in z)
        zy0, zy1 = min(p[1] for p in z), max(p[1] for p in z)
        d = (max(0.0, zx0 - bx1, bx0 - zx1) ** 2 + max(0.0, zy0 - by1, by0 - zy1) ** 2) ** 0.5
        if best[0] is None or d < best[0]:
            best = (d, s.get("nr"))
    return best


def rozdz_geotechnika(o: Opis, D: dict):
    """7. Geotechniczne warunki i sposób posadowienia (§ 23 pkt 2–3 RPB; rozp. Dz.U. 2012 poz. 463 § 7, § 9, § 10)."""
    b, p, mes = D["bud"], D["p"], D["mes_md"] or ""
    geo, fund = b.get("geotechnika", {}), b.get("fundamenty", {})
    gr = geo.get("grunt", {})
    tr = D["dz"].get("teren", {})
    gr_opis = str(tr.get("grunt", "—")).rstrip(". ")
    H = [pt[2] for pt in tr.get("punkty", [])]
    zero = b.get("uklad", {}).get("zero_abs")
    spody = [e["spod"] for e in fund.get("elementy", []) if "spod" in e]
    iz = fund.get("izolacja_obwodowa", {})
    o.rozdzial("Geotechniczne warunki i sposób posadowienia", podstawa="§ 23 pkt 2 RPB; Dz.U. 2012 poz. 463 § 7 ust. 2",
               nowa_strona=True)
    o.wniosek(f"Dane gruntowe są **{FIKCJA}** (brief; rejestr E-04, W-282). Przed wydaniem PT wymagane są "
              "dokumentacja badań podłoża gruntowego i projekt geotechniczny sporządzone na podstawie badań polowych "
              "(CPT/DPL) — do tego czasu wyniki nośności i osiadania są ilustracyjne.", alarm=True)
    o.tekst(f"""
    Kategoria geotechniczna obiektu: **{geo.get('kategoria', '—')}** ({p.kategoria_geotechniczna} w obliczeniach;
    W-280, rejestr D-08) — zgodnie z § 7 ust. 2 rozporządzenia (Dz.U. 2012 poz. 463) opracowuje się dodatkowo
    dokumentację badań podłoża gruntowego i projekt geotechniczny. Warunki gruntowe proste — dokumentacji
    geologiczno-inżynierskiej (§ 7 ust. 3) nie sporządza się (§ 23 pkt 3 RPB — nie dotyczy). Opinia geotechniczna
    (§ 7 ust. 1, § 8) — w projekcie architektoniczno-budowlanym (PAB). Zakres badań: {geo.get('uwagi', '—')}.
    """)
    o.rozdzial("Dokumentacja badań podłoża gruntowego", poziom=2, podstawa="Dz.U. 2012 poz. 463 § 9")
    o.tekst(f"""
    Rozpoznanie przyjęte do projektu {FIKCJA}: {gr_opis}. Teren istniejący w obrysie działki:
    rzędne {L(min(H)) if H else '—'}…{L(max(H)) if H else '—'} m n.p.m.; poziom ±0,000 = {L(zero, 2)} m n.p.m.;
    zwierciadło wody gruntowej ≈ {L(abs(geo.get('ZWG', 0)), 1)} m p.p.t. (rzędna {L(tr.get('ZWG'), 2)} m n.p.m.).
    Dokumentacja badań (opis metodyki badań polowych i laboratoryjnych, wyniki, interpretacja, model geologiczny,
    wartości wyprowadzone dla każdej warstwy) — {dok_zewn('dokumentacja badań podłoża gruntowego, geotechnik z uprawnieniami (E-04)')}.
    """)
    o.rozdzial("Projekt geotechniczny", poziom=2, podstawa="Dz.U. 2012 poz. 463 § 10 pkt 1–10")
    m0_mes = re.search(r"E_s = M₀[^=]*= ([\d ]+)·\(1\+([\d,]+)\)", mes)
    mes_war = [r for t in tabele_md(mes) for r in t if "Stan" in r]
    # parametry MES z pierwszej listy „Parametry podłoża …: φ'_k; c'_k; γ = **φ; c; γ — opis**”
    par_mes = [x.strip() for x in (wartosc_md(mes, "Parametry podłoża") or "").split("—")[0].split(";")]
    par_mes += [""] * (3 - len(par_mes))
    id_obl = re.search(r"I_D\s*≈\s*([\d,]+)", p.grunt.nazwa)
    id_mes = re.search(r"I_D\s*≈\s*([\d,]+)", wartosc_md(mes, "Parametry podłoża") or "")
    o.tekst(f"""
    ### Prognoza zmian właściwości podłoża w czasie {{podstawa: § 10 pkt 1}}
    Piaski średnie niewysadzinowe, ZWG ok. {L(abs(geo.get('ZWG', 0)), 1)} m p.p.t. — poniżej strefy wpływu
    fundamentu płytkiego; istotnych zmian właściwości w czasie nie przewiduje się pod warunkiem ochrony dna wykopu
    przed rozluźnieniem, rozmoczeniem i przemarzaniem w czasie robót oraz wykonania izolacji obwodowej
    ({iz.get('opis', '—')}).

    ### Obliczeniowe parametry geotechniczne {{podstawa: § 10 pkt 2}}
    Podejście obliczeniowe DA2* (PN-EN 1997-1 + NA): parametry materiałowe M1 (γ_φ' = γ_c' = γ_γ = 1,0) — wartości
    obliczeniowe równe charakterystycznym z tabeli poniżej (kolumna „Model”).
    """)
    rozbiezne = [w for w in kontrole_spojnosci(D) if w["obszar"] == "Projekt geotechniczny"]
    o.tabela([
        {"Parametr (wartość charakterystyczna)": "rodzaj gruntu nośnego", "Model (geotechnika)": gr.get("rodzaj", "—"),
         "Obliczenia statyczne": p.grunt.nazwa, "MES płyty": "jw. (M1)"},
        {"Parametr (wartość charakterystyczna)": "stopień zagęszczenia I_D", "Model (geotechnika)": L(gr.get("I_D")),
         "Obliczenia statyczne": f"≈ {id_obl.group(1)} (opis gruntu)" if id_obl else "—",
         "MES płyty": f"≈ {id_mes.group(1)} (opis gruntu)" if id_mes else "—"},
        {"Parametr (wartość charakterystyczna)": "kąt tarcia wewnętrznego φ'_k [°]", "Model (geotechnika)": L(gr.get("phi"), 1),
         "Obliczenia statyczne": L(p.grunt.fi_k, 1), "MES płyty": par_mes[0].rstrip("°") or "—"},
        {"Parametr (wartość charakterystyczna)": "ciężar objętościowy γ [kN/m³]", "Model (geotechnika)": L(gr.get("gamma"), 1),
         "Obliczenia statyczne": L(p.grunt.gamma, 1), "MES płyty": par_mes[2].replace("kN/m³", "").strip() or "—"},
        {"Parametr (wartość charakterystyczna)": "moduł edometryczny M₀ [kPa]", "Model (geotechnika)": L(gr.get("M0"), 0),
         "Obliczenia statyczne": L(p.grunt.M0, 0), "MES płyty": L(_f(m0_mes.group(1)), 0) if m0_mes else "—"},
        {"Parametr (wartość charakterystyczna)": "ZWG [m p.p.t.]", "Model (geotechnika)": L(abs(geo.get("ZWG", 0)), 1),
         "Obliczenia statyczne": L(p.grunt.ZWG, 1), "MES płyty": "γ' pod fundamentem" if "γ'" in mes else "—"},
    ], tytul=f"Parametry geotechniczne podłoża {FIKCJA}", klasa="zwarta",
        wyrownanie={"Parametr (wartość charakterystyczna)": "l", "Model (geotechnika)": "l", "Obliczenia statyczne": "l"},
        uwagi=["Źródłem parametrów projektu geotechnicznego jest model geotechniczny (kolumna „Model”). Rozbieżność "
               "w innej kolumnie oznacza obliczenia do powtórzenia na parametrach modelu — pozycja "
               f"„Projekt geotechniczny” w rozdz. 1 (stan: {'brak rozbieżności' if not rozbiezne else NZ}). "
               "W II kat. geotechnicznej korelacje PN-81/B-03020 niedopuszczalne (W-282)."],
        zrodlo="model budynku (geotechnika); parametry obliczeń; raport MES płyty fundamentowej")
    o.tekst(f"""

    ### Częściowe współczynniki bezpieczeństwa {{podstawa: § 10 pkt 3}}
    A1: γ_G = {L(p.gG_sup)} (ξ = {L(p.xi)}), γ_Q = {L(p.gQ)}; M1: 1,0; R2: γ_R;v = {L(p.gR_v, 1)}, γ_R;h = {L(p.gR_h, 1)}
    (PN-EN 1997-1 NA.2.6, W-283).

    ### Oddziaływania od gruntu {{podstawa: § 10 pkt 4}}
    Budynek niepodpiwniczony — parcie gruntu na ściany nie występuje. Nadkład w poziomie posadowienia:
    q' = {wartosc_md(mes, 'Naprężenie od nadkładu') or '—'} kPa; wypór wody nie występuje (ZWG poniżej posadowienia).

    ### Model obliczeniowy podłoża {{podstawa: § 10 pkt 5}}
    Projektowy przekrój geotechniczny: {gr_opis}. Model Winklera płyty fundamentowej:
    k_s = {wartosc_md(mes, 'Współczynnik podatności') or '—'} kN/m³, obwiednia wariantów k_s,min; k_s,max =
    {wartosc_md(mes, 'Obwiednia wariantów') or '—'} kN/m³ (rozdz. 5).
    """)
    o.tabela([{"Warunek": r.get("Warunek"), "Efekt": r.get("Efekt"), "Nośność / limit": r.get("Nośność / limit"),
               "η": r.get("η"), "Stan": r.get("Stan", "").strip("*") if "NIESPEŁ" not in r.get("Stan", "").upper()
               else f"NIESPEŁNIONY — {NZ}"} for r in mes_war
              if re.search(r"podłoż|osiadan|odryw", r.get("Warunek", ""), re.I)]
             or [{"Warunek": "—", "Efekt": "—", "Nośność / limit": "—", "η": "—", "Stan": f"brak raportu MES — {NZ}"}],
             tytul="Nośność i osiadanie podłoża (§ 10 pkt 6) — wyniki MES płyty fundamentowej", klasa="zwarta",
             wyrownanie={"Warunek": "l"}, szerokosci=[None, "34mm", "34mm", "12mm", "32mm"],
             uwagi=["Stateczność ogólna: teren płaski "
                    f"(spadek {L((max(H) - min(H)), 2) if H else '—'} m na obszarze działki), brak skarp i wykopów "
                    "głębokich — sprawdzenie stateczności ogólnej nie jest miarodajne [ZAŁ]."],
             zrodlo="plyta_fundamentowa_MES.md")
    d_s, nr_s = _odl_sasiadow(D)
    o.tekst(f"""
    ### Dane do zaprojektowania fundamentów {{podstawa: § 10 pkt 7}}
    Posadowienie bezpośrednie: płyta fundamentowa z żebrami, spód elementów na rzędnych {L(max(spody), 2)}…
    {L(min(spody), 2)} m (względem ±0,000); usunięcie ziemi urodzajnej {L(geo.get('humus'), 1)} m; strefa przemarzania
    h_z = {L(geo.get('h_z'), 1)} m — ochrona izolacją obwodową (W-284); osiadanie dopuszczalne
    s ≤ {L(p.s_max_mm, 0)} mm (W-283).

    ### Specyfikacja badań kontrolnych robót ziemnych {{podstawa: § 10 pkt 8}}
    Odbiór dna wykopu przez geotechnika (zgodność gruntu z dokumentacją badań); kontrola zagęszczenia podsypki pod
    płytą (wskaźnik zagęszczenia lub moduł odkształcenia — wartości wymagane wg dokumentacji badań podłoża, rozdz. 7.1);
    kontrola grubości i ciągłości izolacji XPS pod płytą.

    ### Wody gruntowe {{podstawa: § 10 pkt 9}}
    ZWG ≈ {L(abs(geo.get('ZWG', 0)), 1)} m p.p.t. — poniżej poziomu posadowienia; odwodnienie wykopu i drenaż
    opaskowy zbędne (W-285); agresywność wód gruntowych względem betonu — wg dokumentacji badań podłoża (rozdz. 7.1).

    ### Monitorowanie {{podstawa: § 10 pkt 10}}
    Pomiar osiadań płyty (rozdz. 3). Najbliższa zabudowa sąsiednia (dz. {nr_s or '—'}) w odległości
    ≈ {L(d_s, 1)} m od płyty fundamentowej {FIKCJA}; przy wykopie płytkim (spód fundamentów ≤ {L(abs(min(spody)), 2)} m poniżej ±0,000)
    monitoring obiektów sąsiednich nie jest wymagany [ZAŁ].
    """)
    o.rozdzial("Wpływy eksploatacji górniczej", poziom=2, podstawa="§ 23 pkt 2 RPB")
    o.tekst(f"Nie dotyczy — działka poza terenem górniczym {FIKCJA}.")


def rozdz_ppoz(o: Opis, D: dict):
    """8. Dane dotyczące warunków ochrony przeciwpożarowej stosownie do zakresu PT-BO (§ 23 pkt 10 RPB)."""
    from lamela.obliczenia.wspolne import wymaganie
    zl, gw, zw = (wymaganie("ppoz", k) for k in ("kategoria_ZL", "grupa_wysokosci", "zwolnienie_213_kondygnacje_max"))
    n_k = len(D["bud"].get("kondygnacje", []))
    spelnia = n_k <= zw.wartosc
    o.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", podstawa="§ 23 pkt 10 RPB", nowa_strona=True)
    o.tekst(f"""
    Budynek mieszkalny jednorodzinny wolnostojący: kategoria zagrożenia ludzi **{zl.wartosc}** ({zl.zrodlo}; {zl.id}),
    grupa wysokości **{gw.wartosc}** ({gw.zrodlo}), {n_k} kondygnacje nadziemne. Budynek
    {'spełnia' if spelnia else '**NIE SPEŁNIA**'} warunek zwolnienia z wymagań klasy odporności pożarowej
    (≤ {zw.wartosc} kondygnacje nadziemne — {zw.zrodlo}; {zw.id}) — dla elementów konstrukcji (główna konstrukcja
    nośna, stropy, ściany) przepisy {'nie stawiają' if spelnia else 'stawiają'} wymagań klas odporności ogniowej
    R/REI; na rysunkach PT-BO klas odporności ogniowej nie podaje się (RPB § 9 ust. 2; W-219).

    Rozwiązania konstrukcyjno-materiałowe: żelbet, mur z bloczków silikatowych i stal konstrukcyjna — wyroby
    niepalne. Słupy stalowe fasady i łączniki termoizolacyjne wsporników — bez wymagań odporności ogniowej
    (zwolnienie jw.); przejścia instalacyjne przez stropy — wg PT-3 IS i PT-4 IE. Dane ppoż. zagospodarowania
    (droga pożarowa, zaopatrzenie w wodę do zewnętrznego gaszenia pożaru) — PZT i PAB.
    """)


def rozdz_braki(o: Opis, D: dict, ark_info: list[str]):
    """9. Dane do uzupełnienia i uzgodnienia międzybranżowe (z BRAKI_DANYCH.md zespołu BO)."""
    o.rozdzial("Dane do uzupełnienia i uzgodnienia międzybranżowe", podstawa="W-272, W-286, E-04")
    lst = sekcja_md(D["braki_md"], "Dane do uzupełnienia")
    o.tekst(lst or "Brak zgłoszonych braków danych (BRAKI_DANYCH.md).")
    o.tekst("Wyroby wskazane z nazwy w dokumentacji zespołu BO należy traktować jako przykładowe — dopuszcza się "
            "wyroby równoważne spełniające parametry wymagane (nośność, klasa, deklaracja właściwości użytkowych, "
            "ETA/EAD dla łączników termoizolacyjnych).")
    if ark_info:
        o.tekst("Uwagi kontroli jakości arkuszy (AUD-RYS):\n\n" + "\n".join(f"* {u}" for u in ark_info))


def _tekst_pdf(pdf: Path) -> str:
    import pymupdf
    with pymupdf.open(str(pdf)) as doc:
        return " ".join(pg.get_text() for pg in doc)


def arkusze_bo(bez: bool = False) -> tuple[list[Arkusz], list[str], list[str]]:
    """Arkusze PT-BO z ``raport_widokow.json`` (+ arkusze konfiguracji ``model/arkusze_bo.yaml`` bez wpisu w raporcie).
    Zwraca (arkusze, braki → NIEZAMKNIĘTE „NR: opis”, uwagi informacyjne). Uwagi kontroli jakości z raportu widoków
    przypisuje do arkusza tylko przy zgodnym numerze i tytule — pozostałe (nieaktualne) zgłasza zbiorczo."""
    rap = _czytaj(KAT_RYS / "raport_widokow.json") or {"arkusze": []}
    cfg = yaml.safe_load((REPO / "model/arkusze_bo.yaml").read_text(encoding="utf-8")) or {}
    ark, braki, info = [], [], []
    w_rap = {a["nr"] for a in rap.get("arkusze", [])}
    lista = list(rap.get("arkusze", [])) + [dict(nr=c["nr"], tytul=c["tytul"], skala=f"1:{c.get('skala', 50)}",
                                                 pliki={"pdf": ""}) for c in cfg.get("arkusze", []) if c["nr"] not in w_rap]
    nst, normy_wycof = [], []
    for a in lista:
        pdf = Path(a["pliki"].get("pdf") or "")
        pdf = pdf if pdf.is_absolute() else REPO / pdf
        if bez or not a["pliki"].get("pdf") or not pdf.exists():
            ark.append(Arkusz.planowany(a["nr"], a["tytul"], a.get("skala") or "—", a.get("format") or "A3"))
            if not bez:
                braki.append(f"{a['nr']}: brak pliku PDF arkusza „{a['tytul']}” — strona zastępcza")
            continue
        if not a.get("qa", {}).get("ok", True):
            braki.append(f"{a['nr']}: kontrola jakości arkusza z błędami: {a['qa'].get('errors')}")
        ar = Arkusz.z_pdf(pdf)
        ark.append(ar)
        if str(ar.format or "").startswith("nst."):
            nst.append(f"{ar.nr} ({ar.wymiar_tekst()})")
        t = _tekst_pdf(pdf)
        if re.search(r"PN-EN\s*206\+A2|PN-B-06265", t) and not re.search(r"wycofan", t, re.I):
            normy_wycof.append(ar.nr)
    # uwagi QA raportu widoków: „NR TYTUŁ: problem” — aktualne tylko przy zgodnym numerze i tytule arkusza
    tyt = {a.nr: a.tytul for a in ark}
    stare, kolizje = [], OrderedDict()
    for pr in (x.strip() for x in rap.get("problemy", [])):
        m = re.match(r"^(PT-BO-\d+)\s+(.*?):\s*(.*)$", pr)
        if m and tyt.get(m.group(1)) == m.group(2).strip():
            kolizje.setdefault(m.group(1), []).append(m.group(3))
        else:
            stare.append(m.group(1) if m else pr.split(":")[0].strip()[:40])
    for nr, lst in kolizje.items():
        braki.append(f"{nr}: {'; '.join(lst)} — usunąć przed wydaniem (kontrola jakości arkusza)")
    if stare:
        braki.append(f"Raport kontroli arkuszy: {len(stare)} {odmiana(len(stare), 'uwaga', 'uwagi', 'uwag')} dotyczy "
                     f"numerów lub tytułów niezgodnych z wykazem rysunków ({', '.join(sorted(set(stare))[:8])}) — raport "
                     "nieaktualny; wygenerować ponownie arkusze konstrukcji wraz z raportem kontroli")
    if nst:
        braki.append(f"Formaty arkuszy: {len(nst)} {odmiana(len(nst), 'arkusz', 'arkusze', 'arkuszy')} w formacie "
                     f"niestandardowym ({', '.join(nst)}) — dobrać format z szeregu PN-EN ISO 5457 (A0–A4, formaty "
                     "wydłużone; W-313)")
    if normy_wycof:
        braki.append(f"Uwagi na arkuszach: {', '.join(normy_wycof)} — specyfikacja betonu powołuje PN-EN 206+A2 "
                     "i PN-B-06265 bez statusu (normy wycofane, rejestr D-09) — ujednolicić z rozdz. 2.2")
    return ark, braki, info


# ============================================================================================ złożenie
def buduj_pt_bo(d: dict, D: dict, S: dict, ark: list, ark_braki: list, ark_info: list, data: str) -> tuple:
    nz = S["n_nz"] + len(ark_braki)
    podt = "Tom PT-2 — konstrukcja (BO): opis, obliczenia statyczne, projekt geotechniczny, rysunki konstrukcyjne"
    if nz:
        podt += f" · ANALIZY {NZ}: {nz} {odmiana(nz, 'pozycja', 'pozycje', 'pozycji')} (rozdz. 1)"
    dok = Dokument("Projekt techniczny", "PT-BO", d, kod="PT-2 BO", branza="konstrukcja (konstrukcyjno-budowlana)",
                   data=data, tom=(PT_NR, PT_TOMY), podtytul=podt)
    dok.oswiadczenie_projektanta()
    o = Opis(dok)
    o.md += [f"# Projekt techniczny — PT-2 BO (konstrukcja) — tom {PT_NR} z {PT_TOMY}",
             "*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_BO.py`; wersja wiążąca: PDF. "
             "Obliczenia statyczne, raport MES i kontrola zbrojenia — w PDF (pliki źródłowe zespołu BO).*",
             "*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny "
             "`lamela.dokumenty`; pełna treść w PDF]*"]
    o.czesc("Opis techniczny — konstrukcja", podstawa="§ 23 RPB")
    rozdz_stan(o, D, S, ark_braki)
    rozdz_podstawa(o, D)
    rozdz_konstrukcja(o, D)
    rozdz_wyniki(o, D, S)
    rozdz_obliczenia(o, D)
    rozdz_geotechnika(o, D)
    rozdz_ppoz(o, D)
    rozdz_braki(o, D, ark_info)
    dok.czesc_rysunkowa(ark, podstawa="§ 24 pkt 1 RPB; § 7 ust. 1 pkt 4, § 10 RPB")
    o.md.append("## Część rysunkowa — wykaz rysunków\n\n| Nr | Tytuł | Skala | Format | Uwagi |\n|---|---|---|---|---|\n"
                + "\n".join(f"| {a.nr} | {a.tytul} | {a.skala or '—'} | {a.format or '—'} | "
                            f"{'' if a.istnieje else 'brak pliku — strona zastępcza'} |" for a in dok.arkusze))
    return dok, o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(KAT_WYDANIE))
    ap.add_argument("--przelicz", action="store_true", help="uruchom ponownie obliczenia statyczne z modelu")
    ap.add_argument("--bez-arkuszy", action="store_true", help="arkusze jako strony zastępcze (szybki podgląd)")
    a = ap.parse_args(argv)
    t0 = time.time()
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    KAT_ZRODLA.mkdir(parents=True, exist_ok=True)
    d = dane_obiektu()
    data = d.get("data")
    D = wczytaj_dane(a.przelicz)
    S = stan_analiz(D)
    ark, ark_braki, ark_info = arkusze_bo(a.bez_arkuszy)
    print(f"dane: {time.time() - t0:.1f} s; arkusze {len(ark)} (brak {len(ark_braki)}); {NZ}: {S['n_nz']}")
    dok, o = buduj_pt_bo(d, D, S, ark, ark_braki, ark_info, data)
    o.zapisz(KAT_ZRODLA / "PT_BO_opis.md")
    (KAT_ZRODLA / "stan_analiz.json").write_text(json.dumps(dict(
        model=D["t_modelu"], obszary={k: list(v) for k, v in S["obszary"].items()}, niezamkniete=S["n_nz"] + len(ark_braki),
        wiersze=S["wiersze"], arkusze_braki=ark_braki), ensure_ascii=False, indent=1), encoding="utf-8")
    tom = Tom("PT-2 BO", [dok], dane=d, data=data, nr=PT_NR, symbol="BO", strona_tytulowa=False, laczny_spis=False)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB ({time.time() - t0:.0f} s)")
    r = sprawdz_tom(w, LISTY_KONTROLNE["PT_BO"])
    (KAT_ZRODLA / f"raport_kompletnosci_{w.sciezka.stem}.txt").write_text(r.tekst(), encoding="utf-8")
    r.zapisz_json(KAT_ZRODLA / f"raport_kompletnosci_{w.sciezka.stem}.json")
    s = r.podsumowanie()
    print(f"  walidator: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
          f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}")
    for p in r.braki:
        print(f"    ✗ {p.id} [{p.element}] {p.opis} — {p.szczegoly}")
    zamknij_przegladarke()
    return w, r, S


if __name__ == "__main__":
    main()
