# Analiza alternatyw

## Analiza alternatywnych systemów zaopatrzenia w energię (RPB § 20 ust. 1 pkt 10)

**Podstawa:** RPB § 20 ust. 1 pkt 10 lit. a–e; metodologia Dz.U. 2015 poz. 376 ze zm.; WT § 329

> Nakłady inwestycyjne i ceny energii — założenia orientacyjne [ZAŁ] (dane/wyroby_przykladowe.yaml: ceny, capex_zl) — do aktualizacji ofertami i taryfami URE.
> (a) szacunek rocznej energii użytkowej: EU; (b) nośniki dostępne na działce: energia elektryczna (sieć nN), gaz ziemny (sieć w drodze), energia słoneczna (PV); sieć ciepłownicza — brak; (c) system konwencjonalny (B) i alternatywny/hybrydowy (A); (d) obliczenia porównawcze; (e) wynik i wybór.

| System | EU | EK | EP | EP ≤ 70 | E_CO2 [t/rok] | U_oze [%] | Koszt [zł/rok] [ZAŁ] | Nakłady [zł] [ZAŁ] |
|:---|---:|---:|---:|:---|---:|---:|---:|---:|
| A: PC R290 + PV + rekuperacja | 64,4 | 26,6 | 37,0 | ✔ spełnia | 1,14 | 81 | 2 706 | 70 000 |
| A0: PC R290 + rekuperacja, bez PV | 64,4 | 26,6 | 66,5 | ✔ spełnia | 2,05 | 63 | 4 434 | 45 000 |
| B: kocioł gazowy kondensacyjny + rekuperacja | 64,4 | 98,8 | 118,3 | ✘ NIE spełnia | 3,12 | 0 | 6 826 | 30 000 |
| C: PC — wartości domyślne metodologii, bez PV | 64,4 | 41,7 | 104,2 | ✘ NIE spełnia | 3,22 | 52 | 6 647 | — |

Jednostki: EU, EK, EP — kWh/(m²·rok). Koszt — energia systemów technicznych (ogrzewanie, c.w.u., urządzenia pomocnicze) z sieci wg cen założonych + opłaty stałe; bez urządzeń gospodarstwa domowego i bez wartości energii PV oddanej do sieci lub zużytej przez urządzenia domowe (zachowawczo dla wariantów z PV). Nakłady — tylko elementy różniące warianty.

**Wybór:** A: PC R290 + PV + rekuperacja — najniższe EP (37,0 kWh/(m²·rok)) spośród wariantów spełniających EP_max; roczny koszt energii niższy o 4 119 zł względem systemu konwencjonalnego (B), prosty okres zwrotu nakładów dodatkowych ≈ 9,7 lat.

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
