# `lamela.dokumenty` — część opisowa i tomy projektu budowlanego

Składa **element projektu** (PZT, PAB, PT, ZL, dokumenty wniosku) z sekcji Markdown/HTML, tabel, wykresów, bloków
formalnych i arkuszy rysunkowych do PDF, a elementy — w **tom** (jeden plik PDF) z zakładkami, metadanymi, kontrolą
rozmiaru i nazwą wg zał. 1 RPB. Walidator sprawdza kompletność gotowego pliku wg sekcji C rejestru wymagań.

Podstawy: rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego (RPB, t.j. Dz.U. 2022 poz. 1679
ze zm.) — § 2b (PDF, wektor, ≤ 150 MB, nazwy plików), § 5 (oprawa, tomy, PT osobno), § 6 (numeracja), § 7 (strona
tytułowa, spis treści, łączny spis), § 10 (metryka); PB art. 33 ust. 2 pkt 10, art. 34 ust. 3d–3e, art. 41 ust. 4a,
art. 102a; rozp. BIOZ (Dz.U. 2003 nr 120 poz. 1126) § 2, § 6. Konwencja znaczników — rejestr, sekcja E.1.

```
PYTHONPATH=src python3 tools/dokumenty_demo.py            # demo → projekt/00_demo_silnika/dokumenty_demo/
PYTHONPATH=src python3 -c "from lamela.dokumenty import sprawdz_tom; print(sprawdz_tom('plik.pdf').tekst())"
```
Wymagania: Playwright + Chromium (`/opt/pw-browsers/chromium` lub zmienna `LAMELA_CHROMIUM`), PyMuPDF, Jinja2,
Markdown, PyYAML; opcjonalnie pandas (tabele z DataFrame), matplotlib (wykresy). Czcionki lokalne: Liberation Sans
(metrycznie zgodna z Arial, jak w tabliczkach `lamela.draft`), zapasowo DejaVu Sans — bez dostępu do internetu.

## 1. Moduły

| moduł | zawartość |
|---|---|
| `dane.py` | `dane_obiektu()`, `Projektant`, `SPECJALNOSCI` (AR, BO, IS, IE, BT), `ELEMENTY` |
| `dokument.py` | `Dokument` (bloki, render HTML → PDF dwuprzebiegowy), `WynikDokumentu`, `stempluj_arkusz` |
| `bloki.py` | treść oświadczeń, karty podpisów, informacja BIOZ (domyślna treść dla LAMELI) |
| `tom.py` | `Tom`, `WynikTomu`, `PrzekroczonyRozmiar` |
| `arkusze.py` | `Arkusz` (odczyt tabliczki z PDF), `arkusze_z_katalogu`, `plan_skladania` |
| `walidator.py` + `listy_kontrolne.yaml` | `sprawdz_tom`, `LISTY_KONTROLNE` (TOM_I, PT_AR, PT_BO, PT_IS, PT_IE, PT_WB) |
| `nazwy.py` | `nazwa_pliku`, `sprawdz_nazwe` (zał. 1 RPB) |
| `znaczniki.py` | `do_uzup()`, `dok_zewn()`, `DANE_PRZYKLADOWE`, `STATUS_PRZYKLAD`, `policz_znaczniki` |
| `formaty.py` | `liczba()` (1 234,56), `rzedna()` (±0,000), daty, `wykryj_format()` (A0…A4, Ak×n) |
| `render.py` | Chromium (jedna instancja na proces), odnośniki → GoTo |
| `szablony/styl.css.j2`, `szablony/bloki.html.j2` | arkusz stylów (A4, margines na oprawę 25 mm) i makra bloków |

## 2. Dane obiektu — `dane_obiektu(katalog_modelu=None, **nadpisania) -> dict`

Czyta `model/budynek.yaml` (`meta`, opcjonalna sekcja `projekt:` z `inwestor`, `pracownia`, `projektanci`,
`nazwa_zamierzenia`) i `model/dzialka.yaml` (`dzialka:` `nr`, `obreb`, `pow`, opcjonalnie `adres`, `gmina`, `powiat`,
`wojewodztwo`, `jedn_ewid`, `identyfikator`, `status`). Bez plików — wartości z briefu (działka 123/4, obręb 0005
„Przykładowo”) oznaczone `[DANE PRZYKŁADOWE – FIKCYJNE]`. Klucze: `nazwa_krotka`, `obiekt`, `nazwa_zamierzenia`,
`adres`, `dzialka{nr, obreb, obreb_nr, obreb_nazwa, jedn_ewid, gmina, powiat, wojewodztwo, identyfikator, pow_m2}`,
`lokalizacja`, `kategoria` ('I' z `wymagania.yaml`), `inwestor{nazwa, adres}`, `projektanci` (4 × `Projektant`:
architektoniczna / konstrukcyjno-budowlana / instalacyjna sanitarna / instalacyjna elektryczna — bez ograniczeń),
`sprawdzajacy` („nie dotyczy (art. 20 ust. 3 pkt 2 PB)”), `pracownia`, `data`, `przyklad`, `zrodla`, `status`
(pochodzenie każdego pola: `model` / `brief` / `do_uzupelnienia`). Dane osobowe są zawsze polami
`[DO UZUPEŁNIENIA: …]` — system nie fabrykuje nazwisk, numerów uprawnień ani podpisów.

`Projektant(branza, funkcja, imie_nazwisko, nr_uprawnien, specjalnosc, zakres, elementy, adres, izba)`;
`elementy` — kody elementów, których jest autorem (`PZT`, `PAB`, `PT-AR`, `ZL`, `BIOZ`…).

## 3. `Dokument(tytul, czesc, dane=None, **opcje)`

Opcje: `kod` (ramka na stronie tytułowej, np. „PT-1 AR”), `podtytul`, `branza`, `data`, `rewizja`, `projektanci`
(domyślnie autorzy elementu z `dane`), `przyklad`, `tom=(nr, liczba)` (RPB § 7 ust. 6), `stadium`, `znak_wodny`,
`spis_poziom` (2), `strona_tytulowa`, `spis_tresci`, `tytul_spisu` („Spis załączników” dla ZL), `miejscowosc`,
`grupa_poczatkowa`.

Treść (metody zwracają `self`, więc można łączyć):

| metoda | działanie |
|---|---|
| `czesc_opisowa(tytul, podstawa=)` | nagłówek części na nowej stronie; grupa spisu „Część opisowa (§ 7 ust. 5 pkt 1)” |
| `rozdzial(tytul, tresc_md=None, poziom=1, podstawa=, nowa_strona=)` | nagłówek numerowany 1. / 1.1. / 1.1.1.; `podstawa` (np. „§ 14 pkt 1 RPB”) wyświetlana przy nagłówku |
| `markdown(tekst)` | Markdown (extra: tabele, listy, przypisy); `#`/`##` = rozdział/podrozdział; `## Tytuł {podstawa: …}` |
| `html()`, `akapit()`, `lista()`, `wniosek(md, alarm=)`, `nowa_strona()` | wstawki |
| `tabela(dane, kolumny=, tytul=, jednostki=, formaty=, wyrownanie=, szerokosci=, suma=, uwagi=, zrodlo=, lp=)` | DataFrame / lista słowników / lista list; „Nazwa [m²]” → jednostka w nagłówku; liczby 1 234,56; wiersz-napis = wiersz grupy; `_klasa: suma/pod/grupa`; numeracja „Tabela N.”; `<thead>` powtarzany na kolejnych stronach |
| `tabela_przegrody(nazwa, warstwy, Rsi=, Rse=, U_max=, podstawa_Umax=, od_zewnatrz=)` | warstwy z d, λ, R; R_T i U wg PN-EN ISO 6946 (bez ΔU — [ZAŁ]); wynik spełnia/nie spełnia |
| `tabela_wynikow(wiersze)` | parametr, wartość, wymaganie, podstawa, ✓/✗ |
| `obraz(plik|bajty, podpis=, szerokosc=)`, `wykres(fig_matplotlib, …)` | ilustracje numerowane; wykres jako SVG (wektor) |
| `oswiadczenie_projektanta(techniczny=None, art102a=True, pnb=)` | art. 34 ust. 3d pkt 3 PB + tabela współautorów (ust. 3e) z kolumną podpisu; sprawdzający n/d; e-CRUB (ust. 3da); dla PT brzmienie art. 41 ust. 4a pkt 2 |
| `oswiadczenie_sieci_cieplowniczej(wariant=, zalacznik=)` | art. 33 ust. 2 pkt 10 PB, art. 7b Pr. energ.; warianty `brak_sieci` / `zrodlo_indywidualne` / `przylaczenie`; klauzula karna |
| `oswiadczenie_inwestora_102a(organ=, zakres=)` | **WZÓR** (brak urzędowego wzoru, D-02) wg art. 102a ust. 1, 2, 4 PB |
| `informacja_pb5(tytul_prawny=)` | strona informacyjna: oświadczenie o prawie do dysponowania — tylko na urzędowym PB-5 (Dz.U. 2021 poz. 1170) |
| `blok_podpisow(osoby=None)` | karty podpisów z pustymi polami |
| `informacja_bioz(tresc={1..6}, zagrozenia=)` | strona tytułowa § 2 ust. 2 + pkt 1–6 § 2 ust. 3 + tabela robót z § 6 i wniosek o planie BIOZ (art. 21a PB) |
| `zalacznik(tytul)` | „Załącznik nr N.” (ZL; numeracja rozdziałów od 1 w załączniku) |
| `dokument_zewnetrzny(nazwa, organ=, podstawa=)` | strona zastępcza `[DOKUMENT ZEWNĘTRZNY – do dołączenia: …]` |
| `czesc_rysunkowa(arkusze)` | karta części rysunkowej (metryka) + **wykaz rysunków generowany z listy arkuszy**; arkusze dołączane za częścią opisową |

`render_pdf(sciezka=None, dolacz_arkusze=True, stempel_arkuszy=None) -> WynikDokumentu` — render HTML w Chromium
(nagłówek z nazwą obiektu i elementu, stopka ze statusem i „KOD · strona X z Y” w polach marginesowych CSS; strona
tytułowa bez nagłówka i stopki), drugi przebieg z numerami stron w spisie treści (odczytanymi z odnośników
wewnętrznych pierwszego przebiegu), dołączenie arkuszy PDF bez zmiany formatu, zakładki, etykiety stron
(`PZT s. 3`, `PZT-01`), metadane. `render_html()` — sam HTML (podgląd w przeglądarce).

Numeracja: „strona X z Y” obejmuje strony A4 elementu (od strony tytułowej = 1, bez numeru na niej); rysunki
identyfikuje numer rysunku (§ 6 ust. 3). Więcej niż 4 autorów → lista autorów w załączniku do strony tytułowej (§ 7 ust. 4).

## 4. `Arkusz`

`Arkusz.z_pdf(plik, **nadpisz)` — nr, tytuł, skala, data i rewizja z tabliczki (`lamela.draft`: etykiety „NR RYSUNKU”,
„TYTUŁ RYSUNKU”, „SKALA”…), w razie braku — z metadanych i nazwy pliku (`PZT-01_…_1-500.pdf`); format z wymiarów
strony (A0…A4, A3×3…). `Arkusz.planowany(nr, tytul, skala, format)` — rysunek bez pliku: w wykazie ze znacznikiem
`[DO UZUPEŁNIENIA]`, w PDF strona zastępcza w formacie arkusza, w walidatorze status „DO UZUPEŁNIENIA”.
`arkusze_z_katalogu(katalog)` — wszystkie PDF katalogu (bez plików „tom”).

W wersji przykładowej każdy arkusz dostaje znak „PRZYKŁAD – NIE DO ZŁOŻENIA · [DANE PRZYKŁADOWE – FIKCYJNE]” —
pionowo w lewym marginesie na oprawę (0–8 mm od krawędzi), poza ramką, siatką odniesień i odcinkiem kontrolnym.

## 5. `Tom(nazwa, elementy | pliki=, **opcje)` → `zloz(katalog) -> WynikTomu`

Elementy: `Dokument`, ścieżka PDF (opis z innego programu — zakładka z metadanych), `Arkusz` lub ścieżka arkusza
(zagnieżdżane w zakładce poprzedniego elementu), `(tytuł, ścieżka)`. Opcje: `rodzaj` (domyślnie z kodów:
`PZT_PAB_ZL`, `PZT_PAB`, `PT`…), `data`, `nr` i `symbol` (PT: `PT_x_y_z`), `tom=(nr, liczba)`,
`strona_tytulowa` i `laczny_spis` (§ 7 ust. 7 pkt 1; bez PT), `limit_mb=150`.

* Nazwa pliku wg zał. 1 RPB: `PZT_PAB_ZL_2026.09.25.pdf`, `PT_1_AR_…`, `PT_2_BO_…`, `PT_3_IS_…`, `PT_4_WB_…` (tom 4 obejmuje instalacje elektryczne i telekomunikacyjne — dwie specjalności, symbol WB; sam IE → `PT_x_IE_…`). Rozmiar w MB = 10⁶ B.
* PT w jednym pliku z innym elementem (lub dwa tomy PT w jednym pliku) → `ValueError` (§ 5 ust. 3).
* Rozmiar > 150 MB → `PrzekroczonyRozmiar` (podzielić: `PZT_PAB_z` + `ZL_z`, `PAB_x_z`; rastry tylko mapy).
* Zakładki: strona tytułowa tomu, łączny spis, każdy element → strona tytułowa, spis, oświadczenia, rozdziały,
  karta części rysunkowej → każdy rysunek „NR — tytuł (skala)”. Pozycje spisów są odnośnikami.
* Metadane: Title „Dom LAMELA — TOM I: PZT + PAB + ZL (PRZYKŁAD – NIE DO ZŁOŻENIA)”, Author — nazwiska autorów albo
  `[DO UZUPEŁNIENIA: autorzy projektu]`, Subject (element, obiekt, działka, kategoria), Keywords, tryb otwarcia
  z panelem zakładek.

## 6. Walidator — `sprawdz_tom(tom, lista_kontrolna=None) -> RaportKompletnosci`

Czyta gotowy PDF (także spoza systemu). `lista_kontrolna`: klucz (`TOM_I`, `PT_AR`, `PT_BO`, `PT_IS`, `PT_IE`, `PT_WB`)
lub słownik; `None` — dobór po nazwie pliku. Pozycje (`listy_kontrolne.yaml`) odwzorowują sekcję C rejestru:
plik (nazwa, ≤ 150 MB, wektor, metadane, oprawa PT), strona tytułowa (§ 7 ust. 2 pkt 1–3), spis, numeracja,
oświadczenie, punkty opisu (§ 14 pkt 1–8 PZT, § 20 ust. 1 pkt 1–14 PAB, § 23 PT), rysunki (w tym minimalna liczba
rzutów/przekrojów/elewacji i skale ≤ 1:100 / 1:500), metryki arkuszy (`spec: tabliczki` — wiersz „Projektant” niepusty, „Sprawdzający” z osobą albo „nie dotyczy (art. 20 ust. 3 pkt 2 PB)”; W-305, W-320), § 23 pkt 12 w każdym tomie PT, ZL (informacja BIOZ pkt 1–6, zjazd, oświadczenie IS).
Stan modelu (`spec: stan_modelu`, F-06 w PT_WSPOLNE): tom zawiera znacznik „stan modelu: SHA-256 xxxxxxxxxxxx (…)” z `stan_modelu()` (skrót plików danych `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`, `wyposazenie.yaml`); znacznik ≠ bieżący model → BRAK (tom nieaktualny, weryfikacja PT K-1), brak znacznika → OSTRZEŻENIE. Ten sam znacznik we wszystkich tomach PT i w tomie I wykazuje, że powstały z jednego stanu modelu.
Wyszukuje po zakładkach, tekście strony tytułowej, tekście opisu i tytułach rysunków (wyrażenia regularne).

Klucze pozycji poza `szukaj`: `uzupelnic_gdy` (+ `uzupelnic_opis`) — znaleziona treść zawiera znacznik zastępczy
(np. `[DOKUMENT ZEWNĘTRZNY – do dołączenia: dokumentacja badań podłoża…]`) → DO UZUPEŁNIENIA; `brak_gdy`
(+ `brak_opis`) — pozycja „negatywna”: BRAK, gdy tekst elementu zawiera wskazane znaczniki (wzorce `(?-i:…)` są
wrażliwe na wielkość liter), np. C2-BO-06: „NIESPEŁNIONY”, „WYMAGA ANALIZY”, „NIEZAMKNIĘTE” w tomie PT-2 BO.

Statusy pozycji: OK · BRAK · DO UZUPEŁNIENIA (jest, ale z polem `[DO UZUPEŁNIENIA]` / tylko arkusz zastępczy) · N/D
· OSTRZEŻENIE. Status tomu: NIEKOMPLETNY → PRZYKŁAD – NIE DO ZŁOŻENIA (są znaczniki `[DO UZUPEŁNIENIA]` lub
`[DOKUMENT ZEWNĘTRZNY]`, reguła AUD-RYS z E.1) → KOMPLETNY FORMALNIE. `raport.tekst()`, `raport.json()`,
`raport.braki`, lista wszystkich pól do uzupełnienia z liczbą wystąpień.

## 7. Wersja papierowa — składanie arkuszy do A4

Plik elektroniczny zachowuje oryginalne formaty arkuszy (RPB § 2b; wektor), także formaty niestandardowe
„na miarę” treści (np. 630×594, 760×297 — dobór: `lamela.views.uklad`). Dla postaci papierowej (RPB § 2a — oprawa
do formatu A4; 3 egzemplarze do wniosku, PB art. 33 ust. 2 pkt 1) arkusze składa się „do wpięcia” wg praktyki
DIN 824:1981-03 forma A, uogólnionej na formaty wydłużone i niestandardowe [przyjęcie; PN-N-01603:1986 — wycofana
bez następcy, przywołanie informacyjne], zgodnie ze znakami składania na arkuszach `lamela.draft`
(geometria: `lamela.draft.skladanie`):

1. najpierw zgięcia **pionowe** w harmonijkę o **nieparzystej** liczbie pasów: pierwszy pas od lewej (z marginesem
   20 mm na oprawę) leży na spodzie licem do góry z marginesem przy lewej krawędzi paczki, pas z tabliczką przy
   prawej krawędzi (≥ 190 mm) — na wierzchu; pozostałe pasy ≤ 210 mm, tak by prawa krawędź arkusza wróciła do
   rogu paczki A4. Dwie rodziny (wybierany wariant z najlepszą oceną; przy remisie pierwszy pas 210 mm):
   * **A** (praktyka DIN): 210 + pary równe — wszystkie 190–210 mm, inaczej para z tabliczką 190 mm i pozostałe
     pary równe (A2: 210 + 192 + 192; A3×3: 210 + 150,5 + 150,5 + 190 + 190; A1: 210 + 125,5 + 125,5 + 190 + 190);
   * **B**: (20 + m) + m × (2k − 1) + 190, m = (W − 210)/(2k) ≤ 190 — pasy 2…N w [20, 20 + m] paczki, margin
     wolny; A3: 125 + 105 + 190; 690: 140 + 120 + 120 + 120 + 190 (w rodzinie A byłoby 210 + 50 + 50 + 190 + 190);
   * „ładnie” (pasy pośrednie 180–210 mm, równe) składają się długości ≈ 570–630, 930–1050, 1300–1470 mm …;
     L = 210 + 190·n daje same pasy 190 mm tylko dla parzystego n (590, 970, 1350 mm);
2. potem zgięcia **poziome** co 297 mm od dołu (wysokości „ładne”: 297, 594, 891 mm; 420 mm → górny rząd 123 mm);
3. tabliczka rysunkowa pozostaje na wierzchu w prawym dolnym rogu, lewy margines 20 mm do dziurkowania/oprawy;
   na marginesie arkusza znaki zgięć z numerami kolejności (pionowe od pasa z tabliczką, potem poziome).

`plan_skladania(arkusze)` zwraca dla każdego arkusza format, wymiary, położenie zgięć, pasy, rzędy, liczbę warstw,
ocenę („dobre” / „poprawne” / „słabe” — progi jak `tools/metryki_arkuszy.py`) i warunek „tabliczka na wierzchu”
(demo: `plan_skladania.json`). Generator widoków zapisuje ten sam plan w `raport_widokow.json` (pole `skladanie`).
Część opisowa jest drukowana dwustronnie lub jednostronnie na A4 z marginesem na oprawę 25 mm (lewy).

## 8. Ograniczenia

* Chromium nie ma dzielenia wyrazów dla języka polskiego — akapity wyjustowane mogą mieć szersze odstępy.
* Tabele nie dzielą wierszy między stronami (`break-inside: avoid`); bardzo długi pojedynczy wiersz przechodzi w całości.
* Strona tytułowa ma stałą wysokość (A4); zbyt długie dane (> 4 autorów) — autorzy w załączniku; bardzo długa nazwa
  zamierzenia może wymagać skrócenia.
* Zakładki PDF obejmują poziomy spisu treści (domyślnie 2); głębsze nagłówki są tylko w tekście.
* Walidator ocenia **obecność** treści (wyrażenia regularne), nie jej poprawność merytoryczną; nie sprawdza metryk
  rysunków (to AUD-RYS / `lamela.draft.plot.qa`).
* Oświadczenie z art. 102a to WZÓR opracowany z treści ustawy (brak urzędowego wzoru; wzór PIIB — źródło wtórne);
  formularz PB-5 nie jest generowany (tylko informacja i dane do przepisania).
* Podpisy elektroniczne (kwalifikowany/osobisty/zaufany) składa się na gotowym pliku poza systemem; każda zmiana pliku
  po podpisaniu unieważnia podpis — podpisywać wersję ostateczną.
* Brak PDF/A; limity e-Budownictwa (D-26) mogą być ostrzejsze niż 150 MB.
