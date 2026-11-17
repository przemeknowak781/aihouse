# Weryfikacja geometrii i prawa miejscowego – koncepcja „BRAMA I LATARNIA” (synteza 1.0)

**Stan:** 17.11.2026 · **Rola:** niezależny, adwersaryjny weryfikator · **Przedmiot:** `docs/20_koncepcja/koncepcja_wybrana.md` (dalej: spec.) i `model/koncepcja.json` (dalej: JSON) wobec `model/site.json`, MPZP (`30_lokalizacja/mpzp.md`), WT (`40_prawo/wt_kluczowe.md`, `naslonecznienie_metoda.md`), sąsiadów (`30_lokalizacja/sasiedzi.md`) i drzewostanu (`30_lokalizacja/dendrologia.md`).
**Metoda:** wszystkie liczby policzono w shapely 2.2 / scipy (TIN z pikiet NMT) na danych z `site.json` i JSON. Skrypt: `docs/20_koncepcja/_weryfikacja_geometria.py` (uruchomienie z katalogu repo: `/home/user/aihouse/.venv-render/bin/python -I umwd/docs/20_koncepcja/_weryfikacja_geometria.py umwd/model/site.json umwd/model/koncepcja.json`). Układ (u, v) wieży jak w JSON (początek w narożniku SW obszaru A).
**Zasada wyłączenia:** nie korzystano z informacji o rzeczywistych pracach ani wynikach konkursu. Specyfikacji nie edytowano.

---

## 0. Zestawienie

| Nr | Waga | Problem (skrót) | Gdzie |
|---|---|---|---|
| K-1 | **KRYTYCZNY** | Gzyms-attyka z wysięgiem 0,30 m i relief filarów na licach stojących w granicy (skrzydło, dz. 8/8) lub 0,22 m od niej (segment) – nadwieszenie poza obszar (Wyj. 7 odp. 28) albo sprzeczność z traktem 15,0 m | spec. 4.1, 8; JSON `elewacje` |
| K-2 | **KRYTYCZNY** | Próg rampy +0,30 (119,60) stoi 0,22 m od granicy, a chodnik przed bramą ma 119,09: nie da się go osiągnąć na własnym terenie bez wyniesienia stropu rampy ok. 1 m ponad dziedziniec (dach < 18 m poza A – ten sam błąd co w K5, korekta (f)) albo bez garbu 0,51 m na chodniku publicznym | spec. 2 (f), 5, 9; JSON `podziemie.rampa` |
| I-1 | ISTOTNY | Pas pn. segmentu: program 56 m² (trafo, rozdzielnia, BESS, odpady) w pasie 32 m² brutto / ok. 21 m² netto; rampa 2 × 3,0 m (7,0 m ze ścianami) nie mieści się przy ścianie zach. segmentu (6,95 m) | spec. 6 (Segment), 2 (d) |
| I-2 | ISTOTNY | Drzewa: wiążący M.06 (Wyj. 13 odp. 65) – ściana −1 wchodzi w strefy korzeni drzew „zachowanych” (nr 60 Z2 o 3,96 m, nr 58 Z1 o 0,82 m, nr 78 Z1 o 0,08 m); D897 to Z1 (nr 67); „38 zachowanych (86 %)” nieudowodnione | spec. 9, 5; JSON `zagospodarowanie` |
| I-3 | ISTOTNY | Ściany szczelinowe na obwodzie −1 przebiegają po granicy z dz. 8/8 (60 m) i tuż przy szczycie Maz. 19 (15 m): murki prowadzące poza obszarem / pod odsadzką fundamentu Maz. 19 | spec. 5; JSON `siatka.posadowienie` |
| I-4 | ISTOTNY | JSON: poligon skrzydła niepoprawny (self-intersection), inny niż w tabeli 4.1 (wcięcie NE 2,66 m², pole 849,66 vs 847,00); strefy parteru skrzydła (bistro, foyer) wchodzą 31 m² w wieżę/obszar A | JSON `bryly.M`, `parter.skrzydlo` |
| I-5 | ISTOTNY (do potwierdzenia rzutem) | Pojemność elewacji „wieża pd. 6” na kond. 1–4 przy odsłoniętym licu pd. 21,0 m i deklaracji „naroża pd. zajmują szachty i WC” – deficyt 1–2 jedn./kond., rezerwa 3,2 jedn. znika | spec. 6 |
| D-1…D-12 | DROBNE | liczby § 13 i § 60, pasy styku w A, lamele korony R 14,1, odległość bramy, wrażliwość zapasu § 13, własne naroża wklęsłe, drobne niespójności | rozdz. 4 |

**Wynik ogólny:** zasadnicze ustalenia MPZP (wieża wyłącznie w A, pasma 18–25 / 35–45 m, brak zjazdu z 1KDG, § 12 przy dz. 10/2, § 13 i § 60 wobec WS 5, przyleganie do Maz. 19) **są spełnione** liczbowo (rozdz. 1). Błędy krytyczne dotyczą detalu na granicy (K-1) i rampy (K-2) – oba łatwe do usunięcia, ale w obecnym brzmieniu spec. jest wewnętrznie sprzeczna i w jednym z wariantów odczytu narusza wiążące ustalenia.

---

## 1. Kontrole spełnione (dowód liczbowy)

| Kontrola | Wynik obliczeń | Spec. | Ocena |
|---|---|---|---|
| Obrysy w obszarze inwestycji | W: poza OI 0,0000 m²; S: 0,0000; M: 0,0003 (szum numeryczny, lico na granicy) | ✔ | ✔ |
| Wieża wyłącznie w A | W poza A = 0,0000 m²; W w A 1 145,83 m² | 0,000 | ✔ |
| Skrzydło/segment w A | M ∩ A = 0,0000; S ∩ A = 0,0000; min. odstęp od linii A: M 0,049, S 0,041 m | „5–8 cm” | ✔ (patrz D-3) |
| Dachy w A < 35 m | brak, poza pasem styku (D-3: ≤ 0,51 m² obróbki) | „brak” | ✔ z uwagą |
| Pasma MPZP (teren z TIN, pas 2 m; kontrolnie skrajne rzędne OI 118,33/119,44) | W: najniższe pokrycie 36,06 m (od 119,44), najwyższe 36,87 m (37,42 od 118,33), attyka 37,62 (38,17) → 35–45 ✔. M: 20,07 / 21,34 (21,37) / attyka 21,79 (21,82) → 18–25 ✔. S: 19,92 (19,66 od 119,44) / 20,19 (20,77) / attyka 21,24 (21,82) → 18–25 ✔ | 36,06; 20,09; 19,92 | ✔ |
| Odległości od granic | W–9/2 (1KDG) 0,252; W–19/12 0,585–0,625; łuk–19/1 0,449; S–10/1 0,216; S–10/2 4,576; M–8/8 0,000; M–11/3 0,001 | zgodne (± 0,01) | ✔ |
| § 12 przy dz. 10/2 (Bz, nie drogowa) | ściana pd. segmentu bez otworów 4,576 m ≥ 3,0 m; S ∩ dz. 10/2 = 0 | 4,58 | ✔ |
| § 12 ust. 10 (lica z oknami przy działkach drogowych) | 8/8 dr, 9/2 dr, 19/12 dr, 19/1 dr, 10/1 Tp (teren 6KDB/2) | – | ✔ |
| § 12 ust. 3 – Maz. 19 | ściana pd. skrzydła 15,00 m przylega na całej długości do szczytu 15,78 m; M ∩ Maz. 19 = 0 m² | 15,0 | ✔ |
| Zjazd | brama w elewacji wsch. segmentu (v −4,1…−10,1) wychodzi na dz. 10/1 → 6KDB/2; granica 1KDG/6KDB/2 zaczyna się w narożniku (106,341; 79,307), ok. 33 m na pn. od bramy | „z 6KDB/2” | ✔ |
| § 13 – szczyt WS 5, segment (attyka 140,15) | wierzchołek w licu wewn. (mur 0,55 m), sektor ±30° od normalnej 356,7°, okno w dowolnym miejscu lica wewn. (t 0,55–15,71 m): **min. 11,129 m**; wymagane 10,075 (H od 120,0) → **zapas 1,054 m** ≥ 1 m | 11,13 / 1,05 | ✔ (patrz D-1) |
| § 13 – wieża (> 35 m) | **min. 19,000 m** (wierzchołek (102,511; 28,003)) ≥ 17,5 → zapas 1,50; okno pokoju 6/6A: 20,448 | 18,99 / 20,46 | ✔ |
| § 13 – skrzydło | poza sektorem dla każdego położenia okna | „poza sektorem” | ✔ |
| § 60 – lok. 6/6A, pokoje od ulicy (1, 2) | nasz budynek widziany z okien wsch. w az. ok. 309–355° (siatka), droga Słońca 92–259° → brak zacienienia; ok. 4,9 h (20.03, 7:00–11:50) i 5,7 h (23.09, 7:00–12:35) | 5,0 / 5,75 h | ✔ (patrz D-6) |
| § 60 – okna podwórzowe WS 5/WS 6 | po realizacji ≥ 2,4 h (WS 6) i ok. 3,8 h (WS 5) w obu dniach równonocy | ≥ 4,5 h | ✔ wniosek, liczby błędne (D-6) |
| Drzewa w obrysie | w obrysie brył tylko D701, D702 (A) – usuwane; D867, D868, D882, D897 0,32–0,46 m od lica – usuwane; 44 numery/46 pkt w OI, 29 w ogródkach | zgodne | ✔ (patrz I-2) |

---

## 2. Błędy KRYTYCZNE

### K-1. Gzyms-attyka 0,30 m i relief filarów na licach w granicy obszaru

**Stan w spec.:** 4.1 – „Skrzydło: lico zach. na granicy z dz. 8/8”, „Segment: 0,22 m od granicy wsch.”, „Żadnych nadwieszeń poza obszar. Gzymsy, attyki i lamele leżą w obrysie”; 8 – „gzyms-attyka granitowy 0,70 m (…) **wysięg 0,30 m** w obrysie”; „relief filarów 0 / 0,08 / 0,15 / 0,08 m”; 6 – trakt skrzydła „15,0 m (0,50 + 6,10 + 1,80 + 6,10 + 0,50)”.

**Dowód:** szerokość obrysu skrzydła przy Maz. 19 = 15,000 m (od (48,842; 9,683) do (63,498; 6,487)) – cały obrys jest zajęty przez trakt ze ścianami 0,50 m. Lico zach. leży na granicy dz. 8/8 (odległość 0,000 m), lico wsch. segmentu 0,216 m od granicy dz. 10/1. Wnioski:
* jeżeli lico ściany jest na granicy (jak w 4.1 i w trakcie 15,0 m), gzyms wystaje **0,30 m nad dz. 8/8** (ul. Mazowiecka), a nad dz. 10/1 i 19/12 o **0,30 − 0,216 = 0,084 m**; relief filarów M2–M4, jeżeli wysunięty, o 0,08–0,15 m. To nadwieszenie poza obszar inwestycji, zakazane przez Wyj. 7 odp. 28. Spec. sama usunęła ten błąd w K5 (korekta (a)), a teraz powtarza go w gzymsie;
* jeżeli „w obrysie” oznacza, że obrys = lico gzymsu, ściana musi być cofnięta o 0,30 m. Wtedy trakt ma 14,70 m (pokoje 5,80 m → 3,95 × 5,80 = 22,9 m² < 24 m² programu) albo korytarz spada do 1,50 m. Zdanie „lico zach. na granicy” jest wtedy fałszywe, a PZ (PN-ISO 9836 – lico ścian) maleje o ok. 17 m².

**Poprawka (do wyboru, wpisać jednoznacznie w 4.1, 8 i JSON `elewacje.skrzydlo.linie`):**
* **Wariant A (zalecany, bez zmiany współrzędnych):** na licach odległych od granicy o mniej niż 0,30 m (zach. skrzydła, wsch. segmentu) **gzyms-attyka bez wysięgu** (wysięg 0,00), z cieniem uzyskanym fryzem wklęsłym 0,15 m pod gzymsem (spód 139,45). Relief filarów M2–M4 jako **cofnięcie wypełnień** o 0,08 / 0,15 / 0,08 m względem lica filarów, a lico filarów = obrys. Wysięg 0,30 m tylko od dziedzińca i od skweru (lico pn. skrzydła 0,287 m od granicy → maks. 0,25 m).
* **Wariant B:** lico ściany zach. skrzydła przesunięte o 0,30 m do wnętrza: linia (49,135; 9,619)–(61,544; 65,989); trakt 14,70 = 0,50 + 6,10 + 1,50 + 6,10 + 0,50 (korytarz 1,50 ≥ 1,40 m). Lico wsch. segmentu przesunięte do (115,688; 39,859)–(113,189; 50,110), czyli 0,516 m od granicy. PZ −17,3 m² (skrzydło) −3,2 m² (segment).

### K-2. Próg rampy +0,30 wobec chodnika 119,09 – rampa nie mieści się bez dachu nad dziedzińcem

**Stan w spec.:** 5 – „próg rampy 119,60 (+0,30) z prowadnicami zapór mobilnych”; 2 (13) – rampa „w całości pod dachem segmentu”; 2 (f) – „Rampa 18 % opada w całości pod segmentem, a strop rampy na wyjściu z segmentu leży na −0,21, poniżej terenu”; JSON `rampa.prog_npm = 119.6`.

**Dowód (NMT `site.json`, skrypt rozdz. 5):**
* Chodnik przed bramą ma 119,08–119,11 (NMT w punktach (116,2; 43,3), (116,4; 41,0), (115,9; 45,5)). Próg 119,60 jest więc **0,51 m nad chodnikiem**, a między licem bramy a granicą jest tylko 0,216 m.
* Wartość −0,21 ze spec. wychodzi dokładnie z założenia, że rampa zaczyna opadać od progu +0,30 **w licu elewacji**: długość wewnętrzna 18,66 m, 3,0 m przejścia 9 % i 15,66 m spadku 18 % dają posadzkę −2,79, a strop (prześwit 2,30 + płyta 0,28) −0,21. Oznacza to, że 0,51 m wzniesienia pokonuje się **na chodniku publicznym** (dz. 10/1 i 19/12, poza obszarem). Garb 0,51 m na ciągu pieszym bulwaru (6KDB/2 – „ciągi piesze”) jest nie do przyjęcia: nie leży na terenie inwestycji i łamie zasady dostępności.
* Jeżeli wzniesienie do +0,30 nastąpi wewnątrz (0,51 m przy 12 % i 1 m płaskiego progu pod zapory), strop rampy na wyjściu z segmentu wypada na **+0,74 = 120,04 m n.p.m.**, czyli **1,11 m nad istniejącym terenem dziedzińca (118,93)** i 0,79 m nad terenem podniesionym do 119,25. Taki strop jest dachem części budynku poza A o „najniższym punkcie pokrycia” ok. 1 m nad terenem, sprzecznym z MPZP § 6 pkt 3 lit. b (≥ 18 m; `mpzp.md` K-03, K-11). To dokładnie błąd K5, który korekta (f) deklaruje jako usunięty.
* Nawet w wariancie spec. strop −0,21 (119,09) leży **0,16 m nad istniejącym terenem** przy wyjściu (118,93). „Poniżej terenu” jest prawdą tylko po podniesieniu dziedzińca do ≥ 119,25, a zapas wynosi wtedy 0,16 m.
* „W całości pod segmentem” jest niemożliwe: spadek 4,05 m (od +0,30 do −3,75) z przejściami 2 × 3,5 m wymaga ok. **26,0 m** rampy, a segment ma 18,66 m. Ogon rampy (5–8 m) i tak leży pod dziedzińcem.

**Poprawka:** zrezygnować z progu +0,30. **Próg bramy w poziomie chodnika 119,10 (−0,20)**, zabezpieczenie przed wodą powierzchniową **samoczynną zaporą przeciwpowodziową** (lub zaporą mobilną do 120,30) we wnęce bramy + odwodnienie liniowe i pompownia. Spadek od lica: 3,0 m przy 9 % + 15,66 m przy 18 % daje posadzkę przy ścianie zach. segmentu **−3,29**, a wierzch stropu **−0,71 = 118,59 m n.p.m.**, czyli 0,34 m pod istniejącym terenem i 0,66 m pod terenem 119,25 (miejsce na substrat). Dalej przejście dolne 9 % (ok. 5,1 m) pod dziedzińcem do −3,75. Poprawić: 2 (13) „rampa częściowo pod segmentem, ogon ok. 5 m pod dziedzińcem”; 2 (f) „strop −0,71”; 5 „próg 119,10 + zapora samoczynna”; JSON `rampa.prog_npm = 119.10`. Rzędna 119,10 > 119,0 (sytuacja wyjątkowa).

---

## 3. Błędy ISTOTNE

### I-1. Segment: program pasa pn. i rampa nie mieszczą się w obrysie

**Dowód:** segment ma szerokość prostopadłą do ściany pd. **10,38 m przy elewacji wsch. i 6,95 m przy ścianie zach.** Rampa 6,5 m (2 × 3,0) + ściana pd. 0,30 + przegroda 0,20 = 7,0 m > 6,95 m: **przy ścianie zach. rampa nie mieści się w segmencie**. Pas pn. pozostały po rampie: **32,2 m² brutto, ok. 21,0 m² netto**. Spec. umieszcza w nim trafo 21 + rozdzielnię nn 17 + BESS 11 + punkt odpadów 7 = **56 m² netto** (spec. 6 „Segment”; korekta (d) – elektryka nad poziomem zalewu). Klin zwęża się ku zach. od 3,4 m do 0, więc trafo 21 m² z drzwiami od Wybrzeża też się nie mieści.

**Poprawka:** rampa **jednopasowa 3,5 m** z sygnalizacją wahadłową (109 m.p.). Pas obsługi rośnie wtedy do **90,1 m² brutto / ok. 76 m² netto** ≥ 56 m². Zalecane ułożenie (spójne z I-2 i K-2): rampa **wzdłuż ściany pn. segmentu** (v −0,35…−3,85), brama 4,0 m w elewacji wsch. na v −0,4…−4,4 (nadal 6KDB/2, dalej od okna WS 5). Trafo, rozdzielnia, BESS i odpady wzdłuż pełnej ściany pd., z drzwiami od Wybrzeża. Przy progu −0,20 posadzka przy ścianie zach. ≈ −3,22, a strop ≈ −0,64 (pod terenem).

### I-2. Drzewa „zachowane” w strefach korzeni ściany −1; liczba 38 nieudowodniona

**Podstawa:** położenie drzew wiąże M.06, nie M.02 (Wyj. 13 odp. 65; `dendrologia.md` K-05). Strefa projektowa = max(NSOD z tab. 1 M.06 + promień pnia; korona/2 + 1 m). Operat (rozdz. 6) zakazuje w SOD robót ziemnych, zmiany poziomu terenu i przecinania korzeni Ø > 4 cm. Położenia M.06 odczytano z `img/dendro_plan_rekomendacje.png` (±0,5 m).

| Drzewo M.06 | Rekom. | Strefa | Odl. pnia od ściany −1 | Wejście w strefę | Odpowiednik M.02 w spec. |
|---|---|---:|---:|---:|---|
| nr 60 wierzba mandżurska 128+37 cm | Z2 | 6,2 m | **2,24 m** (od lica skrzydła 4,23 m) | **3,96 m** | D703/D704 („palisada”) |
| nr 58 klon zwyczajny 75 cm | **Z1** | 4,2 m | **3,38 m** | 0,82 m | D706 (4,00 m) – w spec. pominięty |
| nr 78 świerk 90 cm | **Z1** | 3,1 m | 3,02 m (+ pas roboczy ściany) | 0,08 m | I881 (3,53 m) |
| nr 67 klon zwyczajny 90 cm | **Z1** | 3,1 m | 0,79 m | 2,31 m | D897 – usuwany, ale spec. nie podaje, że to Z1 |

Ponadto ściana −1 pod skrzydłem leży **0,571 m od granicy ogródków** (murki prowadzące i pas roboczy ściany szczelinowej wchodzą w ogródki), a D886 jest 2,30 m od ściany. „Palisada sieczna + przesłona korzeniowa” 2,3–2,9 m od pnia osłabionej wierzby (strefa 6,2 m) jest sprzeczna z regułami SOD z operatu. Teza „zachowane 38 (86 %), wszystkie 29 drzew ogródków” nie ma pokrycia.

**Poprawka:**
1. Pas −1 pod dziedzińcem zwęzić z 7,0 do **5,0 m** (v 0…−5,0): wierzchołki (72,475; 33,031) i (96,666; 38,929) zastąpić **(72,001; 34,975) i (96,193; 40,872)**. −1: 2 337,2 → **2 287,4 m²** (−49,8 m², ok. −2 m.p. → 107 ≥ 99 wg spec.). Nr 58 (Z1) ma wtedy 5,38 m ≥ 4,2 + 1,0. Wymaga rampy jednopasowej przy ścianie pn. segmentu (I-1).
2. Nr 60 (Z2) leży 4,23 m od samego lica skrzydła i jego −1 (strefa 6,2), więc przy tym obrysie skrzydła **nie da się go uczciwie zadeklarować jako zachowanego**. Należy go wykazać jako „usuwany – kolizja” (z nasadzeniem zastępczym) albo cofnąć lico wsch. skrzydła i −1 o ≥ 2 m na odcinku s 20–34.
3. W bilansie stosować numerację M.06 i rekomendacje Z1/Z2. Uczciwy wynik: zachowane **36–37 z 44** (82–84 %), w tym 1 Z1 (nr 78) „z ryzykiem” i z ochroną (wygrodzenie korona + 1 m, ściana prowadząca od strony wykopu, nadzór arborysty).

### I-3. Ściany szczelinowe na granicy z dz. 8/8 i przy szczycie Maz. 19

**Dowód:** obwód −1 = 244,6 m (zgodnie ze spec.), a obrys −1 leży **0,000 m od granicy** wzdłuż dz. 8/8 (60,2 m, lico zach. skrzydła) i wzdłuż szczytu Maz. 19 (15,0 m; obrys Maz. 19 styka się z obrysem skrzydła, odstęp 0,000 m). Ściana szczelinowa 0,80 m wymaga murków prowadzących (ok. 0,3 m po obu stronach szczeliny). Przy obrysie −1 = lico zewnętrzne ściany murek zewnętrzny leży więc **poza obszarem** (pas jezdni/chodnika Mazowieckiej) albo **pod odsadzką fundamentu kamienicy z 1880 r.** Posadzka −1 (115,55) z płytą 0,90 m daje spód ≈ 114,6, czyli ok. 2 m poniżej posadzki piwnicy Maz. 19 (≈ 116,7) i poniżej ZWG (115,5–116,45). Spec. przewiduje tylko „rozpory i monitoring, bez wibracji”, bez rozwiązania styku. Dotyczy to wprost warunku „styk z Maz. 19 bez naruszenia gabarytu” (MPZP § 8: ochrona gabarytu i elementów kamienicy).

**Poprawka:**
* Wzdłuż Maz. 19 (15,0 m): zamiast ściany szczelinowej **ściana z kolumn iniekcji strumieniowej Ø 0,8–1,2 m**, pełniąca jednocześnie funkcję podbicia fundamentu szczytu, ze wstępnym rozpoznaniem odkrywkami. Obrys −1 na tym odcinku cofnąć o 0,6 m (lico wewn. ściany oporowej) albo pierwsze 6 m M1 bez −1.
* Wzdłuż dz. 8/8: albo obrys −1 cofnięty o 0,40 m (lico zewn. ściany 0,40 m od granicy; −1 −24 m²), albo w opisie wprost „czasowe zajęcie pasa drogowego Mazowieckiej na murek prowadzący (uzgodnienie z ZDiUM)”.
* Uzupełnić 5 („Posadowienie”) i JSON `siatka.posadowienie.obudowa` (obwód ściany szczelinowej 229,6 m + 15,0 m iniekcji).

### I-4. Błędy danych maszynowych `koncepcja.json` (źródło rysunków)

1. **Poligon skrzydła jest niepoprawny:** `Self-intersection [68.372 63.74]`. Trzy pierwsze wierzchołki [68.766, 64.397], [68.372, 63.74], [68.766, 64.397] tworzą kolec 0,54 m w głąb skrzydła. Może to wywrócić silnik rysunków (offsety, cięcia).
2. **JSON ≠ tabela 4.1:** w JSON narożnik NE skrzydła jest zaokrąglony (łuk R 3,509, środek (64,92; 65,36)). Między skrzydłem a wieżą od strony skweru powstaje **wcięcie 2,66 m²** (u −0,08, v 24,35–29,70), którego tabela 4.1 nie ma (lico pn. prosto do (67,494; 69,592)). Pole wg tabeli 4.1 = **849,66 m²**, a nie 847,00 (847,00 to pole JSON). PZ z tabelą 4.1 i wypełnieniem dylatacji = ok. **2 165,7 m²** (58,1 %), nie 2 162,9. Nagłówek tabeli mówi „CCW”, a skrzydło jest podane **zgodnie z ruchem wskazówek**.
3. **Strefy parteru skrzydła wchodzą w wieżę (i w obszar A):** „Foyer 80, szatnia 20, WC 40, magazyn 25” – **20,1 m²** w obrysie wieży; „Bistro 92 m²” – **11,0 m²** w obrysie wieży (prostokąt s 50,0–59,9 × d 0,5–10,0 przy dziobie, który ma głębokość ok. 5,4 m). Rzeczywista powierzchnia bistro w obrysie skrzydła ≤ 82,4 m² brutto, więc 92 m² programu się nie mieści. Nakładają się też ze strefą wieży „Łącznik do foyer” (u 0,5–13,35 × v 21,0–29,2).

**Poprawka:** usunąć dwa pierwsze wierzchołki M. Wybrać jedną geometrię dziobu (zalecana tabela 4.1 – brak szczeliny od skweru) i zaktualizować `pow_rzutu_m2 = 849.66`, `zabudowa.pow_zabudowy_m2 ≈ 2165.7`, 58,1 %. Strefy parteru przyciąć do obrysu skrzydła (np. `shapely.intersection`) i przeliczyć bistro (przenieść 10 m² zaplecza do M4). Nagłówek 4.1 → „kolejność wierzchołków jak w JSON (CCW)”.

### I-5. Pojemność elewacji „wieża pd. 6” (do potwierdzenia rzutem kond. 1)

**Dowód:** na kond. 1–4 segment zasłania lico pd. wieży na u 21,0–40,0 (lico pn. segmentu v −0,05). Odsłonięte lico pd. wieży ma **21,0 m** (u 0–21,0) → maks. **5 jednostek × 4,05 = 20,25 m** przy zerowych stratach w narożach. Spec. liczy 6 (24,3 m) i jednocześnie pisze, że „naroża pd. wieży zajmują szachty i WC” (2 (g)). Przy dwóch narożach zajętych zostają ok. 4 jednostki. Sześć jednostek wymagałoby wliczenia 3,83 m lica pd. skrzydła (u −3,9…0) i braku strat w narożu wklęsłym z segmentem, gdzie § 13 przy sektorze symetrycznym i tak nie jest spełniony (D-9). Deficyt 1–2 jedn./kond. × 4 = **4–8 jedn.**, więc pojemność 216–220 < 220,8 zajętych.

**Poprawka:** przeliczyć pojemność na rzucie kond. 1 (wieża pd. ≤ 5, realnie 4). Brakujące 1–5 jedn. pokryć np. przeniesieniem 2–3 pokoi socjalnych do strefy środkowej z doświetleniem pośrednim albo zamianą 1–2 magazynków „głębokich” na wewnętrzne archiwum. Inaczej punkt 2 (18) „20/20 magazynków przy elewacji” trzeba złagodzić.

---

## 4. Błędy DROBNE

**D-1. § 13 WS 5 – liczby i wrażliwość zapasu.** Okno pokoju 6/6A: odległość do segmentu w sektorze 11,129 m, a nie 11,15 (lica równoległe, az. 86,685° oba). Zapasy wynoszą więc **3,05 m** (H od parapetu 124,0) i **1,05 m** (H od 120,0), nie 3,07 / 1,07. Zapas 1,05 m jest wrażliwy na założenia: przy murze 0,40 m → 0,90 m; przy H od 119,2 (okna piwnic / teren przy WS 5: 118,62–119,25) → 0,65 m; łącznie → 0,50 m. Wariant „najostrożniejszy” nie jest więc najostrożniejszy. **Poprawka (zalecana, tania):** attyka ściany pd. segmentu obniżona do poziomu tarasu **139,10**, z balustradą szklaną 1,10 m cofniętą o 1,5 m (140,20). Zapas wynosi wtedy **1,58 m** (H 120,0) / **1,18 m** (H 119,2), a balustrada ma 2,53 / 2,13 m. MPZP: najniższe pokrycie segmentu 139,10 − 119,44 = 19,66 ≥ 18 ✔.

**D-2. § 13 – wykładnia progu 35 m.** Ust. 1 pkt 1 lit. b odnosi 35 m do „obiektu przesłaniającego o wysokości ponad 35 m”. Nasz budynek jest jednym obiektem o wysokości 37,6 m. Przy literalnym odczycie 17,5 m dotyczyłoby także segmentu (11,13 < 17,5). Spec. stosuje (słusznie, zgodnie z ust. 2 „przesłaniająca część” i z `naslonecznienie_metoda.md` pkt 7) analizę schodkową. **Poprawka:** w części opisowej i na P6 wprost zapisać przyjętą wykładnię (obiekt = część budynku o danej wysokości, łuki schodkowe).

**D-3. Pasy styku w A i sprzeczność „dylatacja / brak dylatacji”.** Linia A nie jest równoległa do lica zach. wieży (u = 0,000 w SW, u = −0,031 w NW), a jej krawędź pd. sięga v = −0,009 przy SE. Pas styku 5–8 cm między skrzydłem/segmentem a wieżą leży więc **częściowo w A: ok. 0,46–0,51 m²** obróbki dachowej na poziomie 139,5–140,15 (< 35 m). Odstęp skrzydła i segmentu od linii A wynosi 0,041–0,049 m, nie „5–8 cm”. Spec. 2 (b) mówi o dylatacji na u −0,05…−0,08, a rozdz. 5 „kondygnacje P–4 ciągłe (bez dylatacji w poziomie stropów)… uskok dachów to tylko obróbka”. **Poprawka:** obróbkę styku zaprojektować jako **pionową listwę na licu wieży** (element elewacji wieży, nie pokrycie dachu), a pokrycie skrzydła i tarasu segmentu zakończyć na u ≤ −0,05 / v ≤ −0,05. Alternatywnie lico zach. wieży na linii A: narożnik NW **(67,542; 69,604)** zamiast (67,572; 69,611). Ujednolicić tekst 2 (b) i 5.

**D-4. Tolerancja linii A.** Lica wieży leżą na liniach A z zapasem 0,000 m. Linia A ma dokładność ±0,3 m, a narożniki z PDF i DWG M.04 różnią się do 0,19 m. Ryzyko jest ujawnione (16.1). Należy dopisać zakaz **jakiegokolwiek wysięgu na licach zach. i pd. wieży** (czapa attyki, obróbka 0,15 m, kordon, parapety, lamele): każdy wysięg > 0 oznacza część wyższą niż 25 m poza A. Na P5 dać detal z zaznaczeniem „linia A wg M.04 (DWG) = lico”.

**D-5. Lamele korony poza obrysem R 14,0.** Szkło na R 13,5 i lamele 0,60 m „bezpośrednio przed szkłem” sięgają R 14,1. Wychodzą poza obrys wieży o 0,10 m (ok. 2,2 m² rzutu) i zmniejszają odległość od ścięcia granicy z 0,443 do **0,343 m**. Nadal mieszczą się w obszarze i w A, ale przeczą tezom „lamele w obrysie” i „lico wewn. 0,50 m od obrysu” (7 – sala do R 13,5). Na marginesie: przy lameli 0,25 m co 0,90 m i głębokości 0,60 m pełne przesłonięcie zachodzi od ok. 47°, nie od 34°. **Poprawka:** szkło (lico zewn.) na R 13,40, lamele 0,60 m na R 13,40–14,00, sala do R 13,25 (−5,3 m², sala 282,1 m², nadal ≥ 280 m²). Albo lamele 0,50 m na R 13,50–14,00.

**D-6. § 60 – błędne azymuty i godziny.** Z okna pokoju 4 lok. 6/6A (elewacja zach. WS 5, n ≈ 24,5) skrzydło zajmuje **az. 245–321°**, a nie 257–270°. Zacienia okno od **15:45–15:55 CET (20.03)** i 16:30–16:40 CEST (23.09), a nie od 16:40. Nasłonecznienie po realizacji wynosi ok. **3,8 h**, a nie „≥ 4,5 h” (istn. 4,25 h). Wniosek (≥ 1,5 h; pokoje 1–2 i tak spełniają § 60) bez zmian. Nasz budynek widziany z pokoi 1–2 leży w az. ok. **309–355°**, nie „340–40°”. **Poprawka:** zastąpić liczby w 13 („§ 60”, punkty 1–2) powyższymi.

**D-7. Odległość bramy garażu od okna lok. 6/6A.** Do najbliższej krawędzi bramy jest 12,6 m, do osi bramy 15,1 m. W tekście (2 (14)) jest „15,0 m”. Należy podawać 12,6 m. Po przeniesieniu rampy na pn. stronę segmentu (I-1) wyjdzie ok. 17,4 m do krawędzi.

**D-8. Rampa „w całości pod dachem segmentu”** (2 (13)) – fizycznie wymaga ok. 26 m, segment ma 18,7 m (patrz K-2). Korekta tekstu.

**D-9. § 13 własnych pomieszczeń w narożu wklęsłym segment/wieża.** Przy sektorze symetrycznym (WT 2002) jednostka „segment zach. 1” ma lico pd. wieży (> 35 m) w sektorze już w **7,0 m** (wymagane 17,5). Okno wieży pd. przy u = 19 ma ścianę zach. segmentu w **4,0 m** (wymagane 10,43 przy H od 119,30). Spec. opiera się na sektorze obróconym (projekt WT, 16.3). **Poprawka:** od razu (nie „alternatywnie”) zamienić „segment zach. 1” i skrajną jednostkę wieży pd. przy segmencie (u ≈ 17–21) na pomieszczenia pomocnicze. Wpływ na pojemność: patrz I-5.

**D-10. Drobne liczby:**
* teren skrzydła (pas 2 m) 118,36/119,43, a nie 118,40/119,41 → 20,07 / 21,79 m zamiast 20,09 / 21,75;
* ogród niezabudowany 3 728,7 − 2 162,9 = 1 565,8 m², a nie 1 568;
* lico wsch. wieży 0,585–0,625 m od granicy, a nie 0,59–0,68;
* elewacja wsch. segmentu 10,55 m ≠ 5 osi × 2,025 (10,125).

**D-11. Wyrzutnie garażu.** Brak lokalizacji wyrzutni wentylacji i oddymiania garażu (−1: 2 337 m², −2: 1 426 m²). Dach i elewacje od ulic/bulwaru odpadają (MPZP § 6 pkt 13). **Poprawka:** wskazać szacht w trzonie B z wyrzutem w lamelach korony od pd., analogicznie do oddymiania korytarzy, i wpisać w 10.

**D-12. Styk z Maz. 19 – wysokość.** Attyka Maz. 19 ma niepewność 139,5–140,25 m (`sasiedzi.md` K-01). Teza „gzyms 140,15 = attyka Maz. 19 − 0,09 m” jest pewna tylko przy 140,24. Gabarytu Maz. 19 to nie narusza (nic nie wchodzi nad jej dach, M ∩ Maz. 19 = 0 m²). Na rysunku elewacji należy jednak dać fugę/uskok 0,30 m (już przewidziany w M1) i zapis „rzędna do potwierdzenia pomiarem”.

---

## 5. Zmiany do wprowadzenia w `koncepcja.json` (zestawienie)

| Klucz | Jest | Ma być |
|---|---|---|
| `bryly[M].obrys_ccw` | kolec na początku, zaokrąglony narożnik NE | bez [68.766, 64.397], [68.372, 63.74] na początku; dziób wg tabeli 4.1; `pow_rzutu_m2: 849.66` |
| `zabudowa.pow_zabudowy_m2` | 2162.9 | ≈ 2165.7 (z tabelą 4.1 i wypełnieniem dylatacji); przy wariancie K-1 B −20,5 m² |
| `elewacje.skrzydlo` | gzyms wysięg 0,30 | wysięg 0,00 na licach < 0,30 m od granicy; relief = cofnięcie wypełnień (K-1 A) |
| `podziemie.rampa.prog_npm` | 119.6 | 119.10 + zapora samoczynna; rampa 1 × 3,5 m przy ścianie pn. segmentu, brama v −0,4…−4,4 (K-2, I-1) |
| `podziemie.-1.obrys_ccw` | (72.475, 33.031), (96.666, 38.929) | (72.001, 34.975), (96.193, 40.872); `pow_m2: 2287.4`; `miejsca: 66` (I-2) |
| `parter.skrzydlo` (bistro, foyer) | wchodzą w wieżę 11,0 / 20,1 m² | przycięte do obrysu M; przeliczony program |
| `par13.segment.okno_pokoju_lok_6_6A` | odl 11.15, zapas 3.07 | odl 11.13, zapas 3.05 |
| `bryly[W].luk.R_szyb_korony` | 13.5 | 13.40 (lamele 13,40–14,00) (D-5) |
| `zagospodarowanie` | zachowane 38, ogródki 29/29 | wg M.06: 36–37/44, nr 60 usuwany lub warunkowo, nr 78 „z ryzykiem”, nr 67 (= D897) jako Z1 usuwane |

---

## 6. Dowód – kluczowe fragmenty skryptu (`_weryfikacja_geometria.py`)

```python
# § 13 – sektor 60° z wierzchołkiem w licu wewnętrznym (mur 0,55 m), okno w dowolnym miejscu szczytu
G0, G1 = np.array([101.93, 28.52]), np.array([118.16, 29.46]); Lg = np.linalg.norm(G1-G0)
t = (G1-G0)/Lg; nv = np.array([-t[1], t[0]]); azn = degrees(atan2(nv[0], nv[1])) % 360   # 356,69°
def wedge(V, az, half=30, R=80): ...                      # wycinek koła 60° wokół normalnej
for s in np.arange(0.55, Lg-0.55, 0.05):                  # cała długość lica wewnętrznego
    V = G0 + s*t - 0.55*nv; d = Point(V).distance(obst.intersection(wedge(V, azn)))
# wynik: segment 11,129 m (wymagane 10,075 → zapas 1,054); wieża 19,000 m (≥ 17,5 → 1,50); skrzydło poza sektorem
# MPZP – TIN (LinearNDInterpolator) z pikiet teren=1 i linii nieciągłości, pas 2 m wokół bryły, krok 0,25 m
# rampa – długość wewn. 18,66 m; próg +0,30 → strop −0,21 (119,09) tylko przy starcie spadku w licu (chodnik 119,09!);
#          próg osiągnięty wewnątrz → strop +0,74 (120,04) > teren 118,93; próg −0,20 → strop −0,71 (118,59)
```

Pełne wyniki (wydruk skryptu): obrysy i A (rozdz. 1), krawędzie OI (rozdz. 2), pasma MPZP (rozdz. 3), § 13 z wrażliwością (rozdz. 4), segment i rampa (rozdz. 5), drzewa M.02/M.06 (rozdz. 6). Analiza § 60 (tor Słońca NOAA, zbieżność południków −0,738°, przeszkody: M, S, W, Maz. 19, Maz. 17, WS 9) i wariantowe obliczenia poprawek – skrypty robocze `w5_par60.py`, `w8_fix.py` w katalogu roboczym sesji weryfikatora (wyniki przytoczone w D-6, I-1, I-2, K-2).
