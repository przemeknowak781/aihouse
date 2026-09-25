# Zestawienie obliczeń fizyki budowli i charakterystyki energetycznej — model testowy (dom_testowy.yaml)

Model: `model/test/dom_testowy.yaml` + `model/test/dzialka_testowa.yaml` — model TESTOWY pipeline'u (nie jest projektem Domu LAMELA).

**Status: PRZYKŁAD – NIE DO ZŁOŻENIA.** Dane wyrobów — przykładowe (typowe wyroby danej klasy, lub równoważne); wartości oznaczone [NZW] do weryfikacji na egzemplarzach norm; [ZAŁ] — założenia projektowe.

| Wielkość | Wartość | Uwagi |
|:---|:---|:---|
| A_f (pow. o regulowanej temperaturze) | 139,52 m² |  |
| Kubatura netto strefy ogrzewanej | 376,7 m³ |  |
| H_tr / H_ve | 141,9 / 13,8 W/K |  |
| H_TB (mostki) | 67,8 W/K | Ψ: deklaracja (przykładowa), domyślna |
| Obciążenie cieplne Φ_HL (θ_e = −18 °C) | 5,71 kW | 40,9 W/m² |
| Wentylacja — strumień projektowy | 100 m³/h | ✔ spełnia |
| EU / EK / EP | 64,4 / 26,6 / **37,0** kWh/(m²·rok) | EP_max = 70 — ✔ spełnia |
| U_oze / E_CO2 | 80,6 % / 1,14 t/rok |  |

## Zgodność z wymaganiami (WT zał. 2, cele projektu)

| Sprawdzenie | Wartość | Wymaganie | Wynik | Uwagi |
|:---|:---|:---|:---|:---|
| U POD-0 (grunt, PN-EN ISO 13370) | 0,17 | ≤ 0,30 | ✔ spełnia | ≤ 0,20: ✔ spełnia |
| U SZ1 (sciana_zewn) | 0,17 | ≤ 0,20 | ✔ spełnia | ≤ 0,15: ✘ NIE spełnia |
| U SD-D1 (dach) | 0,084 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✔ spełnia |
| U_w OP1 (okno) | 0,75 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP3 (okno) | 0,71 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w DZ1 (drzwi_zewn) | 0,90 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w HS1 (drzwi_przesuwne_HS) | 0,75 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w FX1 (fix) | 0,73 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP2 (okno) | 0,72 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP4 (okno) | 0,71 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP8 (okno) | 0,71 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP7 (okno) | 0,75 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP5 (okno) | 0,68 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w HS2 (drzwi_przesuwne_HS) | 0,84 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w OP6 (okno) | 0,79 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| g ≤ 0,35 (okna E/S/W) | 12/13 spełnia | WT zał. 2 pkt 2.1 | ✘ NIE spełnia | O0-08 |
| f_Rsi ≥ f_Rsi,wym | f_wym = 0,720 | WT zał. 2 pkt 2.2 | ✔ spełnia | —; bez danych: 5 węzłów (symulacja) |
| Kondensacja międzywarstwowa | 2/2 dopuszczalna | WT zał. 2 pkt 2.2.5 | ✔ spełnia | — |
| Ciągłość warstw (4 linie) | 2/3 przegród | brief § 9 | ✘ NIE spełnia | POD-0: brak izolacji przeciwwilgociowej/przeciwwodnej podłogi na gruncie (WT § 316 — ochrona przed wilgocią gruntową) |
| Izolacja obwodowa R ≥ 2,0 | brak danych | WT zał. 2 pkt 1.4 | — | energia.grunt.izolacja_obwodowa |
| EP ≤ EP_max | 37,0 | ≤ 70 (WT § 329) | ✔ spełnia | A: PC R290 + PV + rekuperacja |

## Ostrzeżenia geometrii (model)

* stolarka: symbol OP1 występuje w różnych wymiarach (1.50×1.50, 1.80×1.50) — ujednolicić zestawienie stolarki
* stolarka: symbol OP3 występuje w różnych wymiarach (1.50×1.50, 1.60×1.50) — ujednolicić zestawienie stolarki

## Pliki

* [01_przegrody_U.md](01_przegrody_U.md)
* [02_grunt.md](02_grunt.md)
* [03_stolarka_g.md](03_stolarka_g.md)
* [04_mostki.md](04_mostki.md)
* [glaser_SZ1.png](glaser_SZ1.png)
* [glaser_SD-D1.png](glaser_SD-D1.png)
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
