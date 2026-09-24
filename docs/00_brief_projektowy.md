# Brief projektowy — „Dom LAMELA” (dom jednorodzinny wolnostojący)

Status: wersja robocza 0.1 (2026-09-25). Dokument wejściowy dla wszystkich etapów. Wartości oznaczone **[DO WERYFIKACJI]**
muszą zostać potwierdzone w rejestrze wymagań prawnych (`docs/10_podstawy_prawne/`) przed użyciem w projekcie.

## 1. Materiał wejściowy
* `00_wejscie/szkic_koncepcyjny.jpg` — szkic odręczny na serwetce (widok elewacji).
* `00_wejscie/interpretacja_szkicu.png` — interpretacja: warstwy A–E.

### 1.1 Odczyt szkicu (współrzędne w px wycinka 1770×690 z oryginału, x→prawo, y→dół)
| Element | zakres x [px] | zakres y [px] | interpretacja |
|---|---|---|---|
| Linia terenu | 45…1700 | 635 → 605 | teren niemal płaski, lekko wznoszący się ku wschodowi (prawo) |
| E – parter, przeszklenie 5 kwater | 545…1105 (podziały: 545, 625, 715, 835, 950, 1105) | 505…625 | ciągłe przeszklenie strefy dziennej |
| E – płyta dachu parteru | 430…1145 | ≈500 | płyta wysunięta ok. 1,5 m poza lico na zachód i ok. 0,9 m na wschód |
| B – bryła I piętra | 500…1050 | 240…500 | bryła pełna; lewa krawędź to ściana/słup w x=500 |
| C – boks przeszklony (3 kwatery) | 705…1035; rama górna 680…1130 | 295…405 | przeszklony „wykusz/rama” na I piętrze |
| D – linia pozioma | 675…1370 | ≈405 | krawędź stropu nad parterem pod boksem C, biegnąca na wschód nad garażem (v2) |
| D – pion | ≈1378 | 370…590 | wschodni narożnik bryły garażu do terenu (v2) |
| A – bryła II piętra z lamelami | 455…1060; płyta 390…1075 | 80…200 (płyta 185…240) | długa bryła z pionowymi lamelami, wspornik na zachód |

Skala pozioma: bryła B (500…1050 px) ≈ 12,0 m ⇒ ≈ 45,8 px/m. W tej skali: bryła A ≈ 13,2 m (wspornik ≈ 1,0 m na zachód,
płyta ≈ 2,4 m), przeszklenie parteru ≈ 12,2 m (od +1,0 m do +13,2 m względem lica zach. bryły B), boks C ≈ 7,2 m (od +4,5 do +11,7 m),
pion D w odległości ≈ 19,0 m od lica zach. bryły B ⇒ między ścianą wsch. części mieszkalnej parteru a pionem D ≈ 5,5–6,0 m — **garaż na 2 samochody** (wg interpretacji v2).

Proporcje pionowe szkicu są umowne (pasmo B jest ~2× wyższe od pasm A i E) — wysokości przyjmujemy wg wymagań WT i racjonalnej
konstrukcji; zachowujemy natomiast: 3 pasma, przesunięcia brył, wysunięcia płyt, rytm kwater, położenie linii D i narożnika garażu (v2).

### 1.2 Przyjęta interpretacja — WERSJA 2 (po decyzji Inwestora z 25.09.2026, obowiązująca)
Decyzje Inwestora: (1) **„elewacja w S-kę” — kształt S tworzą same przesunięte bryły** (bez osobnej wstęgi/ramy);
(2) element D **nie jest płytą tarasową** (brak tarasu nad garażem); (3) krawędzie płyt **głęboko wysunięte 0,8–1,2 m**
(czytelne poziome warstwy, okapy i osłony przeciwsłoneczne); (4) **garaż 2-stanowiskowy w bryle parteru**.
Grafika: `00_wejscie/interpretacja_szkicu_v2.png`.
* 3 kondygnacje nadziemne, bez podpiwniczenia, dachy płaskie (stropodachy).
* Sylweta elewacji południowej to rytm przesunięć **zachód – wschód – zachód**, tworzący „S”:
  * **A — II piętro (P2)**: długa bryła w pionowych lamelach, przesunięta na ZACHÓD (wspornik ≈ 1,0 m poza lico bryły B,
    płyta stropu/dachu wysunięta dalej, ≈ 0,8–1,2 m poza lico bryły A);
  * **B — I piętro (P1)**: bryła pełna, cofnięta od zachodu i przesunięta na WSCHÓD, z **C — przeszklonym boksem w ramie**
    (3 kwatery, ≈ 7 m), rama wysunięta ≈ 0,8–1,2 m;
  * **G — garaż 2-stanowiskowy** w bryle parteru na WSCHODZIE (od lica wsch. części mieszkalnej do x ≈ 19 m od lica zach. bryły B);
    linia D ze szkicu = krawędź stropu nad parterem biegnąca na wschód i kończąca się narożnikiem garażu (pion do terenu = ściana
    wschodnia garażu). **Dach garażu nieużytkowy** (np. dach zielony ekstensywny), bez tarasu;
  * **E — parter (P0)**: przeszklona strefa dzienna (≈ 12 m, 5 kwater) przesunięta na ZACHÓD, płyta dachu wysunięta
    ≈ 1,5 m na zachód i ≈ 0,8–1,2 m na południe (okap zacieniający przeszklenie latem).
* Elewacja ze szkicu = **elewacja ogrodowa, południowa**. Dojazd od północy (droga gminna); brama garażowa od północy
  (lub od wschodu, jeśli pozwalają odległości); wejście główne zadaszone od północy.
* Pionowe proporcje szkicu są umowne — poziomy kondygnacji wg WT; stropy nad parterem części mieszkalnej i garażu na tym
  samym poziomie konstrukcyjnym (racjonalność), różnice wysokości w szkicu oddajemy grubością/wysunięciem krawędzi płyt.
* ~~Interpretacja v1 (płyta D jako taras nad wiatą na słupie)~~ — **odrzucona przez Inwestora**.

## 2. Przyjęta działka (przykładowa, fikcyjna) **[parametry do potwierdzenia w koncepcji]**
* Lokalizacja: strefa podmiejska Poznania, woj. wielkopolskie (dane klimatyczne i obciążenia: Poznań). Nazwy, numery i uchwała — fikcyjne.
* Działka nr 123/4, obręb 0005 „Przykładowo”, gm. Przykładowo; prostokąt **32,00 m (front od drogi) × 50,00 m = 1600 m²**.
* Droga dojazdowa gminna od północy — ul. Lipowa (fikcyjna), klasa D, w liniach rozgraniczających 10 m, symbol planu 1KDD.
* Sąsiedzi: wschód i zachód — działki MN z budynkami jednorodzinnymi (≥ 8 m od granicy); południe — teren zieleni/rolny.
* Teren: spadek ok. 0,6 % ku południu, ok. 0,5 % wzniesienie ku wschodowi. Rzędne narożników (PL-EVRF2007-NH):
  NW 101,40; NE 101,55; SW 101,10; SE 101,25. ±0,00 ≈ 101,65 m n.p.m. (≈ 0,30 m ponad średni teren pod budynkiem).
* Grunt (opinia geotechniczna — przykładowa): 0,0–0,4 m ziemia urodzajna; poniżej piaski średnie, średniozagęszczone (I_D ≈ 0,6),
  zwierciadło wody gruntowej ≈ 3,8 m p.p.t.; warunki proste, **I kategoria geotechniczna** [DO WERYFIKACJI kryteria].
* Uzbrojenie w drodze: wodociąg PE 110, kanalizacja sanitarna PVC 200, sieć nN 0,4 kV (złącze kablowo-pomiarowe w linii ogrodzenia),
  światłowód; sieć gazowa istnieje, ale **nie jest wykorzystywana** (dom all-electric); brak kanalizacji deszczowej ⇒ retencja i rozsączanie na działce.
* Strefy obciążeń (Poznań) [DO WERYFIKACJI]: śnieg strefa 1 (s_k = 0,7 kN/m²), wiatr strefa 1 (v_b,0 = 22 m/s), teren kat. III,
  głębokość przemarzania h_z = 0,8 m, projektowa temp. zewnętrzna θ_e = −18 °C (III? II? strefa klimatyczna — zweryfikować).

## 3. Przyjęty MPZP (fikcyjny, oparty na typowych zapisach) **[do finalizacji w koncepcji]**
Uchwała nr XII/123/2024 Rady Gminy Przykładowo z dnia 21.03.2024 r. — teren **3MN** (zabudowa mieszkaniowa jednorodzinna wolnostojąca):
* nieprzekraczalna linia zabudowy: 6,0 m od linii rozgraniczającej drogi 1KDD;
* maks. powierzchnia zabudowy: 30 % powierzchni działki; min. powierzchnia biologicznie czynna: 50 %;
* intensywność zabudowy: 0,05–0,80;
* wysokość budynku mieszkalnego: do 11,0 m; do 3 kondygnacji nadziemnych; dachy płaskie o spadku do 12° lub strome 30–45°;
* min. 2 miejsca postojowe na 1 lokal mieszkalny (wliczając miejsca w garażu/wiacie);
* kolorystyka elewacji: biele, szarości, grafit, naturalne drewno, beton architektoniczny;
* wody opadowe: zagospodarowanie w granicach działki (retencja, rozsączanie); zakaz odprowadzania na drogę;
* ogrzewanie: źródła niskoemisyjne/OZE; ogrodzenie od drogi ażurowe, wys. ≤ 1,60 m, bez prefabrykatów betonowych;
* min. powierzchnia nowo wydzielanej działki 1000 m²; brak ochrony konserwatorskiej; poza terenami górniczymi i zalewowymi.

## 4. Program użytkowy (rodzina 4–5 osób, standard podwyższony)
* **P0**: wiatrołap, hol ze schodami, WC gościnne, garderoba/szafa wejściowa, kuchnia z wyspą + spiżarnia, jadalnia, salon
  (przeszklenie na ogród, wyjście na taras), pokój gościnny/gabinet z dostępem do łazienki (pokój na parterze dla gościa/seniora),
  pomieszczenie techniczne (pompa ciepła — jednostka wew./zasobnik CWU, rozdzielnica, przyłącze wody), **garaż 2-stanowiskowy**
  (wymiary w świetle ≥ 5,6 × 6,0 m, brama segmentowa, połączenie z domem przez przedsionek/strefę gospodarczą, miejsce na rowery
  i sprzęt ogrodowy).
* **P1**: hol, 2 pokoje dzieci (każdy ≥ 12 m²), łazienka, pralnia, pokój rodzinny/biblioteka w przeszklonym boksie C (bez tarasu nad garażem).
* **P2**: sypialnia główna z garderobą i łazienką (apartament rodziców), gabinet/pokój, pomieszczenie techniczne rekuperacji
  (lub w P0 — decyzja projektowa), wyjście na dach techniczny (PV) — klapa/wyłaz.
* **Zewnątrz**: 1–2 miejsca gościnne na podjeździe przed garażem, taras ogrodowy przy salonie, miejsce na pojemniki na odpady,
  zbiornik retencyjny wód opadowych + skrzynki rozsączające, ogród, zieleń izolacyjna, ogrodzenie z bramą przesuwną i furtką.
* Docelowa powierzchnia użytkowa: ok. 230–270 m² (weryfikacja racjonalności — nie przewymiarować).

## 5. Wymagania projektowe (skrót, [DO WERYFIKACJI w rejestrze wymagań])
* Pokoje przeznaczone na pobyt ludzi: wysokość w świetle ≥ 2,50 m; pomieszczenia pomocnicze ≥ 2,20 m; okna ≥ 1/8 pow. podłogi.
* Pokój w mieszkaniu ≥ 8 m² (pokój dzienny ≥ 16 m² w mieszkaniu wielopokojowym); kuchnia z oknem.
* Schody wewnętrzne w budynku jednorodzinnym: szer. biegu ≥ 0,80 m, spocznika ≥ 0,80 m, wys. stopnia ≤ 0,19 m, 2h+s = 0,60–0,65 m;
  balustrady; tu przyjąć komfortowe: bieg ≥ 1,00 m, h ≈ 0,175 m, s ≈ 0,28 m.
* Odległości od granic działki: ściana z oknami/drzwiami ≥ 4,0 m; bez otworów ≥ 3,0 m.
* Izolacyjność cieplna (WT 2021): ściany zewn. U ≤ 0,20; stropodachy U ≤ 0,15; podłoga na gruncie U ≤ 0,30; okna U ≤ 0,9;
  drzwi zewn. U ≤ 1,3 W/(m²·K); EP ≤ 70 kWh/(m²·rok); ograniczenie A0max i g_c ≤ 0,35 dla dużych przeszkleń (wyjątek N).
* Balustrady: wysokość i prześwity wg WT (balkony/tarasy 1,10 m; schody w domu jednorodzinnym — zweryfikować).
* Wentylacja: mechaniczna nawiewno-wywiewna z odzyskiem ciepła; strumienie wg PN-83/B-03430/Az3:2000 [DO WERYFIKACJI].
* Pożar: budynek ZL IV, klasa odporności pożarowej wg § 212–213 WT (dla jednorodzinnych do 3 kondygnacji) [DO WERYFIKACJI].
* PV: moc ≤ 6,5 kW — bez uzgodnienia z rzeczoznawcą ppoż. (art. 56 ust. 1a Prawa budowlanego) [DO WERYFIKACJI].

## 6. Założenia konstrukcyjno-materiałowe (wstępne — do rozstrzygnięcia w PT)
* Ściany nośne murowane (np. bloczki silikatowe 18/24 cm) + ETICS (EPS grafitowy / wełna), stropy żelbetowe monolityczne,
  wsporniki (bryła P2, wysunięte krawędzie płyt 0,8–1,5 m, rama boksu C) — żelbet z łącznikami termoizolacyjnymi; posadowienie bezpośrednie
  (ławy lub płyta fundamentowa — rozstrzygnąć wielowariantowo). Stolarka aluminiowa/PVC z szybą 3-szybową, osłony zewnętrzne.
* Instalacje: pompa ciepła powietrze–woda + ogrzewanie podłogowe, CWU z zasobnika, rekuperacja, PV ≤ 6,5 kWp,
  instalacja elektryczna TN-S, przyłącze nN kablowe, woda z sieci, ścieki do sieci, deszczówka — retencja + rozsączanie.

## 7. Zasady pracy (obowiązują wszystkie etapy)
1. **Jedno źródło prawdy**: `model/budynek.yaml` + `model/dzialka.yaml` (schemat: `docs/SCHEMAT_MODELU.md`). Rysunki, model 3D,
   obliczenia, zestawienia i opisy są GENEROWANE z modelu — żadnych wartości wpisywanych ręcznie, które mogłyby się rozjechać.
2. Każde stwierdzenie normatywne w części opisowej ma podane źródło (akt prawny z Dz.U. i paragrafem / norma z numerem i rokiem).
3. Język dokumentacji: polski. Jednostki SI, wymiary na rysunkach w cm / rzędne w m (zgodnie z PN-B-01029).
4. Dane osobowe projektantów, numery uprawnień, podpisy — **pola do uzupełnienia** (nie wolno fabrykować danych rzeczywistych osób).
