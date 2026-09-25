# Charakterystyka energetyczna

## Charakterystyka energetyczna — A: PC R290 + PV + rekuperacja

**Podstawa:** rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm., ost. Dz.U. 2023 poz. 697) — metoda obliczeniowa miesięczna; WT § 328–329 (EP_max); RPB § 23 pkt 11 lit. a–d

> System: pompa ciepła powietrze–woda (R290) + ogrzewanie podłogowe 35/28 °C z regulacją pokojową + c.w.u. z PC (zasobnik) + wentylacja z odzyskiem + PV.

### Współczynniki strat ciepła

| Składnik | H [W/K] |
|:---|---:|
| ściany zewnętrzne | 24,60 |
| okna i drzwi balkonowe | 35,14 |
| drzwi zewnętrzne | 2,28 |
| dachy/stropodachy | 6,13 |
| stropy nad powietrzem zewn. | 0,00 |
| grunt (f_g1·f_g2·G_w·A·U) | 5,89 |
| przestrzenie nieogrzewane (b_u) | 0,00 |
| mostki cieplne H_TB | 67,83 |
| **H_tr razem** | **141,85** |
| H_ve = 0,34·[(1 − η_oc)·V_su + V_x] (V_su = 100 m³/h, η_oc = 0,85, V_x = 26,4 m³/h) | 13,79 |

A_f = 139,52 m²; V = 376,7 m³; θ_int,H = 20,00 °C; C_m = 36,3 MJ/K; τ = 64,7 h; a_H = 5,32.

### Bilans miesięczny [kWh]

| Wielkość | I | II | III | IV | V | VI | VII | VIII | IX | X | XI | XII | Rok |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| θ_e [°C] | 0,2 | −1,8 | 2,7 | 8,3 | 13,0 | 16,8 | 18,2 | 18,4 | 13,5 | 7,0 | 2,2 | −0,1 |  |
| Q_tr | 2 094 | 2 074 | 1 823 | 1 199 | 743 | 324 | 185 | 171 | 662 | 1 371 | 1 821 | 2 126 | 14 591 |
| Q_ve | 204 | 202 | 177 | 117 | 72 | 31 | 18 | 17 | 64 | 133 | 177 | 207 | 1 418 |
| Q_int | 706 | 638 | 706 | 683 | 706 | 683 | 706 | 706 | 683 | 706 | 683 | 706 | 8 311 |
| Q_sol | 423 | 491 | 849 | 1 141 | 1 383 | 1 493 | 1 457 | 1 237 | 930 | 597 | 402 | 263 | 10 667 |
| γ | 0,49 | 0,50 | 0,78 | 1,39 | 2,56 | 6,13 | 10,67 | 10,35 | 2,22 | 0,87 | 0,54 | 0,42 |  |
| η_H,gn | 0,988 | 0,988 | 0,927 | 0,681 | 0,389 | 0,163 | 0,094 | 0,097 | 0,447 | 0,895 | 0,982 | 0,994 |  |
| Q_H,nd | 1 182 | 1 161 | 559 | 74 | 3 | 0 | 0 | 0 | 6 | 338 | 933 | 1 368 | 5 623 |
| Q_W,nd | 285 | 258 | 285 | 276 | 285 | 276 | 285 | 285 | 276 | 285 | 276 | 285 | 3 361 |
| Q_K,H | 307 | 302 | 145 | 19 | 1 | 0 | 0 | 0 | 2 | 88 | 243 | 356 | 1 463 |
| Q_K,W | 147 | 133 | 147 | 142 | 147 | 142 | 147 | 147 | 142 | 147 | 142 | 147 | 1 728 |
| E_pom | 52 | 47 | 52 | 50 | 33 | 32 | 33 | 33 | 32 | 52 | 50 | 52 | 518 |
| E_PV | 189 | 231 | 454 | 594 | 774 | 775 | 737 | 632 | 467 | 276 | 182 | 110 | 5 421 |
| a_n | 0,57 | 0,58 | 0,36 | 0,26 | 0,20 | 0,20 | 0,22 | 0,24 | 0,30 | 0,46 | 0,60 | 0,74 |  |
| E_PV,sys | 108 | 135 | 164 | 154 | 155 | 158 | 159 | 154 | 140 | 128 | 109 | 81 | 1 646 |

![Bilans miesięczny](bilans_energii.png)

### Sprawności i energia pomocnicza

| System | η_g | η_s | η_d | η_e | η_tot | Źródło |
|:---|---:|---:|---:|---:|---:|:---|
| ogrzewanie | 4,500 | 1,00 | 0,96 | 0,89 | 3,845 | SCOP = 4,50 (PN-EN 14825, dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna)); η_H,e = 0,89 (tab. 3 lp. 6b), η_H,d = 0,96 (tab. 6 lp. 3a), η_H,s = 1,00 (tab. 8 lp. 3) |
| c.w.u. | 3,200 | 0,875 | 0,80 | — | 2,239 | COP_cwu = 3,20 (PN-EN 16147); η_W,s = 0,875 (strata zasobnika 55 W); η_W,d = 0,80 (tab. 12 lp. 6.1a — cyrkulacja z ograniczeniem czasu pracy) |

| Urządzenie pomocnicze | P [W] | t [h/rok] | E [kWh/rok] | System |
|:---|---:|---:|---:|:---|
| pompa obiegowa ogrzewania podłogowego (EC) | 25,0 | 5 088 | 127 | H |
| sterownik/grzałka tacy PC (poza SCOP) | 15,0 | 8 760 | 131 | H |
| wentylatory centrali (P = SFP·q) | 28,0 | 8 760 | 245 | H |
| pompa cyrkulacyjna c.w.u. z zegarem | 5,0 | 2 920 | 15 | W |

### Wskaźniki

| Wskaźnik | Wartość | Jedn. |
|:---|---:|:---|
| Q_H,nd (ogrzewanie i wentylacja) | 5 623 | kWh/rok |
| Q_W,nd (c.w.u., wzór (61)) | 3 361 | kWh/rok |
| EU = (Q_H,nd + Q_W,nd)/A_f | 64,4 | kWh/(m²·rok) |
| Q_K = Q_K,H + Q_K,W + E_el,pom | 3 709 | kWh/rok |
| EK = Q_K/A_f | 26,6 | kWh/(m²·rok) |
| Produkcja PV / zużyta przez systemy (w = 0) | 5 421 / 1 646 | kWh/rok |
| EP_H (ogrzewanie + pomocnicze H) | 23,6 | kWh/(m²·rok) |
| EP_W (c.w.u. + pomocnicze W) | 13,4 | kWh/(m²·rok) |
| **EP = Q_p/A_f** | **37,0** | kWh/(m²·rok) |
| EP_max (WT § 329) | 70,0 | kWh/(m²·rok) |
| Wynik | ✔ spełnia |  |
| E_CO2 | 0,0082 | t CO2/(m²·rok) |
| U_oze (wzór (100)) [INT] | 80,6 | % |
| Koszt energii (eksploatacja) [ZAŁ] | 2 706 | zł/rok |

Autokonsumpcja PV (symulacja godzinowa TMY): produkcja 5 421 kWh/rok, zużyta przez systemy techniczne 1 646 kWh/rok (a = 0,30), przez urządzenia domowe 787 kWh/rok; reszta oddana do sieci (nie obniża EP).

**Założenia i dane wejściowe:**

* PC: SCOP = 4,50, COP_cwu = 3,20, udział grzałki w ogrzewaniu 0,00 % (TMY) [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna)
* Dezynfekcja termiczna c.w.u. grzałką: 227 kWh/rok (1×/tydz., 250 dm³, 55→70 °C) [ZAŁ] — źródło: WT § 120 ust. 2a; rejestr W-133
* Dane klimatyczne: typowy rok meteorologiczny ISO (PN-EN ISO 15927-4:2007), stacja Poznań (Ławica) (WMO 12330), okres 1971–2000; Ministerstwo Inwestycji i Rozwoju (archiwum) — „Dane do obliczeń energetycznych budynków”, pliki wmo123300iso.zip (godzinowy) i wmo123300iso_stat.txt (statystyki miesięczne); https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow (pobrano 2026-09-25)
* θ_int,H = 20,00 °C (średnia ważona kubaturą temperatur pomieszczeń wg WT § 134 ust. 2) — źródło: metodologia pkt 5.2.3.1.1, przypis *
* Pojemność cieplna: klasa „ciezka” — C_m = 260 kJ/(m²·K)·A_f [NZW] — źródło: PN-EN ISO 13790:2008 tab. 12
* Infiltracja przy pracy wentylatorów: V_x = V·n50·e/(1 + (f/e)·(ΔV/(V·n50))²), n50 = 1,0 h⁻¹ (cel — do potwierdzenia próbą; bez próby metodologia każe przyjąć 4 h⁻¹), e = 0,07, f = 15 [NZW] — źródło: metodologia tab. 21 i przypis do V_x,su; PN-EN ISO 13789
* Zyski słoneczne: C_i = A_g/A_w z obliczeń U_w, g_gl = 0,9·g_n, F_sh,gl = 1 (osłony ruchome podniesione w sezonie grzewczym), F_sh — zacienienie stałe z TMY [NZW] — źródło: metodologia wzór (59); PN-EN ISO 13790 p. 11.4
* Wskaźniki emisji CO2: energia elektryczna 553 kg/MWh; gaz ziemny 56,16 kg/GJ — źródło: KOBiZE, „Wskaźniki emisyjności CO2 … dla energii elektrycznej … za 2024 rok”, grudzień 2025, tab. 2 (odbiorcy końcowi); KOBiZE, „Wartości opałowe (WO) i wskaźniki emisji CO2 (WE) w roku 2023 …”, grudzień 2025, tab. 15
* Ceny energii (koszty eksploatacji, poza EP): 1,05 zł/kWh el., 0,36 zł/kWh gazu + opłaty stałe [ZAŁ] — źródło: założenie projektowe na IX 2026 (rząd wielkości taryf G11/W-3.6 dla Poznania); aktualizacja: bip.ure.gov.pl — taryfy energii elektrycznej i paliw gazowych
* PV 6,45 kWp (15 × 430 Wp), azymut 180°, nachylenie 30°, PR = 0,80; autokonsumpcja przez systemy techniczne — miesięczny współczynnik a_n z symulacji godzinowej TMY (urządzenia domowe 2500 kWh/rok konkurują o energię PV, sterowanie ładowania c.w.u. w godz. 11–15: tak) [INT] — źródło: metodologia tab. 1 lp. 6 (w = 0); R6-15 (brak wytycznych — założenie zachowawcze)

### Wrażliwość

| Wariant | EP [kWh/(m²·rok)] | EP ≤ EP_max |
|:---|:---|:---|
| A (n50 = 4 h⁻¹ — brak próby szczelności) | 45,7 | ✔ spełnia |
| A (Ψ „dobra praktyka” zamiast domyślnych PN-EN ISO 14683: H_TB = 18,3 zamiast 67,8 W/K) | 22,1 | ✔ spełnia |

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
