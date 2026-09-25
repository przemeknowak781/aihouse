# Rejestr wymagań prawnych i normowych — „Dom LAMELA” (skonsolidowany)

Wersja 1.0 · 2026-09-25 · stan prawny: Dz.U. 2026 do poz. 1244 (23.09.2026), katalog PKN 24–25.09.2026.
Źródła: rejestry domenowe `R1…R8` w tym katalogu **po weryfikacji niezależnej** (poprawki z sekcji „Weryfikacja niezależna” mają pierwszeństwo) oraz brief `docs/00_brief_projektowy.md` (sekcja 1.2 — interpretacja v2).
Wartości liczbowe do skryptów: `wymagania.yaml` (ten katalog). Identyfikatory `W-xxx` są wspólne dla obu plików.

**Oznaczenia statusu** (w tabelach):
* bez oznaczenia — wymaganie zweryfikowane na źródle pierwotnym (tekst aktu, katalog PKN);
* **[NZW]** — wartość niezweryfikowana (treść normy płatnej, źródło wtórne) — potwierdzić przed wydaniem PT;
* **[INT]** — interpretacja przepisu przyjęta w projekcie;
* **[ZAŁ]** — założenie lub cel projektowy (nie przepis);
* **[PROG]** — wymaganie programowe Inwestora albo z fikcyjnego MPZP.

**Gdzie stosujemy:** PZT, PAB, PT-AR, PT-BO, PT-IS, PT-IE, OBL (obliczenia), OPIS (część opisowa), ZL (załączniki), WN (pakiet wniosku).

**Sposób sprawdzenia** (skrypty oznaczone * są do utworzenia; czytają `model/*.yaml` i `wymagania.yaml`):
* `AUD-WT` — `tools/audyt_wt.py`*: geometria budynku (wysokości, drzwi, schody, garaż, okna/podłoga, przesłanianie, kondygnacje);
* `AUD-PZT` — `tools/audyt_pzt.py`*: odległości od granic i linii zabudowy, wskaźniki MPZP, miejsca postojowe, rzędne, spadki;
* `AUD-RYS` — `tools/audyt_rysunkow.py`*: metryki, skale, legendy, nazwy plików, PDF wektorowy ≤ 150 MB, dokładność zapisu, znaczniki danych (sekcja E);
* `SUN` — analiza nasłonecznienia `src/lamela/sun.py`;
* `OBL-FIZ` — U, ψ, f_Rsi, g, akustyka przegród; `OBL-EP` — charakterystyka energetyczna; `OBL-IS` — obciążenie cieplne, wentylacja, woda, kanalizacja, retencja, hałas PC; `OBL-IE` — bilans mocy, ΔU, Z_s, CRL, ryzyko piorunowe; `OBL-KON` — statyka i geotechnika;
* `KR` — kontrola ręczna rysunku/opisu wg listy; `DOK` — kontrola kompletności dokumentów (sekcje C i E).

---

## A. Stan prawny i podstawa projektu

### A.1 Podstawa techniczno-budowlana — decyzja

1. **WT z 2002 r. utraciły moc** z mocy art. 66 ustawy o dostępności (84 miesiące od 20.09.2019); ELI: „uznany za uchylony”, 21.09.2026. **Nowych WT dla budynków nie wydano** (Dz.U. do poz. 1244; projekt MFiG, wykaz nr 29, TRIS 2026/0422/PL — niepodpisany, nie powoływać). [R1-01, R3 S-01, S-02]
2. **Wariant przyjęty (A):** Inwestor składa organowi **oświadczenie z art. 102a ust. 1 PB** (Dz.U. 2026 poz. 1161, w mocy od 02.09.2026). Wtedy PZT, PAB **i PT** (ust. 2) sporządza się według **WT (t.j. Dz.U. 2022 poz. 1225, zm. Dz.U. 2023 poz. 2442 w brzmieniu Dz.U. 2024 poz. 474, Dz.U. 2024 poz. 726) w brzmieniu obowiązującym do 19.09.2026**, a WT stosuje się do decyzji dotyczących całego zamierzenia (ust. 4). Treść WT nie zmieniła się od 15.08.2024, więc rozbieżność dat 19/20/21.09.2026 nie ma wpływu na treść.
3. Wniosek z oświadczeniem — **najpóźniej 19.03.2028** (18 miesięcy od 20.09.2026; PIIB podaje 20.03.2028 — przyjęto datę bezpieczną).
4. Formuła w opisach: „§ … rozporządzenia MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowanego na podstawie art. 102a ust. 1 i 2 ustawy – Prawo budowlane (Dz.U. 2026 poz. 524 ze zm.) w związku z oświadczeniem Inwestora z dnia [DO UZUPEŁNIENIA]”. Nie piszemy, że WT „obowiązują”. [R1 3.2, R3 1.1 pkt 7]
5. Normy powołane w zał. 1 WT jako **datowane** stosuje się w powołanym wydaniu (także wycofane), obok nich aktualne wydania jako zasady wiedzy technicznej (art. 5 ust. 1 PB); projekt ma spełniać oba. [R6 3.1, R7 1]

**Decyzje proceduralne** (z wartościami):
* Tryb: **wniosek o pozwolenie na budowę** (PB-1) do starosty (art. 28 ust. 1, art. 29 ust. 5, art. 82 ust. 2 PB); decyzja w **65 dni** (art. 35 ust. 6 pkt 1). Obszar oddziaływania w całości na działce ⇒ stroną tylko Inwestor (art. 28 ust. 2; zrzeczenie się odwołania art. 127a KPA). [R1-05, R1-07, R1-08]
* **Kategoria obiektu I** — budynki mieszkalne jednorodzinne (zał. do PB) — na wszystkich stronach tytułowych. [R1-33]
* Projekt **bez odstępstw** (art. 9 PB). Istotne odstąpienie wymagające zmiany PnB m.in.: pow. zabudowy > 5 %, wysokość/długość/szerokość > 2 %, liczba kondygnacji (art. 36a ust. 5). PnB wygasa po **3 latach** bez rozpoczęcia budowy (art. 37 ust. 1). [R1-42, R1-48]
* **Uprawnienia bez ograniczeń** we wszystkich branżach: kubatura prawdopodobnie > 1000 m³; limity ograniczonych uprawnień konstrukcyjnych: ≤ 1000 m³, ≤ 12 m, ≤ 3 kondygnacje, kondygnacja ≤ 4,8 m, posadowienie ≤ 3 m, rozpiętość ≤ 6 m, **wspornik ≤ 2 m** (art. 15a ust. 3, 5, 21, 23 PB). Od 02.10.2026 osoba zawieszona w izbie nie pełni funkcji (art. 12 ust. 7b) — sprawdzać e-CRUB. [R1-30, R1-32]
* **Sprawdzający** ustawowo niewymagany (art. 20 ust. 3 pkt 2 PB); rekomendacja: dobrowolne sprawdzenie PT-BO. [R1-27]
* **Informacja BIOZ** w projekcie; **plan BIOZ wymagany** (roboty na wysokości > 5,0 m; wykopy pionowe > 1,5 m bez rozparcia; dźwig) — sporządza kierownik budowy (art. 21a PB; rozp. BIOZ §6). [R1-25, R1-26]
* PT **nie jest składany** z wnioskiem; przekazywany kierownikowi budowy przed rozpoczęciem robót (art. 34 ust. 4, art. 42 ust. 1 PB). [R1-15]

### A.2 Akty prawne (status na 25.09.2026)

| Akt | Dz.U. (t.j. / zmiany) | Status | Zastosowanie w projekcie |
|---|---|---|---|
| Prawo budowlane (PB) | t.j. 2026 poz. 524; zm. 2026 poz. 605, 646, **1161**; nowelizacja 2025 poz. 1847 | obowiązuje; art. 102a–102c od 02.09.2026; art. 12 ust. 7b od 02.10.2026; definicje art. 3 pkt 2b–2g, 24–27 od 20.09.2026; **art. 56 ust. 1a uchylony** | procedura, zawartość projektu, PV (art. 29 ust. 4 pkt 3 lit. c) |
| WT — warunki techniczne budynków (MI 12.04.2002) | 2002 nr 75 poz. 690; t.j. 2022 poz. 1225; zm. 2023 poz. 2442 (termin 2024 poz. 474 → 01.08.2024), 2024 poz. 726 (od 15.08.2024) | **„uznany za uchylony” (ELI 21.09.2026)** — stosowany na podstawie art. 102a PB | wymagania techniczne (sekcja B) |
| WT użytkowania budynków mieszkalnych (MSWiA 16.08.1999) | 1999 nr 74 poz. 836 | uznany za uchylony; art. 102c PB (18 mies.) | poza projektem |
| Ustawa o zapewnianiu dostępności (art. 66) | t.j. 2024 poz. 1411 (art. 66 wg 2024 poz. 1081) | obowiązuje | podstawa wygaśnięcia WT |
| Rozp. w sprawie szczegółowego zakresu i formy projektu budowlanego (RPB) | 2020 poz. 1609; t.j. 2022 poz. 1679; zm. 2023 poz. 2405 (od 01.04.2024; §23 pkt 4a od 01.08.2024 wg 2024 poz. 473), 2026 poz. 597 (od 19.05.2026; **§15 ust. 3 i §20 ust. 1 pkt 8 od 05.11.2026**) | obowiązuje (nie wygasł razem z WT) | zakres i forma (sekcja C, B.16) |
| Wzór PB-1 (wniosek o PnB) | 2026 poz. 255 (od 04.03.2026; uchylił 2021 poz. 410) | obowiązuje | WN |
| Wzór PB-5 (prawo do dysponowania nieruchomością) | 2021 poz. 1170 | obowiązuje | WN |
| Wzory: rozpoczęcie robót / zakończenie budowy / odrębne zatwierdzenie / zmiana PnB / zgłoszenie | 2026 poz. 254 / 272 / 223 / 242 / 282 | obowiązują | etap realizacji |
| Rozp. BIOZ (MI 23.06.2003) | 2003 nr 120 poz. 1126 | obowiązuje | ZL |
| Rozp. geotechniczne warunki posadawiania (MTBiGM 25.04.2012) | 2012 poz. 463 | obowiązuje | PAB, PT-BO |
| Rozp. standardy geodezyjne / BDOT500 i mapa zasadnicza / PSOP | t.j. 2022 poz. 1670 / 2021 poz. 1385 / t.j. 2024 poz. 342 zm. 2025 poz. 106 | obowiązują | mapa do celów projektowych |
| Prawo geodezyjne i kartograficzne | t.j. 2024 poz. 1151 ze zm. | obowiązuje | art. 2 pkt 7a, 12b, 28b |
| Ustawa o planowaniu i zagospodarowaniu przestrzennym (upzp) | t.j. 2026 poz. 538; zm. 781, 864, 912; reforma 2023 poz. 1688 (art. 65, 67) | obowiązuje | definicje wskaźników art. 2 pkt 28–35 |
| Rozp. w sprawie projektu MPZP (MFiG 07.09.2026) | 2026 poz. 1192 (od 24.09.2026; uchylił 2021 poz. 2404) | obowiązuje | tylko sporządzanie planów |
| Ustawa o drogach publicznych / rozp. techniczne dróg | t.j. 2025 poz. 889 (zm. 2026 poz. 815, 982 — bez wpływu na art. 29, 39, 40, 43) / 2022 poz. 1518 zm. 2025 poz. 1352 | obowiązują | zjazd, art. 43 |
| Ustawa o ochronie przyrody | t.j. 2026 poz. 13 ze zm. | obowiązuje | drzewa (art. 83f) |
| POŚ / rozp. hałas w środowisku / rozp. instalacje wymagające zgłoszenia | t.j. 2025 poz. 647 / t.j. 2014 poz. 112 / t.j. 2019 poz. 1510 | obowiązują | hałas PC |
| Prawo wodne | t.j. 2025 poz. 960 ze zm. (2025 poz. 1535; 2026 poz. 445, 605, 815, 1033, 1156) | obowiązuje | wody opadowe, rozsączanie |
| Ustawa o ochronie gruntów rolnych i leśnych | t.j. 2024 poz. 82 ze zm. | obowiązuje | wyłączenie z produkcji |
| Rozp. RM — przedsięwzięcia mogące znacząco oddziaływać | 2019 poz. 1839 ze zm. (2022/1071, 2023/1724, 2026/706, 2026/1185) | obowiązuje | DŚU — nie dotyczy |
| Ustawa o charakterystyce energetycznej budynków / metodologia | t.j. 2024 poz. 101 / 2015 poz. 376 zm. 2017 poz. 22, 2019 poz. 1829, **2023 poz. 697** | obowiązują (nie wygasły z WT) | EP, świadectwo |
| Prawo energetyczne / OZE / rozp. systemowe (RSys) | t.j. 2026 poz. 43 (zm. 516, 607, 900) / t.j. 2026 poz. 68 / t.j. 2025 poz. 919 zm. 2026 poz. 668 | obowiązują | sieć ciepłownicza (art. 7b), przyłącze nN, mikroinstalacja |
| Rozp. MSWiA ochrona ppoż. budynków (ROPoż) | t.j. 2023 poz. 822, zm. 2024 poz. 1716 | obowiązuje | czujki dymu (§28a), PWP (§4 ust. 2 pkt 2) |
| Rozp. woda ppoż. i drogi pożarowe / rozp. uzgadnianie projektu ppoż. | 2009 nr 124 poz. 1030 / 2023 poz. 1563 | obowiązują | dane ppoż. |
| Ustawa o elektromobilności | t.j. 2026 poz. 1243 | obowiązuje | EV — brak obowiązku |
| Zbiorowe zaopatrzenie w wodę + ustawa o PIS (nowelizacja) | 2026 poz. 605 | obowiązuje | art. 4i nie dotyczy; wyroby (rozdz. 3b PIS) |
| Opłata skarbowa / KPA / normalizacja / ochrona ludności | t.j. 2025 poz. 1154 ze zm. / t.j. 2025 poz. 1691 / 2015 poz. 1483 / 2024 poz. 1907 zm. 2026 poz. 646 | obowiązują | zwolnienie PnB; 17 zł pełnomocnictwo; PN dobrowolne; ochrona ludności — nie dotyczy |
| UE: 305/2011; 2024/573 (F-gazy); 813/2013 (ekoprojekt PC); 1253/2014 (centrale); 2016/631 (NC RfG); **2024/1309 (GIA, art. 10 od 12.02.2026)**; 2024/1275 (EPBD) | Dz.Urz. UE | obowiązują; EPBD **nietransponowana** (termin 29.05.2026) | PC, wentylacja, PV, światłowód, EV |

### A.3 Normy (status PKN 24–25.09.2026)

Wycofanie normy nie zakazuje jej stosowania (stanowisko PKN); normy datowane z zał. 1 WT stosuje się w powołanym wydaniu. **WYCOF.** = wycofana.

| Norma | Status | Zastępcza / uwaga | Rola |
|---|---|---|---|
| **Rysunek — zał. 2 RPB** („najnowsza norma opublikowana w języku polskim”) | | | |
| PN-EN ISO 4157-1, -2, -3:2001 | aktualne | — | oznaczenia budynków, pomieszczeń |
| PN-EN ISO 6284:2001 (pol.) | **WYCOF.** 2024-06-28 | PN-EN ISO 6284:2024-06 (ang.) — D-10 | odchyłki |
| PN-EN ISO 11091:2001; PN-B-01025:2004; PN-B-01027:2002; PN-B-01029:2000 | aktualne | — | PZT, oznaczenia, wymiarowanie |
| PN-EN ISO 5261:2002; PN-EN ISO 2553:2019-06; PN-EN ISO 5845-1:2002 | aktualne | — | stal, spoiny, złącza |
| PN-ISO 9836:2022-07 | aktualna | zastąpiła **WYCOF.** PN-ISO 9836:2015-12 | powierzchnie, kubatura (§12 RPB) |
| **Rysunek — pozostałe** | | | |
| PN-B-01030:2000; PN-B-01040:1994; PN-EN ISO 3766:2006 | aktualne | 3766 zastąpiła **WYCOF.** PN-EN ISO 4066:2001 | materiały, konstrukcja, zbrojenie |
| PN-EN ISO 5457:2002 (+A1:2010); 7200:2007; 9431:2011; 5455:1998; 3098-2…-6:2002 | aktualne | — | arkusz, tabliczka, podziałki, pismo |
| PN-EN ISO 128-2:2023-05 (ang.) | aktualna | zastąpiła **WYCOF.** PN-EN ISO 128-20/-21, PN-ISO 128-22/-23/-24 | linie |
| PN-EN ISO 128-3:2023-02 (ang.) | aktualna | zastąpiła **WYCOF.** PN-ISO 128-30/-34/-40/-44/-50 | przekroje, kreskowanie |
| PN-EN ISO 3098-1:2015-06 (ang.) | aktualna | zastąpiła **WYCOF.** PN-EN ISO 3098-0 | pismo |
| PN-EN ISO 7519:2024-09 | **WYCOF.** 2026-04-16 | brak następcy PN (ISO 7519:2025) | dobra praktyka |
| PN-EN 60617-11:2004; PN-B-01701:1984; PN-B-01410:1989; PN-B-01440:1998 | **WYCOF.** bez następcy | symbole tylko z legendą (baza IEC 60617) | symbole instalacji |
| PN-EN 12792:2006; PN-B-01700:1999; PN-EN 1861:2001; PN-EN ISO 6412-1…-3:2018 | aktualne | — | wentylacja, sieci wod-kan, PC, rurociągi |
| PN-70/B-02365; PN-N-01603:1986; PN-ISO 4068:1998 | **WYCOF.** | PN-ISO 9836 / praktyka | — |
| **Konstrukcja i geotechnika** | | | |
| Eurokody 1. gen.: PN-EN 1990:2004+A1/NA:2010; 1991-1-1/NA:2010; 1991-1-3/NA:2010 (+Ap1); 1991-1-4/NA:2010; 1991-1-7/NA:2015-02; 1992-1-1:2008/NA:2018-11; 1993-1-1/NA:2010; 1996-1-1+A1:2013-05/NA:2014-03 (+Ap2:2014-09); 1997-1:2008/NA:2011 (+Ap2:2010); 1997-2:2009 | aktualne | 2. gen. do 30.09.2027, 1. gen. wycofywana do 31.03.2028; **nie mieszać** (PN-EN 1992-1-1:2024-05 ang. — nie stosować) | PT-BO |
| PN-EN 206+A2:2021-08; PN-B-06265:2022-08 (+Az1:2025-08) | **WYCOF.** | PN-EN 206-1:2026-09, PN-EN 206-2:2026-09 (ang.) — D-09 | beton |
| PN-H-93220:2018-02 (+Ap1:2018-04) | aktualna | — | B500SP |
| PN-EN 1090-2+A1:2024-10 | aktualna | zastąpiła **WYCOF.** 1090-2:2018-09 | stal |
| PN-B-03020:1981 | **WYCOF.** 31.03.2010 | PN-EN 1997-1; mapa h_z stosowana jako wiedza techniczna | przemarzanie |
| PN-B-10725:1997; PN-B-10736:1999 | **WYCOF.** | brak; warunki gestora | przykrycie przewodów |
| PN-EN ISO 13793:2002; PN-B-02171:2017-06 | aktualne | — | płyta fundamentowa; drgania |
| **Fizyka budowli, energia, ogrzewanie** | | | |
| PN-EN ISO 6946:2017-10; 13370:2017-09; 10077-1/-2:2017-10; 10211:2017-09; 14683:2017-09; 13788:2013-05; 13789:2017-10; 52016-1:2017-09 | aktualne | 52016-1 zastąpiła **WYCOF.** PN-EN ISO 13790 | U, ψ, f_Rsi |
| PN-EN 12831:2006 | **WYCOF.** (powołana w WT) | PN-EN 12831-1:2017-08 (ang., bez NA) | obciążenie cieplne |
| PN-B-02403:1982 | **WYCOF.** (powołana w WT) | brak | θ_e |
| PN-EN 12207:2001; PN-EN 13829:2002 | **WYCOF.** (powołane w WT) | PN-EN 12207:2017-01 (ang.); PN-EN ISO 9972:2015-10 (ang.) | szczelność |
| PN-EN 14825:2022-11; 16147+A1:2023-06; 12102-1:2022-12; 13141-7+A1:2026-05; 13141-8:2023-02; PN-EN 16798-1:2019-06 | aktualne | 16798-1 zastąpiła PN-EN 15251 | deklaracje wyrobów, klimat wewn. |
| PN-EN 378-1+A1:2021-03; PN-EN IEC 60335-2-40:2025-02 | aktualne (ang.) | — | R290 |
| **Wentylacja, woda, kanalizacja** | | | |
| PN-B-03430:1983/Az3:2000 | **WYCOF.** bez zastępstwa — **wiąże przez WT** | — | strumienie powietrza |
| PN-EN 779 | **WYCOF.** | PN-EN ISO 16890-1:2017-01 | filtry |
| PN-B-01706:1992; PN-B-01707:1992; PN-B-10720:1998; PN-B-02440:1976; PN-B-02414:1999 | **WYCOF.** (powołane w WT) | kontrolnie PN-EN 806-1…-5 (aktualne) | woda, c.w.u. |
| PN-EN 1717:2003 | **WYCOF.** (powołana w WT) | PN-EN 1717+A1:2026-09 (ang.) | przepływ zwrotny |
| PN-EN 12056-1…-5:2002; 12109:2003; 12380:2005; 13564-1:2004; 752:2017-06; 1610:2015-10; 1401-1+A1:2023-09; 16941-1:2024-08 | aktualne | — | kanalizacja, deszczówka |
| DWA-A 138:2005 (niemiecka, nie PN) | zastąpiona | DWA-A 138-1 (10/2024) | rozsączanie |
| **Akustyka** | | | |
| PN-B-02151-2:2018-01; PN-B-02151-3:2015-10 (+Ap1:2016-02) | aktualne | — | §326 WT |
| **Elektryka, odgromowa, teletechnika** | | | |
| PN-HD 60364-4-41:2009 | **WYCOF.** (w WT) | PN-HD 60364-4-41:2017-09 (RCD na oświetleniu) | ochrona przeciwporażeniowa |
| PN-HD 60364-4-43:2012; -5-534:2012 i 2016-04; -6:2008; -7-701:2010 | **WYCOF.** (w WT) | -4-43:2024-04; **-5-53:2022-10**; -6:2016-07; -7-701:2025-02 (ang.) | — |
| PN-HD 60364-1:2010; -4-42:2011; -4-443:2016-03; -4-444:2012; -5-51:2011; -5-52:2011; -5-54:2011; -5-559:2012; -5-56:2019-01; -7-712:2016-05; -7-714:2012; -7-722:2019-01; -8-1:2019-07; PN-HD 308 S2:2007 | aktualne | — | PT-IE |
| PN-EN 62305-1…-4 (2008/2011/2012) | **WYCOF.** (w WT) | PN-EN IEC 62305-1…-4:2025-09 (ang.) | LPS, analiza ryzyka |
| PN-EN 60445:2010 | **WYCOF.** | PN-EN IEC 60445:2022-04 | oznaczenia żył |
| PN-EN IEC 61643-11:2026-04; 62606:2014-05; 62423:2013-06; 14604:2006; 50291-1:2018-06; 50618:2015-03; 62446-1:2016-08; 50549-1:2019-02; 50173-4:2018-07; 50174-2:2018-08; 50310:2016-09; IEC 61851-1:2019-10; IEC 61439-3:2025-09; 61082-1:2015-03; IEC 81346-1:2023-01 | aktualne | 61643-11 zastąpiła wyd. 2013 | wyroby, dokumentacja |
| N SEP-E-002 (norma SEP, nie PN) | dobrowolna | — | planowanie instalacji |

### A.4 Korekty briefu i rozstrzygnięte sprzeczności

Korekty briefu (wartość z rejestru ma pierwszeństwo):

| # | Brief | Jest (rejestr) | Źródło |
|---|---|---|---|
| K-1 | I kategoria geotechniczna | **II kategoria** (3 kondygnacje, schemat statycznie niewyznaczalny) | R1-39, R2 A-G, R5-81 |
| K-2 | PV — art. 56 ust. 1a PB | art. 56 ust. 1a **uchylony**; podstawa: **art. 29 ust. 4 pkt 3 lit. c PB** | R1-34, R6-77, R7-I01 |
| K-3 | „ograniczenie A0max” | A0max **nie obowiązuje** od 01.01.2018; pozostaje g ≤ 0,35 | R3 E-13 |
| K-4 | pokój ≥ 8 m², dzienny ≥ 16 m² | nie są wymaganiami WT — program Inwestora | R3 B-19 |
| K-5 | balustrady balkonów/tarasów 1,10 m | dom jednorodzinny: **≥ 0,90 m**, prześwit nieregulowany | R3 K-10 |
| K-6 | wentylacja z odzyskiem (jako wymóg) | odzysk obowiązkowy dopiero ≥ 500 m³/h; tu wynika z EP i decyzji | R3 IV-08, R6-41 |
| K-7 | klasa odporności pożarowej wg §212–213 | **zwolnienie** z §212 i §216 (§213 pkt 1 lit. a) | R3 P-02, R5-100 |
| K-8 | „WT 2021”, rzędne z 2 miejscami | WT t.j. 2022 poz. 1225 ze zm. (art. 102a); rzędne arch. **3 miejsca**, PZT 2 | R3, R4-G01 |
| K-9 | śnieg | brief już poprawiony: strefa 2, s_k = 0,9 kN/m² | R5-30 |
| K-10 | pomocnicze ≥ 2,20 m | czasowy pobyt 2,20; techniczne i gospodarcze **2,00**; łazienki 2,20 tylko przy wentylacji mechanicznej | R3 B-10, B-13, B-21 |

Sprzeczności między rejestrami (wybrano wartość zweryfikowaną lub bezpieczniejszą):

| # | Sprzeczność | Rozstrzygnięcie |
|---|---|---|
| S-1 | c.w.u.: R6 — „dezynfekcja termiczna 70–80 °C” jako wymóg; R3 (poprawka weryfikacji) — wymagana **możliwość** dezynfekcji chemicznej lub fizycznej, 70–80 °C tylko przy metodzie cieplnej | brzmienie R3 (weryfikacja §120 ust. 2a); w projekcie wybrano metodę cieplną ⇒ 70–80 °C (W-133) |
| S-2 | brzmienie WT: R6 (weryfikacja) „obowiązującym do 20.09.2026” vs art. 102a „do 19.09.2026” | formuła ustawowa (19.09.2026); treść identyczna |
| S-3 | cele U: R3 (ściana 0,17, podłoga 0,25) vs R6 (ściana 0,15, podłoga 0,20, ściana dom–garaż 0,25) | R6 (domena energii, surowsze; są to cele, nie przepis) |
| S-4 | rozsączanie od fundamentów: R6/Aquanet ≥ 1,5·h_f + 0,5 m (≈ 2,0 m) vs R8 ≥ 3,0 m (przy izolacji przeciwwodnej) | **3,0 m** (obie wartości nienormatywne; bezpieczniejsza) |
| S-5 | q_p wiatru 0,72 (R5 pierwotnie) vs 0,71 (weryfikacja, wzór NA.3) | **0,71 kN/m²** (0,72 dopuszczalne jako zaokrąglenie w górę) |
| S-6 | R4, R5, R7 opisują v1 (taras na płycie D, wiata na słupach) | brief v2: **brak tarasu nad garażem i wiaty**; dach garażu nieużytkowy (kat. H, dach zielony) |
| S-7 | R2/R3: płyty wysunięte 0,8–1,5 m | brief v2: 0,8–1,2 m; płyta dachu P0 na zachód ≈ 1,5 m |
| S-8 | PWP: R3 „wymagany przy > 1000 m³” vs R7 (zwolnienie ROPoż) | projektować PWP (spełnia obie interpretacje) — D-04 |
| S-9 | beton: R5 (tekst) PN-EN 206+A2 jako obowiązująca vs weryfikacja — wycofana | wg N-11 R5 — D-09 |
| S-10 | śnieg: R5 pierwotnie bez sytuacji wyjątkowej vs weryfikacja — B2 obowiązkowa | B2 obowiązkowa (W-264) |
| S-11 | koniec okresu art. 102a: 19.03 vs 20.03.2028 | 19.03.2028 |
| S-12 | numeracja: model P0/„0.01” vs PN-B-01025 (parter = 1) | model bez zmian; na rysunkach 1/2/3 i `1.01…` (W-314) |
| S-13 | PU: próg PN-ISO 9836 (1,90 m) vs RPB §20 (2,20/1,40 m) | do PU wg RPB (W-316) |

---

## B. Wymagania projektowe

Kolumna „Podstawa” podaje akt/normę z jednostką redakcyjną, a w nawiasie kwadratowym identyfikatory w rejestrach domenowych. „WT” = stosowane na podstawie art. 102a PB (A.1).

### B.1 Usytuowanie i działka

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-001 | Ściana z oknami lub drzwiami ≥ **4,00 m** od granicy działki; **każda płaszczyzna uskoku/załamania = odrębna ściana** (bryły „S”, wspornik A, boks C wymiarować osobno) | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726), zał. 1a [R3 U-01; R8-18] | PZT, PAB | AUD-PZT |
| W-002 | Ściana bez okien i drzwi ≥ **3,00 m** od granicy | WT §12 ust. 1 pkt 2 [R3 U-01] | PZT | AUD-PZT |
| W-003 | Ściana nierównoległa do granicy 3,00–4,00 m tylko przy krawędzi okna/drzwi ≥ 4,00 m — w projekcie nie korzystamy (ściany równoległe) | WT §12 ust. 1a [R3 U-02; R8-18] | PZT | KR |
| W-004 | Okap, gzyms, balkon, daszek nad wejściem, taras, schody zewnętrzne, rampa, pochylnia ≥ **1,50 m** od granicy; okno w dachu ≥ 4,00 m. Płyty wysunięte 0,8–1,2 m (płyta P0 na zachód ≈ 1,5 m) traktowane jak okapy/gzymsy [INT] | WT §12 ust. 6 pkt 1–2 [R3 U-04; R8-19] | PZT | AUD-PZT |
| W-005 | Od granicy z działką drogową (1KDD) odległości z §12 nie obowiązują — obowiązuje linia zabudowy (W-006) | WT §12 ust. 10 [R3 U-05] | PZT | KR |
| W-006 | Nieprzekraczalna linia zabudowy **6,00 m** od linii rozgraniczającej 1KDD; zalecenie: **żaden element** (płyty, daszek wejścia, schody) jej nie przekracza | MPZP 3MN; upzp art. 15 ust. 2 pkt 6 [R8-09, R8 3.1] [PROG] | PZT | AUD-PZT |
| W-007 | Obiekt ≥ **6,0 m** od zewnętrznej krawędzi jezdni drogi gminnej (teren zabudowy; poza nim 15 m) | u.d.p. art. 43 ust. 1 tab. lp. 3 lit. c [R8-44] | PZT | AUD-PZT |
| W-008 | Przesłanianie: w poziomym kącie **60°** od osi okna pomieszczenia na pobyt ludzi brak obiektu (także części własnego budynku, garażu) bliżej niż jego wysokość przesłaniania (mierzona od dolnej krawędzi najniższego okna) | WT §13 ust. 1–2 [R3 U-07; R8-20] | PZT, PAB | AUD-WT |
| W-009 | Nasłonecznienie pokoi ≥ **3 h** w dniach równonocy w godz. **7:00–17:00** (mieszkanie wielopokojowe: ≥ 1 pokój); sprawdzić też okna sąsiadów E/W (obszar oddziaływania) | WT §60 ust. 1–2 [R3 U-08; R8-21] | PAB, OPIS | SUN |
| W-010 | Odległość ścian budynków ZL–ZL ≥ **8,0 m** (+50 % / +100 % przy ścianie lub dachu rozprzestrzeniającym ogień); ściany i dach **NRO**; sąsiedzi ≥ 8 m od granic + LAMELA ≥ 4 m ⇒ ≥ 12 m; ryzyko §271 ust. 4–5 — D-03 | WT §271 ust. 1–2 [R3 P-09, P-10; R8-31] | PZT, PAB | AUD-PZT |
| W-011 | Od granicy działki niezabudowanej (S, teren rolny R) dom ze ścianami i dachem NRO sytuuje się jak w §12; odległości od lasu nie dotyczą | WT §272 ust. 2; §271 ust. 8–8a [R3 P-11, P-12] | PZT | KR |
| W-012 | Obszar oddziaływania **w całości na działce 123/4**; PZT wskazuje przepisy: WT §12, 13, 19, 23, 28–29, 60, 271; u.d.p. art. 43; POŚ art. 144 ust. 2 z Dz.U. 2014 poz. 112; PW art. 234; MPZP | PB art. 3 pkt 20, art. 20 ust. 1 pkt 1c, art. 34 ust. 3 pkt 1 lit. e; RPB §14 pkt 8, §18 [R1-09; R2 Z10; R8-46, R8 3.6] | PZT (opis) | KR |
| W-013 | Dojazd: jezdnia ≥ **3,00 m** (zalecane 5,0–6,0 m przed garażem); nawierzchnia dla pojazdów do 2,5 t | WT §14 ust. 1, §15 ust. 2 [R3 Z-01, Z-03; R8-22] | PZT | AUD-PZT |
| W-014 | Stanowisko postojowe **2,50 × 5,00 m**, nawierzchnia utwardzona lub gruntowa stabilizowana, ze spadkiem | WT §21 ust. 1 pkt 1, ust. 3 [R3 Z-08; R8-23] | PZT | AUD-PZT |
| W-015 | Miejsca gościnne: maks. **2 niezadaszone** przy budynku (zwolnienie z 7 m od okien); **≥ 3,00 m od granic E i W**; przy granicy z 1KDD odległość niewymagana | WT §19 ust. 1 pkt 1 lit. a, ust. 2 pkt 1 lit. a, ust. 5–7 [R3 Z-06, Z-07; R8-24] | PZT | AUD-PZT |
| W-016 | Miejsce na pojemniki do segregacji (osłona), utwardzone dojście do miejsca odbioru; odległości od okien i granic nieokreślone (zabudowa jednorodzinna) | WT §22 ust. 1–3, §23 ust. 4 [R3 Z-09, Z-10; R8-25] | PZT | KR |
| W-017 | Ogrodzenie bez ostrych zakończeń i drutu kolczastego poniżej **1,80 m**; brama i furtka nie otwierają się na zewnątrz działki (brama przesuwna); brama ≥ **2,40 m** (zalecane ≥ 4,0 m), furtka ≥ **0,90 m** w świetle | WT §41 ust. 1–2, §42 ust. 1, §43 [R3 Z-15…Z-17; R8-28] | PZT | AUD-PZT |
| W-018 | Wody opadowe na własny teren nieutwardzony, do dołów chłonnych lub zbiorników retencyjnych (budynek niski, brak sieci); zakaz zmiany spływu na działki sąsiednie i odprowadzania na drogę / do rowu | WT §28 ust. 2, §29; PW art. 234 ust. 1; u.d.p. art. 39 ust. 1 pkt 9; MPZP [R3 Z-12; R8-27, R8-58] | PZT, PT-IS | KR |
| W-019 | Teren ze spadkiem od budynku (≥ 2 % [ZAŁ]); na granicach E, W, S rzędne projektowane = istniejące; podjazd ze spadkiem ku działce, odwodnienie liniowe przed bramą | WT §316 ust. 2; PW art. 234; u.d.p. art. 39 [R3 Z-18; R8 3.5] | PZT | AUD-PZT |
| W-020 | Zjazd: decyzja zarządcy drogi o lokalizacji zjazdu (załącznik wniosku o PnB; wygasa po **3 latach** bez budowy); parametry wg decyzji (założenie: jezdnia zjazdu 5,00 m [ZAŁ]); poza koronami drzew przydrożnych | u.d.p. art. 29 ust. 1, 3, 3a, 5; art. 39 ust. 1 pkt 12; rozp. Dz.U. 2022 poz. 1518 §54–56 [R1-38; R8-42, R8-44b] | PZT, WN | DOK |
| W-021 | Możliwość przyłączenia do sieci wodociągowej, kanalizacyjnej, elektroenergetycznej; indywidualne źródło ciepła (PC) równorzędne z siecią ciepłowniczą | WT §26 ust. 1–2 [R3 Z-11; R8-26] | PZT, PAB | KR |
| W-022 | PZT na aktualnej **mapie do celów projektowych** (klauzula urzędowa albo oświadczenie geodety), 1:500, PL-2000 strefa 6 (18°E), PL-EVRF2007-NH; budynek ≤ 4 m od granicy (bez danych I grupy) ⇒ pomiar punktów granicznych — zalecane lica ścian ≥ **4,50 m** od granic E/W | PB art. 34 ust. 3 pkt 1, art. 34b; PGiK art. 2 pkt 7a, 12b; rozp. Dz.U. 2022 poz. 1670 §31–33 [R2 Z11; R8-32…R8-38] | PZT | DOK |
| W-023 | Drzewa: osoba fizyczna, cel niegospodarczy — bez zezwolenia, ale **zgłoszenie** przy obwodzie na wys. 5 cm > **80 / 65 / 50 cm** (oględziny 21 dni, sprzeciw 14 dni); prace przy drzewach zachowywanych w sposób najmniej szkodliwy | u.o.p. art. 83f ust. 1 pkt 3, 3a, ust. 4–8; art. 87a [R8-48…R8-50] | PZT | KR |
| W-024 | Hałas na granicy działek MN (E, W): L_Aeq,D ≤ **50 dB** (6:00–22:00), L_Aeq,N ≤ **40 dB** (22:00–6:00); cel ≤ **35 dB(A)** nocą [ZAŁ]; jednostka PC ≥ **6,0 m** od granicy E [ZAŁ], nie pod oknami sypialni | rozp. MŚ, t.j. Dz.U. 2014 poz. 112, tab. 1 lp. 2a; POŚ art. 112a, 144 ust. 2 [R3 H-11; R6-72, R6-73; R8-51…R8-53, R8 3.4] | PZT, PT-IS | OBL-IS |
| W-025 | Decyzja o wyłączeniu gruntów z produkcji rolnej tylko dla klas I–IIIb i IV–VI organicznych (przed PnB, załącznik wniosku); bez opłat do 0,05 ha. Założono RIVb/RV mineralne ⇒ nie dotyczy | u.o.g.r.l. art. 11 ust. 1, 4, 4a; art. 12a pkt 1 [R8-61, R8-62] | WN | DOK |
| W-026 | DŚU niewymagana (zabudowa mieszkaniowa w MPZP od 2/4 ha; garaże od 0,5/1,0 ha pow. użytkowej) — adnotacja w opisie | rozp. RM Dz.U. 2019 poz. 1839 §3 ust. 1 pkt 55 lit. a, pkt 58 [R8-63] | OPIS | KR |

### B.2 Wskaźniki MPZP (fikcyjny MPZP, uchwała XII/123/2024, teren 3MN; działka 1600,00 m²)

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-030 | Udział powierzchni zabudowy ≤ **30 %** ⇒ ≤ **480,00 m²**; rzut po zewnętrznym obrysie ścian zewnętrznych (wspornik A i boks C wliczone); wariant kontrolny z rzutem płyt wysuniętych (D-06) | MPZP; upzp art. 2 pkt 35; RPB §14 pkt 4 lit. a; PN-ISO 9836:2022-07 p. 5.1.2 [R8-06; R4-P03] [PROG] | PZT | AUD-PZT |
| W-031 | Pow. biologicznie czynna ≥ **50 %** ⇒ ≥ **800,00 m²**; bez nawierzchni ażurowych i terenu nad skrzynkami; dach zielony garażu (≥ 10 m², liczony w 50 %) tylko jako rezerwa | MPZP; upzp art. 2 pkt 28–29; WT §3 pkt 22 [R8-01, R8-02, R8-30] [PROG] | PZT | AUD-PZT |
| W-032 | (Nadziemna) intensywność zabudowy **0,05–0,80** ⇒ Σ pow. kondygnacji nadziemnych **80,00–1280,00 m²** (po zewnętrznym obrysie ścian, bez balkonów, loggii, tarasów; garaż wliczony) | MPZP; upzp art. 2 pkt 31–34, art. 15 ust. 2 pkt 6 [R8-04, R8-05, R8-08] [PROG] | PZT | AUD-PZT |
| W-033 | Wysokość zabudowy ≤ **11,00 m**: od średniej z min. i maks. rzędnej terenu na obwodzie ścian do najwyższego punktu (attyka, balustrady, PV, wyłaz — wliczane); rezerwa ≥ 0,30 m ⇒ ≤ **10,70 m**; PV nie ponad attykę; liczyć od niższej rzędnej (istniejąca/projektowana) | MPZP; upzp art. 2 pkt 30 [R8-03, R8 3.2, R8-R5] [PROG] | PZT, PAB | AUD-PZT |
| W-034 | Maks. **3 kondygnacje nadziemne** — warunek także zwolnienia ppoż. (W-211) | MPZP; upzp art. 2 pkt 34; WT §3 pkt 16 [R8 3.1; R3 D-03] [PROG] | PAB | AUD-WT |
| W-035 | Dachy płaskie o spadku ≤ **12°** | MPZP [PROG] | PAB | AUD-WT |
| W-036 | ≥ **2 miejsca postojowe** na lokal (wliczając garaż); liczba miejsc wg MPZP | MPZP; WT §18 ust. 2 [R3 Z-05; R8-23] [PROG] | PZT | AUD-PZT |
| W-037 | Kolorystyka elewacji: biele, szarości, grafit, naturalne drewno, beton architektoniczny — wykazać w opisie i na elewacjach | MPZP; RPB §20 ust. 1 pkt 3 [R2 A03] [PROG] | PAB | KR |
| W-038 | Ogrodzenie od drogi ażurowe, wys. ≤ **1,60 m**, bez prefabrykatów betonowych (ZKP we wnęce murka/słupka) | MPZP [R7 3.1] [PROG] | PZT | AUD-PZT |
| W-039 | Ogrzewanie ze źródeł niskoemisyjnych/OZE (PC powietrze–woda); PV na dachu dopuszczalna | MPZP; upzp art. 15 ust. 4 [R8-14] [PROG] | PAB | KR |
| W-040 | Fikcyjny MPZP uzupełnić o § „Definicje” (art. 2 pkt 28–35 upzp; art. 67 ust. 3 pkt 1 u.zm.upzp) i definicję linii zabudowy z dopuszczalnymi wysunięciami | u.zm.upzp (Dz.U. 2023 poz. 1688) art. 67 ust. 2–3 [R8-07, R8-09, R8 3.1] | OPIS | DOK |
| W-041 | Zestawienie powierzchni w PZT: zabudowy (bez tarasów naziemnych i podpartych słupami, gzymsów, balkonów, loggii), dróg i placów, PBC, pozostałe wskaźniki MPZP (intensywność, wysokość, miejsca, odległość od linii zabudowy); m² z 2 miejscami | RPB §14 pkt 4 lit. a–d (lit. a wg Dz.U. 2023 poz. 2405) [R2 Z05; R8-45] | PZT (opis) | AUD-PZT |

### B.3 Pomieszczenia, wysokości, drzwi

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-050 | Wysokość w świetle pokoi ≥ **2,50 m** (kuchnię przyjęto 2,50 m) | WT §72 ust. 1 [R3 B-10] | PAB | AUD-WT |
| W-051 | Pomieszczenia na czasowy pobyt ludzi ≥ **2,20 m** | WT §72 ust. 1 [R3 B-10] | PAB | AUD-WT |
| W-052 | Łazienki i WC ≥ **2,50 m**; **2,20 m** dopuszczalne przy wentylacji mechanicznej | WT §77 ust. 2–3 [R3 B-13] | PAB | AUD-WT |
| W-053 | Pomieszczenia techniczne i gospodarcze (garderoby, spiżarnia) ≥ **2,00 m**; przejścia pod przewodami ≥ **1,90 m** | WT §97 ust. 1–2 [R3 B-21] | PAB | AUD-WT |
| W-054 | Podłoga pomieszczeń na stały pobyt ≥ poziomu terenu przy budynku (±0,00 ≈ 0,30 m nad terenem) | WT §73 ust. 1 [R3 B-11] | PAB | AUD-WT |
| W-055 | Drzwi wejściowe ≥ **0,90 × 2,00 m** w świetle ościeżnicy (skrzydło główne ≥ 0,90 m); próg ≤ **0,02 m** | WT §62 ust. 1, 3 [R3 B-06, B-07] | PAB, PT-AR | AUD-WT |
| W-056 | Wejście chronione przed zimnym powietrzem — wiatrołap | WT §63 [R3 B-08] | PAB | KR |
| W-057 | Daszek nad wejściem (budynek > 2 kondygnacji): szerokość ≥ szerokość drzwi + **1,0 m**, wysięg ≥ **1,0 m**; przenosi obciążenie od spadających szyb i okładzin; ≥ 1,50 m od granic (W-004), bez przekraczania linii zabudowy (W-006) | WT §292 ust. 1–2 [R3 K-12] | PAB, PT-BO | AUD-WT |
| W-058 | Drzwi do pokoi i kuchni ≥ **0,80 × 2,00 m**, bez progów | WT §75 ust. 1, 3 [R3 B-12] | PAB | AUD-WT |
| W-059 | Drzwi do łazienek i WC otwierane **na zewnątrz** (lub przesuwne), ≥ **0,80 × 2,00 m**, otwory w dolnej części ≥ **0,022 m²** | WT §79 ust. 1–2 [R3 B-15] | PAB | AUD-WT |
| W-060 | Wydzielony WC: szerokość ≥ **0,90 m**, pole przed miską **0,60 × 0,90 m** | WT §83 [R3 B-17] | PAB | AUD-WT |
| W-061 | Ściany łazienek zmywalne i odporne na wilgoć do **2,0 m**; posadzki łazienek, WC, pralni zmywalne, nienasiąkliwe, nieśliskie; kabina natryskowa murowana do stropu ≥ 1,5 m², szer. ≥ 0,9 m, z wywiewem mechanicznym | WT §78, §81 ust. 2 [R3 B-14, B-16] | PT-AR | KR |
| W-062 | Wymiary z WT rozumiane z wykończeniem; szerokość drzwi w świetle ościeżnicy (skrzydło jej nie zmniejsza); odległości mierzone poziomo w miejscu najmniejszego oddalenia, od lica ocieplenia/okładziny | WT §9 ust. 1–4 [R3 D-08, D-09; R4-F15] | wszystkie | AUD-WT |
| W-063 | Wysokość budynku wg WT (od terenu przy najniższym wejściu do górnej powierzchni najwyższego stropu z izolacją lub najwyższego punktu stropodachu nad pomieszczeniami) — grupa **N** (≤ 12 m lub ≤ 4 kondygnacje); wykazać obok wysokości wg upzp (W-033) | WT §6, §8 pkt 1, §3 pkt 15 [R3 D-01, D-02; R8-29] | PAB | AUD-WT |
| W-064 | Na dachu brak przestrzeni technicznej o średniej wysokości w świetle > **2,0 m** (byłaby kondygnacją — utrata W-211) | WT §3 pkt 16 [R3 D-03; R5 3.9] | PAB | AUD-WT |
| W-065 | Wyjście na dach: klapa ≥ **0,80 × 0,80 m** (lub drzwi 0,80 × 1,90 m); drabina szer. ≥ **0,50 m**, szczeble co ≤ **0,30 m**, obręcze od 3,0 m, ≥ 0,15 m od ściany | WT §308 ust. 1, 3; §101 ust. 2–3 [R3 K-20, K-21] | PAB, PT-AR | AUD-WT |
| W-066 | Pomieszczenie techniczne z urządzeniami hałaśliwymi (PC, centrala) obok pomieszczeń na stały pobyt — przegrody i posadowienie chroniące przed hałasem i drganiami | WT §96 ust. 1–2; PN-B-02171:2017-06 (zał. 1 lp. 2) [R3 B-20; R5-04] | PT-AR, PT-IS | KR |
| W-067 | Nawierzchnie dojść, schodów i podłóg (także garażu) nieśliskie; przezroczyste skrzydła drzwi oznakowane, szkło bezpieczne; wycieraczka wpuszczana, kratki na przejściu ≤ **20 mm** | WT §305 ust. 1, §295, §294 ust. 2–3 [R3 K-14, K-15, K-19] | PT-AR | KR |
| W-068 | Program Inwestora (nie WT): pokój ≥ 8 m², pokoje dzieci ≥ 12 m², PU ≈ 230–270 m², kuchnia z oknem, pokój gościnny na P0 | brief §4–5; dawny §94 ust. 2 uchylony (Dz.U. 2017 poz. 2285) [R3 B-18, B-19] [PROG] | PAB | AUD-WT |
| W-069 | Kubatura brutto (WT §3 pkt 24; PN-ISO 9836) liczona z modelu, m³ z 2 miejscami — rozstrzyga o PWP (W-190) i o zakresie uprawnień (> 1000 m³) | WT §3 pkt 24; PB art. 15a [R3 D-06; R1-32] | PAB (opis) | AUD-WT |

### B.4 Oświetlenie

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-080 | Okna w pomieszczeniu na pobyt ludzi ≥ **1/8** powierzchni podłogi (w świetle ościeżnic, nie szkło); w innych pomieszczeniach z wymaganym światłem dziennym ≥ **1/12** | WT §57 ust. 2 [R3 B-04] | PAB | AUD-WT |
| W-081 | Wyłącznie sztuczne oświetlenie tylko w przypadkach z §58 (garderoby, spiżarnia, techniczne — nie są na pobyt ludzi) | WT §58 ust. 1 [R3 B-05] | PAB | KR |
| W-082 | Elektryczne oświetlenie zewnętrzne wejścia i oświetlenie garażu; oświetlenia dojść i dojazdów nie wymaga się | WT §64, §102 pkt 3, §14 ust. 4 [R3 B-09, Z-02; R7-B12, B13] | PT-IE | KR |

### B.5 Schody, balustrady, okna (bezpieczeństwo użytkowania)

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-090 | Schody wewnętrzne: bieg ≥ **0,80 m**, spocznik ≥ **0,80 m**, wysokość stopnia ≤ **0,19 m**; projekt: bieg 1,00 m, spocznik ≥ 1,00 m, h ≈ 0,175 m, s ≈ 0,28 m | WT §68 ust. 1 [R3 K-01] | PAB, PT-AR | AUD-WT |
| W-091 | **2h + s = 0,60–0,65 m** (projekt 0,63 m); limit 17 stopni w biegu nie dotyczy; szerokość użytkowa mierzona między poręczami | WT §69 ust. 2, 4; §68 ust. 4 [R3 K-03, K-05, K-06] | PT-AR | AUD-WT |
| W-092 | Stopnie wachlarzowe ≥ **0,25 m**, mierzone w odległości 0,40 m od poręczy wewnętrznej | WT §69 ust. 6 [R3 K-07] | PT-AR | AUD-WT |
| W-093 | Schody zewnętrzne do budynku: szerokość ≥ **1,20 m**, ≤ **10 stopni** w biegu (projekt h ≈ 0,15 m); schody techniczne: 0,80 / 0,80 / h ≤ 0,20 m | WT §68 ust. 1, 3; §69 ust. 3 [R3 K-02, K-04, K-05] | PAB, PZT | AUD-WT |
| W-094 | Balustrada od strony otwartej przy różnicy poziomów > **0,50 m**; w domu jednorodzinnym schody ≤ 1,0 m bez balustrady, gdy obustronnie szersze od drzwi o ≥ 0,5 m (wejście ≈ 0,30 m — bez balustrady) | WT §296 ust. 1–2 [R3 K-09] | PAB | AUD-WT |
| W-095 | Balustrady (dom jednorodzinny) ≥ **0,90 m** do wierzchu poręczy; prześwit nieregulowany (zalecane ≤ 0,12 m [ZAŁ]); siły poziome wg PN-EN 1990/1991; szkło o podwyższonej wytrzymałości, bez ostrych elementów | WT §298 ust. 1–2, zał. 1 lp. 59 [R3 K-10] | PAB, PT-AR, PT-BO | AUD-WT |
| W-096 | Poręcze ≥ **0,05 m** od ściany; poręcze schodów zewnętrznych przedłużone o **0,30 m** | WT §298 ust. 5–6 [R3 K-11] | PT-AR | KR |
| W-097 | Podokiennik ≥ **0,85 m** nad podłogą (poza przyziemiem) albo balustrada ≥ 0,90 m lub dolna część stała ze szkła o podwyższonej wytrzymałości (boks C, okna od podłogi na P1 i P2) | WT §301 ust. 1, 3 [R3 K-17] | PAB, PT-AR | AUD-WT |
| W-098 | Okna na P2 (powyżej 2. kondygnacji nadziemnej) i okna nad przejściami otwierane do wewnątrz; uchylne na zewnątrz o osi poziomej — wychylenie ≤ **0,60 m**, szkło bezpieczne; okna HS na P2 — D-17 | WT §299 ust. 1–2 [R3 K-16] | PT-AR (zestawienie stolarki) | AUD-WT |
| W-099 | Pochylnie: piesze zewnętrzne ≤ 15 % (h ≤ 0,15 m) / 8 % (h ≤ 0,5 m) / 6 %; wewnętrzne 15 / 10 / 8 %; samochodowa w garażu indywidualnym ≤ **25 %** | WT §70 [R3 K-08] | PZT, PAB | AUD-WT |
| W-100 | Prześwit nad biegiem schodów ≥ **2,00 m** (dobra praktyka, brak wymogu WT) | [R3 K-22] [ZAŁ] | PT-AR | AUD-WT |
