"""``lamela.dokumenty`` — składanie części opisowej i tomów projektu budowlanego „Dom LAMELA”.

Zgodność: rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego (RPB, t.j. Dz.U. 2022
poz. 1679 ze zm.) — strona tytułowa (§ 7 ust. 2), spis treści z numerami stron (§ 7 ust. 5), numeracja odrębna
dla elementu (§ 6), postać elektroniczna PDF ≤ 150 MB z częścią rysunkową wektorową (§ 2b), nazwy plików wg zał. 1;
oświadczenia z art. 34 ust. 3d pkt 3, art. 33 ust. 2 pkt 10, art. 102a PB; informacja BIOZ (Dz.U. 2003 nr 120
poz. 1126). Konwencja znaczników danych: rejestr wymagań, sekcja E.1. Opis: ``README.md`` w tym katalogu.

Szybki start::

    from lamela.dokumenty import dane_obiektu, Dokument, Tom, Arkusz, sprawdz_tom, LISTY_KONTROLNE
    d = dane_obiektu()                                   # model/budynek.yaml + model/dzialka.yaml (lub brief)
    pzt = Dokument("Projekt zagospodarowania działki", "PZT", d)
    pzt.oswiadczenie_projektanta()
    pzt.czesc_opisowa("Opis techniczny")
    pzt.rozdzial("Przedmiot zamierzenia", "…", podstawa="§ 14 pkt 1 RPB")
    pzt.czesc_rysunkowa([Arkusz.z_pdf("PZT-01.pdf")])
    tom = Tom("TOM I", [pzt, pab, zl], dane=d)
    wynik = tom.zloz("projekt/…/")                      # → PZT_PAB_ZL_rrrr.mm.dd.pdf
    raport = sprawdz_tom(wynik.sciezka, LISTY_KONTROLNE["TOM_I"])
"""
from .znaczniki import (STATUS_PRZYKLAD, DANE_PRZYKLADOWE, ZAL, NZW, do_uzup, dok_zewn, policz_znaczniki,
                        oznacz_html, blokuje_zlozenie)
from .formaty import liczba, rzedna, data_slownie, data_pliku, wykryj_format
from .dane import dane_obiektu, Projektant, projektanci_domyslni, SPECJALNOSCI, ELEMENTY
from .nazwy import nazwa_pliku, sprawdz_nazwe
from .arkusze import Arkusz, arkusze_z_katalogu, plan_skladania
from .dokument import Dokument, WynikDokumentu
from .tom import Tom, WynikTomu
from .walidator import sprawdz_tom, LISTY_KONTROLNE, RaportKompletnosci
from .render import zamknij_przegladarke

__all__ = [
    "STATUS_PRZYKLAD", "DANE_PRZYKLADOWE", "ZAL", "NZW", "do_uzup", "dok_zewn", "policz_znaczniki", "oznacz_html",
    "blokuje_zlozenie", "liczba", "rzedna", "data_slownie", "data_pliku", "wykryj_format", "dane_obiektu",
    "Projektant", "projektanci_domyslni", "SPECJALNOSCI", "ELEMENTY", "nazwa_pliku", "sprawdz_nazwe", "Arkusz",
    "arkusze_z_katalogu", "plan_skladania", "Dokument", "WynikDokumentu", "Tom", "WynikTomu", "sprawdz_tom",
    "LISTY_KONTROLNE", "RaportKompletnosci", "zamknij_przegladarke",
]
