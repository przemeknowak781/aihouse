# Obliczenia U przegród — Dom LAMELA — runda 2 (Ψ z katalogu mostków w modelu)

## Współczynniki przenikania ciepła U przegród (PN-EN ISO 6946:2017)

**Podstawa:** PN-EN ISO 6946:2017-10 (p. 6.7–6.9, zał. C, zał. F); WT zał. 2 pkt 1.1 (U_C(max)); cele projektu wg rejestru W-245

> U_c = 1/R_T + ΔU_g + ΔU_f + ΔU_r; R_T = R_si + Σ d_j/λ_j + R_se (przegrody niejednorodne: R_T = (R'_T + R''_T)/2).
> Wynik U podano z dokładnością do 2 cyfr znaczących; opory — do 0,01 m²·K/W.

| Kod | Przegroda | Rola | R_T [m²K/W] | ΣΔU | U_c [W/(m²K)] | U_C(max) WT | WT | U cel | cel |
|:---|:---|:---|---:|---:|---:|---:|:---|---:|:---|
| POD-0 | Podłoga na płycie fundamentowej (P0): deska/gres, jastrych z ogrzewaniem podł., EPS 100, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm, XPS 300 20 cm, folia PE, podsypka (U_equiv = 0,11 — PN-EN ISO 13370) | podłoga na gruncie | R_f = 7,53 | 0,000 | 0,11 | 0,30 | ✔ spełnia | 0,20 | ✔ spełnia |
| POD-G | Posadzka garażu (nieogrzewany): żywica R11, jastrych cementowy zbrojony 9–14 cm (spadek 0,8 % do bramy: −0,05 przy drzwiach do domu → −0,10 przy bramie), folia PE, XPS 300 10 cm, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm obniżona (wierzch −0,30) na XPS 20 cm | podłoga na gruncie | R_f = 8,56 | 0,000 | 0,10 | — | — | — | — |
| SZ1 | Ściana zewnętrzna nośna: silikat 18 + ETICS EPS 031 20 cm (U = 0,17 z ΔU łączników — obl. PN-EN ISO 6946) | ściana zewnętrzna | 6,87 | 0,021 | 0,17 | 0,20 | ✔ spełnia | 0,15 | ✘ NIE spełnia |
| SWG | Ściana nośna dom–garaż nieogrzewany: silikat 18 + wełna 12 cm od strony garażu + tynk (U = 0,27 ≤ 0,30; szczelna na spaliny) | ściana do pom. nieogrzewanego | 3,94 | 0,020 | 0,27 | 0,30 | ✔ spełnia | 0,25 | ✘ NIE spełnia |
| DZ1 | Dach zielony ekstensywny NIEUŻYTKOWY nad garażem (pom. nieogrzewane) i pasem gospodarczym: substrat 8 cm, geowłóknina, mata drenażowa, włóknina, bariera przeciwkorzenna, 2 × papa SBS, PIR spadkowy 12–24 cm, paroizolacja, płyta ŻB 24 cm (dwukierunkowa); opaska żwirowa 0,5 m przy attykach i wpustach (U = 0,13); nad garażem: pole PV biosolarne (8 modułów) | stropodach/dach | 8,65 | 0,009 | 0,13 | 0,15 | ✔ spełnia | 0,12 | ✘ NIE spełnia |
| SD2 | Stropodach nad P1 (pola pn. poza bryłą A): żwir 5 cm, włóknina, membrana TPO, PIR spadkowy 14–26 cm, paroizolacja, płyta ŻB 22 cm (U = 0,12 — klin wg PN-EN ISO 6946 zał. C) | stropodach/dach | 9,41 | 0,009 | 0,12 | 0,15 | ✔ spełnia | 0,12 | ✔ spełnia |
| SD1 | Stropodach bryły A (P2): membrana TPO, PIR spadkowy 12–32 cm (śr. 22), paroizolacja z Al, płyta ŻB 22 cm, tynk; spadek ≥ 2 % do wpustów WP1/WP2 (U = 0,11 — klin wg PN-EN ISO 6946 zał. C) | stropodach/dach | 10,29 | 0,009 | 0,11 | 0,15 | ✔ spełnia | 0,12 | ✔ spełnia |
| SZ2 | Ściana zewnętrzna bryły A (P2) za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV-stabilna (czarna); szczelina wentylowana ok. 11 cm i lamele na ruszcie — element `lamele` (U = 0,17 — obl. PN-EN ISO 6946) | ściana zewnętrzna | 6,18 | 0,009 | 0,17 | 0,20 | ✔ spełnia | 0,15 | ✘ NIE spełnia |
| SZL | Ściana zewnętrzna lekka A' (na wsporniku P2): GK + OSB (szczelność) + szkielet KVH 45×200 z wełną + DWD + wełna fasadowa 18 cm + membrana UV (lico zewn. 0,30 m od osi — jak SZ2, ciągłość warstw w narożu); bez funkcji nośnej (U = 0,099) | ściana zewnętrzna | 10,35 | 0,002 | 0,099 | 0,20 | ✔ spełnia | 0,15 | ✔ spełnia |
| ST2Z\|P2\|zewn | podłoga POD-1 + płyta ZB_C25 22 cm + sufit SUF-ZEW | strop nad powietrzem zewn. | 8,22 | 0,005 | 0,13 | 0,15 | ✔ spełnia | — | — |

### POD-0 — Podłoga na płycie fundamentowej (P0): deska/gres, jastrych z ogrzewaniem podł., EPS 100, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm, XPS 300 20 cm, folia PE, podsypka (U_equiv = 0,11 — PN-EN ISO 13370) (podłoga na gruncie)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,00 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Deska warstwowa dębowa 15 mm, klejona | konstrukcja | 1,5 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | wykonczenie | 6,5 | 1,200 | 0,054 | jednorodna |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | izolacja | 6,5 | 0,038 | 1,711 | jednorodna |
| 4 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | przeciwwilgociowa | 0,5 | 0,230 | 0,022 | jednorodna |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 25,0 | 2,300 | 0,109 | jednorodna |
| 6 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | izolacja | 20,0 | 0,036 | 5,556 | jednorodna |
| 7 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | rozdzielajaca | 0,0 | 0,330 | 0,001 | jednorodna |
| 8 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | grunt | 20,0 | 2,000 | 0,000 | grunt — podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu) |

Opór warstw podłogi R_f = Σ R_j = 7,535 m²K/W (bez R_si, R_se i gruntu) — U podłogi na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.

**U_equiv = 0,11 W/(m²K)**; wymaganie WT: U ≤ 0,30 (✔ spełnia); cel: 0,20 (✔ spełnia).
* U_equiv wg PN-EN ISO 13370: A = 111,03 m², P = 51,21 m, B' = 4,34 m, d_t = 15,89 m

### POD-G — Posadzka garażu (nieogrzewany): żywica R11, jastrych cementowy zbrojony 9–14 cm (spadek 0,8 % do bramy: −0,05 przy drzwiach do domu → −0,10 przy bramie), folia PE, XPS 300 10 cm, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm obniżona (wierzch −0,30) na XPS 20 cm (podłoga na gruncie)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,00 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Posadzka żywiczna epoksydowa antypoślizgowa R11 (garaż) | wykonczenie | 0,3 | 0,200 | 0,015 | jednorodna |
| 2 | Jastrych cementowy CT-C30-F5 zbrojony (siatka/włókna), dylatacja obwodowa — posadzka garażu na XPS | wykonczenie | 9,2 | 1,200 | 0,077 | jednorodna |
| 3 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | rozdzielajaca | 0,0 | 0,330 | 0,001 | jednorodna |
| 4 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | izolacja | 10,0 | 0,036 | 2,778 | jednorodna |
| 5 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | przeciwwilgociowa | 0,5 | 0,230 | 0,022 | jednorodna |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 25,0 | 2,300 | 0,109 | jednorodna |
| 7 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | izolacja | 20,0 | 0,036 | 5,556 | jednorodna |
| 8 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | rozdzielajaca | 0,0 | 0,330 | 0,001 | jednorodna |
| 9 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | grunt | 20,0 | 2,000 | 0,000 | grunt — podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu) |

Opór warstw podłogi R_f = Σ R_j = 8,557 m²K/W (bez R_si, R_se i gruntu) — U podłogi na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.

**U_equiv = 0,10 W/(m²K)**; wymaganie WT: U ≤ — (—); cel: — (—).
* U_equiv wg PN-EN ISO 13370: A = 37,42 m², P = 24,56 m, B' = 3,05 m, d_t = 17,94 m

### SZ1 — Ściana zewnętrzna nośna: silikat 18 + ETICS EPS 031 20 cm (U = 0,17 z ΔU łączników — obl. PN-EN ISO 6946) (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | szczelnosc | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | konstrukcja | 18,0 | 0,900 | 0,200 | jednorodna |
| 3 | Styropian grafitowy EPS 031 (ETICS, NRO w systemie) | izolacja | 20,0 | 0,031 | 6,452 | jednorodna |
| 4 | ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (biały / jasnoszary NCS S 1500-N) | tynk | 1,0 | 0,800 | 0,012 | jednorodna |

R_T = 0,13 + Σ R_j + 0,04 = 6,872 m²K/W; U₀ = 1/R_T = 0,1455 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0088, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,1663 W/(m²K).

**U = 0,17 W/(m²K)**; wymaganie WT: U ≤ 0,20 (✔ spełnia); cel: 0,15 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].

### SWG — Ściana nośna dom–garaż nieogrzewany: silikat 18 + wełna 12 cm od strony garażu + tynk (U = 0,27 ≤ 0,30; szczelna na spaliny) (ściana do pom. nieogrzewanego)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,13 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | tynk | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | konstrukcja | 18,0 | 0,900 | 0,200 | jednorodna |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | izolacja | 12,0 | 0,035 | 3,429 | jednorodna |
| 4 | Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne) | tynk | 1,0 | 0,820 | 0,012 | jednorodna |

R_T = 0,13 + Σ R_j + 0,13 = 3,938 m²K/W; U₀ = 1/R_T = 0,2539 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0076, ΔU_f = 0,0120, ΔU_r = 0,0000 W/(m²K); U_c = 0,2735 W/(m²K).

**U = 0,27 W/(m²K)**; wymaganie WT: U ≤ 0,30 (✔ spełnia); cel: 0,25 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 2 (ściana dom–garaż) (W-243); cel: R6 3.2 [ZAŁ].

### DZ1 — Dach zielony ekstensywny NIEUŻYTKOWY nad garażem (pom. nieogrzewane) i pasem gospodarczym: substrat 8 cm, geowłóknina, mata drenażowa, włóknina, bariera przeciwkorzenna, 2 × papa SBS, PIR spadkowy 12–24 cm, paroizolacja, płyta ŻB 24 cm (dwukierunkowa); opaska żwirowa 0,5 m przy attykach i wpustach (U = 0,13); nad garażem: pole PV biosolarne (8 modułów) (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 9 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 24,0 | 2,300 | 0,104 | jednorodna |
| 8 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | paroizolacja | 0,4 | 0,230 | 0,017 | jednorodna |
| 7 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | izolacja | 18,0 | 0,022 | 8,182 | klin — grubość minimalna warstwy klinowej (zał. C) |
| 6 | Hydroizolacja 2 × papa SBS (podkładowa + wierzchniego krycia, dach zielony) | hydroizolacja | 0,9 | 0,230 | 0,041 | jednorodna |
| 5 | Bariera przeciwkorzenna PE-HD 0,5 mm (PN-EN 13948) | bariera_korzenna | 0,1 | 0,400 | 0,001 | jednorodna |
| 4 | Włóknina ochronna PP 300 g/m² | geowloknina | 0,4 | 0,500 | 0,008 | jednorodna |
| 3 | Mata drenażowo-retencyjna HDPE 25 mm (dach zielony) | drenaz | 2,5 | 0,500 | 0,050 | jednorodna |
| 2 | Geowłóknina filtracyjna PP 150 g/m² | geowloknina | 0,2 | 0,500 | 0,004 | jednorodna |
| 1 | Substrat ekstensywny 8 cm z matą rozchodnikową (sedum) | substrat | 8,0 | 0,800 | 0,100 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 8,648 m²K/W; U₀ = 1/R_T = 0,1156 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0090, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1246 W/(m²K).

Warstwa klinowa: U_śr = 0,1197 W/(m²K) (zał. C — wzór dla kształtu 'prostokat'); U = U_śr + ΣΔU = 0,1287 W/(m²K).

**U = 0,13 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 12,0 cm, d_max = 24,0 cm

### SD2 — Stropodach nad P1 (pola pn. poza bryłą A): żwir 5 cm, włóknina, membrana TPO, PIR spadkowy 14–26 cm, paroizolacja, płyta ŻB 22 cm (U = 0,12 — klin wg PN-EN ISO 6946 zał. C) (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 7 | Tynk gipsowy maszynowy 1,5 cm | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 22,0 | 2,300 | 0,096 | jednorodna |
| 5 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | paroizolacja | 0,4 | 0,230 | 0,017 | jednorodna |
| 4 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | izolacja | 20,0 | 0,022 | 9,091 | klin — grubość minimalna warstwy klinowej (zał. C) |
| 3 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | hydroizolacja | 0,2 | 0,200 | 0,010 | jednorodna |
| 2 | Włóknina ochronna PP 300 g/m² | geowloknina | 0,4 | 0,500 | 0,008 | jednorodna |
| 1 | Żwir płukany 16/32 mm (balast dachu P1, opaska przy attyce) | balast | 5,0 | 2,000 | 0,025 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 9,412 m²K/W; U₀ = 1/R_T = 0,1062 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0093, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1156 W/(m²K).

Warstwa klinowa: U_śr = 0,1094 W/(m²K) (zał. C — wzór dla kształtu 'prostokat'); U = U_śr + ΣΔU = 0,1187 W/(m²K).

**U = 0,12 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 14,0 cm, d_max = 26,0 cm

### SD1 — Stropodach bryły A (P2): membrana TPO, PIR spadkowy 12–32 cm (śr. 22), paroizolacja z Al, płyta ŻB 22 cm, tynk; spadek ≥ 2 % do wpustów WP1/WP2 (U = 0,11 — klin wg PN-EN ISO 6946 zał. C) (stropodach/dach)

Kierunek strumienia: gora; R_si = 0,10 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 5 | Tynk gipsowy maszynowy 1,5 cm | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 4 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 22,0 | 2,300 | 0,096 | jednorodna |
| 3 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | paroizolacja | 0,4 | 0,230 | 0,017 | jednorodna |
| 2 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | izolacja | 22,0 | 0,022 | 10,000 | klin — grubość minimalna warstwy klinowej (zał. C) |
| 1 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | hydroizolacja | 0,2 | 0,200 | 0,010 | jednorodna |

R_T = 0,10 + Σ R_j + 0,04 = 10,288 m²K/W; U₀ = 1/R_T = 0,0972 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0094, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1066 W/(m²K).

Warstwa klinowa: U_śr = 0,1044 W/(m²K) (zał. C — wzór dla kształtu 'prostokat'); U = U_śr + ΣΔU = 0,1138 W/(m²K).

**U = 0,11 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: 0,12 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ].
* warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 12,0 cm, d_max = 32,0 cm

### SZ2 — Ściana zewnętrzna bryły A (P2) za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV-stabilna (czarna); szczelina wentylowana ok. 11 cm i lamele na ruszcie — element `lamele` (U = 0,17 — obl. PN-EN ISO 6946) (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | szczelnosc | 1,5 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | konstrukcja | 18,0 | 0,900 | 0,200 | jednorodna |
| 3 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | izolacja | 20,0 | 0,035 | 5,714 | jednorodna |
| 4 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | wiatroizolacja | 1,0 | 0,170 | 0,059 | jednorodna |

R_T = 0,13 + Σ R_j + 0,04 = 6,181 m²K/W; U₀ = 1/R_T = 0,1618 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0085, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1703 W/(m²K).

**U = 0,17 W/(m²K)**; wymaganie WT: U ≤ 0,20 (✔ spełnia); cel: 0,15 (✘ NIE spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].

### SZL — Ściana zewnętrzna lekka A' (na wsporniku P2): GK + OSB (szczelność) + szkielet KVH 45×200 z wełną + DWD + wełna fasadowa 18 cm + membrana UV (lico zewn. 0,30 m od osi — jak SZ2, ciągłość warstw w narożu); bez funkcji nośnej (U = 0,099) (ściana zewnętrzna)

Kierunek strumienia: poziomo; R_si = 0,13 m²K/W, R_se = 0,04 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | wykonczenie | 2,5 | 0,250 | 0,100 | jednorodna |
| 2 | Płyta OSB/3 15 mm (usztywnienie i warstwa szczelności ściany A') | szczelnosc | 1,5 | 0,130 | 0,115 | jednorodna |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | izolacja | 20,0 | WELNA_035: 0,035×88 % / DREWNO_KVH: 0,130×12 % | 4,310 | niejednorodna — λ'' = Σ f_q·λ_q (kres dolny) |
| 4 | Płyta drewnopochodna wiatroizolacyjna DWD/MDF.RWH 16 mm | wiatroizolacja | 1,6 | 0,100 | 0,160 | jednorodna |
| 5 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | izolacja | 18,0 | 0,035 | 5,143 | jednorodna |
| 6 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | wiatroizolacja | 0,4 | 0,170 | 0,024 | jednorodna |

Metoda kresów (p. 6.7.2): R'_T = 10,687, R''_T = 10,022, R_T = (R'_T + R''_T)/2 = 10,355 m²K/W, e = 3,2 %.

Poprawki (zał. F): ΔU_g = 0,0025, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,0990 W/(m²K).

**U = 0,099 W/(m²K)**; wymaganie WT: U ≤ 0,20 (✔ spełnia); cel: 0,15 (✔ spełnia). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ].
* ΣΔU < 3 % U — poprawki mogłyby zostać pominięte (zał. F); przyjęto je zachowawczo

### ST2Z|P2|zewn — podłoga POD-1 + płyta ZB_C25 22 cm + sufit SUF-ZEW (strop nad powietrzem zewn.)

Kierunek strumienia: dol; R_si = 0,17 m²K/W, R_se = 0,17 m²K/W.

| Lp. | Warstwa (od ciepłej strony) | Funkcja | d [cm] | λ [W/(m·K)] | R [m²K/W] | Uwagi |
|---:|:---|:---|:---|---:|---:|:---|
| 1 | Deska warstwowa dębowa 15 mm, klejona | konstrukcja | 1,5 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | wykonczenie | 6,5 | 1,200 | 0,054 | jednorodna |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | izolacja | 4,0 | 0,038 | 1,053 | jednorodna |
| 4 | Styropian elastyfikowany EPS T (akustyczny, pod jastrychem) | izolacja | 3,0 | 0,040 | 0,750 | jednorodna |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 22,0 | 2,300 | 0,096 | jednorodna |
| 6 | Tynk gipsowy maszynowy 1,5 cm | tynk | 1,0 | 0,400 | 0,025 | jednorodna |
| 7 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | konstrukcja | 22,0 | 2,300 | 0,096 | jednorodna |
| 8 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | izolacja | 20,0 | 0,035 | 5,714 | jednorodna |
| 9 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | wiatroizolacja | 0,1 | 0,170 | 0,006 | jednorodna |
| 10 | Pustka wentylowana 40 mm (ruszt lamel) | pustka | 4,0 | — | 0,000 | pustka_dw — dobrze wentylowana — R_se := R_si, warstwy zewnętrzne pominięte (p. 6.9.4) |
| 11 | Podsufitka zewnętrzna: płyta włóknocementowa 12 mm na ruszcie, RAL 7016 | wykonczenie | 1,2 | 0,350 | — | pominieta — poza dobrze wentylowaną warstwą powietrza — pominięta (p. 6.9.4) |

R_T = 0,17 + Σ R_j + 0,17 = 8,217 m²K/W; U₀ = 1/R_T = 0,1217 W/(m²K).

Poprawki (zał. F): ΔU_g = 0,0048, ΔU_f = 0,0000, ΔU_r = 0,0000 W/(m²K); U_c = 0,1265 W/(m²K).

**U = 0,13 W/(m²K)**; wymaganie WT: U ≤ 0,15 (✔ spełnia); cel: — (—). Źródło wymagania: WT zał. 2 pkt 1.1 lp. 5 („nad przejazdami”) — spód wspornika P2 (W-243) [INT].

**Założenia i dane wejściowe:**

* Grunt: piasek — λ = 2,0 W/(m·K), ρc = 2,0 MJ/(m³·K) (PN-EN ISO 13370 tab. kategorii gruntu; opinia geotechniczna przykładowa: piaski średnie) [NZW]
* f_g1 = 1,45, G_w = 1,00 (ZWG ≈ 3,8 m p.p.t. > 1 m), θ_m,e = 7,9 °C [NZW] — źródło: PN-EN 12831:2006 p. 7.1.3 i NA; rejestr W-150
* Stolarka: U_g, U_f, Ψ_g, szerokości ram, g_n — dane przykładowe typowych wyrobów (dane/wyroby_przykladowe.yaml); do zastąpienia deklaracjami wybranego producenta [DANE PRZYKŁADOWE – FIKCYJNE]
* Łączniki ETICS: n_f = 6,0 szt./m², χ_p = 0,002 W/K (ΔU_f = n_f·χ_p, PN-EN ISO 6946:2017 zał. F.3) [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z ETA typowego łącznika ETICS z trzpieniem stalowym, χ_p = 0,002 W/K (lub równoważny)
* Nieszczelności w warstwie izolacji: poziom 1 (ΔU'' = 0,01 W/(m²·K)), chyba że wykazano poziom 0 [NZW] — źródło: PN-EN ISO 6946:2017 zał. F.2; rejestr W-250
* Zacienienie stałe (okapy — płyty wysunięte, lamele) — F_sh z danych godzinowych TMY Poznań i położenia Słońca; model izotropowy nieba, ρ_g = 0,2 [ZAŁ] — źródło: PN-EN ISO 52016-1 p. 6.5.13 (idea); lamela.sun

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
