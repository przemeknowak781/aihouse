# Zestawienie obliczeń fizyki budowli i charakterystyki energetycznej — Dom LAMELA — runda 2 (Ψ z katalogu mostków w modelu)

Model: `model/budynek.yaml` + `model/dzialka.yaml`

**Status: PRZYKŁAD – NIE DO ZŁOŻENIA.** Dane wyrobów — przykładowe (typowe wyroby danej klasy, lub równoważne); wartości oznaczone [NZW] do weryfikacji na egzemplarzach norm; [ZAŁ] — założenia projektowe.

| Wielkość | Wartość | Uwagi |
|:---|:---|:---|
| A_f (pow. o regulowanej temperaturze) | 262,36 m² |  |
| Kubatura netto strefy ogrzewanej | 721,1 m³ |  |
| H_tr / H_ve | 170,6 / 35,1 W/K |  |
| H_TB (mostki) | 30,6 W/K | Ψ: przykładowa, — |
| Obciążenie cieplne Φ_HL (θ_e = −18 °C) | 7,41 kW | 28,2 W/m² |
| Wentylacja — strumień projektowy | 365 m³/h | ✔ spełnia |
| EU / EK / EP | 41,2 / 23,1 / **35,6** kWh/(m²·rok) | EP_max = 70 — ✔ spełnia |
| U_oze / E_CO2 | 74,7 % / 2,07 t/rok |  |

## Zgodność z wymaganiami (WT zał. 2, cele projektu)

| Sprawdzenie | Wartość | Wymaganie | Wynik | Uwagi |
|:---|:---|:---|:---|:---|
| U POD-0 (grunt, PN-EN ISO 13370) | 0,11 | ≤ 0,30 | ✔ spełnia | ≤ 0,20: ✔ spełnia |
| U SZ1 (sciana_zewn) | 0,17 | ≤ 0,20 | ✔ spełnia | ≤ 0,15: ✘ NIE spełnia |
| U SWG (sciana_nieogrz) | 0,27 | ≤ 0,30 | ✔ spełnia | ≤ 0,25: ✘ NIE spełnia |
| U DZ1 (dach) | 0,13 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✘ NIE spełnia |
| U SD2 (dach) | 0,12 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✔ spełnia |
| U SD1 (dach) | 0,11 | ≤ 0,15 | ✔ spełnia | ≤ 0,12: ✔ spełnia |
| U SZ2 (sciana_zewn) | 0,17 | ≤ 0,20 | ✔ spełnia | ≤ 0,15: ✘ NIE spełnia |
| U SZL (sciana_zewn) | 0,099 | ≤ 0,20 | ✔ spełnia | ≤ 0,15: ✔ spełnia |
| U ST2Z\|P2\|zewn (strop_zewn) | 0,13 | ≤ 0,15 | ✔ spełnia | — |
| U_w DZ1 (drzwi_zewn) | 0,90 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w FX3 (fix) | 0,87 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w DG1 (drzwi) | 1,1 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w FX1 (fix) | 0,64 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w HS1 (drzwi_przesuwne_HS) | 0,84 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w FX2 (fix) | 0,61 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w HS2 (drzwi_przesuwne_HS) | 0,82 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w ON1 (okno) | 0,89 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w OZ1 (okno) | 0,81 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w DZ3 (drzwi_zewn) | 1,0 | ≤ 1,30 | ✔ spełnia | ≤ 1,10: ✔ spełnia |
| U_w OE1 (okno) | 0,75 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w BC1 (okno) | 0,78 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w ON2 (okno) | 0,88 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w ON3 (okno) | 0,86 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| U_w OP1 (okno) | 0,71 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP3 (okno) | 0,74 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w OP2 (okno) | 0,77 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✔ spełnia |
| U_w ON4 (okno) | 0,82 | ≤ 0,90 | ✔ spełnia | ≤ 0,80: ✘ NIE spełnia |
| g ≤ 0,35 (okna E/S/W) | 24/24 spełnia | WT zał. 2 pkt 2.1 | ✔ spełnia | — |
| f_Rsi ≥ f_Rsi,wym | f_wym = 0,720 | WT zał. 2 pkt 2.2 | ✔ spełnia | —; bez danych: 3 węzłów (symulacja) |
| Kondensacja międzywarstwowa | 8/8 dopuszczalna | WT zał. 2 pkt 2.2.5 | ✔ spełnia | — |
| Ciągłość warstw (4 linie) | 10/10 przegród | brief § 9 | ✔ spełnia | — |
| Izolacja obwodowa R ≥ 2,0 | 2,78 | WT zał. 2 pkt 1.4 | ✔ spełnia |  |
| EP ≤ EP_max | 35,6 | ≤ 70 (WT § 329) | ✔ spełnia | A: PC R290 + PV + rekuperacja |

## Ostrzeżenia geometrii (model)

* 0.01: po drugiej stronie ściany S0-06 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* 0.01: krawędź 0.05 m bez ściany i bez sąsiedniego pomieszczenia (x=9.91, y=6.68) — pominięta
* 0.01: krawędź 0.03 m bez ściany i bez sąsiedniego pomieszczenia (x=9.88, y=6.67) — pominięta
* 0.02: krawędź 0.05 m bez ściany i bez sąsiedniego pomieszczenia (x=9.88, y=6.57) — pominięta
* 0.04: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=7.12, y=5.07) — pominięta
* 0.04: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=5.98, y=5.06) — pominięta
* 0.16: krawędź 0.15 m bez ściany i bez sąsiedniego pomieszczenia (x=7.19, y=7.47) — pominięta
* 0.07: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=7.12, y=5.02) — pominięta
* 0.07: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=5.94, y=5.02) — pominięta
* 0.11: odcinek 0.12 m ściany wewn. S0-17 bez pomieszczenia po drugiej stronie (wnętrze obrysu) — przyjęto przegrodę adiabatyczną
* 0.13: po drugiej stronie ściany S0-05 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* 0.13: krawędź 0.12 m bez ściany i bez sąsiedniego pomieszczenia (x=12.16, y=8.75) — pominięta
* 1.01: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=8.43, y=5.02) — pominięta
* 1.01: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=5.94, y=5.02) — pominięta
* 1.05: krawędź 0.02 m bez ściany i bez sąsiedniego pomieszczenia (x=5.27, y=6.44) — pominięta
* 1.05: krawędź 0.04 m bez ściany i bez sąsiedniego pomieszczenia (x=5.29, y=6.45) — pominięta
* 1.06: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=8.39, y=5.06) — pominięta
* 1.06: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=5.98, y=5.06) — pominięta
* 2.01: odcinek 0.03 m ściany wewn. S2-15 bez pomieszczenia po drugiej stronie (wnętrze obrysu) — przyjęto przegrodę adiabatyczną
* 2.01: odcinek 0.03 m ściany wewn. S2-15 bez pomieszczenia po drugiej stronie (wnętrze obrysu) — przyjęto przegrodę adiabatyczną
* 2.01: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=7.26, y=5.02) — pominięta
* 2.02: krawędź 0.04 m bez ściany i bez sąsiedniego pomieszczenia (x=-0.87, y=5.00) — pominięta
* 2.02: krawędź 0.04 m bez ściany i bez sąsiedniego pomieszczenia (x=-0.87, y=0.13) — pominięta
* 2.03: krawędź 0.03 m bez ściany i bez sąsiedniego pomieszczenia (x=5.79, y=2.62) — pominięta
* 2.03: po drugiej stronie ściany S2-07 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* 2.04: po drugiej stronie ściany S2-06 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* 2.04: krawędź 0.02 m bez ściany i bez sąsiedniego pomieszczenia (x=5.27, y=6.44) — pominięta
* 2.04: krawędź 0.04 m bez ściany i bez sąsiedniego pomieszczenia (x=5.29, y=6.45) — pominięta
* 2.05: po drugiej stronie ściany S2-03 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* 2.05: krawędź 0.03 m bez ściany i bez sąsiedniego pomieszczenia (x=8.59, y=2.62) — pominięta
* 2.06: krawędź 0.15 m bez ściany i bez sąsiedniego pomieszczenia (x=7.19, y=7.47) — pominięta
* 2.06: odcinek 0.12 m ściany wewn. S2-11 bez pomieszczenia po drugiej stronie (wnętrze obrysu) — przyjęto przegrodę adiabatyczną
* 2.06: krawędź 0.08 m bez ściany i bez sąsiedniego pomieszczenia (x=7.26, y=5.07) — pominięta
* 2.06: krawędź 0.09 m bez ściany i bez sąsiedniego pomieszczenia (x=8.39, y=5.06) — pominięta
* 2.06: po drugiej stronie ściany S2-04 brak pomieszczenia w obrysie kondygnacji — przyjęto powietrze zewnętrzne
* stolarka: symbol BC1 występuje w różnych wymiarach (2.24×1.50, 2.29×1.50) — ujednolicić zestawienie stolarki

## Pliki

* [01_przegrody_U.md](01_przegrody_U.md)
* [02_grunt.md](02_grunt.md)
* [03_stolarka_g.md](03_stolarka_g.md)
* [04_mostki.md](04_mostki.md)
* [glaser_SZ1.png](glaser_SZ1.png)
* [glaser_SWG.png](glaser_SWG.png)
* [glaser_DZ1.png](glaser_DZ1.png)
* [glaser_SD2.png](glaser_SD2.png)
* [glaser_SD1.png](glaser_SD1.png)
* [glaser_SZ2.png](glaser_SZ2.png)
* [glaser_SZL.png](glaser_SZL.png)
* [glaser_ST2Z_P2_zewn.png](glaser_ST2Z_P2_zewn.png)
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
