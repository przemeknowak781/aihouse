# Weryfikacja niezależna tomów PT — obliczenia i spójność faktów

Data: 2026-09-25, godz. ok. 07:50. Weryfikator: niezależny, sceptyczny (zakres: OBLICZENIA). Nie wprowadzałem poprawek.

Przedmiot weryfikacji:

* `projekt/wydanie/PT_1_AR_2026.09.25.pdf` (wygenerowany o 06:52), `PT_2_BO_…` (07:27), `PT_3_IS_…` (07:17), `PT_4_IE_…` (07:31);
* źródła Markdown w `projekt/09_opis_i_zalaczniki/PT_*/`;
* generatory `tools/dokumenty/tom_PT_*.py`, `pt_is_*.py`, `pt_ie_*.py`.

Metoda: obliczenia `fizyka_energia.oblicz_wszystko` (ψ z modelu oraz ψ z `wyniki_mostki.json`) i `instalacje.oblicz_wszystko`
uruchomiłem na kopii `src` w katalogu roboczym, na **bieżącym** modelu (`model/budynek.yaml` z 07:34). Do tego doszły
obliczenia ręczne (ISO 6946, ISO 13370, EC2, N SEP-E-002) oraz odczyt `wyniki.json`, `kontrola_zbrojenia.json`
i `obliczenia_statyczne.md` zespołu BO.

## 1. Wyniki odtworzone poprawnie (bez uwag)

| Obszar | Wartość w tomie | Odtworzenie |
|---|---|---|
| U SZ1 (ISO 6946 + ΔU_g + ΔU_f) | R_T 6,872; U 0,17 | 0,13+0,0375+0,200+6,452+0,0125+0,04 = 6,872; U = 0,1455+0,0088+0,012 = 0,166 |
| U SWG (R_se = R_si) | 3,938; 0,27 | zgodne; spełnia U_max = 0,30 |
| U SZL (metoda kresów) | R′/R″ 10,69/10,02 | 10,687 / 10,022; błąd względny 3,2 % |
| Kliny SD1 / DZ1 (zał. C) | U_śr 0,104 / 0,120 | R₁ = Δd/λ; U = ln(1+R₁/R₀)/R₁ → 0,1044 / 0,1197 |
| Podłoga POD-0 (ISO 13370 z izolacją krawędziową) | B′ 4,34; d_t 15,89; U 0,11 | U = 0,1119; Ψ_edge = −0,0098 → U′ = 0,107 |
| Σψ·l + Σχ | H_TB = 30,63 W/K | 29,876 + 0,75 = 30,626 (model); 30,658 (symulacje) |
| Φ_HL, EP (A / A0) | 7,41 kW; 35,59 / 57,85 | 7,408 kW; 35,59 / 57,85 (model z 07:34) |
| Sprawności η_tot | 3,84 / 1,78 | 4,5·1,0·0,96·0,89 = 3,845; 3,2·0,929·0,60 = 1,784 |
| Wentylacja | 365/365; minimum wywiewu 362 | Σ z tabeli 365/365; Σ wyw_min = 361,8 |
| Kanalizacja, wodomierz | Q_ww 2,27 l/s; q 1,128 dm³/s | 0,5·√20,6 = 2,269; 1,128·3,6 = 4,06 m³/h |
| WLZ ∆U, I_B, bilans | 0,61 %; P_s 41,32 kW; 26,2 kW / 39,8 A | √3·40·28,3·r/400 → 0,608 %; Σk_j·P = 41,32; 26 210/(√3·400·0,95) = 39,8 A |
| Obwody | I_B, Z_s, I_k1 | D1 10,68 A; D6 12,22 A; G12 Z_s 0,683 Ω — zgodne |
| PV | 6,45 kWp; U_oc,max 350 V | 15 × 430 Wp; 8 × 43,75 V |
| l_bd B500SP / C25/30 (γ_c = 1,4) | φ12: 451 / 644 mm | f_bd = 2,893 MPa → 450,9; η₁ = 0,7 → 644; α₆ = √2 |
| Mur (W-270) | f_d = 4,50 MPa | 7,66/1,7 = 4,506 |
| Poz. 6.11 (ścinanie, V_Rd,max) | 147,49 kN | 180·192·0,54·17,86/2,256 ≈ 147,5 |
| Kubatura strefy (PWP) | 1 354,40 m³ | Σ składników = 1 354,42 |

## 2. Problemy krytyczne

**K-1. PT-2 BO — tom nie może być podpisany ani wydany.** Tom sam wykazuje 31 pozycji NIEZAMKNIĘTYCH:

* η > 100 % w pozycjach: PL-2 336 %, S0-01 541 %, S1-06 382 %, S0-10 367 % i 10 innych ścianach;
* docisk do podłoża 114 %;
* zbrojenie PF1+PF2 niewykonalne w grubości płyty (4 299 < 5 243 mm²/m);
* zbrojenie na ścinanie płyt poza kontrolą rysunków.

Wyniki `wyniki.json` (06:33), MES (06:48) i kontroli zbrojenia (06:48) są starsze niż model, który od złożenia tomu
zmienił się jeszcze raz (07:34). Bez ponownej analizy i zamknięcia tych pozycji oświadczenie projektanta PT
z art. 41 ust. 4a pkt 2 PB nie może być złożone.

**K-2. PT-2 BO, poz. 6.11 (nadproże N-O0-18) — pozycja uznana za spełnioną, choć zbrojenie ściskane jest za małe.**

* Obliczenie daje przekrój podwójnie zbrojony: μ = 0,486 > μ_lim = 0,372 i A_s2 = **235 mm²**.
* Kontrola rysunku PT-BO-25 przyjmuje górą 2Ø12 = **226 mm²** < 235 mm². Sprawdza tylko warunek 0,15·A_s,dół = 181 mm².
* Wysokość użyteczną d = 213 mm przyjęto dla jednej warstwy prętów. Kontrola zbrojenia podaje jednak dołem 6Ø16
  „w 2 warstwach (3 + 3)”. Wtedy d ≈ 192 mm, M_lim ≈ 44 kNm i A_s2 ≈ 430 mm², czyli prawie dwa razy więcej niż 226 mm².
* W wnioskach pozycji jest „wszystkie warunki spełnione”, a zbrojenia górnego nie wymieniono.

Wniosek: sprawdzić A_s2 ≤ A_s,górą w module i w kontroli rysunków. Nadproże zwiększyć albo zespolić ze stropem.

## 3. Problemy istotne

**I-1. Cztery tomy powstały z czterech różnych stanów modelu.**

| Tom | Stan modelu użyty w tomie |
|---|---|
| AR | ok. 06:50 |
| IS | 06:48 |
| BO | 07:16 |
| IE | 07:28 |
| model bieżący | 07:34 |

Przykłady rozbieżności:

* odwodnienie dachów w IS: Q = 11,46 l/s, a obecnie 12,51 l/s (A = 249,0 m²);
* H_TB: AR 30,63 W/K, IS 30,7 W/K.

Po zamrożeniu modelu trzeba wygenerować ponownie wszystkie 4 tomy i arkusze IS/IE/BO w jednym przebiegu.

**I-2. Numeracja pomieszczeń niezgodna między tomami i rysunkami.**

* PT-1 AR i wszystkie arkusze (`numeracja_pomieszczen: iso`) mają parter = 1.xx.
* Części opisowe PT-3 IS i PT-4 IE mają identyfikatory modelu: parter = 0.xx. Przykłady: RG w „0.12”; tabela strumieni
  powietrza; tabele obwodów G1–G12; temperatury θ_i.

Ten sam numer oznacza różne pomieszczenia w różnych tomach. Na przykład 1.06 to klatka schodowa w IS/IE, a salon w AR.

**I-3. Instalacja PV opisana na trzy sposoby.**

| Źródło | Rozmieszczenie | Produkcja |
|---|---|---|
| model `energia.pv.pola` | D1 — 8 modułów, D4 — 7 modułów (biosolarny) | — |
| AR, nazwa przegrody DZ1 | „8 modułów” nad garażem | — |
| PT-4 IE | 15 modułów na D1, EW10, „nie wystają ponad attykę 0,35 m” | 5 610 kWh/rok (PVGIS); E_PV,tech = 2 451 kWh/rok |
| EP w PT-3 IS | moduł własny: azymut 180°, 10°, PR 0,78 | 4 985 kWh/rok; E_PV,sys = 2 337 kWh/rok |

Tom IE pisze, że wartość 2 451 kWh/rok jest „przekazana do charakterystyki energetycznej (PT-3 IS)”. To nieprawda:
EP A liczono z 2 337 kWh/rok. Trzeba ujednolicić rozmieszczenie (model), źródło produkcji i E_PV do EP.

**I-4. Dane wejściowe EP (PT-3 IS) odbiegają od zaprojektowanej instalacji.**

* **Pompa ciepła.** EP liczono dla PC „7–8 kW” z SCOP = 4,50. Dobór i zasilanie (IS/IE) dotyczą PC-R290-07:
  P(A−7/W35) = 6,2 kW, SCOP deklarowany 4,70, z bilansu godzinowego 4,09. Moc nominalna w innym miejscu tomu: 7,4 kW.
* **Zasobnik c.w.u.** EP przyjmuje zasobnik Z250 (strata 55 W, dezynfekcja 227 kWh/a). Projekt ma 400 dm³, a tekst IS
  podaje dezynfekcję 526 kWh/a. Tabela 7 tomu nie ujawnia, że liczono dla Z250.
* **Wpływ.** Szacuję EP A0 ≈ 57,9 → ok. 62 kWh/(m²·rok): SCOP 4,09 daje ok. +1,1, dezynfekcja ok. +2,9, a straty
  większego zasobnika jeszcze więcej. Wymaganie EP ≤ 70 jest nadal spełnione, ale wartości w tomie nie opisują
  zaprojektowanej instalacji.

**I-5. PT-4 IE — tekst i rysunek określają przewody, które nie spełniają wymagań.**

* WLZ w opisie, na trasie i w schemacie RG: YKY 5×16. Tom sam wykazuje ∆U = 0,61 % > 0,50 %.
* Obwód DC PV: H1Z2Z2-K 6 mm², ∆U = 1,04 % > 1 %.
* Zmiana na 5×25 i 10 mm² jest tylko w tabeli 2, z dopiskiem „do tego czasu obowiązuje przekrój z kolumny Rozwiązanie”.
  Tom zawiera więc dwa sprzeczne przekroje. Trzeba zmienić parametry obliczeń i przeliczyć.

**I-6. PT-2 BO — obciążenia dachów pominięte albo zaniżone.**

* Zestawienia obciążeń D1 (η = 99,9 %) i D4 (η = 97 %) nie zawierają ciężaru PV. Na D1 jest konstrukcja balastowa EW10,
  na D4 pole biosolarne. PT-4 IE odsyła „obciążenie dachu — PT-2 BO”.
* Tabela 6 BO: „substrat nasycony ≈ 1,4 kN/m²”. Obliczenia: 8 cm × 14,0 kN/m³ = 1,12 kN/m², czyli 1,4 t/m³,
  a nie 1,4 kN/m².
* Retencja maty drenażowej (IS: 30 dm³/m² dla substratu i maty) nie jest ujęta.
* Łącznie mogą brakować ok. 0,3–0,6 kN/m². Przy η = 97 % płyta D4 może przekroczyć 100 %.

**I-7. PT-2 BO, nadproża (poz. 6.x) — wartości q_k i q_d są nieweryfikowalne, a kombinacja 6.10b jest niepełna.**

* Wypisane q_k to suma przypadków QA + QA_pA + QA_pB + H + S1 + S2 + SB2 (`pozycje.py` l. 2178–2179). Obciążenia
  szachownicowe i alternatywne przypadki śniegu liczą się tam wielokrotnie, a do tego dochodzi sytuacja wyjątkowa.
* q_d liczone jest z QA, S2 i H. Przykład poz. 6.11: g_k = 117,83 i q_k = 71,33 dawałyby wg 6.10b 242 kN/m,
  a w pozycji jest 196,14.
* W 6.10b pominięto oddziaływania towarzyszące (człon `gQ·0,7·0`).
* W 6.10a obciążenie H łączy się ze śniegiem, choć PN-EN 1991-1-1 p. 3.3.2 na to nie pozwala.

**I-8. PT-2 BO — okapy obciążone jak taras.**

* Przegroda OK1 ma w modelu `typ: taras`, więc PL-E, PL-DA, PL-2 i PL-3 obciążono kat. A/I: 4,0 kN/m², Q_k 3,0 kN.
* Według PT-1 AR i modelu są to okapy i krawędzie niedostępne (rynny ukryte, bez balustrad). W-263 mówi „taras — nie dotyczy”.
* Założenie wpływa na PL-2 (η = 336 %) i na siły dla łączników termoizolacyjnych. Trzeba rozstrzygnąć funkcję płyt:
  kat. H 0,4 kN/m² albo taras z balustradą i warstwami tarasu w AR.

**I-9. PT-2 BO — podstawa prawna PT podana błędnie.** Tom podaje „art. 34 ust. 3 pkt 4 (projekt techniczny)”;
ta treść jest wpisana w generatorze `tom_PT_BO.py` l. 403. Rejestr (W-251, W-274) i PT-1 AR podają **art. 34 ust. 3 pkt 3**.

**I-10. PT-2 BO — pozycje ZASTĄPIONE i MES bez pełnego uzasadnienia.**

* Pozycje ZF i SF z niespełnioną głębokością posadowienia (η do 289 %) uznano za zastąpione izolacją obwodową.
  Tom sam pisze jednak, że tej izolacji (D = 1,0 m, d_n = 10 cm) nie sprawdzono wg PN-EN ISO 13793.
* W MES płyty przyjęto kat. A 2,0 kN/m² na całej powierzchni. W garażu obowiązuje kat. F: 2,5 kN/m² i Q_k = 20 kN
  (tabela 6 tomu).
* M₀ = 80 000 kPa w modelu i MES, a 100 000 kPa w obliczeniach statycznych.

**I-11. PT-1 AR — U_w obliczone większe niż wymagane, bez oceny w tabeli 42.** OZ1: 0,81 > 0,80. ON4: 0,82 > 0,80.
Tabela nie ma kolumny oceny U_w względem U_w,wym.

**I-12. PT-1 AR — U stropu ST2Z liczone z błędnym układem warstw (tabela 36).**

* Płyta ŻB 22 cm występuje dwa razy, a tynk leży między płytami. R_T jest zawyżone o 0,121 m²·K/W.
* Poprawnie R_T = 8,096 i U = 0,128. Wynik po zaokrągleniu się nie zmienia (0,13), ale tabela obliczeniowa w tomie jest błędna.
* Moduł fizyki (`warstwy_stropu`) wymaga poprawki. Tom PT-2 BO (ST2Z) ma warstwy poprawne.

## 4. Problemy drobne

* **D-1. H_TB z dwóch źródeł.** AR liczy H_TB z ψ projektowych modelu (30,63), a IS z `wyniki_mostki.json` (30,66 → „30,7”).
  AR pisze przy tym, że H_TB „do charakterystyki energetycznej w PT-3 IS”.
* **D-2. Niespójne założenia U dla przegród zewnętrznych.** SZ2 i ST2Z mają ΔU_f = 0, choć wełnę mocuje się łącznikami
  (SZ1: ΔU_f = 0,012; SZ2 → ok. 0,18, ST2Z → 0,14 ≤ U_max). SZ2 i SZL mają R_se = 0,04 przy elewacji wentylowanej,
  a ST2Z R_se = R_si. Membrana SZ2 ma w obliczeniu d = 10 mm (R = 0,059).
* **D-3. Tabela Glasera AR (tabela 40).** Kolumna M_a,max podaje 0,243–0,338 g/m², a ocena „M_a,max = 0 g/m²”.
  W przypisie jest zbędny tekst „przestrzeń nieogrzewana 0.13”.
* **D-4. Wysokość attyki.** „h attyki” D1 = 0,35 m (tabela 49 AR) to jedna wartość. Z rzędnych modelu wychodzi
  korona 9,876 − pokrycie 9,426…9,626 = 0,25–0,45 m. BO liczy zaspę dla h = 0,35 m (μ₂ = 0,8). Przy wpustach
  h = 0,45 m daje μ₂ = 1,0 i s = 0,90 zamiast 0,72 kN/m².
* **D-5. Wewnętrzne niespójności PT-3 IS:**
  * niecka: 8,4 m³ (model, 28 m²) i 5,85 m³ (moduł, 19,5 m²);
  * PC od granicy E: 7,0 m (opis) i 7,60 m (obliczenie hałasu);
  * roczne ciepło na ogrzewanie: 11 202 kWh/a (moduł ogrzewania, podstawa SCOP 4,09 i udziału grzałki)
    i Q_H,nd = 4 481 kWh/a (EP);
  * „14 wpustów dachowych” i 9 pól, a AR (tabela 49) ma 6 wpustów WP1–WP6, płyty PL-* mają rynny ukryte.
* **D-6. PT-4 IE:**
  * CRL opisano jako „krytyczną długość linii”; wg PN-HD 60364-4-443 p. 443.5 to obliczeniowy poziom ryzyka;
  * wzór DLM daje 24,32 + 2,01 = 26,33 kW, a w wyniku jest 26,2 kW (podział na fazy); L1 = 40,00 A przy C40, bez zapasu;
  * rekuperator D9 ma 0,18 kW, a IS podaje moc wentylatorów 102 W.
* **D-7. Tabela 26 AR.**
  * Kolumna U_cel jest podana bez oceny, a cele nie są osiągnięte: SZ1 i SZ2 0,17 > 0,15; SWG 0,27 > 0,25; DZ1 0,13 > 0,12.
  * Wiersz POD-0 ma R_T z R_si, choć przypis mówi, że to R_f.
* **D-8. PT-2 BO — rysunki i generator.**
  * Lista uwag AUD-RYS nie zgadza się z wykazem rysunków: PT-BO-05, -11 i -14 raz są „ZBROJENIE…”, raz „ZESTAWIENIE STALI”.
  * W `tom_PT_BO.py` l. 748–753 wpisano na sztywno „≈ 0,6 (opis)” i „18,5” (kolumna MES).

## 5. Zalecana kolejność

1. Zamrozić model.
2. Zespół BO: I-7 (kombinacje i A_s2) oraz K-2, potem ponowna analiza. Rozstrzygnąć I-8 i I-6.
3. Ujednolicić PV i dane PC/zasobnika w `energia` i `instalacje.wyroby` (I-3, I-4).
4. Poprawić parametry WLZ/DC (I-5) i numerację w IS/IE (I-2).
5. Wygenerować ponownie arkusze i 4 tomy w jednym przebiegu. Powtórzyć weryfikację.
