# PZT — braki danych w modelu (dzialka.yaml / budynek.yaml)

Wygenerowano: 2026-09-25 — `lamela.views.site.braki_md` (generator rysunków PZT). Model NIE był edytowany; na rysunkach PZT-01…03 elementy oparte na danych zastępczych oznaczono **[DO UZUPEŁNIENIA]**. Proponowane formaty pól — zgodne z `docs/SCHEMAT_MODELU.md` §3 (dzialka.yaml) i §6 (rozszerzenia wody/odwodnienia).

Regeneracja: `PYTHONPATH=src python3 -m lamela.views.site --braki projekt/02_PZT/BRAKI_DANYCH.md`

| # | Pole modelu | Czego brakuje / do czego potrzebne | Proponowany format pola | Rysunki |
|---|---|---|---|---|
| 1 | `dzialka.yaml: sasiedzi[].kondygnacje, sasiedzi[].funkcja` | liczba kondygnacji i funkcja budynków sąsiednich (opis budynku na mapie wg BDOT500: np. „m2”) — obecnie odczytywane z tekstu 'opis' | `kondygnacje: 2, funkcja: m   # m — mieszkalny` | PZT-01…03 |
| 2 | `dzialka.yaml: drzewa[].obwod` | obwód pnia drzew istniejących na wys. 5 cm (u.o.p. art. 83f ust. 4 — progi 80/65/50 cm) i ewentualne pomniki przyrody (treść mapy do celów projektowych, rozp. 2022/1670 § 32) | `obwod: 95   # cm, na wys. 5 cm; pomnik_przyrody: false` | PZT-01…03 |
| 3 | `dzialka.yaml: bramy[].otwieranie` | strona zawiasów i kierunek otwierania furtki (WT § 42 ust. 1 — do wewnątrz działki) | `otwieranie: {zawiasy: lewa\|prawa, do: wewnatrz}` | PZT-01, PZT-02 |
| 4 | `dzialka.yaml: zjazd` | zjazd z drogi 1KDD w pasie drogowym (szerokość, skosy/łuki, nawierzchnia, przepust) — wg zezwolenia zarządcy drogi (u.d.p. art. 29 ust. 3a); na rysunku przedłużenie podjazdu do krawędzi jezdni w szerokości bramy | `zjazd: {obrys: [[x, y], ...], szer: 5.0, promienie: 3.0, nawierzchnia: '...', decyzja: 'nr … z …'}` | PZT-01, PZT-02 |
| 5 | `dzialka.yaml: retencja.zbiornik.{obrys\|sr, rzedna_dna, rzedna_wlotu, rzedna_przelewu}` | wymiary rzutu zbiornika retencyjnego i rzędne (dno, wlot, przelew) — rysunek pokazuje symbol umowny w punkcie xy | `zbiornik: {xy: [x, y], V: 5.0, sr: 2.0, rzedna_dna: 99.0, rzedna_wlotu: 100.6, rzedna_przelewu: 100.4}` | PZT-01, PZT-03 |
| 6 | `dzialka.yaml: uzbrojenie.projektowane[].{dn, material, spadek, rzedne}` | średnice, spadki i rzędne dna/wierzchu przewodów w punktach załamania i włączenia (RPB § 15 ust. 2 pkt 11) — obecnie tylko w tekście 'opis' | `{branza: kan_sanit, linia: [...], dn: 160, material: PVC-U, spadek: 0.02, rzedne: [[x, y, H_dna], ...], przykrycie_min: 1.2}` | PZT-02, PZT-03 |
| 7 | `dzialka.yaml: uzbrojenie.obiekty (studzienki deszczowe)` | studzienki rewizyjne/połączeniowe na kolektorach deszczowych KD (włączenia rur spustowych, załamania trasy, osadnik przed zbiornikiem) — brak obiektów w modelu | `{id: SD1, xy: [x, y], opis: 'studzienka PP Ø315 z osadnikiem', rzedna_wlazu: 101.30, rzedna_dna: 100.45}` | PZT-03 |
| 8 | `dzialka.yaml: uzbrojenie.obiekty[PC-JZ].{strefa_r, wym}` | promień strefy bezpieczeństwa czynnika R290 (bez otworów, wpustów, studzienek) i wymiary jednostki — obecnie odczytane z tekstu 'opis' | `{id: PC-JZ, xy: [x, y], strefa_r: 1.0, wym: [1.20, 0.45], L_WA_noc: 55}` | PZT-01, PZT-03 |
| 9 | `dzialka.yaml: dzialka.mpzp (wskaźniki)` | wskaźniki i parametry MPZP potrzebne do tabeli zgodności PZT (RPB § 14 pkt 4 lit. d) — w modelu jest tylko tekst uchwały; wartości wzięto z konfiguracji arkuszy (brief § 3) | `mpzp: {uchwala: '…', teren: 3MN, linia_zabudowy: 6.0, max_udzial_zabudowy: 0.30, min_udzial_pbc: 0.50, intensywnosc: [0.05, 0.80], max_wysokosc: 11.0, max_kondygnacji: 3, dach: 'płaski ≤ 12° lub 30–45°', min_miejsc_postojowych: 2, ogrodzenie_max_wys: 1.60}` | PZT-01 |
| 10 | `budynek.yaml: energia.wentylacja.wywiewki_kanalizacyjne[] — rzędna z` | rzędna wylotu wywiewki kanalizacyjnej (element najwyższy dla wysokości zabudowy, upzp art. 2 pkt 30 lit. a) — przyjęto wierzch pokrycia + 0,50 m; bez założenia H = 10,25 m | `wywiewki_kanalizacyjne: [[5.57, 6.2, 10.05]]  # [x, y, z]` | PZT-01 (tabela wskaźników), lamela.wskazniki |
| 11 | `budynek.yaml: energia.pv.z_max` | rzędna górnej krawędzi modułów PV (element wliczany do wysokości zabudowy) — obecnie tylko w tekście 'uwagi' | `pv: {..., z_max: 9.78}` | PZT-01, lamela.wskazniki |

## Założenia przyjęte na rysunkach do czasu uzupełnienia

* Limity MPZP — z konfiguracji `model/arkusze_pzt.yaml: wspolne.mpzp` (brief § 3, fikcyjny MPZP 3MN).
* Zjazd — przedłużenie bramy przesuwnej do krawędzi jezdni ze skosami 1,0 m (linia kreskowa).
* Zbiornik retencyjny — symbol umowny 7 × 4 mm (PN-B-01027 poz. 6); do PBC wyłączono rzut ≈ max(2,0; V/1,6) m² (jak audyt A1).
* Strefa R290 — promień odczytany z tekstu 'opis' obiektu PC-JZ (1,0 m).
* Liczba kondygnacji budynków sąsiednich — odczytana z tekstu 'opis' (opis BDOT500 „m2”).
* Minimalne odległości między sieciami — zasady wiedzy technicznej z `arkusze_pzt.yaml` (nie przepis).
