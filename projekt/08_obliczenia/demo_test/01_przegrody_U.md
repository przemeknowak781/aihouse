# Obliczenia U przegród — model testowy (dom_testowy.yaml)

## Współczynniki przenikania ciepła U przegród (PN-EN ISO 6946:2017)

**Podstawa:** PN-EN ISO 6946:2017-10 (p. 6.7–6.9, zał. C, zał. F); WT zał. 2 pkt 1.1 (U_C(max)); cele projektu wg rejestru W-245

> U_c = 1/R_T + ΔU_g + ΔU_f + ΔU_r; R_T = R_si + Σ d_j/λ_j + R_se (przegrody niejednorodne: R_T = (R'_T + R''_T)/2).
> Wynik U podano z dokładnością do 2 cyfr znaczących; opory — do 0,01 m²·K/W.

| Kod | Przegroda | Rola | R_T [m²K/W] | ΣΔU | U_c [W/(m²K)] | U_C(max) WT | WT | U cel | cel |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|:---|
| POD-0 | Podłoga na gruncie | podłoga na gruncie | R_f = 4,42 | 0,000 | 0,17 | 0,30 | ✔ spełnia | 0,20 | ✔ spełnia |
| SZ1 | Ściana zewnętrzna nośna, silikat 18 + ETICS EPS 20 | ściana zewnętrzna | 6,90 | 0,021 | 0,17 | 0,20 | ✔ spełnia | 0,15 | ✘ NIE spełnia |
| SD-D1 | Stropodach pełny, odwrócony spadek PIR | stropodach/dach | 10,25 | 0,010 | 0,084 | 0,15 | ✔ spełnia | 0,12 | ✔ spełnia |

### POD-0 — Podłoga na gruncie (podłoga na gruncie)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,00 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Płytki gresowe 60x120 | wykonczenie | 1,0 | 1,300 | 0,008 | jednorodna |
| 2 | Jastrych cementowy | wykonczenie | 6,5 | 1,000 | 0,065 | jednorodna |
| 3 | Polistyren ekstrudowany XPS 300 | izolacja | 15,0 | 0,035 | 4,286 | jednorodna |
| 4 | Beton C25/30 (płyta podkładowa) | konstrukcja | 12,0 | 2,000 | 0,060 | jednorodna |
| 5 | Podsypka piaskowa zagęszczona | grunt | 15,0 | 2,000 | 0,000 | grunt — podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu) |

Opór warstw podłogi R_f = Σ R_j = 4,418 m²K/W (bez R_si, R_se i gruntu) — U podłogi na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.

**U_equiv = 0,17 W/(m²K)**; wymaganie WT: U ≤ 0,30 (✔ spełnia); cel: 0,20 (✔ spełnia).
* U_equiv wg PN-EN ISO 13370: A = 74,03 m², P = 34,59 m, B' = 4,28 m, d_t = 9,66 m

### SZ1 — Ściana zewnętrzna nośna, silikat 18 + ETICS EPS 20 (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy maszynowy | tynk | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy 18 cm, kl. 20 | konstrukcja | 18,0 | 0,770 | 0,234 | jednorodna |
| 3 | Styropian grafitowy EPS 031 | izolacja | 20,0 | 0,031 | 6,452 | jednorodna |
| 4 | Tynk silikonowy cienkowarstwowy, biały | tynk | 0,7 | 0,700 | 0,010 | jednorodna |

R_T = 0,13 + Σ R_j + 0,04 = 6,903 m²K/W; U₀ = 1/R_T = 0,1449 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0087, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,1656 W/(m²K).

**U = 0,17 W/(m²K)**; wymaganie WT: U ≤ 0,20 (✔ spełnia); cel: 0,15 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].

### SD-D1 — Stropodach pełny, odwrócony spadek PIR (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 5 | Tynk gipsowy maszynowy | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 4 | Żelbet C30/37 | konstrukcja | 20,0 | 2,300 | 0,087 | jednorodna |
| 3 | Paroizolacja bitumiczna | paroizolacja | 0,2 | 0,230 | — | pominieta — membrana — opór cieplny pominięty (grubość rysunkowa) |
| 2 | Płyty PIR (izolacja spadkowa) | izolacja | 22,0 | 0,022 | 10,000 | jednorodna |
| 1 | Membrana EPDM 1,5 mm | hydroizolacja | 0,1 | 0,250 | — | pominieta — membrana — opór cieplny pominięty (grubość rysunkowa) |

R_T = 0,10 + Σ R_j + 0,04 = 10,252 m²K/W; U₀ = 1/R_T = 0,0975 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0095, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1071 W/(m²K).

Warstwa klinowa: U_śr = 0,0749 W/(m²K) (całkowanie numeryczne (zał. C, p. C.1), siatka 0,10 m, grubość rosnąca 2,0 % od wpustów); U = U_śr + ΣΔU = 0,0844 W/(m²K).

**U = 0,084 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (całkowanie numeryczne (zał. C, p. C.1), siatka 0,10 m, grubość rosnąca 2,0 % od wpustów); d_min = 22,0 cm, d_max = 35,0 cm

**Założenia i dane wejściowe:**

* Grunt: piasek — λ = 2,0 W/(m·K), ρc = 2,0 MJ/(m³·K) (PN-EN ISO 13370 tab. kategorii gruntu; opinia geotechniczna przykładowa: piaski średnie) [NZW]
* f_g1 = 1,45, G_w = 1,00 (ZWG ≈ 3,8 m p.p.t. > 1 m), θ_m,e = 7,9 °C [NZW] — źródło: PN-EN 12831:2006 p. 7.1.3 i NA; rejestr W-150
* Stolarka: U_g, U_f, Ψ_g, szerokości ram, g_n — dane przykładowe typowych wyrobów (dane/wyroby_przykladowe.yaml); do zastąpienia deklaracjami wybranego producenta [DANE PRZYKŁADOWE – FIKCYJNE]
* Łączniki izolacji mocowanej mechanicznie (ETICS, elewacja wentylowana, docieplenie spodu stropu): n_f = 6,0 szt./m², χ_p = 0,002 W/K (ΔU_f = n_f·χ_p, PN-EN ISO 6946:2017 zał. F.3) [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z ETA typowego łącznika ETICS z trzpieniem stalowym, χ_p = 0,002 W/K (lub równoważny)
* Nieszczelności w warstwie izolacji: poziom 1 (ΔU'' = 0,01 W/(m²·K)), chyba że wykazano poziom 0 [NZW] — źródło: PN-EN ISO 6946:2017 zał. F.2; rejestr W-250
* Izolacja spadkowa dachu D1: grubość z modelu (22 cm) = grubość minimalna przy wpustach; przyrost wg spadku do najbliższego wpustu [ZAŁ]
* Ψ węzłów bez wyników symulacji — wartości domyślne (fallback) PN-EN ISO 14683:2017 zał. C w systemie wymiarów wewnętrznych całkowitych (Ψ_oi); do zastąpienia wynikami ISO 10211 [NZW]
* Katalog węzłów wygenerowany automatycznie z geometrii modelu (brak sekcji `wezly`) — długości sumaryczne wg typów [ZAŁ]
* Zacienienie stałe (okapy — płyty wysunięte, lamele) — F_sh z danych godzinowych TMY Poznań i położenia Słońca; model izotropowy nieba, ρ_g = 0,2 [ZAŁ] — źródło: PN-EN ISO 52016-1 p. 6.5.13 (idea); lamela.sun

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
