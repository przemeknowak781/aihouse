# Weryfikacja: KOSZT, EKOLOGIA, ELEWACJE – „Brama i Latarnia” (synteza 1.0)

**Przedmiot:** `docs/20_koncepcja/koncepcja_wybrana.md` (rozdz. 2, 4.4, 5, 8, 9, 10, 12, 15) i `model/koncepcja.json` (`elewacje`, `bilans`, `zagospodarowanie`, `kondygnacje_biurowe`).
**Data:** 17.11.2026. Weryfikator niezależny (adwersaryjny). Specyfikacji ani JSON nie zmieniano.
**Podstawy:** brief `00_brief_projektowy.md`; `tools/koszty_model.py` (mid, II kw. 2026); `50_research/koszty_benchmarki.md`; `50_research/elewacje_zasady.md` (E01–E29); `40_prawo/strategia_energetyczna.md`, `zero_emisja.md`, `_bilans_energii.py`; `30_lokalizacja/mpzp.md`; `model/site.json`, `sasiedzi.json`. Nie korzystano z informacji o rzeczywistych pracach ani wynikach konkursu.
**Dowód:** `docs/20_koncepcja/_weryfikacja_koszt_eko.py` (`python3 -I docs/20_koncepcja/_weryfikacja_koszt_eko.py --cien`, ok. 20 s). Wszystkie liczby „(skrypt)” pochodzą z tego pliku.
**Skala wag:** KRYTYCZNY – narusza twardy wymóg (limit 150 mln, minimum M.12, MPZP, WT) albo deklaracja jest niewykonalna w przyjętej bryle; ISTOTNY – błąd liczbowy lub luka, która zmienia rysunki, tabele lub hasła plansz, ale nie zmienia koncepcji; DROBNY – niespójność lub drobna liczba.

---

## 0. Zestawienie

| ID | Waga | Błąd (skrót) | Gdzie |
|---|---|---|---|
| K-1 | **KRYTYCZNY** | Po korekcie ilości koszt mid wynosi **150,8–151,7 mln > 150**. Ilości elewacji pominęły ościeża filarów wieży (≈ 1 100 m² granitu) i ościeża okien skrzydła (≈ 670 m²). Model nie zawiera pali CFA ani ściany na uskoku −1/−2. „Dźwignie 1,6 mln” są w rzeczywistości warte 0,57 mln | 2 (17), 12, 16.5; JSON `bilans` |
| K-2 | **KRYTYCZNY** | PV 412 kWp jest nieosiągalne. Dach skrzydła ma 780 m² BIPV przy wnętrzu 775 m², a dach wieży 1 040 m² przy 1 080 m² (96 %). Płyciny od dziedzińca ≤ 25 m mają najwyżej ≈ 92 m², a nie 318 m². Nie uwzględniono cienia wieży na dachu skrzydła (−11,4 %). Realnie wychodzi **≈ 328 kWp < 400 kWp (M.12)**, 272 MWh/rok, EP ≈ 33,5, a nie 26 | 2 (20), 8, 10, 15; JSON `elewacje.PV` |
| I-1 | ISTOTNY | Brak miejsca na dry-cooler hybrydowy. Jest niezbędny dla szczytu chłodu ≈ 600 kW (GPC daje 330 kW) i nadwyżki 165 MWh/rok. W strategii stał na piętrze technicznym, które synteza usunęła; dach i elewacje od ulic są wykluczone (MPZP § 6 pkt 13) | 10 |
| I-2 | ISTOTNY | Pole 75 sond × 99 m nie ma lokalizacji. Przy siatce 6 × 6 m zajmuje 2 700 m², a podziemie ma 2 337 m². Wiercenie z dna −2 sięga 107 m p.p.t., czyli zagraża reżimowi art. 86 PGiG, który spec. deklaruje ominąć. Dochodzi 75 przepustów przez białą wannę | 5, 10 |
| I-3 | ISTOTNY | Lokalizacja urządzeń i otworów technicznych niekompletna (MPZP § 6 pkt 13): spaliny i powietrze agregatu, wentylacja trafo w elewacji od bulwaru, wyciąg bistro, piony czerpni i wyrzutni (≈ 6–7 m²/kond.), czerpnia na tych samych płycinach co BIPV, garaż (por. geometria D-11) | 6, 8, 10 |
| I-4 | ISTOTNY | Agregat HVO i pompownia tryskaczowa leżą na −2 (112,30), 6,7 m pod poziomem sytuacji wyjątkowej 119,0. To sprzeczność z korektą (d) i z briefem („technika krytyczna nad poziomem zalewu”) | 2 (d), 6 |
| I-5 | ISTOTNY | Okno skrzydła 1,20 × 2,40 przy parapecie 0,90 ma nadproże 3,30 m, a spód stropu leży na 3,20 m. Bez kasety ZIP i tak brakuje 0,10 m. W wieży przy parapecie 0,85 nie mieści się kaseta ZIP | 4.2, 8 |
| I-6 | ISTOTNY | Deklarowane U = 0,15 nie wynika z warstw (wełna 200 mm λ 0,033 na ruszcie Al). Wychodzi U0 0,156, a z konsolami 0,18–0,23 przy wymaganiu WT ≤ 0,20 | 8 (tabela 1:50), 10 |
| I-7 | ISTOTNY | Lamele korony 0,25 × 0,60 co 0,90 m tworzą regularny, kontrastowy rytm o okresie 0,9 m, widziany z mostu z odległości 80–200 m (1,6–3,9 c/°). Narusza to E19. Kąt pełnego przesłonięcia wynosi 47,3°, a nie 34° | 2 (5), 8 |
| I-8 | ISTOTNY | „Metoda 2” nie jest niezależna (stawki [Z] skalibrowano na to samo pasmo). Brak miary zł/m² PU, która wynosi 17 400–18 100 przy paśmie 11 400–14 900. Waloryzacja liczona od 144,2 zamiast od kosztu całkowitego | 12 |
| I-9 | ISTOTNY | „Zero odpływu”: zbiornik rozsączający 60 m³ nie ma lokalizacji. Grunt to nasypy niebudowlane (gruz), ZWG maks. 116,45 (≈ 2,8 m p.p.t.), strefa podtopień. Brak warunku dna ≥ 117,45 i badania infiltracji | 2 (22), 9, 10 |
| D-1…D-16 | DROBNY | rozdz. 4 | |

---

## 1. Kontrole spełnione (dowód liczbowy)

* **PC i KW:** 2 003,1 + 4 × 2 160,2 + 3 × 1 145,8 + 69,7 = 14 151,0 m² ✔. KW 42 162 + 17 368 + 3 490 + 8 765 + 6 204 = 77 989 m³ ✔. Elewacje 6 880 m² ≈ geometria bryły (≈ 6 930 m²) ✔. A/V = (6 880 + 2 160 + 2 163) / 63 020 = 0,178 ✔.
* **Model kosztów odtwarzalny:** parametry jawne dają **144,35 mln** (skrypt). Po dopasowaniu 7 parametrów nieujawnionych (h_pod 6,5; drogi 0; ogrodzenie 0; balustrady 60/125 mb; okna wewn. 142,5 m²; drzwi zewn. 106 m²) wychodzi **144,18 mln**, a grupy zgadzają się z tabelą 12 co do 0,01 mln ✔. Suma tabeli 12 = 144,17 ✔.
* **Parametry podziemia:** obwód −1 = 244,6 m ✔, obrys 2 337,2 m² ✔, −2 = 1 426,2 m² ✔. Wykop średnio 6,49 m (spec. 6,9: zawyżenie ok. 0,08 mln) i beton płyt 2 389 m³ (model 2 571: zawyżenie ok. 0,25 mln) działają na korzyść spec. Obie wielkości uwzględniono w korekcie K-1.
* **Brak podwójnego liczenia zieleni i PV:** dachy zielone ma tylko taras segmentu. W modelu kosztów dach_ext = 0, a dach_int = 167. PBC 1 170 m² nie obejmuje dachów BIPV ✔.
* **Retencja – arytmetyka:** model I MPWiK (H60, C10 = 30,44 mm; q15 = 204,7 dm³/(s·ha)). Ψ 0,673 → 0,634 dla 1 993 m² dachów BIPV (0,95), 167 m² tarasu, 430 m² nawierzchni i 1 139 m² zieleni. Qdm 51 → 47 dm³/s ✔. V60 = 30,44 × 0,62 × 3 729 / 1 000 = 70 m³ ✔. Pojemność 60 + 20 + 42 + 10 + 19 = 151 m³ = 2,16 × V60 ✔.
* **Woda – arytmetyka:** szara (403 × 5 + 30 × 40) × 250 = 804 m³ ✔. Deszczowa 1 652 m² × 0,8 (zredukowane) × 0,57 × 0,9 = 848 m³ ✔. Pokrycie spłukiwania min(1 435; 804 + 0,75 × 848) = **100,4 %** ✔ (na granicy, D-11). Redukcja 1 606 / 3 443 = 46,6 % ✔.
* **EPB i EP metodą `_bilans_energii.py`:** EPB 23,9 kWh/m² (5,56 + 1,33 + 3,48 + 5,0 + 2,0 + 6,5) ✔. Af = 297 / 23,9 = 12 427 m². EP bez PV = 23,9 × 2,5 = 60 ✔. Przy PV 347 MWh EP = 26,2 ✔. Wynik jest poprawny arytmetycznie, ale opiera się na zawyżonym PV (K-2).
* **GPC – moc:** 75 × 95 m czynnych × 45 W/m = 321 kW poboru, co daje ≈ 430 kW grzania (COP 4) ✔. 7 425 mb = mb_odw w modelu ✔.
* **Elewacje – linie kontekstu:** E05 – spód gzymsu 139,45 = 118,51 + 20,94 (Maz. 19: 20,98) ✔. E06 – naświetle 122,77 = pas Maz. 19 ✔. E07 – attyka 140,15 przy 140,24 Maz. 19 (±0,15) ✔, kordon 124,10 przesunięty o 1,33 m (≥ 0,6) ✔. E02 – 4 posesje 12,15–16,20 m ✔. E14 – WWR 37,9 % (skrzydło) i 40 % (wieża) ✔. E20 – 2 materiały mineralne + metal ✔. E22 – R ≤ 12 %, ochrona ptaków ✔. E28 – ≤ 5 lx ✔.
* **Niepalność powyżej 25 m:** granit A1 na kotwach nierdzewnych, ceramika A1, aluminium, wełna mineralna, lamele ceramiczne na stali. Okładziny, mocowania i izolacje powyżej 25 m są niepalne ✔. Uwagi dotyczą tylko deklaracji BIPV i rolet ZIP (D-6).
* **Centrale wentylacyjne nie stoją na dachu ani na elewacjach od ulic** ✔: 5 × 25 m² w strefie środkowej wieży (kond. 1–5) oraz centrale P i S na −1. Luki dotyczą innych urządzeń (I-1, I-3).

---

## 2. Błędy KRYTYCZNE

### K-1. Koszt po korekcie ilości przekracza 150 mln (mid)

**Dowód (skrypt, mid, netto, II kw. 2026):**

| Krok | mln zł |
|---|---:|
| A. Spec. odtworzona (144,18) + korekty 2,0 objęte KS 3 % i rezerwą 5 % (spec. dolicza je poza KS i rezerwą: −0,16) | 146,34 |
| B. Korekta ilości: wykop 6,49 m; płyty 2 389 m³; PV wg K-2 (BIPV elew. 400 m², PV dach 351 kWp). Do tego pozycje spoza modelu [Z]: **pale CFA 36 × Ø0,8 × 14 m** (rozdz. 5, brak w modelu) +0,60; **ściana na uskoku −1/−2** o długości 38,1 m (shapely: obwód −2 poza obwodem −1) × 7,5 m +0,39; dry-cooler hybrydowy 2 × 150 kW (I-1) +0,49; wiercenie GPC z dna wykopu i przepusty w białej wannie (I-2) +0,81 | **148,29** |
| C. B + **ościeża pominięte w ilościach elewacji** | **151,72** (stawki modelu) / **150,78** (granit 1 600, okładzina Al 800 zł/m²) |
| low / high (C) | 111,4 / 211,0 |

**Ościeża.** Ilości ze spec. (ceramika i metal 2 100 + granit 1 810 + okna 2 180 + s-r 410 + BIPV 320 = 6 820 m²) to powierzchnia **w widoku elewacji**. Granit 1 810 m² odpowiada licom frontowym: filary wieży 38,9 % × 2 828 m² ≈ 1 100 m², attyka, kordon, gzymsy, filary parteru i masywne filary łuku, razem ≈ 1 840 m². Tymczasem:
* filary wieży (1,05 co 2,70 m) mają **ościeża 0,60 m po obu stronach na całej wysokości** +4,80…+37,20 (rozdz. 4.4, 8; lico = lico filarów, okna cofnięte o 0,60). Daje to 38 filarów pośrednich, 2 × 0,60 m, minus strefa kordonu, czyli **1 098 m² granitu**;
* skrzydło i segment mają 55 osi × 4 kond. okien 1,20 × 2,40 z ościeżem 0,35 m oraz 27 witryn parteru, czyli **673 m²** wyprawy ceramicznej lub Al.

To jest +26 % rozwiniętej okładziny, nieobecne w F.14.B. Koszt wynosi +2,5…+3,4 mln z KS i rezerwą.

**„Dźwignie rezerwowe ≈ 1,6 mln” są zawyżone (skrypt):**
* pas −2 7 → 4 m usuwa 48,4 m² i daje **−0,12** (spec. −0,7);
* lamele −40 % dają **−0,16** (spec. −0,3);
* granit cokołu skrzydła: w cokole jest tylko ≈ 147 m² granitu, a zamiana na ceramikę daje **−0,09** (spec. −0,4 wymagałoby usunięcia 200 m², więcej niż istnieje);
* ceramika w 2 odcieniach −0,2, bez weryfikacji.

Realnie dźwignie dają **≈ −0,57 mln**.

**Ryzyko niewycenione:** tryskacze. Poz. 7.2 obejmuje hydranty i zawory za 60 zł/m², a spec. przewiduje tryskacze i pompownię 80 m². Możliwe +0,5…+1,0 mln.

**Poprawka (liczby do rozdz. 2 pkt 17, 12, 16.5 i JSON `bilans`):**
1. Do ilości elewacji dopisać ościeża: granit +1 098 m², wyprawy ościeży skrzydła i segmentu +673 m². Zapisać plik wejściowy modelu (`tools/koszty_koncepcja.json`) ze wszystkimi kluczami, także h_pod, drogi, ogrodzenie, bal_zew, bal_wew, okna_wew i drzwi_zew.
2. Dopisać pozycje: pale CFA (504 mb), ścianę na uskoku −1/−2 (38,1 m), dry-cooler, przepusty GPC. Korekty 2,0 mln objąć KS i rezerwą.
3. **Pakiet P**, minimum konieczne do zejścia poniżej limitu (skrypt):
   * ościeża wieży 0,60 → **0,45 m** (E15 dopuszcza 0,40–0,60), wyłożone **aluminium anodowanym RAL 8019** na wełnie (824 m², 1 000 zł/m² [Z]); granit tylko na licu filarów;
   * ościeża skrzydła Al (673 m², 800 zł/m²);
   * lamele 450 → 270 m² (rzeczywista powierzchnia: łuk 145 m² + pas wyrzutni ≈ 70 m² + zapas);
   * BESS 250 → 150 kWh;
   * realne dźwignie (−0,57).

   Wynik: **148,96 mln, zapas 1,04 mln (0,7 %), rezerwa 5 % ≈ 7,1 mln w środku, bufor łącznie ≈ 8,1 mln (5,4 %)**.
4. Zapas ≥ 3 mln (2 %) wymaga jeszcze jednej decyzji:
   * (a) budowla ochronna tylko wtedy, gdy wymaga jej postanowienie z art. 95a; samo MDS daje −1,62 mln, czyli 147,3;
   * albo (b) −2 wyłącznie pod wieżą: −232 m², 99 m.p. = minimum MPZP, ok. −0,4 mln;
   * albo (c) ofertowa weryfikacja stawek [Z] ścian szczelinowych (1 400 zł/m² × 4 410 m² = 6,2 mln) i AV (4,0 mln).
5. Tekst 2 (17) i 16.5 zastąpić: „koszt 149,0 mln netto (mid, II kw. 2026) z rezerwą 5 % (7,1 mln) w środku; zapas do limitu 1,0 mln; dźwignie ≈ 0,6 mln + decyzja 4(a)/(b)”. Koszt 146,2 mln i „bufor 10,7 mln (7,1 %)” nie są prawdziwe.

### K-2. PV 412 kWp nieosiągalne – minimum M.12 (0,4 MWp) niespełnione

**Dowód:**
1. **Dachy (shapely, `koncepcja.json`):**
   * wieża: rzut 1 145,8 m², wnętrze od lica wewnętrznego (0,50 m) **1 080,1 m²**. Spec. kładzie 1 040 m² BIPV, czyli 96 % wnętrza;
   * skrzydło: rzut 847,0 m² (poligon JSON niepoprawny, naprawiony `make_valid`; por. geometria I-4), wnętrze **774,7 m²** przy deklarowanych **780 m² BIPV (101 %)**. Fizycznie się nie mieści.

   Na dachu muszą zmieścić się pas serwisowy i przeciwcieniowy przy attyce (attyka wieży 0,75–1,0 m), wpusty i przelewy, wyłaz oraz zwody (D-14). Strategia energetyczna przyjmowała ≈ 74 % dachów (1 700 m²), a spec. ma 91 % rzutu. Realne pola netto (bufor 1,5 m od obrysu):
   * wieża 954 m² − wyłaz i wpusty ≈ 935 m²;
   * skrzydło 635 m², a przy pasie 0,5 m za niską attyką (0,45–0,65 m) 704 m².
2. **Płyciny BIPV „od dziedzińca ≤ 25 m”, 318 m².** Od dziedzińca wieża ma tylko lico pd. u 0–21 (u 21–40 zasłania segment do +20,85; lica pn., wsch. i zach. nad skrzydłem wychodzą na ulice). Płycina ma 1,65 × 1,30 = 2,145 m². Rzędy ≤ 25 m to P/1, 1/2, 2/3, 3/4 i 5/6; rząd 4/5 to granitowy kordon +19,80–20,85. Daje to 8 przęseł × 5 rzędów − 4 płyciny czerpni (u 2–12, kond. 1; I-3) + 7 przęseł rzędu 5/6 nad segmentem ≈ **92 m²** (14 kWp przy 0,15 kWp/m²; w kolorze grafitowego brązu raczej 0,12–0,13). Spec. zawyża tę powierzchnię 3,5 ×.
3. **Zacienienie (symulacja toru słońca, skrypt `--cien`):**
   * wieża (attyka +37,20, 17 m nad dachem skrzydła) zabiera dachowi skrzydła **11,4–11,8 %** rocznego napromieniowania (24 % punktów traci > 20 % promieniowania bezpośredniego), czyli ≈ 793 kWh/kWp zamiast 878;
   * attyka wieży: −4,8 % na całym wnętrzu dachu wieży, −1,7 % przy pasie 1,0 m.

   Uzysk elewacji 562 kWh/kWp jest wyższy od 450 kWh/kWp ze strategii („z zacienieniem własnym i sąsiedztwa”). Spec. zachowała 27 MWh przy mniejszej mocy.
4. **Wydajność 0,20 kWp/m²** przy 0,15 kWp/m² w modelu kosztów i benchmarkach ([Z] BIPV): niespójność. Przy 0,15 dachy dają 273 kWp.

| Wariant (skrypt) | kWp | MWh/rok | PV/EPB | PV/całość | EP | emisje EPB |
|---|---:|---:|---:|---:|---:|---:|
| Spec. | 412 | 347 | 117 % | 54 % | 26,2 | 6,3 |
| **Realnie** (dach wieży 935 m², dach skrzydła 635 m² × 0,20, płyciny 92 m²) | **328** | **272** | **91 %** | **42 %** | **33,5** | **8,0** |
| Nawet przy maksymalnym pokryciu (1 040 + 775 m² × 0,20 + 14 kWp) | 377 | – | – | – | – | – |

**Poprawka (rozdz. 2 pkt 20, 8, 10, 15, JSON `elewacje.PV`):**
* dachy: moduły szkło-szkło **≥ 0,215 kWp/m²**;
  * wieża **935 m²** (pas 1,0 m przy attyce, wyłaz przy trzonie B) = **201 kWp**;
  * skrzydło **700 m²** (pas 0,5 m) = **150 kWp**; na schemacie zaznaczyć strefę cienia wieży;
* płyciny wieży od dziedzińca: **92 m² = 14 kWp** (zdjąć z nich czerpnię albo czerpnię przenieść, I-3);
* **nowe pole: BIPV na ślepej ścianie pd. segmentu**, (96,694; 38,813)–(115,979; 39,930), od +4,80 do +20,85: **310 m² × 0,15 = 46 kWp**. Ściana patrzy na pd. (az. ≈ 177°), nie jest elewacją od ulicy (dz. 10/2 to dojazd w 2MW-U/5), ma ≤ 25 m i klasę NRO. Uzysk przy cieniu WS 5 (139,5 m n.p.m., 10,6 m) wynosi **≈ 452 kWh/kWp** (skrypt). Szkło satynowane w tonie ceramiki S 1010-Y30R jako relief w osiach 2,025 m; pnącza zostają w strefie parteru;
* **razem 411 kWp, 323 MWh/rok, PV/EPB 109 %, PV/całość 50 %, EP 28,6, emisje EPB 6,9 kg/(m²·rok)** (skrypt).

Alternatywa bez ściany segmentu: zadeklarować 0,33 MWp na działce z jawnym uzasadnieniem (MPZP § 6 pkt 13, WT § 216 ust. 8 powyżej 25 m, cień wieży) oraz ≥ 0,07 MWp w społeczności energetycznej. M.12 mówi jednak o „dachu dominanty i elewacjach”, więc to wariant słabszy.

W tekstach zamienić „PV 412 kWp, 347 MWh, 117 % EPB, EP 26” na wartości z wiersza poprawki. Dotyczy to też paska KPI na P8 i punktu 9 części opisowej.

---

## 3. Błędy ISTOTNE

### I-1. Dry-cooler i szczyt chłodu bez lokalizacji

**Dowód.** Strategia (5.2) podaje szczyt chłodu ≈ 600 kW. GPC daje ≈ 330 kW chłodu aktywnego (oddawanie do gruntu ≈ 390 kW). Rocznie gruntowi przybywa ≈ 166 MWh ciepła. Strategia rozwiązuje to „hybrydowym dry-coolerem w piętrze technicznym (wyrzut od dziedzińca)”. Synteza usunęła pomost techniczny (2 pkt 3), a w rozdz. 10 dry-cooler pojawia się tylko „w okresach przejściowych”, bez miejsca i bez mocy. Dach jest wykluczony (MPZP § 6 pkt 13), −1 i −2 nie mają powietrza zewnętrznego. Urządzenie ≈ 300 kW potrzebuje ≈ 25–30 m³/s powietrza.

**Poprawka.** Dry-cooler hybrydowy 2 × 150 kW na **kond. 4 segmentu, w pasie usług od zach.** (≈ 45 m²). Żaluzje akustyczne ≈ 24 m² brutto (≤ 2,5 m/s) w elewacji zach. segmentu (lico (95,020; 45,681)–(96,694; 38,813), kond. 3–4, od dziedzińca) i tłumiki. Odległość od czerpni wieży (u 2–12, kond. 1) wynosi ≈ 14,5 m w poziomie. Usługi z pasa przenieść do strefy środkowej wieży. W rozdz. 10 wpisać: „szczyt chłodu ≈ 600 kW = GPC 330 kW + dry-cooler 2 × 150 kW + przesunięcie TABS; nadwyżka gruntu 165 MWh/rok odprowadzana dry-coolerem i odzyskiem do c.w.u.”. Koszt +0,49 mln ujęto w K-1.

### I-2. Pole sond: brak lokalizacji, za mała powierzchnia, głębokość a art. 86 PGiG

**Dowód.** Strategia: 75 BHE w siatce ≈ 6 × 6 m to ≈ 2 700 m² „pod płytą”. Podziemie ma tylko **2 337 m²** (−1), z czego 1 426 m² to −2 z 36 palami CFA, podszybiami i zbiornikiem deszczówki 50 m³. Przy wierceniu z dna −2 (spód płyty 111,10) sonda 99 m kończy się na 12,1 m n.p.m., czyli **107 m pod terenem** (119,2). Jeżeli organ liczy głębokość od terenu, obowiązuje reżim art. 86 PGiG, który spec. deklaruje ominąć. 75 indywidualnych przepustów przez płytę białej wanny przy naporze 5,4–7,9 m to ryzyko szczelności.

**Poprawka.** **58 sond w siatce 6,0 × 6,0 m pod płytami −1 i −2 (2 088 m² ≤ 2 337 m²)**, dno ≤ 19,2 m n.p.m. (≤ 100 m p.p.t.): 92 m z dna −2 i 95 m z dna −1. Kolektor zbiorczy w warstwie podpłytowej z 1–2 przepustami. **Ściany szczelinowe energetyczne** (4 400 m², ≈ 15–20 W/m², 66–88 kW) i **36 pali energetycznych** (504 mb × 40 W/m ≈ 20 kW). Pobór łącznie ≈ 330–350 kW ≥ 320 kW. Opcję tę strategia już przewidziała (5.2, „Uzupełnienia”). Na przekroju P6 sondy rysować do 19,2 m n.p.m.

### I-3. Urządzenia i otwory techniczne – lokalizacja niekompletna (MPZP § 6 pkt 13)

**Dowód i braki:**
* **Agregat HVO na −2:** „spaliny szachtem do elewacji od dziedzińca” bez lica i wysokości. Agregat ≈ 400–500 kVA potrzebuje też powietrza chłodzącego ≈ 8–12 m³/s. Wylot spalin na niskim licu dziedzińca psuje powietrze w ogrodzie, przy placu zabaw i przy oknach WS 5 i Maz. 19. Trzeba też zachować odległość od czerpni (WT § 152; przyjęto ≥ 8 m w poziomie).
* **Trafo SN/nn z drzwiami od Wybrzeża:** wentylacja komory trafo (≈ 1–1,5 m² wlotu i wylotu) wypada w elewacji od bulwaru. Przeczy to deklaracji „żaluzje czerpni i wyrzutni tylko od dziedzińca”. Pas pn. segmentu jest i tak za mały (geometria I-1).
* **Bistro 92 m²** w dziobie NW nie ma ustalonego wyciągu kuchennego. Wyrzut ponad dach jest zakazany, a `_bilans_energii.py` zakłada „bistro bez kuchni”.
* **Czerpnia zbiorcza** to 4 płyciny ≈ 8,6 m² na kond. 1. Przy ≈ 21 m³/s świeżego powietrza (szacunek: 5 central po ≈ 12 tys. m³/h + P i S ≈ 25 tys. m³/h) daje to ≈ 2,5 m/s, czyli granicę. Te same płyciny są w spec. policzone jako BIPV (K-2).
* **Piony:** czerpnia na kond. 1 → centrale kond. 2–5 i −1, wyrzutnia → korona. Potrzeba ≈ 6–7 m² szachtów na kondygnacji w strefie środkowej wieży, poza bilansem rzutów.
* **Garaż:** brak wyrzutni wentylacji i oddymiania (geometria D-11).
* **Nadciśnienie klatek A, B, C:** brak lokalizacji czerpni (dach wykluczony).

**Poprawka (rozdz. 6, 8, 10):**
* spaliny agregatu i wyrzut oddymiania garażu: szachtem w trzonie B do lameli korony od pd., ≥ 10 m od okien komisji;
* powietrze chłodzące agregatu: żaluzje w elewacji zach. segmentu, kond. 1;
* trafo: wentylacja szachtem do lica zach. segmentu, drzwi od Wybrzeża pełne;
* „bistro bez kuchni gorącej (regeneracja, wyciąg z rekuperacją)”;
* czerpnia: 2 rzędy płycin (P/1 i 1/2) u 2–12 = 17 m² (≈ 1,25 m/s), wyłączone z BIPV;
* piony: 2,7 + 1,4 + 3,5 m² do bilansu strefy środkowej;
* czerpnie nadciśnienia: w elewacji pd. wieży, kond. P, ≥ 5 m od czerpni zbiorczej.

### I-4. Agregat i pompownia tryskaczowa pod poziomem zalewu

**Dowód.** Rozdz. 6, −2: „tryskacze 80 m², agregat HVO 25 m²” na 112,30, czyli 6,7 m poniżej poziomu sytuacji wyjątkowej 119,0 i 4,2 m pod ZWG maks. Korekta (d) przeniosła nad teren rozdzielnię, UPS, BESS i serwerownię, a pominęła dwa urządzenia zasilające bezpieczeństwo pożarowe: dźwig R, nadciśnienie, oddymianie i pompy tryskaczowe.

**Poprawka.** Przenieść oba urządzenia na **−1 do szczelnego boksu**, z progiem i wlotami powietrza ≥ 120,30 (rzędna zapór +1,00) i z odpływem awaryjnym. Alternatywnie agregat na kond. 1 segmentu (≈ 40 m², wzmocniony strop) razem z I-1. Opisać to w 2 (d).

### I-5. Okna: nadproże nad spodem stropu

**Dowód (skrypt).**
* Skrzydło: parapet 0,90 + okno 2,40 = nadproże **3,30**, spód płyty 3,20 (rozdz. 4.2: „biura w skrzydle 3,20 m (płyta 0,40)”). Z kasetą ZIP „w nadprożu” (≈ 0,18) wychodzi 3,48.
* Wieża: przy parapecie 0,85 (≤ 25 m) nadproże 3,30, spód 3,32. Kaseta ZIP się nie mieści.

Na rysunku 1:50 (P7) jest to kolizja oczywista dla sądu.

**Poprawka:**
* skrzydło i segment: parapet 0,60 z dolną kwaterą stałą ze szkła bezpiecznego do 0,90, okno **1,20 × 2,35** (1 : 1,96, E12 ✔), nadproże **2,95**, kaseta ZIP 2,95–3,13 ≤ 3,20; WWR **37,1 %** (zamiast 38 %);
* wieża: parapet 0,55 z kwaterą stałą, okno 1,65 × 2,45 bez zmian, nadproże **3,00**, kaseta ≤ 3,18 ≤ 3,32; WWR 40 % bez zmian.

Tekst 8 („okno 1,20 × 2,40, parapet 0,90”) i JSON `elewacje.skrzydlo.parapet_m` zmienić na 0,60 i [1,20, 2,35].

### I-6. Współczynnik U ścian nie wynika z warstw

**Dowód (skrypt).** Warstwy: wełna 200 mm λ 0,033 + żelbet 200 + Rsi i Rse. Daje to U0 = **0,156** bez łączników. Konsole aluminiowe elewacji wentylowanej dodają ΔU 0,02–0,07, czyli U ≈ **0,18–0,23**. Wymaganie WT to ≤ 0,20, więc przy konsolach Al jest ono zagrożone. Deklaracja 0,15 (tabela 1:50, rozdz. 10) jest nieprawdziwa. Od tej wartości zależy też Q_H w bilansie EP.

**Poprawka.** Wełna **260 mm λ 0,033** (lub 230 mm λ 0,031) i łączniki ze stali nierdzewnej lub GRP (ΔU ≤ 0,025) dają **U ≤ 0,15**. Ściana grubieje o 60 mm. Skutki: ościeże wieży 0,66 m albo izolacja λ 0,031 przy 0,60 m; lico ściany 0,06 m głębiej, co trzeba ująć przy usuwaniu geometrycznego K-1 (gzyms w obrysie). Do tabeli 1:50 wpisać „konsole nierdzewne z przekładką, ΔU ≤ 0,025”.

### I-7. Lamele korony – rytm 0,9 m (E19) i błędny kąt przesłonięcia

**Dowód.** Jasna ceramika S 1005-Y20R na tle ciemnego szkła, rozstaw regularny 0,90 m, element najbardziej eksponowany (W3, W9, widok z mostu). Z 80 / 150 / 200 m daje to 1,6 / 2,9 / 3,9 cykla na stopień (skrypt), czyli pasmo dyskomfortu wzrokowego (`elewacje_zasady.md` 3.5). E19: „unikać regularnych, kontrastowych pasów o okresie 0,5–1,0 m na elewacjach widocznych z 80–200 m”. Rachunek kąta: tan θ = (0,90 − 0,25) / 0,60, więc pełne przesłonięcie zachodzi od **47,3°** od normalnej, a nie od 34° (2 pkt 5).

**Poprawka.** Lamele **0,35 × 0,60 co 1,35 m** (moduł) w rytmie grupowanym 1,35 / 0,675. Obniżyć kontrast (ΔL* ≤ 15): lamela w tonie S 2005-Y20R i sitodruk ceramiczny ≈ 30 % na szkle za lamelami. Przesłonięcie w osi 26 %, pełne od 59°. Lamel będzie mniej (≈ 16 zamiast 24 na łuku 22 m), co pomaga też w K-1. W 2 pkt 5 poprawić „34°” na wartość rzeczywistą.

### I-8. Prezentacja kosztu: metoda kontrolna i miara zł/m² PU

**Dowód:**
* `koszty_benchmarki.md` 7.5: kontrola top-down „nie jest niezależna, bo stawki [Z] dobrano właśnie tak, by trafić w pasmo B”. Spec. podaje ją jako „Metodę 2 (kontrolną)”.
* Ten sam dokument (rozdz. 4) każe podać także zł/m² PU. Wynik: 146,2 / 8 400 = **17 405 zł/m² PU** (po korekcie **18 060**), przy paśmie B1/B2/B6 11 400–14 900. Ekspert sądu to policzy.
* Waloryzacja „+5 % (2027): 151,4” jest liczona od 144,2. Od kosztu całkowitego wychodzi 153,5 (spec.) i ≈ 156,4 (po korekcie, pakiet P).

**Poprawka.** Nazwać metodę 2 „spójnością z pasmem kalibracji (niezależną kontrolą nie jest)”. Dodać obie miary: ≈ 8 300 zł/m² PC i ≈ 17 700 zł/m² PU, z definicją PU i argumentem PC/PU = 2,13 (wysoki udział holi, sali i garażu MDS). Waloryzację liczyć od kosztu całkowitego.

### I-9. Retencja „zero odpływu” – warunki gruntowe i lokalizacja

**Dowód.** Arytmetyka jest poprawna (rozdz. 1). Zbiornik rozsączający 60 m³ nie ma jednak miejsca na planie. Grunt to nasypy niebudowlane z gruzem (2,8–3,8 m, możliwe zanieczyszczenia), ZWG maks. 116,45 (≈ 2,6–2,8 m pod terenem dziedzińca), strefa podtopień (`koszty_benchmarki.md` 6). Rezerwa 20 m³ w zbiorniku na −2 musi być opróżniana pompą przed kolejnym deszczem. Dla zerowego odpływu miarodajny jest też deszcz dłuższy niż 60 min.

**Poprawka.** Skrzynki rozsączające ≈ 55 m² × 1,15 m pod nawierzchnią przepuszczalną w pasie 4,6 m od bulwaru (poza strefami korzeni D703, D704, D886): **dno ≥ 117,45** (1 m nad ZWG maks.), wymiana nasypu pod skrzynkami, badanie k przed PB. Zapisać sterowanie rezerwą 20 m³ (pompa do skrzynek po 24 h). Jeśli k < 1·10⁻⁶ m/s, przejść na dławik ≤ 2 dm³/s i zmienić hasło na „odpływ ograniczony do 2 dm³/s”.

---

## 4. Błędy DROBNE

* **D-1. Wejście modelu kosztów** nie jest zapisane, a 7 parametrów nie ujawniono (rozdz. 1). Jawne parametry dają 144,35, nie 144,2. Zapisać JSON i podać listę.
* **D-2. Korekty 2,0 mln** doliczono poza KS i rezerwą (+0,16 mln). Lamele 450 m² to zawyżenie (≈ 215 m² rzeczywiście), wykop 6,9 m także (6,49). Ujęte w K-1.
* **D-3. Zieleń 1 100 m² × 500 zł** obejmuje zachowane ogródki ≈ 470 m². Możliwa dźwignia ≈ −0,1…−0,2 mln (pielęgnacja zamiast nowej zieleni).
* **D-4. E02 – segmentacja.** M2 (S 1010-Y30R) i M3 (S 1005-Y20R) mają tę samą czerń 10 (ΔL* ≈ 1–2). Na elewacji WNW w cieniu podział będzie słabo czytelny (uwaga weryfikatora w E02). Użyto trzech narzędzi naraz: barwa, relief i faktura (heurystyka: najwyżej dwa). Poprawka: M3 → S 2005-Y20R (ΔL* ≈ 6–8 wobec M2 i M4), faktura tylko dla M2 i M4.
* **D-5. E15, E17, E21:**
  * ościeże skrzydła 0,35 m na elewacji WNW (282°) jest poniżej 0,40 → 0,40 m (wynika z I-6);
  * gzyms z wysięgiem 0,30 m jest poniżej 0,5–0,9 m (E17) i stoi w konflikcie z obrysem (geometria K-1) → czytelność dać wysokością 0,70 m i cieniem fugi 0,15 m, wysięg 0,30 opisać jako świadome odstępstwo;
  * cokół z jasnego granitu S 1502-Y nie jest ciemniejszy o 15–25 L* (E21) → granit w cokole parteru S 3502-Y (płomieniowany, ta sama rodzina strzegomska);
  * M4 S 1510-Y40R wychodzi poza zakres Y10R–Y30R → S 1510-Y30R.
* **D-6. Klasa ogniowa BIPV i ZIP.** Tabela 1:50 podaje „BIPV A2-s1,d0 tylko ≤ 25 m”. Jeśli wyrób miałby klasę A2-s1,d0, byłby niepalny i ograniczenie do 25 m nie wynikałoby z WT. Moduły szkło-szkło z laminatem mają zwykle co najwyżej B-s1,d0. Zapisać „BIPV ≥ B-s1,d0, NRO w układzie ściany, wyłącznie ≤ 25 m”, także dla ściany segmentu (K-2). Rolety ZIP powyżej 25 m (kond. 6 i S) z tkaniny szklano-silikonowej A2-s1,d0.
* **D-7. Proporcja wieży (§ 8.2 pkt 3, E26).** Wieża wypełnia całe A (40 × 29,7 m). Część nad kordonem ma 16,35 × 40 m (H : W ≈ 0,41) i z mostu czyta się jako poziomy blok. Pionowość daje tylko wielki porządek filarów. Trójdzielność 20,85 / 6,45 / 9,9 m odbiega od 2,3 : 1,7 : 1. To decyzja panelu, ale trzeba ją ująć w opisie i sprawdzić na W3 i W9.
* **D-8. M1 „kordon i gzyms w liniach nr 19”** przeczy zapisowi „wspólne są cokół i gzyms; kordon na 124,10”. Linią nr 19 jest naświetle 122,77. Ujednolicić tekst.
* **D-9. Taras nad Oławą „167 m²”** to cały rzut segmentu. Wnętrze ma 140 m², a wewnątrz balustrady cofniętej o 1,5 m zostaje ≈ **92 m²** użytkowych + ≈ 48 m² pasa zieleni. Poprawić 2 (7), 6 i 14 (W11).
* **D-10. Uzysk BIPV elewacji 562 kWh/kWp** przy 450 w strategii, zob. K-2. Kolor grafitowy brąz obniża wydajność do ≈ 0,12–0,13 kWp/m².
* **D-11. Woda:** 100 % spłukiwania wychodzi z zapasem 0,4 %. Zakłada to 75 % wykorzystania 848 m³ przy 30 m³ użytkowych zbiornika (50 − 20 rezerwy), czyli ≈ 12 dni zapotrzebowania na deszczówkę. Pisać „≈ 100 %” albo zwiększyć zbiornik do 60 m³ (+10 m³ na −2).
* **D-12. GWP ≤ 500 kg CO₂e/m² PC (A1–A5)** nie ma obliczenia. Szacunek weryfikatora (skrypt, sekcja 6; 15 100 m³ betonu CEM III/A, z czego 50 % w podziemiu i fundamentach, plus fasady, PV i instalacje wg TM65) daje **370–615, środek ≈ 490**. Cel jest możliwy, ale na granicy. Strategia miała ≤ 600. Podać „≤ 500 (cel), szacunek koncepcyjny ≈ 490 ± 120” i wymagać CEM III/B w ścianach szczelinowych i płytach.
* **D-13. „Przestrzeń sufitowa nad komisjami bez urządzeń”** (2 pkt 3) a „wyrzutnia zbiorcza w pasie nad komisjami” (10). Kanały i plenum nie są urządzeniami, ale tekst trzeba ujednolicić: „wyłącznie kanały i plenum wyrzutni, bez central”.
* **D-14. Dach „bez urządzeń”.** Wymagana instalacja odgromowa: kula toczona 30–45 m przy rozpiętości 30 m daje ugięcie ≈ 4 m, a moduły leżą 0,75–1,0 m pod koroną attyki. Potrzebne zwody i wyłaz. Zapisać: „zwody niskie ≤ korony attyki, obróbka attyki jako zwód naturalny, wyłaz płaski przy trzonie B”.
* **D-15. Falowniki i rozdzielnice DC** dla ≈ 400 kWp nie mają pomieszczenia (≈ 10–15 m²). Wskazać: kond. S przy trzonie B (przestrzeń pod rusztem) albo −1.
* **D-16. `koncepcja.json`:**
  * `elewacje.PV` = 364 / 48 / 412 → 351 dach + 14 płyciny + 46 segment = 411;
  * `bilans.koszt_mln_netto` 146,2 → ≈ 149,0 (pakiet P);
  * `koszt_model_F14B_mid_mln` 144,2 → wartość z zapisanego JSON;
  * poligon skrzydła niepoprawny (geometria I-4), co utrudnia obliczanie dachu.

---

## 5. Zmiany do wprowadzenia (zestawienie liczb)

| Miejsce | Jest | Ma być |
|---|---|---|
| 2 (17), 12, 16.5, JSON `bilans` | 146,2 mln; zapas 3,8; bufor 10,7 (7,1 %); dźwignie 1,6 | **≈ 149,0 mln** (pakiet P, K-1); rezerwa 5 % ≈ 7,1; zapas ≈ 1,0 (0,7 %); dźwignie ≈ 0,6 + decyzja 4(a)/(b) |
| 12, parametry | granit 1 810; ceramika i metal 2 100; BIPV elew. 320; PV dach 364 kWp; lamele 450 | granit 1 663 (bez cokołu skrzydła) + 275 (węgary ościeży wieży); okładzina Al ościeży 824 (wieża) + 673 (skrzydło, segment); ceramika i metal 2 167 (2 100 + 230 z płycin wieży − 310 na BIPV segmentu + 147 cokół skrzydła); BIPV elew. 400 (92 płyciny + 310 segment); PV dach 351 kWp; lamele 270; dodatkowo pale 504 mb, uskok 38,1 m, dry-cooler, przepusty GPC |
| 12, metoda 2 | 8 161 zł/m² PC, „kontrolna” | ≈ 8 300 zł/m² PC i ≈ 17 700 zł/m² PU; spójność z kalibracją, a nie niezależna kontrola; waloryzacja +5 % od kosztu całkowitego |
| 2 (20), 8, 10, 15, JSON `elewacje.PV` | 412 kWp; 347 MWh; 117 % EPB; 54 %; EP 26; 6,3 kg | **411 kWp** (201 + 150 + 14 + 46); **323 MWh**; **109 %**; **50 %**; **EP 28,6**; **6,9 kg** |
| 10 – GPC | 75 × 99 m, bez lokalizacji; dry-cooler „w okresach przejściowych” | 58 × 92–95 m (dno ≤ 19,2 m n.p.m.), siatka 6 × 6 m pod płytą −1/−2; ściany szczelinowe energetyczne 4 400 m² + 36 pali; dry-cooler 2 × 150 kW na kond. 4 segmentu; szczyt chłodu 600 kW |
| 6, 10 – technika | agregat i tryskacze na −2; spaliny „do elewacji od dziedzińca” | boks szczelny na −1 (wloty ≥ 120,30) lub kond. 1 segmentu; spaliny szachtem w trzonie B do korony pd.; wentylacja trafo do lica zach. segmentu; bistro bez kuchni gorącej |
| 8 – okna | skrzydło 1,20 × 2,40, parapet 0,90; wieża parapet ≥ 0,85 | skrzydło **1,20 × 2,35, parapet 0,60 + kwatera stała**, nadproże 2,95, WWR 37,1 %; wieża parapet 0,55 + kwatera stała, nadproże 3,00 |
| 8 – przekrój 1:50 | wełna 200, U 0,15; BIPV A2-s1,d0; ościeże skrzydła 0,35 | wełna 260 (λ 0,033), konsole nierdzewne, U ≤ 0,15; BIPV ≥ B-s1,d0, NRO, ≤ 25 m; ościeże skrzydła 0,40; ościeża wieży 0,45 (Al) |
| 2 (5), 8 – lamele | 0,25 × 0,60 co 0,90; 100 % od 34° | 0,35 × 0,60 co 1,35 (grupowane); 100 % od 59°; sitodruk 30 % za lamelami |
| 9, 10 – retencja | zbiornik rozsączający 60 m³ bez lokalizacji | skrzynki ≈ 55 m² × 1,15 m w pasie 4,6 m, dno ≥ 117,45, wymiana nasypu, badanie k; warunek zapasowy: dławik 2 dm³/s |
| 2 (7), 6, 14 | taras 167 m² | taras ≈ 92 m² użytkowych + 48 m² zieleni |

---

## 6. Dowód – wynik skryptu (`_weryfikacja_koszt_eko.py --cien`)

```
== 1. KOSZT (mid, mln zł netto, II kw. 2026)
  parametry jawne spec.: 144.35
  + parametry nieujawnione (dopasowanie do tabeli 12): 144.18  grupy {1: 10.94, 2: 9.14, 3: 22.06, 4: 5.72, 5: 1.95, ... 18: 8.57}
  spec. 144,2 + 2,0 objęte KS i rezerwą: 146.34 (spec.: 146,2)
  B. korekta ilości + pozycje spoza modelu: 148.29
  ościeża pominięte: granit (filary wieży, 2 × 0,60 m) 1098 m²; ościeża okien i witryn skrzydła/segmentu 673 m² (55 osi)
  C. B + ościeża: stawki modelu 151.72; stawki obniżone (granit 1 600, okładzina Al 800) 150.78   | low 111.4 | high 211.0
  zł/m² PC (C): 8470; zł/m² PU 8 400 (C): 18062; spec.: 17405 zł/m² PU
  dźwignie: pas −2 7→4 m -0.12 (spec. −0,7); lamele −40 % -0.16 (spec. −0,3); granit cokołu → ceramika -0.09 (spec. −0,4)
  P. pakiet (ościeża wieży 0,45 m Al, ościeża skrzydła Al, dźwignie realne, BESS 150 kWh): 148.96, zapas 1.04
== 2. PV / EP
  SPEC:     412 kWp, 347 MWh/rok, PV/EPB 117%, EP 26.2
  REALNIE:  328 kWp, 272 MWh/rok, PV/EPB 91%,  EP 33.5
  POPRAWKA: 411 kWp, 323 MWh/rok, PV/EPB 109%, EP 28.6
== 3. Okna: skrzydło (spec.) nadproże 3.30 > spód stropu 3.20 → KOLIZJA; poprawka 2.95 / ZIP 3.13 → OK; WWR 37.1%
== 4. Lamele: pełne przesłonięcie od 47.3° (spec. 34°); 1.6 / 2.9 / 3.9 c/° z 80 / 150 / 200 m
== 5. Ściana: U0 0.156; z konsolami Al 0.18–0.23; poprawka 260 mm → ≤ 0.15
== 6. GWP A1–A5 ≈ 372–615 kg CO2e/m² PC (beton ≈ 15 144 m³)
== 7. Zacienienie: dach skrzydła (wnętrze 774,7 m²) strata 11,8 %; netto 635,5 m² 11,4 %;
     dach wieży (wnętrze 1 073,6 m²) 4,8 %; netto 954,3 m² 1,7 %; ściana pd. segmentu ≈ 452 kWh/kWp
```

Pozycje oznaczone [Z] (pale 1 100 zł/mb, uskok 1 250 zł/m², dry-cooler 0,45 mln, przepusty GPC 0,75 mln, okładzina Al ościeży 800–1 000 zł/m²) to założenia weryfikatora o tym samym statusie co stawki [Z] modelu. Wniosek K-1 nie zależy od żadnej z nich osobno. Wystarczą ościeża liczone stawkami modelu (+3,43 mln) oraz pale i uskok, które wynikają wprost z tekstu spec. i geometrii (+0,99 mln). Po odjęciu zawyżeń wykopu i płyty oraz zmian PV (−0,34 mln) daje to 146,34 − 0,34 + 0,99 + 3,43 = **150,4 mln > 150**, bez dry-coolera, przepustów GPC i ryzyka tryskaczy.
