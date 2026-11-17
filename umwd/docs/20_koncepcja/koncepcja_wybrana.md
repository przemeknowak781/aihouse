# Koncepcja wybrana – „BRAMA I LATARNIA” (synteza panelu: K5 + przeszczepy)

**Siedziba UMWD i Sejmiku Województwa Dolnośląskiego, Wrocław, Mazowiecka / Wybrzeże J. Słowackiego, przy przyczółku Mostu Grunwaldzkiego**
**Wersja 1.2 (S-3) · 17.11.2026** – scalenie kondygnacji Sejmiku S-3 „hol z galerią” (`kondygnacja_S2.md`, skrypty `_s2_*.py`; rozdz. 7), poprawka I5 trzonów A, B, C (`_v12_trzony.py`), PU, parking i koszt (`_v12_koszt.py`), zapis JSON z walidacją (`_v12_scalenie.py`); rejestr: `rejestr_poprawek_v1_1.md`, sekcja „v1.2 – scalenie S-3”. Wersja 1.1 (po weryfikacji) – poprawki wg `weryfikacja_geometria.md`, `weryfikacja_koszt_eko.md`, `weryfikacja_program.md` i uwag koordynatora (skrypty `_rewizja_*.py`). Wersja 1.0 · podstawa: werdykt panelu (`panel/werdykt_panelu.md`: K5 – 5/5 pierwszych miejsc, średnia 42,8 pkt, Borda 20/20).
Geometria z `model/site.json` (układ lokalny e, n; H w PL-EVRF2007-NH). Liczby geometryczne v1.1 policzono w shapely skryptami `docs/20_koncepcja/_rewizja_*.py` (wspólne dane: `_rewizja_wspolne.py`). Dane maszynowe: `model/koncepcja.json` (meta.wersja „1.2 (S-3)”).
**±0,00 = 119,30 m n.p.m.** (posadzka parteru; skwer 9/2 119,30–119,49, Wybrzeże 119,16–119,26).
Zgodnie z decyzją Inwestora nie korzystano z żadnych informacji o rzeczywistych pracach ani wynikach tego konkursu.

Spis: 1 idea · 2 słabości i ich usunięcie · 3 przeszczepy i sprzeczności · 4 bryły · 5 konstrukcja · 6 kondygnacje · 7 kondygnacja Sejmiku · 8 elewacje · 9 zagospodarowanie · 10 ekologia · 11 dostępność · 12 bilanse i koszt · 13 § 13 / § 60 · 14 kadry wizualizacji · 15 plansze i opis · 16 ryzyka resztkowe.

---

## 1. Nazwa, hasło, idea

**Nazwa:** BRAMA I LATARNIA.

**Hasło:** *Z mostu przez bramę do ogrodu kwartału – a nad bramą Sejmik obraduje pod okiem obywateli, na tle Odry i Ostrowa Tumskiego.*

**Idea (125 słów).** Kwartał przy Kaiserbrücke kończył się w 1934 r. zaokrąglonym narożnikiem. Przywracamy go w języku wrocławskiego modernizmu (Mendelsohn, Poelzig, Scharoun). Ten jeden narożnik pełni dwie role obywatelskie. W parterze jest **Bramą Mostową**: łukowym podcieniem, z którego prosta, przekątna oś Hali Obywatelskiej prowadzi wzrok i krok z mostu do publicznego, nieogrodzonego ogrodu kwartału z zachowanymi drzewami ogródków. Na szczycie jest **Latarnią Sejmiku**. Prezydium obraduje przy pełnej ścianie z godłem. Radni siedzą przed panoramą Odry, mostu i katedry, a obywatel z galerii widzi swój Sejmik na tle miasta. Wieczorem miasto widzi salę przez kamienne lamele. Reszta budynku milknie. Pierzeja Mazowieckiej to cztery „posesje” w skali kamienic z gzymsem w linii Mazowieckiej 19. Wieża ma wielki porządek granitowych filarów. Materiały są trzy: jasny granit, kremowa ceramika i ciemny metal.

---

## 2. Słabości wskazane przez sędziów – jak zostały usunięte

| # | Słabość K5 (sędziowie) | Rozwiązanie w syntezie (liczby) |
|---|---|---|
| 1 | Prezydium przed panoramą 33 × 10,2 m, przeciwświatło (J1, J2, J4) | Sala odwrócona (przeszczep K3). **Prezydium i mównica przy pełnej ścianie pd.**, godło z brązu na tej ścianie nad prezydium. Panorama jest **za plecami radnych** (najmniejszy kąt kierunek patrzenia – szkło 51,1°) i oświetla prezydium od przodu światłem z pn./pn.-wsch. Kamery na prezydium mają tło pełne. Ujęcia radnych pod okno łagodzą lamele 0,60 m, rolety screen 5 % i światło TV ≥ 800 lx w pionie. |
| 2 | Bilans poziomu Sejmiku się nie zamyka; brak korytarza (J1, J2, J4) | Rzut S-3 rozpisany w shapely (rozdz. 7). Wnętrze 1 080,2 m² = pomieszczenia (z salą, holem i szatnią) 789,8 + komunikacja 123,7 (kuluar 83,8) + trzony 123,6 + ściany wewn. 43,1 (+ ściany zewn. 65,6 do PC 1 145,8). **Kuluar 2,20 × 39,0 m** (przy trzonie A 1,75 m; przeszczep K4) łączy obie klatki, salę (drzwi SW, SE i prezydium) i wszystkie komisje i kluby. Sala 232,0 + galeria 65,3 = 297,3 m² (zakres 280–380), hol 74,8 + 89,6 = 164,4 m² wolnej podłogi (program 150) + szatnia 12,5 + bar 32,0; program +88,2 m² nad sumą minimów. |
| 3 | Pomost techniczny 6,6 m z 4 centralami = kondygnacja techniczna (J1, J2, J5) | Pomost usunięty. Centrale piętrowe 25 m² w strefie środkowej wieży (kond. 1–5; kond. 5 obsługuje także 6). Centrale parteru i Sejmiku na −1. Nad komisjami jest tylko przestrzeń sufitowa ≤ 1,95 m bez podłogi i bez urządzeń, czyli nie jest to kondygnacja (WT § 3 pkt 16). |
| 4 | Kondygnacja Sejmiku 12 m – nadmiar kubatury (J2, J3, J4, J5) | **P+6+S** w tej samej bryle zewnętrznej. Sejmik ma **8,90 m** (sala 6,85 m w świetle, antresola +3,60 m). Dodatkowa kondygnacja biurowa (+1 145,8 m² PC) mieści w całości sale narad i magazynki przy elewacji (poz. 8, 18). Wieża ma 37,6 m (K5: 36,8 m). Dach podniesiono o 0,65 m wyłącznie dla zapasu MPZP 1,06 m. |
| 5 | ≈ 650 m² pełnego szkła w koronie (J1, J3, J4, J5) | Przeszklenia korony **262 m²** (−60 %). Na łuku pionowe lamele ceramiczne **0,35 × 0,60 m (R 13,40–14,00) w rozstawach 1,35 / 0,675 m ułożonych w ciągu Fibonacciego** – bez regularnego rytmu, ton w ton ze szkłem (lamela S 4005-Y20R, sitodruk 30 %, ΔL* ≈ 8); przesłonięcie 32 % w osi, 100 % od **59°** (v1.0 podawała błędnie 34°; `_rewizja_elewacje.py`). Okno holu pn. podzielone filarami 1,05 m (kwatery 1,65 × 5,0 m). Szkło g = 0,27, R ≤ 12 %. Nocą korona świeci tylko światłem wnętrza podczas sesji (≤ 5 lx na elewacji, WT § 293). |
| 6 | Wstęgi w pierzei Mazowieckiej, słabe „posesje” (J1, J2, J3, J4) | Porządek pionowy (przeszczep K1). Oś okien **2,025 m** (kamienica: ≈ 2,2 m), okna **1,20 × 2,35 m** nad parapetem 0,60 m z kwaterą stałą do 0,90 m (nadproże 2,95 m mieści kasetę ZIP pod stropem), WWR 37 %. Cztery „posesje” 12,15 / 16,20 / 16,20 / 12,15 m różnią się odcieniem ceramiki i reliefem wypełnień cofniętych za lico filarów o 0 / 0,08 / 0,15 / 0,08 m (lico filarów = obrys). Pasma poziome zostały tylko na łuku narożnika. |
| 7 | Ślepa ściana pd. segmentu SE (J1, J3, J4, J5) | Relief ceramiczny w osiach 2,025 m (pilastry płytkie 0,12 m, fugi z ciemnego metalu) w rysunku elewacji frontowej + pnącza na linkach (7 sadzonek winobluszczu w pasie 4,6 m od granicy dz. 10/2). W v1.1 ściana pd. powyżej parteru jest okładziną **BIPV satynowaną w tonie ceramiki** (295 m², 41 kWp) w tym samym rysunku osi 2,025 m; pnącza w strefie parteru. Nad nią **taras nad Oławą** (135 m² w attyce, w tym ≈ 92 m² użytkowych) z attyką obniżoną do 139,10 i balustradą szklaną cofniętą 1,5 m. |
| 8 | 3 z 6 sal narad bez okien (wszyscy) | **6/6 sal narad przy elewacji** (P: brak; kond. 1, 2, 3 ×2, 4 ×2 – v1.1: sala z kond. 5 na kond. 4). Format głęboki 7,60 × 7,90 m = 60 m² w pierścieniu wieży. |
| 9 | Brama ogrodowa 2,7 m (J1) | **4,05 m** (3 moduły) × 15,0 × wys. 4,80 m, w poziomie chodnika (118,70 → 118,90), granitowy portal na styku posesji M1/M2. |
| 10 | Zapas dachu wieży 0,41 m (J1, J5) | Najniższy punkt pokrycia **155,50 m n.p.m.** = 36,06 m nad najwyższym terenem w A (119,44). Zapas **1,06 m**. Attyka 156,50 (37,62 m nad 118,88). |
| 11 | Obie klatki w jednym trzonie (J2) | **Dwa trzony** (środki klatek 19,8 m; v1.2 – klatki wg I5: A 3,40 × 5,80 m, B 3,40 × 6,64 m, obie do antresoli +30,90). A (radni, pracownicy, dźwig ratowniczy) w środku-zachodzie, B (publiczność) przy pd.; dostawy – dźwig T w segmencie. MDS: ukrycie na −2 (≤ 300 os.) z klatkami A i B (pomiar „≥ 15 m” – rozdz. 16), MDS na −1 (260 os.) z klatką C, rampą i szybem wyjścia zapasowego. |
| 12 | Podnośnik na rzędy (J2, J4, J5) | 4 rzędy na +0,00 / +0,09 / +0,18 / +0,27 m – przewyższenie 0,09 m na rozstawie 1,80 m = **5,0 %**, więc oba przejścia są **pochylniami ≤ 5 %** bez spoczników. **Stanowisko dla wózka w każdym rzędzie** (4; przeszczep K4) + 3 na galerii. 47 stałych stanowisk (wymagane 44). |
| 13 | Dostawy po dz. 10/2, rampa 20 % (J2) | **Jeden punkt obsługi w segmencie SE** od Wybrzeża (przeszczep K4). Dostawy samochodami ≤ 2,20 m rampą na −1, dalej korytarzem obsługi do dźwigu T 2 t w narożniku SE segmentu. Dz. 10/2 nie jest używana przez nasz ruch. Rampa **jednopasowa 3,50 m ≤ 18 %** z przejściami 9 % i sygnalizacją wahadłową, wzdłuż ściany pn. segmentu; w segmencie ok. 19 m, ogon (u 14,8–21,0) pod dziedzińcem, cały strop poniżej terenu. |
| 14 | Brama garażu 9–11 m od WS 5, hałas (J3) | Brama **4,0 m** w elewacji wsch. segmentu (v −0,40…−4,40), **17,4 m od okna lok. 6/6A** (do krawędzi bramy), zwrócona na wsch. (okno patrzy na pn.). Zasłania ją bryła segmentu. Rampa obudowana, ściany chłonne, cicha brama rolowana. |
| 15 | Pasaż w kształcie L (J3) | **Prosta oś przekątna** (azymut 211,7°, 33,4 m + podcień 3 m) od drzwi w łuku (101,86; 71,57) do drzwi ogrodowych (84,32; 43,12). Z progu widać drzewa ogródków (D795, D797). W najwęższym miejscu (między blokiem WC a trzonem B) ma 6,3 m (przeszczep K3). |
| 16 | Ażurowa brama 2,5 m na dz. 10/2 (J3) | Usunięta. Nic nie stoi na dz. 10/2. Pas 4,6 m w obszarze inwestycji między segmentem a dz. 10/2 to otwarte wejście do ogrodu od bulwaru (ława granitowa, 2 drzewa, bez furty). |
| 17 | Rezerwa budżetowa 2,3 % (J3) | Koszt v1.2 **148,98 mln zł netto** (mid, II kw. 2026, ilości weryfikatora z ościeżami, palami i uskokiem, garaż 110 m.p., antresola S-3 297,9 m²) z **rezerwą 5 % (7,09 mln) w środku** (wymóg ≥ 4 %) i zapasem 1,02 mln do limitu (rozdz. 12). |
| 18 | Magazynki „zamienne na biura” w środku (J4) | **20/20 magazynków przy elewacji** (typ standardowy 4,05 × 6,10 m lub głęboki 2,60 × 9,25 m dobierany do miejsca – v1.1 wg modelu pomieszczeń: 12 standardowych + 8 głębokich). Każdy ma okno ≥ 3,0 m² i 3 punkty. |
| 19 | Naroże segmentu 2,96 m od dz. 10/2 (J4) | Ściana pd. segmentu **4,58 m** od granicy dz. 10/2 (≥ 3,0 m wg WT § 12 ust. 1). |
| 20 | PV zawyżone (biosolar + zieleń na tych samych m²) (J5) | **BIPV jako pokrycie** za attyką (pola netto po attyce, pasie przy attyce, wyłazach, wpustach i przerwie): wieża 948 m² = 204 kWp, skrzydło 685 m² = 147 kWp (0,215 kWp/m², η ≥ 22,5 %; cień wieży na dachu skrzydła −11,6 % uzysku). Dachy dają 351 kWp < 400, więc dochodzą pola ≤ 25 m od dziedzińca i od dz. 10/2: płyciny wieży 82 m² = 11 kWp, **ściana pd. segmentu 295 m² = 41 kWp**, **zadaszenie tarasu ogrodowego** przy elewacji pd. wieży 80 m² = 13 kWp. **Razem 415 kWp** (≥ 0,4 MWp M.12; `_rewizja_pv_ep.py`). Dach zielony tylko na tarasie segmentu (135 m², osobno). Bez stelaży. |
| 21 | Brak celu GWP (J5) | **GWP ≤ 500 kg CO₂e/m² PC (A1–A5)**, LCA wg PN-EN 15978 i Level(s) od koncepcji, raport A–C wg EPBD art. 7 ust. 2 (przeszczep K1). |
| 22 | Retencja tylko redukuje odpływ (J5) | **Retencja 157 m³** (skrzynki rozsączające 66 m³ w pasie 4,6 m pd. od segmentu, dno ≥ 117,45 + rezerwa zbiornika deszczówki 20 + ogród deszczowy 42 + dach niebieski tarasu 10 + podbudowa nawierzchni 19). To 2,2 × objętość opadu 60 min C = 10 (70 m³), czyli zero odpływu do kanalizacji dla deszczu miarodajnego – pod warunkiem k ≥ 1·10⁻⁶ m/s (badanie przed PB; inaczej odpływ dławiony ≤ 2 dm³/s). |
| 23 | Jeden dźwig publiczny (J5) | **P1 i P2** 1 600 kg, kabiny 1,5 × 2,1 m (M.13), z lobby Wejścia Obywatelskiego wprost na antresolę (przeszczep K3). |
| 24 | 22 punkty EV (J5) | **55 punktów** (1 na 2 miejsca, EPBD art. 14), okablowanie 100 %. |
| 25 | § 13 segmentu – zapas 0,40 / 0,93 m (J5) | Ściana pd. równoległa do szczytu WS 5, 10,58 m od jego lica, z attyką obniżoną do poziomu tarasu 139,10. Wariant najostrożniejszy (okno w dowolnym miejscu szczytu, wierzchołek w licu wewn., H od najniższych okien 120,0): zapas **1,58 m** (balustrada cofnięta 1,5 m: 2,53 m). Okno pokoju lok. 6/6A: **3,58 m**. Wieża: **1,50 m** (wymagane 17,5 m). |
| 26 | Podziemie 3 922 m² (J5) | v1.2: wymaganie MPZP § 13 przy PU 8 871 m² (po S-3) to **106 m.p.** (ostrożnie 108), a 109 m.p. z v1.0 nie mieściło się w obrysie (model pomieszczeń: 41). **−1 (2 264 m²) i −2 (2 101 m²: wieża, segment, pas 5 m, skrzydło bez M1)**, −1 podwyższona do 4,20 m; **110 m.p.** = 78 stanowisk na posadzce + 32 w stackerach zależnych na −1 (pracownicy), w tym 6 OzN (`_rewizja_parking.py`). Podziemie 4 365 m². Technika krytyczna nad terenem, tryskacze nieprojektowane (nieobowiązkowe). |

**Korekty własne (błędy K5, których sędziowie nie wskazali):**
(a) Pilastry K5 wystawały ok. 0,30 m poza granicę obszaru (ściana 0,25 m od granicy + pilaster 0,55 m), co narusza Wyj. 7 odp. 28. Teraz **lico zewnętrzne = lico filarów** (0,25 m od granicy), a okna są cofnięte o 0,45 m (ościeża z blachy Al). v1.1: na wszystkich licach < 0,30 m od granicy gzyms-attyka **bez wysięgu** (fryz wklęsły 0,15 m), relief jako cofnięcie wypełnień.
(b) Styk skrzydła z wieżą leżał na linii u = 0, czyli do 0,46 m² skrzydła w A. Teraz lico skrzydła jest na u = −0,05…−0,08 (szczelina 4–5 cm), w A jest 0,00 m². Obróbka styku to pionowa listwa na licu wieży (element elewacji wieży); pokrycia skrzydła i tarasu kończą się na u ≤ −0,05 / v ≤ −0,05.
(c) W ogródkach w obszarze inwestycji rośnie **29** drzew, a nie 33 (`site.json`, weryfikacja).
(d) Rozdzielnia, UPS, BESS i serwerownia leżały w K5 na −1 (poniżej poziomu sytuacji wyjątkowej 119,0). Teraz są nad terenem: trafo, rozdzielnia i BESS w segmencie (P, 119,30 + cokoły), serwerownia i UPS na kondygnacji 1, **agregat HVO na kond. 1 segmentu (124,10)**; pompowni tryskaczowej nie ma (tryskacze nieobowiązkowe).
(e) Sala 200 os. była pod belkami transferowymi 14,2 m (jak w K1). Teraz stropy skrzydła są sprężone, o rozpiętości 14,2 m bez słupów pośrednich, i sala ma **4,25 m w świetle** bez belek.
(f) Dach rampy wystawał nad teren dziedzińca. v1.1: próg bramy 119,10 (= chodnik) z samoczynną zaporą do 120,30; rampa 18 % przy ścianie pn. segmentu; strop rampy przy licu zach. segmentu na **−0,77 = 118,53**, 0,40 m pod terenem istniejącym (118,93) i 0,72 m pod projektowanym (119,25).
(g) § 13 dla własnych pokoi w narożach wklęsłych: jednostki „segment zach. 1” i skrajna jednostka wieży pd. przy segmencie (u ≈ 17–21) są pomieszczeniami pomocniczymi (sektor symetryczny WT 2002 nie byłby spełniony).
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
* *Dostawy z Wybrzeża (J2) vs obsługa na bulwarze jako wada (J3):* jeden portal na skrajnym, pd. odcinku frontu (segment, 10,55 m). Brama garażowa 4,0 m i drzwi trafo/odpadów stoją we wspólnym rytmie granitowych filarów. Pozostałe 38 m frontu od bulwaru jest publiczne: Wejście Obywatelskie, kancelaria, podcień.
* *−2 tylko pod wieżą (J5) vs parkowanie wg MPZP (≥ 106 m.p. przy PU 8 850 m²) i krytyka platform:* v1.1 – −2 pod całym obrysem poza M1 przy Maz. 19, a brakujące stanowiska dają **stackery zależne tylko na −1 i tylko dla pracowników** (32 z 110 miejsc); goście, OzN i dostawy parkują na posadzce. Trzecia kondygnacja podziemna byłaby droższa o ok. 4 mln i zbliżała wykop do Maz. 19 (`geotechnika.md` – „nie rekomendujemy”).
* *Centrale na −2 (J1, J2) vs „technika krytyczna nad poziomem zalewu” (brief):* centrale nie są krytyczne, ale skracamy piony i rozdzielamy strefy pożarowe, więc są piętrowe (centrala parteru na kond. 1, centrala S na −1 przy trzonie B). Krytyczna elektryka i agregat stoją nad terenem (parter i kond. 1 segmentu).
* *Pełna kubatura Sejmiku (K5) vs minimum 35 m w A:* dodatkowa kondygnacja biurowa w tej samej bryle (PC nadziemna / PU 1,60 < 1,71 programu; PU 8 850 m² wg modelu pomieszczeń).

---

## 4. Bryły

### 4.1 Obrysy (e, n) – kolejność wierzchołków w JSON: CCW

| Bryła | Obrys (e; n) | Rzut | Kond. |
|---|---|---:|---|
| **W – Wieża Sejmiku** (w A) | SW (74,606; 40,756) → SE (113,468; 50,230) → początek łuku (109,750; 65,483) → **łuk R = 14,00 m**, środek (96,148; 62,167), przeciwnie do ruchu wskazówek → koniec łuku (92,832; 75,769) → NW (67,572; 69,611). W układzie (u, v): prostokąt 40,00 × 29,70 m, łuk z (40; 15,7) do (26; 29,7) | **1 145,83 m²**, poza A **0,000 m²** | P+6+S (+ antresola) |
| **M – Skrzydło Mazowieckie** | (48,842; 9,683) → (61,251; 66,053) → **łuk R = 3,50 m**, środek (64,669; 65,301), kąt naroża 116,1° → (63,840; 68,701) → (67,494; 69,592) → (74,557; 40,744) → (70,839; 39,838) → (63,498; 6,487) (w tabeli zgodnie z ruchem wskazówek; w JSON odwrotnie, bez kolca z v1.0, dziób wg tej tabeli) | **849,65 m²**, w A **0,000** | P+4 |
| **S – Segment Wybrzeża** | (96,694; 38,813) → (115,979; 39,930) → (113,480; 50,181) → (95,020; 45,681) | **167,40 m²**, w A **0,000** | P+4 |
| **Razem** (z wypełnieniem dylatacji) | | **2 165,8 m²** (58,1 % obszaru inwestycji) | |

Kontrole (shapely, `_rewizja_geometria.py`): wieża 0,25 m od granicy pn. (1KDG), 0,585–0,625 m od wsch. (6KDB/2); łuk 0,45 m od ścięcia granicy (dz. 19/1). Skrzydło: lico zach. na granicy z dz. 8/8 (droga, WT § 12 ust. 10), lico pd. przylega do szczytu Maz. 19 na 15,0 m (§ 12 ust. 3), dziób pn. 0,285 m od granicy. Segment: 0,24 m od granicy wsch., 4,58 m od dz. 10/2. **Żadnych nadwieszeń poza obszar (wariant A):** na licach < 0,30 m od granicy (wieża pn., skrzydło zach. i pd., dziób pn., segment wsch.) gzyms-attyka ma wysięg 0,00 m, a cień daje fryz wklęsły 0,15 m pod gzymsem; relief filarów to cofnięcie wypełnień za lico filarów = obrys. Wysięg 0,30 m tylko na licach dziedzińcowych skrzydła i segmentu. Na licach wieży (linia A i granica) – żadnego wysięgu (czapa attyki, obróbki, parapety, lamele w obrysie). Część wyższa niż 25 m istnieje wyłącznie w A, a w A nie ma dachu niższego niż 35 m.

### 4.2 Rzędne kondygnacji (±0,00 = 119,30 m n.p.m.)

| Kond. | Posadzka wzgl. | m n.p.m. | Wys. kond. | Strop nad kondygnacją: wierzch konstr. / spód (wieża; skrzydło) | Zakres |
|---|---:|---:|---:|---|---|
| −2 | −7,20 | 112,10 | 3,00 | wierzch −4,20 / spód −4,55 (w świetle 2,65) | wieża + segment + pas 5 m + skrzydło od s 12,15 (bez M1) |
| −1 | −4,20 | 115,10 | 4,20 | wierzch −0,15 / spód −0,55 (w świetle 3,65 – stackery) | całość + pas dziedzińca 5 m |
| P | ±0,00 | 119,30 | 4,80 | +4,65 / +4,37; +4,25 | całość |
| 1 | +4,80 | 124,10 | 3,75 | +8,40 / +8,12; +8,00 | całość |
| 2 | +8,55 | 127,85 | 3,75 | +12,15 / +11,87; +11,75 | całość |
| 3 | +12,30 | 131,60 | 3,75 | +15,90 / +15,62; +15,50 | całość |
| 4 | +16,05 | 135,35 | 3,75 | wieża +19,65 / +19,37; dach skrzydła +19,80 / +19,40; dach segmentu +19,10 (0,70 m na warstwy tarasu, retencję i donice; kond. 4 segmentu 2,87 m w świetle) | całość |
| 5 | +19,80 | 139,10 | 3,75 | +23,40 / +23,12 | wieża (= poziom tarasu segmentu) |
| 6 | +23,55 | 142,85 | 3,75 | +27,15 / +26,87 | wieża |
| **S** | **+27,30** | **146,60** | **8,90** | dach: ruszt 1,60 m, spód +34,15 | wieża |
| antresola S | +30,90 | 150,20 | — | — (3,30 m pod / 3,25 m nad antresolą) | wieża, 297,9 m² (26 % rzutu) |

Wysokości w świetle: biura w wieży 3,32 m (płyta 0,28 + podłoga 0,15; TABS odsłonięty, baffle); biura w skrzydle 3,20 m (płyta 0,40); parter wieży 4,37 m; sala 200 os. 4,25 m bez belek; sala obrad 6,85 m (rozdz. 7); pod antresolą S 3,30 m; garaż −1 3,65 m, −2 2,65 m.

### 4.3 Dachy a MPZP (od najniekorzystniejszego terenu w pasie 2 m wokół bryły)

| Dach | Teren min / max | Najniższy pkt pokrycia | → nad najwyższym terenem | Najwyższy pkt (attyka) | → nad najniższym terenem | Pasmo MPZP |
|---|---|---|---:|---|---:|---|
| Wieża (A) | 118,88 / 119,44 | +36,20 = **155,50** | **36,06 m** (≥ 35; zapas 1,06) | pokrycie max +36,45 = 155,75; attyka +37,20 = **156,50** | **37,62 m** (38,17 od 118,33) | 35–45 ✔ |
| Skrzydło | 118,36 / 119,43 | +20,20 = **139,50** | **20,07 m** (≥ 18; zapas 2,07) | pokrycie max 139,70; gzyms-attyka **140,15** | **21,79 m** | 18–25 ✔ |
| Segment (taras) | 118,91 / 119,18 | taras +19,80 = **139,10** | **19,92 m** (zapas 1,92) | attyka ściany pd. **139,10** (balustrada szklana cofnięta 1,5 m); pozostałe lica 140,15 | **21,24 m** | 18–25 ✔ |

Gzyms 140,15 = attyka Maz. 19 (140,24) −0,09 m (E07 „wyrównaj”). Spód gzymsu 139,45 (Maz. 19: 139,49). Hełmy pylonów mostu ≈ 147 m n.p.m. (szac.) leżą 6,9 m nad gzymsem kwartału.

### 4.4 Cofnięcia i wnęki

* **Podcień „Brama Mostowa”:** łuk między R 14 a R 11 (szklenie na R = 11,0 m) + elewacja pn. u 13,5–26,0 (szklenie na v = 26,70). Razem 96,4 m², głębokość 3,0 m, wys. 4,80 m, posadzka z granitu w poziomie skweru.
* **Brama ogrodowa:** (51,454; 21,549)–(52,325; 25,504)–(66,974; 22,280)–(66,103; 18,324). 4,05 × 15,0 m, wys. 4,80 m, 60,8 m².
* **Wnęki wejść 1,5 m** (WT § 292): Wejście Obywatelskie (elewacja wsch. wieży, v 1,4–6,8), wejście konferencyjne (dziób NW skrzydła), wejście ogrodowe (elewacja pd. wieży, u 8,6–11,4), wejście od skweru (podcień pn., u 21–24).
* **Ościeża:** wieża **0,45 m** (blacha Al lakierowana proszkowo w kolorze stolarki, granit tylko na licu filarów); skrzydło i segment 0,35 m (blacha Al). Kond. 6 („kondygnacja cienia”): szkło i metal 0,40 m za licem filarów. Łuk korony: lamele 0,60 m (R 13,40–14,00), szkło na R 13,40.
* Brak kondygnacji cofniętych. Brak balkonów powyżej 25 m (taras segmentu leży na +19,80).
* **Zadaszenie tarasu ogrodowego** wzdłuż elewacji pd. wieży (u 0,5–20,5, głęb. 4,0 m, h ≈ 4,0 m): BIPV szkło-szkło półprzezierne nad wejściem ogrodowym i wjazdem do rowerowni – element elewacji dziedzińcowej (MPZP § 6 pkt 13 nie obejmuje elewacji od dziedzińca).

---

## 5. Konstrukcja, trzony, posadowienie

**Siatka.** Wieża: moduł 1,35 m, filary elewacji co 2,70 m, słupy w co trzecim filarze, czyli osie u = 0,00 / 8,10 / 16,20 / 24,30 / 32,40 / 40,00 i **v = 0,00 / 8,70 / 16,00 / 23,15 / 29,70** (v1.1: słupy w liniach 8,70 i 23,15 jako 0,60 × 0,35 m w licach ścian korytarzy pierścieniowych, oś 16,00 w strefie środkowej; poza drogami garażu – stanowiska w trójkach 3 × 2,50 m między słupami u co 8,10 m, bez belek transferowych). Na łuku słupy promieniowe co 15° na R 13,50 i R 7,00. Płyty sprężone 0,28 m z TABS, rozpiętości ≤ 8,70 m. Słupy wewnętrzne kończą się na stropie S. Dach S to ruszt stalowy z kratownic 1,60 m (rozpiętość 19,5 m nad salą) z płytą zespoloną, oparty na ścianach trzonów, ścianie pd. sali i filarach łuku. Skrzydło: słupy w filarach obu elewacji co 4,05 m (2 osie okienne), płyty sprężone 0,40 m o rozpiętości **14,20 m bez słupów pośrednich**, dzięki czemu garaż pod skrzydłem ma 2 rzędy stanowisk bez słupów. Segment: słupy elewacyjne co 4,05 m, ściana pd. żelbetowa, płyta 0,28 m. Kondygnacje P–4 są ciągłe w rzucie (bez dylatacji w poziomie stropów; wspólna płyta fundamentowa). Uskok dachów na linii A to tylko obróbka.

**Trzony** (współrzędne (u, v) → e, n w `koncepcja.json`):

| Trzon | Obrys | Zakres | Skład |
|---|---|---|---|
| **A** | v1.2: u 8,30–15,50 × **v 11,85–20,85** (64,8 m²; wydłużony o 0,60 m na pd. – I5); (79,863; 54,235)–(86,858; 55,940)–(84,727; 64,684)–(77,732; 62,979) | −2…S + antresola | pas pn.: dźwigi A1, A2 po 1 600 kg (kabiny 1,5 × 2,1, szyby 2,25 × 2,55 m, **drzwi pn. na wszystkich kondygnacjach**) i **R – dźwig dla ekip ratowniczych PN-EN 81-72 i ewakuacyjny PN-EN 81-76**, 1 000 kg, kabina 1,1 × 2,1 m, szyb REI 60, drzwi pd. do przedsionka; pas pd.: **klatka A REI 60 3,40 × 5,80 m** (biegi 1,60 m, M.13) i **przedsionek ppoż. 3,10 × 5,80 m** z MOE 1,5 × 1,5 m, krzesłem ewakuacyjnym i interkomem, nadciśnienie; szachty nadciśnienia, oddymiania korytarzy, pionów |
| **B** | u 24,85–31,10 × v 0,50–9,90 (58,8 m²); (98,631; 47,127)–(104,703; 48,607)–(102,476; 57,740)–(96,404; 56,260) | −2…S + antresola | **klatka B 3,40 × 6,64 m** (v1.2: ściana klatka/przedsionek przesunięta o 0,29 m) i przedsionek 3,40 × 2,06 m z MOE 1,5 × 1,5 m; **P1, P2** publiczne **1 600 kg, kabiny 1,5 × 2,1 m** (M.13), drzwi wsch.; P1: P, 1–6, antresola; P2 przelotowy: −2, −1 (drzwi zach. do przedsionka B), P, 1–6, S (służbowy), antresola; szacht 2,15 × 3,20 m (po dźwigu T): spaliny agregatu, wyrzut i oddymianie garażu, piony centrali S → lamele korony od pd. |
| **T** (segment) | u 36,90–39,20 × v −9,70…−6,45, narożnik SE segmentu | −2…4 | dźwig osobowo-towarowy 2 000 kg, kabina 1,5 × 2,7 m; parter: drzwi od Wybrzeża (punkt odpadów, dostawy ręczne); −1: korytarz obsługi od stopy rampy (P-I5) |
| **C** (skrzydło) | s 0,5–8,6 × d 8,4–14,5; (57,153; 8,365)–(58,894; 16,276)–(64,852; 14,965)–(63,110; 7,054) | −1…4 | v1.2: **klatka C 5,80 × 3,40 m** (biegi 1,60 m; v1.1 – model pomieszczeń 6,00 × 3,05 m = biegi 1,425 m < M.13, a MDS 260 os. wymaga 1,56 m), przedsionek 5,80 × 2,00 m z MOE, szachty 1,60 × 5,60 m; **bez szybu rezerwowego C1** (nie mieści się obok klatki 3,40 m; ściana przy Maz. 19 REI 120 bez otworów); skrzydło obsługują dźwigi A1/A2 przez ciągłe korytarze kond. 1–4 |

Odległość klatek A–B: **19,8 m** między środkami klatek (v1.1: 20,0 m; najmniejsza między obudowami 13,95 m – rozdz. 16). Dojście z drogi pożarowej (dalszy pas Wybrzeża) do dźwigu R przez Bramę Mostową i halę: ok. 43 m (≤ 50 m). Holy windowe (`_v12_trzony.py` [T5]): A1/A2 (drzwi pn.) – hol Sejmiku na S i +30,90 5,95 m, łącznik pn. na P ≥ 3,6 m, korytarz pn. na kond. 1–6 **2,15 m**, na −1/−2 przedsionek ppoż. dźwigów w ślepym końcu drogi A2 (7,20 × 1,75 m, bez utraty miejsc); P1/P2 (drzwi wsch.) – korytarz wsch. na kond. 1–6 2,20 m (WT § 195 ≥ 1,6 m ✔; zalecenie M.13 3,6 m – świadome odstępstwo dla obu banków na kondygnacjach biurowych).

**Klatki (poprawka I5, `_v12_trzony.py` [T1]–[T4]).** Stopnie ≤ 17,5 × 28 cm (2h + s = 0,61–0,63 m), biegi 1,60 m, spoczniki ≥ 1,50 m, ≤ 17 stopni w biegu, prześwit ≥ 2,20 m. Klatka dwubiegowa wymaga: 5,24 m (3,00), 5,80 m (3,60 i 3,75), 6,08 m (4,20), 6,64 m (4,80). Klatka A v1.1 miała 5,15 m (brak 0,65 m na kondygnacjach typowych).

| Klatka (w świetle) | Kondygnacje typowe 3,75 m i S → +30,90 | −1 → P (4,20 m) | P → 1 (4,80 m) | Decyzja v1.2 |
|---|---|---|---|---|
| **A** 3,40 × 5,80 | 2 biegi × 11 st. 17,05 cm (S → ANT 11 + 10 st. 17,14), 5,80 m | 3 biegi × 8 st. 17,50 cm, 4,96 m | 3 biegi 10 + 9 + 9 st. 17,14 cm, 5,52 m | trzon A wydłużony o 0,60 m na pd. (v 12,45 → 11,85, ściana 0,20 m) kosztem holu strefy środkowej, Hali i kuluaru S; spocznik parteru na końcu pn. (przedsionek wzdłuż całej klatki), na pozostałych kondygnacjach na końcu pd. |
| **B** 3,40 × 6,64 | 2 biegi, 5,80 m | 2 biegi × 12 st. 17,50 cm, 6,08 m | 2 biegi × 14 st. 17,14 cm, 6,64 m | ściana klatka/przedsionek przesunięta o 0,29 m (przy 6,35 m parter wymagałby 4 biegów z prześwitem 2,05 m < 2,20); spocznik zawsze przy przedsionku |
| **C** 5,80 × 3,40 | 2 biegi, 5,80 m | 3 biegi × 8 st., 4,96 m | 3 biegi 10 + 9 + 9 st., 5,52 m | nowy układ w obrysie trzonu C (biegi 1,60 zamiast 1,425 m), bez szybu C1 |

Wpływ na kondygnacje biurowe: pas 7,20 × 0,60 m (4,32 m²) zajmuje wyłącznie komunikację – hol przed przedsionkiem A na kond. 1–6 (pozostaje ≥ 3,35 m), Halę na P (naroże trzonu 4,57 m od osi Hali, było 4,99) i pas za stanowiskami R2 w garażu (110 m.p. bez zmian, `_rewizja_parking.py` z obrysem v1.2). **Liczba jednostek elewacyjnych bez zmian (0 naruszonych; 43/43/43/43/22/20 + P 4).**

**Ustrój:** żelbet monolityczny, sztywność dają trzony A, B, C i ściana przy Maz. 19 (REI 120). Beton CEM III/A–B, kruszywo z recyklingu w elementach niekonstrukcyjnych, stal zbrojeniowa i konstrukcyjna z pieca łukowego.

**Posadowienie i woda gruntowa** (`geotechnika.md`): ZWG średnio 115,5, maks. 116,45, poziom obliczeniowy ≥ **117,0**, sytuacja wyjątkowa 119,0 m n.p.m.
* **Obudowa:** ściany szczelinowe **0,60 m** (wykop ≈ 8 m rozparty stropami) na obwodzie −1 poza odcinkiem przy Maz. 19: **222,6 m × 19 m ≈ 4 230 m²**, wcięte w gliny zwałowe QpB (strop 101,8–103,4; `geotechnika.md`: 19–20 m), jednocześnie absorbery GPC (ściany energetyczne). Biała wanna, odwodnienie tylko wewnątrz obudowy, **bez obniżania zwierciadła poza wykopem** (ochrona Maz. 19, WS 5–6 i drzew). Bez kotew gruntowych poza granicą (rozparcie stropami).
* **Przy Maz. 19 (15,0 m):** zamiast ściany szczelinowej **ściana z kolumn iniekcji strumieniowej Ø 1,2 m** (siecznie, styczne do granicy, kształtowniki co drugą kolumnę, okładzina żelbetowa 0,30 m), która **podbija fundament szczytu** (kolumny pod odsadzką; wejście pod budynek sąsiada wymaga zgody właściciela/zarządcy – art. 47 Pb); przed robotami odkrywki fundamentu, inwentaryzacja rys, monitoring geodezyjny, bez wibracji. Lico −1 na tym odcinku 1,20 m od granicy. −2 nie sięga pod M1 (s < 12,15), więc wykop przy kamienicy ma głębokość −1.
* **Granica z dz. 8/8 (60,2 m):** lico zewnętrzne ściany szczelinowej 0,15 m od granicy (tolerancja wykonania + odchyłka pionu 0,5 % × 19 m); zewnętrzna ściana prowadząca tymczasowo w chodniku Mazowieckiej – zajęcie pasa drogowego za zezwoleniem ZDiUM (art. 40 ustawy o drogach publicznych), rozbierana po wykonaniu oczepu. Tak samo przy licu pn. wieży (0,25 m) i wsch. segmentu (0,24 m) – ściany prowadzące 0,20 m. Ściana parteru stoi na oczepie ze wspornikiem 0,15 m.
* **Wieża:** płyta palowo-fundamentowa 1,10 m na −2 (spód 110,90 m n.p.m.), 36 pali CFA Ø 0,8 m, L ≈ 14 m (energetyczne), oparte na glinach.
* **Skrzydło i segment:** płyta 0,90 m; pod skrzydłem z −2 wypór 61 kPa (117,0) / 81 kPa (119,0) < 0,9 × ≈ 110 kPa ciężaru stałego. Pas dziedzińca bez nadbudowy: mikropale kotwiące (121,5 m²).
* Przy drzewie nr 78 (M.06, Z1): wygrodzenie korona + 1 m, odkrywki ręczne, nadzór arborysty (bez palisady).
* **Zabezpieczenie przed wodą powierzchniową:** próg bramy **119,10** (= chodnik) + **samoczynna zapora przeciwpowodziowa do 120,30** we wnęce bramy, odwodnienie liniowe, pompownia, zawory zwrotne; wszystkie otwory podziemia ≥ 120,30.
* **Pole sond GPC:** 58 sond w siatce 6,0 × 6,0 m pod płytą −2 (2 088 m²), L = 91 m od spodu płyty → dno 19,9 m n.p.m., **≤ 99,5 m pod terenem** (poza reżimem art. 86 PGiG), kolektory w warstwie podpłytowej, 2 przejścia szczelne do maszynowni.

---

## 6. Organizacja kondygnacji

**Moduł i pokój.** Moduł 1,35 m. Pokój 24 m² = 3 moduły: oś 4,05 m, szerokość netto 3,95 m × głębokość netto 6,10 m = **24,1 m²**. Pokój GW 32 m²: w skrzydle 4 moduły (5,30 × 6,10 = 32,3 m²), w wieży „głęboki” 3,95 × 8,10 = 32,0 m². Sala narad 7,60 × 7,90 m = 60 m². Magazynek głęboki 2,60 × 9,25 m = 24,05 m². Okno pokoju 24 m² w wieży (1,5 przęsła) to 6,1 m² w świetle ościeżnic, w skrzydle (2 okna 1,20 × 2,35) 5,6 m², czyli ≥ 1/8 podłogi (WT § 57).

**Trakty.** Wieża: pokoje 6,10 | korytarz pierścieniowy 1,80 | strefa środkowa ≈ 12,2 m (trzon A, WC, socjalne, centrala 25 m², MFP, PD, porządkowe, miejsca oczekiwania, budki do rozmów) | 1,80 | 6,10. Skrzydło: trakt dwustronny 15,00 m = 0,47 (ściana z wełną 240 mm λ 0,031) + 6,08 + 0,10 + **1,70** (korytarz) + 0,10 + 6,08 + 0,47; pokój 3,95 × 6,08 = 24,02 m². Segment: pokoje od Wybrzeża + korytarz w osi korytarza wsch. wieży + pas usług od zach.

**Pojemność elewacyjna** (jednostki 4,05 m przy głębokości 6,10 m; sucha próba modelu pomieszczeń `docs/70_rysunki/rzuty_raport.md`): kondygnacje 1–4 po **43**; kondygnacja 5 – **22** (sama wieża: naroża z końcami korytarzy, trzon B przy elewacji pd.); kondygnacja 6 – **20** (łuk zajmuje gabinet Przewodniczącego z zapleczem i asystentem); parter 4. Razem 218, zajęte ≈ 216 – bez rezerwy (v1.0 „rezerwa 3,2 j.” nie istniała). Jednostki w narożu wklęsłym segment/wieża są pomieszczeniami pomocniczymi.

### Rozmieszczenie (187 pokoi wg zał. 1 M.01; departamenty niedzielone)

| Kond. | Komórki (pokoje) | Pokoje | Sale narad | Magazynki 24 m² (przy elewacji) | Socjalne 24 m² | Inne |
|---|---|---:|---:|---:|---:|---|
| −2 | – | – | – | – | – | garaż **40 m.p.** (budowla ochronna – ukrycie ≤ 300 os., wyjścia klatkami A i B), maszynownia GPC + bufory 95 m² (przy trzonie B), filtrowentylacja 30 m² + WC ukrycia 15 m², zbiornik deszczówki 50 m³ (łuk); stopa rampy wewnętrznej w segmencie; tryskaczy i agregatu brak |
| −1 | – | – | – | – | – | garaż **70 m.p.** (38 na posadzce + 32 w stackerach zależnych; 6 OzN przy trzonach A i B), MDS 260 os. (klatka C, rampa, szyb wyjścia zapasowego z tunelem 7,6 m), sanitariaty MDS 30 m² z WC dostępnym, pralnia 10 m² (pn. od trzonu A), centrala S 40 m² (wsch. od trzonu B), woda szara MBR 27 m² (łuk), przyłącze wody 20 m² (pod rampą), warsztat PPT 40 m², odpady 24 m², magazyn MDS 20 m² (M1), korytarz obsługi do dźwigu T; szatnie rowerzystów przy rowerowni na parterze, szatnie personelu – parter (u 0,5–8,15) |
| P | **DK II (2)**, **DW (2)** | 4 | – | – | – | strefa publiczna, centrum konferencyjne, bistro (niżej) |
| 1 | **DOS (38)** | 38 | 1 | 3 (głębokie) | 3 | serwerownia TIER II 50 m² + UPS 15 m² (strefa środkowa) |
| 2 | **DI (25) + DST (13)** | 38 | 1 | 3 | 3 | – |
| 3 | **DGP (24) + GW (11 = 8 × 32 m² w wieży + 3 × 24)** | 35 | 2 | 4 | 3 | archiwa GW 48 + 24 m², pracownia/urządzenia GW 24 m² (Wyj. 6 odp. 26) |
| 4 | **pion 8: CZ (3) + DKD (12) + DZ (19)**, gabinety CZ, dyrektorów departamentów i wydziałów obok siebie przy trzonie A (Wyj. 10 odp. 62) | 34 | 2 | 6 | 3 | sala narad z kond. 5 |
| 5 | **DSS (19) + DRA 5.2 (2)** (Wyj. 17 odp. 70 – sąsiednia kondygnacja) | 21 | – (→ kond. 4) | 1 (3 → kond. 1 i 2) | 2 | wyjście na taras nad Oławą (135 m²); 21/22 j. |
| 6 | **Kancelaria Sejmiku (8)** + gabinet Przewodniczącego 48 m², zaplecze 8 m² i asystent 24 m² (łuk NE, widok na most) + 3 gabinety Wiceprzewodniczących po 24 m² (elewacja; zakres programu 24–40) + sala spotkań KS.05 dzielona 2 × 44 m² (strefa środkowa przy holu A, przeszklona, doświetlenie pośrednie przez pokój narożny NW – sale okresowego użytku) + miejsca oczekiwania KS.06 i DRA.OCZ jako wnęki holu; **DRA (9)** | 17 | – | – | 1 | 20/20 j.; połączenie z kondygnacją Sejmiku dźwigami A1/A2 i klatką A |
| S | Sejmik (rozdz. 7) | – | – | – | – | – |
| **Σ** | | **187** (179 × 24 + 8 × 32) | **6** | **20** | **15** | MFP 10, porządkowe 12, PD na każdej kondygnacji |

Na każdej kondygnacji 1–6 jest zespół WC w strefie środkowej wieży (K, M, toaleta dostępna): kond. 1–4 ≥ 24 m² (nieoświetlony pas zach. wieży), kond. 5–6 ≥ 26 m²; na kond. 1–4 drugi zespół przy trzonie C. **WC razem ≥ 380 m²** (model pomieszczeń: 397,7 m²); parter: WC ogólnodostępne ≥ 30 m² + komfortka. Pokoje socjalne: 4. pokój na kond. 1 (pas zach.), drugi na kond. 6 w strefie środkowej (D3). Archiwum PZGiK na kond. 3 – strefa płyty 0,40 m z belkami, gaszenie gazem (D15). Miejsca oczekiwania (9) leżą przy sekretariatach. Strefy pożarowe: kond. 1–4 po 2 160 m², P 2 003 m², S z antresolą 1 443,7 m² (< 2 500).

**Parter (P):**
* **Wieża (1 049,5 m² PC poza podcieniem):**
  * Hala Obywatelska z osią przekątną: informacja 8 m², poczekalnia 40 m², lapidarium (ściana witryn 12 m przy trzonie A + ślad murów piwnic inkrustowany w posadzce), pokój cichy 16 m²;
  * kancelaria ogólna 36 m² (3 stanowiska, lada niska 0,75 m, pętla) z zapleczem **DK II** (2 pokoje od Wybrzeża);
  * **Wejście Obywatelskie** – lobby 57 m² z kontrolą i szatnią przy P1/P2 (u 31,25–39,5 × v 0,5–7,45);
  * WC ogólnodostępne ≥ 30 m² + **komfortka 12 m²** (3,0 × 4,0 m, 14 m od wejścia głównego; u 15,65–21,0 × v 15,0–20,85, strefa poszerzona kosztem hali);
  * szatnie i WC personelu + zaplecze sanitarne rowerowni (u 0,5–8,15 × v 12,45–20,85); centrum monitoringu 24 m² + socjal ochrony 10 m² w łączniku od skweru (okna pn., D15);
  * **rowerownia 50 stanowisk** 90 m² (u 0,5–8,15 × v 0,5–12,3) z wjazdem od dziedzińca pod zadaszeniem BIPV, zaplecze sanitarne obok (PR.02);
  * łącznik do foyer skrzydła z oknami na skwer (u 0,5–13,35 × v 21,0–29,2); drugie wejście od skweru w podcieniu pn. (u 21–24).
* **Skrzydło (786,2 m²):**
  * M1 (s 0–12,15): DW (2 pokoje od ulicy), trzon C, pokój techników 20 m², socjal personelu technicznego 20 m²;
  * brama ogrodowa (s 12,15–16,20);
  * **sala 80 os.** 6,90 × 14,0 = 96,6 m² (s 16,35–23,25);
  * **sala 200 os.** 16,20 × 14,0 = 226,8 m², w tym 2 reżyserki po 10 m², dzielona ścianą mobilną na 2 × 103 m², 4,25 m w świetle (s 23,40–39,60);
  * foyer, szatnia, WC konferencyjne, magazyn mebli (s 39,75–50; 138,2 m² w obrysie skrzydła – v1.0 liczyła 20 m² w wieży);
  * **bistro 82 m² brutto** (sala 62 + zaplecze 20, bez kuchni gorącej – regeneracja, wyciąg z odzyskiem do instalacji ogólnej) w dziobie NW z tarasem na najszerszej (17,9 m) części skweru; obok wejście konferencyjne; 10 m² zaplecza przeniesione do M4.
* **Segment (167,4 m²):** rampa garażu **jednopasowa 3,50 m wzdłuż ściany pn.** (v −0,35…−3,85), **brama 4,0 m** od Wybrzeża (v −0,40…−4,40), próg 119,10 z zaporą samoczynną; w pasie pd. (93 m² brutto / 80 m² netto) trafo SN/nn 21 m² (drzwi od Wybrzeża, wentylacja kanałem do lica zach.), rozdzielnia nn z SZR 17 m², BESS 100 kWh 11 m² (EI 120; v1.2), punkt wystawienia odpadów 7 m² i szyb dźwigu T w narożniku SE.
* **Segment, piętra:** kond. 1 – agregat HVO (pas zach., wzmocniony strop; powietrze przez żaluzje 8 m² w licu zach., spaliny szachtem w trzonie B do korony); kond. 2 – falowniki i rozdzielnice DC PV 12 m²; kond. 4 – dry-cooler hybrydowy 2 × 150 kW (żaluzje akustyczne 2 × 12 m² w licu zach. na kond. 3–4); pozostałe usługi pasa zach. – strefa środkowa wieży.

---

## 7. Kondygnacja Sejmiku (+27,30 = 146,60 m n.p.m.; h = 8,90 m; antresola +30,90) – S-3 „hol z galerią”

> **v1.2:** rozdział zastępuje stan 1.0. Wariant S-3 przyjęto po sprawdzeniu hipotezy weryfikatora S-2 i wariantów galerii (`kondygnacja_S2.md`, rozdz. 2). Dane: `model/koncepcja.json["kondygnacja_sejmiku"]` (= `kondygnacja_S2.json`). Dowody: `_s2_geometria.py` [G1]–[G8], `_s2_sala.py` [S1]–[S7], `_s2_ewakuacja.py` [E1]–[E6], trzony `_v12_trzony.py` [T1]–[T7]. Rzut: `img/s2_plan.png`, przekrój linii wzroku: `img/s2_przekroj.png`.

**Zasada (Wyj. 21 odp. 85; WT § 3 pkt 19).** Wszystkie pomieszczenia zamknięte programu Sejmiku leżą na poziomie S w obrysie wieży, czyli w całości w A (wieża poza A: 0,000 m²; [W2] `_v12_scalenie.py`). Antresola **297,9 m² (26,0 % rzutu)** ma dwie otwarte części rozdzielone ścianą i pustką sali:
* radnych 161,4 m² – hol górny 89,6 + bar SWD.05 32,0 + strefa multimedialna SWD.03 33,8 + przedsionek A' 6,0;
* publiczności 136,5 m² – galeria SWD.01g 65,3 + hol P1/P2 22,0 + korytarz EI 30 43,5 + toaleta dostępna 5,7.

Zamknięte przegrodami na +30,90 są tylko toaleta publiczności, przedsionek A' (element klatki A) i korytarz publiczny EI 30 (droga ewakuacyjna). Antresola jest wszędzie ≥ 1,35 m od lica elewacji (w pasie przyelewacyjnym 0,00 m²), więc okna 1,65 × 4,20 m (pd., zach.) i 1,65 × 5,00 m (pn.) zachowują pełną wysokość. Pod antresolą 3,30 m w świetle, nad nią 3,25 m do spodu kratownic. Kancelaria Sejmiku leży kondygnację niżej (kond. 6; wykładnia I7 – rozdz. 16).

### 7.1 Pomieszczenia (netto z poligonów, PN-ISO 9836) [G4]

| Kod | Pomieszczenie | Poziom | m² | Program (zakres) |
|---|---|---|---:|---|
| SWD.01 | Sala obrad – płyta (47 stanowisk, prezydium, mównica, goście 12, media 8, obsługa 4, PJM 2) | S | 232,0 | |
| SWD.01g | Galeria publiczności (część SWD.01): 31 miejsc + 3 dla wózków | ANT | 65,3 | |
| **SWD.01** | **razem** | | **297,3** | 320 (280–380) ✔ |
| SWD.02 | Hol reprezentacyjny – poziom dolny (pustka 2-kond. NW, hol dźwigów A1/A2, pas pn.) | S | 74,8 | |
| SWD.02g | Hol reprezentacyjny – poziom górny (antresola radnych) | ANT | 89,6 | |
| **SWD.02** | **razem (wolna podłoga, bez szatni i baru)** | | **164,4** | 150 (120–220) ✔ |
| SWD.03 | Sala multimedialna / poczekalnia gości – strefa otwarta na antresoli holu, 20 miejsc, ekran, głośniki kierunkowe, pętla | ANT | 33,8 | 40 (30–60) ✔ |
| SWD.04 | Reżyserka (przeszklenie na prezydium i rzędy) | S | 17,6 | 20 (15–30) ✔ |
| SWD.05 | Przestrzeń socjalno-gastronomiczna (bar z przyłączami) | ANT | 32,0 | 40 (30–60) ✔ |
| SWD.06 | Szatnia – lada 4,1 m + wieszaki (otwarta na hol) | S | 12,5 | 15 (12–20) ✔ |
| SWD.07 | Pokój matki z dzieckiem | S | 11,2 | 10 (8–12) ✔ |
| SWD.08 | Sala komisji 50 os. | S | 90,5 | 100 (90–120) ✔ |
| SWD.09 | Sala komisji 30 os. | S | 54,3 | 60 (54–72) ✔ |
| SWD.10a/b | Zaplecza nagrań komisji (okna do sal, drzwi do kuluaru) | S | 2 × 8,7 | 10 (8–12) ✔ |
| SWD.11a | Klub radnych 30 os. (1) | S | 54,5 | 60 (54–72) ✔ |
| SWD.11b | Klub radnych 30 os. (2), naroże SE (okna pd. i wsch.) | S | 55,4 | 60 (54–72) ✔ |
| SWD.12a/b | 2 kluby radnych 15 os. (okna zach.) | S | 2 × 30,2 | 36 (30–40) ✔ |
| SWD.13 | Wspólna sala radnych (okno pn. – Ostrów Tumski) | S | 36,2 | 48 (36–60) ✔ |
| SWD.14 | Pokój socjalny radnych (aneks kuchenny, okno pn.) | S | 20,0 | 24 (20–30) ✔ |
| SWD.15 | Magazyn podręczny (pod wyższą częścią biegu schodów) | S | 6,0 | 10 (6–15) ✔ |
| PHS.05a/b | WC damskie / męskie, każde z kabiną dostępną 2,2 × 2,5 m | S | 2 × 18,4 | |
| PHS.05c | Toaleta dostępna publiczności (przy holu P1/P2) | ANT | 5,7 | |
| **PHS.05** | **razem** | | **42,5** | 45 (35–60) ✔ |
| PP.06 | Pomieszczenie porządkowe | S | 5,5 | 6 (4–8) ✔ |
| IT.02 | Punkt dystrybucyjny IT (przy zapleczach nagrań) | S | 4,8 | 6 (4–10) ✔ |
| | **Suma programu (SWD + PHS.05 + PP.06 + IT.02)** | | **1 016,2** | 1 106 (min. 928): **+88,2 nad minimum** |

Wszystkie pozycje mieszczą się w zakresach programu (SWD.01 i SWD.02 liczone łącznie z częścią na antresoli). Każde pomieszczenie ma drzwi na komunikację [G3].

### 7.2 Bilans poziomu S i antresoli [G5], [G6]

| Składnik | m² |
|---|---:|
| Pomieszczenia (z salą, holem i szatnią) | 789,8 |
| Komunikacja: kuluar 83,8 + pasaż zach. 15,4 + łącznik wsch. 12,0 + dojście do SWD.11b 4,2 + schody reprezentacyjne 8,4 | 123,7 |
| Trzony A (64,8; v1.2 wydłużony wg I5) i B (58,8) | 123,6 |
| Ściany wewnętrzne (średnio 0,219 m; ściany sali 0,30 m) | 43,1 |
| **Wnętrze od lica wewnętrznego** | **1 080,2** |
| Ściany zewnętrzne | 65,6 |
| **PC poziomu S = rzut wieży w A** | **1 145,8** |
| **Antresola +30,90** (radni 161,4 + publiczność 136,5) | **297,9** |

### 7.3 Sala obrad – rzędy, galeria, linie wzroku [S1]–[S7]

| Rząd | Krawędź pulpitu R (od mównicy F = u 27,50; v 15,20) | Podest | Stanowiska | Wózek |
|---|---:|---:|---:|---|
| 1 | 4,50 m | +0,00 | 7 + 1 | koniec zach., na posadzce |
| 2 | 6,30 m | +0,09 | 10 + 1 | koniec zach., przy pochylni |
| 3 | 8,10 m | +0,18 | 12 + 1 | jw. |
| 4 | 9,90 m | +0,27 | 14 + 1 | jw. |
| **Razem** | | | **43 + 4 = 47** (wymagane 44) | pole 0,9 × 1,4 w każdym rzędzie |

* **Wymiary:** płyta 232,0 m² (u 22,0–39,5 × v 12,6–29,2 minus łuk R 13,5 i reżyserka w narożu SE), 6,85 m w świetle (+27,30 → spód kratownic +34,15); z galerią 297,3 m².
* **Pochylnie bez podnośników:** przewyższenie 0,09 m na rozstawie 1,80 m = 5,0 %, więc przejście wsch. (promieniowe, 1,30 m) ma dokładnie 5,00 %, a przejście zach. wzdłuż ściany sali odcinki 3,90 / 4,39 / 4,61 % (8,61 m); równolegle przejście płaskie 1,10 m.
* **Prezydium (4, stół 6,0 m) i mównica** (blat regulowany 0,75–1,20 m, pętla) na +0,00 przy **pełnej ścianie pd.** z godłem; za nią drzwi prezydium z kuluaru. PJM przy mównicy w kadrze kamery. Mównica – 1. rząd 5,40 m.
* **Płyta:** 47 + prezydium 4 + obsługa 4 + PJM 2 + goście 12 (strefa NW przy drzwiach z holu) + media 8 (łuk R 11,95 m) = **77** (wymagane 70). **Galeria 31 + 3 dla wózków.** Razem ≥ 100.
* **Galeria publiczności** – antresola nad holem dźwigów A1/A2 (u 15,5–22,0 × v 12,6–22,65), balustrada szklana 1,10 m (część pionowa 0,70 + pozioma 0,50), 2 rzędy: +0,00 (3 miejsca dla wózków z opiekunami + 10) i +0,90 (18). Linia wzroku rzędu 2 nad rzędem 1: **C ≥ 77 mm** do całego prezydium (36/36), ≥ 346 / 395 mm do mówcy siedzącego / stojącego; zapas nad cokołem ≥ 289 mm; kąt na prezydium 34°–91° (mediana 60°), odległość 6,1–11,1 m. Galeria w łuku NE za radnymi sprawdzona i odrzucona (38 / 31 miejsc).
* **Linie wzroku radnych:** do mówcy stojącego C ≥ 111 mm (39/39); do siedzącego prezydium 125/156 linii z C ≥ 60 mm (pozostałe skośne, min. 39 mm – uzupełnienie: ekrany pulpitów).
* **Poufność głosowania:** ekrany pulpitów z filtrem ±30°; najmniejszy kąt normalna ekranu – oko na galerii **38,7°** ✔ + tryb tajny w systemie.
* **Światło:** radni patrzą na pełną ścianę pd.; najmniejszy kąt kierunek patrzenia – szkło **51,1°** (pole ±45° wolne); odcinek łuku φ 0–10° przy reżyserce – szkło nieprzezierne za lamelami (z zewnątrz bez zmian).
* Wentylacja wyporowa z cokołów pulpitów (kanały w podestach i warstwie posadzki 0,15 m), centrala S na −1 przy trzonie B. Pętla indukcyjna, napisy na żywo.

### 7.4 Strefy, ruch i układ

* **Poziom S:** pas pd. (okna 1,65 × 4,20) – SWD.08, SWD.09 z zapleczami nagrań, PD, klub SWD.11a przy trzonie B; naroże SE – SWD.11b (dojście 1,6 m z kuluaru i służbowy przystanek P2), pokój matki z dzieckiem, porządkowe. **Kuluar 2,20 m** (przy trzonie A 1,75 m) łączy klatki A i B – droga chroniona EI 30, drzwi S, samoczynne oddymianie. Pas zach.: kluby 15 os. (okna zach.) i pasaż 1,8 m; między trzonem A a salą łącznik 1,4 m i WC K, M; pas pn.: pokój socjalny i wspólna sala radnych (okna 1,65 × 5,0); naroże NW: pustka 2-kond. (okna pn. na Ostrów Tumski i zach. na pl. Społeczny), szatnia, schody reprezentacyjne na antresolę radnych.
* **Radni, Zarząd, goście:** dźwigi A1/A2 (drzwi pn.) z holu głównego i garażu prosto do holu Sejmiku (wolna głębokość 5,95 m), wejście główne do sali z holu (NW, 1,6 m). Hol dolny i górny łączą schody reprezentacyjne i A1/A2 (przystanek +30,90).
* **Publiczność:** Wejście Obywatelskie → kontrola → P1/P2 → przystanek +30,90 (hol 3,6 × 6,1 m = 22,0 m² z toaletą dostępną) → korytarz EI 30 nad kuluarem → galeria. **P1 nie zatrzymuje się na S**, P2 – tylko służbowo (na klucz). Publiczność nie wchodzi w strefę radnych; drzwi przedsionków A i A' z kontrolą dostępu zwalnianą przez SSP.

### 7.5 Ewakuacja, strefy, dźwigi [E1]–[E6]

* **Osoby:** maks. 354 → biegi 0,6 × 3,54 = 2,12 m ≤ 2 × 1,60 m ✔; kuluar 2,12 m ≤ 2,20 m ✔; przy trzonie A 1,75 m na 7,20 m (≥ 1,40 m WT; przepustowość 292 os. > ≈ 84 os. z części zach., bo hol i antresola radnych mają łącznik do przedsionka A i przedsionek A').
* **Strefa ZL I:** S + antresola = 1 145,8 + 297,9 = **1 443,7 m² ≤ 2 500 m²**. Strefy dymowe: (1) sala + galeria, (2) hol + antresola radnych (schody reprezentacyjne wewnątrz), (3) kuluar i korytarz publiczny – drogi chronione. Bez schodów z antresoli do kuluaru (I4).
* **Klatki A i B przedłużone do +30,90.** Przedsionki z nadciśnieniem i MOE 1,5 × 1,5 m: A 3,10 × 5,80 m (z dźwigiem R), A' 2,00 × 3,00 m, B 3,40 × 2,06 m.
* **Limity (tryskacze nieprojektowane – v1.1):** przejście 40 m (+25 % w sali i holu h > 5 m), dojście ZL I 10 m (1 kierunek) / 40 m (2 kierunki); kuluar i korytarz publiczny z samoczynnym oddymianiem sterowanym SSP → +50 % (15 / 60 m, § 256 ust. 3; wykładnia do potwierdzenia z rzeczoznawcą).

| Droga | Przejście [m] | Dojście [m] | Klatka |
|---|---:|---:|---|
| Sala: media NE → przejście wsch. → drzwi SE → kuluar | 17,1 | 8,2 | B |
| Sala: media NE → za rzędem 4 → przejście zach. → drzwi SW → kuluar | 25,5 | 10,9 | A |
| Galeria → foyer → przedsionek A (+30,90) / → korytarz publiczny → przedsionek B | 9,0 / 11,2 | 0 / 12,0 | A / B |
| Toaleta publiczności → hol P1/P2 → korytarz → przedsionek B (1 kierunek) | 2,2 | 14,1 ≤ 15* | B |
| Antresola radnych: bar → przedsionek A' / → schody → hol → łącznik → kuluar | 21,1 / 39,7 | 0 / 13,2 | A / B |
| Hol NW → pasaż → kuluar / → łącznik → przedsionek A | 10,7 / 17,6 | 16,6 / 4,9 | A |
| SWD.08 (naroże SW) → kuluar | 9,6 | 11,5 (A) / 21,5 (B) | A, B |
| SWD.11b (naroże SE) → dojście → kuluar (1 kierunek do B) | 9,7 | 10,2* (B) / 22,8 (A) | B, A |
| PP.06 – ślepy koniec kuluaru wsch. (odcinek 11,4 m) | 0,9 | 13,9* | B |

\* dojście jednokierunkowe > 10 m – wymaga zwiększenia +50 % za samoczynne oddymianie drogi (limit 15 m).

| Dźwig | Udźwig / kabina | Drzwi i przystanki na S / +30,90 | Wolna głębokość |
|---|---|---|---:|
| A1, A2 | 1 600 kg, 1,5 × 2,1 (3,15 ≤ 3,56 m², PN-EN 81-20 tabl. 6) | pn., S i +30,90 | 5,95 m ✔ M.13 |
| P1, P2 | 1 600 kg, 1,5 × 2,1 | wsch.; P1 tylko +30,90, P2 +30,90 i S (służbowy) | 3,60 / 1,60 m ✔ |
| R | 1 000 kg, 1,1 × 2,1 (PN-EN 81-72/76) | pd. do przedsionka A, S i +30,90 | MOE w przedsionku ✔ |

### 7.6 Dostępność i odstępstwa

* Galeria: 3 miejsca dla wózków z opiekunami w rzędzie 1, bez stopni z P1/P2; toaleta dostępna ≈ 4 m od drzwi dźwigów. Sala: 4 stanowiska radnych dla wózków (po jednym w rzędzie) przy pochylniach ≤ 5 %; prezydium i mównica bez stopni. WC K i M z kabinami dostępnymi 2,2 m (przewijaki w przedsionkach). Szatnia z częścią lady 0,75–0,80 m. MOE w przedsionkach A, A', B.
* **Świadome odstępstwa od M.13 (WT spełnione):** szerokość 1,8 m – łącznik wsch. 1,40 m, dojście do SWD.11b 1,60 m, przystanek służbowy P2 1,60 m, kuluar przy trzonie A 1,75 m (v1.2).

---

## 8. Elewacje

**Materiały (2 mineralne + metal):**
* **G – jasny granit strzegomski płomieniowany**, NCS S 1502-Y. Lica filarów wieży (bez ościeży), gzymsy, kordon, attyka, posadzki zewn. (skwer, wejścia); cokół parteru w odcieniu S 3502-Y (ta sama rodzina, ciemniejszy o ≈ 15–25 L*). Ta sama rodzina co okładzina pylonów mostu.
* **C – ceramika glazurowana półmatowa** (profile ekstrudowane 40 mm, A1) na elewacjach od ulic, w odcieniach: M1 S 1505-Y20R, M2 S 1010-Y30R, M3 S 2005-Y20R, M4 S 1510-Y30R, segment S 1010-Y30R, łuk S 1005-Y20R, **lamele korony S 4005-Y20R** (ton w ton ze szkłem). Elewacje dziedzińcowe skrzydła i segmentu (≈ 410 m²): tynk mineralny cienkowarstwowy na wełnie (A2-s1,d0) w tonie ceramiki posesji.
* **Me – aluminium, grafitowy brąz** (RAL 8019 ≈ NCS S 7502-Y; stolarka anodowana, ościeża i obróbki lakierowane proszkowo). Stolarka, **ościeża wieży (0,45 m) i skrzydła (0,35 m)**, płyciny wieży (od dziedzińca ≤ 25 m jako BIPV w tym kolorze, bez płycin czerpni), kondygnacja 6, obróbki, żaluzje czerpni i wyrzutni (tylko od dziedzińca).
* **Szkło:** neutralne, R ≤ 12 %. Biura g 0,33, Tvis 0,62, Uw ≤ 0,80. Korona g 0,27, Tvis 0,48, Ucw ≤ 0,90. Ochrona ptaków od strony Odry (wzór punktowy na szkle korony).

**Kompozycja: cokół / trzon / zwieńczenie.**
* **Skrzydło i segment – porządek kamieniczny:**
  * oś okien **2,025 m** (1,5 modułu), filar 0,825 m, okno **1,20 × 2,35 m** (parapet 0,60 m, kwatera stała ze szkła bezpiecznego do 0,90 m, pochwyt 1,10 m; nadproże 2,95 m, kaseta ZIP do 3,13 m pod stropem 3,20 m), ościeże 0,35 m (blacha Al), WWR 37 %;
  * **cokół** (P, 4,80 m): granitowe filary co 4,05 m, witryny na pełną wysokość z naświetlem na **122,77** (linia pasa nad parterem Maz. 19); kordon granitowy 0,35 m na **124,10**; w części pd. (chodnik 118,60–118,72) cokół pełny 0,70 m jak boniowany parter Maz. 19;
  * **trzon** (1–4): ceramika w reliefie posesji;
  * **zwieńczenie:** gzyms-attyka granitowy 0,70 m (spód **139,45**, wierzch **140,15**); **od ulicy, skweru i przy Maz. 19 bez wysięgu** (lico < 0,30 m od granicy), linię cienia daje **fryz wklęsły 0,15 m** pod gzymsem; wysięg 0,30 m tylko od dziedzińca. Świadome odstępstwo od E17 (0,5–0,9 m) – czytelność dają wysokość 0,70 m i fryz.
* **Wieża – wielki porządek:**
  * filary granitowe 1,05 m co **2,70 m**, ciągłe od +4,80 do +37,20 (32,4 m, smukłość 1 : 31);
  * okna **1,65 × 2,45 m** (dwuskrzydłowe, słupek w osi modułu, partycje w filarach lub słupkach; parapet 0,55 m z kwaterą stałą, nadproże 3,00 m, kaseta ZIP do 3,18 m pod stropem 3,32 m), **ościeże 0,45 m z blachy Al** (granit tylko na licu filara), płyciny z ciemnego metalu, WWR trzonu 40 %;
  * **kordon kwartału** (pas granitu +19,80–20,85 między filarami) w linii gzymsu skrzydła;
  * **kond. 6 – „kondygnacja cienia”:** szkło i metal 0,40 m za licem filarów, ciemne pasmo oddziela trzon od korony;
  * **korona S** (8,90 m): od pn. okno holu między filarami (kwatery 1,65 × 5,0 m); od pd. i zach. okna komisji i klubów 1,65 × 4,20 m, a nad nimi pas ceramicznych lameli maskujących wyrzutnie wentylacji (strona dziedzińca);
  * **attyka** 1,00 m z granitową czapą i cienką obróbką z ciemnego metalu – bez wysięgu poza lico (linia A, granica). Bez masztów i urządzeń na dachu; zwody niskie ≤ korony attyki, wyłaz płaski przy trzonie B.
* **Narożnik (łuk R 14):**
  * parter – podcień 3,0 m;
  * kond. 1–6 – **5 pasm** ceramiki 1,30 m z oknami wstęgowymi 2,45 m na łuku, jedyne poziome pasma w budynku („ruch mostu”);
  * korona – **pionowe lamele ceramiczne 0,35 × 0,60 m** (R 13,40–14,00) w rozstawach 1,35 / 0,675 m ułożonych w ciągu Fibonacciego (21 lameli na łuku, brak regularnego rytmu 0,5–1,0 m – E19), ton w ton (S 4005-Y20R + sitodruk ceramiczny 30 % na szkle; ΔL* ≈ 8), szkło na R 13,40; przesłonięcie 32 % w osi, pełne od 59°;
  * na stykach łuku z elewacjami prostymi masywne filary 2,2 m (SE) i 1,7 m (NW-pn.): pion trzyma poziom.
* **Segmentacja pierzei (DWKZ P8):** Mazowiecka **M1 12,15 | M2 16,20 (z bramą ogrodową 4,05 w pierwszych 3 modułach) | M3 16,20 | M4 12,15** + naroże NW 3,2 m (dziób R 3,5).
  * Posesje różnią się odcieniem ceramiki, reliefem filarów (0 / 0,08 / 0,15 / 0,08 m) i fakturą (gładka / ryflowana co 0,135 m / glazura cieniowana / ryflowana).
  * Fugi między posesjami: pionowa szczelina 0,20 m z ciemnego metalu cofnięta 0,15 m. Wspólne są cokół i gzyms. Faktura tylko dla M2 i M4 (najwyżej dwa narzędzia segmentacji naraz).
  * **M1 – przęsło przejściowe przy Maz. 19** (przeszczep K1): najbliższy kamienicy odcień, pierwsza oś cofnięta 0,30 m (fuga/uskok przy szczycie), gzyms w linii attyki nr 19 (rzędna 139,5–140,25 do potwierdzenia pomiarem), naświetle parteru w linii pasa 122,77. Piętra wyraźnie przesunięte względem jej stropów (o 1,0–1,2 m, reguła E07).
  * Wybrzeże: segment 10,55 m (5 osi kamienicznych) | elewacja wsch. wieży 15,7 m (wielki porządek) | łuk 22 m.
* **PV bez podwójnego liczenia (415 kWp):** BIPV jako pokrycie dachów za attyką (pola netto: wieża 948 m², skrzydło 685 m²) + BIPV w płycinach wieży od dziedzińca ≤ 25 m (82 m²) + **BIPV na ślepej ścianie pd. segmentu** (295 m², od dz. 10/2 – nie ulica, ≤ 25 m, szkło satynowane w tonie ceramiki w rysunku osi 2,025 m) + **zadaszenie tarasu ogrodowego** (80 m², elewacja dziedzińcowa). Od ulic i powyżej 25 m PV nie ma (MPZP § 6 pkt 13, WT § 216 ust. 8). BIPV: klasa ≥ B-s1,d0 w układzie NRO, wyłącznie ≤ 25 m. Dach zielony ma tylko taras segmentu (135 m², osobno).

**Przekrój elewacji 1:50 (warstwy od zewnątrz):**

| Typ | Warstwy (mm) | U [W/(m²K)] | Reakcja na ogień |
|---|---|---:|---|
| Filar wieży | granit 40 na kotwach ze stali nierdzewnej (nieodpadające ≥ 60 min) / pustka wentylowana 40 / wełna mineralna λ 0,033 – **260** / ściana-słup żelbet 300 | ≤ 0,15 | A1 (całość NRO) |
| Płycina wieży (≤ 25 m od dziedzińca BIPV) | panel Al 3 lub BIPV szkło-szkło 10 / pustka 40 / wełna **260** λ 0,033 / żelbet 200, **konsole nierdzewne z przekładką (ΔU 0,025)**; pas międzykondygnacyjny EI 60 0,80 m | **0,147** | A1 / BIPV ≥ B-s1,d0, NRO, tylko ≤ 25 m |
| Ściana skrzydła i segmentu | ceramika ekstrudowana 40 (od dziedzińca: tynk mineralny 10) / pustka 40 / wełna **240 λ 0,031** / żelbet 150; konsole nierdzewne punktowe (ΔU 0,020); razem 0,47 m | **0,144** | A1 / A2-s1,d0 |
| Okno | rama Al z przekładką termiczną, pakiet 3-szybowy 54 mm, kwatera dolna stała ze szkła bezpiecznego, roleta ZIP w nadprożu (≤ 25 m tkanina poliestrowa, > 25 m tkanina szklano-silikonowa A2-s1,d0), parapet zewn. Al, ościeże 450 (wieża) / 350 (skrzydło) z blachy Al na wełnie | Uw ≤ 0,80 | – |
| Korona – łuk | lamela ceramiczna 350 × 600 na ruszcie stalowym (R 13,40–14,00) / fasada słupowo-ryglowa 3-szybowa z sitodrukiem ceramicznym 30 % (R 13,40) | Ucw ≤ 0,90 | A1 / szkło |
| Dach wieży i skrzydła | BIPV szkło-szkło (BROOF(t1)) / membrana / spadki / wełna mineralna 300 / paroizolacja / płyta | ≤ 0,12 | NRO |

Powyżej 25 m wszystkie okładziny, mocowania i izolacje są niepalne. Podokienniki mają ≥ 1,10 m lub szkło bezpieczne stałe (WT § 301). Brak balkonów.

---

## 9. Zagospodarowanie terenu

* **Plac Mostowy (skwer 9/2, 355 m², bez kubatury):**
  * posadzka z granitu strzegomskiego; **ślad pierzei z 1934 r.** pasem granitu z listwą z brązu i tablicą z planem kwartału; **szpaler 4 lip drobnolistnych** wzdłuż śladu w zach. części skweru (skwer nie jest drogą pożarową);
  * okrągła ława przy łuku („okrągły element” przedmościa 1934);
  * taras bistro w zach. części (17,9 m głębokości), 20 stojaków rowerowych dla gości.
* **Ogród Województwa (dziedziniec, 1 563 m² niezabudowanego obszaru):**
  * **nieogrodzony**, dostępny z trzech stron: Hala (oś z mostu), brama ogrodowa (Mazowiecka), pas 4,6 m od bulwaru;
  * zachowane ogródki (490,6 m², w obszarze inwestycji 469,5 m²) – **ścieżki ogrodu prowadzone obrzeżem, poza poligonem ogródków** (w ogródkach tylko istniejące ścieżki i trawnik, bez korytowania i zmiany poziomu terenu – M.06 rozdz. 6); w ogródkach 28 drzew M.06: 19 zachowanych w miejscu, 1 przesadzane (nr 72), 8 martwych/zamierających (U) do decyzji arborysty, żadne nie jest usuwane kolizyjnie;
  * trawnik, **ogród deszczowy 140 m²**, ławki przy murze kamienic, mały plac zabaw (poza ogródkami) dla dzieci z sąsiednich kamienic, meble z drewna lokalnego; taras ogrodowy na stropie pasa −1 (nawierzchnia, bez nasadzeń) pod zadaszeniem BIPV wzdłuż elewacji pd. wieży;
  * ścieżki z cegły i gruzu z wykopu oraz z płyt na podbudowie przepuszczalnej.
* **Drzewa – bilans wg numeracji i położeń operatu M.06** (wiąże M.06 – Wyj. 13 odp. 65; położenia z wektorów załącznika graficznego, ±0,5–1 m; `_rewizja_drzewa.py`):
  * w obszarze inwestycji **44 drzewa** (gatunki drzewiaste M.06);
  * **usuwane kolizyjnie 8:** nr 1 i 2 (obszar A; nr 2 z hubiakiem), **nr 60 wierzba (Z2)** – 4,27 m od lica skrzydła i podziemia przy strefie 6,2 m (zachowanie wymagałoby cofnięcia skrzydła i utraty pokoi), nr 61 (Z3, 1,3 m od ściany szczelinowej), **nr 67 klon (Z1)** – 0,82 m od ściany −1, nr 79, 80, 81 śliwy (Z2) – w obrysie skrzydła; **przesadzana 1:** nr 72 (młoda jodła);
  * **usuwane sanitarnie (U – martwe lub zamierające), niezależnie od inwestycji, po ocenie arborysty: 10** (nr 5, 13, 18, 19, 20, 38, 53, 57, 59, 62);
  * **zachowane w miejscu 25**, w tym wszystkie pozostałe Z1 (3, 26, 46, 50, 58, 78, 89, 90) i Z2 (7, 10, 12, 14, 28); **nr 58 (Z1)** 5,45 m od lica −1 dzięki zwężeniu pasa −1 do 5,0 m; **nr 78 (Z1)** 2,99 m od ściany (wejście 0,11 m w strefę) – wygrodzenie korona + 1 m, odkrywki ręczne, nadzór arborysty;
  * zachowane **36 z 44 (82 %)** bez usunięć sanitarnych, **26 z 44 (59 %)** po nich;
  * **26 nowych drzew**: 4 lipy drobnolistne na skwerze (śladem pierzei, zamiast nr 1 i 2), 6 na Wybrzeżu po stronie rzeki (szpaler 6KDB/2, poza pasem roboczym drogi pożarowej), 2 w pasie 4,6 m od bulwaru, 14 w ogrodzie na gruncie rodzimym poza stropem garażu (klon polny 'Elsrijk', grab, lipa, wiąz – gatunki z rozdz. 7 M.06), w tym 8 nasadzeń zastępczych za drzewa usuwane kolizyjnie.
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
* **Zjazd do garażu:** wyłącznie z **Wybrzeża Słowackiego (6KDB/2)** przez segment. **Brama 4,0 m (v −0,40…−4,40), próg 119,10 w poziomie chodnika, samoczynna zapora przeciwpowodziowa do 120,30, rampa jednopasowa 3,50 m z sygnalizacją wahadłową**. Z 1KDG brak wjazdu, Mazowiecka bez wjazdów (zgodność z K-01/K-02: tunel i tramwaj).
* **Rowery:** 50 stanowisk w parterze z wjazdem od dziedzińca (przez pas od bulwaru lub bramę ogrodową) + 20 dla gości na skwerze + 10 przy bramie ogrodowej, w tym 4 dla rowerów cargo.
* **Drogi pożarowe:** dalszy pas jezdni Mazowieckiej (bliższa krawędź ok. 8,9–9,7 m od elewacji) i Wybrzeża Słowackiego (ok. 7,9–9,1 m od elewacji wieży, ok. 9 m od segmentu). Zabudowa pierzejowa, 100 % elewacji frontowej (rozp. MSWiA 2009 § 12 ust. 3). Między jezdnią a elewacjami nie ma drzew > 3 m. Plac manewrowy niepotrzebny (przejazd ulicami bez cofania).
* **Retencja 157 m³** (rozdz. 10): skrzynki rozsączające 60 m² × 1,15 m pod nawierzchnią przepuszczalną pasa 4,6 m pd. od segmentu (dno ≥ 117,45; 12,9 m od najbliższego drzewa). Nawierzchnie przepuszczalne 430 m², w tym ścieżki z cegły i gruzu z wykopu 550 m² (granit tylko skwer i wejścia, 500 m²).
* **Szyb wyjścia zapasowego MDS** (91,75; 32,00) – płaska klapa w trawniku, tunel 7,6 m do −1; poza ogródkami, 7,1 m od najbliższego drzewa.

---

## 10. Ekologia (liczby z `_bilans_energii.py` uruchomionego z danymi v1.1 przez `_rewizja_pv_ep.py`)

* **Budynek bezemisyjny** (EPBD 2024/1275, od 1.01.2028 dla budynków publicznych), bez spalania na działce. Agregat tylko awaryjny, na HVO.
* **Forma:** A/V ≈ 0,18 m⁻¹; elewacje 6 880 m² (0,49 m²/m² PC nadziemnej); WWR 37–40 %, szkło pełne tylko w koronie (262 m²); osłony ZIP na elewacjach E, S, W; ościeża 0,45 m w wieży. Przegrody: ściana U 0,144–0,147 (wełna 260 / 240 mm, konsole nierdzewne – `_rewizja_elewacje.py`), dach ≤ 0,12, okna ≤ 0,80.
* **Ciepło i chłód:** gruntowe pompy ciepła; dolne źródło: **58 sond × 91 m pod płytą −2** (siatka 6 × 6 m, dno 19,9 m n.p.m. ≤ 99,5 m p.p.t. – poza reżimem art. 86 PGiG) = 238 kW poboru + **ściany szczelinowe energetyczne** 4 230 m² (63 kW) + **36 pali energetycznych** (20 kW) = **321 kW** → moc grzewcza ok. **430 kW** (COP 4), chłód aktywny z gruntu ok. 330 kW + free cooling. Kolektory w warstwie podpłytowej, 2 przejścia przez białą wannę. **Szczyt chłodu ≈ 600 kW = GPC 330 kW + dry-cooler hybrydowy 2 × 150 kW** (kond. 4 segmentu, żaluzje w licu zach. od dziedzińca) + przesunięcie TABS. Nadwyżka ciepła gruntu 166 MWh/rok – dry-cooler, odzysk do c.w.u. i przepływ wód gruntowych (piaski połączone z Odrą). Sieć ciepłownicza tylko jako rezerwa/szczyt (≈ 0,3 MW). Odra jako źródło – odrzucona (`strategia_energetyczna.md`). TRT na 2 otworach próbnych.
* **Wentylacja:** 5 central piętrowych (25 m², strefa środkowa wieży, kond. 1–5; kond. 5 obsługuje też 6) + centrala parteru na kond. 1 (pas zach. wieży) + centrala Sejmiku na −1 przy trzonie B, rekuperacja ≥ 80 %, sterowanie CO₂. **Czerpnia zbiorcza:** 2 rzędy płycin (P/1 i 1/2) elewacji pd. wieży u 2–12 = 17 m² (≈ 1,25 m/s), wyłączone z BIPV. **Piony** 2,7 + 1,4 + 3,5 m²/kond. w strefie środkowej. **Wyrzutnia zbiorcza:** lamele w pasie nad komisjami w koronie od pd. (21 m w poziomie i ≈ 29 m w pionie od czerpni; w przestrzeni sufitowej nad komisjami wyłącznie kanały i plenum). Wentylatory oddymiania korytarzy w szachtach trzonów A i B. **Garaż:** wyrzut wentylacji i oddymiania oraz **spaliny agregatu** – szacht w trzonie B (miejsce po dźwigu T) do lameli korony od pd.; **powietrze agregatu** – żaluzje 8 m² w licu zach. segmentu (kond. 1); **wentylacja trafo** – kanałem do lica zach. segmentu; **bistro bez kuchni gorącej** (wyciąg z odzyskiem do instalacji ogólnej); czerpnie nadciśnienia klatek – elewacja pd. wieży (parter), ≥ 5 m od czerpni zbiorczej; filtrowentylacja ukrycia – czerpnia w lamelach korony. Nic na dachu ani na elewacjach od ulic i bulwaru.
* **PV 415 kWp, 328 MWh/rok:** dach wieży 204 kWp (179 MWh), dach skrzydła 147 kWp (116 MWh; cień wieży −11,6 %), płyciny wieży 11 kWp (5 MWh), ściana pd. segmentu 41 kWp (19 MWh), zadaszenie tarasu ogrodowego 13 kWp (9 MWh). Gęstość pola dachowego 0,215 kWp/m² (η ≥ 22,5 % × pokrycie 0,955 – warunek specyfikacji; przy η 21 % byłoby 391 kWp). Falowniki i rozdzielnice DC na kond. 2 segmentu (12 m²). Magazyn energii 100 kWh (v1.2; autokonsumpcja 0,80 w `_bilans_energii.py` bez zmian).
* **Bilans:** zużycie EPB ≈ 297 MWh/rok (23,9 kWh/(m²·rok)), całkowite ≈ 645 MWh/rok; **PV pokrywa 111 % EPB i 51 % całości**. Resztę daje społeczność energetyczna OZE Województwa (EPBD art. 11 ust. 7).
* **EP ≈ 28 kWh/(m²·rok)** (bez PV 60) wobec EPmax 95 (WT 2002) i progu ZEB 85 (projekt WT). Emisje operacyjne EPB 6,7 kg CO₂/(m²·rok) (próg ZEB 31,4).
* **Woda:** woda szara (804 m³/rok) i deszczowa (848 m³/rok) pokrywają **≈ 100 %** spłukiwania (zapas 0,4 % przy zbiorniku 50 m³ – D-11). Zużycie wody wodociągowej spada o **47 %** (1 600 m³/rok).
* **Retencja:** ψ śr. 0,67 → 0,62 (dachy BIPV są szczelne), Qdm(15 min, C = 10) 51 → 47 dm³/s przed retencją. Objętość opadu 60 min C = 10 z powierzchni zredukowanej: 70 m³. **Pojemność retencyjna 157 m³** (skrzynki rozsączające 66 m³ – dno ≥ 117,45, 1,0 m nad ZWG maks., wymiana nasypu pod skrzynkami; rezerwa 20 m³ zbiornika opróżniana pompą do skrzynek po 24 h; ogród deszczowy 42; dach niebieski 10; podbudowa 19) **daje zero odpływu do kanalizacji dla deszczu miarodajnego** – pod warunkiem k ≥ 1·10⁻⁶ m/s (badanie przed PB; inaczej dławik ≤ 2 dm³/s i hasło „odpływ ograniczony”). Przelew awaryjny działa dopiero przy przekroczeniu.
* **GWP ≤ 500 kg CO₂e/m² PC (A1–A5) – cel**; szacunek koncepcyjny ≈ 490 ± 120 (weryfikacja, D-12), dlatego CEM III/B w ścianach szczelinowych i płytach; LCA A–C od koncepcji. Sposoby: CEM III, stropy sprężone (−25 % betonu), podziemie tylko w zakresie wymaganym przez parking MPZP i MDS, kruszywo z gruzowych nasypów działki w betonach niekonstrukcyjnych i podbudowach (przeszczep K3), aluminium ≥ 75 % z recyklingu, granit lokalny (≈ 60 km), demontowalne panele ceramiczne (100 lat), stały moduł 1,35 i jednakowe pokoje (adaptowalność). Cel BREEAM Excellent.
* **Bioróżnorodność i mikroklimat:** ogród na pd. od budynku, 36 z 44 drzew zachowanych (M.06; 26 po usunięciach sanitarnych) + 26 nowych, ogród deszczowy, 24 budki dla jerzyków, ochrona ptaków na szkle korony, pnącza w strefie parteru ściany segmentu.
* **Mobilność:** 55 punktów ładowania EV (1/2), 80 miejsc rowerowych (50 + 30 dla gości), prysznice.

---

## 11. Dostępność (wyróżniki)

* **Wszystkie wejścia bez schodów i pochylni.** ±0,00 = 119,30, czyli poziom skweru i Wybrzeża (niwelacja chodnika ≤ 2 %). Dziedziniec przy drzwiach ogrodowych i rowerowni podniesiony do 119,25 i łagodnie (≤ 4 %) obniżony ku ogrodom, poza strefami korzeni. Brama ogrodowa w poziomie chodnika i ogrodu (spadek ≤ 2 %).
* **Oś Hali bez przeszkód** (szerokość ≥ 6 m). Ścieżki dotykowe od przystanków tramwajowych na przyczółku, od wejść i z garażu do informacji i dźwigów (przeszczep K4). Tyflomapy przy wejściach. Kontrast posadzek, ścian i drzwi. Niski blat informacji i kancelarii. Pętle indukcyjne: sala obrad, komisje, kluby, sale konferencyjne, kancelaria.
* **Komfortka 12 m²** (3,0 × 4,0 m) 14 m od wejścia głównego (WT § 85a). WC dostępne na każdej kondygnacji i w każdej strefie, także na −1 (sanitariaty MDS) i dla publiczności galerii (toaleta dostępna 5,7 m² przy holu P1/P2 na +30,90; rozdz. 7). **Pokój cichy** 16 m² przy Hali.
* **Sala obrad:**
  * prezydium i mównica na poziomie podłogi;
  * pochylnie ≤ 5 % do każdego rzędu, **stanowisko dla wózka w każdym rzędzie**;
  * 4 stanowiska radnych dla wózków (po jednym w rzędzie) + 3 miejsca dla wózków z opiekunami na galerii (dostęp P1/P2 bez stopni);
  * tłumacz PJM w kadrze, napisy na żywo.
* **Dwa publiczne dźwigi** (redundancja), 1 600 kg, kabiny 1,5 × 2,1 m (M.13), sygnalizacja głosowa i wizualna.
* **Ewakuacja OzN:** MOE 1,5 × 1,5 m z krzesłem ewakuacyjnym i interkomem do ochrony i KDR w przedsionkach klatek A (3,10 × 5,80 m), B (3,40 × 2,06 m), C (5,80 × 2,00 m) na każdej kondygnacji i w przedsionku A' na antresoli (poza drogą i polem otwierania drzwi). Dźwig ewakuacyjny R (PN-EN 81-76). Sygnalizatory optyczne alarmu w WC i przestrzeniach ogólnodostępnych.
* **Garaż:** 6 miejsc dla OzN 3,6 × 5,0 m przy trzonach A i B na −1, na posadzce (nie w stackerach); WC dostępne na −1. Pokój matki z dzieckiem na kondygnacji Sejmiku, przewijaki w WC holu i konferencji. Ogród bez barier dla mieszkańców.

---

## 12. Bilanse (PN-ISO 9836) i koszt

| Wskaźnik | Wartość |
|---|---|
| Powierzchnia zabudowy (PZ) | **2 165,8 m²** (58,1 % obszaru 3 728,7 m²) |
| PBC | ≈ **1 185 m²** (teren 1 117,5 m², w tym zachowane ogródki 469,5 m², + 50 % × 135,3 m² dachu zielonego tarasu) = 32 % |
| PC nadziemna | **14 392,7 m²** (P 2 005,8; kond. 1–4 po 2 162,9; kond. 5, 6, S po 1 145,8; **antresola S-3 297,9** – v1.1: 69,7 + rezerwa w koszcie do ≈ 180 m²) |
| PC podziemna | **4 365 m²** (−1: 2 263,9; −2: 2 101,3) |
| PC razem | **18 757,9 m²** (= podstawa wskaźnika zł/m² PC) |
| PU (PN-ISO 9836) | **8 871,47 m²** = 8 850,37 (suma pomieszczeń kategorii PU modelu pomieszczeń, F.15.A, F.15.C I.12; bez RU 4 342, US 590, PG 2 334) **+ 21,10 (S-3 wobec kondygnacji S w modelu: SWD +8,39, WC +7,25, PP.06 +5,46; antresola wnosi PU galerii, SWD.03, SWD.05 i toalety; `_v12_koszt.py` [K0])**; w tym pokoje 4 794, Sejmik 799, konferencje 362, strefa wejściowa 181, sale narad 360, socjalne 361, pomocnicze 1 130, WC 405, rowery 90, PPT 105, KS 96, inne 188 (model pomieszczeń do przeliczenia po v1.2) |
| PC nadziemna / PU | 1,62 (program 1,71) |
| Kubatura brutto (KW) | ≈ **81 400 m³** (wieża 42 162; skrzydło 17 423; segment 3 490; −1 9 508; −2 z płytą 8 825) |
| Miejsca postojowe | **110** (−1: 70 = 38 na posadzce + 32 w stackerach zależnych; −2: 40), w tym 6 OzN; **wymagane (MPZP § 13): 12/1 000 × (8 871,47 − 88,47) + 6/1 000 × 88,47 = 105,93 → 106** (odczyt ostrożny 108; bar SWD.05 liczony jak PU biurowe) ✔, zapas 4; 110 m.p. wystarcza do PU 9 210,9 m² (rezerwa 339 m²); trzon A v1.2 bez wpływu na garaż (`_rewizja_parking.py`, `_v12_trzony.py` [T6]) |
| Pokoje | 187 (179 × 24 + 8 × 32); pojemność elewacji 218 jedn. (43 × 4 + 22 + 20 + 4), zajęte ≈ 216 |
| MDS / budowla ochronna | MDS ≥ PU/15: v1.1 przyjęła 560 os. (= 8 400/15, PU szacunkowe v1.0); przy PU 8 871,47 m² wychodzi 8 871,47/15 = 591,4 → 592 os. – różnica 32 os. do rozstrzygnięcia (pojemność określa organ, art. 95a; rozdz. 16): **−2 ukrycie ≤ 300 os.** z filtrowentylacją, wyjścia klatkami A i B (środki 19,8 m); **−1 MDS 260 os.** – klatka C, rampa, szyb wyjścia zapasowego (91,75; 32,00) 12,6 m od wieży (≥ H/3) z tunelem 7,6 m; sanitariaty MDS 30 m² + WC ukrycia 15 m² |

**Koszt realizacji (netto, ceny II kw. 2026) – model F.14.B `tools/koszty_model.py`, poziom mid; v1.2 – `_v12_koszt.py`** (na bazie `_rewizja_koszt.py` v1.1; wejście modelu ze wszystkimi kluczami: `_rewizja_koszt_wejscie_v1_2.json`; ilości weryfikatora przyjęte: ościeża filarów wieży i okien skrzydła, pale CFA, ściana na uskoku, dry-cooler, przepusty GPC).
Parametry: A_nad 14 392,7 (z antresolą S-3 297,9 m²); A_pod 4 365; obrys podziemia 2 264; ściany szczelinowe 222,6 m × 19 m; wykop średnio 7,92 m; płyta zastępcza 1,00 m; obrys parteru 2 166; wypór poza obrysem 121,5 m²; 3 klatki × 9,0 kond. (klatka A do +30,90); 5 dźwigów osobowych + 1 towarowy; ceramika i metal 1 763 m²; tynk mineralny 410 m²; granit 1 663 m² (bez cokołu skrzydła i bez węgarów); okna 2 167 m²; fasady słupowo-ryglowe 410 m²; BIPV elewacyjne i zadaszenie 457 m²; lamele 240 m²; dachy 2 163 m² (taras intensywny 135,3); stal 73 t; PV dachowe 351 kWp; BESS 100 kWh; balustrady wewn. 130 mb; sondy 58 × 91 = 5 278 mb; teren 2 224 m² (granit 500, zieleń 630 + pielęgnacja ogródków 470); 26 drzew; 55 EV; ścianki mobilne 60 m².

| Grupa F.14.B | mln zł |
|---|---:|
| 1 Roboty przygotowawcze i ziemne (ściany szczelinowe 0,60 m, wykop, archeologia, monitoring sąsiadów) | 10,83 |
| 2 Przyłącza i sieci, GPC (58 × 91 m), PV dachowe 351 kWp | 8,57 |
| 3 Stan surowy (z garażem 4 365 m²) | 22,37 |
| 4 Stolarka zewnętrzna i fasady słupowo-ryglowe | 5,70 |
| 5 Stolarka wewnętrzna | 2,01 |
| 6 Elewacje (ceramika, tynk dziedzińcowy, granit, BIPV 457 m², lamele) | 7,31 |
| 7 Instalacje sanitarne i HVAC | 21,34 |
| 8 Instalacje elektryczne (BESS 100 kWh) | 12,32 |
| 9 Teletechnika i AV (głosowanie, transmisja, PJM) | 11,27 |
| 10 Dźwigi (5 + T) | 3,80 |
| 11 Wykończenie ścian, sala Sejmiku | 11,65 |
| 12 Sufity | 2,58 |
| 13 Posadzki | 4,59 |
| 14 Balustrady | 0,76 |
| 15 Zagospodarowanie terenu | 4,96 |
| 17 Woda szara | 0,70 |
| 18 MDS, zamurowanie okien Maz. 19 | 1,70 |
| **Roboty – model** | **132,46** |
| Pozycje spoza modelu (z rozbiciem w `_rewizja_koszt.py` i `_v12_koszt.py`): budowla ochronna 1,50; lapidarium 0,30; pale CFA 0,55; uskok −1/−2 0,14; iniekcja strumieniowa i podbicie Maz. 19 0,44; dry-cooler 0,45; GPC – wiercenie z dna, kolektory, absorbery ścian i pali 0,62; stackery 16 jedn. 1,12; zapora i sygnalizacja 0,16; szyb MDS 0,25; agregat w segmencie 0,11; ościeża Al wieży 0,54 i skrzydła 0,44; ścieżki 0,22; pielęgnacja ogródków 0,05; korekty: ściana 0,60 m −0,85, rampy jednopasowe −0,13; **v1.2:** trzon A wydłużony (I5) 0,03; klatki A i C trójbiegowe na −1/P i P/1 0,11; bez szybu C1 −0,03; biura z odsłoniętym TABS – wyspy akustyczne zamiast sufitu modułowego −0,43; ścianki szklane 10 → 8 % A −0,29 | 5,30 |
| 16 Koszty stałe budowy 3 % | 4,13 |
| **Roboty z kosztami stałymi** | **141,89** |
| 18.3 Rezerwa na nieprzewidziane (contingency) **5 %** (wymóg ≥ 4 %) | 7,09 |
| **Koszt realizacji z rezerwą** | **148,98 mln zł netto** |
| Zapas do limitu 150 mln | **1,02 mln (0,7 %)**; bufor łącznie z rezerwą 8,11 mln (5,7 % robót); przy rezerwie 4 % – 147,56 mln (zapas 2,44) |

**Dźwignie projektowe v1.1 (efekt w mln zł z KS i rezerwą, `_rewizja_koszt.py`):** ościeża wieży 0,60 m granit → 0,45 m blacha Al −1,80; ościeża skrzydła → blacha Al −0,58; ściany szczelinowe 0,80 → 0,60 m −0,91; dźwig C1 – szyb rezerwowy −0,65; elewacje dziedzińcowe skrzydła i segmentu – tynk mineralny −0,49; nawierzchnie: granit 1 050 → 500 m² −0,30; BESS 250 → 150 kWh −0,24; pole sond 58 × 91 m (+ ściany i pale energetyczne) −0,24; lapidarium 0,5 → 0,3 −0,22; ogródki – pielęgnacja zamiast nowej zieleni −0,20; lamele 450 → 240 m² −0,18; rampy jednopasowe −0,15; cokół skrzydła granit → ceramika −0,09. **v1.2 (`_v12_koszt.py`):** antresola S-3 ponad rezerwę v1.1 (+118,2 m² PC) +0,49; klatka A do +30,90 i balustrady +0,09; trzony I5 +0,12 → przed dźwigniami 149,87 mln (zapas 0,13). Dźwignie v1.2 – najpierw niewidoczne na planszach: **biura z odsłoniętym TABS** (rozdz. 4.2; pokoje 4 794 m² – wyspy akustyczne 0,35 m²/m² zamiast sufitu modułowego; korekta spójności modelu) −0,46; **ścianki szklane 10 → 8 % A** (pokoje od korytarza – GK z naświetlem; szkło w salach narad, sekretariatach, holach i strefie Sejmiku bez zmian) −0,31; **BESS 100 kWh** (rezerwowa v1.1) −0,12 → 148,98 mln, zapas 1,02 mln. Dźwignia rezerwowa niewykorzystana (widoczna na P7/W10): filary elewacji pd. wieży w ceramice −0,23.

**Wskaźniki (uczciwie, oba):** 148,98 mln / 18 757,9 m² PC = **7 942 zł/m² PC** – w paśmie porównywalnych budynków publicznych 7 400–9 300 zł/m² PC; **16 793 zł/m² PU** (PU 8 871 m²) – **powyżej** pasma B1/B2/B6 11 400–14 900 zł/m² PU (`koszty_benchmarki.md`), bo PC/PU = 2,11: dwie kondygnacje garażu–MDS (4 365 m² dla 110 m.p.), wysokie hole, sala Sejmiku i kondygnacja S. Porównanie z pasmem PC to **spójność z pasmem kalibracji stawek [Z] (nie jest niezależną kontrolą)**. Scenariusz low 109,4; high 207,4; waloryzacja +5 % (2027) od kosztu całkowitego: 156,4 mln (ryzyko opisane, F.14.B na poziomie cen II kw. 2026). Koszt Dokumentacji ≈ 7,6 mln zł netto (≤ 5,4 % = 8,1 mln), liczony osobno.

---

## 13. § 13 i § 60 WT wobec Wybrzeża Słowackiego 5 i Mazowieckiej 19 (dowody liczbowe)

**Dane:** szczyt pn. WS 5 (101,93; 28,52)–(118,16; 29,46), normalna 356,7°. Grubość muru 0,55 m: wierzchołek kąta leży w licu wewnętrznym na osi okna. Sektor 60° symetryczny (±30°). Okno pokoju nr 3 lok. 6/6A: (110,5; 29,0), parapet ≈ 124,0. Wariant najostrożniejszy: okno w dowolnym miejscu szczytu (e 102,4–117,7), a H liczone od najniżej położonych okien budynku (≈ 120,0, parter frontowy; § 13 ust. 2 literalnie). Zabudowa śródmiejska: odległości ½ (§ 13 ust. 4).

| Przeszkoda | Najwyższa krawędź | Wariant | H | Wymagane | Najmniejsza odległość w sektorze | **Zapas** |
|---|---|---|---:|---:|---:|---:|
| Segment SE (ściana pd. pełna) | attyka ściany pd. **139,10** (v1.1) | najostrożniejszy (okno w dowolnym miejscu, H od 120,0) | 19,10 | 9,55 | 11,13 (wierzchołek (116,69; 28,82)) | **1,58 m** ✔ (przy H od 119,2: 1,18 m) |
| Segment SE – balustrada szklana cofnięta 1,5 m | 140,20 | jw. | 20,20 | 10,10 | 12,63 | **2,53 m** ✔ |
| Segment SE | 139,10 | okno pokoju lok. 6/6A, H od parapetu 124,0 | 15,10 | 7,55 | 11,13 | **3,58 m** ✔ |
| Segment SE | 139,10 | okno pokoju, H od 120,0 | 19,10 | 9,55 | 11,13 | **1,58 m** ✔ |
| Wieża (> 35 m) | attyka 156,50 | dowolne okno szczytu | – | 17,50 | 19,00 (wierzchołek (102,51; 28,00)) | **1,50 m** ✔ |
| Wieża | 156,50 | okno pokoju lok. 6/6A | – | 17,50 | 20,46 | **2,96 m** ✔ |
| Skrzydło | 140,15 | – | – | – | poza sektorem | ✔ |

* **Wykładnia § 13 ust. 1 pkt 1 lit. b** (G-D-2): „obiekt przesłaniający” = część budynku o danej wysokości (analiza schodkowa – ust. 2 „przesłaniająca część”; `naslonecznienie_metoda.md` pkt 7); zapisana na P6.
* **§ 12:** ściana pd. segmentu bez otworów stoi 4,58 m od granicy dz. 10/2 (≥ 3 m); okładzina BIPV ściany nie tworzy otworów.
* **§ 271:** 10,58 m od ściany z oknami (≥ 8 m).
* Prywatność: biura nie mają okien na szczyt. Okna szczytu WS 5 pozostają czynne (zakaz zamurowania, Wyj. 3 odp. 13).

**§ 60 (1,5 h w każdym dniu równonocy, 7–17 czasu urzędowego):**
* **Lokal 6/6A** jest dwustronny. Pokoje 1 (25,0 m²) i 2 (15,0 m²) od wsch. mają słońce 7:00–11:50 (20.03, ≈ 4,9 h) i 7:00–12:35 (23.09, ≈ 5,7 h). Nasz budynek leży względem nich w azymutach ≈ 309–355°, poza drogą słońca (≈ 92–259°), więc ich nie zacienia. Okno szczytu (normalna 356,7°) nie dostaje słońca w równonoc niezależnie od projektu, dlatego rozstrzyga dla niego § 13 (spełniony).
* **Pokój 4 lokalu i elewacje podwórzowe WS 5–6** (zach.): skrzydło leży w azymutach ≈ 245–321° (z okna pokoju 4). Zacienia je od ok. 15:45–15:55 (20.03, CET) i 16:30–16:40 (23.09, CEST). Po realizacji okno ma ≈ 3,8 h słońca (stan istniejący 4,25 h), okna podwórzowe WS 6 ≥ 2,4 h – w obu dniach ≥ 1,5 h (§ 60). Pas 12 m przed elewacjami podwórzowymi pozostaje niezabudowany.
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
| **W7** | **Hol sali Sejmiku** | (82,097; 64,918; 28,90) przed drzwiami pn. dźwigów A1/A2 | (69,432; 68,315; 30,50), az. 285° | 20 mm, shift_y +0,05 | 29.10 16:20 CET | początek błękitnej godziny; pustka 2-kond. w narożu NW, okna na pl. Społeczny i wieże katedry, schody reprezentacyjne na antresolę radnych z barem, szatnia, wejście do sali, ludzie w rozmowie |
| **W8** | **Sala Sejmiku z galerią publiczności i jej oddzielnym wejściem** | (98,661; 72,970; 29,00) za 4. rzędem (≈ 11 m od mównicy) | (100,188; 60,373; 30,90), az. 173° | 20 mm, shift_y +0,08 | 22.10 10:30 CEST, sesja | prezydium przy pełnej ścianie z godłem, oświetlone dziennym światłem z łuku za kamerą; 47 stanowisk w 4 łukowych rzędach; po prawej galeria zach. z balustradą szklaną, publicznością i wejściem z korytarza publicznego (P1/P2); tłumacz PJM w kadrze; stanowisko radnego na wózku przy pochylni |
| W9 | Latarnia wieczorem z mostu (dod.) | (126,0; 152,0; 3,90) chodnik mostu | (96,0; 62,0; 26,0), az. 198° | 50 mm | 29.10 17:05 CET, sesja | błękitna godzina; korona świeci zza lamel, pierzeja spokojna, gzyms poniżej hełmów |
| W10 | Ogród Województwa (dod.) | (78,0; 17,0; 1,16) | (88,0; 45,0; 10,0), az. 20° | 24 mm, shift_y +0,12 | 22.10 13:30 CEST | mieszkańcy i pracownicy, drzewa ogródków, ogród deszczowy, wejście ogrodowe na końcu osi |
| W11 | Taras nad Oławą (dod.; 135 m² w attyce, ≈ 92 m² użytkowych) | (101,169; 41,570; 21,40) | (117,0; 73,7; 20,0), az. 26° | 24 mm | 22.10 14:30 CEST | przerwa pracowników, Oława, most, Ostrów Tumski |
| W12 | Aksonometria „kwartał 1934 / projekt” (dod.) | rzut aksonometryczny od SE | – | – | dzień, światło rozproszone | dawna linia pierzei na skwerze, łuk 1934 vs łuk projektu, posesje |

---

## 15. Narracja 8 plansz i część opisowa

**Hierarchia:** 1) idea Bramy i Latarni; 2) kwartał domknięty w skali kamienic; 3) Sejmik bezbłędny prawnie i dostępny; 4) liczby (koszt, ZEB, § 13).

| Plansza | Zawartość | Dominanta |
|---|---|---|
| **P1** | Hasło + idea (≤ 60 słów), **W1 (F.17.A)** na 60 % planszy, zagospodarowanie 1:500 z cieniami SW 45°, schemat „1934 / projekt” | W1 |
| **P2** | **W3** (Brama Mostowa z mostem), **W2 (F.17.B)**, aksonometria funkcji (Brama → oś → ogród; Latarnia), schemat ruchu radni / publiczność / dostawy | W3 |
| **P3** | Rzut parteru 1:200 z otoczeniem i ogrodem, rzuty −1 i −2 1:200 (garaż 110 m.p. z oznaczeniem stackerów i OzN, MDS z wyjściami, ukrycie, technika), dostępność: legenda | rzut P |
| **P4** | Rzuty kond. 1 (charakterystyczna, z analizą § 13 na rzucie) i 2–4 1:200, moduł 1,35 / pokój 24,1 m², tabela departamentów | rzut 1 |
| **P5** | Rzuty kond. 5, 6, **S z antresolą** 1:200, tabela pomieszczeń Sejmiku (rozdz. 7.1) i dowód „całość w A”, rzut dachu (BIPV) | rzut S |
| **P6** | Przekroje A-A (pn.–pd. przez łuk i segment z WS 5) i B-B (wsch.–zach. przez salę i skrzydło) 1:200 z ZWG i stropem glin; analiza przesłaniania i nasłonecznienia (§ 13 – tabela rozdz. 13); schemat ppoż. i dostępności | przekroje |
| **P7** | Elewacje 1:200: Mazowiecka z Maz. 19, Wybrzeże z WS 5, pn. od skweru, pd. od ogrodu; przekrój elewacyjny + fragment 1:50 (wieża i skrzydło); **W4, W5** | elewacja Mazowiecka |
| **P8** | **W6, W7, W8** (wnętrza), schemat proekologiczny (GPC 58 × 91 m + ściany i pale energetyczne, BIPV 415 kWp, dry-cooler, woda, retencja 157 m³, GWP), pasek KPI: EP 28 · PV 415 kWp / 111 % EPB · 110 m.p. · 149,0 mln | W8 |

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
   * antresola otwarta (26 % rzutu; galeria publiczności oddzielona od antresoli radnych);
   * prezydium przy pełnej ścianie;
   * pochylnie ≤ 5 %;
   * publiczność z osobnym wejściem.
6. **Dostępność:** wyróżniki z rozdz. 11.
7. **Konstrukcja i grunt:** ściany szczelinowe 0,60 m do glin (energetyczne), iniekcja strumieniowa z podbiciem przy Maz. 19, biała wanna, płyta palowo-fundamentowa, stropy sprężone 14,2 m, brak odwodnienia regionalnego, zapora samoczynna w bramie.
8. **Ppoż.:**
   * budynek W, klasa B;
   * strefy ≤ 2 500 m²;
   * 3 klatki z przedsionkami i nadciśnieniem;
   * dźwig R;
   * SSP, DSO, oddymianie korytarzy i garażu (tryskacze nieobowiązkowe – nieprojektowane);
   * drogi pożarowe z ulic;
   * elewacje > 25 m niepalne.
9. **Ekologia:** EP 28, PV 415 kWp (dachy 351 + ściana segmentu, płyciny, zadaszenie – bez podwójnego liczenia), GPC 58 × 91 m + ściany i pale energetyczne, dry-cooler od dziedzińca, woda −47 %, retencja 157 m³, GWP ≤ 500 (cel; szacunek ≈ 490), zieleń.
10. **Zagospodarowanie:** Plac Mostowy ze śladem 1934 i lipami, Ogród Województwa, drzewa wg M.06: 36/44 zachowanych (26 po usunięciach sanitarnych), 8 usuwanych kolizyjnie, 26 nowych.
11. **Prawo:** MPZP (tabela rozdz. 4.3), § 13 / § 60 (rozdz. 13), WT 2002 + projekt WT, budowla ochronna (art. 93).
12. **Koszt:** F.14.B 149,0 mln (148,98; rezerwa 5 % w środku, zapas 1,0 mln), 7 942 zł/m² PC i 16 793 zł/m² PU z pasmami, dźwignie, koszt Dokumentacji ≈ 7,6 mln.

---

## 16. Ryzyka resztkowe

1. **Linia A z rastra 1:1000 (±0,3 m).** Lica wieży leżą na liniach A (bez żadnego wysięgu), a skrzydła i segmentu 4–5 cm poza nimi. Potrzebny pomiar geodezyjny, korekta lic bez zmiany układu.
2. **Wykładnia antresoli (S-3):** 297,9 m² (26 % rzutu), otwarta na salę i pustkę holu; zamknięte tylko toaleta publiczności 5,7 m², przedsionek A' i korytarz EI 30 (dojścia) – wszystkie pomieszczenia programu na poziomie S; przedstawić jako uzgodnienie z rzeczoznawcą ppoż.
3. **§ 13 dla własnych pokoi w narożach wklęsłych** – jednostki w narożu segment/wieża są pomieszczeniami pomocniczymi; pojemność kond. 5–6 (21/22 i 20/20 j.) nie ma rezerwy, a druga sala spotkań KS ma doświetlenie pośrednie (P-I8 – uzgodnienie z PWIS).
4. **BIPV jako pokrycie** wobec MPZP § 6 pkt 13 (K-05) wymaga zgodnej interpretacji organu. Minimum 400 kWp wymaga modułów η ≥ 22,5 % (przy 21 % – 391 kWp) oraz BIPV na ścianie segmentu i zadaszeniu ogrodowym.
5. **Budżet:** 148,98 mln z rezerwą 5 % (7,09 mln) i zapasem 1,02 mln; przy rezerwie 4 % zapas 2,44 mln; waloryzacja do 2027 r. +5 % (156,4 mln – opis w części opisowej). Dźwignia rezerwowa niewykorzystana: filary pd. wieży w ceramice −0,23 mln. Pozycje [Z] do weryfikacji ofertowej: ściany szczelinowe, AV, stackery, iniekcja strumieniowa.
6. **Woda gruntowa i archeologia** (relikty piwnic) wpływają na harmonogram podziemia.
7. **Budowla ochronna:** kategoria i pojemność zależą od postanowienia Prezydenta Miasta (art. 95a).
8. **Okna szczytu WS 5 na piętrach 2–4:** przyjęto wariant najostrożniejszy, pomiar przy wizji.
9. **Przebudowa przyczółka** (tramwaj, tunel; K-01, K-02): wibroizolacja sali obrad, izolacyjność elewacji pn. i zach.
10. **Parking:** 110 m.p. wobec 106 wymaganych (ostrożnie 108) przy PU 8 871 m² – zapas 4; 32 miejsca w stackerach zależnych (przydział parami, eksploatacja i serwis); wzrost PU o > 339 m² wymagałby dodatkowych stanowisk.
11. **Maz. 19:** podbicie fundamentu szczytu iniekcją strumieniową wymaga zgody właściciela/zarządcy (art. 47 Pb) i odkrywek; bez zgody – kolumny tylko po naszej stronie granicy i monitoring.
12. **Zajęcie pasa drogowego** Mazowieckiej na ściany prowadzące (zezwolenie ZDiUM) – harmonogram robót podziemnych.
13. **Retencja zero odpływu** zależy od współczynnika filtracji (badanie k przed PB); wariant zapasowy – dławik ≤ 2 dm³/s.
14. **Klatki – M.13 pkt 6** mierzy bieg 1,60 m między wewnętrznymi krawędziami poręczy: przy klatkach 3,40 m (2 × 1,60 + 0,20) i pochwytach obustronnych w świetle ≈ 1,46 m; pełna zgodność wymaga ≈ 3,69 m (A – możliwa kosztem przedsionka 3,10 → 2,81 m; B – brak 0,29 m w obrysie) albo pochwytów we wnękach ścian trzonu (brak ≈ 0,05 m) – do uzgodnienia (`_v12_trzony.py` [T7]).
15. **Ewakuacja S bez tryskaczy:** trzy dojścia jednokierunkowe (10,2 / 13,9 / 14,1 m) mieszczą się w 15 m tylko przy zwiększeniu +50 % za samoczynne oddymianie kuluaru i korytarza publicznego (§ 256 ust. 3) – potwierdzić z rzeczoznawcą; alternatywa: tryskacze w strefie S.
16. **MDS:** pojemność 560 os. (300 + 260) przyjęta w v1.1 z PU 8 400 m²; przy PU 8 871 m² art. 94 daje 592 os. (+32) – zwiększyć MDS −1 albo przyjąć pojemność z postanowienia organu (art. 95a). **Ukrycie −2 (≤ 300 os.):** środki klatek A i B 19,8 m, obudowy 13,95 m (po I5; v1.1 model pomieszczeń 15,58 m) – sposób pomiaru „2 klatki ≥ 15 m” (rozp. 2025 poz. 932 § 6) do potwierdzenia; alternatywa: szyb awaryjny z −2.
17. **Holy windowe na kondygnacjach biurowych:** A1/A2 (drzwi pn. wg S-3) 2,15 m i P1/P2 2,20 m (WT § 195 ✔, M.13 3,6 m ✗ – świadome odstępstwo); kuluar S przy trzonie A 1,75 m (M.13 1,80 m).
