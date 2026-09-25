# Dom LAMELA — niezależna weryfikacja koncepcji ostatecznej i podglądy uzupełniające

Data: 2026-09-25. Dokument uzupełnia `docs/20_koncepcja/koncepcja.md`. Nie zastępuje go i nie zmienia bilansu w §9, który generuje
`tools/podglad_modelu.py`. Zakres:
1. niezależne przeliczenie wskaźników z modelu i porównanie z §9;
2. porównanie U w §6 z obliczeniem;
3. sprawdzenie w modelu przeszczepów i poprawek;
4. opis wykonanych podglądów: arkusze, PZT, 3D;
5. lista błędów i niespójności do audytu i poprawek.

**Stan modelu.** Wszystkie liczby dotyczą tego samego stanu modelu co §9 koncepcji: pliki z 04:19:44 UTC, walidacja 0 błędów i 0 ostrzeżeń.

| plik | SHA-256 |
|---|---|
| `model/budynek.yaml` | `d238ec0e…ecf11d` |
| `model/dzialka.yaml` | `0e576be3…19848b` |

Po każdej zmianie modelu wyniki trzeba przeliczyć (Aneks A).

**Podstawy.**
* WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu obowiązującym do 19.09.2026. Stosowane na podstawie art. 102a PB.
* MPZP 3MN — uchwała fikcyjna **[DANE PRZYKŁADOWE – FIKCYJNE]**. Działka 123/4, uzbrojenie i teren też są fikcyjne.
* PN-ISO 9836:2022-07 z modyfikacjami RPB §20 (W-316).
* Identyfikatory `W-xxx` odsyłają do `docs/10_podstawy_prawne/00_rejestr_wymagan.md`.

---

## 1. Metoda

Liczby pochodzą wyłącznie z plików modelu i zostały policzone skryptami w scratchpadzie sesji; nie wpisywano ich ręcznie. Użyto API
`lamela.model`: `load_model`, `zestawienie_powierzchni`, `pow_zabudowy`, `pow_brutto_kondygnacji`, `kubatura_brutto`, `obrys_kondygnacji`.
Geometrię (PBC, odległości, teren na obwodzie, ważenie wysokości pod schodami) liczono w shapely/scipy. Użyto też IR
`lamela.ir.build_ir` (najwyższe punkty) oraz modułów obliczeniowych repozytorium:
* `lamela.obliczenia.fizyka_energia` — U, mostki, EP, Φ_HL, wentylacja;
* `lamela.obliczenia.instalacje` — deszczówka i retencja, drenaż, ogrzewanie podłogowe, elektryka, PV.

Raporty modułów zostały w scratchpadzie i nie należą do repozytorium. Da się je odtworzyć poleceniami z Aneksu A.

## 2. Wskaźniki — porównanie z §9 koncepcji

| wskaźnik | §9 `koncepcja.md` | weryfikacja niezależna | metoda / uwagi | wymaganie | ocena |
|---|---|---|---|---|---|
| PU wg RPB §20 / W-316 | **240,24 m²** | **240,24 m²**: P0 96,29, P1 84,39, P2 59,57 | Σ pow. zaliczonych bez klatek 0.04/1.06/2.06, garażu 0.13 i pom. technicznych. Spiżarnia 0.05 liczona w 50 % wg umownej wysokości 1,90 m z modelu | 230–270 m² (brief §4) | ✓ |
| PU — wariant z geometrycznym ważeniem spiżarni | — | **239,26 m²** | Pod biegiem 2 i spocznikiem liczono rzeczywistą wysokość (spocznik +1,575, płyta 0,18 m → pod spocznikiem 1,37 m). Wynik: 0,98 m² × 100 %, 1,47 m² × 50 %, 2,95 m² × 0 %, razem 1,72 m² zamiast 2,70 m² (W-316: ≥ 2,20 → 100 %, 1,40–2,20 → 50 %, < 1,40 → 0 %) | jw. | ✓ |
| PU z pasem 1.06 na P1 | — | 240,73 m² | 1.06 ma 0,49 m² podłogi przy wyjściu z biegu na P1. W-316 wyłącza schody i podesty, a ten pas można uznać za komunikację | jw. | ✓ |
| wartość PU podana wcześniej przez syntezę | 241,07 m² (komunikat syntezy) | **nie potwierdzono** | W obecnym modelu 240,24 m² (−0,83 m²) | — | — |
| kategorie PN-ISO 9836 w PU | — | podstawowa 158,78; pomocnicza bez garażu 41,16; ruchu bez klatek 40,30 m² | Garaż 37,42 m² i pom. techniczne 16,24 m² wykazano osobno (W-316) | — | — |
| powierzchnia zabudowy | 187,50 m² (11,72 %) | **187,50 m²** (11,72 %) | Obrys P0 z ETICS 181,78 m² + wspornik bryły A na P2 5,73 m² (W-030). Rama C nie jest kubaturą, więc jej nie wliczono. Z rzutem płyt wysuniętych: 212,99 m² (13,31 %) | ≤ 480 m² (30 %, MPZP, W-030) | ✓ |
| PBC | 1 281,57 m² (80,10 %) | **1 271,31 m²** (79,46 %) | Z PBC wyłączono sumę geometryczną 328,69 m²: budynek P0 181,78; taras T1 63,08; podesty T2 2,99 i T3 1,30; U1 48,61; U2 9,04; U3 1,05; U4 4,16; U5 1,12; U6 ażur 0,90 (W-031: ażur nie jest PBC); opaska żwirowa 0,5 m 29,95. Dachu zielonego D4 (63,97 m²) nie liczono. Różnica wobec §9 wynosi 10,26 m² i wynika z ujęcia opaski lub ażuru **[DO WYJAŚNIENIA w `podglad_modelu.py`]** | ≥ 800 m² (50 %, W-031) | ✓ |
| intensywność zabudowy | 0,248 | **0,248** | (181,78 + 117,81 + 96,80) / 1600 = 396,39 / 1600 | 0,05–0,80 (W-032) | ✓ |
| wysokość zabudowy (upzp art. 2 pkt 30) | 10,25 m | **10,02 m** do attyki; **10,25 m** z czerpnią/wyrzutnią | Attyka D1 +9,776 (111,426 m n.p.m.). Teren istniejący na obwodzie ścian P0: min 101,328, max 101,479, średnia 101,404 m n.p.m.; TIN terenu projektowanego daje przy licach te same rzędne. Czerpnia +9,95 i wyrzutnia +10,00 (`energia.wentylacja`) są najwyższymi punktami (W-033) → 10,25 m. PV wystaje ponad attykę o 0,05 m (§6 poz. A4) → 10,07 m do PV | ≤ 11,00 m; z rezerwą ≤ 10,70 m (W-033) | ✓ |
| wysokość budynku wg WT §6 | 9,85 m | 9,79–9,85 m | Narzędzia dają różne wartości. Arkusze PB-AR-05…10 przyjmują teren −0,267 i wierzch pokrycia +9,526, co daje 9,79 m. `podglad_modelu.py` przyjmuje teren przy najniższym wejściu −0,326, co daje 9,85 m (§6 poz. C5) | grupa N ≤ 12 m (WT §8 pkt 1, W-063) | ✓ |
| kubatura brutto | 1 354,5 m³ | **1 354,5 m³** | PN-ISO 9836 p. 5.2 z rdzenia. Składniki: P0 578,05 + P1 345,18 + P2 283,63 + płyty ST1 26,83, ST2 21,76, ST2Z 1,80, D1 44,14, D2 8,43, D3 7,69, D4 37,03 m³ | > 1000 m³ → PWP (WT §183, W-190) | — |
| kondygnacje nadziemne / miejsca postojowe | 3 / 4 | 3 / 4 (MP1–MP4 w `dzialka.yaml`) | — | ≤ 3 (W-034); ≥ 2 (W-036) | ✓ |
| odległość budynku od jezdni 1KDD | — | 9,88 m | Lico ściany pn. garażu do krawędzi jezdni | ≥ 6,0 m (u.d.p. art. 43, W-007) | ✓ |
| jednostka zewnętrzna PC od granicy E | 7,00 m (§8, bilans) | 6,90 m od krawędzi fundamentu U5; 7,60 m od środka urządzenia | `dzialka.yaml`: U5, PC-JZ | ≥ 6,0 m (W-024) | ✓ |
| EP | szacunek J2: 55–59 (§7) | **57,2 kWh/(m²·rok)** | Moduł fizyki: A_f 262,74 m², H_tr 276,5 W/K, H_ve 37,2 W/K, H_TB 137,6 W/K (Ψ domyślne PN-EN ISO 14683 / przykładowe łączniki), EU/EK 74,7/32,7. Wrażliwość: Ψ „dobra praktyka” → 40,8; n50 = 4 h⁻¹ → 68,0; bez PV → 81,8 (> 70) | ≤ 70 (WT §329, W-240) | ✓ |
| obciążenie cieplne Φ_HL | — | 11,48 kW (43,7 W/m²) | PN-EN 12831, θ_e = −18 °C. Wynik jest zawyżony przez domyślne Ψ; zob. §6 poz. B4 | — | — |

Odległości od granic w §9 (tabela generowana) zgadzają się z weryfikacją do 0,01 m:
* W: 7,30 m (ściany P0/P1), 6,30 m (P2), 5,20 m (płyty PL-2/PL-3), 4,30 m (taras T1);
* E: 5,725 m (garaż);
* N: 1,625 m za linią zabudowy (brama garażu), 0,95 m za linią (daszek PL-DA).

Spełniają W-001, W-004 i W-006, a daszek ma zapas ≥ 0,30 m wymagany przez J1.

## 3. Współczynniki U — §6 koncepcji wobec obliczenia z modelu

Obliczenia: PN-EN ISO 6946:2017-10 z poprawkami ΔU oraz PN-EN ISO 13370 dla podłogi na gruncie, moduł
`lamela.obliczenia.fizyka.u_przegrody`. Wymagania: WT zał. 2 pkt 1.1 (W-243). Cele projektu: W-245.

| kod | U w §6 i w nazwie przegrody | U obliczone | U_max WT | cel W-245 | uwagi |
|---|---|---|---|---|---|
| SZ1 | 0,15 | **0,17** | 0,20 ✓ | 0,15 ✗ | ΔU łączników 0,021; opis w modelu i w §6 zaniża U |
| SZ2 | 0,16 | **0,17** | 0,20 ✓ | 0,15 ✗ | — |
| SZL | 0,10 | 0,099 | 0,20 ✓ | ✓ | — |
| SWG (dom–garaż) | 0,26 (nazwa: 0,24) | **0,27** | 0,30 ✓ | 0,25 ✗ | — |
| SD1 | 0,10 | 0,11 | 0,15 ✓ | 0,12 ✓ | — |
| SD2 | 0,11 | 0,12 | 0,15 ✓ | 0,12 ✓ | — |
| DZ1 (nad pasem gosp.) | 0,12 | **0,13** | 0,15 ✓ | 0,12 ✗ | Poprawka J2 nr 4 (U ≤ 0,15) spełniona |
| POD-0 | 0,13 (nazwa: 0,14) | 0,11 (U_equiv) | 0,30 ✓ | 0,20 ✓ | A = 110,65 m², B′ = 4,04 m |
| ST2Z / SUF-ZEW | 0,15 | 0,13 | 0,15 ✓ | — | — |
| stolarka | U_w 0,73–0,90 (deklaracje) | 0,61–0,89; **FX3 1,0** | 0,9 (drzwi 1,3) | 0,80 | FX3 to doświetle 0,35 × 2,40 m z dużym udziałem ramy. Jako okno nie spełnia 0,9; można je liczyć z drzwiami DZ1 (≤ 1,3) albo zmienić profil |

Inne wyniki modułu fizyki dla tego stanu modelu:
* g ≤ 0,35: 22/22 okien spełnia (W-247);
* kondensacja międzywarstwowa: 9/9 przegród dopuszczalnych (PN-EN ISO 13788);
* ciągłość „4 linii”: 11/11 przegród;
* izolacja obwodowa: R = 2,78 m²K/W ≥ 2,0 (WT zał. 2 pkt 1.4);
* f_Rsi: 16 węzłów `wezly` nie ma jeszcze symulacji PN-EN ISO 10211 (W-248). Ψ pochodzą z wartości domyślnych PN-EN ISO 14683 oraz przykładowych deklaracji łączników **[DANE PRZYKŁADOWE – FIKCYJNE]**.

## 4. Przeszczepy z W1/W3 i poprawki obowiązkowe — sprawdzenie w modelu

| przeszczep / poprawka | źródło | stan w modelu | ocena |
|---|---|---|---|
| PC R290 monoblok, jednostka zewn. ≥ 6,0 m od granicy E | J1 pkt 6.3, J2 pkt 4.1 (z W3) | `PC-JZ` przy ścianie pd. pasa gospodarczego, 6,90–7,60 m od granicy E. Strefa R290 1,0 m jest bez otworów; najbliższa studnia skroplin SK-PC leży 1,85 m od urządzenia (W-156) | ✓ |
| zbiornik 5,0 m³ + niecka 24 m² × 0,30 m w ogrodzie pd. | J1 5.1, J2 4.2 (z W3) | zbiornik ma 5,0 m³, a niecka 24,0 m² i 7,2 m³ brutto. Niecka leży 12,70 m od budynku, 8,60 m od granicy W i 2,0 m od pnia lipy DR1 (W-144). Moduł deszczowy daje pojemność niecki 6,75 m³ przy V_min 6,65 m³ (zbiornik pełny; W-143, Aquanet 2024) | ✓ (zapas 1,5 %) |
| słupy fasady E w osiach boksu C; kwatery 1,90/1,90/2,34/2,34/2,92; HS w kwaterach 3 i 4 | J2 4.3 (z W3) | SL3 x = 6,44 = SL5; SL4 x = 8,78 = SL6. O0-01…O0-05: 1,90 / 1,90 / 2,34 (HS1) / 2,34 (HS1) / 2,92 m | ✓ |
| lekka rama stalowa C | J2 4.4 (z W1) | PL-C1/PL-C2 z materiału `RAMA_C` na konsolach z przekładką (WZ-14). Pas górny sięga do x = 13,45 | ✓ |
| HS salonu 2,40 × 2,75 na taras zach. pod okapem 1,50 m | J2 4.5 (z W1/W3) | O0-11 HS2 2,40 × 2,75 m. Okap PL-E wysunięty 1,50 m na zachód | ✓ |
| przeszklone drzwi gospodarcze w systemie fasady E | J2 4.6 (z W1) | O0-06 DZ3 0,90 × 2,75 m pod okapem; pas E czytany ≈ 12,85 m | ✓ |
| pas komunikacyjny 1,20 m przy schodach, ekran lamel h 2,10 m | J1 5.2 / 6.7 (z W3) | 0.07: 3,51 m². Od lica ekranu LAM-P0 do lica ściany osi 3 jest ≈ 1,20 m, ale wielobok pomieszczenia ma 1,17 m | ✓ |
| szklana ścianka wiatrołap/hol | J1 5.3 (z W3) | S0-21 (SGL) z drzwiami DS1; doświetle FX3 przy DZ1 | ✓ |
| ciąg kuchenny na ścianie osi E + wyspa | J1 5.4 (z W1) | blat y 1,40–5,02 (3,62 m) i wyspa 2,20 × 1,00 m; drzwi O0-21 przy fasadzie | ✓ |
| pralnia ≈ 6,6 m² + osobne WC z prysznicem | J1 5.6 (z W3) | 1.08: 6,64 m²; 1.07 WC z natryskiem: 4,08 m² | ✓ |
| szafa na rowery i sprzęt ogrodowy w garażu | J1 5.8 (z W1) | szafa 2,40 × 0,60 m przy ścianie osi F, y 6,8–9,2. Kolizja z bramą — §6 poz. B2 | ⚠ |
| spiżarnia pod biegiem 2; pom. techniczne 8,85 m² dostępne z domu | J2 5.2 | 0.05: 5,40 m² netto, zaliczona 2,70 m² (lub 1,72 m² — §2). 0.12: 8,85 m², drzwi D4 z przedsionka 0.11 | ✓ |
| klatka poszerzona: bieg 1,15 m, szerokość użytkowa ≥ 1,05 m | J1 6.2 | biegi 1,15 / 1,145 m. Od lica ściany C (x 5,98) do wewnętrznej krawędzi pochwytu BL1 (x 7,059 − Ø42/2) jest ≈ 1,06 m ≥ 1,00 m (W-091). 2h + s = 0,63 m | ✓ |
| ściany żelbetowe trzonu schodów na P0 (warunkowo) | J2 4.7 / 5.6 | S0-12 i S0-13 z przegrody SWZB. Potrzeba nadal wynika tylko z założenia (mimośród sztywności) — obliczenie jest w PT | ✓ (warunkowo) |
| PU wg W-316 bez klatek i podestów | J1 6.5, J2 5.7 | §9 = 240,24 m² | ✓ |
| odwodnienie dachów: wpusty z grzałką, przelewy awaryjne, rury w SI | J2 5.1 | D1: 2 wpusty, 3 przelewy; D2/D3: po 1 i 1; D4: 2 i 2. Rury RS1/RS2 w SI. Dno przelewów D1 leży za nisko — §6 poz. A3 | ⚠ |
| czerpnia dachowa ≥ 0,40 m nad pokryciem i ≥ 6,0 m od wywiewek, wykazana na rzucie dachu | J1 6.6 | odległości spełnione (czerpnia–K1 7,8 m, czerpnia–wyrzutnia 9,81 m), ale Δz wyrzutni wynosi 0,05 m (§6 poz. A1). Na rzucie dachu PB-AR-04 nie narysowano czerpni, wyrzutni ani K1 | ✗ |
| niskie parapety P1/P2: stała część VSG do 0,85 m | J1 6.8 | BC1, OP1, OP3: tak (opisy stolarki). Skrzydła P2 otwierane do wewnątrz (W-098) | ✓ |
| docieplenie spodu stropu garażu pasem 1,0 m; U dachu nad pasem ≤ 0,15 | J2 5.4 | SUF-G (wełna 10 cm); DZ1 U = 0,13 | ✓ |

## 5. Podglądy wykonane w ramach weryfikacji (`docs/20_koncepcja/final/`)

Pliki z tej weryfikacji mają przedrostki `arkusz_*`, `pzt_*` i `3D_*`. Nie zastępują podglądów syntezy
(`rzut_*`, `elewacja_*`, `przekroj_*`, `dzialka.png`, `bilans.*` z `tools/podglad_modelu.py`) — uzupełniają je o pełne arkusze PB w skali,
koncepcyjny PZT i widoki 3D. Wszystkie powstały ze stanu modelu opisanego w nagłówku.

### 5.1 Arkusze architektury `arkusz_01…10_*.png`

`tools/generuj_widoki.py`, PNG 170 dpi, skala rysunku 1:50. Każdy arkusz ma kolumnę opisową, tabliczkę, legendę materiałów
(PN-B-01030) i podziałkę. Raport QA: 10/10 arkuszy OK, 0 błędów. Jedyne ostrzeżenie dotyczy pustego pola „projektant” w tabliczce
**[DO UZUPEŁNIENIA: imię, nazwisko i nr uprawnień projektanta]**.

| plik | format arkusza | co przedstawia |
|---|---|---|
| `arkusz_01_rzut_P0.png` | A1 | Rzut parteru, cięcie +1,10. Widoczne: przeszklenie E (FX1/FX1/HS1/HS1/FX2) na słupach SL1–SL4; HS2 na taras zachodni; kuchnia z ciągiem na ścianie osi E i wyspą; pas 1.07 za ekranem lamel (linia punktowa); klatka z biegiem 1 i biegiem 2 nad spiżarnią; wiatrołap ze ścianką VSG; przedsionek gospodarczy z drzwiami DZ3, DG1 i D4; pomieszczenie techniczne z modułem PC, zasobnikiem 300 dm³ i buforem; garaż 6,05 × 6,175 m w świetle z bramą BR1 i drzwiami DZ2. Są też obrysy płyt PL-E i PL-DA oraz tarasu T1 (linie kreskowe), osie A′…F i 1…5, łańcuchy wymiarowe i zestawienie pomieszczeń. Numeracja na arkuszu to ISO (parter = 1.xx) — §6 poz. C3 |
| `arkusz_02_rzut_P1.png` | A3×3 | Rzut I piętra: hol 1.01 wzdłuż osi 3 z galerią OT2 2,40 m do pokoju rodzinnego (28,36 m²); boks C (BC1, 3 kwatery 2,34 m) z ramą wysuniętą 1,00 m (boki SL7/SL8); pokoje dzieci 13,19 i 12,52 m² z oknami zachodnimi; łazienka dzieci i WC z natryskiem w pionach SI/K2; pralnia 6,64 m². Kreskami zaznaczono dach garażu D4 i daszek wejścia |
| `arkusz_03_rzut_P2.png` | A3×3 | Rzut II piętra (bryła A): apartament rodziców, czyli sypialnia 21,43 m² nad wspornikiem, garderoba-przedpokój 10,57 m² i łazienka w nadbudowie; hol 2.01; pom. techniczne z centralą i wyłazem WYL1; gabinet 16,32 m² (S + E). Zaznaczono ścianę lekką A′, lamele (linia punktowa przed licem pd.) i dachy D2/D3 przy nadbudowie |
| `arkusz_04_rzut_dachu.png` | A2×3 | Rzut dachów D1–D4: spadki 2 % ze strzałkami, wpusty (WD), świetlik SW1, wyłaz WYL1, rzędne pokrycia i attyk (+9,526/+9,776; +6,410/+6,660; +3,305/+3,850), obrysy płyt PL-2/PL-3/PL-E. Brakuje PV, czerpni, wyrzutni i wywiewki K1 (§6 poz. A1, A4, C1). Opisy warstw nachodzą na siebie. Arkusz jest w ok. 55 % pusty |
| `arkusz_05_przekroj_A-A.png` | A3×3 | Przekrój A-A, x = 6,55, patrz na E. Pokazuje trzy kondygnacje po 3,15/3,15/3,00 m, wysokość w świetle 2,77 m, schody SCH1/SCH2 ze spocznikami +1,575 i +4,725, spiżarnię 1.05 (h 1,90) pod biegiem, stropodach D1 z attyką, płytę fundamentową na XPS, a od południa okap PL-E (+2,75…+3,05), ramę C (+3,65…+5,55), PL-2, PL-3 i lamele. Opisano warstwy SD1, POD-1, SZ1 i OK1. Nota: H wg WT §6 = 9,79 m |
| `arkusz_06_przekroj_B-B.png` | A3×3 | Przekrój B-B, y = 3,30, patrz na N. Wspornik bryły A 1,00 m (B3/B4) z płytą PL-2 1,10 m, strefa dzienna z ekranem lamel w widoku, pokoje P1 i P2, garaż z dachem zielonym DZ1 (warstwy opisane), attyka +3,85 |
| `arkusz_07_elewacja_S.png` | A3×3 | Elewacja ogrodowa. Sylweta „S”: A w lamelach (wysunięta na zachód) → B pełna z boksem C w ciemnej ramie → E przeszklona pod okapem 1,50/1,00 m → blok G z drzwiami gospodarczymi. Linia D (+3,85) łączy dolny pas ramy C z attyką garażu. Legenda kolorystyki: biel/jasnoszary NCS S 1500-N, antracyt RAL 7016, drewno termo (MPZP, W-037) |
| `arkusz_08_elewacja_N.png` | A3×3 | Elewacja od ulicy: brama garażu 5,00 × 2,25 m, wejście pod daszkiem z doświetlem, małe okna pomieszczeń pomocniczych, nadbudowa klatki z oknem ON4, attyki D2/D3. Na obu końcach widać lamele i okapy bryły A |
| `arkusz_09_elewacja_E.png` | A2 | Elewacja wschodnia: ściana garażu z drzwiami DZ2, okno OE1 pokoju rodzinnego ponad attyką garażu, bok ramy C, lamele LAM-E i okno OP2 gabinetu, nadbudowa |
| `arkusz_10_elewacja_W.png` | A2 | Elewacja zachodnia: HS2 i OZ1 na parterze, dwa okna OZ1 pokoi dzieci, wspornik A z lamelami LAM-W i oknem OP3 za nimi, okapy PL-E (1,50 m), PL-2 i PL-3, bok ramy C |

### 5.2 PZT koncepcyjny `pzt_koncepcja.png`

Skrypt matplotlib czytający wyłącznie `dzialka.yaml` i `budynek.yaml`; A3 poziomo, 170 dpi, podziałka graficzna. Rysunek przedstawia:
* działkę 32,00 × 50,00 m, sąsiednie działki i budynki, drogę 1KDD z jezdnią, linię zabudowy 6,00 m;
* budynek: rzut P0 jako powierzchnię zabudowy, wspornik A, obrysy P1/P2, płyty wysunięte, dach zielony garażu;
* taras T1, podesty, podjazd U1 z MP3/MP4, MP1/MP2 w garażu, dojście, stanowisko pojemników;
* opaskę żwirową, odwodnienia liniowe, niecki trawiaste, zbiornik 5,0 m³, nieckę chłonną 24 m²;
* jednostkę PC z ramką strefy R290, SK-PC, ZKP, SR1;
* sieci istniejące i projektowane (woda, kanalizacja sanitarna i deszczowa, nN, teletechnika; gaz nieużywany);
* ogrodzenie z bramą przesuwną i furtką, drzewa (projektowane i zachowane);
* rzędne narożników działki;
* wymiary do granic: W 7,30 / 6,30 / 5,20 / 4,30 m, E 5,73 m, N 7,62 m, daszek 0,95 m za linią zabudowy, PC 6,90 m od granicy E.

Kolumna opisowa zawiera wskaźniki z §2 i legendę. To podgląd koncepcyjny, a nie PZT na mapie do celów projektowych (W-022).
**[DANE PRZYKŁADOWE – FIKCYJNE]**.

### 5.3 Widoki 3D `3D_*.png`

Rendery pipeline'u `lamela.pipeline` (glTF → three.js w Chromium /opt/pw-browsers/chromium), 2000 × 1250 px, słońce dla Poznania
(`lamela.sun`):
* `3D_aksonometria_rozwarstwiona.png` — aksonometria z rozsuniętymi kondygnacjami P0, P1, P2 i dachem, z etykietami (21.03, 12:00). Widać układ wnętrz, klatkę na wszystkich poziomach, dach zielony garażu w warstwie P1, świetlik i wyłaz;
* `3D_widok_lotniczy_SE.png` — widok lotniczy od płd.-wsch.: sylweta „S”, taras L, blok G z dachem zielonym, ogrodzenie i żywopłoty, sąsiedzi;
* `3D_widok_od_ulicy_N.png` — widok z ul. Lipowej (21.06, 19:30): brama garażu, wejście pod daszkiem, ogrodzenie ażurowe, osłona pojemników.

Rendery (glTF 58 500 trójkątów) wygenerowano ze stanu modelu z nagłówka. Przy każdej zmianie modelu trzeba je wygenerować ponownie (Aneks A).

## 6. Błędy i niespójności (do audytu i poprawek)

Kategorie:
* **A** — niezgodność z wymaganiem; wymaga zmiany modelu przed PAB;
* **B** — decyzja projektowa do podjęcia;
* **C** — błąd rysunkowy, narzędziowy albo niespójność dokumentów.

Źródło każdej pozycji podano w nawiasie. Modelu nie zmieniano.

### A — niezgodności z wymaganiami

1. **Czerpnia a wyrzutnia na dachu** (moduł fizyki, `07_wentylacja`).
   * Wyrzutnia (+10,00) jest tylko 0,05 m wyżej od czerpni (+9,95). Przy wyrzucie pionowym wymagane jest ≥ 1,0 m albo zestaw zblokowany (WT §152, W-167). Odległość 9,81 m jest poprawna (≥ 6 m).
   * Podniesienie wyrzutni do +10,95 dałoby wysokość zabudowy 101,65 + 10,95 − 101,404 = **11,20 m > 11,00 m** (MPZP, W-033).
   * Możliwe rozwiązania:
     * czerpnia na dachu D2/D3, ≈ +6,8, czyli ≥ 0,40 m nad pokryciem (Δz ≈ 3 m); sprawdzić ≥ 6 m od K1 i od wyrzutni;
     * czerpnia ścienna wg W-166: ≥ 8 m od ulicy, pojemników i wywiewek, dolna krawędź ≥ 2 m nad terenem;
     * certyfikowany zestaw zblokowany.
   * Zgodnie z poprawką J1 nr 6 czerpnia, wyrzutnia i K1 mają być na rzucie dachu. Na PB-AR-04 ich nie ma.
2. **Spadki terenu od budynku** (moduł drenażu).
   * Wymagane ≥ 2 % na 1,5–2 m (W-019, brief §9.6). Moduł liczy teren od lica do punktu 2 m dalej i dostaje na wszystkich ścianach tylko 0,2–1,1 %.
   * Punkty projektowane w `dzialka.yaml` mają 101,35 w pasie 0,5 m i 101,32 w pasie 2,0 m od lic. Daje to 2 % tylko między tymi pierścieniami, a przy licu TIN interpoluje rzędne istniejące.
   * Trzeba dodać punkty przy cokole, np. +0,02–0,03 wyżej niż pierścień 0,5 m.
3. **Przelewy awaryjne D1** (moduł deszczowy).
   * Dno przelewów leży 0,01–0,05 m **pod** pokryciem przy wpuście, a wymagane jest ≥ 0,03 m nad nim (W-142; J2 poprawka 5.1: 30–50 mm).
   * W tym stanie przelew działałby jak główny odpływ zamiast wpustów WP1/WP2.
4. **PV ponad attyką** (moduł PV).
   * Stelaże dają górną krawędź modułów 0,30 m nad pokryciem, attyka ma 0,25 m. Moduły wystają więc o 0,05 m (W-033, D-15).
   * Uwaga w `energia.pv` („≤ +9,78”) i tekst §7 („nie wyżej niż attyka”) są z tym sprzeczne.
   * PV nie ma ani na rzucie dachu, ani w 3D.
5. **Cokół** (moduł deszczowy/drenażowy).
   * Minimalna wysokość to 0,14 m, przy drzwiach DZ2 garażu (strona wsch., teren wyższy). Wymagane ≥ 0,30 m albo odwodnienie liniowe przy drzwiach (brief §9.4).
   * Odwodnienia OL-* obejmują HS, wejście i bramy, ale nie DZ2.
6. **Doświetle FX3** (moduł fizyki).
   * Obliczone U_w = 1,0 > 0,9 W/(m²K) dla okna (WT zał. 2 pkt 1.2, W-244), przy deklaracji 0,85.
   * Rozwiązania: zmienić profil albo zestawić FX3 jako część drzwi DZ1 (U ≤ 1,3).
7. **Moc ogrzewania podłogowego** (moduł ogrzewania; PN-EN 1264; W-153).
   * Przy θ_V = 35 °C brakuje mocy w łazienkach i WC: 0.03, 0.09, 1.05, 1.07, 2.04. Deficyt 98–312 W oznacza grzejniki drabinkowe.
   * Brakuje też w pomieszczeniach 2.02 (−308 W), 2.05 (−312 W), 0.06 (−276 W) i 0.11 (−113 W).
   * Przyczyną jest m.in. Φ_HL liczone z domyślnymi Ψ (poz. B4).
   * Moc nominalna PC dobrana przez moduł to 12,2 kW **[DO UZUPEŁNIENIA: dobór PC po symulacji Ψ i wg DTR wyrobu]**.

### B — decyzje projektowe

1. **Odwodnienie płyt wysuniętych.** Dotyczy PL-E (≈ 16 m, wysięg 1,00/1,50 m), PL-2, PL-3 (+9,40), PL-C1/C2 i daszka PL-DA.
   * Mają spadek 2 % od budynku i okapnik, bez rynien. Moduł deszczowy zgłasza brak wpustów.
   * Linia kapania wypada nad tarasem T1, nad krawędzią podestu wejścia T2 (daszek i podest mają po 1,30 m, więc ryzyko oblodzenia przy wejściu) i nad podestem T3.
   * Do rozstrzygnięcia: rynna ukryta w krawędzi albo odwodnienie liniowe pod linią kapania (brief §9.3).
2. **Szafa na rowery w garażu** (x 17,67–18,27, y 6,8–9,2).
   * Czoło szafy wchodzi 0,08 m w światło bramy (krawędź BR1 x 17,75), a szafa kończy się 0,07 m przed licem ściany z bramą. Koliduje to z prowadnicą bramy segmentowej.
   * W strefie przedniej szerokość garażu w świetle spada do 5,45 m < 5,60 m (W-112).
   * Propozycja: skrócić szafę do y ≤ 8,6 m i zmniejszyć głębokość do ≤ 0,45 m albo przenieść ją na ścianę osi 2 poza tor jazdy.
3. **EP zależy od PV i od Ψ.**
   * EP = 57,2 przy Ψ domyślnych (H_TB = 137,6 W/K, ΔU_TB = 0,225 W/(m²K)).
   * Bez PV EP = 81,8 > 70. PV 6,45 kWp jest więc warunkiem spełnienia W-240, a nie opcją.
   * 16 węzłów czeka na symulację PN-EN ISO 10211 (brief §9.2, W-248). Z Ψ „dobrej praktyki” EP spada do 40,8.
4. **Obciążenie cieplne 11,48 kW (43,7 W/m²)** jest wysokie jak na U ≤ 0,17. Dominują Ψ domyślne: attyki 0,75, cokół 0,80, ST2Z 0,60. Dobór PC i ogrzewania (A7) powtórzyć po symulacji węzłów.
5. **Wentylacja.** Strumień projektowy wynosi 407 m³/h, a w trybie intensywnym 477 m³/h. Centrala ma 450 m³/h, więc zapas nominalny to ok. 10 %, a tryb intensywny go przekracza. Sprawdzić dobór (W-161…W-164).
6. **Retencja.** Niecka ma 6,75 m³ przy V_min 6,65 m³ (zapas 1,5 %; W-143). Zalecane powiększenie niecki do ≥ 26 m². Pogłębianie odpada, bo W-145 dopuszcza ogród deszczowy o głębokości ≤ 0,30 m.
7. **Elektryka** (moduł obwodów, etap PT):
   * prąd najbardziej obciążonej fazy 40,2 A > 40 A (W-192);
   * spadek napięcia na WLZ 0,61 % > 0,50 % (W-185);
   * spadek napięcia DC w PV 1,03 % > 1,00 % (W-194).
8. **Uskok podsufitki wspornika A.** Spód docieplenia IZ-ST2Z (+5,73) leży 0,22 m niżej niż spód płyty PL-2 (+5,95). Na elewacji W widać go jako gzyms pod okapem. Rozstrzygnąć detal (wyrównanie spodu albo świadomy uskok) i narysować podsufitkę.
9. **Zalecenia nieobowiązkowe J2/J3, niezrealizowane:**
   * gabinet/pokój 5. osoby na P2 nie ma łazienki dostępnej inaczej niż przez apartament;
   * pom. techniczne 2.07 zajmuje ok. 2,6 m elewacji pd. za lamelami (J2 poz. 8).
10. **Widok od ulicy.** Na elewacji N dominuje pełny tynk z sześcioma małymi oknami (J3: katalog „sprzedaje się widokiem od ulicy”). W renderze `3D_widok_od_ulicy_N.png` ogrodzenie stoi na jasnym cokole — potwierdzić, że to nie prefabrykat betonowy (MPZP, W-038).

### C — rysunki, narzędzia, spójność dokumentów

1. **PB-AR-04 (rzut dachu).**
   * Brakuje: PV, czerpni, wyrzutni, wywiewki K1, strefy obsługi PV i drogi od wyłazu.
   * Opisy warstw D2/D1/D4 nachodzą na siebie i wychodzą poza pola dachu.
   * Arkusz A2×3 jest w ok. 55 % pusty (lepszy byłby A2 albo A3×3).
2. **Wełna IZ-ST2Z widoczna jako żółty pas.**
   * Widać ją pod wspornikiem A na PB-AR-07/08/10, w `elewacja_S_szkic.png` i w 3D (kolor wełny #efe3b0), bo podsufitka PODSUF istnieje tylko jako warstwa SUF-ZEW, a nie jako element.
   * Na PB-AR-09 pod lamelami LAM-E (od +6,20) widać czarny pas membrany ściany (od +6,15).
3. **Numeracja pomieszczeń.**
   * Arkusze (`arkusze.yaml`: `numeracja_pomieszczen: iso`) numerują parter 1.xx, I p. 2.xx, II p. 3.xx. Model i `koncepcja.md` używają 0.xx/1.xx/2.xx.
   * Ten sam numer oznacza więc różne pomieszczenia: „1.06” to salon na PB-AR-01, a klatka P1 w koncepcji.
   * Ujednolicić albo dodać do opisu tabelę przejścia.
4. **„Użytkowa” w zestawieniach pomieszczeń na arkuszach** (np. PB-AR-01: 115,94 m²) i „PU” rdzenia (`zestawienie_powierzchni()` = 237,36 m²) to podstawowa + pomocnicza **z garażem i bez komunikacji**. To nie jest PU wg W-316 z §9 (240,24 m²). Zmienić etykietę albo definicję.
5. **Wysokość wg WT §6.** Arkusze (nota PB-AR-05…10) podają 9,79 m, §9 podaje 9,85 m. Różnią się przyjętym „terenem przy najniższym wejściu” (−0,267 i −0,326). Ujednolicić definicję: wejście główne, brama garażu czy drzwi DZ2.
6. **Posadzka garażu.** Model ją ma na −0,10 (warstwy POD-G na płycie −0,15, uwaga O0-07, §5 koncepcji). PB-AR-01 i przekrój B-B opisują ją jako „±0,000”, a zestawienie podaje wysokość 2,76 m.
7. **Kolizje napisów na PB-AR-01.**
   * Opisy drzwi DG1 i D4 nachodzą na siebie.
   * Opisy „wodomierz + zawór antyskażeniowy (PN-EN 1717)” i „rozdzielnica główna RG” wychodzą poza ściany pomieszczenia 0.12.
8. **U w nazwach przegród modelu i w tabeli §6 koncepcji** są niższe od obliczonych (tabela w §3). SZ1 i SZ2 nie osiągają celu projektowego 0,15 (W-245).
9. **Tekst koncepcji wobec modelu:**
   * §6 „teren ze spadkiem ≥ 2 %” i „cokół ≥ 0,30 m” — zob. A2 i A5;
   * §7 „PV nie wyżej niż attyka” — zob. A4;
   * §7 czerpnia i wyrzutnia „W-166/W-167” — W-167 niespełniony (A1);
   * §8 „PC 7,0 m od granicy E” — 6,90 m od krawędzi fundamentu, 7,60 m od środka urządzenia (wymóg spełniony);
   * §9 PBC 1 281,57 m² wobec 1 271,31 m² w weryfikacji (różnica metody, poz. §2).
10. **Wcześniejsze liczby syntezy.**
    * PU 241,07 m² — obecny model daje 240,24 m².
    * Wysokość 10,02 m — to wartość do attyki. W-033 wlicza urządzenia dachowe, więc właściwa wartość to 10,25 m (tak podaje §9), a do PV 10,07 m.
    * Pow. zabudowy 187,51 m² — dokładnie 187,50 m².
11. **Narzędzia.**
    * `lamela.obliczenia.sanitarne.deszczowa` traktuje wszystkie `wsporniki_plyty` jako pola dachu. Alarmy „brak wpustów” dla IZ-ST2Z, SW1 i WYL1 są fałszywe; dla PL-* zob. B1.
    * `raport_obciazenie` kończył się `ZeroDivisionError` dla pomieszczenia o powierzchni 0 m² (klatka 1.06 we wcześniejszym stanie modelu).
    * Brak generatora arkusza PZT z modelu: plugin `lamela.views.site` z `VIEW_PLUGINS` nie istnieje. `pzt_koncepcja.png` jest podglądem skryptowym.

## Aneks A. Odtworzenie wyników (z katalogu repozytorium, `PYTHONPATH=src`)

```bash
python3 -m lamela.model model/budynek.yaml model/dzialka.yaml                     # walidacja + powierzchnie rdzenia
python3 tools/generuj_widoki.py --out <katalog> --formaty png --dpi 170 --bez-tomu  # arkusz_01…10 (kopie PB-AR-01…10)
python3 -m lamela.pipeline --budynek model/budynek.yaml --dzialka model/dzialka.yaml --out <katalog> --views ade --size 2000x1250
python3 -m lamela.obliczenia.fizyka_energia --budynek model/budynek.yaml --dzialka model/dzialka.yaml --out <katalog>
python3 -m lamela.obliczenia.instalacje --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
    --wyposazenie model/wyposazenie.yaml --instalacje model/instalacje.yaml --phi-hl energia --wentylacja energia --out <katalog>
```

PU wg W-316 (konwencja modelu) — ten sam wynik co §9:

```python
from lamela.model import load_model
m = load_model("model/budynek.yaml", "model/dzialka.yaml", strict=True)
wyl = {"0.04", "1.06", "2.06", "0.13"}                     # klatki (W-316) i garaż (osobno)
pom = [r for k in ("P0", "P1", "P2") for r in m.pomieszczenia(k)]
pu = sum(r.pow_zaliczona for r in pom if r.id not in wyl and r.kategoria != "techniczna")
print(round(pu, 2), m.pow_zabudowy()["budynek"], m.kubatura_brutto()["razem"])   # 240.24 187.5 1354.5
```
