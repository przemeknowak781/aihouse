# Zero-emisyjność budynku UMWD – prawo UE i PL, Załącznik M.12, rozbieżności (stan prawny na 16.11.2026)

| | |
|---|---|
| Stan prawny | **16.11.2026**. Polskie akty sprawdzono w API ELI Sejmu (api.sejm.gov.pl) i ISAP. Akty UE sprawdzono w EUR-Lex: teksty w języku polskim, pobrane 16.11.2026 |
| Obiekt | budynek administracyjny UMWD z salą obrad Sejmiku na najwyższych kondygnacjach. Dominanta ma 35–45 m, więc budynek należy do grupy **W** (25–55 m; § 8 WT, zob. `wt_kluczowe.md`). Ma 2 kondygnacje podziemne z garażem. Stoi w zabudowie śródmiejskiej, w obszarze wpisanym do rejestru zabytków (538/A/05). Inwestor: Województwo Dolnośląskie, w imieniu którego działa Inwestycje Dolnośląskie Sp. z o.o. Grunt jest własnością Województwa |
| Pliki powiązane | `strategia_energetyczna.md` (strategia i liczby), `_bilans_energii.py` (obliczenia szacunkowe), `wt_kluczowe.md` (WT, art. 102a Pb, rozdz. 12–13), `ppoz.md` (PV/BESS i elewacja > 25 m), `../30_lokalizacja/mpzp.md` (konflikt K-05), `../20_program/program.md` (powierzchnie) |
| Zakaz Inwestora | nie korzystano z informacji o pracach nagrodzonych ani konkurencyjnych w tym konkursie. Nie wyszukiwano ich i żadne przejrzane źródło ich nie zawierało |

**Oznaczenia statusu:**
- **[O]** – przepis polski obowiązujący 16.11.2026.
- **[P]** – przepis, który utracił moc, ale można go stosować przejściowo (art. 102a Pb).
- **[UE]** – akt UE obowiązujący. Dyrektywa wiąże państwo i działa wobec inwestora dopiero po transpozycji. Rozporządzenie UE działa bezpośrednio.
- **[UE-NT]** – przepis dyrektywy, którego Polska nie przetransponowała.
- **[PR]** – projekt aktu (nie obowiązuje).
- **wniosek** – wniosek własny, nie przepis.
- *źródło wtórne* – portal lub opracowanie branżowe, użyte pomocniczo.

Numery [Z..] odsyłają do wykazu źródeł w rozdz. 13.

---

## 0. Najważniejsze wnioski (TL;DR)

1. **Data „1 stycznia 2027 r.” z Regulaminu (rozdz. III ust. 1 pkt 10) i z M.12 nie wynika z obowiązującego prawa.** Pochodzi z **wniosku Komisji COM(2021) 802** (art. 7 ust. 1 lit. a: „od dnia 1 stycznia 2027 r. – nowe budynki zajmowane lub będące własnością organów publicznych”) [Z2]. Przyjęta **dyrektywa (UE) 2024/1275** mówi w art. 7 ust. 1 lit. a: **od 1 stycznia 2028 r.** dla nowych budynków **będących własnością instytucji publicznych**, a od 1 stycznia 2030 r. dla wszystkich nowych budynków [Z1]. Z wniosku Komisji pochodzi też formuła M.12 o „bilansowaniu rocznym” produkcji OZE i zużycia (wniosek mówił o pokrywaniu zużycia „on a net annual basis” – „w ujęciu rocznym netto”, zał. III wniosku). <!-- poprawione przez weryfikatora --> **Dyrektywa zachowuje wymóg pokrycia *całkowitego rocznego* zużycia energii pierwotnej ZEB** (art. 11 ust. 7), ale ze źródeł na miejscu, w pobliżu, ze społeczności energetycznej OZE, z efektywnego systemu ciepłowniczego lub ze źródeł bezemisyjnych, a gdy to niewykonalne – z sieci. **Nie wymaga, by produkcja OZE na działce równoważyła roczne zużycie** – to wymóg M.12, ostrzejszy od dyrektywy. Data 2027 występuje w dyrektywie tylko przy innych obowiązkach: plan działania GWP do 1.01.2027 (art. 7 ust. 5) i punkty ładowania w istniejących budynkach niemieszkalnych > 20 miejsc do 1.01.2027 (art. 14 ust. 2).
2. **Budynek UMWD najpewniej i tak podlegałby standardowi bezemisyjnemu (ZEB).** Województwo jest „instytucją publiczną” w rozumieniu art. 2 pkt 12 dyrektywy (UE) 2023/1791 („władze … regionalne”) [Z4]. Obowiązek dotyczy nowych budynków od 1.01.2028. Państwo może wyłączyć budynki, dla których wniosek o pozwolenie na budowę (PnB) złożono przed tą datą (art. 7 ust. 4). Polski projekt nowych WT przewiduje ZEB dla „budynku będącego własnością jednostki sektora finansów publicznych od 1 stycznia 2028 r.” i przepisy przejściowe dla wniosków złożonych przed wejściem w życie rozporządzenia (§ 392) [Z11]. Wniosek o PnB dla tej inwestycji zostanie złożony realnie w latach 2027–2028, więc objęcie obowiązkiem jest prawdopodobne. JST są jednostkami sektora finansów publicznych (art. 9 pkt 2 ustawy o finansach publicznych) [Z19]. → **wniosek:** projektować jako ZEB w rozumieniu art. 11 dyrektywy. W opisie pracy podać poprawną podstawę, bez polemiki z Zamawiającym.
3. **Definicja ZEB w dyrektywie (art. 2 pkt 2, art. 11)** obejmuje cztery elementy:
   - **zero emisji CO₂ z paliw kopalnych na miejscu** (żadnego spalania gazu ani oleju w budynku i na działce);
   - zapotrzebowanie na energię pierwotną **co najmniej 10% niższe od krajowego progu nZEB** z 28.05.2024 r.;
   - operacyjne emisje GHG poniżej progu krajowego;
   - całe roczne zużycie energii pierwotnej pokrywane z OZE na miejscu lub w pobliżu, ze społeczności energetycznej OZE, z **efektywnego systemu ciepłowniczego** (art. 26 ust. 1 dyrektywy 2023/1791) albo ze źródeł bezemisyjnych. Gdy to niewykonalne, dopuszcza się inną energię z sieci.

   **Załącznik III dyrektywy dotyczy obliczania GWP, nie progów ZEB.** Liczbowe progi ZEB (np. biura, strefa kontynentalna: < 85 kWh/(m²·rok) energii pierwotnej całkowitej) były tylko w zał. III **wniosku** Komisji. Od 24.05.2026 zał. III dyrektywy zastąpiło rozporządzenie delegowane **(UE) 2026/52** – unijne ramy obliczania GWP w cyklu życia [Z3].
4. **Transpozycja w Polsce nie została zakończona (16.11.2026).** Termin z art. 35 dyrektywy minął 29.05.2026.
   - Ustawa o charakterystyce energetycznej budynków ma t.j. Dz.U. 2024 poz. 101. Ostatnia nowelizacja weszła w życie 1.10.2023 (wg metryki ELI) [Z8].
   - W Dz.U. 2025–2026 nie ma aktu z tytułem o charakterystyce energetycznej ani nowych WT dla budynków.
   - 15.07.2026 Komisja wysłała **wezwania do usunięcia uchybienia wszystkim 27 państwom** za brak pełnej notyfikacji transpozycji dyrektywy 2024/1275 [Z7].
   - Projekty: ustawa UC82, obejmująca m.in. EPBD (*źródło wtórne*, status niepotwierdzony, bo RCL był niedostępny) [Z15]; nowe WT (projekt 13.05.2026; wersja 6.08.2026 notyfikowana KE wg `wt_kluczowe.md`; planowane wejście w życie 20.09.2026 nie nastąpiło) [Z11]; <!-- poprawione przez weryfikatora --> nowelizacja Prawa energetycznego UC121 – nowe kryteria efektywnego systemu ciepłowniczego wg art. 26 EED (projekt OSR z 15.05.2026) [Z14].
5. <!-- poprawione przez weryfikatora --> **Na 16.11.2026 w Polsce nie obowiązują żadne warunki techniczne dla budynków.** WT 2002 utraciły moc z upływem 84 miesięcy od wejścia w życie ustawy o dostępności (art. 66 ustawy z 19.07.2019, t.j. Dz.U. 2024 poz. 1411). Art. 102a Pb mówi o przepisach „obowiązujących do dnia 19 września 2026 r.”, a ISAP/ELI podaje datę 21.09.2026. Nowe WT nie zostały ogłoszone: projekt przewidywał wejście w życie 20.09.2026 (§ 394 projektu), a w Dz.U. 2026 nie ma takiego aktu (sprawdzono w ELI). **Pomost: art. 102a Pb** (dodany przez art. 2 pkt 4 ustawy Dz.U. 2026 poz. 1161, w życie 2.09.2026). W okresie 18 miesięcy od 20.09.2026 (koniec ok. 19–20.03.2028; bezpiecznie przyjąć 19.03.2028) PZT i PAB do wniosku o PnB **może** zostać sporządzony według WT 2002. Wymaga to **oświadczenia inwestora**, a wtedy projekt techniczny i decyzje dla całego zamierzenia także opierają się na WT 2002 (ust. 2 i 4). Szczegóły w `wt_kluczowe.md`. Limity WT 2002 (stosowane fakultatywnie):
   - **EPmax** budynku użyteczności publicznej: **45 + ΔEPC 25 + ΔEPL 25/50** kWh/(m²·rok): **95** przy pełnym chłodzeniu i t₀ < 2500 h; **120**, gdy t₀ ≥ 2500 h. **Uwaga (NIEPEWNE):** domyślny czas działania oświetlenia w biurach wg PN-EN 15193 to prawdopodobnie 2250 + 250 = 2500 h, a wtedy ΔEPL = 50. Wartość 95 jest więc **zachowawcza**. Normy nie zweryfikowano w PKN;
   - **Uc,max**: ściany 0,20; dach 0,15; okna i fasady 0,9 W/(m²K);
   - **g ≤ 0,35**.

   Projekt nowych WT od 1.01.2028 dla JSFP: **EPH+W 40, ΔEPC 22, ΔEPL 23/45**, zakaz emisji CO₂ z paliw kopalnych na miejscu, próg emisji operacyjnych **ECO2,ZEB = 0,000274·EPZEB + 0,0081 t CO₂/(m²·rok)**, obowiązek instalacji słonecznej dla budynku niemieszkalnego > 250 m² [Z11].
6. **Ciepło sieciowe Wrocławia (Fortum) jest dziś formalnie „efektywnym systemem ciepłowniczym”**. Sprawozdanie za 2025 r. [Z20]: **85,11% ciepła z kogeneracji**, OZE 1,22%, ciepło odpadowe 0,35%, w = 0,620. Polskie kryterium to art. 7b ust. 4 pkt 3 Prawa energetycznego (≥ 75% kogeneracji), zgodne z art. 26 ust. 1 lit. a EED (do 31.12.2027). Ocena według okresów:
   - **od 2028 r.** status będzie zależał od tego, czy ≥ 80% ciepła pochodzi z **wysokosprawnej** kogeneracji (warunek alternatywny: OZE ≥ 5% przy ≥ 50% łącznie OZE, ciepła odpadowego i **wysokosprawnej** kogeneracji – art. 26 ust. 1 lit. b EED); <!-- poprawione przez weryfikatora -->
   - **od 2035 r.** obecny miks nie spełni kryteriów (wymagane ≥ 35% OZE lub ciepła odpadowego).

   **Wniosek:** decyzja M.12, by sieć była **tylko źródłem rezerwowym i szczytowym**, jest trafna. ZEB oparty na sieci byłby formalnie możliwy dziś, ale nietrwały w cyklu życia budynku.
7. **Obowiązek przyłączenia do sieci ciepłowniczej (art. 7b ust. 1 Prawa energetycznego) nie koliduje z gruntowymi pompami ciepła.** Wyłączenie z ust. 3 obejmuje indywidualne źródło o **wskaźniku w ≤ 0,8** i **≥ 60% ciepła z OZE**. Spełnienie stwierdza audyt (ust. 3c) [Z13]. Przy w_el = 2,5 (Dz.U. 2023 poz. 697) [Z9] gruntowa PC spełnia oba warunki, gdy SCOP ≥ 3,125, a z zapasem ≥ 3,2 (wniosek: w = 2,5/SCOP ≤ 0,8; udział OZE = 1 − 1/SCOP ≥ 60% już od SCOP 2,5). <!-- poprawione przez weryfikatora -->
8. **Odwierty pomp ciepła:**
   - do 30 m są poza ustawą PGiG (art. 3 pkt 2);
   - powyżej 30 m – projekt robót geologicznych **zgłasza się staroście**, czyli Prezydentowi Wrocławia (art. 85 ust. 1–3; art. 161 ust. 2 pkt 5); sprzeciw może wpłynąć w 30 dni;
   - **powyżej 100 m** stosuje się przepisy o zakładzie górniczym (art. 86) [Z17].

   → **wniosek:** odwierty ≤ 100 m (np. 99 m). Układ otwarty na wodach podziemnych wymaga pozwolenia wodnoprawnego. Zrzut wód z pomp ciepła do wód podziemnych dopuszcza art. 76 ust. 1 pkt 5 Prawa wodnego [Z18].
9. **Konflikty prawa miejscowego i przepisów ppoż. z wymaganiem PV 0,4–1,0 MWp (M.12):**
   - MPZP § 6 pkt 13 zakazuje „urządzeń technicznych i budowlanych” na **dachach** oraz na **elewacjach od placów, bulwarów i ulic** [Z26] (`mpzp.md` K-05);
   - WT § 216 ust. 8: okładzina elewacji **powyżej 25 m** musi być niepalna (`ppoz.md` 7.7).

   → **wniosek:** PV jako **pokrycie dachu i element przegrody (BIPV)**, a nie urządzenie nadstawione; BIPV elewacyjne na elewacjach od dziedzińca i do 25 m; BIPV powyżej 25 m tylko przy potwierdzonej klasyfikacji ogniowej. Realny potencjał PV na działce to **ok. 0,40 MWp, warunkowo 0,50 MWp**. **1,0 MWp na działce jest nieosiągalne** bez naruszenia MPZP, przepisów ppoż. i wymagań konserwatorskich (szczegóły w `strategia_energetyczna.md`).
10. **Dyrektywa wymaga też elementów, których M.12 nie wymienia. Warto pokazać je na planszy jako atut:**
    - obliczenie **GWP w cyklu życia** (nowe budynki > 1000 m² od 1.01.2028; zał. III w brzmieniu rozp. 2026/52: 50 lat, kg CO₂e/m² powierzchni użytkowej, moduły A–C, D osobno) [Z1][Z3];
    - monitorowanie jakości powietrza wewnętrznego w niemieszkalnych ZEB (art. 13 ust. 5);
    - BACS dla mocy > 290 kW i automatyczne sterowanie oświetleniem (art. 13 ust. 9–12);
    - e-mobilność: w nowych **biurowcach 1 punkt ładowania na 2 miejsca**, okablowanie wstępne ≥ 50%, rowery ≥ 15% średniej lub 10% całkowitej liczby użytkowników (art. 14 ust. 1) [UE-NT]. Obowiązujące prawo polskie wymaga ≥ 1 punktu i kanałów kablowych na 1 punkt / 5 stanowisk (art. 12a ustawy o elektromobilności) oraz mocy przyłączeniowej pozwalającej wyposażyć **wszystkie** stanowiska w punkty ≥ 3,7 kW (art. 12) [Z16];
    - przyszły obowiązek SRI dla budynków niemieszkalnych > 290 kW (akt delegowany do 30.06.2027, art. 15 ust. 2).

---

## 1. Załącznik M.12 – treść, wymagania, uwagi

### 1.1. Treść (przeczytano w całości: 3 strony, `00_materialy/tekst/M.12._STANDARD_ZERO-EMISYJNOŚCI.txt`)

**Uwagi redakcyjne (fakt):**
- okładka M.12 nosi datę 2025.10.29;
- na okładce znajduje się omyłkowa „informacja” o standardach dostępności MSWiA (pozostałość po M.13);
- w nagłówku stron wewnętrznych dokument nazwany jest „Załącznik M.09”. Merytorycznie chodzi o M.12 (Regulamin rozdz. III ust. 1 pkt 10 i rozdz. XII pkt 12).

**Pkt 1. Zero emisyjność.** Budynek „powinien być zaprojektowany jako budynek zeroemisyjny wykorzystujący OZE”. Uzasadnienie M.12: wymóg UE „od 1 stycznia 2027 roku w przypadku wszystkich nowych budynków zajmowanych przez władze publiczne lub będących ich własnością” (por. rozdz. 3). Definicja robocza M.12: „budynek w całym cyklu użytkowania nie generuje emisji dwutlenku węgla związanych z eksploatacją”, „nie występują źródła spalania paliw kopalnych”, a energia „pochodzi z OZE wytwarzanych lokalnie lub w pobliżu”. Zasady:

| # | Zasada M.12 | Uwaga (wniosek) |
|---|---|---|
| a | bardzo niskie zapotrzebowanie na energię (wysoka efektywność) | zgodne z art. 11 ust. 2–3 dyrektywy (próg ≤ 90% nZEB) |
| b | OZE: PV, pompy ciepła, magazyny energii | – |
| c | brak lokalnych emisji CO₂ – żadnych kotłów gazowych i olejowych | zgodne z art. 11 ust. 1. **Uwaga:** agregat prądotwórczy (PU s. 13, s. 16) to źródło spalania. Zalecenie: paliwo HVO100, praca tylko w testach i awariach, krótkie zaniki pokrywa BESS (rozdz. 11 R-08) |
| d | **bilansowanie energii – produkcja OZE równoważy roczne zużycie** | wymóg **ostrzejszy** niż dyrektywa: brzmienie wniosku COM(2021) 802 („w ujęciu rocznym netto”). Na działce realne dla zużycia regulowanego (EPB), nie dla całego zużycia (rozdz. 4 strategii) |
| e | integracja z BMS/EMS, praca w trybie samowystarczalnym | interpretacja (wniosek): tryb wyspowy dla odbiorów krytycznych (serwerownia TIER II, MDS, BMS, oświetlenie awaryjne, dźwig), nie dla całego budynku |

**Zakres do zaprojektowania (pkt 1 A–E):**
- **A. Gruntowe pompy ciepła** – „główne źródło ciepła i chłodu”, praca rewersyjna. Wymagana **analiza liczby odwiertów, ich głębokości i łącznej długości czynnej**. **Odwierty można lokalizować pod budynkiem.**
- **B. PV 0,4–1,0 MWp** „montowanych na dachu dominanty i elewacjach”.
- **C. Magazyny ciepła i chłodu:**
  - krótkoterminowe – zbiorniki buforowe w pomieszczeniach technicznych;
  - **sezonowy** – „ładowany nadmiarem energii latem (chłód) i oddający ciepło zimą”. Wniosek: tę funkcję pełni sam pionowy wymiennik gruntowy pracujący jako magazyn sezonowy BTES (lato: oddawanie ciepła z chłodzenia do gruntu; zima: pobór).
- **D. Magazyn energii elektrycznej z PV** („należy przewidzieć możliwość”).
- **E. Sieć ciepłownicza** – „jedynie funkcja rezerwowa i szczytowa”.
- Uwzględnić **akumulację cieplną konstrukcji i zyski ciepła**, z preferencją dla rozwiązań pasywnych. Rozwiązania „sprawdzone i optymalne” technicznie i kosztowo.

**Pkt 2. Rozwiązania proekologiczne:**
- **A. Woda wyłącznie z sieci miejskiej**, bez własnego ujęcia (zgodne z MPZP § 14 pkt 2). Należy maksymalnie ograniczyć pobór wody przez retencję i ponowne użycie wody opadowej i szarej.
- **B. Retencja:**
  - podczyszczanie wód z dachów i nawierzchni utwardzonych;
  - **zbiorniki retencyjne na terenie zewnętrznym**;
  - wykorzystanie do podlewania zieleni, nawadniania dachu zielonego (jeśli będzie), mycia nawierzchni i **spłukiwania toalet po podczyszczeniu**;
  - przelew awaryjny do sieci.
- **C. Woda szara:** rozdział kanalizacji na **ścieki czarne** (WC, pisuary – do sieci) i **szare** (umywalki, prysznice, zmywarki – podczyszczanie i spłukiwanie WC). **Zakaz łączenia instalacji wody pitnej i szarej.**
- **D. Odzysk ciepła z wody szarej:** analiza możliwości z integracją z c.w.u., wentylacją i pompami ciepła, wraz z oceną ekonomiczną.

### 1.2. Powiązane wymagania Regulaminu, Programu i formularzy (fakt)

| Źródło | Wymaganie | Konsekwencja (wniosek) |
|---|---|---|
| Regulamin rozdz. III ust. 1 pkt 10 | wymóg zero-emisyjności („od 1 stycznia 2027”), woda szara; **szczegółowa ocena ekspertów Sądu w Etapie II: koszty inwestycyjne, operacyjne i efektywność ekologiczna** | potrzebne liczby: bilans energii i emisji, koszty w F.14.B, koszty eksploatacji |
| Regulamin rozdz. III ust. 1 pkt 9 | trwałość, niskie koszty eksploatacji, rezerwy w szachtach i na tarasach technicznych | rezerwy na rozbudowę PV/BESS, okablowanie EV |
| Regulamin rozdz. III ust. 1 pkt 11 | pierwszorzędnym kryterium jest jakość funkcjonalna i przestrzenna | ekologia nie może psuć architektury; integracja (BIPV, zieleń) |
| Regulamin rozdz. VI ust. 1 i rozdz. VIII ust. 1 pkt 1 lit. d | kryterium pierwszorzędowe (równoważne innym): **„zastosowanie rozwiązań proekologicznych i energooszczędnych oraz ich efektywność i zasadność”**; drugorzędowe: realność ekonomiczna inwestycji i utrzymania | liczy się „zasadność” – rozwiązania uzasadnione liczbami, bez gadżetów |
| Regulamin, Etap II, część graficzna lit. h | **„Schemat rozwiązań pro-ekologicznych i zrównoważonych zastosowanych w budynku”** | treść schematu: `strategia_energetyczna.md` rozdz. 9 |
| Regulamin, Etap II, część opisowa | opis rozwiązań proekologicznych i energooszczędnych (≤ 10 stron A4) | tekst wzorcowy: `strategia_energetyczna.md` rozdz. 10 |
| PU s. 3 | „Budynek ma spełniać wymogi obiektu zeroemisyjnego … oparta na źródłach odnawialnych … woda szara i wody opadowe” | – |
| PU s. 13–15 | piętro techniczne; **na dachu tylko urządzenia, których nie da się umieścić na piętrze technicznym**; SN/nn, agregaty, UPS, PV z magazynami; wentylacja z rekuperacją i klimatyzacja we wszystkich strefach; ciepło z OZE, „np. pomp gruntowych”; rozdział kanalizacji pod wodę szarą; retencja i infiltracja (zbiorniki, studnie chłonne, rozsączanie, PBC) | – |
| PU s. 16 | serwerownia ≤ 50 m², TIER II (zasilanie dwutorowe, SZR, UPS, agregat) | ciepło odpadowe serwerowni do pętli pomp ciepła |
| PU s. 17 | **dopuszcza się zielony dach ekstensywny** na części dachu | biosolar (PV nad zielenią) |
| PU s. 12 | parking podziemny „wyposażony w infrastrukturę ładowania pojazdów elektrycznych”; 50 stanowisk rowerowych w parterze (Wyj. 7/32: nie na −1) | EV i rowery: rozdz. 2.8 |
| F.14.B | pozycje m.in.: 2.12 (system ciepła i chłodu z pomp ciepła), 2.13 (PV), 7.1/7.3 (woda szara), 7.8–7.9 (instalacje PC, magazyny ciepła), 8.17 (PV z magazynem energii), 15.9 (stacje ładowania), 15.10 (retencja), 17 (rozwiązania proekologiczne, 17.1 rekuperacja) | wycena orientacyjna: `strategia_energetyczna.md` rozdz. 6.6 |
| F.15.C | wiersz I.13 „powierzchnia dachów zielonych”; 3.3 PBC na dachach i tarasach | PBC dachów liczy się w 50% (WT § 3 pkt 22) |

---

## 2. Dyrektywa (UE) 2024/1275 (EPBD recast) [UE] – przepisy kluczowe dla projektu

Akt: dyrektywa Parlamentu Europejskiego i Rady (UE) 2024/1275 z 24.04.2024 w sprawie charakterystyki energetycznej budynków (wersja przekształcona), **Dz.Urz. UE L 2024/1275 z 8.5.2024**. Weszła w życie 20. dnia po publikacji, tj. **28.05.2024**. Termin transpozycji: **29.05.2026** (art. 35 ust. 1). Dyrektywa 2010/31/UE utraciła moc 30.05.2026 (art. 36) [Z1].

### 2.1. Definicje (art. 2)
- **pkt 2 „budynek bezemisyjny”** – „budynek o bardzo wysokiej charakterystyce energetycznej określonej zgodnie z załącznikiem I, wymagający zerowej lub bardzo małej ilości energii, niewytwarzający na miejscu emisji dwutlenku węgla z paliw kopalnych i wytwarzający zerowe lub bardzo małe ilości operacyjnych emisji gazów cieplarnianych, zgodnie z art. 11”.
- **pkt 5 „instytucje publiczne”** – odesłanie do art. 2 pkt 12 dyrektywy 2023/1791: „władze krajowe, regionalne lub lokalne oraz podmioty bezpośrednio finansowane i zarządzane przez te władze, lecz niemające charakteru przemysłowego ani handlowego” [Z4]. → Samorząd województwa to „władza regionalna” (wniosek).
- **pkt 54 „na miejscu”** – „w lub na określonym budynku lub na działce, na której znajduje się ten budynek”.
- **pkt 55 „energia ze źródeł odnawialnych wytwarzana w pobliżu”** – energia wytwarzana lokalnie, która łącznie: (a) jest dystrybuowana i wykorzystywana tylko lokalnie przez **specjalny system dystrybucyjny**, (b) pozwala obliczyć szczegółowy współczynnik energii pierwotnej, (c) jest wykorzystywana przez **specjalne podłączenie**. → Zwykły zakup „zielonej energii” z sieci **nie jest** energią „w pobliżu” (wniosek). Może mieścić się w art. 11 ust. 7 lit. b (społeczność energetyczna OZE) lub w akapicie drugim (energia z sieci spełniająca kryteria krajowe).
- **pkt 33–34** – punkt ładowania; „okablowanie wstępne” to kable, trasy kablowe, transmisja danych i liczniki, które umożliwiają późniejszy montaż punktu ładowania.

### 2.2. Art. 7 – nowe budynki (terminy)
- **ust. 1** – nowe budynki mają być **bezemisyjne zgodnie z art. 11**: lit. a) **od 1.01.2028 r. – nowe budynki będące własnością instytucji publicznych**; lit. b) od 1.01.2030 r. – wszystkie nowe budynki. Do tego czasu – co najmniej nZEB. Gdy instytucja publiczna zamierza **zająć** budynek, który nie jest jej własnością, „dąży do tego”, by był bezemisyjny.
- **ust. 2** – **GWP w cyklu życia** obliczany wg zał. III i ujawniany w świadectwie charakterystyki energetycznej: lit. a) **od 1.01.2028 – nowe budynki o powierzchni użytkowej > 1000 m²**; lit. b) od 1.01.2030 – wszystkie nowe budynki.
- **ust. 3** – akt delegowany o unijnych ramach obliczania GWP do 31.12.2025. Przyjęty jako **rozporządzenie delegowane (UE) 2026/52** (rozdz. 2.8).
- **ust. 4** – państwo **może** nie stosować ust. 1–2 do budynków, dla których **wniosek o PnB złożono przed terminami**.
- **ust. 5** – do **1.01.2027** państwa publikują plan działania z wartościami granicznymi GWP dla nowych budynków od 2030 r. (stan dla Polski: nie ustalono).
- **ust. 6** – przy nowych budynkach państwa uwzględniają jakość środowiska wewnętrznego, adaptację do zmian klimatu, bezpieczeństwo pożarowe, ryzyko sejsmiczne i dostępność dla osób z niepełnosprawnościami, a także pochłanianie dwutlenku węgla związane z jego magazynowaniem w budynkach lub na nich (np. w drewnie konstrukcyjnym). <!-- poprawione przez weryfikatora -->

### 2.3. Art. 11 – wymagania dla budynku bezemisyjnego
- **ust. 1** – budynek ZEB **„nie może powodować na miejscu żadnych emisji dwutlenku węgla z paliw kopalnych”**. Jeśli jest to wykonalne, musi reagować na sygnały zewnętrzne (elastyczność zużycia, wytwarzania i magazynowania).
- **ust. 2–3** – krajowy **maksymalny próg zapotrzebowania na energię** dla ZEB ma być **co najmniej o 10% niższy** od progu całkowitego zużycia energii pierwotnej dla nZEB obowiązującego 28.05.2024. W Polsce próg nZEB dla budynku użyteczności publicznej „pozostałego” wynosi EPH+W 45 + ΔEPC 25 + ΔEPL 25/50. Projekt WT wpisuje 40/22/23/45, czyli ok. −10% [Z11].
- **ust. 5** – operacyjne emisje GHG ZEB poniżej krajowego progu (projekt WT: wzór w rozdz. 5.2).
- **ust. 7** – **całkowite roczne zużycie energii pierwotnej** ZEB pokrywa się z:
  - a) OZE na miejscu lub w pobliżu (kryteria art. 7 RED);
  - b) OZE ze **społeczności energetycznej** działającej w zakresie OZE (art. 22 RED);
  - c) **efektywnego systemu ciepłowniczego i chłodniczego** wg art. 26 ust. 1 dyrektywy 2023/1791;
  - d) **źródeł bezemisyjnych**.

  Jeśli to niewykonalne technicznie lub ekonomicznie – także „inną energią pochodzącą z sieci, która spełnia kryteria ustanowione na poziomie krajowym”.

  <!-- poprawione przez weryfikatora --> **Wniosek:** ust. 7 to wymóg **rocznego pokrycia** całego zużycia energii pierwotnej (bilans roczny w sensie źródeł). Nie wymaga natomiast, by produkcja na działce równoważyła zużycie. Formuła M.12 „produkcja OZE równoważy roczne zużycie” jest więc ostrzejsza od dyrektywy wtedy, gdy rozumie się ją jako produkcję na miejscu.

### 2.4. Art. 10 – energia słoneczna
- **ust. 1** – każdy nowy budynek projektuje się tak, by **zoptymalizować potencjał energii słonecznej** („solar-ready”).
- **ust. 3 lit. a** – **do 31.12.2026 r.** odpowiednie instalacje słoneczne na **wszystkich nowych budynkach publicznych i niemieszkalnych > 250 m²** powierzchni użytkowej, „jeżeli jest to odpowiednie pod względem technicznym oraz wykonalne pod względem ekonomicznym i funkcjonalnym”.
- **ust. 4** – krajowe kryteria i zwolnienia z uwzględnieniem m.in. integralności konstrukcji i **dachów zielonych**. W Polsce: projekt WT § 356 ust. 2 i 5 (zwrot ≤ 15 lat) [PR].

### 2.5. Art. 13 – systemy techniczne
- **ust. 3** – samoregulacja temperatury w pomieszczeniach lub strefach, równoważenie hydrauliczne.
- **ust. 4–5** – standardy jakości środowiska wewnętrznego; **niemieszkalne ZEB wyposaża się w urządzenia do monitorowania i regulacji jakości powietrza wewnątrz** (CO₂, temperatura, wilgotność).
- **ust. 9** – systemy automatyki i sterowania budynków (**BACS**) w budynkach niemieszkalnych o mocy znamionowej ogrzewania lub klimatyzacji **> 290 kW do 31.12.2024**, > 70 kW do 31.12.2029. **ust. 10:** ciągłe monitorowanie, benchmarking, interoperacyjność, a do 29.05.2026 także monitorowanie jakości środowiska wewnętrznego.
- **ust. 12** – **automatyczne sterowanie oświetleniem z wykrywaniem obecności**: > 290 kW do 31.12.2027, > 70 kW do 31.12.2029.
- Nasz budynek ma szacunkowo ok. 350 kW ogrzewania i ok. 600 kW chłodzenia (`strategia_energetyczna.md`), więc mieści się w kategorii > 290 kW (wniosek).

### 2.6. Art. 14 – zrównoważona mobilność [UE-NT]
- **ust. 1** – nowe budynki niemieszkalne z > 5 miejscami parkingowymi wewnątrz budynku lub przylegającymi:
  - a) ≥ 1 punkt ładowania na 5 miejsc;
  - b) **okablowanie wstępne ≥ 50%** miejsc i kanały na kable dla pozostałych;
  - c) **miejsca dla rowerów ≥ 15% średniej lub 10% całkowitej liczby użytkowników**, z miejscem na rowery większe niż standardowe (cargo).
  - **Nowe budynki biurowe: ≥ 1 punkt ładowania na 2 miejsca.**
  - Okablowanie dobiera się do jednoczesnego korzystania z punktów, z systemem zarządzania obciążeniem.
- **ust. 2** – wszystkie budynki niemieszkalne z > 20 miejscami do 1.01.2027: ≥ 1 punkt ładowania na 10 miejsc lub kanały kablowe dla ≥ 50% miejsc, rowery jak wyżej. Dla budynków instytucji publicznych (własność lub użytkowanie) okablowanie wstępne ≥ 50% do 1.01.2033. W praktyce to przepis dla zasobu istniejącego; dla nowego biurowca surowszy jest ust. 1 (wniosek).
- **ust. 6** – ładowanie inteligentne, a w stosownych przypadkach dwukierunkowe (V2G).
- **ust. 10** – wytyczne KE w sprawie bezpieczeństwa pożarowego parkingów do 31.12.2025. Nie sprawdzano ich publikacji. **Do weryfikacji** przy projektowaniu EV w garażu podziemnym.
- **Liczby dla nas (wniosek):**
  - minimum MPZP to 103 miejsca (`program.md`) → **≥ 52 punkty ładowania** (poziom EPBD dla biurowców) i okablowanie wstępne dla pozostałych;
  - rowery – 403 pracowników plus średnio ok. 100 gości daje ≥ 75 miejsc (15% średniej). Szczyt ok. 900–1 330 osób daje 90–133 miejsca (10% całkowitej). Program wymaga 50 miejsc w parterze, więc należy **dodać ok. 30–50 miejsc dla gości** na skwerze lub bulwarze (MPZP § 46: na 6KDB/2 dopuszczone parkingi rowerowe).

### 2.7. Art. 15 – wskaźnik gotowości do obsługi inteligentnych sieci (SRI)
- System unijny jest **opcjonalny**. KE przyjmie do **30.06.2027** akt delegowany wprowadzający **obowiązkowe** stosowanie SRI w budynkach niemieszkalnych o mocy systemów HVAC > 290 kW (ust. 2), a do 30.06.2027 akt wykonawczy (ust. 4).
- **Wniosek:** projektować BACS klasy A (PN-EN ISO 52120-1), z interoperacyjnymi protokołami (BACnet/IP, KNX, Modbus), cyfrowym bliźniakiem i dziennikiem budynku (art. 16) – pod przyszłą ocenę SRI.

### 2.8. Załącznik III (GWP) i rozporządzenie delegowane (UE) 2026/52 [UE]
- **Pierwotny zał. III dyrektywy:**
  - GWP w cyklu życia podaje się jako wskaźnik dla każdego etapu, w **kg CO₂e/m² powierzchni użytkowej**, przy **okresie referencyjnym 50 lat**;
  - obliczenia wg **EN 15978**, zakres elementów wg **Level(s) wskaźnik 1.2**;
  - priorytet mają dane EPD wyrobów budowlanych.
- **Rozporządzenie delegowane Komisji (UE) 2026/52 z 16.12.2025** zmienia i zastępuje zał. III: unijne ramy krajowego obliczania GWP. Opublikowane w **Dz.Urz. UE L 2026/52 z 4.5.2026**, weszło w życie **24.05.2026** [Z3]. Kluczowe elementy (fakt z tekstu PL):
  - okres referencyjny **50 lat**;
  - jednostka **kg CO₂e/m² powierzchni użytkowej**, z przejrzystą definicją powierzchni (bez „rozcieńczania” wyniku powierzchniami o małym wpływie);
  - moduły A1–A5, B1–B7 (B6 dzielone na B6.1–B6.3, w tym ładowanie EV na terenie budynku), C1–C4; **moduł D osobno**;
  - minimalny zakres: elementy powłoki i podstawowe (poziom 2 tabeli 4) oraz wyposażenie techniczne, w tym **zbiorniki wody szarej i deszczowej z urządzeniami oczyszczającymi** oraz **pompy ciepła gruntowe**;
  - **obliczenie lub oszacowanie już na etapie projektowania**, a w świadectwie – wynik **powykonawczy**;
  - preferowane dane z rozporządzenia (UE) 2024/3110 o wyrobach budowlanych.
- **Wniosek dla konkursu:** w Etapie II podać szacunek GWP A1–A5 i A–C (kg CO₂e/m²) z deklaracją metody (EN 15978, Level(s) 1.2, rozp. 2026/52). Takie podejście wyróżni pracę na tle wymagań M.12.

### 2.9. Załącznik I – metodologia (fragmenty istotne)
- Gdy budynek jest zasilany z sieci ciepłowniczej, korzyści (udział OZE) uwzględnia się przez **indywidualnie certyfikowane lub uznane współczynniki energii pierwotnej**.
- Współczynniki energii pierwotnej są „perspektywiczne”, rozróżniają energię nieodnawialną, odnawialną i całkowitą i są raportowane wg EN 17423.
- Państwa podają też **operacyjne emisje GHG w kg CO₂e/(m²·rok)**.
- W Polsce nadal obowiązuje metodologia z rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376) ze zmianą Dz.U. 2023 poz. 697 (w życie 28.04.2023). **w_i dla energii elektrycznej z sieci = 2,50** (wcześniej 3,00). Inne wartości w_i: **ciepło sieciowe z kogeneracji (węgiel, gaz) – 0,80**; ciepłownia węglowa 1,30; ciepłownia gazowa 1,20; energia słoneczna 0,00 [Z9].

---

## 3. Rozbieżność: „1 stycznia 2027 r.” (Regulamin, M.12) a prawo UE

| Element | Wniosek Komisji COM(2021) 802 (15.12.2021) [Z2] | Dyrektywa (UE) 2024/1275 (przyjęta) [Z1] | M.12 / Regulamin |
|---|---|---|---|
| Termin ZEB dla sektora publicznego | **od 1.01.2027** | **od 1.01.2028** (art. 7 ust. 1 lit. a) | „od 1 stycznia 2027” |
| Zakres podmiotowy | budynki „**zajmowane lub będące własnością** organów publicznych” | budynki „**będące własnością** instytucji publicznych”. Dla zajmowanych tylko „dążą do tego” (art. 7 ust. 1 akapit 2) | „zajmowanych przez władze publiczne lub będących ich własnością” |
| Termin ZEB dla wszystkich | od 1.01.2030 | od 1.01.2030 | – |
| GWP w cyklu życia | od 1.01.2027 dla > 2000 m² | **od 1.01.2028 dla > 1000 m²**; od 2030 wszystkie | brak |
| Definicja ZEB i progi | **zał. III**: tabela progów (biura, strefa kontynentalna: < 85 kWh/(m²·rok) całkowitej energii pierwotnej); pokrycie zużycia „**w ujęciu rocznym netto**” z OZE na miejscu, ze społeczności OZE lub z efektywnego systemu ciepłowniczego | **art. 11**: próg krajowy ≥ 10% poniżej nZEB; emisje operacyjne poniżej progu krajowego; **całkowite roczne** zużycie energii pierwotnej pokryte z czterech źródeł (ust. 7 lit. a–d, także spoza działki); w razie niewykonalności – energia z sieci; zał. III dotyczy już tylko GWP <!-- poprawione przez weryfikatora --> | „bilansowanie energii – ilość energii wyprodukowanej z OZE równoważy roczne zużycie” |
| Brak spalania paliw kopalnych na miejscu | tak | tak (art. 11 ust. 1) | tak |

**Wyjaśnienie (wniosek):** M.12 (data na okładce 29.10.2025) powiela brzmienie **wniosku Komisji z 2021 r.**, a nie tekst przyjęty w 2024 r.:
- data 2027;
- formuła „zajmowanych lub będących własnością”;
- idea rocznego bilansu netto. <!-- poprawione przez weryfikatora --> Dyrektywa zachowała roczne pokrycie zużycia (art. 11 ust. 7), ale bez sformułowania „netto” i z dopuszczeniem źródeł spoza działki oraz – awaryjnie – sieci.

Prawdopodobnie autor korzystał z opracowań wtórnych sprzed końca procesu legislacyjnego. **Skutki:**
1. **Nie ma kolizji projektowej.** Wymóg Zamawiającego obowiązuje uczestników jako wytyczna konkursowa, niezależnie od stanu prawa. Ocenia się „efektywność i zasadność” rozwiązań.
2. **Prawny obowiązek ZEB dla tej inwestycji** wynika z art. 7 ust. 1 lit. a dyrektywy po transpozycji (projekt WT: od 1.01.2028 dla JSFP). Zależy od daty wniosku o PnB i od tego, czy Polska skorzysta z art. 7 ust. 4. Przy harmonogramie konkurs 2026 → umowa → projekt 2027 → PnB ok. 2027/2028 **prawdopodobieństwo objęcia obowiązkiem jest wysokie** (wniosek). Projektowanie ZEB od początku eliminuje ryzyko przeprojektowania.
3. **Rekomendowane sformułowanie do opisu pracy:** „Budynek zaprojektowano w standardzie budynku bezemisyjnego (zero-emission building) w rozumieniu art. 2 pkt 2 i art. 11 dyrektywy (UE) 2024/1275, wymaganego dla nowych budynków będących własnością instytucji publicznych od 1 stycznia 2028 r. (art. 7 ust. 1 lit. a). Spełnia też wytyczne M.12, w tym roczny bilans OZE dla energii na potrzeby ogrzewania, chłodzenia, wentylacji, c.w.u. i oświetlenia.” Bez wytykania błędu Zamawiającemu. Precyzja prawna buduje wiarygodność wobec ekspertów Etapu II.

---

## 4. Stan transpozycji EPBD w Polsce na 16.11.2026

| Akt / projekt | Status | Co zawiera dla nas | Źródło |
|---|---|---|---|
| Ustawa z 29.08.2014 o charakterystyce energetycznej budynków, **t.j. Dz.U. 2024 poz. 101** | [O]; ostatnia nowelizacja Dz.U. 2023 poz. 1762 (w życie 1.10.2023) wg metryki ELI. **Brak nowelizacji 2025–2026**, więc EPBD 2024 nie została przetransponowana | świadectwa charakterystyki energetycznej, metodologia (art. 15) | [Z8] |
| Rozp. MIiR z 27.02.2015 w sprawie metodologii (Dz.U. 2015 poz. 376), zm. 2017 poz. 22, 2019 poz. 1829, **2023 poz. 697** | [O] | w_el = 2,50; ciepło z kogeneracji 0,80 | [Z9] |
| Rozp. MI z 12.04.2002 (WT 2002), t.j. Dz.U. 2022 poz. 1225, zm. Dz.U. 2023 poz. 2442 oraz 2024 poz. 474 i 726 <!-- poprawione przez weryfikatora --> | **[P]** – utraciły moc na podstawie art. 66 ustawy o dostępności (84 miesiące od 20.09.2019; art. 102a Pb: „obowiązujące do dnia 19 września 2026 r.”; ISAP: uznane za uchylone 21.09.2026). **Fakultatywnie** stosowane na podstawie art. 102a Pb (Dz.U. 2026 poz. 1161): wymaga oświadczenia inwestora i wniosku o PnB złożonego w okresie 18 miesięcy od 20.09.2026. Nowelizacje 2023–2024 nie zmieniły § 3 pkt 22, § 126, § 216 ust. 8, § 328–329 ani zał. 2 | EPmax, Uc,max, g (zob. `wt_kluczowe.md` 12.1) | [Z10][Z12][Z41] |
| **Projekt rozporządzenia w sprawie WT** (wersja 13.05.2026; wg `wt_kluczowe.md` wersja 6.08.2026 notyfikowana KE pod nr 2026/0422/PL – numeru notyfikacji weryfikator nie potwierdził w TRIS) | [PR]; **planowane wejście w życie 20.09.2026 (§ 394 projektu) nie nastąpiło** – brak aktu w Dz.U. do 16.11.2026 (ELI) <!-- poprawione przez weryfikatora --> | § 354 ust. 1 pkt 3 (ZEB od 1.01.2028 dla JSFP), § 355 (EP 2030/2028), § 356 (instalacja słoneczna > 250 m², zwrot ≤ 15 lat; ust. 2 i 4 miały wejść w życie 31.12.2026), § 22 ust. 4–5 (priorytet zagospodarowania wód opadowych na działce), § 310–314 (BESS), § 15 (EV – odesłanie do art. 12a ustawy o elektromobilności). Numeracja może się różnić w kolejnych wersjach | [Z11] |
| **Projekt ustawy o zmianie ustawy o charakterystyce energetycznej budynków oraz niektórych innych ustaw (UC82)** | [PR]; etap niepotwierdzony (RCL legislacja.gov.pl i gov.pl niedostępne 16.11.2026; *źródło wtórne* z 5.11.2026 opisuje projekt UC82, projekt RCL 12347353) | m.in. świadectwa dla nowych budynków, klasy energetyczne (wg *źródła wtórnego*) | [Z15] |
| **Projekt ustawy o zmianie ustawy – Prawo energetyczne (UC121)**, OSR z 15.05.2026 (Ministerstwo Energii) | [PR]; wdraża EED 2023/1791 i RED III (ciepłownictwo) | „nowe kryteria dla efektywnego systemu ciepłowniczego lub chłodniczego” wg okresów art. 26 ust. 1 EED i kryteria emisyjne z art. 26 ust. 2; lokalne plany ogrzewania i chłodzenia dla gmin > 45 000 mieszkańców | [Z14] |
| Komisja Europejska – wezwania do usunięcia uchybienia (15.07.2026) | fakt | wezwania do **wszystkich 27 państw** za brak pełnej notyfikacji transpozycji dyrektywy 2024/1275; 2 miesiące na odpowiedź | [Z7] |
| Ustawa – Prawo energetyczne, **t.j. Dz.U. 2026 poz. 43**, zm. 2026 poz. 516, 607, 900, 1348 oraz 1347 (w części dot. Pe w życie 1.12.2026; nie zmienia art. 7b) <!-- poprawione przez weryfikatora --> | [O] | art. 7b (obowiązek przyłączenia do sieci ciepłowniczej, wyłączenie dla źródła z w ≤ 0,8 i ≥ 60% OZE, definicja efektywnego systemu: 50% OZE / 50% ciepła odpadowego / **75% kogeneracji** / 50% kombinacji); nowy ust. 4a (kotły elektryczne zasilane OZE – Dz.U. 2026 poz. 900, art. 1 pkt 6) | [Z13] |
| Ustawa o elektromobilności i paliwach alternatywnych, **t.j. Dz.U. 2026 poz. 1243** | [O] | art. 12 ust. 1 (moc przyłączeniowa dla wszystkich stanowisk – punkty ≥ 3,7 kW; gminy z art. 60 ust. 1, w tym Wrocław); art. 12a ust. 1 (> 10 stanowisk: ≥ 1 punkt ładowania i kanały na 1 punkt / 5 stanowisk) | [Z16] |

**Wniosek:** na 16.11.2026 polski inwestor nie ma jeszcze ustawowego obowiązku ZEB, GWP ani 1 punktu ładowania na 2 miejsca. Te obowiązki pojawią się wraz z transpozycją, której spodziewamy się przed PnB tej inwestycji. Projekt konkursowy powinien je spełniać z wyprzedzeniem („future-proof”). To argument ekonomiczny: unika się przeprojektowania i ryzyka nieważności założeń.

---

## 5. Wymagania energetyczne WT (obowiązujące i projektowane) – liczby dla budynku UMWD

### 5.1. WT 2002 w brzmieniu z 19.09.2026 [P] (szczegóły i paragrafy w `wt_kluczowe.md` 12.1)
- **§ 329 – EPmax** dla budynku użyteczności publicznej „pozostałego”. Budynek **zajmowany przez organ administracji publicznej i będący jego własnością** musi spełniać wymagania 2021 już od 1.01.2019 (§ 328 ust. 1b, przypisy do tabel § 329). Składniki: **EPH+W = 45**, **ΔEPC = 25·Af,C/Af**, **ΔEPL = 25** (t₀ < 2500 h/rok) lub **50** (t₀ ≥ 2500 h). Przy 100% powierzchni chłodzonej i t₀ < 2500 h: **EPmax = 95 kWh/(m²·rok)**. Przy t₀ ≥ 2500 h (prawdopodobna wartość domyślna dla biur – NIEPEWNE, zob. rozdz. 0 pkt 5): **120**. Dla budynku o różnych funkcjach EPmax liczy się jako średnią ważoną powierzchnią Af (§ 329 ust. 3). <!-- poprawione przez weryfikatora -->
- **Zał. 2 – izolacyjność:**
  - Uc,max: ściany 0,20; dach i stropodach 0,15; podłoga na gruncie 0,30; strop nad garażem 0,25;
  - okna i fasady przezroczyste 0,9; drzwi zewnętrzne 1,3 W/(m²K);
  - **g ≤ 0,35** latem (nie dotyczy kierunków NW–NE);
  - okna w klasie przepuszczalności powietrza 3; fRsi ≥ 0,72.
- **WT 2002 nie określa wprost minimalnego udziału OZE.** Wymóg nZEB (EPmax) wymusza OZE pośrednio, przez niskie w_i. Obowiązek instalacji słonecznej pojawi się dopiero z transpozycją art. 10 (projekt WT § 356).
- **§ 126 ust. 3** – wody opadowe ze zbiorników wykorzystywane do spłukiwania toalet, podlewania i mycia nawierzchni wymagają **odrębnej instalacji, niepołączonej z instalacją wodociągową** [Z10].
- **§ 3 pkt 22** – do terenu biologicznie czynnego wlicza się **50% powierzchni tarasów i stropodachów** z nawierzchnią zapewniającą wegetację (min. 10 m²) [Z10].

### 5.2. Projekt nowych WT (13.05.2026) [PR] [Z11]
- **§ 354 ust. 1 pkt 3** – dla budynku **będącego własnością jednostki sektora finansów publicznych od 1.01.2028 r.**:
  - a) źródła ciepła, chłodu i energii elektrycznej **nie emitują na miejscu CO₂ z paliw kopalnych**, a emisje GHG są zerowe lub niższe od progu. Dla budynku użyteczności publicznej „pozostałego”: **ECO2,ZEB = 0,000274·EPZEB + 0,0081 t CO₂/(m²·rok)**;
  - b) zapotrzebowanie na energię nieodnawialną pokrywane z: OZE, obywatelskich społeczności energetycznych, spółdzielni energetycznych, klastrów energii, prosumentów (w tym wirtualnych i zbiorowych), źródeł bezemisyjnych albo efektywnego systemu ciepłowniczego (art. 7b ust. 4 Prawa energetycznego). Warunek: istnieją techniczne i ekonomiczne warunki.

  **ust. 2** – w razie braku tych warunków dopuszcza się inną energię z sieci. **ust. 5** – budynek spełniający ust. 1 i 2 jest bezemisyjny. **ust. 7** – nie dotyczy budynku **wpisanego** do rejestru zabytków. Nasz nowy budynek nim nie jest; położenie w obszarze wpisanym nie zwalnia (wniosek).
- **§ 355** – od 1.01.2030, a dla JSFP od 1.01.2028: **EPH+W 40; ΔEPC 22·Af,C/Af; ΔEPL 23 (t₀ < 2500) / 45**. Przy pełnym chłodzeniu i t₀ < 2500 h: **EPZEB = 85 kWh/(m²·rok)**, a więc **ECO2,ZEB ≈ 0,000274·85 + 0,0081 = 0,0314 t = 31,4 kg CO₂/(m²·rok)** (wniosek – arytmetyka). Przy t₀ ≥ 2500 h: EPZEB = 107 i ECO2,ZEB ≈ 37,4 kg CO₂/(m²·rok) (wniosek). Projekt objaśnia 0,000274 t CO₂/kWh jako „średnią emisję CO₂ nośników energii odniesioną do energii pierwotnej (nieodnawialnej)”. <!-- poprawione przez weryfikatora -->
- **§ 394 projektu** – planowane wejście w życie 20.09.2026, a § 356 ust. 2 i 4 – 31.12.2026. **Nie nastąpiło** (stan 16.11.2026). Data stosowania ZEB dla JSFP (1.01.2028) pozostaje więc tylko propozycją. <!-- poprawione przez weryfikatora -->
- **§ 356 ust. 2 i 5** – budynek inny niż mieszkalny > 250 m² wyposaża się w instalacje wykorzystujące promieniowanie słoneczne, gdy jest to odpowiednie technicznie, funkcjonalnie i ekonomicznie (zwrot ≤ 15 lat). **ust. 6:** „należy rozważyć wykorzystanie magazynu energii”.
- **§ 310–314 (BESS)**:
  - maks. **600 kWh w jednej strefie pożarowej**;
  - 60–300 kWh – na 1. kondygnacji podziemnej lub 1. nadziemnej, z dostępem dla ratowników z zewnątrz lub przez drogę komunikacji ogólnej, garaż albo jedno pomieszczenie techniczne;
  - **> 300 kWh – tylko na 1. kondygnacji nadziemnej z bezpośrednim dostępem z zewnątrz**;
  - zakaz instalacji **powyżej 25 m** (z wyjątkami zewnętrznymi);
  - wyłącznik awaryjny BESS;
  - wentylacja i detekcja.

  → wniosek: BESS ≤ 300 kWh na −1 albo w parterze przy strefie dostaw od Wybrzeża Słowackiego. Uwaga na zagrożenie powodziowe (M.05).
- **§ 22 ust. 4–5** – wody opadowe w pierwszej kolejności na terenie własnym (zieleń, rozsączanie, zbiorniki), z bezpiecznym zagospodarowaniem opadu ponadnormatywnego. Przyłączenie do sieci – gdy nie ma takiej możliwości.

### 5.3. Unijna taksonomia (rozp. delegowane (UE) 2021/2139, zał. I, sekcja 7.1 „Budowa nowych budynków”) [UE] [Z5]
Ma znaczenie przy ewentualnym finansowaniu „zielonym” (obligacje, kredyty EBI/BGK) – wniosek.
1. **PED co najmniej o 10% mniejsze niż próg nZEB**, potwierdzone powykonawczym świadectwem.
2. Budynki **> 5000 m²**: **badanie szczelności i integralności cieplnej** po ukończeniu.
3. Budynki > 5000 m²: **GWP w cyklu życia** obliczany dla etapów i udostępniany na żądanie.
4. DNSH – woda:
   - umywalki i zlewy ≤ **6 l/min**;
   - prysznice ≤ **8 l/min**;
   - WC: maks. 6 l, średnio ≤ **3,5 l**;
   - pisuary ≤ 2 l/muszlę/h (spłukiwane ≤ 1 l).

   Gospodarka obiegu zamkniętego: ≥ 70% odpadów budowlanych do odzysku; projekt pod demontaż (ISO 20887). Emisje formaldehydu i LZO z materiałów.

### 5.4. Ekoprojekt central wentylacyjnych (rozp. Komisji (UE) nr 1253/2014) [UE] [Z6]
Od 1.01.2018 dla dwukierunkowych central niemieszkalnych (SWNM): **sprawność temperaturowa odzysku ciepła ≥ 73%**; dla układów z medium pośredniczącym (glikolowe) ≥ 68%. Projektowo zakładamy ≥ 80% (wniosek).

---

## 6. Ciepło sieciowe we Wrocławiu – czy może być „zero-emisyjne”?

**Operator i źródła (fakt).** Sieć miejską we Wrocławiu prowadzi Fortum Power and Heat Sp. z o.o. Większość ciepła wytwarza KOGENERACJA S.A. Według formuły taryfowej Fortum ok. 96,7% ceny ciepła odpowiada cenie z KOGENERACJA S.A., a reszta to pompy ciepła Fortum [Z21]. Pompa ciepła ze ścieków „WROMPA” (12,5 MW) ma pokrywać do ok. 5% rocznego zapotrzebowania (*źródło wtórne*) [Z39].

**Sprawozdanie z art. 7b ust. 5 Prawa energetycznego za 2025 r. (sieć „miasto Wrocław”)** [Z20]:

| Parametr | Wartość 2025 |
|---|---|
| udział OZE (biomasa) | **1,22%** |
| udział ciepła odpadowego | **0,35%** |
| udział ciepła z kogeneracji | **85,11%** |
| współczynnik nakładu nieodnawialnej energii pierwotnej | **0,620** |
| końcowe zużycie energii cieplnej brutto | 8 919 026 GJ |

**Ocena według kryteriów (wniosek):**

| Kryterium | Okres | Spełnione? |
|---|---|---|
| art. 7b ust. 4 Prawa energetycznego (≥ 75% kogeneracji) = art. 26 ust. 1 lit. a EED | do 31.12.2027 | **tak** – system jest dziś „efektywny” |
| art. 26 ust. 1 lit. b EED: ≥ 80% **wysokosprawnej** kogeneracji albo kombinacja z OZE ≥ 5% i ≥ 50% łącznie | od 1.01.2028 | **niepewne**. 85% kogeneracji, ale nie wiadomo, jaka część jest „wysokosprawna”; OZE 1,22% < 5% |
| art. 26 ust. 1 lit. c EED: ≥ 50% OZE lub ciepła odpadowego, albo ≥ 80% łącznie (z kogeneracją) i ≥ 35% OZE lub ciepła odpadowego | od 1.01.2035 | **nie** przy obecnym miksie (1,57% OZE i ciepła odpadowego) |
| art. 26 ust. 2 EED (alternatywa emisyjna): ≤ 150 g/kWh od 2026, ≤ 100 g/kWh od 2035 | zależnie od wyboru państwa | brak danych o emisyjności (nie publikowane w sprawozdaniu) |

**Wnioski:**
- Pokrycie zapotrzebowania z sieci Fortum mieści się dziś formalnie w art. 11 ust. 7 lit. c dyrektywy (ZEB) i w projekcie WT § 354 ust. 1 pkt 3 lit. b. Status ten jest **zależny od przyszłych zmian miksu** (UC121 wprowadzi kryteria EED 2028/2035). Przy przewadze węgla w kogeneracji obciąża też bilans operacyjnych emisji GHG.
- **Strategia M.12 jest właściwa:** gruntowe pompy ciepła jako źródło podstawowe, sieć jako rezerwa i szczyt.
- **Koszty taryfowe (fakt, od 1.07.2026, część wytwórcza)** [Z21]: cena za moc zamówioną **163 124,57 zł/MW/rok**, cena ciepła **86,39 zł/GJ** (netto; bez opłat przesyłowych). Moc rezerwowa ok. 0,3–0,4 MW kosztowałaby ok. 49–65 tys. zł/rok samej opłaty stałej za wytwarzanie (wniosek). Należy ją zoptymalizować w umowie (np. moc szczytowa tylko w sezonie, rezerwa z redundancji PC N+1).
- **Art. 7b ust. 1 Prawa energetycznego** – obowiązek przyłączenia do sieci, „o ile istnieją techniczne i ekonomiczne warunki”. **Wyłączenie z ust. 3** obejmuje źródło indywidualne z w ≤ 0,8 i ≥ 60% ciepła z OZE, potwierdzone audytem (ust. 3c–3d). Dla PC: w = 2,5/SCOP i udział OZE = 1 − 1/SCOP (wniosek), więc SCOP ≥ 3,125 daje w ≤ 0,8, a SCOP ≥ 2,5 daje ≥ 60% OZE. Przy SCOP ok. 4,5: **w ≈ 0,56, OZE ≈ 78%**. M.12 i tak przewiduje przyłączenie rezerwowe, więc kolizji nie ma. Pb art. 33 ust. 2 pkt 10 wymaga oświadczenia o możliwości przyłączenia do sieci (zob. `wt_kluczowe.md` rozdz. 13).

---

## 7. Pompy ciepła gruntowe i wodne – uwarunkowania prawne i lokalne

### 7.1. Warunki gruntowo-wodne (M.05, opinia geotechniczna, IX 2025 – fakt)
- **Rozpoznanie do 30 m p.p.t.:**
  - nasypy niebudowlane do 2,8–3,8 m;
  - holoceńskie piaski drobne i średnie do 6,5–8,6 m;
  - plejstoceńskie **piaski, pospółki i żwiry** tarasów nadzalewowych;
  - **gliny zwałowe**.

  Do 30 m nie przewiercono osadów czwartorzędowych.
- **Zwierciadło wody swobodne na 3,2–3,8 m p.p.t.** (rzędne ok. 115,1–116,0 m n.p.m.), wahania ±0,5 m. Lokalnie (O-01) woda **naporowa na 16,5 m**.
- Obszar w strefie **narażonej na podtopienia** (PIG) i na **obszarze narażonym na niebezpieczeństwo powodzi** (Hydroportal).
- **Wniosek dla energetyki:**
  - nawodnione piaski i żwiry o wysokiej przewodności cieplnej i możliwym przepływie wód (bliskość ujścia Oławy do Odry) **sprzyjają pionowym wymiennikom gruntowym (BHE)**, a także układom otwartym (studnie);
  - poniżej 30 m budowa jest nierozpoznana (prawdopodobnie gliny i iły o niższej przewodności), więc **potrzebny test reakcji termicznej (TRT)**;
  - wody naporowe na 16,5 m wymagają szczelnego zacementowania otworów (iniekcja przewodząca), żeby nie łączyć poziomów wodonośnych;
  - urządzeń krytycznych (BESS, rozdzielnie SN/nn) nie lokalizować na −2.
- Średnia roczna temperatura powietrza we Wrocławiu (1991–2020) wynosi **9,7°C** (*źródło wtórne* – wroclaw.pl) [Z36]. Temperatura gruntu na głębokości 10–100 m to orientacyjnie ok. 10–12°C (wniosek; potwierdzić TRT).
- Orientacyjne jednostkowe moce poboru wg **VDI 4640 Bl. 2** (małe instalacje, 1800 h/rok): nawodnione piaski i żwiry **65–80 W/m**; wilgotne gliny i iły 35–50 W/m; suche piaski < 25 W/m. Przy 2400 h/rok odpowiednio 55–65, 30–40 i < 20 W/m (*źródło wtórne* – zestawienie w przewodniku Schleswig-Holstein) [Z32]. **Dla dużych instalacji tabele VDI nie zastępują symulacji** (EED/EWS, 25 lat) ani TRT. W koncepcji przyjęto ostrożnie **45 W/m poboru i 55 W/m oddawania** (wniosek).

### 7.2. Prawo geologiczne i górnicze, **t.j. Dz.U. 2026 poz. 69** [O] [Z17]
- **art. 3 pkt 2** – ustawy nie stosuje się do otworów **do 30 m** w celu wykorzystania ciepła Ziemi (poza obszarami górniczymi).
- **art. 85 ust. 1–3** – projekt robót geologicznych obejmujących wiercenia dla ciepła Ziemi **nie wymaga zatwierdzenia, lecz zgłoszenia staroście**. Roboty można zacząć, jeśli w 30 dni starosta nie wniesie sprzeciwu (decyzja; przesłanki: zagrożenie środowiska, niezgodność z prawem, nieadekwatność do celu). We Wrocławiu (miasto na prawach powiatu) właściwy jest **Prezydent Miasta** (art. 161 ust. 2 pkt 5).
- **art. 86** – do robót geologicznych **na głębokości większej niż 100 m** stosuje się odpowiednio przepisy o **zakładzie górniczym i jego ruchu**. → **Rekomendacja: BHE ≤ 100 m (99 m)**, bo przekroczenie 100 m znacząco komplikuje i podraża realizację (wniosek).
- Po robotach – dokumentacja geologiczna (art. 88).

### 7.3. Prawo wodne, **t.j. Dz.U. 2026 poz. 1335** [O] [Z18]
- **Układ otwarty** (studnie: pobór i zatłaczanie wód podziemnych) to **usługa wodna** (pobór wód podziemnych – art. 35 ust. 3 pkt 1), więc wymaga **pozwolenia wodnoprawnego** (art. 389 pkt 1–2) – ponad zwykłe korzystanie do 5 m³/d. <!-- poprawione przez weryfikatora --> **art. 76 ust. 1 pkt 5**: dopuszcza się wprowadzanie **wód wykorzystanych pochodzących z pomp ciepła** do wód podziemnych. Dokumentacja hydrogeologiczna z próbnym pompowaniem; ujęcia ≤ 50 m³/h należą do właściwości starosty (PGiG art. 161 ust. 2 pkt 2).
- **Woda rzeczna (Odra, Oława – ok. 30–80 m od działki):** pobór wód powierzchniowych i zrzut wód o zmienionej temperaturze wymagają pozwolenia wodnoprawnego. Potrzebne byłyby budowle w strefie nabrzeża i obwałowań (uzgodnienia z Wodami Polskimi; ochrona przeciwpowodziowa; strefa konserwatorska nabrzeża Ohlau-Ufer).
- **Ocena (wniosek):**
  - temperatura wody rzecznej zimą spada w okolice 0°C – we Wrocławiu notowano zjawiska lodowe na skanalizowanym odcinku Odry (*źródło wtórne*: komunikaty RZGW Wody Polskie z II 2021, niepobrane) [Z37];
  - latem woda jest ciepła (dla porównania Ren w Mannheim: ok. 5°C zimą i do 25°C latem; rzeczna PC MVV 20 MW_th / 7 MW_el, czyli efektywność ok. 2,9 przy temperaturach sieciowych 83–99°C – *źródło wtórne*) [Z33];
  - rzeka daje **gorsze parametry niż grunt** (ok. 10–12°C stabilnie) zarówno dla grzania w szczycie, jak i dla free-coolingu;
  - wysoki koszt ujęcia i barier formalnych, ryzyko jakości wody (zasolenie, zakwity) i zarastania wymienników.

  → **Odra i Oława nie jako źródło podstawowe.** Można je wskazać w opisie jako perspektywę miejskiej sieci niskotemperaturowej („anergii”) z udziałem Miasta, MPWiK i Fortum.
- **art. 34 pkt 4** – szczególne korzystanie z wód przy wyłączeniu > 70% nieruchomości > 3500 m² z powierzchni biologicznie czynnej **na obszarach nieujętych w systemy kanalizacji otwartej lub zamkniętej**. Działka w śródmieściu jest skanalizowana, więc przepis najpewniej nie ma zastosowania (wniosek). Opłaty za wody opadowe pobiera MPWiK (rozdz. 8).
- Zmiana Prawa wodnego **Dz.U. 2026 poz. 1156** (w życie 1.01.2027) dotyczy wody odzyskanej ze ścieków w chłodzeniu elektrowni i elektrociepłowni – nie dotyczy budynku (fakt).
- <!-- poprawione przez weryfikatora --> **art. 390 ust. 1 pkt 1 lit. b** – pozwolenie wodnoprawne wymagane jest też na lokalizowanie **nowych obiektów budowlanych na obszarach szczególnego zagrożenia powodzią** (Q1% i Q10%, art. 169 ust. 2 pkt 2). Według ISOK teren leży poza scenariuszami Q10/Q1/Q0,2%, ale opinia M.05 mówi o „obszarze narażonym na niebezpieczeństwo powodzi” (`../30_lokalizacja/geotechnika.md` K-02). **Wniosek:** przepis prawdopodobnie nie ma zastosowania. Trzeba to potwierdzić na aktualnych mapach zagrożenia powodziowego przed PnB.
- Odwodnienie wykopu dla 2 kondygnacji podziemnych w wodzie gruntowej to osobny temat formalny: usługa wodna z art. 35 ust. 3 pkt 8 Pw oraz projekt robót geologicznych (PGiG art. 161 ust. 2 pkt 4 – właściwość starosty do 50 m³/h). Poza zakresem tego opracowania (wniosek).

### 7.4. MPZP a układ otwarty (wniosek)
MPZP § 14 pkt 2: „zaopatrzenie w wodę dopuszcza się wyłącznie z sieci wodociągowej” [Z26]. Studnie pomp ciepła nie służą zaopatrzeniu w wodę, ale dla bezpieczeństwa interpretacyjnego **układ zamknięty (BHE)** jest wariantem bezspornym. Układ otwarty to opcja do analizy w fazie projektu.

### 7.5. Konstrukcje termoaktywne (wniosek; literatura)
Dwie kondygnacje podziemne w wodzie gruntowej oznaczają prawdopodobnie **ściany szczelinowe** i być może **pale lub mikropale kotwiące przeciw wyporowi**. Można je wykorzystać jako **ściany i pale energetyczne** (rury w zbrojeniu), co uzupełnia pole BHE. Metoda jest opisana w literaturze geotechnicznej (Brandl 2006, *Géotechnique* 56(2)) [Z31]. Wymaga koordynacji z konstrukcją i nie zastępuje odwiertów.

---

## 8. Retencja, woda deszczowa i szara – prawo i uwarunkowania Wrocławia

- **Wrocław – Zarządzenie Prezydenta Wrocławia nr 5364/26** (wytyczne GWO, obowiązujące od 25.06.2026):
  - zasada „zagospodarować opad w miejscu, do sieci tylko nadmiar”;
  - priorytet zielono-niebieskiej infrastruktury;
  - wiąże jednostki miejskie, a dla inwestorów prywatnych jest rekomendacją (wroclaw.pl, 7.08.2026) [Z23].
- **MPWiK Wrocław – „Wytyczne w zakresie gospodarowania wodami opadowymi” RW25 v.4.1 (1.07.2026)** [Z22]:
  - MPWiK opiniuje i uzgadnia koncepcje oraz projekty i wydaje warunki przyłączenia; może zmienić ilość wód odprowadzanych do odbiornika (III.1.4). **„Trudne warunki gruntowo-wodne nie zwalniają z obowiązku stosowania rozwiązań z zakresu ZNI”** (II) – ważne przy wodzie gruntowej na 3,2–3,8 m;
  - model opadowy Wrocławia (Kotowski i in. 2010): dla **zabudowy śródmiejskiej deszcz miarodajny C = 10 lat**, wylewy z kanałów C = 50 lat. Natężenie 15-min **q = 204,7 dm³/(s·ha)**; wysokości opadu: 15 min **18,42 mm**, 60 min **30,44 mm**, 24 h 68,82 mm (Tabela 1–2);
  - współczynniki spływu (Tabela 3): dachy ≤ 5° – 0,95; **zielone dachy ≤ 5° o warstwie sypkiej > 10 cm – 0,30**, do 10 cm – 0,60; kostka – 0,80; kostka na podbudowie przepuszczalnej – 0,60; ażurowe na piasku – 0,40; zadarniona gleba – 0,10;
  - wymagany bilans wód opadowych i wymiarowanie obiektów ZNI i zbiorników (rozdz. IV).
- **Opłata za odprowadzanie wód opadowych** w MPWiK dotyczy nieruchomości przyłączonych do systemu. Retencja i ponowne wykorzystanie wody (zbiorniki, zielone dachy) pozwalają opłaty uniknąć lub ją ograniczyć (*źródło wtórne* – wroclaw.pl; stawek nie zweryfikowano).
- **Woda szara:**
  - prawo polskie nie ma odrębnej regulacji ustawowej dla budynków (fakt w zakresie sprawdzonych aktów: WT 2002, projekt WT);
  - stosuje się WT § 126 ust. 3 analogicznie – odrębna instalacja niepołączona z wodociągową (wymóg M.12 pkt 2C);
  - normy branżowe dla systemów wody deszczowej i szarej (seria PN-EN 16941) oraz zabezpieczenie przed przepływem zwrotnym (PN-EN 1717) – **do weryfikacji aktualnych wydań PKN** (nie sprawdzano).
- **MPZP § 14 pkt 3**: „odprowadzenie ścieków komunalnych dopuszcza się wyłącznie siecią kanalizacyjną” – nie koliduje z ponownym użyciem wody szarej, bo nadmiar i ścieki po spłukaniu trafiają do sieci (wniosek). MPZP nie reguluje wód opadowych (`mpzp.md` poz. 36, K-09).

---

## 9. Dachy zielone – uwarunkowania
- PU s. 17 dopuszcza **dach zielony ekstensywny** na części dachu. F.15.C wymaga podania powierzchni dachów zielonych (I.13) i PBC na dachach (3.3).
- WT § 3 pkt 22 – zielone stropodachy liczą się do PBC w **50%** (min. 10 m²). MPZP nie wyznacza minimum PBC dla zabudowy usługowej (`mpzp.md` poz. 17).
- RW25 – zielony dach > 10 cm warstw sypkich ma **ψ = 0,30** (zamiast 0,95), więc dwu–trzykrotnie zmniejsza odpływ szczytowy z dachu [Z22].
- EPBD art. 10 ust. 4 – kryteria solarne mają uwzględniać dachy zielone. **Wniosek:** dach biosolarny (PV nad roślinnością) łączy oba wymagania. Chłodzenie roślinnością zwiększa uzysk PV latem (efekt jakościowy). Zgodność z MPZP § 6 pkt 13 – patrz rozdz. 11 R-01.

---

## 10. Certyfikacje wielokryterialne – co jest racjonalne

| System | Charakter | Dla budynku UMWD (wniosek) |
|---|---|---|
| **Level(s)** (UE) | darmowe ramy raportowania (wskaźniki 1.1 energia, **1.2 GWP**, 3.1 woda, 4.x komfort, 6.1 LCC) | **rekomendowany jako minimum** – spójny z zał. III EPBD i rozp. 2026/52 [Z1][Z3]; bez kosztów licencji |
| **BREEAM International New Construction** | najpopularniejszy w Polsce dla biur; kategorie Ene, Wat, Mat (LCA), Hea, LE | **rekomendowany** – cel **„Excellent”** (ambitnie, realistycznie przy GSHP, PV, wodzie szarej, LCA). „Outstanding” wymaga dodatkowych kosztów i weryfikacji; nie deklarować w konkursie |
| **LEED v5 BD+C** (USGBC, 2025) | od v5 wymóg **ilościowego GWP** konstrukcji, przegród i nawierzchni (prerekwizyt MRp2) | alternatywa; mniej typowa dla polskiej administracji (*źródło wtórne*) [Z34] |
| **DGNB / BNB** | system niemiecki, silne LCA i LCC; BNB dla budynków federalnych | merytorycznie dobry wzór (LCA, LCC), w Polsce rzadki – opcja |
| **WELL v2** | zdrowie i komfort użytkowników | opcjonalny; wysoki koszt operacyjny – nie rekomendować w konkursie |
| **PLGBC „Zielony Dom”** | system dla **budynków mieszkaniowych** (jedno- i wielorodzinnych) | **nie dotyczy** budynku biurowego (*źródło wtórne*) [Z35] |
| Taksonomia UE (7.1) | kryteria finansowania | warto wykazać zgodność (PED −10% nZEB, test szczelności, GWP, DNSH woda) – rozdz. 5.3 |

**Wniosek:** w pracy deklarować **„standard ZEB (EPBD) + raport Level(s) + przygotowanie do BREEAM Excellent”**, bez obietnicy konkretnego certyfikatu (koszt i zakres to decyzja Zamawiającego). Uniknie to zarzutu nierealności przy kryterium drugorzędowym.

---

## 11. Rejestr rozbieżności i ryzyk (zero-emisja)

| # | Rozbieżność / ryzyko | Źródła | Rekomendacja (wniosek) |
|---|---|---|---|
| R-01 | **MPZP § 6 pkt 13** (zakaz urządzeń technicznych i budowlanych na dachach i elewacjach od ulic, placów, bulwarów) a **M.12 B** (PV na dachu dominanty i elewacjach) i PU s. 13 | M.03; M.12; PU; `mpzp.md` K-05 | PV jako **pokrycie dachu / BIPV** – element przegrody, nie urządzenie nadstawione; PV niewidoczne zza attyki; BIPV elewacyjne na elewacjach **od dziedzińca**; urządzenia (falowniki, dry-coolery) w piętrze technicznym z czerpniami i wyrzutniami od dziedzińca. W opisie wskazać interpretację i potrzebę jej potwierdzenia z Miastem i konserwatorem |
| R-02 | **WT § 216 ust. 8** – okładzina elewacji **> 25 m** niepalna (A1/A2); typowe moduły szkło-szkło z folią EVA/PVB nie są A1/A2 | `ppoz.md` 7.7; projekt WT § 227 ust. 9–10 [PR] | BIPV na dominancie > 25 m **tylko jako wariant warunkowy**: przeszklenia lub moduły z potwierdzoną klasyfikacją i elewacją NRO. Wariant podstawowy PV opiera się na dachach |
| R-03 | **M.12: PV 0,4–1,0 MWp** a realny potencjał na działce (ok. 0,40 MWp; warunkowo 0,50 MWp) | `strategia_energetyczna.md` rozdz. 5.1 | Deklarować **0,40 MWp na działce** (dolna granica M.12, ok. 74% dachów jako PV-aktywne). Pozostałą część „bilansu OZE” pokryć z OZE w pobliżu lub ze społeczności energetycznej (art. 11 ust. 7 lit. b EPBD; projekt WT: spółdzielnia, klaster, prosument wirtualny) – np. farma PV na gruntach Województwa w klastrze. Uzasadnić liczbowo (elewacje N: ok. 192 kWh/kWp – nieekonomiczne) |
| R-04 | **„Bilansowanie roczne” M.12** dla całego zużycia jest nieosiągalne na działce (wieża 45 m, mała działka, zużycie nieregulowane: IT, serwerownia) | M.12 pkt 1 lit. d | Bilans 100% OZE na działce dla zużycia **EPB** (ogrzewanie, chłodzenie, wentylacja, c.w.u., oświetlenie). Dla zużycia całkowitego – OZE z sieci pochodzące ze społeczności lub klastra, ewentualnie gwarancje pochodzenia (raportowanie rynkowe). Pokazać to uczciwie na schemacie |
| R-05 | Termin **„1.01.2027”** i zakres „zajmowanych” | Regulamin; M.12; COM(2021) 802; EPBD art. 7 | rozdz. 3 – poprawna podstawa w opisie |
| R-06 | **Status sieci ciepłowniczej jako „efektywnej” po 2027/2035** | Fortum 2025; EED art. 26; UC121 [PR] | sieć tylko rezerwowo i szczytowo (zgodnie z M.12); minimalna moc zamówiona |
| R-07 | **Brak transpozycji EPBD** (ZEB, GWP, EV 1/2, BACS, SRI) – zmienność wymagań przed PnB | rozdz. 4 | projektować z wyprzedzeniem: ZEB, GWP (rozp. 2026/52), 1 punkt ładowania / 2 miejsca, BACS klasy A, monitoring IEQ |
| R-08 | **Agregat prądotwórczy** (PU) to spalanie paliwa na miejscu | PU s. 13, 16; EPBD art. 11 ust. 1 | paliwo **HVO100** (odnawialne), praca tylko awaryjna i testowa; krótkie zaniki pokrywa BESS + UPS. W opisie: „brak spalania paliw kopalnych w eksploatacji”. Interpretacji KE nie weryfikowano |
| R-09 | **BESS** – lokalizacja i limity (projekt WT § 312), strefa zagrożenia powodzią i podtopieniami (M.05) | [PR]; M.05 | BESS ≤ 300 kWh w parterze lub na −1 z dostępem dla ratowników, wyłącznik awaryjny, osobna strefa EI; nie na −2 |
| R-10 | **Odwierty pod budynkiem z 2 kondygnacjami w wodzie gruntowej** – technologia (wiercenie z dna wykopu przed płytą, przejścia przez płytę, woda naporowa na 16,5 m) | M.05; M.12 A | wiercić z dna wykopu przed betonowaniem płyty; kolektory w podbudowie; uszczelnienia; koordynacja z palami i ścianami; TRT na etapie PB |
| R-11 | **Głębokość BHE > 100 m** to reżim zakładu górniczego (PGiG art. 86) | [Z17] | BHE ≤ 100 m |
| R-12 | **Nadwyżka ciepła oddawanego do gruntu** (dominacja chłodzenia w biurowcu) – przegrzewanie pola BHE w 25 latach | `_bilans_energii.py` | odzysk ciepła z chłodzenia do c.w.u. i ogrzewania (jednoczesne grzanie i chłodzenie), dry-cooler hybrydowy w piętrze technicznym na szczyty i okresy przejściowe, ograniczenie zysków (osłony zewnętrzne); symulacja 25-letnia |
| R-13 | Wymagania EPBD art. 14 dla rowerów (≥ 75–133 miejsc) a program (50 miejsc w parterze) | EPBD; PU s. 12; Wyj. 7/32 | +30–50 miejsc dla gości na skwerze lub bulwarze (MPZP § 46), miejsca cargo, ładowanie e-rowerów |
| R-14 | Moc przyłączeniowa EV (art. 12 ustawy o elektromobilności: wszystkie stanowiska × ≥ 3,7 kW) | [Z16] | ok. 103 × 3,7 ≈ 380 kW; przy zarządzaniu obciążeniem i współczynniku jednoczesności uwzględnić w stacji SN/nn (wniosek) |
| R-15 | Rozbieżność redakcyjna M.12 (okładka z informacją o standardach dostępności; nagłówek „M.09”) | M.12 | bez skutków merytorycznych; w opisie powoływać „Załącznik nr M.12” |

---

## 12. Benchmarki (skrót; pełne zestawienie i cele – `strategia_energetyczna.md` rozdz. 3)

| Wskaźnik | Wartość | Źródło / status |
|---|---|---|
| EPmax (PL, WT 2002) – budynek użyteczności publicznej, chłodzony, t₀ < 2500 h | 95 kWh/(m²·rok) energii pierwotnej nieodnawialnej (tylko usługi EPB); przy t₀ ≥ 2500 h – 120 <!-- poprawione przez weryfikatora --> | [P] [Z10] |
| EPZEB (PL, projekt WT, JSFP od 2028) | 85 kWh/(m²·rok); ECO2,ZEB ≈ 31,4 kg CO₂/(m²·rok); przy t₀ ≥ 2500 h – 107 i ≈ 37,4 <!-- poprawione przez weryfikatora --> | [PR] [Z11] |
| Próg ZEB biura, strefa kontynentalna (tylko **wniosek** Komisji 2021) | < 85 kWh/(m²·rok) energii pierwotnej całkowitej | [Z2] – nie obowiązuje |
| RIBA 2030 Climate Challenge v2 (UK, biura nowe): energia operacyjna (całe zużycie) | BAU ok. 130; cel 2025 < 75; cel 2030 < 55 kWh/(m²·rok) | *źródło wtórne* [Z28] |
| RIBA v2 – węgiel wbudowany biur (A1–A5, B1–B5, C1–C4) | cel 2030 < 750 kg CO₂e/m² | *źródło wtórne* [Z28] |
| GLA (Londyn) – benchmark upfront A1–A5 biura | < 950 kg CO₂e/m² GIA (aspiracyjny < 600); A–C bez B6–B7 z węglem biogenicznym < 1 400 (aspiracyjny < 970) | GLA, IX 2025 [Z27] |
| UK NZCBS (pilot IX 2024) – biura, całe budynki, upfront A1–A5 | 2025: 735 → 2028: 625 → 2030: 550 kg CO₂e/m² GIA | GLA, IX 2025 [Z27] |
| Modelowanie GLA – biura (upfront A1–A5, kg CO₂e/m² GIA; dwie skale: 5 400 / 13 500 m²) | Spec. 1: rama i stropy żelbetowe 9×9 m, 0% zamienników cementu – **908–932**; Spec. 2a: żelbet 7,5×7,5 m, 25% zamienników – **649–778**; Spec. 2b: jak 2a + 2 kondygnacje podziemne – **608–710** (wskaźnik na m² spada przez większą GIA, ale **emisje całkowite rosną**); Spec. 3: **stropy CLT na ramie stalowej (50% recyklingu)**, siatka 6×6 m – **509–549** | GLA, IX 2025 [Z27] |
| Żelbet vs drewno klejone (przegląd 62 badań) | średnio **o 42,68% wyższe** wbudowane emisje GHG budynków żelbetowych niż ich odpowiedników z drewna masywnego; energia wbudowana drewna średnio o 23% wyższa | Duan, Huang, Zhang 2022 (abstrakt) [Z29] |

---

## 13. Źródła

**Akty i dokumenty urzędowe (źródła oficjalne)**
- [Z1] Dyrektywa Parlamentu Europejskiego i Rady **(UE) 2024/1275** z 24.04.2024 w sprawie charakterystyki energetycznej budynków (wersja przekształcona), **Dz.Urz. UE L 2024/1275 z 8.5.2024** – art. 2, 7, 10, 11, 13, 14, 15, 16, 35–37; zał. I, III, IV: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32024L1275 (ELI: http://data.europa.eu/eli/dir/2024/1275/oj)
- [Z2] Wniosek Komisji **COM(2021) 802 final** z 15.12.2021 – dyrektywa w sprawie charakterystyki energetycznej budynków (przekształcenie), art. 7 i zał. III: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:52021PC0802
- [Z3] **Rozporządzenie delegowane Komisji (UE) 2026/52** z 16.12.2025 zmieniające załącznik III do dyrektywy (UE) 2024/1275 (unijne ramy obliczania GWP w cyklu życia), **Dz.Urz. UE L 2026/52 z 4.5.2026**, w życie 24.05.2026: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32026R0052 (ELI: http://data.europa.eu/eli/reg_del/2026/52/oj)
- [Z4] Dyrektywa Parlamentu Europejskiego i Rady **(UE) 2023/1791** z 13.09.2023 w sprawie efektywności energetycznej (EED), **Dz.Urz. UE L 231 z 20.9.2023, s. 1** – art. 2 pkt 12, art. 6, 7, 26, zał. IV: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32023L1791
- [Z5] Rozporządzenie delegowane Komisji **(UE) 2021/2139** (taksonomia – kryteria klimatyczne), wersja skonsolidowana z 1.01.2024, zał. I sekcja 7.1: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:02021R2139-20240101
- [Z6] Rozporządzenie Komisji **(UE) nr 1253/2014** (ekoprojekt central wentylacyjnych), zał. III pkt 2: https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32014R1253
- [Z7] Komisja Europejska / Transition Pathways – „Commission urges EU countries to implement reinforced building energy rules” (procedury z 15.07.2026; strona z 4.08.2026): https://transition-pathways.europa.eu/construction/news/commission-urges-eu-countries-implement-reinforced-building-energy-rules
- [Z8] Ustawa z 29.08.2014 o charakterystyce energetycznej budynków, **t.j. Dz.U. 2024 poz. 101**: https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20240000101 ; metryka ELI (akty zmieniające, ostatni Dz.U. 2023 poz. 1762): https://api.sejm.gov.pl/eli/acts/DU/2014/1200
- [Z9] Rozp. MIiR z 27.02.2015 w sprawie metodologii wyznaczania charakterystyki energetycznej budynku lub części budynku oraz świadectw charakterystyki energetycznej (**Dz.U. 2015 poz. 376**): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20150000376 ; zmiana **Dz.U. 2023 poz. 697** (w_el = 2,50; w życie 28.04.2023): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20230000697
- [Z10] Rozp. MI z 12.04.2002 w sprawie warunków technicznych … (WT 2002), **t.j. Dz.U. 2022 poz. 1225**, zm. Dz.U. 2023 poz. 2442, 2024 poz. 474 i 726 (§ 3 pkt 22, § 8, § 126, § 216 ust. 8, § 328–329, zał. 2 – brzmienie sprawdzone przez weryfikatora): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20220001225 ; status „uznany za uchylony” (2026-09-21; podstawa: art. 66 ustawy o dostępności [Z41]): https://api.sejm.gov.pl/eli/acts/DU/2002/690 <!-- poprawione przez weryfikatora -->
- [Z11] **Projekt** rozporządzenia w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (wersja z 13.05.2026; § 15, § 22, § 310–314, § 354–356, § 392). Kopia dokumentu rządowego w serwisie ZPP: https://www.zpp.pl/storage/library/2026-05/630f87410f0e537f673f75461f8dde4d.pdf (RCL niedostępny 16.11.2026)
- [Z12] Ustawa z 31.07.2026 o zmianie ustawy o samorządach zawodowych architektów oraz inżynierów budownictwa oraz ustawy – Prawo budowlane, **Dz.U. 2026 poz. 1161** (ogł. 1.09.2026). Art. 2 pkt 4 dodaje rozdz. 10a „Przepisy epizodyczne” – art. 102a–102c Pb – i wchodzi w życie dzień po ogłoszeniu, tj. 2.09.2026; reszta ustawy – 2.10.2026 (art. 5): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001161 ; tekst: https://api.sejm.gov.pl/eli/acts/DU/2026/1161/text.pdf (analiza: `wt_kluczowe.md`) <!-- poprawione przez weryfikatora -->
- [Z13] Ustawa – Prawo energetyczne, **t.j. Dz.U. 2026 poz. 43** (art. 7b): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000043 ; zmiana **Dz.U. 2026 poz. 900** (art. 1 pkt 6 – art. 7b ust. 4a, 9): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000900
- [Z14] **Projekt** ustawy o zmianie ustawy – Prawo energetyczne (UC121), OSR z 15.05.2026, Ministerstwo Energii (wdrożenie EED i RED III w ciepłownictwie). Kopia w serwisie ZPP: https://www.zpp.pl/storage/library/2026-05/290adc768518e2293fc00222f4696958.pdf
- [Z16] Ustawa o elektromobilności i paliwach alternatywnych, **t.j. Dz.U. 2026 poz. 1243** (art. 12, 12a): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001243
- [Z17] Ustawa – Prawo geologiczne i górnicze, **t.j. Dz.U. 2026 poz. 69** (art. 3 pkt 2, 85, 86, 88, 161): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000069
- [Z18] Ustawa – Prawo wodne, **t.j. Dz.U. 2026 poz. 1335** (art. 34 pkt 4, art. 76 ust. 1 pkt 5); zm. Dz.U. 2026 poz. 1358, poz. 1156 (w życie 1.01.2027): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001335
- [Z19] Ustawa o finansach publicznych, **t.j. Dz.U. 2026 poz. 1447** (art. 9 pkt 2): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260001447
- [Z20] Fortum Power and Heat Sp. z o.o. – sprawozdanie z art. 7b ust. 5 Prawa energetycznego za 2025 r. (Wrocław): https://www.fortum.pl/o-fortum/zrownowazony-rozwoj/sprawozdanie-z-dzialan-majacych-na-celu-osiagniecie-efektywnego-energetycznie-systemu-cieplowniczego
- [Z21] Fortum – wyciąg z taryf dla Wrocławia (stawki od 1.07.2026; decyzja Prezesa URE OWR.ZT.4210.33.2025.134.XXIV.SK z 12.12.2025): https://www.fortum.pl/cieplo/obsluga-klienta/taryfy-i-cenniki/wroclaw
- [Z22] MPWiK S.A. we Wrocławiu – „Wytyczne w zakresie gospodarowania wodami opadowymi na terenie miasta Wrocławia” RW25 v.4.1 (1.07.2026): https://www.mpwik.wroc.pl/wp-content/uploads/2026/06/RW25-v.4.1-WYTYCZNE.pdf
- [Z23] Urząd Miejski Wrocławia (wroclaw.pl, 7.08.2026) – Zarządzenie nr 5364/26, wytyczne GWO od 25.06.2026: https://www.wroclaw.pl/dla-mieszkanca/nowe-standardy-gospodarowania-woda-szkolenia-we-wroclawiu-mpwik
- [Z24] JRC PVGIS 5.3 (SARAH3, ERA5 2005–2023, horyzont DEM): https://re.jrc.ec.europa.eu/pvg_tools/en/ – zapytania API `PVcalc` dla 51,112°N 17,045°E (16.11.2026)
- [Z25] Materiały Organizatora: M.12, Regulamin (t.j. 13.02.2026), Program użytkowy (11.2025), F.14.B, F.15.C, M.05 – `/home/user/aihouse/umwd/00_materialy/tekst/`
- [Z26] MPZP – uchwała nr XLV/1366/10 Rady Miejskiej Wrocławia z 21.01.2010 (§ 6 pkt 13, § 14) – `../30_lokalizacja/mpzp_uchwala_XLV-1366-10_OCR.txt`, `../30_lokalizacja/mpzp.md`
- [Z27] Greater London Authority – „Towards a new London Plan. Evidence base for embodied and whole life carbon policies” (IX 2025): https://data.london.gov.uk/download/2yoq5/127/LPNZ%20Evidence-Embodied%20carbon.pdf
- [Z41] <!-- poprawione przez weryfikatora --> Ustawa z 19.07.2019 o zapewnianiu dostępności osobom ze szczególnymi potrzebami, **t.j. Dz.U. 2024 poz. 1411** – art. 66: dotychczasowe przepisy wykonawcze z art. 7 ust. 2 i 3 Pb zachowują moc „nie dłużej jednak niż przez 84 miesiące od dnia wejścia w życie niniejszej ustawy” (podstawa utraty mocy WT 2002): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20240001411 ; metryka WT 2002 w ELI („Uchylenia wynikające z: DU/2019/1696”): https://api.sejm.gov.pl/eli/acts/DU/2002/690
- [Z42] <!-- poprawione przez weryfikatora --> Ustawa – Prawo budowlane, **t.j. Dz.U. 2026 poz. 524** z późn. zm. – art. 33 ust. 2 pkt 10 (oświadczenie projektanta o możliwości podłączenia do sieci ciepłowniczej wg art. 7b Pe): https://isap.sejm.gov.pl/isap.nsf/DocDetails.xsp?id=WDU20260000524
- [Z43] <!-- poprawione przez weryfikatora --> Ustawa – Prawo wodne, t.j. Dz.U. 2026 poz. 1335 – art. 35 ust. 3, art. 169, art. 389, art. 390 ust. 1 pkt 1 lit. b: https://api.sejm.gov.pl/eli/acts/DU/2026/1335/text.pdf

**Źródła wtórne i literatura (pomocniczo)**
- [Z15] Inżynier Budownictwa (5.11.2026), „Transpozycja dyrektywy EPBD 2024/1275 do polskiego prawa budowlanego” – *źródło wtórne*: https://inzynierbudownictwa.pl/transpozycja-dyrektywy-epbd-2024-1275-do-polskiego-prawa-budowlanego/ ; RCL (niedostępne): https://legislacja.gov.pl/projekt/12347353
- [Z28] RIBA – 2030 Climate Challenge v2 (2021), strony architecture.com – *źródło wtórne* (wartości z omówień; PDF niepobrany): https://www.architecture.com/knowledge-and-resources/knowledge-landing-page/riba-2030-climate-challenge-aligning-the-targets-across-the-built-environment
- [Z29] Duan Z., Huang Q., Zhang Q. (2022), „Life cycle assessment of mass timber construction: A review”, *Building and Environment* 221, 109320 (wartości z abstraktu): https://doi.org/10.1016/j.buildenv.2022.109320
- [Z31] Brandl H. (2006), „Energy foundations and other thermo-active ground structures”, *Géotechnique* 56(2), 81–122 – literatura (niepobrana): https://doi.org/10.1680/geot.2006.56.2.81
- [Z32] Land Schleswig-Holstein – Erläuterungstext zur Wärmeleitfähigkeitskarte (zestawienie wartości VDI 4640 Bl. 2) – *źródło wtórne*: https://umweltanwendungen.schleswig-holstein.de/data/meta/boden/geotherm/ob/dok/Erlaeuterungstext_WLF.pdf
- [Z33] pv magazine (17.10.2023), „German energy supplier switches on 20 MW ‘river’ heat pump” (MVV Mannheim) – *źródło wtórne*: https://www.pv-magazine.com/2023/10/17/german-energy-supplier-switches-on-20-mw-river-heat-pump
- [Z34] CaGBC – „What new prerequisites under LEED v5 mean for projects” – *źródło wtórne*: https://www.cagbc.org/news-resources/cagbc-news/what-new-prerequisites-under-leed-v5-mean-for-projects
- [Z35] PLGBC – przewodnik Zielony Dom v2.01 – *źródło wtórne*: https://przewodnik.plgbc.org.pl
- [Z36] wroclaw.pl – zmiany klimatyczne we Wrocławiu (średnia temperatura 1991–2020: 9,7°C) – *źródło wtórne*: https://www.wroclaw.pl/zielony-wroclaw/zmiany-klimatyczne-we-wroclawiu-coraz-cieplejsze-lata-i-zimy-jakie-sa-prognozy-na-przyszlosc
- [Z37] RZGW Wody Polskie Wrocław – komunikaty o sytuacji hydrologicznej (II 2021, zjawiska lodowe na Odrze skanalizowanej) – znane z wyników wyszukiwania; dokumentów nie pobrano (serwer odrzucał połączenia): https://wroclaw.wody.gov.pl/
- [Z39] Fortum – WROMPA (pompa ciepła ze ścieków, 12,5 MW): https://www.fortum.pl/wrompa (dane za omówieniem w wynikach wyszukiwania)

**Nie zweryfikowano (16.11.2026):**
- aktualnych wskaźników emisyjności energii elektrycznej KOBiZE – serwis zwracał stronę „nie znaleziono”;
- etapu prac nad UC82 – RCL i gov.pl niedostępne;
- stawek opłaty za wody opadowe MPWiK;
- normy wieloletniej sumy opadów dla Wrocławia (IMGW 1991–2020).
- <!-- poprawione przez weryfikatora --> domyślnego czasu działania oświetlenia t₀ dla biur wg PN-EN 15193-1 (rozstrzyga, czy EPmax = 95 czy 120);
- numeru notyfikacji TRIS projektu WT (2026/0422/PL) i publikacji wytycznych KE dla bezpieczeństwa pożarowego parkingów (art. 14 ust. 10 EPBD). Limit wyszukiwań weryfikatora również został wyczerpany.

Limit wyszukiwań w tej sesji został wyczerpany.

### Weryfikacja adwersaryjna (16.11.2026) <!-- poprawione przez weryfikatora -->
Ponad 40 twierdzeń sprawdzono w tekstach źródłowych:
- EUR-Lex: dyrektywa 2024/1275 (EN/PL), COM(2021) 802, rozp. 2026/52, EED 2023/1791, taksonomia 2021/2139, rozp. 1253/2014;
- ELI/ISAP: metryki i teksty Dz.U. 2026 poz. 43, 69, 524, 900, 1161, 1243, 1335, 1447, Dz.U. 2024 poz. 1411, Dz.U. 2023 poz. 697, Dz.U. 2022 poz. 1225 wraz ze zmianami;
- projekt WT z 13.05.2026, M.12 i Regulamin.

Poprawiono:
- „dyrektywa nie wymaga bilansu rocznego” – wymaga rocznego pokrycia (art. 11 ust. 7);
- status WT 2002 – od 20.09.2026 nie obowiązują; art. 102a Pb jest opcją inwestora, a podstawą utraty mocy jest art. 66 ustawy o dostępności;
- nieurzeczywistnione wejście w życie projektu WT (§ 394);
- przypadek t₀ ≥ 2500 h (EPmax 120 / EPZEB 107);
- „wysokosprawna” kogeneracja w art. 26 EED;
- próg SCOP;
- podstawa pozwolenia wodnoprawnego (art. 389 Pw).

Dodano art. 390 ust. 1 pkt 1 lit. b Pw (warunkowo), uzupełniono art. 7 ust. 6 EPBD i listę zmian Pe.
