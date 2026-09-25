"""Generator elementu PAB tomu I — projekt architektoniczno-budowlany „Dom LAMELA” (RPB § 20–21).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_I_pab.py [--wyjscie KATALOG] [--data RRRR-MM-DD] [--png]

Skład elementu: strona tytułowa (RPB § 7 ust. 2), spis treści (§ 7 ust. 5), oświadczenie projektanta (PB art. 34 ust. 3d
pkt 3, ust. 3e), część opisowa wg § 20 ust. 1 pkt 1–14 i ust. 2 (rozdział = punkt przepisu), załącznik nr 1 — opinia
geotechniczna (rozp. Dz.U. 2012 poz. 463 § 7 ust. 1, § 8), część rysunkowa (§ 21 pkt 1) z arkuszami z
``projekt/03_PAB/rysunki/raport_widokow.json`` albo — gdy kompletu jeszcze nie ma — z arkuszami zastępczymi wg
``model/arkusze.yaml``. Wszystkie liczby pochodzą z modelu i obliczeń (``pab_dane.DanePAB``) przy każdym uruchomieniu.

Wynik w ``projekt/09_opis_i_zalaczniki/tom_I/``: ``PAB_rrrr.mm.dd.pdf`` (nazwa wg zał. 1 RPB), raport walidatora
(lista TOM_I zawężona do PAB), ``PAB_otwarte.json`` (sprawy do zamknięcia danymi Inwestora/modelu).
Do złożenia tomu PZT_PAB_ZL: ``from tom_I_pab import buduj_pab`` → ``Dokument`` elementu PAB.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for _p in (REPO / "src", REPO / "tools", HERE):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from lamela.dokumenty import (Arkusz, Dokument, LISTY_KONTROLNE, Tom, dane_obiektu, sprawdz_tom,  # noqa: E402
                              zamknij_przegladarke)

import pab_geotechnika  # noqa: E402
import pab_opis_a as A  # noqa: E402
import pab_opis_b as B  # noqa: E402
import pab_opis_c as C  # noqa: E402
import pab_opis_d as E  # noqa: E402
import pab_param  # noqa: E402
from pab_dane import DanePAB  # noqa: E402

WYJSCIE = REPO / "projekt/09_opis_i_zalaczniki/tom_I"


def arkusze_pab(D) -> list:
    """Arkusze części rysunkowej: pliki z raportu generatora widoków albo arkusze zastępcze wg model/arkusze.yaml."""
    cfg = D.arkusze_cfg
    sk = (cfg.get("wspolne") or {}).get("skala")
    plan = {str(a["nr"]): a for a in cfg.get("arkusze") or []}
    out = []
    if D.raport_rys:
        for a in D.raport_rys.get("arkusze") or []:
            pdf = (a.get("pliki") or {}).get("pdf")
            p = (REPO / pdf) if pdf and not Path(pdf).is_absolute() else Path(pdf) if pdf else None
            if p is not None and p.exists():
                out.append(Arkusz.z_pdf(p, nr=a.get("nr"), tytul=a.get("tytul"), skala=a.get("skala")))
            else:
                out.append(Arkusz.planowany(a.get("nr"), a.get("tytul"), a.get("skala") or "—", a.get("format")))
            plan.pop(str(a.get("nr")), None)
    for nr, a in plan.items():
        out.append(Arkusz.planowany(nr, a.get("tytul"), f"1:{sk}" if sk else "—", None))
    return out


def buduj_pab(d: dict, D: DanePAB, arkusze: list | None = None, data: str | None = None) -> Dokument:
    pab = Dokument("Projekt architektoniczno-budowlany", "PAB", d, data=data or d.get("data"))
    pab.oswiadczenie_projektanta()
    A.wstep(pab, D, d)
    A.r01(pab, D, d)
    A.r02(pab, D, d)
    A.r03(pab, D, d)
    pab_param.r04(pab, D, d)
    B.r05(pab, D, d)
    B.r06_08(pab, D, d)
    B.r09(pab, D, d)
    C.r10(pab, D, d)
    C.r11(pab, D, d)
    E.r12(pab, D, d)
    E.r13(pab, D, d)
    E.r14_15(pab, D, d)
    pab_geotechnika.opinia(pab, D, d)
    pab.czesc_rysunkowa(arkusze if arkusze is not None else arkusze_pab(D))
    return pab


def uzupelnij_otwarte(D) -> None:
    """Sprawy wynikające z treści opisu (posadowienie, kolorystyka, normy) — dopisywane do ``D.otwarte``."""
    P = B.dane_posadowienia(D)
    hz = (P["geo"] or {}).get("h_z")
    if P["gl_obw"] is not None and hz is not None and P["gl_obw"] < hz:
        D.otwarte.append(f"Posadowienie: spód żeber obwodowych {P['gl_obw']:.2f} m p.p.t. < h_z = {hz:.2f} m — płytkie "
                         "posadowienie z izolacją obwodową wymaga sprawdzenia wg PN-EN ISO 13793 w PT-2 BO (W-284).")
    for r in A.wyroby_elewacji(D):
        if "[DO UZUP" in str(r["Kolorystyka"]) + str(r["Paleta MPZP"]):
            D.otwarte.append(f"Kolorystyka: {r['Element']} — {r['Wyrób (model)'][:70]}: kolor/zgodność z paletą MPZP do "
                             "ustalenia (karta kolorystyki; decyzja Inwestora).")
    D.otwarte.append("Kubatura i pow. zabudowy: algorytmy lamela.model powołują PN-ISO 9836:2015 — potwierdzić zgodność "
                     "definicji z PN-ISO 9836:2022-07 (W-316).")
    D.otwarte.append("Analiza ekonomiczna regulacji pomieszczeniowej (WT § 135 ust. 9 pkt 2): nakład K i oszczędność s — "
                     "z ofert/danych producenta w PT-3 IS; opinia techniczna projektanta IS (imię, nr uprawnień).")
    D.otwarte.append("Opinia geotechniczna: zastąpić opinią z badań (autor, kwalifikacje, metryki sondowań); hydrant "
                     "i budynki sąsiednie potwierdzić na mapie do celów projektowych.")


def lista_pab() -> dict:
    """Lista kontrolna TOM_I zawężona do elementu PAB (plik PAB_rrrr.mm.dd.pdf)."""
    t = LISTY_KONTROLNE["TOM_I"]
    poz = [p for p in t["pozycje"] if p.get("el") in ("PAB", "*") and p["id"] not in ("C1-0-01",)]
    return dict(t, opis="Element PAB (rejestr C.1 poz. 2)", nazwa_pliku="PAB", elementy=["PAB"], pozycje=poz)


def podglad_png(pdf: Path, katalog: Path, strony: list[int] | None = None, dpi: int = 70) -> list[Path]:
    import pymupdf
    katalog.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf))
    out = []
    for i in (strony or range(doc.page_count)):
        if 0 <= i < doc.page_count:
            p = katalog / f"{pdf.stem}_s{i + 1:03d}.png"
            doc[i].get_pixmap(dpi=dpi).save(str(p))
            out.append(p)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(WYJSCIE))
    ap.add_argument("--data", default=None, help="data opracowania (domyślnie meta.data modelu)")
    ap.add_argument("--png", default=None, help="katalog podglądu PNG stron (opcjonalnie)")
    a = ap.parse_args(argv)
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    d = dane_obiektu()
    data = a.data or d.get("data")
    print("Dane PAB (model + obliczenia):")
    D = DanePAB()
    uzupelnij_otwarte(D)
    pab = buduj_pab(d, D, data=data)
    tom = Tom("PAB", [pab], dane=d, rodzaj="PAB", data=data, strona_tytulowa=False, laczny_spis=False)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB ({time.time() - t0:.0f} s)")
    r = sprawdz_tom(w, lista_pab())
    (out / f"raport_kompletnosci_{w.sciezka.stem}.txt").write_text(r.tekst(), encoding="utf-8")
    r.zapisz_json(out / f"raport_kompletnosci_{w.sciezka.stem}.json")
    s = r.podsumowanie()
    print(f"  walidator: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
          f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}")
    for p in r.braki:
        print(f"    ✗ {p.id} {p.opis} — {p.szczegoly}")
    otw = dict(plik=w.nazwa, wygenerowano=time.strftime("%Y-%m-%d %H:%M"), otwarte=D.otwarte,
               walidator=[f"{p.id} {p.opis}: {p.status} — {p.szczegoly}" for p in r.pozycje if p.status != "OK"])
    (out / "PAB_otwarte.json").write_text(json.dumps(otw, ensure_ascii=False, indent=1), encoding="utf-8")
    if a.png:
        podglad_png(w.sciezka, Path(a.png))
    zamknij_przegladarke()
    print(f"gotowe w {time.time() - t0:.0f} s → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
