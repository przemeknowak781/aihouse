# R7 — Instalacje elektryczne, odgromowe i teletechniczne: rejestr wymagań

**Projekt:** Dom LAMELA. Budynek mieszkalny jednorodzinny wolnostojący, 3 kondygnacje nadziemne, bez podpiwniczenia, dachy płaskie, 1 lokal mieszkalny, garaż 2-stanowiskowy w bryle, dom all-electric (pompa ciepła powietrze–woda, rekuperacja, PV ≤ 6,5 kWp). Działka przykładowa pod Poznaniem (woj. wielkopolskie), sieć nN 0,4 kV w drodze, OSD dla tego obszaru: ENEA Operator.
**Domena:** R7. Instalacja elektryczna (WT § 180–§ 189, seria PN-HD 60364), ochrona odgromowa (WT § 53, seria 62305), przyłącze nN, PV prosumenckie, ładowanie EV, instalacja telekomunikacyjna, przeciwpożarowy wyłącznik prądu.
**Data weryfikacji:** 2026-09-25.

**Metoda:**
* Teksty aktów prawnych pobrałem z API ELI Sejmu (PDF), tekst wyciągnąłem biblioteką pymupdf. Tekst WT (t.j. Dz.U. 2022 poz. 1225) wziąłem z plików roboczych zespołu R3. W kolumnie „pierw.” te źródła mają „TAK”.
* Akty UE (EPBD 2024/1275, GIA 2024/1309) pobrałem z EUR-Lex (tekst PL). Też „TAK”.
* Status norm sprawdziłem w wyszukiwarce PKN (wiedza.pkn.pl) 25.09.2026. Zapis wyników: `R7_pkn_status_2026-09-25.json`. Status normy to „TAK”, jej treść nie.
* Treść norm jest płatna. Wartości liczbowe z norm potwierdzam:
  * tekstem IEC (bezpłatne podglądy iTeh, publiczna kopia IEC 60364-7-712:2017) — oznaczenie „IEC”;
  * albo źródłami wtórnymi (SEP, RST, elektro.info, INPE, producenci) — oznaczenie „NIE”.
  * Czego nie potwierdziłem, oznaczam **NIEZWERYFIKOWANE**.
* Dokumenty OSD (standardy ENEA Operator, PTPiREE) oznaczam „OSD”. Nie są przepisami prawa, ale wiążą w procesie przyłączenia.

**Pliki robocze:** `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R7/`, w tym:
* `*.txt` — teksty aktów, norm IEC i źródeł wtórnych;
* `R7_pkn_status_2026-09-25.json` — status norm w PKN;
* `batch.py`, `pkn.py`, `pknparse.py` — skrypty zapytań PKN.

**Skróty:**
* **WT** — rozp. MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie. W tekście: „WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) §…”.
  > **Status WT wymaga potwierdzenia przez zespół R3.** ELI podaje dla Dz.U. 2002 nr 75 poz. 690 status „uznany za uchylony” z datą 2026-09-21. Według R3 WT stosuje się na podstawie art. 102a PB (Dz.U. 2026 poz. 1161), po złożeniu oświadczenia inwestora, a wniosek trzeba złożyć w ciągu 18 miesięcy od 20.09.2026. Wszystkie odwołania do WT w tym dokumencie zakładają ten tryb.
* **PB** — ustawa Prawo budowlane, t.j. Dz.U. 2026 poz. 524 ze zm.
* **PE** — ustawa Prawo energetyczne, t.j. Dz.U. 2026 poz. 43, zm. m.in. Dz.U. 2026 poz. 516 i 900.
* **OZE** — ustawa o odnawialnych źródłach energii, t.j. Dz.U. 2026 poz. 68.
* **RSys** — rozp. MKiŚ z 22.03.2023 w sprawie szczegółowych warunków funkcjonowania systemu elektroenergetycznego, t.j. Dz.U. 2025 poz. 919, zm. Dz.U. 2026 poz. 668.
* **ROPoż** — rozp. MSWiA z 7.06.2010 w sprawie ochrony przeciwpożarowej budynków, innych obiektów budowlanych i terenów, t.j. Dz.U. 2023 poz. 822, zm. Dz.U. 2024 poz. 1716. Akt obowiązujący (ELI). Wydano go na podstawie ustawy o ochronie ppoż., więc nie wygasł razem z WT.
* **UEm** — ustawa o elektromobilności i paliwach alternatywnych, t.j. Dz.U. 2026 poz. 1243 (stan prawny na 26.08.2026).
* **EPBD** — dyrektywa (UE) 2024/1275.
* **GIA** — rozporządzenie (UE) 2024/1309 (Gigabit Infrastructure Act).
* **RCD** — wyłącznik różnicowoprądowy. **SPD** — ogranicznik przepięć. **AFDD** — urządzenie do detekcji zwarć łukowych. **LPS** — urządzenie piorunochronne. **PWP** — przeciwpożarowy wyłącznik prądu. **ZKP** — złącze kablowo-pomiarowe. **RG** — rozdzielnica główna budynku. **GSU** — główna szyna uziemiająca (MET).

---

## 1. Streszczenie

1. **Większość norm elektrycznych przywołanych w WT jest wycofana, a ich następcy są surowsi.** Załącznik nr 1 do WT (lp. 1, 3, 41–47a) powołuje normy z datą wydania. W PKN (stan na 25.09.2026) wycofane są m.in.:

   | Norma w WT | Aktualny następca | Istotna zmiana |
   |---|---|---|
   | PN-HD 60364-4-41:2009 | 2017-09 | nowy wymóg RCD ≤ 30 mA dla obwodów oświetleniowych w lokalu jednej rodziny |
   | PN-HD 60364-4-43:2012 | 2024-04 | — |
   | PN-HD 60364-5-534:2012 | PN-HD 60364-5-53:2022-10 (ograniczniki przepięć włączono do 5-53) | — |
   | PN-HD 60364-7-701:2010 | 2025-02 (tylko wersja angielska) | — |
   | PN-HD 60364-6:2008 | 2016-07 | — |
   | **PN-EN 62305-1…4 (2008/2011/2012)** | **PN-EN IEC 62305-1…4:2025-09** (tylko wersja angielska) | — |

   Rekomendacja: projektować tak, aby spełnić jednocześnie literę WT (normy datowane) i aktualne normy (zasady wiedzy technicznej, art. 5 ust. 1 PB). Obecne normy są w praktyce surowsze.
2. **Rdzeń wymagań WT dla domu jednorodzinnego to § 183 ust. 1 pkt 1–10.** Obejmuje:
   * złącze w miejscu dostępnym;
   * **oddzielne przewody PE i N w obwodach rozdzielczych i odbiorczych**;
   * **RCD**;
   * wyłączniki nadprądowe w obwodach odbiorczych;
   * selektywność;
   * PWP;
   * połączenia wyrównawcze główne i miejscowe;
   * trasy przewodów równoległe do krawędzi;
   * **żyły wyłącznie miedziane do 10 mm²**;
   * **urządzenia ochrony przeciwprzepięciowej**.

   Dochodzą do tego:
   * uziom fundamentowy (§ 184 ust. 1);
   * obwody wydzielone w mieszkaniu (§ 188 ust. 2): oświetlenie, gniazda ogólne, gniazda w łazience, gniazda kuchenne, odbiorniki wymagające indywidualnego zabezpieczenia;
   * łączniki wieloobwodowe w pokojach (§ 189 ust. 2);
   * oświetlenie zewnętrzne wejścia (§ 64);
   * oświetlenie elektryczne garażu (§ 102 pkt 3).
3. **RCD 30 mA:**
   * na wszystkich obwodach gniazd ≤ 32 A (PN-HD 60364-4-41:2017, 411.3.3);
   * na obwodach oświetleniowych w lokalu jednej rodziny (411.3.4);
   * na wszystkich obwodach łazienek (7-701);
   * **indywidualnie dla każdego punktu ładowania EV**, typ A z detekcją DC 6 mA lub typ B (7-722).
4. **SPD jest obowiązkowy w dwóch trybach.**
   * WT § 183 ust. 1 pkt 10 wymaga ochrony przeciwprzepięciowej bezwarunkowo.
   * Według PN-HD 60364-4-443:2016 ocena CRL dla przedmieść Poznania daje CRL < 1000 dla każdej realistycznej długości linii kablowej nN. Nawet przy L_P = 0,1 km i N_g = 1,8 wychodzi CRL ≈ 944, więc SPD jest wymagany.
   * Skoro SPD jest wymagany po stronie AC, to według IEC 60364-7-712 (712.443.4.101) **także po stronie DC instalacji PV**.
5. **Uziom:**
   * Jeżeli płyta lub ławy są w pełni izolowane termicznie (XPS) albo przeciwwodnie (folia > 0,5 mm), beton fundamentu nie działa jako uziom (PN-HD 60364-5-54:2011, zał. C.2).
   * Wtedy trzeba wykonać **uziom otokowy w gruncie** pod izolacją lub wokół budynku (Cu, StCu lub StSt). Zbrojenie łączy się z nim jako element połączeń wyrównawczych.
   * **Decyzję o wariancie posadowienia trzeba skoordynować z R5.**
6. **Ochrona odgromowa (LPS):**
   * WT § 53 ust. 2 wiąże obowiązek z „Polską Normą dotyczącą ochrony odgromowej”. PN-EN 62305 nie zawiera listy obiektów, więc o LPS decyduje **analiza ryzyka** wg PN-EN 62305-2.
   * Mój wstępny szacunek dla domu 19 × 11 × 10,5 m przy N_g = 1,8: R1 ≈ 5,5·10⁻⁶ (< R_T = 10⁻⁵) przy „zwykłym” ryzyku pożaru, ale ≈ 3·10⁻⁵ przy „wysokim”. **Wynik zależy od klasy obciążenia ogniowego. Rozstrzygnąć w PT.**
   * Niezależnie od wyniku rekomenduję uziom otokowy przygotowany pod LPS i SPD typu 1+2.
7. **PWP:**
   * WT § 183 ust. 2 wymaga PWP w strefie pożarowej o kubaturze > 1000 m³. Dom z garażem stanowi jedną strefę i według R3 prawdopodobnie przekracza 1000 m³.
   * ROPoż § 4 ust. 2 pkt 2 **wyłącza z obowiązku wyposażenia w PWP właścicieli budynków mieszkalnych jednorodzinnych**.
   * Przepisy są niespójne. **Rekomendacja: zaprojektować PWP**, bo spełnia obie interpretacje przy małym koszcie. Rozstrzygnięcie zostawiam jako otwarte (R3/PPOŻ).
8. **Czujki dymu są obowiązkowe:**
   * ROPoż § 28a ust. 1 (dodany przez Dz.U. 2024 poz. 1716) wymaga co najmniej 1 autonomicznej czujki dymu w lokalu mieszkalnym.
   * Czujka tlenku węgla jest potrzebna tylko w pomieszczeniu ze spalaniem paliwa, z wyjątkiem zamkniętej komory spalania. Dom all-electric bez kominka jej nie potrzebuje.
9. **Przyłącze nN (ENEA Operator):**
   * grupa przyłączeniowa V: ≤ 1 kV, moc ≤ 40 kW (RSys § 3 ust. 1 pkt 5);
   * warunki przyłączenia w 21 dni, ważne 2 lata (PE art. 7 ust. 8g pkt 1, ust. 8i);
   * układ pomiarowy dla budownictwa jednorodzinnego **na zewnątrz budynku, w linii ogrodzenia** na terenie nieruchomości (standard ENEA);
   * ZKP ma zabezpieczenie przedlicznikowe w postaci wyłącznika nadprądowego o charakterystyce C (moduły 1-fazowe) oraz listwę dla kabla odbiorcy do 4×35 mm² z przewodem PEN (TN-C do ZKP);
   * pomiar bezpośredni przy mocy ≤ 40 kW i zabezpieczeniu przedlicznikowym ≤ 63 A.
10. **PV ≤ 6,5 kW:**
    * nie wymaga uzgodnienia z rzeczoznawcą ppoż. ani zawiadomienia PSP, bo ten obowiązek dotyczy PV > 6,5 kW (PB art. 29 ust. 4 pkt 3 lit. c w brzmieniu z Dz.U. 2025 poz. 1847; art. 56 ust. 1a uchylony);
    * „moc zainstalowana” to suma mocy modułów (OZE art. 2 pkt 19b lit. b);
    * mikroinstalację przyłącza się **na podstawie zgłoszenia**, jeżeli jej moc nie przekracza mocy z warunków przyłączenia. OSD przyłącza w 30 dni bez opłaty (PE art. 7 ust. 8d4–8d7, ust. 8 pkt 3 lit. b);
    * falownik musi mieć certyfikat NC RfG z listy PTPiREE. Od 1.01.2027 obowiązuje etap II procedury certyfikacji.
11. **EV:**
    * dla domu jednorodzinnego **nie ma obowiązku** infrastruktury ładowania, bo UEm art. 12 i 12a dotyczą budynków wielorodzinnych, UP oraz budynków z > 10 stanowiskami;
    * EPBD art. 14 ust. 4 obejmuje nowe budynki mieszkalne z **> 3 miejscami postojowymi** w budynku lub przylegającymi do niego. Wymaga okablowania wstępnego ≥ 50 % miejsc, kanałów na resztę i ≥ 1 punktu ładowania. Termin transpozycji minął 29.05.2026, ale do 26.08.2026 transpozycji nie ogłoszono, więc przepis nie wiąże inwestora wprost;
    * rekomendacja: projektować tak, jakby wymóg obowiązywał.
12. **Telekomunikacja — nowy obowiązek z GIA:**
    * WT (§ 26, § 56, § 192a–§ 192f) nie wymaga instalacji telekomunikacyjnej w domu jednorodzinnym;
    * **GIA art. 10 ust. 1, stosowane bezpośrednio od 12.02.2026**, wymaga, aby każdy nowy budynek, dla którego wniosek o pozwolenie na budowę złożono po 12.02.2026, miał wewnątrzbudynkową infrastrukturę przystosowaną do światłowodu **i okablowanie światłowodowe do punktu zakończenia sieci**;
    * Polska nie ogłosiła do 25.09.2026 aktu z kategoriami wyłączeń (art. 10 ust. 7), co sprawdziłem w ELI, więc **obowiązek dotyczy Domu LAMELA**.

---

## 2. Rejestr wymagań

Kolumna „pierw.”:
* **TAK** — tekst aktu prawnego z ELI lub EUR-Lex, sprawdzony;
* **PKN** — status normy sprawdzony w katalogu PKN;
* **IEC** — treść potwierdzona w tekście normy IEC (bazowej dla PN-HD), nie w samej PN;
* **OSD** — dokument operatora lub PTPiREE;
* **NIE** — źródło wtórne.

### A. Ramy prawne i status norm

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-A01 | WT: ELI podaje status „uznany za uchylony” od 2026-09-21. Projekt według WT wymaga oświadczenia inwestora z art. 102a PB. Oświadczenie obejmuje PZT, PAB i PT | ELI DU/2002/690; art. 102a PB (Dz.U. 2026 poz. 1161) | https://api.sejm.gov.pl/eli/acts/DU/2002/690 | TAK | **Status wymaga potwierdzenia przez zespół R3** |
| R7-A02 | Zał. 1 WT lp. 41 (§ 180) powołuje datowane normy: PN-HD 308 S2:2007, PN-HD 60364-1:2010, -4-41:2009, -4-42:2011, -4-43:2012, PN-IEC 60364-4-443:1999, -4-444:2012, -5-51:2011, PN-IEC 60364-5-52:2002, -5-523:2001, -5-534:2012, -5-54:2011, -5-559:2010, -5-56:2010, -6:2008, -7-701:2010, -7-714:2003, PN-EN 60445:2010, PN-EN 60446:2010, PN-EN 50310:2012, PN-EN 50160:2010, PN-EN 61140:2005, PN-EN 60529:2003 | WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) zał. 1 lp. 41 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Lp. 3 (§ 98 ust. 2) powtarza część tych norm dla pomieszczeń technicznych. Lp. 43: § 184 ust. 2 → PN-HD 60364-5-54:2011 |
| R7-A03 | Zał. 1 lp. 1 (§ 53 ust. 2): PN-EN 62305-1:2011, PN-EN 62305-2:2008. Lp. 44 (§ 184 ust. 3): PN-EN 62305-1:2011, -2:2008, -3:2011, -4:2011 oraz PN-IEC 60364-4-443:1999 | WT zał. 1 lp. 1, 44 | jw. | TAK | — |
| R7-A04 | **Status w PKN (25.09.2026), aktualne:** PN-HD 60364-1:2010 (+A11:2017); **-4-41:2017-09** (+A11:2017, A12:2020); -4-42:2011 (+A1:2015, A11:2022, Ap1, Ap2:2019); **-4-43:2024-04**; -4-443:2016-03; -4-444:2012; -5-51:2011 (+A11, A12); -5-52:2011 (+A11:2018, A12:2023, **A1:2025-11**, Ap1, Ap2:2019); **-5-53:2022-10** (+AC:2025); -5-54:2011 (+A11:2017, **A1:2023-04**); -5-559:2012; -5-56:2019-01; **-6:2016-07**; **-7-701:2025-02** (ang., +A11:2025); -7-712:2016-05; -7-714:2012; -7-722:2019-01; -8-1:2019-07; PN-HD 308 S2:2007; PN-EN IEC 60445:2022-04 | Katalog PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN | Wycofane: -4-41:2009, -4-43:2012, **-5-534:2016** (zastąpiona przez 5-53:2022-10), -6:2008, -7-701:2010, PN-EN 60445:2010 i 2018. Wyniki w `R7_pkn_status_2026-09-25.json` |
| R7-A05 | **Seria 62305:** PN-EN 62305-1:2011, -2:2012 (i 2008), -3:2011, -4:2011 są **wycofane**. Zastąpiły je **PN-EN IEC 62305-1:2025-09, -2:2025-09, -3:2025-09, -4:2025-09** (wersje angielskie; wprowadzają IEC/EN IEC 62305:2024) | Katalog PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN | WT (tryb art. 102a) powołuje wydania datowane, a wiedza techniczna — 2025. Analizę ryzyka zalecam wykonać wg PN-EN IEC 62305-2:2025. Wyniki mogą się różnić od 2008/2012: **NIEZWERYFIKOWANE** |
| R7-A06 | Pozostałe aktualne normy PKN: PN-EN IEC 62561-1:2023-12, -2:2018-04 (+AC:2020); PN-EN 50160:2023-10 (+A1:2025); PN-EN IEC 61643-11:2026-04 (ang.; zastąpiła PN-EN 61643-11:2013); PN-EN 62606:2014-05 (+A1:2018, A11:2026-08); PN-EN 62423:2013-06 (+A11, A12); PN-EN 61008-1:2013-05 i PN-EN 61009-1:2013-06 (ze zmianami); PN-EN 50618:2015-03; PN-EN 50549-1:2019-02 (+A1:2024); PN-EN 50174-2:2018-08; PN-EN 50173-4:2018-07 (+A1:2024); PN-EN IEC 61851-1:2019-10 (+AC:2024); PN-EN 50310:2016-09 (+A1:2020); PN-EN IEC 61439-3:2025-09 (ang.); PN-EN 14604:2006 (+AC:2009); PN-EN 50291-1:2018-06 | Katalog PKN | jw. | PKN | Normy zharmonizowane i wyrobów przywołuje się w opisie technicznym i zestawieniach |
| R7-A07 | N SEP-E-002 „Instalacje elektryczne w obiektach budowlanych. Instalacje elektryczne w budynkach mieszkalnych. Podstawy planowania” to **norma SEP, nie PN**. Zatwierdzona przez prezesa SEP 25.06.2003. Stosowanie dobrowolne jako zasady wiedzy technicznej | SEP | https://sep.com.pl/opracowania/opracowania_zasady_wyzn_mocy_zapotrzeb_dla_mieszkan.pdf | NIE | Data zatwierdzenia wg źródła wtórnego (wyniki wyszukiwania). Pełnej treści (tablice gniazd i wypustów) nie miałem |

### B. WT — instalacja elektryczna (§ 53, § 64, § 98, § 102, § 180–§ 189)

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-B01 | Budynek wyposaża się w wewnętrzną instalację elektryczną stosownie do potrzeb | WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) § 53 ust. 1 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Status WT: R3 |
| R7-B02 | Instalacja zapewnia: (1) dostawę energii o odpowiednich parametrach, **w tym infrastrukturę ładowania EV zgodnie z ustawą o elektromobilności**; (2) ochronę przed porażeniem, przepięciami łączeniowymi i atmosferycznymi, pożarem, wybuchem; (3) ochronę przed drganiami, hałasem i polem elektromagnetycznym | WT § 180 pkt 1–3 | jw. | TAK | Co do EV zob. R7-J01 (UEm nie nakłada obowiązków na dom jednorodzinny) |
| R7-B03 | Stosuje się (§ 183 ust. 1): 1) złącza umożliwiające odłączenie od sieci, w miejscu dostępnym, zabezpieczone przed uszkodzeniami, atmosferą i osobami niepowołanymi; 2) **oddzielny przewód ochronny i neutralny w obwodach rozdzielczych i odbiorczych**; 3) **urządzenia różnicowoprądowe**; 4) wyłączniki nadprądowe w obwodach odbiorczych; 5) **selektywność**; 6) PWP; 7) połączenia wyrównawcze główne i miejscowe; 8) trasy w liniach prostych, równoległych do krawędzi ścian i stropów; 9) **żyły wyłącznie miedziane, jeżeli przekrój ≤ 10 mm²**; 10) **urządzenia ochrony przeciwprzepięciowej** | WT § 183 ust. 1 | jw. | TAK | Markiewicz (SEP) czyta pkt 2 tak, że **cała instalacja, łącznie z obwodami rozdzielczymi, ma być TN-S lub TN-C-S**. Jest to zaostrzenie względem PN-HD 60364, które dopuszcza PEN ≥ 10 mm² Cu (zob. R7-L04, konflikt ze standardem ZKP ENEA) |
| R7-B04 | Połączeniami wyrównawczymi obejmuje się: metalową instalację wodociągową; metalowe elementy kanalizacji; metalową instalację grzewczą; metalowe elementy instalacji gazowej; szybów dźwigowych; przewodów kominowych; **metalowe elementy wentylacji i klimatyzacji**; **metalowe obudowy urządzeń telekomunikacyjnych** | WT § 183 ust. 1a | jw. | TAK | W Domu LAMELA: rury metalowe (jeśli będą), kanały rekuperacji (jeśli metalowe), obudowa szafki teletechnicznej, zbrojenie, konstrukcja PV i wiata stalowa |
| R7-B05 | PWP odcina zasilanie wszystkich obwodów z wyjątkiem niezbędnych podczas pożaru. **Wymagany w strefach pożarowych o kubaturze > 1000 m³** lub zawierających strefy zagrożone wybuchem. Umieszcza się go przy głównym wejściu lub złączu i oznakowuje. Jego zadziałanie nie może załączać drugiego źródła, z wyjątkiem źródła oświetlenia awaryjnego | WT § 183 ust. 2–4 | jw. | TAK | Konflikt z ROPoż § 4 ust. 2 pkt 2 (R7-M01). Kubaturę strefy (cały budynek z garażem, bo § 226 i brak oddzieleń ppoż.) liczy R3 lub model |
| R7-B06 | Jako uziomy **należy wykorzystywać** metalowe konstrukcje, **zbrojenie fundamentów** lub elementy metalowe w fundamentach niezbrojonych (sztuczny uziom fundamentowy). Wodociąg jako uziom tylko za zgodą eksploatatora. LPS wykonuje się wg PN dotyczących ochrony odgromowej | WT § 184 ust. 1–3 | jw. | TAK | Przy izolowanym fundamencie zob. R7-G02 |
| R7-B07 | Urządzenia pomiarowe w miejscu łatwo dostępnym, zabezpieczone przed uszkodzeniem i ingerencją | WT § 185 ust. 1 | jw. | TAK | ZKP w linii ogrodzenia (R7-L03) |
| R7-B08 | Instalacje i urządzenia prowadzi się bezkolizyjnie z innymi instalacjami. Ust. 2 (ciągi w szybach) dotyczy tylko budynków wielorodzinnych, ZL i UP | WT § 186 ust. 1–2 | jw. | TAK | — |
| R7-B09 | Przewody wymienialne bez naruszania konstrukcji. Przewody wtynkowe pod warstwą tynku **≥ 5 mm**. Ust. 3–7 (zespoły kablowe dla urządzeń ppoż., klasa PH) — w domu nie ma urządzeń ppoż. wymagających podtrzymania, więc nie dotyczy | WT § 187 ust. 1–2 (ust. 3–7) | jw. | TAK | W stropach monolitycznych przewody prowadzić w rurach osłonowych (wymienialność) |
| R7-B10 | W instalacji mieszkania wydziela się obwody: **oświetlenia; gniazd ogólnego przeznaczenia; gniazd w łazience; gniazd kuchennych; odbiorników wymagających indywidualnego zabezpieczenia** | WT § 188 ust. 2 | jw. | TAK | „Mieszkanie” wg § 3 pkt 9 WT obejmuje także lokal w domu jednorodzinnym (R3 IE-08) |
| R7-B11 | W pomieszczeniach wypusty oświetleniowe i niezbędna liczba gniazd. **Oświetlenie w pokojach załączane łącznikami wieloobwodowymi** | WT § 189 ust. 1–2 | jw. | TAK | Każdy pokój: co najmniej 2 grupy świateł (łącznik świecznikowy lub 2 łączniki) |
| R7-B12 | Wejście do budynku ma **elektryczne oświetlenie zewnętrzne**. Wyłączenie dotyczy tylko zabudowy zagrodowej i rekreacyjnej. Oświetlenie dojść i dojazdów **nie jest wymagane** dla budynków jednorodzinnych | WT § 64; § 14 ust. 4 | jw. | TAK | — |
| R7-B13 | Garaż ma elektryczną instalację oświetleniową | WT § 102 pkt 3 | jw. | TAK | — |
| R7-B14 | Pomieszczenia techniczne mają instalacje i urządzenia elektryczne dostosowane do przeznaczenia, zgodnie z PN | WT § 98 ust. 2; zał. 1 lp. 3 | jw. | TAK | Pomieszczenie techniczne P0: RG, pompa ciepła lub zasobnik, szafka teletechniczna |
| R7-B15 | Metalową instalację wodociągową łączy się przed i za wodomierzem przewodem metalowym wg PN o uziemieniach | WT § 116 ust. 3; zał. 1 lp. 7 | jw. | TAK | Dotyczy tylko rur przewodzących. Przy PE/PEX nie dotyczy |
| R7-B16 | Zasilanie z dwóch niezależnych źródeł i oświetlenie awaryjne wymagane są tylko tam, gdzie zanik napięcia zagraża życiu. Oświetlenie ewakuacyjne dotyczy wyliczonych pomieszczeń i dróg. **Dom jednorodzinny nie jest w katalogu** | WT § 181 | jw. | TAK | Nie dotyczy |

### C. Ochrona przeciwporażeniowa, RCD

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-C01 | Ochrona uzupełniająca RCD o **I_Δn ≤ 30 mA** dla: gniazd AC **≤ 32 A** używanych przez osoby postronne (ogólnego przeznaczenia) oraz ruchomych urządzeń AC **≤ 32 A** używanych na zewnątrz | PN-HD 60364-4-41:2017-09, 411.3.3 (tekst IEC 60364-4-41:2005/AMD1:2017) | https://cdn.standards.iteh.ai/samples/22593/faab23b5c332418984d5b3c627cbd1b0/IEC-60364-4-41-2005-AMD1-2017.pdf | IEC | HD 2017 wprowadza IEC AMD1:2017. Modyfikacje wspólne CENELEC: **NIEZWERYFIKOWANE** |
| R7-C02 | **W lokalach przeznaczonych dla jednego gospodarstwa domowego obwody końcowe AC zasilające oprawy oświetleniowe chroni się RCD ≤ 30 mA** (TN i TT) | PN-HD 60364-4-41:2017-09, 411.3.4 | jw. | IEC | Nowość względem wydania 2009 powołanego w WT |
| R7-C03 | Maksymalne czasy wyłączenia (TN, 120 V < U₀ ≤ 230 V, AC): **0,4 s** dla obwodów końcowych ≤ 63 A z gniazdami oraz ≤ 32 A zasilających wyłącznie odbiorniki stałe | PN-HD 60364-4-41:2017, 411.3.2.2, tabl. 41.1 | jw. | IEC | 5 s dla obwodów rozdzielczych (411.3.2.3): nie było tego w przejrzanym fragmencie, **NIEZWERYFIKOWANE** |
| R7-C04 | WT nakazuje stosować RCD („uzupełniające podstawową ochronę przeciwporażeniową i ochronę przed powstaniem pożaru”) | WT § 183 ust. 1 pkt 3 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Obwody bez RCD (np. stały alarm, lodówka) trzeba uzasadnić w opisie. Zalecam, by nie było ich wcale |
| R7-C05 | Rodzaj RCD dobiera się do prądów różnicowych odbiornika. Typ AC jest niedopuszczalny w obwodach ładowania EV | PN-HD 60364-7-722:2019 (R7-J03); PN-HD 60364-5-53:2022-10 | https://www.elektro.info.pl/artykul/ochrona-przeciwporazeniowa/203812,stosowanie-wylacznikow-roznicowopradowych-w-instalacjach-ladowania-pojazdow-elektrycznych | NIE | Brzmienie zasady doboru typu w 5-53:2022 (pkt 531.3.x): **NIEZWERYFIKOWANE**. Projektowo: min. typ A, dla falowników i pomp ciepła typ F lub B wg DTR |

### D. Ochrona przed skutkami cieplnymi — AFDD

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-D01 | **Zaleca się** (nie wymaga) środki przeciw skutkom zwarć łukowych w obwodach końcowych: w pomieszczeniach sypialnych, w lokalizacjach BE2 (materiały palne), CA2 (palne materiały konstrukcyjne), CB2 (konstrukcje rozprzestrzeniające ogień) i z dobrami niezastąpionymi. AFDD wg EN 62606 montuje się na początku obwodu. W Polsce AFDD nie są obowiązkowe | PN-HD 60364-4-42:2011/A1:2015, 421.7 | https://electricalom.com/site/knowledgebase.php?action=displayarticle&id=11 | NIE | Źródło wtórne referuje BS 7671 421.1.7 (odpowiednik). IEC 60364-4-42:2024 przenosi te postanowienia do rozdz. 426, ale PN go jeszcze nie wprowadziła. Treść PN-HD: **NIEZWERYFIKOWANE** |

### E. Przewody, przetężenia, spadki napięcia, oznaczenia

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-E01 | Przy przekroju ≤ 10 mm² tylko żyły Cu. Powyżej 10 mm² dopuszcza się Al | WT § 183 ust. 1 pkt 9 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | — |
| R7-E02 | Minimalne przekroje w instalacjach stałych (tabl. 52.2): obwody siłowe i oświetleniowe **1,5 mm² Cu**; sygnalizacyjne i sterownicze **0,5 mm² Cu**; przewody gołe siłowe 10 mm² Cu | PN-HD 60364-5-52:2011, tabl. 52.2 | https://www.viessmann.edu.pl/wp-content/uploads/E6_2__RC_29_04_2021.pdf | NIE | Zgodne z IEC 60364-5-52:2009 |
| R7-E03 | Zalecany spadek napięcia od złącza do odbiornika: **3 % dla oświetlenia, 5 % dla pozostałych**. Wydanie **PN-IEC 60364-5-52:2002, powołane w zał. 1 WT lp. 41**, podawało **4 %** od złącza do końca dowolnego obwodu w budynkach nieprzemysłowych | PN-HD 60364-5-52:2011, zał. G (informacyjny); PN-IEC 60364-5-52:2002 | https://elektryka.edu.pl/dopuszczalny-spadek-napiecia/ | NIE (A. Wrzosek, 15.05.2026) | W treści norm: **NIEZWERYFIKOWANE**. Tryb WT (norma datowana 2002) daje ≤ 4 %, wiedza techniczna ≤ 3 %/5 %. Kryterium projektowe z R7-E04 spełnia oba |
| R7-E04 | N SEP-E-002: spadek **≤ 3 % od licznika do odbiornika** i **≤ 0,5 % między złączem a licznikiem** (wlz) | N SEP-E-002 | https://elektryka.edu.pl/dopuszczalny-spadek-napiecia/ | NIE | Tablica normy SEP: **NIEZWERYFIKOWANE**. W domu z licznikiem w ZKP kabel ZKP–RG leży za licznikiem, więc wchodzi w 3 %. Przyjmuję jako kryterium projektowe: ΔU(ZKP→odbiornik) ≤ 3 %, w tym kabel ZKP–RG ≤ 0,5 % |
| R7-E05 | Przewody od wlz do rozdzielnicy mieszkaniowej: obciążalność **≥ 50 A** (≈ 10 mm² Cu) | N SEP-E-002 (wg wtórnego opracowania szkoleniowego) | https://www.viessmann.edu.pl/wp-content/uploads/E6_2__RC_29_04_2021.pdf | NIE | Przypisanie do N SEP-E-002: **NIEZWERYFIKOWANE** |
| R7-E06 | Koordynacja przewód–zabezpieczenie przeciążeniowe: I_B ≤ I_n ≤ I_z oraz I₂ ≤ 1,45·I_z | PN-HD 60364-4-43:2024-04, 433.1 | — | — | Reguła powszechnie znana, ale jej brzmienia w wydaniu 2024 nie sprawdziłem: **NIEZWERYFIKOWANE** |
| R7-E07 | Barwy izolacji: L — brązowy, czarny, szary; N — niebieski; PE — zielono-żółty. Obwody 1-fazowe trzyżyłowe, gniazda ze stykiem ochronnym | PN-HD 308 S2:2007 (aktualna, PKN); PN-EN IEC 60445:2022-04 | https://www.muratorplus.pl/technika/instalacje-elektryczne/zasady-rozmieszczania-wypustow-oswietleniowych-i-gniazd-wtyczkowych-w-budynkach-mieszkalnych-aa-XnJ9-i1FL-Yhg6.html | NIE (status PKN) | — |
| R7-E08 | Rezystancje żył Cu w 20 °C (kl. 1/2), użyte do szacunków ΔU w części 3: 1,5 mm² 12,1; 2,5 — 7,41; 4 — 4,61; 6 — 3,08; 10 — 1,83; 16 — 1,15 Ω/km | IEC 60228 | — | — | **NIEZWERYFIKOWANE** (wartości z pamięci normatywnej). W PT przeliczyć programem z temperaturą roboczą, ok. +20 % przy 70 °C |

### F. Ochrona przed przepięciami (SPD)

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-F01 | W instalacjach stosuje się urządzenia ochrony przeciwprzepięciowej | WT § 183 ust. 1 pkt 10 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Obowiązek bezwarunkowy w trybie WT |
| R7-F02 | Ochronę przed przepięciami przejściowymi zapewnia się, gdy przepięcie zagraża: a) życiu ludzi, b) usługom publicznym lub dziedzictwu, c) działalności komercyjnej lub przemysłowej. W pozostałych przypadkach wykonuje się ocenę ryzyka wg 443.5, **a bez niej ochronę stosuje się obowiązkowo**. Wyjątek: pojedyncza jednostka mieszkalna, w której wartość chronionej instalacji jest < 5 × wartość SPD w złączu. Komitety krajowe mogą ten wyjątek zmienić | PN-HD 60364-4-443:2016-03, 443.4 (tekst IEC 60364-4-44:2007/AMD1:2015) | https://cdn.standards.iteh.ai/samples/19248/93bc85b1469144ebbfb684a1b8d7ddd9/IEC-60364-4-44-2007-AMD1-2015.pdf | IEC | Dla Domu LAMELA wyjątek nie ma zastosowania, bo wartość instalacji z PV, PC i EV znacznie przekracza 5 × wartość SPD |
| R7-F03 | **CRL = f_env / (L_P · N_g)**. f_env = 85·F (tereny wiejskie i podmiejskie) albo 850·F (miejskie). L_P = 2·L_PAL + L_PCL + 0,4·L_PAH + 0,2·L_PCH [km], suma długości ≤ 1 km. **CRL < 1000 oznacza, że SPD jest wymagany.** Współczynnik F dla mieszkań ustalają komitety krajowe (1–3). W Polsce odsyłacz krajowy zaleca **F = 2** | PN-HD 60364-4-443:2016, 443.5, tabl. 443.1 | jw.; https://rst.pl/wp-content/uploads/2018/10/Zeszyty_RST_2018-1_Dobor_SPD_wg_PN-HD-60364.pdf | IEC (wzór); NIE (F = 2 dla PL, RST 2018) | Dom LAMELA (przedmieścia): f_env = 170. Przy L_PCL = 0,1 km i N_g = 1,8 wychodzi CRL = 944; przy 0,3 km → 315. Wniosek: **SPD wymagany** |
| R7-F04 | Obiekt z LPS lub narażony na prądy piorunowe (np. zasilanie linią napowietrzną) ma w złączu lub RG **SPD typu 1**. Dla LPL III–IV wystarcza **I_imp = 12,5 kA na biegun**. SPD typu 2: **I_n ≥ 5 kA (8/20)** | PN-HD 60364-5-534 (obecnie w PN-HD 60364-5-53:2022-10) | https://rst.pl/wp-content/uploads/2018/10/Zeszyty_RST_2018-1_Dobor_SPD_wg_PN-HD-60364.pdf | NIE | Wartości wg RST (2018, dla 5-534:2016). Nie sprawdziłem, czy 5-53:2022 je zmieniła: **NIEZWERYFIKOWANE** |
| R7-F05 | Kategorie wytrzymałości udarowej 230/400 V: **IV — 6 kV** (złącze), **III — 4 kV** (rozdzielnice, oprzewodowanie, gniazda), **II — 2,5 kV** (odbiorniki), **I — 1,5 kV** (urządzenia specjalnie chronione) | PN-HD 60364-4-443 (tabl. 443.2) | https://sep.com.pl/opracowania/opracowania_ochr_odgrom_bud.pdf | NIE | Z tego wynika U_p SPD w RG ≤ 2,5 kV. Zalecam ≤ 1,5 kV (T1+2 z niskim U_p) |
| R7-F06 | PV: jeżeli 443 wymaga ochrony przed przepięciami, **stosuje się ją także po stronie DC PV**. Poza tym kryterium: SPD po stronie DC są potrzebne, gdy L ≥ L_crit, gdzie **L_crit = 115/N_g** dla PV na budynku (200/N_g dla PV poza budynkiem), a L to maksymalna długość trasy od falownika do przyłączy łańcuchów | IEC 60364-7-712:2017, 712.443.4.101, 712.443.5.101, tabl. 712.1 (PN-HD 60364-7-712:2016-05) | https://lsp.global/wp-content/uploads/2025/10/IEC-60364-7-712-2017-Part-7-712-Requirements-for-special-installations-or-locations-Solar-photovoltaic-PV-power-supply-systems.pdf | IEC | Przy N_g = 1,8: L_crit ≈ 64 m. W Domu LAMELA SPD DC są wymagane już z pierwszego kryterium |

### G. Uziemienia i połączenia wyrównawcze

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-G01 | Zbrojenie fundamentów wykorzystuje się jako uziom | WT § 184 ust. 1 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | — |
| R7-G02 | **Gdy fundament jest całkowicie izolowany termicznie materiałem nieprzewodzącym albo ma izolację przeciwwodną z folii > 0,5 mm, beton fundamentu nie nadaje się na uziom.** Zbrojenie wykorzystuje się wtedy do połączeń wyrównawczych, a uziemienie wykonuje się inaczej: dodatkowy uziom fundamentowy pod izolacją, uziom wokół budynku albo uziom fundamentowy w gruncie | PN-HD 60364-5-54:2011, zał. C.1–C.2 (informacyjny) | https://rst.pl/wp-content/uploads/Uziom-fundamentowy-projektowanie-i-budowa-zgodnie-z-Polskimi-Normami.pdf | IEC (treść zweryfikowana w tekście IEC 60364-5-54:2011) + NIE (RST 2021) | Płyta fundamentowa na XPS: **uziom otokowy w gruncie** pod pospółką lub wokół budynku (RST). **Koordynacja z R5** |
| R7-G03 | Uziom w betonie: otulina **≥ 5 cm**. Płaskownik układa się na sztorc i mocuje do zbrojenia co **≤ 2 m**. Połączenia przez spawanie egzotermiczne, złączki lub zaciski — nie wolno łączyć drutem wiązałkowym. Zamknięte pierścienie lub prostokąty o wymiarach **do 20 m**. Co najmniej jeden dostępny zacisk przyłączeniowy (do GSU, do pomiarów). Na zbrojenie spawane potrzebna zgoda konstruktora | PN-HD 60364-5-54:2011, zał. C.3.1–C.3.5; 542.2.8; 542.3.2 | jw. | IEC + NIE | — |
| R7-G04 | Minimalne wymiary uziomów (tabl. 54.1): **stal w betonie** — pręt okrągły Ø10 mm lub płaskownik 75 mm² przy grubości 3 mm; **stal ocynkowana ogniowo w gruncie** — płaskownik 90 mm², 3 mm, powłoka 500 g/m² (63 µm); drut okrągły poziomy Ø10 mm (350 g/m², 45 µm); pręt pionowy Ø16 mm (350 g/m², 45 µm). Stal pomiedziowana i miedź wg tej samej tablicy | PN-HD 60364-5-54:2011, tabl. 54.1 | jw. | IEC | Wg RST (2021) stali ocynkowanej w betonie się nie zaleca, a w gruncie stosować Cu, StCu lub StSt. Zmiany A1:2023 (IEC AMD1:2021) w tabl. 54.1: **NIEZWERYFIKOWANE** |
| R7-G05 | Przewód uziemiający **≥ 6 mm² Cu lub 50 mm² stali**. Przewodów Al nie stosuje się. Przy połączeniu z LPS zaleca się **≥ 16 mm² Cu lub 50 mm² Fe** | PN-HD 60364-5-54:2011, 542.3.1 z uwagą | jw. | IEC | — |
| R7-G06 | Przewody połączeń wyrównawczych ochronnych do GSU: **≥ połowa przekroju największego przewodu PE instalacji i ≥ 6 mm² Cu** (16 mm² Al, 50 mm² stali). Nie muszą przekraczać **25 mm² Cu** | PN-HD 60364-5-54:2011, 544.1 | jw. | IEC | — |
| R7-G07 | Przewód PE poza kablem lub osłoną wspólną: **≥ 2,5 mm² Cu**, gdy jest chroniony mechanicznie, **≥ 4 mm² Cu**, gdy nie jest | PN-HD 60364-5-54:2011, 543.1.3 | jw. | IEC | — |
| R7-G08 | Pręty zbrojenia użyte jako uziom lub przewód LPS: **≥ Ø10 mm**. Pręty łączy się zakładem ≥ 70 mm, spoina **≥ 50 mm**. Spawanie punktowe jest niedopuszczalne | PN-EN 62305-3 (tabl. 7; E.4.3.3) | https://rst.pl/wp-content/uploads/Uziom-fundamentowy-projektowanie-i-budowa-zgodnie-z-Polskimi-Normami.pdf | NIE | Wartości wg wydania 2011 (wycofane). Wydanie 2025: **NIEZWERYFIKOWANE** |

### H. Pomieszczenia z wanną lub natryskiem (7-701)

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-H01 | Aktualna jest **PN-HD 60364-7-701:2025-02** (wersja angielska, HD 60364-7-701:2024, +A11:2025). PN-HD 60364-7-701:2010 powołana w WT jest wycofana | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN | Treści wydania 2025 nie miałem (bazą jest IEC 60364-7-701:2019). Zmiany stref: **NIEZWERYFIKOWANE** |
| R7-H02 | **Wszystkie obwody** wprowadzone do pomieszczenia z wanną lub natryskiem objęte RCD **I_Δn ≤ 30 mA** | PN-HD 60364-7-701:2010 (i następne) | https://inzynierbudownictwa.pl/wymagania-stawiane-instalacji-elektrycznej-w-pomieszczeniach-kapielowych/ | NIE (E. Musiał) | — |
| R7-H03 | Stopień ochrony w strefach 1 i 2: **co najmniej IPX4**. Dotyczy to też obwodów SELV/PELV ≤ AC 25 V. W strefie 1 nie montuje się gniazd (z wyjątkiem SELV), łączników ani puszek | PN-HD 60364-7-701:2010 | jw. | NIE | IPX5 przy strumieniach wody, IPX7 w strefie 0 i dozwolone gniazda golarkowe w strefie 2: **NIEZWERYFIKOWANE** |
| R7-H04 | Geometria stref (wydanie 2010): strefa 0 — wnętrze wanny lub brodzika; **strefa 1 — nad strefą 0 do wysokości 2,25 m**; **strefa 2 — pas 0,6 m poza strefą 1**, do 2,25 m | PN-HD 60364-7-701:2010; IEC 60364-7-701 | https://www.electrical-installation.org/enwiki/Bathroom_electrical_installation | NIE | Wartości znam tylko ze streszczeń wyników wyszukiwania. Strony źródłowej nie pobrałem (HTTP 403), więc **NIEZWERYFIKOWANE**. Tak samo natrysk bez brodzika (promień strefy 1 od wylewki) i zmiany w IEC 2019 / HD 2024. W PT zweryfikować z PN-HD 60364-7-701:2025-02 |
| R7-H05 | Miejscowe połączenia wyrównawcze: nowsze wydania nie wymagają łączenia metalowej wanny, jeżeli instalacje wod-kan wykonano z tworzyw | PN-HD 60364-7-701:2010, 701.415.2 | https://inzynierbudownictwa.pl/wymagania-stawiane-instalacji-elektrycznej-w-pomieszczeniach-kapielowych/ | NIE | Warunki pominięcia: **NIEZWERYFIKOWANE** w treści |
| R7-H06 | Gniazda w łazience na osobnym obwodzie | WT § 188 ust. 2 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | — |

### I. Fotowoltaika (mikroinstalacja prosumencka)

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-I01 | Instalowanie urządzeń PV o mocy zainstalowanej elektrycznej **≤ 150 kW** oraz magazynów energii **≤ 30 kWh** nie wymaga pozwolenia na budowę ani zgłoszenia. **Dla PV > 6,5 kW** wymagane są: uzgodnienie projektu z rzeczoznawcą ds. zabezpieczeń ppoż., zawiadomienie PSP o zakończeniu instalowania i przekazanie „planu urządzenia fotowoltaicznego dla ekip ratowniczych”. **Art. 56 ust. 1a uchylono** | PB art. 29 ust. 4 pkt 3 lit. c (brzmienie z Dz.U. 2025 poz. 1847, w życie 7.01.2026); art. 56 ust. 1 | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Brief powołuje nieaktualny art. 56 ust. 1a (tak samo R1-34). Zmiany PB po t.j. (2026/605, 646, 1161) nie dotyczą tego przepisu, co sprawdziłem |
| R7-I02 | Mikroinstalacja to OZE o mocy zainstalowanej elektrycznej **≤ 50 kW**, przyłączona do sieci < 110 kV. **Moc zainstalowana PV to łączna moc znamionowa czynna modułów** z tabliczek | OZE art. 2 pkt 19, 19b lit. b | https://api.sejm.gov.pl/eli/acts/DU/2026/68/text.pdf | TAK | Próg 6,5 kW liczyć po mocy modułów (DC STC). Falownik ≤ 6,5 kW (R1-35) |
| R7-I03 | Jeżeli prosument jest już odbiorcą końcowym, a moc mikroinstalacji **nie przekracza mocy określonej w warunkach przyłączenia**, przyłączenie odbywa się **na podstawie zgłoszenia** po zainstalowaniu zabezpieczeń i licznika. **OSD przyłącza w 30 dni** i ponosi koszt układu zabezpieczającego i pomiarowo-rozliczeniowego. Zgłoszenie zawiera dane z ust. 8d5 i oświadczenie o tytule prawnym (ust. 8d6). **Za przyłączenie mikroinstalacji nie pobiera się opłaty.** Mocy magazynu nie wlicza się (8d12) | PE art. 7 ust. 8d4–8d7, 8d12; ust. 8 pkt 3 lit. b | https://api.sejm.gov.pl/eli/acts/DU/2026/43/text.pdf | TAK | Zmiana Dz.U. 2026 poz. 516 nie narusza ust. 8d4–8d7 (sprawdzone). Moc przyłączeniowa odbiorcy musi być ≥ mocy PV |
| R7-I04 | OSD może ograniczyć pracę lub odłączyć mikroinstalację **> 10 kW** przy zagrożeniu sieci | PE art. 7 ust. 8d10 | jw. | TAK | Przy PV ≤ 6,5 kW nie dotyczy |
| R7-I05 | Moduły wytwarzania typu A (w PL 0,8 kW – 200 kW) podlegają NC RfG (rozp. UE 2016/631). Przyłączenie wymaga certyfikatu zgodności falownika wg „Warunków i procedur wykorzystania certyfikatów” PTPiREE. **Wersja 1.3 obowiązuje od 1.11.2024**, etap I trwa do 31.12.2026. **Od 1.01.2027 wymagane są certyfikaty potwierdzające zgodność z NC RfG i Wymogami Ogólnego Stosowania** | Rozp. (UE) 2016/631; PTPiREE v1.3; RSys § 5 ust. 1 | https://ptpiree.pl/en/actions-network-codes/conditions-and-procedures/ | OSD | Falownik z listy certyfikatów PTPiREE. PN-EN 50549-1:2019-02 (+A1:2024) aktualna. Stan prac nad NC RfG 2.0 (wymogi grid-forming > 1 MW) nie dotyczy mikroinstalacji |
| R7-I06 | RCD w obwodzie AC falownika: **typ B** (IEC 62423), chyba że: falownik zapewnia co najmniej separację prostą AC/DC; albo instalacja zapewnia separację transformatorem; albo falownik spełnia IEC 62109-1, a producent nie wymaga typu B (wtedy typ wg DTR) | IEC 60364-7-712:2017, 712.530.3.101 (PN-HD 60364-7-712:2016-05) | https://lsp.global/wp-content/uploads/2025/10/IEC-60364-7-712-2017-Part-7-712-Requirements-for-special-installations-or-locations-Solar-photovoltaic-PV-power-supply-systems.pdf | IEC | — |
| R7-I07 | Uziemienie funkcjonalne generatora PV wykonuje się w jednym punkcie i łączy z GSU | IEC 60364-7-712:2017, 712.444.5.5.101 | jw. | IEC | Połączenie ram i konstrukcji PV z GSU: przekrój wg DTR i 5-54. Wartości 6/10 mm² z wyszukiwarki: **NIEZWERYFIKOWANE** |
| R7-I08 | Przewody DC PV według normy wyrobu PN-EN 50618:2015-03 (typ H1Z2Z2-K), aktualnej w PKN | PN-EN 50618:2015-03 | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN | Wymóg normy 7-712 co do typu przewodu: **NIEZWERYFIKOWANE** (dobra praktyka) |

### J. Ładowanie pojazdów elektrycznych

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-J01 | UEm art. 12: moc przyłączeniowa pod punkty ≥ 3,7 kW dotyczy **budynków UP i wielorodzinnych** w gminach z art. 60 ust. 1. Art. 12a: budynki niemieszkalne > 10 stanowisk (punkt + kanały 1/5) oraz **mieszkalne > 10 stanowisk** (kanały na wszystkich stanowiskach). **Dla domu jednorodzinnego brak obowiązku** | UEm art. 12, 12a (t.j. Dz.U. 2026 poz. 1243, stan na 26.08.2026) | https://api.sejm.gov.pl/eli/acts/DU/2026/1243/text.pdf | TAK | WT § 180 pkt 1 odsyła do UEm, więc też nie tworzy obowiązku |
| R7-J02 | **EPBD art. 14 ust. 4:** w nowych budynkach mieszkalnych z **więcej niż 3 miejscami parkingowymi** (wewnątrz lub fizycznie przylegającymi) państwa zapewniają okablowanie wstępne **≥ 50 % miejsc**, kanały dla pozostałych, **≥ 1 punkt ładowania** i ≥ 2 miejsca dla rowerów na moduł mieszkalny. Okablowanie ma pozwalać na jednoczesne ładowanie na wszystkich miejscach. **Termin transpozycji: 29.05.2026** (art. 35) | Dyrektywa (UE) 2024/1275 art. 14 ust. 4, 6; art. 35 ust. 1 | https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=OJ:L_202401275 | TAK | Transpozycji art. 14 nie ma w UEm (t.j. 2026/1243) ani w innych aktach (ELI, 25.09.2026). **Przepis nie wiąże wprost. Rekomendacja: spełnić dobrowolnie**, jeżeli PZT przewiduje > 3 miejsca (2 w garażu + 2 na podjeździe) |
| R7-J03 | Każdy punkt przyłączenia EV ma **osobny obwód** i **indywidualny RCD ≤ 30 mA**. Typ co najmniej A. Przy gniazdach i złączach IEC 62196: **typ B albo typ A lub F z RDC-DD 6 mA DC**. **Typ AC niedopuszczalny. Układ TN-C niedopuszczalny** | PN-HD 60364-7-722:2019-01 | https://www.elektro.info.pl/artykul/ochrona-przeciwporazeniowa/203812,stosowanie-wylacznikow-roznicowopradowych-w-instalacjach-ladowania-pojazdow-elektrycznych | NIE (S. Czapp, 2024) | Numery punktów (722.531.3.101 itd.): **NIEZWERYFIKOWANE** |
| R7-J04 | Wymagania dla stacji ładowania (wyrób): PN-EN IEC 61851-1:2019-10 (+AC:2024), aktualna | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN | — |

### K. Ochrona odgromowa (LPS)

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-K01 | Budynek wyposaża się w instalację piorunochronną. Obowiązek dotyczy budynków **„wyszczególnionych w Polskiej Normie dotyczącej ochrony odgromowej”**, a instalację wykonuje się wg PN | WT § 53 ust. 2; § 184 ust. 3; zał. 1 lp. 1, 44 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | PN-EN 62305 nie zawiera listy budynków, więc o potrzebie LPS decyduje ocena ryzyka (62305-2). Zgodne z R3 B-02 |
| R7-K02 | Ocena ryzyka: R1 (utrata życia) porównuje się z ryzykiem tolerowanym **R_T = 10⁻⁵ /rok**. Klasy ryzyka pożaru wg obciążenia ogniowego: **niskie < 400 MJ/m², zwykłe 400–800 MJ/m², wysokie > 800 MJ/m²** | PN-EN 62305-2:2008 (w wydaniu 2012 identycznie) | http://archiwum.geopoz.pl/bip/RAPORT-D_instalacja%20odgromowac9fe.pdf?t=210&id=4183 | NIE (raport analizy ryzyka dla budynku w Poznaniu, DEHN Risk Tool) | Wartości w PN-EN IEC 62305-2:2025: **NIEZWERYFIKOWANE** |
| R7-K03 | Gęstość wyładowań w Polsce wg danych PN-86/E-05003/01: **N_g = 1,8 wył./km²/rok na północ od 51°30'** (w tym Poznań, ≈ 18 dni burzowych) i **2,5** na pozostałym terenie. N_g = 0,1·T_d | SEP (A. Boczkowski, 2013); raport geopoz (N_g = 1,8 dla Poznania) | https://sep.com.pl/opracowania/opracowania_ochr_odgrom_bud.pdf | NIE | Nowsze dane z sieci detekcji (PIORUN) mogą dawać inne N_g: **NIEZWERYFIKOWANE** |
| R7-K04 | Propozycja Polskiego Komitetu Ochrony Odgromowej SEP: domy jednorodzinne → LPS klasy **III–IV** (tablica 18) | SEP (Boczkowski 2013), tabl. 18 | https://sep.com.pl/opracowania/opracowania_ochr_odgrom_bud.pdf | NIE | **Propozycja środowiskowa, nie przepis** |
| R7-K05 | Wstępny szacunek R1 dla Domu LAMELA (moje obliczenie, **NIEZWERYFIKOWANE współczynniki**). Założenia: obrys 19 × 11 m, H = 10,5 m, C_D = 1, N_g = 1,8, linia nN kablowa 1 km, C_I = 0,5, C_E = 0,5, L_T = r_t = 10⁻², L_F = 10⁻², r_p = h_z = 1. Wyniki: A_D ≈ 5216 m², N_D ≈ 0,0094/rok, N_L ≈ 0,018/rok. **Przy „zwykłym” ryzyku pożaru (r_f = 10⁻²) R1 ≈ 5,5·10⁻⁶ < R_T, przy „wysokim” (r_f = 10⁻¹) R1 ≈ 3,0·10⁻⁵ > R_T** | Metodyka PN-EN 62305-2:2012 (zał. A–C) | — | — | Współczynniki przyjęte z wiedzy ogólnej, bez dostępu do norm: **NIEZWERYFIKOWANE**. Rozstrzygające jest obciążenie ogniowe: czy dom to „zwykłe” czy „wysokie” ryzyko. **Pełna analiza w PT** (oprogramowanie, PN-EN IEC 62305-2:2025) |

### L. Przyłącze nN, złącze, pomiar

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-L01 | OSD musi zawrzeć umowę o przyłączenie, jeżeli istnieją warunki techniczne i ekonomiczne. **Opłata za przyłączenie do sieci ≤ 1 kV: według stawek taryfowych** (kalkulowanych z 1/4 średniorocznych nakładów). **Warunki przyłączenia dla grupy V (≤ 1 kV): w 21 dni.** Warunki są ważne 2 lata | PE art. 7 ust. 1, ust. 8 pkt 2, ust. 8g pkt 1, ust. 8i | https://api.sejm.gov.pl/eli/acts/DU/2026/43/text.pdf | TAK | Zmiany 2026/516 (zaliczki, system informatyczny) dotyczą sieci > 1 kV. Przy nN nie zmieniają ust. 8g pkt 1 (sprawdzone) |
| R7-L02 | **Grupa przyłączeniowa V: ≤ 1 kV i moc przyłączeniowa ≤ 40 kW.** Grupa IV: > 40 kW | RSys § 3 ust. 1 pkt 4–5 | https://api.sejm.gov.pl/eli/acts/DU/2025/919/text.pdf | TAK | Zmiana Dz.U. 2026 poz. 668 dotyczy bilansowania i danych, nie grup (sprawdzone) |
| R7-L03 | Warunki przyłączenia określają m.in.: moc przyłączeniową; miejsce przyłączenia i rozgraniczenia własności; miejsce układu pomiarowego; rodzaj i dane zabezpieczenia głównego; prądy zwarciowe; **dane do doboru ochrony przeciwporażeniowej** (pkt 17). Wniosek zawiera m.in. moc przyłączeniową, termin i **schemat jednokreskowy** instalacji | RSys § 4 ust. 2 pkt 1–17; § 6 ust. 1 pkt 1–7 | jw. | TAK | Układ sieci (TN-C) i wymagania co do rozdziału PEN potwierdzić w warunkach |
| R7-L04 | Parametry napięcia dla grup III–V: 95 % 10-minutowych wartości w tygodniu w przedziale **±10 % U_n**; częstotliwość **50 Hz ±1 %** przez 99,5 % tygodnia (+4 %/−6 % przez 100 %); P_lt ≤ 1 | RSys § 45 ust. 5 | jw. | TAK | Uzupełnia PN-EN 50160:2023-10 |
| R7-L05 | **Budownictwo jednorodzinne: układ pomiarowo-rozliczeniowy na zewnątrz budynku, w linii ogrodzenia na terenie nieruchomości** albo w pasie przynależnym do ogólnodostępnego ciągu komunikacyjnego (przyłącza kablowe). Pomiar **bezpośredni do 40 kW** (zabezpieczenie przedlicznikowe ≤ 63 A). Pole odczytowe licznika w złączu wolnostojącym **≥ 48 cm** nad terenem, w innych przypadkach 80–180 cm | Standard ENEA Operator „Układy pomiarowe energii elektrycznej” (od 02.04.2024), pkt 7 tab. 1, pkt 8.1 | https://www.operator.enea.pl/media/698/uklady-pomiarowe-energii-elektrycznej-obowiazuje-od-02042024pdf.pdf | OSD | Zgodne z briefem (ZKP w linii ogrodzenia) |
| R7-L06 | ZKP typu **ZK1x-1P**. Przedział złączowy: rozłącznik bezpiecznikowy wielkości 00, **szyna PEN** z możliwością pomiaru uziemienia cęgami. Przedział pomiarowy: **zabezpieczenie przedlicznikowe — wyłącznik nadprądowy o charakterystyce C** (moduły 1-fazowe), **rozłącznik ≥ 63 A (6 kA)**, **listwa na kabel odbiorcy do 4×35 mm²**, przewód PEN prowadzony do listwy, połączenia H07V-K 10 mm². Na kabel odbiorcy **rura osłonowa 50 mm**, ok. 150 cm | Standard ENEA „Szafy kablowe oraz złącza kablowe nn z układem pomiarowo-rozliczeniowym” (od 01.02.2024), pkt 8.1 | https://www.operator.enea.pl/media/693/szafy-kablowe-oraz-zlacza-kablowe-nn-z-ukladem-pomiarowo-rozliczeniowym-energii | OSD | **Konflikt:** standard przewiduje wyjście z ZKP w układzie TN-C (4 żyły z PEN), a WT § 183 ust. 1 pkt 2 wymaga PE i N w obwodach rozdzielczych. Zob. „Nierozstrzygnięte” pkt 3 |
| R7-L07 | Kable nN w ziemi na głębokości (do wierzchu kabla) **≥ 70 cm** (poza użytkami rolnymi i leśnymi) albo **≥ 100 cm** (na tych użytkach). Kabel w piasku lub gruncie drobnoziarnistym, oznaczniki co ≤ 5 m, **niebieska taśma ostrzegawcza**, rury osłonowe przy płytszym ułożeniu i skrzyżowaniach (N SEP-E-004:2004) | Standard ENEA „Elektroenergetyczne linie kablowe niskiego napięcia” (od 01.10.2025), pkt 5.4.2–5.4.5, tabl. 5.3 | https://www.operator.enea.pl/media/2710/elektroenergetyczne-linie-kablowe-niskiego-napiecia-obowiazuje-od-01102025pdf.pdf | OSD | Standard dotyczy sieci OSD. Dla kabla ZKP–RG stosować analogicznie (dobra praktyka) |
| R7-L08 | Moc zapotrzebowana: **30 kVA** dla mieszkania lub budynku jednorodzinnego bez ciepłej wody z sieci zewnętrznej, 12,5 kVA z taką wodą, 7 kVA w wariancie zubożonym. **Elektryczne ogrzewanie pomieszczeń dolicza się oddzielnie** | N SEP-E-002 (wg SEP, A. Boczkowski 2013) | https://sep.com.pl/opracowania/opracowania_zasady_wyzn_mocy_zapotrzeb_dla_mieszkan.pdf | NIE (SEP) | Wartość planistyczna, niewiążąca. W Domu LAMELA zastąpić bilansem mocy (część 3.1) |
| R7-L09 | Moc a prąd zabezpieczenia 3-f (U = 400 V, cos φ = 1, P = √3·U·I): 16 A → 11,1 kW; 20 A → 13,9 kW; 25 A → 17,3 kW; **32 A → 22,2 kW; 40 A → 27,7 kW**; 50 A → 34,6 kW; 63 A → 43,6 kW | Obliczenie własne | — | — | Tabela OSD „moc przyłączeniowa ↔ zabezpieczenie przedlicznikowe” dla ENEA: **NIEZWERYFIKOWANE** (w wynikach wyszukiwania pojawiły się sprzeczne wartości). Potwierdzić w warunkach przyłączenia |

### M. Ochrona przeciwpożarowa związana z instalacją elektryczną

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-M01 | Właściciele budynków **z wyjątkiem budynków mieszkalnych jednorodzinnych** „wyposażają obiekty w przeciwpożarowe wyłączniki prądu zgodnie z przepisami techniczno-budowlanymi” | ROPoż § 4 ust. 2 pkt 2 (t.j. Dz.U. 2023 poz. 822) | https://api.sejm.gov.pl/eli/acts/DU/2023/822/text.pdf | TAK | Źródła wtórne (elektro.info, portale ppoż.) wywodzą stąd, że **dom jednorodzinny jest zwolniony z PWP niezależnie od kubatury**. WT § 183 ust. 2 wyjątku nie zawiera. **Konflikt → „Nierozstrzygnięte” pkt 2** |
| R7-M02 | **Lokal mieszkalny wyposaża się w co najmniej jedną autonomiczną czujkę dymu** zgodną z PN dotyczącą czujek autonomicznych (PN-EN 14604:2006, aktualna). Nie dotyczy lokalu chronionego SSP lub stałym urządzeniem gaśniczym. **Czujkę tlenku węgla** (PN-EN 50291-1:2018-06) montuje się w pomieszczeniu lokalu, w którym spala się paliwo stałe, ciekłe lub gazowe, z wyjątkiem urządzeń z zamkniętą komorą spalania i kuchenek gazowych. Nowe lokale od 23.12.2024, istniejące do 1.01.2030 | ROPoż § 28a ust. 1–4 (dodany Dz.U. 2024 poz. 1716, § 1 pkt 4; § 2 ust. 2–3; § 3) | https://api.sejm.gov.pl/eli/acts/DU/2024/1716/text.pdf | TAK | Dom all-electric bez kominka: tylko czujki dymu. Kominek (np. na etapie koncepcji) oznacza też czujkę CO |
| R7-M03 | Budynki mieszkalne jednorodzinne do 3 kondygnacji nadziemnych są wyłączone z wymagań § 212 (klasa odporności pożarowej) i § 216. **Strefę pożarową tworzy budynek** lub jego część oddzielona elementami oddzielenia ppoż. | WT § 213 pkt 1 lit. a; § 226 ust. 1 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Garaż bez oddzielenia leży w tej samej strefie. Kubaturę do § 183 ust. 2 liczyć dla całego budynku |

### N. Instalacja telekomunikacyjna

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-N01 | Instalację telekomunikacyjną (§ 56), możliwość przyłączenia do sieci telekomunikacyjnej (§ 26 ust. 1), sygnalizację dzwonkową (§ 192a) oraz zakres, punkt styku i parametry światłowodu (§ 192b–§ 192f) WT przewiduje dla budynków **wielorodzinnych, zamieszkania zbiorowego i UP**. **Nie dotyczy domu jednorodzinnego** | WT § 26 ust. 1, § 56, § 192a–§ 192f | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK | Zgodne z R3 B-03 |
| R7-N02 | **Wszystkie nowe budynki**, dla których **wniosek o pozwolenie na budowę złożono po 12.02.2026**, muszą mieć **wewnątrzbudynkową infrastrukturę techniczną przystosowaną do technologii światłowodowej** oraz **wewnątrzbudynkowe okablowanie światłowodowe do punktu fizycznego, w którym użytkownik końcowy podłącza się do sieci publicznej** (punkt zakończenia sieci). Punkt dostępu (ust. 2) wymagany jest tylko w budynkach wielorodzinnych. Państwa określają kategorie budynków zwolnionych (ust. 7–8) i normy techniczne (ust. 4, termin 12.11.2025). Art. 10 ust. 1–3 stosuje się od 12.02.2026 | Rozp. (UE) 2024/1309 (GIA) art. 10 ust. 1–8; art. 19 ust. 3 lit. c | https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=OJ:L_202401309 | TAK | Rozporządzenie UE stosuje się bezpośrednio. W ELI (25.09.2026) nie znalazłem polskiego aktu wykonawczego ani kategorii wyłączeń: t.j. megaustawy Dz.U. 2026 poz. 562 go nie zawiera, a zmiana 2026/815 dotyczy zarządzania kryzysowego. Zatem **obowiązek dotyczy Domu LAMELA**. Źródło wtórne (Murator, 23.09.2025) opisuje projekt MC: infrastruktura w domach jednorodzinnych plus przyłącze do granicy działki |
| R7-N03 | Definicje: „wewnątrzbudynkowa infrastruktura techniczna” łączy punkt dostępu budynku z punktem zakończenia sieci; „wewnątrzbudynkowe okablowanie światłowodowe” to kable światłowodowe w obiekcie użytkownika łączące punkt dostępu z punktem zakończenia sieci; „punkt dostępu” to punkt fizyczny wewnątrz lub na zewnątrz budynku, dostępny dla operatorów | GIA art. 2 pkt 6–8, 11 | jw. | TAK | — |
| R7-N04 | Parametry odniesienia (WT dla wielorodzinnych, jako dobra praktyka): **≥ 2 włókna jednomodowe**, złącza **SC/APC**, tłumienie toru **≤ 1,2 dB** (1310 i 1550 nm), włókna o tłumienności ≤ 0,4 dB/km (1310–1625 nm) i ≤ 0,25 dB/km (1550 nm). Normy okablowania: PN-EN 50174-2:2018-08, **PN-EN 50173-4:2018-07 (+A1:2024)** dla zabudowy mieszkalnej, PN-EN 50310:2016-09 (+A1:2020) dla połączeń wyrównawczych | WT § 192f ust. 5; PKN | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK (WT); PKN | Polskie normy lub specyfikacje z GIA art. 10 ust. 4: **NIEZWERYFIKOWANE** (nie znalazłem) |
| R7-N05 | Metalowe obudowy urządzeń telekomunikacyjnych obejmuje się połączeniami wyrównawczymi. Dobra praktyka z § 192f ust. 3: SPD w instalacji telekomunikacyjnej; elementy ponad dachem w strefie ochronnej LPS albo bezpośrednio uziemione | WT § 183 ust. 1a pkt 8; § 192f ust. 3 | jw. | TAK | § 192f dotyczy formalnie budynków z § 56 |

### O. Planowanie instalacji w lokalu i sprawdzenia

| ID | Wymaganie / reguła | Podstawa | URL | pierw. | Uwagi |
|---|---|---|---|---|---|
| R7-O01 | Minimalna liczba wypustów oświetleniowych: **1 w pokoju do 20 m², 2 w większym**. W kuchni dodatkowo oświetlenie nad blatem, w łazience wypusty przy lustrze. Gniazda **podwójne zamiast pojedynczych**, rozmieszczone tak, by nie trzeba było przedłużaczy | N SEP-E-002, tabl. 1–2 (wg J. Strzyżewski, Muratorplus 21.02.2024) | https://www.muratorplus.pl/technika/instalacje-elektryczne/zasady-rozmieszczania-wypustow-oswietleniowych-i-gniazd-wtyczkowych-w-budynkach-mieszkalnych-aa-XnJ9-i1FL-Yhg6.html | NIE | Tablica minimalnej liczby gniazd (grafika) i strefy instalacyjne: **NIEZWERYFIKOWANE** |
| R7-O02 | Przed oddaniem instalację sprawdza się (oględziny, próby, pomiary): ciągłość PE, rezystancję izolacji, samoczynne wyłączenie (impedancja pętli Z_s), RCD, biegunowość, kolejność faz, spadek napięcia | PN-HD 60364-6:2016-07 | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | PKN (status) | Zakres pomiarów: **NIEZWERYFIKOWANE** w treści. Na tym etapie tylko przegląd |
| R7-O03 | Do zawiadomienia o zakończeniu budowy dołącza się **protokoły badań i sprawdzeń przyłączy i instalacji**, sporządzone przez osoby z uprawnieniami budowlanymi w odpowiedniej specjalności lub osoby z art. 62 ust. 6 | PB art. 57 ust. 1 pkt 4 lit. a | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Projektant PT elektrycznego: uprawnienia w specjalności instalacyjnej, zakres elektryczny i elektroenergetyczny (R1-31) |

---

## 3. Implikacje dla projektu Dom LAMELA

Zasady gotowe do przeniesienia do PT branży elektrycznej. Wartości oznaczone „założenie” to propozycje projektowe, nie wymogi.
Wymiary budynku biorę z briefu. Ostateczne wartości (długości tras, kubatura, moc) muszą pochodzić z `model/budynek.yaml`.

### 3.1 Przyłącze, ZKP, moc przyłączeniowa

1. **Wniosek do ENEA Operator.** Wnioskodawca jest w grupie V (≤ 40 kW) [R7-L02]. Do wniosku dołączyć:
   * moc przyłączeniową;
   * termin;
   * schemat jednokreskowy [R7-L03];
   * informację o planowanej mikroinstalacji PV ≤ 6,5 kW.
   OSD wydaje warunki w 21 dni [R7-L01].
2. **Moc przyłączeniowa — propozycja: 27 kW (zabezpieczenie przedlicznikowe 40 A, 3f)** [R7-L09].
   * Wariant minimalny: 22 kW / 32 A. Wymaga dynamicznego zarządzania mocą ładowarki EV i blokady grzałek pompy ciepła.
   * Szacunek bilansu (do potwierdzenia w PT):

     | Pozycja | Moc |
     |---|---|
     | oświetlenie LED | ≈ 2 kW |
     | gniazda ogólne | ≈ 8 kW |
     | płyta indukcyjna | 7,4 kW |
     | piekarnik i mikrofalówka | ≈ 4,5 kW |
     | zmywarka, pralka, suszarka | ≈ 5,4 kW |
     | pompa ciepła (sprężarka) | ≈ 4 kW |
     | grzałka rezerwowa i CWU | ≈ 6 kW |
     | rekuperator | ≈ 0,3 kW |
     | EV | 11 kW |
     | inne | ≈ 1,5 kW |
     | **Moc zainstalowana** | **≈ 50 kW** |

   * Moc szczytowa przy współczynnikach jednoczesności 0,3–1,0: ≈ 29 kW bez zarządzania mocą, ≈ 22 kW z zarządzaniem.
   * N SEP-E-002 zaleca 30 kVA plus ogrzewanie elektryczne liczone oddzielnie [R7-L08].
   * Warunek PV: moc PV ≤ moc przyłączeniowa, co pozwala przyłączyć mikroinstalację na zgłoszenie [R7-I03].
3. **ZKP typu ZK1x-1P w linii ogrodzenia od ul. Lipowej** [R7-L05, R7-L06]:
   * na terenie działki, wnęka w ogrodzeniu, dostęp od strony drogi;
   * pole odczytowe licznika ≥ 48 cm nad terenem;
   * pozycja w PZT: przy bramie i furtce. MPZP: ogrodzenie ażurowe ≤ 1,60 m, bez prefabrykatów betonowych, więc ZKP wbudować w murek lub słupek.

   Zabezpieczenie przedlicznikowe to wyłącznik C wg standardu OSD. W RG jako wyłącznik główny zastosować **rozłącznik izolacyjny 3P 63 A** zamiast wyłącznika nadprądowego, aby zachować selektywność [WT § 183 ust. 1 pkt 5].
4. **WLZ (ZKP → RG)** — założenie: **YKY 5×16 mm² Cu** w ziemi na głębokości ≥ 0,7 m, w piasku, z niebieską taśmą ostrzegawczą, w rurze przy wejściu do budynku i pod utwardzeniami [R7-L07].
   * Przekrój dobrano na spadek napięcia: 40 A, L = 25 m daje ΔU ≈ 0,50 % (20 °C) [R7-E04, R7-E08]. Przy 5×10 mm² wyszłoby ≈ 0,79 %.
   * Obciążalność jest wystarczająca z zapasem dla I_n ≤ 40 A [R7-E05, obciążalność ≥ 50 A].
   * Rozdział PEN: preferowany w ZKP, a WLZ 5-żyłowy (litera WT § 183 ust. 1 pkt 2) — **wymaga zgody OSD**. Jeżeli OSD nie wyrazi zgody: YKY 4×16 (PEN ≥ 10 mm² Cu wg 5-54) i rozdział w RG z uziemieniem na GSU. Zob. „Nierozstrzygnięte” pkt 3.
5. **Rurowanie rezerwowe od ZKP do budynku:** rura na kabel sterowania bramy, wideodomofonu i furtki oraz osobna mikrokanalizacja telekomunikacyjna (pkt 3.10).

### 3.2 Rozdzielnica główna RG (pomieszczenie techniczne P0)

1. **Lokalizacja RG:** pomieszczenie techniczne P0 [R7-B14], blisko środka obciążenia (kuchnia, pralnia na P1). Na P1/P2 opcjonalnie podrozdzielnica RP2, np. przy pionie instalacyjnym na P2 — decyzja w PT.
   * Obudowa wg PN-EN IEC 61439-3:2025-09 [R7-A06].
   * Rezerwa min. 20 % modułów (założenie).
2. **Aparatura na wejściu RG:**
   * aparat główny z możliwością zdalnego wyłączenia przyciskiem PWP (pkt 3.9). Do wyboru w PT:
     * rozłącznik 3P ≥ 63 A z napędem lub wyzwalaczem;
     * wyłącznik z wyzwalaczem wzrostowym, selektywny względem zabezpieczenia przedlicznikowego C (selektywność sprawdzić tabelami producenta);
   * **SPD typu 1+2** (T1: I_imp ≥ 12,5 kA na biegun; U_p ≤ 1,5 kV, wymagane ≤ 2,5 kV) [R7-F01…F05], w układzie zgodnym z punktem rozdziału PEN;
   * zabezpieczenie SPD wg DTR;
   * rozłącznik lub bezpieczniki dla obwodu falownika;
   * listwy PE i N, połączenie z GSU.
3. **RCD** [R7-C01, C02, C04; R7-H02]:
   * wszystkie obwody gniazd ≤ 32 A: I_Δn = 30 mA;
   * wszystkie obwody oświetleniowe: 30 mA;
   * wszystkie obwody łazienek: 30 mA;
   * obwody odbiorników stałych: 30 mA (preferowane) albo uzasadnione w opisie;
   * **Preferowane RCBO 1P+N (typ A, 30 mA) dla każdego obwodu gniazd, oświetlenia i łazienek.** Zapewnia selektywność: awaria jednego obwodu nie wyłącza innych [WT § 183 ust. 1 pkt 5]. Alternatywa: RCCB 4P 40 A/30 mA typu A dla grup ≤ 4–5 obwodów;
   * **nie stosować typu AC** [R7-C05];
   * pompa ciepła i falownik: typ wg DTR [R7-I06]. Typ B, gdy falownik nie ma separacji i producent tego wymaga;
   * EV: RCD własny, typ B albo A + RDC-DD 6 mA [R7-J03].
4. **Zabezpieczenia nadprądowe (założenia):**
   * oświetlenie B10;
   * gniazda B16;
   * odbiorniki 3f wg DTR (C dla sprężarek).

   Warunek I_B ≤ I_n ≤ I_z [R7-E06] i czas wyłączenia 0,4 s przy Z_s [R7-C03] sprawdzić obliczeniowo w PT.

### 3.3 Obwody — lista wyjściowa (do PT)

Przekroje Cu [R7-E01, R7-E02]. Przewody YDYp lub YDY 450/750 V w tynku (≥ 5 mm tynku) albo w rurach w stropach [R7-B09]. Na zewnątrz i w ziemi YKY. Typy przewodów to założenie.

| Obw. | Przeznaczenie | Przekrój | Zabezp. | RCD | Podstawa / uwagi |
|---|---|---|---|---|---|
| L1 | Oświetlenie P0 strefa dzienna (salon, jadalnia, kuchnia — kilka grup) | 3×1,5 | B10 | 30 mA A | § 188 ust. 2; § 189 ust. 2 (łączniki wieloobwodowe); 411.3.4 |
| L2 | Oświetlenie P0: wiatrołap, hol, schody, WC, pokój gościnny i łazienka P0 (w łazience IPX4 w strefach) | 3×1,5 | B10 | 30 mA | jw.; 7-701 |
| L3 | Oświetlenie P1 | 3×1,5 | B10 | 30 mA | jw. |
| L4 | Oświetlenie P2 | 3×1,5 | B10 | 30 mA | jw. |
| L5 | Oświetlenie zewnętrzne: wejście, elewacja, taras, ogród (IP44+) | 3×1,5 / YKY 3×1,5 | B10 | 30 mA | **§ 64 (wejście — obowiązkowe)**; 7-714 |
| L6 | Oświetlenie garażu i pomieszczenia technicznego | 3×1,5 | B10 | 30 mA | **§ 102 pkt 3** |
| G1–G2 | Gniazda P0: salon, jadalnia | 3×2,5 | B16 | 30 mA | § 188 ust. 2; 411.3.3 |
| G3–G4 | **Gniazda kuchenne**: blat, 2 obwody; wyspa (gniazda w wyspie) | 3×2,5 | B16 | 30 mA | **§ 188 ust. 2 (kuchnia)** |
| G5 | Gniazda P0: pokój gościnny i gabinet | 3×2,5 | B16 | 30 mA | — |
| G6 | **Gniazda łazienki P0 i WC** (poza strefami 0–2) | 3×2,5 | B16 | 30 mA | **§ 188 ust. 2 (łazienka)**; 7-701 |
| G7–G8 | Gniazda P1: pokoje dzieci; pokój rodzinny i hol | 3×2,5 | B16 | 30 mA | — |
| G9 | **Gniazda łazienki P1** | 3×2,5 | B16 | 30 mA | § 188 ust. 2 |
| G10–G11 | Gniazda P2: sypialnia, garderoba; gabinet | 3×2,5 | B16 | 30 mA (opcjonalnie AFDD w sypialniach) | 4-42 A1: zalecenie [R7-D01] |
| G12 | **Gniazda łazienki P2** | 3×2,5 | B16 | 30 mA | § 188 ust. 2 |
| G13 | Gniazda garażu (IP44) | 3×2,5 | B16 | 30 mA | — |
| G14 | Gniazda zewnętrzne: taras, ogród (IP44/IP54, z klapką) | YKY 3×2,5 | B16 | 30 mA | 411.3.3 (urządzenia ruchome na zewnątrz) |
| G15 | Gniazda pomieszczenia technicznego i szafki teletechnicznej | 3×2,5 | B16 | 30 mA | — |
| D1 | Płyta indukcyjna (3f lub 2f wg DTR) | 5×2,5 | 3×B16 lub wg DTR | 30 mA | § 188 ust. 2 (indywidualne zabezpieczenie) |
| D2 | Piekarnik | 3×2,5 | B16 | 30 mA | jw. |
| D3 | Zmywarka | 3×2,5 | B16 | 30 mA | jw. |
| D4–D5 | Pralka; suszarka (pralnia P1) | 3×2,5 | B16 | 30 mA | jw.; pralnia z wodą — rozważyć 7-701 |
| D6 | **Pompa ciepła — jednostka zewnętrzna** (3f) | 5×2,5 lub wg DTR | C16 lub wg DTR | wg DTR (A/F/B) | [R7-C05] |
| D7 | Grzałka rezerwowa PC lub zasobnik CWU (3f) | 5×2,5 | wg DTR | 30 mA / wg DTR | Blokada w systemie zarządzania mocą |
| D8 | Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego | 3×1,5 | B10 | 30 mA | — |
| D9 | Rekuperator | 3×1,5 | B10 | 30 mA | — |
| D10 | **Ładowarka EV** 11 kW (3f), w garażu; przewód na rozbudowę do 22 kW | 5×6 | C32 lub wg DTR | **własny: B albo A + 6 mA DC** | [R7-J03]. ΔU dla 16 A, L = 15 m, 6 mm²: ≈ 0,32 % |
| D11 | Rezerwa (rura i puszka) na drugi punkt ładowania na podjeździe | rura Ø ≥ 40 | — | — | EPBD art. 14 ust. 4 (dobrowolnie) [R7-J02] |
| D12 | **Falownik PV** (3f, ≤ 6,5 kW) | 5×4 | B16/B20 wg DTR | wg 712.530.3.101 | [R7-I06]. ΔU ≈ 0,4 % (10 A, 20 m) |
| D13 | Brama garażowa | 3×1,5 | B10 | 30 mA | — |
| D14 | Brama wjazdowa, furtka elektryczna, wideodomofon (w linii ogrodzenia) | YKY 3×2,5 | B16 | 30 mA | ΔU ≈ 1,55 % (6 A, 40 m) |
| D15 | Pompa zbiornika retencyjnego lub nawadniania (jeśli będą) | YKY 3×2,5 | B16 | 30 mA | Koordynacja z branżą sanitarną |
| D16 | Osłony przeciwsłoneczne i rolety (napędy) | 3×1,5 | B10 | 30 mA | Elewacja z osłonami (brief) |
| D17 | Teletechnika: ONT, router, rack, SSWiN | 3×2,5 | B16 | 30 mA | — |
| D18 | Czujki dymu 230 V z podtrzymaniem (jeśli sieciowe) | 3×1,5 | B10 | 30 mA | § 28a ROPoż dopuszcza czujki bateryjne |
| R | Rezerwa ≥ 20 % | — | — | — | — |

**Długości obwodów:**
* Gniazda 2,5 mm² B16: przy I_B = 16 A obwód może mieć **≤ 24 m** od RG do ostatniego gniazda (ΔU ≤ 2,5 % przy 20 °C). Razem z WLZ (≤ 0,5 %) daje to ≤ 3 % wg N SEP-E-002 [R7-E04]. Dłuższe obwody (P2, gniazda zewnętrzne) projektować przewodem 4 mm² albo zasilać z RP2.
* Oświetlenie LED przy obciążeniu rzędu 3 A jest mało krytyczne (≈ 0,95 % przy 30 m, 1,5 mm²).

**Rozmieszczenie:**
* Każdy pokój ma ≥ 1 wypust przy powierzchni ≤ 20 m², ≥ 2 przy większej [R7-O01].
* Gniazda podwójne.
* Liczba gniazd w pokojach (założenie projektowe, nie wymóg; tablica N SEP-E-002 **NIEZWERYFIKOWANA**): pokój ≥ 3 punkty podwójne, salon ≥ 5, kuchnia ≥ 4 nad blatem plus gniazda urządzeń, łazienka 1–2 (poza strefą 2), hol 1–2.
* Trasy prowadzić w liniach prostych, równolegle do krawędzi [§ 183 ust. 1 pkt 8].

### 3.4 Łazienki (łazienka P0 gościnna, łazienki P1 i P2, WC P0)

1. Wszystkie obwody w pomieszczeniu objęte RCD 30 mA [R7-H02]. Gniazda łazienek na osobnym obwodzie [R7-H06].
2. Rysunki PT: zaznaczyć **strefy 0/1/2** na rzutach łazienek (strefa 1 do 2,25 m, strefa 2 szer. 0,6 m) [R7-H04].
   * **Przed wydaniem PT zweryfikować geometrię stref z PN-HD 60364-7-701:2025-02**, szczególnie dla natrysków bez brodzika.
   * Gniazda i łączniki poza strefami 0–2. W strefach 1–2 osprzęt ≥ IPX4 [R7-H03].
3. Ogrzewanie podłogowe elektryczne w łazienkach (jeśli będzie) oraz grzejniki drabinkowe z grzałką: obwód z RCD 30 mA, montaż wg 7-701 (poza strefą 0).
4. Miejscowe połączenia wyrównawcze: jeśli instalacje wod-kan są z tworzyw, łączenia wanny nie wymaga się [R7-H05]. Metalowe elementy (np. odpływy liniowe, kratki) ocenić w PT.

### 3.5 Uziemienie i połączenia wyrównawcze

1. **Wariant posadowienia (R5):**
   * **płyta na XPS** (izolacja termiczna od spodu i po obwodzie): uziom **otokowy w gruncie** wokół budynku albo pod warstwą pospółki. Materiał: **miedź, stal pomiedziowana (StCu) lub nierdzewna (StSt)** [R7-G02, R7-G04]. Zbrojenie płyty połączyć z otokiem w ≥ 4 punktach (założenie) i z GSU;
   * **ławy bez izolacji od gruntu:** uziom fundamentowy w betonie ławy (płaskownik na sztorc, otulina ≥ 5 cm, mocowany do zbrojenia co ≤ 2 m, pierścienie ≤ 20 m) [R7-G03].
2. Wyprowadzenia (zaciski przyłączeniowe) co najmniej:
   * do GSU w pomieszczeniu technicznym;
   * do ZKP lub rozdzielenia PEN, jeśli OSD tego wymaga;
   * **2–4 wyprowadzenia w narożnikach pod ewentualne przewody odprowadzające LPS** (rezerwa) [R7-K01];
   * do konstrukcji stalowej wiaty lub słupów, jeśli będą.
3. **GSU** w pomieszczeniu technicznym. Przewód uziemiający ≥ 16 mm² Cu (wymóg ≥ 6 mm², a zalecenie przy LPS to 16 mm²) [R7-G05].
4. **Główne połączenia wyrównawcze** (≥ 6 mm² Cu, ≥ ½ największego PE, ≤ 25 mm² Cu) [R7-G06]. Obejmują:
   * wodociąg metalowy i mostek przy wodomierzu [R7-B15];
   * metalowe elementy kanalizacji;
   * rury instalacji grzewczej (miedź lub stal, jeśli będą);
   * metalowe kanały rekuperacji;
   * obudowę szafki teletechnicznej;
   * konstrukcję PV i jej uziemienie funkcjonalne (jeden punkt) [R7-I07];
   * zbrojenie;
   * elementy stalowe wiaty [R7-B04].

### 3.6 Ochrona przepięciowa

1. **RG:** SPD T1+2 (ewentualnie T2), jak w pkt 3.2 [R7-F01…F05]. Uzasadnienie w opisie:
   * WT § 183 ust. 1 pkt 10;
   * CRL < 1000. Obliczenie z długością linii od OSD i N_g = 1,8 (albo z danych aktualnych) dołączyć do PT.
2. **PV DC:** SPD typu 2 dla DC (U_CPV ≥ napięcie łańcucha w najniższej temperaturze) przy falowniku, o ile falownik nie ma wbudowanych SPD DC typu 2 [R7-F06]. Przewody łańcuchów prowadzić razem (małe pętle).
3. **Telekomunikacja:** SPD na wejściu linii miedzianych i antenowych (dobra praktyka, § 192f ust. 3) [R7-N05]. Światłowód dielektryczny ochrony nie wymaga.
4. **Ochrona lokalna (T3)** przy wrażliwych odbiornikach (rack, sterownik PC) — opcjonalnie.

### 3.7 Ochrona odgromowa

1. W PT wykonać **analizę ryzyka wg PN-EN IEC 62305-2:2025** oraz, dla zgodności z literą WT, odnieść się do PN-EN 62305-2:2008 [R7-A05, R7-K01]. Wejście do analizy:
   * obrys i wysokość z modelu;
   * **N_g** (1,8 wg danych historycznych albo aktualnych) [R7-K03];
   * linia zasilająca: kabel nN;
   * linia telekomunikacyjna: światłowód dielektryczny, poza analizą;
   * **obciążenie ogniowe domu** (klasyfikacja ryzyka pożaru: zwykłe czy wysokie) [R7-K02];
   * środki ppoż.: gaśnica, czujki.
2. Wstępny szacunek: LPS nie jest wymagany przy ryzyku „zwykłym”, a przy „wysokim” (SPD + LPS IV) jest [R7-K05].
3. **Rekomendacja:** niezależnie od wyniku zaprojektować uziom otokowy z wyprowadzeniami pod LPS. W razie wyniku pozytywnego przyjąć LPS klasy III lub IV (zgodnie z propozycją PKOO SEP [R7-K04]):
   * zwody poziome na dachach płaskich z uwzględnieniem modułów PV;
   * zachowany **odstęp separacyjny s** od PV, albo połączenie wyrównawcze i SPD typu 1 po stronie DC.

### 3.8 Fotowoltaika

1. **Moc modułów ≤ 6,5 kWp**, suma z tabliczek. Falownik ≤ 6,5 kW [R7-I01, R7-I02]. Dzięki temu nie są potrzebne:
   * uzgodnienie z rzeczoznawcą ppoż.;
   * zawiadomienie PSP;
   * plan PV dla ekip ratowniczych.

   Przekroczenie 6,5 kW (np. przy rozbudowie) oznacza obowiązki z art. 29 ust. 4 pkt 3 lit. c PB.
2. **Lokalizacja modułów:**
   * dach techniczny P2 lub dach garażu (zielony ekstensywny — sprawdzić kolizję);
   * dostęp przez wyłaz;
   * falownik w pomieszczeniu technicznym lub w garażu;
   * trasa DC w osłonie, możliwie krótka.
3. **Przyłączenie przez zgłoszenie mikroinstalacji do ENEA Operator** (PE art. 7 ust. 8d4), bez opłaty. OSD przyłącza w ≤ 30 dni i wymienia licznik na dwukierunkowy [R7-I03].
4. **Falownik** z certyfikatem NC RfG z listy PTPiREE [R7-I05]. Przewody DC typu H1Z2Z2-K (PN-EN 50618) [R7-I08]. Rozłącznik DC przy falowniku (dobra praktyka). RCD dla obwodu AC wg R7-I06.
5. **Magazyn energii** (opcja): ≤ 30 kWh bez pozwolenia [R7-I01]. Jego moc nie wlicza się do mocy mikroinstalacji przy zgłoszeniu (PE art. 7 ust. 8d12).

### 3.9 PWP i czujki

1. **PWP (rekomendacja).**
   * Przycisk PWP przy wejściu głównym (strona północna) lub przy ZKP, oznakowany.
   * Działa na wyzwalacz lub napęd aparatu głównego RG i odcina wszystkie obwody, w tym obwód AC falownika.
   * Falownik z zabezpieczeniem przed pracą wyspową sam przestaje zasilać sieć domową. **Strona DC PV pozostaje pod napięciem** — oznakować.
   * Podstawa: WT § 183 ust. 2–4 (kubatura > 1000 m³, liczona z modelu). Uwaga o zwolnieniu z ROPoż § 4 ust. 2 pkt 2 [R7-B05, R7-M01].
2. **Czujki dymu (obowiązek):**
   * wymagane minimum: 1 w lokalu [R7-M02];
   * projektowo: ≥ 1 na każdej kondygnacji (hol lub klatka) i w sypialniach, czujki wg PN-EN 14604, łączone bezprzewodowo;
   * czujka CO tylko przy kominku lub innym spalaniu.

### 3.10 Teletechnika (GIA)

1. **Mikrokanalizacja od granicy działki (ZKP lub ogrodzenie) do pomieszczenia technicznego** — założenie: 2 × rura HDPE Ø40 (lub wiązka mikrorur), promienie gięcia wg specyfikacji operatora [R7-N02]. W PZT pokazać trasę razem z trasą WLZ [R2 Z23].
2. **Punkt zakończenia sieci (ONT)** — skrzynka telekomunikacyjna w pomieszczeniu technicznym z gniazdem 230 V (obwód D17). Obudowa objęta połączeniem wyrównawczym [R7-N05].
3. **Okablowanie światłowodowe wewnątrzbudynkowe** od punktu wprowadzenia do punktu zakończenia sieci:
   * co najmniej 2 włókna jednomodowe, złącza SC/APC, tłumienie toru ≤ 1,2 dB [R7-N04 — parametry WT jako dobra praktyka];
   * rozwiązanie „w pełni zgodne z GIA” zależy od polskich norm z art. 10 ust. 4, które nie są znane: **NIEZWERYFIKOWANE**.
4. **Okablowanie strukturalne mieszkania** (założenie, PN-EN 50173-4:2018 i PN-EN 50174-2:2018):
   * gniazda RJ45 kat. 6A w pokojach, salonie, gabinecie i przy TV;
   * punkty dostępowe Wi-Fi na każdej kondygnacji (PoE);
   * RG-6 kl. A z rury pionowej na dach do punktów TV;
   * rurowanie do wideodomofonu przy furtce i do bramy;
   * SSWiN (opcja).

### 3.11 EV

1. Obwód dedykowany do garażu: 5×6 mm², ładowarka 11 kW (zarządzanie mocą) [R7-J03]. RCD indywidualny typu B albo A + RDC-DD.
2. Jeżeli PZT przewiduje > 3 miejsca postojowe (2 w garażu + 2 na podjeździe), **dobrowolnie spełnić EPBD art. 14 ust. 4**:
   * okablowanie wstępne dla ≥ 2 miejsc;
   * kanał kablowy do pozostałych;
   * 1 punkt ładowania [R7-J02].

   Alternatywa: w PZT ograniczyć liczbę miejsc do 3 (MPZP wymaga min. 2).

### 3.12 Części rysunkowe i opisowe PT „instalacje elektryczne i teletechniczne” (lista kontrolna)

**Rysunki:**
* rzuty P0, P1, P2 i dachu w skali 1:50: oświetlenie, gniazda i siła, teletechnika, SPD i uziomy, PV na dachu;
* schemat jednokreskowy RG (i RP2);
* schemat zasilania ZKP–RG;
* plan uziomu i połączeń wyrównawczych;
* schemat PV (DC i AC);
* strefy łazienek.

Symbole wg IEC 60617 z legendą (R4-N01…N03).

**Opis:**
* bilans mocy;
* obliczenia: I_B, I_z, ΔU, Z_s i czas wyłączenia;
* analiza CRL (443);
* analiza ryzyka 62305-2;
* zestawienie obwodów i materiałów;
* wymagania PN-HD 60364-6 dla sprawdzeń odbiorczych [R7-O02];
* informacja o protokołach do zawiadomienia (PB art. 57) [R7-O03].

---

## 4. Nierozstrzygnięte

1. **Status WT i tryb projektowania (R3).** Wszystkie wymagania z WT stosuje się tylko w trybie art. 102a PB. Bez oświadczenia inwestora podstawą pozostają PN (wiedza techniczna). Rozwiązania z części 3 spełniają oba tryby.
2. **PWP w domu jednorodzinnym.**
   * WT § 183 ust. 2 (> 1000 m³) i ROPoż § 4 ust. 2 pkt 2 (zwolnienie właścicieli domów jednorodzinnych) są niespójne. Źródła wtórne przyjmują zwolnienie; nie znalazłem oficjalnego stanowiska KG PSP.
   * Kubatura strefy: do obliczenia z modelu (R3).
   * Rekomendacja: zastosować PWP (koszt pomijalny, spełnia oba odczytania).
3. **Rozdział PEN i WLZ 4- czy 5-żyłowy.**
   * Standard ENEA dla ZK1x-1P przewiduje listwę na kabel odbiorcy do 4×35 mm² z przewodem PEN.
   * WT § 183 ust. 1 pkt 2 wymaga oddzielnych PE i N w obwodach rozdzielczych.
   * Do wyjaśnienia z OSD we wniosku o warunki przyłączenia: czy możliwy jest rozdział PEN w ZKP i wyprowadzenie 5 żył.
4. **Moc przyłączeniowa i tabela OSD.** Mapowanie mocy na zabezpieczenie przedlicznikowe w ENEA nie jest zweryfikowane. Bilans mocy (zależny od doboru PC, płyty, EV) do obliczenia w PT.
5. **Analiza ryzyka odgromowego.** Rozstrzyga klasa ryzyka pożaru (obciążenie ogniowe domu). Brak aktualnej wartości N_g z sieci detekcji. Wydanie 2025 normy jest dostępne tylko po angielsku. Moje współczynniki są **NIEZWERYFIKOWANE**.
6. **Posadowienie a uziom (R5).** Płyta na XPS czy ławy — od tego zależy konstrukcja uziomu (otok w gruncie). Uziom trzeba ująć w PT konstrukcji: rysunek zbrojenia z wyprowadzeniami i otokiem.
7. **PN-HD 60364-7-701:2025-02.** Treść nowego wydania (geometria stref, gniazda, połączenia miejscowe) niezweryfikowana. Do sprawdzenia przed wydaniem PT.
8. **GIA:**
   * brak polskiego aktu wykonawczego (kategorie wyłączeń z art. 10 ust. 7, normy techniczne z ust. 4, procedury kontroli z ust. 5) — stan ELI 25.09.2026;
   * nie wiadomo, czy dla domów jednorodzinnych przewidziano wyłączenie. Projekt MC z 2025 r. zakładał obowiązek;
   * RCL i strony MC nie zostały sprawdzone.
9. **EPBD art. 14.** Transpozycja spóźniona (termin 29.05.2026). Może wejść w życie przed złożeniem wniosku lub w trakcie postępowania — śledzić Dz.U. Liczba miejsc postojowych w PZT decyduje o objęciu przepisem.
10. **SPD — wydania norm.**
    * PN-HD 60364-5-534 wchłonęła 5-53:2022. Nie zweryfikowałem, czy zmieniły się wartości I_imp i I_n.
    * PN-EN IEC 61643-11:2026-04 (wyrób) jest nowa.
    * Nie sprawdziłem, czy ENEA dopuszcza SPD w ZKP przed licznikiem (w projekcie SPD jest za licznikiem, w RG).
11. **AFDD.** Tylko zalecenie (4-42 A1:2015). Decyzja inwestora (sypialnie P1 i P2).
12. **Wartości N SEP-E-002** (liczba gniazd i obwodów, strefy instalacyjne, spadki 3 % i 0,5 %): tylko ze źródeł wtórnych. Treści normy SEP nie miałem.
13. **Wartości liczbowe z IEC 60228 i PN-HD 60364-5-52** (rezystancje, obciążalności): **NIEZWERYFIKOWANE**. Obliczenia w PT wykonać programem (np. wg PN-HD 60364-5-52 zał. B).
14. **NC RfG i certyfikacja** od 1.01.2027 (etap II PTPiREE): falownik wybrać z aktualnej listy w chwili zakupu.
