# Koncepcja wybrana – „BRAMA I LATARNIA” (synteza panelu: K5 + przeszczepy)

**Siedziba UMWD i Sejmiku Województwa Dolnośląskiego, Wrocław, Mazowiecka / Wybrzeże J. Słowackiego, przy przyczółku Mostu Grunwaldzkiego**
Wersja syntezy 1.0 · 17.11.2026 · podstawa: werdykt panelu (`panel/werdykt_panelu.md`: K5 – 5/5 pierwszych miejsc, średnia 42,8 pkt, Borda 20/20).
Geometria z `model/site.json` (układ lokalny e, n; H w PL-EVRF2007-NH). Liczby geometryczne policzono w shapely na `site.json` (skrypty robocze w katalogu sesji). Dane maszynowe: `model/koncepcja.json`.
**±0,00 = 119,30 m n.p.m.** (posadzka parteru; skwer 9/2 119,30–119,49, Wybrzeże 119,16–119,26).
Zgodnie z decyzją Inwestora nie korzystano z żadnych informacji o rzeczywistych pracach ani wynikach tego konkursu.

Spis: 1 idea · 2 słabości i ich usunięcie · 3 przeszczepy i sprzeczności · 4 bryły · 5 konstrukcja · 6 kondygnacje · 7 kondygnacja Sejmiku · 8 elewacje · 9 zagospodarowanie · 10 ekologia · 11 dostępność · 12 bilanse i koszt · 13 § 13 / § 60 · 14 kadry wizualizacji · 15 plansze i opis · 16 ryzyka resztkowe.

---

## 1. Nazwa, hasło, idea

**Nazwa:** BRAMA I LATARNIA.

**Hasło:** *Z mostu przez bramę do ogrodu kwartału – a nad bramą Sejmik obraduje pod okiem obywateli, na tle Odry i Ostrowa Tumskiego.*

**Idea (148 słów).** Kwartał przy Kaiserbrücke kończył się w 1934 r. zaokrąglonym narożnikiem. Przywracamy go w języku wrocławskiego modernizmu (Mendelsohn, Poelzig, Scharoun). Ten jeden narożnik pełni dwie role obywatelskie. W parterze jest **Bramą Mostową**: łukowym podcieniem, z którego prosta, przekątna oś Hali Obywatelskiej prowadzi wzrok i krok z mostu do publicznego, nieogrodzonego ogrodu kwartału z zachowanymi drzewami ogródków. Na szczycie jest **Latarnią Sejmiku**. Prezydium obraduje przy pełnej ścianie z godłem. Radni siedzą przed panoramą Odry, mostu i katedry, a obywatel z galerii widzi swój Sejmik na tle miasta. Wieczorem miasto widzi salę przez kamienne lamele. Reszta budynku milknie. Pierzeja Mazowieckiej to cztery „posesje” w skali kamienic z gzymsem w linii Mazowieckiej 19. Wieża ma wielki porządek granitowych filarów. Materiały są trzy: jasny granit, kremowa ceramika i ciemny metal.

---

## 2. Słabości wskazane przez sędziów – jak zostały usunięte

| # | Słabość K5 (sędziowie) | Rozwiązanie w syntezie (liczby) |
|---|---|---|
| 1 | Prezydium przed panoramą 33 × 10,2 m, przeciwświatło (J1, J2, J4) | Sala odwrócona (przeszczep K3). **Prezydium i mównica przy pełnej ścianie pd.**, godło z brązu na balustradzie galerii nad prezydium. Panorama jest **za plecami radnych** i oświetla prezydium od przodu światłem z pn./pn.-wsch. Kamery na prezydium mają tło pełne. Ujęcia radnych pod okno łagodzą lamele 0,60 m, rolety screen 5 % i światło TV ≥ 800 lx w pionie. |
| 2 | Bilans poziomu Sejmiku się nie zamyka; brak korytarza (J1, J2, J4) | Rzut rozpisany w shapely (rozdz. 7). Wnętrze 1 080,1 m² = pomieszczenia (z salą i holem) 836,3 + trzony 119,2 + galeria kuluarowa 87,8 + ściany wewn. 36,9 (+ ściany zewn. 65,7 do PC 1 145,8). **Kuluar 2,25 × 39,0 m** (przeszczep K4) łączy obie klatki, salę (wejście prezydium) i wszystkie komisje i kluby. Sala zmniejszona do 287,4 m² (zakres 280–380), hol 79,9 m² + kuluar 87,8 m² = 167,7 m² (program 150). |
| 3 | Pomost techniczny 6,6 m z 4 centralami = kondygnacja techniczna (J1, J2, J5) | Pomost usunięty. Centrale piętrowe 25 m² w strefie środkowej wieży (kond. 1–5; kond. 5 obsługuje także 6). Centrale parteru i Sejmiku na −1. Nad komisjami jest tylko przestrzeń sufitowa ≤ 1,95 m bez podłogi i bez urządzeń, czyli nie jest to kondygnacja (WT § 3 pkt 16). |
| 4 | Kondygnacja Sejmiku 12 m – nadmiar kubatury (J2, J3, J4, J5) | **P+6+S** w tej samej bryle zewnętrznej. Sejmik ma **8,90 m** (sala 6,85 m w świetle, antresola +3,60 m). Dodatkowa kondygnacja biurowa (+1 145,8 m² PC) mieści w całości sale narad i magazynki przy elewacji (poz. 8, 18). Wieża ma 37,6 m (K5: 36,8 m). Dach podniesiono o 0,65 m wyłącznie dla zapasu MPZP 1,06 m. |
| 5 | ≈ 650 m² pełnego szkła w koronie (J1, J3, J4, J5) | Przeszklenia korony **262 m²** (−60 %). Na łuku pionowe lamele ceramiczne 0,25 × 0,60 m co 0,90 m (przesłonięcie ≈ 28 % w osi, do 100 % pod kątem > 34°). Okno holu pn. podzielone filarami 1,05 m (kwatery 1,65 × 5,0 m). Szkło g = 0,27, R ≤ 12 %. Nocą korona świeci tylko światłem wnętrza podczas sesji (≤ 5 lx na elewacji, WT § 293). |
| 6 | Wstęgi w pierzei Mazowieckiej, słabe „posesje” (J1, J2, J3, J4) | Porządek pionowy (przeszczep K1). Oś okien **2,025 m** (kamienica: ≈ 2,2 m), okna **1,20 × 2,40 m (1 : 2)**, WWR 38 %. Cztery „posesje” 12,15 / 16,20 / 16,20 / 12,15 m różnią się odcieniem ceramiki i reliefem filarów 0 / 0,08 / 0,15 / 0,08 m. Pasma poziome zostały tylko na łuku narożnika. |
| 7 | Ślepa ściana pd. segmentu SE (J1, J3, J4, J5) | Relief ceramiczny w osiach 2,025 m (pilastry płytkie 0,12 m, fugi z ciemnego metalu) w rysunku elewacji frontowej + pnącza na linkach (7 sadzonek winobluszczu w pasie 4,6 m od granicy dz. 10/2). Nad nią **taras nad Oławą** (167 m², +19,80) z balustradą cofniętą 1,5 m. |
| 8 | 3 z 6 sal narad bez okien (wszyscy) | **6/6 sal narad przy elewacji** (P: brak; kond. 1, 2, 3 ×2, 4, 5). Format głęboki 7,60 × 7,90 m = 60 m² w pierścieniu wieży. |
| 9 | Brama ogrodowa 2,7 m (J1) | **4,05 m** (3 moduły) × 15,0 × wys. 4,80 m, w poziomie chodnika (118,70 → 118,90), granitowy portal na styku posesji M1/M2. |
| 10 | Zapas dachu wieży 0,41 m (J1, J5) | Najniższy punkt pokrycia **155,50 m n.p.m.** = 36,06 m nad najwyższym terenem w A (119,44). Zapas **1,06 m**. Attyka 156,50 (37,62 m nad 118,88). |
| 11 | Obie klatki w jednym trzonie (J2) | **Dwa trzony** w odległości 20,0 m. A (radni, pracownicy, dźwig ratowniczy) w środku-zachodzie, B (publiczność, dostawy) przy pd. Spełnia też rozp. MSWiA o MDS (2 klatki ≥ 15 m). |
| 12 | Podnośnik na rzędy (J2, J4, J5) | Rzędy +0,15 / +0,30 / +0,45 m z **pochylniami bocznymi ≤ 5 %** (3,0 m na uskok). **Stanowisko dla wózka w każdym rzędzie** (przeszczep K4). |
| 13 | Dostawy po dz. 10/2, rampa 20 % (J2) | **Jeden punkt obsługi w segmencie SE** od Wybrzeża (przeszczep K4). Dostawy samochodami ≤ 2,20 m rampą na −1 do zatoki przy dźwigu T 2 t. Dz. 10/2 nie jest używana przez nasz ruch. Rampa **≤ 18 %** z przejściami 9 %, w całości pod dachem segmentu. |
| 14 | Brama garażu 9–11 m od WS 5, hałas (J3) | Brama 6,0 m w elewacji wsch. segmentu, **15,0 m od okna lok. 6/6A**, zwrócona na wsch. (okno patrzy na pn.). Zasłania ją bryła segmentu. Rampa obudowana, ściany chłonne, cicha brama rolowana. |
| 15 | Pasaż w kształcie L (J3) | **Prosta oś przekątna** (azymut 211,7°, 33,4 m + podcień 3 m) od drzwi w łuku (101,86; 71,57) do drzwi ogrodowych (84,32; 43,12). Z progu widać drzewa ogródków (D795, D797). W najwęższym miejscu (między blokiem WC a trzonem B) ma 6,3 m (przeszczep K3). |
| 16 | Ażurowa brama 2,5 m na dz. 10/2 (J3) | Usunięta. Nic nie stoi na dz. 10/2. Pas 4,6 m w obszarze inwestycji między segmentem a dz. 10/2 to otwarte wejście do ogrodu od bulwaru (ława granitowa, 2 drzewa, bez furty). |
| 17 | Rezerwa budżetowa 2,3 % (J3) | Koszt **146,2 mln zł netto** z **rezerwą 5 % (6,9 mln) w środku** i zapasem 3,8 mln do limitu. Łączny bufor 10,7 mln (7,1 %). Dwie metody (rozdz. 12). |
| 18 | Magazynki „zamienne na biura” w środku (J4) | **20/20 magazynków przy elewacji** (13 standardowych 4,05 × 6,10 m i 7 głębokich 2,70 × 9,25 m w wieży). Każdy ma okno ≥ 3,0 m² i 3 punkty. |
| 19 | Naroże segmentu 2,96 m od dz. 10/2 (J4) | Ściana pd. segmentu **4,58 m** od granicy dz. 10/2 (≥ 3,0 m wg WT § 12 ust. 1). |
| 20 | PV zawyżone (biosolar + zieleń na tych samych m²) (J5) | **Wyłącznie BIPV jako pokrycie** za attyką: wieża 1 040 m² = 208 kWp, skrzydło 780 m² = 156 kWp. Do tego pasy podokienne od dziedzińca ≤ 25 m: 318 m² = 48 kWp. **Razem 412 kWp** (≥ 0,4 MWp M.12). Dachy zielone liczone osobno (tylko taras segmentu). Bez stelaży. |
| 21 | Brak celu GWP (J5) | **GWP ≤ 500 kg CO₂e/m² PC (A1–A5)**, LCA wg PN-EN 15978 i Level(s) od koncepcji, raport A–C wg EPBD art. 7 ust. 2 (przeszczep K1). |
| 22 | Retencja tylko redukuje odpływ (J5) | **Retencja 151 m³** (zbiornik rozsączający 60 + rezerwa zbiornika deszczówki 20 + ogród deszczowy 42 + dach niebieski tarasu 10 + podbudowa nawierzchni 19). To 2,2 × objętość opadu 60 min C = 10 (70 m³), czyli zero odpływu do kanalizacji dla deszczu miarodajnego (przeszczep K4). |
| 23 | Jeden dźwig publiczny (J5) | **P1 i P2**, kabiny 1,4 × 2,4 m, z lobby Wejścia Obywatelskiego wprost na antresolę (przeszczep K3). |
| 24 | 22 punkty EV (J5) | **55 punktów** (1 na 2 miejsca, EPBD art. 14), okablowanie 100 %. |
| 25 | § 13 segmentu – zapas 0,40 / 0,93 m (J5) | Ściana pd. równoległa do szczytu WS 5, 10,58 m od jego lica. Wariant najostrożniejszy (okno w dowolnym miejscu szczytu, wierzchołek w licu wewn., H od najniższych okien 120,0): zapas **1,05 m**. Okno pokoju lok. 6/6A: **3,07 m**. Wieża: **1,49 m** (wymagane 17,5 m). |
| 26 | Podziemie 3 922 m² (J5) | **−2 tylko pod wieżą, segmentem i pasem 7 m dziedzińca** (bez skrzydła). Podziemie **3 763 m²** (−159 m²), 109 m.p. bez platform. Technika usunięta z podziemia (centrale piętrowe, elektryka nad terenem). |

**Korekty własne (błędy K5, których sędziowie nie wskazali):**
(a) Pilastry K5 wystawały ok. 0,30 m poza granicę obszaru (ściana 0,25 m od granicy + pilaster 0,55 m), co narusza Wyj. 7 odp. 28. Teraz **lico zewnętrzne = lico filarów** (0,25 m od granicy), a okna są cofnięte o 0,60 m.
(b) Styk skrzydła z wieżą leżał na linii u = 0, czyli do 0,46 m² skrzydła w A. Teraz lico skrzydła jest na u = −0,05…−0,08 (dylatacja), w A jest 0,00 m².
(c) W ogródkach w obszarze inwestycji rośnie **29** drzew, a nie 33 (`site.json`, weryfikacja).
(d) Rozdzielnia, UPS, BESS i serwerownia leżały w K5 na −1 (poniżej poziomu sytuacji wyjątkowej 119,0). Teraz są nad terenem: rozdzielnia i BESS w segmencie (P), serwerownia i UPS na kondygnacji 1.
(e) Sala 200 os. była pod belkami transferowymi 14,2 m (jak w K1). Teraz stropy skrzydła są sprężone, o rozpiętości 14,2 m bez słupów pośrednich, i sala ma **4,25 m w świetle** bez belek.
(f) Dach rampy wystawał nad teren dziedzińca. Rampa 18 % opada w całości pod segmentem, a strop rampy na wyjściu z segmentu leży na −0,21, poniżej terenu.
(g) § 13 dla własnych pokoi w narożach wklęsłych (segment/wieża, skrzydło/wieża) sprawdzono przy sektorze obróconym (ramię ≥ 12° od lica, por. projekt WT § 12). Naroża pd. wieży zajmują szachty i WC.
(h) Parter skrzydła (±0,00) leży 0,6–0,7 m nad chodnikiem w części pd. Wejścia są tylko tam, gdzie różnica ≤ 0,15 m. Na południu cokół granitowy 0,70 m, jak boniowany parter Maz. 19 (+0,73).

---

## 3. Przeszczepy (wzmacniające jedną ideę) i rozstrzygnięte sprzeczności

**Przyjęte (każdy wzmacnia „Bramę” albo „Latarnię”):**
1. **K3 – prezydium przy pełnej ścianie; publiczność widzi Sejmik na tle miasta.** Latarnia pozostaje latarnią, ale z punktu widzenia obywatela, nie prezydium. Usuwa wadę nr 1.
2. **K3 – Wejście Obywatelskie** od bulwaru z własnym lobby (57 m²), kontrolą, szatnią i dwoma dźwigami P1/P2 wprost na galerię. Druga, obywatelska brama do Latarni.
3. **K3 – prosta oś most → ogród.** Brama staje się przejściem na wylot.
4. **K4 – kuluar, pochylnie ≤ 5 %, stanowisko dla wózka w każdym rzędzie, pokój cichy** (16 m², w hali przy trzonie A).
5. **K3/K2 – dwa oddzielne trzony.** Bezpieczeństwo i rozdział ruchu radni/publiczność.
6. **K1 – pionowy porządek, segmentacja posesji, przęsło przejściowe przy Maz. 19, lamele przed salą.** Spokój pierzei wzmacnia gest narożnika (kontrast „pion–łuk”).
7. **K1 – rygor bilansu; § 13 dla każdego położenia okna; GWP ≤ 500.**
8. **K1/K4 – brama ogrodowa 4,05 m; taras nad Oławą** na dachu segmentu.
9. **K4 – obsługa w jednym punkcie (segment SE), retencja z zerowym odpływem, narracja Ogrodu Województwa.** Ogród jest celem drogi przez Bramę.
10. **K2/K1 – pamięć miejsca:** cegła i gruz z wykopu w posadzkach ścieżek ogrodu i w „ścianie pamięci” lapidarium, ślad pierzei z 1934 r. w posadzce skweru ze szpalerem 4 lip, napis „SEJMIK WOJEWÓDZTWA DOLNOŚLĄSKIEGO” wykuty w granitowym nadprożu Bramy Mostowej, budki dla jerzyków w kasetach elewacji dziedzińcowych (24 szt.).
11. **K2 (częściowo) – arkada:** podcień 3,0 m na całym łuku i dalej na 12,5 m elewacji pn. (96,4 m²) jako zadaszona krawędź skweru od mostu do drugiego wejścia od Placu Mostowego.
12. **K3/K4 – drogi pożarowe z ulic.** Skwer 9/2 nie jest drogą pożarową, więc może mieć drzewa.

**Odrzucone (z uzasadnieniem):**
* **HBV w skrzydle (J1, J4, J5):** skrzydło jest częścią jednego budynku W, więc obowiązuje NRO (WT § 212/216) i trzeba by iść drogą rozwiązania zamiennego (3–6 mies.). Rozpiętość 14,2 m bez słupów, która daje salę 200 os. bez transferu, jest dla HBV nieracjonalna. Ślad węglowy obniżają CEM III, stropy sprężone, kruszywo z recyklingu i stal z pieca łukowego.
* **Platformy parkingowe** (wariant J5 „−2 tylko pod wieżą + platformy”): sami sędziowie (J1, J3, J4, J5) krytykowali je w K1.
* **Latarnia ponad dachem (K4), kampanila (K2):** jedna dominanta, spokojne zwieńczenie (DWKZ).

**Sprzeczności rozstrzygnięte:**
* *Dostawy z Wybrzeża (J2) vs obsługa na bulwarze jako wada (J3):* jeden portal na skrajnym, pd. odcinku frontu (segment, 10,55 m). Brama garażowa 6,0 m i drzwi trafo/odpadów stoją we wspólnym rytmie granitowych filarów. Pozostałe 38 m frontu od bulwaru jest publiczne: Wejście Obywatelskie, kancelaria, podcień.
* *−2 tylko pod wieżą (J5) vs parkowanie ≥ 104 m.p. (MPZP) i krytyka platform:* −2 pod wieżą, segmentem i pasem 7 m; 109 m.p. bez platform; podziemie −159 m².
* *Centrale na −2 (J1, J2) vs „technika krytyczna nad poziomem zalewu” (brief):* centrale nie są krytyczne, ale skracamy piony i rozdzielamy strefy pożarowe, więc są piętrowe. Krytyczna elektryka stoi nad terenem.
* *Pełna kubatura Sejmiku (K5) vs minimum 35 m w A:* dodatkowa kondygnacja biurowa w tej samej bryle (PC/PU 1,68 < 1,71 programu).

---

## 4. Bryły

### 4.1 Obrysy (e, n), CCW

| Bryła | Obrys (e; n), CCW | Rzut | Kond. |
|---|---|---:|---|
| **W – Wieża Sejmiku** (w A) | SW (74,606; 40,756) → SE (113,468; 50,230) → początek łuku (109,750; 65,483) → **łuk R = 14,00 m**, środek (96,148; 62,167), przeciwnie do ruchu wskazówek → koniec łuku (92,832; 75,769) → NW (67,572; 69,611). W układzie (u, v): prostokąt 40,00 × 29,70 m, łuk z (40; 15,7) do (26; 29,7) | **1 145,83 m²**, poza A **0,000 m²** | P+6+S (+ antresola) |
| **M – Skrzydło Mazowieckie** | (48,842; 9,683) → (61,251; 66,053) → **łuk R = 3,50 m**, środek (64,669; 65,301), kąt naroża 116,1° → (63,840; 68,701) → (67,494; 69,592) → (74,557; 40,744) → (70,839; 39,838) → (63,498; 6,487) | **847,00 m²**, w A **0,000** | P+4 |
| **S – Segment Wybrzeża** | (96,694; 38,813) → (115,979; 39,930) → (113,480; 50,181) → (95,020; 45,681) | **167,40 m²**, w A **0,000** | P+4 |
| **Razem** (z wypełnieniem dylatacji) | | **2 162,9 m²** (58,0 % obszaru inwestycji) | |

Kontrole (shapely): wieża 0,25 m od granicy pn. (1KDG), 0,59–0,68 m od wsch. (6KDB/2); łuk 0,45 m od ścięcia granicy (dz. 19/1). Skrzydło: lico zach. na granicy z dz. 8/8 (droga, WT § 12 ust. 10), lico pd. przylega do szczytu Maz. 19 na 15,0 m (§ 12 ust. 3). Segment: 0,22 m od granicy wsch., 4,58 m od dz. 10/2. **Żadnych nadwieszeń poza obszar.** Gzymsy, attyki i lamele leżą w obrysie (Wyj. 7 odp. 28). Część wyższa niż 25 m istnieje wyłącznie w A, a w A nie ma dachu niższego niż 35 m.

### 4.2 Rzędne kondygnacji (±0,00 = 119,30 m n.p.m.)

| Kond. | Posadzka wzgl. | m n.p.m. | Wys. kond. | Strop nad kondygnacją: wierzch konstr. / spód (wieża; skrzydło) | Zakres |
|---|---:|---:|---:|---|---|
| −2 | −7,00 | 112,30 | 3,25 | wierzch −3,90 / spód −4,25 | wieża + segment + pas 7 m |
| −1 | −3,75 | 115,55 | 3,75 | wierzch −0,15 / spód −0,50 | całość + pas dziedzińca |
| P | ±0,00 | 119,30 | 4,80 | +4,65 / +4,37; +4,25 | całość |
| 1 | +4,80 | 124,10 | 3,75 | +8,40 / +8,12; +8,00 | całość |
| 2 | +8,55 | 127,85 | 3,75 | +12,15 / +11,87; +11,75 | całość |
| 3 | +12,30 | 131,60 | 3,75 | +15,90 / +15,62; +15,50 | całość |
| 4 | +16,05 | 135,35 | 3,75 | wieża +19,65 / +19,37; dach skrzydła +19,80 / +19,40; dach segmentu +19,50 | całość |
| 5 | +19,80 | 139,10 | 3,75 | +23,40 / +23,12 | wieża (= poziom tarasu segmentu) |
| 6 | +23,55 | 142,85 | 3,75 | +27,15 / +26,87 | wieża |
| **S** | **+27,30** | **146,60** | **8,90** | dach: ruszt 1,60 m, spód +34,15 | wieża |
| antresola S | +30,90 | 150,20 | — | — | wieża |

Wysokości w świetle: biura w wieży 3,32 m (płyta 0,28 + podłoga 0,15; TABS odsłonięty, baffle); biura w skrzydle 3,20 m (płyta 0,40); parter wieży 4,37 m; sala 200 os. 4,25 m bez belek; sala obrad 6,85 m.

### 4.3 Dachy a MPZP (od najniekorzystniejszego terenu w pasie 2 m wokół bryły)

| Dach | Teren min / max | Najniższy pkt pokrycia | → nad najwyższym terenem | Najwyższy pkt (attyka) | → nad najniższym terenem | Pasmo MPZP |
|---|---|---|---:|---|---:|---|
| Wieża (A) | 118,88 / 119,44 | +36,20 = **155,50** | **36,06 m** (≥ 35; zapas 1,06) | pokrycie max +36,45 = 155,75; attyka +37,20 = **156,50** | **37,62 m** (38,17 od 118,33) | 35–45 ✔ |
| Skrzydło | 118,40 / 119,41 | +20,20 = **139,50** | **20,09 m** (≥ 18; zapas 2,09) | pokrycie max 139,70; gzyms-attyka **140,15** | **21,75 m** | 18–25 ✔ |
| Segment (taras) | 118,91 / 119,18 | taras +19,80 = **139,10** | **19,92 m** (zapas 1,92) | attyka **140,15** | **21,24 m** | 18–25 ✔ |

Gzyms 140,15 = attyka Maz. 19 (140,24) −0,09 m (E07 „wyrównaj”). Spód gzymsu 139,45 (Maz. 19: 139,49). Hełmy pylonów mostu ≈ 147 m n.p.m. (szac.) leżą 6,9 m nad gzymsem kwartału.

### 4.4 Cofnięcia i wnęki

* **Podcień „Brama Mostowa”:** łuk między R 14 a R 11 (szklenie na R = 11,0 m) + elewacja pn. u 13,5–26,0 (szklenie na v = 26,70). Razem 96,4 m², głębokość 3,0 m, wys. 4,80 m, posadzka z granitu w poziomie skweru.
* **Brama ogrodowa:** (51,454; 21,549)–(52,325; 25,504)–(66,974; 22,280)–(66,103; 18,324). 4,05 × 15,0 m, wys. 4,80 m, 60,8 m².
* **Wnęki wejść 1,5 m** (WT § 292): Wejście Obywatelskie (elewacja wsch. wieży, v 1,4–6,8), wejście konferencyjne (dziób NW skrzydła), wejście ogrodowe (elewacja pd. wieży, u 8,6–11,4), wejście od skweru (podcień pn., u 21–24).
* **Ościeża:** wieża 0,60 m; skrzydło i segment 0,35 m. Kond. 6 („kondygnacja cienia”): szkło i metal 0,40 m za licem filarów. Łuk korony: lamele 0,60 m przed szkłem.
* Brak kondygnacji cofniętych. Brak balkonów powyżej 25 m (taras segmentu leży na +19,80).

---

## 5. Konstrukcja, trzony, posadowienie

**Siatka.** Wieża: moduł 1,35 m, filary elewacji co 2,70 m, słupy w co trzecim filarze, czyli osie u = 0,00 / 8,10 / 16,20 / 24,30 / 32,40 / 40,00 i v = 0,00 / 8,10 / 21,60 / 29,70. Na łuku słupy promieniowe co 15° na R 13,50 i R 7,00. Płyty sprężone 0,28 m z TABS, rozpiętości ≤ 8,10 m. Słupy wewnętrzne kończą się na stropie S. Dach S to ruszt stalowy z kratownic 1,60 m (rozpiętość 19,5 m nad salą) z płytą zespoloną, oparty na ścianach trzonów, ścianie pd. sali i filarach łuku. Skrzydło: słupy w filarach obu elewacji co 4,05 m (2 osie okienne), płyty sprężone 0,40 m o rozpiętości **14,20 m bez słupów pośrednich**, dzięki czemu garaż pod skrzydłem ma 2 rzędy stanowisk bez słupów. Segment: słupy elewacyjne co 4,05 m, ściana pd. żelbetowa, płyta 0,28 m. Kondygnacje P–4 są ciągłe w rzucie (bez dylatacji w poziomie stropów; wspólna płyta fundamentowa). Uskok dachów na linii A to tylko obróbka.

**Trzony** (współrzędne (u, v) → e, n w `koncepcja.json`):

| Trzon | Obrys | Zakres | Skład |
|---|---|---|---|
| **A** | u 8,30–15,50 × v 12,45–20,85 (60,5 m²); (79,721; 54,818)–(86,716; 56,523)–(84,727; 64,684)–(77,732; 62,979) | −2…S | klatka A REI 60, biegi 1,60 m (M.13), przedsionek ppoż. 2,4 × 3,0 m z MOE 0,9 × 1,4 m, krzesłem ewakuacyjnym i interkomem, nadciśnienie; dźwigi A1, A2 po 1 600 kg; **R – dźwig dla ekip ratowniczych PN-EN 81-72 i ewakuacyjny PN-EN 81-76**, 1 000 kg, kabina 1,1 × 2,1 m, szyb REI 60; szachty nadciśnienia, oddymiania korytarzy, pionów |
| **B** | u 24,85–31,10 × v 0,50–9,90 (58,8 m²); (98,631; 47,127)–(104,703; 48,607)–(102,476; 57,740)–(96,404; 56,260) | −2…S + antresola | klatka B jw. z przedsionkiem i MOE; **P1, P2** publiczne 1 275 kg, kabiny 1,4 × 2,4 m, przystanki −2…6, S, antresola +30,90 (P2 z drzwiami przelotowymi do przedsionka publicznego na S); **T** osobowo-towarowy 2 000 kg, kabina 1,5 × 2,7 m |
| **C** (skrzydło) | s 0,5–8,6 × d 8,4–14,5; (57,153; 8,365)–(58,894; 16,276)–(64,852; 14,965)–(63,110; 7,054) | −1…4 | klatka C z przedsionkiem i MOE; dźwig C1 1 000 kg z drzwiami przelotowymi (przyszłe połączenie z Maz. 19 na jej rzędnych) |

Odległość klatek A–B: **20,0 m**. Dojście z drogi pożarowej (dalszy pas Wybrzeża) do dźwigu R: ok. 37 m (≤ 50 m).

**Ustrój:** żelbet monolityczny, sztywność dają trzony A, B, C i ściana przy Maz. 19 (REI 120). Beton CEM III/A–B, kruszywo z recyklingu w elementach niekonstrukcyjnych, stal zbrojeniowa i konstrukcyjna z pieca łukowego.

**Posadowienie i woda gruntowa** (`geotechnika.md`): ZWG średnio 115,5, maks. 116,45, poziom obliczeniowy ≥ **117,0**, sytuacja wyjątkowa 119,0 m n.p.m.
* **Obudowa:** ściany szczelinowe 0,80 m na całym obwodzie −1 (**244,6 m**), wcięte w gliny zwałowe QpB (strop 101,8–103,4), głębokość ≈ 18 m, czyli ok. 4 400 m². Biała wanna, odwodnienie tylko wewnątrz obudowy, **bez obniżania zwierciadła poza wykopem** (ochrona Maz. 19, WS 5–6 i drzew).
* **Wieża:** płyta palowo-fundamentowa 1,10 m na −2 (spód 111,20 m n.p.m. ≈ 4,2 m pod ZWG maks.), 36 pali CFA Ø 0,8 m, L ≈ 14 m, oparte na glinach.
* **Skrzydło i segment:** płyta 0,90 m (ciężar budynku > wypór 25–55 kPa). Pas dziedzińca bez nadbudowy: mikropale kotwiące (175 m²).
* Przy Maz. 19: rozpory i monitoring geodezyjny, bez wibracji. Przy D703, D704, D886: palisada sieczna zamiast skarpy.
* **Zabezpieczenie przed wodą powierzchniową:** próg rampy 119,60 (+0,30) z prowadnicami zapór mobilnych do +1,00, zawory zwrotne, pompownia.

---

## 6. Organizacja kondygnacji

**Moduł i pokój.** Moduł 1,35 m. Pokój 24 m² = 3 moduły: oś 4,05 m, szerokość netto 3,95 m × głębokość netto 6,10 m = **24,1 m²**. Pokój GW 32 m²: w skrzydle 4 moduły (5,30 × 6,10 = 32,3 m²), w wieży „głęboki” 3,95 × 8,10 = 32,0 m². Sala narad 7,60 × 7,90 m = 60 m². Magazynek głęboki 2,60 × 9,25 m = 24,05 m². Okno pokoju 24 m² w wieży (1,5 przęsła) to 6,1 m² w świetle ościeżnic, w skrzydle (2 okna) 5,8 m², czyli ≥ 1/8 podłogi (WT § 57).

**Trakty.** Wieża: pokoje 6,10 | korytarz pierścieniowy 1,80 | strefa środkowa ≈ 12,2 m (trzon A, WC, socjalne, centrala 25 m², MFP, PD, porządkowe, miejsca oczekiwania, budki do rozmów) | 1,80 | 6,10. Skrzydło: trakt dwustronny 15,0 m (0,50 + 6,10 + 1,80 + 6,10 + 0,50). Segment: pokoje od Wybrzeża + korytarz w osi korytarza wsch. wieży + pas usług od zach.

**Pojemność elewacyjna** (jednostki 4,05 m przy głębokości 6,10 m): kondygnacje 1–4 po **43** (skrzydło: ulica 13 + dziób 1 + dziedziniec 6; wieża: pn. 6 + łuk 4 + pd. 6; elewacja wsch. wieży i segmentu 6; segment zach. 1); kondygnacje 5 i 6 po **24**; parter 4. Razem 224. Zajęte 220,8, rezerwa 3,2 jedn.

### Rozmieszczenie (187 pokoi wg zał. 1 M.01; departamenty niedzielone)

| Kond. | Komórki (pokoje) | Pokoje | Sale narad | Magazynki 24 m² (przy elewacji) | Socjalne 24 m² | Inne |
|---|---|---:|---:|---:|---:|---|
| −2 | – | – | – | – | – | garaż 41 m.p. (budowla ochronna – ukrycie), maszynownia GPC + bufory 120 m², tryskacze 80 m², agregat HVO 25 m² (spaliny szachtem do elewacji od dziedzińca), filtrowentylacja 30 m², zbiornik deszczówki 50 m³ |
| −1 | – | – | – | – | – | garaż 68 m.p. (6 OzN), zatoka dostaw przy dźwigu T, odpady 24 m², centrale P i S 80 m², przyłącze wody i woda szara 50 m², szatnie i prysznice rowerzystów i personelu 40 m², warsztat PPT 40 m², magazyn MDS 20 m², pralnia 10 m² |
| P | **DK II (2)**, **DW (2)** | 4 | – | – | – | strefa publiczna, centrum konferencyjne, bistro (niżej) |
| 1 | **DOS (38)** | 38 | 1 | 3 (głębokie) | 3 | serwerownia TIER II 50 m² + UPS 15 m² (strefa środkowa) |
| 2 | **DI (25) + DST (13)** | 38 | 1 | 3 | 3 | – |
| 3 | **DGP (24) + GW (11 = 8 × 32 m² w wieży + 3 × 24)** | 35 | 2 | 4 | 3 | archiwa GW 48 + 24 m², pracownia/urządzenia GW 24 m² (Wyj. 6 odp. 26) |
| 4 | **pion 8: CZ (3) + DKD (12) + DZ (19)**, gabinety CZ, dyrektorów departamentów i wydziałów obok siebie przy trzonie A (Wyj. 10 odp. 62) | 34 | 1 | 6 | 3 | – |
| 5 | **DSS (19)** | 19 | 1 | 4 (głębokie) | 2 | wyjście na taras nad Oławą (167 m²) |
| 6 | **Kancelaria Sejmiku (8)** + gabinet Przewodniczącego 40 m² i asystent 14,5 m² (łuk NE, widok na most) + zaplecze 8 m² + 3 gabinety Wiceprzewodniczących po 30 m² + 2 sale spotkań 20 os. po 44 m² (wnętrze, przeszklone) + miejsce oczekiwania 12 m²; **DRA (11)** | 19 | – | – | 1 | połączenie z kondygnacją Sejmiku dźwigami A1/A2 i klatką A |
| S | Sejmik (rozdz. 7) | – | – | – | – | – |
| **Σ** | | **187** (179 × 24 + 8 × 32) | **6** | **20** | **15** | MFP 10, porządkowe 12, PD na każdej kondygnacji |

Na każdej kondygnacji 1–6 jest zespół WC w strefie środkowej wieży (K, M, toaleta dostępna). Na kond. 1–4 drugi zespół przy trzonie C. Miejsca oczekiwania (9) leżą przy sekretariatach. Strefy pożarowe: kond. 1–4 po 2 160 m², P 2 003 m², S z antresolą 1 215 m² (< 2 500).

**Parter (P):**
* **Wieża (1 049,5 m² PC poza podcieniem):**
  * Hala Obywatelska z osią przekątną: informacja 8 m², poczekalnia 40 m², lapidarium (ściana witryn 12 m przy trzonie A + ślad murów piwnic inkrustowany w posadzce), pokój cichy 16 m²;
  * kancelaria ogólna 36 m² (3 stanowiska, lada niska 0,75 m, pętla) z zapleczem **DK II** (2 pokoje od Wybrzeża);
  * **Wejście Obywatelskie** – lobby 57 m² z kontrolą i szatnią przy P1/P2 (u 31,25–39,5 × v 0,5–7,45);
  * WC ogólnodostępne 19 m² + **komfortka 12 m²** (3,0 × 4,0 m, 14 m od wejścia głównego; u 15,65–21,0 × v 15,0–20,85);
  * centrum monitoringu 24 m² + socjal ochrony 10 m² + szatnie i WC personelu (u 0,5–8,15 × v 12,45–20,85);
  * **rowerownia 50 stanowisk** 90 m² (u 0,5–8,15 × v 0,5–12,3) z wjazdem od dziedzińca, zaplecze na −1 przy trzonie A;
  * łącznik do foyer skrzydła z oknami na skwer (u 0,5–13,35 × v 21,0–29,2); drugie wejście od skweru w podcieniu pn. (u 21–24).
* **Skrzydło (786,2 m²):**
  * M1 (s 0–12,15): DW (2 pokoje od ulicy), trzon C, pokój techników 20 m², socjal personelu technicznego 20 m²;
  * brama ogrodowa (s 12,15–16,20);
  * **sala 80 os.** 6,90 × 14,0 = 96,6 m² (s 16,35–23,25);
  * **sala 200 os.** 16,20 × 14,0 = 226,8 m², w tym 2 reżyserki po 10 m², dzielona ścianą mobilną na 2 × 103 m², 4,25 m w świetle (s 23,40–39,60);
  * foyer 80 m², szatnia 20 m², WC konferencyjne 40 m², magazyn mebli 25 m² (s 39,75–50);
  * **bistro** 92 m² (sala 70 + zaplecze 22) w dziobie NW z tarasem na najszerszej (17,9 m) części skweru; obok wejście konferencyjne.
* **Segment (167,4 m²):** rampa garażu 6,5 m (2 × 3,0 m) wzdłuż ściany pd., brama 6,0 m od Wybrzeża; w pasie pn. trafo SN/nn 21 m² (drzwi od Wybrzeża), rozdzielnia nn z SZR 17 m², BESS 250 kWh 11 m² (EI 120), punkt wystawienia odpadów 7 m² przy dźwigu T.

---

## 7. Kondygnacja Sejmiku (+27,30 = 146,60 m n.p.m.; h = 8,90 m; antresola +30,90)

**Zasada (Wyj. 21 odp. 85; WT § 3 pkt 19).** Wszystkie pomieszczenia zamknięte programu Sejmiku leżą na poziomie głównym w obrysie wieży, czyli w całości w A (wieża poza A: 0,000 m²). Antresola (69,7 m², 6 % rzutu) jest w całości otwarta na salę i kuluar. Mieści tylko galerię publiczności i foyer publiczne pełniące funkcję sali multimedialnej. Kancelaria Sejmiku leży kondygnację niżej (kond. 6). Wewnętrzne lico ścian zewnętrznych jest 0,50 m od obrysu.

### 7.1 Poziom główny – pomieszczenia (powierzchnie netto policzone z rzutu)

| Kod | Pomieszczenie | Położenie (u, v) | m² | Program (zakres) |
|---|---|---|---:|---|
| SWD.01 | **Sala obrad** (płyta) | u 20,00–39,50 × v 12,45–29,20 minus łuk R 13,5 | **287,4** | 320 (280–380) ✔ |
| SWD.02 | **Hol reprezentacyjny**: 2 kondygnacje, narożnik NW z oknami na pl. Społeczny i Ostrów Tumski; w nim lada baru SWD.05 (30 m², przyłącza) i szatnia SWD.06 (12 m²) | NW + korytarz pn. + pasaż zach. | **79,9** | 150 (120–220): razem z kuluarem **167,7** ✔ |
| KUL | **Galeria kuluarowa** (okna na zach. i wsch.; w części zach. wysokość 8,9 m) | v 10,05–12,30 × u 0,50–39,50 | **87,8** | (komunikacja, przeszczep K4) |
| SWD.08 | Sala komisji 50 os. | u 0,50–10,65 × v 0,50–9,90 | 95,4 | 100 (90–120) ✔ |
| SWD.10a/b | 2 zaplecza nagrań komisji (okna do sal) | u 10,80–12,75 | 2 × 9,0 | 10 (8–12) ✔ |
| SWD.09 | Sala komisji 30 os. | u 12,90–18,80 × v 0,50–9,90 | 55,5 | 60 (54–72) ✔ |
| SWD.11a | Klub radnych 30 os. (1) | u 18,95–24,70 × v 0,50–9,90 | 54,1 | 60 (54–72) ✔ |
| SWD.11b | Klub radnych 30 os. (2) | u 31,25–39,50 × v 0,50–7,10 | 54,5 | 60 (54–72) ✔ |
| SWD.12a/b | 2 kluby radnych 15 os. (okna na zach.) | u 0,50–6,50 × v 12,45–22,80 | 2 × 30,6 | 36 (30–40) ✔ |
| SWD.13 | Wspólna sala radnych (okno na Ostrów Tumski) | u 8,30–14,35 × v 22,55–29,20 | 40,2 | 48 (36–60) ✔ |
| SWD.14 | Pokój socjalny radnych | u 14,50–17,70 × v 22,55–29,20 | 21,3 | 24 (20–30) ✔ |
| SWD.04 | Reżyserka (okno do sali, wgląd na prezydium) | u 15,65–19,85 × v 12,45–16,30 | 16,2 | 20 (15–30) ✔ |
| SWD.07 | Pokój matki z dzieckiem | u 35,15–39,50 × v 7,25–9,90 | 11,5 | 10 (8–12) ✔ |
| SWD.15 | Magazyn podręczny sali | u 15,65–19,85 × v 19,45–20,85 | 5,9 | 10 (6–15) ≈ |
| PHS.05 | WC męskie z toaletą dostępną 12,0; WC damskie z toaletą dostępną 13,3 | | 25,3 | – |
| PHS.05c | Przedsionek publiczny z toaletą dostępną (dostęp wyłącznie dźwigiem P2 z antresoli) | u 31,25–35,00 × v 7,25–9,90 | 9,9 | – |
| C-A, C-B | Trzony A i B | | 119,2 | – |
| | **Suma** | | **1 043,2** | |
| | ściany wewnętrzne | | 36,9 | |
| | **Wnętrze (od lica wewn.)** | | **1 080,1** | |
| | ściany zewnętrzne | | 65,7 | |
| | **PC poziomu głównego = rzut wieży w A** | | **1 145,8** | |

### 7.2 Antresola +30,90 (69,7 m² PC)

* **Galeria publiczności** 32,0 m² (u 21,0–37,0 × v 11,45–13,45; wysunięta 1,0 m nad salę). 2 rzędy, **30 miejsc, w tym 3 dla wózków** w 1. rzędzie bez stopni, balustrada szklana 1,10 m. Filtry prywatności na pulpitach radnych (przeszczep K3) zapewniają poufność głosowania.
* **Foyer publiczne z ekranami** 37,7 m², czyli sala multimedialna / poczekalnia gości SWD.03 (40 m², zakres 30–60). Pas nad północną częścią kuluaru, otwarty na kuluar i salę.
* Pod antresolą kuluar ma 3,25 m w świetle. Nad antresolą jest 3,25 m do rusztu dachu.

### 7.3 Sala obrad

* **Wymiary:** 19,5 × 16,75 m minus łuk, 287,4 m². Wysokość 6,85 m w świetle (+27,30 → spód rusztu +34,15). Kubatura ≈ 1 970 m³, RT ≈ 0,9 s (sufit z baffli, perforowane drewno na ścianach zach. i pd., ściana prezydium rozpraszająca).
* **Układ amfiteatralny bez podnośników:** ognisko rzędów w (u 30,0; v 13,4). Trzy łukowe rzędy R 4,8 / 6,9 / 9,0 m na +0,15 / +0,30 / +0,45: **10 + 15 + 19 = 44 stałe stanowiska** (36 radnych z 4-os. prezydium, 5 członków Zarządu, Skarbnik, Sekretarz, przedstawiciel Wojewody) z głosowaniem, tabletami i mikrofonami. Pochylnie boczne ≤ 5 % (3,0 m na każdy uskok). **W każdym rzędzie miejsce dla wózka** (rząd 1: 2).
* **Prezydium (4) i mównica** (blat regulowany 0,75–0,80 m, pętla) na poziomie podłogi przy **pełnej ścianie pd.**, za nią drzwi z kuluaru. Godło na balustradzie galerii nad prezydium. Światło z łuku pada z przodu.
* **Płyta:** 44 + media 8 + goście 12 + obsługa kancelaryjna 4 + tłumacze PJM 2 (w kadrze kamery przy prezydium) = 70. **Galeria 30. Razem 100.**
* **Panorama za radnymi:** łuk R 13,5 (szkło 22 × 6,6 m za lamelami) + okno pn. między filarami. Widok na most, Odrę i Ostrów Tumski (katedra: azymut ok. 328°, 670 m).
* **Wyjścia:** drzwi do holu (zach.) i 2 drzwi do kuluaru (pd.), odstęp ≥ 5 m (WT § 238). Dojście do klatki B ≤ 22 m, do klatki A ≤ 26 m.
* Wentylacja wyporowa spod rzędów (centrala S na −1, piony w trzonie A). Pętla indukcyjna, napisy na żywo.

**Ruch:** radni, Zarząd i goście jadą dźwigami A1/A2 z holu głównego i z garażu do holu Sejmiku. Publiczność wchodzi od bulwaru: Wejście Obywatelskie → kontrola → P1/P2 lub klatka B → foyer na antresoli → galeria. Do strefy radnych nie wchodzi. Toaleta publiczności jest w PHS.05c (P2, drzwi przelotowe). Druga droga z antresoli prowadzi otwartymi schodami do zach. części kuluaru (w czasie sesji zamknięte drzwiami z zamkiem ewakuacyjnym). Hol Sejmiku łączy się z holem głównym bankiem dźwigów A1/A2 (2 × 21 os./kurs) i P1/P2.

---

## 8. Elewacje

**Materiały (2 mineralne + metal):**
* **G – jasny granit strzegomski płomieniowany**, NCS S 1502-Y. Filary wieży, cokół, gzymsy, kordon, attyka, posadzki zewn. Ta sama rodzina co okładzina pylonów mostu.
* **C – ceramika glazurowana półmatowa** (profile ekstrudowane 40 mm, A1), w odcieniach: M1 S 1505-Y20R, M2 S 1010-Y30R, M3 S 1005-Y20R, M4 S 1510-Y40R, segment S 1010-Y30R, łuk i lamele korony S 1005-Y20R.
* **Me – aluminium anodowane, grafitowy brąz** (RAL 8019 ≈ NCS S 7502-Y). Stolarka, płyciny wieży (od dziedzińca ≤ 25 m jako BIPV w tym kolorze), kondygnacja 6, obróbki, żaluzje czerpni i wyrzutni (tylko od dziedzińca).
* **Szkło:** neutralne, R ≤ 12 %. Biura g 0,33, Tvis 0,62, Uw ≤ 0,80. Korona g 0,27, Tvis 0,48, Ucw ≤ 0,90. Ochrona ptaków od strony Odry (wzór punktowy na szkle korony).

**Kompozycja: cokół / trzon / zwieńczenie.**
* **Skrzydło i segment – porządek kamieniczny:**
  * oś okien **2,025 m** (1,5 modułu), filar 0,825 m, okno **1,20 × 2,40 m** (1 : 2, parapet 0,90 m), ościeże 0,35 m, WWR 38 %;
  * **cokół** (P, 4,80 m): granitowe filary co 4,05 m, witryny na pełną wysokość z naświetlem na **122,77** (linia pasa nad parterem Maz. 19); kordon granitowy 0,35 m na **124,10**; w części pd. (chodnik 118,60–118,72) cokół pełny 0,70 m jak boniowany parter Maz. 19;
  * **trzon** (1–4): ceramika w reliefie posesji;
  * **zwieńczenie:** gzyms-attyka granitowy 1,40 m (spód **139,45**, wierzch **140,15**, wysięg 0,30 m w obrysie).
* **Wieża – wielki porządek:**
  * filary granitowe 1,05 m co **2,70 m**, ciągłe od +4,80 do +37,20 (32,4 m, smukłość 1 : 31);
  * okna **1,65 × 2,45 m** (dwuskrzydłowe, słupek w osi modułu, partycje w filarach lub słupkach), ościeże 0,60 m, płyciny z ciemnego metalu, WWR trzonu 40 %;
  * **kordon kwartału** (pas granitu +19,80–20,85 między filarami) w linii gzymsu skrzydła;
  * **kond. 6 – „kondygnacja cienia”:** szkło i metal 0,40 m za licem filarów, ciemne pasmo oddziela trzon od korony;
  * **korona S** (8,90 m): od pn. okno holu między filarami (kwatery 1,65 × 5,0 m); od pd. i zach. okna komisji i klubów 1,65 × 4,20 m, a nad nimi pas ceramicznych lameli maskujących wyrzutnie wentylacji (strona dziedzińca);
  * **attyka** 1,00 m z granitową czapą i cienką obróbką z ciemnego metalu (0,15 m). Bez masztów i urządzeń na dachu.
* **Narożnik (łuk R 14):**
  * parter – podcień 3,0 m;
  * kond. 1–6 – **5 pasm** ceramiki 1,30 m z oknami wstęgowymi 2,45 m na łuku, jedyne poziome pasma w budynku („ruch mostu”);
  * korona – **pionowe lamele ceramiczne** 0,25 × 0,60 m co 0,90 m, szkło bezpośrednio za nimi (R 13,5);
  * na stykach łuku z elewacjami prostymi masywne filary 2,2 m (SE) i 1,7 m (NW-pn.): pion trzyma poziom.
* **Segmentacja pierzei (DWKZ P8):** Mazowiecka **M1 12,15 | M2 16,20 (z bramą ogrodową 4,05 w pierwszych 3 modułach) | M3 16,20 | M4 12,15** + naroże NW 3,2 m (dziób R 3,5).
  * Posesje różnią się odcieniem ceramiki, reliefem filarów (0 / 0,08 / 0,15 / 0,08 m) i fakturą (gładka / ryflowana co 0,135 m / glazura cieniowana / ryflowana).
  * Fugi między posesjami: pionowa szczelina 0,20 m z ciemnego metalu cofnięta 0,15 m. Wspólne są cokół i gzyms.
  * **M1 – przęsło przejściowe przy Maz. 19** (przeszczep K1): najbliższy kamienicy odcień, pierwsza oś cofnięta 0,30 m, kordon i gzyms w liniach nr 19. Piętra wyraźnie przesunięte względem jej stropów (o 1,0–1,2 m, reguła E07).
  * Wybrzeże: segment 10,55 m (5 osi kamienicznych) | elewacja wsch. wieży 15,7 m (wielki porządek) | łuk 22 m.
* **PV bez podwójnego liczenia:** BIPV jako pokrycie dachów za attyką (wieża 1 040 m², skrzydło 780 m²) + BIPV w płycinach od dziedzińca ≤ 25 m (318 m²). Od ulic i powyżej 25 m PV nie ma (MPZP § 6 pkt 13, WT § 216 ust. 8). Dach zielony ma tylko taras segmentu (osobno).

**Przekrój elewacji 1:50 (warstwy od zewnątrz):**

| Typ | Warstwy (mm) | U [W/(m²K)] | Reakcja na ogień |
|---|---|---:|---|
| Filar wieży | granit 40 na kotwach ze stali nierdzewnej (nieodpadające ≥ 60 min) / pustka wentylowana 40 / wełna mineralna λ 0,033 – 200 / ściana-słup żelbet 300 | 0,15 | A1 (całość NRO) |
| Płycina wieży (≤ 25 m od dziedzińca BIPV) | panel Al anodowany 3 lub BIPV szkło-szkło 10 / pustka 40 / wełna 200 / żelbet 200; pas międzykondygnacyjny EI 60 0,80 m | 0,15 | A1 / BIPV A2-s1,d0 tylko ≤ 25 m |
| Ściana skrzydła | ceramika ekstrudowana 40 / ruszt Al / pustka 40 / wełna 200 / żelbet 200 | 0,15 | A1 |
| Okno | rama Al z przekładką termiczną, pakiet 3-szybowy 54 mm, roleta ZIP w nadprożu, parapet zewn. Al, ościeże 600 (wieża) / 350 (skrzydło) z wyprawą granitową / ceramiczną | Uw ≤ 0,80 | – |
| Korona – łuk | lamela ceramiczna 250 × 600 na ruszcie stalowym / fasada słupowo-ryglowa 3-szybowa | Ucw ≤ 0,90 | A1 / szkło |
| Dach wieży i skrzydła | BIPV szkło-szkło (BROOF(t1)) / membrana / spadki / wełna mineralna 300 / paroizolacja / płyta | ≤ 0,12 | NRO |

Powyżej 25 m wszystkie okładziny, mocowania i izolacje są niepalne. Podokienniki mają ≥ 1,10 m lub szkło bezpieczne stałe (WT § 301). Brak balkonów.

---

## 9. Zagospodarowanie terenu

* **Plac Mostowy (skwer 9/2, 355 m², bez kubatury):**
  * posadzka z granitu strzegomskiego; **ślad pierzei z 1934 r.** pasem granitu z listwą z brązu i tablicą z planem kwartału; **szpaler 4 lip drobnolistnych** wzdłuż śladu w zach. części skweru (skwer nie jest drogą pożarową);
  * okrągła ława przy łuku („okrągły element” przedmościa 1934);
  * taras bistro w zach. części (17,9 m głębokości), 20 stojaków rowerowych dla gości.
* **Ogród Województwa (dziedziniec, 1 568 m² niezabudowanego obszaru):**
  * **nieogrodzony**, dostępny z trzech stron: Hala (oś z mostu), brama ogrodowa (Mazowiecka), pas 4,6 m od bulwaru;
  * zachowane ogródki (490,6 m²) i **wszystkie 29 drzew ogródków**;
  * trawnik, **ogród deszczowy 140 m²**, ławki i pergola przy murze kamienic, mały plac zabaw dla dzieci z sąsiednich kamienic, meble z drewna lokalnego;
  * ścieżki z cegły i gruzu z wykopu oraz z płyt na podbudowie przepuszczalnej.
* **Drzewa:**
  * w obszarze inwestycji 44 drzewa (46 punktów); **usuwamy 6**: D701, D702 (w obszarze A, nieuniknione; nr 1 i 2 wg M.06, nr 2 z hubiakiem) oraz D867, D868, D882, D897 (0,32–0,46 m od lica skrzydła, poza ogródkami); **zachowane 38 (86 %)**;
  * D703, D704, D886 (2,3–2,9 m od ściany −1): palisada sieczna, przesłona korzeniowa, cięcia koron przez arborystę, wygrodzenie korona + 1 m na czas budowy;
  * **18 nowych drzew**: 4 lipy na skwerze, 2 przy pasie od bulwaru, 6 w ogrodzie (klon polny, grab), 6 na Wybrzeżu po stronie rzeki (poza pasem roboczym drogi pożarowej).
* **Wejścia (8):**
  1. Brama Mostowa – główne, łuk;
  2. od skweru – podcień pn.;
  3. Wejście Obywatelskie – Wybrzeże;
  4. konferencyjne – dziób NW;
  5. ogrodowe – pd. elewacja wieży;
  6. rowerownia – od dziedzińca;
  7. brama ogrodowa – przejście publiczne;
  8. portal obsługi w segmencie (garaż, dostawy, trafo, odpady).
* **Dostawy:** samochody ≤ 2,20 m rampą na −1. Odbiór odpadów: pojemniki wystawiane dźwigiem T w dniu odbioru do punktu w segmencie, z drzwiami od Wybrzeża (bez postoju na jezdni dłuższego niż czas załadunku; Wyj. 6 odp. 25).
* **Zjazd do garażu:** wyłącznie z **Wybrzeża Słowackiego (6KDB/2)** przez segment. Brama 6,0 m (v −4,1…−10,1). Z 1KDG brak wjazdu, Mazowiecka bez wjazdów (zgodność z K-01/K-02: tunel i tramwaj).
* **Rowery:** 50 stanowisk w parterze z wjazdem od dziedzińca (przez pas od bulwaru lub bramę ogrodową) + 20 dla gości na skwerze + 10 przy bramie ogrodowej, w tym 4 dla rowerów cargo.
* **Drogi pożarowe:** dalszy pas jezdni Mazowieckiej (bliższa krawędź ok. 8,9–9,7 m od elewacji) i Wybrzeża Słowackiego (ok. 7,9–9,1 m od elewacji wieży, ok. 9 m od segmentu). Zabudowa pierzejowa, 100 % elewacji frontowej (rozp. MSWiA 2009 § 12 ust. 3). Między jezdnią a elewacjami nie ma drzew > 3 m. Plac manewrowy niepotrzebny (przejazd ulicami bez cofania).
* **Retencja 151 m³** (rozdz. 10). Nawierzchnie przepuszczalne 430 m².

---

## 10. Ekologia (liczby z `_bilans_energii.py`, wersja dla syntezy)

* **Budynek bezemisyjny** (EPBD 2024/1275, od 1.01.2028 dla budynków publicznych), bez spalania na działce. Agregat tylko awaryjny, na HVO.
* **Forma:** A/V ≈ 0,18 m⁻¹; elewacje 6 880 m² (0,49 m²/m² PC nadziemnej); WWR 38–40 %, szkło pełne tylko w koronie (262 m²); osłony ZIP na elewacjach E, S, W; ościeża 0,60 m w wieży. Przegrody: ściana U ≤ 0,15, dach ≤ 0,12, okna ≤ 0,80.
* **Ciepło i chłód:** gruntowe pompy ciepła, **75 sond × 99 m** (poza reżimem art. 86 PGiG), moc grzewcza ok. **430 kW**, chłód aktywny ok. 330 kW + free cooling. TABS, wentylacja wyporowa w salach, odzysk ciepła z serwerowni do c.w.u. Sieć ciepłownicza tylko jako rezerwa. Pole sond ma nadwyżkę ciepła 165 MWh/rok, którą bilansuje odzysk do c.w.u. i dry-cooler w okresach przejściowych (symulacja 25-letnia EED/EWS i TRT w projekcie – przeszczep K4).
* **Wentylacja:** 5 central piętrowych (25 m², strefa środkowa wieży, kond. 1–5; kond. 5 obsługuje też 6) + centrale parteru i Sejmiku na −1, rekuperacja ≥ 80 %, sterowanie CO₂. Czerpnia zbiorcza: żaluzje w płycinach elewacji pd. wieży na kond. 1 (u 2–12, od dziedzińca). Wyrzutnia zbiorcza: lamele w pasie nad komisjami w koronie od pd. (≈ 29 m wyżej). Wentylatory oddymiania korytarzy w szachtach trzonów A i B, wyrzut jw. Nic na dachu ani na elewacjach od ulic i bulwaru.
* **PV 412 kWp, 347 MWh/rok:** dach wieży 208 kWp (183 MWh), dach skrzydła 156 kWp (137 MWh), elewacje od dziedzińca 48 kWp (27 MWh). Magazyn energii 250 kWh.
* **Bilans:** zużycie EPB ≈ 297 MWh/rok (23,9 kWh/(m²·rok)), całkowite ≈ 646 MWh/rok; **PV pokrywa 117 % EPB i 54 % całości**. Resztę daje społeczność energetyczna OZE Województwa (EPBD art. 11 ust. 7).
* **EP ≈ 26 kWh/(m²·rok)** (bez PV 60) wobec EPmax 95 (WT 2002) i progu ZEB 85 (projekt WT). Emisje operacyjne EPB 6,3 kg CO₂/(m²·rok) (próg ZEB 31,4).
* **Woda:** woda szara (804 m³/rok) i deszczowa (848 m³/rok) pokrywają 100 % spłukiwania. Zużycie wody wodociągowej spada o **47 %** (1 600 m³/rok).
* **Retencja:** ψ śr. 0,67 → 0,62 (dachy BIPV są szczelne), Qdm(15 min, C = 10) 51 → 47 dm³/s przed retencją. Objętość opadu 60 min C = 10 z powierzchni zredukowanej: 70 m³. **Pojemność retencyjna 151 m³ daje zero odpływu do kanalizacji dla deszczu miarodajnego.** Przelew awaryjny działa dopiero przy przekroczeniu.
* **GWP ≤ 500 kg CO₂e/m² PC (A1–A5)**, LCA A–C od koncepcji. Sposoby: CEM III, stropy sprężone (−25 % betonu), ograniczone podziemie (−159 m²), kruszywo z gruzowych nasypów działki w betonach niekonstrukcyjnych i podbudowach (przeszczep K3), aluminium ≥ 75 % z recyklingu, granit lokalny (≈ 60 km), demontowalne panele ceramiczne (100 lat), stały moduł 1,35 i jednakowe pokoje (adaptowalność). Cel BREEAM Excellent.
* **Bioróżnorodność i mikroklimat:** ogród na pd. od budynku, 38 drzew zachowanych + 18 nowych, ogród deszczowy, 24 budki dla jerzyków, ochrona ptaków na szkle korony, pnącza na ścianie segmentu.
* **Mobilność:** 55 punktów ładowania EV (1/2), 80 miejsc rowerowych (50 + 30 dla gości), prysznice.

---

## 11. Dostępność (wyróżniki)

* **Wszystkie wejścia bez schodów i pochylni.** ±0,00 = 119,30, czyli poziom skweru i Wybrzeża (niwelacja chodnika ≤ 2 %). Dziedziniec przy drzwiach ogrodowych i rowerowni podniesiony do 119,25 i łagodnie (≤ 4 %) obniżony ku ogrodom, poza strefami korzeni. Brama ogrodowa w poziomie chodnika i ogrodu (spadek ≤ 2 %).
* **Oś Hali bez przeszkód** (szerokość ≥ 6 m). Ścieżki dotykowe od przystanków tramwajowych na przyczółku, od wejść i z garażu do informacji i dźwigów (przeszczep K4). Tyflomapy przy wejściach. Kontrast posadzek, ścian i drzwi. Niski blat informacji i kancelarii. Pętle indukcyjne: sala obrad, komisje, kluby, sale konferencyjne, kancelaria.
* **Komfortka 12 m²** (3,0 × 4,0 m) 14 m od wejścia głównego (WT § 85a). WC dostępne na każdej kondygnacji i w każdej strefie, w tym dla publiczności galerii (PHS.05c). **Pokój cichy** 16 m² przy Hali.
* **Sala obrad:**
  * prezydium i mównica na poziomie podłogi;
  * pochylnie ≤ 5 % do każdego rzędu, **stanowisko dla wózka w każdym rzędzie**;
  * 3 miejsca dla wózków na galerii (dostęp P1/P2 bez stopni) + 2 wśród gości;
  * tłumacz PJM w kadrze, napisy na żywo.
* **Dwa publiczne dźwigi** (redundancja), kabiny 1,4 × 2,4 m, sygnalizacja głosowa i wizualna.
* **Ewakuacja OzN:** MOE 0,9 × 1,4 m z krzesłem ewakuacyjnym i interkomem do ochrony i KDR na każdym podeście klatek A, B, C (poza szerokością biegu 1,60 m). Dźwig ewakuacyjny R (PN-EN 81-76). Sygnalizatory optyczne alarmu w WC i przestrzeniach ogólnodostępnych.
* **Garaż:** 6 miejsc dla OzN 3,6 × 5,0 m przy trzonach A i B na −1. Pokój matki z dzieckiem na kondygnacji Sejmiku, przewijaki w WC holu i konferencji. Ogród bez barier dla mieszkańców.

---

## 12. Bilanse (PN-ISO 9836) i koszt

| Wskaźnik | Wartość |
|---|---|
| Powierzchnia zabudowy (PZ) | **2 162,9 m²** (58,0 % obszaru 3 728,7 m²) |
| PBC | ≈ 1 170 m² (ogród 1 139 m² + 50 % donic tarasu) = 31 % |
| PC nadziemna | **14 151 m²** (P 2 003,1; kond. 1–4 po 2 160,2; kond. 5, 6, S po 1 145,8; antresola 69,7) |
| PC podziemna | **3 763 m²** (−1: 2 337,2; −2: 1 426,2) |
| PC razem | 17 914 m² |
| PU (bez RU i US) | ≈ **8 400 m²** (pokoje 4 570, KS 253, Sejmik 826, konferencje 410, strefa wejściowa 214, sale narad 360, socjalne 360, pomocnicze 692, WC 260, rowery 114, PPT 97, budki i strefy pracy wspólnej w strefach środkowych 240) |
| PC nadziemna / PU | 1,68 (program 1,71) |
| Kubatura brutto (KW) | ≈ **78 000 m³** (wieża 42 162; skrzydło 17 368; segment 3 490; −1 8 765; −2 z płytą 6 204) |
| Miejsca postojowe | **109** (−1: 68, −2: 41); wymagane 12/1 000 m² PU + 6/1 000 m² gastronomii = 99 (107, gdyby wliczyć hole) ✔ |
| Pokoje | 187 (179 × 24 + 8 × 32); pojemność elewacji 224 jedn. |
| MDS / budowla ochronna | MDS ≥ PU/15 = 560 os. w garażu −1/−2; −2 jako ukrycie z filtrowentylacją, 2 wyjścia (klatki A, B w odległości 20 m) + rampa; część MDS ≥ 20 m od bramy |

**Koszt realizacji (netto, ceny II kw. 2026) – metoda 1: model F.14.B `tools/koszty_model.py`, poziom mid.**
Parametry: A_nad 14 151; A_pod 3 763; obrys podziemia 2 337; obwód ścian szczelinowych 245 m × 18 m; wykop średnio 6,9 m; płyta 1,1 m; obrys parteru 2 163; wypór poza obrysem 175 m²; 3 klatki × 8,67 kond.; 6 dźwigów osobowych + 1 towarowy; ceramika i metal 2 100 m²; granit 1 810 m²; okna 2 180 m²; fasady słupowo-ryglowe 410 m²; BIPV elewacyjne 320 m²; lamele 450 m²; dachy 2 160 m² (intensywny 167); stal 70 t; PV dachowe 364 kWp; BESS 250 kWh; sondy 7 425 mb; teren 2 224 m² (kamień 1 050, zieleń 1 100); 18 drzew; 55 EV; ścianki mobilne 60 m².

| Grupa F.14.B | mln zł |
|---|---:|
| 1 Roboty przygotowawcze i ziemne (ściany szczelinowe, archeologia, monitoring sąsiadów) | 10,94 |
| 2 Przyłącza i sieci, GPC, PV | 9,14 |
| 3 Stan surowy | 22,06 |
| 4 Stolarka zewnętrzna i fasady słupowo-ryglowe | 5,72 |
| 5 Stolarka wewnętrzna | 1,95 |
| 6 Elewacje | 7,79 |
| 7 Instalacje sanitarne i HVAC | 20,74 |
| 8 Instalacje elektryczne | 12,33 |
| 9 Teletechnika i AV (głosowanie, transmisja, PJM) | 11,08 |
| 10 Dźwigi | 4,40 |
| 11 Wykończenie ścian, sala Sejmiku | 11,50 |
| 12 Sufity | 2,54 |
| 13 Posadzki | 4,44 |
| 14 Balustrady | 0,73 |
| 15 Zagospodarowanie terenu | 5,54 |
| 17 Woda szara | 0,70 |
| 18 MDS, zamurowanie okien Maz. 19 | 1,70 |
| 16 Koszty stałe budowy | 4,00 |
| 18.3 Rezerwa na nieprzewidziane 5 % | 6,87 |
| **Suma modelu (mid)** | **144,2** |
| Korekty poza modelem: budowla ochronna – filtrowentylacja, śluzy, wzmocnienia (+1,5); lapidarium i ekspozycja reliktów (+0,5) | +2,0 |
| **Koszt realizacji z rezerwą 5 %** | **146,2 mln zł netto** |
| Zapas do limitu 150 mln | 3,8 mln (2,5 %); bufor łącznie z rezerwą 10,7 mln (7,1 %) |

**Metoda 2 (kontrolna – wskaźnik rynkowy):** 146,2 mln / 17 914 m² PC = **8 161 zł/m² PC**, czyli w środku pasma porównywalnych budynków publicznych 7 400–9 300 zł/m² (`koszty_benchmarki.md`). Scenariusz low 105,6; high 201,0; waloryzacja +5 % (2027): 151,4 (opis ryzyka w części opisowej; F.14.B na poziomie cen II kw. 2026). Dźwignie rezerwowe (≈ 1,6 mln): ceramika w 2 zamiast 3 odcieniach (−0,2), uproszczenie lameli korony (−0,3), pas −2 pod dziedzińcem 7 → 4 m (−0,7; −3 m.p.), lżejszy ruszt dachu S z drewna klejonego (≈ 0; −CO₂), mniejsza powierzchnia granitu w cokole skrzydła (−0,4). Koszt Dokumentacji ≈ 7,6 mln zł netto (≤ 5,4 % = 8,1 mln), liczony osobno.

---

## 13. § 13 i § 60 WT wobec Wybrzeża Słowackiego 5 i Mazowieckiej 19 (dowody liczbowe)

**Dane:** szczyt pn. WS 5 (101,93; 28,52)–(118,16; 29,46), normalna 356,7°. Grubość muru 0,55 m: wierzchołek kąta leży w licu wewnętrznym na osi okna. Sektor 60° symetryczny (±30°). Okno pokoju nr 3 lok. 6/6A: (110,5; 29,0), parapet ≈ 124,0. Wariant najostrożniejszy: okno w dowolnym miejscu szczytu (e 102,4–117,7), a H liczone od najniżej położonych okien budynku (≈ 120,0, parter frontowy; § 13 ust. 2 literalnie). Zabudowa śródmiejska: odległości ½ (§ 13 ust. 4).

| Przeszkoda | Najwyższa krawędź | Wariant | H | Wymagane | Najmniejsza odległość w sektorze | **Zapas** |
|---|---|---|---:|---:|---:|---:|
| Segment SE (ściana pd. pełna) | attyka 140,15 | najostrożniejszy (okno w dowolnym miejscu, H od 120,0) | 20,15 | 10,08 | 11,13 (wierzchołek (116,69; 28,82)) | **1,05 m** ✔ |
| Segment SE | 140,15 | okno pokoju lok. 6/6A, H od parapetu 124,0 | 16,15 | 8,08 | 11,15 | **3,07 m** ✔ |
| Segment SE | 140,15 | okno pokoju, H od 120,0 | 20,15 | 10,08 | 11,15 | **1,07 m** ✔ |
| Wieża (> 35 m) | attyka 156,50 | dowolne okno szczytu | – | 17,50 | 18,99 (wierzchołek (102,46; 28,00)) | **1,49 m** ✔ |
| Wieża | 156,50 | okno pokoju lok. 6/6A | – | 17,50 | 20,46 | **2,96 m** ✔ |
| Skrzydło | 140,15 | – | – | – | poza sektorem | ✔ |

* **§ 12:** ściana pd. segmentu bez otworów stoi 4,58 m od granicy dz. 10/2 (≥ 3 m).
* **§ 271:** 10,58 m od ściany z oknami (≥ 8 m).
* Prywatność: biura nie mają okien na szczyt. Okna szczytu WS 5 pozostają czynne (zakaz zamurowania, Wyj. 3 odp. 13).

**§ 60 (1,5 h w każdym dniu równonocy, 7–17 czasu urzędowego):**
* **Lokal 6/6A** jest dwustronny. Pokoje 1 (25,0 m²) i 2 (15,0 m²) od wsch. mają słońce 7:00–12:00 (20.03, 5,0 h) i 7:00–12:45 (23.09, 5,75 h). Nasz budynek leży względem nich w sektorze 340–40°, poza drogą słońca (≈ 92–259°), więc ich nie zacienia. Okno szczytu (normalna 356,7°) nie dostaje słońca w równonoc niezależnie od projektu, dlatego rozstrzyga dla niego § 13 (spełniony).
* **Pokój 4 lokalu i elewacje podwórzowe WS 5–6** (zach.): skrzydło leży w azymucie ≈ 257–270°. Zacienia je dopiero od ok. 16:40 (20.03, CET) i 16:45 (23.09, CEST), przy wysokości słońca < 10°. Słońce od ok. 12:00 do 16:40 daje ≥ 4,5 h. Pas 12 m przed elewacjami podwórzowymi pozostaje niezabudowany.
* **Mazowiecka 19:** nasz budynek leży na pn., więc fronty (zach.) i podwórze (wsch.) zachowują pełne nasłonecznienie. Skrzydło przylega do ślepego szczytu (okna łazienek do zamurowania przez Zamawiającego, Wyj. 3 odp. 13; pomieszczenia nieprzeznaczone na pobyt ludzi). Attyka 140,15 ≤ 140,24, więc § 218 nie ogranicza. Ściana oddzielenia REI 120 bez otworów.
* **Cienie w równonoc 7–17:** cień wieży mieści się w sektorze WNW–N–ENE (pl. Społeczny, przyczółek, Odra) i nie sięga zabudowy mieszkaniowej kwartału. Na planszy zagospodarowania 1:500 cienie z SW pod 45° (wymóg Etapu I).

---

## 14. Kadry wizualizacji (8 obowiązkowych + 4 dodatkowe)

z = wysokość względem ±0,00 (119,30). Kamery ludzkie są poziome (perspektywa dwupunktowa, shift_y). Wszystkie widoki zewnętrzne pokazują późny październik (rodzina obrazów jak F.17). Poza granicą opracowania na F.17 stan obecny, bez hełmów (Wyj. 9 odp. 61). Hełmy pojawiają się tylko w W3 (perspektywa z mostem, Wyj. 7 odp. 29; M.11.F).

| # | Kadr | Kamera (e; n; z) | Cel (e; n; z) | Ogniskowa (36 mm) | Pora | Nastrój / co musi być w kadrze |
|---|---|---|---|---|---|---|
| **W1** | Lot ptaka od wsch. **na F.17.A** | (356,815; 20,455; 84,62) – H 203,922; yaw 287,808°, pitch −12,053°, roll −0,652° | wieża | 17,248 mm, shift_x −0,0124, shift_y −0,0115, 8 470 × 4 475 | 29.10.2025 11:38 CET (słońce 180,7°/25,3°) | łuk z koroną i lamelami nad przyczółkiem, pierzeja Wybrzeża z segmentem i WS 5, ogród, dachy BIPV za attyką (z góry); render tylko w granicy, cienie przez shadow catcher (`kamery_F17.json`) |
| **W2** | Lot ptaka od zach. **na F.17.B** | (−42,839; −26,435; 46,89) – H 166,193; yaw 56,523°, pitch −12,103° | pierzeja Mazowieckiej | 17,524 mm, shift_x −0,0564, shift_y −0,0236, 7 962 × 4 505 | 29.10.2025 11:57 CET (185,8°/25,1°) | 4 posesje w osiach 2,025 m od Maz. 19 do dziobu NW, brama ogrodowa, wieża w tle, pl. Społeczny |
| **W3** | **Brama Mostowa z poziomu człowieka, z mostem** | (125,0; 60,5; 1,69) chodnik nadrzeczny Wybrzeża | (101,5; 93,0; 10,0), az. 324° | 24 mm, shift_y +0,20 | 23.10 09:40 CEST (≈ 142°/19°) | chłodny złoty poranek; podcień z ciepłym światłem, napis w nadprożu, piesi z mostu, portal z odtworzonymi hełmami w tle, lamele korony u góry kadru; osoba na wózku wjeżdżająca samodzielnie |
| **W4** | **Powiązanie z WS 5** | (130,0; 21,0; 1,56) | (107,0; 41,0; 9,0), az. 311° | 28 mm, shift_y +0,15 | 23.10 11:15 CEST | codzienność bulwaru; relief ściany segmentu w słońcu, czynne okna szczytu WS 5 w cieniu, pas 4,6 m z ławą i drzewem jako wejście do ogrodu, wieża w tle |
| **W5** | **Powiązanie z Maz. 19** | (36,5; 0,0; 0,68) chodnik zach. Mazowieckiej | (56,0; 26,0; 9,0), az. 37° | 28 mm, shift_y +0,18 | 22.10 15:30 CEST | światło skośne z SW; gzyms i kordon w liniach nr 19, przęsło przejściowe, brama ogrodowa z widokiem na drzewa |
| **W6** | **Hala Obywatelska** | (100,236; 68,619; 1,60) przy drzwiach w łuku | (84,321; 43,124; 1,80), az. 212° | 20 mm | 23.10 11:00 CEST | oś na wylot do ogrodu (drzewa na końcu), kancelaria z niskim blatem, lapidarium, granitowa posadzka ze śladem murów, tyflomapa |
| **W7** | **Hol sali Sejmiku** | (82,097; 64,918; 28,90) przy dźwigach A | (69,432; 68,315; 30,50), az. 285° | 20 mm, shift_y +0,05 | 29.10 16:20 CET | początek błękitnej godziny; dwukondygnacyjny narożnik NW, okna na pl. Społeczny i wieże katedry, lada baru, wejście do sali, ludzie w rozmowie |
| **W8** | **Sala Sejmiku z galerią publiczności i jej oddzielnym wejściem** | (98,661; 72,970; 29,00) za 3. rzędem | (100,188; 60,373; 30,90), az. 173° | 20 mm, shift_y +0,08 | 22.10 10:30 CEST, sesja | prezydium przy pełnej ścianie z godłem, oświetlone dziennym światłem z łuku za kamerą; 44 stanowiska; galeria z publicznością i widocznymi drzwiami z foyer (P1/P2); tłumacz PJM w kadrze; stanowisko radnego na wózku |
| W9 | Latarnia wieczorem z mostu (dod.) | (126,0; 152,0; 3,90) chodnik mostu | (96,0; 62,0; 26,0), az. 198° | 50 mm | 29.10 17:05 CET, sesja | błękitna godzina; korona świeci zza lamel, pierzeja spokojna, gzyms poniżej hełmów |
| W10 | Ogród Województwa (dod.) | (78,0; 17,0; 1,16) | (88,0; 45,0; 10,0), az. 20° | 24 mm, shift_y +0,12 | 22.10 13:30 CEST | mieszkańcy i pracownicy, drzewa ogródków, ogród deszczowy, wejście ogrodowe na końcu osi |
| W11 | Taras nad Oławą (dod.) | (101,169; 41,570; 21,40) | (117,0; 73,7; 20,0), az. 26° | 24 mm | 22.10 14:30 CEST | przerwa pracowników, Oława, most, Ostrów Tumski |
| W12 | Aksonometria „kwartał 1934 / projekt” (dod.) | rzut aksonometryczny od SE | – | – | dzień, światło rozproszone | dawna linia pierzei na skwerze, łuk 1934 vs łuk projektu, posesje |

---

## 15. Narracja 8 plansz i część opisowa

**Hierarchia:** 1) idea Bramy i Latarni; 2) kwartał domknięty w skali kamienic; 3) Sejmik bezbłędny prawnie i dostępny; 4) liczby (koszt, ZEB, § 13).

| Plansza | Zawartość | Dominanta |
|---|---|---|
| **P1** | Hasło + idea (≤ 60 słów), **W1 (F.17.A)** na 60 % planszy, zagospodarowanie 1:500 z cieniami SW 45°, schemat „1934 / projekt” | W1 |
| **P2** | **W3** (Brama Mostowa z mostem), **W2 (F.17.B)**, aksonometria funkcji (Brama → oś → ogród; Latarnia), schemat ruchu radni / publiczność / dostawy | W3 |
| **P3** | Rzut parteru 1:200 z otoczeniem i ogrodem, rzuty −1 i −2 1:200 (garaż, ukrycie, technika), dostępność: legenda | rzut P |
| **P4** | Rzuty kond. 1 (charakterystyczna, z analizą § 13 na rzucie) i 2–4 1:200, moduł 1,35 / pokój 24,1 m², tabela departamentów | rzut 1 |
| **P5** | Rzuty kond. 5, 6, **S z antresolą** 1:200, tabela pomieszczeń Sejmiku (rozdz. 7.1) i dowód „całość w A”, rzut dachu (BIPV) | rzut S |
| **P6** | Przekroje A-A (pn.–pd. przez łuk i segment z WS 5) i B-B (wsch.–zach. przez salę i skrzydło) 1:200 z ZWG i stropem glin; analiza przesłaniania i nasłonecznienia (§ 13 – tabela rozdz. 13); schemat ppoż. i dostępności | przekroje |
| **P7** | Elewacje 1:200: Mazowiecka z Maz. 19, Wybrzeże z WS 5, pn. od skweru, pd. od ogrodu; przekrój elewacyjny + fragment 1:50 (wieża i skrzydło); **W4, W5** | elewacja Mazowiecka |
| **P8** | **W6, W7, W8** (wnętrza), schemat proekologiczny (GPC, BIPV 412 kWp, woda, retencja 151 m³, GWP), pasek KPI | W8 |

**Część opisowa (5 × A3, ≥ 11 pkt) – punkty:**
1. **Idea:** Brama Mostowa i Latarnia Sejmiku; pamięć narożnika 1934; wrocławski modernizm; ciągłość z Etapem I.
2. **Urbanistyka:**
   * dwie pierzeje domknięte;
   * gzyms 140,15 = Maz. 19;
   * jedna dominanta 37,6 m w dolnym zakresie A;
   * ogród dostępny z trzech stron;
   * brak wjazdów z 1KDG i Mazowieckiej.
3. **Architektura:** porządek kamieniczny (2,025 m) i wielki porządek wieży (2,70 m) na jednym module 1,35; 2 materiały + metal; łuk jako jedyne pasma; lamele zamiast tafli szkła.
4. **Funkcja:**
   * hala na wylot;
   * Wejście Obywatelskie;
   * dwa trzony;
   * 187 pokoi;
   * sale narad i magazynki przy elewacji;
   * departamenty na jednej kondygnacji;
   * KS pod Sejmikiem.
5. **Sejmik:**
   * cały program zamknięty na poziomie sali;
   * antresola otwarta;
   * prezydium przy pełnej ścianie;
   * pochylnie ≤ 5 %;
   * publiczność z osobnym wejściem.
6. **Dostępność:** wyróżniki z rozdz. 11.
7. **Konstrukcja i grunt:** ściany szczelinowe do glin, biała wanna, płyta palowo-fundamentowa, stropy sprężone 14,2 m, brak odwodnienia regionalnego.
8. **Ppoż.:**
   * budynek W, klasa B;
   * strefy ≤ 2 500 m²;
   * 3 klatki z przedsionkami i nadciśnieniem;
   * dźwig R;
   * tryskacze, SSP, DSO, oddymianie korytarzy;
   * drogi pożarowe z ulic;
   * elewacje > 25 m niepalne.
9. **Ekologia:** EP 26, PV 412 kWp (bez podwójnego liczenia), GPC 75 × 99 m, woda −47 %, retencja 151 m³, GWP ≤ 500, zieleń.
10. **Zagospodarowanie:** Plac Mostowy ze śladem 1934 i lipami, Ogród Województwa, 38/44 drzew, 18 nowych.
11. **Prawo:** MPZP (tabela rozdz. 4.3), § 13 / § 60 (rozdz. 13), WT 2002 + projekt WT, budowla ochronna (art. 93).
12. **Koszt:** F.14.B 146,2 mln (rezerwa 5 % w środku), metoda kontrolna, dźwignie, koszt Dokumentacji ≈ 7,6 mln.

---

## 16. Ryzyka resztkowe

1. **Linia A z rastra 1:1000 (±0,3 m).** Lica wieży leżą na liniach A, a skrzydła i segmentu 5–8 cm poza nimi. Potrzebny pomiar geodezyjny, korekta lic bez zmiany układu.
2. **Wykładnia antresoli** jest bezpieczna: brak pomieszczeń zamkniętych, 6 % rzutu.
3. **§ 13 dla własnych pokoi w narożach wklęsłych** opiera się na sektorze obróconym (praktyka WT 2002, projekt WT § 12). Do potwierdzenia przy uzgodnieniach. Alternatywnie zamiana 3 pokoi na pomieszczenia pomocnicze (rezerwa elewacyjna 3,2 jedn.).
4. **BIPV jako pokrycie** wobec MPZP § 6 pkt 13 (K-05) wymaga zgodnej interpretacji organu.
5. **Budżet:** bufor 7,1 %, waloryzacja do 2027 r. +5 % (opis w części opisowej). Dźwignie rezerwowe ≈ 1,6 mln.
6. **Woda gruntowa i archeologia** (relikty piwnic) wpływają na harmonogram podziemia.
7. **Budowla ochronna:** kategoria i pojemność zależą od postanowienia Prezydenta Miasta (art. 95a).
8. **Okna szczytu WS 5 na piętrach 2–4:** przyjęto wariant najostrożniejszy, pomiar przy wizji.
9. **Przebudowa przyczółka** (tramwaj, tunel; K-01, K-02): wibroizolacja sali obrad, izolacyjność elewacji pn. i zach.
