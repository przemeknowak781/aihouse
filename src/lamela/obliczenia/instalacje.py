"""Uruchomienie kompletu obliczeń instalacji (sanitarne + elektryczne) dla modelu i zapis raportów.

    PYTHONPATH=src python3 -m lamela.obliczenia.instalacje \\
        --budynek model/test/dom_testowy.yaml --dzialka model/test/dzialka_testowa.yaml \\
        --wyposazenie model/test/wyposazenie_testowe.yaml --instalacje model/test/instalacje_testowe.yaml \\
        --out projekt/08_obliczenia/demo_test/instalacje [--phi-hl plik.yaml] [--wentylacja plik.yaml|330]

Kolejność (zależności): woda → kanalizacja → deszczowa → drenaż → ogrzewanie (c.w.u. z wody; Φ_HL z modułu energii)
→ bilans mocy (PC, grzałka) → obwody → PV (profil zużycia z ogrzewania/wody) → odgromowa (PV) → schematy PNG.
Wynik: raporty ``*.md``, ``schemat_RG.png``, ``schemat_PC_CWU.png``, ``README.md`` (spis, podsumowanie sprawdzeń,
założenia, dane wymagane od modelu), ``wyniki_instalacje.json`` (m.in. sekcja ``do_EP`` dla modułu energii).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .inst_wspolne import dane_z_modelu, f, phi_hl_z, tabela, wentylacja_z

DANE_WYMAGANE = [
    ("wyposazenie.yaml", "przybory sanitarne z typem (wc, umywalka, umywalka_blat, bidet, wanna, prysznic, zlew, zmywarka, pralka, "
                         "suszarka) — punkt na licu ściany + obrot; zawory ogrodowe, zlewiki, wpusty podłogowe (typy w przybory.KATALOG)"),
    ("wyposazenie.yaml", "urządzenia: pompa_ciepla (jednostka wewn.), zasobnik, rekuperator, plyta, lodowka — z mocą/typem wyrobu (opcjonalnie)"),
    ("instalacje.yaml (nowy)", "osoby; lokalizacje: RG, wodomierz, zasobnik, rozdzielacze_co per kondygnacja, ZKP, studzienka, czerpnia, "
                               "pompa_ciepla_jz {xy, ustawienie: wolnostojaca|przy_scianie|naroze}"),
    ("instalacje.yaml (nowy)", "piony: [{id, xy}] — trasy pionów wod.-kan. (inaczej grupowanie automatyczne R ≤ 3,5 m)"),
    ("instalacje.yaml (nowy)", "wyroby: dane DTR/DWU (PC: moc/COP w punktach A-15…A12 W35, L_WA, SCOP, η_s; moduł PV; falownik; "
                               "wpusty dachowe: przepustowość; zawór EA/filtr: k_v; wodomierz: ∆p(Q3))"),
    ("instalacje.yaml lub moduł energii", "obciazenie_cieplne: Φ_HL pomieszczeń [W] (PN-EN 12831) — w tym opracowaniu wskaźnikowe zastępcze, jeśli brak"),
    ("budynek.yaml: dachy[]", "wpusty [{xy, dn, podgrzewany}], przelewy_awaryjne [{xy, sciana_attyki, szer, wys, rzedna_dna}], "
                              "rury_spustowe [{id, od_wpustu, trasa, xy_pion, dn, do}], spadki (schemat §6)"),
    ("budynek.yaml: przegrody", "dach zielony: warstwy z nazwami (substrat, drenaż, geowłóknina, bariera przeciwkorzenna); podłoga: "
                                "jastrych (grubość, λ) i izolacja pod wężownicą; posadzki — kody (płytki / drewno / wykładzina)"),
    ("budynek.yaml: pomieszczenia", "temp (20/24 °C), went {naw, wyw}; nazwy jednoznaczne (łazienka, WC, kuchnia, pralnia, garaż, techniczne)"),
    ("budynek.yaml: fundamenty", "typ (lawy/plyta) i izolacja płyty (XPS pod płytą → uziom otokowy); spód fundamentu"),
    ("dzialka.yaml", "uzbrojenie istniejące i projektowane (woda, kan_sanit, en) z rzędnymi/głębokością; retencja (zbiornik xy/V, "
                     "niecka/rozsączanie obrys); odwodnienia [{typ: liniowe|opaska_zwirowa|drenaz_opaskowy|niecka, ...}]; "
                     "teren.punkty_projektowane (spadki ≥ 2 % od budynku); bramy; ZKP"),
    ("geotechnika (opinia)", "k_f in situ, ZWG, rodzaj gruntu — decyzja o drenażu i objętość niecki"),
    ("warunki przyłączenia", "ciśnienie dyspozycyjne i maks. w sieci wod., rzędna kanału, Z_Q / I_k w ZKP, typ zabezpieczenia przedlicznikowego"),
]


def oblicz_wszystko(budynek, dzialka=None, wyposazenie=None, instalacje=None, phi_hl=None, wentylacja=None, out=None,
                    schematy: bool = True) -> dict:
    """Pełny komplet obliczeń; gdy ``out`` — zapis raportów do katalogu. Zwraca słownik wyników (obiekty modułów)."""
    from .elektryka.bilans import bilans_mocy, odbiorniki_z_modelu
    from .elektryka.obwody import oblicz_obwody
    from .elektryka.odgromowa import ocena_ryzyka
    from .elektryka.pv import oblicz_pv
    from .sanitarne.deszczowa import oblicz_deszczowa
    from .sanitarne.drenaz import ocen_drenaz
    from .sanitarne.kanalizacja import oblicz_kanalizacje
    from .sanitarne.ogrzewanie import oblicz_ogrzewanie
    from .sanitarne.woda import ParametryWoda, oblicz_wode

    dane = dane_z_modelu(budynek, dzialka, wyposazenie, instalacje)
    went = wentylacja_z(wentylacja, dane)
    V = max(went["suma_wyw"], went["suma_naw"]) or 330.0          # wentylacja zrównoważona: max(Σnawiew, Σwywiew)
    wyn = {"dane": dane}
    woda0 = oblicz_wode(dane, ParametryWoda())
    wyn["ogrzewanie"] = oblicz_ogrzewanie(dane, phi_hl=phi_hl, cwu=woda0.cwu)
    P7 = float(dict(zip(wyn["ogrzewanie"].pc["T"], wyn["ogrzewanie"].pc["P"])).get(7, 6.0))
    wyn["woda"] = oblicz_wode(dane, ParametryWoda(P_PC_cwu_kW=P7))       # moc PC w trybie c.w.u. z doboru PC
    wyn["kanalizacja"] = oblicz_kanalizacje(dane)
    wyn["deszczowa"] = oblicz_deszczowa(dane)
    wyn["drenaz"] = ocen_drenaz(dane)
    odb = odbiorniki_z_modelu(dane, ogrzewanie=wyn["ogrzewanie"], woda=wyn["woda"], wentylacja_m3h=V)
    wyn["pv"] = oblicz_pv(dane, ogrzewanie=wyn["ogrzewanie"], woda=wyn["woda"], wentylacja_m3h=V)
    wyn["bilans"] = bilans_mocy(dane, odb, pv_kWp=wyn["pv"].P_kWp)
    wyn["obwody"] = oblicz_obwody(dane, odb, I_zab=wyn["bilans"].I_zab)
    wyn["odgromowa"] = ocena_ryzyka(dane, pv=wyn["pv"])
    wyn["wentylacja"] = went
    if out:
        zapisz(wyn, out, schematy=schematy)
    return wyn


RAPORTY = [("woda", "01_woda.md", "Instalacja wodociągowa i c.w.u."), ("kanalizacja", "02_kanalizacja.md", "Kanalizacja sanitarna"),
           ("deszczowa", "03_deszczowa.md", "Odwodnienie dachów, retencja"), ("drenaz", "04_drenaz.md", "Drenaż i odwodnienie powierzchniowe"),
           ("ogrzewanie", "05_ogrzewanie.md", "Pompa ciepła, ogrzewanie podłogowe, hałas"), ("bilans", "06_bilans_mocy.md", "Bilans mocy"),
           ("obwody", "07_obwody.md", "Obwody, zabezpieczenia, SPD, PWP"), ("pv", "08_pv.md", "Fotowoltaika"),
           ("odgromowa", "09_odgromowa.md", "Ochrona odgromowa, uziom")]


def zapisz(wyn: dict, out, schematy: bool = True) -> Path:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    wiersze = []
    wyniki_json = {}
    for klucz, plik, tyt in RAPORTY:
        r = wyn[klucz].raport()
        if klucz == "obwody" and schematy:
            r.img("Schemat ideowy RG", "schemat_RG.png")
        if klucz == "ogrzewanie" and schematy:
            r.img("Schemat ideowy PC / c.w.u.", "schemat_PC_CWU.png")
        r.zapisz(out / plik)
        w = r.warunki
        wiersze.append([f"[{tyt}]({plik})", str(len(w)), str(sum(1 for x in w if x.ok)), str(sum(1 for x in w if x.ok is False)),
                        "; ".join(f"{x.id} {x.opis}" for x in w if x.ok is False)[:300] or "—"])
        wyniki_json[klucz] = wyn[klucz].do_dict()
    if schematy:
        from .elektryka.schemat_rg import rysuj_schemat_rg
        from .sanitarne.schemat_pc import rysuj_schemat_pc
        rysuj_schemat_rg(wyn["obwody"], out / "schemat_RG.png")
        rysuj_schemat_pc(wyn["ogrzewanie"], wyn["woda"], out / "schemat_PC_CWU.png")
    do_ep = {"cwu": {"Q_W_nd_kWh_a": wyniki_json["woda"]["Q_W_nd_kWh_a"], "eta_W_d": wyniki_json["woda"]["eta_W_d"],
                     "zasobnik_l": wyniki_json["woda"]["zasobnik_l"], "dezynfekcja_kWh_a": wyniki_json["woda"]["dezynfekcja_kWh_a"]},
             "ogrzewanie": wyniki_json["ogrzewanie"]["do_EP"], "pv": wyniki_json["pv"]["do_EP"]}
    wyniki_json["do_EP"] = do_ep
    d = wyn["dane"]
    (out / "wyniki_instalacje.json").write_text(json.dumps(wyniki_json, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    lines = [f"# Obliczenia instalacji — {d.nazwa}", "",
             "Biblioteka `lamela.obliczenia.sanitarne` i `lamela.obliczenia.elektryka`. Model: " +
             ", ".join(f"{k}: `{v}`" for k, v in d.zrodla.items()) + ".",
             "**Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE]; wartości [ZAŁ] i [NZW] do potwierdzenia przed PT (D-19, D-23).**", "",
             "## Raporty", "", tabela(["Raport", "Warunków", "Spełnione", "Niespełnione", "Niespełnione (skrót)"], wiersze, "lrrrl"), "",
             "Schematy: [schemat ideowy RG](schemat_RG.png), [schemat PC / c.w.u.](schemat_PC_CWU.png). "
             "Wyniki liczbowe: [wyniki_instalacje.json](wyniki_instalacje.json).", "",
             "## Najważniejsze wyniki", ""]
    w = wyniki_json
    lines += [f"* Woda: q_obl = {f(w['woda']['q_obl_dm3s'], 3)} dm³/s, wodomierz {w['woda']['wodomierz']}, p_wym = "
              f"{f(w['woda']['p_wym_kPa'], 0)} kPa ({w['woda']['punkt_krytyczny']}); zasobnik c.w.u. {w['woda']['zasobnik_l']} dm³, "
              f"cyrkulacja: {w['woda']['cyrkulacja']}.",
              f"* Kanalizacja: ΣDU = {f(w['kanalizacja']['sum_DU'], 1)} l/s, Q_ww = {f(w['kanalizacja']['Q_ww_l_s'], 2)} l/s, "
              f"przykanalik {w['kanalizacja']['przykanalik']}.",
              f"* Wody opadowe: dachy {f(w['deszczowa']['A_dachow_m2'], 1)} m², Q = {f(w['deszczowa']['Q_dachy_l_s'], 2)} l/s; zbiornik "
              f"{f(w['deszczowa']['V_zbiornika_m3'], 1)} m³ + niecka {f(w['deszczowa']['niecka_A_m2'], 1)} m² (V_min "
              f"{f(w['deszczowa']['niecka_V_min_m3'], 2)} m³); pokrycie podlewania {f(100 * w['deszczowa']['pokrycie_podlewania'], 0)} %.",
              f"* Drenaż opaskowy: {w['drenaz']['drenaz_opaskowy']} ({w['drenaz']['klasa_oddzialywania_wody']}).",
              f"* Ogrzewanie: Φ_HL = {f(w['ogrzewanie']['Phi_HL_kW'], 2)} kW ({w['ogrzewanie']['zrodlo_Phi_HL']}); PC {w['ogrzewanie']['PC']}, "
              f"θ_biv = {f(w['ogrzewanie']['theta_biv'], 1)} °C; θ_V = {f(w['ogrzewanie']['theta_V_des'], 1)} °C; bufor {w['ogrzewanie']['bufor_l']} dm³; "
              f"hałas na granicy {f(w['ogrzewanie']['L_A_granica_dB'], 1)} dB(A).",
              f"* Bilans mocy: P_inst = {f(w['bilans']['P_inst_kW'], 1)} kW, P_szczyt (DLM) = {f(w['bilans']['P_szczyt_DLM_kW'], 1)} kW "
              f"≤ P_przył = {f(w['bilans']['P_przylaczeniowa_kW'], 0)} kW / {f(w['bilans']['I_zab_A'], 0)} A.",
              f"* Obwody: {w['obwody']['obwody']}; WLZ {w['obwody']['WLZ']} (∆U = {f(w['obwody']['dU_WLZ_proc'], 2)} %); maks. ∆U = "
              f"{f(w['obwody']['dU_max_proc'], 2)} %; CRL = {f(w['obwody']['CRL'], 0)} → SPD T1+2; PWP: {w['obwody']['PWP']}.",
              f"* PV: {w['pv']['n_modulow']} × moduł = {f(w['pv']['P_kWp'], 2)} kWp ({w['pv']['wariant']}), E = {f(w['pv']['E_PV_kWh_a'], 0)} kWh/a, "
              f"autokonsumpcja {f(100 * w['pv']['autokonsumpcja'], 0)} %.",
              f"* Odgromowa: A_D = {f(w['odgromowa']['A_D_m2'], 0)} m²; {w['odgromowa']['decyzja_LPS']}; uziom: {w['odgromowa']['uziom']}.", "",
              "## Dane przekazywane do charakterystyki energetycznej (moduł energii)", "",
              "```json", json.dumps(do_ep, ensure_ascii=False, indent=1), "```", "",
              "## Założenia ogólne i uwagi", ""]
    Vw = max(wyn["wentylacja"]["suma_wyw"], wyn["wentylacja"]["suma_naw"]) or 330.0
    lines += [f"* {u}" for u in d.uwagi] + [f"* Wentylacja (moc rekuperatora, profil zużycia): {f(Vw, 0)} m³/h = max(Σnawiew, Σwywiew) — "
                                             + wyn["wentylacja"]["zrodlo"] + ".", ""]
    lines += ["## Dane wymagane od modelu / wyposażenia (do uzupełnienia w `model/`)", "",
              tabela(["Plik / źródło", "Dane"], [[a, b] for a, b in DANE_WYMAGANE], "ll"), ""]
    (out / "README.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Obliczenia instalacji sanitarnych i elektrycznych (Dom LAMELA)")
    ap.add_argument("--budynek", required=True)
    ap.add_argument("--dzialka")
    ap.add_argument("--wyposazenie")
    ap.add_argument("--instalacje")
    ap.add_argument("--phi-hl", help="Φ_HL pomieszczeń (YAML/JSON {id: W}) z modułu energii")
    ap.add_argument("--wentylacja", help="strumienie powietrza (YAML/JSON) lub liczba m³/h")
    ap.add_argument("--out", required=True)
    ap.add_argument("--bez-schematow", action="store_true")
    a = ap.parse_args(argv)
    went = None
    if a.wentylacja:
        try:
            went = float(a.wentylacja)
        except ValueError:
            import yaml
            went = yaml.safe_load(Path(a.wentylacja).read_text(encoding="utf-8"))
    wyn = oblicz_wszystko(a.budynek, a.dzialka, a.wyposazenie, a.instalacje, phi_hl=phi_hl_z(a.phi_hl) if a.phi_hl else None,
                          wentylacja=went, out=a.out, schematy=not a.bez_schematow)
    print(f"Zapisano raporty do {a.out}")
    for klucz, plik, _ in RAPORTY:
        w = wyn[klucz].warunki
        print(f"  {plik:22s} warunków {len(w):3d}, niespełnionych {sum(1 for x in w if x.ok is False)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
