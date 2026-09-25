# Koncepcja — WARIANT W1: „wierność szkicowi i zwartość”

**Dom LAMELA** — dom jednorodzinny wolnostojący, 3 kondygnacje nadziemne (P0, P1, P2), bez podpiwniczenia, stropodachy.
Działka 123/4 (fikc.), 32,00 × 50,00 m, droga od północy. Data: 2026-09-25. Opracowanie koncepcyjne (etap: warianty → ocena → synteza).

**Podstawy:** brief `docs/00_brief_projektowy.md` (sekcja 1.2 — interpretacja v2), decyzje Inwestora z 25.09.2026
(„elewacja w S-kę” z samych przesuniętych brył; linia D **nie** jest płytą tarasową; płyty wysunięte 0,8–1,2 m; garaż 2-stan. w bryle parteru),
rejestr wymagań `docs/10_podstawy_prawne/` (dostępne: R1, R2, R5). Wg R1 rozporządzenie WT z 2002 r. utraciło moc 20.09.2026 —
projekt zakłada złożenie przez inwestora **oświadczenia z art. 102a PB** (Dz.U. 2026 poz. 1161), więc stosujemy WT
(t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu z 19.09.2026. Śnieg: strefa 2, s_k = 0,90 kN/m² (R5). Powierzchnie wg PN-ISO 9836
z modyfikacjami § 20 RZF (schody i spoczniki poza PU; garaż i pom. techniczne wykazane osobno — R2).

**Model:** wszystkie liczby i rysunki tego wariantu generowane są z jednego modelu parametrycznego (`model_W1.json` w tym katalogu;
źródło: skrypty w katalogu roboczym koncepcji). Układ: **x → wschód, y → północ, z → góra; (0,0) = przecięcie osi A i 1;
±0,00 = posadzka parteru = 101,65 m n.p.m.** Osie przechodzą przez środek warstwy konstrukcyjnej ścian. Wymiary w m, na rysunkach w cm.

| rysunek | zawartość |
|---|---|
| `rzut_P0.png` | rzut parteru z osiami, wymiarami, otworami, schodami, słupami, obrysem płyt nad |
| `rzut_P1.png` | rzut I piętra, boks C, linia D, dach zielony parteru/garażu |
| `rzut_P2.png` | rzut II piętra, lamele, pustka klatki ze świetlikiem, wysunięcia płyt |
| `elewacja_S.png` | elewacja południowa + skalibrowany szkic z liniami porównawczymi |
| `przekroj.png` | przekrój A-A (N–S przez schody i boks C) i B-B (W–E przez wsporniki zach. i garaż), rzędne |
| `zagospodarowanie.png` | działka, droga, linia zabudowy, odległości, dojazd, parkowanie, przyłącza, retencja, wskaźniki |

## 1. Idea

Sylweta „S” powstaje wyłącznie z **przesuniętych brył** (bez osobnej wstęgi/ramy): **A** (II piętro, bryła w lamelach) wysuwa się
na **zachód** 1,00 m poza lico bryły B; **B** (I piętro, bryła pełna 12,00 m) z przeszklonym **boksem C** i dalej **linią D**
(pogrubiona krawędź stropu nad parterem) prowadzi rytm na **wschód** aż do narożnika garażu **G** (19,20 m od lica zach. B);
**E** (parter) wraca na **zachód** — cienka płyta ST1 wysunięta 1,50 m na zachód poza lico B i 1,00 m na południe, pod nią ciągłe
przeszklenie strefy dziennej w 5 kwaterach. Wszystkie płyty mają głębokie krawędzie 0,8–1,2 m (poziome warstwy, okapy).

Priorytet W1: **maksymalna wierność proporcjom szkicu** (wszystkie charakterystyczne krawędzie elewacji w położeniach odczytanych ze
szkicu z tolerancją ≤ 0,45 m — patrz tabela 2) oraz **zwartość**: parter to jeden prostokąt 18,20 × 11,10 m (część mieszkalna + garaż),
piętra to dwa prostokąty 12,00 × 7,90 i 13,00 × 7,90 m ustawione jeden nad drugim z licami płd. i płn. w jednej płaszczyźnie;
**trzon schodowy centralnie przy ścianie północnej** (środek trzonu x = 6,10 wobec środka bryły B x = 5,70).

## 2. Odczyt szkicu i przyjęte wymiary (L = odległość od lica zach. bryły B; x = L − 0,30)

| element | szkic (odczyt, L [m]) | W1 (L [m]) | W1 (x w układzie budynku) | uwagi |
|---|---|---|---|---|
| A — bryła II piętra (lamele) | −1,0 … 12,2 | −1,00 … 12,00 | −1,30 … 11,70 | wspornik 1,00 m; lico wsch. = lico B (ściany w pionie) |
| A — płyta pod bryłą (ST2) | −2,4 … 12,6 | −2,20 … 12,40 | −2,50 … 12,10 | wysunięcie 1,20 m zach., 1,00 m płd., 0,40 m wsch. |
| A — płyta dachu (ST3) + attyka | −1,6 … 12,4 | −1,80 … 12,40 | −2,10 … 12,10 | wysunięcie 0,80 m zach./płd. |
| B — bryła I piętra | 0 … 12,0 | 0 … 12,00 | −0,30 … 11,70 | skala szkicu: B = 12,00 m (≈45,6 px/m) |
| C — boks przeszklony (3 kwatery) | 4,5 … 11,7 (2,17/2,66/2,35) | rama 4,25 … 12,00; szkło 4,50 … 11,60 (3 × 2,37) | 3,95 … 11,70 | rama wysunięta 1,00 m, siedzisko h = 0,55 |
| C — rama górna | 3,9 … 13,9 | 4,25 … 13,75 | 3,95 … 13,45 | wysięg 1,75 m na wschód poza B (lekka stal) |
| D — linia pozioma | 3,8 … 19,2 | 4,25 … 19,20 | 3,95 … 18,90 | pas krawędziowy stropu ST1 2,70–3,70 nad garażem — **bez tarasu** |
| D — pion (narożnik G) | 19,0–19,2 | 19,20 | 18,90 | lico wsch. garażu |
| E — przeszklenie parteru | 1,0 … 13,2 (5 kwater) | 1,00 … 13,20 (lica); szkło 1,405 … 12,795 | 0,70 … 12,90 | 5 równych kwater 2,28 m (w szkicu nierówne) |
| E — płyta dachu parteru | −1,5 … 14,1 | −1,50 … (ciągła do 19,20 jako D) | −1,80 … 18,90 | wysunięcie 1,50 m zach. poza B, 1,00 m płd. |
| G — garaż | 13,2 … 19,2 | 13,20 … 19,20 | 12,90 … 18,90 | w świetle 5,68 × 6,49 m |

Proporcje pionowe szkicu są umowne (pasmo B ~2× wyższe) — wysokości przyjęto wg WT. Linia D leży wyżej niż płyta E (jak w szkicu):
wierzch pasa D = **+3,70** (dolna rama boksu C = siedzisko + attyka dachu garażu), krawędź płyty E = 2,70–3,05.
Porównanie graficzne: `elewacja_S.png` (górny panel — szkic skalibrowany w poziomie, czerwone linie — krawędzie W1).

## 3. Pełna definicja wymiarowa

### 3.1 Siatka osi (środek warstwy konstrukcyjnej)

| oś | x [m] | rola | | oś | y [m] | rola |
|---|---|---|---|---|---|---|
| A' | -1,00 | ściana zach. P2 (ŻB, na tarczach P2) | | 1 | 0,00 | płd.: ściany P1/P2, słupy SL1–SL4 + belka ukryta ST1 w P0, ściana płd. garażu |
| A | 0,00 | ściana zach. P1 (ŻB, na tarczach P1) — **początek układu** | | 1a | 3,80 | ściana garaż / pom. gosp. |
| B | 1,00 | ściana zach. P0 (ŻB — podpora wsporników) | | 2 | 4,80 | ściana płd. trzonu (ŻB) + ściany nośne P0 (salon/ zaplecze), P1/P2 (strefa wsch.) |
| C | 3,70 | ściana zach. trzonu (ŻB) | | 3 | 7,30 | ściana płn. P1/P2 i trzonu; w P0 ściana wewn. nośna |
| D | 8,50 | ściana wsch. trzonu (ŻB) | | 4 | 10,50 | ściana płn. P0 (skrzydło płn. + garaż) |
| E | 11,40 | ściana wsch. P1/P2 (ŻB — ściana-tarcza nad kuchnią) | | | | |
| F | 12,60 | ściana wsch. części mieszkalnej P0 / zach. garażu | | | | |
| G | 18,60 | ściana wsch. garażu (narożnik „pionu D”) | | | | |

### 3.2 Poziomy (rzędne względne; ±0,00 = 101,65 m n.p.m.)

| element | rzędna / grubość |
|---|---|
| posadzka P0 | ±0,00 (warstwy na gruncie: jastrych z ogrzewaniem podł. 0,10 + EPS/XPS 0,20 + płyta ŻB 0,15 → spód −0,45) |
| garaż, pom. gosp. | −0,15 (spadek 2 % do bramy; próg 15 cm przy drzwiach EI30 do sieni) |
| strop ST1 (nad P0, dach garażu i skrzydła płn.) | spód +2,78, wierzch +3,00, gr. 0,22 |
| posadzka P1 | +3,15 (warstwy 0,15: jastrych z ogrz. podł. + izolacja akust./term.) |
| linia D (wierzch pasa krawędziowego / siedzisko boksu C) | +3,70; pas D: +2,70 … +3,70 |
| dach zielony nad P0/garażem | wierzch ≈ +3,45 (ocieplenie 0,20–0,25 + dach zielony ekstensywny 0,10–0,12), attyka +3,70 |
| strop ST2 (nad P1) | spód +5,93, wierzch +6,15, gr. 0,22 |
| posadzka P2 | +6,30 |
| strop ST3 (dach P2) | spód +9,08, wierzch +9,30, gr. 0,22 |
| pokrycie dachu P2 (spadek 2 %) | śr. +9,62 (PIR/EPS 0,25–0,35 + membrana) |
| attyka / okap dachu P2 | **+9,85** (najwyższy punkt konstrukcji) |
| wysokość kondygnacji / w świetle | 3,15 / **2,78 m** (wszystkie kondygnacje; garaż 2,93 m) |
| ławy fundamentowe | spód −1,10 (strefa przemarzania 0,80 m od terenu ≈ −0,30) |
| teren przy budynku | −0,22 (NE) … −0,34 (SW); najniższe wejście (HS salonu, W) -0,31 |

### 3.3 Przegrody (typy)

| kod | układ | lico wewn. / zewn. od osi |
|---|---|---|
| SZ1 — ściana zewn. | tynk 1,5 + silikat 18 (kl. 20, cienka spoina) **lub ŻB 18** w strefach tarcz + EPS grafit/MW 20 + tynk 1 | −0,105 / +0,30 (gr. 40,5 cm) |
| SW1 — ściana wewn. nośna | tynk + SIL 18 (lub ŻB 18 w trzonie) + tynk | ±0,105 |
| SD1 — ścianka działowa | tynk + SIL 12 + tynk | ±0,075 |
| SG1 — ściana dom/garaż (oś F) | tynk + SIL 18 + wełna 12 cm (garaż) + wyprawa; EI 60 | −0,105 / +0,22 |
| przeszklenie E | aluminium z przekładką term., 3-szybowe, U_w ≤ 0,9, g ≤ 0,35 z osłoną ZIP w kasecie | pas y −0,25 … −0,10 |

### 3.4 Obrysy zewnętrzne kondygnacji (lica zewnętrzne z ociepleniem)

| kondygnacja | obrys (x × y) | wymiary | pow. całkowita (brutto) |
|---|---|---|---|
| P0 (część mieszk. + garaż) | x 0,70 … 18,90, y -0,30 … 10,80 | 18,20 × 11,10 m | 202,02 m² |
| P1 (bryła B) | x -0,30 … 11,70, y -0,30 … 7,60 | 12,00 × 7,90 m | 94,80 m² + boks C 7,75 m² |
| P2 (bryła A) | x -1,30 … 11,70, y -0,30 … 7,60 | 13,00 × 7,90 m | 102,70 m² |
| boks C (P1) | x 3,95 … 11,70, y -1,30 … -0,30 | 7,75 × 1,00 m | 7,75 m² (z +3,00 do +5,45) |

### 3.5 PARTER P0 (±0,00)

**Ściany** (oś warstwy konstrukcyjnej):

| typ | położenie (oś warstwy konstr.) | od–do | grubość / przegroda |
|---|---|---|---|
| zewn. SZ1 | prostokąt osi x 1,00–18,60, y 0,00–10,50 | obwód (bez przeszklenia E x 1,105–12,495 w osi 1) | 18 cm SIL/ŻB + 20 cm EPS/MW + tynki = 40,5 cm; oś B: ŻB 18 (podpora wsporników) |
| wewn. | x = 3,70 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | x = 8,50 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 3,60–8,61 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 1,00–3,60 | SIL 18 nośna |
| wewn. | y = 4,80 | x 8,60–12,60 | SIL 18 nośna |
| wewn. | y = 7,30 | x 1,00–3,60 | SIL 18 nośna |
| wewn. | y = 7,30 | x 3,60–8,61 | ŻB 18 (trzon) |
| wewn. | y = 7,30 | x 8,60–12,60 | SIL 18 nośna |
| wewn. | x = 9,75 | y 4,91–7,20 | SIL 12 działowa |
| wewn. | x = 12,60 | y 0,00–10,50 | SIL 18 + MW 12 od garażu (EI 60) |
| wewn. | y = 3,80 | x 12,82–18,50 | SIL 18 nośna |
| wewn. | x = 4,80 | y 7,41–10,39 | SIL 12 działowa |
| wewn. | y = 8,80 | x 4,88–12,49 | SIL 12 działowa |
| wewn. | x = 6,80 | y 8,88–10,39 | SIL 12 działowa |
| wewn. | x = 9,40 | y 8,88–10,39 | SIL 12 działowa |
| wewn. | x = 11,00 | y 8,88–10,39 | SIL 12 działowa |

**Otwory** (położenie: zakres wzdłuż ściany w układzie budynku, w świetle muru; wysokość w świetle; parapet od posadzki kondygnacji):

| id | ściana / położenie | typ | szer. × wys. [m] | parapet [m] | symbol / uwagi |
|---|---|---|---|---|---|
| O0-01 | zach. (oś B), y 0,80–3,20 | drzwi HS | 2,40 × 2,60 | 0,00 | HS1 drzwi przesuwne na taras zach. |
| O0-02 | zach. (oś B), y 5,50–6,40 | okno | 0,90 × 0,80 | 1,50 | OK3  |
| O0-03 | zach. (oś B), y 8,20–9,80 | okno | 1,60 × 1,50 | 0,85 | OK1  |
| O0-04 | płn. (oś 4), x 7,30–8,30 | drzwi zewn. | 1,00 × 2,20 | 0,00 | DZ1 drzwi wejściowe |
| O0-05 | płn. (oś 4), x 8,40–8,90 | fix | 0,50 × 2,20 | 0,00 | FX1 doświetle boczne |
| O0-06 | płn. (oś 4), x 9,90–10,50 | okno | 0,60 × 0,80 | 1,50 | OK4  |
| O0-07 | płn. (oś 4), x 13,16–18,16 | brama | 5,00 × 2,25 | 0,00 | BG1 brama segmentowa 500x225 |
| O0-08 | wsch. (oś G), y 0,80–1,80 | drzwi zewn. | 1,00 × 2,10 | 0,00 | DZ2 drzwi do ogrodu (pom. gosp.) |
| O0-09 | wsch. (oś G), y 6,00–7,50 | okno | 1,50 × 0,80 | 1,40 | OK5  |
| D0-01 | ściana y=4,80, x 7,15–8,35 | przejście | 1,20 × 2,05 | 0,00 |  przejście spocznik -> jadalnia |
| D0-02 | ściana y=4,80, x 8,72–9,52 | drzwi | 0,80 × 2,05 | 0,00 |  otwierane na zewnątrz (półki) |
| D0-03 | ściana y=4,80, x 5,95–6,75 | drzwi | 0,80 × 1,80 | 0,00 |  schowek pod schodami |
| D0-04 | ściana y=7,30, x 1,95–2,85 | drzwi | 0,90 × 2,05 | 0,00 |  90 cm (senior) |
| D0-05 | ściana y=7,30, x 7,15–8,35 | przejście | 1,20 × 2,05 | 0,00 |   |
| D0-06 | ściana y=7,30, x 10,40–11,20 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D0-07 | ściana x=4,80, y 7,55–8,45 | drzwi | 0,90 × 2,05 | 0,00 |   |
| D0-08 | ściana y=8,80, x 5,40–6,20 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D0-09 | ściana y=8,80, x 7,30–8,20 | drzwi | 0,90 × 2,05 | 0,00 |  drzwi szklane wiatrołapu |
| D0-10 | ściana y=8,80, x 9,80–10,60 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D0-11 | ściana y=8,80, x 11,40–12,20 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D0-12 | ściana x=12,60, y 7,55–8,45 | drzwi | 0,90 × 2,05 | 0,00 |  EI30 samozamykające |
| D0-13 | ściana y=3,80, x 16,50–17,40 | drzwi | 0,90 × 2,05 | 0,00 |   |
| E1 | płd. (oś 1), x 1,10–3,38 | fix | 2,28 × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |
| E2 | płd. (oś 1), x 3,38–5,66 | drzwi HS | 2,28 × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |
| E3 | płd. (oś 1), x 5,66–7,94 | fix | 2,28 × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |
| E4 | płd. (oś 1), x 7,94–10,22 | drzwi HS | 2,28 × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |
| E5 | płd. (oś 1), x 10,22–12,49 | fix | 2,28 × 2,72 | 0,00 | przeszklenie strefy dziennej, słupek/słup SL w osi podziału |

**Pomieszczenia** (wieloboki netto w licach wykończonych):

| nr | pomieszczenie | kategoria | wymiary netto [m] (x × y) | pow. netto [m²] | wielobok (x,y) |
|---|---|---|---|---|---|
| 0.01 | Wiatrołap | komunikacja | 2,45 × 1,52 | **3,72** | (9,32, 8,88); (9,32, 10,39); (6,88, 10,39); (6,88, 8,88) |
| 0.02 | Hol | komunikacja | 4,53 × 1,32 | **5,97** | (9,40, 7,41); (9,40, 8,72); (4,88, 8,72); (4,88, 7,41) |
| 0.03 | Garderoba | pomocnicze | 1,85 × 1,52 | **2,81** | (6,72, 8,88); (6,72, 10,39); (4,88, 10,39); (4,88, 8,88) |
| 0.04 | WC | pomocnicze | 1,45 × 1,52 | **2,20** | (10,93, 8,88); (10,93, 10,39); (9,47, 10,39); (9,47, 8,88) |
| 0.05 | Schowek gosp. | pomocnicze | 1,42 × 1,52 | **2,16** | (12,49, 8,88); (12,49, 10,39); (11,07, 10,39); (11,07, 8,88) |
| 0.06 | Sień gospodarcza | komunikacja | 3,09 × 1,32 | **4,09** | (12,49, 7,41); (12,49, 8,72); (9,40, 8,72); (9,40, 7,41) |
| 0.07 | Pokój gościnny / gabinet | mieszk./pobyt | 3,62 × 2,99 | **10,82** | (4,72, 7,41); (4,72, 10,39); (1,10, 10,39); (1,10, 7,41) |
| 0.08 | Łazienka (prysznic) | pomocnicze | 2,49 × 2,29 | **5,70** | (3,60, 4,91); (3,60, 7,20); (1,10, 7,20); (1,10, 4,91) |
| 0.09 | Schody | schody (poza PU) | 4,59 × 2,29 | **10,51** | (8,39, 4,91); (8,39, 7,20); (3,81, 7,20); (3,81, 4,91) |
| 0.10 | Spiżarnia | pomocnicze | 1,07 × 2,29 | **2,45** | (9,68, 4,91); (9,68, 7,20); (8,61, 7,20); (8,61, 4,91) |
| 0.11 | Pom. techniczne | techniczne | 2,67 × 2,29 | **6,11** | (12,49, 4,91); (12,49, 7,20); (9,82, 7,20); (9,82, 4,91) |
| 0.12 | Salon + jadalnia + kuchnia | mieszk./pobyt | 11,39 × 4,79 | **54,62** | (12,49, -0,10); (12,49, 4,70); (1,10, 4,70); (1,10, -0,10) |
| 0.13 | Garaż 2-stanowiskowy | garaż / gosp. | 5,68 × 6,49 | **36,83** | (18,50, 3,90); (18,50, 10,39); (12,82, 10,39); (12,82, 3,90) |
| 0.14 | Pom. gosp. (rowery, ogród) | garaż / gosp. | 5,68 × 3,59 | **20,37** | (18,50, 0,10); (18,50, 3,69); (12,82, 3,69); (12,82, 0,10) |

Suma P0: PU (mieszk.+pomocn.+komunik.) **94,55 m²**, pom. techniczne 6,11 m², schody/spoczniki 10,51 m², garaż + pom. gosp. 57,20 m².

Funkcja: wejście od północy (daszek 1,50 m = wysunięcie ST1, x 6,60–10,00) → wiatrołap 0.01 → hol 0.02 → na osi wejścia spocznik trzonu (przejście 1,20 m) → jadalnia i widok na ogród. Z holu: pokój gościnny 0.07 (z łazienką 0.08 en-suite, drzwi 90 cm), garderoba 0.03; hol przechodzi w sień gospodarczą 0.06 → WC 0.04, schowek 0.05, pom. techniczne 0.11, drzwi EI30 do garażu 0.13. Strefa dzienna 0.12 (salon/jadalnia/kuchnia z wyspą, spiżarnia 0.10) na całej elewacji płd., wyjścia HS na taras płd. (E2, E4) i zach. (HS1, taras pod okapem ST1).

### 3.6 I PIĘTRO P1 (+3,15)

**Ściany** (oś warstwy konstrukcyjnej):

| typ | położenie (oś warstwy konstr.) | od–do | grubość / przegroda |
|---|---|---|---|
| zewn. SZ1 | prostokąt osi x 0,00–11,40, y 0,00–7,30 | obwód | 18 cm SIL/ŻB + 20 cm EPS/MW + tynki = 40,5 cm; osie A, E oraz N/S w strefie x ≤ 3,70–4,20: ŻB 18 (tarcze) |
| wewn. | x = 3,70 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | x = 8,50 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 3,60–8,61 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 8,60–11,40 | SIL 18 nośna |
| wewn. | x = 3,70 | y 0,10–4,70 | SIL 12 działowa |
| wewn. | y = 3,60 | x 0,10–3,62 | SIL 12 działowa |
| wewn. | y = 2,80 | x 8,43–11,29 | SIL 12 działowa |
| wewn. | x = 8,50 | y 2,73–4,70 | SIL 12 działowa |

**Otwory** (położenie: zakres wzdłuż ściany w układzie budynku, w świetle muru; wysokość w świetle; parapet od posadzki kondygnacji):

| id | ściana / położenie | typ | szer. × wys. [m] | parapet [m] | symbol / uwagi |
|---|---|---|---|---|---|
| O1-01 | zach. (oś A), y 0,90–2,70 | okno | 1,80 × 1,60 | 0,85 | OK2  |
| O1-02 | zach. (oś A), y 4,60–6,40 | okno | 1,80 × 1,60 | 0,85 | OK2  |
| O1-03 | wsch. (oś E), y 3,30–4,30 | okno | 1,00 × 1,20 | 1,00 | OK6  |
| O1-04 | wsch. (oś E), y 5,60–6,60 | okno | 1,00 × 0,80 | 1,40 | OK4  |
| O1-05 | płn. (oś 3), x 7,35–8,15 | okno | 0,80 × 1,50 | 0,90 | OK7 okno klatki (nad dachem P0) |
| O1-06 | płd. (oś 1), x 4,20–11,30 | otwór do boksu | 7,10 × 1,50 | 0,55 | C otwór do boksu C (siedzisko h=0,55) |
| D1-01 | ściana x=3,70, y 2,60–3,40 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D1-02 | ściana x=3,70, y 3,80–4,60 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D1-03 | ściana x=8,50, y 3,10–3,90 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D1-04 | ściana x=8,50, y 5,20–6,00 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D1-05 | ściana y=4,80, x 7,15–8,35 | przejście | 1,20 × 2,05 | 0,00 |   |

**Pomieszczenia** (wieloboki netto w licach wykończonych):

| nr | pomieszczenie | kategoria | wymiary netto [m] (x × y) | pow. netto [m²] | wielobok (x,y) |
|---|---|---|---|---|---|
| 1.01 | Pokój dziecka 1 | mieszk./pobyt | 3,52 × 3,42 | **12,04** | (3,62, 0,10); (3,62, 3,52); (0,10, 3,52); (0,10, 0,10) |
| 1.02 | Pokój dziecka 2 | mieszk./pobyt | 3,49 × 3,52 | **12,28** | (3,60, 3,67); (3,60, 7,20); (0,10, 7,20); (0,10, 3,67) |
| 1.03 | Pokój rodzinny / biblioteka + hol | mieszk./pobyt | wielobok | **28,86** | (3,77, 0,10); (11,29, 0,10); (11,29, 2,73); (8,43, 2,73); (8,43, 4,70); (3,77, 4,70) |
| 1.04 | Pralnia | pomocnicze | 2,72 × 1,82 | **4,95** | (11,29, 2,88); (11,29, 4,70); (8,57, 4,70); (8,57, 2,88) |
| 1.05 | Łazienka | pomocnicze | 2,69 × 2,29 | **6,16** | (11,29, 4,91); (11,29, 7,20); (8,61, 7,20); (8,61, 4,91) |
| 1.06 | Schody | schody (poza PU) | 4,59 × 2,29 | **10,51** | (8,39, 4,91); (8,39, 7,20); (3,81, 7,20); (3,81, 4,91) |

Suma P1: PU (mieszk.+pomocn.+komunik.) **64,30 m²**, pom. techniczne 0,00 m², schody/spoczniki 10,51 m².

Funkcja: ze spocznika trzonu (x 7,095–8,395) → hol-biblioteka 1.03 (otwarta przestrzeń rodzinna przed boksem C, siedzisko-czytelnia 7,10 m w wykuszu) → pokoje dzieci 1.01 (SW) i 1.02 (NW), oba z oknami zach.; pralnia 1.04 z oknem wsch.; łazienka 1.05 wejście bezpośrednio ze spocznika. Na wschód od bryły B — dach zielony ekstensywny parteru/garażu (nieużytkowy, bez wyjścia, bez tarasu).

### 3.7 II PIĘTRO P2 (+6,30)

**Ściany** (oś warstwy konstrukcyjnej):

| typ | położenie (oś warstwy konstr.) | od–do | grubość / przegroda |
|---|---|---|---|
| zewn. SZ1 | prostokąt osi x -1,00–11,40, y 0,00–7,30 | obwód | 18 cm SIL/ŻB + 20 cm EPS/MW + tynki = 40,5 cm; osie A', E, S (cała) i N (x ≤ 3,70): ŻB 18 (tarcze) |
| wewn. | x = 3,70 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | x = 8,50 | y 4,70–7,41 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 3,60–8,61 | ŻB 18 (trzon) |
| wewn. | y = 4,80 | x 8,60–11,40 | SIL 18 nośna |
| wewn. | x = 3,70 | y 0,10–4,70 | SIL 12 działowa |
| wewn. | y = 4,20 | x -0,90–3,62 | SIL 12 działowa |
| wewn. | x = 1,30 | y 4,28–7,20 | SIL 12 działowa |
| wewn. | y = 3,00 | x 3,77–8,43 | SIL 12 działowa |
| wewn. | x = 8,50 | y 0,10–4,70 | SIL 12 działowa |

**Otwory** (położenie: zakres wzdłuż ściany w układzie budynku, w świetle muru; wysokość w świetle; parapet od posadzki kondygnacji):

| id | ściana / położenie | typ | szer. × wys. [m] | parapet [m] | symbol / uwagi |
|---|---|---|---|---|---|
| O2-01 | płd. (oś 1), x -0,30–2,70 | okno | 3,00 × 2,10 | 0,60 | OK8 za lamelami, dolna kwatera VSG do 1,10 |
| O2-02 | płd. (oś 1), x 4,60–7,60 | okno | 3,00 × 2,10 | 0,60 | OK8  |
| O2-03 | płd. (oś 1), x 8,90–10,90 | okno | 2,00 × 2,10 | 0,60 | OK9  |
| O2-04 | zach. (oś A'), y 1,20–3,00 | okno | 1,80 × 1,60 | 0,90 | OK2  |
| O2-05 | zach. (oś A'), y 5,40–6,40 | okno | 1,00 × 0,80 | 1,50 | OK3  |
| O2-06 | wsch. (oś E), y 1,60–3,20 | okno | 1,60 × 1,60 | 0,90 | OK10  |
| O2-07 | płn. (oś 3), x 1,90–2,90 | okno | 1,00 × 0,80 | 1,50 | OK4  |
| D2-01 | ściana x=3,70, y 3,20–4,00 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D2-02 | ściana y=4,20, x 2,50–3,30 | drzwi | 0,80 × 2,05 | 0,00 |  łazienka |
| D2-03 | ściana y=4,20, x -0,30–0,50 | drzwi | 0,80 × 2,05 | 0,00 |  garderoba |
| D2-04 | ściana y=3,00, x 4,40–5,20 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D2-05 | ściana x=8,50, y 3,85–4,65 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D2-06 | ściana x=8,50, y 5,30–6,10 | drzwi | 0,80 × 2,05 | 0,00 |   |
| D2-07 | ściana y=4,80, x 7,15–8,35 | przejście | 1,20 × 2,05 | 0,00 |   |

**Pomieszczenia** (wieloboki netto w licach wykończonych):

| nr | pomieszczenie | kategoria | wymiary netto [m] (x × y) | pow. netto [m²] | wielobok (x,y) |
|---|---|---|---|---|---|
| 2.01 | Sypialnia rodziców | mieszk./pobyt | 4,52 × 4,02 | **18,17** | (3,62, 0,10); (3,62, 4,12); (-0,90, 4,12); (-0,90, 0,10) |
| 2.02 | Garderoba | pomocnicze | 2,12 × 2,92 | **6,19** | (1,23, 4,28); (1,23, 7,20); (-0,90, 7,20); (-0,90, 4,28) |
| 2.03 | Łazienka rodziców | pomocnicze | 2,22 × 2,92 | **6,48** | (3,60, 4,28); (3,60, 7,20); (1,38, 7,20); (1,38, 4,28) |
| 2.04 | Gabinet | mieszk./pobyt | 4,65 × 2,82 | **13,11** | (8,43, 0,10); (8,43, 2,92); (3,77, 2,92); (3,77, 0,10) |
| 2.05 | Hol | komunikacja | 4,65 × 1,62 | **7,53** | (8,43, 3,08); (8,43, 4,70); (3,77, 4,70); (3,77, 3,08) |
| 2.06 | Pokój (5. osoba / hobby) | mieszk./pobyt | 2,72 × 4,59 | **12,48** | (11,29, 0,10); (11,29, 4,70); (8,57, 4,70); (8,57, 0,10) |
| 2.07 | Pom. techn. (rekuperator, wyłaz) | techniczne | 2,69 × 2,29 | **6,16** | (11,29, 4,91); (11,29, 7,20); (8,61, 7,20); (8,61, 4,91) |
| 2.08 | Spocznik (pustka nad schodami) | schody (poza PU) | 1,30 × 2,29 | **2,98** | (8,39, 4,91); (8,39, 7,20); (7,09, 7,20); (7,09, 4,91) |

Suma P2: PU (mieszk.+pomocn.+komunik.) **63,97 m²**, pom. techniczne 6,16 m², schody/spoczniki 2,98 m².

Funkcja: apartament rodziców w części zach. (sypialnia 2.01 S+W za lamelami i nad wspornikiem, garderoba 2.02, łazienka 2.03), gabinet 2.04 (S), pokój 2.06 (S+E — dla 5. członka rodziny / hobby / gość), pom. techniczne 2.07 z rekuperatorem i wyłazem dachowym 90×120 (drabina stała) — wejście ze spocznika; nad pustką klatki świetlik 2,60 × 1,80 m.

### 3.8 Płyty, wysunięcia, boks C, lamele

| element | obrys (x × y) | rzędne | wysunięcie poza lico | uwagi |
|---|---|---|---|---|
| ST1 (dach P0/garażu, strop P1) | wielobok: (−1,80; −1,30) (18,90; −1,30) (18,90; 10,80) (10,00; 10,80) (10,00; 12,30) (6,60; 12,30) (6,60; 10,80) (0,70; 10,80) (0,70; 7,60) (−1,80; 7,60) | 2,78–3,00 | zach. 1,50 poza B (2,50 poza P0), płd. 1,00, daszek płn. 1,50 | otwór schodów x 3,805–7,095, y 4,905–7,195 |
| ST2 (strop P2) | x −2,50 … 12,10; y −1,30 … 7,60 | 5,93–6,15 | zach. 1,20 poza A, płd. 1,00, wsch. 0,40 | otwór schodów jw. |
| ST3 (dach P2) | x −2,10 … 12,10; y −1,10 … 7,60 | 9,08–9,30 | zach./płd. 0,80, wsch. 0,40 | świetlik x 4,20–6,80, y 5,10–6,90; wyłaz x 9,50–10,40, y 5,40–6,60 |
| pasy krawędziowe | ST1: 2,70–3,05; D: 2,70–3,70 (x 3,95–18,90); ST2: 5,90–6,25; ST3+attyka: 9,05–9,85 | — | — | beton architektoniczny / okładzina włókno-cement, szary |
| boks C | rama x 3,95–11,70, y −1,30 … −0,30; szkło x 4,20–11,30 w płaszczyźnie y = −1,10 (3 kwatery 2,37 m) | siedzisko 3,00–3,70, szkło 3,70–5,20, rama górna 5,20–5,45 | 1,00 m | otwór w ścianie P1 x 4,20–11,30, h 3,70–5,20; rama górna przedłużona do x = 13,45 |
| lamele A | płd.: y = −0,45, x −1,25 … 11,65 co 0,30; zach.: x = −1,45, y −0,45 … 7,55 co 0,30 | 6,25–9,05 | 0,15 m od lica | 6 × 20 cm, drewno termo (lub alu w kolorze drewna) |

### 3.9 Schody SCH1 (trzon ŻB, stos 3 kondygnacji, U-kształtne)

* Trzon w świetle: x 3,81 … 8,39 (4,59 m), y 4,91 … 7,20 (2,29 m); ściany ŻB 18 cm w osiach C, D, 2, 3.
* Na kondygnację: **18 podnóżków × 17,5 cm = 3,15 m**, stopnie **s = 28 cm**, **2h + s = 63 cm**, nachylenie 32°; 2 biegi po 9 podnóżków (8 stopni).
* Bieg „a” (pasmo płn. y 6,11 … 7,20, szer. 1,09 m): pierwszy podnóżek x = 7,095, w górę **na zachód**
  do x = 4,855 (linie krawędzi stopni x = 7,095 − k·0,28, k = 0…8), rzuty 2,24 m; Z → Z + 1,575.
* Spocznik międzykondygnacyjny: x 3,805 … 4,855 (1,05 m ≥ szer. biegu), y 4,905 … 7,195; rzędne +1,575 i +4,725.
* Bieg „b” (pasmo płd. y 4,91 … 6,00, szer. 1,09 m): z x = 4,855 w górę **na wschód** do x = 7,095; Z + 1,575 → Z + 3,15.
* Spocznik kondygnacyjny (wejście/wyjście na każdej kondygnacji): x 7,095 … 8,395 (1,30 m), y 4,905 … 7,195; przejścia w ścianie osi 2
  (x 7,15–8,35) do holi, w P0 także w ścianie osi 3 (do holu wejściowego); drzwi z podestu: P1 → łazienka 1.05, P2 → pom. techn. 2.07.
* Między biegami „duszek” 11 cm — pełna ścianka szklana/stalowa (balustrada) na całą wysokość biegów; pochwyty obustronne h = 0,90 m.
* Otwory w stropach ST1/ST2: x 3,805 … 7,095, y 4,905 … 7,195. W P2 nad biegiem „a” i spocznikiem międzykond. **pustka** (świetlik),
  balustrada h = 1,10 m, prześwity ≤ 0,12 m na krawędzi spocznika P2 (x = 7,095) i wzdłuż biegu.
* **Prześwit nad biegami:** biegi kolejnych kondygnacji leżą dokładnie nad sobą (przesunięcie pionowe 3,15 m) → prześwit pionowy nad
  każdym stopniem = 3,15 − 0,35 (płyta biegu mierzona pionowo) = **2,80 m ≥ 2,00 m**; nad spocznikiem międzykond. 4,725 − 0,20 − 1,575 = 2,95 m;
  na starcie biegu „a” w P0 pod płytą spocznika P1: 2,78 − 0,175 = 2,60 m; w P2 do stropu ST3: ≥ 2,78 m.

### 3.10 Piony instalacyjne (w jednej osi przez kondygnacje)

| pion | xy | przebieg |
|---|---|---|
| K1 | (11,20; 6,25) | kan. + woda: łaz. P1, pralnia P1, skropliny rekuperatora P2 -> pom. techn. P0 |
| K2 | (3,40; 7,05) | kan. + woda: łaz. P2 -> szacht 30x30 w narożu pok. 1.02 (przy trzonie) -> łaz. P0 |
| W1 | (8,80; 7,00) | kanały wentylacji mech. (rekuperator P2) -> łaz. P1 -> spiżarnia/kuchnia P0 |

Kuchnia (blat przy osi F), WC 0.04 i łazienka 0.08 odprowadzane poziomo pod posadzką P0 do kolektora wzdłuż skrzydła płn. i wyjścia
w osi x = 9,00 (studzienka rewizyjna przy granicy). Dach P2: wpusty + rury spustowe w narożach NE/NW (wewnątrz ocieplenia), dachy zielone
P0/garażu: wpusty z przelewami awaryjnymi przez attykę.

## 4. Koncepcja konstrukcji

**System:** ścianowo-płytowy; stropy żelbetowe monolityczne gr. 22 cm (C30/37, B500SP) pracujące jako płyty dwukierunkowe/ciągłe
na ścianach; ściany nośne z bloczków silikatowych 18 cm (kl. 20) oraz **żelbetowe 18 cm** w: trzonie schodowym (wszystkie kondygnacje),
ścianie P0 w osi B, „U” strefy zachodniej P1 i P2 (ściany zach. A / A' + ściany N i S do x ≈ 3,70–4,20), ścianach wsch. P1/P2 (oś E)
oraz ścianie płd. P2 (tarcza nad boksem C). Sztywność: trzon ŻB + tarcze + stropy jako przepony.

**Rozpiętości płyt (≤ 6,5 m):**
* ST1: pasmo płd. strefy dziennej — kierunek N–S, **4,80 m** (podpory: oś 1 = belka ukryta ~100×22 cm na słupach SL1–SL4
  + narożnikach ścian B i F; oś 2 = ściany nośne/trzon); pasmo środkowe 2,50 m; skrzydło płn. 3,20 m; dach garażu płyta dwukierunkowa
  6,00 × 6,50 m na ścianach F, G, 1a, 4 (obc. dach zielony ok. 1,8 kN/m² + śnieg 0,72 kN/m² + zaspy przy attyce/uskoku — wg R5).
* ST2 i ST3: płyty dwukierunkowe na obwodzie + trzon: strefa zach. (x 0/−1,0 … 3,70) pracuje głównie E–W, **3,70 / 4,70 m**;
  strefa środkowa N–S **4,80 m** (oś 1 – ściana trzonu w osi 2); strefa wsch. N–S 4,80 m (oś 1 – ściana nośna w osi 2 na P1/P2,
  pod nią ściana w osi 2 w P0) i 2,50 m.
* Ścianki działowe P1/P2 nie są nośne (SIL 12 na stropie jako obciążenie liniowe, R5).

**Słupy i belki:** SL1–SL4 — stal RK 120×120×8 (lub ŻB 25×25) w osi 1 za słupkami przeszklenia, x = 3,38, 5,66, 7,94, 10,22;
na stopach 1,0×1,0 m. Belka ukryta ST1 w osi 1 (od ściany B do ściany F) przenosi krawędź stropu, parapet P1 i siły skupione z tarcz
(z tarczy wsch. P1 w x = 11,40 — między SL4 a narożnikiem F, rozpiętość 2,38 m). Nadproże-tarcza nad otworem boksu C w ścianie P1
(x 4,20–11,30, 7,10 m): ŻB 24 cm od +5,20 do +5,93 zespolone z płytą ST2 i ścianą płd. P2 (ŻB) — tarcza o wysokości ~3,7 m (z otworami
okien P2) opiera się na tarczy zach. P1 (x ≤ 4,20) i na ścianie-tarczy wsch. P1 (oś E). Wariant zapasowy (do decyzji w PT): 2 słupki
stalowe 100×100 w słupkach ramy C (x = 6,57 i 8,93) → rozpiętości ~2,4 m.

**Wsporniki i ścieżka obciążeń (strefa zach. — „S” na zachód):**
1. **Bryła A (P2) — wspornik 1,00 m** poza ścianę A: ściana A' (ŻB) wisi na **ścianach-tarczach N (y = 7,30) i S (y = 0) kondygnacji P2**
   (ŻB 18 cm, wys. 2,93 m), które wspornikowo wychodzą 1,00 m poza ścianę A i są ciągle podparte na ścianach N/S P1 (zaplecze ≥ 3,70 m).
2. **Bryła B (P1) — wspornik 1,00 m** poza ścianę P0 w osi B: ściana A (ŻB) wisi na **ścianach-tarczach N i S kondygnacji P1**, wspornikowo
   1,00 m poza ścianę B; zaplecze: tarcza S do słupa SL1 (x = 3,383, 2,38 m) i dalej w nadproże-tarczę boksu C; tarcza N do ściany trzonu
   w osi C (2,70 m). Sumaryczny „schodkowy” wysięg ściany A' względem podpory na gruncie (oś B) = 2,00 m — przenoszony wyłącznie przez
   tarcze wys. ~2,9 m (ramię sił wewnętrznych ~2,3 m), a **nie** przez płyty; ściany murowane na wspornikach płyt — brak.
3. Ściana P0 w osi B (ŻB) → ława 0,70 × 0,35 m. Sprawdzić w PT: EQU (1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb), ugięcie końca ≤ wysięg/125
   (≤ 8 mm, R5), zarysowanie tarcz przy otworach okiennych (okna w tarczach N/S tylko poza strefą zakotwienia).
4. **Płyty wspornikowe** (poza obrysem ogrzewanym, z łącznikami termoizolacyjnymi z ETA w linii ocieplenia): ST1 — płd. 1,00 m
   (pas D + boks C, obciążenie liniowe od boksu ~3,5 kN/m), zach. 1,50 m (wolna płyta, bez ścian); ST2 — zach. 1,20 m, płd. 1,00 m,
   wsch. 0,40 m; ST3 — 0,80 / 0,40 m. Wszystkie wsporniki płyt ≤ 1,50 m i **bez ścian murowanych** na końcach. Część ST1 x −0,30 … 0,70
   i ST2 x −1,30 … −0,30 jest wewnątrz obrysu ogrzewanego (podłoga nad powietrzem zewn.) — ocieplenie od spodu, bez łączników.
5. **Rama górna boksu C** przedłużona 1,75 m na wschód (x 11,70 → 13,45): lekki kształtownik stalowy ocynkowany w okładzinie
   (≤ 0,5 kN/m), zakotwiony w ramie C i w ścianie-tarczy wsch. P1 przez łączniki termoizolacyjne stalowe.
6. **Wsch. P1/P2 (oś E) nad kuchnią:** ściany ŻB jako tarcze o rozpiętości 4,80 m (podpory: belka ukryta ST1 w osi 1 oraz ściana P0
   w osi 2) + 2,50 m do osi 3; brak ściany pod osią E w strefie dziennej (otwarta kuchnia).

**Fundamenty:** ławy żelbetowe 0,70 × 0,35 m (spód −1,10) pod ścianami zewn., trzonem i ścianami nośnymi (osie 1 garażu, 1a, 2, 3, 4,
B, C, D, F, G), stopy 1,0 × 1,0 m pod SL1–SL4; płyta posadzki 15 cm na XPS; grunt: piaski średnie I_D ≈ 0,6, woda gruntowa ~3,8 m p.p.t.
Wg R5: 3 kondygnacje i wsporniki → **II kategoria geotechniczna** (dokumentacja badań podłoża + projekt geotechniczny) — do potwierdzenia.

## 5. Zagospodarowanie działki

* **Położenie:** narożnik SW działki = (−7,30; −31,00) w układzie budynku; działka x −7,30 … 24,70, y −31,00 … 19,00
  (granica z drogą y = 19,00; linia zabudowy y = 13,00).
* **Odległości:** zach. — płyta ST2 4,80 m, dach ST3 5,20 m, płyta ST1 5,50 m, ściana P2 z oknami 6,00 m, ściana P1 7,00 m, ściana P0 8,00 m;
  wsch. — ściana garażu z drzwiami i oknem 5,80 m, ściany P1/P2 13,00 m, jednostka PC 3,40 m; płn. — elewacja P0 8,20 m od granicy z drogą
  (2,20 m za linią zabudowy), daszek wejścia 6,70 m (0,70 m za linią); płd. — boks C/płyty 29,70 m, taras 26,70 m.
* **Dojazd:** zjazd 6,0 m z ul. Lipowej → brama przesuwna 5,00 m (odjazd na wschód wzdłuż ogrodzenia, x 18,30–23,60) → podjazd
  6,00 × 8,20 m (kostka betonowa) do bramy garażowej BG1 5,00 × 2,25 m. **Miejsca postojowe:** 2 w garażu + 2 gościnne 2,50 × 5,00 m na
  podjeździe (tandemowo przed bramą) — MPZP ≥ 2 ✔.
* **Dojście:** furtka 1,00 m (x 7,30–8,30) i chodnik 1,50 m w osi drzwi wejściowych; wejście bezprogowe (teren −0,23 → spocznik
  przed drzwiami −0,02, chodnik o spadku ≤ 5 %).
* **Tarasy:** płd. x −1,80 … 12,90, y −4,30 … −0,30 + zach. pod okapem ST1 x −1,80 … 0,70, y −0,30 … 4,20; razem
  70,0 m², poziom −0,02 (deska kompozytowa na legarach); > 35 m² — objęty
  projektem (art. 29 PB w brzmieniu z 2026 r.). Dojście boczne do ogrodu: płyty x −1,80 … 0,70, y 7,60 … 10,80 oraz ścieżka wzdłuż
  płd. i wsch. ściany garażu (drzwi do pom. gosp.).
* **Pojemniki na odpady:** osłona 2,60 × 1,30 m przy podjeździe (x 9,30–11,90, y 14,60–15,90), **3,10 m od granicy z drogą**, dostęp od chodnika.
  WT § 23 ust. 1 (10 m od okien/drzwi i 3 m od granicy) — dla zabudowy jednorodzinnej odległości od okien nie stosuje się
  [DO WERYFIKACJI w rejestrze R3 — przyjęto zachowawczo ≥ 3 m od granic].
* **Wody opadowe:** z dachu P2 i płyt → zbiornik retencyjny 6 m³ (x ≈ 15,3; y ≈ −6,6; podlewanie ogrodu) z przelewem do skrzynek
  rozsączających ~5 m³ (x 14,00–18,40, y −12,40 … −10,20, ≥ 6 m od granic); dachy zielone P0/garażu retencjonują część opadu.
  Szacunek: A_red ≈ 185 m² × 150 l/(s·ha) × 15 min ≈ 2,5 m³ — zapas. Zakaz odprowadzania na drogę (MPZP) ✔.
  Zbiornik bezodpływowy 5–15 m³ — w PB objęty projektem (zgłoszenie wg art. 29 PB, R1).
* **Pompa ciepła:** jednostka zewn. powietrze–woda na fundamencie przy wsch. ścianie garażu (x 20,20–21,30, y 5,60–6,20),
  **3,40 m od granicy wsch.** (≥ 3,0 m), z dala od sypialni (najbliższe okno sypialni: pokój 2.06 — 9,6 m).
* **Przyłącza:** ZK w linii ogrodzenia przy bramie (x ≈ 12,4) → kabel YKY 5×16 do RG w pom. techn. 0.11; woda PE 40 z sieci PE 110
  (x = 11,20) do wodomierza w 0.11; kanalizacja PVC 160 z kolektora pod skrzydłem płn. (wyjście x = 9,00) przez studzienkę rewizyjną Ø425
  (1,40 m od granicy) do sieci PVC 200; światłowód do 0.11; gaz — nie przyłączany (dom all-electric).
* **Zieleń:** pas żywopłotu 1,0 m wzdłuż granic zach., wsch. i płd. (zieleń izolacyjna), drzewa w ogrodzie płd.;
  **ogrodzenie:** od drogi ażurowe h = 1,50 m (≤ 1,60, bez prefabrykatów betonowych), pozostałe panelowe h = 1,50 m.

## 6. Orientacja, doświetlenie, energia

* **Strefa dzienna na południe:** 5 kwater przeszklenia (33,71 m² w świetle ościeżnic z oknem zach., stosunek 1:1,6).
  Okap ST1 1,00 m nad +2,70: w południe 21.06 (wys. słońca ok. 61° dla φ = 52,4°) cień sięga 1,00·tg61° ≈ 1,80 m w dół —
  zacienia ok. 2/3 przeszklenia; w grudniu (14°) słońce wpada w pełni (zyski zimowe). Dodatkowo screeny ZIP w kasecie nad szkłem (g_c ≤ 0,35).
* **Boks C** (P1) — 3 kwatery pod okapem ST2 (1,00 m) i ramą górną; screen ZIP. **Bryła A** — pionowe lamele (ok. 20 % zacienienia
  czołowego, znacznie więcej przy niskim słońcu wsch./zach.), okna za lamelami z dolną kwaterą VSG jako barierą do 1,10 m.
* **Sypialnie:** dzieci — zachód (1.01, 1.02), rodzice — południe + zachód (2.01), pokój 2.06 — południe + wschód, pokój gościnny — zachód.
* **Północ:** tylko drzwi wejściowe z doświetlem, małe okno WC, okno klatki na P1 i małe okno łazienki P2 (≈ 4,5 m² łącznie);
  od północy pomieszczenia pomocnicze i komunikacja (trzon, hol, sień, garderoba, WC, schowek, techniczne, łazienki, pralnia).
* **Zwartość:** parter prostokąt 18,20 × 11,10 m, piętra prostokąty z licami płd./płn. w jednej płaszczyźnie; A/V_e (część ogrzewana,
  szacunek) ≈ 0,66 m⁻¹. Garaż poza strefą ogrzewaną (ściana SG1 z wełną 12 cm, drzwi EI30), jako bufor od NE.
* **Instalacje:** PC powietrze–woda (monoblok/split) + ogrzewanie podłogowe, zasobnik CWU 300 l, RG, wodomierz w pom. techn. 0.11
  (6,11 m² ≥ 6 m²); rekuperator w 2.07 (czerpnia/wyrzutnia przez dach), pion wentylacyjny W1 przy trzonie; PV ≤ 6,5 kWp
  (~15 modułów, ~30 m²) na dachu P2, cofnięte ≥ 1,0 m od krawędzi, poniżej attyki; wyłaz dachowy z 2.07.

## 7. TABELA KONTROLNA

### 7.1 Pomieszczenia — powierzchnie i wysokości

| pom. | pow. [m²] | minimum | wys. w świetle [m] | minimum | ocena |
|---|---|---|---|---|---|
| 0.12 Salon + jadalnia + kuchnia | 54,62 | 50,00 — strefa dzienna ≥ 50 (brief); pokój dzienny ≥ 16 (WT § 94) | 2,78 | 2,50 | ✔ |
| 0.07 Pokój gościnny / gabinet | 10,82 | 8,00 — pokój ≥ 8 (WT § 94) | 2,78 | 2,50 | ✔ |
| 1.01 Pokój dziecka 1 | 12,04 | 12,00 — pokój dziecka ≥ 12 (brief) | 2,78 | 2,50 | ✔ |
| 1.02 Pokój dziecka 2 | 12,28 | 12,00 — pokój dziecka ≥ 12 (brief) | 2,78 | 2,50 | ✔ |
| 1.03 Pokój rodzinny / biblioteka + hol | 28,86 | 16,00 — pokój dzienny rodzinny ≥ 16 | 2,78 | 2,50 | ✔ |
| 2.01 Sypialnia rodziców | 18,17 | 14,00 — sypialnia rodziców ≥ 14 (brief) | 2,78 | 2,50 | ✔ |
| 2.04 Gabinet | 13,11 | 8,00 — pokój ≥ 8 | 2,78 | 2,50 | ✔ |
| 2.06 Pokój (5. osoba / hobby) | 12,48 | 8,00 — pokój ≥ 8 | 2,78 | 2,50 | ✔ |
| 0.11 Pom. techniczne | 6,11 | 6,00 — pom. techniczne ≥ 6 (brief) | 2,78 | 2,20 | ✔ |
| pomieszczenia pomocnicze, komunikacja (wszystkie) | — | — | 2,78 | 2,20 | ✔ |
| garaż 0.13 (w świetle 5,68 × 6,49 m) | 36,83 | 5,60 × 6,00 m (brief) | 2,93 | 2,20 | ✔ |

### 7.2 Oświetlenie dzienne (WT § 57: okna ≥ 1/8 pow. podłogi; kuchnia z oknem)

| pom. | pow. podłogi [m²] | okna (symbol) | pow. okien w świetle ościeżnic [m²] | stosunek | wymóg ≥ 1:8 |
|---|---|---|---|---|---|
| 0.07 Pokój gościnny / gabinet | 10,82 | OK1 | 2,04 | 1:5,3 | ✔ |
| 0.12 Salon + jadalnia + kuchnia | 54,62 | FX2, HS2, FX2, HS2, FX2, HS1 | 33,71 | 1:1,6 | ✔ |
| 1.01 Pokój dziecka 1 | 12,04 | OK2 | 2,49 | 1:4,8 | ✔ |
| 1.02 Pokój dziecka 2 | 12,28 | OK2 | 2,49 | 1:4,9 | ✔ |
| 1.03 Pokój rodzinny / biblioteka + hol | 28,86 | C | 9,63 | 1:3,0 | ✔ |
| 2.01 Sypialnia rodziców | 18,17 | OK8, OK2 | 8,19 | 1:2,2 | ✔ |
| 2.04 Gabinet | 13,11 | OK8 | 5,70 | 1:2,3 | ✔ |
| 2.06 Pokój (5. osoba / hobby) | 12,48 | OK9, OK10 | 5,91 | 1:2,1 | ✔ |

Kuchnia — kwatera E5 (x 10,22–12,50) w strefie kuchni ✔. Łazienki bez okien (0.08 ma okno, 1.05 i 2.03 mają małe okna) — wentylacja mechaniczna.

### 7.3 Schody

| parametr | projekt | wymóg | ocena |
|---|---|---|---|
| wysokość stopnia h | 0,175 m (18 × 0,175 = 3,15) | ≤ 0,19 (WT § 68, jednorodzinny); cel ≈ 0,175 | ✔ |
| szerokość (głębokość) stopnia s | 0,28 m | cel ≈ 0,28 | ✔ |
| 2h + s | 0,63 m | 0,60–0,65 | ✔ |
| szerokość biegu w świetle | 1,09 m | ≥ 0,80 (WT); cel ≥ 1,00 | ✔ |
| spocznik międzykond. / kond. | 1,05 / 1,30 m | ≥ szer. biegu (1,00) | ✔ |
| prześwit nad biegami | ≥ 2,60 m (start), 2,80 m (typowo) | ≥ 2,00 m | ✔ |
| balustrady | ścianka między biegami, pochwyty 0,90; pustka P2 h = 1,10, prześwit ≤ 0,12 | WT § 296–298 [DO WERYFIKACJI] | ✔ |

### 7.4 Odległości od granic i linii zabudowy (lica zewn. z ociepleniem; WT § 12 — z otworami ≥ 4,0 m, bez ≥ 3,0 m; płyty/okapy przyjęto ≥ 4,0 m)

| element | odległość [m] | wymóg [m] | ocena |
|---|---|---|---|
| ściana zach. P2 z oknami (lico) | 6,00 | ≥ 4,0 | ✔ |
| ściana zach. P1 z oknami (lico) | 7,00 | ≥ 4,0 | ✔ |
| ściana zach. P0 z oknami/drzwiami (lico) | 8,00 | ≥ 4,0 | ✔ |
| płyta ST2 wysunięta na zach. (krawędź) | 4,80 | ≥ 4,0 | ✔ |
| płyta dachu ST3 (krawędź) | 5,20 | ≥ 4,0 | ✔ |
| płyta ST1 wysunięta 1,50 m (krawędź) | 5,50 | ≥ 4,0 | ✔ |
| ściana wsch. garażu z drzwiami i oknem (lico) | 5,80 | ≥ 4,0 | ✔ |
| ściany wsch. P1/P2 z oknami (lico) | 13,00 | ≥ 4,0 | ✔ |
| jednostka zewn. PC | 3,40 | ≥ 3,0 | ✔ |
| elewacja płn. P0 od granicy z drogą | 8,20 | ≥ 6,0 | ✔ |
| daszek nad wejściem od granicy z drogą | 6,70 | ≥ 6,0 | ✔ |
| elewacja płd. / boks C od granicy tylnej | 29,70 | ≥ 4,0 | ✔ |
| osłona pojemników od granicy z drogą | 3,10 | ≥ 3,0 | ✔ |
| budynek względem nieprzekraczalnej linii zabudowy (y = 13,00) | elewacja 2,20 za linią, daszek 0,70 za linią | nie przekraczać | ✔ |

### 7.5 Wskaźniki MPZP 3MN, wysokość, PU

| wskaźnik | projekt | wymóg | ocena |
|---|---|---|---|
| pow. zabudowy (rzut brył zamkniętych: P0 ∪ P1 ∪ P2 ∪ boks C) | 225,6 m² = 14,1 % | ≤ 30 % (480 m²) | ✔ |
| pow. zabudowy zachowawczo (z płytami, okapami, daszkiem) | 253,8 m² = 15,9 % | ≤ 30 % | ✔ |
| pow. biologicznie czynna (bez dachów zielonych) | 1241 m² = 77,5 % (+ ok. 58 m² jako 50 % dachów zielonych — nie wliczono) | ≥ 50 % (800 m²) | ✔ |
| intensywność zabudowy (pow. całkowita kondygnacji nadz. 407,3 m² / 1600 m²) | 0,25 | 0,05–0,80 | ✔ |
| liczba kondygnacji nadziemnych | 3 | ≤ 3 | ✔ |
| **wysokość budynku** (WT § 6: od terenu przy najniżej położonym wejściu -0,31 do attyki +9,85) | **10,16 m** (od wejścia głównego: 10,08 m) | ≤ 11,0 m | ✔ |
| dach | płaski, spadek 2 % | ≤ 12° | ✔ |
| miejsca postojowe | 2 (garaż) + 2 gościnne | ≥ 2 | ✔ |
| ogrodzenie od drogi | ażurowe 1,50 m | ≤ 1,60, bez prefabrykatów betonowych | ✔ |
| PU budynku (bez garażu, bez schodów) | **235,09 m²** | 230–270 m² (brief) | ✔ |

### 7.6 Zestawienie powierzchni

| kondygnacja | PU mieszk.+pomocn.+komunik. | pom. techniczne | schody/spoczniki (poza PU) | garaż + pom. gosp. | pow. całkowita (brutto) |
|---|---|---|---|---|---|
| P0 | 94,55 | 6,11 | 10,51 | 57,20 | 202,02 |
| P1 | 64,30 | 0,00 | 10,51 | 0,00 | 102,55 |
| P2 | 63,97 | 6,16 | 2,98 | 0,00 | 102,70 |
| **razem** | **222,82** | **12,27** | **24,00** | **57,20** | **407,27** |

* **PU budynku mieszkalnego = 222,82 + 12,27 = 235,09 m²** (wartość do porównania z celem 230–270 m²;
  bez garażu z pom. gosp. i bez schodów).
* PU łącznie z garażem i pom. gosp.: 292,30 m²; powierzchnia netto wszystkich pomieszczeń (z klatką): 316,30 m².
* Boks C (siedzisko h = 0,55) nie jest wliczany do PU. Kubatura brutto (szacunek): ≈ 1 380 m³.

## 8. Samokontrola — odstępstwa, słabości, ryzyka

**Iteracje rysunków (wykonane 2 pełne przebiegi + poprawki):** 1) poprawiono kolizje skrzydeł drzwi z wyposażeniem (zasobnik CWU
w pom. techn., wanna w łaz. P1, natrysk w łaz. P2, łóżko w 2.06, półki spiżarni, drzwi garażu/samochód); 2) pion K2 przeniesiono
tak, aby przechodził przez pomieszczenia mokre/szacht na wszystkich kondygnacjach (łazienka P2 przeniesiona na wschód nad szacht
przy trzonie — rury poza strefą wspornika); 3) uporządkowano wymiary/legendy; 4) elewację porównano ze szkicem (tab. 2) — wszystkie
krawędzie w tolerancji ≤ 0,45 m.

Odstępstwa od szkicu/założeń (z uzasadnieniem):
1. Kwatery E i C równe (2,28 / 2,37 m) zamiast nierównych ze szkicu — powtarzalność stolarki i słupków SL1–SL4 w osiach podziałów.
2. Linia D i płyta E na tym samym poziomie konstrukcyjnym (+3,00); różnicę wysokości ze szkicu oddaje pas D 2,70–3,70 (attyka dachu
   garażu + dolna rama boksu C). Na wschód od x = 3,95 płyta E „wtapia się” w pas D (w szkicu dwie osobne linie).
3. Rama górna C przedłużona do 13,45 (szkic ~13,6) jako lekka stal; boks C 7,10 m szkła (szkic 7,2).
4. PU 235,09 m² — przy dolnej granicy celu (świadomie: wariant zwartości).

Słabości / do weryfikacji w dalszych etapach:
* Łazienka 1.05 i pom. techn. 2.07 dostępne bezpośrednio ze spocznika klatki (brak holu) — mniejsza prywatność łazienki dzieci.
* Łazienka 0.08 tylko z pokoju gościnnego (goście dzienni korzystają z WC 0.04); pokój gościnny 10,8 m² — kompaktowy.
* Spiżarnia 0.10 wąska (1,07 m; półki jednostronne, drzwi otwierane na zewnątrz).
* Pokój 1.02 (NW) z jednym oknem zach. i szachtem K2 w narożu.
* Hol P0 ma szer. 1,32 m, a główne przejście do strefy dziennej prowadzi przez spocznik trzonu (otwór 1,20 m).
* Podwójny schodkowy wspornik zachodni (A' → A → B, 2 × 1,00 m) wymaga tarcz ŻB w ścianach N/S P1 i P2 (koszt, ograniczenie okien
  w strefie zakotwienia, EQU, ugięcia ≤ 8 mm, łączniki termoizolacyjne) — do obliczeń w PT.
* Nadproże-tarcza 7,10 m nad boksem C lub słupki w ramie C — decyzja w PT; belka ukryta ST1 w osi 1 z siłą skupioną z tarczy wsch. P1.
* Okna P2 za lamelami — współczynnik 1/8 spełniony geometrycznie, rzeczywiste natężenie światła do sprawdzenia (symulacja DF).
* Wysokość 10,16 m — zapas 0,84 m do 11,0 m; moduły PV muszą pozostać poniżej attyki lub MPZP musi wyłączać urządzenia techniczne.
* Garaż 5,68 m w świetle — minimalnie ponad 5,60 m (przejścia boczne 0,55–0,85 m).
* Jednostka PC 3,40 m od granicy — wymagana analiza akustyczna względem sąsiada (poziom hałasu nocą).
* WT § 23 (pojemniki) i § 12 (nowelizacja 2023/2442) — do potwierdzenia po uzupełnieniu rejestru (R3).
