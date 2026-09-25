# Braki danych modelu — instalacje sanitarne (PT-IS)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | Pion/szacht wentylacyjny (SUP, ETA) | brak w modelu szachtu wentylacyjnego (szacht SI zajęty przez piony wod.-kan. i deszczowe) — przyjęto lokalizację proponowaną algorytmicznie | pomieszczenia: {nazwa: 'Szacht wentylacyjny SW', wielobok} + instalacje.piony: [{id: W1, xy, rodzaj: wentylacja, kond: [P0, P1, P2]}] | PT-IS-09 |
| 2 | Piony c.o. (zasilanie rozdzielaczy P1, P2) | brak tras pionów c.o. w instalacje.yaml — przyjęto pion proponowany przy rozdzielaczu R-P1 | piony: [{id: PCO, xy: [x, y], rodzaj: co, kond: [P0, P1, P2], opis}] | PT-IS-07 |
| 3 | Trasy przewodów (woda, kanalizacja, c.o., wentylacja) | model nie zawiera przebiegów przewodów — trasy wyznaczono algorytmicznie (ortogonalnie, przy ścianach, z pionów/rozdzielaczy do przyborów) | instalacje.trasy: [{medium: Wz\|Wc\|Cyrk\|Ks\|Z\|P\|SUP\|ETA, kond, linia: [[x, y], …], dn, z}] | PT-IS-02, PT-IS-07, PT-IS-09 |
| 4 | instalacje.piony — rodzaj pionu | lista pionów zawiera rury spustowe (RS…) bez pola `rodzaj`; biblioteka grupowania pionów traktowała je jako piony wod.-kan. — w obliczeniach do rysunków odfiltrowane | piony: [{id, xy, rodzaj: kanalizacja\|deszczowa\|woda\|co\|wentylacja\|teletechnika, kond: [P0, …], opis}] | PT-IS-02, PT-IS-07, PT-IS-09 |
| 5 | instalacje.wyroby | brak danych wyrobów (DTR/DWU) — obliczenia na danych przykładowych bibliotek (PC, wodomierz ∆p(Q3), EA k_v, wpusty, centrala went., moduł PV, falownik) | wyroby: {PC: {P_A7W35, COP, SCOP_35, L_WA}, wodomierz: {DN, Q3, dp_Q3}, EA: {kv}, centrala: {V_nom, eta_t, SFP}, PV: {modul: {...}, falownik: {...}}} | PT-IS-02, PT-IS-07, PT-IS-09 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
