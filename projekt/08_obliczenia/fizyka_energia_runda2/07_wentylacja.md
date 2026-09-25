# Wentylacja

## Wentylacja mechaniczna z odzyskiem ciepła — bilans powietrza i dobór centrali

**Podstawa:** PN-83/B-03430/Az3:2000 (przez WT § 147 ust. 1, § 149 ust. 1) [NZW]; WT § 148–154; rozp. (UE) 1253/2014

> Źródło strumieni: strumienie z modelu (`pomieszczenia[].went`) — sprawdzone: minima, bilans ±10 %, 20 m³/h·os..

| Pom. | Nazwa | Rodzaj | A [m²] | V [m³] | Wywiew min [m³/h] | Wywiew [m³/h] | Nawiew [m³/h] | Transfer [m³/h] | n [h⁻¹] | Podstawa wywiewu |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| 0.01 | Wiatrołap | komunikacja | 3,9 | 10,8 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.02 | Hol | komunikacja | 4,4 | 12,3 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.03 | WC gościnne | wc | 2,3 | 6,4 | 30 | 30 | 0 | 30 | 4,66 | wydzielony WC |
| 0.04 | Klatka schodowa | komunikacja | 2,8 | 7,7 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.05 | Spiżarnia | pomocnicze | 1,0 | 2,8 | 15 | 15 | 0 | 15 | 5,32 | pomieszczenie pomocnicze bezokienne |
| 0.15 | Schowek pod schodami (h 1,40–2,20) | strefa_spizarni | 1,4 | 2,6 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.16 | Schowek pod spocznikiem (h < 1,40) | strefa_spizarni | 2,9 | 4,0 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.06 | Salon + jadalnia + kuchnia | kuchnia | 54,4 | 150,8 | 50 | 50 | 90 | 0 | 0,60 | kuchnia z kuchenką elektryczną, > 3 osób |
| 0.07 | Pas komunikacyjny przy schodach | komunikacja | 3,5 | 9,7 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.08 | Przedpokój gościnny | komunikacja | 1,4 | 4,0 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.09 | Łazienka gościnna (natrysk) | lazienka | 3,8 | 10,6 | 50 | 50 | 0 | 50 | 4,70 | łazienka |
| 0.10 | Pokój gościnny / gabinet | pokoj | 12,5 | 34,7 | 0 | 0 | 40 | 0 | 1,15 | — |
| 0.11 | Przedsionek gospodarczy | komunikacja | 7,2 | 19,8 | 0 | 0 | 0 | 0 | 0,00 | — |
| 0.12 | Pomieszczenie techniczne | techniczne | 8,8 | 24,4 | 15 | 15 | 0 | 15 | 0,61 | pomieszczenie pomocnicze bezokienne |
| 1.01 | Hol | komunikacja | 14,1 | 39,0 | 0 | 0 | 0 | 0 | 0,00 | — |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | pokoj | 28,4 | 78,6 | 0 | 0 | 50 | 0 | 0,64 | — |
| 1.03 | Pokój dziecka 1 | pokoj | 13,2 | 36,5 | 0 | 0 | 40 | 0 | 1,09 | — |
| 1.04 | Pokój dziecka 2 | pokoj | 12,5 | 34,7 | 0 | 0 | 40 | 0 | 1,15 | — |
| 1.05 | Łazienka dzieci (wanna) | lazienka | 5,5 | 15,2 | 50 | 50 | 0 | 50 | 3,28 | łazienka |
| 1.06 | Klatka schodowa | komunikacja | 0,5 | 1,4 | 0 | 0 | 0 | 0 | 0,00 | — |
| 1.07 | WC z natryskiem | lazienka | 4,1 | 11,3 | 50 | 50 | 0 | 50 | 4,42 | łazienka |
| 1.08 | Pralnia z suszarnią | pralnia | 6,6 | 18,4 | 37 | 40 | 0 | 40 | 2,17 | pralnia ≥ 2 h⁻¹ |
| 2.01 | Hol | komunikacja | 5,7 | 15,9 | 0 | 0 | 0 | 0 | 0,00 | — |
| 2.02 | Sypialnia rodziców | pokoj | 21,4 | 59,4 | 0 | 0 | 60 | 0 | 1,01 | — |
| 2.03 | Garderoba (przedpokój apartamentu) | pomocnicze | 10,5 | 29,1 | 0 | 0 | 0 | 0 | 0,00 | — |
| 2.04 | Łazienka rodziców | lazienka | 5,5 | 15,3 | 50 | 50 | 0 | 50 | 3,28 | łazienka |
| 2.05 | Gabinet / pokój gościnny okazjonalny | pokoj | 16,2 | 45,0 | 0 | 0 | 45 | 0 | 1,00 | — |
| 2.06 | Klatka schodowa (wyjście z biegu 2, pustka) | komunikacja | 0,2 | 0,7 | 0 | 0 | 0 | 0 | 0,00 | — |
| 2.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | techniczne | 5,9 | 16,4 | 15 | 15 | 0 | 15 | 0,92 | pomieszczenie pomocnicze bezokienne |
| 0.14 | Szacht instalacyjny SI | szacht | 0,4 | 1,2 | 0 | 0 | 0 | 0 | 0,00 | — |
| 1.09 | Szacht instalacyjny SI | szacht | 0,4 | 1,2 | 0 | 0 | 0 | 0 | 0,00 | — |
| 2.08 | Szacht instalacyjny SI | szacht | 0,4 | 1,2 | 0 | 0 | 0 | 0 | 0,00 | — |
|  | **Razem** |  |  |  | 362 | 365 | 365 |  |  |  |

Strumień projektowy q = max(Σ nawiewu; Σ wywiewu) = **365 m³/h**; okresowo (kuchnia 120 m³/h) 435 m³/h. Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 % — V_nom = 450 m³/h, η_t = 0,85, P_el = SFP·q = 102 W; kanał główny Ø250 mm (v ≤ 3 m/s).

| Sprawdzenie | Wartość | Wynik |
|:---|:---|:---|
| Nawiew ≥ 20 m³/h·os. (WT § 149 ust. 1) | 365 ≥ 100 m³/h | ✔ spełnia |
| Wywiew ≥ minima PN-B-03430/Az3 (WT § 149 ust. 1) | 365 ≥ 362 m³/h | ✔ spełnia |
| Bilans nawiew = wywiew (±10 %) | 365 / 365 m³/h | ✔ spełnia |
| Wydajność centrali ≥ strumień okresowy (kuchnia 120 m³/h) | 500 ≥ 435 m³/h | ✔ spełnia |
| Odzysk ciepła ≥ 50 % (WT § 151 — obowiązkowy od 500 m³/h) | q = 365 m³/h; η = 0,85 | ✔ spełnia |
| Odzysk ciepła ≥ cel projektu 0,85 [ZAŁ] | η = 0,85 | ✔ spełnia |
| SFP nawiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,90 kW/(m³/s) | ✔ spełnia |
| SFP wywiewu z odzyskiem (WT § 154 ust. 10–11) | 0,50 ≤ 1,30 kW/(m³/s) | ✔ spełnia |
| Ekoprojekt (UE) 1253/2014: SEC ≤ −20 kWh/(m²·a), by-pass, napęd wielobiegowy | SEC = −40 kWh/(m²·a) (klasa A) | ✔ spełnia |
| Czerpnia dachowa ≥ 6 m od wywiewek (WT § 152 ust. 4) | 7,96 m | ✔ spełnia |
| Czerpnia dachowa ≥ 6 m od wywiewek (WT § 152 ust. 4) | 6,59 m | ✔ spełnia |
| Czerpnia–wyrzutnia ≥ 10 m (wyrzut poziomy, WT § 152 ust. 10) | 10,15 m | ✔ spełnia |
| Garaż 0.13: otwory wentylacji naturalnej ≥ 0,04 m²/stanowisko (WT § 108 ust. 1 pkt 1) | 0,100 ≥ 0,08 m² (2 stan.) | ✔ spełnia |
| Garaż 0.13: bez podłączenia do rekuperacji (R6 3.5) | wentylacja naturalna | ✔ spełnia |


**Założenia i dane wejściowe:**

* Liczba osób: 5 [PROG] — źródło: brief §4; wymagania.yaml wentylacja.liczba_osob
* Centrala: Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 %; η_t = 0,85, SFP = 0,28 Wh/m³ [DANE PRZYKŁADOWE – FIKCYJNE] — źródło: dane przykładowe z karty katalogowej typowej centrali mieszkaniowej 450 m³/h klasy SEC A (lub równoważna)
* Podział mocy wentylatorów nawiew/wywiew 50/50 do sprawdzenia SFP [ZAŁ]

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
