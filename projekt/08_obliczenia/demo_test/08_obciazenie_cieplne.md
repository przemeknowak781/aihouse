# Obciążenie cieplne

## Projektowe obciążenie cieplne (PN-EN 12831-1:2017, kontrolnie PN-EN 12831:2006)

**Podstawa:** WT § 134 ust. 1–2 (θ_int), zał. 1 lp. 16; PN-EN 12831-1:2017-08 p. 6 (metoda podstawowa); PN-EN ISO 13370 (grunt), PN-EN ISO 13789 (przestrzenie nieogrzewane)

> Φ_HL,i = Φ_T,i + Φ_V,i + Φ_RH,i; Φ_V,i = 0,34·[q_inf·(θ_i − θ_e) + q_su·(θ_i − θ_su) + q_tr·(θ_i − θ_tr)].

| Pom. | Nazwa | θ_int [°C] | A [m²] | Φ_T [W] | q_inf [m³/h] | q_su [m³/h] | q_tr [m³/h] | Φ_V [W] | Φ_RH [W] | Φ_HL [W] | [W/m²] |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.01 | Gabinet | 20 | 17,2 | 637 | 2,8 | 20 | 0 | 73 | 0 | 710 | 41,2 |
| 0.02 | Hol ze schodami | 20 | 13,2 | 517 | 1,4 | 0 | 0 | 18 | 0 | 535 | 40,4 |
| 0.03 | Salon | 20 | 24,6 | 953 | 4,0 | 20 | 0 | 88 | 0 | 1 042 | 42,4 |
| 0.04 | Kuchnia z jadalnią | 20 | 19,0 | 661 | 3,1 | 0 | 100 | 39 | 0 | 700 | 36,9 |
| 1.01 | Sypialnia | 20 | 12,0 | 514 | 2,0 | 20 | 0 | 63 | 0 | 576 | 47,8 |
| 1.02 | Hol | 20 | 11,2 | 578 | 1,2 | 0 | 0 | 15 | 0 | 593 | 52,8 |
| 1.03 | Pokój | 20 | 24,1 | 939 | 3,9 | 20 | 0 | 88 | 0 | 1 026 | 42,5 |
| 1.04 | Garderoba | 20 | 9,4 | 352 | 1,0 | 0 | 0 | 13 | 0 | 365 | 39,0 |
| 1.05 | Sypialnia 2 | 20 | 8,7 | 239 | 0,9 | 20 | 0 | 50 | 0 | 289 | 33,2 |
|  | **Budynek** |  | 139,5 | 5 390 |  |  |  | 319 | 0 | **5 709** | 40,9 |

θ_e = −18 °C; nawiew po odzysku θ_su = 14,3 °C (η = 0,85); n50 = 1,0 h⁻¹. Budynek: infiltracja z wsp. jednoczesności 0,5.

### Dobór źródła ciepła — pompa ciepła powietrze–woda

| Wielkość | Wartość |
|:---|:---|
| Projektowe obciążenie cieplne budynku Φ_HL | 5,71 kW |
| Wyrób (dane przykładowe) | Pompa ciepła powietrze–woda typu monoblok, czynnik R290, sterowanie inwerterowe — dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna) |
| Moc PC przy A−7/W35 (deklaracja) | 8,0 kW |
| Moc PC przy θ_e = −18 °C (ekstrapolacja) | 5,80 kW |
| Punkt biwalentny (P_PC = Φ(θ)) | brak — P_PC(θ_e) ≥ Φ_HL (praca monowalentna) |
| Udział grzałki w cieple sezonowym (TMY Poznań, θ < 15 °C) | 0,00 % |
| Wymagana moc grzałki przy θ_e | 0,00 kW (zainstalowana 6,0 kW) |

Charakterystyka mocy PC — interpolacja liniowa punktów A−15/A−7/A2 (W35) z karty; zapotrzebowanie liniowe względem θ_e (θ_int = 20 °C). Przygotowanie c.w.u. — priorytet z blokadą ogrzewania; zasobnik wyrównuje obciążenie (sprawdzenie czasu ładowania w PT).

### Składniki strat przez przenikanie (pomieszczenia)

**0.01 Gabinet** (θ = 20 °C): Φ_T = 637 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O0-02 | okno OP1 | 2,70 | 0,755 | 38,0 | 77 |
| W001 | sciana_zewn SZ1 | 9,51 | 0,166 | 38,0 | 60 |
| O0-09 | okno OP3 | 2,25 | 0,706 | 38,0 | 60 |
| W004 | sciana_zewn SZ1 | 10,97 | 0,166 | 38,0 | 69 |
| F005 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 17,24 | 0,172 | 38,0 | 52 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 42,67 | — | 38,0 | 318 |

**0.02 Hol ze schodami** (θ = 20 °C): Φ_T = 517 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O0-03 | drzwi DZ1 | 2,53 | 0,900 | 38,0 | 87 |
| W008 | sciana_zewn SZ1 | 9,68 | 0,166 | 38,0 | 61 |
| W009 | sciana_zewn SZ1 | 10,16 | 0,166 | 38,0 | 64 |
| F010 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 13,25 | 0,172 | 38,0 | 40 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 35,62 | — | 38,0 | 266 |

**0.03 Salon** (θ = 20 °C): Φ_T = 953 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O0-01 | okno HS1 | 10,40 | 0,746 | 38,0 | 295 |
| W012 | sciana_zewn SZ1 | 6,71 | 0,166 | 38,0 | 42 |
| O0-05 | okno OP1 | 2,25 | 0,706 | 38,0 | 60 |
| W013 | sciana_zewn SZ1 | 11,20 | 0,166 | 38,0 | 70 |
| F014 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 24,57 | 0,172 | 38,0 | 74 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 55,12 | — | 38,0 | 411 |

**0.04 Kuchnia z jadalnią** (θ = 20 °C): Φ_T = 661 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O0-08 | okno FX1 | 2,00 | 0,729 | 38,0 | 55 |
| W015 | sciana_zewn SZ1 | 8,39 | 0,166 | 38,0 | 53 |
| O0-04 | okno OP2 | 1,92 | 0,724 | 38,0 | 53 |
| W016 | sciana_zewn SZ1 | 15,19 | 0,166 | 38,0 | 96 |
| F018 | grunt POD-0 (f_g1·f_g2·G_w = 0,462) | 18,98 | 0,172 | 38,0 | 57 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 46,47 | — | 38,0 | 347 |

**1.01 Sypialnia** (θ = 20 °C): Φ_T = 514 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O1-01 | okno OP4 | 3,84 | 0,715 | 38,0 | 104 |
| W019 | sciana_zewn SZ1 | 6,97 | 0,166 | 38,0 | 44 |
| O1-07 | okno OP8 | 2,10 | 0,713 | 38,0 | 57 |
| W022 | sciana_zewn SZ1 | 6,08 | 0,166 | 38,0 | 38 |
| R023 | dach SD-D1 | 12,05 | 0,084 | 38,0 | 39 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 31,05 | — | 38,0 | 232 |

**1.02 Hol** (θ = 20 °C): Φ_T = 578 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O1-06 | okno OP7 | 2,70 | 0,755 | 38,0 | 77 |
| W024 | sciana_zewn SZ1 | 8,11 | 0,166 | 38,0 | 51 |
| W025 | sciana_zewn SZ1 | 12,52 | 0,166 | 38,0 | 79 |
| R028 | dach SD-D1 | 18,43 | 0,084 | 38,0 | 59 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 41,77 | — | 38,0 | 312 |

**1.03 Pokój** (θ = 20 °C): Φ_T = 939 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O1-02 | okno OP5 | 8,64 | 0,684 | 38,0 | 225 |
| W031 | sciana_zewn SZ1 | 6,51 | 0,166 | 38,0 | 41 |
| O1-03 | okno HS2 | 5,52 | 0,842 | 38,0 | 177 |
| W032 | sciana_zewn SZ1 | 6,19 | 0,166 | 38,0 | 39 |
| R033 | dach SD-D1 | 24,15 | 0,084 | 38,0 | 77 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 51,00 | — | 38,0 | 381 |

**1.04 Garderoba** (θ = 20 °C): Φ_T = 352 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| W035 | sciana_zewn SZ1 | 9,00 | 0,166 | 38,0 | 57 |
| O1-04 | okno OP6 | 1,00 | 0,791 | 38,0 | 30 |
| W036 | sciana_zewn SZ1 | 6,64 | 0,166 | 38,0 | 42 |
| R038 | dach SD-D1 | 9,36 | 0,084 | 38,0 | 30 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 26,00 | — | 38,0 | 194 |

**1.05 Sypialnia 2** (θ = 20 °C): Φ_T = 239 W

| Element | Opis | A [m²] | U [W/(m²K)] | ΔT [K] | Φ [W] |
|:---|:---|---:|---:|---:|---:|
| O1-05 | okno OP3 | 2,40 | 0,701 | 38,0 | 64 |
| W039 | sciana_zewn SZ1 | 4,70 | 0,166 | 38,0 | 30 |
| R043 | dach SD-D1 | 8,70 | 0,084 | 38,0 | 28 |
| TB | mostki (H_TB rozdzielone proporcjonalnie do pola obudowy) | 15,80 | — | 38,0 | 118 |

**Założenia i dane wejściowe:**

* θ_e = −18 °C (strefa II, Poznań), θ_m,e = 7,9 °C [NZW] — źródło: NA do PN-EN 12831:2006; rejestr W-150
* Szczelność: n50 = 1,0 h⁻¹ (cel projektu — do potwierdzenia próbą PN-EN ISO 9972); e_i = 0,02/0,03 (osłonięcie średnie), ε = 1,0 [NZW] — źródło: PN-EN 12831:2006 tab. D.6–D.7
* Nawiew po odzysku: θ_su = θ_e + η·(θ_ex − θ_e) = 14,3 °C (η = 0,85; bez nagrzewnicy wtórnej); powietrze transferowe do łazienek o θ = 20,0 °C [ZAŁ]

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
