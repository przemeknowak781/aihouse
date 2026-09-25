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
* **E — parter:** ciągłe przeszklenie strefy dziennej w 5 kwaterach o narastającym rytmie 1,90 / 1,90 / 2,335 / 2,335 / 2,93 m (przeszczep z W3).
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
| J2 (z W3) | słupy E w osiach ramy C (jedna linia pionowa) | SL3/SL4 (x 6,435 / 8,77) = SL5/SL6 boksu C; kwatery 1,90/1,90/2,335/2,335/2,93 |
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
