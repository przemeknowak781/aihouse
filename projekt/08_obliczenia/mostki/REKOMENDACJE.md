# REKOMENDACJE — mostki cieplne, ciągłość 4 linii, odprowadzenie wody (Dom LAMELA)

Rekomendacje zmian projektu wynikające z katalogu mostków (symulacja 2D PN-EN ISO 10211) i kontroli detali. **Modelu nie zmieniano** — zmiany do wprowadzenia w parametrach `tools/buduj_model.py` przez zespół modelu. Warianty policzono tym samym solverem (`tools/mostki_budynku.py`, funkcja `warianty`).

**f_Rsi:** wszystkie węzły spełniają f_Rsi ≥ 0,72 (WT zał. 2 pkt 2.2.1 / PN-EN ISO 13788) — minimum 0,760 w węźle WZ-09a.

## A. Węzły z ψ wyraźnie gorszym od wytycznych albo z przerwaną linią izolacji

Kryterium: ψ_oi > dobra praktyka + 0,03 W/(m·K) [ZAŁ] albo ocena „ZŁY” (izolacja przerwana konstrukcją). Dobra praktyka / wartość domyślna — `fizyka.mostki.PSI_DOMYSLNE` [NZW].

| węzeł | ψ_oi | dobra pr. | ocena | wariant policzony | ψ_oi wariantu | f_Rsi wariantu |
|---|---|---|---|---|---|---|
| WZ-04 | +0,220 | 0,15 | DO POPRAWY | łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09) | +0,128 | 0,929 |
| WZ-05 | +0,226 | 0,15 | DO POPRAWY | łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09) | +0,134 | 0,927 |
| WZ-06 | +0,385 | 0,20 | DO POPRAWY | łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09) | +0,305 | 0,853 |
|  |  |  |  | łącznik 120 mm + blok termoizolacyjny nośny 15 cm u podstawy attyki | +0,203 | 0,890 |
| WZ-07a | +0,182 | 0,15 | DO POPRAWY | łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09) | +0,152 | 0,851 |
| WZ-09a | +0,616 | 0,10 | ZŁY | XPS 10 cm na płycie pod posadzką garażu | +0,344 | 0,852 |
|  |  |  |  | XPS 10 cm pod posadzką garażu + blok z betonu komórkowego 400 (24 cm) u podstawy ściany | +0,299 | 0,911 |
| WZ-09b | +0,071 | 0,10 | ZŁY | — (patrz opis) | — | — |
| WZ-09c | +0,081 | 0,10 | ZŁY | — (patrz opis) | — | — |
| WZ-16a | +0,236 | 0,15 | DO POPRAWY | łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09) | +0,194 | 0,854 |

* **WZ-04, WZ-05** — Płyta wspornikowa: łącznik termoizolacyjny z modułem izolacyjnym **120 mm** (w warstwie ocieplenia 20 cm) i λ_eq ≤ 0,08 W/(m·K) wg ETA (zamiast przykładowego 80 mm / 0,09) — ψ spada do poziomu dobrej praktyki; łącznik w strefie izolacji, płyta stropu do lica konstrukcji (audyt A2 K-1).
* **WZ-06** — Attyka z okapem PL-3: łącznik 120 mm **oraz** nośny blok termoizolacyjny u podstawy attyki (element attykowy z ETA / szkło piankowe klasy nośności wg PT-K, h ≈ 15 cm) — ψ ≈ dobra praktyka (wariant policzony); alternatywa: attyka lekka (rama drewniana/stalowa z przekładką) na płycie ocieplonej z góry.
* **WZ-07a, WZ-16a** — Krawędź stropu nad powietrzem z płytą PL-2: jak wyżej — łącznik 120 mm; belki odwrócone B3/B4/B5 w linii ściany obłożyć ociepleniem ściany na całą wysokość (wełna elewacji A ciągła do podsufitki); podsufitka jedna płaszczyzna pod wspornikiem A i pasem zach. PL-2 (audyt A2 I-5) — ψ < dobra praktyka możliwe dopiero przy łączniku 120 mm.
* **WZ-09a, WZ-09b, WZ-09c** — Połączenie z garażem na ciągłej płycie: płyta fundamentowa jest ciągła pod ścianą SWG (XPS tylko pod płytą) — ciepło z domu przepływa płytą do posadzki garażu (ψ_iu duże). Zalecane: **XPS ≥ 10 cm na płycie pod posadzką garażu** (cała posadzka albo pas ≥ 1,5–2,0 m przy SWG; jastrych garażu zbrojony, z dylatacją obwodową) + blok termoizolacyjny w 1. warstwie muru SWG (nośność — PT-K). Pod stropem (WZ-09b/c) pas docieplenia SUF-G 1,0 m ogranicza mostek (f_Rsi spełnione); ocena „ZŁY” wynika z testu ołówka (płyta ŻB dochodzi do przestrzeni nieogrzewanej) — akceptowalne przy ψ_ie ≤ 0,10; alternatywa: docieplenie całego spodu stropu garażu przy ścianach E i 2 pasem 1,5 m.

## B. Woda, hydroizolacja, detale (weryfikacja koncepcji / audyt A2 — uwzględnione w detalach PT-AR-D)

### R-W1. Odwodnienie płyt wysuniętych (okapy, daszek)

Płyty mają w modelu spadek 2 % od budynku i okapnik, bez odbioru wody — linia kapania wypada nad tarasem, podestem wejścia i podestem drzwi gospodarczych (ryzyko oblodzenia, zachlapania przeszkleń HS i cokołu). Zalecenie: **spadek ≥ 2 % od budynku do czoła, rynna ukryta za blendą czołową** (korytko ze stali nierdzewnej / blachy powlekanej 0,7 mm, spadek 0,5 % do wylotu), wyloty do rur spustowych przy narożach i słupach, rury do kanalizacji deszczowej KD → zbiornik retencyjny; kapinos (okapnik ≥ 3 cm) na obróbce blendy i na podsufitce. Uzasadnienie: linia kapania przy wejściu i nad tarasem użytkowym jest niedopuszczalna funkcjonalnie (brief §9.3), a odwodnienie liniowe pod linią kapania na tarasie z deski na wspornikach wymagałoby przerwania nawierzchni i nie chroni podestu T2 przed oblodzeniem; rynna ukryta nie narusza łącznika termoizolacyjnego (mocowana do czoła płyty za blendą, poza strefą izolacji).

| płyta | pow. [m²] | Q = r·A·C [l/s] (r = 0,030 l/(s·m²), C = 1,0) | pod linią kapania | zalecenie |
|---|---|---|---|---|
| PL-E | 23,7 | 0,71 | T1, T3 | rynna ukryta za blendą, spadek 2 % do czoła, RS DN70–DN90 do KD |
| PL-DA | 3,0 | 0,09 | T2 | rynna ukryta za blendą, spadek 2 % do czoła, RS DN70–DN90 do KD |
| PL-2 | 23,0 | 0,69 | T1, T3 | rynna ukryta za blendą, spadek 2 % do czoła, RS DN70–DN90 do KD |
| PL-3 | 23,0 | 0,69 | T1, T3 | rynna ukryta za blendą, spadek 2 % do czoła, RS DN70–DN90 do KD |

Obciążenie normowe deszczem r = 300 l/(s·ha) = 0,030 l/(s·m²) [ZAŁ — przyjęcie typowe w PL; wymiarowanie wg PN-EN 12056-3 w PT instalacji]; rynna 100 mm przy spadku 0,5 % odbiera ≥ 1 l/s — z zapasem.

### R-W2. Rzędne przelewów awaryjnych

Kryteria: dno przelewu ≥ pokrycie przy wpuście + 0,03 m (W-142; J2 poprawka 5.1: 30–50 mm) i nie niżej niż pokrycie w miejscu przelewu; górna krawędź otworu ≤ wierzch wywinięć (pokrycie + 0,15 m, DAFA) i poniżej korony attyki. Pokrycie = wierzch hydroizolacji; grubość izolacji spadkowej d = d_min + spadek × odległość od wpustu (powierzchnia stożkowa wokół wpustu) [INT].

| dach | przelew | dno model | pokrycie przy wpuście | pokrycie w miejscu przelewu | zakres dna | ocena | zalecane dno |
|---|---|---|---|---|---|---|---|
| D1 | przelew PA1 — attyka pn. nadbudowy (na d | 9,480 | 9,426 | 9,441 | 9,456…9,476 | ✗ | **9,476** |
| D1 | przelew PA2 — na dach D2 (pole zach., z  | 9,520 | 9,426 | 9,498 | 9,498…9,498 | ✗ | **9,498** |
| D1 | przelew PA3 — na dach D3 (pole wsch., z  | 9,520 | 9,426 | 9,527 | 9,527…9,527 | ✗ | **9,527** |
| D2 | przelew PA4 — attyka zach. | 6,460 | 6,296 | 6,325 | 6,326…6,346 | ✗ | **6,346** |
| D3 | przelew PA5 — attyka wsch. (awaryjnie na | 6,460 | 6,296 | 6,360 | 6,360…6,360 | ✗ | **6,360** |
| D4 | przelew PA6 — attyka wsch. (garaż) | 3,360 | 3,134 | 3,185 | 3,185…3,185 | ✗ | **3,185** |
| D4 | przelew PA7 — attyka wsch. (pas gosp.; > | 3,360 | 3,134 | 3,176 | 3,176…3,183 | ✗ | **3,183** |

Wniosek: rzędne przelewów w modelu odnoszą się do pokrycia **średniego** (grubość średnia izolacji spadkowej), a nie do pokrycia przy wpuście — przy izolacji spadkowej przelewy D2/D3/D4 leżą 0,13–0,23 m nad pokryciem przy wpuście (spiętrzenie wody ponad dopuszczalne), a przy odniesieniu do pokrycia średniego — D1 poniżej pokrycia (uwaga weryfikacji A3). Zalecenie: w modelu podać rzędne pokrycia przy wpustach (pole `rzedna_pokrycia`), dno przelewu = pokrycie przy wpuście + 0,03…0,05 m; przelewy, dla których pokrycie lokalne jest wyższe niż ten zakres (PA2, PA3, PA5, PA6), przenieść na odcinki attyki bliżej wpustów (najniższa strefa pola) albo wykonać w attyce kosz/obniżenie izolacji spadkowej do rzędnej dna.

### R-W3. Wysokość wywinięć hydroizolacji na attykach (≥ 15 cm ponad warstwę wierzchnią)

| dach | korona attyki | max wierzch warstw dachu przy attyce | wywinięcie min. | ocena |
|---|---|---|---|---|
| D1 | 9,776 | 9,599 | 0,18 m | ✓ |
| D2 | 6,660 | 6,439 | 0,22 m | ✓ |
| D3 | 6,660 | 6,435 | 0,22 m | ✓ |
| D4 | 3,850 | 3,365 | 0,49 m | ✓ |

Źródło wymagania: Stowarzyszenie DAFA, „Wytyczne do projektowania i wykonywania dachów z izolacją wodochronną — wytyczne dachów płaskich” (wywinięcie ≥ 15 cm ponad najwyższą warstwę wykończeniową — żwir, substrat; 12/10 cm dla dachów o większym spadku); zgodnie z DIN 18531 / ZVDH Flachdachrichtlinie (przywoływane pomocniczo). PN-EN 1991 (oddziaływania na konstrukcje) wysokości wywinięć **nie** określa. Na D1 w najwyższych narożach pól wywinięcie wynosi dokładnie 15 cm — bez zapasu na tolerancję wykonania izolacji spadkowej: zalecane podniesienie korony attyki D1 o 5 cm albo obniżenie d_max klinów przy attyce.

### R-W4. Cokół przy drzwiach DZ2 garażu

Weryfikacja koncepcji (§6 A5): cokół 0,14 m przy DZ2 (strona wsch., teren wyższy) < 0,30 m, brak odwodnienia liniowego. Zalecenie (detal PT-AR-D): odwodnienie liniowe przed progiem DZ2 na całą szerokość drzwi + 0,15 m z każdej strony, podłączone do KD-E; nawierzchnia ze spadkiem 2 % od drzwi; uszczelnienie progu taśmą EPDM / masą KMB wywiniętą ≥ 15 cm na ościeża poza strefę rozbryzgu i połączoną z izolacją przeciwwilgociową płyty; lokalne obniżenie terenu przy DZ2 (niecka NT-E) tak, by cokół poza drzwiami ≥ 0,30 m (DIN 18533-1: uszczelnienie cokołu ok. 30 cm, min. 15 cm nad terenem w stanie końcowym).

### R-W5. Podsufitka i czoło wspornika bryły A

Audyt A2 poz. I-5 / weryfikacja B8: docieplenie spodu ST2Z odkryte, uskok względem spodu PL-2. Zalecenie (detal PT-AR-D): jedna płaska podsufitka włóknocementowa pod wspornikiem A i pasem zach. PL-2 na rzędnej spodu SUF-ZEW (spód ST2Z − 0,252 m), czoło PL-2 obudowane blendą do tej rzędnej, wełna 20 cm ciągła od ściany P1 (ETICS) do czoła, szczelina wentylowana 4 cm z kratką przeciw owadom na obwodzie.

### R-W6. Konwencja obrysów płyt (audyt A2 K-1)

Stropy i dachy przyciąć do lica warstwy konstrukcyjnej (±0,09 m od osi ścian zewn.), wierzchy płyt wspornikowych zrównać ze stropem, łącznik termoizolacyjny w strefie izolacji, attyka 0,18 m w osi muru. Obliczenia mostków i detale PT-AR-D wykonano wg tej docelowej konwencji.

## C. Drenaż opaskowy

Decyzja w modelu działki: `DR-0` — NIE PROJEKTUJE SIĘ — piaski przepuszczalne, ZWG ≈ 3,8 m p.p.t., posadowienie ≈ 0,5 m p.p.t. (W-285); ochrona płyty: XPS + membrana SBS, opaska żwirowa i spadki terenu (`dzialka.odwodnienia`; fundamenty: „posadowienie bezpośrednie na piaskach średnich (I_D ≈ 0,6), niewysadzinowych; ZWG ≈ 3,8 m p.p.t. — drenaż opaskowy zbędny (W-285); zdjęcie humusu 0,4 m, podsypk…”). **Detalu drenażu nie opracowano** — detal cokołu PT-AR-D pokazuje opaskę żwirową, spadek terenu i uszczelnienie strefy cokołu.

Uzasadnienie geotechniczne (potwierdzenie decyzji): grunt: piasek średni (MSa), średniozagęszczony (niespoisty, przepuszczalny — typowo k ≈ 10⁻⁵…10⁻⁴ m/s [NZW]); ZWG −3,8 m p.p.t.; najniższe posadowienie −0,85 m (względem ±0,00, teren ≈ −0,25…−0,30) → odległość zwierciadła od spodu fundamentu ≈ 3,2 m, znacznie powyżej podciągania kapilarnego piasków średnich (rzędu 0,1–0,3 m [NZW]). Obciążenie wodą: wilgoć gruntowa i woda infiltrująca, niespiętrzająca się → wystarcza izolacja przeciwwilgociowa (membrana SBS na płycie, XPS pod płytą, uszczelnienie cokołu), drenaż opaskowy nie jest wymagany (brief §9.6). Warunki utrzymania decyzji (do potwierdzenia w opinii geotechnicznej i projekcie geotechnicznym, W-280…W-282): (1) brak przewarstwień gruntów spoistych do ok. 2 m pod poziomem posadowienia (ryzyko wody zawieszonej), (2) maksymalny stan ZWG (wahania sezonowe) ≥ 1,0 m poniżej spodu XPS, (3) spadki terenu ≥ 2 % na 1,5–2 m od budynku — w obecnym modelu działki 0,2–1,1 % przy licach (weryfikacja §6 A2: dodać punkty projektowane przy cokole), (4) opaska żwirowa 16/32 na geowłókninie i odwodnienia liniowe przy HS, wejściu, bramie i DZ2. Jeżeli badania wykażą gliny/pyły lub wodę zawieszoną — drenaż opaskowy DN100 w obsypce filtracyjnej na poziomie spodu XPS, ze studzienkami kontrolnymi w narożach, odprowadzony do niecki chłonnej (nie do zbiornika wody deszczowej bez zabezpieczenia przed cofką).

## D. Model — spójność sekcji `wezly`

1. Pole `dlugosc` sekcji `wezly` liczy część odcinków podwójnie (WZ-01↔WZ-06, WZ-05↔WZ-07↔WZ-16, WZ-08↔WZ-11T, WZ-10 — połączenia dach–ściana ×2, WZ-12 — naroża garażu). Zalecenie: długości z `zestawienie_HTB.md` §2 (geometria, każdy odcinek raz) albo generować je w `buduj_model.py` tą samą metodą (`mostki2d.zestawienie.dlugosci_geometryczne`).
2. Dodać do sekcji `wezly` węzły wykryte w geometrii: **WZ-X1** (dachy D2/D3 – ściany P2) i **WZ-X2** (dach D4 nad pasem gospodarczym – ściana P1), typ „dach_sciana” (dziś wliczone do WZ-10 jako strop pośredni, co zaniża ψ).
3. Rozdzielić WZ-07 na krawędź A′ (ściana lekka na belce B3 z okapem PL-2) i krawędź nad ścianą osi A, a WZ-09 na: ścianę SWG na płycie fundamentowej, SWG pod dachem zielonym (oś 2) i SWG pod stropem ze ścianą P1 (oś E) — geometrie różne, ψ różne o rząd wielkości (katalog: podwęzły a/b/c).
4. Materiał WELNA_FAS ma w nazwie „elewacja wentylowana” — solver mostków traktował go jako pustkę wentylowaną (poprawione w `mostki2d.geometria.material_z_modelu`: tylko materiały-powietrze).

## E. Dane do potwierdzenia przed wydaniem PT

* Łączniki termoizolacyjne płyt (PL-E, PL-DA, PL-2, PL-3): ETA wybranego wyrobu — λ_eq, grubość modułu (zalecane 120 mm), ψ i f_Rsi producenta; wartości w obliczeniach są DANYMI PRZYKŁADOWYMI.
* Konsole lamel i ramy C (χ): deklaracja producenta lub obliczenie 3D; profile progowe HS (λ podwaliny).
* Klasa wilgotności pomieszczeń (Glaser — przyjęto klasę 3, PN-EN ISO 13788 zał. A).
