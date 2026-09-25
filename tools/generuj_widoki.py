#!/usr/bin/env python3
"""Generator kompletu arkuszy architektonicznych z modelu budynku (lamela.views).

Rzuty wszystkich kondygnacji + rzut dachu, przekroje (z konfiguracji albo automatyczne A-A przez schody i B-B),
4 elewacje — każdy arkusz jako DXF + PDF (wektorowy, dokładna skala) + PNG, tom PDF ze spisem rysunków oraz raport
QA (``plot.qa`` silnika: metryka, legenda, podziałki, grubości linii, pismo, sumy łańcuchów wymiarowych).

Przykłady:
  PYTHONPATH=src python3 tools/generuj_widoki.py \\
      --budynek model/test/dom_testowy.yaml --dzialka model/test/dzialka_testowa.yaml \\
      --arkusze model/test/arkusze_testowe.yaml --wyposazenie model/test/wyposazenie_testowe.yaml \\
      --out projekt/00_demo_silnika/widoki_test

  PYTHONPATH=src python3 tools/generuj_widoki.py --out projekt/03_PAB/widoki      # model/budynek.yaml + dzialka.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.views.sheets import generate  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budynek", default=str(ROOT / "model" / "budynek.yaml"))
    ap.add_argument("--dzialka", default=None, help="domyślnie dzialka.yaml obok pliku budynku (jeśli istnieje)")
    ap.add_argument("--arkusze", default=None, help="konfiguracja arkuszy YAML (domyślnie arkusze.yaml obok budynku)")
    ap.add_argument("--wyposazenie", default=None, help="wyposażenie YAML (domyślnie wyposazenie.yaml obok budynku)")
    ap.add_argument("--out", required=True, help="katalog wyjściowy")
    ap.add_argument("--formaty", default="dxf,pdf,png")
    ap.add_argument("--dpi", type=int, default=None, help="rozdzielczość PNG (domyślnie 150)")
    ap.add_argument("--tylko", default=None, help="numery arkuszy rozdzielone przecinkami")
    ap.add_argument("--bez-tomu", action="store_true")
    a = ap.parse_args(argv)
    bud = Path(a.budynek)
    if not bud.exists():
        ap.error(f"brak pliku modelu {bud}")
    dz = a.dzialka
    if dz is None:
        for nm in ("dzialka.yaml", "dzialka_testowa.yaml"):
            c = bud.with_name(nm)
            if c.exists():
                dz = str(c)
                break
    ark = a.arkusze
    if ark is None and bud.with_name("arkusze.yaml").exists():
        ark = str(bud.with_name("arkusze.yaml"))
    print(f"Model: {bud}\nDziałka: {dz}\nArkusze: {ark or '(zestaw domyślny)'}\nWyjście: {a.out}")
    rep = generate(str(bud), dz, ark, a.wyposazenie, a.out, formats=tuple(a.formaty.split(",")), dpi=a.dpi,
                   only=set(a.tylko.split(",")) if a.tylko else None, tom=not a.bez_tomu)
    n_err = sum(1 for s in rep["arkusze"] if "blad" in s or not s.get("qa", {}).get("ok", False))
    print(f"Arkusze: {len(rep['arkusze'])}, z błędami/uwagami QA: {n_err}; czas {rep['czas_s']} s")
    if rep.get("problemy"):
        print("Uwagi generatorów:")
        for p in rep["problemy"]:
            print("  -", p)
    print(f"Raport: {Path(a.out) / 'raport_widokow.json'}")
    return 0 if not any("blad" in s for s in rep["arkusze"]) else 1


if __name__ == "__main__":
    sys.exit(main())
