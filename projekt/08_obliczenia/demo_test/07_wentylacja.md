# Wentylacja

## Wentylacja mechaniczna z odzyskiem ciepła — bilans powietrza i dobór centrali

**Podstawa:** PN-83/B-03430/Az3:2000 (przez WT § 147 ust. 1, § 149 ust. 1) [NZW]; WT § 148–154; rozp. (UE) 1253/2014

> Źródło strumieni: bilans projektowy (minima PN-83/B-03430/Az3 + nawiew 20 m³/h·os., rozdział nawiewu proporcjonalnie do powierzchni pokoi, min. 20 m³/h na pokój).

| Pom. | Nazwa | Rodzaj | A [m²] | V [m³] | Wywiew min [m³/h] | Wywiew [m³/h] | Nawiew [m³/h] | Transfer [m³/h] | n [h⁻¹] | Podstawa wywiewu |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| 0.01 | Gabinet | pokoj | 17,2 | 46,5 | 0 | 0 | 20 | 0 | 0,43 | — |
| 0.02 | Hol ze schodami | komunikacja | 13,2 | 35,8 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.03 | Salon | pokoj | 24,6 | 66,3 | 0 | 0 | 20 | 0 | 0,30 | — |
| 0.04 | Kuchnia z jadalnią | kuchnia | 19,0 | 51,2 | 50 | 100 | 0 | 100 | 1,95 | kuchnia z kuchenką elektryczną, > 3 osób |
| 1.01 | Sypialnia | pokoj | 12,0 | 32,5 | 0 | 0 | 20 | 0 | 0,61 | — |
| 1.02 | Hol | komunikacja | 11,2 | 30,3 | 0 | 0 | 0 | 0 | 0,00 | — |
| 1.03 | Pokój | pokoj | 24,1 | 65,2 | 0 | 0 | 20 | 0 | 0,31 | — |
| 1.04 | Garderoba | pomocnicze | 9,4 | 25,3 | 0 | 0 | 0 | 0 | 0,00 | — |
| 1.05 | Sypialnia 2 | pokoj | 8,7 | 23,5 | 0 | 0 | 20 | 0 | 0,85 | — |
|  | **Razem** |  |  |  | 50 | 100 | 100 |  |  |  |

Strumień projektowy q = max(Σ nawiewu; Σ wywiewu) = **100 m³/h**; okresowo (kuchnia 120 m³/h) 120 m³/h. Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 % — V_nom = 450 m³/h, η_t = 0,85, P_el = SFP·q = 28 W; kanał główny Ø125 mm (v ≤ 3 m/s).

| Sprawdzenie | Wartość | Wynik |
|:---|:---|:---|
| Nawiew ≥ 20 m³/h·os. (WT § 149 ust. 1) | 100 ≥ 100 m³/h | ✔ spełnia |
| Wywiew ≥ minima PN-B-03430/Az3 (WT § 149 ust. 1) | 100 ≥ 50 m³/h | ✔ spełnia |
| Bilans nawiew = wywiew (±10 %) | 100 / 100 m³/h | ✔ spełnia |
| Wydajność centrali ≥ strumień okresowy (kuchnia 120 m³/h) | 500 ≥ 120 m³/h | ✔ spełnia |
| Odzysk ciepła ≥ 50 % (WT § 151 — obowiązkowy od 500 m³/h) | q = 100 m³/h; η = 0,85 | ✔ spełnia |
| Odzysk ciepła ≥ cel projektu 0,85 [ZAŁ] | η = 0,85 | ✔ spełnia |
| SFP nawiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,90 kW/(m³/s) | ✔ spełnia |
| SFP wywiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,30 kW/(m³/s) | ✔ spełnia |
| Ekoprojekt (UE) 1253/2014: SEC ≤ −20 kWh/(m²·a), by-pass, napęd wielobiegowy | SEC = −40 kWh/(m²·a) (klasa A) | ✔ spełnia |
| Czerpnia/wyrzutnia — położenie (WT § 152) | [DO UZUPEŁNIENIA] energia.wentylacja.czerpnia/wyrzutnia | — |

* Strumienie w modelu (`went`) nie spełniają minimów lub bilansu — przyjęto bilans projektowy (poniżej); do przeniesienia do modelu.

**Założenia i dane wejściowe:**

* Liczba osób: 5 [PROG] — źródło: brief §4; wymagania.yaml wentylacja.liczba_osob
* Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 %; η_t = 0,85, SFP = 0,28 Wh/m³ [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z karty katalogowej typowej centrali mieszkaniowej 450 m³/h klasy SEC A (lub równoważna)
* Podział mocy wentylatorów nawiew/wywiew 50/50 do sprawdzenia SFP [ZAŁ]

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
