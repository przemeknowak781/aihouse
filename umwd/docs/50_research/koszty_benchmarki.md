# Koszty realizacji: benchmarki cenowe i parametryczny model kosztów (pod Załącznik F.14.B)

**Status:** research „koszty”, wersja 1.0
**Data opracowania i dostępu do wszystkich źródeł:** 2026-11-16
**Plik:** `docs/50_research/koszty_benchmarki.md`. Model obliczeniowy: `tools/koszty_model.py` (uruchomienie: `python3 -I tools/koszty_model.py [wejscie.json] [--rows mid]`)
**Poziom cen przyjęty w modelu:** II kw. 2026 (termin złożenia prac Etapu II: 10.07.2026, `10_regulamin/lista_kontrolna_etap2.md`). Ceny **netto** z narzutami (koszty pośrednie i zysk zawarte w cenach jednostkowych, zgodnie z definicją „ceny jednostkowej” w § 1 pkt 1 rozp. MRiT z 20.12.2021, Dz.U. 2021 poz. 2458).

---

## 0. Metryka i zasady

### 0.1 Legenda źródeł
- **[O]**: źródło oficjalne. Należą tu GUS, Dziennik Ustaw, zamawiający publiczny (BIP, komunikat prasowy urzędu), TED oraz materiały konkursowe.
- **[R]**: raport firmy doradczej lub badawczej (Arcadis, Turner & Townsend, Spectis, PSB). To źródło branżowe, ale metodyka jest jawna tylko częściowo.
- **[W]**: źródło wtórne, czyli portal branżowy, prasa albo poradnik cenowy (kb.pl, muratordom.pl, oferteo.pl, globenergia.pl, eurobuildcee.com, inzynierbudownictwa.pl, wnp.pl itp.).
- **[Z]**: założenie zespołu. **Nie jest to cena ze źródła.** Jest to stawka dobrana tak, aby suma modelu zgadzała się z benchmarkami przetargowymi z rozdz. 4. Każde [Z] trzeba zweryfikować ofertą lub kosztorysantem.
- **„Wniosek:”** oznacza interpretację zespołu, a nie fakt.
- **(s)** przy źródle oznacza, że dane pochodzą ze streszczenia wyników wyszukiwarki, a strony nie otwierano bezpośrednio. Wiarygodność jest wtedy niższa i dane wymagają weryfikacji.

### 0.2 Zakaz Inwestora
Nie wyszukiwano, nie otwierano i nie wykorzystano żadnych informacji o pracach nagrodzonych, wyróżnionych ani konkurencyjnych w konkursie UMWD/Sejmik (Wrocław, Mazowiecka / Wybrzeże Słowackiego). W jednym wyszukiwaniu dotyczącym innych urzędów wyszukiwarka sama podała nagłówek o wynikach tego konkursu. Nie otwierano go i nic z niego nie zanotowano. Adres przekazano orkiestratorowi w polu `discarded_sources`, a w tym pliku go nie ma. Wykorzystano wyłącznie dane o innych inwestycjach, w tym o siedzibie Sejmiku Województwa Mazowieckiego i o wrocławskim Sądzie Apelacyjnym.

### 0.3 Ograniczenia, które trzeba znać przed wnioskami
1. **Brak jawnych, autorytatywnych cen elementów.** Sekocenbud (BCO/BCE), Orgbud i Intercenbud są płatne. Darmowy dodatek Sekocenbud BCO cz. Ia (III kw. 2025) zawiera tylko opisy obiektów, bez cen. GUS publikuje dla obiektów **wyłącznie indeksy**, bez cen bezwzględnych. Stawki elementowe w rozdz. 5 to więc poradniki rynkowe [W] (głównie dla budownictwa mieszkaniowego) oraz założenia [Z].
2. **Netto czy brutto w benchmarkach.** Część komunikatów prasowych nie podaje, czy kwota jest netto czy brutto. W tabeli B pokazano obie interpretacje.
3. **Definicje powierzchni.** „Powierzchnia użytkowa” w komunikatach zamawiających bywa liczona różnie (z komunikacją lub bez, z garażem lub bez). Porównanie w zł/m² PU jest obarczone dużym błędem. Porównanie w zł/m² PC jest pewniejsze, ale PC podaje mniej źródeł.
4. **Limit wyszukiwań.** Budżet wyszukiwań tej rundy się wyczerpał (limit narzędzia). Nie udało się dotrzeć do przetargów na systemy głosowania sejmików ani do jawnych cen ścian szczelinowych. Pozycje te mają status [Z]. Można je uzupełnić w kolejnej rundzie.

---

## 1. Najważniejsze wnioski (streszczenie)

1. **Limit 150 mln zł netto jest twardy i realnie wiążący.** Bottom-up model w układzie F.14.B (poziom „mid”, II kw. 2026) dla wariantu referencyjnego V1 daje **146,3 mln zł netto**, w tym rezerwę 5%. V1 to PC nadziemna 14 000 m² i podziemie 3 900 m² (1 kondygnacja + częściowa −2). Zapas względem limitu wynosi tylko 2,5%. Wariant z dwiema pełnymi kondygnacjami podziemnymi (V2, 5 800 m²) daje **152,4 mln**, czyli przekracza limit. Wariant z PC nadziemną 13 000 m² (V1b) daje **141,4 mln**, czyli zapas ok. 6%. *(Wniosek; model rozdz. 7.)*
2. **Pasmo rynkowe dla porównywalnych budynków publicznych** po normalizacji do II kw. 2026 wynosi **ok. 7 400–9 300 zł/m² PC netto**, przy środku ok. 8 000–8 500. Model V1 mid daje 8 170 zł/m² PC, czyli mieści się w paśmie. Najbliższy analog to siedziba Sejmiku Województwa Mazowieckiego (umowa IV 2026): 124,3 mln zł za >6 800 m² PU. Przy interpretacji „brutto” daje to ok. 7 800–9 300 zł/m² PC netto. *(rozdz. 4)*
3. **Ceny budowlane przyspieszyły w 2026 r.** Średnioroczny wzrost cen produkcji budowlano-montażowej wyniósł +6,0% w 2024 r. i +3,2% w 2025 r. We wrześniu 2026 r. było to już **+6,9% r/r**, w tym budowa budynków +6,7%, a roboty specjalistyczne +7,7% [O GUS]. Prognozy z początku 2026 r. zakładały 2,5–3,5% dla Warszawy [R Arcadis], więc **zaniżyły tempo**. Każdy rok opóźnienia oznacza +4–7% kosztu. *(rozdz. 3)*
4. **Waloryzacja do 2027 r. „zjada” zapas.** V1 przy +5% daje 153,6 mln. W połowie budowy (ok. 2030) V1 kosztuje 163–189 mln przy 3–7% rocznie. *Wniosek:* w F.14.B podać koszt na **jawnie opisanym poziomie cen (II kw. 2026)**, a ryzyko waloryzacji opisać w części opisowej i pokazać rezerwę. Wpisanie wartości zwaloryzowanych do 2030 r. w sumę porównywaną z limitem formalnie wykluczyłoby pracę z limitu, którego Regulamin nie indeksuje (R.III ust. 3). Ten punkt jest interpretacją.
5. **Największe dźwignie kosztu (mid, krańcowo):** +1 000 m² PC nadziemnej to ok. +4,9 mln zł. Druga pełna kondygnacja podziemna to ok. +6,1 mln zł w modelu, a realnie +6–9 mln (rozdz. 7.5). Zamiana 1 000 m² ceramiki na ścianę słupowo-ryglową to +1,5 mln zł. Zamiana 1 000 m² ceramiki na BIPV to +1,0 mln zł.
6. **M.12 wymaga PV 0,4–1,0 MWp „na dachu dominanty i elewacjach”.** Dach dominanty (≈1 100–1 200 m²) mieści ok. 0,2 MWp. Do minimum brakuje ok. 0,2 MWp, czyli ok. 1 300–1 400 m² BIPV na elewacjach. Przy zamianie okładziny ceramicznej kosztuje to ok. **+1,4 mln zł**. Jest to wykonalne w budżecie, jeżeli BIPV zastępuje okładzinę, a nie jest warstwą dodatkową (+2,6 mln/1 000 m²). *(Wniosek; [Z] 0,15 kWp/m².)*
7. **Uwarunkowania lokalne podnoszą koszt podziemia.** Woda gruntowa stabilizuje się na 3,2–3,8 m p.p.t. Teren leży w strefie narażonej na podtopienia oraz na obszarze zagrożenia powodzią. Nasypy niebudowlane mają miąższość do 3,8 m [O M.05]. Wymaga to szczelnej obudowy (ściany szczelinowe), białej wanny, zabezpieczenia przed wyporem i utylizacji nasypów. Podziemie V1 kosztuje w modelu ok. 22,6 mln zł: ok. 5 800 zł/m² PC, ok. 205 tys. zł na miejsce postojowe (22,6 mln / 110), z MDS, bez kosztów stałych i rezerwy. <!-- poprawione przez weryfikatora: było „ok. 220 tys.”, błąd arytmetyczny -->
8. **Koszt Dokumentacji ≤ 5,4% × 150 mln = 8,1 mln zł.** Według rozp. MRiT 2021 (Dz.U. 2021 poz. 2458) wskaźnik W% dla robót o wartości 150 mln zł wynosi: kategoria IV 4,10%, V 5,05%, VI 6,00% [O]. Limit 5,4% obejmuje też nadzór autorski (7% wynagrodzenia wg F.01 § 14) i doradztwo przetargowe (1%). Dla samych projektów zostaje więc ok. 4,97%, czyli poziom kategorii V. *Wniosek:* zadeklarować **ok. 7,5–7,9 mln zł netto** z podziałem na etapy wg F.01. *(rozdz. 8)*
9. **Sąd oceni rzetelność wyceny z udziałem ekspertów od kosztów** (Reg. R.III ust. 1 pkt 10; Wyj. 20 odp. 74) [O]. *Wniosek:* przewagą będzie przedmiar spójny z rysunkami i F.15. Do tego ceny jednostkowe w kolumnie pomocniczej i krótka nota metodyczna (poziom cen, źródła, rezerwa), a nie tylko „okrągłe” kwoty.
10. **Uwaga weryfikatora: wariant referencyjny V1 nie spełnia minimum PV z M.12.** W `REF` modelu jest 200 kWp na dachu + 400 m² BIPV × 0,15 kWp/m² = **260 kWp**, a M.12 wymaga **0,4–1,0 MWp**. Doprowadzenie do 400 kWp (ok. 1 333 m² BIPV zamiast ceramiki, czyli +933 m²) daje w modelu: V1 mid **147,3 mln** (+0,96 mln; low 108,0 / high 204,5), V1b mid ok. **142,0 mln**, V2 mid ok. **153,4 mln**. Zapas V1 wobec limitu spada do ok. 1,8%. <!-- poprawione przez weryfikatora: przeliczenie tools/koszty_model.py -->

---

## 2. Wymagania Regulaminu wobec kosztów (fakty)

| # | Wymaganie | Źródło [O] |
|---|---|---|
| R1 | Maksymalny planowany łączny koszt realizacji Inwestycji w stanie wykończonym wraz z zagospodarowaniem terenu: **150 mln zł netto**. Uczestnik „powinien podać realny koszt wynikający z przedstawionych rozwiązań”. | Regulamin R.III ust. 3 pkt 1–2 (tekst: `00_materialy/tekst/2_Regulamin_Konkursu-sig.txt`, s. 21) |
| R2 | Koszt jest **nieprzekraczalny**, a skalę, technologię i standard należy dostosować do budżetu. Sąd dokona „eksperckiej oceny rzetelności Państwa wyceny”. „Niedopuszczalne jest sztuczne zaniżanie kosztorysu”. | Wyjaśnienia nr 20, odp. 74 (`10_regulamin/wyjasnienia_streszczenie.md`, W-053) |
| R3 | Maksymalny koszt wykonania Przedmiotu zamówienia (Dokumentacja + nadzór) wynosi **5,4%** planowanego łącznego kosztu realizacji netto, czyli 8,1 mln zł. Regulamin nie mówi wprost, czy ta kwota jest netto czy brutto. | Reg. R.III ust. 4, s. 21–22 |
| R4 | Rozwiązania proekologiczne „zostaną poddane szczegółowej ocenie przez ekspertów powołanych przez Sąd Konkursowy w zakresie kosztów inwestycyjnych, operacyjnych i efektywności ekologicznej” (Etap II). | Reg. R.III ust. 1 pkt 10, s. 20 |
| R5 | Kryterium drugorzędne: „Realność i optymalizacja ekonomiczna przyjętych rozwiązań w odniesieniu do kosztów realizacji Inwestycji i kosztów jej użytkowania i utrzymania”. Kryterium kosztowe może być rozpatrywane rozdzielnie. | Reg. R.VIII ust. 1 pkt 2 i ust. 2 pkt 4, s. 48–49 |
| R6 | F.14.B jest obowiązkowy. Praca bez niego „nie będzie podlegała ocenie”. Składa się go w PDF opisu i jako xlsx na wzorze. | Reg. R.VII ust. 2 pkt 3 lit. f, s. 45; ust. 3 pkt 2 lit. b, s. 46 (`10_regulamin/formularze_tabele.md`) |
| R7 | Struktura F.14.B: 18 grup, wiersze „Ilość / J.m. / Wartość netto / VAT / Wartość brutto”, **bez kolumny ceny jednostkowej**. Wzór ma błędy (np. komórki kosztu Dokumentacji H163/H164 = suma robót, brak formuł brutto, pozycje bez j.m. lub VAT). | `00_materialy/tekst/F.14.B_…txt`; pełna analiza pułapek: `10_regulamin/formularze_tabele.md` rozdz. 2.3 |
| R8 | Zakres F.01 obejmuje ekspertyzy wpływu na budynki WS 5 i Mazowiecka 19 z projektem zabezpieczeń oraz projekt zamurowania okien w szczycie Mazowieckiej 19. Koszty robót z tym związanych trzeba więc ująć w kosztach realizacji. | F.01 zał. 3 (tekst F.01 l. 1931–1936) |
| R9 | Podział wynagrodzenia za Dokumentację wg etapów: E1 12% / E2 30% / E3 10% / E4 40% / E5 1% (doradztwo przetargowe) / E6 7% (nadzór autorski). | F.01 § 14 ust. 2 |
| R10 | M.12 wymaga: gruntowe pompy ciepła jako główne źródło (odwierty możliwe pod budynkiem), PV **0,4–1,0 MWp** na dachu dominanty i elewacjach, magazyny ciepła i chłodu (krótko- i długoterminowe), magazyn energii elektrycznej, sieć ciepłownicza tylko rezerwowo, retencja, woda szara do spłukiwania WC, analiza odzysku ciepła z wody szarej. | M.12 s. 1–2 (`00_materialy/tekst/M.12._STANDARD_ZERO-EMISYJNOŚCI.txt`) |

---

## 3. Dynamika cen i waloryzacja

### 3.1 Wskaźniki (tabela D)

| Wskaźnik | Wartość | Okres | Źródło |
|---|---|---|---|
| Ceny produkcji budowlano-montażowej, średnio r/r | **+6,0%** | 2024 | [O] GUS, *Sytuacja społeczno-gospodarcza kraju w 2025 r.*, rozdz. „Ceny produkcji budowlano-montażowej” |
| j.w. | **+3,2%** (budowa budynków +3,2%) | 2025 | j.w. |
| j.w., grudzień r/r | +3,6% (budowa budynków +3,4%) | XII 2025 | j.w. |
| Ceny produkcji b-m, kwartał do kwartału | **+2,1%** | II kw. 2026 / I kw. 2026 | [O] GUS, komunikat o zmianach cen produkcji b-m w II kw. 2026 |
| Ceny produkcji b-m r/r | +6,2% (budowa budynków +5,7%) | VII 2026 | [O] GUS, *Price indices of construction and assembly production in July 2026* |
| Ceny produkcji b-m r/r | **+6,9%** (budowa budynków +6,7%; inżynieria +6,5%; roboty specjalistyczne +7,7%); m/m +0,7% | IX 2026 (publ. 20.10.2026) | [O] GUS, *Wskaźniki cen produkcji budowlano-montażowej we wrześniu 2026 r.* |
| Indeks cen obiektu „budynek administracyjno-biurowy” (PKOB 1220, reprezentant GUS) | 102,8 (IX 2025 / IX 2024); 103,5 (I–IX 2025 / I–IX 2024) | 2025 | [O] GUS, *Ceny robót budowlano-montażowych i obiektów budowlanych – wrzesień 2025*, tabl. 2. Reprezentantem jest stary, 6-kondygnacyjny biurowiec o PU 2 124 m², a publikacja podaje tylko indeks, bez ceny bezwzględnej |
| Ceny produkcji b-m r/r w 2022–2023 | VII 2022 +13,4%; XII 2022 ok. +14,3%; I 2023 +13,1%; V 2023 +10,9%; VIII 2023 +9,8%; X 2023 +8,2%; XII 2023 +7,5% | 2022–2023 | [W] globenergia.pl, blog.ongeo.pl (cytują GUS) (s). **Średnioroczny 2023: +10,2%** [O] GUS, *Sytuacja społeczno-gospodarcza kraju w 2024 r.* (tam też wstępne 2024: +5,9%, później skorygowane do +6,0%). Średniorocznej wartości 2022 nie zweryfikowano <!-- poprawione przez weryfikatora --> |
| Inflacja kosztów budowy, Warszawa | 2024: 4–5%; prognoza 2025: 5–6%; indeks kosztów Warszawy 99 (Amsterdam = 100) | ICC 2025 | [R] Arcadis, *International Construction Costs 2025* (PDF) |
| j.w. | 4Q 2025: 2,5–3,5%; prognoza 4Q 2026: 2,5–3,5%; indeks Warszawy 100 | ICC 2026 | [R] Arcadis, *International Construction Costs 2026* (PDF) |
| Inflacja kosztów budowy, Warszawa | 5,1% (2024) → prognoza 2,8% (2025) | 2025 | [R] Turner & Townsend, *Global Construction Market Intelligence 2025 – Europe* (s) |
| Ceny materiałów budowlanych | IV kw. 2025: 0,0% r/r (Spectis); I poł. 2026: +1,1%, VI 2026: +3,5% r/r (PSB); „spokój cenowy dobiega końca” | 2025–2026 | [R/W] Spectis i Grupa PSB cytowani przez inzynierbudownictwa.pl, kb.pl, muratordom.pl (s) |

**Wniosek (krytycznie):** w 2026 r. ceny robót rosną szybciej niż ceny materiałów (+6,9% wobec ok. +3,5%). Przyspieszenie napędzają robocizna i marże, czyli ożywienie popytu, a nie materiały. Prognozy konsultantów z przełomu 2025/2026 (2,5–3,5%) okazały się za niskie. Do planowania należy przyjmować **4–6% rocznie**, a w scenariuszu stresowym 7%.

*Uwaga weryfikatora:* błąd prognoz działa w obie strony. Arcadis ICC 2025 przewidywał dla Warszawy w 2025 r. 5–6%, a GUS podał za 2025 r. +3,2% (przeszacowanie). Arcadis ICC 2026 przewidywał 2,5–3,5%, a GUS za IX 2026 podaje +6,9% r/r (niedoszacowanie). Miary nie są też identyczne: Arcadis mierzy ceny budynków w Warszawie (do IV kw.), a GUS ceny produkcji budowlano-montażowej w całym kraju, łącznie z inżynierią. Wniosek: pasmo 4–6% jest rozsądne, ale nie dlatego, że „konsultanci zaniżają”. Uzasadnia je niepewność ±2–3 p.p. <!-- poprawione przez weryfikatora -->

### 3.2 Współczynniki waloryzacji użyte do normalizacji benchmarków (do II kw. 2026)

| Rok bazowy kontraktu | Współczynnik | Wyprowadzenie |
|---|---|---|
| 2021 | **≈ 1,42** (±0,05) | 1,125 (2022, przybliżenie z odczytów r/r) × 1,10 (2023; GUS: +10,2% [O], przybliżenie poprawne <!-- poprawione przez weryfikatora -->) × 1,060 (2024 [O]) × 1,032 (2025 [O]) × 1,05 (I poł. 2026 wobec średniej 2025: II kw./I kw. +2,1% i VII r/r +6,2% [O]). Wniosek |
| 2022 | ≈ 1,26 | j.w. bez 2022 |
| 2024 | ≈ 1,08 | 1,032 × 1,05 |
| 2025 | ≈ 1,05 | j.w. |

### 3.3 Waloryzacja w przód (scenariusze dla wariantu V1 mid = 146,3 mln zł, II kw. 2026)

| Horyzont | 3%/rok | 4%/rok | 5%/rok | 6%/rok | 7%/rok |
|---|---|---|---|---|---|
| II kw. 2027 (1 rok) | 150,7 | 152,2 | 153,6 | 155,1 | 156,5 |
| Połowa budowy ≈ I kw. 2030 (3,75 roku; założenie harmonogramu: Dokumentacja 2027–2028, przetarg GW 2028, budowa 2028–2031) | 163,4 | 169,3 | 175,7 | 182,1 | 188,6 |

*Wniosek:* inwestor zdefiniował limit bez klauzuli waloryzacyjnej. Należy więc pokazać koszt na poziomie cen z daty złożenia pracy i wyraźnie to zaznaczyć. W opisie warto dodać jedno zdanie o ryzyku waloryzacji i o rezerwie. To podnosi wiarygodność w oczach eksperta kosztowego (R2, R4).

---

## 4. Benchmarki przetargowe: budynki publiczne 2021–2026 (tabela B)

Normalizacja: jeżeli źródło podaje „brutto”, netto = brutto / 1,23. Gdy status VAT jest nieznany, podano obie interpretacje. Waloryzacja wg tab. 3.2. „PC” to powierzchnia całkowita, „PU” to powierzchnia użytkowa wg źródła.

| # | Obiekt (zamawiający) | Rok / etap | Wartość | Powierzchnia, cechy | zł/m² wg źródła | Netto, II kw. 2026 (wniosek) | Źródło |
|---|---|---|---|---|---|---|---|
| **B1** | **Siedziba Sejmiku Województwa Mazowieckiego** (budynek samorządu) + Sąd Apelacyjny, Warszawa, ul. Świętojerska 9 (Woj. Mazowieckie) | umowa 9.04.2026; przetarg ogłoszony 8.07.2025; koniec poł. 2029 | budynek samorządu **124,3 mln zł**; Sąd 102,2 mln; ul. Telakowskiej 1,5 mln; razem >239,6 mln. VAT niepodany; wg streszczenia wyszukiwarki najtańsza z 13 ofert to ok. 239 mln zł **brutto** przy założeniach inwestora >300 mln (s, niezweryfikowane) | samorząd >6 800 m² PU (Sejmik, kancelaria, jednostki); 2 budynki 6-kondygnacyjne ≤23,4 m; 2 niezależne parkingi podziemne; BMS, dachy zielone, geotermia, PV; prace archeologiczne i częściowa rozbiórka | 18 280 zł/m² PU | jeśli brutto: **14 860 zł/m² PU**; przy PC = 1,6–1,9 × PU → **7 820–9 290 zł/m² PC**. Jeśli netto: 9 620–11 430 zł/m² PC | [O] mazovia.pl (9.04.2026); [W] inzynierbudownictwa.pl (14.04.2026), wnp.pl (9.04.2026), propertydesign.pl (13.04.2026), nowawarszawa.pl (10.07.2025) |
| **B2** | Siedziba Komendy Miejskiej Policji w Katowicach | oferta XII 2025; umowa 21.05.2026; 60 mies. | **153,93 mln zł brutto** = 125,1 mln netto | budynek główny administracyjno-biurowy ≈ 11 000 m² PU, 3 kond. nadz. + 1 podz.; osobny budynek garażowy oraz budynki techniczno-magazynowy i kynologiczny (więc wskaźnik na PU budynku głównego jest zawyżony) <!-- poprawione przez weryfikatora: investmap.pl --> ; >200 miejsc na terenie | 13 990 brutto / 11 380 netto zł/m² PU (całość ÷ PU budynku głównego) | ≈ 11 800 zł/m² PU (×1,04) | [W] biznesradar.pl (31.12.2025), investmap.pl (25.05.2026) |
| **B3** | Siedziba Archiwum Województwa Mazowieckiego, Piaseczno (Woj. Mazowieckie) | umowa VII 2024 | **>110 mln zł brutto** = >89,4 mln netto | PC 12 808,59 m², PU 11 279,40 m² (PU/PC ≈ 0,88); budynek archiwalno-biurowo-magazynowy, 3 kond. nadz. | 6 980 zł/m² PC netto | **≈ 7 550 zł/m² PC** (≈ 8 600 zł/m² PU). *Uwaga weryfikatora:* słaby analog dla UMWD (funkcja magazynowa, PU/PC 0,88 wobec ok. 0,5 w UMWD, 3 kondygnacje, teren podmiejski), zaniża dolną granicę pasma <!-- poprawione przez weryfikatora: PC wg mota-engil-ce.eu 12 808,59 m² zamiast „≈13 000” --> | [W] eurobuildcee.com (19.07.2024), mota-engil-ce.eu (18.07.2024) |
| **B4** | Centrum Administracyjne w Ciechanowie (Woj. Mazowieckie + Starostwo) | umowa 2021; koniec 30.06.2023 | 53 375 850 zł („całkowity koszt budowy”, VAT niepodany) | **PC 7 673,68 m²**, 36 499 m³, 5 kond. + podpiwniczenie | 6 956 zł/m² PC | jeśli brutto: **≈ 8 040**; jeśli netto: ≈ 9 890 zł/m² PC | [W] forsal.pl (2.07.2021) |
| **B5** | Budynek Urzędu Miasta Lublin, ul. Leszczyńskiego (zaprojektuj i wybuduj, Budimex) | umowa 2021; koniec 30.09.2023 | 82,6 mln zł (projekt + roboty; VAT niepodany) | PU ≈ 13 700 m² (w tym ≈ 7 600 m² biur), 7 kond. nadz. + parking podziemny; rozbiórka starego budynku | 6 030 zł/m² PU | jeśli brutto: 6 970; jeśli netto: 8 570 zł/m² PU. *Wniosek:* nisko; formuła D&B z 2021 r., przed szczytem inflacji | [W] inzynierbudownictwa.pl (2021) |
| **B6** | Sąd Apelacyjny we Wrocławiu (teren dawnego targowiska Zielińskiego) | oferty 2021; 38 mies. | najkorzystniejsza 73,0 mln zł (Mirbud); pozostałe 83,0 / 88,1 / 94,3 mln (rozrzut +14…+29%) | PU ≈ 6 000 m², >33 000 m³, 6 kond., parking | 12 170 zł/m² PU; 2 212 zł/m³ | jeśli brutto: ≈ 14 060 zł/m² PU | [O] wroclaw.pl (29.06.2021) |
| **B7** | Sąd Rejonowy i prokuratura, Wieliczka | ogłoszenie TED 20.06.2022 (zamawiający: Sąd Okręgowy w Krakowie); **umowa XI 2022** (RE-Bau), koniec III kw. 2025 | wartość w TED: 73 784 488 zł (bez VAT); **umowa: „ponad 124 mln zł”** (VAT niepodany), czyli ok. +68% wobec wartości z TED | pow. netto łącznie >8 500 m² (sąd ok. 7 200 + prokuratura ok. 1 400), 5 kond. Pow. zabudowy 1 739 m² niepotwierdzona | wg umowy: ≈ 14 400 zł/m² pow. netto (jeśli brutto: ≈ 11 700 netto) | **≈ 14 800–18 200 zł/m² pow. netto** (×1,26; wg umowy, a nie szacunku). Lekcja: szacunek zamawiającego z 2022 r. był o ok. 40% niższy od ceny umownej <!-- poprawione przez weryfikatora: wcześniej liczono z wartości szacunkowej TED (73,8 mln), nie z umowy; dane TED potwierdzone przez api.ted.europa.eu, dane umowy przez radiokrakow.pl (28.11.2022) --> | [O] TED 328918-2022 (api.ted.europa.eu); [W] radiokrakow.pl (28.11.2022) |
| **B8** | Parking podziemny pod pl. Powstańców Warszawy (PPP, Immo Park / Mota-Engil) | umowa 2022; otwarcie 21.03.2025 | ok. **85 mln zł brutto** = 69,1 mln netto | 420 miejsc, 4 poziomy (jedno źródło: 407 miejsc / 2 poziomy) | 164 500 zł/miejsce netto | **≈ 208 000 zł/miejsce** | [W] eurobuildcee.com (3.08.2022), auto-swiat.pl; [O] warszawa19115.pl |
| B9 | Urząd Marszałkowski Województwa Lubelskiego + Centrum Kongresowe, Lublin (historyczny) | umowa 12.03.2014 | 89,7 mln zł netto | PC 28 100 m² (UM 18,3 tys. + CK 9,8 tys.), 6 kond. nadz. + 3 podz., 238 miejsc | 3 192 zł/m² PC | nie normalizowano (brak serii 2015–2020 w zebranych źródłach). *Wniosek:* dołek cenowy 2014, nie do kalibracji | [W] Budimex, komunikat prasowy (2014), budimex.pl <!-- poprawione przez weryfikatora: pierwotny URL wskazywał domenę testową bdm-stg.mda.pl --> |
| B10 | Zespół budynków Urzędu Marszałkowskiego Woj. Małopolskiego, Kraków (3 budynki, w tym Sejmik) | przetarg 2018; unieważniony 2019 | szacunek ≈ 240 mln zł | brak powierzchni | — | — | [W] radiokrakow.pl (2018, 2019). Lekcja: przetarg unieważniono, uznając, że budowa „nie leży w interesie publicznym”, i zapowiedziano analizę redukcji skali i kosztów |
| B11 | Starostwo Powiatowe w Białej Podlaskiej (zaprojektuj i wybuduj) | umowa 15.03.2024 | ≈ 43 mln zł | 4 kond.; brak powierzchni | — | — | [W] radio.lublin.pl |
| B12 | Komenda Powiatowa Policji w Polkowicach | umowa 2023 | >44,2 mln zł (szacunek) | PU >2 900 m², 3 budynki z garażami | 15 240 zł/m² PU | — (efekt małej skali) | [O] samorzad.gov.pl (s) |

**Wnioski z tabeli B:**
- **Pasmo kalibracyjne (budynki kompletne, zł/m² PC netto, II kw. 2026): 7 400–9 300, środek ≈ 8 000–8 500** (B1 przy interpretacji brutto, B3, B4). Siedziba Sejmiku (B1) leży w historycznym śródmieściu i ma garaż podziemny, czyli warunki najbliższe UMWD. Warunki UMWD są jednak trudniejsze: budynek wysoki 35–45 m (B1 ma ≤23,4 m), woda gruntowa nad posadowieniem, wymagania M.12 dotyczące PV i GPC.
- **Uwaga weryfikatora do B1:** kwoty dla budynków (124,3 + 102,2 = 226,5 mln, z ul. Telakowskiej 228,0 mln) nie sumują się do podanego „ponad 239,6 mln zł” kosztu robót (mazovia.pl, wnp.pl, propertydesign.pl). Ok. 11–13 mln to najpewniej koszty wspólne (teren, infrastruktura). Po proporcjonalnym rozdziale koszt budynku samorządu rósłby o ok. 5–6%. Także przelicznik PC = 1,6–1,9 × PU dla B1 jest założeniem [Z]: źródła nie podają PC, a z dwoma garażami podziemnymi wskaźnik może przekraczać 2,0. <!-- poprawione przez weryfikatora -->
- **W przeliczeniu na PU** wartości są znacznie wyższe: 11 400–14 900 zł/m² PU netto (B1, B2, B6), a dla B7 liczonego z ceny umownej nawet 14 800–18 200 zł/m² pow. netto. <!-- poprawione przez weryfikatora: było „11 400–14 900 (B1, B2, B6, B7)” --> UMWD ma programową PU ok. 8 600 m² (bez KW i garażu, `20_program/program.md`). Przy 146 mln daje to ok. 17 000 zł/m² PU. *Wniosek:* jeżeli ekspert Sądu porówna koszt w zł/m² PU, UMWD wypadnie drogo z powodu wskaźnika PC/PU ≈ 1,7 i wysokiego udziału holi i sal. **Efektywność powierzchni (PU/PC) jest więc argumentem kosztowym.** W opisie trzeba podać obie miary i definicję PU.
- **Rozrzut ofert w jednym przetargu sięga +30%** (B6). Do tego dochodzi różnica „założenia inwestora wobec najtańszej oferty” (B1, niezweryfikowana). *Wniosek:* „realny koszt” to koszt bliski medianie rynku, a nie najtańszej ofercie.
- **Garaż w wodzie gruntowej w centrum miasta** kosztuje ok. 200 tys. zł/miejsce w obiekcie samodzielnym (B8). W budynku z garażem pod spodem koszt jest niższy, bo konstrukcja i rdzenie są wspólne. Rynek deweloperski podaje 60–120 tys. zł/miejsce [W money.pl (s)], ale dla budynków mieszkalnych i bez wymagań MDS.

---

## 5. Wskaźniki elementowe (tabela E): wartość, zakres, rok, źródło

Stawki „model” to wartości low / **mid** / high wpisane do `tools/koszty_model.py` (netto, II kw. 2026, z montażem i narzutami). Kolumna „Źródło rynkowe” pokazuje, skąd pochodzi dolna granica albo kontekst. Poradniki [W] dotyczą zwykle domów i inwestorów indywidualnych. Dla budynku publicznego, wysokiego (W), z wymaganiami ogniowymi (okładziny A1/A2) i rusztowaniami na pełną wysokość zastosowano narzut [Z].

| Element | Stawka modelu (low / **mid** / high) | Źródło rynkowe (wartość, rok) | Status |
|---|---|---|---|
| **Budynek kompletny (kontrola top-down)** | 7 400 / **8 200** / 9 300 zł/m² PC | tab. B (B1, B3, B4 po normalizacji) | [O/W] → wniosek |
| Część nadziemna: konstrukcja + instalacje + wykończenie (bez fasady, dachu, dźwigów, AV, źródeł OZE) | ≈ 4 600 / **5 200** / 6 000 zł/m² PC (suma pozycji 3, 5, 7–9, 11–14 modelu) | brak jawnego źródła. Kalibracja do tab. B | [Z] |
| Część podziemna all-in (ściany szczelinowe, wykop, odwodnienie, płyta, biała wanna, stropy, instalacje, posadzki, rampa, MDS) | wynik modelu (mid, bez KS i rezerwy): V1 ≈ 5 800 zł/m² PC, ok. 205 tys. zł/miejsce przy 110 miejscach; V2 ≈ 4 900 zł/m² PC, ok. 167 tys. zł/miejsce przy 170 miejscach <!-- poprawione przez weryfikatora: było 220 / 180 tys., błąd arytmetyczny --> | B8: ok. 208 tys. zł/miejsce (obiekt samodzielny, 4 poziomy, centrum Warszawy) | [W] → [Z], zgodne z B8 |
| Ściany szczelinowe 60–80 cm (m² ściany) | 1 100 / **1 400** / 1 800 zł/m² | jawnej ceny nie znaleziono. Dolny punkt odniesienia: ścianka Larsena tymczasowa 400–750, stała 880–1 200 zł/m² brutto (8%) [W kb.pl (s)] | [Z]: zweryfikować ofertą firmy fundamentowej |
| Wykop z wywozem i utylizacją nasypów niebudowlanych | 60 / **80** / 110 zł/m³ | brak źródła. Nasypy do 3,8 m z gruzem ceglanym [O M.05] | [Z] |
| Płyta fundamentowa (z biała wanną, ok. 150 kg/m³ zbrojenia) | 1 200 / **1 400** / 1 650 zł/m³ | brak źródła | [Z] |
| Fasada wentylowana z okładziną ceramiczną / klinkierową (z podkonstrukcją, izolacją, montażem) | 1 150 / **1 450** / 1 800 zł/m² | system kompletny 600–1 200 zł/m² (oferteo.pl, 11.07.2025, sprawdzone) <!-- poprawione przez weryfikatora: było 550–1 200 -->; podkonstrukcja 90–200; ceramika 450–900 (materiał); montaż ceramiki 100–300; płytki klinkierowe 90–200+; wełna 50–95 zł/m² [W muratordom.pl, kb.pl (s), rozbicia nie weryfikowano] | [W] + narzut [Z] ×1,3–1,5 (budynek W, A1/A2, rusztowania, detale) |
| Okładzina kamienna (granit 3–4 cm na kotwach nierdzewnych, z izolacją) | 1 600 / **2 000** / 2 600 zł/m² | kamień elewacyjny 150–600 zł/m² + montaż 100–150 zł/m² (2025) [W oferteo.pl (s)] | [W] + [Z] |
| Okna aluminiowe 3-szybowe w elewacji otworowej | 1 500 / **1 800** / 2 200 zł/m² | okna 3-szybowe 700–1 300 zł/m² (11.02.2025; bez informacji o montażu) [W globenergia.pl]; okna alu z pakietem 3-szybowym z montażem 800–1 600, trudny montaż 1 200–1 900 zł/m² (brutto z VAT 8%, akt. 07.01.2026) [W kb.pl] <!-- poprawione przez weryfikatora: dopisano status VAT i daty -->; Aluprof: +5% na ciepłe profile od 1.02.2025 [O producent: aluprof.com, pismo dyr. handlowego] | [W] + [Z] |
| Ściana słupowo-ryglowa (szkło 3-szybowe, przeciwsłoneczne) | 2 300 / **2 800** / 3 500 zł/m² | brak jawnej ceny fasad | [Z] |
| BIPV elewacyjne (szkło-szkło, z podkonstrukcją) | 1 900 / **2 400** / 3 000 zł/m²; wydajność [Z] ≈ 0,15 kWp/m² | brak jawnej ceny | [Z] |
| Przesłony stałe / lamele (ceramiczne, alu) | 500 / **800** / 1 200 zł/m² | brak | [Z] |
| Dach płaski: izolacje termiczne i przeciwwodne | 350 / **450** / 600 zł/m² | brak | [Z] |
| Dach zielony ekstensywny (z izolacjami) | 550 / **700** / 900 zł/m² (dopłata za zieleń ≈ 150–350) | 150–350 zł/m², z matami rozchodnikowymi >400 zł/m² [W muratordom.pl (s)]; tani wariant 100–160 zł/m² bez hydroizolacji [W prawo.pl (s)] | [W] |
| Dach intensywny / taras użytkowy (z izolacjami) | 900 / **1 200** / 1 600 zł/m² | 400–1 000 zł/m², ogród dachowy 1 200–1 500 zł/m² [W muratordom.pl (s)]; sama robocizna 347 zł/m² (2026) [W cenauslug.pl (s)] | [W] |
| PV dachowe (BIPV pokrycia dachu dominanty) | 3 500 / **4 000** / 5 000 zł/kWp | instalacja ok. 50 kWp: 145,9–183 tys. zł netto, średnio **3 333 zł/kWp netto** [W globenergia.pl, artykuł z **10.09.2021**, czyli sprzed spadku cen modułów w latach 2023–2024; jako punkt odniesienia dla 2026 r. nieaktualny] <!-- poprawione przez weryfikatora: dopisano rok źródła -->; 2 000–4 000 zł/kWp netto dla firm [W enerad.pl (s)] | [W] + dopłata BIPV [Z] |
| Magazyn energii elektrycznej | 1 600 / **2 200** / 3 000 zł/kWh | brak | [Z] |
| GPC: odwierty pionowe z sondą | 190 / **240** / 300 zł/mb | woj. dolnośląskie: z sondą i materiałem średnio 178 zł/mb netto (192 brutto), bez sondy 90 zł/mb netto [W kb.pl, 29.04.2026]; średnio 302 zł/mb (16.06.2026), zakres 263–380, Warszawa 380, **bez materiałów** [W cenauslug.pl]; 165–274 zł/mb z sondą (brutto z VAT 8%) [W muratordom.pl 2026] <!-- poprawione przez weryfikatora: wartość „duże miasta 190–230 zł/mb netto” nie występuje na wskazanej stronie kb.pl --> | [W] |
| GPC: pompy ciepła, maszynownia, hydraulika źródła (≈ 0,7–1,0 MW) | 1,8 / **2,5** / 3,5 mln zł | brak | [Z] |
| Długość odwiertów (ilość) | **14 400 mb** (np. 120 × 120 m) | M.12 wymaga analizy liczby i głębokości [O] | [Z]: do analizy energetycznej |
| Instalacje: woda+kanal.+CO+wentylacja z odzyskiem+chłód | ≈ 1 200 zł/m² PC nadz. (mid; poz. 7.1–7.7) | brak | [Z] |
| Instalacje elektryczne podstawowe / teletechnika | 520 / 345 zł/m² PC (mid) + pozycje kpl | brak | [Z] |
| AV: sala Sejmiku (głosowanie imienne, transmisja, PJM, pętle indukcyjne) + centrum konferencyjne | 2,5 / **4,0** / 6,0 mln zł | przetargów nie znaleziono (limit wyszukiwań). Głosowania jawne na sesjach sejmiku odbywają się za pomocą urządzeń utrwalających imienny wykaz głosowań (ustawa o samorządzie województwa, rozdz. 3; lexlege.pl (s), numeru artykułu nie weryfikowano) | [Z] |
| Sala Sejmiku: amfiteatr, stanowiska stałe, akustyka | 1,2 / **2,0** / 3,0 mln zł | brak | [Z] |
| Dźwigi osobowe (budynek 35–45 m, w tym dla ekip ratowniczych) | 0,45 / **0,60** / 0,80 mln zł/szt. | brak | [Z] |
| Nawierzchnie z kamienia naturalnego (płyty / kostka granitowa z podbudową) | 700 / **900** / 1 200 zł/m² | sama robocizna układania kostki granitowej śr. **171,32 zł/m² brutto** [W kb.pl / cenauslug.pl (s)]; płyty granitowe (materiał) 90–1 100 zł/m² [W kb.pl (s)] | [W] + [Z] |
| Zieleń niska (w tym na stropie garażu) | 350 / **500** / 800 zł/m² | brak | [Z] |
| Drzewa duże z systemem korzeniowym (skrzynki, substrat strukturalny) | 10 / **18** / 30 tys. zł/szt. | brak | [Z] |
| Stacje ładowania EV | 25 / **35** / 50 tys. zł/szt. | brak | [Z] |
| Adaptacja garażu na MDS | 0,8 / **1,5** / 2,5 mln zł | wymóg PU (MDS w garażu; rozp. MSWiA z 9.07.2025) wg `20_program/program.md` | [Z] |
| Koszty stałe budowy (zaplecze, żurawie, ochrona, media, CAR) | 2 / **3** / 4% robót | ceny jednostkowe zawierają już koszty pośrednie (rozp. MRiT 2021 § 1) | [Z] |
| Rezerwa na nieprzewidziane | 3 / **5** / 7% | brak | [Z] |
| Kontekst (nie w modelu): fit-out biura, Warszawa | ≈ 1 275–1 313 €/m² | [R] Cushman & Wakefield, *Office Fit-out Cost Guide* (s) | — |

---

## 6. Uwarunkowania lokalne wpływające na koszt (fakty z materiałów → skutki)

| Uwarunkowanie | Fakt [O] | Skutek kosztowy (wniosek) |
|---|---|---|
| Woda gruntowa | Zwierciadło swobodne, miejscami naporowe, ustabilizowane 3,20–3,80 m p.p.t. (115,07–115,95 m n.p.m.), pomiar 1–3.09.2025, wahania ±0,5 m. „Stabilizujące się powyżej przypuszczalnego poziomu posadowienia” (M.05 s. 6, 12–13) | Szczelna obudowa wykopu (ściany szczelinowe zagłębione w gliny), biała wanna, płyta 1,0–1,2 m, kotwienie przeciw wyporowi poza obrysem nadziemia. Każda kondygnacja podziemna kosztuje więcej niż „na sucho” |
| Powódź i podtopienia | Strefa narażona na podtopienia od wód gruntowych (PIG); obszar narażony na niebezpieczeństwo powodzi rzecznej (Hydroportal) (M.05 s. 6) | Zabezpieczenia przeciwpowodziowe wjazdów i otworów garażu, pompownie, rzędna parteru. W modelu ujęte w rezerwie i w pozycjach 1.3 i 3.14* |
| Grunty | Nasypy niebudowlane do 2,8–3,8 m (gruz ceglany); niżej piaski holoceńskie do ok. 8,6 m; gliny plejstoceńskie, w tym warstwa plastyczna QpB3a; II kategoria geotechniczna, warunki złożone (M.05 s. 6–13) | Utylizacja nasypów (pozycja 1.4), możliwe zanieczyszczenia. Glina może posłużyć jako przesłona dla ścian szczelinowych, co ogranicza odwodnienie |
| Archeologia | Strefa ochrony archeologicznej; relikty piwnic kamienic (`30_lokalizacja/konserwator.md`, brief) | Badania i nadzór archeologiczny (pozycja 1.7*: 0,3–1,2 mln) oraz ryzyko harmonogramu |
| Sąsiedzi | WS 5 (okna w szczycie) i Mazowiecka 19 (przyleganie, zamurowanie okien) (F.01 zał. 3; brief) | Zabezpieczenie i monitoring (pozycja 1.8*: 0,6–2,5 mln). Ściany szczelinowe przy fundamentach sąsiadów, ewentualnie podbicia |
| Przyszły tunel / tramwaj pod Mazowiecką (MPZP §34, §37; K-02 w `30_lokalizacja/mpzp.md`) | Plan przewiduje podziemną ulicę i tramwaj | Ryzyko dla głębokości garażu przy zachodniej granicy. Wniosek: nie projektować podziemia poza obszarem inwestycji |
| Zakaz urządzeń technicznych na dachach (MPZP, brief) | — | Technika w bryle (piętro techniczne = PC bez PU, czyli koszt), PV jako pokrycie (BIPV), droższe niż PV na konstrukcji |
| PV 0,4–1,0 MWp (M.12) | dach dominanty i elewacje | Dach ≈ 0,2 MWp → ok. 1 300–1 400 m² BIPV na elewacjach |
| Budynek wysoki (W) 35–45 m | klasa „B”, klatki z przedsionkami, dźwig dla ekip ratowniczych, ochrona przed zadymieniem (`40_prawo/ppoz.md`) | Pozycje 9.12, 10.1, 5.2; droższa konstrukcja rdzenia i fasady (wiatr, A1/A2) |
| Sala Sejmiku na najwyższej kondygnacji w obszarze A | duża rozpiętość bez podpór, antresola (brief) | Konstrukcja stalowa / przekrycie (pozycja 3.9), ewentualnie strefa transferowa |

---

## 7. Metoda szacowania: parametryczny model kosztów

### 7.1 Zasada
Model jest **bottom-up w układzie F.14.B**: każdy wiersz to *ilość × cena jednostkowa*. Ilości pochodzą z modelu bryły albo ze współczynników przedmiarowych [Z]. Model kontroluje się **top-down**: suma podzielona przez PC musi mieścić się w paśmie z tab. B (7 400–9 300 zł/m² PC). Trzy poziomy:
- **low**: dolne ceny rynkowe, sprawna realizacja;
- **mid**: wartość do F.14.B;
- **high**: górna granica ryzyka.

Rozrzut low–high (−27% / +39% wokół mid) odpowiada dokładności typowej dla etapu koncepcji (wiedza ogólna).

```
K_realizacji = Σ_i (Q_i(geometria) × c_i)                ← grupy 1–15, 17, 18 (bez rezerwy)
             + KS × Σ                                     ← 16.1 koszty stałe budowy (2–4%)
             + REZ × (Σ + KS)                             ← 18.3* rezerwa (3–7%)
poziom cen: II kw. 2026, netto;   K(t) = K × (1 + i)^t   ← waloryzacja informacyjnie (i = 4–6%)
```

### 7.2 Dane wejściowe z modelu bryły (interfejs, klucze w `tools/koszty_model.py → REF`)

| Klucz | Znaczenie | Wartość referencyjna V1 |
|---|---|---|
| `A_nad` | PC nadziemna [m²] (PN-ISO 9836) | 14 000 |
| `A_pod` | PC podziemna [m²] | 3 900 (V2: 5 800) |
| `fp_pod`, `fp_nad` | obrys podziemia / zabudowy [m²] | 2 900 / 2 500 |
| `obw_pod`, `h_sz`, `h_wyk`, `h_pod` | obwód ścian szczelinowych [m], ich głębokość, głębokość wykopu, wysokość ścian podziemia | 220 / 15 / 6,0 / 4,0 (V2: 18 / 8,5 / 7,5) |
| `t_plyty`, `fp_wypor` | grubość płyty [m]; podziemie poza obrysem nadziemia [m²] | 1,1 / 400 |
| `fas_went`, `fas_kamien`, `fas_tynk`, `okna`, `fas_sr`, `fas_bipv`, `przeslony` | powierzchnie elewacji wg typu [m²] (netto, bez otworów, z wyjątkiem okien) | 3 800 / 600 / 0 / 2 400 / 800 / 400 / 1 200 (razem ok. 8 000 m² brutto elewacji ≈ 0,57 × A_nad) |
| `dach`, `dach_ext`, `dach_int` | dachy płaskie łącznie / w tym zielony ekstensywny / intensywny lub taras [m²] | 2 700 / 1 200 / 500 |
| `kwp_dach`, `kwh_bess`, `mb_odw` | PV dachowe [kWp], magazyn energii [kWh], odwierty [mb] | 200 / 250 / 14 400 |
| `n_klatek`, `n_kond_klatki`, `windy_os`, `windy_tow` | klatki, średnia liczba kondygnacji na klatkę, dźwigi | 3 / 8 / 6 / 1 |
| `A_teren`, `t_kam`, `t_ziel`, `drogi`, `drzewa`, `ev` | zagospodarowanie (działka bez zabudowy + skwer dz. 9/2 + pasy), nawierzchnie kamienne, zieleń, drogi [m²], drzewa, ładowarki [szt.] | 2 100 / 1 300 / 600 / 250 / 12 / 10 |
| `stal_kg`, `sciany_mobilne`, `bal_zew`, `bal_wew` | konstrukcje stalowe [kg], ścianki mobilne [m²], balustrady [mb] | 60 000 / 150 / 150 / 120 |

Współczynniki przedmiarowe [Z] (ilości liczone z PC, gdy brak danych z modelu):
- ściany żelbetowe 0,30 × PC;
- słupy 0,022 m³/m² PC;
- ścianki GK 0,85 × A_nad;
- ścianki szklane 0,10 × A_nad;
- sufit modułowy 0,55 × A_nad, GK 0,20, akustyczny 0,12;
- wykładzina 0,55 × A_nad;
- posadzki kamienne w holach 0,06 × A_nad;
- drzwi 1 szt./28 m² A_nad;
- posadzka żywiczna garażu 0,75 × A_pod.

Po wykonaniu rzutów trzeba je zastąpić ilościami z rysunków. Spójność z F.15.A–C jest wymagana (lista kontrolna etapu II, R-217).

### 7.3 Wyniki (II kw. 2026, netto, mln zł, z kosztami stałymi i rezerwą)

| Wariant | low | **mid** | high | mid: zł/m² PC | mid: II kw. 2027 (+5%) |
|---|---|---|---|---|---|
| **V1** – A_nad 14 000, A_pod 3 900 (1 kond. + częściowa −2) | 107,3 | **146,3** | 203,3 | 8 174 | 153,6 |
| **V2** – A_nad 14 000, A_pod 5 800 (2 pełne kondygnacje, M.01) | 112,0 | **152,4** | 211,3 | 7 696 | 160,0 |
| **V1b** – A_nad 13 000 (fasada proporcjonalnie mniejsza), A_pod 3 900 | 103,4 | **141,4** | 196,7 | 8 364 | 148,4 |

Podział V1 mid na grupy F.14.B [mln zł]:

| Gr. | Nazwa | mln zł | Gr. | Nazwa | mln zł |
|---|---|---|---|---|---|
| 1 | Roboty przygotowawcze (z wykopem, ścianami szczelinowymi, archeologią, zabezpieczeniem sąsiadów) | 9,49 | 10 | Windy | 4,40 |
| 2 | Przyłącza, instalacje zewnętrzne, GPC, PV | 10,16 | 11 | Roboty wykończeniowe (z wyposażeniem stałym i salą Sejmiku) | 11,62 |
| 3 | Konstrukcja (z dachami) | 23,79 | 12 | Sufity | 2,51 |
| 4 | Stolarka zewnętrzna (z fasadami słupowo-ryglowymi) | 7,26 | 13 | Podłogi | 4,41 |
| 5 | Stolarka wewnętrzna | 1,84 | 14 | Balustrady | 0,84 |
| 6 | Elewacja | 8,63 | 15 | Zagospodarowanie terenu | 3,99 |
| 7 | Instalacje sanitarne | 20,63 | 16 | Koszty stałe budowy | 4,06 |
| 8 | Instalacje elektryczne | 12,30 | 17 | Rozwiązania proekologiczne (woda szara) | 0,70 |
| 9 | Instalacje teletechniczne (z AV) | 11,05 | 18 | Inne (MDS, zamurowanie okien Maz. 19, **rezerwa 6,97**) | 8,67 |
| | | | | **Razem** | **146,3** |

Wiersze ze szczegółami (ilość, j.m., cena jednostkowa, wartość) dla F.14.B daje polecenie: `python3 -I tools/koszty_model.py wejscie.json --rows mid`. Pozycje „*” to wiersze dopisywane w miejscu „….* inne”. Uwaga na zakresy SUM we wzorze xlsx (`formularze_tabele.md` 2.3 pkt 6).

### 7.4 Wrażliwość (mid, zmiana kosztu całkowitego z KS i rezerwą)

| Decyzja projektowa | Δ koszt |
|---|---|
| +1 000 m² PC nadziemnej (z przyrostem fasady o ok. 480 m²) | **+4,9 mln zł** |
| druga pełna kondygnacja podziemna (3 900 → 5 800 m², głębsze ściany i wykop) | **+6,1 mln zł** (realnie 6–9 mln, p. 7.5) |
| 1 000 m² okładziny ceramicznej → ściana słupowo-ryglowa | +1,5 mln zł |
| 1 000 m² okładziny ceramicznej → BIPV (+ ok. 150 kWp) | +1,0 mln zł |
| 1 000 m² BIPV jako dodatkowa powierzchnia | +2,6 mln zł |
| 500 m² dachu ekstensywnego → intensywny / taras | +0,3 mln zł |
| +5 000 mb odwiertów | +1,3 mln zł |
| AV i sala Sejmiku: high zamiast mid | +3,0 mln zł |

### 7.5 Kontrola krzyżowa i znane słabości modelu
- **Top-down:** V1 mid daje 8 174 zł/m² PC, czyli środek pasma B (7 400–9 300). Wynik spójny. *Uwaga weryfikatora:* ta kontrola **nie jest niezależna**, bo stawki [Z] dobrano właśnie tak, by trafić w pasmo B (rozdz. 0.1). Spójność potwierdza tylko kalibrację, a nie poprawność cen. Samo pasmo opiera się na założeniach (B1: VAT i PC/PU; B3: archiwum o PU/PC ≈ 0,88). <!-- poprawione przez weryfikatora -->
- **Podziemie:** średnio zgodne z B8. V1 daje ok. 205 tys. zł/miejsce, V2 ok. 167 tys. zł/miejsce, a B8 ok. 208 tys. zł/miejsce. <!-- poprawione przez weryfikatora: było 220 / 180 tys. --> **Krańcowy koszt drugiej kondygnacji** to w modelu tylko ok. 3 200 zł/m², bo ściany obwodowe i płyta są wspólne. Przy większym wyporze, głębszym odwodnieniu i ryzyku gruntowym realnie może to być 3 200–4 700 zł/m², czyli +6–9 mln zł. *Wniosek:* jeżeli projekt zachowa 2 pełne kondygnacje, w F.14.B przyjąć poziom „high” dla wierszy 1.3, 1.4, 1.6* i 3.15*. To ok. +2 mln zł.
- **Wcześniejsze założenie programu** (`20_program/program.md` 12.4: nadziemie 8 000–10 000 zł/m², podziemie 4 500–6 000 zł/m², teren i przyłącza 4–8 mln, razem 142–183 mln) jest zgodne co do rzędu wielkości. Model zawęża środek do 141–152 mln (mid, z rezerwą 5%).
- **Stawki [Z] stanowią ok. 80–85% wartości** (pozycje z jakimkolwiek odniesieniem [W] w tab. E, nawet z narzutem [Z], to ok. 15% sumy V1 mid). <!-- poprawione przez weryfikatora: było „ok. 60%”, przeliczenie wierszy modelu --> Przed oddaniem F.14.B warto zweryfikować u kosztorysanta i 2–3 dostawców co najmniej: ściany szczelinowe, fasady (ceramika wentylowana, słupowo-ryglowa, BIPV), AV sali obrad, dźwigi i maszynownię GPC.

### 7.6 Jak zmieścić się w limicie z zapasem (wniosek, priorytety)
1. **PC nadziemna ≤ 13 500 m².** Środki: zwarta kondygnacja Sejmiku z antresolą, KW ≤ 25–30%, piętro techniczne zminimalizowane. Każde 1 000 m² to ok. 4,9 mln.
2. **Podziemie = minimum funkcjonalne** (103–110 miejsc + technika + MDS ≈ 3 800–4 000 m²). Drugą kondygnację ograniczyć do strefy technicznej i zbiorników, z uzasadnieniem w opisie (Reg. II.2). Oszczędność wobec M.01: 6–10 mln.
3. **Fasada:** ceramika wentylowana jako tło (rytm segmentów 12–20 m wg DWKZ), przeszklenia ≤ 40% elewacji. Słupowo-ryglowa tylko w holu i sali Sejmiku. BIPV jako **zamiennik** okładziny w spandrelach dominanty, a nie dodatkowa warstwa.
4. **Zero-emisyjność „systemowa, nie gadżetowa”:** GPC z odwiertami pod budynkiem (wykonanymi przed płytą), pole sond jako magazyn sezonowy (BTES) zamiast osobnego zbiornika, BESS o rozsądnej pojemności (ok. 250 kWh). Wniosek; zgodne z M.12 pkt C, D.
5. **Rezerwa 5% pokazana jawnie w grupie 18.** Pozwala bronić tezy o realności (R2) bez „zaniżania”. Wariant docelowy: **V1b mid ≈ 141 mln zł netto** (zapas ok. 9 mln = 6%).

---

## 8. Koszt Dokumentacji (≤ 5,4%)

Rozp. MRiT z 20.12.2021 (Dz.U. 2021 poz. 2458), załącznik, tabela 1 [O]: planowane koszty prac projektowych WPP = W% × WRB. Wartość W% interpoluje się liniowo (pkt I.3). Nie obejmuje ona danych wyjściowych: map, geologii, inwentaryzacji, operatów (§ 10 ust. 5).

| WRB [tys. zł] | kat. IV | kat. V | kat. VI |
|---|---|---|---|
| 100 000 | 4,30% | 5,30% | 6,30% |
| 200 000 | 3,90% | 4,80% | 5,70% |
| **150 000 (interpolacja)** | **4,10% → 6,15 mln** | **5,05% → 7,57 mln** | **6,00% → 9,00 mln** |

Klasyfikacja wg tabeli 2 [O]:
- „siedziby władz wojewódzkich, ratusze”: kategoria **IV**, z możliwością podwyższenia do V lub VI przy wymaganiach większych niż podstawowe;
- „budynki biurowe ze specjalnymi wymaganiami (np. prestiżowe siedziby instytucji)”: **VI**;
- „budynki biurowe … średnio wysokie i wysokie (do 55 m), z garażami”: IV z możliwością V.

Fazy wg § 10 ust. 6: koncepcja 7–15%, PB 30–45%, PW 40–60%.

**Wniosek:**
- Limit 5,4% (8,1 mln) obejmuje całą usługę z F.01, w tym nadzór autorski (7%) i doradztwo (1%). Dla projektów zostaje ok. 92%, czyli ok. **4,97%**. To poziom kategorii V, właściwy dla budynku wysokiego, wielofunkcyjnego, z salą obrad i systemami M.12.
- Zalecana deklaracja w F.14.B: **ok. 7,5–7,9 mln zł netto** (5,0–5,3% limitu, poniżej górnej granicy).
- Przykład dla 7,8 mln: E1 0,936 / E2 2,340 / E3 0,780 / E4 3,120 / E5 0,078 / E6 0,546 mln zł netto.
- Regulamin liczy 5,4% od kwoty netto, więc wynik przyjmować jako netto. Jeżeli zespół chce zabezpieczyć się przed interpretacją „8,1 mln brutto”, granica netto wynosi 6,59 mln (8,1/1,23). Ta kwota wciąż mieści się powyżej kategorii IV (6,15 mln).
- **Pamiętać o błędzie wzoru:** H163/H164 trzeba nadpisać wartościami (`formularze_tabele.md` 2.3 pkt 1).

---

## 9. Zalecenia do wypełnienia F.14.B (wniosek)

1. W nagłówku lub przypisie wpisać: „Ceny netto, poziom cen II kw. 2026, Wrocław; ceny jednostkowe z narzutami; koszty stałe budowy w gr. 16; rezerwa 5% w gr. 18; bez waloryzacji do terminu realizacji”.
2. W kolumnie pomocniczej poza obszarem wydruku (J) podać ceny jednostkowe, a w F wpisać formułę D × J. W H uzupełnić formuły `=F*(1+G)`.
3. Stawki VAT: zostawić 23% oraz 8% tam, gdzie wpisał je wzór (7.8 i 15.7). Uzupełnić brakujące VAT i j.m. (2.12, 2.13, 5.2, 7.9, 8.17, 15.10, 17.1), zgodnie z `formularze_tabele.md`. Kwestię 8% w poz. 7.8 zasygnalizować, bo budzi wątpliwość podatkową.
4. Unikać podwójnego liczenia. Rekuperację (17.1) wpisać jako „ujęta w 7.6”. BIPV elewacyjne wpisać w 6.5*, a PV dachowe w 2.13. Magazyn energii elektrycznej wpisać w 8.17, a bufory ciepła w 7.9. Retencja należy do 15.10, a woda szara do 17.2*.
5. W grupie 18 ująć osobno: MDS, zamurowanie okien Mazowieckiej 19, rezerwę. Zabezpieczenie sąsiadów (1.8*) i archeologię (1.7*) ująć w grupie 1. Wyposażenie ruchome i meble nie należą do „stanu wykończonego”, więc trzeba to wyraźnie zaznaczyć w opisie.
6. Liczby muszą być spójne z F.15.C: m² dachów zielonych (I.13) = 3.12 + 3.13*; PC, PU, liczba miejsc postojowych. Spójność dotyczy też opisu i rysunków (R-217).
7. W opisie (1/2 strony A4) podać: metodę, pasmo benchmarków (zł/m² PC i zł/m² PU z definicją PU), rezerwę, ryzyka (woda gruntowa, archeologia, waloryzacja) i koszty eksploatacji (GPC+PV, czyli niskie opłaty za energię). Koszty eksploatacji są elementem kryterium drugorzędnego (R5).

---

## 10. Ryzyka i krytyczna ocena danych

- **Duży udział [Z].** Model jest spójny z pasmem rynkowym, ale jego struktura (podział między grupy) nie ma jawnego źródła cen elementowych. Przy ocenie przez eksperta wiarygodność zależy od spójności przedmiaru, a nie od pojedynczych stawek.
- **Benchmarki prasowe.** Status VAT jest często nieznany (B1, B4, B5, B6), a definicje PU są różne. Najważniejszy analog B1 ma interpretację „brutto” niezweryfikowaną bezpośrednio. Gdyby kwota 124,3 mln była netto, pasmo przesunęłoby się w górę do ok. 9 600–11 400 zł/m² PC, a model V1 mid byłby **niedoszacowany**. *Wniosek:* przed złożeniem pracy sprawdzić ogłoszenie o udzieleniu zamówienia (BZP/TED) dla Świętojerskiej 9.
- **Poradniki cenowe [W]** (fasady, dachy zielone, PV, odwierty, kostka) opisują rynek domów jednorodzinnych. Stawki dla budynków publicznych są systematycznie wyższe. Zastosowano narzut, ale jego wartość to [Z].
- **Przyspieszenie cen w 2026 r.** (+6,9% r/r we wrześniu) przy prognozach 2,5–3,5% [R] pokazuje, że prognozy konsultantów są niepewne. Wynik mid ma ważność ok. 6–12 miesięcy.
- **Ryzyka techniczne:** woda gruntowa i wypór, nasypy (możliwe zanieczyszczenia), archeologia, wpływ na kamienice sąsiednie, przyszły tunel pod Mazowiecką. Wszystkie działają w górę. Rezerwa 5% pokrywa je tylko częściowo.

---

## 11. Źródła (dostęp: 2026-11-16)

**Oficjalne [O]**
1. GUS, *Sytuacja społeczno-gospodarcza kraju w 2025 r.*: https://ssgk.stat.gov.pl/Sytuacja_społeczno-gospodarcza_kraju_2025.pdf
2. GUS, komunikat w sprawie zmian cen produkcji budowlano-montażowej w II kw. 2026 r.: https://stat.gov.pl/sygnalne/komunikaty-i-obwieszczenia/lista-komunikatow-i-obwieszczen/komunikat-w-sprawie-zmian-cen-produkcji-budowlano-montazowej-w-drugim-kwartale-2026-r-,266,51.html
3. GUS, *Price indices of construction and assembly production in July 2026*: https://publikacje.new.stat.gov.pl/en/publications-portal/price-indices-construction-and-assembly-production-july-2026
4. GUS, *Wskaźniki cen produkcji budowlano-montażowej we wrześniu 2026 r.* (20.10.2026): https://stat.gov.pl/obszary-tematyczne/ceny-handel/wskazniki-cen/wskazniki-cen-produkcji-budowlano-montazowej-we-wrzesniu-2026-r-,15,94.html
5. GUS, *Ceny robót budowlano-montażowych i obiektów budowlanych – wrzesień 2025* (PDF, tabl. 1–2): https://stat.gov.pl/obszary-tematyczne/ceny-handel/ceny/ceny-robot-budowlano-montazowych-i-obiektow-budowlanych-wrzesien-2025-r-,5,164.html
6. Rozporządzenie MRiT z 20.12.2021 w sprawie określenia metod i podstaw sporządzania kosztorysu inwestorskiego, obliczania planowanych kosztów prac projektowych…, Dz.U. 2021 poz. 2458: https://api.sejm.gov.pl/eli/acts/DU/2021/2458/text/O/D20212458.pdf
7. Urząd Marszałkowski Województwa Mazowieckiego, „Nowe siedziby Sejmiku Województwa Mazowieckiego i Sądu Apelacyjnego w Warszawie” (9.04.2026): https://mazovia.pl/pl/dla_mediow/informacje_prasowe/nowe-siedziby-sejmiku-wojewodztwa-mazowieckiego-i-sadu-apelacyjnego-w-warszawie.html
8. wroclaw.pl, „Na terenie byłego targowiska Zielińskiego powstanie gmach Sądu Apelacyjnego” (29.06.2021): https://www.wroclaw.pl/przedsiebiorczy-wroclaw/na-terenie-bylego-targowiska-zielinskiego-powstanie-gmach-sadu-apelacyjnego
9. TED 328918-2022 (zamawiający: Sąd Okręgowy w Krakowie; roboty budowlane w zakresie budynków sądowych, PL214; publ. 20.06.2022; wartość 73 784 488 zł; potwierdzone przez API TED: https://api.ted.europa.eu/v3/notices/search, zapytanie publication-number=328918-2022): https://ted.europa.eu/en/notice/328918-2022/pdf <!-- poprawione przez weryfikatora -->
10. Warszawa 19115, „Parkingi podziemne”: https://warszawa19115.pl/-/parkingi-podziemne
11. samorzad.gov.pl, powiat polkowicki, „Umowa na budowę komendy podpisana” ((s)): https://samorzad.gov.pl/web/powiat-polkowicki/umowa-na-budowe-komendy-podpisana
12. Aluprof, pismo Dyrektora Handlowego (cennik od 1.02.2025): https://aluprof.com/files/documents/Pismo_Dyrektora_Handlowego.pdf
13. Materiały konkursowe (lokalnie): Regulamin (`00_materialy/tekst/2_Regulamin_Konkursu-sig.txt`), Wyjaśnienia nr 20, F.01, F.14.B (txt i xlsx), M.05 Opinia geotechniczna, M.12 Standard zero-emisyjności; opracowania zespołu w `docs/10_regulamin`, `20_program`, `30_lokalizacja`.

**Raporty [R]**
14. Arcadis, *International Construction Costs 2025*: https://images.connect.arcadis.com/Web/Arcadis/%7B508ee8f9-5a5a-4660-8268-dd312b604ec2%7D_International-Construction-Costs-2025.pdf
15. Arcadis, *International Construction Costs 2026 – White Paper*: https://images.connect.arcadis.com/Web/Arcadis/%7Bc927075d-3e7f-4f72-99be-26cd39802d79%7D_International_Construction_Costs_2026_White_Paper_Report.pdf
16. Turner & Townsend, *Global Construction Market Intelligence 2025 – Europe* ((s)): https://publications.turnerandtownsend.com/global-construction-market-intelligence-2025/europe
17. Cushman & Wakefield, *Office Fit-out Cost Guide* ((s)): https://www.cushmanwakefield.com/pl-pl/poland/insights/office-fit-out-cost-guide

**Wtórne [W]**
18. inzynierbudownictwa.pl, „W Warszawie rusza budowa nowych siedzib Sejmiku Mazowsza i Sądu Apelacyjnego” (14.04.2026): https://inzynierbudownictwa.pl/w-warszawie-rusza-budowa-nowych-siedzib-sejmiku-mazowsza-i-sadu-apelacyjnego/
19. wnp.pl (9.04.2026): https://www.wnp.pl/rynki/warszawa-podpisano-umowe-na-budowe-siedzib-sejmiku-wojewodztwa-mazowieckiego-i-sadu-apelacyjnego,1050701.html
20. propertydesign.pl (13.04.2026): https://www.propertydesign.pl/architektura/104/w_centrum_warszawy_buduja_gmachy_panstwowe_za_240_mln_inwestycja_wymaga_wyburzenia_szkoly,54105.html
21. nowawarszawa.pl (10.07.2025): https://nowawarszawa.pl/nowy-kompleks-administracyjno-sadowy-przy-swietojerskiej-coraz-blizej-rusza-przetarg-na-realizacje-projektu-projekt-praga/
22. biznesradar.pl, „Dekpol Budownictwo wybrany do budowy siedziby komendy policji w Katowicach” (31.12.2025): https://www.biznesradar.pl/a/142527,dekpol-budownictwo-wybrany-do-budowy-siedziby-komendy-policji-w-katowicach
23. investmap.pl, „Rusza budowa nowej siedziby KMP w Katowicach” (25.05.2026): https://investmap.pl/rusza-budowa-nowej-siedziby-komendy-miejskiej-policji-w-katowicach.a318051
24. eurobuildcee.com, „Mają kontrakt na Archiwum” (19.07.2024): https://eurobuildcee.com/news/58979-maja-kontrakt-na-archiwum
25. mota-engil-ce.eu, „MECE will build the headquarters of the Masovian Voivodeship Archive”: https://mota-engil-ce.eu/news/mece-will-build-the-headquarters-of-the-masovian-voivodeship-archive,news,58,394
26. forsal.pl, „Budimex ma umowę na budowę Centrum Administracyjnego w Ciechanowie” (2.07.2021): https://forsal.pl/biznes/aktualnosci/artykuly/8202443,budimex-ma-umowe-na-budowe-centrum-administracyjnego-w-ciechanowie.html
27. inzynierbudownictwa.pl, „Urząd miasta w Lublinie będzie miał nową siedzibę” (2021): https://inzynierbudownictwa.pl/urzad-miasta-w-lublinie-bedzie-mial-nowa-siedzibe/
28. Budimex, „Budimex will build a conference centre and the seat of the Marshal's Office in Lublin” (12.03.2014): https://www.budimex.pl/en/press/budimex-will-build-a-conference-centre-and-the-seat-of-the-marshals-office-in-lublin <!-- poprawione przez weryfikatora: zamiast domeny testowej bdm-stg.mda.pl -->
29. radiokrakow.pl: przetarg na budowę UM za 240 mln (2018) https://www.radiokrakow.pl/aktualnosci/krakow/przetarg-na-budowe-urzedu-marszalkowskiego-za-240-milionow-zlotych ; unieważnienie (2019) https://www.radiokrakow.pl/aktualnosci/krakow/przetarg-na-budowe-ratusza-marszalkowskiego-zostal-uniewazniony/ ; Wieliczka https://radiokrakow.pl/aktualnosci/krakow/w-wieliczce-powstanie-nowa-siedziba-sadu-rejonowego-i-prokuratury
30. radio.lublin.pl, Starostwo w Białej Podlaskiej (15.03.2024): https://radio.lublin.pl/2024/03/starostwo-bedzie-miec-nowoczesny-budynek-stary-ma-pojsc-do-rozbiorki
31. eurobuildcee.com, „Zaparkujemy pod placem Powstańców Warszawy” (3.08.2022): https://eurobuildcee.com/news/52827-zaparkujemy-pod-placem-powstancow-warszawy ; auto-swiat.pl (420 miejsc): https://www.auto-swiat.pl/wiadomosci/aktualnosci/duzy-parking-otwarty-w-samym-centrum-warszawy-znamy-cennik/zhq5fr8
32. Poradniki cenowe ((s), strony nieotwierane bezpośrednio): kb.pl (ścianki Larsena; płyty elewacyjne; okna aluminiowe; odwierty; kostka granitowa), muratordom.pl (elewacja klinkierowa 2025; zielony dach; odwierty 2026), oferteo.pl (elewacja wentylowana vs tynk 2025; kamień na elewację 2025), globenergia.pl (PV ok. 50 kWp; okna 2025; GUS VII 2022), enerad.pl (PV dla firm), cenauslug.pl (dach intensywny 2026; odwierty 2026), prawo.pl (zielony dach), money.pl (koszt miejsca postojowego), rynekpierwotny.pl (ceny miejsc postojowych V 2026), blog.ongeo.pl (GUS 2023). Adresy: https://kb.pl/cenniki/uslugi/cennik-scian-oporowych-ile-kosztuja-scianki-szczelne-larsena/ ; https://kb.pl/cenniki/produkty/okna-aluminiowe/ ; https://kb.pl/cenniki/miejskie/odwierty-pionowe/dolnoslaskie/ ; https://kb.pl/cenniki/ukladanie-kostki-granitowej ; https://muratordom.pl/budowa/dach/zielony-dach-ile-kosztuje-ekologiczny-hit-architektury-aa-1FzB-vE1a-8AEZ.html ; https://muratordom.pl/instalacje/pompy-ciepla/ile-kosztuje-odwiert-pod-pompe-ciepla-ceny-2026-w-calej-polsce-aa-G6Hz-Mus9-7ic4.html ; https://www.oferteo.pl/artykuly/elewacja-wentylowana-vs-tynk-ktora-technologie-elewacji-wybrac ; https://www.oferteo.pl/artykuly/kamien-na-elewacje ; https://globenergia.pl/ile-kosztuje-instalacja-fotowoltaiczna-o-mocy-ok-50-kwp-w-zaleznosci-od-lokalizacji-przeglad-ofert/ ; https://globenergia.pl/ile-kosztuje-wymiana-okien-w-2025-roku-kiedy-oplaca-sie-je-wymienic/ ; https://enerad.pl/fotowoltaika-dla-firm-oplacalnosc-i-finansowanie/ ; https://cenauslug.pl/budowa-i-remont/wykonanie-dachu-zielonego-intensywnego ; https://cenauslug.pl/budowa-i-remont/odwierty-pionowe-pod-pompy-ciepla ; https://www.money.pl/gospodarka/miejsce-postojowe-w-hali-garazowej-ile-kosztuje-i-czy-oplaca-sie-w-nie-zainwestowac-pod-wynajem-6429354921117825a.html ; https://www.blog.ongeo.pl/w-grudniu-2023-budowa-budynkow-wzrosla ; https://globenergia.pl/ceny-produkcji-budowlano-montazowej-wzrosly-o-134-proc-w-lipcu-2022-r/

**Odrzucone lub bez wartości cenowej:**
- Sekocenbud, *BCO cz. Ia – opisy obiektów* (III kw. 2025), https://sekocenbud.pl/public/BZ/2025/2025k3/BCO_cz1a_2025k3_dodatek_opisy.pdf: zawiera tylko opisy, bez cen. Użyto jedynie zasady, że wskaźniki BCO cz. I nie obejmują zagospodarowania, przyłączy ani kosztów dodatkowych.
- trojmiasto.pl (biurowiec Urzędu Marszałkowskiego Woj. Pomorskiego ze schronem): HTTP 403, nie wykorzystano.
- lublin.eu (przetarg ul. Leszczyńskiego): HTTP 503; dane wzięto ze źródła 27.
