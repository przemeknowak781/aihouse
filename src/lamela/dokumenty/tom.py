"""``Tom`` — plik projektu w postaci elektronicznej (RPB § 5 ust. 1a, 2, 2a: każdy plik = osobny tom).

Składa elementy (``Dokument``, gotowe PDF, arkusze) w jeden PDF:
* opcjonalna wspólna strona tytułowa tomu i **łączny spis treści** (RPB § 7 ust. 7 pkt 1; nie obejmuje PT — ust. 8),
* zakładki (outline) dla każdego elementu, rozdziału i rysunku; etykiety stron (np. „PZT s. 3”, „PB-AR-01”),
* metadane (Title, Author, Subject, Keywords), tryb otwarcia z panelem zakładek,
* kontrola rozmiaru ≤ 150 MB (RPB § 2b ust. 3) i nazwy wg zał. 1 RPB (``nazwy.py``),
* blokada wspólnej oprawy PT z innymi elementami w postaci elektronicznej (RPB § 5 ust. 3).

Arkusze pozostają w formatach oryginalnych (plik elektroniczny). Wersja papierowa: składanie do A4 — ``plan_skladania``.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf
from markupsafe import escape

from . import render as R
from .arkusze import Arkusz
from .dane import dane_obiektu, ELEMENTY, SPECJALNOSCI
from .dokument import Dokument, WynikDokumentu, _env, _metadane, _plain, stempluj_arkusz, GRUPY
from .formaty import data_iso, data_slownie, odmiana
from .nazwy import nazwa_pliku, sprawdz_nazwe
from .znaczniki import STATUS_PRZYKLAD, oznacz_html, indeksy_html

URI_EL = "https://lamela.invalid/e/"
LIMIT_MB = 150.0


class PrzekroczonyRozmiar(Exception):
    pass


@dataclass
class WynikTomu:
    sciezka: Path
    nazwa: str
    rozmiar_mb: float
    strony: int
    elementy: list = field(default_factory=list)   # [{kod, tytul, start, strony_opisu, strony, arkusze}]
    zakladki: list = field(default_factory=list)
    nazwa_zgodna: bool = True
    uwagi: list = field(default_factory=list)
    arkusze: list = field(default_factory=list)    # [(Arkusz, strona w tomie)]

    @property
    def rozmiar_ok(self) -> bool:
        return self.rozmiar_mb <= LIMIT_MB


class Tom:
    """Tom projektu (jeden plik PDF).

    ``elementy`` — lista: ``Dokument`` | ścieżka PDF | ``Arkusz`` | ``(tytuł, ścieżka)``. Arkusze i PDF bez własnego
    elementu nadrzędnego dostają zakładkę najwyższego poziomu; ``zagniezdzaj_arkusze=True`` — arkusze podane
    bezpośrednio za elementem trafiają do jego zakładki.

    ``rodzaj`` — 'PZT_PAB_ZL' (domyślnie wg kodów elementów), 'PZT_PAB', 'PT', …; dla PT: ``nr`` i ``symbol``.
    """

    def __init__(self, nazwa: str = "TOM I", elementy: list | None = None, *, pliki: list | None = None,
                 dane: dict | None = None, rodzaj: str | None = None, data=None, nr: int | None = None,
                 symbol: str | None = None, tom: tuple[int, int] | None = None, przyklad: bool | None = None,
                 strona_tytulowa: bool = True, laczny_spis: bool = True, tytul: str = "Projekt budowlany",
                 podtytul: str | None = None, limit_mb: float = LIMIT_MB, zagniezdzaj_arkusze: bool = True,
                 stempel_arkuszy: bool | None = None):
        self.nazwa = nazwa
        self.elementy = list(elementy or []) + list(pliki or [])
        self.dane = dane or next((e.dane for e in self.elementy if isinstance(e, Dokument)), None) or dane_obiektu()
        self.data = data_iso(data or self.dane.get("data"))
        self.nr, self.symbol = nr, symbol
        self.tom = tom
        self.przyklad = self.dane.get("przyklad", True) if przyklad is None else przyklad
        self.strona_tytulowa = strona_tytulowa
        self.laczny_spis = laczny_spis
        self.tytul = tytul
        self.podtytul = podtytul
        self.limit_mb = limit_mb
        self.zagniezdzaj = zagniezdzaj_arkusze
        self.stempel = stempel_arkuszy
        self.rodzaj = rodzaj or self._rodzaj_domyslny()
        self.wynik: WynikTomu | None = None
        self._sprawdz_oprawe()

    # --------------------------------------------------------------------------------------------- reguły
    def _kody(self) -> list[str]:
        return [e.czesc.split("-")[0] for e in self.elementy if isinstance(e, Dokument)]

    def _rodzaj_domyslny(self) -> str:
        k = set(self._kody())
        if "PT" in k:
            return "PT"
        for r in ("PZT_PAB_ZL", "PZT_PAB", "PZT_ZL", "PAB_ZL"):
            if k == set(r.split("_")):
                return r
        return next(iter(k)) if len(k) == 1 else "PZT_PAB_ZL"

    def _sprawdz_oprawe(self):
        k = self._kody()
        if "PT" in k and (len(set(k)) > 1 or k.count("PT") > 1):
            raise ValueError("Projekt techniczny w postaci elektronicznej nie może być objęty wspólną oprawą z innymi "
                             "elementami ani innymi tomami PT — każdy tom PT to osobny plik (RPB § 5 ust. 3, zał. 1)")

    def nazwa_pliku(self) -> str:
        if self.rodzaj == "PT":
            return nazwa_pliku("PT", self.data, nr=self.nr, symbol=self.symbol)
        return nazwa_pliku(self.rodzaj, self.data, nr=self.nr)

    # --------------------------------------------------------------------------------------------- składanie
    def zloz(self, cel: str | Path, *, nazwa: str | None = None) -> WynikTomu:
        """Renderuje elementy i zapisuje tom. ``cel`` — katalog (nazwa wg zał. 1 RPB) albo pełna ścieżka pliku."""
        cel = Path(cel)
        nazwa = nazwa or (cel.name if cel.suffix.lower() == ".pdf" else self.nazwa_pliku())
        sciezka = cel if cel.suffix.lower() == ".pdf" else cel / nazwa
        sciezka.parent.mkdir(parents=True, exist_ok=True)
        czesci = self._renderuj_czesci(nazwa)
        front = self._renderuj_front(czesci, nazwa) if (self.strona_tytulowa or self.laczny_spis) else None

        out = pymupdf.open()
        zakladki, etykiety, uwagi = [], [], []
        n_front = 0
        if front is not None:
            fdoc = pymupdf.open(stream=front, filetype="pdf")
            n_front = fdoc.page_count
            out.insert_pdf(fdoc, links=True)
            fdoc.close()
            if self.strona_tytulowa:
                zakladki.append([1, f"Strona tytułowa — {self.nazwa}", 1])
            if self.laczny_spis:
                zakladki.append([1, "Łączny spis treści", 2 if self.strona_tytulowa else 1])
            etykiety.append({"startpage": 0, "prefix": f"{self.nazwa} s. ", "style": "D", "firstpagenum": 1})
        starty, elementy_info, arkusze_tomu = [], [], []
        for c in czesci:
            start = out.page_count + 1
            starty.append(start)
            src = pymupdf.open(stream=c["pdf"], filetype="pdf")
            out.insert_pdf(src, links=True, annots=True)
            src.close()
            if c.get("zagniezdzony"):
                zakladki.append([2, c["tytul_zakladki"], start])
            else:
                zakladki.append([1, c["tytul_zakladki"], start])
                for lvl, t, s in c["zakladki"]:
                    zakladki.append([lvl + 1, t, s + start - 1])
            for e in c["etykiety"]:
                etykiety.append(dict(e, startpage=e["startpage"] + start - 1))
            for a, s in c.get("arkusze", []):
                arkusze_tomu.append((a, s + start - 1))
            elementy_info.append(dict(kod=c["kod"], tytul=c["tytul"], start=start, strony=c["strony"],
                                      strony_opisu=c.get("strony_opisu", 0), arkusze=len(c.get("arkusze", []))))

        def mapa(uri: str):
            if not uri.startswith(URI_EL):
                return None
            ei, p = uri[len(URI_EL):].split("/")[:2]
            return starty[int(ei)] + int(p) - 2
        R.linki_na_goto(out, mapa)
        out.set_toc(_popraw_poziomy(zakladki))
        try:
            out.set_page_labels(etykiety)
        except Exception:
            pass
        kody = " + ".join(c["kod"] for c in czesci if not c.get("zagniezdzony"))
        _metadane(out, tytul=f"{self.dane['nazwa_krotka']} — {self.nazwa}: {kody}", dane=self.dane,
                  temat=f"{self.tytul} — {kody} — {self.dane['obiekt']}", przyklad=self.przyklad,
                  slowa=kody.replace(" + ", "; "))
        out.save(str(sciezka), garbage=3, deflate=True, deflate_fonts=True)
        n = out.page_count
        out.close()
        mb = R.rozmiar_mb(sciezka)
        ok_n, opis_n = sprawdz_nazwe(sciezka.name, self.rodzaj)
        if not ok_n:
            uwagi.append(opis_n)
        if mb > self.limit_mb:
            raise PrzekroczonyRozmiar(f"{sciezka.name}: {mb:.1f} MB > {self.limit_mb} MB (RPB § 2b ust. 3) — "
                                      "podziel tom (PZT_PAB_z + ZL_z albo PAB_x_z) lub zmniejsz rastry")
        self.wynik = WynikTomu(sciezka=sciezka, nazwa=sciezka.name, rozmiar_mb=mb, strony=n, elementy=elementy_info,
                               zakladki=zakladki, nazwa_zgodna=ok_n, uwagi=uwagi, arkusze=arkusze_tomu)
        return self.wynik

    def _renderuj_czesci(self, nazwa: str) -> list[dict]:
        dok_el = [e for e in self.elementy if isinstance(e, Dokument)]
        zaw = [dict(kod=e.kod, tytul=e.tytul, biezacy=False) for e in dok_el]
        czesci = []
        poprzedni_dok = False
        for e in self.elementy:
            if isinstance(e, Dokument):
                e.plik_tomu = nazwa
                e.zawartosc_tomu = [dict(z, biezacy=(z["kod"] == e.kod)) for z in zaw]
                if self.tom and not e.tom:
                    e.tom = self.tom
                w: WynikDokumentu = e.render_pdf()
                czesci.append(dict(kod=e.kod, tytul=e.tytul, tytul_zakladki=f"{e.kod} — {e.tytul}", pdf=w.pdf,
                                   zakladki=w.zakladki, etykiety=w.etykiety, wpisy=w.wpisy, strony=w.strony_razem,
                                   strony_opisu=w.strony_opisu, arkusze=w.arkusze, dok=e))
                poprzedni_dok = True
                continue
            if isinstance(e, tuple):
                tyt, p = e
                a = None
            elif isinstance(e, Arkusz):
                a, p, tyt = e, e.plik, e.etykieta
            else:
                p = Path(e)
                a = Arkusz.z_pdf(p) if _wyglada_na_arkusz(p) else None
                tyt = a.etykieta if a else (pymupdf.open(str(p)).metadata.get("title") or p.stem)
            doc = pymupdf.open(str(p))
            if a is not None and (self.stempel if self.stempel is not None else self.przyklad):
                for pg in doc:
                    stempluj_arkusz(pg)
            own = doc.get_toc()
            pdf = doc.tobytes(garbage=1, deflate=True)
            n = doc.page_count
            doc.close()
            zagn = bool(a is not None and self.zagniezdzaj and poprzedni_dok)
            etyk = [{"startpage": 0, "prefix": a.nr if a else _plain(tyt)[:24], "style": "" if a else "D",
                     "firstpagenum": 1}]
            czesci.append(dict(kod=a.nr if a else Path(p).stem, tytul=tyt, tytul_zakladki=tyt, pdf=pdf,
                               zakladki=[[l, t, s] for l, t, s in own], etykiety=etyk, wpisy=[], strony=n,
                               arkusze=[(a, 1)] if a else [], zagniezdzony=zagn))
        return czesci

    def _renderuj_front(self, czesci: list[dict], nazwa: str) -> bytes:
        """Strona tytułowa tomu + łączny spis treści (bez PT — § 7 ust. 8 RPB)."""
        front = Dokument(self.tytul, "TOM", self.dane, kod=self.nazwa, data=self.data, przyklad=self.przyklad,
                         spis_tresci=False, strona_tytulowa=False, tom=self.tom)
        front.plik_tomu = nazwa
        m = _env.get_template("bloki.html.j2").module
        kody = [c for c in czesci if not c.get("zagniezdzony")]
        pod = self.podtytul or " · ".join(c["tytul"] for c in kody)
        zaw = []
        for c in kody:
            opis = f"{c['strony_opisu'] or c['strony']} {odmiana(c['strony_opisu'] or c['strony'], 'strona', 'strony', 'stron')}"
            if c.get("arkusze"):
                na = len(c["arkusze"])
                opis += f" + {na} {odmiana(na, 'rysunek', 'rysunki', 'rysunków')}"
            zaw.append(dict(kod=c["kod"], tytul=f"{c['tytul']} ({opis})", biezacy=False))
        ctx = front._ctx_tytulowej()
        ctx.update(tytul=self.tytul, podtytul=pod, zawartosc_tomu=zaw,
                   tom_opis=" · ".join(x for x in [
                       f"Tom {self.tom[0]} z {self.tom[1]}" if self.tom else "",
                       f"{self.nazwa}: {' + '.join(c['kod'] for c in kody)}",
                       "wspólna oprawa elementów w jednym pliku (RPB § 5 ust. 3–4)"] if x),
                   autorzy=[dict(p.slownik(), branza=SPECJALNOSCI.get(p.branza, ("", "", p.branza))[2])
                            for p in self.dane["projektanci"]],
                   uwaga_dodatkowa="Łączny spis treści nie obejmuje projektu technicznego (§ 7 ust. 8 RPB).")
        body = []
        if front.znak_wodny:
            body.append(f'<div class="znak-wodny">{STATUS_PRZYKLAD}</div>')
        if self.strona_tytulowa:
            body.append(str(m.strona_tytulowa(self.dane, ctx)))
        if self.laczny_spis:
            wpisy = []
            for ei, c in enumerate(czesci):
                if c.get("zagniezdzony"):
                    wpisy.append(dict(poziom=2, numer=c["kod"], tytul=c["tytul"], strona="rys.", rys=True,
                                      href=f"{URI_EL}{ei}/1", grupa_naglowek=None))
                    continue
                wpisy.append(dict(poziom=1, numer=c["kod"], tytul=c["tytul"], strona="", el=True,
                                  href=f"{URI_EL}{ei}/1", grupa_naglowek=None))
                dok = c.get("dok")
                if dok is not None:
                    if dok.strona_tytulowa_wl:
                        wpisy.append(dict(poziom=2, numer="", tytul="Strona tytułowa", strona="1",
                                          href=f"{URI_EL}{ei}/1", grupa_naglowek=None))
                    if dok.spis_wl:
                        sp = 2 if dok.strona_tytulowa_wl else 1
                        wpisy.append(dict(poziom=2, numer="", tytul=dok.tytul_spisu, strona=str(sp),
                                          href=f"{URI_EL}{ei}/{sp}", grupa_naglowek=None))
                for w in c["wpisy"]:
                    if w["poziom"] > 2 or not w.get("strona"):
                        continue
                    wpisy.append(dict(poziom=min(w["poziom"] + 1, 3), numer=w["numer"], tytul=w["tytul"],
                                      rys=w.get("rys"), strona="rys." if w.get("rys") else str(w["strona"]),
                                      href=f"{URI_EL}{ei}/{w['strona']}", grupa_naglowek=None))
            leg = ("Numeracja stron odrębna dla każdego elementu projektu (§ 6 ust. 1 RPB); rysunki oznaczono numerem "
                   "rysunku (§ 6 ust. 3 RPB). Pozycje spisu są odnośnikami do stron pliku. Projekt techniczny nie jest "
                   "objęty łącznym spisem (§ 7 ust. 8 RPB).")
            body.append(str(m.spis(dict(tytul="Łączny spis treści", wpisy=wpisy, legenda=leg,
                                        podstawa=f"{self.nazwa} — § 7 ust. 7 pkt 1 RPB"))))
        tyt = escape(f"{self.dane['nazwa_krotka']} — {self.nazwa}")
        html = (f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{tyt}</title>'
                f"<style>{front.css()}</style></head><body>" + "\n".join(body) + "</body></html>")
        return R.html_na_pdf(indeksy_html(oznacz_html(html)))


def _wyglada_na_arkusz(p: Path) -> bool:
    try:
        d = pymupdf.open(str(p))
        r = d[0].rect
        d.close()
        return not (abs(r.width - 595.3) < 3 and abs(r.height - 841.9) < 3)
    except Exception:
        return False


def _popraw_poziomy(z: list) -> list:
    """Zakładki PDF: pierwszy wpis na poziomie 1, każdy kolejny najwyżej o 1 głębiej od poprzedniego."""
    out, prev = [], 0
    for lvl, t, s in z:
        lvl = max(1, min(lvl, prev + 1))
        out.append([lvl, t, s])
        prev = lvl
    return out
