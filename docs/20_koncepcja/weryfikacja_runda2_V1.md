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
