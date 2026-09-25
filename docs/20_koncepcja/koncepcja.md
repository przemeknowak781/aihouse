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
* **D — linia pozioma:** pas dolny ramy C (+3,65…+3,85) przechodzi w **głęboką krawędź PL-D** (wysunięcie 1,00 m, +3,65…+3,85, lekka
  rama stalowa w okładzinie na konsolach punktowych) biegnącą nad pasem gospodarczym do narożnika garażu, na wysokości korony attyki
  zielonego dachu D4. Kończy się narożnikiem garażu **18,975 m** od lica zachodniego bryły B (szkic ≈ 19,0 m); linia jest ciągła także
  w 3D i w perspektywie (poprawka po audycie A2, I-8). **Nie jest tarasem:** dach garażu jest ekstensywny i nieużytkowy, bez
  wyjścia i bez wiaty (decyzja Inwestora 2).
* **G — garaż 2-stanowiskowy:** w bryle parteru, **w licu ogrodowym** (przeszczep J3/W1). W świetle ma 6,05 × 6,175 m. Brama od północy.
* **E — parter:** ciągłe przeszklenie strefy dziennej w 5 kwaterach o narastającym rytmie 1,90 / 1,90 / 2,34 / 2,34 / 2,92 m (przeszczep z W3).
  Szósta kwatera to przeszklone drzwi gospodarcze w tym samym systemie, więc pas E czyta się na ok. 12,85 m. Nad nim płyta-okap E wystaje
  1,00 m na południe i 1,50 m na zachód (PL-E, +2,70…+3,00 — wierzch równy ze stropem ST1).
  Kwatery szklone są osadzone między licami słupów RK 120 (w świetle 1,78 / 1,78 / 2,22 / 2,22 / 2,86 m, wysokość 2,78 m do spodu B1).

Porównanie krawędzi z modelu z odczytem szkicu (brief §1.1, 45,8 px/m; x liczone od lica zach. bryły B):

| element | szkic [m] | model [m] | uwagi |
|---|---|---|---|
| A — bryła II p. | −0,98 … +12,23 | −1,00 … +12,60 | wspornik 1,00 m jak w szkicu; wsch. koniec w licu B (ściany w pionie) |
| A — płyty | −2,40 … +12,55 | −2,10 … +12,90 | okap 1,10 m zach., 1,00 m pd., 0,30 m wsch. |
| B — bryła I p. | 0 … +12,01 | 0 … +12,60 | +0,6 m: moduł osi 12,00 m + ETICS (odstępstwo świadome) |
| C — boks (szkło) | +4,48 … +11,68 | +4,40 … +11,42 | 3 kwatery między słupkami SL5/SL6 (2,29 / 2,24 / 2,29 m) |
| C — rama górna | +3,93 … +13,76 | +3,90 … +13,75 | przedłużona na wschód (przeszczep z W1) |
| D — linia | +3,82 … +19,00 | +3,90 … +18,975 | jedna ciągła głęboka krawędź PL-C1 + PL-D (+3,85) do narożnika G |
| E — przeszklenie | +0,98 … +13,21 | +0,60 … +13,45 | z drzwiami gospodarczymi w systemie fasady |
| E — płyta | −1,53 … +14,08 | −1,50 … +14,10 | okap zach. 1,50 m |

Graficzne porównanie z odchyłkami liczonymi przez skrypt jest w `final/elewacja_S_szkic.png`. Proporcje pionowe szkicu są umowne,
bo wysokości kondygnacji wynikają z WT. Zachowano kolejność pasm:
* okap E +2,70…+3,00;
* linia D +3,65…+3,85;
* boks C +3,85…+5,35;
* rama górna +5,35…+5,55;
* płyta A +5,85…+6,15 (z obudową czoła i podsufitką wspornika do +5,67 na zachodzie);
* lamele +6,15…+8,98;
* krawędź stropodachu PL-3 +8,98…+9,30, attyka +9,776.

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
* spiżarnia 0.05 pod górnym odcinkiem biegu 2 (h ≥ 2,20; wejście od strony strefy dziennej), dalej bez ścianki schowek pod schodami
  0.15 (h 1,40–2,20, PU 50 %) i schowek pod spocznikiem 0.16 (h < 1,40, poza PU) — podział wg audytu A1;
* przedpokój gościnny 0.08 → pokój gościnny/gabinet 0.10 (12,5 m², okno zach.) i łazienka gościnna 0.09 z natryskiem (drzwi przesuwne
  **chowane w kasecie** ścianki GK S0-19, światło 0,80 m — w przedpokoju nie ma skrzydła; poprawka A2 I-7);
* przedsionek gospodarczy 0.11:
  * wejście z garażu drzwiami szczelnymi z samozamykaczem;
  * drzwi do kuchni przy fasadzie, droga auto → kuchnia ≈ 6 m;
  * drzwi przeszklone do ogrodu;
  * wejście do pomieszczenia technicznego 0.12 (8,85 m², **dostęp z domu** — poprawka J2);
* garaż 0.13 (6,05 × 6,175 m w świetle, nieogrzewany):
  * brama segmentowa 5,00 × 2,25 m;
  * drzwi boczne od wschodu;
  * stanowiska 2,50 × 5,90 m (MP1 0,30 m od ściany osi E, MP2 0,30 m od szafy); płytka szafa 0,40 m na rowery i sprzęt ogrodowy przy
    ścianie osi F, poza prowadnicami bramy;
  * posadzka −0,05 przy drzwiach do domu → −0,10 przy bramie (spadek 0,8 %), próg dom–garaż 5 cm (W-114).

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
* bieg 1,135 / 1,130 m między licami; szerokość użytkowa przy jednym pochwycie ciągłym Ø42 wokół ściany środkowej ≈ 1,04 m ≥ 1,00;
* spocznik 2,415 × 1,175 m;
* prześwit nad biegiem ≈ 2,75 m;
* klatka obudowana ścianami C/D i ścianą środkową ŻB 15 (SCZB15, ciągła P0–P2), więc bez otwartych krawędzi;
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
| J1, J2, J3 | drzwi ≥ 0,90 × 2,10 w murze; łazienki/WC na zewnątrz lub przesuwne; wejście ≥ 1,10 × 2,15 | symbole D1/D2/D1P/D4/D4A 0,90 × 2,10; O0-14 przesuwne naścienne (D1P), O0-16 skrzydłowe D2 na zewnątrz (runda 2, A3 I-3); O0-19, O1-10, O1-11, O2-10 na zewnątrz; DZ1 1,10 × 2,40 |
| J1 | schody: szerokość użytkowa ≥ 1,00 m | biegi 1,15 / 1,145 m, jeden pochwyt ciągły (BL1, BL2) → ≈ 1,05 m |
| J1, J2 | PC monoblok R290, ≥ 6,0 m od granicy E, strefa 1,0 m, ekran, L_Aeq,N ≤ 40 (cel 35) dB | jednostka przy ścianie pd. pasa gospodarczego, 7,0 m od granicy E (PC-JZ w `dzialka.yaml`); strefa R290 bez okien/drzwi/wpustów; osłona lamelowa z ekranem od tarasu; szacunek hałasu §7 |
| J1, J2 (z W3) | retencja: szczelny zbiornik ≤ 5 m³ + niecka ≈ 24 m² (W-145) | zbiornik 5,0 m³ + niecka NCH-1 24 m² × 0,30 m w ogrodzie pd., ≥ 3 m od fundamentów, ≥ 2 m od granic |
| J1, J2, J3 | PU wg RPB §20 / W-316 bez klatek, garaż i techniczne osobno | bilans §9 (podgląd liczy wg W-316; spiżarnia pod biegiem w 50 %) |
| J1 (z W3) | stopa schodów dostępna z holu bez strefy mebli | pas komunikacyjny 0.07 + ekran z lamel LAM-P0 (h 2,10) |
| J1 (z W3) | szklana przegroda wiatrołap/hol, doświetle drzwi | ścianka SGL S0-21 z drzwiami DS1 w osi wejścia; FX3 |
| J1 (z W1) | kuchnia z ciągłą zabudową; drzwi przedsionek → kuchnia przy fasadzie | O0-21 w S0-15 na y 0,25–1,15; blaty y 1,30–5,02 + wyspa |
| J1 | pralnia ≈ 6,5 m²; zysk dla łazienki/pokoju | pralnia 1.08 ≈ 6,6 m² + WC z natryskiem 1.07 (drugi punkt sanitarny P1) |
| J1 | czerpnia W-166, wyrzutnia W-167 | czerpnia (11,60; 1,00; +10,00) i wyrzutnia (1,90; 4,00; +10,00): ≥ 0,40 m nad lokalnym pokryciem z klinem, **10,15 m od siebie (≥ 10,00 m, WT §152 ust. 10)**, czerpnia 7,96 m od wywiewki K1, wyrzutnia ≥ 3 m od krawędzi dachu nad oknami (`energia.wentylacja`; poprawione po audycie A1 — wcześniej błędnie „≥ 6 m od siebie”) |
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
  Nad wejściem na schody i nad wyjściem z nich płyty podpierają podciągi B8/B9 25 × 50 w osi 3 (C–D). Stropodach D1 ma w tym miejscu
  podciąg **B10 25 × 50** (spód +8,80) oparty na ścianach S2-10 i S2-04 — na P2 oś 3 jest przerwana między x 7,19 a 8,50 (wyjście z biegu 2),
  a ścianki S2-13/S2-14 są działowe (poprawka A2 I-1). Płyty ST1, ST2 i D1 kończą się na licu warstwy konstrukcyjnej ścian (±0,09 od osi);
  ETICS/wełna ścian przechodzi ciągle przed czołami płyt i attyk (A2 K-1).
* **Fasada E na parterze.** Belka odwrócona **B1 18 × 107 cm** (w licu muru, bez wejścia w ETICS) (+2,78…+3,85, tworzy pas podokienny boksu C) leży na słupach RK 120×120×8
  SL1–SL4 w szprosach przeszklenia oraz na ścianach A i E. Przęsła mają ≤ 3,23 m. B1 niesie ścianę pd. P1 i P2 i pas trzech stropów.
  **Słupki boksu C SL5/SL6 stoją w jednej linii pionowej ze słupami SL3/SL4**, więc siły skupione nadproża B2 (18 × 80) trafiają nad podpory B1.
  Słupy stoją w filarkach 0,12 m między kwaterami szklonymi (fasada słupowo-ryglowa), a otwory E sięgają spodu B1 (+2,78) — bez pasa muru
  nad szkłem (A2 I-6).
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
* **Płyty wysunięte ≤ 1,50 m** (PL-E, PL-DA, PL-2, PL-3) są na łącznikach termoizolacyjnych z ETA (W-272) w płaszczyźnie ocieplenia ściany
  (pas −0,30…−0,09); wierzch płyty wysuniętej jest równy wierzchowi stropu (+3,00 / +6,15 / +9,30), a „gruba krawędź” 0,30–0,32 m powstaje
  od spodu — łącznik bez uskoku, spadek 2 % od budynku bez progu (A2 I-4). **Pas zachodni PL-2/PL-3** (1,10 m na belce B3 opartej na końcach
  wsporników B4/B5, łączny wysięg od osi A 2,40 m): szacunek EQU — moment wywracający od B3 (ściana A' ≈ 3,2 kN/m, pas PL 1,10 m ≈ 9 kN/m,
  połowa ST2Z ≈ 2,8 kN/m, obciążenia zmienne) ≈ 1,1·50 + 1,5·8 ≈ 70 kNm na belkę, moment utrzymujący przęsła zakotwienia A–B (ściany P2,
  ST3, ST2 ≈ 35 kN/m × 3,875 m × 1,94 m) · 0,9 ≈ 235 kNm; ugięcie końca PL (l/d ≈ 3,7) i B4/B5 (l/d ≈ 1,3) ≪ l/125 — do wykazania w PT
  (W-262, W-268), skrócenia pasa nie wprowadzono (A2 D-12). Rama C to lekki ruszt stalowy
  w okładzinie na konsolach punktowych. Nad stolarką pod krawędziami okapu E i ramy C przewidziano szczelinę dylatacyjną.
* **Usztywnienie.** Ściany w obu kierunkach i stropy jako tarcze. Przy przeszklonej fasadzie pd. parteru sztywność w kierunku x daje trzon
  klatki z **żelbetowymi ścianami C i D na P0** (SWZB, poprawka J2) razem ze ścianami osi 3 i 4.
* **Schody.** Płyty biegów ŻB 18 cm: dolny koniec na stropie/podciągu osi 3 (B8/B9/B10), górny na płycie spocznika; spocznik na ścianach
  C/D i **ścianie środkowej ŻB 15 cm** (SCZB15), monolitycznej z płytami biegów, ciągłej P0–P2 przez poziomy stropów i zakotwionej
  w podciągach osi 3 — zamiast ścianki silikatowej 12 cm o wysokości 9,3 m z wolnym końcem (A2 I-2). Stopnie dębowe.
* **Dach garażu D4 przy ścianie osi E.** Obrys D4 zaczyna się od lica ocieplenia ściany P1 (x 12,30); płyta D4 łączy się z wieńcem ściany E
  i płytą ST1 łącznikiem termoizolacyjnym w płaszczyźnie ETICS ściany P1 (pas 12,09–12,30) — podparcie D4 na ścianie E przez łącznik (PT).

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

Garaż stoi na tej samej płycie. Jego posadzka ma spadek 0,8 % do bramy: −0,05 przy drzwiach O0-22, −0,10 przy bramie, próg dom–garaż
5 cm ≥ 3 cm (W-114; audyt A1). Zakres badań podłoża: opinia geotechniczna,
≥ 3 sondowania CPT/DPL do ≥ 6 m, projekt geotechniczny (W-281/W-282).

## 6. Materiały, przegrody, fizyka budowli i woda

Przegrody mają pełne warstwy w `przegrody`, a materiały opisują λ, ρ, c_p i μ lub sd ze źródłem w polu `zrodlo` (PN-EN ISO 10456, PN-EN 1745,
DWU typowych wyrobów „lub równoważne”). U — wartości OBLICZONE modułem fizyki (PN-EN ISO 6946 z poprawkami ΔU, klin zał. C; podłoga
PN-EN ISO 13370) — runda 2 (weryfikacja §6 C8); nazwy przegród w modelu podają te same wartości.

| kod | przegroda | U [W/(m²K)] | wymaganie |
|---|---|---|---|
| SZ1 | silikat 18 + ETICS EPS 031 20 cm | 0,17 | ≤ 0,20 (W-243); cel 0,15 (W-245) nieosiągnięty — patrz §14.2 |
| SZ2 | P2 za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV, szczelina wentylowana, lamele | 0,17 | ≤ 0,20 |
| SZL | ściana lekka A' na wsporniku: szkielet KVH z wełną, OSB (szczelność), DWD, wełna fasadowa 18 cm | 0,099 | ≤ 0,20 |
| SWG | ściana dom–garaż: silikat 18 + wełna 12 cm od garażu | 0,27 | ≤ 0,30 |
| SD1 | stropodach bryły A: TPO, PIR spadkowy 12–32 cm, paroizolacja z Al, ŻB 22 | 0,11 | ≤ 0,15 |
| SD2 | dachy nad P1: żwir, TPO, PIR 14–26 cm, paroizolacja, ŻB 22 | 0,12 | ≤ 0,15 |
| DZ1 | dach zielony ekstensywny garażu i pasa gosp.: substrat 8 cm, geowłóknina, mata drenażowa, bariera przeciwkorzenna, 2 × papa SBS, PIR 12–24 cm, paroizolacja, ŻB 24 | 0,13 | ≤ 0,15 nad pasem ogrzewanym |
| POD-0 | płyta fundamentowa: posadzka, jastrych z ogrzewaniem, EPS 6,5 cm, membrana SBS, ŻB 25, XPS 20 cm | 0,11 (U_equiv) | ≤ 0,30 |
| POD-1 | strop międzykondygnacyjny: deska/gres, jastrych z wężownicą, EPS 100 + EPS T | — | akustyka R'w, L'n,w (W-230) |
| SUF-ZEW | spód stropu nad powietrzem (wspornik A): wełna 20 cm + podsufitka wentylowana | 0,13 | ≤ 0,15 |
| AT1 | attyka ŻB 18 w osi muru, izolowana z 3 stron (PIR 10 cm od dachu, ETICS/wełna ściany ciągła od zewnątrz, PIR na koronie) | — | f_Rsi ≥ 0,72 (W-248) |

**Zasada „4 linii”** (brief §9.1) jest ciągła wokół całej obudowy ogrzewanej:
* **izolacja:** XPS pod płytą → XPS cokołu → ETICS / wełna fasadowa (ciągła przed czołami stropów i attyk — płyty kończą się na licu
  konstrukcji) → PIR na attykach i dachach → wełna pod wspornikiem A (z pustką i jedną płaską podsufitką PS-A +5,67 pod wspornikiem i pasem
  zach. PL-2, czoło obudowane — A2 I-5); płyty wysunięte przechodzą przez nią tylko łącznikami z ETA; garaż jest buforem wewnątrz ciągłego
  ETICS parteru;
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
Woda z posadzki garażu i podjazdu (odwodnienia OL-1, OL-4 — możliwe węglowodory) **nie trafia do zbiornika**: przez osadnik z separatorem
SEP-1 (PN-EN 858) odpływa do niecki trawiastej NT-E (audyt A1).

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

  Jednostka zewnętrzna stoi przy ścianie pd. pasa gospodarczego, **7,0 m od granicy E**, w osłonie lamelowej z ekranem od tarasu, pod
  okapem linii D (PL-D). **Odstępstwo od założenia „jednostka od N/E” (uzasadnienie, audyt A1/A2 D-11):** od północy jest wjazd, wejście
  i strefa ZKP/przyłączy (brak miejsca ≥ 1,0 m strefy R290 poza dojściami), a wariant od wschodu (przy ścianie wsch. pom. 0.12) daje
  ≈ 4,8 m od granicy E — ≥ 3,0 m, ale < 6,0 m wymaganego w W-024 dla hałasu na granicy MN. Stanowisko pd. jest 7,0 m od granicy E, ≥ 3 m
  od sypialni (brak okien sypialni nad jednostką — P1 nad nią to ściana wsch. pokoju rodzinnego bez okna od pd.), a od tarasów T1/T3
  i drzwi O0-06 oddziela je ekran akustyczny (płyta z wełną, h ≥ 1,5 m, strona zach.). Szacunek na tarasie T3 (r ≈ 3 m, Q = 2, ekran
  −10 dB): ≈ 55 + 10·log(2/(4π·9)) − 10 ≈ 33 dB(A); na tarasie T1 (r ≥ 5 m) < 33 dB(A). Na granicy E (niżej) ≈ 33 dB(A) ≤ 40 dB noc.
  Elewacja ogrodowa G (S0-02): zielona ściana z pnączy na kratownicy stalowej odsuniętej od ETICS i ażurowa osłona z lamel wokół
  jednostki (decyzja Inwestora K-13 — §15), pod okapem PL-D. Strefa R290
  1,0 m jest wolna od otworów, wpustów i studzienek (W-156). Skropliny odprowadza studnia chłonna ≥ 0,8 m p.p.t. Szacunek hałasu:
  L_WA ≈ 55 dB(A), Q = 4, r ≈ 7 m → L_p ≈ 55 + 10·log(4/(4π·7²)) ≈ 33 dB(A) na granicy. To mniej niż 40 dB (noc) i mniej niż cel 35 dB
  (W-024); w PT potwierdzić DTR wyrobu.
* **Wentylacja mechaniczna z odzyskiem ciepła.** Centrala ≈ 450 m³/h (η ≈ 0,85) stoi na P2 w pomieszczeniu 2.07 (frontem serwisowym na
  wschód, drzwi otwierane do holu, wyłaz przesunięty na x 7,20–8,10). Czerpnia i wyrzutnia są dachowe (W-166/W-167, WT §152 — wydanie, §15):
  **czerpnia na dachu D3** (pole wsch. nad P1, `energia.wentylacja.czerpnia`), dolna krawędź wlotu ≥ 0,40 m nad powierzchnią dachu
  (ust. 4), ≥ 6 m od wywiewki K1; **wyrzutnia na D1 z wylotem pionowym** (1,90; 4,00), ≥ 0,40 m nad lokalnym pokryciem z klinem,
  3,00 m od krawędzi konstrukcji dachu nad oknem O2-04 (ust. 12); czerpnia–wyrzutnia ≥ 6 m i wyrzutnia ≥ 1,0 m ponad czerpnią (ust. 10
  w brzmieniu dosłownym); ust. 7 (0,4 m nad linią najwyższych punktów w promieniu 10 m) dotyczy wylotu poziomego — nie ma zastosowania.
  Maks. wysokości urządzeń (`czerpnia_z_top`, `wyrzutnia_z_top`) wchodzą do wysokości zabudowy (`lamela.wskazniki`). Świetlik SW1
  jest **stały, nieotwierany i bez funkcji wentylacyjnej**; wymóg WT §152 ust. 12–13 (wylot ≥ 1 m nad górną krawędzią okna w odległości
  3–10 m) odnosimy do okien otwieranych, przez które powietrze wyrzucane mogłoby wrócić do budynku — interpretację potwierdzić
  w uzgodnieniu z rzeczoznawcą ds. sanitarnohigienicznych. Kanały biegną pionowo w szachcie SI, poziomo w sufitach podwieszanych holi i łazienek. Wywiew wg PN-83/B-03430/Az3
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
| W | płyty PL-2/PL-3 i obudowa czoła OB-A | 5,20 / 5,18 m |
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
  Stanowiska w garażu 2,50 × 5,90 m: MP1 x_dz 20,12–22,62, MP2 x_dz 22,67–25,17 (dłuższe krawędzie ≥ 0,30 m od ścian i szafy — WT §104,
  W-112; audyt A1).

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
| PU wg RPB §20 / W-316 (bez klatek, garażu i techn.) | **239,13 m²** (P0 95,33, P1 84,39, P2 59,42) | 230–270 m² | ✓ |
| kontrolnie PN-ISO 9836 (rdzeń `lamela.model`, pipeline): podstawowa / pomocnicza z garażem / ruchu / techniczna | 158,70 / 77,55 / 43,81 / 16,10 m² („PU” rdzenia = podst. + pomocn. = 236,25 m² — z garażem, bez komunikacji) | — | — |
| garaż (osobno) / pom. techniczne (osobno) / klatki | 37,42 / 16,10 / 3,51 m² | — | — |
| strefa dzienna salon + jadalnia + kuchnia | 54,44 m² | ≥ 50 m² | ✓ |
| powierzchnia zabudowy (obrysy kondygnacji) | 187,50 m² (11,72 %); z płytami 218,08 m² | ≤ 480 m² (30 %) | ✓ |
| powierzchnia biologicznie czynna | 1 270,15 m² (79,38 %); rezerwa 50 % dachu zielonego 29,53 m² | ≥ 800 m² (50 %) | ✓ |
| intensywność zabudowy (Σ brutto kondygnacji / działka) | 0,248 | 0,05–0,80 | ✓ |
| kubatura brutto | 1 354,5 m³ | — (> 1000 m³ → PWP, W-190) | — |
| wysokość zabudowy (upzp art. 2 pkt 30 lit. a; `lamela.wskazniki`): najwyższy punkt 10,000 (czerpnia wentylacji (dachowa)) − średnia z min./maks. terenu na obwodzie (-0,360 / -0,175 → -0,267; niższa z rzędnych istn./proj. — D-15); informacyjnie od t_min: 10,36 m | **10,27 m** | ≤ 11,00 m (rezerwa → 10,70) | ✓ |
| wysokość budynku wg WT §6 (`lamela.wskazniki`): do najwyższego punktu pokrycia z klinem 9,626 − teren przy najniższym wejściu O0-03 -0,348 | 9,97 m | grupa N ≤ 12 m | ✓ |
| kondygnacje nadziemne | 3 | ≤ 3 | ✓ |
| miejsca postojowe (garaż + podjazd) | 4 | ≥ 2 | ✓ |
| schody SCH1: 18 × h 0,175 / s 0,28; 2h+s; bieg | 2h+s = 0,630 m; bieg 1,135 / 1,130 m | h ≤ 0,19; 0,60–0,65; ≥ 1,00 (cel) | ✓ |
| schody SCH2: 18 × h 0,175 / s 0,28; 2h+s; bieg | 2h+s = 0,630 m; bieg 1,135 / 1,130 m | h ≤ 0,19; 0,60–0,65; ≥ 1,00 (cel) | ✓ |

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
| płyta PS-A | 5,20 | 24,70 | 31,40 | 5,87 |
| płyta OB-A | 5,18 | 24,70 | 31,38 | 5,85 |
| płyta OB-A2 | 7,30 | 24,68 | 31,40 | 11,60 |
| płyta SW1 | 13,60 | 16,10 | 40,05 | 2,75 |
| płyta WYL1 | 14,70 | 16,20 | 33,50 | 9,40 |
| płyta PL-D | 20,20 | 5,72 | 31,40 | 11,60 |
| taras T1 | 4,30 | 12,10 | 29,40 | 6,17 |
| taras T2 | 17,40 | 12,70 | 41,75 | 0,95 |
| taras T3 | 19,80 | 10,90 | 31,40 | 11,60 |
| jednostka zewn. PC | 23,80 | 7,00 | 31,05 | 11,75 |

**Okna / podłoga w pomieszczeniach na pobyt ludzi** (w świetle ościeżnic ≈ (szer − 0,14)(wys − 0,14); WT §57, W-080 ≥ 1/8):

| pomieszczenie | pow. [m²] | okna | A okien [m²] | stosunek | ocena |
|---|---|---|---|---|---|
| 0.06 Salon + jadalnia + kuchnia | 54,44 | O0-01, O0-02, O0-03, O0-04, O0-05, O0-11 | 32,79 | 1:1,7 | ✓ |
| 0.10 Pokój gościnny / gabinet | 12,52 | O0-12 | 2,26 | 1:5,5 | ✓ |
| 1.02 Pokój rodzinny / biblioteka (boks C) | 28,36 | O1-01, O1-13, O1-14, O1-02 | 10,55 | 1:2,7 | ✓ |
| 1.03 Pokój dziecka 1 | 13,19 | O1-06 | 2,26 | 1:5,8 | ✓ |
| 1.04 Pokój dziecka 2 | 12,52 | O1-05 | 2,26 | 1:5,5 | ✓ |
| 2.02 Sypialnia rodziców | 21,43 | O2-01, O2-04 | 9,52 | 1:2,3 | ✓ |
| 2.05 Gabinet / pokój gościnny okazjonalny | 16,25 | O2-03, O2-05 | 5,91 | 1:2,7 | ✓ |

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
| E — przeszklenie parteru | 0,98 … 13,21 | 0,66 … 13,55 | 0,34 |
| E — płyta dachu parteru | -1,53 … 14,08 | -1,50 … 14,10 | 0,03 |

**Zestawienie pomieszczeń** (PN-ISO 9836:2022; h — wysokość w świetle; zaliczenie 100/50/0 % wg W-316):

| nr | pomieszczenie | kategoria | pow. netto [m²] | h [m] | zaliczona [m²] |
|---|---|---|---|---|---|
| 0.01 | Wiatrołap | ruchu | 3,89 | 2,77 | 3,89 |
| 0.02 | Hol | ruchu | 4,44 | 2,77 | 4,44 |
| 0.03 | WC gościnne | pomocnicza | 2,32 | 2,77 | 2,32 |
| 0.04 | Klatka schodowa | ruchu | 2,78 | 2,77 | 2,78 |
| 0.05 | Spiżarnia | pomocnicza | 1,02 | 2,77 | 1,02 |
| 0.15 | Schowek pod schodami (h 1,40–2,20) | pomocnicza | 1,45 | 1,80 | 0,72 |
| 0.16 | Schowek pod spocznikiem (h < 1,40) | pomocnicza | 2,91 | 1,37 | 0,00 |
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
| 2.03 | Garderoba (przedpokój apartamentu) | pomocnicza | 10,49 | 2,77 | 10,49 |
| 2.04 | Łazienka rodziców | pomocnicza | 5,51 | 2,77 | 5,51 |
| 2.05 | Gabinet / pokój gościnny okazjonalny | podstawowa | 16,25 | 2,77 | 16,25 |
| 2.06 | Klatka schodowa (wyjście z biegu 2, pustka) | ruchu | 0,24 | 2,77 | 0,24 |
| 2.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | techniczna | 5,90 | 2,77 | 5,90 |
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
3. **Iteracja 3 — poprawki po audytach A1 i A2** (rejestr w §13): konwencja obrysów płyt po licu konstrukcji, attyki w osi muru,
   wyrównane wierzchy płyt wysuniętych, B10, ściana środkowa ŻB, fasada E słupowo-ryglowa, PL-D, wentylacja dachowa, garaż, spiżarnia.
   Wynik: walidacja 0/0, audyt A1 0 niezgodności, kolizje brył IR ściana–płyta–attyka usunięte (zostają zamierzone: belki i słupy w murze).
4. **Podgląd** liczy PU wg W-316, odległości od granic, wysokości (upzp i WT §6), okna/podłogę i wierność szkicowi.
   Wyniki wstawia do §9.

## 10. Odstępstwa, ryzyka i dalsze kroki

* **Świadome odstępstwa od szkicu:**
  * bryła B ma 12,60 m w licach zamiast ≈ 12,0 m: moduł osi 12,00 m + ETICS, ściany w pionie;
  * przeszklenie E zaczyna się ≈ 0,4 m bliżej zachodu niż w szkicu, bo słup narożny i ściana A są w osi A.
* **Odstępstwo od założeń — jednostka zewnętrzna PC od południa** (nie od N/E): uzasadnienie i szacunek hałasu w §7 (W-024 ≥ 6,0 m
  od granicy E wyklucza stanowisko wschodnie ≈ 4,8 m; od północy wjazd i wejście).
* **Świetlik SW1 a wyrzutnia (WT §152 ust. 12)** — przyjęta interpretacja: przepis dotyczy okien otwieranych; SW1 stały. Ryzyko
  interpretacyjne do potwierdzenia (rzeczoznawca ds. sanitarnohigienicznych); alternatywą jest zestaw zblokowany czerpnia/wyrzutnia.
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
* Audyty: `audyt_A1.md` (WT/MPZP, stan przed poprawkami), `audyt_A2.md` (geometria), `audyt_A1_po_poprawkach.md` (ponowny przebieg
  `tools/audyt_wt.py` po poprawkach); rejestr decyzji — §13.

## 12. Weryfikacja niezależna i podglądy 3D

> **Stan historyczny** (przed rundą 2 i wydaniem) — wartości aktualne: §9 (bilans z modelu) i §15.

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

## 13. Rejestr zmian po audycie (A1 — zgodność z WT/MPZP, A2 — spójność geometryczna)

> **Stan historyczny** (runda 1) — wartości wysokości i położenia czerpni/wyrzutni zastąpione w §14.2 i §15.

Stan wyjściowy: audyt A1 — 3 niezgodności, 5 uwag, 152 kontrole OK (`audyt_A1.md`); audyt A2 — 1 krytyczna, 9 istotnych, 12 drobnych
(`audyt_A2.md`). Poprawki wprowadzono w `tools/buduj_model.py` (model regenerowany), w rdzeniu `src/lamela/model.py` i IR
`src/lamela/ir.py` (konwencja płyt/attyk, SCHEMAT §5 pkt 8) oraz w `tools/podglad_modelu.py`. **Wynik po poprawkach:** walidacja rdzenia
0 błędów / 0 ostrzeżeń; `tools/audyt_wt.py` — **0 niezgodności**, 4 uwagi (opisane niżej), 165 OK (`audyt_A1_po_poprawkach.md`); arkusze
PB-AR-01…10 QA OK; testy `test_pipeline`, `test_obliczenia_*` zaliczone; bryła bez zmian (zabudowa 187,50 m², H zabudowy 10,33 m,
H wg WT §6 9,95 m, PU 239,32 m², sylweta „S” — odchyłka ≤ 0,59 m).

| uwaga (audyt, waga) | decyzja | zmiana w modelu / opisie |
|---|---|---|
| A1 — czerpnia–wyrzutnia 9,81 m, Δh 0,05 m (WT §152 ust. 10; istotna) | **przyjęta** | czerpnia (11,60; 1,00; +10,00), wyrzutnia (1,90; 4,00; +10,00) → 10,15 m; wyrzutnia przesunięta o 0,2 m względem propozycji A1 (1,70; 3,00), bo po zmianie obrysu D1 na lico konstrukcji odległość od krawędzi nad O2-04 wynosiłaby 2,80 m; zdanie w §4 (J1) poprawione |
| A1 — czerpnia 0,377 m nad lokalnym pokryciem (W-166; drobna) | **przyjęta** | dolna krawędź wlotu +10,00 → 0,42 m nad pokryciem z klinem; rzędne urządzeń liczone od pokrycia lokalnego |
| A1 — stanowiska MP1/MP2 0,18 / 0,27 m od ścian (WT §104; drobna) | **przyjęta z modyfikacją** | 2,50 × 5,90 m; MP1 x_dz 20,12–22,62 (0,30 m od S0-16), MP2 22,67–25,17 — 0,30 m od płytkiej szafy na rowery (0,40 m), 0,70 m od S0-03 (A2 D-5 i A1 łącznie) |
| A1 — próg dom–garaż 0,9 cm; woda z garażu do zbiornika (W-114; drobna) | **przyjęta** | spadek 0,8 %: −0,05 przy O0-22, −0,10 przy bramie (próg 5,1 cm); OL-1 i OL-4 → separator SEP-1 → niecka NT-E; `rzedna: -0.10` pom. 0.13 |
| A1 — wyrzutnia 6,1 m od SW1 (WT §152 ust. 12; drobna) | **przyjęta (wariant a)** | SW1 zapisany jako świetlik stały, nieotwierany (`otwierany: false`), interpretacja w §7 i §10; audyt nadal zgłasza UWAGĘ (narzędzie nie rozpoznaje interpretacji) |
| A1 — spiżarnia h 1,37–2,75, PU „wys 1,90” zawyżona (WT §97, W-316; drobna) | **przyjęta** | podział: 0.05 spiżarnia (h ≥ 2,20, 1,02 m²), 0.15 schowek (h 1,40–2,20, 1,45 m², PU 50 %), 0.16 schowek pod spocznikiem (h < 1,40, poza PU); PU 239,32 m²; audyt zgłasza UWAGĘ dla 0.15/0.16 (reguła „pomieszczenie gospodarcze ≥ 2,00”) — to schowki pod schodami, nie pomieszczenia |
| A1 / A2 D-11 — jednostka PC od S (założenie N/E; drobna) | **odrzucona zmiana lokalizacji, uzasadnienie dopisane** | W-024 (≥ 6,0 m od granicy E) wyklucza stanowisko wsch. (≈ 4,8 m); od N wjazd/wejście; ekran akustyczny od T1/T3/O0-06, szacunek hałasu w §7; jednostka pod okapem PL-D |
| A1 — WT §6 do średniego pokrycia, H zabudowy od średniego terenu (drobna) | **przyjęta** | `podglad_modelu.py`: WT §6 do najwyższego punktu pokrycia z klinem (9,95 m), H zabudowy kontrolnie od najniższego terenu (10,33 m; wg definicji od średniej 10,25 m) |
| A2 K-1 — płyty i attyki do lica ETICS, beton przecina izolację (krytyczna) | **przyjęta** | ST1/ST2/D1–D4 po licu warstwy konstrukcyjnej (±0,09; A' ±0,10), przy uskokach bryły do lica ściany wyższej; attyka ŻB 18 w osi muru (`szer: 0.18`) + PIR 10 cm od dachu + ETICS ściany ciągły; rdzeń: nie przedłuża ETICS na czoło płyty ciągłej na zewnątrz i nie obniża go w narożach nad ścianą niższą; IR: okładzina attyki tylko tam, gdzie brak ocieplenia ściany. PL-* zaczynają się od lica ETICS: pas −0,30…−0,09 = łącznik w płaszczyźnie izolacji (**odstępstwo od propozycji „od −0,09”** — płyta nie przecina ETICS geometrycznie, a łącznik z ETA jest w strefie izolacji); kolizje płyta/attyka–ocieplenie: 0 |
| A2 I-1 — brak podpory D1 w osi 3 (C–D) (istotna) | **przyjęta** | belka B10 25 × 50, spód +8,80, na S2-10 i S2-04 |
| A2 I-2 — ścianka środkowa urwana na stropach, 12 cm × 9,3 m (istotna) | **przyjęta** | ściana ŻB 15 (SCZB15), `z_do` 3,00 / 6,15, monolityczna z biegami/spocznikami; biegi 1,135 / 1,130 m (użytkowa ≈ 1,04 m ≥ 1,00) |
| A2 I-3 — końce attyk D2/D3/D4 urwane 0,30 m przed ścianą wyższą (istotna) | **przyjęta** | `ir._attic_ring`: usuwany tylko pas równoległy do lica ściany wyższej; końce attyk dochodzą do lica; węzeł attyka–ściana wyższa w opisie AT1 (wywinięcie ≥ 0,15 m) |
| A2 I-4 — wierzchy płyt wysuniętych 5–10 cm nad stropem (istotna) | **przyjęta** | PL-E/PL-DA +3,00, PL-2 +6,15, PL-3 +9,30; pogrubienie od spodu (PL-E 0,30, PL-2 0,30, PL-3 0,32) |
| A2 I-5 — wełna pod wspornikiem A odkryta (istotna) | **przyjęta** | IZ-ST2Z + pustka + jedna płaska podsufitka PS-A (+5,67) pod wspornikiem i pasem zach. PL-2; obudowa czoła OB-A/OB-A2 do spodu podsufitki |
| A2 I-6 — słupy w otworach, pas muru 3 cm nad E (istotna) | **przyjęta** | kwatery E między licami słupów (1,78 / 1,78 / 2,22 / 2,22 / 2,86 m), wysokość 2,78 do spodu B1; HS2 2,78; DZ3 2,76 (spód D4); boks C w 3 otworach (O1-01, O1-13, O1-14) między słupkami SL5/SL6 |
| A2 I-7 — drzwi przesuwne łazienki gościnnej bez miejsca na skrzydło (istotna) | **przyjęta (wariant: drzwi chowane)** | O0-16 x 4,08–4,88 (0,80 w świetle), kaseta w ściance GK S0-19 (przegroda DZGK), przesuw do x 5,68; przedpokoju nie powiększano (bez zmiany szachtu SI) |
| A2 I-8 — linia D urywa się w 3D na x 12,6 (istotna) | **przyjęta** | PL-D: x 12,60–18,675, wysunięcie 1,00 m, +3,65…+3,85, rama stalowa w okładzinie na konsolach (WZ-14: 17 konsol) — do narożnika garażu; nie jest tarasem |
| A2 I-9 — brak koncepcja.md / final / main w podglądzie (istotna) | **nieaktualna** | koncepcja.md, `final/*` i `podglad_modelu.py main` istniały przed rozpoczęciem poprawek; podglądy i bilans odświeżone po zmianach |
| A2 D-1 — skrzydło O0-17 w regale | przyjęta | regał y 6,20–7,40 |
| A2 D-2 — skrzydło O0-23 na module PC | przyjęta | zawias przy y 1,60 (`strona: prawa`) |
| A2 D-3 — O2-12 vs centrala i drabina | przyjęta | drzwi do holu; wyłaz i drabina x 7,20–8,10 (front serwisowy centrali wolny) |
| A2 D-4 — szafa wiatrołapu zasłania FX3; skrzydła DZ1/DS1 | przyjęta | szafa y 6,72–8,00; DS1 otwierane do holu |
| A2 D-5 — szafa rowerowa w świetle bramy | przyjęta | szafa 0,40 × 2,40 m, y 6,45–8,85 (MP2 przesunięte, patrz A1) |
| A2 D-6 — okno O0-12 poza okapem PL-E | przyjęta (wariant osłony nadstawnej) | kaseta żaluzji nadstawna przed licem ETICS; okapu zach. nie wydłużano (sylweta E bez zmian) |
| A2 D-7 — PL-2 bez pasa wsch., LAM-E bez płyty, szczeliny lamel w narożach | przyjęta | PL-2 z pasem x 12,30–12,60; LAM-E od +6,15; linie lamel domknięte w narożach |
| A2 D-8 — brak nadproży | przyjęta | nadproża N* dla wszystkich otworów w ścianach nośnych/zewnętrznych (poza fasadą E/boksem C — belki B1/B2); ≤ 0,12 m muru → wieniec |
| A2 D-9 — B1/B2 b = 0,25 w EPS | przyjęta | B1 18 × 107, B2 18 × 80 w licu muru |
| A2 D-10 — powierzchnie klatek 1.06/2.06; rzędna garażu | częściowo | 2.06 bez ściany S2-09; garaż `rzedna: -0.10`. Zapisu klatki P1/P2 jako rzutu biegu nie wprowadzono — rdzeń odejmuje otwór stropu, klatki i tak są poza PU (W-316); do rozstrzygnięcia w zestawieniu PN-ISO 9836 w PT |
| A2 D-11 — PC przed elewacją S | patrz A1 | uzasadnienie w §7 |
| A2 D-12 — pas zach. PL-2/PL-3 2,4 m od podpory | **odrzucona (bez skracania)**, uzasadnienie | szacunek EQU i ugięć w §5 (M_dst ≈ 70 kNm ≪ 0,9·M_stb ≈ 235 kNm); skrócenie do 0,80 m osłabiłoby płytę A ze szkicu; pełne obliczenie w PT (W-262, W-268) |

**Pozostałe uwagi audytu A1 po poprawkach (świadome, opisane):** 0.15/0.16 — schowki pod schodami (reguła narzędzia dla pomieszczeń
gospodarczych), SW1 — interpretacja WT §152 ust. 12, PC-JZ — odstępstwo od założenia N/E. **Poza zakresem A1/A2** (z weryfikacji §12,
do kolejnej iteracji): spadki terenu przy budynku, rzędne den przelewów awaryjnych D1 względem pokrycia z klinem, wysokość stelaży PV,
cokół przy DZ2, U_w doświetla FX3; zaleca się też ponowne uruchomienie katalogu mostków (`tools/katalog_mostkow.py`) i pipeline'u 3D
na nowym modelu.

## 14. Rejestr zmian — runda 2

Źródło wejścia: `docs/20_koncepcja/poprawki_runda2_wejscie.md`. Zapis: uwaga → decyzja → podstawa. Zmiany wprowadzone wyłącznie
w `tools/buduj_model.py` (model/*.yaml generowane), bez zmiany brył A/B/C/G ani linii D/E.

### 14.1 Funkcja i ergonomia — audyt A3 (część 1 rundy 2; K-6 z listy wejściowej)

Kontrola po zmianach: walidacja rdzenia 0 błędów / 0 ostrzeżeń; `tools/audyt_wt.py` — 0 NIEZGODNE, te same 4 UWAGI co przed
zmianami (0.15, 0.16, SW1, PC-JZ — bez nowych); kontrola kolizji mebli ze sobą, ze ścianami i z łukami skrzydeł drzwi (logika stron
otwierania jak w rzucie `lamela.views.plan`) — 0 kolizji na P0–P2 (przed zmianami: 3). Podglądy `final/rzut_P0…P2.png` i bilans §9
odświeżone (PU W-316 239,13 m²; wskaźniki i wysokości z `lamela.wskazniki` bez zmian).

| Uwaga A3 (waga) | Decyzja | Podstawa |
|---|---|---|
| K-1 — wyspa prostopadle do zabudowy, 0,395 m przed zlewem (krytyczna) | **przyjęta.** Wyspa 2,20 × 1,00 **równolegle** do zabudowy osi E: x 9,10–10,10, y 1,80–4,00. Ciąg roboczy wyspa ↔ fronty (x 11,295) **1,195 m**; od pn. do lica ściany osi 3: 1,02 m (przejście OT1 ↔ pas 0.07). Na ścianie E bez zmian: zmywarka – zlew – blat roboczy – słupek piekarnika – lodówka; płyta indukcyjna na wyspie od strony ciągu (y 2,50–3,30), 0,70 m blatu po obu stronach. Trójkąt lodówka–zlew–płyta ≈ 2,0 + 1,8 + 2,0 ≈ 5,8 m. O0-21 → lodówka wzdłuż ciągu ≈ 3,6 m, bez obchodzenia wyspy. Wyspa bez hokerów. | ergonomia kuchni: ciąg 1,00–1,20 m, suma boków trójkąta ≤ ok. 7–8 m (Neufert — dobra praktyka); brief §4 („kuchnia z wyspą”) |
| I-1 — stół w poprzek strefy, krzesło szczytowe przy ekranie LAM-P0 (istotna) | **przyjęta.** Stół 2,20 × 1,00 wzdłuż E–W: x 5,20–7,40, y 1,85–2,85, 8 miejsc (3 + 3 + 2). Przejście przy przeszkleniu do HS1: ≈ 1,15 m (od strefy krzeseł do lica); od krzeseł pn. do ekranu LAM-P0: 0,95 m; szczyt wsch. (x 8,00) → wyspa 1,10 m; szczyt zach. (x 4,60) → sofa 0,90 m. | strefa krzesła 0,60–0,75 m + przejście ≥ 0,90 m (ergonomia); brief §4 (stół 6–8 os.) |
| I-2 — regał rowerowy zawęża garaż, w strefie bramy (istotna) | **przyjęta — wariant B (bez przesuwania osi F, bryła G bez zmian).** Szafa 0,40 zastąpiona przechowywaniem ściennym **≤ 0,30 m** przy ścianie osi F: rowery (uchwyty 2-poziomowe, rowery równolegle do ściany) y 6,10–8,90 przy drzwiach DZ2 oraz panel na sprzęt ogrodowy y 3,25–4,75. Szerokość wolna **5,75 m ≥ 5,60**; front 0,22 m od krawędzi światła bramy (x 17,75) — poza światłem i prowadnicami; MP2 0,40 m od frontu (≥ 0,30). Wariant A (oś F +0,60 m) odrzucony — zmienia bryłę G, pow. zabudowy i wierność szkicowi (warunek Inwestora). | W-112 (WT §104, §21); brief §4 (garaż ≥ 5,6 × 6,0 z miejscem na rowery i sprzęt ogrodowy) |
| I-3 — przedpokój gościnny 0.08: drzwi chowane nie mieszczą się, 3 skrzydła w 1,5 m² (istotna) | **przyjęta.** O0-14 (salon → 0.08) — drzwi **przesuwne naścienne** po stronie salonu (D1P), skrzydło parkuje na wolnej ścianie S0-08 x 3,25–4,20. O0-16 (łazienka 0.09) — drzwi skrzydłowe D2 0,90 × 2,10 **na zewnątrz** do 0.08, x 4,25–5,15 (≥ 0,10 m od obudowy SI), zawias od wsch. — otwarte skrzydło parkuje przy obudowie SI. O0-15 do pokoju 0.10. Ścianka S0-19: DZGK (kaseta kolidowała z węzłem obudowy SI S0-23 i z podejściem WC do pionu K1) → **DZ12**. Wolna strefa przedpokoju ≈ 1,2 × 1,1 m. | WT §79 ust. 1 (W-059); brief §4 (pokój gościa/seniora z łazienką) |
| I-4 — trasa garaż → schody przez narożnik roboczy kuchni (istotna) | **przyjęta.** Nowe drzwi **DG2 (O0-24)** 0,90 × 2,10 w ścianie SWG S0-16, y 5,60–6,50: stalowe ocieplone, szczelne, samozamykacz, U ≤ 1,3; otwierane do holu, zawias przy y 6,50 (auto na MP1 nie blokuje skrzydła; łuk rozłączny z łukiem DS1). Garaż → hol → OT1 → pas 0.07 → schody ≈ 6–7 m, bez przejścia przez ciąg roboczy (x 10,10–11,295). DG1 → przedsionek → kuchnia zostaje dla zakupów i ogrodu. Szafa holu przy ścianie E usunięta → szafa płytka 1,15 × 0,45 przy ścianie osi 3 (x 10,45–11,60), przejście przed nią do ścianki S0-21: 0,92 m. Nadproże nowego otworu generowane automatycznie (ściana nośna SWG). | W-113 (WT §106 ust. 1 — drzwi garaż–dom szczelne z samozamykaczem), W-114 (próg 5 cm), W-244; brief §4; ergonomia tras |
| I-5 — pokój 1.04: łóżko–szafa 0,12 m (istotna) | **przyjęta.** Szafa 1,80 × 0,60 na ścianie S1-05 (x 0,30–2,10, y 5,23–5,83; jak w 1.03), drzwi przesuwne; łóżko bez zmian (x 2,15–3,05, do ściany osi B 0,72 m); biurko pod oknem O1-05 y 6,30–7,70. Przed szafą do łóżka 0,815 m, poza biurkiem pełna głębokość; skrzydło O1-09 (x 2,65–3,50) poza szafą i łóżkiem. | strefa przed szafą ≥ 0,70 (przesuwne) / 0,90 m (skrzydłowe), przy łóżku ≥ 0,60 m (ergonomia); W-068 (pokój dziecka ≥ 12 m² — 12,52 m²) |
| I-6 — oś miski WC 0,235 m od ściany (1.05, 2.04) (istotna) | **przyjęta.** Miski przesunięte do x 5,15–5,55: oś **0,42 m** od lica ściany osi C (5,77). Stelaż samonośny w zabudowie przy obudowie SI (podejście do K1 bez zmian, odpływ wchodzi do szachtu przy x 5,37–5,55). W 1.05: od blatu umywalki (x 4,48) 0,67 m. | W-060 (WT §83 — analogicznie), wytyczne montażu stelaży WC (oś ≥ 0,40 m od ściany bocznej) |
| I-7 — łazienka 2.04: 0,595 m przed miską, blat na natrysku, „podwójna” 1,20 m (istotna) | **przyjęta.** Natrysk walk-in **1,79 × 0,90** (y 7,745–8,645; 1,61 m²) → przed miską **0,695 m** × 0,90 m; blat podwójny **1,40 × 0,50** na ścianie zach. (y 6,25–7,65), 0,095 m do natrysku, szyba stała od strony blatu; wejście z O2-10 — strefa y 5,23–6,25 wolna. | W-060 (pole przed miską 0,60 × 0,90), W-061 (natrysk szer. ≥ 0,90); ergonomia (0,70 m na stanowisko umywalki) |
| I-8 — centrala za ścianką 12 cm od pokoju 2.05 (istotna) | **przyjęta.** S2-13 i S2-14 z silikatu **18 cm** (nowa przegroda `DZ18A`, ścianka działowa akustyczna bez funkcji nośnej, styk ze stropem wypełniony elastycznie; cel R'A1 ≥ 50 dB — do sprawdzenia w PT). Centrala: podstawa antywibracyjna, połączenia elastyczne, tłumiki na 4 króćcach. O2-12 — nowy symbol **D4A**: R_w ≥ 32 dB, bez kratki, uszczelka obwodowa + próg z uszczelką opadającą. Poziom hałasu w pokojach wg PN-B-02151-2 — obliczenie w PT-IS. Meble 2.03/2.05/2.07 dosunięte do nowych lic. | W-066 (WT §96), W-230 (WT §326; PN-B-02151-2/-3), W-232 (WT §327) |
| D-1 — szafa wiatrołapu zasłania FX3, brak ławki (drobna) | **zrealizowana w rundzie 1** (szafa 1,28 m, y 6,72–8,00; przed FX3 0,64 m na ławkę). Ławki nie zapisano w modelu — katalog wyposażenia rdzenia nie ma typu „ławka” (dopisać w PAB). | W-056 (WT §63) |
| D-2 — skrzydła DZ1/DS1 zajmują głębokość wiatrołapu (drobna) | **zrealizowana w rundzie 1** (DS1 do holu); teraz strona zawiasu zapisana jawnie (`lewa` → zawias przy x 10,15), łuk DS1 rozłączny z łukiem DG2. | W-056 (funkcja śluzy) |
| D-3 — łuki O2-09 i O2-10 nakładają się (drobna) | **przyjęta.** O2-09 otwierane do holu 2.01 (łuk x 5,95–6,80, poza wyjściem z biegu 2 x ≥ 7,25 i łukiem O2-12). | W-059; ergonomia drzwi |
| D-4 — O2-12 vs centrala i drabina (drobna) | **zrealizowana w rundzie 1** (O2-12 na zewnątrz do holu; wyłaz x 7,10–8,20). | W-065 |
| D-5 — skrzydło WC 1.07 w poprzek holu przy wyjściu ze schodów (drobna) | **przyjęta.** O1-11 zawias od wsch. (x 9,61, strona `prawa`). | W-059; WT §5 ust. 1 pkt 4 (bezpieczeństwo użytkowania — ogólnie) |
| D-6 — OT2 otwarty akustycznie na hol i klatkę (drobna) | **odroczona do PAB.** Otwarcie pokoju rodzinnego na galerię jest zamierzeniem kompozycyjnym; wartości PN-B-02151-3 wewnątrz lokalu są zalecane. W PAB rozważyć ściankę szklaną z drzwiami przesuwnymi 2 × 1,20 m (wymaga danych systemu — bez wymyślania parametrów). | W-230 (wartości zalecane) |
| D-7 — pokój 2.05 bez sanitariatu dla stałego mieszkańca (drobna) | **przyjęta.** 2.05 = „Gabinet / pokój gościnny okazjonalny”; stały 5. mieszkaniec — pokój 0.10 z łazienką 0.09. | brief §4 (rodzina 4–5 osób) |
| D-8 — skrzydło O0-23 wchodzi w moduł PC (drobna) | **przyjęta.** Strona zawiasu poprawiona na `lewa` (rzeczywiście y 1,60 — w rundzie 1 `prawa` dawała zawias przy y 2,50); moduł PC przesunięty do x 15,45–16,05. RG (y 0,50–1,30) poza łukiem, strefa obsługi ≥ 0,80 m wolna. | PN-HD 60364 (strefa obsługi rozdzielnicy); DTR urządzeń |
| D-9 — pokój 0.10: szafa–łóżko 0,815 m; natrysk dla seniora (drobna) | **przyjęta.** Szafa z drzwiami przesuwnymi; w 0.09 natrysk posadzkowy **1,20 × 0,90** (x 3,98–5,18, y 7,745–8,645) z odpływem liniowym, do umywalki 0,14 m. | ergonomia; brief §4 (gość/senior); W-061 |
| D-10 — „spiżarnia” pod schodami (drobna) | **zrealizowana w rundzie 1** (podział 0.05 h ≥ 2,20 / 0.15 schowek h 1,40–2,20 PU 50 % / 0.16 < 1,40). Bez zmian. | W-053 (WT §97), W-316 |
| D-11 — kuchnia bez otwieranego skrzydła (drobna) | **odroczona do PAB.** Kwatera FX2 jest częścią podziału fasady E; skrzydło uchylno-rozwierne w kwaterze wymaga danych systemu fasady (słupek, U_w) — bez danych producenta nie zmieniam. Kuchnię przewietrza HS1 jadalni (2,3 m); wymaganie W-068 („kuchnia z oknem”) spełnione. | W-068; zasada „lub równoważne” — bez wymyślania danych |
| D-12 — pusta elewacja S bryły G, PC na osi widoku; 6,90 vs 7,0 m (drobna) | **odroczona.** Okładzina lamelowa S0-02 zmienia elewację (zespoły rysunków/PZT) — decyzja Inwestora w PAB. Odległość PC od granicy E: środek jednostki 7,60 m (x_dz 24,40), krawędź zależy od wymiarów urządzenia (brak danych wyrobu) — ujednolicić w PZT po wyborze PC. | W-024, W-156 |

**Nie zmieniono:** brył A/B/C/G, osi, stropów, dachów, otworów fasad (poza DG2 w ścianie wewnętrznej dom–garaż), wskaźników MPZP
i wysokości (`lamela.wskazniki`). Nowe elementy: przegroda `DZ18A`, symbole stolarki `D1P`, `D4A`, otwór `O0-24` (DG2). Symbol `D2P`
usunięty (nieużywany); przegroda `DZGK` pozostaje w katalogu (nieprzypisana).

### 14.2 Fizyka, woda, instalacje (część 2 rundy 2; K-1…K-12 bez K-6, weryfikacja §6 A/B/C, REKOMENDACJE mostków A/B, BRAKI PT-IS/PT-IE)

Zmiany wyłącznie w `tools/buduj_model.py` (model/*.yaml generowane) oraz minimalne poprawki bibliotek obliczeniowych (`lamela.obliczenia`,
bez rdzenia `model.py`/`ir.py` i bez `views/**`) — każda poprawka biblioteki czyta nowe pole modelu albo usuwa fałszywy alarm (lista
na końcu). Wynik końcowy: walidacja 0 błędów / 0 ostrzeżeń; `audyt_wt.py` 0 NIEZGODNE (te same 4 UWAGI co przed rundą); drenaż/teren,
deszczowa, kanalizacja, ogrzewanie — 0 niespełnionych; EP = **35,6** (z PV), **57,8 bez PV** ≤ 70; H_TB = 30,6 W/K (było 138,2);
Φ_HL = 7,41 kW (było 11,70); wszystkie węzły f_Rsi ≥ 0,72 (min. 0,836).

**A. Woda, teren, cokół, odwodnienie**

| Uwaga | Decyzja | Podstawa |
|---|---|---|
| K-1 / wer. A2, A5 — spadki terenu 0,2–1,1 %, cokół 0,14 m | **przyjęta.** Nowe rzędne projektowane (`teren_projekt()`): pierścienie 0 / 0,3 / 0,8 / 1,5 / 2,3 m od lic P0, H = 101,32 − 0,03·d (spadek **3 %** od budynku; teren przy licu **−0,33** → cokół ≥ 0,30 z zapasem na interpolację), pierścień 2,3 m = dno niecek NT-N / NT-E (spadek podłużny ≥ 0,5 % do ogrodu pd.); ogród i pas zach. ≈ 0,5 % ku niecce NCH-1; przed elewacją pn. i za NT-E powrót do terenu istniejącego. Moduł drenażu: spadki 2,7–4,0 % na wszystkich ścianach, cokół min. **0,31 m** poza strefami drzwi. Fundament PC (U5) usunięty z punktów terenu (obiekt, nie teren). | W-019, brief §9 pkt 4 i 6, DIN 18533-1 (pomocniczo), WT §28, §316 |
| K-1 / R-W4 — drzwi bezprogowe, DZ2, DZ3 | **przyjęta.** Strefy drzwi z odwodnieniem liniowym: podest wejścia T2 −0,02 (x 9,80–11,70; OL-3), fartuch bramy −0,12 ze spadkiem 2,4 % do **OL-1 przeniesionego 2,3 m od bramy** (grzbiet podjazdu 4,3 m od bramy, OL-4 przy furtce/bramie wjazdowej), **OL-5** przy progu DZ2 (podest −0,12, stopień 0,15, → KD-E), **OL-6** przy progu DZ3 (podest T3 −0,02, 2 stopnie, → RS8/KD-E). Moduł drenażu uznaje strefę drzwi (± 0,30 m, brama ± 1,0 m) z odwodnieniem liniowym ≤ 2,5 m za spełnienie brief §9 pkt 4 („lub odwodnienie liniowe”) i raportuje cokół w strefie informacyjnie. Przy garażu teren −0,33 = 0,23 m pod posadzką −0,10 (≥ 0,15). | brief §9 pkt 4; DIN 18533-1 (uszczelnienie cokołu ≥ 0,15 m); PT-AR-D-14 |
| K-2 — niecka NCH-1 w rzucie korony lipy DR1 | **przyjęta.** DR1 przesunięta do (4,0; −22,0) — dojrzała korona r 3,5 m ≥ 1,0 m od krawędzi niecki (odległość od korony, nie od pnia); 7,2 m od granicy pd. | W-144 (≥ 1,0 m od drzew — interpretacja: rzut korony) [źródło wytycznej — DO WERYFIKACJI] |
| wer. B6 — niecka 6,75 m³ przy V_min 6,65 m³ | **przyjęta.** NCH-1 powiększona do **28 m²** (7,0 × 4,0 m, głęb. 0,30 m, V 8,4 m³); moduł deszczowy — bilans spełniony. | W-143, W-145 (≤ 0,30 m) |
| R-W1 / wer. B1, BRAKI PT-IS 1–11 — płyty wysunięte bez odbioru wody | **przyjęta.** PL-E, PL-DA, PL-2, PL-3, PL-D: spadek 2 % od budynku + **rynna ukryta za blendą** (korytko 100 mm, 0,5 % do wylotu, kapinos ≥ 3 cm, podgrzewany wylot); wyloty DN70 → rury DN80 przy ścianach: **RS7** (ściana zach. P0, rynny zach. PL-E i PL-2 → KD-W), **RS8** (ściana pd. pasa gosp., rynny PL-E pd. i PL-D → KD-E; linia kapania PL-D już nie nad jednostką PC), **RS10** (ściana wsch. bryły B → opaska D4), PL-3 → **RS11/RS12** w szczelinie za lamelami LAM-E/LAM-W → rynna PL-2, PL-DA → RS4. PL-C1/PL-C2 (rama C), SW1, WYL1 — `odwodnienie: na_powierzchnie` (spływ na płytę z rynną / na D1); IZ-ST2Z, PS-A, OB-A — `nie_dotyczy`. Nowe przyłącza KD w `dzialka.uzbrojenie`. | brief §9 pkt 3; PN-EN 12056-3; W-142 |
| R-W2 / wer. A3 — dno przelewów względem pokrycia średniego | **przyjęta.** Pole `rzedna_pokrycia` (wierzch hydroizolacji) przy każdym wpuście i przelewie (stożek izolacji spadkowej 2 % — funkcja `pokrycie()`); dno = pokrycie przy wpuście + 0,03…0,05 i ≥ pokrycie lokalne (asercja w skrypcie): D1 PA1 9,46 (0,78 m od WP2), **PA2 przeniesiony** do attyki zach. nadbudowy 9,47 (→ D2), PA3 usunięty (przepustowość PA1 + PA2 = 22,4 ≥ 8,0 l/s); D2 PA4 6,33 (0,60 m od WP3); D3 **PA5** w attyce pn. 6,33 (0,35 m od WP4, wylot poza daszkiem PL-DA); D4 PA6/PA7 3,17 (0,57/0,75 m od WP5/WP6). | W-142; J2 poprawka 5.1 (30–50 mm); DAFA (wywinięcie 15 cm) |
| R-W3 / K-12 — wywinięcie na D1 = 15 cm w najwyższym narożu | **przyjęta z nadwyżką.** Attyka D1 **+0,10 m** (0,35 nad pokryciem średnim, korona +9,876): wywinięcie w najwyższym narożu 0,28 m; jednocześnie moduły PV poniżej korony (A4). Wysokość zabudowy bez wpływu (najwyżej czerpnia/wyrzutnia +10,00). | DAFA / DIN 18531 (pomocniczo); W-033 |
| K-12 — posadzka garażu bez membrany, niespójna POD-G | **przyjęta.** POD-G: żywica, jastrych zbrojony 9–14 cm (−0,05 przy drzwiach do domu → −0,10 przy bramie), folia, **XPS 10 cm**, **membrana SBS**, płyta ŻB obniżona (**PF2**, wierzch −0,30), XPS 20 cm. Żebro licowane z czołem płyty — do uzgodnienia z BO (K-5). | W-114; REKOMENDACJE mostków A (WZ-09a) |

**B. Fizyka budowli, mostki, EP**

| Uwaga | Decyzja | Podstawa |
|---|---|---|
| Mostki A — WZ-04/05/07a/16a (ψ > dobra praktyka) | **przyjęta.** `wsporniki_plyty[].lacznik` = {d 0,12, λ_eq 0,08} (wymaganie; ETA do potwierdzenia) dla PL-E, PL-DA, PL-2, PL-3; biblioteka mostków czyta łącznik z modelu. ψ_oi: WZ-04 0,220 → **0,128**, WZ-05 0,226 → **0,134**, WZ-07a 0,182 → **0,152**, WZ-16a 0,236 → **0,194**. Podsufitka PS-A — jedna płaszczyzna (+5,67) pod wspornikiem A i pasem zach. PL-2 (bez zmian, zgodna z R-W5). | REKOMENDACJE mostków A; W-248, W-272; PN-EN ISO 10211 |
| Mostki A — WZ-06 attyka z okapem PL-3 | **przyjęta.** `dachy[D1].attyka.blok_termoizolacyjny` {h 0,15, λ 0,045} (materiał BLOK_TERM — szkło piankowe / element z ETA, nośność PT-K) + łącznik 120 mm: ψ_oi 0,385 → **0,205**, f_Rsi 0,825 → 0,889; WZ-01 0,174 → **0,086**. | jw. |
| Mostki A — WZ-09a garaż (ψ 0,616, „ZŁY”) | **przyjęta.** XPS 10 cm + membrana na obniżonej płycie garażu (PF2) i blok z betonu komórkowego 600 (λ 0,16) h 0,24 m w 1. warstwie muru SWG (`wezly[WZ-09].blok_u_podstawy`): ψ_iu **0,301**, f_Rsi 0,760 → **0,903**. Ocena „ZŁY” pozostaje (test ołówka — płyta ciągła pod SWG); f_Rsi spełnione z zapasem. | REKOMENDACJE mostków A; W-248 |
| Mostki D — długości `wezly` liczone podwójnie; WZ-X1/X2 poza sekcją | **przyjęta.** Sekcja `wezly`: `dlugosc` z geometrii (każdy odcinek raz), `psi` (Ψ_oi) i `f_rsi` z katalogu mostków budynku (tabela `_SYM` w skrypcie; węzły złożone — średnia ważona z `podwezly` a/b/c), nowe WZ-X1 (D2/D3 – ściana P2) i WZ-X2 (D4 – ściana P1). Moduł energii bierze Ψ z modelu bez dodatkowych plików. | REKOMENDACJE mostków D1–D3; PN-EN ISO 14683 |
| K-4 / wer. B3 — EP spełnione tylko z PV (bez PV 81,8) | **przyjęta.** Po mostkach z symulacji H_TB **138,2 → 30,6 W/K**, Φ_HL 11,70 → **7,41 kW**; EP (A: PC R290 + PV + rekuperacja) **35,6**; **bez PV 57,8 ≤ 70** (zapas 17 %); wrażliwość: n50 = 4 h⁻¹ (brak próby szczelności) — EP 44,1 z PV (raport `projekt/08_obliczenia/fizyka_energia_runda2/`). PV pozostaje elementem projektu (EP, U_oze), ale spełnienie W-240 od niego nie zależy. | WT §328–329, zał. 2 pkt 1.1; rozp. MIiR 2015 (metodologia) |
| wer. A6 — U_w FX3 = 1,0 > 0,9 | **przyjęta (wariant „zmienić profil”).** Wymaganie ramy U_f ≤ 0,80 (rama z rdzeniem izolacyjnym, klasa phA — lub równoważna), U_g ≤ 0,50, Ψ_g ≤ 0,04 → U_w = **0,87**. Scalenia z DZ1 w zestaw drzwiowy nie przyjęto (zmiana rysunku stolarki i łuku skrzydła). | WT zał. 2 pkt 1.2 (W-244); PN-EN ISO 10077-1/-2 |
| wer. C8 — U w nazwach przegród niższe od obliczonych | **przyjęta.** Nazwy przegród i tabela §6: SZ1/SZ2 0,17, SZL 0,099, SWG 0,27, SD1 0,11, SD2 0,12, DZ1 0,13, POD-0 0,11 (U_equiv), ST2Z 0,13. Cel W-245 dla ścian (0,15) — **nieosiągnięty, świadomie**: pogrubienie ETICS zmienia lica/obrys (pow. zabudowy, sylweta, odległości) przy zapasie EP już 17 % bez PV; wymaganie WT (≤ 0,20) spełnione. | W-243, W-245 (cel, nie przepis; sprzeczność S-3) |

**C. Instalacje**

| Uwaga | Decyzja | Podstawa |
|---|---|---|
| K-8 / BRAKI PT-IS 15, 20 — piony bez `rodzaj` | **przyjęta.** `instalacje.piony[]`: `rodzaj` (kanalizacja / deszczowa / co) i `kond`; nowe **K3** (pom. techn. 0.12, wywiewka nad D4, 6,6 m od czerpni) i **PCO** (piony c.o. do R-P1/R-P2). Grupowanie pionów kanalizacji bierze tylko `rodzaj: kanalizacja` (dotąd RS6 zbierał przybory 0.12 i kuchni). | PN-EN 12056-2/-3; WT §125, §152 ust. 4 |
| K-9 / BRAKI PT-IS 17 — bilans wentylacji | **przyjęta.** `went` pomieszczeń: wywiew Σ 365 m³/h (kuchnia 50, 4 łazienki × 50, WC 30, pralnia 40, spiżarnia 15, pom. techn. 2 × 15), nawiew Σ 365 m³/h (salon z jadalnią 90, pokoje 40/40/40, pokój rodzinny 50, sypialnia 60, gabinet 45); szachty SI `rodzaj: szacht` — bez wywiewu; strefy pod schodami 0.15/0.16 — jedna przestrzeń ze spiżarnią 0.05 (`strefa_spizarni`). Moduł wentylacji przyjmuje strumienie z modelu (bilans ±10 %, minima, 20 m³/h·os. — spełnione). | PN-83/B-03430/Az3; WT §149–150 (W-161, W-162) |
| wer. B5 — centrala 450 m³/h vs 477 m³/h okresowo | **przyjęta.** Strumień projektowy 365 m³/h (81 % V_nom), tryb okresowy (okap 120) **435 m³/h ≤ 450**; wyrzutnia z wylotem poziomym — 10,15 m od czerpni ≥ 10 m (flaga `wyrzut` była niespójna z uwagą rundy 1). | WT §152 ust. 10 (W-167), W-163, W-164 |
| K-10 / wer. A7 / BRAKI PT-IS 12–13 — niedobór mocy podłogówki, PC 12,2 kW | **przyjęta.** Po obniżeniu Φ_HL niedobór pozostał w łazienkach/WC i klatce P2 → `instalacje.grzejniki`: ściany grzewcze WODNE z obiegu PC 35/30 °C (0.03 80 W, 0.09 280 W, 1.05 150 W, 1.07 180 W, 2.04 180 W, 2.06 200 W; bez grzałek elektrycznych — EP); moduł ogrzewania odejmuje ich moc od Φ_HL podłogi. Wynik: 0 niespełnionych (q ≤ q_G, moc przy θ_V ≤ 35 °C); PC — klasa ok. **7 kW** (≤ 12 kW — R290 zgodnie z (UE) 2024/573), dobór wg DTR. | PN-EN 1264-2/-3/-5; PN-EN 12831-1; W-153, W-155 |
| K-7 / wer. A4 / BRAKI PT-IE 1 — PV ponad attyką, 10 z 15 modułów | **przyjęta.** Faktyczny układ modułów w `energia.pv.pola` (prostokąty, pole montażu, z_max): D1 — **7** modułów EW10 (strefa brzegowa 1,0 m, wyłaz, czerpnia/wyrzutnia/wywiewka ± 1,0 m, wpusty ± 0,5 m), D4 — **8** modułów na dachu **biosolarnym** (1,5 m od ściany bryły B) → 15 × 430 Wp = 6,45 kWp ≤ 6,5; górna krawędź modułów D1 **+9,863 ≤ korona attyki +9,876** przy pokryciu lokalnym (asercja w skrypcie), D4 +3,70 ≤ +3,85; PR 0,78 (−0,02 na zacienienie popołudniowe pola D4 [ZAŁ]). `energia.pv.z_max` wliczone do wysokości zabudowy. | W-033, D-15, W-194; PB art. 29 ust. 4 pkt 3 lit. c |
| BRAKI PT-IS 19 — zasobnik 300 vs 400 dm³ | **przyjęta.** Zasobnik c.w.u. **400 dm³** (moduł wody: V_zas ≥ 367 dm³). | PN-EN 12831-3; W-133 |
| K-3 / K-11 — wysokość zabudowy w narzędziach od t_min | **przyjęta.** `tools/audyt_wt.py` i `tools/podglad_modelu.py` biorą wysokość zabudowy i wysokość wg WT §6 wyłącznie z `lamela.wskazniki` (wariant od t_min — informacyjnie); podgląd — także pow. zabudowy, PBC i intensywność. Wywiewki K1/K3 z jawną rzędną (bez założenia +0,50 nad pokryciem średnim). | upzp art. 2 pkt 30 lit. a (Dz.U. 2026 poz. 538); W-033, W-063 |
| wer. C3, C4 — numeracja pomieszczeń, etykieta PU | **przyjęta (dane).** `meta.numeracja_pomieszczen` (model K.NN ↔ arkusze iso (K+1).NN, przykład przejścia) i `meta.PU_definicja` (PU wg W-316 ≠ „użytkowa” rdzenia z garażem) — do opisów arkuszy (zespoły rysunków). | RPB §20, PN-ISO 9836:2022, W-316 |

**D. Wyniki kontroli po zmianach (model po rundzie 2, część 2)**

| Wielkość | Wartość | Źródło / wymaganie |
|---|---|---|
| PU (W-316) / pow. zabudowy / PBC | 239,13 m² / 187,50 m² (11,7 %) / 1 270,15 m² (79,4 %) | `lamela.wskazniki`, podglad_modelu.py; MPZP ≤ 30 %, ≥ 50 % |
| wysokość zabudowy | **10,27 m** (od t_śr 101,38; najwyżej czerpnia/wyrzutnia +10,00; PV +9,863, attyka D1 +9,876, wywiewka K1 +9,94) | upzp art. 2 pkt 30 lit. a; ≤ 11,00 (rezerwa 10,70) — W-033 |
| wysokość wg WT §6 | 9,97 m (wejście O0-03) — grupa N | WT §6, §8 (W-063) |
| EP / EP bez PV | **35,6 / 57,8** kWh/(m²·rok) | ≤ 70 (W-240) |
| H_TB | 30,6 W/K (moduł energii, Ψ z modelu); katalog mostków 32,4 W/K (z b_u i χ) | PN-EN ISO 14683 / 10211 |
| f_Rsi min. | 0,836 (WZ-09b) | ≥ 0,72 (W-248) |
| Φ_HL / PC | 7,41 kW / klasa ok. 7 kW R290 | PN-EN 12831-1; W-155 |
| wentylacja | 365 / 365 m³/h, okresowo 435 m³/h ≤ 450 | W-161…W-164 |
| PV | 15 × 430 Wp = 6,45 kWp (D1 7 + D4 8), 5 610 kWh/a | W-194, W-033 |
| przelewy / wywinięcia | wszystkie ✓ (moduł deszczowy i katalog mostków R-W2/R-W3) | W-142; DAFA |
| teren / cokół | spadki 2,7–4,0 %; cokół ≥ 0,31 m poza strefami drzwi z OL | W-019; brief §9 pkt 4 |
| testy | test_pipeline (23), test_obliczenia_fizyka (24), _instalacje (22), _konstrukcja --lamela (28), test_mostki2d (26), test_rysunki_konstrukcja --model (12), test_wskazniki — zaliczone | — |

Raporty: `projekt/08_obliczenia/fizyka_energia_runda2/`, `projekt/08_obliczenia/instalacje_runda2/`, katalog mostków
`projekt/08_obliczenia/mostki/` (przeliczony dla nowego modelu), audyt `docs/20_koncepcja/audyt_A1.md`.

**E. Minimalne poprawki bibliotek (bez rdzenia i bez `views/**`)**
* `obliczenia/sanitarne/przybory.py` — grupowanie pionów tylko z `rodzaj: kanalizacja` (K-8);
* `obliczenia/sanitarne/deszczowa.py`, `inst_wspolne.py` — dno przelewu względem `rzedna_pokrycia` przy wpuście + kontrola pokrycia lokalnego;
  elementy `odwodnienie: nie_dotyczy | na_powierzchnie` nie są polami dachu (wer. C11);
* `obliczenia/sanitarne/drenaz.py` — cokół: strefy drzwi z odwodnieniem liniowym wg brief §9 pkt 4 („lub odwodnienie liniowe”);
* `obliczenia/sanitarne/ogrzewanie.py` — dodatkowe powierzchnie grzewcze `instalacje.grzejniki` odejmowane od Φ_HL podłogi;
* `obliczenia/energia/bryla.py` — krótki odcinek ściany WEWNĘTRZNEJ bez pomieszczenia za nią (wnętrze obrysu) = przegroda adiabatyczna,
  nie zewnętrzna (fałszywe „U ściany zewn.” SWG/DZ12/SCZB15, 0,1–0,3 m²);
* `obliczenia/mostki2d/katalog_dod.py`, `katalog.py` — łącznik (`wsporniki_plyty[].lacznik`), blok attyki (`attyka.blok_termoizolacyjny`)
  i blok u podstawy SWG (`wezly[].blok_u_podstawy`) czytane z modelu;
* `tools/audyt_wt.py`, `tools/podglad_modelu.py` — wysokości (i w podglądzie wskaźniki MPZP) z `lamela.wskazniki` (K-11).

**F. Pozostaje (poza zakresem części 2 lub do decyzji)**
* **BO (K-5):** uskok płyty fundamentowej pod garażem (PF2, wierzch −0,30; żebra SWG i garażu do −0,85), blok z betonu komórkowego 600
  w 1. warstwie SWG — sprawdzić w MES płyty i nośności muru; żebro licowane z czołem płyty (K-12).
* **Zespoły rysunków (`views/**`, arkusze):** układ PV z `energia.pv.pola` (rysunek IE-PV liczy własny układ i raportuje 10 z 15),
  rynny ukryte / RS7–RS12, OL-5/OL-6, T2 x 9,80, attyka D1 +0,10 m, ściany grzewcze (`instalacje.grzejniki` — nie w `wyposazenie`,
  bo rzut architektury nie zna typu „grzejnik”), numeracja (`meta.numeracja_pomieszczen`), etykieta PU.
* **PT-IE (wer. B7):** spadek napięcia WLZ 0,61 % > 0,50 % i DC PV 1,04 % > 1,00 % — parametry bibliotek (przekrój WLZ, trasa DC),
  nie danych modelu; rozwiązać w PT (YKY 5×25 lub RG bliżej ZKP; DC 10 mm² lub falownik przy dachu).
* **PT-IS:** trasy przewodów, pion/szacht wentylacyjny (BRAKI 14), teletechnika T1/RACK, dane wyrobów (DoP/DTR) — bez wymyślania danych;
  spójność cyrkulacji c.w.u. (moduł wody: cyrkulacja czasowa; EP: η_W,d 0,60 zachowawczo, bez pompy cyrkulacyjnej).
* Mostki: WZ-06 (0,205) i WZ-16a (0,194) nadal powyżej dobrej praktyki; kolejny krok — attyka lekka / obłożenie belek B3–B5 wełną
  (REKOMENDACJE A) — do decyzji w PT-AR-D. Cel W-245 dla ścian (0,15) — świadomie nieosiągnięty (§14.2 B).
* Audyt A1 — 4 UWAGI bez zmian (strefy pod schodami, wyrzutnia ↔ SW1 stały, PC-JZ od elewacji S).
* `docs/SCHEMAT_MODELU.md` — dopisać nowe pola (rdzeń je ignoruje — INFO walidacji): `wpusty/przelewy_awaryjne[].rzedna_pokrycia`,
  `dachy[].rzedna_pokrycia`, `attyka.blok_termoizolacyjny`, `wsporniki_plyty[].odwodnienie/lacznik/spadek`, `wezly[].psi/f_rsi/podwezly/
  blok_u_podstawy`, `energia.pv.pola/z_max`, `instalacje.piony[].rodzaj/kond`, `instalacje.grzejniki` (właściciel schematu).

### 14.3 Weryfikacja niezależna V1 po rundzie 2 (WT/MPZP, geometria) — bez zmian modelu

Pełny raport: `docs/20_koncepcja/weryfikacja_runda2_V1.md`. Wyniki kontroli: walidacja rdzenia 0/0; `audyt_wt.py` — 0 NIEZGODNE,
4 UWAGI świadome; `test_wskazniki`, `test_pipeline --szybko`, `test_obliczenia_*` zaliczone; PB-AR-01…10 — QA OK.
H zabudowy 10,27 m, WT §6 9,97 m (`lamela.wskazniki`).

| uwaga V1 → decyzja (do rundy 3) | podstawa |
|---|---|
| V1-01 WZ-09a/b/c „ZŁY” (ψ 0,301, izolacja przerwana), brak w §14.2 F → dopisać do pozycji otwartych, blok u podstawy SWG o niższej λ, przeliczyć | brief §9 pkt 1–2; PN-EN ISO 14683/10211 |
| V1-02 cokół 0,12 m na filarkach przy bramie BR1 → OL przy progu bramy + filarki albo obniżenie; zwolnienie w `drenaz.py` tylko szer. drzwi + 0,15 | brief §9 pkt 4; W-019 |
| V1-03 przekroje/elewacje: WT §6 „9,79 m” z `views/section.py` → brać z `lamela.wskazniki` (zespół rysunków) | K-3; WT §6 |
| V1-04 ST2Z do lica ETICS → przyciąć do lica konstrukcji, łącznik PL-2 w strefie izolacji | A2 K-1; R-W6; W-272 |
| V1-05 wyspa z hokerami na PB-AR-01 → mapowanie `stools` w `views` + `hokery: 0` w modelu | A3 K-1 |
| V1-06 żebra osiowe poza czołem płyty, warstwa ŻB POD-P0 = PF1 → licować (BO), usunąć dublowanie | K-12; PN-EN ISO 13793 |
| V1-07 decyzja Inwestora K-13 (kratownica z pnączami, osłona PC) — niewprowadzona → wprowadzić | K-13; W-024 |
| V1-08…V1-14 drobne (rzut dachu, PBC w audycie, filarki/słupy, obróbki attyk, stare wartości §12/§13, korona DR1, klatki) | raport V1 §7 |

## 15. Rejestr zmian — wydanie

Wejście: decyzja Inwestora K-13 (brief §10), weryfikacje niezależne `weryfikacja_runda2_V1.md` i `weryfikacja_runda2_V2.md` (w całości),
kontrola funkcji V3 (niewykonana przez weryfikatora — wykonana w tym etapie skryptem), listy otwarte: `poprawki_runda2_wejscie.md`,
§13–14 (w tym 14.2 F), `projekt/08_obliczenia/mostki/REKOMENDACJE.md`, `projekt/*/BRAKI_DANYCH.md`. Zmiany konstrukcyjne
z `projekt/04_PT_konstrukcja/REKOMENDACJE_MODEL.md` — poza zakresem (następny etap „Konstrukcja”). Zapis: uwaga → decyzja → podstawa.
Źródło zmian: `tools/buduj_model.py` (model/*.yaml generowane); rozszerzenie schematu i rdzenia opisane w `docs/SCHEMAT_MODELU.md` §2, §10.
Bryły A/B/C/G, linie D/E, sylweta „S”, funkcje pomieszczeń i przejścia — bez zmian.

### 15.1 Decyzja Inwestora K-13 — zielona ściana i osłona jednostki PC (V1-07, V2 N-8, A3 D-12)

| Uwaga | Decyzja | Podstawa |
|---|---|---|
| K-13 — elewacja ogrodowa bryły G (S0-02) i jednostka PC na osi widoku | **wprowadzona.** Nowa sekcja modelu `elementy_zewn` (rdzeń: walidacja, IR, elewacje/przekroje, PZT, 3D; SCHEMAT §10.1): **KR-1** — kratownica stalowa ocynkowana (siatka 0,30 m, rama 40×40) w płaszczyźnie 0,15 m przed licem ETICS, pełna wysokość x 14,45–15,95 (+0,05…+3,45, pod PL-D); **KR-2** — panel nad jednostką PC od +1,50 (przestrzeń zasysania za urządzeniem wolna); konsole ze stali nierdzewnej z przekładką termiczną, najniższy rząd +0,40 (≈ 0,7 m nad terenem, poza strefą uszczelnienia cokołu), dolna krawędź kratownicy wolna — **bez przebić hydroizolacji cokołu**; pnącza wijące/owijające (bez przylg na ETICS) z pasa gruntu **Z7** (x 14,45–15,10, poza strefą R290; warstwa drenażowa → rozsączanie w piaski, bez wpustów; od cokołu XPS + membrana kubełkowa + obrzeże), dobór gatunków — [DO UZUPEŁNIENIA] (arch. krajobrazu). **OS-PC** — ażurowa osłona z lamel pionowych (≈ 60 % prześwitu) z 3 stron, otwarta od ściany i od góry (PL-D nad), prześwit ≥ 0,10 m nad terenem (R290 cięższy od powietrza), odstępy od urządzenia 1,0 m (wylot) i 0,6 m (boki) — do potwierdzenia wg DTR; strefa R290 1,0 m wolna od otworów, wpustów, studzienek i zagłębień. Obiekt PC-JZ: `strefa_r`, `wym` (przykładowe — [DO UZUPEŁNIENIA wg DTR]), `oslona`. | brief §10; brief §9 pkt 1–2; W-024, W-156 |
| mostki punktowe konsol | **WZ-17** (typ `kotwa`): liczba konsol z modelu, χ ≤ 0,010 W/K na konsolę (wymaganie = wartość w H_TB; potwierdzić deklaracją/3D); rdzeń obliczeń energii czyta `chi` z modelu | PN-EN ISO 14683, 10211; W-248 |
| rysunki / 3D | elewacja S: kratownica i osłona (materiał STAL_OCYNK w legendzie kolorystyki); PZT-01/02: linia zielonej ściany i osłona PC (legenda), opis „zielona ściana”; 3D: pręty, konsole, pnącza, lamele, bryła jednostki; testy `test_pipeline`: `test_elementy_zewn_walidacja`, `_ir`, `_lamela` | RPB §20; SCHEMAT §10.1 |

### 15.2 Weryfikacja V1 (WT/MPZP, geometria) — uwagi istotne i wybrane drobne

| Uwaga V1 | Decyzja | Podstawa |
|---|---|---|
| V1-01 / V2 N-6 — WZ-09a „ZŁY”, generator bez uskoku PF1/PF2 | **przyjęta.** Generator węzła dom–garaż odwzorowuje uskok płyt (0,15 m) i żebro pod SWG z `fundamenty` (`mostki2d.katalog_dod._uskok_zebro`); blok u podstawy SWG: beton komórkowy 600 → **nośny blok termoizolacyjny BLOK_TERM** (λ ≤ 0,045, ETA / lub równoważny; nośność 1. warstwy — PT-K); wełna SWG od garażu po czole uskoku do wierzchu PF2. Wynik na geometrii modelu: ψ_iu **0,406** (poprzednie 0,301 dotyczyło płyty bez uskoku), f_Rsi **0,901** ≥ 0,72. Wariant z przerwą termiczną PF2 przy żebrze (XPS 10 cm) daje 0,385 — ścieżka ciepła przez żebro i grunt; przerwy nie wprowadzono (zmiana konstrukcyjna o małym efekcie). **Świadoma akceptacja**: ocena „ZŁY” (test ołówka — płyta ciągła pod SWG) przy spełnionym f_Rsi; ψ wliczone w H_TB (b_u = 0,8); WZ-09a/b/c w pozycjach otwartych PT-AR-D. | brief §9 pkt 1–2; PN-EN ISO 10211, 13789; W-248 |
| V1-02 / V2 N-3, N-4 — cokół przy filarkach BR1 (0,12 m), filar S0-05 (0,04 m), krawędzie podestów | **przyjęta.** Korytka odwodnienia liniowego **przy licu**: **OL-7** (próg bramy BR1 na całą szerokość ściany pn. garażu z filarkami, → SEP-1) i **OL-7a** (ściana S0-05 we wnęce wejścia); OL-6 przy licu (T3); podest T2 zawężony do szer. drzwi + 0,15 m (x 9,90–11,70), T3 od x 12,30 (bez nakładania na T1), podest DZ2 = szer. drzwi + 0,15 m; krawędzie podestów, fartucha i dojścia U2 w pasie 0–2,3 m jako obrzeża (punkty projektowane 0,03 m za krawędzią). Moduł `drenaz.py`: TIN rzędnych projektowanych co 0,10 m, strefa progu = szer. otworu + 0,15 m, OL ≤ 1,5 m od progu, korytka `przy_licu`. **Wynik (TIN): cokół min 0,316 m poza strefami, spadek ≥ 3,0 % na wszystkich ścianach.** | brief §9 pkt 4, 6; W-019; DIN 18533-1 (pomocniczo) |
| V1-03 — przekroje/elewacje „H = 9,79 m” | **przyjęta.** `views.section.building_height` → `lamela.wskazniki` (`wysokosc_WT6`); arkusze: H = 9,97 m | K-3; WT §6 |
| V1-04 — ST2Z do lica ETICS | **przyjęta.** ST2Z y −0,09…5,215 (lico konstrukcji); łącznik PL-2 w pasie ocieplenia; katalog mostków przeliczony: WZ-07a 0,152 (L 5,30 m), WZ-16a 0,189 (f_Rsi 0,820) | A2 K-1; R-W6; W-272 |
| V1-05 — wyspa z 3 hokerami, płyta od jadalni | **przyjęta.** `wyposazenie`: `hokery: 0`, `plyta_strona: E`; `views.plan` mapuje `hokery`/`krzesla` → `stools` i stronę płyty (symbol `kitchen_island(hob_side)`) | A3 K-1 |
| V1-06 — żebra poza czołem płyty; izolacja cokołu −0,45 vs żebro −0,40; warstwa ŻB POD-P0 = PF1 | **przyjęta w części modelu:** rdzeń — ocieplenie cokołu do spodu płyty fundamentowej (= wierzch żebra, bez kolizji); IR — podłoga na płycie bez warstwy konstrukcyjnej (płyta = element `fundamenty`), XPS/podsypka pod każdą płytą (PF1, PF2) poza żebrami. **Licowanie żeber z czołem płyty — etap „Konstrukcja”** (REKOMENDACJE_MODEL p. 5.1). | K-12; PN-EN ISO 13793 |
| V1-09 — PBC i A_z+ w audycie własną metodą | **przyjęta.** `audyt_wt.py`: wartości z `lamela.wskazniki`, metoda audytu kontrolnie w opisie | K-3 |
| V1-11 — lamele w podsufitce PL-3; T1/T3 | **przyjęta:** LAM-S/W/E do +8,96; T3 od x 12,30. Obróbka attyk przy ścianie wyższej, nadproża N2/N3, dublowanie ETICS w narożach — do PT (drobne, bez wpływu na wskaźniki) | spójność modelu |
| V1-12 — nieaktualne wartości §4, §7, §12, §13 | **przyjęta:** §4 (D1P, O0-16 D2), §7 (czerpnia/wyrzutnia, elewacja G) zaktualizowane; §12, §13 oznaczone jako stan historyczny | K-3 |
| V1-13 / V2 N-14 — korona DR1 | **przyjęta:** korona dojrzałej lipy zachowawczo 10 m [DO WERYFIKACJI — dendrolog], pień y −23,5: 1,5 m od NCH-1 (≥ 1,0), 9,2 m od granicy pd. | W-144; K-2 |
| V1-08 (rzut dachu: PV, PA, czerpnia), V1-10 (filarki ↔ słupy SL — REKOMENDACJE_MODEL p. 3, 8), V1-14 (klatki, PN-ISO 9836) | przekazane: rysunki / etap „Konstrukcja” / PT | — |
