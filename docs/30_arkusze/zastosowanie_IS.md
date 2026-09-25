# Zastosowanie silnika ekonomicznego ustawienia na arkuszach — komplet IS (PT instalacje sanitarne)

Data: 2026-09-25. Konfiguracja: `model/arkusze_is.yaml`. Wynik: `projekt/05_PT_instalacje_sanitarne/rysunki` (PDF, PNG,
DXF, `raport_widokow.json`, `tom_PT-IS.pdf` ze spisem rysunków PT-IS-00) oraz `projekt/05_PT_instalacje_sanitarne/
BRAKI_DANYCH.md`. Silnik: `lamela.views.uklad` (format `auto`) i `lamela.draft.skladanie`.

> **Aktualizacja (runda poprawek po weryfikacji, 2026-09-25):** tabele i formaty poniżej opisują stan po pierwszym wdrożeniu silnika (stan zweryfikowany w `weryfikacja_M.md` / `weryfikacja_C.md`). Stan bieżący (kandydaci „szerokość = rolka”, pismo PZT ≥ 2,5 mm, poprawki czytelności) — `docs/30_arkusze/podsumowanie.md`.


Wymaganie inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

## 1. Wynik

| Stan | Arkuszy | Formaty | Papier [m²] | ≈ A4 | W ważone¹ | W min¹ | W szac.² | Warstwy A4 | Składanie d/p/s |
|---|---|---|---|---|---|---|---|---|---|
| PRZED — stan wyjściowy (`metryki_stan_wyjsciowy.md`) | 17 | 16× A3x3, 1× A1 | 6,49 | 104 | 51 % | 37 % (IS-06) | — | 170 | 0/17/0 |
| POŚREDNI — silnik `auto`, dotychczasowa konfiguracja (17 ark.) | 17 | 12 formatów „na miarę”, 5× A2 | 4,39 | 70 | 80 % | 68 % (IS-06) | 69 % | 108 | 1/16/0 |
| **PO — silnik `auto`, nowa konfiguracja** | **11** | 790×420, 2× 1130×297, 3× 710×420, 590×841, 2× 1320×297, 1410×297, A2 | **3,85** | **62** | **82 %** | **71 % (IS-08)** | **71 %** | **90** | **3/8/0** |

¹ `tools/metryki_arkuszy.py` (W obw.). ² `uklad.wypelnienie_szac` z raportu generatora, ważone polem arkusza.
Zmiana PRZED → PO: papier −41 % (−2,64 m² na egzemplarz), arkuszy −35 %, warstwy A4 w paczce −47 %; względem
samego przełączenia silnika (POŚREDNI) dodatkowo −0,54 m² (−12 %) i −6 arkuszy. Żaden arkusz nie składa się „słabo”.

Skale bez zmian: rzuty **1:50** (RPB § 9 ust. 3, W-306: PT ≥ 1:100 — spełnione), schematy bez skali (rzędne w skali
jak dotąd). Pismo bez zmian. Na każdym arkuszu: tabliczka w prawym dolnym rogu (na wierzchu po złożeniu), margines
20 mm po lewej, znaki zgięć z numerami, oznaczenie formatu niestandardowego „nst. …” na marginesie, legenda symboli
(W-308). QA (`plot.qa`) — 0 błędów; jedyne ostrzeżenie na każdym arkuszu: puste pole projektanta w tabliczce (§ 10).

Pomiar PRZED wzięto z `docs/30_arkusze/metryki_stan_wyjsciowy.md`. W katalogu wynikowym przed tą zmianą leżał już
PT-IS-01 790×420 z próbnego przebiegu silnika (raport wskazywał A3x3), więc ponowny pomiar tego katalogu dawał 6,44 m².

| Nr | Tytuł (= tabliczka i spis w tomie) | Widoki | Format | Pole [m²] | W obw. | Pasy [mm] × rzędy [mm] (warstwy) | Składanie |
|---|---|---|---|---|---|---|---|
| PT-IS-01 | INSTALACJA WODOCIĄGOWA — RZUT PARTERU | IS-W P0 1:50 | 790×420 | 0,332 | 81 % | 165+145×3+190 × 297+123 (10) | poprawne |
| PT-IS-02 | INSTALACJA WODOCIĄGOWA — RZUTY I PIĘTRA I II PIĘTRA | IS-W P1, P2 (wiersz) | 1130×297 | 0,336 | 81 % | 210+135×4+190+190 × 297 (7) | poprawne |
| PT-IS-03 | KANALIZACJA SANITARNA — RZUT PARTERU | IS-K P0 | 710×420 | 0,298 | 77 % | 145+125×3+190 × 297+123 (10) | poprawne |
| PT-IS-04 | KANALIZACJA SANITARNA — RZUTY I PIĘTRA I II PIĘTRA | IS-K P1, P2 (wiersz) | 1130×297 | 0,336 | 81 % | 210+135×4+190+190 × 297 (7) | poprawne |
| PT-IS-05 | ODWODNIENIE DACHÓW — RZUT DACHU I RZUT PARTERU | IS-D dach nad P0 (kolumna) | 590×841 | 0,496 | 89 % | 210+190+190 × 297+297+247 (9) | poprawne |
| PT-IS-06 | OGRZEWANIE — RZUT PARTERU | IS-CO P0 | 710×420 | 0,298 | 95 % | 145+125×3+190 × 297+123 (10) | poprawne |
| PT-IS-07 | OGRZEWANIE — RZUTY I PIĘTRA I II PIĘTRA | IS-CO P1, P2 (wiersz) | 1320×297 | 0,392 | 77 % | 205+185×5+190 × 297 (7) | dobre |
| PT-IS-08 | WENTYLACJA MECHANICZNA — RZUT PARTERU | IS-WM P0 | 710×420 | 0,298 | 71 % | 145+125×3+190 × 297+123 (10) | poprawne |
| PT-IS-09 | WENTYLACJA MECHANICZNA — RZUTY I PIĘTRA I II PIĘTRA | IS-WM P1, P2 (wiersz) | 1320×297 | 0,392 | 83 % | 205+185×5+190 × 297 (7) | dobre |
| PT-IS-10 | KANALIZACJA I WODOCIĄG — ROZWINIĘCIA | rozwinięcie kanalizacji + wodociągu (wiersz) | 1410×297 | 0,419 | 78 % | 210+200×6 × 297 (7) | dobre |
| PT-IS-11 | SCHEMAT POMPY CIEPŁA, C.O. I C.W.U. | schemat PC | 580×420 (nst.; wcześniej A2 594×420) | 0,244 | 85 % | 210+192+192 × 297+123 (6) | poprawne |

Numeracja ciągła PT-IS-01…11. Tabliczki mają „1/11 … 11/11”. Spis rysunków w `tom_PT-IS.pdf` (PT-IS-00) zgadza się
z tabliczkami: numery, tytuły, skale i formaty sprawdzono w tekście PDF. `BRAKI_DANYCH.md` odwołuje się do nowych
numerów (PT-IS-01…09).

## 2. Decyzje (arkusz po arkuszu)

Obejrzano każdy arkusz w wariancie pośrednim, w wariantach próbnych i w wersji końcowej. Oglądano całe arkusze
i wycinki PIL: kolumnę opisową, tabliczkę, styk widoków, strefy znaków centrujących i dół rzutów.

* **Rzuty I i II piętra (W, K, CO, WM) — połączone w jeden arkusz na branżę.** Osobno każdy zajmował 690×297
  (W, K) albo A2 (CO, WM). Rzut II piętra jest mały: jedna łazienka dla W i K, a na arkuszach zostawały duże puste
  pola (W = 64–68 %). W jednym wierszu oba rzuty mają te same osie i tę samą wysokość. Legenda i uwagi występują
  raz, a tabele kondygnacji (pętle P1/P2, strumienie P1/P2) mają różne tytuły.
  * W, K: 2× 0,205 → **0,336 m²** (−0,074 m² na branżę).
  * CO, WM: 2× 0,249 → **0,392 m²** (−0,107 m² na branżę), składanie „dobre” (pasy 185 mm).
  * `auto` wybrało wiersz H = 297. Kandydaci: 940×420 i 690×594 są droższi o 5–20 %.
* **Rzuty parteru z piętrami na jednym arkuszu — rozważone i odrzucone.** Wiersz P0+P1+P2 przy H = 420 zajmuje ok.
  1800×420 = 0,76 m², a osobno 0,67 m². Przy H ≥ 594 rzuty nie mieszczą się w jednej kolumnie. Rzut parteru każdej
  branży zostaje osobno.
* **PT-IS-01, PT-IS-06 (W, CO — parter)** — bez zmian konfiguracji. `auto` daje 790×420 i 710×420. Wariant
  610×594 / 590×594 („dobre”) kosztuje o 1–9 % więcej.
* **PT-IS-03, PT-IS-08 (K, WM — parter)** — `max_wysokosc: 420` (nie format jawny: długość nadal dobiera `auto`).
  `auto` wybierało 520×594 o koszcie 0,3309 wobec 0,3317 dla 710×420 (różnica 0,2 %, w granicach kary za składanie).
  Papier jednak rośnie: 0,309 vs **0,298 m²**. Na 520×594 rzut WM zostawiał pusty pas ok. 290×110 mm pod rzutem
  i 115×125 mm nad nim. Na 710×420 cztery rzuty parteru mają jednakowy układ (rzut po lewej, kolumna nad tabliczką,
  format 710–790×420), więc łatwiej je porównywać między branżami. Koszt: 10 warstw A4 zamiast 6.
* **PT-IS-05 (odwodnienie)** — rzut dachu nad rzutem parteru z rurami spustowymi. Ten sam zasięg budynku i te same
  osie, rury RS1–RS6 w jednej pionowej linii. Osobno: 690×420 + 580×594 = 0,635 m². Razem **590×841 = 0,496 m²**,
  89 %. Tabela „WYNIKI OBLICZEŃ — ODWODNIENIE DACHÓW” (całego budynku) występuje raz, a nie dwa razy (§ 3).
  Wariant 580×891 („dobre”) ma koszt praktycznie równy (0,5323 vs 0,5315), ale większe pole — `auto` wybrało
  mniejsze pole.
* **PT-IS-10 (rozwinięcia kanalizacji i wodociągu)** — jeden pasek H = 297. Osobno 730×297 + 750×297 = 0,440 m²,
  razem **1410×297 = 0,419 m²**. Składanie „dobre” (pasy 200 mm, 7 warstw zamiast 10), wspólna legenda przewodów.
  Schematy są z natury rzadkie (W kontur 30 %), ale nie da się ich zagęścić układem arkusza. Pionowa oś rzędnych
  schematów pozostaje w skali.
* **PT-IS-11 (schemat PC)** — po przegenerowaniu 580×420 (dawniej A2; 85 %). Łączenie ze schematami H = 297 albo z rzutami c.o. zwiększało
  papier: 1640×420 = 0,69 m² wobec 0,67 m² osobno.
* Tytuły arkuszy łączonych: „RZUTY I PIĘTRA I II PIĘTRA” zamiast „RZUTY I I II PIĘTRA” (wielkie litery „I I II” są
  nieczytelne). Tytuły widoków pozostały bez zmian („… — RZUT I PIĘTRA”, „… — RZUT II PIĘTRA”).
* Formatu jawnego nie użyto nigdzie. Po rundzie poprawek modelu wystarczy przegenerować komplet — długości
  arkuszy dobierze `auto`.

## 3. Zmiany w repozytorium

* `model/arkusze_is.yaml` — nowy układ: 11 arkuszy (sekcja `arkusze`) z komentarzem uzasadniającym. Sekcja `wspolne`
  bez zmian (`format: auto`, skala 50). W arkuszach wielowidokowych każdy widok ma powtórzone `nr`. Widoki z listy
  `widoki` nie dziedziczą pól arkusza, a bez `nr` moduł instalacji zapisywał braki danych bez numeru arkusza
  (`BRAKI_DANYCH.md`, kolumna „Arkusze”) — patrz § 4 p. 4.
* `src/lamela/views/instalacje/wspolne.py`:
  * `Legenda._order` i `Legenda.suma()` — legenda łączna kilku widoków, pozycje bez powtórzeń;
  * `legenda_arkusza(ctx, leg)` — blok legendy wspólnej dla widoków jednego arkusza. Widoki arkusza powstają przed
    pomiarem bloków, więc legendy (o tym samym tytule) utworzone od ostatniego rysowania legendy tworzą grupę arkusza.
    Pierwszy blok rysuje sumę legend, kolejne nic nie rysują i silnik (`uklad.bloki_z_kolumny`) je pomija. Na
    arkuszu z jednym widokiem wynik jest identyczny jak dotąd. Sprawdzono też na PT-IE-01/02 (komplet IE korzysta
    z tej samej klasy bazowej) — jedna legenda, bez zmian;
  * `table_block(..., raz_na_arkusz=klucz)` — tabela wspólna kilku widoków rysowana raz na arkusz.
* `src/lamela/views/instalacje/baza.py` (`Rysunek.finish`) i `sch_kan.py` (rozwinięcia) — legenda przez
  `legenda_arkusza`. `is_desz.py` — tabela wyników odwodnienia z `raz_na_arkusz="desz"` (dotąd na arkuszu
  „dach + parter” byłaby dwa razy).
* `projekt/05_PT_instalacje_sanitarne/rysunki/` — komplet wygenerowany od nowa. Stare pliki 17 arkuszy usunięto, bo
  nazwy i numery się zmieniły. `BRAKI_DANYCH.md` przegenerowany.

Polecenia:

```
PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_is.yaml --out projekt/05_PT_instalacje_sanitarne/rysunki
PYTHONPATH=src python3 tools/metryki_arkuszy.py PO=projekt/05_PT_instalacje_sanitarne/rysunki --md <md> --podglad <katalog>
```

## 4. Błędy i ograniczenia silnika (nie poprawiane — do zespołu silnika)

1. **Znaki centrujące nachodzą na treść.** Znaki rysuje `draft.sheet.Sheet._draw_frame`: 0,7 mm, 10 mm w głąb
   ramki na osiach symetrii arkusza. Silnik (`uklad.rama`, `PAD_V` = 6 mm, `PAD_B` = 3 mm, `Wolne`,
   `sprawdz_nakladanie`) nie rezerwuje ich stref, więc raport pokazuje „kolizje: []”, choć na arkuszach są
   nałożenia:
   * PT-IS-02 i PT-IS-04 — dolny znak (x = 565 mm) przecina tytuł widoku „… — RZUT II PIĘTRA”;
   * PT-IS-09 — dolny znak (x = 660 mm) przecina koniec tytułu widoku „… — RZUT II PIĘTRA”;
   * PT-IS-06 — dolny znak (x = 355 mm) przecina blok „OBJAŚNIENIA I UWAGI (cd.)”, pkt 5;
   * PT-IS-02/04/07/09 — prawy znak (y = H/2) dotyka litery „N” róży kierunków w bloku „róża i podziałka”
     zakotwiczonym nad tabliczką.

   Przyczyna: pole ramki traktowane jako w pełni wolne. Propozycja: zająć w `Wolne` i w obwiedni grupy widoków
   prostokąty ok. 2×(10+odstęp) mm przy czterech znakach centrujących. Do sprawdzenia także długość: PN-EN ISO 5457
   p. 4.3 podaje, według naszej wiedzy, ok. 5 mm poza ramkę do wnętrza — sprawdzić z tekstem normy.
2. **Uwagi dzielone na części w kolejności nieprzestrzennej** — ten sam mechanizm co w błędzie 1 z
   `zastosowanie_AR.md` (`uklad._pakuj_uwagi`). Na PT-IS-06 (c.o. parter, 710×420) uwagi mają 3 części:
   * pkt 1–3 — kolumna prawa, środek wysokości;
   * pkt 4–5 „(cd.)” — dół arkusza obok legendy, na lewo od tabliczki;
   * pkt 6–7 „(cd.)” — kolumna prawa, tuż nad tabliczką.

   Czytając kolumnę z góry, po pkt 3 trafia się na pkt 6. Kolumnę nad tabliczką rozbija opis pompy ciepła
   (etykieta PC wychodzi z rzutu w prawo, ok. 155–165 mm nad dolną krawędzią), więc podział jest uzasadniony, ale kolejność części nie
   jest.
3. **Kolejność bloków w kolumnach opisowych.** Kolejne kolumny są dokładane w lewo. Na PT-IS-07 blok
   „PĘTLE … — P1” stoi w kolumnie prawej pod legendą, a „PĘTLE … — P2” w kolumnie lewej u góry — czytając od
   lewej, P2 wypada przed P1. Tak samo na PT-IS-09 (uwagi po lewej, a legenda i tabele P1/P2 po prawej). Zgodne
   z opisem silnika, ale odwraca porządek czytania. Do rozważenia: przy więcej niż jednej kolumnie przypisywać
   bloki do kolumn od lewej w kolejności listy.
4. **API: widoki z listy `widoki` nie dostają numeru arkusza** (`sheets._przygotuj`: `vspecs = [dict(vs) …]`).
   Moduły rejestrowane (`register_view`) nie znają więc `nr`, a instalacje zapisują przez to braki danych bez
   odwołania do arkusza. Obejście: `nr` w każdym widoku w YAML. Propozycja: `vs.setdefault("nr", spec["nr"])`
   w `_przygotuj`.
5. **Bloki kolumny kilku widoków są sklejane bez scalania** (`_przygotuj`: `col.add(nm, fn)` dla każdego widoku).
   Dwie legendy albo dwie identyczne tabele pojawiają się na arkuszu dwukrotnie. Dla IS obsłużono to w module
   blokami zależnymi od stanu arkusza (§ 3), które silnik obsługuje poprawnie. Warto opisać ten kontrakt w
   `register_view` albo scalać bloki o tej samej nazwie i treści w `sheets`.

## 5. Sprawy pozostałe (poza układem arkuszy)

* **Tom PT-3 IS** (`tools/dokumenty/tom_PT_IS.py`, `projekt/09_opis_i_zalaczniki/PT_IS/PT_IS_opis.md`) odwołuje się
  do starej numeracji (PT-IS-01…17). Generator czyta listę arkuszy z `raport_widokow.json`, więc po rundzie poprawek
  modelu wystarczy przegenerować tom. Kodu nie trzeba zmieniać.
* Schemat PC (PT-IS-11, `lamela.obliczenia.sanitarne.schemat_pc`) pokazuje rozdzielacze P0 i P1, a brak na nim
  rozdzielacza R-P2 (7 obiegów), który jest na PT-IS-07 — treść obliczeń, nie układ.
* PT-IS-01, -03, -06, -08: składanie „poprawne” (pasy 125–145 mm, górny rząd 123 mm). Warianty H = 594 („dobre”)
  kosztują 1–9 % więcej papieru, więc wybrano ekonomię zgodnie z wymaganiem.
* Model był zmieniany w trakcie pracy (m.in. liczba pętli P0 i tabliczka z polami [DO UZUPEŁNIENIA]). Arkusze
  wygenerowano z bieżącego stanu, więc po zakończeniu rundy poprawek wystarczy ponowić polecenie z § 3.
