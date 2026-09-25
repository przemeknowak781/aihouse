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
