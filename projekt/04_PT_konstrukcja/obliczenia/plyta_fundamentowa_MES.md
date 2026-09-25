# Płyta fundamentowa PF1+PF2 — MES na podłożu sprężystym (pozycja PF-MES)

Plik generowany przez `lamela.views.konstrukcja` (moduł obliczeń `lamela.obliczenia.konstrukcja.plyta_fundamentowa`). Model: płyta ACM z żebrami/pogrubieniami jako strefami zwiększonej grubości, sprężyny Winklera w węzłach, kontakt jednostronny (iteracja strefy docisku), obciążenia ścian parteru i słupów z obliczeń statycznych (profile obciążeń, średnia krocząca 2,0 m), obwiednia kombinacji STR (PN-EN 1990 + NA) × 3 warianty k_s (30 rozwiązań). Siatka elementów ≤ 0,30 m, 3298 elementów.

## Weryfikacja modelu

Belka nieskończona na podłożu sprężystym (Hetényi 1946): ugięcie pod siłą — błąd < 0,1 %, moment w środku elementu — błąd < 0,5 % (test `tools/test_rysunki_konstrukcja.py::test_hetenyi`).

## Współczynnik podatności podłoża (Winkler) z parametrów geotechnicznych

- Moduł sprężystości gruntu z modułu edometrycznego: E_s = M₀·(1+ν)(1−2ν)/(1−ν) = 80000·(1+0,30)(1−2·0,30)/(1−0,30) = **59429** kPa *(teoria sprężystości (jednoosiowy stan odkształcenia); PN-EN 1997-2 zał. K)*
- Współczynnik wpływu (środek prostokąta, m = L/B): I_c(m), m = L/B = I_c(1,940) = **1,513** *(Bowles (1996) (5-16a); PN-EN 1997-1 zał. F.2)*
- Współczynnik podatności (osiadanie średnie α·s_c): k_s = E_s/(α·B·(1−ν²)·I_c) = 59429/(0,85·9,57·(1−0,30²)·1,513) = **5303** kN/m³
- Obwiednia wariantów (niepewność modelu Winklera): k_s,min = k_s/r; k_s,max = k_s·r = 5303/2,0; 5303·2,0 = **2652; 10606** kN/m³ *([ZAŁ] Bowles 9.7)*

## Nośność podłoża pod płytą fundamentową (PN-EN 1997-1 zał. D, DA2*)

- Parametry podłoża (charakterystyczne, M1: γ_φ = 1,0): φ'_k; c'_k; γ = **33,0°; 0,0 kPa; 18,5 kN/m³ — Piasek średni (Ps), średnio zagęszczony, I_D ≈ 0,6 [DANE PRZYKŁADOWE]**
- Współczynnik nośności (nadkład): N_q = e^(π·tg φ')·tg²(45° + φ'/2) = **26,09** *((D.2))*
- Współczynnik nośności (spójność): N_c = (N_q − 1)·ctg φ' = **38,64**
- Współczynnik nośności (ciężar gruntu): N_γ = 2·(N_q − 1)·tg φ' = **32,59**
- Wymiary efektywne: B' = B − 2e_B; L' = L − 2e_L = **18,575 m × 9,575 m**
- Współczynniki kształtu: s_q = 1 + (B'/L')·sin φ'; s_γ = 1 − 0,3·B'/L' = **s_q = 2,057; s_γ = 0,418** *((D.4))*
- Naprężenie od nadkładu w poziomie posadowienia: q' = γ·D = 18,50·0,30 = **5,55** kPa
- Ciężar efektywny gruntu pod fundamentem (wpływ ZWG): γ' = **11,60** kN/m³
- Jednostkowy opór graniczny: R_k/A' = c'·N_c·s_c·i_c + q'·N_q·s_q·i_q + ½·γ'·B'·N_γ·s_γ·i_γ = 0,0 + 5,55·26,09·2,057·1,000 + 0,5·11,60·18,575·32,59·0,418·1,000 = **1765,7** kPa *((D.2))*
- Opór graniczny: R_k = (R_k/A')·A' = 1765,7·177,856 = **314039,8** kN
- Obliczeniowy opór graniczny (DA2*): R_d = R_k/γ_R;v = 314039,8/1,40 = **224314,1** kN *(NA.2.6 (Ap2:2010), tabl. A.5)*

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Nośność podłoża (GEO, DA2*) | V_d = 13797,8 kN | R_d = 224314,1 kN | 6% | spełniony | PN-EN 1997-1 (6.1), NA.2.6 |

> Parametry gruntu PRZYKŁADOWE (brief) — w II kat. geotechnicznej wymagane badania CPT/DPL (W-282, E-04).

## Nacisk lokalny — maks. docisk MES p_d pod pasmem b = 1,00 m (żebro + 2h)

- Parametry podłoża (charakterystyczne, M1: γ_φ = 1,0): φ'_k; c'_k; γ = **33,0°; 0,0 kPa; 18,5 kN/m³ — Piasek średni (Ps), średnio zagęszczony, I_D ≈ 0,6 [DANE PRZYKŁADOWE]**
- Współczynnik nośności (nadkład): N_q = e^(π·tg φ')·tg²(45° + φ'/2) = **26,09** *((D.2))*
- Współczynnik nośności (spójność): N_c = (N_q − 1)·ctg φ' = **38,64**
- Współczynnik nośności (ciężar gruntu): N_γ = 2·(N_q − 1)·tg φ' = **32,59**
- Szerokość efektywna ławy: B' = B − 2e_B = 1,00 − 2·0,000 = **1,000** m
- Naprężenie od nadkładu w poziomie posadowienia: q' = γ·D = 18,50·0,30 = **5,55** kPa
- Jednostkowy opór graniczny: R_k/A' = c'·N_c·s_c·i_c + q'·N_q·s_q·i_q + ½·γ'·B'·N_γ·s_γ·i_γ = 0,0 + 5,55·26,09·1,000·1,000 + 0,5·18,50·1,000·32,59·1,000·1,000 = **446,3** kPa *((D.2))*
- Opór graniczny (na 1 m ławy): R_k = (R_k/A')·A' = 446,3·1,000 = **446,3** kN/m
- Obliczeniowy opór graniczny (DA2*): R_d = R_k/γ_R;v = 446,3/1,40 = **318,8** kN/m *(NA.2.6 (Ap2:2010), tabl. A.5)*
- Maks. docisk obliczeniowy z MES (obwiednia k_s, kombinacje STR/GEO): p_d,max = **291,3** kPa

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Docisk lokalny do podłoża (pasmo pod żebrem) | p_d,max = 291,3 kPa | q_Rd = 318,8 kPa | 91% | spełniony | PN-EN 1997-1 6.5.2, zał. D |

> Parametry gruntu PRZYKŁADOWE (brief) — w II kat. geotechnicznej wymagane badania CPT/DPL (W-282, E-04).

## Odrywanie płyty od podłoża i osiadanie (MES, kontakt jednostronny)

- Udział powierzchni bez kontaktu (maks. po kombinacjach ULS i wariantach k_s): A_oder/A = **0,0** %
- Maks. docisk charakterystyczny (SLS): p_k,max = **228,0** kPa
- Maks. osiadanie sprężyste (SLS, k_s nominalne): w_k,max = **35,0** mm

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Osiadanie (PN-EN 1997-1 zał. H: s ≤ 50 mm dla fundamentów bezpośrednich) | w_k = 35,0 mm | s_dop = 50,0 mm | 70% | spełniony | PN-EN 1997-1 zał. H |

## Przebicie płyty pod słupem SL1 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **132,3** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,017 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,023 MPa | v_Rd = 0,343 MPa | 7% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL2 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **319,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,017 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,056 MPa | v_Rd = 0,343 MPa | 16% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL3 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **410,1** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,017 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,071 MPa | v_Rd = 0,343 MPa | 21% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL4 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **470,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,017 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,082 MPa | v_Rd = 0,343 MPa | 24% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL9 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **661,8** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,55 m = **488** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **0,976 m; 7,292 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,186 MPa | v_Rd = 0,368 MPa | 51% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL11 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **510,7** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,55 m = **488** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **0,976 m; 7,292 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,143 MPa | v_Rd = 0,368 MPa | 39% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL13 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1322,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,457 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,219 MPa | v_Rd = 0,343 MPa | 64% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL16 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1460,0** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,457 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,242 MPa | v_Rd = 0,343 MPa | 71% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL18 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1333,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **1,276 m; 9,457 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,221 MPa | v_Rd = 0,343 MPa | 64% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL20 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **241,1** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,50 m = **438** mm
- Obwód miarodajny (min v_Rd/v_Ed dla a ≤ 2d; bez redukcji odporem): a; u = **0,876 m; 6,744 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,082 MPa | v_Rd = 0,380 MPa | 21% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Obwiednia momentów i zbrojenie wymagane

| Kierunek | M_Ed ekstremalny [kNm/m] | A_s,req maks. [mm²/m] | A_s,req 90 % pola płyty [mm²/m] |
|---|---:|---:|---:|
| dol_x | 1418.5 | 5675 | 521 |
| dol_y | 799.0 | 4942 | 645 |
| gora_x | -1341.6 | 5726 | 809 |
| gora_y | -1190.7 | 6567 | 1621 |

Elementy z μ > μ_lim — przekrój podwójnie zbrojony: 1 z 3298 (A_s2,max = 328 mm²/m; A_s2 = ΔM/(σ_s2·(d − a₂)), ΔM = M_Ed − μ_lim·b·d²·η·f_cd, σ_s2 = min(f_yd; E_s·ε_cu3·(1 − a₂/x_lim)); A_s2 dodane do wymagania warstwy przeciwnej, A_s1 = A_s,lim + A_s2·σ_s2/f_yd).

