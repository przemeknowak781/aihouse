# Koncepcja — WARIANT W3: „ŚWIATŁO · OGRÓD · SEKWENCJA WEJŚCIA”

Dom LAMELA, dz. nr 123/4 (32,00 × 50,00 m), MPZP 3MN. Wersja robocza 2026-09-25. Interpretacja szkicu **v2** (decyzje Inwestora z 25.09.2026, brief §1.2).
Wszystkie liczby w tym opisie, na rzutach i w tabelach pochodzą z modelu `src/model_w3.py` (geometria: `src/base_w3.py`, `src/geo_p0.py`,
`src/geo_p1.py`, `src/geo_p2.py`, `src/geo_ext.py`). Tabele z §3–§4 i §8 wygenerowano skryptem `src/calc_w3.py`. Rysunki odtwarza się poleceniem
`cd src && python3 draw_plans.py .. && python3 draw_elev.py .. && python3 draw_sections.py .. && python3 draw_site.py ..`.

| Rysunek | Plik |
|---|---|
| Rzut parteru P0 | `rzut_P0.png` |
| Rzut I piętra P1 | `rzut_P1.png` |
| Rzut II piętra P2 | `rzut_P2.png` |
| Elewacja południowa + porównanie ze szkicem | `elewacja_S.png` |
| Przekroje A-A (oś widoku) i B-B (klatka schodowa) | `przekroj.png` |
| Zagospodarowanie działki | `zagospodarowanie.png` |

**Parametry wariantu (z modelu):** PU **262,61 m²** (P0 122,18 + P1 81,35 + P2 59,08; bez garażu 38,21 m²), powierzchnia zabudowy
**200,18 m²** (12,5 %), wysokość budynku wg MPZP **10,10 m**, 3 kondygnacje nadziemne, bez piwnicy, dachy płaskie.

---

## 1. Idea wariantu W3

Priorytet: **światło, ogród i sekwencja wejścia**. Dom jest ułożony wzdłuż jednej, prostej **osi widoku x = 8,00 m** poprowadzonej z północy na
południe przez całą działkę:

> furtka w ogrodzeniu → dojście z płyt (1,20 m) → daszek nad wejściem → drzwi wejściowe (1,10 × 2,40) → **wiatrołap** doświetlony
> świetlikiem SW2 w zielonym dachu skrzydła → **szklana przegroda** z drzwiami szklanymi → **hol** (3,10 × 3,37 m, obok schody za ekranem
> z drewnianych lamel) → wylot 2,60 m w ścianie grzbietowej → **jadalnia pod dwukondygnacyjną pustką** (h = 5,70–5,95 m, doświetlona przez
> boks C) → **drzwi HS w kwaterze 4** fasady → taras → **oś ogrodowa** z płyt w trawie → soliter (drzewo) na końcu osi (y ≈ −24,5 m).

Z progu drzwi wejściowych widać przez cały dom ogród i zamknięcie osi — sekwencja „ściśnięcie → rozprężenie”: niski (2,80 m), jasny od góry
wiatrołap i hol, a potem wysoka, rozświetlona jadalnia i ogród.

Pozostałe cechy wariantu:
* **Światło z trzech stron w strefie dziennej**: salon — przeszklenie S (kwatery 1–2) i przeszklenie zachodnie z HS na taras zachodni pod
  okapem 1,50 m (wieczorne słońce); jadalnia — S + światło z góry przez pustkę i boks C; kuchnia — S (kwatera 5) + drzwi przeszklone na
  **patio poranne** od wschodu (słońce przy śniadaniu).
* **Garaż cofnięty o 4,80 m** względem lica ogrodowego — między kuchnią a garażem powstaje osłonięte od północy **patio poranne** (5,10 × 4,80 m),
  a linia D (dolna płyta ramy C → attyka garażu) nadal czytelnie przebiega w elewacji do narożnika garażu 19,00 m od lica zach. bryły B.
* **Latarnia świetlna nad klatką schodową** (SW1, 1,85 × 2,90 m, w poziomie attyki) — światło zenitalne spada przez rdzeń 3 kondygnacji;
  klatka jest otwarta na hol parteru przez ekran z lamel, na galerię P1 i hol P2.
* **Loggia P2 za lamelami** — pokoje II piętra cofnięte do osi 1' (y = 1,20); ekran pionowych lamel w licu bryły A (jak w szkicu) jest
  jednocześnie osłoną przeciwsłoneczną i balustradą loggii 13,0 × 1,20 m (taras rodziców z widokiem na ogród, dostęp z gabinetu, holu i sypialni).
* **Galeria P1 nad pustką** — pokój rodzinny/biblioteka w boksie C jest otwarty na galerię i pustkę; dzieci i rodzina mają wizualny kontakt z
  jadalnią i ogrodem.
* Pomieszczenia pomocnicze i komunikacja od północy (skrzydło wejściowe z zielonym dachem, pom. techniczne, przedsionek gospodarczy,
  pralnia, łazienki), sypialnie od W (dzieci), S+E (rodzice) i W+S (gabinet/pokój).

## 2. Odczyt szkicu w W3 (porównanie ilościowe)

Skala szkicu wg briefu §1.1: bryła B (500…1050 px) = 12,0 m ⇒ 45,8 px/m; odniesienie = lico zach. bryły B (x = −0,30).

| Element szkicu | szkic (od lica zach. B) | W3 (od lica zach. B) | W3 — współrzędne x [m] | uwagi |
|---|---|---|---|---|
| A — bryła II piętra w lamelach | −1,0 … +12,2 (13,2 m) | −1,0 … +12,6 (13,6 m) | −1,30 … 12,30 | wspornik 1,00 m na zachód |
| A — płyta pod/nad bryłą | −2,4 … +12,6 | −1,9 … +12,9 | −2,20 … 12,60 | wysunięcie 0,90 m (S i W) |
| B — bryła I piętra | 0 … +12,0 | 0 … +12,6 | −0,30 … 12,30 | pełna, lewa część bez okien od S |
| C — boks przeszklony, 3 kwatery | +4,5 … +11,7 (7,2 m) | +4,8 … +12,0 (7,2 m) | 4,50 … 11,70 | kwatery 3 × 2,40 m |
| C — rama | +3,9 … +13,8 | +3,9 … +13,2 | 3,60 … 12,90 | wysunięcie 1,00 m |
| D — linia pozioma do narożnika | +3,8 … +19,0 | +3,9 … +19,0 | 3,60 … 18,70 | dolna płyta ramy C (+3,65) = attyka garażu (+3,65) |
| D — pion (narożnik garażu) | +19,0 | +19,0 | 18,70 | ściana wsch. garażu |
| E — przeszklenie parteru, 5 kwater | +1,0 … +13,2 | +1,3 … +12,15 | 1,00 … 11,85 | szer. kwater 1,60/1,90/2,40/2,40/2,55 — narastające ku wschodowi jak w szkicu |
| E — płyta dachu parteru | −1,5 … +14,1 | −1,5 … +14,1 | −1,80 … 13,80 | okap 1,50 m W, 1,00 m S, nad patio 1,50 m |
| G — garaż | +13,2 … +19,0 | +12,6 … +19,0 | 12,30 … 18,70 | 2 stanowiska, cofnięty w głąb o 4,80 m |

Sylweta „S” (zachód–wschód–zachód) jest zachowana wyłącznie przesunięciami brył: A wysunięta na zachód (wspornik), B z boksem C
przesunięta na wschód (rama C wychodzi 0,60 m poza lico wsch. B), E przesunięta na zachód (okap 1,50 m), a garaż G zamyka linię D na wschodzie
(`elewacja_S.png` — górny panel: obrys W3 na szkicu). Odstępstwo świadome: garaż w W3 jest cofnięty w głąb działki (w elewacji to samo
położenie w osi x, inna głębokość planu) — w widoku od ogrodu czyta się jako tło dla patio; wysokości pasm wg WT, nie wg umownych proporcji szkicu.

---

## 3. Definicja wymiarowa

### 3.1 Układ współrzędnych i siatka osi

Układ budynku: x → wschód, y → północ, z → góra; początek (0; 0) = przecięcie osi **A** (zachodnia oś nośna bryły B) i osi **1** (południowa).
Osie = środek warstwy konstrukcyjnej (silikat 18 cm). Lica zewnętrzne ścian z ociepleniem leżą 0,30 m na zewnątrz osi.
Działka w tym układzie: x −7,30 … 24,70, y −31,00 … 19,00 (granica z drogą 1KDD na y = 19,00; linia zabudowy y = 13,00).

| Oś X | x [m] | znaczenie | Oś Y | y [m] | znaczenie |
|---|---|---|---|---|---|
| A' | −1,000 | ściana zach. P2 na wsporniku (lekka) | 1 | 0,000 | lico ogrodowe: fasada E (P0), ściana/boks C (P1), linia słupów loggii (P2) |
| A | 0,000 | ściana zach. P0/P1 | 1' | 1,200 | przeszklenia pokoi P2 (za loggią), uskok ST2/ST2L |
| B | 4,050 | pokój gościnny / klatka; kid 2 / klatka; nadbudowa | 2 | 4,800 | ściana pd. garażu (patio) |
| B' | 4,500 | krawędź zach. pustki, podciąg PD-2, słup SL2 | 3 | 5,400 | ściana grzbietowa (nośna P0–P2) |
| C | 6,400 | klatka / hol (P0: ekran lamel), klatka / łazienki (P1, P2) | 4 | 8,900 | ściana pn. P1, nadbudowy P2; P0: granica skrzydła wejściowego |
| D | 9,650 | hol / pom. techn.; łazienka / pralnia; nadbudowa | 5 | 11,300 | ściana pn. skrzydła wejściowego i garażu |
| E | 12,000 | ściana wsch. domu = ściana dom/garaż | | | |
| F | 18,400 | ściana wsch. garażu (pion D) | | | |

Rozstawy osi X: 4,05 / 0,45 / 1,90 / 3,25 / 2,35 / 6,40 m; osi Y: 1,20 / 3,60 / 0,60 / 3,50 / 2,40 m.
Linie podziałów fasady E (słupy SL1–SL4): x = 2,60 / 4,50 / 6,90 / 9,30; boksu C (słupki SLC1–SLC2): x = 6,90 / 9,30 (w jednej linii pionowej ze słupami
SL3/SL4 i słupami loggii SLA3/SLA4).

### 3.2 Poziomy i grubości (±0,000 = 101,65 m n.p.m.)

| Element | rzędna spodu | rzędna wierzchu | grubość / uwagi |
|---|---|---|---|
| Posadzka P0 (FFL) | — | ±0,000 | warstwy 0,15 m (ogrzewanie podłogowe) na płycie/podkładzie z XPS |
| Teren średni przy budynku | — | −0,25 (−0,33 … −0,17) | wejście: podest −0,02 / 1 stopień |
| ST1 — strop nad P0 | +2,800 | +3,000 | płyta 20 cm; h w świetle P0 = 2,80 m |
| Posadzka P1 (FFL) | — | +3,150 | warstwy 0,15 m |
| ST2 — strop nad P1 | +5,950 | +6,150 | płyta 20 cm; h w świetle P1 = 2,80 m |
| ST2L — płyta loggii (y ≤ 1,20) | +5,700 | +5,900 | obniżona o 0,25 m (taras nad pom. ogrzewanym); h P1 pod loggią 2,55 m |
| Posadzka P2 (FFL) / loggia | — | +6,300 / +6,28 | loggia: izolacja spadkowa + deska na wspornikach, odwodnienie liniowe |
| ST3 — stropodach P2 i nadbudowy | +9,100 | +9,320 | płyta 22 cm; h w świetle P2 = 2,80 m |
| Warstwy dachu P2 / attyka | — | +9,62 / **+9,85** | PIR spadkowy ≥ 2 %, membrana; latarnia SW1 bez wyniesienia ponad attykę |
| Stropodach skrzydła wejściowego | +2,800 | +3,000 | dach zielony do +3,30, attyka +3,40 |
| Stropodach garażu STG | +2,760 | +3,000 | płyta 24 cm (dach zielony), attyka **+3,65** = linia D |
| Rama C: płyta dolna / górna | +3,45 / +5,15 | +3,65 / +5,35 | wysunięcie 1,00 m, łączniki termoizolacyjne |
| Lamele bryły A | +5,90 | +9,10 | 40 × 80 mm co 12 cm, y = −0,40 |
| Pustka nad jadalnią | ±0,000 | +5,70 / +5,95 | h w świetle 5,70 (pod loggią) – 5,95 m |
| Spód ław | −1,10 | — | poniżej h_z = 0,80 m |

Wysokość kondygnacji 3,15 m = warstwy podłogi 0,15 + płyta 0,20 + 2,80 m w świetle.

### 3.3 Typy przegród pionowych

| Typ | Opis | grubość [m] |
|---|---|---|
| SZ1 | ściana zewn. nośna: tynk 1,5 + silikat 18 + EPS grafit / wełna 20 + tynk 1 cm (U ≈ 0,15) | 0,405 |
| SZL | ściana zewn. lekka P2 (wspornik A', lico 1'): szkielet stal/drewno + wełna 20 + płyta | 0,405 |
| SW18 | ściana wewn. nośna: silikat 18 + 2 × tynk 1,5 | 0,21 |
| SWG | ściana nośna dom/garaż: tynk + silikat 18 + wełna 12 + tynk (U ≈ 0,28, szczelna na spaliny) | 0,325 |
| DZ12 | ścianka działowa: silikat 12 + 2 × tynk 1,5 | 0,15 |
| DZL | ścianka lekka GK 12,5 cm (na stropie nad otwartą strefą parteru, krawędź pustki) | 0,125 |
| SK | przegroda szklana w ramie stalowej (wiatrołap / hol) | 0,06 |
| LAM | ekran z pionowych lamel drewnianych 4 × 8 cm co 12 cm (klatka / hol) | 0,08 |

### 3.4 PARTER P0 (±0,000)

**Obrys zewnętrzny P0** (lica ocieplenia, wielobok): (−0,30; −0,30) → (12,30; −0,30) → (12,30; 4,50) → (18,70; 4,50) → (18,70; 11,60) → (−0,30; 11,60) → (−0,30; −0,30); pow. 195,38 m² (część mieszkalna 12,60 × 11,90 m + garaż 6,40 × 7,10 m). Skrzydło wejściowe (y 8,90–11,60) jest jednokondygnacyjne, z zielonym dachem i świetlikiem SW2.

**Ściany P0**

| id | typ | oś od | oś do | dł. osi [m] | grubość [m] | uwagi |
|---|---|---|---|---|---|---|
| S0-01 | SZ1 | (0,00; 0,00) | (12,00; 0,00) | 12,00 | 0,405 | fasada pd. strefy dziennej (E): 5 kwater na słupach stalowych SL1-SL4 + podciąg w ST1; filar narożny 0...1,0 m |
| S0-02 | SZ1 | (12,00; 0,00) | (12,00; 4,80) | 4,80 | 0,405 | ściana wsch. kuchni (drzwi na patio poranne) |
| S0-03 | SZ1 | (12,00; 4,80) | (18,40; 4,80) | 6,40 | 0,405 | ściana pd. garażu (od patio; pełna, zielona fasada) |
| S0-04 | SZ1 | (18,40; 4,80) | (18,40; 11,30) | 6,50 | 0,405 | ściana wsch. garażu = pion D |
| S0-05 | SZ1 | (18,40; 11,30) | (0,00; 11,30) | 18,40 | 0,405 | ściana pn. garażu i skrzydła wejściowego (brama, drzwi wejściowe) |
| S0-06 | SZ1 | (0,00; 11,30) | (0,00; 0,00) | 11,30 | 0,405 | ściana zach. (oś A) |
| S0-07 | SWG | (12,00; 4,80) | (12,00; 11,30) | 6,50 | 0,325 | oś E - dom/garaż (ocieplona od garażu, szczelna) |
| S0-08 | SW18 | (0,00; 5,40) | (12,00; 5,40) | 12,00 | 0,210 | ściana grzbietowa (oś 3) - otwory: stopa schodów, wylot holu |
| S0-09a | SW18 | (0,00; 8,90) | (6,40; 8,90) | 6,40 | 0,210 | oś 4 - pod ścianą pn. P1 |
| S0-09b | SK | (6,40; 8,90) | (9,65; 8,90) | 3,25 | 0,060 | oś 4 - przeszklona przegroda wiatrołap/hol (nad nią podciąg PD-4 w ST1) |
| S0-09c | SW18 | (9,65; 8,90) | (12,00; 8,90) | 2,35 | 0,210 | oś 4 - pom. techn./przedsionek |
| S0-10 | SW18 | (4,05; 5,40) | (4,05; 8,90) | 3,50 | 0,210 | oś B - pokój gościnny/klatka |
| S0-11 | SW18 | (9,65; 5,40) | (9,65; 11,30) | 5,90 | 0,210 | oś D - hol/pom. techn., wiatrołap/przedsionek |
| S0-12 | DZ12 | (2,55; 8,90) | (2,55; 11,30) | 2,40 | 0,150 | łazienka gościnna / przedpokój |
| S0-13 | DZ12 | (2,55; 9,90) | (3,95; 9,90) | 1,40 | 0,150 | WC gościnne |
| S0-14 | DZ12 | (3,95; 9,90) | (3,95; 11,30) | 1,40 | 0,150 | WC gościnne |
| S0-15 | DZ12 | (6,40; 8,90) | (6,40; 11,30) | 2,40 | 0,150 | przedpokój gościnny / wiatrołap |
| S0-16 | DZ12 | (10,60; 4,00) | (12,00; 4,00) | 1,40 | 0,150 | spiżarnia |
| S0-17 | DZ12 | (10,60; 4,00) | (10,60; 5,40) | 1,40 | 0,150 | spiżarnia |
| S0-18 | LAM | (6,40; 5,40) | (6,40; 8,90) | 3,50 | 0,080 | ekran z lamel drewnianych klatka/hol (nad nim podciąg PD-C w ST1 pod ścianą C na P1) |

**Otwory P0** (położenie „od–do” wzdłuż ściany: x dla ścian równoległych do osi X, y dla ścian równoległych do osi Y; parapet i wysokość od FFL P0)

| id | ściana | od | do | szer. [m] | wys. [m] | parapet [m] | typ / symbol | uwagi |
|---|---|---|---|---|---|---|---|---|
| O0-01 | S0-01 | 1,000 | 11,850 | 10,85 | 2,75 | 0,00 | fasada FS1 | przeszklenie E: kwatery 1,60/1,90/2,40/2,40/2,55 m (rytm szkicu narastający ku wsch.), HS w kw. 2 (salon) i 4 (oś wejścia); podziały 2,60, 4,50, 6,90, 9,30 |
| O0-02 | S0-06 | 1,200 | 4,400 | 3,20 | 2,75 | 0,00 | okno HS-W | przeszklenie zach. salonu z drzwiami HS na taras zach. pod okapem 1,5 m |
| O0-03 | S0-06 | 6,300 | 8,100 | 1,80 | 1,50 | 0,90 | okno OZ2 | pokój gościnny |
| O0-04 | S0-02 | 0,900 | 2,100 | 1,20 | 2,40 | 0,00 | drzwi_zewn DZ2 | drzwi przeszklone kuchnia - patio poranne |
| O0-05 | S0-05 | 7,450 | 8,550 | 1,10 | 2,40 | 0,00 | drzwi_zewn DZ1 | drzwi wejściowe 110x240 na osi widoku (x = 8,00) |
| O0-06 | S0-05 | 8,750 | 9,400 | 0,65 | 2,40 | 0,10 | okno ON4 | doświetlenie boczne wiatrołapu (szkło mleczne) |
| O0-07 | S0-05 | 12,700 | 17,700 | 5,00 | 2,25 | 0,00 | brama BR1 | brama segmentowa 500x225, kratki went. >= 0,08 m2 |
| O0-08 | S0-04 | 5,600 | 6,500 | 0,90 | 2,10 | 0,00 | drzwi_zewn DZ3 | drzwi boczne garażu (rowery, ogród) |
| O0-09 | S0-05 | 0,800 | 1,700 | 0,90 | 0,60 | 1,60 | okno ON1 | łazienka gościnna |
| O0-10 | S0-05 | 10,300 | 11,300 | 1,00 | 0,60 | 1,60 | okno ON1 | przedsionek gospodarczy |
| O0-11 | S0-08 | 5,295 | 6,295 | 1,00 | 2,60 | 0,00 | otwor  | stopa biegu 1 (P0->P1) |
| O0-12 | S0-08 | 6,950 | 9,545 | 2,60 | 2,60 | 0,00 | otwor  | wylot holu do strefy dziennej - oś widoku |
| O0-13 | S0-09a | 0,800 | 1,600 | 0,80 | 2,05 | 0,00 | drzwi D2 | łazienka gościnna (z pokoju gościnnego) |
| O0-14 | S0-09a | 3,000 | 3,900 | 0,90 | 2,05 | 0,00 | drzwi D1 | pokój gościnny |
| O0-15 | S0-09b | 7,550 | 8,450 | 0,90 | 2,10 | 0,00 | drzwi DS1 | drzwi szklane wiatrołap - hol (na osi) |
| O0-16 | S0-09c | 10,100 | 11,000 | 0,90 | 2,05 | 0,00 | drzwi D1 | pom. techniczne |
| O0-17 | S0-11 | 9,800 | 10,700 | 0,90 | 2,05 | 0,00 | drzwi D1 | wiatrołap - przedsionek gosp. |
| O0-18 | S0-07 | 9,400 | 10,300 | 0,90 | 2,05 | 0,00 | drzwi DG1 | garaż - przedsionek: szczelne, samozamykacz, U<=1,3 |
| O0-19 | S0-13 | 2,750 | 3,550 | 0,80 | 2,05 | 0,00 | drzwi D2 | WC gościnne (na zewnątrz) |
| O0-20 | S0-15 | 9,300 | 10,800 | 1,50 | 2,30 | 0,00 | otwor  | przedpokój gościnny / garderoba - wiatrołap |
| O0-21 | S0-17 | 4,350 | 5,150 | 0,80 | 2,05 | 0,00 | drzwi D3 | spiżarnia |

**Pomieszczenia P0** (lica wykończone)

| nr | pomieszczenie | wielobok netto (xmin; ymin – xmax; ymax) | pow. [m²] | posadzka | uwagi |
|---|---|---|---|---|---|
| 0.01 | Salon + jadalnia + kuchnia | wielobok (obwiednia) (0,105; 0,105 – 11,895; 5,295) | 59,31 | dąb/gres | jadalnia pod pustką 2-kondygnacyjną (oś B'-C'), kuchnia z wyspą przy ścianie E |
| 0.02 | Spiżarnia | prostokąt (10,675; 4,075 – 11,895; 5,295) | 1,49 | gres |  |
| 0.03 | Pokój gościnny / gabinet | prostokąt (0,105; 5,505 – 3,945; 8,795) | 12,63 | dąb |  |
| 0.04 | Klatka schodowa | prostokąt (4,155; 5,505 – 6,295; 8,795) | 7,04 | dąb |  |
| 0.05 | Hol (oś światła) | wielobok (obwiednia) (6,440; 5,505 – 9,545; 8,870) | 10,29 | dąb |  |
| 0.06 | Pomieszczenie techniczne | wielobok (obwiednia) (9,755; 5,505 – 11,895; 8,795) | 6,88 | gres | PC split (hydrobox), zasobnik CWU 300 l, bufor 100 l, centrala wentylacyjna, rozdzielacze, RG, wodomierz |
| 0.07 | Wiatrołap / hol wejściowy | prostokąt (6,475; 8,930 – 9,545; 11,195) | 6,95 | gres | świetlik 1,2x2,0 m w stropodachu skrzydła |
| 0.08 | Przedsionek gospodarczy | prostokąt (9,755; 9,005 – 11,895; 11,195) | 4,69 | gres | garaż - dom; szafa na buty/kurtki robocze |
| 0.09 | Łazienka gościnna (prysznic) | prostokąt (0,105; 9,005 – 2,475; 11,195) | 5,19 | gres |  |
| 0.10 | WC gościnne | prostokąt (2,625; 9,975 – 3,875; 11,195) | 1,53 | gres | szer. 1,25 >= 0,90 (W-060) |
| 0.11 | Przedpokój gościnny / garderoba | wielobok (obwiednia) (2,625; 9,005 – 6,325; 11,195) | 6,18 | dąb | szafy wnękowe 0,6 m wzdłuż ściany pn. |
| 0.12 | Garaż 2-stanowiskowy | prostokąt (12,220; 4,905 – 18,295; 11,195) | 38,21 | posadzka żywiczna | w świetle 6,08 x 6,29 m |
| | **PU P0 (bez garażu)** | | **122,18** | | |

Wieloboki nieprostokątne: **0.01** = prostokąt (0,105; 0,105 – 11,895; 5,295) minus narożnik spiżarni (10,525; 3,925 – 11,895; 5,295);
**0.05** = (6,44; 5,505 – 9,545; 8,87) minus szacht SI (6,505; 5,505 – 6,905; 5,905); **0.06** = (9,755; 5,505 – 11,895; 8,795) minus pion K2
(9,755; 8,395 – 10,155; 8,795); **0.11** = (2,625; 9,005 – 6,325; 9,825) ∪ (4,025; 9,825 – 6,325; 11,195).

Funkcja P0: strefa dzienna 59,31 m² w jednym paśmie 11,79 × 5,19 m (salon x 0,1–4,5 / jadalnia pod pustką x 4,5–8,4 / kuchnia z wyspą x 8,4–11,9);
pasmo północne: pokój gościnny (W) z łazienką z prysznicem w skrzydle (drzwi bezpośrednio z pokoju), klatka schodowa za ekranem lamel, hol na osi,
pom. techniczne 6,88 m² (PC split — hydrobox, CWU 300 l, bufor, centrala wentylacyjna, RG, wodomierz) przy garażu. Skrzydło wejściowe: łazienka
gościnna, WC gościnne, przedpokój gościnny z szafami, wiatrołap / hol wejściowy 6,95 m² (świetlik SW2), przedsionek gospodarczy 4,69 m²
łączący garaż (drzwi DG1 szczelne z samozamykaczem, WT §106) z wiatrołapem i pom. technicznym. Droga zakupów: garaż → przedsionek → wiatrołap →
hol → kuchnia (≈ 11 m). Jednostka zewnętrzna PC przy elewacji pn. (x 10,20–11,40; y 11,85–12,45) w osłonie lamelowej.

### 3.5 I PIĘTRO P1 (+3,150)

**Obrys zewnętrzny P1**: prostokąt (−0,30; −0,30) – (12,30; 9,20) = 12,60 × 9,50 m, pow. 119,70 m² (+ rama C wysunięta 1,00 m poza lico — element
zewnętrzny, bez wnętrza). W stropie ST1 **pustka** nad jadalnią: x 4,50–8,40, y 0,15–4,00 (15,0 m²) z balustradą szklaną h = 1,00 m wzdłuż
y = 4,00 i x = 8,40 (od strony pokoju rodzinnego).

**Ściany P1**

| id | typ | oś od | oś do | dł. osi [m] | grubość [m] | uwagi |
|---|---|---|---|---|---|---|
| S1-01 | SZ1 | (0,00; 0,00) | (12,00; 0,00) | 12,00 | 0,405 | ściana pd. bryły B: pełna 0...4,5 i 11,7...12, boks C 4,5...11,7 na słupkach SLC w osiach 6,9 / 9,3 |
| S1-02 | SZ1 | (12,00; 0,00) | (12,00; 8,90) | 8,90 | 0,405 | ściana wsch. (oś E) |
| S1-03 | SZ1 | (12,00; 8,90) | (0,00; 8,90) | 12,00 | 0,405 | ściana pn. (oś 4) |
| S1-04 | SZ1 | (0,00; 8,90) | (0,00; 0,00) | 8,90 | 0,405 | ściana zach. (oś A) - pod wspornikiem P2 |
| S1-05 | SW18 | (0,00; 5,40) | (12,00; 5,40) | 12,00 | 0,210 | ściana grzbietowa (oś 3) |
| S1-06 | SW18 | (4,05; 5,40) | (4,05; 8,90) | 3,50 | 0,210 | oś B |
| S1-07 | SW18 | (6,40; 5,40) | (6,40; 8,90) | 3,50 | 0,210 | oś C - na podciągu PD-C w ST1 |
| S1-08 | SW18 | (9,65; 5,40) | (9,65; 8,90) | 3,50 | 0,210 | oś D |
| S1-09 | DZL | (0,00; 4,00) | (4,50; 4,00) | 4,50 | 0,125 | pokój dziecka 1 / galeria |
| S1-10 | DZL | (4,50; 0,00) | (4,50; 4,00) | 4,00 | 0,125 | pokój dziecka 1 / pustka - na podciągu PD-2 (oś B') |

**Otwory P1** (parapet i wysokość od FFL P1)

| id | ściana | od | do | szer. [m] | wys. [m] | parapet [m] | typ / symbol | uwagi |
|---|---|---|---|---|---|---|---|---|
| O1-01 | S1-01 | 4,500 | 11,700 | 7,20 | 1,50 | 0,50 | boks BC1 | boks C: 3 kwatery 2,40 m, szkło 3,65...5,15, dolna część stała VSG do 0,85 (W-097); przed pustką i pokojem rodzinnym; podziały 6,90, 9,30 |
| O1-02 | S1-04 | 1,000 | 3,000 | 2,00 | 1,50 | 0,85 | okno OZ3 | pokój dziecka 1 - zachód |
| O1-03 | S1-04 | 6,100 | 8,100 | 2,00 | 1,50 | 0,85 | okno OZ3 | pokój dziecka 2 - zachód |
| O1-04 | S1-02 | 1,000 | 3,400 | 2,40 | 1,50 | 0,85 | okno OE1 | pokój rodzinny - wschód, widok na dach zielony garażu |
| O1-05 | S1-03 | 7,400 | 8,800 | 1,40 | 0,60 | 1,50 | okno ON2 | łazienka |
| O1-06 | S1-03 | 10,300 | 11,400 | 1,10 | 0,60 | 1,50 | okno ON2 | pralnia |
| O1-07 | S1-03 | 4,400 | 6,000 | 1,60 | 2,40 | 0,40 | okno ON3 | okno klatki (spocznik 4,725) - światło pn. w rdzeniu |
| O1-08 | S1-05 | 1,200 | 2,100 | 0,90 | 2,05 | 0,00 | drzwi D1 | pokój dziecka 2 |
| O1-09 | S1-05 | 4,155 | 6,295 | 2,14 | 2,60 | 0,00 | otwor  | klatka schodowa - wyjście biegu 2 i wejście na bieg 3 |
| O1-10 | S1-05 | 7,100 | 7,900 | 0,80 | 2,05 | 0,00 | drzwi D2 | łazienka (na zewnątrz) |
| O1-11 | S1-05 | 10,000 | 10,800 | 0,80 | 2,05 | 0,00 | drzwi D1 | pralnia |
| O1-12 | S1-09 | 2,600 | 3,500 | 0,90 | 2,05 | 0,00 | drzwi D1 | pokój dziecka 1 |

**Pomieszczenia P1**

| nr | pomieszczenie | wielobok netto (xmin; ymin – xmax; ymax) | pow. [m²] | posadzka | uwagi |
|---|---|---|---|---|---|
| 1.01 | Galeria nad pustką (hol) | prostokąt (0,105; 4,062 – 8,400; 5,295) | 10,22 | dąb | balustrada szklana 1,00 m wzdłuż pustki; od pd. światło boksu C |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | prostokąt (8,400; 0,105 – 11,895; 5,295) | 18,14 | dąb | otwarty na galerię i pustkę (balustrada), wyjście schodów |
| 1.03 | Pokój dziecka 1 | prostokąt (0,105; 0,105 – 4,438; 3,938) | 16,60 | dąb | z szafą wnękową |
| 1.04 | Pokój dziecka 2 | prostokąt (0,105; 5,505 – 3,945; 8,795) | 12,63 | dąb |  |
| 1.05 | Klatka schodowa | prostokąt (4,155; 5,505 – 6,295; 8,795) | 7,04 | dąb |  |
| 1.06 | Łazienka | wielobok (obwiednia) (6,505; 5,505 – 9,545; 8,795) | 9,84 | gres | wanna + prysznic + 2 umywalki + WC |
| 1.07 | Pralnia z suszarnią | wielobok (obwiednia) (9,755; 5,505 – 11,895; 8,795) | 6,88 | gres |  |
| | **PU P1** | | **81,35** | | |


Funkcja P1: galeria (hol) 1,23 m szerokości wzdłuż ściany grzbietowej prowadzi od wyjścia schodów (x 4,2–5,2) do pokojów dzieci (W) i łazienki;
pokój rodzinny/biblioteka 18,14 m² za boksem C (kwatery 2–3) i oknem wschodnim otwiera się na galerię i pustkę; pralnia z suszarnią nad pom.
technicznym (pion K2). Pokoje dzieci 16,60 i 12,63 m² od zachodu (elewacja S bryły B pełna jak w szkicu, x −0,30 … 4,50).

### 3.6 II PIĘTRO P2 (+6,300)

**Obrys zewnętrzny P2** (lica): (−1,30; 0,90) → (12,30; 0,90) → (12,30; 5,70) → (9,95; 5,70) → (9,95; 9,20) → (3,75; 9,20) → (3,75; 5,70) →
(−1,30; 5,70); pow. 86,98 m². Przed licem 1' loggia y −0,30 … 0,90 (za ekranem lamel y = −0,40), płyty ST2L/ST3 wysunięte do y = −1,20 i
x = −2,20. Bryła A (z lamelami) ma w elewacji 13,60 m (x −1,30 … 12,30).

**Ściany P2**

| id | typ | oś od | oś do | dł. osi [m] | grubość [m] | uwagi |
|---|---|---|---|---|---|---|
| S2-01 | SZL | (-1,00; 1,20) | (12,00; 1,20) | 13,00 | 0,405 | lico pd. pokoi (oś 1') - lekka ściana/przeszklenia za loggią; na uskoku ST2/ST2L |
| S2-02 | SZ1 | (12,00; 1,20) | (12,00; 5,40) | 4,20 | 0,405 | ściana wsch. |
| S2-03 | SZ1 | (12,00; 5,40) | (9,65; 5,40) | 2,35 | 0,405 | ściana pn. bryły A (nad dachem P1) |
| S2-04 | SZ1 | (9,65; 5,40) | (9,65; 8,90) | 3,50 | 0,405 | nadbudowa - ściana wsch. |
| S2-05 | SZ1 | (9,65; 8,90) | (4,05; 8,90) | 5,60 | 0,405 | nadbudowa - ściana pn. |
| S2-06 | SZ1 | (4,05; 8,90) | (4,05; 5,40) | 3,50 | 0,405 | nadbudowa - ściana zach. |
| S2-07a | SZ1 | (4,05; 5,40) | (0,00; 5,40) | 4,05 | 0,405 | ściana pn. bryły A (oś 3) |
| S2-07b | SZL | (0,00; 5,40) | (-1,00; 5,40) | 1,00 | 0,405 | ściana pn. na wsporniku 1,0 m (lekka) |
| S2-08 | SZL | (-1,00; 5,40) | (-1,00; 1,20) | 4,20 | 0,405 | ściana zach. na wsporniku 1,0 m (lekka, oś A') |
| S2-09 | SW18 | (4,05; 5,40) | (9,65; 5,40) | 5,60 | 0,210 | oś 3 wewn. (klatka, łazienka) |
| S2-10 | SW18 | (6,40; 5,40) | (6,40; 8,90) | 3,50 | 0,210 | oś C - klatka/łazienka |
| S2-11 | DZ12 | (4,05; 1,20) | (4,05; 5,40) | 4,20 | 0,150 | gabinet / hol |
| S2-12 | DZ12 | (6,40; 1,20) | (6,40; 5,40) | 4,20 | 0,150 | hol / garderoba |
| S2-13 | DZ12 | (8,00; 1,20) | (8,00; 5,40) | 4,20 | 0,150 | garderoba / sypialnia |

**Otwory P2** (parapet i wysokość od FFL P2; okna P2 otwierane do wewnątrz — WT §299)

| id | ściana | od | do | szer. [m] | wys. [m] | parapet [m] | typ / symbol | uwagi |
|---|---|---|---|---|---|---|---|---|
| O2-01 | S2-01 | -0,800 | 3,850 | 4,65 | 2,60 | 0,00 | okno HS-P2 | gabinet - przeszklenie na loggię (HS, W-098: D-17); za lamelami; podziały 1,55 |
| O2-02 | S2-01 | 4,350 | 6,200 | 1,85 | 2,60 | 0,00 | okno DL1 | hol - wyjście na loggię; podziały 5,30 |
| O2-03 | S2-01 | 6,650 | 7,750 | 1,10 | 1,60 | 0,85 | okno OP2 | garderoba - na loggię |
| O2-04 | S2-01 | 8,250 | 11,750 | 3,50 | 2,60 | 0,00 | okno HS-P2 | sypialnia - przeszklenie na loggię (HS); podziały 10,00 |
| O2-05 | S2-08 | 2,000 | 4,600 | 2,60 | 1,80 | 0,60 | okno OP1 | gabinet - zachód (okno na wsporniku), dolna część stała VSG |
| O2-06 | S2-02 | 2,000 | 4,400 | 2,40 | 1,60 | 0,85 | okno OE2 | sypialnia - wschód (poranne słońce) |
| O2-07 | S2-05 | 7,400 | 8,800 | 1,40 | 0,80 | 1,50 | okno ON2 | łazienka rodziców |
| O2-08 | S2-05 | 4,400 | 6,000 | 1,60 | 1,70 | 0,90 | okno ON3 | okno klatki (pn.) - nad biegami P1-P2 |
| O2-09 | S2-11 | 4,000 | 4,900 | 0,90 | 2,05 | 0,00 | drzwi D1 | gabinet |
| O2-10 | S2-12 | 4,000 | 4,900 | 0,90 | 2,05 | 0,00 | otwor DP1 | drzwi przesuwne (w ścianie) - garderoba = przedpokój apartamentu |
| O2-11 | S2-13 | 4,000 | 4,900 | 0,90 | 2,05 | 0,00 | drzwi D1 | sypialnia |
| O2-12 | S2-09 | 4,155 | 6,295 | 2,14 | 2,60 | 0,00 | otwor  | wyjście z biegu 4; balustrada nad biegiem 3 |
| O2-13 | S2-09 | 7,000 | 7,800 | 0,80 | 2,05 | 0,00 | drzwi D2 | łazienka rodziców (z garderoby) |

**Pomieszczenia P2** (2.06 — przestrzeń nad biegami, nie wlicza się do PU)

| nr | pomieszczenie | wielobok netto (xmin; ymin – xmax; ymax) | pow. [m²] | posadzka | uwagi |
|---|---|---|---|---|---|
| 2.01 | Hol | prostokąt (4,125; 1,305 – 6,325; 5,295) | 8,78 | dąb | klapa na dach 0,9x0,9 + drabina składana; wyjście na loggię |
| 2.02 | Gabinet / pokój | prostokąt (-0,895; 1,305 – 3,975; 5,295) | 19,43 | dąb | wspornik 1,0 m na zachód |
| 2.03 | Garderoba (przedpokój apartamentu) | prostokąt (6,475; 1,305 – 7,925; 5,295) | 5,79 | dąb |  |
| 2.04 | Sypialnia rodziców | prostokąt (8,075; 1,305 – 11,895; 5,295) | 15,24 | dąb | okna S (loggia) i E |
| 2.05 | Łazienka rodziców | wielobok (obwiednia) (6,505; 5,505 – 9,545; 8,795) | 9,84 | gres | prysznic walk-in, wanna wolnostojąca, 2 umywalki, WC |
| 2.06 | Przestrzeń nad klatką (latarnia) | prostokąt (4,155; 5,505 – 6,295; 8,795) | 7,04 | - | nie wlicza się do PU (rzut biegów liczony na P0 i P1) |
| | **PU P2** | | **59,08** | | |

