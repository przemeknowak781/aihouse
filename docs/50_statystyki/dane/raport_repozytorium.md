## Statystyki produktu w repozytorium /home/user/aihouse

Wszystkie liczby pochodzą z jednego przypiętego commita **HEAD d4716b00 (2026-09-25 08:36:03Z)** na gałęzi claude/single-family-house-project-2pkn7l. Użyłem tylko odczytu: `git log`, `ls-tree` i `show`, a `git archive` rozpakował src/ i model/ do scratchpad/statystyki/snapshot. Nie zmieniłem niczego w repozytorium.

Podczas pomiaru gałąź przesunęła się o kolejne 5 commitów (do 08:42Z, w tym „Raport postępu nr 51” i 5 arkuszy PT-AR). Nie są wliczone.

### 1. Commity
Źródło: `git log HEAD --root --numstat`, czas commitera w UTC. Pliki binarne (w numstat „-”) nie wchodzą do sum linii.

| Miara | Wartość |
|---|---|
| Commity razem (0 merge'y) | **402** (397 do 08:30:00Z) |
| Pierwszy commit | 2026-09-24 23:22:16Z, 9c732b3 „Etap 0: szkic wejściowy…” |
| Ostatni commit | 2026-09-25 08:36:03Z, d4716b0 (autocommit) |
| Rozpiętość | 9,23 h |
| Autocommity (temat dokładnie „Prace robocze zespołów (autocommit)”) | **287**: od 00:38:19Z, mediana odstępu 93 s (skrypt tools/autocommit.sh czeka 90 s) |
| Inne „Prace robocze zespołów…” (commity ręczne) | 39 |
| Commity z własnym tematem | 76 |
| Linie dodane / usunięte (bez binarnych) | **15 463 559 / 7 800 400** |
| Zmiany plików binarnych | 2 576 |

**Rozkład godzinowy (UTC, czas polski to +2 h):**

| Godzina | 23 | 00 | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 (do 08:36) |
|---|---|---|---|---|---|---|---|---|---|---|
| Commity | 5 | 27 | 34 | 56 | 46 | 46 | 56 | 51 | 44 | 37 |

**Sumy linii zawyżają pliki generowane:**
- **DXF:** +13,63 mln / −6,64 mln linii.
- **OBJ:** +0,66 mln / −0,25 mln linii.
- **Anomalia:** commit dac9ac4 („Raport postępu nr 50”, 08:31:03Z) zapisał do tools/dokumenty/tom_PT_AR.py 48 MB powtórzonych fragmentów kodu (+782 371 linii). Autocommit ddddb92 przywrócił plik 24 s później.
- **Bez anomalii, DXF i OBJ:** **+388 335 / −132 479** linii.
- **Sam Python bez anomalii:** +96 701 / −6 704 linii.

### 2. Pliki i kod
Źródło: `git ls-tree -r -l HEAD`.

| Rozszerzenie | Pliki | MB |
|---|---|---|
| .png | 547 | 190,8 |
| .py | 235 | 5,0 |
| .md | 125 | 4,1 |
| .pdf | 107 | 58,0 |
| .json | 103 | 8,4 |
| .dxf | 87 | 48,3 |
| .html | 23 | 1,8 |
| .yaml | 22 | 0,37 |
| .txt | 11 | 0,09 |
| .svg | 10 | 0,68 |
| .webp | 8 | 0,89 |
| .jpg | 5 | 8,9 |
| .js | 5 | 0,06 |
| .gz | 3 | 0,33 |
| .glb | 2 | 7,6 |
| .j2 | 2 | 0,04 |
| .obj | 1 | 15,2 |
| .mtl, .css, .sh, bez rozszerzenia | po 1 | ~0,04 łącznie |
| **Razem** | **1 300** | **350,45** |

**Rozmiar repozytorium:**
- Pliki śledzone na HEAD: 350,45 MB.
- Drzewo robocze bez .git: 596,9 MB (`du -sb`), w tym ignorowany build/ 205,5 MB.
- .git: 804,3 MB (8 743 luźne obiekty, brak paczek).
- Pomiary `du` zrobiono około 08:43, więc obejmują zmiany wprowadzone już po HEAD.

| Python (śledzone) | Pliki | Linie | Bez pustych i komentarzy | Funkcje (def) | Klasy |
|---|---|---|---|---|---|
| src/ | 148 | 64 746 | 57 087 | 2 757 | 267 |
| tools/ | 56 | 19 338 | 16 618 | 754 | 17 |

Poza tym 31 plików .py leży w docs/ (generatory koncepcji W1–W3 i slajdów).

**Testy:**
- 8 plików tools/test_*.py.
- **158 funkcji test\*** (policzone przez `ast`, potwierdzone grepem `def test`) i 488 asercji `assert`.
- Skrypty są samodzielne (`__main__`), nie korzystają z pytest.
- Liczba funkcji w plikach: arkusze_formaty 14, mostki2d 26, fizyka 24, instalacje 24, konstrukcja 28, pipeline 28, rysunki_konstrukcja 12, wskazniki 2.
- W dokumentach są wyniki „x/y” z wcześniejszych przebiegów: 25/25 (pipeline, spec_10–13), 24/24 (fizyka), 22/22 (instalacje, docs/20_koncepcja/weryfikacja_runda2_V2.md), 28/28 (tarcze, spec_29–50), 14/14 (arkusze IE).
- Nie uruchamiałem testów, bo zapisują pliki.

### 3. Dokumentacja
Arkusze liczone na HEAD, bez plików tom*.pdf (także tom_widoki.pdf). Strony policzyłem pypdf; każdy arkusz ma 1 stronę.

| Komplet | Arkusze PDF | MB |
|---|---|---|
| 02_PZT/rysunki | 3 | 0,52 |
| 03_PAB/rysunki | 5 | 1,25 |
| 10_PT_architektura/detale | 6 | 2,03 |
| 04_PT_konstrukcja/rysunki | 26 | 2,75 |
| 05_PT_instalacje_sanitarne/rysunki | 11 | 1,61 |
| 06_PT_instalacje_elektryczne/rysunki | 14 | 1,76 |
| **Razem** | **65** | 9,93 |

Arkusze PT-AR-01…05 w 10_PT_architektura/rysunki na HEAD były jeszcze nieśledzone (0 w git), a na dysku leżało ich 5.

| Tom w projekt/wydanie | Strony | MB |
|---|---|---|
| PZT_PAB_ZL_2026.09.25.pdf | 59 | 4,52 |
| PT_1_AR_2026.09.25.pdf | 49 | 4,50 |
| PT_2_BO_2026.09.25.pdf | 370 | 11,32 |
| PT_3_IS_2026.09.25.pdf | 82 | 3,04 |
| PT_4_WB_2026.09.25.pdf | 49 | 2,89 |
| **Razem: 5 tomów** | **609** | **26,28** |

**Markdown:** słowa to tokeny rozdzielone białymi znakami (`len(text.split())`), razem ze składnią i tabelami.
- docs/: 35 plików, 232 298 słów.
- projekt/: 84 pliki, 426 790 słów.
- **Razem 119 plików, 659 088 słów.**
- W tym 38 plików i 123 341 słów to wyniki testowe w projekt/08_obliczenia/demo_test. Bez nich zostaje 81 plików i 535 747 słów.
- Sam generowany obliczenia_statyczne.md ma 134 079 słów.

### 4. Rejestr wymagań, plansze postępu, mostki cieplne, obliczenia
- **Rejestr wymagań (docs/10_podstawy_prawne/wymagania.yaml):** jako wpis liczę słownik z kluczem `wartosc`, poza sekcją meta.
  - **418 pozycji** w 17 sekcjach.
  - 148 unikalnych identyfikatorów W-xxx; 14 pozycji nie ma identyfikatora.
  - Status: 236 zweryfikowane, 96 niezweryfikowane, 61 założenie, 20 program, 5 interpretacja.
  - Rejestr opisowy 00_rejestr_wymagan.md ma 207 wierszy z unikalnym W-xxx.
- **Plansze postępu raporty/raport_*.png:** **50** (nr 01–50, bez luk) plus 50 plików spec_*.json.
  - Nazwy zaczynają się na 01:22, a kończą na 10:30.
  - Nazwy są w czasie lokalnym UTC+2: porównanie z commitami dodającymi pliki daje różnicę około 119–120 min. W UTC to 23:22Z–08:30Z.
  - Średnio jedna plansza co 11,2 min.
- **Mostki cieplne:**
  - **22 węzły liniowe budynku** (WZ-*): wyniki_mostki.json, zestawienie_mostkow.json i sekcja `wezly` w budynek.yaml podają tę samą liczbę.
  - 4 mostki punktowe χ.
  - 6 wariantów węzłów.
  - Katalog demonstracyjny KOLEJNOSC_DEMO w mostki2d/katalog.py ma 20 węzłów.
- **Obliczenia statyczne:**
  - **132 pozycje w 10 grupach** plus grupa 0 z założeniami (nagłówki „### Poz. N.M” w obliczenia_statyczne.md). Plik wyniki.json też ma 132 pozycje.
  - Podział: ściany 38, nadproża 30, fundamenty 23, belki 17, płyty 11, słupy 8, wieńce 3, schody 2.
  - W wyniki.json jest 48 uwag i 0 braków danych.
  - Poza tym 08_obliczenia ma 11 plików .md z fizyki i energii oraz 10 z instalacji.

### 5. Model (load_model na kopii HEAD; liczby zgodne z sekcjami budynek.yaml)

| Element | Liczba |
|---|---|
| Kondygnacje | 3 (P0, P1, P2) |
| **Ściany** | **57** (23 / 15 / 19) |
| **Otwory** | **50** (24 / 14 / 12): drzwi 20, okna 17, fix 4, drzwi przesuwne HS 3, drzwi zewnętrzne 3, otwory 2, brama 1 |
| **Pomieszczenia** | **33** (16 / 9 / 8): pomocnicze 11, ruchu 10, podstawowe 7, techniczne 5 |
| Przegrody / materiały | 24 / 50 |
| Płyty | 20 (stropy 3, dachy 4, wsporniki 13) |
| Belki / słupy / schody | 38 / 8 / 2 |
| Stolarka (sekcja YAML) | 29 |
| Powierzchnia zabudowy | 187,5 m² (218,08 m² z płytami) |
| Kubatura brutto | 1 354,4 m³ |
| Walidacja | 0 błędów, 0 ostrzeżeń, 389 komunikatów INFO |

budynek.yaml ma 730 linii.

Pełne wyniki są w **/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/repo.json**. Pliki pośrednie (commity.json, pliki.json, dokumentacja.json, rejestr_model.json) i skrypty (commity.py, pliki.py, dokumentacja.py, rejestr_model.py, agreguj_repo.py) są w tym samym katalogu.