# Płyta fundamentowa PF1+PF2 — MES na podłożu sprężystym (pozycja PF-MES)

Plik generowany przez `lamela.views.konstrukcja` (moduł obliczeń `lamela.obliczenia.konstrukcja.plyta_fundamentowa`). Model: płyta ACM z żebrami/pogrubieniami jako strefami zwiększonej grubości, sprężyny Winklera w węzłach, kontakt jednostronny (iteracja strefy docisku), obciążenia ścian parteru i słupów z obliczeń statycznych (profile obciążeń, średnia krocząca 2,0 m), obwiednia kombinacji STR (PN-EN 1990 + NA) × 3 warianty k_s (39 rozwiązań). Siatka elementów ≤ 0,30 m, 3544 elementów.

## Weryfikacja modelu

Belka nieskończona na podłożu sprężystym (Hetényi 1946): ugięcie pod siłą — błąd < 0,1 %, moment w środku elementu — błąd < 0,5 % (test `tools/test_rysunki_konstrukcja.py::test_hetenyi`).

## Współczynnik podatności podłoża (Winkler) z parametrów geotechnicznych

- Moduł sprężystości gruntu z modułu edometrycznego: E_s = M₀·(1+ν)(1−2ν)/(1−ν) = 80000·(1+0,30)(1−2·0,30)/(1−0,30) = **59429** kPa *(teoria sprężystości (jednoosiowy stan odkształcenia); PN-EN 1997-2 zał. K)*
- Współczynnik wpływu (środek prostokąta, m = L/B): I_c(m), m = L/B = I_c(1,940) = **1,513** *(Bowles (1996) (5-16a); PN-EN 1997-1 zał. F.2)*
- Współczynnik podatności (osiadanie średnie α·s_c): k_s = E_s/(α·B·(1−ν²)·I_c) = 59429/(0,85·9,57·(1−0,30²)·1,513) = **5303** kN/m³
- Obwiednia wariantów (niepewność modelu Winklera): k_s,min = k_s/r; k_s,max = k_s·r = 5303/2,0; 5303·2,0 = **2652; 10606** kN/m³ *([ZAŁ] Bowles 9.7)*

## Obciążenia płyty fundamentowej w MES (poza ścianami i słupami)

- Ciężar płyty (z żebrami/pogrubieniami) i warstw podłogi nad płytą: g = 25·h_el + g_podł = **25·h_el + 1,60** kN/m²
- Obciążenie użytkowe posadzki — kat. A (stropy mieszkalne (kat. A)): q_k = **2,00** kN/m² *(PN-EN 1991-1-1 tabl. 6.2 + NA; R5 3.3 [NZW NA — górna granica EN])*
- Płyta PF2: obciążenie użytkowe — kat. F (garaż (kat. F)); ψ₀/ψ₁/ψ₂ = 0,7/0,7/0,6: q_k; Q_k = **2,50 kN/m²; 20 kN** *(PN-EN 1991-1-1 tabl. 6.8)*

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
| Nośność podłoża (GEO, DA2*) | V_d = 13990,7 kN | R_d = 224314,1 kN | 6% | spełniony | PN-EN 1997-1 (6.1), NA.2.6 |

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
- Maks. docisk obliczeniowy z MES (obwiednia k_s, kombinacje STR/GEO): p_d,max = **272,8** kPa

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Docisk lokalny do podłoża (pasmo pod żebrem) | p_d,max = 272,8 kPa | q_Rd = 318,8 kPa | 86% | spełniony | PN-EN 1997-1 6.5.2, zał. D |

> Parametry gruntu PRZYKŁADOWE (brief) — w II kat. geotechnicznej wymagane badania CPT/DPL (W-282, E-04).

## Odrywanie płyty od podłoża i osiadanie (MES, kontakt jednostronny)

- Udział powierzchni bez kontaktu (maks. po kombinacjach ULS i wariantach k_s): A_oder/A = **0,0** %
- Maks. docisk charakterystyczny (SLS): p_k,max = **213,0** kPa
- Maks. osiadanie sprężyste (SLS, k_s nominalne): w_k,max = **33,4** mm

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Osiadanie (PN-EN 1997-1 zał. H: s ≤ 50 mm dla fundamentów bezpośrednich) | w_k = 33,4 mm | s_dop = 50,0 mm | 67% | spełniony | PN-EN 1997-1 zał. H |

## Przebicie płyty pod słupem SL1 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **132,3** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **132,3 kN; 27,5 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,191 m; 1,301 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,189 MPa | v_Rd = 2,286 MPa | 8% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL2 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **319,9** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **319,9 kN; 64,9 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,447 m; 2,102 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,285 MPa | v_Rd = 0,980 MPa | 29% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL3 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **410,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **410,4 kN; 71,8 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,510 m; 2,303 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,346 MPa | v_Rd = 0,857 MPa | 40% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL4 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **470,6** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **470,6 kN; 55,8 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,510 m; 2,303 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,424 MPa | v_Rd = 0,857 MPa | 49% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL9 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **662,1** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,90 m = **838** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **662,1 kN; 141,0 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,754 m; 1,784 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,523 MPa | v_Rd = 0,727 MPa | 72% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL11 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **510,8** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,55 m = **488** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **510,8 kN; 100,5 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,537 m; 2,466 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,511 MPa | v_Rd = 0,668 MPa | 77% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL13 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1326,2** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup wewnętrzny = **1,15** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **1326,2 kN; 196,9 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,638 m; 5,447 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,374 MPa | v_Rd = 0,686 MPa | 54% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL16 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1462,4** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup wewnętrzny = **1,15** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **1462,3 kN; 223,7 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,702 m; 5,848 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,382 MPa | v_Rd = 0,624 MPa | 61% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL18 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **1335,0** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,70 m = **638** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup wewnętrzny = **1,15** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **1335,0 kN; 179,3 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,638 m; 5,447 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,382 MPa | v_Rd = 0,686 MPa | 56% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Przebicie płyty pod słupem SL20 (6.4.4(2))

- Siła od słupa (obwiednia ULS): V_Ed = **241,0** kN
- Wysokość użyteczna w strefie słupa: d = h = 0,50 m = **438** mm
- Położenie słupa względem krawędzi płyty; współczynnik β: β (6.39), rys. 6.21N = słup narożny = **1,50** *(PN-EN 1992-1-1 6.4.3(6) [wartości zalecane])*
- Kombinacja miarodajna: siła słupa i odpór netto w obwodzie (MES, grunt − 1,35·ciężar płyty): V_Ed; ΔV_Ed = **241,0 kN; 54,4 kN** *(6.4.4(2))*
- Obwód miarodajny (maks. v_Ed/v_Rd dla a ≤ 2d; przycięty krawędzią płyty): a; u = **0,526 m; 2,731 m**

| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |
|---|---|---|---|---|---|
| Przebicie — fundament (6.4.4(2), (6.51)–(6.53)) | v_Ed = 0,234 MPa | v_Rd = 0,633 MPa | 37% | spełniony | PN-EN 1992-1-1 6.4.4 |

## Obwiednia momentów i zbrojenie wymagane

| Kierunek | M_Ed ekstremalny [kNm/m] | A_s,req maks. [mm²/m] | A_s,req 90 % pola płyty [mm²/m] |
|---|---:|---:|---:|
| dol_x | 1344.0 | 5339 | 489 |
| dol_y | 771.6 | 4742 | 666 |
| gora_x | -1335.9 | 5153 | 823 |
| gora_y | -972.2 | 5148 | 1665 |

Elementy z μ > μ_lim — przekrój podwójnie zbrojony: 1 z 3544 (A_s2,max = 403 mm²/m; A_s2 = ΔM/(σ_s2·(d − a₂)), ΔM = M_Ed − μ_lim·b·d²·η·f_cd, σ_s2 = min(f_yd; E_s·ε_cu3·(1 − a₂/x_lim)); A_s2 dodane do wymagania warstwy przeciwnej, A_s1 = A_s,lim + A_s2·σ_s2/f_yd).

