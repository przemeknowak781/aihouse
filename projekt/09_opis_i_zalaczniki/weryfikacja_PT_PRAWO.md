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

### ISTOTNE

**I-1. PT-2 BO podaje błędną podstawę PT: „art. 34 ust. 3 pkt 4 (projekt techniczny)”.**
Miejsce: s. 7, rozdz. 2.1; źródło w `tools/dokumenty/tom_PT_BO.py`, linia 403. W t.j. Dz.U. 2026 poz. 524 art. 34
ust. 3 pkt 4 dotyczy oświadczenia zarządcy drogi. Projekt techniczny opisuje pkt 3 lit. a–e; dla BO właściwe są
lit. a i d. PT-1 AR ma już poprawne brzmienie (pkt 3 lit. c).
Uwaga: ten sam błąd jest w treści zlecenia.

**I-2. W tomach brakuje RPB § 23 pkt 12 albo podano złe uzasadnienie.**
Pkt 12 („dane dotyczące warunków ochrony ludności…”) dodał Dz.U. 2026 poz. 597 § 1 pkt 6. Nie jest wyjątkiem
z § 3, więc obowiązuje od 19.05.2026.
- PT-1 AR i PT-2 BO nie wspominają pkt 12.
- PT-3 IS i PT-4 IE piszą „§ 23 pkt … 12 — nie dotyczy (budynek mieszkalny, nie liniowy)”. To uzasadnienie
  pkt 6 — nie pasuje do pkt 12.
- Rejestr C.2 również wymienia pkt 12 jako n/d bez podstawy. `listy_kontrolne.yaml` (PT_WSPOLNE) w ogóle go nie sprawdza.
Poprawka: w każdym tomie dodać wpis: „§ 23 pkt 12 — nie dotyczy: PZT i PAB nie przewidują budowli ochronnej ani
miejsca doraźnego schronienia (PAB § 20 ust. 1 pkt 14 — n/d)”. Do PT_WSPOLNE dodać regex `§ 23 pkt 12`.

**I-3. PT-4 IE zawiera instalacje telekomunikacyjne, a jedynym autorem jest projektant ze specjalnością elektryczną.**
Tom obejmuje przyłącze światłowodowe, okablowanie strukturalne, RTV/SAT i SSWiN (rozdz. 7, arkusze PT-IE-07…09).
Autor na stronie tytułowej i w oświadczeniu ma specjalność „instalacyjna (elektryczne i elektroenergetyczne)”.
Zakres telekomunikacji przewodowej należy do specjalności telekomunikacyjnej (PB art. 15a ust. 18); zakres
z ust. 22 jej nie obejmuje.
Skutki:
- strona tytułowa i oświadczenie muszą wskazać współautora z tymi uprawnieniami (§ 7 ust. 2 pkt 3, art. 34 ust. 3e);
- symbol pliku powinien być `WB` (zał. 1 RPB, objaśnienie 2 lit. l), np. `PT_4_WB_…`. Druga możliwość: osobny tom `PT_5_BT_…`.
Ten sam podział ma rejestr C.2 — do korekty.

**I-4. PT-2 BO — wycofane normy są przywołane bez statusu, a rysunki zawierają wymagania oparte na tych normach.**
- Uwagi na arkuszach i w rozdz. 9: „beton wg PN-EN 206+A2 i PN-B-06265”, „napowietrzenie/w/c wg PN-B-06265”.
  Obie normy są wycofane (rejestr A.3, D-09). Zastąpiły je PN-EN 206-1:2026-09 i PN-EN 206-2:2026-09.
- Lista norm w rozdz. 2.2 nie zawiera normy betonu ani PN-EN 13670 i PN-EN 10080 (obie używane w uwagach), a także
  norm spoza rejestru.
- PN-EN 1996-3 i PN-EN ISO 3766 podano bez roku wydania.
Naruszone: W-319 i rejestr A.1 pkt 5.
Poprawka: dodać wykaz norm z wydaniem i statusem (aktualna / wycofana / powołana w WT) i ujednolicić uwagi na rysunkach.

**I-5. W PT-3 IS dane ppoż. są niepełne (W-215, WT § 267 ust. 8) i sprzeczne z uwagami na rysunkach.**
- Rozdz. 7 nie podaje wymogu nierozprzestrzeniania ognia dla izolacji cieplnych i akustycznych instalacji wod.-kan.
  i c.o. Zwolnienie z § 213 obejmuje tylko § 212 i § 216, a § 267 ust. 8 nadal obowiązuje.
- Rozdz. 7 mówi, że przejścia są „bez wymagań odporności ogniowej przepustów”. Uwaga 5 na arkuszach odwodnienia
  (PT-IS-07/08) każe wykonać „przejścia przez stropy z uszczelnieniem ppoż. wg klasy stropu”.
Poprawka: dopisać W-215 do rozdz. 7 i ujednolicić uwagę na arkuszach.

**I-6. PT-3 IS — charakterystyka energetyczna (§ 23 pkt 11 lit. c–d) liczy się na innych danych pompy ciepła niż ogrzewanie.**
Moduł energii przyjmuje P(A−7/W35) = 8,0 kW i SCOP 4,50. Moduł ogrzewania (PC-R290-07) przyjmuje 6,2 kW i SCOP 4,70
(rozdz. 1, poz. 4). Wynik EP ≤ EP_max nie odnosi się więc do urządzenia z projektu.
Poprawka: jedno źródło danych (instalacje.wyroby.PC), a potem przeliczyć EP, punkt biwalentny i hałas.

**I-7. PT-2 BO — § 23 pkt 2 RPB i § 9–10 rozp. Dz.U. 2012 poz. 463 nie są spełnione, a walidator daje „OK”.**
- Dokumentacji badań podłoża nie ma — jest tylko [DOKUMENT ZEWNĘTRZNY – do dołączenia] (s. 302).
- W tab. 8 projektu geotechnicznego parametry są sprzeczne: M₀ = 80 000 kPa w modelu i MES, a 100 000 kPa
  w obliczeniach statycznych. To dotyczy § 10 pkt 2 (parametry obliczeniowe).
- C2-BO-02 ma status „OK”. Powinien być „DO UZUPEŁNIENIA”.
Poprawka: ujednolicić parametry z jednego źródła. W walidatorze [DOKUMENT ZEWNĘTRZNY] w pozycji C2-BO-02 powinien
dawać status inny niż OK.

**I-8. PT-4 IE — ocena ryzyka piorunowego jest wykonana tylko wg wycofanych wydań, a sprawdzenie wg aktualnego odłożono „do PT”.**
Rozdz. 11.4.9: „PN-EN 62305-2:2008/2012 — metodyka; PN-EN IEC 62305-2:2025-09 (EN) — do PT”. Tom jest właśnie PT.
Rejestr A.1 pkt 5 wymaga spełnienia obu wydań.
Dodatkowo:
- N_G przyjęto „wg PN-86/E-05003/01” — norma dawno wycofana, bez statusu;
- przywołano „PN-HD 60364-4-443/-5-534” — -5-534 jest wycofana, zastąpiła ją PN-HD 60364-5-53:2022-10.
Poprawka: wykonać sprawdzenie kontrolne wg wydania z 2025 r. albo uzasadnić jego pominięcie, podać statusy norm
i usunąć zwrot „do PT”.

**I-9. Metryki rysunków we wszystkich tomach: pola projektanta są puste bez znacznika, a pole sprawdzającego nie ma wpisu „nie dotyczy”.**
Na tabliczkach (np. PT-AR-01, PT-AR-D-05, PT-BO-03, PT-IS-01, PT-IE-14) pola „Imię i nazwisko” oraz
„Specjalność, nr uprawnień” są puste i nie mają znacznika [DO UZUPEŁNIENIA]. Pole „Sprawdzający” jest puste.
Naruszone: RPB § 10 ust. 1 pkt 3, W-305 („nie dotyczy (art. 20 ust. 3 pkt 2 PB)”) i W-320.
Walidator sprawdza znaczniki tylko na stronie tytułowej, więc tego nie wykrywa.
Poprawka: wypełnić tabliczki znacznikami z modelu (sekcja projekt) i dodać kontrolę tabliczek w AUD-RYS.

### DROBNE

**D-1. PT-1 AR — w części rysunkowej są arkusze stadium PAB (PB-AR-01…10, tabliczka „PB”), takie same jak w tomie I.**
§ 24 pkt 1 RPB wymaga rysunków „niezawartych” w PAB. Kopie nie są niezgodne z przepisem, ale po zmianie PnB
(art. 36a PB) mogą się rozejść z tomem I.
Poprawka: odesłać do tomu I albo wygenerować arkusze PT-AR (stadium PT). To samo zgłosił zespół.

**D-2. W treści PT są ścieżki lokalne i identyfikatory kodu.**
- PT-3 IS, s. 31: `/home/user/aihouse/model/budynek.yaml`;
- PT-4 IE: „ParametryObwody.WLZ_przekroj, ParametryPV.s_DC”, „tools/generuj_widoki.py”;
- PT-2 BO: „wyniki.json”, „BRAKI_DANYCH.md”, „lamela.views.konstrukcja”.
Są to informacje wewnętrzne, niepotrzebne czytelnikowi PT (kierownikowi budowy); pogarszają zrozumiałość opisu.
Poprawka: zastąpić opisem źródła, np. „model budynku, wersja z dnia …”.

**D-3. PT-2 BO — czytelność i porządek.**
- W wykazie rysunków (tab. 10, s. 306) kolumna „Format” jest za wąska („540×5 / 94”), a numery Lp. się łamią („10 / .”).
- Formaty „nst.” (230×594, 250×594, 510×594 mm itd.) nie są formatami PN-EN ISO 5457 (W-313).
- Strona 8 jest prawie pusta.
- Rozdz. 9 zawiera uwagi o kolizjach napisów. Numery lub tytuły w tych uwagach (PT-BO-05, -11, -14) nie zgadzają się
  z wykazem rysunków (np. PT-BO-05 to w wykazie „ZESTAWIENIE STALI — FUNDAMENT”) — uwagi pochodzą z nieaktualnego
  `raport_widokow.json`. Kolizje napisów trzeba usunąć przed wydaniem.

**D-4. Zakres opracowania na stronie tytułowej i w oświadczeniu PT wykracza poza tom.**
Wymieniono „PZT i PAB…; informacja BIOZ” (AR), „oświadczenie z art. 33 ust. 2 pkt 10 PB” (IS), „PZT — zasilanie nN” (IE).
§ 7 ust. 2 pkt 3 RPB dotyczy zakresu opracowania w danym elemencie, więc w tomie PT należy podać tylko zakres PT.

**D-5. Normy bez wydania lub statusu w PT-1 AR i PT-3 IS (W-319).**
- AR: „klasa ≥ 3 (WT zał. 2 pkt 2.3.2 (PN-EN 12207))” — powinno być „PN-EN 12207:2001, wycofana, powołana w WT”;
  PN-EN ISO 9972 bez roku (:2015-10); PN-EN ISO 15927-4:2007 — nie ma jej w rejestrze A.3.
- IS: PN-EN ISO 13790:2008 (wycofana, zastąpiona przez PN-EN ISO 52016-1) — bez statusu; jako źródło treści normy
  podano „próbkę normy (iTeh, SIST EN 806-3:2006)”, co nie jest źródłem powołania w PT.
- IE: PN-EN 12464-1 bez roku.

**D-6. Oznaczenie danych fikcyjnych.**
W PT-3 IS (rozdz. 7) hydrant „DN80 (ul. Lipowa) [do potwierdzenia]” leży przy ulicy fikcyjnej, a nie ma znacznika
[DANE PRZYKŁADOWE – FIKCYJNE] (rejestr E.1).

**D-7. Metadane PDF i raporty.**
- Pole keywords: „RPB Dz.U. 2022 poz. 1679” bez „ze zm.”.
- Raporty walidacji podają rozmiar w MiB, ale z jednostką „MB” (BO: „10.62 MB”, a plik ma 11,13 MB).

**D-8. Tabliczki PT-IS i PT-IE (format A3×3).**
Numer pola siatki „18” nakłada się na napis formatu „A3×3 (891×420)”.

## 4. Wniosek

Warstwa formalna jest poprawna: nazwy plików, osobne tomy, wektorowość, rozmiar, strona tytułowa, spis treści,
dosłowne brzmienie oświadczenia, znaczniki danych osobowych i fikcyjnych, rozdziały ppoż.

Tomy nie są gotowe do podpisu oświadczenia projektanta:
- K-1: każdy tom powstał z innego, nieaktualnego stanu modelu;
- K-2: PT-2 BO ma niespełnione warunki i 31 niezamkniętych analiz;
- K-3: rysunki IS i IE są sprzeczne z obliczeniami.
Przed ostatnim złożeniem trzeba też poprawić podstawę PT w PT-2 BO (I-1), § 23 pkt 12 (I-2) i uprawnienia
telekomunikacyjne w PT-4 IE (I-3).

Walidator `sprawdz_tom` daje dziś wynik „OK” mimo K-2, K-3, I-7 i I-9. Listy kontrolne trzeba uzupełnić
o te warunki.
