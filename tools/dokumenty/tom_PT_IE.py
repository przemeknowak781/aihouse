"""Generator tomu PT-4 IE — projekt techniczny, instalacje elektryczne („Dom LAMELA”).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_PT_IE.py [--wyjscie projekt/wydanie] [--bez-arkuszy] [--cache PLIK]

Wynik:
* ``projekt/wydanie/PT_4_WB_rrrr.mm.dd.pdf`` — tom PT-4 (osobny plik, RPB § 5 ust. 3; nazwa wg zał. 1 RPB — symbol WB,
  bo tom obejmuje dwie specjalności: instalacyjną elektryczną i telekomunikacyjną, PB art. 15a ust. 18 i 22;
  współautor telekomunikacyjny na stronie tytułowej i w oświadczeniu — art. 34 ust. 3e PB):
  strona tytułowa (§ 7 ust. 2, „tom 4 z 4” — § 7 ust. 6), spis treści, oświadczenie projektanta PT
  (PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2), część opisowa (§ 23 RPB): stan opracowania,
  zakres i podstawy, zasilanie i powiązanie z siecią (§ 23 pkt 8), instalacje elektroenergetyczne (§ 23 pkt 7
  lit. g), fotowoltaika (PN-HD 60364-7-712), punkt ładowania EV (PN-HD 60364-7-722), telekomunikacja (lit. h,
  W-196), instalacja piorunochronna, uziom, połączenia wyrównawcze (lit. i), ochrona przeciwporażeniowa
  i przeciwprzepięciowa, bilans mocy (§ 23 pkt 11 lit. a, pkt 8 lit. b), obliczenia (pełne raporty bibliotek),
  dane ppoż. i PWP (§ 23 pkt 10, WT § 183 ust. 2–4), wyroby, próby i odbiory, braki danych; część rysunkowa
  (§ 24 pkt 4 lit. b) — arkusze z ``projekt/06_PT_instalacje_elektryczne/rysunki/raport_widokow.json``;
* ``projekt/09_opis_i_zalaczniki/PT_IE/`` — źródło Markdown części opisowej, raport walidatora (txt/json),
  ``stan.json`` (sprawy otwarte, rozbieżności rysunków).

ŹRÓDŁA (odczyt i obliczenia przy każdym uruchomieniu — brak liczb wpisanych na sztywno): ``model/*.yaml``,
``lamela.obliczenia.fizyka_energia`` i ``lamela.obliczenia.instalacje`` (patrz ``pt_ie_dane.py``).
``--cache PLIK`` — zapis/odczyt wyników obliczeń (pickle) wyłącznie do podglądu układu; tom z pamięci podręcznej
jest oznaczony „PODGLĄD” i nie nadaje się do wydania.
Dane osobowe, uprawnienia, podpisy — ``[DO UZUPEŁNIENIA]``; działka/MPZP/grunt/warunki przyłączenia —
``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pt_ie_dane import KAT_ZRODLA, REPO, DanePTIE, Opis  # noqa: E402
import pt_ie_opis_a as A  # noqa: E402
import pt_ie_opis_b as B  # noqa: E402
import pt_ie_opis_c as C  # noqa: E402
import pt_ie_opis_d as E  # noqa: E402

from lamela.dokumenty import (Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              zamknij_przegladarke)
from lamela.dokumenty.dane import Projektant  # noqa: E402
from lamela.dokumenty.formaty import odmiana  # noqa: E402

KAT_WYDANIE = REPO / "projekt/wydanie"
PT_TOMY = 4                                  # PT-1 AR, PT-2 BO, PT-3 IS, PT-4 IE (rejestr C.2)
PT_NR = 4
SYMBOL = "WB"                                # zał. 1 RPB: więcej niż jedna specjalność (IE + telekomunikacja)
KOD = "PT-4 IE+BT"


def autorzy_pt4(D: DanePTIE) -> list[Projektant]:
    """Autorzy tomu: projektant instalacji elektrycznych i współautor ze specjalnością telekomunikacyjną
    (PB art. 15a ust. 18 i 22, art. 34 ust. 3e). Dane osobowe — [DO UZUPEŁNIENIA]."""
    tele = D.arkusze_nr("teletechnika")
    return [Projektant("IE", zakres="PT-4 — instalacje elektroenergetyczne, zasilanie i RG, fotowoltaika, punkt "
                                    "ładowania EV, ochrona odgromowa, uziom i połączenia wyrównawcze, bilans mocy, "
                                    "zasilanie urządzeń teletechnicznych", elementy=("PT-IE",)),
            Projektant("BT", funkcja="Projektant (współautor)",
                       zakres=f"PT-4 — instalacje telekomunikacyjne: przyłącze światłowodowe, okablowanie strukturalne, "
                              f"RTV/SAT, SSWiN, wideodomofon (rozdz. „Instalacje telekomunikacyjne”, arkusze {tele})",
                       elementy=("PT-IE",))]


def buduj_pt_ie(d: dict, D: DanePTIE, data: str) -> tuple[Dokument, Opis]:
    n = len(D.otwarte)
    podt = ("Tom PT-4 — instalacje elektryczne (IE) i telekomunikacyjne (BT): zasilanie i rozdzielnica główna, "
            "instalacje elektroenergetyczne, fotowoltaika, punkt ładowania EV, instalacje telekomunikacyjne, ochrona "
            "odgromowa i uziemienia, bilans mocy")
    if n:
        podt += f" · SPRAWY OTWARTE: {n} {odmiana(n, 'pozycja', 'pozycje', 'pozycji')} (rozdz. 1)"
    dok = Dokument("Projekt techniczny", "PT-IE", d, kod=KOD, branza="instalacje elektryczne i telekomunikacyjne",
                   data=data, tom=(PT_NR, PT_TOMY), podtytul=podt, projektanci=autorzy_pt4(D))
    dok.oswiadczenie_projektanta()
    o = Opis(dok)
    o.md += [f"# Projekt techniczny — {KOD} (instalacje elektryczne i telekomunikacyjne) — tom {PT_NR} z {PT_TOMY}",
             "*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_IE.py`; wersja wiążąca: PDF. "
             "Pełne obliczenia (raporty bibliotek `lamela.obliczenia.elektryka`) i tabele wyników — w PDF.*",
             "*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny "
             "`lamela.dokumenty`; pełna treść w PDF]*"]
    o.czesc("Opis techniczny — instalacje elektryczne", podstawa="§ 23 RPB")
    A.rozdz_stan(o, D)
    A.rozdz_podstawy(o, D, d)
    A.rozdz_zasilanie(o, D)
    A.rozdz_elektroenergetyczne(o, D)
    B.rozdz_pv(o, D)
    B.rozdz_ev(o, D)
    B.rozdz_tele(o, D)
    B.rozdz_odgromowa(o, D)
    C.rozdz_ochrona(o, D)
    C.rozdz_bilans(o, D)
    C.rozdz_obliczenia(o, D)
    C.rozdz_ppoz(o, D)
    E.rozdz_wyroby(o, D)
    E.rozdz_proby(o, D)
    E.rozdz_braki(o, D)
    dok.czesc_rysunkowa(D.arkusze, podstawa="§ 24 pkt 4 lit. b RPB; § 7 ust. 1 pkt 4, § 10 RPB")
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
    D = DanePTIE(cache=Path(a.cache) if a.cache else None, bez_arkuszy=a.bez_arkuszy)
    print(f"dane: {time.time() - t0:.1f} s; arkusze {len(D.arkusze)} (brak {len(D.ark_braki)}); "
          f"sprawy otwarte: {len(D.otwarte)}; P_s,DLM = {D.bil.P_s_dlm:.1f} kW; PV = {D.pv.P_kWp:.2f} kWp")
    dok, o = buduj_pt_ie(d, D, data)
    o.zapisz(KAT_ZRODLA / "PT_IE_opis.md")
    (KAT_ZRODLA / "stan.json").write_text(json.dumps(dict(
        model=D.t_modelu, podglad=D.z_cache, sprawy_otwarte=D.otwarte, arkusze_braki=D.ark_braki,
        rozbieznosci_rysunkow=D.rozb_rys, propozycje=D.propozycje, wyniki={k: v for k, v in D.Wd.items()},
        kubatura_m3=round(D.kubatura, 2),
        niespelnione=[(m, x.opis) for m, x in D.niespelnione()]), ensure_ascii=False, indent=1, default=str),
        encoding="utf-8")
    tom = Tom(KOD, [dok], dane=d, data=data, nr=PT_NR, symbol=SYMBOL, strona_tytulowa=False, laczny_spis=False)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB ({time.time() - t0:.0f} s)")
    for st in sorted(out.glob("PT_4_*.pdf")):          # poprzednie nazwy tomu 4 (np. PT_4_IE_…) — nieaktualne
        if st.name != w.nazwa:
            st.unlink()
            print(f"  usunięto nieaktualny plik {st.name}")
    for st in sorted(KAT_ZRODLA.glob("raport_kompletnosci_PT_4_*")):
        if w.sciezka.stem not in st.name:
            st.unlink()
    r = sprawdz_tom(w, LISTY_KONTROLNE["PT_" + SYMBOL])
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
