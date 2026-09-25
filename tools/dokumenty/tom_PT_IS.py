"""Generator tomu PT-3 IS — projekt techniczny, instalacje sanitarne („Dom LAMELA”).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_PT_IS.py [--wyjscie projekt/wydanie] [--bez-arkuszy] [--cache PLIK]

Wynik:
* ``projekt/wydanie/PT_3_IS_rrrr.mm.dd.pdf`` — tom PT-3 IS (osobny plik, RPB § 5 ust. 3; nazwa wg zał. 1 RPB):
  strona tytułowa (§ 7 ust. 2, „tom 3 z 4” — § 7 ust. 6), spis treści, oświadczenie projektanta PT
  (PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2), część opisowa (§ 23 RPB): stan opracowania,
  zakres i podstawy, opis instalacji (§ 23 pkt 7 lit. a, d, e), powiązania z sieciami (§ 23 pkt 8), założenia,
  wyniki i pełne obliczenia (obciążenie cieplne, PC i podłogówka, wentylacja, woda i c.w.u., kanalizacja,
  wody opadowe i retencja, drenaż), charakterystyka energetyczna (§ 23 pkt 11 lit. a–d; wariant bez PV jawnie),
  dane ppoż. (§ 23 pkt 10), urządzenia (§ 23 pkt 9), próby i odbiory, braki danych; część rysunkowa (§ 24 pkt 4
  lit. a) — arkusze z ``projekt/05_PT_instalacje_sanitarne/rysunki/raport_widokow.json``;
* ``projekt/09_opis_i_zalaczniki/PT_IS/`` — źródło Markdown części opisowej, raport walidatora (txt/json),
  ``stan.json`` (sprawy otwarte), ``obliczenia/bilans_energii.png``.

ŹRÓDŁA (odczyt i obliczenia przy każdym uruchomieniu — brak liczb wpisanych na sztywno): ``model/*.yaml``,
``lamela.obliczenia.fizyka_energia`` i ``lamela.obliczenia.instalacje`` (patrz ``pt_is_dane.py``).
``--cache PLIK`` — zapis/odczyt wyników obliczeń (pickle) wyłącznie do podglądu układu; tom z pamięci podręcznej
jest oznaczony „PODGLĄD” i nie nadaje się do wydania.
Dane osobowe, uprawnienia, podpisy — ``[DO UZUPEŁNIENIA]``; działka/MPZP/grunt — ``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pt_is_dane import KAT_ZRODLA, REPO, DanePTIS, Opis  # noqa: E402
import pt_is_opis_a as A  # noqa: E402
import pt_is_opis_b as B  # noqa: E402

from lamela.dokumenty import (Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              zamknij_przegladarke)
from lamela.dokumenty.formaty import odmiana  # noqa: E402

KAT_WYDANIE = REPO / "projekt/wydanie"
PT_TOMY = 4                                  # PT-1 AR, PT-2 BO, PT-3 IS, PT-4 IE (rejestr C.2)
PT_NR = 3


def buduj_pt_is(d: dict, D: DanePTIS, data: str) -> tuple[Dokument, Opis]:
    n = len(D.otwarte)
    podt = ("Tom PT-3 — instalacje sanitarne (IS): ogrzewanie z pompą ciepła, wentylacja mechaniczna z odzyskiem "
            "ciepła, wodociąg i c.w.u., kanalizacja, wody opadowe i retencja, charakterystyka energetyczna")
    if n:
        podt += f" · SPRAWY OTWARTE: {n} {odmiana(n, 'pozycja', 'pozycje', 'pozycji')} (rozdz. 1)"
    dok = Dokument("Projekt techniczny", "PT-IS", d, kod="PT-3 IS", branza="instalacje sanitarne",
                   data=data, tom=(PT_NR, PT_TOMY), podtytul=podt)
    dok.oswiadczenie_projektanta()
    o = Opis(dok)
    o.md += [f"# Projekt techniczny — PT-3 IS (instalacje sanitarne) — tom {PT_NR} z {PT_TOMY}",
             "*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_IS.py`; wersja wiążąca: PDF. "
             "Pełne obliczenia (raporty bibliotek `lamela.obliczenia`) — w PDF.*",
             "*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny "
             "`lamela.dokumenty`; pełna treść w PDF]*"]
    o.czesc("Opis techniczny — instalacje sanitarne", podstawa="§ 23 RPB")
    A.rozdz_stan(o, D)
    A.rozdz_podstawy(o, D, d)
    A.rozdz_ogrzewanie(o, D)
    A.rozdz_wentylacja(o, D)
    A.rozdz_woda(o, D)
    A.rozdz_kanalizacja(o, D)
    A.rozdz_deszczowa(o, D)
    A.rozdz_sieci(o, D)
    B.rozdz_obliczenia(o, D)
    B.rozdz_ep(o, D)
    B.rozdz_ppoz(o, D)
    B.rozdz_urzadzenia(o, D)
    B.rozdz_proby(o, D)
    B.rozdz_braki(o, D)
    dok.czesc_rysunkowa(D.arkusze, podstawa="§ 24 pkt 3 i pkt 4 lit. a RPB; § 7 ust. 1 pkt 4, § 10 RPB")
    o.md.append("## Część rysunkowa — wykaz rysunków\n\n| Nr | Tytuł | Skala | Format | Uwagi |\n|---|---|---|---|---|\n"
                + "\n".join(f"| {a.nr} | {a.tytul} | {a.skala or '—'} | {a.format or '—'} | "
                            f"{'' if a.istnieje else 'brak pliku — strona zastępcza'} |" for a in dok.arkusze))
    return dok, o


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(KAT_WYDANIE))
    ap.add_argument("--bez-arkuszy", action="store_true", help="arkusze jako strony zastępcze (szybki podgląd)")
    ap.add_argument("--cache", help="plik pamięci podręcznej obliczeń (tylko podgląd układu)")
    a = ap.parse_args(argv)
    t0 = time.time()
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    KAT_ZRODLA.mkdir(parents=True, exist_ok=True)
    d = dane_obiektu()
    data = d.get("data")
    D = DanePTIS(cache=Path(a.cache) if a.cache else None, bez_arkuszy=a.bez_arkuszy)
    print(f"dane: {time.time() - t0:.1f} s; arkusze {len(D.arkusze)} (brak {len(D.ark_braki)}); "
          f"sprawy otwarte: {len(D.otwarte)}; EP = {D.ep.EP:.1f} (bez PV {D.ep0.EP if D.ep0 else float('nan'):.1f})")
    dok, o = buduj_pt_is(d, D, data)
    o.zapisz(KAT_ZRODLA / "PT_IS_opis.md")
    (KAT_ZRODLA / "stan.json").write_text(json.dumps(dict(
        model=D.t_modelu, podglad=D.z_cache, sprawy_otwarte=D.otwarte, arkusze_braki=D.ark_braki,
        EP=round(D.ep.EP, 1), EP_bez_PV=round(D.ep0.EP, 1) if D.ep0 else None, EP_max=D.ep.EP_max,
        niespelnione=[(m, getattr(x, "opis", None) or x[0]) for m, x in D.niespelnione()]),
        ensure_ascii=False, indent=1), encoding="utf-8")
    tom = Tom("PT-3 IS", [dok], dane=d, data=data, nr=PT_NR, symbol="IS", strona_tytulowa=False, laczny_spis=False)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB ({time.time() - t0:.0f} s)")
    r = sprawdz_tom(w, LISTY_KONTROLNE["PT_IS"])
    (KAT_ZRODLA / f"raport_kompletnosci_{w.sciezka.stem}.txt").write_text(r.tekst(), encoding="utf-8")
    r.zapisz_json(KAT_ZRODLA / f"raport_kompletnosci_{w.sciezka.stem}.json")
    s = r.podsumowanie()
    print(f"  walidator: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
          f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}")
    for p in r.braki:
        print(f"    ✗ {p.id} [{p.element}] {p.opis} — {p.szczegoly}")
    zamknij_przegladarke()
    return w, r, D


if __name__ == "__main__":
    main()
