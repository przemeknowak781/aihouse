# Zastosowanie silnika ekonomicznego ustawienia na arkuszach — komplet IE (PT-IE-01…14)

Data: 2026-09-25. Komplet: projekt techniczny — instalacje elektryczne, 14 arkuszy, rzuty 1:50 i schemat RG (bez skali).
Konfiguracja: `model/arkusze_ie.yaml`. Wynik: `projekt/06_PT_instalacje_elektryczne/rysunki` (PDF, PNG, DXF,
`raport_widokow.json`, `tom_PT-IE.pdf`).

Wymaganie inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

Polecenia:

```
PYTHONPATH=src python3 tools/generuj_widoki.py --arkusze model/arkusze_ie.yaml --out projekt/06_PT_instalacje_elektryczne/rysunki
PYTHONPATH=src python3 tools/metryki_arkuszy.py IE=projekt/06_PT_instalacje_elektryczne/rysunki --md <md> --json <json>
```

## 1. Wynik — przed i po

| Wskaźnik | Przed (stan wyjściowy) | Po (auto + poprawki) | Zmiana |
|---|---|---|---|
| Arkuszy | 14 | 14 | — |
| Formaty | 14× A3×3 (891×420) | 4× 690×420, 2× 690×297, 2× 570×297, 1× 570×594, 1× A2, 1× 730×297, 1× 520×594, 1× 710×420, 1× 870×297 | — |
| Papier | 5,24 m² (≈ 84 A4) | **3,58 m²** (≈ 57 A4) | **−1,66 m² (−32 %)** |
| Wypełnienie ważone / średnie | 51 % / 51 % | **84 % / 84 %** | +33 pp |
| Najgorsze wypełnienie | 36 % (PT-IE-09) | 66 % (PT-IE-13) | +30 pp |
| Puste pole w ramkach | 2,37 m² | 0,51 m² | −1,86 m² |
| Warstwy A4 po złożeniu | 140 | 94 | −33 % |
| Składanie (dobre/poprawne/słabe) | 0/14/0 | 3/11/0 | +3 „dobre” |

Etapy (ten sam pomiar `tools/metryki_arkuszy.py`):

1. Sam silnik (`format: auto`, konfiguracja bez zmian): 3,69 m², wypełnienie 80 %, najgorsze 65 % (PT-IE-06),
   99 warstw, składanie 1/13/0.
2. Poprawki modułu widoku i konfiguracji (rozdz. 3): 3,58 m², 84 %, najgorsze 66 %, 94 warstwy, składanie 3/11/0.

Skale bez zmian: wszystkie rzuty 1:50 (RPB § 9 ust. 3; rejestr W-306 — PT 1:50), schemat RG bez skali. Pismo bez
zmian. Tabliczka w prawym dolnym rogu, margines 20 mm z lewej, znaki składania z numerami na marginesie. QA
generatora: 14/14 OK (jedyne ostrzeżenie na każdym arkuszu to puste pole projektanta w tabliczce, § 10 rozp.).

## 2. Arkusze — przed i po

| Nr | Przed: format, pole, W | Po: format, pole, W | Pasy × rzędy [mm] | Warstwy | Składanie |
|---|---|---|---|---|---|
| PT-IE-01 oświetlenie P0 | A3×3, 0,374 m², 57 % | 690×420, 0,290 m², 91 % | 140+120×3+190 × 297+123 | 10 | poprawne |
| PT-IE-02 oświetlenie P1 | A3×3, 0,374 m², 47 % | 690×297, 0,205 m², 88 % | 140+120×3+190 × 297 | 5 | poprawne |
| PT-IE-03 oświetlenie P2 | A3×3, 0,374 m², 38 % | 570×297, 0,169 m², 83 % | 200+180+190 × 297 | 3 | dobre |
| PT-IE-04 gniazda P0 | A3×3, 0,374 m², 66 % | 570×594, 0,339 m², 91 % | 200+180+190 × 297+297 | 6 | dobre |
| PT-IE-05 gniazda P1 | A3×3, 0,374 m², 48 % | A2 594×420, 0,249 m², 81 % | 210+192+192 × 297+123 | 6 | poprawne |
| PT-IE-06 gniazda P2 | A3×3, 0,374 m², 39 % | 730×297, 0,217 m², 95 % | 150+130×3+190 × 297 | 5 | poprawne |
| PT-IE-07 teletechnika P0 | A3×3, 0,374 m², 57 % | 520×594, 0,309 m², 74 % | 175+155+190 × 297+297 | 6 | poprawne |
| PT-IE-08 teletechnika P1 | A3×3, 0,374 m², 45 % | 690×297, 0,205 m², 85 % | 140+120×3+190 × 297 | 5 | poprawne |
| PT-IE-09 teletechnika P2 | A3×3, 0,374 m², 36 % | 570×297, 0,169 m², 80 % | 200+180+190 × 297 | 3 | dobre |
| PT-IE-10 PV dach | A3×3, 0,374 m², 59 % | 690×420, 0,290 m², 91 % | 140+120×3+190 × 297+123 | 10 | poprawne |
| PT-IE-11 PV parter | A3×3, 0,374 m², 57 % | 690×420, 0,290 m², 90 % | 140+120×3+190 × 297+123 | 10 | poprawne |
| PT-IE-12 uziom P0 | A3×3, 0,374 m², 57 % | 710×420, 0,298 m², 86 % | 145+125×3+190 × 297+123 | 10 | poprawne |
| PT-IE-13 odgromowa dach | A3×3, 0,374 m², 51 % | 690×420, 0,290 m², 66 % | 140+120×3+190 × 297+123 | 10 | poprawne |
| PT-IE-14 schemat RG | A3×3, 0,374 m², 53 % | 870×297, 0,258 m², 78 % | 210+140+140+190+190 × 297 | 5 | poprawne |

W = współczynnik wypełnienia „W obw.” z `tools/metryki_arkuszy.py`. Wszystkie arkusze mają H ≤ 594 mm, więc mieszczą
się na rolce 36″. PT-IE-13 (66 %) to rzut dachu z samym przewodem wyrównawczym konstrukcji PV, bo LPS nie jest
wymagany. Treść jest tam rzadka, a obwiednię rzutni wyznacza podkład dachu. Mniejszą skalę odrzucono, bo przyjęta
skala PT to 1:50.

## 3. Zmiany

### 3.1. Konfiguracja `model/arkusze_ie.yaml`

* `format: auto` (ekonomiczny) na wszystkich arkuszach. Formatów jawnych nie ma (uzasadnienie w 4.2).
* `osie_instalacji: zakres` w `wspolne` włącza osie tylko w zasięgu treści rzutu (rozdz. 3.2). Rzuty II piętra
  (03, 06, 09) nie mają już osi P i F garażu. Przedtem te osie dodawały do rzutni pusty pas ok. 100 mm. Efekt:
  PT-IE-03 i PT-IE-09 mają 570×297 zamiast 690×297 i składanie „dobre”, a PT-IE-06 ma 730×297 zamiast A2
  (0,217 zamiast 0,249 m²).
* `tytul_widoku` = `tytul` na arkuszach 01–13. Przedtem tytuł pod rzutem pochodził z generatora i różnił się od
  tabliczki i spisu, np. PT-IE-12 „UZIEMIENIA, POŁĄCZENIA WYRÓWNAWCZE, OCHRONA ODGROMOWA — RZUT PARTERU” przy
  tabliczce „UZIOM I POŁĄCZENIA WYRÓWNAWCZE — RZUT PARTERU”. Teraz tytuł widoku, tabliczka i spis w tomie są
  zgodne.
* `tytul_tomu: "PT — instalacje elektryczne (rysunki)"`. Dawny nagłówek spisu miał 234 mm pismem 5 mm i wychodził
  poza arkusz A4 (dostępne 172 mm). To obejście błędu S4 (rozdz. 6), do cofnięcia po poprawce `plot.volume`.

### 3.2. Moduł widoku `src/lamela/views/instalacje/` (drobne błędy, zmiany wstecznie zgodne)

* `podklad.osie(..., zakres=False)` i `baza.finish`: opcjonalne pomijanie osi, które nie przecinają narysowanej
  treści (± 0,35 m, tak jak w `plan._axes` na rzutach AR). Włącza się je opcją widoku `osie: zakres` albo
  `wspolne.osie_instalacji: zakres`. **Domyślnie bez zmian**, więc komplet IS nie jest dotknięty, dopóki go nie
  włączy (zalecane: rzuty II p. IS mają ten sam pusty pas).
* `wspolne.table_block` i nowe `_table_wrap`: gdy tekst komórki nie mieści się w kolumnie nawet pismem 1,8 mm,
  jest łamany na kilka wierszy i wiersz tabeli rośnie. Przedtem tekst wychodził poza komórkę i poza tabelę.
  Przykład: PT-IE-12, „(przy tworzywach zwykle niewymagane)” za prawą krawędzią tabeli, a „stolarka” na linii
  kolumn. Gdy wszystko się mieści, tabela jest rysowana jak dotąd (`draft.sheet.table`), więc arkusze IS bez
  przepełnień się nie zmieniają.
* `ie_rzut.tabela_obwodow`: zniesione obcinanie opisów do 52 znaków (odbiorniki) i 26 znaków (RCD) bez
  wielokropka. Ucinało ono treść, np. „własny RCD typ B 30 mA lub” bez dalszej części. Teraz tekst jest łamany.
  PT-IE-04: pełny opis obwodu G1 (lista pomieszczeń) i D11.
* `wspolne.Legenda.sym(..., wys=None)`: opcjonalna najmniejsza wysokość wiersza legendy dla wysokich symboli.
  W `ie_rzut` ustawiono ją dla PIR, CD i WD, bo na PT-IE-07 kółko „CD” nachodziło na opis „WD”. Domyślnie bez
  zmian.

## 4. Warianty sprawdzone i odrzucone

### 4.1. Łączenie rzutów I i II piętra jednej branży (arkusze 02+03, 05+06, 08+09)

Próba w katalogu roboczym dała formaty 1190×297, 1220×297 i 1050×297 (wypełnienie 97 / 80 / 85 %), łącznie
1,03 m² zamiast 1,21 m². To **−0,19 m² (−5 % kompletu) i 11 arkuszy zamiast 14**. Wariant odrzucono z
następujących powodów:

* zmieniłaby się numeracja PT-IE-03…14, do której odwołują się `PT_IE_opis.md`, `BRAKI_DANYCH.md`,
  `weryfikacja_PT_PRAWO.md`, a także struktura równoległa do kompletu IS (arkusz = kondygnacja);
* powstałyby pasy 1,05–1,22 m, składane w 6–7 pasów harmonijki i nieporęczne na budowie.

Wariant jest gotowy do decyzji Inwestora lub projektanta. Wystarczy w konfiguracji zastąpić parę arkuszy jednym
z `widoki: [{typ: inst_rzut, branza: …, kond: P1}, {… kond: P2}]`. Legenda i tabele łączą się same
(`legenda_arkusza`).

### 4.2. Jawna wysokość 420 mm dla PT-IE-04 (750×420) i PT-IE-07 (710×420)

Auto wybrało 570×594 i 520×594. Koszt wariantów 420 mm w silniku jest praktycznie równy (0,350 wobec 0,349 i
0,332 wobec 0,331). Przewagę daje tylko kara za niepełny górny rząd 123 mm. Wariant 420 mm zużywa 0,035 m² mniej
papieru (−1 %), ale ma 10 zamiast 6 warstw A4 i składanie „poprawne” zamiast „dobre” (PT-IE-04). Oba układy
obejrzano i oba są czytelne. **Zostaje wybór auto** (format jawny tylko wtedy, gdy auto daje gorszy wynik; tu go
nie daje).

## 5. Kontrola wizualna

Obejrzano każdy arkusz: całość w PNG i powiększone wycinki PIL (tabele obwodów, legendy, bloki uwag, okolice
znaków centrujących i zgięć, tabliczki). W rzutni nie ma nakładania bloków na treść. `sprawdz_nakladanie` nie
zgłasza kolizji. Numeracja „ARKUSZ n/14” i nr rysunku w tabliczkach są zgodne ze spisem w `tom_PT-IE.pdf`
(15 stron: spis A4 i 14 arkuszy z formatami jak w tabeli 2).

Większe wolne pola, które zostały:

* PT-IE-07: pas nad rzutem, ok. 125×120 mm z lewej u góry. Przy H = 594 treść nie wypełnia wysokości, a wariant
  710×420 opisano w 4.2.
* PT-IE-09: ok. 180×45 mm między uwagami a podziałką w kolumnie nad tabliczką.
* PT-IE-13: rzadka treść wewnątrz obwiedni rzutu dachu.

Są to pola wynikające z dyskretnych wysokości arkusza, a nie z błędów układu.

## 6. Błędy silnika (nie poprawiane; do zespołu `uklad.py` / `draft`)

* **S1. Bloki kolumny opisowej nachodzą na znaki centrujące.**
  * Arkusze: PT-IE-02, 03, 06, 08, 09 — litera „N” róży kierunków na prawym znaku centrującym (y = H/2 = 148,5 mm);
    PT-IE-10 — tytuł „WYNIKI OBLICZEŃ — PV …” przecięty górnym znakiem; PT-IE-11 — tytuł „OBJAŚNIENIA I UWAGI
    (cd.)” (górny znak) i ostatni wiersz uwag (dolny znak); PT-IE-12 — pkt 4 uwag przecięty dolnym znakiem.
  * Objaw: linia 0,7 mm przez tekst.
  * Przyczyna: `Sheet._draw_frame` rysuje znaki centrujące na osiach arkusza 10 mm w głąb pola rysunku (od krawędzi
    do ramka ± 10 mm). `uklad.py` ma tylko `PAD_B = 3 mm` od ramki i nie traktuje tych 4 odcinków jako przeszkód.
    Na arkuszach H = 297 róża (wiersz 180×30 nad tabliczką) wypada dokładnie na prawym znaku.
  * Poprawka: 4 prostokąty zajętości (np. 3×12 mm) w MaxRects/`sprawdz_nakladanie`.
* **S2. Kolejność części uwag „(cd.)”.** PT-IE-10 i PT-IE-11: część 1 (pkt 1–4/5) stoi na dole w środku arkusza,
  a „OBJAŚNIENIA I UWAGI (cd.)” (pkt 5/6–8) u góry, nad częścią 1 i daleko od niej. Czytelnik trafia najpierw na
  kontynuację. Przyczyna: części są rozmieszczane niezależnie przez MaxRects bez warunku kolejności czytania.
  Proponowany warunek: część k+1 na prawo od części k albo pod nią.
* **S3. Znak centrujący przecina nagłówek spisu w tomie** (`draft.plot.volume`, strona 1 `tom_PT-IE.pdf`): nagłówek
  pismem 5 mm na y1 − 14 mm sięga górnego znaku (10 mm w głąb od ramki).
* **S4. `plot.volume` nie dopasowuje tekstów spisu.** Nagłówek (`tytul_tomu.upper()`, 5 mm) nie jest łamany ani
  zmniejszany. Dawny tytuł IE (234 mm) wychodził poza A4 i obejściem jest skrócenie w konfiguracji (3.1). Tytuły
  arkuszy w kolumnie „Tytuł rysunku” przy 1,8 mm nadal wchodzą na kolumnę „Skala”: PT-IE-11 „… (FALOWNIK, SPD)”,
  PT-IE-13 „… — RZUT DACHU”. Potrzebne łamanie wiersza (jak `_table_wrap` w 3.2). Komplet IS ma analogiczny
  długi `tytul_tomu`.

## 7. Do zrobienia poza tym kompletem

* `projekt/09_opis_i_zalaczniki/PT_IE/PT_IE_opis.md`: wykaz rysunków ma kolumnę „Format” = A3×3. Trzeba ponownie
  wygenerować opis (`tools/dokumenty/pt_ie_*`). Formaty czyta z `raport_widokow.json`, więc wystarczy uruchomić
  generator tomu IE.
* Komplet IS: zalecane `osie_instalacji: zakres` (3.2) i sprawdzenie skutków zmiany `_table_wrap` na arkuszach z
  przepełnionymi tabelami. Zmiana dotyczy tylko tabel, w których tekst wychodził poza komórkę.
* Decyzja Inwestora w sprawie wariantu 4.1 (−0,19 m², 11 arkuszy, nowa numeracja).
