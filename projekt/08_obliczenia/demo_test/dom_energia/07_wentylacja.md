# Wentylacja

## Wentylacja mechaniczna z odzyskiem ciepła — bilans powietrza i dobór centrali

**Podstawa:** PN-83/B-03430/Az3:2000 (przez WT § 147 ust. 1, § 149 ust. 1) [NZW]; WT § 148–154; rozp. (UE) 1253/2014

> Źródło strumieni: bilans projektowy (minima PN-83/B-03430/Az3 + nawiew 20 m³/h·os., rozdział nawiewu proporcjonalnie do powierzchni pokoi, min. 20 m³/h na pokój).

| Pom. | Nazwa | Rodzaj | A [m²] | V [m³] | Wywiew min [m³/h] | Wywiew [m³/h] | Nawiew [m³/h] | Transfer [m³/h] | n [h⁻¹] | Podstawa wywiewu |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| 0.01 | Pokój dzienny | pokoj | 45,3 | 122,0 | 0 | 0 | 59 | 0 | 0,49 | — |
| 0.02 | Łazienka | lazienka | 10,8 | 29,0 | 50 | 50 | 0 | 50 | 1,73 | łazienka |
| 0.03 | Kuchnia | kuchnia | 18,4 | 49,5 | 50 | 50 | 0 | 50 | 1,01 | kuchnia z kuchenką elektryczną, > 3 osób |
| 1.01 | Sypialnia | pokoj | 51,2 | 137,6 | 0 | 0 | 67 | 0 | 0,49 | — |
| 1.02 | Łazienka | lazienka | 14,6 | 39,3 | 50 | 50 | 0 | 50 | 1,27 | łazienka |
| 1.03 | Pokój | pokoj | 18,4 | 49,5 | 0 | 0 | 24 | 0 | 0,49 | — |
|  | **Razem** |  |  |  | 150 | 150 | 150 |  |  |  |

Strumień projektowy q = max(Σ nawiewu; Σ wywiewu) = **150 m³/h**; okresowo (kuchnia 120 m³/h) 220 m³/h. Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 % — V_nom = 450 m³/h, η_t = 0,85, P_el = SFP·q = 42 W; kanał główny Ø160 mm (v ≤ 3 m/s).

| Sprawdzenie | Wartość | Wynik |
|:---|:---|:---|
| Nawiew ≥ 20 m³/h·os. (WT § 149 ust. 1) | 150 ≥ 80 m³/h | ✔ spełnia |
| Wywiew ≥ minima PN-B-03430/Az3 (WT § 149 ust. 1) | 150 ≥ 150 m³/h | ✔ spełnia |
| Bilans nawiew = wywiew (±10 %) | 150 / 150 m³/h | ✔ spełnia |
| Wydajność centrali ≥ strumień okresowy (kuchnia 120 m³/h) | 500 ≥ 220 m³/h | ✔ spełnia |
| Odzysk ciepła ≥ 50 % (WT § 151 — obowiązkowy od 500 m³/h) | q = 150 m³/h; η = 0,85 | ✔ spełnia |
| Odzysk ciepła ≥ cel projektu 0,85 [ZAŁ] | η = 0,85 | ✔ spełnia |
| SFP nawiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,90 kW/(m³/s) | ✔ spełnia |
| SFP wywiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,30 kW/(m³/s) | ✔ spełnia |
| Ekoprojekt (UE) 1253/2014: SEC ≤ −20 kWh/(m²·a), by-pass, napęd wielobiegowy | SEC = −40 kWh/(m²·a) (klasa A) | ✔ spełnia |
| Czerpnia–wyrzutnia na dachu ≥ 6 m, wyrzutnia ≥ 1 m wyżej (wyrzut pionowy, WT § 152 ust. 10) | 6,50 m; Δz = 1,10 m | ✔ spełnia |
| Garaż 0.04: otwory wentylacji naturalnej ≥ 0,04 m²/stanowisko (WT § 108 ust. 1 pkt 1) | 0,100 ≥ 0,08 m² (2 stan.) | ✔ spełnia |
| Garaż 0.04: bez podłączenia do rekuperacji (R6 3.5) | wentylacja naturalna | ✔ spełnia |


**Założenia i dane wejściowe:**

* Liczba osób: 4 [PROG] — źródło: brief §4; wymagania.yaml wentylacja.liczba_osob
* Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 %; η_t = 0,85, SFP = 0,28 Wh/m³ [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z karty katalogowej typowej centrali mieszkaniowej 450 m³/h klasy SEC A (lub równoważna)
* Podział mocy wentylatorów nawiew/wywiew 50/50 do sprawdzenia SFP [ZAŁ]

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
