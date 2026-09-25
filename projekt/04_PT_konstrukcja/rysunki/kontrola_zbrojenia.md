# Kontrola zbrojenia rysunków PT-BO — A_s,prov ≥ max(A_s,req; A_s,min)

Plik generowany automatycznie przez `lamela.views.konstrukcja` (moduł `konstrukcja_dane.rejestruj`) przy rysowaniu arkuszy. A_s,req, A_s,min — z obiektów wyników biblioteki `lamela.obliczenia.konstrukcja` (pozycje obliczeń statycznych); A_s,prov — zbrojenie NARYSOWANE na arkuszach (φ/s lub n·φ). Warunki: PN-EN 1992-1-1 6.1, 9.2.1.1(1) (9.1N) + NA, 9.2.1.1(3) (A_s,max = 0,04·A_c), 9.3.1.1(3) (s_max).

**Wynik: 43/45 pozycji spełnia warunek A_s,prov ≥ A_s,req** (2 niespełnionych — kolumna „Uwagi”).

| Element | Miejsce | Poz. obl. | A_s,req | A_s,min | A_s,prov | Jedn. | Zbrojenie | Zapas | Wynik | Arkusze | Uwagi |
|---|---|---|---:|---:|---:|---|---|---:|---|---|---|
| PF1+PF2 | dozbrojenie D1 dół x | MES-PF | 2583 | 0 | 3121 | mm²/m | Ø14 co 15 + Ø20 co 15 | +21% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D1 dół y | MES-PF | 5243 | 0 | 4299 | mm²/m | Ø14 co 15 + Ø25 co 15 | -18% | ✗ | PT-BO-03 | wymagane zbrojenie niewykonalne w grubości płyty (rozstaw w świetle 8.2(2)) — obciążenie skupione węzła ścian/belek: pogrubienie płyty (stopa) pod węzłem — REKOMENDACJE_MODEL.md [WYMAGA ZMIANY MODELU] |
| PF1+PF2 | dozbrojenie D2 dół x | MES-PF | 1263 | 0 | 1361 | mm²/m | Ø14 co 15 + Ø8 co 15 | +8% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D2 dół y | MES-PF | 1474 | 0 | 1550 | mm²/m | Ø14 co 15 + Ø10 co 15 | +5% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D3 dół x | MES-PF | 1272 | 0 | 1361 | mm²/m | Ø14 co 15 + Ø8 co 15 | +7% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D3 dół y | MES-PF | 2556 | 0 | 3121 | mm²/m | Ø14 co 15 + Ø20 co 15 | +22% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D4 dół x | MES-PF | 1086 | 0 | 1361 | mm²/m | Ø14 co 15 + Ø8 co 15 | +25% | ✓ | PT-BO-03 |  |
| PF1+PF2 | dozbrojenie D4 dół y | MES-PF | 1456 | 0 | 1550 | mm²/m | Ø14 co 15 + Ø10 co 15 | +6% | ✓ | PT-BO-03 |  |
| PF1+PF2 | siatka dolna x (MES, poza dozbrojeniami) | MES-PF | 1019 | 246 | 1026 | mm²/m | Ø14 co 15 | +1% | ✓ | PT-BO-03 |  |
| PF1+PF2 | siatka dolna y (MES, poza dozbrojeniami) | MES-PF | 1020 | 246 | 1026 | mm²/m | Ø14 co 15 | +1% | ✓ | PT-BO-03 |  |
| PF1+PF2 | strefa S1 (płyta) — podwójnie zbrojona, najniekorz. el. (dół y) | MES-PF | 5243 | 0 | 4299 | mm²/m | siatka + dozbr./żebro | -18% | ✗ | PT-BO-03 | zbrojenie wymagane niewykonalne w grubości płyty — pogrubienie (stopa) pod węzłem, REKOMENDACJE_MODEL.md [WYMAGA ZMIANY MODELU]; A_s2,max = 1829 mm²/m; A_s1 + A_s2 = 7072 ≤ A_s,max = 10000 mm²/m; płyta: pręty ściskane usztywnione siatką poprzeczną s = 7.5 cm ≤ 15φ [ZAŁ] |
| SF1 | pogrubienie — siatka dolna (MES) | 10.20 | 1534 | 538 | 1539 | mm²/m | Ø14 co 10 | +0% | ✓ | PT-BO-03 |  |
| SF2 | pogrubienie — siatka dolna (MES) | 10.21 | 1931 | 538 | 1964 | mm²/m | Ø20 co 16 | +2% | ✓ | PT-BO-03 |  |
| SF3 | pogrubienie — siatka dolna (MES) | 10.22 | 899 | 538 | 905 | mm²/m | Ø12 co 12.5 | +1% | ✓ | PT-BO-03 |  |
| SF4 | pogrubienie — siatka dolna (MES) | 10.23 | 789 | 538 | 789 | mm²/m | Ø14 co 19.5 | +0% | ✓ | PT-BO-03 |  |
| ZF1 | żebro — dołem (MES: A_s,req·b) | 10.3 | 1249 | 0 | 1294 | mm² | 6Ø12 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF1 | żebro — górą (MES: A_s,req·b) | 10.3 | 5920 | 0 | 6140 | mm² | 10Ø25 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF10 | żebro — dołem (MES: A_s,req·b) | 10.12 | 800 | 0 | 852 | mm² | 3Ø12 + siatka | +6% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF10 | żebro — górą (MES: A_s,req·b) | 10.12 | 116 | 0 | 1252 | mm² | 2Ø12 + siatka | +979% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — dołem (MES: A_s,req·b) | 10.13 | 902 | 0 | 966 | mm² | 4Ø12 + siatka | +7% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — górą (MES: A_s,req·b) | 10.13 | 198 | 0 | 1252 | mm² | 2Ø12 + siatka | +532% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — dołem (MES: A_s,req·b) | 10.14 | 2618 | 0 | 2712 | mm² | 7Ø20 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — górą (MES: A_s,req·b) | 10.14 | 415 | 0 | 1252 | mm² | 2Ø12 + siatka | +202% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — dołem (MES: A_s,req·b) | 10.15 | 2376 | 0 | 2524 | mm² | 10Ø16 + siatka | +6% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — górą (MES: A_s,req·b) | 10.15 | 412 | 0 | 1252 | mm² | 2Ø12 + siatka | +204% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — dołem (MES: A_s,req·b) | 10.16 | 2189 | 0 | 2323 | mm² | 9Ø16 + siatka | +6% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — górą (MES: A_s,req·b) | 10.16 | 385 | 0 | 1252 | mm² | 2Ø12 + siatka | +225% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — dołem (MES: A_s,req·b) | 10.17 | 180 | 0 | 739 | mm² | 2Ø12 + siatka | +311% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — górą (MES: A_s,req·b) | 10.17 | 822 | 0 | 1252 | mm² | 2Ø12 + siatka | +52% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — dołem (MES: A_s,req·b) | 10.18 | 1012 | 0 | 1079 | mm² | 5Ø12 + siatka | +7% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — górą (MES: A_s,req·b) | 10.18 | 823 | 0 | 1252 | mm² | 2Ø12 + siatka | +52% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF17 | żebro — dołem (MES: A_s,req·b) | 10.19 | 694 | 0 | 739 | mm² | 2Ø12 + siatka | +7% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF17 | żebro — górą (MES: A_s,req·b) | 10.19 | 628 | 0 | 1252 | mm² | 2Ø12 + siatka | +99% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — dołem (MES: A_s,req·b) | 10.4 | 503 | 0 | 842 | mm² | 2Ø12 + siatka | +67% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — górą (MES: A_s,req·b) | 10.4 | 345 | 0 | 1458 | mm² | 2Ø12 + siatka | +322% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — dołem (MES: A_s,req·b) | 10.7 | 135 | 0 | 842 | mm² | 2Ø12 + siatka | +526% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — górą (MES: A_s,req·b) | 10.7 | 996 | 0 | 1458 | mm² | 2Ø12 + siatka | +46% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — dołem (MES: A_s,req·b) | 10.8 | 0 | 0 | 842 | mm² | 2Ø12 + siatka | — | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — górą (MES: A_s,req·b) | 10.8 | 452 | 0 | 1458 | mm² | 2Ø12 + siatka | +222% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF7 | żebro — dołem (MES: A_s,req·b) | 10.9 | 1736 | 0 | 1747 | mm² | 10Ø12 + siatka | +1% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF7 | żebro — górą (MES: A_s,req·b) | 10.9 | 1912 | 0 | 2023 | mm² | 7Ø12 + siatka | +6% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF8 | żebro — dołem (MES: A_s,req·b) | 10.10 | 1540 | 0 | 1634 | mm² | 9Ø12 + siatka | +6% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF8 | żebro — górą (MES: A_s,req·b) | 10.10 | 4192 | 0 | 4373 | mm² | 10Ø20 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF9 | żebro — dołem (MES: A_s,req·b) | 10.11 | 1417 | 0 | 1418 | mm² | 8Ø12 + siatka | +0% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF9 | żebro — górą (MES: A_s,req·b) | 10.11 | 2454 | 0 | 2635 | mm² | 8Ø16 + siatka | +7% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
