# Audyt A1 — zgodność koncepcji ostatecznej z WT i MPZP (obliczenia z modelu)

Wygenerowano: 2026-09-25 skryptem `tools/audyt_wt.py` (uruchomienie: `python3 tools/audyt_wt.py`). Model: `model/budynek.yaml` (wersja 1.0, stadium: koncepcja ostateczna (synteza W2 + przeszczepy W1/W3 + poprawki J1–J3)), `model/dzialka.yaml`; wartości progowe z `docs/10_podstawy_prawne/wymagania.yaml` (418 wpisów). Model nie był modyfikowany.

**Wynik kontroli automatycznych:** 0 × NIEZGODNE, 4 × UWAGA, 174 × OK, 3 × INFO.


## 1. Niezgodności i uwagi (z kontroli automatycznych)

| # | Status | Sekcja | Element / miejsce | Parametr | Wartość | Wymóg | Podstawa | Proponowana poprawka |
|---|---|---|---|---|---|---|---|---|
| 1 | **UWAGA** | Wysokości | 0.15 Schowek pod schodami (h 1,40–2,20) | strefy h pod schodami | ≥2,20: 0,00 m²; 1,40–2,20: 1,49 m²; <1,40: 0,00 m²; h_min 1,40 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] | część o h < 2,00 m opisać jako schowek pod schodami (nie pomieszczenie); w PU liczyć strefami (100/50/0 %) — wg audytu 0,75 m² zamiast 0,72 m² z 'wys: 1,90' |
| 2 | **UWAGA** | Wysokości | 0.16 Schowek pod spocznikiem (h < 1,40) | strefy h pod schodami | ≥2,20: 0,00 m²; 1,40–2,20: 0,00 m²; <1,40: 2,93 m²; h_min 1,39 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] | część o h < 2,00 m opisać jako schowek pod schodami (nie pomieszczenie); w PU liczyć strefami (100/50/0 %) — wg audytu 0,00 m² zamiast 1,46 m² z 'wys: 1,90' |
| 3 | **UWAGA** | Wentylacja | wyrzutnia ↔ okno w dachu SW1 — wyrzutnia [1.9, 4.0, 10.0]; SW1 [6.0, 7.35]…[8.3, 8.55], wierzch +9,75 | odległość / wylot ponad oknem | 5,29 m / 0,25 m | 3–10 m ⇒ wylot ≥ 1,00 m nad górną krawędzią okna (≥ +10,75) | WT §152 ust. 12 [W-167]; R6-43 | (a) SW1 jako świetlik NIEOTWIERANY bez funkcji wentylacyjnej i zapis interpretacji w opisie (przepis dotyczy okien) — rekomendowane; (b) wylot wyrzutni ≥ +10,75 — koliduje z wys. zabudowy ≤ 11,00 m (MPZP); (c) ≥ 10 m od SW1 — niewykonalne na D1 przy ≥ 3 m od krawędzi nad oknami |
| 4 | **UWAGA** | Zagospodarowanie | PC-JZ (jedn. zewn. PC) | elewacja, przy której stoi jednostka | S (x 24,40, y 31,65 w ukł. działki; 0,75 m od lica) | N lub E (TWARDE ZAŁOŻENIA) | TWARDE ZAŁOŻENIA (energia i światło); W-024 (hałas) | wariant E: przy ścianie wsch. pom. techn. 0.12 / garażu (jednostka gł. ≈ 0,6 m, 0,3 m od lica ⇒ x_dz ≈ 26,6–27,2, ≈ 4,8 m od granicy E: ≥ 3,0 wg założeń, lecz < 6,0 wg W-024 — wymaga obliczenia hałasu L_Aeq,N ≤ 40 dB); elewacja N zajęta przez podjazd i wejście. Jeśli jednostka zostaje od S — wpisać do koncepcji uzasadnienie odstępstwa (W-024: ≥ 6,0 m od granicy E; krótkie przewody do 0.12), ekran akustyczny od tarasu T1/T3 i obliczenie hałasu na tarasie i granicy E |

## 2. Wskaźniki MPZP i wysokość

| Wskaźnik | Wartość | Wymóg | Status |
|---|---|---|---|
| linia zabudowy — najdalej wysunięty element (+ = przekroczenie) | -0,95 m (T2) | ≤ 0,00 | OK |
| pow. zabudowy (1) obrys ścian zewn. wszystkich kondygnacji (lamela.wskazniki) — A_z | 187,50 m² (11,7 %) | ≤ 480,00 m² | OK |
| pow. zabudowy (2) kontrolnie z płytami wysuniętymi (lamela.wskazniki) — A_z+ | 218,08 m² (13,6 %); metoda audytu: 217,86 m² | ≤ 480,00 m² | OK |
| intensywność zabudowy — Σ pow. kondygnacji nadziemnych / pow. działki | 396,39 / 1600,00 = 0,248 | 0,05–0,80 | OK |
| pow. biologicznie czynna (teren) — PBC | 1270,23 m² (79,4 %) | ≥ 800,00 m² | OK |
| miejsca postojowe — liczba (garaż + zewn.) | 4 (2 w garażu) | ≥ 2 | OK |
| kondygnacje nadziemne — liczba | 3 | ≤ 3 | OK |
| D1 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D2 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D3 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D4 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| ogrodzenie [0.0, 50.0]→[17.6, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| ogrodzenie [18.6, 50.0]→[20.3, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| ogrodzenie [25.9, 50.0]→[32.0, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| wysokość zabudowy (upzp art. 2 pkt 30 lit. a — lamela.wskazniki) — od średniej t_śr = (101,29 + 101,48)/2 = 101,38 do wyrzutnia wentylacji (dachowa, szczyt urządzenia) (+10,200) | 10,47 m (informacyjnie od t_min 101,29: 10,56 m) | ≤ 11,00 (z rezerwą ≤ 10,70) | OK |
| wysokość budynku wg WT §6 (lamela.wskazniki) — teren przy wejściu O0-03: 101,30 → wierzch D1 z izol. (+9,626) | 9,97 m | ≤ 12,00 (N); ≤ 11,00 (MPZP) | OK |

Powierzchnie kondygnacji (obrys zewnętrzny): P0 181,78 m², P1 117,81 m², P2 96,80 m².
PBC: teren 1270,23 m²; powierzchnie wyłączone 331,41 m²; rezerwa — dach zielony (50 %) 29,53 m² (nie wliczona).
Teren na obwodzie ścian zewnętrznych (lamela.wskazniki — niższa z rzędnych istn./proj.): t_min 101,29, t_max 101,48, t_śr 101,38 m n.p.m.; ±0,00 = 101,65 m n.p.m.; najwyższy punkt: wyrzutnia wentylacji (dachowa, szczyt urządzenia) (+10,200); wysokość zabudowy 10,47 m (informacyjnie od t_min 10,56 m). WT §6: wejście O0-03, teren 101,30 m n.p.m. → 9,97 m.

## 3. Pomieszczenia — powierzchnie, wysokości, oświetlenie

| Nr | Nazwa | Kat. | Pobyt | Pow. netto [m²] | Pow. do PU [m²] | h w świetle [m] | h min / pod belką | Okna | A_ok/A_p (ościeżn.) |
|---|---|---|---|---|---|---|---|---|---|
| 0.01 | Wiatrołap | ruchu | — | 3,89 | 3,89 | 2,77 | — | O0-10 | 0,109 |
| 0.02 | Hol | ruchu | — | 4,44 | 4,44 | 2,77 | — | — | — |
| 0.03 | WC gościnne | pomocnicza | — | 2,32 | 2,32 | 2,53 | — | — | — |
| 0.04 | Klatka schodowa | ruchu | — | 2,78 | 2,78 | otwarta (pustka) |  / 2,50 (B8) | — | — |
| 0.05 | Spiżarnia | pomocnicza | — | 1,03 | 1,03 | zmienna 2,22…2,75 | 2,22 | — | — |
| 0.15 | Schowek pod schodami (h 1,40–2,20) | pomocnicza | — | 1,49 | 0,75 | zmienna 1,40…2,19 | 1,40 | — | — |
| 0.16 | Schowek pod spocznikiem (h < 1,40) | pomocnicza | — | 2,93 | 0,00 | zmienna 1,39…1,40 | 1,39 | — | — |
| 0.06 | Salon + jadalnia + kuchnia | podstawowa | tak | 54,44 | 54,44 | 2,77 | — | O0-01, O0-02, O0-03, O0-04, O0-05, O0-11 | 0,592 |
| 0.07 | Pas komunikacyjny przy schodach | ruchu | — | 3,51 | 3,51 | 2,77 | — | — | — |
| 0.08 | Przedpokój gościnny | ruchu | — | 1,44 | 1,44 | 2,77 | — | — | — |
| 0.09 | Łazienka gościnna (natrysk) | pomocnicza | — | 3,84 | 3,84 | 2,53 | — | O0-13 | 0,073 |
| 0.10 | Pokój gościnny / gabinet | podstawowa | tak | 12,52 | 12,52 | 2,77 | — | O0-12 | 0,176 |
| 0.11 | Przedsionek gospodarczy | ruchu | — | 7,18 | 7,18 | 2,75 | — | — | — |
| 0.12 | Pomieszczenie techniczne | techniczna | — | 8,85 | 8,85 | 2,75 | — | — | — |
| 0.13 | Garaż 2-stanowiskowy | pomocnicza | — | 37,42 | 37,42 | 2,70 | — | — | — |
| 1.01 | Hol | ruchu | — | 14,09 | 14,09 | 2,77 | — | — | — |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | podstawowa | tak | 28,36 | 28,36 | 2,77 | — | O1-01, O1-13, O1-14, O1-02 | 0,363 |
| 1.03 | Pokój dziecka 1 | podstawowa | tak | 13,19 | 13,19 | 2,77 | — | O1-06 | 0,167 |
| 1.04 | Pokój dziecka 2 | podstawowa | tak | 12,52 | 12,52 | 2,77 | — | O1-05 | 0,176 |
| 1.05 | Łazienka dzieci (wanna) | pomocnicza | — | 5,50 | 5,50 | 2,53 | — | O1-03 | 0,059 |
| 1.06 | Klatka schodowa | ruchu | — | 0,49 | 0,49 | otwarta (pustka) |  / 2,50 (B9) | — | — |
| 1.07 | WC z natryskiem | pomocnicza | — | 4,08 | 4,08 | 2,53 | — | — | — |
| 1.08 | Pralnia z suszarnią | pomocnicza | — | 6,64 | 6,64 | 2,77 | — | O1-04 | 0,069 |
| 2.01 | Hol | ruchu | — | 5,74 | 5,74 | 2,77 | — | — | — |
| 2.02 | Sypialnia rodziców | podstawowa | tak | 21,43 | 21,43 | 2,77 | — | O2-01, O2-04 | 0,436 |
| 2.03 | Garderoba (przedpokój apartamentu) | pomocnicza | — | 10,49 | 10,49 | 2,77 | — | O2-02 | 0,158 |
| 2.04 | Łazienka rodziców | pomocnicza | — | 5,51 | 5,51 | 2,53 | — | O2-06 | 0,059 |
| 2.05 | Gabinet / pokój gościnny okazjonalny | podstawowa | tak | 16,25 | 16,25 | 2,77 | — | O2-03, O2-05 | 0,355 |
| 2.06 | Klatka schodowa (wyjście z biegu 2, pustka) | ruchu | — | 0,24 | 0,24 | otwarta (pustka) |  / 2,50 (B10) | O2-07 | 8,598 |
| 2.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | techniczna | — | 5,90 | 5,90 | 2,77 | — | — | — |
| 0.14 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |
| 1.09 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |
| 2.08 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |

PU mieszkalna (podstawowa 158,71 + pomocnicza bez garażu 40,16 + komunikacja bez klatek 40,29) = **239,16 m²**; PU wg PN-ISO 9836 (podstawowa + pomocnicza, bez garażu) = 198,87 m²; garaż 37,42 m²; techniczna 16,10 m²; klatki schodowe (wyłączone) 3,51 m². Założenia: światło ościeżnicy = światło muru − 2 × 0,08 m; sufit podwieszany SUF_GK obniża o 0,25 m.

## 4. Schody

| Bieg | z0 [m] | stopni | szer. model / w świetle ścian [m] | długość [m] | prześwit min [m] (element) |
|---|---|---|---|---|---|
| SCH1/bieg1 | 0,000 | 9 | 1,135 / 1,135 | 2,24 | 2,325 (B8) |
| SCH1/bieg2 | 1,575 | 9 | 1,130 / 1,130 | 2,24 | 2,763 (SCH2/bieg2) |
| SCH2/bieg1 | 3,150 | 9 | 1,135 / 1,135 | 2,24 | 2,325 (B9) |
| SCH2/bieg2 | 4,725 | 9 | 1,130 / 1,130 | 2,24 | 2,805 (D1) |

## 5. Odległości od granic działki (WT §12) — wartości minimalne na element

| Element | Rodzaj | Granica | Odległość [m] | Wymóg [m] |
|---|---|---|---|---|
| RS5 | rura spustowa zewn. | E | 5,61 | 4,00 |
| S0-03 | ściana zewn. P0 (z otworami) | E | 5,73 | 4,00 |
| PL-D | płyta wysunięta/okap/daszek | E | 5,73 | 4,00 |
| D4/przelew@[18.465, 8.6] | przelew awaryjny (rzygacz ~0,15 m) | E | 5,79 | 4,00 |
| D4/przelew@[18.465, 0.9] | przelew awaryjny (rzygacz ~0,15 m) | E | 5,79 | 4,00 |
| D4 | dach z attyką | E | 5,94 | 4,00 |
| PL-E | płyta wysunięta/okap/daszek | E | 10,60 | 4,00 |
| T3 | taras naziemny/podest | E | 10,90 | 1,50 |
| PL-C2 | płyta wysunięta/okap/daszek | E | 10,95 | 4,00 |
| PL-C1 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| PL-2 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| PL-3 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| LAM-E | lamele (osłona elewacji) | E | 11,87 | 4,00 |
| LAM-S | lamele (osłona elewacji) | E | 11,95 | 4,00 |
| S1-02 | ściana zewn. P1 (z otworami) | E | 12,10 | 4,00 |
| S2-02 | ściana zewn. P2 (z otworami) | E | 12,10 | 4,00 |
| S2-04 | ściana zewn. P2 (bez otworów) | E | 15,60 | 3,00 |
| S0-01 | ściana zewn. P0 (z otworami) | S | 32,40 | 4,00 |
| S0-02 | ściana zewn. P0 (z otworami) | S | 32,40 | 4,00 |
| S1-01 | ściana zewn. P1 (z otworami) | S | 32,40 | 4,00 |
| S2-01 | ściana zewn. P2 (z otworami) | S | 32,40 | 4,00 |
| T1 | taras naziemny/podest | W | 4,30 | 1,50 |
| OB-A | płyta wysunięta/okap/daszek | W | 5,18 | 4,00 |
| PL-2 | płyta wysunięta/okap/daszek | W | 5,20 | 4,00 |
| PL-3 | płyta wysunięta/okap/daszek | W | 5,20 | 4,00 |
| PS-A | płyta wysunięta/okap/daszek | W | 5,20 | 4,00 |
| PL-E | płyta wysunięta/okap/daszek | W | 5,80 | 4,00 |
| LAM-W | lamele (osłona elewacji) | W | 6,07 | 4,00 |
| LAM-S | lamele (osłona elewacji) | W | 6,15 | 4,00 |
| S2-08 | ściana zewn. P2 (z otworami) | W | 6,30 | 4,00 |
| IZ-ST2Z | płyta wysunięta/okap/daszek | W | 6,30 | 4,00 |
| D1 | dach z attyką | W | 6,50 | 4,00 |
| S0-07 | ściana zewn. P0 (z otworami) | W | 7,30 | 4,00 |
| S1-04 | ściana zewn. P1 (z otworami) | W | 7,30 | 4,00 |
| OB-A2 | płyta wysunięta/okap/daszek | W | 7,30 | 4,00 |
| D2/przelew@[-0.09, 8.2] | przelew awaryjny (rzygacz ~0,15 m) | W | 7,36 | 4,00 |
| D2 | dach z attyką | W | 7,51 | 4,00 |
| SL9 | słup | W | 7,51 | 4,00 |
| SL10 | słup | W | 7,51 | 4,00 |
| SL11 | słup | W | 7,51 | 4,00 |
| SL12 | słup | W | 7,51 | 4,00 |
| RS3 | rura spustowa zewn. | W | 7,94 | 4,00 |
| SL1 | słup | W | 9,74 | 4,00 |
| SL13 | słup | W | 11,10 | 4,00 |
| SL14 | słup | W | 11,10 | 4,00 |
| SL15 | słup | W | 11,10 | 4,00 |
| S2-06 | ściana zewn. P2 (bez otworów) | W | 11,18 | 3,00 |
| PL-C1 | płyta wysunięta/okap/daszek | W | 11,20 | 4,00 |
| PL-C2 | płyta wysunięta/okap/daszek | W | 11,20 | 4,00 |
| D1/przelew@[3.785, 5.7] | przelew awaryjny (rzygacz ~0,15 m) | W | 11,24 | 4,00 |
| SL21 | słup | W | 11,30 | 4,00 |
| SL7 | słup | W | 11,55 | 4,00 |
| SL2 | słup | W | 11,64 | 4,00 |
| S0-05 | ściana zewn. P0 (bez otworów) | W | 19,30 | 3,00 |

Najbardziej wysunięty ku drodze element budynku leży 0,95 m przed nieprzekraczalną linią zabudowy (po stronie działki).

## 6. Pełna lista kontroli

| Sekcja | Element | Parametr | Wartość | Wymóg | Status | Podstawa |
|---|---|---|---|---|---|---|
| Wysokości | 0.03 WC gościnne | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 0.04 Klatka schodowa | h pod belką B8 | 2,50 | ≥ 2,20 (lokalnie) | OK | WT §72 (lokalne obniżenie) |
| Wysokości | 0.05 Spiżarnia | strefy h pod schodami | ≥2,20: 1,03 m²; 1,40–2,20: 0,00 m²; <1,40: 0,00 m²; h_min 2,22 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | OK | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] |
| Wysokości | 0.15 Schowek pod schodami (h 1,40–2,20) | strefy h pod schodami | ≥2,20: 0,00 m²; 1,40–2,20: 1,49 m²; <1,40: 0,00 m²; h_min 1,40 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | UWAGA | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] |
| Wysokości | 0.16 Schowek pod spocznikiem (h < 1,40) | strefy h pod schodami | ≥2,20: 0,00 m²; 1,40–2,20: 0,00 m²; <1,40: 2,93 m²; h_min 1,39 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | UWAGA | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] |
| Wysokości | 0.06 Salon + jadalnia + kuchnia | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 0.09 Łazienka gościnna (natrysk) | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 0.10 Pokój gościnny / gabinet | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 0.12 Pomieszczenie techniczne | h w świetle | 2,75 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 0.13 Garaż 2-stanowiskowy | h w świetle | 2,70 | ≥ 2,20 | OK | WT §102 pkt 1 [W-110] |
| Wysokości | 1.02 Pokój rodzinny / biblioteka (boks C) | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.03 Pokój dziecka 1 | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.04 Pokój dziecka 2 | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.05 Łazienka dzieci (wanna) | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 1.06 Klatka schodowa | h pod belką B9 | 2,50 | ≥ 2,20 (lokalnie) | OK | WT §72 (lokalne obniżenie) |
| Wysokości | 1.07 WC z natryskiem | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 1.08 Pralnia z suszarnią | h w świetle | 2,77 | ≥ 2,20 | OK | brief §5 |
| Wysokości | 2.02 Sypialnia rodziców | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 2.03 Garderoba (przedpokój apartamentu) | h w świetle | 2,77 | ≥ 2,20 | OK | brief §5 |
| Wysokości | 2.04 Łazienka rodziców | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 2.05 Gabinet / pokój gościnny okazjonalny | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 2.06 Klatka schodowa (wyjście z biegu 2, pustka) | h pod belką B10 | 2,50 | ≥ 2,20 (lokalnie) | OK | WT §72 (lokalne obniżenie) |
| Wysokości | 2.07 Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 0.14 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 1.09 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 2.08 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Powierzchnie | 0.06 Salon + jadalnia + kuchnia | pow. netto | 54,44 m² | ≥ 50,0 m² | OK | brief §4 / założenie (salon+jadalnia+kuchnia ≥ 50 m²; pokój dzienny ≥ 16 m²) |
| Powierzchnie | 0.10 Pokój gościnny / gabinet | pow. netto | 12,52 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | 1.02 Pokój rodzinny / biblioteka (boks C) | pow. netto | 28,36 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | 1.03 Pokój dziecka 1 | pow. netto | 13,19 m² | ≥ 12,0 m² | OK | brief §4 [W-068] |
| Powierzchnie | 1.04 Pokój dziecka 2 | pow. netto | 12,52 m² | ≥ 12,0 m² | OK | brief §4 [W-068] |
| Powierzchnie | 2.02 Sypialnia rodziców | pow. netto | 21,43 m² | ≥ 14,0 m² | OK | brief §4 / założenie (sypialnia rodziców ≥ 14 m²) |
| Powierzchnie | 2.05 Gabinet / pokój gościnny okazjonalny | pow. netto | 16,25 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | budynek | PU mieszkalna (podst.+pomocn.+komunikacja, bez klatek, garażu, techn.) | 239,16 m² | 230–270 m² | OK | brief §4 [W-068]; RPB §20 / PN-ISO 9836 [W-316] |
| Powierzchnie | 0.06 | strefa dzienna otwarta (salon+jadalnia+kuchnia) | 54,44 m² | ≥ 50,0 m² | OK | brief §4 (TWARDE ZAŁOŻENIA) |
| Oświetlenie | 0.06 Salon + jadalnia + kuchnia | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,592 (mur: 0,677; O0-01, O0-02, O0-03, O0-04, O0-05, O0-11) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 0.10 Pokój gościnny / gabinet | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,176 (mur: 0,216; O0-12) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.02 Pokój rodzinny / biblioteka (boks C) | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,363 (mur: 0,440; O1-01, O1-13, O1-14, O1-02) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.03 Pokój dziecka 1 | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,167 (mur: 0,205; O1-06) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.04 Pokój dziecka 2 | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,176 (mur: 0,216; O1-05) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 2.02 Sypialnia rodziców | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,436 (mur: 0,504; O2-01, O2-04) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 2.05 Gabinet / pokój gościnny okazjonalny | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,355 (mur: 0,425; O2-03, O2-05) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Schody | SCH1 | wysokość stopnia h | 0,175 | ≤ 0,190 (projekt ≈ 0,175) | OK | WT §68 ust. 1 [W-090] |
| Schody | SCH1 | 2h+s | 0,630 | 0,60–0,65 | OK | WT §69 ust. 4 [W-091] |
| Schody | SCH1 | Σ podnóżków × h = Δ kondygnacji | 18 × 0,175 = 3,150 vs 3,150 | równe | OK | geometria |
| Schody | SCH2 | wysokość stopnia h | 0,175 | ≤ 0,190 (projekt ≈ 0,175) | OK | WT §68 ust. 1 [W-090] |
| Schody | SCH2 | 2h+s | 0,630 | 0,60–0,65 | OK | WT §69 ust. 4 [W-091] |
| Schody | SCH2 | Σ podnóżków × h = Δ kondygnacji | 18 × 0,175 = 3,150 vs 3,150 | równe | OK | geometria |
| Schody | SCH1/bieg1 | szerokość biegu w świetle ścian | 1,135 (model: 1,135) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH1/bieg1 | prześwit nad biegiem (min.) | 2,325 (element: B8) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH1/bieg2 | szerokość biegu w świetle ścian | 1,130 (model: 1,130) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH1/bieg2 | prześwit nad biegiem (min.) | 2,763 (element: SCH2/bieg2) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH2/bieg1 | szerokość biegu w świetle ścian | 1,135 (model: 1,135) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH2/bieg1 | prześwit nad biegiem (min.) | 2,325 (element: B9) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH2/bieg2 | szerokość biegu w świetle ścian | 1,130 (model: 1,130) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH2/bieg2 | prześwit nad biegiem (min.) | 2,805 (element: D1) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH1/spocznik1 | głębokość spocznika | 1,175 | ≥ szer. biegu 1,135 | OK | WT §68 ust. 1 [W-090]; brief §5 |
| Schody | SCH1/spocznik1 | prześwit nad spocznikiem (min.) | 2,970 (SCH2/spocznik1) | ≥ 2,00 | OK | R3 K-22 |
| Schody | SCH2/spocznik1 | głębokość spocznika | 1,175 | ≥ szer. biegu 1,135 | OK | WT §68 ust. 1 [W-090]; brief §5 |
| Schody | SCH2/spocznik1 | prześwit nad spocznikiem (min.) | 4,355 (D1) | ≥ 2,00 | OK | R3 K-22 |
| Schody | BL1 | wysokość balustrady/pochwytu | 0,90 | ≥ 0,90 | OK | WT §298 ust. 1–2 (budynki jednorodzinne; prześwit nieregulowany) [W-095] |
| Schody | BL2 | wysokość balustrady/pochwytu | 0,90 | ≥ 0,90 | OK | WT §298 ust. 1–2 (budynki jednorodzinne; prześwit nieregulowany) [W-095] |
| Odległości | S0-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-02 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-03 | lico zewn. → granica E | 5,73 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-05 | lico zewn. → granica W | 19,30 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S0-07 | lico zewn. → granica W | 7,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-02 | lico zewn. → granica E | 12,10 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-04 | lico zewn. → granica W | 7,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-02 | lico zewn. → granica E | 12,10 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-04 | lico zewn. → granica E | 15,60 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S2-06 | lico zewn. → granica W | 11,18 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S2-08 | lico zewn. → granica W | 6,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | PL-E | płyta wysunięta/okap/daszek → granica E | 10,60 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-E | płyta wysunięta/okap/daszek → granica W | 5,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C1 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C1 | płyta wysunięta/okap/daszek → granica W | 11,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C2 | płyta wysunięta/okap/daszek → granica E | 10,95 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C2 | płyta wysunięta/okap/daszek → granica W | 11,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-2 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-2 | płyta wysunięta/okap/daszek → granica W | 5,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-3 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-3 | płyta wysunięta/okap/daszek → granica W | 5,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | IZ-ST2Z | płyta wysunięta/okap/daszek → granica W | 6,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PS-A | płyta wysunięta/okap/daszek → granica W | 5,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | OB-A | płyta wysunięta/okap/daszek → granica W | 5,18 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | OB-A2 | płyta wysunięta/okap/daszek → granica W | 7,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-D | płyta wysunięta/okap/daszek → granica E | 5,73 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D1 | dach z attyką → granica W | 6,50 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D2 | dach z attyką → granica W | 7,51 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4 | dach z attyką → granica E | 5,94 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | T1 | taras naziemny/podest → granica W | 4,30 m | ≥ 1,50 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | T3 | taras naziemny/podest → granica E | 10,90 m | ≥ 1,50 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-S | lamele (osłona elewacji) → granica E | 11,95 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-S | lamele (osłona elewacji) → granica W | 6,15 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-W | lamele (osłona elewacji) → granica W | 6,07 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-E | lamele (osłona elewacji) → granica E | 11,87 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL1 | słup → granica W | 9,74 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL2 | słup → granica W | 11,64 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL7 | słup → granica W | 11,55 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL9 | słup → granica W | 7,51 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL10 | słup → granica W | 7,51 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL11 | słup → granica W | 7,51 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL12 | słup → granica W | 7,51 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL13 | słup → granica W | 11,10 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL14 | słup → granica W | 11,10 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL15 | słup → granica W | 11,10 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL21 | słup → granica W | 11,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D1/przelew@[3.785, 5.7] | przelew awaryjny (rzygacz ~0,15 m) → granica W | 11,24 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | RS3 | rura spustowa zewn. → granica W | 7,94 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D2/przelew@[-0.09, 8.2] | przelew awaryjny (rzygacz ~0,15 m) → granica W | 7,36 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | RS5 | rura spustowa zewn. → granica E | 5,61 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4/przelew@[18.465, 8.6] | przelew awaryjny (rzygacz ~0,15 m) → granica E | 5,79 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4/przelew@[18.465, 0.9] | przelew awaryjny (rzygacz ~0,15 m) → granica E | 5,79 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| MPZP | linia zabudowy | najdalej wysunięty element (+ = przekroczenie) | -0,95 m (T2) | ≤ 0,00 | OK | MPZP 3MN (fikcyjny) — nieprzekraczalna linia zabudowy od 1KDD; żaden element jej nie przekracza [W-006] |
| MPZP | pow. zabudowy (1) obrys ścian zewn. wszystkich kondygnacji (lamela.wskazniki) | A_z | 187,50 m² (11,7 %) | ≤ 480,00 m² | OK | MPZP 3MN × 1600,00 m² [W-030] |
| MPZP | pow. zabudowy (2) kontrolnie z płytami wysuniętymi (lamela.wskazniki) | A_z+ | 218,08 m² (13,6 %); metoda audytu: 217,86 m² | ≤ 480,00 m² | OK | rejestr D-06 |
| MPZP | intensywność zabudowy | Σ pow. kondygnacji nadziemnych / pow. działki | 396,39 / 1600,00 = 0,248 | 0,05–0,80 | OK | MPZP 3MN; upzp art. 2 pkt 31–33 (nadziemna) [W-032] |
| MPZP | pow. biologicznie czynna (teren) | PBC | 1270,23 m² (79,4 %) | ≥ 800,00 m² | OK | MPZP 3MN × 1600,00 m² [W-031]; opaska żwirowa wyłączona z PBC (ostrożnie); teren nad zbiornikiem ≈ 3,1 m² wyłączony (W-031); wartość z lamela.wskazniki; metoda audytu kontrolnie 1268,59 m² |
| MPZP | miejsca postojowe | liczba (garaż + zewn.) | 4 (2 w garażu) | ≥ 2 | OK | MPZP 3MN; WT §18 ust. 2 [W-036] |
| MPZP | kondygnacje nadziemne | liczba | 3 | ≤ 3 | OK | MPZP 3MN; warunek WT §213 pkt 1 lit. a [W-034] |
| MPZP | D1 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D2 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D3 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D4 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | ogrodzenie [0.0, 50.0]→[17.6, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| MPZP | ogrodzenie [18.6, 50.0]→[20.3, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| MPZP | ogrodzenie [25.9, 50.0]→[32.0, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| Zagospodarowanie | przesuwna @ [23.1, 50.0] | szerokość w świetle | 5,60 | ≥ 2,40 | OK | WT §43 [W-017] |
| Zagospodarowanie | furtka @ [18.1, 50.0] | szerokość w świetle | 1,00 | ≥ 0,90 | OK | WT §43 [W-017] |
| MPZP | wysokość zabudowy (upzp art. 2 pkt 30 lit. a — lamela.wskazniki) | od średniej t_śr = (101,29 + 101,48)/2 = 101,38 do wyrzutnia wentylacji (dachowa, szczyt urządzenia) (+10,200) | 10,47 m (informacyjnie od t_min 101,29: 10,56 m) | ≤ 11,00 (z rezerwą ≤ 10,70) | OK | MPZP 3MN; upzp art. 2 pkt 30 [W-033]; upzp (t.j. Dz.U. 2026 poz. 538) art. 2 pkt 30 lit. a; rejestr D-15 |
| WT | wysokość budynku wg WT §6 (lamela.wskazniki) | teren przy wejściu O0-03: 101,30 → wierzch D1 z izol. (+9,626) | 9,97 m | ≤ 12,00 (N); ≤ 11,00 (MPZP) | OK | WT §8 pkt 1 (lub ≤ 4 kondygnacje mieszkalne) [W-063]; [W-063] |
| Garaż | 0.13 | wymiary w świetle | 6,05 × 6,17 m | ≥ 5,60 × 6,00 | OK | WT §104 + §21 ust. 1 (0,3 + 2×2,5 + 0,3) [W-112]; brief §4 |
| Garaż | O0-07 | brama w świetle | 5,00 × 2,25 | ≥ 2,30 × 2,00 | OK | WT §102 pkt 2 [W-111] |
| Garaż | MP1 | stanowisko | 2,50 × 5,90 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Garaż | MP1 | dłuższa krawędź stanowiska → lico ściany | 0,30 m | ≥ 0,30 | OK | WT §104 ust. 1 pkt 1 [W-112] |
| Garaż | MP2 | stanowisko | 2,50 × 5,90 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Garaż | MP2 | dłuższa krawędź stanowiska → lico ściany | 0,60 m | ≥ 0,30 | OK | WT §104 ust. 1 pkt 1 [W-112] |
| Zagospodarowanie | MP3 | stanowisko | 2,50 × 5,00 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Zagospodarowanie | MP3 | odl. od granic bocznych/tylnej | 9,00 m | ≥ 3,00 (granica z drogą — bez wymogu) | OK | WT §19 ust. 2 pkt 1 lit. a (nie dotyczy granicy z działką drogową, ust. 7) [W-015] |
| Zagospodarowanie | MP4 | stanowisko | 2,50 × 5,00 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Zagospodarowanie | MP4 | odl. od granic bocznych/tylnej | 6,30 m | ≥ 3,00 (granica z drogą — bez wymogu) | OK | WT §19 ust. 2 pkt 1 lit. a (nie dotyczy granicy z działką drogową, ust. 7) [W-015] |
| Garaż | O0-22 (drzwi garaż–dom) | różnica posadzek dom − garaż przy drzwiach | 0,051 m (posadzka przy bramie -0,10, spadek 0,8 % na 6,10 m) | ≥ 0,030 (próg) | OK | WT §107 ust. 2 [W-114] |
| Garaż | O0-07 | wrota → okna: pion / poziom (pobyt ludzi) | brak okien nad wrotami / 9,43 m | ≥ 1,50 / ≥ 1,50 | OK | WT §279 ust. 1 (wszystkie okna) [W-117] |
| WT | O0-09 | drzwi wejściowe (światło ościeżnicy, szac.) | 0,96 × 2,33 | ≥ 0,90 × 2,00 | OK | WT §62 ust. 1 (w świetle ościeżnicy) [W-055] |
| WT | PL-DA | daszek nad wejściem: wysięg / szerokość | 1,30 / 2,30 m | ≥ 1,00 / ≥ 2,10 | OK | WT §292 ust. 1 (budynek > 2 kondygnacji, grupa N) [W-057] |
| WT | O1-01 | podokiennik | 0,70 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O1-13 | podokiennik | 0,70 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O1-14 | podokiennik | 0,70 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-01 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-01 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-02 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-03 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-03 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-04 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-04 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-05 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-06 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-07 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | WYL1 | wyłaz dachowy w świetle | 0,90 × 0,90 | ≥ 0,80 × 0,80 | OK | WT §308 ust. 3 [W-065] |
| Wentylacja | czerpnia dachowa (D3) | wysokość nad pokryciem (lokalnie, klin) | 0,504 m (pokrycie ≈ +6,396) | ≥ 0,40 | OK | WT §152 ust. 4 [W-166] |
| Wentylacja | wyrzutnia dachowa (D1, wylot pionowy) | wysokość nad pokryciem (lokalnie, klin) | 0,495 m | ≥ 0,40 | OK | WT §152 ust. 7 (także nad punktami w promieniu 10 m) [W-167] |
| Wentylacja | wyrzutnia (wylot pionowy) ↔ najwyższe punkty w promieniu 10 m | ust. 7 — tylko wylot poziomy | nie dotyczy (wylot pionowy; informacyjnie 0,060 m nad wywiewka) | — | INFO | WT §152 ust. 7; W-167 |
| Wentylacja | czerpnia ↔ wywiewka kanalizacyjna | odległość | 6,16 m | ≥ 6,00 | OK | WT §152 ust. 4 [W-166] |
| Wentylacja | czerpnia ↔ wywiewka kanalizacyjna | odległość | 9,20 m | ≥ 6,00 | OK | WT §152 ust. 4 [W-166] |
| Wentylacja | czerpnia ↔ wyrzutnia (dach) | odległość / wyrzutnia wyżej o | 10,37 m / 3,10 m | ≥ 6,00 m (wyrzut pionowy) i wyrzutnia ≥ 1,00 m ponad czerpnią (lub zestaw zblokowany — ust. 11) | OK | WT §152 ust. 10 [W-167]; R6-43 |
| Wentylacja | wyrzutnia ↔ okno w dachu SW1 | odległość / wylot ponad oknem | 5,29 m / 0,25 m | 3–10 m ⇒ wylot ≥ 1,00 m nad górną krawędzią okna (≥ +10,75) | UWAGA | WT §152 ust. 12 [W-167]; R6-43 |
| Wentylacja | wyrzutnia ↔ krawędź dachu nad oknami | odległość | 3,00 m | ≥ 3,00 | OK | WT §152 ust. 12 [W-167] |
| Zagospodarowanie | PC-JZ (jedn. zewn. PC) | odl. od granic | S 31,65, E 7,60, N 18,35, W 24,40 | ≥ 3,0 (założenie); E ≥ 6,0 | OK | R8 3.4 [W-024] |
| Zagospodarowanie | PC-JZ (jedn. zewn. PC) | elewacja, przy której stoi jednostka | S (x 24,40, y 31,65 w ukł. działki; 0,75 m od lica) | N lub E (TWARDE ZAŁOŻENIA) | UWAGA | TWARDE ZAŁOŻENIA (energia i światło); W-024 (hałas) |
| Zagospodarowanie | PC-JZ strefa R290 | otwory/wpusty/studzienki w strefie 1,0 m | brak | brak | OK | dane producentów (DTR); PN-EN 378-1+A1:2021-03 [W-156] |
| Zagospodarowanie | retencja/zbiornik | odl. od granic / od budynku | min 10,60 / 5,70 m | ≥ 2,0 / ≥ 3,0 | OK | R8 3.5 [W-144] [W-144, W-145] |
| Zagospodarowanie | retencja/rozsaczanie | odl. od granic / od budynku | min 8,10 / 12,70 m | ≥ 2,0 / ≥ 3,0 | OK | R8 3.5 [W-144] [W-144, W-145] |
| Zagospodarowanie | miejsce na pojemniki | odl. od granic | S 48,60, E 14,80, N 0,10, W 14,00 | zabudowa jednorodzinna — odległości nieustalone (WT §23 ust. 4) | INFO | WT §22, §23 ust. 4 [W-016] |
| Sąsiedztwo | dz. 123/3 | odl. budynek–budynek sąsiedni | 14,31 m | ≥ 8,00 (ppoż.); ≥ H = 10,47 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 123/5 | odl. budynek–budynek sąsiedni | 13,72 m | ≥ 8,00 (ppoż.); ≥ H = 10,47 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 118/2 | odl. budynek–budynek sąsiedni | 28,13 m | ≥ 8,00 (ppoż.); ≥ H = 10,47 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 118/3 | odl. budynek–budynek sąsiedni | 29,86 m | ≥ 8,00 (ppoż.); ≥ H = 10,47 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| WT | kubatura brutto (lamela, PN-ISO 9836) | V | 1354,4 m³ | > 1000 m³ ⇒ PWP (W-190); uprawnienia bez ogr. | INFO | WT §3 pkt 24; PB art. 15a [W-069] |
