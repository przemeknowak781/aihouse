# Ocena koncepcji W1–W3 — sędzia J2 (konstruktor · kosztorysant · fizyk budowli)

Data: 2026-09-25. Podstawa: brief v2 (§1.2, §4, §8, §9), rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`
(W-004, W-006, W-024, W-112, W-145, W-243…W-248, W-262…W-270, D-03, D-17), opisy `opis.md` oraz wszystkie rysunki
w `W1/`, `W2/`, `W3/`. Liczby oznaczone „J2” zostały policzone samodzielnie przez sędziego. Są to szacunki koncepcyjne ±10 %.

**Status W3 (pytanie Inwestora „co z agentem W3?”):** agent W3 skończył pracę ok. 02:39 UTC. Dostarczył `opis.md`, 6 rysunków
i komplet skryptów `src/`. Skrypt `python3 src/calc_w3.py kontrola` działa i odtwarza tabelę kontrolną z opisu (sprawdzone).
**Brakuje eksportu `model_W3.json`**, który W1 i W2 mają. Trzeba go uzupełnić przed syntezą. Streszczenie W3 w zadaniu mówi
o „wiernej sylwecie”, ale przeszklenie E ma tylko 10,85 m wobec 12,2 m w szkicu, a garaż jest cofnięty o 4,80 m.

## 1. Wyniki

| wariant | ocena J2 | werdykt |
|---|---|---|
| **W2** | **76** | **baza** — najtańsza i najprostsza konstrukcja, najkrótsze instalacje; 1 błąd krytyczny (odwodnienie dachu P2), łatwy do usunięcia |
| W1 | 66 | poprawny i zwarty, ale drogi: ok. 290 m² ścian ŻB i słaby punkt w belce ukrytej osi 1 |
| W3 | 57 | najlepsza przestrzeń i najsłabsza fizyka budowli: loggia nad pomieszczeniami ogrzewanymi, 6 pól dachowych, o ok. 1/3 więcej szkła, przeciążony filar P0 |

## 2. Porównanie ilościowe (J2)

| parametr | W1 | W2 | W3 |
|---|---|---|---|
| PU wg opisu | 235,09 (bez klatek) | 257,40 (z klatkami) | 262,61 (z klatkami) |
| **PU ujednolicona (bez klatek schodowych)** | **235,1** | **≈ 245,8** | **≈ 248,5** |
| kubatura ogrzewana brutto (J2) | ≈ 1 090 m³ | ≈ 1 080 m³ | ≈ 1 140 m³ |
| pow. przegród zewn. części ogrzewanej A (J2) | ≈ 725 m² | ≈ 740 m² | ≈ 745 m² |
| A/V_e (J2) | ≈ 0,67 | ≈ 0,68 | ≈ 0,66 |
| przeszklenia (otwory w świetle muru, bez bramy i drzwi pełnych; J2) | ≈ 90 m² | ≈ 88 m² | **≈ 120 m²** |
| w tym od północy (J2) | ≈ 3,6 m² | ≈ 4,5 m² | **≈ 11,9 m²** |
| przeszklenia / PU | 0,35 | 0,34 | **0,46** |
| pola dachowe (odwodnienie) | 2 (+ daszek boksu C) | 4 | **6** (w tym taras-loggia nad P1) |
| ściany żelbetowe (J2) | **≈ 290 m²** (trzon 3 kond., tarcze P1/P2, oś B, oś E, ściana pd. P2) | ≈ 18 m² + belki B1–B5 | ≈ 8 m² + 9 podciągów (PD-1…PD-7, PD-C, PD-4, belka-próg) |
| łączniki termoizolacyjne liniowe (J2) | ≈ 65 m | ≈ 88 m | ≈ 75 m + stopień ST2L/ST2 13 m + 5 słupów SLA w tarasie |
| rozpiętości stropów | ≤ 4,8 m; garaż 6,0 × 6,5 dwukierunkowo, 22 cm | 4,8 / 3,6 m; **garaż 6,40 m jednokierunkowo, 24 cm** | 5,40 / 3,50 m; **garaż 6,40 m jednokierunkowo, 24 cm**; ST3 5,40 + wspornik 1,20 m |
| wspornik zachodni | 1,0 + 1,0 m schodkowo (tarcze ŻB P1 i P2) | 1,0 m (2 tarcze ŻB P2 + lekka ściana A' na B3) | 1,0 m (PD-6, PD-7 + tarcza osi 3; ściany lekkie) |
| piony mokre | K1, K2, W1 (K2 w narożu pokoju dziecka) | **1 szacht SI dla 3 łazienek w stosie + K2** | SI (łazienki P1/P2 w stosie) + K2; łazienki P0 osobno w skrzydle |
| pom. techn. P0 | 6,11 m² (reku na P2) | 6,56 m² (reku na P2), **wejście tylko przez garaż** | 6,88 m² z PC + CWU 300 l + bufor 100 l + centralą — **przepełnione** |
| trasa garaż → kuchnia | ≈ 12 m (przez spocznik klatki) | **≈ 6 m** | ≈ 11 m (przez wiatrołap wejścia gł.) |
| jednostka zewn. PC od granicy E | 3,40 m ✗ (W-024: 6,0 m) | 3,80 m ✗ | **13,30 m ✓** |
| wody opadowe (W-145: zbiornik ≤ 5 m³ + niecka) | 6 m³ + skrzynki ✗ | 6 m³ + skrzynki w ogródku frontowym ✗ | **5 m³ + niecka 24 m² ✓** (1,8 m od granicy W < 2,0) |
| garaż w świetle (W-112: zalecane ≥ 5,90) | 5,68 × 6,49 (na styk) | 6,08 × 6,08 | 6,08 × 6,29 |
| koszt SSZ + instalacje, względnie (J2) | 100 % + 4–7 % (ok. +100…130 tys. zł za ŻB) | **100 %** | 100 % + 8–12 % (loggia, latarnia, pustka, podciągi, 6 dachów) |
| EP (J2, dane producenta PC, bez PV) | ≈ 56–60 | ≈ 55–59 | ≈ 60–66 (najmniejszy zapas do 70) |

Szacunek EP: metodologia z rejestru (w_el = 2,5; Q_W,nd ≈ 24 kWh/(m²·rok)), SCOP ≈ 4. Dodatkowe ≈ 30 m² szkła w W3 daje
ok. +20…27 W/K H_T (ok. +12 %). Wszystkie trzy warianty mogą spełnić EP ≤ 70 przy deklarowanych danych urządzeń i autokonsumpcji PV.
W3 ma najmniejszy zapas i największe ryzyko przegrzewania: HS zachodnie 3,20 × 2,75 m, latarnia pozioma 5,4 m², pustka z efektem kominowym.

## 3. Oceny szczegółowe

### W2 — 76 pkt (wariant bazowy)
**Mocne strony**
* Ściany murowane stoją w pionie. Stropy jednokierunkowe mają 4,80/3,60 m przy 20 cm. Elementy transferowe są tylko krótkie
  i powtarzalne: B1 25 × 105 (belka odwrócona schowana w parapecie C), B2, B3 i 2 tarcze ŻB wspornika A. Ciężkich ścian na
  wspornikach nie ma, ściana A' jest lekka. To najtańsza i najpewniejsza ścieżka obciążeń.
* Łazienki P0, P1 i P2 stoją w jednym stosie przy jednym szachcie SI. Podejścia mają ≤ 1,5 m. Centrala rekuperacji jest na P2
  z czerpnią i wyrzutnią przez dach. Pom. techn. leży przy garażu i PC, więc przewody chłodnicze mają ok. 2 m.
* Logistyka garaż → przedsionek → kuchnia ma ok. 6 m. Wejście jest przy bramie. Garaż 6,08 × 6,08 m.
* Szkła jest najmniej (≈ 88 m²), a od północy tylko ≈ 4,5 m². Strefa dzienna jest płytka (4,59 m), więc okap 1,00 m działa w pełni.

**Błąd krytyczny (dyskwalifikujący do czasu poprawy)**
* **Stropodach P2 odwadniają rzygacze na dach P1.** To sprzeczne z nadrzędnym wymaganiem Inwestora (brief §9 p. 3): każde pole
  ma mieć wpusty i przelewy awaryjne, a rury spustowe mają iść w szachcie lub mieć czyszczaki. Główny spływ z ok. 100 m² rzygaczami
  z wysokości ok. 3 m na membranę dachu P1 grozi erozją, lodem i zawilgoceniem attyki.

**Pozostałe słabości:** pom. techn. dostępne tylko przez garaż; PC 3,80 m od granicy E (W-024); zbiornik 6 m³ ze skrzynkami
w ogródku frontowym nad przyłączami (W-145); strop garażu 24 cm/6,40 m jednokierunkowo pod dachem zielonym i zaspą przy uskoku
(l/d ≈ 31 — ugięcie na granicy); dwie płyty wspornikowe E (+2,75/3,05) i D (+3,65/3,85) w odstępie 0,60 m, czyli dwie linie
łączników; ogrzewany pas gospodarczy pod dachem garażu tworzy mostek na styku z garażem; E ma 11,40 m zamiast 12,2 m;
pom. rekuperacji zajmuje 2,33 m południowej elewacji P2; schody startują ze strefy dziennej; PU liczona razem z klatkami.

### W1 — 66 pkt
**Mocne strony:** największa wierność szkicowi. Parter to jeden prostokąt, piętra mają lica pd. i pn. w jednej płaszczyźnie.
Trzon ŻB centralny przy ścianie pn. usztywnia budynek. Rozpiętości ≤ 4,9 m, dach garażu dwukierunkowo 6,0 × 6,5 m.
Szkła ≈ 90 m², od północy ≈ 3,6 m². Dach ma 2 pola z wpustami i przelewami. Reku jest na P2 z wyłazem.

**Błąd krytyczny (do czasu poprawy)**
* **Belka ukryta 100 × 22 cm w osi 1 ma być podporą dla dwukondygnacyjnej ściany-tarczy ŻB osi E.** Ściana E (P1 + P2) waży
  ok. 190 kN plus stropy. Reakcja pd. to ok. 240 kN (ULS) i przypada w x = 11,40, między słupem SL4 (RK 120 × 120 × 8) a narożem F.
  Daje to M ≈ 140 kNm i ρ ≈ 1,1 % w płycie 22 cm. Ścinanie jest na granicy nośności, a przebicie przy głowicy RK120 nie zostało sprawdzone.
  Do tego dochodzą reakcje tarczy pd. P1 (x 0…4,2) na SL1. Ścieżka obciążeń nie jest wykazana. Trzeba zastosować belkę odwróconą
  (np. 30 × 65 jak PD-1 w W3 albo 25 × 105 jak B1 w W2).

**Słabości:** ok. 290 m² ścian ŻB (+100…130 tys. zł); schodkowy wspornik 2 × 1,0 m; ogrzewany boks C wysunięty 0,8 m
(dodatkowe ok. 15 m² przegród nad i pod powietrzem zewnętrznym oraz mostki); PC 3,40 m od granicy E (W-024 ✗); 6 m³ + skrzynki (W-145 ✗);
spocznik międzykondygnacyjny 1,05 m przy biegu 1,09 m (naruszone założenie „spocznik ≥ bieg”); przejście hol → strefa dzienna
przez spocznik klatki; kuchnia ok. 12 m od garażu; garaż 5,68 m (W-112 zaleca 5,90–6,00); pion K2 w narożu pokoju dziecka.

### W3 — 57 pkt
**Mocne strony:** słupy SL3/SL4 → SLC1/SLC2 → SLA3/SLA4 stoją w jednej linii pionowej (x 6,90 / 9,30). Ściany na wsporniku są lekkie.
PC stoi 13,3 m od granicy E. Retencja jest zgodna z W-145. Garaż 6,08 × 6,29 m. Łazienki P1 i P2 są w stosie.
Rytm kwater E odpowiada szkicowi. Strefa dzienna ma najlepszą głębokość (5,19 m).

**Błędy krytyczne (do czasu poprawy)**
1. **Filar P0 w osi 3 (x 6,295–6,95, 0,655 × 0,18 m z silikatu, bez ściany poprzecznej, bo oś C na P0 to ekran z lamel).**
   Zbiera nadproża otworów 1,00 m i 2,60 m, pasma 3 stropów (5,40 + 3,50 m), ścianę osi 3 z P1/P2 oraz reakcję PD-C
   (ściana C z P1 i P2). J2 szacuje N_Ed ≈ 550–650 kN wobec N_Rd ≈ Φ·A·f_d ≈ 0,75 · 0,118 · (2,6–4,5) MPa ≈ 230–400 kN.
   Filar jest przeciążony 1,5–2,5 razy.
2. **Ciągłość izolacji w strefie loggii nie jest wykazana** (brief §9 p. 1–2). ST3 wychodzi 2,1 m poza lico P2 (oś 1') bez łącznika,
   z dopiskiem „okap ocieplony”, a pod nim jest lekka ściana przeszkleń, co daje ryzyko f_Rsi < 0,72. Taras-loggia ST2L leży nad
   pomieszczeniami ogrzewanymi. Stopień ST2/ST2L ma 13 m. 5 słupów SLA przebija hydroizolację. Warstwy tarasu mają tylko 0,38 m
   (+5,90 → +6,28), a próg HS jest na +6,30.

**Słabości:** podciągi transferowe PD-4 (pn. ściana zewn. P1 i ściana nadbudowy P2 nad szklaną przegrodą, 3,25 m) i PD-C (ściana C
z 2 kondygnacji), więc zasada „ściany w pionie” jest złamana w 2 osiach; PD-1 skręcany przez dwie płyty wspornikowe (E-okap i C-dol)
na odcinku 3,9 m przy pustce; ok. 120 m² szkła i ok. 11,9 m² od północy (okna klatki 3,84 + 2,72 m²); latarnia pozioma 5,4 m²;
6 pól dachowych; okno klatki ON3 ma parapet ≈ +3,55, czyli tylko ok. 0,25 m nad dachem skrzydła (+3,30), w strefie zaspy przy uskoku;
pom. techn. 6,88 m² z centralą jest przepełnione; szacht SI 0,40 × 0,40 m ma pomieścić K1 Ø110 i kanały reku dla 2 kondygnacji;
czerpnia na elewacji pn. skrzydła obok jednostki PC i podjazdu (spaliny); spiżarnia 1,49 m²; strop garażu 24 cm/6,40 m jednokierunkowo
jak w W2; E ma 10,85 m zamiast 12,2 m; garaż cofnięty 4,80 m, więc linia D jest przerwana w 3D; daszek tylko 0,20 m przed linią
zabudowy; największe przeszklenia zachodnie (ryzyko D-03, §271); największy koszt (+8–12 %).

## 4. Rekomendacja: baza W2 + przeszczepy

1. **Z W3 (jednostka PC):** jednostka zewn. PC w osłonie lamelowej ≥ 6,0 m od granicy E (W-024). Dla W2: przy ścianie pd. pasa
   gospodarczego, x ≈ 16,3–17,5, y ≈ −1,3…−0,7, czyli 6,9 m od granicy E, przewody ok. 2 m, skropliny do żwirowej studni chłonnej ≥ 0,8 m p.p.t.
2. **Z W3 (retencja, W-145):** szczelny zbiornik 5,0 m³ z przelewem do niecki chłonnej ≥ 24 m² (głęb. ≤ 0,30 m), ≥ 2,0 m od granic
   i ≥ 3,0 m od fundamentów, w ogrodzie pd.-zach. Rezygnacja ze skrzynek w ogródku frontowym nad przyłączami.
3. **Z W3 (słupy w jednej linii) + rytm szkicu:** słupy SL fasady E w osiach ramy C. Kwatery E: 1,90 / 1,90 / 2,33 / 2,34 / 2,93 m,
   czyli x 0,30–2,20–4,10–6,43–8,77–11,70. Wtedy SL3/SL4 = SLC1/SLC2 i B1 nie dostaje sił skupionych w przęsłach.
   Drzwi HS w kwaterach 3 i 4 (po 2,33 m).
4. **Z W1 (lekka rama C):** płyty ramy C (dolna = linia D i górna) jako lekka rama stalowa ocynkowana w okładzinie na punktowych
   konsolach z przekładką termiczną (mostki χ) zamiast płyt ŻB na łącznikach liniowych. Daje to ok. −18 m łączników i ok. −25…35 tys. zł,
   a także usuwa szczelinę 0,60 m między dwiema płytami ŻB. Górny pas ramy przedłużony lekko na wschód do x ≈ 13,4, jak w W1 i w szkicu.
5. **Z W1/W3 (wyjście na taras zach.):** okno zach. salonu O0-02 zamienione na HS 2,40 × 2,60 m pod okapem 1,50 m. Szerokości nie
   zwiększać (ryzyko D-03).
6. **Z W1 (długość pasa E):** przeszklone drzwi gospodarcze O0-19 wykonane w systemie i podziale fasady E. Pas E czyta się wtedy
   jako ok. 12,85 m (x 0,30…13,15) bez przesuwania ściany nośnej E.
7. **Z W1 (warunkowo):** ściany klatki C–D na P0 jako ŻB 18 cm, jeśli analiza mimośrodu sztywności P0 w kierunku x
   (fasada pd. na słupach) tego wymaga.

## 5. Poprawki obowiązkowe (dla bazy W2)

1. **Odwodnienie dachu P2 (brief §9 p. 3, W-142):** ok. 100 m², Q ≈ 0,046 · 100 = 4,6 l/s. Min. 2 wpusty DN100 z grzałką przy
   attyce pn., rury spustowe w izolowanym szachcie SI lub nadbudowie, 2 przelewy awaryjne w attyce (≥ 100 × 60 mm, dno 30–50 mm
   nad membraną przy wpuście). Każde z 2 pól dachu P1 (+6,50) dostaje wpust i przelew. Wszystko prowadzi do zbiornika.
   Zakaz rzygaczy jako głównego odpływu.
2. **Pom. techniczne dostępne z domu:** przedsionek 0.10 łączy się z pom. techn. przez drzwi 0,90 m w ścianie x = 14,275.
   Spiżarnia 0.11 zostaje włączona do pom. techn., które rośnie do x 14,35–18,295, czyli ok. 9,4 m². Spiżarnię przenieść pod schody
   (0.05, 2,24 m², wejście od jadalni). Drzwi do garażu mogą zostać (EI30, U ≤ 1,3, samozamykacz).
3. **Strop nad garażem i pasem gospodarczym:** płyta dwukierunkowa na ścianach E, F, osi 2 i osi 5 (6,40 × 6,40 m, 24 cm) albo
   jednokierunkowo 26–28 cm. Obciążenia: zaspa przy uskoku do bryły B (μ_w = 4,0, czyli s ≈ 3,6 kN/m² przy ścianie na l_s ≈ 6,7 m),
   sytuacja wyjątkowa B2 (W-264) i dach zielony nasycony. Ugięcie ≤ L/250 (≤ 25 mm) z pełzaniem.
4. **Mostki przy pasie ogrzewanym:** stropodach nad pasem gospodarczym ma U ≤ 0,15 (PIR ≥ 20 cm lub równoważnie). Na styku z garażem
   (oś 2) potrzebne docieplenie spodu stropu garażu pasem ≥ 1,0 m (MW 10 cm) oraz dylatacja posadzek z XPS. Wszystkie węzły
   B1 + łącznik E-okap + łącznik C-dol, attyki i podparcie ściany A' na B3 policzyć numerycznie (PN-EN ISO 10211), f_Rsi ≥ 0,72 (W-248).
5. **Hałas PC:** po przeniesieniu wg przeszczepu 1 wykazać obliczeniowo L_Aeq,N ≤ 40 dB (cel 35 dB) na granicy E (W-024).
6. **Sztywność P0 w kierunku x:** sprawdzić mimośród środka sztywności (fasada pd. na słupach RK120 + B1, ściany osi 3 i 4, klatka C–D).
   Jeśli trzeba — ŻB w ścianach C/D na P0 (przeszczep 7) lub rama B1 + SL z połączeniami sztywnymi.
7. **PU ujednolicona** wg PN-ISO 9836 i RZF §20 (bez klatek schodowych): W2 ≈ 245,8 m². Nadal mieści się w przedziale 230–270.
   Schowek pod schodami liczyć tylko w części o wysokości ≥ 2,20 m, a pas 1,40–2,20 m w 50 %.
8. *(zalecenie, nie warunek)* **Pom. rekuperacji P2 (2.06)** zajmuje 2,33 m elewacji pd. za lamelami. Rozważyć przeniesienie
   centrali do nadbudowy przy klatce (np. kosztem części łazienki 2.04 lub garderoby) i oddanie tego pasa garderobie lub gabinetowi.
9. **Wykonawczo (dla wszystkich wariantów):** wsporniki EQU 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb i ugięcie końca ≤ wysięg/125;
   łączniki z ETA (W-272); rama C i krawędź okapu E ze szczeliną dylatacyjną nad stolarką (W-268).

**Jeśli synteza wybierze inny wariant:** W1 wymaga zastąpienia belki ukrytej w osi 1 belką odwróconą ≥ 30 × 65 cm, spocznika ≥ 1,10 m,
PC ≥ 6,0 m i retencji wg W-145. W3 wymaga filara ŻB C30/37 25 × 65 cm na stopie 1,2 × 1,2 m w osi 3 (x 6,30–6,95),
łącznika termoizolacyjnego ST3 na linii 1' albo obłożenia podsufitki loggii ≥ 12 cm (ψ ≤ 0,10), warstw tarasu ≥ 0,45 m
z odwodnieniem liniowym przy HS, centrali reku na P2, szachtu SI ≥ 0,40 × 0,90 m, czerpni ≥ 8 m od podjazdu i ≥ 3 m od PC,
parapetu ON3 ≥ +3,80 (≥ 0,50 m nad dachem skrzydła), niecki ≥ 2,0 m od granicy W i daszka ≥ 0,50 m przed linią zabudowy.
