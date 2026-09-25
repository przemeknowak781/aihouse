#!/usr/bin/env python3
"""Generator elementów TOMU I: **PZT** (projekt zagospodarowania działki) i **ZL** (załączniki) — „Dom LAMELA”.

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_I_pzt_zl.py [--wyjscie KATALOG] [--bez-walidacji]

Wynik (domyślnie ``projekt/09_opis_i_zalaczniki/tom_I/``):

* ``PZT_rrrr.mm.dd.pdf`` + ``PZT_opis.md`` — strona tytułowa (RPB § 7 ust. 2), spis treści, oświadczenie projektanta
  z listą współautorów (PB art. 34 ust. 3d pkt 3, ust. 3e), część opisowa wg RPB § 14 pkt 1–8 i § 18, część
  rysunkowa: arkusze PZT-01…03 z ``projekt/02_PZT/rysunki`` (wykaz generowany z tabliczek);
* ``ZL_rrrr.mm.dd.pdf`` + ``ZL_zalaczniki.md`` — strona tytułowa „Załączniki”, spis załączników (RPB § 7 ust. 1a),
  informacja BIOZ (rozp. MI, Dz.U. 2003 nr 120 poz. 1126, § 2), strona zastępcza zezwolenia na lokalizację zjazdu
  (u.d.p. art. 29), oświadczenie projektanta IS o sieci ciepłowniczej (PB art. 33 ust. 2 pkt 10), wzór oświadczenia
  Inwestora z art. 102a ust. 1 PB;
* ``raport_kompletnosci_PZT_ZL.txt/.json`` — walidator ``lamela.dokumenty.sprawdz_tom`` (lista TOM_I, pozycje PZT i ZL).

Zasada: żadnych liczb wpisanych ręcznie — wszystkie wartości z modelu (``model/*.yaml``), ``lamela.wskazniki``,
audytu ``tools/audyt_wt.py`` i ``lamela.obliczenia`` przy każdym uruchomieniu (``pzt_dane.DaneZag``). Dane osobowe,
numery uprawnień, podpisy — pola ``[DO UZUPEŁNIENIA]``; dane działki/MPZP/gruntu — ``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (REPO / "src", REPO / "tools", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from lamela.dokumenty import (LISTY_KONTROLNE, Dokument, Tom, dane_obiektu, nazwa_pliku, sprawdz_tom,  # noqa: E402
                              zamknij_przegladarke)

import pzt_opis_a as A  # noqa: E402
import pzt_opis_b as B  # noqa: E402
import pzt_opis_c as C  # noqa: E402
import zl_zalaczniki as ZL  # noqa: E402
from pzt_dane import DaneZag  # noqa: E402
from zapis import Zapis  # noqa: E402

WYJSCIE = REPO / "projekt/09_opis_i_zalaczniki/tom_I"


def buduj_pzt(z: DaneZag, d: dict) -> Zapis:
    pzt = Dokument("Projekt zagospodarowania działki", "PZT", d)
    zp = Zapis(pzt, "Projekt zagospodarowania działki (PZT) — część opisowa")
    zp.blok("Oświadczenie projektanta z listą osób biorących udział w opracowaniu (PB art. 34 ust. 3d pkt 3, ust. 3e)",
            "oswiadczenie_projektanta")
    zp.czesc_opisowa("Opis techniczny do projektu zagospodarowania działki", podstawa="§ 14 RPB")
    A.wstep(zp, z, d)
    A.pkt1(zp, z, d)
    A.pkt2(zp, z, d)
    A.pkt3(zp, z, d)
    B.pkt4(zp, z, d)
    C.pkt5(zp, z, d)
    C.pkt6(zp, z, d)
    C.pkt7(zp, z, d)
    C.pkt8(zp, z, d)
    C.rysunki(zp, z, d)
    return zp


def buduj_zl(z: DaneZag, d: dict) -> Zapis:
    zl = Dokument("Załączniki", "ZL", d)
    zp = Zapis(zl, "Załączniki (ZL) — tom I")
    ZL.buduj_zl(zp, z, d)
    return zp


def waliduj(docs: list, d: dict, out: Path, tmp: Path) -> str:
    """Składa PZT + ZL w pliku roboczym (``PZT_ZL``) i sprawdza pozycje listy TOM_I dla elementów PZT i ZL."""
    lista = dict(LISTY_KONTROLNE["TOM_I"])
    lista["pozycje"] = [p for p in lista["pozycje"] if p.get("el") in ("PZT", "ZL")
                        or p.get("id") in ("F-02", "F-03", "F-04")]
    lista["elementy"] = ["PZT", "ZL"]
    lista["nazwa_pliku"] = "PZT_ZL"
    lista["opis"] = "TOM I — kontrola elementów PZT i ZL (bez PAB)"
    w = Tom("TOM I (PZT + ZL — kontrola)", docs, dane=d, strona_tytulowa=False, laczny_spis=False).zloz(tmp)
    r = sprawdz_tom(w, lista)
    (out / "raport_kompletnosci_PZT_ZL.txt").write_text(r.tekst(), encoding="utf-8")
    r.zapisz_json(out / "raport_kompletnosci_PZT_ZL.json")
    s = r.podsumowanie()
    lin = [f"walidator: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
           f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}"]
    lin += [f"  ✗ {p.id} [{p.element}] {p.opis} — {p.szczegoly}" for p in r.braki]
    return "\n".join(lin)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(WYJSCIE))
    ap.add_argument("--bez-walidacji", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    d = dane_obiektu()
    print("dane: model + wskaźniki + audyt A1 + obliczenia instalacyjne …")
    z = DaneZag(REPO)
    print(f"  ({time.time() - t0:.0f} s)")
    wyniki = []
    for kod, fn, md in (("PZT", buduj_pzt, "PZT_opis.md"), ("ZL", buduj_zl, "ZL_zalaczniki.md")):
        zp = fn(z, d)
        sciezka = out / nazwa_pliku(kod, d["data"])
        w = zp.dok.render_pdf(sciezka)
        (out / md).write_text(zp.md, encoding="utf-8")
        wyniki.append(zp.dok)
        print(f"✓ {sciezka.name}: {w.strony_razem} stron; źródło {md}")
    if not a.bez_walidacji:
        import tempfile
        with tempfile.TemporaryDirectory(prefix="lamela_tomI_") as tmp:
            print(waliduj(wyniki, d, out, Path(tmp)))
    zamknij_przegladarke()
    print(f"gotowe w {time.time() - t0:.0f} s → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
