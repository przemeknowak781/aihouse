# Audyt A1 — zgodność koncepcji ostatecznej z WT i MPZP (obliczenia z modelu)

Wygenerowano: 2026-09-25 skryptem `tools/audyt_wt.py` (uruchomienie: `python3 tools/audyt_wt.py`). Model: `model/budynek.yaml` (wersja 1.0, stadium: koncepcja ostateczna (synteza W2 + przeszczepy W1/W3 + poprawki J1–J3)), `model/dzialka.yaml`; wartości progowe z `docs/10_podstawy_prawne/wymagania.yaml` (418 wpisów). Model nie był modyfikowany.

**Wynik kontroli automatycznych:** 3 × NIEZGODNE, 5 × UWAGA, 152 × OK, 2 × INFO.


## 0. Ocena audytora A1 (część opisowa; liczby — z obliczeń skryptu poniżej)

**Przedmiot:** koncepcja ostateczna: `model/budynek.yaml`, `model/dzialka.yaml` (stan z commita `edde275`, 25.09.2026 04:21), `docs/20_koncepcja/koncepcja.md` oraz podglądy w `docs/20_koncepcja/final/`.
**Zakres A1:** zgodność z WT (t.j. Dz.U. 2022 poz. 1225 ze zm., w brzmieniu do 19.09.2026 — art. 102a PB) i z MPZP 3MN. Wartości progowe pochodzą z rejestru `docs/10_podstawy_prawne/wymagania.yaml`.
**Tryb:** tylko raport. Modelu nie poprawiałem.
**Uwaga o stanie modelu:** w trakcie audytu inne zespoły zmieniały model (m.in. doszły szachty 0.14 / 1.09 / 2.08). Każdą kolejną wersję sprawdza się ponownie poleceniem `python3 tools/audyt_wt.py`.

### 0.1 Werdykt

Koncepcja **spełnia** wymagania WT i MPZP w obszarach:
* **usytuowanie** — każda płaszczyzna ściany, wszystkie płyty, okapy, lamele, attyki, rzygacze i rury spustowe leżą ≥ 4,0 m od granic; linia zabudowy nie jest przekroczona;
* **wskaźniki MPZP** — zabudowa, PBC, intensywność, liczba kondygnacji, spadek dachów, miejsca postojowe, ogrodzenie;
* **wysokość** — liczona wg upzp oraz wg WT §6;
* **pomieszczenia** — powierzchnie i wysokości w świetle;
* **oświetlenie dzienne** (≥ 1/8);
* **schody** — h, s, 2h+s, szerokości, spoczniki, prześwity;
* **garaż** — wymiary, brama, wysokość, wrota–okna;
* **pozostałe** — daszek nad wejściem, podokienniki P1/P2, otwieranie okien P2, wyłaz, odległości ppoż. od sąsiadów.

Poniższe usterki trzeba poprawić **przed przekazaniem do PAB/PZT**. Żadna nie wymaga zmiany bryły.

| # | Waga | Miejsce (id / współrzędne) | Problem | Poprawka (z wymiarami) | Podstawa |
|---|---|---|---|---|---|
| A1-1 | **istotny** | `energia.wentylacja` (oraz `instalacje.lokalizacje`, `tools/buduj_model.py` wiersze ≈ 921 i 1287). Czerpnia [11,40; 1,00; +9,95], wyrzutnia [1,80; 3,00; +10,00] na D1 | Odległość czerpnia–wyrzutnia wynosi **9,81 m < 10,00 m**. Wyrzutnia jest tylko **0,05 m** wyżej od czerpni, a warunek dla 6 m wymaga ≥ 1,0 m. Opis przyjął „≥ 6 m od siebie” (`koncepcja.md`, tabela poprawek: wiersz J1 „czerpnia W-166, wyrzutnia W-167”), co jest błędną interpretacją. | **Czerpnia → (11,60; 1,00)**, dolna krawędź wlotu ≥ **+10,00** (pokrycie lokalne ≈ +9,58 + 0,40). **Wyrzutnia → (1,70; 3,00)**, wylot ≥ +10,00; zostaje 3,00 m od krawędzi zach. nad O2-04 i 3,30 m od krawędzi pd. Odległość wyniesie **10,10 m**. Czerpnia będzie 7,96 m od wywiewki K1 (≥ 6 m). Wysokość zabudowy bez zmian: 10,33 m. Wariant „wyrzutnia +1,0 m wyżej” (+10,95) daje wysokość zabudowy 11,28 m > 11,00 m (MPZP), więc odpada. Poprawić też zdanie w `koncepcja.md`. | WT §152 ust. 10 [W-167]; R6-43 |
| A1-2 | drobny | `dzialka.yaml` `miejsca_postojowe` MP1 [[20,0; 35,9]…[22,7; 41,8]], MP2 [[22,9; 35,9]…[25,6; 41,8]] (garaż 0.13: lica x = 12,22 / 18,27 w ukł. budynku) | Dłuższa krawędź MP1 leży **0,18 m** od lica ściany S0-16, a MP2 **0,27 m** od lica S0-03. Wymagane jest ≥ 0,30 m. Garaż w świetle (6,05 m) jest poprawny — błędnie narysowano tylko stanowiska na PZT. | Stanowiska 2,50 × 5,90 m: **MP1 x_dz 20,12…22,62**, **MP2 x_dz 23,07…25,57**, y bez zmian. Odstęp między nimi wyniesie 0,45 m, od ścian po 0,30 m. Przy szerokości 2,70 m zostaje odstęp 0,05 m. | WT §104 ust. 1 pkt 1 [W-112] |
| A1-3 | drobny | Garaż 0.13, drzwi garaż–dom **O0-22** (S0-17, x 13,60…14,50; y 2,875); `pomieszczenia 0.13.uwagi` „posadzka −0,10, spadek 1,5 % do bramy” | Posadzka ma −0,10 przy bramie i spadek 1,5 % na 6,1 m, więc przy O0-22 wypada ≈ **−0,01**. Próg dom–garaż ma tylko **0,9 cm** (< 3 cm). Woda z posadzki spływa przez bramę na utwardzony podjazd, potem do OL-1, KD-E i do **zbiornika wody do podlewania**, co grozi zanieczyszczeniem olejami. | Spadek posadzki **0,8 %**: −0,10 przy bramie, **−0,05 przy O0-22** (próg 5 cm). Alternatywa: obniżyć płytę PF1 pod garażem o 0,05 m. Odpływ OL-1 skierować przez osadnik/separator albo do niecki chłonnej na terenie nieutwardzonym, nie do zbiornika retencyjnego. | WT §107 ust. 1–2 [W-114] |
| A1-4 | drobny | Czerpnia [11,40; 1,00; +9,95] na D1 (klin PIR 0,12–0,32; wpust WP1 (5,57; 5,45)) | Z klinem spadkowym (2 % na 7,3 m od WP1) pokrycie w miejscu czerpni wynosi ≈ +9,573. Wlot stoi więc **0,377 m** nad dachem (< 0,40). Wysokości czerpni i wyrzutni policzono od średniej grubości PIR (0,22 m). | Dolna krawędź wlotu ≥ **+10,00** (łącznie z A1-1). Rzędne urządzeń dachowych liczyć od lokalnego pokrycia z klinem. | WT §152 ust. 4 [W-166] |
| A1-5 | drobny | Wyrzutnia [1,80; 3,00; +10,00] ↔ świetlik **SW1** [6,00…8,40 × 7,45…8,65], wierzch +9,75 | Wyrzutnia stoi 6,12 m od świetlika. Przy odległości 3–10 m wylot powinien być ≥ 1,0 m ponad górną krawędzią okna (≥ +10,75). Jest 0,25 m. Na D1 nie da się odsunąć wyrzutni ≥ 10 m od SW1 i jednocześnie trzymać ≥ 3 m od krawędzi nad oknami. | Zapisać SW1 jako **świetlik stały (nieotwierany, bez funkcji wentylacyjnej)** i dopisać w opisie interpretację: przepis chroni otwierane okna przed zasysaniem powietrza wywiewanego. Podniesienie wylotu do +10,75 koliduje z MPZP (≈ 11,1 m). | WT §152 ust. 12 [W-167] (interpretacja); R6-43 |
| A1-6 | drobny | Spiżarnia **0.05** (wielobok 5,98…8,395 × 5,23…8,645), `wys: 1.9` | Pod biegiem 2 i spocznikiem wysokość zmienia się od 1,37 do 2,75 m. Strefy: ≥ 2,20 m — 1,03 m²; 1,40–2,20 m — 1,49 m²; < 1,40 m — 2,82 m² (pod spocznikiem h = 1,395 m). Umowna „wys. 1,90 → 50 %” zawyża PU o 0,92 m² (2,70 zamiast 1,78 m²). Część o h < 2,00 m nie spełnia WT §97 dla pomieszczenia gospodarczego. | Część pod spocznikiem i dolną częścią biegu opisać jako **schowek pod schodami**, a PU liczyć strefami 100/50/0 %. Bilans koncepcji: 240,24 − 0,92 = 239,32 m². Audyt liczy strefami i daje 239,85 m². Obie wartości mieszczą się w 230–270 m². | WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] |
| A1-7 | drobny | PC-JZ (24,40; 31,65 w ukł. działki; fundament U5), elewacja **S** pasa gospodarczego, 0,75 m od lica | Twarde założenia każą stawiać jednostkę zewnętrzną PC od N lub E. Model stawia ją od S, przy ogrodzie i tarasach T1/T3. Faktycznym powodem jest W-024 (≥ 6,0 m od granicy E), ale `koncepcja.md` nie nazywa tego odstępstwem. | Pozostawić, ale wpisać do §7 koncepcji uzasadnienie odstępstwa. Wariant E (przy ścianie wsch. 0.12) daje ≈ 4,8 m od granicy: ≥ 3,0 m, ale < 6,0 m wg W-024. Wykazać L_Aeq,N ≤ 40 dB na granicy E i oszacować hałas na tarasach T1/T3. Ekran akustyczny od strony T3/O0-06. | TWARDE ZAŁOŻENIA; W-024; W-156 |
| A1-8 | drobny | `koncepcja.md` §9 (blok generowany przez `tools/podglad_modelu.py`) | (a) Wysokość wg WT §6 podano 9,85 m, licząc do średniego wierzchu pokrycia (+9,52). Najwyżej położony punkt stropodachu D1 (klin d_max 0,32) to **+9,626**, co daje **9,96 m**. (b) Wysokość zabudowy 10,25 m policzono od średniego terenu. Rejestr D-15 każe liczyć od niższej rzędnej, co daje **10,33 m**. Obie wartości mieszczą się w limitach. | Poprawić formuły w `podglad_modelu.py`: WT §6 do max(pokrycia) z klinem; upzp od min(teren istniejący, projektowany). | WT §6 [W-063]; upzp art. 2 pkt 30 [W-033]; D-15 |

### 0.2 Kluczowe wyniki (obliczone z modelu)

| Wielkość | Wynik | Wymóg |
|---|---|---|
| Pow. zabudowy (obrys ścian) / z płytami wysuniętymi | 187,50 m² (11,7 %) / 212,99 m² (13,3 %) | ≤ 480,00 m² |
| PBC (teren; opaska żwirowa i teren nad zbiornikiem wyłączone) | 1268,19 m² (79,3 %) | ≥ 800,00 m² |
| Intensywność (P0 181,78 + P1 117,81 + P2 96,80 = 396,39 m²) | 0,248 | 0,05–0,80 |
| Wysokość zabudowy (upzp, od najniższego terenu 101,32 do wyrzutni +10,00) | 10,33 m | ≤ 11,00 (rezerwa 10,70) |
| Wysokość wg WT §6 (teren przy HS O0-04: 101,32 → D1 +9,626) | 9,96 m | ≤ 12,00 (N) |
| Najmniejsze odległości: ściana z otworami / płyta / taras / linia zabudowy | 5,73 m (S0-03, E) / 5,20 m (PL-2, PL-3, W) / 4,30 m (T1, W) / 0,95 m za linią (T2, PL-DA) | ≥ 4,0 / ≥ 4,0 (zał.; WT 1,5) / ≥ 1,5 / ≤ 0 |
| PU mieszkalna (bez klatek, garażu, techn.) | 239,85 m² | 230–270 m² |
| Strefa dzienna 0.06 | 54,44 m² | ≥ 50 m² |
| Wysokości w świetle pokoi / łazienek (sufit podwieszany −0,25) / garażu | 2,77 / 2,53 / 2,85 m | ≥ 2,50 / ≥ 2,20 / ≥ 2,20 |
| Najmniejszy stosunek okien do podłogi (światło ościeżnic, szac.) | 0,167 (1.03 Pokój dziecka 1) | ≥ 0,125 |
| Schody SCH1/SCH2 | h 0,175; s 0,28; 2h+s 0,630; bieg 1,150/1,145 m (po odjęciu pochwytu ≈ 1,04 m); spocznik 1,175 m; prześwit min. 2,325 m (pod B8/B9), nad biegami 2,76 m | h ≤ 0,19; 0,60–0,65; ≥ 1,00; ≥ bieg; ≥ 2,00 |

### 0.3 Metoda i założenia skryptu (`tools/audyt_wt.py`)
* **Wieloboki pomieszczeń** — z lic ścian wykończonych: shapely, rdzeń `lamela.model`. W pomieszczeniach pod schodami skrypt próbkuje wysokość co 5 cm pod podniebieniem biegów i spoczników, przyjmując płytę biegu 0,18 m.
* **Wysokości w świetle** — mediana (spód płyty − sufit − posadzka). Posadzka garażu wynika z różnicy warstw POD-G/POD-0. Belki są uwzględnione, jeśli wystają poza ściany.
* **Okna** — światło ościeżnicy szacowane jako światło muru − 2 × 0,08 m.
* **Odległości** — od lica zewnętrznego każdej ściany (każdy uskok osobno) do granicy, w którą ściana jest zwrócona, oraz od wszystkich płyt, dachów z attyką, lamel (z odsunięciem), słupów, rur spustowych i rzygaczy. Wymóg dla płyt to 4,0 m (twarde założenie), dla tarasów naziemnych 1,5 m (WT).
* **Teren** — istniejący interpolowany liniowo (TIN), projektowany z punktów ≤ 1,5–2,0 m. Do wysokości przyjmowana jest niższa z tych rzędnych.
* **Poza zakresem A1:** konstrukcja, fizyka budowli i mostki, instalacje, ppoż. poza odległościami. Tych obszarów nie oceniałem.


## 1. Niezgodności i uwagi (z kontroli automatycznych)

| # | Status | Sekcja | Element / miejsce | Parametr | Wartość | Wymóg | Podstawa | Proponowana poprawka |
|---|---|---|---|---|---|---|---|---|
| 1 | **NIEZGODNE** | Garaż | MP1 — PZT [20.0, 35.9]…[22.7, 41.8] | dłuższa krawędź stanowiska → lico ściany | 0,18 m | ≥ 0,30 | WT §104 ust. 1 pkt 1 [W-112] | rozmieścić stanowiska: 0,30 + 2,50 + (odstęp) + 2,50 + 0,30 w świetle 6,05 m (np. x = 12,52…15,02 i 15,47…17,97 w ukł. budynku) |
| 2 | **NIEZGODNE** | Garaż | MP2 — PZT [22.9, 35.9]…[25.6, 41.8] | dłuższa krawędź stanowiska → lico ściany | 0,27 m | ≥ 0,30 | WT §104 ust. 1 pkt 1 [W-112] | rozmieścić stanowiska: 0,30 + 2,50 + (odstęp) + 2,50 + 0,30 w świetle 6,05 m (np. x = 12,52…15,02 i 15,47…17,97 w ukł. budynku) |
| 3 | **NIEZGODNE** | Wentylacja | czerpnia ↔ wyrzutnia (dach) — energia.wentylacja: czerpnia [11.4, 1.0, 9.95], wyrzutnia [1.8, 3.0, 10.0] | odległość / wyrzutnia wyżej o | 9,81 m / 0,05 m | ≥ 10,00 m, albo ≥ 6,00 m przy wyrzutni ≥ 1,00 m wyżej (lub zestaw zblokowany) | WT §152 ust. 10 [W-167]; R6-43 | rozsunąć na ≥ 10,00 m, np. czerpnia (11,60; 1,00), wyrzutnia (1,70; 3,00) → 10,10 m (wyrzutnia 3,00 m od krawędzi dachu nad oknami; czerpnia 7,96 m od wywiewki); rzędne wylotów ≥ pokrycie lokalne + 0,40; alternatywnie podnieść wyrzutnię ≥ 1,0 m ponad czerpnię (sprawdzić wys. zabudowy) albo zestaw zblokowany |
| 4 | **UWAGA** | Wysokości | 0.05 Spiżarnia (pod schodami) | strefy h pod schodami | ≥2,20: 1,03 m²; 1,40–2,20: 1,49 m²; <1,40: 2,82 m²; h_min 1,37 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] | część o h < 2,00 m opisać jako schowek pod schodami (nie pomieszczenie); w PU liczyć strefami (100/50/0 %) — wg audytu 1,78 m² zamiast 2,70 m² z 'wys: 1,90' |
| 5 | **UWAGA** | Garaż | O0-22 (drzwi garaż–dom) — S0-17 / O0-22 | różnica posadzek dom − garaż przy drzwiach | 0,009 m (posadzka przy bramie -0,10, spadek 1,5 % na 6,10 m) | ≥ 0,030 (próg) | WT §107 ust. 2 [W-114] | obniżyć płytę/posadzkę garażu o ≥ 0,04 m (posadzka przy bramie ≤ -0,14, przy drzwiach ≤ −0,05) i teren/odwodnienie liniowe przed bramą ≥ 0,02 m niżej niż próg bramy |
| 6 | **UWAGA** | Wentylacja | czerpnia dachowa — [11.4, 1.0, 9.95] | wysokość nad pokryciem (lokalnie, klin) | 0,377 m (pokrycie ≈ +9,573) | ≥ 0,40 | WT §152 ust. 4 [W-166] | dolna krawędź otworu czerpni ≥ +9,97 |
| 7 | **UWAGA** | Wentylacja | wyrzutnia ↔ okno w dachu SW1 — wyrzutnia [1.8, 3.0, 10.0]; SW1 [6.0, 7.45]…[8.4, 8.65], wierzch +9,75 | odległość / wylot ponad oknem | 6,12 m / 0,25 m | 3–10 m ⇒ wylot ≥ 1,00 m nad górną krawędzią okna (≥ +10,75) | WT §152 ust. 12 [W-167]; R6-43 | (a) SW1 jako świetlik NIEOTWIERANY bez funkcji wentylacyjnej i zapis interpretacji w opisie (przepis dotyczy okien) — rekomendowane; (b) wylot wyrzutni ≥ +10,75 — koliduje z wys. zabudowy ≤ 11,00 m (MPZP); (c) ≥ 10 m od SW1 — niewykonalne na D1 przy ≥ 3 m od krawędzi nad oknami |
| 8 | **UWAGA** | Zagospodarowanie | PC-JZ (jedn. zewn. PC) | elewacja, przy której stoi jednostka | S (x 24,40, y 31,65 w ukł. działki; 0,75 m od lica) | N lub E (TWARDE ZAŁOŻENIA) | TWARDE ZAŁOŻENIA (energia i światło); W-024 (hałas) | wariant E: przy ścianie wsch. pom. techn. 0.12 / garażu (jednostka gł. ≈ 0,6 m, 0,3 m od lica ⇒ x_dz ≈ 26,6–27,2, ≈ 4,8 m od granicy E: ≥ 3,0 wg założeń, lecz < 6,0 wg W-024 — wymaga obliczenia hałasu L_Aeq,N ≤ 40 dB); elewacja N zajęta przez podjazd i wejście. Jeśli jednostka zostaje od S — wpisać do koncepcji uzasadnienie odstępstwa (W-024: ≥ 6,0 m od granicy E; krótkie przewody do 0.12), ekran akustyczny od tarasu T1/T3 i obliczenie hałasu na tarasie i granicy E |

## 2. Wskaźniki MPZP i wysokość

| Wskaźnik | Wartość | Wymóg | Status |
|---|---|---|---|
| linia zabudowy — najdalej wysunięty element (+ = przekroczenie) | -0,95 m (T2) | ≤ 0,00 | OK |
| pow. zabudowy (1) obrys ścian zewn. wszystkich kondygnacji — A_z | 187,50 m² (11,7 %) | ≤ 480,00 m² | OK |
| pow. zabudowy (2) kontrolnie z płytami wysuniętymi — A_z+ | 212,99 m² (13,3 %) | ≤ 480,00 m² | OK |
| intensywność zabudowy — Σ pow. kondygnacji nadziemnych / pow. działki | 396,39 / 1600,00 = 0,248 | 0,05–0,80 | OK |
| pow. biologicznie czynna (teren) — PBC | 1268,19 m² (79,3 %) | ≥ 800,00 m² | OK |
| miejsca postojowe — liczba (garaż + zewn.) | 4 (2 w garażu) | ≥ 2 | OK |
| kondygnacje nadziemne — liczba | 3 | ≤ 3 | OK |
| D1 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D2 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D3 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| D4 — spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK |
| ogrodzenie [0.0, 50.0]→[17.6, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| ogrodzenie [18.6, 50.0]→[20.3, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| ogrodzenie [25.9, 50.0]→[32.0, 50.0] — wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK |
| wysokość zabudowy (upzp art. 2 pkt 30) — od najniższego terenu 101,32 do wyrzutnia (+10,000) | 10,33 m (od średniej 101,40: 10,25 m) | ≤ 11,00 (z rezerwą ≤ 10,70) | OK |
| wysokość budynku wg WT §6 — teren przy wejściu O0-04: 101,32 → wierzch D1 z izol. (+9,626) | 9,96 m | ≤ 12,00 (N); ≤ 11,00 (MPZP) | OK |

Powierzchnie kondygnacji (obrys zewnętrzny): P0 181,78 m², P1 117,81 m², P2 96,80 m².
PBC: teren 1268,19 m²; powierzchnie wyłączone 331,81 m²; rezerwa — dach zielony (50 %) 31,98 m² (nie wliczona).
Teren przy obwodzie parteru: istniejący 101,33…101,48, projektowany 101,32…101,63 m n.p.m.; ±0,00 = 101,65 m n.p.m. Wejścia (teren niższy z istn./proj.): O0-03 101,35, O0-04 101,32, O0-06 101,35, O0-07 101,46, O0-08 101,46, O0-09 101,44, O0-11 101,34.

## 3. Pomieszczenia — powierzchnie, wysokości, oświetlenie

| Nr | Nazwa | Kat. | Pobyt | Pow. netto [m²] | Pow. do PU [m²] | h w świetle [m] | h min / pod belką | Okna | A_ok/A_p (ościeżn.) |
|---|---|---|---|---|---|---|---|---|---|
| 0.01 | Wiatrołap | ruchu | — | 3,89 | 3,89 | 2,77 | — | O0-10 | 0,109 |
| 0.02 | Hol | ruchu | — | 4,44 | 4,44 | 2,77 | — | — | — |
| 0.03 | WC gościnne | pomocnicza | — | 2,32 | 2,32 | 2,53 | — | — | — |
| 0.04 | Klatka schodowa | ruchu | — | 2,82 | 2,82 | otwarta (pustka) |  / 2,50 (B8) | — | — |
| 0.05 | Spiżarnia (pod schodami) | pomocnicza | — | 5,35 | 1,78 | zmienna 1,37…2,75 | 1,37 | — | — |
| 0.06 | Salon + jadalnia + kuchnia | podstawowa | tak | 54,44 | 54,44 | 2,77 | — | O0-01, O0-02, O0-03, O0-04, O0-05, O0-11 | 0,611 |
| 0.07 | Pas komunikacyjny przy schodach | ruchu | — | 3,51 | 3,51 | 2,77 | — | — | — |
| 0.08 | Przedpokój gościnny | ruchu | — | 1,44 | 1,44 | 2,77 | — | — | — |
| 0.09 | Łazienka gościnna (natrysk) | pomocnicza | — | 3,84 | 3,84 | 2,53 | — | O0-13 | 0,073 |
| 0.10 | Pokój gościnny / gabinet | podstawowa | tak | 12,52 | 12,52 | 2,77 | — | O0-12 | 0,176 |
| 0.11 | Przedsionek gospodarczy | ruchu | — | 7,18 | 7,18 | 2,75 | — | — | — |
| 0.12 | Pomieszczenie techniczne | techniczna | — | 8,85 | 8,85 | 2,75 | — | — | — |
| 0.13 | Garaż 2-stanowiskowy | pomocnicza | — | 37,42 | 37,42 | 2,85 | — | — | — |
| 1.01 | Hol | ruchu | — | 14,09 | 14,09 | 2,77 | — | — | — |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | podstawowa | tak | 28,36 | 28,36 | 2,77 | — | O1-01, O1-02 | 0,387 |
| 1.03 | Pokój dziecka 1 | podstawowa | tak | 13,19 | 13,19 | 2,77 | — | O1-06 | 0,167 |
| 1.04 | Pokój dziecka 2 | podstawowa | tak | 12,52 | 12,52 | 2,77 | — | O1-05 | 0,176 |
| 1.05 | Łazienka dzieci (wanna) | pomocnicza | — | 5,50 | 5,50 | 2,53 | — | O1-03 | 0,059 |
| 1.06 | Klatka schodowa | ruchu | — | 0,49 | 0,49 | otwarta (pustka) |  / 2,50 (B9) | — | — |
| 1.07 | WC z natryskiem | pomocnicza | — | 4,08 | 4,08 | 2,53 | — | — | — |
| 1.08 | Pralnia z suszarnią | pomocnicza | — | 6,64 | 6,64 | 2,77 | — | O1-04 | 0,069 |
| 2.01 | Hol | ruchu | — | 5,74 | 5,74 | 2,77 | — | — | — |
| 2.02 | Sypialnia rodziców | podstawowa | tak | 21,43 | 21,43 | 2,77 | — | O2-01, O2-04 | 0,436 |
| 2.03 | Garderoba (przedpokój apartamentu) | pomocnicza | — | 10,57 | 10,57 | 2,77 | — | O2-02 | 0,156 |
| 2.04 | Łazienka rodziców | pomocnicza | — | 5,51 | 5,51 | 2,53 | — | O2-06 | 0,059 |
| 2.05 | Gabinet / pokój | podstawowa | tak | 16,32 | 16,32 | 2,77 | — | O2-03, O2-05 | 0,354 |
| 2.06 | Klatka schodowa (wyjście z biegu 2, pustka) | ruchu | — | 0,24 | 0,24 | otwarta (pustka) | — | O2-07 | 8,598 |
| 2.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | techniczna | — | 6,05 | 6,05 | 2,77 | — | — | — |
| 0.14 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |
| 1.09 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |
| 2.08 | Szacht instalacyjny SI | techniczna | — | 0,45 | 0,45 | 2,77 | — | — | — |

PU mieszkalna (podstawowa 158,78 + pomocnicza bez garażu 40,24 + komunikacja bez klatek 40,29) = **239,31 m²**; PU wg PN-ISO 9836 (podstawowa + pomocnicza, bez garażu) = 199,02 m²; garaż 37,42 m²; techniczna 16,25 m²; klatki schodowe (wyłączone) 3,55 m². Założenia: światło ościeżnicy = światło muru − 2 × 0,08 m; sufit podwieszany SUF_GK obniża o 0,25 m.

## 4. Schody

| Bieg | z0 [m] | stopni | szer. model / w świetle ścian [m] | długość [m] | prześwit min [m] (element) |
|---|---|---|---|---|---|
| SCH1/bieg1 | 0,000 | 9 | 1,150 / 1,150 | 2,24 | 2,325 (B8) |
| SCH1/bieg2 | 1,575 | 9 | 1,145 / 1,145 | 2,24 | 2,763 (SCH2/bieg2) |
| SCH2/bieg1 | 3,150 | 9 | 1,150 / 1,150 | 2,24 | 2,325 (B9) |
| SCH2/bieg2 | 4,725 | 9 | 1,145 / 1,145 | 2,24 | 2,805 (D1) |

## 5. Odległości od granic działki (WT §12) — wartości minimalne na element

| Element | Rodzaj | Granica | Odległość [m] | Wymóg [m] |
|---|---|---|---|---|
| D4/przelew@[18.675, 6.5] | przelew awaryjny (rzygacz ~0,15 m) | E | 5,58 | 4,00 |
| D4/przelew@[18.675, 2.4] | przelew awaryjny (rzygacz ~0,15 m) | E | 5,58 | 4,00 |
| RS5 | rura spustowa zewn. | E | 5,61 | 4,00 |
| S0-03 | ściana zewn. P0 (z otworami) | E | 5,73 | 4,00 |
| D4 | dach z attyką | E | 5,73 | 4,00 |
| PL-E | płyta wysunięta/okap/daszek | E | 10,60 | 4,00 |
| T3 | taras naziemny/podest | E | 10,90 | 1,50 |
| PL-C2 | płyta wysunięta/okap/daszek | E | 10,95 | 4,00 |
| PL-C1 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| PL-2 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| PL-3 | płyta wysunięta/okap/daszek | E | 11,80 | 4,00 |
| LAM-E | lamele (osłona elewacji) | E | 11,87 | 4,00 |
| D3/przelew@[12.3, 7.2] | przelew awaryjny (rzygacz ~0,15 m) | E | 11,95 | 4,00 |
| S1-02 | ściana zewn. P1 (z otworami) | E | 12,10 | 4,00 |
| S2-02 | ściana zewn. P2 (z otworami) | E | 12,10 | 4,00 |
| S2-04 | ściana zewn. P2 (bez otworów) | E | 15,60 | 3,00 |
| S0-01 | ściana zewn. P0 (z otworami) | S | 32,40 | 4,00 |
| S0-02 | ściana zewn. P0 (z otworami) | S | 32,40 | 4,00 |
| S1-01 | ściana zewn. P1 (z otworami) | S | 32,40 | 4,00 |
| S2-01 | ściana zewn. P2 (z otworami) | S | 32,40 | 4,00 |
| T1 | taras naziemny/podest | W | 4,30 | 1,50 |
| PL-2 | płyta wysunięta/okap/daszek | W | 5,20 | 4,00 |
| PL-3 | płyta wysunięta/okap/daszek | W | 5,20 | 4,00 |
| PL-E | płyta wysunięta/okap/daszek | W | 5,80 | 4,00 |
| LAM-W | lamele (osłona elewacji) | W | 6,07 | 4,00 |
| LAM-S | lamele (osłona elewacji) | W | 6,30 | 4,00 |
| S2-08 | ściana zewn. P2 (z otworami) | W | 6,30 | 4,00 |
| IZ-ST2Z | płyta wysunięta/okap/daszek | W | 6,30 | 4,00 |
| D1 | dach z attyką | W | 6,30 | 4,00 |
| D2/przelew@[-0.3, 7.2] | przelew awaryjny (rzygacz ~0,15 m) | W | 7,15 | 4,00 |
| S0-07 | ściana zewn. P0 (z otworami) | W | 7,30 | 4,00 |
| S1-04 | ściana zewn. P1 (z otworami) | W | 7,30 | 4,00 |
| D2 | dach z attyką | W | 7,30 | 4,00 |
| RS3 | rura spustowa zewn. | W | 7,94 | 4,00 |
| D1/przelew@[2.0, 5.425] | przelew awaryjny (rzygacz ~0,15 m) | W | 9,45 | 4,00 |
| SL1 | słup | W | 9,74 | 4,00 |
| S2-06 | ściana zewn. P2 (bez otworów) | W | 11,18 | 3,00 |
| PL-C1 | płyta wysunięta/okap/daszek | W | 11,20 | 4,00 |
| PL-C2 | płyta wysunięta/okap/daszek | W | 11,20 | 4,00 |
| SL7 | słup | W | 11,55 | 4,00 |
| SL2 | słup | W | 11,64 | 4,00 |
| S0-05 | ściana zewn. P0 (bez otworów) | W | 19,30 | 3,00 |

Najbardziej wysunięty ku drodze element budynku leży 0,95 m przed nieprzekraczalną linią zabudowy (po stronie działki).

## 6. Pełna lista kontroli

| Sekcja | Element | Parametr | Wartość | Wymóg | Status | Podstawa |
|---|---|---|---|---|---|---|
| Wysokości | 0.03 WC gościnne | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 0.04 Klatka schodowa | h pod belką B8 | 2,50 | ≥ 2,20 (lokalnie) | OK | WT §72 (lokalne obniżenie) |
| Wysokości | 0.05 Spiżarnia (pod schodami) | strefy h pod schodami | ≥2,20: 1,03 m²; 1,40–2,20: 1,49 m²; <1,40: 2,82 m²; h_min 1,37 | pomocnicze ≥ 2,20 (brief §5); gospodarcze ≥ 2,00 (WT §97) | UWAGA | brief §5; WT §97 ust. 1 [W-053]; RPB §20 / PN-ISO 9836 [W-316] |
| Wysokości | 0.06 Salon + jadalnia + kuchnia | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 0.09 Łazienka gościnna (natrysk) | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 0.10 Pokój gościnny / gabinet | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 0.12 Pomieszczenie techniczne | h w świetle | 2,75 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 0.13 Garaż 2-stanowiskowy | h w świetle | 2,85 | ≥ 2,20 | OK | WT §102 pkt 1 [W-110] |
| Wysokości | 1.02 Pokój rodzinny / biblioteka (boks C) | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.03 Pokój dziecka 1 | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.04 Pokój dziecka 2 | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 1.05 Łazienka dzieci (wanna) | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 1.06 Klatka schodowa | h pod belką B9 | 2,50 | ≥ 2,20 (lokalnie) | OK | WT §72 (lokalne obniżenie) |
| Wysokości | 1.07 WC z natryskiem | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 1.08 Pralnia z suszarnią | h w świetle | 2,77 | ≥ 2,20 | OK | brief §5 |
| Wysokości | 2.02 Sypialnia rodziców | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 2.03 Garderoba (przedpokój apartamentu) | h w świetle | 2,77 | ≥ 2,20 | OK | brief §5 |
| Wysokości | 2.04 Łazienka rodziców | h w świetle | 2,53 | ≥ 2,20 (went. mech.) | OK | WT §77 ust. 3 [W-052] |
| Wysokości | 2.05 Gabinet / pokój | h w świetle | 2,77 | ≥ 2,50 (cel 2,70–2,80) | OK | WT §72 ust. 1 [W-050] |
| Wysokości | 2.07 Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 0.14 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 1.09 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Wysokości | 2.08 Szacht instalacyjny SI | h w świetle | 2,77 | ≥ 2,00 | OK | WT §97 ust. 1 [W-053] |
| Powierzchnie | 0.06 Salon + jadalnia + kuchnia | pow. netto | 54,44 m² | ≥ 50,0 m² | OK | brief §4 / założenie (salon+jadalnia+kuchnia ≥ 50 m²; pokój dzienny ≥ 16 m²) |
| Powierzchnie | 0.10 Pokój gościnny / gabinet | pow. netto | 12,52 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | 1.02 Pokój rodzinny / biblioteka (boks C) | pow. netto | 28,36 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | 1.03 Pokój dziecka 1 | pow. netto | 13,19 m² | ≥ 12,0 m² | OK | brief §4 [W-068] |
| Powierzchnie | 1.04 Pokój dziecka 2 | pow. netto | 12,52 m² | ≥ 12,0 m² | OK | brief §4 [W-068] |
| Powierzchnie | 2.02 Sypialnia rodziców | pow. netto | 21,43 m² | ≥ 14,0 m² | OK | brief §4 / założenie (sypialnia rodziców ≥ 14 m²) |
| Powierzchnie | 2.05 Gabinet / pokój | pow. netto | 16,32 m² | ≥ 8,0 m² | OK | brief §5 (nie WT; dawny §94 ust. 2 uchylony Dz.U. 2017 poz. 2285) [W-068] |
| Powierzchnie | budynek | PU mieszkalna (podst.+pomocn.+komunikacja, bez klatek, garażu, techn.) | 239,31 m² | 230–270 m² | OK | brief §4 [W-068]; RPB §20 / PN-ISO 9836 [W-316] |
| Powierzchnie | 0.06 | strefa dzienna otwarta (salon+jadalnia+kuchnia) | 54,44 m² | ≥ 50,0 m² | OK | brief §4 (TWARDE ZAŁOŻENIA) |
| Oświetlenie | 0.06 Salon + jadalnia + kuchnia | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,611 (mur: 0,697; O0-01, O0-02, O0-03, O0-04, O0-05, O0-11) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 0.10 Pokój gościnny / gabinet | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,176 (mur: 0,216; O0-12) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.02 Pokój rodzinny / biblioteka (boks C) | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,387 (mur: 0,451; O1-01, O1-02) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.03 Pokój dziecka 1 | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,167 (mur: 0,205; O1-06) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 1.04 Pokój dziecka 2 | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,176 (mur: 0,216; O1-05) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 2.02 Sypialnia rodziców | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,436 (mur: 0,504; O2-01, O2-04) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Oświetlenie | 2.05 Gabinet / pokój | A_okien/A_podłogi (w świetle ościeżnic, szac.) | 0,354 (mur: 0,423; O2-03, O2-05) | ≥ 0,125 | OK | WT §57 ust. 2 (1/8, w świetle ościeżnic) [W-080] |
| Schody | SCH1 | wysokość stopnia h | 0,175 | ≤ 0,190 (projekt ≈ 0,175) | OK | WT §68 ust. 1 [W-090] |
| Schody | SCH1 | 2h+s | 0,630 | 0,60–0,65 | OK | WT §69 ust. 4 [W-091] |
| Schody | SCH1 | Σ podnóżków × h = Δ kondygnacji | 18 × 0,175 = 3,150 vs 3,150 | równe | OK | geometria |
| Schody | SCH2 | wysokość stopnia h | 0,175 | ≤ 0,190 (projekt ≈ 0,175) | OK | WT §68 ust. 1 [W-090] |
| Schody | SCH2 | 2h+s | 0,630 | 0,60–0,65 | OK | WT §69 ust. 4 [W-091] |
| Schody | SCH2 | Σ podnóżków × h = Δ kondygnacji | 18 × 0,175 = 3,150 vs 3,150 | równe | OK | geometria |
| Schody | SCH1/bieg1 | szerokość biegu w świetle ścian | 1,150 (model: 1,150) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH1/bieg1 | prześwit nad biegiem (min.) | 2,325 (element: B8) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH1/bieg2 | szerokość biegu w świetle ścian | 1,145 (model: 1,145) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH1/bieg2 | prześwit nad biegiem (min.) | 2,763 (element: SCH2/bieg2) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH2/bieg1 | szerokość biegu w świetle ścian | 1,150 (model: 1,150) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH2/bieg1 | prześwit nad biegiem (min.) | 2,325 (element: B9) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH2/bieg2 | szerokość biegu w świetle ścian | 1,145 (model: 1,145) | ≥ 1,00 (WT ≥ 0,80) | OK | brief §5 [W-090]; WT §68 ust. 1 (budynki jednorodzinne) [W-090] |
| Schody | SCH2/bieg2 | prześwit nad biegiem (min.) | 2,805 (element: D1) | ≥ 2,00 | OK | R3 K-22 (dobra praktyka) [W-100] |
| Schody | SCH1/spocznik1 | głębokość spocznika | 1,175 | ≥ szer. biegu 1,150 | OK | WT §68 ust. 1 [W-090]; brief §5 |
| Schody | SCH1/spocznik1 | prześwit nad spocznikiem (min.) | 2,970 (SCH2/spocznik1) | ≥ 2,00 | OK | R3 K-22 |
| Schody | SCH2/spocznik1 | głębokość spocznika | 1,175 | ≥ szer. biegu 1,150 | OK | WT §68 ust. 1 [W-090]; brief §5 |
| Schody | SCH2/spocznik1 | prześwit nad spocznikiem (min.) | 4,355 (D1) | ≥ 2,00 | OK | R3 K-22 |
| Schody | BL1 | wysokość balustrady/pochwytu | 0,90 | ≥ 0,90 | OK | WT §298 ust. 1–2 (budynki jednorodzinne; prześwit nieregulowany) [W-095] |
| Schody | BL2 | wysokość balustrady/pochwytu | 0,90 | ≥ 0,90 | OK | WT §298 ust. 1–2 (budynki jednorodzinne; prześwit nieregulowany) [W-095] |
| Odległości | S0-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-02 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-03 | lico zewn. → granica E | 5,73 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S0-05 | lico zewn. → granica W | 19,30 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S0-07 | lico zewn. → granica W | 7,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-02 | lico zewn. → granica E | 12,10 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S1-04 | lico zewn. → granica W | 7,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-01 | lico zewn. → granica S | 32,40 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-02 | lico zewn. → granica E | 12,10 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | S2-04 | lico zewn. → granica E | 15,60 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S2-06 | lico zewn. → granica W | 11,18 m | ≥ 3,00 (bez otworów) | OK | WT §12 ust. 1 pkt 2 [W-002] |
| Odległości | S2-08 | lico zewn. → granica W | 6,30 m | ≥ 4,00 (okna/drzwi) | OK | WT §12 ust. 1 pkt 1 i część wspólna (Dz.U. 2023 poz. 2442, 2024 poz. 726); każdy uskok = odrębna ściana [W-001] |
| Odległości | PL-E | płyta wysunięta/okap/daszek → granica E | 10,60 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-E | płyta wysunięta/okap/daszek → granica W | 5,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C1 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C1 | płyta wysunięta/okap/daszek → granica W | 11,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C2 | płyta wysunięta/okap/daszek → granica E | 10,95 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-C2 | płyta wysunięta/okap/daszek → granica W | 11,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-2 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-2 | płyta wysunięta/okap/daszek → granica W | 5,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-3 | płyta wysunięta/okap/daszek → granica E | 11,80 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | PL-3 | płyta wysunięta/okap/daszek → granica W | 5,20 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | IZ-ST2Z | płyta wysunięta/okap/daszek → granica W | 6,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D1 | dach z attyką → granica W | 6,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D2 | dach z attyką → granica W | 7,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4 | dach z attyką → granica E | 5,73 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | T1 | taras naziemny/podest → granica W | 4,30 m | ≥ 1,50 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | T3 | taras naziemny/podest → granica E | 10,90 m | ≥ 1,50 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-S | lamele (osłona elewacji) → granica W | 6,30 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-W | lamele (osłona elewacji) → granica W | 6,07 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | LAM-E | lamele (osłona elewacji) → granica E | 11,87 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL1 | słup → granica W | 9,74 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL2 | słup → granica W | 11,64 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | SL7 | słup → granica W | 11,55 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D1/przelew@[2.0, 5.425] | przelew awaryjny (rzygacz ~0,15 m) → granica W | 9,45 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | RS3 | rura spustowa zewn. → granica W | 7,94 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D2/przelew@[-0.3, 7.2] | przelew awaryjny (rzygacz ~0,15 m) → granica W | 7,15 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D3/przelew@[12.3, 7.2] | przelew awaryjny (rzygacz ~0,15 m) → granica E | 11,95 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | RS5 | rura spustowa zewn. → granica E | 5,61 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4/przelew@[18.675, 6.5] | przelew awaryjny (rzygacz ~0,15 m) → granica E | 5,58 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| Odległości | D4/przelew@[18.675, 2.4] | przelew awaryjny (rzygacz ~0,15 m) → granica E | 5,58 m | ≥ 4,00 (założenie proj.); WT ≥ 1,50 | OK | WT §12 ust. 6 pkt 1 (płyty wysunięte traktowane jak okapy — interpretacja) [W-004]; TWARDE ZAŁOŻENIA |
| MPZP | linia zabudowy | najdalej wysunięty element (+ = przekroczenie) | -0,95 m (T2) | ≤ 0,00 | OK | MPZP 3MN (fikcyjny) — nieprzekraczalna linia zabudowy od 1KDD; żaden element jej nie przekracza [W-006] |
| MPZP | pow. zabudowy (1) obrys ścian zewn. wszystkich kondygnacji | A_z | 187,50 m² (11,7 %) | ≤ 480,00 m² | OK | MPZP 3MN × 1600,00 m² [W-030] |
| MPZP | pow. zabudowy (2) kontrolnie z płytami wysuniętymi | A_z+ | 212,99 m² (13,3 %) | ≤ 480,00 m² | OK | rejestr D-06 |
| MPZP | intensywność zabudowy | Σ pow. kondygnacji nadziemnych / pow. działki | 396,39 / 1600,00 = 0,248 | 0,05–0,80 | OK | MPZP 3MN; upzp art. 2 pkt 31–33 (nadziemna) [W-032] |
| MPZP | pow. biologicznie czynna (teren) | PBC | 1268,19 m² (79,3 %) | ≥ 800,00 m² | OK | MPZP 3MN × 1600,00 m² [W-031]; opaska żwirowa wyłączona z PBC (ostrożnie); teren nad zbiornikiem ≈ 3,1 m² wyłączony (W-031) |
| MPZP | miejsca postojowe | liczba (garaż + zewn.) | 4 (2 w garażu) | ≥ 2 | OK | MPZP 3MN; WT §18 ust. 2 [W-036] |
| MPZP | kondygnacje nadziemne | liczba | 3 | ≤ 3 | OK | MPZP 3MN; warunek WT §213 pkt 1 lit. a [W-034] |
| MPZP | D1 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D2 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D3 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | D4 | spadek dachu | 2,0 % (1,1°) | ≤ 12° | OK | MPZP 3MN [W-035] |
| MPZP | ogrodzenie [0.0, 50.0]→[17.6, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| MPZP | ogrodzenie [18.6, 50.0]→[20.3, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| MPZP | ogrodzenie [25.9, 50.0]→[32.0, 50.0] | wysokość (od drogi) | 1,50 | ≤ 1,60; ażurowe | OK | MPZP 3MN (ażurowe, bez prefabrykatów betonowych) [W-038] |
| Zagospodarowanie | przesuwna @ [23.1, 50.0] | szerokość w świetle | 5,60 | ≥ 2,40 | OK | WT §43 [W-017] |
| Zagospodarowanie | furtka @ [18.1, 50.0] | szerokość w świetle | 1,00 | ≥ 0,90 | OK | WT §43 [W-017] |
| MPZP | wysokość zabudowy (upzp art. 2 pkt 30) | od najniższego terenu 101,32 do wyrzutnia (+10,000) | 10,33 m (od średniej 101,40: 10,25 m) | ≤ 11,00 (z rezerwą ≤ 10,70) | OK | MPZP 3MN; upzp art. 2 pkt 30 [W-033]; rejestr D-15 |
| WT | wysokość budynku wg WT §6 | teren przy wejściu O0-04: 101,32 → wierzch D1 z izol. (+9,626) | 9,96 m | ≤ 12,00 (N); ≤ 11,00 (MPZP) | OK | WT §8 pkt 1 (lub ≤ 4 kondygnacje mieszkalne) [W-063]; [W-063] |
| Garaż | 0.13 | wymiary w świetle | 6,05 × 6,17 m | ≥ 5,60 × 6,00 | OK | WT §104 + §21 ust. 1 (0,3 + 2×2,5 + 0,3) [W-112]; brief §4 |
| Garaż | O0-07 | brama w świetle | 5,00 × 2,25 | ≥ 2,30 × 2,00 | OK | WT §102 pkt 2 [W-111] |
| Garaż | MP1 | stanowisko | 2,70 × 5,90 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Garaż | MP1 | dłuższa krawędź stanowiska → lico ściany | 0,18 m | ≥ 0,30 | NIEZGODNE | WT §104 ust. 1 pkt 1 [W-112] |
| Garaż | MP2 | stanowisko | 2,70 × 5,90 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Garaż | MP2 | dłuższa krawędź stanowiska → lico ściany | 0,27 m | ≥ 0,30 | NIEZGODNE | WT §104 ust. 1 pkt 1 [W-112] |
| Zagospodarowanie | MP3 | stanowisko | 2,50 × 5,00 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Zagospodarowanie | MP3 | odl. od granic bocznych/tylnej | 9,00 m | ≥ 3,00 (granica z drogą — bez wymogu) | OK | WT §19 ust. 2 pkt 1 lit. a (nie dotyczy granicy z działką drogową, ust. 7) [W-015] |
| Zagospodarowanie | MP4 | stanowisko | 2,50 × 5,00 m | ≥ 2,50 × 5,00 | OK | WT §21 ust. 1 pkt 1 [W-014] |
| Zagospodarowanie | MP4 | odl. od granic bocznych/tylnej | 6,30 m | ≥ 3,00 (granica z drogą — bez wymogu) | OK | WT §19 ust. 2 pkt 1 lit. a (nie dotyczy granicy z działką drogową, ust. 7) [W-015] |
| Garaż | O0-22 (drzwi garaż–dom) | różnica posadzek dom − garaż przy drzwiach | 0,009 m (posadzka przy bramie -0,10, spadek 1,5 % na 6,10 m) | ≥ 0,030 (próg) | UWAGA | WT §107 ust. 2 [W-114] |
| Garaż | O0-07 | wrota → okna: pion / poziom (pobyt ludzi) | brak okien nad wrotami / 9,43 m | ≥ 1,50 / ≥ 1,50 | OK | WT §279 ust. 1 (wszystkie okna) [W-117] |
| WT | O0-09 | drzwi wejściowe (światło ościeżnicy, szac.) | 0,96 × 2,33 | ≥ 0,90 × 2,00 | OK | WT §62 ust. 1 (w świetle ościeżnicy) [W-055] |
| WT | PL-DA | daszek nad wejściem: wysięg / szerokość | 1,30 / 2,30 m | ≥ 1,00 / ≥ 2,10 | OK | WT §292 ust. 1 (budynek > 2 kondygnacji, grupa N) [W-057] |
| WT | O1-01 | podokiennik | 0,70 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-01 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-01 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-02 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-03 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-03 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-04 | podokiennik | 0,60 m + dolna część stała VSG | ≥ 0,85 albo zabezpieczenie | OK | WT §301 ust. 1, 3 (poza przyziemiem) [W-097] |
| WT | O2-04 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-05 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-06 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | O2-07 | otwieranie okna P2 | do_wewn | do wewnątrz | OK | WT §299 ust. 2 [W-098] |
| WT | WYL1 | wyłaz dachowy w świetle | 0,90 × 0,90 | ≥ 0,80 × 0,80 | OK | WT §308 ust. 3 [W-065] |
| Wentylacja | czerpnia dachowa | wysokość nad pokryciem (lokalnie, klin) | 0,377 m (pokrycie ≈ +9,573) | ≥ 0,40 | UWAGA | WT §152 ust. 4 [W-166] |
| Wentylacja | wyrzutnia dachowa | wysokość nad pokryciem (lokalnie, klin) | 0,484 m | ≥ 0,40 | OK | WT §152 ust. 7 (także nad punktami w promieniu 10 m) [W-167] |
| Wentylacja | czerpnia ↔ wywiewka kanalizacyjna | odległość | 7,81 m | ≥ 6,00 | OK | WT §152 ust. 4 [W-166] |
| Wentylacja | czerpnia ↔ wyrzutnia (dach) | odległość / wyrzutnia wyżej o | 9,81 m / 0,05 m | ≥ 10,00 m, albo ≥ 6,00 m przy wyrzutni ≥ 1,00 m wyżej (lub zestaw zblokowany) | NIEZGODNE | WT §152 ust. 10 [W-167]; R6-43 |
| Wentylacja | wyrzutnia ↔ okno w dachu SW1 | odległość / wylot ponad oknem | 6,12 m / 0,25 m | 3–10 m ⇒ wylot ≥ 1,00 m nad górną krawędzią okna (≥ +10,75) | UWAGA | WT §152 ust. 12 [W-167]; R6-43 |
| Wentylacja | wyrzutnia ↔ krawędź dachu nad oknami | odległość | 3,10 m | ≥ 3,00 | OK | WT §152 ust. 12 [W-167] |
| Zagospodarowanie | PC-JZ (jedn. zewn. PC) | odl. od granic | S 31,65, E 7,60, N 18,35, W 24,40 | ≥ 3,0 (założenie); E ≥ 6,0 | OK | R8 3.4 [W-024] |
| Zagospodarowanie | PC-JZ (jedn. zewn. PC) | elewacja, przy której stoi jednostka | S (x 24,40, y 31,65 w ukł. działki; 0,75 m od lica) | N lub E (TWARDE ZAŁOŻENIA) | UWAGA | TWARDE ZAŁOŻENIA (energia i światło); W-024 (hałas) |
| Zagospodarowanie | PC-JZ strefa R290 | otwory/wpusty/studzienki w strefie 1,0 m | brak | brak | OK | dane producentów (DTR); PN-EN 378-1+A1:2021-03 [W-156] |
| Zagospodarowanie | retencja/zbiornik | odl. od granic / od budynku | min 10,60 / 5,70 m | ≥ 2,0 / ≥ 3,0 | OK | R8 3.5 [W-144] [W-144, W-145] |
| Zagospodarowanie | retencja/rozsaczanie | odl. od granic / od budynku | min 8,60 / 12,70 m | ≥ 2,0 / ≥ 3,0 | OK | R8 3.5 [W-144] [W-144, W-145] |
| Zagospodarowanie | miejsce na pojemniki | odl. od granic | S 48,60, E 14,80, N 0,10, W 14,00 | zabudowa jednorodzinna — odległości nieustalone (WT §23 ust. 4) | INFO | WT §22, §23 ust. 4 [W-016] |
| Sąsiedztwo | dz. 123/3 | odl. budynek–budynek sąsiedni | 14,31 m | ≥ 8,00 (ppoż.); ≥ H = 10,33 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 123/5 | odl. budynek–budynek sąsiedni | 13,72 m | ≥ 8,00 (ppoż.); ≥ H = 10,33 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 118/2 | odl. budynek–budynek sąsiedni | 28,13 m | ≥ 8,00 (ppoż.); ≥ H = 10,33 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| Sąsiedztwo | dz. 118/3 | odl. budynek–budynek sąsiedni | 29,86 m | ≥ 8,00 (ppoż.); ≥ H = 10,33 (przesłanianie, uproszcz.) | OK | WT §271 ust. 1 [W-010]; WT §13, §60 |
| WT | kubatura brutto (lamela, PN-ISO 9836) | V | 1354,5 m³ | > 1000 m³ ⇒ PWP (W-190); uprawnienia bez ogr. | INFO | WT §3 pkt 24; PB art. 15a [W-069] |
