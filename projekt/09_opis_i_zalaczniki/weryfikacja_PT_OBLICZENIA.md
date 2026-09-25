# Weryfikacja niezależna tomów PT — obliczenia i spójność faktów

Data: 2026-09-25, godz. ok. 07:50. Weryfikator: niezależny, sceptyczny (zakres: OBLICZENIA). Nie wprowadzałem poprawek.

Przedmiot weryfikacji:

* `projekt/wydanie/PT_1_AR_2026.09.25.pdf` (wygenerowany o 06:52), `PT_2_BO_…` (07:27), `PT_3_IS_…` (07:17), `PT_4_IE_…` (07:31);
* źródła Markdown w `projekt/09_opis_i_zalaczniki/PT_*/`;
* generatory `tools/dokumenty/tom_PT_*.py`, `pt_is_*.py`, `pt_ie_*.py`.

Metoda: obliczenia `fizyka_energia.oblicz_wszystko` (ψ z modelu oraz ψ z `wyniki_mostki.json`) i `instalacje.oblicz_wszystko`
uruchomiłem na kopii `src` w katalogu roboczym, na **bieżącym** modelu (`model/budynek.yaml` z 07:34). Do tego doszły
obliczenia ręczne (ISO 6946, ISO 13370, EC2, N SEP-E-002) oraz odczyt `wyniki.json`, `kontrola_zbrojenia.json`
i `obliczenia_statyczne.md` zespołu BO.

## 1. Wyniki odtworzone poprawnie (bez uwag)

| Obszar | Wartość w tomie | Odtworzenie |
|---|---|---|
| U SZ1 (ISO 6946 + ΔU_g + ΔU_f) | R_T 6,872; U 0,17 | 0,13+0,0375+0,200+6,452+0,0125+0,04 = 6,872; U = 0,1455+0,0088+0,012 = 0,166 |
| U SWG (R_se = R_si) | 3,938; 0,27 | zgodne; spełnia U_max = 0,30 |
| U SZL (metoda kresów) | R′/R″ 10,69/10,02 | 10,687 / 10,022; błąd względny 3,2 % |
| Kliny SD1 / DZ1 (zał. C) | U_śr 0,104 / 0,120 | R₁ = Δd/λ; U = ln(1+R₁/R₀)/R₁ → 0,1044 / 0,1197 |
| Podłoga POD-0 (ISO 13370 z izolacją krawędziową) | B′ 4,34; d_t 15,89; U 0,11 | U = 0,1119; Ψ_edge = −0,0098 → U′ = 0,107 |
| Σψ·l + Σχ | H_TB = 30,63 W/K | 29,876 + 0,75 = 30,626 (model); 30,658 (symulacje) |
| Φ_HL, EP (A / A0) | 7,41 kW; 35,59 / 57,85 | 7,408 kW; 35,59 / 57,85 (model z 07:34) |
| Sprawności η_tot | 3,84 / 1,78 | 4,5·1,0·0,96·0,89 = 3,845; 3,2·0,929·0,60 = 1,784 |
| Wentylacja | 365/365; minimum wywiewu 362 | Σ z tabeli 365/365; Σ wyw_min = 361,8 |
| Kanalizacja, wodomierz | Q_ww 2,27 l/s; q 1,128 dm³/s | 0,5·√20,6 = 2,269; 1,128·3,6 = 4,06 m³/h |
| WLZ ∆U, I_B, bilans | 0,61 %; P_s 41,32 kW; 26,2 kW / 39,8 A | √3·40·28,3·r/400 → 0,608 %; Σk_j·P = 41,32; 26 210/(√3·400·0,95) = 39,8 A |
| Obwody | I_B, Z_s, I_k1 | D1 10,68 A; D6 12,22 A; G12 Z_s 0,683 Ω — zgodne |
| PV | 6,45 kWp; U_oc,max 350 V | 15 × 430 Wp; 8 × 43,75 V |
| l_bd B500SP / C25/30 (γ_c = 1,4) | φ12: 451 / 644 mm | f_bd = 2,893 MPa → 450,9; η₁ = 0,7 → 644; α₆ = √2 |
| Mur (W-270) | f_d = 4,50 MPa | 7,66/1,7 = 4,506 |
| Poz. 6.11 (ścinanie, V_Rd,max) | 147,49 kN | 180·192·0,54·17,86/2,256 ≈ 147,5 |
| Kubatura strefy (PWP) | 1 354,40 m³ | Σ składników = 1 354,42 |

## 2. Problemy krytyczne

**K-1. PT-2 BO — tom nie może być podpisany ani wydany.** Tom sam wykazuje 31 pozycji NIEZAMKNIĘTYCH:

* η > 100 % w pozycjach: PL-2 336 %, S0-01 541 %, S1-06 382 %, S0-10 367 % i 10 innych ścianach;
* docisk do podłoża 114 %;
* zbrojenie PF1+PF2 niewykonalne w grubości płyty (4 299 < 5 243 mm²/m);
* zbrojenie na ścinanie płyt poza kontrolą rysunków.

Wyniki `wyniki.json` (06:33), MES (06:48) i kontroli zbrojenia (06:48) są starsze niż model, który od złożenia tomu
zmienił się jeszcze raz (07:34). Bez ponownej analizy i zamknięcia tych pozycji oświadczenie projektanta PT
z art. 41 ust. 4a pkt 2 PB nie może być złożone.

**K-2. PT-2 BO, poz. 6.11 (nadproże N-O0-18) — pozycja uznana za spełnioną, choć zbrojenie ściskane jest za małe.**

* Obliczenie daje przekrój podwójnie zbrojony: μ = 0,486 > μ_lim = 0,372 i A_s2 = **235 mm²**.
* Kontrola rysunku PT-BO-25 przyjmuje górą 2Ø12 = **226 mm²** < 235 mm². Sprawdza tylko warunek 0,15·A_s,dół = 181 mm².
* Wysokość użyteczną d = 213 mm przyjęto dla jednej warstwy prętów. Kontrola zbrojenia podaje jednak dołem 6Ø16
  „w 2 warstwach (3 + 3)”. Wtedy d ≈ 192 mm, M_lim ≈ 44 kNm i A_s2 ≈ 430 mm², czyli prawie dwa razy więcej niż 226 mm².
* W wnioskach pozycji jest „wszystkie warunki spełnione”, a zbrojenia górnego nie wymieniono.

Wniosek: sprawdzić A_s2 ≤ A_s,górą w module i w kontroli rysunków. Nadproże zwiększyć albo zespolić ze stropem.
