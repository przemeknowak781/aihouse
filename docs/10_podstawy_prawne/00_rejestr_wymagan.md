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

### B.6 Garaż (2-stanowiskowy w bryle parteru, nieogrzewany)

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-110 | Wysokość w świetle konstrukcji ≥ **2,20 m**, do spodu instalacji ≥ **2,00 m**; oświetlenie elektryczne | WT §102 pkt 1, 3 [R3 B-22] | PAB | AUD-WT |
| W-111 | Wrota w świetle ≥ **2,30 m** szerokości i ≥ **2,00 m** wysokości (przyjęto bramę segmentową ok. 5,00 × 2,125 m [ZAŁ]) | WT §102 pkt 2 [R3 B-22] | PAB | AUD-WT |
| W-112 | Dłuższa krawędź stanowiska ≥ **0,30 m** od ściany, ≥ 0,10 m od słupa; droga manewrowa ≥ 5,0 m; szerokość w świetle ≥ **5,60 m** (0,3 + 2 × 2,5 + 0,3; szerokość stanowiska 2,5 m przeniesiona z §21 [INT]), zalecane 5,90–6,00 m; głębokość ≥ 6,00 m [PROG] | WT §104 ust. 1 pkt 1, ust. 3; §21 ust. 1 [R3 B-23 (weryf.)] | PAB | AUD-WT |
| W-113 | Ściany i strop garaż–dom: izolacyjność akustyczna wg §326 i **szczelność na spaliny i opary**; drzwi garaż–dom z uszczelką i samozamykaczem [ZAŁ] | WT §106 ust. 1 [R3 B-24] | PAB, PT-AR | KR |
| W-114 | Posadzka ze spadkiem do wpustu lub (dom jednorodzinny) na nieutwardzony teren; próg **30 mm** na krawędzi posadzki | WT §107 ust. 1–2 [R3 B-25] | PT-AR | KR |
| W-115 | Garaż **nieogrzewany** (decyzja): wentylacja naturalna, otwory netto ≥ **0,04 m² na stanowisko** ⇒ ≥ **0,08 m²** [INT], w ścianach przeciwległych/bocznych lub we wrotach; nie podłączać do rekuperacji (wariant ogrzewany: ≥ 1,5 wymiany/h) | WT §108 ust. 1 pkt 1–2; §150 ust. 5 [R3 B-26 (weryf.); R6-46] | PAB, PT-IS | AUD-WT |
| W-116 | Przedsionek ppoż. garaż–dom niewymagany (dom jednorodzinny); §271 nie stosuje się do usytuowania garażu ≤ 3 stanowisk | WT §280 ust. 3, §276 ust. 2 [R3 P-05, P-06] | PAB | KR |
| W-117 | Wrota–okna: w pionie ≥ **1,50 m** (dotyczy wszystkich okien; 1,10 m przy daszku niepalnym o wysięgu ≥ 0,60 m wysuniętym 0,80 m poza boki wrót albo przy wrotach cofniętych o 0,80 m); w poziomie od wrót do okien pomieszczeń na pobyt ludzi ≥ **1,50 m** | WT §279 ust. 1–2 [R3 P-07 (weryf.)] | PAB (elewacja z bramą) | AUD-WT |
| W-118 | W garażu zakaz studzienek rewizyjnych, urządzeń i przewodów gazowych, otworów rewizyjnych kanałów dymowych, spalinowych i wentylacyjnych (centrala i rewizje poza garażem) | WT §281 [R3 P-08] | PT-IS, PT-AR | KR |
| W-119 | Dach garażu **nieużytkowy** (zielony ekstensywny), bez tarasu i bez dostępu: obciążenie użytkowe kat. H + ciężar dachu zielonego jako stały (wg producenta); współczynnik spływu 0,5; PBC 50 % jako rezerwa | brief §1.2 (v2); PN-EN 1991-1-1 p. 6.3.4.2 + NA [R5-22; R6-64; R8-01] | PAB, PT-BO | OBL-KON |

### B.7 Instalacje wodociągowe, kanalizacyjne, c.w.u., wody opadowe

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-130 | Ciśnienie przed każdym punktem czerpalnym **0,05–0,60 MPa** (zawór redukcyjny przy wyższym) | WT §114 ust. 1 [R3 IW-02; R6-49] | PT-IS | OBL-IS |
| W-131 | Wodomierz główny w wydzielonym, łatwo dostępnym miejscu na parterze (pom. techniczne P0), chroniony przed zalaniem, mrozem i osobami postronnymi (studzienka tylko przy braku miejsca); za wodomierzem zabezpieczenie przed przepływem zwrotnym (PN-EN 1717); mostek przed i za wodomierzem przy rurach metalowych | WT §115 ust. 1–2, §116 ust. 1–3, §117 [R3 IW-03…IW-05; R6-49] | PT-IS, PZT | KR |
| W-132 | Instalacja wg PN-B-01706:1992 (wycof., powołana w WT); przepływ obliczeniowy **q = 0,682·(Σq_n)^0,45 − 0,14** (Σq_n ≤ 20 dm³/s); kontrolnie PN-EN 806-3 (LU) | WT §113 ust. 4, zał. 1 lp. 4 [R6-48, R6-50, R6-51] [NZW q_n] | PT-IS | OBL-IS |
| W-133 | C.w.u. w punktach czerpalnych **55–60 °C**; możliwość dezynfekcji (chemicznej lub fizycznej) — przy metodzie cieplnej **70–80 °C** w punktach (projekt: grzałka/program antylegionella + termostatyczny zawór mieszający); zabezpieczenie przed przekroczeniem ciśnienia i temperatury; ciepła woda z lewej strony armatury | WT §120 ust. 2, 2a, 4, 5 [R3 IW-06 (weryf.); R6-52] — sprzeczność S-1 | PT-IS | KR |
| W-134 | Cyrkulacja c.w.u. niewymagana (dom jednorodzinny) — cyrkulacja czasowa (η_W,d 0,80) albo brak przy krótkich przewodach; inny sposób podgrzewania c.w.u. w przerwach pracy ogrzewania (grzałka, tryb c.w.u. PC) | WT §119, §120 ust. 1 [R3 IW-07, IW-08; R6-17] | PT-IS | KR |
| W-135 | Izolacja przewodów c.w.u. i c.o. (λ = 0,035 W/(m·K)): d_w ≤ 22 mm → **20 mm**; 22–35 mm → **30 mm**; 35–100 mm → równa d_w; > 100 mm → 100 mm; w przejściach przez przegrody 50 % | WT §118 ust. 3, §133 ust. 9, zał. 2 pkt 1.5 [R3 IW-09; R6-25] | PT-IS | KR |
| W-136 | Deszczówka do spłukiwania WC/podlewania — odrębna instalacja, bez połączenia z wodociągiem | WT §126 ust. 3 [R3 Z-13; R6-54] | PT-IS | KR |
| W-137 | Wyroby w kontakcie z wodą do spożycia z certyfikatem wg rozdz. 3b ustawy o PIS; ocena ryzyka wewnętrznego systemu wodociągowego nie dotyczy domu jednorodzinnego | Dz.U. 2026 poz. 605 (art. 4i ust. 10; art. 37ao–37ap PIS) [R6-53] | PT-IS | KR |
| W-138 | Kanalizacja wg PN-EN 12056-1…5:2002, do pierwszej studzienki; **Q_ww = 0,5·√ΣDU** (nie mniej niż największy DU [NZW]); pion z miską ustępową ≥ **DN100** | WT §122 ust. 1–2, zał. 1 lp. 10 [R3 IK-01; R6-55, R6-57, R6-58] | PT-IS | OBL-IS |
| W-139 | Piony wentylowane ponad dach i powyżej górnej krawędzi okien/drzwi w odległości poziomej < **4 m**; zawory napowietrzające (PN-EN 12380) tylko gdy ostatni pion na każdym przewodzie odpływowym i co najmniej co piąty wyprowadzone ponad dach; zakaz włączania do kanałów wentylacyjnych | WT §125 ust. 1–3 [R3 IK-02; R6-56] | PT-IS | KR |
| W-140 | Zabezpieczenie przed cofką, gdy grawitacyjny spływ może być czasowo niemożliwy — sprawdzić rzędne studni wobec wpustów garażu | WT §124 [R3 IK-03; R6-59] | PT-IS | OBL-IS |
| W-141 | Przykrycie przyłącza wodociągowego ≥ **h_z + 0,4 m = 1,20 m** do wierzchu rury (normy wycofane — wiedza techniczna; potwierdzić w warunkach gestora) | PN-B-10725:1997, PN-B-10736:1999 (wycof.) [R5-95 (weryf.)] [NZW] | PZT, PT-IS | KR |
| W-142 | Odwodnienie dachów: rynny, spusty, wpusty na **r = 0,046 l/(s·m²)** (zakres zaleceń 0,03–0,05); dachy płaskie z przelewami awaryjnymi; spadki dachów ≥ 2 % [ZAŁ] | WT §126 ust. 1, §319 ust. 1; PN-EN 12056-3 [R6-61; R3 H-04] [NZW] | PT-IS, PT-AR | OBL-IS |
| W-143 | Retencja/rozsączanie (metodyka Aquanet 2024): deszcz PANDa 2050 RCP4.5, Poznań-Ławica, **C = 10 lat**; V_min = **1,2·V_obl** (1,1 z przelewem awaryjnym); k_f,nn = **0,5·k_f**; opróżnianie ≤ **24 h**; osadnik przed urządzeniem; ψ: dach płaski 0,95, dach zielony ekstensywny 0,5, kostka 0,8, ażur 0,4, ogród 0,15; k_f z badań | Aquanet S.A., zał. C (2024) — wytyczne operatora [R6-62…R6-64] [ZAŁ] | PT-IS, PZT | OBL-IS |
| W-144 | Lokalizacja urządzeń rozsączających (nienormatywne): ≥ **3,0 m** od fundamentów (i ≥ 1,5·h_f + 0,5 m), ≥ **2,0 m** od granic, ≥ **1,0 m** od drzew; dno ≥ **1,0 m** nad maks. ZWG | [R6-62; R8 3.5, R8-R4] [ZAŁ] — sprzeczność S-4 | PZT | AUD-PZT |
| W-145 | Wariant bazowy (najniższe ryzyko wodnoprawne): szczelny zbiornik ≤ **5 m³** (nie jest urządzeniem wodnym) + przelew do niecki/ogrodu deszczowego (≤ 0,3 m) na podstawie WT §28 ust. 2; skrzynki rozsączające tylko po stanowisku PGW Wody Polskie (D-05) | PW art. 16 pkt 65 lit. f, art. 389 pkt 6, art. 395; PB art. 29 ust. 1 pkt 38, ust. 2 pkt 36 [R8 3.5; R6-66, R6-67; R1-36] | PZT, PT-IS | DOK |
| W-146 | Skropliny z PC do gruntu w strefie niezamarzającej albo do deszczówki z ochroną przed zamarzaniem; nie do studzienek w strefie R290 | [R6 3.7] [ZAŁ] | PT-IS | KR |

### B.8 Ogrzewanie, temperatury, źródło ciepła

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-150 | θ_i: pokoje, hol, kuchnia **+20 °C**; łazienki **+24 °C**; garaż nieogrzewany (wariant ogrzewany +5 °C); θ_e = **−18 °C** (strefa II), θ_m,e = **7,9 °C** | WT §134 ust. 2; NA do PN-EN 12831:2006 [R3 IO-03; R5-110; R6-35] [NZW przypisanie strefy] | PT-IS | OBL-IS |
| W-151 | Obciążenie cieplne formalnie wg **PN-EN 12831:2006** (powołana w WT, wycof.), kontrolnie PN-EN 12831-1:2017-08 | WT §134 ust. 1, zał. 1 lp. 16 [R6-34, R6 N-2] | PT-IS | OBL-IS |
| W-152 | **Automatyczna regulacja temperatury oddzielnie w każdym pomieszczeniu** (termostaty + siłowniki; strefowa, gdy montaż niemożliwy) — gdy technicznie możliwa i okres zwrotu ≤ **5 lat**; analiza w PAB | WT §135 ust. 7–10; RPB §20 ust. 1 pkt 11 [R3 IO-05; R6-06, R6-36] | PAB, PT-IS | KR |
| W-153 | Regulatory dopływu ciepła na odbiornikach; czynnik grzewczy w pomieszczeniach ≤ **90 °C**, zakaz ogrzewania parowego; nieosłonięte powierzchnie c.o. ≤ 90 °C; podłogówka ≤ 35 °C [ZAŁ] | WT §134 ust. 4, §135 ust. 5, §302 ust. 1 [R3 IO-04, IO-07, K-18] | PT-IS | KR |
| W-154 | Podział na obiegi, armatura odcinająca i spustowa, odpowietrzenie, zabezpieczenie instalacji wodnej (PN-B-02414:1999), niska ilość wody uzupełniającej; przewody wymienialne bez naruszania konstrukcji | WT §133 ust. 3–6, §134 ust. 8, 10, §138 [R3 IO-06, IO-08, IO-09] | PT-IS | KR |
| W-155 | PC: **monoblok powietrze–woda na czynniku naturalnym (R290)** — od **01.01.2027** zakaz wprowadzania do obrotu monobloków i splitów powietrze–woda ≤ 12 kW z F-gazem o GWP ≥ 150; ekoprojekt: η_s ≥ **125 %** (niskotemperaturowa), L_WA zewn. ≤ **65 dB** (≤ 6 kW) / ≤ **70 dB** (6–12 kW) | rozp. (UE) 2024/573 zał. IV pkt 8–9; (UE) 813/2013 zał. II [R6-68…R6-71] | PAB, PT-IS | KR |
| W-156 | Strefa bezpieczeństwa R290 wg DTR (typowo **1,0 m**): bez okien, drzwi, otworów wentylacyjnych, wpustów, studzienek, zagłębień terenu i źródeł zapłonu; wrysować na PZT i elewacji | PN-EN 378-1+A1:2021-03; dane producentów [R6-75] [NZW] | PZT, PT-IS | AUD-PZT |
| W-157 | Analiza wysoce wydajnych systemów alternatywnych: roczna energia użytkowa (ogrzewanie, wentylacja, c.w.u.), dostępne nośniki, **2 systemy** (np. kocioł gazowy kondensacyjny vs PC R290 + PV + rekuperacja), obliczenia porównawcze, wynik i wybór | RPB §20 ust. 1 pkt 10 lit. a–e [R1-20; R2 A13; R6-05] | PAB (opis) | DOK |
| W-158 | Oświadczenie projektanta instalacyjnego (art. 14 ust. 1 pkt 4 lit. b PB) o możliwości przyłączenia do sieci ciepłowniczej (brak sieci), z klauzulą o odpowiedzialności karnej | PB art. 33 ust. 2 pkt 10; Pr. energ. art. 7b ust. 1, 3, 3c [R1-46; R2 W07] | WN | DOK |

### B.9 Wentylacja

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-160 | Wentylacja mechaniczna nawiewno-wywiewna z odzyskiem ciepła; w pomieszczeniach z wentylacją mechaniczną **zakaz** wentylacji grawitacyjnej i hybrydowej; regulacja wydajności wentylatorów | WT §148 ust. 2, 5 [R3 IV-05, IV-06; R6-40] | PT-IS | KR |
| W-161 | Powietrze zewnętrzne ≥ **20 m³/h na osobę** na pobyt stały (5 osób ⇒ ≥ 100 m³/h) i ≥ Σ wywiewu; przepływ z pokoi do kuchni i łazienek; łączenie przewodów z różnych pomieszczeń dozwolone | WT §149 ust. 1, §150 ust. 2–3 [R3 IV-02, IV-04, IV-07; R6-39] | PT-IS | OBL-IS |
| W-162 | Wywiew minimalny (PN-B-03430:1983/Az3:2000 — wycof., wiąże przez WT): kuchnia z kuchenką elektryczną **50 m³/h** (> 3 osób; ≤ 3 osób 30), okresowo ≥ 120; łazienka **50**; WC **30**; pomieszczenie bezokienne **15**; pralnia ≥ 2 h⁻¹; suma ≈ **330 m³/h** | WT §147 ust. 1, §149 ust. 1, zał. 1 lp. 26, 28 [R3 IV-03; R6-38, R6 3.5] [NZW] | PT-IS | OBL-IS |
| W-163 | Odzysk ciepła ≥ 50 % obowiązkowy dopiero od **500 m³/h** (tu nie zachodzi); cel projektowy η ≥ **85 %** [ZAŁ]; przenikanie strumieni w wymienniku płytowym ≤ 0,25 % | WT §151 ust. 1–2 [R3 IV-08; R6-41] | PT-IS | KR |
| W-164 | SFP: nawiew z odzyskiem ≤ **1,60 kW/(m³/s)**, wywiew z odzyskiem ≤ **1,00 kW/(m³/s)**; +0,3 przy odzysku > 67 % | WT §154 ust. 10–11 [R3 IV-14; R6-44] | PT-IS | OBL-IS |
| W-165 | Filtry przed wymiennikiem, nagrzewnicą i chłodnicą ≥ **G4** (PN-EN 779, wycof.); projekt: ISO ePM1 50 % na nawiewie, ISO Coarse na wywiewie [ZAŁ] | WT §154 ust. 6 [R3 IV-13; R6-44] | PT-IS | KR |
| W-166 | Czerpnia na terenie lub ścianie 2 najniższych kondygnacji: ≥ **8 m** od ulic, miejsc gromadzenia odpadów, wywiewek kanalizacyjnych; dolna krawędź ≥ **2 m** nad terenem. Czerpnia dachowa ≥ **0,4 m** nad powierzchnią i ≥ **6 m** od wywiewek | WT §152 ust. 3–4 [R3 IV-09; R6-42] | PT-IS, PZT | AUD-WT |
| W-167 | Wyrzutnia dachowa ≥ 0,4 m nad powierzchnią i nad punktami w promieniu 10 m; czerpnia–wyrzutnia na dachu ≥ **10 m** (wyrzut poziomy) / ≥ **6 m** (pionowy), wyrzutnia ≥ 1 m wyżej (albo zestaw zblokowany); ≥ **3 m** od krawędzi dachu z oknami poniżej. Wyrzutnia ścienna: ściana sąsiada z oknami ≥ 10 m (bez okien 8 m), okna tej ściany ≥ 3 m poziomo i ≥ 2 m pionowo, czerpnia niżej, ≥ 1,5 m | WT §152 ust. 6–13 [R3 IV-10; R6-43, R6 3.5 (weryf.)] | PT-IS | AUD-WT |
| W-168 | Przewody powietrza zewnętrznego i do odzysku izolowane cieplnie i przeciwwilgociowo; przewody w przestrzeniach nieogrzewanych izolowane; otwory rewizyjne; połączenia elastyczne ≤ **0,25 m**; przewody palne dopuszczalne (dom 1-lokalowy) | WT §153 ust. 5–7, §154 ust. 8, §267 ust. 1a, 7 [R3 IV-11, IV-12, IV-15, P-15; R6-44] | PT-IS | KR |
| W-169 | Centrala wentylacyjna zgodna z ekoprojektem: SEC ≤ **−20 kWh/(m²·a)**, obejście (by-pass), napęd wielobiegowy lub płynny, sygnalizacja wymiany filtra | rozp. (UE) 1253/2014 zał. II pkt 2 [R6-45] | PT-IS | KR |

### B.10 Instalacje elektryczne, odgromowa, teletechnika

| ID | Wymaganie | Podstawa | Gdzie | Sprawdzenie |
|---|---|---|---|---|
| W-180 | Złącze w miejscu dostępnym; **oddzielne PE i N** w obwodach rozdzielczych i odbiorczych (TN-S); RCD; wyłączniki nadprądowe; **selektywność**; połączenia wyrównawcze główne i miejscowe; trasy równoległe do krawędzi; żyły wyłącznie **Cu** do 10 mm²; **ochrona przeciwprzepięciowa** | WT §183 ust. 1 pkt 1–10 [R3 IE-02; R7-B03] | PT-IE | KR |
| W-181 | RCD I_Δn ≤ **30 mA**: gniazda ≤ 32 A, **obwody oświetleniowe** (lokal jednego gospodarstwa), wszystkie obwody łazienek, urządzenia ruchome na zewnątrz; typ AC niedopuszczalny (min. A; PC i falownik wg DTR); preferowane RCBO | PN-HD 60364-4-41:2017-09 p. 411.3.3–411.3.4; PN-HD 60364-7-701 [R7-C01…C05, H02] | PT-IE | KR |
| W-182 | Samoczynne wyłączenie (TN, 230 V) w **0,4 s** dla obwodów końcowych ≤ 63 A z gniazdami i ≤ 32 A odbiorników stałych; I_B ≤ I_n ≤ I_z, I₂ ≤ 1,45·I_z [NZW] | PN-HD 60364-4-41 tabl. 41.1; PN-HD 60364-4-43:2024-04 [R7-C03, E06] | PT-IE | OBL-IE |
| W-183 | Obwody wydzielone: oświetlenie, gniazda ogólne, **gniazda w łazienkach**, **gniazda kuchenne**, odbiorniki z indywidualnym zabezpieczeniem; łączniki wieloobwodowe w pokojach; ≥ 1 wypust w pokoju ≤ 20 m², ≥ 2 w większym | WT §188 ust. 2, §189 ust. 1–2; N SEP-E-002 [R3 IE-08, IE-09; R7-B10, B11, O01] | PT-IE | KR |
| W-184 | Przewody wymienialne; tynk nad przewodem ≥ **5 mm**; min. **1,5 mm² Cu** (siłowe, oświetleniowe), 0,5 mm² (sterownicze); w stropach monolitycznych w rurach | WT §187 ust. 1–2; PN-HD 60364-5-52 tabl. 52.2 [R7-B09, E02] | PT-IE | KR |
| W-185 | Spadek napięcia ZKP → odbiornik ≤ **3 %**, w tym kabel ZKP–RG ≤ **0,5 %** (norma z WT, wyd. 2002: ≤ 4 %); obciążalność WLZ ≥ 50 A | N SEP-E-002; PN-IEC 60364-5-52:2002 [R7-E03…E05] [NZW] | PT-IE | OBL-IE |
| W-186 | SPD obowiązkowy (WT; ponadto CRL < 1000: f_env = 170, N_g = 1,8 ⇒ graniczna długość linii kablowej 94 m); w RG **typ 1+2**, I_imp ≥ **12,5 kA** na biegun, U_p ≤ **2,5 kV** (zalecane ≤ 1,5 kV); SPD po stronie DC PV | WT §183 ust. 1 pkt 10; PN-HD 60364-4-443:2016 p. 443.4–443.5, tabl. 443.2; PN-HD 60364-7-712 [R7-F01…F06] | PT-IE | OBL-IE |
| W-187 | Uziom fundamentowy ze zbrojenia; przy fundamencie izolowanym termicznie (XPS) albo folią > 0,5 mm — **uziom otokowy w gruncie** (Cu, StCu, StSt); w betonie otulina ≥ **5 cm**, płaskownik na sztorc mocowany co ≤ **2 m**, bez drutu wiązałkowego; wyprowadzenia: GSU + 2–4 narożniki pod LPS | WT §184 ust. 1; PN-HD 60364-5-54:2011 zał. C [R7-G01…G04, G08] | PT-IE, PT-BO | KR |
| W-188 | Przewód uziemiający ≥ 6 mm² Cu (przy LPS ≥ **16 mm²** — przyjęto 16); połączenia wyrównawcze główne ≥ ½ największego PE, ≥ **6 mm²**, ≤ 25 mm² Cu; osobny PE ≥ 2,5 (chroniony) / 4 mm²; objąć wodociąg metalowy, kanalizację, c.o., kanały wentylacji, obudowy teletechniczne, konstrukcję PV, zbrojenie | WT §183 ust. 1a; PN-HD 60364-5-54 p. 542.3.1, 543.1.3, 544.1 [R7-B04, G05…G07] | PT-IE | KR |
| W-189 | Łazienki: strefy 0/1/2 na rzutach (strefa 1 do 2,25 m, strefa 2 — pas 0,60 m wg wyd. 2010 [NZW]; zweryfikować z PN-HD 60364-7-701:2025-02); osprzęt w strefach 1–2 ≥ **IPX4**; bez gniazd i łączników w strefach 0–2 | PN-HD 60364-7-701 [R7-H01…H06] | PT-IE | KR |
| W-190 | **PWP projektować** (rekomendacja): przy wejściu głównym lub ZKP, oznakowany, odcina wszystkie obwody (także AC falownika; strona DC PV oznakowana). WT wymaga przy strefie pożarowej > **1000 m³**; ROPoż zwalnia właścicieli domów jednorodzinnych — D-04 | WT §183 ust. 2–4; ROPoż §4 ust. 2 pkt 2 [R3 IE-04; R7-B05, M01] | PT-IE | OBL-IE |
| W-191 | Ochrona odgromowa: analiza ryzyka wg PN-EN IEC 62305-2:2025 z odniesieniem do PN-EN 62305-2:2008 (WT); R_T = **10⁻⁵/rok**, N_g = 1,8; klasa obciążenia ogniowego (< 400 / 400–800 / > 800 MJ/m²) rozstrzyga; LPS klasy III–IV gdy wymagany; uziom otokowy z wyprowadzeniami zawsze | WT §53 ust. 2, §184 ust. 3, zał. 1 lp. 1, 44 [R3 B-02; R7-K01…K05] [NZW] | PT-IE | OBL-IE |
| W-192 | Przyłącze nN (ENEA Operator): grupa V (≤ 1 kV, ≤ **40 kW**); warunki w 21 dni, ważne 2 lata; ZKP w linii ogrodzenia na działce, pole odczytowe ≥ **0,48 m** nad terenem; pomiar bezpośredni ≤ 40 kW (≤ 63 A); moc przyłączeniowa **27 kW / 40 A** [ZAŁ]; kabel w ziemi ≥ **0,70 m**, taśma niebieska; WLZ YKY 5×16 [ZAŁ] | RSys §3 ust. 1 pkt 5, §4 ust. 2; Pr. energ. art. 7 ust. 8g–8i; standardy ENEA [R7-L01…L09] | PZT, PT-IE | OBL-IE |
| W-193 | Rozdział PEN: preferowany w ZKP i WLZ 5-żyłowy (wymaga zgody OSD); inaczej WLZ 4-żyłowy i rozdział w RG — D-12 | WT §183 ust. 1 pkt 2; standard ENEA ZK1x-1P [R7-L06] | PT-IE | DOK |
| W-194 | PV: moc zainstalowana (Σ mocy modułów z tabliczek) ≤ **6,5 kWp** i falownik ≤ 6,5 kW ⇒ bez uzgodnienia z rzeczoznawcą ppoż., zawiadomienia PSP i planu dla ekip ratowniczych; magazyn ≤ **30 kWh**; mikroinstalacja na zgłoszenie do OSD (moc ≤ mocy przyłączeniowej; ≤ 30 dni, bez opłaty); falownik z certyfikatem NC RfG (od 01.01.2027 etap II); RCD typ B lub wg 712.530.3.101; PN-HD 60364-7-712, odbiór PN-EN 62446-1 | PB art. 29 ust. 4 pkt 3 lit. c (art. 56 ust. 1a uchylony); OZE art. 2 pkt 19, 19b lit. b; Pr. energ. art. 7 ust. 8d4–8d12 [R1-34, R1-35; R6-76…R6-80; R7-I01…I08] | PT-IE, PAB | OBL-IE |
| W-195 | EV: brak obowiązku (UEm art. 12, 12a); EPBD art. 14 ust. 4 (> 3 miejsca: okablowanie wstępne ≥ 50 %, kanały, ≥ 1 punkt) nietransponowana — przy 4 miejscach spełnić dobrowolnie albo ograniczyć do 3; obwód EV osobny, RCD indywidualny typu B lub A/F + RDC-DD 6 mA, bez TN-C | UEm t.j. 2026 poz. 1243; dyr. (UE) 2024/1275 art. 14 ust. 4; PN-HD 60364-7-722:2019-01 [R7-J01…J03; R3 IE-01] | PT-IE, PZT | KR |
| W-196 | Światłowód: infrastruktura wewnątrzbudynkowa przystosowana do światłowodu + okablowanie światłowodowe do punktu zakończenia sieci (wniosek o PnB po 12.02.2026); mikrokanalizacja od granicy działki (2 × HDPE Ø40 [ZAŁ]); dobra praktyka: ≥ 2 włókna SM, SC/APC, tłumienie toru ≤ **1,2 dB** | rozp. (UE) 2024/1309 art. 10 ust. 1; WT §192f ust. 5 (analogia) [R7-N01…N05] | PT-IE, PZT | KR |
| W-197 | Czujki dymu: ≥ **1** autonomiczna czujka w lokalu (PN-EN 14604); projekt: ≥ 1 na kondygnację + sypialnie [ZAŁ]; czujka CO nie dotyczy (brak spalania paliw) | ROPoż §28a ust. 1–4 (Dz.U. 2024 poz. 1716) [R7-M02] | PT-IE | KR |
| W-198 | AFDD — zalecenie (sypialnie), nieobowiązkowe | PN-HD 60364-4-42/A1:2015 p. 421.7 [R7-D01] [NZW] | PT-IE | KR |
| W-199 | Sprawdzenia odbiorcze wg PN-HD 60364-6:2016-07; protokoły badań instalacji do zawiadomienia o zakończeniu budowy | PB art. 57 ust. 1 pkt 4 lit. a [R7-O02, O03] | PT-IE | DOK |
