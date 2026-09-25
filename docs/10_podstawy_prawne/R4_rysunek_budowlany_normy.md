# R4 — Normy rysunku budowlanego: specyfikacja dla silnika rysunkowego (Dom LAMELA)

Zespół: R4 (normy rysunku budowlanego). Stan badań: 2026-09-24/25. Wersja: 1.0.
Materiały robocze (pobrane źródła, wyciągi tekstu, statusy PKN w JSON):
`/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R4/`
(`R4_pkn_status_2026-09-25.json`: 263 rekordy z katalogu PKN; `det_*.txt`: karty norm ze spisami treści; `src/`: PDF-y i wyciągi).

**Oznaczenia w kolumnie „pierwotne?”**
* **TAK-A**: tekst aktu prawnego (API ELI Sejmu, PDF Dziennika Ustaw).
* **TAK-K**: katalog PKN (wyszukiwarka norm na wiedza.pkn.pl). Źródło statusu, dat, spisów treści i zakresu.
* **TAK-N**: oryginalny tekst normy ISO/EN z oficjalnego podglądu (iTeh „STANDARD PREVIEW”). To zwykle fragment normy.
  Polska wersja PN może się różnić tłumaczeniem, ale nie treścią techniczną (wprowadzenie IDT).
* **NIE**: źródło wtórne, np. wykład uczelniany, podręcznik, materiał izby, PKN-u (prezentacja) lub producenta.
* **NIEZWERYFIKOWANE**: wartości, których nie potwierdziło żadne dostępne źródło. W projekcie traktujemy je jako założenie
  i objaśniamy je w legendzie rysunku.

Zasada zespołu R3: rozporządzenie WT (Dz.U. 2002 nr 75 poz. 690) ma w ELI status „uznany za uchylony” od 2026-09-21.
Powiązania podajemy jako „WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) §…”. Status WT musi potwierdzić zespół R3.

---

## 1. Streszczenie

1. **Rysunki mają podstawę prawną w rozporządzeniu, nie w samych normach.** Chodzi o rozporządzenie Ministra Rozwoju z 11.09.2020 r.
   w sprawie szczegółowego zakresu i formy projektu budowlanego (Dz.U. 2020 poz. 1609; t.j. Dz.U. 2022 poz. 1679; zm. Dz.U. 2023
   poz. 2405, zmienionym przez Dz.U. 2024 poz. 473, oraz Dz.U. 2026 poz. 597; w ELI: „akt posiada tekst jednolity”, IN_FORCE;
   akty zmieniające wg ELI: 2021/1169, 2021/2280, 2023/2405, 2026/597).
   * § 9 ust. 1 wymaga oznaczeń graficznych i literowych **z Polskich Norm z załącznika nr 2 „lub innych objaśnionych w legendzie”**
     oraz zasad wymiarowania z norm z załącznika nr 2.
   * Załącznik nr 2 zawiera PN-EN ISO 4157-1/-2/-3, PN-EN ISO 6284, PN-EN ISO 11091, PN-B-01025, PN-B-01027, PN-B-01029,
     PN-EN ISO 5261, PN-EN ISO 2553, PN-EN ISO 5845-1 oraz (dla § 12) PN-ISO 9836.
   * Ma dopisek „**Stosuje się najnowszą normę opublikowaną w języku polskim**”.
   * Normy arkusza, linii, pisma i podziałek (ISO 5457, 7200, 9431, 128, 3098, 5455), materiałów (PN-B-01030), zbrojenia
     (ISO 3766) i symboli elektrycznych **nie są powołane w rozporządzeniu**. Są to normy dobrowolne, choć PN-B-01025:2004
     powołuje je normatywnie w swoim rozdz. 2.
   * Wniosek dla silnika: **każdy arkusz dostaje legendę**. Pokrywa ona wszystkie symbole spoza norm z zał. 2 oraz symbole
     z norm wycofanych.
2. **Skale minimalne (§ 9 ust. 3 i 5).** Rysunki PAB i PT: nie mniejsza niż **1:100** (1:200 tylko dla obiektów dużych).
   PZT: nie mniejsza niż **1:500**, na aktualnej mapie do celów projektowych lub jej kopii (§ 15 ust. 1).
3. **Metryka rysunku (§ 10).** Obowiązkowe pola:
   * nazwa obiektu;
   * tytuł, skala i numer rysunku;
   * imię i nazwisko projektanta oraz nr uprawnień;
   * data sporządzenia;
   * podpis, ale tylko w postaci papierowej.

   Dane sprawdzającego trafiają do metryki tylko przy obowiązku sprawdzenia. Art. 20 ust. 3 pkt 2 PB (t.j. Dz.U. 2026 poz. 524 ze zm.: poz. 605 i 646, które art. 20 nie zmieniają)
   zwalnia z niego projekty budynków mieszkalnych jednorodzinnych.
   Plik PDF podpisuje się kwalifikowanym podpisem elektronicznym, podpisem osobistym albo zaufanym (§ 7 ust. 4a).
4. **Forma elektroniczna (§ 2b).** Obowiązuje PDF, a część rysunkowa ma być **wektorowa**. Plik ≤ **150 MB**. Nazwy plików wg
   zał. nr 1, np. `PZT_PAB_ZL_rrrr.mm.dd`, `PT_1_BO_rrrr.mm.dd`. Wersję papierową oprawia się do formatu A4 (§ 2a).
5. **Nowość 2026 (Dz.U. 2026 poz. 597, § 15 ust. 3).** Na PZT odległości od granic, odległości wzajemne i wymiary obiektów
   zapisuje się z dokładnością **0,01 m**. Wartości w pełnych metrach można zapisać z jednym miejscem po przecinku.
   Przepis wchodzi w życie po 6 miesiącach od ogłoszenia (ogłoszono 4.05.2026, czyli ok. 5.11.2026; wyliczenie własne).
   Nie dotyczy wniosków złożonych wcześniej. Silnik stosuje tę zasadę od razu.
6. **Zmiany statusów norm (katalog PKN, 2026-09-24/25).**
   * Normy linii PN-EN ISO 128-20/-21, PN-ISO 128-22/-23/-24 są **wycofane**. Zastępuje je **PN-EN ISO 128-2:2023-05** (wersja
     angielska, wprowadza EN ISO 128-2:2022).
   * Normy widoków i przekrojów PN-ISO 128-30/-34/-40/-44/-50 (w tym dawne PN-ISO 4069) są wycofane. Zastępuje je
     **PN-EN ISO 128-3:2023-02** (EN).
   * PN-EN ISO 3098-0 jest wycofana, zastępuje ją PN-EN ISO 3098-1:2015-06 (EN).
   * PN-EN ISO 4066 włączono do PN-EN ISO 3766:2006.
   * **PN-ISO 9836:2015-12 jest wycofana**. Obowiązuje **PN-ISO 9836:2022-07** (wersja polska, IDT z ISO 9836:2017).
   * **PN-EN ISO 7519:2024-09 wycofano 2026-04-16 bez następcy w katalogu**. ISO wydało ISO 7519:2025.
   * **PN-EN 60617-11:2004 (symbole planów instalacji elektrycznych) wycofano 2005-12-01 bez zastępstwa.** Obowiązuje baza IEC 60617.
   * **PN-B-01701:1984 (symbole instalacji wod.-kan. wewnętrznych) jest wycofana bez zastępstwa.**
   * PN-B-01410:1989 (wentylacja) jest wycofana. Aktualna jest PN-EN 12792:2006.
   * PN-70/B-02365 jest wycofana (zastąpiły ją kolejno PN-ISO 9836:1997, PN-ISO 9836:2015-12 i PN-ISO 9836:2022-07).
7. **Normy aktualne, z których silnik bierze konkretne reguły:**
   * PN-B-01025:2004, PN-B-01027:2002, PN-B-01029:2000, PN-B-01030:2000;
   * PN-EN ISO 4157-1/-2/-3:2001, PN-EN ISO 5457:2002 (+A1:2010), PN-EN ISO 7200:2007, PN-EN ISO 9431:2011;
   * PN-EN ISO 5455:1998, PN-EN ISO 3098-2…-6:2002, PN-EN ISO 11091:2001, PN-EN ISO 3766:2006;
   * PN-B-01040:1994, PN-B-01700:1999, PN-EN 12792:2006, PN-EN 1861:2001, PN-ISO 2594:1998.
8. **Kluczowe wartości dla silnika:**
   * linie: szereg 0,13/0,18/0,25/0,35/0,5/0,7/1/1,4/2 mm, proporcje 1:2:4 (cienka:gruba:bardzo gruba);
   * odstęp linii równoległych ≥ 0,7 mm;
   * pismo: 1,8/2,5/3,5/5/7/10/14/20 mm;
   * ramka arkusza: 20 mm z lewej, 10 mm z pozostałych stron, linia 0,7 mm;
   * tabliczka: szerokość 180 mm, prawy dolny róg;
   * podziałki: 1:500/1:100/1:50/1:20/1:10/1:5;
   * wymiary: ukośne kreski pod 45°, pierwszy ciąg ok. 10 mm od obrysu, kolejne co 7–8 mm, otwory ułamkiem szer./wys.;
   * rzędne w m z 3 miejscami po przecinku (PN-B-01025);
   * numeracja kondygnacji od 1 na poziomie terenu (PN-B-01025, ISO 4157-1).
9. **Kolizje z założeniami projektu.**
   * `SCHEMAT_MODELU.md` numeruje pomieszczenia „0.01” (parter = 0), a brief zakłada rzędne „±0,00, +3,15” (2 miejsca po
     przecinku). Według PN-B-01025 (źródła wtórne zgodne z ISO 4157-1) parter ma numer **1**, a rzędne podaje się z **3** miejscami
     po przecinku. Rekomendacja w pkt 3.9 i 3.6.
   * Układ współrzędnych geodezyjnych PL-2000 ma oś **X na północ i Y na wschód**, odwrotnie niż model (x→E, y→N). Ma to
     znaczenie dla siatki współrzędnych na PZT (PN-B-01027 pkt 4.2: „pierwszą x, drugą y”).

---

## 2. Tabela wymagań i reguł

### 2.1 Rejestr norm: numer, rok, tytuł, status PKN

Status sprawdzono w wyszukiwarce norm PKN (https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm) w dniach 2026-09-24/25.
Źródło: TAK-K. Kolumna „Rola” pokazuje, jak używamy normy w projekcie.

| Norma (numer:rok, wersja) | Tytuł (PKN) | Status PKN | Zastępuje / zastąpiona przez | Rola w projekcie |
|---|---|---|---|---|
| PN-EN ISO 5457:2002 (pol.) + PN-EN ISO 5457:2002/A1:2010 (ang.) | Dokumentacja techniczna wyrobu – Wymiary i układ arkuszy rysunkowych | aktualna (obie) | zast. PN-N-01601:1976, PN-N-01612:1980 | formaty, ramka, pola siatki |
| PN-EN ISO 7200:2007 (pol.) | Dokumentacja techniczna wyrobu – Pola danych w tabliczkach rysunkowych i nagłówkach dokumentów | aktualna | zast. PN-EN ISO 7200:2005 | tabliczka |
| PN-EN ISO 9431:2011 (ang.) | Rysunek budowlany – Części arkusza rysunkowego przeznaczone na rysunek, tekst i tabliczkę tytułową | aktualna | zast. PN-ISO 9431:1994 (pol., wycofana) | układ arkusza |
| PN-EN ISO 128-1:2020-12 (ang.) | TPD – Zasady ogólne przedstawiania – Cz. 1: Wprowadzenie i wymagania podstawowe | aktualna | zast. PN-ISO 128-1:2006 | ogólne |
| **PN-EN ISO 128-2:2023-05 (ang.)** | TPD – Zasady ogólne przedstawiania – Cz. 2: Zasady podstawowe dotyczące linii | **aktualna** | zast. PN-EN ISO 128-2:2021-02, a ta zast. PN-EN ISO 128-20:2002, 128-21:2006, PN-ISO 128-22:2003, **PN-ISO 128-23:2002**, 128-24:2003 | linie |
| **PN-EN ISO 128-3:2023-02 (ang.)** | TPD – Zasady ogólne przedstawiania – Cz. 3: Widoki, przekroje i kłady | **aktualna** | zast. PN-EN ISO 128-3:2021-01, a ta zast. PN-ISO 128-30/-34/-40/-44/**-50**:2006 | przekroje, kreskowanie |
| PN-EN ISO 128-100:2020-12 (ang.) | … Cz. 100: Indeks | aktualna | — | — |
| PN-ISO 128-23:2002 (pol.) | Rysunek techniczny – Ogólne zasady przedstawiania – Cz. 23: Linie na rysunkach budowlanych | **wycofana** | zastąpiona przez PN-EN ISO 128-2 | tabela zastosowań linii (treść historyczna) |
| PN-EN ISO 3098-1:2015-06 (ang.) | Dokumentacja techniczna wyrobu – Pismo – Cz. 1: Wymagania ogólne | aktualna | zast. PN-EN ISO 3098-0:2002 | pismo |
| PN-EN ISO 3098-2:2002, -3:2002, -4:2002, -5:2002, -6:2002 (pol.) | Pismo – cz. 2 alfabet łaciński; 3 grecki; 4 znaki diakrytyczne; 5 pismo CAD; 6 cyrylica | aktualne | — | pismo (diakrytyki PL, CAD) |
| PN-EN ISO 5455:1998 (pol.) | Rysunek techniczny – Podziałki | aktualna | zast. PN-N-01610:1980 | podziałki |
| **PN-B-01029:2000** (pol.) | Rysunek budowlany – Zasady wymiarowania na rysunkach architektoniczno-budowlanych | **aktualna** (zatw./publ. 2000-05-08) | zast. PN-B-01029:1960 | wymiarowanie, **zał. 2 rozp.** |
| **PN-B-01025:2004** (pol.) | Rysunek budowlany – Oznaczenia graficzne na rysunkach architektoniczno-budowlanych | **aktualna** (zatw. 2003-12-05, publ. 2004-06-01) | zast. PN-B-01025:1970 | oznaczenia arch.-bud., **zał. 2 rozp.** |
| **PN-B-01030:2000** (pol.) | Rysunek budowlany – Oznaczenia graficzne materiałów budowlanych | **aktualna** (2000-10-31) | zast. PN-B-01030:1970 | kreskowanie materiałów |
| **PN-B-01027:2002** (pol.) | Rysunek budowlany – Oznaczenia graficzne stosowane w projektach zagospodarowania działki lub terenu | **aktualna** (2002-07-11) | zast. PN-B-01027:1971, PN-B-01035:1971 | PZT, **zał. 2 rozp.** |
| PN-EN ISO 11091:2001 (pol.) | Rysunek budowlany – Projekty zagospodarowania terenu | aktualna | zast. PN-B-01031:1962 | PZT, **zał. 2 rozp.** |
| PN-EN ISO 4157-1:2001, -2:2001, -3:2001 (pol.) | Rysunek budowlany – Systemy oznaczeń – Cz. 1: Budynki i części budynków; Cz. 2: Nazwy i numery pomieszczeń; Cz. 3: Identyfikatory pomieszczeń | aktualne | zast. PN-B-01025:1970 (cz.) | numeracja, **zał. 2 rozp.** |
| PN-EN ISO 7519:1999 (pol.) | Rysunek techniczny – Rysunki budowlane – Ogólne zasady przedstawiania na rysunkach zestawieniowych | wycofana | zastąpiona przez PN-EN ISO 7519:2024-09 | historyczna |
| **PN-EN ISO 7519:2024-09 (ang.)** | TPD – Dokumentacja budowlana – Ogólne zasady przedstawiania na rysunkach zestawieniowych ogólnych i montażowych | **wycofana 2026-04-16**, następca w katalogu PKN: brak | (ISO 7519:2025, 3. wyd., drobna rewizja) | zasady przedstawiania (nieobowiązkowe) |
| PN-EN ISO 3766:2006 (pol.) | Rysunek budowlany – Uproszczony sposób przedstawiania zbrojenia betonu | aktualna | zast. PN-EN ISO 3766:2005 oraz **PN-EN ISO 4066:2001** | zbrojenie, zestawienie stali |
| PN-B-01040:1994 (pol.) | Rysunek konstrukcyjny budowlany – Zasady ogólne | aktualna | — | rysunki konstrukcyjne |
| PN-B-01041:1988 | Rysunek konstrukcyjny budowlany – Konstrukcje betonowe, żelbetowe i sprężone | wycofana, bez następcy | — | — |
| PN-B-01042:1999 (pol.) | Rysunek konstrukcyjny budowlany – Konstrukcje drewniane | aktualna | — | ew. elementy drewniane |
| PN-EN ISO 5261:2002 (pol.) | Rysunek techniczny – Przedstawianie uproszczone prętów i kształtowników | aktualna | zast. PN-ISO 5261:1994 | stal (słupy wiaty), **zał. 2 rozp.** |
| PN-EN ISO 2553:2019-06 (pol./ang./niem.) | Spajanie i procesy pokrewne – Umowne przedstawianie na rysunkach – Złącza spajane | aktualna | zast. PN-EN ISO 2553:2014-03 | spoiny, **zał. 2 rozp.** |
| PN-EN ISO 5845-1:2002 (pol.) | Rysunek techniczny – Przedstawianie uproszczone zespołów z częściami złącznymi – Cz. 1 | aktualna | — | śruby/kotwy, **zał. 2 rozp.** |
| PN-EN ISO 6284:2024-06 (ang.) / PN-EN ISO 6284:2001 (pol.) | Dokumentacja budowlana – Oznaczanie odchyłek granicznych | 2024-06: aktualna; 2001 (pol.): wycofana | 2024-06 zast. 2001 | tolerancje, **zał. 2 rozp.** |
| PN-ISO 2594:1998 (pol.) | Rysunek budowlany – Metody rzutowania | aktualna | — | rzutowanie |
| PN-EN ISO 5456-1/-2/-3:2002, -4:2006 (pol.) | Rysunek techniczny – Metody rzutowania | aktualne | — | aksonometria/wizualizacje |
| PN-EN ISO 8560:2019-06 (ang.) | Rysunek techniczny – Rysunki budowlane – Przedstawianie modularnych wymiarów, linii i siatek | aktualna | zast. PN-EN ISO 8560:2011 | osie/siatki |
| PN-EN ISO 129-1:2020-03 (ang.) + A1:2021-06 | TPD – Prezentacja wymiarów i tolerancji – Cz. 1: Zasady ogólne | aktualna | — | ogólne zasady wymiarów |
| PN-EN ISO 10209:2022-08 (ang.) | TPD – Terminologia | aktualna | — | słownictwo |
| PN-EN ISO 13567-1:2017-11, -2:2017-12 (ang.) | Organizacja i nazewnictwo warstw w programach CAD | aktualne | — | nazwy warstw (opcja) |
| PN-EN ISO 7518:2011 (ang.) | Rysunki budowlane – Uproszczone przedstawianie rozbiórki i przebudowy | aktualna | — | nie dotyczy (nowy budynek) |
| PN-ISO 4068:1998 | Rysunek budowlany – Linie odniesienia (nawiązania) | wycofana, bez następcy | — | — |
| PN-N-01603:1986 | Rysunek techniczny – Składanie formatów arkuszy | wycofana, bez następcy | — | składanie do A4: praktyka |
| **PN-ISO 9836:2022-07 (pol.)** | Właściwości użytkowe w budownictwie – Określanie i obliczanie wskaźników powierzchniowych i kubaturowych | **aktualna** (zatw. 2022-05-24, publ. 2022-07-18; IDT ISO 9836:2017) | zast. **PN-ISO 9836:2015-12** (wycofana), a ta zast. PN-ISO 9836:1997 | powierzchnie/kubatura, **§ 12 i zał. 2 rozp.** |
| PN-B-02365:1970 (PN-70/B-02365) | Powierzchnia budynków – Podział, określenia i zasady obmiaru | **wycofana** | zastąpiona przez PN-ISO 9836:1997 | tylko porównanie „katalogowe” |
| PN-EN 60617-2…-13 (2002–2004) | Symbole graficzne stosowane w schematach | **wycofane** | — | — |
| **PN-EN 60617-11:2004 (pol.)** | … Cz. 11: Architektoniczne i topograficzne plany i schematy instalacji elektrycznych | **wycofana 2005-12-01, bez następcy** | zast. PN-EN 60617-11:2002 | symbole elektryczne tylko z legendą (baza IEC 60617) |
| PN-EN 61082-1:2015-03 (ang.) | Przygotowanie dokumentów używanych w elektrotechnice – Cz. 1: Podstawowe zasady | aktualna | zast. PN-EN 61082-1:2006 | schematy rozdzielnic |
| PN-EN IEC 81346-1:2023-01 (ang.) | Systemy przemysłowe… – Zasady strukturyzacji i oznaczenia referencyjne – Cz. 1 | aktualna | zast. PN-EN 81346-1:2009 | oznaczenia aparatów (-F1, -Q1…) |
| PN-EN ISO 81714-1:2010 (ang.) | Projektowanie symboli graficznych stosowanych w dokumentacji technicznej wyrobów – Cz. 1 | aktualna | zast. PN-EN ISO 81714-1:2002 | projektowanie własnych symboli |
| PN-B-01700:1999 (pol.) | Wodociągi i kanalizacja – Urządzenia i sieć zewnętrzna – Oznaczenia graficzne | aktualna | zast. PN-B-01700:1985 | przyłącza wod.-kan. (PZT, PT) |
| **PN-B-01701:1984** | Instalacje wewnętrzne wodociągowe i kanalizacyjne – Oznaczenia na rysunkach | **wycofana, bez następcy** | — | tylko z legendą |
| PN-EN ISO 6412-1:2018-03, -2:2018-04, -3:2018-03 (ang.) | TPD – Uproszczone przedstawianie rurociągów (cz. 1 zasady/rzutowanie prostokątne; cz. 2 izometria; cz. 3 elementy końcowe went. i odwadniające) | aktualne | zast. wersje 2001 (pol.) | rurociągi wod.-kan., c.o. |
| PN-EN 12792:2006 (pol.) | Wentylacja budynków – Symbole, terminologia i oznaczenia na rysunkach | aktualna | zast. PN-EN 12792:2004 (ang.), a ta zast. PN-B-01411:1999 | wentylacja (rekuperacja) |
| PN-B-01410:1989 | Wentylacja i klimatyzacja – Rysunek techniczny – Zasady wykonywania i oznaczenia | wycofana | — | — |
| PN-B-01440:1998 | Technika sanitarna – Istotne wielkości, symbole i jednostki miar | wycofana | — | — |
| PN-EN 1861:2001 (pol.) | Instalacje ziębnicze i pompy ciepła – Schematy ideowe i montażowe instalacji, rurociągów i przyrządów – Układy i symbole | aktualna | — | schemat pompy ciepła |

### 2.2 Reguły, wymagania i wartości

Skróty URL:
* **[ROZP]** https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf (t.j.);
* **[ROZP23]** https://api.sejm.gov.pl/eli/acts/DU/2023/2405/text.pdf;
* **[ROZP26]** https://api.sejm.gov.pl/eli/acts/DU/2026/597/text.pdf;
* **[ELI1609]** https://api.sejm.gov.pl/eli/acts/DU/2020/1609;
* **[PB]** https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf;
* **[PKN]** https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm;
* **[AGH-P]** https://home.agh.edu.pl/~olesiak/rysunek/04_przekroje.pdf;
* **[AGH-W]** https://galaxy.agh.edu.pl/~olesiak/rysunek/05_wymiarowanie.pdf;
* **[AGH-Z]** https://galaxy.agh.edu.pl/~olesiak/budownictwo/01_Projekt%20zagospodarowania%20dzialki_www.pdf;
* **[AGH-K]** https://home.agh.edu.pl/~olesiak/rysunek/06a_konstrukcyjny.pdf;
* **[PWR9]** https://wis.pwr.edu.pl/d/JGBUKOTtQKxVvEkBoSk8TDxZIUTggT0FAGRoIVURNWHxXAlhnRkokXiVvBChKWQBPFgEYITwyHUBTdE0TFRwTPTxUWHFVFW1aClkQelJaAlcBXlE7PhtPWEsjE14IA1hhQUMDOwEbdQQo/rystech_z_geom_wykr-_cw_9_9.pdf;
* **[PCEZ]** http://www.pcez-bytow.pl/download/plk/rysunek-budowlany.pdf (materiał szkolny KOWEZ; cytuje Wojciechowski L., „Dokumentacja budowlana 1. Rysunek budowlany”, WSiP 1999);
* **[7519:1991]** https://cdn.standards.iteh.ai/samples/14288/eddd4c11ea654c9cbdf5dcd53f717597/ISO-7519-1991.pdf (oryginalny tekst ISO 7519:1991, podgląd).

#### A. Podstawa prawna części rysunkowej

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-A01 | Projekt sporządza się **po polsku**, w czytelnej technice graficznej. | rozp. § 2 | [ROZP] | TAK-A | — |
| R4-A02 | Projekt papierowy oprawia się do formatu **A4**. | rozp. § 2a | [ROZP] | TAK-A | Arkusze większe składa się do A4. PN-N-01603 (składanie) jest wycofana, więc stosujemy praktykę (pkt 3.1). |
| R4-A03 | Wersja elektroniczna: strona tytułowa, spis treści, części opisowa i rysunkowa jako **PDF**. Rysunki **w postaci wektorowej**. Pojedynczy plik **≤ 150 MB**. | rozp. § 2b ust. 1–3 | [ROZP] | TAK-A | Silnik eksportuje PDF wektorowy. Rastry są dopuszczalne tylko jako podkład mapy (§ 15 ust. 1a). |
| R4-A04 | Nazwy plików wg zał. nr 1: PZT_z / PZT_x_z; PAB_z / PAB_x_z; PT_z / PT_x_y_z; ZL_z / ZL_x_z; PZT_PAB_z; PZT_PAB_ZL_z; PZT_ZL_z; PAB_ZL_z. Oznaczenia: x = nr kolejny pliku; y = symbol specjalności (AR, BO, IS, IE, BT, IN, WB …); z = data **rrrr.mm.dd**. | rozp. § 2b ust. 4, zał. nr 1 | [ROZP] | TAK-A | Np. `PT_1_AR_2026.09.25.pdf`, `PT_2_BO_…`, `PT_3_IS_…`, `PT_4_IE_…`. |
| R4-A05 | PZT, PAB i załączniki mają tę samą postać (papier albo e-). PT może mieć inną postać. | rozp. § 5a | [ROZP] | TAK-A | — |
| R4-A06 | Strony numeruje się kolejno, osobno dla każdego elementu i tomu. W części rysunkowej wystarczy **numer rysunku**. | rozp. § 6 ust. 1–3 | [ROZP] | TAK-A | Numer rysunku musi być unikalny w danym elemencie projektu. |
| R4-A07 | Część rysunkową zaopatruje się w oznaczenia graficzne i literowe **z PN wymienionych w zał. nr 2** „**lub inne objaśnione w legendzie**” oraz w wyjaśnienia opisowe. Wymiaruje się wg zasad PN z zał. nr 2. | rozp. § 9 ust. 1 | [ROZP] | TAK-A | Podstawa reguły „legenda na każdym arkuszu”. |
| R4-A08 | Zał. nr 2 (miejsce powołania: § 9 ust. 1): PN-EN ISO 4157-1, -2, -3; PN-EN ISO 6284; PN-EN ISO 11091; PN-B-01025; PN-B-01027; PN-B-01029; PN-EN ISO 5261; PN-EN ISO 2553; PN-EN ISO 5845-1. Dla § 12: PN-ISO 9836. Dopisek: „**Stosuje się najnowszą normę opublikowaną w języku polskim**”. | rozp. zał. nr 2 | [ROZP] | TAK-A | Dla PN-EN ISO 6284 najnowsza wersja **polska** to 2001 (wycofana), aktualna 2024-06 jest angielska. Patrz pkt 4. |
| R4-A09 | PAB i PT oznacza się klasami odporności ogniowej lub dymoszczelności elementów oddzielenia ppoż. oraz elementów z przejściami instalacyjnymi, a także drzwi i bram ppoż. | rozp. § 9 ust. 2 | [ROZP] | TAK-A | Silnik obsługuje etykietę klasy (np. „EI 30”) przy ścianie lub drzwiach. Zakres ustala zespół ppoż. |
| R4-A10 | Skala PAB i PT: nie mniejsza niż **1:200** dla obiektów dużych i **1:100** dla pozostałych obiektów oraz ich części. | rozp. § 9 ust. 3 | [ROZP] | TAK-A | Dom LAMELA: min. 1:100. |
| R4-A11 | Skala PZT: dostosowana do obiektu i czytelna, **nie mniejsza niż 1:500** (dla inwestycji liniowych 1:1000). | rozp. § 9 ust. 5 | [ROZP] | TAK-A | — |
| R4-A12 | **Metryka** na każdym rysunku: 1) nazwa obiektu (min. skrócona, identyfikująca); 2) tytuł, skala i numer rysunku; 3) imię i nazwisko projektanta oraz nr uprawnień; 4) data sporządzenia rysunku; 5) podpis projektanta (tylko wersja papierowa). | rozp. § 10 ust. 1 | [ROZP] | TAK-A | Dane osobowe są **polami do uzupełnienia** (brief § 7 pkt 4). |
| R4-A13 | Jeśli PAB/PT podlega sprawdzeniu, metryka zawiera dodatkowo imię i nazwisko, nr uprawnień, datę sprawdzenia i podpis sprawdzającego (podpis tylko w wersji papierowej). | rozp. § 10 ust. 2 | [ROZP] | TAK-A | — |
| R4-A14 | Obowiązek sprawdzenia PAB i PT (art. 20 ust. 2) **nie dotyczy** m.in. „projektów obiektów budowlanych o prostej konstrukcji, jak: budynki mieszkalne jednorodzinne…”. | PB art. 20 ust. 3 pkt 2 | [PB] | TAK-A | Pole „sprawdzający” jest więc opcjonalne. Czy LAMELA (wsporniki) to „prosta konstrukcja”, rozstrzyga zespół prawny (pkt 4). |
| R4-A15 | Osoba opracowująca lub sprawdzająca część projektu w postaci elektronicznej opatruje plik **kwalifikowanym podpisem elektronicznym, podpisem osobistym albo zaufanym**. | rozp. § 7 ust. 4a | [ROZP] | TAK-A | Na PDF nie wstawia się grafiki podpisu, a pole „podpis” w metryce pozostaje puste lub z adnotacją. |
| R4-A16 | Część rysunkowa PZT powstaje na **aktualnej mapie do celów projektowych** lub jej kopii. W postaci elektronicznej mapa może być wektorowa lub rastrowa. | rozp. § 15 ust. 1, 1a | [ROZP] | TAK-A | Podkład: mapa geodezyjna. Dla przykładowej działki jest fikcyjna i trzeba ją oznaczyć jako przykładową. |
| R4-A17 | Treść rysunku PZT obejmuje m.in.: orientację względem stron świata; granice działki; obrys i usytuowanie obiektów z wejściami i wjazdami; liczbę kondygnacji; rzędne terenu istniejącego i projektowanego; wymiary i odległości od granic; komunikację; zieleń; uzbrojenie ze spadkami, przekrojami, rzędnymi i odległościami; odprowadzenie wód opadowych. | rozp. § 15 ust. 2 pkt 1–15 (pkt 15 dodany przez Dz.U. 2026 poz. 597 § 1 pkt 3 lit. a, w mocy od 2026-05-19: elementy obiektu zbiorowej ochrony, **nie dotyczy** domu jednorodzinnego) | [ROZP]; [ROZP26] | TAK-A | Lista kontrolna dla generatora PZT (pkt 3.11). *Weryfikacja 2026-09-25: było „pkt 1–14” (stan t.j. 2022) i odsyłacz „pkt 3.12” (to sekcja instalacji), poprawiono.* |
| R4-A18 | **Nowy § 15 ust. 3:** na PZT odległości od granic, wzajemne odległości obiektów i urządzeń oraz ich wymiary oznacza się z dokładnością zapisu **0,01 m**. Wartości w pełnych metrach mogą mieć jedno miejsce po przecinku. Zakres: co jest potrzebne do sprawdzenia zgodności z przepisami, WZ lub uchwałą lokalizacyjną. | rozp. § 15 ust. 3, dodany przez Dz.U. 2026 poz. 597 § 1 pkt 3 lit. b | [ROZP26] | TAK-A | Wchodzi w życie po 6 mies. od ogłoszenia (4.05.2026), czyli ok. 5.11.2026 (wyliczenie własne). Nie dotyczy wniosków złożonych wcześniej (§ 2 ust. 2 rozp. zm.). *Weryfikacja 2026-09-25: treść § 1 pkt 3 lit. b, § 2 ust. 2 i § 3 potwierdzona w PDF Dz.U. 2026 poz. 597. Data ogłoszenia 4.05.2026 potwierdzona. Wejście reszty aktu 2026-05-19 wg ELI. ELI nie podaje odrębnej daty dla § 1 pkt 3 lit. b: 6 mies. mija 4.11.2026, więc przepis wchodzi 5.11.2026.* |
| R4-A19 | PAB (rysunki): rzuty wszystkich charakterystycznych poziomów; charakterystyczne przekroje z nawiązaniem do terenu i podłoża; widoki elewacji **ze wszystkich widocznych stron** oraz dachu, z oznaczeniem wyrobów wykończeniowych i kolorystyki. | rozp. § 21 pkt 1 | [ROZP] | TAK-A | Dach płaski: rysunek „rzut dachu” lub widok z góry. |
| R4-A20 | Wszystkie normy rysunkowe PN są w PKN normami dobrowolnymi. Powołanie w rozporządzeniu czyni je jego „integralną częścią”. Wycofanie normy nie oznacza zakazu jej stosowania. | PKN, komunikat KT 232 (PN-ISO 9836) | https://wiedza.pkn.pl/en/web/popularne-zagadnienia/polska-norma-dotyczaca-obliczania-powierzchni-i-kubatury | TAK-K | Uzasadnia używanie wycofanych norm symboli (np. PN-B-01701, PN-EN 60617-11), ale **tylko z legendą**. |

#### B. Arkusz, ramka, tabliczka, pola arkusza

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-B01 | Formaty po obcięciu (T), mm: **A0 841×1189; A1 594×841; A2 420×594; A3 297×420; A4 210×297**. Pole rysunkowe (±0,5): A0 821×1159; A1 574×811; A2 400×564; A3 277×390; A4 180×277. Arkusz nieobcięty: A0 880×1230 … A4 240×330. | ISO 5457:1999 tabl. 1 (PN-EN ISO 5457:2002) | https://cdn.standards.iteh.ai/samples/29017/e46c0ec5d98f470aab82dae76889f229/ISO-5457-1999.pdf | TAK-N | Rysunek na najmniejszym arkuszu, który zapewnia czytelność (3.1). |
| R4-B02 | Formaty wydłużone **należy unikać**. Jeśli trzeba, łączy się krótszy bok formatu A z dłuższym bokiem większego formatu, np. A3.1 = 297×841. | ISO 5457 3.2 | j.w. | TAK-N | — |
| R4-B03 | **Margines lewy 20 mm** (z ramką, na wpięcie), **pozostałe 10 mm**. Ramka pola rysunkowego to **linia ciągła 0,7 mm**. | ISO 5457 4.2 | j.w. | TAK-N | — |
| R4-B04 | **4 znaki centrujące** na osiach symetrii arkusza (tolerancja 1 mm): linia ciągła 0,7 mm od pola siatki odniesień, wchodząca **10 mm** za ramkę. | ISO 5457 4.3 | j.w. | TAK-N | — |
| R4-B05 | **Siatka odniesień**: pola dł. **50 mm** liczone od osi symetrii; wiersze literami od góry (bez I i O), kolumny cyframi od lewej. Znaki **3,5 mm** pismem prostym. Linie **0,35 mm**. Liczba pól (dłuższy × krótszy bok): **A0 24×16; A1 16×12; A2 12×8; A3 8×6; A4 6×4**. Na A4 znaki tylko u góry i z prawej. | ISO 5457 4.4, tabl. 2 | j.w. | TAK-N | Opcjonalne w praktyce PB, ale zgodne z normą. Zalecamy włączyć dla A2 i większych. |
| R4-B06 | Znaczniki obcięcia w narożnikach: dwa nakładające się prostokąty **10×5 mm**. | ISO 5457 4.5 | j.w. | TAK-N | Tylko przy wydruku na arkuszu nieobciętym. |
| R4-B07 | Tabliczka w **prawym dolnym rogu** pola rysunkowego. Oznaczenie formatu (np. „A1”) w dolnym marginesie przy prawym rogu. Kierunek czytania rysunku = kierunek czytania tabliczki. Wg wyd. 1999 A3–A0 tylko poziomo, A4 tylko pionowo. **Zmiana A1:2010 dopuszcza A4 także poziomo.** | ISO 5457 3.1, 4.1; Amd 1:2010 | j.w.; https://www.iso.org/standard/46218.html | TAK-N / NIE (A1: opis wtórny z wyszukiwania) | Treść A1:2010 wg streszczenia wtórnego; tekstu zmiany nie widzieliśmy. |
| R4-B08 | Tabliczka (ISO 7200:2004 = PN-EN ISO 7200:2007). **Pola obowiązkowe (M):** właściciel prawny dokumentu; nr identyfikacyjny (zalecane 16 znaków); data wydania (10 zn.); nr arkusza (4 zn.); tytuł (25/30 zn.); osoba zatwierdzająca (20 zn.); autor/opracował (20 zn.); rodzaj dokumentu (30 zn.). **Opcjonalne (O):** indeks zmian (2 zn.), liczba arkuszy, kod języka, tytuł uzupełniający (2×25/30), jednostka odpowiedzialna, osoba kontaktowa, klasyfikacja, status dokumentu, nr strony, liczba stron, format. | ISO 7200:2004 tabl. 1–3 | https://cdn.standards.iteh.ai/samples/35446/d3b0887cb4fa47f49f8718807d3b8903/ISO-7200-2004.pdf | TAK-N | W indeksie zmian **należy unikać** liter I i O („should be avoided”, 5.1.4; weryfikacja 2026-09-25: było „nie służą”, co jest mocniejsze niż tekst normy). Pola dynamiczne (np. skala) mogą stać poza tabliczką. |
| R4-B09 | **Całkowita szerokość tabliczki 180 mm**, tak by mieściła się na A4 (margines lewy 20, prawy 10). Ta sama tabliczka dla wszystkich formatów. | ISO 7200:2004 rozdz. 6 | j.w. | TAK-N | ISO 9431:1990 podaje dla kolumny tekstowej „max 170 mm” (za ISO 7200:1984). Przyjmujemy 180 mm (pkt 3.1). |
| R4-B10 | Arkusz dzieli się na **pole rysunku** i **pole tekstu**. Pole tekstu zwykle przy **prawej krawędzi**, o szerokości tabliczki (**max 170 mm**, min **100 mm**), podzielone na kolumny. Gdy rysunek zajmuje całą szerokość, pole tekstu idzie do dolnej krawędzi. | ISO 9431:1990 3, 5.1 (PN-EN ISO 9431:2011) | https://cdn.standards.iteh.ai/samples/17133/4760842add8742d48c61396b73eb970e/ISO-9431-1990.pdf | TAK-N | — |
| R4-B11 | Pole tekstu zawiera: tabliczkę; **objaśnienia** (symbole, oznaczenia, skróty, **jednostki wymiarów**); **instrukcje** (materiały, wykonanie); **odniesienia** do innych rysunków; **rysunek lokalizacyjny** (widoczny po złożeniu: schemat sytuacji ze strzałką północy lub schemat rzutu/przekroju); **tabelę zmian** (oznaczenie, opis, data, podpis). | ISO 9431 5.2.1–5.2.6 | j.w. | TAK-N | Szerokość tabeli zmian = szerokość tabliczki, gdy stoi nad nią, albo ≥ 100 mm, gdy stoi obok. |
| R4-B12 | Rysunki układa się w **wierszach i kolumnach**. Rysunek główny w lewym górnym rogu. Uwzględnia się linie złożenia do A4. | ISO 9431 4 | j.w. | TAK-N | — |
| R4-B13 | Każdy rysunek określa swój cel w tytule lub tytule uzupełniającym (wg ISO 7200). Wymagana **legenda symboli** w polu tekstu (wg ISO 9431) albo odrębny rysunek-legenda z odwołaniem. Rysunek podaje **zamierzony format papieru**, a każdy widok **swoją skalę**. Rysunki opierają się na układzie współrzędnych z wyróżnionym punktem odniesienia terenu. | ISO 7519:2025 (3. wyd., 2025-02) 4.1.2–4.1.3 | https://cdn.standards.iteh.ai/samples/89718/3807035b2f954bc98668456e679dc0ce/ISO-7519-2025.pdf | TAK-N | Norma bez aktualnej wersji PN (pkt 2.1). Stosujemy jako dobrą praktykę spójną z § 9 rozp. *Weryfikacja 2026-09-25: było „ISO/FDIS 7519:2024 (= ISO 7519:2025)” z URL projektu FDIS. ISO 7519:2024 to odrębne 2. wydanie (iso.org/standard/83163), a FDIS z projektu 89718 dotyczy 3. wydania. Treść 4.1.2–4.1.3 potwierdzono w tekście ISO 7519:2025.* |
| R4-B14 | PN-B-01025:2004 rozdz. 2 „Ogólne zasady sporządzania rysunków” obejmuje: 2.1 formaty; 2.2 podział arkusza; 2.3 tabliczki tytułowe; 2.4 linie; 2.5 pismo; 2.6 podziałki; 2.7 kompletację; 2.8 zmiany i uzupełnienia. Powołuje PN-ISO 7200, PN-ISO 9431, PN-ISO 128-23, PN-80/N-01606 (pismo), PN-80/N-01612 (formaty), PN-86/N-01603 (składanie). Wszystkie te normy są dziś wycofane lub zastąpione. | PN-B-01025:2004 spis treści, powołania | [PKN] (karta normy) | TAK-K | Treści pkt 2.x nie widzieliśmy, więc szczegóły tabliczki wg PN-B-01025 są NIEZWERYFIKOWANE. Zastępujemy je ISO 7200/9431 + § 10 rozp. |

#### C. Linie

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-C01 | Szereg grubości linii d (współczynnik 1:√2): **0,13; 0,18; 0,25; 0,35; 0,5; 0,7; 1; 1,4; 2 mm**. Proporcja **bardzo gruba : gruba : cienka = 4:2:1**. Grubość stała na całej długości linii. | ISO 128-2:2022 5.1 (PN-EN ISO 128-2:2023-05) | https://cdn.standards.iteh.ai/samples/83355/10bb39d36fc34caeb80ecd25347ddb0c/ISO-128-2-2022.pdf | TAK-N | — |
| R4-C02 | Odchyłka grubości przy sprzęcie o stałej grubości: **≤ ±0,1d**. | ISO 128-2 5.2 | j.w. | TAK-N | — |
| R4-C03 | Długości elementów linii nieciągłych: kropka **≤ d**; przerwa **3d**; kreska krótka **6d**; kreska **12d**; kreska długa **≈24d**; odstęp (typ 03) **18d**. Przy zakończeniach półokrągłych długość całkowita = wartość + d. | ISO 128-2 5.3, tabl. 4 | j.w. | TAK-N | Parametry wzorów linii w PDF (dash array). |
| R4-C04 | Minimalny odstęp między liniami równoległymi: **0,7 mm**. | ISO 128-2 6.1 | j.w. | TAK-N | Dla silnika: warstwy cieńsze niż 0,7 mm × skala (1:100 → 70 mm, 1:50 → 35 mm) nie są rysowane osobnymi liniami. |
| R4-C05 | Linie nieciągłe (typy 02–06, 08–15) przecinają się **na kresce**, a typ 07 na kropce. | ISO 128-2 6.2.1 | j.w. | TAK-N | — |
| R4-C06 | Typy podstawowe: 01 ciągła; 02 kreskowa; 03 kreskowa z odstępem; 04 punktowa (kreska długa–kropka); 05 dwupunktowa; 06 trzypunktowa; 07 kropkowa; 08–15 kombinacje. Podtypy: .1 cienka, .2 gruba, .3 bardzo gruba. | ISO 128-2 tabl. 1–2 | j.w. | TAK-N | — |
| R4-C07 | Na rysunku budowlanym zwykle stosuje się **trzy grubości: cienką, grubą, bardzo grubą (1:2:4)**. Specjalna grubość dla symboli graficznych i ich opisów leży między cienką a grubą. **Grupy linii (cienka/gruba/b. gruba/symbole) [mm]:** 0,25: 0,13/0,25/0,5/0,18; **0,35: 0,18/0,35/0,7/0,25**; **0,5: 0,25/0,5/1/0,35**; **0,7: 0,35/0,7/1,4/0,5**; 1: 0,5/1/2/0,7. Grubość dobiera się do rodzaju, wielkości i skali rysunku oraz do wymagań reprodukcji. | ISO 128-23:1999 rozdz. 5, tabl. 2 | https://cdn.standards.iteh.ai/samples/22292/a9f6396b7eb94397aa5e41513ebf09b1/ISO-128-23-1999.pdf | TAK-N (norma wycofana) | Treść przeniesiono do ISO 128-2 zał. B (normatywny). **NIEZWERYFIKOWANE**, czy tabela zał. B jest identyczna. Tabelę powiela też [PCEZ] (NIE). |
| R4-C08 | **Zastosowania linii w budownictwie** (ISO 128-23 tabl. 1), wyciąg:<br>• **01.1 ciągła cienka:** granice materiałów; kreskowanie; przekątne otworów, wnęk i nisz; strzałki schodów, pochylni i spadków; siatka modularna I stopnia; krótkie osie; linie pomocnicze wymiarowe; linie wymiarowe z ogranicznikami; linie odniesienia; istniejące warstwice; widoczne zarysy w widoku; uproszczone drzwi, okna, schody i wyposażenie; obramowanie szczegółów; zygzak na granicy urwania.<br>• **01.2 ciągła gruba:** zarysy części w przekroju **gdy stosuje się kreskowanie**; granice materiałów (alternat.); zarysy w widoku (alternat.); uproszczone drzwi i okna (alternat.); siatka modularna II stopnia; **strzałki oznaczenia widoków i przekrojów**; projektowane warstwice.<br>• **01.3 ciągła bardzo gruba:** zarysy części w przekroju **bez kreskowania**; **pręty zbrojeniowe**; linie o szczególnym znaczeniu.<br>• **02.1 kreskowa cienka:** istniejące warstwice (alternat.); podział rabat i trawników; zarysy niewidoczne.<br>• 02.2 kreskowa gruba: zarysy niewidoczne.<br>• **02.3 kreskowa b. gruba:** pręty w warstwie dolnej lub dalszej, gdy obie warstwy są na jednym rysunku.<br>• **04.1 punktowa cienka:** **płaszczyzny przekroju (na końcach i załamaniach 04.2)**; osie; osie symetrii (na końcach dwie krótkie równoległe kreski); obramowanie szczegółów powiększonych; linie odniesienia.<br>• **04.2 punktowa gruba:** końce i załamania linii przekroju; **zarysy części widocznych przed płaszczyzną przekroju**.<br>• 04.3 punktowa b. gruba: linie tyczenia; granice kontraktów, etapów i stref.<br>• **05.1 dwupunktowa cienka:** położenia skrajne części ruchomych; linie środków ciężkości; zarysy części przyległych.<br>• 05.2 dwupunktowa gruba: zarysy części niewidocznych **przed** płaszczyzną przekroju.<br>• 05.3: cięgna sprężające.<br>• **07.1 kropkowa cienka:** zarysy części **nieobjętych projektem**. | ISO 128-23:1999 tabl. 1 | j.w. | TAK-N (norma wycofana) | Mapowanie typów linii w silniku (pkt 3.2). [PCEZ] podaje skrót tej tabeli wg PN-ISO 128-23:2002. |
| R4-C09 | Na rysunkach zestawieniowych: części w przekroju rysuje się grubszą linią niż części w widoku. Stosunek przekrój:widok = 2:1. Na jednym rysunku 2–3 grubości. Stropy pochyłe i spadki: linia cienka + strzałka w kierunku spadku + nachylenie. | ISO 7519:1991 4.1–4.8 | https://cdn.standards.iteh.ai/samples/14288/eddd4c11ea654c9cbdf5dcd53f717597/ISO-7519-1991.pdf | TAK-N (wyd. historyczne) | — |
| R4-C10 | Wszystkie rysunki na jednym arkuszu wykonane w tej samej skali mają linie z **tej samej grupy grubości**. | [PCEZ] s. 32 (wg PN-ISO 128-23) | [PCEZ] | NIE | Zasada spójności grup. |

#### D. Pismo

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-D01 | Wysokości nominalne pisma h (wysokość wielkich liter i cyfr): **1,8; 2,5; 3,5; 5; 7; 10; 14; 20 mm** (szereg √2). Ta sama grubość linii dla małych i wielkich liter. | ISO 3098-1:2015 5.1, 5.3 (PN-EN ISO 3098-1:2015-06) | https://cdn.standards.iteh.ai/samples/65679/d6c3a5303d6a48cba4486718d1947b0c/ISO-3098-1-2015.pdf | TAK-N | — |
| R4-D02 | Odstęp między znakami = **2× grubość linii pisma** (dla par typu LA, TV można 1×). | ISO 3098-1 4.2 | j.w. | TAK-N | — |
| R4-D03 | Pismo proste albo pochyłe pod **75°** do poziomu. Rodzaje: A, B (**B proste zalecane**), w CAD **CA i CB (CB proste zalecane)**. W CAD obowiązują te same wymiary co w innych technikach. | ISO 3098-1 5.2, 5.4, 5.5 | j.w. | TAK-N | — |
| R4-D04 | Pismo B: grubość linii **d = h/10**, wysokość małych liter **7/10 h**. Pismo A: d = h/14, małe litery 10/14 h. | [PCEZ] s. 28–29 (tabl. 5 wg PN-EN ISO 3098-0) | [PCEZ] | NIE | Tablice wymiarowe ISO 3098-1 nie są w podglądzie. |
| R4-D05 | Polskie znaki diakrytyczne: PN-EN ISO 3098-4:2002. Pismo CAD: PN-EN ISO 3098-5:2002. | PKN (karty norm) | [PKN] | TAK-K | Font musi zawierać ą ć ę ł ń ó ś ź ż (Ą…Ż). |
| R4-D06 | Przy edytorach komputerowych „zaleca się pismo o kroju **ARIAL CE i szerokości 0,8** (według PN-B-01025:2004)”. | [PCEZ] s. 28 | [PCEZ] | NIE | **NIEZWERYFIKOWANE** w tekście PN-B-01025 (pkt 2.5 istnieje wg spisu treści). |
| R4-D07 | Litery oznaczenia przekroju mają wysokość ok. **1,41×** pisma zasadniczego (np. 3,5 → 5 mm). | [AGH-P] (za PN-EN ISO 128-3) | [AGH-P] | NIE | ISO 128-3:2022 odsyła do zał. A (brak w podglądzie). |

#### E. Podziałki

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-E01 | Podziałki zalecane. Zwiększające: 50:1, 20:1, 10:1, 5:1, 2:1. Naturalna: 1:1. **Zmniejszające: 1:2, 1:5, 1:10, 1:20, 1:50, 1:100, 1:200, 1:500, 1:1000, 1:2000, 1:5000, 1:10 000.** Wyjątkowo dopuszcza się podziałki pośrednie. | ISO 5455:1979 5.1 (PN-EN ISO 5455:1998) | https://cdn.standards.iteh.ai/samples/11500/dc0452907ab547f5aee36c22006aa275/ISO-5455-1979.pdf | TAK-N | — |
| R4-E02 | Oznaczenie: „PODZIAŁKA 1:X” lub samo „1:X”, jeśli nie ma ryzyka pomyłki. **Podziałka główna w tabliczce**, inne przy oznaczeniu widoku lub szczegółu. | ISO 5455 3, 4.1–4.2 | j.w. | TAK-N | Praktyka PL: „SKALA 1:100”. |
| R4-E03 | Rodzaje oznaczeń wg skali (PN-B-01025 1.3): **umowne** przy 1:200 i mniejszych (koncepcje); **uproszczone** przy 1:50–1:200 (PAB i wykonawcze); **dokładne** przy skalach większych od 1:50 (szczegóły). | PN-B-01025:2004 pkt 1.3 | [AGH-P] s. 30; [PCEZ] s. 25 | NIE | Dwa niezależne źródła wtórne są zgodne. |
| R4-E04 | Oznaczenia graficzne materiałów stosuje się na przekrojach i rzutach w skali **1:100 i większej**. Kreskowanie rysuje się linią cienką. | [AGH-P] s. 25 (wg PN-B-01030:2000) | [AGH-P] | NIE | — |

#### F. Wymiarowanie (PN-B-01029:2000 i zasady ogólne)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-F01 | Zakres PN-B-01029: ogólne zasady wymiarowania; wymiarowanie elementów konstrukcyjnych, otworów okiennych i drzwiowych, kanałów na przekrojach poziomych, schodów i pochylni oraz elementów powtarzających się. Norma ma 8 stron i jest dostosowana do PN-ISO 129. | PKN (karta normy) | [PKN] | TAK-K | Normę powołuje zał. 2 rozp. |
| R4-F02 | Linie wymiarowe i pomocnicze: **cienka ciągła**. **Ograniczniki: krótkie ukośne kreski pod 45°** (rysunek budowlany), tej samej grubości co linia wymiarowa. Bazę wymiarową można oznaczyć **kropką**. | [AGH-W]; [PWR9] s. 2–4; [PCEZ] s. 33 | [AGH-W] | NIE | Trzy niezależne źródła wtórne. |
| R4-F03 | Przy ukośnych kreskach **linia wymiarowa wychodzi poza linie pomocnicze**, a linie pomocnicze **wychodzą poza linię wymiarową** (ok. 1–2 mm). W rysunku budowlanym zaleca się **nie doprowadzać linii pomocniczych do obrysu** i nadać im **jednakową długość**. | [AGH-W]; [PWR9] s. 6 | j.w. | NIE | — |
| R4-F04 | Kreska ogranicznika ma dł. **ok. 3,5 mm** (PWr). Pierwsza linia wymiarowa **ok. 10 mm** od obrysu, następne co **7–8 mm** (min. 7 mm). Liczby **ok. 0,5–1,5 mm nad linią**, możliwie w środku. Wysokość cyfr **≥ 2 mm** (PCEZ), dla wymiarów nominalnych **≥ 3,5 mm** (PWr, rysunek ogólny). | [PCEZ] s. 32; wykład PWr „wymiarowanie” | [PCEZ]; https://wis.pwr.edu.pl/download/SsJWU1BTBGWycqYDgneXckHEsnIA0eLiwwLTpxTnYIKBQwYz8ILEYVSBJ1OxUXNGgoZn8MCxt7EnVnFSV3,QHHEcPNw4PJlwjQwgiBQkHD14OGDI0BhBURGlLGlAbEDEITQIgGVQ3TD8GHS1eSBxJAlpSfg/rystech_z_geom_wykr-_cw6_7.pdf | NIE | Wartości w mm na papierze. PN-B-01027 dla PZT: min. **2,5 mm** (R4-M10). |
| R4-F05 | Liczby wymiarowe czyta się **od dołu lub od prawej strony** arkusza. Nie przecina się ich liniami rysunku. Nie powtarza się wymiarów. W ciągach bliżej obiektu stoją wymiary mniejsze. | [AGH-W]; [PWR9] s. 3; [PCEZ] s. 33 | j.w. | NIE | — |
| R4-F06 | **Jednostki:** na jednym rysunku jedna jednostka, bez symbolu przy liczbach. Jednostkę dominującą (albo różne jednostki) podaje się w uwadze lub objaśnieniu. W rysunku architektoniczno-budowlanym praktyką jest **centymetr**, w konstrukcjach metalowych mm, na PZT metr. | [AGH-W] (cytat norm ISO 129 i PN-B-01029 + praktyka) | [AGH-W] | NIE | Pole „Wymiary w cm, rzędne w m” w objaśnieniach. |
| R4-F07 | **Ułamki centymetra** (np. 87,5 cm) zapisuje się w praktyce PL **indeksem górnym**: 87⁵; dla metrów 1.87⁵. | CADprofi, pomoc „Wymiarowanie architektoniczne” (praktyka programów CAD) | https://cadprofi.com/online-help/pl/architectural_dim.htm | NIE | **NIEZWERYFIKOWANE** jako wymóg PN-B-01029. Traktujemy jako konwencję i objaśniamy w legendzie. |
| R4-F08 | **Kolejność zewnętrznych ciągów wymiarowych, od obrysu:** a) wymiary szczegółowe (otwory i filary, „linia murarska”); b) wymiary części lub rozstawu osi (osie otworów, ściany wewnętrzne); c) wymiary modularne lub rozstaw osi konstrukcyjnych, jeśli występują; d) wymiary całego obiektu lub jego części. Ciągi umieszcza się wzdłuż **każdej ściany zewnętrznej**. Liczba ciągów wynika z potrzeb: przy ścianie bez okien pomija się ciągi otworów. AGH podaje wariant 5-ciągowy: 1 otwory i filary; 2 osie otworów; 3 osie konstrukcyjne; 4 grubości ścian wewn. + szerokości pomieszczeń; 5 całość. | PN-B-01029 (wg [PWR9] s. 4–8; [PCEZ] s. 32–33; [AGH-W]) | [PWR9] | NIE | Trzy źródła wtórne są zgodne co do kolejności a–d. |
| R4-F09 | **Ciągi wewnętrzne** podają to, czego brak w zewnętrznych: otwory w stropach; ściany wewnętrzne (grubości i szerokości pomieszczeń); otwory w ścianach wewnętrznych; kanały i wnęki. Położenie wymiaruje się od **najbliższego elementu konstrukcyjnego**. Ciągów wewnętrznych nie trzeba zamykać. | [AGH-W] | [AGH-W] | NIE | — |
| R4-F10 | **Otwory okienne i drzwiowe:** wymiar na osi otworu w postaci **ułamka: licznik = szerokość, mianownik = wysokość**. Wysokość parapetu (ściany podokiennej) podaje się **w nawiasie przed wysokością otworu**, jeśli nie ma jej na przekroju. Liczy się ją **od wierzchu podłogi wykończonej do dolnej krawędzi ościeża lub wierzchu parapetu**. Przy zestawieniu stolarki zamiast wymiarów można dać **symbol** okna lub drzwi. Położenie otworu: odległość krawędzi (lub osi) od najbliższego elementu konstrukcyjnego lub sąsiedniego otworu. | PN-B-01029 (wg [PWR9] s. 9–10; [AGH-W]) | [PWR9]; [AGH-W] | NIE | Zgodne w obu źródłach. |
| R4-F11 | **Kanały:** prostokątne wymiaruje się ułamkiem na osi (licznik: wymiar prostopadły do lica ściany, mianownik: wzdłuż lica). Okrągłe: „⌀” + średnica nad osią. Kanałów typowych (140×140 mm, ⌀150) nie wymiaruje się. | PN-B-01029 (wg [AGH-W]; [PWR9] s. 13) | j.w. | NIE | — |
| R4-F12 | **Elementy powtarzalne:** wymiaruje się szczegółowo jeden element, a pozostałe oznacza symbolem literowym. Odnośnik elementów powtarzalnych to linia wymiarowa między osiami skrajnych elementów z symbolem w kółku i „× liczba”. | PN-B-01029, PN-B-01025 3.9 (wg [PWR9] s. 14, 18) | [PWR9] | NIE | — |
| R4-F13 | **Schody:** opis „**liczba × wysokość × szerokość (posunięcie)**”, np. „11 × 160 × 300” (PWr). Wg AGH nad strzałką biegu liczba stopni × wysokość, pod strzałką szerokość stopnia. | PN-B-01029/PN-B-01025 (wg [PWR9] s. 35; [AGH-P] s. 59–65) | j.w. | NIE | Jednostka w przykładzie PWr to mm. Dla rysunków w cm: „17×17,5×28” (**NIEZWERYFIKOWANE**). |
| R4-F14 | Odchyłki graniczne zapisuje się np. „890 ± 12”, „890 +5/−19”, a położenie „+12,300 ± 0,010”. | PN-EN ISO 6284:2001 (wg [PCEZ] s. 33) | [PCEZ] | NIE | W PB rzadko potrzebne. |
| R4-F15 | Wymagane w WT wymiary rozumie się **z uwzględnieniem wykończenia** powierzchni elementów budynku, a szerokość drzwi jako **wymiar w świetle ościeżnicy** (§ 9 ust. 1). Grubość otwartego skrzydła nie może pomniejszać szerokości w świetle ościeżnicy (§ 9 ust. 2). **Odległości** budynku od innych budynków, urządzeń i granicy działki mierzy się **w poziomie, w miejscu najmniejszego oddalenia** (§ 9 ust. 3), co dotyczy wymiarowania na PZT. | WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) § 9 ust. 1–3 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | TAK-A (weryfikacja 2026-09-25; wcześniej cytat wtórny IARP) | **Status WT do potwierdzenia przez R3.** Silnik liczy wymiary „surowe” (otwory w murze) i „wykończone” (sprawdzenia WT, powierzchnie). |

#### G. Rzędne wysokościowe i poziomy

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-G01 | Na rzutach i przekrojach oznacza się poziomy. Rzędną podaje się **w metrach z dokładnością do trzech miejsc po przecinku** (w praktyce często dwóch). Poziom zerowy to zwykle podłoga pierwszej kondygnacji nadziemnej. | PN-B-01025:2004 pkt 3.5 (wg [AGH-P] s. 66; [PWR9] s. 46) | [AGH-P]; [PWR9] | NIE | Dwa źródła są zgodne co do 3 miejsc. Rekomendacja w pkt 3.6. |
| R4-G02 | **Poziom zerowy na przekroju:** grot zamknięty o kącie **90°**, **w połowie zaczerniony**, ostrzem do linii poziomu. Grot łączy krótka pionowa kreska z poziomą linią odniesienia; **nad nią „±0,000”**, **pod nią rzędna bezwzględna (m n.p.m.)** albo zapis w linii „±0,000 = 234,50”. Linia cienka ciągła. | [AGH-P] s. 66–67 (wg PN-B-01025) | [AGH-P] | NIE | Geometrię odczytano z rysunku w źródle. |
| R4-G03 | **Inne poziomy na przekrojach i elewacjach:** grot **otwarty 90°** do poziomu, kreska pionowa, linia odniesienia i wartość nad nią (np. „+3,150”). | [AGH-P] s. 68 | [AGH-P] | NIE | — |
| R4-G04 | **Poziomy na rzutach:** znak „**×**” w punkcie i linia odniesienia do poziomej kreski z wartością nad nią (np. „+ 14,400”). Gdy punkt wyznacza przecięcie dwóch linii zarysu, „×” zastępuje się **kółkiem**. Linia cienka. | [AGH-P] s. 69 | [AGH-P] | NIE | — |
| R4-G05 | **Spadki** powierzchni (dachy, tarasy, parkingi): strzałka z grotem **w kierunku spadku**, obok nachylenie w **% lub ‰**. **Wzniesienia** (schody, pochylnie): strzałka w kierunku wznoszenia z **kółkiem na początku**, nachylenie przy strzałce. | PN-B-01025 3.6 (wg [PWR9] s. 24–25; [AGH-P] s. 58, 70) | [PWR9] | NIE | Zgodne z ISO 7519:1991 4.10 (R4-H06). |
| R4-G06 | Na PZT budynek opisuje się rzędną podłogi parteru „**0,00=267,50**” z trójkątem, a obok innych punktów podaje się rzędne bezwzględne. Liczbę kondygnacji nadziemnych zapisuje się **cyfrą rzymską w kółku** (np. „IV+P”, gdzie P = poddasze użytkowe). Litery 0,25 mm, **min. wysokość 2,5 mm**. | PN-B-01027:2002 poz. 1.8 (wg [AGH-Z] s. 9) | [AGH-Z] | NIE | Przykład w normie ma 2 miejsca po przecinku. |

#### H. Oznaczenia graficzne arch.-bud. (PN-B-01025:2004, ISO 7519, ISO 128-3)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-H01 | Struktura PN-B-01025:2004:<br>• 3.1 kierunek północny; **3.2 zalecana orientacja budynku ze względu na nasłonecznienie**; 3.3 przekroje; 3.4 numeracja kondygnacji i pomieszczeń; 3.5 poziomy i rzędne; 3.6 wzniesienia i spadki; 3.7 wejścia; 3.8 zapis wymiarów liniowych i kątowych; 3.9 odnośniki;<br>• 4.1 skarpy; 4.2 fundamenty; 4.3 mury i ściany; 4.4 przegrody poziome; 4.5 podciągi, żebra, nadproża; 4.6 otwory; 4.7 komunikacja i transport pionowy; 4.8 dylatacje; 4.9 izolacje;<br>• 5 urządzenia instalacji budowlanych; 6 meble wbudowane; 7 wyposażenie ruchome; zał. A (przykłady). | PN-B-01025:2004 spis treści | [PKN] (karta) | TAK-K | Zakres: „jednobarwne oznaczenia graficzne, umowne i uproszczone”. Kolor nie ma znaczenia normowego. |
| R4-H02 | **Kierunek północy** oznacza się na arkuszu z rzutem parteru. W **projektach powtarzalnych** (realizowanych na różnych działkach) oznacza się **dopuszczalne odchylenie osi budynku od północy** ze względu na nasłonecznienie pomieszczeń. | PN-B-01025 3.1–3.2 (wg [AGH-P] s. 31) | [AGH-P] | NIE | **Istotne dla oferty „projekt typowy”** (strona WWW). |
| R4-H03 | **Oznaczenie przekroju** na rzutach (najlepiej na wszystkich): **cienka linia punktowa, pogrubiona na załamaniach i końcach**, strzałki kierunku patrzenia i przy nich **wielkie litery** (rzadziej cyfry rzymskie). Przekrój budowlany jest zawsze pionowy. | PN-B-01025 3.3 (wg [AGH-P] s. 32) | [AGH-P] | NIE | Zgodne z ISO 128-23 04.1.1 i 04.2.1 (R4-C08). |
| R4-H04 | Każda płaszczyzna przekroju ma **dwie takie same wielkie litery** przy strzałkach, czytane od dołu rysunku. Oznaczenie „A-A” stoi **bezpośrednio nad** rysunkiem przekroju. Strzałki mają kąt 30° lub 90° (zał. A normy). | ISO 128-3:2022 6.2.2–6.2.3 | https://cdn.standards.iteh.ai/samples/83356/d1819f3aabb74441890b2302a24a4cb6/ISO-128-3-2022.pdf | TAK-N | Dla budownictwa norma odsyła do zał. F (brak w podglądzie). |
| R4-H05 | Rzut kondygnacji to przekrój poziomy **ok. 1 m nad podłogą**, z odchyleniami dla istotnych elementów (np. kominów). Elementy nad płaszczyzną (belki, nadproża, podciągi) rysuje się odpowiednią linią. | PN-B-01025 (wg [AGH-P] s. 24) | [AGH-P] | NIE | PZT: przekrój poziomy obiektu **1,0 m nad terenem** (R4-M02). |
| R4-H06 | **Schody i pochylnie na rzucie:** linia cienka. **Strzałka w osi biegu: otwarte kółko przy pierwszym stopniu, otwarty grot przy ostatnim** (kierunek wznoszenia). Przecięcie biegu płaszczyzną rzutu to **ukośna cienka linia z zygzakiem** (zygzak można pominąć). Można numerować stopnie od „1” u dołu i podać rzędne spoczników. Pochylnia: analogicznie (kółko na dole, grot u góry) + nachylenie. | ISO 7519:1991 4.9–4.10 | [7519:1991] https://cdn.standards.iteh.ai/samples/14288/eddd4c11ea654c9cbdf5dcd53f717597/ISO-7519-1991.pdf | TAK-N (wyd. hist.) | To samo w PN-B-01025 (wg [AGH-P] s. 59–65). |
| R4-H07 | **Drzwi:** otwarcie skrzydła rozwieranego rysuje się **pod 30° bez łuku** albo **pod 90° z łukiem**. W skalach ≥ 1:50 pokazuje się rodzaj, osadzenie i próg. PN-B-01025: w oznaczeniach uproszczonych wszystkie drzwi są otwarte, a skrzydło rozwierane, wahadłowe i składane ma **pełny zakres ruchu z łukiem**. W oznaczeniach umownych (1:200) skrzydło stoi pod **30° bez łuku**. Osobne symbole mają drzwi przesuwne (także chowane w ścianie), harmonijkowe, fałdowe, obrotowe, podnoszone (bramy) i balkonowe. | ISO 7519:1991 5.1–5.4; PN-B-01025 (wg [AGH-P] s. 47–53; [PCEZ] tabl. 3) | [7519:1991]; [AGH-P] | TAK-N / NIE | — |
| R4-H08 | **Okna:** linia cienka lub gruba. Szyby można zaznaczyć linią cienką. Warianty uproszczone: bez węgarka i parapetu; z węgarkiem i parapetem; z parapetem i wnęką podokienną. Przekrój wg rzutu. | ISO 7519:1991 5.1, 5.3; PN-B-01025 (wg [AGH-P] s. 44–46; [PCEZ] tabl. 4) | j.w. | TAK-N / NIE | — |
| R4-H09 | **Otwory w ścianie lub stropie:** **dwie przekątne** linią cienką. **Wnęki:** **jedna przekątna** (obie można pominąć, gdy znaczenie jest jasne). **Sufit podwieszany:** na rzucie przekątna **linią dwupunktową cienką** + rzędna spodu. Wg PN-B-01025 (AGH) sufity podwieszane to **gruba dwupunktowa**. | ISO 7519:1991 6.1–6.2; [AGH-P] | [7519:1991]; [AGH-P] | TAK-N / NIE | Grubości w obu źródłach się różnią. Przyjmujemy cienką (ISO), bo i tak jest objaśniona w legendzie. |
| R4-H10 | **Belki, podciągi, nadproża** wyższe od stropu (skale 1:50–1:200): **cienka punktowa**, gdy leżą nad płaszczyzną rzutu (w praktyce cienka kreskowa), i **cienka kreskowa**, gdy leżą pod nią. | PN-B-01025 4.5 (wg [AGH-P] s. 39; [PWR9] s. 31) | [AGH-P]; [PWR9] | NIE | Dotyczy wsporników, podciągów i nadproży w LAMELI. |
| R4-H11 | **Kanały** (1:50–1:200): **wentylacyjny = przekątna** otworu; **spalinowy = przekątna z zaczernioną połową** pod przekątną; **dymowy = całość zaczerniona**. Wloty to linie od kanału prostopadłe do lica, oznaczane na kondygnacji wlotu. Wszystko linią cienką. | PN-B-01025 (wg [AGH-P] s. 54) | [AGH-P] | NIE | LAMELA: kanały wentylacyjne lub pion rekuperacji. Budynek bez kominów dymowych (all-electric, brief). |
| R4-H12 | **Wejścia:** strzałka **zaczerniona** dla wejść na poziomie zerowym lub powyżej, **niewypełniona** dla wejść poniżej poziomu zerowego. | PN-B-01025 3.7 (wg [AGH-P] s. 33) | [AGH-P] | NIE | Na PZT: trójkąt zaczerniony, bok 4 mm (R4-M05). |
| R4-H13 | **Skarpy:** na rzucie kreski od korony lub krawędzi w kierunku spadku. Nachylenie na przekroju jako **1:x** lub %/‰. | PN-B-01025 4.1 (wg [AGH-P] s. 33; [PWR9] s. 26) | j.w. | NIE | — |
| R4-H14 | **Odnośniki** (linia cienka):<br>• **linia wskazująca** kończy się **grotem** na zarysie lub krawędzi, **kropką** (Ø ok. **5× grubość linii cienkiej**) wewnątrz pola, a na innej linii bez zakończenia;<br>• **odnośnik skrótowy**: mała litera lub cyfra nad linią odniesienia, wyjaśniona w legendzie;<br>• **odnośnik szczegółu**: wielka litera + okrąg obwodzący;<br>• **odnośnik elementu wielowarstwowego** („drabinka”): warstwy poziome od góry, pionowe od lewej;<br>• **odnośnik elementów powtarzalnych**: symbol w kółku. | PN-B-01025 3.9 (wg [AGH-P] s. 72–84; [PWR9] s. 15–18) | [AGH-P]; [PWR9] | NIE | Opisy przegród ze słownika `przegrody` w modelu. |
| R4-H15 | **Osie projektowe (konstrukcyjne):** **cyfry i wielkie litery w okręgach** na końcach osi, poza wymiarowaniem. Te same oznaczenia na wszystkich rzutach (od fundamentów) i przekrojach. | [AGH-P] s. 85–86 (wg PN-B-01025) | [AGH-P] | NIE | Średnica okręgu: **NIEZWERYFIKOWANE** (przyjmujemy 10 mm, pkt 3.7). |
| R4-H16 | **Izolacje** (przeciwwilgociowe, termiczne, akustyczne) pokazuje się na przekrojach 1:50–1:200 i opisuje warstwy odnośnikiem wielowarstwowym. **Dylatacje:** jednakowy symbol na rzutach, przekrojach i elewacjach. | PN-B-01025 4.8–4.9 (wg [AGH-P] s. 57; [PWR9] s. 40) | j.w. | NIE | — |
| R4-H17 | Urządzenia instalacji budowlanych (zlew, umywalka, wanna, miska ustępowa…) na rzutach arch. mają symbole uproszczone PN-B-01025 rozdz. 5. Meble wbudowane: rozdz. 6. Wyposażenie ruchome: rozdz. 7. | PN-B-01025 spis treści; [PCEZ] tabl. 4; [PWR9] s. 41 | [PKN]; [PCEZ] | TAK-K / NIE | Kształty z reprodukcji wtórnych. Wymiary wg wyrobów, rysowane w skali. |
| R4-H18 | **Plan terenu (site plan):** północ **pionowo**. Budynek to **obrys (footprint) linią 01.3**. Granica terenu: **04.3**. Otoczenie istniejące: **01.2**. Pokazuje się położenie geoprzestrzenne. **Rysunek zagospodarowania (site layout):** północ w I ćwiartce. Obrys na poziomie terenu: **01.3**. **Części nadziemne wystające (stropy, dachy, balkony): 04.2.** Części podziemne: **02.2**. Podaje się punkt odniesienia (datum) ze współrzędnymi. | ISO 7519:2025 4.4–4.5, rys. 1–2 | https://cdn.standards.iteh.ai/samples/89718/3807035b2f954bc98668456e679dc0ce/ISO-7519-2025.pdf | TAK-N | Spójne z PN-B-01027 poz. 1.6 (R4-M04). Norma bez wersji PN (pkt 4). *Weryfikacja 2026-09-25: treść potwierdzona w wydaniu 2025. Wg przedmowy wyd. 2025 jedyna zmiana merytoryczna względem ISO 7519:2024 dotyczy klucza 2 na rys. 1 (granica terenu: 04.2 → **04.3**) oraz przecinka dziesiętnego na rysunkach. W kluczu rys. 1 PN-EN ISO 7519:2024-09 (wycofanej) był więc typ 04.2. Stosujemy **04.3**.* |

#### I. Oznaczenia materiałów w przekroju (PN-B-01030:2000, ISO 128-3)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-I01 | PN-B-01030:2000 podaje oznaczenia **15 materiałów**, „które nie były uwzględnione w normie PN-ISO 4069”. Ma 3 strony. | PKN (karta normy) | [PKN] | TAK-K | PN-ISO 4069 zastąpiła PN-ISO 128-50, a tę PN-EN ISO 128-3. |
| R4-I02 | **Wzory 15 materiałów** (opis geometrii odczytany z dwóch niezależnych reprodukcji tablicy normy):<br>1) **powierzchnia gruntu (przekrój):** gruba linia albo gruba linia z krótkimi ukośnymi kreskami pod nią, na przemian „/” i „\”;<br>2) **podsypka, tynk, zaprawa:** nieregularne **kropki**;<br>3) **beton niezbrojony i kamień:** kreskowanie **45° liniami przerywanymi** (kreski przesunięte w kolejnych liniach);<br>4) **żelbet:** kreskowanie **45° na przemian linią ciągłą i przerywaną**, gęstsze niż w 3;<br>5) **beton lekki:** jak 3 + **grupy małych kółek** (kruszywo);<br>6) **beton lekki zbrojony:** jak 4 + grupy kółek;<br>7) **cegły i pustaki** (mur ceramiczny): kreskowanie **45° liniami ciągłymi**;<br>8) **drewno:** a) przekrój poprzeczny: kwadrat z przekątnymi i łukami słojów albo koncentryczne słoje; b) wzdłuż włókien: falujące linie słojów;<br>9) **sklejka:** gęste linie równoległe do długości;<br>10) **płyty drewnopochodne:** dwie linie brzegowe z poprzecznymi kreskami („drabinka”);<br>11) **metal:** przekrój cienki **zaczerniony**;<br>12) **izolacja termiczna i akustyczna:** pas z **linią falistą meandrową** („UUU”) **albo zygzakiem** („VVV”) między liniami brzegowymi;<br>13) **izolacja wodochronna:** gruby pas **czarny z białymi prostokątami** na przemian;<br>14) **szkło i materiały przezroczyste:** wąski pas z **grupami 3 krótkich ukośnych kresek**;<br>15) **tworzywa sztuczne:** bardzo gęste kreskowanie 45° (prawie ciemne pole). | PN-B-01030:2000 (wg [AGH-P] s. 25–28 i [PCEZ] tabl. 2, za Wojciechowski 1999, s. 110) | [AGH-P]; [PCEZ] | NIE | Kąty i rodzaje linii są zgodne w obu reprodukcjach. **Odstępy w mm norma ma tylko na rysunku, więc są NIEZWERYFIKOWANE** (przyjęcia w pkt 3.8). |
| R4-I03 | Norma **nie rozróżnia** osobno: silikatów, betonu komórkowego, izolacji miękkiej i twardej, paroizolacji, gruntu nasypowego, piasku i żwiru. | ta sama tablica | j.w. | NIE | Muszą być zdefiniowane w **legendzie** (rozp. § 9 ust. 1). Propozycje w pkt 3.8. |
| R4-I04 | Kreskowanie: linie **cienkie, równoległe, 45°** do głównych zarysów lub osi. **Stałe odstępy, proporcjonalne do wielkości pola**. Przy brzegach zbliżonych do 45° stosuje się **30° lub 60°**. **Sąsiednie przekroje** kreskuje się w **różnych kierunkach** z tą samą podziałką. Przy 3 i więcej elementach różnicuje się kierunek, podziałkę lub przesunięcie. **Duże pola** kreskuje się tylko przy brzegach. **Wąskie przekroje zaczernia się**, a między stykającymi się zaczernionymi przekrojami zostawia się prześwit **≥ 0,7 mm**. | PN-EN ISO 128-3 rozdz. 7 (wg [AGH-P] s. 18–20); ISO 128-2 6.1 | [AGH-P]; ISO 128-2 (URL w R4-C01) | NIE / TAK-N (0,7 mm) | Tytuły 7.2–7.7 ISO 128-3:2022 (kreskowanie, cieniowanie, zarysy b. grube, cienkie przekroje, materiały) potwierdza spis treści (TAK-N). |
| R4-I05 | Wzorów materiałów (np. marmur, parkiet) normalnie się nie pokazuje. Jeśli trzeba, pokazuje się je na osobnych rysunkach. Części w przekroju można odróżnić grubością linii, kreskowaniem lub cieniowaniem. | ISO 7519:1991 4.6 | [7519:1991] | TAK-N | — |

#### J. Oznaczenia budynków, kondygnacji, pomieszczeń i elementów (PN-EN ISO 4157, PN-B-01025 3.4)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-J01 | **Kondygnacje (storeys)** numeruje się kolejno **od dołu do góry, od 1** na najniższym poziomie użytkowym. **0** oznacza przestrzeń tuż pod nim. Klatki schodowe mają numer kondygnacji, na której są. Granicą kondygnacji jest wierzch konstrukcji stropu. | ISO 4157-1:1998 7.2 (PN-EN ISO 4157-1:2001) | https://cdn.standards.iteh.ai/samples/26189/0ee2760f255344578079c1b0fd8f9a3e/ISO-4157-1-1998.pdf | TAK-N | LAMELA (bez piwnicy): parter = 1, I p. = 2, II p. = 3. |
| R4-J02 | **Piętra (floors)** numeruje się wg praktyki krajowej (7.4.1). Numery pomieszczeń opierają się na numeracji pięter wg ISO 4157-2 (7.4.2). | ISO 4157-1 7.4 | j.w. | TAK-N | Praktykę krajową określa PN-B-01025 3.4 (R4-J03). |
| R4-J03 | PN-B-01025: kondygnacje numeruje się **rosnąco od poziomu terenu** (kondygnacja przy terenie = **1**) w górę i w dół. Numery podziemnych mają „**–**”. **Numer pomieszczenia = numer kondygnacji + dwie lub trzy cyfry.** Numeruje się **zgodnie z ruchem wskazówek zegara, od pomieszczenia najbliższego wejścia głównego**. | PN-B-01025 3.4 (wg [AGH-P] s. 71; [PWR9] s. 45) | [AGH-P]; [PWR9] | NIE | **Kolizja ze schematem modelu** („0.01” dla parteru). Rekomendacja w pkt 3.9. *Weryfikacja 2026-09-25: AGH s. 72 i 75 (ta sama treść, nr slajdów o 1 wyższe) potwierdza. Uwaga: ten sam wykład (s. 76) podaje też **alternatywę opartą na numerach pięter** (parter 01–99 lub G01–G99, I piętro 101–199), zgodną z ISO 4157-1 7.4.2 (R4-J02).* |
| R4-J04 | Numer pomieszczenia: najlepiej **dwucyfrowy poprzedzony numerem piętra** (piętro 1: 101–199…). **Brak numerów „zerowych”** (np. 300 = otoczenie zewnętrzne kondygnacji). Numerów **czterocyfrowych nie rozdziela się** spacją ani kropką. Parter, antresola i piwnica mogą mieć G01, M02, B03. Numeruje się **zgodnie z ruchem wskazówek zegara od wejścia głównego** lub w innym logicznym porządku. Numery można pomijać (rezerwa). | ISO 4157-2:1998 4.1–4.5 | https://cdn.standards.iteh.ai/samples/26190/21b6343fa10b406eb6409023b3427184/ISO-4157-2-1998.pdf | TAK-N | — |
| R4-J05 | **Numer i nazwę pomieszczenia podkreśla się na rysunku.** W małych pomieszczeniach wystarczy numer, a nazwy podaje się w tabeli na tym samym arkuszu (chyba że wyjaśnia je symbol). Szafy i schowki mogą mieć numer pomieszczenia z literą (np. 404a). Klatki schodowe i szyby **najlepiej z tym samym numerem na wszystkich piętrach**. Numerować można także przestrzenie zewnętrzne (wiata, loggia, taras). | ISO 4157-2 4.3, 4.5.3, 4.6, 4.1 | j.w. | TAK-N | Wiata i taras mogą mieć numery (np. 1.20 „Wiata”). |
| R4-J06 | Identyfikator pomieszczenia (cykl życia): „**I#**” + nr kondygnacji + 3 cyfry (I#n001…), o jedną cyfrę dłuższy od numeru pomieszczenia. Warto dodać współrzędne X0Y0Z0 / Xmin… / Xmax…. | ISO 4157-3:1998 4.5–4.8 | https://cdn.standards.iteh.ai/samples/26950/ddc0b46c7e1d48338bd351c652e3cb32/ISO-4157-3-1998.pdf | TAK-N | Opcja dla modelu (klucz trwały). Na rysunkach PB zbędny. |
| R4-J07 | **Oznaczenia elementów:** główne oznaczenie (np. WINDOW/W, DOOR/D) + oznaczenie typu (np. **W12b**) lub kolejne numery (P1, P2…). **Elementy nośne:** 4 znaki, w tym nr kondygnacji + dwucyfrowy nr kolejny: **C201, S201, W201, B201** (słup, płyta, ściana, belka na kondygnacji 2). | ISO 4157-1 6.1–6.2, 7.5 | URL R4-J01 | TAK-N | Praktyka PL: O (okno), D (drzwi). Mapowanie na ID modelu w pkt 3.9. |
| R4-J08 | **Nazwy pomieszczeń:** powszechnie stosowane, odzwierciedlające funkcję. Na rzutach numery, a w zestawieniu tabelarycznym nazwa, powierzchnia i rodzaj posadzki. | [AGH-P] s. 71 (wg PN-B-01025, PN-EN ISO 4157-2) | [AGH-P] | NIE | — |

#### K. Zestawienia (schedules)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-K01 | ISO 7519 (2024 i 2025) ma rozdział 5.7.6 „Schedules and lists” (zestawienia i wykazy) oraz 5.7.3 „Designations”. Treści w podglądzie brak. | ISO 7519:2025 spis treści | URL R4-B13 | TAK-N (spis) | Szczegóły **NIEZWERYFIKOWANE**. |
| R4-K02 | **Zestawienie stolarki:** symbol typu (ISO 4157-1 6.2, np. O1, D2), liczba, wymiary otworu i stolarki, opis. Zamiast wymiarów na rzucie można dać symbol (R4-F10). | ISO 4157-1; PN-B-01029 (wg [PWR9] s. 10) | j.w. | TAK-N / NIE | Kolumny zestawienia w pkt 3.10. Parametry cieplne (U, g) wg zespołu R-fizyka. |
| R4-K03 | **Zestawienie pomieszczeń:** nr, nazwa, powierzchnia, posadzka (R4-J08). Powierzchnie wg PN-ISO 9836:2022-07 i rozp. § 20 (sekcja P). | j.w. | j.w. | NIE / TAK-A | — |
| R4-K04 | **Wykaz elementów** (konstrukcje stalowe) umieszcza się nad tabliczką, a przy wielu elementach na osobnym arkuszu formatu A4. Zawiera wymiary, masę i gatunek. Śruby w odrębnym wykazie. | PN-B-01040/praktyka (wg [AGH-K] s. 23, 61) | [AGH-K] | NIE | Słupy wiaty (stal). |

#### L. Zbrojenie i rysunek konstrukcyjny (PN-EN ISO 3766:2006, PN-B-01040:1994)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-L01 | Rysunek zbrojenia podaje:<br>• klasę betonu, klasę ekspozycji i inne wymagania;<br>• gatunek stali;<br>• **nr pręta, liczbę, średnicę, kształt i położenie**;<br>• rozstaw i długość zakładów;<br>• zabezpieczenie położenia (podkładki dystansowe);<br>• **wymiar c_v** z otulenia nominalnego c_nom i odchyłki Δc;<br>• średnice lub promienie trzpieni gięcia. | ISO 3766:2003 rozdz. 3 | https://cdn.standards.iteh.ai/samples/34171/3a43c9a895634c6081447d5a36b0b5e5/ISO-3766-2003.pdf | TAK-N | Norma zastąpiła też ISO 4066 (wykaz prętów). |
| R4-L02 | Pręt w widoku: **linia ciągła bardzo gruba**. Pręt odgięty jako łamana lub linia z łukami. Wiązka: jedna linia ze znacznikami liczby prętów. Zestaw jednakowych prętów: jeden pręt w skali + linia z ukośnymi kreskami na skrajnych prętach + **kółko** łączące. Warstwa dolna lub dalsza na wspólnym rzucie: **linia kreskowa bardzo gruba**. Oznaczenia warstw: B (dolna), T (górna), N (bliższa), F (dalsza), 1/2 (kolejność od powierzchni); w PL litery można zmienić. Siatka zgrzewana: prostokąt + przekątna (+ kreska na kierunek zbrojenia głównego), w przekroju **linia punktowa bardzo gruba**. | ISO 3766 tabl. 1 poz. 1–18 | j.w. | TAK-N | — |
| R4-L03 | Opis prętów: każdy pręt różniący się choć jedną cechą ma **indywidualny numer w okręgu** na rzucie, przekrojach i wysuniętych rzutach. **Wysunięty rzut pręta:** nr, liczba, średnica, długości odcinków, długość całkowita. Zestawy: nr, całkowita liczba, średnica, rozstaw (strefy: liczba w nawiasie + rozstaw). Odgięcia wymiaruje się po zewnętrznej, a średnice i promienie od wewnątrz. **Pręty w mm, kąty w stopniach.** | [AGH-K] s. 87–91 (wg PN-EN ISO 3766) | [AGH-K] | NIE | — |
| R4-L04 | **Wykaz (zestawienie) zbrojenia — kolumny:** oznaczenie elementu; nr pręta; klasa lub gatunek stali; średnica [mm]; długość pręta [mm lub m]; liczba elementów; liczba prętów w elemencie; łączna liczba prętów; łączna długość. Opcjonalnie kody kształtów (2 znaki) i haków (0, ±1, 2, 3) oraz tabela mas. | ISO 3766 rozdz. 7 (spis); [AGH-K] s. 99–105 | URL R4-L01; [AGH-K] | TAK-N (spis) / NIE (kolumny) | Masa: m = 7850 kg/m³ · π·d²/4. Wartość gęstości wg PN-EN 10080: **NIEZWERYFIKOWANE** w tej domenie (zespół konstrukcji). |
| R4-L05 | Rysunki zestawieniowe konstrukcji: skala **1:50, 1:100 lub 1:200**. Elementy oznacza się symbolami, np. **S – słup, R – rygiel, F – stopa, P – płyta**. Rysunki robocze elementów: zasadniczo **1:20** (uzasadnione 1:10 lub 1:50). Jeden element na arkuszu. Numery pozycji w **kółkach Ø 8–10 mm**, jednolite w projekcie (warianty „3a”). | PN-B-01040 (wg [AGH-K] s. 25–26, 66–73) | [AGH-K] | NIE | Zmiana ISO 4157-1 7.5 (C201…) jest alternatywą (R4-J07). |
| R4-L06 | **Kształtowniki i pręty stalowe:** oznaczenie ISO wyrobu lub **symbol graficzny przekroju + wymiary charakterystyczne**, a po myślniku długość cięcia, np. „L 89×60×7 – 500”. Rura: ⌀d×t. Profil zamknięty prostokątny: h×b×t. Oznaczenie stoi blisko elementu. Schematy konstrukcji: linie osi środków ciężkości (ciągła gruba) z odległościami punktów węzłowych. | ISO 5261:1995 rozdz. 4–5 (PN-EN ISO 5261:2002) | https://cdn.standards.iteh.ai/samples/21512/1afc9a89ecce4408b4a3d9e1d53aae1d/ISO-5261-1995.pdf | TAK-N | Zapis dla kwadratowego profilu zamkniętego (np. „□120×120×8” vs „□120×8”): tekst podglądu jest nieczytelny, więc **NIEZWERYFIKOWANE**. |

#### M. Projekt zagospodarowania działki (PN-B-01027:2002, PN-EN ISO 11091, § 15 rozp.)

Grubości linii w mm podane dla rysunku PZT. Źródło: tablice PN-B-01027:2002 reprodukowane w [AGH-Z] s. 4–32 (NIE, ale odczyt jest dosłowny).

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-M01 | Zakres PN-B-01027: jednobarwne oznaczenia i symbole słowno-literowe dla obiektów i urządzeń, komunikacji, ukształtowania terenu, zieleni i urządzeń terenowych, granic i linii regulacyjnych oraz wymiarowania na PZT. | PKN (karta) | [PKN] | TAK-K | Powołana w zał. 2 rozp. |
| R4-M02 | **1.1 Obrys i przekrój projektowanego obiektu:** linia ciągła **1,4**. Przekrój poziomy **1,0 m nad terenem**. Zewnętrzna krawędź obrysu = rzeczywisty zewnętrzny obrys ścian (z ociepleniem i wykończeniem). | PN-B-01027 poz. 1.1 | [AGH-Z] s. 4 | NIE | — |
| R4-M03 | 1.2 obiekt adaptowany: obrys 1,0 + kratka ukośna 0,25 pod 45° co 2 mm. 1.3 obiekt do likwidacji: znaki „×” 0,35 na obrysie geodezyjnym (0,5). 1.4 obiekt tymczasowy: obrys 0,25 + linia wielopunktowa 1,0. 1.5 objaśnienia: odnośnik 0,18, liczby i tekst 0,25, numer w kółku. | poz. 1.2–1.5 | [AGH-Z] s. 5–6 | NIE | — |
| R4-M04 | **1.6 Części projektowanego budynku:** a) obrys parteru 1,0 m nad terenem: ciągła **1,4**; b) część podziemna: **kreskowa 0,7**; c) **zadaszenie lub przewieszenie budynku > 1,0 m: punktowa 0,7**; d) podcienia z podporami lub obrys wyższych kondygnacji: linia nieciągła 0,7; e) przejazd lub przejście w parterze: krzyż 0,35. | poz. 1.6 | [AGH-Z] s. 7 | NIE | **LAMELA:** wspornik P2 (ok. 1,0 m), płyta D z wiatą i okap parteru (ok. 1,5 m) to linia punktowa 0,7 z opisem. *Weryfikacja 2026-09-25 (odczyt tablicy normy w [AGH-Z] s. 7): symbol c) dotyczy przewieszeń **> 1,0 m**. Wysięg ≤ 1,0 m norma pozwala pominąć. Dla zamkniętego wspornika P2 można też uznać wariant d) „obrys wyższych kondygnacji” (linia nieciągła 0,7). Wybór objaśnić w legendzie PZT.* |
| R4-M05 | **1.7 Wejścia:** **trójkąt równoboczny zaczerniony, bok 4 mm** + linie kierunkowe 0,35 wewnątrz obrysu. Oznacza się **tylko wejścia główne i ewakuacyjne**. | poz. 1.7 | [AGH-Z] s. 8 | NIE | — |
| R4-M06 | **1.8 Opis budynku:** „0,00=267,50”, liczba kondygnacji nadziemnych w kółku (np. „IV+P”), nr porządkowy (Nr1) przy wielu budynkach. Litery 0,25, **min. 2,5 mm**. | poz. 1.8 | [AGH-Z] s. 9 | NIE | LAMELA: „±0,00=101,65” i „III” (3 kond. nadziemne, brief). *Weryfikacja 2026-09-25: wzór normy to „0,00=267,50” (bez „±”) z grotem pod linią, a obok rzędna terenu przy wejściu (np. 266,50). Zapis z „±” jest dopuszczalny tylko jako objaśniony w legendzie.* |
| R4-M07 | **Linie zabudowy:** **obowiązująca:** ciągła 0,35 z **zaczernionymi trójkątami równobocznymi o boku 2 mm** (rytm „12·2·12”). **Nieprzekraczalna:** jak wyżej z **trójkątami niezaczernionymi**. Trójkąty są po stronie terenu zabudowy. | poz. 2.1–2.2 | [AGH-Z] s. 10 | NIE | MPZP LAMELI: nieprzekraczalna 6,0 m od 1KDD, więc niezaczernione. Liczby rytmu w mm (interpretacja). *Weryfikacja 2026-09-25: w tablicy normy poz. 2.2 nosi nazwę „Maksymalna nieprzekraczalna linia zabudowy”.* |
| R4-M08 | 2.3 oś jezdni: punktowa 0,25 (rytm 6·2·6). 2.4 granica działki do likwidacji: „×” 0,25. **2.5 linia rozgraniczająca tereny o różnym przeznaczeniu:** ciągła **0,7**, wymiarowana w osi. **2.6 granica obszaru opracowania:** kreskowa **0,5** (6·2·6). **2.7 granica działki budowlanej:** ciągła **0,35** z punktami **Ø1,0**, narożniki jako **kółko + litera** (A, B, C…). 2.8 projektowane ogrodzenie: ciągła 0,35 z kreskami poprzecznymi, gdy nie pokrywa się z granicą. 2.9 brama i furtka: symbol 0,35. 2.10 granice stref ochronnych lub uciążliwości: ciągła 0,5 z punktami 2,0 (10·1·10). | poz. 2.3–2.10 | [AGH-Z] s. 11–14 | NIE | — |
| R4-M09 | **Komunikacja:** krawędź jezdni i dojazdu **0,5**; chodnika i ścieżki **0,35**; parking: krawędzie 0,35, podział stanowisk 0,25, opis „P-n”, stanowiska dla niepełnosprawnych **NP** (krzyż w stanowisku). Nachylenie dróg w **%** ze znakiem trójkąta. | poz. 3.1–3.5 | [AGH-Z] s. 15–17 | NIE | — |
| R4-M10 | **Wymiarowanie na PZT:** linie wymiarowe, pomocnicze i ograniczniki **0,18**. Litery **min. 2,5 mm**. Symbol „//” (0,25) oznacza elementy równoległe, np. budynek // granica. Wymiaruje się obrys obiektu, odległości od granic i odległości od obiektów istniejących. **Siatka współrzędnych:** punkty krzyżykiem, opis „x …, y …” (**najpierw x, potem y**) z tą samą dokładnością. | poz. 4.1–4.2 | [AGH-Z] s. 18–19 | NIE | Przykład normy pokazuje 20,67; 9,16; 13,50 oraz 6,0 i 4,0, co zgadza się z R4-A18. |
| R4-M11 | **Ukształtowanie terenu:** skarpa projektowana: linia 0,35 z kreskami (długie i krótkie na przemian od krawędzi górnej). Rysunek a) i b) rozróżnia nachylenie > 50 % i < 50 %. **Warstwice:** istniejące ciągła **0,18**, projektowane ciągła **0,50**, do likwidacji z „×”. | poz. 5.1–5.2 | [AGH-Z] s. 20 | NIE | — |
| R4-M12 | **Sieci i przyłącza:**<br>• **kanalizacja sanitarna:** ciągła **0,7** + **zaczerniony trójkąt 3 mm** (kierunek przepływu), „Ks”, spadek „…%”;<br>• **deszczowa:** 0,7 + **trójkąt niezaczerniony**, „Kd”;<br>• wpust: prostokąt **4×2 mm** 0,25, „WK”;<br>• osadnik lub szambo: prostokąt min. **7×4 mm**;<br>• **wodociąg:** ciągła **0,5** z otwartymi „<”, **„×” w miejscu połączenia** sieci istniejącej z projektowaną;<br>• studzienka wodomierzowa: „SW”;<br>• hydrant: „HP”;<br>• studnia: punkt 2,0 + „S”;<br>• punkt świetlny: kółko Ø5 mm, słup to zaczerniony punkt Ø2 mm;<br>• **gaz:** punktowa **0,7** (3·10·3), „g”;<br>• **kabel energetyczny podziemny:** kreskowa **0,7** (2·9·2), „e”;<br>• **telekomunikacja:** wielopunktowa **0,5** (4·9·4), „t”;<br>• **ciepłownicza:** dwie ciągłe 0,5 w odstępie 2 mm, „c”. | poz. 6.1–6.13 | [AGH-Z] s. 21–25 | NIE | LAMELA: Ks (do sieci), Kd (retencja i rozsączanie), woda, „e” (złącze nN), „t” (światłowód). Gaz jest w drodze, ale nie jest wykorzystywany (tylko istniejący). |
| R4-M13 | **Zieleń:**<br>• drzewo liściaste projektowane: okrąg korony 0,35 + krzyżyk pnia 0,25, korona w skali dla średniego wieku gatunku;<br>• istniejące: okrąg 0,35 + kropka pnia min. 1 mm;<br>• iglaste: okrąg z krótkimi promieniowymi kreskami (+ krzyżyk lub kropka);<br>• drzewo do przesadzenia: okrąg kreskowy 0,35 + nr;<br>• **do usunięcia: skreślenie „X” 0,50**;<br>• żywopłot projektowany (liściasty falisty, iglasty zygzak) 0,35; istniejący 0,25;<br>• trawnik projektowany: kropki;<br>• nawierzchnia z małych elementów: linie 0,18 co 2 mm, nie na całej powierzchni;<br>• nawierzchnia z dużych elementów: kwadraty 0,18 o boku 4 mm;<br>• ściana oporowa: ciągła 0,7 z kreskami od strony skarpy. | poz. 7.1–7.11 | [AGH-Z] s. 26–32 | NIE | — |
| R4-M14 | PN-EN ISO 11091:2001 (ISO 11091:1994): zasady rysunku zagospodarowania terenu. Linie: istniejące warstwice cienka ciągła (lub cienka kreskowa), projektowane gruba ciągła, podział rabat i trawników cienka kreskowa. | ISO 128-23 tabl. 1 (odwołania do 11091) | URL R4-C07 | TAK-N | Pełnej treści ISO 11091 **nie zweryfikowano** (brak podglądu). |

#### N. Instalacje elektryczne — symbole

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-N01 | PN-EN 60617-2…-13 i **PN-EN 60617-11:2004** są wycofane (-11: 2005-12-01) bez zastępstwa. IEC 60617 prowadzi się jako **bazę danych symboli** (identyfikatory S00xxx, np. **S00457** „gniazdo wtyczkowe (siłowe), symbol ogólny”). | PKN (karta PN-EN 60617-11:2004); IEC | [PKN]; https://products.iec.ch/view/grs/8141 | TAK-K / NIE | Na rysunkach elektrycznych symbole IEC 60617 i **legenda obowiązkowa**. |
| R4-N02 | **Symbole planów instalacji** (numery wg dawnego IEC/EN 60617-11):<br>• 11-13-01 gniazdo (ogólny: półokrąg na trzonku); **11-13-04 gniazdo ze stykiem ochronnym** (półokrąg + kreska pozioma nad nim); 11-13-02 gniazdo potrójne (cyfra 3); 11-13-06 gniazdo z wyłącznikiem; 11-13-08 z transformatorem separacyjnym; 11-13-09 teletechniczne (TP, TV…);<br>• 11-14-01 łącznik (kółko + ukośna kreska); 11-14-02 podświetlany; **11-14-03 jednobiegunowy**; 11-14-04 dwubiegunowy; **11-14-05 grupowy (świecznikowy)**; **11-14-06 zmienny (schodowy)**; **11-14-07 krzyżowy**; 11-14-08 ściemniacz; 11-14-10 przycisk (dwa kółka);<br>• **11-15-01 wypust oświetleniowy** (linia zakończona „×”); 11-15-02 kinkiet; **11-15-03 lampa lub oprawa (kółko z krzyżem)**; 11-15-04 świetlówka; 11-15-11 oświetlenie awaryjne;<br>• 11-16-01 grzejnik wody; 11-16-02 wentylator;<br>• **11-12-07 rozdzielnica**;<br>• przewody N, PE, PEN oraz linie do góry, w dół i przechodzące są w tym samym zestawieniu (grupy numerów 11-11 i 11-03; przypisanie do poszczególnych symboli **NIEZWERYFIKOWANE**). | Zestawienie „Symbole graficzne wg PN-EN 60617” (INPE nr 144, s. 63–67; plik udostępniony przez Viessmann) | https://www.viessmann.edu.pl/wp-content/uploads/RT4_Zalacznik_ELEKTRYKA_Symbole_graficzne-_wg_PN-EN-60617.pdf | NIE | Nazwy symboli zgodne z listą IEC 60617 (qelectrotech), co potwierdza je częściowo. Przypisanie niektórych numerów (np. rozdzielnica) **NIEZWERYFIKOWANE** w bazie IEC. |
| R4-N03 | Dokumenty elektrotechniczne (schematy rozdzielnic, schematy jednokreskowe): PN-EN 61082-1:2015-03 (EN). Oznaczenia referencyjne aparatów: PN-EN IEC 81346-1:2023-01 (EN). | PKN | [PKN] | TAK-K | Treści nie badano (poza domeną rysunku budowlanego). |

#### O. Instalacje sanitarne, c.o., wentylacja, pompa ciepła — symbole

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-O01 | **Sieć zewnętrzna wod.-kan.:** PN-B-01700:1999 „Wodociągi i kanalizacja – Urządzenia i sieć zewnętrzna – Oznaczenia graficzne” (aktualna). **Instalacje wewnętrzne:** PN-B-01701:1984 jest **wycofana bez następcy**. **Brak aktualnej PN symboli instalacji wewnętrznych wod.-kan. i c.o.** (PN-B-01410:1989 i PN-B-01440:1998 są wycofane). | PKN | [PKN] | TAK-K | Silnik: symbole instalacji wewnętrznych wg PN-EN ISO 6412 + **legenda**. Na PZT symbole PN-B-01027 (R4-M12). |
| R4-O02 | Rurociągi uproszczone: PN-EN ISO 6412-1:2018-03 (zasady, rzutowanie prostokątne), -2:2018-04 (izometria), -3:2018-03 (elementy końcowe went. i odwadniające). Wszystkie aktualne (EN). | PKN; ISO | [PKN]; https://www.iso.org/standard/73352.html | TAK-K | Treści szczegółowej nie zweryfikowano (brak podglądu). |
| R4-O03 | **Wentylacja:** PN-EN 12792:2006 (pol., aktualna, EN 12792:2003). Rozdz. 5 „LINE GRAPHICAL SYMBOLS”: 5.1 dyfuzja (nawiewniki, wywiewniki), 5.2 rozprowadzenie (przewody, przepustnice), 5.3 uzdatnianie (filtry, wymienniki, wentylatory), 5.4 sterowanie i przyrządy. | EN 12792:2003 spis treści (podgląd SIST) | https://cdn.standards.iteh.ai/samples/6432/b9abf3cf11574ddd974e4530962891ff/SIST-EN-12792-2004.pdf | TAK-N (spis) | Kształtów symboli nie ma w podglądzie, więc są **NIEZWERYFIKOWANE**. Rysować wg legendy. |
| R4-O04 | Rodzaje powietrza i kolory (EN 16798-3): **ODA** (zewnętrzne) zielony, linia punktowa; **ETA** (wywiewane) żółty, kreskowa; **EHA** (wyrzutowe) brązowy, kreskowa; **RCA** (recyrkulacja) pomarańczowy; **IDA** (wewnętrzne) szary. **SUP** (nawiewane): kolor zależny od obróbki termodynamicznej (THM-C0…C5: zielony, niebieski, czerwony, fioletowy). | Rienhardt W., „Luftarten nach EN 16798-3” (2019) | https://www.technikplushygiene.info/fileadmin/user_upload/Artikel_2019/Luftarten_nach_EN_16798-3_20Jun2019_gesetzt_JanRi_06Aug2019.pdf | NIE | Status PN-EN 16798-3 ustala zespół instalacji. Kolory są pomocnicze (PN-B-01025 wymaga oznaczeń jednobarwnych), więc kod literowy musi być zawsze obecny. |
| R4-O05 | **Pompa ciepła:** schematy ideowe i montażowe instalacji ziębniczych i pomp ciepła wg **PN-EN 1861:2001** (pol., aktualna): „Układy i symbole”. | PKN | [PKN] | TAK-K | Treści nie zweryfikowano. |

#### P. Powierzchnie i kubatura (PN-ISO 9836:2022-07, rozp. § 12, § 14, § 20)

| ID | Wymaganie / reguła | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R4-P01 | Powierzchnie budynku określa się wg PN dotyczącej wskaźników powierzchniowych i kubaturowych z zał. nr 2, czyli **PN-ISO 9836**, z uwzględnieniem § 14 pkt 4 lit. a i § 20 ust. 1 pkt 4 lit. b. Najnowsza wersja polska to **PN-ISO 9836:2022-07**. Obowiązuje od publikacji 2022-07-18. | rozp. § 12, zał. 2; PKN | [ROZP]; PKN (URL w R4-A20) | TAK-A / TAK-K | — |
| R4-P02 | Treść PN-ISO 9836:2022-07 = ISO 9836:2017 (IDT). Trzy podejścia pomiarowe: w licu przegród (intra/extra-muros), w osiach ścian, kombinacje wg przepisów krajowych. **Powierzchnie w m² z 2 miejscami po przecinku.** Płaszczyzny pochyłe liczy się w rzucie. | ISO 9836:2017 1, 5.1.1; PKN (zakres) | https://cdn.standards.iteh.ai/samples/73149/406e5c48b7a44a41b394f0e074b99553/ISO-9836-2017.pdf | TAK-N / TAK-K | — |
| R4-P03 | **Powierzchnia zabudowy** (5.1.2) = rzut pionowy zewnętrznych wymiarów budynku w stanie wykończonym na teren. **Nie wlicza się:** części niewystających ponad teren; elementów drugorzędnych (schody i rampy zewnętrzne, **daszki**, **poziome osłony przeciwsłoneczne**, **okapy**, oświetlenie zewnętrzne); obiektów pomocniczych (szklarnie, przybudówki). **Rozporządzenie dodatkowo pomniejsza** ją o: **tarasy naziemne i podparte słupami, gzymsy, balkony oraz loggie**. | ISO 9836:2017 5.1.2; rozp. § 14 pkt 4 lit. a w brzmieniu Dz.U. 2023 poz. 2405 | URL R4-P02; [ROZP23] | TAK-N / TAK-A | LAMELA: płyta D z wiatą i okap to kwestia otwarta (pkt 4). |
| R4-P04 | **Powierzchnia całkowita** (5.1.3) = suma kondygnacji po **zewnętrznym obrysie na poziomie posadzki** (z tynkami, okładzinami, balustradami). Rozróżnia się: a) zamknięte i przekryte; b) przekryte, niezamknięte (loggie), liczone po obrysie przekrycia; c) nieprzekryte (balkony). **Rozp. § 20:** powierzchnię całkowitą pomniejsza się o tarasy, balkony i loggie. | ISO 9836:2017 5.1.3; rozp. § 20 ust. 1 pkt 4 lit. b tiret 5 (Dz.U. 2023 poz. 2405) | j.w. | TAK-N / TAK-A | Intensywność zabudowy w MPZP może mieć własną definicję (pkt 4). |
| R4-P05 | **Powierzchnia netto** (5.1.5) = w świetle wykończonych przegród **na poziomie posadzki**, bez listew i progów. Obejmuje elementy demontowalne (przepierzenia, rury, kanały). **Nie obejmuje** przegród stałych, wnęk drzwiowych i okiennych ani nisz. Dzieli się na **użytkową** (podstawowa i pomocnicza), **usługowo-techniczną** i **ruchu**. **Stałe ściany działowe** należą do **powierzchni konstrukcji** (5.1.6.1). | ISO 9836:2017 5.1.5–5.1.7; komunikat PKN KT 232 | URL R4-P02; PKN (URL w R4-A20) | TAK-N / TAK-K | — |
| R4-P06 | **Powierzchnia użytkowa wg rozporządzenia (§ 20 ust. 1 pkt 4 lit. b):**<br>• **pomniejsza się** o przekrój poziomy wszystkich przegród wewnętrznych, przejścia i otwory w przegrodach, przejścia w przegrodach zewnętrznych, balkony, tarasy, loggie, **schody wewnętrzne i podesty w lokalach wielopoziomowych**, nieużytkowe poddasza;<br>• **powiększa się** o antresole, ogrody zimowe, wbudowane szafy, schowki i garderoby;<br>• **wysokość w świetle ≥ 2,20 m → 100 %; 1,40–2,20 m → 50 %; < 1,40 m → 0 %**. | rozp. § 20 ust. 1 pkt 4 lit. b | [ROZP] | TAK-A | Zasady te **uzupełniają** PN-ISO 9836 (w normie próg 1,90 m klasyfikuje tylko jako pow. pomocniczą, wg PKN/Starzyk). |
| R4-P07 | **Kubatura brutto** = objętość ograniczona zewnętrznymi powierzchniami elementów ograniczających. **Kubatura netto** = wewnętrznymi. Podaje się ją w m³ **z 2 miejscami po przecinku**. Liczy się ją z powierzchni wg 5.1 × wysokości, a bryły nieortogonalne wg wzorów. PN-ISO 9836:2022-07 rozdziela kubaturę brutto na: 5.2.2 części zamknięte i przekryte; 5.2.3 przekryte niezamknięte; 5.2.4 nieprzekryte. | PN-ISO 9836:2015 5.2.1 (wg prezentacji IARP, Żabicki 2021); spis treści PN-ISO 9836:2022-07 (PKN) | URL R4-F15; [PKN] | NIE / TAK-K | Szczegóły, np. od której rzędnej liczyć kubaturę i czy wliczać fundamenty lub attyki: **NIEZWERYFIKOWANE** (pkt 4). |
| R4-P08 | **PN-70/B-02365** (wycofana, dawniej w katalogach projektów gotowych):<br>• obmiar **na wysokości 1,00 m nad podłogą**, **w stanie surowym** (bez tynków i okładzin);<br>• wnęki > 0,1 m² dolicza się;<br>• dokładność: pomiar 0,01 m, **powierzchnia 0,1 m²**;<br>• wysokości: < 1,40 m 0 %, 1,40–2,20 m 50 %, > 2,20 m 100 %;<br>• balkony i loggie nie wchodzą do pow. pomieszczeń.<br>**PN-ISO 9836:1997** (i następne): obmiar **na poziomie podłogi**, **w stanie wykończonym**, powierzchnia 0,01 m², część < 1,90 m to pow. pomocnicza. | prezentacja dr inż. arch. A. Starzyk, udostępniona przez PKN (wiedza.pkn.pl) | https://wiedza.pkn.pl/documents/14109/17909/prezentacja_dr_inz._arch.a.starzyk.pdf/96020d77-09b0-41fa-a836-c952b9cd56fa | NIE (materiał PKN) | Wynik wg PN-70 jest zwykle wyższy (brak tynków). Wg geodetów PKiG różnica sięga ok. **5 %** (NIE; https://powierzchnie.pkig.pl/jak-podsumowac-pn-iso-9836-po-kilku-miesiacach-od-wejscia-aktualizacji/). |

---

## 3. Implikacje dla projektu Dom LAMELA: gotowe wartości dla silnika

Wartości oznaczone **[przyjęcie]** to decyzje projektowe w granicach norm. Norma nie podaje dla nich liczby, więc objaśniamy
je w legendzie lub objaśnieniach arkusza (rozp. § 9 ust. 1).

### 3.1 Arkusze, ramka, tabliczka, układ
* **Formaty** (R4-B01). PZT 1:500 na A3 poziomo (działka 30×50 m daje 60×100 mm, plus droga i otoczenie).
  Rzuty i przekroje 1:100 na **A3** lub **A2**. Elewacje 1:100 na A2. Szczegóły 1:20/1:10 na A3.
  Konstrukcja 1:50 na A1/A2, detale 1:20/1:10. Instalacje 1:100 lub 1:50 na A2/A1.
  Wydłużone formaty tylko w razie konieczności (A3.1 = 297×841).
* **Ramka** (R4-B03, R4-B04):
  * margines lewy 20 mm, pozostałe 10 mm;
  * linia ramki 0,7 mm;
  * znaki centrujące 0,7 mm, 10 mm do środka;
  * siatka odniesień (pola 50 mm, linie 0,35, znaki 3,5 mm) na A2 i większych, na A3 opcjonalnie [przyjęcie].
* **Pole tekstu** przy prawej krawędzi, **szerokość 180 mm** (ISO 7200:2004; ISO 9431 dopuszcza ≤ 170 i ≥ 100) [przyjęcie: 180].
  Od góry do dołu:
  1. objaśnienia i legenda (symbole, materiały, jednostki: „Wymiary w cm, rzędne w m”);
  2. uwagi i instrukcje;
  3. odniesienia do innych rysunków;
  4. rysunek lokalizacyjny (mini-PZT ze strzałką N);
  5. tabela zmian (oznaczenie, opis, data, podpis);
  6. **tabliczka (metryka)** w prawym dolnym rogu.
* **Tabliczka, pola** (M = wymagane prawem lub ISO 7200):
  1. właściciel dokumentu / biuro projektowe (M, ISO 7200) — placeholder;
  2. **nazwa obiektu** (M § 10): „Budynek mieszkalny jednorodzinny wolnostojący »Dom LAMELA«”;
  3. **adres obiektu, nr działki ewid., obręb, jedn. ewid.** [praktyka; § 7 ust. 2 dla strony tytułowej]:
     „dz. nr 123/4, obręb 0005 Przykładowo, gm. Przykładowo” (dane fikcyjne);
  4. **inwestor** [praktyka; § 7 ust. 2 pkt 2 lit. d dla strony tytułowej] — placeholder;
  5. **stadium / część**: PZT | PAB | PT; **branża**: architektura (AR), konstrukcja (BO), instalacje sanitarne (IS),
     instalacje elektryczne (IE) (kody z zał. 1 rozp.);
  6. **tytuł rysunku** (M § 10; ISO 7200 zaleca ≤ 25/30 znaków w polu tytułu, dłuższe w tytule uzupełniającym);
  7. **skala** (M § 10; ISO 5455 4.1);
  8. **nr rysunku** (M § 10) w formacie `<część>-<branża>-<nr>`, np. `PAB-A-03`, `PT-K-05` [przyjęcie]. Nr arkusza
     i liczba arkuszy wg ISO 7200;
  9. **data sporządzenia** (M § 10) jako `rrrr-mm-dd` (ISO 7200: pole 10 znaków) [przyjęcie];
  10. **projektant**: imię i nazwisko, specjalność, **nr uprawnień**, podpis (tylko papier) (M § 10). Pola do uzupełnienia;
  11. **sprawdzający**: jak wyżej + data sprawdzenia. Pole opcjonalne, bo art. 20 ust. 3 pkt 2 PB zwalnia budynki
      jednorodzinne. Silnik ukrywa pole, gdy `sprawdzenie=false` [przyjęcie];
  12. opracował (creator, M ISO 7200);
  13. indeks zmian (O);
  14. format arkusza (O ISO 7200; oznaczenie formatu także w dolnym marginesie wg ISO 5457);
  15. rodzaj dokumentu (M ISO 7200): rzut / przekrój / elewacja / zestawienie / schemat.
* **Podpis:** w PDF podpis kwalifikowany, osobisty lub zaufany **dla pliku** (§ 7 ust. 4a). Na rysunku pole „podpis”
  zostaje puste lub z adnotacją „podpisano elektronicznie”.
* **Pliki:** `PZT_PAB_ZL_2026.mm.dd.pdf` (lub osobno) oraz `PT_1_AR_…`, `PT_2_BO_…`, `PT_3_IS_…`, `PT_4_IE_…`.
  Każdy plik ≤ 150 MB, wektorowy. Dla wydruku: składanie do A4 z tabliczką na wierzchu i marginesem 20 mm do wpięcia
  [przyjęcie; PN-N-01603 wycofana].

### 3.2 Linie: mapowanie typów i grup (ISO 128-2 / ISO 128-23)
| Skala rysunku | Grupa (ISO 128-23 tabl. 2) | cienka | gruba | b. gruba | symbole |
|---|---|---|---|---|---|
| 1:100 (rzuty, przekroje, elewacje PAB) | **0,5** [przyjęcie] | 0,25 | 0,5 | 1,0 | 0,35 |
| 1:50 (konstrukcja, instalacje, rzuty PT) | **0,7** [przyjęcie] | 0,35 | 0,7 | 1,4 | 0,5 |
| 1:20 / 1:10 / 1:5 (detale) | **0,7** [przyjęcie] | 0,35 | 0,7 | 1,4 | 0,5 |
| 1:500 (PZT) | grubości wprost z PN-B-01027 (R4-M02…M13) | — | — | — | — |

Przypisanie w silniku (typ ISO → element):
* **01.2** (gruba ciągła): zarys ścian i stropów **w przekroju z kreskowaniem**; strzałki przekrojów.
* **01.3** (b. gruba): zarys w przekroju bez kreskowania; **pręty zbrojeniowe**; obrys budynku na planie sytuacyjnym.
* **01.1** (cienka): widok za płaszczyzną przekroju; kreskowanie; wymiary; odnośniki; stolarka; schody; wyposażenie; strzałki spadków.
* **04.1 + 04.2 na końcach**: linia przekroju.
* **04.1**: osie konstrukcyjne.
* **02.1** (cienka kreskowa): elementy **pod** płaszczyzną, zarysy niewidoczne.
* **04.2** (punktowa gruba): elementy **przed** płaszczyzną przekroju, np. **wsporniki P2 i płyta D na rzucie parteru**.
* **05.1**: położenia skrajne skrzydeł i bram przesuwnych.
* **07.1**: obiekty nieobjęte projektem (budynki sąsiednie na rzutach).

Wzory kresek (R4-C03):
* kreska 12d, przerwa 3d, kreska długa 24d, kropka ≤ d;
* odstęp linii równoległych ≥ 0,7 mm;
* warstwy przegród cieńsze od 0,7 mm na papierze łączy się w obrysie przegrody. Przy 1:100 to warstwy < 7 cm, przy 1:50 < 3,5 cm.

Eksport PDF: 1 mm = 2,8346 pt. Linie w mm na wydruku 1:1 formatu (grubość nie skaluje się z podziałką).

### 3.3 Pismo
* Font CAD typu **CB proste** (ISO 3098-5), z polskimi znakami (ISO 3098-4).
  Wariant zgodny z wtórną informacją o PN-B-01025: **Arial (CE), szerokość 0,8** (R4-D06).
  [przyjęcie: font bezszeryfowy z pełnym zestawem PL, szerokość 0,8].
* Wysokości [przyjęcie z szeregu ISO 3098-1]:
  * wymiary i rzędne **2,5 mm** (PN-B-01027 min. 2,5 na PZT);
  * numery i nazwy pomieszczeń **2,5–3,5 mm** (podkreślone, ISO 4157-2);
  * oznaczenia osi **3,5 mm** w okręgu Ø10 mm [przyjęcie];
  * litery przekroju **5 mm** (≈1,41×3,5);
  * tytuły widoków **5 mm**;
  * tytuł w tabliczce **5–7 mm**;
  * drobne opisy w tabliczce **1,8–2,5 mm**.
* Grubość kreski pisma d = h/10 dla typu B (R4-D04; np. 2,5 mm → 0,25 mm). Odstęp znaków 2d.

### 3.4 Podziałki dla poszczególnych rysunków
* PZT: **1:500** (min. prawny 1:500), orientacja „N do góry”.
* PAB: rzuty, przekroje i elewacje **1:100** (min. prawny); rzut dachu 1:100.
* PT architektura: **1:50** rzuty i przekroje (czytelność warstw); detale **1:10, 1:5**.
* PT konstrukcja: rzuty **1:50**, zestawieniowe 1:50–1:100, elementy żelbetowe **1:20** (R4-L05), węzły 1:10/1:5.
* PT instalacje: **1:50** (rzuty), schematy bez skali (opis „bez skali” w polu skali).
* Oznaczenie w tabliczce „1:100”, a w widokach o innej skali skala przy tytule widoku (ISO 5455 4.2).

### 3.5 Wymiarowanie
* Jednostki: **cm** na rysunkach arch.-bud., **m** na PZT, **mm** na rysunkach zbrojenia i stali.
  W objaśnieniach: „Wymiary w cm, rzędne w m n.p.m./względne w m”.
  Ułamki cm jako indeks górny (87⁵) [przyjęcie; praktyka, R4-F07] **albo** zapis dziesiętny 87,5.
  Na rysunku stosujemy jeden sposób i objaśniamy go w legendzie.
* Ograniczniki: kreska **45°**, długość **3 mm** [przyjęcie w przedziale 2,5–3,5], grubość jak linia wymiarowa (cienka).
  Linia wymiarowa wystaje **2 mm** poza skrajne linie pomocnicze, a pomocnicze wystają **2 mm** poza linię wymiarową
  [przyjęcie, R4-F03]. Pomocnicze zaczynają się **2 mm** od obrysu i mają jednakową długość [przyjęcie].
* Odstępy: pierwszy ciąg **10 mm** od najdalszego obrysu, kolejne co **7 mm** [R4-F04, 7–8 mm].
  Liczby **1 mm** nad linią [przyjęcie w przedziale 0,5–1,5].
* **Ciągi zewnętrzne na każdej elewacji rzutu, od obrysu** [R4-F08]:
  1. otwory i filary w licu muru (szerokości otworów w świetle muru);
  2. osie otworów i ściany wewnętrzne dochodzące do ściany zewnętrznej;
  3. osie konstrukcyjne (A, B, …, 1, 2, …);
  4. wymiar całkowity.

  Ciągi 1–2 pomija się przy ścianach bez otworów.
* **Otwory:** na osi otworu ułamek `szer / (parapet) wys`, np. `120 / (85) 150` [R4-F10], albo symbol stolarki (O3, D2),
  gdy jest zestawienie. W LAMELI stosujemy symbole + zestawienie, a na rzucie w nawiasie wysokość parapetu, gdy jest
  niestandardowa.
* **Schody:** `n × h × s`, np. `17 × 17,6 × 28` (cm) przy strzałce biegu [przyjęcie, R4-F13]. Wartości ustala zespół architektury.
* **PZT:** wymiary w m, **2 miejsca po przecinku**. Pełne metry mogą mieć 1 miejsce (np. 6,0). Zakres: obrys budynku,
  odległości od każdej granicy, od linii zabudowy i linii rozgraniczającej 1KDD, odległości od budynków sąsiednich
  (R4-A17, R4-A18, R4-M10). Symbol „//” przy równoległości budynku do granic.

### 3.6 Rzędne
* Architektura i konstrukcja: **3 miejsca po przecinku** w m wg PN-B-01025 3.5 (R4-G01): `±0,000`, `+3,150`, `–0,300`.
  Kolizja z briefem („±0,00, +3,15”); **rekomendacja: 3 miejsca**. Model trzyma rzędne w m z dokładnością 1 mm.
* Przekroje i elewacje: zero jako grot 90° w połowie zaczerniony, pozostałe jako grot otwarty 90°.
  Nad kreską wartość względna, pod kreską bezwzględna: `±0,000` / `101,650`. Alternatywnie `±0,000 = 101,65`.
* Rzuty: „×” + linia odniesienia + wartość (poziomy posadzek, tarasów, podestów). Kółko, gdy punkt leży na przecięciu linii.
* PZT: `±0,00=101,65` (2 miejsca, wzór PN-B-01027 poz. 1.8). Rzędne terenu istniejącego i projektowanego w m n.p.m.
  z 2 miejscami (PL-EVRF2007-NH).
* Spadki: strzałka w kierunku spadku + `2 %` (stropodachy, tarasy, podjazd). Pochylnie: kółko + grot + `%`.

### 3.7 Symbole architektoniczne (rzut, przekrój)
* Rzut na wysokości **1,0 m** nad posadzką kondygnacji.
* **Linia przekroju:** cienka 04.1 z odcinkami 04.2 na końcach i załamaniach (długość [przyjęcie] 10 mm).
  Strzałki grube, litery **A-A, B-B** po obu stronach, 5 mm. Tytuł „PRZEKRÓJ A-A” nad rysunkiem przekroju.
  Przekroje oznacza się na wszystkich rzutach.
* **Strzałka północy** na PZT, rzucie parteru i rysunku lokalizacyjnym.
  **Dla oferty projektu typowego:** oznaczyć **zalecaną orientację i dopuszczalne odchylenie od N** (PN-B-01025 3.2):
  elewacja ogrodowa na S. Zakres odchylenia ustala zespół koncepcji (pkt 4).
* **Drzwi:** skrzydło pod **90° z łukiem** (1:50 i 1:100). Drzwi przesuwne HS i przesuwne chowane w ścianie mają osobne
  symbole. Brama wiaty (jeśli jest) jako podnoszona lub przesuwna wg PN-B-01025.
* **Okna:** uproszczone z parapetem (wariant PN-B-01025). Kierunek otwierania na elewacjach: trójkąt otwierania linią
  cienką. Konwencja otwierania: **NIEZWERYFIKOWANE** w PN-B-01025, więc objaśniamy ją w legendzie.
* **Schody:** strzałka od kółka (dół) do grota (góra). Przecięcie ukośną linią z zygzakiem. Opis `n × h × s`.
* **Otwory w stropach** (klatka, wyłaz na dach P2): dwie przekątne cienkie. **Wnęki**: jedna przekątna.
* **Elementy nad płaszczyzną rzutu** (wsporniki P2, płyta D, okap parteru, podciągi): linia **04.2** lub cienka kreskowa
  wg R4-H10, **z opisem** („obrys płyty D nad”).
* **Kanały wentylacyjne:** przekątna. Piony instalacyjne: prostokąt + opis.
* **Osie konstrukcyjne:** okręgi **Ø10 mm** [przyjęcie], litery w kierunku x (A, B, …) i cyfry w kierunku y (1, 2, …)
  zgodnie z modelem (`osie.x`, `osie.y`).
* **Klasy ppoż.** (§ 9 ust. 2): etykieta tekstowa przy elemencie, jeśli zespół ppoż. je wyznaczy.

### 3.8 Materiały w przekroju: specyfikacja kreskowań
Kąty i rodzaje linii zgodne z PN-B-01030 (R4-I02). Odstępy (mm na papierze) to **[przyjęcie]**, bo PN-B-01030 ich nie podaje.
Stała podziałka kreskowania niezależna od skali rysunku jest zgodna z ISO 128-3 7.2 (odstęp dostosowany do pola).
Wszystkie linie kreskowania: **cienkie** (grupa rysunku).

| Kod kreskowania (model) | Materiał | Wzór | Parametry [przyjęcie] |
|---|---|---|---|
| ZELBET | żelbet (stropy, wieńce, wsporniki, ławy/płyta) | 45°, na przemian linia ciągła i przerywana | odstęp linii 1,5 mm; przerywana: kreska 3 mm / przerwa 1 mm |
| BETON | beton niezbrojony (chudy beton, podkład) | 45°, wszystkie linie przerywane, przesunięte | odstęp 2,0 mm; kreska 3 / przerwa 1 mm, przesunięcie 1,5 mm |
| MUR_CERAM | ceramika (cegły, pustaki) | 45° ciągłe | odstęp 1,5 mm |
| MUR_SILIKAT | bloczki wapienno-piaskowe | **brak w PN-B-01030** → 45° ciągłe + 135° ciągłe (kratka ukośna) | odstęp 2,0 mm; **w legendzie** |
| BET_KOM | beton komórkowy | **brak osobnego wzoru** → jak „beton lekki”: 45° przerywane + grupy kółek Ø0,8 mm co ok. 8 mm | **w legendzie** |
| IZOL_MIEKKA | wełna mineralna | meander (linia falista „UUU”) na całą grubość warstwy | skok 2 mm (przy grubości ≥ 2 mm na papierze) |
| IZOL_TWARDA | EPS/XPS/PIR | zygzak („VVV”) na całą grubość | skok 2 mm |
| HYDRO | izolacja przeciwwilgociowa lub przeciwwodna | pas czarny z białymi prostokątami (min. 0,7 mm grubości na papierze); przy cienkiej warstwie linia b. gruba | czarny 3 mm / biały 1,5 mm |
| PAROIZOL | paroizolacja | **brak w PN-B-01030** → linia kreskowa cienka po ciepłej stronie | kreska 3 / przerwa 1 mm; **w legendzie** |
| TYNK / WYLEWKA / ZAPRAWA / PODSYPKA | tynki, jastrych, podsypki | kropki nieregularne | gęstość ok. 8 kropek/cm² [przyjęcie] |
| GRUNT_RODZIMY | grunt rodzimy | linia gruba + ukośne kreski pod linią na przemian (wzór PN-B-01030 poz. 1) | kreski 2 mm co 2 mm |
| NASYP | nasyp, zasypka | **brak** → kropki + kreski krótkie nieregularne | **w legendzie** |
| PIASEK / ZWIR | podsypka piaskowa / żwirowa | kropki (jak podsypka) / kółka | **w legendzie** |
| DREWNO | drewno (przekrój / wzdłuż) | krzyż + słoje / linie słojów | wg PN-B-01030 poz. 8 |
| STAL | stal (słupy wiaty, łączniki) | przekrój zaczerniony; przy dużych przekrojach kreskowanie 45° gęste 0,7 mm | ISO 128-3 7.5 (cienkie przekroje) |
| SZKLO | szyby | pas z grupami 3 kresek ukośnych | wg PN-B-01030 poz. 14 |

Zasady ogólne:
* sąsiednie elementy z tego samego materiału kreskuje się w przeciwnych kierunkach;
* duże pola kreskuje się pasem przy brzegu (szerokość pasa 5 mm [przyjęcie]);
* przekroje węższe od 1,5 mm na papierze się zaczernia, zostawiając prześwit **≥ 0,7 mm**;
* przy 1:100 warstwy < 7 cm pomija się (R4-C04), a ich opis podaje się w „drabince” (R4-H14).

### 3.9 Numeracja kondygnacji, pomieszczeń i elementów
* **Kolizja (doprecyzowana w weryfikacji 2026-09-25):** schemat modelu stosuje „0.01” (P0 = parter). ISO 4157-1 7.2 numeruje od 1
  **kondygnacje (storeys)**, co jest podstawą *identyfikatorów* pomieszczeń (ISO 4157-3, 7.4.3). **Numery pomieszczeń**
  (ISO 4157-2) opierają się natomiast na krajowej praktyce numeracji **pięter (floors)**, z literami dla parteru (G01), 7.4.2.
  Samo ISO nie wyklucza więc schematu „parter = 0/G”. Kolizja zachodzi tylko z PN-B-01025 3.4 (wg źródeł wtórnych), która
  poprzedza numer pomieszczenia numerem kondygnacji. PN-B-01025 3.4 i ISO 4157-1 7.2 (wtórnie i pierwotnie) każą
  numerować **kondygnację przy terenie jako 1**.
* **Rekomendacja:** ID w modelu bez zmian (P0/P1/P2, „0.01” jako klucz wewnętrzny). Na rysunkach drukujemy
  **numer kondygnacji = 1, 2, 3** i **numer pomieszczenia = `<kond>.<nn>`**: parter 1.01–1.xx, I piętro 2.01…, II piętro 3.01….
  Alternatywa ISO 4157-2: 101, 201, 301 bez kropki. Zapis z kropką przy numerach 3-cyfrowych nie narusza zakazu
  z ISO 4157-2 4.4.3, który dotyczy numerów 4-cyfrowych. Odbiega jednak od formy **zalecanej** w 4.4.1 („preferably” 101–199),
  więc format trzeba objaśnić w legendzie.
* Numeracja **zgodnie z ruchem wskazówek zegara od wejścia głównego**. Klatka schodowa **ten sam numer końcowy** na
  każdej kondygnacji (np. 1.02, 2.02, 3.02 „Klatka schodowa”). Wiata i taras mogą mieć numery (np. 1.20 „Wiata”).
  Szafy wnękowe: 1.05a.
* Numer i nazwa **podkreślone**. W małych pomieszczeniach tylko numer, a tabela nazw na arkuszu (ISO 4157-2 4.3).
* Elementy: stolarka `O1…`, `D1…`, `HS1…` (typy wg ISO 4157-1 6.2) [przyjęcie liter PL]. Konstrukcja zgodnie z PN-B-01040
  (S – słup, P – płyta, R – rygiel/belka, F – stopa, Ł – ława [przyjęcie]) albo wg ISO 4157-1 7.5 (C201…).
  **Rekomendacja:** mapować ID modelu (SL1, B1, W1, ST1) na etykiety rysunkowe z numerem kondygnacji ISO, np. `S101`.
  Numery pozycji zbrojenia w kółkach **Ø8–10 mm**.

### 3.10 Zestawienia (generowane z modelu)
* **Zestawienie pomieszczeń** (na każdym rzucie): nr | nazwa | pow. [m², 2 miejsca] | posadzka | (opcj.) wys. w świetle |
  kategoria wg PN-ISO 9836 (podstawowa / pomocnicza / ruchu / usługowo-techniczna). Suma pow. użytkowej kondygnacji
  wg § 20 rozp. (R4-P06).
* **Zestawienie stolarki:** symbol | widok od zewnątrz (1:50) | wymiar otworu w świetle muru (szer. × wys.) |
  wymiar stolarki | szer. w świetle ościeżnicy (drzwi, WT § 9) | rodzaj otwierania | U, g (od zespołu fizyki) |
  osłona | liczba | uwagi.
* **Zestawienie stali zbrojeniowej** (R4-L04): element | nr pręta | stal | ⌀ [mm] | dł. [m] | liczba elem. |
  szt./elem. | szt. razem | dł. razem wg średnic | masa wg średnic [kg] | suma.
* **Zestawienie powierzchni i kubatury** (PAB, część opisowa i rysunek zbiorczy): pow. zabudowy (§ 14; ISO 5.1.2),
  pow. całkowita (ISO 5.1.3 minus tarasy, balkony, loggie wg § 20), pow. netto, użytkowa (§ 20), ruchu,
  usługowo-techniczna, kubatura brutto (5.2.2–5.2.4 osobno), wysokość, liczba kondygnacji.

### 3.11 PZT (1:500): konkretna symbolika
* Budynek: obrys **1,4** wg przekroju 1,0 m nad terenem. Wspornik P2, płyta D z wiatą i okap parteru: linia **punktowa 0,7**
  z opisem wysięgu. Słupy wiaty w rzucie. Wejście główne: trójkąt zaczerniony 4 mm.
  Opis: `±0,00=101,65`, `III` w kółku, funkcja „bud. mieszk. jednorodz.”.
* Linia zabudowy nieprzekraczalna (6,0 m od 1KDD): ciągła 0,35 z **niezaczernionymi** trójkątami 2 mm.
  Linia rozgraniczająca drogi: ciągła **0,7**.
* Granica działki: ciągła **0,35** z punktami Ø1,0. Narożniki `A, B, C, D` w kółkach ze współrzędnymi (x = północ, y = wschód).
* Ogrodzenie: 0,35 z kreskami. Brama przesuwna i furtka: symbol. Miejsce na pojemniki na odpady: obrys + opis.
* Uzbrojenie:
  * woda: ciągła 0,5 z „<”, wodomierz „SW” w budynku lub studzience;
  * **Ks**: 0,7 + trójkąt pełny, spadek %;
  * **Kd**: 0,7 + trójkąt pusty do zbiornika retencyjnego i skrzynek rozsączających (obrys + opis);
  * **e**: kreskowa 0,7 od złącza w linii ogrodzenia;
  * **t**: wielopunktowa 0,5;
  * istniejące sieci w drodze wg mapy.
  * Miejsca włączeń: „×”.
* Teren: rzędne istniejące i projektowane (m n.p.m., 2 miejsca). Warstwice istniejące 0,18, projektowane 0,50.
* Zieleń: drzewa istniejące, do usunięcia (X 0,50) i projektowane. Trawnik: kropki. Nawierzchnie: 7.10/7.11.
* Wymiary w m: odległości budynek–granice (4 strony), budynek–linia zabudowy, budynek–budynki sąsiednie, wymiary
  obrysu, szerokość zjazdu, miejsca postojowe (P-3 w tym wiata).
* Legenda (§ 9 ust. 1) + zestawienie powierzchni (§ 14 pkt 4) + strzałka N + skala liniowa [przyjęcie] + informacja
  o mapie do celów projektowych (przykładowej, fikcyjnej).

### 3.12 Instalacje: podejście „legenda najpierw”
* Każdy arkusz PT instalacyjny ma **legendę symboli**, bo brak aktualnej PN dla symboli instalacji wewnętrznych wod.-kan.
  i c.o. (R4-O01), a PN-EN 60617-11 jest wycofana (R4-N01).
* Elektryka: symbole z R4-N02, w legendzie z numerem IEC (np. „11-13-04 gniazdo 230 V z bolcem ochronnym”).
  Obwody: opis przy symbolu (np. „G3/1”), wysokości montażu w legendzie. Rozdzielnica RG: prostokąt + oznaczenie.
* Wentylacja (rekuperacja): kody **ODA, SUP, ETA, EHA** zawsze tekstem (R4-O04). Kolory opcjonalne, bo rysunek musi być
  czytelny jednobarwnie (PN-B-01025: oznaczenia jednobarwne).
* Pompa ciepła: schemat ideowy wg PN-EN 1861 (R4-O05) + legenda.
* Rurociągi: pojedyncza linia z oznaczeniem medium i średnicy (np. „Wz PE-X 16×2,0”, „Kan PVC 110”) i strzałką spadku
  kanalizacji z %. Oznaczenia literowe mediów [przyjęcie, praktyka PL]: Wz (woda zimna), Wc (woda ciepła), Cyrk,
  Kan/Ks, Kd, Z/P (zasilanie/powrót c.o.). Wszystkie w legendzie.

### 3.13 Obliczanie powierzchni i kubatury w silniku
Algorytm dla każdej kondygnacji:
1. `pow_calkowita` z obrysu zewnętrznego (z ociepleniem i tynkiem) **na poziomie posadzki**, osobno a/b/c (5.1.3.1).
   Dla § 20 odejmuje się tarasy, balkony i loggie.
2. `pow_netto` z wieloboków pomieszczeń w świetle **wykończonych** przegród na poziomie posadzki (bez listew i progów).
   Wnęki drzwiowe i okienne należą do pow. konstrukcji. Ściany działowe stałe również (komunikat PKN).
3. Klasyfikacja pomieszczeń: `kategoria` ∈ {podstawowa, pomocnicza, ruchu, usługowo-techniczna}.
   Pom. techniczne pompy ciepła i rekuperatora to usługowo-techniczna (5.1.8). Hol i klatka to ruchu (5.1.9).
4. `pow_uzytkowa_rozp` wg § 20: suma pomieszczeń bez schodów wewnętrznych (lokal wielopoziomowy), z szafami, schowkami
   i garderobami, z wagą wysokości (≥ 2,20 → 1,0; 1,40–2,20 → 0,5; < 1,40 → 0). LAMELA ma stropodachy płaskie,
   więc w praktyce waga 1,0 (wysokości w świetle ≥ 2,50 m wg briefu).
5. `pow_zabudowy` = rzut zewnętrznego obrysu części zamkniętych (z przewieszeniami zamkniętymi, np. wspornik P2) na teren,
   bez okapów, daszków, poziomych osłon, schodów i ramp zewnętrznych, **tarasów podpartych słupami (płyta D)**,
   gzymsów, balkonów i loggii (ISO 5.1.2 + § 14 pkt 4 lit. a). Status wiaty: pkt 4.
6. Zaokrąglenie: m² i m³ do **0,01** (ISO 5.1.1.2; 5.2.1.3).
7. Informacyjnie (strona WWW, porównanie z katalogami): pow. „wg PN-70/B-02365” (obmiar 1 m nad podłogą w stanie surowym,
   dokładność 0,1 m²). **Nie umieszczać jej w projekcie budowlanym** jako parametru formalnego.

### 3.14 Kontrola jakości rysunków: lista automatycznych testów
1. Każdy arkusz ma: tytuł, skalę, nr, datę, nazwę obiektu, projektanta z nr uprawnień (§ 10), oznaczenie formatu (ISO 5457)
   i legendę (§ 9).
2. Skala PAB/PT ≥ 1:100, PZT ≥ 1:500.
3. Odstęp linii równoległych ≥ 0,7 mm. Grubości wyłącznie z szeregu R4-C01.
4. Wysokości tekstu wyłącznie z szeregu R4-D01, min. 2,5 mm na PZT.
5. Wymiary PZT z 2 miejscami (lub 1 dla pełnych metrów). Rzędne arch. z 3 miejscami.
6. Każdy otwór ma symbol w zestawieniu. Każde pomieszczenie ma nr i wpis w zestawieniu.
7. Łańcuchy wymiarowe sumują się do wymiaru całkowitego (tolerancja 0).
8. PDF wektorowy, rozmiar pliku ≤ 150 MB, nazwa wg zał. 1.

---

## 4. Nierozstrzygnięte

1. **PN-EN ISO 7519:** wersję 2024-09 (EN) wycofano 2026-04-16. W katalogu PKN nie znaleziono następcy
   (zapytania „PN-EN ISO 7519”, „7519”, „PN-EN ISO 7519:2026”). ISO wydało ISO 7519:2025 (3. wyd., drobna rewizja).
   Status EN ISO 7519:2025 i ewentualnej PN: **NIEZWERYFIKOWANE**. Normy nie ma w zał. 2 rozp., więc skutki są tylko
   dobrą praktyką.
2. **PN-EN ISO 6284 w zał. 2 („najnowsza norma opublikowana w języku polskim”):** najnowsza polska wersja
   (PN-EN ISO 6284:2001) jest **wycofana**, a aktualna to PN-EN ISO 6284:2024-06 (ang.). Którą uznać za „powołaną”,
   rozstrzyga zespół prawny. W LAMELI tolerancji wymiarów na rysunkach PB nie przewidujemy.
3. **Numeracja kondygnacji (parter = 1 wg PN-B-01025/ISO 4157-1 vs parter = 0 w schemacie modelu):** tekst PN-B-01025 3.4
   znamy tylko ze źródeł wtórnych (AGH, PWr). Przed zamrożeniem szablonu warto sprawdzić tekst normy (zakup PKN).
   *Weryfikacja 2026-09-25:* ISO 4157-1 7.4.2 opiera **numery pomieszczeń** na krajowej praktyce numeracji pięter
   (dopuszcza G01), a nie na numeracji kondygnacji z 7.2. Kolizja dotyczy więc wyłącznie PN-B-01025 (pkt 3.9).
4. **Dokładność rzędnych (3 vs 2 miejsca po przecinku):** PN-B-01025 3.5 wg źródeł wtórnych każe 3 miejsca. Brief zakłada 2.
   Rekomendujemy 3 na rysunkach arch.-bud. i 2 na PZT. Decyzję trzeba zapisać w briefie.
5. **Tabliczka wg PN-B-01025 pkt 2.3** („Tabliczki tytułowe”): treści nie widzieliśmy. Szablon oparto na § 10 rozp.
   + ISO 7200 + praktyce.
6. **ISO 128-2:2022 zał. B** (linie w budownictwie, normatywny): nie wiadomo, czy tabela zastosowań i grup linii jest
   identyczna jak w wycofanej ISO 128-23:1999, na której oparliśmy mapowanie. **NIEZWERYFIKOWANE**.
7. **Kreskowania PN-B-01030:** geometrię odczytano z dwóch reprodukcji. Odstępy i długości kresek norma pokazuje tylko
   graficznie, więc wartości w pkt 3.8 to przyjęcia. Brak wzorów dla silikatów, betonu komórkowego, paroizolacji, nasypu,
   piasku i żwiru, więc **legenda obowiązkowa**. Przypisanie „meander = wełna, zygzak = styropian” to konwencja projektu,
   nie wymóg normy.
8. **Superskrypt mm (87⁵):** to praktyka biurowa i funkcja programów CAD. Nie potwierdzono jej jako wymogu PN-B-01029.
9. **Opis schodów** („n × h × s”): kolejność i jednostki (mm czy cm) wg PN-B-01029/PN-B-01025 potwierdzone tylko
   częściowo, a źródła wtórne różnią się w szczegółach.
10. **Powierzchnia zabudowy a wiata i płyta D:** § 14 rozp. wyłącza „tarasy podparte słupami”, a ISO 9836 5.1.2 wyłącza
    „daszki” (canopies). Czy wiata pod płytą D (zadaszenie na słupach, nad nią taras) wchodzi do powierzchni zabudowy
    w rozumieniu **MPZP** (fikcyjna uchwała, własne definicje?), rozstrzyga zespół MPZP/PZT. Wpływa to na wskaźnik 30 %.
11. **Kubatura brutto:** dokładne granice pomiaru (od spodu płyty parteru czy od fundamentu, attyki, wsporniki, części
    przekryte niezamknięte, np. wiata, wg 5.2.3) wymagają tekstu PN-ISO 9836:2022-07 pkt 5.2.2–5.2.4. **NIEZWERYFIKOWANE**.
12. **Sprawdzenie projektu:** czy LAMELA (wsporniki żelbetowe, 3 kondygnacje) mieści się w „prostej konstrukcji”
    z art. 20 ust. 3 pkt 2 PB. Wpływa na pole „sprawdzający” w metryce. Do rozstrzygnięcia przez zespół prawny.
13. **Wejście w życie § 15 ust. 3** (dokładność 0,01 m na PZT): data „ok. 5.11.2026” to wyliczenie własne
    (6 mies. od ogłoszenia 4.05.2026). Potwierdzić w ELI (akt 2026/597 ma status IN_FORCE od 2026-05-19 dla części głównej).
    *Weryfikacja 2026-09-25:* ELI nie ma odrębnej daty dla § 1 pkt 3 lit. b. Wyliczenie (koniec terminu 4.11.2026, wejście
    w życie 5.11.2026) sprawdzono ponownie i uznajemy za prawidłowe. Status: **rozstrzygnięte przez wyliczenie**.
    Silnik stosuje 0,01 m niezależnie od daty.
14. **Symbole instalacji wewnętrznych (wod.-kan., c.o.):** brak aktualnej PN. Treści PN-EN ISO 6412-1:2018,
    PN-EN 12792:2006 (symbole went.) i PN-EN 1861:2001 nie zweryfikowano (brak podglądu).
    Przyjęcie: symbole praktyki + legenda.
15. **Numery IEC 60617 dla symboli elektrycznych:** podano wg zestawienia wtórnego (numeracja dawnej EN 60617-11).
    Identyfikatory bazy IEC (S00xxx) potwierdzono tylko dla S00457. Do weryfikacji w bazie IEC (płatny dostęp).
16. **Treść zmiany PN-EN ISO 5457/A1:2010** (A4 poziomo): znana tylko ze streszczenia wtórnego.
17. **Status WT** (Dz.U. 2002 nr 75 poz. 690, „uznany za uchylony” 2026-09-21): wpływa na R4-F15 (wymiary z wykończeniem,
    drzwi w świetle ościeżnicy) i na odesłanie w § 20 ust. 1 pkt 11 rozp. Do potwierdzenia przez R3.
18. **Font:** ISOCPEUR jest komercyjny. Otwarty font zgodny z ISO 3098 (np. osifont) ma **NIEZWERYFIKOWANE** pokrycie
    polskich znaków. Zalecenie PN-B-01025 „Arial CE, szer. 0,8” pochodzi ze źródła wtórnego.

---

## 5. Weryfikacja niezależna (2026-09-25)

Weryfikator: niezależny agent (adwersarz). Przyjęto założenie, że każde ustalenie może być błędne, i sprawdzono je
w źródłach pobranych samodzielnie. Materiały i skrypty zapytań:
`/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R4ver/`
(`q.py`/`q2.py`/`q3.py`: własne zapytania do katalogu PKN; PDF-y aktów z API ELI; podglądy ISO z iTeh; strony AGH/PCEZ).

### 5.1 Potwierdzone (źródło pierwotne, pobrane ponownie)

**Akty prawne (API ELI i PDF Dz.U.)**
* **Dz.U. 2020 poz. 1609:** „akt posiada tekst jednolity”. T.j. to Dz.U. 2022 poz. 1679. Akty zmieniające: 2021/1169,
  2021/2280, 2023/2405 (w mocy od 2024-04-01, zmieniony przez 2024/473) i 2026/597 (w mocy od 2026-05-19).
* **T.j. 2022/1679**, brzmienie zgodne z plikiem:
  * § 2, § 2a (A4), § 2b ust. 1–4 (PDF, wektor, 150 MB);
  * § 5a, § 6 ust. 1–3, § 7 ust. 2 i 4a;
  * § 9 ust. 1–5 (zał. 2 „lub inne objaśnione w legendzie”; 1:200/1:100; PZT ≥ 1:500);
  * § 10 ust. 1–2, § 12, § 15 ust. 1, 1a i 2, § 21 pkt 1;
  * zał. nr 1 (PZT_z … PAB_ZL_z; AR/BO/IS/IE/BT/IN/WB; rrrr.mm.dd);
  * zał. nr 2 (12 norm, dopisek „Stosuje się najnowszą normę opublikowaną w języku polskim”).
* **Dz.U. 2023 poz. 2405:**
  * § 14 pkt 4 lit. a z dopiskiem „oraz loggie”;
  * § 20 ust. 1 pkt 4 lit. b, tiret 5 (pow. całkowita pomniejszona o tarasy, balkony i loggie);
  * § 20 ust. 1 pkt 4 lit. b: progi 2,20 m (100 %) i 1,40 m (50 %).
* **Dz.U. 2026 poz. 597** (MFiG, 27.04.2026, ogłoszony 4.05.2026):
  * § 15 ust. 3 (0,01 m; pełne metry z 1 miejscem po przecinku);
  * § 2 ust. 2 (przepis przejściowy);
  * § 3 (14 dni; § 1 pkt 3 lit. b i pkt 4 lit. a po 6 miesiącach).
* **PB t.j. Dz.U. 2026 poz. 524:** art. 20 ust. 2–3 pkt 2 brzmi dosłownie jak w pliku. Późniejsze zmiany (2026/605 art. 64;
  2026/646 art. 33) nie dotyczą art. 20.
* **WT t.j. Dz.U. 2022 poz. 1225:** § 9 ust. 1 potwierdzony w tekście aktu. Status WT nadal do potwierdzenia przez R3.

**Katalog PKN (własne zapytania 2026-09-25)**

| Norma | Stan w katalogu PKN |
|---|---|
| PN-EN ISO 7519:2024-09 | wycofana **2026-04-16**, brak „zastąpiona przez”; wprowadza EN ISO 7519:2024 |
| PN-EN ISO 128-2:2023-05 | aktualna (EN ISO 128-2:2022) |
| PN-ISO 128-23:2002 | wycofana 2021-02-04 → PN-EN ISO 128-2:2021-02 |
| PN-EN ISO 128-3:2023-02 | aktualna (ISO 128-3:2022) |
| PN-ISO 9836:2022-07 | aktualna (zatw. 2022-05-24, publ. 2022-07-18, IDT ISO 9836:2017) |
| PN-ISO 9836:2015-12 | wycofana 2022-07-18 |
| PN-EN 60617-11:2004 | wycofana **2005-12-01**, bez następcy |
| PN-B-01701:1984 | wycofana 2006-10-09, bez następcy |
| PN-B-01410:1989 | wycofana 2015-08-25; tytuł zgodny z plikiem |
| PN-B-01440:1998 | wycofana 2014-10-16 |
| PN-EN ISO 3098-0:2002 | wycofana 2015-06-30 → PN-EN ISO 3098-1:2015-06 (EN) |
| PN-EN ISO 3098-2, -4, -5:2002 | aktualne |
| PN-EN ISO 4066:2001 | wycofana → PN-EN ISO 3766:2006 (aktualna) |
| PN-EN ISO 6284:2024-06 (EN) | aktualna |
| PN-EN ISO 6284:2001 (pol.) | wycofana 2024-06-28 |
| PN-EN ISO 2553:2019-06 | aktualna, jest wersja polska |
| PN-B-01025:2004, B-01027:2002, B-01029:2000 (8 s.), B-01030:2000 (3 s.) | aktualne; daty zgodne z plikiem |
| PN-EN ISO 11091:2001, 4157-1/-2/-3:2001 | aktualne |
| PN-EN ISO 5457:2002 | aktualna; na karcie normy powiązane PN-EN ISO 5457:2002/A1:2010 (EN) |
| PN-EN ISO 7200:2007, 9431:2011 (EN) | aktualne |
| PN-EN 12792:2006, PN-EN 1861:2001, PN-B-01700:1999 | aktualne |
| PN-EN ISO 6412-1:2018-03 | aktualna |
| PN-EN ISO 128-1:2020-12, 8560:2019-06 | aktualne |
| PN-ISO 4068:1998 | wycofana 2005-06-21, bez następcy |
| PN-N-01603:1986 | wycofana 2011-10-10, bez następcy |

Komunikat PKN (KT 232) potwierdza, że stałe ściany działowe wlicza się do powierzchni konstrukcji. Potwierdza też, że wycofanie
normy nie oznacza zakazu jej stosowania (jeśli strony tak uzgodnią).

**Teksty norm ISO (podglądy iTeh, pobrane ponownie)**
* **ISO 128-2:2022:** 5.1 (szereg d, 4:2:1), 5.2 (±0,1d), tabl. 4 (≤ d, 3d, 6d, 12d, ≈24d, 18d), 6.1 (0,7 mm) i 6.2.1.
* **ISO 128-23:1999:** tabl. 1 (zastosowania 01.1–07.1, zgodne z R4-C08) i tabl. 2 (grupy linii, zgodne z R4-C07).
* **ISO 5457:1999:**
  * tabl. 1 (formaty i pola rysunkowe) i tabl. 2 (24×16 … 6×4);
  * 4.1 (A0–A3 poziomo, A4 pionowo);
  * 4.2 (marginesy 20/10 mm, ramka 0,7);
  * 4.3 (znaki centrujące: 0,7 mm, +10 mm);
  * 4.4 (pola 50 mm, 3,5 mm, bez I i O, linie 0,35);
  * 4.5 (znaczniki obcięcia 10×5 mm).
* **ISO 7200:2004:** szerokość 180 mm (A4, marginesy 20/10), tabl. 1–3 (pola M/O i liczby znaków).
* **ISO 9431:1990:** pole tekstu max 170 / min 100 mm.
* **ISO 3098-1:2015:** 4.2 (odstęp 2d), 5.4 (75°), 5.5 (B i CB zalecane).
* **ISO 5455:1979:** 4.1–4.2.
* **ISO 4157-1:1998:** 7.2 (kondygnacje od 1, „0” pod spodem), 7.4, 7.5 (C201/S201/W201/B201).
* **ISO 4157-2:1998:** 4.3 (podkreślanie), 4.4.1–4.4.3 (101–199, „ROOM 0”, zakaz interpunkcji numerów 4-cyfrowych),
  4.5.1 (zgodnie z ruchem wskazówek zegara).
* **ISO 3766:2003:** tabl. 1:
  * poz. 13: siatka w przekroju linią punktową b. grubą;
  * poz. 16–17: B/T/N/F/1/2, warstwa dolna lub dalsza linią kreskową b. grubą.
* **ISO 128-3:2022:** 6.2.2–6.2.3.
* **ISO 9836:2017:** 5.1.1.2 (m² z 2 miejscami), 5.1.2 (wyłączenia: schody i rampy zewnętrzne, daszki, osłony, okapy),
  5.1.3.
* **ISO 5261:1995:** rozdz. 4 i przykład „L 89 × 60 × 7 – 500”.
* **ISO 7519:2025** (3. wyd., 2025-02, „minor revision” ISO 7519:2024): 4.1.2–4.1.3 i 4.4–4.5 zgodne z R4-B13 i R4-H18.

**Źródła wtórne (pobrane ponownie, odczyt obrazów tablic)**
* **PN-B-01027:2002 wg [AGH-Z]:**
  * poz. 1.6 (1,4 / 0,7 / > 1,0 m), 1.7 (trójkąt 4 mm, 0,35), 1.8 („0,00=267,50”, „IV+P”, 2,5 mm);
  * poz. 2.1–2.2 (0,35, trójkąty 2 mm, 12·2·12), 2.3–2.5, 2.6 (0,5; 6·2·6), 2.7 (0,35, punkty 1,0, 5·1·5);
  * poz. 4.1 (0,18, 2,5 mm, „//” 0,25, przykład 20,67 / 9,16 / 6,0 / 4,0);
  * poz. 6.1–6.5 (Ks/Kd 0,7 z trójkątem 3 mm, wpust 4×2 mm, osadnik 7×4 mm, wodociąg 0,5);
  * poz. 6.9–6.13 (lampa Ø5 i Ø2 mm; gaz 0,7, 3·10·3; „e” 0,7, 2·9·2; „t” 0,5, 4·9·4; „c” 2 × 0,5 co 2 mm).
* **PN-B-01025 wg [AGH-P]:** rzut ok. 1 m nad podłogą; rzędne w m z 3 miejscami (w praktyce 2); grot zera 90°
  w połowie zaczerniony; kondygnacja przy terenie = 1, podziemne z „–”; numer pomieszczenia poprzedzony numerem kondygnacji,
  zgodnie z ruchem wskazówek zegara; wejścia (zaczernione / niewypełnione); kanały (wentylacyjny, spalinowy, dymowy).
* **PN-B-01029 wg [AGH-W]:** ukośne kreski 45°; ułamek szer./wys. na osi otworu; parapet w nawiasie przed wysokością,
  liczony od podłogi wykończonej; kanały 140×140 mm nie są wymiarowane.
* **[PCEZ]:** ograniczniki 45°; pierwsza linia ok. 10 mm, kolejne co 7–8 mm; liczby ok. 1 mm nad linią, ≥ 2 mm;
  „ARIAL CE, szerokość 0,8 (wg PN-B-01025:2004)”.

### 5.2 Poprawione (było → jest)

| ID | Było | Jest | Źródło |
|---|---|---|---|
| R4-A17 | „§ 15 ust. 2 pkt 1–14”; odsyłacz do pkt 3.12 | pkt 1–15 (pkt 15 dodany przez Dz.U. 2026 poz. 597, w mocy od 2026-05-19; obiekty zbiorowej ochrony, nie dotyczy LAMELI); odsyłacz do pkt 3.11 (PZT) | https://api.sejm.gov.pl/eli/acts/DU/2026/597/text.pdf |
| R4-B13, R4-H18, R4-K01 | „ISO/FDIS 7519:2024 (= ISO 7519:2025)”, URL projektu FDIS | ISO 7519:2025 (3. wyd., 2025-02). ISO 7519:2024 to odrębne 2. wyd., wprowadzone przez wycofaną PN-EN ISO 7519:2024-09. Wyd. 2025 zmieniło klucz 2 rys. 1 (granica terenu) z 04.2 na 04.3 | https://cdn.standards.iteh.ai/samples/89718/3807035b2f954bc98668456e679dc0ce/ISO-7519-2025.pdf |
| R4-F15 | § 9 WT z cytatu wtórnego (IARP), „NIE” | cytat z tekstu aktu (TAK-A) + § 9 ust. 2–3 (odległości mierzone w poziomie, w miejscu najmniejszego oddalenia; ważne dla PZT) | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf |
| R4-B08 | „Litery I i O nie służą jako indeks zmian” | „należy unikać” liter I i O (ISO 7200 5.1.4: „should be avoided”) | https://cdn.standards.iteh.ai/samples/35446/d3b0887cb4fa47f49f8718807d3b8903/ISO-7200-2004.pdf |
| pkt 3.9, R4-J03, pkt 4.3 | kolizja numeracji wywodzona z PN-B-01025 **i** ISO 4157-1 7.2 | ISO 4157-1 7.2 dotyczy kondygnacji i identyfikatorów (ISO 4157-3). Numery pomieszczeń opierają się na krajowej numeracji pięter (7.4.2, dopuszcza G01), więc kolizja wynika tylko z PN-B-01025 (wtórnie). Format „1.01” odbiega od zalecanego „101” (4.4.1), więc trzeba go objaśnić w legendzie | https://cdn.standards.iteh.ai/samples/26189/0ee2760f255344578079c1b0fd8f9a3e/ISO-4157-1-1998.pdf |
| Streszczenie pkt 3 | „PB (t.j. Dz.U. 2026 poz. 524)” | „t.j. Dz.U. 2026 poz. 524 ze zm.” (poz. 605 i 646 nie zmieniają art. 20) | https://api.sejm.gov.pl/eli/acts/DU/2026/524 |
| R4-A18, pkt 4.13 | data „ok. 5.11.2026” do potwierdzenia | ELI nie ma odrębnej daty; wyliczenie 5.11.2026 sprawdzone i uznane za prawidłowe | https://api.sejm.gov.pl/eli/acts/DU/2026/597 |

Uzupełnienia bez zmiany ustaleń:
* **R4-M04:** symbol c) dotyczy przewieszeń **> 1,0 m**. Wspornik ≤ 1,0 m można pominąć albo pokazać jako „obrys wyższych
  kondygnacji” (d).
* **R4-M06:** wzór normy to „0,00=267,50”, bez „±”.
* **R4-M07:** nazwa poz. 2.2 w normie to „Maksymalna nieprzekraczalna linia zabudowy”.

### 5.3 Niemożliwe do weryfikacji (dostęp płatny lub brak podglądu)
* **ISO 128-2:2022 zał. B** (linie w budownictwie): podgląd kończy się przed załącznikiem, więc tożsamość z ISO 128-23
  pozostaje NIEZWERYFIKOWANA.
* **Tekst PN-B-01025:2004** (pkt 2.3, 2.5, 3.2, 3.4, 3.5), **PN-B-01029:2000** i **PN-B-01030:2000**: dostępne tylko
  reprodukcje wtórne. Nie da się sprawdzić odstępów kreskowań ani zalecenia „Arial CE 0,8” w oryginale.
* **Treść PN-EN ISO 5457:2002/A1:2010** (A4 poziomo): potwierdzono tylko istnienie zmiany w katalogu PKN.
* **Numery symboli IEC 60617** (R4-N02) oraz kształty symboli PN-EN 12792, PN-EN 1861 i PN-EN ISO 6412: brak dostępu.
* **Próg 1,90 m** i szczegóły kubatury 5.2.2–5.2.4 w PN-ISO 9836:2022-07: poza podglądem ISO 9836:2017.
* Kolory rodzajów powietrza wg EN 16798-3 (R4-O04) i zasady PN-70/B-02365 (R4-P08): tylko źródła wtórne, nie sprawdzano
  ponownie.
