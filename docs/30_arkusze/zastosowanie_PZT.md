# Zastosowanie ekonomicznego ustawienia na arkuszach — komplet PZT

Data: 2026-09-25. Komplet: projekt zagospodarowania działki (PZT-01…PZT-03). Konfiguracja: `model/arkusze_pzt.yaml`.
Wynik: `projekt/02_PZT/rysunki` (PDF, PNG, DXF, `tom_PZT.pdf`, `raport_widokow.json`). Silnik: `lamela.views.uklad`
(format `auto` = ekonomiczny), składanie: `lamela.draft.skladanie`. Pomiar: `tools/metryki_arkuszy.py` (ta sama metoda
co w `metryki_stan_wyjsciowy.md`).

Wymaganie Inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

Polecenia:

```
PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_pzt.yaml --out projekt/02_PZT/rysunki
PYTHONPATH=src python3 tools/metryki_arkuszy.py PZT=projekt/02_PZT/rysunki --md <md> --json <json> --podglad <png>
```

## 1. Wynik — przed i po

| Stan | Arkuszy | Formaty | Papier [m²] | ≈ A4 | W ważone | W średnie | W min (arkusz) | Puste [m²] | Warstwy A4 | Składanie (dobre/poprawne/słabe) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Przed** — stan wyjściowy (dawny algorytm, pliki z repozytorium) | 3 | 3× A2 (594×420) | 0,75 | 12 | 78 % | 78 % | 77 % (PZT-02) | 0,15 | 18 | 0/3/0 |
| Silnik `auto` bez zmian konfiguracji (model po bieżącej rundzie) | 3 | A2 pion., 400×594, 580×594 | 0,83 | 13,3 | 73 % | 75 % | 64 % (PZT-03) | — | 18 | 3/0/0 |
| **Po** — silnik + poprawki konfiguracji | 3 | A2 pion. (420×594), 400×594, 620×420 | **0,75** | **12,0** | **82 %** | **82 %** | **77 % (PZT-01)** | **0,12** | 18 | **2/1/0** |

| Nr | Skala | Przed | Po | Pole przed → po [m²] | W obw. przed → po | Pasy / rzędy po [mm] | Składanie po |
|---|---|---|---|---|---|---|---|
| PZT-01 | 1:500 | A2 594×420 | A2 pionowo 420×594 | 0,249 → 0,249 | 79 % → 77 % | 125 + 105 + 190 / 297 + 297 | dobre |
| PZT-02 | 1:200 | A2 594×420 | nst. 400×594 | 0,249 → 0,238 | 77 % → 85 % | 115 + 95 + 190 / 297 + 297 | dobre |
| PZT-03 | 1:200 | A2 594×420 | nst. 620×420 | 0,249 → 0,260 | 80 % → 84 % | 210 + 205 + 205 / 297 + 123 | poprawne (górny rząd 123 mm) |

Porównywalność: w trakcie pracy trwała runda poprawek modelu. W `dzialka.yaml` przybyły kolektory kd5…kd8
i przyłącza, więc tabele PZT-03 urosły ze ~13 do 22 wierszy w tabeli koordynacji. Doszło też 1078 rzędnych
projektowanych (TIN) i „zielona ściana”. Z dzisiejszą treścią dawny układ nie zmieściłby PZT-03 na A2: wariant
`format: A2` daje układ klasyczny z przyciętym widokiem, co sprawdzono. Uczciwym punktem odniesienia dla tej samej
treści jest więc wiersz „silnik auto bez zmian konfiguracji” (0,83 m²). Względem niego wynik to −10 % papieru
i +9 p.p. wypełnienia. Względem stanu wyjściowego ta sama ilość papieru mieści więcej treści. Składanie 2× dobre
zamiast 3× poprawne: rzędy 2 × 297 mm zamiast 297 + 123. Paczka ma 18 warstw A4, tak jak przed.

Skale bez zmian: PZT-01 1:500, PZT-02 i PZT-03 1:200. Spełniają W-306 (RPB § 9 ust. 5: PZT nie mniejsza niż
1:500 plus rysunek szczegółowy 1:200). Pismo bez zmian: tabele 2,5 mm, jak w rzutni. Tabliczka jest w prawym
dolnym rogu, na wierzchu paczki. Margines 20 mm po lewej, znaki zgięć z numerami na marginesie, oznaczenie
„nst. L×H” formatów niestandardowych. Numeracja w tabliczkach: 1/3, 2/3, 3/3. Spis rysunków w `tom_PZT.pdf`
(strona A4, PZT-00) podaje formaty „A2”, „400×594”, „620×420”. Tom ma 4 strony w wymiarach nominalnych. Kolizje
w raporcie układu: brak na wszystkich arkuszach. QA: 0 błędów, 1 ostrzeżenie na arkusz (pole projektanta
[DO UZUPEŁNIENIA] — § 10 rozp.).

## 2. Decyzje arkusz po arkuszu

### PZT-01 — plan zagospodarowania 1:500 → A2 pionowo (format auto, konfiguracja bez zmian)

* Kandydaci silnika: A2 420×594 (koszt 0,2495, dobre); 600×420 (0,252 m², poprawne); 410×841; A3×3.
* H = 297 jest niemożliwe. Mapa z opisem podkładu („MAPA DO CELÓW PROJEKTOWYCH — PODKŁAD PRZYKŁADOWY”) ma 285 mm
  wysokości, a pole ramki na wysokości 297 ma 277 mm minus odstępy. Zmniejszenie `otoczenie` (25 m) obcięłoby
  kontekst mapy do celów projektowych (sąsiednie działki, droga, pikiety). Nie robimy tego dla kilku procent papieru.
* Wariant `tabele: kolumna` daje ten sam format i wypełnienie 77 %, ale uwagi lądują w lewym górnym rogu nad mapą.
  Zostaje wariant domyślny: tabele wskaźników i odległości w rzutni, obok mapy, na wysokości rysunku.
* Pozostaje puste pole 210×164 mm w lewym dolnym rogu, pod uwagami (0,034 m²). Mniejszego arkusza dla tej treści
  nie ma, bo szerokość 420 = mapa 190 + kolumna 180 + marginesy.

### PZT-02 — plan szczegółowy 1:200 → 400×594 (format auto, konfiguracja bez zmian)

* Kandydaci: 400×594 (0,2376 m², koszt 0,2447, dobre); A2 594×420 (0,2595, poprawne). Wypełnienie 85 %.
  Najmniejszy pusty prostokąt w komplecie to 164×78 mm.
* `tabele: kolumna` dawałby 610×420 (0,256 m², 76 %, poprawne), czyli gorzej. Tabele zostają w rzutni.
* Naprawiony błąd modułu widoku: opis rzędnych projektowanych, sekcja 3.

### PZT-03 — rysunek koordynacyjny 1:200 → 620×420 (tabele jako bloki, format jawny — uzasadnienie)

| Wariant | Format | Pole [m²] | W obw. | Składanie | Uwagi |
|---|---|---|---|---|---|
| tabele w rzutni, auto | 580×594 | 0,345 | 63 % | dobre | tabele 408 mm > mapa 330 mm; puste 196×236 mm pod legendą |
| tabele w rzutni, `A2` | 594×420 | 0,249 | 59 % | poprawne | nie mieści się, układ klasyczny, widok przycięty |
| `tabele: kolumna`, auto | 610×420 | 0,256 | 89 % | poprawne | uwagi w 3 częściach, „(cd.)” 6–7 nad mapą, poz. 8 osobno — **nieczytelne** |
| `kolumna`, `modul_skladania: 205` | 620×420 | 0,260 | 84 % | poprawne | wyśrodkowanie grupy znów dzieli uwagi na 3 części (błąd silnika 3) |
| `kolumna`, `620x420` | 620×420 | 0,260 | 84 % | poprawne | uwagi w jednym bloku; znak centrujący przecina tytuł tabeli „OBIEKTY…” |
| **`kolumna`, `620x420`, `kolejnosc_tabel`** | **620×420** | **0,260** | **84 %** | **poprawne** | **wybrany**: uwagi w całości, nic nie koliduje |
| `kolumna`, `630x420` / `650x420` | — | 0,265 / 0,273 | 82 % / 80 % | poprawne / słabe | bez korzyści |
