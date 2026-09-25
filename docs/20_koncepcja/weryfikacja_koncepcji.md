# Dom LAMELA — niezależna weryfikacja koncepcji ostatecznej i podglądy uzupełniające

Data: 2026-09-25. Dokument uzupełnia `docs/20_koncepcja/koncepcja.md`. Nie zastępuje go i nie zmienia bilansu w §9, który generuje
`tools/podglad_modelu.py`. Zakres:
1. niezależne przeliczenie wskaźników z modelu i porównanie z §9;
2. porównanie U w §6 z obliczeniem;
3. sprawdzenie w modelu przeszczepów i poprawek;
4. opis wykonanych podglądów: arkusze, PZT, 3D;
5. lista błędów i niespójności do audytu i poprawek.

**Stan modelu.** Wszystkie liczby dotyczą tego samego stanu modelu co §9 koncepcji: pliki z 04:19:44 UTC, walidacja 0 błędów i 0 ostrzeżeń.

| plik | SHA-256 |
|---|---|
| `model/budynek.yaml` | `d238ec0e…ecf11d` |
| `model/dzialka.yaml` | `0e576be3…19848b` |

Po każdej zmianie modelu wyniki trzeba przeliczyć (Aneks A).

**Podstawy.**
* WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu obowiązującym do 19.09.2026. Stosowane na podstawie art. 102a PB.
* MPZP 3MN — uchwała fikcyjna **[DANE PRZYKŁADOWE – FIKCYJNE]**. Działka 123/4, uzbrojenie i teren też są fikcyjne.
* PN-ISO 9836:2022-07 z modyfikacjami RPB §20 (W-316).
* Identyfikatory `W-xxx` odsyłają do `docs/10_podstawy_prawne/00_rejestr_wymagan.md`.

---

## 1. Metoda

Liczby pochodzą wyłącznie z plików modelu i zostały policzone skryptami w scratchpadzie sesji; nie wpisywano ich ręcznie. Użyto API
`lamela.model`: `load_model`, `zestawienie_powierzchni`, `pow_zabudowy`, `pow_brutto_kondygnacji`, `kubatura_brutto`, `obrys_kondygnacji`.
Geometrię (PBC, odległości, teren na obwodzie, ważenie wysokości pod schodami) liczono w shapely/scipy. Użyto też IR
`lamela.ir.build_ir` (najwyższe punkty) oraz modułów obliczeniowych repozytorium:
* `lamela.obliczenia.fizyka_energia` — U, mostki, EP, Φ_HL, wentylacja;
* `lamela.obliczenia.instalacje` — deszczówka i retencja, drenaż, ogrzewanie podłogowe, elektryka, PV.

Raporty modułów zostały w scratchpadzie i nie należą do repozytorium. Da się je odtworzyć poleceniami z Aneksu A.

## 2. Wskaźniki — porównanie z §9 koncepcji

| wskaźnik | §9 `koncepcja.md` | weryfikacja niezależna | metoda / uwagi | wymaganie | ocena |
|---|---|---|---|---|---|
| PU wg RPB §20 / W-316 | **240,24 m²** | **240,24 m²**: P0 96,29, P1 84,39, P2 59,57 | Σ pow. zaliczonych bez klatek 0.04/1.06/2.06, garażu 0.13 i pom. technicznych. Spiżarnia 0.05 liczona w 50 % wg umownej wysokości 1,90 m z modelu | 230–270 m² (brief §4) | ✓ |
| PU — wariant z geometrycznym ważeniem spiżarni | — | **239,26 m²** | Pod biegiem 2 i spocznikiem liczono rzeczywistą wysokość (spocznik +1,575, płyta 0,18 m → pod spocznikiem 1,37 m). Wynik: 0,98 m² × 100 %, 1,47 m² × 50 %, 2,95 m² × 0 %, razem 1,72 m² zamiast 2,70 m² (W-316: ≥ 2,20 → 100 %, 1,40–2,20 → 50 %, < 1,40 → 0 %) | jw. | ✓ |
| PU z pasem 1.06 na P1 | — | 240,73 m² | 1.06 ma 0,49 m² podłogi przy wyjściu z biegu na P1. W-316 wyłącza schody i podesty, a ten pas można uznać za komunikację | jw. | ✓ |
| wartość PU podana wcześniej przez syntezę | 241,07 m² (komunikat syntezy) | **nie potwierdzono** | W obecnym modelu 240,24 m² (−0,83 m²) | — | — |
| kategorie PN-ISO 9836 w PU | — | podstawowa 158,78; pomocnicza bez garażu 41,16; ruchu bez klatek 40,30 m² | Garaż 37,42 m² i pom. techniczne 16,24 m² wykazano osobno (W-316) | — | — |
| powierzchnia zabudowy | 187,50 m² (11,72 %) | **187,50 m²** (11,72 %) | Obrys P0 z ETICS 181,78 m² + wspornik bryły A na P2 5,73 m² (W-030). Rama C nie jest kubaturą, więc jej nie wliczono. Z rzutem płyt wysuniętych: 212,99 m² (13,31 %) | ≤ 480 m² (30 %, MPZP, W-030) | ✓ |
| PBC | 1 281,57 m² (80,10 %) | **1 271,31 m²** (79,46 %) | Z PBC wyłączono sumę geometryczną 328,69 m²: budynek P0 181,78; taras T1 63,08; podesty T2 2,99 i T3 1,30; U1 48,61; U2 9,04; U3 1,05; U4 4,16; U5 1,12; U6 ażur 0,90 (W-031: ażur nie jest PBC); opaska żwirowa 0,5 m 29,95. Dachu zielonego D4 (63,97 m²) nie liczono. Różnica wobec §9 wynosi 10,26 m² i wynika z ujęcia opaski lub ażuru **[DO WYJAŚNIENIA w `podglad_modelu.py`]** | ≥ 800 m² (50 %, W-031) | ✓ |
| intensywność zabudowy | 0,248 | **0,248** | (181,78 + 117,81 + 96,80) / 1600 = 396,39 / 1600 | 0,05–0,80 (W-032) | ✓ |
| wysokość zabudowy (upzp art. 2 pkt 30) | 10,25 m | **10,02 m** do attyki; **10,25 m** z czerpnią/wyrzutnią | Attyka D1 +9,776 (111,426 m n.p.m.). Teren istniejący na obwodzie ścian P0: min 101,328, max 101,479, średnia 101,404 m n.p.m.; TIN terenu projektowanego daje przy licach te same rzędne. Czerpnia +9,95 i wyrzutnia +10,00 (`energia.wentylacja`) są najwyższymi punktami (W-033) → 10,25 m. PV wystaje ponad attykę o 0,05 m (§6 poz. A4) → 10,07 m do PV | ≤ 11,00 m; z rezerwą ≤ 10,70 m (W-033) | ✓ |
| wysokość budynku wg WT §6 | 9,85 m | 9,79–9,85 m | Narzędzia dają różne wartości. Arkusze PB-AR-05…10 przyjmują teren −0,267 i wierzch pokrycia +9,526, co daje 9,79 m. `podglad_modelu.py` przyjmuje teren przy najniższym wejściu −0,326, co daje 9,85 m (§6 poz. C5) | grupa N ≤ 12 m (WT §8 pkt 1, W-063) | ✓ |
| kubatura brutto | 1 354,5 m³ | **1 354,5 m³** | PN-ISO 9836 p. 5.2 z rdzenia. Składniki: P0 578,05 + P1 345,18 + P2 283,63 + płyty ST1 26,83, ST2 21,76, ST2Z 1,80, D1 44,14, D2 8,43, D3 7,69, D4 37,03 m³ | > 1000 m³ → PWP (WT §183, W-190) | — |
| kondygnacje nadziemne / miejsca postojowe | 3 / 4 | 3 / 4 (MP1–MP4 w `dzialka.yaml`) | — | ≤ 3 (W-034); ≥ 2 (W-036) | ✓ |
| odległość budynku od jezdni 1KDD | — | 9,88 m | Lico ściany pn. garażu do krawędzi jezdni | ≥ 6,0 m (u.d.p. art. 43, W-007) | ✓ |
| jednostka zewnętrzna PC od granicy E | 7,00 m (§8, bilans) | 6,90 m od krawędzi fundamentu U5; 7,60 m od środka urządzenia | `dzialka.yaml`: U5, PC-JZ | ≥ 6,0 m (W-024) | ✓ |
| EP | szacunek J2: 55–59 (§7) | **57,2 kWh/(m²·rok)** | Moduł fizyki: A_f 262,74 m², H_tr 276,5 W/K, H_ve 37,2 W/K, H_TB 137,6 W/K (Ψ domyślne PN-EN ISO 14683 / przykładowe łączniki), EU/EK 74,7/32,7. Wrażliwość: Ψ „dobra praktyka” → 40,8; n50 = 4 h⁻¹ → 68,0; bez PV → 81,8 (> 70) | ≤ 70 (WT §329, W-240) | ✓ |
| obciążenie cieplne Φ_HL | — | 11,48 kW (43,7 W/m²) | PN-EN 12831, θ_e = −18 °C. Wynik jest zawyżony przez domyślne Ψ; zob. §6 poz. B4 | — | — |

Odległości od granic w §9 (tabela generowana) zgadzają się z weryfikacją do 0,01 m:
* W: 7,30 m (ściany P0/P1), 6,30 m (P2), 5,20 m (płyty PL-2/PL-3), 4,30 m (taras T1);
* E: 5,725 m (garaż);
* N: 1,625 m za linią zabudowy (brama garażu), 0,95 m za linią (daszek PL-DA).

Spełniają W-001, W-004 i W-006, a daszek ma zapas ≥ 0,30 m wymagany przez J1.

## 3. Współczynniki U — §6 koncepcji wobec obliczenia z modelu

Obliczenia: PN-EN ISO 6946:2017-10 z poprawkami ΔU oraz PN-EN ISO 13370 dla podłogi na gruncie, moduł
`lamela.obliczenia.fizyka.u_przegrody`. Wymagania: WT zał. 2 pkt 1.1 (W-243). Cele projektu: W-245.

| kod | U w §6 i w nazwie przegrody | U obliczone | U_max WT | cel W-245 | uwagi |
|---|---|---|---|---|---|
| SZ1 | 0,15 | **0,17** | 0,20 ✓ | 0,15 ✗ | ΔU łączników 0,021; opis w modelu i w §6 zaniża U |
| SZ2 | 0,16 | **0,17** | 0,20 ✓ | 0,15 ✗ | — |
| SZL | 0,10 | 0,099 | 0,20 ✓ | ✓ | — |
| SWG (dom–garaż) | 0,26 (nazwa: 0,24) | **0,27** | 0,30 ✓ | 0,25 ✗ | — |
| SD1 | 0,10 | 0,11 | 0,15 ✓ | 0,12 ✓ | — |
| SD2 | 0,11 | 0,12 | 0,15 ✓ | 0,12 ✓ | — |
| DZ1 (nad pasem gosp.) | 0,12 | **0,13** | 0,15 ✓ | 0,12 ✗ | Poprawka J2 nr 4 (U ≤ 0,15) spełniona |
| POD-0 | 0,13 (nazwa: 0,14) | 0,11 (U_equiv) | 0,30 ✓ | 0,20 ✓ | A = 110,65 m², B′ = 4,04 m |
| ST2Z / SUF-ZEW | 0,15 | 0,13 | 0,15 ✓ | — | — |
| stolarka | U_w 0,73–0,90 (deklaracje) | 0,61–0,89; **FX3 1,0** | 0,9 (drzwi 1,3) | 0,80 | FX3 to doświetle 0,35 × 2,40 m z dużym udziałem ramy. Jako okno nie spełnia 0,9; można je liczyć z drzwiami DZ1 (≤ 1,3) albo zmienić profil |

Inne wyniki modułu fizyki dla tego stanu modelu:
* g ≤ 0,35: 22/22 okien spełnia (W-247);
* kondensacja międzywarstwowa: 9/9 przegród dopuszczalnych (PN-EN ISO 13788);
* ciągłość „4 linii”: 11/11 przegród;
* izolacja obwodowa: R = 2,78 m²K/W ≥ 2,0 (WT zał. 2 pkt 1.4);
* f_Rsi: 16 węzłów `wezly` nie ma jeszcze symulacji PN-EN ISO 10211 (W-248). Ψ pochodzą z wartości domyślnych PN-EN ISO 14683 oraz przykładowych deklaracji łączników **[DANE PRZYKŁADOWE – FIKCYJNE]**.
