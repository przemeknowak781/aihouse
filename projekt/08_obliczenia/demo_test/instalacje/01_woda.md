# Obliczenia instalacji wodociągowej i c.w.u.

Obiekt: Dom testowy pipeline'u 3D. Model: budynek: `/home/user/aihouse/model/test/dom_testowy.yaml`, dzialka: `/home/user/aihouse/model/test/dzialka_testowa.yaml`, wyposazenie: `/home/user/aihouse/model/test/wyposazenie_testowe.yaml`, instalacje: `/home/user/aihouse/model/test/instalacje_testowe.yaml`. Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE] tam, gdzie oznaczono [ZAŁ].

## 1. Podstawy i metoda

* WT §113–120 (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowane na podstawie art. 102a PB; wymagania W-130…W-137.
* PN-B-01706:1992 (+Az1:1999) — powołana w WT zał. 1 lp. 4 (wycofana w PKN, wiąże przez WT); kontrolnie PN-EN 806-3:2006.
* **Wybór metody przepływu obliczeniowego:** q = 0,682·(Σq_n)^0,45 − 0,14 (PN-B-01706, budynki mieszkalne) — metoda wskazana w rejestrze (W-132) i powołana przez WT; daje wartości wyższe (bezpieczniejsze) niż PN-EN 806-3 (Nowakowski, RI 4/2011); przejście LU → Q_D w PN-EN 806-3 jest graficzne — raport podaje ΣLU i Q_T = 0,1·ΣLU kontrolnie oraz warunki ciśnień PN-EN 806-3 p. 4.3.
* PN-EN 1717:2003 (WT zał. 1 lp. 5) / PN-EN 1717+A1:2026-09 (aktualna, EN) — zabezpieczenia przed przepływem zwrotnym.
* Straty liniowe: Darcy–Weisbach + Colebrook–White; straty miejscowe 50 % liniowych (PWr) [W].

## 2. Dane wejściowe i założenia

* Przyłącze: uzbrojenie projektowane (dzialka.yaml); L = 14,70 m; oś sieci 1,40 m p.p.t. [ZAŁ].
* Wodomierz: lokalizacja z instalacje.yaml.
* Rury instalacji: PE-RT/Al/PE-RT (k = 0,007 mm); przyłącze PE100 SDR11 [ZAŁ].
* Prędkości maks. [m/s]: przylacze 1,0, glowny 1,0, pion 1,5, rozdzielczy 1,5, podejscie 2,0 (PN-EN 806-3: ≤ 2 m/s; przewody główne 1,0 m/s dla ograniczenia strat i hałasu) [ZAŁ].
* Długości odcinków: trasy równoległe do ścian (odległość „miejska” w rzucie) + podejścia pionowe; piony zgrupowane automatycznie (R ≤ 3,5 m) lub z instalacje.yaml [UPR].
* Ciśnienie w sieci: dyspozycyjne 0,35 MPa, maks. statyczne 0,60 MPa [ZAŁ — do potwierdzenia w warunkach technicznych gestora, D-23].

### 2.1 Przybory (z modelu)

| Przybór | Liczba | q_n zw [dm³/s] | q_n cw [dm³/s] | Σq_n [dm³/s] | LU (zw+cw) | DU [l/s] | Odpływ |
|:---|---:|---:|---:|---:|---:|---:|:---|
| Pralka automatyczna (≤ 12 kg) | 1 | 0,25 | 0,00 | 0,25 | 2 | 1,50 | DN50 |
| Natrysk (odpływ liniowy/brodzik bez korka) z baterią | 1 | 0,15 | 0,15 | 0,30 | 4 | 0,60 | DN50 |
| Umywalka z baterią | 2 | 0,07 | 0,07 | 0,28 | 2 | 0,50 | DN40 |
| Miska ustępowa z płuczką zbiornikową 6 l | 2 | 0,13 | 0,00 | 0,26 | 1 | 2,00 | DN100 |
| Zawór czerpalny ogrodowy DN15 ze złączką do węża | 2 | 0,30 | 0,00 | 0,60 | 5 | 0,00 | — |
| Zlewozmywak z baterią | 1 | 0,07 | 0,07 | 0,14 | 4 | 0,80 | DN50 |
| Zmywarka do naczyń | 1 | 0,15 | 0,00 | 0,15 | 2 | 0,80 | DN50 |

| Id | Typ | Kond. | Pomieszczenie | x, y [m] | Źródło |
|:---|:---|:---|:---|:---|:---|
| ZLE01 | zlew | P0 | 0.04 Kuchnia z jadalnią | 8,20; 7,89 | wyposazenie |
| ZMY02 | zmywarka | P0 | 0.04 Kuchnia z jadalnią | 8,90; 7,89 | wyposazenie |
| WC03 | wc | P0 | 0.02 Hol ze schodami | 4,09; 6,60 | instalacje |
| UMY04 | umywalka | P0 | 0.02 Hol ze schodami | 4,09; 7,50 | instalacje |
| WC05 | wc | P1 | 1.04 Garderoba | 9,89; 7,00 | instalacje |
| UMY06 | umywalka | P1 | 1.04 Garderoba | 8,60; 7,89 | instalacje |
| PRY07 | prysznic | P1 | 1.04 Garderoba | 7,08; 7,20 | instalacje |
| PRA08 | pralka | P1 | 1.04 Garderoba | 9,89; 5,20 | instalacje |
| ZAW09 | zawor_ogrodowy | P0 | — na zewnątrz / poza pomieszczeniem | 2,00; −0,30 | instalacje |
| ZAW10 | zawor_ogrodowy | P0 | — na zewnątrz / poza pomieszczeniem | 9,00; 8,30 | instalacje |

### 2.2 Piony

| Pion | Położenie x, y [m] | Kondygnacje | Pomieszczenia | Przybory | Źródło |
|:---|:---|:---|:---|:---|:---|
| P1 | 4,09; 6,60 | P0 | P0: 0.02 | WC03, UMY04 | auto |
| P2 | 9,89; 7,00 | P0, P1 | P0: 0.04; P1: 1.04 | ZLE01, ZMY02, WC05, UMY06, PRY07, PRA08 | auto |

## 3. Zapotrzebowanie na wodę

* Średnie dobowe zapotrzebowanie (bytowe): Q_d,śr = N·q_j = 4·120/1000 = **0,480** m³/d — _q_j = 120 dm³/(os·d) [ZAŁ — dom jednorodzinny z pełnym wyposażeniem]_
* Podlewanie zieleni (sezon V–IX): Q_pod = A·q_p = 100·3,0/1000 = **0,300** m³/d — _[ZAŁ]_
* Maksymalne dobowe: Q_d,max = N_d·Q_d,śr + Q_pod = 1,5·0,480 + 0,300 = **1,020** m³/d — _N_d = 1,5 [ZAŁ]_
* Maksymalne godzinowe: Q_h,max = N_h·Q_d,max/24 = 3,0·1,020/24 = **0,128** m³/h — _N_h = 3,0 [ZAŁ]_

## 4. Przepływ obliczeniowy

* Suma wypływów normatywnych (woda zimna + ciepła) na zestawie wodomierzowym: Σq_n = **1,98** dm³/s — _PN-92/B-01706 tabl. 1_
* Przepływ obliczeniowy: q = 0,682·(Σq_n)^0,45 − 0,14 = 0,682·(1,98)^0,45 − 0,14 = **0,787** dm³/s — _PN-92/B-01706 (budynki mieszkalne); W-132_
* Przepływ obliczeniowy przyjęty (≥ max q_n, ≤ Σq_n): q = **0,787** dm³/s — _[UPR]_
* Kontrolnie PN-EN 806-3: suma jednostek obciążenia i Q_T: Q_T = 0,1·ΣLU = 0,1·28 = **2,80** l/s — _PN-EN 806-3 tabl. 2 (Q_D z nomogramu normy ≤ Q_T)_

## 5. Wymiarowanie przewodów i straty ciśnienia

### 5.1 Woda zimna (z przyłączem i zasilaniem zasobnika)

| Nr | Odcinek | Typ | L [m] | Σq_n [dm³/s] | q [dm³/s] | ΣLU | Rura d_z×s | d_w [mm] | v [m/s] | R [kPa/m] | ∆p_l [kPa] | ∆p_m [kPa] |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|
| 1 | SIEC→WEJ: przyłącze wodociągowe (PE100 SDR11) | przylacze | 14,70 | 1,98 | 0,787 | 28 | PE100 SDR11 40×3,7 | 33 | 0,94 | 0,350 | 5,14 | 2,57 |
| 2 | WEJ→WOD: wejście do budynku → zestaw wodomierzowy | glowny | 3,90 | 1,98 | 0,787 | 28 | PE-RT/Al/PE-RT 40×3,5 | 33 | 0,92 | 0,327 | 1,28 | 0,64 |
| 3 | WOD→T0: zestaw wodomierzowy (zawór, wodomierz, filtr, EA) | glowny | 1,00 | 1,98 | 0,787 | 28 | PE-RT/Al/PE-RT 40×3,5 | 33 | 0,92 | 0,327 | 0,33 | 0,16 |
| 4 | T0→ZAS: zasilanie zasobnika c.w.u. (grupa bezpieczeństwa) | glowny | 1,40 | 0,36 | 0,291 | 6 | PE-RT/Al/PE-RT 25×2,5 | 20 | 0,93 | 0,618 | 0,87 | 0,43 |
| 5 | T0→ZAW09: przewód do zawór czerpalny ogrodowy dn15 ze złączką do węża (ZAW09) | rozdzielczy | 9,60 | 0,30 | 0,300 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,49 | 1,906 | 18,30 | 9,15 |
| 6 | T0→ZAW10: przewód do zawór czerpalny ogrodowy dn15 ze złączką do węża (ZAW10) | rozdzielczy | 9,20 | 0,30 | 0,300 | 5 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,49 | 1,906 | 17,54 | 8,77 |
| 7 | T0→P1Z@P0: przewód rozdzielczy do pionu P1 | glowny | 4,19 | 0,20 | 0,191 | 2 | PE-RT/Al/PE-RT 20×2,0 | 16 | 0,95 | 0,855 | 3,58 | 1,79 |
| 8 | P1Z@P0→RZ_0.02: odgałęzienie do pom. 0.02 Hol ze schodami | rozdzielczy | 0,96 | 0,20 | 0,191 | 2 | PE-RT/Al/PE-RT 20×2,0 | 16 | 0,95 | 0,855 | 0,82 | 0,41 |
| 9 | RZ_0.02→WC03Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC03) | podejscie | 0,95 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 1,64 | 0,82 |
| 10 | RZ_0.02→UMY04Z: podejście: umywalka z baterią (UMY04) | podejscie | 1,25 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,73 | 0,37 |
| 11 | T0→P2Z@P0: przewód rozdzielczy do pionu P2 | glowny | 9,59 | 0,82 | 0,484 | 10 | PE-RT/Al/PE-RT 32×3,0 | 26 | 0,91 | 0,433 | 4,15 | 2,08 |
| 12 | P2Z@P0→RZ_0.04: odgałęzienie do pom. 0.04 Kuchnia z jadalnią | rozdzielczy | 2,73 | 0,22 | 0,205 | 4 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,973 | 2,66 | 1,33 |
| 13 | RZ_0.04→ZLE01Z: podejście: zlewozmywak z baterią (ZLE01) | podejscie | 1,20 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 0,70 | 0,35 |
| 14 | RZ_0.04→ZMY02Z: podejście: zmywarka do naczyń (ZMY02) | podejscie | 0,65 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 1,45 | 0,72 |
| 15 | P2Z@P0→P2Z@P1: pion P2 P0→P1 | pion | 3,06 | 0,60 | 0,402 | 6 | PE-RT/Al/PE-RT 25×2,5 | 20 | 1,28 | 1,097 | 3,36 | 1,68 |
| 16 | P2Z@P1→RZ_1.04: odgałęzienie do pom. 1.04 Garderoba | rozdzielczy | 1,70 | 0,60 | 0,402 | 6 | PE-RT/Al/PE-RT 25×2,5 | 20 | 1,28 | 1,097 | 1,86 | 0,93 |
| 17 | RZ_1.04→WC05Z: podejście: miska ustępowa z płuczką zbiornikową 6 l (WC05) | podejscie | 1,71 | 0,13 | 0,130 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,15 | 1,729 | 2,96 | 1,48 |
| 18 | RZ_1.04→UMY06Z: podejście: umywalka z baterią (UMY06) | podejscie | 2,14 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,587 | 1,26 | 0,63 |
| 19 | RZ_1.04→PRY07Z: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY07) | podejscie | 3,07 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 2,224 | 6,83 | 3,41 |
| 20 | RZ_1.04→PRA08Z: podejście: pralka automatyczna (≤ 12 kg) (PRA08) | podejscie | 3,15 | 0,25 | 0,250 | 2 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,24 | 1,380 | 4,35 | 2,17 |

### 5.2 Ciepła woda użytkowa (55 °C)

| Nr | Odcinek | Typ | L [m] | Σq_n [dm³/s] | q [dm³/s] | ΣLU | Rura d_z×s | d_w [mm] | v [m/s] | R [kPa/m] | ∆p_l [kPa] | ∆p_m [kPa] |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|---:|---:|---:|---:|
| 21 | ZAS→P1C@P0: przewód rozdzielczy do pionu P1 | glowny | 3,79 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,73 | 0,87 |
| 22 | P1C@P0→RC_0.02: odgałęzienie do pom. 0.02 Hol ze schodami | rozdzielczy | 1,41 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,64 | 0,32 |
| 23 | RC_0.02→UMY04C: podejście: umywalka z baterią (UMY04) | podejscie | 0,80 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,37 | 0,18 |
| 24 | ZAS→P2C@P0: przewód rozdzielczy do pionu P2 | glowny | 9,19 | 0,29 | 0,251 | 5 | PE-RT/Al/PE-RT 25×2,5 | 20 | 0,80 | 0,379 | 3,49 | 1,74 |
| 25 | P2C@P0→RC_0.04: odgałęzienie do pom. 0.04 Kuchnia z jadalnią | rozdzielczy | 3,09 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 1,41 | 0,71 |
| 26 | RC_0.04→ZLE01C: podejście: zlewozmywak z baterią (ZLE01) | podejscie | 0,85 | 0,07 | 0,070 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,39 | 0,19 |
| 27 | P2C@P0→P2C@P1: pion P2 P0→P1 | pion | 3,06 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,38 | 1,19 |
| 28 | P2C@P1→RC_1.04: odgałęzienie do pom. 1.04 Garderoba | rozdzielczy | 3,10 | 0,22 | 0,205 | 3 | PE-RT/Al/PE-RT 20×2,0 | 16 | 1,02 | 0,778 | 2,41 | 1,21 |
| 29 | RC_1.04→UMY06C: podejście: umywalka z baterią (UMY06) | podejscie | 1,91 | 0,07 | 0,070 | 1 | PE-RT/Al/PE-RT 16×2,0 | 12 | 0,62 | 0,457 | 0,87 | 0,44 |
| 30 | RC_1.04→PRY07C: podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią (PRY07) | podejscie | 2,01 | 0,15 | 0,150 | 2 | PE-RT/Al/PE-RT 16×2,0 | 12 | 1,33 | 1,790 | 3,60 | 1,80 |

### 5.3 Wymagane ciśnienie — najniekorzystniej położony punkt

* Najniekorzystniej położony punkt: natrysk (odpływ liniowy/brodzik bez korka) z baterią PRY07 (kond. P1, pom. 1.04), c.w.u.
* Wysokość geometryczna (oś sieci → wylewka): h_g = z_wyl − z_sieci = 4,26 − (−1,61) = **5,87** m
* Ciśnienie na pokonanie wysokości: p_g = ρ·g·h_g = 1000·9,81·5,87/1000 = **57,6** kPa
* Straty liniowe na drodze (odcinki 1, 2, 3, 4, 24, 27, 28, 30): Σ∆p_l = 5,1 + 1,3 + 0,3 + 0,9 + 3,5 + 2,4 + 2,4 + 3,6 = **19,5** kPa — _Darcy–Weisbach, Colebrook–White_
* Straty miejscowe: Σ∆p_m = 0,5·Σ∆p_l = 0,5·19,5 = **9,7** kPa — _PWr [W]_
* Straty na urządzeniach (wodomierz, EA, filtr, podgrzewacz, TZM): Σ∆p_urz = **110,6** kPa
* Wymagane ciśnienie wypływu: p_w = **100** kPa — _PN-92/B-01706 tabl. 1; PN-EN 806-3 p. 4.3 (≥ 100 kPa)_
* Wymagane ciśnienie w miejscu włączenia do sieci: p_wym = p_g + Σ∆p_l + Σ∆p_m + Σ∆p_urz + p_w = 57,6 + 19,5 + 9,7 + 110,6 + 100 = **297,5** kPa — _W-130_

| Punkt | Medium | h_g [m] | Σ∆p_l [kPa] | Σ∆p_m [kPa] | Σ∆p_urz [kPa] | p_w [kPa] | p_wym [kPa] |
|:---|:---|---:|---:|---:|---:|---:|---:|
| PRY07 prysznic (P1) | c.w.u. | 5,87 | 19,5 | 9,7 | 110,6 | 100 | 297,5 |
| UMY06 umywalka (P1) | c.w.u. | 5,77 | 16,8 | 8,4 | 110,6 | 100 | 292,4 |
| PRY07 prysznic (P1) | woda zimna | 5,87 | 22,9 | 11,5 | 80,6 | 100 | 272,6 |
| PRA08 pralka (P1) | woda zimna | 5,47 | 20,5 | 10,2 | 80,6 | 100 | 265,0 |
| UMY06 umywalka (P1) | woda zimna | 5,77 | 17,4 | 8,7 | 80,6 | 100 | 263,3 |
| ZLE01 zlew (P0) | c.w.u. | 2,76 | 12,9 | 6,4 | 110,6 | 100 | 257,1 |
| UMY04 umywalka (P0) | c.w.u. | 2,71 | 10,4 | 5,2 | 110,6 | 100 | 252,8 |
| ZAW09 zawor_ogrodowy (P0) | woda zimna | 2,21 | 25,0 | 12,5 | 80,6 | 100 | 239,9 |
| ZAW10 zawor_ogrodowy (P0) | woda zimna | 2,21 | 24,3 | 12,1 | 80,6 | 100 | 238,7 |
| ZLE01 zlew (P0) | woda zimna | 2,76 | 14,3 | 7,1 | 80,6 | 100 | 229,1 |
| UMY04 umywalka (P0) | woda zimna | 2,71 | 11,9 | 5,9 | 80,6 | 100 | 225,0 |
| ZMY02 zmywarka (P0) | woda zimna | 2,21 | 15,0 | 7,5 | 80,6 | 100 | 224,8 |
| WC05 wc (P1) | woda zimna | 5,47 | 19,1 | 9,5 | 80,6 | 50 | 212,9 |
| WC03 wc (P0) | woda zimna | 2,41 | 12,8 | 6,4 | 80,6 | 50 | 173,5 |

### 5.4 Ciśnienie statyczne

* Maks. ciśnienie statyczne w najniżej położonym punkcie: p_st = p_sieci,max − ρ·g·(z_min − z_sieci) = 600 − 9,81·(0,60 − (−1,61)) = **578** kPa
* Reduktor ciśnienia za wodomierzem (nastawa): p_red = **400** kPa — _PN-EN 806-3 p. 4.3: p_st ≤ 500 kPa w punktach_

## 6. Zestaw wodomierzowy i zabezpieczenia

* Przepływ obliczeniowy na wodomierzu: q_wod = 3,6·q = 3,6·0,787 = **2,83** m³/h
* Dobór wodomierza (pierwszy o Q3 ≥ q_wod): q_wod ≤ Q3 = 2,83 ≤ 4,0 = **DN20, Q3 = 4,0 m³/h** — _PN-EN ISO 4064 (MID); przykład PWr_
* Strata ciśnienia na wodomierzu: ∆p_wod = ∆p(Q3)·(q_wod/Q3)² = 63·(2,83/4,0)² = **31,6** kPa — _klasa ΔP63 [ZAŁ] — przyjąć z karty wyrobu_
* Strata na zaworze antyskażeniowym EA DN20: ∆p_EA = 100·(q_wod/k_v)² = 100·(2,83/4,9)² = **33,5** kPa — _k_v [ZAŁ — karta wyrobu]_
* Strata na filtrze DN20: ∆p_F = 100·(q_wod/k_v)² = 100·(2,83/7,2)² = **15,5** kPa — _k_v [ZAŁ — karta wyrobu]_

Zestaw wodomierzowy (od strony sieci): zawór odcinający, wodomierz, zawór odcinający, filtr z płukaniem wstecznym, zawór antyskażeniowy EA, reduktor ciśnienia; mostek wyrównawczy przed i za wodomierzem przy rurach metalowych (WT §116 ust. 3). Lokalizacja: pomieszczenie techniczne na parterze (WT §115 ust. 1; W-131).

### 6.1 Zabezpieczenia przed przepływem zwrotnym (PN-EN 1717)

| Miejsce | Kategoria płynu | Zabezpieczenie | Podstawa |
|:---|:---:|:---|:---|
| Za wodomierzem głównym (całe przyłącze) | 2 | EA DN20 (zawór antyskażeniowy kontrolowany) | WT §115 ust. 2; PN-EN 1717 tabl. 2–3; wymagania gestora (typ może być podwyższony w warunkach) |
| Zasilanie zasobnika c.w.u. (woda zmieniona temperaturowo) | 2 | EA w grupie bezpieczeństwa + zawór bezpieczeństwa + naczynie przeponowe c.w.u. | PN-EN 1717; PN-B-02440:1976 (powołana w WT, wycof.) |
| Napełnianie/uzupełnianie instalacji c.o. (woda z inhibitorami) | 3 | CA (zawór antyskażeniowy o strefach różnych ciśnień) + odłączany wąż napełniający | PN-EN 1717 — kat. 3 (przy glikolu toksycznym kat. 4 → BA) |
| Zawory ogrodowe (wąż, możliwy kontakt z nawozami) | 3 (4) | HA/HD — zawór ze złączką do węża z zabezpieczeniem; przy dozownikach nawozów kat. 4 → BA / przerwa | PN-EN 1717; R6 §3.6 |
| Pralka, zmywarka | 3 | zabezpieczenie wbudowane w urządzenie (PN-EN 61770) | PN-EN 1717 |
| Instalacja wody deszczowej (jeśli uzupełniana z wodociągu) | 5 | AA/AB — przerwa powietrzna; instalacje rozdzielone (bez połączenia) | WT §126 ust. 3 (W-136) |

## 7. Ciepła woda użytkowa

### 7.1 Zapotrzebowanie i zasobnik

* Dobowe zapotrzebowanie c.w.u. (55 °C) — wskaźnik na osobę: V_d1 = N·q_cwu = 4·50 = **200** dm³/d — _q_cwu = 50 dm³/(os·d) [ZAŁ]_
* Dobowe zapotrzebowanie wg metodologii EP: V_d2 = V_Wi·A_f = 1,40·139,5 = **195** dm³/d — _Dz.U. 2015 poz. 376 tab. 27 (R6-18)_
* Przyjęto: V_d = max(V_d1, V_d2) = **200** dm³/d
* Dobowe ciepło na c.w.u.: Q_d = V_d·c·(θ_cwu − θ_zw) = 200·1,163·10⁻³·45 = **10,47** kWh/d
* Roczne zapotrzebowanie normatywne (do EP): Q_W,nd = V_Wi·A_f·c·ρ·(θ_W − θ_0)·k_R·t_R/3600 = 1,40·139,5·4,19·1000·45·0,90·365/3600/1000 = **3361** kWh/a — _metodologia wzór (61) (R6-18)_
* Pobór szczytowy (1 h): 1 natrysk(i) × 50 dm³ + 2 × umywalka 5 dm³ (40 °C) + zlewozmywak 10 dm³ (55 °C): V_55 = V_40·(40 − θ_zw)/(θ_cwu − θ_zw) + V_zl = 60·30/45 + 10 = **50** dm³ — _[ZAŁ — profil poboru]_
* Minimalna pojemność zasobnika: V_zas ≥ max(V_55/f_u; V_d), f_u = 0,8 = max(50/0,8; 200) = **200** dm³ — _[ZAŁ/W — PC: zasobnik ≈ dobowe zapotrzebowanie]_
* Dobrano zasobnik c.w.u. z wężownicą dla pompy ciepła: V_zas = **200** dm³
* Czas ładowania zasobnika (10 → 55 °C) mocą PC w trybie c.w.u.: t = V_zas·c·∆θ/P_PC = 200·1,163·10⁻³·45/5,0 = **2,09** h
* Wymagana powierzchnia wężownicy: A ≥ 0,25 m²/kW·P_PC = 0,25·5,0 = **1,25** m² — _dane producentów PC [W]_

### 7.2 Cyrkulacja

* Największa objętość wody w przewodach c.w.u. od zasobnika do punktu poboru: V_max = Σ(π·d_w²/4·L) = **4,35** dm³ — _reguła 3 litrów (DVGW W 551; R6 §3.6) [W]_
* Decyzja: **cyrkulacja czasowa (V > 3 dm³)** — _WT §120 ust. 1 — w domu jednorodzinnym niewymagana_
* Strata ciepła przewodów rozprowadzających c.w.u., L = 23,6 m (izolacja wg WT, λ = 0,040): Q_z = Σ q_l·L = **150,8** W
* Strata ciepła przewodu cyrkulacyjnego 16×2, L_c = 23,6 m: Q_c = q_l·L_c = **122,1** W
* Strumień cyrkulacji: V_c = (Q_z + Q_c)/(c·∆θ_c) = 272,9·3600/(4190·5) = **46,9** dm³/h — _∆θ_c = 5 K (DVGW W 551) [W]_
* Wysokość podnoszenia pompy cyrkulacyjnej: ∆p = 1,5·R·2L_c + ∆p_TV = 1,5·0,025·2·23,6 + 10 = **11,8** kPa — _zawór termostatyczny cyrkulacji 10 kPa [ZAŁ]_
* Roczne straty ciepła w pętli przy pracy 6 h/d: E = Q·h·365 = **598** kWh/a
* Sprawność przesyłu c.w.u. do EP: η_W,d = **0,80** — _metodologia tab. 12 (R6-17)_

| Punkt | Objętość do punktu [dm³] |
|:---|---:|
| PRY07C | 4,35 |
| UMY04C | 0,68 |
| UMY06C | 4,34 |
| ZLE01C | 3,33 |

### 7.3 Dezynfekcja termiczna

* Wymagana temperatura w punktach podczas dezynfekcji: θ_dez = **70** °C — _WT §120 ust. 2a (70–80 °C; metoda cieplna wybrana — S-1)_
* Nastawa zasobnika w cyklu dezynfekcji: θ_zas = **75** °C — _zapas na straty w przewodach [ZAŁ]; grzałka elektryczna / tryb PC R290 wysokotemperaturowy_
* Energia jednego cyklu (dogrzanie zasobnika + 1 h pracy pętli): E_1 = V_zas·c·(θ_zas − θ_cwu) + Q_pętli·1 h = 200·1,163·10⁻³·20 + 0,273 = **4,92** kWh
* Energia roczna (cykl co 7 dni): E_rok = E_1·365/n = **257** kWh/a — _[ZAŁ]_

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
| woda zimna PE-RT/Al/PE-RT 16×2,0 | 12 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 20×2,0 | 16 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 25×2,5 | 20 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 32×3,0 | 26 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| woda zimna PE-RT/Al/PE-RT 40×3,5 | 33 | — | — | 9 | — | — | izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga] |
| cyrkulacja 16×2,0 | 12 | 20 | 25,5 | 30 | 10 | 5,6 | W-135 |

## 9. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-131 | Przepływ obliczeniowy ≤ Q3 wodomierza | 2,83 m³/h | ≤ 4,00 m³/h | SPEŁNIONY | PN-EN ISO 4064 / MID |
| W-131 | Średnica wodomierza ≤ średnicy wewn. przewodu | 20,00 mm | ≤ 33,00 mm | SPEŁNIONY | praktyka (PWr) |
| W-130 | Wymagane ciśnienie w sieci ≤ ciśnienie dyspozycyjne | 0,297 MPa | ≤ 0,350 MPa | SPEŁNIONY | warunki gestora [ZAŁ p_dysp]; przy niespełnieniu — zestaw podnoszący ciśnienie (ZPC) |
| W-130 | Nastawa reduktora ≥ ciśnienie wymagane za zestawem wodomierzowym (najniekorzystniejszy punkt) | 400 kPa | ≥ 186 kPa | SPEŁNIONY | kolejność: wodomierz, filtr, EA, reduktor |
| W-130 | Ciśnienie statyczne w punkcie ≤ 0,60 MPa (WT §114) | 0,400 MPa | ≤ 0,600 MPa | SPEŁNIONY | WT §114 ust. 1 |
| W-130 | Ciśnienie statyczne w punkcie ≤ 500 kPa (PN-EN 806-3 p. 4.3) | 400 kPa | ≤ 500 kPa | SPEŁNIONY | PN-EN 806-3:2006 p. 4.3 |
| W-132 | Maks. prędkość w przewodach rozdzielczych i pionach | 1,49 m/s | ≤ 2,00 m/s | SPEŁNIONY | PN-EN 806-3 (≤ 2 m/s) |
| W-133 | Temperatura c.w.u. w punktach | 55 °C | ∈ 55–60 °C | SPEŁNIONY | WT §120 ust. 2 |
| W-133 | Temperatura dezynfekcji w punktach | 70 °C | ∈ 70–80 °C | SPEŁNIONY | WT §120 ust. 2a |
| W-133 | Nastawa zasobnika w dezynfekcji ≥ temp. wymagana w punktach | 75 °C | ≥ 70 °C | SPEŁNIONY |  |
| W-133 | Pojemność zasobnika ≥ minimalna | 200 dm³ | ≥ 200 dm³ | SPEŁNIONY |  |

## 10. Wyniki do innych opracowań

| Wielkość | Wartość |
|:---|---:|
| q_obl_dm3s | 0,7870 |
| p_wym_kPa | 297,5 |
| punkt_krytyczny | PRY07 prysznic (c.w.u.) |
| wodomierz | DN20 Q3=4.0 |
| Q_d_sr_m3 | 0,4800 |
| Q_h_max_m3 | 0,1280 |
| cwu_V_d_l | 200,0 |
| zasobnik_l | 200 |
| cyrkulacja | czasowa |
| eta_W_d | 0,8000 |
| Q_W_nd_kWh_a | 3361 |
| dezynfekcja_kWh_a | 257,0 |

## Podsumowanie sprawdzeń

Warunków: 11; spełnionych: 11; niespełnionych: 0; informacyjnych: 0.

## Źródła

1. WT — rozp. MI z 12.04.2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) §113–120, zał. 2 pkt 1.5 — stosowane na podst. art. 102a PB
2. PN-B-01706:1992 (+Az1:1999) — wg PWr, „Materiały pomocnicze do projektu instalacji wodociągowej” (tabl. q_n, przykład obliczeniowy) [W]
3. PN-EN 806-3:2006 p. 4.3 (ciśnienia) — próbka normy (iTeh, SIST EN 806-3:2006); tabl. LU wg instsani.pl [W]
4. Nowakowski E., Obliczeniowe przepływy wody w budynkach mieszkalnych – wybór metody, Rynek Instalacyjny 4/2011
5. PN-EN 1717:2003 / PN-EN 1717+A1:2026-09
6. Rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm.) — metodologia EP, wzór (61), tab. 12, 27
7. DVGW W 551 — reguła 3 litrów, ∆θ cyrkulacji 5 K [W]
8. Rejestr wymagań: docs/10_podstawy_prawne/00_rejestr_wymagan.md (W-130…W-137), wymagania.yaml
