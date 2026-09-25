# Dom LAMELA — weryfikacja niezależna V2 po rundzie 2 poprawek: fizyka, woda, instalacje

Data: 25.09.2026. Weryfikator: V2 (niezależny; modelu, skryptów projektu i bibliotek nie zmieniano).
Zakres: mostki cieplne (ψ, f_Rsi, ciągłość „4 linii”), EP z PV i bez PV, obciążenie cieplne i moc podłogówki, bilans
wentylacji, odwodnienie dachów (wpusty, przelewy awaryjne względem pokrycia przy wpuście, rury spustowe, rynny płyt
wysuniętych), PV (rozmieszczenie, wysokość względem attyki), teren (spadki, cokół ≥ 0,30 m). Sprawdzono też, czy
rozwiązano pozycje z `projekt/08_obliczenia/mostki/REKOMENDACJE.md`, z weryfikacji koncepcji §6 i z listy K-1…K-13
(`docs/20_koncepcja/poprawki_runda2_wejscie.md`). Pozycje funkcjonalne A3 (część 1 rundy) są poza zakresem V2.

## 0. Metoda i stan modelu

* Model odtworzyłem skryptem w scratchpadzie (import `tools/buduj_model.py`, zapis do katalogu tymczasowego). Wszystkie
  4 pliki `model/*.yaml` są **bajtowo identyczne** z wersją w repozytorium, więc model odpowiada skryptowi.
* Walidacja rdzenia (`load_model(..., strict=True).raport_walidacji()`) daje 0 błędów i 0 ostrzeżeń (373 INFO o polach
  spoza schematu).
* Przeliczyłem wszystko od nowa do katalogu tymczasowego (repozytorium bez zmian):
  * `tools/mostki_budynku.py`, czyli 22 węzły 2D wg PN-EN ISO 10211. Walidacja solvera na przypadkach 1 i 2 z zał. C
    daje |Δθ| ≤ 0,048 K;
  * `lamela.obliczenia.fizyka_energia`;
  * `lamela.obliczenia.instalacje` (woda, kanalizacja, deszczowa, drenaż, ogrzewanie, bilans mocy, obwody, PV,
    odgromowa).
* Skrypty pomocnicze (scratchpad `runda2_V2/`):
  * `teren_tin.py` sprawdza obwód P0 co 0,10 m na **liniowym TIN rzędnych projektowanych**, czyli tą samą metodą co
    `lamela.wskazniki.Teren`;
  * `wz09.py` liczy warianty węzła WZ-09a;
  * `ep.py` liczy EP bez PV przy n50 = 4 h⁻¹.
* Testy:
  * `test_obliczenia_fizyka`: 24/24 zaliczone;
  * `test_pipeline`: w pierwszym przebiegu 24 zaliczone i 1 niezaliczony (sekcja 5);
  * pozostałe wyniki podano w sekcji 5.

## 1. Wyniki kontrolne (przeliczone przez V2)

| Wielkość | Wynik V2 | Wymaganie / podstawa | Ocena |
|---|---|---|---|
| f_Rsi, minimum z 22 węzłów | 0,836 (WZ-09b) | ≥ 0,72 (WT zał. 2 pkt 2.2.1; W-248) | ✓ |
| H_TB (Ψ_oi z symulacji, sekcja `wezly`) | 30,63 W/K (ΔU_TB 0,050) | PN-EN ISO 14683 / 10211 | ✓ zgodne z 14.2 |
| Φ_HL (θ_e = −18 °C) | 7,41 kW (28,2 W/m²) | PN-EN 12831-1 | ✓ zgodne z 14.2 |
| EP z PV (A) / bez PV (A0) | 35,6 / 57,8 kWh/(m²·rok) | ≤ 70 (WT §329, W-240) | ✓ |
| EP przy n50 = 4 h⁻¹ z PV / **bez PV** | 44,1 / **67,1** | ≤ 70 | ✓, ale bez PV i bez próby szczelności zapas wynosi tylko **4 %** (N-12) |
| Ogrzewanie podłogowe (PN-EN 1264) | 0 niespełnionych; θ_V,des 35 °C; łazienki, WC i 2.06 ze ścianami grzewczymi wodnymi | W-153 | ✓ |
| Pompa ciepła | 7,4 kW R290, punkt biwalentny −9,7 °C, pokrycie mocy 10,55 ≥ 8,66 kW | W-155; (UE) 2024/573 | ✓ |
| Wentylacja: Σ nawiewu / Σ wywiewu, tryb okresowy | 365 / 365 m³/h, okresowo 435 m³/h, centrala 450 | PN-83/B-03430/Az3; W-161…W-164 | ✓ bilans; pom. 2.07 bez dopływu powietrza (N-9) |
| Przelewy awaryjne D1–D4 | dno = pokrycie przy wpuście + 0,03…0,04 m i ≥ pokrycie lokalne (6 przelewów) | W-142; J2 5.1 | ✓ |
| Wywinięcia na attykach D1 / D2 / D3 / D4 | 0,28 / 0,22 / 0,22 / 0,49 m | ≥ 0,15 m (DAFA; brief §9.4) | ✓ |
| Rury spustowe | wszystkie Q ≤ Q_RWP | PN-EN 12056-3 | ✓, ale bez dopływu z PL-3 do PL-2 (N-7) |
| Retencja | niecka NCH-1 28 m² × 0,30 = 8,4 m³ ≥ V_min 5,71 m³, opróżnianie 1,6 h | W-143, W-145 | ✓ (moduł raportuje własny dobór „19,5 m²”, N-13) |
| Spadki terenu (moduł drenażu, środki ścian) | 2,7–4,0 % | ≥ 2 % (W-019) | ✓ w środkach ścian; lokalnie poniżej wymagania (N-3, N-4) |
| Cokół poza strefami drzwi z OL | moduł podaje 0,31 m; **TIN V2: 0,04 m** (S0-05), 0,27 m (S0-02), 0,29 m (S0-03) | ≥ 0,30 m (brief §9.4) | ✗ (N-3, N-4) |
| PV: liczba modułów i moc | D1 7 + D4 8 = 15 × 430 Wp = 6,45 kWp | ≤ 6,5 kWp (W-194) | ✓ |
| PV: górna krawędź / korona attyki | D1 +9,863 / +9,876 (zapas **13 mm**); D4 +3,704 / +3,85 | PV nie ponad attykę (W-033, D-15) | ✓ bez tolerancji wykonania (N-10) |
| Wysokość zabudowy (`lamela.wskazniki`) | 10,27 m (od t_śr; najwyższy element: czerpnia z = +10,00) | ≤ 11,00 m, rezerwa 10,70 (W-033) | ✓ formalnie, ale +10,00 to **dolna krawędź wlotu**, a nie szczyt urządzenia (N-2) |
| Wyrzutnia dachowa z wylotem poziomym | +10,00: 0,12 m nad koroną attyki D1, 0,06 m nad wywiewką K1 (obie w promieniu 10 m) | ≥ 0,4 m nad linią najwyższych punktów w promieniu 10 m (WT §152; W-167, R6-43) | ✗ (N-1) |
| Spadek napięcia DC PV / WLZ | 1,04 % / 0,61 % | ≤ 1,00 % [ZAŁ] / ≤ 0,50 % (W-194, W-185) | ✗ bez zmian od rundy 1 (N-11) |

## 2. Status pozycji wejściowych rundy 2 (zakres V2)

### 2.1 Lista koordynatora K-1…K-13

| # | Stan po rundzie 2 (sprawdzenie V2) | Ocena V2 |
|---|---|---|
| K-1 teren i cokół | Pierścienie projektowane 0–2,3 m dają w środkach ścian spadek 2,7–4,0 %. Strefy drzwi mają OL-1…OL-6. Na liniowym TIN zostały jednak trzy miejsca: filar S0-05 między podestem T2 a bramą (cokół 0,04 m, spadek −1 % ku ścianie), S0-02 przy x 13,6 (0,27 m) i S0-03 przy DZ2 (0,29 m). Membrana posadzki garażu leży poniżej nawierzchni przy BR1, DZ2 i T2. | **częściowo** (N-3, N-4, N-5) |
| K-2 niecka a korona DR1 | DR1 przesunięta do (4,0; −22,0). Krawędź korony (r 3,5 m) jest 1,5 m od NCH-1. | ✓ przy przyjętej średnicy korony 7,0 m (N-14) |
| K-3 / K-11 wysokości z `lamela.wskazniki` | `audyt_wt.py` i `podglad_modelu.py` biorą H z modułu: 10,27 m. | ✓ metoda. Dana wejściowa czerpni zaniżona (N-2) |
| K-4 EP po mostkach | 35,6 z PV, 57,8 bez PV, 67,1 bez PV przy n50 = 4. | ✓ (zapas bez PV i bez próby szczelności — N-12) |
| K-5 MES płyty (BO) | Poza zakresem V2. PF2 z uskokiem 0,15 m czeka na BO. | przekazane (N-6: skutek dla mostka WZ-09a) |
| K-6 audyt A3 | Poza zakresem V2 (część 1). Jedna konsekwencja instalacyjna: drzwi D4A do 2.07. | N-9 |
| K-7 PV | Faktyczny układ modułów (7 + 8), z_max ≤ korona, z_max wliczone do H. | ✓ z uwagami (N-10, N-11) |
| K-8 piony `rodzaj` | K1, K2, K3 — kanalizacja; RS1, RS2, RS6 — deszczowa; PCO — c.o. Kanalizacja: 0 niespełnionych. | ✓ |
| K-9 bilans wentylacji | Σ nawiewu = Σ wywiewu = 365 m³/h, szachty bez wywiewu, okresowo 435 ≤ 450. | ✓ bilans; 2.07 bez dopływu (N-9) |
| K-10 podłogówka / PC | 0 niespełnionych, ściany grzewcze wodne, PC ok. 7 kW. | ✓ (N-13 e — sprzeczny tekst modułu) |
| K-12 mostki / woda | R-W2 ✓, R-W3 ✓, POD-G z membraną ✓, długości `wezly` z geometrii ✓, WZ-X1/X2 ✓. Żebro licowane z czołem płyty uzgadnia BO. | ✓ z wyjątkiem N-5, N-6 |
| K-13 decyzja Inwestora (pnącza na kratownicy, osłona PC) | **Brak w modelu i w rejestrze 14.1/14.2.** Skrypt nie zawiera kratownicy, konsol, pasa gruntu ani osłony PC. | ✗ (N-8) |

### 2.2 Weryfikacja koncepcji §6 (pozycje fizyki, wody i instalacji)

| Poz. | Stan | Ocena V2 |
|---|---|---|
| A1 czerpnia / wyrzutnia | Wyrzut poziomy, 10,15 m ≥ 10 m. Wysokość wylotu nad punktami w promieniu 10 m nie jest sprawdzana. | **nowa niezgodność** (N-1) |
| A2 spadki terenu | 2,7–4,0 % w środkach ścian. Lokalny przeciwspadek przy S0-05 i S0-06. | częściowo (N-3, N-4) |
| A3 przelewy D1 | Dno = pokrycie przy wpuście + 0,03…0,04 m. | ✓ |
| A4 PV ponad attyką | +9,863 ≤ +9,876. | ✓ (zapas 13 mm — N-10) |
| A5 cokół | Moduł drenażu podaje 0,31 m. TIN pokazuje 0,04 m przy S0-05. | ✗ (N-3) |
| A6 FX3 | U_w 0,87 ≤ 0,90 przy wymaganiu U_f ≤ 0,80. | ✓ |
| A7 moc podłogówki | 0 niespełnionych. | ✓ |
| B1 odwodnienie płyt | Rynny ukryte i RS7–RS12 są w modelu. Nie ma przelewów awaryjnych rynien, a przepływ PL-3 → PL-2 nie wchodzi do bilansu. | częściowo (N-7) |
| B3 / B4 EP i Φ_HL a Ψ | H_TB 30,6 W/K, Φ_HL 7,41 kW. | ✓ |
| B5 centrala | 365 m³/h (81 % V_nom), okresowo 435 m³/h. | ✓ |
| B6 retencja | NCH-1 28 m², 8,4 m³. | ✓ |
| B7 elektryka | Faza 40,0 A ≤ 40 A ✓. WLZ 0,61 % i DC PV 1,04 % bez zmian. | ✗ (N-11, odłożone do PT) |
| C8 U w nazwach przegród | Zgodne z obliczeniem. | ✓ |
| C11 fałszywe alarmy deszczowej | Typy `nie_dotyczy` / `na_powierzchnie` usunęły alarmy. | ✓ (inne usterki narzędzi — N-13) |

### 2.3 REKOMENDACJE mostków (A–E)

| Poz. | Stan | Ocena V2 |
|---|---|---|
| A: WZ-04 / 05 / 07a | Łącznik 120 mm, λ_eq 0,08: ψ_oi 0,128 / 0,134 / 0,152. | ✓ (WZ-07a nadal „DO POPRAWY”, 0,152) |
| A: WZ-06 attyka z PL-3 | Blok termoizolacyjny 15 cm + łącznik: ψ_oi 0,205. | nadal „DO POPRAWY” (N-15) |
| A: WZ-16a | 0,194. | nadal „DO POPRAWY” (N-15) |
| A: WZ-09a garaż | 0,301, ocena **ZŁY**, linia izolacji przerwana. | ✗ (N-6) |
| B: R-W1 płyty wysunięte | Rynny ukryte, spadek 2 %, RS. | częściowo (N-7) |
| B: R-W2 przelewy | ✓ | ✓ |
| B: R-W3 wywinięcia | ✓ (0,28 m) | ✓ (skutek uboczny: N-1) |
| B: R-W4 cokół DZ2 | OL-5 przed progiem, podest −0,12. Membrana PF2 na −0,295. | częściowo (N-5) |
| B: R-W5 / R-W6 | Podsufitka PS-A jedną płaszczyzną; konwencja obrysów. | ✓ (poza zakresem rysunków) |
| C: drenaż opaskowy | Nie jest wymagany (k_f > 10⁻⁴, ZWG 3,24 m pod spodem fundamentu). Warunek (3), spadki ≥ 2 %, spełniony poza miejscami N-3/N-4. | ✓ z N-3/N-4 |
| D: sekcja `wezly` | Długości z geometrii, WZ-X1/X2 dodane, WZ-07/09 z podwęzłami. | ✓ |
| E: dane do PT | ETA łączników, χ konsol, klasa wilgotności — nadal [DANE PRZYKŁADOWE]. | otwarte (etap PT, poza listą) |

## 3. Problemy nierozwiązane lub nowe

Stopnie: **krytyczny** blokuje PAB, **istotny** wymaga zmiany modelu lub detalu przed PAB, **drobny** do PT albo poprawka narzędzia.

### N-1 (istotny, nowy) — wyrzutnia dachowa za nisko względem punktów w promieniu 10 m
* **Miejsce:** `energia.wentylacja.wyrzutnia` [1,90; 4,00; +10,00], wyrzut poziomy (`tools/buduj_model.py`, `WYRZUTNIA`).
* **Problem:**
  * Wyrzutnia z wylotem poziomym musi być ≥ 0,4 m nad powierzchnią dachu i nad linią najwyższych punktów w promieniu
    10 m.
  * W promieniu 10 m są korona attyki D1 +9,876 (podniesiona w R-W3), wywiewka K1 +9,94 (4,3 m) i PV +9,863.
  * Wylot musi więc być ≥ **+10,34**, a jest na +10,00 (brakuje 0,34 m).
  * Audyt A1 sprawdził tylko nadwyżkę nad pokryciem (0,495 m).
* **Poprawka (jeden z wariantów):**
  * podnieść wylot do ≥ +10,34 i sprawdzić wysokość zabudowy (N-2);
  * albo przenieść K1 poza promień 10 m (lub zakończyć ją zaworem napowietrzającym, jeśli pozwala na to W-139 / WT §125
    ust. 2) i ponownie sprawdzić attykę;
  * albo zastosować wyrzutnię ścienną wg WT §152 ust. 9;
  * albo certyfikowany zestaw zblokowany.
  * Dodać ten warunek do `tools/audyt_wt.py`.
* **Podstawa:** WT §152 ust. 6–13; W-167, R6-43 (brzmienie ustępu do potwierdzenia w t.j. Dz.U. 2022 poz. 1225 [NZW]).

### N-2 (istotny) — do wysokości zabudowy wchodzi dolna krawędź wlotu czerpni, a nie szczyt urządzenia
* **Miejsce:** `CZERPNIA = [11.60, 1.00, 10.00]` („z dolnej krawędzi wlotu”), `WYRZUTNIA` (z wylotu) → `lamela.wskazniki.punkty_najwyzsze()` bierze `v[2]` jako z_top.
* **Problem:**
  * Urządzenia dachowe wlicza się do wysokości zabudowy.
  * Kołpak czerpni i wyrzutni sięga wyżej niż przyjęte +10,00, więc H = 10,27 m jest zaniżone o wysokość kołpaka.
  * Razem z N-1 wynik może przekroczyć rezerwę 10,70 m (W-033).
* **Poprawka:**
  * Dodać w modelu `z_top` czerpni i wyrzutni: maksymalną wysokość urządzenia jako wymaganie („lub równoważne”, bez
    danych konkretnego producenta).
  * `wskazniki` ma brać `max(z, z_top)`.
  * Przeliczyć H i zapisać wynik w §9 koncepcji.
* **Podstawa:** upzp art. 2 pkt 30 lit. a (urządzenia techniczne wliczane); W-033;
  `docs/10_podstawy_prawne/weryfikacja_upzp_art2_definicje.md`.

### N-3 (istotny) — cokół 0,04 m i spadek ku ścianie przy filarze S0-05 (T2 / BR1)
* **Miejsce:** ściana S0-05 (odcinek zach. garażu, x 11,70, y 9,35–9,68). Punkty `teren_projekt()` — strefy T2 i BR1
  stykają się na x 11,70.
* **Problem:**
  * Liniowy TIN rzędnych projektowanych daje tu teren −0,04…−0,06, czyli cokół 0,04 m. Spadek na 1,5 m wynosi −1 %, więc
    woda płynie ku ścianie.
  * Odcinek leży poza strefami drzwi z odwodnieniem liniowym: strefa FX3 kończy się na y 9,35, strefa BR1 zaczyna się na
    x 11,75.
  * Nawierzchnia podestu jest wyżej niż posadzka garażu (−0,10) i ok. 0,25 m nad membraną PF2 (−0,295).
  * Moduł drenażu tego nie wykrywa, bo interpoluje metodą IDW z 60 punktów obwodu (N-13 a). Wynik „cokół 0,31 m” w 14.2
    nie jest więc potwierdzony.
* **Poprawka:**
  * Przedłużyć OL-3 albo korytko do narożnika S0-05 i nadać podestowi T2 spadek od ściany S0-05.
  * Albo włączyć filar do strefy progowej: uszczelnienie pionowe KMB lub membraną ≥ 0,15 m nad nawierzchnią, połączone
    z membraną PF2 (detal PT-AR-D-03/-14).
  * W drenaz.py liczyć teren TIN-em (`lamela.wskazniki.Teren.projekt`), z krokiem ≤ 0,10 m.
* **Podstawa:** brief §9 pkt 4 i 6; W-019; DIN 18533-1 (pomocniczo: ≥ 0,15 m w strefie progowej, 0,30 m poza nią).

### N-4 (drobny) — lokalnie cokół < 0,30 m i spadek < 2 % (TIN)
* **Miejsce:**
  * S0-02 przy x ≈ 13,6 (między strefą DZ3/T3 a ścieżką U6): cokół 0,268 m;
  * S0-03 obok strefy DZ2 (y 4,5 i 6,2–6,3): 0,288–0,295 m;
  * S0-06 przy x 9,55–9,65 (krawędź podestu T2): spadek 0–2 m od −0,8 % do +2,0 %.
* **Problem:** trójkąty TIN łączą pierścień 0 m (−0,33) z punktami podestów (−0,02 / −0,12), co zawyża teren przy
  krawędziach stref.
* **Poprawka:** dodać punkty projektowane na krawędziach stref T2, T3 i DZ2 (np. −0,33 w odległości 0,3 m od krawędzi
  podestu, wzdłuż lica) albo obrzeże z korytkiem; sprawdzić TIN-em.
* **Podstawa:** brief §9 pkt 4 i 6; W-019.

### N-5 (istotny, nowy po K-12) — hydroizolacja posadzki garażu poniżej nawierzchni przy BR1, DZ2 i T2
* **Miejsce:** POD-G na PF2: membrana SBS na ≈ −0,295, XPS 10 cm, jastrych do −0,10; fartuch bramy −0,12 (OL-1 dopiero
  2,3 m dalej), podest DZ2 −0,12, podest T2 −0,02…−0,06 przy S0-05.
* **Problem:**
  * Warstwy XPS i jastrych garażu leżą w „wannie” 0,17–0,25 m poniżej nawierzchni zewnętrznej.
  * Model i rejestr nie opisują zakończenia membrany w progach BR1 i DZ2 ani połączenia z uszczelnieniem cokołu. Linia
    niebieska ma przerwę na krawędzi PF2 w otworach.
  * Woda z podbudowy fartucha może wejść pod jastrych.
* **Poprawka:**
  * Belka progowa z betonu wodoszczelnego na PF2 do rzędnej posadzki w świetle BR1 i DZ2, z membraną wywiniętą na belkę.
  * Uszczelnienie cokołu ≥ 0,15 m nad nawierzchnią.
  * Korytko odwodnienia w progu bramy albo bezpośrednio przed nim (OL-1 może zostać jako drugie).
  * XPS garażu zakończony na belce; opisać to w `przegrody.POD-G.uwagi` i w detalu PT-AR-D-14. Uzgodnić z BO (K-5).
* **Podstawa:** brief §9 pkt 1 (linia niebieska) i pkt 4 (progi, cokół); WT §315–317; DIN 18533-1 (pomocniczo).

### N-6 (istotny) — WZ-09a (SWG na płycie): nadal ocena „ZŁY”, a model 2D nie odwzorowuje uskoku PF1/PF2
* **Miejsce:** `wezly[WZ-09]` (`blok_u_podstawy` BET_KOM_600, h 0,24); `mostki2d/wezly_dod.wezel_garaz_plyta`.
* **Problem:**
  * ψ_oi = 0,301 W/(m·K) przy wartości domyślnej 0,20 i dobrej praktyce 0,10.
  * Linia izolacji jest przerwana na drodze TYNK_GIPS → BET_KOM_600 → ZB_C25 → TYNK_CW.
  * Warianty V2 (`wz09.py`):
    * bez bloku: 0,339;
    * blok betonu komórkowego 400 (24 cm): 0,295;
    * blok termoizolacyjny λ 0,045 (24 cm): 0,284;
    * bez XPS nad PF2: 0,478.
  * Blok z betonu komórkowego 600 (λ 0,16) prawie nic nie daje. Mostek tworzy ciągła płyta pod SWG.
  * Generator węzła zakłada jedną płytę na rzędnej płyty domu i układa POD-G na niej: posadzka garażu wychodzi na +0,05
    zamiast −0,10. Pomija też uskok 0,15 m i żebra ZF16/ZF17 do −0,85. Wynik nie dotyczy więc geometrii modelu.
  * f_Rsi = 0,903 jest spełnione.
* **Poprawka:**
  * BO (K-5): przerwa termiczna płyty w osi SWG, np. XPS pionowy w uskoku PF1/PF2 z łącznikami zbrojenia z ETA
    („lub równoważne”), albo docieplenie czoła uskoku i żebra od strony garażu.
  * Nośny blok termoizolacyjny (λ ≤ 0,05) zamiast betonu komórkowego 600.
  * W generatorze odwzorować uskok i żebro, potem przeliczyć.
  * Jeśli ocena „ZŁY” zostaje, zapisać świadomą decyzję w rejestrze (f_Rsi spełnione, ψ w H_TB).
* **Podstawa:** brief §9 pkt 1–2 (ciągłość linii czerwonej, symulacja wszystkich węzłów); W-248; PN-EN ISO 10211;
  REKOMENDACJE A.

### N-7 (istotny) — rynny ukryte za blendą: bez przelewów awaryjnych i z niepełnym bilansem PL-2
* **Miejsce:** `wsporniki_plyty[PL-E, PL-DA, PL-2, PL-3, PL-D].odwodnienie = rynna_ukryta`. Moduł deszczowy pokazuje
  „Przelewy 0×”.
* **Problem:**
  * Płyty mają spadek 2 % ku czołu. Zapchana rynna za blendą cofa wodę na płytę aż do wysokości korony blendy, czyli
    przy blendzie 0,10 m do 5 m od czoła, pod ścianę i próg.
  * Model nie ma ani przelewu (obniżenia lub rzygacza w blendzie), ani rzędnej korony blendy względem wywinięcia przy
    ścianie.
  * PL-2 przyjmuje też wodę z PL-3 (RS11/RS12). Moduł liczy RS7 i RS10 tylko z PL-2 (0,53 l/s), a powinno być ok.
    1,06 l/s na wylot. Rynna 100 mm przy spadku 0,5 % ma przepustowość „≥ 1 l/s” (REKOMENDACJE R-W1), więc brak zapasu.
* **Poprawka:**
  * Dla każdej rynny ukrytej podać w modelu przelew awaryjny (obniżenie blendy lub rzygacz w czole) z dnem ≥ 0,03 m
    poniżej wywinięcia hydroizolacji przy ścianie i przy progu.
  * Sprawdzić przepustowość rynny wg PN-EN 12056-3 z F_R (rynna ukryta, ryzyko zalania) dla PL-2 razem z PL-3.
  * Dodać dopływ PL-3 → PL-2 w `deszczowa.py` (odbiornik RS jako pole).
* **Podstawa:** brief §9 pkt 3 (przelew awaryjny dla każdego pola, PN-EN 12056-3); W-142.

### N-8 (istotny) — decyzja Inwestora K-13 (pnącza na kratownicy, osłona PC) niewprowadzona
* **Miejsce:** elewacja S0-02 (6,4 × 3,85 m) i jednostka PC (16,8; −1,05). `tools/buduj_model.py` nie ma kratownicy,
  konsol, pasa gruntu, donic ani osłony z lamel. Rejestr 14.1 (D-12 odroczona) i 14.2 nie wspominają o K-13.
* **Problem:**
  * Decyzja Inwestora z 25.09 (godz. 08:27) jest wiążąca.
  * Za S0-02 są pomieszczenia ogrzewane 0.11 i 0.12, więc konsole kratownicy w ETICS to mostki punktowe χ.
  * Pas gruntu lub donice przy cokole zmieniają teren i odwodnienie (N-4).
  * Osłona PC musi zachować strefę R290 i przepływ powietrza.
* **Poprawka:**
  * Wprowadzić kratownicę z konsolami na przekładkach termicznych i dodać węzeł χ (typ `kotwa`, WZ-14 lub nowy) —
    wartość χ jako wymaganie („lub równoważne”).
  * Pas gruntu lub donice z odwodnieniem, bez przebić hydroizolacji cokołu.
  * Osłona z lamel wokół PC: strefa 1,0 m bez otworów, wpustów i zagłębień; odstępy wg DTR.
  * Zapisać w 14.x.
* **Podstawa:** decyzja Inwestora (`poprawki_runda2_wejscie.md` K-13); brief §9 pkt 1–2; W-156; W-024.

### N-9 (istotny, nowy po A3 I-8) — pom. techniczne 2.07: wywiew bez dopływu powietrza
* **Miejsce:** pomieszczenie 2.07: `went` {naw 0, wyw 15}. Drzwi O2-12 typu D4A są „BEZ kratki, uszczelka obwodowa
  i próg z uszczelką opadającą”. W pomieszczeniu jest wyłaz WYL1.
* **Problem:**
  * Wywiew 15 m³/h nie ma skąd pobrać powietrza.
  * W pomieszczeniu powstaje podciśnienie. Zimne powietrze wchodzi nieszczelnościami wyłazu, co grozi kondensacją przy
    WYL1, a centrala pracuje z niezbilansowanym pomieszczeniem.
* **Poprawka:** jeden z wariantów:
  * nawiew 15 m³/h do 2.07 (bilans pomieszczenia 0);
  * akustyczny przepust transferowy (tłumiona kratka) w DZ18A lub w drzwiach, przy zachowaniu R_w ≥ 32 dB;
  * rezygnacja z wywiewu z 2.07, jeśli centrala nie wymaga wentylacji pomieszczenia (DTR).
* **Podstawa:** PN-83/B-03430/Az3 (dopływ powietrza do pomieszczeń z wywiewem przez otwory lub szczeliny w drzwiach)
  [NZW]; W-161 (przepływ do pomieszczeń wywiewnych); W-230 (akustyka).

### N-10 (drobny) — PV: niespójne parametry i brak tolerancji wysokości
* **Miejsce:** `energia.pv`: `uklad: EW10`, a jednocześnie `azymut 180` i `nachylenie 10`; z_max D1 +9,863 wobec korony
  +9,876.
* **Problem:**
  * EP liczy PV jako moduły skierowane na południe (4 985 kWh/a), a moduł PT-IE jako układ EW10 (5 610 kWh/a).
  * Zapas 13 mm pod koroną attyki nie mieści tolerancji stelaża ani izolacji spadkowej.
  * PR 0,78 dla zacienienia D4 przez bryłę B to [ZAŁ].
* **Poprawka:**
  * Azymut i nachylenie podać dla każdego pola (EW: 90° i 270°).
  * Wymagana wysokość stelaża ≤ 0,28 m nad pokryciem lokalnym (tolerancja ≥ 2 cm).
  * Symulacja zacienienia D4 w PT-IE.
* **Podstawa:** W-033, D-15; metodologia EP (Dz.U. 2015 poz. 376 ze zm.); W-194.

### N-11 (drobny) — instalacja elektryczna i PV: moduł nie czyta układu pól, spadki napięcia
* **Miejsce:** `lamela.obliczenia.elektryka.pv` („Dach PV: D1 … 34,0 m² ≤ 47,2 m²”, L_DC 21,9 m); raport 07_obwody
  (WLZ).
* **Problem:**
  * Sprawdzenie „moduły mieszczą się na D1” i długość trasy DC nie odpowiadają faktycznemu układowi 7 + 8 na D1 i D4.
  * Spadek napięcia DC wynosi 1,04 % > 1,00 % [ZAŁ], WLZ 0,61 % > 0,50 %.
* **Poprawka:**
  * `pv.py` ma czytać `energia.pv.pola`: łańcuchy po polach, trasy DC osobno dla D1 i D4.
  * Przekrój DC 10 mm² lub falownik bliżej pól; WLZ o większym przekroju albo RG bliżej ZKP (etap PT-IE).
* **Podstawa:** W-194; W-185 (N SEP-E-002) [NZW].

### N-12 (drobny) — mały zapas EP bez PV bez próby szczelności; dane c.w.u. w EP niespójne
* **Miejsce:** `energia.n50 = 1,0` (cel); `energia.cwu.zasobnik = Z250` (strata postojowa przykładowego zasobnika
  250 dm³) przy V_projekt = 400 dm³; w EP η_W,d = 0,60 bez cyrkulacji, a moduł wody zakłada cyrkulację czasową.
* **Problem:**
  * Bez PV i przy n50 = 4 h⁻¹ (wartość metodologii, gdy nie ma próby) EP = 67,1 (zapas 4 %).
  * Większa strata zasobnika 400 dm³ i pompa cyrkulacyjna ten zapas zmniejszą.
* **Poprawka:**
  * Wpisać w opis PB/PT obowiązkową próbę szczelności wg PN-EN ISO 9972 (n50 ≤ 1,0).
  * Zasobnik 400 dm³ jako wymaganie z klasą strat („lub równoważny”); cyrkulację ujednolicić między modułem wody i EP.
  * PV pozostaje elementem obowiązkowym.
* **Podstawa:** WT §329, W-240; brief §9 pkt 5; metodologia EP.

### N-13 (drobny) — usterki narzędzi obliczeniowych (bez zmiany wyników formalnych)
* (a) `sanitarne/drenaz.py`:
  * cokół i teren z `dane.teren_z` (IDW z potęgą 2 na wszystkich punktach) na 60 punktach obwodu;
  * spadki tylko w środkach ścian od 0,3 m;
  * nie wykrywa N-3 i N-4.
  * Poprawka: TIN `wskazniki.Teren.projekt`, krok ≤ 0,10 m, pas 0–2 m od lica.
* (b) `mostki2d/karta.py`: dla WZ-04/05 zostaje „! UWAGA: odprowadzenie wody z krawędzi płyty nieokreślone”, mimo że
  płyty mają `odwodnienie: rynna_ukryta`. Poprawka: czytać `wsporniki_plyty[].odwodnienie`.
* (c) `energia/obudowa`: stos ST2Z = POD-1 (ma już ZB 22 cm i tynk) + płyta ZB 22 cm + SUF-ZEW. Płyta jest liczona
  podwójnie (U 0,1265 zamiast ok. 0,128, podwójna masa). Poprawka: dla stropów nad powietrzem brać warstwy POD-1 bez
  konstrukcji albo pominąć płytę.
* (d) `sanitarne/deszczowa.py`: raportuje „przyjęta niecka 19,5 m²” (własny dobór minimalny) zamiast 28 m² z
  `dzialka.retencja`. Poprawka: sprawdzać niecko z modelu.
* (e) `sanitarne/ogrzewanie.py`: stały tekst „łazienki — dodatkowo grzejnik drabinkowy z grzałką” przeczy decyzji 14.2
  (ściany grzewcze wodne, bez grzałek — EP). Poprawka: tekst warunkowy.
* (f) `energia.psi_wariant: domyslna` i etykieta „Ψ: przykładowa” w zestawieniu, choć Ψ pochodzą z symulacji.
  Poprawka: zmienić etykietę i wariant.
* **Podstawa:** rzetelność obliczeń (RPB §20 — obliczenia jako część PT); brief §9.

### N-14 (drobny) — K-2: średnica „dojrzałej” korony lipy DR1
* **Miejsce:** `drzewa[DR1].sr_korony = 7,0` (komentarz: „rzut dojrzałej korony r 3,5 m”); pień 5,0 m od krawędzi
  NCH-1.
* **Problem:** lipa drobnolistna w wieku dojrzałym ma zwykle koronę wyraźnie szerszą niż 7 m [do weryfikacji w źródle
  dendrologicznym lub katalogu szkółkarskim]. Przy r ≥ 4 m odstęp 1,0 m od niecki (W-144) nie jest zachowany.
* **Poprawka:** przyjąć średnicę korony dojrzałego drzewa ze źródła albo gatunek lub odmianę o węższej koronie, albo
  przesunąć DR1 lub NCH-1 (pień ≥ r + 1,0 m od krawędzi niecki).
* **Podstawa:** W-144 [ZAŁ]; K-2.

### N-15 (drobny) — mostki „DO POPRAWY” bez decyzji
* **Miejsce:** WZ-06 ψ_oi 0,205 (dobra praktyka 0,15), WZ-16a 0,194, WZ-07a 0,152, WZ-02 0,171 / WZ-03 0,195 (ocena
  DOBRY przy wartości domyślnej).
* **Problem:** 14.2 F przekazuje je do PT-AR-D bez rozstrzygnięcia. f_Rsi jest spełnione (≥ 0,851).
* **Poprawka:** decyzja w PT-AR-D (attyka lekka nad PL-3, obłożenie belek B3–B5 wełną na całą wysokość) albo świadoma
  akceptacja zapisana w rejestrze.
* **Podstawa:** brief §9 pkt 2; W-248, W-272; REKOMENDACJE A.

## 4. Stwierdzenia rejestru 14.2, których V2 nie potwierdza

* „cokół ≥ 0,31 m poza strefami drzwi z OL” (14.2 A i D) — na TIN minimum wynosi 0,04 m przy S0-05 (N-3).
* „Wysokość zabudowy bez wpływu (najwyżej czerpnia/wyrzutnia +10,00)” (14.2 A, R-W3) — podniesienie attyki D1 obniżyło
  zapas wyrzutni względem punktów w promieniu 10 m (N-1), a +10,00 to dolna krawędź wlotu (N-2).
* „WZ-09a … przyjęta” (14.2 B) — ψ pozostało 0,301 z oceną ZŁY, a blok z betonu komórkowego 600 prawie nie działa
  (N-6).
* Brak wpisu o K-13 (N-8).

## 5. Testy (przebieg V2, bez zmian w repozytorium)

* `tools/test_obliczenia_fizyka.py`: 24/24 zaliczonych.
* `tools/test_obliczenia_instalacje.py`: 22/22 zaliczonych.
* `tools/test_wskazniki.py`: ZALICZONE.
* `tools/test_pipeline.py`:
  * w pierwszym przebiegu 24 zaliczonych, 1 niezaliczony;
  * w tym samym czasie inne sesje (weryfikator V1) uruchamiały testy i zapisywały do `projekt/08_obliczenia/demo_test`;
  * wynik drugiego przebiegu jest w sekcji 5.1.

## Aneks. Odtworzenie

```bash
# model identyczny ze skryptem: import tools/buduj_model.py z OUT → katalog tymczasowy, cmp z model/*.yaml
PYTHONPATH=src python3 tools/mostki_budynku.py --out <tmp>/mostki
PYTHONPATH=src python3 -m lamela.obliczenia.fizyka_energia --budynek model/budynek.yaml --dzialka model/dzialka.yaml --out <tmp>/fe
PYTHONPATH=src python3 -m lamela.obliczenia.instalacje --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
    --wyposazenie model/wyposazenie.yaml --instalacje model/instalacje.yaml --phi-hl energia --wentylacja energia --out <tmp>/is
# teren: TIN rzędnych projektowanych (lamela.wskazniki.Teren.projekt), obwód P0 co 0,10 m — skrypt teren_tin.py (scratchpad V2)
```

### 5.1 Drugi przebieg `test_pipeline`

* Wynik: 24 zaliczonych, 1 niezaliczony.
* Niezaliczony: `test_podglad_www`, `playwright … Page.screenshot: Timeout 30000ms exceeded`. To limit czasu zrzutu
  ekranu z przeglądarki przy obciążonej maszynie (kilka sesji liczyło równolegle). Nie jest to błąd modelu ani obliczeń.
* Test zaliczał się w rundzie 2 (rejestr 14.2 D). Do powtórzenia bez obciążenia.
* Wszystkie testy modelu, IR i obliczeń są zaliczone.
