# R6 — Energia i instalacje sanitarne: rejestr wymagań dla „Dom LAMELA”

Wersja: 1.0 (2026-09-25). Zespół R6.

**Zakres:**
* charakterystyka energetyczna (metodologia, EP, wymagany zakres projektu);
* fizyka budowli: normy obliczeniowe U, ψ, f_Rsi, obciążenie cieplne;
* wentylacja z odzyskiem ciepła;
* woda i c.w.u., kanalizacja, wody opadowe;
* pompa ciepła: F-gazy, hałas, montaż;
* instalacja PV: próg ppoż.

**Data weryfikacji stanu prawnego: 2026-09-25.** Wykaz Dz.U. 2026 w API ELI sprawdzono do poz. 1244 (23.09.2026).

**Metoda:**
* Akty prawne pobrano z API ELI Sejmu (metadane, status, powiązania, PDF przez pymupdf).
* Rozporządzenia UE pobrano z EUR-Lex (PDF). Przy blokadzie WAF użyto tekstu na legislation.gov.uk (wersja „retained”, zgodna z pierwotną).
* Status norm sprawdzono w wyszukiwarce PKN (`wiedza.pkn.pl`, skrypt `pkn_r6.py`, wyniki w `pkn_r6.json` i `pkn_r6b.json`).
* Treść norm jest płatna. Liczby z norm potwierdzano w próbkach ISO (iTeh), w publikacjach naukowych, podręcznikach, u przedsiębiorstw wodociągowych i producentów.

**Pliki robocze:** `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R6/`, m.in.:
* `t_2015_376.txt` — metodologia;
* `t_2023_697.txt`;
* `t_2024_101.txt` / `ucheb_tj.txt` — ustawa o charakterystyce energetycznej;
* `fgas_pl.txt`;
* `aquanet_c.txt`;
* `pw_2025_960.txt`;
* `pkn_r6*.json`;
* `br443.txt`;
* `iso6946_s.txt`.

**Oznaczenia:**
* **P** — źródło pierwotne: tekst aktu z Dz.U. lub Dz.Urz. UE, katalog PKN, oficjalna próbka normy ISO.
* **W** — źródło wtórne: publikacja naukowa lub branżowa, wytyczne przedsiębiorstwa wodociągowego, materiały producenta.
* **NIEZWERYFIKOWANE** — brak potwierdzenia w dostępnym źródle.

**Skróty:**
* **WT** — rozporządzenie MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie; t.j. Dz.U. 2022 poz. 1225, zm. 2023 poz. 2442, 2024 poz. 474 i 726. **Status WT wymaga potwierdzenia przez zespół R3.** W ELI akt ma status „uznany za uchylony”, repealDate 2026-09-21. WT stosujemy na podstawie art. 102a PB (oświadczenie inwestora) — patrz R1 i R3.
* **Metodologia** — rozporządzenie MIiR z 27.02.2015 w sprawie metodologii wyznaczania charakterystyki energetycznej budynku lub części budynku oraz świadectw charakterystyki energetycznej, Dz.U. 2015 poz. 376, zm. 2017 poz. 22, 2019 poz. 1829, 2023 poz. 697.
* **UChEB** — ustawa z 29.08.2014 o charakterystyce energetycznej budynków, t.j. Dz.U. 2024 poz. 101.
* **RPB** — rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, t.j. Dz.U. 2022 poz. 1679, zm. 2023 poz. 2405, 2024 poz. 473, 2026 poz. 597.
* **PB** — Prawo budowlane, t.j. Dz.U. 2026 poz. 524 ze zm.
* **POŚ-hałas** — rozporządzenie MŚ w sprawie dopuszczalnych poziomów hałasu w środowisku, t.j. Dz.U. 2014 poz. 112.
* **F-gas** — rozporządzenie (UE) 2024/573.

---

## 1. Streszczenie

1. **Metodologia EP: obowiązuje rozporządzenie Dz.U. 2015 poz. 376.** Nowego aktu nie wydano.
   * Ostatnia zmiana to Dz.U. 2023 poz. 697, w mocy od 28.04.2023. W ELI akt ma status „obowiązujący” i nie ma późniejszych aktów zmieniających.
   * Akt wydano na podstawie art. 15 UChEB, a nie art. 7 PB. Wygaśnięcie WT (art. 66 ustawy o dostępności) go nie dotyczy.
   * Projekt nowej metodologii z klasami A+–G (2024, zapowiadany na 01.01.2026) **nie został ogłoszony** do Dz.U. 2026 poz. 1244.
2. **Współczynniki w_i od 28.04.2023:**
   * energia elektryczna z sieci systemowej **w_el = 2,50** (wcześniej 3,00);
   * energia słoneczna, wiatrowa i geotermalna wytwarzana miejscowo **w = 0,00**;
   * biomasa 0,20; paliwa kopalne miejscowo 1,10.

   Wartości od dostawcy mają pierwszeństwo przed tabelą. Metodologia nie przewiduje „zaliczenia” energii z PV oddanej do sieci. W literaturze (Chwieduk, PW 2016) z w = 0 liczy się tylko energię PV zużytą przez systemy techniczne budynku.
3. **EP_max dla budynku mieszkalnego jednorodzinnego:** EP_H+W = **70 kWh/(m²·rok)** + ΔEP_C + ΔEP_L. Wartość obowiązuje od 31.12.2020.
   * ΔEP_C = 5·A_f,C/A_f, gdy budynek ma instalację chłodzenia; w przeciwnym razie 0.
   * ΔEP_L = 0.

   Źródło: WT § 329 ust. 1–2. **W latach 2023–2024 nie wprowadzono dodatkowych wymagań energetycznych w WT.** Zmiany 2023 poz. 2442 oraz 2024 poz. 474 i 726 nie dotyczą Działu X ani zał. 2. Wymóg A0max usunięto już wcześniej (zob. R3).
4. **Wymóg analizy alternatywnych systemów zaopatrzenia w energię nadal obowiązuje** — RPB § 20 ust. 1 pkt 10, część opisowa PAB.
   * Analiza obejmuje: szacunek rocznej energii użytkowej, dostępne nośniki, porównanie 2 systemów (konwencjonalny vs alternatywny lub hybrydowy) i wybór.
   * Dodatkowo RPB § 20 ust. 1 pkt 11 wymaga analizy automatycznej regulacji temperatury w pomieszczeniach (WT § 135 ust. 7–10, § 147 ust. 5–7).
   * PT zawiera **charakterystykę energetyczną** (PB art. 34 ust. 3 pkt 3 lit. b; RPB § 23 pkt 11 lit. a–d).
   * Po budowie do zawiadomienia o zakończeniu budowy dołącza się **świadectwo charakterystyki energetycznej** sporządzone w centralnym rejestrze charakterystyki energetycznej budynków (UChEB art. 4 ust. 3; PB art. 57 ust. 1 pkt 6a). [Poprawka weryfikacji: pierwotnie „z CEEB” — CEEB to centralna ewidencja emisyjności budynków, inny rejestr.]
5. **UChEB:** tekst jednolity Dz.U. 2024 poz. 101. Po t.j. nie było zmian; ostatni akt zmieniający to Dz.U. 2023 poz. 1762.
   * **Dyrektywa EPBD (UE) 2024/1275** (termin transpozycji 29.05.2026) **nie została transponowana** — brak aktu w Dz.U.
   * Kierunek z EPBD na przyszłość: budynki zeroemisyjne od 2030 r.; instalacje słoneczne na nowych budynkach mieszkalnych do 31.12.2029.
6. **Domyślne sprawności w metodologii mocno obniżają wynik EP pompy ciepła.**
   * Wartości: η_H,g (PC powietrze/woda) = 2,60 przy 55/45 °C i 3,00 przy 35/28 °C; c.w.u. 2,60; η_W,d = 0,60 dla domu jednorodzinnego bez cyrkulacji.
   * Szacunek R6 dla A_f ≈ 250 m², EU_H = 35: przy wartościach tabelarycznych **EP ≈ 99 kWh/(m²·rok) > 70**.
   * Z danymi producenta (SCOP 4,5; COP_DHW 3,2) i rzeczywistą mocą urządzeń pomocniczych: **EP ≈ 58**.

   **Wniosek: do EP trzeba użyć deklarowanych danych producenta i zminimalizować straty c.w.u.** Q_W,nd wynosi normatywnie ≈ 24,1 kWh/(m²·rok) i dominuje w bilansie.
7. **Normy obliczeniowe — statusy w PKN na 2026-09-25:**
   * Aktualne: PN-EN ISO 6946:2017-10, 13370:2017-09, 10077-1:2017-10, 10211:2017-09, 14683:2017-09, 13789:2017-10 — wersje polskie. Aktualna jest też PN-EN ISO 13788:2013-05 (PL).
   * **PN-EN 12831-1:2017-08 istnieje tylko po angielsku.** W katalogu PKN nie znaleziono polskiego załącznika krajowego NA. Zastąpiła PN-EN 12831:2006.
   * **WT § 134 ust. 1 (zał. 1 lp. 16) powołuje wydania datowane z 2008 r. i PN-EN 12831:2006.** Obecnie są one wycofane.
   * Zał. 2 pkt 1.1 powołuje PN-EN ISO 6946 i 13370 bez daty, czyli wydania z 2017 r.
8. **Wentylacja:**
   * **PN-B-03430:1983/Az3:2000** jest wycofana w PKN bez zastępstwa. Pozostaje wiążąca, bo powołują ją WT § 147 ust. 1, § 149 ust. 1 i § 155 ust. 4 (zał. 1 lp. 26, 28, 33).
   * Wywiew (wtórne): kuchnia z kuchenką elektryczną 30 m³/h (≤ 3 osoby) / **50 m³/h (> 3 osoby)**; łazienka 50; WC 30; pomieszczenie pomocnicze bezokienne 15. Zalecenie okresowego zwiększenia do ≥ 120 m³/h.
   * Nawiew w mieszkaniu ≥ **20 m³/h na osobę** (WT § 149 ust. 1).
   * Odzysk ciepła ≥ 50% jest obowiązkowy dopiero od **500 m³/h** (WT § 151 ust. 1). LAMELA ma ok. 330 m³/h, więc obowiązek nie powstaje.
   * Dla central domowych obowiązuje ekoprojekt (UE) 1253/2014: SEC ≤ −20 kWh/(m²·a), obejście (bypass) termiczne, wielobiegowy napęd, sygnalizacja filtra.
   * Czerpnie i wyrzutnie: WT § 152 (m.in. czerpnia ≥ 2 m nad terenem, ≥ 8 m od ulic i wywiewek; na dachu ≥ 6 m od wywiewek).
9. **C.w.u.:** w punktach czerpalnych **55–60 °C**; możliwość dezynfekcji termicznej **70–80 °C** (WT § 120 ust. 2 i 2a).
   * W domu jednorodzinnym **cyrkulacja nie jest wymagana** (§ 120 ust. 1).
   * Pompa ciepła musi mieć dogrzewanie (grzałkę) do ≥ 70 °C w punktach.
   * Ocena ryzyka wewnętrznego systemu wodociągowego (nowe przepisy, Dz.U. 2026 poz. 605) **nie dotyczy budynków jednorodzinnych**.
10. **Woda — normy:**
    * PN-B-01706:1992 jest wycofana, ale wiąże przez WT § 113 ust. 4.
    * Seria PN-EN 806 jest aktualna: część 1 po polsku, części 2–5 po angielsku.
    * PN-EN 1717 ma nowe wydanie **PN-EN 1717+A1:2026-09** (EN). WT powołuje wydanie z 2003 r.
    * Ciśnienie przed punktem czerpalnym 0,05–0,6 MPa (WT § 114).
11. **Kanalizacja:**
    * PN-EN 12056-1…5:2002 (PL) są aktualne i powołane w WT § 122 ust. 2.
    * Piony wentylowane ponad dach. Zawory napowietrzające (PN-EN 12380:2005) dopuszczalne, jeśli ostatni pion na każdym przewodzie odpływowym i co piąty pion wyprowadzono ponad dach (WT § 125).
12. **Wody opadowe:**
    * PN-EN 12056-3 nie podaje natężenia deszczu dla PL. Zalecenia literaturowe: **r = 0,030–0,050 l/(s·m²)**.
    * Do retencji i rozsączania dla Poznania: **PANDa 2050 (RCP 4.5), C = 10 lat**, metoda bilansowa, f_b = 1,2, k_f,nn = 0,5·k_f. Źródło: Aquanet 2024.
    * Zbiornik chłonny: ≥ 1,5·h_fund + 0,5 m od fundamentów; dno ≥ 1 m nad maksymalnym zwierciadłem wody gruntowej.
    * DWA-A 138:2005 **zastąpiono DWA-A 138-1 (10/2024)**.
    * **Nierozstrzygnięte:** czy skrzynki rozsączające wymagają pozwolenia wodnoprawnego (Prawo wodne art. 16 pkt 65 lit. f i art. 389 pkt 6).
13. **F-gazy (UE) 2024/573, zał. IV pkt 8–9** (zakazy wprowadzania do obrotu):
    * Od **01.01.2027**: monobloki PC ≤ 12 kW z F-gazem o GWP ≥ 150 oraz split powietrze-woda ≤ 12 kW z GWP ≥ 150. R32 ma GWP 675, więc takie urządzenia nie mogą być wprowadzane do obrotu.
    * Od 2032 r. monobloki ≤ 12 kW bez F-gazów. Od 2035 r. splity ≤ 12 kW bez F-gazów.
    * **Rekomendacja: monoblok powietrze-woda na R290 (propan; GWP₁₀₀ = 0,02 wg IPCC AR6 — źródło wtórne, wartości nie ma w rozp. 2024/573).** Wymaga strefy bezpieczeństwa ok. 1 m (dane producentów, wtórne).
14. **Hałas pompy ciepła:**
    * Teren MN, „pozostałe obiekty”: **L_Aeq,D = 50 dB, L_Aeq,N = 40 dB** (POŚ-hałas, tab. 1 lp. 2a).
    * Ekoprojekt 813/2013: L_WA na zewnątrz ≤ 65 dB (≤ 6 kW), ≤ 70 dB (6–12 kW).
    * WT § 327 ust. 2–3: posadowienie antywibracyjne.
15. **PV:** **art. 56 ust. 1a PB uchylono** (ustawa Dz.U. 2025 poz. 1847). Obowiązki przeniesiono do **art. 29 ust. 4 pkt 3 lit. c PB**.
    * Powyżej **6,5 kW** potrzebne są: uzgodnienie projektu z rzeczoznawcą ppoż., zawiadomienie PSP i plan PV dla ekip ratowniczych.
    * „Moc zainstalowana elektryczna” PV to łączna moc znamionowa modułów z tabliczki (ustawa OZE art. 2 pkt 19b lit. b). **PV ≤ 6,5 kWp (DC) zwalnia z uzgodnienia.**

---

## 2. Rejestr wymagań

### 2.A Akty prawne — status i zakres projektu

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-01 | Metodologia wyznaczania charakterystyki energetycznej: **Dz.U. 2015 poz. 376**, status „obowiązujący”. Akty zmieniające: 2017 poz. 22, 2019 poz. 1829, 2023 poz. 697 (w życie 28.04.2023). Podstawa: art. 15 UChEB. Brak nowszej metodologii w Dz.U. do 2026 poz. 1244 | ELI: DU/2015/376, pole „references” | https://api.sejm.gov.pl/eli/acts/DU/2015/376 | P | Akt z delegacji UChEB, więc wygaśnięcie WT (art. 66 ustawy o dostępności) go nie obejmuje. Projekt metodologii z klasami A+–G (konsultacje VII–VIII 2024; W: globenergia.pl) nieogłoszony |
| R6-02 | UChEB: t.j. **Dz.U. 2024 poz. 101**. Ostatni akt zmieniający: Dz.U. 2023 poz. 1762 (w życie 01.10.2023). Świadectwo sporządza osoba z wykazu (art. 16a, art. 17), w centralnym rejestrze charakterystyki energetycznej budynków (art. 4 ust. 3; nie mylić z CEEB — centralną ewidencją emisyjności budynków z ustawy o wspieraniu termomodernizacji, art. 27a). Ważność 10 lat (art. 14). Zwolnienie m.in. dla budynku wolnostojącego o pow. użytkowej < 50 m² (art. 3 ust. 4 pkt 5) — LAMELA nie jest zwolniony | UChEB art. 3, 4, 14, 16a, 17 | https://api.sejm.gov.pl/eli/acts/DU/2024/101/text.pdf | P | ELI: DU/2014/1200, „akt posiada tekst jednolity” |
| R6-03 | Do zawiadomienia o zakończeniu budowy dołącza się kopię lub wydruk **świadectwa charakterystyki energetycznej** (z wyłączeniem budynków z art. 3 ust. 4 UChEB) | PB art. 57 ust. 1 pkt 6a | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | Etap po budowie. W PT przewidzieć dane do świadectwa |
| R6-04 | PAB zawiera „informację o wyposażeniu technicznym budynku, w tym projektowanym źródle lub źródłach ciepła do ogrzewania i przygotowania ciepłej wody użytkowej”. **PT zawiera charakterystykę energetyczną** (w przypadku budynków) | PB art. 34 ust. 3 pkt 2 lit. g; pkt 3 lit. b | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | — |
| R6-05 | **PAB, część opisowa — analiza alternatywnych systemów zaopatrzenia w energię i ciepło** (OZE, kogeneracja, ciepło sieciowe, pompy ciepła). Zawartość: (a) szacunek rocznej energii użytkowej na ogrzewanie, wentylację i c.w.u.; (b) dostępne nośniki; (c) wybór 2 systemów: konwencjonalny + alternatywny albo konwencjonalny + hybrydowy; (d) obliczenia optymalizacyjno-porównawcze; (e) wyniki i wybór | RPB § 20 ust. 1 pkt 10 | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | P | Zmiany 2023 poz. 2405, 2024 poz. 473 i 2026 poz. 597 **nie zmieniły** pkt 10. Wymóg aktualny |
| R6-06 | **PAB — analiza technicznych i ekonomicznych możliwości** zastosowania urządzeń automatycznie regulujących temperaturę oddzielnie w pomieszczeniach lub strefie, zgodnie z WT § 135 ust. 7–10 i § 147 ust. 5–7 | RPB § 20 ust. 1 pkt 11 | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | P | Kryterium ekonomiczne w WT: prosty okres zwrotu ≤ 5 lat (R6-17) |
| R6-07 | **PT, część opisowa:** instalacje ogrzewcze, chłodnicze i klimatyzacji z automatyczną regulacją temperatury w pomieszczeniach lub strefie; wentylacja; woda i kanalizacja; elektryka; piorunochron (§ 23 pkt 7). Powiązanie z sieciami, założenia i wyniki obliczeń, dobór urządzeń; parametry klimatu wewnętrznego; moc cieplna, chłodnicza i elektryczna (pkt 8). **Charakterystyka energetyczna wg przepisów z art. 15 UChEB:** (a) bilans mocy urządzeń; (b) właściwości cieplne przegród; (c) sprawności instalacji; (d) dane wykazujące spełnienie wymagań oszczędności energii (pkt 11) | RPB § 23 pkt 7, 8, 11 | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | P | 2026 poz. 597 dodała tylko pkt 12 (ochrona ludności) |
| R6-08 | **PT, część rysunkowa:** rozwiązania przegród zewnętrznych ze szczegółami wpływającymi na właściwości cieplne i szczelność powietrzną (§ 24 pkt 2). Instalacje wod.-kan., ogrzewcze, wentylacyjne, elektryczne na rzutach i przekrojach, co najmniej jako schematy (§ 24 pkt 4) | RPB § 24 pkt 2 i 4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | P | Detale wsporników i połączeń płyt (mostki) do PT |
| R6-09 | Wymagania minimalne: (1) **EP ≤ EP_max** (EP liczone wg przepisów z art. 15 UChEB); (2) przegrody i wyposażenie ≥ wymagania zał. 2. Budynek ogranicza ryzyko przegrzewania latem (§ 328 ust. 2). Warunek uznaje się za spełniony, gdy okna spełniają zał. 2 pkt 2.1.1 (§ 329 ust. 4) | WT § 328 ust. 1–2, § 329 ust. 4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Status WT → R3. Por. R3 E-01…E-03 |
| R6-10 | **EP_max = EP_H+W + ΔEP_C + ΔEP_L.** Budynek mieszkalny jednorodzinny: EP_H+W = **95** (od 01.01.2017) / **70** (od 31.12.2020). ΔEP_C = 10·A_f,C/A_f (2017) / **5·A_f,C/A_f** (od 31.12.2020), gdy budynek ma instalację chłodzenia, w przeciwnym razie 0. ΔEP_L = 0 dla budynków mieszkalnych | WT § 329 ust. 1–2 (tabele) | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Zmiany 2023–2024 (2023 poz. 2442; 2024 poz. 474, 726) nie dotyczą § 328–329 ani zał. 2. Sprawdzono wykaz zmienianych jednostek redakcyjnych |
| R6-11 | Projekt przyszłych WT („rozp. MFiG w sprawie WT … oraz warunków technicznych użytkowania budynków mieszkalnych”, wykaz MFiG nr 29, TRIS 2026/0422/PL) — **niepodpisany** | R1 § 1.1 pkt 2 | — | W | Monitorować. Przy braku oświadczenia z art. 102a PB wymagania EP nie mają podstawy w WT. Podstawą jest wtedy PB art. 5 i zasady wiedzy technicznej (R1) |
| R6-12 | **EPBD (UE) 2024/1275:** nowe budynki zeroemisyjne od 01.01.2030 (publiczne od 01.01.2028). Instalacje słoneczne na nowych budynkach mieszkalnych do 31.12.2029. GWP w cyklu życia dla wszystkich nowych budynków od 2030 r. Transpozycja do 29.05.2026 — **w PL brak aktu transponującego** (UChEB i metodologia bez zmian) | Dyrektywa 2024/1275 art. 7, 10, 35 | https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:32024L1275 | P (daty potwierdzone w tekście PL: art. 7 ust. 1–2, art. 10 ust. 3 lit. d, art. 35 ust. 1) | Nie wiąże inwestora bezpośrednio. PV i niski EP w LAMELA wpisują się w kierunek EPBD |

### 2.B Charakterystyka energetyczna — procedura obliczeń EP (dom z pompą ciepła, rekuperacją, PV)

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-13 | EP = Q_p/A_f; EK = Q_k/A_f; EU = Q_u/A_f [kWh/(m²·rok)]. A_f = powierzchnia pomieszczeń o regulowanej temperaturze. Q_p = Q_p,H + Q_p,W + Q_p,C + Q_p,L. **Q_p,L nie wyznacza się dla budynków mieszkalnych.** Q_p,H = w_H·Q_k,H + w_el·E_el,pom,H (analogicznie W i C). Dla systemów złożonych (np. PC z siecią + PV) sumuje się podsystemy z ich własnymi w_i, wzory (10)–(13) | Metodologia zał. 1 pkt 2.1, 3.1.1–3.1.2, 3.2.1–3.2.2 | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | — |
| R6-14 | **w_i (tab. 1 w brzmieniu 2023 poz. 697):** miejscowe olej, gaz ziemny, gaz płynny, węgiel kamienny i brunatny **1,10**; **energia słoneczna, wiatrowa, geotermalna 0,00**; biomasa 0,20; biogaz 0,50; ciepło sieciowe z kogeneracji (węgiel lub gaz) 0,80, (biomasa, biogaz) 0,15; ciepłownia węglowa 1,30, gazowa lub olejowa 1,20; **sieć elektroenergetyczna systemowa 2,50** (poprzednio 3,00). Pierwszeństwo mają dane dostawcy; wartość ujemną przyjmuje się jako 0,00 | Metodologia zał. 1 pkt 3.1.3, tab. 1 (Dz.U. 2023 poz. 697 § 1 pkt 1) | https://api.sejm.gov.pl/eli/acts/DU/2023/697/text.pdf | P | W LAMELA: sieć 2,50; PV (autokonsumpcja) 0,00 |
| R6-15 | **Energia z PV:** metodologia nie zawiera odrębnej procedury dla PV. Energię słoneczną wytworzoną miejscowo traktuje się jako nośnik z w = 0,00 (tab. 1 lp. 6) dla części zapotrzebowania systemów technicznych (H, W, pomocnicze), którą ta energia pokrywa. **Energia oddana do sieci nie obniża EP.** W studium PW (2016) 80% produkcji PV nie zostało uwzględnione w EP | Metodologia tab. 1 lp. 6, wzory (10)–(13); Chwieduk B., JCEEA t. XXXIII z. 63 (4/16), 2016, s. 53–60, DOI 10.7862/rb.2016.247 | http://doi.prz.edu.pl/pl/pdf/biis/684 | P (tabela) / W (sposób bilansowania) | Krok bilansu (godzinowy lub miesięczny) i sposób wyznaczenia udziału autokonsumpcji — **NIEZWERYFIKOWANE** (brak wytycznych ministerialnych). Przyjąć zachowawczo |
| R6-16 | **Pompa ciepła — domyślne η_H,g (SCOP, tab. 2):** powietrze/woda elektryczna **2,60 (55/45 °C), 3,00 (35/28 °C)**; glikol/woda 3,50 / 4,00; woda/woda 3,60 / 4,00; powietrze/powietrze 3,00. **C.w.u. (tab. 9): PC powietrze/woda 2,60**, glikol/woda 3,00. Pierwszeństwo mają dane producenta lub dostawcy | Metodologia pkt 4.1.2.2 (tab. 2 lp. 17–28), 4.1.3.2 (tab. 9 lp. 8–15) | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | Czy użyć SCOP „klimat umiarkowany” wg PN-EN 14825:2022-11 — patrz Nierozstrzygnięte |
| R6-17 | **Sprawności składowe (domyślne):** η_H,e: wodne podłogowe z regulacją centralną + miejscową dwustawną lub P **0,89**; bez regulacji miejscowej 0,76; płaszczyznowe < 30 °C bez regulacji miejscowej 0,85 (tab. 3). η_H,d: centralne z izolowanymi przewodami w przestrzeni ogrzewanej **0,96**, w nieogrzewanej 0,90 (tab. 6). η_W,d: **dom jednorodzinny bez cyrkulacji 0,60**; cyrkulacja z ograniczonym czasem pracy, z pionami i zaizolowanymi przewodami rozprowadzającymi, ≤ 30 punktów **0,80**; to samo bez ograniczenia czasu pracy 0,70 (tab. 12 lp. 5.1a i 6.1a). η_W,s: zasobnik produkowany po 2005 r. **0,85** (tab. 14) | Metodologia tab. 3, 6, 12, 14 | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | Cyrkulacja czasowa daje wyższe η_W,d niż brak cyrkulacji (0,80 vs 0,60) |
| R6-18 | **C.w.u. — zapotrzebowanie normatywne:** Q_W,nd = V_Wi·A_f·c_W·ρ_W·(θ_W − θ_0)·k_R·t_R/3600. Budynek jednorodzinny: **V_Wi = 1,40 dm³/(m²·doba), k_R = 0,90**, θ_W = 55 °C, θ_0 = 10 °C, t_R = 365. Wynik: **Q_W,nd ≈ 24,1 kWh/(m²·rok)** (obliczenie R6) | Metodologia pkt 5.3 wzór (61), tab. 27 | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | Zależy od A_f, nie od liczby osób. Przy A_f = 250 m² daje to ok. 350 dm³/dobę 55 °C |
| R6-19 | Zyski wewnętrzne q_int budynku jednorodzinnego = **6,8 W/m²** (tab. 26). Wentylacja nawiewno-wywiewna: b_ve = 1 − η_oc (tab. 21) | Metodologia tab. 21, 26 | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | η_oc wg deklaracji centrali (PN-EN 13141-7+A1:2026-05, R6-45) |
| R6-20 | **Energia pomocnicza (domyślne, tab. 20):** pompy obiegowe ogrzewania podłogowego 0,50 W/m² × 6700 h (A_f ≤ 250 m²). Wentylator centrali nawiewno-wywiewnej: **0,50 W/m² (n ≤ 0,6 h⁻¹) / 1,30 W/m² (n > 0,6 h⁻¹) × 8760·β h**. Pompa cyrkulacyjna ciągła (A_f ≤ 250) 0,15 W/m² × 8760 h; przerywana do 4 h/d (A_f > 250) 0,04 × 7300. Pompa ładująca zasobnik c.w.u. 0,25 × 270 (≤ 250 m²) / 0,20 × 580 (> 250 m²). Pierwszeństwo mają moce zainstalowanych urządzeń | Metodologia pkt 4.1.6.5, tab. 20 | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | Domyślne wartości pomocnicze dają ok. 19,5 kWh/(m²·rok) EP (szacunek R6). Liczyć z rzeczywistych mocy. Próg A_f = 250 m² zmienia wartości domyślne |
| R6-21 | Dane klimatyczne do EP: średnie miesięczne temperatury i napromieniowanie **z najbliższej stacji meteorologicznej**, publikowane w BIP ministra właściwego ds. budownictwa (dla LAMELA: Poznań). Współczynniki H_tr — metodą podstawową wg PN dotyczącej projektowego obciążenia cieplnego | Metodologia pkt 5.2.x | https://api.sejm.gov.pl/eli/acts/DU/2015/376/text.pdf | P | Zbiór danych (typowe lata meteorologiczne) — pobrać z BIP MFiG/MRiT; wersja **NIEZWERYFIKOWANA** |

### 2.C Izolacyjność, okna, kondensacja, szczelność (WT zał. 2)

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-22 | **U_C(max) od 31.12.2020 [W/(m²·K)]:** ściany zewnętrzne t_i ≥ 16 °C **0,20**; 8–16 °C 0,45; < 8 °C 0,90. Ściany wewnętrzne ogrzewane/nieogrzewane **0,30**. Dachy i stropodachy t_i ≥ 16 °C **0,15**; 8–16 °C 0,30; < 8 °C 0,70. Podłogi na gruncie t_i ≥ 16 °C **0,30**; 8–16 °C 1,20; < 8 °C 1,50. Stropy nad nieogrzewanymi **0,25**. Strop oddzielający ogrzewane od nieogrzewanego 0,25. U_C obejmuje poprawki (pustki, łączniki, opady na dachy odwrócone) wg PN o U i przenoszeniu ciepła przez grunt | WT zał. 2 pkt 1.1 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Garaż **nieogrzewany**: jego przegrody zewnętrzne nie podlegają U_C(max) (tabela dotyczy pomieszczeń ogrzewanych, t_i wg § 134 ust. 2; por. zał. 2 pkt 1.2 lp. 5 — stolarka pomieszczeń nieogrzewanych „bez wymagań”). Wymagana jest tylko przegroda dom–garaż: ściana 0,30 (lp. 2c), strop 0,25 (lp. 8c), drzwi 1,3. Wartości 0,90/0,70/1,50 dotyczą garażu **ogrzewanego** do +5 °C (t_i < 8 °C). [Poprawka weryfikacji] |
| R6-23 | **U(max) stolarki od 31.12.2020:** okna, drzwi balkonowe, powierzchnie przezroczyste nieotwieralne (t_i ≥ 16 °C) **0,9**; okna połaciowe 1,1; okna w ścianach wewnętrznych do pomieszczeń nieogrzewanych 1,1; **drzwi zewnętrzne i drzwi między ogrzewanym a nieogrzewanym 1,3**; okna i drzwi w pomieszczeniach nieogrzewanych — bez wymagań | WT zał. 2 pkt 1.2 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Brama garażowa (garaż nieogrzewany) — bez wymagań; drzwi garaż→dom ≤ 1,3 |
| R6-24 | Podłoga na gruncie w pomieszczeniu ogrzewanym: **izolacja obwodowa o R ≥ 2,0 m²·K/W** | WT zał. 2 pkt 1.4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Przy płycie fundamentowej: izolacja pod płytą i na krawędzi |
| R6-25 | **Izolacja przewodów c.o. i c.w.u.** (λ = 0,035 W/(m·K)): d_w ≤ 22 mm **20 mm**; 22–35 mm **30 mm**; 35–100 mm = d_w; > 100 mm 100 mm. Przejścia przez przegrody 50%. Przewody między pomieszczeniami różnych użytkowników 50%; takie przewody w podłodze 6 mm | WT zał. 2 pkt 1.5 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Por. R3 IW-09 (interpretacja lp. 6–7 w domu jednorodzinnym) |
| R6-26 | **Okna — ochrona przed przegrzewaniem:** g = f_C·g_n ≤ **0,35** (lato). g_n wg deklaracji właściwości użytkowych; domyślnie potrójne z powłoką selektywną 0,5. Nie dotyczy okien N (NW–NE, ±45°), okien < 0,5 m² oraz okien chronionych elementem zacieniającym spełniającym pkt 2.1.1. f_C (tab. 2.1.3): białe żaluzje o nastawnych lamelach zewnętrzne **0,10/0,15/0,35**, wewnętrzne 0,25/0,30/0,45 (dla przepuszczalności 0,05/0,1/0,3); zasłony z powłoką aluminiową zewnętrzne 0,08 | WT zał. 2 pkt 2.1.1–2.1.4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Wysunięte płyty (okapy 0,8–1,5 m) nie mają wartości f_C w tabeli. Skuteczność wykazać obliczeniem albo zastosować osłony zewnętrzne |
| R6-27 | Kondensacja powierzchniowa: **f_Rsi ≥ f_Rsi,kryt** wg PN-EN ISO 13788 (rozdz. 5), φ_i = 50%. **Dopuszcza się f_Rsi,kryt = 0,72** (pomieszczenia ≥ 20 °C). Mostki cieplne 3D — wg PN o obliczaniu strumieni i temperatur (PN-EN ISO 10211). Kondensacja międzywarstwowa dopuszczalna, jeśli wyparuje latem bez degradacji (rozdz. 5 i 6 PN-EN ISO 13788) | WT § 321, zał. 2 pkt 2.2.1–2.2.5; zał. 1 lp. 70–71 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Zał. 1 lp. 70 powołuje datowaną **PN-EN ISO 13788:2013-05** (aktualna, R6-33) |
| R6-28 | Szczelność: całkowita szczelność przegród, złączy i przejść instalacyjnych. Okna i drzwi balkonowe w budynkach N/SW/W: ≤ 2,25 m³/(m·h) lub ≤ 9 m³/(m²·h) przy 100 Pa (**klasa 3** PN-EN 12207). **Zalecane n50 < 1,5 h⁻¹** przy wentylacji mechanicznej (< 3,0 przy grawitacyjnej). Zalecana próba szczelności | WT zał. 2 pkt 2.3.1–2.3.4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | WT powołuje PN-EN 12207:2001 (wycofana → PN-EN 12207:2017-01, EN) i PN-EN 13829:2002 (wycofana → **PN-EN ISO 9972:2015-10**, EN) — PKN |

### 2.D Normy obliczeniowe fizyki budowli i obciążenia cieplnego — status i kluczowe reguły

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-29 | **PN-EN ISO 6946:2017-10** (PL i EN) — **aktualna**; zastąpiła 2008. **R_se = 0,04 m²·K/W; R_si = 0,10 (strumień w górę) / 0,13 (poziomo, ±30°) / 0,17 (w dół).** Poprawki ΔU wg zał. F; pomija się je, gdy suma < 3% U. U podaje się z dokładnością do 2 cyfr znaczących, R do 2 miejsc po przecinku, obliczenia pośrednie ≥ 3 miejsca. Pustki: poziom 0 → ΔU'' = 0; **poziom 1 → 0,01**; poziom 2 → 0,04 (poziom 1 domyślny). Łączniki mechaniczne: zał. F.3 (χ wg ISO 10211 albo metoda przybliżona) | PKN; ISO 6946:2017 pkt 6.5, 6.6, 6.7.1.1, tab. 5 (próbka oficjalna); BRE BR 443:2019 pkt 4.1, 4.8 | https://sklep.pkn.pl/pn-en-iso-6946-2017-10p.html ; https://cdn.standards.iteh.ai/samples/65708/fcbae03d539c493d89aa2b10bee7691c/ISO-6946-2017.pdf ; https://www.cibse.org/media/wzrjrf3l/conventions-for-u-value-calculations.pdf | P (status, reguły 3%/zaokrąglenia) / W (R_si, ΔU'') | Współczynnik α we wzorze na ΔU_f (0,8; 0,8·d1/d0 dla wpuszczanych) — **NIEZWERYFIKOWANE** (zał. F poza próbką) |
| R6-30 | **PN-EN ISO 13370:2017-09** (PL i EN) — **aktualna**. Podłoga na gruncie: wymiar charakterystyczny B' = A/(0,5·P), grubość równoważna d_t; ψ złącza ściana–podłoga liczony osobno. Zał. D: izolacja krawędziowa | PKN; ISO 13370:2017 pkt 3.4, 6.7.1, 7.1, zał. D (próbka) | https://sklep.pkn.pl/pn-en-iso-13370-2017-09p.html ; https://cdn.standards.iteh.ai/samples/65716/0fc4017ab7f449d0bfd649e4b4b2f1fe/ISO-13370-2017.pdf | P | Wzory na U (d_t < B' i d_t ≥ B') oraz λ gruntu domyślne (piasek i żwir 2,0 W/(m·K)) — **NIEZWERYFIKOWANE** (poza próbką) |
| R6-31 | **PN-EN ISO 10077-1:2017-10** i **10077-2:2017-10** (PL i EN) — aktualne. U_w okien wg deklaracji właściwości użytkowych | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | P | WT zał. 1 lp. 16 powołuje 10077-1:2007 (wycofana) |
| R6-32 | **PN-EN ISO 10211:2017-09** i **PN-EN ISO 14683:2017-09** (PL i EN) — aktualne. 14683: metody uproszczone ψ i **wartości domyślne ψ w zał. C** (normatywny); trzy systemy wymiarów (wewnętrzne, całkowite wewnętrzne, zewnętrzne) | PKN; ISO 14683:2017 pkt 5.3.3, zał. C (spis treści próbki) | https://cdn.standards.iteh.ai/samples/65706/b2253222d49c4b318a8b60208981c5b0/ISO-14683-2017.pdf | P | Konkretne ψ domyślne (np. balkon/wspornik ≈ 0,95 W/(m·K)) — **NIEZWERYFIKOWANE** (tylko streszczenie wtórne). Dla wsporników LAMELA liczyć ψ numerycznie (ISO 10211) lub z deklaracji łącznika |
| R6-33 | **PN-EN ISO 13788:2013-05** (PL i EN) — aktualna; jest to wydanie datowane w WT zał. 1 lp. 70. PN-EN ISO 13789:2017-10 aktualna (WT powołuje 2008). PN-EN ISO 52016-1:2017-09 zastąpiła PN-EN ISO 13790:2009 | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | P | — |
| R6-34 | **Obciążenie cieplne: PN-EN 12831-1:2017-08 — aktualna, wyłącznie wersja angielska** (97 s., zatwierdzona 07.08.2017; wprowadza EN 12831-1:2017 IDT; zastępuje PN-EN 12831:2006). **Polskiego załącznika krajowego NA nie znaleziono w PKN.** Norma ma zał. A (szablon danych krajowych), zał. B (wartości domyślne) i pkt 6.3.7 (dane klimatyczne). PN-EN 12831-3:2017-08 (c.w.u.) też tylko EN | PKN (karta normy) | https://sklep.pkn.pl/pn-en-12831-1-2017-08e.html | P | **WT § 134 ust. 1 i zał. 1 lp. 16 powołują datowaną PN-EN 12831:2006** (wycofaną) — patrz Nierozstrzygnięte |
| R6-35 | Temperatury obliczeniowe wewnętrzne: pokoje, przedpokoje, kuchnie z paleniskami elektrycznymi **+20 °C**; **łazienki +24 °C**; klatki schodowe w budynkach mieszkalnych +8 °C; garaże indywidualne +5 °C (jeśli ogrzewane). Temperatura zewnętrzna wg PN-B-02403:1982 (wycofana, powołana w WT) — **Poznań: strefa II, θ_e = −18 °C** (weryfikacja R5); θ_m,e = 7,9 °C (R5) | WT § 134 ust. 2, zał. 1 lp. 17; brief § 2 (R5) | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P (WT) / W (strefa — R5) | — |
| R6-36 | Regulatory dopływu ciepła na odbiornikach (§ 134 ust. 4). Automatyka zależna od temperatury wewnętrznej wg § 134 ust. 5 **nie dotyczy domów jednorodzinnych**. Jednak **§ 135 ust. 7–9: automatyczna regulacja temperatury oddzielnie w pomieszczeniach** (albo w strefie, gdy montaż niemożliwy) — jeśli możliwe technicznie (opinia projektanta z uprawnieniami) i ekonomicznie (zwrot ≤ 5 lat). Czynnik grzewczy w pomieszczeniach dla ludzi ≤ 90 °C (§ 135 ust. 5) | WT § 134 ust. 4–5, § 135 ust. 5, 7–10 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Podłogówka z termostatami pokojowymi i siłownikami — spełnia wymóg; opisać w analizie wg RPB § 20 ust. 1 pkt 11 |

### 2.E Wentylacja

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-37 | **PN-B-03430:1983 (+Az3:2000) — wycofana w PKN, bez zastępstwa.** Nadal wiążąca przez powołanie w WT (zał. 1 lp. 26: § 147 ust. 1 z wyjątkiem pkt 5.2.1 i 5.2.3; lp. 28: § 149 ust. 1, pkt 2.1.2–2.1.4, 3.1, 4.1; lp. 33: § 155 ust. 4, pkt 2.1.5) | PKN; WT zał. 1 | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm ; https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Por. R3 IV-01 |
| R6-38 | **Wywiew minimalny (budynek mieszkalny):** kuchnia z oknem i kuchenką elektryczną **30 m³/h (mieszkanie do 3 osób) / 50 m³/h (> 3 osób)**; kuchnia bez okna z kuchenką elektryczną 50; kuchnia z kuchenką gazową 70; **łazienka (z WC lub bez) 50**; **wydzielone WC 30**; **pomocnicze pomieszczenie bezokienne 15**; pokój oddzielony > 2 drzwiami lub na wyższym poziomie domu wielopoziomowego 30. Zaleca się okresowe zwiększenie do ≥ 120 m³/h. Pralnie ≥ 2 h⁻¹; suszarnie 1 h⁻¹ | PN-83/B-03430/Az3:2000 (wyciąg) | https://www.jelwent.pl/pliki/pn03430.pdf ; https://www.wentylacja.org.pl/pages-62.html | W | Dwa niezależne źródła wtórne są zgodne (Stowarzyszenie Polska Wentylacja). Treść normy niedostępna |
| R6-39 | Strumień powietrza zewnętrznego w mieszkaniach wynika ze strumienia wywiewanego, **≥ 20 m³/h na osobę** przewidzianą na pobyt stały. Przepływ z pokoi do kuchni i pomieszczeń higieniczno-sanitarnych. W domu jednorodzinnym dopuszcza się łączenie przewodów z pomieszczeń o różnych wymaganiach | WT § 149 ust. 1, § 150 ust. 2–3 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | 5 osób → ≥ 100 m³/h nawiewu |
| R6-40 | W pomieszczeniu z wentylacją mechaniczną **nie stosuje się wentylacji grawitacyjnej**. Instalacja nawiewno-wywiewna ma regulację wydajności wentylatorów | WT § 148 ust. 2, 5 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Wyklucza kominy wentylacyjne w pomieszczeniach obsługiwanych przez rekuperację |
| R6-41 | **Odzysk ciepła:** obowiązkowy, **≥ 50% sprawności temperaturowej, dla instalacji ≥ 500 m³/h**. Przenikanie między strumieniami: wymiennik płytowy ≤ 0,25%, obrotowy ≤ 5% (przy 400 Pa) | WT § 151 ust. 1–2 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | LAMELA ok. 330 m³/h, więc obowiązek z § 151 nie zachodzi. Rekuperacja wynika z EP |
| R6-42 | **Czerpnie:** na terenie lub na ścianie 2 najniższych kondygnacji ≥ **8 m** (w rzucie) od ulic, parkingów > 20 stanowisk, miejsc gromadzenia odpadów, wywiewek kanalizacyjnych; dolna krawędź ≥ **2 m** nad terenem. Czerpnia dachowa: ≥ 0,4 m nad powierzchnią montażu i ≥ **6 m** od wywiewek | WT § 152 ust. 1–4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | — |
| R6-43 | **Wyrzutnie:** dachowa z wylotem poziomym ≥ 0,4 m nad powierzchnią i ≥ 0,4 m nad linią najwyższych punktów w promieniu 10 m. **Ścienna** dopuszczalna, gdy: brak zapachów i zanieczyszczeń; ściana sąsiada z oknami ≥ 10 m (bez okien ≥ 8 m); okna w tej samej ścianie ≥ 3 m w poziomie i ≥ 2 m w pionie; czerpnia w tej samej ścianie niżej lub równo i ≥ 1,5 m. Na dachu czerpnia–wyrzutnia ≥ 10 m (wyrzut poziomy) / ≥ 6 m (pionowy), wyrzutnia ≥ 1 m wyżej — chyba że urządzenie zblokowane skutecznie rozdziela strugi. Wyrzutnia dachowa ≥ 3 m od krawędzi dachu z oknami poniżej i od okien w dachu lub ścianie ponad dachem; przy 3–10 m dolna krawędź ≥ 1 m ponad oknem | WT § 152 ust. 6–13 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Wyrzutnia na terenie tylko za zgodą PIS (§ 152 ust. 8) |
| R6-44 | Filtry: przed nagrzewnicami, chłodnicami i odzyskiem ciepła co najmniej **G4** (wg PN-EN 779 powołanej w WT). **Moc właściwa wentylatorów (SFP):** nawiew z odzyskiem ≤ **1,60** kW/(m³/s), wywiew z odzyskiem ≤ **1,00**; dodatek +0,3 przy odzysku > 67% i przy dodatkowym stopniu filtracji. Przewody z powietrzem zewnętrznym przez pomieszczenia ogrzewane izolowane cieplnie i przeciwwilgociowo. W domu jednorodzinnym jednolokalowym przewody mogą być palne | WT § 154 ust. 6, 10–11; § 153 ust. 6–7; § 267 ust. 1a | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | PN-EN 779 wycofana → **PN-EN ISO 16890-1:2017-01** (PKN). Odpowiednik G4 w ISO 16890 (np. ISO Coarse ≥ 60%) — **NIEZWERYFIKOWANE** |
| R6-45 | **Ekoprojekt central wentylacyjnych dla mieszkań (RVU), od 01.01.2018:** SEC (klimat umiarkowany) ≤ **−20 kWh/(m²·a)**; wentylatory wielobiegowe lub płynnie regulowane; **centrale dwukierunkowe (BVU) z obejściem termicznym (by-pass)**; wizualny sygnał wymiany filtra; jednostki bezkanałowe L_WA ≤ 40 dB | rozp. (UE) 1253/2014 zał. II pkt 2 | https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:32014R1253 | P (weryfikacja: tekst PL EUR-Lex; w PL wersji: „JZE”, „DSW”, „SWNM”) | Badania central: PN-EN 13141-7+A1:2026-05 (EN), PN-EN 13141-8:2023-02 (EN) — PKN |
| R6-46 | **Garaż zamknięty:** nieogrzewany nadziemny wbudowany — co najmniej wentylacja naturalna, otwory netto ≥ **0,04 m² na stanowisko** (2 stanowiska → ≥ 0,08 m²). Ogrzewany ≤ 10 stanowisk — grawitacyjna ≥ **1,5 h⁻¹**. Dopuszcza się wentylowanie garażu powietrzem z pomieszczeń innych niż higieniczno-sanitarne | WT § 108 ust. 1 pkt 1–2; § 150 ust. 5 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Decyzja: garaż nieogrzewany (U garażu z R6-22) |
| R6-47 | PN-EN 16798-1:2019-06 (PL i EN, aktualna; zastąpiła PN-EN 15251:2012) — kryteria środowiska wewnętrznego (opcjonalnie). PN-B-03421:1978 (parametry powietrza wewnętrznego, WT § 147 ust. 3, § 149 ust. 4) — wycofana | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | P | — |

### 2.F Instalacja wodociągowa i c.w.u.

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-48 | Instalacja wg PN dotyczącej projektowania instalacji wodociągowych: **PN-B-01706:1992** (zał. 1 lp. 4, w zakresie wybranych punktów) — **w PKN wycofana bez zastępstwa**, wiążąca przez WT. Zabezpieczenie przed przepływem zwrotnym wg PN-EN 1717:2003 (zał. 1 lp. 5) — w PKN zastąpiona przez **PN-EN 1717:2026-01 → PN-EN 1717+A1:2026-09 (EN, aktualna)** | WT § 113 ust. 4, 7; zał. 1 lp. 4–5; PKN | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | PN-EN 806-1:2004 (PL), -2:2005, -3:2006, -4:2010, -5:2012 (EN) — **aktualne** (PKN). Metoda LU z PN-EN 806-3 jako kontrola |
| R6-49 | **Ciśnienie przed każdym punktem czerpalnym: 0,05–0,6 MPa.** Zestaw wodomierza głównego wg PN-B-10720:1998 (wycofana, powołana), za nim zabezpieczenie przed przepływem zwrotnym. Wodomierz w piwnicy lub **na parterze w wydzielonym, łatwo dostępnym miejscu** chronionym przed zalaniem, mrozem i dostępem osób postronnych. W studzience poza budynkiem tylko, gdy budynek niepodpiwniczony i brak miejsca na parterze. Przewodzące instalacje połączyć metalowo przed i za wodomierzem | WT § 114, § 115 ust. 1–2, § 116 ust. 1–3, § 117 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Warunki techniczne przyłączenia (Aquanet lub gminne przedsiębiorstwo) mogą wymagać studni wodomierzowej — **NIEZWERYFIKOWANE** |
| R6-50 | **Normatywne wypływy q_n [dm³/s] (PN-92/B-01706):** bateria umywalkowa 0,07 + 0,07 (z./c.); zlewozmywakowa 0,07 + 0,07; wannowa 0,15 + 0,15; natryskowa 0,15 + 0,15; płuczka zbiornikowa 0,13 (min. 0,05 MPa); zmywarka 0,15; pralka automatyczna 0,25; zawór czerpalny bez perlatora DN15 0,30. Przepływ obliczeniowy w budynkach mieszkalnych (Σq_n ≤ 20, q_n < 0,5): **q = 0,682·(Σq_n)^0,45 − 0,14** | PN-92/B-01706 tabl. 1 i wzór (wg materiałów PWr i kalkulatorprojektanta.pl) | https://wis.pwr.edu.pl/d/HGBUKOTtQKxVvEkBoSk8TDxZIUTggT0FAGRoIVURNWHxXAlhnRkokXiVvBChKWQBPFgEYITwyHUBTdE0TFRwTPTxUWHFVFW1aClkQelJSAVEBRl9qPx8bQFNnB0MJGQ5vTxUOMhRcbQ1mTQ/wbliw__sd_iii_rok_-_materialy_i_przyklad_dla_ins_1.pdf ; https://www.kalkulatorprojektanta.pl/teoria/wyznaczanie-przeplywu-obliczeniowego-wody | W | Wzór sprawdzony na przykładzie PWr (Σq_n = 1,82 → q = 0,75). Wartość dla natrysku rozbieżna w źródłach (0,07–0,15) — przyjąć 0,15 + 0,15 (PWr) |
| R6-51 | **PN-EN 806-3 (metoda uproszczona LU):** umywalka, bidet, spłuczka WC 1 LU (Q_A 0,1 l/s); zlewozmywak, zmywarka, natrysk 2 LU (0,2); wanna 4 LU (0,4); **zawór ogrodowy 5 LU (0,5)**; zawór spłukujący DN20 15 LU. Prędkości ≤ 2 m/s w przewodach rozdzielczych, ≤ 4 m/s w podejściach. Ciśnienie w punkcie ≥ 1 bar, w sieci ≤ 5 bar (zawory ogrodowe do 10 bar) | PN-EN 806-3:2006 tabl. 1 (wg instsani.pl) | https://instsani.pl/technik-inzynierii-sanitarnej/materialy-do-zajec/projektowanie-instalacji-i-sieci/projektowanie-instalacji-wody-zimnej-cieplej-i-ppoz/obliczanie-przewodow-wodociagowych/obliczenia-wedlug-normy-pn-en-806-32006/ | W | — |
| R6-52 | **C.w.u.:** energia na przygotowanie na racjonalnie niskim poziomie; straty przesyłu niskie; izolacja wg zał. 2 (§ 118). Gdy c.w.u. przygotowywana z instalacji ogrzewczej, trzeba zapewnić inny sposób podgrzewania w przerwach jej pracy (§ 119). **Temperatura w punktach czerpalnych 55–60 °C** (§ 120 ust. 2). **Dezynfekcja termiczna: 70–80 °C w punktach** (§ 120 ust. 2a). Zabezpieczenie przed przekroczeniem ciśnienia i temperatury wg PN-B-02440:1976 (wycofana, powołana). Ciepła woda po lewej stronie armatury. **Stały obieg (cyrkulacja) nie jest wymagany w budynkach jednorodzinnych** (§ 120 ust. 1) | WT § 118–120 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | § 119 wymaga c.w.u. latem (PC z trybem c.w.u. lub grzałką). Metodologia liczy θ_W = 55 °C |
| R6-53 | **Ocena ryzyka wewnętrznego systemu wodociągowego** (art. 4i–4m ustawy o zbiorowym zaopatrzeniu w wodę, dodane ustawą z 13.03.2026) **nie dotyczy budynków mieszkalnych jednorodzinnych** (art. 4i ust. 10). Materiały i wyroby w kontakcie z wodą do spożycia: wprowadzane do obrotu z certyfikatem zgodności wg art. 11 dyrektywy (UE) 2020/2184 (nowy rozdz. 3b ustawy o PIS, art. 37ao–37ap) | Dz.U. 2026 poz. 605 art. 1 (art. 4i ust. 10), art. 2 (rozdz. 3b ustawy o PIS) | https://api.sejm.gov.pl/eli/acts/DU/2026/605/text.pdf | P | W specyfikacji PT żądać wyrobów z certyfikatem lub oznakowaniem zgodnym z nowymi przepisami. Przepisy przejściowe dla wyrobów — **NIEZWERYFIKOWANE** |
| R6-54 | Wykorzystanie deszczówki (spłukiwanie WC, podlewanie) — **odrębna instalacja, niepołączona z wodociągiem** | WT § 126 ust. 3; PN-EN 16941-1:2024-08 (EN, aktualna) | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Opcja: podlewanie ogrodu ze zbiornika |

### 2.G Kanalizacja sanitarna

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-55 | Instalacja kanalizacyjna do pierwszej studzienki od strony budynku, zgodnie z PN: **PN-EN 12056-1:2002 (pkt 4, 5), -2:2002 (pkt 4–6), -3:2002 (pkt 4–7), -4:2002 (pkt 4–6), -5:2002 (pkt 5–9)** — w PKN **aktualne, wersje polskie** | WT § 122 ust. 1–2, zał. 1 lp. 10; PKN | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Zewnętrzne: PN-EN 752:2017-06 (PL); budowa i badania PN-EN 1610:2015-10 (PL) — aktualne |
| R6-56 | **Piony (przewody spustowe) wyprowadzone ponad dach jako wentylujące** i powyżej górnej krawędzi okien i drzwi w odległości poziomej < 4 m od wylotu. Dopuszcza się piony zakończone **urządzeniami napowietrzającymi**, jeśli ponad dach wyprowadzono: ostatni pion na każdym przewodzie odpływowym i co najmniej co piąty z pozostałych. Zakaz wprowadzania wentylacji pionów do przewodów dymowych, spalinowych i wentylacyjnych. Pion > 10 m: podłączenia na najniższej kondygnacji wg PN-B-01707:1992 | WT § 125 ust. 1–4 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | Zawory napowietrzające: **PN-EN 12380:2005** (PL, aktualna). Wywiewka ≥ 6 m od czerpni dachowej (R6-42) |
| R6-57 | **Równoważniki odpływu DU (system I) [l/s]:** umywalka i bidet 0,5; natrysk bez korka 0,6, z korkiem 0,8; wanna 0,8; zlewozmywak 0,8; zmywarka 0,8; pralka ≤ 6 kg 0,8, ≤ 12 kg 1,5; miska ustępowa 6 l i 7,5 l **2,0**, 9 l 2,5; wpust DN50 0,8, DN70 1,5, DN100 2,0. **K = 0,5** (użytkowanie nieciągłe — mieszkania). **Q_ww = K·√ΣDU**, nie mniej niż największy pojedynczy DU | PN-EN 12056-2:2002 tabl. 2 i 3 (wg kalkulatorprojektanta.pl) | https://kalkulatorprojektanta.pl/teoria/wyznaczanie-natezenia-przeplywu-sciekow | W | Reguła „Q_ww ≥ max DU” — **NIEZWERYFIKOWANE** (praktyka projektowa) |
| R6-58 | Minimalna średnica pionu z miską ustępową **0,10 m (DN100)**, pionu bez WC 0,07 m. Zawór napowietrzający pionu: Q_a ≥ 8·Q_tot; podejść 1–2·Q_tot | PN-EN 12056-2 (wg instsani.pl) | https://instsani.pl/technik-inzynierii-sanitarnej/materialy-do-zajec/projektowanie-instalacji-i-sieci/projektowanie-instalacji-kanalizacyjnych/rzewodu-laczacego-przybor-sanitarny-z-pionem-srednica-podejscia-nie-moze-byc-mniejsza-od-srednicy-wylotu-z-przyboru-norma-pn-en-12056-22002-osobno-traktuje-podejscia-wentylowane-i-niewentylo/piony-kanalizacyjne/ | W | Przepustowość pionu DN100 z wentylacją główną (ok. 4,0 l/s) i limity podejść niewentylowanych — **NIEZWERYFIKOWANE** (tabele normy niedostępne) |
| R6-59 | Pomieszczenia, z których grawitacyjny spływ może być czasowo niemożliwy: przepompownia (PN-EN 12056-4) albo zamknięcie przeciwzalewowe (PN-EN 13564-1:2004, PL, aktualna) | WT § 124 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | LAMELA bez piwnic; ±0,00 = 0,30 m nad terenem. Sprawdzić rzędną studni rewizyjnej względem wpustów w garażu |

### 2.H Wody opadowe i roztopowe

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-60 | Działka wyposażona w kanalizację do odprowadzania wód opadowych do sieci. Przy **budynkach niskich lub braku możliwości przyłączenia** dopuszcza się odprowadzenie na własny teren nieutwardzony, do dołów chłonnych lub zbiorników retencyjnych. **Zakaz zmiany naturalnego spływu w kierunku sąsiada.** Dachy, tarasy i zagłębienia przy ścianach mają odprowadzenie wody zgodnie z § 28 ust. 2 | WT § 28 ust. 1–2, § 29, § 126 ust. 1 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | MPZP (brief): zagospodarowanie w granicach działki, zakaz odprowadzania na drogę |
| R6-61 | **Natężenie deszczu do rynien i rur spustowych:** PN-EN 12056-3 wymienia jedynie możliwe wartości 0,010…0,060 l/(s·m²), bez wartości dla PL. Zalecenie literaturowe: **0,030–0,050 l/(s·m²)** (300–500 l/(s·ha)) z uwzględnieniem zmian klimatu | PN-EN 12056-3:2002; Dąbrowski W., Dąbrowska B., Jasik H., „Rynek Instalacyjny” 12/2015 | https://www.rynekinstalacyjny.pl/artykul/kanalizacja-deszczowa/22908,odwadnianie-dachow-wymiarowanie-rynien-okapowych | W | Odwodnienie awaryjne dachów płaskich (przelewy) — wg PN-EN 12056-3 pkt 7; szczegóły **NIEZWERYFIKOWANE** |
| R6-62 | **Retencja i rozsączanie (metodyka Aquanet 2024, Poznań):** k_f gruntu 10⁻⁶–10⁻³ m/s. Zbiornik infiltracyjny ≥ **1,5·h + 0,5 m** od fundamentów (h = głębokość posadowienia). Dno ≥ **1 m** nad maksymalnym zwierciadłem wód gruntowych. Osadnik przed infiltracją. Deszcz: **PANDa 2050 (RCP 4.5), stacja Poznań-Ławica, C_z = 10 lat** (sieć C = 5), t_d = 5…4320 min. **V_obl = max[0,06·q(t_d, C_z)·Σ(ψ_i·A_i[ha])·t_d − 0,06·(Q_inf + Q_od)·t_d]** [m³]. **Q_inf = 1000·A_inf·k_f,nn** [l/s]; A_inf = dno + ½ ścian; **k_f,nn = 0,5·k_f**. **V_min = 1,2·V_obl** (1,1 przy przelewie awaryjnym). Opróżnianie ≤ 24 h | Aquanet S.A., „Załącznik C – Metodyka obliczania niezbędnej objętości zbiorników detencyjno-retencyjnych (infiltracyjnych) wód opadowych i roztopowych”, 2024, rozdz. I–III | https://www.aquanet.pl/wp-content/uploads/2024/08/Zalacznik-C-Metodyka-obliczania-niezbednej-objetosci-zbiornikow-detencyjno-retencyjnych-infiltracyjnych-wod-opadowych-i-.pdf | W | Wytyczne operatora sieci poznańskiej (nie przepis). Zalecenie „V ≥ 100 m³” dotyczy zlewni sieciowych, nie działki |
| R6-63 | **Natężenia PANDa 2050, Poznań, C = 10 lat [l/(s·ha)]:** t_d = 5 min **464,6**; 10 min 305,8; 15 min 239,5; 30 min 157,6; 60 min 91,0; 120 min 52,5; 180 min 38,1; 240 min 30,3; 360 min 22,0; 720 min 12,7; 1440 min 7,33 | Aquanet 2024, tab. 3 | https://www.aquanet.pl/wp-content/uploads/2024/08/Zalacznik-C-Metodyka-obliczania-niezbednej-objetosci-zbiornikow-detencyjno-retencyjnych-infiltracyjnych-wod-opadowych-i-.pdf | W | Atlas: https://atlaspanda.pl/ (IMGW-PIB). Dla gminy spoza Poznania — odczytać z atlasu dla najbliższej stacji |
| R6-64 | **Współczynniki spływu ψ:** dach płaski (papa, blacha) **0,95**; dach < 10° 0,90; dach żwirowy 0,60; **dach zielony ekstensywny (substrat 8–10 cm) 0,5**; intensywny (≥ 26 cm) 0,30; kostka betonowa bez zalanych spoin 0,80; płyty ażurowe na piasku 0,40; ogrody 0,15; ogród deszczowy, niecka 1,00 | Aquanet 2024, tab. 2 | jw. | W | — |
| R6-65 | **DWA-A 138:2005 wycofana**; zastąpiona przez **DWA-A 138-1 (10/2024)** „Anlagen zur Versickerung von Niederschlagswasser – Teil 1”. Zmiany: dokładniejsza ocena przepuszczalności gruntu, współczynniki bezpieczeństwa, rozróżnienie systemów zdecentralizowanych i centralnych. DWA-M 138-2 — projekt 10/2025 | DWA e.V. | https://de.dwa.de/de/regelwerk-news-volltext/arbeitsblatt-dwa-a-138-1-anlagen-zur-versickerung-von-niederschlagswasser-teil-1-planung-bau-betrieb.html | W | Wytyczna niemiecka, nie PN. Metodyka Aquanet ma podobną logikę bilansową |
| R6-66 | **Prawo wodne:** zwykłe korzystanie z wód — wprowadzanie ścieków do ziemi ≤ 5 m³/d (art. 33 ust. 4). Opłata za zmniejszenie naturalnej retencji tylko dla nieruchomości **> 3500 m²** z wyłączeniem > 70% powierzchni biologicznie czynnej (art. 34 pkt 4, art. 269 ust. 1 pkt 1) — działka 1600 m², więc nie dotyczy. Wody opadowe z dachów nie należą do „ścieków” (art. 16 pkt 61). „Urządzenia wodne” obejmują jednak „wyloty służące do wprowadzania wody … do ziemi” (art. 16 pkt 65 lit. f), a ich wykonanie wymaga pozwolenia wodnoprawnego (art. 389 pkt 6). Art. 395 nie zawiera zwolnienia dla rozsączania deszczówki | Prawo wodne, t.j. Dz.U. 2025 poz. 960 ze zm. (2025 poz. 1535; 2026 poz. 445, 605, 815, 1033, 1156) | https://api.sejm.gov.pl/eli/acts/DU/2025/960/text.pdf | P | **Nierozstrzygnięte** — w praktyce Wody Polskie wydają pozwolenia na „zespół skrzynek rozsączających” (BIP Powiatu Lipnowskiego). Zmiany 2026 poz. 1033 i 1156 dotyczą legalizacji ujęć i wody odzyskanej, nie deszczówki |
| R6-67 | Bezodpływowe zbiorniki na wody opadowe: **do 5 m³ łącznie — bez zgłoszenia i pozwolenia; 5–15 m³ — zgłoszenie** | PB art. 29 (brzmienie wg Dz.U. 2025 poz. 1847) — R1 | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P (wg R1) | W projekcie budowlanym budynku zbiornik objęty PnB. Próg ma znaczenie przy późniejszych zmianach |

### 2.I Pompa ciepła powietrze–woda: czynnik, hałas, montaż

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-68 | **Zakaz wprowadzania do obrotu (zał. IV pkt 8)** samodzielnych (monoblokowych) klimatyzatorów i pomp ciepła: (b) **≤ 12 kW z F-gazem o GWP ≥ 150 — od 01.01.2027** (GWP 750, jeśli wymagają tego względy bezpieczeństwa); (c) ≤ 12 kW z jakimkolwiek F-gazem — od 01.01.2032; (d) > 12 do 50 kW GWP ≥ 150 — od 01.01.2027; (e) pozostałe samodzielne GWP ≥ 150 — od 01.01.2030 | Rozp. (UE) 2024/573 art. 11 ust. 1, zał. IV pkt 8 | https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:32024R0573 | P | „Samodzielny”: art. 3 pkt 38 — części z gazem nie są łączone na miejscu (monoblok) |
| R6-69 | **Split (zał. IV pkt 9):** (a) pojedyncze split < 3 kg F-gazu z GWP ≥ 750 — od 01.01.2025; (b) **split powietrze–woda ≤ 12 kW z GWP ≥ 150 — od 01.01.2027**; (c) split powietrze–powietrze ≤ 12 kW GWP ≥ 150 — od 01.01.2029; (d) split ≤ 12 kW z jakimkolwiek F-gazem — od 01.01.2035; (e) > 12 kW GWP ≥ 750 — 2029; (f) > 12 kW GWP ≥ 150 — 2033 | Rozp. (UE) 2024/573 zał. IV pkt 9; art. 3 pkt 39 | jw. | P | R32: GWP 675 (zał. I — P). **R290 (propan)** nie figuruje w zał. I–III, więc nie jest F-gazem (P). GWP₁₀₀ = 0,02 pochodzi z IPCC AR6 (W), nie z rozporządzenia. W starszych źródłach (AR4, PN-EN 378) GWP = 3 |
| R6-70 | Po upływie roku od daty zakazu dalsze dostawy produktów wprowadzonych legalnie przed tą datą są dopuszczalne tylko z dowodem daty wprowadzenia. Od 01.01.2026 zakaz serwisowania PC F-gazami o GWP ≥ 2500 (art. 13 ust. 4) | Rozp. (UE) 2024/573 art. 11 ust. 1 akapit ostatni, art. 13 ust. 4 | jw. | P | Budowa LAMELA prawdopodobnie od 2027 r. — wybrać czynnik naturalny |
| R6-71 | **Ekoprojekt 813/2013:** sezonowa efektywność η_s od 26.09.2017: PC ≥ **110%**; **niskotemperaturowe PC ≥ 125%**. **L_WA (od 26.09.2015), wewnątrz/na zewnątrz:** ≤ 6 kW 60/**65** dB; 6–12 kW 65/**70** dB; 12–30 kW 70/78 dB; 30–70 kW 80/88 dB. Metoda pomiaru: PN-EN 12102-1:2022-12 (PL); SCOP wg PN-EN 14825:2022-11 (PL); c.w.u. PC wg PN-EN 16147+A1:2023-06 (EN) — aktualne w PKN | Rozp. (UE) 813/2013 zał. II pkt 1 b) i pkt 3 (tekst PL z EUR-Lex); PKN | https://eur-lex.europa.eu/legal-content/PL/TXT/PDF/?uri=CELEX:32013R0813 | P (weryfikacja: tekst PL EUR-Lex) / P (statusy PKN) | Rewizja 813/2013 w toku (konsultacje KE 28.11.2025–23.01.2026). EUR-Lex 2026-09-25: 813/2013 „In force”, bez daty końca obowiązywania, więc nowe rozporządzenie nie uchyliło go do tej daty. Czy nowy akt przyjęto bez rozpoczęcia stosowania — NIEZWERYFIKOWANE |
| R6-72 | **Dopuszczalny hałas w środowisku, tereny zabudowy mieszkaniowej jednorodzinnej (lp. 2a), „pozostałe obiekty i działalność”: L_Aeq,D = 50 dB** (8 najmniej korzystnych godzin dnia kolejno po sobie), **L_Aeq,N = 40 dB** (1 najmniej korzystna godzina nocy) | POŚ-hałas, zał. tab. 1 | https://api.sejm.gov.pl/eli/acts/DU/2014/112/text.pdf | P | Rozp. 2007/826 „obowiązujące”, t.j. 2014/112. Por. R3 H-11. PORT PC zaleca ≤ 35 dB(A) w nocy (W) |
| R6-73 | Szacowanie poziomu przy odbiorniku: **L_A = L_WA + 10·log(Q/(4·π·r²))**; Q = 2 (na wolnej przestrzeni przy gruncie), 4 (przy ścianie), 8 (w narożu) | PORT PC, „Wytyczne do ograniczania hałasu instalacji z pompami ciepła”, pkt 4.4 | https://www.teraz-srodowisko.pl/media/pdf/aktualnosci/1406-Wytyczne-ograniczanie-halasu-instalacji-pompy-ciepla.pdf | W | Metoda przybliżona, bez ekranowania i tonalności |
| R6-74 | Instalacje i urządzenia nie mogą powodować nadmiernego hałasu i drgań. **Posadowienie i połączenia zapobiegają przenoszeniu drgań.** Pomieszczenie techniczne z urządzeniami hałaśliwymi przy pokojach — rozwiązania ochronne. Przewody instalacyjne nie mogą pogarszać izolacyjności akustycznej przegród | WT § 96, § 326 ust. 3, § 327 ust. 2–3 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | PN-B-02151-2:2018-01 (PL, aktualna) — dopuszczalne poziomy w pomieszczeniach |
| R6-75 | **R290 — strefa bezpieczeństwa wokół jednostki zewnętrznej:** zwykle **1 m** od krawędzi urządzenia (Kaisai); u innych producentów 1,0–1,5 m. W strefie nie może być okien, drzwi, otworów wentylacyjnych, świetlików, włazów, **studzienek kanalizacyjnych, wpustów, zagłębień terenu** ani źródeł zapłonu (gniazda, łączniki, oprawy). Propan jest cięższy od powietrza (ok. 1,5×). Wymagania bezpieczeństwa: PN-EN 378-1+A1:2021-03 (EN), PN-EN IEC 60335-2-40:2025-02 (EN) | Polski Instalator (19.06.2023); Globenergia; PKN (statusy) | https://www.polskiinstalator.com.pl/artykuly/instalacje-oze/3213-pompy-ciep%C5%82a-na-propan-r290-%E2%80%93-wymagania-producent%C3%B3w-dotycz%C4%85ce-monta%C5%BCu,-uruchomienia-i-serwisowania-urz%C4%85dze%C5%84 | W | Ostateczna strefa — wg DTR wybranego modelu. Wrysować na PZT i elewacji |

### 2.J Instalacja fotowoltaiczna (PV) i mikroinstalacja

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R6-76 | Bez pozwolenia i zgłoszenia: instalowanie pomp ciepła, **urządzeń PV ≤ 150 kW**, magazynów energii ≤ 30 kWh. **Dla PV > 6,5 kW:** uzgodnienie projektu z rzeczoznawcą ds. zabezpieczeń ppoż., zawiadomienie PSP o zakończeniu instalowania i przekazanie **planu urządzenia PV dla ekip ratowniczych** | PB art. 29 ust. 4 pkt 3 lit. c (brzmienie z ustawy Dz.U. 2025 poz. 1847) | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | — |
| R6-77 | **Art. 56 ust. 1a PB — uchylony.** Art. 56 ust. 1: zawiadomienie PSP i PIS tylko wtedy, gdy projekt wymagał ich uzgodnienia | PB art. 56 ust. 1 i 1a (t.j. 2026, przypis 81) | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | Korekta briefu § 5 („art. 56 ust. 1a”) |
| R6-78 | „Moc zainstalowana elektryczna” instalacji OZE innej niż biogazowa i hybrydowa = **łączna moc znamionowa czynna … modułu fotowoltaicznego podana przez producenta na tabliczce znamionowej**. **Mikroinstalacja ≤ 50 kW** | Ustawa OZE, t.j. Dz.U. 2026 poz. 68, art. 2 pkt 19 i 19b lit. b | https://api.sejm.gov.pl/eli/acts/DU/2026/68/text.pdf | P | PB nie definiuje tego pojęcia. Przyjęcie definicji z ustawy OZE to interpretacja: **limit 6,5 kW liczyć po stronie modułów (kWp DC)** |
| R6-79 | Przyłączenie mikroinstalacji odbiorcy już przyłączonego, gdy moc ≤ mocy z warunków przyłączenia: **na zgłoszenie do OSD**, po zainstalowaniu zabezpieczeń i licznika. Koszt zabezpieczeń i licznika ponosi OSD | Prawo energetyczne, t.j. Dz.U. 2026 poz. 43, art. 7 ust. 8d4–8d6 | https://api.sejm.gov.pl/eli/acts/DU/2026/43/text.pdf | P | Po t.j. zmiany: 2026 poz. 516, 607 i 900 (ELI). Wyszukiwanie w ich tekstach: żadna nie zmienia ust. 8d4–8d6 (516 zmienia m.in. ust. 8d3, 8d8, 8d11, 8d13, 8d15). Stan ust. 8d4–8d6 bez zmian (weryfikacja 2026-09-25). Szczegóły → zespół elektryczny |
| R6-80 | Normy PV: **PN-HD 60364-7-712:2016-05** (PL, aktualna); dokumentacja i badania PN-EN 62446-1:2016-08 (EN); współpraca z siecią PN-EN 50549-1:2019-02 (PL) | PKN | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | P | — |

---

## 3. Implikacje dla projektu Dom LAMELA — wartości i reguły gotowe do użycia

### 3.1 Podstawa formalna (do opisu PAB i PT)
* Oświadczenie inwestora z art. 102a PB (R1). **WT w brzmieniu obowiązującym do 20.09.2026** (repealDate w ELI: 21.09.2026): Dział IV rozdz. 1–2 i 4–7 (instalacje), Dział IX (hałas), Dział X i zał. 2 (energia), zał. 1 (normy).
* Metodologia: Dz.U. 2015 poz. 376, zm. 2017 poz. 22, 2019 poz. 1829, 2023 poz. 697. UChEB: t.j. Dz.U. 2024 poz. 101.
* RPB: § 20 ust. 1 pkt 10 i 11 (PAB), § 23 pkt 7, 8, 11 i § 24 pkt 2, 4 (PT).
* Powoływać **dokładnie te wydania norm, które wymienia WT zał. 1**, a obok nich aktualne wydania „jako zasady wiedzy technicznej”. Dotyczy to zwłaszcza PN-EN 12831:2006 wobec 12831-1:2017 (Nierozstrzygnięte).

### 3.2 Przegrody (cele projektowe z zapasem wobec WT)
Proponowane wartości projektowe U [W/(m²·K)] (cel R6; wymaganie WT w nawiasie):

| Przegroda | Cel U (WT) |
|---|---|
| Ściany zewnętrzne | ≤ 0,15 (0,20) |
| Stropodachy | ≤ 0,12 (0,15) |
| Podłoga na gruncie lub płyta fundamentowa, U wg PN-EN ISO 13370 | ≤ 0,20 (0,30) |
| Okna | U_w ≤ 0,8 (0,9) |
| Drzwi zewnętrzne i drzwi dom–garaż | ≤ 1,1 (1,3) |
| Ściana dom–garaż | ≤ 0,25 (0,30) |

* Izolacja obwodowa R ≥ 2,0 m²·K/W.
* Zapas jest potrzebny do spełnienia EP (pkt 3.3), bo metoda domyślna dla c.w.u. jest niekorzystna.
* U liczyć wg **PN-EN ISO 6946:2017**: R_si 0,13/0,10/0,17, R_se 0,04, poprawki wg zał. F. Pustki: poziom 1 (ΔU'' = 0,01), chyba że wykazano poziom 0. Łączniki ETICS przechodzące przez izolację liczyć zawsze. Wynik: 2 cyfry znaczące.
* **Mostki:** wsporniki płyt (P2 ok. 1,0 m, okapy 0,8–1,5 m), rama boksu C, połączenie wiata/płyta. Stosować łączniki termoizolacyjne z deklarowanym ψ i χ. Weryfikować f_Rsi ≥ 0,72 i ψ numerycznie (PN-EN ISO 10211:2017). Nie używać „domyślnych” ψ z ISO 14683 do wsporników — są wysokie i niepewne (R6-32).
* **Okna S, W i E:** g ≤ 0,35. Wariant A (zalecany): żaluzje zewnętrzne (f_C 0,10–0,35) + szyby g_n ≈ 0,5. Wariant B: szkło przeciwsłoneczne g_n ≤ 0,35 bez osłon, co pogarsza zyski zimowe. Okapy płyt nie wystarczą same — tabela f_C ich nie obejmuje.
* **Szczelność:** okna klasa ≥ 3 wg PN-EN 12207 (zalecane 4). Cel **n50 ≤ 1,0 h⁻¹** (WT zaleca < 1,5). Test wg PN-EN ISO 9972.

### 3.3 Charakterystyka energetyczna — procedura i budżet EP
1. Liczyć wg metodologii (zał. 1, metoda obliczeniowa, standardowe użytkowanie). A_f = powierzchnia o regulowanej temperaturze (bez nieogrzewanego garażu). Dane klimatyczne: stacja Poznań z BIP ministerstwa.
2. **EP_max = 70** (bez instalacji chłodzenia). Z chłodzeniem rewersyjną PC (np. przez podłogę w części pomieszczeń): **EP_max = 70 + 5·A_f,C/A_f**, ale do EP dochodzi wtedy Q_p,C.
3. **Orientacyjny szacunek R6** (A_f ≈ 250 m²; założone EU_H = 35 kWh/(m²·rok); nie jest to obliczenie projektowe):

   | Pozycja | Wartości domyślne metodologii | Dane producenta i projekt |
   |---|---|---|
   | Ogrzewanie: η_H,g / η_H,e / η_H,d | 3,00 / 0,89 / 0,96 | SCOP 4,5 / 0,89 / 0,96 |
   | EP ogrzewanie | 34,1 | 22,8 |
   | C.w.u.: Q_W,nd | 24,1 | 24,1 |
   | C.w.u.: η_W,g / η_W,d / η_W,s | 2,60 / 0,60 / 0,85 | COP_DHW 3,2 / 0,80 (cyrkulacja czasowa) / 0,85 |
   | EP c.w.u. | 45,4 | 27,7 |
   | Pomocnicze: domyślne 0,50 W/m² × 6700 h + 0,50 W/m² × 8760 h + ładowanie | 19,5 | 8,0 (wentylatory 70 W śr., pompa 25 W, cyrkulacja 5 W × 8 h/d) |
   | **EP razem** | **≈ 99 (NIE spełnia)** | **≈ 58 (spełnia)** |
   | Autokonsumpcja PV (w = 0) | — | dodatkowo −5…−15 |

   **Wniosek:** do spełnienia EP potrzebne są:
   * **deklarowane dane producenta**: SCOP wg PN-EN 14825, COP c.w.u. wg PN-EN 16147, η_oc i moc wentylatorów wg PN-EN 13141-7, straty zasobnika (klasa ErP);
   * krótkie przewody c.w.u. (węzeł sanitarny nad pomieszczeniem technicznym, pion blisko łazienek P1 i P2);
   * cyrkulacja z ograniczonym czasem pracy albo jej brak przy bardzo krótkich przewodach — wtedy jednak η_W,d = 0,60 z tabeli, chyba że wykaże się straty obliczeniowo wg pkt 4.1.3.3;
   * pompy i wentylatory EC;
   * PV z autokonsumpcją: sterowanie ładowaniem c.w.u. i bufora w godzinach produkcji.
4. W PT (RPB § 23 pkt 11) podać: bilans mocy urządzeń; U wszystkich przegród z wymaganiami; sprawności; EP, EK, EU, U_oze i E_CO2 wraz z EP_max. Przygotować dane do świadectwa (centralny rejestr charakterystyki energetycznej budynków, UChEB art. 4 ust. 3) na etap odbioru.

### 3.4 Ogrzewanie
* Obciążenie cieplne:
  * formalnie **PN-EN 12831:2006** (WT zał. 1 lp. 16); kontrolnie PN-EN 12831-1:2017;
  * θ_e = **−18 °C** (Poznań, strefa II), θ_m,e = 7,9 °C;
  * θ_int: pokoje, kuchnia, hol **20 °C**, łazienki **24 °C**, garaż nieogrzewany (lub +5 °C, jeśli temperowany).
* Źródło i instalacja:
  * źródło: **monoblok powietrze–woda R290** (≤ 12 kW), niskotemperaturowy, z η_s ≥ 125% (ekoprojekt);
  * instalacja: **ogrzewanie podłogowe ≤ 35 °C**, regulacja pokojowa (termostaty + siłowniki) — spełnia WT § 135 ust. 7 i daje η_H,e = 0,89;
  * izolacja przewodów wg zał. 2 pkt 1.5.
* W PAB: **analiza alternatyw (RPB § 20 ust. 1 pkt 10)** — np. system konwencjonalny „kocioł gazowy kondensacyjny + c.w.u. gazowa” (sieć gazowa jest w drodze) vs alternatywny „PC R290 + PV + rekuperacja”. Obliczenia: EU i EP, koszty inwestycyjne i eksploatacyjne, emisja. Plus **analiza regulacji pomieszczeniowej (pkt 11)**.

### 3.5 Wentylacja mechaniczna z odzyskiem ciepła (bilans wywiewu wg PN-83/B-03430/Az3, wartości minimalne)

| Pomieszczenie (program z briefu) | Wywiew min. [m³/h] | Podstawa |
|---|---|---|
| Kuchnia P0 (kuchenka elektryczna/indukcyjna, rodzina 4–5 os.) | 50 (+ okresowo ≥ 120) | R6-38 |
| WC gościnne P0 | 30 | R6-38 |
| Łazienka przy pokoju gościnnym P0 | 50 | R6-38 |
| Spiżarnia, garderoba wejściowa (bezokienne) P0 | 15 + 15 | R6-38 |
| Pomieszczenie techniczne P0 (bezokienne) | 15 | R6-38 |
| Łazienka P1 | 50 | R6-38 |
| Pralnia P1 | ≥ 2 h⁻¹ (np. 8 m² × 2,6 m → ≈ 42) | R6-38 (W) |
| Łazienka rodziców P2 | 50 | R6-38 |
| Garderoba P2 (bezokienna) | 15 | R6-38 |
| **Suma (przykład)** | **≈ 330** | — |

* Nawiew ≥ max(Σ wywiewu, 20 m³/h × 5 os. = 100) → projekt ok. **330 m³/h** (bilans zrównoważony).
* Centrala o wydajności ok. 400–450 m³/h. Odzysk ≥ 85% (cel R6; WT nie wymaga, bo < 500 m³/h). Bypass, filtry min. ISO ePM1 50% na nawiewie i ISO Coarse na wywiewie (cel R6; wymóg WT: ≥ G4). SFP w granicach § 154 ust. 10–11. RVU zgodna z 1253/2014.
* Zakaz grawitacyjnych kratek w pomieszczeniach z wentylacją mechaniczną (§ 148 ust. 2). Okap kuchenny: recyrkulacyjny albo wywiew z osobnym przewodem i dopływem (decyzja w PT).
* **Czerpnia i wyrzutnia:**
  * preferowane na dachu P2: czerpnia ≥ 0,4 m nad dachem; wyrzutnia ≥ 1 m wyżej i ≥ 6 m (wyrzut pionowy) od czerpni albo zblokowany zestaw;
  * czerpnia dachowa ≥ 6 m od wywiewek kanalizacyjnych (wymóg § 152 ust. 4); dla wyrzutni ta sama odległość jest tylko zaleceniem R6, WT jej nie wymaga; wyrzutnia ≥ 3 m od krawędzi dachu z oknami poniżej (§ 152 ust. 12);
  * alternatywa — czerpnia ścienna ≥ 2 m nad terenem i ≥ 8 m od ulicy (front 6 m od linii rozgraniczającej: sprawdzić), od miejsca na odpady i wywiewek.
* Garaż nieogrzewany: otwory wentylacyjne ≥ 0,08 m² netto (np. w bramie i ścianie przeciwległej). Nie podłączać do rekuperacji.

### 3.6 Woda i c.w.u.
* Wodomierz główny w pomieszczeniu technicznym P0 (parter, wydzielone miejsce), za nim zawór antyskażeniowy (typ wg kategorii zagrożenia PN-EN 1717, np. EA na wejściu, HA/HB przy zaworach ogrodowych). Napełnianie c.o. przez zabezpieczenie odpowiedniej kategorii. Mostek wyrównawczy przed i za wodomierzem przy rurach metalowych.
* Ciśnienie przed punktami 0,05–0,6 MPa (zawór redukcyjny, jeśli sieć > 6 bar).
* Przepływ obliczeniowy wg PN-92/B-01706: q = 0,682·(Σq_n)^0,45 − 0,14. Przykład: Σq_n ≈ 3,3 dm³/s → q ≈ 1,03 dm³/s. Kontrola LU wg PN-EN 806-3.
* **C.w.u. z PC:**
  * zasobnik 250–300 dm³ (dobór wg PN-EN 12831-3 lub doświadczenia; wartość orientacyjna R6 — NIEZWERYFIKOWANE);
  * temperatura w punktach 55–60 °C; **grzałka lub program antylegionella 70–80 °C w punktach** (cykliczny, z kontrolą mieszania na wyjściu);
  * zawór bezpieczeństwa, naczynie przeponowe c.w.u.;
  * **termostatyczny zawór mieszający** na wyjściu (ochrona przed poparzeniem) przy dezynfekcji;
  * cyrkulacja z zegarem (η_W,d = 0,80) albo brak cyrkulacji przy przewodach ≤ 3 dm³ do punktów (dobra praktyka „reguły 3 litrów”; zob. też kryterium 3 l w art. 4i Dz.U. 2026 poz. 605 — dotyczy innych budynków).
* Wyroby w kontakcie z wodą pitną z certyfikatem wg nowego rozdz. 3b ustawy o PIS.

### 3.7 Kanalizacja sanitarna
* Grawitacyjna do sieci PVC 200 w drodze: przykanalik PVC-U (PN-EN 1401-1+A1:2023-09) DN150 lub DN160, spadek wg warunków gestora, studzienka rewizyjna na działce.
* Piony **DN100 (110)** z WC.
* Podejścia (praktyka, NIEZWERYFIKOWANE): umywalka DN40–50, natrysk, wanna, zlew, pralka, zmywarka DN50, WC DN100.
* Q_ww = 0,5·√ΣDU. Przykład: ΣDU ≈ 17 → ≈ 2,1 l/s.
* Wentylacja:
  * co najmniej **jeden pion wyprowadzony ponad dach** (ostatni na przewodzie odpływowym);
  * pozostałe piony mogą mieć zawory napowietrzające PN-EN 12380, montowane w miejscu dostępnym i wentylowanym;
  * wylot ≥ 4 m w poziomie od okien albo ponad ich górną krawędź;
  * wylot ≥ 6 m od czerpni dachowej.
* Skropliny z pompy ciepła: do gruntu w strefie niezamarzającej (studzienka żwirowa) albo do deszczówki z ochroną przed zamarzaniem. **Nie do studzienek w strefie R290.**

### 3.8 Wody opadowe (brak kanalizacji deszczowej)
* Rynny i spusty oraz wpusty dachowe: r = **0,03–0,05 l/(s·m²)**. Zalecenie R6: 0,046 l/(s·m²) ≈ PANDa C10, 5 min. Dachy płaskie z **przelewami awaryjnymi**.
* Retencja i rozsączanie metodą Aquanet (R6-62). Przykład dla A_red = 200 m² (0,02 ha — do podmiany na wartości z modelu):
  * [Poprawka weryfikacji: w pierwotnym przykładzie skrzynki 2,4 × 1,2 × 0,66 m mają objętość ok. 1,8 m³ netto, a wymagane V_min wynosiło 6,8 m³. Przykład był wewnętrznie sprzeczny.]
  * skrzynki 4,8 × 2,4 × 0,66 m → A_inf = 11,52 + ½·(14,4·0,66) = 16,27 m²; objętość brutto 7,60 m³, netto ≈ 7,2 m³ (porowatość ok. 95% — dana producentów, W; przyjąć wg DTR);
  * piasek średni k_f = 1·10⁻⁴ m/s → k_f,nn = 5·10⁻⁵ → Q_inf = 1000·16,27·5·10⁻⁵ = 0,81 l/s;
  * V_obl = max[0,06·q·0,02·t_d − 0,06·0,81·t_d] ≈ 4,2 m³ (t_d ≈ 30 min; q interpolowane log-log z tab. 3 Aquanet) → **V_min = 1,2·4,2 = 5,1 m³ ≤ 7,2 m³ (warunek spełniony)**; czas opróżniania V_min/Q_inf ≈ 1,7 h (< 24 h).
* Opcjonalnie szczelny zbiornik na podlewanie (≤ 5 m³ — bez zgłoszenia przy późniejszej realizacji) z przelewem do skrzynek. Osadnik przed skrzynkami.
* Lokalizacja: ≥ 1,5·h_f + 0,5 m od fundamentów (przy h_f ≈ 1,0 m → **≥ 2,0 m**). Dno ≤ 2,8 m p.p.t. (woda gruntowa 3,8 m). Nie kierować wód na działki sąsiednie (§ 29). **Wyniki k_f z badań geotechnicznych są wymagane** (R5).
* Dach garażu zielony ekstensywny ψ = 0,5. Nawierzchnie przepuszczalne podjazdu (ażur ψ 0,40) zmniejszają A_red.

### 3.9 Pompa ciepła — lokalizacja i hałas
* Czynnik **R290**. Moc dobrana do obciążenia cieplnego, przewidywana 6–10 kW (NIEZWERYFIKOWANE — po obliczeniu).
* Jednostka na fundamencie z wibroizolacją, **nie pod oknami sypialni**, poza strefą wjazdu. Strefa R290 (≥ 1 m wg DTR) wolna od okien, drzwi, wpustów, studzienek i zagłębień.
* Sprawdzenie hałasu na granicy działki (i przy oknach sąsiadów) dla nocy: **L_A ≤ 40 dB**, cel ≤ 35 dB. Przykład: L_WA = 55 dB(A), przy ścianie (Q = 4): 4 m → 38 dB; 8 m → 32 dB. Przy L_WA = 60 dB(A) potrzeba ≥ 6 m (39,5 dB). Tryb nocny (cichy) w specyfikacji.
* Na PZT wrysować jednostkę zewnętrzną, strefę R290 i odległość od granic. Działki wschodnia i zachodnia (MN) — preferowana strona południowa lub północno-zachodnia, z dala od granic bocznych.

### 3.10 PV
* **Moc modułów ≤ 6,5 kWp** (np. 15 × 430 Wp = 6,45 kWp) → **bez uzgodnienia ppoż.** (art. 29 ust. 4 pkt 3 lit. c PB).
* Przekroczenie 6,5 kWp → uzgodnienie z rzeczoznawcą ppoż., zawiadomienie PSP i plan dla ekip ratowniczych.
* Magazyn energii ≤ 30 kWh — bez dodatkowych formalności budowlanych.
* Przyłączenie: zgłoszenie mikroinstalacji do OSD.
* W EP liczy się tylko autokonsumpcja.
* Instalacja wg PN-HD 60364-7-712 (wyłączniki DC, oznakowanie), odbiór wg PN-EN 62446-1.

### 3.11 Zawartość dokumentacji (lista kontrolna R6)
* **PZT:** jednostka PC ze strefą R290; przyłącza wod.-kan. i nN; studzienka rewizyjna; wodomierz (jeśli w studni); skrzynki rozsączające z osadnikiem i odległościami; zbiornik deszczówki; czerpnia (jeśli terenowa).
* **PAB, opis:**
  * źródło ciepła i c.w.u.;
  * **analiza alternatyw (§ 20 ust. 1 pkt 10)**;
  * **analiza regulacji (§ 20 ust. 1 pkt 11)**;
  * parametry środowiskowe: woda i ścieki, wody opadowe, hałas PC, odpady (§ 20 ust. 1 pkt 9).
* **PT:**
  * opisy instalacji (§ 23 pkt 7–8);
  * **charakterystyka energetyczna (§ 23 pkt 11 a–d)**;
  * obliczenia: U, ψ, f_Rsi, obciążenie cieplne, strumienie wentylacji, woda, kanalizacja, retencja;
  * rysunki instalacji i detale mostków (§ 24).

### 3.12 Propozycja wpisu do modelu (`model/budynek.yaml`, sekcja energia/instalacje — do uzgodnienia ze schematem)
```yaml
energia:
  metodologia: "Dz.U. 2015 poz. 376 ze zm. (ost. 2023 poz. 697)"
  w_el_siec: 2.50
  w_pv_autokonsumpcja: 0.00
  EP_max: 70.0            # + 5*Af_C/Af jeśli chłodzenie
  Q_W_nd_kWh_m2a: 24.09   # V_Wi=1.4, kR=0.9, 55/10 °C
  q_int_W_m2: 6.8
  stacja_klimatyczna: "Poznań (BIP ministerstwa)"
  theta_e: -18
  theta_me: 7.9
  theta_int: {pokoj: 20, lazienka: 24, garaz_nieogrzewany: null}
przegrody_U_cel: {sciana: 0.15, stropodach: 0.12, podloga_grunt: 0.20, okno: 0.80, drzwi_zewn: 1.10, sciana_dom_garaz: 0.25}
przegrody_U_max_WT: {sciana: 0.20, stropodach: 0.15, podloga_grunt: 0.30, okno: 0.90, drzwi_zewn: 1.30, sciana_ogrz_nieogrz: 0.30}
okna_g_max: 0.35
n50_cel: 1.0
wentylacja:
  wywiew_min_m3h: {kuchnia: 50, lazienka: 50, wc: 30, bezokienne: 15, pralnia_krotnosc: 2}
  nawiew_min_na_osobe: 20
  osoby: 5
  odzysk_cel: 0.85
pompa_ciepla: {typ: "monoblok powietrze-woda", czynnik: R290, strefa_bezp_m: 1.0, LAeq_noc_granica_dB: 40}
cwu: {T_punkty: [55, 60], T_dezynfekcja: [70, 80], cyrkulacja: "czasowa lub brak"}
pv: {moc_kWp_max: 6.5}
deszcz: {r_rynny_l_s_m2: 0.046, model: "PANDa 2050 Poznań C10", fb: 1.2, kf_nn_wsp: 0.5}
```

---

## 4. Nierozstrzygnięte

1. **Status WT po 20.09.2026** (R1, R3). Wszystkie wymagania z WT w tym rejestrze zakładają oświadczenie inwestora z art. 102a PB. Bez oświadczenia nie ma formalnej podstawy dla EP_max = 70 ani U_max. Stosować je wtedy jako „zasady wiedzy technicznej” (PB art. 5). Decyzja: R1 i inwestor.
2. **Które wydanie PN-EN 12831 stosować.** WT zał. 1 lp. 16 powołuje datowaną PN-EN 12831:2006 (wycofaną). Aktualna PN-EN 12831-1:2017-08 istnieje tylko po angielsku i bez polskiego NA w katalogu PKN. Propozycja: obliczenia formalne wg 2006 (zgodność z WT), wynik kontrolny wg 2017. Decyzja zespołu instalacyjnego.
3. **SCOP do EP.** Metodologia pozwala na „dane udostępnione przez producenta”. Nie określa jednak, czy użyć SCOP dla klimatu umiarkowanego (PN-EN 14825), czy wartości przeliczonej na klimat PL. Brak wytycznych ministerialnych — NIEZWERYFIKOWANE. Przyjąć SCOP „average” dla 35 °C i opisać założenie.
4. **Bilansowanie PV w EP.** Nie ustalono kroku czasowego ani metody wyznaczenia autokonsumpcji (godzinowy lub miesięczny). Brak wytycznych — przyjąć zachowawczo, np. miesięczny udział autokonsumpcji z symulacji godzinowej, i opisać.
5. **Pozwolenie wodnoprawne na skrzynki rozsączające.** Art. 16 pkt 65 lit. f i art. 389 pkt 6 Prawa wodnego wobec praktyki. Istnieją decyzje Wód Polskich wydające pozwolenia na zespoły skrzynek. Opcje: (a) uzyskać stanowisko Wód Polskich (RZGW Poznań); (b) zaprojektować rozsączanie powierzchniowe (niecka lub ogród deszczowy) bez „wylotu”; (c) ująć pozwolenie w harmonogramie. Decyzja: R8 i inwestor.
6. **Przepływy wody — rozbieżności wtórne.** Natrysk 0,07 vs 0,15 dm³/s; płuczka 0,13 vs 0,30. Przyjęto wartości PWr (0,15 + 0,15; 0,13). Potwierdzić w tekście PN-92/B-01706 (Az1:1999).
7. **ψ domyślne (ISO 14683 zał. C), współczynnik α dla łączników (ISO 6946 zał. F), wzory ISO 13370 dla podłogi na gruncie.** Brak dostępu do tekstu normy. Do weryfikacji przez zespół fizyki budowli z egzemplarzem normy (PKN).
8. **PN-EN 12056-2** — przepustowości pionów, limity podejść niewentylowanych, minimalne średnice podejść: NIEZWERYFIKOWANE (tabele normy niedostępne).
9. **Rewizja ekoprojektu 813/2013** (konsultacje do 23.01.2026). Wg EUR-Lex (2026-09-25) 813/2013 nadal „In force”, bez daty końca obowiązywania. Obowiązują więc limity z R6-71. Czy nowy akt przyjęto z późniejszą datą stosowania — NIEZWERYFIKOWANE.
10. **Warunki techniczne przyłączenia wody i kanalizacji** (przedsiębiorstwo gminne lub Aquanet): lokalizacja wodomierza (budynek lub studnia), rodzaj zaworu antyskażeniowego, spadki przykanalika — fikcyjne, przyjąć w PZT jako założenia.
11. **Dane klimatyczne do EP (BIP ministerstwa)** — aktualny zbiór i stacja: NIEZWERYFIKOWANE. Pobrać przy obliczeniach.
12. ~~Prawo energetyczne po zmianie Dz.U. 2026 poz. 516~~ — **rozstrzygnięte przez weryfikację:** zmiany 2026 poz. 516, 607 i 900 nie dotyczą art. 7 ust. 8d4–8d6 (R6-79). Zgłoszenie mikroinstalacji do OSD bez zmian.
13. **Filtry:** WT § 154 ust. 6 (G4 wg PN-EN 779, wycofanej) wobec klasyfikacji PN-EN ISO 16890 — brak oficjalnej tabeli przejścia. Przyjąć wyższą klasę (ISO ePM10/ePM1).
