# Weryfikacja definicji wskaźników zabudowy — ustawa o planowaniu i zagospodarowaniu przestrzennym, art. 2 pkt 28–35

**Źródło (pierwotne, urzędowe):** obwieszczenie Marszałka Sejmu RP z dnia 27 marca 2026 r. w sprawie ogłoszenia jednolitego tekstu
ustawy z dnia 27 marca 2003 r. o planowaniu i zagospodarowaniu przestrzennym — **Dz.U. 2026 poz. 538** (status w ELI: „obowiązujący”),
tekst PDF pobrany 25.09.2026 z API ELI Sejmu: `https://api.sejm.gov.pl/eli/acts/DU/2026/538/text.pdf` (s. 10–11 Dziennika Ustaw).
Cytaty poniżej są dosłowne (zmieniono wyłącznie podział wierszy).

| pkt | Definicja (cytat) | Konsekwencja dla projektu (interpretacja projektanta) |
|---|---|---|
| 28 | „powierzchni biologicznie czynnej” – teren zapewniający naturalną wegetację roślin i retencję wód opadowych i roztopowych, teren pokryty ciekami lub zbiornikami wodnymi, z wyłączeniem basenów rekreacyjnych i przemysłowych, a także 50 % powierzchni tarasów i stropodachów oraz innych powierzchni zapewniających naturalną wegetację roślin, o powierzchni niemniejszej niż 10 m² | Dach zielony garażu (≥ 10 m²) **może** być liczony w 50 %; w projekcie wykazywany jako rezerwa (W-031, podejście ostrożne). Nawierzchnie ażurowe — nie są „terenem zapewniającym naturalną wegetację” w pełnym zakresie → nie wliczane. |
| 29 | „udziale powierzchni biologicznie czynnej” – stosunek sumy PBC na działce budowlanej do powierzchni tej działki (MPZP) | Wskaźnik % liczony do 1600,00 m². |
| 30 | „wysokości zabudowy” – różnica pomiędzy wysokością: a) najwyżej położonego punktu budynku na dachu, ścianie lub attyce, **z wyłączeniem komina, nadbudówki mieszczącej maszynownię dźwigu lub innego pomieszczenia technicznego oraz wyjścia z klatki schodowej**, a **średnią wysokością najniższego i najwyższego poziomu terenu mierzoną na obwodzie rzutu poziomego ścian zewnętrznych budynku** | Podstawa odniesienia = **średnia** z min. i maks. rzędnej terenu na obwodzie ścian zewnętrznych (NIE najniższy punkt terenu). Wyłączenia są zamknięte: czerpnia/wyrzutnia wentylacji, wywiewka kanalizacyjna, moduły PV, wyłaz dachowy **nie** są wymienione → wliczane (ostrożnie; wywiewka mogłaby być uznana za „komin” — nie korzystamy z tej interpretacji). Teren: istniejący vs projektowany — ustawa nie rozstrzyga (ryzyko D-15) → na każdym punkcie obwodu przyjmujemy **niższą** z rzędnych. |
| 31–32 | „intensywności zabudowy” / „nadziemnej intensywności zabudowy” – stosunek sumy powierzchni (nadziemnych) kondygnacji budynków na działce do powierzchni działki | Liczone z pkt 33. |
| 33 | „powierzchni kondygnacji” – powierzchnia rzutu poziomego kondygnacji, mierzona po zewnętrznym obrysie rzutu poziomego ścian zewnętrznych tej kondygnacji, z wyłączeniem powierzchni balkonów, logii i tarasów | Obrys po licu zewnętrznym ocieplenia; płyty wysunięte/okapy nie wliczane. |
| 34 | „kondygnacji nadziemnej” – kondygnacja niezagłębiona poniżej poziomu przylegającego terenu o więcej niż połowę jej wysokości w świetle | P0, P1, P2 — nadziemne (3 ≤ 3 wg MPZP). |
| 35 | „udziale powierzchni zabudowy” – stosunek sumy powierzchni rzutu poziomego budynków, z wyłączeniem części zagłębionych poniżej poziomu terenu, mierzonej po zewnętrznym obrysie rzutu poziomego ścian zewnętrznych tych budynków, do powierzchni działki budowlanej | Obrys ścian zewnętrznych wszystkich kondygnacji w rzucie (wspornik bryły A wliczony, bo jest obrysem ścian zewnętrznych kondygnacji P2); płyty wysunięte — tylko wariant kontrolny (W-030). |

**Rozbieżność wykryta 25.09.2026 (~06:40):** w materiałach roboczych występowały wysokości zabudowy 10,02 / 10,04 / 10,25 / 10,33 m.
Przyczyny: pominięcie urządzeń dachowych (10,02; 10,04) oraz odniesienie do najniższego punktu terenu zamiast średniej z min. i maks.
(10,33 — tools/audyt_wt.py, wersja audytu A1). **Poprawna metoda wg pkt 30 lit. a** daje wartość z urządzeniami dachowymi, liczoną od
średniej z min./maks. terenu na obwodzie ścian (wg weryfikacji niezależnej: 10,25 m przy średniej 101,404 m n.p.m. — do przeliczenia po
poprawkach modelu jednym, wspólnym modułem `lamela.wskazniki`).

Uwaga: wysokość budynku wg § 6 WT (grupa wysokości N) jest odrębnym parametrem (inna definicja — od terenu przy najniżej położonym
wejściu do górnej płaszczyzny stropu/stropodachu nad najwyższą kondygnacją użytkową z izolacją) i musi być wykazywana osobno (W-063).
