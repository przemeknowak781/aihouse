# Braki danych modelu — instalacje sanitarne (PT-IS)

Plik generowany automatycznie przez `lamela.views.instalacje` przy tworzeniu rysunków PT. Elementy narysowane z oznaczeniem **[DO UZUPEŁNIENIA]** (linia kreskowa, kolor purpurowy, warstwa `I-BRAKI`) wyznaczono algorytmicznie albo przyjęto z obliczeń — do potwierdzenia/uzupełnienia w modelu.

Źródła: `model/budynek.yaml`, `model/instalacje.yaml`, `model/wyposazenie.yaml`, `model/dzialka.yaml`.

| Lp. | Element | Brak / stan w modelu | Proponowany format pola | Arkusze |
|---:|:---|:---|:---|:---|
| 1 | Ogrzewanie — pomieszczenia z niedoborem mocy podłogi | Moc nominalna PC (zakaz F-gazów dotyczy ≤ 12 kW — czynnik R290, GWP₁₀₀ = 0,02); 0.03 WC gościnne: gęstość strumienia ≤ q_G (θ_F ≤ 29 °C); 0.03 WC gościnne: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.06 Salon + jadalnia + kuchnia: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.09 Łazienka gościnna (natrysk): gęstość strumienia ≤ q_G (θ_F ≤ 33 °C); 0.09 Łazienka gościnna (natrysk): moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL | wyposazenie.yaml: {typ: grzejnik, xy, obrot, moc_W} (grzejnik łazienkowy) lub decyzja projektowa | PT-IS-09, PT-IS-10, PT-IS-11 |
| 2 | Piony c.o. (zasilanie rozdzielaczy P1, P2) | brak tras pionów c.o. w instalacje.yaml — przyjęto pion proponowany przy rozdzielaczu R-P1 | piony: [{id: PCO, xy: [x, y], rodzaj: co, kond: [P0, P1, P2], opis}] | PT-IS-09, PT-IS-10, PT-IS-11 |

Po uzupełnieniu danych w `model/*.yaml` (lub w `tools/buduj_model.py`) wystarczy ponownie wygenerować arkusze: `PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki` (analogicznie `arkusze_ie.yaml`).
