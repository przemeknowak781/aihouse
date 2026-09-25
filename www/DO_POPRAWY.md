# Strona www — do poprawy przed publikacją końcową (przegląd koordynatora 25.09.2026 ~09:25)

1. Rzuty SVG (rys01 — parter, rys03 — II piętro): kolizje etykiet — „Przedsionek gospodarczy” × „Pomieszczenie techniczne”,
   „Salon + jadalnia + kuchnia” na stole jadalnianym, „Gabinet / pokój gościnny okazjonalny” na meblach. Etykiety odsuwać
   od mebli i od siebie (algorytm jak w lamela.views.common.Placer) albo skracać nazwy z odnośnikiem do tabeli.
2. Energia: kafel „PV 15 × 430 Wp” — sprawdzić z faktycznym rozmieszczeniem modułów w modelu (energia.pv.pola) po zamrożeniu.
3. Schemat działki minimalnej: po stronie zachodniej wymiar 2,23 m do tarasu przy tabeli „zachód — lamele 4,00 m” — wymiar
   decydujący (4,00 m) ma być narysowany; taras naziemny opisać osobno albo nie wymiarować.
4. Publikacja: .glb nie jest serwowany — build zamienia go na assets/model.gltf.json (glTF z osadzonym buforem) — zachować.
5. Duże SVG wydzielane do assets/svg/*.svg (wstawiane skryptem) — zachować (strona czytelna do przeglądu przed publikacją).
