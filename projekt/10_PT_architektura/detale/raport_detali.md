# Raport modułu detali (lamela.views.detale)

Kontrola automatyczna każdego detalu: zgodność grubości warstw narysowanych z przegrodami `model/budynek.yaml` (tolerancja 0,5 mm; warstwy klinowe — w zakresie d_min…d_max), kolizje opisów (napis–napis, napis–linia rysunku), ciągłość 4 linii (karta mostka + liczba odcinków linii na rysunku).

| detal | tytuł | skala | węzły | grubości zgodne | kolizje napis–napis | napisy na liniach | H | S | P | I |
|---|---|---|---|---|---|---|---|---|---|---|
| D-01 | Cokół — ściana na płycie fundamentowej | 1:10 | WZ-08 | 12/12 | 1 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-03 | Próg drzwi HS bezprogowy z odwodnieniem liniowym | 1:10 | WZ-11T | 8/8 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-07 | Rura spustowa RS3 przy cokole — czyszczak i odpływ do KD | 1:10 | WZ-08 | 12/12 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-02 | Okno — ciepły montaż (podokiennik i nadproże) | 1:5 | WZ-11P, WZ-11N, WZ-11 | 8/8 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-09 | Okap PL-E 1,50 m nad przeszkleniem HS | 1:10 | WZ-04 | 8/8 | 0 | 0 | ! | ✓ | ✓ | ✓ |
| D-04 | Attyka dachu D1 — przelew awaryjny | 1:10 | WZ-01 | 11/11 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-05 | Attyka dachu D2 — wpust boczny i rura spustowa | 1:10 | WZ-02 | 13/13 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-06 | Wpust dachowy WP1 i rura RS1 | 1:10 | WZ-15 | 11/11 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-08 | Wspornik bryły A — krawędź ST2Z z płytą PL-2 | 1:10 | WZ-07a, WZ-16a | 14/14 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-12 | Lamele elewacyjne SZ2 — konsola rusztu (rzut) | 1:5 | WZ-13 | 4/4 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-10 | Ściana dom–garaż (SWG) i dach zielony D4 przy ścianie domu | 1:10 | WZ-09c | 23/23 | 0 | 0 | ✓ | ✓ | ✓ | ! |
| D-11 | Ściana dom–garaż (SWG) na płycie fundamentowej | 1:10 | WZ-09a | 13/13 | 0 | 0 | ✓ | ✓ | ✓ | ! |
| D-14 | Próg drzwi DZ2 garażu — odwodnienie liniowe i uszczelnienie | 1:10 | — | 6/6 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-13 | Wyłaz dachowy WYL1 — cokół ocieplony h 0,30 m | 1:10 | — | 5/5 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |
| D-13a | Świetlik SW1 — cokół ocieplony h 0,30 m | 1:10 | — | 5/5 | 0 | 0 | ✓ | ✓ | ✓ | ✓ |

## Szczegóły — grubości warstw (model ↔ rysunek)

* **D-01** — 12/12 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-03** — 8/8 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — ciągłość zachowana
* **D-07** — 12/12 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-02** — 8/8 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-09** — 8/8 warstw zgodnych; 4 linie: H — WZ-04: spadek płyty od budynku: nieokreślony w modelu (wymagany ≥ 1,5–2 %); odprowadzenie wody z krawędzi płyty (rynn; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-04** — 11/11 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-05** — 13/13 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-06** — 11/11 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 4 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-08** — 14/14 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-12** — 4/4 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — brak w detalu; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-10** — 23/23 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — WZ-09c: przerwana: TYNK_GIPS → SIL18 → ZB_C25 (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny); obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-11** — 13/13 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — WZ-09a: przerwana: TYNK_GIPS → SIL18 → ZB_C25 → TYNK_CW (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny); obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-14** — 6/6 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — brak w detalu; I — ciągłość zachowana
* **D-13** — 5/5 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 3 części (w tym warstwy dodatkowe, np. izolacja podłogi)
* **D-13a** — 5/5 warstw zgodnych; 4 linie: H — ciągłość zachowana; S — ciągłość zachowana; P — ciągłość zachowana; I — obrys izolacji: 2 części (w tym warstwy dodatkowe, np. izolacja podłogi)
