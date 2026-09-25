"""Energia — obciążenie cieplne, wentylacja, charakterystyka energetyczna — „Dom LAMELA”.

Moduły i główne API:
* `klimat` — TMY Poznań (MIiR, WMO 12330): `klimat_miesieczny()` (θ_e, φ_e, p_e, I(azymut, nachylenie)),
  `klimat_godzinowy()` (+ `pozycja_slonca()`), `p_sat`, `theta_z_psat`;
* `bryla` — `buduj_bryle(m)` → `Bryla` (elementy przegród pomieszczeń: ściany/okna/drzwi/podłogi/stropy/dachy,
  sąsiedztwo zewn./grunt/pomieszczenie, azymut, zacienienie okien, węzły liniowe z geometrii); wymiary wewnętrzne całkowite;
* `obudowa` — `oblicz_obudowe(m, wyniki_symulacji=None, wariant_psi=None)` → `Obudowa` (U wszystkich elementów,
  grunt, stolarka, mostki H_TB, zacienienie, g, ciągłość warstw), `raport_ciaglosc`;
* `wentylacja` — `bilans_wentylacji(bryla, cfg=…)` → `WynikWent` (PN-83/B-03430/Az3, WT § 147–154), `raport_wentylacja`;
* `obciazenie_cieplne` — `obciazenie_cieplne(ob, went)` → `WynikObc` (PN-EN 12831-1 per pomieszczenie, θ_u garażu,
  dobór PC — punkt biwalentny z TMY), `raport_obciazenie`;
* `pv` — produkcja PV (TMY) i autokonsumpcja miesięczna z symulacji godzinowej;
* `ep` — metodologia Dz.U. 2015 poz. 376 ze zm.: `oblicz_ep(ob, went, System, obc=…)` → `WynikEP`
  (EU, EK, EP, E_CO2, U_oze, koszt), `system_projektowy`, `system_gazowy`, `system_pc_domyslny`, `raport_ep`,
  `wykres_bilans` (PNG), `raport_alternatywy` (RPB § 20 ust. 1 pkt 10).
Łańcuch dla modelu i raporty: `lamela.obliczenia.fizyka_energia` (CLI).

Dane wejściowe z modelu `budynek.yaml` (poza sekcjami schematu) — wszystkie opcjonalne, w razie braku przyjmowane są
wartości przykładowe / domyślne (oznaczane w raportach):
  materialy.<kod>: lambda (obliczeniowa), mu (albo sd — dla membran), rho, cp, [funkcja: izolacja|paroizolacja|
      hydroizolacja|przeciwwilgociowa|wiatroizolacja|drenaz|geowloknina|bariera_korzenna|substrat|…]
  przegrody.<kod>.warstwy[]: [frakcje: [{mat, udzial}], grupa] (warstwa niejednorodna), [pustka: nw|sw|dw],
      [klin: {d_min, d_max, ksztalt: prostokat|trojkat_max|trojkat_min}], [lambda], [R], [funkcja]
  pomieszczenia[]: temp (θ_int wg WT § 134; null lub `ogrzewane: false` — nieogrzewane), went {naw, wyw},
      [rodzaj: kuchnia|lazienka|wc|pralnia|pomocnicze|techniczne|pokoj|komunikacja|garaz], [podloga: <kod przegrody>]
  stropy[]: sufit (kod PRZEGRODY z pełnymi warstwami pod płytą — obowiązkowo nad garażem i nad powietrzem zewn.), mat
  dachy[]: przegroda (pełne warstwy, izolacja spadkowa `klin` albo wpusty + spadek)
  otwory[]: symbol, oslona (zaluzja_zewn|roleta_zewn|screen_zip|brak), [kwatery]
  stolarka.<symbol>: {wyrob: <klucz dane/wyroby_przykladowe.yaml>, U_g, U_f, psi_g, b_f, b_s, g_n, U_D}
  wezly[]: {id, typ, dlugosc | liczba, przegrody, [psi], [f_rsi]} — Ψ/f_Rsi z symulacji: energia.wezly_wyniki
  energia:
    n50, osoby, pojemnosc (bardzo_lekka|lekka|srednia|ciezka|bardzo_ciezka), chlodzenie, psi_wariant, wezly_wyniki
    grunt: {typ: piasek|glina|skala, lambda, G_w, psi_wf, izolacja_obwodowa: {typ: pionowa|pozioma, D, d_n, lam_n}}
    wentylacja: {centrala: <klucz>|{V_nom_m3h, V_max_m3h, eta_t, SFP_Wh_m3, SEC_kWh_m2a}, r_n,
                 czerpnia: [x, y, z], wyrzutnia: [x, y, z], wyrzut: pionowy|poziomy, zestaw_zblokowany,
                 wywiewki_kanalizacyjne: [[x, y]], rzedna_terenu}
    ogrzewanie: {zrodlo: <klucz>|{P_Am15W35_kW, P_Am7W35_kW, P_A2W35_kW, SCOP_35, COP_cwu, moc_grzalki_kW},
                 temp_zasilania, SCOP, eta_H_e, eta_H_d, eta_H_s, pompy_W}
    cwu: {zasobnik: <klucz>, COP, eta_W_s, eta_W_d, cyrkulacja: {moc_W, h_doba} | false, dezynfekcja_kWh_rok}
    pv: {moduly, P_modul_Wp | P_kWp, azymut, nachylenie, PR, autokonsumpcja: symulacja|<liczba>, sterowanie_cwu_pv,
         E_dom_kWh} | false
    garaz: {stanowiska, otwory_went_m2, n_went}
    capex_A, capex_B
"""
