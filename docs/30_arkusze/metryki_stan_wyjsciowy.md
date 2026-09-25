# Metryki arkuszy — stan wyjściowy (przed optymalizacją ustawienia na arkuszach)

Data pomiaru: 2026-09-25. Narzędzie: `tools/metryki_arkuszy.py` (do wielokrotnego użycia). Dane szczegółowe
(obwiednie bloków, plany składania): `docs/30_arkusze/metryki_stan_wyjsciowy.json`.

Wymaganie inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.” Ten raport tylko **mierzy** stan obecny. Nic tu
nie zmieniamy. Jest punktem odniesienia dla kolejnych kroków.

Polecenie:

```
PYTHONPATH=src python3 tools/metryki_arkuszy.py AR=projekt/01_koncepcja/widoki PZT=projekt/02_PZT/rysunki \
  IS=projekt/05_PT_instalacje_sanitarne/rysunki IE=projekt/06_PT_instalacje_elektryczne/rysunki \
  BO=projekt/04_PT_konstrukcja/rysunki BO-robocze=<scratchpad>/bo/out DETALE=projekt/10_PT_architektura/detale \
  DETALE-robocze=<scratchpad>/detale --md <tabele.md> --json docs/30_arkusze/metryki_stan_wyjsciowy.json \
  --podglad <katalog PNG>
```

## 1. Metoda

* **Wejście:** katalog z `raport_widokow.json` z generatora (lista arkuszy i ścieżek PDF). Gdy raportu nie ma,
  brane są wszystkie `*.pdf` oprócz `tom*.pdf`. Mierzona jest pierwsza strona każdego PDF.
* **Format i wymiary:** wymiary strony PDF [mm]. Nazwa formatu pochodzi z raportu generatora albo z
  `lamela.dokumenty.formaty.wykryj_format`. **Pole wewnątrz ramki:** ramka odczytana z PDF (największy
  obrysowany prostokąt). W `lamela.draft.Sheet` ramka ma 20 mm po lewej i 10 mm z pozostałych stron.
* **Bloki treści (z rzeczywistej zawartości PDF, PyMuPDF):**
  1. Każda ścieżka z `page.get_drawings()` jest rozbijana na segmenty (odcinek, krzywa, prostokąt, czworobok).
     Każdy segment ma własną obwiednię, bo matplotlib łączy w jedną ścieżkę linie leżące daleko od siebie. Do tego
     dochodzą obwiednie spanów tekstu z `page.get_text('dict')`.
  2. **Pomijane są:** elementy, które nie leżą w całości wewnątrz ramki (znaki składania, znaki centrujące, siatka
     pól odniesienia, opis formatu w marginesie), sama ramka i niewidoczne białe wypełnienia (tła i maski).
     Pomijana jest też **tabliczka z tabelą zmian**. Wykrywa się ją jako białe wypełnienia szerokości ≈ 180 mm
     w prawym dolnym rogu ramki i dolicza jako jeden stały blok.
  3. Obwiednie trafiają na siatkę 1 mm. Następnie: domknięcie morfologiczne o promieniu 6 mm (`--odstep`) i
     wypełnienie dziur. Każda spójna składowa daje **prostokątną obwiednię bloku**: rzutnię z opisami i
     wymiarami, tabelę, blok kolumny opisowej, różę kierunków, tytuł widoku.
* **Wskaźniki:**
  * **W obw.** — współczynnik wypełnienia: pole sumy prostokątów bloków i tabliczki (bez podwójnego liczenia)
    podzielone przez pole wewnątrz ramki. To wskaźnik główny.
  * **W rys.** — to samo bez tabliczki (w liczniku i w mianowniku).
  * **W kontur** — pole samej domkniętej maski, bez prostokątów. Bardzo niski W kontur przy wyższym W obw.
    oznacza „rzadki” rysunek: schemat, aksonometrię albo dużo pustego tła wewnątrz rzutni.
  * **Największy pusty prostokąt** wewnątrz ramki (siatka 2 mm) — gdzie leży marnowany papier.
  * **Przycięty** — obwiednia całej treści plus marginesy 20/10 mm. Tyle papieru zostaje, jeśli **tylko** odetniemy
    puste pasy przy obecnym układzie.
* **Plan składania:** `lamela.draft.sheet.fold_positions` (tak samo, jak znaki składania na arkuszu i
  `plan_skladania`). Pasy pionowe liczone są od lewej, rzędy od dołu. Warstwy = liczba pasów × liczba rzędów,
  czyli grubość paczki A4. **Ocena „ładnego” składania:**
  * pasy pośrednie równe (rozrzut ≤ 5 mm) i w przedziale 180–210 mm → *dobre*; węższe od 120 mm → *słabe*;
  * górny rząd ≥ 0,9·297 mm → *dobre*; ≥ 104 mm → *poprawne*; węższy → *słabe*;
  * paczka szersza niż 210 mm → *słabe*.
  * Ocena końcowa to gorsza z dwóch ocen.
* **Kontrola wizualna:** podglądy PNG (`--podglad`). Czerwone są bloki, niebieska tabliczka, zielony największy
  pusty prostokąt, fioletowe linie zgięć. Obejrzano AR-01, AR-05, IS-16 i BO-03: bloki zgadzają się z rzutniami,
  tabelami i kolumną opisową, a ramka, siatka i znaki są poprawnie pominięte.
* **Ograniczenia:** obwiednia rzutni obejmuje osie modularne i linie wymiarowe, które wystają poza budynek.
  Puste wnętrza pomieszczeń liczą się więc jako treść, co jest poprawne dla czytelności. Bloki bliższe niż 6 mm
  scalają się w jeden. Wynik jest niezależny od stylu kreski.

## 2. Wyniki zbiorcze

UWAGA: komplety BO i detali są w trakcie przebudowy przez inne zespoły, a pliki zmieniały się w czasie pomiaru.
* **BO** (`projekt/04_PT_konstrukcja/rysunki`) to wersja zapisana w repozytorium.
* **BO-robocze** to bieżąca wersja robocza zespołu BO: 26 arkuszy, zbrojenia płyt przeniesione z A0 na A3×3/A2.
* **DETALE** — `projekt/10_PT_architektura/detale` jeszcze nie ma arkuszy.
* **DETALE-robocze** — `raport_widokow.json` w tym katalogu opisuje w chwili pomiaru tylko arkusz testowy T13.
  PDF-y T1–T12 z wcześniejszego przebiegu nie są w raporcie, więc ich nie liczono.

| Komplet | Arkuszy | Formaty | Papier [m²] | ≈ A4 | W ważone | W średnie | W min (arkusz) | Puste [m²] | Po przycięciu [m²] | Warstwy A4 | Składanie (dobre/poprawne/słabe) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AR | 10 | 1× A1, 6× A3x3, 1× A2x3, 2× A2 | 3,99 | 64 | 54 % | 55 % | 44 % (PB-AR-05) | 1,68 | 3,65 | 96 | 0/10/0 |
| PZT | 3 | 3× A2 | 0,75 | 12 | 78 % | 78 % | 77 % (PZT-02) | 0,15 | 0,73 | 18 | 0/3/0 |
| IS | 17 | 16× A3x3, 1× A1 | 6,49 | 104 | 51 % | 51 % | 37 % (PT-IS-06) | 2,92 | 5,82 | 170 | 0/17/0 |
| IE | 14 | 14× A3x3 | 5,24 | 84 | 51 % | 51 % | 36 % (PT-IE-09) | 2,37 | 4,66 | 140 | 0/14/0 |
| BO | 21 | 6× A3x3, 3× A2, 6× A0, 4× A1, 1× A2x3, 1× A3 | 11,87 | 190 | 32 % | 37 % | 21 % (PT-BO-16) | 7,61 | 9,77 | 261 | 1/14/6 |
| BO-robocze | 26 | 11× A3x3, 10× A2, 2× A1, 2× A2x3, 1× A3 | 9,23 | 148 | 43 % | 45 % | 25 % (PT-BO-21) | 4,87 | 8,20 | 221 | 1/25/0 |
| DETALE | 0 | — | — | — | — | — | — | — | — | — | — |
| DETALE-robocze | 1 | 1× A2 | 0,25 | 4 | 48 % | 48 % | 48 % (PT-AR-D-T13) | 0,12 | 0,21 | 6 | 0/1/0 |


## 3. Wnioski ze stanu wyjściowego

Łącznie dla kompletów AR, PZT, IS, IE i BO-robocze: 70 arkuszy i **25,7 m² papieru** (≈ 412 A4) na jeden
egzemplarz. Ważone wypełnienie wynosi **49 %**, a w ramkach jest **≈ 12,0 m² pustego pola**. Samo odcięcie pustych
pasów przy obecnym układzie zmniejsza zużycie do 23,1 m² (−10 %). Po złożeniu wychodzi 645 warstw A4.

1. **Format A3×3 (891×420) dominuje:** 16/17 arkuszy IS, 14/14 IE, 6/10 AR. Rzut kondygnacji 1:50 z kolumną
   opisową rzadko wypełnia go szczelnie. Typowe straty to:
   * pionowy pas 80–150 mm między rzutnią a kolumną opisową (rzuty I i II piętra: przycięta szerokość 771–790 mm);
   * poziomy pas ≈ 680×78 mm pod rzutnią (rzuty II piętra IS/IE: W = 36–39 %).
2. **Najsłabsze arkusze:**
   * PT-IS-03/06/14 i PT-IE-03/06/09 (rzuty II piętra, 36–38 %);
   * PB-AR-04 (rzut dachu na A2×3, 46 %) i PB-AR-05 (przekrój na A3×3, 44 %);
   * schematy PT-IS-15/16/17 (W kontur 19–24 %);
   * w BO z repozytorium sześć arkuszy A0 z wypełnieniem 21–26 %. Wersja robocza BO już je przenosi na
     mniejsze formaty (43 %).
3. **PZT (3× A2) jest wypełniony dobrze (78 %).** Rezerwa jest niewielka, ale PZT nie może zejść poniżej 1:500.
4. **Składanie:** żaden arkusz nie jest „ładny” w obu kierunkach. Wyjątek to A3 (PT-BO-21/26).
   * Wysokość 420 mm (A2, A3×n) daje zawsze górny rząd **123 mm**.
   * Szerokość 891 mm daje pasy 210 + 150 + 150 + 190 + 190. Szerokość 841 mm (A1) daje 210 + 126 + 126 + 190 + 190.
   * Przy obecnym `fold_positions`, gdzie pasy 190 mm dodawane są parami, ocenę „dobre” w poziomie dają tylko
     szerokości **570–630, 960–980 i 1340–1360 mm**. Na przykład 780 mm (210 + 190 + 190 + 190) daje pasy
     210 + 105 + 105 + 190 + 190. Jeśli formaty niestandardowe mają się ładnie składać, trzeba uogólnić
     algorytm na nieparzystą liczbę pasów 190 mm. Taka zmiana należy do silnika `lamela.draft`, a ten raport jej
     nie wprowadza.
   * Wysokości przyjazne składaniu to 297, 594 i 891 mm. Dopuszczalne są też wysokości z górnym rzędem
     ≥ 267 mm, na przykład 570–594 mm.
5. **Kierunki dalszych prac** (wymaganie inwestora, bez obniżania skal RPB § 9 i bez zmniejszania pisma):
   * dobór formatu niestandardowego „na miarę” treści: szerokość = obwiednia treści + 30 mm, zaokrąglona w górę do
     wymiaru dającego równe pasy; wysokość 297 albo 594 mm, gdzie to możliwe;
   * gęstsze upakowanie kolumny opisowej: legenda i uwagi obok tabliczki, a nie pas na całą wysokość;
   * łączenie małych widoków (przekroje, elewacje, schematy) na wspólnych arkuszach.

## 4. Norma składania

**Przywołanie w kodzie:** „PN-N-01603 / DIN 824 A” (`lamela/draft/sheet.py: fold_positions`,
`lamela/dokumenty/arkusze.py: plan_skladania`, README obu pakietów).

**PN-N-01603 — ustalenia:**
* Norma istnieje. Tytuł: **PN-N-01603:1986 „Rysunek techniczny — Składanie formatów arkuszy”** (ang. *Technical
  drawings — Folding of drawing sheets*). Zastąpiła PN-N-01603:1976 „Rysunek techniczny — Składanie rysunków”,
  a ta PN-M-01112:1960.
* **Status: wycofana, bez następcy.**
  * Źródło: karta w katalogu PKN (sklep.pkn.pl/pn-n-01603-1986p.html), odczytana 2026-09-24. Zapis:
    `scratchpad/research/pkn_PN_N_01603.json`.
  * Data wycofania **2011-10-10** pochodzi z weryfikacji R4 (`docs/10_podstawy_prawne/R4_rysunek_budowlany_normy.md`,
    tabela statusów). Nie udało się jej dziś potwierdzić ponownie: serwis PKN zwracał 503 / błąd TLS.
  * Wykaz w bibliotece (w.bibliotece.pl) potwierdza tytuł „Rysunek techniczny. Składanie formatów arkuszy PN-86
    N-01603”.
* PN-B-01025:2004 nadal powołuje PN-86/N-01603. Zgodnie z komunikatem PKN normę wycofaną wolno stosować
  dobrowolnie.
* **Treść (wymiary pasów, margines na oprawę): NIE ZWERYFIKOWANO.** Tekst normy jest płatny i niedostępny online.
  Źródła wtórne (materiały dydaktyczne) mówią tylko tyle: najpierw składa się wzdłuż linii prostopadłych do dolnej
  krawędzi, potem równoległych, a tabliczka ma być widoczna bez rozkładania.

**DIN 824 — ustalenia:**
* **DIN 824:1981-03 „Technische Zeichnungen; Faltung auf Ablageformat”**, 4 strony. Według DIN Media status to
  **aktualna** (*current*).
* Norma rozróżnia trzy formy składania do A4:
  * forma A — do wpięcia, z odłożonym marginesem na oprawę (dziurkowanie);
  * forma B — z doklejonym paskiem do wpięcia;
  * forma C — bez wpięcia.
* Tabliczka ma leżeć na wierzchu w prawym dolnym rogu i być czytelna bez rozkładania.
* Konkretne wymiary 190 mm (pas z tabliczką), 20 mm (margines) i 210 mm (pas z marginesem) znamy tylko ze źródeł
  wtórnych: stron firm składających plany i kursów. Z tekstem normy ich nie porównano.
* Kod stosuje **własne uogólnienie**: pierwszy pas 210 mm pozostaje pełny, pasy pośrednie dzieli się po równo,
  a pasy 190 mm dodaje parami. Na formaty wydłużone i niestandardowe norma i tak się nie rozciąga.

**Propozycja bezpiecznego sformułowania w kodzie i dokumentacji** (zamiast „wg PN-N-01603 / DIN 824 A”):

> „składanie do A4 „do wpięcia” wg praktyki DIN 824:1981-03, forma A (pas z tabliczką 190 mm na wierzchu, margines
> 20 mm na oprawę), uogólnione na formaty wydłużone i niestandardowe [przyjęcie]; PN-N-01603:1986 — wycofana, bez
> następcy, przywołanie informacyjne”.

W opisie technicznym i wykazie rysunków: „arkusze złożone do formatu A4 z marginesem do wpięcia (praktyka
DIN 824 A)”. Nie należy pisać „zgodnie z PN-N-01603”.

Źródła:
* [PKN — karta PN-N-01603:1986](https://sklep.pkn.pl/pn-n-01603-1986p.html)
* [w.bibliotece.pl — PN-86 N-01603](https://w.bibliotece.pl/1160418/Rysunek+techniczny.+Sk%C5%82adanie+format%C3%B3w+arkuszy+PN-86+N-01603)
* [PKN — stosowanie PN wycofanych](https://wiedza.pkn.pl/en/web/wiedza-normalizacyjna/stanowisko-pkn-w-sprawie-stosowania-pn-wycofanych)
* [DIN Media — DIN 824:1981-03](https://www.dinmedia.de/en/standard/din-824/891673)
* [Wikipedia — DIN 824](https://de.wikipedia.org/wiki/DIN_824)
* [Nehlsen — formy A/B/C](https://www.nehlsen-hamburg.de/magazin/detail/wir-falten-ihre-plaene-richtig-nach-din-824/)

## 5. Tabele szczegółowe

### AR — `projekt/01_koncepcja/widoki`

Stan plików PDF: 2026-09-25 05:19.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PB-AR-01 | A1 | 841×594 | 0,500 | 62 % | 60 % | 47 % | 630×86 (0,054 m²) | 818×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PB-AR-02 | A3x3 | 891×420 | 0,374 | 71 % | 70 % | 52 % | 70×400 (0,028 m²) | 823×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-03 | A3x3 | 891×420 | 0,374 | 57 % | 55 % | 43 % | 122×400 (0,049 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-04 | A2x3 | 1261×594 | 0,749 | 46 % | 45 % | 32 % | 322×370 (0,119 m²) | 1124×594 | 210 + 146 + 146 + 190 + 190 + 190 + 190 | 297 + 297 | 14 | poprawne — najwęższy pas pośredni 146 mm; pasy nierówne (rozrzut 44 mm) |
| PB-AR-05 | A3x3 | 891×420 | 0,374 | 44 % | 41 % | 30 % | 150×400 (0,060 m²) | 743×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-06 | A3x3 | 891×420 | 0,374 | 58 % | 56 % | 38 % | 252×152 (0,038 m²) | 820×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-07 | A3x3 | 891×420 | 0,374 | 50 % | 47 % | 33 % | 680×76 (0,052 m²) | 815×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-08 | A3x3 | 891×420 | 0,374 | 48 % | 45 % | 33 % | 680×80 (0,054 m²) | 815×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PB-AR-09 | A2 | 594×420 | 0,249 | 56 % | 52 % | 38 % | 384×80 (0,031 m²) | 584×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PB-AR-10 | A2 | 594×420 | 0,249 | 58 % | 54 % | 39 % | 194×152 (0,029 m²) | 584×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |

**Suma:** 10 ark. (1× A1, 6× A3x3, 1× A2x3, 2× A2); papier 3,99 m² (≈ 64,0 A4); wypełnienie ważone 54 %, średnie 55 %, najniższe 44 % (PB-AR-05); puste pole w ramkach 1,68 m²; po samym przycięciu pustych pasów 3,65 m² (−8 %); warstw A4 po złożeniu: 96; składanie — poprawne: 10.

### PZT — `projekt/02_PZT/rysunki`

Stan plików PDF: 2026-09-25 05:36.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PZT-01 | A2 | 594×420 | 0,249 | 79 % | 77 % | 61 % | 384×68 (0,026 m²) | 586×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PZT-02 | A2 | 594×420 | 0,249 | 77 % | 75 % | 64 % | 198×78 (0,015 m²) | 579×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PZT-03 | A2 | 594×420 | 0,249 | 80 % | 78 % | 68 % | 544×18 (0,010 m²) | 576×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |

**Suma:** 3 ark. (3× A2); papier 0,75 m² (≈ 12,0 A4); wypełnienie ważone 78 %, średnie 78 %, najniższe 77 % (PZT-02); puste pole w ramkach 0,15 m²; po samym przycięciu pustych pasów 0,73 m² (−2 %); warstw A4 po złożeniu: 18; składanie — poprawne: 3.

### IS — `projekt/05_PT_instalacje_sanitarne/rysunki`

Stan plików PDF: 2026-09-25 05:17.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT-IS-01 | A3x3 | 891×420 | 0,374 | 72 % | 70 % | 51 % | 842×32 (0,027 m²) | 831×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-02 | A3x3 | 891×420 | 0,374 | 46 % | 43 % | 39 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-03 | A3x3 | 891×420 | 0,374 | 37 % | 34 % | 32 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-04 | A3x3 | 891×420 | 0,374 | 61 % | 59 % | 49 % | 104×400 (0,042 m²) | 789×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-05 | A3x3 | 891×420 | 0,374 | 46 % | 42 % | 39 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-06 | A3x3 | 891×420 | 0,374 | 37 % | 33 % | 31 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-07 | A3x3 | 891×420 | 0,374 | 66 % | 64 % | 47 % | 680×46 (0,031 m²) | 840×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-08 | A3x3 | 891×420 | 0,374 | 61 % | 59 % | 48 % | 680×46 (0,031 m²) | 817×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-09 | A1 | 841×594 | 0,500 | 50 % | 48 % | 38 % | 630×136 (0,086 m²) | 799×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-IS-10 | A3x3 | 891×420 | 0,374 | 53 % | 51 % | 44 % | 680×68 (0,046 m²) | 780×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-11 | A3x3 | 891×420 | 0,374 | 46 % | 43 % | 38 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-12 | A3x3 | 891×420 | 0,374 | 57 % | 54 % | 46 % | 104×400 (0,042 m²) | 789×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-13 | A3x3 | 891×420 | 0,374 | 48 % | 45 % | 41 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-14 | A3x3 | 891×420 | 0,374 | 43 % | 40 % | 36 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-15 | A3x3 | 891×420 | 0,374 | 47 % | 44 % | 21 % | 272×190 (0,052 m²) | 801×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-16 | A3x3 | 891×420 | 0,374 | 47 % | 44 % | 19 % | 680×102 (0,069 m²) | 883×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IS-17 | A3x3 | 891×420 | 0,374 | 52 % | 49 % | 24 % | 288×232 (0,067 m²) | 784×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |

**Suma:** 17 ark. (16× A3x3, 1× A1); papier 6,49 m² (≈ 104,0 A4); wypełnienie ważone 51 %, średnie 51 %, najniższe 37 % (PT-IS-06); puste pole w ramkach 2,92 m²; po samym przycięciu pustych pasów 5,82 m² (−10 %); warstw A4 po złożeniu: 170; składanie — poprawne: 17.

### IE — `projekt/06_PT_instalacje_elektryczne/rysunki`

Stan plików PDF: 2026-09-25 05:18.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT-IE-01 | A3x3 | 891×420 | 0,374 | 57 % | 55 % | 45 % | 92×400 (0,037 m²) | 801×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-02 | A3x3 | 891×420 | 0,374 | 47 % | 43 % | 39 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-03 | A3x3 | 891×420 | 0,374 | 38 % | 34 % | 31 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-04 | A3x3 | 891×420 | 0,374 | 66 % | 64 % | 50 % | 78×400 (0,031 m²) | 814×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-05 | A3x3 | 891×420 | 0,374 | 48 % | 45 % | 42 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-06 | A3x3 | 891×420 | 0,374 | 39 % | 36 % | 34 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-07 | A3x3 | 891×420 | 0,374 | 57 % | 55 % | 44 % | 104×400 (0,042 m²) | 789×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-08 | A3x3 | 891×420 | 0,374 | 45 % | 42 % | 38 % | 120×400 (0,048 m²) | 773×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-09 | A3x3 | 891×420 | 0,374 | 36 % | 33 % | 30 % | 680×78 (0,053 m²) | 771×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-10 | A3x3 | 891×420 | 0,374 | 59 % | 56 % | 45 % | 86×400 (0,034 m²) | 806×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-11 | A3x3 | 891×420 | 0,374 | 57 % | 54 % | 44 % | 266×138 (0,037 m²) | 806×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-12 | A3x3 | 891×420 | 0,374 | 57 % | 55 % | 49 % | 100×400 (0,040 m²) | 793×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-13 | A3x3 | 891×420 | 0,374 | 51 % | 49 % | 44 % | 290×160 (0,046 m²) | 782×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-IE-14 | A3x3 | 891×420 | 0,374 | 53 % | 50 % | 47 % | 680×82 (0,056 m²) | 868×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |

**Suma:** 14 ark. (14× A3x3); papier 5,24 m² (≈ 84,0 A4); wypełnienie ważone 51 %, średnie 51 %, najniższe 36 % (PT-IE-09); puste pole w ramkach 2,37 m²; po samym przycięciu pustych pasów 4,66 m² (−11 %); warstw A4 po złożeniu: 140; składanie — poprawne: 14.

### BO — `projekt/04_PT_konstrukcja/rysunki`

Stan plików PDF: 2026-09-25 05:31.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT-BO-01 | A3x3 | 891×420 | 0,374 | 60 % | 57 % | 50 % | 96×400 (0,038 m²) | 796×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-02 | A2 | 594×420 | 0,249 | 38 % | 32 % | 26 % | 274×244 (0,067 m²) | 504×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-03 | A0 | 1189×841 | 1,000 | 22 % | 21 % | 19 % | 978×276 (0,270 m²) | 914×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-04 | A1 | 841×594 | 0,500 | 45 % | 43 % | 39 % | 630×152 (0,096 m²) | 741×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-05 | A3x3 | 891×420 | 0,374 | 58 % | 56 % | 49 % | 102×400 (0,041 m²) | 790×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-06 | A3x3 | 891×420 | 0,374 | 44 % | 41 % | 35 % | 144×400 (0,058 m²) | 748×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-07 | A3x3 | 891×420 | 0,374 | 42 % | 38 % | 34 % | 156×400 (0,062 m²) | 737×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-08 | A0 | 1189×841 | 1,000 | 26 % | 25 % | 23 % | 978×262 (0,256 m²) | 931×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-09 | A0 | 1189×841 | 1,000 | 26 % | 25 % | 23 % | 978×262 (0,256 m²) | 931×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-10 | A0 | 1189×841 | 1,000 | 21 % | 20 % | 18 % | 978×278 (0,272 m²) | 879×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-11 | A0 | 1189×841 | 1,000 | 21 % | 20 % | 19 % | 978×278 (0,272 m²) | 879×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-12 | A1 | 841×594 | 0,500 | 40 % | 37 % | 34 % | 630×154 (0,097 m²) | 706×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-13 | A1 | 841×594 | 0,500 | 40 % | 37 % | 34 % | 630×154 (0,097 m²) | 706×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-14 | A2 | 594×420 | 0,249 | 40 % | 35 % | 26 % | 242×244 (0,059 m²) | 535×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-15 | A2 | 594×420 | 0,249 | 34 % | 28 % | 19 % | 254×244 (0,062 m²) | 524×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-16 | A0 | 1189×841 | 1,000 | 21 % | 20 % | 15 % | 436×546 (0,238 m²) | 1032×841 | 210 + 110 + 110 + 190 + 190 + 190 + 190 | 297 + 297 + 247 | 21 | słabe — najwęższy pas pośredni 110 mm; pasy nierówne (rozrzut 80 mm); górny rząd 247 mm (niepełny) |
| PT-BO-17 | A1 | 841×594 | 0,500 | 26 % | 23 % | 20 % | 332×332 (0,110 m²) | 718×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-18 | A3x3 | 891×420 | 0,374 | 40 % | 36 % | 29 % | 134×400 (0,054 m²) | 759×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-19 | A3x3 | 891×420 | 0,374 | 43 % | 40 % | 35 % | 256×156 (0,040 m²) | 825×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-20 | A2x3 | 1261×594 | 0,749 | 26 % | 24 % | 21 % | 1050×90 (0,095 m²) | 1100×594 | 210 + 146 + 146 + 190 + 190 + 190 + 190 | 297 + 297 | 14 | poprawne — najwęższy pas pośredni 146 mm; pasy nierówne (rozrzut 44 mm) |
| PT-BO-21 | A3 | 420×297 | 0,125 | 67 % | 60 % | 56 % | 204×54 (0,011 m²) | 398×297 | 105 + 125 + 190 | 297 | 3 | dobre |

**Suma:** 21 ark. (6× A3x3, 3× A2, 6× A0, 4× A1, 1× A2x3, 1× A3); papier 11,87 m² (≈ 190,2 A4); wypełnienie ważone 32 %, średnie 37 %, najniższe 21 % (PT-BO-16); puste pole w ramkach 7,61 m²; po samym przycięciu pustych pasów 9,77 m² (−18 %); warstw A4 po złożeniu: 261; składanie — dobre: 1, poprawne: 14, słabe: 6.

### BO-robocze — `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/bo/out`

Stan plików PDF: 2026-09-25 05:40.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT-BO-01 | A3x3 | 891×420 | 0,374 | 60 % | 57 % | 50 % | 96×400 (0,038 m²) | 796×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-02 | A2 | 594×420 | 0,249 | 38 % | 32 % | 25 % | 274×244 (0,067 m²) | 504×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-03 | A3x3 | 891×420 | 0,374 | 47 % | 44 % | 39 % | 128×400 (0,051 m²) | 765×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-04 | A3x3 | 891×420 | 0,374 | 47 % | 44 % | 38 % | 128×400 (0,051 m²) | 765×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-05 | A2 | 594×420 | 0,249 | 34 % | 28 % | 33 % | 282×268 (0,076 m²) | 496×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-06 | A3x3 | 891×420 | 0,374 | 58 % | 56 % | 49 % | 102×400 (0,041 m²) | 790×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-07 | A3x3 | 891×420 | 0,374 | 42 % | 39 % | 35 % | 156×400 (0,062 m²) | 737×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-08 | A3x3 | 891×420 | 0,374 | 42 % | 38 % | 34 % | 156×400 (0,062 m²) | 737×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-09 | A3x3 | 891×420 | 0,374 | 52 % | 49 % | 42 % | 290×162 (0,047 m²) | 782×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-10 | A3x3 | 891×420 | 0,374 | 53 % | 50 % | 43 % | 110×400 (0,044 m²) | 782×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-11 | A3x3 | 891×420 | 0,374 | 45 % | 42 % | 29 % | 334×268 (0,090 m²) | 739×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-12 | A2 | 594×420 | 0,249 | 62 % | 58 % | 51 % | 196×154 (0,030 m²) | 582×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-13 | A2 | 594×420 | 0,249 | 63 % | 59 % | 52 % | 196×142 (0,028 m²) | 582×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-14 | A1 | 841×594 | 0,500 | 36 % | 33 % | 21 % | 310×442 (0,137 m²) | 715×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-15 | A2 | 594×420 | 0,249 | 61 % | 58 % | 49 % | 196×162 (0,032 m²) | 582×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-16 | A2 | 594×420 | 0,249 | 62 % | 59 % | 51 % | 196×150 (0,029 m²) | 582×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-17 | A2 | 594×420 | 0,249 | 35 % | 29 % | 33 % | 282×268 (0,076 m²) | 496×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-18 | A2 | 594×420 | 0,249 | 40 % | 35 % | 26 % | 242×244 (0,059 m²) | 535×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-19 | A2 | 594×420 | 0,249 | 34 % | 28 % | 19 % | 254×244 (0,062 m²) | 524×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-20 | A2x3 | 1261×594 | 0,749 | 31 % | 29 % | 24 % | 828×188 (0,156 m²) | 1206×594 | 210 + 146 + 146 + 190 + 190 + 190 + 190 | 297 + 297 | 14 | poprawne — najwęższy pas pośredni 146 mm; pasy nierówne (rozrzut 44 mm) |
| PT-BO-21 | A1 | 841×594 | 0,500 | 25 % | 22 % | 19 % | 318×342 (0,109 m²) | 728×594 | 210 + 126 + 126 + 190 + 190 | 297 + 297 | 10 | poprawne — najwęższy pas pośredni 126 mm; pasy nierówne (rozrzut 64 mm) |
| PT-BO-22 | A2 | 594×420 | 0,249 | 40 % | 34 % | 31 % | 236×172 (0,041 m²) | 570×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |
| PT-BO-23 | A3x3 | 891×420 | 0,374 | 39 % | 36 % | 29 % | 134×400 (0,054 m²) | 759×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-24 | A3x3 | 891×420 | 0,374 | 43 % | 40 % | 35 % | 256×156 (0,040 m²) | 825×420 | 210 + 150 + 150 + 190 + 190 | 297 + 123 | 10 | poprawne — najwęższy pas pośredni 150 mm; pasy nierówne (rozrzut 40 mm); górny rząd 123 mm (niepełny) |
| PT-BO-25 | A2x3 | 1261×594 | 0,749 | 25 % | 23 % | 22 % | 164×574 (0,094 m²) | 1100×594 | 210 + 146 + 146 + 190 + 190 + 190 + 190 | 297 + 297 | 14 | poprawne — najwęższy pas pośredni 146 mm; pasy nierówne (rozrzut 44 mm) |
| PT-BO-26 | A3 | 420×297 | 0,125 | 67 % | 60 % | 56 % | 204×54 (0,011 m²) | 398×297 | 105 + 125 + 190 | 297 | 3 | dobre |

**Suma:** 26 ark. (11× A3x3, 10× A2, 2× A1, 2× A2x3, 1× A3); papier 9,23 m² (≈ 148,0 A4); wypełnienie ważone 43 %, średnie 45 %, najniższe 25 % (PT-BO-21); puste pole w ramkach 4,87 m²; po samym przycięciu pustych pasów 8,20 m² (−11 %); warstw A4 po złożeniu: 221; składanie — dobre: 1, poprawne: 25.

### DETALE — `projekt/10_PT_architektura/detale`

Brak arkuszy PDF.

### DETALE-robocze — `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/detale`

Stan plików PDF: 2026-09-25 05:40.

| Nr | Format | W×H [mm] | Pow. [m²] | W obw. | W rys. | W kontur | Największy pusty prostokąt | Przycięty [mm] | Pasy [mm] | Rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PT-AR-D-T13 | A2 | 594×420 | 0,249 | 48 % | 43 % | 31 % | 384×116 (0,045 m²) | 508×420 | 210 + 192 + 192 | 297 + 123 | 6 | poprawne — górny rząd 123 mm (niepełny) |

**Suma:** 1 ark. (1× A2); papier 0,25 m² (≈ 4,0 A4); wypełnienie ważone 48 %, średnie 48 %, najniższe 48 % (PT-AR-D-T13); puste pole w ramkach 0,12 m²; po samym przycięciu pustych pasów 0,21 m² (−14 %); warstw A4 po złożeniu: 6; składanie — poprawne: 1.
