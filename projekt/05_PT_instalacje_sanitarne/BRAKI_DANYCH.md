# Braki danych modelu — instalacje sanitarne (PT-IS)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | Odwodnienie powierzchni IZ-ST2Z | wspornik, A = 5,7 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 2 | Odwodnienie powierzchni PL-2 | taras, A = 21,3 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 3 | Odwodnienie powierzchni PL-3 | taras, A = 23,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 4 | Odwodnienie powierzchni PL-C1 | wspornik, A = 9,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 5 | Odwodnienie powierzchni PL-C2 | wspornik, A = 9,8 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 6 | Odwodnienie powierzchni PL-DA | taras, A = 3,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 7 | Odwodnienie powierzchni PL-E | taras, A = 23,7 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 8 | Odwodnienie powierzchni SW1 | wspornik, A = 2,9 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 9 | Odwodnienie powierzchni WYL1 | wspornik, A = 1,2 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | element `dachy` (SCHEMAT p. 5.1) albo `wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}` | PT-IS-07 |
| 10 | Przelewy awaryjne / wpusty | sprawdzenie niespełnione: Pole D1: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | dachy[].przelewy_awaryjne[].rzedna_dna > rzędna pokrycia przy wpuście | PT-IS-07, PT-IS-08 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
