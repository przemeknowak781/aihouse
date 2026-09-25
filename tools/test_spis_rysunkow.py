#!/usr/bin/env python3
"""Test spisu rysunków tomu (``lamela.draft.plot.spisy_rysunkow``): krótki spis — jedna strona A4; długi spis
(np. 27 arkuszy PT-BO z tytułami łamanymi w dwóch wierszach) — kolejne strony A4 z tytułem „… (k/n)” i polem
„arkusz” k/n, a suma wysokości wierszy każdej strony mieści się nad tabliczką.

Użycie: PYTHONPATH=src python3 tools/test_spis_rysunkow.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.draft import plot  # noqa: E402
from lamela.draft.sheet import Sheet, TitleBlock  # noqa: E402

TYTULY = ["RZUT FUNDAMENTÓW", "PRZEKROJE CHARAKTERYSTYCZNE FUNDAMENTU", "ZBROJENIE DOLNE PŁYTY FUNDAMENTOWEJ",
          "ZBROJENIE GÓRNE PŁYTY FUNDAMENTOWEJ", "WĘZŁY WSPORNIKÓW Z ŁĄCZNIKAMI TERMOIZOLACYJNYMI",
          "WIENIEC I OPARCIE STROPU NA MURZE SILIKATOWYM", "ZBROJENIE SŁUPÓW ŻELBETOWYCH W MURZE"]


def arkusze(n: int) -> list[Sheet]:
    return [Sheet("A3", title_block=TitleBlock(tytul=TYTULY[i % len(TYTULY)], nr_rysunku=f"PT-BO-{i + 1:02d}",
                                               skala="1:50")) for i in range(n)]


def main() -> int:
    bledy = []
    tb = TitleBlock(tytul="SPIS RYSUNKÓW", nr_rysunku="PT-BO-00", skala="—")
    krotki = plot.spisy_rysunkow(arkusze(8), "Projekt techniczny — konstrukcja (rysunki)", tb)
    if len(krotki) != 1 or krotki[0].tb.tytul != "SPIS RYSUNKÓW":
        bledy.append(f"krótki spis: {len(krotki)} stron, tytuł {krotki[0].tb.tytul!r}")
    dlugi = plot.spisy_rysunkow(arkusze(27), "Projekt techniczny — konstrukcja (rysunki)", tb)
    n = len(dlugi)
    if n < 2:
        bledy.append(f"długi spis (27 arkuszy, tytuły dwuwierszowe) na {n} stronie — tabela wchodzi na tabliczkę")
    for k, sh in enumerate(dlugi, 1):
        if sh.tb.tytul != f"SPIS RYSUNKÓW ({k}/{n})" or sh.tb.arkusz != f"{k}/{n}":
            bledy.append(f"strona {k}: tytuł {sh.tb.tytul!r}, arkusz {sh.tb.arkusz!r}")
    if plot.spis_rysunkow(arkusze(27), "T", tb).tb.tytul != f"SPIS RYSUNKÓW (1/{n})":
        bledy.append("spis_rysunkow (zgodność wsteczna) nie zwraca pierwszej strony")
    if tb.tytul != "SPIS RYSUNKÓW":
        bledy.append("tabliczka wejściowa została zmieniona w miejscu")
    for b in bledy:
        print("BŁĄD ", b)
    print(f"{'ZALICZONE' if not bledy else 'NIEZALICZONE'}: krótki spis {len(krotki)} str., długi spis {n} str.")
    return 1 if bledy else 0


if __name__ == "__main__":
    sys.exit(main())
