"""Dane obiektu, działki, inwestora i projektantów do stron tytułowych, metryk i oświadczeń.

Jedno źródło prawdy: ``model/budynek.yaml`` (sekcja ``meta`` i opcjonalna ``projekt``) oraz ``model/dzialka.yaml``
(sekcja ``dzialka``). Gdy plików nie ma (etap koncepcji), dane pochodzą z briefu (``docs/00_brief_projektowy.md``)
i są oznaczone jako przykładowe; dane osobowe są zawsze polami ``[DO UZUPEŁNIENIA: …]`` — nie fabrykujemy
danych osób, numerów uprawnień ani podpisów (brief §7 pkt 4, rejestr W-320, E-11).

Opcjonalne klucze w ``dzialka.yaml → dzialka``: ``adres``, ``gmina``, ``powiat``, ``wojewodztwo``,
``jedn_ewid`` (kod TERYT jednostki ewidencyjnej ``WWPPGG_R`` z nazwą), ``identyfikator`` (pełny identyfikator
działki ewidencyjnej ``WWPPGG_R.OOOO.NR``), ``status`` (``fikcyjne`` | ``przykladowe`` | ``rzeczywiste``).

Opcjonalna sekcja ``projekt`` w ``budynek.yaml``::

    projekt:
      nazwa_zamierzenia: "Budowa budynku …"
      inwestor: {nazwa: "…", adres: "…"}
      pracownia: {nazwa: "…", adres: "…"}
      projektanci:
        - {branza: AR, imie_nazwisko: "…", nr_uprawnien: "…", zakres: "…", elementy: [PZT, PAB, PT-AR]}
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

from .znaczniki import do_uzup, DANE_PRZYKLADOWE, SPRAWDZAJACY_ND

REPO = Path(__file__).resolve().parents[3]

# ------------------------------------------------------------------------------------------------ elementy projektu
# kod → (nazwa na stronie tytułowej, forma w bierniku do oświadczeń, forma w dopełniaczu)
ELEMENTY = {
    "PZT": ("Projekt zagospodarowania działki", "projekt zagospodarowania działki",
            "projektu zagospodarowania działki"),
    "PAB": ("Projekt architektoniczno-budowlany", "projekt architektoniczno-budowlany",
            "projektu architektoniczno-budowlanego"),
    "PT": ("Projekt techniczny", "projekt techniczny", "projektu technicznego"),
    "ZL": ("Załączniki", "załączniki", "załączników"),
    "BIOZ": ("Informacja dotycząca bezpieczeństwa i ochrony zdrowia", "informację BIOZ", "informacji BIOZ"),
    "WN": ("Dokumenty do wniosku o pozwolenie na budowę", "dokumenty do wniosku", "dokumentów do wniosku"),
}

# symbol specjalności (zał. 1 RPB) → (nazwa krótka, pełna specjalność uprawnień, nazwa branży, forma skrócona
# na stronę tytułową)
SPECJALNOSCI = {
    "AR": ("architektoniczna", "architektoniczna do projektowania bez ograniczeń", "architektura",
           "architektoniczna bez ograniczeń"),
    "BO": ("konstrukcyjno-budowlana", "konstrukcyjno-budowlana do projektowania bez ograniczeń", "konstrukcja",
           "konstrukcyjno-budowlana bez ograniczeń"),
    "IS": ("instalacyjna sanitarna",
           "instalacyjna w zakresie sieci, instalacji i urządzeń cieplnych, wentylacyjnych, gazowych, wodociągowych "
           "i kanalizacyjnych do projektowania bez ograniczeń", "instalacje sanitarne",
           "instalacyjna (cieplne, wentylacyjne, gazowe, wod.-kan.) bez ograniczeń"),
    "IE": ("instalacyjna elektryczna",
           "instalacyjna w zakresie sieci, instalacji i urządzeń elektrycznych i elektroenergetycznych "
           "do projektowania bez ograniczeń", "instalacje elektryczne",
           "instalacyjna (elektryczne i elektroenergetyczne) bez ograniczeń"),
    "BT": ("instalacyjna telekomunikacyjna",
           "instalacyjna w zakresie sieci, instalacji i urządzeń telekomunikacyjnych do projektowania bez ograniczeń",
           "instalacje telekomunikacyjne", "instalacyjna (telekomunikacyjne) bez ograniczeń"),
}


@dataclass
class Projektant:
    """Autor części projektu. Pola osobowe domyślnie ``[DO UZUPEŁNIENIA: …]``."""
    branza: str = "AR"
    funkcja: str = "Projektant"
    imie_nazwisko: str = field(default_factory=lambda: do_uzup("imię i nazwisko"))
    nr_uprawnien: str = field(default_factory=lambda: do_uzup("nr uprawnień budowlanych"))
    specjalnosc: str | None = None
    zakres: str = ""
    elementy: tuple = ("PZT", "PAB")
    adres: str = field(default_factory=lambda: do_uzup("adres projektanta"))
    izba: str = field(default_factory=lambda: do_uzup("izba samorządu zawodowego, nr członkowski"))

    def __post_init__(self):
        if not self.specjalnosc:
            self.specjalnosc = SPECJALNOSCI.get(self.branza, ("", self.branza, ""))[1]
        self.elementy = tuple(self.elementy)

    @property
    def specjalnosc_krotka(self) -> str:
        return SPECJALNOSCI.get(self.branza, (self.specjalnosc, "", ""))[0]

    def dotyczy(self, element: str) -> bool:
        """Czy projektant jest autorem (współautorem) elementu ``element`` (np. 'PZT', 'PT-AR', 'BIOZ')."""
        e = element.upper()
        return e in self.elementy or (e.startswith("PT") and "PT" in self.elementy)

    @property
    def specjalnosc_skrot(self) -> str:
        """Forma skrócona na stronę tytułową i metryki (pełna — w oświadczeniach)."""
        s = SPECJALNOSCI.get(self.branza)
        return s[3] if s and self.specjalnosc == s[1] else self.specjalnosc

    def slownik(self) -> dict:
        d = asdict(self)
        d["specjalnosc_krotka"] = self.specjalnosc_krotka
        d["specjalnosc_skrot"] = self.specjalnosc_skrot
        return d


def projektanci_domyslni() -> list[Projektant]:
    """Zespół autorów Domu LAMELA (4 specjalności, uprawnienia bez ograniczeń — rejestr A.1, D-11)."""
    return [
        Projektant("AR", zakres="PZT i PAB — rozwiązania architektoniczne i zagospodarowanie działki; PT-1 AR; "
                                "informacja BIOZ", elementy=("PZT", "PAB", "PT-AR", "ZL", "BIOZ")),
        Projektant("BO", zakres="PAB — rozwiązania konstrukcyjne i sposób posadowienia; PT-2 BO",
                   elementy=("PAB", "PT-BO")),
        Projektant("IS", zakres="PZT — przyłącza wod.-kan., wody opadowe; PAB — wyposażenie instalacyjne, "
                                "źródło ciepła; PT-3 IS; oświadczenie z art. 33 ust. 2 pkt 10 PB",
                   elementy=("PZT", "PAB", "PT-IS", "ZL")),
        Projektant("IE", zakres="PZT — zasilanie nN i teletechnika; PAB — wyposażenie elektryczne; PT-4 IE",
                   elementy=("PZT", "PAB", "PT-IE")),
    ]


# ------------------------------------------------------------------------------------------------------ odczyt YAML
def _czytaj(p: Path) -> dict:
    try:
        with open(p, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        return d if isinstance(d, dict) else {}
    except FileNotFoundError:
        return {}


def _obreb(txt: str) -> tuple[str, str]:
    m = re.match(r"\s*(\d{4})\s*[„\"]?([^”\"]*)[”\"]?\s*$", str(txt))
    return (m.group(1), m.group(2).strip()) if m else ("", str(txt))


def dane_obiektu(katalog_modelu: str | Path | None = None, *, budynek: str = "budynek.yaml",
                 dzialka: str = "dzialka.yaml", przyklad: bool | None = None, **nadpisania) -> dict:
    """Słownik danych do stron tytułowych, metryk, oświadczeń i informacji BIOZ.

    Klucze: ``nazwa_krotka``, ``obiekt``, ``nazwa_zamierzenia``, ``adres``, ``dzialka`` (nr, obreb, obreb_nr,
    obreb_nazwa, jedn_ewid, gmina, powiat, wojewodztwo, identyfikator, pow_m2), ``lokalizacja`` (tekst),
    ``kategoria`` ('I'), ``kategoria_opis``, ``inwestor`` {nazwa, adres}, ``projektanci`` [Projektant],
    ``sprawdzajacy``, ``pracownia`` {nazwa, adres}, ``data``, ``wersja``, ``przyklad`` (bool), ``zrodla`` (list),
    ``status`` (słownik pole → 'model' | 'brief' | 'do_uzupelnienia').

    ``nadpisania`` zastępują dowolny klucz najwyższego poziomu (np. ``inwestor={...}``, ``projektanci=[...]``).
    """
    kat = Path(katalog_modelu) if katalog_modelu else REPO / "model"
    pb, pd = kat / budynek, kat / dzialka
    rb, rd = _czytaj(pb), _czytaj(pd)
    meta = rb.get("meta") or {}
    proj = rb.get("projekt") or meta.get("projekt") or {}
    dz = rd.get("dzialka") or {}
    zrodla, status = [], {}
    if rb:
        zrodla.append(str(pb.relative_to(REPO)) if pb.is_relative_to(REPO) else str(pb))
    if rd:
        zrodla.append(str(pd.relative_to(REPO)) if pd.is_relative_to(REPO) else str(pd))
    if not rb or not rd:
        zrodla.append("docs/00_brief_projektowy.md (wartości domyślne — brak pliku modelu)")

    def z(klucz, wartosc_model, domyslna, zrodlo_dom="brief"):
        if wartosc_model not in (None, ""):
            status[klucz] = "model"
            return wartosc_model
        status[klucz] = zrodlo_dom if "DO UZUPEŁNIENIA" not in str(domyslna) else "do_uzupelnienia"
        return domyslna

    nazwa = z("nazwa_krotka", meta.get("nazwa"), "Dom LAMELA")
    if "LAMELA" not in nazwa.upper() and not rb:
        nazwa = "Dom LAMELA"
    obiekt = z("obiekt", proj.get("obiekt") or meta.get("obiekt"),
               f"Budynek mieszkalny jednorodzinny wolnostojący „{nazwa}”")
    zamierzenie = z("nazwa_zamierzenia", proj.get("nazwa_zamierzenia"),
                    f"Budowa budynku mieszkalnego jednorodzinnego wolnostojącego „{nazwa}” z garażem "
                    "dwustanowiskowym w bryle budynku, wraz z zagospodarowaniem terenu i infrastrukturą towarzyszącą "
                    "(zjazd, dojazd i dojście, miejsca postojowe, zbiornik retencyjny wód opadowych, ogrodzenie)")

    nr = z("dzialka.nr", dz.get("nr"), "123/4")
    obreb_txt = z("dzialka.obreb", dz.get("obreb"), "0005 Przykładowo")
    obreb_nr, obreb_nazwa = _obreb(obreb_txt)
    gmina = z("dzialka.gmina", dz.get("gmina"), "Przykładowo")
    powiat = z("dzialka.powiat", dz.get("powiat"), do_uzup("powiat"))
    woj = z("dzialka.wojewodztwo", dz.get("wojewodztwo"), "wielkopolskie")
    jedn = z("dzialka.jedn_ewid", dz.get("jedn_ewid") or dz.get("jednostka"),
             do_uzup("jednostka ewidencyjna — kod TERYT WWPPGG_R i nazwa"))
    kod = None
    m = re.search(r"\b(\d{6}_\d)\b", str(jedn))
    if m:
        kod = m.group(1)
    ident = dz.get("identyfikator")
    if ident:
        status["dzialka.identyfikator"] = "model"
    else:
        ident = f"{kod or do_uzup('kod TERYT jedn. ewid. WWPPGG_R')}.{obreb_nr or '[obręb]'}.{nr}"
        status["dzialka.identyfikator"] = "brief" if kod else "do_uzupelnienia"
    pow_m2 = z("dzialka.pow_m2", dz.get("pow"), 1600.0)
    adres = z("adres", dz.get("adres") or proj.get("adres"),
              f"ul. Lipowa (bez nr porządkowego), gm. {gmina}, woj. {woj}")
    fikcyjne = str(dz.get("status", "fikcyjne" if not rd else "")).lower() in ("fikcyjne", "przykladowe", "")
    if not rd:
        fikcyjne = True
    lokalizacja = (f"działka ewid. nr {nr}, obręb {obreb_nr} „{obreb_nazwa}”, gm. {gmina}"
                   if obreb_nazwa else f"działka ewid. nr {nr}, obręb {obreb_txt}, gm. {gmina}")

    inw = proj.get("inwestor") or {}
    inwestor = {"nazwa": z("inwestor.nazwa", inw.get("nazwa"), do_uzup("imię i nazwisko lub nazwa inwestora")),
                "adres": z("inwestor.adres", inw.get("adres"), do_uzup("adres inwestora"))}
    prac = proj.get("pracownia") or {}
    pracownia = {"nazwa": z("pracownia.nazwa", prac.get("nazwa"), do_uzup("nazwa pracowni projektowej")),
                 "adres": z("pracownia.adres", prac.get("adres"), do_uzup("adres pracowni"))}
    if proj.get("projektanci"):
        projektanci = [p if isinstance(p, Projektant) else Projektant(**p) for p in proj["projektanci"]]
        status["projektanci"] = "model"
    else:
        projektanci = projektanci_domyslni()
        status["projektanci"] = "do_uzupelnienia"

    kat_I = "I"
    try:
        wym = _czytaj(REPO / "docs/10_podstawy_prawne/wymagania.yaml")
        kat_I = str(wym["procedura"]["kategoria_obiektu"]["wartosc"])
    except Exception:
        pass

    wynik = {
        "nazwa_krotka": nazwa,
        "obiekt": obiekt,
        "nazwa_zamierzenia": zamierzenie,
        "adres": adres + (f" {DANE_PRZYKLADOWE}" if fikcyjne and "PRZYKŁADOWE" not in adres else ""),
        "dzialka": {"nr": nr, "obreb": obreb_txt, "obreb_nr": obreb_nr, "obreb_nazwa": obreb_nazwa,
                    "jedn_ewid": jedn, "gmina": gmina, "powiat": powiat, "wojewodztwo": woj,
                    "identyfikator": ident, "pow_m2": pow_m2, "fikcyjna": fikcyjne},
        "lokalizacja": lokalizacja,
        "kategoria": kat_I,
        "kategoria_opis": f"kategoria {kat_I} – budynki mieszkalne jednorodzinne "
                          "(załącznik do ustawy – Prawo budowlane)",
        "inwestor": inwestor,
        "projektanci": projektanci,
        "sprawdzajacy": SPRAWDZAJACY_ND,
        "pracownia": pracownia,
        "data": str(meta.get("data") or "2026-09-25"),
        "wersja": str(meta.get("wersja") or "0"),
        "przyklad": True if przyklad is None else bool(przyklad),
        "zrodla": zrodla,
        "status": status,
    }
    if przyklad is None:
        wynik["przyklad"] = fikcyjne or any(v == "do_uzupelnienia" for v in status.values())
    wynik.update(nadpisania)
    return wynik


def projektanci_elementu(dane: dict, element: str) -> list[Projektant]:
    return [p for p in dane.get("projektanci", []) if p.dotyczy(element)]


# ------------------------------------------------------------------------------------------------ stan modelu
PLIKI_MODELU = ("budynek.yaml", "dzialka.yaml", "instalacje.yaml", "wyposazenie.yaml")
RE_STAN_MODELU = re.compile(r"stan modelu:?\s*SHA-256\s+([0-9a-f]{12})", re.I)


def stan_modelu(katalog_modelu: str | Path | None = None) -> dict:
    """Skrót SHA-256 (12 znaków) plików danych modelu (``PLIKI_MODELU``) — wspólny znacznik stanu modelu,
    wpisywany do każdego tomu i sprawdzany przez walidator (weryfikacja PT, K-1: tomy z jednego stanu modelu).
    Zwraca {skrot, pliki, tekst} — ``tekst``: „stan modelu: SHA-256 1a2b3c4d5e6f (budynek, dzialka, …)”."""
    import hashlib
    kat = Path(katalog_modelu) if katalog_modelu else REPO / "model"
    h = hashlib.sha256()
    pliki = []
    for n in PLIKI_MODELU:
        p = kat / n
        if p.exists():
            h.update(n.encode() + b"\0" + p.read_bytes() + b"\0")
            pliki.append(n.rsplit(".", 1)[0])
    s = h.hexdigest()[:12]
    return {"skrot": s, "pliki": pliki, "tekst": f"stan modelu: SHA-256 {s} ({', '.join(pliki)})"}
