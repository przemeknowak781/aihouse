"""``Dokument`` — element projektu budowlanego (PZT, PAB, PT, ZL, informacja BIOZ, dokumenty wniosku)
składany z sekcji Markdown/HTML, tabel, ilustracji, bloków oświadczeń i arkuszy rysunkowych do PDF.

Render:
1. HTML (szablony Jinja ``szablony/``, style ``styl.css.j2``) → PDF w Chromium (``render.py``);
   nagłówek, stopka i „strona X z Y” w polach marginesowych CSS; strona tytułowa bez nagłówka i stopki;
2. drugi przebieg: numery stron w spisie treści odczytane z odnośników wewnętrznych pierwszego przebiegu
   (powtarzany, aż numery są stabilne);
3. PyMuPDF: dołączenie arkuszy PDF (formaty oryginalne; brakujące — strony zastępcze), znak statusu na
   arkuszach w wersji przykładowej, zakładki (outline), etykiety stron, metadane, odnośniki GoTo.

Numeracja stron — odrębna dla elementu (RPB § 6 ust. 1); w części rysunkowej rysunki identyfikuje numer
rysunku (§ 6 ust. 3), dlatego „strona X z Y” obejmuje wyłącznie strony A4 części opisowej.
"""
from __future__ import annotations

import base64
import html as _html
import io
import mimetypes
import re
from dataclasses import dataclass, field
from pathlib import Path

import jinja2
import markdown as _md
import pymupdf
from markupsafe import Markup, escape

from . import render as R
from .arkusze import Arkusz, MM
from .dane import ELEMENTY, SPECJALNOSCI, Projektant, dane_obiektu, projektanci_elementu
from .formaty import liczba, data_slownie, data_iso, odmiana
from .znaczniki import (STATUS_PRZYKLAD, DANE_PRZYKLADOWE, do_uzup, dok_zewn, oznacz_html, indeksy_html,
                        bez_indeksow)

SZABLONY = Path(__file__).with_name("szablony")
FONT_REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
URI_RYS = "https://lamela.invalid/rys/"
PUSTE = (None, "", "—", "–", "-", "n/d", "nie dotyczy")

_env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(SZABLONY)), autoescape=jinja2.select_autoescape(
    enabled_extensions=("html", "j2"), default_for_string=True), trim_blocks=True, lstrip_blocks=True)
_env.globals["znacznik_przykl"] = DANE_PRZYKLADOWE

GRUPY = {
    "dolaczone": "Dokumenty dołączone do projektu (§ 7 ust. 5 pkt 3 RPB)",
    "opisowa": "Część opisowa (§ 7 ust. 5 pkt 1 RPB)",
    "rysunkowa": "Część rysunkowa (§ 7 ust. 5 pkt 2 RPB)",
    "zalaczniki": "Załączniki (§ 7 ust. 1a RPB)",
    "wniosek": "Dokumenty do wniosku (poza projektem budowlanym)",
}

MD_EXT = ["extra", "sane_lists", "smarty"]
MD_CFG = {"smarty": {"smart_quotes": False, "smart_dashes": True, "smart_ellipses": True}}


def _css_str(s: str) -> str:
    return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


@dataclass
class WynikDokumentu:
    """Wynik renderu elementu. ``strona`` w wpisach i zakładkach — numer strony w elemencie (od 1)."""
    kod: str
    tytul: str
    pdf: bytes
    sciezka: Path | None
    strony_opisu: int
    strony_razem: int
    wpisy: list = field(default_factory=list)      # [{id, numer, tytul, poziom, grupa, strona, rys}]
    zakladki: list = field(default_factory=list)   # [[poziom, tytul, strona]]
    etykiety: list = field(default_factory=list)   # reguły etykiet stron (PyMuPDF set_page_labels)
    arkusze: list = field(default_factory=list)    # [(Arkusz, strona)]
    przebiegi: int = 0


class Dokument:
    """Element projektu budowlanego.

    >>> d = dane_obiektu()
    >>> pzt = Dokument("Projekt zagospodarowania działki", "PZT", d)
    >>> pzt.oswiadczenie_projektanta()
    >>> pzt.czesc_opisowa("Opis techniczny do projektu zagospodarowania działki")
    >>> pzt.rozdzial("Przedmiot zamierzenia", "Tekst **Markdown** …", podstawa="§ 14 pkt 1 RPB")
    >>> pzt.tabela(df, tytul="Zestawienie powierzchni", suma=["Powierzchnia [m²]"])
    >>> pzt.czesc_rysunkowa([Arkusz.z_pdf("PZT-01.pdf")])
    >>> pzt.render_pdf("PZT.pdf")
    """

    def __init__(self, tytul: str, czesc: str, dane: dict | None = None, *, podtytul: str | None = None,
                 kod: str | None = None, branza: str | None = None, data=None, rewizja: str = "0",
                 projektanci: list[Projektant] | None = None, przyklad: bool | None = None,
                 tom: tuple[int, int] | None = None, stadium: str = "PROJEKT BUDOWLANY", stadium_opis: str | None = None,
                 strona_tytulowa: bool = True, spis_tresci: bool = True, znak_wodny: bool | None = None,
                 spis_poziom: int = 2, pokaz_dzialke: bool = True, tytul_spisu: str | None = None,
                 miejscowosc: str | None = None, grupa_poczatkowa: str = "opisowa"):
        self.dane = dane if dane is not None else dane_obiektu()
        self.tytul = tytul
        self.czesc = czesc.upper()
        self.kod = kod or self.czesc.replace("-", " ")
        self.podtytul = podtytul
        self.branza = branza
        self.data = data_iso(data or self.dane.get("data"))
        self.rewizja = rewizja
        self.przyklad = self.dane.get("przyklad", True) if przyklad is None else przyklad
        self.projektanci = projektanci if projektanci is not None else projektanci_elementu(self.dane, self.czesc)
        self.tom = tom
        self.stadium = stadium
        self.stadium_opis = stadium_opis or ("projekt techniczny — nie podlega zatwierdzeniu" if self.czesc.startswith("PT")
                                             else "do wniosku o pozwolenie na budowę")
        self.strona_tytulowa_wl = strona_tytulowa
        self.spis_wl = spis_tresci
        self.znak_wodny = self.przyklad if znak_wodny is None else znak_wodny
        self.spis_poziom = spis_poziom
        self.pokaz_dzialke = pokaz_dzialke
        self.tytul_spisu = tytul_spisu or ("Spis załączników" if self.czesc == "ZL" else "Spis treści")
        self.miejscowosc = miejscowosc or do_uzup("miejscowość")
        self.autorzy_na_stronie = 4     # więcej autorów → załącznik do strony tytułowej (§ 7 ust. 4 RPB)
        # ustawiane przez Tom
        self.plik_tomu: str | None = None
        self.zawartosc_tomu: list | None = None
        # stan
        self._bloki: list[tuple[str, dict]] = []
        self._wpisy: list[dict] = []
        self._licz = [0, 0, 0, 0, 0]
        self._przes = 0
        self._grupa = grupa_poczatkowa
        self._n_tab = 0
        self._n_ilu = 0
        self._n_zal = 0
        self._id = 0
        self.arkusze: list[Arkusz] = []

    # ------------------------------------------------------------------------------------------ narzędzia
    def _nowe_id(self, pref="b") -> str:
        self._id += 1
        return f"{pref}{self._id}"

    def _wpis(self, id_, tytul, poziom, numer="", **kw):
        w = dict(id=id_, tytul=tytul, poziom=poziom, numer=numer, grupa=self._grupa, rys=False)
        w.update(kw)
        self._wpisy.append(w)
        return w

    @property
    def element_nazwa(self) -> str:
        return ELEMENTY.get(self.czesc.split("-")[0], (self.tytul,))[0]

    # ------------------------------------------------------------------------------------------ struktura
    def czesc_opisowa(self, tytul: str = "Część opisowa", *, podstawa: str | None = None, nowa_strona: bool = True):
        """Rozpoczyna część opisową (nagłówek części na nowej stronie, grupa spisu treści)."""
        self._grupa = "opisowa"
        id_ = self._nowe_id("cz")
        self._bloki.append(("czesc", dict(id=id_, tytul=tytul, podstawa=podstawa, nowa_strona=nowa_strona)))
        return self

    def _zalacznik_wpis(self, tytul: str) -> tuple[str, str]:
        """Rejestruje załącznik w spisie (bez nagłówka) — zwraca (id kotwicy, „Załącznik nr N.”)."""
        self._grupa = "zalaczniki"
        self._n_zal += 1
        self._licz = [0, 0, 0, 0, 0]
        self._przes = 1
        id_ = self._nowe_id("zal")
        numer = f"Załącznik nr {self._n_zal}."
        self._wpis(id_, tytul, 1, numer)
        return id_, numer

    def zalacznik(self, tytul: str, *, podstawa: str | None = None, nowa_strona: bool = True):
        """Numerowany załącznik (element ZL): „Załącznik nr N. tytuł”; numeracja rozdziałów od 1 w załączniku."""
        id_, numer = self._zalacznik_wpis(tytul)
        self._bloki.append(("naglowek", dict(id=id_, tag="h1", klasa="zal", numer=numer, tytul=tytul,
                                              podstawa=podstawa, nowa_strona=nowa_strona)))
        return self

    def rozdzial(self, tytul: str, tresc: str | None = None, *, poziom: int = 1, podstawa: str | None = None,
                 nowa_strona: bool = False, w_spisie: bool | None = None, numeruj: bool = True):
        """Nagłówek numerowany (1. / 1.1. / 1.1.1.) + opcjonalna treść Markdown. ``podstawa`` — jednostka
        redakcyjna przepisu wyświetlana przy nagłówku (np. „§ 14 pkt 1 RPB”)."""
        poziom = max(1, min(4, poziom))
        numer = ""
        if numeruj:
            self._licz[poziom - 1] += 1
            for i in range(poziom, len(self._licz)):
                self._licz[i] = 0
            numer = ".".join(str(n) for n in self._licz[:poziom]) + "."
        lvl = poziom + self._przes
        id_ = self._nowe_id("r")
        if w_spisie is None:
            w_spisie = lvl <= self.spis_poziom
        if w_spisie:
            self._wpis(id_, tytul, lvl, numer)
        self._bloki.append(("naglowek", dict(id=id_, tag=f"h{min(lvl, 6)}", klasa=f"g{poziom}", numer=numer,
                                              tytul=tytul, podstawa=podstawa, nowa_strona=nowa_strona)))
        if tresc:
            self.markdown(tresc)
        return self

    def podrozdzial(self, tytul: str, tresc: str | None = None, **kw):
        return self.rozdzial(tytul, tresc, poziom=2, **kw)

    def markdown(self, tekst: str, *, przesuniecie: int = 0):
        """Treść Markdown (tabele, listy, pogrubienia, przypisy…). Nagłówki w treści stają się rozdziałami
        numerowanymi: ``#`` — poziom 1 (rozdział), ``##`` — poziom 2 (podrozdział) itd. (+ ``przesuniecie``).
        Podstawę prawną nagłówka podaje się na końcu: ``## Tytuł {podstawa: § 14 pkt 3 lit. c}``."""
        tekst = _dedent(tekst)
        czesci = re.split(r"^(#{1,4})[ \t]+(.+?)[ \t]*#*[ \t]*$", tekst, flags=re.M)
        self._md_blok(czesci[0])
        for i in range(1, len(czesci), 3):
            poz = len(czesci[i]) + przesuniecie
            tyt = czesci[i + 1]
            m = re.match(r"(.*?)\s*\{podstawa:\s*(.+)\}\s*$", tyt)
            self.rozdzial(m.group(1) if m else tyt, poziom=poz, podstawa=m.group(2) if m else None)
            self._md_blok(czesci[i + 2])
        return self

    def _md_blok(self, tekst: str):
        if tekst and tekst.strip():
            h = _md.markdown(tekst, extensions=MD_EXT, extension_configs=MD_CFG, output_format="html")
            h = h.replace("<table>", '<table class="tab">')
            self._bloki.append(("html", dict(html=Markup(h))))

    def html(self, html: str):
        """Wstawia gotowy fragment HTML (bez przetwarzania)."""
        self._bloki.append(("html", dict(html=Markup(html))))
        return self

    def akapit(self, tekst: str):
        self._bloki.append(("html", dict(html=Markup(f"<p>{escape(tekst)}</p>"))))
        return self

    def lista(self, pozycje: list, *, numerowana: bool = False):
        tag = "ol" if numerowana else "ul"
        li = "".join(f"<li>{escape(p) if not isinstance(p, Markup) else p}</li>" for p in pozycje)
        self._bloki.append(("html", dict(html=Markup(f"<{tag}>{li}</{tag}>"))))
        return self

    def wniosek(self, tekst: str, *, alarm: bool = False):
        """Wyróżniony akapit wniosku / konkluzji (Markdown w linii)."""
        h = _md.markdown(tekst, extensions=MD_EXT, extension_configs=MD_CFG)
        self._bloki.append(("html", dict(html=Markup(f'<div class="wniosek{" alarm" if alarm else ""}">{h}</div>'))))
        return self

    def nowa_strona(self):
        self._bloki.append(("html", dict(html=Markup('<div class="nowa-strona"></div>'))))
        return self

    # ------------------------------------------------------------------------------------------ tabele
    def tabela(self, dane, kolumny=None, *, tytul: str | None = None, jednostki: dict | None = None,
               formaty: dict | None = None, wyrownanie: dict | None = None, szerokosci: list | None = None,
               suma=None, etykieta_sumy: str = "Razem", uwagi: list | str | None = None, zrodlo: str | None = None,
               lp: bool = False, klasa: str = "", html_komorki: bool = False, wiersze_klasy: dict | None = None):
        """Tabela z DataFrame, listy słowników lub listy list (``kolumny`` — nagłówki).

        * nagłówek „Powierzchnia [m²]” → jednostka w drugiej linii nagłówka (lub ``jednostki={kol: 'm²'}``),
        * ``formaty={kol: 2 | '{:.1f}' | callable}`` — liczby w zapisie polskim (domyślnie float → 2 miejsca),
        * ``wyrownanie={kol: 'l'|'r'|'c'}`` — domyślnie liczby do prawej,
        * ``suma=True | [kolumny] | {kol: wartość}`` — wiersz „Razem”,
        * wiersz będący napisem → wiersz grupy na całą szerokość; słownik z kluczem ``_klasa`` — klasa wiersza
          (``suma``, ``grupa``, ``pod``).
        """
        cols, rows = _normalizuj(dane, kolumny)
        n = len(cols)
        jednostki = dict(jednostki or {})
        formaty = dict(formaty or {})
        wyrownanie = dict(wyrownanie or {})
        naglowki = []
        for c in cols:
            nazwa, jedn = str(c), jednostki.get(c)
            m = re.match(r"^(.*?)\s*\[(.+)\]\s*$", nazwa)
            if m and jedn is None:
                nazwa, jedn = m.group(1), m.group(2)
            naglowki.append((nazwa, f"[{jedn}]" if jedn and not str(jedn).startswith("[") else jedn))
        numeryczne = [all(isinstance(r[1][j], (int, float)) and not isinstance(r[1][j], bool)
                          for r in rows if r[0] is None and r[1][j] not in PUSTE) and
                      any(isinstance(r[1][j], (int, float)) for r in rows if r[0] is None) for j in range(n)]

        def fmt(j, v):
            c = cols[j]
            f = formaty.get(c)
            if v is None or (isinstance(v, float) and v != v):
                return "—"
            if callable(f):
                return f(v)
            if isinstance(f, int):
                return liczba(v, f)
            if isinstance(f, str) and isinstance(v, (int, float)):
                return liczba(v, _miejsca_z_formatu(f)) if re.fullmatch(r"\{:\.\d+f\}", f) else f.format(v)
            if isinstance(v, bool):
                return "tak" if v else "nie"
            if isinstance(v, float):
                return liczba(v, 2)
            if isinstance(v, int):
                return liczba(v, 0)
            return v

        def kl(j):
            a = wyrownanie.get(cols[j], "r" if numeryczne[j] else "l")
            return {"r": "num", "c": "c", "l": ""}[a]

        wiersze = []
        if lp:
            naglowki.insert(0, ("Lp.", None))
        nr = 0
        for klasa_w, r in rows:
            if klasa_w == "grupa_txt":
                wiersze.append(dict(klasa="grupa", komorki=[dict(tekst=_cell(r, html_komorki), klasa="", colspan=n + lp)]))
                continue
            komorki = [dict(tekst=_cell(fmt(j, v), html_komorki),
                            klasa=kl(j) + (" wrap" if isinstance(v, str) and numeryczne[j] else ""), colspan=1)
                       for j, v in enumerate(r)]
            if lp:
                if klasa_w in (None, ""):
                    nr += 1
                komorki.insert(0, dict(tekst=f"{nr}." if klasa_w in (None, "") else "", klasa="lp", colspan=1))
            wiersze.append(dict(klasa=klasa_w or "", komorki=komorki))
        if suma:
            if suma is True:
                sumy = {cols[j]: sum(r[1][j] for r in rows if r[0] is None and isinstance(r[1][j], (int, float)))
                        for j in range(n) if numeryczne[j]}
            elif isinstance(suma, dict):
                sumy = suma
            else:
                sumy = {c: sum(r[1][cols.index(c)] for r in rows if r[0] is None
                               and isinstance(r[1][cols.index(c)], (int, float))) for c in suma}
            kom = []
            for j, c in enumerate(cols):
                if c in sumy:
                    kom.append(dict(tekst=_cell(fmt(j, sumy[c]), html_komorki), klasa=kl(j), colspan=1))
                else:
                    kom.append(dict(tekst="", klasa="", colspan=1))
            if not any(cols[0] == c for c in sumy):
                kom[0]["tekst"] = etykieta_sumy
            if lp:
                kom.insert(0, dict(tekst="", klasa="lp", colspan=1))
            wiersze.append(dict(klasa="suma", komorki=kom))
        kolumny_t = [dict(naglowek=h, jedn=j, klasa=("lp" if (lp and i == 0) else kl(i - lp) if i - lp >= 0 else ""))
                     for i, (h, j) in enumerate(naglowki)]
        self._n_tab += 1
        if isinstance(uwagi, str):
            uwagi = [uwagi]
        t = dict(id=self._nowe_id("tab"), numer=self._n_tab, tytul=tytul, kolumny=kolumny_t, wiersze=wiersze,
                 uwagi=[Markup(_md.markdown(u).removeprefix("<p>").removesuffix("</p>")) for u in (uwagi or [])],
                 zrodlo=zrodlo, klasa=klasa, szerokosci=szerokosci)
        self._bloki.append(("tabela", t))
        return self

    def tabela_przegrody(self, nazwa: str, warstwy: list, *, Rsi: float = 0.13, Rse: float = 0.04,
                         U_max: float | None = None, podstawa_Umax: str | None = None, strumien: str = "poziomy",
                         od_zewnatrz: bool = False, uwagi: list | None = None, zrodlo: str | None = None,
                         kod: str | None = None) -> dict:
        """Tabela przegrody z warstwami i obliczeniem U wg PN-EN ISO 6946:2017-10 (bez poprawek ΔU — [ZAŁ]).
        ``warstwy``: [(nazwa, d [m], λ [W/(m·K)])] lub słowniki {nazwa, d, lambda, R}; kolejność warstw — od strony
        wewnętrznej, chyba że ``od_zewnatrz=True`` (np. stropodach opisany od góry). Zwraca {R_T, U, spelnia}."""
        kol = "Warstwa (od zewnątrz)" if od_zewnatrz else "Warstwa (od wewnątrz)"
        w_si = {"_klasa": "pod", kol: f"opór przejmowania ciepła po stronie wewnętrznej R_{{si}} ({strumien} strumień)",
                "d [m]": None, "λ [W/(m·K)]": None, "R [m²·K/W]": Rsi}
        w_se = {"_klasa": "pod", kol: "opór przejmowania ciepła po stronie zewnętrznej R_{se}",
                "d [m]": None, "λ [W/(m·K)]": None, "R [m²·K/W]": Rse}
        wiersze, R_suma = [w_se if od_zewnatrz else w_si], 0.0
        for w in warstwy:
            if isinstance(w, dict):
                nz, d, lam, Rw = w.get("nazwa"), w.get("d"), w.get("lambda"), w.get("R")
            else:
                nz, d, lam = w[:3]
                Rw = w[3] if len(w) > 3 else None
            if Rw is None:
                Rw = d / lam if lam else 0.0
            R_suma += Rw
            wiersze.append({kol: nz, "d [m]": d, "λ [W/(m·K)]": lam, "R [m²·K/W]": Rw})
        wiersze.append(w_si if od_zewnatrz else w_se)
        RT = Rsi + R_suma + Rse
        U = 1.0 / RT
        d_suma = sum((w.get("d") if isinstance(w, dict) else w[1]) or 0 for w in warstwy)
        wiersze.append({"_klasa": "suma", kol: "Całkowity opór cieplny R_{T} / grubość przegrody",
                        "d [m]": d_suma, "λ [W/(m·K)]": None, "R [m²·K/W]": RT})
        spelnia = None if U_max is None else U <= U_max + 1e-9
        wynik_txt = f"<b>U = {liczba(U, 3)} W/(m²·K)</b>"
        if U_max is not None:
            wynik_txt += f" {'≤' if spelnia else '>'} U_{{max}} = {liczba(U_max, 2)} W/(m²·K) — " + \
                         ("<b class='ok'>spełnia</b>" if spelnia else "<b class='nok'>NIE SPEŁNIA</b>")
        u = [f"Współczynnik przenikania ciepła: {wynik_txt}"
             + (f" ({podstawa_Umax})" if podstawa_Umax else "") + "."]
        u.append("Obliczenie wg PN-EN ISO 6946:2017-10, bez poprawek ΔU na łączniki mechaniczne i nieszczelności "
                 "— [ZAŁ]; λ — wartości obliczeniowe z modelu materiałów.")
        u += list(uwagi or [])
        self.tabela(wiersze, tytul=f"{kod + ' — ' if kod else ''}{nazwa}", lp=False,
                    formaty={"d [m]": 3, "λ [W/(m·K)]": 3, "R [m²·K/W]": 3}, szerokosci=[None, "18mm", "22mm", "24mm"],
                    uwagi=u, zrodlo=zrodlo, klasa="zwarta")
        return {"R_T": RT, "U": U, "spelnia": spelnia}

    def tabela_wynikow(self, wiersze: list[dict], *, tytul: str = "Zestawienie wyników sprawdzenia",
                       uwagi=None, zrodlo=None):
        """Wyniki obliczeń/sprawdzeń: wiersze {parametr, wartosc, jedn, wymaganie, podstawa, spelnia(True/False/None)}."""
        rows = []
        for w in wiersze:
            s = w.get("spelnia")
            st = ("<span class='ok'>✓ spełnia</span>" if s is True else "<span class='nok'>✗ nie spełnia</span>"
                  if s is False else "<span class='nd'>—</span>")
            wart = w.get("wartosc")
            wart = liczba(wart, w.get("miejsca", 2)) if isinstance(wart, (int, float)) else (wart or "—")
            rows.append({"Parametr": Markup(escape(w.get("parametr", ""))),
                         "Wartość": Markup(f"{escape(wart)} {escape(w.get('jedn', ''))}".strip()),
                         "Wymaganie": Markup(escape(w.get("wymaganie", "—"))),
                         "Podstawa": Markup(f"<span class='mn'>{escape(w.get('podstawa', ''))}</span>"),
                         "Wynik": Markup(st)})
        return self.tabela(rows, tytul=tytul, lp=True, wyrownanie={"Wartość": "r"}, uwagi=uwagi, zrodlo=zrodlo,
                           html_komorki=True, szerokosci=["7mm", None, "26mm", "30mm", "44mm", "22mm"])

    # ------------------------------------------------------------------------------------------ ilustracje
    def obraz(self, zrodlo, *, podpis: str | None = None, szerokosc: str | None = None):
        """Obraz z pliku (PNG/JPG/SVG) lub bajtów PNG — osadzony w HTML (SVG jako wektor)."""
        if isinstance(zrodlo, (bytes, bytearray)):
            h = f'<img src="data:image/png;base64,{base64.b64encode(zrodlo).decode()}">'
        else:
            p = Path(zrodlo)
            if p.suffix.lower() == ".svg":
                h = _svg_inline(p.read_text(encoding="utf-8"))
            else:
                mt = mimetypes.guess_type(p.name)[0] or "image/png"
                h = f'<img src="data:{mt};base64,{base64.b64encode(p.read_bytes()).decode()}">'
        return self._ilustracja(h, podpis, szerokosc)

    def wykres(self, fig, *, podpis: str | None = None, szerokosc: str | None = None):
        """Wykres matplotlib osadzony jako SVG (wektor w PDF)."""
        buf = io.StringIO()
        fig.savefig(buf, format="svg", bbox_inches="tight")
        return self._ilustracja(_svg_inline(buf.getvalue()), podpis, szerokosc)

    def _ilustracja(self, h, podpis, szerokosc):
        self._n_ilu += 1
        self._bloki.append(("ilustracja", dict(id=self._nowe_id("il"), html=Markup(h), numer=self._n_ilu,
                                                podpis=podpis, szerokosc=szerokosc)))
        return self

    # ------------------------------------------------------------------------------------------ bloki formalne
    def _osw_w_spisie(self, id_, tytul, w_spisie):
        """Oświadczenia przed częścią opisową trafiają do grupy „Dokumenty dołączone” spisu treści."""
        if not w_spisie:
            return
        g = self._grupa
        if g == "opisowa" and not any(b[0] == "czesc" for b in self._bloki):
            self._grupa = "dolaczone"
            self._wpis(id_, tytul, 1 + self._przes)
            self._grupa = g
        else:
            self._wpis(id_, tytul, 1 + self._przes)

    def oswiadczenie_projektanta(self, *, projektant: Projektant | None = None, osoby: list | None = None,
                                 techniczny: bool | None = None, art102a: bool = True, pnb: str | None = None,
                                 w_spisie: bool = True, podpisuja: list | None = None):
        """Oświadczenie projektanta o sporządzeniu projektu zgodnie z przepisami i zasadami wiedzy technicznej
        (art. 34 ust. 3d pkt 3 PB) z listą osób biorących udział w opracowaniu (ust. 3e). Dla PT
        (``techniczny=True``, domyślnie gdy część zaczyna się od „PT”) — brzmienie z art. 41 ust. 4a pkt 2 PB."""
        from .bloki import kontekst_oswiadczenia_projektanta
        if techniczny is None:
            techniczny = self.czesc.startswith("PT")
        o = kontekst_oswiadczenia_projektanta(self, projektant=projektant, osoby=osoby, techniczny=techniczny,
                                              art102a=art102a, pnb=pnb, podpisuja=podpisuja)
        self._osw_w_spisie(o["id"], "Oświadczenie projektanta (art. 34 ust. 3d pkt 3 PB)", w_spisie)
        self._bloki.append(("oswiadczenie_projektanta", o))
        return self

    def oswiadczenie_sieci_cieplowniczej(self, *, projektant: Projektant | None = None, wariant: str = "brak_sieci",
                                         zrodlo_ciepla: str | None = None, uzasadnienie: str | None = None,
                                         w_spisie: bool = True, zalacznik: bool | str = False):
        """Oświadczenie projektanta instalacji sanitarnych o możliwości podłączenia do sieci ciepłowniczej
        (art. 33 ust. 2 pkt 10 PB, art. 7b Prawa energetycznego) z klauzulą o odpowiedzialności karnej.
        ``wariant``: 'brak_sieci' | 'zrodlo_indywidualne' | 'przylaczenie'."""
        from .bloki import kontekst_oswiadczenia_sieci
        o = kontekst_oswiadczenia_sieci(self, projektant=projektant, wariant=wariant, zrodlo_ciepla=zrodlo_ciepla,
                                        uzasadnienie=uzasadnienie, zalacznik=zalacznik)
        if not zalacznik:
            self._osw_w_spisie(o["id"], "Oświadczenie projektanta dotyczące sieci ciepłowniczej "
                                        "(art. 33 ust. 2 pkt 10 PB)", w_spisie)
        self._bloki.append(("oswiadczenie_sieci", o))
        return self

    def oswiadczenie_inwestora_102a(self, *, organ: str | None = None, zakres: str | None = None,
                                    postepowanie: str | None = None, w_spisie: bool = True,
                                    zalacznik: bool | str = False):
        """WZÓR oświadczenia Inwestora o stosowaniu WT w brzmieniu do 19.09.2026 (art. 102a ust. 1 PB).
        ``zalacznik`` — numerowany załącznik elementu ZL (tytuł: True = domyślny lub tekst)."""
        from .bloki import kontekst_oswiadczenia_102a
        o = kontekst_oswiadczenia_102a(self, organ=organ, zakres=zakres, postepowanie=postepowanie, zalacznik=zalacznik)
        if not zalacznik:
            self._osw_w_spisie(o["id"], "Oświadczenie Inwestora z art. 102a ust. 1 PB — wzór", w_spisie)
        self._bloki.append(("oswiadczenie_102a", o))
        return self

    def informacja_pb5(self, *, tytul_prawny: str | None = None, w_spisie: bool = True):
        """Informacja: oświadczenie o prawie do dysponowania nieruchomością — tylko na urzędowym wzorze PB-5."""
        id_ = self._nowe_id("pb5")
        self._osw_w_spisie(id_, "Oświadczenie o prawie do dysponowania nieruchomością (PB-5) — informacja", w_spisie)
        self._bloki.append(("informacja_pb5", dict(id=id_, tytul_prawny=tytul_prawny or do_uzup(
            "tytuł prawny (własność / współwłasność / użytkowanie wieczyste / inny) — wg księgi wieczystej"))))
        return self

    def blok_podpisow(self, osoby: list | None = None):
        """Karty podpisów (pola puste): domyślnie autorzy elementu."""
        from .bloki import karty_podpisow
        self._bloki.append(("podpisy", dict(osoby=karty_podpisow(osoby or self.projektanci, self.data))))
        return self

    def informacja_bioz(self, tresc: dict | None = None, *, projektant: Projektant | None = None,
                        zagrozenia: list | None = None, jako_zalacznik: bool = True):
        """Informacja BIOZ (rozp. BIOZ Dz.U. 2003 nr 120 poz. 1126 § 2): strona tytułowa (§ 2 ust. 2) i część
        opisowa pkt 1–6 (§ 2 ust. 3) + zestawienie robót z § 6 rozp. i wniosek o planie BIOZ (art. 21a PB)."""
        from .bloki import dodaj_informacje_bioz
        dodaj_informacje_bioz(self, tresc=tresc, projektant=projektant, zagrozenia=zagrozenia,
                              jako_zalacznik=jako_zalacznik)
        return self

    def dokument_zewnetrzny(self, nazwa: str, *, organ: str, podstawa: str, sygnatura: str | None = None,
                            uwagi: str | None = None, jako_zalacznik: bool = True):
        """Strona zastępcza dokumentu wydawanego przez organ/gestora (znacznik [DOKUMENT ZEWNĘTRZNY – …])."""
        if jako_zalacznik:
            self.zalacznik(nazwa, nowa_strona=True)
        id_ = self._nowe_id("zw")
        self._bloki.append(("dokument_zewnetrzny", dict(
            id=id_, nazwa=nazwa, organ=organ, podstawa=podstawa,
            sygnatura=sygnatura or do_uzup("numer i data dokumentu"),
            znacznik=dok_zewn(f"{nazwa}, {organ}, {podstawa}"), uwagi=uwagi, bez_przerwy=jako_zalacznik)))
        return self

    def czesc_rysunkowa(self, arkusze: list, *, podstawa: str = "§ 7 ust. 1 pkt 4, § 10 RPB",
                        autorzy: list | None = None):
        """Karta części rysunkowej z metryką i wykazem rysunków (generowanym z listy arkuszy) + dołączenie
        arkuszy PDF za częścią opisową. Elementy listy: ``Arkusz`` lub ścieżka PDF."""
        self._grupa = "rysunkowa"
        self._przes = 0          # część rysunkowa nie jest częścią poprzedzającego załącznika (np. opinii w PAB)
        self.arkusze = [a if isinstance(a, Arkusz) else Arkusz.z_pdf(a) for a in arkusze]
        id_ = self._nowe_id("rys")
        self._wpis(id_, "Karta części rysunkowej i wykaz rysunków", 1 + self._przes)
        for k, a in enumerate(self.arkusze):
            self._wpis(f"{URI_RYS}{k}", f"{a.tytul}" + (f" ({a.skala})" if a.skala and a.skala != "—" else ""),
                       2 + self._przes, numer=a.nr, rys=True, arkusz=k)
        rows = []
        for a in self.arkusze:
            status = a.uwagi or ("" if a.istnieje else do_uzup("brak pliku arkusza"))
            rows.append({"Nr rysunku": Markup(f"<b>{escape(a.nr)}</b>"), "Tytuł rysunku": a.tytul, "Skala": a.skala or "—",
                         # format niestandardowy: „nst.” — wymiary w kolumnie obok (bez łamania „540×5/94”)
                         "Format": "nst." if str(a.format or "").startswith("nst.") else (a.format or "—"),
                         "Wymiary [mm]": a.wymiar_tekst(), "Uwagi": status})
        self._n_tab += 1
        wykaz = _tabela_ctx(self._nowe_id("tab"), self._n_tab, "Wykaz rysunków", rows, lp=True,
                            szerokosci=["9mm", "19mm", None, "13mm", "14mm", "19mm", "42mm"],
                            wyrown={"Skala": "c", "Format": "c", "Wymiary [mm]": "c"})
        self._bloki.append(("karta_rysunkowa", dict(
            id=id_, podstawa=podstawa, element=f"{self.kod} — {self.tytul}", branza=self.branza,
            autorzy=[p.slownik() for p in (autorzy or self.projektanci)], data=data_slownie(self.data),
            liczba=f"{len(self.arkusze)} {odmiana(len(self.arkusze), 'rysunek', 'rysunki', 'rysunków')}", wykaz=wykaz)))
        return self

    # ------------------------------------------------------------------------------------------ render HTML
    def _ctx_tytulowej(self) -> dict:
        from .bloki import zawartosc_domyslna
        tom_opis = []
        if self.tom:
            tom_opis.append(f"Tom {self.tom[0]} z {self.tom[1]}")
        if self.branza:
            tom_opis.append(f"branża: {self.branza}")
        tom_opis.append("element projektu budowlanego wg art. 34 ust. 3 PB" if self.czesc in ("PZT", "PAB") or
                        self.czesc.startswith("PT") else "element projektu budowlanego wg § 5 ust. 1 pkt 4 RPB"
                        if self.czesc == "ZL" else "")
        zaw = self.zawartosc_tomu or zawartosc_domyslna(self)
        autorzy = [dict(p.slownik(), branza=SPECJALNOSCI.get(p.branza, ("", "", p.branza))[2]) for p in self.projektanci]
        return dict(kod=self.kod, tytul=self.tytul, podtytul=self.podtytul, stadium=self.stadium,
                    stadium_opis=self.stadium_opis, tom_opis=" · ".join(t for t in tom_opis if t),
                    przyklad=self.przyklad, pokaz_dzialke=self.pokaz_dzialke, autorzy=autorzy,
                    data=data_slownie(self.data), rewizja=f"rew. {self.rewizja}", plik=self.plik_tomu,
                    zawartosc_tomu=zaw, uwaga_dodatkowa="", autorzy_osobno=len(autorzy) > self.autorzy_na_stronie)

    def _wpisy_spisu(self, strony: dict) -> list[dict]:
        out, g = [], None
        for w in self._wpisy:
            e = dict(w)
            e["grupa_naglowek"] = GRUPY.get(w["grupa"]) if w["grupa"] != g else None
            g = w["grupa"]
            if w.get("rys"):
                e["href"] = w["id"]
                e["strona"] = "rys."
            else:
                e["href"] = "#" + w["id"]
                s = strony.get(w["id"])
                e["strona"] = str(s) if s else ""
            out.append(e)
        return out

    def css(self) -> str:
        d = self.dane
        lewy = f"{d['nazwa_krotka']} · {d['obiekt'].split('„')[0].strip().rstrip(',')} · dz. ewid. {d['dzialka']['nr']}"
        prawy = f"{self.kod} · {self.tytul}"
        if self.przyklad:
            stopka = f"{STATUS_PRZYKLAD} · {DANE_PRZYKLADOWE}"
        else:
            stopka = f"{self.plik_tomu or ''} · rew. {self.rewizja} · {self.data}"
        return _env.get_template("styl.css.j2").render(
            naglowek_lewy=_css_str(lewy), naglowek_prawy=_css_str(prawy), stopka_lewa=_css_str(stopka),
            stopka_prawa=_css_str(f"{self.kod} · "), przyklad=self.przyklad)

    def render_html(self, strony: dict | None = None) -> str:
        strony = strony or {}
        m = _env.get_template("bloki.html.j2").module
        d = self.dane
        body = []
        if self.znak_wodny:
            body.append(f'<div class="znak-wodny">{STATUS_PRZYKLAD}</div>')
        if self.strona_tytulowa_wl:
            ctx = self._ctx_tytulowej()
            body.append(str(m.strona_tytulowa(d, ctx)))
            if ctx["autorzy_osobno"]:
                body.append(str(m.autorzy_zalacznik(d, ctx)))
        if self.spis_wl:
            leg = ("Numeracja stron odrębna dla elementu (§ 6 ust. 1 RPB); rysunki oznaczono numerem rysunku "
                   "(§ 6 ust. 3 RPB). Pozycje spisu są odnośnikami w pliku PDF.")
            body.append(str(m.spis(dict(tytul=self.tytul_spisu, wpisy=self._wpisy_spisu(strony), legenda=leg,
                                        podstawa=f"{self.kod} — {self.tytul}"))))
        pierwszy = True
        for typ, b in self._bloki:
            if typ == "naglowek":
                h = str(m.naglowek(b))
                if b.get("nowa_strona"):
                    h = f'<div class="nowa-strona">{h}</div>'
                body.append(h)
            elif typ == "czesc":
                ns = " nowa-strona" if b["nowa_strona"] and not pierwszy else ""
                body.append(f'<div class="nagl czesc{ns}" id="{b["id"]}"><span class="t">{escape(b["tytul"])}</span>'
                            + (f'<span class="podst">{escape(b["podstawa"])}</span>' if b.get("podstawa") else "")
                            + "</div>")
            elif typ == "html":
                body.append(str(b["html"]))
            elif typ == "tabela":
                body.append(str(m.tabela(b)))
            elif typ == "ilustracja":
                body.append(str(m.ilustracja(b)))
            elif typ == "podpisy":
                body.append(str(m.podpisy(b["osoby"], jeden=len(b["osoby"]) == 1)))
            elif typ == "oswiadczenie_projektanta":
                body.append(str(m.oswiadczenie_projektanta(b, d)))
            elif typ == "oswiadczenie_sieci":
                body.append(str(m.oswiadczenie_sieci(b, d)))
            elif typ == "oswiadczenie_102a":
                body.append(str(m.oswiadczenie_102a(b, d)))
            elif typ == "informacja_pb5":
                body.append(str(m.informacja_pb5(b, d)))
            elif typ == "bioz_tytulowa":
                body.append(str(m.bioz_tytulowa(b, d)))
            elif typ == "dokument_zewnetrzny":
                h = str(m.dokument_zewnetrzny(b))
                if b.get("bez_przerwy"):
                    h = h.replace('<section class="zewn"', '<section class="zewn" style="break-before:auto"', 1)
                body.append(h)
            elif typ == "karta_rysunkowa":
                body.append(str(m.karta_rysunkowa(b, d)))
            else:
                raise ValueError(f"nieznany blok {typ}")
            pierwszy = False
        tyt = _html.escape(f"{d['nazwa_krotka']} — {self.kod} {self.tytul}")
        doc = (f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{tyt}</title>'
               f"<style>{self.css()}</style></head><body>" + "\n".join(body) + "</body></html>")
        return indeksy_html(oznacz_html(doc))

    # ------------------------------------------------------------------------------------------ render PDF
    def render_pdf(self, sciezka: str | Path | None = None, *, dolacz_arkusze: bool = True,
                   stempel_arkuszy: bool | None = None, maks_przebiegow: int = 4) -> WynikDokumentu:
        """Render dwuprzebiegowy (numery stron w spisie) + dołączenie arkuszy. Zapisuje PDF, gdy podano ścieżkę."""
        strony: dict = {}
        pdf = None
        przebieg = 0
        for przebieg in range(1, maks_przebiegow + 1):
            pdf = R.html_na_pdf(self.render_html(strony))
            doc = pymupdf.open(stream=pdf, filetype="pdf")
            nowe = {k: v + 1 for k, v in R.kotwice(doc).items()}
            doc.close()
            if nowe == strony:
                break
            strony = nowe
        doc = pymupdf.open(stream=pdf, filetype="pdf")
        n_opis = doc.page_count
        arkusze_strony = []
        if dolacz_arkusze and self.arkusze:
            stempel = self.przyklad if stempel_arkuszy is None else stempel_arkuszy
            zastepcze = [a for a in self.arkusze if not a.istnieje]
            zdoc = pymupdf.open(stream=_strony_zastepcze(zastepcze, self), filetype="pdf") if zastepcze else None
            zi = 0
            for a in self.arkusze:
                start = doc.page_count
                if a.istnieje:
                    src = pymupdf.open(str(a.plik))
                    doc.insert_pdf(src, links=True, annots=True)
                    src.close()
                else:
                    doc.insert_pdf(zdoc, from_page=zi, to_page=zi)
                    zi += 1
                if stempel:
                    for pno in range(start, doc.page_count):
                        stempluj_arkusz(doc[pno])
                arkusze_strony.append((a, start + 1))
        # odnośniki: nazwane → GoTo; URI wykazu rysunków → GoTo do arkusza
        mapa = {k: s - 1 for k, (a, s) in enumerate(arkusze_strony)}
        R.linki_na_goto(doc, lambda u: mapa.get(int(u[len(URI_RYS):])) if u.startswith(URI_RYS) else None)
        wpisy = []
        for w in self._wpisy:
            e = dict(w)
            e["strona"] = arkusze_strony[w["arkusz"]][1] if w.get("rys") and arkusze_strony else strony.get(w["id"])
            wpisy.append(e)
        zakladki = self._zakladki(wpisy)
        etykiety = [{"startpage": 0, "prefix": f"{self.kod} s. ", "style": "D", "firstpagenum": 1}]
        for a, s in arkusze_strony:
            etykiety.append({"startpage": s - 1, "prefix": f"{a.nr}", "style": "", "firstpagenum": 1})
        doc.set_toc(zakladki)
        try:
            doc.set_page_labels(etykiety)
        except Exception:
            pass
        _metadane(doc, tytul=f"{self.dane['nazwa_krotka']} — {self.kod} {self.tytul}", dane=self.dane,
                  temat=f"{self.tytul} — {self.dane['obiekt']}", przyklad=self.przyklad, projektanci=self.projektanci)
        dane_pdf = doc.tobytes(garbage=3, deflate=True, deflate_fonts=True)
        doc.close()
        wynik = WynikDokumentu(kod=self.kod, tytul=self.tytul, pdf=dane_pdf, sciezka=None, strony_opisu=n_opis,
                               strony_razem=n_opis + sum(max(a.strony, 1) for a in self.arkusze if dolacz_arkusze),
                               wpisy=wpisy, zakladki=zakladki, etykiety=etykiety, arkusze=arkusze_strony,
                               przebiegi=przebieg)
        if sciezka:
            p = Path(sciezka)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(dane_pdf)
            wynik.sciezka = p
        return wynik

    def _zakladki(self, wpisy) -> list:
        z = []
        if self.strona_tytulowa_wl:
            z.append([1, "Strona tytułowa", 1])
        if self.spis_wl:
            z.append([1, self.tytul_spisu, 2 if self.strona_tytulowa_wl else 1])
        ostatni = 1 if z else 0
        for w in wpisy:
            if not w.get("strona"):
                continue
            lvl = w["poziom"]
            lvl = min(lvl, ostatni + 1) if ostatni else 1
            tyt = f"{w['numer']} {w['tytul']}".strip() if not w.get("rys") else f"{w['numer']} — {w['tytul']}"
            z.append([lvl, _plain(tyt), int(w["strona"])])
            ostatni = lvl
        return z


# ================================================================================================ funkcje pomocnicze
def _dedent(t: str) -> str:
    import textwrap
    return textwrap.dedent(t).strip("\n")


def _plain(s) -> str:
    return bez_indeksow(re.sub(r"<[^>]+>", "", str(s)))


def _cell(v, html_ok: bool):
    if isinstance(v, Markup):
        return v
    if html_ok:
        return Markup(str(v))
    return escape(str(v))


def _miejsca_z_formatu(f: str) -> int:
    return int(re.search(r"\.(\d+)f", f).group(1))


def _normalizuj(dane, kolumny):
    """→ (kolumny, [(klasa_wiersza | None | 'grupa_txt', wartości)])"""
    try:
        import pandas as pd
        if isinstance(dane, pd.DataFrame):
            cols = list(kolumny or dane.columns)
            rows = [(None, [(_py(v)) for v in r]) for r in dane[cols].itertuples(index=False, name=None)]
            return cols, rows
    except ImportError:
        pass
    dane = list(dane)
    if kolumny is None and any(isinstance(r, dict) for r in dane):
        cols = []
        for r in dane:
            if isinstance(r, dict):
                for k in r:
                    if k != "_klasa" and k not in cols:
                        cols.append(k)
    else:
        cols = list(kolumny or [])
    rows = []
    for r in dane:
        if isinstance(r, str):
            rows.append(("grupa_txt", r))
        elif isinstance(r, dict):
            rows.append((r.get("_klasa"), [_py(r.get(c)) for c in cols]))
        else:
            rows.append((None, [_py(v) for v in r]))
    return cols, rows


def _py(v):
    try:
        import numpy as np
        if isinstance(v, np.generic):
            return v.item()
    except ImportError:
        pass
    return v


def _tabela_ctx(id_, numer, tytul, rows, lp=False, szerokosci=None, wyrown=None):
    """Kontekst tabeli dla makr (bez rejestrowania w dokumencie)."""
    cols = list(rows[0].keys()) if rows else ["Nr rysunku", "Tytuł rysunku"]
    wyrown = wyrown or {}
    kol = ([dict(naglowek="Lp.", jedn=None, klasa="lp")] if lp else [])
    for c in cols:
        m = re.match(r"^(.*?)\s*\[(.+)\]\s*$", c)
        kol.append(dict(naglowek=m.group(1) if m else c, jedn=f"[{m.group(2)}]" if m else None,
                        klasa={"c": "c", "r": "num"}.get(wyrown.get(c), "")))
    wiersze = []
    for i, r in enumerate(rows):
        kom = ([dict(tekst=f"{i + 1}.", klasa="lp", colspan=1)] if lp else [])
        kom += [dict(tekst=v if isinstance(v, Markup) else escape(str(v)),
                     klasa={"c": "c", "r": "num"}.get(wyrown.get(c), ""), colspan=1) for c, v in r.items()]
        wiersze.append(dict(klasa="", komorki=kom))
    return dict(id=id_, numer=numer, tytul=tytul, kolumny=kol, wiersze=wiersze, uwagi=[], zrodlo=None, klasa="",
                szerokosci=szerokosci)


def _svg_inline(s: str) -> str:
    s = re.sub(r"<\?xml[^>]*\?>", "", s)
    s = re.sub(r"<!DOCTYPE[^>]*>", "", s)
    return s.strip()


def stempluj_arkusz(page: pymupdf.Page, tekst: str = STATUS_PRZYKLAD, drugi: str = DANE_PRZYKLADOWE):
    """Znak statusu na arkuszu — pionowo w lewym marginesie na oprawę (pas 0–8 mm od krawędzi), w górnej części
    arkusza: poza ramką, siatką odniesień (litery ~13–17 mm), odcinkiem kontrolnym i znakiem centrującym
    (wektorowo, czcionka osadzona)."""
    H = page.rect.height
    page.insert_font(fontname="lsb", fontfile=FONT_BOLD)
    page.insert_font(fontname="lsr", fontfile=FONT_REG)
    fb, fr = pymupdf.Font(fontfile=FONT_BOLD), pymupdf.Font(fontfile=FONT_REG)
    s1, s2 = 8.0, 6.2
    w1, w2 = fb.text_length(tekst, s1), fr.text_length(drugi, s2)
    x = 6.2 * MM
    y0 = min(14 * MM + w1 + 3 * MM + w2, H / 2 - 12 * MM)   # koniec tekstu nad znakiem centrującym
    page.insert_text((x, y0), tekst, fontname="lsb", fontsize=s1, color=(0.64, 0.15, 0.16), rotate=90)
    page.insert_text((x, y0 - w1 - 3 * MM), drugi, fontname="lsr", fontsize=s2, color=(0.52, 0.10, 0.11), rotate=90)
    uzupelnij_metryke(page)


WIERSZE_METRYKI = ("Projektant", "Sprawdzający", "Opracował")


def metryka_arkusza(page: pymupdf.Page) -> list[dict]:
    """Wiersze metryki arkusza (tabliczka ``lamela.draft``: kolumny „IMIĘ I NAZWISKO”, „SPECJALNOŚĆ, NR UPRAWNIEŃ”,
    „DATA”; RPB § 10 ust. 1 pkt 3) — ``[{funkcja, rect, x_nazw, x_spec, x_data, pusty}]``; [] gdy brak tabliczki."""
    w = page.get_text("words")
    hdr = next((x for i, x in enumerate(w) if x[4] == "IMIĘ" and i + 2 < len(w) and w[i + 2][4].startswith("NAZWISKO")), None)
    spec = next((x for x in w if x[4].startswith("SPECJALNO") and hdr and abs(x[1] - hdr[1]) < 3), None)
    if hdr is None or spec is None:
        return []
    data = next((x for x in w if x[4] == "DATA" and abs(x[1] - hdr[1]) < 3 and x[0] > spec[0]), None)
    ym = (hdr[1] + hdr[3]) / 2
    pion = sorted({round(a.x, 1) for d in page.get_drawings() for it in d["items"] if it[0] == "l"
                   for a, b in [(it[1], it[2])] if abs(a.x - b.x) < 0.3 and min(a.y, b.y) - 0.5 <= ym <= max(a.y, b.y) + 0.5}
                  | {round(x, 1) for d in page.get_drawings() for it in d["items"] if it[0] == "re"
                     for r in [it[1]] if r.y0 - 0.5 <= ym <= r.y1 + 0.5 for x in (r.x0, r.x1)})

    def granice(x0, x1):          # kolumna tabliczki zawierająca nagłówek [x0, x1] (linie pionowe rysunku)
        lewe, prawe = [v for v in pion if v <= x0 + 0.5], [v for v in pion if v >= x1 - 0.5]
        return (lewe[-1] if lewe else x0 - 2), (prawe[0] if prawe else x1 + 2)
    x_nazw, _ = granice(hdr[0], w[w.index(hdr) + 2][2])
    x_spec, x_data = granice(spec[0], spec[2] + 40 if not data else data[0] - 1)
    if data is not None:
        x_data = granice(data[0], data[2])[0]
    out = []
    for x in w:
        if x[4] in WIERSZE_METRYKI and hdr[3] < x[1] < hdr[3] + 90 and x[2] <= x_nazw + 1:
            y0, y1 = x[1] - 1.5, x[3] + 1.5
            zajety = any(x_nazw + 0.5 <= v[0] < x_data - 0.5 and v[1] < y1 and v[3] > y0 for v in w)
            out.append(dict(funkcja=x[4], rect=pymupdf.Rect(x[:4]), x_nazw=x_nazw, x_spec=x_spec, x_data=x_data,
                            pusty=not zajety))
    return out


def uzupelnij_metryke(page: pymupdf.Page) -> int:
    """Wpisuje w puste pola metryki arkusza znaczniki zamiast pozostawiania ich pustych (RPB § 10 ust. 1 pkt 3):
    projektant / opracował — ``[DO UZUPEŁNIENIA: …]``; sprawdzający — „nie dotyczy (art. 20 ust. 3 pkt 2 PB)”
    (budynek mieszkalny jednorodzinny). Zwraca liczbę uzupełnionych wierszy."""
    rows = [r for r in metryka_arkusza(page) if r["pusty"]]
    if not rows:
        return 0
    page.insert_font(fontname="lsr", fontfile=FONT_REG)
    f = pymupdf.Font(fontfile=FONT_REG)
    for r in rows:
        if r["funkcja"] == "Sprawdzający":
            t1, t2 = "nie dotyczy", "art. 20 ust. 3 pkt 2 PB"
        else:
            t1, t2 = do_uzup("imię i nazwisko"), do_uzup("specjalność, nr uprawnień")
        y = r["rect"].y1 - 1.2
        for t, x0, x1 in ((t1, r["x_nazw"], r["x_spec"]), (t2, r["x_spec"], r["x_data"])):
            s = min(5.5, 0.92 * (x1 - x0 - 3) / max(f.text_length(t, 1), 1e-6))
            page.insert_text((x0 + 1.5, y), t, fontname="lsr", fontsize=s, color=(0.36, 0.28, 0.0))
    return len(rows)


def _strony_zastepcze(arkusze: list[Arkusz], dok: Dokument) -> bytes:
    """Strony zastępcze dla arkuszy bez pliku (format arkusza, ramka, metryka skrócona, znacznik)."""
    from .formaty import rozmiar_formatu
    css, body = [], []
    for i, a in enumerate(arkusze):
        try:
            s, l = rozmiar_formatu(a.format or "A3")
        except ValueError:
            s, l = rozmiar_formatu("A3")
        W, H = (l, s) if (a.format or "A3").upper() != "A4" else (s, l)
        css.append(f"@page z{i} {{ size: {W}mm {H}mm; margin: 0 }}")
        body.append(f"""<section style="page: z{i}; width:{W}mm; height:{H}mm; position:relative; break-after: page">
          <div style="position:absolute; left:20mm; top:10mm; right:10mm; bottom:10mm; border:0.7mm solid #1c2229">
            <div style="position:absolute; left:0; right:0; top:38%; text-align:center; font-family:'Liberation Sans'">
              <div style="font-size:9pt; letter-spacing:0.12em; color:#5b6672">ARKUSZ ZASTĘPCZY — RYSUNEK NIEDOŁĄCZONY</div>
              <div style="font-size:20pt; font-weight:bold; margin:4mm 0 2mm">{escape(a.nr)} · {escape(a.tytul)}</div>
              <div style="font-size:11pt">skala {escape(a.skala or '—')} · format {escape(a.format or 'A3')}</div>
              <div style="font-size:10pt; margin-top:6mm"><span class="zn zn-uzup">{escape(do_uzup('rysunek ' + a.nr + ' — ' + (a.uwagi or 'arkusz do wygenerowania z modelu')))}</span></div>
            </div>
            <div style="position:absolute; right:0; bottom:0; width:180mm; border-top:0.5mm solid #1c2229; border-left:0.5mm solid #1c2229;
                        font:8pt 'Liberation Sans'; padding:2mm 3mm">{escape(dok.dane['obiekt'])}<br><b>{escape(a.nr)}</b> · {escape(a.tytul)} · {escape(a.skala or '—')}</div>
          </div></section>""")
    h = (f"<!doctype html><html lang=pl><head><meta charset=utf-8><style>{' '.join(css)} body{{margin:0}}"
         ".zn-uzup{background:#fff0b3;color:#5c4700;border-bottom:0.6pt dashed #b48a00;padding:0 1mm}</style></head><body>"
         + "".join(body) + "</body></html>")
    return R.html_na_pdf(h)


def _metadane(doc: pymupdf.Document, *, tytul: str, dane: dict, temat: str, przyklad: bool, projektanci=None,
              slowa: str = ""):
    autorzy = [p.imie_nazwisko for p in (projektanci or dane.get("projektanci", []))
               if "DO UZUPEŁNIENIA" not in p.imie_nazwisko]
    autor = "; ".join(autorzy) if autorzy else do_uzup("autorzy projektu")
    if przyklad:
        tytul = f"{tytul} ({STATUS_PRZYKLAD})"
    doc.set_metadata({
        "title": tytul, "author": autor, "subject": f"{temat}; {dane.get('lokalizacja', '')}; "
                                                    f"kategoria obiektu {dane.get('kategoria', 'I')}",
        "keywords": "; ".join(k for k in ["projekt budowlany", "RPB Dz.U. 2022 poz. 1679 ze zm.", dane.get("nazwa_krotka", ""),
                                          f"kategoria {dane.get('kategoria', 'I')}", slowa,
                                          STATUS_PRZYKLAD if przyklad else ""] if k),
        "creator": "lamela.dokumenty (Chromium + PyMuPDF)", "producer": f"PyMuPDF {pymupdf.VersionBind}",
        "creationDate": pymupdf.get_pdf_now(), "modDate": pymupdf.get_pdf_now(),
    })
    try:
        doc.set_pagemode("UseOutlines")
    except Exception:
        pass
