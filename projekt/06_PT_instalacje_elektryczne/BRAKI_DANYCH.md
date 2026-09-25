# Braki danych modelu — instalacje elektryczne (PT-IE)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | PV — rozmieszczenie modułów | w polu użytkowym dachu D1 zmieszczono 10 z 15 modułów (odsunięcia od krawędzi, otworów, czerpni/wyrzutni) | energia.pv.pole: [[x, y], …] (jawne pole montażu) lub zmiana liczby modułów | PT-IE-10 |
| 2 | PV — trasa DC | brak w modelu trasy przewodów DC i przepustu dachowego — przyjęto trasę po dachach (poza drogami ewakuacyjnymi) do pom. technicznego | energia.pv.trasa_dc: [[x, y, z], …], przepust: [x, y] | PT-IE-10 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
