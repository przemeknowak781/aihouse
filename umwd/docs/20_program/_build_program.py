# -*- coding: utf-8 -*-
"""Generator ekstrakcji programu uzytkowego (M.01) -> program.yaml, program_tabela.csv.

Uruchomienie (z dowolnego katalogu):  python3 -I _build_program.py <katalog_wyjsciowy>
Dane wpisane recznie po lekturze zrodel (PU = "Program uzytkowy budynku administracyjnego
UWMD zatwierdzony 11_2025.pdf", numeracja stron = numer drukowany w stopce; PDF = s.+1).
Wartosci oznaczone szacunek=True NIE pochodza z M.01 - sa wnioskiem wlasnym (wskazniki m2/os.).
"""
import csv
import math
import sys
from collections import OrderedDict

import yaml

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

# ---------------------------------------------------------------------------
# 1. Zalacznik nr 1 PU (s.19) - zweryfikowane z obrazem strony (PDF s.20)
#    (nr, nazwa, dyr, zast, samodz, sekr, prac, razem)
# ---------------------------------------------------------------------------
Z1 = [
    ("KS", [("1", "Kancelaria Sejmiku", 1, 2, 0, 2, 11, 16)]),
    ("DOS", [
        ("2", "Departament Ochrony Środowiska - dyrekcja", 1, 0, 0, 1, 0, 2),
        ("2.1", "Wydział Opłat Środowiskowych - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("2.1.1", "Dział Opłat Produktowych", 0, 0, 0, 0, 14, 14),
        ("2.1.2", "Dział Opłat za Korzystanie ze Środowiska i BDO", 0, 0, 0, 0, 18, 18),
        ("2.1.3", "Dział Księgowości", 0, 0, 0, 0, 6, 6),
        ("2.2", "Wydział Instrumentów Środowiskowych - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("2.2.1", "Dział Emisji do Powietrza", 0, 0, 0, 0, 9, 9),
        ("2.2.2", "Dział Gospodarki Wodno-Ściekowej", 0, 0, 0, 0, 6, 6),
        ("2.2.3", "Dział Sprawozdawczości", 0, 0, 0, 0, 7, 7),
        ("2.2.4", "Dział Gospodarki Odpadami", 0, 0, 0, 0, 14, 14),
        ("2.2.5", "Dział Planowania i Koordynacji w Gospodarce Odpadami", 0, 0, 0, 0, 17, 17),
    ]),
    ("DSS", [
        ("3", "Departament Spraw Społecznych i Rynku Pracy - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("3.1", "Dział ds. Wdrażania i Realizacji Projektów", 0, 0, 0, 0, 7, 7),
        ("3.2", "Koordynator", 0, 0, 1, 0, 0, 1),
        ("3.3", "Wydział Edukacji - Dyrekcja", 1, 0, 0, 0, 0, 1),
        ("3.3.1", "Dział Rozwoju Szkolnictwa", 0, 0, 0, 0, 6, 6),
        ("3.3.2", "Dział Ekonomiczno-Finansowy", 0, 0, 0, 0, 4, 4),
        ("3.4", "Wydział Integracji Społecznej - Dyrekcja", 1, 0, 0, 0, 10, 11),
        ("3.5", "Wydział Polityki Senioralnej i Projektów Społecznych - Dyrekcja", 1, 0, 0, 0, 6, 7),
    ]),
    ("DST", [
        ("4", "Departament Sportu i Turystyki", 1, 0, 0, 1, 0, 2),
        ("4.1", "Wydział Sportu - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("4.1.1", "Dział Sportu Powszechnego i Szkolenia Sportowego", 0, 0, 0, 0, 7, 7),
        ("4.1.2", "Dział Inwestycji i Modernizacji Infrastruktury Sportowej", 0, 0, 0, 0, 3, 3),
        ("4.2", "Wydział Turystyki - Dyrekcja", 1, 0, 0, 0, 0, 1),
        ("4.2.1", "Dział Usług Turystycznych", 0, 0, 0, 0, 4, 4),
        ("4.2.2", "Dział Rozwoju i Promocji Turystyki", 0, 0, 0, 0, 5, 5),
    ]),
    ("DRA", [
        ("5", "Departament Rozwoju Aglomeracji - Dyrekcja", 1, 0, 2, 0, 0, 3),
        ("5.1", "Wydział ds. Aglomeracji", 1, 0, 0, 0, 2, 3),
        ("5.2", "Wydział Analiz i Rozwoju", 1, 0, 0, 0, 3, 4),
        ("5.3", "Planowany Wydział", 1, 0, 0, 0, 7, 8),
    ]),
    ("DGP", [
        ("6", "Departament Gospodarki i Promocji - Dyrekcja", 1, 1, 0, 2, 0, 4),
        ("6.1", "Stanowisko ds. Budżetu Departamentu", 0, 0, 1, 0, 0, 1),
        ("6.2", "Wydział Rozwoju Regionalnego - Dyrekcja", 1, 2, 0, 0, 0, 3),
        ("6.2.1", "Dział Planowania Strategicznego", 0, 0, 0, 0, 10, 10),
        ("6.2.2", "Dział Rewitalizacji i Analiz", 0, 0, 0, 0, 5, 5),
        ("6.2.3", "Dział Programu Regionalnego", 0, 0, 0, 0, 8, 8),
        ("6.2.4", "Dział Programów Europejskiej Współpracy Terytorialnej", 0, 0, 0, 0, 6, 6),
        ("6.2.5", "Dział Innowacji", 0, 0, 0, 0, 7, 7),
        ("6.2.6", "Dział Współpracy Gospodarczej i Przedsiębiorczości", 0, 0, 0, 0, 7, 7),
    ]),
    ("DI", [
        ("7", "Departament Infrastruktury - Dyrekcja", 1, 1, 0, 1, 0, 3),
        ("7.1", "Wydział Transportu - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("7.1.1", "Dział Nadzoru Jednostek Certyfikujących", 0, 0, 1, 0, 7, 8),
        ("7.1.2", "Dział Inżynierii Ruchu", 0, 0, 0, 0, 6, 6),
        ("7.1.3", "Dział Transportu Autobusowego", 0, 0, 0, 0, 10, 10),
        ("7.1.4", "Dział Transportu Kolejowego", 0, 0, 0, 0, 9, 9),
        ("7.1.5", "Dział Rozwoju Ruchu Rowerowego", 0, 0, 0, 0, 3, 3),
        ("7.2", "Wydział Mienia Wojewódzkiego - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("7.2.1", "Dział Zarządzania Nieruchomościami", 0, 0, 0, 0, 8, 8),
        ("7.2.2", "Dział Sprzedaży Nieruchomości", 0, 0, 0, 0, 3, 3),
    ]),
    ("CZ", [("8", "Członek Zarządu", 1, 0, 1, 1, 0, 3)]),
    ("DKD", [
        ("8.1", "Departament Kultury i Dziedzictwa Kulturowego - Dyrekcja", 1, 0, 0, 1, 0, 2),
        ("8.1.1", "Wydział Kultury - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("8.1.1.1", "Dział Instytucji Kultury, Finansów i Inwestycji", 0, 0, 0, 0, 6, 6),
        ("8.1.1.2", "Dział Współpracy ze Środowiskiem Kultury", 0, 0, 0, 0, 7, 7),
        ("8.1.2", "Wydział Dziedzictwa Kulturowego", 1, 0, 0, 0, 5, 6),
    ]),
    ("DZ", [
        ("8.2", "Departament Zdrowia - Dyrekcja", 1, 0, 0, 1, 0, 2),
        ("8.2.1", "Wydział Nadzoru Finansowego i Restrukturyzacji - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("8.2.1.1", "Dział Analiz Systemowych i e-zdrowia", 0, 0, 0, 0, 5, 5),
        ("8.2.1.2", "Dział Kontrolingu Finansowego", 0, 0, 0, 0, 3, 3),
        ("8.2.1.3", "Dział Organizacji i Budżetowania", 0, 0, 0, 0, 3, 3),
        ("8.2.2", "Wydział Zdrowia - Dyrekcja", 1, 1, 0, 0, 0, 2),
        ("8.2.2.1", "Dział Zdrowia Publicznego", 0, 0, 0, 0, 6, 6),
        ("8.2.2.2", "Dział Organizacji i Nadzoru", 0, 0, 0, 0, 7, 7),
        ("8.2.3", "Wydział Inwestycji", 1, 0, 0, 1, 5, 7),
    ]),
    ("GW", [
        ("9", "Geodeta Województwa - Wydział Geodezji i Kartografii - Dyrekcja", 1, 1, 0, 1, 0, 3),
        ("9.1", "Wojewódzki Ośrodek Dokumentacji Geodezyjnej i Kartograficznej", 0, 0, 0, 0, 15, 15),
        ("9.1.1", "Dział ds. Dolnośląskiej Infrastruktury Informacji Przestrzennej", 0, 0, 0, 0, 7, 7),
        ("9.1.2", "Dział ds. Ochrony Gruntów Rolnych", 0, 0, 0, 0, 8, 8),
    ]),
    ("DK", [("10", "Dział Kancelaryjny II", 0, 0, 0, 0, 4, 4)]),
    ("DW", [("11", "Dział Wsparcia Informatycznego II", 0, 0, 0, 0, 4, 4)]),
]
Z1_SUMA_PU = dict(dyr=29, zast=16, samodz=6, sekr=12, prac=340, razem=403)  # PU s.19 wiersz "Suma"

BLOK_NAZWY = OrderedDict([
    ("SW", "Strefa wejściowa"),
    ("SK", "Strefa konferencyjna"),
    ("SWD", "Sejmik Województwa Dolnośląskiego"),
    ("KS", "Kancelaria Sejmiku"),
    ("DOS", "Departament Ochrony Środowiska"),
    ("DSS", "Departament Spraw Społecznych i Rynku Pracy"),
    ("DST", "Departament Sportu i Turystyki"),
    ("DRA", "Departament Rozwoju Aglomeracji"),
    ("DGP", "Departament Gospodarki i Promocji"),
    ("DI", "Departament Infrastruktury"),
    ("CZ", "Członek Zarządu"),
    ("DKD", "Departament Kultury i Dziedzictwa Kulturowego"),
    ("DZ", "Departament Zdrowia"),
    ("GW", "Geodeta Województwa - Wydział Geodezji i Kartografii"),
    ("DK", "Dział Kancelaryjny II"),
    ("DW", "Dział Wsparcia Informatycznego II"),
    ("SN", "Sale narad"),
    ("PS", "Pomieszczenia socjalne"),
    ("PP", "Pomieszczenia pomocnicze"),
    ("PHS", "Pomieszczenia higieniczno-sanitarne"),
    ("PPT", "Pomieszczenia pracowników technicznych"),
    ("IT", "Infrastruktura techniczna (w tym serwerownia)"),
    ("PR", "Parking dla rowerów"),
    ("PPM", "Parking podziemny pełniący funkcję MDS"),
    ("KW", "Komunikacja wewnętrzna"),
])

SRC_OFF = "PU s.4-5 (24 m2/3 st.; GW 32 m2/4 st.; pokoje 1-os.); Wyj.3 odp.16-17; Wyj.16 odp.69; Wyj.17 odp.70; Wyj.8 odp.48-50"

# ---------------------------------------------------------------------------
# 2. Reguly wyznaczania pokoi biurowych
# ---------------------------------------------------------------------------

def office_rooms(blok, row):
    nr, nazwa, dyr, zast, samodz, sekr, prac, razem = row
    gw = blok == "GW"
    rooms = []
    if dyr:
        if blok == "CZ":
            rooms.append(dict(typ="CZ", nazwa="Gabinet Członka Zarządu (pokój 1-os., możliwość pracy 3 os.)",
                              liczba=1, pow_jedn=24, osoby=1, stanowiska=3))
        else:
            rooms.append(dict(typ="DYR", nazwa="Gabinet dyrektora (pokój 1-os., możliwość pracy 3 os.)",
                              liczba=dyr, pow_jedn=24, osoby=dyr, stanowiska=3 * dyr))
    if zast:
        rooms.append(dict(typ="ZDYR", nazwa="Pokój zastępcy dyrektora (1-os., możliwość pracy 3 os.)",
                          liczba=zast, pow_jedn=24, osoby=zast, stanowiska=3 * zast))
    if samodz:
        rooms.append(dict(typ="SAM", nazwa="Pokój samodzielnego stanowiska (1-os., możliwość pracy 3 os.)",
                          liczba=samodz, pow_jedn=24, osoby=samodz, stanowiska=3 * samodz))
    if sekr:
        n = math.ceil(sekr / 3)
        rooms.append(dict(typ="SEK", nazwa="Sekretariat (pokój obok gabinetów dyrekcji, połączony drzwiami)",
                          liczba=n, pow_jedn=24, osoby=sekr, stanowiska=3 * n))
    if prac:
        if gw:
            n = math.ceil(prac / 4)
            rooms.append(dict(typ="PR32", nazwa="Pokój zespołu GW (4 stanowiska, 32 m2)",
                              liczba=n, pow_jedn=32, osoby=prac, stanowiska=4 * n))
        else:
            n = math.ceil(prac / 3)
            rooms.append(dict(typ="PR", nazwa="Pokój pracowników (do 3 stanowisk)",
                              liczba=n, pow_jedn=24, osoby=prac, stanowiska=3 * n))
    for r in rooms:
        r["id"] = f"{blok}.{nr}.{r['typ']}"
        r["pow_laczna"] = r["liczba"] * r["pow_jedn"]
        r["szacunek"] = False
        r["kategoria_pn_iso"] = "PU"
        r["zrodlo"] = "PU s.19 (zał.1, wiersz %s); %s" % (nr, SRC_OFF)
    return rooms


# ---------------------------------------------------------------------------
# 3. Pozostale pomieszczenia: (id, nazwa, liczba, pow_jedn, zakres, osoby, szac, kat, wymagania, zrodlo)
#    kat: PU = powierzchnia uzytkowa; US = uslugowa (techniczna); RU = ruchu (KW)
# ---------------------------------------------------------------------------
N_KOND = 12  # scenariusz: 2 kond. podziemne + parter + 9 pieter (dominanta) - parametr do korekty
N_OCZEK = 9  # miejsca oczekiwania przy CZ i dyrektorach departamentow (Wyj.4 odp.19)

R = OrderedDict()
R["SW"] = [
    ("SW.01", "Hol główny (reprezentacyjny węzeł komunikacyjny; wiz. nr 6)", 1, 300, [220, 450], None, True, "RU",
     ["wejście główne widoczne w bryle, z poziomu terenu, bez barier", "połączenie z parkingiem podziemnym",
      "łatwa orientacja; ścieżki naprowadzające i tyflomapa", "wydzielone strefy funkcji"],
     "PU s.8-9; Reg. III.1.8 s.20; Reg. VII.2.2.g s.44; Wyj.20 odp.73 (ruch w SW dopuszczalny w SW)"),
    ("SW.02", "Kancelaria ogólna (3 stanowiska)", 1, 36, [30, 45], 3, True, "PU",
     ["w holu głównym", "pętla indukcyjna", "min. 1 stanowisko obsługi dostosowane (M.13)"],
     "PU s.8, s.12; Reg. III.1.8 s.20"),
    ("SW.03", "Punkt informacyjny (1 stanowisko)", 1, 8, [6, 12], 1, True, "PU",
     ["w holu, widoczny od wejścia", "lada dostępna"], "PU s.8"),
    ("SW.04", "Pomieszczenie ochrony budynku / centrum monitoringu", 1, 24, [18, 30], 2, True, "PU",
     ["CCTV, kontrola dostępu; interkom z miejsc oczekiwania na ewakuację", "przy holu"],
     "PU s.8, s.11, s.14; Reg. III.1.8 s.20"),
    ("SW.05", "Miejsce socjalne ochrony", 1, 10, [8, 14], None, True, "PU",
     ["powiązane z SW.04"], "PU s.8"),
    ("SW.06", "Strefa recepcyjna / poczekalnia", 1, 40, [30, 60], 15, True, "PU",
     ["w holu"], "PU s.8"),
    ("SW.07", "Bistro - sala konsumpcyjna (kilkanaście stolików)", 1, 90, [70, 120], 60, True, "PU",
     ["bezpośrednie sąsiedztwo holu", "obsługa centrum konferencyjnego, pracowników i gości"],
     "PU s.9"),
    ("SW.08", "Bistro - zaplecze (tylko podgrzewanie, zmywanie, magazyn podręczny)", 1, 25, [15, 35], None, True, "PU",
     ["bez przygotowywania posiłków", "dostęp od strefy dostaw (wniosek)"], "PU s.9"),
]
R["SK"] = [
    ("SK.01", "Sala konferencyjna 200 os. (podział na 2 mniejsze)", 1, 240, [220, 280], 200, True, "PU",
     ["parter, bezpośrednio przy holu", "ściana mobilna - podział na 2 przestrzenie",
      "zaplecze techniczne: prezentacje i transmisja", "pętla indukcyjna", "ZL I (>50 os.) - wniosek"],
     "PU s.8, s.12; Wyj.8 odp.35"),
    ("SK.02", "Sala konferencyjna mniejsza 80 os.", 1, 100, [90, 120], 80, True, "PU",
     ["parter, przy holu", "zaplecze techniczne", "pętla indukcyjna"], "PU s.8, s.12"),
    ("SK.03", "Zaplecze techniczne / reżyserka AV sali 200 os.", 1, 12, [10, 16], 1, True, "PU",
     ["wgląd na salę"], "PU s.8"),
    ("SK.04", "Zaplecze techniczne / reżyserka AV sali 80 os.", 1, 10, [8, 12], 1, True, "PU", [], "PU s.8"),
    ("SK.05", "Magazyn mebli i ścianek mobilnych", 1, 30, [20, 40], None, True, "PU",
     ["przy sali dzielonej (wniosek)"], "wniosek (PU s.8 - elastyczny podział sali)"),
    ("SK.06", "Foyer / kuluary centrum konferencyjnego", 1, 100, [60, 150], None, True, "RU",
     ["może stanowić część holu głównego"], "PU s.8 ('niewielkie centrum konferencyjne'); wniosek"),
    ("SK.07", "Szatnia centrum konferencyjnego", 1, 25, [20, 35], None, True, "PU", [], "wniosek (pojemność 280 os.)"),
]
R["SWD"] = [
    ("SWD.01", "Sala obrad Sejmiku (sala sesyjna) - max 100 os., układ amfiteatralny", 1, 320, [280, 380], 100, True, "PU",
     ["najwyższe piętro dominanty", "charakter reprezentacyjny", "podwyższane rzędy",
      "strefy: radni, prezydium, zarząd, goście, media, obsługa techniczna i kancelaryjna, tłumacze PJM",
      "stałe stanowiska z systemem głosowania, tabletami i mikrofonami",
      "publiczność: oddzielne wejście, może być wizualnie odseparowana / galeria-antresola dopuszczalna",
      "poufność głosowania", "dostęp bez barier do stanowisk, prezydium i mównicy",
      "min. 3 miejsca dla wózków na 100 miejsc widowni (M.13 s.218)", "pętla indukcyjna",
      "kamery, mikrofony, głośniki - nagrywanie i transmisja", "wysokość dowolna (Wyj.8 odp.36)"],
     "PU s.5-7, s.12; Wyj.4 odp.18; Wyj.8 odp.36, 52; Reg. III.1.5 s.19; M.13 s.218-219"),
    ("SWD.02", "Hol reprezentacyjny sali obrad (wiz. nr 7)", 1, 150, [120, 220], None, True, "RU",
     ["ta sama kondygnacja co sala obrad", "szybki dostęp większej liczby osób z parkingu i strefy wejściowej"],
     "PU s.6; Reg. VII.2.2.g s.44; Wyj.21 odp.82, 85"),
    ("SWD.03", "Sala multimedialna / poczekalnia gości (ekran, głośniki)", 1, 40, [30, 60], 20, True, "PU",
     ["śledzenie obrad", "ta sama kondygnacja"], "PU s.6; Wyj.21 odp.85"),
    ("SWD.04", "Pomieszczenie obsługi technicznej obrad (nagrywanie, transmisja)", 1, 20, [15, 30], 3, True, "PU",
     ["wgląd na salę (wniosek)", "ta sama kondygnacja"], "PU s.6-7; Wyj.21 odp.85"),
    ("SWD.05", "Przestrzeń socjalno-gastronomiczna (z przyłączami)", 1, 40, [30, 60], None, True, "PU",
     ["ta sama kondygnacja"], "PU s.6; Wyj.21 odp.85"),
    ("SWD.06", "Szatnia strefy Sejmiku", 1, 15, [12, 20], None, True, "PU", ["ta sama kondygnacja"], "PU s.6"),
    ("SWD.07", "Pokój dla matki z dzieckiem (pokój rodzinny)", 1, 10, [8, 12], None, True, "PU",
     ["nie w toalecie; fotel, przewijak, umywalka, podgrzewacz (M.13 s.203)"], "PU s.6; M.13 s.203"),
    ("SWD.08", "Sala komisji 50 os. (zaplecze do nagrywania)", 1, 100, [90, 120], 50, True, "PU",
     ["AV: kamery, mikrofony, głośniki, nagrywanie, transmisja", "ekran + punkty dostępowe", "ta sama kondygnacja"],
     "PU s.7; Wyj.8 odp.53; Wyj.21 odp.85"),
    ("SWD.09", "Sala komisji 30 os. (zaplecze do nagrywania)", 1, 60, [54, 72], 30, True, "PU",
     ["jw."], "PU s.7; Wyj.8 odp.53; Wyj.21 odp.85"),
    ("SWD.10", "Zaplecze techniczne nagrywania posiedzeń komisji", 2, 10, [8, 12], 1, True, "PU",
     ["po jednym przy każdej sali komisji"], "PU s.7; Wyj.8 odp.53"),
    ("SWD.11", "Sala klubu radnych 30 os.", 2, 60, [54, 72], 30, True, "PU",
     ["ekran + punkty dostępowe"], "PU s.7; Wyj.21 odp.85"),
    ("SWD.12", "Sala klubu radnych 15 os.", 2, 36, [30, 40], 15, True, "PU",
     ["ekran + punkty dostępowe"], "PU s.7; Wyj.21 odp.85"),
    ("SWD.13", "Wspólna sala radnych (doraźna praca indywidualna)", 1, 48, [36, 60], 12, True, "PU",
     ["ekran + punkty dostępowe"], "PU s.7"),
    ("SWD.14", "Pokój socjalny radnych (podgrzanie i spożycie posiłku)", 1, 24, [20, 30], 8, True, "PU", [], "PU s.7"),
    ("SWD.15", "Magazyn podręczny strefy Sejmiku (zalecenie własne)", 1, 10, [6, 15], None, True, "PU",
     ["nie wymagany przez M.01"], "wniosek"),
]
R["KS"] = [  # pomieszczenia KS poza pokojami biurowymi z zal.1
    ("KS.01", "Gabinet Przewodniczącego Sejmiku (reprezentacyjny; 1 stanowisko + spotkania 5 os.)", 1, 48, [36, 60], 1, True, "PU",
     ["w pobliżu KS", "miejsce oczekiwania gości (Wyj.4 odp.19)"], "PU s.7; Wyj.4 odp.19"),
    ("KS.02", "Zaplecze sanitarno-socjalne gabinetu Przewodniczącego", 1, 8, [6, 10], None, True, "PU", [], "PU s.7"),
    ("KS.03", "Pokój asystenta Przewodniczącego (1 stanowisko)", 1, 24, [12, 24], 1, True, "PU",
     ["przy gabinecie Przewodniczącego; moduł 24 m2 (wniosek)"], "PU s.7"),
    ("KS.04", "Gabinet Wiceprzewodniczącego Sejmiku (1 stanowisko + spotkania 5 os.)", 3, 36, [24, 40], 1, True, "PU",
     [], "PU s.7"),
    ("KS.05", "Sala spotkań 20 os. (Przewodniczący, Wiceprzewodniczący, KS)", 2, 48, [40, 50], 20, True, "PU",
     ["ekran + punkty dostępowe"], "PU s.7; Wyj.6 odp.23; Wyj.7 odp.31"),
    ("KS.06", "Miejsce oczekiwania gości (Przewodniczący, KS)", 1, 12, [8, 15], 5, True, "PU", [], "Wyj.4 odp.19"),
]
R["SN"] = [
    ("SN.01", "Sala narad 30 os.", 6, 60, [54, 72], 30, True, "PU",
     ["rozmieszczone równomiernie w budynku", "ekran + punkty dostępowe do komputerów"],
     "PU s.8; Wyj.8 odp.54"),
]
R["PS"] = [
    ("PS.01", "Pokój socjalny pracowników (do 30 os.)", 15, 24, [24, 24], None, False, "PU",
     ["równomiernie w strefie biurowej", "napoje, podgrzewanie, spożycie posiłków"], "PU s.9"),
]
R["PP"] = [
    ("PP.01", "Podręczny magazyn dokumentacji (konwertowalny na biuro)", 20, 24, [24, 24], None, False, "PU",
     ["3 punkty dostępowe el. i teletech. (zmiana na biuro)"], "PU s.9"),
    ("PP.02", "Archiwum Państwowego Zasobu Geodezyjnego i Kartograficznego (GW)", 1, 48, [48, 48], None, False, "PU",
     ["szafy jezdne (obciążenie stropu - wniosek)", "kontrola temperatury i wilgotności", "ta sama kondygnacja co GW"],
     "PU s.9-10; Wyj.6 odp.26"),
    ("PP.03", "Archiwum operatów kartograficznych i dokumentacji technicznej (GW)", 1, 24, [24, 24], None, False, "PU",
     ["jw."], "PU s.9-10; Wyj.6 odp.26"),
    ("PP.04", "Pomieszczenie urządzeń specjalistycznych GW (ploter, skaner wielkoformatowy, MFP, skanowanie)", 1, 24, [24, 24], 1, False, "PU",
     ["przy GW (wniosek)"], "PU s.10"),
    ("PP.05", "Pomieszczenie / wnęka sieciowego urządzenia wielofunkcyjnego", 10, 5, [3, 8], None, True, "PU",
     ["wzdłuż ciągów komunikacyjnych, równomiernie", "wentylacja"], "PU s.10"),
    ("PP.06", "Pomieszczenie porządkowe (magazyn sprzętu i środków czystości, dostęp do wody)", N_KOND - 1, 6, [4, 8], None, True, "PU",
     ["na każdym piętrze (liczba = scenariusz %d kondygnacji, w tym PP.07)" % N_KOND], "PU s.10"),
    ("PP.07", "Pomieszczenie porządkowe z pralnią i suszarnią", 1, 15, [10, 20], None, True, "PU", [], "PU s.10"),
]
R["PHS"] = [
    ("PHS.01", "Zespół sanitarny kondygnacji biurowej (K, M, toaleta dostępna)", N_KOND - 2, 28, [22, 40], None, True, "PU",
     ["równomiernie; min. 1 toaleta dostępna na każdej kondygnacji",
      "w toaletach pochwyt poziomy na skrzydle drzwi, kontrast ścian/posadzki"],
     "PU s.10; Reg. III.1.8 s.20"),
    ("PHS.02", "Toalety ogólnodostępne przy holu głównym (K, M, dostępna, przewijak)", 1, 30, [24, 40], None, True, "PU",
     [], "PU s.9; M.13 (przewijaki)"),
    ("PHS.03", "Komfortka - toaleta z możliwością przebierania dorosłych (przy wejściu głównym)", 1, 12, [12, 15], None, False, "PU",
     ["parter, max 20 m od wejścia, szer. min 3 m, pow. min 12 m2, leżanka, prysznic"],
     "PU s.10; Reg. III.1.8 s.20; M.13 s.202 (min 12 m2)"),
    ("PHS.04", "Toalety strefy konferencyjnej (wg pojemności 280 os.)", 1, 50, [40, 70], None, True, "PU",
     ["liczba przyborów dostosowana do maks. liczby użytkowników"], "PU s.10"),
    ("PHS.05", "Toalety strefy Sejmiku (w tym dla OzN)", 1, 45, [35, 60], None, True, "PU",
     ["ta sama kondygnacja co sala obrad"], "PU s.6, s.10; Wyj.21 odp.85"),
]
R["PPT"] = [
    ("PPT.01", "Pomieszczenie techników (3 stanowiska)", 1, 24, [20, 30], 3, True, "PU", [], "PU s.15; Wyj.6 odp.24"),
    ("PPT.02", "Magazyn narzędzi i materiałów eksploatacyjnych", 1, 24, [15, 30], None, True, "PU", [], "PU s.15"),
    ("PPT.03", "Strefa serwisowo-konserwacyjna (warsztat)", 1, 24, [15, 30], None, True, "PU", [], "PU s.15"),
    ("PPT.04", "Pomieszczenie socjalne z szatnią - personel techniczny", 1, 20, [15, 25], None, True, "PU", [], "PU s.15"),
    ("PPT.05", "Pomieszczenie socjalne z szatnią - personel sprzątający", 1, 20, [15, 25], None, True, "PU", [], "PU s.15"),
    ("PPT.06", "Pomieszczenie sanitarne z prysznicami (personel tech. i sprzątający)", 1, 15, [12, 20], None, True, "PU", [], "PU s.15"),
]
R["IT"] = [
    ("IT.01", "Serwerownia (TIER II)", 1, 50, [40, 50], None, False, "US",
     ["pow. do 50 m2", "światłowód jednomodowy do serwerowni głównej (Wybrzeże Słowackiego 12-14)",
      "klimatyzacja precyzyjna; dwutorowe zasilanie; SZR; UPS do startu agregatu; redundancja UPS/chłodzenia"],
     "PU s.15-16"),
    ("IT.02", "Punkt dystrybucyjny IT (PD) na każdej kondygnacji", N_KOND, 6, [4, 10], None, True, "US",
     ["telefonia IP / transmisja danych"], "PU s.14"),
    ("IT.03", "Pomieszczenie UPS", 1, 15, [10, 20], None, True, "US", ["IT i systemy bezpieczeństwa"], "PU s.13, s.16"),
    ("IT.04", "Stacja transformatorowa SN/nn", 1, 50, [35, 70], None, True, "US",
     ["w wydzielonych pomieszczeniach budynku lub na terenie"], "PU s.13"),
    ("IT.05", "Rozdzielnia główna nn z SZR", 1, 30, [20, 40], None, True, "US", [], "PU s.13, s.16"),
    ("IT.06", "Agregat prądotwórczy", 1, 35, [25, 50], None, True, "US",
     ["wentylacja, dostęp serwisowy"], "PU s.13, s.16"),
    ("IT.07", "Magazyn energii elektrycznej (PV)", 1, 30, [20, 50], None, True, "US", [], "PU s.13; M.12 pkt 1.D"),
    ("IT.08", "Maszynownia gruntowych pomp ciepła (rozdzielacze)", 1, 150, [100, 200], None, True, "US",
     ["odwierty możliwe pod budynkiem (M.12)"], "PU s.14; M.12 pkt 1.A"),
    ("IT.09", "Magazyn ciepła/chłodu krótkoterminowy (zbiorniki buforowe)", 1, 50, [30, 80], None, True, "US",
     ["w wydzielonych pomieszczeniach technicznych"], "M.12 pkt 1.C"),
    ("IT.10", "Węzeł cieplny (sieć ciepłownicza - funkcja rezerwowa/szczytowa)", 1, 20, [15, 30], None, True, "US",
     [], "M.12 pkt 1.E; F.14.B poz. 2.1, 7.5"),
    ("IT.11", "Pomieszczenie przyłącza wody / pompownia (wniosek)", 1, 25, [15, 40], None, True, "US", [], "PU s.14"),
    ("IT.12", "Instalacja wody szarej (podczyszczanie, zbiorniki) + odzysk ciepła", 1, 40, [25, 60], None, True, "US",
     ["rozdział ścieków czarnych/szarych; zakaz łączenia z wodą pitną"], "PU s.3, s.14; M.12 pkt 2.C-D"),
    ("IT.13", "Piętro techniczne - centrale wentylacyjne z rekuperacją, agregaty chłodnicze", 1, 650, [500, 900], None, True, "US",
     ["urządzenia centralne na piętrze technicznym", "na dachu tylko urządzenia niemożliwe do umieszczenia na piętrze technicznym"],
     "PU s.13-14"),
    ("IT.14", "Pomieszczenie odpadów komunalnych", 1, 25, [15, 35], None, True, "PU",
     ["łatwy dostęp dla firm odbierających", "warunki sanitarne, wentylacja"], "PU s.15"),
    ("IT.15", "Strefa dostaw - przyjęcie towaru (od Wybrzeża Słowackiego, z poziomu terenu)", 1, 20, [15, 30], None, True, "PU",
     ["winda osobowo-towarowa", "bez miejsca postojowego na działce drogowej (Wyj.6 odp.25)"],
     "PU s.15, s.17; Wyj.4 odp.20; Wyj.6 odp.25"),
]
R["PR"] = [
    ("PR.01", "Parking rowerowy - 50 stanowisk (stojaki typu U)", 1, 90, [75, 110], None, True, "PU",
     ["parter, wjazd od strony podwórza", "dobrze oświetlony", "nie na poz. -1 (Wyj.7 odp.32)",
      "zalecenie własne: 10 miejsc dla hulajnóg/UTO z ładowaniem w ramach PR.01 (M.01 nie wymaga)"],
     "PU s.12; Wyj.7 odp.32"),
    ("PR.02", "Zaplecze sanitarne parkingu rowerowego", 1, 25, [15, 35], None, True, "PU",
     ["bezpośrednie sąsiedztwo; dostępne dla wszystkich użytkowników parkingu rowerowego"], "PU s.12"),
]

# ---------------------------------------------------------------------------
# 4. Obliczenia
# ---------------------------------------------------------------------------

def mk(t, blok):
    rid, nazwa, liczba, pj, zakres, osoby, szac, kat, wym, src = t
    return OrderedDict([
        ("id", rid), ("nazwa", nazwa), ("liczba", liczba), ("pow_jedn", pj),
        ("pow_laczna", liczba * pj), ("zakres_pow_jedn", zakres), ("osoby", osoby),
        ("szacunek", szac), ("kategoria_pn_iso", kat), ("wymagania", wym), ("zrodlo", src),
    ])

bloki = OrderedDict((k, []) for k in BLOK_NAZWY)
komorki = OrderedDict()
tot = dict(dyr=0, zast=0, samodz=0, sekr=0, prac=0, razem=0)
for blok, rows in Z1:
    komorki[blok] = []
    for row in rows:
        nr, nazwa, dyr, zast, samodz, sekr, prac, razem = row
        assert dyr + zast + samodz + sekr + prac == razem, row
        for k, v in zip(["dyr", "zast", "samodz", "sekr", "prac", "razem"], row[2:]):
            tot[k] += v
        rooms = office_rooms(blok, row)
        komorki[blok].append(OrderedDict([
            ("nr", nr), ("nazwa", nazwa), ("dyr", dyr), ("zast", zast), ("samodz", samodz),
            ("sekr", sekr), ("prac", prac), ("razem", razem),
            ("pokoje", sum(r["liczba"] for r in rooms)),
            ("pow_biurowa", sum(r["pow_laczna"] for r in rooms)),
            ("stanowiska_max", sum(r["stanowiska"] for r in rooms)),
        ]))
        for r in rooms:
            bloki[blok].append(OrderedDict([
                ("id", r["id"]), ("nazwa", r["nazwa"]), ("liczba", r["liczba"]), ("pow_jedn", r["pow_jedn"]),
                ("pow_laczna", r["pow_laczna"]), ("zakres_pow_jedn", [r["pow_jedn"], r["pow_jedn"]]),
                ("osoby", r["osoby"]), ("stanowiska_max", r["stanowiska"]), ("komorka", nr),
                ("szacunek", False), ("kategoria_pn_iso", "PU"), ("wymagania", []), ("zrodlo", r["zrodlo"]),
            ]))
assert tot == Z1_SUMA_PU, (tot, Z1_SUMA_PU)

# miejsca oczekiwania przy CZ i dyrektorach departamentow (Wyj.4 odp.19)
for blok in ["DOS", "DSS", "DST", "DRA", "DGP", "DI", "CZ", "DKD", "DZ"]:
    bloki[blok].append(mk((f"{blok}.OCZ", "Miejsce oczekiwania gości (kilka osób) przy gabinecie dyrektora departamentu / CZ",
                           1, 6, [4, 10], 4, True, "PU", ["wnęka przy korytarzu dopuszczalna (wniosek)"],
                           "Wyj.4 odp.19"), blok))

for blok, items in R.items():
    for t in items:
        bloki[blok].append(mk(t, blok))

# sumy
def s_kat(kat, bl=None):
    return sum(p["pow_laczna"] for b, ps in bloki.items() if (bl is None or b in bl) for p in ps
               if p["kategoria_pn_iso"] == kat)

biur_bloki = ["KS", "DOS", "DSS", "DST", "DRA", "DGP", "DI", "CZ", "DKD", "DZ", "GW", "DK", "DW"]
pow_biur = sum(p["pow_laczna"] for b in biur_bloki for p in bloki[b] if p["id"].split(".")[-1] in
               ("DYR", "ZDYR", "SAM", "SEK", "PR", "PR32", "CZ"))
pokoje_24 = sum(p["liczba"] for b in biur_bloki for p in bloki[b] if p["id"].split(".")[-1] in
                ("DYR", "ZDYR", "SAM", "SEK", "PR", "CZ"))
pokoje_32 = sum(p["liczba"] for b in biur_bloki for p in bloki[b] if p["id"].endswith(".PR32"))
stan_max = sum(p.get("stanowiska_max", 0) for b in biur_bloki for p in bloki[b])

PU = s_kat("PU")
US = s_kat("US")
RU_SW = s_kat("RU")  # hol/foyer/hol Sejmiku przypisane do blokow (dopuszczenie Wyj.20)
KW_UDZIAL = 0.30      # wniosek: komunikacja (korytarze, klatki, przedsionki, windy) / PU
KW = int(round(KW_UDZIAL * PU, -1))
NETTO = PU + US + RU_SW + KW
KONSTR = 0.12          # wniosek: udzial scian i konstrukcji w pow. calkowitej
PC_NADZ = int(round(NETTO / (1 - KONSTR), -1))

# parking wg MPZP par.13 pkt 1 lit. e: 12 msc / 1000 m2 PU biur i obiektow konferencyjnych
msc_min = math.ceil(12 * PU / 1000.0)
ozn_min = max(math.ceil(0.04 * msc_min), 4) if msc_min > 100 else (3 if msc_min > 40 else 2)

bloki["KW"].append(mk(("KW.01", "Komunikacja wewnętrzna nadziemna (korytarze, klatki ewakuacyjne z przedsionkami p.poż., szyby dźwigowe, pochylnie)",
                       1, KW, [int(round(0.25 * PU, -1)), int(round(0.35 * PU, -1))], None, True, "RU",
                       ["klatki poprzedzone przedsionkami p.poż. (budynek wysoki - wniosek)",
                        "miejsca oczekiwania na ewakuację dla wózka na podestach + interkom + miejsce na krzesło ewakuacyjne",
                        "ścieżki naprowadzające z holu i parkingu; kontrast ścian i posadzek",
                        "windy dostępne dla OzN; min. 1 osobowo-towarowa w strefie dostaw",
                        "wszystkie powierzchnie ruchu wg PN-ISO 9836:2022-07 (Wyj.20 odp.73)"],
                       "PU s.10-11, s.15; Reg. III.1.8 s.20; Wyj.20 odp.73; wniosek (udział 30% PU)"), "KW"))

GAR_M2_NA_MSC = 27.0  # wniosek: pow. brutto garazu na 1 stanowisko (z drogami, rampa)
bloki["PPM"] = [
    mk(("PPM.01", "Garaż podziemny - stanowiska postojowe ogólne (2 kondygnacje: -1, -2)", msc_min - ozn_min, 12.5, [12.5, 12.5], None, True, "PG",
        ["lokalizacja bezpośrednio pod budynkiem (MPZP)", "dla pracowników; w dni sesji/wydarzeń - radni i goście",
         "infrastruktura ładowania EV", "liczba = minimum MPZP przy PU z niniejszej ekstrakcji (parametr)",
         "stanowisko 2,5 x 5,0 m (wniosek)"],
        "PU s.3, s.12-13; MPZP par.13 pkt 1 lit. e i pkt 2-3 (M.03 s.15-16); Wyj.21 odp.83"), "PPM"),
    mk(("PPM.02", "Stanowiska dla osób z niepełnosprawnościami (łącznie z PPM.01 = minimum MPZP)", ozn_min, 18.0, [18.0, 18.0], None, False, "PG",
        ["min. 4% przy >100 stanowisk; 3,6 x 5,0 m; najbliżej dostępnego wejścia/dźwigu"],
        "PU s.13; M.13 s.80-81"), "PPM"),
    mk(("PPM.03", "Drogi manewrowe, rampa/zjazd, klatki garażowe (szac. brutto - netto stanowisk)", 1,
        int(round(msc_min * GAR_M2_NA_MSC - (msc_min - ozn_min) * 12.5 - ozn_min * 18.0, -1)), None, None, True, "RU",
        ["zjazd z drogi publicznej w obrębie inwestycji (Reg. III.1.2)", "dojazd do terenu wg MPZP par.26 ust.3"],
        "Reg. III.1.2 s.18; MPZP par.26 ust.3 (M.03 s.25); wniosek"), "PPM"),
    mk(("PPM.04", "Funkcja MDS - zaplecze (magazyn wyposażenia, sanitariaty) - parametry wg rozp. MSWiA z 9.07.2025", 1, 30, [20, 60], None, True, "PU",
        ["pojemność MDS nie podana w M.01 (luka)", "dla okolicznej ludności i pracowników"],
        "PU s.3, s.13, s.18"), "PPM"),
]

# ---------------------------------------------------------------------------
# 5. Zapis YAML
# ---------------------------------------------------------------------------
def blok_suma(b):
    return sum(p["pow_laczna"] for p in bloki[b])

wyj = OrderedDict()
wyj["meta"] = OrderedDict([
    ("tytul", "Program użytkowy budynku administracyjnego UMWD - ekstrakcja maszynowa (Załącznik M.01)"),
    ("data_ekstrakcji", "2026-11-16"),
    ("wersja_obowiazujaca", "Program użytkowy budynku administracyjnego UWMD zatwierdzony 11_2025.pdf (listopad 2025; md5 dad3bae4...); "
                            "okładka M.01 z dat 2025.11.04 / 2025.10.29 (katalog 5_..._pop.13.02.2026)"),
    ("wersja_nieaktualna", "katalog 'M.01. PROGRAM UŻYTKOWY STARTY' (29.10.2025) - wycofany: Wyj.3 odp.11, Sprostowanie nr 1 pkt 2"),
    ("skroty_zrodel", OrderedDict([
        ("PU", "Program użytkowy ... zatwierdzony 11_2025 (M.01); s. = numer drukowany w stopce (PDF = s.+1)"),
        ("Reg", "Regulamin Konkursu - tekst jednolity 13.02.2026; Rozdział.ust.pkt, s. = strona drukowana"),
        ("WyjN odp.M", "Wyjaśnienia treści Regulaminu nr N, odpowiedź na pytanie nr M"),
        ("MPZP", "M.03 - uchwała XLV/1366/10 RMW z 21.01.2010 (teren 2MW-U/5, par.26)"),
        ("M.12", "Wytyczne zero-emisyjności"), ("M.13", "Standardy dostępności MSWiA (s. = strona drukowana)"),
        ("F.15.A/B/C", "Tabele programowa / zestawienie pomieszczeń / dane bilansowe (xlsx)"),
        ("wniosek", "ustalenie własne - nie pochodzi z dokumentów Organizatora"),
    ])),
    ("konwencje", OrderedDict([
        ("pow", "m2 netto pomieszczenia wg PN-ISO 9836:2022-07 (Wyj.20 odp.73)"),
        ("szacunek", "true = powierzchnia nie podana w M.01 - wartość docelowa z zakresem (wniosek; Wyj.8 odp.33,45: brak zestawienia Organizatora)"),
        ("kategoria_pn_iso", "PU = użytkowa; US = usługowa (techniczna); RU = ruchu; PG = stanowiska garażowe (liczone osobno - nie wchodzą do PU dla wskaźnika MPZP; sposób ujęcia w F.15.C do rozstrzygnięcia)"),
        ("id", "skróty bloków wg Wyj.20 odp.73; pokoje biurowe: <BLOK>.<nr komórki z zał.1>.<typ> (Wyj.8 odp.46)"),
        ("typy_pokoi", "CZ, DYR, ZDYR, SAM, SEK, PR (24 m2/3 st.), PR32 (GW 32 m2/4 st.), OCZ (miejsce oczekiwania)"),
        ("scenariusz_kondygnacji", "N_KOND=%d (2 podziemne + parter + 9 pięter) - wpływa na liczbę PP.06, PHS.01, IT.02" % N_KOND),
    ])),
])
wyj["zalozenia_ogolne"] = OrderedDict([
    ("teren", "dz. 10/3, 11/6, 19/11, 9/1, obr. 022 Południe; 3 729 m2 (PU s.2); do obliczeń - Obszar inwestycji z M.04 (Wyj.8 odp.59)"),
    ("forma", "trzy części: 2 skrzydła (Mazowiecka, Wybrzeże Słowackiego) + dominanta w narożniku; skrzydło przy Mazowieckiej przylega do kamienicy nr 19 (zwarta pierzeja); brak połączenia z Wybrzeże Słowackiego 5 (PU s.2-3)"),
    ("wysokosc_skrzydel", "PU s.2: 5 kondygnacji, do 22 m; MPZP par.6 pkt 3: 18-25 m; Wyj.3 odp.10: obowiązuje MPZP, 22 m to sygnał dla styku z zabudową sąsiednią"),
    ("wysokosc_dominanty", "PU s.2: do 45 m; MPZP par.26 ust.2 pkt 3 (obszar A): najwyższy punkt dachu <=45 m, najniższy >=35 m"),
    ("podziemie", "2 kondygnacje podziemne: parking + infrastruktura techniczna; parking = MDS (PU s.3, s.13)"),
    ("standard", "zeroemisyjny, OZE, woda szara i opadowa (PU s.3; M.12); projektowanie uniwersalne, ustawa o dostępności, standardy MSWiA (PU s.3-4; Reg. III.1.8)"),
    ("elastycznosc", "jednolite pokoje 24 m2 dla 1-3 os.; trwałe technologie; rezerwy instalacyjne (PU s.3-4; Reg. III.1.9)"),
    ("budzet", "maks. 150 mln zł netto realizacji z zagospodarowaniem - nieprzekraczalny (Reg. III.3 s.21; Wyj.20 odp.74)"),
    ("kryterium_pierwszorzedne", "jakość rozwiązań funkcjonalnych i przestrzennych (Reg. III.1.11 s.21)"),
])
wyj["reguly_pokoi_biurowych"] = [
    "Każdy pokój biurowy 24 m2 z 3 stanowiskami i punktami el./teletech. dla 3 os., niezależnie od obsady (PU s.4); wartość obligatoryjna (Wyj.3 odp.17).",
    "GW (Wydział Geodezji i Kartografii): pokoje pracowników 32 m2 dla zespołów 4-os. (PU s.5).",
    "Pokoje 1-os.: Członek Zarządu, dyrektorzy, zastępcy, samodzielne stanowiska - z możliwością pracy 3 os. (PU s.5).",
    "Pokoje obok dyrekcji łatwo zamienialne i łączone drzwiami w sekretariaty (PU s.5).",
    "Nie łączyć w jednym pokoju pracowników różnych wydziałów ani różnych działów (Wyj.3 odp.16; Wyj.16 odp.69; Wyj.17 odp.70).",
    "Wiersz 'X - Dyrekcja' z pracownikami (np. 3.4, 3.5): 1 gabinet dyrektora + pokoje dla pracowników (Wyj.8 odp.48-49).",
    "Gabinety: pion 8 - CZ + dyrektorzy departamentów 8.1, 8.2 + dyrektorzy wydziałów obok siebie; piony 2-7, 9 - dyrektor departamentu + dyrektorzy wydziałów obok siebie i w pobliżu swoich komórek (PU s.5; Wyj.10 odp.62).",
    "Wydziały jednego departamentu mogą zajmować 2 sąsiednie kondygnacje przy komunikacji pionowej (Wyj.17 odp.70).",
    "Sekretariat: 1 pokój 24 m2 na komórkę (do 3 os.) - wniosek (zgodny z przykładem w pyt. 69, Wyj.16).",
    "Liczba pokoi pracowników = ceil(n/3), GW ceil(n/4) dla każdej komórki z zał.1 osobno - wniosek wynikający z Wyj.16-17.",
]
wyj["kadra"] = OrderedDict([
    ("suma_zal1", Z1_SUMA_PU), ("suma_kontrolna_obliczona", tot),
    ("zgodnosc", tot == Z1_SUMA_PU),
    ("osoby_spoza_403", "Przewodniczący + 3 Wiceprzewodniczących (radni), asystent Przewodniczącego (niejasne, czy w 16 os. KS), 36 radnych, 5 członków Zarządu (poza CZ), Skarbnik, Sekretarz, przedstawiciel Wojewody, ochrona, sprzątanie, 3 techników (Wyj.6 odp.24) - PU s.6-7, s.15"),
    ("czas_pracy", "średnio 8-godzinny dzień pracy (PU s.9); brak godzin otwarcia i częstotliwości sesji w M.01 (luka)"),
    ("komorki", komorki),
])
wyj["bloki"] = []
for b, nazwa in BLOK_NAZWY.items():
    wyj["bloki"].append(OrderedDict([
        ("kod", b), ("nazwa", nazwa), ("pow_suma", blok_suma(b)),
        ("pomieszczenia", bloki[b]),
    ]))

LOK = OrderedDict([
    ("SW", "parter; wejście główne widoczne, od ulicy i przystanków, z poziomu terenu, połączone z parkingiem (PU s.8)"),
    ("SK", "parter, bezpośrednio przy holu, dostęp od wnętrza i od wejścia głównego (PU s.8)"),
    ("SWD", "najwyższe kondygnacje dominanty (obszar A MPZP); sala obrad na najwyższym piętrze; wszystkie pomieszczenia Sejmiku z PU s.5-7 na tej samej kondygnacji co sala obrad (PU s.5; Reg. III.1.5; Wyj.21 odp.84-85)"),
    ("KS", "przy gabinetach Przewodniczącego i Wiceprzewodniczących; dopuszczalnie kondygnacja sąsiednia do sali obrad (PU s.7; Wyj.21 odp.84-85)"),
    ("departamenty", "strefa biurowa; zwarte strefy pionów; wydziały na max 2 sąsiednich kondygnacjach (Wyj.17 odp.70)"),
    ("GW", "archiwa PZGiK i operatów na tej samej kondygnacji co GW (Wyj.6 odp.26)"),
    ("SN", "rozmieszczone równomiernie (PU s.8)"),
    ("PS", "równomiernie w strefie biurowej (PU s.9)"),
    ("PR", "parter, wjazd od podwórza (PU s.12; Wyj.7 odp.32)"),
    ("PPM", "2 kondygnacje podziemne bezpośrednio pod budynkiem (PU s.3, s.12)"),
    ("IT", "piętro techniczne dla central i agregatów; dach tylko dla urządzeń niemożliwych na piętrze technicznym (PU s.13-14)"),
    ("dostawy", "od ul. Wybrzeże Słowackiego, z poziomu terenu, winda osobowo-towarowa (PU s.17; Wyj.4 odp.20)"),
])
wyj["lokalizacja_blokow"] = LOK
wyj["relacje_funkcjonalne"] = [
    OrderedDict([("od", "Wejście główne"), ("do", "Hol główny"), ("typ", "bezpośrednia"), ("zrodlo", "PU s.8")]),
    OrderedDict([("od", "Hol główny"), ("do", "Kancelaria ogólna, informacja, ochrona, poczekalnia, toalety, komfortka"), ("typ", "w holu"), ("zrodlo", "PU s.8-10")]),
    OrderedDict([("od", "Hol główny"), ("do", "Strefa konferencyjna (SK)"), ("typ", "bezpośrednie sąsiedztwo"), ("zrodlo", "PU s.8")]),
    OrderedDict([("od", "Hol główny"), ("do", "Bistro"), ("typ", "bezpośrednie sąsiedztwo"), ("zrodlo", "PU s.9")]),
    OrderedDict([("od", "Hol główny / parking podziemny"), ("do", "Strefa Sejmiku"), ("typ", "szybki przepływ większej liczby osób (dźwigi o dużej wydajności - wniosek)"), ("zrodlo", "PU s.6")]),
    OrderedDict([("od", "Parking podziemny"), ("do", "Hol główny"), ("typ", "połączenie bezpośrednie + ścieżki naprowadzające"), ("zrodlo", "PU s.8, s.11")]),
    OrderedDict([("od", "Sala obrad"), ("do", "Hol Sejmiku, sala multimedialna, reżyserka, socjalno-gastr., szatnia, toalety, pokój matki, komisje, kluby, sala radnych, pokój socjalny radnych"), ("typ", "ta sama kondygnacja"), ("zrodlo", "Wyj.21 odp.85")]),
    OrderedDict([("od", "Publiczność"), ("do", "Sala obrad"), ("typ", "oddzielne wejście; separacja od radnych"), ("zrodlo", "PU s.6; Wyj.4 odp.18")]),
    OrderedDict([("od", "Kancelaria Sejmiku"), ("do", "Gabinety Przewodniczącego i Wiceprzewodniczących"), ("typ", "bezpośrednia bliskość"), ("zrodlo", "PU s.7")]),
    OrderedDict([("od", "Kancelaria Sejmiku"), ("do", "Sala obrad"), ("typ", "ta sama lub sąsiednia kondygnacja"), ("zrodlo", "Wyj.21 odp.84-85")]),
    OrderedDict([("od", "Gabinety dyrekcji pionu"), ("do", "Sekretariat, sale narad, aneks socjalny, toalety, miejsce oczekiwania"), ("typ", "bliskość"), ("zrodlo", "PU s.5; Wyj.4 odp.19; Wyj.10 odp.62")]),
    OrderedDict([("od", "GW"), ("do", "Archiwa PZGiK i operatów, pracownia urządzeń"), ("typ", "ta sama kondygnacja"), ("zrodlo", "PU s.9-10; Wyj.6 odp.26")]),
    OrderedDict([("od", "Parking rowerowy"), ("do", "Podwórze; zaplecze sanitarne"), ("typ", "wjazd / bezpośrednie sąsiedztwo"), ("zrodlo", "PU s.12")]),
    OrderedDict([("od", "Strefa dostaw"), ("do", "Winda osobowo-towarowa; bistro; magazyny; odpady"), ("typ", "bezpośrednia (wniosek dla bistro/odpady)"), ("zrodlo", "PU s.15, s.17")]),
    OrderedDict([("od", "Serwerownia"), ("do", "Serwerownia główna (Wybrzeże Słowackiego 12-14)"), ("typ", "światłowód jednomodowy"), ("zrodlo", "PU s.15-16")]),
    OrderedDict([("od", "Budynek (skrzydło Mazowiecka)"), ("do", "Kamienica Mazowiecka 19"), ("typ", "przyleganie; zalecany potencjał przyszłego połączenia funkcjonalnego"), ("zrodlo", "PU s.3; Wyj.3 odp.13; Wyj.8 odp.37")]),
]
wyj["sejmik_sala_obrad"] = OrderedDict([
    ("pojemnosc_max", 100),
    ("uczestnicy_standardowi", OrderedDict([("radni", 36), ("zarzad_wojewodztwa", 5), ("skarbnik", 1), ("sekretarz", 1),
                                            ("przedstawiciel_wojewody", 1)])),
    ("stanowiska_stale_min", 44),
    ("pozostali", "obsługa techniczna i kancelaryjna, tłumacze PJM, media, zaproszeni goście, publiczność (liczby nie podane - PU s.6)"),
    ("propozycja_podzialu_100_miejsc_wniosek", OrderedDict([
        ("radni_w_tym_prezydium_4", 36), ("zarzad_skarbnik_sekretarz_wojewoda", 8), ("obsluga_kancelaryjna", 4),
        ("tlumacze_PJM", 2), ("media", 10), ("goscie", 15), ("publicznosc", 25)])),
    ("miejsca_dla_wozkow_min", "3 na 100 miejsc widowni (M.13 s.218) + dostępne stanowisko radnego, prezydium i mównica (PU s.6)"),
    ("kabiny_tlumaczy", "M.01 NIE wymaga kabin tłumaczy symultanicznych; wymagane miejsce dla tłumaczy PJM (PU s.6); M.13 s.219: napisy / tłumaczenie PJM przy nagłośnieniu"),
    ("galeria", "dopuszczalna (antresola) - Wyj.4 odp.18"),
    ("wysokosc", "nie narzucona (Wyj.8 odp.36)"),
    ("technologia", "zintegrowany system głosowania, wbudowane tablety i mikrofony (wyposażenie stałe), kamery, głośniki, nagrywanie i transmisja, pętla indukcyjna (PU s.6-7, s.12)"),
])
wyj["parking"] = OrderedDict([
    ("samochody_min_MPZP", "12 msc / 1000 m2 PU biur i obiektów konferencyjnych (MPZP par.13 pkt 1 lit. e, M.03 s.15); minimum (Wyj.21 odp.83)"),
    ("samochody_min_przy_PU_ekstrakcji", msc_min),
    ("samochody_min_gdy_hol_foyer_liczone_do_PU", math.ceil(12 * (PU + RU_SW) / 1000.0)),
    ("PU_przyjete_do_obliczenia", PU),
    ("OzN_min", ozn_min),
    ("OzN_regula", "1 st. przy 6-15; 2 przy 16-40; 3 przy 41-100; 4% przy >100 (M.13 s.81); wymiary 3,6 x 5,0 m (M.13 s.80)"),
    ("EV", "infrastruktura ładowania wymagana (PU s.13); liczba punktów wg przepisów (do weryfikacji w module prawnym)"),
    ("MDS", "parking = miejsce doraźnego schronienia wg rozp. MSWiA z 9.07.2025 (PU s.13); pojemność nie podana"),
    ("rowery", "50 stanowisk na parterze, stojaki U, wjazd od podwórza (PU s.12); nie na -1 (Wyj.7 odp.32)"),
    ("hulajnogi", "brak wymogu w M.01 (luka) - zalecenie własne 10 miejsc z ładowaniem"),
    ("rampy_zjazdy", "zjazd/zjazdy z drogi publicznej do parkingu w obrębie Inwestycji (Reg. III.1.2); dojazd do terenu tylko od 3KDL/1, 4KDPL/3, 6KDB/2 (MPZP par.26 ust.3)"),
    ("garaz_brutto_szac_m2", int(round(msc_min * GAR_M2_NA_MSC, -1))),
])
wyj["strefy_dostepu"] = [
    OrderedDict([("kod", "Z0"), ("nazwa", "zewnętrzna publiczna"), ("zakres", "skwer dz. 9/2, dziedziniec/ogródek nieogrodzony dla pracowników i mieszkańców"), ("zrodlo", "Reg. III.1.2; PU s.16; Wyj.20 odp.77")]),
    OrderedDict([("kod", "Z1"), ("nazwa", "publiczna"), ("zakres", "hol, kancelaria ogólna, informacja, poczekalnia, bistro, toalety, komfortka; SK podczas wydarzeń"), ("zrodlo", "PU s.8-9; wniosek")]),
    OrderedDict([("kod", "Z2"), ("nazwa", "półpubliczna kontrolowana"), ("zakres", "galeria publiczności sali obrad (oddzielne wejście), hol Sejmiku w dni sesji, sale konferencyjne, poczekalnie przy gabinetach"), ("zrodlo", "PU s.6; Wyj.4 odp.18-19; wniosek")]),
    OrderedDict([("kod", "Z3"), ("nazwa", "biurowa"), ("zakres", "kondygnacje departamentów, sale narad, pokoje socjalne - kontrola dostępu"), ("zrodlo", "PU s.14; wniosek")]),
    OrderedDict([("kod", "Z4"), ("nazwa", "Sejmik / VIP"), ("zakres", "strefa radnych i prezydium, gabinety Przewodniczącego i Wiceprzewodniczących, sale komisji i klubów, sala multimedialna gości"), ("zrodlo", "PU s.5-7; wniosek")]),
    OrderedDict([("kod", "Z5"), ("nazwa", "techniczna / chroniona"), ("zakres", "serwerownia, archiwa GW, centrum monitoringu, pomieszczenia techniczne, strefa dostaw, odpady"), ("zrodlo", "PU s.8, s.10, s.13-17; wniosek")]),
    OrderedDict([("kod", "Z6"), ("nazwa", "parking / MDS"), ("zakres", "pracownicy; w dni sesji radni i goście; w sytuacji kryzysowej ludność (MDS)"), ("zrodlo", "PU s.12-13; wniosek")]),
]
wyj["technologia"] = OrderedDict([
    ("serwerownia", "<=50 m2, TIER II: dwutorowe zasilanie, SZR, UPS do startu agregatu, klimatyzacja z obu źródeł, redundancja UPS/agregat/chłodzenie; światłowód jednomodowy do Wybrzeże Słowackiego 12-14 (PU s.15-16)"),
    ("IT", "telefonia IP i transmisja danych, punkty dystrybucyjne na każdej kondygnacji; pokoje z punktami dla 3 (GW 4) stanowisk; magazynki z 3 punktami (PU s.4-5, s.9, s.14)"),
    ("AV", "sala obrad i sale komisji: kamery, mikrofony zintegrowane, głośniki, nagrywanie, transmisja, system głosowania, tablety; sale konferencyjne: prezentacje i transmisja; sale narad/kluby/sala radnych/sale spotkań: ekran + punkty dostępowe; sala multimedialna: ekran i głośniki (PU s.6-8)"),
    ("bezpieczenstwo", "kontrola dostępu z centralą; SAP z sygnalizacją głosową i wizualną; CCTV wewn./zewn. z rejestratorem; centrum monitoringu przy holu; interkom z miejsc oczekiwania na ewakuację (PU s.8, s.11, s.14)"),
    ("dostepnosc", "pętle indukcyjne (SK, Sejmik, kancelaria ogólna), tyflomapy, ścieżki naprowadzające, SIW zgodny ze standardami MSWiA i identyfikacją UMWD (PU s.11-12)"),
])
wyj["instalacje"] = OrderedDict([
    ("energia", "stacje SN/nn, agregaty, UPS, PV 0,4-1,0 MWp (dach dominanty i elewacje) + magazyn energii (PU s.13; M.12 pkt 1.B, 1.D)"),
    ("HVAC", "wentylacja mechaniczna z rekuperacją + klimatyzacja we wszystkich strefach; centrale i agregaty na piętrze technicznym (PU s.13-14)"),
    ("cieplo", "gruntowe pompy ciepła (rewersyjne, chłód), magazyny ciepła/chłodu krótkoterminowe i sezonowe; sieć ciepłownicza tylko rezerwowo/szczytowo; brak spalania paliw kopalnych (PU s.14; M.12 pkt 1)"),
    ("woda_kanalizacja", "woda wyłącznie z sieci; rozdział ścieków czarnych/szarych; woda szara do spłukiwania WC; analiza odzysku ciepła z wody szarej (PU s.14; M.12 pkt 2)"),
    ("deszczowka", "retencja i infiltracja (zbiorniki na terenie zewnętrznym, studnie chłonne, rozsączanie, PBC); wykorzystanie do podlewania, dachu zielonego, mycia nawierzchni, spłukiwania WC; przelew awaryjny (PU s.14; M.12 pkt 2.B)"),
    ("teletechnika", "IP, kontrola dostępu, SAP, CCTV; skalowalność i rezerwy (szachty, kanały) (PU s.14-15; Reg. III.1.9)"),
    ("windy", "liczba wg układu, dostępne dla OzN; min. 1 osobowo-towarowa w strefie dostaw; dedykowana winda Sejmiku niewymagana (PU s.15; Wyj.18 odp.71)"),
    ("BMS_EMS", "pełna integracja z BMS/EMS (M.12 pkt 1)"),
    ("dach", "dopuszczalny zielony dach ekstensywny (PU s.17); dach - tylko urządzenia niemożliwe na piętrze technicznym (PU s.13)"),
])
wyj["sumy"] = OrderedDict([
    ("pokoje_biurowe_24m2", pokoje_24), ("pokoje_biurowe_32m2_GW", pokoje_32),
    ("pow_pokoi_biurowych", pow_biur), ("stanowiska_max_w_pokojach", stan_max),
    ("PU_programowa_szac", PU), ("US_techniczna_szac", US), ("RU_w_blokach_SW_SK_SWD", RU_SW),
    ("KW_szac_30proc_PU", KW), ("netto_nadziemne_i_techniczne_szac", NETTO),
    ("PC_szac_bez_garazu", PC_NADZ), ("wskaznik_PU_do_PC", round(PU / PC_NADZ, 2)),
    ("bloki", OrderedDict((b, blok_suma(b)) for b in BLOK_NAZWY)),
])

with open(f"{OUT}/program.yaml", "w", encoding="utf-8") as f:
    f.write("# Program użytkowy UMWD (M.01) - ekstrakcja maszynowa. Wygenerowano: _build_program.py\n")
    f.write("# Wartości 'szacunek: true' = wniosek własny (M.01 nie podaje powierzchni); źródła w polu 'zrodlo'.\n")
    yaml.add_representer(OrderedDict, lambda d, data: d.represent_mapping("tag:yaml.org,2002:map", data.items()))
    def _lst(d, data):
        flow = len(data) <= 2 and all(isinstance(x, (int, float)) for x in data)
        return d.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=flow)
    yaml.add_representer(list, _lst)
    yaml.dump(wyj, f, allow_unicode=True, sort_keys=False, width=140, default_flow_style=False)

# ---------------------------------------------------------------------------
# 6. CSV
# ---------------------------------------------------------------------------
with open(f"{OUT}/program_tabela.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["blok", "id", "nazwa", "liczba", "pow_jedn", "pow_laczna", "osoby", "uwagi", "zrodlo"])
    for b in BLOK_NAZWY:
        for p in bloki[b]:
            uw = []
            if p.get("szacunek"):
                z = p.get("zakres_pow_jedn")
                uw.append("SZACUNEK (wniosek)" + (f" zakres {z[0]}-{z[1]} m2" if z else ""))
            uw.append("kat. " + p["kategoria_pn_iso"])
            if p.get("stanowiska_max"):
                uw.append(f"stanowiska max {p['stanowiska_max']}")
            if p.get("komorka"):
                uw.append("komórka zał.1 nr " + p["komorka"])
            uw += p.get("wymagania", [])
            w.writerow([b, p["id"], p["nazwa"], p["liczba"], p["pow_jedn"], p["pow_laczna"],
                        "" if p.get("osoby") is None else p["osoby"], " | ".join(uw), p["zrodlo"]])

# ---------------------------------------------------------------------------
# 7. Raport kontrolny na stdout
# ---------------------------------------------------------------------------
print("kadra:", tot, "OK" if tot == Z1_SUMA_PU else "BLAD")
print("pokoje 24:", pokoje_24, "pokoje 32:", pokoje_32, "pow biur:", pow_biur, "stanowiska max:", stan_max)
for b in BLOK_NAZWY:
    n_off = sum(p["liczba"] for p in bloki[b] if p["id"].split(".")[-1] in ("DYR", "ZDYR", "SAM", "SEK", "PR", "PR32", "CZ"))
    print(f"{b:4s} {blok_suma(b):8.1f}  pokoje_biur={n_off}")
print("PU", PU, "US", US, "RU_SW", RU_SW, "KW", KW, "NETTO", NETTO, "PC", PC_NADZ, "PU/PC", round(PU / PC_NADZ, 3))
print("parking min", msc_min, "OzN", ozn_min, "garaz brutto", round(msc_min * GAR_M2_NA_MSC, -1))
for b in biur_bloki:
    print(b, [(k["nr"], k["pokoje"], k["pow_biurowa"], k["stanowiska_max"]) for k in komorki[b]])
