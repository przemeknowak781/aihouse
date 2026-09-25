# Obliczenia instalacji wodociągowej i c.w.u.

Obiekt: Dom LAMELA. Model: budynek: `model/budynek.yaml`, dzialka: `model/dzialka.yaml`, wyposazenie: `model/wyposazenie.yaml`, instalacje: `model/instalacje.yaml`. Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE] tam, gdzie oznaczono [ZAŁ].

## 1. Podstawy i metoda

* WT §113–120 (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowane na podstawie art. 102a PB; wymagania W-130…W-137.
* PN-B-01706:1992 (+Az1:1999) — powołana w WT zał. 1 lp. 4 (wycofana w PKN, wiąże przez WT); kontrolnie PN-EN 806-3:2006.
* **Wybór metody przepływu obliczeniowego:** q = 0,682·(Σq_n)^0,45 − 0,14 (PN-B-01706, budynki mieszkalne) — metoda wskazana w rejestrze (W-132) i powołana przez WT; daje wartości wyższe (bezpieczniejsze) niż PN-EN 806-3 (Nowakowski, RI 4/2011); przejście LU → Q_D w PN-EN 806-3 jest graficzne — raport podaje ΣLU i Q_T = 0,1·ΣLU kontrolnie oraz warunki ciśnień PN-EN 806-3 p. 4.3.
* PN-EN 1717:2003 (WT zał. 1 lp. 5) / PN-EN 1717+A1:2026-09 (aktualna, EN) — zabezpieczenia przed przepływem zwrotnym.
* Straty liniowe: Darcy–Weisbach + Colebrook–White; straty miejscowe 50 % liniowych (PWr) [W].

## 2. Dane wejściowe i założenia

* Przyłącze: uzbrojenie projektowane (dzialka.yaml); L = 25,98 m; oś sieci 1,40 m p.p.t. [ZAŁ].
* Wodomierz: lokalizacja z instalacje.yaml.
* Rury instalacji: PE-RT/Al/PE-RT (k = 0,007 mm); przyłącze PE100 SDR11 [ZAŁ].
* Prędkości maks. [m/s]: przylacze 1,0, glowny 1,0, pion 1,5, rozdzielczy 1,5, podejscie 2,0 (PN-EN 806-3: ≤ 2 m/s; przewody główne 1,0 m/s dla ograniczenia strat i hałasu) [ZAŁ].
* Długości odcinków: trasy równoległe do ścian (odległość „miejska” w rzucie) + podejścia pionowe; piony zgrupowane automatycznie (R ≤ 3,5 m) lub z instalacje.yaml [UPR].
* Ciśnienie w sieci: dyspozycyjne 0,35 MPa, maks. statyczne 0,60 MPa [ZAŁ — do potwierdzenia w warunkach technicznych gestora, D-23].

### 2.1 Przybory (z modelu)

| Przybór | Liczba | q_n zw [dm³/s] | q_n cw [dm³/s] | Σq_n [dm³/s] | LU (zw+cw) | DU [l/s] | Odpływ |
|:---|---:|---:|---:|---:|---:|---:|:---|
| Pralka automatyczna (≤ 12 kg) | 1 | 0,25 | 0,00 | 0,25 | 2 | 1,50 | DN50 |
| Natrysk (odpływ liniowy/brodzik bez korka) z baterią | 3 | 0,15 | 0,15 | 0,90 | 4 | 0,60 | DN50 |
| Suszarka kondensacyjna z odprowadzeniem skroplin | 1 | 0,00 | 0,00 | 0,00 | 0 | 0,00 | DN40 |
| Umywalka z baterią | 3 | 0,07 | 0,07 | 0,42 | 2 | 0,50 | DN40 |
| Umywalka nablatowa z baterią | 2 | 0,07 | 0,07 | 0,28 | 2 | 0,50 | DN40 |
| Wanna z baterią | 1 | 0,15 | 0,15 | 0,30 | 8 | 0,80 | DN50 |
| Miska ustępowa z płuczką zbiornikową 6 l | 5 | 0,13 | 0,00 | 0,65 | 1 | 2,00 | DN100 |
| Wpust podłogowy DN50 | 1 | 0,00 | 0,00 | 0,00 | 0 | 0,80 | DN50 |
| Zawór czerpalny ogrodowy DN15 ze złączką do węża | 2 | 0,30 | 0,00 | 0,60 | 5 | 0,00 | — |
| Zlewozmywak z baterią | 3 | 0,07 | 0,07 | 0,42 | 4 | 0,80 | DN50 |
| Zmywarka do naczyń | 1 | 0,15 | 0,00 | 0,15 | 2 | 0,80 | DN50 |

| Id | Typ | Kond. | Pomieszczenie | x, y [m] | Źródło |
|:---|:---|:---|:---|:---|:---|
| WC01 | wc | P0 | 0.03 WC gościnne | 9,20; 8,64 | wyposazenie |
| UMY02 | umywalka | P0 | 0.03 WC gościnne | 8,61; 7,60 | wyposazenie |
| PRY03 | prysznic | P0 | 0.09 Łazienka gościnna (natrysk) | 4,58; 8,64 | wyposazenie |
| WC04 | wc | P0 | 0.09 Łazienka gościnna (natrysk) | 5,77; 7,20 | wyposazenie |
| UMY05 | umywalka | P0 | 0.09 Łazienka gościnna (natrysk) | 5,77; 8,20 | wyposazenie |
| ZLE06 | zlew | P0 | 0.06 Salon + jadalnia + kuchnia | 11,89; 2,60 | wyposazenie |
| ZMY07 | zmywarka | P0 | 0.06 Salon + jadalnia + kuchnia | 11,89; 1,90 | wyposazenie |
| ZLE08 | zlew | P0 | 0.12 Pomieszczenie techniczne | 18,27; 2,20 | wyposazenie |
| WAN09 | wanna | P1 | 1.05 Łazienka dzieci (wanna) | 4,88; 8,64 | wyposazenie |
| WC10 | wc | P1 | 1.05 Łazienka dzieci (wanna) | 5,35; 6,45 | wyposazenie |
| UMY11 | umywalka_blat | P1 | 1.05 Łazienka dzieci (wanna) | 3,98; 7,20 | wyposazenie |
| PRY12 | prysznic | P1 | 1.07 WC z natryskiem | 9,20; 8,64 | wyposazenie |
| WC13 | wc | P1 | 1.07 WC z natryskiem | 9,80; 7,20 | wyposazenie |
| UMY14 | umywalka | P1 | 1.07 WC z natryskiem | 8,61; 6,40 | wyposazenie |
| PRA15 | pralka | P1 | 1.08 Pralnia z suszarnią | 9,95; 8,20 | wyposazenie |
| SUS16 | suszarka | P1 | 1.08 Pralnia z suszarnią | 9,95; 7,55 | wyposazenie |
| ZLE17 | zlew | P1 | 1.08 Pralnia z suszarnią | 11,89; 8,20 | wyposazenie |
| PRY18 | prysznic | P2 | 2.04 Łazienka rodziców | 4,88; 8,64 | wyposazenie |
| WC19 | wc | P2 | 2.04 Łazienka rodziców | 5,35; 6,45 | wyposazenie |
| UMY20 | umywalka_blat | P2 | 2.04 Łazienka rodziców | 3,98; 6,95 | wyposazenie |
| ZAW21 | zawor_ogrodowy | P0 | — na zewnątrz / poza pomieszczeniem | 1,00; −0,30 | instalacje |
| ZAW22 | zawor_ogrodowy | P0 | — na zewnątrz / poza pomieszczeniem | 18,68; 7,50 | instalacje |
| WPU23 | wpust_podlogowy | P0 | 0.12 Pomieszczenie techniczne | 16,00; 1,60 | instalacje |

### 2.2 Piony

| Pion | Położenie x, y [m] | Kondygnacje | Pomieszczenia | Przybory | Źródło |
|:---|:---|:---|:---|:---|:---|
| K1 | 5,57; 6,20 | P0, P1, P2 | P0: 0.09; P1: 1.05; P2: 2.04 | PRY03, WC04, UMY05, WAN09, WC10, UMY11, PRY18, WC19, UMY20 | instalacje.yaml |
| K2 | 9,70; 8,52 | P0, P1 | P0: 0.03; P1: 1.07, 1.08 | WC01, UMY02, PRY12, WC13, UMY14, PRA15, SUS16, ZLE17 | instalacje.yaml |
| K3 | 18,15; 1,75 | P0 | P0: 0.06, 0.12 | ZLE06, ZMY07, ZLE08, WPU23 | instalacje.yaml |

## 3. Zapotrzebowanie na wodę

* Średnie dobowe zapotrzebowanie (bytowe): Q_d,śr = N·q_j = 5·120/1000 = **0,600** m³/d — _q_j = 120 dm³/(os·d) [ZAŁ — dom jednorodzinny z pełnym wyposażeniem]_
* Podlewanie zieleni (sezon V–IX): Q_pod = A·q_p = 100·3,0/1000 = **0,300** m³/d — _[ZAŁ]_
* Maksymalne dobowe: Q_d,max = N_d·Q_d,śr + Q_pod = 1,5·0,600 + 0,300 = **1,200** m³/d — _N_d = 1,5 [ZAŁ]_
* Maksymalne godzinowe: Q_h,max = N_h·Q_d,max/24 = 3,0·1,200/24 = **0,150** m³/h — _N_h = 3,0 [ZAŁ]_

## 4. Przepływ obliczeniowy

* Suma wypływów normatywnych (woda zimna + ciepła) na zestawie wodomierzowym: Σq_n = **3,97** dm³/s — _PN-92/B-01706 tabl. 1_
* Przepływ obliczeniowy: q = 0,682·(Σq_n)^0,45 − 0,14 = 0,682·(3,97)^0,45 − 0,14 = **1,128** dm³/s — _PN-92/B-01706 (budynki mieszkalne); W-132_
* Przepływ obliczeniowy przyjęty (≥ max q_n, ≤ Σq_n): q = **1,128** dm³/s — _[UPR]_
* Kontrolnie PN-EN 806-3: suma jednostek obciążenia i Q_T: Q_T = 0,1·ΣLU = 0,1·61 = **6,10** l/s — _PN-EN 806-3 tabl. 2 (Q_D z nomogramu normy ≤ Q_T)_

## 5. Wymiarowanie przewodów i straty ciśnienia

### 5.1 Woda zimna (z przyłączem i zasilaniem zasobnika)

| Nr | Odcinek | Typ | L [m] | Σq_n [dm³/s] | q [dm³/s] | ΣLU | Rura d_z×s | d_w [mm] | v [m/s] | R [kPa/m] | ∆p_l [kPa] | ∆p_m [kPa] |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|
| 1 | SIEC→WEJ: przyłącze wodociągowe (PE100 SDR11) | przylacze | 25,98 | 3,97 | 1,128 | 61 | PE100 SDR11 50×4,6 | 41 | 0,86 | 0,226 | 5,87 | 2,93 |
| 2 | WEJ→WOD: wejście do budynku → zestaw wodomierzowy | glowny | 12,74 | 3,97 | 1,128 | 61 | PE-RT/Al/PE-RT 50×4,0 | 42 | 0,81 | 0,195 | 2,49 | 1,24 |
| 3 | WOD→T0: zestaw wodomierzowy (zawór, wodomierz, filtr, EA) | glowny | 1,00 | 3,97 | 1,128 | 61 | PE-RT/Al/PE-RT 50×4,0 | 42 | 0,81 | 0,195 | 0,20 | 0,10 |
| 4 | T0→ZAS: zasilanie zasobnika c.w.u. (grupa bezpieczeństwa) | glowny | 4,12 | 1,16 | 0,589 | 21 | PE-RT/Al/PE-RT 40×3,5 | 33 | 0,69 | 0,196 | 0,81 | 0,40 |
| 5 | T0→ZAW21: przewód do zawór czerpalny ogrodowy dn15 ze złączką do węża (ZAW21) | rozdzielczy | 20,07 | 0,30 | 0,300 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,49 | 1,906 | 38,26 | 19,13 |
| 6 | T0→ZAW22: przewód do zawór czerpalny ogrodowy dn15 ze złączką do węża (ZAW22) | rozdzielczy | 7,61 | 0,30 | 0,300 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,49 | 1,906 | 14,51 | 7,25 |
| 7 | T0→K1Z@P0: przewód rozdzielczy do pionu K1 | glowny | 18,40 | 1,05 | 0,557 | 14 | PE-RT/Al/PE-RT 40×3,5 | 33 | 0,65 | 0,178 | 3,27 | 1,63 |
| 8 | K1Z@P0→RZ_0.09: odgałęzienie do pom. 0.09 Łazienka gościnna (natrysk) | rozdzielczy | 2,51 | 0,35 | 0,285 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,42 | 1,743 | 4,37 | 2,19 |
| 9 | RZ_0.09→PRY03Z: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY03) | podejscie | 2,32 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 5,16 | 2,58 |
| 10 | RZ_0.09→WC04Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC04) | podejscie | 1,71 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 2,96 | 1,48 |
| 11 | RZ_0.09→UMY05Z: podejście: umywalka z baterią (UMY05) | podejscie | 1,38 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,81 | 0,41 |
| 12 | K1Z@P0→K1Z@P1: pion K1 P0→P1 | pion | 3,15 | 0,70 | 0,441 | 10 | PE-RT/Al/PE-RT 25×2,5 | 20 | 1,40 | 1,292 | 4,07 | 2,04 |
| 13 | K1Z@P1→RZ_1.05: odgałęzienie do pom. 1.05 Łazienka dzieci (wanna) | rozdzielczy | 2,57 | 0,35 | 0,285 | 6 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,42 | 1,743 | 4,48 | 2,24 |
| 14 | RZ_1.05→WAN09Z: podejście: wanna z baterią (WAN09) | podejscie | 1,80 | 0,15 | 0,150 | 4 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 4,00 | 2,00 |
| 15 | RZ_1.05→WC10Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC10) | podejscie | 2,10 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 3,63 | 1,82 |
| 16 | RZ_1.05→UMY11Z: podejście: umywalka nablatowa z baterią (UMY11) | podejscie | 1,89 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 1,11 | 0,56 |
| 17 | K1Z@P1→K1Z@P2: pion K1 P1→P2 | pion | 3,15 | 0,35 | 0,285 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,42 | 1,743 | 5,49 | 2,74 |
| 18 | K1Z@P2→RZ_2.04: odgałęzienie do pom. 2.04 Łazienka rodziców | rozdzielczy | 2,48 | 0,35 | 0,285 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,42 | 1,743 | 4,32 | 2,16 |
| 19 | RZ_2.04→PRY18Z: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY18) | podejscie | 2,34 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 5,20 | 2,60 |
| 20 | RZ_2.04→WC19Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC19) | podejscie | 2,01 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 3,47 | 1,74 |
| 21 | RZ_2.04→UMY20Z: podejście: umywalka nablatowa z baterią (UMY20) | podejscie | 2,05 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 1,20 | 0,60 |
| 22 | T0→K2Z@P0: przewód rozdzielczy do pionu K2 | glowny | 16,59 | 0,87 | 0,501 | 10 | PE-RT/Al/PE-RT 32×3,0 | 26 | 0,94 | 0,460 | 7,63 | 3,81 |
| 23 | K2Z@P0→RZ_0.03: odgałęzienie do pom. 0.03 WC gościnne | rozdzielczy | 1,70 | 0,20 | 0,191 | 2 | PE-RT/Al/PE-RT 20×2,0 | 16 | 0,95 | 0,855 | 1,45 | 0,73 |
| 24 | RZ_0.03→WC01Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC01) | podejscie | 1,32 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 2,28 | 1,14 |
| 25 | RZ_0.03→UMY02Z: podejście: umywalka z baterią (UMY02) | podejscie | 1,62 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,95 | 0,48 |
| 26 | K2Z@P0→K2Z@P1: pion K2 P0→P1 | pion | 3,15 | 0,67 | 0,430 | 8 | PE-RT/Al/PE-RT 25×2,5 | 20 | 1,37 | 1,234 | 3,89 | 1,94 |
| 27 | K2Z@P1→RZ_1.07: odgałęzienie do pom. 1.07 WC z natryskiem | rozdzielczy | 2,10 | 0,35 | 0,285 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,42 | 1,743 | 3,66 | 1,83 |
| 28 | RZ_1.07→PRY12Z: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY12) | podejscie | 2,13 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 4,74 | 2,37 |
| 29 | RZ_1.07→WC13Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC13) | podejscie | 1,31 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 2,26 | 1,13 |
| 30 | RZ_1.07→UMY14Z: podejście: umywalka z baterią (UMY14) | podejscie | 2,41 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 1,42 | 0,71 |
| 31 | K2Z@P1→RZ_1.08: odgałęzienie do pom. 1.08 Pralnia z suszarnią | rozdzielczy | 2,04 | 0,32 | 0,268 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,33 | 1,565 | 3,19 | 1,60 |
| 32 | RZ_1.08→PRA15Z: podejście: pralka automatyczna (≤ 12 kg) (PRA15) | podejscie | 1,47 | 0,25 | 0,250 | 2 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,24 | 1,380 | 2,03 | 1,01 |
| 33 | RZ_1.08→ZLE17Z: podejście: zlewozmywak z baterią (ZLE17) | podejscie | 1,82 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 1,07 | 0,53 |
| 34 | T0→K3Z@P0: przewód rozdzielczy do pionu K3 | glowny | 1,37 | 0,29 | 0,251 | 6 | PE-RT/Al/PE-RT 25×2,5 | 20 | 0,80 | 0,477 | 0,65 | 0,33 |
| 35 | K3Z@P0→RZ_0.06: odgałęzienie do pom. 0.06 Salon + jadalnia + kuchnia | rozdzielczy | 7,25 | 0,22 | 0,205 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,973 | 7,05 | 3,53 |
| 36 | RZ_0.06→ZLE06Z: podejście: zlewozmywak z baterią (ZLE06) | podejscie | 1,20 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,70 | 0,35 |
| 37 | RZ_0.06→ZMY07Z: podejście: zmywarka do naczyń (ZMY07) | podejscie | 0,65 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 1,45 | 0,72 |
| 38 | K3Z@P0→RZ_0.12: odgałęzienie do pom. 0.12 Pomieszczenie techniczne | rozdzielczy | 1,07 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,63 | 0,31 |
| 39 | RZ_0.12→ZLE08Z: podejście: zlewozmywak z baterią (ZLE08) | podejscie | 0,85 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,50 | 0,25 |

### 5.2 Ciepła woda użytkowa (55 °C)

| Nr | Odcinek | Typ | L [m] | Σq_n [dm³/s] | q [dm³/s] | ΣLU | Rura d_z×s | d_w [mm] | v [m/s] | R [kPa/m] | ∆p_l [kPa] | ∆p_m [kPa] |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|
| 40 | ZAS→K1C@P0: przewód rozdzielczy do pionu K1 | glowny | 15,28 | 0,66 | 0,426 | 11 | PE-RT/Al/PE-RT 32×3,0 | 26 | 0,80 | 0,276 | 4,22 | 2,11 |
| 41 | K1C@P0→RC_0.09: odgałęzienie do pom. 0.09 Łazienka gościnna (natrysk) | rozdzielczy | 3,12 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,43 | 1,21 |
| 42 | RC_0.09→PRY03C: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY03) | podejscie | 1,72 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 1,790 | 3,08 | 1,54 |
| 43 | RC_0.09→UMY05C: podejście: umywalka z baterią (UMY05) | podejscie | 1,62 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,74 | 0,37 |
| 44 | K1C@P0→K1C@P1: pion K1 P0→P1 | pion | 3,15 | 0,44 | 0,331 | 8 | PE-RT/Al/PE-RT 25×2,5 | 20 | 1,05 | 0,627 | 1,97 | 0,99 |
| 45 | K1C@P1→RC_1.05: odgałęzienie do pom. 1.05 Łazienka dzieci (wanna) | rozdzielczy | 3,36 | 0,22 | 0,205 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,61 | 1,31 |
| 46 | RC_1.05→WAN09C: podejście: wanna z baterią (WAN09) | podejscie | 1,62 | 0,15 | 0,150 | 4 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 1,790 | 2,90 | 1,45 |
| 47 | RC_1.05→UMY11C: podejście: umywalka nablatowa z baterią (UMY11) | podejscie | 2,07 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,95 | 0,47 |
| 48 | K1C@P1→K1C@P2: pion K1 P1→P2 | pion | 3,15 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,45 | 1,23 |
| 49 | K1C@P2→RC_2.04: odgałęzienie do pom. 2.04 Łazienka rodziców | rozdzielczy | 3,24 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,52 | 1,26 |
| 50 | RC_2.04→PRY18C: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY18) | podejscie | 2,19 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 1,790 | 3,92 | 1,96 |
| 51 | RC_2.04→UMY20C: podejście: umywalka nablatowa z baterią (UMY20) | podejscie | 2,19 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,00 | 0,50 |
| 52 | ZAS→K2C@P0: przewód rozdzielczy do pionu K2 | glowny | 13,47 | 0,36 | 0,291 | 6 | PE-RT/Al/PE-RT 25×2,5 | 20 | 0,93 | 0,495 | 6,67 | 3,33 |
| 53 | K2C@P0→RC_0.03: odgałęzienie do pom. 0.03 WC gościnne | rozdzielczy | 2,51 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,15 | 0,57 |
| 54 | RC_0.03→UMY02C: podejście: umywalka z baterią (UMY02) | podejscie | 0,80 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,37 | 0,18 |
| 55 | K2C@P0→K2C@P1: pion K2 P0→P1 | pion | 3,15 | 0,29 | 0,251 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,25 | 1,119 | 3,53 | 1,76 |
| 56 | K2C@P1→RC_1.07: odgałęzienie do pom. 1.07 WC z natryskiem | rozdzielczy | 2,29 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 1,78 | 0,89 |
| 57 | RC_1.07→PRY12C: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY12) | podejscie | 2,32 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 1,790 | 4,15 | 2,08 |
| 58 | RC_1.07→UMY14C: podejście: umywalka z baterią (UMY14) | podejscie | 2,22 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,01 | 0,51 |
| 59 | K2C@P1→RC_1.08: odgałęzienie do pom. 1.08 Pralnia z suszarnią | rozdzielczy | 3,02 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,38 | 0,69 |
| 60 | RC_1.08→ZLE17C: podejście: zlewozmywak z baterią (ZLE17) | podejscie | 0,85 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,39 | 0,19 |
| 61 | ZAS→K3C@P0: przewód rozdzielczy do pionu K3 | glowny | 2,75 | 0,14 | 0,140 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 0,70 | 0,393 | 1,08 | 0,54 |
| 62 | K3C@P0→RC_0.06: odgałęzienie do pom. 0.06 Salon + jadalnia + kuchnia | rozdzielczy | 7,60 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 3,47 | 1,74 |
| 63 | RC_0.06→ZLE06C: podejście: zlewozmywak z baterią (ZLE06) | podejscie | 0,85 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,39 | 0,19 |
| 64 | K3C@P0→RC_0.12: odgałęzienie do pom. 0.12 Pomieszczenie techniczne | rozdzielczy | 1,07 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,49 | 0,24 |
| 65 | RC_0.12→ZLE08C: podejście: zlewozmywak z baterią (ZLE08) | podejscie | 0,85 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,39 | 0,19 |

### 5.3 Wymagane ciśnienie — najniekorzystniej położony punkt

* Najniekorzystniej położony punkt: natrysk (odpływ liniowy/brodzik bez korka) z baterią PRY18 (kond. P2, pom. 2.04), c.w.u.
* Wysokość geometryczna (oś sieci → wylewka): h_g = z_wyl − z_sieci = 7,50 − (−1,70) = **9,20** m
* Ciśnienie na pokonanie wysokości: p_g = ρ·g·h_g = 1000·9,81·9,20/1000 = **90,2** kPa
* Straty liniowe na drodze (odcinki 1, 2, 3, 4, 40, 44, 48, 49, 50): Σ∆p_l = 5,9 + 2,5 + 0,2 + 0,8 + 4,2 + 2,0 + 2,5 + 2,5 + 3,9 = **24,4** kPa — _Darcy–Weisbach, Colebrook–White_
* Straty miejscowe: Σ∆p_m = 0,5·Σ∆p_l = 0,5·24,4 = **12,2** kPa — _PWr [W]_
* Straty na urządzeniach (wodomierz, EA, filtr, podgrzewacz, TZM): Σ∆p_urz = **102,0** kPa
* Wymagane ciśnienie wypływu: p_w = **100** kPa — _PN-92/B-01706 tabl. 1; PN-EN 806-3 p. 4.3 (≥ 100 kPa)_
* Wymagane ciśnienie w miejscu włączenia do sieci: p_wym = p_g + Σ∆p_l + Σ∆p_m + Σ∆p_urz + p_w = 90,2 + 24,4 + 12,2 + 102,0 + 100 = **328,9** kPa — _W-130_

| Punkt | Medium | h_g [m] | Σ∆p_l [kPa] | Σ∆p_m [kPa] | Σ∆p_urz [kPa] | p_w [kPa] | p_wym [kPa] |
|:---|:---|---:|---:|---:|---:|---:|---:|
| PRY18 prysznic (P2) | c.w.u. | 9,20 | 24,4 | 12,2 | 102,0 | 100 | 328,9 |
| UMY20 umywalka_blat (P2) | c.w.u. | 9,20 | 21,5 | 10,8 | 102,0 | 100 | 324,5 |
| PRY18 prysznic (P2) | woda zimna | 9,20 | 30,9 | 15,5 | 72,0 | 100 | 308,6 |
| UMY20 umywalka_blat (P2) | woda zimna | 9,20 | 26,9 | 13,5 | 72,0 | 100 | 302,6 |
| PRY12 prysznic (P1) | c.w.u. | 6,05 | 25,5 | 12,7 | 102,0 | 100 | 299,6 |
| UMY14 umywalka (P1) | c.w.u. | 5,95 | 22,3 | 11,2 | 102,0 | 100 | 293,9 |
| ZLE17 zlew (P1) | c.w.u. | 6,00 | 21,3 | 10,7 | 102,0 | 100 | 292,8 |
| UMY11 umywalka_blat (P1) | c.w.u. | 6,05 | 19,1 | 9,6 | 102,0 | 100 | 290,0 |
| WAN09 wanna (P1) | c.w.u. | 5,60 | 21,1 | 10,5 | 102,0 | 100 | 288,5 |
| PRY12 prysznic (P1) | woda zimna | 6,05 | 28,5 | 14,2 | 72,0 | 100 | 274,0 |
| UMY14 umywalka (P1) | woda zimna | 5,95 | 25,1 | 12,6 | 72,0 | 100 | 268,1 |
| ZLE17 zlew (P1) | woda zimna | 6,00 | 24,3 | 12,2 | 72,0 | 100 | 267,3 |
| PRA15 pralka (P1) | woda zimna | 5,65 | 25,3 | 12,6 | 72,0 | 100 | 265,3 |
| ZAW21 zawor_ogrodowy (P0) | woda zimna | 2,30 | 46,8 | 23,4 | 72,0 | 100 | 264,8 |
| UMY11 umywalka_blat (P1) | woda zimna | 6,05 | 21,5 | 10,7 | 72,0 | 100 | 263,6 |
| WAN09 wanna (P1) | woda zimna | 5,60 | 24,4 | 12,2 | 72,0 | 100 | 263,5 |
| PRY03 prysznic (P0) | c.w.u. | 2,90 | 19,1 | 9,5 | 102,0 | 100 | 259,1 |
| UMY02 umywalka (P0) | c.w.u. | 2,80 | 17,5 | 8,8 | 102,0 | 100 | 255,8 |
| UMY05 umywalka (P0) | c.w.u. | 2,80 | 16,7 | 8,4 | 102,0 | 100 | 254,6 |
| WC19 wc (P2) | woda zimna | 8,80 | 29,2 | 14,6 | 72,0 | 50 | 252,1 |
| ZLE06 zlew (P0) | c.w.u. | 2,85 | 14,3 | 7,1 | 102,0 | 100 | 251,4 |
| ZLE08 zlew (P0) | c.w.u. | 2,85 | 11,3 | 5,7 | 102,0 | 100 | 246,9 |
| PRY03 prysznic (P0) | woda zimna | 2,90 | 21,3 | 10,7 | 72,0 | 100 | 232,5 |
| ZAW22 zawor_ogrodowy (P0) | woda zimna | 2,30 | 23,1 | 11,5 | 72,0 | 100 | 229,1 |
| UMY02 umywalka (P0) | woda zimna | 2,80 | 18,6 | 9,3 | 72,0 | 100 | 227,3 |
| ZLE06 zlew (P0) | woda zimna | 2,85 | 17,0 | 8,5 | 72,0 | 100 | 225,4 |
| UMY05 umywalka (P0) | woda zimna | 2,80 | 17,0 | 8,5 | 72,0 | 100 | 225,0 |
| ZMY07 zmywarka (P0) | woda zimna | 2,30 | 17,7 | 8,8 | 72,0 | 100 | 221,1 |
| WC13 wc (P1) | woda zimna | 5,65 | 26,0 | 13,0 | 72,0 | 50 | 216,4 |
| ZLE08 zlew (P0) | woda zimna | 2,85 | 10,3 | 5,2 | 72,0 | 100 | 215,4 |
| WC10 wc (P1) | woda zimna | 5,65 | 24,0 | 12,0 | 72,0 | 50 | 213,4 |
| WC01 wc (P0) | woda zimna | 2,50 | 19,9 | 10,0 | 72,0 | 50 | 176,4 |
| WC04 wc (P0) | woda zimna | 2,50 | 19,1 | 9,6 | 72,0 | 50 | 175,2 |

### 5.4 Ciśnienie statyczne

* Maks. ciśnienie statyczne w najniżej położonym punkcie: p_st = p_sieci,max − ρ·g·(z_min − z_sieci) = 600 − 9,81·(0,60 − (−1,70)) = **577** kPa
* Reduktor ciśnienia za wodomierzem (nastawa): p_red = **400** kPa — _PN-EN 806-3 p. 4.3: p_st ≤ 500 kPa w punktach_

## 6. Zestaw wodomierzowy i zabezpieczenia

* Przepływ obliczeniowy na wodomierzu: q_wod = 3,6·q = 3,6·1,128 = **4,06** m³/h
* Dobór wodomierza (pierwszy o Q3 ≥ q_wod): q_wod ≤ Q3 = 4,06 ≤ 6,3 = **DN25, Q3 = 6,3 m³/h** — _PN-EN ISO 4064 (MID); przykład PWr_
* Strata ciśnienia na wodomierzu: ∆p_wod = ∆p(Q3)·(q_wod/Q3)² = 63·(4,06/6,3)² = **26,2** kPa — _klasa ΔP63 [ZAŁ] — przyjąć z karty wyrobu_
* Strata na zaworze antyskażeniowym EA DN25: ∆p_EA = 100·(q_wod/k_v)² = 100·(4,06/7,5)² = **29,3** kPa — _k_v [ZAŁ — karta wyrobu]_
* Strata na filtrze DN25: ∆p_F = 100·(q_wod/k_v)² = 100·(4,06/10,0)² = **16,5** kPa — _k_v [ZAŁ — karta wyrobu]_

Zestaw wodomierzowy (od strony sieci): zawór odcinający, wodomierz, zawór odcinający, filtr z płukaniem wstecznym, zawór antyskażeniowy EA, reduktor ciśnienia; mostek wyrównawczy przed i za wodomierzem przy rurach metalowych (WT §116 ust. 3). Lokalizacja: pomieszczenie techniczne na parterze (WT §115 ust. 1; W-131).

### 6.1 Zabezpieczenia przed przepływem zwrotnym (PN-EN 1717)

| Miejsce | Kategoria płynu | Zabezpieczenie | Podstawa |
|:---|:---:|:---|:---|
| Za wodomierzem głównym (całe przyłącze) | 2 | EA DN25 (zawór antyskażeniowy kontrolowany) | WT §115 ust. 2; PN-EN 1717 tabl. 2–3; wymagania gestora (typ może być podwyższony w warunkach) |
| Zasilanie zasobnika c.w.u. (woda zmieniona temperaturowo) | 2 | EA w grupie bezpieczeństwa + zawór bezpieczeństwa + naczynie przeponowe c.w.u. | PN-EN 1717; PN-B-02440:1976 (powołana w WT, wycof.) |
| Napełnianie/uzupełnianie instalacji c.o. (woda z inhibitorami) | 3 | CA (zawór antyskażeniowy o strefach różnych ciśnień) + odłączany wąż napełniający | PN-EN 1717 — kat. 3 (przy glikolu toksycznym kat. 4 → BA) |
| Zawory ogrodowe (wąż, możliwy kontakt z nawozami) | 3 (4) | HA/HD — zawór ze złączką do węża z zabezpieczeniem; przy dozownikach nawozów kat. 4 → BA / przerwa | PN-EN 1717; R6 §3.6 |
| Pralka, zmywarka | 3 | zabezpieczenie wbudowane w urządzenie (PN-EN 61770) | PN-EN 1717 |
| Instalacja wody deszczowej (jeśli uzupełniana z wodociągu) | 5 | AA/AB — przerwa powietrzna; instalacje rozdzielone (bez połączenia) | WT §126 ust. 3 (W-136) |

## 7. Ciepła woda użytkowa

### 7.1 Zapotrzebowanie i zasobnik

* Dobowe zapotrzebowanie c.w.u. (55 °C) — wskaźnik na osobę: V_d1 = N·q_cwu = 5·50 = **250** dm³/d — _q_cwu = 50 dm³/(os·d) [ZAŁ]_
* Dobowe zapotrzebowanie wg metodologii EP: V_d2 = V_Wi·A_f = 1,40·262,4 = **367** dm³/d — _Dz.U. 2015 poz. 376 tab. 27 (R6-18)_
* Przyjęto: V_d = max(V_d1, V_d2) = **367** dm³/d
* Dobowe ciepło na c.w.u.: Q_d = V_d·c·(θ_cwu − θ_zw) = 367·1,163·10⁻³·45 = **19,22** kWh/d
* Roczne zapotrzebowanie normatywne (do EP): Q_W,nd = V_Wi·A_f·c·ρ·(θ_W − θ_0)·k_R·t_R/3600 = 1,40·262,4·4,19·1000·45·0,90·365/3600/1000 = **6320** kWh/a — _metodologia wzór (61) (R6-18)_
* Pobór szczytowy (1 h): wanna 140 dm³ + 2 natrysk(i) × 50 dm³ + 2 × umywalka 5 dm³ (40 °C) + zlewozmywak 10 dm³ (55 °C): V_55 = V_40·(40 − θ_zw)/(θ_cwu − θ_zw) + V_zl = 250·30/45 + 10 = **177** dm³ — _[ZAŁ — profil poboru]_
* Minimalna pojemność zasobnika: V_zas ≥ max(V_55/f_u; V_d), f_u = 0,8 = max(177/0,8; 367) = **367** dm³ — _[ZAŁ/W — PC: zasobnik ≈ dobowe zapotrzebowanie]_
* Dobrano zasobnik c.w.u. z wężownicą dla pompy ciepła: V_zas = **400** dm³
* Czas ładowania zasobnika (10 → 55 °C) mocą PC w trybie c.w.u.: t = V_zas·c·∆θ/P_PC = 400·1,163·10⁻³·45/7,2 = **2,91** h
* Wymagana powierzchnia wężownicy: A ≥ 0,25 m²/kW·P_PC = 0,25·7,2 = **1,80** m² — _dane producentów PC [W]_

### 7.2 Cyrkulacja

* Największa objętość wody w przewodach c.w.u. od zasobnika do punktu poboru: V_max = Σ(π·d_w²/4·L) = **10,63** dm³ — _reguła 3 litrów (DVGW W 551; R6 §3.6) [W]_
* Decyzja: **cyrkulacja czasowa (V > 3 dm³)** — _WT §120 ust. 1 — w domu jednorodzinnym niewymagana_
* Strata ciepła przewodów rozprowadzających c.w.u., L = 67,2 m (izolacja wg WT, λ = 0,040): Q_z = Σ q_l·L = **434,1** W
* Strata ciepła przewodu cyrkulacyjnego 16×2, L_c = 67,2 m: Q_c = q_l·L_c = **347,0** W
* Strumień cyrkulacji: V_c = (Q_z + Q_c)/(c·∆θ_c) = 781,1·3600/(4190·5) = **134,2** dm³/h — _∆θ_c = 5 K (DVGW W 551) [W]_
* Wysokość podnoszenia pompy cyrkulacyjnej: ∆p = 1,5·R·2L_c + ∆p_TV = 1,5·0,151·2·67,2 + 10 = **40,4** kPa — _zawór termostatyczny cyrkulacji 10 kPa [ZAŁ]_
* Roczne straty ciepła w pętli przy pracy 6 h/d: E = Q·h·365 = **1711** kWh/a
* Sprawność przesyłu c.w.u. do EP: η_W,d = **0,80** — _metodologia tab. 12 (R6-17)_

| Punkt | Objętość do punktu [dm³] |
|:---|---:|
| PRY03C | 8,93 |
| PRY12C | 5,59 |
| PRY18C | 10,63 |
| UMY02C | 4,61 |
| UMY05C | 8,92 |
| UMY11C | 10,01 |
| UMY14C | 5,58 |
| UMY20C | 10,63 |
| WAN09C | 9,96 |
| ZLE06C | 1,51 |
| ZLE08C | 0,77 |
| ZLE17C | 5,30 |

### 7.3 Dezynfekcja termiczna

* Wymagana temperatura w punktach podczas dezynfekcji: θ_dez = **70** °C — _WT §120 ust. 2a (70–80 °C; metoda cieplna wybrana — S-1)_
* Nastawa zasobnika w cyklu dezynfekcji: θ_zas = **75** °C — _zapas na straty w przewodach [ZAŁ]; grzałka elektryczna / tryb PC R290 wysokotemperaturowy_
* Energia jednego cyklu (dogrzanie zasobnika + 1 h pracy pętli): E_1 = V_zas·c·(θ_zas − θ_cwu) + Q_pętli·1 h = 400·1,163·10⁻³·20 + 0,781 = **10,09** kWh
* Energia roczna (cykl co 7 dni): E_rok = E_1·365/n = **526** kWh/a — _[ZAŁ]_

* Termostatyczny zawór mieszający na wyjściu z zasobnika (ochrona przed poparzeniem, 45–55 °C) z obejściem / programem na czas dezynfekcji; w cyklu dezynfekcji praca pompy cyrkulacyjnej (jeśli jest).
* Zabezpieczenie zasobnika przed przekroczeniem ciśnienia i temperatury: grupa bezpieczeństwa (zawór bezpieczeństwa 6 bar, zawór zwrotny EA), naczynie przeponowe c.w.u. (obliczenie w module ogrzewania).
* Ciepła woda po lewej stronie armatury (WT §120 ust. 5).

## 8. Izolacja cieplna przewodów

* Przeliczenie grubości izolacji na λ materiału (przykład d_z = 20 mm, t_ref = 20 mm): t = d_z/2·[((d_z + 2t_ref)/d_z)^(λ/0,035) − 1] = 20/2·[((20 + 2·20)/20)^(0,040/0,035) − 1] = **25,1** mm — _równoważność oporu cieplnego izolacji cylindrycznej [UPR]_

| Przewód | d_w [mm] | t_WT (λ=0,035) [mm] | t przy λ_izol [mm] | t przyjęta [mm] | przejścia (50 %) [mm] | q_l [W/m] | Podstawa |
|:---|---:|---:|---:|---:|---:|---:|:---|
| c.w.u. PE-RT/Al/PE-RT 16×2,0 | 12 | 20 | 25,5 | 30 | 10 | 5,6 | WT zał. 2 pkt 1.5 lp. 1–4 (W-135) |
| c.w.u. PE-RT/Al/PE-RT 20×2,0 | 16 | 20 | 25,1 | 30 | 10 | 6,3 | WT zał. 2 pkt 1.5 lp. 1–4 (W-135) |
| c.w.u. PE-RT/Al/PE-RT 25×2,5 | 20 | 20 | 24,8 | 25 | 10 | 7,2 | WT zał. 2 pkt 1.5 lp. 1–4 (W-135) |
| c.w.u. PE-RT/Al/PE-RT 32×3,0 | 26 | 30 | 37,5 | 40 | 15 | 6,8 | WT zał. 2 pkt 1.5 lp. 1–4 (W-135) |
| woda zimna PE-RT/Al/PE-RT 16×2,0 | 12 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 20×2,0 | 16 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 25×2,5 | 20 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 32×3,0 | 26 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 40×3,5 | 33 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 50×4,0 | 42 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| cyrkulacja 16×2,0 | 12 | 20 | 25,5 | 30 | 10 | 5,6 | W-135 |

## 9. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-131 | Przepływ obliczeniowy ≤ Q3 wodomierza | 4,06 m³/h | ≤ 6,30 m³/h | SPEŁNIONY | PN-EN ISO 4064 / MID |
| W-141 | Przykrycie przyłącza wodociągowego (ochrona przed przemarzaniem) | 1,40 m | ≥ 1,20 m | SPEŁNIONY | W-141: h_z + 0,4 m; PN-B-10725:1997, PN-B-10736:1999 (wycof.) — wiedza techniczna [niezweryfikowane] |
| W-131 | Średnica wodomierza ≤ średnicy wewn. przewodu | 25,00 mm | ≤ 42,00 mm | SPEŁNIONY | praktyka (PWr) |
| W-130 | Wymagane ciśnienie w sieci ≤ ciśnienie dyspozycyjne | 0,329 MPa | ≤ 0,350 MPa | SPEŁNIONY | warunki gestora [ZAŁ p_dysp]; przy niespełnieniu — zestaw podnoszący ciśnienie (ZPC) |
| W-130 | Nastawa reduktora ≥ ciśnienie wymagane za zestawem wodomierzowym (najniekorzystniejszy punkt) | 400 kPa | ≥ 223 kPa | SPEŁNIONY | kolejność: wodomierz, filtr, EA, reduktor |
| W-130 | Ciśnienie statyczne w punkcie ≤ 0,60 MPa (WT §114) | 0,400 MPa | ≤ 0,600 MPa | SPEŁNIONY | WT §114 ust. 1 |
| W-130 | Ciśnienie statyczne w punkcie ≤ 500 kPa (PN-EN 806-3 p. 4.3) | 400 kPa | ≤ 500 kPa | SPEŁNIONY | PN-EN 806-3:2006 p. 4.3 |
| W-132 | Maks. prędkość w przewodach rozdzielczych i pionach | 1,49 m/s | ≤ 2,00 m/s | SPEŁNIONY | PN-EN 806-3 (≤ 2 m/s) |
| W-133 | Temperatura c.w.u. w punktach | 55 °C | ∈ 55–60 °C | SPEŁNIONY | WT §120 ust. 2 |
| W-133 | Temperatura dezynfekcji w punktach | 70 °C | ∈ 70–80 °C | SPEŁNIONY | WT §120 ust. 2a |
| W-133 | Nastawa zasobnika w dezynfekcji ≥ temp. wymagana w punktach | 75 °C | ≥ 70 °C | SPEŁNIONY |  |
| W-133 | Pojemność zasobnika ≥ minimalna | 400 dm³ | ≥ 367 dm³ | SPEŁNIONY |  |

## 10. Wyniki do innych opracowań

| Wielkość | Wartość |
|:---|---:|
| q_obl_dm3s | 1,128 |
| p_wym_kPa | 328,9 |
| punkt_krytyczny | PRY18 prysznic (c.w.u.) |
| wodomierz | DN25 Q3=6.3 |
| Q_d_sr_m3 | 0,6000 |
| Q_h_max_m3 | 0,1500 |
| cwu_V_d_l | 367,0 |
| zasobnik_l | 400 |
| cyrkulacja | czasowa |
| eta_W_d | 0,8000 |
| Q_W_nd_kWh_a | 6320 |
| dezynfekcja_kWh_a | 526,0 |

## Podsumowanie sprawdzeń

Warunków: 12; spełnionych: 12; niespełnionych: 0; informacyjnych: 0.

## Źródła

1. WT — rozp. MI z 12.04.2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) §113–120, zał. 2 pkt 1.5 — stosowane na podst. art. 102a PB
2. PN-B-01706:1992 (+Az1:1999) — wg PWr, „Materiały pomocnicze do projektu instalacji wodociągowej” (tabl. q_n, przykład obliczeniowy) [W]
3. PN-EN 806-3:2006 p. 4.3 (ciśnienia) — próbka normy (iTeh, SIST EN 806-3:2006); tabl. LU wg instsani.pl [W]
4. Nowakowski E., Obliczeniowe przepływy wody w budynkach mieszkalnych – wybór metody, Rynek Instalacyjny 4/2011
5. PN-EN 1717:2003 / PN-EN 1717+A1:2026-09
6. Rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm.) — metodologia EP, wzór (61), tab. 12, 27
7. DVGW W 551 — reguła 3 litrów, ∆θ cyrkulacji 5 K [W]
8. Rejestr wymagań: docs/10_podstawy_prawne/00_rejestr_wymagan.md (W-130…W-137), wymagania.yaml
