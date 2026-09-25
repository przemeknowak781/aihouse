# Koncepcja — WARIANT W2: „FUNKCJA · EKONOMIA · KONSTRUKCJA”

Dom LAMELA, dom jednorodzinny wolnostojący, 3 kondygnacje nadziemne, dachy płaskie. Wersja koncepcji 1.0 z 25.09.2026.
Podstawa: `docs/00_brief_projektowy.md` (interpretacja szkicu **v2**, decyzje Inwestora z 25.09.2026) oraz rejestr wymagań `docs/10_podstawy_prawne/R1…R8`.
Przyjęto WT 2002 w brzmieniu obowiązującym do 19.09.2026, stosowane na podstawie **art. 102a PB** (R3 S-03). Wymaga to oświadczenia Inwestora składanego z wnioskiem.
Wszystkie liczby w tabelach generuje `src/make_opis.py` z modelu `src/model_w2.py`. Ten sam model rysuje rzuty, elewację, przekroje i plan zagospodarowania. Pełne dane są w `model_W2.json`.

**Wynik w skrócie**

| Parametr | Wartość |
|---|---|
| PU mieszkalna (bez garażu) | **257,40 m²** (P0 104,39 + P1 90,15 + P2 62,86) |
| Garaż 2-stanowiskowy (w świetle 6,08 × 6,08 m) | 36,91 m² |
| Strefa dzienna (salon + jadalnia + kuchnia) | 54,12 m² (wymagane ≥ 50) |
| Powierzchnia zabudowy (lica ścian zewnętrznych) | **180,60 m²**, czyli 11,3 % (limit 30 % = 480 m²) |
| Powierzchnia zabudowy, wariant kontrolny z płytami | 204,82 m² (12,8 %) |
| PBC | 1268,80 m², czyli 79,3 % (≥ 50 %) |
| Intensywność nadziemna | 0,238 (0,05–0,80) |
| Wysokość zabudowy wg upzp / MPZP (do attyki) | **10,05 m** (≤ 11,00) |
| Wysokość budynku wg WT § 6 | 9,90 m (grupa N) |

## 1. Idea wariantu W2

W2 odtwarza sylwetę „S” z mniejszą liczbą elementów konstrukcyjnych i niższym kosztem. Założenia:

* **Jeden prostokątny trzon mieszkalny 12,60 × 9,00 m** na P0 i P1. Wszystkie ściany nośne biegną w pionie jedna nad drugą.
* **Garaż z pasem gospodarczym** dostawiony od wschodu w jednej kondygnacji.
* **Długa lamelowa bryła A** na P2, cofnięta do strefy południowej (głębokość 4,80 m w osiach). Stoi na ścianach osi 1 i 3.

Kształt „S” powstaje z przesunięć brył i z wysuniętych płyt:

* Bryła A wysunięta na **zachód** jako wspornik 1,00 m.
* Bryła B z ramą boksu C, a pod nią **linia D**, która biegnie na **wschód** aż do narożnika garażu.
* Przeszklony parter E z okapem **na zachód** 1,50 m.

Każdy element nośny, który nie stoi na ścianie, jest krótki i ma wskazaną ścieżkę obciążeń:

* słupy stalowe w szprosach fasady E;
* belki B1 i B2;
* ściany-tarcze ŻB wspornika A;
* płyty z łącznikami termoizolacyjnymi.

Główne zasady:

* **Konstrukcja:** siatka osi A–F × 1–5. Stropy ŻB 20 cm pracują jednokierunkowo (N–S) na rozpiętościach 4,80 i 3,60 m. Nad garażem strop 24 cm o rozpiętości 6,40 m. Wsporniki ≤ 1,50 m.
* **Instalacje:** jeden szacht **SI** (x 5,59–5,99; y 4,905–5,605) łączy łazienki P0, P1 i P2 ustawione dokładnie jedna nad drugą. Drugi, krótki pion **K2** obsługuje pralnię P1 i WC P0. Pomieszczenie techniczne leży obok garażu, a jednostka zewnętrzna PC stoi przy ścianie wschodniej.
* **Funkcja:** wejście i garaż są od północy, obok siebie. Z garażu przez przedsionek gospodarczy (ze spiżarnią) prowadzi droga prosto do kuchni, łącznie ok. 6 m. Strefa dzienna ma 11,4 m przeszklenia na południe. Pokoje dzieci są od zachodu, dzięki czemu elewacja bryły B pozostaje pełna jak w szkicu. Sypialnia rodziców i gabinet są w bryle A za lamelami.

## 2. Odczyt szkicu w W2 (porównanie ilościowe)

Skala szkicu: 45,8 px/m (brief 1.1). Współrzędne szkicu przeliczono na układ W2, w którym lico zachodnie bryły B = x −0,30. Porównanie graficzne jest w `elewacja_S.png`: szkic z nałożonym czerwonym obrysem W2.

| element szkicu | szkic (x od lica zach. B) | W2 (x od lica zach. B) | komentarz |
|---|---|---|---|
| A — bryła II p. w lamelach | −1,0…+12,2 (13,2 m) | −1,00…+12,60 (13,60 m) | wspornik zach. 1,00 m jak w szkicu; wsch. koniec w licu B (ściany w pionie) |
| płyty A (dół/góra) | −2,4…+12,5 | −2,10…+12,90 (15,00 m) | wysunięcie 1,10 m zach., 1,00 m pd., 0,30 m wsch. |
| B — bryła I p. | 0…12,0 | 0…12,60 | +0,60 m (moduł 12,00 m w osiach A–E dla stropów i garażu) |
| C — boks 3 kwatery | +4,5…+11,7 (7,2 m) | +4,40…+11,40 (7,00 m) | rama wysunięta 1,00 m, x +3,90…+12,90 |
| D — linia pozioma | +3,8…+19,0 | +3,90…+19,00 (+3,85) | płyta dolna ramy C, dalej attyka dachu zielonego garażu |
| D — pion / narożnik G | +19,0 | +19,00 | ściana wsch. garażu (lico) |
| E — przeszklenie 5 kwater | +1,0…+13,2 (12,2 m) | +0,60…+12,00 (11,40 m) | **odstępstwo −0,8 m**: koniec w osi ściany nośnej E (ściany w pionie) |
| E — płyta dachu parteru | −1,5…+14,1 | −1,50…+12,90 | okap zach. 1,50 m, pd. 1,00 m |
| G — pełna ściana garażu | +13,2…+19,0 (5,8 m) | +13,45…+19,00 (5,55 m) | przed nią przeszklone drzwi gospodarcze przedsionka (x +12,55…+13,45) |

Proporcje pionowe szkicu są umowne (brief 1.1). Kolejność i relacje pasm są zachowane:

* okap E (+2,75…+3,05) leży poniżej linii D (+3,65…+3,85);
* boks C (+3,85…+5,35) jest wpisany w bryłę B pod płytą A (+5,95…+6,25);
* lamele A (+6,15…+9,10) są zamknięte płytą dachu (+9,10…+9,42) i cofniętą attyką (+9,80).

Rytm przesunięć zachód–wschód–zachód jest zachowany, czyli kształt „S”. **Nie ma tarasu na płycie D ani wiaty na słupie.** Dach garażu jest zielony i nieużytkowy, bez wyjścia.

## 3. Definicja wymiarowa

### 3.1 Układ i siatka osi
* Osie x → wschód, y → północ, z → góra. Początek układu to przecięcie osi A (zach. oś nośna bryły głównej) i osi 1 (pd.).
* Osie przechodzą przez środek warstwy konstrukcyjnej ścian.
* ±0,00 = posadzka P0 = **101,65 m n.p.m.** (PL-EVRF2007-NH).

| oś x | x [m] | znaczenie |
|---|---|---|
| A' | -1,000 | ściana zach. P2 na wsporniku (lekka) |
| A | 0,000 | ściana zach. P0/P1, podpora wspornika A |
| B | 3,875 | ściana pokój gościnny / łazienki (P0–P1, nadbudowa P2) |
| C | 6,095 | ściana zach. klatki schodowej |
| D | 8,425 | ściana wsch. klatki schodowej |
| E | 12,000 | ściana wsch. bryły B/A; ściana dom/garaż |
| F | 18,400 | ściana wsch. garażu (pion D) |

| oś y | y [m] | znaczenie |
|---|---|---|
| 1 | 0,000 | linia fasady pd. (P0: belka B1 na słupach; P1/P2 ściany) |
| 2 | 2,600 | ściana strefa gosp. / garaż |
| 3 | 4,800 | ściana grzbietowa (nośna, P0–P2) |
| 4 | 8,400 | ściana pn. części mieszkalnej |
| 5 | 9,000 | ściana pn. garażu (brama) |

Obrys lica zewnętrznego (ocieplenie):
* **P0** (bryła mieszkalna + garaż): (-0,30; -0,30) → (-0,30; 8,70) → (11,70; 8,70) → (11,70; 9,30) → (18,70; 9,30) → (18,70; -0,30)
* **P1**: (12,30; -0,30) → (-0,30; -0,30) → (-0,30; 8,70) → (12,30; 8,70)
* **P2**: (12,30; -0,30) → (-1,30; -0,30) → (-1,30; 5,10) → (3,58; 5,10) → (3,58; 8,70) → (8,73; 8,70) → (8,73; 5,10) → (12,30; 5,10)

### 3.2 Poziomy i grubości
| element | rzędna / grubość |
|---|---|
| posadzka P0 (±0,00) | 0,00 = 101,65 m n.p.m.; teren przy budynku −0,33…−0,17 (średnio ≈ −0,25) |
| podłoga na gruncie | warstwy 0,15 (wykładzina/gres, jastrych 6,5 cm z ogrzewaniem podł., EPS 100) + płyta ŻB 0,25 + XPS 0,15 |
| wysokość kondygnacji | 3,15 m = warstwy 0,15 + strop 0,20 + w świetle 2,80 |
| ST1 (nad P0) | spód +2,80, wierzch +3,00; posadzka P1 +3,15 |
| ST2 (nad P1) | spód +5,95, wierzch +6,15; posadzka P2 +6,30 |
| ST3 stropodach P2 | spód +9,10, wierzch płyty +9,32 (22 cm); PIR ~0,24 + membrana → +9,60; attyka +9,80 |
| dach P1 (część pn., poza nadbudową) | wierzch warstw +6,50; attyka +6,70 |
| strop garażu / strefy gosp. | spód +2,76, wierzch +3,00 (24 cm); dach zielony ekstensywny → +3,35; attyka (linia D) +3,85 |
| wysokości w świetle | pokoje P0/P1/P2 2,80 m; garaż 2,86 m (posadzka −0,10); pom. pomocnicze pod sufitem podwieszonym (kanały) ≥ 2,50 m |
| ławy fundamentowe | ŻB 60 × 35 cm, spód −1,10 (≥ h_z = 0,80 m pod terenem ≈ −0,30); ściany fundamentowe 24 cm |
| krawędzie płyt (widok) | okap E +2,75…+3,05; linia D +3,65…+3,85; rama C góra +5,35…+5,55; ST2 +5,95…+6,25; ST3 +9,10…+9,42 |

### 3.3 Typy przegród pionowych
| kod | opis | lico od osi: strona wnętrza / zewn. [m] |
|---|---|---|
| SZ1 | ściana zewn. nośna: tynk 1,5 + silikat 18 + EPS grafit/wełna 20 + tynk 1 cm | 0,105 / 0,300 |
| SZL | ściana zewn. lekka P2 (wspornik): szkielet stal/drewno + wełna 20 + płyta, gr. 40,5 cm | 0,105 / 0,300 |
| SW18 | ściana wewn. nośna: silikat 18 + 2x tynk 1,5 | 0,105 / 0,105 |
| SWG | ściana nośna dom/garaż: tynk 1,5 + silikat 18 + wełna 12 + tynk 1 (U~0,28) | 0,105 / 0,220 |
| SC12 | ścianka środkowa schodów: silikat 12 (fair-faced) | 0,060 / 0,060 |
| DZ12 | ścianka działowa: silikat 12 + 2x tynk 1,5 | 0,075 / 0,075 |

### 3.4 PARTER P0 (±0,00)

**Ściany**

| ID | oś warstwy konstr. (x; y) [m] | dł. osi | typ | grub. całk. | uwagi |
|---|---|---|---|---|---|
| S0-01 | (0,000; 0,000) → (12,000; 0,000) | 12,00 | SZ1 | 0,405 | fasada pd. strefy dziennej: przeszklenie 5 kwater na słupach stalowych SL1-SL4 + belka B1 |
| S0-02 | (12,000; 0,000) → (18,400; 0,000) | 6,40 | SZ1 | 0,405 | ściana pd. strefy gospodarczej (pełna - bryła G) |
| S0-03 | (18,400; 0,000) → (18,400; 9,000) | 9,00 | SZ1 | 0,405 | ściana wsch. garażu (pion D) |
| S0-04 | (18,400; 9,000) → (12,000; 9,000) | 6,40 | SZ1 | 0,405 | ściana pn. garażu z bramą |
| S0-05 | (12,000; 9,000) → (12,000; 8,400) | 0,60 | SZ1 | 0,405 | ściana zach. garażu - odcinek zewn. |
| S0-06 | (12,000; 8,400) → (0,000; 8,400) | 12,00 | SZ1 | 0,405 | ściana pn. części mieszkalnej |
| S0-07 | (0,000; 8,400) → (0,000; 0,000) | 8,40 | SZ1 | 0,405 | ściana zach. (oś A) |
| S0-08 | (0,000; 4,800) → (12,000; 4,800) | 12,00 | SW18 | 0,210 | ściana grzbietowa (oś 3) |
| S0-09 | (3,875; 4,800) → (3,875; 8,400) | 3,60 | SW18 | 0,210 | oś B |
| S0-10 | (6,095; 4,800) → (6,095; 8,400) | 3,60 | SW18 | 0,210 | oś C - klatka schodowa |
| S0-11 | (8,425; 4,800) → (8,425; 8,400) | 3,60 | SW18 | 0,210 | oś D - klatka schodowa |
| S0-12 | (12,000; 0,000) → (12,000; 2,600) | 2,60 | SW18 | 0,210 | oś E - kuchnia/przedsionek |
| S0-13 | (12,000; 2,600) → (12,000; 8,400) | 5,80 | SWG | 0,325 | oś E - dom/garaż (ocieplona od garażu) |
| S0-14 | (18,400; 2,600) → (12,000; 2,600) | 6,40 | SWG | 0,325 | oś 2 - strefa gosp./garaż |
| S0-15 | (7,260; 4,800) → (7,260; 7,145) | 2,34 | SC12 | 0,120 | ścianka środkowa schodów |
| S0-16 | (3,875; 6,275) → (6,095; 6,275) | 2,22 | DZ12 | 0,150 | działowa |
| S0-17 | (8,425; 6,375) → (12,000; 6,375) | 3,57 | DZ12 | 0,150 | działowa |
| S0-18 | (9,675; 6,375) → (9,675; 8,400) | 2,03 | DZ12 | 0,150 | działowa |
| S0-19 | (14,275; 0,000) → (14,275; 2,600) | 2,60 | DZ12 | 0,150 | działowa |
| S0-20 | (15,475; 0,000) → (15,475; 2,600) | 2,60 | DZ12 | 0,150 | działowa |

**Otwory** (położenie wzdłuż osi ściany; szerokość i wysokość w świetle muru; parapet względem posadzki kondygnacji)

| ID | ściana | położenie | szer. | wys. | parapet | typ | symbol | otwieranie | uwagi |
|---|---|---|---|---|---|---|---|---|---|
| O0-01 | S0-01 | x 0,30…11,70 | 11,40 | 2,75 | 0,00 | fasada (5 kw.) | FS1 |  | przeszklenie E: 5 kwater po 2,28 m (kw. 2 i 4 - drzwi HS), słupki SL1-SL4 w szprosach |
| O0-02 | S0-07 | y 1,20…3,60 | 2,40 | 2,15 | 0,45 | okno | OZ1 |  | okno zach. salonu (siedzisko), pod okapem 1,5 m |
| O0-03 | S0-07 | y 5,50…7,30 | 1,80 | 1,50 | 0,90 | okno | OZ2 |  | pokój gościnny |
| O0-04 | S0-06 | x 10,20…11,30 | 1,10 | 2,40 | 0,00 | drzwi_zewn | DZ1 | zawias a, na -y | drzwi wejściowe 110x240 (w świetle ościeżnicy >= 0,90x2,00), próg <= 2 cm |
| O0-05 | S0-04 | x 12,75…17,75 | 5,00 | 2,25 | 0,00 | brama | BR1 |  | brama segmentowa 500x225, kratki went. >= 0,08 m2 |
| O0-06 | S0-03 | y 5,00…5,90 | 0,90 | 2,10 | 0,00 | drzwi_zewn | DZ2 | zawias a, na -x | drzwi boczne garażu (rowery, ogród) |
| O0-07 | S0-08 | x 4,20…5,10 | 0,90 | 2,10 | 0,00 | otwor |  |  | przejście do przedpokoju gościnnego |
| O0-08 | S0-08 | x 6,20…7,20 | 1,00 | 2,55 | 0,00 | otwor |  |  | wejście na bieg 1 schodów |
| O0-09 | S0-08 | x 7,40…8,20 | 0,80 | 2,00 | 0,00 | drzwi | D3 | zawias a, na +y | schowek pod schodami |
| O0-10 | S0-08 | x 8,80…10,20 | 1,40 | 2,40 | 0,00 | otwor |  |  | hol - strefa dzienna |
| O0-11 | S0-09 | y 5,10…6,00 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias a, na -x | pokój gościnny |
| O0-12 | S0-16 | x 4,20…5,00 | 0,80 | 2,05 | 0,00 | drzwi | D2 | zawias a, na -y | łazienka gościnna (na zewnątrz, kratka) |
| O0-13 | S0-17 | x 10,30…11,20 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias b, na -y | wiatrołap - hol |
| O0-14 | S0-17 | x 8,70…9,50 | 0,80 | 2,05 | 0,00 | drzwi | D2 | zawias a, na -y | WC (na zewnątrz, kratka) |
| O0-15 | S0-12 | y 1,00…1,90 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias a, na +x | kuchnia - przedsionek gosp. |
| O0-16 | S0-14 | x 12,50…13,40 | 0,90 | 2,05 | 0,00 | drzwi | DG1 | zawias a, na +y | przedsionek - garaż: szczelne, samozamykacz, U<=1,3 |
| O0-17 | S0-14 | x 16,60…17,50 | 0,90 | 2,05 | 0,00 | drzwi | DG1 | zawias b, na +y | pom. techniczne - garaż |
| O0-19 | S0-02 | x 12,25…13,15 | 0,90 | 2,40 | 0,00 | drzwi_zewn | DZ3 | zawias a, na -y | drzwi gospodarcze przeszklone przedsionek - ogród/taras (otwierane na zewnątrz) |
| O0-18 | S0-19 | y 1,10…1,90 | 0,80 | 2,05 | 0,00 | drzwi | D3 | zawias a, na +x | spiżarnia |

**Pomieszczenia**

| nr | pomieszczenie | geometria (lica wykończone) | pow. netto [m²] | kategoria | pobyt ludzi | posadzka | uwagi |
|---|---|---|---|---|---|---|---|
| 0.01 | Wiatrołap | prost. x 9,750…11,895; y 6,450…8,295 | 3,96 | ruchu | nie | gres | szafa wnękowa 0,6 m |
| 0.02 | Hol | prost. x 8,530…11,895; y 4,905…6,300 | 4,69 | ruchu | nie | gres |  |
| 0.03 | WC gościnne | prost. x 8,530…9,600; y 6,450…8,295 | 1,97 | pomocnicza | nie | gres | szer. 1,07 >= 0,90 (B-17) |
| 0.04 | Klatka schodówa | wielobok (7,200; 4,905) (6,200; 4,905) (6,200; 7,145) (6,200; 8,295) (8,320; 8,295) (8,320; 7,145) (7,200; 7,145) | 4,68 | ruchu | nie | dąb |  |
| 0.05 | Schowek pod schodami | prost. x 7,320…8,320; y 4,905…7,145 | 2,24 | pomocnicza | nie | dąb | wys. zmienna 1,37-2,77 m |
| 0.06 | Salon + jadalnia + kuchnia | prost. x 0,105…11,895; y 0,105…4,695 | 54,12 | podstawowa | tak | dąb/gres | strefa otwarta; kuchnia z wyspą przy ścianie E |
| 0.07 | Przedpokój gościnny | wielobok (3,980; 4,905) (3,980; 6,200) (5,990; 6,200) (5,990; 5,605) (5,590; 5,605) (5,590; 4,905) | 2,32 | ruchu | nie | dąb |  |
| 0.08 | Łazienka gościnna (prysznic) | prost. x 3,980…5,990; y 6,350…8,295 | 3,91 | pomocnicza | nie | gres |  |
| 0.09 | Pokój gościnny / gabinet | prost. x 0,105…3,770; y 4,905…8,295 | 12,42 | podstawowa | tak | dąb |  |
| 0.10 | Przedsionek gospodarczy | prost. x 12,105…14,200; y 0,105…2,495 | 5,01 | ruchu | nie | gres | ławka, buty, zlew gosp. |
| 0.11 | Spiżarnia | prost. x 14,350…15,400; y 0,105…2,495 | 2,51 | pomocnicza | nie | gres |  |
| 0.12 | Pomieszczenie techniczne | prost. x 15,550…18,295; y 0,105…2,495 | 6,56 | techniczna | nie | gres | PC split (jedn. wewn.), zasobnik CWU 300 l, bufor, rozdzielacze, rozdzielnica RG, wodomierz |
| 0.13 | Garaż 2-stanowiskowy | prost. x 12,220…18,295; y 2,820…8,895 | 36,91 | garaż | nie | posadzka żywiczna | w świetle 6,08 x 6,08 m |

**Suma PU P0 (bez garażu): 104,39 m²**; garaż: 36,91 m².

### 3.5 I PIĘTRO P1 (+3,15)

**Ściany**

| ID | oś warstwy konstr. (x; y) [m] | dł. osi | typ | grub. całk. | uwagi |
|---|---|---|---|---|---|
| S1-01 | (0,000; 0,000) → (12,000; 0,000) | 12,00 | SZ1 | 0,405 | ściana pd. bryły B, otwor boksu C na belce B1 |
| S1-02 | (12,000; 0,000) → (12,000; 8,400) | 8,40 | SZ1 | 0,405 | ściana wsch. (oś E) |
| S1-03 | (12,000; 8,400) → (0,000; 8,400) | 12,00 | SZ1 | 0,405 | ściana pn. |
| S1-04 | (0,000; 8,400) → (0,000; 0,000) | 8,40 | SZ1 | 0,405 | ściana zach. (oś A) |
| S1-05 | (0,000; 4,800) → (12,000; 4,800) | 12,00 | SW18 | 0,210 | ściana grzbietowa (oś 3) |
| S1-06 | (3,875; 4,800) → (3,875; 8,400) | 3,60 | SW18 | 0,210 | oś B |
| S1-07 | (6,095; 4,800) → (6,095; 8,400) | 3,60 | SW18 | 0,210 | oś C |
| S1-08 | (8,425; 4,800) → (8,425; 8,400) | 3,60 | SW18 | 0,210 | oś D |
| S1-09 | (7,260; 4,800) → (7,260; 7,145) | 2,34 | SC12 | 0,120 | ścianka środkowa schodów |
| S1-10 | (3,875; 0,000) → (3,875; 3,575) | 3,58 | DZ12 | 0,150 | działowa |
| S1-11 | (0,000; 3,575) → (3,875; 3,575) | 3,88 | DZ12 | 0,150 | działowa |

**Otwory** (położenie wzdłuż osi ściany; szerokość i wysokość w świetle muru; parapet względem posadzki kondygnacji)

| ID | ściana | położenie | szer. | wys. | parapet | typ | symbol | otwieranie | uwagi |
|---|---|---|---|---|---|---|---|---|---|
| O1-01 | S1-01 | x 4,10…11,10 | 7,00 | 1,50 | 0,70 | boks (3 kw.) | BC1 |  | boks C: 3 kwatery 2,33 m, dolna część stała VSG do 0,85 m (K-17), słupki w szprosach |
| O1-02 | S1-02 | y 1,60…2,80 | 1,20 | 1,50 | 0,85 | okno | OE1 |  | pokój rodzinny - widok na dach zielony |
| O1-03 | S1-03 | x 4,40…5,30 | 0,90 | 0,60 | 1,50 | okno | ON1 |  | łazienka - okno doświetlające |
| O1-04 | S1-03 | x 10,00…11,20 | 1,20 | 0,60 | 1,50 | okno | ON2 |  | pralnia |
| O1-05 | S1-04 | y 5,70…7,50 | 1,80 | 1,50 | 0,85 | okno | OZ2 |  | pokój dziecka 2 |
| O1-06 | S1-04 | y 0,90…2,70 | 1,80 | 1,50 | 0,85 | okno | OZ2 |  | pokój dziecka 1 (elewacja pd. bryły B pełna jak w szkicu) |
| O1-07 | S1-05 | x 2,70…3,60 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias a, na +y | pokój dziecka 2 |
| O1-08 | S1-05 | x 4,20…5,00 | 0,80 | 2,05 | 0,00 | drzwi | D2 | zawias a, na -y | łazienka (na zewnątrz) |
| O1-09 | S1-05 | x 6,20…8,32 | 2,12 | 2,55 | 0,00 | otwor |  |  | klatka schodówa - oba biegi |
| O1-10 | S1-05 | x 9,00…9,90 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias b, na +y | pralnia |
| O1-11 | S1-11 | x 2,70…3,60 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias a, na -y | pokój dziecka 1 |

**Pomieszczenia**

| nr | pomieszczenie | geometria (lica wykończone) | pow. netto [m²] | kategoria | pobyt ludzi | posadzka | uwagi |
|---|---|---|---|---|---|---|---|
| 1.01 | Hol | prost. x 0,105…8,320; y 3,650…4,695 | 8,58 | ruchu | nie | dąb |  |
| 1.02 | Pokój rodzinny / biblioteka (boks C) | wielobok (11,895; 0,105) (3,950; 0,105) (3,950; 3,650) (8,320; 3,650) (8,320; 4,695) (11,895; 4,695) (11,895; 3,650) | 31,90 | podstawowa | tak | dąb |  |
| 1.03 | Pokój dziecka 1 | prost. x 0,105…3,800; y 0,105…3,500 | 12,54 | podstawowa | tak | dąb |  |
| 1.04 | Pokój dziecka 2 | prost. x 0,105…3,770; y 4,905…8,295 | 12,42 | podstawowa | tak | dąb |  |
| 1.05 | Łazienka | wielobok (3,980; 4,905) (3,980; 8,295) (5,990; 8,295) (5,990; 5,605) (5,590; 5,605) (5,590; 4,905) | 6,53 | pomocnicza | nie | gres |  |
| 1.06 | Klatka schodówa | wielobok (6,200; 4,905) (6,200; 8,295) (8,320; 8,295) (8,320; 4,905) (7,320; 4,905) (7,320; 7,145) (7,200; 7,145) (7,200; 4,905) | 6,92 | ruchu | nie | dąb |  |
| 1.07 | Pralnia z suszarnią | wielobok (11,895; 8,295) (11,895; 4,905) (8,530; 4,905) (8,530; 7,900) (8,900; 7,900) (8,900; 8,295) | 11,26 | pomocnicza | nie | gres |  |

**Suma PU P1 (bez garażu): 90,15 m²**.

### 3.6 II PIĘTRO P2 (+6,30)

**Ściany**

| ID | oś warstwy konstr. (x; y) [m] | dł. osi | typ | grub. całk. | uwagi |
|---|---|---|---|---|---|
| S2-01 | (-1,000; 0,000) → (12,000; 0,000) | 13,00 | SZ1 | 0,405 | ściana pd. bryły A; odc. x -1,0...2,0 żelbetowa ściana-tarcza |
| S2-02 | (12,000; 0,000) → (12,000; 4,800) | 4,80 | SZ1 | 0,405 | ściana wsch. |
| S2-03 | (12,000; 4,800) → (8,425; 4,800) | 3,57 | SZ1 | 0,405 | ściana pn. bryły A (nad dachem P1) |
| S2-04 | (8,425; 4,800) → (8,425; 8,400) | 3,60 | SZ1 | 0,405 | nadbudowa klatki/łazienki - ściana wsch. |
| S2-05 | (8,425; 8,400) → (3,875; 8,400) | 4,55 | SZ1 | 0,405 | nadbudowa - ściana pn. |
| S2-06 | (3,875; 8,400) → (3,875; 4,800) | 3,60 | SZ1 | 0,405 | nadbudowa - ściana zach. |
| S2-07 | (3,875; 4,800) → (-1,000; 4,800) | 4,88 | SZ1 | 0,405 | ściana pn. bryły A; odc. x -1,0...2,0 żelbetowa ściana-tarcza |
| S2-08 | (-1,000; 4,800) → (-1,000; 0,000) | 4,80 | SZL | 0,405 | ściana zach. na wsporniku 1,0 m (lekka) |
| S2-09 | (3,875; 4,800) → (8,425; 4,800) | 4,55 | SW18 | 0,210 | oś 3 wewn. |
| S2-10 | (6,095; 4,800) → (6,095; 8,400) | 3,60 | SW18 | 0,210 | oś C |
| S2-11 | (7,260; 4,800) → (7,260; 7,145) | 2,34 | SC12 | 0,120 | ścianka środkowa schodów |
| S2-12 | (3,675; 0,000) → (3,675; 4,800) | 4,80 | DZ12 | 0,150 | działowa |
| S2-13 | (6,125; 0,000) → (6,125; 4,800) | 4,80 | DZ12 | 0,150 | działowa |
| S2-14 | (8,395; 0,000) → (8,395; 4,800) | 4,80 | DZ12 | 0,150 | działowa |
| S2-15 | (6,125; 2,725) → (8,395; 2,725) | 2,27 | DZ12 | 0,150 | działowa |

**Otwory** (położenie wzdłuż osi ściany; szerokość i wysokość w świetle muru; parapet względem posadzki kondygnacji)

| ID | ściana | położenie | szer. | wys. | parapet | typ | symbol | otwieranie | uwagi |
|---|---|---|---|---|---|---|---|---|---|
| O2-01 | S2-01 | x 0,20…3,20 | 3,00 | 2,00 | 0,60 | okno | OP1 |  | sypialnia; za lamelami; dolna część stała do 0,85; skrzydła do wewnątrz (K-16) |
| O2-02 | S2-01 | x 4,30…5,50 | 1,20 | 1,75 | 0,85 | okno | OP2 |  | garderoba; za lamelami |
| O2-03 | S2-01 | x 8,90…11,30 | 2,40 | 2,00 | 0,60 | okno | OP1 |  | gabinet; za lamelami |
| O2-04 | S2-02 | y 1,80…3,00 | 1,20 | 1,75 | 0,85 | okno | OP2 |  | gabinet - wschod |
| O2-05 | S2-05 | x 6,40…8,10 | 1,70 | 1,50 | 0,90 | okno | ON3 |  | okno nad klatka schodówa (północ) |
| O2-06 | S2-05 | x 4,30…5,20 | 0,90 | 0,80 | 1,50 | okno | ON1 |  | łazienka rodziców |
| O2-07 | S2-08 | y 1,20…3,60 | 2,40 | 2,00 | 0,60 | okno | OP1 |  | sypialnia - zachod |
| O2-08 | S2-09 | x 4,20…5,00 | 0,80 | 2,05 | 0,00 | drzwi | D2 | zawias a, na -y | łazienka rodziców (na zewnątrz) |
| O2-09 | S2-09 | x 7,32…8,32 | 1,00 | 2,40 | 0,00 | otwor |  |  | wyjście z biegu 2 schodów |
| O2-10 | S2-12 | y 3,40…4,20 | 0,80 | 2,05 | 0,00 | drzwi | D1 | zawias b, na -x | sypialnia |
| O2-11 | S2-13 | y 3,30…4,10 | 0,80 | 2,05 | 0,00 | drzwi | D1 | zawias b, na -x | garderoba (wejście do apartamentu) |
| O2-12 | S2-14 | y 3,30…4,20 | 0,90 | 2,05 | 0,00 | drzwi | D1 | zawias b, na +x | gabinet |
| O2-13 | S2-15 | x 6,60…7,40 | 0,80 | 2,05 | 0,00 | drzwi | D3 | zawias a, na -y | pom. techniczne (rekuperator, wyłaz na dach) |

**Pomieszczenia**

| nr | pomieszczenie | geometria (lica wykończone) | pow. netto [m²] | kategoria | pobyt ludzi | posadzka | uwagi |
|---|---|---|---|---|---|---|---|
| 2.01 | Hol | prost. x 6,200…8,320; y 2,800…4,695 | 4,02 | ruchu | nie | dąb |  |
| 2.02 | Sypialnia rodziców | prost. x -0,895…3,600; y 0,105…4,695 | 20,63 | podstawowa | tak | dąb |  |
| 2.03 | Garderoba | prost. x 3,750…6,050; y 0,105…4,695 | 10,56 | pomocnicza | nie | dąb |  |
| 2.04 | Łazienka rodziców | wielobok (3,980; 4,905) (3,980; 8,295) (5,990; 8,295) (5,990; 5,605) (5,590; 5,605) (5,590; 4,905) | 6,53 | pomocnicza | nie | gres |  |
| 2.05 | Gabinet | prost. x 8,470…11,895; y 0,105…4,695 | 15,72 | podstawowa | tak | dąb |  |
| 2.06 | Pom. techn. (reku + wyłaz) | prost. x 6,200…8,320; y 0,105…2,650 | 5,40 | techniczna | nie | gres | klapa 0,9x0,9 + drabina (K-20, K-21) |

**Suma PU P2 (bez garażu): 62,86 m²**.

### 3.7 Elementy zewnętrzne: płyty, rama C, lamele, słupy

| ID | opis | rzut | z [m] | łącznik termoizol. |
|---|---|---|---|---|
| E-okap | ST1: okap pd. strefy dziennej (linia E) - wysunięcie 1,00 m | prost. x -1,800…12,600; y -1,300…-0,300 | 2,75…3,05 | tak |
| E-okap-W | ST1: okap zach. - wysunięcie 1,50 m | prost. x -1,800…-0,300; y -0,300…4,800 | 2,75…3,05 | tak |
| daszek | ST1: daszek nad wejściem 2,80 x 1,30 m (K-12) | prost. x 9,500…12,300; y 8,700…10,000 | 2,80…3,05 | tak |
| C-dol | rama C - płyta dolna (linia D) wysunięcie 1,00 m | prost. x 3,600…12,600; y -1,300…-0,300 | 3,65…3,85 | tak |
| C-gora | rama C - płyta górna wysunięcie 1,00 m | prost. x 3,600…12,600; y -1,300…-0,300 | 5,35…5,55 | tak |
| ST2-okap | ST2: krawędź pd. + zach. (spód bryły A) - wysunięcie 1,00 / 1,10 m | wielobok (12,600; -0,300) (12,600; -1,300) (-2,400; -1,300) (-2,400; -0,300) (-2,400; 5,100) (-1,300; 5,100) (-1,300; -0,300) | 5,95…6,25 | tak |
| ST3-okap | ST3: stropodach bryły A - wysunięcie pd. 1,00, zach. 1,10, wsch. 0,30 m | wielobok (12,600; -1,300) (-2,400; -1,300) (-2,400; -0,300) (-2,400; 5,100) (-1,300; 5,100) (-1,300; -0,300) (12,300; -0,300) (12,300; 5,100) (12,600; 5,100) (12,600; -0,300) | 9,10…9,42 | tak |

* **Rama C.** Boki ramy to pionowe płaskowniki stalowe w okładzinie 0,15 × 1,00 m, na x 3,60–3,75 i 12,45–12,60, na wysokości +3,85…+5,35. Płyty ramy są żelbetowe, gr. 20 cm, wysunięte 1,00 m na łącznikach termoizolacyjnych:
  * płyta dolna (linia D) wysunięta z belki B1;
  * płyta górna wysunięta z belki B2.
* **Lamele A:** pionowe, 40 × 80 mm co 0,12 m, x -1,30…12,30, z +6,15…+9,10, w płaszczyźnie y = -0,45 (15 cm przed licem). Materiał: drewno termo / aluminium drewnopodobne. Przed oknami P2 pracują jako stała osłona (prywatność, cień latem). Okna P2 otwierają się do wewnątrz (K-16).
* **Słupy SL1–SL4** (fasada E, x = 2,58 / 4,86 / 7,14 / 9,42; y = 0): RK 120 × 120 × 8, S355, w szprosach. **Słupki SLC1–SLC2** (boks C, x = 6,433 / 8,767): RK 100 × 100 × 6.

### 3.8 Schody SCH1 (P0→P1) i SCH2 (P1→P2): dwubiegowe, identyczne, jedne nad drugimi
| parametr | wartość | wymaganie |
|---|---|---|
| liczba podnóżków na kondygnację | 18 × 0,175 = 3,15 m | h ≤ 0,19 (WT § 68, K-01); cel ≈ 0,175 |
| szerokość stopnia s | 0,28 | cel ≈ 0,28 |
| 2h + s | 0,630 | 0,60–0,65 (WT § 69 ust. 4, K-06) ✓ |
| biegi | 2 × 9 podnóżków (8 stopni + wyjście), dł. rzutu biegu 2,24 m, nachylenie 32,0° | limit 17 stopni nie dotyczy domu jednorodzinnego (K-05) |
| szerokość biegu | 1,00 m (między ścianą a ścianką środkową 12 cm) | ≥ 0,80 (K-01); cel ≥ 1,00 ✓ |
| spocznik międzypiętrowy | 2,12 × 1,15 m, rzędne +1,575 i +4,725 | ≥ szer. biegu (1,00) ✓ |
| bieg 1 (pas W) | x 6,20–7,20; od y 4,905 (lico ściany osi 3) w górę ku północy do y 7,145 |  |
| bieg 2 (pas E) | x 7,32–8,32; od spocznika y 7,145 w górę ku południu, wyjście na y 4,905 |  |
| ścianka środkowa | silikat 12 cm, x 7,20–7,32, y 4,905–7,145, P0–P2 | zamiast balustrady: brak otwartej krawędzi, pochwyty przyścienne ≥ 0,05 m od ściany (K-11) |
| prześwit nad biegiem | 2,76 m (3,15 − h − płyta biegu 0,18/cos α) | ≥ 2,00 (dobra praktyka, K-22) ✓ |
| otwarcie w stropach | ST1 i ST2: x 6,20–8,32 × y 4,905–8,295; ST3 nad nadbudową: świetlik 1,70 × 2,90 (≤ +9,80) |  |
| P2 | bieg 1 SCH2 zamknięty od holu ścianą osi 3; wyjście z biegu 2 przez otwór 1,00 m (x 7,32–8,32) | balustrady niepotrzebne (brak krawędzi > 0,5 m) |

Pod biegiem 2 na P0 jest schowek 0.05 (dostęp z jadalni). Wysokość: ≈ 2,77 m przy ścianie osi 3, ≈ 1,37 m przy spoczniku.

## 4. Koncepcja konstrukcji

**System.** Ściany murowe z bloczków silikatowych 18 cm (kl. 20) na zaprawie cienkowarstwowej. Stropy żelbetowe monolityczne C25/30, B500SP. Posadowienie bezpośrednie na ławach, w gruncie z piasków średnich (I_D ≈ 0,6), w I kategorii geotechnicznej. Obciążenia: śnieg strefa 2 (s_k = 0,9 kN/m²), wiatr strefa 1, kat. terenu III (brief, R5).

**Ściany nośne w pionie.** Nie ma ścian odsadzonych na stropie.
* **Oś A:** P0 i P1.
* **Oś E:** P0 do P2.
* **Oś 3 (grzbietowa):** P0 do P2.
* **Oś 4 (pn.):** P0 i P1, na P2 w nadbudowie.
* **Osie B, C, D:** P0 i P1 w strefie pn., na P2 w nadbudowie klatki i łazienki.
* **Oś 1 (pd.):** P1 i P2, na belce B1.
* **Garaż:** osie E, F, 1, 5.

Ściany działowe na stropach mają 12 cm (silikat). Ich obciążenie przyjęto zastępczo ~1,2 kN/m².

**Kierunki pracy i rozpiętości płyt**
| płyta | kierunek / podpory | rozpiętości [m] | wysunięcia i uwagi |
|---|---|---|---|
| ST1 (nad P0), 20 cm | N–S, ciągła 2-przęsłowa: oś 1 (belka B1) – oś 3 – oś 4 | 4,80 / 3,60 | okap pd. 1,00; zach. 1,50; daszek pn. 1,30 |
| ST1-G (nad garażem i strefą gosp.), 24 cm | E–W: oś E – oś F | 6,40 | attyka +3,85; dach zielony ekstensywny |
| ST2 (nad P1), 20 cm | N–S: oś 1 (belka B2 / ściana) – oś 3 – oś 4 | 4,80 / 3,60 | okap pd. 1,00; zach. 2,40 od osi A (patrz wspornik A) |
| ST3 (stropodach P2), 22 cm | N–S: oś 1 – oś 3; nadbudowa: oś 3 – oś 4 | 4,80 / 3,60 | okap pd. 1,00; zach. 1,10 od lica A; wsch. 0,30 |
| Płyty spocznikowe / biegi, 18 cm | między ścianami C, D i ścianką środkową | 2,12 / 2,24 | oparte na ścianach klatki |

**Belki i słupy**
* **B1: podciąg fasady E** (oś 1, x 0,00–12,00). Wymiary 25 × 105 cm (+2,80…+3,85), belka odwrócona. Jej część nad stropem tworzy pas podokienny boksu C.
  * Podpory: słupy SL1–SL4 oraz narożniki ścian A i E. Pięć przęseł po ≈ 2,28 m.
  * Przenosi ściany pd. P1 i P2 (w tym reakcje B2), pas stropów ST1–ST3 szer. ≈ 2,4 m oraz płytę dolną ramy C.
  * Obciążenie orientacyjne ≈ 65 kN/m. Reakcja słupa ≈ 160 kN.
  * Słupy stalowe RK 120 × 120 × 8, h = 2,80 m. Stopy pod słupami 1,0 × 1,0 m są wpisane w ławę osi 1.
* **B2: nadproże boksu C.** Wymiary 25 × 80 cm (+5,35…+6,15, razem z ST2). Trzy przęsła po 2,33 m, oparte na ścianach i słupkach SLC1–SLC2 w szprosach. Z B2 wysunięta jest płyta górna ramy C.
* **B3: belka krawędziowa ST2 w osi A'.** Wymiary 25 × 40 cm, x = −1,0, y 0…4,8. Rozpiętość 4,80 m między końcami ścian-tarcz. Niesie lekką ścianę zach. P2 i wspornik płyty 1,10 m.
* **B4: nadproże bramy garażu.** Wymiary 25 × 50 cm, rozpiętość ≈ 5,30 m, w ścianie osi 5 (pas +2,25…+2,76 + attyka).
* **B5: nadproża w ścianie grzbietowej** nad otworem klatki (2,12 m na P1, 1,00 m na P0 i P2) oraz nad otworem holu P0 (1,40 m). Wymiary 25 × 25 cm.

**Wsporniki: długości i sposób przeniesienia**
1. **Bryła A: 1,00 m w osi (1,30 m do lica) na zachód.**
   * Ściany P2 w osiach 1 i 3 na odcinku x −1,00…+2,00 mają rdzeń **żelbetowy 18 cm**, czyli ściany-tarcze o wysokości kondygnacji 2,95 m. Są zespolone ze stropem ST2 (dół) i stropodachem ST3 (góra), więc tworzą belki-ściany wysokie.
   * Tarcze wspierają się na narożnikach ścian P1: A/1 i A/3. Moment równoważy przęsło zaplecza 2,0 m, dociążone ścianami i stropami P2.
   * Ściana zach. P2 (oś A') jest **lekka**: szkielet z wełną 20 cm, ≤ 1,0 kN/m², z dużym oknem. Stoi na belce B3.
   * Stosunek wspornika do wysokości tarczy ≈ 1 : 2,3, więc ugięcia są pomijalne. **Nie ma ciężkiej ściany murowanej na wsporniku.**
2. **Płyty-okapy.** Wysunięcia pracują jako wsporniki płyt z łącznikami termoizolacyjnymi (typu K, izolacja 8–12 cm w płaszczyźnie ocieplenia):
   * ST1: 1,00 m (pd.), 1,50 m (zach.), daszek wejścia 1,30 m (pn.);
   * ST2: 1,00 m (pd.), 1,10 m (zach., z belki B3);
   * ST3: 1,00 m (pd.), 1,10 m (zach.), 0,30 m (wsch.).

   Wszystkie wysunięcia ≤ 1,50 m. Obciążenie to ciężar własny, warstwy i śnieg, bez obciążeń użytkowych, bo płyty nie są tarasami.
3. **Rama C.** Płyty 1,00 m z łącznikami, wysunięte z B1 (dół) i B2 (góra). Boki stalowe spinają obie płyty (tłumienie drgań, stężenie krawędzi).
4. **Linia D nad garażem.** To attyka stropu garażu w licu ściany, bez wspornika.

**Usztywnienie.** Budynek usztywniają ściany w obu kierunkach:
* w kierunku y: osie A, B, C, D, E, F;
* w kierunku x: osie 3, 4, 5, 2 oraz ściany pd. P1 i P2.

Tarczami poziomymi są stropy monolityczne. Fasada pd. P0 jest przeszklona, więc siły poziome w kierunku x na P0 przejmują ściany osi 3 i 4 oraz sztywny rdzeń klatki C–D. Mimośród sztywności trzeba sprawdzić w PT (P0: rama B1 + słupy jako dodatkowa rama).

**Fundamenty.** Ławy ŻB 60 × 35 cm pod wszystkimi ścianami nośnymi. Pod słupami SL1–SL4 ława osi 1 jest poszerzona do 1,00 m. Płyta posadzki garażu ma 15 cm i spadek 1,5 % do bramy (B-25).

## 5. Instalacje (założenia wariantu)
* **Piony mokre.**
  * **SI** (0,40 × 0,70 m): kanalizacja K1 Ø110 z odpowietrzeniem nad dach P2 oraz kanały nawiewno-wywiewne rekuperacji. Łazienki 0.08, 1.05 i 2.04 leżą jedna nad drugą (x 3,98–5,99). Ich misy WC przylegają do SI, więc podejścia mają ≤ 1,5 m.
  * **K2** (Ø110/75): pralnia 1.07 i WC 0.03, x 8,53–8,90, y 7,90–8,30. Odpowietrzenie przez dach P1.
  * Kuchnia i przedsionek odprowadzają ścieki podejściami w posadzce P0.
  * Wyjście kanalizacji ścianą pn. w osi x = 5,00. Studzienka rewizyjna na działce, przykanalik ≈ 8 m.
* **Pom. techniczne 0.12** (6,56 m², P0):
  * jednostka wewnętrzna pompy ciepła split, zasobnik CWU 300 l, bufor, rozdzielacze ogrzewania podłogowego;
  * rozdzielnica główna RG, wodomierz i zawór antyskażeniowy.

  Jednostka zewnętrzna PC stoi przy ścianie wsch. garażu, 3,80 m od granicy, z dala od sypialni.
* **Rekuperacja.** Centrala w pom. 2.06 na P2 (obok wyłazu na dach), czerpnia i wyrzutnia przez dach. Rozprowadzenie:
  * na P2 w suficie podwieszonym holu i garderoby;
  * pionowo w szachcie SI;
  * na P1 i P0 w stropach/sufitach holu i łazienek.
* **PV** ≤ 6,5 kWp na dachu P2 (≈ 80 m² netto), stelaże niskie E–W ≤ +9,80 (nie wyżej niż attyka).
* **Deszczówka.** Stropodach P2 odwadniają rzygacze na dach P1. Dach P1 (część pn.) ma wpusty i rury spustowe na elewacji pn. Woda płynie do zbiornika 6 m³ (podlewanie), a jego przelew do skrzynek rozsączających ≈ 5,5 m³. Dach zielony garażu ma wpust i rurę w narożu NE.
* **Wyjście na dach:** klapa 0,90 × 0,90 m w stropodachu nad pom. 2.06, z drabiną wg § 101 (K-20, K-21).

## 6. Zagospodarowanie działki
Działka 32,00 × 50,00 m (1600 m²). W układzie budynku granice to:
* zach. x = -7,60;
* wsch. x = 24,40;
* pn. (linia rozgraniczająca ul. Lipowej, 1KDD) y = 17,30;
* pd. y = -32,70.

Nieprzekraczalna linia zabudowy biegnie w y = 11,30, czyli 6,00 m od drogi. Budynek jest przesunięty na północ, dzięki czemu od południa zostaje ogród o głębokości ≈ 28 m.

| strona | element | odległość [m] | wymaganie [m] | ocena |
|---|---|---|---|---|
| W | ściana zach. P0/P1 (lico ocieplenia, okna) | 7,30 | 4,00 | ✓ |
| W | ściana zach. P2 na wsporniku (okno) | 6,30 | 4,00 | ✓ |
| W | okap ST1 zach. (1,50 m) | 5,80 | 1,50 | ✓ |
| W | płyty ST2/ST3 (krawędź zach.) | 5,20 | 1,50 | ✓ |
| W | taras ogrodowy | 5,80 | 1,50 | ✓ |
| E | ściana wsch. garażu (drzwi boczne) | 5,70 | 4,00 | ✓ |
| E | ściana wsch. brył B i A (okna) | 12,10 | 4,00 | ✓ |
| E | rama C / okapy (krawędź wsch.) | 11,80 | 1,50 | ✓ |
| E | jednostka zewn. pompy ciepła | 3,80 | 3,00 | ✓ |
| E | miejsce gościnne P2 (niezadaszone, WT §19 ust. 2) | 6,30 | 3,00 | ✓ |
| W | miejsce gościnne P1 (niezadaszone) | 20,50 | 3,00 | ✓ |
| N | ściana pn. garażu (brama) — do linii rozgraniczającej drogi | 8,00 | 6,00 | ✓ |
| N | ściana pn. części mieszkalnej (drzwi wejściowe) | 8,60 | 6,00 | ✓ |
| N | daszek nad wejściem (najbardziej wysunięty element) | 7,30 | 6,00 | ✓ |
| S | ściany pd. (przeszklenie E) | 32,40 | 4,00 | ✓ |
| S | okapy pd. (ST1/ST2/ST3, rama C) | 31,40 | 1,50 | ✓ |
| S | taras | 28,40 | 1,50 | ✓ |

Wymagania (WT § 12 ust. 1 i 6, § 19, MPZP):
* ściany z otworami ≥ 4,0 m od granicy;
* okapy i płyty ≥ 1,5 m, tu utrzymane ≥ 4,0 m dla bezpieczeństwa;
* każdy uskok elewacji sprawdzony osobno;
* od strony drogi obowiązuje linia zabudowy. Nie przekracza jej żaden element, także daszek, który jest 1,30 m za linią.

* **Dojazd i parkowanie.**
  * Brama przesuwna 5,60 m (odjazd na wschód, wewnątrz działki, § 42) i furtka 1,00 m.
  * Podjazd x 12,30–18,70 (6,40 m) prowadzi do bramy garażu, 8,00 m.
  * **2 miejsca gościnne** 2,5 × 5,0 m, niezadaszone, na podjeździe przed garażem.
  * Razem z garażem jest **4 stanowiska** (MPZP ≥ 2).
* **Dojście** szer. 2,50 m od furtki do zadaszonego wejścia. Daszek 2,80 × 1,30 m spełnia K-12: szerokość ≥ drzwi + 1,0, wysięg ≥ 1,0.
* **Taras ogrodowy** −0,05, 61,7 m², w kształcie litery L. Zajmuje pas pd. przed przeszkleniem E pod okapem 1,00 m oraz pas zach. pod okapem 1,50 m. Wyjście na taras zapewniają drzwi HS salonu i jadalni. Drzwi gospodarcze przedsionka prowadzą na taras i ogród.
* **Odpady.** Osłona na 4 pojemniki stoi w linii ogrodzenia przy furtce, z drzwiczkami od ulicy. WT § 23 ust. 4: w zabudowie jednorodzinnej odległości od okien i granicy się nie określa (R3 Z-10, R8-25).
* **Retencja.** Zbiornik 6 m³ i skrzynki rozsączające stoją w ogródku frontowym. Są ≥ 5 m od budynku i ≥ 2 m od granic. Wody gruntowe ≈ 3,8 m p.p.t., więc rozsączanie jest możliwe. Powierzchni nad skrzynkami nie wliczono do PBC.
* **Przyłącza z ul. Lipowej.**
  * woda PE 40, wodomierz w pom. 0.12, ≈ 18 m;
  * kanalizacja PVC 160 ze studzienką, ≈ 14 m;
  * złącze ZK we wnęce ogrodzenia przy furtce, WLZ do RG;
  * światłowód;
  * gazu nie przyłącza się (dom all-electric).
* **Zieleń.** Żywopłoty izolacyjne wzdłuż granic E, W i S. Drzewa liściaste w ogrodzie: od zachodu cień letni, zimą przepuszczają słońce. Ogrodzenie od drogi ażurowe, h = 1,50 m (≤ 1,60, MPZP).

| wskaźnik (MPZP 3MN) | W2 | limit | ocena |
|---|---|---|---|
| powierzchnia zabudowy (lica ścian, upzp art. 2 pkt 35) | 180,60 m² (11,3 %) | ≤ 480 m² (30 %) | ✓ |
| jw., wariant kontrolny z płytami, okapami, ramą C, daszkiem | 204,82 m² (12,8 %) | ≤ 480 m² | ✓ |
| utwardzenia (podjazd, dojście, taras, ścieżka, osłony, skrzynki) | 150,60 m² | — |  |
| PBC (bez dachu zielonego i bez terenu nad skrzynkami) | 1268,80 m² (79,3 %) | ≥ 800 m² (50 %) | ✓ |
| rezerwa: 50 % dachu zielonego garażu | +25,92 m² | — |  |
| suma pow. kondygnacji nadziemnych (obrys zewn.) | 380,58 m² | 80…1280 m² | ✓ |
| intensywność nadziemna | 0,238 | 0,05–0,80 | ✓ |
| wysokość zabudowy (upzp art. 2 pkt 30) | 10,05 m | ≤ 11,00 m | ✓ |
| liczba kondygnacji nadziemnych | 3 | ≤ 3 | ✓ |
| miejsca postojowe | 2 garaż + 2 gościnne | ≥ 2 | ✓ |

## 7. Orientacja, doświetlenie, energia
* **Strefa dzienna** jest na południe: 11,40 m przeszklenia w 5 kwaterach, h = 2,75 m. Latem w południe (wysokość słońca ≈ 61°) okap 1,00 m zacienia górne ≈ 1,8 m przeszklenia; resztę osłaniają rolety screen ZIP. Zimą (≈ 14°) słońce wpada na całą głębokość strefy dziennej 4,6 m.
* **Okno zach. salonu** jest pod okapem 1,50 m. Osłony zewnętrzne: rolety screen ZIP na przeszkleniach pd. i zach.
* **Boks C** (P1, pd.) ma ramę wysuniętą 1,00 m, która działa jak łamacz światła nad oknem wys. 1,50 m.
* **Sypialnie.**
  * Rodziców i gabinet (P2) mają lamele pd. i okna zach./wsch.
  * Pokoje dzieci są od zachodu i spełniają § 60: ≥ 3 h słońca w równonoc. Okno ma parapet +4,00, a płyta ST2 wystaje 2,10 m nad nadprożem +5,50, co daje kąt odcięcia 43° (> 37,6° maks. wysokości słońca w równonoc).
  * Pokój gościnny jest od zachodu.
* **Północ** ma minimalne przeszklenia:
  * drzwi wejściowe;
  * dwa okna-szczeliny 1,20 × 0,60 i 0,90 × 0,60 m na P1;
  * okna łazienki i klatki w nadbudowie P2.

  Od północy są też komunikacja, łazienki, WC, pralnia i garaż jako bufor.
* **Zwartość.** Trzon mieszkalny 12,6 × 9,0 m i bryła A 13,6 × 5,4 m bez dodatkowych uskoków. Garaż i strefa gospodarcza są częściowo ogrzewane i buforują od wschodu. Ściana dom/garaż ma U ≈ 0,28 W/(m²K) (≤ 0,30).
* **§ 13 (przesłanianie).** Okna P0 i P1 nie mają przesłon w kącie 60°:
  * attyka garażu +3,85 leży poniżej parapetu okna wsch. P1 (+4,00);
  * boki ramy C mają 0,15 m.

  Lamele A traktuje się jako osłonę okna, nie jako obiekt przesłaniający. Wymaga to potwierdzenia w PAB (ryzyko).

## 8. Tabela kontrolna
**Powierzchnie pokoi a minima programowe** (brief; ≥ 8 / ≥ 16 m² to wymagania programowe, nie WT, zob. R3 B-19)

| pomieszczenie | pow. | minimum | ocena |
|---|---|---|---|
| 0.06 Salon + jadalnia + kuchnia | 54,12 m² | ≥ 50,00 m² | ✓ |
| 0.09 Pokój gościnny / gabinet | 12,42 m² | ≥ 8,00 m² | ✓ |
| 0.12 Pomieszczenie techniczne | 6,56 m² | ≥ 6,00 m² | ✓ |
| 1.02 Pokój rodzinny / biblioteka (boks C) | 31,90 m² | ≥ 16,00 m² | ✓ |
| 1.03 Pokój dziecka 1 | 12,54 m² | ≥ 12,00 m² | ✓ |
| 1.04 Pokój dziecka 2 | 12,42 m² | ≥ 12,00 m² | ✓ |
| 2.02 Sypialnia rodziców | 20,63 m² | ≥ 14,00 m² | ✓ |
| 2.05 Gabinet | 15,72 m² | ≥ 8,00 m² | ✓ |

**Doświetlenie** (okna w świetle ościeżnic ≥ 1/8 pow. podłogi, WT § 57 ust. 2, B-04). Ościeżnice przyjęto 7 cm z każdej strony, szprosy 10 cm.

| pomieszczenie | pow. [m²] | okna | A okien [m²] | wymagane 1/8 [m²] | stosunek | ocena |
|---|---|---|---|---|---|---|
| 0.06 Salon + jadalnia + kuchnia | 54,12 | O0-01, O0-02 | 32,89 | 6,76 | 1 : 1,6 | ✓ |
| 0.09 Pokój gościnny / gabinet | 12,42 | O0-03 | 2,26 | 1,55 | 1 : 5,5 | ✓ |
| 1.02 Pokój rodzinny / biblioteka (boks C) | 31,90 | O1-01, O1-02 | 10,50 | 3,99 | 1 : 3,0 | ✓ |
| 1.03 Pokój dziecka 1 | 12,54 | O1-06 | 2,26 | 1,57 | 1 : 5,6 | ✓ |
| 1.04 Pokój dziecka 2 | 12,42 | O1-05 | 2,26 | 1,55 | 1 : 5,5 | ✓ |
| 2.02 Sypialnia rodziców | 20,63 | O2-01, O2-07 | 9,52 | 2,58 | 1 : 2,2 | ✓ |
| 2.05 Gabinet | 15,72 | O2-03, O2-04 | 5,91 | 1,97 | 1 : 2,7 | ✓ |

Kuchnia ma okno: jest częścią 0.06, przy kwaterze 5 przeszklenia E. Łazienki i WC mają wentylację mechaniczną.

**Pozostałe kontrole**

| kontrola | W2 | wymaganie | ocena |
|---|---|---|---|
| wysokość w świetle pokoi P0/P1/P2 | 2,80 m | ≥ 2,50 (§ 72); cel 2,70–2,80 | ✓ |
| wysokość łazienek / pomocniczych | 2,80 m (≥ 2,50 pod sufitem podwieszonym) | ≥ 2,20 (§ 77 ust. 3, went. mech.) | ✓ |
| garaż: w świetle / brama | 6,08 × 6,08 m, h = 2,86 m; brama 5,00 × 2,25 m | ≥ 5,60 × 6,00; h ≥ 2,20; brama ≥ 2,30 × 2,00 (§ 102, § 104) | ✓ |
| pom. techniczne P0 | 6,56 m² | ≥ 6 m² (brief) | ✓ |
| schody: h / s / 2h+s | 0,175 / 0,28 / 0,630 | ≤ 0,19 / — / 0,60–0,65 | ✓ |
| schody: bieg / spocznik | 1,00 / 1,15 m | ≥ 0,80 (cel 1,00) / ≥ szer. biegu | ✓ |
| schody: prześwit nad biegiem | 2,76 m | ≥ 2,00 | ✓ |
| drzwi wejściowe | 1,10 × 2,40 (w świetle ościeżnicy ≈ 0,96 × 2,33) | ≥ 0,90 × 2,00, próg ≤ 2 cm (§ 62) | ✓ |
| drzwi łazienek / WC | otwierane na zewnątrz, kratka ≥ 0,022 m² | § 79 | ✓ |
| WC gościnne | szer. 1,07 m | ≥ 0,90 (§ 83) | ✓ |
| okna P1/P2 z niskim parapetem | dolna część stała VSG do 0,85; skrzydła P2 do wewnątrz | § 299, § 301 (K-16, K-17) | ✓ |
| daszek nad wejściem | 2,80 × 1,30 m | ≥ drzwi + 1,0 × ≥ 1,0 (§ 292) | ✓ |
| najmniejsza odległość ściany z otworami od granicy | 5,70 m | ≥ 4,00 | ✓ |
| najmniejsza odległość okapu/płyty od granicy bocznej | 5,20 m | ≥ 1,50 (§ 12 ust. 6); cel ≥ 4,00 | ✓ |
| daszek / lico od linii zabudowy | 1,30 m za linią | nie przekracza | ✓ |
| pow. zabudowy | 180,60 m² (11,3 %) | ≤ 480 m² | ✓ |
| PBC | 1268,80 m² (79,3 %) | ≥ 800 m² | ✓ |
| intensywność | 0,238 | 0,05–0,80 | ✓ |
| wysokość zabudowy (upzp): attyka +9,80 − śr. terenu na obwodzie | 10,05 m (teren -0,33…-0,17, śr. -0,25) | ≤ 11,00 (rezerwa zalecana 0,30) | ✓ |
| wysokość budynku WT § 6 (do wierzchu warstw +9,60) | 9,90 m (najniższe wejście: drzwi HS salonu (pd.), teren -0,30) | grupa N ≤ 12 m | ✓ |
| PU mieszkalna (bez garażu) | 257,40 m² | 230–270 m² | ✓ |
| strefa otwarta salon + jadalnia + kuchnia | 54,12 m² | ≥ 50 m² | ✓ |

PU obejmuje schowek pod schodami 0.05 w całości (2,24 m²). Po pomniejszeniu stref o wysokości < 2,20 m byłoby to ok. −0,7 m². Powierzchni stropu nad biegami P2 (pustka) nie liczono.

## 9. Ocena wariantu

**Zalety**
1. **Najprostszy układ nośny.** Wszystkie ściany nośne stoją w pionie. Stropy są jednokierunkowe, o rozpiętości 4,80 / 3,60 m i grubości 20 cm, bez podciągów w pomieszczeniach. Jedyne elementy „transferowe” są krótkie i powtarzalne: belka B1 na 4 słupach w szprosach fasady, nadproże B2 boksu C i dwie ściany-tarcze wspornika A.
2. **Krótkie instalacje.** Jeden szacht SI obsługuje trzy łazienki ustawione jedna nad drugą, a drugi krótki pion K2 pralnię i WC. Pomieszczenie techniczne jest obok garażu i przyłączy. Centrala rekuperacji na P2 ma czerpnię i wyrzutnię prosto przez dach.
3. **Logistyka dnia codziennego.** Samochód → przedsionek gospodarczy ze spiżarnią → kuchnia to ok. 6 m. Wejście główne jest obok bramy, pod daszkiem. Drzwi gospodarcze prowadzą do ogrodu, a drzwi boczne garażu do rowerów i narzędzi ogrodowych.
4. **Zwarty rzut i umiarkowana PU.** 257,40 m² przy powierzchni zabudowy 180,60 m². Brak przewymiarowania, duże rezerwy wskaźników MPZP.
5. **Sylweta „S” czytelna.** Porównanie ze szkicem pokazuje zgodność A, B, C, D (do narożnika garażu na 19,00 m) i G. Przesunięcia i głębokie płyty (1,00–1,50 m) dają warstwowość oraz osłony przeciwsłoneczne.
6. **Klatka schodowa obudowana ścianami** (bez balustrad). Tanie wykonanie i dobra akustyka. Świetlik nad klatką doświetla wszystkie kondygnacje.

**Słabości i ryzyka**
1. Przeszklenie E ma 11,40 m zamiast ≈ 12,2 m: zaczyna się 0,4 m bardziej na zachód i kończy ok. 1,2 m wcześniej niż w szkicu. To świadoma cena ścian w pionie (oś E). Kompensują to przeszklone drzwi gospodarcze.
2. Strefa dzienna ma głębokość 4,59 m, czyli jest wydłużona (11,8 m). Kuchnia z wyspą przy ścianie E jest wygodna, ale salon płytszy niż typowo.
3. Nadbudowa klatki i łazienki na P2 (od północy) tworzy dodatkowy fragment stropodachu i attyki. Od południa jej nie widać.
4. Pokój rodzinny P1 (31,9 m² z częścią komunikacji) jest duży jak na potrzeby. Działa jednak jako galeria/hol przy schodach.
5. Łazienka gościnna (3,91 m²) i przedpokój gościnny są minimalne. Pokój gościnny ma dostęp przez przedpokój z salonu, nie z holu.
6. Dwie płyty w jednym pasie (okap E +3,05 i płyta dolna ramy C +3,65, obie 1,00 m) dają odstęp 0,60 m. Trzeba go odwadniać i czyścić, a detal wymaga dopracowania w PT.
7. Lamele przed oknami P2 obniżają realny współczynnik światła dziennego. Wymóg formalny 1/8 jest spełniony z dużym zapasem. Trzeba potwierdzić, że lamele nie są „obiektem przesłaniającym” (§ 13).
8. Fasada pd. P0 na słupach stalowych daje mniejszą sztywność w kierunku x na parterze. Trzeba to sprawdzić w PT (rdzeń klatki C–D i ściany osi 3/4).
9. Stan prawny: WT 2002 wygasły 20.09.2026 (R3 S-01). Projekt wymaga oświadczenia z art. 102a PB i wniosku do 19.03.2028.

## 10. Pliki
* `rzut_P0.png`, `rzut_P1.png`, `rzut_P2.png`: rzuty z osiami, wymiarami, pomieszczeniami (pow. netto), otworami, schodami i szachtami.
* `elewacja_S.png`: elewacja południowa oraz szkic z nałożonym obrysem W2 (kontrola wierności).
* `przekroj.png`: przekroje A-A (x = 6,70, przez schody i boks C) i B-B (y = 2,00, przez wspornik A i garaż) z rzędnymi.
* `zagospodarowanie.png`: plan działki z granicami, drogą, linią zabudowy, odległościami, przyłączami i bilansem terenu.
* `model_W2.json`: dane modelu (osie, poziomy, ściany, otwory, pomieszczenia, płyty, schody, teren).
* `src/`:
  * `model_w2.py`: model;
  * `calc_w2.py`: obliczenia kontrolne;
  * `draw_*.py`: rysunki;
  * `make_opis.py`: ten opis.

  Odtworzenie: `cd src && for f in draw_plans draw_elev draw_sections draw_site make_opis; do python3 $f.py ..; done`.
