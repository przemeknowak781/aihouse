## Weryfikacja źródeł obu raportów (stan 2026-09-25, ok. 09:00–09:15 UTC)

**Wynik ogólny.** W cenniku API wszystkie 20 twierdzeń się potwierdza; jedno z nich (ceny cache w trybie fast) jest wyliczeniem z reguły podanej na stronie. W raporcie o koszcie pracy ludzi 31 z 32 pozycji potwierdza się u źródła. Niedostępne jest tylko B5 (HTTP 403). Błędy są głównie w tym, jak liczby zostały użyte, a nie w samych liczbach.

Metoda: każdy URL pobrałem ponownie przez curl. Tekst wyciągnąłem z HTML, z PDF przez pypdf, a z XLSX przez openpyxl, i przeszukałem grepem. Cytaty są dosłowne. Stronę cennika Anthropic sprawdziłem dodatkowo przez WebFetch.

Pobrane kopie `pricing.md` i `models/overview.md` są identyczne bajt w bajt z kopiami z poprzedniego kroku. To samo dotyczy wszystkich plików PDF i XLSX w `ludzie_zrodla/`.

### 1. Cennik API
- **Cena claude-opus-5-5: POTWIERDZONE na oficjalnej stronie.** Wiersz tabeli: „| Claude Opus 5.5 | $4 / MTok | $5 / MTok | $8 / MTok | $0.20 / MTok<sup>2</sup> | $20 / MTok |” (platform.claude.com/docs/en/about-claude/pricing).
  - To samo jest na claude.com/pricing: Read $0.20, Write $5, Input $4, Output $20.
  - ID `claude-opus-5-5` potwierdza strona models/overview.
  - Wycena nie jest więc przybliżeniem cenowym.
- **Odczyt z cache 0,05x: POTWIERDZONE.** Przypis 2 i tabela mnożników na stronie cennika, a na models/overview: „5% on Claude Opus 5.5”.
  - To najważniejszy parametr. Przeliczyłem koszt kontrolnie o 09:10Z (max każdego pola usage na message.id, liczone globalnie): ok. 930,74 USD. Odczyty z cache to ok. 63% tej kwoty.
  - Przy standardowym mnożniku 0,1x wyszłoby 1 517,51 USD, czyli o ok. 63% więcej. To tylko test wrażliwości, a nie wynik statystyk.
- **Zapis do cache: POTWIERDZONE.** 5 min = 1,25x ($5), 1 h = 2x ($8).
  - Uwaga: claude.com pokazuje tylko „Write $5” z dopiskiem „reflects 5-minute TTL”.
  - W tej sesji zapisy 1 h to 1 747 107 z 51 828 839 tokenów zapisu (3,4%). Wpływ na koszt to ok. 5,24 USD (0,6%).
- **thinking liczony jako output: POTWIERDZONE, ale na innej stronie.** Strona cennika nie zawiera słowa „thinking”. Potwierdzenie jest na stronie thinking-steering-and-cost: „billed as output tokens” oraz że thinking_tokens „is always less than or equal to output_tokens”.
- **Pozostałe punkty: POTWIERDZONE.** Chodzi o:
  - ceny Batch i fast,
  - brak dopłaty za długi kontekst,
  - mnożnik US-only 1,1x,
  - web search $10 za 1000 wyszukiwań,
  - przekierowania 302 i 301,
  - tabelę 18 modeli i przypis o Sonnet 5,
  - zastrzeżenie o tokenizerze,
  - ceny planów Pro, Max, Team i Enterprise oraz zdania o podatku, limitach 5 h i tygodniowych oraz o Claude Code w planach.
- **Ceny cache w trybie fast ($10 / $16 / $0,40): wyliczenie zgodne z regułą ze strony** („Prompt caching multipliers apply on top of fast mode pricing”). Tryb fast nie był używany, więc nie ma to wpływu na wycenę.
- **Nieścisła atrybucja.** Zdanie „Both options are billed monthly” pochodzi z claude.com/pricing, a nie z artykułu support. Support mówi to samo innymi słowami: „currently available as a monthly subscription only”.
- **Liczby z transkryptów.** Dokładnych wartości z 08:41–08:43Z nie da się odtworzyć, bo pliki rosną. Kontrola o 09:01Z:
  - plik główny: 1376 linii i 779 unikalnych message.id,
  - subagenty: 99 plików, 16 364 linie i 8627 id.

  Pozostałe ustalenia raportu się potwierdzają: wszędzie jest wyłącznie claude-opus-5-5, service_tier ma zawsze wartość „standard”, inference_geo zawsze „not_available”, a web_search sumuje się do 0.
- **Deduplikacja potwierdzona empirycznie.** W 1992 powtórzonych liniach różni się wyłącznie output_tokens, więc reguła „max na message.id” jest konieczna. Jeden message.id występuje w 2 plikach subagentów, więc deduplikacja musi być globalna, a nie w obrębie pliku.

### 2. Koszt pracy ludzi: źródła
- **Potwierdzone dosłownie:**
  - O1: rozporządzenie — tabela W%, udział faz i §10 ust. 5,
  - O2 i O3: GUS — wszystkie kwoty, 1742 h, zasięg „10 i więcej osób”, data publikacji 10.02.2026; działu PKD 71 w tablicach rzeczywiście nie ma,
  - O4 i O5: wskaźniki odtworzeniowe,
  - B2, B3 i B4,
  - R1–R16, R18 i R19.
- **Częściowo nieścisłe:**
  - B1 (SARP): stawki w dokumencie to 50–600 zł/h, nie 75–600. Są to minima w cenach 2014 r.
  - R13: zakresu „999–15 000 zł” nie ma w tytule strony ani w jej treści.
  - O4: numeru „Dz.Urz. 2025 poz. 2948” nie ma na stronie frigg. Wskaźnika wielkopolskiego na 2026 nadal nie ustaliłem, bo serwisy wojewody są nieosiągalne.
  - R17: wniosek o niespójności jest trafny, ale sumy etapów 590–970 h nie odtworzyłem. Wychodzi 440–630, 540–830 albo 600–1010 h, zależnie od wariantu.
  - R9: strona pisze „brutto (bez VAT)”, co wskazuje na kwotę bez VAT.
  - R19: widełki geotechniki 1 200–3 500 zł netto potwierdza inne źródło (dzialkopedia.pl), a nie strony wskazane w raporcie.
- **NIEDOSTĘPNE: B5 (Nieradka, 414–440 h).** curl i WebFetch zwracają 403. Wyszukiwarka pokazuje tylko zakresy faz (98–131, 98–126 i 190–223 h, 4 domy o powierzchni 140–360 m²), ale nie sumę 414–440 h.
- **Porównywalność zakresu — tu leżą główne błędy użycia:**
  - Cenniki BIAMS, Disinn i Energetyczny Projekt liczą cenę od powierzchni podłogi, a raport mnożył ją przez PU 239,16 m². Według repozytorium PU nie obejmuje garażu (37,42 m²) ani pomieszczeń technicznych, a powierzchnia netto wynosi ok. 299,86 m².
  - BIAMS podaje VAT 8–23%, a nie 23%. Poprawnie: 68–78 tys. zł netto przy VAT 23% albo 78–89 tys. przy VAT 8%. Raport podał 54–62 tys. Pakiet obejmuje też koncepcję z wizualizacjami, więc jest najbliższym punktem odniesienia.
  - Disinn liczony od powierzchni podłogi daje 39–57 tys. zł, a nie 31–45 tys.
  - Extradom wprost podaje netto i stan deweloperski, więc zastrzeżenie raportu „nie wiadomo, czy netto” jest nieaktualne. Oznacza to, że koszt budowy 6 004 zł/m² jest dolnym scenariuszem.
  - Cena wg SARP i rozporządzenia obejmuje koncepcję, projekt budowlany i pełny projekt wykonawczy (PK+PB+PW). Porównywany zakres kończy się na projekcie technicznym (PT), jest więc węższy. Moje założenie, bez źródła: taki zakres to ok. 57–90% ceny SARP.
- **Arytmetyka raportu jest poprawna.** Wyniki zgadzają się co do złotówki: 75 441 / 104 343 zł, 96 411 / 133 095 zł, 18 349,60 zł, 10–32 tygodni i 3,79–7,58 etatomiesiąca.

### 3. Ocena widełek dla zespołu ludzi
- **Koszt 30–150 tys. zł netto:**
  - **Dolna granica jest zaniżona.** Składnik sanitarny ~4 tys. zł pochodzi z niezweryfikowanego wyniku wyszukiwarki; zweryfikowana oferta DraftSanit (R10) to 14,5 tys. zł. Do tego cena wizualizacji nie obejmuje modelu 3D. Ze zweryfikowanych składników wychodzi 40 110–45 350 zł.
  - **Środek 60–100 tys. jest uczciwy.** BIAMS policzony poprawnie plus strona daje ok. 70–93 tys. Zestaw Disinn, DraftSanit, elektryka, charakterystyka energetyczna, wizualizacje i strona daje ok. 61–85 tys.
  - **Górna granica 150 tys. da się obronić tylko jako granica normatywna SARP.** Jako granica rynkowa jest zawyżona. Opiera się na założeniu 8 000 zł/m² (eyecad podaje 6 000–7 500 zł/m²), kategorii IV i pełnym projekcie wykonawczym. Żadne źródło rynkowe z lat 2024–2026 nie przekracza ok. 96 tys. zł.
  - **Propozycja:** ok. 40–130 tys. zł netto, najbardziej prawdopodobne 60–95 tys. zł netto.
- **Czas 10–32 tygodni jest uczciwy.** Zgadza się z R4, R14 i R6. Zastrzeżenia: czas PT jest przybliżony czasem „projektu wykonawczego” z R4, a „typowo 16–26 tygodni” nie ma źródła.
- **Roboczogodziny 550–1 100 h są prawdopodobne, ale słabo ugruntowane:**
  - główny składnik (B5) jest niedostępny,
  - stawka 120–150 zł/h to założenie bez źródła; przy tańszym biurze wychodzi ok. 400 h,
  - „typowo 700–900 h” i zespół 5–7 osób to założenia.

  Uczciwiej: ok. 400–1 100 h, oznaczone jako szacunek.
- **Zastrzeżenie ogólne.** Biuro dostarcza kompletną, podpisaną dokumentację na realnych danych, z odpowiedzialnością zawodową. W repozytorium są pliki BRAKI_DANYCH.md z pozycjami [DO UZUPEŁNIENIA] w PZT, PT-BO, PT-IS i PT-IE, a działka, MPZP i geotechnika są fikcyjne. Koszt biura to więc koszt pełnego odpowiednika, a nie wycena tego, co faktycznie powstało.

### Pliki
- Wynik: `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/weryfikacja_zrodel.json`
- Katalog pomocniczy `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/statystyki/weryf/` zawiera:
  - skrypty: `sprawdz_modele.py`, `sprawdz_cache.py`, `przeliczenia.py` i `weryfikacja_zapisz.py`,
  - kopie źródeł w `src/`,
  - sumy kontrolne w `sha256_kopii.txt`.

W /home/user/aihouse niczego nie zmieniałem. Zmiany widoczne w `git status` (raporty/nadzor.json, pozycje.py, test_arkusze_formaty.py) nie pochodzą ode mnie.