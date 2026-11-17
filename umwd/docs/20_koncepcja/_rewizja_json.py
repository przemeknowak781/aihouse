#!/usr/bin/env python3
"""Rewizja v1.1 – zapis model/koncepcja.json (ten sam schemat i klucze; klucz `kondygnacja_sejmiku` bez zmian).

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_rewizja_json.py [--zapisz]
Bez --zapisz tylko sprawdza (diff kluczy, poprawność wielokątów). Liczby z `_rewizja_*.py`.
Przekształcenie jest idempotentne (ponowne uruchomienie na pliku v1.1 daje ten sam wynik).
"""
import copy
import json
import os
import sys

from shapely.geometry import Polygon
from shapely.validation import explain_validity

sys.path.insert(0, os.path.dirname(__file__))
import _rewizja_wspolne as WS
from _rewizja_wspolne import ROOT, K, W, M, SEG, level_m1, level_m2, uv2en, rect_uv, unary_union, sd2en, rect_sd

OUT = os.path.join(ROOT, "model", "koncepcja.json")


def ring(g, nd=3):
    c = [(round(x, nd), round(y, nd)) for x, y in g.exterior.coords[:-1]]
    if not Polygon(c).exterior.is_ccw:
        c = c[::-1]
    return [list(p) for p in c]


def en_rect(u0, v0, u1, v1):
    return [list(map(lambda x: round(x, 3), uv2en(u, v))) for u, v in ((u0, v0), (u1, v0), (u1, v1), (u0, v1))]


def build():
    d = copy.deepcopy(K)
    sejm_before = json.dumps(K["kondygnacja_sejmiku"], sort_keys=True)
    m = d["meta"]
    m["wersja"] = "1.1 (po weryfikacji)"
    m["data_wersji"] = "17.11.2026"
    m["rejestr_poprawek"] = "docs/20_koncepcja/rejestr_poprawek_v1_1.md (dowody: docs/20_koncepcja/_rewizja_*.py)"
    m["kondygnacja_S_v1_1"] = "kondygnacja S – patrz docs/20_koncepcja/kondygnacja_S2.md i kondygnacja_S2.json (v1.1); klucz kondygnacja_sejmiku = stan 1.0"
    m["zrodla"] = sorted(set(m.get("zrodla", []) + ["docs/20_koncepcja/rejestr_poprawek_v1_1.md", "docs/30_lokalizacja/dendrologia.md"]))

    # ---------------------------------------------------------------- bryły
    b = {x["id"]: x for x in d["bryly"]}
    b["W"]["luk"]["R_szyb_korony"] = 13.4
    b["W"]["luk"]["lamele_korony"] = "R 13,40–14,00; 0,35 × 0,60 m; rozstawy 1,35 / 0,675 m w ciągu Fibonacciego; ceramika S 4005-Y20R, sitodruk 30 % na szkle"
    b["W"]["dach"]["attyka"]["wysiegi_m"] = 0.0
    b["W"]["dach"]["zwody"] = "niskie, ≤ korony attyki; wyłaz płaski przy trzonie B"
    b["M"]["obrys_ccw"] = ring(M)
    b["M"]["pow_rzutu_m2"] = round(M.area, 2)
    b["M"]["dach"]["najnizszy_pkt_pokrycia"].update({"nad_najwyzszym_terenem": 20.07, "zapas": 2.07})
    b["M"]["dach"]["gzyms_attyka"].update({"nad_najnizszym_terenem": 21.79,
                                           "wysiegi_m": {"lica_przy_granicy_(zach., pd., dziób pn.)": 0.0, "lico_dziedzincowe": 0.30},
                                           "fryz_wklesly_m": 0.15})
    b["S"]["dach"]["attyka"]["sciana_pd_npm"] = 139.10
    b["S"]["dach"]["attyka"]["balustrada_szklana"] = "1,10 m, cofnięta 1,5 m od lica pd. (140,20)"
    b["S"]["dach"]["attyka"]["wysiegi_m"] = {"lico_wsch_(Wybrzeze)": 0.0, "lico_zach_(dziedziniec)": 0.30}
    b["S"]["dach"]["taras_pow_m2"] = 135.3
    b["S"]["dach"]["strop_wierzch"] = 19.1      # P-D10: 0,70 m na izolację, spadki, retencję 10 m³ i donice; kond. 4 segmentu 2,87 m w świetle
    d["zabudowa"] = {"pow_zabudowy_m2": 2165.8, "udzial_w_OI_proc": 58.1}

    # ---------------------------------------------------------------- kondygnacje i siatka
    for k in d["kondygnacje"]:
        if k["kondygnacja"] == "4":
            k["strop_nad"].update({"dach_segmentu_wierzch": 19.1, "dach_segmentu_spod": 18.82})
        if k["kondygnacja"] == "-2":
            k.update({"posadzka_wzgl": -7.2, "posadzka_npm": 112.1, "wysokosc_kondygnacji": 3.0,
                      "zakres": ["wieza", "segment", "pas dziedzinca 5 m", "skrzydlo od s = 12,15 (bez M1 przy Maz. 19)"],
                      "plyta_denna": {"wierzch": -7.3, "spod": -8.4, "spod_npm": 110.9, "grubosc_wieza_m": 1.1, "grubosc_poza_wieza_m": 0.9},
                      "strop_nad": {"wierzch": -4.2, "spod_wieza": -4.55}, "wys_w_swietle": 2.65})
        if k["kondygnacja"] == "-1":
            k.update({"posadzka_wzgl": -4.2, "posadzka_npm": 115.1, "wysokosc_kondygnacji": 4.2,
                      "zakres": ["calosc (lico 0,15 m od dz. 8/8, 1,20 m od Maz. 19)", "pas dziedzinca 5 m"],
                      "strop_nad": {"wierzch": -0.15, "spod_wieza": -0.55}, "wys_w_swietle": 3.65,
                      "uwaga": "wysokość 4,20 m dla stackerów zależnych 2-poziomowych (≥ 3,50 m w świetle)"})
    s = d["siatka"]
    s["wieza"]["osie_v"] = [0.0, 8.7, 16.0, 23.15, 29.7]
    s["wieza"]["uwaga_osie_v"] = ("v1.1: słupy poza drogami garażu i w licach ścian korytarzy (v 8,70 i 23,15 jako 0,60 × 0,35 m); "
                                  "dodatkowa oś v 16,00 w strefie środkowej; rozpiętości 8,70 / 7,30 / 7,15 / 6,55 m")
    s["wieza"]["strop"] = "płyta sprężona 0,28 m z aktywacją termiczną (TABS), rozpiętości ≤ 8,70 m"
    s["skrzydlo"]["trakt_m"] = "15,00 = 0,47 + 6,08 + 0,10 + 1,70 + 0,10 + 6,08 + 0,47"
    p = s["posadowienie"]
    p["wieza"] = "płyta palowo-fundamentowa 1,10 m na −2 (spód 110,90 m n.p.m.), 36 pali CFA Ø 0,8 m L ≈ 14 m (energetyczne) do glin zwałowych QpB"
    p["skrzydlo_segment"] = "płyta 0,90 m na −2 (skrzydło od s 12,15, segment, pas) i na −1 (M1); pas dziedzińca: mikropale kotwiące (121,5 m²)"
    p["obudowa"] = ("ściany szczelinowe 0,60 m (energetyczne), 222,6 m × 19 m = 4 229 m², wcięte w gliny QpB; przy Maz. 19 (15,0 m) ściana "
                    "z kolumn iniekcji strumieniowej Ø 1,2 m z podbiciem fundamentu szczytu, lico −1 1,20 m od granicy; przy dz. 8/8 lico zewn. "
                    "ściany 0,15 m od granicy, ściana prowadząca zewn. tymczasowo w pasie drogowym (zezwolenie ZDiUM); biała wanna; bez kotew "
                    "poza granicą; bez odwodnienia regionalnego")
    p["sondy_GPC"] = "58 × 91 m pod płytą −2 (siatka 6,0 × 6,0 m), dno 19,9 m n.p.m. ≤ 99,5 m p.p.t. (poza art. 86 PGiG)"

    # ---------------------------------------------------------------- rdzenie
    r = d["rdzenie"]
    r["A"]["sklad"][1] = "dźwig A1 1 600 kg (os.), kabina 1,5 × 2,1 m, przelotowa"
    r["A"]["sklad"][2] = "dźwig A2 1 600 kg (os.), kabina 1,5 × 2,1 m, przelotowa"
    r["B"]["sklad"] = ["klatka B obudowana REI 60, biegi 1,60 m, przedsionek ppoż. z MOE i interkomem, nadciśnienie",
                       "dźwigi publiczne P1, P2 1 600 kg, kabiny 1,5 × 2,1 m (przystanki −2…6, S, antresola)",
                       "szacht (≈ 4 m², po dźwigu T): przewód spalin agregatu, wyrzut wentylacji i oddymiania garażu, piony centrali S → lamele korony od pd.",
                       "szachty"]
    r["C"]["sklad"][1] = "szyb C1 w stanie surowym – rezerwa (przyszłe połączenie z Mazowiecką 19), bez urządzenia dźwigowego"
    r["T"] = {"obrys_uv": [[36.9, -9.7], [39.2, -9.7], [39.2, -6.45], [36.9, -6.45]], "obrys_en": en_rect(36.9, -9.7, 39.2, -6.45),
              "zakres": "−2…4 (segment)", "sklad": ["dźwig T osobowo-towarowy 2 000 kg, kabina 1,5 × 2,7 m – narożnik SE segmentu (P-I5); "
                                                   "parter: drzwi od Wybrzeża, punkt wystawienia odpadów"]}

    # ---------------------------------------------------------------- podziemie
    L1, L2 = level_m1(), level_m2()
    pz = d["podziemie"]
    pz["-1"].update({"obrys_ccw": ring(L1), "pow_m2": round(L1.area, 1), "miejsca": 70, "posadzka_wzgl": -4.2,
                     "miejsca_opis": "38 na posadzce + 32 w stackerach (16 jednostek podwójnych), w tym 6 OzN 3,60 × 5,00 m"})
    pz["-2"].update({"obrys_ccw": ring(L2), "pow_m2": round(L2.area, 1), "miejsca": 40, "posadzka_wzgl": -7.2})
    pz["razem_miejsc"] = 110
    pz["wymagane_MPZP"] = {"PU_m2": 8850.37, "PU_gastronomia_m2": 88.47, "wymagane": 106, "odczyt_ostrozny": 108,
                           "wzor": "12/1000 × (PU − PU_gastr.) + 6/1000 × PU_gastr. = 105,67 → 106"}
    pz["stackery"] = {"typ": "zależne 2-poziomowe bez zagłębienia, jednostki podwójne 5,0 m", "jednostki": 16, "miejsca_gorne": 32,
                      "wys_w_swietle_min_m": 3.5, "rzedy": "−1: skrzydło zach., R1, R2, R3, R4 (pracownicy z przydziałem parami)"}
    pz["rampa"] = {"wjazd": "elewacja wsch. segmentu (6KDB/2), brama 4,0 m, v −0,40…−4,40", "pochylenie_max_proc": 18, "przejscia_proc": 9,
                   "prog_npm": 119.1, "szerokosc_m": 3.5, "pas_v": [-0.35, -3.85], "dlugosc_m": 25.22,
                   "zapora": "samoczynna przeciwpowodziowa do 120,30 we wnęce bramy + odwodnienie liniowe i pompownia",
                   "strop_przy_licu_zach_segmentu_npm": 118.53, "sygnalizacja": "wahadłowa (jednopasowa)",
                   "rampa_wewnetrzna": {"miejsce": "kieszeń wsch. wieży u 34,6–38,5", "dlugosc_m": 19.67, "pochylenie_max_proc": 18,
                                        "szerokosc_m": 3.5, "z": "−1 (v 16,6)", "do": "−2 (segment)"}}
    pz["MDS"] = {"pojemnosc_os": 560, "ukrycie_-2_os": 300, "MDS_-1_os": 260,
                 "wyjscia": "−2: klatki A, B; −1: klatka C, rampa, szyb wyjścia zapasowego (91,75; 32,00) + tunel 7,6 m",
                 "sanitariaty": "−1 pn. od trzonu A 30 m² z WC dostępnym; −2 WC ukrycia 15 m²"}
    pz["technika"] = {"-1": "warsztat PPT, odpady, magazyn MDS (M1); sanitariaty MDS, pralnia (pn. od trzonu A); centrala S (wsch. od trzonu B); "
                            "woda szara MBR (łuk); przyłącze wody (pod rampą); korytarz do dźwigu T",
                      "-2": "maszynownia GPC (przy trzonie B); filtrowentylacja ukrycia; zbiornik deszczówki 50 m³ (łuk)",
                      "tryskacze": "nieprojektowane (nieobowiązkowe – ppoz.md 7.3)"}

    # ---------------------------------------------------------------- elewacje
    e = d["elewacje"]
    e["materialy"][0]["NCS_cokol"] = "S 3502-Y (płomieniowany, ta sama rodzina)"
    e["materialy"][1]["NCS"].update({"M3": "S 2005-Y20R", "M4": "S 1510-Y30R", "lamele_korony": "S 4005-Y20R"})
    e["materialy"][1]["gdzie"] = "skrzydło i segment od ulic, pasma łuku, lamele korony; elewacje dziedzińcowe skrzydła i segmentu – tynk mineralny w tonie posesji"
    e["materialy"][2]["gdzie"] = "stolarka, ościeża wieży (0,45 m) i skrzydła (0,35 m), płyciny wieży (od dziedzińca ≤ 25 m jako BIPV w tym kolorze), kondygnacja 6, obróbki, żaluzje czerpni i wyrzutni (tylko od dziedzińca)"
    sk = e["skrzydlo"]
    sk.update({"okno_m": [1.2, 2.35], "parapet_m": 0.6, "kwatera_stala_do_m": 0.9, "nadproze_m": 2.95, "WWR": 0.371, "osciez_m": 0.35,
               "relief_opis": "cofnięcie wypełnień za lico filarów (lico filarów = obrys)",
               "gzyms": {"wysieg_lica_przy_granicy_m": 0.0, "wysieg_dziedziniec_m": 0.3, "fryz_wklesly_m": 0.15}})
    e["wieza"].update({"parapet_m": 0.55, "nadproze_m": 3.0, "osciez_m": 0.45, "osciez_material": "blacha Al lakierowana proszkowo RAL 8019"})
    e["luk"]["S"] = ("lamele ceramiczne pionowe 0,35 × 0,60 m (R 13,40–14,00), rozstawy 1,35 / 0,675 m w ciągu Fibonacciego, ton w ton "
                     "(S 4005-Y20R + sitodruk 30 %), przesłonięcie w osi 32 %, pełne od 59°")
    e["U_scian"] = {"wieza": 0.147, "skrzydlo_segment": 0.144, "opis": "wełna 260 λ 0,033 (wieża) / 240 λ 0,031 (skrzydło), konsole nierdzewne z przekładką"}
    e["PV"] = {"BIPV_dach_kWp": 351, "BIPV_elewacje_kWp": 52, "BIPV_zadaszenie_kWp": 13, "razem_kWp": 415, "MWh_rok": 328,
               "pola": {"dach_wiezy_m2": 948, "dach_skrzydla_m2": 685, "plyciny_wiezy_m2": 82, "sciana_pd_segmentu_m2": 295,
                        "zadaszenie_tarasu_ogrodowego_m2": 80},
               "gestosc_dach_kWp_m2": 0.215, "warunek": "sprawność modułów ≥ 22,5 %"}

    # ---------------------------------------------------------------- zagospodarowanie
    z = d["zagospodarowanie"]
    z.update({"drzewa_usuniete": ["D701", "D702", "D703", "D704", "D867", "D868", "D882", "D897"],
              "drzewa_usuniete_M06": [1, 2, 60, 61, 67, 79, 80, 81], "drzewa_przesadzane_M06": [72],
              "drzewa_U_sanitarnie_M06": [5, 13, 18, 19, 20, 38, 53, 57, 59, 62],
              "drzewa_chronione_palisada": ["I881"],
              "drzewa_chronione_opis": "nr 78 M.06 (= I881): wygrodzenie korona + 1 m, odkrywki ręczne, nadzór arborysty; bez palisady",
              "drzewa_w_OI_numery": 44, "zachowane_numery": 36, "zachowane_po_usunieciach_sanitarnych": 26,
              "drzewa_ogrodkow_zachowane": "28 drzew M.06 w ogródkach: 19 w miejscu, 1 przesadzane (72), 8 U sanitarnie, 0 kolizyjnie",
              "nowe_nasadzenia": 26, "retencja_m3": 157, "V60_C10_m3": 70,
              "sciezki": "poza poligonem ogródków (obrzeżem); w ogródkach tylko istniejące ścieżki"})

    # ---------------------------------------------------------------- bilans, § 13
    d["bilans"] = {"PZ_m2": 2165.8, "PC_nadziemna_m2": 14164.5, "PC_podziemna_m2": round(L1.area + L2.area, 1), "PU_m2": 8850.37,
                   "PU_definicja": "PN-ISO 9836 – pomieszczenia kategorii PU (model pomieszczeń, F.15.A); bez RU, US, PG",
                   "KW_m3": 81408, "PBC_m2": 1185, "koszt_mln_netto": 149.18, "koszt_model_F14B_mid_mln": 142.8,
                   "koszt_roboty_KS_mln": 142.08, "rezerwa_proc": 5, "rezerwa_mln": 7.1, "zapas_do_limitu_mln": 0.82,
                   "zl_m2_PC": 8003, "zl_m2_PU": 16856, "EP_kWh_m2": 28.0, "EPB_kWh_m2": 23.9}
    ps = d["par13"]["segment"]
    ps["wariant_ostrozny_H_od_120_0"] = {"H": 19.10, "wymagane": 9.55, "min_odl": 11.13, "zapas": 1.58,
                                          "uwaga": "attyka ściany pd. 139,10; balustrada 140,20 cofnięta 1,5 m: 12,63 ≥ 10,10 (zapas 2,53)"}
    ps["okno_pokoju_lok_6_6A"] = {"H": 15.10, "wymagane": 7.55, "odl": 11.13, "zapas": 3.58}
    d["par13"]["wieza"].update({"min_odl_dowolne_okno": 19.0, "zapas": 1.5})

    # ---------------------------------------------------------------- parter, piętra
    for zz in d["parter"]["skrzydlo"]:
        g = Polygon(zz["en"])
        if g.intersection(W).area > 0.5:
            cl = g.intersection(M)
            zz["en"] = ring(cl)
            if zz["strefa"].startswith("Bistro"):
                zz["strefa"] = f"Bistro {cl.area:.1f} m² brutto (sala 62 + zaplecze 20, bez kuchni gorącej), taras na skwerze; wejście konferencyjne w dziobie NW"
            else:
                zz["strefa"] = f"Foyer, szatnia, WC konferencyjne, magazyn mebli (+10 m² z bistro) – {cl.area:.1f} m² brutto"
    d["parter"]["segment"] = [{"strefa": "Rampa 1 × 3,50 m (≤ 18 %) przy ścianie pn., brama 4,0 m od Wybrzeża (v −0,40…−4,40), próg 119,10 + zapora samoczynna"},
                              {"strefa": "Pas pd.: trafo SN/nn 21 m² (drzwi od Wybrzeża, wentylacja do lica zach.), rozdzielnia nn z SZR 17, BESS 150 kWh 11 (EI 120), punkt odpadów 7, szyb T (narożnik SE)"},
                              {"strefa": "Kond. 1: agregat HVO (pas zach.); kond. 2: falowniki PV 12 m²; kond. 4: dry-cooler 2 × 150 kW (żaluzje w licu zach.)"}]
    kb = d["kondygnacje_biurowe"]
    kb["pojemnosc_jedn"] = {"1-4": 43, "5": 22, "6": 20, "P": 4, "razem": 218, "zajete": 216.1,
                            "uwaga": "wg suchej próby modelu pomieszczeń (docs/70_rysunki/rzuty_raport.md)"}
    for rr in kb["rozmieszczenie"]:
        if rr["kond"] == "5":
            rr.update({"komorki": {"DSS": 19, "DRA": 2}, "pokoje": 21, "sale_narad": 0, "magazynki": 1,
                       "inne": "wyjście na taras nad Oławą (135 m²); DRA 5.2 (Wyj. 17 odp. 70)"})
        if rr["kond"] == "6":
            rr.update({"komorki": {"KS": 8, "DRA": 9}, "pokoje": 17,
                       "inne": "gabinet Przewodniczącego 48 + zaplecze 8 + asystent 24 (łuk NE), 3 × Wiceprzewodniczący 24 (elewacja), "
                               "sala spotkań KS.05 2 × 44 dzielona (strefa środkowa, doświetlenie pośrednie), miejsca oczekiwania KS.06 i DRA.OCZ – wnęki holu"})
        if rr["kond"] == "4":
            rr["sale_narad"] = 2
            rr["inne"] = "sala narad z kond. 5"
    kb["sumy"]["WC_m2_min"] = 380
    kb["centrale_pietrowe"] = ("25 m² w strefie środkowej wieży na kond. 1–5 (kond. 5 obsługuje 5 i 6) + centrala parteru na kond. 1 (pas zach.); "
                               "centrala S na −1 przy trzonie B; czerpnia: płyciny elewacji pd. kond. P/1 i 1/2 (u 2–12, 17 m²); wyrzutnia: lamele korony od pd.")
    d["wysokosci_w_swietle"].update({"garaz_-1": 3.65, "garaz_-2": 2.65})
    assert json.dumps(d["kondygnacja_sejmiku"], sort_keys=True) == sejm_before
    return d


def validate(d):
    ok = True
    for b in d["bryly"]:
        g = Polygon(b["obrys_ccw"])
        print(f"  bryla {b['id']}: valid={g.is_valid} ({explain_validity(g)}), CCW={g.exterior.is_ccw}, pole={g.area:.2f}")
        ok &= g.is_valid and g.exterior.is_ccw
    for k in ("-1", "-2"):
        g = Polygon(d["podziemie"][k]["obrys_ccw"])
        print(f"  podziemie {k}: valid={g.is_valid}, CCW={g.exterior.is_ccw}, pole={g.area:.1f}")
        ok &= g.is_valid
    for k, v in d["cofniecia_wneki"].items():
        if isinstance(v, dict) and "obrys_ccw" in v:
            g = Polygon(v["obrys_ccw"])
            print(f"  {k}: valid={g.is_valid}")
            ok &= g.is_valid
    for zz in d["parter"]["skrzydlo"] + [x for x in d["parter"]["wieza"] if "en" in x]:
        g = Polygon(zz["en"])
        ok &= g.is_valid
    for pomk, pom in d["kondygnacja_sejmiku"]["pomieszczenia"].items():
        for poly in pom.get("obrys_en", []):
            pass
    print("  wszystkie wielokąty poprawne:", ok)
    return ok


def main():
    d = build()
    old_keys = set(K.keys())
    new_keys = set(d.keys())
    print("klucze najwyższego poziomu: usunięte", old_keys - new_keys, "dodane", new_keys - old_keys)
    ok = validate(d)
    txt = json.dumps(d, ensure_ascii=False, indent=1)
    json.loads(txt)
    if "--zapisz" in sys.argv and ok:
        open(OUT, "w", encoding="utf-8").write(txt + "\n")
        print("zapisano", os.path.relpath(OUT, ROOT), len(txt), "B")


if __name__ == "__main__":
    main()
