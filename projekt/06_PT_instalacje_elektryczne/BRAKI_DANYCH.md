# Braki danych modelu — instalacje elektryczne (PT-IE)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | Punkty instalacji elektrycznych i teletechnicznych | model nie zawiera położeń opraw, łączników, gniazd i punktów teletechnicznych — rozmieszczenie algorytmiczne (opis w uwagach arkuszy) | instalacje.elektryka.punkty: [{typ: oprawa\|lacznik\|gniazdo\|wypust\|RJ45\|TV\|PIR, kond, xy, obrot, h, obwod, opis}] | PT-IE-01, PT-IE-02, PT-IE-03, PT-IE-04, PT-IE-05, PT-IE-06, PT-IE-07, PT-IE-08, PT-IE-09 |
| 2 | Trasy teletechniczne (pion, RACK) | brak w modelu pionu/tras teletechnicznych — przyjęto pion proponowany (wspólna lokalizacja z pionem wentylacyjnym) | instalacje.piony: [{id: T1, xy, rodzaj: teletechnika}], lokalizacje: {RACK: [x, y, kond]} | PT-IE-07, PT-IE-08, PT-IE-09 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
