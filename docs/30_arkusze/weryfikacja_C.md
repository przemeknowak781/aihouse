# Weryfikacja C — czytelność i jakość rysunkowa po ekonomicznym układzie arkuszy

Data: 2026-09-25. Weryfikator niezależny (C). Kodu ani konfiguracji nie zmieniano.

Zakres: 33 arkusze w czterech kompletach i ich tomy PDF:
- PZT: `projekt/02_PZT/rysunki`, 3 arkusze;
- AR (PAB): `projekt/03_PAB/rysunki`, 5 arkuszy;
- IS: `projekt/05_PT_instalacje_sanitarne/rysunki`, 11 arkuszy;
- IE: `projekt/06_PT_instalacje_elektryczne/rysunki`, 14 arkuszy.

Kompletów BO i detali nie oceniano, bo nadal są w pracy.

Metoda:
1. Każdy arkusz obejrzano w całości (render PDF, ok. 1800 px), a miejsca gęste we wycinkach 150–300 dpi (×2–×3).
2. Skrypt przeanalizował tekst we wszystkich PDF: wysokość pisma (wersaliki = rozmiar em × 0,688), nakładanie się napisów, wyjście tekstu poza arkusz.
3. Sprawdzono siatkę odniesień, znaki centrujące, tomy (puste strony, spis) oraz raporty `raport_widokow.json`.

Pliki robocze: `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/arkusze/weryfC/` (`analiza_tekstu.py`, `tekst.json`, `wytnij.py`, `img/`).

## 1. Wynik ogólny

Ekonomia **nie zepsuła czytelności rysunków**. Wszystkie widoki mają skale bez zmian: 1:50 dla AR/IS/IE, 1:200 i 1:500 dla PZT (RPB § 9 spełniony). Pismo należy wyłącznie do szeregu 1,8 / 2,5 / 3,5 / 5,0 mm. Żaden napis nie ma mniej niż 1,8 mm i żaden nie wychodzi poza arkusz; wyjątkiem jest oznaczenie formatu w marginesie, które stoi tam celowo i nie jest obcięte. Tytuły widoków stoją przy widokach. Tabliczka jest w prawym dolnym rogu, a lewy margin ma 20 mm. Znaki składania i centrujące nie wchodzą w treść. Legendy są na każdym arkuszu. Tomy nie mają pustych stron: spis A4 plus arkusze, liczba stron zgodna ze spisem.

Wykryte problemy dzielą się na dwie grupy:
- **Skutki upakowania** (pkt 2.3, 2.6–2.10): obcięte komórki tabel PZT mimo wolnego miejsca w kolumnie, bloki dosunięte do ramki, róża i podziałka odsunięte od tabliczki (PT-IE-07), legenda linii oderwana od pozostałych legend (PB-AR-03) oraz prawie pusty arkusz PT-IE-13.
- **Wady generatorów widoków** (pkt 2.1, 2.2, 2.4, 2.5): są niezależne od układu, ale widać je na arkuszach PAB/PT. To nakładanie się opisów na ściany i inne opisy w rzutach AR, tabele warstw przecięte liniami na przekrojach oraz średnice przekreślone liniami w rozwinięciach IS.

## 2. Problemy (od najpoważniejszych)

### 2.1 [istotny] PB-AR-01, 02, 03: opisy urządzeń i drzwi nachodzą na ściany i na siebie (`views/plan.py`)
- **PB-AR-01**, pom. 1.12:
  - „wodomierz + zawór antyskażeniowy (PN-EN 1717)” przecina wymiar 269⁵ i ścianę zewnętrzną, a potem wychodzi poza budynek;
  - „rozdzielnica główna RG” i „rozdzielacz ogrzewania podłogowego P0” leżą na szrafurze ściany;
  - drugi napis „CWU 300 l” leży na okręgu symbolu;
  - znacznik D4 zasłania DG1.
- **PB-AR-01**: w pasie 1.07 wisi para „1182”/„857” bez linii wymiarowej, a „1182” jest narysowane dwa razy.
- **PB-AR-02**, hol 2.01:
  - „rozdzielacz ogrzewania podłogowego P1 (w holu)” przecina ścianę i wychodzi poza obrys;
  - dwa znaczniki D1 z opisami „90/210” leżą jeden na drugim.
- **PB-AR-03**, pom. 3.07: „REKUPERATOR” nachodzi na „rozdzielacz ogrzewania podłogowego P2”. To ok. 10 mm nakładania, potwierdzone analizą PDF.

**Poprawka:**
- Opisy wyposażenia prowadzić odnośnikiem na wolne pole z testem kolizji ze ścianami i z innymi opisami. Tak robi to już IE: „D14 RACK…”, „RG — rozdzielnica…”.
- Znaczniki drzwi, które się pokrywają, rozsuwać.
- Usunąć zdublowane i osierocone liczby wymiarowe.

### 2.2 [istotny] PB-AR-04: tabele opisu warstw leżą na przekroju (`views/section.py`)
- Tabele ST1/POD-1, OK1, POD-0 i DZ1 przecinają osie, linie wymiarowe „277” i elementy przekroju.
- Numer pomieszczenia „2.02” wchodzi w nagłówek tabeli ST1.
- Dwa razy występuje wiersz „Tynk gipsowy maszynowy 1,5 cm 1 cm”, z podwójną grubością w treści.
- Nagłówki są ucięte „…”.

Na tym samym arkuszu pod przekrojem A-A zostaje puste pole ok. 410×112 mm.

**Poprawka:**
- Białe tło (maska) pod tabelami warstw albo wyniesienie ich odnośnikiem w wolne pole.
- Deduplikacja warstw i formatowanie grubości bez powtórzeń.

### 2.3 [istotny] PZT-02, PZT-03: obcięte komórki tabel („…”), choć kolumna ma wolną szerokość
- **PZT-02, RZĘDNE CHARAKTERYSTYCZNE**: „T2 — płyty betonowe 60…” i „T3 — płyty betonowe 60…” po obcięciu wyglądają identycznie.
- **PZT-02, ODWODNIENIE POWIERZCHNIOWE**: „pas zach. → ogród p…”, „grunt (piaski, ZWG…”.
- **PZT-02, NAWIERZCHNIE UTWARDZONE**: „deska kompozytowa na lega…”, „fundament jednostki zewn.…”, „płyty betonowe 60×60, spa…”.
- Tabele kończą się ok. 45 mm przed ramką, a tekst uwag w tej samej kolumnie sięga ramki.
- **PZT-03, SIECI I PRZYŁĄCZA**: „2 × HDPE Ø40 + mikrokabel świ…”, „przelew zbiornika DN160 do ni…”, „kanalizacja teletechniczna /…”, „gazociąg PE 63 (nie wykorzyst…”.
- **PZT-03, OBIEKTY**: „…w osłonie lamelowe…”.
- **PZT-03, na planie**: „t — 2 × HDPE Ø40 + mikrokabel światło…”, „kd3 — przelew zbiornika DN160 do niecki…”.

**Poprawka:** w tabelach PZT użyć `table(..., zawijaj=True)`, czyli poprawki silnika z AR 2, albo rozciągnąć kolumny do szerokości bloku. Etykiet sieci na planie nie ucinać, tylko łamać na dwie linie.

### 2.4 [istotny] PT-IE-14: opisy obwodów na schemacie RG ucięte
Ok. 20 z 36 odejść kończy się „…”, na przykład „Gniazda P0: 0.10 Pokój gościnny / gabinet, 0…” i „Oświetlenie zewnętrzne (wejście, elewacje, ta…”. Tymczasem pod opisami, wewnątrz ramki RG, zostaje ok. 30–35 mm wolnego pola.

**Poprawka:** opisy łamać na 2 linie (obrót 90°) albo wykorzystać pełną długość do szyny PE. Pełną listę odbiorników można też odesłać do tabeli obwodów.

### 2.5 [istotny] PT-IS-10: średnice podejść przekreślone liniami
W rozwinięciu kanalizacji pionowe napisy „Ø110”, „Ø50” i „Ø40” stoją osią na liniach podejść, więc linia przechodzi przez środek tekstu. Przy „zasobnik c.w.u.” czerwona linia TZM przecina napis.

**Poprawka:** przesunąć opis obok linii o ok. 1 mm (strona lewa) w generatorze rozwinięć (`views/instalacje/`).

### 2.6 [drobny] PT-IS-11, PT-IE-14: pusty blok „OZNACZENIA” i napisy na liniach schematu
- Blok zawiera jedną pozycję („linie schematu — wg legendy na rysunku”) i dubluje legendę umieszczoną w samym schemacie.
- Na PT-IS-11 linia wody zimnej przecina napisy „cyrkulacja czasowa 134 dm³/h” oraz „grzałka el. — dezynfekcja 75 °C”.

**Poprawka:** przenieść legendę schematu do bloku OZNACZENIA albo blok pominąć. Napisy odsunąć od linii.

### 2.7 [drobny] Brak siatki odniesień na 7 arkuszach
Brakuje jej na PZT-02 (400×594), PT-IS-11 (580×420), PT-IE-02 i 08 (690×297), PT-IE-03 i 09 (570×297) oraz PT-IE-06 (730×297). Przyczyną jest próg `W·H ≥ A2` w `draft/sheet.py`, który formaty niestandardowe o długości 690–730 mm pomijają. Pozostałe arkusze tych samych kompletów mają siatkę, więc komplety są niejednolite.

**Poprawka:** siatkę rysować na wszystkich arkuszach poza A4 albo ustawić próg na dłuższym boku (> 420 mm).

### 2.8 [drobny] PT-IE-07: róża i podziałka u góry arkusza, daleko od tabliczki
Podziałka i N stoją nad rzutem przy legendzie, ok. 300 mm od tabliczki; na pozostałych arkuszach są nad tabliczką. Arkusz ma też duże puste pola: ok. 300×90 mm nad rzutem i ok. 300×115 mm pod tytułem. Wypełnienie wynosi 71 %.

**Poprawka:** różę z podziałką przenieść nad tabliczkę. Sprawdzić format 690×420 dla tego samego rzutu parteru (tak jak PT-IE-01): daje 0,290 m² zamiast 0,309 m².

### 2.9 [drobny] PT-IE-13: arkusz prawie pusty
Rzut dachu 1:50 na 690×420 zawiera tylko podkład, dwa opisy i jedną linię wyrównawczą. Wypełnienie wynosi 66 %, a puste pole ok. 190×175 mm. Podkład jest ten sam co na PT-IE-10 (PV, rzut dachu, 690×420).

**Poprawka:** rozważyć połączenie treści IE-13 z IE-10 na jednym arkuszu, co daje −0,29 m² i −10 warstw A4. Druga możliwość to mniejszy format.

### 2.10 [drobny] Bloki dosunięte do ramki i ciasne odstępy
- Na PT-IS-02 i PT-IS-07 prawa krawędź bloku „OBJAŚNIENIA I UWAGI” pokrywa się z linią ramki.
- Na PB-AR-05 kody kolorów w tabeli materiałów stoją 1,6 mm od ramki.
- Na PT-IS-02 tytuł drugiego widoku jest przesunięty za dolny znak centrujący (odstęp ok. 2,5 mm), a jego podkreślenie stoi ok. 2 mm nad ramką.

**Poprawka:** zapas bloków od ramki co najmniej 3 mm (poza tabliczką) i tytułów widoków co najmniej 4 mm.

### 2.11 [drobny] PB-AR-03: legenda „OZNACZENIA LINII” oderwana od pozostałych legend
Stoi między rzutem II piętra a rzutem dachu, ok. 400 mm od „OZNACZENIA MATERIAŁÓW” i uwag (raport: `kolejnosc_czytania: false`). Pod podziałką w dolnym pasie zostaje wolne pole ok. 215×50 mm, w którym zmieściłaby się legenda o wymiarach ok. 120×20 mm.

**Poprawka:** wskazać silnikowi grupę legend albo umieścić legendę w dolnym pasie.

### 2.12 [drobny] PB-AR-03 (dach) i PZT-01/03: napisy przecięte liniami
- Na rzucie dachu opisy D1 i D4 przecinają osie konstrukcyjne.
- Na PZT-01 „zielona ściana” leży na wymiarze 18,98, a opis działki na okręgu drzewa.
- Na PZT-03 „L = 0,75 m (model: 0,80 m)”, „e — ZKP w linii ogrodzenia” i „L = 3,47 m” leżą na liniach sieci.

**Poprawka:** maska tła pod opisami w widokach (`views/plan.py`, `views/site*.py`).

### 2.13 [drobny] Miara wypełnienia zawyża wynik na arkuszach z dużym pustym polem
PT-IE-04 ma „W obw.” = 90 %, choć pod tytułem widoku zostaje pole ok. 170×235 mm. Jest to ten sam objaw, który zespół AR zgłosił dla PB-AR-01. `pusty_prostokat_mm` w raporcie podaje dla IE-04 tylko 360×52 mm.

**Poprawka:** w `tools/metryki_arkuszy.py` liczyć największy pusty prostokąt bez domknięcia 6 mm scalającego bloki.

## 3. Czego nie stwierdzono
- Pismo poniżej 1,8 mm: brak. Histogram: 1,8 / 2,5 / 3,5 / 5,0 mm.
- Bloki kolumny wchodzące na widok: brak. Tytuły widoków odklejone od widoków: brak.
- Brak legendy na arkuszu: brak. Puste strony w tomach: brak.
  - tom_PZT: 4 strony;
  - tom_widoki: 6 stron;
  - tom_PT-IS: 12 stron;
  - tom_PT-IE: 15 stron.
- Znaki centrujące na treści: brak. Tabliczka zawsze w prawym dolnym rogu, na wierzchu po złożeniu.
- Tabela pomieszczeń AR (PB-AR-01, 02, 03): komórki się łamią i nic nie nachodzi, więc poprawka silnika działa.
- Glif ⌀ w tablicy materiałów PB-AR-05: jest wyświetlany jako „Ø12”, poprawnie.
