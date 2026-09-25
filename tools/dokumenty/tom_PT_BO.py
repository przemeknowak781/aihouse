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
                          stan="ZASTĄPIONE", opis=f"model ławy izolowanej ({opis}) — miarodajna analiza MES płyty "
                          "fundamentowej (rozdz. 5); głębokość posadowienia — płyta na XPS z izolacją obwodową (W-284)",
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
    return dict(wiersze=W, obszary=ok_obszary, n_nz=sum(w["stan"] == NZ for w in W))


# ============================================================================================ rozdziały
def rozdz_stan(o: Opis, D: dict, S: dict, ark_uwagi: list[str]):
    """1. Stan opracowania — analizy zamknięte / NIEZAMKNIĘTE (jawnie, aktualizowane z wyników BO)."""
    o.rozdzial("Stan opracowania i analiz konstrukcji", podstawa="§ 23 pkt 1 RPB; W-274")
    nz = S["n_nz"] + len(ark_uwagi)
    o.tekst(f"""
    Zestawienie generowane automatycznie przy każdym złożeniu tomu z wyników obliczeń zespołu BO (model
    `model/budynek.yaml` z {D['t_modelu']}). Pozycja **{NZ}** oznacza analizę nie domkniętą: niespełniony warunek
    stanu granicznego, wymagane obliczeniowo zbrojenie nieujęte w kontroli rysunków, uwagę biblioteki
    „[WYMAGA ANALIZY]” albo brak arkusza rysunkowego. Pozycja **ZASTĄPIONE** — wynik modelu uproszczonego zastąpiony
    analizą dokładniejszą (wskazaną w opisie). Po domknięciu analiz i ponownym uruchomieniu generatora wiersze
    znikają z zestawienia.
    """)
    if nz:
        o.wniosek(f"**PROJEKT KONSTRUKCJI NIEZAMKNIĘTY — {nz} {'pozycja' if nz == 1 else 'pozycji'} {NZ}.** "
                  "Tom nie może być przekazany kierownikowi budowy (art. 42 ust. 1 PB) ani objęty oświadczeniem "
                  "projektanta z art. 41 ust. 4a pkt 2 PB przed domknięciem wszystkich pozycji z tabeli poniżej.",
                  alarm=True)
    else:
        o.wniosek("Wszystkie analizy konstrukcji objęte zestawieniem są domknięte (brak pozycji NIEZAMKNIĘTYCH).")
    ob = [{"Obszar analizy": k, "Warunki spełnione": f"{a} z {b}", "Stan": "zamknięte" if a == b else NZ}
          for k, (a, b) in S["obszary"].items()]
    ob.append({"Obszar analizy": "Część rysunkowa (arkusze z raport_widokow.json)",
               "Warunki spełnione": "komplet" if not ark_uwagi else f"brak {len(ark_uwagi)}",
               "Stan": "zamknięte" if not ark_uwagi else NZ})
    o.tabela(ob, tytul="Stan analiz według obszarów", wyrownanie={"Obszar analizy": "l"},
             szerokosci=[None, "40mm", "34mm"], zrodlo="wyniki.json, plyta_fundamentowa_MES.md, kontrola_zbrojenia.json")
    kol = ("Obszar", "Element", "Wynik", "Opis", "Źródło")
    rows = [dict(zip(kol, (w["obszar"], w["element"], w["wynik"], w["opis"], w["zrodlo"])))
            for w in S["wiersze"] if w["stan"] == NZ]
    rows += [dict(zip(kol, ("Część rysunkowa", u.split(":")[0], "—", u.split(":", 1)[-1].strip(), "raport_widokow.json")))
             for u in ark_uwagi]
    if rows:
        o.tabela(rows, tytul=f"Pozycje {NZ} (do domknięcia przez zespół BO przed wydaniem PT)", klasa="zwarta",
                 lp=True, wyrownanie={"Opis": "l", "Element": "l"}, szerokosci=["24mm", "30mm", "20mm", None, "30mm"])
    zast = [dict(zip(("Element", "Wynik modelu uproszczonego", "Opis"), (w["element"], w["wynik"], w["opis"])))
            for w in S["wiersze"] if w["stan"] == "ZASTĄPIONE"]
    if zast:
        o.tabela(zast, tytul="Pozycje ZASTĄPIONE analizą dokładniejszą", klasa="zwarta", wyrownanie={"Opis": "l"},
                 szerokosci=["26mm", "26mm", None], zrodlo="BRAKI_DANYCH.md (zespół BO)")


def rozdz_podstawa(o: Opis, D: dict):
    """2. Podstawa opracowania: przepisy, normy (z biblioteki obliczeń), dane wejściowe z datami."""
    o.rozdzial("Podstawa opracowania", podstawa="§ 23 pkt 1 RPB")
    meta = D["bud"].get("meta", {})
    o.tekst(f"""
    ## Przepisy
    * ustawa — Prawo budowlane (PB), w szczególności art. 34 ust. 3 pkt 4 (projekt techniczny), art. 41 ust. 4a
      pkt 2 (oświadczenie projektanta PT), art. 102a (stosowanie WT w dotychczasowym brzmieniu);
    * rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego (RPB, Dz.U. 2020 poz. 1609,
      t.j. Dz.U. 2022 poz. 1679 ze zm.) — § 23 pkt 1–3 i 10 (część opisowa PT), § 24 pkt 1 (część rysunkowa);
    * rozporządzenie w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (WT,
      t.j. Dz.U. 2022 poz. 1225 ze zm.) — w brzmieniu stosowanym na podstawie art. 102a PB ({meta.get('uwagi', '—')});
    * rozporządzenie MTBiGM z 25.04.2012 w sprawie ustalania geotechnicznych warunków posadawiania obiektów
      budowlanych (Dz.U. 2012 poz. 463) — § 7 ust. 2 (kat. II: dokumentacja badań podłoża i projekt geotechniczny),
      § 9, § 10.

    ## Normy (Eurokody z załącznikami krajowymi)
    """)
    o.tekst("\n".join(f"* {n}" for n in D["RAP"].NORMY))
    wiersze = [{"Dane wejściowe": "model budynku", "Plik": "model/budynek.yaml",
                "Stan": f"wersja {meta.get('wersja', '—')}, {D['t_modelu']}"}]
    for nazwa, (akt, kiedy) in D["aktualnosc"].items():
        wiersze.append({"Dane wejściowe": nazwa, "Plik": {"obliczenia statyczne": rel(D["kat_obl"] / "wyniki.json"),
                        "MES płyty fundamentowej": rel(KAT_OBL / "plyta_fundamentowa_MES.md"),
                        "kontrola zbrojenia": rel(KAT_RYS / "kontrola_zbrojenia.json")}[nazwa],
                        "Stan": f"{kiedy} — {'aktualne względem modelu' if akt else NZ + ' (nieaktualne)'}"})
    o.tabela(wiersze, tytul="Dane wejściowe tomu (odczyt przy każdym złożeniu)", wyrownanie={"Plik": "l"},
             szerokosci=["40mm", None, "58mm"])
