# Rzuty 1:200 i model pomieszczeń – raport kontrolny

Wygenerowano z `model/koncepcja.json` (synteza 1.0, 17.11.2026) i `docs/20_program/program.yaml` narzędziem `tools/model_pomieszczen.py` → `model/budynek.json`, `model/zestawienie_pomieszczen.csv` (podstawa F.15.B); rysunki `tools/rzuty.py` → `build/rzuty/rzut_*_1-200.svg` (+ PNG), podglądy `docs/70_rysunki/podglady/rzut_*_1-200.png`. Powierzchnie netto wg PN-ISO 9836 z poligonów w świetle ścian. Numeracja: kod grupy (Wyj. 20 odp. 73) + numer kolejny; biura `KOD.nn` z numerem komórki z tabeli 1 M.01 w nazwie.

## 1. Testy-asercje

| test | wynik | szczegóły |
|---|---|---|
| liczba pokoi biurowych = sumy.pokoje | OK | 187 / 187 |
| pokoje GW 32 m² = sumy.pokoje_32 | OK | 8 / 8 |
| pokoje 24 m² = sumy.pokoje_24 | OK | 179 / 179 |
| powierzchnia pokoi ≥ 24,0 m² (GW ≥ 32,0 m²) | OK | poniżej: [] |
| pokoje per komórka zgodnie z zał. 1 M.01 (Wyj. 16/17) | OK |  |
| departamenty niedzielone (dopuszczalny podział wydziałami na 2 sąsiednie kondygnacje) | OK |  / sąsiednie (Wyj. 17): DRA: ['5', '6'] |
| rozmieszczenie komórek na kondygnacjach wg specyfikacji (z relokacjami Wyj. 17) | OK | kond. 6 DRA: 9/11 (wydział na kondygnacji sąsiedniej) |
| bez łączenia działów w pokojach (1 pokój = 1 komórka) | OK |  |
| sale narad = sumy.sale_narad | OK | 6 / 6 |
| pokoje socjalne = sumy.socjalne | OK | 15 / 15 |
| magazynki przy elewacji = sumy.magazynki | OK | 20 / 20 |
| WC z toaletą dostępną na każdej kondygnacji | OK | brak: [] |
| komfortka na parterze | OK |  |
| miejsca oczekiwania na ewakuację (MOE) w przedsionkach na każdej kondygnacji | OK | brak: [] |
| miejsca postojowe = podziemie.razem_miejsc | **BŁĄD** | 41 / 109 (−1: 29, −2: 12) |
| miejsca OzN ≥ podziemie.OzN | OK | 6 / 6 |

## 2. Sumy powierzchni netto per kondygnacja

| kondygnacja | pomieszczeń | pow. netto [m²] | w tym KW | pokoje biurowe (szt.) | stanowiska postojowe |
|---|---:|---:|---:|---:|---:|
| −2 | 20 | 1 264,4 | 97,4 | 0 | 12 |
| −1 | 27 | 2 093,4 | 129,3 | 0 | 29 |
| P | 48 | 1 794,8 | 166,4 | 4 | 0 |
| 1 | 81 | 1 935,2 | 480,5 | 38 | 0 |
| 2 | 82 | 1 934,2 | 480,5 | 38 | 0 |
| 3 | 78 | 1 937,9 | 463,0 | 35 | 0 |
| 4 | 84 | 1 932,4 | 472,8 | 34 | 0 |
| 5 | 43 | 1 018,5 | 323,1 | 21 | 0 |
| 6 | 43 | 1 018,0 | 325,7 | 17 | 0 |
| S | 29 | 1 021,4 | 185,1 | 0 | 0 |
| S (antresola) | 12 | 167,1 | 97,4 | 0 | 0 |
| **razem** | | **16 117,2** | | | |

## 3. Sumy per kod grupy (wszystkie kondygnacje) wobec programu (M.01)

| kod | nazwa bloku | model [m²] | program [m²] |
|---|---|---:|---:|
| KW | Komunikacja wewnętrzna | 3 221,4 | 2 570 |
| PPM | Parking podziemny pełniący funkcję MDS | 2 788,8 | 2 815 |
| PP | Pomieszczenia pomocnicze | 1 124,3 | 707 |
| DOS | Departament Ochrony Środowiska | 939,7 | 918 |
| SWD | Sejmik Województwa Dolnośląskiego | 870,7 | 1 049 |
| SW | Strefa wejściowa | 707,6 | 533 |
| IT | Infrastruktura techniczna (w tym serwerownia) | 673,1 | 1 262 |
| DI | Departament Infrastruktury | 623,5 | 606 |
| DGP | Departament Gospodarki i Promocji | 586,0 | 582 |
| DSS | Departament Spraw Społecznych i Rynku Pracy | 488,4 | 462 |
| DZ | Departament Zdrowia | 465,5 | 462 |
| SK | Strefa konferencyjna | 460,9 | 517 |
| KS | Kancelaria Sejmiku | 440,8 | 488 |
| PHS | Pomieszczenia higieniczno-sanitarne | 397,7 | 417 |
| PS | Pomieszczenia socjalne | 360,7 | 360 |
| SN | Sale narad | 359,9 | 360 |
| GW | Geodeta Województwa - Wydział Geodezji i Kartografii | 328,9 | 328 |
| DST | Departament Sportu i Turystyki | 320,3 | 318 |
| DKD | Departament Kultury i Dziedzictwa Kulturowego | 309,1 | 294 |
| DRA | Departament Rozwoju Aglomeracji | 279,5 | 270 |
| PPT | Pomieszczenia pracowników technicznych | 105,2 | 127 |
| PR | Parking dla rowerów | 90,3 | 115 |
| CZ | Członek Zarządu | 78,3 | 78 |
| DK | Dział Kancelaryjny II | 48,6 | 48 |
| DW | Dział Wsparcia Informatycznego II | 48,0 | 48 |

## 4. Kontrola 187 pokoi (zał. 1 M.01, Wyj. 16/17 – bez łączenia działów)

| kond. | specyfikacja (komórki) | model (pokoje biurowe wg kodu) |
|---|---|---|
| P | DK II 2, DW 2 | DK 2, DW 2 |
| 1 | DOS 38 | DOS 38 |
| 2 | DI 25, DST 13 | DI 25, DST 13 |
| 3 | DGP 24, GW 11 | DGP 24, GW 11 |
| 4 | CZ 3, DKD 12, DZ 19 | CZ 3, DKD 12, DZ 19 |
| 5 | DSS 19 | DRA 2, DSS 19 |
| 6 | KS 8, DRA 11 | DRA 9, KS 8 |

Pojemność elewacji (jednostki pokoju 24 m², sucha próba układu): kond. 1: 43, kond. 2: 43, kond. 3: 43, kond. 4: 43, kond. 5: 22, kond. 6: 20. Specyfikacja zakłada: kond. 1–4 po 43, kond. 5 i 6 po 24. Wieża bez skrzydła (kond. 5–6) mieści 22 jednostki (narożniki SW/NW/SE z końcami korytarzy przy elewacji, trzon B przy elewacji pd., trzon A wymuszający korytarz zach.), na kond. 6 łuk zajmują gabinet Przewodniczącego z zapleczem i asystent – zostaje 20 miejsc.

**Przeniesienia wykonane przez generator (relokacja nadmiaru):**

* SN.01 (sala narad) z kond. 5 na kond. 4
* PP.01 (magazynek) z kond. 5 na kond. 2
* PP.01 (magazynek) z kond. 5 na kond. 2
* PP.01 (magazynek) z kond. 5 na kond. 1
* DRA – wydział/komórka 5.2 (2 pok.) z kond. 6 na sąsiednią kond. 5 (Wyj. 17 odp. 70)

## 5. Garaż – wykonalność 109 miejsc

* **−2**: w układzie rysunku **12 m.p.** (OzN 1); specyfikacja 41. Powierzchnia garażu (stanowiska + drogi, bez rampy i techniki) 769,1 m² → górne oszacowanie przy bardzo wydajnym układzie 25 m²/m.p.: **≤ 30**, realnie (30 m²/m.p.): ≈ 25. Rampa 164,7 m², technika i pomieszczenia 233,2 m², trzony 97,4 m².
* **−1**: w układzie rysunku **29 m.p.** (OzN 5); specyfikacja 68. Powierzchnia garażu (stanowiska + drogi, bez rampy i techniki) 1 565,0 m² → górne oszacowanie przy bardzo wydajnym układzie 25 m²/m.p.: **≤ 62**, realnie (30 m²/m.p.): ≈ 52. Rampa 164,7 m², technika i pomieszczenia 226,4 m², trzony 129,3 m².

Razem w układzie: **41 m.p.**, górne oszacowanie powierzchniowe ≤ 92; wymaganie MPZP ≥ 12 m.p./1000 m² PU → przy PU 8 400 m² ≥ 101 m.p. **109 m.p. nie mieści się w obrysach −1/−2 przy drogach 6,0 m i stanowiskach 2,5 × 5,0 m.** Przyczyny: (1) siatka wieży 8,10 m z liniami słupów v = 0 / 8,10 / 21,60 przecinającymi pasma – drogi muszą omijać linie słupów, a pas 13,5 m między v = 8,10 i 21,60 zajmuje trzon A; (2) trzony A i B w środku rzutu; (3) rampa(y) 26,0 + kolejne odcinki (spadek 18 %, przejścia 9 %) w pasie dziedzińca i segmencie; (4) technika na −1/−2 (centrale, GPC, tryskacze, agregat, zbiorniki, ukrycie) ≈ 600 m²; (5) skrzydło 15 m (13,4 m w świetle ścian szczelinowych) mieści tylko jeden rząd stanowisk 90° z drogą 6,0 m. Do decyzji: transfer słupów nad garażem (ruszt na stropie −0,15) i siatka garażowa 7,5 / 16,0 m, przeniesienie techniki na dach segmentu / do wieży, rampa jednopasmowa (rewizja), ew. −2 także pod skrzydłem.

## 6. Rozbieżności ze specyfikacją i założenia własne

* Trakt skrzydła 15,0 m (0,50 + 6,10 + 1,80 + 6,10 + 0,50) nie mieści ścian korytarza – przyjęto ścianę zewn. 0,40 m, pokoje 3,95 × 6,08 m = 24,02 m², ściany korytarza 0,12 m, korytarz 1,80 m (M.13). Wieża: ściana 0,50, pokoje 3,95 × 6,10 = 24,10 m², korytarz 1,80.
* Ścianki między pokojami 0,10 m (wynika ze specyfikacji: oś 4,05 → netto 3,95); pozostałe ściany działowe 0,12 m, ściany trzonów 0,25 m.
* Osie konstrukcyjne v = 8,10 i 21,60 (spec.) przypadają w pasie korytarzy pierścieniowych (6,72–8,52 i 21,18–22,98) – słupy zaznaczone w osiach zwężają korytarz; do korekty siatki (np. v = 8,58 / 21,12) lub słupy w licu ścian korytarza.
* Hol przed dźwigami P1/P2 na kond. 1–6 ma 2,2 m (korytarz wsch. przy licu trzonu B): WT § 195 ≥ 1,6 m spełnione, M.13 zaleca 3,6 m. Hol przed A1/A2 (pd.) ≥ 3,6 m.
* Pokoje GW 32 m²: w strefach głębokich wieży 3,95 × 8,11 m, poza nimi format 4-modułowy 5,30 × 6,10 m (spec. dopuszcza oba).
* Magazynki: 20/20 przy elewacji; w strefach głębokich jako 2,60 × 9,25 m (głębokie), poza nimi 3,95 × 6,10 m – typ dobierany wg miejsca (więcej głębokich niż 7 ze spec.), co pozwala zmieścić program kond. 5–6.
* Kond. 6: dwie sale spotkań 20 os. (KS.05) i miejsce oczekiwania nie mieszczą się w strefie środkowej razem z WC i socjalnym – nadmiar przeniesiony niżej (lista w uwagach). Gabinet Przewodniczącego na łuku NE w pierścieniu głębokim z zapleczem od strony korytarza.
* Sejmik (S) i antresola – narysowane z poligonów specyfikacji (bez zmian); hol/kuluar przed dźwigami 2,25 m.
* Rampa i garaż liczone parametrycznie z `podziemie.rampa` (brama, szerokość, spadki, próg) i obrysów −1/−2.

### Uwagi generatora

* [relokacja] SN.01 (sala narad) z kond. 5 na kond. 4
* [relokacja] PP.01 (magazynek) z kond. 5 na kond. 2
* [relokacja] PP.01 (magazynek) z kond. 5 na kond. 2
* [relokacja] PP.01 (magazynek) z kond. 5 na kond. 1
* [relokacja] DRA – wydział/komórka 5.2 (2 pok.) z kond. 6 na sąsiednią kond. 5 (Wyj. 17 odp. 70)
* [strefa środkowa] kond. 6: brak miejsca w strefie środkowej – przeniesiono na kond. 5: KS.05 Sala spotkań 20 os. (przeszklona), DRA.OCZ Miejsce oczekiwania gości (DRA)
* [strefa środkowa] kond. 5: brak miejsca w strefie środkowej – przeniesiono na kond. 4: KS.05 Sala spotkań 20 os. (przeszklona), DRA.OCZ Miejsce oczekiwania gości (DRA)
* [dane wejściowe] bryła M: kolec (A→B→A) w wierzchołku (68.372, 63.74) – usunięto
* [dane wejściowe] Sejmik SWD.02: 57 zdublowanych/współliniowych wierzchołków – oczyszczono

## 7. Zależności od zapowiedzianej rewizji specyfikacji

1. **Kondygnacja S (S-2, antresola 180 m², galeria zach., trzon A do +30,90, 4 rzędy):** rzuty S i antresoli są rysowane wprost z `kondygnacja_sejmiku.pomieszczenia` / `antresola_strefy`; po zmianie danych wystarczy ponowne uruchomienie (bez zmian kodu, o ile zachowane zostaną klucze `obrys_en`/`obrys_uv`, `sala.rzedy`, `ognisko_rzedow_uv`). Trzon A na antresoli: dodać w `build_ANT` (lista trzonów).
2. **Rampa jednopasmowa 3,5 m wzdłuż ściany pn. segmentu, brama 4,0 m (v −0,4…−4,4), próg 119,10, technika przy ścianie pd.:** `ramp_spec()` sam rozpozna stronę (brama przy v≈0 → ściana pn.), szerokość i długość (spadki, próg); pomieszczenia w pasie pn. segmentu na parterze (trafo, rozdzielnia, BESS, odpady) są dziś układane przy licu pn. – po rewizji przenieść do pasa pd. (stała `segn` w `build_P`). Wejście nr 8 na rzucie P czyta zakres bramy z tekstu `wjazd`.
3. **Pas −1 pod dziedzińcem 7,0 → 5,0 m (−1 = 2 287 m², ok. 66 m.p.):** obrys −1 czytany z `podziemie['-1'].obrys_ccw`, droga T1 liczona od lica pasa (v = max(0,6; lico + 5,0)) – przeliczy się automatycznie; liczba miejsc spadnie o rząd w pasie.

