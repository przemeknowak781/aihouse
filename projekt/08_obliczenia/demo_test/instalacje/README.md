# Obliczenia instalacji — Dom testowy pipeline'u 3D

Biblioteka `lamela.obliczenia.sanitarne` i `lamela.obliczenia.elektryka`. Model: budynek: `/home/user/aihouse/model/test/dom_testowy.yaml`, dzialka: `/home/user/aihouse/model/test/dzialka_testowa.yaml`, wyposazenie: `/home/user/aihouse/model/test/wyposazenie_testowe.yaml`, instalacje: `/home/user/aihouse/model/test/instalacje_testowe.yaml`.
**Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE]; wartości [ZAŁ] i [NZW] do potwierdzenia przed PT (D-19, D-23).**

## Raporty

| Raport | Warunków | Spełnione | Niespełnione | Niespełnione (skrót) |
|:---|---:|---:|---:|:---|
| [Instalacja wodociągowa i c.w.u.](01_woda.md) | 12 | 12 | 0 | — |
| [Kanalizacja sanitarna](02_kanalizacja.md) | 19 | 19 | 0 | — |
| [Odwodnienie dachów, retencja](03_deszczowa.md) | 16 | 16 | 0 | — |
| [Drenaż i odwodnienie powierzchniowe](04_drenaz.md) | 5 | 0 | 5 | W-019 Spadek terenu od budynku, ściana 1 (śr. 5,0; −0,3); W-019 Spadek terenu od budynku, ściana 2 (śr. 10,3; 4,0); W-019 Spadek terenu od budynku, ściana 3 (śr. 5,0; 8,3); W-019 Spadek terenu od budynku, ściana 4 (śr. −0,3; 4,0); W-019 Wysokość cokołu (posadzka parteru − teren), minimum na obwodzie |
| [Pompa ciepła, ogrzewanie podłogowe, hałas](05_ogrzewanie.md) | 36 | 35 | 1 | W-153 1.04 Garderoba: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL |
| [Bilans mocy](06_bilans_mocy.md) | 7 | 7 | 0 | — |
| [Obwody, zabezpieczenia, SPD, PWP](07_obwody.md) | 84 | 83 | 0 | — |
| [Fotowoltaika](08_pv.md) | 12 | 12 | 0 | — |
| [Ochrona odgromowa, uziom](09_odgromowa.md) | 3 | 2 | 0 | — |

Schematy: [schemat ideowy RG](schemat_RG.png), [schemat PC / c.w.u.](schemat_PC_CWU.png). Wyniki liczbowe: [wyniki_instalacje.json](wyniki_instalacje.json).

## Najważniejsze wyniki

* Woda: q_obl = 0,787 dm³/s, wodomierz DN20 Q3=4.0, p_wym = 298 kPa (PRY07 prysznic (c.w.u.)); zasobnik c.w.u. 200 dm³, cyrkulacja: czasowa.
* Kanalizacja: ΣDU = 8,7 l/s, Q_ww = 2,00 l/s, przykanalik DN150 i=0.02.
* Wody opadowe: dachy 102,8 m², Q = 4,73 l/s; zbiornik 5,0 m³ + niecka 9,0 m² (V_min 2,66 m³); pokrycie podlewania 85 %.
* Drenaż opaskowy: NIEWYMAGANY (W1.1-E (wilgoć gruntowa, woda nienaporowa)).
* Ogrzewanie: Φ_HL = 4,88 kW (WSKAŹNIKOWE ZASTĘPCZE [ZAŁ] — do zastąpienia wynikami PN-EN 12831 (moduł energii)); PC PC-R290-05 (przykład), θ_biv = −11,1 °C; θ_V = 34,2 °C; bufor 50 dm³; hałas na granicy 24,6 dB(A).
* Bilans mocy: P_inst = 43,0 kW, P_szczyt (DLM) = 24,0 kW ≤ P_przył = 27 kW / 40 A.
* Obwody: 24; WLZ YKY 5×16 (∆U = 0,38 %); maks. ∆U = 2,37 %; CRL = 315 → SPD T1+2; PWP: PROJEKTOWAĆ (rekomendacja D-04 — spełnia WT §183 ust. 2 i jest zgodne z ROPoż).
* PV: 15 × moduł = 6,45 kWp (EW10), E = 5610 kWh/a, autokonsumpcja 51 %.
* Odgromowa: A_D = 2165 m²; LPS NIEWYMAGANY (R1 ≤ R_T przy SPD T1 dla obu klas obciążenia ogniowego); uziom: fundamentowy w ławach.

## Dane przekazywane do charakterystyki energetycznej (moduł energii)

```json
{
 "cwu": {
  "Q_W_nd_kWh_a": 3361.0,
  "eta_W_d": 0.8,
  "zasobnik_l": 200,
  "dezynfekcja_kWh_a": 257.0
 },
 "ogrzewanie": {
  "eta_H_g_SCOP": 4.8,
  "COP_cwu": 3.3,
  "eta_H_e": 0.89,
  "eta_H_d": 0.96,
  "E_el_PC_kWh_a": 1802.0,
  "E_grzalka_kWh_a": 1.0,
  "Q_H_TMY_kWh_a": 7384.0
 },
 "pv": {
  "E_PV_uzyta_H_kWh_a": 282.0,
  "E_PV_uzyta_W_kWh_a": 997.0,
  "E_PV_uzyta_pom_kWh_a": 349.0,
  "E_PV_uzyta_H_W_pom_miesiecznie_kWh": [
   66.4,
   129.8,
   192.0,
   211.0,
   174.4,
   157.6,
   157.0,
   154.9,
   137.6,
   126.5,
   72.7,
   48.3
  ],
  "w_PV": 0.0,
  "metoda": "bilans godzinowy, przypisanie proporcjonalne [UPR]"
 }
}
```

## Założenia ogólne i uwagi

* Wentylacja (moc rekuperatora, profil zużycia): 210 m³/h = max(Σnawiew, Σwywiew) — model (pola went pomieszczeń).

## Dane wymagane od modelu / wyposażenia (do uzupełnienia w `model/`)

| Plik / źródło | Dane |
|:---|:---|
| wyposazenie.yaml | przybory sanitarne z typem (wc, umywalka, umywalka_blat, bidet, wanna, prysznic, zlew, zmywarka, pralka, suszarka) — punkt na licu ściany + obrot; zawory ogrodowe, zlewiki, wpusty podłogowe (typy w przybory.KATALOG) |
| wyposazenie.yaml | urządzenia: pompa_ciepla (jednostka wewn.), zasobnik, rekuperator, plyta, lodowka — z mocą/typem wyrobu (opcjonalnie) |
| instalacje.yaml (nowy) | osoby; lokalizacje: RG, wodomierz, zasobnik, rozdzielacze_co per kondygnacja, ZKP, studzienka, czerpnia, pompa_ciepla_jz {xy, ustawienie: wolnostojaca\|przy_scianie\|naroze} |
| instalacje.yaml (nowy) | piony: [{id, xy}] — trasy pionów wod.-kan. (inaczej grupowanie automatyczne R ≤ 3,5 m) |
| instalacje.yaml (nowy) | wyroby: dane DTR/DWU (PC: moc/COP w punktach A-15…A12 W35, L_WA, SCOP, η_s; moduł PV; falownik; wpusty dachowe: przepustowość; zawór EA/filtr: k_v; wodomierz: ∆p(Q3)) |
| instalacje.yaml lub moduł energii | obciazenie_cieplne: Φ_HL pomieszczeń [W] (PN-EN 12831) — w tym opracowaniu wskaźnikowe zastępcze, jeśli brak |
| budynek.yaml: dachy[] | wpusty [{xy, dn, podgrzewany}], przelewy_awaryjne [{xy, sciana_attyki, szer, wys, rzedna_dna}], rury_spustowe [{id, od_wpustu, trasa, xy_pion, dn, do}], spadki (schemat §6) |
| budynek.yaml: przegrody | dach zielony: warstwy z nazwami (substrat, drenaż, geowłóknina, bariera przeciwkorzenna); podłoga: jastrych (grubość, λ) i izolacja pod wężownicą; posadzki — kody (płytki / drewno / wykładzina) |
| budynek.yaml: pomieszczenia | temp (20/24 °C), went {naw, wyw}; nazwy jednoznaczne (łazienka, WC, kuchnia, pralnia, garaż, techniczne) |
| budynek.yaml: fundamenty | typ (lawy/plyta) i izolacja płyty (XPS pod płytą → uziom otokowy); spód fundamentu |
| dzialka.yaml | uzbrojenie istniejące i projektowane (woda, kan_sanit, en) z rzędnymi/głębokością; retencja (zbiornik xy/V, niecka/rozsączanie obrys); odwodnienia [{typ: liniowe\|opaska_zwirowa\|drenaz_opaskowy\|niecka, ...}]; teren.punkty_projektowane (spadki ≥ 2 % od budynku); bramy; ZKP |
| geotechnika (opinia) | k_f in situ, ZWG, rodzaj gruntu — decyzja o drenażu i objętość niecki |
| warunki przyłączenia | ciśnienie dyspozycyjne i maks. w sieci wod., rzędna kanału, Z_Q / I_k w ZKP, typ zabezpieczenia przedlicznikowego |
