# Walidacja solvera mostków 2D (`lamela.obliczenia.mostki2d`) — PN-EN ISO 10211:2017 zał. C

Metoda: objętości skończone na siatce prostokątnej zagęszczanej przy granicach materiałów, warunki Robina (h = 1/R_s), rozwiązanie bezpośrednie (scipy.sparse, SuperLU). Kryterium normy dla metody dokładnej 2D: temperatury ± 0,1 K, strumień ± 0,1 W/m.

| Przypadek | Wynik | max |Δθ| [K] | ΔΦ [W/m] | Tolerancja |
|---|---|---|---|---|
| ISO 10211 zał. C — przypadek 1 (28 punktów, tabela normy) | **SPEŁNIA** | 0,0481 | — | |Δθ| ≤ 0,1 K |
| ISO 10211 zał. C — przypadek 2 (punkty A…I + strumień) | **SPEŁNIA** | 0,0387 | −0,0097 | |Δθ| ≤ 0,1 K; |ΔΦ| ≤ 0,1 W/m |
| A1 — ściana warstwowa 1D (Robin), rozwiązanie dokładne | **SPEŁNIA** | 0,0000 | — | |Δθ| < 10⁻⁶ K; |ΔU| < 10⁻⁹ |
| A2 — przypadek 1 vs szereg Fouriera (bez zaokrągleń) | **SPEŁNIA** | 0,0018 | — | |Δθ| ≤ 0,02 K |
| A3 — naroże 90°, powierzchnie izotermiczne: ΔS = S − (a+b)/t | **SPEŁNIA** | — | — | |ΔS − 0,559| ≤ 0,01 |

## ISO 10211 zał. C — przypadek 1 (28 punktów, tabela normy)

Siatka: 81 × 145 = 11745 komórek; Δx ∈ [1.94; 19.72] mm, Δy ∈ [1.94; 19.86] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| 1.1 | (0.25; 1.75) | 9,7000 | 9,6576 | −0,0424 |
| 1.2 | (0.50; 1.75) | 13,4000 | 13,3788 | −0,0212 |
| 1.3 | (0.75; 1.75) | 14,7000 | 14,7282 | +0,0282 |
| 1.4 | (1.00; 1.75) | 15,1000 | 15,0846 | −0,0154 |
| 2.1 | (0.25; 1.50) | 5,3000 | 5,2519 | −0,0481 |
| 2.2 | (0.50; 1.50) | 8,6000 | 8,6412 | +0,0412 |
| 2.3 | (0.75; 1.50) | 10,3000 | 10,3147 | +0,0147 |
| 2.4 | (1.00; 1.50) | 10,8000 | 10,8097 | +0,0097 |
| 3.1 | (0.25; 1.25) | 3,2000 | 3,1904 | −0,0096 |
| 3.2 | (0.50; 1.25) | 5,6000 | 5,6101 | +0,0101 |
| 3.3 | (0.75; 1.25) | 7,0000 | 7,0140 | +0,0140 |
| 3.4 | (1.00; 1.25) | 7,5000 | 7,4649 | −0,0351 |
| 4.1 | (0.25; 1.00) | 2,0000 | 2,0142 | +0,0142 |
| 4.2 | (0.50; 1.00) | 3,6000 | 3,6409 | +0,0409 |
| 4.3 | (0.75; 1.00) | 4,7000 | 4,6578 | −0,0422 |
| 4.4 | (1.00; 1.00) | 5,0000 | 4,9995 | −0,0005 |
| 5.1 | (0.25; 0.75) | 1,3000 | 1,2622 | −0,0378 |
| 5.2 | (0.50; 0.75) | 2,3000 | 2,3091 | +0,0091 |
| 5.3 | (0.75; 0.75) | 3,0000 | 2,9862 | −0,0138 |
| 5.4 | (1.00; 0.75) | 3,2000 | 3,2186 | +0,0186 |
| 6.1 | (0.25; 0.50) | 0,7000 | 0,7399 | +0,0399 |
| 6.2 | (0.50; 0.50) | 1,4000 | 1,3597 | −0,0403 |
| 6.3 | (0.75; 0.50) | 1,8000 | 1,7669 | −0,0331 |
| 6.4 | (1.00; 0.50) | 1,9000 | 1,9083 | +0,0083 |
| 7.1 | (0.25; 0.25) | 0,3000 | 0,3417 | +0,0417 |
| 7.2 | (0.50; 0.25) | 0,6000 | 0,6297 | +0,0297 |
| 7.3 | (0.75; 0.25) | 0,8000 | 0,8201 | +0,0201 |
| 7.4 | (1.00; 0.25) | 0,9000 | 0,8863 | −0,0137 |

bilans energii: 8.1e-14

## ISO 10211 zał. C — przypadek 2 (punkty A…I + strumień)

Siatka: 307 × 145 = 44515 komórek; Δx ∈ [0.0863; 1.999] mm, Δy ∈ [0.0863; 1.904] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| A | (0; 47.5) mm | 7,1000 | 7,0639 | −0,0361 |
| B | (500; 47.5) mm | 0,8000 | 0,7613 | −0,0387 |
| C | (0; 41.5) mm | 7,9000 | 7,8970 | −0,0030 |
| D | (15; 41.5) mm | 6,3000 | 6,2772 | −0,0228 |
| E | (500; 41.5) mm | 0,8000 | 0,8275 | +0,0275 |
| F | (0; 36.5) mm | 16,4000 | 16,4084 | +0,0084 |
| G | (15; 36.5) mm | 16,3000 | 16,2734 | −0,0266 |
| H | (0; 0) mm | 16,8000 | 16,7677 | −0,0323 |
| I | (500; 0) mm | 18,3000 | 18,3337 | +0,0337 |
| Φ [W/m] | HI → AB | 9,5000 | 9,4903 | −0,0097 |

bilans energii: 4.5e-10; Φ_AB = 9.4903 W/m

## A1 — ściana warstwowa 1D (Robin), rozwiązanie dokładne

Siatka: 111 × 45 = 4995 komórek; Δx ∈ [0.914; 18.7] mm, Δy ∈ [0.973; 19.46] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| θ_si | x = 0.000 | 19,2844 | 19,2844 | +0,0000 |
| styk 1/2 | x = 0.015 | 19,0779 | 19,0779 | +0,0000 |
| styk 2/3 | x = 0.195 | 17,7910 | 17,7910 | +0,0000 |
| styk 3/4 | x = 0.395 | −17,7248 | −17,7248 | −0,0000 |
| θ_se | x = 0.402 | −17,7798 | −17,7798 | −0,0000 |
| U [W/(m²K)] | — | 0,1449 | 0,1449 | −0,0000 |

## A2 — przypadek 1 vs szereg Fouriera (bez zaokrągleń)

Siatka: 81 × 145 = 11745 komórek; Δx ∈ [1.94; 19.72] mm, Δy ∈ [1.94; 19.86] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| 1.1 | (0.25; 1.75) | 9,6582 | 9,6576 | −0,0006 |
| 1.2 | (0.50; 1.75) | 13,3791 | 13,3788 | −0,0002 |
| 1.3 | (0.75; 1.75) | 14,7289 | 14,7282 | −0,0007 |
| 1.4 | (1.00; 1.75) | 15,0854 | 15,0846 | −0,0008 |
| 2.1 | (0.25; 1.50) | 5,2517 | 5,2519 | +0,0002 |
| 2.2 | (0.50; 1.50) | 8,6406 | 8,6412 | +0,0007 |
| 2.3 | (0.75; 1.50) | 10,3155 | 10,3147 | −0,0008 |
| 2.4 | (1.00; 1.50) | 10,8106 | 10,8097 | −0,0009 |
| 3.1 | (0.25; 1.25) | 3,1887 | 3,1904 | +0,0018 |
| 3.2 | (0.50; 1.25) | 5,6090 | 5,6101 | +0,0011 |
| 3.3 | (0.75; 1.25) | 7,0142 | 7,0140 | −0,0002 |
| 3.4 | (1.00; 1.25) | 7,4651 | 7,4649 | −0,0002 |
| 4.1 | (0.25; 1.00) | 2,0142 | 2,0142 | +0,0001 |
| 4.2 | (0.50; 1.00) | 3,6406 | 3,6409 | +0,0003 |
| 4.3 | (0.75; 1.00) | 4,6582 | 4,6578 | −0,0003 |
| 4.4 | (1.00; 1.00) | 5,0000 | 4,9995 | −0,0005 |
| 5.1 | (0.25; 0.75) | 1,2625 | 1,2622 | −0,0003 |
| 5.2 | (0.50; 0.75) | 2,3086 | 2,3091 | +0,0005 |
| 5.3 | (0.75; 0.75) | 2,9858 | 2,9862 | +0,0004 |
| 5.4 | (1.00; 0.75) | 3,2185 | 3,2186 | +0,0001 |
| 6.1 | (0.25; 0.50) | 0,7396 | 0,7399 | +0,0002 |
| 6.2 | (0.50; 0.50) | 1,3594 | 1,3597 | +0,0002 |
| 6.3 | (0.75; 0.50) | 1,7668 | 1,7669 | +0,0000 |
| 6.4 | (1.00; 0.50) | 1,9083 | 1,9083 | +0,0000 |
| 7.1 | (0.25; 0.25) | 0,3418 | 0,3417 | −0,0001 |
| 7.2 | (0.50; 0.25) | 0,6296 | 0,6297 | +0,0001 |
| 7.3 | (0.75; 0.25) | 0,8199 | 0,8201 | +0,0001 |
| 7.4 | (1.00; 0.25) | 0,8863 | 0,8863 | +0,0000 |

## A3 — naroże 90°, powierzchnie izotermiczne: ΔS = S − (a+b)/t

Siatka: 286 × 286 = 81796 komórek; Δx ∈ [0.481; 9.902] mm, Δy ∈ [0.481; 9.902] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| ΔS (siatka n) | t = 0.3, a = b = 1.2 | 0,5590 | 0,5578 | −0,0012 |
| ΔS (siatka 2n) |  | 0,5590 | 0,5585 | −0,0005 |

Wartość odniesienia 0,559 — kwadrat narożny ≈ 0,56 „kwadratu” (odwzorowanie konforemne); wzór Langmuira–Adamsa–Stevensa (1919) podaje 0,54 (przybliżenie).

## Źródła danych referencyjnych

* Physibel — Validation of the program BISCO according to ISO 10211 (rys. C.1, C.2 normy z danymi): https://www.physibel.be/uploads/knowledge_bases/document/40/A2-Validation_BISCO_EN10211.pdf
* SimScale — Thermal Bridge Case 2 (ISO 10211 zał. C, przypadek 2): https://www.simscale.com/docs/validation-cases/thermal-bridge-case-2/
* QuickField — ISO 10211:2007 test case A.2: https://quickfield.com/advanced/iso_10211_2007_case2.htm
* WUFI — Two-dimensional test cases of ISO 10211 (opis przypadku 1): https://wufi.de/en/2015/04/09/two-dimensional-test-cases-of-iso-10211/

Tekst PN-EN ISO 10211:2017 nie był dostępny; dane przypadków 1 i 2 odczytano z rysunków normy zamieszczonych w raporcie walidacyjnym Physibel i potwierdzono niezależnie (SimScale, QuickField — identyczne wymiary, λ, warunki i wyniki). Przed wydaniem PT zaleca się porównanie z egzemplarzem normy (PKN) [NZW — źródło wtórne].
