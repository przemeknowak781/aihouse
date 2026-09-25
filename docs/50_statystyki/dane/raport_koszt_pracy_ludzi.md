# Ile to samo kosztowałoby i trwało w biurze projektowym (Polska 2024–2026) — Dom LAMELA

## Wynik
Porównywany zakres: koncepcja, PZT, PAB oraz PT (architektura, konstrukcja, instalacje sanitarne z charakterystyką energetyczną, instalacje elektryczne z PV), do tego wizualizacje i strona sprzedażowa. Nie liczę mapy, badań gruntu, opłat, uzgodnień ani nadzoru autorskiego.

| | Widełki | Na czym się opiera |
|---|---|---|
| **Koszt (zł netto)** | **30 000–150 000**; najbardziej prawdopodobne **60 000–100 000** | Tanie biuro regionalne z cenników: ok. 30 tys. Rynek, pełny zakres: 60–100 tys. Metoda SARP i rozporządzenia: 75–133 tys., z wizualizacjami i stroną ok. 80–150 tys. |
| **Czas pracy zespołu** | **10–32 tygodni** (typowo 16–26) | Koncepcja 2–8 tyg., PZT+PAB 4–12 tyg., PT 4–12 tyg. Wizualizacje (1–2 tyg.) i strona robione równolegle. Nie wliczam urzędu: pozwolenie trwa do 65 dni. |
| **Roboczogodziny** | **ok. 550–1 100 h** (typowo 700–900 h) | To 3,8–7,6 etatomiesiąca (145,2 h/mies. wg GUS). Zespół 5–7 osób. |

Dane budynku z repozytorium: powierzchnia użytkowa 239,16 m², kubatura 1 354,45 m³ (raport weryfikacji PAB).

## Metoda i założenia
- **Metoda SARP i rozporządzenia.** Wzór: cena projektu = W% × koszt budowy (Kb), gdzie W% to wskaźnik procentowy z tabeli; wartości między wierszami tabeli interpolowałem liniowo.
  - Dom z garażem to kategoria III, dom z indywidualnymi wymaganiami — IV. Reguła SARP: cenę przyjmuje się w przedziale od danej kategorii do kategorii wyższej.
  - Koszt budowy (Kb) w trzech scenariuszach:

| Koszt 1 m² | Skąd | Kb | Cena projektu kat. III / IV |
|---|---|---|---|
| 6 004 zł | Sekocenbud Q2 2026, cytowany przez extradom | 1,436 mln zł | 75 441 / 104 343 zł |
| 6 207 zł | wskaźnik wojewody wielkopolskiego, 2025 H1 | 1,484 mln zł | 77 667 / 107 403 zł |
| 8 000 zł | **moje założenie** dla standardu podwyższonego (to nie dana ze źródła) | 1,913 mln zł | 96 411 / 133 095 zł |

- **Wizualizacje i strona** są doliczone osobno, bo SARP wyłącza z ceny projektu makiety i specjalne opracowania graficzne.
- **Roboczogodziny liczyłem na dwa sposoby:**
  - Oddolnie, ok. 575–980 h: architektura 414–440 h (B5), elektryka 30–45 h dla 150 m² przeskalowane do 239 m² (R11). Godziny dla konstrukcji, instalacji sanitarnych, wizualizacji i strony to **moje założenia** (cena podzielona przez 120–150 zł/h).
  - Odgórnie: 75–133 tys. zł / 120–150 zł/h ≈ 490–1 110 h.
- **Strona sprzedażowa:** czas 2–6 tyg. to założenie, bo nie znalazłem źródła.

## Tabela źródeł
Typ: O = oficjalne, B = branżowe, R = rynkowe (mniej wiarygodne). Liczby z plików pobranych bezpośrednio są dosłowne. Pozycje oznaczone „WF” pochodzą z narzędzia WebFetch, które zwraca streszczenie — cytat może nie być dosłowny.

| ID | Typ | Źródło, rok | Wartość | Uwagi o porównywalności |
|---|---|---|---|---|
| O1 | O | Rozporządzenie MRiT, Dz.U. 2021 poz. 2458, api.sejm.gov.pl (obowiązuje od 2022) | W% kat. III: 5,45 przy Kb 1 mln / 5,00 przy 2 mln; kat. IV: 7,55 / 6,90. Fazy: PK 7–15%, PB 30–45%, PW 40–60% | Narzędzie dla zamówień publicznych, nie cennik. Nie obejmuje mapy i geologii (§10 ust. 5). |
| O2 | O | GUS, Struktura wynagrodzeń wg zawodów X 2024 (xlsx, publ. 10.02.2026) | Sekcja M: 12 145,66 zł/mies., 65,75 zł/h. Architekci, geodeci i projektanci (216): 8 808,89 zł/mies., 47,74 zł/h. Inżynierowie (214): 10 918,02 zł / 58,61 zł/h. Elektrotechnologia (215): 12 819,97 zł / 68,57 zł/h. Średnia w Polsce: 8 944,79 zł | Kwoty brutto etatowe, bez kosztów pracodawcy, biura i marży. **Dział PKD 71 nie jest publikowany.** |
| O3 | O | GUS, Zatrudnienie i wynagrodzenia 2024 (xlsx) | Sekcja M: 11 213,57 zł/mies. (109,5% r/r); 1 742 h przepracowane na osobę rocznie | Tylko firmy od 10 pracujących (uwagi metodologiczne, pkt 9). |
| O4 | O, przez źródło wtórne | Wskaźnik kosztu odtworzenia 1 m², woj. wielkopolskie, 1.04–30.09.2025 (frigg.com.pl) | 6 207 zł bez Poznania; 9 870 zł Poznań | Serwis wojewody niedostępny. **Wartości na 2026 nie udało się odczytać.** |
| O5 | O | Obwieszczenia wojewodów na 1.04–30.09.2026 | kujawsko-pomorskie 6 685; zachodniopomorskie 7 718 (Szczecin 8 723); mazowieckie bez Warszawy 7 828,57 (Warszawa 12 149,38) zł/m² | Wskaźnik z prawa lokatorskiego, nie kosztorys domu. |
| B1 | B | ZWPP SARP, uchwała nr 70 z 5.04.2014 (sarp.pl) | Ta sama tabela W% co O1. Podział PB: architektura 50, konstrukcja 15, sanitarne 10, elektryczne 5, koordynacja 10%. Nadzór autorski dodatkowo ≥15%. Stawki 2014: 75–600 zł/h | Niewiążące. **Dokumentu „Środowiskowe Standardy Wynagradzania” nie znalazłem** — odpowiednikami są ZWPP SARP i ŚZWPP IPB. |
| B2 | B | IARP, „Jak wycenić projekt?” (WF) | brak liczb | Prawo konkurencji zabrania wiążących cenników. |
| B3 | B | IPB (ŚZWPP), stawka za jednostkę nakładu pracy (j.n.p.) | 28,70 zł (2024), 30,80 (2025), 33,30 (2026) netto | j.n.p. to jednostka umowna, nie roboczogodzina. Tabele dla domów są w płatnym wydaniu, więc **tą metodą nie liczyłem**. |
| B4 | B | PIIB, raport o wynagrodzeniach 2024/25 (publ. 2026) | Projektanci budynków z uprawnieniami: 9 698,98 zł; projektanci sanitarni: 9 014,20 zł (kwoty netto, na rękę) | Ankieta, n=3306. |
| B5 | B, niezweryfikowane | Architektura & Biznes, K. Nieradka (strona zwraca 403) | 414–440 h na dom 140–360 m² (koncepcja 98–131, PB 98–126, PW 190–223) | **Liczby tylko z wyniku wyszukiwarki.** To prawdopodobnie godziny samej pracowni architektonicznej. |
| R1 | R | muratordom, 13.06.2025 (WF) | 90–160 zł/m²; PAB 50–140, PT 100–200 zł/m²; gotowy projekt 3–6 tys.; adaptacja 5–10 tys. | Miesza kwoty netto i brutto. |
| R2 | R | Disinn, aktualizacja 22.10.2025 (WF) | 130–190 zł/m² netto | PZT+PAB+PT; instalacje i PV dopłacane osobno. |
| R3 | R | Jura Projekt, 25.10.2024 (WF) | 80–150 zł/m² netto; 10–50 tys. zł | |
| R4 | R | Energetyczny Projekt, 22.10.2024 (WF) | 100–300 zł/m²; koncepcja 2–6 tyg., PB 4–10 tyg., PT do ok. 3 mies. | Firma wykonawcza — możliwy konflikt interesów. |
| R5 | R | Archeton, 17.08.2026 (WF) | 60–250 zł/m² | Bardzo szeroki zakres. |
| R6 | R | Rankomat, 11.06.2026 (WF) | 150–300 zł/m²; projekt indywidualny 3–9 mies.; mapa ok. 1 200, geotechnika ok. 1 800 zł (przykłady) | |
| R7 | R | BIAMS, cennik bez daty (WF) | 280–320 zł/m² brutto dla 180–270 m², z konstrukcją, instalacjami i PT; netto ok. 54–62 tys. zł | Zakres najbliższy naszemu. Przeliczenie na netto przy 23% VAT to założenie. |
| R8 | R | Projekty Format, cennik 2025 (PDF, dosłownie) | Architektura+konstrukcja 16 000 zł + 60 zł/m² ponad 200 m², czyli ok. 18 350 zł netto; konstrukcja 35 zł/m² | Tanie biuro, bez instalacji. |
| R9 | R | Biuro Projektów Konstrukcji, bez daty (WF) | 25,70 zł/m² (PB+PT konstrukcji) | Nie podano, czy netto. |
| R10 | R | DraftSanit, bez daty (WF) | Pakiet sanitarny 180–250 m² z pompą ciepła i rekuperacją: 14 500 zł netto; charakterystyka energetyczna od 900 zł | |
| R11 | R | instalacje-ele.pl, 15.06.2026 (WF) | Projekt elektryczny 1 500–4 500 zł netto; 30–45 h dla 150 m² | Brak ceny projektu PV. |
| R12 | R | Rooven, 2026 (WF) | Od 520–630 zł netto za ujęcie, model 3D płatny osobno; 5–10 dni roboczych | |
| R13 | R | KC Mobile, 13.09.2026 (WF) | Landing page 2 260–4 500 zł netto (w tytule 999–15 000 zł) | Brak czasu realizacji. |
| R14 | R | Ciemińscy, 8.08.2026 (WF) | Koncepcja 2–8 tyg.; PB z koordynacją 4–12 tyg.; do pozwolenia 4–8 mies. | |
| R15 | R | Murator Projekty, 13.06.2024 (WF) | Koncepcja 2–6 tyg.; całość 1–2 mies. | Optymistyczne. |
| R16 | R | eyecad, 15.01.2026 (WF) | 150–350 zł/m² netto; 4–8% kosztu budowy | |
| R17 | R | architektbudowlany.pl, 17.07.2026 | 800–2 500 h dla domu 150 m² | **Nie użyte:** brak źródła, a suma etapów z tego samego tekstu (590–970 h) się nie zgadza. |
| R18 | R | extradom (dane Sekocenbud), 24.08.2026 (WF) | Koszt budowy 6 004 zł/m² (Q2 2026) | Źródło wtórne; nie wiadomo, czy netto. |
| R19 | R | geodetawozniak / wynik wyszukiwarki, 2026 | Mapa do celów projektowych 1 300–1 800 zł; geotechnika 1 200–3 500 zł | |

## Czego praca AI nie zastępuje
- **Uprawnienia i odpowiedzialność:** potrzebne są uprawnienia budowlane i członkostwo w izbie z obowiązkowym OC, podpis i oświadczenia projektantów, odpowiedzialność zawodowa, cywilna i karna. Tam, gdzie wymaga tego Prawo budowlane, także sprawdzenie projektu (art. 20 — wyjątki dla domów jednorodzinnych trzeba zweryfikować).
- **Dane wejściowe z terenu:** mapę do celów projektowych robi uprawniony geodeta. Badania gruntu i opinia geotechniczna to prace terenowe.
- **Formalności:** realne MPZP lub WZ, warunki przyłączenia od gestorów sieci, uzgodnienia (np. rzeczoznawca ppoż. przy PV powyżej 6,5 kW) i procedura pozwolenia na budowę.
- **Praca z inwestorem i na budowie:** wizja lokalna, spotkania, nadzór autorski (≥15% ceny projektu wg SARP), licencja lub prawa autorskie.
- **Dane w repozytorium są fikcyjne.** W `docs/00_brief_projektowy.md` działka, MPZP i opinia geotechniczna są opisane jako fikcyjne lub przykładowe. Biuro musiałoby je najpierw pozyskać.

## Czego nie udało się ustalić
- **Serwisy Wojewody Wielkopolskiego** zrywały połączenie (connection reset) albo zwracały HTTP 503. Proxy działa (enabled, bundleCoversEveryHost=true), a błędy dotyczą tylko tych serwerów. Dlatego nie mam wskaźnika wielkopolskiego na 2026.
- **Inne blokady:** bgk.pl, architekturaibiznes.pl i z500.pl zwracały HTTP 403, 3d-archi.pl HTTP 503, a Inforlex i LEX mają paywall.
- **Nie ustaliłem:** płac dla działu PKD 71, pracochłonności według tabel ŚZWPP (wydanie płatne), ceny samego projektu PV, godzin dla konstrukcji i instalacji sanitarnych (użyłem założeń opisanych wyżej) ani czasu wykonania strony.
- **Repozytorium tylko czytałem.** Zmiana w `git status` (`M src/lamela/views/uklad.py`) nie pochodzi ode mnie.

## Pliki
Wszystkie w `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/`:
- `ludzie.json` — 29 wpisów o źródłach z URL-ami, cytatami i uwagami, obliczenia, widełki, lista tego, czego AI nie zastępuje, problemy z dostępem
- `ludzie_oblicz.py`, `ludzie_oblicz_wynik.json` — obliczenia
- `ludzie_zapisz.py` — generator pliku JSON
- `ludzie_zrodla/` — pobrane PDF i XLSX z wyciągniętym tekstem (SARP, rozporządzenie, IPB, GUS, PIIB, Format, obwieszczenia)