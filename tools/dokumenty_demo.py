"""Demonstracja systemu składania części opisowej i tomów (``lamela.dokumenty``).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty_demo.py [--wyjscie KATALOG] [--bez-widokow]

Wynik w ``projekt/00_demo_silnika/dokumenty_demo/``:
* ``PZT_PAB_ZL_2026.09.25.pdf`` — TOM I: strona tytułowa tomu, łączny spis treści, PZT (oświadczenie, opis
  § 14 z tabelami i wykresem, część rysunkowa z arkuszami zastępczymi), PAB (oświadczenie, opis § 20 z tabelami
  generowanymi z modelu testowego, arkusze z ``projekt/00_demo_silnika``), ZL (informacja BIOZ, strona zastępcza
  decyzji o zjeździe, oświadczenie o sieci ciepłowniczej);
* ``PT_1_AR_2026.09.25.pdf`` — przykładowy tom PT (osobny plik, oświadczenie wg art. 41 ust. 4a pkt 2 PB);
* ``WN_wzory_oswiadczen_2026.09.25.pdf`` — wzór oświadczenia Inwestora z art. 102a PB i informacja o PB-5
  (dokumenty wniosku, poza projektem);
* ``raport_kompletnosci_*.txt/json`` — wynik walidatora (lista kontrolna z sekcji C rejestru);
* ``plan_skladania.json`` — składanie arkuszy do A4 dla wersji papierowej.

Dane działki, MPZP i gruntu są fikcyjne; tabele pomieszczeń, stolarki i przegród pochodzą z modelu testowego
``model/test/dom_testowy.yaml`` (nie jest to model Domu LAMELA). Status wszystkich plików: PRZYKŁAD – NIE DO ZŁOŻENIA.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

import yaml  # noqa: E402

from lamela.dokumenty import (Arkusz, Dokument, Tom, dane_obiektu, sprawdz_tom, plan_skladania,  # noqa: E402
                              LISTY_KONTROLNE, liczba, do_uzup, DANE_PRZYKLADOWE, ZAL, NZW, zamknij_przegladarke)

DEMO = REPO / "projekt/00_demo_silnika"
WYM = yaml.safe_load(open(REPO / "docs/10_podstawy_prawne/wymagania.yaml", encoding="utf-8"))
DATA = "2026-09-25"


def wym(sekcja, klucz):
    w = WYM[sekcja][klucz]
    return w["wartosc"], w["zrodlo"], w.get("id")


# ================================================================================================ PZT
def buduj_pzt(d) -> Dokument:
    pzt = Dokument("Projekt zagospodarowania działki", "PZT", d, data=DATA)
    pzt.oswiadczenie_projektanta()
    pzt.czesc_opisowa("Opis techniczny do projektu zagospodarowania działki", podstawa="§ 14 RPB")
    pzt.markdown(f"""
    Opracowanie sporządzono zgodnie z rozporządzeniem w sprawie szczegółowego zakresu i formy projektu budowlanego
    (t.j. Dz.U. 2022 poz. 1679 ze zm.) — dalej RPB — oraz, w zakresie wymagań techniczno-budowlanych,
    z rozporządzeniem w sprawie warunków technicznych (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowanym na podstawie
    art. 102a ust. 1 PB w związku z oświadczeniem Inwestora z dnia {do_uzup('data')}. Działka, ustalenia MPZP
    i sieci uzbrojenia są danymi przykładowymi {DANE_PRZYKLADOWE}.
    """)
    pzt.rozdzial("Przedmiot zamierzenia", f"""
    Przedmiotem zamierzenia jest budowa **budynku mieszkalnego jednorodzinnego wolnostojącego „Dom LAMELA”**
    (3 kondygnacje nadziemne, bez podpiwniczenia, garaż dwustanowiskowy w bryle parteru) wraz z:

    * zjazdem z drogi gminnej 1KDD (ul. Lipowa), dojazdem i dojściem, dwoma miejscami postojowymi dla gości;
    * tarasem naziemnym przy strefie dziennej, miejscem na pojemniki na odpady w osłonie;
    * zbiornikiem retencyjnym wód opadowych ≤ 5 m³ z przelewem do niecki chłonnej (wariant bazowy, rejestr D-05);
    * ogrodzeniem z bramą przesuwną i furtką;
    * przyłączami: wodociągowym, kanalizacyjnym i elektroenergetycznym nN {ZAL}.
    """, podstawa="§ 14 pkt 1 RPB")
    pzt.rozdzial("Istniejący stan zagospodarowania działki", f"""
    Działka nr ewid. 123/4 (obręb 0005 „Przykładowo”) o powierzchni 1600,00 m² jest **niezabudowana**; brak obiektów
    przeznaczonych do rozbiórki. Teren płaski, ze spadkiem ok. 0,6 % ku południowi; rzędne narożników
    101,10–101,55 m n.p.m. (PL-EVRF2007-NH). Od północy działka graniczy z drogą gminną 1KDD, od wschodu i zachodu
    z działkami zabudowy jednorodzinnej, od południa z terenem rolnym {DANE_PRZYKLADOWE}.
    """, podstawa="§ 14 pkt 2 RPB")
    pzt.rozdzial("Projektowane zagospodarowanie działki", podstawa="§ 14 pkt 3 RPB")
    pzt.markdown(f"""
    ## Układ komunikacyjny i dostęp do drogi publicznej {{podstawa: § 14 pkt 3 lit. c–d}}
    Dostęp do drogi publicznej — nowym zjazdem z drogi gminnej 1KDD o szerokości 5,00 m {ZAL}, na podstawie
    decyzji zarządcy drogi (załącznik ZL nr 2). Dojazd do garażu i miejsca postojowe z kostki betonowej na podbudowie,
    ze spadkiem od budynku; odwodnienie liniowe przed bramą wjazdową.

    ## Odprowadzanie ścieków i wód opadowych {{podstawa: § 14 pkt 3 lit. b}}
    Ścieki bytowe — przyłączem do sieci kanalizacji sanitarnej PVC 200 w drodze 1KDD. Wody opadowe z dachów
    i utwardzeń — do szczelnego zbiornika retencyjnego z przelewem do niecki chłonnej na terenie działki
    (WT § 28 ust. 2, § 29; Prawo wodne art. 234 ust. 1); zakaz odprowadzania na drogę (u.d.p. art. 39 ust. 1 pkt 9).
    """)
    pzt.rozdzial("Zestawienie powierzchni i wskaźników zagospodarowania", podstawa="§ 14 pkt 4 RPB")
    pow_dz = d["dzialka"]["pow_m2"]
    bilans = OrderedDict([("Powierzchnia zabudowy (obrys ścian zewnętrznych)", 262.40),
                          ("Dojazd, miejsca postojowe, dojścia, taras naziemny", 172.70),
                          ("Inne powierzchnie nieaktywne biologicznie (osłona odpadów, opaski żwirowe)", 12.30)])
    bilans["Powierzchnia biologicznie czynna (teren)"] = round(pow_dz - sum(bilans.values()), 2)
    pzt.tabela([{"Element zagospodarowania": k, "Powierzchnia [m²]": v, "Udział [%]": 100 * v / pow_dz}
                for k, v in bilans.items()], tytul="Bilans terenu działki nr ewid. 123/4", suma=True,
               formaty={"Udział [%]": 2}, etykieta_sumy="Powierzchnia działki",
               uwagi=[f"Wartości ilustracyjne {DANE_PRZYKLADOWE} — w projekcie generowane z `model/dzialka.yaml` "
                      "(kontrola AUD-PZT). Powierzchnia zabudowy wg RPB § 14 pkt 4 lit. a i PN-ISO 9836:2022-07; "
                      "dach zielony garażu nie jest wliczany do powierzchni biologicznie czynnej (rezerwa, W-031)."])
    u_zab, zr_zab, _ = wym("mpzp", "udzial_pow_zabudowy_max")
    u_pbc, zr_pbc, _ = wym("mpzp", "udzial_PBC_min")
    ints, zr_int, _ = wym("mpzp", "intensywnosc_zakres")
    hmax, zr_h, _ = wym("mpzp", "wys_zabudowy_max")
    kmax, zr_k, _ = wym("mpzp", "kondygnacje_nadziemne_max")
    mp, zr_mp, _ = wym("mpzp", "miejsca_postojowe_na_lokal_min")
    pc_nadz = 398.60
    zab = list(bilans.values())[0]
    pbc = list(bilans.values())[-1]
    pzt.tabela_wynikow([
        dict(parametr="Udział powierzchni zabudowy", wartosc=100 * zab / pow_dz, jedn="%",
             wymaganie=f"≤ {liczba(100 * u_zab, 0)} %", podstawa=zr_zab, spelnia=zab / pow_dz <= u_zab),
        dict(parametr="Udział powierzchni biologicznie czynnej", wartosc=100 * pbc / pow_dz, jedn="%",
             wymaganie=f"≥ {liczba(100 * u_pbc, 0)} %", podstawa=zr_pbc, spelnia=pbc / pow_dz >= u_pbc),
        dict(parametr="Intensywność zabudowy (nadziemna)", wartosc=pc_nadz / pow_dz, jedn="",
             wymaganie=f"{liczba(ints[0], 2)}–{liczba(ints[1], 2)}", podstawa=zr_int,
             spelnia=ints[0] <= pc_nadz / pow_dz <= ints[1]),
        dict(parametr="Wysokość zabudowy", wartosc=10.15, jedn="m", wymaganie=f"≤ {liczba(hmax, 1)} m",
             podstawa=zr_h, spelnia=10.15 <= hmax),
        dict(parametr="Liczba kondygnacji nadziemnych", wartosc="3", wymaganie=f"≤ {kmax}", podstawa=zr_k,
             spelnia=True),
        dict(parametr="Miejsca postojowe (garaż 2 + zewnętrzne 2)", wartosc="4", jedn="szt.",
             wymaganie=f"≥ {mp} na lokal", podstawa=zr_mp, spelnia=True),
    ], tytul="Zgodność z ustaleniami MPZP — teren 3MN (uchwała XII/123/2024, fikcyjna)",
        uwagi=[f"Wartości projektu ilustracyjne {DANE_PRZYKLADOWE}; wymagania z `docs/10_podstawy_prawne/wymagania.yaml`."])
    pzt.wykres(_wykres_bilansu(bilans, pow_dz, u_zab, u_pbc), szerokosc="100%",
               podpis="Struktura zagospodarowania działki na tle wskaźników MPZP (dane z tabeli 1)")
    pzt.rozdzial("Ograniczenia, zabytki, wpływ eksploatacji górniczej, zagrożenia dla środowiska", f"""
    Działka leży w terenie 3MN miejscowego planu (fikcyjnego); nie jest wpisana do rejestru ani gminnej ewidencji
    zabytków, nie leży na terenie górniczym ani zalewowym {DANE_PRZYKLADOWE}. Zamierzenie nie jest przedsięwzięciem
    mogącym znacząco oddziaływać na środowisko (rozp. RM, Dz.U. 2019 poz. 1839 § 3 ust. 1 pkt 55 lit. a) — decyzja
    środowiskowa nie jest wymagana. Jednostka zewnętrzna pompy ciepła ≥ 6,0 m od granicy wschodniej; poziom hałasu
    na granicy działek MN nie przekroczy 40 dB nocą (rozp. MŚ, t.j. Dz.U. 2014 poz. 112, tab. 1 lp. 2a) {ZAL}.
    """, podstawa="§ 14 pkt 5 RPB")
    pzt.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", """
    Budynek niski (N), ZL IV; droga pożarowa nie jest wymagana (rozp. MSWiA, Dz.U. 2009 nr 124 poz. 1030, § 12
    ust. 1). Dojście od drogi publicznej utwardzonym dojściem od furtki. Zaopatrzenie wodne do zewnętrznego gaszenia
    pożaru — z hydrantu na sieci wodociągowej w drodze 1KDD (§ 3 ust. 2 rozporządzenia) [DO UZUPEŁNIENIA: lokalizacja
    i wydajność najbliższego hydrantu wg gestora].
    """, podstawa="§ 14 pkt 6 RPB")
    pzt.rozdzial("Dane dotyczące ochrony ludności", "Nie dotyczy — budynek mieszkalny jednorodzinny nie jest obiektem "
                 "zbiorowej ochrony (ustawa o ochronie ludności i obronie cywilnej, art. 93–95a).",
                 podstawa="§ 14 pkt 6a RPB")
    pzt.rozdzial("Informacja o obszarze oddziaływania obiektu", """
    Obszar oddziaływania określono na podstawie przepisów: WT § 12, 13, 19, 23, 28–29, 60 i 271 (stosowanych na podstawie
    art. 102a PB), ustawy o drogach publicznych art. 43, POŚ art. 144 ust. 2 w związku z rozp. MŚ (t.j. Dz.U. 2014
    poz. 112), Prawa wodnego art. 234 oraz ustaleń MPZP (PB art. 3 pkt 20, art. 20 ust. 1 pkt 1c).

    **Obszar oddziaływania obiektu mieści się w całości na działce nr ewid. 123/4.**
    """, podstawa="§ 14 pkt 8, § 18 RPB")
    pzt.czesc_rysunkowa([
        Arkusz.planowany("PZT-01", "Plan zagospodarowania działki na mapie do celów projektowych", "1:500", "A3",
                         uwagi=do_uzup("mapa do celów projektowych z klauzulą (E-01)")),
        Arkusz.planowany("PZT-02", "Plan szczegółowy — wymiary, odległości, rzędne", "1:200", "A2"),
        Arkusz.planowany("PZT-03", "Rysunek koordynacyjny uzbrojenia terenu", "1:200", "A2"),
    ])
    return pzt


def _wykres_bilansu(bilans, pow_dz, u_zab, u_pbc):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 8, "svg.fonttype": "path"})
    kolory = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]    # paleta referencyjna (walidacja CVD: PASS)
    nazwy = ["zabudowa", "utwardzenia", "inne", "biologicznie czynna"]
    kolory = [kolory[0], kolory[1], kolory[3], kolory[2]]
    fig, ax = plt.subplots(figsize=(6.6, 1.55), dpi=100)
    x = 0.0
    for (k, v), c, n in zip(bilans.items(), kolory, nazwy):
        w = 100 * v / pow_dz
        ax.barh(0, w, left=x, height=0.4, color=c, edgecolor="white", linewidth=1.2)
        if w > 6:
            ax.text(x + w / 2, 0, f"{n}\n{liczba(w, 1)} %", ha="center", va="center", fontsize=7.4,
                    color="white" if c in ("#2a78d6", "#eb6834") else "#0b0b0b")
        else:
            ax.annotate(f"{n} {liczba(w, 1)} %", xy=(x + w / 2, -0.23), xytext=(x + w / 2 + 2.5, -0.56),
                        fontsize=7, color="#52514e", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.5, color="#52514e", shrinkA=0, shrinkB=0))
        x += w
    for pos, txt in ((100 * u_zab, f"MPZP: zabudowa ≤ {liczba(100 * u_zab, 0)} %"),
                     (100 - 100 * u_pbc, f"MPZP: biologicznie czynna ≥ {liczba(100 * u_pbc, 0)} % (od prawej)")):
        ax.plot([pos, pos], [-0.3, 0.52], color="#0b0b0b", lw=0.8, ls=(0, (3, 2)))
        ax.text(pos + 0.7, 0.52, txt, ha="left", va="top", fontsize=7, color="#0b0b0b")
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.72, 0.6)
    ax.set_yticks([])
    ax.set_xticks(range(0, 101, 10))
    ax.set_xticklabels([f"{t} %" for t in range(0, 101, 10)], fontsize=6.8, color="#52514e")
    ax.tick_params(axis="x", length=2, color="#9aa1a9", pad=2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#9aa1a9")
    ax.spines["bottom"].set_linewidth(0.6)
    fig.tight_layout(pad=0.3)
    return fig


# ================================================================================================ PAB
def _model_testowy():
    try:
        from lamela.model import load_model
        return load_model(REPO / "model/test/dom_testowy.yaml", REPO / "model/test/dzialka_testowa.yaml",
                          strict=False)
    except Exception as e:                   # pragma: no cover
        print("  (model testowy niedostępny:", e, ")")
        return None


def _nr_iso(pid: str, kond: str) -> str:
    """Identyfikator modelu „0.01” → numer na rysunkach wg PN-B-01025 (parter = 1): „1.01” (W-314)."""
    try:
        return f"{int(kond[1:]) + 1}.{pid.split('.')[1]}"
    except Exception:
        return pid


def buduj_pab(d, model, arkusze) -> Dokument:
    pab = Dokument("Projekt architektoniczno-budowlany", "PAB", d, data=DATA)
    pab.oswiadczenie_projektanta()
    pab.czesc_opisowa("Opis techniczny do projektu architektoniczno-budowlanego", podstawa="§ 20 RPB")
    pab.markdown(f"""
    Fragment demonstracyjny. Tabele pomieszczeń, stolarki i przegród wygenerowano automatycznie z **modelu testowego**
    `model/test/dom_testowy.yaml` (nie jest to model Domu LAMELA) — w projekcie źródłem jest `model/budynek.yaml`.
    Pozostałe wartości są przykładowe {DANE_PRZYKLADOWE}.
    """)
    pab.rozdzial("Rodzaj i kategoria obiektu budowlanego", """
    Budynek mieszkalny jednorodzinny wolnostojący (PB art. 3 pkt 2a), **kategoria I** — budynki mieszkalne
    jednorodzinne (załącznik do ustawy – Prawo budowlane). Kategoria geotechniczna II (rejestr K-1, D-08).
    """, podstawa="§ 20 ust. 1 pkt 1 RPB")
    pab.rozdzial("Zamierzony sposób użytkowania i program użytkowy", """
    Budynek przeznaczony do zaspokajania potrzeb mieszkaniowych jednej rodziny (4–5 osób), stanowiący jeden lokal
    mieszkalny wielopoziomowy z garażem dwustanowiskowym. Program pomieszczeń — tabela poniżej.
    """, podstawa="§ 20 ust. 1 pkt 2 RPB")
    if model is not None:
        rows, grupa = [], None
        for r in sorted(model.pomieszczenia(), key=lambda r: (r.kond, r.id)):
            if r.kond != grupa:
                grupa = r.kond
                rows.append(f"Kondygnacja {int(r.kond[1:]) + 1} — {model.kondygnacja(r.kond).nazwa.lower()}")
            rows.append({"Nr": _nr_iso(r.id, r.kond), "Nazwa pomieszczenia": r.nazwa,
                         "Kategoria wg PN-ISO 9836": r.kategoria, "Posadzka": model.material(r.posadzka).nazwa
                         if r.posadzka and model.material(r.posadzka) else "—",
                         "Wysokość w świetle [m]": r.wysokosc, "Pow. netto [m²]": r.pow_netto,
                         "Pow. użytkowa [m²]": r.pow_zaliczona})
        pab.tabela(rows, tytul="Zestawienie pomieszczeń (generowane z modelu)", klasa="zwarta",
                   suma=["Pow. netto [m²]", "Pow. użytkowa [m²]"],
                   szerokosci=["11mm", None, "24mm", "40mm", "18mm", "18mm", "19mm"],
                   formaty={"Wysokość w świetle [m]": 2}, wyrownanie={"Kategoria wg PN-ISO 9836": "l"},
                   uwagi=["Numeracja pomieszczeń wg PN-B-01025 (parter = 1.xx) — identyfikatory modelu 0.xx (W-314). "
                          "Powierzchnia użytkowa wg PN-ISO 9836:2022-07 z modyfikacjami RPB § 20 ust. 1 pkt 4 lit. b "
                          "(h ≥ 2,20 m — 100 %, 1,40–2,20 m — 50 %, < 1,40 m — 0 %)."],
                   zrodlo="model/test/dom_testowy.yaml (model testowy)")
    pab.rozdzial("Układ przestrzenny, forma architektoniczna, wyroby wykończeniowe i kolorystyka", """
    Trzy przesunięte względem siebie bryły kondygnacji tworzą w elewacji ogrodowej sylwetę „S”; głęboko wysunięte
    krawędzie płyt (0,8–1,2 m) pełnią funkcję okapów i osłon przeciwsłonecznych. Dachy płaskie, dach garażu zielony
    ekstensywny. Kolorystyka zgodna z ustaleniami MPZP (biele, szarości, grafit, drewno, beton).
    """, podstawa="§ 20 ust. 1 pkt 3 RPB")
    pab.tabela([
        {"Element": "Ściany zewnętrzne — tynk cienkowarstwowy", "Wyrób": "tynk silikonowy, faktura drobna", "Kolor": "biały, RAL 9010"},
        {"Element": "Bryła II piętra — lamele", "Wyrób": "drewno termojesion, 40×80 mm, rozstaw 120 mm", "Kolor": "naturalny, olejowany"},
        {"Element": "Krawędzie płyt, attyki", "Wyrób": "obróbki aluminiowe, beton architektoniczny", "Kolor": "grafit, RAL 7016"},
        {"Element": "Stolarka zewnętrzna", "Wyrób": "aluminium z przekładką termiczną, szyby 3-komorowe", "Kolor": "grafit, RAL 7016"},
        {"Element": "Balustrady", "Wyrób": "szkło VSG 44.2, pochwyt stalowy", "Kolor": "grafit, RAL 7016"},
    ], tytul="Wyroby wykończeniowe i kolorystyka elewacji", lp=True,
        uwagi=[f"Dobór przykładowy {DANE_PRZYKLADOWE}; zgodność z § MPZP „kolorystyka” (W-037)."])
    pab.rozdzial("Charakterystyczne parametry techniczne", podstawa="§ 20 ust. 1 pkt 4 RPB")
    if model is not None:
        pow_kat = OrderedDict()
        for r in model.pomieszczenia():
            pow_kat.setdefault(r.kategoria, 0.0)
            pow_kat[r.kategoria] += r.pow_zaliczona
        pu = sum(pow_kat.values())
        pab.tabela([{"Parametr": f"Powierzchnia — kategoria „{k}”", "Wartość": v, "Jedn.": "m²"} for k, v in pow_kat.items()]
                   + [{"_klasa": "suma", "Parametr": "Powierzchnia użytkowa (PU) lokalu", "Wartość": pu, "Jedn.": "m²"},
                      {"Parametr": "Liczba kondygnacji nadziemnych / podziemnych", "Wartość": f"{len(model.kondygnacje)} / 0", "Jedn.": "—"},
                      {"Parametr": "Kubatura brutto (PN-ISO 9836)", "Wartość": do_uzup("z modelu — AUD-WT"), "Jedn.": "m³"},
                      {"Parametr": "Wysokość budynku (WT § 6) / wysokość zabudowy (upzp)", "Wartość": do_uzup("z modelu"), "Jedn.": "m"}],
                   tytul="Parametry budynku (model testowy)", wyrownanie={"Wartość": "r", "Jedn.": "c"},
                   szerokosci=[None, "34mm", "14mm"], zrodlo="model/test/dom_testowy.yaml; RPB § 20 ust. 1 pkt 4 lit. a–d")
    pab.rozdzial("Opinia geotechniczna i sposób posadowienia", f"""
    Posadowienie bezpośrednie na piaskach średnich średniozagęszczonych (I_{{D}} ≈ 0,6), poniżej głębokości przemarzania
    h_{{z}} = 0,8 m; zwierciadło wody gruntowej ok. 3,8 m p.p.t. {DANE_PRZYKLADOWE}. **Opinia geotechniczna** ustalająca
    przydatność gruntów i kategorię geotechniczną (rozp. Dz.U. 2012 poz. 463 § 7 ust. 1, § 8) —
    [DOKUMENT ZEWNĘTRZNY – do dołączenia: opinia geotechniczna, geotechnik z uprawnieniami, rozp. 2012/463 § 8].
    """, podstawa="§ 20 ust. 1 pkt 5 RPB")
    pab.rozdzial("Liczba lokali; lokale dostępne; dostępność", """
    Budynek zawiera **1 lokal mieszkalny** i 0 lokali użytkowych (§ 20 ust. 1 pkt 6). Punkty 7 i 8 — nie dotyczy:
    wymagania dotyczą budynków wielorodzinnych i użyteczności publicznej (§ 20 ust. 1 pkt 7–8 RPB).
    """, podstawa="§ 20 ust. 1 pkt 6–8 RPB")
    pab.rozdzial("Wpływ na środowisko, zdrowie ludzi i obiekty sąsiednie", f"""
    Zapotrzebowanie na wodę z sieci ok. 0,6 m³/d; ścieki bytowe do sieci kanalizacyjnej; wody opadowe zagospodarowane
    na działce. Brak emisji spalin (budynek all-electric). Odpady komunalne — segregacja w miejscu gromadzenia odpadów.
    Źródło hałasu: jednostka zewnętrzna pompy ciepła (L_{{WA}} wg DTR wybranego modelu {do_uzup('dane wyrobu E-13')}).
    """, podstawa="§ 20 ust. 1 pkt 9 RPB")
    pab.rozdzial("Analiza wysoce wydajnych systemów alternatywnych", """
    Porównano: (A) kocioł gazowy kondensacyjny zasilany z sieci gazowej w drodze 1KDD oraz (B) pompę ciepła powietrze–woda
    z instalacją PV ≤ 6,5 kWp. Wybrano wariant B — niższy wskaźnik EP i zgodność z ustaleniami MPZP (źródła
    niskoemisyjne/OZE). Pełna analiza — PT-3 IS (rejestr W-157).
    """, podstawa="§ 20 ust. 1 pkt 10 RPB")
    pab.rozdzial("Analiza automatycznej regulacji temperatury", """
    Zastosowano ogrzewanie podłogowe z regulacją pokojową (termostaty w pomieszczeniach na pobyt ludzi) i pogodową
    regulacją temperatury zasilania — zgodnie z WT § 135 ust. 7–10 i § 147 ust. 5–7 (stosowanymi na podstawie art. 102a
    PB). Rozwiązanie jest technicznie i ekonomicznie uzasadnione (rejestr W-152).
    """, podstawa="§ 20 ust. 1 pkt 11 RPB")
    pab.rozdzial("Zasadnicze elementy wyposażenia budowlano-instalacyjnego", f"""
    Źródło ciepła i c.w.u.: pompa ciepła powietrze–woda (R290) z zasobnikiem; wentylacja mechaniczna nawiewno-wywiewna
    z odzyskiem ciepła; instalacja elektryczna TN-S, instalacja PV ≤ 6,5 kWp (PB art. 29 ust. 4 pkt 3 lit. c).
    Przegrody zewnętrzne (informacyjnie; rozwiązania szczegółowe w PT-1 AR):
    """, podstawa="§ 20 ust. 1 pkt 12 RPB")
    if model is not None:
        _przegroda(pab, model, "SZ1", ("energia", "U_max_sciana"), "poziomy", 0.13)
        _przegroda(pab, model, "SD-D1", ("energia", "U_max_stropodach"), "w górę", 0.10, od_zewnatrz=True)
    pab.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", podstawa="§ 20 ust. 1 pkt 13 RPB")
    pab.tabela([
        {"Parametr": "Wysokość / grupa wysokości", "Wartość": "budynek niski (N)", "Podstawa": "WT § 8 pkt 1"},
        {"Parametr": "Kategoria zagrożenia ludzi", "Wartość": "ZL IV", "Podstawa": "WT § 209 ust. 2 pkt 4"},
        {"Parametr": "Klasa odporności pożarowej", "Wartość": "wymagania nie stawia się", "Podstawa": "WT § 213 pkt 1 lit. a"},
        {"Parametr": "Ściany zewnętrzne i dach", "Wartość": "NRO", "Podstawa": "WT § 271; W-010, W-213"},
        {"Parametr": "Przeciwpożarowy wyłącznik prądu", "Wartość": "projektuje się", "Podstawa": "WT § 183 ust. 2; D-04"},
        {"Parametr": "Czujki dymu", "Wartość": "w pomieszczeniach na pobyt ludzi", "Podstawa": "ROPoż § 28a"},
    ], tytul="Dane przeciwpożarowe budynku", lp=True, zrodlo="rejestr wymagań B.11 (WT stosowane na podstawie art. 102a PB)")
    pab.rozdzial("Dane dotyczące ochrony ludności; odstępstwa", """
    Ochrona ludności — nie dotyczy (§ 20 ust. 1 pkt 14 RPB). Projekt nie wymaga odstępstw od przepisów
    techniczno-budowlanych (§ 20 ust. 2 RPB; PB art. 9).
    """, podstawa="§ 20 ust. 1 pkt 14, ust. 2 RPB")
    if model is not None:
        _stolarka(pab, model)
    pab.czesc_rysunkowa(arkusze)
    return pab


def _przegroda(dok, model, kod, klucz_umax, strumien, Rsi, od_zewnatrz=False):
    p = model.przegrody.get(kod) if isinstance(model.przegrody, dict) else model.przegroda(kod)
    if p is None:
        return
    warstwy = []
    for w in p.warstwy:
        m = model.material(w.mat)
        warstwy.append((m.nazwa if m else w.mat, w.d, m.lambda_ if m else None))
    umax, zr, wid = wym(*klucz_umax)
    dok.tabela_przegrody(p.nazwa, warstwy, kod=kod, Rsi=Rsi, U_max=umax, strumien=strumien, od_zewnatrz=od_zewnatrz,
                         podstawa_Umax=f"{zr}; {wid}", zrodlo="model/test/dom_testowy.yaml — sekcje materialy, przegrody")


def _stolarka(dok, model):
    grupy = OrderedDict()
    for o in model.otwory():
        if o.typ in ("otwor",):
            continue
        g = grupy.setdefault(o.symbol or o.id, dict(o=o, n=0, kond=set()))
        g["n"] += 1
        g["kond"].add(o.kond)
    typy = {"okno": "okno", "fix": "przeszklenie stałe", "drzwi_zewn": "drzwi zewnętrzne",
            "drzwi_przesuwne_HS": "drzwi przesuwne HS", "drzwi": "drzwi wewnętrzne"}
    oslony = {"zaluzja_zewn": "żaluzja zewn.", "roleta_zewn": "roleta zewn.", "screen_zip": "screen ZIP", "brak": "—"}
    u_ok, zr_ok, _ = wym("energia", "U_max_okno")
    u_dz, zr_dz, _ = wym("energia", "U_max_drzwi_zewn")
    rows = []
    for sym, g in grupy.items():
        o = g["o"]
        zewn = o.typ not in ("drzwi",)
        otw = o.otwieranie or {}
        rows.append({"Symbol": sym, "Rodzaj": typy.get(o.typ, o.typ),
                     "Wymiary w świetle muru [cm]": f"{round(o.szer * 100)} × {round(o.wys * 100)}",
                     "Parapet [cm]": round(o.parapet * 100) if o.typ in ("okno", "fix") else "—",
                     "Otwieranie": f"{otw.get('rodzaj', '—')}, {otw.get('strona', '')}".strip(", ") if otw else "stałe",
                     "Osłona": oslony.get(o.oslona or "brak", o.oslona), "Liczba [szt.]": g["n"],
                     "U_{max} [W/(m²·K)]": (u_dz if "drzwi_zewn" in o.typ else u_ok) if zewn else "—"})
    dok.tabela(rows, tytul="Zestawienie stolarki (generowane z modelu)", klasa="zwarta",
               formaty={"U_{max} [W/(m²·K)]": 1}, wyrownanie={"Otwieranie": "l", "Osłona": "l", "Symbol": "l"},
               szerokosci=["13mm", "31mm", "24mm", "14mm", None, "20mm", "13mm", "19mm"],
               uwagi=[f"U_{{max}}: okna i przeszklenia {liczba(u_ok, 1)} — {zr_ok}; drzwi zewnętrzne {liczba(u_dz, 1)} — "
                      f"{zr_dz}. Szczelność okien klasa ≥ 3 (WT zał. 2 pkt 2.3.2). Wartości U_{{w}} i g wybranych "
                      f"wyrobów {do_uzup('deklaracje producenta, E-13')}."],
               zrodlo="model/test/dom_testowy.yaml — otwory (grupowanie po symbolu)")


# ================================================================================================ ZL, WN, PT
def buduj_zl(d) -> Dokument:
    zl = Dokument("Załączniki", "ZL", d, data=DATA)
    zl.informacja_bioz()
    zl.dokument_zewnetrzny("Decyzja zarządcy drogi o lokalizacji zjazdu z drogi gminnej 1KDD",
                           organ=f"Wójt Gminy {d['dzialka']['gmina']} — zarządca drogi gminnej",
                           podstawa="art. 29 ust. 1 i 3a ustawy o drogach publicznych (t.j. Dz.U. 2025 poz. 889); "
                                    "PB art. 33 ust. 2 pkt 1",
                           uwagi="Zezwolenie wygasa, jeżeli zjazdu nie zbudowano w ciągu 3 lat (u.d.p. art. 29 ust. 5).")
    zl.oswiadczenie_sieci_cieplowniczej(zalacznik="Oświadczenie projektanta dotyczące sieci ciepłowniczej "
                                                  "(art. 33 ust. 2 pkt 10 PB)")
    return zl


def buduj_wn(d) -> Dokument:
    wn = Dokument("Dokumenty do wniosku o pozwolenie na budowę", "WN", d, data=DATA, projektanci=[],
                  podtytul="Wzory oświadczeń Inwestora — poza projektem budowlanym (rejestr C.0)",
                  stadium="WNIOSEK O POZWOLENIE NA BUDOWĘ", stadium_opis="formularz PB-1 (Dz.U. 2026 poz. 255)",
                  grupa_poczatkowa="wniosek")
    wn.oswiadczenie_inwestora_102a()
    wn.informacja_pb5()
    return wn


def buduj_pt_ar(d, model, arkusze) -> Dokument:
    pt = Dokument("Projekt techniczny", "PT-AR", d, kod="PT-1 AR", branza="architektura", data=DATA, tom=(1, 4),
                  podtytul="Tom PT-1 — architektura (AR)")
    pt.oswiadczenie_projektanta()
    pt.czesc_opisowa("Opis techniczny — architektura", podstawa="§ 23 RPB")
    pt.rozdzial("Rozwiązania konstrukcyjno-materiałowe przegród", f"""
    Przegrody zewnętrzne zaprojektowano z ciągłą warstwą izolacji cieplnej i szczelności powietrznej; łączniki
    termoizolacyjne wsporników i płyt wysuniętych wg PT-2 BO. Warstwy i obliczenie U — tabele poniżej {ZAL}.
    """, podstawa="§ 23 pkt 4 RPB")
    if model is not None:
        _przegroda(pt, model, "SZ1", ("energia", "U_max_sciana"), "poziomy", 0.13)
        _przegroda(pt, model, "POD-0", ("energia", "U_max_podloga_na_gruncie"), "w dół", 0.17)
        _przegroda(pt, model, "SD-D1", ("energia", "U_max_stropodach"), "w górę", 0.10, od_zewnatrz=True)
        _stolarka(pt, model)
    pt.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", """
    Klasy reakcji na ogień wyrobów elewacyjnych: ETICS — NRO jako system (WT § 216 w zw. z § 213); przejścia instalacyjne
    przez strop garażu — uszczelnienia wg PT-3 IS [NZW].
    """, podstawa="§ 23 pkt 10 RPB")
    pt.czesc_rysunkowa(arkusze)
    return pt


# ================================================================================================ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(DEMO / "dokumenty_demo"))
    ap.add_argument("--bez-widokow", action="store_true", help="nie dołączaj arkuszy z widoki_test/")
    a = ap.parse_args(argv)
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    d = dane_obiektu()
    model = _model_testowy()

    ark_demo = [Arkusz.z_pdf(p) for p in sorted(DEMO.glob("DEMO-*.pdf"))]
    ark_widoki = [] if a.bez_widokow else [Arkusz.z_pdf(p) for p in sorted((DEMO / "widoki_test").glob("T-AR-*.pdf"))]
    print(f"arkusze demo: {[x.nr for x in ark_demo]}; widoki modelu testowego: {[x.nr for x in ark_widoki]}")

    tom1 = Tom("TOM I", [buduj_pzt(d), buduj_pab(d, model, ark_widoki + ark_demo), buduj_zl(d)], dane=d, data=DATA)
    w1 = tom1.zloz(out)
    print(f"✓ {w1.nazwa}: {w1.strony} stron, {w1.rozmiar_mb:.2f} MB; elementy: "
          + ", ".join(f"{e['kod']} od s. {e['start']}" for e in w1.elementy))

    tom_pt = Tom("PT-1 AR", [buduj_pt_ar(d, model, ark_widoki or ark_demo)], dane=d, data=DATA, nr=1, symbol="AR",
                 strona_tytulowa=False, laczny_spis=False)
    w2 = tom_pt.zloz(out)
    print(f"✓ {w2.nazwa}: {w2.strony} stron, {w2.rozmiar_mb:.2f} MB")

    wn = buduj_wn(d)
    w3 = wn.render_pdf(out / f"WN_wzory_oswiadczen_{DATA.replace('-', '.')}.pdf")
    print(f"✓ {w3.sciezka.name}: {w3.strony_razem} stron")

    for w, lista in ((w1, "TOM_I"), (w2, "PT_AR")):
        r = sprawdz_tom(w, LISTY_KONTROLNE[lista])
        stem = w.sciezka.stem
        (out / f"raport_kompletnosci_{stem}.txt").write_text(r.tekst(), encoding="utf-8")
        r.zapisz_json(out / f"raport_kompletnosci_{stem}.json")
        s = r.podsumowanie()
        print(f"  walidator {stem}: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, "
              f"DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; "
              f"znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}")
        for p in r.braki:
            print(f"    ✗ {p.id} [{p.element}] {p.opis} — {p.szczegoly}")

    plan = plan_skladania([x for x in ark_widoki + ark_demo])
    (out / "plan_skladania.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    zamknij_przegladarke()
    print(f"gotowe w {time.time() - t0:.1f} s → {out}")


if __name__ == "__main__":
    main()
