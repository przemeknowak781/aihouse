# Mostki cieplne

## Mostki cieplne — Ψ, χ, H_TB, f_Rsi węzłów

**Podstawa:** PN-EN ISO 14683:2017-09 (zał. C — wartości domyślne, wyłącznie rozwiązanie awaryjne); PN-EN ISO 10211:2017-09 (symulacje — moduł mostki2d); PN-EN ISO 13788:2013 rozdz. 5; WT zał. 2 pkt 2.2.1–2.2.3

> H_TB = Σ l_k·Ψ_k + Σ χ_j; system wymiarów: wewnętrzne całkowite (Ψ_oi).
> Kolumna „Źródło Ψ” wskazuje: symulację ISO 10211, deklarację producenta (dane przykładowe) albo wartość domyślną [NZW].

| Węzeł | Opis | Typ | l [m] / n | Ψ [W/(mK)] | H [W/K] | Źródło Ψ | f_Rsi | f_Rsi ≥ 0,72 |
|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| WZ-01 | Attyka stropodachu bryły A (D1) | attyka | 19,94 | 0,086 | 1,71 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,93 | ✔ spełnia |
| WZ-02 | Attyki dachów P1 (D2, D3) — poza ścianami bryły A | attyka | 13,41 | 0,171 | 2,29 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,90 | ✔ spełnia |
| WZ-03 | Attyka dachu zielonego nad pasem gospodarczym (linia D, częś | attyka | 7,17 | 0,195 | 1,40 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,89 | ✔ spełnia |
| WZ-04 | Okap E (PL-E) i daszek wejścia — łącznik termoizolacyjny | plyta_wspornikowa_lacznik | 22,47 | 0,128 | 2,88 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,93 | ✔ spełnia |
| WZ-05 | Krawędź ST2 (PL-2) — łącznik termoizolacyjny pod bryłą A | plyta_wspornikowa_lacznik | 18,71 | 0,134 | 2,51 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,93 | ✔ spełnia |
| WZ-06 | Krawędź ST3 (PL-3) — łącznik termoizolacyjny przy attyce bry | plyta_wspornikowa_lacznik | 24,30 | 0,205 | 4,98 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,89 | ✔ spełnia |
| WZ-07 | Strop P2 nad powietrzem zewnętrznym (ST2Z) — krawędzie wspor | strop_zewn_krawedz | 11,44 | 0,046 | 0,53 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi; średnia ważona podwęzłów — runda 2, 25.09.2026 | 0,85 | ✔ spełnia |
| WZ-08 | Cokół: ściana zewn. – płyta fundamentowa na XPS (część ogrze | sciana_grunt | 27,77 | 0,100 | 2,78 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,90 | ✔ spełnia |
| WZ-09 | Połączenia dom–garaż nieogrzewany (ściany osi E i 2 z płytą  | polaczenie_nieogrz | 24,51 | 0,188 | 4,61 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi; średnia ważona podwęzłów — runda 2, 25.09.2026 | 0,84 | ✔ spełnia |
| WZ-10 | Strop pośredni ST1/ST2 – ściana zewn. z ETICS ciągłym (wieni | strop_posredni | 18,20 | 0,000 | 0,00 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,96 | ✔ spełnia |
| WZ-11 | Ościeża okien/drzwi — ciepły montaż (rama 5 cm w murze, 4 cm | oscieze | 96,28 | 0,005 | 0,48 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,93 | ✔ spełnia |
| WZ-11N | Nadproża — BEZ kaset osłon w ociepleniu (kasety w okapach /  | nadproze | 45,03 | 0,008 | 0,36 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,94 | ✔ spełnia |
| WZ-11P | Podokienniki — parapet zewn. z okapnikiem na profilu z XPS | podokiennik | 29,42 | 0,006 | 0,18 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,91 | ✔ spełnia |
| WZ-11T | Progi HS / drzwi zewn. na płycie P0 — profil progowy termoiz | prog | 15,67 | 0,118 | 1,85 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,84 | ✔ spełnia |
| WZ-12 | Narożniki wypukłe ścian zewnętrznych | naroznik_wypukly | 40,05 | 0,066 | 2,64 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,93 | ✔ spełnia |
| WZ-13 | Konsole rusztu lamel (przekładka termiczna) | konsola_lamel | 50 szt. | χ=0,010 | 0,50 | wartość przykładowa — konsola mocowania lamel (przekładka termiczna) [DANE PRZYKŁADOWE – FIKCYJNE] | — | — |
| WZ-14 | Konsole ramy boksu C i linii D (PL-C1/PL-C2/PL-D; punktowe,  | kotwa | 17 szt. | χ=0,010 | 0,17 | wartość przykładowa — punktowa kotwa stalowa przez izolację [DANE PRZYKŁADOWE – FIKCYJNE] | — | — |
| WZ-15 | Przejścia instalacji przez przegrody zewnętrzne (wywiewka K1 | przejscie_instalacji | 16 szt. | χ=0,005 | 0,08 | wartość przykładowa — przejście instalacji przez przegrodę zewnętrzną (mankiet) [DANE PRZYKŁADOWE – FIKCYJNE] | — | — |
| WZ-16 | Belki wspornikowe B4/B5 i belka B3 w linii izolacji wspornik | strop_zewn_krawedz | 2,02 | 0,159 | 0,32 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi; średnia ważona podwęzłów — runda 2, 25.09.2026 | 0,85 | ✔ spełnia |
| WZ-X1 | Dachy D2/D3 (SD2) – ściana SZ1 bryły A wyższej kondygnacji n | dach_sciana | 13,79 | 0,022 | 0,30 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,96 | ✔ spełnia |
| WZ-X2 | Dach D4 (DZ1) – ściana SZ1 bryły B na krawędzi (pas gospodar | dach_sciana | 2,79 | 0,022 | 0,06 | katalog mostków budynku — tools/mostki_budynku.py (PN-EN ISO 10211, 2D), Ψ_oi — runda 2, 25.09.2026 | 0,96 | ✔ spełnia |

**H_TB = 30,63 W/K**; ΔU_TB = H_TB/A_obudowy = 0,050 W/(m²K) (A_obudowy = 611,3 m²).

Węzły bez f_Rsi (wymagana symulacja PN-EN ISO 10211 — moduł mostki2d): WZ-13, WZ-14, WZ-15.

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
