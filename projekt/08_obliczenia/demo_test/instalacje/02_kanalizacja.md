# Obliczenia instalacji kanalizacji sanitarnej

Obiekt: Dom testowy pipeline'u 3D. PN-EN 12056-2:2002, system I. Dane przykładowe oznaczono [ZAŁ].

## 1. Podstawy i założenia

* WT §122–125, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-138…W-140, W-118.
* PN-EN 12056-1…5:2002 (PL, aktualne); PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10.
* Tablice PN-EN 12056-2 (Q_max podejść i pionów) — wartości z literatury, oznaczone [NZW] (treść normy płatna; rejestr R6 Nierozstrz. 8). Przepustowość przewodów odpływowych liczona wzorem Colebrooka–White'a jak w zał. B normy.
* K = 0,5 — użytkowanie nieciągłe (budynek mieszkalny), PN-EN 12056-2 tabl. 3 (W-138).
* Rury: wewnątrz PP-HT (PN-EN 1451-1), pod posadzką i przykanalik PVC-U SN8 lity (PN-EN 1401-1+A1:2023-09) [ZAŁ].
* Spadki: podejścia 2,0 %, przewody pod posadzką 2,0 % (≤ DN100) / 1,5 % (> DN100), przykanalik 2,0 % [ZAŁ].
* Trasy: podejścia i przewody pod posadzką równoległe do ścian (odległość „miejska”) [UPR].
* Rzędne przewodów obniżono o 0,53 m względem założenia startowego (−0,65 m), aby zapewnić przykrycie przykanalika ≥ 1,00 m (strefa przemarzania).

## 2. Przybory i równoważniki odpływu

| Id | Przybór | Kond. | Pom. | DU [l/s] | Podejście |
|:---|:---|:---|:---|---:|:---|
| ZLE01 | Zlewozmywak z baterią | P0 | 0.04 | 0,8 | DN50 |
| ZMY02 | Zmywarka do naczyń | P0 | 0.04 | 0,8 | DN50 |
| WC03 | Miska ustępowa z płuczką zbiornikową 6 l | P0 | 0.02 | 2,0 | DN100 |
| UMY04 | Umywalka z baterią | P0 | 0.02 | 0,5 | DN40 |
| WC05 | Miska ustępowa z płuczką zbiornikową 6 l | P1 | 1.04 | 2,0 | DN100 |
| UMY06 | Umywalka z baterią | P1 | 1.04 | 0,5 | DN40 |
| PRY07 | Natrysk (odpływ liniowy/brodzik bez korka) z baterią | P1 | 1.04 | 0,6 | DN50 |
| PRA08 | Pralka automatyczna (≤ 12 kg) | P1 | 1.04 | 1,5 | DN50 |

## 3. Przewody

| Odcinek | Opis | Rodzaj | DN | Rura | L [m] | ΣDU [l/s] | Q_ww [l/s] | i [%] | h/d | v [m/s] | Q_max [l/s] | Uwagi |
|:---|:---|:---|---:|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| WC03 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 0,30 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY04 | podejście: umywalka z baterią | podejscie | 40 | PP-HT 40 | 0,91 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PZ_0.02 | podejście zbiorcze w pom. 0.02 → pion P1 | podejscie_zbiorcze | 100 | PP-HT 110 | 0,91 | 2,5 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| ZLE01 | podejście: zlewozmywak z baterią | podejscie | 50 | PP-HT 50 | 2,59 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| ZMY02 | podejście: zmywarka do naczyń | podejscie | 50 | PP-HT 50 | 1,88 | 0,8 | 0,80 | 2,0 | — | — | — |  |
| PZ_0.04 | podejście zbiorcze w pom. 0.04 → pion P2 | podejscie_zbiorcze | 50 | PP-HT 50 | 2,59 | 1,6 | 0,80 | 2,0 | — | — | 0,80 | nieodpowietrzane (tabl. 5) |
| WC05 | podejście: miska ustępowa z płuczką zbiornikową 6 l | podejscie | 100 | PP-HT 110 | 0,30 | 2,0 | 2,00 | 2,0 | — | — | — |  |
| UMY06 | podejście: umywalka z baterią | podejscie | 40 | PP-HT 40 | 2,19 | 0,5 | 0,50 | 2,0 | — | — | — |  |
| PRY07 | podejście: natrysk (odpływ liniowy/brodzik bez korka) z baterią | podejscie | 50 | PP-HT 50 | 3,02 | 0,6 | 0,60 | 2,0 | — | — | — |  |
| PRA08 | podejście: pralka automatyczna (≤ 12 kg) | podejscie | 50 | PP-HT 50 | 1,80 | 1,5 | 1,50 | 2,0 | — | — | — |  |
| PZ_1.04 | podejście zbiorcze w pom. 1.04 → pion P2 | podejscie_zbiorcze | 100 | PP-HT 110 | 3,02 | 4,6 | 2,00 | 2,0 | — | — | 2,50 | nieodpowietrzane (tabl. 5) |
| PION_P1 | pion P1 (P0) | pion | 100 | PP-HT 110 | 1,60 | 2,5 | 2,00 | — | — | — | 4,00 | wentylacja główna, trójniki proste (tabl. 11) |
| PION_P2 | pion P2 (P0, P1) | pion | 100 | PP-HT 110 | 4,66 | 6,2 | 2,00 | — | — | — | 4,00 | wentylacja główna, trójniki proste (tabl. 11) |
| KOL1 | przewód odpływowy pod posadzką: pion P1 → włączenie pionu P2 | poziom | 100 | PVC-U SN8 110 | 6,20 | 2,5 | 2,00 | 2,0 | 0,33 | 0,84 | 4,35 |  |
| KOL2 | przewód odpływowy pod posadzką: pion P2 → wyjście z budynku | poziom | 100 | PVC-U SN8 110 | 4,19 | 8,7 | 2,00 | 2,0 | 0,33 | 0,84 | 4,35 |  |
| PRZ | przykanalik: budynek → studzienka rewizyjna | przykanalik | 150 | PVC-U SN8 160 | 9,20 | 8,7 | 2,00 | 2,0 | 0,20 | 0,80 | 19,75 | min. DN150 (praktyka gestorów) [ZAŁ] |

### 3.1 Piony

* Pion P1: przepływ ścieków: Q_ww = K·√ΣDU (≥ DU_max) = 0,5·√2,5 = 0,79; DU_max = 2,0 = **2,00** l/s — _PN-EN 12056-2 wzór (1), tabl. 2–3_
* Pion P2: przepływ ścieków: Q_ww = K·√ΣDU (≥ DU_max) = 0,5·√6,2 = 1,24; DU_max = 2,0 = **2,00** l/s — _PN-EN 12056-2 wzór (1), tabl. 2–3_

### 3.2 Przykanalik i studzienka

* Suma równoważników odpływu budynku: ΣDU = 0,8 + 0,8 + 2,0 + 0,5 + 2,0 + 0,5 + 0,6 + 1,5 = **8,7** l/s
* Przepływ ścieków w przykanaliku: Q_ww = K·√ΣDU = 0,5·√8,7 = **2,00** l/s — _PN-EN 12056-2 p. 6.2_
* Napełnienie DN150 (d_w = 150,6 mm) przy i = 2,0 %: Q(h/d) z Colebrooka–White'a = **0,197** — _k_b = 1,0 mm_
* Prędkość przy Q_ww: v = **0,80** m/s
* Rzędna dna przykanalika przy studzience: z_st = z_E − i·L = −1,391 − 0,020·9,20 = **−1,575** m
* Przykrycie przykanalika przy studzience: h = z_ter − (z_st + d) = −0,183 − (−1,575 + 0,151) = **1,24** m

* Studzienka: studzienka rewizyjna z tworzywa PP DN425 z kinetą przelotową, właz żeliwny B125 [ZAŁ]; położenie (układ budynku) 7,00; 16,50; teren −0,18 m, dno −1,58 m (względne), głębokość 1,39 m; odległość od granicy działki 1,50 m.
* Rewizje: czyszczaki u podstawy każdego pionu (≈ 0,5 m nad posadzką) i przy zmianach kierunku przewodów pod posadzką; przejście przez ścianę fundamentową w tulei ochronnej, gazoszczelne (WT §234 ust. 4, W-214).

| Punkt | Rzędna dna [m, wzgl. ±0,00] |
|:---|---:|
| pion P1 | −1,183 |
| pion P2 | −1,307 |
| wyjście z budynku | −1,391 |
| studzienka (dno wlotu) | −1,575 |

## 4. Wentylacja pionów (WT §125)

| Pion | DN | Q_ww [l/s] | Zakończenie | Uzasadnienie | Dach [m] | Wylot [m] | Okna < 4 m | Q_a zaworu ≥ [l/s] |
|:---|---:|---:|:---|:---|---:|---:|:---|---:|
| P1 | 100 | 2,00 | wywiewka ponad dach | ostatni pion na przewodzie odpływowym | 6,19 | 6,69 | O0-03 (↑2,30), O0-04 (↑2,20), O1-04 (↑5,36), O1-05 (↑5,46), O1-06 (↑5,46) | 16,0 |
| P2 | 100 | 2,00 | zawór napowietrzający PN-EN 12380 (dozwolony) | pion pośredni | 6,19 | — | O0-04 (↑2,20), O0-05 (↑2,40), O0-08 (↑2,10), O1-03 (↑5,36), O1-04 (↑5,36), O1-05 (↑5,46) | 16,0 |

* Wywiewki: wylot ≥ 0,5 m nad pokryciem [ZAŁ], ≥ 6 m od czerpni dachowej (WT §152 ust. 4) i ≥ 8 m od czerpni terenowej/ściennej (§152 ust. 3); nie włączać do kanałów wentylacyjnych (§125 ust. 3).
* Zawory napowietrzające (PN-EN 12380) w miejscu dostępnym, wentylowanym, powyżej najwyższego podejścia; przepływ nominalny Q_a ≥ 8·Q_ww (pion), 1–2·Q_ww (podejście) [W].

## 5. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-138 | Podejście zbiorcze 0.02: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 0.02: długość | 0,91 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 0.04: Q_ww ≤ Q_max(DN50) | 0,80 l/s | ≤ 0,80 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 0.04: długość | 2,59 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Podejście zbiorcze 1.04: Q_ww ≤ Q_max(DN100) | 2,00 l/s | ≤ 2,50 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 5 |
| W-138 | Podejście nieodpowietrzane 1.04: długość | 3,02 m | ≤ 4,00 m | SPEŁNIONY | PN-EN 12056-2 tabl. 6 [NZW] |
| W-138 | Pion P1: Q_ww ≤ Q_max(DN100, wentylacja główna) | 2,00 l/s | ≤ 4,00 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 11 [NZW] |
| W-138 | Pion P1 z miską ustępową: średnica | 100 DN | ≥ 100 DN | SPEŁNIONY | PN-EN 12056-2; R6-58 |
| W-138 | Pion P2: Q_ww ≤ Q_max(DN100, wentylacja główna) | 2,00 l/s | ≤ 4,00 l/s | SPEŁNIONY | PN-EN 12056-2 tabl. 11 [NZW] |
| W-138 | Pion P2 z miską ustępową: średnica | 100 DN | ≥ 100 DN | SPEŁNIONY | PN-EN 12056-2; R6-58 |
| W-138 | KOL1: napełnienie h/d | 0,33 | ≤ 0,50 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.1) |
| W-138 | KOL2: napełnienie h/d | 0,33 | ≤ 0,50 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.1) |
| W-138 | Przykanalik: napełnienie h/d | 0,20 | ≤ 0,70 | SPEŁNIONY | PN-EN 12056-2 zał. B (tabl. B.2) |
| W-138 | Przykanalik: prędkość przy Q_ww (samooczyszczanie) | 0,80 m/s | ≥ 0,70 m/s | SPEŁNIONY | praktyka [ZAŁ] — informacyjnie przy małych Q (spłukiwanie miską ustępową) |
| W-141 | Przykrycie przykanalika przy budynku (ochrona przed przemarzaniem) | 1,00 m | ≥ 1,00 m | SPEŁNIONY | h_z = 0,80 m + 0,2 m (geotechnika.h_z) [ZAŁ] |
| W-141 | Przykrycie przykanalika przy studzience (ochrona przed przemarzaniem) | 1,24 m | ≥ 1,00 m | SPEŁNIONY | h_z = 0,80 m + 0,2 m (geotechnika.h_z) [ZAŁ] |
| W-138 | Grawitacyjne połączenie: dno studzienki ≥ dno kanału sieciowego + 0,10 m | −1,58 m | ≥ −2,28 m | SPEŁNIONY | rzędna dna kanału [ZAŁ — mapa do celów projektowych / warunki gestora] |
| W-140 | Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy) | 0,00 m | > −0,20 m | SPEŁNIONY | WT §124; PN-EN 12056-1 — inaczej zamknięcie przeciwzalewowe PN-EN 13564-1 lub przepompownia PN-EN 12056-4 |
| W-139 | Wywiewka pionu P1: wylot powyżej górnej krawędzi okien/drzwi w odl. < 4 m | 6,69 m | > 5,46 m | SPEŁNIONY | WT §125 ust. 1; okna: O0-03, O0-04, O1-04, O1-05, O1-06 |

## Podsumowanie sprawdzeń

Warunków: 19; spełnionych: 19; niespełnionych: 0; informacyjnych: 0.

## Źródła

1. WT §122–125, §152, §234, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.) — art. 102a PB
2. PN-EN 12056-2:2002 — tabl. 2, 3, 5–7, 11, zał. B (wartości wg kalkulatorprojektanta.pl, instsani.pl — [NZW])
3. Rejestr R6: R6-55…R6-59, §3.7; rejestr wymagań W-138…W-141
