<!-- wygenerowano: tools/dokumenty/tom_PT_AR.py; model: model/budynek.yaml (2026-09-25) -->
# PT-1 AR — projekt techniczny, architektura (źródło części opisowej)

# Część opisowa — architektura (§ 7 ust. 1 pkt 3, § 23 RPB)

## Przedmiot i zakres tomu — § 23 RPB

Przedmiotem tomu jest projekt techniczny w specjalności architektonicznej dla zamierzenia
„Budowa budynku mieszkalnego jednorodzinnego wolnostojącego „Dom LAMELA” z garażem dwustanowiskowym w bryle budynku, wraz z zagospodarowaniem terenu i infrastrukturą towarzyszącą (zjazd, dojazd i dojście, miejsca postojowe, zbiornik retencyjny wód opadowych, ogrodzenie)” — Budynek mieszkalny jednorodzinny wolnostojący „Dom LAMELA”, działka ewid. nr 123/4, obręb 0005 „Przykładowo”, gm. Przykładowo (fikcyjna). Obiekt kategorii I;
3 kondygnacje nadziemne, wysokość wg WT § 6:
9,97 m (grupa wysokości N); 1 lokal mieszkalny.
Dane działki, MPZP i gruntu są przykładowe [DANE PRZYKŁADOWE – FIKCYJNE].

Tom PT-1 AR obejmuje: rozwiązania konstrukcyjno-materiałowe przegród zewnętrznych i wewnętrznych
(§ 23 pkt 4 RPB), ocenę wymogu analizy akustycznej (§ 23 pkt 4a), obliczenia cieplno-wilgotnościowe przegród
i węzłów, zestawienia przegród, stolarki i wykończeń, opis ciągłości warstw („4 linii”) i odwodnienia oraz dane
dotyczące warunków ochrony przeciwpożarowej w zakresie architektury (§ 23 pkt 10). Część rysunkowa (§ 24 pkt 1–2)
obejmuje rzuty z rzutem dachu, przekroje i elewacje w skali 1:50 oraz detale w skalach 1:5 i 1:10.

**Pozostałe punkty § 23 RPB — gdzie opracowano:** pkt 1–2 (konstrukcja, posadowienie) — PT-2 BO; pkt 3
(dokumentacja geologiczno-inżynierska) — nie dotyczy (warunki proste, rejestr C.2); pkt 5 i 6 — nie dotyczy
(obiekt mieszkalny, niebędący obiektem liniowym); pkt 7–9 i 11 — PT-3 IS i PT-4 IE (instalacje, charakterystyka
energetyczna); pkt 10 — w każdym tomie stosownie do zakresu (tu: rozdział „Dane dotyczące warunków ochrony przeciwpożarowej”).

**Podstawy:** PB (t.j. Dz.U. 2026 poz. 524 ze zm.) art. 34 ust. 3 pkt 4; RPB (t.j. Dz.U. 2022 poz. 1679 ze zm.)
§ 23–24; WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) stosowane na podstawie art. 102a PB; PN-EN ISO 6946:2017-10,
PN-EN ISO 13370:2017-09, PN-EN ISO 10077-1:2017-10, PN-EN ISO 10211:2017-09, PN-EN ISO 13788:2013-05,
PN-EN ISO 14683:2017-09 (rejestr wymagań, W-243…W-250). Tom jest zgodny z PZT i PAB (PB art. 34 ust. 3c).

## Wyroby budowlane — zasada doboru — PB art. 10

Wyroby określono **parametrami wymaganymi** (λ obliczeniowe, grubość, klasa reakcji na ogień, opór dyfuzyjny s_d,
U_w/U_D, g, klasa szczelności). Nazwy systemów i dane z kart katalogowych przywołane w modelu są
**przykładowe — dopuszcza się wyroby równoważne** o parametrach nie gorszych, wprowadzone do obrotu zgodnie
z PB art. 10 (oznakowanie CE lub znak budowlany B, deklaracja właściwości użytkowych). Wartości oznaczone
[ZAŁ] (założenie) i [NZW] (niezweryfikowane) wymagają potwierdzenia deklaracją wybranego wyrobu przed
wbudowaniem.

## Rozwiązania konstrukcyjno-materiałowe przegród — § 23 pkt 4 RPB

Przegrody zestawiono z modelu budynku (sekcje `przegrody` i `materialy`). Warstwy ścian podano od strony
wewnętrznej, warstwy przegród poziomych — od góry. Grubości w milimetrach; λ — wartość obliczeniowa
[W/(m·K)]. Współczynniki U wyznaczono w rozdziale „Obliczenia cieplno-wilgotnościowe przegród i węzłów”.

**Tabela 1. Zestawienie przegród budowlanych**

| Kod | Rodzaj | Nazwa (model) | Grubość [mm] | U [W/(m²·K)] | Detale |
|---|---|---|---|---|---|
| SZ1 | ściana zewnętrzna | Ściana zewnętrzna nośna: silikat 18 + ETICS EPS 031 20 cm | 405 | 0,170 | D-01, D-02, D-03, D-04, D-05, D-06, D-08, D-09 |
| SZ2 | ściana zewnętrzna | Ściana zewnętrzna bryły A (P2) za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV-stabilna (czarna); szczelina wentylowana ok. 11 cm i lamele na ruszcie — element `lamele` | 405 | 0,170 | D-02, D-04, D-08, D-12 |
| SZL | ściana zewnętrzna | Ściana zewnętrzna lekka A' (na wsporniku P2): GK + OSB (szczelność) + szkielet KVH 45×200 z wełną + DWD + wełna fasadowa 18 cm + membrana UV (lico zewn. 0,30 m od osi — jak SZ2, ciągłość warstw w narożu); bez funkcji nośnej | 440 | 0,099 | D-02, D-08, D-12 |
| SW18 | ściana wewnętrzna nośna | Ściana wewnętrzna nośna: silikat 18, tynk gipsowy obustronnie | 210 | — | — |
| SWZB | ściana wewnętrzna nośna | Ściana wewnętrzna nośna żelbetowa 18 cm (trzon klatki na P0 — usztywnienie w kierunku x, J2) | 210 | — | — |
| SWG | ściana wewnętrzna nośna | Ściana nośna dom–garaż nieogrzewany: silikat 18 + wełna 12 cm od strony garażu + tynk | 325 | 0,270 | D-10 |
| SCZB15 | ściana wewnętrzna nośna | Ściana środkowa klatki schodowej: żelbet C25/30 15 cm, monolityczna z płytami biegów i spoczników, ciągła P0–P2 (przez poziomy stropów), zakotwiona w podciągach B8/B9/B10 osi 3 (audyt A2 I-2) | 150 | — | — |
| DZ12 | ścianka działowa | Ścianka działowa: silikat 12 + tynk gipsowy obustronnie (R'w ≥ 45 dB) | 150 | — | — |
| DZGK | ścianka działowa | Ścianka działowa GK 12,5 cm z kasetą drzwi przesuwnych chowanych (2 × GK impregnowana 12,5 mm obustronnie, kaseta stalowa 7,5 cm z wełną poza strefą kasety; R'w ≥ 40 dB) | 125 | — | — |
| DZ18A | ścianka działowa | Ścianka działowa akustyczna pom. technicznego z centralą (P2): silikat 18 kl. 15 na zaprawie cienkowarstwowej, tynk gipsowy obustronnie, bez funkcji nośnej, styk ze stropem wypełniony elastycznie; cel R'A1 ≥ 50 dB do sprawdzenia w PT (audyt A3 I-8; W-066, W-230) | 210 | — | — |
| GK10 | ścianka działowa | Obudowa szachtu SI: 2 × GKF 12,5 + profil CW 50 z wełną + 2 × GKF 12,5 (EI 30) | 100 | — | — |
| SGL | ścianka działowa | Ścianka szklana wiatrołap/hol: VSG w ramie aluminiowej z drzwiami szklanymi 0,90 m | 50 | — | — |
| AT1 | attyka | Attyka: żelbet 18 cm (wieniec podniesiony), izolacja z 3 stron (EPS 031 10 cm od dachu, ETICS od zewnątrz, PIR 4 cm na koronie), obróbka blacharska ze spadkiem do dachu, wywinięcie membrany ≥ 0,15 m | 485 | — | D-04, D-05 |
| POD-0 | podłoga na gruncie | Podłoga na płycie fundamentowej (P0): deska/gres, jastrych z ogrzewaniem podł., EPS 100, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm, XPS 300 20 cm, folia PE, podsypka | 800 | 0,110 | D-01, D-03, D-06, D-10 |
| POD-0L | podłoga na gruncie | Podłoga na płycie (P0) — łazienki, WC, przedsionek, pom. techniczne: gres na hydroizolacji podpłytkowej | 800 | — | — |
| POD-G | podłoga na gruncie | Posadzka garażu (nieogrzewany): żywica R11, jastrych cementowy zbrojony 9–14 cm (spadek 0,8 % do bramy: −0,05 przy drzwiach do domu → −0,10 przy bramie), folia PE, XPS 300 10 cm, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm obniżona (wierzch −0,30) na XPS 20 cm | 850 | 0,100 | — |
| POD-1 | strop / sufit | Strop międzykondygnacyjny: deska dębowa, jastrych z ogrzewaniem podł., EPS 100, EPS T (akustyczny), płyta ŻB 22 cm, tynk | 380 | — | D-08, D-09 |
| POD-1L | strop / sufit | Strop międzykondygnacyjny — łazienki, WC, pralnia: gres na hydroizolacji podpłytkowej | 380 | — | — |
| SUF-ZEW | strop / sufit | Sufit pod stropem nad powietrzem zewnętrznym (wspornik bryły A): wełna 20 cm na kołkach + podsufitka włóknocementowa na ruszcie z pustką wentylowaną | 253 | — | D-08 |
| SUF-G | strop / sufit | Docieplenie spodu stropu garażu pasem 1,0 m przy ścianach osi E i 2 (wełna 10 cm + płyta) — ograniczenie mostka (J2) | 110 | — | D-10 |
| SD1 | stropodach / dach | Stropodach bryły A (P2): membrana TPO, PIR spadkowy 12–32 cm (śr. 22), paroizolacja z Al, płyta ŻB 22 cm, tynk; spadek ≥ 2 % do wpustów WP1/WP2 | 456 | 0,110 | D-04, D-06 |
| SD2 | stropodach / dach | Stropodach nad P1 (pola pn. poza bryłą A): żwir 5 cm, włóknina, membrana TPO, PIR spadkowy 14–26 cm, paroizolacja, płyta ŻB 22 cm | 490 | 0,120 | D-05 |
| DZ1 | stropodach / dach | Dach zielony ekstensywny NIEUŻYTKOWY nad garażem (pom. nieogrzewane) i pasem gospodarczym: substrat 8 cm, geowłóknina, mata drenażowa, włóknina, bariera przeciwkorzenna, 2 × papa SBS, PIR spadkowy 12–24 cm, paroizolacja, płyta ŻB 24 cm (dwukierunkowa); opaska żwirowa 0,5 m przy attykach i wpustach; nad garażem: pole PV biosolarne (8 modułów) | 545 | 0,130 | D-06, D-10 |
| OK1 | płyta wysunięta / okap | Płyta wysunięta (okap, daszek, krawędź ST2/ST3): obróbka/membrana ze spadkiem 2 % od budynku, płyta ŻB C30/37 z łącznikiem termoizolacyjnym (ETA), podsufitka z okapnikiem | 314 | — | D-08, D-09 |

U — wartość z obliczenia wg PN-EN ISO 6946 / 13370 (obliczenia cieplno-wilgotnościowe), zaokrąglona do 2 cyfr znaczących; „—” — przegroda wewnętrzna między pomieszczeniami ogrzewanymi (bez wymagań U).

Detale — detale PT-AR-D obejmujące węzły z udziałem przegrody (sekcja `wezly` modelu).

*Źródło: model/budynek.yaml — przegrody; lamela.obliczenia.fizyka_energia*

### Przegrody zewnętrzne i oddzielające od garażu

**Tabela 2. SZ1 — Ściana zewnętrzna nośna: silikat 18 + ETICS EPS 031 20 cm**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | szczelność powietrzna | — |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Styropian grafitowy EPS 031 (ETICS, NRO w systemie) | 200,000 | 0,031 | izolacja cieplna | — |
| 4 | ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (biały / jasnoszary NCS S 1500-N) | 10,000 | 0,800 | tynk | — |

**Tabela 3. SZ2 — Ściana zewnętrzna bryły A (P2) za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV-stabilna (czarna); szczelina wentylowana ok. 11 cm i lamele na ruszcie — element `lamele`**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | szczelność powietrzna | — |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | 200,000 | 0,035 | izolacja cieplna | — |
| 4 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 10,000 | 0,170 | wiatroizolacja | — |

**Tabela 4. SZL — Ściana zewnętrzna lekka A' (na wsporniku P2): GK + OSB (szczelność) + szkielet KVH 45×200 z wełną + DWD + wełna fasadowa 18 cm + membrana UV (lico zewn. 0,30 m od osi — jak SZ2, ciągłość warstw w narożu); bez funkcji nośnej**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | wykonczenie | — |
| 2 | Płyta OSB/3 15 mm (usztywnienie i warstwa szczelności ściany A') | 15,000 | 0,130 | szczelność powietrzna | — |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 200,000 | 0,035 | izolacja cieplna | niejednorodna: WELNA_035 88 %, DREWNO_KVH 12 %; warstwa nośna / konstrukcyjna |
| 4 | Płyta drewnopochodna wiatroizolacyjna DWD/MDF.RWH 16 mm | 16,000 | 0,100 | wiatroizolacja | — |
| 5 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | 180,000 | 0,035 | izolacja cieplna | — |
| 6 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 4,000 | 0,170 | wiatroizolacja | — |

**Tabela 5. SWG — Ściana nośna dom–garaż nieogrzewany: silikat 18 + wełna 12 cm od strony garażu + tynk**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 120,000 | 0,035 | izolacja cieplna | — |
| 4 | Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne) | 10,000 | 0,820 | tynk | — |

**Tabela 6. AT1 — Attyka: żelbet 18 cm (wieniec podniesiony), izolacja z 3 stron (EPS 031 10 cm od dachu, ETICS od zewnątrz, PIR 4 cm na koronie), obróbka blacharska ze spadkiem do dachu, wywinięcie membrany ≥ 0,15 m**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 100,000 | 0,022 | izolacja cieplna | — |
| 2 | Żelbet C30/37 XC4/XF1 (krawędzie płyt wysuniętych, attyki, belki) | 180,000 | 2,500 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Styropian grafitowy EPS 031 (ETICS, NRO w systemie) | 200,000 | 0,031 | izolacja cieplna | — |
| 4 | ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (biały / jasnoszary NCS S 1500-N) | 5,000 | 0,800 | tynk | — |

**Tabela 7. POD-0 — Podłoga na płycie fundamentowej (P0): deska/gres, jastrych z ogrzewaniem podł., EPS 100, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm, XPS 300 20 cm, folia PE, podsypka**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Deska warstwowa dębowa 15 mm, klejona | 15,000 | 0,180 | konstrukcja | — |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | wykonczenie | — |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 65,000 | 0,038 | izolacja cieplna | — |
| 4 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | 5,000 | 0,230 | izolacja przeciwwilgociowa/przeciwradonowa | — |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 250,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 6 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 200,000 | 0,036 | izolacja cieplna | — |
| 7 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | warstwa rozdzielająca | — |
| 8 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | 200,000 | 2,000 | grunt | — |

**Tabela 8. POD-0L — Podłoga na płycie (P0) — łazienki, WC, przedsionek, pom. techniczne: gres na hydroizolacji podpłytkowej**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płytki gresowe 60×120 na kleju C2TE S1 | 12,000 | 1,300 | wykonczenie | — |
| 2 | Hydroizolacja podpłytkowa (masa uszczelniająca + taśmy), strefy mokre | 3,000 | 0,200 | hydroizolacja | — |
| 3 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | wykonczenie | — |
| 4 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 65,000 | 0,038 | izolacja cieplna | — |
| 5 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | 5,000 | 0,230 | izolacja przeciwwilgociowa/przeciwradonowa | — |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 250,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 7 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 200,000 | 0,036 | izolacja cieplna | — |
| 8 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | warstwa rozdzielająca | — |
| 9 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | 200,000 | 2,000 | grunt | — |

**Tabela 9. POD-G — Posadzka garażu (nieogrzewany): żywica R11, jastrych cementowy zbrojony 9–14 cm (spadek 0,8 % do bramy: −0,05 przy drzwiach do domu → −0,10 przy bramie), folia PE, XPS 300 10 cm, membrana SBS (przeciwwilgociowa, przeciwradonowa), płyta ŻB 25 cm obniżona (wierzch −0,30) na XPS 20 cm**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Posadzka żywiczna epoksydowa antypoślizgowa R11 (garaż) | 3,000 | 0,200 | wykonczenie | — |
| 2 | Jastrych cementowy CT-C30-F5 zbrojony (siatka/włókna), dylatacja obwodowa — posadzka garażu na XPS | 92,000 | 1,200 | wykonczenie | — |
| 3 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | warstwa rozdzielająca | — |
| 4 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 100,000 | 0,036 | izolacja cieplna | — |
| 5 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | 5,000 | 0,230 | izolacja przeciwwilgociowa/przeciwradonowa | — |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 250,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 7 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 200,000 | 0,036 | izolacja cieplna | — |
| 8 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | warstwa rozdzielająca | — |
| 9 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | 200,000 | 2,000 | grunt | — |

**Tabela 10. SUF-ZEW — Sufit pod stropem nad powietrzem zewnętrznym (wspornik bryły A): wełna 20 cm na kołkach + podsufitka włóknocementowa na ruszcie z pustką wentylowaną**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 200,000 | 0,035 | izolacja cieplna | warstwa nośna / konstrukcyjna |
| 2 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 1,000 | 0,170 | wiatroizolacja | — |
| 3 | Pustka wentylowana 40 mm (ruszt lamel) | 40,000 | 0,250 | pustka powietrzna | — |
| 4 | Podsufitka zewnętrzna: płyta włóknocementowa 12 mm na ruszcie, RAL 7016 | 12,000 | 0,350 | wykonczenie | — |

**Tabela 11. SUF-G — Docieplenie spodu stropu garażu pasem 1,0 m przy ścianach osi E i 2 (wełna 10 cm + płyta) — ograniczenie mostka (J2)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 100,000 | 0,035 | izolacja cieplna | warstwa nośna / konstrukcyjna |
| 2 | Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne) | 10,000 | 0,820 | tynk | — |

**Tabela 12. SD1 — Stropodach bryły A (P2): membrana TPO, PIR spadkowy 12–32 cm (śr. 22), paroizolacja z Al, płyta ŻB 22 cm, tynk; spadek ≥ 2 % do wpustów WP1/WP2**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | 2,000 | 0,200 | hydroizolacja | — |
| 2 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 220,000 | 0,022 | izolacja cieplna | spadkowa 120–320 mm |
| 3 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | paroizolacja | — |
| 4 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 5 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | tynk | — |

**Tabela 13. SD2 — Stropodach nad P1 (pola pn. poza bryłą A): żwir 5 cm, włóknina, membrana TPO, PIR spadkowy 14–26 cm, paroizolacja, płyta ŻB 22 cm**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Żwir płukany 16/32 mm (balast dachu P1, opaska przy attyce) | 50,000 | 2,000 | balast | — |
| 2 | Włóknina ochronna PP 300 g/m² | 4,000 | 0,500 | filtracja/ochrona | — |
| 3 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | 2,000 | 0,200 | hydroizolacja | — |
| 4 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 200,000 | 0,022 | izolacja cieplna | spadkowa 140–260 mm |
| 5 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | paroizolacja | — |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 7 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | tynk | — |

**Tabela 14. DZ1 — Dach zielony ekstensywny NIEUŻYTKOWY nad garażem (pom. nieogrzewane) i pasem gospodarczym: substrat 8 cm, geowłóknina, mata drenażowa, włóknina, bariera przeciwkorzenna, 2 × papa SBS, PIR spadkowy 12–24 cm, paroizolacja, płyta ŻB 24 cm (dwukierunkowa); opaska żwirowa 0,5 m przy attykach i wpustach; nad garażem: pole PV biosolarne (8 modułów)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Substrat ekstensywny 8 cm z matą rozchodnikową (sedum) | 80,000 | 0,800 | substrat roślinny | — |
| 2 | Geowłóknina filtracyjna PP 150 g/m² | 2,000 | 0,500 | filtracja/ochrona | — |
| 3 | Mata drenażowo-retencyjna HDPE 25 mm (dach zielony) | 25,000 | 0,500 | drenaż | — |
| 4 | Włóknina ochronna PP 300 g/m² | 4,000 | 0,500 | filtracja/ochrona | — |
| 5 | Bariera przeciwkorzenna PE-HD 0,5 mm (PN-EN 13948) | 0,500 | 0,400 | bariera korzenna | — |
| 6 | Hydroizolacja 2 × papa SBS (podkładowa + wierzchniego krycia, dach zielony) | 9,500 | 0,230 | hydroizolacja | — |
| 7 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 180,000 | 0,022 | izolacja cieplna | spadkowa 120–240 mm |
| 8 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | paroizolacja | — |
| 9 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 240,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |

**Tabela 15. OK1 — Płyta wysunięta (okap, daszek, krawędź ST2/ST3): obróbka/membrana ze spadkiem 2 % od budynku, płyta ŻB C30/37 z łącznikiem termoizolacyjnym (ETA), podsufitka z okapnikiem**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | 2,000 | 0,200 | hydroizolacja | — |
| 2 | Żelbet C30/37 XC4/XF1 (krawędzie płyt wysuniętych, attyki, belki) | 300,000 | 2,500 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Podsufitka zewnętrzna: płyta włóknocementowa 12 mm na ruszcie, RAL 7016 | 12,000 | 0,350 | wykonczenie | — |

### Przegrody wewnętrzne

**Tabela 16. SW18 — Ściana wewnętrzna nośna: silikat 18, tynk gipsowy obustronnie**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |

**Tabela 17. SWZB — Ściana wewnętrzna nośna żelbetowa 18 cm (trzon klatki na P0 — usztywnienie w kierunku x, J2)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |
| 2 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 180,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |

**Tabela 18. SCZB15 — Ściana środkowa klatki schodowej: żelbet C25/30 15 cm, monolityczna z płytami biegów i spoczników, ciągła P0–P2 (przez poziomy stropów), zakotwiona w podciągach B8/B9/B10 osi 3 (audyt A2 I-2)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 150,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |

**Tabela 19. DZ12 — Ścianka działowa: silikat 12 + tynk gipsowy obustronnie (R'w ≥ 45 dB)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |
| 2 | Bloczek wapienno-piaskowy 12 cm, kl. 15 (ścianki działowe, licowy w klatce) | 120,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |

**Tabela 20. DZGK — Ścianka działowa GK 12,5 cm z kasetą drzwi przesuwnych chowanych (2 × GK impregnowana 12,5 mm obustronnie, kaseta stalowa 7,5 cm z wełną poza strefą kasety; R'w ≥ 40 dB)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | wykonczenie | — |
| 2 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 75,000 | 0,035 | izolacja cieplna | warstwa nośna / konstrukcyjna |
| 3 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | wykonczenie | — |

**Tabela 21. DZ18A — Ścianka działowa akustyczna pom. technicznego z centralą (P2): silikat 18 kl. 15 na zaprawie cienkowarstwowej, tynk gipsowy obustronnie, bez funkcji nośnej, styk ze stropem wypełniony elastycznie; cel R'A1 ≥ 50 dB do sprawdzenia w PT (audyt A3 I-8; W-066, W-230)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | konstrukcja | warstwa nośna / konstrukcyjna |
| 3 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | tynk | — |

**Tabela 22. GK10 — Obudowa szachtu SI: 2 × GKF 12,5 + profil CW 50 z wełną + 2 × GKF 12,5 (EI 30)**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | wykonczenie | — |
| 2 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 50,000 | 0,035 | izolacja cieplna | warstwa nośna / konstrukcyjna |
| 3 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | wykonczenie | — |

**Tabela 23. SGL — Ścianka szklana wiatrołap/hol: VSG w ramie aluminiowej z drzwiami szklanymi 0,90 m**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Ścianka szklana VSG 2 × 8 mm w ramie aluminiowej (wiatrołap / hol) | 50,000 | 1,000 | wykonczenie | warstwa nośna / konstrukcyjna |

**Tabela 24. POD-1 — Strop międzykondygnacyjny: deska dębowa, jastrych z ogrzewaniem podł., EPS 100, EPS T (akustyczny), płyta ŻB 22 cm, tynk**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Deska warstwowa dębowa 15 mm, klejona | 15,000 | 0,180 | konstrukcja | — |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | wykonczenie | — |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 40,000 | 0,038 | izolacja cieplna | — |
| 4 | Styropian elastyfikowany EPS T (akustyczny, pod jastrychem) | 30,000 | 0,040 | izolacja cieplna | — |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 6 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | tynk | — |

**Tabela 25. POD-1L — Strop międzykondygnacyjny — łazienki, WC, pralnia: gres na hydroizolacji podpłytkowej**

| Lp. | Materiał / wyrób (parametry wymagane) | d [mm] | λ [W/(m·K)] | Funkcja | Uwagi |
|---|---|---|---|---|---|
| 1 | Płytki gresowe 60×120 na kleju C2TE S1 | 12,000 | 1,300 | wykonczenie | — |
| 2 | Hydroizolacja podpłytkowa (masa uszczelniająca + taśmy), strefy mokre | 3,000 | 0,200 | hydroizolacja | — |
| 3 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | wykonczenie | — |
| 4 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 40,000 | 0,038 | izolacja cieplna | — |
| 5 | Styropian elastyfikowany EPS T (akustyczny, pod jastrychem) | 30,000 | 0,040 | izolacja cieplna | — |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | konstrukcja | warstwa nośna / konstrukcyjna |
| 7 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | tynk | — |

## Analiza akustyczna (§ 23 pkt 4a RPB) — nie dotyczy — § 23 pkt 4a RPB

**Nie dotyczy.** Zgodnie z § 23 pkt 4a RPB (dodanym rozp. Dz.U. 2023 poz. 2405) analizę w zakresie rozwiązań
technicznych i materiałowych mających na celu spełnienie wymagań akustycznych sporządza się „w przypadku budynku
mieszkalnego jednorodzinnego z dwoma lokalami, budynku mieszkalnego jednorodzinnego w zabudowie szeregowej lub
bliźniaczej lub budynku mieszkalnego wielorodzinnego”. Projektowany budynek jest wolnostojącym budynkiem
mieszkalnym jednorodzinnym z **jednym** lokalem (rejestr W-231).

Wymagania WT § 326 ust. 1–3 obowiązują niezależnie od analizy: poziom hałasu w pomieszczeniach wg PN-B-02151-2:2018-01
(WT §326 ust. 1, zał. 1 (Dz.U. 2023 poz. 2442); W-230), izolacyjność akustyczna przegród wg PN-B-02151-3:2015-10 (WT §326 ust. 2, zał. 1; W-230). Rozwiązania ograniczające przenoszenie
dźwięku przyjęte w modelu:

* DZ12 — Ścianka działowa: silikat 12 + tynk gipsowy obustronnie (R'w ≥ 45 dB)
* DZGK — Ścianka działowa GK 12,5 cm z kasetą drzwi przesuwnych chowanych (2 × GK impregnowana 12,5 mm obustronnie, kaseta stalowa 7,5 cm z wełną poza strefą kasety; R'w ≥ 40 dB)
* DZ18A — Ścianka działowa akustyczna pom. technicznego z centralą (P2): silikat 18 kl. 15 na zaprawie cienkowarstwowej, tynk gipsowy obustronnie, bez funkcji nośnej, styk ze stropem wypełniony elastycznie; cel R'A1 ≥ 50 dB do sprawdzenia w PT (audyt A3 I-8; W-066, W-230)
* POD-1 — Strop międzykondygnacyjny: deska dębowa, jastrych z ogrzewaniem podł., EPS 100, EPS T (akustyczny), płyta ŻB 22 cm, tynk
* D4 — drzwi pom. technicznego 0,90 × 2,10 z kratką, akustyczne R_w ≥ 32 dB
* D4A — drzwi pom. technicznego z centralą (P2) 0,90 × 2,10, akustyczne R_w ≥ 32 dB, BEZ kratki, uszczelka obwodowa i próg z uszczelką opadającą (A3 I-8; W-230)

## Obliczenia cieplno-wilgotnościowe przegród i węzłów — W-243…W-250

### Współczynniki przenikania ciepła U (PN-EN ISO 6946, PN-EN ISO 13370) — PN-EN ISO 6946:2017-10

Opory przejmowania ciepła R_si/R_se wg kierunku strumienia (PN-EN ISO 6946:2017-10 p. 6.8); warstwy niejednorodne
— metoda kresów (p. 6.7.2); poprawki ΔU wg zał. F (nieszczelności ΔU_g, łączniki ΔU_f, dach odwrócony ΔU_r);
izolacja spadkowa — zał. C (U średnie po powierzchni). Wymagania U_C,max — WT zał. 2 pkt 1.1–1.2 (W-243, W-244);
cele projektowe — W-245 [ZAŁ]. Założenia obliczeń: Grunt: piasek — λ = 2,0 W/(m·K), ρc = 2,0 MJ/(m³·K) (PN-EN ISO 13370 tab. kategorii gruntu; opinia geotechniczna przykładowa: piaski średnie) [NZW]; f_g1 = 1,45, G_w = 1,00 (ZWG ≈ 3,8 m p.p.t. > 1 m), θ_m,e = 7,9 °C [NZW]; Stolarka: U_g, U_f, Ψ_g, szerokości ram, g_n — dane przykładowe typowych wyrobów (dane/wyroby_przykladowe.yaml); do zastąpienia deklaracjami wybranego producenta [DANE PRZYKŁADOWE – FIKCYJNE]; Łączniki ETICS: n_f = 6,0 szt./m², χ_p = 0,002 W/K (ΔU_f = n_f·χ_p, PN-EN ISO 6946:2017 zał. F.3) [DANE PRZYKŁADOWE – FIKCYJNE]; Nieszczelności w warstwie izolacji: poziom 1 (ΔU'' = 0,01 W/(m²·K)), chyba że wykazano poziom 0 [NZW]; Zacienienie stałe (okapy — płyty wysunięte, lamele) — F_sh z danych godzinowych TMY Poznań i położenia Słońca; model izotropowy nieba, ρ_g = 0,2 [ZAŁ].

**Tabela 26. Współczynniki przenikania ciepła przegród zewnętrznych — zestawienie**

| Przegroda | Rola | R_T [m²·K/W] | U₀ [W/(m²·K)] | ΔU [W/(m²·K)] | U [W/(m²·K)] | U_max [W/(m²·K)] | U_cel [W/(m²·K)] | Ocena |
|---|---|---|---|---|---|---|---|---|
| POD-0 | podłoga na gruncie | 7,705 | 0,130 | 0,000 | 0,110 | 0,300 | 0,200 | spełnia |
| POD-G | podloga_grunt_nieogrz | 8,727 | 0,115 | 0,000 | 0,100 | — | — | — |
| SZ1 | ściana zewnętrzna | 6,872 | 0,146 | 0,021 | 0,170 | 0,200 | 0,150 | spełnia |
| SWG | ściana do pom. nieogrzewanego | 3,938 | 0,254 | 0,020 | 0,270 | 0,300 | 0,250 | spełnia |
| DZ1 | stropodach/dach | 8,648 | 0,116 | 0,009 | 0,130 | 0,150 | 0,120 | spełnia |
| SD2 | stropodach/dach | 9,412 | 0,106 | 0,009 | 0,120 | 0,150 | 0,120 | spełnia |
| SD1 | stropodach/dach | 10,288 | 0,097 | 0,009 | 0,110 | 0,150 | 0,120 | spełnia |
| SZ2 | ściana zewnętrzna | 6,181 | 0,162 | 0,009 | 0,170 | 0,200 | 0,150 | spełnia |
| SZL | ściana zewnętrzna | 10,355 | 0,097 | 0,002 | 0,099 | 0,200 | 0,150 | spełnia |
| ST2Z | strop nad powietrzem zewn. | 8,217 | 0,122 | 0,005 | 0,130 | 0,150 | — | spełnia |
| POD-0 (grunt) | podłoga na gruncie — U_equiv wg PN-EN ISO 13370 | 7,535 | 0,112 | — | 0,110 | 0,300 | 0,200 | spełnia |

U — wartość do bilansu (U₀ + ΔU; dla izolacji spadkowej — średnia wg zał. C), 2 cyfry znaczące. Dla podłogi na gruncie R_T oznacza R_f (bez R_si/R_se).

*Źródło: lamela.obliczenia.fizyka (u_przegrody, grunt); wymagania.yaml — sekcja energia*

Podłoga na gruncie (PN-EN ISO 13370:2017-09): A = 111,0 m², P = 51,2 m, B' = 4,34 m,
d_t = 15,89 m, U = 0,11 W/(m²·K). Izolacja krawędziowa
pozioma D = 1,00 m, d_n = 0,10 m,
λ_n = 0,036 W/(m·K) — R_n ≥ R_min = 2,0 m²·K/W:
spełnia (WT zał. 2 pkt 1.4; W-246).

### Obliczenie U — układy warstw z oporami cieplnymi

**Tabela 27. POD-0 — podłoga na gruncie: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,170 | dol |
| 1 | Deska warstwowa dębowa 15 mm, klejona | 15,000 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | 0,054 | jednorodna |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 65,000 | 0,038 | 1,711 | jednorodna |
| 4 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | 5,000 | 0,230 | 0,022 | jednorodna |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 250,000 | 2,300 | 0,109 | jednorodna |
| 6 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 200,000 | 0,036 | 5,556 | jednorodna |
| 7 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | 0,001 | jednorodna |
| 8 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | 200,000 | 2,000 | 0,000 | grunt |
|  | R_se | — | — | 0,000 |  |
|  | R_T (kresy: —) | 800,200 | — | 7,705 |  |

U₀ = 1/R_T = 0,130; ΔU_g = 0,000, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,107; **U = 0,11 W/(m²·K)** (U_max = 0,30; WT zał. 2 pkt 1.1 lp. 6 (W-243); cel: R6 3.2 (R3: 0,25) [ZAŁ]).

U_equiv wg PN-EN ISO 13370: A = 111,03 m², P = 51,21 m, B' = 4,34 m, d_t = 15,89 m

**Tabela 28. POD-G — podloga_grunt_nieogrz: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,170 | dol |
| 1 | Posadzka żywiczna epoksydowa antypoślizgowa R11 (garaż) | 3,000 | 0,200 | 0,015 | jednorodna |
| 2 | Jastrych cementowy CT-C30-F5 zbrojony (siatka/włókna), dylatacja obwodowa — posadzka garażu na XPS | 92,000 | 1,200 | 0,077 | jednorodna |
| 3 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | 0,001 | jednorodna |
| 4 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 100,000 | 0,036 | 2,778 | jednorodna |
| 5 | Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej | 5,000 | 0,230 | 0,022 | jednorodna |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 250,000 | 2,300 | 0,109 | jednorodna |
| 7 | Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) | 200,000 | 0,036 | 5,556 | jednorodna |
| 8 | Folia PE 0,2 mm — warstwa rozdzielająca pod XPS (nie pełni funkcji paroizolacji) | 0,200 | 0,330 | 0,001 | jednorodna |
| 9 | Podsypka piaskowa zagęszczona (I_s ≥ 0,98) | 200,000 | 2,000 | 0,000 | grunt |
|  | R_se | — | — | 0,000 |  |
|  | R_T (kresy: —) | 850,400 | — | 8,727 |  |

U₀ = 1/R_T = 0,115; ΔU_g = 0,000, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,103; **U = 0,10 W/(m²·K)** (U_max = —; WT zał. 2 pkt 1.1 lp. 6 (W-243); cel: R6 3.2 (R3: 0,25) [ZAŁ]).

U_equiv wg PN-EN ISO 13370: A = 37,42 m², P = 24,56 m, B' = 3,05 m, d_t = 17,94 m

**Tabela 29. SZ1 — ściana zewnętrzna: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,130 | poziomo |
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | 0,200 | jednorodna |
| 3 | Styropian grafitowy EPS 031 (ETICS, NRO w systemie) | 200,000 | 0,031 | 6,452 | jednorodna |
| 4 | ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (biały / jasnoszary NCS S 1500-N) | 10,000 | 0,800 | 0,012 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: —) | 405,000 | — | 6,872 |  |

U₀ = 1/R_T = 0,146; ΔU_g = 0,009, ΔU_f = 0,012, ΔU_r = 0,000; U_c = 0,166; **U = 0,17 W/(m²·K)** (U_max = 0,20; WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ]).

**Tabela 30. SWG — ściana do pom. nieogrzewanego: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,130 | poziomo |
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | 0,200 | jednorodna |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 120,000 | 0,035 | 3,429 | jednorodna |
| 4 | Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne) | 10,000 | 0,820 | 0,012 | jednorodna |
|  | R_se | — | — | 0,130 |  |
|  | R_T (kresy: —) | 325,000 | — | 3,938 |  |

U₀ = 1/R_T = 0,254; ΔU_g = 0,008, ΔU_f = 0,012, ΔU_r = 0,000; U_c = 0,273; **U = 0,27 W/(m²·K)** (U_max = 0,30; WT zał. 2 pkt 1.1 lp. 2 (ściana dom–garaż) (W-243); cel: R6 3.2 [ZAŁ]).

**Tabela 31. DZ1 — stropodach/dach: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,100 | gora |
| 9 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 240,000 | 2,300 | 0,104 | jednorodna |
| 8 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | 0,017 | jednorodna |
| 7 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 180,000 | 0,022 | 8,182 | klin |
| 6 | Hydroizolacja 2 × papa SBS (podkładowa + wierzchniego krycia, dach zielony) | 9,500 | 0,230 | 0,041 | jednorodna |
| 5 | Bariera przeciwkorzenna PE-HD 0,5 mm (PN-EN 13948) | 0,500 | 0,400 | 0,001 | jednorodna |
| 4 | Włóknina ochronna PP 300 g/m² | 4,000 | 0,500 | 0,008 | jednorodna |
| 3 | Mata drenażowo-retencyjna HDPE 25 mm (dach zielony) | 25,000 | 0,500 | 0,050 | jednorodna |
| 2 | Geowłóknina filtracyjna PP 150 g/m² | 2,000 | 0,500 | 0,004 | jednorodna |
| 1 | Substrat ekstensywny 8 cm z matą rozchodnikową (sedum) | 80,000 | 0,800 | 0,100 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: —) | 545,000 | — | 8,648 |  |

U₀ = 1/R_T = 0,116; ΔU_g = 0,009, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,125; izolacja spadkowa: U_śr = 0,120 (zał. C — wzór dla kształtu 'prostokat'); **U = 0,13 W/(m²·K)** (U_max = 0,15; WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ]).

warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 12,0 cm, d_max = 24,0 cm

**Tabela 32. SD2 — stropodach/dach: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,100 | gora |
| 7 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | 0,025 | jednorodna |
| 6 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | 0,096 | jednorodna |
| 5 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | 0,017 | jednorodna |
| 4 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 200,000 | 0,022 | 9,091 | klin |
| 3 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | 2,000 | 0,200 | 0,010 | jednorodna |
| 2 | Włóknina ochronna PP 300 g/m² | 4,000 | 0,500 | 0,008 | jednorodna |
| 1 | Żwir płukany 16/32 mm (balast dachu P1, opaska przy attyce) | 50,000 | 2,000 | 0,025 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: —) | 490,000 | — | 9,412 |  |

U₀ = 1/R_T = 0,106; ΔU_g = 0,009, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,116; izolacja spadkowa: U_śr = 0,109 (zał. C — wzór dla kształtu 'prostokat'); **U = 0,12 W/(m²·K)** (U_max = 0,15; WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ]).

warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 14,0 cm, d_max = 26,0 cm

**Tabela 33. SD1 — stropodach/dach: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,100 | gora |
| 5 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | 0,025 | jednorodna |
| 4 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | 0,096 | jednorodna |
| 3 | Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) | 4,000 | 0,230 | 0,017 | jednorodna |
| 2 | Płyty PIR z okładziną (izolacja spadkowa stropodachów) | 220,000 | 0,022 | 10,000 | klin |
| 1 | Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) | 2,000 | 0,200 | 0,010 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: —) | 456,000 | — | 10,288 |  |

U₀ = 1/R_T = 0,097; ΔU_g = 0,009, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,107; izolacja spadkowa: U_śr = 0,104 (zał. C — wzór dla kształtu 'prostokat'); **U = 0,11 W/(m²·K)** (U_max = 0,15; WT zał. 2 pkt 1.1 lp. 5 (W-243); cel: R6 3.2; R3 3.6 [ZAŁ]).

warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C (zał. C — wzór dla kształtu 'prostokat'); d_min = 12,0 cm, d_max = 32,0 cm

**Tabela 34. SZ2 — ściana zewnętrzna: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,130 | poziomo |
| 1 | Tynk gipsowy maszynowy 1,5 cm | 15,000 | 0,400 | 0,037 | jednorodna |
| 2 | Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej | 180,000 | 0,900 | 0,200 | jednorodna |
| 3 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | 200,000 | 0,035 | 5,714 | jednorodna |
| 4 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 10,000 | 0,170 | 0,059 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: —) | 405,000 | — | 6,181 |  |

U₀ = 1/R_T = 0,162; ΔU_g = 0,009, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,170; **U = 0,17 W/(m²·K)** (U_max = 0,20; WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ]).

**Tabela 35. SZL — ściana zewnętrzna: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,130 | poziomo |
| 1 | Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach) | 25,000 | 0,250 | 0,100 | jednorodna |
| 2 | Płyta OSB/3 15 mm (usztywnienie i warstwa szczelności ściany A') | 15,000 | 0,130 | 0,115 | jednorodna |
| 3 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 200,000 | 0,046 | 4,310 | niejednorodna |
| 4 | Płyta drewnopochodna wiatroizolacyjna DWD/MDF.RWH 16 mm | 16,000 | 0,100 | 0,160 | jednorodna |
| 5 | Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) | 180,000 | 0,035 | 5,143 | jednorodna |
| 6 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 4,000 | 0,170 | 0,024 | jednorodna |
|  | R_se | — | — | 0,040 |  |
|  | R_T (kresy: 10,69/10,02) | 440,000 | — | 10,355 |  |

U₀ = 1/R_T = 0,097; ΔU_g = 0,002, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,099; **U = 0,10 W/(m²·K)** (U_max = 0,20; WT zał. 2 pkt 1.1 lp. 1 (t_i ≥ 16 °C) (W-243); cel: R6 3.2 (sprzeczność S-3: R3 0,17) [ZAŁ]).

ΣΔU < 3 % U — poprawki mogłyby zostać pominięte (zał. F); przyjęto je zachowawczo

**Tabela 36. ST2Z — strop nad powietrzem zewn.: obliczenie U**

| Lp. | Warstwa | d [mm] | λ [W/(m·K)] | R [m²·K/W] | Rodzaj |
|---|---|---|---|---|---|
|  | R_si | — | — | 0,170 | dol |
| 1 | Deska warstwowa dębowa 15 mm, klejona | 15,000 | 0,180 | 0,083 | jednorodna |
| 2 | Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego | 65,000 | 1,200 | 0,054 | jednorodna |
| 3 | Styropian podłogowy EPS 100-038 (pod jastrychem) | 40,000 | 0,038 | 1,053 | jednorodna |
| 4 | Styropian elastyfikowany EPS T (akustyczny, pod jastrychem) | 30,000 | 0,040 | 0,750 | jednorodna |
| 5 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | 0,096 | jednorodna |
| 6 | Tynk gipsowy maszynowy 1,5 cm | 10,000 | 0,400 | 0,025 | jednorodna |
| 7 | Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany) | 220,000 | 2,300 | 0,096 | jednorodna |
| 8 | Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) | 200,000 | 0,035 | 5,714 | jednorodna |
| 9 | Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) | 1,000 | 0,170 | 0,006 | jednorodna |
| 10 | Pustka wentylowana 40 mm (ruszt lamel) | 40,000 | — | 0,000 | pustka dw |
| 11 | Podsufitka zewnętrzna: płyta włóknocementowa 12 mm na ruszcie, RAL 7016 | 12,000 | 0,350 | 0,000 | pominieta |
|  | R_se | — | — | 0,170 |  |
|  | R_T (kresy: —) | 853,000 | — | 8,217 |  |

U₀ = 1/R_T = 0,122; ΔU_g = 0,005, ΔU_f = 0,000, ΔU_r = 0,000; U_c = 0,127; **U = 0,13 W/(m²·K)** (U_max = 0,15; WT zał. 2 pkt 1.1 lp. 5 („nad przejazdami”) — spód wspornika P2 (W-243) [INT]).

### Mostki cieplne — ψ i f_Rsi (PN-EN ISO 10211, PN-EN ISO 13788) — PN-EN ISO 10211, 13788, 14683

Węzły liniowe obliczono numerycznie w modelu 2D (PN-EN ISO 10211:2017-09; karty węzłów:
`projekt/08_obliczenia/mostki/katalog_mostkow.md`). ψ_oi — w systemie wymiarów wewnętrznych całkowitych.
Do bilansu (H_TB) przyjęto wartości projektowe z sekcji `wezly` modelu (runda poprawek; węzły złożone —
średnia ważona podwęzłów). Mostki punktowe χ — wartości przykładowe [DANE PRZYKŁADOWE – FIKCYJNE] do zastąpienia
deklaracją (ETA) wybranych łączników. Kryterium kondensacji powierzchniowej i pleśni:
f_Rsi ≥ f_Rsi,wym = max(f_Rsi,kryt = 0,661 — miesiąc krytyczny 3,
φ_i = 50 % przy θ_i = 20 °C (WT zał. 2 pkt 2.2.2); 0,72 — WT zał. 2 pkt 2.2.1) = **0,720**.

**Tabela 37. Mostki cieplne liniowe — ψ, długości, f_Rsi**

| Węzeł | Opis | ψ_oi karta [W/(m·K)] | ψ projekt [W/(m·K)] | l [m] | ψ·l [W/K] | f_Rsi karta | f_Rsi projekt | f_Rsi ≥ wym. | Detal |
|---|---|---|---|---|---|---|---|---|---|
| WZ-01 | Attyka stropodachu bryły A (D1) | 0,086 | 0,086 | 19,940 | 1,715 | 0,932 | 0,932 | tak | D-04 (PT-AR-D-03) |
| WZ-02 | Attyki dachów P1 (D2, D3) — poza ścianami bryły A | 0,171 | 0,171 | 13,410 | 2,293 | 0,900 | 0,900 | tak | D-05 (PT-AR-D-03) |
| WZ-03 | Attyka dachu zielonego nad pasem gospodarczym (linia D, część ogrzewan… | 0,195 | 0,195 | 7,170 | 1,398 | 0,890 | 0,890 | tak | — |
| WZ-04 | Okap E (PL-E) i daszek wejścia — łącznik termoizolacyjny | 0,128 | 0,128 | 22,470 | 2,876 | 0,929 | 0,929 | tak | D-09 (PT-AR-D-02) |
| WZ-05 | Krawędź ST2 (PL-2) — łącznik termoizolacyjny pod bryłą A | 0,134 | 0,134 | 18,710 | 2,507 | 0,927 | 0,927 | tak | D-08 (PT-AR-D-04) |
| WZ-06 | Krawędź ST3 (PL-3) — łącznik termoizolacyjny przy attyce bryły A | 0,205 | 0,205 | 24,300 | 4,981 | 0,889 | 0,889 | tak | — |
| WZ-07 | Strop P2 nad powietrzem zewnętrznym (ST2Z) — krawędzie wspornika bryły… | a: 0,152; b: −0,061 | 0,046 | 11,440 | 0,526 | 0,851 | 0,851 | tak | D-08 (PT-AR-D-04) |
| WZ-08 | Cokół: ściana zewn. – płyta fundamentowa na XPS (część ogrzewana) | 0,100 | 0,100 | 27,770 | 2,777 | 0,903 | 0,903 | tak | D-01 (PT-AR-D-01) |
| WZ-09 | Połączenia dom–garaż nieogrzewany (ściany osi E i 2 z płytą i stropem;… | a: 0,301; b: 0,071; c: 0,081 | 0,188 | 24,510 | 4,608 | 0,836 | 0,836 | tak | D-10 (PT-AR-D-05) |
| WZ-10 | Strop pośredni ST1/ST2 – ściana zewn. z ETICS ciągłym (wieniec) | 0,000 | 0,000 | 18,200 | 0,000 | 0,963 | 0,963 | tak | — |
| WZ-11 | Ościeża okien/drzwi — ciepły montaż (rama 5 cm w murze, 4 cm w izolacj… | 0,005 | 0,005 | 96,280 | 0,481 | 0,930 | 0,930 | tak | D-02 (PT-AR-D-02) |
| WZ-11N | Nadproża — BEZ kaset osłon w ociepleniu (kasety w okapach / ramie C / … | 0,008 | 0,008 | 45,030 | 0,360 | 0,938 | 0,938 | tak | D-02 (PT-AR-D-02) |
| WZ-11P | Podokienniki — parapet zewn. z okapnikiem na profilu z XPS | 0,006 | 0,006 | 29,420 | 0,177 | 0,911 | 0,911 | tak | D-02 (PT-AR-D-02) |
| WZ-11T | Progi HS / drzwi zewn. na płycie P0 — profil progowy termoizolacyjny n… | 0,118 | 0,118 | 15,670 | 1,849 | 0,845 | 0,845 | tak | D-03 (PT-AR-D-01), D-02 (PT-AR-D-02) |
| WZ-12 | Narożniki wypukłe ścian zewnętrznych | 0,066 | 0,066 | 40,050 | 2,643 | 0,926 | 0,926 | tak | — |
| WZ-16 | Belki wspornikowe B4/B5 i belka B3 w linii izolacji wspornika bryły A … | a: 0,194; b: 0,123 | 0,159 | 2,020 | 0,321 | 0,854 | 0,854 | tak | D-08 (PT-AR-D-04) |
| WZ-X1 | Dachy D2/D3 (SD2) – ściana SZ1 bryły A wyższej kondygnacji na krawędzi… | 0,022 | 0,022 | 13,790 | 0,303 | 0,964 | 0,964 | tak | — |
| WZ-X2 | Dach D4 (DZ1) – ściana SZ1 bryły B na krawędzi (pas gospodarczy, pomie… | 0,022 | 0,022 | 2,790 | 0,061 | 0,964 | 0,964 | tak | — |

*Źródło: model/budynek.yaml — wezly; projekt/08_obliczenia/mostki/zestawienie_mostkow.json*

**Tabela 38. Mostki cieplne punktowe χ**

| Węzeł | Opis | n [szt.] | χ [W/K] | n·χ [W/K] | Źródło χ |
|---|---|---|---|---|---|
| WZ-13 | Konsole rusztu lamel (przekładka termiczna) | 50,000 | 0,010 | 0,500 | wartość przykładowa — konsola mocowania lamel (przekładka termiczna) [DANE PRZYKŁADOWE – FIKCYJNE] |
| WZ-14 | Konsole ramy boksu C i linii D (PL-C1/PL-C2/PL-D; punktowe, przekładka termiczna) | 17,000 | 0,010 | 0,170 | wartość przykładowa — punktowa kotwa stalowa przez izolację [DANE PRZYKŁADOWE – FIKCYJNE] |
| WZ-15 | Przejścia instalacji przez przegrody zewnętrzne (wywiewka K1, czerpnia, wyrzutnia, PC, wpusty, przyłącza) | 16,000 | 0,005 | 0,080 | wartość przykładowa — przejście instalacji przez przegrodę zewnętrzną (mankiet) [DANE PRZYKŁADOWE – FIKCYJNE] |

Współczynnik strat przez mostki cieplne **H_TB = Σψ·l + Σχ = 30,63 W/K** (moduł energii, ψ projektowe
z modelu; do charakterystyki energetycznej w PT-3 IS).

**Tabela 39. Czynnik temperaturowy f_Rsi przegród w polu (wymagane ≥ 0,720)**

| Przegroda | Opis | f_Rsi | Metoda | Ocena |
|---|---|---|---|---|
| POD-0 | przegroda (podloga_grunt), U = 0,11 | 0,973 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SZ1 | przegroda (sciana_zewn), U = 0,17 | 0,958 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SWG | przegroda (sciana_nieogrz), U = 0,27 | 0,932 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| DZ1 | przegroda (dach), U = 0,13 | 0,968 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SD2 | przegroda (dach), U = 0,12 | 0,970 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SD1 | przegroda (dach), U = 0,11 | 0,972 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SZ2 | przegroda (sciana_zewn), U = 0,17 | 0,957 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| SZL | przegroda (sciana_zewn), U = 0,099 | 0,975 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |
| ST2Z/P2/zewn | przegroda (strop_zewn), U = 0,13 | 0,968 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | spełnia |

*Źródło: lamela.obliczenia.fizyka.kondensacja — f_rsi_przegrody, f_rsi_min*

### Kondensacja międzywarstwowa (PN-EN ISO 13788, metoda Glasera) — PN-EN ISO 13788:2013-05

Obliczenie miesięczne dla przegród zewnętrznych i oddzielających od garażu. Założenia: Glaser: warunki wewnętrzne — klasa wilgotności 3 (budynki o nieznanym zagęszczeniu), θ_i = 20 °C, p_i = p_e + 1,10·Δp [ZAŁ]; Kryterium akumulacji kondensatu 0,5 kg/m² (DIN 4108-3 — kryterium literaturowe) [ZAŁ]; Dane klimatyczne: typowy rok meteorologiczny ISO (PN-EN ISO 15927-4:2007), stacja Poznań (Ławica) (WMO 12330), okres 1971–2000; Ministerstwo Inwestycji i Rozwoju (archiwum) — „Dane do obliczeń energetycznych budynków”, pliki wmo123300iso.zip (godzinowy) i wmo123300iso_stat.txt (statystyki miesięczne); https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow (pobrano 2026-09-25).
Wymaganie: brak kondensacji albo kondensacja okresowa wysychająca w cyklu rocznym (WT zał. 2 pkt 2.2.5; W-248).

**Tabela 40. Kondensacja międzywarstwowa — wyniki**

| Przegroda | Rola | Kondensacja | M_a,max [g/m²] | Wysycha | s_d paroizolacji istn. [m] | s_d wym. (brak kond.) [m] | Ocena |
|---|---|---|---|---|---|---|---|
| SZ1 | sciana zewn | nie | 0,000 | tak | 0,150 | 0,000 | dopuszczalna — brak kondensacji międzywarstwowej |
| SWG | sciana nieogrz | nie | 0,000 | tak | — | 0,000 | dopuszczalna — brak kondensacji międzywarstwowej |
| DZ1 | dach | tak | 0,243 | tak | 1 500,000 | — | dopuszczalna — kondensacja okresowa, M_a,max = 0 g/m² — wysycha w okresie letnim (dopuszczalna wg WT zał. 2 pkt 2.2.5) |
| SD2 | dach | tak | 0,295 | tak | 1 500,000 | — | dopuszczalna — kondensacja okresowa, M_a,max = 0 g/m² — wysycha w okresie letnim (dopuszczalna wg WT zał. 2 pkt 2.2.5) |
| SD1 | dach | tak | 0,338 | tak | 1 500,000 | — | dopuszczalna — kondensacja okresowa, M_a,max = 0 g/m² — wysycha w okresie letnim (dopuszczalna wg WT zał. 2 pkt 2.2.5) |
| SZ2 | sciana zewn | nie | 0,000 | tak | 0,150 | 0,000 | dopuszczalna — brak kondensacji międzywarstwowej |
| SZL | sciana zewn | nie | 0,000 | tak | 3,000 | 0,000 | dopuszczalna — brak kondensacji międzywarstwowej |
| ST2Z | strop zewn | nie | 0,000 | tak | — | 0,000 | dopuszczalna — brak kondensacji międzywarstwowej |

strona zimna — przestrzeń nieogrzewana 0.13: θ_u,n = 20 − b_u·(20 − θ_e,n), b_u = 0,80; ciśnienie pary jak na zewnątrz

dach zielony: metoda Glasera (stan ustalony, bez transportu wilgoci w cieczy) ma ograniczoną miarodajność dla warstw nad hydroizolacją — ocena warstw pod hydroizolacją

*Źródło: lamela.obliczenia.fizyka.kondensacja — glaser, wymagane_sd_paroizolacji*

Kontrola ciągłości warstw funkcjonalnych w przekroju przegród (izolacja, szczelność, paroizolacja, ochrona przed wodą): **brak braków** w SZ1, SWG, POD-0L, POD-0, DZ1, SD2, SD1, SZ2, SZL, ST2Z.

## Zestawienie stolarki okiennej i drzwiowej — W-317, W-244, W-247, W-249

Zestawienie stolarki wygenerowano z modelu (sekcje `otwory` i `stolarka`), grupując otwory według symbolu
(W-317). Wymiary — w świetle otworu w murze. Parametry cieplne: U_w obliczone wg PN-EN ISO 10077-1:2017-10
dla wymiarów otworu i danych przykładowego wyrobu [DANE PRZYKŁADOWE – FIKCYJNE]; U_w wym. — wartość wymagana dla wyrobu
(model); U_max — WT zał. 2 pkt 1.2 (W-244). Szczelność: klasa ≥ 3 (WT zał. 2 pkt 2.3.2 (PN-EN 12207); W-249). Całkowita przepuszczalność
energii promieniowania słonecznego g = f_C·g_n ≤ 0,35 dla okien E, S, W (WT zał. 2 pkt 2.1.1 (g = f_C·g_n; wyjątki pkt 2.1.4); W-247).

**Tabela 41. Zestawienie stolarki zewnętrznej — wymiary, otwieranie, osłony, montaż**

| Symbol | Rodzaj | Opis wyrobu (parametry wymagane) | Wymiary [cm] | Szt. | Kond. | Otwieranie | Osłona | Montaż |
|---|---|---|---|---|---|---|---|---|
| FX1 | przeszklenie stałe | przeszklenie stałe ALU 3-szybowe, 1,90 × 2,75 m, VSG od wewn. (strefa uderzeń) | 178 × 278 | 2 | P0 | stałe | screen ZIP | M1 |
| HS1 | drzwi podnoszono-przesuwne HS | drzwi podnoszono-przesuwne ALU 2,34 × 2,75 m, próg termiczny bezprogowy, odwodnienie liniowe | 222 × 278 | 2 | P0 | HS, prawa, do wewn | screen ZIP | M1 |
| FX2 | przeszklenie stałe | przeszklenie stałe ALU 3-szybowe, 2,92 × 2,75 m | 286 × 278 | 1 | P0 | stałe | screen ZIP | M1 |
| DZ3 | drzwi zewnętrzne | drzwi gospodarcze przeszklone ALU 0,90 × 2,75 w systemie fasady E, otwierane na zewn. | 90 × 276 | 1 | P0 | R, lewa, na zewn | screen ZIP | M1 |
| BR1 | brama garażowa | brama segmentowa ocieplona 5,00 × 2,25 m, napęd, kratki went. ≥ 0,08 m² | 500 × 225 | 1 | P0 | segmentowa, lewa, do wewn | — | — |
| DZ2 | drzwi zewnętrzne | drzwi boczne garażu 1,00 × 2,10 (garaż nieogrzewany) | 100 × 210 | 1 | P0 | R, lewa, na zewn | — | M1 |
| DZ1 | drzwi zewnętrzne | drzwi wejściowe ALU ocieplone 1,10 × 2,40 w murze (światło ościeżnicy ≥ 0,96 × 2,33), próg ≤ 2 cm | 110 × 240 | 1 | P0 | R, prawa, do wewn | — | M1 |
| FX3 | przeszklenie stałe | doświetle drzwi wejściowych 0,35 × 2,40 m, VSG mleczne; rama o podwyższonej izolacyjności (wymagane U_f ≤ 0,80, U_w ≤ 0,90 — WT zał. 2 pkt 1.2, W-244) | 35 × 240 | 1 | P0 | stałe | — | M1 |
| HS2 | drzwi podnoszono-przesuwne HS | drzwi HS ALU 2,40 × 2,75 m (taras zach.) | 240 × 278 | 1 | P0 | HS, prawa, do wewn | screen ZIP | M1 |
| OZ1 | okno | okno RU 1,80 × 1,50 m | 180 × 150 | 3 | P0, P1 | RU, lewa, do wewn | żaluzja zewn. | M1 |
| ON1 | okno | okno uchylne 0,80 × 0,60 m, szkło mleczne | 80 × 60 | 1 | P0 | U, lewa, do wewn | — | M1 |
| BC1 | okno | boks C: 3 kwatery 2,34 × 1,50 m (środkowa RU), dolna część stała VSG do 0,85 m | 229 × 150 | 3 | P1 | F, lewa, do wewn | screen ZIP | M1 |
| OE1 | okno | okno RU 1,50 × 1,50 m | 150 × 150 | 1 | P1 | RU, lewa, do wewn | żaluzja zewn. | M1 |
| ON2 | okno | okno uchylne 0,90 × 0,60 m, szkło mleczne | 90 × 60 | 2 | P1, P2 | U, lewa, do wewn | — | M1 |
| ON3 | okno | okno uchylne 1,20 × 0,60 m | 120 × 60 | 1 | P1 | U, lewa, do wewn | — | M1 |
| OP1 | okno | okno P2 3,00 × 2,00 m, parapet 0,60 — dolna część stała VSG do 0,85, skrzydła do wewn. (W-097/098) | 300 × 200 | 1 | P2 | RU, lewa, do wewn | screen ZIP | M1 |
| OP2 | okno | okno P2 1,20 × 1,75 m, skrzydło RU do wewn. | 120 × 175 | 2 | P2 | RU, lewa, do wewn | screen ZIP | M1 |
| OP3 | okno | okno P2 2,40 × 2,00 m, parapet 0,60 — dolna część stała VSG do 0,85 | 240 × 200 | 2 | P2 | RU, lewa, do wewn | screen ZIP | M1 |
| ON4 | okno | okno klatki 1,70 × 1,50 m (P2), uchylne do wewn. | 170 × 150 | 1 | P2 | U, lewa, do wewn | — | M1 |

*Źródło: model/budynek.yaml — otwory, stolarka (grupowanie po symbolu)*

**Tabela 42. Zestawienie stolarki zewnętrznej — parametry cieplne, g, szczelność**

| Symbol | U_w obl. [W/(m²·K)] | U_w wym. [W/(m²·K)] | U_max [W/(m²·K)] | g_n | f_C | g | Ocena g | Klasa szczeln. |
|---|---|---|---|---|---|---|---|---|
| FX1 | 0,64 | 0,750 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| HS1 | 0,84 | 0,850 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| FX2 | 0,61 | 0,730 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| DZ3 | 1,00 | 1,000 | 1,300 | — | — | — | — | 4 |
| BR1 | 1,50 | 1,500 | — | — | — | — | — | — |
| DZ2 | 1,30 | 1,300 | — | — | — | — | — | 4 |
| DZ1 | 0,90 | 0,900 | 1,300 | — | — | — | — | 4 |
| FX3 | 0,87 | 0,870 | 0,900 | 0,400 | — | — | orientacja N ± 45° (pkt 2.1.4) | 4 |
| HS2 | 0,82 | 0,850 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| OZ1 | 0,81 | 0,800 | 0,900 | 0,500 | 0,15 | 0,075 | spełnia | 4 |
| ON1 | 0,89 | 0,900 | 0,900 | 0,500 | — | — | orientacja N ± 45° (pkt 2.1.4) | 4 |
| BC1 | 0,78 | 0,800 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| OE1 | 0,75 | 0,800 | 0,900 | 0,500 | 0,15 | 0,075 | spełnia | 4 |
| ON2 | 0,88 | 0,900 | 0,900 | 0,500 | — | — | orientacja N ± 45° (pkt 2.1.4) | 4 |
| ON3 | 0,86 | 0,880 | 0,900 | 0,500 | — | — | orientacja N ± 45° (pkt 2.1.4) | 4 |
| OP1 | 0,71 | 0,780 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| OP2 | 0,77 | 0,820 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| OP3 | 0,74 | 0,790 | 0,900 | 0,500 | 0,14 | 0,068 | spełnia | 4 |
| ON4 | 0,82 | 0,800 | 0,900 | 0,500 | — | — | orientacja N ± 45° (pkt 2.1.4) | 4 |

U_w obl. — zakres dla otworów danego symbolu (PN-EN ISO 10077-1; drzwi — U_D z danych wyrobu). f_C — współczynnik redukcji osłony (WT zał. 2 pkt 2.1.3 lub PN-EN ISO 52022-1 metodą uproszczoną [NZW]). Deklarowane U_w, g, klasa szczelności wybranego wyrobu — do potwierdzenia deklaracją właściwości użytkowych.

*Źródło: lamela.obliczenia.fizyka.okna — u_okna, sprawdz_g*

**Tabela 43. Montaż stolarki zewnętrznej**

| Kod | Sposób montażu (osadzenia) stolarki | Detal |
|---|---|---|
| M1 | ciepły montaż: rama wsunięta 5 cm w mur, 4 cm w warstwie ocieplenia; izolacja ościeża z zakładem 3 cm na ramę; taśma paroszczelna od wewnątrz, paroprzepuszczalna od zewnątrz; parapet zewn. z okapnikiem na profilu nośnym z XPS (bez przerywania izolacji) | D-02 (PT-AR-D-02) |

**Tabela 44. Zestawienie drzwi wewnętrznych**

| Symbol | Rodzaj | Opis wyrobu (parametry wymagane) | Wymiary [cm] | Szt. | Kond. | Otwieranie |
|---|---|---|---|---|---|---|
| D1P | drzwi wewnętrzne | drzwi przesuwne naścienne 0,90 × 2,10 (salon → przedpokój gościnny), prowadnica natynkowa po stronie salonu, skrzydło 1,00 × 2,15 z zakładem, uszczelka szczotkowa | 90 × 210 | 1 | P0 | przesuwne, lewa, na zewn |
| D1 | drzwi wewnętrzne | drzwi wewnętrzne pełne 0,90 × 2,10 w murze (światło ościeżnicy ≥ 0,80 × 2,00), bez progu | 90 × 210 | 8 | P0, P1, P2 | R, lewa, do wewn |
| D2 | drzwi wewnętrzne | drzwi łazienkowe/WC 0,90 × 2,10, otwierane na zewnątrz, z tuleją/podcięciem ≥ 0,022 m² | 90 × 210 | 5 | P0, P1, P2 | R, prawa, na zewn |
| D3 | drzwi wewnętrzne | drzwi spiżarni 0,80 × 2,00 z kratką | 80 × 200 | 1 | P0 | R, lewa, do wewn |
| DS1 | drzwi wewnętrzne | drzwi szklane VSG 0,90 × 2,10 w ściance wiatrołapu, oznakowane (W-067) | 90 × 210 | 1 | P0 | R, lewa, na zewn |
| DG1 | drzwi wewnętrzne | drzwi garaż–dom stalowe ocieplone, szczelne, z samozamykaczem 0,90 × 2,10 | 90 × 210 | 2 | P0 | R, lewa, do wewn |
| D4 | drzwi wewnętrzne | drzwi pom. technicznego 0,90 × 2,10 z kratką, akustyczne R_w ≥ 32 dB | 90 × 210 | 1 | P0 | R, lewa, do wewn |
| D4A | drzwi wewnętrzne | drzwi pom. technicznego z centralą (P2) 0,90 × 2,10, akustyczne R_w ≥ 32 dB, BEZ kratki, uszczelka obwodowa i próg z uszczelką opadającą (A3 I-8; W-230) | 90 × 210 | 1 | P2 | R, lewa, na zewn |

## Zestawienie wykończeń wnętrz — W-317

Wykończenia pomieszczeń wg modelu (kody materiałów — legenda w tabeli następnej; układ warstw podłóg i stropów —
rozdział „Rozwiązania konstrukcyjno-materiałowe przegród”). Numeracja pomieszczeń jak na rzutach (parter = 1.xx).

**Tabela 45. Wykończenia pomieszczeń**

| Nr | Pomieszczenie | Posadzka | Podłoga / strop | Ściany | Sufit | θ_i [°C] |
|---|---|---|---|---|---|---|
| 1.01 | Wiatrołap | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 16 |
| 1.02 | Hol | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.03 | WC gościnne | GRES | POD-0L | PLYTKI_SC | SUF_GK | 20 |
| 1.04 | Klatka schodowa | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.05 | Spiżarnia | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 16 |
| 1.15 | Schowek pod schodami (h 1,40–2,20) | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 16 |
| 1.16 | Schowek pod spocznikiem (h < 1,40) | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 16 |
| 1.06 | Salon + jadalnia + kuchnia | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.07 | Pas komunikacyjny przy schodach | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.08 | Przedpokój gościnny | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.09 | Łazienka gościnna (natrysk) | GRES | POD-0L | PLYTKI_SC | SUF_GK | 24 |
| 1.10 | Pokój gościnny / gabinet | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.11 | Przedsionek gospodarczy | GRES | POD-0L | TYNK_GIPS | TYNK_GIPS | 20 |
| 1.12 | Pomieszczenie techniczne | GRES | POD-0L | TYNK_CW | TYNK_GIPS | 16 |
| 1.13 | Garaż 2-stanowiskowy | ZYWICA | POD-G | TYNK_CW | TYNK_CW | — |
| 2.01 | Hol | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 2.02 | Pokój rodzinny / biblioteka (boks C) | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 2.03 | Pokój dziecka 1 | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 2.04 | Pokój dziecka 2 | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 2.05 | Łazienka dzieci (wanna) | GRES | POD-1L | PLYTKI_SC | SUF_GK | 24 |
| 2.06 | Klatka schodowa | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 2.07 | WC z natryskiem | GRES | POD-1L | PLYTKI_SC | SUF_GK | 24 |
| 2.08 | Pralnia z suszarnią | GRES | POD-1L | PLYTKI_SC | TYNK_GIPS | 20 |
| 3.01 | Hol | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 3.02 | Sypialnia rodziców | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 3.03 | Garderoba (przedpokój apartamentu) | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 3.04 | Łazienka rodziców | GRES | POD-1L | PLYTKI_SC | SUF_GK | 24 |
| 3.05 | Gabinet / pokój gościnny okazjonalny | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 3.06 | Klatka schodowa (wyjście z biegu 2, pustka) | DESKA_DEB | — | TYNK_GIPS | TYNK_GIPS | 20 |
| 3.07 | Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | GRES | POD-1L | TYNK_GIPS | TYNK_GIPS | 16 |
| 1.14 | Szacht instalacyjny SI | — | — | — | — | 20 |
| 2.09 | Szacht instalacyjny SI | — | — | — | — | 20 |
| 3.08 | Szacht instalacyjny SI | — | — | — | — | 20 |

*Źródło: model/budynek.yaml — pomieszczenia*

**Tabela 46. Legenda wykończeń**

| Kod | Wyrób / wykończenie (parametry wymagane) |
|---|---|
| GRES | Płytki gresowe 60×120 na kleju C2TE S1 |
| TYNK_GIPS | Tynk gipsowy maszynowy 1,5 cm |
| PLYTKI_SC | Płytki ścienne ceramiczne (łazienki, WC, pralnia — do 2,0 m / do sufitu w natryskach) |
| SUF_GK | Sufit podwieszany GK (strefy kanałów wentylacji) |
| DESKA_DEB | Deska warstwowa dębowa 15 mm, klejona |
| TYNK_CW | Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne) |
| ZYWICA | Posadzka żywiczna epoksydowa antypoślizgowa R11 (garaż) |

**Tabela 47. Lamele, balustrady, tarasy i podesty**

| Element | Rodzaj | Opis |
|---|---|---|
| LAM-S | lamele, elewacja S | Lamele elewacyjne 40×80 mm, drewno termojesion (klasa 1 trwałości), olejowane; rozstaw 0,12 m, rzędne 6,15…8,98 m; bryła A — pionowe lamele na 2 ryglach, konsole z przekładką (χ); stała osłona okien P2 |
| LAM-W | lamele, elewacja W | Lamele elewacyjne 40×80 mm, drewno termojesion (klasa 1 trwałości), olejowane; rozstaw 0,12 m, rzędne 6,15…8,98 m; czoło wspornika bryły A |
| LAM-E | lamele, elewacja E | Lamele elewacyjne 40×80 mm, drewno termojesion (klasa 1 trwałości), olejowane; rozstaw 0,12 m, rzędne 6,15…8,98 m; czoło wsch. bryły A |
| LAM-P0 | lamele, elewacja S | Lamele dębowe 30×60 mm (ekran komunikacji P0, h 2,10 m); rozstaw 0,10 m, rzędne 0,00…2,10 m; ekran wewnętrzny P0 wydzielający pas komunikacyjny przy schodach (przeszczep J1 z W3) |
| BL1 | balustrada / pochwyt h = 0,90 m | pochwyt stal nierdzewna Ø42 na wspornikach, ciągły wokół ścianki środkowej (W-095/W-096); od strony ścian C/D — ściany pełne, brak krawędzi otwartej |
| BL2 | balustrada / pochwyt h = 0,90 m | pochwyt stal nierdzewna Ø42 na wspornikach, ciągły wokół ścianki środkowej (W-095/W-096); od strony ścian C/D — ściany pełne, brak krawędzi otwartej |
| T1 | taras / podest, rzędna −0,02 m | deska kompozytowa na legarach i wspornikach regulowanych, szczeliny 5 mm; odwodnienie liniowe przy progach HS; taras ogrodowy w kształcie L (pd. przed E pod okapem 1,00 m, zach. pod okapem 1,50 m) — 4,30 m od granicy zach. |
| T2 | taras / podest, rzędna −0,02 m | płyty betonowe 60×60 na podsypce, spadek 2 % od drzwi; podest wejścia głównego pod daszkiem (x 9,80–11,70: DZ1 + FX3 + 0,25 m), bez stopni, odwodnienie liniowe OL-3 przy krawędzi pn.; poza podestem teren −0,32 (cokół ≥ 0,30 — runda 2, K-1) |
| T3 | taras / podest, rzędna −0,02 m | płyty betonowe 60×60, spadek 2 % od drzwi; podest drzwi gospodarczych pod okapem E; odwodnienie liniowe OL-6 przy progu (→ RS8/KD-E), 2 stopnie do ogrodu (teren −0,34) |

*Źródło: model/budynek.yaml — lamele, balustrady, tarasy*

## Zasada „4 linii” — ciągłość warstw obudowy — § 24 pkt 2 RPB; W-248, W-249

Obudowę części ogrzewanej projektuje się tak, aby cztery warstwy funkcjonalne były ciągłe w każdym węźle
i były możliwe do narysowania jedną linią bez odrywania ołówka na każdym detalu:

1. **I — izolacja cieplna:** Styropian grafitowy EPS 031 (ETICS, NRO w systemie) (SZ1, AT1); Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1) (SZ2, SZL); Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż) (SZL, SWG, SUF-ZEW); Płyty PIR z okładziną (izolacja spadkowa stropodachów) (AT1, SD1, SD2, DZ1); Styropian podłogowy EPS 100-038 (pod jastrychem) (POD-0, POD-0L); Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa) (POD-0, POD-0L, POD-G, POD-G); w węzłach — łączniki termoizolacyjne płyt wysuniętych i bloki
   termoizolacyjne u podstawy attyk (parametry wg PT-2 BO, W-272);
2. **H — ochrona przed wodą (hydroizolacja, izolacja przeciwwilgociowa, wiatroizolacja):** Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m) (SZ2, SZL, SUF-ZEW); Płyta drewnopochodna wiatroizolacyjna DWD/MDF.RWH 16 mm (SZL); Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej (POD-0, POD-0L, POD-G); Hydroizolacja podpłytkowa (masa uszczelniająca + taśmy), strefy mokre (POD-0L); Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów) (SD1, SD2); Hydroizolacja 2 × papa SBS (podkładowa + wierzchniego krycia, dach zielony) (DZ1);
3. **S — szczelność powietrzna:** Tynk gipsowy maszynowy 1,5 cm (SZ1, SZ2); Płyta OSB/3 15 mm (usztywnienie i warstwa szczelności ściany A') (SZL); połączenia ze stolarką i przejścia instalacji — taśmy
   i mankiety systemowe; próba szczelności budynku PN-EN ISO 9972 (W-249);
4. **P — kontrola pary wodnej:** Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów) (SD1, SD2, DZ1); opór dyfuzyjny warstw maleje ku stronie zimnej (sprawdzenie — „Kondensacja międzywarstwowa”).

Ocenę ciągłości w węzłach (karty mostków, PN-EN ISO 10211) i odesłania do detali zawiera tabela poniżej.

**Tabela 48. Ciągłość „4 linii” w węzłach obudowy**

| Węzeł | Opis | I | H | S | P | Ciągłość / uwaga | Detal |
|---|---|---|---|---|---|---|---|
| WZ-01 | Attyka stropodachu bryły A (D1) | ✓ | ✓ | ✓ | ✓ | zachowana | D-04 (PT-AR-D-03) |
| WZ-02 | Attyki dachów P1 (D2, D3) — poza ścianami bryły A | ✓ | ✓ | ✓ | ✓ | zachowana | D-05 (PT-AR-D-03) |
| WZ-03 | Attyka dachu zielonego nad pasem gospodarczym (linia D, częś… | ✓ | ✓ | ✓ | ✓ | zachowana | — |
| WZ-04 | Okap E (PL-E) i daszek wejścia — łącznik termoizolacyjny | ✓ | ! | ✓ | ✓ | uwaga — hydroizolacja / ochrona przed wodą: odprowadzenie wody z krawędzi płyty (rynna / okapnik / rzygacz → rura spustowa) — nieokreślone w modelu; o… | D-09 (PT-AR-D-02) |
| WZ-05 | Krawędź ST2 (PL-2) — łącznik termoizolacyjny pod bryłą A | ✓ | ! | ✓ | ✓ | uwaga — hydroizolacja / ochrona przed wodą: odprowadzenie wody z krawędzi płyty (rynna / okapnik / rzygacz → rura spustowa) — nieokreślone w modelu; o… | D-08 (PT-AR-D-04) |
| WZ-06 | Krawędź ST3 (PL-3) — łącznik termoizolacyjny przy attyce bry… | ✓ | ✓ | ✓ | ✓ | zachowana | — |
| WZ-07a | Krawędź stropu ST2Z nad powietrzem: ściana SZL na belce B3 +… | ✓ | ✓ | ✓ | ✓ | zachowana | D-08 (PT-AR-D-04) |
| WZ-07b | Krawędź stropu ST2Z nad ścianą SZ1 niższej kondygnacji (ocie… | ✓ | ✓ | ✓ | ✓ | zachowana | D-08 (PT-AR-D-04) |
| WZ-08 | Cokół: ściana zewn. – płyta fundamentowa na XPS (część ogrze… | ✓ | ✓ | ✓ | ✓ | zachowana | D-01 (PT-AR-D-01) |
| WZ-09a | Ściana dom–garaż (SWG) na płycie fundamentowej (POD-0 / POD-… | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: TYNK_GIPS → BET_KOM_600 → ZB_C25 → TYNK_CW (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) | D-10 (PT-AR-D-05), D-11 (PT-AR-D-05) |
| WZ-09b | Ściana SWG pod płytą: dom — D4, garaż — D4, pas docieplenia … | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: TYNK_GIPS → SIL18 → ZB_C25 (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) | D-10 (PT-AR-D-05) |
| WZ-09c | Ściana SWG pod płytą: dom — ST1 + ściana SZ1, garaż — D4, pa… | ! | ✓ | ✓ | ✓ | uwaga — izolacja cieplna: przerwana: TYNK_GIPS → SIL18 → ZB_C25 (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny) | D-10 (PT-AR-D-05) |
| WZ-10 | Strop pośredni ST1/ST2 – ściana zewn. z ETICS ciągłym (wieni… | ✓ | ✓ | ✓ | ✓ | zachowana | — |
| WZ-11 | Ościeża okien/drzwi — ciepły montaż (rama 5 cm w murze, 4 cm… | ✓ | ✓ | ✓ | ✓ | zachowana | D-02 (PT-AR-D-02) |
| WZ-11N | Nadproża — BEZ kaset osłon w ociepleniu (kasety w okapach / … | ✓ | ✓ | ✓ | ✓ | zachowana | D-02 (PT-AR-D-02) |
| WZ-11P | Podokienniki — parapet zewn. z okapnikiem na profilu z XPS | ✓ | ✓ | ✓ | ✓ | zachowana | D-02 (PT-AR-D-02) |
| WZ-11T | Progi HS / drzwi zewn. na płycie P0 — profil progowy termoiz… | ✓ | ✓ | ✓ | ✓ | zachowana | D-03 (PT-AR-D-01), D-02 (PT-AR-D-02) |
| WZ-12 | Narożniki wypukłe ścian zewnętrznych | ✓ | ✓ | ✓ | ✓ | zachowana | — |
| WZ-16a | Krawędź stropu ST2Z nad powietrzem: ściana SZ2 na belce B4 +… | ✓ | ✓ | ✓ | ✓ | zachowana | D-08 (PT-AR-D-04) |
| WZ-16b | Krawędź stropu ST2Z nad powietrzem: ściana SZ1 na belce B5 | ✓ | ✓ | ✓ | ✓ | zachowana | D-08 (PT-AR-D-04) |
| WZ-X1 | Dach D2/D3 (SD2) – ściana SZ1 wyższej kondygnacji na krawędz… | ✓ | ✓ | ✓ | ✓ | zachowana | — |
| WZ-X2 | Dach D4 (DZ1) – ściana SZ1 wyższej kondygnacji na krawędzi (… | ✓ | ✓ | ✓ | ✓ | zachowana | — |

✓ — ciągłość zachowana; ! — uwaga wykonawcza (opis w kolumnie „Ciągłość / uwaga” i na karcie węzła); ✗ — brak ciągłości.

*Źródło: projekt/08_obliczenia/mostki/zestawienie_mostkow.json — linie4*

## Odwodnienie dachów, tarasów i przyziemia — PN-EN 12056-3; W-142

Każde pole dachu ma izolację spadkową (spadek ≥ 2,0 % — R3 H-04 (dobra praktyka); W-142),
co najmniej jeden wpust z grzałką i przelew awaryjny w attyce. Obróbki attyk, wpustów i przelewów — detale
D-04 (PT-AR-D-03), D-05 (PT-AR-D-03), D-06 (PT-AR-D-03); rury spustowe przy cokole — D-07 (PT-AR-D-01), D-05 (PT-AR-D-03), D-06 (PT-AR-D-03); progi z odwodnieniem
liniowym — D-03 (PT-AR-D-01), D-14 (PT-AR-D-05). Wymiarowanie hydrauliczne i odbiorniki wód opadowych — PT-3 IS.

**Tabela 49. Odwodnienie dachów**

| Dach | Przegroda | Spadek [%] | Wpusty | Rury spustowe | Attyka nad pokryciem [m] |
|---|---|---|---|---|---|
| D1 | SD1 | 2,000 | WP1 DN100 z grzałką; WP2 DN100 z grzałką | RS1 DN100 (wewn.) → zbiornik; RS2 DN100 (wewn.) → zbiornik | 0,350 |
| D2 | SD2 | 2,000 | wpust przy attyce (boczny) WP3 DN100 z grzałką | RS3 DN100 (zewn.) → zbiornik | 0,250 |
| D3 | SD2 | 2,000 | wpust przy attyce (boczny) WP4 DN100 z grzałką | RS4 DN100 (zewn.) → zbiornik | 0,250 |
| D4 | DZ1 | 2,000 | WP5 DN100 z grzałką; WP6 DN100 z grzałką | RS5 DN100 (zewn.) → zbiornik; RS6 DN100 (wewn.) → zbiornik | 0,545 |

*Źródło: model/budynek.yaml — dachy*

**Tabela 50. Przelewy awaryjne w attykach — rzędne**

| Przelew | Dach | Wymiary [cm] | Rzędna dna [m] | Rzędna pokrycia [m] | Δh [mm] | Opis |
|---|---|---|---|---|---|---|
| przelew PA1 | D1 | 20 × 10 | 9,460 | 9,441 | 19,000 | przelew PA1 — attyka pn. nadbudowy (na teren, rzygacz z okapnikiem) |
| przelew PA2 | D1 | 20 × 10 | 9,470 | 9,462 | 8,000 | przelew PA2 — attyka zach. nadbudowy (na dach D2, pole z własnym wpustem WP3) |
| przelew PA4 | D2 | 20 × 10 | 6,330 | 6,308 | 22,000 | przelew PA4 — attyka zach., 0,60 m od WP3 (R-W2) |
| przelew PA5 | D3 | 20 × 10 | 6,330 | 6,303 | 27,000 | przelew PA5 — attyka pn., 0,35 m od WP4; rzygacz z okapnikiem, wylot 0,40 m na zach. od daszka PL-DA (R-W2) |
| przelew PA6 | D4 | 20 × 10 | 3,170 | 3,146 | 24,000 | przelew PA6 — attyka wsch. (garaż), 0,57 m od WP5 (R-W2) |
| przelew PA7 | D4 | 20 × 10 | 3,170 | 3,149 | 21,000 | przelew PA7 — attyka wsch. (pas gosp.), 0,75 m od WP6; 2,6 m od jedn. PC (> 1 m — W-156) |

Δh — wzniesienie dna przelewu ponad lokalną rzędną pokrycia (wierzch hydroizolacji); przelew działa po zablokowaniu wpustu, poniżej korony attyki. Rzędne względne: ±0,000 = posadzka parteru = 101,65 m n.p.m. [DANE PRZYKŁADOWE – FIKCYJNE].

*Źródło: model/budynek.yaml — dachy.przelewy_awaryjne*

Przyziemie: nawierzchnie przy budynku ze spadkiem od ścian, odwodnienia liniowe przy progach drzwi HS, drzwi zewnętrznych i bramy (tarasy i podesty — tabela „Lamele, balustrady, tarasy i podesty”); hydroizolację płyty fundamentowej wywija się na cokół (detal D-01 (PT-AR-D-01), D-13 (PT-AR-D-06), D-13a (PT-AR-D-06)).

## Dane dotyczące warunków ochrony przeciwpożarowej — § 23 pkt 10 RPB

Dane w zakresie architektury (§ 23 pkt 10 RPB — stosownie do zakresu projektu; dane ogólne budynku — PAB,
§ 20 ust. 1 pkt 13):

* kategoria zagrożenia ludzi **ZL IV** (WT §209 ust. 2 pkt 4; W-210); grupa wysokości **N** (WT §8 pkt 1; W-210), wysokość wg WT § 6 —
  9,97 m;
* 3 kondygnacje nadziemne ≤ 3 — wymagań klasy odporności pożarowej budynku nie stawia się (WT §213 pkt 1 lit. a; W-211);
  budynek stanowi jedną strefę pożarową razem z garażem (W-212);
* ściany zewnętrzne i dach — nierozprzestrzeniające ognia (W-213): ETICS jako system z klasyfikacją NRO
  (Styropian grafitowy EPS 031 (ETICS, NRO w systemie)); pokrycia dachów z klasyfikacją B_ROOF(t1) [ZAŁ];
* okładziny elewacyjne i lamele mocowane mechanicznie do konstrukcji (W-216);
* obudowy szachtów instalacyjnych: GK10 — Obudowa szachtu SI: 2 × GKF 12,5 + profil CW 50 z wełną + 2 × GKF 12,5 (EI 30);
* przejścia instalacji przez przegrody zewnętrzne poniżej terenu — gazoszczelne (W-214), uszczelnienia
  systemowe wg PT-3 IS i PT-4 IE;
* klasy odporności ogniowej podaje się na rysunkach wyłącznie dla elementów, dla których są wymagane (W-219).

## Wykaz rysunków — część rysunkowa — § 24 RPB

Część rysunkowa (§ 24 pkt 1–2 RPB) obejmuje rzuty wszystkich kondygnacji z rzutem dachu, przekroje i elewacje
w skali 1:50 (arkusze AR z katalogu `projekt/01_koncepcja/widoki` — rysunki PAB dołączone jako podstawa rozwiązań PT; zmiany
względem PAB — brak) oraz detale cieplne i szczelności PT-AR-D w skalach 1:5 i 1:10. Wykaz rysunków z numerami,
skalami i formatami — karta części rysunkowej (generowana z tabliczek arkuszy).

**Tabela 51. Wykaz rysunków tomu PT-1 AR**

|  |
|
