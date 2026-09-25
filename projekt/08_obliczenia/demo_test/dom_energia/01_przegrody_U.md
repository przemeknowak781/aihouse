# Obliczenia U przegród — model testowy energii (garaż, wspornik, dach zielony)

## Współczynniki przenikania ciepła U przegród (PN-EN ISO 6946:2017)

**Podstawa:** PN-EN ISO 6946:2017-10 (p. 6.7–6.9, zał. C, zał. F); WT zał. 2 pkt 1.1 (U_C(max)); cele projektu wg rejestru W-245

> U_c = 1/R_T + ΔU_g + ΔU_f + ΔU_r; R_T = R_si + Σ d_j/λ_j + R_se (przegrody niejednorodne: R_T = (R'_T + R''_T)/2).
> Wynik U podano z dokładnością do 2 cyfr znaczących; opory — do 0,01 m²·K/W.

| Kod | Przegroda | Rola | R_T [m²K/W] | ΣΔU | U_c [W/(m²K)] | U_C(max) WT | WT | U cel | cel |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|:---|
| POD-0 | Podłoga na gruncie (izolacja pod jastrychem, papa na płycie) | podłoga na gruncie | R_f = 5,29 | 0,000 | 0,13 | 0,30 | ✔ spełnia | 0,20 | ✔ spełnia |
| POD-G | Posadzka garażu na gruncie | podłoga na gruncie | R_f = 0,07 | 0,000 | 0,93 | — | — | — | — |
| SZ1 | Ściana zewnętrzna, silikat 18 + ETICS EPS 20 | ściana zewnętrzna | 6,90 | 0,021 | 0,17 | 0,20 | ✔ spełnia | 0,15 | ✘ NIE spełnia |
| DZ-P0 | Stropodach zielony ekstensywny nad parterem | stropodach/dach | 10,50 | 0,009 | 0,10 | 0,15 | ✔ spełnia | 0,12 | ✔ spełnia |
| SWG | Ściana dom–garaż, silikat 18 + EPS 12 od garażu | ściana do pom. nieogrzewanego | 4,41 | 0,020 | 0,25 | 0,30 | ✔ spełnia | 0,25 | ✔ spełnia |
| SZG | Ściana zewnętrzna garażu nieogrzewanego, silikat 24 | ściana zewnętrzna | 0,51 | 0,000 | 2,0 | — | — | — | — |
| SD-G | Dach garażu (nieogrzewany) | stropodach/dach | 0,23 | 0,000 | 4,3 | — | — | — | — |
| ST3\|P1\|zewn | podłoga POD-1 + płyta ZB_C30 20 cm + sufit SUF-Z | strop nad powietrzem zewn. | 11,76 | 0,017 | 0,10 | 0,15 | ✔ spełnia | — | — |
| SD-D1 | Stropodach PIR 24 cm, EPDM | stropodach/dach | 11,18 | 0,010 | 0,082 | 0,15 | ✔ spełnia | 0,12 | ✔ spełnia |
| ST2\|P1\|dol | podłoga POD-1 + płyta ZB_C30 20 cm + sufit SUF-G | strop nad pom. nieogrzewanym | 10,28 | 0,004 | 0,10 | 0,25 | ✔ spełnia | — | — |

### POD-0 — Podłoga na gruncie (izolacja pod jastrychem, papa na płycie) (podłoga na gruncie)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,00 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Płytki gresowe | wykonczenie | 1,0 | 1,300 | 0,008 | jednorodna |
| 2 | Jastrych cementowy | wykonczenie | 6,5 | 1,000 | 0,065 | jednorodna |
| 3 | Folia PE 0,2 mm (warstwa rozdzielająca) | paroizolacja | 0,0 | 0,350 | 0,001 | jednorodna |
| 4 | Polistyren ekstrudowany XPS 300 | izolacja | 18,0 | 0,035 | 5,143 | jednorodna |
| 5 | Izolacja przeciwwilgociowa — papa termozgrzewalna | przeciwwilgociowa | 0,4 | 0,230 | 0,017 | jednorodna |
| 6 | Beton C25/30 | konstrukcja | 12,0 | 2,000 | 0,060 | jednorodna |
| 7 | Podsypka piaskowa | grunt | 15,0 | 2,000 | 0,000 | grunt — podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu) |

Opór warstw podłogi R_f = Σ R_j = 5,294 m²K/W (bez R_si, R_se i gruntu) — U podłogi na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.

**U_equiv = 0,13 W/(m²K)**; wymaganie WT: U ≤ 0,30 (✔ spełnia); cel: 0,20 (✔ spełnia).
* U_equiv wg PN-EN ISO 13370: A = 74,53 m², P = 35,04 m, B' = 4,25 m, d_t = 11,41 m

### POD-G — Posadzka garażu na gruncie (podłoga na gruncie)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,00 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Beton C25/30 | konstrukcja | 15,0 | 2,000 | 0,075 | jednorodna |
| 2 | Podsypka piaskowa | grunt | 15,0 | 2,000 | 0,000 | grunt — podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu) |

Opór warstw podłogi R_f = Σ R_j = 0,075 m²K/W (bez R_si, R_se i gruntu) — U podłogi na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.

**U_equiv = 0,93 W/(m²K)**; wymaganie WT: U ≤ — (—); cel: — (—).
* U_equiv wg PN-EN ISO 13370: A = 43,66 m², P = 26,76 m, B' = 3,26 m, d_t = 0,83 m

### SZ1 — Ściana zewnętrzna, silikat 18 + ETICS EPS 20 (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy | tynk | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy 18 cm | konstrukcja | 18,0 | 0,770 | 0,234 | jednorodna |
| 3 | Styropian grafitowy EPS 031 | izolacja | 20,0 | 0,031 | 6,452 | jednorodna |
| 4 | Tynk silikonowy cienkowarstwowy | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,13 + Σ R_j + 0,04 = 6,903 m²K/W; U₀ = 1/R_T = 0,1449 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0087, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,1656 W/(m²K).

**U = 0,17 W/(m²K)**; wymaganie WT: U ≤ 0,20 (✔ spełnia); cel: 0,15 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].

### DZ-P0 — Stropodach zielony ekstensywny nad parterem (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 8 | Tynk gipsowy | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 7 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 6 | Paroizolacja bitumiczna z wkładką Al | paroizolacja | 0,4 | 0,230 | 0,017 | jednorodna |
| 5 | Płyty PIR | izolacja | 22,0 | 0,022 | 10,000 | jednorodna |
| 4 | Membrana EPDM 1,5 mm (odporna na przerastanie korzeni) | hydroizolacja | 0,1 | 0,250 | 0,006 | jednorodna |
| 3 | Mata drenażowa kubełkowa HDPE | drenaz | 2,5 | 0,300 | 0,083 | jednorodna |
| 2 | Geowłóknina filtracyjna | geowloknina | 0,2 | 0,200 | 0,010 | jednorodna |
| 1 | Substrat dachu zielonego (rozchodniki) | substrat | 8,0 | 0,600 | 0,133 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 10,502 m²K/W; U₀ = 1/R_T = 0,0952 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0091, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1043 W/(m²K).

**U = 0,10 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].

### SWG — Ściana dom–garaż, silikat 18 + EPS 12 od garażu (ściana do pom. nieogrzewanego)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,13 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy | tynk | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy 18 cm | konstrukcja | 18,0 | 0,770 | 0,234 | jednorodna |
| 3 | Styropian grafitowy EPS 031 | izolacja | 12,0 | 0,031 | 3,871 | jednorodna |
| 4 | Tynk silikonowy cienkowarstwowy | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,13 + Σ R_j + 0,13 = 4,412 m²K/W; U₀ = 1/R_T = 0,2266 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0077, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,2463 W/(m²K).

**U = 0,25 W/(m²K)**; wymaganie WT: U ≤ 0,30 (✔ spełnia); cel: 0,25 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 2 (ściana dom–garaż) (W-243); cel: R6 3.2 [ZAŁ].

### SZG — Ściana zewnętrzna garażu nieogrzewanego, silikat 24 (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk cementowo-wapienny | tynk | 1,5 | 0,820 | 0,018 | jednorodna |
| 2 | Bloczek wapienno-piaskowy 24 cm | konstrukcja | 24,0 | 0,770 | 0,312 | jednorodna |
| 3 | Tynk silikonowy cienkowarstwowy | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,13 + Σ R_j + 0,04 = 0,510 m²K/W; U₀ = 1/R_T = 1,9609 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0000, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 1,9609 W/(m²K).

**U = 2,0 W/(m²K)**; wymaganie WT: U ≤ — (—); cel: — (—). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].
* przegroda wyłącznie pomieszczenia nieogrzewanego — bez wymagań U (WT zał. 2 pkt 1.1)

### SD-G — Dach garażu (nieogrzewany) (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 2 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 1 | Membrana EPDM 1,5 mm (odporna na przerastanie korzeni) | hydroizolacja | 0,1 | 0,250 | 0,006 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 0,233 m²K/W; U₀ = 1/R_T = 4,2926 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0000, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 4,2926 W/(m²K).

**U = 4,3 W/(m²K)**; wymaganie WT: U ≤ — (—); cel: — (—). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* przegroda wyłącznie pomieszczenia nieogrzewanego — bez wymagań U (WT zał. 2 pkt 1.1)

### ST3|P1|zewn — podłoga POD-1 + płyta ZB_C30 20 cm + sufit SUF-Z (strop nad powietrzem zewn.)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Deska podłogowa dębowa | wykonczenie | 1,5 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy | wykonczenie | 5,5 | 1,000 | 0,055 | jednorodna |
| 3 | Styropian akustyczny EPS T | izolacja | 13,0 | 0,040 | 3,250 | jednorodna |
| 4 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 5 | Styropian grafitowy EPS 031 | izolacja | 25,0 | 0,031 | 8,065 | jednorodna |
| 6 | Tynk silikonowy cienkowarstwowy | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,17 + Σ R_j + 0,04 = 11,760 m²K/W; U₀ = 1/R_T = 0,0850 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0047, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,1017 W/(m²K).

**U = 0,10 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: — (—). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 („nad przejazdami”) — spód wspornika P2 (W-243) [INT].

### SD-D1 — Stropodach PIR 24 cm, EPDM (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 5 | Tynk gipsowy | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 4 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 3 | Paroizolacja bitumiczna z wkładką Al | paroizolacja | 0,4 | 0,230 | 0,017 | jednorodna |
| 2 | Płyty PIR | izolacja | 24,0 | 0,022 | 10,909 | klin — grubość minimalna warstwy klinowej (zał. C) |
| 1 | Membrana EPDM 1,5 mm (odporna na przerastanie korzeni) | hydroizolacja | 0,1 | 0,250 | 0,006 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 11,184 m²K/W; U₀ = 1/R_T = 0,0894 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0095, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,0989 W/(m²K).

Warstwa klinowa: U_śr = 0,0728 W/(m²K) (zał. C — wzór dla kształtu 'prostokat'); U = U_śr + ΣΔU = 0,0823 W/(m²K).

**U = 0,082 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 24,0 cm, d_max = 36,0 cm

### ST2|P1|dol — podłoga POD-1 + płyta ZB_C30 20 cm + sufit SUF-G (strop nad pom. nieogrzewanym)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,17 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Deska podłogowa dębowa | wykonczenie | 1,5 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy | wykonczenie | 5,5 | 1,000 | 0,055 | jednorodna |
| 3 | Styropian akustyczny EPS T | izolacja | 13,0 | 0,040 | 3,250 | jednorodna |
| 4 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 5 | Styropian grafitowy EPS 031 | izolacja | 20,0 | 0,031 | 6,452 | jednorodna |
| 6 | Tynk silikonowy cienkowarstwowy | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,17 + Σ R_j + 0,17 = 10,277 m²K/W; U₀ = 1/R_T = 0,0973 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0039, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1012 W/(m²K).

**U = 0,10 W/(m²K)**; wymaganie WT: U ≤ 0,25 (✔ spełnia); cel: — (—). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 7, 8c (W-243).

**Założenia i dane wejściowe:**

* Grunt: piasek — λ = 2,0 W/(m·K), ρc = 2,0 MJ/(m³·K) (PN-EN ISO 13370 tab. kategorii gruntu; opinia geotechniczna przykładowa: piaski średnie) [NZW]
* f_g1 = 1,45, G_w = 1,00 (ZWG ≈ 3,8 m p.p.t. > 1 m), θ_m,e = 7,9 °C [NZW] — źródło: PN-EN 12831:2006 p. 7.1.3 i NA; rejestr W-150
* Stolarka: U_g, U_f, Ψ_g, szerokości ram, g_n — dane przykładowe typowych wyrobów (dane/wyroby_przykladowe.yaml); do zastąpienia deklaracjami wybranego producenta [DANE PRZYKŁADOWE – FIKCYJNE]
* Łączniki izolacji mocowanej mechanicznie (ETICS, elewacja wentylowana, docieplenie spodu stropu): n_f = 6,0 szt./m², χ_p = 0,002 W/K (ΔU_f = n_f·χ_p, PN-EN ISO 6946:2017 zał. F.3) [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z ETA typowego łącznika ETICS z trzpieniem stalowym, χ_p = 0,002 W/K (lub równoważny)
* Nieszczelności w warstwie izolacji: poziom 1 (ΔU'' = 0,01 W/(m²·K)), chyba że wykazano poziom 0 [NZW] — źródło: PN-EN ISO 6946:2017 zał. F.2; rejestr W-250
* Ψ węzłów bez wyników symulacji — wartości domyślne (fallback) PN-EN ISO 14683:2017 zał. C w systemie wymiarów wewnętrznych całkowitych (Ψ_oi); do zastąpienia wynikami ISO 10211 [NZW]
* Zacienienie stałe (okapy — płyty wysunięte, lamele) — F_sh z danych godzinowych TMY Poznań i położenia Słońca; model izotropowy nieba, ρ_g = 0,2 [ZAŁ] — źródło: PN-EN ISO 52016-1 p. 6.5.13 (idea); lamela.sun

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
