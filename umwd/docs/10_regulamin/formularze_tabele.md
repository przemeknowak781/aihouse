# Formularze konkursowe: F.11, F.13, F.14.A/B, F.15.A/B/C, F.16 – struktura i sposób wypełnienia

**Konkurs SARP nr 1089 – UMWD Wrocław** · stan: 2026-11-16

**Źródła:**
- edytowalne wzory: `00_materialy/_rozpak/4.Zalaczniki_Formalne_F.03-F.16_edytowalne/` (xlsx odczytane przez openpyxl: komórki, formuły, wypełnienia);
- PDF: `00_materialy/_rozpak/3.Zalaczniki_Formalne_F.01-F.17_PDF/`;
- tekst: `00_materialy/tekst/F.1*.txt`;
- Regulamin (tekst jednolity z 13.02.2026): `tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt`, w skrócie „Reg.”;
- wyjaśnienia: „Wyj. N odp. K”, zob. `wyjasnienia_streszczenie.md`.

Uwagi własne oznaczono jako *wniosek*.

## 1. Zestawienie formularzy według etapu

| Formularz | Etap | Gdzie się go składa | Podstawa |
|---|---|---|---|
| F.10 Pokwitowanie złożenia opracowania studialnego | I | w otwartej kopercie przy postaci fizycznej | Reg. R.V ust.3 |
| F.11 Karta identyfikacyjna opracowania studialnego | I | jako PDF z kwalifikowanym podpisem elektronicznym (KPE) | Reg. R.V ust.2 pkt1 lit.c, pkt4; s.32, 34–35 |
| F.14.A Wstępna informacja o kosztach | I | w części opisowej (PDF) i jako xlsx | Reg. R.V ust.2 pkt3 lit.d, s.34: „Opracowanie niezawierające powyższych informacji […] nie będzie podlegała ocenie” |
| F.12 Pokwitowanie złożenia pracy konkursowej | II | w otwartej kopercie, zaadresowanej na adres inny niż adres Uczestnika | Reg. R.VII ust.3 pkt7, s.48 |
| F.13 Karta identyfikacyjna pracy konkursowej | II | jako PDF z KPE, jedyny podpisany element | Reg. R.VII ust.2 pkt4, s.45; ust.3 pkt2 lit.c, s.46 |
| F.14.B Informacja o kosztach realizacji i kosztach Dokumentacji | II | w części opisowej (PDF, zeszyt A3) i jako xlsx | Reg. R.VII ust.2 pkt3 lit.f, s.45: „Praca niezawierająca powyższych informacji (lit. f)) nie będzie podlegała ocenie.” |
| F.15.A Tabela programowa | II | w części opisowej i jako xlsx | Reg. R.VII ust.2 pkt3 lit.c; ust.3 pkt2 lit.b |
| F.15.B Zestawienie pomieszczeń | II | j.w. | Reg. R.VII ust.2 pkt3 lit.d |
| F.15.C Dane bilansowe | II | j.w. | Reg. R.VII ust.2 pkt3 lit.e |
| F.16 Układ plansz | I | sugerowany, nieobowiązkowy | Reg. R.V ust.2 pkt1 lit.a; Wyj. 8 odp. 43, 55 |
| F.17.A/B Zdjęcia lotnicze | I + II | podkład wizualizacji nr 1 i nr 2 | zob. `zdjecia_F17_metadane.md` |

**Niespójność nazw.** Reg. R.VII ust.2 pkt1 lit.b (s.42) nazywa F.15.A–C kolejno „tabela programowa budynku, tabela parametrów budynku oraz tabela bilansu terenu”. Ta sama sekcja, pkt 3 lit.c–e (s.44), a także same wzory używają nazw „Tabela programowa / Zestawienie pomieszczeń / Dane bilansowe”. Merytorycznie „parametry budynku” i „bilans terenu” znajdują się razem w F.15.C, a F.15.B to zestawienie pomieszczeń. *Wniosek:* obowiązuje treść wzorów.

**Forma elektroniczna** (Reg. R.VII ust.3 pkt2 lit.b, s.46): „jeden plik w formacie PDF z częścią opisową uwzględniający wszystkie elementy […] oraz tabele w formacie xlsx, przygotowane na wzorze, stanowiącym Załączniki F.14.A-B - F.15.A-C”. Tabele trzeba więc złożyć **dwa razy**: w PDF opisu i jako osobne xlsx na wzorze. Pliki nie mogą zawierać numeru identyfikacyjnego ani metadanych autora. W xlsx trzeba wyczyścić pola Autor, Firma i Ostatnio modyfikowane przez (Reg. R.VII ust.3 pkt4 lit.c–d, s.47).

## 2. F.14.B – Informacja o szacowanych kosztach realizacji Inwestycji oraz kosztach wykonania Przedmiotu usługi (Etap II)

### 2.1. Układ arkusza

- Plik: `F.14.B_Informacja o kosztach - ETAP II.xlsx`, arkusz „F.14.B”, zakres A1:L164.
- Nagłówek: tytuł konkursu (B2), tytuł tabeli (B3), „Załącznik nr F.14.B do Regulaminu Konkursu” (B4).

| Kolumna | B | C | D | E | F | G | H |
|---|---|---|---|---|---|---|---|
| Nagłówek (wiersz 6) | „L.p.” | „Opis” | „Ilość” | „J.m.” | „Wartość [netto]” | „VAT” (format %) | „Wartość [brutto]” |
| Zawartość | numer | nazwa pozycji | **pusta, do uzupełnienia** | wstępnie wpisana | **pusta, do uzupełnienia** | stawka wstępnie wpisana | **pusta**: w wierszach szczegółowych nie ma formuły |

**Brak kolumny ceny jednostkowej.** „Wartość [netto]” to wartość całej pozycji.
- *Wniosek:* cenę jednostkową dokładamy w kolumnie pomocniczej poza drukowanym obszarem (np. J), a F wyliczamy jako D × cena. Kolumna J ma we wzorze ustawioną szerokość (30,9), ale jest pusta.

**Wiersze grup (szare)** sumują wiersze szczegółowe formułą `=SUM(...)` w kolumnach F i H. Uwaga we wzorze (B160): „W pozycjach zaznaczonych na szaro należy wpisać kwotę sumaryczną wynikającą z pozycji zaznaczonych na biało. *w razie potrzeby wstawić odpowiednią liczbę wierszy i kontynuować numerowanie”.

### 2.2. Pełna lista pozycji (wszystkie wiersze wzoru xlsx)

Tabelę wygenerowano skryptem z pliku xlsx. Literówki pochodzą ze wzoru i zostawiono je dosłownie [sic]:
- „Izoalcja” (3.2);
- „Agergat” (8.15);
- „eleketrycznych” (15.9);
- „Przylącze” (2.1–2.5);
- „Pochwyt ścienny (klatki schodowy)” (14.2).

W wersji PDF wzoru (`tekst/F.14.B_…txt`) pozycje są identyczne. Pozycje 5.2, 8.17 i 2.12/2.13 mają tam również puste pole VAT. Kolumna „Wiersz” to numer wiersza w arkuszu.

| Wiersz | L.p. | Opis (dosłownie) | J.m. | VAT | Uwagi |
|---|---|---|---|---|---|
| 7 | 1 | **ROBOTY PRZYGOTOWAWCZE** | kpl |  | netto `=SUM(F8:F13)`, brutto `=SUM(H8:H13)` |
| 8 | 1.1 | Przygotowanie i zabezpieczenie placu budowy (ogrodzenie, wycinka drzew) | kpl | 23% |  |
| 9 | 1.2 | Zdjęcie humusu | m3 | 23% |  |
| 10 | 1.3 | Odwodnienie i zabezpieczenie wykopu | kpl | 23% |  |
| 11 | 1.4 | Wykop pod budynek | m3 | 23% |  |
| 12 | 1.5 | Wymiana gruntów | m3 | 23% |  |
| 13 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 14 | 2 | **PRZYŁĄCZA I INSTALACJE ZEWNĘTRZNE** | kpl |  | netto `=SUM(F15:F28)`, brutto `=SUM(H15:H28)` |
| 15 | 2.1 | Przylącze ciepłownicze | kpl | 23% |  |
| 16 | 2.2 | Przylącze wodociągowe | kpl | 23% |  |
| 17 | 2.3 | Przylącze kanalizacyjne | kpl | 23% |  |
| 18 | 2.4 | Przylącze energetyczne | kpl | 23% |  |
| 19 | 2.5 | Przylącze telekomunikacyjne | kpl | 23% |  |
| 20 | 2.6 | Kanalizacja sanitarna wraz z urządzeniami | kpl | 23% |  |
| 21 | 2.7 | Kanalizacja deszczowa wraz z urządzeniami | kpl | 23% |  |
| 22 | 2.8 | Instalacja wodociągowa (zewnętrzna) | kpl | 23% |  |
| 23 | 2.9 | Instalacja ciepłownicza (zewnętrzna) | kpl | 23% |  |
| 24 | 2.10 | Instalacja elektryczna (zewnętrzna) | kpl | 23% |  |
| 25 | 2.11 | Rezerwowe źródło wody | kpl | 23% |  |
| 26 | 2.12 | System zasilania w ciepło i chłód w oparciu o pompy ciepła |  | — | brak j.m.; brak stawki VAT |
| 27 | 2.13 | System zasilania w energię elektryczną z paneli fotowoltaicznych |  | — | brak j.m.; brak stawki VAT |
| 28 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 29 | 3 | **KONSTRUKCJA BUDYNKU** | kpl |  | netto `=SUM(F30:F42)`, brutto `=SUM(H30:H42)` |
| 30 | 3.1 | Płyta fundamentowa | m3 | 23% |  |
| 31 | 3.2 | Izoalcja termiczna i przeciwwodna garażu podziemnego | m2 | 23% |  |
| 32 | 3.3 | Ściany żelbetowe | m2 | 23% |  |
| 33 | 3.4 | Słupy  żelbetowe | m3 | 23% |  |
| 34 | 3.5 | Ściany murowane | m2 | 23% |  |
| 35 | 3.6 | Stropy żelbetowe | m2 | 23% |  |
| 36 | 3.7 | Stropodach | m2 | 23% |  |
| 37 | 3.8 | Schody prefabrykowane + spoczniki | kpl | 23% |  |
| 38 | 3.9 | Konstrukcje stalowe | kg | 23% |  |
| 39 | 3.10 | Ocieplenia ścian i sufitów wewnętrznych | m2 | 23% |  |
| 40 | 3.11 | Izolacje termiczne oraz przeciwwodne dachu | m2 | 23% |  |
| 41 | 3.12 | Dach zielony (izolacje termiczne oraz przeciwwodne) | m2 | 23% |  |
| 42 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 43 | 4 | **STOLARKA ZEWNĘTRZNA** | kpl |  | netto `=SUM(F44:F48)`, brutto `=SUM(H44:H48)` |
| 44 | 4.1 | Stolarka okienna (zewnętrzna) | m2 | 23% |  |
| 45 | 4.2 | Stolarka drzwiowa (zewnętrzna) | m2 | 23% |  |
| 46 | 4.3 | Świetliki dachowe | m2 | 23% |  |
| 47 | 4.4 | Klapy dymowe | m2 | 23% |  |
| 48 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 49 | 5 | **STOLARKA WEWNĘTRZNA** | kpl |  | netto `=SUM(F50:F53)`, brutto `=SUM(H50:H53)` |
| 50 | 5.1 | Drzwi wewnętrzne | szt. | 23% |  |
| 51 | 5.2 | Stolarka drzwiowa przeciwpożarowa | szt. | — | brak stawki VAT |
| 52 | 5.3 | Stolarka okienna wewnętrzna | m2 | 23% |  |
| 53 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 54 | 6 | **ELEWACJA** | kpl |  | netto `=SUM(F55:F58)`, brutto `=SUM(H55:H58)` |
| 55 | 6.1 | Elewacja systemowa z okładziną (izolacja termiczna, podkonstrukcja, płyty) | m2 | 23% |  |
| 56 | 6.2 | Izolacja termiczna + tynk elewacyjny | m2 | 23% |  |
| 57 | 6.3 | Stałe przesłony światła, lamele przyokienne | m2 | 23% |  |
| 58 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 59 | 7 | **INSTALACJE SANITARNE** | kpl |  | netto `=SUM(F60:F69)`, brutto `=SUM(H60:H69)` |
| 60 | 7.1 | Instalacje wodociągowe wody wodociągowej i wody szarej | kpl | 23% |  |
| 61 | 7.2 | Instalacje ppoż | kpl | 23% |  |
| 62 | 7.3 | Instalacje kanalizacyjne ścieków czarnych i ścieków szarych | kpl | 23% |  |
| 63 | 7.4 | Instalacje CO | kpl | 23% |  |
| 64 | 7.5 | Węzeł cieplny | kpl | 23% |  |
| 65 | 7.6 | Wentylacja mechaniczna z centralami | kpl | 23% |  |
| 66 | 7.7 | Wentylacja chłodnicza | kpl | 23% |  |
| 67 | 7.8 | Instalacja doprowadzenia ciepła i chłodu z pomp ciepła | kpl | 8% | VAT 8% (do weryfikacji) |
| 68 | 7.9 | magazyny energii cieplnej |  | — | brak j.m.; brak stawki VAT |
| 69 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 70 | 8 | **INSTALACJE ELEKTRYCZNE** | kpl |  | netto `=SUM(F71:F88)`, brutto `=SUM(H71:H88)` |
| 71 | 8.1 | Tablice rozdzielcze | kpl | 23% |  |
| 72 | 8.2 | Trasy kablowe | kpl | 23% |  |
| 73 | 8.3 | Instalacja oświetlenia podstawowego | kpl | 23% |  |
| 74 | 8.4 | Instalacja oświetlenia awaryjnego i ewakuacyjnego | kpl | 23% |  |
| 75 | 8.5 | Instalacja oświetlenia rezerwowego | kpl | 23% |  |
| 76 | 8.6 | Instalacja oświetlenia nocnego | kpl | 23% |  |
| 77 | 8.7 | Instalacja ppoż | kpl | 23% |  |
| 78 | 8.8 | Instalacja gniazd wtykowych | kpl | 23% |  |
| 79 | 8.9 | Instalacja siłowa | kpl | 23% |  |
| 80 | 8.10 | Instalacja odgromowa i uziemiająca | kpl | 23% |  |
| 81 | 8.11 | Serwerownia | kpl | 23% |  |
| 82 | 8.12 | System SMS | kpl | 23% |  |
| 83 | 8.13 | System BMS | kpl | 23% |  |
| 84 | 8.14 | Instalacja wzmocnienia sygnału GSM | kpl | 23% |  |
| 85 | 8.15 | Agergat prądotworczy | kpl | 23% |  |
| 86 | 8.16 | UPS | kpl | 23% |  |
| 87 | 8.17 | Instalacja zasilania z paneli fotowoltaicznych wraz z magazynem energii | kpl | — | brak stawki VAT |
| 88 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 89 | 9 | **INSTALACJE TELETECHNICZNE** | kpl |  | netto `=SUM(F90:F102)`, brutto `=SUM(H90:H102)` |
| 90 | 9.1 | Instalacja okablowania strukturalnego LAN | kpl | 23% |  |
| 91 | 9.2 | Instalacja kontroli dostępu | kpl | 23% |  |
| 92 | 9.3 | Instalacja systemu sygnalizacji napadu i włamania SSWiN | kpl | 23% |  |
| 93 | 9.4 | Instalacja telewizji dozorowej | kpl | 23% |  |
| 94 | 9.5 | Instalacja systemu przyzywowego | kpl | 23% |  |
| 95 | 9.6 | Instalacja SSP | kpl | 23% |  |
| 96 | 9.7 | Instalacja DSO | kpl | 23% |  |
| 97 | 9.8 | Instalacja światłowodowa | kpl | 23% |  |
| 98 | 9.9 | Instalacja telefoniczna | kpl | 23% |  |
| 99 | 9.10 | Instalacja AV audytoriów | kpl | 23% |  |
| 100 | 9.11 | System integrujący i wizualizacyjny | kpl | 23% |  |
| 101 | 9.12 | Instalacja oddymiania i napowietrzania klatek schodowych | kpl | 23% |  |
| 102 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 103 | 10 | **WINDY** | kpl |  | netto `=SUM(F104:F106)`, brutto `=SUM(H104:H106)` |
| 104 | 10.1 | Winda osobowa | szt. | 23% |  |
| 105 | 10.2 | Winda towarowa | szt. | 23% |  |
| 106 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 107 | 11 | **ROBOTY WYKOŃCZENIOWE** | kpl |  | netto `=SUM(F108:F117)`, brutto `=SUM(H108:H117)` |
| 108 | 11.1 | Tynki | m2 | 23% |  |
| 109 | 11.2 | Ścianki działowe GK | m2 | 23% |  |
| 110 | 11.3 | Ścianki działowe (np. HPL) | m2 | 23% |  |
| 111 | 11.4 | Ścianki mobilne | m2 | 23% |  |
| 112 | 11.5 | Ścianki działowe szklane | m2 | 23% |  |
| 113 | 11.6 | Płytki ceramiczne | m2 | 23% |  |
| 114 | 11.7 | Roboty malarskie | m2 | 23% |  |
| 115 | 11.8 | Okładziny ścienne | m2 | 23% |  |
| 116 | 11.9 | Wyposażenie stałe | kpl | 23% |  |
| 117 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 118 | 12 | **SUFITY** | kpl |  | netto `=SUM(F119:F122)`, brutto `=SUM(H119:H122)` |
| 119 | 12.1 | Sufit podwieszany modułowy | m2 | 23% |  |
| 120 | 12.2 | Sufit pełny GK | m2 | 23% |  |
| 121 | 12.3 | Sufit podwieszany akustyczny | m2 | 23% |  |
| 122 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 123 | 13 | **PODŁOGI** | kpl |  | netto `=SUM(F124:F131)`, brutto `=SUM(H124:H131)` |
| 124 | 13.1 | Warstwy podposadzkowe (izolacje+wylewki) | m2 | 23% |  |
| 125 | 13.2 | Płytki ceramiczne klatek schodowych | m2 | 23% |  |
| 126 | 13.3 | Płytki ceramiczne lub PCV antypoślizgowe | m2 | 23% |  |
| 127 | 13.4 | Posadzka przemysłowa żywiczna | m2 | 23% |  |
| 128 | 13.5 | Posadzka przemysłowa żywiczna - garaż podziemny | m2 | 23% |  |
| 129 | 13.6 | Wykładzina PCV | m2 | 23% |  |
| 130 | 13.7 | Wykładzina PCV - odporna na działanie środków chemicznych | m2 | 23% |  |
| 131 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 132 | 14 | **BALUSTRADY** | kpl |  | netto `=SUM(F133:F138)`, brutto `=SUM(H133:H138)` |
| 133 | 14.1 | Balustrada schodowa na klatkach schodowych | mb | 23% |  |
| 134 | 14.2 | Pochwyt ścienny (klatki schodowy) | mb | 23% |  |
| 135 | 14.3 | Balustrada zewnętrzna | mb | 23% |  |
| 136 | 14.4 | Balustrada wewnętrzna | mb | 23% |  |
| 137 | 14.5 | Pochwyt ścienny | mb | 23% |  |
| 138 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 139 | 15 | **ZAGOSPODAROWANIE TERENU** | kpl |  | netto `=SUM(F140:F150)`, brutto `=SUM(H140:H150)` |
| 140 | 15.1 | Roboty ziemne | m2 | 23% |  |
| 141 | 15.2 | Drogi wewnętrzne | m2 | 23% |  |
| 142 | 15.3 | Parkingi | m2 | 23% |  |
| 143 | 15.4 | Chodniki | m2 | 23% |  |
| 144 | 15.5 | Ogrodzenie, bramy, furtki | mb | 23% |  |
| 145 | 15.6 | Mała architektura (ławki, kosze, stojaki rowerowe) | kpl | 23% |  |
| 146 | 15.7 | Zieleń (niska + wysoka) | kpl | 8% | VAT 8% (do weryfikacji) |
| 147 | 15.8 | Oświetlenie terenów zewnętrznych | kpl | 23% |  |
| 148 | 15.9 | Stacja ładowania pojazdów eleketrycznych | szt. | 23% |  |
| 149 | 15.10 | System retencji wód opadowych |  | — | brak j.m.; brak stawki VAT |
| 150 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 151 | 16 | **KOSZTY STAŁE BUDOWY** | kpl |  | netto `=SUM(F152:F153)`, brutto `=SUM(H152:H153)` |
| 152 | 16.1 | Koszty stałe budowy | kpl | 23% |  |
| 153 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 154 | 17 | **ROZWIĄZANIA PROEKOLOGICZNE I ENERGOOSZCZĘDNE** | kpl |  | netto `=SUM(F155:F156)`, brutto `=SUM(H155:H156)` |
| 155 | 17.1 | Rekuperacja ciepła |  | 23% | brak j.m. |
| 156 | ….* | inne (proszę wymienić) | kpl | 23% |  |
| 157 | 18 | **INNE KOSZTY MAJĄCE WPŁYW NA REALIZACJĘ INWESTYCJI** | kpl |  | netto `=SUM(F158)`, brutto `=SUM(H158)` |
| 158 | ….* | (proszę wymienić) | kpl | 23% |  |
| 159 | (wiersz sumy) | **Szacunkowy koszt realizacji Inwestycji w stanie umożliwiającym odbiór Inwestycji i dopuszczenie jej do użytkowania (suma dla wszystkich elementów składowych)** | kpl |  | netto `=F7+F14+F29+F43+F54+F59+F70+F89+F103+F107+F49+F118+F123+F132+F139+F151+F154+F157`; brutto analogicznie (kolumna H) |

**Wiersze końcowe:**
- B163: „Szacunkowy łączny koszt NETTO wykonania Przedmiotu usługi opisanej w Załączniku nr F.01 do Regulaminu (Umowa o prace projektowe)”, H163 `=F159`;
- B164: „Szacunkowy łączny koszt BRUTTO wykonania Przedmiotu usługi opisanej w Załączniku nr F.01 do Regulaminu (Umowa o prace projektowe)”, H164 `=H159`.

### 2.3. Błędy i pułapki wzoru F.14.B (krytyczne)

1. **BŁĄD WZORU.** Komórki kosztu prac projektowych (H163 netto, H164 brutto) mają formuły `=F159` i `=H159`. Pokazują więc **koszt realizacji Inwestycji, a nie koszt Dokumentacji**. Ten sam błąd jest w F.14.A (H32 `=F28`, H33 `=H28`). Zostawienie formuł oznaczałoby deklarację wynagrodzenia projektowego równego kosztowi budowy. Na wydruku PDF wzoru widać „0,00 zł”.
   - *Wniosek:* nadpisać obie komórki wartościami, czyli kosztem Dokumentacji wg F.01. Limit wynosi ≤ 5,4% z 150 mln = **8,1 mln zł netto** (Reg. R.III ust.4, s.20–21). W opisie (PDF) pokazać kalkulację.
2. **Brak formuł brutto w wierszach szczegółowych.** Kolumna H jest pusta, a sumy grup brutto (H7, H14, …) liczą puste komórki, więc wyjdzie 0 zł.
   - *Wniosek:* wpisać w H każdego wiersza szczegółowego `=F*(1+G)`.
3. **Pozycje bez j.m. lub bez stawki VAT:**
   - 2.12, 2.13 – brak j.m. i VAT;
   - 5.2 – brak VAT;
   - 7.9 – brak j.m. i VAT;
   - 8.17 – brak VAT;
   - 15.10 – brak j.m. i VAT;
   - 17.1 – brak j.m.
   Pozycje te trzeba uzupełnić.
4. **Stawka VAT 8%** jest wstępnie wpisana w 7.8 („Instalacja doprowadzenia ciepła i chłodu z pomp ciepła”) i w 15.7 („Zieleń”).
   - *Wniosek, do weryfikacji podatkowej:* obniżona stawka dla robót instalacyjnych dotyczy co do zasady budownictwa objętego społecznym programem mieszkaniowym, a ten budynek jest biurowy. 8% w 7.8 budzi wątpliwość. Dla usług zagospodarowania zieleni stawka 8% jest możliwa. Kwestię sygnalizujemy, ale stawek wzoru nie zmieniamy bez podstawy.
5. **Grupy F.14.A a F.14.B.** F.14.A ma 20 grup: „18 ZERO EMISYJNOŚĆ I PROPONOWANE SYSTEMOWE ROZWIĄZANIA PROEKOLOGICZNE”, „19 MAGAZYNY ENERGII ELEKTRYCZNEJ I CIEPLNEJ”, „20 INNE KOSZTY”. F.14.B ma 18 grup, a pozycje OZE i magazynów rozproszono: 2.12, 2.13, 7.8, 7.9, 8.17, 15.10 oraz grupa 17. *Wniosek:* w F.14.B dopisać w grupie 17 pozycje zbiorcze dla rozwiązań zeroemisyjnych (M.12) i podać odsyłacze, żeby uniknąć podwójnego liczenia.
6. **Wstawianie wierszy.** Wiersze „….* inne” leżą wewnątrz zakresów SUM. Wiersze wstawione nad nimi rozszerzą zakres, a wstawione pod nimi wypadną z sumy. Grupa 18 ma formułę `=SUM(F158)`, czyli jeden wiersz, i po dodaniu wierszy wymaga poprawki. W F.14.A suma `=SUM(F7:F26)` nie obejmuje wiersza 27 („…. (proszę wymienić)”).
7. **Koszty spoza tabeli.** Nie ma pozycji na wyposażenie ruchome, rezerwę ani prace przy sąsiadach (ekspertyzy, zabezpieczenia WS 5 i Mazowiecka 19; zamurowanie okien Maz. 19 wg F.01 zał. 3), nie ma też MDS (miejsca doraźnego schronienia). *Wniosek:* ująć je w grupie 18 „Inne koszty”.
8. **Limit 150 mln zł netto jest twardy** (Wyj. 20 odp. 74). Suma F159 musi być ≤ 150 000 000 zł netto i jednocześnie wiarygodna. Sąd oceni rzetelność, a sztuczne zaniżanie jest niedopuszczalne.

### 2.4. F.14.A (Etap I) – dla porządku

- Ta sama siatka kolumn B–H.
- 20 grup bez pozycji szczegółowych:
  1. Roboty przygotowawcze
  2. Przyłącza i instalacje zewnętrzne
  3. Konstrukcja budynku
  4. Stolarka zewnętrzna
  5. Stolarka wewnętrzna
  6. Elewacja
  7. Instalacje sanitarne
  8. Instalacje elektryczne
  9. Instalacje teletechniczne
  10. Windy
  11. Roboty wykończeniowe
  12. Sufity
  13. Podłogi
  14. Balustrady
  15. Zagospodarowanie terenu
  16. Koszty stałe budowy
  17. Rozwiązania proekologiczne i energooszczędne
  18. Zero emisyjność i proponowane systemowe rozwiązania proekologiczne (bez j.m.)
  19. Magazyny energii elektrycznej i cieplnej (bez j.m.)
  20. Inne koszty mające wpływ na realizację inwestycji
- Suma: F28 `=SUM(F7:F26)`.
- Uwaga o szarych polach jak w F.14.B.
- Ten sam błąd: H32 `=F28`, H33 `=H28`.

## 3. F.15.A – Tabela programowa (Etap II)

### 3.1. Układ

- Plik: `F.15.A_Tabela Programowa.xlsx`, arkusz „TABELA PROGRAMOWA”, zakres A2:I183.
- Kolumny (wiersz 6): **B „nr”**, **C „opis”**, **D „kond.”**, **E „pow. [m2]”**.
- Komórki numerów mają format tekstowy „@”.
- **We wzorze nie ma żadnej formuły**, także w wierszach „Razem”, i nie ma sumy całkowitej.
- Każda sekcja ma:
  - nagłówek (wypełnienie motywu 0);
  - wiersze kod.01, kod.02, kod.03, kod….;
  - opcjonalny wiersz „… *” z opisem „Inne np. komunikacja, sanitariaty (wymienić)”;
  - wiersz „Razem - … (kod)”.

### 3.2. Sekcje wzoru (dosłownie)

| Wiersze | Nagłówek sekcji (dosłownie) | Pozycje wzoru | Wiersz „Inne”? | Wiersz sumy (dosłownie) |
|---|---|---|---|---|
| 8–14 | Strefa Wejściowa - hol | SW.01, SW.02, SW.03, SW…. | tak | Razem -  Strefa wejściowa (SW) |
| 16–22 | Strefa konferencyjna | SK.01, SK.02, SK.03, SK…. | tak | Razem -  Strefa konferencyjna (SK) |
| 24–30 | Sejmik Województwa Dolnośląskiego | SWD.01, SWD.02, SWD.03, SWD…. | tak | Razem -  Sejmik Województwa Dolnośląskiego (SWD) |
| 32–38 | Kancelaria Sejmiku | KS.01, KS.02, KS.03, KS…. | tak | Razem -  Kancelaria Sejmiku (KS) |
| 40–46 | Departament Ochrony Środowiska (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 2) | DOS.01, DOS.02, DOS.03, DOS…. | tak | Razem -  Departament Ochrony Środowiska (DOS) |
| 48–54 | Departament Spraw Społecznych i Rynku Pracy (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 3) | DSS.01, DSS.02, DSS.03, DSS…. | tak | Razem -  Departament Spraw Społecznych i Rynku Pracy (DSS) |
| 56–62 | Departament Sportu i Turystyki (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 4) | DST.01, DST.02, DST.03, DST…. | tak | Razem -  Departament Sportu i Turystyki (DST) |
| 64–70 | Departament Rozwoju Aglomeracji (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 5) | DRA.01, DRA.02, DRA.03, DRA…. | tak | Razem -  Departament Rozwoju Aglomeracji  (DRA) |
| 72–78 | Departament Gospodarki i Promocji (wraz z komórkami organizacyjnymi oznaczonymi w załączniku do programu użytkowego cyfrą 6) | DGP.01, DGP.02, DGP.03, DGP…. | tak | Razem -  Departament Gospodarki i Promocji  (DGP) |
| 80–86 | Departament Infrastruktury (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 7) | DI.01, DI.02, DI.03, DI…. | tak | Razem -  Departament Infrastruktury  (DI) |
| 88–94 | Członek Zarzadu (oznaczony w załącziku programu użytkowego cyfrą 8) | CZ.01, CZ.02, CZ.03, CZ…. | tak | Razem -  Członek Zarzadu (CZ) |
| 96–102 | Departament Kultury i Dziedzictwa Kulturowego (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 8.1) | DKD.01, DKD.02, DKD.03, DKD…. | tak | Razem -  Departament Kultury i Dziedzictwa Kulturowego |
| 104–110 | Department Zdrowia (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 8.2) | DZ.01, DZ.02, DZ.03, DZ…. | tak | Razem -  Department Zdrowia (DZ) |
| 112–118 | Geodeta Województwa - Wydział Geodezji i Kartografii  (wraz z komórkami organizacyjnymi oznaczonymi w załączniku programu użytkowego cyfrą 9) | GW.01, GW.02, GW.03, GW…. | tak | Razem -  Geodeta Województwa - Wydział Geodezji i Kartografii (GW) |
| 120–126 | Dział Kancelaryjny II | DK.01, DK.02, DK.03, DK…. | tak | Razem -  Dział Kancelaryjny II (DK) |
| 128–134 | Dział Wsparcia Informatycznego II | DW.01, DW.02, DW.03, DW…. | tak | Razem -  Dział Wsparcia Informatycznego II (DW) |
| 136–141 | Sale narad | SN.01, SN.02, SN.03, SN…. | nie | Razem -  Sale narad (SN) |
| 143–148 | Pomieszczenia socjalne | PS.01, PS.02, PS.03, PS…. | nie | Razem -  Pomieszczenia socjalne (PS) |
| 150–155 | Pomieszczenia pomocnicze | PP.01, PP.02, PP.03, PP…. | nie | Razem -  Pomieszczenia pomocnicze (PP) |
| 157–162 | Pomieszczenia dla pracowników technicznych | PPT.01, PPT.02, PPT.03, PPT…. | nie | Razem -  Pomieszczenia dla pracowników technicznych (PPT) |
| 164–169 | Infrastruktura techniczna (w tym serwerownia) | IT.01, IT.02, IT.03, IT…. | nie | Razem -  Infrastruktura techniczna (IT) |
| 171–176 | Parking dla rowerów | PR.01, PR.02, PR.03, PR…. | nie | Razem -  Parking dla rowerów |
| 178–183 | Parking podziemny pełniący funkcję miejsca doraźnego schronienia | PPM.01, PPM.02, PPM.03, PPM…. | nie | Razem -  Parking podziemny pełniący funkcję miejsca doraźnego schronienia |

### 3.3. Sposób wypełnienia (Wyj. 20 odp. 73, Wyj. 21 odp. 80)

- **Numer** = kod grupy + numer kolejny, np. „DOS.01”, zgodny z numerem pomieszczenia na rzucie 1:200 (W-052, W-059).
  - *Wniosek:* w kolumnie „opis” podawać nazwę pomieszczenia i komórkę organizacyjną z tabeli M.01 (np. „pokój 3-os. – Wydział 2.3”). Pozwoli to sprawdzić zakaz łączenia komórek (W-008) i obowiązkowe 24 m² (W-009).
- **„kond.”** – oznaczenie kondygnacji, spójne z F.15.B (−1, 0/P, 1…).
- **Brakujące sekcje:** **PHS** (pomieszczenia higieniczno-sanitarne) i **KW** (komunikacja wewnętrzna) są w wykazie skrótów z odp. 73, ale wzór ich nie ma. Należy je dodać. Odp. 73 dopuszcza dodanie pozycji „wraz z pełną nazwą w tabeli F.15.A”.
- **Konflikt wzoru z odp. 73:** wiersze „Inne np. komunikacja, sanitariaty” w sekcjach. Według odp. 73 **cała** powierzchnia ruchu idzie do KW, z wyjątkiem SW i ruchu bezpośrednio związanego z salą. *Wniosek:* wiersze „Inne” wykorzystywać tylko do tych wyjątków, a sanitariaty przenieść do PHS.
- **Sumy:** dopisać formuły w wierszach „Razem” oraz wiersz „RAZEM BUDYNEK”. Sumy trzeba uzgodnić z F.15.B (RAZEM) i F.15.C (I.12 powierzchnia użytkowa). *Wniosek:* przy KW i IT rozróżnić p.u. od powierzchni ruchu i technicznej wg PN-ISO 9836 (zob. §6), bo inaczej I.12 nie zgodzi się z sumą F.15.A.
- **Parking podziemny (PPM)** pełni funkcję miejsca doraźnego schronienia (MDS) – tak brzmi nagłówek sekcji. Zgadza się to z F.01 zał. 3 pkt 2 ppkt 2 lit.b i pkt 3 ppkt 10. *Wniosek:* w opisie pokazać pojemność MDS.

## 4. F.15.B – Zestawienie pomieszczeń (Etap II)

- Plik: `F.15.B_Zestawienie pomiesczen.xlsx`, arkusz „ZESTAWIENIE POMIESZCZEŃ”, zakres A2:J58.
- Kolumny: **B „nr”**, **C–E (scalone) „opis”**, **F „pow. [m2]”**.
- Sekcje (dosłownie):
  - „KONDYGNACJA -1” (6 wierszy „… *”), „RAZEM KONDYGNACJA -1”;
  - „PARTER”, „RAZEM PARTER”;
  - „1 PIĘTRO” … „6 PIĘTRO” (każde z wierszem „RAZEM n PIĘTRO”);
  - „DACH”, „RAZEM DACH”;
  - „RAZEM ” (B56, zielone wypełnienie FF92D050).
- Przypis B58: „*uzupełnić o numer pomieszczenia zgodnie z częścią rysunkową pracy konkursowej”.
- **We wzorze nie ma formuł.**
- **Liczba kondygnacji we wzorze** (−1, P, 1–6, dach) odpowiada budynkowi P+6 z jedną kondygnacją podziemną. Przy dominancie 35–45 m (strefa A, W-027) potrzeba więcej pięter. *Wniosek:* wzór nie ogranicza liczby kondygnacji; sekcje trzeba dodać, co uprawnia przypis „*” z F.15.C. W PDF wzoru pod „RAZEM DACH” powtarza się nagłówek „KONDYGNACJA / -1”. To artefakt wydruku.
- **Sposób wypełnienia:** każde pomieszczenie (także KW, PHS, IT) z numerem identycznym jak na rzucie (W-059) i z powierzchnią wg PN-ISO 9836:2022-07 (W-052). Suma = suma F.15.A.

## 5. F.15.C – Dane bilansowe (Etap II)

Plik: `F.15.C_Dane_bilansowe.xlsx`, arkusz „DANE BILANSOWE”, zakres A2:J128. **We wzorze nie ma formuł.**

### 5.1. Część 1 – BILANS TERENU (kolumny B „nr”, C–E „opis”, F „pow. [m2]”)

| nr | opis (dosłownie) | jedn. |
|---|---|---|
| 1 | powierzchnia zabudowy | m² |
| 1.1 | - w tym powierzchnia zabudowy projektowana | m² |
| 1.2 | - w tym powierzchnia zabudowy istniejąca | m² |
| 2 | powierzchnia utwardzona | m² |
| 2.1 | - w tym drogi istniejące bez zmian | m² |
| 2.2 | - w tym drogi wewnętrzne | m² |
| 2.3 | - w tym miejsca parkingowe | m² |
| 2.4 | - w tym place | m² |
| 2.5 | - w tym chodniki | m² |
| 2.6 | - w tym inne powierzchnie utwardzone (określić) | m² |
| 3 | powierzchnia biologicznie czynna | m² |
| 3.1 | - w tym powierzchnia biologicznie czynna istniejąca bez zmian | m² |
| 3.2 | - w tym powierzchnia biologicznie czynna istniejąca do rekompozycji / zmiany | m² |
| 3.3 | - w tym powierzchnia biologicznie czynna projektowana na dachach / tarasach | m² |
| …* | inne (określić) | m² |
| RAZEM TEREN OPRACOWANIA | wartość „XXXX” (placeholder, format liczbowy #,##0.00) | m² |

### 5.2. Część 2 – PODSTAWOWE PARAMETRY (kolumny B „nr”, C–D „opis”, E „jednostka”, F „ilość”)

| nr | opis (dosłownie) | jednostka we wzorze |
|---|---|---|
| I.1 | powierzchnia zabudowy budynku administracyjnego UMWD | [m2] |
| I.2 | powierzchnia całkowita wszystkich kondygnacji (nadziemnych i podziemnych) | [m2] |
| I.3 | powierzchnia całkowita kondygnacji nadziemnych | [m2] |
| I.4 | powierzchnia całkowita kondygnacji podziemnych | [m2] |
| I.5 | liczba kondygnacji podziemnych | – |
| I.6 | liczba kondygnacji nadziemnych | – |
| I.7 | wysokość | [m] |
| I.8 | kubatura brutto | [m3] |
| I.9 | kubatura nadziemna brutto | **brak jednostki** (powinno być m³) |
| I.10 | kubatura podziemna brutto | [m3] |
| I.11 | liczba dźwigów osobowych w budynku | – |
| I.12 | powierzchnia użytkowa | [m2] |
| I.13 | powierzchnia dachów zielonych | [m2] |

Przypis (B41): „* W przypadku zaproponowania pomieszczeń lub elementów zagospodarowania wynikających z przedstawionej koncepcji Uczestnik konkursu powinien dodać do tabeli te pozycje.”

### 5.3. Sposób wypełnienia i pułapki

- **Teren odniesienia.** Według Wyj. 8 odp. 59 obliczenia, w tym bilans, prowadzi się dla **Obszaru inwestycji** z M.04 (W-041). Etykieta wzoru „RAZEM TEREN OPRACOWANIA” sugeruje jednak granicę opracowania konkursowego, która obejmuje też skwer na dz. 9/2 i dojazd 10/2.
  - *Wniosek:* wypełnić dla Obszaru inwestycji zgodnie z odp. 59 i wyraźnie to opisać. Opcjonalnie dodać pozycję „*” z bilansem dla granicy opracowania konkursowego.
- **Kontrola:** 1 + 2 + 3 = RAZEM. Pozycja 3.3 (PBC na dachach) nie leży na terenie, więc nie wchodzi do sumy powierzchni terenu. *Wniosek:* 3.3 wykazać informacyjnie, poza sumą (dopisek), aby bilans się zamykał.
- **I.7 wysokość** podawać wg MPZP: „wymiar pionowy budynku, mierzony od poziomu terenu” do najwyższego i najniższego punktu pokrycia dachu (Wyj. 8 odp. 57, § 26 ust. 2 pkt 3 MPZP). *Wniosek:* podać dwie wartości, dla dominanty i dla skrzydeł, oraz rzędną terenu. Pikiety M.02 mają 117,92–121,72 m n.p.m. (`M.02/model terenu/mazowiecka_pikiety do nmt.txt`, 800 punktów).
- **I.11** – ten sam wskaźnik wymaga F.01 zał. 3 pkt 2 ppkt 1 lit.g (analiza przepustowości dźwigów).
- **I.13 dachy zielone** – musi zgadzać się z poz. 3.12 w F.14.B (m²).

## 6. Definicje powierzchni i kubatury

1. **Obowiązująca norma:** „Obliczenia powierzchni należy prowadzić zgodnie z normą PN-ISO 9836:2022-07” (Wyj. 20 odp. 73). Normy nie ma w materiałach, a jej treść jest odpłatna.
   - Pełny tytuł: „Właściwości użytkowe w budownictwie – Określanie i obliczanie wskaźników powierzchniowych i kubaturowych”.
   - Źródło: interpretacja PKN z 29.12.2022, https://www.pkn.pl/interpretacje_pn/PN-ISO%209836_2022-07_zapytanie%201.pdf (dostęp 2026-11-16).
2. **Ściany działowe** (interpretacja PKN j.w., źródło oficjalne):
   - powierzchnia zajęta przez **stałe ściany działowe** należy do **powierzchni konstrukcji** (p. 5.1.6.1 normy);
   - powierzchnia pod **demontowalnymi ścianami typu przepierzenia** należy do **powierzchni netto** (p. 5.1.5.3).
   - *Wniosek:* systemowe ścianki szklane lub demontowalne między pokojami biurowymi liczą się do powierzchni netto, a pośrednio do p.u. Pomaga to dotrzymać 24 m² p.u. na pokój (W-009).
3. **Struktura wskaźników** – *wniosek na podstawie znajomości ISO 9836:2017, którą PN-ISO 9836:2022-07 wprowadza; treść wymaga weryfikacji w egzemplarzu normy:*
   - powierzchnia całkowita = powierzchnia netto + powierzchnia konstrukcji;
   - powierzchnia netto = powierzchnia użytkowa + powierzchnia usługowa (techniczna) + powierzchnia ruchu;
   - powierzchnia użytkowa dzieli się na podstawową i pomocniczą;
   - norma wyodrębnia ponadto powierzchnie o małej wysokości w świetle („nieużyteczne”) oraz kubaturę brutto.
   - Odniesienie do formularzy: KW (odp. 73) = **powierzchnia ruchu**; IT i serwerownia to głównie **powierzchnia usługowa**; F.15.C I.2–I.4 = powierzchnie całkowite; I.8–I.10 = kubatura brutto.
4. **Powierzchnia zabudowy i PBC** (F.15.C poz. 1 i 3, wskaźniki MPZP): stosować definicje z MPZP (M.03). Słowniczek MPZP (M.03, s. 3, pkt 11) definiuje „obszar zabudowy” jako obszar zajęty przez rzut na powierzchnię terenu kondygnacji naziemnych budynku w zewnętrznym obrysie ścian zewnętrznych. Tekst PDF MPZP jest częściowo nieczytelny (błąd kodowania fontów). Pełna analiza definicji MPZP należy do osobnego opracowania. *Wniosek:* dla PBC, gdy MPZP nie stanowi inaczej, przyjąć definicję terenu biologicznie czynnego z § 3 WT i weryfikować udział dachów zielonych.

## 7. F.11 / F.13 – Karty identyfikacyjne

### 7.1. Struktura (F.11 i F.13 są merytorycznie identyczne; różnią się słowami „Opracowanie studialne” / „Praca konkursowa”)

1. **Nagłówek:** „Opracowanie studialne oznaczone [F.13: Praca konkursowa oznaczona] Numerem identyfikacyjnym Uczestnika: ______” – sześciocyfrowa liczba wybrana przez Uczestnika.
2. **Pkt 1 – Uczestnik samodzielny:** nazwa (lub imię i nazwisko) oraz adres lub siedziba.
3. **Pkt 2 – Uczestnicy wspólni:** pozycje 1–4, każda z nazwą i adresem. Dalsze pozycje można dodać.
4. **Pkt 3 – Skład zespołu autorskiego:** imiona i nazwiska oraz miejsca zamieszkania lub prowadzenia działalności autorów i współautorów, którym przysługują autorskie prawa osobiste, z zakresem czynności. Można też wskazać współpracowników z określeniem zasad uczestnictwa. Pozycja 1 to „Główny Projektant”, pozycje 2–5 to kolejne osoby (można dodać 6, 7, 8…).
5. **Pkt 4 – Oświadczenia:**
   - 1) wykonanie obowiązków informacyjnych z art. 13/14 RODO wobec osób wymienionych w karcie;
   - 2) z art. 358 ust. 5 Pzp: „udzielamy / nie udzielamy” (krzyżyk) Zamawiającemu, na wypadek nieotrzymania nagrody, bezpłatnej, niewyłącznej licencji nieograniczonej terytorialnie i czasowo, z prawem do sublicencji, na polach eksploatacji a)–g): publikacje promocyjne, internet, multimedia, wystawianie i nadawanie, reklama, użyczanie. Do tego zgoda na pierwszą prezentację utworu przy ogłoszeniu wyników lub na wystawie pokonkursowej.
6. **Stopka:** „WYMAGANY KWALIFIKOWANY PODPIS ELEKTRONICZNY”.

### 7.2. Co jest jawne, a co anonimowe

| Element | Dane identyfikujące | Numer identyfikacyjny (6 cyfr) | Podpis |
|---|---|---|---|
| Karta identyfikacyjna F.11 / F.13 | **TAK** – jedyne miejsce z nazwą Uczestnika i autorami | **TAK** | **KPE obowiązkowy**; to jedyny podpisany element (Reg. R.VII ust.2 pkt4, s.45) |
| Plansze: pliki TIFF/JPG i wydruki | NIE | **NIE** (Reg. R.VII ust.3 pkt4 lit.b, s.47) | podpisanie plików graficznych KPE skutkuje niedopuszczeniem pracy (s.46) |
| Część opisowa w PDF (z tabelami xlsx) | NIE; także w metadanych plików | **NIE** | zakaz KPE |
| Część opisowa – zeszyt A3 | NIE | **TAK**, wyłącznie na pustej pierwszej kartce, którą Sekretarz może usunąć | – |
| Makieta | NIE | **NIE** | – |
| Opakowanie postaci fizycznej | NIE; na podstawie danych z opakowania nie wolno dać się zidentyfikować | **TAK** + wymagany opis konkursu (Reg. R.VII ust.3 pkt6, s.48) | – |
| Pokwitowanie F.10 / F.12 | adres zwrotny inny niż adres Uczestnika, w otwartej kopercie | – | – |

- Numer jest **ten sam w Etapie I i II** (Reg. R.VII ust.3 pkt4 lit.a, s.47).
- Naruszenie anonimowości, w tym przez metadane plików, może skutkować niedopuszczeniem pracy do oceny (Reg. R.VII ust.2 pkt6, s.45; ust.3 pkt4 lit.d, s.47).
- **Dla symulacji (wniosek):** na planszach nie wolno umieszczać logotypu, nazwy pracowni ani podpisu. Z plików JPG/TIFF trzeba usunąć EXIF i XMP, w tym metadane DJI i Adobe odziedziczone z F.17 (zob. `zdjecia_F17_metadane.md`). Z plików xlsx trzeba usunąć właściwości dokumentu.

## 8. F.16 – Układ plansz (Etap I; sugerowany)

- PDF A3 pionowy z dwiema planszami poziomymi 100×70.
- Proporcje ramek odczytano z renderu `F.16_UKŁAD PLANSZ.pdf` przy 70 dpi. Udziały są przybliżone i liczone względem pola planszy.
- Wersja DWG: `4.Zalaczniki_…/F.16_UKŁAD PLANSZ.dwg`.
- PDF ma uszkodzony strumień: pdftoppm zgłasza błędy składni, ale renderuje stronę.

| Plansza | Pole | Położenie (szer. × wys., ok.) | Skala wg F.16 |
|---|---|---|---|
| 1 | PERSPEKTYWA NR 1 (F.17.A) | lewa góra, ok. 60% × 66% | – |
| 1 | PERSPEKTYWA NR 2 (F.17.B) | prawa góra, ok. 40% × 45% | – |
| 1 | SYTUACJA | prawy dół, ok. 40% × 55%; podkład z obrysem obszaru | 1:500 |
| 1 | PRZEKRÓJ CHARAKTERYSTYCZNY | dół, środek, ok. 30% × 34% | 1:500 |
| 1 | DODATKOWE GRAFIKI DO DECYZJI UCZESTNIKA | lewy dół, ok. 30% × 34% | – |
| 2 | RZUTY | lewa góra, ok. 60% × 70%; obrys obszaru w lewym górnym rogu | 1:500 |
| 2 | PERSPEKTYWA NR 3 (most) | prawa góra, ok. 40% × 47% | – |
| 2 | ROZWINIĘCIA ELEWACYJNE | lewy dół, ok. 60% × 30%; dwa rozwinięcia z sąsiadami | 1:500 |
| 2 | SCHEMAT AKSONOMETRYCZNY | prawy dół, ok. 40% × 53% | – |

**Etap II:** wzoru układu plansz nie ma. Maksymalnie 8 plansz 100×70 cm, poziomo, białe tło (Reg. R.VII ust.2 pkt1 lit.a; Wyj. 20 odp. 76). Wymagane skale to 1:500 (PZT), 1:200 (rzuty, przekroje, elewacje) i 1:50 (przekrój elewacyjny). Każda kondygnacja na osobnym rzucie (Wyj. 21 odp. 79).

## 9. Wymagania umowy F.01 istotne dla koncepcji (bez kwestii rozliczeniowych)

Źródło: `tekst/F.01_Umowa_o_prace_projektowe_z_zalacznikami.txt`. Paragrafy podano wg treści, strony wg stopki PDF.

| Temat | Wymaganie | Źródło | Znaczenie dla koncepcji (*wniosek*) |
|---|---|---|---|
| Zakres dokumentacji | Wielobranżowy Projekt Koncepcyjny, PB, PW, Projekt Aranżacji Wnętrz, Przedmiary, STWiORB, Kosztorys Inwestorski, uzyskanie PnB, doradztwo przy przetargu na GW, nadzór autorski do pozwolenia na użytkowanie | § 1 pkt 2; § 2; § 3 ust. 1 (s.2–4) | Koncepcja musi być wykonalna i dać się wycenić. Dokumentacja wnętrz i SIW należy do zakresu, więc hole i sala Sejmiku na wizualizacjach to realne zobowiązanie. |
| **Etapowanie realizacji** | Etap 1: „koncepcję etapowej realizacji inwestycji”. PB i PW „umożliwiający etapowanie realizacji inwestycji” | § 3 ust. 1 pkt 1 lit.a, pkt 2 lit.a, pkt 4; zał. 3 pkt 2 | Bryłę i konstrukcję warto zaprojektować tak, żeby dało się je etapować, np. skrzydło biurowe i dominanta z salą Sejmiku. Pokazać to schematem. |
| Budżet | Nakłady na roboty nie mogą przekroczyć kwoty z § 7 ust. 1 (w konkursie 150 mln zł netto). Grozi przeprojektowanie albo odstąpienie od umowy | § 7 ust. 1–6 (s.8–9) | Spójne z W-053. Kosztorys koncepcji musi mieć zapas. |
| Terminy | Umowa do 60 miesięcy. PB w 12 mies., PW w 18 mies. od zawarcia. Nadzór do 36 mies. | § 13 ust. 2 (s.14–15) | Technologia ma być sprawdzona i szybka w projektowaniu. Prefabrykacja przyspiesza. |
| WPK – architektura | Ostateczny program, bilans powierzchni, **standardy estetyczne i techniczne**, zasady obsługi (dojazdy, dostawy, serwis), analiza zgodności z MPZP, schematy infrastruktury, zasady ppoż. z wytycznymi dla materiałów, SANEPID/BHP | zał. 3 pkt 2 ppkt 1 lit.a–f (s.38) | Opis konkursowy warto ułożyć według tych pozycji. |
| WPK – parametry | **Analiza przepustowości dźwigów**, szachty, grubości ścian, wysokości sufitów podwieszanych i przestrzeni instalacyjnych, warstwy posadzek, schemat pożarowy i drogi ewakuacyjne | zał. 3 pkt 2 ppkt 1 lit.g (s.38–39) | Przekrój 1:50 i przekroje 1:200 powinny pokazywać wysokość kondygnacji z przestrzenią instalacyjną. Wiąże się z F.15.C I.11. |
| Konstrukcja | Analiza posadowienia i **parking podziemny z funkcją Miejsca Doraźnego Schronienia (MDS)** | zał. 3 pkt 2 ppkt 2 lit.b; pkt 3 ppkt 10; pkt 5 ppkt 2 lit.d | Spójne z nagłówkiem PPM w F.15.A. Uwzględnić wymagania MDS dla garażu −1. |
| Energia | Ciepło i woda lodowa **z OZE**, zgodnie z wymogami **zeroemisyjności** (M.12). Energia elektryczna z OZE z magazynami. **Magazyny ciepła** | zał. 3 pkt 2 ppkt 3 lit.b, ppkt 4 lit.a; pkt 3 ppkt 6; pkt 5 ppkt 2 lit.e–f | Schemat proekologiczny: pompy ciepła (gruntowe lub woda z Odry?), PV, magazyny. Odpowiada pozycjom 2.12, 2.13, 7.8, 7.9, 8.17 F.14.B. |
| Woda | **Szara woda** (rozdział instalacji). **Retencja wód opadowych** | zał. 3 pkt 2 ppkt 3 lit.a, ppkt 7 lit.b; pkt 3 ppkt 7–8 | Dachy zielone i retencyjne, zbiornik szarej wody. |
| Sąsiedzi | Ekspertyzy wpływu na WS 5 i Mazowiecka 19, zabezpieczenia. **Projekt zamurowania okien w ścianie szczytowej (północnej) Mazowiecka 19** z wentylacją | zał. 3 pkt 3 ppkt 4–5 (s.40) | Potwierdza W-004: likwidacja okien dotyczy tylko Maz. 19. |
| Ppoż. i instalacje | Oddymianie garażu, klatek i dróg poziomych, **symulacje CFD**, gaszenie gazem (serwerownia), scenariusz pożarowy z matrycą sterowań, SAP, DSO, BMS jako platforma integrująca, system parkingowy, strażnik mocy, trafostacja wbudowana (jeśli wymagana), agregaty, oświetlenie przeszkodowe (jeśli wymagane) | zał. 3 pkt 5 ppkt 2 lit.e–g (s.41–42) | Oświetlenie przeszkodowe może dotyczyć dominanty 45 m. Trzeba przewidzieć miejsce na trafostację i agregat w −1 lub w parterze od strony dostaw. |
| Zieleń | Aktualizacja operatu dendrologicznego, wnioski o wycinkę, projekt nasadzeń rekompensacyjnych | zał. 3 pkt 5 ppkt 3; ppkt 2 lit.a | Każde drzewo przeznaczone do usunięcia oznacza procedurę i koszt. Zachowanie drzew podwórza (W-056) jest atutem. |
| Wnętrza | Projekt wnętrz ogólnodostępnych z meblami wbudowanymi i **systemem informacji wizualnej** | zał. 3 pkt 5 ppkt 2 lit.c (s.41) | Na wizualizacjach 6–8 warto pokazać spójny język wnętrz i SIW. |
| Wizualizacje w PW | „minimum 5 wizualizacji fotorealistycznych (rozdzielczość druk A3)” | zał. 3 pkt 5 ppkt 6 (s.43) | Informacyjnie. |
| Formaty | WPK w formacie A3/A2. PB/PW w plikach edytowalnych (dwg, docx, xlsx) i PDF, papier A4. Kodyfikacja uzgadniana. Tabele koordynacji międzybranżowej. Rewizje oznaczane „chmurką” | zał. 3 pkt 8 (s.43) | **W F.01 nie ma wymogu BIM/IFC/LOD**: wyszukiwanie fraz „BIM”, „IFC”, „LOD” dało 0 trafień. *Wniosek:* model BIM można zaoferować w opisie jako wartość dodaną. Nie jest obowiązkowy. |
| Organy | Pozwolenie konserwatorskie, wodnoprawne i inne uzgodnienia zgodnie z przepisami. Decyzja środowiskowa, o ile wymagana | § 8 (s.10–11); § 3 ust. 1 pkt 2 lit.b | Bliskość Odry i zabytkowego Mostu Grunwaldzkiego (M.14 DWKZ). Uzgodnienia konserwatorskie to ryzyko terminowe. |
