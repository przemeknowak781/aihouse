"""Zapis równoległy: każde wywołanie treści ``Dokument`` (lamela.dokumenty) jest odwzorowane w źródle Markdown.

``Zapis(dok)`` przekazuje wywołania do obiektu ``Dokument`` i jednocześnie buduje tekst ``.md`` (źródło elementu
w repozytorium — przegląd zmian w diff, bez PDF). Bloki formalne (oświadczenia, strona zastępcza, informacja BIOZ)
zapisuje w MD skrótem z odesłaniem do PDF — ich treść pochodzi z ``lamela.dokumenty.bloki``.
"""
from __future__ import annotations

import re
import textwrap

from lamela.dokumenty import liczba


def _txt(v, nd=2) -> str:
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, (int, float)):
        return liczba(v, nd)
    s = str(v if v is not None else "—")
    s = re.sub(r"<[^>]+>", "", s)                      # Markup → tekst
    return s.replace("|", "\\|").replace("\n", " ")


class Zapis:
    """Opakowanie ``Dokument`` z rejestracją treści w Markdown (``self.md``)."""

    def __init__(self, dok, tytul_md: str | None = None):
        self.dok = dok
        self._n = [0, 0, 0]
        self._n_tab = 0
        self.linie: list[str] = [f"# {tytul_md or dok.tytul}", "",
                                 f"*Źródło Markdown elementu {dok.kod} — generowane przez "
                                 f"`tools/dokumenty/tom_I_pzt_zl.py`; wersja wiążąca: PDF.*", ""]

    # ------------------------------------------------------------------ pomocnicze
    def _dodaj(self, *linie):
        self.linie.extend(linie)

    @property
    def md(self) -> str:
        return "\n".join(self.linie).rstrip() + "\n"

    def _nagl(self, tytul, poziom=1, podstawa=None):
        self._n[poziom - 1] += 1
        for i in range(poziom, 3):
            self._n[i] = 0
        nr = ".".join(str(n) for n in self._n[:poziom]) + "."
        pod = f" *({podstawa})*" if podstawa else ""
        self._dodaj("#" * (poziom + 1) + f" {nr} {tytul}{pod}", "")

    # ------------------------------------------------------------------ struktura
    def czesc_opisowa(self, tytul, **kw):
        self.dok.czesc_opisowa(tytul, **kw)
        self._n = [0, 0, 0]
        pod = f" *({kw['podstawa']})*" if kw.get("podstawa") else ""
        self._dodaj(f"## {tytul}{pod}", "")
        return self

    def rozdzial(self, tytul, tresc=None, *, poziom=1, podstawa=None, **kw):
        self.dok.rozdzial(tytul, poziom=poziom, podstawa=podstawa, **kw)
        self._nagl(tytul, poziom, podstawa)
        if tresc:
            self.markdown(tresc)
        return self

    def markdown(self, tekst):
        """Treść Markdown; nagłówki ``##`` w treści = podrozdziały (numeracja jak w ``Dokument.markdown``)."""
        tekst = textwrap.dedent(tekst).strip("\n")
        czesci = re.split(r"^(#{1,4})[ \t]+(.+?)[ \t]*$", tekst, flags=re.M)
        self.dok.markdown(tekst)
        self._dodaj(czesci[0].strip(), "")
        for i in range(1, len(czesci), 3):
            tyt = czesci[i + 1]
            m = re.match(r"(.*?)\s*\{podstawa:\s*(.+)\}\s*$", tyt)
            self._nagl(m.group(1) if m else tyt, len(czesci[i]), m.group(2) if m else None)
            self._dodaj(czesci[i + 2].strip(), "")
        return self

    def wniosek(self, tekst, **kw):
        self.dok.wniosek(tekst, **kw)
        self._dodaj("> " + tekst.replace("\n", " "), "")
        return self

    def zalacznik(self, tytul, **kw):
        self.dok.zalacznik(tytul, **kw)
        self._n = [0, 0, 0]
        self._dodaj(f"## Załącznik — {tytul}", "")
        return self

    # ------------------------------------------------------------------ tabele
    def _tab_md(self, tytul, kolumny, wiersze, uwagi=None, zrodlo=None):
        self._n_tab += 1
        if tytul:
            self._dodaj(f"**Tabela {self._n_tab}. {tytul}**", "")
        self._dodaj("| " + " | ".join(kolumny) + " |", "|" + "---|" * len(kolumny))
        for w in wiersze:
            if isinstance(w, str):
                self._dodaj(f"| **{_txt(w)}** |" + " |" * (len(kolumny) - 1))
            else:
                self._dodaj("| " + " | ".join(_txt(w.get(k)) for k in kolumny) + " |")
        self._dodaj("")
        for u in uwagi or []:
            self._dodaj(f"*Uwaga: {_txt(u)}*", "")
        if zrodlo:
            self._dodaj(f"*Źródło: {_txt(zrodlo)}*", "")

    def tabela(self, dane, kolumny=None, **kw):
        self.dok.tabela(dane, kolumny, **kw)
        kol = kolumny or next((list(k for k in w if not k.startswith("_")) for w in dane if isinstance(w, dict)), [])
        self._tab_md(kw.get("tytul"), kol, dane, kw.get("uwagi"), kw.get("zrodlo"))
        return self

    def tabela_wynikow(self, wiersze, **kw):
        self.dok.tabela_wynikow(wiersze, **kw)
        rows = [{"Parametr": w["parametr"], "Wartość": (_txt(w["wartosc"]) + (" " + w.get("jedn", "") if w.get("jedn") else "")),
                 "Wymaganie": w.get("wymaganie"), "Podstawa": w.get("podstawa"),
                 "Ocena": {True: "spełnia", False: "NIE SPEŁNIA", None: "—"}.get(w.get("spelnia"), "—")} for w in wiersze]
        self._tab_md(kw.get("tytul", "Zestawienie wyników sprawdzenia"), list(rows[0]) if rows else [], rows,
                     kw.get("uwagi"), kw.get("zrodlo"))
        return self

    # ------------------------------------------------------------------ bloki formalne (skrót w MD)
    def blok(self, nazwa_md: str, metoda: str, *a, **kw):
        getattr(self.dok, metoda)(*a, **kw)
        self._dodaj(f"*[{nazwa_md} — blok formalny `lamela.dokumenty` ({metoda}); pełna treść w PDF]*", "")
        return self

    def czesc_rysunkowa(self, arkusze, **kw):
        self.dok.czesc_rysunkowa(arkusze, **kw)
        self._dodaj("## Część rysunkowa — wykaz rysunków", "", "| Nr | Tytuł | Skala | Format |", "|---|---|---|---|")
        for a in self.dok.arkusze:
            self._dodaj(f"| {a.nr} | {_txt(a.tytul)} | {a.skala or '—'} | {a.format or '—'} |")
        self._dodaj("")
        return self
