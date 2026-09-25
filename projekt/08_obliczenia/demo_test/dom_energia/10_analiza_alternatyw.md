# Analiza alternatyw

## Analiza alternatywnych systemów zaopatrzenia w energię (RPB § 20 ust. 1 pkt 10)

**Podstawa:** RPB § 20 ust. 1 pkt 10 lit. a–e; metodologia Dz.U. 2015 poz. 376 ze zm.; WT § 329

> Nakłady inwestycyjne i ceny energii — założenia orientacyjne [ZAŁ] (dane/wyroby_przykladowe.yaml: ceny, capex_zl) — do aktualizacji ofertami i taryfami URE.
> (a) szacunek rocznej energii użytkowej: EU; (b) nośniki dostępne na działce: energia elektryczna (sieć nN), gaz ziemny (sieć w drodze), energia słoneczna (PV); sieć ciepłownicza — brak; (c) system konwencjonalny (B) i alternatywny/hybrydowy (A); (d) obliczenia porównawcze; (e) wynik i wybór.

| System | EU | EK | EP | EP ≤ 70 | E_CO2 [t/rok] | U_oze [%] | Koszt [zł/rok] [ZAŁ] | Nakłady [zł] [ZAŁ] |
|:---|---:|---:|---:|:---|---:|---:|---:|---:|
| A: PC R290 + PV + rekuperacja | 59,7 | 25,3 | 39,6 | ✔ spełnia | 1,39 | 77 | 3 181 | 70 000 |
| A0: PC R290 + rekuperacja, bez PV | 59,7 | 25,3 | 63,3 | ✔ spełnia | 2,22 | 61 | 4 761 | 45 000 |
| B: kocioł gazowy kondensacyjny + rekuperacja | 59,7 | 93,5 | 113,3 | ✘ NIE spełnia | 3,41 | 0 | 7 357 | 30 000 |
| C: PC — wartości domyślne metodologii, bez PV | 59,7 | 39,9 | 99,7 | ✘ NIE spełnia | 3,50 | 51 | 7 182 | — |

Jednostki: EU, EK, EP — kWh/(m²·rok).

**Wybór:** A: PC R290 + PV + rekuperacja — najniższe EP (39,6 kWh/(m²·rok)) spośród wariantów spełniających EP_max; roczny koszt energii niższy o 4 175 zł względem systemu konwencjonalnego (B), prosty okres zwrotu nakładów dodatkowych ≈ 9,6 lat.

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
