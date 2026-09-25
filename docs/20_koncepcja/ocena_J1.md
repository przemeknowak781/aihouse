# Ocena koncepcji W1–W3 — sędzia J1 (architekt-funkcjonalista, zgodność z przepisami)

Data: 2026-09-25. Zakres: `docs/20_koncepcja/W1`, `W2`, `W3` (opis.md + wszystkie PNG), brief v2 (`docs/00_brief_projektowy.md`, §1.2, §4, §8, §9),
rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md` (W-001…W-316, K-1…K-10). Szkic i `interpretacja_szkicu_v2.png` obejrzane;
interpretacji v1 celowo nie stosowano.

**Status W3:** wariant W3 jest kompletny i został oceniony na równi z W1 i W2 (opis.md z 02:39, 6 rysunków, `src/`). Ma jedną lukę formalną:
**nie ma pliku `model_W3.json`**, a W1 i W2 go mają. Dane W3 są tylko w skryptach `src/*.py`. Trzeba go wygenerować przed syntezą.

Soczewka J1: układ funkcjonalny, ergonomia, strefowanie, komunikacja, doświetlenie, orientacja oraz zgodność z WT/MPZP/rejestrem. Liczby
policzyłem samodzielnie z wymiarów podanych w opisach i modelach. Tam, gdzie wynik różni się od deklaracji autorów, jest to wyraźnie zaznaczone.

---

## 1. Wynik

| kryterium (waga) | W1 | W2 | W3 |
|---|---|---|---|
| A. Układ funkcjonalny i strefowanie (25) | 20 | 19 | 17 |
| B. Komunikacja i relacje (20) | 13 | 14 | 12 |
| C. Ergonomia i wymiary pomieszczeń (15) | 11 | 12 | 9 |
| D. Doświetlenie, orientacja, energia (15) | 12 | 12 | 11 |
| E. Zgodność WT / MPZP / rejestr (25) | 17 | 19 | 14 |
| **Razem (0–100)** | **73** | **76** | **63** |

**Wariant bazowy: W2.** Uzasadnienie: spełnia twarde założenia briefu z najmniejszą liczbą odstępstw. Ściany nośne stoją w pionie, stropy są
jednokierunkowe 4,80/3,60 m, łazienki P0/P1/P2 leżą w jednym pionie SI, a droga garaż → przedsionek ze spiżarnią → kuchnia ma ok. 6 m.
Wejście jest przy garażu, a wszystkie funkcje pomocnicze mieszczą się w zwartym obrysie. Główne wady W2 (stopa schodów i pokój gościnny
dostępne przez strefę dzienną) da się usunąć lokalnie, bez przebudowy układu nośnego. Do bazy należy przeszczepić elementy W1 i W3
(sekcja 5) oraz wykonać poprawki obowiązkowe (sekcja 6).

---

## 2. Własne obliczenia kontrolne (wszystkie warianty)

### 2.1 Odległości (lica z ociepleniem, WT §12, W-001…W-006)
| element | W1 | W2 | W3 | wymóg |
|---|---|---|---|---|
| ściana zach. P2 z oknami | 6,00 | 6,30 | 6,00 | ≥ 4,00 ✔ |
| płyta/okap zach. (najdalej wysunięta) | 4,80 (ST2) | 5,20 | 5,10 | ≥ 1,50 (cel 4,00) ✔ |
| ściana wsch. garażu z drzwiami | 5,80 | 5,70 | 6,00 | ≥ 4,00 ✔ |
| najbardziej wysunięty element N do linii zabudowy | daszek 0,70 za linią | daszek 1,30 za linią | daszek **0,20** za linią | nie przekraczać ✔ (W3 bez zapasu) |
| **jednostka zewn. PC do granicy** | **3,40 (E)** | **3,80 (E)** | 13,30 (E) | W-024: **≥ 6,0 m [ZAŁ]** — W1 ✘, W2 ✘, W3 ✔ |

### 2.2 Wskaźniki MPZP i wysokość
Wszystkie warianty spełniają wymagania z dużym zapasem: zabudowa 11–14 % (≤ 30 %), PBC 77–79 % (≥ 50 %), intensywność 0,24–0,25.
Wysokość wg upzp (attyka minus średni teren): W1 9,85 + 0,28 = **10,13 m**, W2 9,80 + 0,25 = **10,05 m**, W3 9,85 + 0,25 = **10,10 m**. Wszystkie
mieszczą się w limicie ≤ 10,70 m z rezerwą W-033, pod warunkiem że PV, świetliki i wyłazy nie wystają ponad attykę. Liczba kondygnacji
nadziemnych wynosi 3 (W-034/W-211) ✔.

### 2.3 PU wg RPB §20 / PN-ISO 9836 (W-316: bez schodów i podestów)
| | deklarowana | błąd | **skorygowana** |
|---|---|---|---|
| W1 | 235,09 | — (schody wyłączone poprawnie) | **235,09** |
| W2 | 257,40 | wliczona klatka 0.04 (4,68) i 1.06 (6,92) | **245,80** (dodatkowo ok. −0,7 za schowek pod biegiem < 2,20 m) |
| W3 | 262,61 | wliczona klatka 0.04 (7,04) i 1.05 (7,04) | **248,53** |
Po korekcie wszystkie warianty mieszczą się w przedziale 230–270 m², ale W2 i W3 muszą poprawić zestawienie.

### 2.4 Oświetlenie dzienne (WT §57, W-080 — w świetle ościeżnic: −0,07 m z każdej strony)
| pokój | pow. | okna netto | 1/8 | zapas |
|---|---|---|---|---|
| W1 0.07 gość | 10,82 | 1,99 | 1,35 | +47 % ✔ |
| W1 1.01 / 1.02 dzieci | 12,04 / 12,28 | 2,42 | 1,50 / 1,53 | +58–61 % ✔ |
| W2 0.09 / 1.03 / 1.04 | 12,42 / 12,54 / 12,42 | 2,26 | 1,55–1,57 | +44–46 % ✔ |
| W3 1.03 dziecko 1 | 16,60 | 2,53 | 2,08 | **+22 %** ✔ (najmniejszy zapas) |
| W3 1.02 rodzinny (tylko część boksu C przed pokojem + okno E) | 18,14 | 7,23 | 2,27 | ✔ |
| W3 P2 (za loggią 1,20 + lamelami ~67 % prześwitu + okapem 0,90) | — | formalnie ✔ | — | realny DF do symulacji |
Kuchnie w W1, W2 i W3 są częścią strefy dziennej z przeszkleniem pd., więc mają okno ✔.

### 2.5 Schody (W-090, W-091: szerokość użytkowa **między poręczami**)
| | bieg w świetle | 2 poręcze (0,05 + 0,045 z każdej strony) | 1 poręcz | spocznik | cel ≥ 1,00 |
|---|---|---|---|---|---|
| W1 | 1,09 | 0,90 | 1,00 | 1,05 × 2,29 | na granicy |
| W2 | 1,00 (ściana–ścianka 12 cm) | **0,81** | 0,91 | 1,15 × 2,12 | ✘ |
| W3 | 1,00 (+ oko 0,14) | **0,81** | 0,91 | 1,05 × 2,14 | ✘ |
Wszystkie spełniają WT (≥ 0,80, h 0,175, 2h + s = 0,63, prześwit ≥ 2,60 m). Żaden nie osiąga celu 1,00 m przy dwóch poręczach.

### 2.6 Drzwi (WT §62, §75, §79; W-055, W-058, W-059, W-062 — szerokość w świetle ościeżnicy)
Opisy podają otwory „w świetle muru”. Ościeżnica zabiera ok. 0,10 m, więc otwór 0,80 daje ok. 0,70 m w świetle ościeżnicy.
* **W1:** drzwi do pokoi dzieci, sypialni i gabinetu mają 0,80 (✘ §75), łazienki 0.08/1.05/2.03 mają 0,80 i **otwierają się do
  wewnątrz** (model: D0-04 swing −y, D1-04 +x, D2-02 +y — ✘ §79 ust. 1). Drzwi wejściowe 1,00 w murze to ok. 0,88 w świetle ościeżnicy, czyli ✘ §62 (≥ 0,90).
* **W2:** pokoje mają D1 0,90 ✔, ale łazienki i WC (O0-12, O0-14, O1-08, O2-08) oraz sypialnia O2-10 mają 0,80 → ok. 0,70 ✘ (§79/§75).
  Kierunek otwierania drzwi łazienek na zewnątrz ✔.
* **W3:** pokoje D1 0,90 ✔. Łazienki i WC (O0-13, O0-19, O1-10, O2-13) mają 0,80 → ok. 0,70 ✘ §79. Kierunek na zewnątrz ✔.
  **Drzwi WC O0-19 otwierają się w pas przedpokoju gościnnego o głębokości 0,82 m** (y 9,005–9,825), który jest jedynym dojściem do drzwi pokoju gościnnego O0-14.

### 2.7 Kuchnia i spiżarnia (program briefu: kuchnia z wyspą + spiżarnia, rodzina 4–5 os.)
| | ciąg blatów przy ścianie (bez drzwi) | wyspa | spiżarnia |
|---|---|---|---|
| W1 | ok. 4,5 m (ściana osi F bez otworów) | tak | 2,45 m² (1,07 m — wąska), wejście z kuchni |
| W2 | 2,8 m (y 1,90–4,69; drzwi do przedsionka y 1,00–1,90) | tak | 2,51 m², wejście z przedsionka |
| W3 | **ok. 1,8 m** (y 2,10–3,93; ścianę E zajmują drzwi 1,20 na patio otwierane do kuchni, od pd. jest szkło) | tak | **1,49 m²** |

### 2.8 Pompa ciepła, woda opadowa, czerpnia
* **W-155 (monoblok R290):** W2 („PC split, jedn. wewn.”) i W3 („split (R290), hydrobox”) nie są zgodne z decyzją rejestru. W1 ma zapis „monoblok/split” do rozstrzygnięcia.
* **W-156 (strefa R290 1,0 m bez okien i otworów):** w W3 okno przedsionka **O0-10 (x 10,30–11,30, parapet +1,60) jest 0,25 m za
  jednostką** (x 10,20–11,40; y 11,85–12,45) ✘. W W1 okno OK5 jest 1,30 m od jednostki ✔, w W2 w promieniu 1 m nie ma otworów ✔.
* **Brief §8 (szczelny zbiornik ≤ 5 m³ + niecka; skrzynki dopiero po stanowisku PGW WP):** W1 (6 m³ + skrzynki) ✘, W2 (6 m³ + skrzynki) ✘, W3 (5 m³ + niecka 24 m²) ✔.
* **W-166 (czerpnia ≥ 8 m od pojemników na odpady):** W3 ma czerpnię na elewacji pn. skrzydła. Pojemniki stoją w linii ogrodzenia (x 9,20–11,30),
  a elewacja pn. jest w y 11,60, więc warunek jest spełniony tylko dla x ≤ 6,0 lub x ≥ 14,5. W opisie W3 położenia czerpni nie ustalono.
  W1 i W2 mają czerpnię dachową: trzeba wykazać odległość ≥ 6 m od wywiewek pionów K1/K2 na tym samym dachu.

---

## 3. Oceny szczegółowe

### W1 — „wierność szkicowi i zwartość” — 73/100
**Mocne strony**
* Najczystsze strefowanie: pasmo pn. mieści wiatrołap, hol, garderobę, WC, sień gospodarczą, schowek i pomieszczenie techniczne 6,11 m². Pasmo środkowe to
  łazienka gościnna, trzon, spiżarnia i technika, a pasmo pd. to strefa dzienna 54,62 m² na całej elewacji.
* **Najlepsza kuchnia:** ok. 4,5 m zabudowy przy ścianie osi F bez otworów, wyspa i spiżarnia z wejściem z kuchni.
* Pom. gospodarcze 20,37 m² na rowery i sprzęt ogrodowy z drzwiami do ogrodu, a garaż jest czysty. Taras zach. zadaszony na głębokość 2,50 m.
* Dobry program P2: apartament 18,17 + 6,19 + 6,48 m², gabinet 13,11, dodatkowy pokój 12,48 (S+E) dla 5. osoby oraz rekuperator z wyłazem.
* PU policzona poprawnie (235,09 m², bez schodów). Najmniej przeszkleń od północy (ok. 4,5 m²).

**Słabości funkcjonalne**
* **Główna droga wejście → strefa dzienna prowadzi przez spocznik trzonu ŻB** (przejścia D0-05 i D0-01 po 1,20 m, spocznik 1,30 × 2,29 m).
  Wszyscy wchodzący mijają stopę biegu. Droga garaż → kuchnia ma ok. 12 m i prowadzi przez hol, spocznik i jadalnię.
* Łazienka P1 1.05 i pom. techn. P2 2.07 otwierają się bezpośrednio ze spocznika. Pokoje dzieci mają 12,04 i 12,28 m², czyli leżą na samym minimum.
* Pokój gościnny ma 10,82 m² (3,62 × 2,99). Garaż 5,68 m w świetle mieści się w minimum (5,60) bez zapasu na rowery.
* Kanalizacja pionu K2 prowadzi szachtem w narożniku pokoju dziecka 1.02, bo łazienki P0/P1/P2 nie leżą w jednym pionie.
* Ściana zach. P1 nie stoi na ścianie P0: wspornik schodkowy 2 × 1,00 m na tarczach ŻB jest odstępstwem od „ścian w pionie” (koszt, mniej okien w strefie zakotwienia).

**Niezgodności:** drzwi §75/§79/§62 (pkt 2.6), PC 3,40 m (W-024), retencja (brief §8). W boksie C siedzisko ma h = 0,55 m,
a w przeszkleniu nie określono stałej dolnej części VSG ani bariery 0,90 m ponad siedziskiem (W-097).

### W2 — „funkcja · ekonomia · konstrukcja” — 76/100
**Mocne strony**
* **Najlepsza logistyka dnia codziennego:** garaż → przedsionek 5,01 m² (spiżarnia 2,51 m² obok) → kuchnia to ok. 6 m. Wejście pod daszkiem
  2,80 × 1,30 m jest tuż przy bramie, a WC gościnne 1,07 m szerokości stoi przy wiatrołapie.
* Suite gościnna z własnym przedpokojem: łazienka z prysznicem jest dostępna bez przechodzenia przez pokój, co pasuje do scenariusza „senior”.
* Łazienki 0.08, 1.05 i 2.04 leżą dokładnie jedna nad drugą przy szachcie SI. Ściany nośne stoją w pionie, stropy są jednokierunkowe 4,80/3,60 m.
* P2: sypialnia rodziców 20,63 m² (S+W) i garderoba 10,56 m² jako przedpokój apartamentu, więc prywatność jest dobra. Garaż 6,08 × 6,08 m.
* Rzut zwarty (zabudowa 180,6 m²). Klatka obudowana ścianami nie wymaga balustrad i jest dobra akustycznie.

**Słabości funkcjonalne**
* **Stopa schodów (O0-08) i przedpokój gościnny (O0-07) otwierają się ze strefy dziennej**, nie z holu. Tylna ściana salonu, jadalni i kuchni
  (12 m) ma 4 otwory (0,90 / 1,00 / 0,80 / 1,40 m), więc pas pn. strefy dziennej działa jak korytarz. Strefa ma tylko 4,59 m głębokości.
* Program jest źle rozłożony: pralnia 11,26 m² i pokój rodzinny 31,90 m² są przewymiarowane, a łazienka dzieci ma 6,53 m², łazienka gościnna 3,91 m².
* Pomieszczenie techniczne 0.12 i przedsionek leżą od południa. Na P2 pomieszczenie techniczne 5,40 m² zajmuje fragment elewacji pd. za lamelami.
* Użyteczna szerokość biegu wynosi 0,81 m przy dwóch poręczach (pkt 2.5).

**Niezgodności:** drzwi łazienek/WC i sypialni 0,80 (§79/§75), PC 3,80 m (W-024), PC „split” (W-155), retencja 6 m³ + skrzynki
(brief §8), PU z klatką (W-316).

### W3 — „światło · ogród · sekwencja wejścia” — 63/100
**Mocne strony**
* Najlepsza sekwencja przestrzenna: oś x = 8,00, wiatrołap 6,95 m² ze świetlikiem SW2 i szklaną przegrodą, hol 10,29 m², wylot 2,60 m, jadalnia pod
  pustką 5,70–5,95 m.
* Strefa dzienna 59,31 m² jest doświetlona z S, W i E. Ma trzy wyjścia do ogrodu (taras S, taras W pod okapem 1,50, patio poranne).
* Strefa gości jest dobrze wydzielona: przedpokój, WC 1,53 m² i łazienka 5,19 m² z pokojem. Pokoje dzieci mają 16,60 i 12,63 m², łazienki P1/P2 po 9,84 m² i leżą w pionie SI.
* Rozwiązania zgodne z rejestrem, których brakuje w W1 i W2: PC 13,30 m od granicy (W-024 ✔) oraz retencja 5 m³ + niecka 24 m² (brief §8 ✔).

**Błędy krytyczne (do usunięcia przed dalszym etapem)**
1. **Strefa R290 (W-156):** okno O0-10 stoi 0,25 m za jednostką zewnętrzną PC.
2. **Loggia P2 (posadzka +6,28, ok. 6,5 m nad terenem)** jest zabezpieczona tylko ekranem lamel, a opis przewiduje „składanie paneli przesuwnych”. Po otwarciu
   paneli loggia nie ma bariery, co narusza WT §296–298 (W-094/W-095).
3. **Przedpokój gościnny 0.11 ma 0,82 m** (pas y 9,005–9,825) i **0,77 m w świetle przed szafami 0,60 m** (część y 9,825–11,195). Drzwi WC O0-19
   otwierają się w ten pas i blokują dojście do pokoju gościnnego. W tym samym przedpokoju są szafy wejściowe rodziny, więc codzienna droga prowadzi przez przesmyk 0,77 m.
4. Drzwi łazienek i WC 0,80 w murze dają ok. 0,70 m w świetle ościeżnicy (WT §79).

**Słabości funkcjonalne**
* **Kuchnia jest za mała:** ok. 1,8 m blatu przy ścianie plus wyspa. Drzwi 1,20 m na patio otwierają się do strefy roboczej, a spiżarnia ma 1,49 m².
  Dla rodziny 4–5 osób w standardzie podwyższonym to za mało.
* Stopa schodów O0-11 leży w strefie dziennej (jak w W2), 0,65 m od wylotu holu, za stołem pod pustką.
* Brudna droga garaż → przedsionek → **wiatrołap główny** → hol → kuchnia ma ok. 11 m i przecina wejście reprezentacyjne.
* Pustka nad jadalnią: pogłos, zapachy z kuchni idą na galerię i do pokoju rodzinnego nad kuchnią. **Ściana pokoju dziecka 1 od pustki to lekka ścianka GK 12,5 cm (DZL)**, więc izolacyjność akustyczna sypialni jest niewystarczająca.
* Loggia 1,20 m jest za wąska do umeblowania. Wchodzi się na nią z holu i gabinetu, a HS sypialni rodziców otwiera się na tę samą
  loggię, więc prywatność sypialni jest naruszona. Pod loggią pas 1,20 m na P1 ma 2,55 m wysokości (cel 2,70–2,80). Węzeł taras nad ogrzewanym wnętrzem
  ma rezerwę 0,38 m na warstwy przy progu HS na +6,30 (ryzyko brief §9).
* Sypialnia rodziców 15,24 m² jest mniejsza niż gabinet 19,43 m² (odwrócona hierarchia). Garderoba 1,45 m służy jako przejście i ma 0,85 m w świetle.
* Pom. techniczne 6,88 m² ma pomieścić PC, CWU 300 l, bufor 100 l, centralę MVHR, RG i wodomierz. Skrzydło drzwi O0-16 zachodzi na styk na centralę,
  a kanały czerpni i wyrzutni muszą przejść przez przedsionek.
* Zwartość jest najsłabsza: skrzydło jednokondygnacyjne, 5 pól dachowych, najwięcej przeszkleń N i zenitalnych (ON3 3,84 m² na P1, SW1, SW2).
  Garaż cofnięty o 4,80 m rozbija linię D w głąb: płyta ramy C i attyka garażu leżą w płaszczyznach oddalonych o 5,8 m.
* Przeszklenie E ma 10,85 m (szkic ≈ 12,2), najmniej z wariantów. Brak `model_W3.json`.

---

## 4. Wniosek porównawczy
* **W2** ma najlepszy szkielet funkcjonalno-techniczny: piony, logistykę, zwartość i konstrukcję zgodną z założeniami. Jego wady są lokalne.
* **W1** jest najwierniejszy szkicowi i ma najlepszą kuchnię oraz poprawnie policzoną PU. Główna droga przez spocznik, nieułożone w pionie
  łazienki i schodkowy wspornik ścian utrudniają jednak rozwój projektu.
* **W3** ma najlepsze jakości przestrzenne (wejście, światło, strefa gości) i dwa elementy zgodne z rejestrem (PC, retencja). Ma też
  2 błędy bezpieczeństwa, niewydolną kuchnię, przesmyk 0,77–0,82 m i najsłabszą zwartość, dlatego nie nadaje się na bazę.

## 5. Przeszczepy do bazy W2 (grafts)
1. **Z W3 — retencja:** szczelny zbiornik 5,0 m³ z przelewem do niecki chłonnej ok. 24 m² (głęb. 0,30 m) w ogrodzie pd., ≥ 3,0 m od fundamentów
   i ≥ 2,0 m od granic. Zamiast zbiornika 6 m³ i skrzynek w ogródku frontowym.
2. **Z W3 — ekran z lamel:** wydzielić pas komunikacyjny 1,20 × 2,60 m (x 6,20–8,80, y 3,50–4,70) łączący wylot holu 0.02 (O0-10, x 8,80–10,20)
   ze stopą schodów O0-08. Ekran lamelowy lub meblościanka h ≥ 2,10 m. Strefa dzienna po korekcie ma ok. 51 m² (≥ 50).
3. **Z W3 — przegroda szklana** wiatrołap/hol (drzwi szklane 0,90 m w osi) i doświetle boczne przy drzwiach wejściowych.
4. **Z W1 — kuchnia z ciągłą ścianą:** przesunąć drzwi przedsionek → kuchnia (O0-15) na skraj pd., y 0,25–1,15 m (≥ 0,10 m od lica ściany pd.).
   Ciąg zabudowy na ścianie osi E wyniesie wtedy 3,39 m (y 1,30–4,69) plus wyspa. Spiżarnię 0.11 zostawić przy przedsionku (2,51 m²).
5. **Z W1 — wyłączenie schodów z PU** (metoda W1) i tabela powierzchni wg RPB §20.
6. **Z W3 — lepszy rozdział programu na P1:** pralnię 1.07 zmniejszyć z 11,26 do ok. 6,5 m² (x 9,70–11,895). Uzyskane ok. 4,7 m² przeznaczyć na
   łazienkę dzieci (ok. 9 m² z wanną i prysznicem, jak W3 1.06) albo na powiększenie pokoju dziecka 2 do ≥ 14 m².
7. **Z W1 — pokój 5. osoby (opcjonalnie, rodzina 4–5 os.):** jeśli Inwestor potwierdzi 5 osób, wydzielić z pokoju rodzinnego 1.02 (31,90 m²)
   pokój ≥ 12 m² od wschodu (x 8,53–11,895 × y 0,105–3,60, ok. 11,8 m², w razie potrzeby wydłużyć). Okno OE1 powiększyć do 1,80 × 1,50 m (≥ 1/8).
   Pokój rodzinny ≥ 16 m² zostaje przed boksem C.
8. **Z W1 — pom. gospodarcze na rowery i sprzęt ogrodowy** poza torem jazdy samochodów, jeśli garaż ma pozostać 6,08 m (np. szafa 0,60 m przy
   ścianie osi F tylko w strefie przedniej kół).

## 6. Poprawki obowiązkowe (mandatory fixes)
1. **Drzwi (WT §62, §75, §79):** wszystkie drzwi do pokoi, kuchni, łazienek i WC mają mieć otwór w murze ≥ 0,90 × 2,10 m (≥ 0,80 × 2,00 m
   w świetle ościeżnicy). Łazienki i WC otwierane na zewnątrz lub przesuwne, z otworami ≥ 0,022 m². Drzwi wejściowe: otwór ≥ 1,10 × 2,15 m (≥ 0,90 × 2,00
   w świetle ościeżnicy, próg ≤ 0,02 m). W W2 dotyczy O0-12, O0-14, O1-08, O2-08 i O2-10.
2. **Schody (W-091):** szerokość użytkowa ≥ 1,00 m między poręczami. W W2 rdzeń w świetle ≥ 2,34 m (2 × 1,11 + ścianka 0,12): oś C
   przesunąć z x 6,095 na x 5,875. Łazienki pionu SI zachowują wtedy szerokość ≥ 1,75 m. Alternatywa: jedna poręcz na bieg przy ściance środkowej i bieg ≥ 1,10 m w świetle.
3. **Pompa ciepła (W-024, W-155, W-156):** monoblok R290 z modułem hydraulicznym wewnątrz, bez czynnika chłodniczego w budynku. Jednostka zewn.
   ≥ 6,0 m od granic E/W, w W2 np. przy pd. ścianie pom. techn. 0.12 (x 15,90–17,10; y −1,50…−0,90; ok. 7,3 m od granicy E).
   Strefa 1,0 m bez okien, drzwi, kratek i wpustów, ekran akustyczny od strony tarasu. Na PZT i elewacji dorysować strefę.
   Obliczyć L_Aeq,N na granicy ≤ 40 dB (cel 35 dB).
4. **Woda opadowa (brief §8):** szczelny zbiornik ≤ 5,0 m³ + niecka chłonna. Skrzynki rozsączające dopiero po stanowisku PGW WP.
5. **PU (W-316):** zestawienie bez klatek i podestów. W2: 245,80 m² (skorygować też schowek pod biegiem < 2,20 m).
6. **Czerpnia (W-166):** dachowa ≥ 0,40 m nad pokryciem i ≥ 6,0 m od wywiewek pionów K1/K2. Wykazać na rzucie dachu.
7. **Stopa schodów z holu:** w W2 zrealizować pas komunikacyjny 1,20 m z pkt 5.2. Żadna droga hol → schody nie może prowadzić przez strefę
   mebli jadalni lub salonu.
8. **Balustrady i niskie parapety (W-097):** okna P2 z parapetem 0,60 m mają mieć stałą dolną część VSG do 0,85 m. Boks C z parapetem 0,70 m ma mieć VSG do 0,85 m.
   Bez siedzisk podnoszących strefę upadku, chyba że bariera ≥ 0,90 m ponad siedzisko.
9. **Linia zabudowy:** żaden element N (daszek, osłona PC, schody) nie może przekroczyć y = linia zabudowy. Zachować ≥ 0,30 m zapasu tolerancji geodezyjnej.
10. **Model:** wygenerować jeden `model_Wx.json` zgodny ze schematem (`docs/SCHEMAT_MODELU.md`). Dotyczy także W3 przy dalszym użyciu jego elementów.

Jeżeli zespół mimo wszystko rozwija **W3**, obowiązkowe są dodatkowo:
* usunięcie okna O0-10 lub przesunięcie jednostki PC na x 3,30–4,50 przy ścianie pn. skrzydła (≥ 1,0 m od okna O0-09 i drzwi O0-05);
* stała balustrada loggii h ≥ 1,10 m niezależna od paneli lamel (lub rezygnacja z paneli ruchomych);
* pogłębienie skrzydła wejściowego z 2,40 do 3,00 m w osiach, przy przesunięciu budynku o 0,70 m na południe (daszek ≥ 0,30 m za linią zabudowy), tak aby przedpokój gościnny miał ≥ 1,20 m;
  drzwi WC przesuwne;
* drzwi patio kuchni jako HS 1,20 m na y 0,20–1,40, ciąg blatów ≥ 2,50 m na y 1,50–3,93, spiżarnia ≥ 2,50 m²;
* ściana pokoju dziecka 1 od pustki murowana SIL 12 cm lub podwójna GK na osobnych stelażach, R'w ≥ 50 dB;
* czerpnia na x ≤ 6,0 m elewacji pn. albo na dachu (W-166);
* korekta PU do 248,53 m².
