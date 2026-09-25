# Weryfikacja niezależna V1 — runda 2 (zgodność z WT/MPZP, spójność geometrii)

Data: 2026-09-25. Weryfikator: V1 (niezależny; modelu, skryptów projektu, `views/**` i `arkusze_*.yaml` nie zmieniano).
Przedmiot: `model/budynek.yaml`, `dzialka.yaml`, `wyposazenie.yaml`, `instalacje.yaml` po drugiej rundzie poprawek
(część 1 — funkcja/A3; część 2 — fizyka, woda, instalacje, K-1…K-12). Skrypty pomocnicze i wyniki:
`scratchpad/runda2_V1/` (`cokol2.py` — cokół i spadki terenu, `kolizje.py` — kolizje brył IR, `widoki_AR/` — arkusze PB-AR).

## 1. Uruchomione kontrole

| kontrola | wynik |
|---|---|
| `python3 -m lamela.model` (walidacja rdzenia) | 0 błędów, 0 ostrzeżeń, 373 INFO (pola spoza schematu) |
| `tools/audyt_wt.py` (raport do scratchpadu) | **0 NIEZGODNE**, 4 UWAGA, 166 OK, 2 INFO — UWAGI te same co po rundzie 1 (0.15/0.16, wyrzutnia↔SW1, PC-JZ od S), opisane w §10/§13 koncepcji |
| `tools/test_wskazniki.py` | ZALICZONE; A1 = moduł (H zabudowy 10,267 m, WT §6 9,974 m, Δ 0,000) |
| `tools/test_pipeline.py --szybko` | 23 / 23 |
| `tools/test_obliczenia_fizyka / _instalacje / _konstrukcja` | 24 / 22 / 28 — zaliczone |
| `tools/generuj_widoki.py` (PB-AR-01…10 → scratchpad) | 10 arkuszy, QA OK (1 ostrzeżenie/arkusz: dane projektanta w tabliczce) |
| kolizje brył IR (2035 brył budynku, bez otoczenia) | 934 styków — sklasyfikowane w §4 |
| cokół / spadek terenu (obwód P0 co 0,10 m, teren projektowany) | §3 |

## 2. Wskaźniki MPZP i WT (jedno źródło `lamela.wskazniki`)

| wskaźnik | wartość | wymóg | ocena |
|---|---|---|---|
| wysokość zabudowy (upzp art. 2 pkt 30 lit. a): z_top +10,000 (czerpnia) − t_śr 101,383 | **10,27 m** (od t_min informacyjnie 10,36) | ≤ 11,00 (rezerwa 10,70) — W-033 | ✓ |
| wysokość wg WT §6 (teren przy O0-03 101,302 → pokrycie D1 z klinem +9,626) | **9,97 m** | ≤ 12 m (N) | ✓ |
| pow. zabudowy / kontrolnie z płytami | 187,50 / 218,08 m² | ≤ 480 m² — W-030 | ✓ |
| PBC / intensywność / kondygnacje | 1 270,15 m² (79,4 %) / 0,248 / 3 | ≥ 800 m² / 0,05–0,80 / ≤ 3 | ✓ |
| PV D1 górna krawędź +9,863 ≤ korona attyki +9,876 | ✓ | W-033 | ✓ |
| odległości od granic (WT §12) — min.: RS5 5,61 m E, ściana P0 5,73 m E, T1 4,30 m W | ≥ 4,00 / 1,50 | ✓ |

`audyt_wt.py`, `podglad_modelu.py`, §9 koncepcji i tabela PZT (`views/site_data.py`) biorą wysokość z modułu — **K-3/K-11
rozwiązane w narzędziach i PZT**. Wyjątki: przekroje i elewacje AR (§5, V1-03) oraz stare wartości w §12 koncepcji (V1-12).

## 3. K-1 — teren przy budynku, cokół, spadki (brief §9 pkt 4 i 6, W-019)

Teren projektowany (TIN `punkty_projektowane`, próbka 0,05 m od lica, co 0,10 m po obwodzie P0):

* poza strefą 1,0 m od krawędzi otworów: **cokół min. 0,331 m**, spadek na 2 m **min. 2,8 %** — wymaganie spełnione na całym obwodzie ✓;
* strefy drzwi z odwodnieniem liniowym przy progu — zgodnie z briefem: DZ3/O0-06 (T3 −0,02, OL-6), DZ2/O0-08 (podest −0,12, OL-5 na
  szer. drzwi + 0,15), HS (OL-2, OL-2W) ✓;
* wejście DZ1/O0-09 + doświetle FX3/O0-10 + narożnik wnęki (x_dz 17,45…19,30): podest −0,02, spadek 2,3 %, OL-3 na krawędzi podestu
  1,35 m od drzwi, pod daszkiem PL-DA — akceptowalne (próg WZ-11T), do pokazania na detalu;
* **nierozwiązane: filarki ściany garażu przy bramie BR1 (O0-07)** — x_dz 19,30…20,35 (1,05 m, między wnęką wejścia a bramą) i
  25,35…25,52: nawierzchnia podjazdu 101,53 → **cokół 0,12 m** (0,02 m poniżej posadzki garażu −0,10); OL-1 leży 2,3 m od bramy,
  nie przy progu. Ani ≥ 0,30 m, ani „odwodnienie liniowe przy drzwiach” (V1-02).

Uwaga metodyczna: `lamela.wskazniki` do wysokości bierze *niższą* z rzędnych istn./proj. (poprawnie wg definicji upzp); przy podjeździe
teren istniejący (101,44–101,46) jest niższy od projektowanego — do kontroli cokołu właściwy jest teren projektowany (jak wyżej).

## 4. Geometria — kolizje brył, płyty, attyki, łączniki (A2 K-1, I-1…I-8)

Rozwiązane (sprawdzone w IR): stropy ST1/ST2 i dachy D1–D4 po licu warstwy konstrukcyjnej (brak kolizji beton–ETICS); attyki ŻB 0,18
w osi muru (D1 x −1,10…12,09, y −0,09…8,84), korona D1 +9,876; B10 pod D1 (I-1); ścianka SCZB15 ciągła przez stropy (I-2);
wierzchy PL-E/PL-DA +3,00, PL-2 +6,15, PL-3 +9,30 = stropy (I-4); PL-D do narożnika garażu (I-8); lamele domknięte w narożach (D-7);
nadproża N* (D-8); B1/B2 b 0,18 (D-9). Kolizje typu ściana–nadproże, rama okna–izolacja (ciepły montaż 4 cm), płyta–żebro
fundamentowe, ścianka ŻB–strop — zamierzone (monolit/osadzenie).

Nierozwiązane lub nowe:

* **ST2Z** (strop nad powietrzem, wspornik A): obrys y −0,30…5,425 — sięga do lica ETICS (0,21 m poza lico konstrukcji −0,09 / 5,215)
  od S i N; koliduje z EPS S1-01 (naroże x −0,29…−0,09). Łącznik PL-2 leży więc poza płaszczyzną izolacji, a model nie odpowiada
  konwencji, wg której policzono mostki (REKOMENDACJE R-W6). To jedyna płyta nieprzycięta w rundzie 1 (V1-04).
* Żebra fundamentowe ZF (np. ZF1 y −0,30…+0,30, b 0,60 osiowo) wystają 0,20 m poza czoło PF1 (−0,10) pod ETICS; izolacja cokołu
  schodzi do −0,45, a wierzch żebra −0,40 (kolizja 5 cm); XPS i podsypka POD-P0 przechodzą przez żebra; warstwa ŻB przegrody POD-P0
  pokrywa się z PF1 (66 m², podwójna bryła do przedmiarów). K-12 „żebro licowane z czołem płyty” — nadal otwarte (BO) (V1-06).
* Filarki SIL18 0,12 m w S0-01 / S1-01 zajmują tę samą objętość co słupy stalowe SL1–SL6 (kolizja 100 % przekroju słupa) (V1-10).
* Obróbka blacharska attyk D4 (+3,85) i D3 (+6,66) wchodzi 0,235 m w ETICS i mur ścian P1/P2 (S1-01/02/03, S2-02/03/04)
  — `ir._attic_ring` nie przycina obróbki przy ścianie wyższej (V1-11).
* Drobne: N2/N3 (O0-09 / FX3) nachodzą 0,30 m — filarek 0,10 m; lepiej jedno nadproże 1,95 m; lamele LAM-S/W/E wchodzą 15 mm
  w tynk spodu PL-3; T1/T3 nakładają się 0,10 m²; ETICS S0-02/S0-05 (do +3,85) dubluje ETICS S1-01/S1-02/S1-03 na narożach (V1-11).

## 5. Rysunki AR (QA arkuszy w scratchpadzie)

* **Wysokość wg WT §6 na przekrojach i elewacjach: „H = 9,79 m”** — `views/section.building_height` liczy własną metodą (tylko drzwi
  `drzwi_zewn`, teren IR, dach bez klina); moduł podaje 9,97 m. To piąta wartość w dokumentach — K-3 niezamknięte dla AR (V1-03).
* Rzut parteru: wyspa kuchenna rysowana **z 3 hokerami w ciągu roboczym** i z płytą po stronie jadalni — `symbols.kitchen_island`
  ma domyślnie `stools=3`, a model nie może tego wyłączyć; przy kluczu `krzesla` rysunek się wysypie (`chairs` zamiast `stools`).
  Rysunek jest sprzeczny z rozwiązaniem K-1/A3 (V1-05). O0-14 (D1P) nadal rysowane jak skrzydłowe (znane z części 1).
* Rzut dachu: brak modułów PV (D1: 7, D4: 8), przelewów awaryjnych PA*, czerpni/wyrzutni i wywiewek — elementów wymaganych
  w briefie §9 pkt 3 i decydujących o W-033 (V1-08).
* Decyzja Inwestora K-13 (pnącza na kratownicy przy S0-02 + ażurowa osłona PC) — **nie ma jej w modelu ani w koncepcji** (V1-07).

## 6. Mostki i ciągłość izolacji (brief §9 pkt 1–2)

Katalog `projekt/08_obliczenia/mostki/` wygenerowano po ostatniej zmianie `buduj_model.py`. f_Rsi ≥ 0,72 we wszystkich węzłach (min. 0,836) ✓.
Rundę 2 kończą jednak z oceną **ZŁY** — izolacja PRZERWANA — węzły WZ-09a (ψ_oi 0,301 > domyślna 0,20, PN-EN ISO 14683), WZ-09b
i WZ-09c. Z oceną DO POPRAWY zostają WZ-06, WZ-07a i WZ-16a. W §14.2 F koncepcji wymieniono tylko WZ-06 i WZ-16a, a WZ-09a/b/c pominięto (V1-01).
Dla WZ-09a REKOMENDACJE podają wariant z blokiem 400 (ψ 0,216). W modelu jest blok 600 i XPS 10 cm, ale ψ się nie zmieniło (0,301).

## 7. Uwagi nierozwiązane lub nowe

| # | waga | miejsce | problem | poprawka | podstawa |
|---|---|---|---|---|---|
| V1-01 | istotny | `wezly` WZ-09a/b/c (SWG dom–garaż); §14.2 F koncepcji | ψ_oi 0,301 > 0,20, izolacja przerwana (TYNK→BET_KOM_600→ZB→TYNK); pominięte w rejestrze pozycji otwartych | blok u podstawy SWG o λ ≤ bloku 400 z wariantu REKOMENDACJI (albo blok termoizolacyjny z ETA) + XPS pod posadzką garażu pas ≥ 1,5–2,0 m (już jest) — przeliczyć; wpisać WZ-09a/b/c do §14.2 F | brief §9 pkt 1–2; PN-EN ISO 14683; PN-EN ISO 10211; W-248 |
| V1-02 | istotny | filarki ściany garażu przy bramie BR1: bud. x 11,70…12,75 i 17,75…17,92 (dz. 19,30…20,35; 25,35…25,52), y 9,68 | cokół 0,12 m (podjazd 101,53); OL-1 2,3 m od bramy, nie przy progu; moduł `drenaz.py` zwalnia „strefy drzwi z OL ≤ 2,5 m” — szerzej niż brief | OL przy progu bramy na całą szerokość + filarki (dz. y ≈ 42,5) albo pas żwiru/obniżenie do −0,30 przy filarkach; uszczelnienie cokołu (KMB/EPDM) ≥ 0,15 nad nawierzchnią na detalu D-03; strefę zwolnienia w `drenaz.py` ograniczyć do szer. drzwi + 0,15 m | brief §9 pkt 4 i 6; W-019; DIN 18533-1 (pomocniczo) |
| V1-03 | istotny | `views/section.py` `building_height` → PB-AR-05…10 („H = 9,79 m”); zespół rysunków | WT §6 liczone własną metodą (9,79 m zamiast 9,97 m z modułu) | `building_height` → `lamela.wskazniki.wskazniki(m)["wysokosc_WT6"]` (wartość, wejście, z_top) | K-3; WT §6; upzp art. 2 pkt 30 (dla H zabudowy) |
| V1-04 | istotny | `buduj_model.py` ST2Z: `R(xA2 - ZL, -EXT, -ZK, y3 + EXT)` | płyta nad powietrzem sięga lica ETICS (y −0,30 i 5,425) — beton w strefie izolacji, łącznik PL-2 poza płaszczyzną izolacji, model ≠ geometria obliczeń WZ-07a | obrys ST2Z do lica konstrukcji: y −0,09…5,215 (jak ST2/D1); łącznik PL-2 w pasie −0,30…−0,09; ETICS/wełna ciągła na czole; przeliczyć WZ-07a/16a | A2 K-1; REKOMENDACJE R-W6; brief §9 pkt 1–2; W-272 |
| V1-05 | istotny | PB-AR-01 wyspa (`symbols.kitchen_island`, `views/plan.FURN`) | 3 hokery w ciągu roboczym 1,195 m, płyta po stronie jadalni — sprzeczne z modelem (bez hokerów, płyta od ciągu) | w `draw_furniture` mapować `hokery`/`krzesla` → `stools` i stronę płyty; w modelu dopisać `hokery: 0` | A3 K-1 (krytyczna); ergonomia kuchni |
| V1-06 | istotny | `fundamenty` ZF*, PF1, przegroda POD-P0 | żebra osiowe b 0,60 wystają 0,20 m poza czoło płyty pod ETICS; izolacja cokołu −0,45 vs wierzch żebra −0,40; warstwa ŻB POD-P0 dubluje PF1 | żebra licowane z czołem płyty (K-12, uzgodnić z BO); dół izolacji cokołu = wierzch żebra lub izolacja obwodowa czoła żebra; z POD-P0 usunąć warstwę ŻB albo PF1 z przedmiaru | K-12; PN-EN ISO 13793; brief §9 pkt 1 |
| V1-07 | istotny | model/koncepcja — ściana S0-02 bryły G, PC-JZ | decyzja Inwestora K-13 (pnącza na kratownicy, osłona lamelowa PC) nie jest wprowadzona | dodać kratownicę na konsolach z przekładką (χ w katalogu), pas gruntu/donice z odwodnieniem, osłonę PC zachowującą strefę R290 i przepływ wg DTR; opis w koncepcji | decyzja Inwestora 25.09 (K-13); W-024; brief §9 pkt 1 |
| V1-08 | drobny | PB-AR-04 rzut dachu | brak PV, przelewów PA*, czerpni/wyrzutni, wywiewek, RS; nakładające się opisy | zespół rysunków: rysować z `energia.pv.pola`, `przelewy_awaryjne`, `wentylacja` | brief §9 pkt 3; W-033 |
| V1-09 | drobny | `tools/audyt_wt.py` §2 | PBC (1 268,51) i A_z z płytami (217,86) liczone własną metodą; moduł: 1 270,15 / 218,08 | brać z `lamela.wskazniki` (własna metoda jako kontrola) | K-3 („wszystkie narzędzia z modułu”) |
| V1-10 | drobny | S0-01 filarki przy SL1–SL4, S1-01 przy SL5/SL6 | mur SIL18 i słup stalowy w tej samej objętości | filarek jako obudowa słupa (materiał ≠ SIL18) albo słup w szprosie fasady bez muru | spójność modelu (A2 I-6) |
| V1-11 | drobny | `ir._attic_ring` (obróbka D3/D4); N2/N3; LAM-* ↔ PL-3; T1/T3; ETICS S0-02/S0-05 | obróbka attyki wchodzi 0,235 m w ETICS i mur ściany wyższej; nadproża nachodzą; lamele 15 mm w tynku; tarasy i ETICS nakładają się | przyciąć obróbkę przy ścianie wyższej; jedno nadproże O0-09+FX3; LAM z_do = spód tynku PL-3; rozdzielić T1/T3 | spójność modelu; brief §9 pkt 4 (obróbki) |
| V1-12 | drobny | koncepcja §12 (H 10,25 m, „zgodne z §9”), §13 (10,33 / 9,95), §4 wiersz J1–J3 („D2P”, „O0-16 przesuwne”), §7 („SW1 5,4 m”) | wartości nieaktualne po rundzie 2 (moduł: 10,27 / 9,97; SW1 5,29 m; O0-16 = D2 skrzydłowe) | oznaczyć jako historyczne lub zaktualizować | K-3; spójność dokumentacji |
| V1-13 | drobny | `dzialka.yaml` DR1 (`sr_korony: 7.0`, `wys: 10.0`) | K-2 spełnione (1,5 m od korony do NCH-1) tylko przy koronie 7 m | potwierdzić wymiar korony dojrzałej lipy (dendrolog / arch. krajobrazu) albo przyjąć gatunek o mniejszej koronie | K-2; W-144 [DO WERYFIKACJI źródła] |
| V1-14 | drobny | pomieszczenia 1.06 (0,49 m²), 2.06 (0,24 m²) | A2 D-10 nadal „częściowo” — powierzchnie klatek przypadkowe | rozstrzygnąć w zestawieniu PN-ISO 9836 (PT), jak zapisano | W-316; PN-ISO 9836 |

## 8. Status uwag wejściowych

* **A1:** 3 dawne niezgodności usunięte (0 NIEZGODNE). 4 UWAGI świadome i opisane w koncepcji: 0.15/0.16, SW1 stały (WT §152 ust. 12), PC-JZ od S (W-024 — 7,6 m od granicy E).
* **A2:** K-1 rozwiązane poza ST2Z (V1-04). I-1…I-8 i D-1…D-9, D-11, D-12 rozwiązane albo uzasadnione. D-10 częściowo (V1-14).
* **K-1:** rozwiązane na całym obwodzie poza filarkami przy bramie (V1-02).
* **K-3:** rozwiązane w narzędziach, §9 i PZT. Niezamknięte na arkuszach AR (V1-03) i w starszych sekcjach koncepcji (V1-12).
* **K-11:** rozwiązane — `audyt_wt.py` i `podglad_modelu.py` biorą wartości z modułu; wariant od t_min jest tylko informacyjny.
* **K-12:** rozwiązane: R-W3 (wywinięcie 0,28 m), R-W4 (OL-5), membrana i POD-G, długości `wezly`. Otwarte: żebro (V1-06) i WZ-09 (V1-01).
* **K-13:** nie wprowadzono (V1-07).
