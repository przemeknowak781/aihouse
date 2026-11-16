# Metodyka plansz konkursowych 100×70 cm — UMWD Wrocław (Etap I i II)

Data opracowania i dostępu do źródeł: **2026-11-16**. Uzupełnienie: `wizualizacje_metodyka.md` (ten sam katalog).
Zakaz Inwestora przestrzegany: bez jakichkolwiek informacji o pracach/wynikach tego konkursu.

**Legenda:** **[F]** fakt ze źródła · **[P]** pomiar/obliczenie własne (reprodukowalne) · **[S]** źródło wtórne (portal/praktyk) · **[W]** wniosek/rekomendacja.

---

## 0. Najważniejsze decyzje (TL;DR)

1. **[F] Liczba plansz Etapu II: Regulamin mówi „maksymalnie 6”, ale Wyjaśnienia nr 20 (odp. 76) dopuściły maksymalnie 8**, a Wyjaśnienia nr 21 (odp. 79) **zakazały łączenia powtarzalnych kondygnacji na jednym rzucie** („umożliwił przedstawienie … na łącznej liczbie nawet ośmiu plansz, mając na uwadze m.in. czytelne przedstawienie osobno każdego z rzutów”). **[W] Rekomendacja: 8 plansz** (lub 7) — przy ~12–15 rzutach w skali 1:200 6 plansz wymusza zbyt małe teksty/rysunki. Kontekst zadania („≤6”) wymaga aktualizacji.
2. **[F] Białe tło obowiązkowe** (Etap I i II). **[W]** Interpretacja bezpieczna: **brak obrazów „na spad”** i brak dużych kolorowych pól tła; wokół całej treści stały biały margines ≥20 mm.
3. **[F] Format plików: TIFF lub JPG, 100×70 cm, 300 dpi** (każda plansza osobno zalecana) → **[P] 11 811 × 8 268 px**. Wyjaśnienia nr 14 (odp. 67): PDF niedopuszczalny zamiast TIFF/JPG. <!-- poprawione przez weryfikatora: odp. 67 dotyczyła Opracowania studialnego (Etap I) i odsyła do brzmienia Regulaminu („pliki w formacie TIFF lub JPG…”); dla Etapu II identyczny wymóg wynika wprost z rozdz. VII ust. 3 pkt 2 lit. a. Limit 100 MB dotyczy pojedynczego skompresowanego pliku — dopuszczalne jest kilka plików ZIP. --> Spakowany plik ≤100 MB (limit platformy).
4. **[F] Na planszach nie umieszczać numeru identyfikacyjnego**; pliki bez metadanych pozwalających rozpoznać autora (ryzyko niedopuszczenia).
5. **[F] Wydruki 100×70 naklejone na sztywny, lekki podkład + zeszyt A3** z pomniejszonymi planszami (300 dpi). **[P] Skala pomniejszenia A3 = 0,42** → to **pomniejszenie, a nie plansza, wyznacza minimalne rozmiary pisma i linii.**
6. **[P]/[W] Typografia (krój Inter, SIL OFL, zainstalowany):** tekst ciągły **18–20 pt** (min. 18), podpisy/legendy 14–16 pt, numery/powierzchnie pomieszczeń min. 12 pt (z legendą ≥14 pt), tytuły rysunków 24–28 pt, nagłówki 36–40 pt, tytuł planszy ~72 pt. Uzasadnienie: próg płynnego czytania x-height ≈ 0,2° (Legge & Bigelow 2011) dla planszy z 1 m i dla A3 z 40 cm.
7. **[P]/[W] Linie:** minimum **0,18 mm** na planszy (≈2,1 px przy 300 dpi; 0,076 mm na A3); kontury przekroju 0,5–0,7 mm + poché; nie używać 0,13 mm i cieńszych.
8. **[W] Siatka modułowa 12 kolumn × 6 rzędów**, marginesy 20 mm, odstępy 8 mm → moduł 72,7 × 97,0 mm; pas tytułowy 30 mm. Hero 8×4 moduły = **63,7 × 41,2 cm (≈3:2)**; rzut 1:200 typowo 4×3 moduły (31,5 × 30,7 cm) → 6 rzutów na planszę.
9. **[W] Narracja 8 plansz:** 1 Idea i miasto → 2 Urbanistyka → 3 Pierzeje i sąsiedztwo → 4 Parter i wejście → 5–6 Rzuty → 7 Sejmik, przekroje → 8 Elewacja 1:50, ekologia, dostępność.
10. **[F] Wymóg rysunku zagospodarowania 1:500: cienie przy słońcu z SW pod kątem 45°, „nie mogą ograniczać czytelności”** → cienie 20–30% czerni, mnożenie, długość cienia = wysokość budynku, kierunek na NE.
11. **[W] Spójność do porównywania:** wszystkie rzuty północą do góry (jak M.04), te same skale i paleta funkcji na rzutach, aksonometrii i schematach; Sąd porównuje prace między sobą (Merikoski 2020; Svensson 2012).
12. **[P]/[W] Produkcja:** rysunki wektorowo → raster dokładnie 300 dpi (`pdftocairo -r 300`), tekst renderowany PIL (FreeType + raqm, Inter OTF) bezpośrednio w rastrze planszy; eksport JPEG q=95, **subsampling 4:4:4**, dpi=300, bez EXIF/XMP. ReportLab nie osadzi Inter OTF (CFF) — jeśli potrzebny PDF wektorowy, najpierw konwersja OTF→TTF (fontTools).

---

## 1. Wymagania formalne [F]

Źródło: Regulamin (tekst jednolity 13.02.2026) rozdz. V–VII; wyjaśnienia nr 08, 09, 14, 20, 21; załącznik F.16.

### 1.1 Etap II — Praca konkursowa (rozdz. VII ust. 2–3)
- Część graficzna: plansze 100×70 cm **poziomo**, max 6 (→ **8** wg wyjaśnień nr 20); dopuszczalna mniejsza liczba, jeśli zawiera wymaganą treść; **białe tło**.
- Treść (zalecenia ust. 2 pkt 2):
  a) zagospodarowanie terenu na mapie zasadniczej **1:500**: rzut dachów, komunikacja (ppoż., dostawy, parkowanie, place, ruch pieszy i rowerowy), zieleń nowa i istniejąca, inne obiekty, rzędne, liczba kondygnacji, **cienie przy słońcu z SW pod 45°** nieograniczające czytelności;
  b) **rzuty wszystkich kondygnacji 1:200** (w tym podziemnych i dachu): numer, nazwa i powierzchnia pomieszczenia **lub** numer i powierzchnia z legendą obok rzutu; nazwy bloków funkcjonalnych; rzut parteru z otoczeniem, nawierzchniami (rodzaj materiału), małą architekturą, oświetleniem; **każda kondygnacja osobno** (wyjaśnienia nr 21, odp. 79–80);
  c) min. **2 przekroje 1:200**;
  d) **wszystkie elewacje 1:200**; elewacja wzdłuż Wybrzeża Słowackiego **z budynkiem nr 5**, wzdłuż Mazowieckiej **z budynkiem nr 19**;
  e) **przekrój szczegółowy przez elewację z fragmentem elewacji 1:50**;
  f) **schemat aksonometryczny** układu funkcjonalnego;
  g) **min. 8 wizualizacji** (lista w `wizualizacje_metodyka.md` §1);
  h) schemat rozwiązań proekologicznych i zrównoważonych;
  i) rozwiązania dostępności (mogą być na rysunkach jako legenda/oznaczenia lub na schematach);
  j) dowolne dodatkowe schematy/rysunki.
- Część opisowa: max 10 stron A4 (czcionka min. 11 pt) + tabele F.14.B, F.15.A–C + **pomniejszone do A3 plansze**; w wersji papierowej **zeszyt A3**.
- Postać elektroniczna: plansze **TIFF lub JPG 100×70 cm, 300 dpi**, każda jako osobny plik zalecane; A3 w 300 dpi; ZIP ≤100 MB na plik; karta identyfikacyjna jako jedyny plik z podpisem kwalifikowanym (podpisanie plansz/opisu = niedopuszczenie).
- Postać fizyczna: **wydrukowane plansze naklejone na sztywny, lekki podkład**; uzasadnienie Organizatora: zachowanie zamierzonego charakteru graficznego („odcienie kolorystyczne, grubości linii”), bo monitory różnią się jakością. W razie rozbieżności wiąże **postać elektroniczna**.
- Anonimowość: numer identyfikacyjny tylko na pierwszej (pustej) stronie wersji papierowej opisu i w karcie; **nie na planszach, nie w plikach, nie na makiecie**; pliki pozbawione metadanych (ust. 3 pkt 4).
- Ocena (rozdz. VIII): kryteria równoważne (funkcja, wpisanie w tkankę, atrakcyjność i oryginalność, ekologia, dostępność) + drugorzędne koszty; **prace niespełniające obligatoryjnych wymagań „nie powinny otrzymać I, II lub III Nagrody”** (rozdz. VIII ust. 2 pkt 3) → kompletność treści to warunek wygranej. <!-- poprawione przez weryfikatora: przepis ma wyjątek — „chyba że w ocenie Sądu Konkursowego istnieje możliwość doprowadzenia koncepcji do zgodności z wytycznymi obligatoryjnymi na dalszym etapie prac projektowych, bez zasadniczych zmian koncepcji”; ponadto lista treści w rozdz. VII ust. 2 pkt 2 nosi tytuł „zalecenia do zawartości”. Wniosek [W] pozostaje: traktować kompletność jako warunek konieczny (strategia bezpieczna), ale nie jest to automatyczna dyskwalifikacja. -->

### 1.2 Etap I — Opracowanie studialne (rozdz. V ust. 2)
- Max **2 plansze** 100×70 poziomo, białe tło, **sugerowany układ wg F.16** (wyjaśnienia nr 08, odp. 43 i 55: **nieobligatoryjny**, celem ujednolicenie i łatwiejsza ocena).
- Treść: zagospodarowanie 1:500 (+ **schemat zacieniania w dniu równonocy** pozwalający stwierdzić spełnienie § 60 WT dla zabudowy mieszkaniowej wzdłuż Wybrzeża Słowackiego), rzuty wszystkich kondygnacji 1:500 z blokami funkcjonalnymi i ich powierzchniami, przekrój 1:500, min. 2 rozwinięcia elewacyjne 1:500 (z budynkami nr 5 i nr 19), **3 perspektywy** (nr 1 zbieżna z F.17.A lub wklejona; nr 2 zbieżna z F.17.B lub wklejona — w Regulaminie omyłkowo „od strony wschodniej”; nr 3 z poziomu człowieka z sylwetą budynku **w kontekście Mostu Grunwaldzkiego**), schemat aksonometryczny. Forma może być szkicowa; ma to być „manifest i credo projektowe”.
- Część opisowa max 5 stron A4 (11 pt).

### 1.3 Układ F.16 (Etap I) — pomiar proporcji [P]
Pomiar z PDF F.16 (raster 150 dpi, ramka zewnętrzna = 100×70 cm):

| Plansza 1 | Położenie | Wymiar ok. |
|---|---|---|
| Perspektywa nr 1 (hero) | lewa górna | **59 × 48 cm** (~40% powierzchni) |
| Perspektywa nr 2 | prawa górna | 41 × 33 cm |
| Sytuacja 1:500 | prawa dolna | 41 × 37 cm |
| Dodatkowe grafiki / Przekrój 1:500 | lewa dolna, dwa pola | 2 × (30 × 22 cm) |

Plansza 2: Rzuty 1:500 (lewa górna, duże pole), Perspektywa nr 3 (prawa górna), Rozwinięcia elewacyjne (lewa dolna, pas), Schemat aksonometryczny (prawa dolna).
**[W]** Organizator „myśli” układem: duży obraz w lewym górnym rogu → kontekst/sytuacja po prawej → rysunki techniczne na dole. Dla Etapu I trzymać się F.16 (zero ryzyka, łatwe porównanie); dla Etapu II zachować tę samą logikę czytania (lewa góra = najważniejsze) — ciągłość rozpoznawalna dla Sądu oceniającego oba etapy.

---

## 2. Co wiemy o odbiorze plansz przez sąd (źródła i ich siła)

- [F] **Merikoski (2020)** — jury porównuje prace i ma trudność z ich „niewspółmiernością”; retoryka wizualna utrudnia porównanie; metoda warstwowego przerysowania ujawnia podobieństwa ukryte pod różną grafiką. **[W]** Ułatwiać porównanie: standardowe skale, północ do góry, jednoznaczne opisy, tabela zgodności z programem.
- [F] **Svensson (2012)** — sędziowie przechodzą między wizją, realnym miejscem/problemem i wyobrażeniem zbudowanego obiektu w realnym otoczeniu. **[W]** Każda plansza powinna łączyć te trzy poziomy: obraz (wizja) + rysunek (rozwiązanie) + kontekst (relacja z miastem).
- [F] **Kazemian & Rönn (2009)** (za Merikoski 2020) — zawężenie do grupy najlepszych jest łatwe, wybór zwycięzcy opiera się na reakcjach emocjonalnych. **[W]** Plansze muszą przejść dwa sita: (1) szybkie skanowanie — czytelna idea i jakość w kilka sekund z 2–3 m; (2) wnikliwa analiza — kompletność, poprawność, spójność obrazu i rysunku.
- [F] **Legge & Bigelow (2011)**, *Journal of Vision* 11(5):8 — zakres płynnego czytania to x-height od ok. **0,2° do 2°** kąta widzenia (przy 40 cm: 1,4–14 mm); poniżej tempo czytania spada.
- [S] Praktyka (ArchDaily „Competition Board Layout: Do’s and Don’ts” — tylko tytuł, artykuł za paywallem, nieprzeczytany; Learnarchitecture, Illustrarch, Archademia — źródła niskiej wiarygodności): zaczynać od siatki; najsilniejszy obraz w lewym górnym rogu; plansza ma „mówić sama” (brak prezentacji ustnej); typowe słabości: rozdrobnione obrazy, przegadane teksty koncepcji, rzuty przed wizualizacjami. **[W]** Zgodne z logiką F.16 i z Regulaminem (brak prezentacji ustnej w Etapie II).
- **Brak twardych danych:** nie znaleziono badań ilościowych, ile czasu sędzia poświęca jednej planszy ani jak układ wpływa na wynik. Zasady poniżej to synteza typografii, percepcji i praktyki.

---

## 3. Pojemność: ile rysunków się zmieści [P]/[W]

- Rzut 1:200: 1 m w naturze = 5 mm na planszy. Dla kondygnacji ~60 × 45 m → 30 × 22,5 cm + opisy ≈ moduł 4×3 (31,5 × 30,7 cm) → **6 rzutów na planszę** (2 rzędy × 3).
- Szacunek liczby rzutów [W]: dominanta do 45 m (~11–12 kondygnacji nadziemnych w strefie A), niższa część pierzejowa, 1–2 kondygnacje podziemne, rzut dachu → **ok. 13–16 rzutów** → 2,5–3 plansze (rzut parteru z otoczeniem większy, np. 6×4 moduły).
- Elewacje 1:200: pierzeja ~80–100 m z sąsiednimi kamienicami → 40–50 cm szerokości × (45 m → 22,5 cm wysokości) → dwie elewacje uliczne mieszczą się na jednej planszy w pasie 12 kolumn × 2–3 rzędy.
- Wniosek: przy 6 planszach rzuty zajmą połowę zestawu, a na 8 wizualizacji, sytuację, 4+ elewacje, 2 przekroje, detal 1:50 i 3 schematy zostanie ~3 plansze — gęsto. **8 plansz** daje oddech i czytelność.

---

## 4. Narracja zestawu [W]

Plansze wiszą obok siebie (zwykle w rzędzie lub 2 rzędach). Czytanie: od lewej do prawej, od idei do detalu. Na każdej planszy: tytuł + 1 dominujący element + rysunki wspierające.

### 4.1 Wariant 8 plansz (rekomendowany)

| Nr | Temat | Zawartość (wymagania Regulaminu w nawiasach) |
|---|---|---|
| 1 | **Idea i miasto** | HERO (najmocniejszy obraz — ujęcie od Odry/mostu lub fotomatch B), wiz. 1 (F.17.A), krótki manifest ≤120 słów, 3–5 kluczowych liczb (PUM/PU, wysokość, standard zero-emisyjny, liczba stanowisk pracy), mały schemat idei |
| 2 | **Urbanistyka** | zagospodarowanie 1:500 z cieniami SW 45° (a), wiz. 2 (F.17.B), schematy: odtworzenie pierzei, dominanta w strefie A MPZP, osie widokowe, relacja z ochroną konserwatorską, zieleń/retencja |
| 3 | **Pierzeje i sąsiedztwo** | elewacja wzdłuż Wybrzeża Słowackiego z nr 5 i wzdłuż Mazowieckiej z nr 19 (d), wiz. 4 i wiz. 5, schemat linii gzymsów/podziałów |
| 4 | **Parter i wejście** | rzut parteru z otoczeniem 1:200 (b: nawierzchnie, mała architektura, oświetlenie), wiz. 3 (wejście), wiz. 6 (hol główny), legenda dostępności (i) |
| 5 | **Rzuty I** | kondygnacje podziemne + niższe nadziemne 1:200, legendy pomieszczeń, nazwy bloków funkcjonalnych |
| 6 | **Rzuty II** | wyższe kondygnacje + rzut dachu 1:200, schemat aksonometryczny układu funkcjonalnego (f) |
| 7 | **Sejmik i przekroje** | rzuty kondygnacji Sejmiku (jeśli nie na 6), 2 przekroje 1:200 (c), pozostałe elewacje 1:200 (d), wiz. 7, wiz. 8 |
| 8 | **Technika, ekologia, dostępność** | przekrój szczegółowy + fragment elewacji 1:50 (e), schemat zero-emisyjności (h, wg M.12), schemat dostępności (i, wg M.13), bilans/koszt w liczbach |

### 4.2 Wariant 6 plansz (awaryjny)
1 Idea + sytuacja 1:500 + wiz. 1–2 · 2 Pierzeje: elewacje uliczne + wiz. 3–5 · 3 Parter z otoczeniem + wiz. 6 + aksonometria · 4 Rzuty I · 5 Rzuty II + przekroje + pozostałe elewacje · 6 Sejmik (wiz. 7–8) + detal 1:50 + ekologia + dostępność.
Ryzyko [W]: rzuty i elewacje schodzą do minimalnych rozmiarów, tekst w okolice 14–16 pt — sprawdzić A3.

### 4.3 Zasady spójności między planszami
- Ten sam pas tytułowy (wysokość, krój, położenie numeru „1/8”) — numer planszy dozwolony, numer identyfikacyjny **nie**.
- Wspólna linia horyzontu obrazów na sąsiednich planszach (np. górne krawędzie obrazów w 1. rzędzie modułów).
- Rzuty: północ do góry na wszystkich (jak M.04 i mapa zasadnicza), ta sama skala 1:200, ta sama legenda kolorów funkcji, strzałka północy i podziałka przy każdym zestawie.
- Te same kolory funkcji na rzutach, przekrojach, aksonometrii i schematach.

---

## 5. Siatka i hierarchia [W]

- **Format:** 1000 × 700 mm. **Marginesy:** 20 mm (biała rama — zgodność z wymogiem białego tła). **Pas tytułowy:** 30 mm u góry pola treści (tytuł planszy z lewej, numer planszy z prawej, cienka linia 0,35 mm pod spodem).
- **Siatka:** 12 kolumn × 6 rzędów w polu 960 × 622 mm, odstępy 8 mm → **kolumna 72,7 mm, rząd 97,0 mm**.
- Typowe pola: hero 8×4 (63,7 × 41,2 cm); wizualizacja średnia 4×3 (31,5 × 30,7 cm, kadr 3:2 → 31,5 × 21 cm + podpis) lub 6×3 (47,6 × 30,7 cm); rzut 1:200 4×3; elewacja 12×2 (96 × 20,2 cm); schemat 3×2 lub 4×2.
- **Hierarchia (3 poziomy):** 1) jeden dominujący element na planszy (≥30–40% powierzchni na pl. 1–4); 2) rysunki wymagane; 3) teksty i legendy. Rozmiar i kontrast mają odzwierciedlać ważność.
- **Puste miejsce** (biel) jest elementem kompozycji — min. 10–15% powierzchni planszy wolne od treści; nie wypełniać każdej dziury schematem.
- **Wyrównania:** wszystko do siatki; tytuły rysunków zawsze w tym samym miejscu względem rysunku (np. lewy dolny róg, nad podziałką).
- Kontrola „z daleka”: miniatura planszy 10% (ok. 1180 px szer.) powinna nadal pokazywać hierarchię i ideę (test szybkiego sita).

---

## 6. Typografia [P]/[W]

**Krój:** Inter (tekst) + Inter Display (tytuły) — zainstalowane w systemie (`/usr/share/fonts/opentype/inter/`, licencja SIL Open Font License [P] odczyt z pliku), pełne polskie znaki, cyfry tabelaryczne. [P] Wysokość x = 0,546 em (Inter), 0,516 em (Inter Display); wersaliki 0,728 em. Maksymalnie **2 kroje** (tu: jedna rodzina w dwóch optycznych wariantach) — brak mieszania stylów.

### 6.1 Obliczenie minimalnych rozmiarów [P]
Wymagany rozmiar Inter (pt) dla x-height o danym kącie widzenia (1 pt = 0,3528 mm):

| Odległość | 0,2° (próg płynnego czytania) | 0,3° (komfort) | 0,5° | 1,0° |
|---|---|---|---|---|
| 0,4 m (zeszyt A3) | 7,2 pt | 10,9 | 18,1 | 36,2 |
| 0,6 m | 10,9 | 16,3 | 27,2 | 54,4 |
| 1,0 m | 18,1 | 27,2 | 45,3 | 90,6 |
| 1,5 m | 27,2 | 40,8 | 68,0 | 135,9 |
| 2,0 m | 36,2 | 54,4 | 90,6 | 181,2 |

Pomniejszenie A3 (×0,42): plansza 18 pt → A3 7,6 pt (x-height 1,46 mm = **0,21°** z 40 cm ✓); 16 pt → 6,7 pt (0,19°, granica); 14 pt → 5,9 pt (0,16° — tylko krótkie etykiety); 12 pt → 5,0 pt (0,14° — wyłącznie numery z legendą).

### 6.2 Skala typograficzna (do stosowania)

| Rola | Krój / grubość | Rozmiar na planszy | Na A3 |
|---|---|---|---|
| Tytuł planszy | Inter Display SemiBold | 72 pt (może 60–96) | 30 pt |
| Nagłówek sekcji | Inter SemiBold | 36–40 pt | 15–17 pt |
| Tytuł rysunku („RZUT PARTERU 1:200”) | Inter SemiBold, wersaliki, światło +4% | 24–28 pt | 10–12 pt |
| Tekst ciągły | Inter Regular | **18–20 pt**, interlinia 125–135% | 7,6–8,4 pt |
| Podpisy, legendy, opisy rysunków | Inter Regular | 14–16 pt | 5,9–6,7 pt |
| Numery i powierzchnie pomieszczeń | Inter Medium, cyfry tabelaryczne | 12–14 pt (min. 12) | 5–5,9 pt |
| Kluczowe liczby (np. „45 m”) | Inter Display Light/Regular | 60–96 pt | 25–40 pt |

- Długość wiersza 45–75 znaków (przy 20 pt ≈ 3 kolumny siatki, ~23 cm); wyrównanie do lewej, bez justowania; bez dzielenia wyrazów w nagłówkach.
- Kolor tekstu #1A1A1A (nie czysta czerń dla długich tekstów — mniejsze zmęczenie; czysta czerń w rysunkach).
- Ilość tekstu na planszy: **≤150–250 słów** (poza opisami rysunków); reszta w części opisowej (10 stron A4).
- Polskie zasady: cudzysłów „ ”, półpauza w zakresach, spacja przed jednostką (45 m, 1:200), przecinek dziesiętny (12,4 m²), twarde spacje po jednoliterowych spójnikach.

---

## 7. Rysunki techniczne: czytelność 1:500 / 1:200 / 1:50 [P]/[W]

### 7.1 Grubości linii (na planszy; przy 300 dpi i po pomniejszeniu A3)

| Element | Grubość | px @300 dpi | na A3 |
|---|---|---|---|
| Kontur elementów przeciętych (ściany, stropy) + poché | 0,50–0,70 mm | 5,9–8,3 | 0,21–0,29 mm |
| Krawędzie widoczne, okna, schody | 0,25–0,35 mm | 3,0–4,1 | 0,11–0,15 mm |
| Linie drugorzędne, wyposażenie, posadzki | 0,18 mm (min.) | 2,1 | 0,076 mm |
| Linie ukryte / nad płaszczyzną cięcia (przerywane) | 0,18 mm | 2,1 | 0,076 mm |
| **Nie stosować** | ≤0,13 mm | ≤1,5 | ≤0,055 mm (znika w A3) |

- **Poché:** konstrukcja przecięta — pełna czerń (lub 85% szarości przy jasnym wypełnieniu funkcji); ścianki działowe — 50% szarości; to najszybszy nośnik czytelności rzutu z odległości.
- **Wypełnienia funkcji:** jasne tinty (15–25% krycia) pod czarnymi liniami, 6–8 kolorów, stonowane, rozróżnialne dla daltonistów (unikać pary czerwony/zielony o tej samej jasności), legenda wspólna dla zestawu. Nazwy bloków funkcjonalnych na rzucie (wymóg).
- **Kreskowania:** unikać gęstych szraf (mora/szarość po pomniejszeniu A3); materiał w przekroju 1:50 — szrafy rzadkie, min. odstęp 1,5 mm.
- **Opisy pomieszczeń:** „numer / powierzchnia” na rzucie (np. „3.14 · 12,4 m²”), nazwy w legendzie obok rzutu (dopuszczone wyjaśnieniami nr 21, odp. 80); w pomieszczeniach reprezentacyjnych pełna nazwa na rzucie.
- **Elementy obowiązkowe przy rysunkach:** tytuł ze skalą, podziałka liniowa, strzałka północy (rzuty, sytuacja), oznaczenie linii przekrojów, rzędne (±0,00 = … m n.p.m.), liczba kondygnacji na sytuacji.

### 7.2 Zagospodarowanie 1:500
- Cienie: słońce z **SW pod kątem 45°** (wymóg) → cień = wysokość obiektu, skierowany na NE; 20–30% czerni w trybie mnożenia, tak aby nie zakrywał opisów (wymóg „nie mogą ograniczać czytelności”).
- Granica opracowania i strefy wg legendy M.04; zieleń istniejąca/projektowana/do usunięcia rozróżniona; komunikacja: ppoż., dostawy, wjazd do garażu, ruch pieszy i rowerowy — czytelne symbole.
- Etap I: dodatkowo **schemat zacieniania w dniu równonocy** dla zabudowy mieszkaniowej przy Wybrzeżu Słowackiego (§ 60 WT) — osobny mały schemat z godzinami.

### 7.3 Elewacje 1:200 z sąsiadami
- Sąsiednie kamienice (nr 5, nr 19) tą samą grubością linii, w 60% szarości; projekt w pełnym kontraście i w lekkim tonie materiałów; cienie pod 45° (szare) dla reliefu.
- Linie gzymsów/attyk i ich rzędne przedłużone przerywaną linią akcentową przez całą pierzeję — argument „trafności wpisania” widoczny w sekundę.

### 7.4 Przekrój szczegółowy 1:50
- Wszystkie warstwy (konstrukcja, izolacja, okładzina, stolarka, zacienienie, posadzki), numerowane odnośniki + legenda 14–16 pt; obok fragment elewacji 1:50 w kolorze materiału (spójny z renderami) i ewentualnie mały aksonometryczny fragment.

### 7.5 Schematy (aksonometria funkcjonalna, ekologia, dostępność)
- Jeden rzut aksonometryczny dla wszystkich schematów (np. izometria 30°/30°, ta sama skala i kąt), rozsunięcie kondygnacji, kolory funkcji jak na rzutach.
- Schemat ekologiczny: ikony liniowe w jednym stylu, strzałki z liczbami (np. moc PV, retencja m³, udział OZE) wg standardu M.12; schemat dostępności: trasy bez barier, windy, miejsca oczekiwania na ewakuację, tyflomapy, toalety dostępne — wg M.13 i M.01.
- Zasada: każdy schemat odpowiada na jedno pytanie i ma ≤5 etykiet; bez dekoracyjnych grafik bez informacji.

---

## 8. Kolor, biel i obrazy na planszy [W]

- Tło **#FFFFFF** (czysta biel) — w pliku sprawdzić, że marginesy mają wartość 255/255/255 (żadnej szarej „mgiełki” po skalowaniu/kompresji).
- Paleta zestawu: czerń/grafit (rysunek), 1 kolor akcentu (z materiału projektu), stonowane tinty funkcji, kolory obrazów z jednej „rodziny” (patrz `wizualizacje_metodyka.md` §10).
- Bez gradientów tła, cieni pod obrazami, ramek ozdobnych, przezroczystych paneli; obrazy z ostrą krawędzią lub cienką ramką 0,25 mm.
- Obrazy umieszczać w rozdzielczości ≥150 ppi (cel 200 ppi) w skali wydruku; rysunki zawsze natywnie w 300 dpi (nie skalować rastra rysunków).
- Ciemne obrazy na białym tle wyglądają na wydruku ciemniej niż na ekranie — dla wersji drukowanej przygotować wydruk próbny i w razie potrzeby podnieść cienie o 0,1–0,2 EV (wersja elektroniczna = drukowana co do treści; korekta tonalna dotyczy obu plików, bo elektroniczna jest wiążąca).

---

## 9. Czego unikać (lista z uzasadnieniem)

| Błąd | Dlaczego szkodzi | Źródło |
|---|---|---|
| Brak któregokolwiek wymaganego rysunku/wizualizacji, łączenie powtarzalnych rzutów | praca „nie powinna otrzymać I–III nagrody” | [F] Regulamin VIII.2.3; wyjaśnienia nr 21 |
| Numer identyfikacyjny / metadane autora w plikach | niedopuszczenie do oceny | [F] Regulamin VII.3.4 |
| Obrazy na spad, kolorowe tła | ryzyko niezgodności z „białym tłem” | [F] wymóg + [W] interpretacja |
| Ściany tekstu, tekst <16 pt | nieczytelne z 1 m i w A3 | [P] obliczenia §6 |
| Linie ≤0,13 mm, gęste szrafy | znikają/zlewają się w A3 | [P] §7 |
| Mieszanie stylów (różne kroje, różne style renderów i schematów) | utrata spójności, wrażenie chaosu | [W] / [S] |
| Wizualizacje niezgodne z rysunkami | utrata wiarygodności; Sąd porównuje warstwami | [F] Merikoski 2020 |
| Rozdrobnienie (wiele małych obrazów zamiast jednego mocnego) | brak hierarchii w szybkim sicie | [S] Archademia; [W] |
| Różna orientacja rzutów (obrócone) | utrudnia porównanie z sytuacją i innymi pracami | [W] |
| Diagramy dekoracyjne bez informacji | zajmują miejsce, nie pracują na kryteria | [W] |
| Kolory funkcji różne na różnych rysunkach | błędne odczytanie programu | [W] |

---

## 10. Produkcja techniczna [P]/[W]

### 10.1 Narzędzia dostępne w środowisku [P]
- PIL 13 (FreeType ✓, raqm ✓ — poprawny kerning i polskie znaki), numpy; `pdftocairo` (raster PDF w zadanym dpi); ImageMagick 6.9 (limit obszaru 256 MP — wystarczy na 97,6 MP planszy); ReportLab 5.0.1 (PDF wektorowy — **tylko fonty TTF**, Inter jest OTF/CFF); matplotlib 3.11 i ezdxf 1.4.5 w `.venv-render` (rysunki z DWG/DXF); fontTools (konwersja OTF→TTF, jeśli potrzebna).
- Brak: Inkscape, rsvg-convert, Ghostscript, exiftool → metadane kontrolować w PIL.

### 10.2 Potok [W]
1. Specyfikacja układu (JSON: siatka, pola, treści) — jedna dla zestawu.
2. Rysunki wektorowo w skali (1:200 → mm planszy), eksport PDF bez tekstu lub z tekstem w TTF; raster `pdftocairo -png -r 300` → dokładne wymiary pól w px (1 mm = 11,811 px).
3. Złożenie planszy w PIL na płótnie **11 811 × 8 268 px**, RGB, tło (255,255,255); tekst `ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', size_px)` gdzie `size_px = pt × 300/72`.
4. Eksport:
   - JPEG: `quality=95, subsampling=0, dpi=(300,300), optimize=True`, bez `exif`/`icc_profile` z danymi autora (opcjonalnie czysty profil sRGB) — szacunkowo 15–45 MB/plansza.
   - TIFF (alternatywa): kompresja LZW — pliki ~100–300 MB, przekroczą limit ZIP 100 MB → JPEG preferowany.
5. A3 do opisu: skala 0,42 → 4961 × 3473 px wycentrowane na 4961 × 3508 px (A3 @300 dpi), białe pasy 1,5 mm.
6. Kontrola automatyczna: wymiary px, wartość bieli marginesów, brak EXIF/XMP/komentarzy (`Image.open(f).info`, `getexif()`), nazwy plików neutralne (`plansza_1.jpg`…), rozmiar ZIP ≤100 MB.

### 10.3 Wydruk [W]
- Drukarnia wielkoformatowa z kalibracją, papier matowy lub satynowy (bez odblasków w sali obrad sądu), naklejenie na lekką płytę piankową (np. 5 mm) — zgodnie z wymogiem „sztywny, lekki podkład”.
- Przed finalnym drukiem: wydruk próbny 1:1 wycinków krytycznych (najmniejszy tekst, linie 0,18 mm, najciemniejszy render, tinty funkcji) i pełnej planszy w A3; ocena z 0,5, 1 i 2 m.
- Dostarczyć pliki sRGB z osadzonym profilem lub ustalić z drukarnią profil; sprawdzić, czy biel marginesów drukuje się jako biel papieru.

---

## 11. Lista kontrolna jakości plansz

**Zgodność (blokująca):**
- [ ] Liczba plansz ≤8 (wyjaśnienia nr 20), format 100×70 poziomo, białe tło, biały margines wokół treści.
- [ ] Zagospodarowanie 1:500 z cieniami SW 45°, rzędnymi, liczbą kondygnacji, komunikacją (ppoż., dostawy, parking, piesi, rowery), zielenią.
- [ ] Rzuty **wszystkich** kondygnacji 1:200 osobno (w tym podziemne i dach), numer + powierzchnia każdego pomieszczenia (+ nazwa lub legenda obok), nazwy bloków funkcjonalnych; parter z otoczeniem, nawierzchniami i materiałami, małą architekturą, oświetleniem.
- [ ] ≥2 przekroje 1:200; wszystkie elewacje 1:200; elewacje uliczne z budynkami nr 5 i nr 19.
- [ ] Przekrój szczegółowy + fragment elewacji 1:50.
- [ ] Schemat aksonometryczny funkcji; schemat proekologiczny; rozwiązania dostępności.
- [ ] 8 wymaganych wizualizacji, w tym 1 i 2 na zdjęciach F.17.A/B.
- [ ] Brak numeru identyfikacyjnego i metadanych; pliki JPG/TIFF 300 dpi, 11 811 × 8 268 px; ZIP ≤100 MB.
- [ ] Pomniejszenia A3 (300 dpi) w części opisowej.

**Czytelność:**
- [ ] Tekst ciągły ≥18 pt, podpisy ≥14 pt, numery pomieszczeń ≥12 pt; test wydruku A3 z 40 cm.
- [ ] Linie ≥0,18 mm; poché czytelne z 2 m; brak gęstych szraf.
- [ ] Miniatura 10% pokazuje hierarchię i ideę.
- [ ] Tytuł, skala, podziałka, północ przy każdym rysunku; rzuty północą do góry.

**Spójność i estetyka:**
- [ ] Jedna siatka, jeden pas tytułowy, jedna rodzina kroju, jedna paleta funkcji na wszystkich rysunkach i schematach.
- [ ] Wizualizacje z jednej „rodziny” (pora roku, grading, ziarno), zgodne z rysunkami.
- [ ] ≥10–15% białej przestrzeni na planszy; brak ozdobników bez treści.
- [ ] Narracja: od idei (pl. 1) do detalu (pl. 8); każda plansza ma jeden dominujący element.
- [ ] Każde kryterium oceny ma na planszach co najmniej jedno wyraźne „miejsce” (funkcja, wpisanie, atrakcyjność, ekologia, dostępność, koszty).

---

## 12. Źródła (dostęp: 2026-11-16)

**Materiały Organizatora (lokalnie, `/home/user/aihouse/umwd/00_materialy/`)**
- Regulamin Konkursu SARP nr 1089, tekst jednolity 13.02.2026 — `tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt` (rozdz. V ust. 2, rozdz. VII ust. 2–3, rozdz. VIII).
- Wyjaśnienia treści Regulaminu: nr 08 (odp. 42, 43, 55), nr 09 (odp. 61), nr 14 (odp. 67), nr 20 (odp. 76), nr 21 (odp. 79–82) — `tekst/1089_Wyjasnienia_tresci_Regulaminu_nr_XX-sig.txt`.
- F.16 Układ plansz — `_rozpak/3.Zalaczniki_Formalne_F.01-F.17_PDF/F.16_UKŁAD PLANSZ.pdf` (pomiar proporcji [P]).
- M.01 Program użytkowy; M.04 mapa schematyczna; M.12 standard zero-emisyjności; M.13 standard dostępności.

**Publikacje naukowe**
- Legge, G. E., & Bigelow, C. A. (2011). Does print size matter for reading? A review of findings from vision science and typography. *Journal of Vision*, 11(5):8, 1–22. doi:10.1167/11.5.8 — PDF: https://legge.dl8.umn.edu/sites/legge.psych.umn.edu/files/2020-08/Legge%20Bigelow%202011%20Does%20size%20matter%20for%20reading%3F%20A%20review%20of%20findings%20from%20vision%20science%20and%20typography.pdf
- Merikoski, T. (2020). Sights beyond Illusions: Towards Commensurable Competition Proposals. *Nordic Journal of Architectural Research*, 32(1), 9–32 — https://acris.aalto.fi/ws/portalfiles/portal/43329614/1188_655138_1_PB.pdf
- Svensson, C. (2012). Architectural Persuasion: On Quality Assessment in an Architectural Competition. *Nordic Journal of Architectural Research*, 24(1), 97–118 — https://arkitekturforskning.net/na/article/view/20 (abstrakt) <!-- poprawione przez weryfikatora: dodano strony -->
- Kazemian, R., & Rönn, M. (2009). Finnish architectural competitions: structure, criteria and judgement process. *Building Research & Information*, 37(2), 176–186, doi:10.1080/09613210802450705 (cyt. za Merikoski 2020, s. 26). <!-- poprawione przez weryfikatora: dodano DOI -->

**Typografia — literatura klasyczna (nie weryfikowano treści w tej sesji; wiedza ogólna)**
- Müller-Brockmann, J. (1981). *Grid Systems in Graphic Design*. Niggli.
- Bringhurst, R. *The Elements of Typographic Style* (wyd. 4.0, 2012). Hartley & Marks.
- Tufte, E. R. (2001). *The Visual Display of Quantitative Information* (wyd. 2). Graphics Press.

**Źródła wtórne [S]**
- ArchDaily, „Competition Board Layout: Do’s and Don’ts” — https://www.archdaily.com/1113735/competition-board-layout-dos-and-donts (tylko tytuł; treść za paywallem, nieprzeczytana).
- Learnarchitecture, „Architecture jury presentation tip” — https://learnarchitecture.net/articles/32828-architecture-jury-presentation-tip.html ; Illustrarch — https://illustrarch.com/articles/8788-5-tips-to-win-an-architectural-competition.html ; Archademia — https://archademia.com/blog/winning-architecture-competitions/ (niska wiarygodność; wg wyników wyszukiwania).
- Licencja Inter: SIL Open Font License — odczytana z metadanych pliku fontu [P].
