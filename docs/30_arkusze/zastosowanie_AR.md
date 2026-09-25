# Zastosowanie silnika ekonomicznego ustawienia na arkuszach — komplet AR (PAB)

Data: 2026-09-25. Konfiguracja: `model/arkusze.yaml`. Wynik: `projekt/03_PAB/rysunki` (PDF, PNG, DXF,
`raport_widokow.json`, `tom_widoki.pdf`). Silnik: `lamela.views.uklad` (format `auto`) i `lamela.draft.skladanie`.

Wymaganie inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

## 1. Wynik

| Stan | Arkuszy | Formaty | Papier [m²] | ≈ A4 | W ważone¹ | W min¹ | W szac.² | Warstwy A4 | Składanie d/p/s |
|---|---|---|---|---|---|---|---|---|---|
| PRZED — `projekt/01_koncepcja/widoki` (dawny dobór A3×n/ISO) | 10 | 1× A1, 6× A3x3, 1× A2x3, 2× A2 | 3,99 | 64 | 54 % | 44 % (AR-05) | — | 96 | 0/10/0 |
| POŚREDNI — silnik `auto`, dotychczasowa konfiguracja | 10 | 10 formatów „na miarę” | 2,84 | 46 | 80 % | 70 % (AR-04) | 67 % | 64 | 3/7/0 |
| **PO — silnik `auto`, nowa konfiguracja** | **5** | 630×594, 770×420, 590×891, 1130×420, 2050×297 | **2,31** | **37** | **84 %** | **74 % (AR-04)** | **69 %** | **50** | **3/2/0** |

¹ `tools/metryki_arkuszy.py` (W obw.). ² `uklad.wypelnienie_szac` z raportu generatora (pasy treści 5 mm) —
ważone polem arkusza. Zmiana PRZED → PO: papier −42 % (−1,68 m² na egzemplarz), liczba arkuszy −50 %, warstwy
A4 w paczce −48 %, żaden arkusz nie składa się „słabo”. Skala wszystkich widoków bez zmian: **1:50** (RPB § 9: PAB
≥ 1:100 — spełnione), pismo bez zmian, tabliczka w prawym dolnym rogu, margines 20 mm po lewej, znaki zgięć
z numerami i oznaczenie formatu niestandardowego („nst. …”) na marginesie każdego arkusza. QA (`plot.qa`) — 0 błędów;
jedyne ostrzeżenie na każdym arkuszu: puste pole projektanta w tabliczce (§ 10 rozp., dane do uzupełnienia).

| Nr | Tytuł (= tabliczka i spis w tomie) | Widoki 1:50 | Format | Pole [m²] | W obw. | Pasy [mm] × rzędy [mm] | Składanie |
|---|---|---|---|---|---|---|---|
| PB-AR-01 | RZUT PARTERU | rzut P0 | 630×594 | 0,374 | 93 % | 210+210+210 × 297+297 (6) | dobre |
| PB-AR-02 | RZUT I PIĘTRA | rzut P1 | 770×420 | 0,323 | 83 % | 160+140+140+140+190 × 297+123 (10) | poprawne |
| PB-AR-03 | RZUT II PIĘTRA I RZUT DACHU | rzut P2 nad rzutem dachu | 590×891 | 0,526 | 86 % | 210+190+190 × 297×3 (9) | dobre |
| PB-AR-04 | PRZEKROJE A-A I B-B | A-A, B-B w wierszu | 1130×420 | 0,475 | 74 % | 210+135×4+190+190 × 297+123 (14) | poprawne |
| PB-AR-05 | ELEWACJE | S, E, N, W w wierszu | 2050×297 | 0,609 | 84 % | 204+184×9+190 × 297 (11) | dobre |

Numeracja: tabliczki „1/5 … 5/5”, spis rysunków w `tom_widoki.pdf` (PB-AR-00) zgodny z tabliczkami. Prefiks i stadium
bez zmian (konfiguracja już była PB — `PB-AR`, stadium PB).

## 2. Decyzje (arkusz po arkuszu)

Każdy arkusz obejrzano w całości i we wycinkach PIL (tabliczka, kolumna opisowa, styki widoków, opisy dachu, legenda).

* **PB-AR-01 rzut parteru** — bez zmian konfiguracji; `auto` daje 630×594 (3×2 pasy po 210 mm, składanie idealne).
* **PB-AR-02 rzut I piętra** — bez zmian; `auto` 770×420. Rozważono P1+P2 na jednym arkuszu (590×891, 0,526 m²
  zamiast 0,614 m²), ale lepsze jest P2 + dach (niżej): oba warianty łącznie z dachem 1,250 vs **1,223 m²**.
* **PB-AR-03 rzut II piętra i rzut dachu** — połączone (dawniej AR-03 490×594 + AR-04 890×594 = 0,82 m²; po samej
  poprawce opisów dachu 0,29 + 0,35 = 0,64 m²; razem **0,526 m²**, 86 %, 590×891 = siatka 3×3 A4). Oba rzuty
  pokazują ten sam zasięg bryły, jeden nad drugim. Rzut dachu był wcześniej rozdmuchany do 890 mm szerokości przez
  jednowierszowe opisy przegród dachu (~400 mm) — nakładały się też na siebie (znane z weryfikacji V1-08). Poprawka
  w module widoku (§ 3) zawija je do ≤ 90 mm.
* **PB-AR-04 przekroje A-A i B-B** — połączone w jeden wiersz na wspólnej linii terenu, więc rzędne kondygnacji obu
  przekrojów leżą na tej samej wysokości. Wspólna legenda materiałów, uwagi bez powtórzeń. Warianty: osobno
  0,214 + 0,307 = 0,521 m²; w kolumnie 580×841 = 0,488 m² (69 %, duże puste pole pod B-B; ten wybrał `auto`, bo
  karze pasy 135 mm); w wierszu **1130×420 = 0,475 m²** (74 %). Zamiast formatu jawnego użyto `max_wysokosc: 594`
  dla tego arkusza: `auto` nadal dobiera długość, a przy zmianie modelu przeliczy się sam. Format jawny przy trwającej
  rundzie poprawek modelu mógłby przejść w układ klasyczny. Pozostaje pas ok. 410×114 mm pod A-A. Wynika z geometrii:
  wiersz przekrojów ma ok. 297 mm wysokości, pod nim zostaje ok. 90 mm, a tabliczka ma 103 mm, więc musi stać obok
  widoków. Kolumna opisowa zajmuje część tego pasa.
* **PB-AR-05 elewacje** — wszystkie cztery w jednym wierszu w kolejności S → E → N → W, czyli rozwinięcie elewacji:
  sąsiednie widoki stykają się tym samym narożnikiem budynku (SE, NE, NW). Mają wspólną linię terenu i rzędne oraz
  jedną tablicę kolorystyki i materiałów (numeracja wspólna na arkuszu). Warianty: osobno 4 arkusze = 0,802 m²;
  S+N 1300×297 i E+W 970×297 = 0,674 m² (dobre); siatka 2×2 1120×594 = 0,665 m² (74 %, poprawne); **pasek 2050×297 =
  0,609 m²** (84 %, dobre, 11 warstw bez zgięć poziomych). Wybrano wynik `auto`. Pasek o długości 2,05 m mieści się
  w limicie `max_dlugosc` 2400 mm. Jeśli długi pasek okaże się niewygodny w obiegu, zamiennikiem jest para arkuszy
  S+N i E+W (+0,065 m²): wystarczy rozdzielić listę `widoki` na dwa arkusze.
* Rozważono też i odrzucono: przekroje + elewacje na wspólnym arkuszu H = 594 (≥ 1,19 m², więcej niż osobno);
  zmianę skali elewacji na 1:100 (dopuszczalna wg RPB, ale bez potrzeby — wymaganie ekonomii spełnione przy 1:50).

## 3. Zmiany w repozytorium

* `model/arkusze.yaml` — nowy układ: 5 arkuszy (sekcja `arkusze`) z komentarzem uzasadniającym; sekcje
  `wspolne` i `przekroje` bez zmian (`format: auto`, skala 50).
* `src/lamela/views/plan.py` (`draw_roof_plan`) — nowa opcja widoku `opis_dachu_szer` [mm]. Zawija opis przegrody
  dachu do szerokości ≤ opcji i ≤ szerokości pola dachu − 8 mm, a rzędną przesuwa pod opis. Bez opcji rysunek jest
  identyczny jak dotąd, więc podkład rzutu dachu IS/IE (`instalacje/podklad.dach`, wywołanie z `{}`) się nie zmienia.
* `src/lamela/views/section.py` — uwaga „opisy warstw pominięte…” zaczyna się od nazwy przekroju („Przekrój A-A: …”).
  Na arkuszu z dwoma przekrojami było wcześniej niejasne, którego dotyczy. Moduł przekrojów jest używany tylko
  przez komplet AR.
* `tools/dokumenty/pab_dane.py` (`arkusze_ref`) — typ arkusza jest odczytywany także z listy `widoki`. Bez tego
  opis techniczny PAB (tom I) straciłby odwołania do rysunków dachu, przekrojów i elewacji po połączeniu widoków.
  `tools/dokumenty/pab_opis_a.py` — numer arkusza „rzut + dach” podawany raz.
* `projekt/03_PAB/rysunki/` — komplet wygenerowany (5 arkuszy + tom). `projekt/01_koncepcja/widoki` bez zmian
  (stan PRZED).

Polecenia:

```
PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze.yaml --out projekt/03_PAB/rysunki
PYTHONPATH=src python3 tools/metryki_arkuszy.py PRZED=projekt/01_koncepcja/widoki PO=projekt/03_PAB/rysunki --md <md>
```

## 4. Błędy i ograniczenia silnika (nie poprawiane w tym kroku — do zespołu silnika)

1. **Kolejność części uwag odwrócona** (`uklad._pakuj_uwagi` / `_umiesc_blok`). Objaw: przy dotychczasowej
   konfiguracji (arkusz PB-AR-05 „PRZEKRÓJ A-A”, 510×420) część „OBJAŚNIENIA I UWAGI (cd.)” z punktami 5–6 stoi na
   samej górze kolumny (y = 386–407 mm), a część pierwsza z punktami 1–4 — niżej (y = 313–341 mm). Czyta się więc
   najpierw ciąg dalszy. Przyczyna (przypuszczalna): każda część trafia w najlepsze wolne miejsce MaxRects (klucz
   preferuje wyższe pola), bez warunku, że część k+1 leży pod częścią k albo w kolumnie po jej prawej/lewej stronie.
   W nowym układzie uwagi mieszczą się w jednym bloku, więc objaw nie występuje, ale błąd zostaje.
2. **Tabela pomieszczeń — przepełnione kolumny** (`sheets._room_table`, poza `uklad`). Tekst posadzki „Deska warstwowa
   dębowa 15 mm, klejona” (kolumna 46 mm) wchodzi na kolumnę „Kat.” (PB-AR-01, 02, 03). Długie nazwy, np. 3.07
   „Pom. techniczne (centrala rekuperacyjna, wyłaz na dach)”, wchodzą na kolumnę „Posadzka”. Brak zawijania albo
   skracania (`fit`/`wrap`) w komórkach `table`. Czytelność: nakładanie się tekstu.
3. **Brak glifu „⌀” (U+2300)** w kroju Liberation Sans (`draft/render.py`: „Glyph 8960 missing”). Na PB-AR-05
   w tablicy materiałów, poz. 10 („pręty ⌀12”, nazwa materiału z modelu), rysuje się pusty prostokąt. Do rozważenia:
   zamiana ⌀ → Ø (U+00D8) w `draft/text` albo krój zapasowy (DejaVu Sans).
4. **Ograniczenie miary W obw.** (`tools/metryki_arkuszy.py`). Na PB-AR-01 wszystkie bloki łączą się domknięciem
   6 mm w jedną składową, której obwiednia obejmuje cały arkusz. Wynik 93 % nie pokazuje pustego pola ok. 230×110 mm
   pod blokiem uwag (lewy dolny róg). Szacunek silnika (`wypelnienie_szac` = 71 %) jest bliższy rzeczywistości.
   Porównania PRZED/PO są spójne, bo oba pomiary mają to samo ograniczenie.
5. Obserwacja (nie błąd): gdy miejsce nad tabliczką zajmuje obwiednia widoku, blok „róża i podziałka” trafia gdzie
   indziej (np. w wariancie pośrednim AR-03 — do prawego górnego rogu). Takie zachowanie jest zgodne z opisem silnika.

## 5. Sprawy pozostałe (moduły widoków / model — poza zakresem układu)

* Rzut dachu: opis „DACH D4” obejmuje fragment „(liczba modułów — energia.pv.pola)” — to tekst z nazwy przegrody
  w modelu (runda poprawek modelu). Strzałki spadku 2,0 % przy D4 dublują się (dwa wpusty na jednej osi). Pola PV,
  czerpnia i wyrzutnia nadal nie są rysowane (weryfikacja V1-08).
* PB-AR-02: składanie „poprawne” (pasy 140 mm, górny rząd 123 mm). Wariant 590×594 („dobre”) kosztuje więcej
  papieru (0,351 vs 0,323 m²), więc `auto` słusznie go odrzuca.
* Model był zmieniany w trakcie pracy (m.in. doszła kratownica pnączy na elewacji E). Arkusze wygenerowano
  z bieżącego stanu modelu. Po zakończeniu rundy poprawek wystarczy przegenerować komplet tym samym poleceniem —
  formaty dobierze `auto` (żaden arkusz nie ma formatu jawnego).
