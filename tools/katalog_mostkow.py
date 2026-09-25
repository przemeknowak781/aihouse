"""Katalog mostków cieplnych 2D (PN-EN ISO 10211) z kartami węzłów — ciągłość izolacji, woda i wilgoć, ocena.

Dla każdego węzła: symulacja 2D (`lamela.obliczenia.mostki2d`), ψ_e / ψ_i / ψ_oi, θ_si,min i f_Rsi, test ciągłości
izolacji na siatce, lista kontrolna wody i wilgoci (hydroizolacja, paroizolacja, spadki, obróbki, wpusty, przelewy,
rury spustowe, drenaż — z danych modelu), ocena; karta PNG (przekrój z materiałami i liniami hydro/paro/obróbek +
mapa temperatur z izotermami) i raport Markdown z tabelą zbiorczą.

Źródło węzłów:
* model z sekcją `wezly` (docelowy `model/budynek.yaml`, SCHEMAT_MODELU p. 6–7) → wszystkie węzły tej sekcji
  (typy/aliasy: `mostki2d.katalog.ALIASY_WEZLOW`; `dlugosc` → H_TB);
* model bez sekcji `wezly` albo `--demo` → katalog demonstracyjny z przegród modelu z wariantami porównawczymi
  (`mostki2d.katalog.katalog_demonstracyjny`).

Użycie:
    PYTHONPATH=src python3 tools/katalog_mostkow.py                       # budynek.yaml, jeśli istnieje; inaczej model testowy (demo)
    PYTHONPATH=src python3 tools/katalog_mostkow.py --budynek model/test/dom_testowy.yaml \
        --dzialka model/test/dzialka_testowa.yaml --out projekt/08_obliczenia/demo_test/mostki
    PYTHONPATH=src python3 tools/katalog_mostkow.py --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
        --out projekt/08_obliczenia/mostki2d/katalog [--tylko WZ-01,WZ-02] [--demo] [--teren -0.30]
Kod wyjścia: 0 — wszystkie węzły f_Rsi ≥ f_Rsi,min i zbieżne; 2 — co najmniej jeden nie; 1 — błąd.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _domyslne(args):
    bud = args.budynek
    if bud is None:
        bud = str(ROOT / "model" / "budynek.yaml") if (ROOT / "model" / "budynek.yaml").exists() else \
            str(ROOT / "model" / "test" / "dom_testowy.yaml")
    testowy = "test" in Path(bud).parts
    dz = args.dzialka
    if dz is None:
        kand = ROOT / "model" / ("test/dzialka_testowa.yaml" if testowy else "dzialka.yaml")
        dz = str(kand) if kand.exists() else None
    out = args.out or str(ROOT / "projekt" / "08_obliczenia" / ("demo_test/mostki" if testowy else "mostki2d/katalog"))
    return bud, dz, Path(out), testowy


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--budynek", default=None, help="model budynku (domyślnie model/budynek.yaml albo model testowy)")
    ap.add_argument("--dzialka", default=None)
    ap.add_argument("--out", default=None, help="katalog wyników (PNG + katalog_mostkow.md)")
    ap.add_argument("--tylko", default=None, help="id węzłów rozdzielone przecinkami")
    ap.add_argument("--demo", action="store_true", help="katalog demonstracyjny nawet przy sekcji `wezly`")
    ap.add_argument("--teren", type=float, default=-0.30, help="rzędna terenu przy cokole [m] [ZAŁ]")
    ap.add_argument("--bez-szczegolow", action="store_true", help="bez wykresów strumienia/θ_si i raportu szczegółów")
    ap.add_argument("--dodatkowe", action="store_true",
                    help="także węzły spoza sekcji `wezly` wykryte w geometrii modelu (WZ-X…: dach – ściana wyższa)")
    args = ap.parse_args(argv)

    from lamela.model import load_model
    from lamela.obliczenia.mostki2d import karta as K
    from lamela.obliczenia.mostki2d.katalog import (POROWNANIA_DEMO, B_prim, dlugosci_z_modelu,
                                                    katalog_demonstracyjny, wezly_z_sekcji)
    from lamela.obliczenia.mostki2d.walidacja import waliduj_wszystko
    from lamela.obliczenia.mostki2d.wyniki import eksport_wynikow, oblicz_wezel, raport_katalogu

    bud, dz, out, testowy = _domyslne(args)
    out.mkdir(parents=True, exist_ok=True)
    m = load_model(bud, dz)
    pominiete, kody_w = [], {}
    if not args.demo and isinstance(m.raw.get("wezly"), list):
        wezly, dl, pominiete, kody_w = wezly_z_sekcji(m, y_teren=args.teren)
        tryb = f"sekcja `wezly` modelu ({len(wezly)} węzłów)"
        porownania = None
        if args.dodatkowe:
            from lamela.obliczenia.mostki2d.katalog_dod import wezly_dodatkowe
            dod = wezly_dodatkowe(m)
            for w_, L_ in dod:
                wezly.append(w_)
                dl[w_.id] = round(L_, 3)
                kody_w[w_.id] = []
            tryb += f" + {len(dod)} węzły spoza sekcji wykryte w geometrii (WZ-X…, długości z geometrii)"
    else:
        wezly = katalog_demonstracyjny(m, y_teren=args.teren)
        dl, _ = dlugosci_z_modelu(m)
        tryb = "katalog DEMONSTRACYJNY z przegród modelu (warianty porównawcze)"
        porownania = POROWNANIA_DEMO
    if args.tylko:
        ids = set(args.tylko.split(","))
        wezly = [w for w in wezly if w.id in ids]
    if not wezly:
        print("brak węzłów do obliczenia", file=sys.stderr)
        return 1

    wal = waliduj_wszystko()
    wal_ok = all(x.ok for x in wal)
    wal_txt = (f"przypadki 1 i 2 zał. C ISO 10211 oraz analityczne — {'SPEŁNIONE' if wal_ok else 'NIESPEŁNIONE'} "
               f"(max |Δθ| przyp. 1 = {wal[0].max_odch_T:.3f} K, przyp. 2 = {wal[1].max_odch_T:.3f} K ≤ 0,1 K; "
               f"ΔΦ = {wal[1].odch_phi:+.3f} W/m ≤ 0,1 W/m)")
    print(("OK " if wal_ok else "ŹLE") + " walidacja: " + wal_txt)

    karty = []
    for wz in wezly:
        t = time.time()
        r = oblicz_wezel(wz, katalog_wykresow=None if args.bez_szczegolow else out / "rys")
        k = K.karta_wezla(r, m, {"przegrody": kody_w.get(wz.id, [])}, out / f"{wz.id}_karta.png")
        karty.append(k)
        p = r.psi_glowne
        print(f"{wz.id:8s} ψ_e = {p.psi_e:+.3f} ψ_oi = {p.psi_oi:+.3f} f_Rsi = {r.f['f_Rsi']:.3f} "
              f"izolacja: {'ciągła' if k.ciag.ciagla else ('grunt' if k.ciag.przez_grunt else 'PRZERWANA'):9s} "
              f"{k.ocena['klasa']:12s} ({time.time() - t:.1f} s)")

    nazwa = (m.meta or {}).get("nazwa", "") if isinstance(getattr(m, "meta", None), dict) else ""
    tytul = f"Katalog mostków cieplnych — {nazwa or Path(bud).stem}" + (" (DEMONSTRACJA na modelu testowym)"
                                                                       if testowy else "")
    try:
        rel_bud = Path(bud).resolve().relative_to(ROOT)
    except ValueError:
        rel_bud = Path(bud)
    wstep = (f"Model: `{rel_bud}`; źródło węzłów: {tryb}. {B_prim(m)[1]}. Wygenerowano: "
             f"`PYTHONPATH=src python3 tools/katalog_mostkow.py" + (f" --budynek {rel_bud}" if args.budynek else "")
             + (" --demo" if args.demo else "") + (" --dodatkowe" if args.dodatkowe else "") + "`.")
    if testowy:
        wstep += (" **Model testowy pipeline'u — nie jest projektem Domu LAMELA**; katalog demonstruje metodę i "
                  "narzędzie; po utworzeniu `model/budynek.yaml` z sekcją `wezly` skrypt wygeneruje katalog "
                  "docelowy.")
    szcz = None
    if not args.bez_szczegolow:
        szcz = out / "szczegoly_obliczen.md"
        raport_katalogu([k.w for k in karty], szcz, tytul + " — szczegóły obliczeń",
                        wstep="Dane wejściowe, warunki brzegowe, siatki, elementy flankujące i ψ w trzech systemach "
                              "wymiarów dla węzłów z `katalog_mostkow.md`.", dlugosci=dl, walidacja_md=wal_txt)
    K.raport_kart(karty, out / "katalog_mostkow.md", tytul, wstep, wal_txt, porownania, dl, szcz, pominiete)
    wyn = eksport_wynikow([k.w for k in karty], dl)
    for k in karty:
        d = wyn[k.w.wezel.id]
        d.update({"ocena": k.ocena["klasa"], "izolacja_ciagla": k.ciag.ciagla,
                  "droga_mostka": k.ciag.materialy or None,
                  "woda_braki": [p.tekst for p in k.kontrola if p.status == "BRAK"],
                  "woda_uwagi": [p.tekst for p in k.kontrola if p.status == "UWAGA"]})
    import json
    (out / "wyniki_mostki.json").write_text(json.dumps(wyn, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"→ {out / 'katalog_mostkow.md'} ({len(karty)} kart), {out / 'wyniki_mostki.json'}")
    return 0 if all(k.w.fRsi_ok and k.w.zbieznosc_ok for k in karty) and wal_ok else 2


if __name__ == "__main__":
    sys.exit(main())
