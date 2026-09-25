# BRAKI DANYCH — projekt techniczny konstrukcji (PT-BO)

Lista generowana automatycznie przez `lamela.views.konstrukcja` z: (1) braków zgłoszonych przez bibliotekę obliczeń (`AnalizaKonstrukcji.brak_danych`, uwagi „WYMAGA ANALIZY”), (2) elementów modelu bez wyników wymiarowania, (3) danych niezbędnych do rysunków wykonawczych, których model nie zawiera. Uzupełnienie — w `tools/buduj_model.py` (model generowany) lub w bibliotece obliczeń.

## Dane do uzupełnienia w modelu / uzgodnienia międzybranżowe

- Łączniki termoizolacyjne płyt wspornikowych (PL-*): model nie określa wyrobu (typ, wysokość, klasa odporności ogniowej, ETA) — rysunki podają siły m_Ed, v_Ed z obliczeń; dobór wyrobu „lub równoważnego” i sprawdzenie ugięcia z podatnością łącznika — przed wydaniem PT.
- Uziom fundamentowy: brak danych branży E (położenie GSU, potrzeba i klasa LPS wg analizy ryzyka PN-EN 62305-2, liczba przewodów odprowadzających) — trasa otoku, połączenia i wyprowadzenia na rzucie fundamentów są propozycją do uzgodnienia.
- Izolacja obwodowa przeciwprzemarzaniowa: brak w modelu danych klimatycznych do obliczenia wg PN-EN ISO 13793 (wskaźnik mrozowy F_d / F_n, średnia roczna temperatura) — wymiary D = 1,00 m (garaż 1,20 m), d_n = 10 cm przyjęte z modelu bez sprawdzenia.
- Przejścia instalacyjne przez płytę: instalacje.yaml zawiera tylko położenia pionów i przyborów — brak średnic tulei, rzędnych i spadków podejść kanalizacji pod płytą (projekt branży S).
- Geotechnika: parametry gruntu w modelu przykładowe (brief) — wymagana dokumentacja badań podłoża / projekt geotechniczny (kat. II) przed wydaniem PT; k_s płyty wyznaczono z M₀ modelu z obwiednią ×0,5/×2.
- Obciążenie posadzki pasa gospodarczego (pomieszczenie techniczne — ciężar urządzeń wg PT-IS): w MES płyty kat. A (2,0 kN/m²); garaż (PF2) — kat. F wg modelu (fundamenty.elementy[PF2].obciazenie_uzytkowe).
- Obrysy stropów/dachów w modelu po licu ocieplenia (płyty nad warstwą EPS) — do korekty w audycie A2 (lico warstwy konstrukcyjnej); rysunki są generowane z modelu i zaktualizują się automatycznie.
- Beton krawędzi wysuniętych: model XC4 + XF1 (C30/37, c_nom 40 mm) — biblioteka wymiaruje dla XC4 (c_nom 40 mm, zgodne); klasa XF1 wymaga napowietrzenia/w/c wg PN-B-06265 — wpisać w specyfikacji betonu.
- Trzpienie ŻB w murze (SL9–SL21): technologia wykonania (kolejność murowanie/betonowanie, strzępia, kotwy muru) i zakłady prętów przez wieńce — do potwierdzenia przez wykonawcę; status zmian modelu — projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md.

## Wyniki obliczeń — elementy bez wymiarowania lub z niespełnionymi warunkami

- Obliczenia — poz. 10.1 PF1: niespełnione warunki: Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) (η = 259%); Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) (η = 111%) [WYMAGA ZMIANY PRZEKROJU / ANALIZY].
