# Ekonomiczne ustawienie na arkuszach — podsumowanie (po poprawkach z weryfikacji M i C)

Data: 2026-09-25. Wymaganie Inwestora (dosłownie): „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy
sztywno trzymać się geometrii wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

Zakres tej rundy: usunięcie problemów krytycznych i istotnych oraz zasadnych drobnych z `weryfikacja_M.md` (metryki,
składanie, spójność wydania) i `weryfikacja_C.md` (czytelność). Zmiany dotyczą silnika (`src/lamela/views/uklad.py`,
`sheets.py`, `src/lamela/draft/sheet.py`), konfiguracji AR, PZT, IS i IE oraz generatorów widoków, w których weryfikator
C wskazał wady. Kompletów BO i detali nie zmieniano: ani modułów, ani konfiguracji, ani plików wynikowych.

Pomiar: `tools/metryki_arkuszy.py`. Wyniki szczegółowe, arkusz po arkuszu: `metryki_po_poprawkach.md` / `.json`.
Stan wyjściowy: `metryki_stan_wyjsciowy.md`. Stan po 1. rundzie: tabela 2 w `weryfikacja_M.md`.

## 1. Wynik: przed → po

Kolumny: arkusze; papier [m²]; wypełnienie ważone W; najniższe W (arkusz); warstwy paczki A4; ocena składania
d/p/s (dobre / poprawne / słabe); liczba arkuszy z pasem pośrednim harmonijki < 180 mm.

| Komplet | Stan | Arkuszy | Papier | W ważone | W min | Warstwy A4 | Składanie d/p/s | Pasy < 180 |
|---|---|---|---|---|---|---|---|---|
| AR (PAB) | wyjściowy | 10 | 3,99 | 54 % | 44 % | 96 | 0/10/0 | — |
| | po 1. rundzie | 5 | 2,31 | 85 % | 74 % (PB-AR-04) | 50 | 3/2/0 | 2 |
| | **po poprawkach** | **5** | **2,27** | **85 %** | 71 % (PB-AR-04) | **46** | 3/2/0 | **1** |
| PZT | wyjściowy | 3 | 0,75 | 78 % | 77 % | 18 | 0/3/0 | — |
| | po 1. rundzie | 3 | 0,75 | 83 % | 81 % (PZT-01) | 18 | 2/1/0 | 2 |
| | **po poprawkach** | **3** | **0,75** | **91 %** | **86 % (PZT-02)** | 18 | 0/3/0 | **1** |
| IS | wyjściowy | 17 | 6,49 | 51 % | 37 % | 170 | 0/17/0 | — |
| | po 1. rundzie | 11 | 3,84 | 81 % | 71 % (PT-IS-08) | 90 | 3/8/0 | 6 |
| | **po poprawkach** | **11** | **3,69** | **84 %** | **77 % (PT-IS-07)** | **74** | 3/8/0 | **3** |
| IE | wyjściowy | 14 | 5,24 | 51 % | 36 % | 140 | 0/14/0 | — |
| | po 1. rundzie | 14 | 3,58 | 83 % | 66 % (PT-IE-13) | 94 | 3/11/0 | 10 |
| | **po poprawkach** | **14** | **3,36** | **86 %** | **78 % (PT-IE-05)** | **75** | 2/12/0 | **4** |
| **Razem** | wyjściowy | 44 | 16,47 | — | — | 424 | 0/44/0 | — |
| | po 1. rundzie | 33 | 10,48 | — | — | 252 | 11/22/0 | 20 |
| | **po poprawkach** | **33** | **10,07** | — | — | **213** | 8/25/0 | **9** |

Bilans: papier −3,9 % względem 1. rundy i −39 % względem stanu wyjściowego. Paczki A4 mają 213 warstw zamiast 252 (−15 %)
i 424 w stanie wyjściowym (−50 %). Nieregularne harmonijki (pas pośredni < 180 mm) zostały na 9 arkuszach zamiast 20.
Żaden arkusz nie składa się „słabo”. Tabliczka wszędzie jest na wierzchu paczki, w prawym dolnym rogu.

Skale bez zmian (RPB § 9, W-306): AR, IS i IE 1:50, PZT 1:500 + 1:200, schematy bez skali. PDF są wektorowe, bez obrazów
rastrowych. Testy: `tools/test_arkusze_formaty.py` 31/31 (3 nowe testy), `tools/test_pipeline.py` — patrz § 5.

Dlaczego „dobre” jest mniej (11 → 8): arkusze 594 × 430…500 mm („bokiem na rolkę”) mają pasy pionowe 210 + 192 + 192
(ocena „dobre”) i niepełny górny rząd (np. 297 + 143), a za to cała paczka jest „poprawna”. Warianty 690 × 420, które
zastąpiły, też były „poprawne”, tylko z przyczyny pasów 140 + 4 × 120. Paczka ma teraz 6 warstw zamiast 10.
Na PZT „dobre” A2 pionowo (420 × 594) przegrało kosztem z 420 × 530 (−11 % papieru). PZT-02 i PZT-03 zmieniły format,
bo pismo zwiększono do 2,5 mm (W-312) — patrz § 2, pozycja M7.

### Formaty po poprawkach

| Komplet | Arkusze (format) |
|---|---|
| AR | PB-AR-01 620×594 · 02 **594×480** · 03 590×891 · 04 1150×420 · 05 2050×297 |
| PZT | PZT-01 **420×530** · 02 **594×430** · 03 **610×450** (format jawny 620×420 usunięty — `auto`) |
| IS | 01 **610×510** · 02 1130×297 · 03 **594×480** · 04 1130×297 · 05 **594×810** · 06 **594×450** · 07 1310×297 · 08 **594×450** · 09 1310×297 · 10 1410×297 · 11 **510×420** |
| IE | 01 **594×440** · 02 690×297 · 03 570×297 · 04 **594×500** · 05 A2 · 06 **420×450** · 07 **594×470** · 08 690×297 · 09 570×297 · 10, 11, 13 **594×440** · 12 **610×480** · 14 870×297 |

Pogrubiono formaty, które zmieniły się w tej rundzie. Większość to arkusze „bokiem na rolkę”: szerokość jest równa
szerokości rolki (420, 594 lub 610 mm), a wysokość docięta do treści.

## 2. Poprawki — pozycje weryfikacji i ich status

| Poz. | Problem | Poprawka | Status |
|---|---|---|---|
| M § 3 | Silnik nie rozważał arkuszy o szerokości rolki z dociętą wysokością (16 arkuszy za dużych) | `uklad.rozmiesc`: kandydaci „szerokość = rolka” (`rolki`, `min_wysokosc`, `wysokosci_kandydaci`), oceniani tą samą funkcją `koszt()`; do `wysokosci` dopisano 610 i 914 | usunięte; test `test_szerokosc_rolki` |
| M § 3 | `max_wysokosc: 420` przy PT-IS-03/08 blokował tańsze warianty | wymuszenie usunięte z `model/arkusze_is.yaml` | usunięte (594×480, 594×450) |
| M § 4 | 20 arkuszy z pasami < 180 mm | skutek M § 3 | 9 arkuszy (§ 4 — ograniczenia) |
| M § 5 | Wydania PT-3 IS, PT-4 WB i wykazy w opisach miały stare formaty | przebudowane `tom_PT_IS.py`, `tom_PT_IE.py`, `zloz_tom_I.py`, `tom_I_pab.py`, `tom_I_pzt_zl.py`; formaty stron w PDF wydania = `raport_widokow.json` (sprawdzone skryptem) | usunięte |
| M § 6 | PZT-03: format jawny 620×420 był zbędnym obejściem | `format` usunięty (auto), komentarze w YAML poprawione | usunięte |
| M § 7 / W-312 | Pismo 1,8 mm na PZT (uwagi, legenda, nagłówki i przypisy tabel, próbki symboli w legendzie) | opcja silnika `pismo_min` (PZT: 2,5 — uwagi i podziałka); `site_draw`: legenda, tabele kolumny, blok tekstu i próbki symboli 2,5 mm; `draft.sheet.table(h_naglowka=…)` | usunięte: poza tabliczką i marginesem brak napisów < 2,5 mm na PZT-01…03 (analiza PDF) |
| M § 8 | Nieaktualne liczby w `zastosowanie_IS.md` / `_PZT.md`, decyzja PB-AR-04 | poprawione; w każdym `zastosowanie_*.md` odesłanie do tego dokumentu; decyzja PB-AR-04 dopisana w `zastosowanie_AR.md` | usunięte |
| M § 8 | PT-IE-01: pusta przestrzeń nad tabelą OBWODY | nowy format 594×440 | usunięte |
| C 2.1 | PB-AR-01/02/03: opisy urządzeń na ścianach i na sobie; „CWU 300 l” na obu zasobnikach; D4/DG1 i D1/D1 jeden na drugim; „1182”/„857” bez widocznej linii | `plan.py`: opisy urządzeń dłuższe niż symbol (i zasobnika z opisem z modelu) rozmieszczane odnośnikiem z kontrolą kolizji (napis na linii ×4 droższy); znaczniki stolarki z przesunięciem wzdłuż otworu i wariantem po drugiej stronie ściany; linie wymiarów wewnętrznych nie leżą na osiach konstrukcyjnych | usunięte (obejrzane) |
| C 2.2 | PB-AR-04: tabele warstw przecięte liniami, zdublowany tynk „1,5 cm 1 cm”, nagłówki z „…” | `section.py`: białe tło pod całym opisem warstw, tytuł łamany (bez „…”), warstwy sufitu bez powtórzeń; `common.layer_text`: grubość z przegrody zastępuje grubość w nazwie; więcej kandydatów położenia opisów i wymiarów wysokości | usunięte |
| C 2.3 | PZT-02/03: komórki tabel i etykiety sieci ucięte „…” | `site_draw.vp_table`: łamanie komórek do szerokości tabeli (bez zmniejszania pisma); `site.py`: pełne opisy, etykiety sieci i nawierzchni łamane na 2–3 wiersze | usunięte |
| C 2.4 | PT-IE-14: nazwy obwodów ucięte „…” | `schemat_rg`: pełna nazwa do 68 znaków, dłuższa w 2 wierszach; przy bardzo długich listach pomieszczeń: „… i in. (wg tabeli obwodów)” | usunięte |
| C 2.5 | PT-IS-10: średnice na osi podejść; linia TZM na napisie | średnice 1 mm obok linii; maska pod opisami rozwinięć | usunięte |
| C 2.6 | PT-IS-11 / PT-IE-14: blok OZNACZENIA z jedną pozycją; napisy na liniach schematu | legenda schematu przeniesiona z rysunku do bloku OZNACZENIA (linie mediów w kolorach, symbole, skróty); maska pod napisami schematów | usunięte (PT-IS-11: 580×420 → 510×420) |
| C 2.7 | Brak siatki odniesień na 7 arkuszach niestandardowych | `draft/sheet.py`: siatka, gdy dłuższy bok > 420 mm | usunięte; test `test_siatka_formaty_niestandardowe` |
| C 2.8 | PT-IE-07: róża i podziałka daleko od tabliczki, puste pola | nowy format 594×470 — róża i podziałka w dolnym pasie przy tabliczce, jak na PT-IE-01 | usunięte |
| C 2.9 | PT-IE-13 prawie pusty | format 594×440 (−10 % papieru, W 82 %); scalenia z PT-IE-10 nie zrobiono | częściowo (§ 4) |
| C 2.10 | Bloki licujące z ramką, tytuł 2,5 mm od znaku centrującego | bloki mają 177 mm szerokości, 3 mm od prawej ramki (lewa krawędź jak tabliczka); tytuł ≥ 4 mm od znaku | usunięte; test `test_bloki_odsuniete_od_ramki` |
| C 2.11 | PB-AR-03: legenda linii oderwana od legend | `sheets._bloki_ukladu`: legendy kreskowań i linii w jednym bloku | usunięte |
| C 2.12 | Napisy przecięte liniami (dach D1/D4, PZT) | maska opisów dachu 0,8 mm domyka odstępy między wierszami; PZT — etykiety łamane (C 2.3) | usunięte na dachu; PZT częściowo (§ 4) |
| C 2.13 | Metryka zawyża W przy dużym pustym polu | `metryki_arkuszy.py`: największy pusty prostokąt liczony na częściach bloków (jak W skł.) | usunięte |

## 3. Konfiguracja silnika — instrukcja dla zespołów BO i detali

Oba komplety (`model/arkusze_bo.yaml`, `model/arkusze_detale.yaml`) mają już `format: auto`, więc korzystają z silnika
`lamela.views.uklad`. Zmiany tej rundy zadziałają przy najbliższym przegenerowaniu tych kompletów, bez zmian w ich
konfiguracji: kandydaci „szerokość = rolka”, bloki kolumny 177 mm z odstępem 3 mm od ramki, tytuły widoków ≥ 4 mm od
znaków centrujących, siatka odniesień na formatach > 420 mm. Po przegenerowaniu należy sprawdzić arkusze
(`raport_widokow.json`: `uklad.kolizje`, `kolejnosc_czytania`; PNG) i uruchomić `tools/metryki_arkuszy.py`.

**Jak włączyć silnik w komplecie (lub w nowym typie widoku):**

1. W `wspolne` pliku `model/arkusze_*.yaml` ustawić `format: auto`. Tę samą wartość można podać per arkusz. Inne tryby:
   `standardowy` (tylko ISO 216 i wydłużone PN-EN ISO 5457, nowe upakowanie), `klasyczny` (dawny algorytm),
   nazwa (`A2`, `A3x3`), wymiary `"594x440"` (szer. × wys.) albo `[H, L]`. Format jawny używać tylko z uzasadnieniem
   w komentarzu, bo „przypięty” format nie korzysta z poprawek silnika (przykład: dawny PZT-03 620×420).
2. Widok rejestrowany przez `sheets.register_view(typ, fn, rodzaj, qa)` zwraca rzutnię i wynik z polami:
   `column_blocks` (lista `(nazwa, fn(sh, x, y_top, w) → y_bottom)`), `notes`, `bez_skali`, `north`.
   Blok **musi** rysować się w szerokości `w`, którą dostaje. Silnik podaje 177 mm (`uklad.B_W`). Blok o stałej
   szerokości 180 mm wystaje 3 mm i traci wyrównanie z tabliczką. Bloki zależne od stanu arkusza (legenda raz na
   arkusz, ciąg dalszy tabeli) silnik łączy sam (`bloki_z_kolumny`).
3. Wiele widoków na jednym arkuszu: lista `widoki:` w arkuszu. Silnik sprawdza warianty wiersz / kolumna / siatka.
   Widoki, które muszą stać w jednym wierszu (wspólna linia terenu, jak PB-AR-04), wymusza się ograniczeniem
   `max_wysokosc`.

**Parametry** (`wspolne` lub arkusz; wszystkie opcjonalne, domyślne w `uklad.DOMYSLNE`):

| Parametr | Domyślnie | Znaczenie |
|---|---|---|
| `format` | `auto` | tryb / format (patrz wyżej) |
| `wysokosci` | 297, 420, 594, 610, 841, 891, 914 | wysokości H arkuszy „na miarę” (długość L docinana do treści, krok `krok_dlugosci`) |
| `rolki` | 297, 420, 594, 610, 841, 914 | szerokości arkuszy „bokiem na rolkę” (wysokość docinana, ≥ 297 mm); `[]` wyłącza |
| `krok_dlugosci` | 10 mm | siatka długości i wysokości docinanych |
| `max_wysokosc` / `max_dlugosc` | 914 / 2400 mm | ograniczenia (dotyczą też arkuszy „bokiem na rolkę”) |
| `modul_skladania` | `auto` | `auto`: długości do +35 % oceniane kosztem; liczba m: tylko L = 210 + m·n; 0: najmniejsza |
| `kara_niestandard` | 0,03 | dopłata kosztu za format spoza ISO 216 / 5457 |
| `kara_skladania` | dobre 0 / poprawne 0,04 / słabe 0,10 | kara na kierunek składania (`lamela.draft.skladanie`) |
| `kara_czesci_uwag`, `max_czesci_uwag` | 0,02, 4 | podział bloku uwag na części |
| `kara_kolejnosci`, `kolejnosc_uwag` | 0,01, `czytania` | kolejność czytania bloków (kolumnami od lewej) |
| `wolne_obszary` | true | bloki także w pustych narożnikach obwiedni widoków |
| `odstep_widok_blok` | 10 mm | odstęp widok ↔ blok |
| `znaki_centrujace` | `auto` | `rezerwuj` / `skracaj` — strefy znaków centrujących |
| `pismo_min` | 1,8 mm | pismo uwag i podziałki w kolumnie opisowej (PZT: 2,5 — W-312) |

**Koszt** = pole arkusza × (1 + kary składania) × (1 + kara niestandardu) × (1 + kary układu). Wybierany jest
kandydat o najmniejszym koszcie. Wynik i 6 najlepszych kandydatów zapisuje się w `raport_widokow.json`
(`uklad.kandydaci`), co pozwala uzasadnić wybór formatu. Składanie: harmonijka do 210 mm (pierwszy pas z marginesem
20 mm, pas z tabliczką ≥ 190 mm na wierzchu), potem zgięcia poziome co 297 mm od dołu. Znaki i numery zgięć są
na marginesie arkusza.

**Kontrola** (każde wywołanie generatora): `uklad.sprawdz_nakladanie` (nakładanie, wyjście poza ramkę, odstępy),
`uklad.kolizje_znakow` (znaki centrujące a treść), wysokość tabliczki, `plot.qa`, pomiar W na PDF
(`uklad.wypelnienie_pdf`). Testy silnika: `PYTHONPATH=src python3 tools/test_arkusze_formaty.py [--szybko]`.
