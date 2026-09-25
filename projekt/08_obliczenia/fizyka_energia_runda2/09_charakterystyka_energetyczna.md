# Charakterystyka energetyczna

## Charakterystyka energetyczna — A: PC R290 + PV + rekuperacja

**Podstawa:** rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm., ost. Dz.U. 2023 poz. 697) — metoda obliczeniowa miesięczna; WT § 328–329 (EP_max); RPB § 23 pkt 11 lit. a–d

> System: pompa ciepła powietrze–woda (R290) + ogrzewanie podłogowe 35/28 °C z regulacją pokojową + c.w.u. z PC (zasobnik) + wentylacja z odzyskiem + PV.

### Współczynniki strat ciepła

| Składnik | H [W/K] |
|:---|---:|
| ściany zewnętrzne | 43,80 |
| okna i drzwi balkonowe | 62,78 |
| drzwi zewnętrzne | 4,86 |
| dachy/stropodachy | 12,84 |
| stropy nad powietrzem zewn. | 0,34 |
| grunt (f_g1·f_g2·G_w·A·U) | 5,49 |
| przestrzenie nieogrzewane (b_u) | 9,91 |
| mostki cieplne H_TB | 30,63 |
| **H_tr razem** | **170,65** |
| H_ve = 0,34·[(1 − η_oc)·V_su + V_x] (V_su = 365 m³/h, η_oc = 0,85, V_x = 50,5 m³/h) | 35,08 |

A_f = 262,36 m²; V = 721,1 m³; θ_int,H = 19,95 °C; C_m = 68,2 MJ/K; τ = 92,1 h; a_H = 7,14.

### Bilans miesięczny [kWh]

| Wielkość | I | II | III | IV | V | VI | VII | VIII | IX | X | XI | XII | Rok |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| θ_e [°C] | 0,2 | −1,8 | 2,7 | 8,3 | 13,0 | 16,8 | 18,2 | 18,4 | 13,5 | 7,0 | 2,2 | −0,1 |  |
| Q_tr | 2 513 | 2 490 | 2 187 | 1 437 | 888 | 384 | 216 | 200 | 790 | 1 643 | 2 185 | 2 551 | 17 483 |
| Q_ve | 517 | 512 | 449 | 295 | 182 | 79 | 44 | 41 | 162 | 338 | 449 | 524 | 3 594 |
| Q_int | 1 327 | 1 199 | 1 327 | 1 285 | 1 327 | 1 285 | 1 327 | 1 327 | 1 285 | 1 327 | 1 285 | 1 327 | 15 628 |
| Q_sol | 751 | 826 | 1 433 | 1 751 | 2 043 | 2 177 | 2 123 | 1 844 | 1 464 | 990 | 710 | 431 | 16 542 |
| γ | 0,69 | 0,67 | 1,05 | 1,75 | 3,15 | 7,48 | 13,24 | 13,17 | 2,88 | 1,17 | 0,76 | 0,57 |  |
| η_H,gn | 0,978 | 0,980 | 0,856 | 0,566 | 0,317 | 0,134 | 0,076 | 0,076 | 0,347 | 0,799 | 0,963 | 0,992 |  |
| Q_H,nd | 998 | 1 018 | 273 | 14 | 0 | 0 | 0 | 0 | 0 | 130 | 714 | 1 332 | 4 479 |
| Q_W,nd | 537 | 485 | 537 | 519 | 537 | 519 | 537 | 537 | 519 | 537 | 519 | 537 | 6 320 |
| Q_K,H | 260 | 265 | 71 | 4 | 0 | 0 | 0 | 0 | 0 | 34 | 186 | 347 | 1 166 |
| Q_K,W | 320 | 289 | 320 | 310 | 320 | 310 | 320 | 320 | 310 | 320 | 310 | 320 | 3 769 |
| E_pom | 106 | 96 | 106 | 84 | 87 | 84 | 87 | 87 | 84 | 106 | 102 | 106 | 1 136 |
| E_PV | 149 | 195 | 388 | 543 | 733 | 753 | 715 | 596 | 426 | 242 | 148 | 97 | 4 985 |
| a_n | 0,76 | 0,71 | 0,52 | 0,43 | 0,39 | 0,39 | 0,39 | 0,42 | 0,48 | 0,58 | 0,75 | 0,83 |  |
| E_PV,sys | 114 | 138 | 203 | 236 | 286 | 291 | 282 | 251 | 204 | 141 | 111 | 81 | 2 337 |

![Bilans miesięczny](bilans_energii.png)

### Sprawności i energia pomocnicza

| System | η_g | η_s | η_d | η_e | η_tot | Źródło |
|:---|---:|---:|---:|---:|---:|:---|
| ogrzewanie | 4,496 | 1,00 | 0,96 | 0,89 | 3,842 | SCOP = 4,50 (PN-EN 14825, dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna)); η_H,e = 0,89 (tab. 3 lp. 6b), η_H,d = 0,96 (tab. 6 lp. 3a), η_H,s = 1,00 (tab. 8 lp. 3); grzałka 0,02 % |
| c.w.u. | 3,200 | 0,929 | 0,60 | — | 1,784 | COP_cwu = 3,20 (PN-EN 16147); η_W,s = 0,929 (strata zasobnika 55 W); η_W,d = 0,60 (tab. 12 lp. 6.1a — cyrkulacja z ograniczeniem czasu pracy) |

| Urządzenie pomocnicze | P [W] | t [h/rok] | E [kWh/rok] | System |
|:---|---:|---:|---:|:---|
| pompa obiegowa ogrzewania podłogowego (EC) | 25,0 | 4 368 | 109 | H |
| sterownik/grzałka tacy PC (poza SCOP) | 15,0 | 8 760 | 131 | H |
| wentylatory centrali (P = SFP·q) | 102,2 | 8 760 | 895 | H |

### Wskaźniki

| Wskaźnik | Wartość | Jedn. |
|:---|---:|:---|
| Q_H,nd (ogrzewanie i wentylacja) | 4 479 | kWh/rok |
| Q_W,nd (c.w.u., wzór (61)) | 6 320 | kWh/rok |
| EU = (Q_H,nd + Q_W,nd)/A_f | 41,2 | kWh/(m²·rok) |
| Q_K = Q_K,H + Q_K,W + E_el,pom | 6 071 | kWh/rok |
| EK = Q_K/A_f | 23,1 | kWh/(m²·rok) |
| Produkcja PV / zużyta przez systemy (w = 0) | 4 985 / 2 337 | kWh/rok |
| EP_H (ogrzewanie + pomocnicze H) | 15,4 | kWh/(m²·rok) |
| EP_W (c.w.u. + pomocnicze W) | 20,2 | kWh/(m²·rok) |
| **EP = Q_p/A_f** | **35,6** | kWh/(m²·rok) |
| EP_max (WT § 329) | 70,0 | kWh/(m²·rok) |
| Wynik | ✔ spełnia |  |
| E_CO2 | 0,0079 | t CO2/(m²·rok) |
| U_oze (wzór (100)) [INT] | 74,7 | % |
| Koszt energii (eksploatacja) [ZAŁ] | 4 461 | zł/rok |

Autokonsumpcja PV (symulacja godzinowa TMY): produkcja 4 985 kWh/rok, zużyta przez systemy techniczne 2 337 kWh/rok (a = 0,47), przez urządzenia domowe 695 kWh/rok; reszta oddana do sieci (nie obniża EP).

**Założenia i dane wejściowe:**

* PC: SCOP = 4,50, COP_cwu = 3,20, udział grzałki w ogrzewaniu 0,02 % (TMY) [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna)
* Dezynfekcja termiczna c.w.u. grzałką: 227 kWh/rok (1×/tydz., 250 dm³, 55→70 °C) [ZAŁ] — źródło: WT § 120 ust. 2a; rejestr W-133
* Dane klimatyczne: typowy rok meteorologiczny ISO (PN-EN ISO 15927-4:2007), stacja Poznań (Ławica) (WMO 12330), okres 1971–2000; Ministerstwo Inwestycji i Rozwoju (archiwum) — „Dane do obliczeń energetycznych budynków”, pliki wmo123300iso.zip (godzinowy) i wmo123300iso_stat.txt (statystyki miesięczne); https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow (pobrano 2026-09-25)
* θ_int,H = 19,95 °C (średnia ważona kubaturą temperatur pomieszczeń wg WT § 134 ust. 2) — źródło: metodologia pkt 5.2.3.1.1, przypis *
* Pojemność cieplna: klasa „ciezka” — C_m = 260 kJ/(m²·K)·A_f [NZW] — źródło: PN-EN ISO 13790:2008 tab. 12
* Infiltracja przy pracy wentylatorów: V_x = V·n50·e/(1 + (f/e)·(ΔV/(V·n50))²), n50 = 1,0 h⁻¹ (cel — do potwierdzenia próbą; bez próby metodologia każe przyjąć 4 h⁻¹), e = 0,07, f = 15 [NZW] — źródło: metodologia tab. 21 i przypis do V_x,su; PN-EN ISO 13789
* Zyski słoneczne: C_i = A_g/A_w z obliczeń U_w, g_gl = 0,9·g_n, F_sh,gl = 1 (osłony ruchome podniesione w sezonie grzewczym), F_sh — zacienienie stałe z TMY [NZW] — źródło: metodologia wzór (59); PN-EN ISO 13790 p. 11.4
* Wskaźniki emisji CO2: energia elektryczna 553 kg/MWh; gaz ziemny 56,16 kg/GJ — źródło: KOBiZE, „Wskaźniki emisyjności CO2 … dla energii elektrycznej … za 2024 rok”, grudzień 2025, tab. 2 (odbiorcy końcowi); KOBiZE, „Wartości opałowe (WO) i wskaźniki emisji CO2 (WE) w roku 2023 …”, grudzień 2025, tab. 15
* Ceny energii (koszty eksploatacji, poza EP): 1,05 zł/kWh el., 0,36 zł/kWh gazu + opłaty stałe [ZAŁ] — źródło: założenie projektowe na IX 2026 (rząd wielkości taryf G11/W-3.6 dla Poznania); aktualizacja: bip.ure.gov.pl — taryfy energii elektrycznej i paliw gazowych
* PV 6,45 kWp (15 × 430 Wp), azymut 180°, nachylenie 10°, PR = 0,78; autokonsumpcja przez systemy techniczne — miesięczny współczynnik a_n z symulacji godzinowej TMY (urządzenia domowe 2500 kWh/rok konkurują o energię PV, sterowanie ładowania c.w.u. w godz. 11–15: tak) [INT] — źródło: metodologia tab. 1 lp. 6 (w = 0); R6-15 (brak wytycznych — założenie zachowawcze)

### Wrażliwość

| Wariant | EP [kWh/(m²·rok)] | EP ≤ EP_max |
|:---|:---|:---|
| A (n50 = 4 h⁻¹ — brak próby szczelności) | 44,1 | ✔ spełnia |

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
