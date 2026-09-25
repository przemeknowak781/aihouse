# R3 — Warunki techniczne, jakim powinny odpowiadać budynki (WT): status prawny i rejestr wymagań

**Projekt:** Dom LAMELA. Budynek mieszkalny jednorodzinny wolnostojący: 3 kondygnacje nadziemne, bez podpiwniczenia, dachy płaskie, 1 lokal mieszkalny, garaż 2-stanowiskowy w bryle, instalacje all-electric. Działka przykładowa pod Poznaniem, teren MN.
**Domena:** R3. Status prawny WT oraz wymagania techniczno-budowlane dla wolnostojącego budynku jednorodzinnego.
**Data weryfikacji:** 2026-09-24/25. Dziennik Ustaw sprawdziłem w API ELI do **Dz.U. 2026 poz. 1244** (23.09.2026). Pozycje 1245–1250 zwracały HTTP 404 przy ponownym sprawdzeniu 25.09.2026.
**Metoda:**
* Teksty i metadane aktów pobrałem z API ELI Sejmu (`api.sejm.gov.pl/eli/...`, pliki PDF), a tekst wyciągnąłem biblioteką pymupdf. Źródła pierwotne mają w tabeli „TAK”.
* Portale branżowe, izby i gov.pl mają „NIE”.
* Treści Polskich Norm nie miałem. Wartości liczbowe pochodzące z norm oznaczam **NIEZWERYFIKOWANE**.

**Pliki robocze:** `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R3/`:
* `wt_clean.txt`: tekst WT (t.j. 2022/1225);
* `t_*.txt`: pozostałe akty;
* `meta_*.json`: metadane ELI;
* `wt.py`: ekstraktor paragrafów.

Skróty użyte w dokumencie:
* **WT**: rozp. MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (Dz.U. 2002 nr 75 poz. 690), t.j. Dz.U. 2022 poz. 1225, zm. Dz.U. 2023 poz. 2442, Dz.U. 2024 poz. 474, Dz.U. 2024 poz. 726;
* **PB**: ustawa Prawo budowlane, t.j. Dz.U. 2026 poz. 524 ze zm.;
* **UD**: ustawa z 19.07.2019 o zapewnianiu dostępności osobom ze szczególnymi potrzebami (Dz.U. 2019 poz. 1696, t.j. Dz.U. 2024 poz. 1411).

---

## 1. Streszczenie stanu prawnego (na 2026-09-25)

### 1.1 WT z 2002 r. wygasły z mocy ustawy, a nowych WT nie wydano

1. **Podstawa wygaśnięcia.** Art. 66 UD stanowi, że dotychczasowe przepisy wykonawcze wydane na podstawie art. 7 ust. 2 i 3 oraz art. 34 ust. 6 pkt 1 PB „zachowują moc do dnia wejścia w życie przepisów wykonawczych wydanych na podstawie art. 7 ust. 2 i 3 […] w brzmieniu nadanym niniejszą ustawą, **nie dłużej jednak niż przez 84 miesiące od dnia wejścia w życie niniejszej ustawy**”. Tak brzmi on w t.j. Dz.U. 2024 poz. 1411, po zmianie Dz.U. 2024 poz. 1081. Termin wydłużano dwa razy:

   | Brzmienie art. 66 UD | Termin | Źródło |
   |---|---|---|
   | pierwotne | 36 miesięcy | Dz.U. 2019 poz. 1696 |
   | zmiana | 60 miesięcy | Dz.U. 2022 poz. 975, art. 2 |
   | zmiana | 84 miesiące | Dz.U. 2024 poz. 1081, art. 1, w życie 03.08.2024 |

   UD weszła w życie 20.09.2019, więc termin upłynął 20.09.2026. Metadane ELI aktu Dz.U. 2002 nr 75 poz. 690 podają:
   * `status: "uznany za uchylony"`;
   * `repealDate: 2026-09-21`;
   * „Uchylenia wynikające z: DU/2019/1696”.

   Ten sam status mają t.j. Dz.U. 2022 poz. 1225 oraz wszystkie akty zmieniające, w tym 2023/2442, 2024/474 i 2024/726.

   Z tej samej przyczyny straciły moc także:
   * rozp. MSWiA z 16.08.1999 w sprawie warunków technicznych **użytkowania** budynków mieszkalnych (ELI DU/1999/836);
   * rozp. MG z 26.04.2013 w sprawie warunków technicznych dla **sieci gazowych** (Dz.U. 2013 poz. 640);
   * rozp. MŁ z 21.04.1995 w sprawie warunków technicznych zasilania energią elektryczną obiektów budowlanych łączności (ELI DU/1995/271).

   Lista „Akty uznane za uchylone” w metadanych ELI UD.
2. **Nowych WT dla budynków nie ma.**
   * Przejrzałem wykaz Dz.U. 2026 (poz. 1–1244) oraz Dz.U. 2025 (1900 pozycji) i przeszukałem ELI (`title=warunków technicznych, jakim powinny odpowiadać budynki`). Wynik: w latach 2025–2026 nie ogłoszono nowego rozporządzenia o WT dla budynków.
   * W 2026 r. wydano tylko WT dla budowli hydrotechnicznych (Dz.U. 2026 poz. 692) i kolejowych (Dz.U. 2026 poz. 1225).
   * Projekt nowych WT ma numer RCL **12398903**. Projekt nosi datę 09.06.2025, konsultacje ogłoszono 13.06.2025 [S-GOV]. Według źródła wtórnego z 19.07.2026 był „po konsultacjach publicznych, ale przed komitetami Rady Ministrów” [S-PZB]. Strony RCL zwracały 503 lub zrywały połączenie, więc **aktualnego etapu w RCL nie zweryfikowałem**.
3. **Przepis epizodyczny: art. 102a–102c PB.** Dodał go art. 2 pkt 4 ustawy z 31.07.2026 o zmianie ustawy o samorządach zawodowych architektów oraz inżynierów budownictwa oraz ustawy – Prawo budowlane (**Dz.U. 2026 poz. 1161**, ogłoszonej 01.09.2026). Według art. 5 tej ustawy art. 2 pkt 4 wszedł w życie „z dniem następującym po dniu ogłoszenia”, czyli **02.09.2026**. Pozostałe przepisy ustawy wchodzą w życie 02.10.2026, co wyjaśnia datę `entryIntoForce: 2026-10-02` w ELI.

   Brzmienie (cytat):
   > **Art. 102a. 1.** W okresie 18 miesięcy od dnia 20 września 2026 r. projekt zagospodarowania działki lub terenu lub projekt architektoniczno-budowlany, może zostać sporządzony zgodnie z przepisami wydanymi na podstawie art. 7 ust. 2 pkt 1, obowiązującymi do dnia 19 września 2026 r. do: 1) wniosku o pozwolenie na budowę, 2) wniosku o wydanie odrębnej decyzji o zatwierdzeniu projektu zagospodarowania działki lub terenu lub projektu architektoniczno-budowlanego, 3) zgłoszenia budowy – po złożeniu organowi prowadzącemu postępowanie oświadczenia inwestora o stosowaniu tych przepisów.
   > **2.** W przypadku złożenia przez inwestora oświadczenia, o którym mowa w ust. 1, inwestor sporządza projekt techniczny zgodnie z przepisami wydanymi na podstawie art. 7 ust. 2 pkt 1, obowiązującymi do dnia 19 września 2026 r.
   > **4.** W przypadku złożenia przez inwestora oświadczenia, o którym mowa w ust. 1, przepisy wydane na podstawie art. 7 ust. 2 pkt 1, obowiązujące do dnia 19 września 2026 r. stosuje się do decyzji administracyjnych dotyczących całego zamierzenia budowlanego.

   Pozostałe przepisy epizodyczne:
   * **Art. 102a ust. 3** rozciąga ust. 1 na dokumenty legalizacyjne (art. 48b ust. 2 i 3 PB) i obowiązek z art. 51 ust. 1 pkt 3 PB. Dom LAMELA tego nie dotyczy.
   * **Art. 102b** pozwala inwestorowi stosować stare WT do budowy z art. 29 ust. 2 i robót z art. 29 ust. 4 PB, czyli takich, które nie wymagają ani pozwolenia na budowę, ani zgłoszenia. *(Poprawka weryfikacji: wcześniej było „czyli bez projektu”.)*
   * **Art. 102c** pozwala przez 18 miesięcy utrzymywać i użytkować budynki mieszkalne według przepisów wydanych na podstawie art. 7 ust. 3 pkt 1, tj. rozp. z 1999 r.
4. **Stan dla wniosków składanych po 20.09.2026.**
   * **Z oświadczeniem z art. 102a:** PZT, PAB i PT sporządza się według WT w brzmieniu obowiązującym do 19.09.2026. Brzmienie to nie zmieniło się od 15.08.2024 (ostatnia zmiana: Dz.U. 2024 poz. 726). WT stosuje się także do wszystkich decyzji dotyczących zamierzenia, w tym zmian pozwolenia.
   * **Bez oświadczenia:** brak wiążącego aktu wykonawczego z art. 7 ust. 2 pkt 1 PB. Zostają art. 5 ust. 1 PB („w sposób określony w przepisach, w tym techniczno-budowlanych, oraz zgodnie z zasadami wiedzy technicznej”) oraz Polskie Normy jako wiedza techniczna. Organ sprawdza zgodność **PZT** z przepisami, „w tym techniczno-budowlanymi” (art. 35 ust. 1 pkt 2 PB), a bez oświadczenia nie ma dla PZT odniesienia normatywnego. Źródła wtórne oceniają tę sytuację jako „chaos interpretacyjny” i ryzyko sporów [S-IB1], [S-PDOIIB].
   * **Zgodność PAB z WT nie jest przedmiotem sprawdzenia przez organ** (art. 35 ust. 1 PB). Projektant odpowiada za nią sam.
5. **Rozbieżność dat.**
   * ELI przyjmuje utratę mocy z dniem 21.09.2026, więc ostatni dzień mocy to 20.09.2026.
   * Ustawodawca w art. 102a–102c przyjął, że WT obowiązywały „do dnia 19 września 2026 r.”, a okres przejściowy biegnie „od dnia 20 września 2026 r.”.

   Dla projektu nie ma to znaczenia, bo tekst WT był taki sam w obu datach. Koniec 18-miesięcznego okresu to 20.03.2028 według źródła wtórnego [S-IB2]. Bezpiecznie: wniosek z oświadczeniem złożyć **najpóźniej 19.03.2028**.
6. **Źródła wtórne:**
   * Komunikat ministerstwa z 18.09.2026: „Od dnia 20 września 2026 r. w okresie 18 miesięcy do budowy, wykonywania robót budowlanych oraz do utrzymywania i użytkowania budynków mieszkalnych stosuje się dotychczasowe przepisy wykonawcze”; prace nad nowym rozporządzeniem „są nadal prowadzone” [S-prawo], [S-IARP], [S-IB1].
   * Rekomendacje PIIB z 21.09.2026 [S-IB3].
   * Wzór oświadczenia PIIB z instrukcją. Artykuł o nim ukazał się 22.09.2026 [S-IB2]. Według artykułu: „Oświadczenie składa inwestor, nie projektant”; oświadczenie „nie wymaga przyjęcia, zatwierdzenia ani potwierdzenia”; wzoru PIIB „nie należy zmieniać”.
   * Wątpliwości PDOIIB [S-PDOIIB]:
     * postępowania wszczęte przed 20.09.2026 i niezakończone;
     * roboty z art. 29 ust. 3;
     * brak przedłużenia dla aktów z art. 7 ust. 2 pkt 2, np. WT dla sieci gazowych;
     * projekty bez oświadczenia.
   * **Rozbieżność co do nazwy ministerstwa.** Źródła wtórne przypisują komunikat „MRiT”. Według źródła pierwotnego (odnośnik 1 do Dz.U. 2026 poz. 597) działem „budownictwo, planowanie i zagospodarowanie przestrzenne oraz mieszkalnictwo” kieruje **Minister Finansów i Gospodarki**, na podstawie rozp. PRM z 25.07.2025 (Dz.U. 2025 poz. 997). Przypisanie komunikatu do urzędu: NIEZWERYFIKOWANE.
7. **Wniosek dla projektu.** Dom LAMELA projektujemy według **WT w brzmieniu na 19.09.2026**, stosowanych na podstawie **art. 102a PB**. Inwestor składa oświadczenie organowi razem z wnioskiem PB-1. PT sporządzamy według tych samych WT (art. 102a ust. 2). Każde powołanie się na WT w dokumentacji ma formę: „§ … rozporządzenia MI z 12.04.2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowanego na podstawie art. 102a ust. 1 i 2 PB (Dz.U. 2026 poz. 524 ze zm.)”.

### 1.2 Zmiany WT w latach 2022–2024 (brzmienie obowiązujące do 19.09.2026)

| Akt | W życie | Zmienione jednostki WT | Znaczenie dla domu jednorodzinnego |
|---|---|---|---|
| Dz.U. 2022 poz. 248 (w t.j. 2022/1225) | 17.02.2022 | § 267 ust. 1a–1b | Przewody wentylacyjne z materiałów palnych dopuszczone w domu jednorodzinnym z 1 lokalem |
| **Dz.U. 2023 poz. 2442**, w brzmieniu nadanym przez **Dz.U. 2024 poz. 474** (termin przesunięty z 01.04.2024 na **01.08.2024**) | 01.08.2024 | § 3 pkt 27, **§ 12 ust. 1–3, 6, 8, 10, 11**, § 20, § 39, § 40, § 56a, § 76, § 85a, § 95a, § 98a, **§ 326 ust. 2 pkt 1, ust. 4a, 4b**, zał. 1 (lp. 1a, 60a–68, 67a) | Nowe brzmienie odległości od granicy, w tym **§ 12 ust. 6** (1,5 m do okapów, balkonów, tarasów…) i ust. 10 („publicznie dostępny plac”). § 326 ust. 4a i 4b dotyczą domów z 2 lokalami, więc nas nie dotyczą. Nowe normy akustyczne w zał. 1: PN-B-02151-2:2018-01 |
| **Dz.U. 2024 poz. 726** | 15.08.2024 | **§ 12 ust. 1** (część wspólna: „każdą płaszczyznę powstałą w wyniku załamania lub uskoku ściany traktuje się jako oddzielną ścianę”), **§ 12 ust. 1a, 10a, zał. 1a** (rysunki), § 216 ust. 2 pkt 4–5, § 232 ust. 8–9, § 249 ust. 5a (drewno klejone) | Istotne dla elewacji w „S”: każdy uskok ściany ocenia się osobno |

Wcześniejsze zmiany, które przedstawiono w briefie jako aktualne wymagania: **A0max** usunięto z zał. 2, a nowe brzmienie zał. 2 obowiązuje od 01.01.2018 (Dz.U. 2017 poz. 2285, § 1 pkt 67). Wymóg „pokój ≥ 16 m²” (dawny § 94 ust. 2) usunięto tym samym aktem.

---

## 2. Tabela wymagań (WT w brzmieniu na 19.09.2026, stosowane na podstawie art. 102a PB)

Legenda ID:
* **S**: status prawny;
* **D**: definicje i klasyfikacja;
* **U**: usytuowanie;
* **Z**: zagospodarowanie działki;
* **B**: budynek i pomieszczenia;
* **K**: komunikacja, schody i bezpieczeństwo użytkowania;
* **IW**: woda;
* **IK**: kanalizacja;
* **IO**: ogrzewanie;
* **IV**: wentylacja;
* **IE**: elektryka;
* **P**: pożar;
* **H**: hałas i wilgoć;
* **E**: energia.

Kolumna „2023–24” = zmiana z Dz.U. 2023/2442 lub 2024/726. Linki w kolumnie URL (definicje na końcu dokumentu): [WT], [Z2442], [Z726] itd.

### 2.1 Status prawny

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| S-01 | WT z 2002 r. utraciły moc po 84 miesiącach od wejścia w życie UD (20.09.2019). ELI: „uznany za uchylony”, repealDate 2026-09-21 | art. 66 UD (t.j. Dz.U. 2024 poz. 1411; zm. Dz.U. 2024 poz. 1081, art. 1) | [D1411], [U1081], [WT-meta] | TAK | Historia terminu: 36 → 60 (Dz.U. 2022 poz. 975) → 84 mies. |
| S-02 | Brak nowego rozporządzenia o WT dla budynków w Dz.U. do poz. 1244/2026 | wykaz ELI DU/2026 i wyszukiwanie ELI | [DU2026], [SEARCH] | TAK | Projekt RCL 12398903, status NIEZWERYFIKOWANY (RCL niedostępne) |
| S-03 | Przez 18 miesięcy od 20.09.2026 PZT i PAB mogą być sporządzone według WT obowiązujących do 19.09.2026, po złożeniu przez inwestora oświadczenia organowi prowadzącemu postępowanie | art. 102a ust. 1 PB (dodany art. 2 pkt 4 Dz.U. 2026 poz. 1161; w życie 02.09.2026) | [U1161] | TAK | Oświadczenie składa inwestor. Wzór PIIB [S-IB2] (NIE) |
| S-04 | Przy oświadczeniu PT sporządza się według tych samych WT | art. 102a ust. 2 PB | [U1161] | TAK | Dotyczy części instalacyjnej, energetycznej i konstrukcyjnej PT |
| S-05 | Przy oświadczeniu stare WT stosuje się do decyzji administracyjnych dotyczących całego zamierzenia | art. 102a ust. 4 PB | [U1161] | TAK | Obejmuje np. zmianę pozwolenia, także po 20.03.2028 |
| S-06 | Organ sprawdza zgodność **PZT** z przepisami, w tym techniczno-budowlanymi. Zgodność PAB z WT nie jest sprawdzana | art. 35 ust. 1 pkt 2 PB (t.j. 2026/524) | [PB] | TAK | Odpowiedzialność za PAB spoczywa na projektancie |
| S-07 | Obiekt projektuje się „w sposób określony w przepisach, w tym techniczno-budowlanych, oraz zgodnie z zasadami wiedzy technicznej” | art. 5 ust. 1 PB | [PB] | TAK | Podstawa działania bez oświadczenia (ryzyko) |

### 2.2 Definicje i klasyfikacja

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| D-01 | **Wysokość budynku** mierzy się „od poziomu terenu przy najniżej położonym wejściu do budynku lub jego części, znajdującym się na pierwszej kondygnacji nadziemnej budynku, do górnej powierzchni najwyżej położonego stropu, łącznie z grubością izolacji cieplnej i warstwy ją osłaniającej, bez uwzględniania wyniesionych ponad tę płaszczyznę maszynowni dźwigów i innych pomieszczeń technicznych, **bądź do najwyżej położonego punktu stropodachu lub konstrukcji przekrycia budynku znajdującego się bezpośrednio nad pomieszczeniami przeznaczonymi na pobyt ludzi**” | WT § 6 | [WT] | TAK | Attyki i PV nie wliczają się do wysokości wg WT. MPZP może mierzyć inaczej. *Weryfikacja: uzupełniono pominiętą drugą część definicji (wariant „bądź do najwyżej położonego punktu stropodachu…”). Przy stropodachach ze spadkiem liczyć do najwyższego punktu nad pomieszczeniami.* |
| D-02 | Grupa wysokości: **niski (N)**, tj. „do 12 m włącznie nad poziomem terenu lub mieszkalne o wysokości do 4 kondygnacji nadziemnych włącznie” | WT § 8 pkt 1 | [WT] | TAK | Dom LAMELA = N |
| D-03 | **Kondygnacja**: pozioma część budynku między posadzkami. Za kondygnację uważa się też „przestrzeń na urządzenia techniczne, mającą średnią wysokość w świetle większą niż 2 m”. Nie są kondygnacją nadbudówki ponad dachem (obudowa wyjścia z klatki, pomieszczenia techniczne) | WT § 3 pkt 16 | [WT] | TAK | Pilnować limitu 3 kondygnacji nadziemnych (zob. P-02) |
| D-04 | Kondygnacja podziemna: zagłębiona co najmniej w połowie wysokości w świetle. Nadziemna: każda inna | WT § 3 pkt 17–18 | [WT] | TAK | Brak podziemia |
| D-05 | Teren biologicznie czynny wg WT obejmuje także „50% powierzchni tarasów i stropodachów z taką nawierzchnią […] o powierzchni nie mniejszej niż 10 m²” | WT § 3 pkt 22 | [WT] | TAK | Dach zielony garażu. Do wskaźników MPZP stosować definicję z przepisów planistycznych (poza R3) |
| D-06 | Kubatura brutto: suma kubatur kondygnacji w obrysie zewnętrznym. Wlicza się m.in. loggie, podcienia, ganki, balkony i tarasy (do wysokości balustrady). Nie wlicza się fundamentów, zewnętrznych schodów, gzymsów, daszków, attyk ponad dachem | WT § 3 pkt 24 | [WT] | TAK | Potrzebna do P-08 (PWP > 1000 m³) |
| D-07 | Pomieszczenia na stały pobyt ludzi to te, w których te same osoby przebywają > 4 h/dobę. Na czasowy pobyt: 2–4 h. Pomieszczenia < 2 h nie są przeznaczone na pobyt ludzi | WT § 4, § 5 ust. 1 pkt 1 | [WT] | TAK | Kuchnia = co najmniej czasowy pobyt |
| D-08 | Wymiary w WT rozumie się z wykończeniem. Szerokość drzwi mierzy się w świetle ościeżnicy, a skrzydło po otwarciu nie może jej pomniejszać | WT § 9 ust. 1–2 | [WT] | TAK | Rysunki PAB: wymiary w świetle wykończenia |
| D-09 | Odległości od granic i budynków mierzy się poziomo w miejscu najmniejszego oddalenia. Pominięcie ocieplenia dopuszczono tylko dla budynków istniejących | WT § 9 ust. 3–4 | [WT] | TAK | Mierzyć od lica ocieplenia lub okładziny |

### 2.3 Usytuowanie na działce

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| U-01 | Odległość budynku od granicy działki: **≥ 4 m** dla ściany z oknami lub drzwiami, **≥ 3 m** dla ściany bez okien i drzwi, „przy czym każdą płaszczyznę powstałą w wyniku załamania lub uskoku ściany traktuje się jako oddzielną ścianę” | WT § 12 ust. 1 pkt 1–2 i część wspólna | [Z2442], [Z726] | TAK | **2023–24** (pkt 1–4: 2442 od 01.08.2024; część wspólna: 726 od 15.08.2024) |
| U-02 | Ściana nierównoległa do granicy może stać bliżej niż 4 m, ale nie bliżej niż 3 m, jeśli zewnętrzna krawędź okna lub drzwi jest ≥ 4 m od granicy | WT § 12 ust. 1a | [Z726] | TAK | **2024**. Metodę określa zał. 1a (§ 12 ust. 10a) |
| U-03 | Ściana bez otworów w odległości 1,5 m od granicy lub przy granicy jest dopuszczalna, gdy przewiduje to MPZP | WT § 12 ust. 2 | [Z2442] | TAK | **2023–24**. MPZP 3MN (fikcyjny) tego nie przewiduje |
| U-04 | Odległość od granicy do okapu, gzymsu, balkonu, daszku nad wejściem, galerii, tarasu, schodów zewnętrznych, rampy lub pochylni: **≥ 1,5 m**. Do okna w dachu zwróconego ku granicy: **≥ 4 m** | WT § 12 ust. 6 pkt 1–2 | [Z2442] | TAK | **2023–24**. Wysunięte płyty 0,8–1,5 m traktować jako okapy lub gzymsy |
| U-05 | Odległości z ust. 1–9 nie są wymagane, gdy sąsiednia działka jest drogowa lub jest publicznie dostępnym placem | WT § 12 ust. 10 | [Z2442] | TAK | **2023–24**. Od strony ul. Lipowej obowiązuje linia zabudowy MPZP (6 m) |
| U-06 | § 12 ust. 4 pkt 3 (garaż przy granicy, długość ≤ 6,5 m, wysokość ≤ 3 m) dotyczy budowy **budynku** garażu. Garażu w bryle domu nie obejmuje | WT § 12 ust. 4 pkt 3 | [WT] | TAK | Garaż LAMELA spełnia U-01 jako część domu |
| U-07 | **Przesłanianie.** W poziomym kącie 60° od osi okna pomieszczenia na pobyt ludzi nie może być obiektu przesłaniającego, w tym części tego samego budynku, w odległości mniejszej niż jego wysokość przesłaniania (dla h ≤ 35 m). Wysokość mierzy się od dolnej krawędzi najniższego okna | WT § 13 ust. 1–2 | [WT] | TAK | Sprawdzić bryłę garażu i uskoki „S” względem okien P0/P1 |
| U-08 | **Nasłonecznienie:** pokoje mieszkalne ≥ **3 h** w dniach równonocy w godz. 7⁰⁰–17⁰⁰. W mieszkaniu wielopokojowym wystarczy 1 pokój | WT § 60 ust. 1–2 | [WT] | TAK | Elewacja ogrodowa S. Wykazać w PAB |
| U-09 | Budynek z pomieszczeniami na pobyt ludzi sytuuje się poza zasięgiem uciążliwości (hałas, pola EM, zalewanie itd.) albo stosuje się środki techniczne | WT § 11 | [WT] | TAK | Działka poza terenem zalewowym (MPZP) |

### 2.4 Zagospodarowanie działki

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| Z-01 | Dojście i dojazd do drogi publicznej. Szerokość jezdni dojazdu **≥ 3 m** | WT § 14 ust. 1 | [WT] | TAK | — |
| Z-02 | Oświetlenie elektryczne dojść i dojazdów nie jest wymagane dla budynków jednorodzinnych | WT § 14 ust. 4 | [WT] | TAK | — |
| Z-03 | Dojścia używane przez pojazdy gospodarcze i uprzywilejowane do 2,5 t muszą mieć nawierzchnię o odpowiedniej nośności | WT § 15 ust. 2 | [WT] | TAK | — |
| Z-04 | Utwardzone dojście 1,5 m do wejścia (§ 16) dotyczy tylko budynków wielorodzinnych, zamieszkania zbiorowego i użyteczności publicznej | WT § 16 ust. 1 | [WT] | TAK | Dla domu jednorodzinnego brak wymogu |
| Z-05 | Liczba stanowisk postojowych według MPZP | WT § 18 ust. 2 | [WT] | TAK | MPZP: ≥ 2 miejsca na lokal |
| Z-06 | Stanowiska postojowe (także zadaszone) do 10 miejsc: **≥ 7 m** od okien pomieszczeń na stały pobyt ludzi w budynku mieszkalnym. **≥ 3 m** od granicy działki | WT § 19 ust. 1 pkt 1 lit. a, ust. 2 pkt 1 lit. a | [WT] | TAK | — |
| Z-07 | Wyjątki od Z-06: 7 m nie obowiązuje dla **niezadaszonych** parkingów z 1–2 stanowisk na lokal w domu jednorodzinnym, przy budynku (ust. 5). 3 m od granicy nie obowiązuje, gdy stanowiska stykają się z niezadaszonym parkingiem sąsiada (ust. 6) albo sąsiednia działka jest drogowa (ust. 7) | WT § 19 ust. 5–7 | [WT] | TAK | Miejsca gościnne: maks. 2, niezadaszone, ≥ 3 m od granic E i W |
| Z-08 | Wymiary stanowiska dla samochodu osobowego: **2,5 × 5,0 m**. Dla osoby niepełnosprawnej: 3,6 × 5,0 m. Nawierzchnia utwardzona lub gruntowa stabilizowana, ze spadkiem | WT § 21 ust. 1 pkt 1–2, ust. 3 | [WT] | TAK | — |
| Z-09 | Na działce przewiduje się miejsce na pojemniki na odpady z możliwością segregacji (osłona lub pomieszczenie). Od miejsca dojazdu śmieciarki prowadzi utwardzone dojście | WT § 22 ust. 1–3 | [WT] | TAK | — |
| Z-10 | Odległości miejsca na odpady od okien (10 m) i od granicy (3 m) w zabudowie jednorodzinnej **nie określa się** | WT § 23 ust. 4 | [WT] | TAK | — |
| Z-11 | Działka ma mieć możliwość przyłączenia do sieci wodociągowej, kanalizacyjnej, elektroenergetycznej i ciepłowniczej. Za równorzędne uznaje się indywidualne źródło energii lub ciepła | WT § 26 ust. 1–2 | [WT] | TAK | Pompa ciepła = źródło indywidualne |
| Z-12 | Dla budynków niskich dopuszcza się odprowadzenie wód opadowych na własny teren nieutwardzony, do dołów chłonnych lub zbiorników retencyjnych. Zabrania się kierowania spływu na działkę sąsiednią | WT § 28 ust. 2, § 29 | [WT] | TAK | Zgodne z MPZP |
| Z-13 | Wykorzystanie deszczówki do WC lub podlewania wymaga odrębnej instalacji, niepołączonej z wodociągową | WT § 126 ust. 3 | [WT] | TAK | — |
| Z-14 | Studnia: oś ≥ 5 m od granicy (oraz inne odległości) | WT § 31 ust. 1 | [WT] | TAK | Nie projektujemy studni. Wymóg dotyczy tylko ewentualnej studni ogrodowej na wodę pitną |
| Z-15 | Ogrodzenie nie może stwarzać zagrożenia. Zakaz ostrych zakończeń i drutu kolczastego poniżej **1,8 m** | WT § 41 ust. 1–2 | [WT] | TAK | — |
| Z-16 | Bramy i furtki **nie mogą otwierać się na zewnątrz działki** | WT § 42 ust. 1 | [WT] | TAK | Brama przesuwna (wewnątrz działki) lub skrzydłowa do wewnątrz |
| Z-17 | Szerokość bramy w świetle **≥ 2,4 m**, furtki **≥ 0,9 m** | WT § 43 | [WT] | TAK | — |
| Z-18 | Teren wokół budynku ukształtowany ze spływem wody od budynku | WT § 316 ust. 2 | [WT] | TAK | Spadki opaski i terenu w PZT |
| Z-19 | Plac zabaw i teren biologicznie czynny 25% (§ 39–§ 40) dotyczą zabudowy wielorodzinnej, więc Domu LAMELA nie | WT § 39, § 40 | [Z2442] | TAK | **2023–24**. Wskaźnik 50% z MPZP |

### 2.5 Budynek i pomieszczenia

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| B-01 | Budynek ma wodę pitną (§ 45), instalację c.w.u. (§ 46), odprowadzenie ścieków (§ 47), miejsce na odpady (§ 48), ogrzewanie (§ 49), wentylację (§ 51) i instalację elektryczną (§ 53 ust. 1) | WT § 45–§ 53 | [WT] | TAK | — |
| B-02 | **Instalacja piorunochronna** wymagana dla budynków wyszczególnionych w PN dotyczącej ochrony odgromowej: PN-EN 62305-1:2011 i PN-EN 62305-2:2008 (analiza ryzyka) | WT § 53 ust. 2, § 184 ust. 3, zał. 1 lp. 1, 44 | [WT] | TAK | Wynik analizy ryzyka NIEZWERYFIKOWANY (do obliczenia w PT) |
| B-03 | Dźwig (§ 54), pochylnie i urządzenia dla niepełnosprawnych (§ 55) oraz instalacja telekomunikacyjna (§ 56) dotyczą budynków wielorodzinnych i UP, więc nas nie dotyczą | WT § 54–§ 56 | [WT] | TAK | — |
| B-04 | W pomieszczeniu na pobyt ludzi okna w świetle ościeżnic mają powierzchnię **≥ 1/8** powierzchni podłogi. W innym pomieszczeniu, w którym oświetlenie dzienne jest wymagane: ≥ 1/12 | WT § 57 ust. 2 | [WT] | TAK | Liczone w świetle ościeżnic, a nie jako powierzchnia szkła |
| B-05 | Wyłącznie sztuczne oświetlenie pomieszczenia na pobyt ludzi dopuszcza się tylko w przypadkach z § 58 | WT § 58 ust. 1 | [WT] | TAK | Garderoby, spiżarnia, pom. techniczne nie są przeznaczone na pobyt ludzi |
| B-06 | Drzwi wejściowe do budynku i mieszkania w świetle ościeżnicy: **≥ 0,9 × 2,0 m**. W drzwiach dwuskrzydłowych skrzydło główne ≥ 0,9 m | WT § 62 ust. 1 | [WT] | TAK | Dotyczy także domu jednorodzinnego |
| B-07 | Wysokość progów w tych drzwiach: **≤ 0,02 m** | WT § 62 ust. 3 | [WT] | TAK | Detal progu w PT (niski próg ciepły) |
| B-08 | Wejście chronione przed dopływem zimnego powietrza przez przedsionek, kurtynę lub inne rozwiązanie | WT § 63 | [WT] | TAK | Wiatrołap |
| B-09 | Elektryczne oświetlenie zewnętrzne wejścia. Wymóg nie dotyczy tylko budownictwa zagrodowego i rekreacyjnego | WT § 64 | [WT] | TAK | Dotyczy domu jednorodzinnego |
| B-10 | Minimalne wysokości w świetle: pokoje **2,5 m**; pokoje na poddaszu domu jednorodzinnego 2,2 m; pomieszczenia na czasowy pobyt 2,2 m (bez czynników szkodliwych) | WT § 72 ust. 1 (tabela) | [WT] | TAK | Dachy płaskie, więc brak „poddasza”. Kuchnię przyjąć 2,5 m |
| B-11 | Podłoga pomieszczeń na stały pobyt ≥ poziomu terenu przy budynku | WT § 73 ust. 1 | [WT] | TAK | ±0,00 ≈ +0,30 m nad terenem |
| B-12 | Drzwi do pomieszczeń na stały pobyt i do kuchni: **≥ 0,8 × 2,0 m** w świetle ościeżnicy, **bez progów** | WT § 75 ust. 1, 3 | [WT] | TAK | — |
| B-13 | Pomieszczenia higieniczno-sanitarne: wysokość **≥ 2,5 m**. W budynku mieszkalnym dopuszcza się **2,2 m** przy wentylacji mechanicznej wywiewnej lub nawiewno-wywiewnej | WT § 77 ust. 2–3 | [WT] | TAK | Z rekuperacją 2,2 m dopuszczalne |
| B-14 | Ściany pomieszczeń higieniczno-sanitarnych zmywalne i odporne na wilgoć do **2 m**. Posadzki w łazienkach, WC i pralni zmywalne, nienasiąkliwe, nieśliskie | WT § 78 ust. 1–2 | [WT] | TAK | — |
| B-15 | Drzwi do łazienki, umywalni i wydzielonego WC **otwierane na zewnątrz**, **≥ 0,8 × 2,0 m**, z otworami w dolnej części **≥ 0,022 m²**. Dopuszcza się drzwi przesuwne lub składane (poza ogólnodostępnymi) | WT § 79 ust. 1–2 | [WT] | TAK | § 80 (kubatura łazienki) uchylony od 01.01.2018 |
| B-16 | Kabina natryskowa zamknięta (ściany na całą wysokość): ≥ 1,5 m², szerokość ≥ 0,9 m, wentylacja mechaniczna wywiewna | WT § 81 ust. 2 | [WT] | TAK | Dotyczy tylko kabin murowanych na całą wysokość |
| B-17 | Wydzielony ustęp (nie dla niepełnosprawnych): szerokość **≥ 0,9 m**, przed miską **0,6 × 0,9 m** | WT § 83 | [WT] | TAK | WC gościnne P0 |
| B-18 | § 90–§ 95 (przewietrzanie, wyposażenie mieszkania, oświetlenie kuchni, **mieszkanie ≥ 25 m²**, korytarz ≥ 1,2 m) dotyczą mieszkań w budynkach **wielorodzinnych**, więc Domu LAMELA nie | WT Dział III rozdz. 7 (§ 90–§ 95) | [WT] | TAK | Stosować jako dobrą praktykę |
| B-19 | Brief: „pokój ≥ 8 m², dzienny ≥ 16 m²” to **nie jest wymóg WT**. Dawny § 94 ust. 2 (16 m², wielorodzinne) usunięto od 01.01.2018 | Dz.U. 2017 poz. 2285, § 1 pkt 27; t.j. Dz.U. 2015 poz. 1422 (dawny § 94) | [Z2285], [WT2015] | TAK | Parametry programowe inwestora, bez podstawy prawnej |
| B-20 | Pomieszczenie techniczne z urządzeniami hałaśliwymi (np. jednostka wewnętrzna pompy ciepła, centrala) obok pomieszczeń na stały pobyt wymaga rozwiązań chroniących przed hałasem i drganiami. Podpory i złącza nie mogą przenosić drgań | WT § 96 ust. 1–2 | [WT] | TAK | — |
| B-21 | Pomieszczenie techniczne i gospodarcze: wysokość **≥ 2,0 m**. Drzwi i przejścia pod przewodami **≥ 1,9 m** | WT § 97 ust. 1–2 | [WT] | TAK | — |
| B-22 | Garaż: wysokość w świetle konstrukcji **≥ 2,2 m**, do spodu instalacji ≥ 2,0 m. Wrota **≥ 2,3 m** szerokości i **≥ 2,0 m** wysokości w świetle. Oświetlenie elektryczne | WT § 102 pkt 1–3 | [WT] | TAK | — |
| B-23 | Odległość dłuższej krawędzi stanowiska od ściany **≥ 0,3 m**, od słupa ≥ 0,1 m. Droga manewrowa w garażu jednoprzestrzennym przy ustawieniu prostopadłym ≥ 5,0 m | WT § 104 ust. 1 pkt 1, ust. 3 | [WT] | TAK | Minimum: 0,3 + 2 × 2,5 + 0,3 = **5,6 m** szerokości w świetle (= brief). Zalecane 5,9–6,0 m dla komfortu. *Weryfikacja: § 104 nie podaje szerokości stanowiska w garażu. Wartość 2,5 m wzięto z § 21 ust. 1 pkt 1, który dotyczy stanowisk postojowych na działce (Dział II rozdz. 3), więc przeniesienie jej do garażu to interpretacja* |
| B-24 | Garaż w budynku o innym przeznaczeniu: ściany i stropy z izolacyjnością akustyczną wg § 326 oraz **szczelne na spaliny i opary** względem pomieszczeń na pobyt ludzi | WT § 106 ust. 1 | [WT] | TAK | Drzwi garaż–dom szczelne, z samozamykaczem (zalecenie) |
| B-25 | Posadzka garażu ze spadkiem do wpustu. W zabudowie jednorodzinnej dopuszcza się spadek na nieutwardzony teren. Krawędzie posadzki z progiem **30 mm**, z zastrzeżeniem ust. 1 | WT § 107 ust. 1–2 | [WT] | TAK | — |
| B-26 | Wentylacja garażu zamkniętego. **Nieogrzewany** nadziemny: otwory netto **≥ 0,04 m²** na stanowisko (2 st. = 0,08 m²). **Ogrzewany** do 10 stanowisk: co najmniej grawitacyjna, **1,5 wymiany/h** | WT § 108 ust. 1 pkt 1–2 | [WT] | TAK | Zależnie od decyzji: garaż ogrzewany czy nie. *Weryfikacja: przepis mówi o 0,04 m² „na każde, wydzielone przegrodami budowlanymi, stanowisko postojowe”, a otwory mają być w ścianach przeciwległych, bocznych lub we wrotach. Dla garażu 2-stanowiskowego bez przegród przyjęcie 2 × 0,04 = 0,08 m² jest ostrożną interpretacją* |

### 2.6 Schody, balustrady, okna, bezpieczeństwo użytkowania

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| K-01 | Schody w budynku jednorodzinnym: szerokość użytkowa **biegu ≥ 0,8 m**, **spocznika ≥ 0,8 m**, **wysokość stopnia ≤ 0,19 m** | WT § 68 ust. 1 (tabela, wiersz „Budynki mieszkalne jednorodzinne…”) | [WT] | TAK | Projekt: bieg 1,00 m, h ≈ 0,175 m |
| K-02 | Schody do pomieszczeń technicznych i poddaszy nieużytkowych: 0,8 / 0,8 / h ≤ 0,20 m | WT § 68 ust. 1 (ostatni wiersz) | [WT] | TAK | Ewentualny dostęp na dach po schodach |
| K-03 | Szerokość użytkową mierzy się między wewnętrznymi krawędziami poręczy, a przy balustradzie jednostronnej od ściany do poręczy. Urządzenia jej nie ograniczają | WT § 68 ust. 4 | [WT] | TAK | — |
| K-04 | **Schody zewnętrzne do budynku: szerokość ≥ 1,2 m** (nie mniej niż bieg wewnętrzny) | WT § 68 ust. 3 | [WT] | TAK | Brak wyłączenia dla domów jednorodzinnych |
| K-05 | Limit 17 stopni w biegu nie dotyczy domów jednorodzinnych. Schody zewnętrzne: **≤ 10 stopni** w biegu | WT § 69 ust. 2–3 | [WT] | TAK | — |
| K-06 | Stopnie schodów wewnętrznych: **2h + s = 0,60–0,65 m** | WT § 69 ust. 4 | [WT] | TAK | 2 × 0,175 + 0,28 = 0,63 m |
| K-07 | Stopnie wachlarzowe: szerokość **≥ 0,25 m**. W schodach zabiegowych i kręconych mierzona ≤ 0,4 m od poręczy wewnętrznej lub słupa | WT § 69 ust. 6 | [WT] | TAK | — |
| K-08 | Maks. nachylenie pochylni. Piesze, na zewnątrz: 15% (h ≤ 0,15 m), 8% (h ≤ 0,5 m), 6% (h > 0,5 m). Wewnątrz: 15%, 10%, 8%. Samochodowa w garażu indywidualnym: 25% | WT § 70 (tabela) | [WT] | TAK | Ewentualny podjazd lub pochylnia do wejścia |
| K-09 | Schody służące do pokonania wysokości **> 0,5 m** wymagają balustrady od strony otwartej. W domu jednorodzinnym schody o wysokości do 1 m mogą być bez balustrady, jeśli są obustronnie szersze od drzwi o ≥ 0,5 m | WT § 296 ust. 1–2 | [WT] | TAK | Schody wejściowe (ok. 0,3 m) nie wymagają balustrady |
| K-10 | **Balustrady w budynkach jednorodzinnych: wysokość ≥ 0,9 m** (do wierzchu poręczy). Prześwit wypełnienia: **„nie reguluje się”**. Konstrukcja przenosi siły poziome wg PN-EN 1990/1991. Szkło o podwyższonej wytrzymałości, pękające na drobne nieostre odłamki. Bez ostro zakończonych elementów | WT § 298 ust. 1–2 (tabela), zał. 1 lp. 59 | [WT] | TAK | Brief podawał 1,10 m dla tarasów: dla domu jednorodzinnego wystarczy 0,90 m. Zalecenie: prześwity ≤ 0,12 m (dzieci, dobra praktyka) |
| K-11 | Poręcze odsunięte od ściany **≥ 0,05 m**. Poręcze schodów zewnętrznych przedłużone o 0,3 m | WT § 298 ust. 5–6 | [WT] | TAK | — |
| K-12 | Wejście do budynku o **wysokości powyżej dwóch kondygnacji nadziemnych** chroni się daszkiem lub podcieniem: szerokość **≥ szerokość drzwi + 1 m**, wysięg **≥ 1 m** (budynek N). Daszek przenosi obciążenia od spadających szyb lub okładzin | WT § 292 ust. 1–2 | [WT] | TAK | **Dotyczy Domu LAMELA (3 kondygnacje)** |
| K-13 | Daszki, balkony i osłony nad chodnikiem: ≥ 2,4 m nad chodnikiem | WT § 293 ust. 2 | [WT] | TAK | Dotyczy chodników publicznych, więc raczej nie nas |
| K-14 | Zakaz odbojów i wycieraczek wystających ponad płaszczyznę dojścia w szerokości drzwi wejściowych. Kratki ażurowe na trasie przejścia: prześwit ≤ 20 mm | WT § 294 ust. 2–3 | [WT] | TAK | Wycieraczka wpuszczana |
| K-15 | Przezroczyste skrzydła drzwi: oznakowane i ze szkła bezpiecznego | WT § 295 | [WT] | TAK | Drzwi HS i przeszklenia salonu |
| K-16 | **Okna powyżej drugiej kondygnacji nadziemnej** (u nas P2) otwierane do wewnątrz. To samo dotyczy okien na niższych kondygnacjach, które wychodzą na chodniki lub inne przejścia dla pieszych *(uzupełnienie weryfikacji)*. Dopuszcza się okna uchylne na zewnątrz o poziomej osi, wychylenie ≤ 0,6 m, ze szkłem bezpiecznym | WT § 299 ust. 1–2 | [WT] | TAK | Okna przesuwne: interpretacja (zob. ryzyka) |
| K-17 | **Podokiennik ≥ 0,85 m** nad podłogą na kondygnacjach < 25 m, z wyjątkiem przyziemia. Można go obniżyć, stosując balustradę do wymaganej wysokości albo w tej części skrzydło nieotwierane ze szkłem o podwyższonej wytrzymałości | WT § 301 ust. 1, 3 | [WT] | TAK | P1 (boks C) i P2: dolna część stała ze szkła laminowanego do ≥ 0,85 m lub balustrada ≥ 0,90 m |
| K-18 | Temperatura powierzchni nieosłoniętych elementów c.o. ≤ 90 °C | WT § 302 ust. 1 | [WT] | TAK | Ogrzewanie podłogowe spełnia |
| K-19 | Nawierzchnie dojść, schodów i podłóg niepowodujące poślizgu, także w garażu | WT § 305 ust. 1 | [WT] | TAK | — |
| K-20 | **Wyjście na dach** w budynkach o ≥ 2 kondygnacjach nadziemnych, z co najmniej jednej klatki schodowej. Drzwi 0,8 × 1,9 m lub **klapa 0,8 × 0,8 m** w świetle, z dostępem wg § 101 | WT § 308 ust. 1, 3 | [WT] | TAK | Wyłaz z P2 na dach techniczny (PV) |
| K-21 | Drabina lub klamry: szerokość **≥ 0,5 m**, szczeble co **≤ 0,3 m**. Od 3 m nad podłogą obręcze ochronne. Odległość od ściany ≥ 0,15 m | WT § 101 ust. 2–3 | [WT] | TAK | Drabina strychowa lub stała do wyłazu |
| K-22 | Brak wymogu WT dla prześwitu (headroom) nad biegami schodów w budynku mieszkalnym. Wysokość 1,9 m dotyczy tylko dojść technicznych (§ 97, § 100). Schody w domu jednorodzinnym mogą nie spełniać wymagań dróg ewakuacyjnych (§ 248), więc § 242 ust. 3 (2,2 m) ich nie dotyczy | WT § 97 ust. 2, § 100 ust. 1, § 248 | [WT] | TAK | Przyjąć ≥ 2,0 m (dobra praktyka, bez podstawy WT) |

### 2.7 Instalacje

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| IW-01 | Instalacja wodociągowa wg PN-B-01706:1992 (lp. 4). Zabezpieczenie przed przepływem zwrotnym wg PN-EN 1717:2003 (lp. 5) | WT § 113 ust. 4, 7 | [WT] | TAK | Treści norm NIEZWERYFIKOWANE |
| IW-02 | Ciśnienie przed każdym punktem czerpalnym: **0,05–0,6 MPa** | WT § 114 ust. 1 | [WT] | TAK | — |
| IW-03 | Zestaw wodomierza głównego wg PN-B-10720:1998. Za nim zabezpieczenie przed przepływem zwrotnym | WT § 115 ust. 1–2 | [WT] | TAK | — |
| IW-04 | Wodomierz główny w piwnicy lub **na parterze** w wydzielonym, dostępnym miejscu, zabezpieczonym przed zalaniem, mrozem i dostępem osób postronnych. Studzienka poza budynkiem tylko wtedy, gdy nie da się wydzielić miejsca na parterze budynku niepodpiwniczonego. Metalową instalację łączy się przewodem przed i za wodomierzem | WT § 116 ust. 1–3 | [WT] | TAK | Pomieszczenie techniczne P0 |
| IW-05 | Studzienka wodomierzowa (jeśli jest): właz ≥ 0,6 m, dwie pokrywy, zagłębienie do wyczerpywania wody, wentylacja | WT § 117 | [WT] | TAK | Wariant awaryjny |
| IW-06 | C.w.u.: temperatura w punktach czerpalnych **55–60 °C**. Instalacja musi umożliwiać ciągłą lub okresową dezynfekcję metodą chemiczną lub fizyczną, w tym okresowo metodą cieplną. **Przy dezynfekcji cieplnej** w punktach czerpalnych trzeba uzyskać **70–80 °C** (§ 120 ust. 2a). *Weryfikacja: wcześniej było „możliwość dezynfekcji termicznej 70–80 °C”, a przepis nie narzuca metody termicznej.* Zabezpieczenie przed przekroczeniem ciśnienia i temperatury (PN-B-02440:1976). Ciepła woda podłączona z lewej strony | WT § 120 ust. 2, 2a, 4, 5 | [WT] | TAK | Pompa ciepła + grzałka / cykl antylegionella |
| IW-07 | Cyrkulacja c.w.u. **nie jest wymagana** w domach jednorodzinnych | WT § 120 ust. 1 | [WT] | TAK | Decyzja projektowa |
| IW-08 | Gdy c.w.u. przygotowuje instalacja ogrzewcza, w przerwach jej pracy trzeba zapewnić inny sposób podgrzewania | WT § 119 | [WT] | TAK | Grzałka w zasobniku |
| IW-09 | Izolacja przewodów c.w.u. i c.o. wg zał. 2 pkt 1.5 (λ = 0,035). Średnica wewnętrzna ≤ 22 mm: 20 mm; 22–35 mm: 30 mm; 35–100 mm: równa średnicy; > 100 mm: 100 mm. Przejścia przez przegrody: 50%. Przewody w podłodze (lp. 7): 6 mm | WT § 118 ust. 3, § 133 ust. 9, zał. 2 pkt 1.5 | [WT] | TAK | Lp. 6–7 mówią o „różnych użytkownikach”. Stosowanie 6 mm dla podłogi w domu jednorodzinnym to interpretacja |
| IK-01 | Kanalizacja wg PN-EN 12056-1…5:2002, PN-EN 12109:2003. Instalacja sięga do pierwszej studzienki od strony budynku | WT § 122 ust. 1–2, zał. 1 lp. 10 | [WT] | TAK | — |
| IK-02 | Piony wyprowadzone ponad dach jako wentylujące oraz powyżej górnej krawędzi okien i drzwi w odległości poziomej < 4 m od wylotu. Dopuszcza się zawory napowietrzające, jeśli wyprowadzony jest ostatni pion na każdym przewodzie odpływowym i co najmniej co piąty. Zakaz wprowadzania do przewodów wentylacyjnych | WT § 125 ust. 1–3 | [WT] | TAK | Wywiewki na dachu P2 (≥ 6 m od czerpni dachowej, § 152 ust. 4) |
| IK-03 | Zabezpieczenie przed cofką (przepompownia lub zamknięcie przeciwzalewowe), gdy grawitacyjny spływ może być czasowo niemożliwy | WT § 124 | [WT] | TAK | Raczej nie dotyczy (brak podpiwniczenia). Sprawdzić rzędne |
| IK-04 | Dachy i tarasy odwodnione do kanalizacji deszczowej, a przy braku sieci wg § 28 ust. 2 (teren własny, retencja) | WT § 126 ust. 1 | [WT] | TAK | — |
| IO-01 | Budynek wymagający ogrzewania ma instalację ogrzewczą lub urządzenia niebędące piecami, trzonami ani kominkami | WT § 132 ust. 1 | [WT] | TAK | — |
| IO-02 | Szczytowa moc cieplna wg PN o zapotrzebowaniu na ciepło: PN-EN 12831:2006 (lp. 16). Temperatury zewnętrzne wg PN-B-02403:1982 (lp. 17) | WT § 134 ust. 1–2, zał. 1 lp. 16–17 | [WT] | TAK | Dla Poznania θe = −18 °C (strefa II): **NIEZWERYFIKOWANE** (norma niedostępna) |
| IO-03 | **Temperatury obliczeniowe:** pokoje, przedpokoje, kuchnie (paleniska gazowe lub elektryczne) **+20 °C**. **Łazienki +24 °C**. Garaże indywidualne +5 °C. Klatki schodowe w budynkach mieszkalnych +8 °C (tylko klatki poza mieszkaniem) | WT § 134 ust. 2 (tabela) | [WT] | TAK | Hol i schody w domu = przedpokój, więc +20 °C |
| IO-04 | Regulatory dopływu ciepła na grzejnikach i innych odbiornikach. Wymóg automatycznej regulacji wg § 134 ust. 5 **nie dotyczy** domów jednorodzinnych | WT § 134 ust. 4–5 | [WT] | TAK | — |
| IO-05 | **Automatyczna regulacja temperatury oddzielnie w poszczególnych pomieszczeniach.** Regulacja strefowa dopuszczalna, gdy montaż jest niemożliwy. Wymóg obowiązuje, gdy: (1) jest technicznie możliwy (opinia projektanta z uprawnieniami) i (2) okres zwrotu ≤ 5 lat | WT § 135 ust. 7–9 | [WT] | TAK | Podłogówka: termostaty pokojowe + siłowniki |
| IO-06 | Podział instalacji na obiegi przy zróżnicowanym zapotrzebowaniu. Armatura odcinająca i spustowa | WT § 134 ust. 8, 10 | [WT] | TAK | — |
| IO-07 | Zakaz ogrzewania parowego i czynnika > 90 °C w pomieszczeniach na pobyt ludzi | WT § 135 ust. 5 | [WT] | TAK | — |
| IO-08 | Zabezpieczenie instalacji wodnej wg PN-B-02414:1999 i innych (lp. 14). Jakość wody PN-C-04607:1993. Odpowietrzanie. Racjonalnie niska ilość wody uzupełniającej | WT § 133 ust. 3–6 | [WT] | TAK | Treść norm NIEZWERYFIKOWANA |
| IO-09 | Obudowa przewodów c.o. umożliwia ich wymianę bez naruszania konstrukcji | WT § 138 | [WT] | TAK | — |
| IV-01 | Wentylacja zapewnia jakość środowiska wewnętrznego wg PN-B-03430:1983/Az3:2000 (lp. 26, 28, 33) | WT § 147 ust. 1, § 149 ust. 1 | [WT] | TAK | — |
| IV-02 | Strumień powietrza zewnętrznego w mieszkaniu wynika ze strumienia wywiewanego, ale **≥ 20 m³/h na osobę** przewidzianą na pobyt stały | WT § 149 ust. 1 | [WT] | TAK | 5 osób: ≥ 100 m³/h |
| IV-03 | Wywiew wg PN-B-03430/Az3. Kuchnia z kuchenką elektryczną: 30 m³/h (≤ 3 osoby) / 50 m³/h (> 3 osoby). Łazienka 50 m³/h. WC 30 m³/h. Pomieszczenie pomocnicze bez okna 15 m³/h | PN-B-03430:1983/Az3:2000 (przywołana w WT § 149 ust. 1) | [S-KP] | NIE | **NIEZWERYFIKOWANE** (źródło wtórne, treść normy niedostępna) |
| IV-04 | Przepływ powietrza z pokoi do kuchni i pomieszczeń higieniczno-sanitarnych | WT § 150 ust. 2 | [WT] | TAK | — |
| IV-05 | W pomieszczeniu z wentylacją mechaniczną nie wolno stosować grawitacyjnej ani hybrydowej | WT § 148 ust. 2 | [WT] | TAK | Nie projektować kominów wentylacji grawitacyjnej w pomieszczeniach z rekuperacją |
| IV-06 | Regulacja wydajności wentylatorów do potrzeb | WT § 148 ust. 5 | [WT] | TAK | — |
| IV-07 | Łączenie przewodów z pomieszczeń o różnych wymaganiach **dozwolone** w domach jednorodzinnych | WT § 150 ust. 3 | [WT] | TAK | — |
| IV-08 | Odzysk ciepła **≥ 50%** jest obowiązkowy dopiero dla instalacji nawiewno-wywiewnych **≥ 500 m³/h** | WT § 151 ust. 1 | [WT] | TAK | Rekuperacja w LAMELA wynika z EP i decyzji inwestora, nie z § 151 |
| IV-09 | **Czerpnia** na terenie lub ścianie dwóch najniższych kondygnacji: **≥ 8 m** od ulic, parkingów > 20 stanowisk, miejsc na odpady, wywiewek kanalizacyjnych. Dolna krawędź **≥ 2 m** nad terenem. **Czerpnia dachowa:** ≥ 0,4 m nad powierzchnią montażu, **≥ 6 m** od wywiewek kanalizacyjnych | WT § 152 ust. 3–4 | [WT] | TAK | — |
| IV-10 | **Wyrzutnia w ścianie** dopuszczalna, gdy: powietrze bez uciążliwych zapachów i zanieczyszczeń; przeciwległa ściana sąsiada z oknami ≥ 10 m (bez okien ≥ 8 m); okna w tej samej ścianie ≥ 3 m w poziomie i ≥ 2 m w pionie; czerpnia w tej samej ścianie niżej lub na tym samym poziomie, w odległości ≥ 1,5 m | WT § 152 ust. 9 | [WT] | TAK | Wariant: czerpnia i wyrzutnia na dachu P2 (§ 152 ust. 7, 10–13) |
| IV-11 | Przewody przez przestrzenie nieogrzewane izolowane cieplnie. Przewody powietrza zewnętrznego i do odzysku ciepła izolowane cieplnie i przeciwwilgociowo | WT § 153 ust. 6–7 | [WT] | TAK | — |
| IV-12 | Otwory rewizyjne w przewodach (poza pomieszczeniami o podwyższonych wymaganiach higienicznych) | WT § 153 ust. 5 | [WT] | TAK | — |
| IV-13 | Filtry przed wymiennikiem, nagrzewnicą i chłodnicą **≥ G4** wg PN-EN 779 (lp. 32) | WT § 154 ust. 6 | [WT] | TAK | PN-EN 779 zastąpiona przez ISO 16890. Ekwiwalent NIEZWERYFIKOWANY |
| IV-14 | Moc właściwa wentylatorów (SFP). Nawiew z odzyskiem ciepła **≤ 1,60 kW/(m³/s)**, wywiew z odzyskiem **≤ 1,00**. Dodatek +0,3 przy odzysku > 67% | WT § 154 ust. 10–11 | [WT] | TAK | Dobór centrali w PT |
| IV-15 | Połączenia wentylatorów z przewodami elastyczne, ≤ 0,25 m, materiał co najmniej trudno zapalny | WT § 154 ust. 8, § 267 ust. 7 | [WT] | TAK | — |
| IV-16 | Przy wentylacji innej niż mechaniczna nawiewna: nawiewniki w oknach lub przegrodach, a okna otwierane co najmniej w 50% wymaganej powierzchni | WT § 155 ust. 1, 3 | [WT] | TAK | Nie dotyczy przy wentylacji mechanicznej nawiewno-wywiewnej |
| IE-01 | Instalacja elektryczna zapewnia dostawę energii (w tym infrastrukturę ładowania EV wg ustawy o elektromobilności), ochronę przed porażeniem, przepięciami, pożarem i szkodliwym oddziaływaniem | WT § 180 pkt 1–3 | [WT], [EM1243] | TAK | *Weryfikacja (było: NIEZWERYFIKOWANE):* ustawa o elektromobilności i paliwach alternatywnych, t.j. **Dz.U. 2026 poz. 1243**, nakłada obowiązki projektowe infrastruktury ładowania tylko na: budynki UP i mieszkalne wielorodzinne w gminach z art. 60 ust. 1 (art. 12 ust. 1: moc przyłączeniowa pod punkty ≥ 3,7 kW) oraz budynki niemieszkalne z > 10 stanowiskami (art. 12a). **Dla domu jednorodzinnego obowiązku nie ma.** Obwód EV to dobra praktyka |
| IE-02 | Stosuje się: (1) złącze w miejscu dostępnym i zabezpieczonym; (2) **oddzielny przewód ochronny i neutralny**; (3) **wyłączniki różnicowoprądowe**; (4) wyłączniki nadprądowe; (5) **selektywność**; (6) przeciwpożarowe wyłączniki prądu; (7) **połączenia wyrównawcze główne i miejscowe**; (8) trasy w liniach prostych równoległych do krawędzi; (9) **żyły wyłącznie miedziane do 10 mm²**; (10) **ochronę przeciwprzepięciową** | WT § 183 ust. 1 pkt 1–10 | [WT] | TAK | TN-S |
| IE-03 | Połączeniami wyrównawczymi obejmuje się m.in. metalowe instalacje wodne, kanalizacyjne i c.o., kanały wentylacyjne, osłony urządzeń teletechnicznych | WT § 183 ust. 1a | [WT] | TAK | — |
| IE-04 | **Przeciwpożarowy wyłącznik prądu** w strefach pożarowych o kubaturze **> 1000 m³**. Umieszczony przy głównym wejściu lub złączu, oznakowany | WT § 183 ust. 2–3 | [WT] | TAK | Obliczyć kubaturę strefy (cały budynek z garażem). Prawdopodobnie > 1000 m³, więc **PWP wymagany** |
| IE-05 | **Uziom fundamentowy:** jako uziomy wykorzystuje się zbrojenie fundamentów lub metalowe elementy w fundamentach niezbrojonych | WT § 184 ust. 1 | [WT] | TAK | W PT konstrukcji i elektryki |
| IE-06 | Licznik energii w miejscu łatwo dostępnym i zabezpieczonym | WT § 185 ust. 1 | [WT] | TAK | Złącze kablowo-pomiarowe w linii ogrodzenia |
| IE-07 | Przewody wymienialne bez naruszania konstrukcji. Przewody wtynkowe pod tynkiem **≥ 5 mm** | WT § 187 ust. 1–2 | [WT] | TAK | — |
| IE-08 | W mieszkaniu wyodrębnione obwody: oświetlenie, gniazda ogólne, **gniazda w łazience**, **gniazda kuchenne**, odbiorniki wymagające indywidualnego zabezpieczenia | WT § 188 ust. 2 | [WT] | TAK | Mieszkanie wg § 3 pkt 9, więc dotyczy też domu jednorodzinnego |
| IE-09 | Wypusty oświetleniowe i gniazda w pomieszczeniach. Oświetlenie w pokojach z **łącznikami wieloobwodowymi** | WT § 189 ust. 1–2 | [WT] | TAK | — |
| IE-10 | Normy instalacji elektrycznej: seria PN-HD 60364 (zał. 1 lp. 3, 41), odgromowa PN-EN 62305-1…4 (lp. 44) | WT zał. 1 | [WT] | TAK | Wydania datowane wg zał. 1 |

### 2.8 Bezpieczeństwo pożarowe

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| P-01 | Budynek mieszkalny to kategoria **ZL IV** | WT § 209 ust. 2 pkt 4 | [WT] | TAK | — |
| P-02 | Wymagania klasy odporności pożarowej (§ 212) oraz klas odporności ogniowej i rozprzestrzeniania ognia elementów (§ 216) **nie dotyczą** budynków mieszkalnych jednorodzinnych **do trzech kondygnacji nadziemnych włącznie** (z zastrzeżeniem § 217 ust. 2 i § 271 ust. 8a) | WT § 213 pkt 1 lit. a | [WT] | TAK | **Kluczowe:** 4. kondygnacja nadziemna (np. techniczna > 2 m) oznacza utratę zwolnienia i klasę „D” |
| P-03 | Dla porównania: ZL IV niski bez zwolnienia ma klasę „D”: konstrukcja R 30, strop REI 30, ściana zewnętrzna EI 30 | WT § 212 ust. 2, § 216 ust. 1 | [WT] | TAK | Nie dotyczy (P-02) |
| P-04 | § 217 ust. 2 (REI 60 między segmentami) dotyczy domów bliźniaczych i szeregowych, więc nas nie dotyczy | WT § 217 ust. 2 | [WT] | TAK | — |
| P-05 | Garaż ≤ 3 stanowisk w zabudowie jednorodzinnej: § 271 nie stosuje się do jego usytuowania | WT § 276 ust. 2 | [WT] | TAK | — |
| P-06 | Połączenie garażu z budynkiem przez przedsionek przeciwpożarowy (EI 30) **nie jest wymagane** w domu jednorodzinnym | WT § 280 ust. 3 | [WT] | TAK | Przedsionek funkcjonalny według briefu (nie ppoż.) |
| P-07 | Garaż zamknięty w budynku ZL. Odległość w pionie **wrota–okna ≥ 1,5 m** (1,1 m przy daszku niepalnym wysięgu ≥ 0,6 m, wysuniętym 0,8 m poza boki wrót, lub przy wrotach cofniętych o 0,8 m). W poziomie od wrót do najbliższej krawędzi okien pomieszczeń na pobyt ludzi **≥ 1,5 m** | WT § 279 ust. 1–2 | [WT] | TAK | Sprawdzić elewację N (brama) i okna P1 nad garażem |
| P-08 | W garażu **zakaz** studzienek rewizyjnych, urządzeń i przewodów gazowych, otworów od palenisk oraz **otworów rewizyjnych do czyszczenia kanałów dymowych, spalinowych i wentylacyjnych** | WT § 281 | [WT] | TAK | Centrala i rewizje wentylacji poza garażem |
| P-09 | Odległość między ścianami zewnętrznymi budynków ZL–ZL: **8 m**. +50% gdy jedna ze ścian lub dachów jest rozprzestrzeniająca ogień, +100% gdy obie. Dla budynków z § 213 z NRO ścianami bez otworów: −25% | WT § 271 ust. 1–2, 9 | [WT] | TAK | Sąsiedzi ≥ 8 m od granicy + nasze ≥ 4 m, więc ≥ 12 m |
| P-10 | Zwiększenia za ściany z otworami (> 65% / 30–65% / < 30% powierzchni z klasą E): +0% / +50% / +100% | WT § 271 ust. 1, 4–5 | [WT] | TAK | Stosowanie do budynków z § 213: interpretacja **NIEZWERYFIKOWANA** (zob. ryzyka) |
| P-11 | Od granicy **niezabudowanej** działki sąsiedniej dom jednorodzinny ze ścianami i dachem NRO sytuuje się jak w § 12 | WT § 272 ust. 2 | [WT] | TAK | Działka S (teren zieleni) = niezabudowana |
| P-12 | Odległość od lasu: § 271 ust. 8. Dla budynków z § 213 w warunkach ust. 8a: 4 m od granicy lasu na sąsiedniej działce | WT § 271 ust. 8–8a | [WT] | TAK | Brak lasu (południe: teren rolny lub zieleni) |
| P-13 | Przejścia instalacji przez ściany zewnętrzne poniżej terenu zabezpieczone przed przenikaniem gazu | WT § 234 ust. 4 | [WT] | TAK | W ulicy jest sieć gazowa. Przepusty gazoszczelne |
| P-14 | Izolacje cieplne i akustyczne instalacji wodnej, kanalizacyjnej i c.o. nierozprzestrzeniające ognia | WT § 267 ust. 8 | [WT] | TAK | — |
| P-15 | Przewody wentylacyjne z materiałów niepalnych. **Nie dotyczy** domu jednorodzinnego z 1 lokalem | WT § 267 ust. 1, 1a | [WT] | TAK | Zmiana z 2022 (Dz.U. 2022 poz. 248) |
| P-16 | Wymagania § 268 (siły 1 kN, zamocowania niepalne) nie dotyczą budynków jednorodzinnych | WT § 268 ust. 1 | [WT] | TAK | — |
| P-17 | Schody wewnętrzne w domu jednorodzinnym mogą nie spełniać wymagań dróg ewakuacyjnych | WT § 248 | [WT] | TAK | — |
| P-18 | Okładziny elewacyjne mocowane tak, by nie odpadały w czasie krótszym niż wymagany dla ściany. Dla budynku z § 213 brak klasy, więc wymóg praktycznie pusty | WT § 225 | [WT] | TAK | Lamele P2: mocowanie mechaniczne (dobra praktyka) |
| P-19 | Pasy międzykondygnacyjne 0,8 m (§ 223) wynikają z wymaganej klasy EI ścian (§ 223 ust. 3). Dla budynków z § 213: interpretacja | WT § 223 | [WT] | TAK | Wysunięte płyty i tak dają ≥ 0,5 m wysięgu |

### 2.9 Higiena, wilgoć, hałas

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| H-01 | Materiały nieemitujące substancji szkodliwych. Radon ≤ wartości z przepisów odrębnych | WT § 312 ust. 1, § 313 ust. 2 | [WT] | TAK | Przepisy odrębne (Prawo atomowe) poza R3 |
| H-02 | Ochrona przed wodą gruntową (drenaż, gdy wymagany) oraz swobodny spływ wody od budynku | WT § 316 ust. 1–2 | [WT] | TAK | ZWG ≈ 3,8 m ppt, więc drenaż raczej niepotrzebny |
| H-03 | Izolacja przeciwwilgociowa elementów stykających się z gruntem. Ochrona cokołu nad terenem, tarasami i dachami | WT § 317 ust. 1–2 | [WT] | TAK | — |
| H-04 | Spadki dachów i tarasów do rynien lub rur spustowych (wewnętrznych lub zewnętrznych) | WT § 319 ust. 1 | [WT] | TAK | Dachy płaskie: spadki ≥ 2% (dobra praktyka) |
| H-05 | Posadzki tarasów nienasiąkliwe, mrozoodporne, nieśliskie | WT § 320 | [WT] | TAK | Taras ogrodowy |
| H-06 | Brak kondensacji na wewnętrznej powierzchni przegród i narastającego zawilgocenia we wnętrzu przegrody. Sprawdzenie wg PN-EN ISO 13788:2013-05 (zał. 2 pkt 2.2). **fRsi ≥ fRsi,kryt**, dopuszczalne uproszczenie **0,72** (pomieszczenia ≥ 20 °C, φ = 50%) | WT § 321, zał. 2 pkt 2.2.1–2.2.5 | [WT] | TAK | Mostki wsporników płyt: analiza 3D wg PN-EN ISO 10211 (pkt 2.2.3 ppkt 2) |
| H-07 | Ochrona pomieszczeń przed hałasem zewnętrznym, instalacyjnym, między lokalami i pogłosowym | WT § 323 ust. 2 | [WT] | TAK | — |
| H-08 | Poziom hałasu i drgań w pomieszczeniach ≤ wartości z PN-B-02151-2:2018-01. Izolacyjność przegród zewnętrznych i wewnętrznych ≥ PN-B-02151-3:2015-10 (+Ap1:2016-02). Przewody instalacyjne nie mogą pogarszać izolacyjności | WT § 326 ust. 1–3, zał. 1 lp. 64–66 (brzmienie wg Dz.U. 2023 poz. 2442) | [Z2442] | TAK | **2023–24** (nowe normy). Wartości z norm NIEZWERYFIKOWANE |
| H-09 | § 326 ust. 4a–4b (wymogi jak między lokalami; zakaz pogarszania akustyki) dotyczą domów jednorodzinnych z **2 lokalami** i szeregowych, więc nas nie dotyczą | WT § 326 ust. 4a–4b | [Z2442] | TAK | **2023–24** |
| H-10 | Instalacje nie mogą powodować nadmiernego hałasu i drgań. Posadowienie urządzeń i połączeń zapobiega przenoszeniu | WT § 327 ust. 2–3 | [WT] | TAK | Jednostka zewnętrzna pompy ciepła, centrala |
| H-11 | Hałas w środowisku, teren MN (tereny zabudowy mieszkaniowej jednorodzinnej), „pozostałe obiekty i działalność”: **LAeq D = 50 dB** (8 najmniej korzystnych godzin dnia), **LAeq N = 40 dB** (1 najmniej korzystna godzina nocy) | rozp. MŚ z 14.06.2007, t.j. Dz.U. 2014 poz. 112, zał. tab. 1 lp. 2a | [H112] | TAK | Poza WT. Istotne dla lokalizacji jednostki zewnętrznej pompy ciepła względem granic |

### 2.10 Oszczędność energii (Dział X i zał. 2; wartości „od 31 grudnia 2020 r.”)

| ID | Wymaganie | Podstawa | URL | Pierw.? | Uwagi |
|---|---|---|---|---|---|
| E-01 | Wymagania minimalne: (1) EP ≤ EPmax; (2) przegrody i wyposażenie techniczne ≥ zał. 2 | WT § 328 ust. 1 | [WT] | TAK | Oba warunki łącznie |
| E-02 | **EP_H+W dla budynku mieszkalnego jednorodzinnego: 70 kWh/(m²·rok).** ΔEP_C = 5·Af,C/Af (gdy jest chłodzenie; w przeciwnym razie 0). ΔEP_L = 0 | WT § 329 ust. 1–2 (tabele) | [WT] | TAK | EP liczony wg metodologii z art. 15 ustawy o charakterystyce energetycznej (R2) |
| E-03 | Budynek ogranicza ryzyko przegrzewania latem. Warunek uznaje się za spełniony, gdy okna spełniają pkt 2.1.1 zał. 2 | WT § 328 ust. 2, § 329 ust. 4 | [WT] | TAK | — |
| E-04 | **Ściany zewnętrzne (ti ≥ 16 °C): Uc ≤ 0,20 W/(m²K).** 8 ≤ ti < 16: 0,45. ti < 8: 0,90 | WT zał. 2 pkt 1.1 lp. 1 | [WT] | TAK | — |
| E-05 | Ściany wewnętrzne: przy Δti ≥ 8 °C U ≤ 1,00; **oddzielające ogrzewane od nieogrzewanego U ≤ 0,30** | WT zał. 2 pkt 1.1 lp. 2 | [WT] | TAK | Ściana dom–garaż (garaż nieogrzewany) |
| E-06 | **Dachy, stropodachy i stropy pod nieogrzewanymi poddaszami lub nad przejazdami (ti ≥ 16 °C): Uc ≤ 0,15** (8–16 °C: 0,30; < 8 °C: 0,70) | WT zał. 2 pkt 1.1 lp. 5 | [WT] | TAK | Stropodachy P0/P1/P2. Stropy nad powietrzem zewnętrznym (wsporniki P2) przyjąć jak „nad przejazdami”: 0,15 (interpretacja) |
| E-07 | **Podłoga na gruncie (ti ≥ 16 °C): Uc ≤ 0,30** (8–16: 1,20; < 8: 1,50) | WT zał. 2 pkt 1.1 lp. 6 | [WT] | TAK | Garaż ogrzewany do +5 °C: 1,50 |
| E-08 | Stropy nad pomieszczeniami nieogrzewanymi (ti ≥ 16): 0,25. Stropy oddzielające ogrzewane od nieogrzewanego: 0,25 | WT zał. 2 pkt 1.1 lp. 7, 8c | [WT] | TAK | Gdyby pomieszczenie P1 było nad garażem |
| E-09 | **Okna, drzwi balkonowe, przeszklenia stałe (ti ≥ 16): U ≤ 0,9.** Okna połaciowe: 1,1. Okna w ścianach wewnętrznych do nieogrzewanych: 1,1. **Drzwi zewnętrzne i drzwi między ogrzewanym a nieogrzewanym: U ≤ 1,3.** Okna i drzwi w przegrodach zewnętrznych pomieszczeń nieogrzewanych: bez wymagań | WT zał. 2 pkt 1.2 | [WT] | TAK | Brama garażowa (garaż nieogrzewany): bez wymagań |
| E-10 | Podłoga na gruncie w pomieszczeniu ogrzewanym: **izolacja obwodowa R ≥ 2,0 (m²K)/W** | WT zał. 2 pkt 1.4 | [WT] | TAK | Detal cokołu i ław lub płyty |
| E-11 | **g = fC·gn ≤ 0,35** w okresie letnim dla okien i przegród przezroczystych. gn z deklaracji właściwości użytkowych; brak danych: potrójne z powłoką 0,5. fC z tabeli pkt 2.1.3 (np. zewnętrzne żaluzje białe z lamelami nastawnymi 0,10–0,35) | WT zał. 2 pkt 2.1.1–2.1.3 | [WT] | TAK | — |
| E-12 | **Wyjątki od g ≤ 0,35:** powierzchnie pionowe i nachylone > 60° skierowane NW–NE (N ± 45°); okna chronione elementem zacieniającym spełniającym 2.1.1; okna < 0,5 m² | WT zał. 2 pkt 2.1.4 | [WT] | TAK | Okap nad przeszkleniem S musi „spełniać 2.1.1”, co wymaga wykazania |
| E-13 | **A0max nie obowiązuje.** Zał. 2 w brzmieniu od 01.01.2018 nie zawiera limitu powierzchni okien (był w pkt 2.1.1 zał. 2 w brzmieniu z Dz.U. 2013 poz. 926) | Dz.U. 2017 poz. 2285 § 1 pkt 67; zał. 2 t.j. 2022/1225 | [Z2285], [Z926], [WT] | TAK | Korekta briefu |
| E-14 | Całkowita szczelność na przenikanie powietrza przegród, złączy, przejść instalacji i połączeń okien z ościeżem | WT zał. 2 pkt 2.3.1 | [WT] | TAK | Taśmy okienne, detale |
| E-15 | Przepuszczalność powietrza okien i drzwi balkonowych w budynkach N/SW/W: **≤ 2,25 m³/(m·h)** lub **≤ 9 m³/(m²·h)** przy 100 Pa, tj. **klasa 3** wg PN-EN 12207 | WT zał. 2 pkt 2.3.2 | [WT] | TAK | Wymóg obowiązkowy |
| E-16 | **Zalecana** szczelność budynku z wentylacją mechaniczną: **n50 < 1,5 h⁻¹**. **Zalecana** próba ciśnieniowa wg PN-EN 13829:2002 | WT zał. 2 pkt 2.3.3–2.3.4 | [WT] | TAK | Zalecenie, nie obowiązek |
| E-17 | Izolacja przewodów c.o., c.w.u. i ogrzewania powietrznego: tabela pkt 1.5 (zob. IW-09). Przewody ogrzewania powietrznego: 40 mm (część ogrzewana) / 80 mm (nieogrzewana) | WT zał. 2 pkt 1.5 lp. 8–9 | [WT] | TAK | — |
| E-18 | Uc oblicza się z poprawkami (pustki, łączniki, dach odwrócony) wg PN-EN ISO 6946 i PN-EN ISO 13370 (niedatowane, czyli najnowsze wydanie) | WT zał. 2 pkt 1.1, zał. 1 lp. 69 i odnośnik **) | [WT] | TAK | — |
| E-19 | Urządzenia do c.w.u., ogrzewania i wentylacji spełniają przepisy odrębne o efektywności energetycznej (ekoprojekt) | WT § 118 ust. 2, § 134 ust. 3, § 147 ust. 4 | [WT] | TAK | Rozporządzenia UE: poza R3 |

---

## 3. Implikacje dla projektu Dom LAMELA

### 3.1 Formalne
1. **Oświadczenie z art. 102a ust. 1 PB.** Inwestor podpisuje oświadczenie o stosowaniu przepisów wydanych na podstawie art. 7 ust. 2 pkt 1 PB, obowiązujących do 19.09.2026 (wzór PIIB, niemodyfikowany). Oświadczenie **dołącza się do wniosku PB-1** (wzór Dz.U. 2026 poz. 255 nie ma na nie pola: załącznik „inne”, zob. R2). Wniosek trzeba złożyć **do 19.03.2028**.
2. Każdą część opisową, czyli PZT, PAB i PT (art. 102a ust. 2), sporządzamy na podstawie: „rozporządzenie MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (t.j. Dz.U. 2022 poz. 1225, zm. Dz.U. 2023 poz. 2442, Dz.U. 2024 poz. 474, Dz.U. 2024 poz. 726), stosowane na podstawie art. 102a PB”. Nie powołujemy projektu RCL 12398903.
3. W rejestrze wymagań brief należy poprawić w pięciu punktach:
   * usunąć A0max (E-13);
   * „pokój ≥ 8/16 m²” oznaczyć jako wymaganie programowe, nie WT (B-19);
   * balustrady w domu jednorodzinnym ≥ 0,90 m wszędzie, prześwit nieregulowany (K-10);
   * odzysk ciepła nie jest wymogiem WT poniżej 500 m³/h (IV-08);
   * art. 56 ust. 1a PB uchylony (R2).

### 3.2 Bryła, klasyfikacja, usytuowanie
4. **Maks. 3 kondygnacje nadziemne.** Zachowuje to zwolnienie z § 213 (P-02): brak klasy odporności pożarowej i klas REI/EI elementów. Na dachu żadnej przestrzeni technicznej o średniej wysokości > 2 m, która byłaby kondygnacją (D-03). Wyjście na dach przez **klapę ≥ 0,8 × 0,8 m** z drabiną wg § 101 (K-20, K-21).
5. **Wysokość wg § 6 WT:** od terenu przy najniższym wejściu na P0 do wierzchu warstwy osłaniającej izolację stropodachu P2. Szacunek:
   * ±0,00 ≈ +0,30 m nad terenem;
   * 3 × ok. 3,1–3,2 m;
   * warstwy dachu ok. 0,5 m.

   Daje to ok. 10,0–10,4 m. Limit MPZP 11,0 m wymaga zdefiniowania w MPZP (fikcyjnym), czy attyka się wlicza. Grupa N (D-02).
6. **Ściany E i W z oknami ≥ 4,0 m od granic** (U-01). **Każdy uskok elewacji w „S” ocenia się jako osobną ścianę** (Dz.U. 2024 poz. 726). Wspornik P2 ok. 1,0 m na zachód:
   * **lico ściany P2** musi mieć ≥ 4,0 m (z oknami) lub ≥ 3,0 m (bez);
   * płyty wysunięte 0,8–1,5 m (okapy lub gzymsy) ≥ 1,5 m od granicy (U-04).

   Przy działce szerokości 32,00 m maks. długość bryły mierzona po najbardziej wysuniętych licach ścian z oknami wynosi 32,0 − 2 × 4,0 = 24,0 m. Rezerwa na przesunięcia jest duża. Ściana S ≥ 4,0 m od granicy południowej. Od ul. Lipowej obowiązuje linia zabudowy 6,0 m z MPZP (§ 12 ust. 10).
7. Zachować **≥ 8 m od ścian budynków sąsiadów** (P-09). Przy sąsiadach ≥ 8 m od granicy i ścianach LAMELA ≥ 4 m od granicy mamy ≥ 12 m. Ściany i dach projektować jako **nierozprzestrzeniające ognia (NRO)**: system ETICS z klasyfikacją NRO, dach płaski B_ROOF(t1). Unikamy wtedy zwiększeń o 50/100% i mamy spełniony § 272 ust. 2 wobec działki niezabudowanej (S).
8. **Przesłanianie i nasłonecznienie:**
   * sprawdzić § 13 dla okien P0 i P1 sąsiadujących z bryłą garażu i uskokami;
   * wykazać ≥ 3 h słońca 7⁰⁰–17⁰⁰ w dniu równonocy dla co najmniej 1 pokoju (w praktyce salon i pokoje od S);
   * okna ≥ 1/8 powierzchni podłogi (w świetle ościeżnic) w pokojach, kuchni, gabinecie i sypialniach (B-04).

### 3.3 Zagospodarowanie
9. Miejsca gościnne:
   * maks. **2 niezadaszone**, 2,5 × 5,0 m, przy budynku (zwolnienie z 7 m od okien, § 19 ust. 5);
   * **≥ 3,0 m od granic E i W** (§ 19 ust. 2), chyba że stykają się z niezadaszonym parkingiem sąsiada;
   * od granicy z drogą (N) odległości nie wymaga się (§ 19 ust. 7).

   Jezdnia dojazdu ≥ 3,0 m. Nawierzchnia dla pojazdów do 2,5 t.
10. Miejsce na pojemniki do segregacji odpadów (osłona) z utwardzonym dojściem do furtki lub drogi. Odległości od okien i granic nie wymaga się (Z-09, Z-10). Do ustalenia w R-MPZP, czy regulamin gminy nie wymaga czegoś więcej.
11. Ogrodzenie:
   * brama wjazdowa **przesuwna** (wewnątrz działki), światło **≥ 2,4 m** (przyjąć 4,0–4,5 m dla komfortu manewru);
   * furtka **≥ 0,9 m**, otwierana do wewnątrz;
   * bez ostrych elementów poniżej 1,8 m;
   * wysokość i ażurowość wg MPZP.
12. Wody opadowe: retencja i rozsączanie na działce (§ 28 ust. 2). Bez zmiany spływu na sąsiadów (§ 29). Spadki terenu od budynku (§ 316 ust. 2). Ewentualne wykorzystanie deszczówki w osobnej instalacji (§ 126 ust. 3).

### 3.4 Budynek i pomieszczenia
13. Wysokości w świetle:
   * pokoje **≥ 2,50 m**;
   * łazienki ≥ 2,20 m (przy wentylacji mechanicznej, B-13);
   * pomieszczenia techniczne, garderoby i spiżarnie ≥ 2,00 m;
   * kuchnię przyjąć 2,50 m.

   Garaż: w świetle ≥ 2,20 m, pod instalacjami ≥ 2,00 m, brama ≥ 2,30 × 2,00 m (przyjąć 5,0 × 2,125 m). Szerokość w świetle min. **5,6 m** (0,3 + 2 × 2,5 + 0,3), zalecane 5,9–6,0 m (B-22, B-23).
14. Wejście główne:
   * drzwi **≥ 0,90 × 2,00 m** w świetle, **próg ≤ 2 cm**;
   * **wiatrołap**;
   * oświetlenie zewnętrzne;
   * **daszek: szerokość ≥ szerokość drzwi + 1,0 m, wysięg ≥ 1,0 m** (§ 292, bo budynek ma 3 kondygnacje), zaprojektowany na upadek szyb i okładzin;
   * schody zewnętrzne **≥ 1,20 m** szerokości, ≤ 10 stopni, h ≤ 0,19 m (przyjąć ok. 0,15 m).

   Różnica ok. 0,30 m to 2 stopnie, bez balustrady (K-09). Wycieraczka wpuszczana (K-14).
15. Drzwi wewnętrzne:
   * do pokoi i kuchni ≥ 0,80 × 2,00 m, bez progów;
   * do łazienek i WC **otwierane na zewnątrz** (lub przesuwne), ≥ 0,80 m, z kratką lub podcięciem ≥ 0,022 m² (służy też jako przepływ powietrza w wentylacji mechanicznej);
   * WC gościnne szerokości ≥ 0,90 m z polem 0,6 × 0,9 m przed miską.
16. Schody wewnętrzne. Przyjęte założenia:
   * bieg 1,00 m, spocznik ≥ 1,00 m;
   * h = 0,175 m (P0→P1 i P1→P2, np. 18 × 0,175 = 3,15 m), s = 0,28 m, 2h + s = 0,63 m;
   * wachlarzowe ≥ 0,25 m w linii 0,4 m od poręczy;
   * balustrada ≥ 0,90 m, poręcz ≥ 0,05 m od ściany;
   * prześwit nad biegiem ≥ 2,00 m (dobra praktyka).
17. Okna:
   * **P2 (3. kondygnacja): skrzydła otwierane do wewnątrz**, uchylne na zewnątrz tylko z wychyleniem ≤ 0,6 m (K-16);
   * **P1 i P2 podokienniki ≥ 0,85 m** albo dolna część przeszklenia stała ze szkła laminowanego do ≥ 0,85 m lub balustrada ≥ 0,90 m (dotyczy przeszklenia boksu C i okien od podłogi);
   * przeszklenia drzwiowe ze szkła bezpiecznego i oznakowane.
18. Garaż:
   * ściana i drzwi garaż–dom szczelne na spaliny (drzwi z uszczelką i samozamykaczem);
   * ściana dom–garaż (nieogrzewany): **U ≤ 0,30**, drzwi **U ≤ 1,3**;
   * posadzka ze spadkiem na zewnątrz (dopuszczalne w domu jednorodzinnym) lub do odwodnienia liniowego z osadnikiem;
   * wentylacja przez otwory ≥ 0,08 m² netto (garaż nieogrzewany);
   * **w garażu brak rewizji kanałów wentylacyjnych i elementów gazowych** (§ 281);
   * **okna P1 nad bramą ≥ 1,5 m w pionie i ≥ 1,5 m w poziomie od krawędzi bramy** (§ 279).
19. Pomieszczenie techniczne (P0): wodomierz główny, rozdzielnica, jednostka wewnętrzna pompy ciepła i zasobnik. Wysokość ≥ 2,0 m. Posadowienie urządzeń na wibroizolatorach. Nie sytuować bezpośrednio przy sypialniach bez przegród akustycznych (§ 96).

### 3.5 Instalacje
20. **Woda:**
   * wodomierz w budynku na P0 (§ 116), zawór antyskażeniowy za wodomierzem wg PN-EN 1717 (§ 115 ust. 2);
   * ciśnienie przy punktach 0,05–0,6 MPa (reduktor, gdy sieć przekracza);
   * c.w.u. 55–60 °C i możliwość dezynfekcji (§ 120 ust. 2a). Przy wybranej metodzie cieplnej trzeba uzyskać 70–80 °C w punktach czerpalnych (grzałka lub cykl pompy ciepła);
   * cyrkulacja opcjonalna;
   * izolacje wg zał. 2 pkt 1.5.
21. **Kanalizacja:**
   * piony wentylowane ponad dach P2 (w odległości poziomej < 4 m od okien: powyżej ich górnej krawędzi);
   * zawory napowietrzające dopuszczalne tylko przy spełnieniu § 125 ust. 2;
   * wywiewki ≥ 6 m od czerpni dachowej i ≥ 8 m od czerpni ściennej.
22. **Ogrzewanie:** pompa ciepła powietrze–woda i ogrzewanie podłogowe.
   * Obliczenia wg PN-EN 12831:2006: θi = 20 °C w pokojach, holach i kuchni, 24 °C w łazienkach; θe dla Poznania do potwierdzenia z normą (−18 °C?).
   * **Automatyczna regulacja w każdym pomieszczeniu** (termostaty i siłowniki na rozdzielaczach) (§ 135 ust. 7).
   * Temperatura zasilania ≪ 90 °C.
   * Garaż: nieogrzewany (zalecane) albo +5 °C, co zmienia wymagania U (E-04, E-07).
23. **Wentylacja mechaniczna z odzyskiem ciepła.**
   * Nawiew ≥ 20 m³/h na osobę (≥ 100 m³/h dla 5 osób), bilans z wywiewem wg PN-B-03430/Az3 (wartości do potwierdzenia normą).
   * Przepływ pokoje → kuchnia i łazienki. Brak kanałów grawitacyjnych w tych pomieszczeniach.
   * Czerpnia ≥ 2 m nad terenem i ≥ 8 m od wywiewek i miejsca na odpady, albo na dachu ≥ 0,4 m nad powierzchnią i ≥ 6 m od wywiewek.
   * Wyrzutnia na dachu lub w ścianie przy spełnieniu § 152 ust. 9.
   * SFP ≤ 1,60/1,00 (+0,3 przy η > 67%). Filtry ≥ G4 (ekwiwalent ISO 16890 do ustalenia).
   * Kanały plastikowe dopuszczalne (§ 267 ust. 1a). Przewody powietrza zewnętrznego i wyrzutu izolowane cieplnie i paroszczelnie.
   * Okap kuchenny: recyrkulacyjny albo z osobnym wyrzutem, nie do rekuperatora (dobra praktyka).
24. **Elektryka:**
   * układ **TN-S**, **RCD**, **SPD**, selektywność, połączenia wyrównawcze główne i miejscowe;
   * **uziom fundamentowy w ławach lub płycie** (§ 184 ust. 1);
   * obwody wydzielone wg § 188 ust. 2;
   * łączniki wieloobwodowe w pokojach (§ 189 ust. 2);
   * miedź ≤ 10 mm², trasy proste, tynk ≥ 5 mm nad przewodami.

   **PWP:** obliczyć kubaturę strefy pożarowej (cały budynek z garażem, § 3 pkt 24). Jeśli **> 1000 m³**, co jest prawdopodobne, zaprojektować przeciwpożarowy wyłącznik prądu przy wejściu lub złączu.

   **LPS:** analiza ryzyka wg PN-EN 62305-2 (PV na dachu). Dodatkowo obwód dla ładowarki EV w garażu (§ 180 pkt 1, dobra praktyka).
25. **Przepusty** instalacji przez ściany zewnętrzne poniżej terenu muszą być **gazoszczelne** (§ 234 ust. 4). Wymóg obowiązuje zawsze, niezależnie od sieci gazowej w ulicy. Przepusty przez płytę na gruncie wykonać tak samo jako dobrą praktykę, bo przepis wymienia tylko ściany. *(Poprawka weryfikacji: wcześniej było „przez ściany i płytę… bo w ulicy jest gaz”.)*

### 3.6 Energia i fizyka budowli
26. Przyjąć wartości docelowe z zapasem względem Umax:

    | Przegroda | Wartość docelowa | Umax |
    |---|---|---|
    | ściany zewnętrzne | U ≤ 0,17 | 0,20 |
    | stropodachy i stropy nad powietrzem zewnętrznym (wsporniki P2) | U ≤ 0,12 | 0,15 |
    | podłoga na gruncie | U ≤ 0,25 | 0,30 |
    | obwodowa izolacja podłogi na gruncie | R ≥ 2,0 (obowiązkowo) | — |
    | okna i przeszklenia stałe | Uw ≤ 0,8 | 0,9 |
    | drzwi zewnętrzne | Ud ≤ 1,1 | 1,3 |
    | klapa dachowa | ≤ 1,1 | 1,1 (jak okno połaciowe; jako drzwi 1,3) |

    **EP ≤ 70 kWh/(m²·rok)**; przy chłodzeniu pompą ciepła dochodzi ΔEP_C = 5·Af,C/Af.
27. **g ≤ 0,35** dla przeszkleń E, S, W (duże przeszklenia P0, boks C, okna P2). Osłony zewnętrzne (fC ≈ 0,10–0,15), np. raffstory lub screeny, albo szyby przeciwsłoneczne, albo okap spełniający pkt 2.1.1, **wykazany obliczeniowo**. Elewacja N ± 45° zwolniona.
28. **Mostki cieplne wsporników** (płyty wysunięte 0,8–1,5 m, wspornik P2, rama boksu C): łączniki termoizolacyjne, obliczenie fRsi ≥ 0,72 (PN-EN ISO 10211) i sprawdzenie kondensacji wg PN-EN ISO 13788.
29. Okna klasy 3 szczelności (PN-EN 12207). Cel **n50 ≤ 1,0 h⁻¹** (WT zaleca < 1,5), próba blower-door po zakończeniu budowy.
30. Hałas:
   * jednostkę zewnętrzną pompy ciepła lokalizować i dobierać tak, by na granicy z działkami MN było ≤ 50 dB w dzień i **≤ 40 dB w nocy** (Dz.U. 2014 poz. 112);
   * izolacyjność przegród i poziomy dźwięku wewnątrz wg PN-B-02151-2:2018-01 i PN-B-02151-3:2015-10 (do sprawdzenia w PT).

---

## 4. Nierozstrzygnięte / ryzyka

1. **Brak oświadczenia z art. 102a oznacza lukę normatywną.** Jeśli inwestor nie złoży oświadczenia, PZT nie ma wiążących WT, a organ sprawdza zgodność PZT z „przepisami, w tym techniczno-budowlanymi” (art. 35 ust. 1 pkt 2 PB). Grozi to sporami i uchyleniem decyzji [S-IB1], [S-PDOIIB]. **Decyzja: oświadczenie jest obowiązkowym elementem kompletu.**
2. **Nowe WT mogą zostać ogłoszone przed złożeniem wniosku.** Art. 102a to uprawnienie ustawowe na 18 miesięcy, niezależne od wejścia w życie nowego rozporządzenia. Ustawa ma pierwszeństwo przed ewentualnymi przepisami przejściowymi nowego rozporządzenia, ale jest to **NIEZWERYFIKOWANE** (nie znamy treści ostatecznej). Projekt RCL 12398903 według źródła wtórnego nie zaostrza na starcie EP ani U [S-PZB]: NIEZWERYFIKOWANE.
3. **Etap projektu RCL 12398903** nie został sprawdzony u źródła (legislacja.gov.pl: HTTP 503 lub reset połączenia 24–25.09.2026). Ponowić sprawdzenie przed złożeniem wniosku.
4. **Rozbieżność dat** (ELI: utrata mocy 21.09; ustawa: WT „obowiązujące do 19.09”, okres „od 20.09”). Bez wpływu na treść. Koniec okresu 18 miesięcy: 19 czy 20.03.2028. Przyjęto bezpiecznie 19.03.2028.
5. **Nazwa ministerstwa w komunikacie z 18.09.2026:** „MRiT” według źródeł wtórnych, a według Dz.U. 2026 poz. 597 minister właściwy to MFiG. Do wyjaśnienia (nie wpływa na projekt).
6. **Formularz PB-1** (Dz.U. 2026 poz. 255) powstał przed art. 102a i nie ma pola na oświadczenie. Dołączyć jako załącznik dodatkowy (R2).
7. **§ 271 ust. 4–5 a budynki z § 213** (zwiększenie odległości przy ścianach z otworami): stosowanie do domów jednorodzinnych jest **NIEZWERYFIKOWANE**, nie znalazłem źródła rozstrzygającego. Podejście ostrożne:
   * ściany i dach NRO;
   * potwierdzić na mapie do celów projektowych rzeczywiste odległości budynków sąsiadów;
   * ograniczyć duże przeszklenia na elewacjach E i W.

   Gdyby przyjąć +100% (16 m), przy sąsiadach 8 m od granicy nasze ściany E i W musiałyby stać ≥ 8 m od granic. Rozważyć konsultację z rzeczoznawcą ppoż.
8. **Kubatura strefy pożarowej a PWP** (§ 183 ust. 2): obliczyć z modelu (`model/budynek.yaml`). Przy > 1000 m³ PWP jest obowiązkowy.
9. **Normy przywołane w WT (treść płatna, niezweryfikowana):**
   * PN-B-03430:1983/Az3:2000 (strumienie powietrza);
   * PN-EN 12831:2006 i PN-B-02403:1982 (θe dla Poznania; brief zakłada −18 °C);
   * PN-B-02151-2:2018-01 i -3:2015-10 (wartości akustyczne);
   * PN-EN 62305-2:2008 (ryzyko piorunowe);
   * PN-B-01706:1992 (instalacje wodne);
   * PN-EN 779:2005 (wycofana, zastąpiona przez ISO 16890; ekwiwalent G4).

   WT przywołuje normy datowane, które stosuje się w przywołanym wydaniu. Normy niedatowane stosuje się w najnowszym wydaniu (zał. 1 odnośnik **).
10. **U dla stropu nad powietrzem zewnętrznym** (wspornik P2, podcienie): tabela zał. 2 nie ma wprost takiej pozycji. Przyjęto lp. 5 („nad przejazdami”, 0,15), a nie lp. 7 (0,25), ostrożnie.
11. **Garaż ogrzewany czy nieogrzewany:** decyzja zmienia wymagania U (ściana dom–garaż 0,30 vs przegrody garażu 0,90/0,70/1,50) oraz wentylację (0,04 m² na stanowisko vs 1,5 wymiany/h). Rekomendacja: nieogrzewany, poza obrysem cieplnym.
12. **Okna przesuwne (HS) na P2** a § 299 ust. 1 („skrzydła otwierane do wewnątrz”): przepis nie odnosi się do okien przesuwnych, co jest przedmiotem interpretacji. Bezpieczniej: HS przesuwne od wewnątrz z dolną szybą stałą lub balustradą (K-17).
13. **Wysokość budynku wg MPZP vs § 6 WT:** MPZP (fikcyjny) musi jednoznacznie określić sposób pomiaru, w tym attyki i wyłazu. Przy 3 kondygnacjach po ok. 3,15 m zapas do 11,0 m wynosi ok. 0,6–1,0 m.
14. **Analiza akustyczna z § 23 pkt 4a rozporządzenia o projekcie budowlanym** (od 01.08.2024) i jej zakres dla domu z 1 lokalem: poza R3, do rozstrzygnięcia w R2.
15. **§ 180 pkt 1 WT: infrastruktura ładowania EV „zgodnie z przepisami ustawy o elektromobilności”.** *Rozstrzygnięte w weryfikacji.* Ustawa (t.j. Dz.U. 2026 poz. 1243, art. 12 i 12a) nie nakłada obowiązków na domy jednorodzinne.
16. **Dezynfekcja c.w.u.** (§ 120 ust. 2a): wymagana jest możliwość dezynfekcji chemicznej lub fizycznej. Jeśli wybierzemy metodę cieplną, w punktach czerpalnych musi być 70–80 °C, co przy pompie ciepła wymaga grzałki lub zasobnika o odpowiedniej temperaturze. Metodę wskazać w PT.
17. **Postępowanie po 20.03.2028** (np. zmiana pozwolenia): obejmuje je art. 102a ust. 4 („decyzji administracyjnych dotyczących całego zamierzenia”). Użytkowanie (art. 102c) stare przepisy obejmują tylko przez 18 miesięcy, co jest poza zakresem projektu.

---

## 5. Źródła

### Pierwotne (API ELI Sejmu, Dziennik Ustaw)
[WT]: https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf
[WT-meta]: https://api.sejm.gov.pl/eli/acts/DU/2002/690
[Z2442]: https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf
[Z474]: https://api.sejm.gov.pl/eli/acts/DU/2024/474/text.pdf
[Z726]: https://api.sejm.gov.pl/eli/acts/DU/2024/726/text.pdf
[Z2285]: https://api.sejm.gov.pl/eli/acts/DU/2017/2285/text.pdf
[Z926]: https://api.sejm.gov.pl/eli/acts/DU/2013/926/text.pdf
[WT2015]: https://api.sejm.gov.pl/eli/acts/DU/2015/1422/text.pdf
[U1161]: https://api.sejm.gov.pl/eli/acts/DU/2026/1161/text.pdf
[U1081]: https://api.sejm.gov.pl/eli/acts/DU/2024/1081/text.pdf
[U975]: https://api.sejm.gov.pl/eli/acts/DU/2022/975/text.pdf
[D1696]: https://api.sejm.gov.pl/eli/acts/DU/2019/1696
[D1411]: https://api.sejm.gov.pl/eli/acts/DU/2024/1411/text.pdf
[PB]: https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf
[N1847]: https://api.sejm.gov.pl/eli/acts/DU/2025/1847/text.pdf
[RZF597]: https://api.sejm.gov.pl/eli/acts/DU/2026/597/text.pdf
[H112]: https://api.sejm.gov.pl/eli/acts/DU/2014/112/text.pdf
[EM1243]: https://api.sejm.gov.pl/eli/acts/DU/2026/1243/text.pdf
[DU2026]: https://api.sejm.gov.pl/eli/acts/DU/2026
[SEARCH]: https://api.sejm.gov.pl/eli/acts/search?publisher=DU&title=warunk%C3%B3w%20technicznych%2C%20jakim%20powinny%20odpowiada%C4%87%20budynki&limit=50

* WT (t.j. 2022): <https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf>. Metadane aktu bazowego (status, repealDate): <https://api.sejm.gov.pl/eli/acts/DU/2002/690>
* Zmiany WT:
  * 2023/2442: <https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf>
  * 2024/474: <https://api.sejm.gov.pl/eli/acts/DU/2024/474/text.pdf>
  * 2024/726: <https://api.sejm.gov.pl/eli/acts/DU/2024/726/text.pdf>
  * 2017/2285: <https://api.sejm.gov.pl/eli/acts/DU/2017/2285/text.pdf>
  * brzmienie z 2013/926: <https://api.sejm.gov.pl/eli/acts/DU/2013/926/text.pdf>
  * t.j. 2015/1422: <https://api.sejm.gov.pl/eli/acts/DU/2015/1422/text.pdf>
* Ustawa 2026/1161 (art. 102a–102c PB): <https://api.sejm.gov.pl/eli/acts/DU/2026/1161/text.pdf>
* UD, art. 66:
  * metadane: <https://api.sejm.gov.pl/eli/acts/DU/2019/1696>
  * t.j. 2024/1411: <https://api.sejm.gov.pl/eli/acts/DU/2024/1411/text.pdf>
  * zmiany: <https://api.sejm.gov.pl/eli/acts/DU/2024/1081/text.pdf>, <https://api.sejm.gov.pl/eli/acts/DU/2022/975/text.pdf>
* PB t.j. 2026/524: <https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf>. Zmiana 2025/1847: <https://api.sejm.gov.pl/eli/acts/DU/2025/1847/text.pdf>
* Rozp. MFiG 2026/597 (odnośnik o ministrze): <https://api.sejm.gov.pl/eli/acts/DU/2026/597/text.pdf>
* Hałas w środowisku, t.j. 2014/112: <https://api.sejm.gov.pl/eli/acts/DU/2014/112/text.pdf>

### Wtórne (niewiążące)
[S-prawo]: https://www.prawo.pl/biznes/nowe-rozporzadzenie-ws-warunkow-technicznych-dla-budynkow-2026,1553166.html
[S-IB1]: https://inzynierbudownictwa.pl/nowych-warunkow-technicznych-nie-ma-co-dalej/
[S-IB2]: https://inzynierbudownictwa.pl/warunki-techniczne-na-starych-zasadach-jak-zlozyc-oswiadczenie/
[S-IB3]: https://inzynierbudownictwa.pl/nowe-warunki-techniczne-odroczone-rekomendacje-polskiej-izby-inzynierow-budownictwa/
[S-IARP]: https://www.izbaarchitektow.pl/pokaz/komunikat-ministerstwa-rozwoju-i-technologii,3942/
[S-PDOIIB]: https://zpr.pdl.piib.org.pl/2026/09/18/stare-wt-po-20-wrzesnia-komunikat-mrit-nie-rozwiazuje-wszystkich-watpliwosci/
[S-GOV]: https://www.gov.pl/web/rozwoj-technologia/konsultacje-projektu-rozporzadzenia-w-sprawie-warunkow-technicznych-jakim-powinny-odpowiadac-budynki-i-usytuowanie
[S-RCL]: https://legislacja.rcl.gov.pl/projekt/12398903
[S-PZB]: https://pozytywniezbudowani.pl/blog/wt2026-warunki-techniczne-co-oznaczaja-dla-projektu/
[S-KP]: https://www.klimatyzacja.pl/wentylacja/poradnik/normy-i-przepisy/ilosci-powietrza-w-polskich-normach

* prawo.pl, 18.09.2026: <https://www.prawo.pl/biznes/nowe-rozporzadzenie-ws-warunkow-technicznych-dla-budynkow-2026,1553166.html>
* Inżynier Budownictwa:
  * 18.09.2026: <https://inzynierbudownictwa.pl/nowych-warunkow-technicznych-nie-ma-co-dalej/>
  * 22.09.2026: <https://inzynierbudownictwa.pl/warunki-techniczne-na-starych-zasadach-jak-zlozyc-oswiadczenie/>
  * 21.09.2026: <https://inzynierbudownictwa.pl/nowe-warunki-techniczne-odroczone-rekomendacje-polskiej-izby-inzynierow-budownictwa/>
* Izba Architektów RP, komunikat: <https://www.izbaarchitektow.pl/pokaz/komunikat-ministerstwa-rozwoju-i-technologii,3942/>
* ZPR PDOIIB, 18.09.2026: <https://zpr.pdl.piib.org.pl/2026/09/18/stare-wt-po-20-wrzesnia-komunikat-mrit-nie-rozwiazuje-wszystkich-watpliwosci/>
* gov.pl, konsultacje projektu WT (13.06.2025): <https://www.gov.pl/web/rozwoj-technologia/konsultacje-projektu-rozporzadzenia-w-sprawie-warunkow-technicznych-jakim-powinny-odpowiadac-budynki-i-usytuowanie>
* RCL, projekt 12398903 (niedostępny przy weryfikacji): <https://legislacja.rcl.gov.pl/projekt/12398903>
* pozytywniezbudowani.pl, 19.07.2026: <https://pozytywniezbudowani.pl/blog/wt2026-warunki-techniczne-co-oznaczaja-dla-projektu/>
* klimatyzacja.pl (wartości PN-B-03430/Az3): <https://www.klimatyzacja.pl/wentylacja/poradnik/normy-i-przepisy/ilosci-powietrza-w-polskich-normach>

---

## 6. Weryfikacja niezależna (2026-09-25)

**Kto i jak weryfikował.** Weryfikację przeprowadził niezależny weryfikator-adwersarz. Wszystkie teksty aktów pobrał od nowa z API ELI Sejmu (PDF → pymupdf) do katalogu `scratchpad/research/R3ver/`, bez korzystania z plików roboczych autora.

**Stan Dz.U. na 25.09.2026:**
* wykaz DU/2026 kończy się na poz. **1244** (23.09.2026);
* poz. 1245, 1246, 1247, 1250 i 1260 zwracają HTTP 404;
* wyszukiwanie ELI po tytule „warunków technicznych” od 01.01.2025 nie zwraca nowego rozporządzenia o WT dla budynków, a jedynie WT dla budowli hydrotechnicznych (2026/692), budowli kolejowych (2026/1225), budowli ochronnych (2025/1548, MSWiA) i inne akty niezwiązane z tematem.

### 6.1 Potwierdzone (źródło pierwotne, tekst aktu)

**Status prawny WT**
* **S-01, CF-01.** WT z 2002 r. oraz t.j. 2022/1225, 2022/248, 2023/2442, 2024/474 i 2024/726 mają w ELI status „uznany za uchylony”, repealDate 2026-09-21 i „Uchylenia wynikające z: DU/2019/1696”.
* **Art. 66 UD.** Historia terminu potwierdzona na tekstach: 36 mies. (2019/1696), 60 mies. (2022/975, art. 2, w życie dzień po ogłoszeniu 10.05.2022), 84 mies. (2024/1081, art. 1, w życie 03.08.2024).
* **Wejście w życie UD:** 20.09.2019.
* **Inne akty uznane za uchylone:** 1999/836, 2013/640 (sieci gazowe) i 1995/271.

**Przepis epizodyczny (Dz.U. 2026 poz. 1161)**
* **S-02, CF-02.** Brak nowych WT dla budynków.
* **S-03 do S-05, CF-03, CF-04.** Brzmienie art. 102a ust. 1, 2 i 4, art. 102b i art. 102c potwierdzono słowo w słowo.
* **Daty 1161:** ogłoszenie 01.09.2026; art. 5 (art. 2 pkt 4 w życie dzień po ogłoszeniu, reszta po 30 dniach); ELI entryIntoForce 2026-10-02.

**PB i wzór PB-1**
* **S-06, S-07, CF-05.** Art. 35 ust. 1 pkt 2 i art. 5 ust. 1 PB (t.j. 2026/524). Art. 35 ust. 1 nie przewiduje sprawdzania zgodności PAB z WT.
* **PB-1.** Wzór PB-1 (Dz.U. 2026 poz. 255, MFiG z 17.02.2026, w życie 04.03.2026) nie ma pola na oświadczenie z art. 102a. Ma pole „Inne (wymagane przepisami prawa)”.

**Ministerstwo i zmiany WT**
* **Minister.** Odnośnik 1 do Dz.U. 2026 poz. 597: działem budownictwa kieruje Minister Finansów i Gospodarki (rozp. PRM z 25.07.2025, Dz.U. 2025 poz. 997).
* **Tabela 1.2.** Zakres zmian 2022/248 (w życie 17.02.2022), 2023/2442 (§ 3 pkt 27, § 12 ust. 1–3, 6, 8, 10, 11, § 20, § 39, § 40, § 56a, § 76, § 85a, § 95a, § 98a, § 326, zał. 1) oraz 2024/474 (przesunięcie na 01.08.2024).
* **2024/726.** Zmiany § 12 ust. 1 (część wspólna), ust. 1a i 10a, zał. 1a, § 216 ust. 2 pkt 4–5, § 232 ust. 8–9, § 249 ust. 5a; w życie 3 miesiące od ogłoszenia 14.05.2024, czyli 15.08.2024.
* **E-13, B-19, CF-14.** A0max był w zał. 2 pkt 2.1.1 w brzmieniu 2013/926. Dawny § 94 ust. 2 (16 m²) był w t.j. 2015/1422. Rozp. 2017/2285 zmieniło: § 1 pkt 21 (uchylenie § 80), pkt 27 (nowy § 94), pkt 67 (nowy zał. 2); w życie 01.01.2018.

**Wymagania WT: identyfikatory potwierdzone na tekście t.j. 2022/1225 i zmian**
* **D:** D-02 do D-09.
* **U:** U-01 do U-09.
* **Z:** Z-01 do Z-19.
* **B:** B-01 do B-22, B-24, B-25.
* **K:** K-01 do K-15, K-17 do K-22.
* **Instalacje:** IW-01 do IW-05, IW-07 do IW-09, IK-01 do IK-04, IO-01 do IO-09, IV-01, IV-02, IV-04 do IV-16, IE-02 do IE-10.
* **Pożar:** P-01 do P-19.
* **Higiena i hałas:** H-01 do H-11 (H-11 sprawdzono w t.j. Dz.U. 2014 poz. 112, tab. 1 lp. 2a: 50/40 dB).
* **Energia:** E-01 do E-19. Zał. 2 pkt 1.1, 1.2, 1.4, 1.5, 2.1.1–2.1.4, 2.2.1–2.2.5 i 2.3.1–2.3.4; § 328–§ 329 (EP_H+W = 70; ΔEP_C = 5·Af,C/Af).

**Pozostałe potwierdzenia**
* **Normy przywołane w zał. 1 WT** (numery lp. zgodne z rejestrem): lp. 1, 4, 5, 6, 8, 10 (PN-EN 12056-1…5:2002, PN-EN 12109:2003), 14, 16 (PN-EN 12831:2006), 17, 26, 28, 32, 33, 41, 44, 59 (PN-EN 1990/1991), 69–73.
* **Kluczowe ustalenia JSON:** CF-07 do CF-19 i CF-20 w części sprawdzalnej (§ 280 ust. 3, § 279 ust. 1–2, § 281, § 106 ust. 1, § 107, § 108). Uwaga do CF-20: odległość **w pionie** 1,5 m z § 279 ust. 1 dotyczy wszystkich okien budynku, a nie tylko okien pomieszczeń na pobyt ludzi. Wiersz P-07 w tabeli ujmuje to poprawnie.
* **Ryzyko 14.** § 23 pkt 4a rozp. o projekcie budowlanym (analiza akustyczna) dodał § 1 pkt 3 rozp. 2023/2405. W życie 01.08.2024 według 2024/473.

**Źródła wtórne (NIE, sprawdzone WebFetch)**
* **CF-06.** Inżynier Budownictwa, 22.09.2026: „Oświadczenie składa inwestor, nie projektant”; nie wymaga „przyjęcia, zatwierdzenia ani potwierdzenia przez organ”; „Treści wzoru nie należy zmieniać”; koniec okresu 20.03.2028.
* **Komunikat.** prawo.pl, 18.09.2026: komunikat przypisany MRiT, cytat „Od dnia 20 września 2026 r. w okresie 18 miesięcy…”, prace nad rozporządzeniem „są nadal prowadzone”.

### 6.2 Poprawione (było → jest)

| ID | Było | Jest | Źródło |
|---|---|---|---|
| 1.1 pkt 3 (art. 102b) | „robót z art. 29 ust. 4, czyli bez projektu” | Budowa i roboty, które nie wymagają ani pozwolenia, ani zgłoszenia (art. 29 ust. 2 i 4 PB). Dodano też art. 102a ust. 3 | Dz.U. 2026 poz. 1161 art. 2 pkt 4; Dz.U. 2026 poz. 524 art. 29 ust. 2 i 4 |
| D-01 | Cytat § 6 urwany po „pomieszczeń technicznych” | Dodano wariant „bądź do najwyżej położonego punktu stropodachu lub konstrukcji przekrycia budynku znajdującego się bezpośrednio nad pomieszczeniami przeznaczonymi na pobyt ludzi” | WT § 6 (t.j. 2022/1225) |
| IW-06, impl. 20, ryzyko 16 | „Możliwość dezynfekcji termicznej 70–80 °C” | Wymagana możliwość dezynfekcji chemicznej lub fizycznej. 70–80 °C obowiązuje tylko przy metodzie cieplnej | WT § 120 ust. 2a |
| IE-01, ryzyko 15 | Wymogi ustawy o elektromobilności dla domu jednorodzinnego: NIEZWERYFIKOWANE | Brak obowiązku dla domów jednorodzinnych. Art. 12 dotyczy UP i wielorodzinnych, art. 12a budynków niemieszkalnych z > 10 stanowiskami | Dz.U. 2026 poz. 1243 (t.j.), art. 12, 12a |
| Impl. 25 (§ 234 ust. 4) | „przez ściany i płytę… bo w ulicy jest gaz” | Wymóg bezwarunkowy i tylko dla ścian zewnętrznych poniżej terenu. Płyta: dobra praktyka | WT § 234 ust. 4 |
| K-16 | Tylko okna powyżej 2. kondygnacji | Także okna niższych kondygnacji wychodzące na chodniki lub przejścia dla pieszych | WT § 299 ust. 1 |
| B-23 | Szerokość stanowiska 2,5 m podana jak wymóg dla garażu | Oznaczono jako interpretację (§ 21 dotyczy stanowisk na działce; § 104 nie podaje szerokości stanowiska) | WT § 21 ust. 1, § 104 |
| B-26 | 0,04 m² na stanowisko, 2 st. = 0,08 m² | Doprecyzowano: „na każde, wydzielone przegrodami budowlanymi, stanowisko”, więc 0,08 m² to ostrożna interpretacja | WT § 108 ust. 1 pkt 1 |

### 6.3 Niemożliwe do weryfikacji (stan na 25.09.2026)
* **Projekt RCL 12398903** (etap, treść, przepisy przejściowe): legislacja.gov.pl i legislacja.rcl.gov.pl zrywają połączenie (curl exit 35).
* **Wartości z Polskich Norm** (treść płatna): IV-03 (PN-B-03430/Az3), θe dla Poznania (PN-B-02403 / PN-EN 12831), wartości akustyczne (PN-B-02151-2/-3), wynik analizy ryzyka piorunowego (PN-EN 62305-2) oraz ekwiwalent klasy G4 w ISO 16890.
* **Autorstwo komunikatu z 18.09.2026** (MRiT według źródeł wtórnych, a według Dz.U. 2026/597 właściwy jest MFiG): brak źródła pierwotnego.
* **Interpretacje**, dla których nie ma rozstrzygnięcia w źródle pierwotnym:
  * dokładny dzień końca okresu 18 miesięcy (19 czy 20.03.2028);
  * stosowanie § 271 ust. 4–5 do budynków z § 213;
  * okna przesuwne HS a § 299 ust. 1;
  * U stropu nad powietrzem zewnętrznym;
  * zakres art. 102a ust. 4 po 20.03.2028.
