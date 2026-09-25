#!/usr/bin/env python3
"""Składanie TOMU I projektu budowlanego „Dom LAMELA”: PZT + PAB + ZL we wspólnej oprawie, jeden plik PDF.

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/zloz_tom_I.py [--wyjscie projekt/wydanie] [--data RRRR-MM-DD]
                                                         [--z-elementami] [--regeneruj-rysunki] [--png KATALOG]

Przebieg:

1. generatory elementów — ``tom_I_pzt_zl`` (PZT, ZL; dane ``pzt_dane.DaneZag``) i ``tom_I_pab`` (PAB; ``DanePAB``) —
   budują dokumenty z modelu i obliczeń przy każdym uruchomieniu (żadnych liczb wpisanych ręcznie); z
   ``--z-elementami`` dodatkowo zapisują samodzielne pliki elementów w ``projekt/09_opis_i_zalaczniki/tom_I``;
2. arkusze rysunkowe: PZT z ``projekt/02_PZT/rysunki`` (raport_widokow.json), PAB z ``projekt/03_PAB/rysunki``
   albo — gdy kompletu brak — z ``projekt/01_koncepcja/widoki`` (informacja w raporcie); z ``--regeneruj-rysunki``
   arkusze są najpierw generowane z bieżącego modelu (``tools/generuj_widoki.py``: PZT wg ``model/arkusze_pzt.yaml``
   → ``projekt/02_PZT/rysunki``, PAB wg ``model/arkusze.yaml`` → ``projekt/03_PAB/rysunki``; ok. 4–5 min);
3. jeden plik ``PZT_PAB_ZL_rrrr.mm.dd.pdf`` (zał. 1 RPB, ``lamela.dokumenty.nazwy``) w ``projekt/wydanie/``:
   strona tytułowa tomu, łączny spis treści ze spisem załączników (RPB § 7 ust. 7 pkt 1), elementy z odrębną
   numeracją „strona X z Y” (§ 6 ust. 1), rysunki oznaczone numerem rysunku (§ 6 ust. 3), zakładki, metadane;
4. walidator ``sprawdz_tom`` z listą TOM_I → ``raport_kompletnosci_PZT_PAB_ZL_rrrr.mm.dd.md/.json/.txt``;
5. kontrole pliku: rozmiar ≤ 150 MB (RPB § 2b ust. 3), wektorowość arkuszy (§ 2b ust. 2), zgodność arkuszy z
   raportami generatora widoków, aktualność rysunków względem modelu, metadane (``tom_I_kontrole``).

Kod wyjścia 0 — wszystkie pozycje listy kontrolnej OK / DO UZUPEŁNIENIA (dane osobowe, dokumenty zewnętrzne) / N/D
z podstawą, a kontrole pliku bez BRAK; 1 — są braki.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for _p in (REPO / "src", REPO / "tools", HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from lamela.dokumenty import LISTY_KONTROLNE, Tom, dane_obiektu, sprawdz_tom, zamknij_przegladarke  # noqa: E402

import tom_I_kontrole as K  # noqa: E402
import tom_I_pab as GPAB  # noqa: E402
import tom_I_pzt_zl as GPZT  # noqa: E402
from pab_dane import DanePAB  # noqa: E402
from pzt_dane import DaneZag  # noqa: E402
from tom_I_raport import raport_md  # noqa: E402

WYDANIE = REPO / "projekt/wydanie"
ZRODLA_MD = REPO / "projekt/09_opis_i_zalaczniki/tom_I"


def lista_tom_I(z: DaneZag) -> dict:
    """Lista kontrolna TOM_I; podstawa „nie dotyczy” oświadczenia zarządcy drogi — z danych drogi w modelu."""
    lista = copy.deepcopy(LISTY_KONTROLNE["TOM_I"])
    dr = z.droga()
    for p in lista["pozycje"]:
        if p["id"] == "C1-3-12" and p.get("nd"):
            p["nd"] = (f"zjazd z drogi {dr['symbol']} ({dr['nazwa']}; model/dzialka.yaml) — droga gminna, nie krajowa "
                       f"ani wojewódzka; zezwolenie na zjazd: ZL zał. 2 (u.d.p. art. 29)")
    return lista


def regeneruj_rysunki() -> None:
    import subprocess
    for arg, kat in (("model/arkusze_pzt.yaml", K.KAT_PZT), ("model/arkusze.yaml", K.KAT_PAB[0])):
        print(f"generuj_widoki: {arg} → {K._rel(kat)}")
        subprocess.run([sys.executable, str(REPO / "tools/generuj_widoki.py"), "--arkusze", str(REPO / arg),
                        "--out", str(kat)], check=True, cwd=str(REPO))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(WYDANIE))
    ap.add_argument("--data", default=None, help="data opracowania (domyślnie meta.data modelu)")
    ap.add_argument("--z-elementami", action="store_true",
                    help="uruchom też samodzielne generatory (PZT_*.pdf, ZL_*.pdf, PAB_*.pdf w 09_opis_i_zalaczniki)")
    ap.add_argument("--regeneruj-rysunki", action="store_true",
                    help="wygeneruj arkusze PZT i PAB z bieżącego modelu przed składaniem")
    ap.add_argument("--png", default=None, help="katalog podglądu PNG stron tomu (opcjonalnie)")
    a = ap.parse_args(argv)
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    if a.regeneruj_rysunki:
        regeneruj_rysunki()
    if a.z_elementami:
        print("— generatory elementów (pliki samodzielne) —")
        GPZT.main(["--bez-walidacji"])
        GPAB.main([] if not a.data else ["--data", a.data])

    d = dane_obiektu()
    data = a.data or d.get("data")
    if a.data:
        d["data"] = data
    print("dane PAB: model + audyt + fizyka/EP + instalacje …")
    D = DanePAB()
    print(f"dane PZT/ZL (Φ_HL i dobór PC wspólne z PAB) … ({time.time() - t0:.0f} s)")
    z = DaneZag(REPO, phi_hl=D.obc)
    kat_pab, info_pab = K.zrodlo_rysunkow_pab(D)
    GPAB.uzupelnij_otwarte(D)
    print(f"  {info_pab}")

    zp_pzt = GPZT.buduj_pzt(z, d)
    zp_zl = GPZT.buduj_zl(z, d)
    pab = GPAB.buduj_pab(d, D, data=data)
    ZRODLA_MD.mkdir(parents=True, exist_ok=True)
    (ZRODLA_MD / "PZT_opis.md").write_text(zp_pzt.md, encoding="utf-8")
    (ZRODLA_MD / "ZL_zalaczniki.md").write_text(zp_zl.md, encoding="utf-8")

    print(f"składanie tomu … ({time.time() - t0:.0f} s)")
    tom = Tom("TOM I", [zp_pzt.dok, pab, zp_zl.dok], dane=d, rodzaj="PZT_PAB_ZL", data=data,
              strona_tytulowa=True, laczny_spis=True)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB ({time.time() - t0:.0f} s)")

    r = sprawdz_tom(w, lista_tom_I(z))
    ark_pzt = [(x, s) for x, s in w.arkusze if str(x.nr).startswith("PZT")]
    ark_pab = [(x, s) for x, s in w.arkusze if not str(x.nr).startswith("PZT")]
    k_wekt, wekt = K.wektorowosc(w.sciezka, w.arkusze)
    kontrole = [K.rozmiar(w.sciezka), k_wekt, K.metadane(w.sciezka), K.spis_zalacznikow(w.sciezka),
                K.zgodnosc_z_raportem("PZT", K.KAT_PZT, ark_pzt), K.zgodnosc_z_raportem("PAB", kat_pab, ark_pab),
                K.aktualnosc("PZT", K.KAT_PZT), K.aktualnosc("PAB", kat_pab), K.metryki(w.sciezka, w.arkusze)]
    otwarte = dict(PAB=list(D.otwarte), rysunki_PZT=K.problemy_generatora(K.KAT_PZT),
                   rysunki_PAB=K.problemy_generatora(kat_pab))
    zrodla = dict(PZT=K._rel(K.KAT_PZT), PAB=K._rel(kat_pab), PAB_info=info_pab)

    stem = f"raport_kompletnosci_{w.sciezka.stem}"
    (out / f"{stem}.txt").write_text(r.tekst(), encoding="utf-8")
    js = r.json()
    js.update(kontrole_pliku=kontrole, arkusze=wekt, zrodla_rysunkow=zrodla, sprawy_otwarte=otwarte,
              elementy_tomu=w.elementy, wygenerowano=time.strftime("%Y-%m-%d %H:%M"))
    (out / f"{stem}.json").write_text(json.dumps(js, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    (out / f"{stem}.md").write_text(raport_md(r, w, kontrole, wekt, zrodla, otwarte), encoding="utf-8")

    s = r.podsumowanie()
    print(f"walidator: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
          f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}")
    for p in r.pozycje:
        if p.status not in ("OK",):
            print(f"  {p.status:<16} {p.id} [{p.element}] {p.opis} — {p.szczegoly}")
    for k in kontrole:
        print(f"  kontrola {k['id']:<10} {k['status']:<12} {k['opis']} — {k['szczegoly']}")
    if a.png:
        GPAB.podglad_png(w.sciezka, Path(a.png))
    zamknij_przegladarke()
    niedozw = [p for p in r.pozycje if p.status in ("BRAK", "OSTRZEŻENIE")] + \
              [k for k in kontrole if k["status"] == "BRAK"]
    print(f"gotowe w {time.time() - t0:.0f} s → {w.sciezka}")
    return 1 if niedozw else 0


if __name__ == "__main__":
    sys.exit(main())
