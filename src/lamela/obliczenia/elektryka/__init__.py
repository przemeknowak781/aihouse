"""Obliczenia instalacji elektrycznych i odgromowych „Dom LAMELA”.

* ``tabele``     — I_z (PN-HD 60364-5-52 zał. B), współczynniki poprawkowe, rezystancje żył, charakterystyki wyłączników;
* ``bilans``     — ``odbiorniki_z_modelu(dane, ogrzewanie=…)`` (obwody wydzielone wg WT §188) i ``bilans_mocy(dane, odbiorniki)``:
                   moc zainstalowana, k_j, moc szczytowa bez/z DLM, weryfikacja 27 kW / 40 A, podział na fazy;
* ``obwody``     — ``oblicz_obwody(dane, odbiorniki)``: WLZ, dobór przekrojów i zabezpieczeń (I_B ≤ I_n ≤ I_z, I₂ ≤ 1,45·I_z),
                   ∆U (ZKP→RG ≤ 0,5 %, całość ≤ 3 %), Z_s i samoczynne wyłączenie (TN-S, 0,4 s), selektywność, RCD, SPD (CRL),
                   kategorie udarowe, PWP (D-04);
* ``pv``         — ``oblicz_pv(dane, ogrzewanie=…, woda=…)``: ≤ 6,5 kWp, rozmieszczenie, PVGIS (Poznań), autokonsumpcja
                   godzinowa → ``do_dict()['do_EP']``, łańcuchy, zabezpieczenia DC/AC; ``pobierz_pvgis()`` — odświeżenie z API;
* ``odgromowa``  — ``ocena_ryzyka(dane)``: A_D, N_D, N_L, R1 (scenariusze), decyzja LPS, uziom, połączenia wyrównawcze;
* ``schemat_rg`` — ``rysuj_schemat_rg(wynik_obwodow, plik.png)`` — schemat jednokreskowy RG (symbole PN-EN 60617 uproszczone).
"""
