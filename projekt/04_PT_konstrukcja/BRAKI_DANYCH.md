# BRAKI DANYCH — projekt techniczny konstrukcji (PT-BO)

Lista generowana automatycznie przez `lamela.views.konstrukcja` z: (1) braków zgłoszonych przez bibliotekę obliczeń (`AnalizaKonstrukcji.brak_danych`, uwagi „WYMAGA ANALIZY”), (2) elementów modelu bez wyników wymiarowania, (3) danych niezbędnych do rysunków wykonawczych, których model nie zawiera. Uzupełnienie — w `tools/buduj_model.py` (model generowany) lub w bibliotece obliczeń.

## Wyniki obliczeń — elementy bez wymiarowania lub z niespełnionymi warunkami

- Płyta(y) SW1: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) WYL1: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) IZ-ST2Z: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) PL-C2: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Płyta(y) PL-C1: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie nie może być narysowane z obliczeń [WYMAGA ANALIZY].
- Belka B1 (podciąg fasady E, odwrócony (+2,78…+3,85 = parapet boksu C);…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B3 (belka krawędziowa ST2 w osi A' (odwrócona, pod parapetem okn…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B4 (belka wspornikowa w osi 1 (w licu ściany P2, pod parapetem O…): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Belka B5 (belka wspornikowa w osi 3 (w ścianie pn. P2): wspornik 1,00 …): brak pozycji wymiarowania w bibliotece (belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].
- Biblioteka: PL-C1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PL-C1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: PL-C2: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: PL-C2: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: IZ-ST2Z: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: IZ-ST2Z: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC3)
- Biblioteka: SW1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: SW1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC4)
- Biblioteka: WYL1: brak przegrody — przyjęto płytę bez warstw
- Biblioteka: WYL1: klasa betonu nie wynika z modelu (pole mat / materiał warstwy) — przyjęto C30/37 (XC4)
- Biblioteka (uwaga analizy): Grupa płyt SW1: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt WYL1: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Ściana nośna S2-07 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Ściana nośna S2-08 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Ściana nośna S2-09 stoi na płycie ST2 + ST2Z + D2 + D3 + PL-2 bez ściany poniżej — obciążenie liniowe płyty; sprawdzić podciąg/żebro [WYMAGA ANALIZY].
- Biblioteka (uwaga analizy): Grupa płyt IZ-ST2Z: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt PL-C2: MES niewykonalny (MES płyty: za mało podpór) — pominięto
- Biblioteka (uwaga analizy): Grupa płyt PL-C1: MES niewykonalny (MES płyty: za mało podpór) — pominięto
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
