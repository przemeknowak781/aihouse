# Ocena koncepcji W1–W3 — sędzia J3 (wierność szkicowi · potencjał katalogowy)

Data: 2026-09-25. Podstawa: brief v2 (§1.1, §1.2, §4, §7–§9), decyzje Inwestora z 25.09.2026, rejestr wymagań
`docs/10_podstawy_prawne/00_rejestr_wymagan.md` (W-001…W-024, W-030, W-057, W-095…W-098, W-316), szkic
`00_wejscie/szkic_koncepcyjny.jpg`, interpretacja `00_wejscie/interpretacja_szkicu_v2.png`, opisy i wszystkie rysunki w `W1/`, `W2/` i `W3/`.
Interpretacji v1 (wiata, taras na D) nie stosowano. Liczby oznaczone „J3” zostały policzone samodzielnie. Skrypt:
`scratchpad/koncepcja/j3_fid.py`, skala szkicu 45,8 px/m, odniesienie = lico zachodnie bryły B.

**Status W3 (pytanie „co z agentem W3?”):** agent W3 skończył pracę (opis i rzut P0 o 02:39). Dostarczył kompletny `opis.md`,
6 rysunków (rzuty P0–P2, elewację S na tle szkicu, przekroje A-A/B-B, PZT) oraz skrypty `src/`. Uruchomiłem
`python3 src/calc_w3.py kontrola`. Skrypt odtwarza tabelę kontrolną z opisu 1:1 (40/40 pozycji). **Brakuje eksportu
`model_W3.json`**, który W1 i W2 mają. Są też 2 drobne niespójności rysunków: wysokość H = 10,13 m na przekroju wobec 10,10 m
w opisie oraz dach P1 +6,70 w PZT wobec +6,50 na rzucie P2. Wariant nadaje się do oceny.

## 1. Wynik

| wariant | ocena J3 | werdykt |
|---|---|---|
| **W3** | **78** | **baza**: najwyższy potencjał katalogowy, jedyny z rytmem kwater parteru ze szkicu. Warunek: likwidacja cofnięcia garażu o 4,80 m (błąd krytyczny w soczewce J3) |
| W1 | 73 | najwierniejsza elewacja (max odchyłka 0,43 m), ale przeciętne wnętrza, drogi podwójny wspornik i PU wg W-316 = 222,8 m² < 230 |
| W2 | 66 | racjonalny i tani, ale najmniej wierny (pasmo E o 1,21 m krótsze) i najsłabszy katalogowo (hol 4,69 m², pokój gościnny i schody przez salon) |

Wagi soczewki J3: elewacja S (warstwy A–E, proporcje, rytmy) 35 %, czytelność „S” w 3D/perspektywie 10 %, jakość architektoniczna 20 %,
atrakcyjność katalogowa (wow + funkcja + koszt) 20 %, uniwersalność 10 %, nazwa i wyróżniki 5 %.

| kryterium (waga) | W1 | W2 | W3 |
|---|---|---|---|
| elewacja S (35) | 90 | 70 | 82 |
| „S” w 3D (10) | 90 | 80 | 55 |
| jakość architektoniczna (20) | 62 | 58 | 85 |
| atrakcyjność katalogowa (20) | 58 | 66 | 80 |
| uniwersalność (10) | 60 | 64 | 64 |
| nazwa / wyróżniki (5) | 70 | 55 | 80 |
| **razem** | **73** | **66** | **78** |

## 2. Wierność szkicowi — pomiar (J3)

Krawędzie szkicu w metrach od lica zachodniego bryły B: A −0,98…12,23; płyta A −2,40…12,55; B 0…12,01; C (szkło) 4,48…11,68;
rama C górna 3,93…13,76; D 3,82…19,17; E (szkło) 0,98…13,21; płyta E −1,53…14,08; G od 13,21.
Kwatery E w szkicu: 1,75 / 1,97 / 2,62 / 2,51 / 3,38 m, czyli szerokość rośnie ku wschodowi.

| miara (J3) | W1 | W2 | W3 |
|---|---|---|---|
| maks. odchyłka krawędzi | **0,43 m** (początek D) | 1,21 m (koniec E) | 1,06 m (koniec E) |
| średnia / RMS | **0,10 / 0,17 m** | 0,39 / 0,54 m | 0,33 / 0,43 m |
| krawędzie z odchyłką > 0,5 m | **0** | 4 | 5 |
| rytm kwater E | 5 × 2,28 (równe) | 5 × 2,28 (równe) | **1,60/1,90/2,40/2,40/2,55, korelacja ze szkicem 0,91** |
| przeszklenie E | **12,20 m (lica)** | 11,40 m | 10,85 m |
| linia D jako fizyczna krawędź | **ciągła: pas ST1 2,70–3,70, y −1,30, x 3,95–18,90** | C-dół (y −1,30) → attyka G w licu (y −0,30); uskok 1,0 m | **rozerwana w głąb o ≈ 5,8 m:** C-dół y −1,30…−0,30, attyka G y ≈ 4,50 |
| G (garaż) względem lica ogrodowego | w licu | w licu | **cofnięty 4,80 m** (patio) |
| boks C | **prawdziwy wykusz**: szkło w płaszczyźnie ramy, siedzisko 0,55 m | szkło w licu ściany, rama 1,0 m | szkło w licu ściany, rama 1,0 m |
| rama C na wschód poza B | **1,75 m** (szkic 1,76) | 0,30 m | 0,60 m |

Wnioski:
* **W1** ma elewację niemal „przerysowaną” ze szkicu. Jedyne minusy: kwatery E są równe, a pas D łączy się z krawędzią płyty E
  w jeden schodkowy gzyms. W szkicu to dwie osobne linie.
* **W3** na rzucie prostokątnym jest bardzo dobry: płyta E pokrywa się ze szkicem (−1,50…14,10), C ma dokładnie 7,20 m i tylko W3
  ma narastający rytm kwater. W perspektywie wariant traci. Garaż cofnięty o 4,80 m za patio sprawia, że dolna, wschodnia „pętla”
  litery S się cofa. Linia D, według decyzji Inwestora krawędź biegnąca na wschód nad garażem do jego narożnika, jest w 3D dwiema
  krawędziami oddalonymi o ≈ 5,8 m. Płyta E urywa się nad patio na x = 13,80. Rendery katalogowe robi się zawsze z perspektywy
  od ogrodu (SE/SW), więc w soczewce J3 to błąd krytyczny do czasu poprawy. Brief pozwala na przesunięcia brył w głąb, ale ciągłości
  D to nie znosi.
* **W2** skraca pasmo E do 11,40 m, które kończy się w licu B (w szkicu E wychodzi 1,2 m poza B). Płyta E kończy się na 12,90
  (w szkicu 14,08), rama C wystaje tylko 0,30 m. Przeszklone drzwi w ścianie G osłabiają pełny blok garażu.

## 3. Ocena wariantów

### W3 — 78 pkt (BAZA)
**Mocne strony**
* Najsilniejsze wnętrza katalogowe:
  * strefa dzienna 59,31 m², najgłębsza z trzech (5,19 m wobec 4,79 w W1 i 4,59 w W2);
  * jadalnia pod pustką 5,70–5,95 m doświetlona boksem C;
  * oś widoku x = 8,00 od furtki przez wiatrołap ze świetlikiem SW2 do ogrodu;
  * klatka schodowa pod latarnią SW1, za ekranem z lamel;
  * 3 wyjścia do ogrodu, taras zachodni pod okapem 1,50 m;
  * loggia rodziców 13,0 × 1,20 m za lamelami.
* Jedyny wariant z rytmem kwater E ze szkicu. Płyta E zgodna ze szkicem na obu końcach. C ma 7,20 m w 3 kwaterach 2,40 m.
* Pełna zgodność z rejestrem w PZT (J3 sprawdził):
  * jednostka PC 13,30 m od granicy E (W-024: ≥ 6,0 m);
  * szczelny zbiornik 5 m³ + niecka (brief §8);
  * daszek 2,70 × 1,20 m (W-057), 0,20 m przed linią zabudowy;
  * ściany z oknami 6,00/7,00/6,00 m od granic, płyty 5,10 m;
  * H = 10,10 m (≤ 11,0); zabudowa 12,5 %; PBC 77,3 %.
* Okna/podłoga policzone przez J3 (w świetle ościeżnic): salon 34,9/59,31 = 1/1,7; pokój dziecka 1: 2,53/16,60 = 1/6,6;
  pokój dziecka 2: 1/5,0; pokój gościnny: 2,26/12,63 = 1/5,6; wszystkie ≥ 1/8. Pokoje dzieci 16,6 i 12,6 m²,
  sypialnia rodziców 15,24 m², pokój gościnny 12,63 m² z własną łazienką z prysznicem.
* PU wg W-316 (bez klatek 2 × 7,04 m², pom. techniczne osobno): **241,65 m²**, w środku przedziału 230–270.

**Błędy krytyczne (soczewka J3)**
1. Garaż cofnięty o 4,80 m od lica ogrodowego. Linia D rozerwana w głębi o ≈ 5,8 m, pętla G litery „S” czytelna tylko na elewacji
   prostokątnej, nie na renderach.

**Słabości (do poprawy, niedyskwalifikujące)**
* Kuchnia: zabudowa wzdłuż ściany E ma ≈ 1,8 m, bo resztę ściany zajmują drzwi na patio. Spiżarnia ma 1,49 m² (1,22 × 1,22 m).
  To za mało w domu katalogowym 260 m².
* Pralnia 1.07 dostępna tylko przez pokój rodzinny 1.02.
* Droga garaż → kuchnia ≈ 11 m prowadzi przez reprezentacyjny wiatrołap.
* Pom. techniczne 6,88 m² mieści PC, CWU 300 l, bufor 100 l, centralę wentylacyjną, RG i wodomierz „na styk”.
* Na P2 gabinet (19,43 m², naroże W+S nad wspornikiem) jest większy od sypialni rodziców (15,24 m²). Wejście do łazienki
  rodziców prowadzi przez garderobę-przejście szer. 1,45 m.
* Loggia nad pomieszczeniami ogrzewanymi. Płyta ST2L obniżona o 0,25 m daje na P1 wysokość 2,55 m, tylko 5 cm zapasu do 2,50 m.
  Warstwy loggii (+5,90 → +6,28) mają 0,38 m na izolację spadkową, hydroizolację i taras. Ryzyko wg briefu §9.
* Bryła mniej zwarta: 5 pól dachowych, skrzydło 1-kondygnacyjne. Pustka to akustyka i zapachy z kuchni.
* PU w opisie liczona z klatkami (262,61 m²), niezgodnie z W-316. Brak `model_W3.json`.

### W1 — 73 pkt
**Mocne strony:**
* Najwierniejsza elewacja (0 krawędzi z odchyłką > 0,5 m).
* Garaż i pomieszczenie gospodarcze w licu, więc D jest fizycznie ciągła do narożnika 19,20 m.
* Boks C jako prawdziwy przeszklony wykusz z siedziskiem „czytelnia”. Rama górna C przedłużona 1,75 m na wschód jak w szkicu.
* Zwarta bryła (parter to prostokąt 18,20 × 11,10 m).
* Pomieszczenie gospodarcze na rowery i sprzęt ogrodowy 20,37 m², mocny argument sprzedażowy.
* Sypialnia rodziców 18,17 m² w narożu S+W nad wspornikiem.
* Trzon schodowy dostępny z holu.

**Błędy krytyczne:**
1. Jednostka zewnętrzna PC 3,40 m od granicy E. Rejestr W-024 wymaga ≥ 6,0 m od granicy E (i nie pod oknami sypialni).
2. PU wg W-316 = 94,55 + 64,30 + 63,97 = **222,82 m²** (pom. techniczne 12,27 m² osobno). Program wymaga ok. 230–270 m²,
   więc wariant ma za mały program o ≈ 7 m².

**Słabości:**
* Retencja 6 m³ + skrzynki ≈ 5 m³ niezgodna z briefem §8 (≤ 5 m³ szczelny + niecka).
* Podwójny, schodkowy wspornik na zachód (A' nad A nad B, 2 × 1,00 m). Wymaga żelbetowych ścian-tarcz w „U” zachodnim P1 i P2
  oraz tarczy P2 nad otworem boksu C 7,10 m. To najdroższy układ, co w katalogu jest minusem.
* Strefa dzienna ma tylko 4,79 m głębokości i nie ma pustki. Hol 1,32 m szerokości. Wejście do strefy dziennej przez spocznik trzonu.
* Pokoje dzieci 12,04 i 12,28 m², na granicy minimum.
* Łazienka P1 i pom. techniczne P2 otwierane wprost ze spocznika.
* Kwatery E równe.
* Bryła P2 13,00 × 7,90 m jest większa od P1 i wygląda ciężko.

### W2 — 66 pkt
**Mocne strony:**
* Najprostsza i najtańsza konstrukcja: pojedynczy wspornik A na tarczach, lekka ściana A'.
* Łazienki P0–P2 w jednym pionie.
* Najkrótsza droga garaż → przedsionek → kuchnia (≈ 6 m). Wejście tuż obok bramy.
* Garaż w licu, więc D w 3D prawie ciągła (uskok 1,0 m).
* PU wg W-316 ≈ 233,8 m².

**Błędy krytyczne:**
1. Jednostka PC 3,80 m od granicy E. W-024 wymaga ≥ 6,0 m.
2. Zbiornik 6 m³ i skrzynki rozsączające w ogródku frontowym (brief §8: ≤ 5 m³ + niecka; skrzynki dopiero po stanowisku PGW WP).

**Słabości (soczewka J3):**
* Najmniej wierny: pasmo E o 1,21 m krótsze i kończące się w licu B, płyta E o 1,18 m krótsza, rama C o 0,86 m krótsza.
  Kwatery równe. Przeszklone drzwi w ścianie G.
* Wiatrołap 3,96 m² i hol 4,69 m² w domu 257 m². Pokój gościnny (przez przedpokój z salonu) i schody dostępne przez strefę dzienną.
* Na P2 pom. techniczne 5,40 m² i garderoba 10,56 m² zajmują najcenniejszą, południową elewację za lamelami.
* Strefa dzienna ma tylko 4,59 m głębokości, najpłycej z trzech. Pokój rodzinny 31,9 m² jest przewymiarowany.

## 4. Uniwersalność (wszystkie warianty)
* Minimalna szerokość działki (J3): ściany z oknami ≥ 4,0 m, płyty-okapy ≥ 1,5 m (WT §12 ust. 6):
  * W1: 28,2 m;
  * W2 i W3: 28,0 m;
  * przy „bezpiecznych” 4,0 m także dla płyt: 29,4 / 29,1 / 28,9 m;
  * ze ścianą wschodnią garażu bez otworów: 27,0 m (W2/W3).
* Dom katalogowy wymaga więc działki ≥ 27–29 m szerokości z wjazdem od północy (N ± 45°).
* Zalecane odmiany katalogowe: lustro (garaż od zachodu) oraz ściana wschodnia garażu bez otworów (drzwi boczne przenieść na pn.).
* Głębokość działki: ≥ 6,0 (linia zabudowy) + ≈ 13 (budynek z daszkiem) + ≥ 12 (ogród) ≈ 31 m.

## 5. Nazwa i wyróżniki (dla bazy W3)
Proponowana nazwa katalogowa: **„LAMELA Prześwit”**. Wyróżniki do karty katalogowej:
1. fasada „S” z trzech przesuniętych brył;
2. prześwit od furtki przez dom do ogrodu;
3. jadalnia 5,9 m pod szklanym boksem;
4. schody pod latarnią;
5. loggia rodziców za lamelami;
6. zielone dachy + PV + pompa ciepła (all-electric);
7. garaż na 2 auta + pomieszczenie ogrodowe (po poprawce).

Nazwy robocze: W1 „LAMELA Wykusz”, W2 „LAMELA Optima”.

## 6. Przeszczepy (do bazy W3)
1. **Z W1: blok G w licu ogrodowym z pomieszczeniem gospodarczym od południa.** Bryła G x 12,30–18,70, y −0,30…11,60
   (6,40 × 11,90 m). Garaż zostaje (6,08 × 6,29 m w świetle, brama od pn.). Nowy pas pd. G ma w świetle ≈ 5,88 × 4,59 m.
   Jego ściana pd. jest pełna, jak blok G w szkicu. Linia D staje się jedną ciągłą krawędzią płyty (y −1,30, +3,45/+3,65)
   od x 3,60 do narożnika x 18,70 (19,0 m od lica zach. B). Pion D = narożnik G do terenu.
2. **Z W2: przedsionek gospodarczy ze spiżarnią między garażem a kuchnią.** Pas pd. G, x 12,42–14,60:
   * drzwi do kuchni w osi E, y 2,40–3,30;
   * drzwi do garażu w ścianie y 4,80, x 13,00–13,90, szczelne z samozamykaczem;
   * droga auto → kuchnia ≤ 7 m, ruch garażowy poza wiatrołapem.

   Reszta pasa (x 14,75–18,30, ≈ 16 m²) to rowery/ogród z drzwiami zewn. 1,00 × 2,10 w ścianie wsch. (6,00 m od granicy E).
3. **Z W1: rama górna boksu C przedłużona na wschód do x = 13,45** (1,15 m poza lico B; szkic 13,76 od lica B). Lekki kształtownik
   stalowy w okładzinie ≤ 0,5 kN/m na łącznikach termoizolacyjnych.
4. **Z W1: gzyms D jako pogrubiony pas krawędziowy** (wys. ≈ 0,50–0,60 m, np. +3,15…+3,65) nad garażem i pasem gospodarczym.
   Linia D ma pozostać czytelnie wyżej niż płyta E (+2,75/+3,05), jak w szkicu.
5. **Z W2 (opcjonalnie, jeśli detal loggii z poprawki 5 się nie zamknie): ściany P2 w płaszczyźnie lamel** (lico y −0,30, lamele
   15 cm przed licem). Bez obniżonej płyty ST2L, P1 wraca do 2,80 m, znika taras nad ogrzewanym.

## 7. Poprawki obowiązkowe (baza W3)
1. **Garaż w licu (błąd krytyczny):** zlikwidować cofnięcie 4,80 m i patio poranne, wykonać przeszczepy 1–2.
   * Usunąć drzwi kuchni na patio (O0-04) i okap E nad patio poza x 12,30.
   * Płyta E może wejść 1,50 m na lico G (do x 13,80) pod linią D, jak w szkicu.
   * Kontrola: zabudowa ≈ 231 m² (14,4 % ≤ 30 %), PBC ≥ 76 %, rozpiętość dachu G 6,40 m (≤ 6,5).
2. **Kuchnia:** ciągła zabudowa wzdłuż osi E, y 0,30…4,00 (≥ 3,6 m), plus wyspa. Spiżarnia ≥ 3,0 m² w pasie G z drzwiami
   z kuchni. Narożną spiżarnię 0.02 (1,49 m²) zlikwidować, a jej powierzchnię oddać strefie dziennej (0.01 ≈ 60,8 m²).
3. **Pom. techniczne ≥ 8,5 m²:** włączyć dotychczasowy przedsionek 0.08 (4,69 m²) do 0.06, razem ≈ 11,5 m² z wejściem
   z wiatrołapu (O0-17). Garaż obsługuje nowy przedsionek z przeszczepu 2. Wtedy centrala wentylacyjna, PC, CWU 300 l, bufor,
   RG i wodomierz mieszczą się z polami obsługi.
4. **Pralnia P1:** dojście z galerii, nie przez pokój rodzinny. Przedłużyć galerię 1.01 wzdłuż osi 3 do x = 10,90 jako korytarz
   szer. 1,10 m z przegrodą regałową lub szklaną. Drzwi O1-11 (x 10,00–10,80) zostają. Pokój rodzinny 1.02 ≈ 15,4 m².
5. **Loggia / ST2L — przekrój warstwowy i dowody:**
   * h P1 pod loggią ≥ 2,50 m w wykończeniu;
   * warstwy +5,90 → +6,28: PIR spadkowy (U ≤ 0,15), spadek ≥ 2 %, membrana z wywinięciami ≥ 0,15 m, odwodnienie liniowe
     przy progach HS (próg ≤ 0,02 m, W-055), rzygacz awaryjny (brief §9.3);
   * łączniki termoizolacyjne na całych 13,0 m w osi 1 z ψ z symulacji 2D (brief §9.2);
   * balustrada z lamel ≥ 0,90 m (W-095), mocowana do słupów SLA.

   Jeśli się nie zamknie, zastosować przeszczep 5.
6. **PU wg W-316:** bez klatek 0.04 i 1.05 (2 × 7,04 m²), z pom. technicznym i garażem wykazanymi osobno. Obecnie PU = 241,65 m².
   Po poprawkach 1–4 trzymać 235–255 m². Te same zasady stosować w tabelach i na rysunkach.
7. **Model:** wyeksportować `model_W3.json` w schemacie W1/W2 (brief §7, jedno źródło prawdy). Usunąć niespójności
   (H 10,13 wobec 10,10; dach P1 +6,70 wobec +6,50). Wygenerować elewację S ponownie z D ciągłą i G w licu, na tle szkicu.
8. **Uzupełnić elewację północną (uliczną)** i jedną perspektywę od ogrodu z SE. Katalog sprzedaje się widokiem od ulicy
   i renderem, a żaden wariant ich nie ma.

## 8. Zalecenia (nieobowiązkowe)
* Hierarchia P2: sypialnia rodziców ≥ 17 m² (dziś 15,24 m² przy gabinecie 19,43 m²). Np. przesunąć ściankę S2-13 z x 8,00 na x 7,60
  i zastąpić garderobę-przejście szafami, albo zamienić funkcje gabinetu i sypialni, zachowując ciągłość apartamentu.
* Łazienka na P2 dostępna z holu (dziś jedyna łazienka P2 jest w apartamencie, a gabinet może być sypialnią 5. osoby).
* Rozważyć wykusz C z W1 (szkło w płaszczyźnie ramy, siedzisko h 0,55 m, dolna część stała VSG do 0,85 m, W-097) w części
  przed pokojem rodzinnym x 8,40–11,70. To mocny wyróżnik „czytelnia”, ale wymaga spójnego rozwiązania przed pustką.
