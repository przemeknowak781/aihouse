# Walidacja solvera mostków 2D (`lamela.obliczenia.mostki2d`) — PN-EN ISO 10211:2017 zał. C

Metoda: objętości skończone na siatce prostokątnej zagęszczanej przy granicach materiałów, warunki Robina (h = 1/R_s), rozwiązanie bezpośrednie (scipy.sparse, SuperLU). Kryterium normy dla metody dokładnej 2D: temperatury ± 0,1 K, strumień ± 0,1 W/m.

| Przypadek | Wynik | max. odchyłka θ [K] | odchyłka Φ [W/m] | Tolerancja |
|---|---|---|---|---|
| ISO 10211 zał. C — przypadek 1 (28 punktów, tabela normy) | **SPEŁNIA** | 0,0481 | — | Δθ w ± 0,1 K |
| ISO 10211 zał. C — przypadek 2 (punkty A…I + strumień) | **SPEŁNIA** | 0,0387 | −0,0097 | Δθ w ± 0,1 K; ΔΦ w ± 0,1 W/m |
| Przypadek 2 — niezależność od siatki (h_min = 0,5 i 0,1 mm; punkty D, G, Φ) | **SPEŁNIA** | 0,0341 | — | Δθ w ± 0,1 K; ΔΦ w ± 0,1 W/m na każdej siatce |
| A1 — ściana warstwowa 1D (Robin), rozwiązanie dokładne | **SPEŁNIA** | 0,0000 | — | Δθ w ± 10⁻⁶ K; ΔU w ± 10⁻⁹ |
| A2 — przypadek 1 vs szereg Fouriera (bez zaokrągleń) | **SPEŁNIA** | 0,0018 | — | Δθ w ± 0,02 K |
| A3 — naroże 90°, powierzchnie izotermiczne: ΔS = S − (a+b)/t | **SPEŁNIA** | — | — | ΔS = 0,559 ± 0,01 |

## ISO 10211 zał. C — przypadek 1 (28 punktów, tabela normy)

Siatka: 81 × 145 = 11745 komórek; Δx ∈ [1.94; 19.72] mm, Δy ∈ [1.94; 19.86] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| 1.1 | (0.25; 1.75) | 9,7000 | 9,6576 | −0,0424 |
| 1.2 | (0.50; 1.75) | 13,4000 | 13,3788 | −0,0212 |
| 1.3 | (0.75; 1.75) | 14,7000 | 14,7282 | +0,0282 |
| 1.4 | (1.00; 1.75) | 15,1000 | 15,0846 | −0,0154 |
| 2.1 | (0.25; 1.50) | 5,3000 | 5,2519 | −0,0481 |
| 2.2 | (0.50; 1.50) | 8,6000 | 8,6412 | +0,0412 |
| 2.3 | (0.75; 1.50) | 10,3000 | 10,3147 | +0,0147 |
| 2.4 | (1.00; 1.50) | 10,8000 | 10,8097 | +0,0097 |
| 3.1 | (0.25; 1.25) | 3,2000 | 3,1904 | −0,0096 |
| 3.2 | (0.50; 1.25) | 5,6000 | 5,6101 | +0,0101 |
| 3.3 | (0.75; 1.25) | 7,0000 | 7,0140 | +0,0140 |
| 3.4 | (1.00; 1.25) | 7,5000 | 7,4649 | −0,0351 |
| 4.1 | (0.25; 1.00) | 2,0000 | 2,0142 | +0,0142 |
| 4.2 | (0.50; 1.00) | 3,6000 | 3,6409 | +0,0409 |
| 4.3 | (0.75; 1.00) | 4,7000 | 4,6578 | −0,0422 |
| 4.4 | (1.00; 1.00) | 5,0000 | 4,9995 | −0,0005 |
| 5.1 | (0.25; 0.75) | 1,3000 | 1,2622 | −0,0378 |
| 5.2 | (0.50; 0.75) | 2,3000 | 2,3091 | +0,0091 |
| 5.3 | (0.75; 0.75) | 3,0000 | 2,9862 | −0,0138 |
| 5.4 | (1.00; 0.75) | 3,2000 | 3,2186 | +0,0186 |
| 6.1 | (0.25; 0.50) | 0,7000 | 0,7399 | +0,0399 |
| 6.2 | (0.50; 0.50) | 1,4000 | 1,3597 | −0,0403 |
| 6.3 | (0.75; 0.50) | 1,8000 | 1,7669 | −0,0331 |
| 6.4 | (1.00; 0.50) | 1,9000 | 1,9083 | +0,0083 |
| 7.1 | (0.25; 0.25) | 0,3000 | 0,3417 | +0,0417 |
| 7.2 | (0.50; 0.25) | 0,6000 | 0,6297 | +0,0297 |
| 7.3 | (0.75; 0.25) | 0,8000 | 0,8201 | +0,0201 |
| 7.4 | (1.00; 0.25) | 0,9000 | 0,8863 | −0,0137 |

bilans energii: 5.3e-14

## ISO 10211 zał. C — przypadek 2 (punkty A…I + strumień)

Siatka: 307 × 145 = 44515 komórek; Δx ∈ [0.0863; 1.999] mm, Δy ∈ [0.0863; 1.904] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| A | (0; 47.5) mm | 7,1000 | 7,0639 | −0,0361 |
| B | (500; 47.5) mm | 0,8000 | 0,7613 | −0,0387 |
| C | (0; 41.5) mm | 7,9000 | 7,8970 | −0,0030 |
| D | (15; 41.5) mm | 6,3000 | 6,2719 | −0,0281 |
| E | (500; 41.5) mm | 0,8000 | 0,8275 | +0,0275 |
| F | (0; 36.5) mm | 16,4000 | 16,4084 | +0,0084 |
| G | (15; 36.5) mm | 16,3000 | 16,3341 | +0,0341 |
| H | (0; 0) mm | 16,8000 | 16,7677 | −0,0323 |
| I | (500; 0) mm | 18,3000 | 18,3337 | +0,0337 |
| Φ [W/m] | HI → AB | 9,5000 | 9,4903 | −0,0097 |

bilans energii: 3.8e-10; Φ_AB = 9.4903 W/m

## Przypadek 2 — niezależność od siatki (h_min = 0,5 i 0,1 mm; punkty D, G, Φ)

Siatka: 132 × 62 = 8184 komórek; Δx ∈ [0.459; 4.964] mm, Δy ∈ [0.466; 3.47] mm | 307 × 145 = 44515 komórek; Δx ∈ [0.0863; 1.999] mm, Δy ∈ [0.0863; 1.904] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| D | h_min = 0,5 mm (8184 kom,) | 6,3000 | 6,2708 | −0,0292 |
| G | h_min = 0,5 mm (8184 kom,) | 16,3000 | 16,3341 | +0,0341 |
| Φ [W/m] | h_min = 0,5 mm | 9,5000 | 9,4874 | −0,0126 |
| D | h_min = 0,1 mm (44515 kom,) | 6,3000 | 6,2719 | −0,0281 |
| G | h_min = 0,1 mm (44515 kom,) | 16,3000 | 16,3341 | +0,0341 |
| Φ [W/m] | h_min = 0,1 mm | 9,5000 | 9,4903 | −0,0097 |

Niezależny solver węzłowy (weryfikator): G = 16,334 °C, D = 6,273 °C (zbieżne 13k–210k węzłów). Przed poprawką (średnia arytmetyczna rekonstrukcji z 4 komórek wokół wierzchołka) G zależało od siatki: 16,108 (h_min 0,5 mm — poza tolerancją) … 16,273 (siatka walidacyjna) … 16,313 °C.

## A1 — ściana warstwowa 1D (Robin), rozwiązanie dokładne

Siatka: 111 × 45 = 4995 komórek; Δx ∈ [0.914; 18.7] mm, Δy ∈ [0.973; 19.46] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| θ_si | x = 0.000 | 19,2844 | 19,2844 | +0,0000 |
| styk 1/2 | x = 0.015 | 19,0779 | 19,0779 | +0,0000 |
| styk 2/3 | x = 0.195 | 17,7910 | 17,7910 | +0,0000 |
| styk 3/4 | x = 0.395 | −17,7248 | −17,7248 | −0,0000 |
| θ_se | x = 0.402 | −17,7798 | −17,7798 | −0,0000 |
| U [W/(m²K)] | — | 0,1449 | 0,1449 | −0,0000 |

## A2 — przypadek 1 vs szereg Fouriera (bez zaokrągleń)

Siatka: 81 × 145 = 11745 komórek; Δx ∈ [1.94; 19.72] mm, Δy ∈ [1.94; 19.86] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| 1.1 | (0.25; 1.75) | 9,6582 | 9,6576 | −0,0006 |
| 1.2 | (0.50; 1.75) | 13,3791 | 13,3788 | −0,0002 |
| 1.3 | (0.75; 1.75) | 14,7289 | 14,7282 | −0,0007 |
| 1.4 | (1.00; 1.75) | 15,0854 | 15,0846 | −0,0008 |
| 2.1 | (0.25; 1.50) | 5,2517 | 5,2519 | +0,0002 |
| 2.2 | (0.50; 1.50) | 8,6406 | 8,6412 | +0,0007 |
| 2.3 | (0.75; 1.50) | 10,3155 | 10,3147 | −0,0008 |
| 2.4 | (1.00; 1.50) | 10,8106 | 10,8097 | −0,0009 |
| 3.1 | (0.25; 1.25) | 3,1887 | 3,1904 | +0,0018 |
| 3.2 | (0.50; 1.25) | 5,6090 | 5,6101 | +0,0011 |
| 3.3 | (0.75; 1.25) | 7,0142 | 7,0140 | −0,0002 |
| 3.4 | (1.00; 1.25) | 7,4651 | 7,4649 | −0,0002 |
| 4.1 | (0.25; 1.00) | 2,0142 | 2,0142 | +0,0001 |
| 4.2 | (0.50; 1.00) | 3,6406 | 3,6409 | +0,0003 |
| 4.3 | (0.75; 1.00) | 4,6582 | 4,6578 | −0,0003 |
| 4.4 | (1.00; 1.00) | 5,0000 | 4,9995 | −0,0005 |
| 5.1 | (0.25; 0.75) | 1,2625 | 1,2622 | −0,0003 |
| 5.2 | (0.50; 0.75) | 2,3086 | 2,3091 | +0,0005 |
| 5.3 | (0.75; 0.75) | 2,9858 | 2,9862 | +0,0004 |
| 5.4 | (1.00; 0.75) | 3,2185 | 3,2186 | +0,0001 |
| 6.1 | (0.25; 0.50) | 0,7396 | 0,7399 | +0,0002 |
| 6.2 | (0.50; 0.50) | 1,3594 | 1,3597 | +0,0002 |
| 6.3 | (0.75; 0.50) | 1,7668 | 1,7669 | +0,0000 |
| 6.4 | (1.00; 0.50) | 1,9083 | 1,9083 | +0,0000 |
| 7.1 | (0.25; 0.25) | 0,3418 | 0,3417 | −0,0001 |
| 7.2 | (0.50; 0.25) | 0,6296 | 0,6297 | +0,0001 |
| 7.3 | (0.75; 0.25) | 0,8199 | 0,8201 | +0,0001 |
| 7.4 | (1.00; 0.25) | 0,8863 | 0,8863 | +0,0000 |

## A3 — naroże 90°, powierzchnie izotermiczne: ΔS = S − (a+b)/t

Siatka: 286 × 286 = 81796 komórek; Δx ∈ [0.481; 9.902] mm, Δy ∈ [0.481; 9.902] mm

| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |
|---|---|---|---|---|
| ΔS (siatka n) | t = 0.3, a = b = 1.2 | 0,5590 | 0,5578 | −0,0012 |
| ΔS (siatka 2n) |  | 0,5590 | 0,5585 | −0,0005 |

Wartość odniesienia 0,559 — kwadrat narożny ≈ 0,56 „kwadratu” (odwzorowanie konforemne); wzór Langmuira–Adamsa–Stevensa (1919) podaje 0,54 (przybliżenie).

## Weryfikacja niezależna i poprawki

Pakiet sprawdzili dwaj niezależni weryfikatorzy: (A) numeryczno-fizyczny — własny solver węzłowy MOS (vertex-centred), szereg Fouriera przypadku 1 (4001 wyrazów), testy skrajnych kontrastów λ, skalowania, szczelin, zbieżności katalogu; (B) zgodności z normami PN-EN ISO 10211:2017, 14683:2017, 13788:2013, 6946:2017, 13370:2017 (próbki norm iTeh, dane przypadku 2 z QuickField/SimScale/Physibel). Potwierdzone bez zmian: przypadek 1 zbieżny w 2. rzędzie do rozwiązania Fouriera; przypadek 2 poza punktem G zgodny z niezależnym solverem do 0,005 K, Φ = 9,4904 vs 9,4917 W/m; bilans 10⁻¹⁵…3·10⁻⁹; średnia harmoniczna λ i warunki Robina (ściana 1D ze skrajnymi warstwami — błąd U ≤ 5·10⁻¹⁰); ΔS naroża 0,5587; kierunki R_si, R_si = 0,25 w przebiegu f_Rsi, długości l_e/l_i; brak pustek w węzłach katalogu; obszar gruntu i płaszczyzny odcięcia.

| Nr | Waga | Uwaga weryfikatora | Poprawka |
|---|---|---|---|
| 1 | istotna | Temperatura w wierzchołku siatki na styku materiałów (przypadek 2, punkt G: aluminium / drewno / korek) liczona jako średnia arytmetyczna rekonstrukcji z 4 komórek — 1. rząd, zależna od siatki (h_min = 0,5 mm: G = 16,108 °C, poza tolerancją). | `Rozwiazanie.temperatura`: średnia rekonstrukcji ważona λ komórek (dla jednego materiału — bez zmian). Test regresji: przypadek 2 na siatkach h_min = 0,5 i 0,1 mm (tabela wyżej). |
| 2 | istotna | Szczeliny między wielobokami szersze niż tolerancja scalania (10⁻⁷ m) stawały się pustkami adiabatycznymi bez ostrzeżenia; bilans energii tylko raportowany. | (a) `siatka.kontroluj_pustki` — ValueError dla zamkniętych pustek wewnętrznych i dla ciągów komórek pustki ograniczonych z obu stron materiałem/strefą (położenie w komunikacie; `Wezel.dopusc_pustki` — wyjątek dla celowych wcięć); (b) współrzędne wierzchołków przyciągane do siatki 1 µm; (c) `oblicz_wezel` odrzuca rozwiązanie z bilansem ≥ 10⁻⁴ (ValueError). |
| 3 | drobna | θ_si,min i f_Rsi tylko w środkach ścian komórek — zawyżone o O(h_min) w narożu wewnętrznym i na styku ościeża z ramą. | `theta_si_min` sprawdza też wierzchołki łamanej powierzchni (naroża, końce łańcuchów) — temperatura z rekonstrukcji ważonej λ; współczynniki wagowe g (3 temperatury) w tym samym punkcie. |
| 4 | drobna | Cienkie warstwy dobrze przewodzące (blachy, obróbki) — ψ zbieżne tylko w 1. rzędzie; kryterium 1 % strumienia nie kontroluje błędu ψ. | h_min ≤ grubość najcieńszego obszaru o λ ≥ 1; iloraz sąsiednich komórek na liniach granicznych ≤ 2; dodatkowe kryterium zbieżności |ΔL_2D| ≤ max(1 % |ψ|; 0,001 W/(m·K)) przy podwojeniu siatki (obok 1 % Φ wg ISO 10211). |
| 5 | drobna | `podzial` — OverflowError dla długich odcinków przy małym h_max (r**k przed ograniczeniem). | Wzrost komórek ograniczany przed potęgowaniem; resztę odcinka wypełniają komórki h_max liczone wprost. |
| 6 | drobna | Model gruntu i U podłogi (ISO 13370) z b = 8 m zamiast B' budynku. | `katalog_z_modelu`: b = B' = A/(0,5·P) z obrysu zewnętrznego parteru (model testowy: 4,74 m) [INT]. |
| 7 | drobna | Attyka: warstwy dachu nad pustką wentylowaną w modelu 2D, a w U pominięte; „legary” klasyfikowane jako pustka. | Rozróżnienie 'powietrze' (niewentylowana, λ_eq — w U i w 2D) i 'powietrze_went' (nazwa „…wentylowana” lub pole `wentylowana`); `wezel_attyka` z warstwą wentylowaną → ValueError (wariant nieobsługiwany); słowo „legar” nie decyduje o klasyfikacji. |
| 8 | istotna | System wymiarów ψ i H_TB niespójny z projektem (`energia.bryla`, `fizyka.mostki` — wymiary wewnętrzne całkowite, okna w świetle otworu w murze); H_TB = 9,28 W/K liczone z ψ_e. | `ElementFlankujacy.l_oi`, `WynikPsi.psi_oi` (strop pośredni / wspornik / próg: ψ_oi = ψ_e — wysokości „od podłogi do podłogi”; attyka: ściana do spodu płyty; okna: ściana do krawędzi otworu w murze + korekta U_w·x0 pasa między krawędzią ramy a otworem); H_TB = Σ ψ_oi·l_oi z długościami w tym samym systemie; eksport `eksport_wynikow` → {id: {psi_oi, psi_e, psi_i, f_rsi, dlugosc(_oi), typ}} (czytany przez `fizyka.mostki.wczytaj_wyniki_symulacji` — pierwszeństwo psi_oi). Poprzednie H_TB = 9,28 W/K (ψ_e, długości zewn., w tym otwory wewnętrzne) — NIEPORÓWNYWALNE, wycofane. |
| 9 | istotna | Długość WZ-W1 obejmowała otwory w ścianach wewnętrznych/działowych; pominięte progi; nadproża i podokienniki liczone jak ościeże. | `otwory_zewnetrzne` — tylko ściany o przegrodzie `sciana_zewn` (bez `typ: otwor`); nowe węzły 2D (przekroje pionowe): WZ-N1 nadproże, WZ-N2 nadproże z kasetą osłony w ociepleniu (otwory z żaluzją/screenem), WZ-P1 podokiennik z parapetem wewn. i obróbką zewn., WZ-T1 próg na płycie parteru (grunt), WZ-T2 próg okna do podłogi na stropie, WZ-T3 próg drzwi na płycie wspornikowej z łącznikiem; długości: ościeża 2·wys, nadproża/podokienniki/progi szer. |

**Kontrole numeryczne poprawek** (uruchamiane przy generowaniu raportu):

| Uwaga | Kontrola | Wynik | Ocena |
|---|---|---|---|
| 2 | szczelina między wielobokami 0,2 µm / 0,1 mm (ściana SIL 18 + EPS 20) | 0,2 µm → U_2D = 0,1459 (1D: 0,1459; przyciąganie do 1 µm); 0,1 mm → ValueError (szczelina wykryta) | **OK** |
| 5 | podzial(0; 20 m; h = 3 mm) | 6667 komórek, max 3,000 mm (wcześniej OverflowError) | **OK** |
| 3 | θ_si,min naroża wewn. (h_min 2 mm vs 0,25 mm; odniesienie 10,737 °C) | 10,736 / 10,737 °C (wcześniej 10,810 / 10,747 — środki ścian komórek) | **OK** |
| 4 | płaskownik stalowy 2 mm przez izolację 0,2 m (półmodel), ψ vs niezależny solver 0,03472 | ψ = 0,03449 (−0,7 %; wcześniej −1,5 % po akceptacji siatki), siatki 2640, 10560, zbieżność Φ i ψ: tak | **OK** |
| 7 | attyka z warstwą dobrze wentylowaną | ValueError (wariant nieobsługiwany — brak niespójności U/2D) | **OK** |

Wynik punktu G przypadku 2 **zależał od siatki** przed poprawką 1 (tolerancja ± 0,1 K spełniona na siatce walidacyjnej h_min = 0,1 mm częściowo dzięki zaokrągleniu wartości odniesienia 16,3); po poprawce G = 16,334 °C niezależnie od siatki (0,5 mm → 0,025 mm), zgodnie z niezależnym solverem. Odchyłki A (−0,036 K) i B (−0,039 K) są identyczne w obu solverach — wynikają z zaokrąglenia wartości odniesienia.

Wpływ poprawek na katalog (model testowy `model/test/dom_testowy.yaml`, 17 węzłów): f_Rsi zmienia się o ≤ 0,002 (wierzchołki), ψ o ≤ 0,001 W/(m·K) (siatka); cokół WZ-GF1 z B' = 4,74 m: ψ_oi = ψ_i ≈ 0,213 zamiast 0,203 W/(m·K). Nowe węzły: nadproże WZ-N1 ψ_oi ≈ 0,008, z kasetą osłony WZ-N2 ≈ 0,083, podokiennik WZ-P1 ≈ 0,005, próg na gruncie WZ-T1 ≈ 0,21 (f_Rsi ≈ 0,748 — najmniejszy zapas wśród węzłów projektowych), próg na stropie WZ-T2 ≈ 0,023, próg na płycie wspornikowej z łącznikiem WZ-T3 ≈ 0,17 W/(m·K). H_TB modelu testowego = Σ ψ_oi·l_oi ≈ 17,6 W/K (długości oi, tylko otwory w ścianach zewnętrznych); poprzednie 9,28 W/K (ψ_e, inne długości) — nieporównywalne. Wszystkie węzły z ciągłą izolacją spełniają f_Rsi ≥ 0,72; wariant porównawczy WZ-B0 (płyta bez łącznika) — f_Rsi ≈ 0,746, ψ ≈ 0,75 W/(m·K).

## Źródła danych referencyjnych

* Physibel — Validation of the program BISCO according to ISO 10211 (rys. C.1, C.2 normy z danymi): https://www.physibel.be/uploads/knowledge_bases/document/40/A2-Validation_BISCO_EN10211.pdf
* SimScale — Thermal Bridge Case 2 (ISO 10211 zał. C, przypadek 2): https://www.simscale.com/docs/validation-cases/thermal-bridge-case-2/
* QuickField — ISO 10211:2007 test case A.2: https://quickfield.com/advanced/iso_10211_2007_case2.htm
* WUFI — Two-dimensional test cases of ISO 10211 (opis przypadku 1): https://wufi.de/en/2015/04/09/two-dimensional-test-cases-of-iso-10211/

Tekst PN-EN ISO 10211:2017 nie był dostępny; dane przypadków 1 i 2 odczytano z rysunków normy zamieszczonych w raporcie walidacyjnym Physibel i potwierdzono niezależnie (SimScale, QuickField — identyczne wymiary, λ, warunki i wyniki). Przed wydaniem PT zaleca się porównanie z egzemplarzem normy (PKN) [NZW — źródło wtórne].
