# Zestawienie obliczeń fizyki budowli i charakterystyki energetycznej — model testowy energii (garaż, wspornik, dach zielony)

Model: `tools/test_obliczenia_dane/dom_energia.yaml` — model TESTOWY biblioteki (nie jest projektem Domu LAMELA).

**Status: PRZYKŁAD – NIE DO ZŁOŻENIA.** Dane wyrobów — przykładowe (typowe wyroby danej klasy, lub równoważne); wartości oznaczone [NZW] do weryfikacji na egzemplarzach norm; [ZAŁ] — założenia projektowe.

| Wielkość | Wartość | Uwagi |
|:---|:---|:---|
| A_f (pow. o regulowanej temperaturze) | 158,69 m² |  |
| Kubatura netto strefy ogrzewanej | 426,9 m³ |  |
| H_tr / H_ve | 126,8 / 17,5 W/K |  |
| H_TB (mostki) | 60,2 W/K | Ψ: domyślna, przykładowa |
| Obciążenie cieplne Φ_HL (θ_e = −18 °C) | 5,49 kW | 34,6 W/m² |
| Wentylacja — strumień projektowy | 150 m³/h | ✔ spełnia |
| EU / EK / EP | 59,7 / 25,3 / **39,6** kWh/(m²·rok) | EP_max = 70 — ✔ spełnia |
| U_oze / E_CO2 | 76,9 % / 1,39 t/rok |  |

## Zgodność z wymaganiami (WT zał. 2, cele projektu)

| Sprawdzenie | Wartość | Wymaganie | Wynik | Uwagi |
|:---|:---|:---|:---|:---|
| U POD-0 (grunt, PN-EN ISO 13370) | 0,13 | ≤ 0,30 | ✔ spełnia | ≤ 0,20: ✔ spełnia |
| U SZ1 (sciana_zewn) | 0,17 | ≤ 0,20 | ✔ spełnia | ≤ 0,15: ✘ NIE spełnia |
| U DZ-P0 (dach) | 0,10 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✔ spełnia |
| U SWG (sciana_nieogrz) | 0,23 | ≤ 0,30 | ✔ spełnia | ≤ 0,25: ✔ spełnia |
| U ST3\|P1\|zewn (strop_zewn) | 0,090 | ≤ 0,15 | ✔ spełnia | — |
| U SD-D1 (dach) | 0,082 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✔ spełnia |
| U ST2\|P1\|dol (strop_nieogrz) | 0,10 | ≤ 0,25 | ✔ spełnia | — |
| U_w DZ1 (drzwi_zewn) | 0,90 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w OP4 (okno) | 0,73 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP1 (okno) | 0,70 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP2 (okno) | 0,89 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w DG1 (drzwi) | 1,1 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w OP3 (okno) | 0,73 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP5 (okno) | 0,69 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| g ≤ 0,35 (okna E/S/W) | 7/7 spełnia | WT zał. 2 pkt 2.1 | ✔ spełnia | — |
| f_Rsi ≥ f_Rsi,wym | f_wym = 0,720 | WT zał. 2 pkt 2.2 | ✘ NIE spełnia | SZG, SD-G; bez danych: 7 węzłów (symulacja) |
| Kondensacja międzywarstwowa | 6/6 dopuszczalna | WT zał. 2 pkt 2.2.5 | ✔ spełnia | — |
| Ciągłość warstw (4 linie) | 7/7 przegród | brief § 9 | ✔ spełnia | — |
| Izolacja obwodowa R ≥ 2,0 | 4,29 | WT zał. 2 pkt 1.4 | ✔ spełnia |  |
| EP ≤ EP_max | 39,6 | ≤ 70 (WT § 329) | ✔ spełnia | A: PC R290 + PV + rekuperacja |

## Pliki

* [01_przegrody_U.md](01_przegrody_U.md)
* [02_grunt.md](02_grunt.md)
* [03_stolarka_g.md](03_stolarka_g.md)
* [04_mostki.md](04_mostki.md)
* [glaser_SZ1.png](glaser_SZ1.png)
* [glaser_DZ-P0.png](glaser_DZ-P0.png)
* [glaser_SWG.png](glaser_SWG.png)
* [glaser_ST3_P1_zewn.png](glaser_ST3_P1_zewn.png)
* [glaser_SD-D1.png](glaser_SD-D1.png)
* [glaser_ST2_P1_dol.png](glaser_ST2_P1_dol.png)
* [05_wilgotnosc.md](05_wilgotnosc.md)
* [06_ciaglosc_warstw.md](06_ciaglosc_warstw.md)
* [07_wentylacja.md](07_wentylacja.md)
* [08_obciazenie_cieplne.md](08_obciazenie_cieplne.md)
* [bilans_energii.png](bilans_energii.png)
* [09_charakterystyka_energetyczna.md](09_charakterystyka_energetyczna.md)
* [10_analiza_alternatyw.md](10_analiza_alternatyw.md)

Dane klimatyczne: typowy rok meteorologiczny ISO (PN-EN ISO 15927-4:2007), stacja Poznań (Ławica) (WMO 12330), okres 1971–2000; Ministerstwo Inwestycji i Rozwoju (archiwum) — „Dane do obliczeń energetycznych budynków”, pliki wmo123300iso.zip (godzinowy) i wmo123300iso_stat.txt (statystyki miesięczne); https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow (pobrano 2026-09-25).
---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
