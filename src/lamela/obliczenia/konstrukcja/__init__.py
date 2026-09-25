"""Biblioteka obliczeń konstrukcyjnych „Dom LAMELA” — Eurokody 1. generacji + załączniki krajowe PL.

Moduły: ``wspolne`` (kroki, wyniki, parametry projektu), ``materialy`` (beton, stal, mur, kształtowniki), ``obciazenia``
(ciężary warstw, użytkowe, śnieg, wiatr, kombinacje), ``statyka`` (belki MES), ``plyty`` (tablice współczynników, MES
płytowy), ``zelbet``, ``mur``, ``stal``, ``fundamenty``, ``schody``, ``pozycje`` (ścieżka obciążeń z modelu),
``rysunki``, ``raport``. Szczegóły: ``README.md`` w tym katalogu.

Szybki start::

    from lamela.model import load_model
    from lamela.obliczenia.konstrukcja import AnalizaKonstrukcji, generuj_raport, Parametry
    m = load_model("model/budynek.yaml", "model/dzialka.yaml")
    an = AnalizaKonstrukcji(m, Parametry.z_wymagan(), rys_dir="out/rys").uruchom()
    generuj_raport(an, "out")
"""
from .wspolne import Grunt, Krok, Parametry, Warunek, Wynik  # noqa: F401
from .materialy import Beton, Mur, StalKonstr, StalZbrojeniowa, przekroj  # noqa: F401
from .pozycje import AnalizaKonstrukcji, Pozycja  # noqa: F401
from .raport import generuj_raport  # noqa: F401

__version__ = "1.0"
