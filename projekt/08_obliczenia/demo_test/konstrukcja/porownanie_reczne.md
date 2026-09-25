# Niezależne przeliczenie ręczne wybranych pozycji — model testowy

Porównanie wyników biblioteki z rachunkiem ręcznym (wzory zamknięte, bez funkcji biblioteki). Różnice wynikają z uproszczeń rachunku ręcznego (pasmo bez skręcania, obciążenie belki równomierne zamiast rzeczywistego rozkładu reakcji płyty, jedno obciążenie zmienne wiodące).

| Pozycja | Wielkość | Ręcznie | Biblioteka (MES/obl.) | Biblioteka (tablice) | Różnica | Opis rachunku ręcznego |
|---|---|---|---|---|---|---|
| D1 / P2 | M_x,przęsło [kNm/m] | 16,20 | 14,37 | 14,59 | −11,3% | q_d = max(1,35·5,235 + 1,5·0,5·0,72; 0,85·1,35·5,235 + 1,5·0,72) = 7,607 kN/m²; k_x = c_y·l_y⁴/(c_x·l_x⁴ + c_y·l_y⁴) = 0,9005; M_x = 9/128·k_x·q_d·l_x² (pasmo bez skręcania — górne oszacowanie) |
| D1 / P2 | M_x,podpora [kNm/m] | −28,81 | −28,08 | — | −2,5% | M = −k_x·q_d·l_x²/8 (pasmo utwierdzone–przegubowe) |
| B1 | M_Ed,przęsło [kNm] | 54,24 | 45,80 | — | −15,6% | q_G = ΣR_G/L + b·h·25 = 45,28/3,82 + 1,50 = 13,35; q_Q = 8,67; q_S = 3,16 kN/m; q_d = 30,69 kN/m; M = q_d·l²/8, l = 3,76 m (rozkład równomierny zamiast rzeczywistego) |
| B1 | A_s,req [mm²] | 232,80 | 230,86 | — | −0,8% | b_eff = 0,85 m, d = 0,455 m, x = d − √(d² − 2M/(b_eff·f_cd)) = 5,6 mm, A_s = M/(f_yd·(d − x/2)) |
| L1 | V_d [kN/m] | 83,61 | 83,18 | — | −0,5% | G = 49,85 + ława 4,50 + odsadzki 3,42; Q ≈ 5,36 kN/m (Q — suma obciążeń zmiennych, ψ₀ = 0,7 dla wszystkich — bezpiecznie) |
| L1 | R_d [kN/m] | 233,06 | 233,06 | — | 0,0% | N_q = 26,092, N_γ = 32,590; R_k/A' = γD·N_q + ½γB'N_γ = 543,8 kPa; R_d = R_k·B/1,4 |
| L1 | ława niezbrojona (12.13) | 1,00 | 1,00 | — | 0,0% | 1 — warunek spełniony |
