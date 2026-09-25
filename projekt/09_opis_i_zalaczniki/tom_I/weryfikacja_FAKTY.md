# Weryfikacja tomu I — FAKTY (niezależna, sceptyczna)

Przedmiot: `projekt/wydanie/PZT_PAB_ZL_2026.09.25.pdf` (62 s., zbudowany 07:18) oraz elementy w `projekt/09_opis_i_zalaczniki/tom_I/`, generatory `tools/dokumenty/{tom_I_*,pzt_*,pab_*,zl_*}.py`.
Metoda: tekst PDF (PyMuPDF), a obok niego wartości policzone na nowo z bieżącego modelu (budynek.yaml i dzialka.yaml, stan z 07:16): `DaneZag` (lamela.wskazniki, audyt A1, deszczowa, ogrzewanie), `DanePAB` (fizyka_energia, instalacje.oblicz_wszystko, audyt A1: 0 NIEZGODNE / 4 UWAGA / 166 OK), `wyniki_mostki.json`, katalog PC `sanitarne/ogrzewanie.py`. Poprawek nie wprowadzano.

## Co się zgadza (nie wymaga działań)
- Wskaźniki MPZP i bilans terenu (PZT pkt 4, PAB 3.3) są zgodne z bieżącym `lamela.wskazniki`:
  - pow. zabudowy 187,50 m² (11,72 %); PBC 1 270,15 m² (79,38 %);
  - intensywność 0,248; wysokość zabudowy 10,27 m (111,65 − 101,38); wysokość wg WT § 6: 9,97 m;
  - bilans pokrycia terenu sumuje się do 1 600,00 m².
- PAB: PU 239,16 m² (95,36 + 84,38 + 59,42) — sumy grup, pomniejszeń i netto (299,86) arytmetycznie poprawne. Kubatura 1 354,45 m³ zgadza się z sumą składników. Obrysy kondygnacji zgadzają się z modelem.
- Odległości od granic, sąsiadów i jezdni (9,88 m), linia zabudowy (rezerwa 0,95 m), MP1–MP4 — zgodne z audytem A1.
- EP: 35,6 kWh/(m²·rok), EU 41,2, E_CO₂ 2,07 t, OZE 75 % oraz Ψ WZ-08 (0,100 / fRsi 0,903) — zgodne z modułami.
- Liczby w elementach samodzielnych (PZT/PAB/ZL w `tom_I/`) są takie same jak w pliku zbiorczym. W generatorach nie ma liczb wpisanych ręcznie — wyjątki niżej, pkt 9 i 12.

## Problemy

### KRYTYCZNE
1. **Część rysunkowa tomu przeczy części opisowej (rysunki nieaktualne).** Znane ostrzeżenie ze składania, ale rozbieżności są merytoryczne:
   - **PZT-01 i PZT-02:** wysokość zabudowy 10,28 m (z_top 111,68 — „wywiewka, ZAŁOŻENIE”) wobec 10,27 m (czerpnia 111,65) w opisie. Pozostałe różnice (rysunek / opis):

     | Wielkość | Rysunki PZT-01, PZT-02 | Opis |
     |---|---|---|
     | wysokość wg WT § 6 | 9,94 m | 9,97 m |
     | wejście przyjęte do WT § 6 | O0-04 | O0-03 |
     | t_min | 101,32 | 101,29 |
     | tarasy | 67,27 m² | 66,75 m² |
     | opaska | 13,13 m² | 13,33 m² |
     | PBC | 1 269,84 m² (79,36 %) | 1 270,15 m² (79,38 %) |
     | niecka chłonna | **24 m² / 7,2 m³** | **28 m² / 8,40 m³** |
     | zbiornik–budynek | 6,70 m | 5,70 m |
     | zbiornik–granica | 11,60 m | 10,60 m |
     | niecka–granica | 8,60 m | 8,10 m |

   - **PB-AR-01…10 (z `01_koncepcja/widoki`):**
     - na przekroju WT § 6 H = 9,79 m (od −0,267), w opisie 9,97 m (od −0,348);
     - zestawienia pomieszczeń nie zgadzają się z tab. 8 PAB, np. 1.13 h 2,76 wobec 2,70; 1.09 h 2,77 wobec 2,53; 3.05 16,32 wobec 16,25 m²; 3.07 6,05 wobec 5,90 m²; netto P0 148,49 wobec 148,53, P2 66,30 wobec 66,01;
     - na rzucie SZ1 „U ≈ 0,15”, w tab. 13 0,166.

   Wymagane: wygenerować PZT-01…03 i PB-AR-01…10 z bieżącego modelu (`--regeneruj-rysunki`, a dla PAB — komplet w `03_PAB/rysunki`), a następnie ponownie złożyć tom.

### ISTOTNE
2. **Dwie różne pompy ciepła w jednym tomie.**
   - PZT tab. 9: PC-R290-09, L_WA 58/53 dB(A), 27,4 dB(A) na granicy.
   - PAB 9.4 i 12.2: PC-R290-07, L_WA „55 dB(A)”, 26,4 dB(A).
   - Przyczyna: `pzt_dane.DaneZag._instalacje()` wywołuje `oblicz_ogrzewanie` bez `phi_hl`, więc przyjmuje wskaźnikowe Φ = 9,37 kW [ZAŁ], zamiast Φ_HL = 7,41 kW z PN-EN 12831, którego używa PAB.
3. **PAB 12.2 i 9.4 łączą dane dwóch różnych urządzeń.**
   - „Moc pompy przy −18 °C: 5,80 kW” pochodzi z karty `obc.dobor` (pompa 8 kW, θ_biv −13,9 °C). Zaraz obok stoi „punkt biwalentny −9,7 °C”, który pochodzi z PC-R290-07 (4,55 kW przy −18 °C).
   - „L_WA = 55 dB(A)” pochodzi z tej samej karty, a 26,4 dB(A) policzono z L_WA,noc = 52 dB dla PC-R290-07 (w katalogu L_WA = 57 dB). Podana wartość jest nocna; poziomu dziennego nie podano.
   - EP policzono z SCOP 4,5 (karta), a instalacje przyjmują SCOP 4,7 (PC-R290-07).
4. **Niecka chłonna.** PAB 9.1: „A = 19,5 m²” — to wynik obliczenia minimum. W modelu i w PZT (tab. 1, tab. 10): 28,0 m², V 8,40 m³.
5. **PZT tab. 1 a tab. 9 — odległość jednostki PC od granicy E.** Tab. 1: „7,0 m” (tekst z `dzialka.yaml` opis PC-JZ). Tab. 9 i geometria (x = 24,40): 7,60 m.
6. **Nieujawniona uwaga audytu dotycząca WT.** Audyt A1 zgłasza UWAGĘ: wyrzutnia ↔ okno dachowe SW1 w odległości 5,29 m, wylot tylko 0,25 m nad oknem, a WT § 152 ust. 12 wymaga ≥ 1,00 m [W-167]. PAB 12.2 podaje „czerpnia i wyrzutnia dachowe (WT § 152)”, a rozdz. 15 — „audyt: 0 niezgodności”, bez interpretacji (SW1 jako świetlik nieotwierany) i bez zmiany. Nieujawniona jest też UWAGA dotycząca lokalizacji PC przy elewacji S (założenie: N lub E).
7. **ZL, BIOZ pkt 1.4: „płyty wysunięte, okapy i wsporniki żelbetowe monolityczne (13 elementów)”.** Generator liczy wszystkie `wsporniki_plyty`. Żelbetowe są tylko 4 (PL-E, PL-DA, PL-2, PL-3). Pozostałe to rama stalowa (PL-C1, PL-C2, WYL1, PL-D), wełna (IZ-ST2Z), podsufitki (PS-A, OB-A, OB-A2) i szkło (SW1).
8. **Zestawienia pomieszczeń na PB-AR a PU w opisie — różne definicje.** Rysunek podaje „użytkowa (podst. + pomoc.)” 115,93 m² na P0 (garaż wliczony, komunikacja nie), a opis PU (W-316) 95,36 m². Na P1: 70,30 wobec 84,38. Ta sprzeczność pozostanie także po regeneracji rysunków (generator views).

### DROBNE
9. Odsyłacze PZT „(obliczenie — pkt 7)” w 3.2 i „(pkt 3 lit. b, pkt 7)” w tab. 9 wskazują pkt 7 „Ochrona ludności”. Retencja jest w pkt 8.1. Teksty wpisane na sztywno w `pzt_opis_a.py:189` i `pzt_opis_c.py:61`.
10. PZT tab. 3: długości z pola `dl` modelu różnią się od geometrii tras, które pokazuje PZT-03:

    | Trasa | `dl` w modelu | geometria |
    |---|---|---|
    | kabel nN | 18,2 m | 21,0 m |
    | KD-E | 31,6 m | 32,45 m |
    | KD-W | 34,8 m | 34,49 m |

11. Odległość od najbliższego budynku sąsiedniego: PZT pkt 6 i tab. 11 — 13,72 m (123/5, od ścian); PAB tab. 14 — „min. 13,18 m” (123/3, od płyt). Wymaganie dla okapów i płyt: PZT tab. 11 „≥ 1,50 m”, PAB tab. 11 „≥ 4,00 m”.
12. BIOZ pkt 3: „kabel nN 0,” — obcięte „0,4 kV” (`zl_zalaczniki.py:62`, podział po przecinku). „Osłony z lamel (4 pól)” — LAM-P0 to ekran wewnętrzny; osłony elewacyjne są 3 (PAB tab. 4). Forma „pól” jest też błędna gramatycznie.
13. PAB 10.4: produkcja PV 5 610 kWh/rok (elektryka.pv), a EP liczy z E_PV = 4 985 kWh/rok (energia.pv). Bufor „min. 80 dm³”, a w modelu 100 dm³.
14. Wewnętrzne adnotacje w tekście urzędowym:
    - PZT tab. 1: „(powiększona — weryfikacja §6 B6)”, „K-2”;
    - PAB tab. 1: „(brief: I — korekta)”;
    - zapis liczb z kropką: „DN150 i=0.02”, „Q3=6.3” (PAB 9.1 i 12.2);
    - przykanalik: „DN150” w PAB wobec „PVC-U 160” w PZT.
15. PZT tab. 8 pkt 8: „0,95 m przed linią (T2)” — sformułowanie dwuznaczne (sugeruje przekroczenie linii). PAB mówi „rezerwa 0,95 m”.
16. Głębokość posadowienia podana trzema wartościami o różnych definicjach: PZT pkt 3.6 „≈ 0,5 m p.p.t.” (tekst z modelu, DR-0), drenaż 0,56 m, PAB 5.2 0,34 m (od t_min). Należy ujednolicić albo podać definicję.
