# Mostki cieplne — zestawienie ψ·L → H_TB, ciągłość „4 linii” (Dom LAMELA)

Model: `model/budynek.yaml` (stan na 2026-09-25); karty węzłów, mapy temperatur i metoda: [`katalog_mostkow.md`](katalog_mostkow.md), szczegóły: [`szczegoly_obliczen.md`](szczegoly_obliczen.md), rekomendacje: [`REKOMENDACJE.md`](REKOMENDACJE.md). Wygenerowano: `PYTHONPATH=src python3 tools/mostki_budynku.py`.

**Zakres:** wszystkie wpisy sekcji `wezly` modelu (węzły liniowe — symulacja 2D PN-EN ISO 10211, węzły złożone rozdzielone na podwęzły a/b/c wg geometrii) + węzły spoza sekcji wykryte w geometrii (WZ-X…: dach – ściana wyższej kondygnacji) + mostki punktowe χ (konsole, kotwy, przejścia — wartości deklarowane/typowe).

## 1. Węzły — ψ, f_Rsi, ciągłość 4 linii

f_Rsi,min = 0,72 (WT 2021 zał. 2 pkt 2.2.1; PN-EN ISO 13788 — kryterium pleśni, R_si = 0,25). 4 linie: **I** izolacja cieplna, **H** hydroizolacja / ochrona przed wodą, **S** szczelność powietrzna, **P** paroizolacja / kontrola pary (✓ ciągłość zachowana, ! uwaga, ✗ brak). ψ_oi — system wymiarów wewnętrznych całkowitych (H_TB); odniesienia: wartość domyślna PN-EN ISO 14683 / dobra praktyka (`fizyka.mostki.PSI_DOMYSLNE`, [NZW]).

| węzeł | nazwa | ψ_e | ψ_oi | ψ_oi dom. / dobra pr. | f_Rsi | ocena | I | H | S | P | ciągłość |
|---|---|---|---|---|---|---|---|---|---|---|---|
| WZ-01 | Attyka stropodachu bryły A (D1) | −0,025 | **+0,086** | 0,75 / 0,20 | 0,932 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-02 | Attyki dachów P1 (D2, D3) — poza ścianami bryły A | +0,059 | **+0,171** | 0,75 / 0,20 | 0,900 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-03 | Attyka dachu zielonego nad pasem gospodarczym (linia D, część ogrzewana) | +0,069 | **+0,195** | 0,75 / 0,20 | 0,890 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-04 | Okap E (PL-E) i daszek wejścia — łącznik termoizolacyjny | +0,128 | **+0,128** | 0,30 / 0,15 | 0,929 ✓ | DOBRY | ✓ | ! | ✓ | ✓ | uwaga — hydroizolacja / ochrona przed wodą: odprowadzenie wody z krawędzi płyty (rynna / okapnik / rzygacz → rura spustowa) — nieokreślone w modelu; obróbka czo |
| WZ-05 | Krawędź ST2 (PL-2) — łącznik termoizolacyjny pod bryłą A | +0,126 | **+0,134** | 0,30 / 0,15 | 0,927 ✓ | DOBRY | ✓ | ! | ✓ | ✓ | uwaga — hydroizolacja / ochrona przed wodą: odprowadzenie wody z krawędzi płyty (rynna / okapnik / rzygacz → rura spustowa) — nieokreślone w modelu; obróbka czo |
| WZ-06 | Krawędź ST3 (PL-3) — łącznik termoizolacyjny przy attyce bryły A | +0,093 | **+0,205** | 0,75 / 0,20 | 0,889 ✓ | DO POPRAWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-07a | Krawędź stropu ST2Z nad powietrzem: ściana SZL na belce B3 + płyta PL-2 (łącznik) | +0,028 | **+0,152** | 0,60 / 0,15 | 0,851 ✓ | DO POPRAWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-07b | Krawędź stropu ST2Z nad ścianą SZ1 niższej kondygnacji (ocieplenie spodu SUF-ZEW) | −0,014 | **−0,061** | 0,60 / 0,15 | 0,952 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-08 | Cokół: ściana zewn. – płyta fundamentowa na XPS (część ogrzewana) | +0,058 | **+0,100** | 0,80 / 0,15 | 0,903 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-09a | Ściana dom–garaż (SWG) na płycie fundamentowej (POD-0 / POD-G) (ψ_iu = +0,406) | +0,406 | **+0,406** | 0,20 / 0,10 | 0,901 ✓ | ZŁY | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: DESKA_DEB → JASTRYCH → TYNK_GIPS → ZB_C25 → TYNK_CW (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) |
| WZ-09b | Ściana SWG pod płytą: dom — D4, garaż — D4, pas docieplenia SUF-G 1.0 m (ψ_iu = +0,317; ψ_ue = −0,043) | +0,052 | **+0,071** | 0,20 / 0,10 | 0,836 ✓ | ZŁY | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: TYNK_GIPS → SIL18 → ZB_C25 (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) |
| WZ-09c | Ściana SWG pod płytą: dom — ST1 + ściana SZ1, garaż — D4, pas docieplenia SUF-G 1.0 m (ψ_iu = +0,178; ψ_ue = −0,054) | +0,070 | **+0,081** | 0,20 / 0,10 | 0,885 ✓ | ZŁY | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: TYNK_GIPS → SIL18 → ZB_C25 (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) |
| WZ-10 | Strop pośredni ST1/ST2 – ściana zewn. z ETICS ciągłym (wieniec) | −0,000 | **−0,000** | 0,00 / 0,00 | 0,963 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-11 | Ościeża okien/drzwi — ciepły montaż (rama 5 cm w murze, 4 cm w izolacji, zakład izolacji 3 cm n | +0,014 | **+0,005** | 0,10 / 0,04 | 0,930 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-11N | Nadproża — BEZ kaset osłon w ociepleniu (kasety w okapach / ramie C / szczelinie lamel / nadsta | +0,017 | **+0,008** | 0,10 / 0,04 | 0,938 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-11P | Podokienniki — parapet zewn. z okapnikiem na profilu z XPS | +0,015 | **+0,006** | 0,10 / 0,04 | 0,911 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-11T | Progi HS / drzwi zewn. na płycie P0 — profil progowy termoizolacyjny na podwalinie XPS/PUR-GF,  | +0,076 | **+0,118** | 0,80 / 0,15 | 0,845 ✓ | DOBRY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-12 | Narożniki wypukłe ścian zewnętrznych | −0,052 | **+0,066** | 0,15 / 0,06 | 0,926 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-16a | Krawędź stropu ST2Z nad powietrzem: ściana SZ2 na belce B3 + płyta PL-2 (łącznik) | +0,009 | **+0,189** | 0,60 / 0,15 | 0,820 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-16b | Krawędź stropu ST2Z nad powietrzem: ściana SZ1 na belce B3 | −0,047 | **+0,120** | 0,60 / 0,15 | 0,853 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-X1 | Dach D2/D3 (SD2) – ściana SZ1 wyższej kondygnacji na krawędzi (pod spodem ściana SW18, pomieszc | −0,006 | **+0,022** | 0,75 / 0,20 | 0,964 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |
| WZ-X2 | Dach D4 (DZ1) – ściana SZ1 wyższej kondygnacji na krawędzi (pod spodem ściana SW18, pomieszczen | −0,001 | **+0,022** | 0,75 / 0,20 | 0,964 ✓ | BEZMOSTKOWY | ✓ | ✓ | ✓ | ✓ | zachowana |

Pozycje „!/✗” 4 linii — opis w kolumnie „ciągłość” i w [`REKOMENDACJE.md`](REKOMENDACJE.md); pełne listy kontrolne wody i wilgoci — karty w [`katalog_mostkow.md`](katalog_mostkow.md).

## 2. Długości mostków liniowych — geometria modelu ↔ pole `dlugosc` sekcji `wezly`

Długości policzono z geometrii (obrysy kondygnacji, dachy, płyty wspornikowe, stropy, ściany, otwory, pomieszczenia — próbkowanie krawędzi co 0,125 m, klasyfikacja każdego odcinka do JEDNEGO węzła: attyka / attyka z okapem / płyta wspornikowa / dach–ściana wyższa / strop pośredni / cokół / próg). Różnice wobec modelu wynikają głównie z podwójnego liczenia odcinków w `dlugosc` (np. WZ-01 zawiera odcinki z płytą PL-3 liczone też w WZ-06; WZ-05 i WZ-07 — krawędź A′; WZ-08 zawiera progi WZ-11T; WZ-10 — połączenia dachów D2/D3 ze ścianami P2 liczone dwukrotnie).

| węzeł | L model [m] | L geometria [m] | Δ [m] | sposób liczenia (geometria) |
|---|---|---|---|---|
| WZ-01 | 19,94 | 19,94 | −0,00 | attyki nad pomieszczeniami ogrzewanymi, bez odcinków z płytą wspornikową i ze ścianą wyższą: D1 19.94 |
| WZ-02 | 13,41 | 13,41 | −0,00 | attyki nad pomieszczeniami ogrzewanymi, bez odcinków z płytą wspornikową i ze ścianą wyższą: D2 7.08, D3 6.33 |
| WZ-03 | 7,17 | 7,17 | −0,00 | attyki nad pomieszczeniami ogrzewanymi, bez odcinków z płytą wspornikową i ze ścianą wyższą: D4 7.17 |
| WZ-04 | 22,47 | 22,47 | −0,00 | styk płyt z obudową (bez krawędzi stropu nad powietrzem): PL-E 19.97, PL-DA 2.50 |
| WZ-05 | 18,71 | 18,71 | −0,00 | styk płyt z obudową (bez krawędzi stropu nad powietrzem): PL-2 18.71 |
| WZ-06 | 24,30 | 24,30 | +0,00 | styk płyt z obudową (bez krawędzi stropu nad powietrzem): PL-3 24.30 |
| WZ-07a | 10,60 | 5,30 | +0,00 | strop ST2Z (sufit SUF-ZEW); krawędzie typu ściana na krawędzi — łącznie 5.30 m |
| WZ-07b | 10,60 | 5,30 | +0,00 | strop ST2Z (sufit SUF-ZEW); krawędzie typu nad ścianą niższej kondygnacji — łącznie 5.30 m |
| WZ-08 | 27,77 | 27,77 | +0,00 | obwód parteru pomieszczeń ogrzewanych bez progów |
| WZ-09a | 24,51 | 12,25 | −0,01 | ściany S0-16, S0-17 (Σ 12.25 m) na płycie PF |
| WZ-09b | 24,51 | 6,38 | +0,00 | ściany S0-17 (Σ 6.38 m) |
| WZ-09c | 24,51 | 5,88 | +0,00 | ściany S0-16 (Σ 5.88 m) |
| WZ-10 | 18,20 | 18,20 | −0,00 | ściana zewn. nad i pod stropem, bez płyt wspornikowych, dachów i garażu: ST1 13.47, ST2 4.73 |
| WZ-11 | 96,28 | 96,28 | +0,00 | 2 × wysokość 26 otworów w ścianach zewn. części ogrzewanej |
| WZ-11N | 45,03 | 45,03 | +0,00 | szerokości otworów |
| WZ-11P | 29,42 | 29,42 | −0,00 | szerokości 17 okien z parapetem > 5 cm |
| WZ-11T | 15,67 | 15,67 | −0,00 | szerokości otworów drzwiowych/HS parteru (parapet ≤ 5 cm) |
| WZ-12 | 40,05 | 40,05 | +0,00 | naroża wypukłe obrysu ogrzewanego × wys. kondygnacji: P0: 3 × 3.15 m; P1: 4 × 3.15 m; P2: 6 × 3.00 m |
| WZ-16a | 2,02 | 1,01 | +0,00 | strop ST2Z (sufit SUF-ZEW); krawędzie typu ściana na krawędzi — łącznie 1.01 m |
| WZ-16b | 2,02 | 1,01 | +0,00 | strop ST2Z (sufit SUF-ZEW); krawędzie typu ściana na krawędzi — łącznie 1.01 m |
| WZ-X1 | 13,79 | 13,79 | +13,79 | krawędzie dachów D2, D3 pod ścianą SZ1: Σ 13.79 m |
| WZ-X2 | 2,79 | 2,79 | +2,79 | krawędzie dachów D4 pod ścianą SZ1: Σ 2.79 m |

Dla węzłów złożonych (podwęzły a/b/c) „L model” to długość całego wpisu, a Δ liczono względem części przypisanej proporcjonalnie do geometrii.

## 3. H_TB = Σ ψ_oi·l + Σ χ (PN-EN ISO 14683 / PN-EN ISO 13789)

Połączenia z garażem nieogrzewanym: para i–u × b_u = 0,80 (θ_u z bilansu modułu energii: −10,6 °C przy n_u = 1,0 h⁻¹ → b_u ≈ 0,81; przyjęto 0,80) — składnik H_U; para u–e (obudowa garażu) nie wchodzi do H_TB budynku.

| węzeł | para stref | ψ_oi [W/(m·K)] | l [m] | b | ψ·l·b [W/K] | źródło l |
|---|---|---|---|---|---|---|
| WZ-01 | i–e | +0,086 | 19,94 | 1,00 | +1,72 | geometria |
| WZ-02 | i–e | +0,171 | 13,41 | 1,00 | +2,30 | geometria |
| WZ-03 | i–e | +0,195 | 7,17 | 1,00 | +1,40 | geometria |
| WZ-04 | i–e | +0,128 | 22,47 | 1,00 | +2,88 | geometria |
| WZ-05 | i–e | +0,134 | 18,71 | 1,00 | +2,51 | geometria |
| WZ-06 | i–e | +0,205 | 24,30 | 1,00 | +4,97 | geometria |
| WZ-07a | i–e | +0,152 | 5,30 | 1,00 | +0,81 | geometria |
| WZ-07b | i–e | −0,061 | 5,30 | 1,00 | −0,32 | geometria |
| WZ-08 | i–e | +0,100 | 27,77 | 1,00 | +2,78 | geometria |
| WZ-09a | i–u | +0,406 | 12,25 | 0,80 | +3,98 | geometria |
| WZ-09b | i–e | +0,071 | 6,38 | 1,00 | +0,45 | geometria |
| WZ-09b | i–u | +0,317 | 6,38 | 0,80 | +1,62 | geometria |
| WZ-09c | i–e | +0,081 | 5,88 | 1,00 | +0,48 | geometria |
| WZ-09c | i–u | +0,178 | 5,88 | 0,80 | +0,84 | geometria |
| WZ-10 | i–e | −0,000 | 18,20 | 1,00 | −0,00 | geometria |
| WZ-11 | i–e | +0,005 | 96,28 | 1,00 | +0,51 | geometria |
| WZ-11N | i–e | +0,008 | 45,03 | 1,00 | +0,35 | geometria |
| WZ-11P | i–e | +0,006 | 29,42 | 1,00 | +0,17 | geometria |
| WZ-11T | i–e | +0,118 | 15,67 | 1,00 | +1,86 | geometria |
| WZ-12 | i–e | +0,066 | 40,05 | 1,00 | +2,62 | geometria |
| WZ-16a | i–e | +0,189 | 1,01 | 1,00 | +0,19 | geometria |
| WZ-16b | i–e | +0,120 | 1,01 | 1,00 | +0,12 | geometria |
| WZ-X1 | i–e | +0,022 | 13,79 | 1,00 | +0,31 | geometria |
| WZ-X2 | i–e | +0,022 | 2,79 | 1,00 | +0,06 | geometria |

| mostek punktowy | n [szt.] | χ [W/K] | n·χ [W/K] | liczba | źródło χ |
|---|---|---|---|---|---|
| WZ-13 — Konsole rusztu lamel (przekładka termiczna) | 51 | 0,010 | 0,510 | Σ długości linii lamel 25.65 m × 2 rygle / rozstaw konsol 1,0 m [ZAŁ] = 51 | [DANE PRZYKŁADOWE – FIKCYJNE] dane przykładowe z deklaracji typowej konsoli fasadowej z pr |
| WZ-14 — Konsole ramy boksu C i linii D (PL-C1/PL-C2/PL-D; punktowe, przekładka | 17 | 0,010 | 0,170 | liczba z modelu (sekcja `wezly`) | fizyka.mostki.CHI_DOMYSLNE [NZW] |
| WZ-17 — Konsole kratownicy zielonej ściany S0-02 (K-13; punktowe, przekładka t | 10 | 0,010 | 0,100 | liczba z modelu (sekcja `wezly`) | fizyka.mostki.CHI_DOMYSLNE [NZW] |
| WZ-15 — Przejścia instalacji przez przegrody zewnętrzne (wywiewka K1, czerpnia | 16 | 0,005 | 0,080 | liczba z modelu (sekcja `wezly`) | fizyka.mostki.CHI_DOMYSLNE [NZW] |

**H_TB (do zewnętrza, ψ_oi·l z geometrii) = 26,18 W/K**; połączenia z garażem (ψ_iu·l·b_u) = 6,44 W/K; mostki punktowe Σ χ = 0,86 W/K → **H_TB,całk. = 33,48 W/K**.

Dla porównania: Σ ψ_oi·l z długościami pola `dlugosc` modelu (katalog, bez χ, bez b_u) = 30,79 W/K; H_TB z wartości domyślnych Ψ (PN-EN ISO 14683) w module energii = 137,6 W/K (`docs/20_koncepcja/weryfikacja_koncepcji.md`, tab. EP). Wartości symulowane obniżają H_TB kilkukrotnie — do obliczeń EP (moduł `energia`) przekazać `wyniki_mostki.json` (ψ) z długościami z tej tabeli.

**Ograniczenia:** 2D (mostki liniowe); χ — dane przykładowe (konsole lamel wg `wyroby_przykladowe.yaml`, kotwy/przejścia wg `fizyka.mostki.CHI_DOMYSLNE` [NZW]) — do zastąpienia deklaracjami (ETA) lub obliczeniem 3D (PN-EN ISO 10211 model 3D); łączniki termoizolacyjne i profile progowe — dane przykładowe; ramy okien jako materiał zastępczy (λ_eq z U_f); warstwy powietrza wentylowane pominięte (R_se = 0,04 — wariant ostrożny); wierzch płyt wspornikowych zrównany ze stropem (konwencja audytu A2 K-1).
