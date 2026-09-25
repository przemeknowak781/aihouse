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

## Wyniki obliczeń — elementy bez wymiarowania lub z niespełnionymi warunkami

- Płyta(y) SW1: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) WYL1: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) IZ-ST2Z: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) OB-A2: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) PS-A: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) PL-C2: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) PL-C1 + PL-D: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Belka B1 (podciąg fasady E, odwrócony (+2,78…+3,85 = parapet boksu C),…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B3 (belka krawędziowa ST2 w osi A' (odwrócona, pod parapetem okn…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B4 (belka wspornikowa w osi 1 (w licu ściany P2, pod parapetem O…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B5 (belka wspornikowa w osi 3 (w ścianie pn. P2): wspornik 1,00 …): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- ZF1: żebro (b = 60 cm, oś [[0.0, 0.0], [12.0, 0.0]]) wystaje poza obrys płyty PF1 o 2.39 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF2: żebro (b = 60 cm, oś [[12.0, 0.0], [18.375, 0.0]]) wystaje poza obrys płyty PF1 o 1.27 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF3: żebro (b = 60 cm, oś [[18.375, 0.0], [18.375, 9.375]]) wystaje poza obrys płyty PF1 o 1.87 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF4: żebro (b = 60 cm, oś [[18.375, 9.375], [12.0, 9.375]]) wystaje poza obrys płyty PF1 o 1.27 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF5: żebro (b = 60 cm, oś [[12.0, 9.375], [12.0, 8.75]]) wystaje poza obrys płyty PF1 o 0.10 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF6: żebro (b = 60 cm, oś [[12.0, 8.75], [0.0, 8.75]]) wystaje poza obrys płyty PF1 o 2.37 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- ZF7: żebro (b = 60 cm, oś [[0.0, 8.75], [0.0, 0.0]]) wystaje poza obrys płyty PF1 o 1.74 m² w rzucie — niespójność modelu (krawędź płyty a lico żebra); na przekrojach żebro przycięte do lica płyty. Uzgodnić obrys płyty/osie żeber (audyt A2).
- Biblioteka: PL-C1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PL-C1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: PL-C2: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PL-C2: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: IZ-ST2Z: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: IZ-ST2Z: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: PS-A: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PS-A: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: OB-A: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: OB-A: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: OB-A2: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: OB-A2: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: SW1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: SW1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC4)
- Biblioteka: WYL1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: WYL1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC4)
- Biblioteka: PL-D: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PL-D: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC4)
- Biblioteka (uwaga analizy): Grupa płyt SW1: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt WYL1: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Ściana nośna S2-07 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 + OB-A bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Ściana nośna S2-08 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 + OB-A bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Ściana nośna S2-09 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 + OB-A bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Grupa płyt IZ-ST2Z: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt OB-A2: MES niewykonalny (MES płyty: brak elementów (obrys zbyt mały?)) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt PS-A: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt PL-C2: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt PL-C1 + PL-D: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL1 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL2 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL3 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL4 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL1 w polu P2 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL2 w polu P2 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL3 w polu P2 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): ST1: podpora punktowa SL4 w polu P2 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): PL-E: podpora punktowa SL1 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): PL-E: podpora punktowa SL2 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): PL-E: podpora punktowa SL3 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]
- Biblioteka (uwaga analizy): PL-E: podpora punktowa SL4 w polu P1 — sprawdzić przebicie (6.4) [WYMAGA ANALIZY]

## Kontrola zbrojenia — pozycje niespełnione (szczegóły: raport kontroli zbrojenia)

- PF1 / strefa S1 (płyta) — przekrój niewystarczający (poz. MES-PF): A_s,prov = 0 < max(A_s,req; A_s,min) = 1 — M_Ed = 231 kNm/m > M_lim — wymagana wysokość h ≥ 0.25 m (obecnie 0.25 m) [WYMAGA ZMIANY MODELU]
- N-O1-11 / dołem (przęsło) (poz. 6.28): 7Ø10 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O0-18 / dołem (przęsło) (poz. 6.17): 5Ø16 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O0-02 / dołem (przęsło) (poz. 6.2): Nośność krzyżulców betonowych (η = 122%); Nośność strzemion (η = 216%); 6Ø20 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2)); A_s > A_s,max = 1584
- N-O0-02 / górą (podpory; ≥ 0,15·A_s,dół — 9.2.1.2(1)) (poz. 6.2): A_s,prov = 157 < max(A_s,req; A_s,min) = 283 mm² 
- N-O0-04 / dołem (przęsło) (poz. 6.4): 5Ø14 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O0-03 / dołem (przęsło) (poz. 6.3): Ugięcie długotrwałe (quasi-stała) ≤ L/250 (η = 161%); 5Ø16 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O1-13 / dołem (przęsło) (poz. 6.30): 5Ø14 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O1-01 / dołem (przęsło) (poz. 6.20): 6Ø10 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O0-11 / dołem (przęsło) (poz. 6.11): Nośność krzyżulców betonowych (η = 129%); Nośność strzemion (η = 228%); 8Ø20 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2)); A_s > A_s,max = 1584
- N-O0-11 / górą (podpory; ≥ 0,15·A_s,dół — 9.2.1.2(1)) (poz. 6.11): A_s,prov = 157 < max(A_s,req; A_s,min) = 377 mm² 
- N-O0-05 / dołem (przęsło) (poz. 6.5): Ugięcie długotrwałe (quasi-stała) ≤ L/250 (η = 252%); 5Ø20 nie mieści się w jednej warstwie przy b = 18 cm (odstęp w świetle ≥ 21 mm — 8.2(2))
- N-O0-05 / górą (podpory; ≥ 0,15·A_s,dół — 9.2.1.2(1)) (poz. 6.5): A_s,prov = 157 < max(A_s,req; A_s,min) = 236 mm² 
- N-O0-07 / dołem (przęsło) (poz. 6.7): Ugięcie długotrwałe (quasi-stała) ≤ L/250 (η = 219%)
