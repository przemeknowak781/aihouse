# REKOMENDACJE ZMIAN MODELU — konstrukcja (PT-BO)

Dokument zespołu rysunków konstrukcyjnych (generator `lamela.views.konstrukcja`). Model (`model/*.yaml`) **nie był
edytowany** — poniżej zmiany do wprowadzenia przez właściciela modelu (`tools/buduj_model.py`), z uzasadnieniem
z obliczeń (`lamela.obliczenia.konstrukcja`, raport `projekt/04_PT_konstrukcja/obliczenia/obliczenia_statyczne.md`)
i kontroli zbrojenia rysunków (`projekt/04_PT_konstrukcja/rysunki/kontrola_zbrojenia.md`). Rysunki PT-BO są
generowane z modelu — po zmianach zaktualizują się automatycznie (pozycje, zbrojenie, zestawienia stali).

Oznaczenia: **[ZAŁ]** — przyjęcie projektanta (jawne, do akceptacji), **[MODEL]** — zmiana danych modelu,
**[BIBL]** — zmiana wprowadzona w bibliotece obliczeń w tej rundzie (opis w p. 9).

## 0. Stan (model z 2026-09-25, po rundzie zmian biblioteki opisanej w p. 9)

| Zakres | Wynik | Uwagi |
|---|---|---|
| Kontrola zbrojenia rysunków A_s,prov ≥ max(A_s,req; A_s,min), s ≤ s_max, A_s ≤ A_s,max | **275 / 277** | 2 niespełnione — ta sama strefa płyty fundamentowej przy węźle C/3 (p. 5.2): zbrojenie niewykonalne w h = 0,25 m → stopa pod węzłem |
| Pozycje obliczeń biblioteki (132) | 105 spełnionych, 27 z uwagami | 14 — ławy/stopy izolowane ZF/SF zastąpione MES płyty z żebrami (Z6); 12 — mur (p. 1–3); 1 — PL-2 SGU (p. 6) |
| MES płyty fundamentowej | docisk lokalny η = 114 % | p. 5.3 |

Wszystkie pozostałe niespełnienia wymagają **zmiany modelu** (nie da się ich usunąć zbrojeniem rysunku) — lista
zmian poniżej, w kolejności wpływu na konstrukcję: p. 1 (wsporniki bryły A) → p. 3 (węzły belek w osi 3) → p. 2
(fasada nad B1) → p. 5 (stopy pod słupami) → p. 6 (naroże PL-2).

## 1. System wspornikowy bryły A (belki B3, B4, B5; płyty ST2Z, PL-2) — [MODEL] + [ZAŁ]

**Stan modelu.** Belki B3/B4/B5 nie mają zdefiniowanych podpór (B4/B5 — wspornik 1,00 m poza oś A, przęsło zakotwienia
A–B nad murem współliniowym S1-01/S1-05; B3 — belka krawędziowa oparta na końcach B4/B5). Biblioteka pomijała ich
wymiarowanie („brak dwóch podpór”), a obciążenie ściany P2 w osi A'' (S2-08), okapu PL-2 i dachu D1 (przez B6)
„znikało” ze ścieżki obciążeń.

**Przyjęcie [ZAŁ] (wprowadzone w bibliotece, p. 9):** B4/B5 — belka ze wspornikiem: podpora na narożu ścian A/1
(A/3) i na końcu odcinka muru współliniowego (x = 3,875), B3 — belka swobodnie podparta na końcach B4/B5, reakcje B3
przyłożone do B4/B5 jako siły skupione. Wyniki (obwiednia STR):

| Belka | przekrój | M_Ed | V_Ed | reakcje char. (G / Q) | zbrojenie (bibl.) |
|---|---|---|---|---|---|
| B3 | 20×60 | +193 kNm | 423 kN | na B4: 228 / 103 kN; na B5: 80 / 28 kN | dołem 8φ12, strz. φ8 co 10 |
| B4 | 18×80 | −425 kNm (naroże A/1) | 427 kN | naroże A/1: ≈ 298 kN G; koniec x = 3,875: **−52 kN G (odrywanie)** | górą 3φ25 (2 warstwy: 2 + 1) |
| B5 | 18×80 | −171 kNm | 371 kN | S1-05 łącznie 422 / 88 kN | górą 5φ12 |

**Rekomendacje:**
1. [MODEL] Dopisać w `belki` jawny schemat podparcia B3–B5 (np. pole `podpory: [{typ: sciana, id: S1-04, s: 1.0}, …]`
   albo `schemat: wspornik`) — usuwa zależność od reguły [ZAŁ].
2. [MODEL] **Słupy żelbetowe w narożach A/1 (0; 0) i A/3 (0; 5,125)**, P0–P1 (od płyty fundamentowej do +5,93),
   np. 18×40 cm w licu muru (C30/37, 4φ16, strz. φ8 co 15) — przejmują reakcje „podparcia” wsporników B4/B5
   (ok. 400 kN G+Q na naroże) zamiast filarków muru (S1-04 η 155 %, S1-01 η 136 %, S0-01 η 541 %, S0-07 η 132 %).
3. [MODEL] Zakotwienie końca przęsła zakotwienia B4/B5 (x = 3,875) w wieńcu i ścianie S2-01/S2-07 (obliczeniowo
   odrywanie −52 kN G; sprawdzenie EQU z γ_G,inf = 0,9 — ciężar ściany P2 nad belką nie jest w modelu przyłożony do
   belki, tylko do muru poniżej).
4. [ZAŁ → do sprawdzenia] Ugięcie końca wspornika B4/B5 z przekrojem zarysowanym i pełzaniem przy ścianie P2
   (okno O2-04, tynk) — limit L/500 (PN-EN 1992-1-1 7.4.1(5)).

## 2. Ścieżka obciążeń fasady S1-01 nad podciągiem B1 — [MODEL]/[BIBL]

Ściana S1-01 (fasada pd. P1) stoi nad przeszkleniem parteru; w zamyśle niesie ją podciąg odwrócony B1 18×107 na
słupach SL1–SL4. W bibliotece obciążenie ściany jest przekazywane **ściana-na-ścianę** na S0-01, a tam na filarki
12 cm przy słupach (S0-01: η = 541 %, reakcje B1 na słupy tylko 30–51 kN G) — ścieżka niezgodna z koncepcją.
Rekomendacja: w modelu oznaczyć oparcie S1-01 na B1 (np. `sciany[].oparta_na: B1` lub brak ściany S0-01 w strefie
przeszkleń — kwatery jako otwory nienośne) i w bibliotece przekazać obciążenie ściany stojącej na belce do belki.
Do tego czasu wyniki S0-01, słupów SL1–SL4 i żebra ZF1 są niemiarodajne (zawyżone lokalnie / zaniżone na słupach).

## 3. Filarki muru pod oparciami belek — [MODEL]

Niespełnione pozycje muru (biblioteka, PN-EN 1996-1-1): S1-06 (η 382 %, filarek 0,21 m w osi D/3 pod oparciem B9),
S1-08 (docisk 219 %, oparcie B9: 276 kN G), S1-09 (docisk 174 %), S0-10 (η 367 %, filarek 0,40 m w D/3 pod B8/B9/B10),
S0-08 (η 214 %), S0-09 (η 107 %), S1-05 (η 230 %, reakcja B5), S2-09 (η 172 %). Belki B8 (P0), B9 (P1) i B10 (P2)
w osi 3 (C–D) opierają się w tych samych węzłach C/3 (5,875; 5,125) i D/3 (8,5; 5,125) — reakcje sumują się
w pionie (B9: V_Ed = 431 kN).

Rekomendacje: [MODEL] **słupy żelbetowe w węzłach C/3 i D/3 (P0–P2)**, np. 18×25 cm w licu muru, z poduszkami pod
oparcia belek; pod słupami — pogrubienie płyty fundamentowej (stopa 1,2 × 1,2 × 0,60 m) — usuwa też strefę S1 płyty
(p. 5); alternatywnie powiększenie filarków (przesunięcie otworów O1-11, O0-18 o ≥ 0,30 m). Podwyższenie klasy
silikatu (20 → 25) nie wystarcza (η > 200 %).

## 4. Elementy niekonstrukcyjne w `wsporniki_plyty` — [MODEL]

PS-A, OB-A, OB-A2 (podsufitka/obudowa, PODSUF), IZ-ST2Z (wełna), SW1 (szkło), WYL1, PL-C1, PL-C2, PL-D (ramy stalowe
RAMA_C) są w modelu płytami wspornikowymi. Biblioteka liczyła je jak płyty żelbetowe (np. OB-A — 0,488 m „żelbetu”
na obrzeżu PL-2 usztywniało naroże wspornika i zawyżało momenty ST2Z do 966 kNm/m). Obecnie [BIBL] są pomijane
w analizie płyt (kryterium: materiał). Rekomendacja: przenieść je do osobnej sekcji modelu (okładziny/ramy) albo
dodać pole `konstrukcyjny: false`; ramy PL-C1/PL-C2/PL-D (stal) wymagają osobnych pozycji (konsole, przekładki).

## 5. Płyta fundamentowa — [MODEL]

1. Żebra ZF1–ZF7 wystają poza obrys PF1 (1,3–2,4 m² w rzucie) — ujednolicić obrys płyty i osie żeber (A2).
2. Węzły obciążeń skupionych (p. 1 i 3) dają w MES płyty lokalne momenty poza żebrami: strefa S1 przy węźle C/3
   (h = 0,25 m, M_Ed,y ≈ 308 kNm/m, A_s,req ≈ 5250 mm²/m — przekrój podwójnie zbrojony, zbrojenie niewykonalne przy
   rozstawie w świetle wg 8.2(2)). Rekomendacja: pogrubienie płyty (stopa) pod słupami z p. 1 i 3, np. 1,2 × 1,2 m,
   h = 0,60 m, analogicznie do SF1–SF4.
3. Docisk lokalny do podłoża w MES: p_d,max = 364 kPa > q_Rd,lok = 319 kPa (η = 114 %, pasmo żebro + 2h) oraz
   osiadanie w_k,max = 44 mm (≤ 50 mm, ale ≈ 2× więcej niż przed uwzględnieniem wsporników B4/B5) — skutek sił
   skupionych w węzłach A/1, A/3, C/3, D/3. Stopy pod słupami z p. 1 i 3 rozłożą nacisk; do sprawdzenia po zmianie
   modelu (raport `obliczenia/plyta_fundamentowa_MES.md`).
4. Kategoria obciążenia posadzki garażu (F) — przypisać w modelu (obecnie kat. A w MES płyty).

## 6. Naroże wspornika PL-2 (A/1) — [MODEL] + [ZAŁ]

Po wyłączeniu OB-A (p. 4) naroże PL-2 (x < −1,3; y < −0,3) jest wspornikiem dwukierunkowym zawieszonym na końcach
B3/B4 — MES daje osobliwość momentów w narożu linii podparcia. [ZAŁ] momenty płyt wspornikowych uśredniono
poprzecznie na 1,0 m (długość modułu łącznika); rysunek: pręty górne dobrane do A_s,req (φ do 25 mm), pręty ukośne
naroża i łączniki narożne. Wymaganie naroża (≈ 3760 mm²/m) decyduje obecnie o prętach górnych całego pola PL-2
(Ø25 co 13 na całej długości pasa pd. — rozwiązanie bezpieczne, nieekonomiczne). Pozycja 3.2 nadal wykazuje
przekroczenie SGU (ugięcie L/250 η = 286 %, rysy) — **wymagana zmiana modelu**. Rekomendacje (jedna z): pogrubienie PL-2 w strefie naroża do 0,35 m; belka krawędziowa w podsufitce łącząca końce B3/B4 z narożem
(wspornik ukośny); podparcie naroża (słupek/cięgno). Po zmianie — dobór łączników narożnych producenta (ETA)
i sprawdzenie ugięcia z podatnością łącznika.

## 7. Nadproża — reprezentacja w modelu — [MODEL]

Belki modelu N1–N28 („nadproże otworu O…”) są jednocześnie pozycjami belek (gdy płyta się na nich opiera: N16, N17,
N22–N25, N27) i nadproży N-O… (biblioteka). Rysunki biorą belkę, gdy istnieje jej pozycja, w pozostałych przypadkach
typ nadproża. Rekomendacja: jedna reprezentacja (np. `nadproza:` z polem `otwor:`) — usuwa podwójne pozycje.

## 8. Słupy SL1–SL4 pod B1 — [MODEL]

Biblioteka zgłasza „przebicie” płyty ST1/PL-E nad słupami — słupy podpierają belkę B1 (b = 18 cm), więc sprawdzenie
przebicia płyty nie dotyczy; wymagane: głowica słupa (blacha 180 × 180 × 15, kotwy) i docisk belki (PN-EN 1992-1-1
6.7) — dopisać do modelu wymiary blachy czołowej.

## 9. Zmiany w bibliotece obliczeń wprowadzone w tej rundzie — [BIBL]

`src/lamela/obliczenia/konstrukcja/pozycje.py`:
- `_plyta_konstrukcyjna` — płyty z materiałów niekonstrukcyjnych (podsufitki, izolacje, szkło, ramy stalowe)
  pomijane w analizie płyt (kryterium: `mat` elementu, także w `raw` wspornika) — p. 4.
- `_podpory_belki_rozszerzone`, `_na_belce` — podpory belek bez dwóch podpór na końcach: mur współliniowy (podpory na
  końcach odcinka wspólnego poza otworami), ściany poprzeczne w przęśle, oparcie na innej belce (reakcja jako
  `ObcP` na belce podpierającej, belki oparte liczone najpierw, bez podparcia wzajemnego) — p. 1.
- reakcje belki na mur współliniowy rozkładane na długości ≈ h belki (≤ 1,0 m), podparcie ciągłe — sumy reakcji
  w `dane["reakcje"]`.
- `_nadproza` — pozycja nadproża pomijana tylko, gdy otwór przykrywa belka z własną pozycją obliczeniową (np. B1, B2),
  nie gdy belką jest nadproże modelu tego otworu (N…); kandydaci wysokości: nadproże zespolone z płytą i belka
  odwrócona w ścianie kondygnacji wyższej.
- `_m_usrednione`, `B_USR = 1,0 m` — momenty płyt wspornikowych uśredniane poprzecznie (osobliwości MES w narożach
  linii podparcia/łączników), także momenty quasi-stałe do rys — p. 6.
- (wcześniej) `OKNO_SCINANIA = 1,0 m` — reakcje liniowe do ścinania płyt uśredniane na 1,0 m (osobliwości na końcach
  podpór), zbrojenie na ścinanie płyt h ≥ 0,20 m (9.3.2); belki odwrócone jako podpory płyt; łączniki termoizolacyjne
  w strefie izolacji (szczelina ≤ 0,36 m) jako pas ciągły MES.

`src/lamela/obliczenia/konstrukcja/plyta_fundamentowa.py` (moduł MES płyty na podłożu Winklera): przekroje
μ > μ_lim wymiarowane jako podwójnie zbrojone (A_s2 = ΔM/(σ_s2·(d − a₂)), σ_s2 ≤ f_yd z ε_cu3; A_s2 dodane do
wymagania warstwy przeciwnej), zamiast oznaczenia „przekrój niewystarczający”.

## 10. Przyjęcia projektanta [ZAŁ] użyte w rysunkach PT-BO

| Nr | Przyjęcie | Uzasadnienie / źródło |
|---|---|---|
| Z1 | Reakcje liniowe do ścinania płyt — średnia na 1,0 m | osobliwości MES na końcach podpór sztywnych (norma nie podaje reguły wprost — przyjęcie projektanta); por. literatura MES konstrukcji betonowych (G. Rombach, *Finite-element design of concrete structures*, ICE Publishing) |
| Z2 | Momenty płyt wspornikowych — średnia poprzeczna na 1,0 m | jw.; łączniki termoizolacyjne dobierane na m_Ed na metr bieżący (moduł 1,0 m); naroża — łączniki narożne i pręty ukośne |
| Z3 | Belki B4/B5 — schemat belki ze wspornikiem, B3 oparta na końcach B4/B5 | p. 1; do zastąpienia jawnym schematem w modelu |
| Z4 | Płyta fundamentowa: k_s z M₀ (Bowles (5-16a), PN-EN 1997-1 zał. F.2), obwiednia k_s × 0,5 / × 2 | raport `obliczenia/plyta_fundamentowa_MES.md`; weryfikacja Hetényi (błąd < 1 %) |
| Z5 | Obciążenia ścian na płytę fundamentową — średnia krocząca 2,0 m | rozkład obciążenia przez mur i ławę-żebro (kąt rozkładu ≈ 45° na wysokości ściany parteru) |
| Z6 | Pozycje ław/stóp izolowanych biblioteki (ZF, SF) zastąpione MES płyty z żebrami; głębokość posadowienia — izolacja obwodowa PN-EN ISO 13793 (W-284, wariant płyty) | koncepcja: płyta na XPS; warunek D ≥ 1,0 m dotyczy ław |
| Z7 | Pręty górne belek i nadproży ≥ 0,15·A_s,dół | PN-EN 1992-1-1 9.2.1.2(1) (konstrukcja monolityczna z wieńcem) |
| Z8 | Pręty płyt dobrane na rysunku (φ ≤ 25) gdy pręty przyjęte w bibliotece (φ ≤ 16) < A_s,req | A_s,req bez zmian; kontrola `kontrola_zbrojenia.md` |
