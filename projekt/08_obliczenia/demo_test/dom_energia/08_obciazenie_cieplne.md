# Obciążenie cieplne

## Projektowe obciążenie cieplne (PN-EN 12831-1:2017, kontrolnie PN-EN 12831:2006)

**Podstawa:** WT § 134 ust. 1–2 (θ_int), zał. 1 lp. 16; PN-EN 12831-1:2017-08 p. 6 (metoda podstawowa); PN-EN ISO 13370 (grunt), PN-EN ISO 13789 (przestrzenie nieogrzewane)

> Φ_HL,i = Φ_T,i + Φ_V,i + Φ_RH,i; Φ_V,i = 0,34·[q_inf·(θ_i − θ_e) + q_su·(θ_i − θ_su) + q_tr·(θ_i − θ_tr)].

| Pom. | Nazwa | θ_int [°C] | A [m²] | Φ_T [W] | q_inf [m³/h] | q_su [m³/h] | q_tr [m³/h] | Φ_V [W] | Φ_RH [W] | Φ_HL [W] | [W/m²] |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | Pokój dzienny | 20 | 45,3 | 1 497 | 7,3 | 59 | 0 | 160 | 0 | 1 657 | 36,6 |
| 0.02 | Łazienka | 24 | 10,8 | 584 | 1,2 | 0 | 50 | 83 | 0 | 667 | 61,9 |
| 0.03 | Kuchnia | 20 | 18,4 | 490 | 2,0 | 0 | 50 | 25 | 0 | 515 | 28,0 |
| 1.01 | Sypialnia | 20 | 51,2 | 1 302 | 5,5 | 67 | 0 | 146 | 0 | 1 448 | 28,3 |
| 1.02 | Łazienka | 24 | 14,6 | 693 | 1,6 | 0 | 50 | 89 | 0 | 782 | 53,6 |
| 1.03 | Pokój | 20 | 18,4 | 504 | 2,0 | 24 | 0 | 53 | 0 | 557 | 30,2 |
|  | **Budynek** |  | 158,7 | 5 070 |  |  |  | 430 | 0 | **5 500** | 34,7 |

θ_e = −18 °C; nawiew po odzysku θ_su = 16,6 °C (η = 0,85); n50 = 1,0 h⁻¹. Budynek: infiltracja z wsp. jednoczesności 0,5.
Przestrzeń nieogrzewana 0.04: θ_u = −13,0 °C (b_u = 0,87).

### Dobór źródła ciepła — pompa ciepła powietrze–woda

| Wielkość | Wartość |
|:---|:---|
| Projektowe obciążenie cieplne budynku Φ_HL | 5,50 kW |
| Wyrób (dane przykładowe) | Pompa ciepła powietrze–woda typu monoblok, czynnik R290, sterowanie inwerterowe — dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna) |
| Moc PC przy A−7/W35 (deklaracja) | 8,0 kW |
| Moc PC przy θ_e = −18 °C (ekstrapolacja) | 5,80 kW |
| Punkt biwalentny (P_PC = Φ(θ)) | brak — P_PC(θ_e) ≥ Φ_HL (praca monowalentna) |
| Udział grzałki w cieple sezonowym (TMY Poznań, θ < 15 °C) | 0,00 % |
| Wymagana moc grzałki przy θ_e | 0,00 kW (zainstalowana 6,0 kW) |

Charakterystyka mocy PC — interpolacja liniowa punktów A−15/A−7/A2 (W35) z karty; zapotrzebowanie liniowe względem θ_e (θ_int = 20 °C). Przygotowanie c.w.u. — priorytet z blokadą ogrzewania; zasobnik wyrównuje obciążenie (sprawdzenie czasu ładowania w PT).

### Składniki strat przez przenikanie (pomieszczenia)

**0.01 Pokój dzienny** (θ = 20 °C): Φ_T = 1 497 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O0-05 | drzwi DZ1 | 2,10 | 0,900 | 38,0 | 72 |
| W001 | sciana_zewn SZ1 | 15,94 | 0,166 | 38,0 | 100 |
| O0-04 | okno OP4 | 1,80 | 0,729 | 38,0 | 50 |
| W002 | sciana_zewn SZ1 | 22,35 | 0,166 | 38,0 | 141 |
| O0-01 | okno OP1 | 6,90 | 0,703 | 38,0 | 184 |
| W003 | sciana_zewn SZ1 | 11,14 | 0,166 | 38,0 | 70 |
| F005 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 45,34 | 0,130 | 38,0 | 104 |
| R006 | dach DZ-P0 | 20,16 | 0,104 | 38,0 | 80 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 125,73 | — | 38,0 | 696 |

**0.02 Łazienka** (θ = 24 °C): Φ_T = 584 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W007 | sciana_wewn → 0.01 (20 °C) | 8,74 | 2,037 | 4,0 | 71 |
| O0-02 | okno OP2 | 0,48 | 0,889 | 42,0 | 18 |
| W008 | sciana_zewn SZ1 | 11,69 | 0,166 | 42,0 | 81 |
| W009 | sciana_zewn SZ1 | 0,28 | 0,166 | 42,0 | 2 |
| W010 | sciana_nieogrz → 0.04 (θ_u = −13,0 °C) | 8,65 | 0,246 | 37,0 | 79 |
| W011 | sciana_wewn → 0.03 (20 °C) | 11,84 | 2,037 | 4,0 | 97 |
| F012 | grunt POD-0 (f_g1·f_g2·G_w = 0,556) | 10,77 | 0,130 | 42,0 | 33 |
| C013 | strop_wewn → 1.01 (20 °C) | 8,04 | 0,268 | 4,0 | 9 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 31,87 | — | 42,0 | 195 |

**0.03 Kuchnia** (θ = 20 °C): Φ_T = 490 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W015 | sciana_wewn → 0.02 (24 °C) | 11,84 | 2,037 | −4,0 | −97 |
| O0-06@0.03 | drzwi → 0.04 (θ_u = −13,0 °C) | 1,89 | 1,100 | 33,0 | 69 |
| W016 | sciana_nieogrz → 0.04 (θ_u = −13,0 °C) | 12,96 | 0,246 | 33,0 | 105 |
| W017 | sciana_zewn SZ1 | 0,28 | 0,166 | 38,0 | 2 |
| O0-03 | okno OP3 | 1,80 | 0,729 | 38,0 | 50 |
| W018 | sciana_zewn SZ1 | 10,37 | 0,166 | 38,0 | 65 |
| F019 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 18,41 | 0,130 | 38,0 | 42 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 45,71 | — | 38,0 | 253 |

**1.01 Sypialnia** (θ = 20 °C): Φ_T = 1 302 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W026 | sciana_zewn SZ1 | 23,73 | 0,166 | 38,0 | 149 |
| O1-01 | okno OP5 | 9,20 | 0,691 | 38,0 | 242 |
| W027 | sciana_zewn SZ1 | 6,51 | 0,166 | 38,0 | 41 |
| W029 | sciana_zewn SZ1 | 15,71 | 0,166 | 38,0 | 99 |
| F030 | strop_wewn → 0.02 (24 °C) | 8,04 | 0,268 | −4,0 | −9 |
| F031 | strop_zewn ST3 | 3,42 | 0,090 | 38,0 | 12 |
| R032 | dach SD-D1 | 51,16 | 0,082 | 38,0 | 160 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 109,74 | — | 38,0 | 608 |

**1.02 Łazienka** (θ = 24 °C): Φ_T = 693 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W033 | sciana_zewn SZ1 | 10,31 | 0,166 | 42,0 | 72 |
| W034 | sciana_wewn → 1.03 (20 °C) | 10,31 | 2,037 | 4,0 | 84 |
| W035 | sciana_wewn → 1.01 (20 °C) | 10,31 | 2,037 | 4,0 | 84 |
| O1-02 | okno OP2 | 0,48 | 0,889 | 42,0 | 18 |
| W036 | sciana_zewn SZ1 | 9,83 | 0,166 | 42,0 | 68 |
| F037 | strop_nieogrz → 0.04 (θ_u = −13,0 °C) | 7,47 | 0,101 | 37,0 | 28 |
| F038 | strop_zewn ST3 | 2,74 | 0,090 | 42,0 | 10 |
| R039 | dach SD-D1 | 14,59 | 0,082 | 42,0 | 50 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 45,43 | — | 42,0 | 278 |

**1.03 Pokój** (θ = 20 °C): Φ_T = 504 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W040 | sciana_zewn SZ1 | 10,31 | 0,166 | 38,0 | 65 |
| W042 | sciana_wewn → 1.02 (24 °C) | 10,31 | 2,037 | −4,0 | −84 |
| O1-03 | okno OP4 | 1,80 | 0,729 | 38,0 | 50 |
| W043 | sciana_zewn SZ1 | 11,21 | 0,166 | 38,0 | 71 |
| F044 | strop_nieogrz → 0.04 (θ_u = −13,0 °C) | 12,83 | 0,101 | 33,0 | 43 |
| R045 | dach SD-D1 | 18,41 | 0,082 | 38,0 | 58 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 54,57 | — | 38,0 | 302 |

**Założenia i dane wejściowe:**

* θ_e = −18 °C (strefa II, Poznań), θ_m,e = 7,9 °C [NZW] — źródło: NA do PN-EN 12831:2006; rejestr W-150
* Szczelność: n50 = 1,0 h⁻¹ (cel projektu — do potwierdzenia próbą PN-EN ISO 9972); e_i = 0,02/0,03 (osłonięcie średnie), ε = 1,0 [NZW] — źródło: PN-EN 12831:2006 tab. D.6–D.7
* Nawiew po odzysku: θ_su = θ_e + η·(θ_ex − θ_e) = 16,6 °C (η = 0,85; bez nagrzewnicy wtórnej); powietrze transferowe do łazienek o θ = 20,0 °C [ZAŁ]
* Przestrzeń nieogrzewana 0.04: θ_u = −13,0 °C, b_u = 0,87 z bilansu (n_u = 3,0 h⁻¹ — przestrzeń ze stałymi otworami wentylacyjnymi; grunt pod posadzką sprzężony z θ_m,e); b_u stosowane także w bilansie miesięcznym EP [NZW] — źródło: PN-EN ISO 13789:2017 p. 6.4 i tab. krotności dla przestrzeni nieogrzewanych

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
