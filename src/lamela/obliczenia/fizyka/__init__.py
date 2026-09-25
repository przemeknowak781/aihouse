"""Fizyka budowli — „Dom LAMELA” (każda funkcja podaje normę i punkt w docstringu).

Moduły i główne API:
* `u_przegrody` — PN-EN ISO 6946:2017: `oblicz_u(warstwy, materialy, rola=…, poprawki=PoprawkiU(...))` → `WynikU`
  (R_si/R_se wg kierunku, pustki, metoda kresów `frakcje`, ΔU_g/ΔU_f/ΔU_r, `u_klin_*` zał. C),
  `u_przegrody_modelu(m, kod, rola)`, `warstwy_stropu(m, strop, kond_nad)`, `wymagania_u(rola)`, `raport_u(...)`;
* `grunt` — PN-EN ISO 13370:2017: `oblicz_grunt(A, P, w, R_f, izolacja=IzolacjaKrawedziowa(...))` → `WynikGrunt`
  (B', d_t, U, ΔΨ krawędzi, H_g, H_pi/H_pe, H_T,ig wg PN-EN 12831), `raport_grunt`;
* `okna` — PN-EN ISO 10077-1:2017: `u_okna(szer, wys, DaneStolarki)`, `dane_stolarki(symbol, typ, model_stolarka)`,
  `g_tot_uproszczona` (PN-EN ISO 52022-1), `f_c_wt` (WT zał. 2 pkt 2.1.3), `sprawdz_g` (pkt 2.1.1–2.1.4),
  `zacienienie_miesieczne(azymut, szer, wys, okap=Okap(...), lamele=Lamele(...))`, `raport_okna`;
* `kondensacja` — PN-EN ISO 13788:2013: `f_rsi_min(θ_i, phi_i=0.5 | klasa=…)`, `f_rsi_przegrody(U)`,
  `warstwy_glaser(warstwy, materialy, rola=…)`, `glaser(...)` → `WynikGlaser` (M_a, wysychanie, wymagane s_d
  paroizolacji — `sd_par_wym`, `sd_par_wym_dop`), `wykres_glaser` (PNG), `raport_frsi`, `raport_glaser`;
* `mostki` — PN-EN ISO 14683 (wartości domyślne — awaryjnie) / wyniki PN-EN ISO 10211 (`mostki2d`):
  `wezly_z_modelu(m, wyniki_symulacji={id: {psi|psi_i|psi_e|psi_oi, f_rsi, dlugosc}})`, `wyniki_z_mostki2d(...)`,
  `wczytaj_wyniki_symulacji(plik)`, `h_tb`, `sprawdz_frsi`, `raport_mostki`;
* `warstwy` — funkcje warstw i kontrola ciągłości „4 linii”: `sprawdz_ciaglosc(kod, nazwa, warstwy, materialy, rola)`,
  `uwagi_wezla`, `funkcja_warstwy`, `mat_props`, `sd_warstwy`.
"""
