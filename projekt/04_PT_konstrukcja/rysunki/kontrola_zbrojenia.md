# Kontrola zbrojenia rysunków PT-BO — A_s,prov ≥ max(A_s,req; A_s,min)

Plik generowany automatycznie przez `lamela.views.konstrukcja` (moduł `konstrukcja_dane.rejestruj`) przy rysowaniu arkuszy. A_s,req, A_s,min — z obiektów wyników biblioteki `lamela.obliczenia.konstrukcja` (pozycje obliczeń statycznych); A_s,prov — zbrojenie NARYSOWANE na arkuszach (φ/s lub n·φ). Warunki: PN-EN 1992-1-1 6.1, 9.2.1.1(1) (9.1N) + NA, 9.2.1.1(3) (A_s,max = 0,04·A_c), 9.3.1.1(3) (s_max).

**Wynik: 51/52 pozycji spełnia warunek A_s,prov ≥ A_s,req** (1 niespełnionych — kolumna „Uwagi”).

| Element | Miejsce | Poz. obl. | A_s,req | A_s,min | A_s,prov | Jedn. | Zbrojenie | Zapas | Wynik | Arkusze | Uwagi |
|---|---|---|---:|---:|---:|---|---|---:|---|---|---|
| PF1 | dozbrojenie D1 dół x | MES-PF | 2734 | 0 | 3020 | mm²/m | Ø14 co 15.5 + Ø20 co 15.5 | +10% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D1 dół y | MES-PF | 3666 | 0 | 5047 | mm²/m | Ø14 co 15.5 + Ø20 co 7.75 | +38% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D1 góra y | MES-PF | 1690 | 0 | 1720 | mm²/m | Ø12 co 9.5 + Ø8 co 9.5 | +2% | ✓ | PT-BO-04 |  |
| PF1 | dozbrojenie D2 dół x | MES-PF | 1383 | 0 | 1500 | mm²/m | Ø14 co 15.5 + Ø10 co 15.5 | +8% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D2 dół y | MES-PF | 1126 | 0 | 1317 | mm²/m | Ø14 co 15.5 + Ø8 co 15.5 | +17% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D3 dół x | MES-PF | 1005 | 0 | 1317 | mm²/m | Ø14 co 15.5 + Ø8 co 15.5 | +31% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D3 dół y | MES-PF | 1958 | 0 | 1986 | mm²/m | Ø14 co 15.5 + Ø14 co 15.5 | +1% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D4 dół x | MES-PF | 1151 | 0 | 1317 | mm²/m | Ø14 co 15.5 + Ø8 co 15.5 | +14% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D4 dół y | MES-PF | 1445 | 0 | 1500 | mm²/m | Ø14 co 15.5 + Ø10 co 15.5 | +4% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D5 dół x | MES-PF | 1247 | 0 | 1317 | mm²/m | Ø14 co 15.5 + Ø8 co 15.5 | +6% | ✓ | PT-BO-03 |  |
| PF1 | dozbrojenie D6 dół x | MES-PF | 1017 | 0 | 1317 | mm²/m | Ø14 co 15.5 + Ø8 co 15.5 | +30% | ✓ | PT-BO-03 |  |
| PF1 | siatka dolna x (MES, poza dozbrojeniami) | MES-PF | 990 | 246 | 993 | mm²/m | Ø14 co 15.5 | +0% | ✓ | PT-BO-03 |  |
| PF1 | siatka dolna y (MES, poza dozbrojeniami) | MES-PF | 984 | 246 | 993 | mm²/m | Ø14 co 15.5 | +1% | ✓ | PT-BO-03 |  |
| PF1 | siatka górna x (MES, poza dozbrojeniami) | MES-PF | 1043 | 246 | 1190 | mm²/m | Ø12 co 9.5 | +14% | ✓ | PT-BO-04 |  |
| PF1 | siatka górna y (MES, poza dozbrojeniami) | MES-PF | 1187 | 246 | 1190 | mm²/m | Ø12 co 9.5 | +0% | ✓ | PT-BO-04 |  |
| PF1 | strefa S1 (płyta) — przekrój niewystarczający | MES-PF | 1 | 0 | 0 | — | — | -100% | ✗ | PT-BO-03 | M_Ed = 254 kNm/m > M_lim — wymagana wysokość h ≥ 0.26 m (obecnie 0.25 m) [WYMAGA ZMIANY MODELU] |
| SF1 | pogrubienie — siatka dolna (MES) | 10.18 | 324 | 538 | 539 | mm²/m | Ø12 co 21 | +0% | ✓ | PT-BO-03 |  |
| SF2 | pogrubienie — siatka dolna (MES) | 10.19 | 573 | 538 | 580 | mm²/m | Ø12 co 19.5 | +1% | ✓ | PT-BO-03 |  |
| SF3 | pogrubienie — siatka dolna (MES) | 10.20 | 360 | 538 | 539 | mm²/m | Ø12 co 21 | +0% | ✓ | PT-BO-03 |  |
| SF4 | pogrubienie — siatka dolna (MES) | 10.21 | 714 | 538 | 716 | mm²/m | Ø14 co 21.5 | +0% | ✓ | PT-BO-03 |  |
| ZF1 | żebro — dołem (MES: A_s,req·b) | 10.2 | 848 | 0 | 935 | mm² | 3Ø12 + siatka | +10% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF1 | żebro — górą (MES: A_s,req·b) | 10.2 | 1152 | 0 | 1167 | mm² | 4Ø12 + siatka | +1% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF10 | żebro — dołem (MES: A_s,req·b) | 10.11 | 1126 | 0 | 1175 | mm² | 6Ø12 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF10 | żebro — górą (MES: A_s,req·b) | 10.11 | 150 | 0 | 821 | mm² | 2Ø12 + siatka | +446% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — dołem (MES: A_s,req·b) | 10.12 | 1899 | 0 | 1904 | mm² | 7Ø16 + siatka | +0% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF11 | żebro — górą (MES: A_s,req·b) | 10.12 | 251 | 0 | 821 | mm² | 2Ø12 + siatka | +228% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — dołem (MES: A_s,req·b) | 10.13 | 1896 | 0 | 1904 | mm² | 7Ø16 + siatka | +0% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF12 | żebro — górą (MES: A_s,req·b) | 10.13 | 288 | 0 | 821 | mm² | 2Ø12 + siatka | +186% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — dołem (MES: A_s,req·b) | 10.14 | 2249 | 0 | 2306 | mm² | 9Ø16 + siatka | +2% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF13 | żebro — górą (MES: A_s,req·b) | 10.14 | 371 | 0 | 821 | mm² | 2Ø12 + siatka | +121% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — dołem (MES: A_s,req·b) | 10.15 | 170 | 0 | 723 | mm² | 2Ø12 + siatka | +325% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF14 | żebro — górą (MES: A_s,req·b) | 10.15 | 721 | 0 | 821 | mm² | 2Ø12 + siatka | +14% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — dołem (MES: A_s,req·b) | 10.16 | 983 | 0 | 1062 | mm² | 5Ø12 + siatka | +8% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF15 | żebro — górą (MES: A_s,req·b) | 10.16 | 742 | 0 | 821 | mm² | 2Ø12 + siatka | +11% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — dołem (MES: A_s,req·b) | 10.17 | 749 | 0 | 836 | mm² | 3Ø12 + siatka | +12% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF16 | żebro — górą (MES: A_s,req·b) | 10.17 | 569 | 0 | 821 | mm² | 2Ø12 + siatka | +44% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — dołem (MES: A_s,req·b) | 10.3 | 435 | 0 | 822 | mm² | 2Ø12 + siatka | +89% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF2 | żebro — górą (MES: A_s,req·b) | 10.3 | 339 | 0 | 940 | mm² | 2Ø12 + siatka | +177% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF3 | żebro — dołem (MES: A_s,req·b) | 10.4 | 37 | 0 | 822 | mm² | 2Ø12 + siatka | +2113% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF3 | żebro — górą (MES: A_s,req·b) | 10.4 | 322 | 0 | 940 | mm² | 2Ø12 + siatka | +192% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF4 | żebro — dołem (MES: A_s,req·b) | 10.5 | 100 | 0 | 822 | mm² | 2Ø12 + siatka | +719% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF4 | żebro — górą (MES: A_s,req·b) | 10.5 | 1030 | 0 | 1054 | mm² | 3Ø12 + siatka | +2% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — dołem (MES: A_s,req·b) | 10.6 | 3 | 0 | 822 | mm² | 2Ø12 + siatka | +25272% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF5 | żebro — górą (MES: A_s,req·b) | 10.6 | 419 | 0 | 940 | mm² | 2Ø12 + siatka | +124% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — dołem (MES: A_s,req·b) | 10.7 | 1767 | 0 | 1840 | mm² | 11Ø12 + siatka | +4% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF6 | żebro — górą (MES: A_s,req·b) | 10.7 | 921 | 0 | 940 | mm² | 2Ø12 + siatka | +2% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF7 | żebro — dołem (MES: A_s,req·b) | 10.8 | 861 | 0 | 935 | mm² | 3Ø12 + siatka | +9% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF7 | żebro — górą (MES: A_s,req·b) | 10.8 | 1546 | 0 | 1619 | mm² | 8Ø12 + siatka | +5% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF8 | żebro — dołem (MES: A_s,req·b) | 10.9 | 1292 | 0 | 1401 | mm² | 8Ø12 + siatka | +8% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF8 | żebro — górą (MES: A_s,req·b) | 10.9 | 1238 | 0 | 1274 | mm² | 6Ø12 + siatka | +3% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF9 | żebro — dołem (MES: A_s,req·b) | 10.10 | 1194 | 0 | 1288 | mm² | 7Ø12 + siatka | +8% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
| ZF9 | żebro — górą (MES: A_s,req·b) | 10.10 | 56 | 0 | 821 | mm² | 2Ø12 + siatka | +1375% | ✓ | PT-BO-03 | warunki ław biblioteki (model ławy izolowanej) zastąpione MES płyty z żebrami |
