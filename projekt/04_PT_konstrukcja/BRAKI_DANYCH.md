# BRAKI DANYCH — projekt techniczny konstrukcji (PT-BO)

Lista generowana automatycznie przez `lamela.views.konstrukcja` z: (1) braków zgłoszonych przez bibliotekę obliczeń (`AnalizaKonstrukcji.brak_danych`, uwagi „WYMAGA ANALIZY”), (2) elementów modelu bez wyników wymiarowania, (3) danych niezbędnych do rysunków wykonawczych, których model nie zawiera. Uzupełnienie — w `tools/buduj_model.py` (model generowany) lub w bibliotece obliczeń.

## Dane do uzupełnienia w modelu / uzgodnienia międzybranżowe

- Łączniki termoizolacyjne płyt wspornikowych (PL-*): model nie określa wyrobu (typ, wysokość, klasa odporności ogniowej, ETA) — rysunki podają siły m_Ed, v_Ed z obliczeń; dobór wyrobu „lub równoważnego” i sprawdzenie ugięcia z podatnością łącznika — przed wydaniem PT.
- Uziom fundamentowy: brak danych branży E (położenie GSU, potrzeba i klasa LPS wg analizy ryzyka PN-EN 62305-2, liczba przewodów odprowadzających) — trasa otoku, połączenia i wyprowadzenia na rzucie fundamentów są propozycją do uzgodnienia.
- Izolacja obwodowa przeciwprzemarzaniowa: brak w modelu danych klimatycznych do obliczenia wg PN-EN ISO 13793 (wskaźnik mrozowy F_d / F_n, średnia roczna temperatura) — wymiary D = 1,00 m (garaż 1,20 m), d_n = 10 cm przyjęte z modelu bez sprawdzenia.
- Przejścia instalacyjne przez płytę: instalacje.yaml zawiera tylko położenia pionów i przyborów — brak średnic tulei, rzędnych i spadków podejść kanalizacji pod płytą (projekt branży S).
- Geotechnika: parametry gruntu w modelu przykładowe (brief) — wymagana dokumentacja badań podłoża / projekt geotechniczny (kat. II) przed wydaniem PT; k_s płyty wyznaczono z M₀ modelu z obwiednią ×0,5/×2.
- Obciążenie posadzki garażu i pasa gospodarczego (kat. F / sprzęt techniczny) — model nie przypisuje kategorii obciążenia użytkowego do płyty fundamentowej; w MES płyty przyjęto kat. A (2,0 kN/m²) na całej powierzchni.
- Obrysy stropów/dachów w modelu po licu ocieplenia (płyty nad warstwą EPS) — do korekty w audycie A2 (lico warstwy konstrukcyjnej); rysunki są generowane z modelu i zaktualizują się automatycznie.
- Beton krawędzi wysuniętych: model XC4 + XF1 (C30/37, c_nom 40 mm) — biblioteka wymiaruje dla XC4 (c_nom 40 mm, zgodne); klasa XF1 wymaga napowietrzenia/w/c wg PN-B-06265 — wpisać w specyfikacji betonu.
- Zmiany modelu wymagane do spełnienia wszystkich warunków (słupy ŻB w węzłach A/1, A/3, C/3, D/3 ze stopami, jawny schemat wsporników B3–B5, ścieżka obciążeń fasady S1-01 przez B1, naroże PL-2, elementy niekonstrukcyjne w wspornikach) — projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md.

## Wyniki obliczeń — elementy bez wymiarowania lub z niespełnionymi warunkami

- ZF1: żebro (b = 60 cm, oś [[0.0, 0.0], [12.0, 0.0]]) wystaje poza obrys płyty PF1 o 2.39 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF2: żebro (b = 60 cm, oś [[12.0, 0.0], [18.375, 0.0]]) wystaje poza obrys płyty PF1 o 1.27 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF3: żebro (b = 60 cm, oś [[18.375, 0.0], [18.375, 2.875]]) wystaje poza obrys płyty PF1 o 0.57 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF4: żebro (b = 60 cm, oś [[18.375, 2.875], [18.375, 9.375]]) wystaje poza obrys płyty PF1 o 3.90 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF5: żebro (b = 60 cm, oś [[18.375, 9.375], [12.0, 9.375]]) wystaje poza obrys płyty PF1 o 3.83 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF6: żebro (b = 60 cm, oś [[12.0, 9.375], [12.0, 8.75]]) wystaje poza obrys płyty PF1 o 0.34 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF7: żebro (b = 60 cm, oś [[12.0, 8.75], [0.0, 8.75]]) wystaje poza obrys płyty PF1 o 2.39 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF8: żebro (b = 60 cm, oś [[0.0, 8.75], [0.0, 0.0]]) wystaje poza obrys płyty PF1 o 1.74 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF16: żebro (b = 50 cm, oś [[12.0, 2.875], [12.0, 8.75]]) wystaje poza obrys płyty PF1 o 1.46 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF17: żebro (b = 50 cm, oś [[18.375, 2.875], [12.0, 2.875]]) wystaje poza obrys płyty PF1 o 1.59 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
