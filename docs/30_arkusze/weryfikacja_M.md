# Weryfikacja M — metryki i składanie arkuszy (niezależna, adwersaryjna)

Data: 2026-09-25. Zakres: komplety wynikowe AR (PAB), PZT, IS, IE po wdrożeniu silnika ekonomicznego
(`src/lamela/views/uklad.py`) i poprawek zespołów. Weryfikator nie zmieniał kodu ani konfiguracji. Pliki robocze
(sondy, arkusze kontrolne, metryki): `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/arkusze/M/`.

Wymaganie Inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

## 1. Co sprawdzono i jak

| Kontrola | Metoda | Wynik |
|---|---|---|
| Metryki kompletów | `tools/metryki_arkuszy.py` na `projekt/03_PAB`, `02_PZT`, `05_…`, `06_…/rysunki` | tab. 2 |
| Odtwarzalność | ponowne wygenerowanie 4 kompletów z bieżącego modelu do katalogu roboczego | formaty i bloki identyczne jak w `projekt/` |
| Wypełnienie < 50 % | metryki (W obw.) | brak (najniższe 66 %, PT-IE-13) |
| Składanie | `lamela.draft.skladanie`, znaki składania odczytane z PDF | znaki na wszystkich 33 arkuszach zgodne z planem; tabliczka na wierzchu wszędzie; 20 arkuszy z pasami < 180 mm (§ 4) |
| Ramka i tabliczka | ramka z PDF: 20 mm po lewej, 10 mm z pozostałych stron; tabliczka w prawym dolnym rogu ramki | wszystkie 33 arkusze OK |
| Za duży format | sonda 1: ten sam arkusz przy L − 5…30 mm i przy innych wysokościach; sonda 2: jeden bok = szerokość rolki (297/420/594/610/841/914), drugi docięty do treści (krok 10 mm), porównanie **funkcją kosztu samego silnika** | 16 arkuszy ma tańszy wariant (§ 3) |
| Skale (W-306, RPB § 9) | tabliczki i spisy | AR/IS/IE 1:50; PZT 1:500 + 1:200; schematy „—” (IS-10, IS-11, IE-14) — zgodne |
| Numeracja i spisy tomów | tabliczki (NR, ARKUSZ n/N, FORMAT) ↔ spis w `tom_*.pdf` ↔ `raport_widokow.json` | zgodne; rozjazd w opisach technicznych i w `projekt/wydanie` (§ 5) |
| PDF wektorowy (RPB § 2b) | PyMuPDF: obrazy rastrowe, prymitywy, fonty, rozmiar | 0 obrazów na arkuszach, tekst jako tekst, pliki 0,07–0,46 MB, tomy ≤ 1,1 MB |
| Testy | `tools/test_arkusze_formaty.py`; `tools/test_pipeline.py` (pełny i `--szybko`) | 28/28; pełny 27/28 przy obciążeniu CPU (flaky `test_podglad_www`, timeout kliknięcia), osobno PASS; `--szybko` 26/26 |

## 2. Metryki: stan wyjściowy → wynik

| Komplet | Arkuszy | Papier [m²] | W ważone | W min (arkusz) | Warstwy A4 | Składanie d/p/s |
|---|---|---|---|---|---|---|
| AR | 10 → 5 | 3,99 → **2,31** | 54 → **85 %** | 44 → 74 % (PB-AR-04) | 96 → 50 | 0/10/0 → 3/2/0 |
| PZT | 3 → 3 | 0,75 → **0,75** | 78 → **83 %** | 77 → 81 % (PZT-01) | 18 → 18 | 0/3/0 → 2/1/0 |
| IS | 17 → 11 | 6,49 → **3,84** | 51 → **81 %** | 37 → 71 % (PT-IS-08) | 170 → 90 | 0/17/0 → 3/8/0 |
| IE | 14 → 14 | 5,24 → **3,58** | 51 → **83 %** | 36 → 66 % (PT-IE-13) | 140 → 94 | 0/14/0 → 3/11/0 |
| **Razem** | 44 → 33 | 16,47 → **10,48 (−36 %)** | — | — | 424 → 252 | 0/44/0 → 11/22/0 |

Liczby zespołów potwierdzone (różnice ≤ 1 p.p. W, poza PZT-01: raport PZT podaje 77 %, pomiar 81 % — raport sprzed
poprawek silnika). Żaden arkusz nie ma wypełnienia < 50 %, żaden nie składa się „słabo”.

## 3. Formaty większe niż potrzeba — silnik pomija warianty „bokiem na rolkę”

Silnik bierze wysokość H tylko z listy 297/420/594/841/891 i dobiera długość L. Uzasadnienie w `uklad.py` to wydruk
z rolki: H = szerokość rolki, L odcięte. Ta sama zasada działa w drugą stronę: arkusz o **szerokości** równej rolce
(420, 594, 610 mm) i wysokości dociętej do treści drukuje się bez odpadu, a takich kandydatów silnik nie generuje.
Sonda 2 policzyła je funkcją kosztu silnika (`uklad.koszt` z karami składania, niestandardu, części uwag):

| Arkusz | Jest | Tańszy wariant (koszt silnika) | Papier | Warstwy A4 |
|---|---|---|---|---|
| PZT-01 | A2 420×594, 0,2495 | **420×477**, 0,2146 | −20 % | 6 → 6 |
| PB-AR-02 | 770×420, 0,3598 | 594×487, 0,3130 | −11 % | 10 → 6 |
| PT-IS-01 | 790×420, 0,3691 | 610×507, 0,3313 | −7 % | 10 → 6 |
| PT-IS-03 | 710×420, 0,3317 | 594×487, 0,3130 | −3 % | 10 → 6 |
| PT-IS-05 | 590×841, 0,5315 | 594×807, 0,5135 | −3 % | 9 → 9 |
| PT-IS-06 | 710×420, 0,3350 | 594×457, 0,2937 | −9 % | 10 → 6 |
| PT-IS-08 | 710×420, 0,3317 | 594×447, 0,2844 | −11 % | 10 → 6 |
| PT-IE-01, -10, -11, -13 | 690×420, 0,322–0,326 | **594×437**, 0,2781 | −10 % | 10 → 6 |
| PT-IE-04 | 570×594, 0,3487 | 594×497, 0,3194 | −13 % | 6 → 6 |
| PT-IE-05 | A2 594×420, 0,2595 | 594×407, 0,2590 | −3 % | 6 → 6 |
| PT-IE-06 | 730×297, 0,2322 | **420×447**, 0,2011 | −13 % | 5 → 6 |
| PT-IE-07 | 520×594, 0,3309 | 594×467, 0,2971 | −10 % | 6 → 6 |

Razem ok. **−0,42 m² (−4 % papieru kompletów)**, a na 9 arkuszach paczka A4 cieńsza z 10 do 6 warstw (pasy
210 + 192 + 192 zamiast 140 + 120 + 120 + 120 + 190). Wszystkie warianty: 1 blok uwag, bez kolizji
(`sprawdz_nakladanie`), tabliczka na wierzchu. **Sprawdzone na wygenerowanych arkuszach** (katalog roboczy `weryf/`):
PT-IE-13 594×437 (W 82 %), PT-IE-06 420×447 (89 %), PZT-01 420×477 (94 %) — QA OK, lista kolizji pusta, obejrzane
w całości: rzut w pełnej skali 1:50 / 1:500, legenda i uwagi pod rzutem, nic się nie nakłada.

Nie uznano za błąd: warianty krótsze o 5 mm (krok siatki długości 10 mm), PZT-01 410×594 (−2,4 %, zjada go kara
niestandardu 3 %), PB-AR-04 594×727 (przekroje jeden nad drugim, −9 %) — zespół AR świadomie wybrał jeden wiersz na
wspólnej linii terenu; to decyzja czytelności, warto ją tylko odnotować w `zastosowanie_AR.md`.
