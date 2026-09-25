# Weryfikacja niezależna tomów PT — zgodność z przepisami i kompletność (PRAWO)

Data: 2026-09-25 · weryfikator niezależny (bez poprawiania plików) · status tomów: PRZYKŁAD – NIE DO ZŁOŻENIA

## 1. Zakres i metoda

Sprawdzone pliki: `projekt/wydanie/PT_1_AR_2026.09.25.pdf` (49 s.), `PT_2_BO_…` (333 s.), `PT_3_IS_…` (85 s.),
`PT_4_IE_…` (48 s.), źródła MD i raporty walidacji w `projekt/09_opis_i_zalaczniki/PT_*/`, generatory
`tools/dokumenty/tom_PT_*.py`.

Teksty przepisów sprawdzono w źródłach pierwotnych (ELI / pliki Dz.U.):
- PB t.j. Dz.U. 2026 poz. 524 — art. 20 ust. 3, art. 33 ust. 2 pkt 10, art. 34 ust. 3, 3c, 3d, 3e, art. 41 ust. 4a pkt 2, art. 15a ust. 18 i 22;
- RPB t.j. Dz.U. 2022 poz. 1679 — § 2b, § 5, § 6, § 7, § 9, § 10, § 23, § 24, zał. 1; zmiany: Dz.U. 2023 poz. 2405 (§ 23 pkt 4a), Dz.U. 2026 poz. 597 (§ 23 pkt 12);
- rozp. Dz.U. 2012 poz. 463 — § 4, § 7, § 9, § 10; WT t.j. Dz.U. 2022 poz. 1225 — § 267;
- statusy norm — rejestr `docs/10_podstawy_prawne/00_rejestr_wymagan.md`, tab. A.3.

Strony PDF obejrzano po renderowaniu (strony tytułowe, oświadczenia, spisy treści, rozdziały ppoż., tabele obliczeń,
tabliczki rysunków, arkusze PT-AR-01, PT-AR-D-05, PT-BO-03, PT-BO-13, PT-IS-01, PT-IE-14).

## 2. Co jest zgodne (potwierdzone)

- Nazwy plików są zgodne z zał. 1 RPB (`PT_x_y_rrrr.mm.dd`). Każdy tom jest osobnym plikiem (RPB § 5 ust. 2a i 3).
- Pliki mają od 2,9 do 11,1 MB, czyli mniej niż 150 MB (§ 2b ust. 3). Wszystkie czcionki są osadzone.
- Część rysunkowa jest wektorowa (§ 2b ust. 2): na arkuszach nie ma rastrów. Rastry występują tylko w części opisowej:
  wykresy MES w PT-2 BO i jeden wykres w PT-3 IS. Przepis tego nie zabrania.
- Brzmienie oświadczenia projektanta we wszystkich 4 tomach jest dosłownie zgodne z art. 41 ust. 4a pkt 2 PB:
  „…zgodnie z obowiązującymi przepisami, zasadami wiedzy technicznej, projektem zagospodarowania działki lub terenu
  oraz projektem architektoniczno-budowlanym oraz rozstrzygnięciami dotyczącymi zamierzenia budowlanego”.
  Oświadczenia zawierają też art. 34 ust. 3e pkt 1–2, ust. 3d pkt 1–2 i ust. 3da. Powołanie art. 20 ust. 3 pkt 2 PB jest poprawne.
- Strony tytułowe zawierają elementy z § 7 ust. 2 pkt 1–3 i ust. 6 („Tom n z 4”). Dane osobowe, dane inwestora
  i TERYT są oznaczone [DO UZUPEŁNIENIA], a działka i adres — jako fikcyjne. Nie znaleziono wymyślonych nazwisk,
  numerów uprawnień ani nazw handlowych wyrobów. Wyroby są opisane jako „przykładowe — lub równoważne”.
- § 23 pkt 10 (ppoż.) — każdy tom ma osobny rozdział (AR rozdz. 9, BO rozdz. 8, IS rozdz. 7, IE rozdz. 12).
- § 23 pkt 4a — status „nie dotyczy” w PT-1 AR ma poprawną podstawę. Pkt 4a dotyczy tylko budynku jednorodzinnego
  z dwoma lokalami, zabudowy szeregowej lub bliźniaczej i budynków wielorodzinnych.

## 3. Problemy

### KRYTYCZNE

**K-1. Każdy tom powstał z innego, nieaktualnego stanu modelu (wszystkie tomy).**
Plik `model/budynek.yaml` (oraz `dzialka.yaml`, `instalacje.yaml`, `wyposazenie.yaml`) zmieniono o 07:35. Wszystkie
PDF powstały wcześniej: AR o 06:52, IS o 07:17, BO o 07:27, IE o 07:31, tom I o 07:18. Tomy same podają różne stany
modelu: IS „stan z 06:48”, BO „07:16”, IE „07:28”. BO sam oznacza swoje dane wejściowe jako „NIEZAMKNIĘTE (nieaktualne)”:
`wyniki.json` z 06:33 oraz MES i kontrolę zbrojenia z 06:48 (tab. 4, s. 8).
Skutek: nie ma dowodu, że PT jest zgodny z PZT i PAB (art. 34 ust. 3c PB) ani że tomy są zgodne między sobą.
Oświadczenia z art. 34 ust. 3d pkt 3 nie można w takim stanie podpisać.
Poprawka: zamrozić model. Potem w jednym przebiegu uruchomić obliczenia (konstrukcja, mostki, sanitarne, elektryka),
widoki i arkusze, a na końcu 4 generatory PT i tom I. Do `sprawdz_tom` dodać kontrolę wspólnego skrótu
(hash) lub znacznika czasu modelu we wszystkich tomach.

**K-2. PT-2 BO zawiera niespełnione warunki i niezamknięte analizy, a mimo to ma oświadczenie projektanta.**
Strona tytułowa podaje „ANALIZY NIEZAMKNIĘTE: 31 pozycji”. Tab. 9 (s. 303) wykazuje docisk lokalny do podłoża
p_d = 364,0 kPa > q_Rd = 318,8 kPa (η = 114 %, „NIESPEŁNIONY”). Kontrola zbrojenia (rozdz. 6) daje 273/275
pozycji — 2 niespełnione. Przy przebiciu stropu ST1 (SL1–SL3) jest adnotacja [WYMAGA ANALIZY]. Uwaga 11 na PT-BO-13
mówi o niespełnionym warunku PL-2.
Mimo to walidator daje C2-BO-01 „OK”.
Poprawka: zamknąć analizy przed wydaniem. W `listy_kontrolne.yaml` (PT_BO) dodać pozycję BRAK, która uruchamia się
na tekst „NIESPEŁNIONY”, „WYMAGA ANALIZY” lub „NIEZAMKNIĘTE” w tomie.

**K-3. Rysunki PT-3 IS i PT-4 IE są niezgodne z częścią opisową i obliczeniami tego samego tomu.**
- IE, rozdz. 15.1: w PT-IE-04 jest pompa ciepła PC-R290-12, a w obliczeniach PC-R290-07. W PT-IE-06 i PT-IE-14
  centrala ma 437 m³/h, a w obliczeniach 365 m³/h. Na schemacie RG (PT-IE-14) 25 obwodów ma inne fazy lub przewody
  niż w obliczeniach; obwód D6 jest na rysunku 3-fazowy, a w obliczeniach 1-fazowy.
- IE, tab. 2: WLZ (ΔU 0,61 % > 0,50 %) i strona DC PV (1,04 % > 1,00 %) nie spełniają warunków. „Rozwiązanie”
  podano tylko w tekście — „do tego czasu obowiązuje przekrój z kolumny Rozwiązanie” — a rysunki go nie zawierają.
- IS, rozdz. 1: PT-IS-09 i PT-IS-17 pokazują PC-R290-12, obliczenia PC-R290-07. Arkusze PT-IS-07…11 mają adnotację
  „SPRAWDZENIE NIESPEŁNIONE” z poprzedniej wersji obliczeń.
Zasada „wiążące są wartości z obliczeń” nie usuwa sprzeczności wewnątrz tomu PT (RPB § 23 pkt 8, § 24 pkt 4).
Poprawka: wpisać rozwiązania do parametrów obliczeń, przeliczyć, wygenerować arkusze IS i IE ponownie, a potem złożyć tomy.
Walidator powinien dawać BRAK, gdy lista „arkusze nieaktualne” nie jest pusta.
