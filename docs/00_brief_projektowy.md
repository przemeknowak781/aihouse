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
| D – płyta pozioma | 675…1370 | ≈405 | płyta na poziomie posadzki boksu C, wysunięta na wschód do słupa |
| D – słup | ≈1378 | 370…590 | smukły słup do terenu (podpora płyty D) |
| A – bryła II piętra z lamelami | 455…1060; płyta 390…1075 | 80…200 (płyta 185…240) | długa bryła z pionowymi lamelami, wspornik na zachód |

Skala pozioma: bryła B (500…1050 px) ≈ 12,0 m ⇒ ≈ 45,8 px/m. W tej skali: bryła A ≈ 13,2 m (wspornik ≈ 1,0 m na zachód,
płyta ≈ 2,4 m), przeszklenie parteru ≈ 12,2 m (od +1,0 m do +13,2 m względem lica zach. bryły B), boks C ≈ 7,2 m (od +4,5 do +11,7 m),
słup D w odległości ≈ 19,0 m od lica zach. bryły B ⇒ pod płytą D między ścianą wsch. parteru a słupem ≈ 5,5–6,0 m — **wiata na 2 samochody**.

Proporcje pionowe szkicu są umowne (pasmo B jest ~2× wyższe od pasm A i E) — wysokości przyjmujemy wg wymagań WT i racjonalnej
konstrukcji; zachowujemy natomiast: 3 pasma, przesunięcia brył, wysunięcia płyt, rytm kwater, położenie płyty D i słupa.

### 1.2 Przyjęta interpretacja (do rozwinięcia w koncepcji)
* 3 kondygnacje nadziemne, bez podpiwniczenia, dachy płaskie (stropodachy), układ „przesuniętych brył”.
* **Parter (P0)** — strefa dzienna otwarta na ogród (południe), pełne przeszklenie elewacji ogrodowej, płyta dachu parteru wysunięta
  (okap/zadaszenie tarasu, osłona przed słońcem letnim).
* **I piętro (P1)** — bryła pełna, cofnięta; przeszklony boks C (np. pokój rodzinny/biblioteka) z wyjściem na **taras na płycie D**,
  która na wschodzie przechodzi w zadaszenie **wiaty garażowej na 2 samochody** podpartej smukłymi słupami.
* **II piętro (P2)** — długa bryła obłożona pionowymi lamelami (prywatność, osłona przeciwsłoneczna), wspornik na zachód.
* Elewacja ze szkicu = **elewacja ogrodowa, południowa**. Dojazd od północy (droga gminna), wiata po stronie wschodniej.

## 2. Przyjęta działka (przykładowa, fikcyjna) **[parametry do potwierdzenia w koncepcji]**
* Lokalizacja: strefa podmiejska Poznania, woj. wielkopolskie (dane klimatyczne i obciążenia: Poznań). Nazwy, numery i uchwała — fikcyjne.
* Działka nr 123/4, obręb 0005 „Przykładowo”, gm. Przykładowo; prostokąt **30,00 m (front od drogi) × 50,00 m = 1500 m²**.
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
  pomieszczenie techniczne (pompa ciepła — jednostka wew./zasobnik CWU, rozdzielnica, przyłącze wody), schowek ogrodowo-rowerowy
  od strony wiaty (dostęp z zewnątrz).
* **P1**: hol, 2 pokoje dzieci (każdy ≥ 12 m²), łazienka, pralnia, pokój rodzinny/biblioteka w przeszklonym boksie z wyjściem na taras nad wiatą.
* **P2**: sypialnia główna z garderobą i łazienką (apartament rodziców), gabinet/pokój, pomieszczenie techniczne rekuperacji
  (lub w P0 — decyzja projektowa), wyjście na dach techniczny (PV) — klapa/wyłaz.
* **Zewnątrz**: wiata na 2 samochody (pod płytą D), 1 miejsce gościnne, taras ogrodowy przy salonie, miejsce na pojemniki na odpady,
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
  wsporniki (bryła P2, płyta D, okapy) — żelbet z łącznikami termoizolacyjnymi; słupy wiaty stalowe; posadowienie bezpośrednie
  (ławy lub płyta fundamentowa — rozstrzygnąć wielowariantowo). Stolarka aluminiowa/PVC z szybą 3-szybową, osłony zewnętrzne.
* Instalacje: pompa ciepła powietrze–woda + ogrzewanie podłogowe, CWU z zasobnika, rekuperacja, PV ≤ 6,5 kWp,
  instalacja elektryczna TN-S, przyłącze nN kablowe, woda z sieci, ścieki do sieci, deszczówka — retencja + rozsączanie.

## 7. Zasady pracy (obowiązują wszystkie etapy)
1. **Jedno źródło prawdy**: `model/budynek.yaml` + `model/dzialka.yaml` (schemat: `docs/SCHEMAT_MODELU.md`). Rysunki, model 3D,
   obliczenia, zestawienia i opisy są GENEROWANE z modelu — żadnych wartości wpisywanych ręcznie, które mogłyby się rozjechać.
2. Każde stwierdzenie normatywne w części opisowej ma podane źródło (akt prawny z Dz.U. i paragrafem / norma z numerem i rokiem).
3. Język dokumentacji: polski. Jednostki SI, wymiary na rysunkach w cm / rzędne w m (zgodnie z PN-B-01029).
4. Dane osobowe projektantów, numery uprawnień, podpisy — **pola do uzupełnienia** (nie wolno fabrykować danych rzeczywistych osób).
