# Kontrola zbrojenia rysunków PT-BO — A_s,prov ≥ max(A_s,req; A_s,min)

Plik generowany automatycznie przez `lamela.views.konstrukcja` (moduł `konstrukcja_dane.rejestruj`) przy rysowaniu arkuszy. A_s,req, A_s,min — z obiektów wyników biblioteki `lamela.obliczenia.konstrukcja` (pozycje obliczeń statycznych); A_s,prov — zbrojenie NARYSOWANE na arkuszach (φ/s lub n·φ). Warunki: PN-EN 1992-1-1 6.1, 9.2.1.1(1) (9.1N) + NA, 9.2.1.1(3) (A_s,max = 0,04·A_c), 9.3.1.1(3) (s_max).

**Wynik: 45/58 pozycji spełnia warunek A_s,prov ≥ A_s,req** (13 niespełnionych — kolumna „Uwagi”).

| Element | Miejsce | Poz. obl. | A_s,req | A_s,min | A_s,prov | Jedn. | Zbrojenie | Zapas | Wynik | Arkusze | Uwagi |
|---|---|---|---:|---:|---:|---|---|---:|---|---|---|
| PF1 | dozbrojenie D1 dół x | MES-PF | 3318 | 0 | 3553 | mm²/m | Ø16 co 14.5 + Ø20 co 14.5 | +7% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D1 dół y | MES-PF | 3466 | 0 | 3553 | mm²/m | Ø16 co 14.5 + Ø20 co 14.5 | +2% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D2 dół x | MES-PF | 1517 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +14% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D2 dół y | MES-PF | 1660 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +4% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D3 dół x | MES-PF | 1893 | 0 | 1928 | mm²/m | Ø16 co 14.5 + Ø10 co 14.5 | +2% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D3 dół y | MES-PF | 1645 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +5% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D4 dół x | MES-PF | 1636 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +6% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D4 dół y | MES-PF | 3669 | 0 | 5720 | mm²/m | Ø16 co 14.5 + Ø20 co 7.25 | +56% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D5 dół x | MES-PF | 1394 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +24% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D5 dół y | MES-PF | 3057 | 0 | 3553 | mm²/m | Ø16 co 14.5 + Ø20 co 14.5 | +16% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D6 dół x | MES-PF | 2473 | 0 | 2773 | mm²/m | Ø16 co 14.5 + Ø16 co 14.5 | +12% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D6 dół y | MES-PF | 1445 | 0 | 1733 | mm²/m | Ø16 co 14.5 + Ø8 co 14.5 | +20% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D7 dół x | MES-PF | 3916 | 0 | 5720 | mm²/m | Ø16 co 14.5 + Ø20 co 7.25 | +46% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D7 dół y | MES-PF | 3026 | 0 | 3553 | mm²/m | Ø16 co 14.5 + Ø20 co 14.5 | +17% | ✓ | PT-BO-05 |  |
| PF1 | dozbrojenie D8 dół y | MES-PF | 1796 | 0 | 1928 | mm²/m | Ø16 co 14.5 + Ø10 co 14.5 | +7% | ✓ | PT-BO-05 |  |
| PF1 | siatka dolna x (MES, poza dozbrojeniami) | MES-PF | 1378 | 246 | 1387 | mm²/m | Ø16 co 14.5 | +1% | ✓ | PT-BO-05 |  |
| PF1 | siatka dolna y (MES, poza dozbrojeniami) | MES-PF | 1377 | 246 | 1387 | mm²/m | Ø16 co 14.5 | +1% | ✓ | PT-BO-05 |  |
| PF1 | strefa S1 (ZF1) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-05 | M_Ed = 2295 kNm/m > M_lim — wymagana wysokość h ≥ 0.65 m (obecnie 0.55 m) [WYMAGA ZMIANY MODELU] |
| PF1 | strefa S2 (SF2, SF3, ZF1, ZF7, ZF8, płyta) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-05 | M_Ed = 4758 kNm/m > M_lim — wymagana wysokość h ≥ 0.91 m (obecnie 0.70 m) [WYMAGA ZMIANY MODELU] |
| PF1 | strefa S3 (płyta) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-05 | M_Ed = 234 kNm/m > M_lim — wymagana wysokość h ≥ 0.25 m (obecnie 0.25 m) [WYMAGA ZMIANY MODELU] |
| PF1 | strefa S4 (płyta) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-05 | M_Ed = 387 kNm/m > M_lim — wymagana wysokość h ≥ 0.30 m (obecnie 0.25 m) [WYMAGA ZMIANY MODELU] |
| PF1 | strefa S5 (płyta) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-05 | M_Ed = 278 kNm/m > M_lim — wymagana wysokość h ≥ 0.27 m (obecnie 0.25 m) [WYMAGA ZMIANY MODELU] |
| SF1 | pogrubienie — siatka dolna (MES) | 10.18 | 8118 | 538 | 539 | mm²/m | Ø12 co 21 | -93% | ✗ | PT-BO-05 | MES: A_s,req = 8119 mm²/m — nie do rozmieszczenia (φ ≤ 20, s ≥ 7 cm); przekrój pogrubienia niewystarczający [WYMAGA ZMIANY MODELU] |
| SF2 | pogrubienie — siatka dolna (MES) | 10.19 | 7155 | 538 | 539 | mm²/m | Ø12 co 21 | -92% | ✗ | PT-BO-05 | MES: A_s,req = 7155 mm²/m — nie do rozmieszczenia (φ ≤ 20, s ≥ 7 cm); przekrój pogrubienia niewystarczający [WYMAGA ZMIANY MODELU] |
| SF3 | pogrubienie — siatka dolna (MES) | 10.20 | 4069 | 538 | 4189 | mm²/m | Ø20 co 7.5 | +3% | ✓ | PT-BO-05 |  |
| SF4 | pogrubienie — siatka dolna (MES) | 10.21 | 2716 | 538 | 2732 | mm²/m | Ø20 co 11.5 | +1% | ✓ | PT-BO-05 |  |
| ZF1 | żebro — dołem (MES: A_s,req·b) | 10.2 | 4110 | 0 | 4288 | mm² | 11Ø20 + siatka | +4% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF1 | żebro — górą (MES: A_s,req·b) | 10.2 | 5581 | 0 | 5688 | mm² | 9Ø25 + siatka | +2% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF10 | żebro — dołem (MES: A_s,req·b) | 10.11 | 1060 | 0 | 1146 | mm² | 4Ø12 + siatka | +8% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF10 | żebro — górą (MES: A_s,req·b) | 10.11 | 244 | 0 | 1284 | mm² | 2Ø12 + siatka | +427% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — dołem (MES: A_s,req·b) | 10.12 | 3209 | 0 | 3521 | mm² | 9Ø20 + siatka | +10% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — górą (MES: A_s,req·b) | 10.12 | 659 | 0 | 1284 | mm² | 2Ø12 + siatka | +95% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — dołem (MES: A_s,req·b) | 10.13 | 2948 | 0 | 3207 | mm² | 8Ø20 + siatka | +9% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — górą (MES: A_s,req·b) | 10.13 | 546 | 0 | 1284 | mm² | 2Ø12 + siatka | +135% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — dołem (MES: A_s,req·b) | 10.14 | 2566 | 0 | 2704 | mm² | 10Ø16 + siatka | +5% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — górą (MES: A_s,req·b) | 10.14 | 476 | 0 | 1284 | mm² | 2Ø12 + siatka | +170% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — dołem (MES: A_s,req·b) | 10.15 | 219 | 0 | 920 | mm² | 2Ø12 + siatka | +320% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — górą (MES: A_s,req·b) | 10.15 | 1635 | 0 | 1737 | mm² | 6Ø12 + siatka | +6% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — dołem (MES: A_s,req·b) | 10.16 | 1170 | 0 | 1259 | mm² | 5Ø12 + siatka | +8% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — górą (MES: A_s,req·b) | 10.16 | 904 | 0 | 1284 | mm² | 2Ø12 + siatka | +42% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — dołem (MES: A_s,req·b) | 10.17 | 640 | 0 | 920 | mm² | 2Ø12 + siatka | +44% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — górą (MES: A_s,req·b) | 10.17 | 648 | 0 | 1284 | mm² | 2Ø12 + siatka | +98% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — dołem (MES: A_s,req·b) | 10.3 | 542 | 0 | 1058 | mm² | 2Ø12 + siatka | +95% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — górą (MES: A_s,req·b) | 10.3 | 914 | 0 | 1496 | mm² | 2Ø12 + siatka | +64% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF3 | żebro — dołem (MES: A_s,req·b) | 10.4 | 43 | 0 | 1058 | mm² | 2Ø12 + siatka | +2340% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF3 | żebro — górą (MES: A_s,req·b) | 10.4 | 265 | 0 | 1496 | mm² | 2Ø12 + siatka | +465% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF4 | żebro — dołem (MES: A_s,req·b) | 10.5 | 59 | 0 | 1058 | mm² | 2Ø12 + siatka | +1696% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF4 | żebro — górą (MES: A_s,req·b) | 10.5 | 1094 | 0 | 1496 | mm² | 2Ø12 + siatka | +37% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — dołem (MES: A_s,req·b) | 10.6 | 18 | 0 | 1058 | mm² | 2Ø12 + siatka | +5844% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — górą (MES: A_s,req·b) | 10.6 | 738 | 0 | 1496 | mm² | 2Ø12 + siatka | +103% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — dołem (MES: A_s,req·b) | 10.7 | 2346 | 0 | 2415 | mm² | 14Ø12 + siatka | +3% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — górą (MES: A_s,req·b) | 10.7 | 2447 | 0 | 2514 | mm² | 11Ø12 + siatka | +3% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF7 | żebro — dołem (MES: A_s,req·b) | 10.8 | 4011 | 0 | 4288 | mm² | 11Ø20 + siatka | +7% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF7 | żebro — górą (MES: A_s,req·b) | 10.8 | 5819 | 0 | 6179 | mm² | 10Ø25 + siatka | +6% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF8 | żebro — dołem (MES: A_s,req·b) | 10.9 | 2133 | 0 | 2302 | mm² | 8Ø16 + siatka | +8% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF8 | żebro — górą (MES: A_s,req·b) | 10.9 | 4085 | 0 | 4494 | mm² | 7Ø25 + siatka | +10% | ✗ | PT-BO-05 | w strefie żebra μ > μ_lim — pogłębić/poszerzyć żebro [WYMAGA ZMIANY MODELU] |
| ZF9 | żebro — dołem (MES: A_s,req·b) | 10.10 | 836 | 0 | 920 | mm² | 2Ø12 + siatka | +10% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF9 | żebro — górą (MES: A_s,req·b) | 10.10 | 143 | 0 | 1284 | mm² | 2Ø12 + siatka | +799% | ✓ | PT-BO-05 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
