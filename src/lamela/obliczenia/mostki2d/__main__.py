"""CLI: walidacja solvera i katalog węzłów z modelu.

PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d walidacja --out projekt/08_obliczenia/mostki2d
PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d katalog --budynek model/test/dom_testowy.yaml \
    --dzialka model/test/dzialka_testowa.yaml --out build/test/mostki2d [--tylko WZ-C1,WZ-R1]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="lamela.obliczenia.mostki2d")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("walidacja")
    a.add_argument("--out", default="projekt/08_obliczenia/mostki2d")
    b = sub.add_parser("katalog")
    b.add_argument("--budynek", required=True)
    b.add_argument("--dzialka", default=None)
    b.add_argument("--out", required=True)
    b.add_argument("--tylko", default=None, help="lista id węzłów rozdzielona przecinkami")
    b.add_argument("--teren", type=float, default=-0.30, help="rzędna terenu przy cokole (wzgl. ±0,00) [ZAŁ]")
    b.add_argument("--tytul", default=None)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.cmd == "walidacja":
        from .walidacja import raport_walidacji, waliduj_wszystko
        w = waliduj_wszystko()
        raport_walidacji(w, out / "walidacja_ISO10211.md")
        for x in w:
            print(f"{'OK ' if x.ok else 'ŹLE'} {x.nazwa}: max|Δθ| = {x.max_odch_T}, ΔΦ = {x.odch_phi}")
        print(f"→ {out / 'walidacja_ISO10211.md'}")
        return 0 if all(x.ok for x in w) else 1
    from lamela.model import load_model
    from .katalog import B_prim, dlugosci_z_modelu, katalog_z_modelu
    from .walidacja import waliduj_wszystko
    from .wyniki import eksport_wynikow, oblicz_wezel, raport_katalogu
    m = load_model(args.budynek, args.dzialka)
    wezly = katalog_z_modelu(m, y_teren=args.teren)
    if args.tylko:
        ids = set(args.tylko.split(","))
        wezly = [w for w in wezly if w.id in ids]
    wal = waliduj_wszystko()
    wal_txt = ("przypadki 1 i 2 oraz analityczne: " + ("SPEŁNIONE" if all(x.ok for x in wal) else "NIESPEŁNIONE")
               + f"; max |Δθ| przyp. 1 = {wal[0].max_odch_T:.3f} K, przyp. 2 = {wal[1].max_odch_T:.3f} K, "
                 f"ΔΦ = {wal[1].odch_phi:+.3f} W/m")
    wyniki = []
    for wz in wezly:
        t = time.time()
        r = oblicz_wezel(wz, katalog_wykresow=out / "rys")
        p = r.psi_glowne
        print(f"{wz.id:7s} ψ_oi = {p.psi_oi:+.3f} ψ_e = {p.psi_e:+.3f} ψ_i = {p.psi_i:+.3f} f_Rsi = {r.f['f_Rsi']:.3f} "
              f"({time.time() - t:.1f} s)")
        wyniki.append(r)
    dl, uw = dlugosci_z_modelu(m)
    tytul = args.tytul or f"Katalog mostków cieplnych 2D — {m.meta.get('nazwa', '') if hasattr(m, 'meta') else ''}"
    raport_katalogu(wyniki, out / "katalog_mostkow.md", tytul,
                    wstep="Model: `" + args.budynek + "`. " + B_prim(m)[1] + ". Długości do H_TB (system wymiarów "
                          "wewnętrznych całkowitych, przybliżone [INT]): " + "; ".join(uw),
                    dlugosci=dl, walidacja_md=wal_txt)
    eksport_wynikow(wyniki, dl, out / "wyniki_mostki2d.json")
    print(f"→ {out / 'katalog_mostkow.md'}, {out / 'wyniki_mostki2d.json'}")
    return 0 if all(r.fRsi_ok and r.zbieznosc_ok for r in wyniki) else 2


if __name__ == "__main__":
    sys.exit(main())
