# Mostki cieplne

## Mostki cieplne — Ψ, χ, H_TB, f_Rsi węzłów

**Podstawa:** PN-EN ISO 14683:2017-09 (zał. C — wartości domyślne, wyłącznie rozwiązanie awaryjne); PN-EN ISO 10211:2017-09 (symulacje — moduł mostki2d); PN-EN ISO 13788:2013 rozdz. 5; WT zał. 2 pkt 2.2.1–2.2.3

> H_TB = Σ l_k·Ψ_k + Σ χ_j; system wymiarów: wewnętrzne całkowite (Ψ_oi).
> Kolumna „Źródło Ψ” wskazuje: symulację ISO 10211, deklarację producenta (dane przykładowe) albo wartość domyślną [NZW].

| Węzeł | Opis | Typ | l [m] / n | Ψ [W/(mK)] | H [W/K] | Źródło Ψ | f_Rsi | f_Rsi ≥ 0,72 |
|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| WZ-R1 | Attyka stropodachu D1 | attyka | 36,00 | 0,750 | 27,00 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-C1 | Narożnik zewnętrzny | naroznik_wypukly | 17,00 | 0,150 | 2,55 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-G1 | Cokół — ściana/podłoga na gruncie | sciana_grunt | 22,00 | 0,800 | 17,60 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-W1 | Ościeża okien | oscieze | 45,00 | 0,100 | 4,50 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-S1 | Wspornik bryły P1 — krawędź stropu nad powietrzem | strop_zewn_krawedz | 12,00 | 0,600 | 7,20 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-GA | Połączenie ściany dom–garaż ze ścianą zewnętrzną | polaczenie_nieogrz | 5,80 | 0,200 | 1,16 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| WZ-L1 | Konsole lamel | konsola_lamel | 20 szt. | χ=0,010 | 0,20 | wartość przykładowa — konsola mocowania lamel (przekładka termiczna) [DANE PRZYKŁADOWE – FIKCYJNE] | — | — |

**H_TB = 60,21 W/K**; ΔU_TB = H_TB/A_obudowy = 0,146 W/(m²K) (A_obudowy = 413,0 m²).

Węzły bez f_Rsi (wymagana symulacja PN-EN ISO 10211 — moduł mostki2d): WZ-R1, WZ-C1, WZ-G1, WZ-W1, WZ-S1, WZ-GA, WZ-L1.

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
