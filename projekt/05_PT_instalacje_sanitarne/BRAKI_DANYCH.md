# Braki danych modelu — instalacje sanitarne (PT-IS)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | Pion/szacht wentylacyjny (SUP, ETA) | brak w modelu szachtu wentylacyjnego (szacht SI zajęty przez piony wod.-kan. i deszczowe) — przyjęto lokalizację proponowaną algorytmicznie | pomieszczenia: {nazwa: 'Szacht wentylacyjny SW', wielobok} + instalacje.piony: [{id: W1, xy, rodzaj: wentylacja, kond: [P0, P1, P2]}] | PT-IS-12, PT-IS-14 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
