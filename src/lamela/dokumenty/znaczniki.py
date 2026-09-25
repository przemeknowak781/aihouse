"""Znaczniki danych wg rejestru wymagań, sekcja E.1 (docs/10_podstawy_prawne/00_rejestr_wymagan.md).

* ``[DO UZUPEŁNIENIA: <co>]`` — pole bez danych (dane osobowe, nr uprawnień, podpisy, daty decyzji…),
* ``[DANE PRZYKŁADOWE – FIKCYJNE]`` — wartość przyjęta dla przykładu (działka, MPZP, grunt, sieci),
* ``[DOKUMENT ZEWNĘTRZNY – do dołączenia: <nazwa, organ, podstawa>]`` — strona zastępcza dokumentu organu/gestora,
* ``[ZAŁ]`` / ``[NZW]`` / ``[INT]`` / ``[PROG]`` — założenie / wartość niezweryfikowana / interpretacja / program.

Status dokumentu w wersji przykładowej: **„PRZYKŁAD – NIE DO ZŁOŻENIA”** (strona tytułowa, stopka każdej strony).
Walidator (``walidator.py``) blokuje status „do złożenia”, dopóki w pliku jest choć jeden znacznik
``[DO UZUPEŁNIENIA …]`` lub ``[DOKUMENT ZEWNĘTRZNY …]`` (rejestr E.1, reguła AUD-RYS).
"""
from __future__ import annotations

import re
from collections import Counter

STATUS_PRZYKLAD = "PRZYKŁAD – NIE DO ZŁOŻENIA"
DANE_PRZYKLADOWE = "[DANE PRZYKŁADOWE – FIKCYJNE]"
ZAL = "[ZAŁ]"
NZW = "[NZW]"
INT = "[INT]"
PROG = "[PROG]"
SPRAWDZAJACY_ND = "nie dotyczy (art. 20 ust. 3 pkt 2 PB)"


def do_uzup(co: str = "") -> str:
    """``[DO UZUPEŁNIENIA: co]`` — pole do wypełnienia danymi rzeczywistymi (nigdy nie fabrykujemy danych osób)."""
    return f"[DO UZUPEŁNIENIA: {co}]" if co else "[DO UZUPEŁNIENIA]"


def dok_zewn(opis: str) -> str:
    """``[DOKUMENT ZEWNĘTRZNY – do dołączenia: opis]`` — miejsce na dokument wydany przez organ lub gestora."""
    return f"[DOKUMENT ZEWNĘTRZNY – do dołączenia: {opis}]"


# kolejność alternatyw: dłuższe najpierw
RE_ZNACZNIK = re.compile(
    r"\[(?P<typ>DO UZUPEŁNIENIA|DOKUMENT ZEWNĘTRZNY|DANE PRZYKŁADOWE)(?P<reszta>[^\[\]]*)\]"
    r"|\[(?P<krotki>ZAŁ|NZW|INT|PROG)\]")

_KLASY = {"DO UZUPEŁNIENIA": "zn-uzup", "DOKUMENT ZEWNĘTRZNY": "zn-zewn", "DANE PRZYKŁADOWE": "zn-przykl"}
_RE_TAG = re.compile(r"(<[^>]*>)")


def _span(m: re.Match) -> str:
    if m.group("krotki"):
        return f'<span class="zn zn-status">{m.group(0)}</span>'
    return f'<span class="zn {_KLASY[m.group("typ")]}">{m.group(0)}</span>'


def oznacz_html(html: str) -> str:
    """Otacza znaczniki w węzłach tekstowych HTML elementem ``<span class="zn …">`` (wyróżnienie w druku).
    Tekst wewnątrz znaczników ``<style>``/``<script>`` i atrybuty pozostają bez zmian."""
    out, skip = [], False
    for part in _RE_TAG.split(html):
        if part.startswith("<"):
            low = part[:8].lower()
            if low.startswith(("<style", "<script", "<title")):
                skip = True
            elif low.startswith(("</style", "</scrip", "</title")):
                skip = False
            out.append(part)
        elif skip or "[" not in part:
            out.append(part)
        else:
            out.append(RE_ZNACZNIK.sub(_span, part))
    return "".join(out)


_RE_IDX = re.compile(r"([_^])\{([^{}<>]{1,24})\}")


def indeksy_html(html: str) -> str:
    """Zapis indeksów w tekście: ``R_{si}`` → R<sub>si</sub>, ``m^{2}`` → m<sup>2</sup> (węzły tekstowe HTML,
    poza ``<style>``/``<script>``)."""
    out, skip = [], False
    for part in _RE_TAG.split(html):
        if part.startswith("<"):
            low = part[:8].lower()
            if low.startswith(("<style", "<script", "<title")):
                skip = True
            elif low.startswith(("</style", "</scrip", "</title")):
                skip = False
            out.append(part)
        elif skip or "{" not in part:
            out.append(part)
        else:
            out.append(_RE_IDX.sub(lambda m: f"<{'sub' if m.group(1) == '_' else 'sup'}>{m.group(2)}"
                                             f"</{'sub' if m.group(1) == '_' else 'sup'}>", part))
    return "".join(out)


def bez_indeksow(tekst: str) -> str:
    """``R_{si}`` → ``Rsi`` (zakładki PDF, metadane)."""
    return _RE_IDX.sub(lambda m: m.group(2), tekst)


def policz_znaczniki(tekst: str) -> dict:
    """Zlicza znaczniki w tekście (np. wyciągniętym z PDF). Zwraca
    ``{"DO UZUPEŁNIENIA": n, "DOKUMENT ZEWNĘTRZNY": n, "DANE PRZYKŁADOWE": n, "ZAŁ": n, "NZW": n, …,
    "lista": Counter(pełny tekst znacznika → liczba)}``."""
    t = re.sub(r"-\n(?=\w)", "", tekst)       # przeniesienia w tekście z PDF
    t = re.sub(r"\s*\n\s*", " ", t)
    c: Counter = Counter()
    lista: Counter = Counter()
    for m in RE_ZNACZNIK.finditer(t):
        typ = m.group("typ") or m.group("krotki")
        c[typ] += 1
        lista[re.sub(r"\s+", " ", m.group(0))] += 1
    wynik = {k: c.get(k, 0) for k in ("DO UZUPEŁNIENIA", "DOKUMENT ZEWNĘTRZNY", "DANE PRZYKŁADOWE",
                                       "ZAŁ", "NZW", "INT", "PROG")}
    wynik["lista"] = lista
    return wynik


def blokuje_zlozenie(liczniki: dict) -> bool:
    """True, gdy w dokumencie pozostały pola do uzupełnienia lub strony zastępcze dokumentów zewnętrznych."""
    return bool(liczniki.get("DO UZUPEŁNIENIA") or liczniki.get("DOKUMENT ZEWNĘTRZNY"))
