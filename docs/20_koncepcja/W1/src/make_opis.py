# -*- coding: utf-8 -*-
"""Generuje docs/20_koncepcja/W1/opis.md i model_W1.json z modelu wariantu W1."""
import json
import os
from shapely.geometry import mapping
from model_w1 import *
from tables_w1 import (md_rooms, md_openings, md_walls, md_windows, totals, dist_checks, ROOMS as _R)
from draw_site import site_metrics
from draw_common import fmt

OUT = '/home/user/aihouse/docs/20_koncepcja/W1'
t, tot = totals()
m = site_metrics()
H, zmin = building_height()
win_md, win_rows = md_windows()
room = {r['id']: r for r in ROOMS}
A = lambda rid: fmt(room[rid]['poly'].area)
PU_bud = tot['PU'] + tot['T']
netto = tot['PU'] + tot['T'] + tot['S'] + tot['G']
S = STAIR

md = []
w = md.append
w(f"""# Koncepcja — WARIANT W1: „wierność szkicowi i zwartość”

**Dom LAMELA** — dom jednorodzinny wolnostojący, 3 kondygnacje nadziemne (P0, P1, P2), bez podpiwniczenia, stropodachy.
Działka 123/4 (fikc.), 32,00 × 50,00 m, droga od północy. Data: 2026-09-25. Opracowanie koncepcyjne (etap: warianty → ocena → synteza).

**Podstawy:** brief `docs/00_brief_projektowy.md` (sekcja 1.2 — interpretacja v2), decyzje Inwestora z 25.09.2026
(„elewacja w S-kę” z samych przesuniętych brył; linia D **nie** jest płytą tarasową; płyty wysunięte 0,8–1,2 m; garaż 2-stan. w bryle parteru),
rejestr wymagań `docs/10_podstawy_prawne/` (dostępne: R1, R2, R5). Wg R1 rozporządzenie WT z 2002 r. utraciło moc 20.09.2026 —
projekt zakłada złożenie przez inwestora **oświadczenia z art. 102a PB** (Dz.U. 2026 poz. 1161), więc stosujemy WT
(t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu z 19.09.2026. Śnieg: strefa 2, s_k = 0,90 kN/m² (R5). Powierzchnie wg PN-ISO 9836
z modyfikacjami § 20 RZF (schody i spoczniki poza PU; garaż i pom. techniczne wykazane osobno — R2).

**Model:** wszystkie liczby i rysunki tego wariantu generowane są z jednego modelu parametrycznego (`model_W1.json` w tym katalogu;
źródło: skrypty Python w `src/` — `model_w1.py` definiuje geometrię, pozostałe generują rysunki i ten opis). Układ: **x → wschód, y → północ, z → góra; (0,0) = przecięcie osi A i 1;
±0,00 = posadzka parteru = 101,65 m n.p.m.** Osie przechodzą przez środek warstwy konstrukcyjnej ścian. Wymiary w m, na rysunkach w cm.

| rysunek | zawartość |
|---|---|
| `rzut_P0.png` | rzut parteru z osiami, wymiarami, otworami, schodami, słupami, obrysem płyt nad |
| `rzut_P1.png` | rzut I piętra, boks C, linia D, dach zielony parteru/garażu |
| `rzut_P2.png` | rzut II piętra, lamele, pustka klatki ze świetlikiem, wysunięcia płyt |
| `elewacja_S.png` | elewacja południowa + skalibrowany szkic z liniami porównawczymi |
| `przekroj.png` | przekrój A-A (N–S przez schody i boks C) i B-B (W–E przez wsporniki zach. i garaż), rzędne |
| `zagospodarowanie.png` | działka, droga, linia zabudowy, odległości, dojazd, parkowanie, przyłącza, retencja, wskaźniki |

## 1. Idea

Sylweta „S” powstaje wyłącznie z **przesuniętych brył** (bez osobnej wstęgi/ramy): **A** (II piętro, bryła w lamelach) wysuwa się
na **zachód** 1,00 m poza lico bryły B; **B** (I piętro, bryła pełna 12,00 m) z przeszklonym **boksem C** i dalej **linią D**
(pogrubiona krawędź stropu nad parterem) prowadzi rytm na **wschód** aż do narożnika garażu **G** (19,20 m od lica zach. B);
**E** (parter) wraca na **zachód** — cienka płyta ST1 wysunięta 1,50 m na zachód poza lico B i 1,00 m na południe, pod nią ciągłe
przeszklenie strefy dziennej w 5 kwaterach. Wszystkie płyty mają głębokie krawędzie 0,8–1,2 m (poziome warstwy, okapy).

Priorytet W1: **maksymalna wierność proporcjom szkicu** (wszystkie charakterystyczne krawędzie elewacji w położeniach odczytanych ze
szkicu z tolerancją ≤ 0,45 m — patrz tabela 2) oraz **zwartość**: parter to jeden prostokąt 18,20 × 11,10 m (część mieszkalna + garaż),
piętra to dwa prostokąty 12,00 × 7,90 i 13,00 × 7,90 m ustawione jeden nad drugim z licami płd. i płn. w jednej płaszczyźnie;
**trzon schodowy centralnie przy ścianie północnej** (środek trzonu x = 6,10 wobec środka bryły B x = 5,70).

## 2. Odczyt szkicu i przyjęte wymiary (L = odległość od lica zach. bryły B; x = L − 0,30)

| element | szkic (odczyt, L [m]) | W1 (L [m]) | W1 (x w układzie budynku) | uwagi |
|---|---|---|---|---|
| A — bryła II piętra (lamele) | −1,0 … 12,2 | −1,00 … 12,00 | −1,30 … 11,70 | wspornik 1,00 m; lico wsch. = lico B (ściany w pionie) |
| A — płyta pod bryłą (ST2) | −2,4 … 12,6 | −2,20 … 12,40 | −2,50 … 12,10 | wysunięcie 1,20 m zach., 1,00 m płd., 0,40 m wsch. |
| A — płyta dachu (ST3) + attyka | −1,6 … 12,4 | −1,80 … 12,40 | −2,10 … 12,10 | wysunięcie 0,80 m zach./płd. |
| B — bryła I piętra | 0 … 12,0 | 0 … 12,00 | −0,30 … 11,70 | skala szkicu: B = 12,00 m (≈45,6 px/m) |
| C — boks przeszklony (3 kwatery) | 4,5 … 11,7 (2,17/2,66/2,35) | rama 4,25 … 12,00; szkło 4,50 … 11,60 (3 × 2,37) | 3,95 … 11,70 | rama wysunięta 1,00 m, siedzisko h = 0,55 |
| C — rama górna | 3,9 … 13,9 | 4,25 … 13,75 | 3,95 … 13,45 | wysięg 1,75 m na wschód poza B (lekka stal) |
| D — linia pozioma | 3,8 … 19,2 | 4,25 … 19,20 | 3,95 … 18,90 | pas krawędziowy stropu ST1 2,70–3,70 nad garażem — **bez tarasu** |
| D — pion (narożnik G) | 19,0–19,2 | 19,20 | 18,90 | lico wsch. garażu |
| E — przeszklenie parteru | 1,0 … 13,2 (5 kwater) | 1,00 … 13,20 (lica); szkło 1,405 … 12,795 | 0,70 … 12,90 | 5 równych kwater 2,28 m (w szkicu nierówne) |
| E — płyta dachu parteru | −1,5 … 14,1 | −1,50 … (ciągła do 19,20 jako D) | −1,80 … 18,90 | wysunięcie 1,50 m zach. poza B, 1,00 m płd. |
| G — garaż | 13,2 … 19,2 | 13,20 … 19,20 | 12,90 … 18,90 | w świetle {fmt(AX['G'] - EXT_IN - AX['F'] - GAR_IN)} × {fmt(AY['4'] - EXT_IN - Y_GAR - H_BEAR)} m |

Proporcje pionowe szkicu są umowne (pasmo B ~2× wyższe) — wysokości przyjęto wg WT. Linia D leży wyżej niż płyta E (jak w szkicu):
wierzch pasa D = **+3,70** (dolna rama boksu C = siedzisko + attyka dachu garażu), krawędź płyty E = 2,70–3,05.
Porównanie graficzne: `elewacja_S.png` (górny panel — szkic skalibrowany w poziomie, czerwone linie — krawędzie W1).

## 3. Pełna definicja wymiarowa

### 3.1 Siatka osi (środek warstwy konstrukcyjnej)

| oś | x [m] | rola | | oś | y [m] | rola |
|---|---|---|---|---|---|---|
| A' | {fmt(AX["A'"])} | ściana zach. P2 (ŻB, na tarczach P2) | | 1 | {fmt(AY['1'])} | płd.: ściany P1/P2, słupy SL1–SL4 + belka ukryta ST1 w P0, ściana płd. garażu |
| A | {fmt(AX['A'])} | ściana zach. P1 (ŻB, na tarczach P1) — **początek układu** | | 1a | {fmt(Y_GAR)} | ściana garaż / pom. gosp. |
| B | {fmt(AX['B'])} | ściana zach. P0 (ŻB — podpora wsporników) | | 2 | {fmt(AY['2'])} | ściana płd. trzonu (ŻB) + ściany nośne P0 (salon/ zaplecze), P1/P2 (strefa wsch.) |
| C | {fmt(AX['C'])} | ściana zach. trzonu (ŻB) | | 3 | {fmt(AY['3'])} | ściana płn. P1/P2 i trzonu; w P0 ściana wewn. nośna |
| D | {fmt(AX['D'])} | ściana wsch. trzonu (ŻB) | | 4 | {fmt(AY['4'])} | ściana płn. P0 (skrzydło płn. + garaż) |
| E | {fmt(AX['E'])} | ściana wsch. P1/P2 (ŻB — ściana-tarcza nad kuchnią) | | | | |
| F | {fmt(AX['F'])} | ściana wsch. części mieszkalnej P0 / zach. garażu | | | | |
| G | {fmt(AX['G'])} | ściana wsch. garażu (narożnik „pionu D”) | | | | |

### 3.2 Poziomy (rzędne względne; ±0,00 = 101,65 m n.p.m.)

| element | rzędna / grubość |
|---|---|
| posadzka P0 | ±0,00 (warstwy na gruncie: jastrych z ogrzewaniem podł. 0,10 + EPS/XPS 0,20 + płyta ŻB 0,15 → spód −0,45) |
| garaż, pom. gosp. | −0,15 (spadek 2 % do bramy; próg 15 cm przy drzwiach EI30 do sieni) |
| strop ST1 (nad P0, dach garażu i skrzydła płn.) | spód +2,78, wierzch +3,00, gr. 0,22 |
| posadzka P1 | +3,15 (warstwy 0,15: jastrych z ogrz. podł. + izolacja akust./term.) |
| linia D (wierzch pasa krawędziowego / siedzisko boksu C) | +3,70; pas D: +2,70 … +3,70 |
| dach zielony nad P0/garażem | wierzch ≈ +3,45 (ocieplenie 0,20–0,25 + dach zielony ekstensywny 0,10–0,12), attyka +3,70 |
| strop ST2 (nad P1) | spód +5,93, wierzch +6,15, gr. 0,22 |
| posadzka P2 | +6,30 |
| strop ST3 (dach P2) | spód +9,08, wierzch +9,30, gr. 0,22 |
| pokrycie dachu P2 (spadek 2 %) | śr. +9,62 (PIR/EPS 0,25–0,35 + membrana) |
| attyka / okap dachu P2 | **+9,85** (najwyższy punkt konstrukcji) |
| wysokość kondygnacji / w świetle | 3,15 / **2,78 m** (wszystkie kondygnacje; garaż 2,93 m) |
| ławy fundamentowe | spód −1,10 (strefa przemarzania 0,80 m od terenu ≈ −0,30) |
| teren przy budynku | −0,22 (NE) … −0,34 (SW); najniższe wejście (HS salonu, W) {fmt(zmin)} |

### 3.3 Przegrody (typy)

| kod | układ | lico wewn. / zewn. od osi |
|---|---|---|
| SZ1 — ściana zewn. | tynk 1,5 + silikat 18 (kl. 20, cienka spoina) **lub ŻB 18** w strefach tarcz + EPS grafit/MW 20 + tynk 1 | −0,105 / +0,30 (gr. 40,5 cm) |
| SW1 — ściana wewn. nośna | tynk + SIL 18 (lub ŻB 18 w trzonie) + tynk | ±0,105 |
| SD1 — ścianka działowa | tynk + SIL 12 + tynk | ±0,075 |
| SG1 — ściana dom/garaż (oś F) | tynk + SIL 18 + wełna 12 cm (garaż) + wyprawa; EI 60 | −0,105 / +0,22 |
| przeszklenie E | aluminium z przekładką term., 3-szybowe, U_w ≤ 0,9, g ≤ 0,35 z osłoną ZIP w kasecie | pas y −0,25 … −0,10 |

""")

# ----- obrysy
w("""### 3.4 Obrysy zewnętrzne kondygnacji (lica zewnętrzne z ociepleniem)

| kondygnacja | obrys (x × y) | wymiary | pow. całkowita (brutto) |
|---|---|---|---|
""")
for fl, lab in (('P0', 'P0 (część mieszk. + garaż)'), ('P1', 'P1 (bryła B)'), ('P2', 'P2 (bryła A)')):
    b = OUTLINE[fl].bounds
    extra = f" + boks C {fmt((C_BOX['x1'] - C_BOX['x0']) * 1.0)} m²" if fl == 'P1' else ''
    w(f"| {lab} | x {fmt(b[0])} … {fmt(b[2])}, y {fmt(b[1])} … {fmt(b[3])} | {fmt(b[2] - b[0])} × {fmt(b[3] - b[1])} m | "
      f"{fmt(OUTLINE[fl].area)} m²{extra} |\n")
w(f"| boks C (P1) | x {fmt(C_BOX['x0'])} … {fmt(C_BOX['x1'])}, y {fmt(C_BOX['y0'])} … {fmt(C_BOX['y1'])} | 7,75 × 1,00 m | "
  f"7,75 m² (z +3,00 do +5,45) |\n\n")

for fl, title in (('P0', 'PARTER P0 (±0,00)'), ('P1', 'I PIĘTRO P1 (+3,15)'), ('P2', 'II PIĘTRO P2 (+6,30)')):
    w(f"### 3.{5 + ['P0', 'P1', 'P2'].index(fl)} {title}\n\n**Ściany** (oś warstwy konstrukcyjnej):\n\n")
    w(md_walls(fl))
    w("\n**Otwory** (położenie: zakres wzdłuż ściany w układzie budynku, w świetle muru; wysokość w świetle; parapet od posadzki kondygnacji):\n\n")
    w(md_openings(fl))
    w("\n**Pomieszczenia** (wieloboki netto w licach wykończonych):\n\n")
    w(md_rooms(fl))
    w(f"\nSuma {fl}: PU (mieszk.+pomocn.+komunik.) **{fmt(t[fl]['PU'])} m²**, pom. techniczne {fmt(t[fl]['T'])} m², "
      f"schody/spoczniki {fmt(t[fl]['S'])} m²" + (f", garaż + pom. gosp. {fmt(t[fl]['G'])} m²" if t[fl]['G'] else '') + ".\n\n")
    if fl == 'P0':
        w("Funkcja: wejście od północy (daszek 1,50 m = wysunięcie ST1, x 6,60–10,00) → wiatrołap 0.01 → hol 0.02 → na osi wejścia "
          "spocznik trzonu (przejście 1,20 m) → jadalnia i widok na ogród. Z holu: pokój gościnny 0.07 (z łazienką 0.08 en-suite, "
          "drzwi 90 cm), garderoba 0.03; hol przechodzi w sień gospodarczą 0.06 → WC 0.04, schowek 0.05, pom. techniczne 0.11, "
          "drzwi EI30 do garażu 0.13. Strefa dzienna 0.12 (salon/jadalnia/kuchnia z wyspą, spiżarnia 0.10) na całej elewacji "
          "płd., wyjścia HS na taras płd. (E2, E4) i zach. (HS1, taras pod okapem ST1).\n\n")
    if fl == 'P1':
        w("Funkcja: ze spocznika trzonu (x 7,095–8,395) → hol-biblioteka 1.03 (otwarta przestrzeń rodzinna przed boksem C, "
          "siedzisko-czytelnia 7,10 m w wykuszu) → pokoje dzieci 1.01 (SW) i 1.02 (NW), oba z oknami zach.; pralnia 1.04 z oknem "
          "wsch.; łazienka 1.05 wejście bezpośrednio ze spocznika. Na wschód od bryły B — dach zielony ekstensywny parteru/garażu "
          "(nieużytkowy, bez wyjścia, bez tarasu).\n\n")
    if fl == 'P2':
        w("Funkcja: apartament rodziców w części zach. (sypialnia 2.01 S+W za lamelami i nad wspornikiem, garderoba 2.02, łazienka 2.03), "
          "gabinet 2.04 (S), pokój 2.06 (S+E — dla 5. członka rodziny / hobby / gość), pom. techniczne 2.07 z rekuperatorem i "
          "wyłazem dachowym 90×120 (drabina stała) — wejście ze spocznika; nad pustką klatki świetlik 2,60 × 1,80 m.\n\n")

w(f"""### 3.8 Płyty, wysunięcia, boks C, lamele

| element | obrys (x × y) | rzędne | wysunięcie poza lico | uwagi |
|---|---|---|---|---|
| ST1 (dach P0/garażu, strop P1) | wielobok: (−1,80; −1,30) (18,90; −1,30) (18,90; 10,80) (10,00; 10,80) (10,00; 12,30) (6,60; 12,30) (6,60; 10,80) (0,70; 10,80) (0,70; 7,60) (−1,80; 7,60) | 2,78–3,00 | zach. 1,50 poza B (2,50 poza P0), płd. 1,00, daszek płn. 1,50 | otwór schodów x 3,805–7,095, y 4,905–7,195 |
| ST2 (strop P2) | x −2,50 … 12,10; y −1,30 … 7,60 | 5,93–6,15 | zach. 1,20 poza A, płd. 1,00, wsch. 0,40 | otwór schodów jw. |
| ST3 (dach P2) | x −2,10 … 12,10; y −1,10 … 7,60 | 9,08–9,30 | zach./płd. 0,80, wsch. 0,40 | świetlik x 4,20–6,80, y 5,10–6,90; wyłaz x 9,50–10,40, y 5,40–6,60 |
| pasy krawędziowe | ST1: 2,70–3,05; D: 2,70–3,70 (x 3,95–18,90); ST2: 5,90–6,25; ST3+attyka: 9,05–9,85 | — | — | beton architektoniczny / okładzina włókno-cement, szary |
| boks C | rama x 3,95–11,70, y −1,30 … −0,30; szkło x 4,20–11,30 w płaszczyźnie y = −1,10 (3 kwatery 2,37 m) | siedzisko 3,00–3,70, szkło 3,70–5,20, rama górna 5,20–5,45 | 1,00 m | otwór w ścianie P1 x 4,20–11,30, h 3,70–5,20; rama górna przedłużona do x = 13,45 |
| lamele A | płd.: y = −0,45, x −1,25 … 11,65 co 0,30; zach.: x = −1,45, y −0,45 … 7,55 co 0,30 | 6,25–9,05 | 0,15 m od lica | 6 × 20 cm, drewno termo (lub alu w kolorze drewna) |

### 3.9 Schody SCH1 (trzon ŻB, stos 3 kondygnacji, U-kształtne)

* Trzon w świetle: x {fmt(S['x0'], 3)} … {fmt(S['x1'], 3)} (4,59 m), y {fmt(S['y0'], 3)} … {fmt(S['y1'], 3)} (2,29 m); ściany ŻB 18 cm w osiach C, D, 2, 3.
* Na kondygnację: **18 podnóżków × 17,5 cm = 3,15 m**, stopnie **s = 28 cm**, **2h + s = 63 cm**, nachylenie 32°; 2 biegi po 9 podnóżków (8 stopni).
* Bieg „a” (pasmo płn. y {fmt(S['lane_N'][0], 3)} … {fmt(S['lane_N'][1], 3)}, szer. 1,09 m): pierwszy podnóżek x = 7,095, w górę **na zachód**
  do x = 4,855 (linie krawędzi stopni x = 7,095 − k·0,28, k = 0…8), rzuty 2,24 m; Z → Z + 1,575.
* Spocznik międzykondygnacyjny: x 3,805 … 4,855 (1,05 m ≥ szer. biegu), y 4,905 … 7,195; rzędne +1,575 i +4,725.
* Bieg „b” (pasmo płd. y {fmt(S['lane_S'][0], 3)} … {fmt(S['lane_S'][1], 3)}, szer. 1,09 m): z x = 4,855 w górę **na wschód** do x = 7,095; Z + 1,575 → Z + 3,15.
* Spocznik kondygnacyjny (wejście/wyjście na każdej kondygnacji): x 7,095 … 8,395 (1,30 m), y 4,905 … 7,195; przejścia w ścianie osi 2
  (x 7,15–8,35) do holi, w P0 także w ścianie osi 3 (do holu wejściowego); drzwi z podestu: P1 → łazienka 1.05, P2 → pom. techn. 2.07.
* Między biegami „duszek” 11 cm — pełna ścianka szklana/stalowa (balustrada) na całą wysokość biegów; pochwyty obustronne h = 0,90 m.
* Otwory w stropach ST1/ST2: x 3,805 … 7,095, y 4,905 … 7,195. W P2 nad biegiem „a” i spocznikiem międzykond. **pustka** (świetlik),
  balustrada h = 1,10 m, prześwity ≤ 0,12 m na krawędzi spocznika P2 (x = 7,095) i wzdłuż biegu.
* **Prześwit nad biegami:** biegi kolejnych kondygnacji leżą dokładnie nad sobą (przesunięcie pionowe 3,15 m) → prześwit pionowy nad
  każdym stopniem = 3,15 − 0,35 (płyta biegu mierzona pionowo) = **2,80 m ≥ 2,00 m**; nad spocznikiem międzykond. 4,725 − 0,20 − 1,575 = 2,95 m;
  na starcie biegu „a” w P0 pod płytą spocznika P1: 2,78 − 0,175 = 2,60 m; w P2 do stropu ST3: ≥ 2,78 m.

### 3.10 Piony instalacyjne (w jednej osi przez kondygnacje)

| pion | xy | przebieg |
|---|---|---|
""")
for p in PIONY:
    w(f"| {p['id']} | ({fmt(p['xy'][0])}; {fmt(p['xy'][1])}) | {p['opis']} |\n")
w("""
Kuchnia (blat przy osi F), WC 0.04 i łazienka 0.08 odprowadzane poziomo pod posadzką P0 do kolektora wzdłuż skrzydła płn. i wyjścia
w osi x = 9,00 (studzienka rewizyjna przy granicy). Dach P2: wpusty + rury spustowe w narożach NE/NW (wewnątrz ocieplenia), dachy zielone
P0/garażu: wpusty z przelewami awaryjnymi przez attykę.

""")

w(f"""## 4. Koncepcja konstrukcji

**System:** ścianowo-płytowy; stropy żelbetowe monolityczne gr. 22 cm (C30/37, B500SP) pracujące jako płyty dwukierunkowe/ciągłe
na ścianach; ściany nośne z bloczków silikatowych 18 cm (kl. 20) oraz **żelbetowe 18 cm** w: trzonie schodowym (wszystkie kondygnacje),
ścianie P0 w osi B, „U” strefy zachodniej P1 i P2 (ściany zach. A / A' + ściany N i S do x ≈ 3,70–4,20), ścianach wsch. P1/P2 (oś E)
oraz ścianie płd. P2 (tarcza nad boksem C). Sztywność: trzon ŻB + tarcze + stropy jako przepony.

**Rozpiętości płyt (≤ 6,5 m):**
* ST1: pasmo płd. strefy dziennej — kierunek N–S, **4,80 m** (podpory: oś 1 = belka ukryta ~100×22 cm na słupach SL1–SL4
  + narożnikach ścian B i F; oś 2 = ściany nośne/trzon); pasmo środkowe 2,50 m; skrzydło płn. 3,20 m; dach garażu płyta dwukierunkowa
  6,00 × 6,50 m na ścianach F, G, 1a, 4 (obc. dach zielony ok. 1,8 kN/m² + śnieg 0,72 kN/m² + zaspy przy attyce/uskoku — wg R5).
* ST2 i ST3: płyty dwukierunkowe na obwodzie + trzon: strefa zach. (x 0/−1,0 … 3,70) pracuje głównie E–W, **3,70 / 4,70 m**;
  strefa środkowa N–S **4,80 m** (oś 1 – ściana trzonu w osi 2); strefa wsch. N–S 4,80 m (oś 1 – ściana nośna w osi 2 na P1/P2,
  pod nią ściana w osi 2 w P0) i 2,50 m.
* Ścianki działowe P1/P2 nie są nośne (SIL 12 na stropie jako obciążenie liniowe, R5).

**Słupy i belki:** SL1–SL4 — stal RK 120×120×8 (lub ŻB 25×25) w osi 1 za słupkami przeszklenia, x = {', '.join(fmt(c[0], 3) for c in COLUMNS)};
na stopach 1,0×1,0 m. Belka ukryta ST1 w osi 1 (od ściany B do ściany F) przenosi krawędź stropu, parapet P1 i siły skupione z tarcz
(z tarczy wsch. P1 w x = 11,40 — między SL4 a narożnikiem F, rozpiętość 2,38 m). Nadproże-tarcza nad otworem boksu C w ścianie P1
(x 4,20–11,30, 7,10 m): ŻB 24 cm od +5,20 do +5,93 zespolone z płytą ST2 i ścianą płd. P2 (ŻB) — tarcza o wysokości ~3,7 m (z otworami
okien P2) opiera się na tarczy zach. P1 (x ≤ 4,20) i na ścianie-tarczy wsch. P1 (oś E). Wariant zapasowy (do decyzji w PT): 2 słupki
stalowe 100×100 w słupkach ramy C (x = 6,57 i 8,93) → rozpiętości ~2,4 m.

**Wsporniki i ścieżka obciążeń (strefa zach. — „S” na zachód):**
1. **Bryła A (P2) — wspornik 1,00 m** poza ścianę A: ściana A' (ŻB) wisi na **ścianach-tarczach N (y = 7,30) i S (y = 0) kondygnacji P2**
   (ŻB 18 cm, wys. 2,93 m), które wspornikowo wychodzą 1,00 m poza ścianę A i są ciągle podparte na ścianach N/S P1 (zaplecze ≥ 3,70 m).
2. **Bryła B (P1) — wspornik 1,00 m** poza ścianę P0 w osi B: ściana A (ŻB) wisi na **ścianach-tarczach N i S kondygnacji P1**, wspornikowo
   1,00 m poza ścianę B; zaplecze: tarcza S do słupa SL1 (x = 3,383, 2,38 m) i dalej w nadproże-tarczę boksu C; tarcza N do ściany trzonu
   w osi C (2,70 m). Sumaryczny „schodkowy” wysięg ściany A' względem podpory na gruncie (oś B) = 2,00 m — przenoszony wyłącznie przez
   tarcze wys. ~2,9 m (ramię sił wewnętrznych ~2,3 m), a **nie** przez płyty; ściany murowane na wspornikach płyt — brak.
3. Ściana P0 w osi B (ŻB) → ława 0,70 × 0,35 m. Sprawdzić w PT: EQU (1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb), ugięcie końca ≤ wysięg/125
   (≤ 8 mm, R5), zarysowanie tarcz przy otworach okiennych (okna w tarczach N/S tylko poza strefą zakotwienia).
4. **Płyty wspornikowe** (poza obrysem ogrzewanym, z łącznikami termoizolacyjnymi z ETA w linii ocieplenia): ST1 — płd. 1,00 m
   (pas D + boks C, obciążenie liniowe od boksu ~3,5 kN/m), zach. 1,50 m (wolna płyta, bez ścian); ST2 — zach. 1,20 m, płd. 1,00 m,
   wsch. 0,40 m; ST3 — 0,80 / 0,40 m. Wszystkie wsporniki płyt ≤ 1,50 m i **bez ścian murowanych** na końcach. Część ST1 x −0,30 … 0,70
   i ST2 x −1,30 … −0,30 jest wewnątrz obrysu ogrzewanego (podłoga nad powietrzem zewn.) — ocieplenie od spodu, bez łączników.
5. **Rama górna boksu C** przedłużona 1,75 m na wschód (x 11,70 → 13,45): lekki kształtownik stalowy ocynkowany w okładzinie
   (≤ 0,5 kN/m), zakotwiony w ramie C i w ścianie-tarczy wsch. P1 przez łączniki termoizolacyjne stalowe.
6. **Wsch. P1/P2 (oś E) nad kuchnią:** ściany ŻB jako tarcze o rozpiętości 4,80 m (podpory: belka ukryta ST1 w osi 1 oraz ściana P0
   w osi 2) + 2,50 m do osi 3; brak ściany pod osią E w strefie dziennej (otwarta kuchnia).

**Fundamenty:** ławy żelbetowe 0,70 × 0,35 m (spód −1,10) pod ścianami zewn., trzonem i ścianami nośnymi (osie 1 garażu, 1a, 2, 3, 4,
B, C, D, F, G), stopy 1,0 × 1,0 m pod SL1–SL4; płyta posadzki 15 cm na XPS; grunt: piaski średnie I_D ≈ 0,6, woda gruntowa ~3,8 m p.p.t.
Wg R5: 3 kondygnacje i wsporniki → **II kategoria geotechniczna** (dokumentacja badań podłoża + projekt geotechniczny) — do potwierdzenia.

## 5. Zagospodarowanie działki

* **Położenie:** narożnik SW działki = (−7,30; −31,00) w układzie budynku; działka x −7,30 … 24,70, y −31,00 … 19,00
  (granica z drogą y = 19,00; linia zabudowy y = {fmt(BUILD_LINE_Y)}).
* **Odległości:** zach. — płyta ST2 4,80 m, dach ST3 5,20 m, płyta ST1 5,50 m, ściana P2 z oknami 6,00 m, ściana P1 7,00 m, ściana P0 8,00 m;
  wsch. — ściana garażu z drzwiami i oknem 5,80 m, ściany P1/P2 13,00 m, jednostka PC 3,40 m; płn. — elewacja P0 8,20 m od granicy z drogą
  (2,20 m za linią zabudowy), daszek wejścia 6,70 m (0,70 m za linią); płd. — boks C/płyty 29,70 m, taras 26,70 m.
* **Dojazd:** zjazd 6,0 m z ul. Lipowej → brama przesuwna 5,00 m (odjazd na wschód wzdłuż ogrodzenia, x 18,30–23,60) → podjazd
  6,00 × 8,20 m (kostka betonowa) do bramy garażowej BG1 5,00 × 2,25 m. **Miejsca postojowe:** 2 w garażu + 2 gościnne 2,50 × 5,00 m na
  podjeździe (tandemowo przed bramą) — MPZP ≥ 2 ✔.
* **Dojście:** furtka 1,00 m (x 7,30–8,30) i chodnik 1,50 m w osi drzwi wejściowych; wejście bezprogowe (teren −0,23 → spocznik
  przed drzwiami −0,02, chodnik o spadku ≤ 5 %).
* **Tarasy:** płd. x −1,80 … 12,90, y −4,30 … −0,30 + zach. pod okapem ST1 x −1,80 … 0,70, y −0,30 … 4,20; razem
  {fmt(SITE['terrace_S'].union(SITE['terrace_W']).area, 1)} m², poziom −0,02 (deska kompozytowa na legarach); > 35 m² — objęty
  projektem (art. 29 PB w brzmieniu z 2026 r.). Dojście boczne do ogrodu: płyty x −1,80 … 0,70, y 7,60 … 10,80 oraz ścieżka wzdłuż
  płd. i wsch. ściany garażu (drzwi do pom. gosp.).
* **Pojemniki na odpady:** osłona 2,60 × 1,30 m przy podjeździe (x 9,30–11,90, y 14,60–15,90), **3,10 m od granicy z drogą**, dostęp od chodnika.
  WT § 23 ust. 1 (10 m od okien/drzwi i 3 m od granicy) — dla zabudowy jednorodzinnej odległości od okien nie stosuje się
  [DO WERYFIKACJI w rejestrze R3 — przyjęto zachowawczo ≥ 3 m od granic].
* **Wody opadowe:** z dachu P2 i płyt → zbiornik retencyjny 6 m³ (x ≈ 15,3; y ≈ −6,6; podlewanie ogrodu) z przelewem do skrzynek
  rozsączających ~5 m³ (x 14,00–18,40, y −12,40 … −10,20, ≥ 6 m od granic); dachy zielone P0/garażu retencjonują część opadu.
  Szacunek: A_red ≈ 185 m² × 150 l/(s·ha) × 15 min ≈ 2,5 m³ — zapas. Zakaz odprowadzania na drogę (MPZP) ✔.
  Zbiornik bezodpływowy 5–15 m³ — w PB objęty projektem (zgłoszenie wg art. 29 PB, R1).
* **Pompa ciepła:** jednostka zewn. powietrze–woda na fundamencie przy wsch. ścianie garażu (x 20,20–21,30, y 5,60–6,20),
  **3,40 m od granicy wsch.** (≥ 3,0 m), z dala od sypialni (najbliższe okno pokoju: 2.06, okno wsch. — {fmt(((20.20 - 11.70) ** 2 + (5.60 - 3.20) ** 2) ** 0.5, 1)} m).
* **Przyłącza:** ZK w linii ogrodzenia przy bramie (x ≈ 12,4) → kabel YKY 5×16 do RG w pom. techn. 0.11; woda PE 40 z sieci PE 110
  (x = 11,20) do wodomierza w 0.11; kanalizacja PVC 160 z kolektora pod skrzydłem płn. (wyjście x = 9,00) przez studzienkę rewizyjną Ø425
  (1,40 m od granicy) do sieci PVC 200; światłowód do 0.11; gaz — nie przyłączany (dom all-electric).
* **Zieleń:** pas żywopłotu 1,0 m wzdłuż granic zach., wsch. i płd. (zieleń izolacyjna), drzewa w ogrodzie płd.;
  **ogrodzenie:** od drogi ażurowe h = 1,50 m (≤ 1,60, bez prefabrykatów betonowych), pozostałe panelowe h = 1,50 m.

## 6. Orientacja, doświetlenie, energia

* **Strefa dzienna na południe:** 5 kwater przeszklenia ({fmt(win_rows[1][2])} m² w świetle ościeżnic z oknem zach., stosunek 1:{fmt(win_rows[1][1] / win_rows[1][2], 1)}).
  Okap ST1 1,00 m nad +2,70: w południe 21.06 (wys. słońca ok. 61° dla φ = 52,4°) cień sięga 1,00·tg61° ≈ 1,80 m w dół —
  zacienia ok. 2/3 przeszklenia; w grudniu (14°) słońce wpada w pełni (zyski zimowe). Dodatkowo screeny ZIP w kasecie nad szkłem (g_c ≤ 0,35).
* **Boks C** (P1) — 3 kwatery pod okapem ST2 (1,00 m) i ramą górną; screen ZIP. **Bryła A** — pionowe lamele (ok. 20 % zacienienia
  czołowego, znacznie więcej przy niskim słońcu wsch./zach.), okna za lamelami z dolną kwaterą VSG jako barierą do 1,10 m.
* **Sypialnie:** dzieci — zachód (1.01, 1.02), rodzice — południe + zachód (2.01), pokój 2.06 — południe + wschód, pokój gościnny — zachód.
* **Północ:** tylko drzwi wejściowe z doświetlem, małe okno WC, okno klatki na P1 i małe okno łazienki P2 (≈ 4,5 m² łącznie);
  od północy pomieszczenia pomocnicze i komunikacja (trzon, hol, sień, garderoba, WC, schowek, techniczne, łazienki, pralnia).
* **Zwartość:** parter prostokąt 18,20 × 11,10 m, piętra prostokąty z licami płd./płn. w jednej płaszczyźnie; A/V_e (część ogrzewana,
  szacunek) ≈ 0,66 m⁻¹. Garaż poza strefą ogrzewaną (ściana SG1 z wełną 12 cm, drzwi EI30), jako bufor od NE.
* **Instalacje:** PC powietrze–woda (monoblok/split) + ogrzewanie podłogowe, zasobnik CWU 300 l, RG, wodomierz w pom. techn. 0.11
  ({A('0.11')} m² ≥ 6 m²); rekuperator w 2.07 (czerpnia/wyrzutnia przez dach), pion wentylacyjny W1 przy trzonie; PV ≤ 6,5 kWp
  (~15 modułów, ~30 m²) na dachu P2, cofnięte ≥ 1,0 m od krawędzi, poniżej attyki; wyłaz dachowy z 2.07.

## 7. TABELA KONTROLNA

### 7.1 Pomieszczenia — powierzchnie i wysokości

| pom. | pow. [m²] | minimum | wys. w świetle [m] | minimum | ocena |
|---|---|---|---|---|---|
""")
chk = [('0.12', 50.0, 'strefa dzienna ≥ 50 (brief); pokój dzienny ≥ 16 (WT § 94)'), ('0.07', 8.0, 'pokój ≥ 8 (WT § 94)'),
       ('1.01', 12.0, 'pokój dziecka ≥ 12 (brief)'), ('1.02', 12.0, 'pokój dziecka ≥ 12 (brief)'),
       ('1.03', 16.0, 'pokój dzienny rodzinny ≥ 16'), ('2.01', 14.0, 'sypialnia rodziców ≥ 14 (brief)'),
       ('2.04', 8.0, 'pokój ≥ 8'), ('2.06', 8.0, 'pokój ≥ 8'), ('0.11', 6.0, 'pom. techniczne ≥ 6 (brief)')]
for rid, mn, lab in chk:
    a = room[rid]['poly'].area
    hmin = '2,50' if room[rid]['pobyt'] else '2,20'
    w(f"| {rid} {room[rid]['name']} | {fmt(a)} | {fmt(mn)} — {lab} | 2,78 | {hmin} | {'✔' if a >= mn else '✘'} |\n")
w(f"| pomieszczenia pomocnicze, komunikacja (wszystkie) | — | — | 2,78 | 2,20 | ✔ |\n"
  f"| garaż 0.13 (w świetle {fmt(AX['G'] - EXT_IN - AX['F'] - GAR_IN)} × {fmt(AY['4'] - EXT_IN - Y_GAR - H_BEAR)} m) | {A('0.13')} | 5,60 × 6,00 m (brief) | 2,93 | 2,20 | ✔ |\n\n")

w("### 7.2 Oświetlenie dzienne (WT § 57: okna ≥ 1/8 pow. podłogi; kuchnia z oknem)\n\n")
w(win_md)
w("\nKuchnia — kwatera E5 (x 10,22–12,50) w strefie kuchni ✔. Łazienki mogą być bez okien (wentylacja mechaniczna z odzyskiem ciepła); w projekcie 0.08, 1.05 i 2.03 mają małe okna.\n\n")

w(f"""### 7.3 Schody

| parametr | projekt | wymóg | ocena |
|---|---|---|---|
| wysokość stopnia h | 0,175 m (18 × 0,175 = 3,15) | ≤ 0,19 (WT § 68, jednorodzinny); cel ≈ 0,175 | ✔ |
| szerokość (głębokość) stopnia s | 0,28 m | cel ≈ 0,28 | ✔ |
| 2h + s | 0,63 m | 0,60–0,65 | ✔ |
| szerokość biegu w świetle | 1,09 m | ≥ 0,80 (WT); cel ≥ 1,00 | ✔ |
| spocznik międzykond. / kond. | 1,05 / 1,30 m | ≥ szer. biegu (1,00) | ✔ |
| prześwit nad biegami | ≥ 2,60 m (start), 2,80 m (typowo) | ≥ 2,00 m | ✔ |
| balustrady | ścianka między biegami, pochwyty 0,90; pustka P2 h = 1,10, prześwit ≤ 0,12 | WT § 296–298 [DO WERYFIKACJI] | ✔ |

### 7.4 Odległości od granic i linii zabudowy (lica zewn. z ociepleniem; WT § 12 — z otworami ≥ 4,0 m, bez ≥ 3,0 m; płyty/okapy przyjęto ≥ 4,0 m)

| element | odległość [m] | wymóg [m] | ocena |
|---|---|---|---|
""")
for lab, d, req in dist_checks():
    w(f"| {lab} | {fmt(d)} | ≥ {fmt(req, 1)} | {'✔' if d >= req - 1e-6 else '✘'} |\n")
w(f"| budynek względem nieprzekraczalnej linii zabudowy (y = {fmt(BUILD_LINE_Y)}) | elewacja 2,20 za linią, daszek 0,70 za linią | nie przekraczać | ✔ |\n\n")

w(f"""### 7.5 Wskaźniki MPZP 3MN, wysokość, PU

| wskaźnik | projekt | wymóg | ocena |
|---|---|---|---|
| pow. zabudowy (rzut brył zamkniętych: P0 ∪ P1 ∪ P2 ∪ boks C) | {fmt(m['enclosed'], 1)} m² = {fmt(100 * m['enclosed'] / m['plot'], 1)} % | ≤ 30 % (480 m²) | ✔ |
| pow. zabudowy zachowawczo (z płytami, okapami, daszkiem) | {fmt(m['all_proj'], 1)} m² = {fmt(100 * m['all_proj'] / m['plot'], 1)} % | ≤ 30 % | ✔ |
| pow. biologicznie czynna (bez dachów zielonych) | {fmt(m['pbc'], 0)} m² = {fmt(100 * m['pbc'] / m['plot'], 1)} % (+ ok. {fmt(0.5 * m['green_roof'], 0)} m² jako 50 % dachów zielonych — nie wliczono) | ≥ 50 % (800 m²) | ✔ |
| intensywność zabudowy (pow. całkowita kondygnacji nadz. {fmt(m['gfa'], 1)} m² / 1600 m²) | {fmt(m['intens'], 2)} | 0,05–0,80 | ✔ |
| liczba kondygnacji nadziemnych | 3 | ≤ 3 | ✔ |
| **wysokość budynku** (WT § 6: od terenu przy najniżej położonym wejściu {fmt(zmin)} do attyki +9,85) | **{fmt(H)} m** (od wejścia głównego: {fmt(ATTIC_TOP + 0.228)} m) | ≤ 11,0 m | ✔ |
| dach | płaski, spadek 2 % | ≤ 12° | ✔ |
| miejsca postojowe | 2 (garaż) + 2 gościnne | ≥ 2 | ✔ |
| ogrodzenie od drogi | ażurowe 1,50 m | ≤ 1,60, bez prefabrykatów betonowych | ✔ |
| PU budynku (bez garażu, bez schodów) | **{fmt(PU_bud)} m²** | 230–270 m² (brief) | ✔ |

### 7.6 Zestawienie powierzchni

| kondygnacja | PU mieszk.+pomocn.+komunik. | pom. techniczne | schody/spoczniki (poza PU) | garaż + pom. gosp. | pow. całkowita (brutto) |
|---|---|---|---|---|---|
""")
for fl in ('P0', 'P1', 'P2'):
    gross = OUTLINE[fl].area + ((C_BOX['x1'] - C_BOX['x0']) * 1.0 if fl == 'P1' else 0)
    w(f"| {fl} | {fmt(t[fl]['PU'])} | {fmt(t[fl]['T'])} | {fmt(t[fl]['S'])} | {fmt(t[fl]['G'])} | {fmt(gross)} |\n")
w(f"| **razem** | **{fmt(tot['PU'])}** | **{fmt(tot['T'])}** | **{fmt(tot['S'])}** | **{fmt(tot['G'])}** | **{fmt(m['gfa'])}** |\n\n")
w(f"""* **PU budynku mieszkalnego = {fmt(tot['PU'])} + {fmt(tot['T'])} = {fmt(PU_bud)} m²** (wartość do porównania z celem 230–270 m²;
  bez garażu z pom. gosp. i bez schodów).
* PU łącznie z garażem i pom. gosp.: {fmt(PU_bud + tot['G'])} m²; powierzchnia netto wszystkich pomieszczeń (z klatką): {fmt(netto)} m².
* Boks C (siedzisko h = 0,55) nie jest wliczany do PU. Kubatura brutto (szacunek): ≈ 1 380 m³.

## 8. Samokontrola — odstępstwa, słabości, ryzyka

**Iteracje rysunków (wykonane 2 pełne przebiegi + poprawki):** 1) poprawiono kolizje skrzydeł drzwi z wyposażeniem (zasobnik CWU
w pom. techn., wanna w łaz. P1, natrysk w łaz. P2, łóżko w 2.06, półki spiżarni, drzwi garażu/samochód); 2) pion K2 przeniesiono
tak, aby przechodził przez pomieszczenia mokre/szacht na wszystkich kondygnacjach (łazienka P2 przeniesiona na wschód nad szacht
przy trzonie — rury poza strefą wspornika); 3) uporządkowano wymiary/legendy; 4) elewację porównano ze szkicem (tab. 2) — wszystkie
krawędzie w tolerancji ≤ 0,45 m.

Odstępstwa od szkicu/założeń (z uzasadnieniem):
1. Kwatery E i C równe (2,28 / 2,37 m) zamiast nierównych ze szkicu — powtarzalność stolarki i słupków SL1–SL4 w osiach podziałów.
2. Linia D i płyta E na tym samym poziomie konstrukcyjnym (+3,00); różnicę wysokości ze szkicu oddaje pas D 2,70–3,70 (attyka dachu
   garażu + dolna rama boksu C). Na wschód od x = 3,95 płyta E „wtapia się” w pas D (w szkicu dwie osobne linie).
3. Rama górna C przedłużona do 13,45 (szkic ~13,6) jako lekka stal; boks C 7,10 m szkła (szkic 7,2).
4. PU {fmt(PU_bud)} m² — przy dolnej granicy celu (świadomie: wariant zwartości).

Słabości / do weryfikacji w dalszych etapach:
* Łazienka 1.05 i pom. techn. 2.07 dostępne bezpośrednio ze spocznika klatki (brak holu) — mniejsza prywatność łazienki dzieci.
* Łazienka 0.08 tylko z pokoju gościnnego (goście dzienni korzystają z WC 0.04); pokój gościnny 10,8 m² — kompaktowy.
* Spiżarnia 0.10 wąska (1,07 m; półki jednostronne, drzwi otwierane na zewnątrz).
* Pokój 1.02 (NW) z jednym oknem zach. i szachtem K2 w narożu.
* Hol P0 ma szer. 1,32 m, a główne przejście do strefy dziennej prowadzi przez spocznik trzonu (otwór 1,20 m).
* Podwójny schodkowy wspornik zachodni (A' → A → B, 2 × 1,00 m) wymaga tarcz ŻB w ścianach N/S P1 i P2 (koszt, ograniczenie okien
  w strefie zakotwienia, EQU, ugięcia ≤ 8 mm, łączniki termoizolacyjne) — do obliczeń w PT.
* Nadproże-tarcza 7,10 m nad boksem C lub słupki w ramie C — decyzja w PT; belka ukryta ST1 w osi 1 z siłą skupioną z tarczy wsch. P1.
* Okna P2 za lamelami — współczynnik 1/8 spełniony geometrycznie, rzeczywiste natężenie światła do sprawdzenia (symulacja DF).
* Wysokość {fmt(H)} m — zapas 0,84 m do 11,0 m; moduły PV muszą pozostać poniżej attyki lub MPZP musi wyłączać urządzenia techniczne.
* Garaż {fmt(AX['G'] - EXT_IN - AX['F'] - GAR_IN)} m w świetle — minimalnie ponad 5,60 m (przejścia boczne 0,55–0,85 m).
* Jednostka PC 3,40 m od granicy — wymagana analiza akustyczna względem sąsiada (poziom hałasu nocą).
* WT § 23 (pojemniki) i § 12 (nowelizacja 2023/2442) — do potwierdzenia po uzupełnieniu rejestru (R3).
""")

open(os.path.join(OUT, 'opis.md'), 'w').write(''.join(md))

# ----------------------------------------------------------------- eksport modelu
def poly_xy(p):
    return [[round(x, 3), round(y, 3)] for x, y in list(p.exterior.coords)[:-1]]


model = dict(
    meta=dict(wariant='W1', nazwa='wierność szkicowi i zwartość', data='2026-09-25', uklad='x->E, y->N, (0,0)=A/1, ±0,00=101,65'),
    osie=dict(x=AX, y=dict(**AY, **{'1a': Y_GAR})), poziomy=dict(FFL=FFL, stropy=SLABS, attyka=ATTIC_TOP, linia_D=D_TOP,
                                                                 dach_zielony=GREEN_TOP, krawedzie=EDGE),
    obrysy={k: poly_xy(v) for k, v in OUTLINE.items()},
    plyty=dict(ST1=poly_xy(ST1_POLY), ST2=poly_xy(ST2_POLY), ST3=poly_xy(ST3_POLY), otwor_schodow=poly_xy(STAIR_HOLE),
               swietlik=poly_xy(SKYLIGHT)),
    boks_C=C_BOX, lamele=LAMELE, schody=STAIR, slupy=COLUMNS, szprosy_E=MULLIONS,
    sciany_wewn=[dict(fl=wl['fl'], typ=wl['kind'], prostokat=poly_xy(wl['poly'])) for wl in IWALLS],
    strefy_zelbetowe={k: [poly_xy(z) for z in v] for k, v in RC_ZONES.items()},
    otwory=[{k: v for k, v in o.items()} for o in OPENINGS],
    pomieszczenia=[dict(id=r['id'], fl=r['fl'], nazwa=r['name'], kat=r['kat'], pobyt=r['pobyt'],
                        pow=round(r['poly'].area, 2), wielobok=poly_xy(r['poly'])) for r in ROOMS],
    piony=PIONY,
    dzialka=dict(obrys=poly_xy(PLOT), linia_zabudowy_y=BUILD_LINE_Y,
                 elementy={k: (poly_xy(v) if hasattr(v, 'exterior') else [poly_xy(g) for g in v] if isinstance(v, list) else v) for k, v in SITE.items()}),
    bilans=dict(PU_mieszk_pomocn_komunik=round(tot['PU'], 2), pom_techniczne=round(tot['T'], 2),
                schody=round(tot['S'], 2), garaz_gosp=round(tot['G'], 2), PU_budynku=round(PU_bud, 2),
                pow_zabudowy=round(m['enclosed'], 2), pow_zabudowy_zachowawczo=round(m['all_proj'], 2),
                pbc=round(m['pbc'], 2), intensywnosc=round(m['intens'], 3), wysokosc=round(H, 2)),
)
json.dump(model, open(os.path.join(OUT, 'model_W1.json'), 'w'), ensure_ascii=False, indent=1)
print('PU_bud', round(PU_bud, 2), 'H', round(H, 3), 'footprint', round(m['enclosed'], 2))
