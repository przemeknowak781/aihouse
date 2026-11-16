# Strategia energetyczna i proekologiczna dla koncepcji budynku UMWD (rekomendacja konkursowa)

| | |
|---|---|
| Stan na | 16.11.2026 |
| Podstawa | `zero_emisja.md` (prawo UE i PL, M.12, rozbieżności, źródła [Z..]); obliczenia szacunkowe: `_bilans_energii.py` (uruchomienie: `python3 -I _bilans_energii.py`); powierzchnie: `../20_program/program.md`; warunki gruntowe: M.05; konflikty: `../30_lokalizacja/mpzp.md` (K-05), `ppoz.md` (7.7) |
| Status liczb | **szacunki koncepcyjne (wniosek)**. Do weryfikacji symulacją dynamiczną, testem TRT i kosztorysem po ustaleniu bryły. Wszystkie założenia są w `_bilans_energii.py` – po zmianie geometrii wystarczy podmienić parametry |
| Zakaz Inwestora | nie korzystano z informacji o pracach konkursowych tego konkursu |

---

## 1. Idea w jednym zdaniu i wskaźniki docelowe (KPI)

**Idea (wniosek):** budynek, który najpierw potrzebuje mało energii (bryła, osłony, masa termiczna, światło dzienne), potem korzysta z ciepła i chłodu gruntu pod sobą (75 odwiertów ≤ 100 m pracujących jak sezonowy magazyn), a resztę energii pobiera ze słońca zintegrowanego z dachami i przegrodami. Nie ma w nim żadnego spalania. Sieć miejska pełni rolę rezerwy, a woda deszczowa i szara obsługuje toalety i zieleń.

| KPI | Cel koncepcji | Odniesienie | Status |
|---|---|---|---|
| Spalanie paliw kopalnych na miejscu | **0** (bez przyłącza gazu; agregat na HVO100 tylko awaryjnie) | EPBD art. 11 ust. 1; M.12 pkt 1 lit. c | wymóg |
| EP (energia pierwotna nieodnawialna, usługi EPB) | **≈ 30 kWh/(m²·rok)** z PV (≈ 60 bez PV) | EPmax WT 2002 = 95; EPZEB (projekt WT, od 2028) = 85 – obie wartości dla t₀ < 2500 h (zachowawczo); przy t₀ ≥ 2500 h: 120 / 107 <!-- poprawione przez weryfikatora --> | szacunek |
| Energia końcowa – całość (z IT i serwerownią) | **≈ 52 kWh/(m² Af·rok)** ≈ 650 MWh/rok (≈ 32 kWh/(m² PC·rok)) | RIBA 2030: biura < 55 (cel 2030) | szacunek |
| Energia końcowa – usługi EPB | **≈ 24 kWh/(m² Af·rok)** ≈ 300 MWh/rok | – | szacunek |
| PV na działce | **0,40 MWp ≈ 333 MWh/rok** (wariant warunkowy 0,50 MWp ≈ 393 MWh/rok) | M.12: 0,4–1,0 MWp | szacunek |
| Roczny bilans OZE na działce | **≈ 110% zużycia EPB**, ≈ 51% zużycia całkowitego | M.12 pkt 1 lit. d | szacunek |
| Emisje operacyjne (lokalizacyjne, EF 0,6 kg/kWh) | **≈ 7 kg CO₂/(m²·rok)** (EPB); ≈ 18 (całość) | próg ZEB projektu WT ≈ 31 | szacunek |
| Pompy ciepła gruntowe | **75 BHE × 99 m** (≈ 7 400 m), pole ≈ 2 700 m² pod budynkiem; ≈ 430 kW grzania, ≈ 330 kW chłodu aktywnego z gruntu + free-cooling | M.12 pkt 1 A | szacunek |
| Woda z sieci | **−40–45%** (ok. 1 440 m³/rok zastąpione wodą szarą i deszczową) | M.12 pkt 2 | szacunek |
| Odpływ wód opadowych | ψ śr. 0,72 → **0,48**; Qdm(C = 10, 15 min) 55 → **36 dm³/s** przed retencją; zbiorniki ≥ 55 m³ retencji + 60–80 m³ zbiornika użytkowego | RW25 v.4.1 | szacunek |
| Węgiel wbudowany A1–A5 | **≤ 600 kg CO₂e/m² PC** (ambicja ≤ 550) | GLA aspiracyjny < 600; UK NZCBS 2028: 625, 2030: 550 | cel |
| GWP w cyklu życia | obliczany wg EN 15978 / Level(s) 1.2 / rozp. (UE) 2026/52 od koncepcji | EPBD art. 7 ust. 2 | deklaracja |
| Automatyka | **BACS klasy A** (PN-EN ISO 52120-1), EMS, monitoring IEQ (CO₂, T, RH) | EPBD art. 13 ust. 5, 9–12; art. 15 (SRI) | deklaracja |
| E-mobilność | **≥ 1 punkt ładowania / 2 miejsca** (≥ 52 przy 103 m.p.), okablowanie wstępne 100%; rowery 50 + 30–50 dla gości, w tym cargo | EPBD art. 14; ustawa o elektromobilności art. 12, 12a | deklaracja |

---

## 2. Zasada porządkująca: „najpierw efektywność, potem źródła”

Kolejność działań wynika z zasady „efektywność energetyczna przede wszystkim” (EED art. 3) i z M.12 („preferencja dla rozwiązań pasywnych”):

1. **Pasywne** – bryła, przegrody, osłony, światło, masa termiczna, przewietrzanie, zieleń.
2. **Aktywne, wysokosprawne** – niskotemperaturowe ogrzewanie i wysokotemperaturowe chłodzenie, odzysk ciepła, LED, automatyka.
3. **OZE** – grunt i słońce na miejscu.
4. **Magazyny** – bufory, BTES, BESS.
5. **Zarządzanie** – BMS/EMS, elastyczność wobec sieci, monitoring i rozruch.
6. **Uzupełnienie z zewnątrz** – OZE ze społeczności lub klastra, sieć ciepłownicza jako rezerwa.

---

## 3. Benchmarki – gdzie plasuje się projekt

### 3.1. Energia operacyjna

| Benchmark | Wartość | Metryka | Źródło |
|---|---|---|---|
| WT 2002 – EPmax, budynek użyteczności publicznej, chłodzony, t₀ < 2500 h | 95 | kWh/(m² Af·rok), energia pierwotna nieodnawialna, usługi EPB | [Z10] |
| Projekt WT – EPZEB (JSFP od 2028) | 85 | jw. | [Z11] |
| Wniosek KE 2021 – próg ZEB biura, strefa kontynentalna | < 85 | kWh/(m²·rok), energia pierwotna **całkowita** | [Z2] (nie obowiązuje) |
| RIBA 2030 Climate Challenge v2 – nowe biura (UK) | BAU ≈ 130; 2025: < 75; 2030: < 55 | kWh/(m²·rok) energii dostarczonej, całe zużycie | [Z28] *źródło wtórne* |
| **Projekt UMWD (szacunek)** | **≈ 52 (całość) / ≈ 24 (EPB) / EP ≈ 30** | jw. | `_bilans_energii.py` |

Metryki różnią się zakresem (EPB a całość, Af a GIA, energia pierwotna a dostarczona). Na planszy porównywać tylko **EP z EPmax** (prawo polskie) oraz **energię końcową całkowitą z RIBA 2030** (wniosek).

### 3.2. Węgiel wbudowany (embodied carbon)

| Benchmark | Wartość [kg CO₂e/m² GIA] | Źródło |
|---|---|---|
| GLA (Londyn) – biura, upfront A1–A5 | benchmark < 950; aspiracyjny < 600 | [Z27] |
| GLA – biura, A–C bez B6–B7, z węglem biogenicznym | < 1 400; aspiracyjny < 970 | [Z27] |
| UK NZCBS (pilot 2024) – biura, upfront | 2025: 735; 2028: 625; 2030: 550 | [Z27] |
| RIBA 2030 v2 – biura (A1–A5, B1–B5, C1–C4) | cel 2030 < 750 | [Z28] *źródło wtórne* |
| Modelowanie GLA – specyfikacje biurowe | żelbet 9×9 m bez zamienników cementu 908–932; żelbet 7,5×7,5 m z 25% zamienników 649–778; z 2 kondygnacjami podziemnymi 608–710 (emisje całkowite rosną); **stropy CLT na ramie stalowej (50% recyklingu) 509–549** | [Z27] |
| Przegląd 62 badań LCA (Duan i in. 2022) | budynki żelbetowe średnio **+42,68%** wbudowanych emisji GHG wobec odpowiedników z drewna masywnego | [Z29] |

---

## 4. Warstwa pasywna (architektura) – zalecenia

| Element | Zalecenie (wniosek) | Uzasadnienie |
|---|---|---|
| Bryła | kwartałowa, zwarta (domknięcie kwartału), dominanta jako zwarty segment. Mały współczynnik A/V; ograniczać uskoki i wspornikowe tarasy (mostki) | mniejsze straty; spójne z wytycznymi DWKZ (`konserwator.md`) |
| Przeszklenie (WWR) | **35–50%** na elewacjach w pierzejach (rytm okien jak w kamienicach), więcej w holach i sali obrad – z osłonami. Elewacje N bez ograniczeń dla światła | kompromis: światło dzienne, zyski i chłód, konserwator („unikać dominacji szkła kurtynowego”) |
| Przegrody (cele lepsze od WT) | ściany **U ≤ 0,15**; dachy **≤ 0,12**; okna i fasady **Uw/Ucw ≤ 0,8** (pakiety 3-szybowe); strop nad garażem ≤ 0,20; mostki Ψ ≤ 0,05 W/(mK); szczelność **n50 ≤ 0,6–1,0 h⁻¹** z testem (taksonomia: obowiązkowy test dla > 5000 m²) | WT 2002: 0,20 / 0,15 / 0,9 [Z10]; taksonomia 7.1 [Z5] |
| Osłony przeciwsłoneczne | elewacje S/E/W: **zewnętrzne** żaluzje lub lamele sterowane (fc ≤ 0,15) albo stałe głębokie ościeża i lizeny (rytm pionowy). Szkło g ≈ 0,30–0,35, Lt ≥ 0,6. Sala Sejmiku: świetliki lub okna N i E oraz osłony | WT zał. 2: g ≤ 0,35; główny czynnik ograniczający chłód (budynek biurowy jest „chłodzeniowy”) |
| Światło dzienne | głębokość traktu biurowego ≤ 6–7 m od okna (pokoje 24 m²); jasne stropy; cel wg PN-EN 17037 (poziom minimalny w strefach pracy) | mniejsze zużycie na oświetlenie (ΔEPL) |
| Masa termiczna | odsłonięte stropy żelbetowe w biurach lub **TABS** (betonowe stropy aktywowane termicznie) w części żelbetowej; nocne wychładzanie | „akumulacja cieplna konstrukcji” – M.12 pkt 1. Wysokotemperaturowe chłodzenie (16–19°C) zwiększa udział free-coolingu z gruntu |
| Przewietrzanie | uchylne skrzydła od dziedzińca (cicho) – przewietrzanie w okresach przejściowych i nocne (automatyka). Od ulic i mostu okna z nawiewnikami akustycznymi lub zamknięte (wentylacja mechaniczna) | hałas tramwaju i mostu; `wt_kluczowe.md` 11 |
| Mikroklimat | zachowane drzewa w ogródku, zielony dziedziniec, jasne nawierzchnie (wysokie albedo), ogród deszczowy, zielone dachy | miejska wyspa ciepła; retencja (RW25) |
| Sala Sejmiku | wentylacja wyporowa lub podpodłogowa sterowana CO₂, odzysk ciepła, akustyka sufitu, ograniczone przeszklenia S i W (lub głębokie osłony), światło górne z osłonami | duże zyski od ludzi przy sporadycznym użytkowaniu – sterowanie popytowe |

---

## 5. Warstwa aktywna i OZE

### 5.1. Fotowoltaika (PV/BIPV)

**Uzyski jednostkowe (PVGIS 5.3, SARAH3, Wrocław 51,112°N 17,045°E, straty 14%, horyzont terenowy bez zacienienia zabudową)** [Z24]:

| Orientacja / kąt | kWh/kWp·rok | Napromieniowanie płaszczyzny kWh/m²·rok |
|---|---|---|
| S 35° (optimum) | **1 090** | 1 362 |
| S 10° (dach płaski) | 983 | 1 240 |
| E lub W 10° (układ „wschód–zachód” na dachu płaskim) | 893–894 | 1 138–1 139 |
| pion S | **787** | 990 |
| pion SE / SW | 718–728 | 912–916 |
| pion E / W | 532–536 | 689–703 |
| pion NE | 301 | 420 |
| pion N | **192** | 291 |

**Ograniczenia lokalizacji PV (fakt / wniosek):**
- MPZP § 6 pkt 13 zakazuje urządzeń na dachach i na elewacjach od ulic, placów i bulwarów. Rozwiązanie: **PV jako pokrycie dachu (BIPV/biosolar) za attyką i jako element przegrody od dziedzińca** (`zero_emisja.md` R-01).
- WT § 216 ust. 8 wymaga niepalnej okładziny powyżej 25 m, więc **BIPV na dominancie powyżej 25 m jest tylko wariantem warunkowym** (R-02).
- Elewacje N są nieopłacalne (192 kWh/kWp).

**Bilans PV (szacunek):**

| Pole PV | kWp | kWh/kWp | MWh/rok | Uwagi |
|---|---|---|---|---|
| Dachy – BIPV jako pokrycie / biosolar E-W 10°, ok. 1 700 m² (≈ 74% dachów) | 340 | 900 | **306** | dach dominanty + dachy skrzydeł; nad zielenią ekstensywną; niewidoczne z mostu i ulic (attyka); ok. 0,20 kWp/m² w układzie E-W |
| Elewacje od dziedzińca ≤ 25 m – BIPV w pasach podokiennych, ok. 400 m² | 60 | 450 | **27** | uwzględnia zacienienie własne i sąsiedztwa |
| **Razem – wariant podstawowy** | **400** | – | **333** | = dolna granica M.12 (0,4 MWp) |
| Opcja: dominanta > 25 m – BIPV w przeszkleniach i pasach szklanych S/E/W | +100 | 600 | +60 | tylko przy klasyfikacji ogniowej i NRO elewacji |
| **Razem z opcją** | **500** | – | **393** | |

**Dlaczego nie 1,0 MWp na działce (do opisu):**
- 1 MWp wymaga ok. 5 000–6 500 m² modułów. Wszystkie dachy mają ok. 2 300 m², a sensowne elewacje do 25 m od dziedzińca – kilkaset m².
- Elewacje od ulic wyklucza MPZP, a elewacje N dają 192 kWh/kWp.
- **Uzupełnienie (wniosek):** brakujące ok. 0,5–0,6 MWp jako instalacja Województwa poza działką, w ramach **społeczności energetycznej, spółdzielni energetycznej lub klastra energii**. Mieści się to w EPBD art. 11 ust. 7 lit. b i w projekcie WT § 354 ust. 1 pkt 3 lit. b. Tak domyka się „bilans roczny” M.12 dla całego zużycia.

### 5.2. Źródło ciepła i chłodu – gruntowe pompy ciepła z magazynem sezonowym (BTES)

**Zapotrzebowanie (szacunek; Af ≈ 12 500 m²):**
- ogrzewanie ≈ 25 kWh/(m²·rok) energii użytkowej (≈ 310 MWh/rok);
- c.w.u. ≈ 4 kWh/(m²·rok) (≈ 50 MWh/rok);
- chłodzenie ≈ 30 kWh/(m²·rok) (≈ 375 MWh/rok);
- serwerownia ≈ 10 kW średnio (≈ 88 MWh/rok ciepła odpadowego do odzysku);
- moce szczytowe: grzanie ≈ 350 kW (θe = −18°C), chłód ≈ 600 kW.

**Układ (wniosek):**
- **Pole BHE: 75 otworów × 99 m** (≤ 100 m – poza reżimem art. 86 PGiG), siatka ok. 6 × 6 m, ≈ 2 700 m² **pod płytą fundamentową** (dopuszcza to M.12 pkt 1 A). Długość czynna ≈ 7 125 m. Rury PE-RC 2U lub koaksjalne, iniekcja przewodząca (szczelność wobec poziomu naporowego na 16,5 m – M.05).
- Moce z gruntu (45 W/m pobór, 55 W/m oddawanie – ostrożnie wobec VDI 4640 dla nawodnionych żwirów 55–80 W/m):
  - pobór ≈ 320 kW, czyli **moc grzewcza PC ≈ 430 kW** – pokrywa całe zapotrzebowanie;
  - oddawanie ≈ 390 kW, czyli **chłód aktywny ≈ 330 kW** oraz free-cooling (bez sprężarki) w okresach przejściowych i nocą.
- **Pompy ciepła:** 2–3 jednostki woda-woda (redundancja N+1), w tym jedna z **jednoczesnym grzaniem i chłodzeniem** (odzysk ciepła z chłodzenia do c.w.u. i ogrzewania strefy N w okresach przejściowych). Czynnik o niskim GWP (np. propan R290 lub R1234ze w maszynowni wydzielonej). Niskotemperaturowe ogrzewanie (TABS lub belki/klimakonwektory 30–35°C) i wysokotemperaturowe chłodzenie (16/19°C). SCOP grzania ≈ 4,5; EER aktywny ≈ 5,5.
- **Bilans gruntu:** rocznie pobór ≈ 243 MWh, oddanie ≈ 409 MWh. Nadwyżka ≈ 166 MWh/rok groziłaby stopniowym ogrzewaniem pola. Środki:
  1. ograniczenie zysków (osłony zewnętrzne);
  2. odzysk ciepła z chłodzenia i z serwerowni do c.w.u. i ogrzewania;
  3. **hybrydowy dry-cooler** w piętrze technicznym (wyrzut od dziedzińca; nie na dachu – MPZP) do zrzutu nadwyżki i pokrycia szczytów chłodu ponad ≈ 330 kW;
  4. symulacja 25-letnia (EED/EWS/TRNSYS) i TRT na etapie PB.

  To jest właśnie „magazyn sezonowy” z M.12: lato ładuje grunt ciepłem z chłodzenia, zima je odbiera.
- **Uzupełnienia (opcje):**
  - **ściany szczelinowe i pale energetyczne** (konstrukcje termoaktywne) – jeżeli konstrukcja garażu w wodzie gruntowej przewiduje ściany szczelinowe lub pale kotwiące (Brandl 2006) [Z31];
  - **układ otwarty (dublet studni)** w czwartorzędowych żwirach – po próbnym pompowaniu. Wymaga pozwolenia wodnoprawnego (art. 389 pkt 1 w zw. z art. 35 ust. 3 pkt 1 Pw); zatłaczanie wód z pomp ciepła do wód podziemnych dopuszcza art. 76 ust. 1 pkt 5 Pw. <!-- poprawione przez weryfikatora -->
  - **Odra i Oława – nie** jako źródło podstawowe: zimą woda ok. 0°C (zjawiska lodowe), latem ciepła; ujęcie i formalności nieproporcjonalne (`zero_emisja.md` 7.3).
- **Magazyny krótkoterminowe:** zbiorniki buforowe ciepła ≈ 10–15 m³ i chłodu ≈ 20 m³ w maszynowni. Stabilizują sprężarki, przesuwają pracę na godziny produkcji PV i umożliwiają nocne schładzanie TABS.
- **c.w.u.:** głównie lokalna (umywalki w biurach bez c.w.u. lub z małymi podgrzewaczami tylko tam, gdzie potrzebne). Centralnie: prysznice przy rowerowni, zaplecza, pralnia – stopień dogrzewu na PC (COP ≈ 3) zasilany ciepłem z serwerowni i chłodzenia. Legionella: dezynfekcja termiczna.
- **Rezerwa i szczyt: węzeł ciepłowniczy Fortum** (M.12 pkt 1 E) o mocy zamówionej ograniczonej do ok. 0,3–0,4 MW. Pracuje tylko przy awarii lub ekstremach. Opłata stała ≈ 163 tys. zł/MW/rok (część wytwórcza, od 1.07.2026) [Z21], dlatego moc rezerwy należy optymalizować (redundancja N+1 PC może ją zmniejszyć).

### 5.3. Wentylacja i odzysk ciepła
- Centrale nawiewno-wywiewne w piętrze technicznym (PU s. 13), odzysk **≥ 80%** (wymóg ekoprojektu ≥ 73%) [Z6].
- Sterowanie popytowe wg CO₂ i obecności (VAV): biura, sale konferencyjne, sala obrad.
- SFP ≈ 1,2–1,5 kW/(m³/s).
- Czerpnie i wyrzutnie od dziedzińca lub w integracji z architekturą (MPZP § 6 pkt 13).
- Free-cooling nocny powietrzem.
- Filtry F7/ePM1 (smog w sezonie grzewczym).

### 5.4. Elektryczność, oświetlenie, automatyka
- **LED ≤ 5 W/m²** w biurach, DALI-2 ze sterowaniem światłem dziennym i obecnością (EPBD art. 13 ust. 12).
- **BACS klasy A** (PN-EN ISO 52120-1) i **EMS**:
  - podliczniki na każdym piętrze i medium;
  - pulpit energii w holu (edukacja publiczna);
  - prognozowanie PV i taryf;
  - sterowanie ładowaniem EV i BESS;
  - monitoring IEQ (EPBD art. 13 ust. 5).
- Otwarte protokoły (BACnet/IP, KNX/DALI, Modbus); cyfrowy dziennik budynku (EPBD art. 16) pod przyszłą ocenę SRI (art. 15).
- **Dźwigi** z odzyskiem energii hamowania.
- **Serwerownia TIER II**: chłodzenie wodne lub rzędowe z odzyskiem ciepła do pętli PC; podwyższone temperatury zasilania (ASHRAE A1, 18–27°C).

### 5.5. Magazyn energii, praca wyspowa, odporność
- **BESS ≈ 250–300 kWh (LFP)**: przesuwanie produkcji PV, ograniczenie mocy szczytowej (EV), zasilanie odbiorów krytycznych z UPS.
- **Lokalizacja:** parter przy strefie dostaw od Wybrzeża Słowackiego (dostęp z zewnątrz) albo −1 z dostępem przez garaż. Osobne pomieszczenie EI, detekcja, wyłącznik awaryjny (projekt WT § 310–314: ≤ 300 kWh na −1 lub w parterze; > 300 kWh tylko w parterze z bezpośrednim wejściem z zewnątrz; nie powyżej 25 m) [Z11]. Nie na −2 (zagrożenie powodziowe – M.05).
- **Tryb samowystarczalny (M.12 pkt 1 lit. e):** wydzielona szyna odbiorów krytycznych – serwerownia, BMS, oświetlenie awaryjne, wentylacja MDS (garaż jako miejsce doraźnego schronienia – PU s. 3), dźwig ewakuacyjny, punkt dowodzenia. Zasilanie z PV, BESS i agregatu na **HVO100** (paliwo odnawialne; praca tylko w testach i awariach – `zero_emisja.md` R-08).

### 5.6. Mobilność
- **Garaż** (minimum 103 m.p. wg MPZP; `program.md`):
  - **≥ 52 punkty AC 11 kW** (1 punkt / 2 miejsca – EPBD art. 14 ust. 1 dla biurowców), okablowanie wstępne dla pozostałych;
  - 2 punkty DC 50 kW dla floty urzędu (pojazdy służbowe – gotowość V2G);
  - dynamiczne zarządzanie mocą.
  - Przyłącze z mocą pozwalającą wyposażyć wszystkie stanowiska w punkty ≥ 3,7 kW (art. 12 ustawy o elektromobilności): ok. 380 kW przed współczynnikiem jednoczesności.
- **Rowery:** 50 stanowisk w parterze z zapleczem i prysznicami (PU s. 12) oraz **30–50 stojaków dla gości** na skwerze lub bulwarze (MPZP § 46) i **2–4 miejsca cargo**, ładowanie e-rowerów (EPBD: ≥ 15% średniej liczby użytkowników ≈ 75 miejsc).
- Bezpieczeństwo pożarowe EV w garażu: koordynacja z `ppoz.md` (tryskacze, wentylacja, wyłączniki).

---

## 6. Kwantyfikacja (wyniki `_bilans_energii.py`; szacunek)

### 6.1. Energia końcowa (elektryczna), Af ≈ 12 500 m²

| Pozycja | kWh/(m²·rok) | MWh/rok |
|---|---|---|
| Ogrzewanie (25 / SCOP 4,5) | 5,6 | 70 |
| c.w.u. (4 / COP 3,0) | 1,3 | 17 |
| Chłodzenie (30; 50% free-cooling SEER 20, 50% aktywnie EER 5,5) | 3,5 | 44 |
| Wentylatory | 5,0 | 63 |
| Pompy, automatyka | 2,0 | 25 |
| Oświetlenie | 6,5 | 81 |
| **Suma EPB** | **23,9** | **≈ 298** |
| Urządzenia biurowe | 18,0 | 225 |
| Serwerownia (10 kW × 8760 h) | 7,0 | 88 |
| Dźwigi, inne | 3,0 | 38 |
| **Razem** | **≈ 52** | **≈ 648** |

### 6.2. Bilans OZE i sieć
- PV 0,40 MWp: **333 MWh/rok**, czyli **112% zużycia EPB** i **51% zużycia całkowitego**.
- Autokonsumpcja ≈ 80% (profil dzienny biura, BESS, EV, magazyny ciepła i chłodu): **266 MWh**, eksport ≈ 67 MWh.
- Pobór z sieci ≈ 380 MWh/rok. Dla raportowania „100% OZE” – kontrakt ze społeczności energetycznej lub klastra Województwa albo gwarancje pochodzenia (ujęcie rynkowe; wniosek).

### 6.3. Energia pierwotna i emisje
- **EP ≈ 60 kWh/(m²·rok) bez PV** (23,9 × w_el 2,5). **EP ≈ 28–32 z PV**, zależnie od przypisania autokonsumpcji usługom EPB w metodologii [Z9]. Porównanie: EPmax 95 (WT 2002), EPZEB 85 (projekt WT) – obie przy t₀ < 2500 h. **Margines wobec 95: ok. −37% bez PV i ok. −66–71% z PV.** Przy t₀ ≥ 2500 h (EPmax 120) margines jest jeszcze większy. <!-- poprawione przez weryfikatora -->
- Emisje operacyjne (lokalizacyjne, EF ≈ 0,6 kg CO₂/kWh – rząd wielkości, nie zweryfikowano w KOBiZE):
  - EPB ≈ **6,6 kg CO₂/(m²·rok)**;
  - całość ≈ **18 kg CO₂/(m²·rok)** (≈ 230 t/rok).

  Próg ZEB z projektu WT ≈ **31,4 kg**. Przy kontraktach OZE emisje rynkowe ≈ 0.
- **Art. 7b Prawa energetycznego:** wskaźnik w źródła PC ≈ 2,5/4,5 = **0,56 ≤ 0,8**, udział OZE ≈ **78% ≥ 60%**, więc obowiązek przyłączenia nie dotyczy źródła podstawowego (`zero_emisja.md` 6).

### 6.4. Woda

| Strumień | m³/rok | Założenie |
|---|---|---|
| Spłukiwanie WC i pisuarów | ≈ 1 435 | 403 os. × 13 l + 100 gości × 5 l, 250 dni; WC 6/3 l (średnio ≤ 3,5 l), pisuary ≤ 1 l |
| Woda szara (umywalki, prysznice) | ≈ 805 | baterie ≤ 6 l/min (5 l/os.·d); 30 pryszniców/d × 40 l |
| Woda deszczowa (dachy) | ≈ 665 | opad ≈ 570 mm/rok (założenie – do weryfikacji IMGW); 1 100 m² dachów twardych × 0,8 + 1 200 m² zielonych × 0,35; 90% sprawności zbierania |
| Podlewanie | ≈ 135 | 900 m² zieleni × 0,15 m³/m² sezon |
| **Zużycie bazowe wody z sieci** | **≈ 3 400** | 30 l/os.·d pracownika, 10 l/gościa + podlewanie |
| **Zastąpione wodą szarą i deszczową** | **≈ 1 440 (−42%)** | spłukiwanie ≈ 91% (≈ 1 304 z 1 435 m³) z wody szarej i deszczowej, reszta z wodociągu przez zabezpieczone dopuszczenie (PN-EN 1717); podlewanie w 100% z deszczowej <!-- poprawione przez weryfikatora: wynik _bilans_energii.py, min(1435; 804 + 0,75·667) --> |

Urządzenia:
- dwa systemy kanalizacji (czarna i szara) z odrębną instalacją „wody szarej oczyszczonej”, oznakowaną i **niepołączoną z wodociągiem** (M.12 pkt 2C; WT § 126 ust. 3 analogicznie);
- **oczyszczalnia wody szarej MBR + UV ≈ 5 m³/d** (pomieszczenie ≈ 25–35 m² na −1);
- **zbiornik użytkowy wody deszczowej 60–80 m³** na zewnątrz budynku (M.12 pkt 2B), pod nawierzchnią dojazdu i poza strefą korzeni zachowanych drzew. Woda gruntowa na 3,2–3,8 m wymaga zakotwienia przeciw wyporowi i zaworu zwrotnego (strefa podtopień).

**Odzysk ciepła z wody szarej (M.12 pkt 2D) – analiza (wniosek):**
- strumień ≈ 805 m³/rok × ΔT ≈ 10 K × 1,163 kWh/(m³·K) ≈ **9 MWh/rok** potencjału teoretycznego, czyli ≈ 2–3% zapotrzebowania na ciepło;
- praktycznie przy pionowych wymiennikach na odpływach pryszniców (ok. 50% sprawności) ≈ 3–5 MWh/rok.

**Wniosek:** stosować tylko na odpływach pryszniców (rowerownia, zaplecza) – tanie, bezobsługowe. Priorytetem są większe źródła ciepła odpadowego: **serwerownia ≈ 88 MWh/rok** i odzysk z chłodzenia. Uczciwa liczba na planszy podnosi wiarygodność („zasadność”).

### 6.5. Retencja (RW25 v.4.1; C = 10 lat – zabudowa śródmiejska) [Z22]

| Powierzchnia | m² | ψ przed | ψ po |
|---|---|---|---|
| Dach dominanty z PV | 900 | 0,95 | 0,95 |
| Dachy skrzydeł (zielone > 10 cm, biosolar) | 1 200 | 0,95 | **0,30** |
| Tarasy | 200 | 0,95 | 0,80 |
| Nawierzchnie dziedzińca i dojazdu (kostka na podbudowie przepuszczalnej) | 500 | 0,80 | 0,60 |
| Zieleń na gruncie (ogródek, ogród deszczowy) | 900 | 0,10 | 0,10 |
| **Średnio** | **3 700** | **0,72** | **0,48** |

- **Qdm (15 min, q = 204,7 dm³/(s·ha))**: ≈ 55 → **≈ 36 dm³/s** (−35%) przed retencją zbiornikową.
- Objętość opadu 60 min (30,44 mm) z powierzchni zredukowanej ≈ **54 m³**. Wymiarowanie właściwe: metoda zbiorników wg RW25 rozdz. IV.3 i dopuszczalny odpływ z warunków MPWiK – nieznany na etapie konkursu.
- **Rekomendacja:**
  - zbiornik retencyjno-detencyjny ≥ 55–70 m³ z regulatorem odpływu i przelewem awaryjnym do sieci (M.12 pkt 2B), oddzielny od zbiornika użytkowego;
  - ogród deszczowy lub niecka w dziedzińcu;
  - zielone dachy;
  - nawierzchnie przepuszczalne.

  Infiltracja ograniczona (woda gruntowa płytko, nasypy) – RW25 i tak wymaga rozwiązań ZNI („trudne warunki nie zwalniają”).

### 6.6. Orientacyjne koszty pozycji F.14.B (rząd wielkości; wniosek – do weryfikacji kosztorysem i ofertami)

| Pozycja F.14.B | Zakres | Rząd kosztu netto |
|---|---|---|
| 2.12 / 7.8 | pole BHE ≈ 7 400 mb, kolektory, maszynownia PC ≈ 430/330 kW, dry-cooler hybrydowy, automatyka | ≈ 4–6 mln zł |
| 7.9 | bufory ciepła i chłodu | ≈ 0,2–0,4 mln zł |
| 2.13 / 8.17 | PV 0,40 MWp (BIPV dachowe + elewacyjne od dziedzińca) + BESS ≈ 250–300 kWh | ≈ 2,5–3,5 mln zł |
| 7.1 / 7.3 | podwójne instalacje (szara i czarna), oczyszczalnia MBR + UV, sieć wody szarej | ≈ 0,8–1,5 mln zł |
| 15.10 | retencja i zbiornik użytkowy, ogród deszczowy, regulatory | ≈ 0,4–0,8 mln zł |
| 15.9 | ≥ 52 punkty AC + 2 DC, zarządzanie mocą, trasy kablowe | ≈ 1,0–1,6 mln zł |
| 17 / 17.1 | przyrost kosztu: odzysk ciepła ≥ 80%, BACS klasy A, EMS, monitoring IEQ, zielone dachy ≈ 1 200–1 500 m² | ≈ 1,0–2,0 mln zł |
| **Razem rozwiązania „eko”** | | **≈ 10–16 mln zł (≈ 7–11% z 150 mln zł)** |

**Efekt eksploatacyjny (wniosek; ceny do weryfikacji):**
- PV: ≈ 266 MWh autokonsumpcji × ok. 0,8–1,0 zł/kWh ≈ 0,2–0,27 mln zł/rok;
- PC zamiast ciepła sieciowego: koszt sieci ≥ 0,18 mln zł/rok (sama część wytwórcza wg taryfy Fortum) wobec ≈ 0,08 mln zł energii dla PC;
- free-cooling zamiast agregatów (≈ 60 MWh/rok mniej);
- woda: ≈ 1 440 m³/rok.

Łącznie rzędu **0,4–0,5 mln zł/rok**. Część nakładów i tak jest obowiązkowa (PV, EV, wentylacja, chłodzenie), więc okres zwrotu przyrostu ok. 12–17 lat (wniosek orientacyjny). W opisie przedstawić to jako analizę kosztów w cyklu życia (LCC, Level(s) 6.1), nie jako „zwrot”.

---

## 7. Węgiel wbudowany i materiały – strategia

1. **Największą dźwignią jest podziemie.** Dwie kondygnacje w wodzie gruntowej to ściany szczelinowe, gruba płyta przeciw wyporowi i ewentualnie pale kotwiące, czyli duży udział emisji A1–A5 i kosztu. Według GLA piwnice podnoszą emisje całkowite, nawet jeśli wskaźnik na m² nie rośnie [Z27]. **Rekomendacja:** kompaktowy garaż wymiarowany na minimum MPZP (103 m.p.) i MDS, bez nadmiaru miejsc. Kubaturę −2 przeznaczyć na technikę i MDS tylko w niezbędnym zakresie (decyzja programowa Zamawiającego: PU zakłada 2 kondygnacje).
2. **Beton niskoemisyjny:** cementy CEM III/A lub CEM II/C-M, wysoki udział zamienników (żużel, popiół), kruszywa z recyklingu w elementach niekonstrukcyjnych; specyfikacja ślad GWP betonu w kg CO₂e/m³ z EPD.
3. **Lekka nadbudowa.** Płyty sprężone (cieńsze stropy) albo **hybryda: stropy drewniano-betonowe (TCC) lub CLT na ramie stalowej lub żelbetowej** w skrzydłach (≤ 25 m). Mniejszy ciężar odciąża fundamenty i zmniejsza podziemną konstrukcję. Benchmark GLA Spec. 3 (stropy CLT na ramie stalowej): **≈ 509–549 kg CO₂e/m²** wobec 650–930 dla żelbetu [Z27]. **Warunek:** klasa odporności pożarowej „B” (R 120, NRO) dla budynku W lub rozdzielenie skrzydeł jako SW (`ppoz.md`). Drewno w przegrodach głównie zabezpieczone (enkapsulacja), widoczne w wybranych wnętrzach z klasyfikacją reakcji na ogień.
4. **Elewacje:** ceramika lub kamień (trwałość ponad 50 lat – mniej wymian B4), mocowania nierdzewne, mineralna izolacja (A1). Aluminium z wysokim udziałem recyklingu. Unikać kosztownego węglowo szkła kurtynowego w pierzejach – zgodne z wytycznymi konserwatorskimi.
5. **Obieg zamknięty:** projekt pod demontaż (ISO 20887), ≥ 70% odpadów budowlanych do odzysku (taksonomia), ponowne wykorzystanie gruntu z wykopu (M.05: piaski nadają się po doziarnieniu), paszport materiałowy w BIM.
6. **Obliczenie GWP:** narzędzie zgodne z EN 15978 i Level(s), dane EPD (krajowe bazy, np. ITB); zakres i moduły wg rozp. (UE) 2026/52. Na planszy: wykres „upfront vs operacyjne w 50 latach” i porównanie z benchmarkiem.

**Szacunek rzędu wielkości (wniosek):**
- PC ≈ 20 000 m² × 575–600 kg = **≈ 11,5–12 tys. t CO₂e A1–A5**, wobec ≈ 15–18 tys. t w wariancie zwykłym (750–900 kg/m²). Oszczędność ≈ 3–6 tys. t.
- Emisje operacyjne w 50 lat przy stałym EF: ≈ 230 t/rok × 50 ≈ 11–12 tys. t (górna granica; w rzeczywistości mniej, bo sieć się dekarbonizuje).

→ **Węgiel wbudowany to ok. połowa śladu w cyklu życia. Dlatego konstrukcja i podziemie są równie ważne jak instalacje.**

---

## 8. Certyfikacja (rekomendacja)
- **Deklaracja w pracy:** „Standard budynku bezemisyjnego (EPBD 2024/1275 art. 11) + raportowanie wskaźników Level(s) (1.1, 1.2, 3.1, 4.1, 6.1) + projekt przygotowany do certyfikacji BREEAM International New Construction na poziomie Excellent”.
- Bez zobowiązania do konkretnego certyfikatu (decyzja i koszt Zamawiającego).
- „Zielony Dom” PLGBC nie dotyczy (system dla mieszkaniówki).
- LEED v5 i DGNB – alternatywy (`zero_emisja.md` rozdz. 10).

---

## 9. Schemat pro-ekologiczny na planszy (Regulamin, Etap II, część graficzna lit. h) – zawartość

**Forma (wniosek):** jeden główny **przekrój perspektywiczny lub aksonometryczny „z wycięciem”** przez dominantę, dziedziniec i skrzydło (N–S) – czytelny z 2–3 m przy makiecie, w spójnej palecie planszy. Wokół 3–4 małe diagramy i pasek KPI. Liczby identyczne z częścią opisową i F.14.B (jedno źródło: `_bilans_energii.py`).

### 9.1. Warstwy przekroju (legenda z numerami)
1. **Słońce i osłony:** kąty słońca w południe dla Wrocławia (φ = 51,1°N): **21.06 – 62,3°**, **równonoc – 38,9°**, **21.12 – 15,5°** (wniosek – arytmetyka: 90° − φ ± 23,44°). Zewnętrzne lamele (lato: odcięcie, zima: zyski), światło dzienne w głąb pokoi.
2. **PV/BIPV:** dach biosolarny (340 kWp) i pasy BIPV od dziedzińca (60 kWp). Etykieta „0,40 MWp · ≈ 333 MWh/rok · 112% potrzeb EPB”.
3. **Zielone dachy i retencja:** ψ 0,30, krople spływające do zbiornika, ogród deszczowy w dziedzińcu, przelew do sieci.
4. **Woda szara:** pętla umywalki → MBR + UV → WC; woda deszczowa → zbiornik → WC i podlewanie. Etykieta „−42% wody z sieci”.
5. **Wentylacja:** centrale w piętrze technicznym, odzysk ≥ 80%, CO₂-DCV, przewietrzanie od dziedzińca, wentylacja wyporowa w sali Sejmiku.
6. **TABS i masa:** strzałki ciepła w stropach, nocne schładzanie.
7. **Grunt:** **75 sond × 99 m** pod płytą (rysunek w skali głębokości – efekt wizualny „korzeni” budynku). Opis: „magazyn sezonowy BTES: lato ładuje ciepłem z chłodzenia, zima oddaje”. Woda gruntowa 3,2–3,8 m p.p.t.
8. **Maszynownia PC + bufory + dry-cooler** (piętro techniczne), serwerownia → odzysk ciepła.
9. **BESS + odbiory krytyczne + MDS** (tryb wyspowy), agregat HVO (mała ikona „tylko awaria”).
10. **Sieć ciepłownicza – rezerwa** (przerywana linia „tylko szczyt/awaria”).
11. **Mobilność:** garaż z ładowarkami (≥ 52), rowerownia 50 + stojaki gości, przystanki tramwajowe i trasy rowerowe (most Grunwaldzki).
12. **Bioróżnorodność:** zachowane drzewa, budki dla jerzyków i nietoperzy na elewacji dziedzińcowej, łąka ekstensywna na dachu.

### 9.2. Diagramy pomocnicze
- **A. Trzy pory roku** (mini-przekroje): zima (grzanie z gruntu, PV niska, rezerwa sieci); lato (free-cooling z gruntu, ładowanie BTES, nadwyżka PV do BESS i EV); okres przejściowy (przewietrzanie, odzysk ciepła z chłodzenia).
- **B. Wykres Sankeya lub słupek bilansu:** zapotrzebowanie (EPB ≈ 300 / nieregulowane ≈ 350 MWh) a źródła (PV 333; sieć z kontraktem OZE ≈ 380; eksport 67); osobno ciepło z gruntu ≈ 243 MWh i odzysk z serwerowni ≈ 88 MWh.
- **C. Wykres EP:** EP projektu ≈ 30 wobec EPZEB 85 i EPmax 95 kWh/(m²·rok).
- **D. Węgiel w cyklu życia:** słupki A1–A5 (cel ≤ 600 kg CO₂e/m²) obok benchmarków (GLA 950 / 600; NZCBS 2030 550) oraz emisje operacyjne w 50 latach.
- **E. Cykl wody:** pętla z liczbami (m³/rok).

### 9.3. Pasek KPI (6–8 ikon, duże liczby)
„0 spalania” · „EP ≈ 30 (−65% vs WT)” · „0,40 MWp PV” · „75 × 99 m geotermii” · „−42% wody z sieci” · „ψ 0,48 – retencja” · „≥ 52 ładowarki EV” · „≤ 600 kg CO₂e/m² (A1–A5)”.

### 9.4. Zasady graficzne
- Jedna paleta zgodna z planszami: ciepło – ciepły odcień, chłód – chłodny, woda – niebieski, energia elektryczna – akcent.
- Cienkie linie i strzałki przepływów, bez „infografikowego” kiczu.
- Liczby zaokrąglone i konsekwentne.
- Opisy po polsku (plansze konkursowe), jednostki SI.

---

## 10. Tekst wzorcowy do części opisowej (ok. 300 słów; do redakcji)

> **Rozwiązania proekologiczne i energooszczędne.** Budynek zaprojektowano w standardzie budynku bezemisyjnego w rozumieniu art. 2 pkt 2 i art. 11 dyrektywy (UE) 2024/1275, wymaganym dla nowych budynków będących własnością instytucji publicznych od 1 stycznia 2028 r., z uwzględnieniem wytycznych Załącznika M.12. Kolejność rozwiązań wynika z zasady „najpierw efektywność”.
>
> Zwarta, kwartałowa bryła, przegrody o izolacyjności lepszej od wymagań warunków technicznych, zewnętrzne osłony przeciwsłoneczne, światło dzienne i masa termiczna stropów ograniczają potrzeby energetyczne. Ciepło i chłód zapewniają gruntowe pompy ciepła współpracujące z polem 75 sond o głębokości 99 m pod budynkiem. Pole pracuje jako sezonowy magazyn: latem przyjmuje ciepło z chłodzenia, zimą je oddaje. Niskotemperaturowe ogrzewanie i wysokotemperaturowe chłodzenie pozwalają na długie okresy free-coolingu. Ciepło serwerowni i chłodzenia przygotowuje ciepłą wodę. Miejska sieć ciepłownicza pełni wyłącznie rolę rezerwy. W budynku nie ma żadnych źródeł spalania paliw kopalnych.
>
> Fotowoltaika o mocy ok. 0,40 MWp, zintegrowana z dachami biosolarnymi i przegrodami od dziedzińca, wytwarza ok. 330 MWh rocznie. To więcej niż roczne zapotrzebowanie budynku na ogrzewanie, chłodzenie, wentylację, ciepłą wodę i oświetlenie. Szacowany wskaźnik EP wynosi ok. 30 kWh/(m²·rok), wobec 95 dopuszczalnych według warunków technicznych z 2002 r. i 85 przewidzianych w projekcie nowych warunków technicznych dla budynków bezemisyjnych. <!-- poprawione przez weryfikatora: WT 2002 nie obowiązują od 20.09.2026, stosowane fakultatywnie (art. 102a Pb) --> Magazyn energii elektrycznej i automatyka klasy A umożliwiają pracę wyspową odbiorów krytycznych i elastyczność wobec sieci.
>
> Rozdział kanalizacji na ścieki szare i czarne, oczyszczanie wody szarej oraz zbiornik wody deszczowej pokrywają spłukiwanie toalet i podlewanie zieleni, ograniczając pobór wody z sieci o ok. 40%. Zielone dachy, ogród deszczowy i zbiornik retencyjny zatrzymują opad w miejscu. Konstrukcję optymalizowano pod kątem śladu węglowego w cyklu życia (cel ≤ 600 kg CO₂e/m² w etapach A1–A5, obliczenie wg EN 15978 i Level(s)).

---

## 11. Ryzyka i kroki weryfikacyjne (po konkursie / w Etapie II)

| # | Krok | Po co |
|---|---|---|
| 1 | Interpretacja MPZP § 6 pkt 13 dla BIPV i PV jako pokrycia (Miasto, MPU) oraz opinia DWKZ | podstawa PV (R-01) |
| 2 | Klasyfikacja ogniowa BIPV na elewacjach (≤ 25 m: NRO; > 25 m: A1/A2) – rzeczoznawca ppoż. | wariant 0,50 MWp (R-02) |
| 3 | **TRT** na 1–2 otworach próbnych (≤ 100 m) i symulacja pola na 25 lat; zgłoszenie projektu robót geologicznych do Prezydenta Wrocławia | wymiarowanie BHE (M.12 pkt 1 A) |
| 4 | Warunki przyłączenia od Fortum (moc rezerwowa, taryfa) i audyt z art. 7b ust. 3c Prawa energetycznego | rezerwa sieci; formalności |
| 5 | Warunki MPWiK (odpływ dopuszczalny, koncepcja GWO wg RW25) | wymiarowanie retencji |
| 6 | Symulacja dynamiczna (EnergyPlus lub IDA ICE) z osłonami i TABS; analiza światła dziennego (PN-EN 17037) | potwierdzenie EP i chłodu |
| 7 | LCA (EN 15978, Level(s) 1.2, rozp. 2026/52) dla 2–3 wariantów konstrukcji (żelbet niskoemisyjny / hybryda TCC lub CLT) | cel ≤ 600 kg CO₂e/m² |
| 8 | Weryfikacja kosztów (kosztorysant) dla pozycji F.14.B | kryterium drugorzędowe |
| 9 | Śledzenie transpozycji EPBD (UC82, nowe WT, UC121) przed PnB | zgodność prawna |
| 10 | <!-- poprawione przez weryfikatora --> Decyzja o podstawie WT: wniosek o PnB z oświadczeniem z art. 102a Pb (WT 2002) tylko do ok. 19.03.2028; później – nowe WT (jeśli zostaną wydane). Projektować tak, by spełnić **oba** zestawy wymagań (ZEB z projektu WT § 354–355) | ryzyko zmiany podstawy prawnej między konkursem a PnB |
| 11 | <!-- poprawione przez weryfikatora --> Ustalić t₀ oświetlenia (PN-EN 15193-1) dla stref biurowych i sali obrad: wpływa na EPmax (95 albo 120) i na próg ZEB | poprawny benchmark EP na planszy |
