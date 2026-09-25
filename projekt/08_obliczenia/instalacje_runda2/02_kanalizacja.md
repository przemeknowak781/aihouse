# Obliczenia instalacji kanalizacji sanitarnej

Obiekt: Dom LAMELA. PN-EN 12056-2:2002, system I. Dane przykładowe oznaczono [ZAŁ].

## 1. Podstawy i założenia

* WT §122–125, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-138…W-140, W-118.
* PN-EN 12056-1…5:2002 (PL, aktualne); PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10.
* Tablice PN-EN 12056-2 (Q_max podejść i pionów) — wartości z literatury, oznaczone [NZW] (treść normy płatna; rejestr R6 Nierozstrz. 8). Przepustowość przewodów odpływowych liczona wzorem Colebrooka–White'a jak w zał. B normy.
* K = 0,5 — użytkowanie nieciągłe (budynek mieszkalny), PN-EN 12056-2 tabl. 3 (W-138).
* Rury: wewnątrz PP-HT (PN-EN 1451-1), pod posadzką i przykanalik PVC-U SN8 lity (PN-EN 1401-1+A1:2023-09) [ZAŁ].
* Spadki: podejścia 2,0 %, przewody pod posadzką 2,0 % (≤ DN100) / 1,5 % (> DN100), przykanalik 2,0 % [ZAŁ].
* Trasy: podejścia i przewody pod posadzką równoległe do ścian (odległość „miejska”) [UPR].
* Rzędne przewodów obniżono o 0,34 m względem założenia startowego (−0,65 m), aby zapewnić przykrycie przykanalika ≥ 1,00 m (strefa przemarzania).

## 2. Przybory i równoważniki odpływu

| Id | Przybór | Kond. | Pom. | DU [l/s] | Podejście |
|:---|:---|:---|:---|---:|:---|
| WC01 | Miska ustępowa z płuczką zbiornikową 6 l | P0 | 0.03 | 2,0 | DN100 |
| UMY02 | Umywalka z baterią | P0 | 0.03 | 0,5 | DN40 |
| PRY03 | Natrysk (odpływ liniowy/brodzik bez korka) z baterią | P0 | 0.09 | 0,6 | DN50 |
| WC04 | Miska ustępowa z płuczką zbiornikową 6 l | P0 | 0.09 | 2,0 | DN100 |
| UMY05 | Umywalka z baterią | P0 | 0.09 | 0,5 | DN40 |
| ZLE06 | Zlewozmywak z baterią | P0 | 0.06 | 0,8 | DN50 |
| ZMY07 | Zmywarka do naczyń | P0 | 0.06 | 0,8 | DN50 |
| ZLE08 | Zlewozmywak z baterią | P0 | 0.12 | 0,8 | DN50 |
| WAN09 | Wanna z baterią | P1 | 1.05 | 0,8 | DN50 |
| WC10 | Miska ustępowa z płuczką zbiornikową 6 l | P1 | 1.05 | 2,0 | DN100 |
| UMY11 | Umywalka nablatowa z baterią | P1 | 1.05 | 0,5 | DN40 |
| PRY12 | Natrysk (odpływ liniowy/brodzik bez korka) z baterią | P1 | 1.07 | 0,6 | DN50 |
| WC13 | Miska ustępowa z płuczką zbiornikową 6 l | P1 | 1.07 | 2,0 | DN100 |
| UMY14 | Umywalka z baterią | P1 | 1.07 | 0,5 | DN40 |
| PRA15 | Pralka automatyczna (≤ 12 kg) | P1 | 1.08 | 1,5 | DN50 |
| SUS16 | Suszarka kondensacyjna z odprowadzeniem skroplin | P1 | 1.08 | 0,0 | DN40 |
| ZLE17 | Zlewozmywak z baterią | P1 | 1.08 | 0,8 | DN50 |
| PRY18 | Natrysk (odpływ liniowy/brodzik bez korka) z baterią | P2 | 2.04 | 0,6 | DN50 |
| WC19 | Miska ustępowa z płuczką zbiornikową 6 l | P2 | 2.04 | 2,0 | DN100 |
| UMY20 | Umywalka nablatowa z baterią | P2 | 2.04 | 0,5 | DN40 |
| WPU23 | Wpust podłogowy DN50 | P0 | 0.12 | 0,8 | DN50 |

## 3. Przewody

| Odcinek | Opis | Rodzaj | DN | Rura | L [m] | ΣDU [l/s] | Q_ww [l/s] | i [%] | h/d | v [m/s] | Q_max [l/s] | Uwagi |
|:---|:---|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| PRY03 | podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią | podejscie | 50 | PP-HT 50 | 3,43 | 0,6 | 0,60 | 2,0 | — | — | — |  |
| WC04 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 1,20 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY05 | podejście: umywalka z baterią | podejscie | 40 | PP-HT 40 | 2,20 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_0.09 | podejście zbiorcze w pom. 0.09 → pion K1 | podejscie_zbiorcze | 100 | PP-HT 110 | 3,43 | 3,1 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| WAN09 | podejście: wanna z baterią | podejscie | 50 | PP-HT 50 | 3,14 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| WC10 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 0,47 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY11 | podejście: umywalka nablatowa z baterią | podejscie | 40 | PP-HT 40 | 2,59 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_1.05 | podejście zbiorcze w pom. 1.05 → pion K1 | podejscie_zbiorcze | 100 | PP-HT 110 | 3,14 | 3,3 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| PRY18 | podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią | podejscie | 50 | PP-HT 50 | 3,14 | 0,6 | 0,60 | 2,0 | — | — | — |  |
| WC19 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 0,47 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY20 | podejście: umywalka nablatowa z baterią | podejscie | 40 | PP-HT 40 | 2,34 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_2.04 | podejście zbiorcze w pom. 2.04 → pion K1 | podejscie_zbiorcze | 100 | PP-HT 110 | 3,14 | 3,1 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| WC01 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 0,62 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY02 | podejście: umywalka z baterią | podejscie | 40 | PP-HT 40 | 2,01 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_0.03 | podejście zbiorcze w pom. 0.03 → pion K2 | podejscie_zbiorcze | 100 | PP-HT 110 | 2,01 | 2,5 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| PRY12 | podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią | podejscie | 50 | PP-HT 50 | 0,62 | 0,6 | 0,60 | 2,0 | — | — | — |  |
| WC13 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 1,42 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY14 | podejście: umywalka z baterią | podejscie | 40 | PP-HT 40 | 3,21 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_1.07 | podejście zbiorcze w pom. 1.07 → pion K2 | podejscie_zbiorcze | 100 | PP-HT 110 | 3,21 | 3,1 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| PRA15 | podejście: pralka automatyczna (≤ 12 kg) | podejscie | 50 | PP-HT 50 | 0,57 | 1,5 | 1,50 | 2,0 | — | — | — |  |
| SUS16 | podejście: suszarka kondensacyjna z odprowadzeniem skroplin | podejscie | 40 | PP-HT 40 | 1,22 | 0,0 | 0,00 | 2,0 | — | — | — |  |
| ZLE17 | podejście: zlewozmywak z baterią | podejscie | 50 | PP-HT 50 | 2,52 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| PZ_1.08 | podejście zbiorcze w pom. 1.08 → pion K2 | podejscie_zbiorcze | 70 | PP-HT 75 | 2,52 | 2,3 | 1,50 | 2,0 | — | — | 1,50 | nieodpowietrzane (tabl. 5) |
| ZLE06 | podejście: zlewozmywak z baterią | podejscie | 50 | PP-HT 50 | 7,10 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| ZMY07 | podejście: zmywarka do naczyń | podejscie | 50 | PP-HT 50 | 6,40 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| PZ_0.06 | podejście zbiorcze w pom. 0.06 → pion K3 | podejscie_zbiorcze | 70 | PP-HT 75 | 7,10 | 1,6 | 0,80 | 2,0 | — | — | 2,25 | odpowietrzane (tabl. 7) — L > 4 m lub Q > Q_max: zawór napowietrzający na końcu podejścia |
| ZLE08 | podejście: zlewozmywak z baterią | podejscie | 50 | PP-HT 50 | 0,57 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| WPU23 | podejście: wpust podłogowy dn50 | podejscie | 50 | PP-HT 50 | 2,30 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| PZ_0.12 | podejście zbiorcze w pom. 0.12 → pion K3 | podejscie_zbiorcze | 50 | PP-HT 50 | 2,30 | 1,6 | 0,80 | 2,0 | — | — | 0,80 | nieodpowietrzane (tabl. 5) |
| PION_K1 | pion K1 (P0, P1, P2) | pion | 100 | PP-HT 110 | 7,90 | 9,5 | 2,00 | — | — | — | 4,00 | wentylacja główna, trójniki proste (tabl. 11) |
| PION_K2 | pion K2 (P0, P1) | pion | 100 | PP-HT 110 | 4,75 | 7,9 | 2,00 | — | — | — | 4,00 | wentylacja główna, trójniki proste (tabl. 11) |
| PION_K3 | pion K3 (P0) | pion | 70 | PP-HT 75 | 1,60 | 3,2 | 0,89 | — | — | — | 1,50 | wentylacja główna, trójniki proste (tabl. 11) |
| KOL1 | przewód odpływowy pod posadzką: pion K3 → włączenie pionu K2 | poziom | 100 | PVC-U SN8 110 | 15,22 | 3,2 | 0,89 | 2,0 | 0,22 | 0,66 | 4,35 |  |
| KOL2 | przewód odpływowy pod posadzką: pion K2 → włączenie pionu K1 | poziom | 100 | PVC-U SN8 110 | 6,45 | 11,1 | 2,00 | 2,0 | 0,33 | 0,84 | 4,35 |  |
| KOL3 | przewód odpływowy pod posadzką: pion K1 → wyjście z budynku | poziom | 100 | PVC-U SN8 110 | 3,02 | 20,6 | 2,27 | 2,0 | 0,35 | 0,87 | 4,35 |  |
| PRZ | przykanalik: budynek → studzienka rewizyjna | przykanalik | 150 | PVC-U SN8 160 | 3,05 | 20,6 | 2,27 | 2,0 | 0,21 | 0,83 | 19,75 | min. DN150 (praktyka gestorów) [ZAŁ] |

### 3.1 Piony

* Pion K1: przepływ ścieków: Q_ww = K·√ΣDU (≥ DU_max) = 0,5·√9,5 = 1,54; DU_max = 2,0 = **2,00** l/s — _PN-EN 12056-2 wzór (1), tabl. 2–3_
* Pion K2: przepływ ścieków: Q_ww = K·√ΣDU (≥ DU_max) = 0,5·√7,9 = 1,41; DU_max = 2,0 = **2,00** l/s — _PN-EN 12056-2 wzór (1), tabl. 2–3_
* Pion K3: przepływ ścieków: Q_ww = K·√ΣDU (≥ DU_max) = 0,5·√3,2 = 0,89; DU_max = 0,8 = **0,89** l/s — _PN-EN 12056-2 wzór (1), tabl. 2–3_

### 3.2 Przykanalik i studzienka

* Suma równoważników odpływu budynku: ΣDU = 2,0 + 0,5 + 0,6 + 2,0 + 0,5 + 0,8 + 0,8 + 0,8 + 0,8 + 2,0 + 0,5 + 0,6 + 2,0 + 0,5 + 1,5 + 0,0 + 0,8 + 0,6 + 2,0 + 0,5 + 0,8 = **20,6** l/s
* Przepływ ścieków w przykanaliku: Q_ww = K·√ΣDU = 0,5·√20,6 = **2,27** l/s — _PN-EN 12056-2 p. 6.2_
* Napełnienie DN150 (d_w = 150,6 mm) przy i = 2,0 %: Q(h/d) z Colebrooka–White'a = **0,210** — _k_b = 1,0 mm_
* Prędkość przy Q_ww: v = **0,83** m/s
* Rzędna dna przykanalika przy studzience: z_st = z_E − i·L = −1,482 − 0,020·3,05 = **−1,543** m
* Przykrycie przykanalika przy studzience: h = z_ter − (z_st + d) = −0,376 − (−1,543 + 0,151) = **1,02** m

* Studzienka: studzienka rewizyjna z tworzywa PP DN425 z kinetą przelotową, właz żeliwny B125 [ZAŁ]; położenie (układ budynku) 5,40; 11,10; teren −0,38 m, dno −1,54 m (względne), głębokość 1,17 m; odległość od granicy działki 6,20 m.
* Rewizje: czyszczaki u podstawy każdego pionu (≈ 0,5 m nad posadzką) i przy zmianach kierunku przewodów pod posadzką; przejście przez ścianę fundamentową w tulei ochronnej, gazoszczelne (WT §234 ust. 4, W-214).

| Punkt | Rzędna dna [m, wzgl. ±0,00] |
|:---|---:|
| pion K3 | −0,988 |
| pion K2 | −1,293 |
| pion K1 | −1,422 |
| wyjście z budynku | −1,482 |
| studzienka (dno wlotu) | −1,543 |

## 4. Wentylacja pionów (WT §125)

| Pion | DN | Q_ww [l/s] | Zakończenie | Uzasadnienie | Dach [m] | Wylot [m] | Okna < 4 m | Q_a zaworu ≥ [l/s] |
|:---|---:|---:|:---|:---|---:|---:|:---|---:|
| K1 | 100 | 2,00 | wywiewka ponad dach | co piąty pion | 9,53 | 10,03 | O0-13 (↑2,20), O1-03 (↑5,35), O2-06 (↑8,50), O2-07 (↑8,70) | 16,0 |
| K2 | 100 | 2,00 | zawór napowietrzający PN-EN 12380 (dozwolony) | pion pośredni | 6,41 | — | O0-09 (↑2,40), O0-10 (↑2,40), O1-04 (↑5,35), O2-07 (↑8,70) | 16,0 |
| K3 | 70 | 0,89 | wywiewka ponad dach | ostatni pion na przewodzie odpływowym | 3,31 | 3,81 | O0-08 (↑2,10) | 7,2 |

* Wywiewki: wylot ≥ 0,5 m nad pokryciem [ZAŁ], ≥ 6 m od czerpni dachowej (WT §152 ust. 4) i ≥ 8 m od czerpni terenowej/ściennej (§152 ust. 3); nie włączać do kanałów wentylacyjnych (§125 ust. 3).
* Zawory napowietrzające (PN-EN 12380) w miejscu dostępnym, wentylowanym, powyżej najwyższego podejścia; przepływ nominalny Q_a ≥ 8·Q_ww (pion), 1–2·Q_ww (podejście) [W].

## 5. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-138 | Podejście zbiorcze 0.09: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 0.09: długość | 3,43 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 1.05: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 1.05: długość | 3,14 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 2.04: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 2.04: długość | 3,14 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 0.03: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 0.03: długość | 2,01 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 1.07: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 1.07: długość | 3,21 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 1.08: Q_ww ≤ Q_max(DN70) | 1,50 l/s | ≤ 1,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 1.08: długość | 2,52 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 0.06: Q_ww ≤ Q_max(DN70) | 0,80 l/s | ≤ 2,25 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 7 |
| W-138 | Podejście zbiorcze 0.12: Q_ww ≤ Q_max(DN50) | 0,80 l/s | ≤ 0,80 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 0.12: długość | 2,30 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Pion K1: Q_ww ≤ Q_max(DN100, wentylacja główna) | 2,00 l/s | ≤ 4,00 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 11 [NZW] |
| W-138 | Pion K1 z miską ustępową: średnica | 100 DN | ≥ 100 DN | SPEŁNIONY | PN-EN 12056-2; R6-58 |
| W-138 | Pion K2: Q_ww ≤ Q_max(DN100, wentylacja główna) | 2,00 l/s | ≤ 4,00 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 11 [NZW] |
| W-138 | Pion K2 z miską ustępową: średnica | 100 DN | ≥ 100 DN | SPEŁNIONY | PN-EN 12056-2; R6-58 |
| W-138 | Pion K3: Q_ww ≤ Q_max(DN70, wentylacja główna) | 0,89 l/s | ≤ 1,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 11 [NZW] |
| W-138 | KOL1: napełnienie h/d | 0,22 | ≤ 0,50 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.1) |
| W-138 | KOL2: napełnienie h/d | 0,33 | ≤ 0,50 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.1) |
| W-138 | KOL3: napełnienie h/d | 0,35 | ≤ 0,50 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.1) |
| W-138 | Przykanalik: napełnienie h/d | 0,21 | ≤ 0,70 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.2) |
| W-138 | Przykanalik: prędkość przy Q_ww (samooczyszczanie) | 0,83 m/s | ≥ 0,70 m/s | SPEŁNIONY | praktyka [ZAŁ] — informacyjnie przy małych Q (spłukiwanie miską ustępową) |
| W-141 | Przykrycie przykanalika przy budynku (ochrona przed przemarzaniem) | 1,00 m | ≥ 1,00 m | SPEŁNIONY | h_z = 0,80 m + 0,2 m (geotechnika.h_z) [ZAŁ] |
| W-141 | Przykrycie przykanalika przy studzience (ochrona przed przemarzaniem) | 1,02 m | ≥ 1,00 m | SPEŁNIONY | h_z = 0,80 m + 0,2 m (geotechnika.h_z) [ZAŁ] |
| W-138 | Grawitacyjne połączenie: dno studzienki ≥ dno kanału sieciowego + 0,10 m | −1,54 m | ≥ −2,48 m | SPEŁNIONY | rzędna dna kanału [ZAŁ — mapa do celów projektowych / warunki gestora] |
| W-140 | Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy) | 0,00 m | > −0,31 m | SPEŁNIONY | WT §124; PN-EN 12056-1 — inaczej zamknięcie przeciwzalewowe PN-EN 13564-1 lub przepompownia PN-EN 12056-4 |
| W-139 | Wywiewka pionu K1: wylot powyżej górnej krawędzi okien/drzwi w odl. < 4 m | 10,03 m | > 8,70 m | SPEŁNIONY | WT §125 ust. 1; okna: O0-13, O1-03, O2-06, O2-07 |
| W-166 | Wywiewka K1 — odległość od czerpni | 7,96 m | ≥ 6,00 m | SPEŁNIONY | WT §152 ust. 4 (czerpnia dachowa) / ust. 3 (8 m — terenowa) |
| W-139 | Wywiewka pionu K3: wylot powyżej górnej krawędzi okien/drzwi w odl. < 4 m | 3,81 m | > 2,10 m | SPEŁNIONY | WT §125 ust. 1; okna: O0-08 |
| W-166 | Wywiewka K3 — odległość od czerpni | 6,59 m | ≥ 6,00 m | SPEŁNIONY | WT §152 ust. 4 (czerpnia dachowa) / ust. 3 (8 m — terenowa) |

## Podsumowanie sprawdzeń

Warunków: 33; spełnionych: 33; niespełnionych: 0; informacyjnych: 0.

## Źródła

1. WT §122–125, §152, §234, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.) — art. 102a PB
2. PN-EN 12056-2:2002 — tabl. 2, 3, 5–7, 11, zał. B (wartości wg kalkulatorprojektanta.pl, instsani.pl — [NZW])
3. Rejestr R6: R6-55…R6-59, §3.7; rejestr wymagań W-138…W-141
