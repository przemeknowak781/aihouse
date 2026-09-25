# Obliczenia instalacji — Dom LAMELA

Biblioteka `lamela.obliczenia.sanitarne` i `lamela.obliczenia.elektryka`. Model: budynek: `model/budynek.yaml`, dzialka: `model/dzialka.yaml`, wyposazenie: `model/wyposazenie.yaml`, instalacje: `model/instalacje.yaml`.
**Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE]; wartości [ZAŁ] i [NZW] do potwierdzenia przed PT (D-19, D-23).**

## Raporty

| Raport | Warunków | Spełnione | Niespełnione | Niespełnione (skrót) |
|:---|---:|---:|---:|:---|
| [Instalacja wodociągowa i c.w.u.](01_woda.md) | 12 | 12 | 0 | — |
| [Kanalizacja sanitarna](02_kanalizacja.md) | 33 | 33 | 0 | — |
| [Odwodnienie dachów, retencja](03_deszczowa.md) | 64 | 64 | 0 | — |
| [Drenaż i odwodnienie powierzchniowe](04_drenaz.md) | 18 | 7 | 0 | — |
| [Pompa ciepła, ogrzewanie podłogowe, hałas](05_ogrzewanie.md) | 67 | 61 | 0 | — |
| [Bilans mocy](06_bilans_mocy.md) | 8 | 7 | 0 | — |
| [Obwody, zabezpieczenia, SPD, PWP](07_obwody.md) | 117 | 115 | 1 | W-185 WLZ: spadek napięcia ZKP → RG |
| [Fotowoltaika](08_pv.md) | 12 | 11 | 1 | W-194 Spadek napięcia po stronie DC |
| [Ochrona odgromowa, uziom](09_odgromowa.md) | 3 | 2 | 0 | — |

Schematy: [schemat ideowy RG](schemat_RG.png), [schemat PC / c.w.u.](schemat_PC_CWU.png). Wyniki liczbowe: [wyniki_instalacje.json](wyniki_instalacje.json).

## Najważniejsze wyniki

* Woda: q_obl = 1,128 dm³/s, wodomierz DN25 Q3=6.3, p_wym = 329 kPa (PRY18 prysznic (c.w.u.)); zasobnik c.w.u. 400 dm³, cyrkulacja: czasowa.
* Kanalizacja: ΣDU = 20,6 l/s, Q_ww = 2,27 l/s, przykanalik DN150 i=0.02.
* Wody opadowe: dachy 249,0 m², Q = 11,46 l/s; zbiornik 5,0 m³ + niecka 19,5 m² (V_min 5,71 m³); pokrycie podlewania 100 %.
* Drenaż opaskowy: NIEWYMAGANY (W1.1-E (wilgoć gruntowa, woda nienaporowa)).
* Ogrzewanie: Φ_HL = 7,41 kW (moduł fizyki/energii (PN-EN 12831)); PC PC-R290-07 (przykład), θ_biv = −9,7 °C; θ_V = 35,0 °C; bufor 80 dm³; hałas na granicy 26,4 dB(A).
* Bilans mocy: P_inst = 71,4 kW, P_szczyt (DLM) = 26,2 kW ≤ P_przył = 27 kW / 40 A.
* Obwody: 35; WLZ YKY 5×16 (∆U = 0,61 %); maks. ∆U = 2,98 %; CRL = 315 → SPD T1+2; PWP: PROJEKTOWAĆ (rekomendacja D-04 — spełnia WT §183 ust. 2 i jest zgodne z ROPoż).
* PV: 15 × moduł = 6,45 kWp (EW10), E = 5610 kWh/a, autokonsumpcja 65 %.
* Odgromowa: A_D = 4281 m²; LPS NIEWYMAGANY (R1 ≤ R_T przy SPD T1 dla obu klas obciążenia ogniowego); uziom: otokowy w gruncie.

## Dane przekazywane do charakterystyki energetycznej (moduł energii)

```json
{
 "cwu": {
  "Q_W_nd_kWh_a": 6320.0,
  "eta_W_d": 0.8,
  "zasobnik_l": 400,
  "dezynfekcja_kWh_a": 526.0
 },
 "ogrzewanie": {
  "eta_H_g_SCOP": 4.7,
  "COP_cwu": 3.2,
  "eta_H_e": 0.89,
  "eta_H_d": 0.96,
  "E_el_PC_kWh_a": 2735.0,
  "E_grzalka_kWh_a": 4.0,
  "Q_H_TMY_kWh_a": 11200.0
 },
 "pv": {
  "E_PV_uzyta_H_kWh_a": 348.0,
  "E_PV_uzyta_W_kWh_a": 1574.0,
  "E_PV_uzyta_pom_kWh_a": 528.0,
  "E_PV_uzyta_H_W_pom_miesiecznie_kWh": [
   75.1,
   148.3,
   256.8,
   331.5,
   288.6,
   283.6,
   277.1,
   268.8,
   221.5,
   162.1,
   83.2,
   54.0
  ],
  "w_PV": 0.0,
  "metoda": "bilans godzinowy, przypisanie proporcjonalne [UPR]"
 }
}
```

## Założenia ogólne i uwagi

* Wentylacja (moc rekuperatora, profil zużycia): 365 m³/h = max(Σnawiew, Σwywiew) — moduł wentylacji.

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
