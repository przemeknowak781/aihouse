"""CLI: obliczenia statyczne z modelu budynku.

    PYTHONPATH=src python3 -m lamela.obliczenia.konstrukcja MODEL.yaml [DZIALKA.yaml] --out KATALOG [--status TEKST]
        [--siatka 0.2] [--bez-html] [--wymagania docs/10_podstawy_prawne/wymagania.yaml]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from lamela.model import load_model

from .pozycje import AnalizaKonstrukcji
from .raport import generuj_raport
from .wspolne import Parametry


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lamela.obliczenia.konstrukcja", description="Obliczenia statyczne (Eurokody + NA)")
    ap.add_argument("budynek")
    ap.add_argument("dzialka", nargs="?")
    ap.add_argument("--out", required=True)
    ap.add_argument("--status", default=None, help="napis statusu dokumentu (np. PRZYKŁAD – NIE DO ZŁOŻENIA)")
    ap.add_argument("--tytul", default=None)
    ap.add_argument("--siatka", type=float, default=None, help="bok elementu MES płyt [m] (domyślnie 0,20)")
    ap.add_argument("--wymagania", default=None, help="ścieżka wymagania.yaml (domyślnie z repozytorium)")
    ap.add_argument("--bez-html", action="store_true")
    ap.add_argument("--nie-strict", action="store_true", help="nie przerywać przy błędach walidacji modelu")
    ap.add_argument("--scisle", action="store_true", help="błąd dowolnego etapu analizy przerywa obliczenia (debug)")
    a = ap.parse_args(argv)
    t0 = time.time()
    m = load_model(a.budynek, a.dzialka, strict=not a.nie_strict)
    p = Parametry.z_wymagan(a.wymagania)
    if a.siatka:
        p.siatka_mes = a.siatka
    out = Path(a.out)
    an = AnalizaKonstrukcji(m, p, rys_dir=out / "rys").uruchom(scisle=a.scisle)
    f = generuj_raport(an, out, tytul=a.tytul, status=a.status, html=not a.bez_html)
    n = sum(len(g.podpozycje) for g in an.pozycje)
    nok = sum(1 for g in an.pozycje for pz in g.podpozycje if not pz.ok)
    print(f"Raport: {f}  ({n} pozycji, niespełnione: {nok}, czas {time.time() - t0:.0f} s)")
    for g in an.pozycje:
        for pz in g.podpozycje:
            if not pz.ok:
                print(f"  ✗ Poz. {pz.nr} {pz.ident}: η = {pz.wykorzystanie * 100:.0f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
