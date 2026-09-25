# Mostki cieplne

## Mostki cieplne — Ψ, χ, H_TB, f_Rsi węzłów

**Podstawa:** PN-EN ISO 14683:2017-09 (zał. C — wartości domyślne, wyłącznie rozwiązanie awaryjne); PN-EN ISO 10211:2017-09 (symulacje — moduł mostki2d); PN-EN ISO 13788:2013 rozdz. 5; WT zał. 2 pkt 2.2.1–2.2.3

> H_TB = Σ l_k·Ψ_k + Σ χ_j; system wymiarów: wewnętrzne całkowite (Ψ_oi).
> Kolumna „Źródło Ψ” wskazuje: symulację ISO 10211, deklarację producenta (dane przykładowe) albo wartość domyślną [NZW].

| Węzeł | Opis | Typ | l [m] / n | Ψ [W/(mK)] | H [W/K] | Źródło Ψ | f_Rsi | f_Rsi ≥ 0,72 |
|:---|:---|:---|---:|---:|---:|:---|---:|:---|
| AUTO-01 | ościeża, nadproża i progi/parapety otworów (obwód otworu) | oscieze | 102,20 | 0,100 | 10,22 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| AUTO-02 | narożnik zewnętrzny (wypukły) ścian zewnętrznych | naroznik_wypukly | 23,08 | 0,150 | 3,46 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| AUTO-03 | połączenie ściana zewnętrzna – podłoga na gruncie / płyta fu | sciana_grunt | 34,59 | 0,800 | 27,67 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| AUTO-04 | połączenie ściany zewnętrznej ze stropem pośrednim | strop_posredni | 34,59 | 0,000 | 0,00 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| AUTO-05 | połączenie stropodachu ze ścianą zewnętrzną (attyka / okap) | attyka | 34,29 | 0,750 | 25,72 | PN-EN ISO 14683:2017 zał. C — wartość domyślna (fallback) [NZW] | — | — |
| AUTO-06 | płyta wspornikowa przechodząca przez ścianę zewnętrzną — łąc | plyta_wspornikowa_lacznik | 5,04 | 0,150 | 0,76 | deklaracja łącznika — dane przykładowe z deklaracji typowego łącznika termoizolacyjnego do płyt wspornikowych (lub równoważny) [DANE PRZYKŁADOWE – FIKCYJNE] | 0,82 | ✔ spełnia |

**H_TB = 67,83 W/K**; ΔU_TB = H_TB/A_obudowy = 0,196 W/(m²K) (A_obudowy = 345,5 m²).

Węzły bez f_Rsi (wymagana symulacja PN-EN ISO 10211 — moduł mostki2d): AUTO-01, AUTO-02, AUTO-03, AUTO-04, AUTO-05.

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
