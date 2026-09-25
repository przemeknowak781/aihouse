# Dom LAMELA — KONCEPCJA OSTATECZNA (synteza wariantów W1–W3)

Wersja 2.0 z 25.09.2026, stadium: koncepcja architektoniczno-budowlana. Jedno źródło prawdy to `model/budynek.yaml` i `model/dzialka.yaml`. Oba pliki
generuje skrypt parametryczny `tools/buduj_model.py`, razem z `model/wyposazenie.yaml` i `model/instalacje.yaml`. Schemat danych opisuje
`docs/SCHEMAT_MODELU.md`. Wszystkie rysunki, bilans i model 3D powstają z tych plików:
* podgląd kontrolny: `tools/podglad_modelu.py` → `docs/20_koncepcja/final/`;
* arkusze PB: `tools/generuj_widoki.py` → `projekt/01_koncepcja/widoki/`;
* model 3D: `lamela.pipeline` → `projekt/07_model_3D/wstepne/`.

Liczby w tabelach bilansu (sekcja 9) wstawia automatycznie podgląd. Wartości podane w tekście odczytano z modelu w chwili wydania.

Podstawa techniczna to WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu obowiązującym do 19.09.2026. WT stosuje się na podstawie
art. 102a ust. 1 i 2 PB (Dz.U. 2026 poz. 524 ze zm.) w związku z oświadczeniem Inwestora [data do uzupełnienia] (rejestr W-A.1). Identyfikatory
`W-xxx` odsyłają do `docs/10_podstawy_prawne/00_rejestr_wymagan.md`.

---

## 1. Wybór bazy — werdykt panelu i rola wariantu W3

| sędzia (soczewka) | W1 | W2 | W3 | rekomendowana baza |
|---|---|---|---|---|
| J1 — funkcja i przepisy | 73 | **76** | 63 | W2 |
| J2 — konstrukcja, koszt, fizyka budowli | 66 | **76** | 57 | W2 |
| J3 — wierność szkicowi, potencjał katalogowy | 73 | 66 | **78** | W3 |
| **średnia / większość** | 70,7 | **72,7** | 66,0 | **W2** (2 z 3 głosów i najwyższa średnia) |

**Bazą jest W2** („funkcja · ekonomia · konstrukcja”). Jego zalety:
* ściany nośne stoją w pionie, stropy są jednokierunkowe;
* łazienki P0/P1/P2 leżą w jednym pionie przy szachcie SI;
* droga garaż → przedsionek → kuchnia ma ok. 6 m;
* wszystkie odległości od granic mają zapas.

Na bazę przeniesiono przeszczepy z W1 i W3 oraz **wszystkie poprawki obowiązkowe** sędziów J1–J3 (sekcja 4).

**Wariant W3 („Światło · Ogród · Sekwencja wejścia”).** Agent W3 zakończył pracę ok. 02:39. Dostarczył `W3/opis.md`, 6 rysunków i skrypty `src/`,
ale bez eksportu `model_W3.json`. Panel ocenił go na równi z W1 i W2: J1 63, J2 57, J3 78. Nie został bazą z trzech powodów:
* przeciążony filar P0 (J2);
* loggia nad pomieszczeniami ogrzewanymi (J2);
* cofnięty garaż, który w 3D rozrywa linię D (J3).

W3 ma jednak najlepsze rozwiązania w kilku obszarach i stąd pochodzi 6 przeszczepów:
* retencja: zbiornik 5 m³ + niecka;
* jednostka zewnętrzna PC ≥ 6 m od granicy;
* ekran z lamel wydzielający pas komunikacyjny;
* szklana przegroda wiatrołapu;
* rytm kwater przeszklenia E;
* słupy w jednej linii pionowej.

Uzupełnienie `model_W3.json` przestało być potrzebne, bo model ostateczny jest jeden (`model/*.yaml`).

## 2. Idea i relacja do szkicu

Dom to trzy poziome warstwy przesunięte względem siebie w rytmie **zachód – wschód – zachód**. Tworzą one sylwetę „S” na elewacji ogrodowej
(interpretacja v2, decyzje Inwestora z 25.09.2026). Litery odpowiadają oznaczeniom szkicu:
* **A — II piętro:** bryła 13,60 m w pionowych lamelach z drewna termo. Wysunięta 1,00 m na zachód poza lico bryły B (wspornik na belkach
  B4/B5). Płyty ST2/ST3 wystają 1,00 m na południe i 1,10 m na zachód (PL-2, PL-3).
* **B — I piętro:** bryła pełna 12,60 m (lica ETICS, osie A–E 12,00 m), cofnięta od zachodu.
* **C — boks w ramie:** trzy kwatery okna BC1 (≈ 7,0 m, słupki SL5/SL6) w lekkiej ramie stalowej wysuniętej 1,00 m (PL-C1, PL-C2). Pas górny
  ramy biegnie na wschód do x = 13,45, jak w szkicu.
* **D — linia pozioma:** pas dolny ramy C (+3,65…+3,85) przechodzi w attykę zielonego dachu garażu D4 (+3,85). Kończy się narożnikiem
  garażu **18,975 m** od lica zachodniego bryły B (szkic ≈ 19,0 m). **Nie jest tarasem:** dach garażu jest ekstensywny i nieużytkowy, bez
  wyjścia i bez wiaty (decyzja Inwestora 2).
* **G — garaż 2-stanowiskowy:** w bryle parteru, **w licu ogrodowym** (przeszczep J3/W1). W świetle ma 6,05 × 6,175 m. Brama od północy.
* **E — parter:** ciągłe przeszklenie strefy dziennej w 5 kwaterach o narastającym rytmie 1,90 / 1,90 / 2,34 / 2,34 / 2,92 m (przeszczep z W3).
  Szósta kwatera to przeszklone drzwi gospodarcze w tym samym systemie, więc pas E czyta się na ok. 12,85 m. Nad nim płyta-okap E wystaje
  1,00 m na południe i 1,50 m na zachód (PL-E, +2,75…+3,05).

Porównanie krawędzi z modelu z odczytem szkicu (brief §1.1, 45,8 px/m; x liczone od lica zach. bryły B):

| element | szkic [m] | model [m] | uwagi |
|---|---|---|---|
| A — bryła II p. | −0,98 … +12,23 | −1,00 … +12,60 | wspornik 1,00 m jak w szkicu; wsch. koniec w licu B (ściany w pionie) |
| A — płyty | −2,40 … +12,55 | −2,10 … +12,90 | okap 1,10 m zach., 1,00 m pd., 0,30 m wsch. |
| B — bryła I p. | 0 … +12,01 | 0 … +12,60 | +0,6 m: moduł osi 12,00 m + ETICS (odstępstwo świadome) |
| C — boks (szkło) | +4,48 … +11,68 | +4,40 … +11,42 | 3 kwatery ≈ 2,34 m |
| C — rama górna | +3,93 … +13,76 | +3,90 … +13,75 | przedłużona na wschód (przeszczep z W1) |
| D — linia | +3,82 … +19,00 | +3,90 … +18,975 | jedna ciągła krawędź (+3,85) do narożnika G |
| E — przeszklenie | +0,98 … +13,21 | +0,60 … +13,45 | z drzwiami gospodarczymi w systemie fasady |
| E — płyta | −1,53 … +14,08 | −1,50 … +14,10 | okap zach. 1,50 m |

Graficzne porównanie z odchyłkami liczonymi przez skrypt jest w `final/elewacja_S_szkic.png`. Proporcje pionowe szkicu są umowne,
bo wysokości kondygnacji wynikają z WT. Zachowano kolejność pasm:
* okap E +2,75…+3,05;
* linia D +3,65…+3,85;
* boks C +3,85…+5,35;
* rama górna +5,35…+5,55;
* płyta A +5,95…+6,25;
* lamele +6,25…+9,08;
* stropodach +9,08…+9,40, attyka +9,776.

## 3. Funkcja

**Układ ogólny.** Trzon mieszkalny ma w osiach A–E × 1–4 wymiary 12,00 × 8,75 m. Strefa dzienna leży na południu (pas osi 1–3, 5,125 m),
pomocnicza i komunikacja na północy (pas osi 3–4, 3,625 m). Od wschodu dostawiono bryłę G (osie E–F, 6,375 m) z pasem gospodarczym od
ogrodu (oś 1–2) i garażem (oś 2–5). Klatka schodowa U w osiach C–D przechodzi przez 3 kondygnacje. Szacht SI (0,40 × 1,12 m) przy osi C
obsługuje łazienki P0, P1 i P2 ustawione jedna nad drugą (x 3,98–5,77).

**Parter P0 (±0,00):**
* wejście pod daszkiem 2,30 × 1,30 m;
* wiatrołap 0.01 z drzwiami szklanymi VSG w osi wejścia (x ≈ 10,60) i doświetlem bocznym;
* hol 0.02 z szafą wejściową;
* WC gościnne 0.03 (szerokość 1,195 m ≥ 0,90);
* **pas komunikacyjny 0.07** wydzielony ekranem z lamel dębowych h = 2,10 m, prowadzący z holu do stopy schodów bez przechodzenia przez strefę
  mebli (poprawka J1);
* strefa dzienna 0.06 — salon, jadalnia, kuchnia ≈ 54 m²:
  * przeszklenie E z dwoma HS;
  * HS 2,40 m na taras zachodni pod okapem 1,50 m;
  * kuchnia z **ciągłą zabudową na ścianie osi E** (y 1,30–5,02) i wyspą, z oknem FX2 od południa;
* spiżarnia 0.05 pod biegiem 2 (wejście od jadalni);
* przedpokój gościnny 0.08 → pokój gościnny/gabinet 0.10 (12,5 m², okno zach.) i łazienka gościnna 0.09 z natryskiem (drzwi przesuwne);
* przedsionek gospodarczy 0.11:
  * wejście z garażu drzwiami szczelnymi z samozamykaczem;
  * drzwi do kuchni przy fasadzie, droga auto → kuchnia ≈ 6 m;
  * drzwi przeszklone do ogrodu;
  * wejście do pomieszczenia technicznego 0.12 (8,85 m², **dostęp z domu** — poprawka J2);
* garaż 0.13 (6,05 × 6,175 m w świetle, nieogrzewany):
  * brama segmentowa 5,00 × 2,25 m;
  * drzwi boczne od wschodu;
  * miejsce na rowery i sprzęt ogrodowy przy ścianie osi 2, poza torem jazdy.

**I piętro P1 (+3,15):**
* hol 1.01 z galerią przy schodach;
* pokój rodzinny/biblioteka 1.02 za boksem C z oknem wschodnim;
* dwa pokoje dzieci od zachodu: 13,2 i 12,5 m²;
* łazienka dzieci z wanną w pionie SI;
* WC z natryskiem 1.07 nad WC parteru (pion K2);
* pralnia z suszarnią 1.08, zmniejszona do ≈ 6,6 m² (przeszczep J1).

**II piętro P2 (+6,30), bryła A za lamelami:**
* apartament rodziców: sypialnia 2.02 (≈ 21 m², naroże S+W nad wspornikiem), garderoba 2.03 pełniąca rolę przedpokoju apartamentu, łazienka
  2.04 w pionie SI w nadbudowie od północy;
* gabinet/pokój 2.05 (16,3 m², S+E), który może też być pokojem 5. osoby;
* hol 2.01;
* pomieszczenie techniczne 2.07 z centralą rekuperacyjną i wyłazem 0,90 × 0,90 m na dach (PV).

**Schody SCH1/SCH2** (jednakowe, jedne nad drugimi, WT §68–69, W-090/W-091):
* 2 × 9 podnóżków, h = 0,175 m, s = 0,28 m, 2h + s = 0,63 m;
* bieg 1,15 / 1,145 m między licami; szerokość użytkowa przy jednym pochwycie ciągłym Ø42 wokół ścianki środkowej ≈ 1,05 m ≥ 1,00;
* spocznik 2,415 × 1,175 m;
* prześwit nad biegiem ≈ 2,75 m;
* klatka obudowana ścianami C/D i ścianką środkową SC12, więc bez otwartych krawędzi;
* nad spocznikiem świetlik SW1, od północy okno ON4.

**Kontrola wymagań** (szczegóły w bilansie §9):
* wysokość w świetle pokoi 2,77 m (≥ 2,50; cel 2,70–2,80);
* drzwi do pokoi, łazienek i WC 0,90 × 2,10 w murze, łazienki i WC otwierane na zewnątrz lub przesuwne, z podcięciem ≥ 0,022 m²
  (WT §75, §79, W-058/W-059);
* drzwi wejściowe 1,10 × 2,40, próg ≤ 0,02 (W-055);
* okna ≥ 1/8 powierzchni podłogi we wszystkich pokojach (W-080);
* niskie parapety P1/P2: dolna część stała VSG do 0,85 m, skrzydła P2 otwierane do wewnątrz (W-097/W-098).

## 4. Przeszczepy i poprawki obowiązkowe — rozliczenie

| źródło | wymaganie / przeszczep | rozwiązanie w modelu |
|---|---|---|
| J1, J2, J3 | drzwi ≥ 0,90 × 2,10 w murze; łazienki/WC na zewnątrz lub przesuwne; wejście ≥ 1,10 × 2,15 | symbole D1/D2/D2P/D4 0,90 × 2,10; O0-16 przesuwne; O0-19, O1-10, O1-11, O2-10 na zewnątrz; DZ1 1,10 × 2,40 |
| J1 | schody: szerokość użytkowa ≥ 1,00 m | biegi 1,15 / 1,145 m, jeden pochwyt ciągły (BL1, BL2) → ≈ 1,05 m |
| J1, J2 | PC monoblok R290, ≥ 6,0 m od granicy E, strefa 1,0 m, ekran, L_Aeq,N ≤ 40 (cel 35) dB | jednostka przy ścianie pd. pasa gospodarczego, 7,0 m od granicy E (PC-JZ w `dzialka.yaml`); strefa R290 bez okien/drzwi/wpustów; osłona lamelowa z ekranem od tarasu; szacunek hałasu §7 |
| J1, J2 (z W3) | retencja: szczelny zbiornik ≤ 5 m³ + niecka ≈ 24 m² (W-145) | zbiornik 5,0 m³ + niecka NCH-1 24 m² × 0,30 m w ogrodzie pd., ≥ 3 m od fundamentów, ≥ 2 m od granic |
| J1, J2, J3 | PU wg RPB §20 / W-316 bez klatek, garaż i techniczne osobno | bilans §9 (podgląd liczy wg W-316; spiżarnia pod biegiem w 50 %) |
| J1 (z W3) | stopa schodów dostępna z holu bez strefy mebli | pas komunikacyjny 0.07 + ekran z lamel LAM-P0 (h 2,10) |
| J1 (z W3) | szklana przegroda wiatrołap/hol, doświetle drzwi | ścianka SGL S0-21 z drzwiami DS1 w osi wejścia; FX3 |
| J1 (z W1) | kuchnia z ciągłą zabudową; drzwi przedsionek → kuchnia przy fasadzie | O0-21 w S0-15 na y 0,25–1,15; blaty y 1,30–5,02 + wyspa |
| J1 | pralnia ≈ 6,5 m²; zysk dla łazienki/pokoju | pralnia 1.08 ≈ 6,6 m² + WC z natryskiem 1.07 (drugi punkt sanitarny P1) |
| J1 | czerpnia W-166, wyrzutnia W-167 | czerpnia i wyrzutnia dachowe ≥ 0,40 m nad pokryciem, ≥ 6 m od wywiewki K1 i od siebie (`energia.wentylacja`) |
| J1 | niskie parapety W-097 | OP1/OP3 i BC1 z dolną częścią stałą VSG do 0,85 m; brak siedziska w boksie |
| J1, J2 | linia zabudowy: zapas ≥ 0,30–0,50 m | daszek PL-DA i podest 0,95 m za linią zabudowy |
| J2 | odwodnienie stropodachu P2 wpustami (nie rzygaczami), przelewy w każdym polu | D1: WP1/WP2 DN100 podgrzewane → RS1/RS2 w izolowanym szachcie SI; przelewy PA1–PA3; D2, D3, D4 z własnymi wpustami, przelewami i rurami (§6) |
| J2 | strop garażu dwukierunkowy / pogrubiony; zaspa, B2, dach zielony nasycony | płyta D4 24 cm dwukierunkowa na ścianach E, F, osi 2 i 5 (6,375 × 6,50 m) |
| J2 | mostki pasa gospodarczego pod dachem garażu | ciągły ETICS wokół całego P0 (garaż jako bufor wewnątrz obudowy); SWG z wełną 12 cm od garażu; docieplenie spodu stropu garażu pasem 1,0 m (SUF-G); węzły WZ-09 |
| J2 | mimośród sztywności P0 (fasada na słupach) | ściany trzonu klatki C i D na P0 żelbetowe 18 cm (przegroda SWZB) |
| J2 | wsporniki: EQU, ugięcia, łączniki z ETA, szczelina nad stolarką | `konstrukcja.sciezka_obciazen`; wszystkie płyty wysunięte `lacznik_termiczny: true` |
| J2 (z W3) | słupy E w osiach ramy C (jedna linia pionowa) | SL3/SL4 (x 6,44 / 8,78) = SL5/SL6 boksu C; kwatery 1,90/1,90/2,34/2,34/2,92 |
| J2 (z W1) | lekka rama C na konsolach punktowych | PL-C1/PL-C2 z materiału RAMA_C (stal w okładzinie), węzeł χ WZ-14 |
| J2 | HS na taras zach.; drzwi gospodarcze w systemie fasady E | O0-11 (HS2 2,40 × 2,75); O0-06 (DZ3) w podziale fasady |
| J3 | garaż w licu ogrodowym, linia D jedną krawędzią do narożnika | bryła G x 12,30–18,675, lico y −0,30; linia D +3,85 do x 18,675 |
| J3 | rama górna C przedłużona na wschód | PL-C2 do x 13,45 |
| J3 | elewacja północna i widok od ogrodu | arkusze PB-AR-07…10 i model 3D (pipeline) |

**Wytyczne koordynatora z symulacji mostków 2D** (katalog `projekt/08_obliczenia/demo_test/mostki`) wprowadzono do przegród, otworów
i sekcji `wezly`:
1. **Ciepły montaż stolarki.** Rama wsunięta 5 cm w mur i 4 cm w izolację, izolacja ościeża z zakładem 3 cm na ramę, taśmy
   paroszczelne wewnątrz i paroprzepuszczalne na zewnątrz (pole `montaz` każdego otworu zewnętrznego).
2. **Brak kaset osłon w ociepleniu** (`oslona_montaz`):
   * P0: kasety screenów w podsufitce okapu PL-E;
   * boks C: w pasie górnym ramy;
   * P2: w szczelinie wentylowanej za lamelami;
   * okna zachodnie: kasety nadstawne przed licem ETICS.
3. **Posadowienie.** Płyta fundamentowa na XPS 20 cm z ciągłą izolacją cokołu (WZ-GF2 „dobry”).
4. **Garaż.** Izolacja domu ciągła po zewnątrz, a ściany i strop garażu jej nie przerywają (WZ-G1).
5. **Progi HS i drzwi na płycie P0.** Profil progowy termoizolacyjny na podwalinie XPS/PUR-GF, odwodnienie liniowe OL-2/OL-2W/OL-3
   (pole `prog`, węzeł WZ-11T).
6. **Płyty wysunięte.** Wszystkie na łącznikach z ETA, ze spadkiem 2 % od budynku i okapnikiem.
7. **Rury spustowe.** Zewnętrzne RS3–RS5 przed licem na obejmach dystansowych. Wewnętrzne RS1/RS2 w izolowanym szachcie SI, RS6
   w pomieszczeniu technicznym. Żadna nie jest we wnęce ocieplenia.
8. **Typy węzłów** wg `ALIASY_WEZLOW` (`mostki2d/katalog.py`), więc `tools/katalog_mostkow.py` policzy je automatycznie.

## 5. Konstrukcja

**System.** Ściany nośne są murowane z bloczków silikatowych 18 cm, kl. 20, na zaprawie cienkowarstwowej (f_d = 4,50 MPa przy klasie
wykonania A, W-270). Stropy to płyty żelbetowe monolityczne C25/30 grubości 22 cm, jednokierunkowe N–S. Elementy wysunięte, attyki
i belki są z betonu C30/37 XC4/XF1. Stal B500SP. Stosowane są Eurokody 1. generacji z NA (W-260), klasa CC2/RC2, okres użytkowania 50 lat.
Budynek jest w **II kategorii geotechnicznej** (W-280).

**Ściany nośne w pionie** (model: `sciany`):
* oś A: P0–P1;
* oś E: P0–P2;
* oś 3 (grzbietowa): P0–P2;
* oś 4: P0–P1 oraz P2 w nadbudowie;
* osie B, C, D: P0–P1 i nadbudowa P2;
* oś 1: P1–P2 na belce B1;
* garaż i pas gospodarczy: osie E, F, 2, 5.

**Ścieżki obciążeń** (`konstrukcja.sciezka_obciazen`):
* **ST1 i ST2** (22 cm) pracują N–S jako płyty ciągłe dwuprzęsłowe o rozpiętości 5,125 / 3,625 m. Podpory: oś 1 (belka B1 / ściana), oś 3 i oś 4.
  Nad wejściem na schody i nad wyjściem z nich płyty podpierają podciągi B8/B9 25 × 50 w osi 3 (C–D).
* **Fasada E na parterze.** Belka odwrócona **B1 25 × 107 cm** (+2,78…+3,85, tworzy pas podokienny boksu C) leży na słupach RK 120×120×8
  SL1–SL4 w szprosach przeszklenia oraz na ścianach A i E. Przęsła mają ≤ 3,23 m. B1 niesie ścianę pd. P1 i P2 i pas trzech stropów.
  **Słupki boksu C SL5/SL6 stoją w jednej linii pionowej ze słupami SL3/SL4**, więc siły skupione nadproża B2 (25 × 80) trafiają nad podpory B1.
* **Wspornik bryły A (1,00 m w osi).** Obciążenie przechodzi kolejno:
  1. lekka ściana szkieletowa A' (SZL, ≤ 1,0 kN/m²);
  2. belka krawędziowa B3 20 × 60 w osi A' (odwrócona, pod parapetem okna O2-04) wraz z okapem PL-2;
  3. końce **belek wspornikowych B4 i B5** 18 × 80 cm w licach ścian P2 w osiach 1 i 3 (pod parapetami okien P2);
  4. ściana A na P1 jako podpora, z zakotwieniem w przęśle A–B 3,875 m dociążonym ścianami P2 i stropem ST3.

  Stropodach nad wspornikiem niesie belka B6 w osi A'. Nie ma ścian-tarcz: wszystkie elementy są prętowe i sprawdzalne w bibliotece
  konstrukcji (SCHEMAT p. 9). Warunki: EQU 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb (W-262), ugięcie końca ≤ l/125 (W-268).
* **Dach garażu D4.** Płyta 24 cm dwukierunkowa na ścianach E, F, osi 2 i osi 5 (6,375 × 6,50 m, l/d ≈ 27). Obciążenia:
  * dach zielony w stanie nasyconym ≈ 1,6 kN/m² jako stałe;
  * zaspa przy uskoku do bryły B, μ_w ≤ 4,0 (W-264);
  * sytuacja wyjątkowa B2.
* **Płyty wysunięte ≤ 1,50 m** (PL-E, PL-DA, PL-2, PL-3) są na łącznikach termoizolacyjnych z ETA (W-272). Rama C to lekki ruszt stalowy
  w okładzinie na konsolach punktowych. Nad stolarką pod krawędziami okapu E i ramy C przewidziano szczelinę dylatacyjną.
* **Usztywnienie.** Ściany w obu kierunkach i stropy jako tarcze. Przy przeszklonej fasadzie pd. parteru sztywność w kierunku x daje trzon
  klatki z **żelbetowymi ścianami C i D na P0** (SWZB, poprawka J2) razem ze ścianami osi 3 i 4.
* **Schody.** Płyty biegów i spoczników ŻB 18 cm oparte na ścianach C/D i ściance środkowej. Stopnie dębowe.

**Posadowienie — płyta fundamentowa na XPS (decyzja).** Porównano ją z ławami W2 (60 × 35 cm, spód −1,10). Wybrano płytę ŻB 25 cm C25/30 XC2
na XPS 300 20 cm, z pogrubieniami (żebrami) pod ścianami nośnymi (60 × 30 / 50 × 25 cm) i pod słupami SL1–SL4 (1,0 × 1,0 × 0,45 m).
Uzasadnienie:
1. **Ciągłość izolacji.** Węzeł cokołu z płytą na XPS jest „dobry”, a ława z murem fundamentowym zamyka izolację przez grunt, więc jest
   „do poprawy” (katalog mostków WZ-GF1/GF2). To wymaganie Inwestora z briefu §9.
2. **Grunt.** Piaski średnie I_D ≈ 0,6 i ZWG ≈ 3,8 m p.p.t. to warunki proste: drenaż zbędny (W-285), a posadowienie płytkie
   z przeciwprzemarzaniową izolacją obwodową XPS 10 cm × 1,00 m wg PN-EN ISO 13793 (W-284 — wariant płyty).
3. **Obciążenia.** Siły skupione ze słupów fasady E i obciążenia nierównomierne (wspornik, trzon) rozkładają się na płycie, co ogranicza
   różnice osiadań (W-283: s ≤ 50 mm, Δ ≤ 10 mm).
4. **Szczelność i uziom.** Płyta daje ciągłą membranę przeciwwilgociową i przeciwradonową, a uziom otokowy można ułożyć w gruncie pod XPS
   (W-286).
5. **Nośność XPS 300.** Naprężenia pod pogrubieniami ≈ 70–110 kPa, czyli poniżej dopuszczalnego ≈ 130 kPa (pełzanie 50 lat) — do wykazania w PT.

Garaż stoi na tej samej płycie. Jego posadzka −0,10 ma spadek 1,5 % do bramy (W-114). Zakres badań podłoża: opinia geotechniczna,
≥ 3 sondowania CPT/DPL do ≥ 6 m, projekt geotechniczny (W-281/W-282).

## 6. Materiały, przegrody, fizyka budowli i woda

Przegrody mają pełne warstwy w `przegrody`, a materiały opisują λ, ρ, c_p i μ lub sd ze źródłem w polu `zrodlo` (PN-EN ISO 10456, PN-EN 1745,
DWU typowych wyrobów „lub równoważne”). U podano orientacyjnie wg PN-EN ISO 6946; dokładne wartości z mostkami liczy moduł fizyki.

| kod | przegroda | U ≈ [W/(m²K)] | wymaganie |
|---|---|---|---|
| SZ1 | silikat 18 + ETICS EPS 031 20 cm | 0,15 | ≤ 0,20 (W-243) |
| SZ2 | P2 za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV, szczelina wentylowana, lamele | 0,16 | ≤ 0,20 |
| SZL | ściana lekka A' na wsporniku: szkielet KVH z wełną, OSB (szczelność), DWD, wełna fasadowa 18 cm | 0,10 | ≤ 0,20 |
| SWG | ściana dom–garaż: silikat 18 + wełna 12 cm od garażu | 0,26 | ≤ 0,30 |
| SD1 | stropodach bryły A: TPO, PIR spadkowy 12–32 cm, paroizolacja z Al, ŻB 22 | 0,10 | ≤ 0,15 |
| SD2 | dachy nad P1: żwir, TPO, PIR 14–26 cm, paroizolacja, ŻB 22 | 0,11 | ≤ 0,15 |
| DZ1 | dach zielony ekstensywny garażu i pasa gosp.: substrat 8 cm, geowłóknina, mata drenażowa, bariera przeciwkorzenna, 2 × papa SBS, PIR 12–24 cm, paroizolacja, ŻB 24 | 0,12 | ≤ 0,15 nad pasem ogrzewanym |
| POD-0 | płyta fundamentowa: posadzka, jastrych z ogrzewaniem, EPS 6,5 cm, membrana SBS, ŻB 25, XPS 20 cm | 0,13 | ≤ 0,30 |
| POD-1 | strop międzykondygnacyjny: deska/gres, jastrych z wężownicą, EPS 100 + EPS T | — | akustyka R'w, L'n,w (W-230) |
| SUF-ZEW | spód stropu nad powietrzem (wspornik A): wełna 20 cm + podsufitka wentylowana | 0,15 | ≤ 0,15 |
| AT1 | attyka ŻB 18, izolowana z 3 stron (PIR 10 cm od dachu, ETICS, PIR na koronie) | — | f_Rsi ≥ 0,72 (W-248) |

**Zasada „4 linii”** (brief §9.1) jest ciągła wokół całej obudowy ogrzewanej:
* **izolacja:** XPS pod płytą → XPS cokołu → ETICS / wełna fasadowa → PIR na attykach i dachach → wełna pod wspornikiem; płyty wysunięte
  przechodzą przez nią tylko łącznikami z ETA; garaż jest buforem wewnątrz ciągłego ETICS parteru;
* **hydroizolacja:** membrana SBS na płycie → wywinięcie na cokół ≥ 0,30 m → pasy przy progach → membrany dachów z wywinięciem na attyki
  ≥ 0,15 m; w łazienkach hydroizolacja podpłytkowa;
* **szczelność powietrzna i paroizolacja:** tynk wewnętrzny → taśmy przy stolarce → paroizolacja z Al na płytach stropodachów → OSB ściany
  SZL; cel n50 ≤ 1,0 h⁻¹ (W-249);
* **warstwa zewnętrzna:** tynk ETICS / membrana UV za lamelami / obróbki.

Katalog węzłów do symulacji PN-EN ISO 10211 jest w sekcji `wezly` modelu: attyki D1–D4, płyty wysunięte na łącznikach, strop nad powietrzem,
ościeża, nadproża, podokienniki, progi, cokół, połączenia z garażem, konsole lamel i ramy C, przejścia instalacji.

**Odwodnienie dachów** (W-142, PN-EN 12056-3, r = 0,046 l/(s·m²)). Każde pole dachu ma spadek ≥ 2 % na izolacji spadkowej, wpust i przelew
awaryjny w attyce:
* **D1** (≈ 97 m²; Q ≈ 4,5 l/s): wpusty WP1/WP2 DN100 z grzałką; rury RS1/RS2 w izolowanym szachcie SI; przelewy PA1–PA3;
* **D2 i D3** (pola nad P1): wpusty attykowe WP3/WP4; rury zewnętrzne RS3/RS4 na elewacji pn. przed licem, z czyszczakami; przelewy PA4/PA5;
* **D4** (dach zielony): wpusty WP5/WP6 w studzienkach kontrolnych w opasce żwirowej; RS5 zewnętrzna w narożu NE, RS6 w pomieszczeniu
  technicznym; przelewy PA6/PA7.

Wszystkie rury prowadzą kolektorami KD-W/KD-E do szczelnego zbiornika 5,0 m³. Jego przelew DN160 idzie do niecki chłonnej 24 m² (W-145).

**Woda gruntowa i powierzchniowa.** Drenażu opaskowego się **nie projektuje**: piaski przepuszczalne, ZWG ≈ 3,8 m p.p.t., posadowienie
≈ 0,5 m p.p.t. (W-285). Zamiast niego:
* teren ze spadkiem ≥ 2 % od budynku na ≥ 1,5–2 m (`teren.punkty_projektowane`);
* opaska żwirowa 0,5 m;
* odwodnienia liniowe przed bramą, przy progach HS, przy wejściu i przy bramie wjazdowej;
* niecki trawiaste od drogi i od granicy E.

Woda nie spływa na drogę ani na działki sąsiednie (W-018, W-019).

## 7. Energia i instalacje

* **Orientacja i osłony.** Strefa dzienna ma przeszklenie E od południa pod okapem 1,00 m. W czerwcu w południe (h ≈ 61°) okap zacienia górną
  część szkła, a resztę osłaniają screeny ZIP z kasetami w podsufitce okapu. Zimą (h ≈ 14°) słońce wpada na całą głębokość strefy. Pozostałe
  osłony:
  * boks C: rama wysunięta 1,00 m jako łamacz światła, screen w ramie;
  * P2: stałe lamele pionowe i screeny w szczelinie za lamelami;
  * okna zachodnie: żaluzje zewnętrzne z kasetą przed licem.

  Wymaganie g ≤ 0,35 (W-247) spełniają osłony zewnętrzne. Od północy są tylko drzwi wejściowe, małe okna łazienek i pralni oraz okno klatki.
  Pomieszczenia pomocnicze i komunikacja leżą od północy, sypialnie od E, S i W.
* **Źródło ciepła.** Pompa ciepła powietrze–woda typu **monoblok R290** (W-155). Moduł hydrauliczny stoi w pomieszczeniu technicznym 0.12,
  razem z:
  * zasobnikiem CWU 300 dm³ i buforem 100 dm³;
  * rozdzielaczami ogrzewania podłogowego 35/28 °C z regulacją w każdym pomieszczeniu (W-152);
  * rozdzielnicą RG i wodomierzem z zabezpieczeniem przed przepływem zwrotnym (W-131).

  Jednostka zewnętrzna stoi przy ścianie pd. pasa gospodarczego, **7,0 m od granicy E**, w osłonie lamelowej z ekranem od tarasu. Strefa R290
  1,0 m jest wolna od otworów, wpustów i studzienek (W-156). Skropliny odprowadza studnia chłonna ≥ 0,8 m p.p.t. Szacunek hałasu:
  L_WA ≈ 55 dB(A), Q = 4, r ≈ 7 m → L_p ≈ 55 + 10·log(4/(4π·7²)) ≈ 33 dB(A) na granicy. To mniej niż 40 dB (noc) i mniej niż cel 35 dB
  (W-024); w PT potwierdzić DTR wyrobu.
* **Wentylacja mechaniczna z odzyskiem ciepła.** Centrala ≈ 450 m³/h (η ≈ 0,85) stoi na P2 w pomieszczeniu 2.07. Czerpnia i wyrzutnia są dachowe
  (W-166/W-167). Kanały biegną pionowo w szachcie SI, poziomo w sufitach podwieszanych holi i łazienek. Wywiew wg PN-83/B-03430/Az3
  (`pomieszczenia[].went`, W-162):
  * kuchnia 50 (okresowo 120) m³/h;
  * łazienki i WC z natryskiem po 50 m³/h;
  * WC 30 m³/h;
  * pralnia 40 m³/h;
  * pomieszczenia bezokienne 15 m³/h.

  Nawiew do pokoi pokrywa ≥ 20 m³/h na osobę (W-161). Garaż nie jest podłączony do rekuperacji: wentylacja naturalna ≥ 0,08 m² przez
  kratki bramy (W-115).
* **Kanalizacja.**
  * Pion K1 Ø110 w SI obsługuje łazienki P0/P1/P2 i jest wentylowany ponad dach nadbudowy.
  * Pion K2 obsługuje WC P0 i WC z natryskiem na P1, z zaworem napowietrzającym (W-139).
  * Wyjście pod płytą do studzienki SR1 przed elewacją pn. (poza garażem — W-118), przykanalik PVC 160.
* **PV.** 15 modułów × 430 Wp = 6,45 kWp ≤ 6,5 kWp (art. 29 ust. 4 pkt 3 lit. c PB, W-194) na dachu D1, na niskich stelażach nie wyżej niż
  attyka. Wyłaz na dach 0,90 × 0,90 m z drabiną (W-065).
* **Energia pierwotna.** EP liczy moduł `lamela.obliczenia.fizyka_energia` z danych `energia` modelu na deklarowanych parametrach
  urządzeń (W-242). Szacunek panelu (J2) dla bazy W2 wynosił EP ≈ 55–59 kWh/(m²·rok), czyli ≤ 70 (W-240).

## 8. Zagospodarowanie działki

Działka nr 123/4 ma 32,00 × 50,00 m = 1600 m². Droga 1KDD przebiega od północy. Transformacja budynek → działka: p_d = p_b + (7,60; 32,70).
W układzie budynku granice to: W x = −7,60, E x = 24,40, S y = −32,70, droga y = 17,30. Nieprzekraczalna linia zabudowy biegnie
w **y = 11,30**, czyli 6,00 m od drogi.

**Odległości** (od lic zewnętrznych z ociepleniem, WT §12, W-001…W-006; komplet w bilansie §9):

| strona | element | odległość |
|---|---|---|
| W | ściany P0/P1 z oknami | 7,30 m |
| W | ściana P2 na wsporniku z oknem | 6,30 m |
| W | płyty PL-2/PL-3 | 5,20 m |
| W | okap PL-E | 5,80 m |
| W | taras T1 | 4,30 m |
| E | ściana wsch. garażu z drzwiami bocznymi | 5,725 m |
| E | bryły A i B | 12,10 m |
| E | jednostka zewnętrzna PC | 7,0 m |
| S | elewacja ogrodowa | 32,40 m |
| N (linia zabudowy) | daszek PL-DA | 0,95 m za linią |
| N (linia zabudowy) | brama garażu | 1,625 m za linią |

**Dojazd i parkowanie.**
* Brama przesuwna 5,60 m (odsuwana na wschód wewnątrz działki) i furtka 1,00 m w osi wejścia (W-017).
* Podjazd z kostki betonowej, szer. 6,375 m, dł. ≈ 7,6 m, ze spadkiem od garażu i odwodnieniem liniowym przed bramą garażu i przy bramie
  wjazdowej.
* **2 miejsca gościnne** 2,5 × 5,0 m na podjeździe (niezadaszone, ≥ 3 m od granicy E — W-015) i 2 w garażu, razem 4 (MPZP ≥ 2).

**Pozostałe elementy.**
* Dojście z płyt betonowych 1,30 m od furtki do podestu wejścia pod daszkiem.
* Osłona z lamel na 4 pojemniki przy furtce, z dostępem od ulicy (WT §23 ust. 4 — odległości nieokreślone, W-016).
* ZKP we wnęce ogrodzenia przy furtce (pole odczytowe ≥ 0,48 m), PWP przy wejściu (W-190).
* Przyłącza od ul. Lipowej:
  * woda PE 40, przykrycie ≥ 1,20 m, wodomierz w pom. 0.12;
  * kanalizacja PVC 160 ze studzienką SR1;
  * WLZ nN;
  * 2 × HDPE Ø40 ze światłowodem;
  * gazu nie przyłącza się (dom all-electric).

**Ogród.**
* Taras ogrodowy w kształcie litery L z deski kompozytowej pod okapami E (1,00 m) i zachodnim (1,50 m).
* Oś widokowa ogrodu kończy się lipą-soliterem; zachowano istniejącą brzozę i sosnę.
* Żywopłoty izolacyjne na granicach E, W i S.
* Retencja: szczelny zbiornik 5,0 m³ z pompą do podlewania i niecka chłonna 24 m² × 0,30 m w ogrodzie pd.
* Ogrodzenie od drogi ażurowe z grafitowych sztachet stalowych, h = 1,50 m (MPZP ≤ 1,60 m, bez prefabrykatów betonowych).

Obszar oddziaływania mieści się w całości na działce (W-012).

## 9. Bilans powierzchni i wskaźniki (generowany z modelu)

<!-- BILANS:START -->
*Blok generowany przez `tools/podglad_modelu.py` z `model/budynek.yaml` + `model/dzialka.yaml` — nie edytować ręcznie.*

| wskaźnik | wartość | wymaganie | ocena |
|---|---|---|---|
| PU wg RPB §20 / W-316 (bez klatek, garażu i techn.) | **240,24 m²** (P0 96,29, P1 84,39, P2 59,57) | 230–270 m² | ✓ |
| kontrolnie PN-ISO 9836 (rdzeń `lamela.model`, pipeline): podstawowa / pomocnicza z garażem / ruchu / techniczna | 158,78 / 78,58 / 43,85 / 16,24 m² („PU” rdzenia = podst. + pomocn. = 237,36 m² — z garażem, bez komunikacji) | — | — |
| garaż (osobno) / pom. techniczne (osobno) / klatki | 37,42 / 16,24 / 3,55 m² | — | — |
| strefa dzienna salon + jadalnia + kuchnia | 54,44 m² | ≥ 50 m² | ✓ |
| powierzchnia zabudowy (obrysy kondygnacji) | 187,50 m² (11,72 %); z płytami 212,99 m² | ≤ 480 m² (30 %) | ✓ |
| powierzchnia biologicznie czynna | 1 281,57 m² (80,10 %); rezerwa 50 % dachu zielonego 31,98 m² | ≥ 800 m² (50 %) | ✓ |
| intensywność zabudowy (Σ brutto kondygnacji / działka) | 0,248 | 0,05–0,80 | ✓ |
| kubatura brutto | 1 354,5 m³ | — (> 1000 m³ → PWP, W-190) | — |
| wysokość zabudowy (upzp): najwyższy punkt 10,000 − śr. teren -0,251 | **10,25 m** | ≤ 11,00 m (rezerwa → 10,70) | ✓ |
| wysokość budynku wg WT §6 (teren przy najniższym wejściu -0,326) | 9,85 m | grupa N ≤ 12 m | ✓ |
| kondygnacje nadziemne | 3 | ≤ 3 | ✓ |
| miejsca postojowe (garaż + podjazd) | 4 | ≥ 2 | ✓ |
| schody SCH1: 18 × h 0,175 / s 0,28; 2h+s; bieg | 2h+s = 0,630 m; bieg 1,150 / 1,145 m | h ≤ 0,19; 0,60–0,65; ≥ 1,00 (cel) | ✓ |
| schody SCH2: 18 × h 0,175 / s 0,28; 2h+s; bieg | 2h+s = 0,630 m; bieg 1,150 / 1,145 m | h ≤ 0,19; 0,60–0,65; ≥ 1,00 (cel) | ✓ |

**Odległości od granic działki i linii zabudowy** (lica zewnętrzne; WT §12: ściana z otworami ≥ 4,00 m, bez otworów ≥ 3,00 m; okapy/płyty ≥ 1,50 m — przyjęto ≥ 4,00 m):

| element | W | E | S | do linii zabudowy |
|---|---|---|---|---|
| ściany P0 (lico ocieplenia) | 7,30 | 5,72 | 32,40 | 1,62 |
| ściany P1 (lico ocieplenia) | 7,30 | 12,10 | 32,40 | 2,25 |
| ściany P2 (lico ocieplenia) | 6,30 | 12,10 | 32,40 | 2,25 |
| płyta PL-E | 5,80 | 10,60 | 31,40 | 6,17 |
| płyta PL-DA | 17,00 | 12,70 | 41,75 | 0,95 |
| płyta PL-C1 | 11,20 | 11,80 | 31,40 | 11,60 |
| płyta PL-C2 | 11,20 | 10,95 | 31,40 | 11,60 |
| płyta PL-2 | 5,20 | 11,80 | 31,40 | 5,87 |
| płyta PL-3 | 5,20 | 11,80 | 31,40 | 5,87 |
| płyta IZ-ST2Z | 6,30 | 24,70 | 32,40 | 5,87 |
| płyta SW1 | 13,60 | 16,00 | 40,15 | 2,65 |
| płyta WYL1 | 14,20 | 16,70 | 33,50 | 9,40 |
| taras T1 | 4,30 | 12,10 | 29,40 | 6,17 |
| taras T2 | 17,00 | 12,70 | 41,75 | 0,95 |
| taras T3 | 19,80 | 10,90 | 31,40 | 11,60 |
| jednostka zewn. PC | 23,80 | 7,00 | 31,05 | 11,75 |

**Okna / podłoga w pomieszczeniach na pobyt ludzi** (w świetle ościeżnic ≈ (szer − 0,14)(wys − 0,14); WT §57, W-080 ≥ 1/8):

| pomieszczenie | pow. [m²] | okna | A okien [m²] | stosunek | ocena |
|---|---|---|---|---|---|
| 0.06 Salon + jadalnia + kuchnia | 54,44 | O0-01, O0-02, O0-03, O0-04, O0-05, O0-11 | 33,83 | 1:1,6 | ✓ |
| 0.10 Pokój gościnny / gabinet | 12,52 | O0-12 | 2,26 | 1:5,5 | ✓ |
| 1.02 Pokój rodzinny / biblioteka (boks C) | 28,36 | O1-01, O1-02 | 11,21 | 1:2,5 | ✓ |
| 1.03 Pokój dziecka 1 | 13,19 | O1-06 | 2,26 | 1:5,8 | ✓ |
| 1.04 Pokój dziecka 2 | 12,52 | O1-05 | 2,26 | 1:5,5 | ✓ |
| 2.02 Sypialnia rodziców | 21,43 | O2-01, O2-04 | 9,52 | 1:2,3 | ✓ |
| 2.05 Gabinet / pokój | 16,32 | O2-03, O2-05 | 5,91 | 1:2,8 | ✓ |

**Wierność szkicowi** (krawędzie elewacji S od lica zach. bryły B; szkic: brief §1.1, 45,8 px/m):

| element | szkic [m] | model [m] | odchyłka [m] |
|---|---|---|---|
| A — bryła II p. (lamele) | -0,98 … 12,23 | -1,00 … 12,60 | 0,37 |
| A — płyty (dół/góra) | -2,40 … 12,55 | -2,10 … 12,90 | 0,35 |
| B — bryła I p. | 0,00 … 12,01 | 0,00 … 12,60 | 0,59 |
| C — boks (przeszklenie) | 4,48 … 11,68 | 4,40 … 11,42 | 0,26 |
| C — rama górna | 3,93 … 13,76 | 3,90 … 13,75 | 0,03 |
| D — linia pozioma | 3,82 … 19,00 | 3,90 … 18,98 | 0,08 |
| D — pion (narożnik G) | 19,17 … 19,17 | 18,98 … 18,98 | 0,20 |
| E — przeszklenie parteru | 0,98 … 13,21 | 0,60 … 13,55 | 0,38 |
| E — płyta dachu parteru | -1,53 … 14,08 | -1,50 … 14,10 | 0,03 |

**Zestawienie pomieszczeń** (PN-ISO 9836:2022; h — wysokość w świetle; zaliczenie 100/50/0 % wg W-316):

| nr | pomieszczenie | kategoria | pow. netto [m²] | h [m] | zaliczona [m²] |
|---|---|---|---|---|---|
| 0.01 | Wiatrołap | ruchu | 3,89 | 2,77 | 3,89 |
| 0.02 | Hol | ruchu | 4,44 | 2,77 | 4,44 |
| 0.03 | WC gościnne | pomocnicza | 2,32 | 2,77 | 2,32 |
| 0.04 | Klatka schodowa | ruchu | 2,82 | 2,77 | 2,82 |
| 0.05 | Spiżarnia (pod schodami) | pomocnicza | 5,40 | 1,90 | 2,70 |
| 0.06 | Salon + jadalnia + kuchnia | podstawowa | 54,44 | 2,77 | 54,44 |
| 0.07 | Pas komunikacyjny przy schodach | ruchu | 3,51 | 2,77 | 3,51 |
| 0.08 | Przedpokój gościnny | ruchu | 1,44 | 2,77 | 1,44 |
| 0.09 | Łazienka gościnna (natrysk) | pomocnicza | 3,84 | 2,77 | 3,84 |
| 0.10 | Pokój gościnny / gabinet | podstawowa | 12,52 | 2,77 | 12,52 |
| 0.11 | Przedsionek gospodarczy | ruchu | 7,18 | 2,76 | 7,18 |
| 0.12 | Pomieszczenie techniczne | techniczna | 8,85 | 2,76 | 8,85 |
| 0.13 | Garaż 2-stanowiskowy | pomocnicza | 37,42 | 2,76 | 37,42 |
| 1.01 | Hol | ruchu | 14,09 | 2,77 | 14,09 |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | podstawowa | 28,36 | 2,77 | 28,36 |
| 1.03 | Pokój dziecka 1 | podstawowa | 13,19 | 2,77 | 13,19 |
| 1.04 | Pokój dziecka 2 | podstawowa | 12,52 | 2,77 | 12,52 |
| 1.05 | Łazienka dzieci (wanna) | pomocnicza | 5,50 | 2,77 | 5,50 |
| 1.06 | Klatka schodowa | ruchu | 0,49 | 2,77 | 0,49 |
| 1.07 | WC z natryskiem | pomocnicza | 4,08 | 2,77 | 4,08 |
| 1.08 | Pralnia z suszarnią | pomocnicza | 6,64 | 2,77 | 6,64 |
| 2.01 | Hol | ruchu | 5,74 | 2,77 | 5,74 |
| 2.02 | Sypialnia rodziców | podstawowa | 21,43 | 2,77 | 21,43 |
| 2.03 | Garderoba (przedpokój apartamentu) | pomocnicza | 10,57 | 2,77 | 10,57 |
| 2.04 | Łazienka rodziców | pomocnicza | 5,51 | 2,77 | 5,51 |
| 2.05 | Gabinet / pokój | podstawowa | 16,32 | 2,77 | 16,32 |
| 2.06 | Klatka schodowa (wyjście z biegu 2, pustka) | ruchu | 0,24 | 2,77 | 0,24 |
| 2.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | techniczna | 6,05 | 2,77 | 6,05 |
| 0.14 | Szacht instalacyjny SI | techniczna | 0,45 | 2,77 | 0,45 |
| 1.09 | Szacht instalacyjny SI | techniczna | 0,45 | 2,77 | 0,45 |
| 2.08 | Szacht instalacyjny SI | techniczna | 0,45 | 2,77 | 0,45 |
<!-- BILANS:END -->

## 9a. Kontrola spójności modelu — iteracje

Model zweryfikowano podglądem (`final/*.png`), arkuszami PB (`projekt/01_koncepcja/widoki`), pipeline'em 3D oraz modułem fizyki
(`energia.obudowa`: ciągłość warstw i sąsiedztwo przegród). Poprawki wprowadzone w kolejnych iteracjach:
1. **Iteracja 1 (rzuty, elewacje):**
   * artefakt naroża P2 (lico −1,42 zamiast −1,30) usunięto: oś A' = −1,00, a ściana SZL ma wełnę fasadową 18 cm, więc jej lico zewnętrzne
     jest 0,30 m od osi, jak w SZ2;
   * wspornik bryły A ma teraz 1,00 m w osi i lico–lico.
2. **Iteracja 2 (ciągłość „4 linii”, moduł fizyki):**
   * warstwę szczelności powietrznej oznaczono w SZ1, SZ2 i SZL; w SZL usunięto warstwę instalacyjną po ciepłej stronie OSB;
   * pod wspornikiem dodano wiatroizolację (SUF-ZEW);
   * folię PE pod XPS oznaczono jako warstwę rozdzielającą (nie paroizolację);
   * szacht SI dostał przestrzeń techniczną na każdej kondygnacji, bo inaczej moduł fizyki traktował go jak powietrze zewnętrzne;
   * ściany P2 w osiach C i D podzielono w węźle ścianki S2-15;
   * granicę hol/klatka na P1 przesunięto do lica osi 3;
   * ścianę spiżarni pod schodami zmieniono na silikat 18.

   Wynik: walidacja 0 błędów i 0 ostrzeżeń, audyt ciągłości warstw bez uwag.
3. **Podgląd** liczy PU wg W-316, odległości od granic, wysokości (upzp i WT §6), okna/podłogę i wierność szkicowi.
   Wyniki wstawia do §9.

## 10. Odstępstwa, ryzyka i dalsze kroki

* **Świadome odstępstwa od szkicu:**
  * bryła B ma 12,60 m w licach zamiast ≈ 12,0 m: moduł osi 12,00 m + ETICS, ściany w pionie;
  * przeszklenie E zaczyna się ≈ 0,4 m bliżej zachodu niż w szkicu, bo słup narożny i ściana A są w osi A.
* **Wspornik bryły A.** Belki B4/B5 w licach ścian P2 wymagają w PT obliczenia EQU, ugięć (z pełzaniem) i drgań. Wymagają też ciągłości
  zbrojenia z wieńcem ST2 oraz koordynacji z oknami P2 (parapety +6,90 ponad belkami). Zalecane dobrowolne sprawdzenie PT-BO (W-275).
* **Belka B1 i słupy fasady E.** Wymagają obliczenia ramy i sztywności w kierunku x razem z trzonem ŻB oraz sprawdzenia przebicia pogrubień
  płyty. Ugięcie ≤ L/500 nad stolarką.
* **Lamele P2** a przesłanianie (WT §13). Traktujemy je jako osłonę okna, nie obiekt przesłaniający; potwierdzić przy PAB. Wymóg 1/8
  spełniony z zapasem.
* **Stan prawny.** Wymagane oświadczenie z art. 102a PB. Wniosek o pozwolenie na budowę najpóźniej 19.03.2028 (W-A.1).
* **Dalej:**
  * katalog mostków z sekcji `wezly` (`tools/katalog_mostkow.py`);
  * obliczenia fizyki i EP, instalacji i konstrukcji z modelu;
  * opinia geotechniczna;
  * warunki przyłączenia;
  * DTR pompy ciepła (hałas, strefa R290);
  * dobór stolarki i łączników z ETA.

## 11. Pliki

* `tools/buduj_model.py` — skrypt parametryczny, który generuje `model/budynek.yaml`, `model/dzialka.yaml`, `model/wyposazenie.yaml`
  i `model/instalacje.yaml`.
* Walidacja: `PYTHONPATH=src python3 -m lamela.model model/budynek.yaml model/dzialka.yaml` (0 błędów, 0 ostrzeżeń).
* `tools/podglad_modelu.py` → `docs/20_koncepcja/final/`:
  * rzuty P0–P2 (`rzut_P0…P2.png`) i rzut dachów z odwodnieniem (`rzut_dachu.png`);
  * elewacje S/N/E/W (`elewacja_S/N/E/W.png`, zbiorczo `elewacje.png`);
  * elewacja S na tle szkicu;
  * przekroje A-A i B-B;
  * działka;
  * `bilans.md` / `bilans.json`.
* `tools/generuj_widoki.py` → `projekt/01_koncepcja/widoki/`: arkusze PB-AR-01…10 (DXF, PDF, PNG) i tom PDF.
* `lamela.pipeline` → `projekt/07_model_3D/wstepne/`: model glTF/OBJ, wskaźniki, walidacja.
* Oceny panelu: `docs/20_koncepcja/ocena_J1.md`, `ocena_J2.md`, `ocena_J3.md`; warianty: `docs/20_koncepcja/W1…W3/`.

## 12. Weryfikacja niezależna i podglądy 3D

Szczegóły są w `docs/20_koncepcja/weryfikacja_koncepcji.md`. Weryfikację wykonano na tym samym stanie modelu co bilans §9
(`budynek.yaml` SHA-256 `d238ec0e…`).

**Wskaźniki zgodne z §9:**
* PU wg W-316: 240,24 m²; przy geometrycznym ważeniu wysokości spiżarni pod schodami 239,26 m²;
* powierzchnia zabudowy: 187,50 m²;
* intensywność zabudowy: 0,248;
* kubatura: 1 354,5 m³;
* wysokość zabudowy: 10,25 m z czerpnią i wyrzutnią dachową, 10,02 m do attyki;
* EP z modułu fizyki: 57,2 kWh/(m²·rok) ≤ 70.

PBC wychodzi 1 271,31 m² (79,5 %) wobec 1 281,57 m² w §9 — różnica wynika z metody liczenia.

**Główne niezgodności do poprawy:**
* wyrzutnia tylko 0,05 m nad czerpnią (W-167); jej podniesienie przekroczyłoby wysokość 11,0 m z MPZP;
* spadki terenu od budynku < 2 % (W-019);
* dno przelewów awaryjnych D1 poniżej pokrycia (W-142);
* PV 0,05 m ponad attyką (W-033);
* cokół 0,14 m przy drzwiach DZ2;
* U_w doświetla FX3 = 1,0.

**Nowe podglądy w `final/`:**
* `arkusz_01…10_*.png` — arkusze PB-AR-01…10, 1:50, 170 dpi;
* `pzt_koncepcja.png`;
* `3D_aksonometria_rozwarstwiona.png`, `3D_widok_lotniczy_SE.png`, `3D_widok_od_ulicy_N.png`.
