# Audyt konstrukcyjno-funkcjonalny koncepcji v1.2 – rejestr ustaleń

**Obiekt:** siedziba Urzędu Marszałkowskiego Województwa Dolnośląskiego z salą Sejmiku, Wrocław, róg ul. Mazowieckiej i Wybrzeża J. Słowackiego.
**Stan ocenianego projektu:** specyfikacja v1.2 (S-3): `docs/20_koncepcja/koncepcja_wybrana.md`, `model/koncepcja.json` (1.2 S-3), `docs/20_koncepcja/kondygnacja_S2.md`; układ garażu v1.1 (`_rewizja_parking.py`); model pomieszczeń `model/budynek.json` i rzuty 1:200 w stanie v1.0 (przebudowa czeka jako V12-OPEN 1).
**Data:** 17.11.2026.
**Zakres:** rejestr zbiorczy sześciu soczewek audytu: S1 konstrukcja, S2 posadowienie, S3 ochrona ppoż., F1 komunikacja, F2 program biur, F3 garaż i technika.
**Metoda:** każde ustalenie zgłoszone przez soczewkę zweryfikowano dwukrotnie i niezależnie (weryfikacja 1 i 2) skryptami w `scratchpad/audyt_kf/` (shapely, obliczenia wg PN-EN, WT, rozp. MSWiA). Do rejestru weszły tylko ustalenia potwierdzone w obu weryfikacjach. „Waga końcowa” to waga po weryfikacji, a w nawiasie podano wagę zgłoszoną. Problemy znane z `weryfikacja_geometria.md`, `weryfikacja_program.md`, `weryfikacja_koszt_eko.md`, `rejestr_poprawek_v1_1.md` i `kondygnacja_S2.md` pominięto (rozdz. 4).
**Integralność:** nie korzystano z żadnych informacji o wynikach konkursu ani o pracach konkursowych. Źródła to wyłącznie repozytorium oraz przepisy i normy powołane przy ustaleniach.
**Zmiany w projekcie:** utworzono wyłącznie ten plik. Spójność poprawek między sobą sprawdzono skryptem `/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/audyt_kf/redakcja/spojnosc.py` (rozdz. 5.4).

**Skala wag**

- **KRYTYCZNY** – niezgodność z przepisem (WT, rozp. MSWiA) albo z obligatoryjnym wymaganiem regulaminu, widoczna na planszach lub w opisie. Sąd albo rzeczoznawca uzna ją za błąd projektu.
- **ISTOTNY** – błąd albo istotne ryzyko, które wymaga zmiany rzutu, przekroju albo opisu konstrukcji lub instalacji. Wykryje je rzeczoznawca albo konstruktor.
- **DROBNY** – uzupełnienie opisu, wymiarowania albo technologii bez zmiany bryły i układu funkcjonalnego.

**Właściciele poprawek**

- `rewizja_spec`: `koncepcja_wybrana.md`, `koncepcja.json`, skrypty `_rewizja_*.py` i `_v12_*.py`;
- `agent_rzutow`: `tools/model_pomieszczen.py` → `model/budynek.json`, rzuty 1:200;
- `kondygnacja_S2`: `kondygnacja_S2.md` i `.json`, skrypty `_s2_*.py`.

---

## 0. Streszczenie

| Waga końcowa | Liczba | Ustalenia |
|---|---|---|
| KRYTYCZNY | 8 | S3-ppoz-01, -02, -03, -04; F1-komunikacja-02, -10; F2-program-biura-01; F3-garaz-technika-01 |
| ISTOTNY | 19 | S1-konstrukcja-01, -03, -08; S3-ppoz-07, -08, -10; F1-komunikacja-01, -03; F2-program-biura-02, -03, -04, -05, -07, -08; F3-garaz-technika-02, -03, -04, -05, -06 |
| DROBNY | 14 | S1-konstrukcja-04, -06; S2-posadowienie-01, -05, -07; S3-ppoz-09; F1-komunikacja-05, -07; F2-program-biura-09, -10; F3-garaz-technika-07, -08, -09, -10 |
| **Razem** | **41** | w weryfikacji 15 obniżono, 1 podwyższono (F1-komunikacja-10), 25 bez zmiany wagi |

| Właściciel | KRYT. | IST. | DROB. | Razem |
|---|---|---|---|---|
| rewizja_spec | 6 | 11 | 12 | 29 |
| agent_rzutow | 2 | 7 | 2 | 11 |
| kondygnacja_S2 | – | 1 | – | 1 |

Pięć najważniejszych zdań:

1. Ewakuacja jest dziś niezgodna z WT w czterech miejscach o randze krytycznej:
   - na rzutach żadna klatka nie ma dostępu przez przedsionek (S3-ppoz-01);
   - na parterze obie klatki wieży wychodzą przez jeden hol, wbrew § 256 ust. 6 i Wyj. 20 odp. 78, a klatka C i M1 nie mają wyjścia (S3-ppoz-02);
   - sale konferencyjne 200 i 80 os. nie mają po dwa wyjścia (S3-ppoz-03 = F1-komunikacja-02 = F2-program-biura-01);
   - kondygnacja −2 ma faktycznie jedno wyjście, a przejście wynosi ok. 50–54 m bez tryskaczy (S3-ppoz-04).
2. Rampy garażu są jednopasowe z sygnalizacją wahadłową, a na kondygnacjach jest 70 i 40 stanowisk, co łamie WT § 103 ust. 2 (F3-garaz-technika-01). Rampa zgodna z przepisem (5,5 m) przebudowuje parter segmentu, konstrukcję segmentu nad bramą i kieszeń wschodnią wieży. Od tej decyzji zależy kilkanaście innych poprawek.
3. Po koniecznych poprawkach bilans miejsc postojowych spada ze 110 do 103, czyli poniżej wymaganych 106. Tracą się 2 miejsca przez uskok stropu pod bramą ogrodową (S1-konstrukcja-08 / F1-komunikacja-10) i 5 przez zatokę do zawracania (F3-garaz-technika-02). Jedynym konkretnym źródłem kompensacji jest −2 pod M1 (+6 m.p.), co kosztuje 0,4–0,6 mln zł i wymaga robót przy kamienicy Maz. 19.
4. Konstrukcja ma dwie luki w drodze obciążeń:
   - dach i antresolę sali Sejmiku opisano jako oparte na trzonach, które do sali nie sięgają. Rozwiązaniem jest ściana-tarcza pd. sali na trzonie A i nowy słup elewacji wsch. ciągły do −2 (S1-konstrukcja-01);
   - pierścień słupów R 7,0 kończy się nad parterem bez przejęcia ok. 10–11 MN, a słupy stoją w osi Bramy. Rozwiązaniem jest usunięcie pierścienia, słupa (32,40; 23,15) i słupa łuku 45° (S1-konstrukcja-03).
5. Parter M1 jest niedostępny bez schodów: do bramy ogrodowej jest uskok 0,40–0,60 m, a szyb C1 usunięto. To narusza obligatoryjny wymóg regulaminu III.1.8 (F1-komunikacja-10). Tania naprawa to obniżenie posadzki M1 do poziomu bramy, które przy okazji daje klatce C i MDS wyjście bez stopni.

### 0.1. Uwagi redakcyjne

- **Duplikaty.** Kilka ustaleń opisuje ten sam problem z różnych soczewek. Wdraża się je raz:
  - G1, wyjścia i dojście do sal konferencyjnych: S3-ppoz-03, F1-komunikacja-02, F2-program-biura-01 (pakiet G1 w rozdz. 2);
  - G2, drzwi trzonów: S3-ppoz-01, F1-komunikacja-03 pkt c, F2-program-biura-08;
  - G3, zbiornik i pompownia ppoż.: S3-ppoz-08, F3-garaz-technika-04;
  - G4, przepompownie i separator: S2-posadowienie-07, F3-garaz-technika-04 pkt d;
  - G5, oś Hali: F1-komunikacja-01, S1-konstrukcja-03;
  - G6, M1 i klatka C: S3-ppoz-02 pkt c, F1-komunikacja-10;
  - G7, strop nad −1: S1-konstrukcja-08, F1-komunikacja-10, F3-garaz-technika-03.
- **Konflikty między poprawkami.** Przy redakcji wykryto 19 pozycji koordynacyjnych (K-1…K-19), w tym 18 kolizji między poprawkami z różnych soczewek, m.in.:
  - lokalizacja PHS.02 z F2-02 przecina oś Hali na 5,5 m;
  - korytarz klatki B z S3-02 zamyka pokój cichy z F1-01;
  - BESS > 60 kWh na kond. 1 (F3-01);
  - słupy segmentu z S1-06 wypadają w świetle nowej bramy 6,0 m;
  - kanały z S3-07 przechodzą przez cięgno tarczy z S1-01.

  Rozstrzygnięcia są w rozdz. 5.4. Poprawki w tabeli i w rozdz. 2 już je uwzględniają (oznaczenie „[red.]”).
- **Źródło błędów modelu.** Większość błędów modelu pomieszczeń bierze się z jednej reguły generatora: `doors_for()` daje „jedne drzwi na pomieszczenie” i tylko do komunikacji. Przebudowę z V12-OPEN 1 trzeba połączyć z jednym pakietem testów (rozdz. 5.2, faza 2).
- **Koszt.** Suma szacunków poprawek wynosi ok. 2,3–3,3 mln zł, a w wariancie z tryskaczami w garażu o 0,35–0,45 mln więcej. Zapas v1.2 to 1,01 mln przy rezerwie 5 % i 2,43 mln przy rezerwie 4 % (V12F-KOSZT). Szczegóły w rozdz. 5.6.

---

## 1. Tabela ustaleń (KRYTYCZNY → ISTOTNY → DROBNY)

| ID | Waga końcowa (zgł.) | Soczewka | Problem | Dowód (skrót) | Wymaganie (źródło) | Poprawka (najlepsza) | Właściciel | Wpływ na rysunki / tabele / koszt |
|---|---|---|---|---|---|---|---|---|
| S3-ppoz-01 | KRYTYCZNY (KRYT.) | S3 ppoż. | Klatki A, B, C bez prawidłowych drzwi na wszystkich kondygnacjach modelu i rzutów | −2, −1, ANT: 0 drzwi; P i S: żadne do trzonów; klatka B wprost na korytarz (kond. 1, 2, 4), A (kond. 5); klatka C bez drzwi; przyczyna `doors_for()` | WT § 246 ust. 1, § 232 ust. 3–4, § 253 ust. 2, § 280 ust. 1, § 239 ust. 3 | Drzwi trzonów z `koncepcja.json` v1.2: korytarz → przedsionek (EI 30) → klatka (E 30); przedsionek B tylko w licu pn. (v 9,90); szer. ≥ 1,0 m (S/ANT ≥ 1,2 m); test grafu drzwi | agent_rzutow | wszystkie rzuty 1:200 (P3–P5), `budynek.json` testy; koszt 0 |
| S3-ppoz-02 | KRYTYCZNY (KRYT.) | S3 ppoż. | Parter: klatki A i B wychodzą przez jeden hol (Hala); klatka C i M1 bez wyjścia na zewnątrz | przedsionek A → Hala; trzon B otoczony segmentem z rampą, P1/P2, kancelarią i Halą; C tylko z korytarza M1; koniec skrzydła 55–65 m w jednym kierunku | WT § 256 ust. 6 (Wyj. 20 odp. 78; ppoz.md D9), § 246 ust. 1, § 250 ust. 1, § 256 ust. 2 | A jedyna przez Halę (drzwi do Hali EI 30); B: drzwi 1,2 m z podestu w licu zach. u 24,85 + korytarz EI 60 1,6 m do drzwi w licu pd. u 18,9–21,6; C: drzwi z podestu w licu d = 15 (s 5,0–6,5); bariery § 250 [red.: K-4, K-5, K-13] | rewizja_spec | rzut P, rozdz. 5–6; −18 m² Hali; < 0,1 mln zł |
| S3-ppoz-03 | KRYTYCZNY (KRYT.) | S3 ppoż. | Sale 200 os. (2 × 100) i 80 os. bez wymaganych wyjść | SK.01: 1 drzwi 1,6 m do ślepego KW.P.15; SK.02 i reżyserki: 0 drzwi; spec. nie określa wyjść | WT § 238, § 239, § 236 ust. 4 | Pakiet G1 (rozdz. 2, przy F1-02): po 2 wyjścia ≥ 5 m z sali 80 i z każdej połowy sali 200; drzwi zewnętrzne wyłącznie na dziedziniec | rewizja_spec | rzut P, PZT (spoczniki); ok. 0,10–0,15 mln (raz dla G1) |
| S3-ppoz-04 | KRYTYCZNY (KRYT.) | S3 ppoż. | −2: przedsionek B niedostępny (faktycznie 1 wyjście); przejście ok. 50–54 m > 40 m bez tryskaczy | GPC przylega do przedsionka B od pn. i wsch., słup 0,25 m przed licem zach. (ok. 0,88 m w świetle); 45–50 m w linii prostej z końca rzędu skrzydła | WT § 278 (40 m; +50 % tylko z tryskaczami lub samoczynnym oddymianiem, nie strumieniowym), § 239 ust. 3; V12-OPEN 3 | Drzwi EI 30 w licu pn. przedsionka B na −2 i −1 (pole 1,5 × 1,5 m kosztem GPC ok. 2,3 m²); samoczynna wentylacja oddymiająca kanałowa (limit 60 m) albo tryskacze OH2 w garażu | rewizja_spec | rzuty −1/−2, rozdz. 5, 6, 16; +0,15–0,25 mln (tryskacze ok. 0,6) |
| F1-komunikacja-02 | KRYTYCZNY (KRYT.) | F1 komunikacja | Strefa konferencyjna: foyer bez połączenia z holem, sala 80 dostępna tylko przez salę 200, brak wyjść | spec.: „łącznik do foyer” przylega do bistro, sala 80 sąsiaduje tylko z bramą i salą 200; model: SK.06 bez drzwi do hali | WT § 238, § 239 ust. 2 pkt 3; program rozdz. 8 („SK bezpośrednio przy holu”, PU s. 8–9) | Pakiet G1: przejście hala–foyer 2,95 m (u 0,5–8,15 × v 8,9–11,85); sala 200 przy bramie (s 16,35–32,85, netto ok. 221 m²), sala 80 przy foyer (s 33,0–40,6) z kuluarem 1,95 m | rewizja_spec | rozdz. 6, `parter.skrzydlo`, rzut P, F.15.B; zamyka P-D5; koszt w S3-03 |
| F1-komunikacja-10 | KRYTYCZNY (IST.) | F1 komunikacja | Parter M1 niedostępny bez schodów (odcięty bramą, uskok 0,40–0,60 m) | brama 118,70–118,90, M1 119,30; M1 poza listą 8 wejść; szyb C1 usunięty (V12-I5C) | Regulamin III.1.8 (R-036, R-037); WT § 54 ust. 2 | Obniżyć posadzkę M1 (s 0–12,15) do ok. 118,82–118,85, wejście z bramy bez progu; przeliczyć klatkę C; skreślić jednostkę stackera pod bramą (wspólnie z S1-08) | rewizja_spec | rozdz. 2 (h), 6, 9; przekrój; −1 pod M1 3,20 m; koszt pomijalny |
| F2-program-biura-01 | KRYTYCZNY (KRYT.) | F2 program | Centrum konferencyjne w modelu: SK.02 bez drzwi, SK.01 jedne drzwi, foyer jest wyspą; rzut pokazuje 336 i 126 krzeseł | na P 19 drzwi, żadne nie należy do SK.02; KW.P.15 bez innych drzwi; szablon „chairs” 16 × 21 bez przejść | WT § 238; ppoz.md 5.5 (§ 261: ≤ 16 miejsc między przejściami) | W modelu pakiet G1: drzwi w miejscu okien (skrzydło 1,0 m przy ościeżu), ściana mobilna na filarze, spoczniki 119,28, widownia 200/80 w blokach ≤ 16; test „> 50 os. ⇒ ≥ 2 wyjścia ≥ 5 m” | agent_rzutow | rzut P, `model_pomieszczen.py`, `rzuty.py` |
| F3-garaz-technika-01 | KRYTYCZNY (KRYT.) | F3 garaż | Rampy jednopasowe z sygnalizacją wahadłową przy 70 i 40 m.p. na kondygnacji | rampa uliczna i wewnętrzna 3,5 m; brama 0,50–0,60 m od granicy, 4,84–5,42 m do krawężnika, więc czekające auto zajmuje chodnik | WT § 103 ust. 2–3 (t.j. Dz.U. 2022 poz. 1225); proj. WT § 101 | Rampa uliczna dwukierunkowa 5,5 m (6,0 m w świetle odbojów), brama ≥ 6,0 m cofnięta 1,5–2,0 m; pas −1 poszerzony do v −7,35; parterowe poszerzenie segmentu o 1,5 m; obsługa −2 rampą 6,0 m albo dźwigiem samochodowym [red.: K-6, K-7, K-8, K-11, K-12] | rewizja_spec | segment P i kond. 1, kieszeń wsch., −1/−2, przekrój A-A, E-K-1; ok. +0,65 mln |
| S1-konstrukcja-01 | ISTOTNY (KRYT.) | S1 konstrukcja | Sala Sejmiku: ruszt dachu, antresola i galeria bez drogi obciążeń; opis podpór sprzeczny (rozdz. 5 i S2 pkt 9.7) | trzony nie sięgają sali (A u ≤ 15,50, B v ≤ 9,90); ściany pd. i zach. na płycie 0,28 m poza liniami słupów; reakcje końcowe ok. 2,1 MN | PN-EN 1990 p. 2.1; PN-EN 1992-1-1 p. 5.1, 6.4; regulamin R-117 b (opis konstrukcji) | Ruszt pn.–pd. ≤ 17,25 m; ściana pd. jako tarcza 0,30–0,35 m o wys. czynnej ok. 6,0 m na 24,2 m z cięgnem ok. 2,4 MN, oparta na trzonie A i nowym słupie 0,60 × 0,60 m w filarze wsch., ciągłym do −2; ściana zach. nienośna [red.: K-9, K-17] | kondygnacja_S2 | rozdz. 5, JSON `dach_S`, przekroje A-A i B-B; ok. 0,1–0,2 mln |
| S1-konstrukcja-03 | ISTOTNY (IST.) | S1 konstrukcja | Pierścień R 7,0 kończy się nad parterem (ok. 10–11 MN bez przejęcia); słupy w osi Bramy | 7 słupów R 7,0 tylko na kond. 1–6; słup R 13,5/45° 2,50 m przed drzwiami, słup (32,40; 23,15) 1,21 m za drzwiami | PN-EN 1990 p. 2.1; rozdz. 1, 2 poz. 15 i 11; PN-ISO 21542 | Usunąć pierścień R 7,0, słup (32,40; 23,15) na −2…6 i słup R 13,5/45° (największe puste koło 6,13 m, przęsło ok. 8,7 m; przęsło podcienia 6,99 m z belką 0,45 × 0,90 m w nadprożu); rozdz. 11: pas osi ≥ 2,0 m [red.: K-5] | rewizja_spec | rozdz. 5, JSON `luk`, rzuty P, 1–6, −1, −2, przekroje, kadry W3 i W6 |
| S1-konstrukcja-08 | ISTOTNY (IST.) | S1 konstrukcja | Strop nad −1 (wierzch 119,15) leży wyżej niż posadzka bramy ogrodowej (118,70–118,90) | brama nad −1/−2 w pasie s 12,15–16,20; uskok do ≤ 118,45 daje na −1 2,95 m < 3,50 m wymaganych dla stackerów | wykonalność warstw nad stropem podziemia; JSON `stackery` (≥ 3,50 m); MPZP § 13 | Uskok stropu s 12,15–16,20 × d 0–15 do ≤ 118,45 (belki w osiach portalu); rząd stackerów od s ≥ 16,5 (−2 m.p.); strop pasa dziedzińca ze spadkiem 1,5 % (nad R1 ≥ 3,55 m) [red.: K-18] | rewizja_spec | 4.2, rozdz. 12, 16 pkt 10, JSON `podziemie`, F.15; przekrój przez bramę; −2 m.p. |
| S3-ppoz-07 | ISTOTNY (IST.) | S3 ppoż. | W trzonach brak szachtów nadciśnienia i oddymiania korytarzy; szacht B przeciążony | trzon A zajęty w 100 % (0 m² szachtów); szacht B 6,88 m² brutto (ok. 6,0 netto) wobec ok. 7,0–7,5 m² potrzeb | WT § 246 ust. 2, § 247 ust. 1, § 253 ust. 4, § 270 | Szacht B tylko na oddymianie garażu (EI 120), spaliny, piony centrali S i nadciśnienie B (ok. 5,2 m²); nowy szacht SZ-1 ok. 5 m² od P do S (wentylacja pożarowa 2,0 m² + wyrzutnia 2,8 m²) [red.: K-9, K-12] | rewizja_spec | rozdz. 5, 10; rzuty P–S, przekrój A-A; `_s2_geometria.py` |
| S3-ppoz-08 | ISTOTNY (IST.) | S3 ppoż. | Brak zbiornika i pompowni wody ppoż. (hydranty, zawory 52) w budynku W | brak w spec. v1.2 i w `LEVELS.plant`; zawór 52 na 147,95 m n.p.m., czyli ok. 0,6–0,65 MPa na przyłączu; zawory na −2 ok. 0,69 MPa | rozp. MSWiA 2010 § 19 ust. 6, § 22, § 23 pkt 3 lit. a, § 24 ust. 2–5; WT § 212 ust. 9 | Zbiornik 25 m³ (sieć ≥ 15 dm³/s, nasada 75 mm) albo 50 m³ i zestaw pomp 1+1 (10 dm³/s × 0,65 MPa), odrębna strefa REI 120 / EI 60, reduktory na −2; 2 hydranty zewnętrzne DN 80; lokalizacja wg K-6 | rewizja_spec | rozdz. 6, 15; rzut −2 lub segmentu; PZT; F.14.B ok. 0,25–0,30 mln (wspólne z F3-04) |
| S3-ppoz-10 | ISTOTNY (IST.) | S3 ppoż. | Okna skrzydła 0,41 m od ściany oddzielenia przy Maz. 19 (P–4, obie elewacje) | pierwsze okno w s 0,41–1,61 przy d = 0 i d = 15 (`budynek.json`, `elewacje.py`); uskok 0,30 m nie jest wysunięciem ściany | WT § 235 ust. 2, § 272 ust. 3; ppoz.md 11.2 (D14); WT § 57 | Pierwsza oś (s 0,41–1,61) jako przeszklenie stałe EI 60; filary i wypełnienia w pasie s 0–2,0 m jako NRO EI 60; drzwi klatki C poza pasem (s ≥ 2,0) | rewizja_spec | elewacje 1:200, rozdz. 8; ok. 0,12–0,15 mln |
| F1-komunikacja-01 | ISTOTNY (KRYT.) | F1 komunikacja | Oś Hali i wejście ogrodowe zablokowane przez WC PHS.04 | oś przecina PHS.04 na ok. 5,6 m; wnęka wejścia ogrodowego styka się tylko z PHS.04; ścieżka FON przechodzi przez WC; SW.06 0,86 m od osi | idea (rozdz. 1, 2 poz. 15), rozdz. 11; spec. rozdz. 6 (WC przy foyer) | Usunąć PHS.04, pas u 8,3–15,5 × v 0,5–11,85 włączyć do hali; WC konferencyjne wg F2-02; SW.06 poza pasem osi i poza korytarzem klatki B; pole 1,5 × 1,5 m za drzwiami ogrodowymi; FON w osi [red.: K-1, K-4, K-5] | agent_rzutow | rzut P, kadry W6/W10 |
| F1-komunikacja-03 | ISTOTNY (KRYT.) | F1 komunikacja | Pierścień korytarza przerwany na kond. 1–4 (WC do 78 m, ślepa odnoga) | ramię pd. zajmują IT.01 (L 1,21 × 14,2 m), PS.01f, PP.02, PS.01l; WC od DOS.16 77,8 m; po odtworzeniu odcinka ok. 44 m | spec. rozdz. 6 (pierścień 1,80 m); bhp, Dz.U. 2003 poz. 1650 zał. 3 (≤ 75 m); WT § 256 ust. 2–3 | Zakaz pomieszczeń w pasie pierścienia i w łączniku do holu P1/P2; odtworzyć odcinek u 21,4–23,1; serwerownia i archiwa jako prostokąty (F2-04); drzwi trzonów jak w S3-01 | agent_rzutow | rzuty 1–5 (P4/P5), generator |
| F2-program-biura-02 | ISTOTNY (IST.) | F2 program | WC konferencyjne 37,3 m² dla 280 os., w złym miejscu; wejście ogrodowe prowadzi przez WC | PHS.04 37,3 m² w Hali; potrzeba ok. 55–60 m² (7 K, 5 M + 5 pisuarów, 14 umywalek, 2 kabiny dostępne); PHS.02 9,26 m² (znane P-I3) | WT § 84 ust. 2–3 (wg dostepnosc.md); program PHS.04 (PU s. 10) | WC konferencyjne ok. 58 m² netto w pasie u 0,5–8,15 × v 12,45–20,85 z wejściem z foyer; PR.02 przy rowerowni; PHS.02 ≥ 30 m² poza pasem osi [red.: lokalizacja PHS.02 z F2-02 pkt 3 odrzucona – K-1, K-2, K-3] | agent_rzutow | rzut P, F.15.B; bilans powierzchni zerowy |
| F2-program-biura-03 | ISTOTNY (IST.) | F2 program | 56 ścianek między biurami trafia w szybę (siatki przesunięte o 0,45 m) | wieża: podział okna 1,24 / 0,33 m (ścianki w osiach 0,45 + 4,05j, okna 1,35 + 2,70k); skrzydło od dziedzińca 0,40 / 0,72 m | spec. rozdz. 8 („partycje w filarach lub słupkach”); PN-B-02151-3 | Dodatkowy słupek okienny w osi każdej ścianki (wieża: skrzydło 0,825 m + kwatery 0,45 / 0,375 m; skrzydło budynku: kwatera 0,40 m + skrzydło 0,72 m), osobne kasety ZIP; warunek 1:8 zachowany | rewizja_spec | rozdz. 8, elewacje 1:200, przekrój 1:50; ok. 0,1 mln |
| F2-program-biura-04 | ISTOTNY (IST.) | F2 program | Serwerownia i archiwa pod i nad pokojami socjalnymi; kształt L z pasem 1,33 m; strop biurowy pod UPS | IT.01 37,7 m² (spec. 50 m²) w 100 % pod PS.01f; PP.03 między PS.01e i PS.01k; obciążenie obliczeniowe pod UPS 30,6 kN/m² (+68 %) | PN-EN 50600-2-1, TIA-942, PN-ISO 11799, PN-EN 1991-1-1 | Pokoje socjalne do pasa pionów WC; IT.01 ≥ 45 m², prostokąt szer. ≥ 5,0 m; PP.02 ≥ 48 m², PP.04 ≥ 24 m²; jedna strefa wzmocniona (płyta 0,40 m z głowicami) pod archiwami, serwerownią i UPS | agent_rzutow | rzuty 1–4, rozdz. 5, `siatka.strop`; < 0,06 mln |
| F2-program-biura-05 | ISTOTNY (IST.) | F2 program | Stałe stanowiska pracy bez światła dziennego albo w narożu wklęsłym | DOS.19 0 m² okien; DI.08 0,111 < 1/8; GW.06/07 w narożu kond. 3 (§ 13 niespełniony); SW.02 bez okien | WT § 57, § 58, § 13; bhp § 26; zasada (g) spec. | Okno w licu styku 3,83 m (wariant przy słupie narożnym – K-10); GW.06/07 na miejsca PP.01l i PP.01m; kancelaria jako lada w Hali albo przy elewacji Wybrzeża [red.: K-14] | agent_rzutow | rzuty 1–3, P |
| F2-program-biura-07 | ISTOTNY (IST.) | F2 program | 31 „pomieszczeń-szczelin” 0,79–1,6 m (PD, porządkowe, OCZ, MFP); brak PD i pomieszczenia porządkowego na P | 21 pomieszczeń o szer. ≤ 1,0 m, bez drzwi; 8 PD wobec 12 w programie | program PP.06 i IT.02; TIA-569, ISO/IEC 14763-2 | Łączyć szczeliny i dzielić strefę środkową w poprzek na pasy ok. 3,0 m: PD 2,0 × 3,0 m, porządkowe 2,0 × 3,0 m, wnęki OCZ i MFP; na P w dawnym PHS.02; test szer. ≥ 1,8 m | agent_rzutow | rzuty 1–6, P; F.15.B |
| F2-program-biura-08 | ISTOTNY (IST.) | F2 program | 51 pomieszczeń bez drzwi (m.in. 20 pokoi na łuku, gabinet Przewodniczącego, sala narad 30 os.); sekretariaty bez drzwi do gabinetów | `drzwi2.py`: KS.01 bez wejścia; drzwi do gabinetu ma 1 sekretariat z 10 | program („sekretariat … połączony drzwiami”, PU s. 5); WT § 236–237 | Drzwi 0,9 m z pokoi na łuku; wejście do KS.01 przez KS.03; drzwi sekretariat–gabinet oraz zamiany GW.03↔04, CZ.02↔03, DZ.08, KS.10; drzwi trafo ≥ 1,4 m od Wybrzeża, BESS EI 120-C; testy | agent_rzutow | rzuty P–6 |
| F3-garaz-technika-02 | ISTOTNY (KRYT.) | F3 garaż | Na −1 brak pętli dróg; zawrócenie o 180° u stopy rampy wymaga cofania (53 ze 113 pozycji) | obwiednia pojazdu 4,74 × 1,76 m (R 5,86 m) sięga v 7,48, a linia R2 leży na 6,60 | WT § 104 ust. 1; EAR 2005 / RAS-K-1 | Zatoka do zawracania: usunąć trójkę R2 u 8,4–15,9 × v 6,6–11,6 na −1 (−5 pozycji); ostatnie 3 m rampy wewnętrznej bez odboju od zach.; kompensacja miejsc (rozdz. 5.5) | rewizja_spec | rzut −1, tab. 12, F.15.C; −5 m.p.; kompensacja 0,4–0,6 mln |
| F3-garaz-technika-03 | ISTOTNY (IST.) | F3 garaż | Opis OzN i EV niezgodny z układem stackerów; rząd R1 na granicy wysokości | 6 OzN „na −1” to −9 pozycji, a skrypt liczy −3 (wynik 101–104); 55 punktów EV wobec 46 stanowisk niezależnych; R1 3,45 m < 3,50 | MPZP § 13; WT § 21; ppoz.md rozdz. 8 | 6 OzN na −2 przy trzonach A i B (−3, jak w skrypcie): −1 73, −2 37; EV tylko na stanowiskach niezależnych + trasy kablowe; jedna rzędna stropu pasa; F.15.C wariant ostrożny 78 + 32 [red.: K-18] | rewizja_spec | JSON `podziemie`, rozdz. 5, tab. 12, F.15.C |
| F3-garaz-technika-04 | ISTOTNY (IST.) | F3 garaż | W bilansie −1/−2 brak zbiornika ppoż., pompowni, węzła cieplnego i przepompowni | E-I-4 usunął pompownię razem z tryskaczami; brak IT.10; klin −2 ma 25,7 m² brutto (14,8 m² o szer. ≥ 2,0 m) | rozp. MSWiA 2010 § 22, § 24; WT § 212 ust. 9, § 102 pkt 5, § 281 | Klin −2: zbiornik 24–25 m³ + pompownia ok. 8 m², strefa REI/EI 120; klin −1: odpady (F3-05); węzeł IT.10 w pasie u 31,1–33,4 na −1; przepompownie kompaktowe; nasada 75 mm | rewizja_spec | rozdz. 5, 10, JSON `technika`, rzut −1/−2; F.14.B ok. +0,2–0,3 mln (wspólne z S3-08) |
| F3-garaz-technika-05 | ISTOTNY (IST.) | F3 garaż | Korytarz do dźwigu T na −1 nie łączy się z garażem; brak drogi odpadów i strefy IT.15 | 0,35 m między odbojem rampy a ścianą pasa; odpady w M1 ok. 60–70 m od T bez drogi wywozu | PU s. 15, 17 (IT.14, IT.15); rozp. (WE) 852/2004 zał. II rozdz. VI | Dostawy z poziomu terenu przez przedsionek T (IT.15 12–15 m² po poszerzeniu segmentu z F3-01); odpady IT.14 w klinie −1 przy T; z opisu usunąć trasę „rampą na −1 i korytarzem” | rewizja_spec | rozdz. 6, poz. 13, `rdzenie.T`, rzuty P i −1 |
| F3-garaz-technika-06 | ISTOTNY (IST.) | F3 garaż | Brak obowiązkowej drogi wewnętrznej do odbioru osób i drobnych dostaw (powiązanie z dz. 10/2) | spec. poz. 13: „dz. 10/2 nie jest używana”; na terenie brak miejsca zatrzymania pojazdu | PU s. 16–17 („projekt musi obejmować”); Wyj. 4 odp. 20; R-214; kryterium 1a | Droga jednokierunkowa 3,0–3,5 m z dz. 10/2 w pasie pd. od segmentu; miejsce krótkotrwałego zatrzymania (nie „stanowisko postojowe”, § 19); zawracanie na placu typu T albo wyjazd przez dz. 10/2; skrzynki rozsączające SLW 30 [red.: K-16] | rewizja_spec | PZT, rozdz. 9, poz. 13 |
| S1-konstrukcja-04 | DROBNY (IST.) | S1 konstrukcja | Skrzydło przy wieży: w klinie s 34,2–42,9 przęsło do 18,4 m; na styku długości 26,7 m brak drugiej elewacji | L/h ok. 46 przy płycie 0,40 m; reakcja 120–160 kN/m na pas u = 0 (M ok. 0,9–1,2 MNm wobec nośności ok. 230 kNm/m) | PN-EN 1992-1-1 p. 7.4; spójność z rozdz. 5 | Belka pasmowa ok. 1,2 × 0,60 m (9,5 m) od słupa narożnego (s 34,18; d 15,00) do słupa wieży (0; 8,70); pas nośny u = 0 w stropach P–4; zapis w rozdz. 5 [red.: K-10] | rewizja_spec | rozdz. 5 |
| S1-konstrukcja-06 | DROBNY (IST.) | S1 konstrukcja | Segment: płyta 0,28 m na 7,07–10,55 m bez zapisu „sprężona”; taras; układ słupów przy bramie i rampie | pod tarasem L/h 37,7; przy „słupach co 4,05 m” brama 4,0 m jest niemożliwa; rampa pod licem zach. | PN-EN 1992-1-1 tab. 7.4N, p. 7.4.2 | Płyty sprężone 0,28 m (kond. 1–4) i 0,35 m (taras; kond. 4 2,70 m w świetle); słupy przy bramie po F3-01: żaden w v 0…−6,7, belki krawędziowe ok. 6,7 m i 7,1 m [red.: K-8] | rewizja_spec | rozdz. 5, tab. 4.2, elewacja wsch., przekrój A-A |
| S2-posadowienie-01 | DROBNY (KRYT.) | S2 posadowienie | Brak III kategorii geotechnicznej i warunku DGI; strop glin nierozpoznany na ok. 130 m obwodu | ściany 19 m wchodzą w glinę 1,8–2,7 m w O-01…O-04; na pd. odcinku (n < 40,75) otwory O-05…O-09 kończą się w pospółkach (K-01) | Dz.U. 2012 poz. 463 § 4 ust. 3 pkt 3 lit. e, § 7 ust. 3; formularze, zał. 3 pkt 2 ppkt 2 lit. b | Zostawić 19 m; dopisać III kategorię, DGI (3 otwory 25–30 m, CPTu co ok. 20 m, piezometry) i warunek „≥ 2 m w ciągłą QpB”; otwory TRT jako rozpoznanie pod gliną; sondy w rurach osłonowych | rewizja_spec | rozdz. 5, 16, JSON `obudowa`, opis etap2; rezerwa (ok. 0,3 mln przy +2 m) |
| S2-posadowienie-05 | DROBNY (IST.) | S2 posadowienie | Przesłona z iniekcji przy Maz. 19: głębokość nieokreślona, zakład kolumn grozi oknami | 17 kolumn na 15 m: zakład 0,26 m wobec rozejścia 0,38–0,76 m na 19 m; ława prawdopodobnie na gruncie organicznym (CPTu O-08) | PN-EN 12716, PN-EN 1538, PN-EN 1997-1 p. 2.4.9 | Kolumny Ø 1,2 do 99,75, rozstaw ≤ 0,75 m (21 szt.), inklinometria ≤ 1 %, pole próbne; podbicie osobno, z progiem wypiętrzenia ok. 3 mm; monitoring WS 5 | rewizja_spec | rozdz. 5, JSON `obudowa`; ok. +0,05 mln |
| S2-posadowienie-07 | DROBNY (IST.) | S2 posadowienie | Brak przepompowni ścieków i separatora; zbiornik deszczówki na −2 bez przelewu | odbiorniki na −1 (115,10) i −2 (112,10) leżą poniżej dna kanałów 117,2–117,7 | PN-EN 12056-4; PN-EN 858; PN-EN 81-72 | Jedna przepompownia 6–8 m² na −2 w strefie pn. od trzonu A (pompy 1+1, pętla ≥ 119,50, zasilanie z agregatu); separator w garażu; przelew deszczówki w studni zewnętrznej | agent_rzutow | rozdz. 6, 10, model −2; ok. 0,1 mln |
| S3-ppoz-09 | DROBNY (IST.) | S3 ppoż. | Trafo pod pokojem biurowym (< 2,8 m w pionie); rozdzielnia z SZR bez wydzielenia | 4,80 − 0,30 − (1,9…2,2) = 2,3–2,6 m < 2,8 m | WT § 182, § 212, § 183 | Nad komorą trafo pomieszczenie bez stałego pobytu ludzi (magazynek, falowniki albo rozdzielnia z F3-01); trafo i rozdzielnia z SZR jako odrębne strefy REI 120 / EI 60 [red.: K-7] | rewizja_spec | rozdz. 6, rzut kond. 1 segmentu; koszt 0 |
| F1-komunikacja-05 | DROBNY (IST.) | F1 komunikacja | Strefowanie dźwigów na P: od wejścia głównego pracownicy mają tylko A1/A2 | P1/P2 obsługują kond. 1–6, ale ich lobby nie łączy się z halą (D16); A1 + A2: INT ok. 46–51 s, z R ok. 31–34 s | CIBSE Guide D:2020; ISO 8100-32; F.15.C I.11 | R w grupie A; przejście ≥ 1,5 m z lobby P1/P2 do hali (kieszeń u 31,1–33,4 × v 7,45–10,05) z bramką; sterowanie docelowe; tabela ruchu; I.11 = 5 + T | rewizja_spec | rozdz. 5, 7, F.15.C |
| F1-komunikacja-07 | DROBNY (IST.) | F1 komunikacja | Brak matrycy stref dostępu dla dźwigów i klatek | A1/A2 z publicznego łącznika jadą do Z3 i Z4; P1/P2 mają przystanki 1–6, P2 także −2/−1; M1 i klatka C dostępne z bramy | program rozdz. 7 (Z1–Z6; PU s. 14) | Matryca w rozdz. 5, 7 i na schemacie P2: karty na przystankach i w kabinach; drzwi klatek – wejście na kartę, wyjście zwalniane przez SSP; M1 z wideodomofonem | rewizja_spec | rozdz. 5, 7, plansza P2 |
| F2-program-biura-09 | DROBNY (IST.) | F2 program | Bistro: wyciąg „z odzyskiem do instalacji ogólnej”; zaplecze bez połączenia z salą | zapis E-I-3; SW.08 ma drzwi tylko do SK.06 | PN-EN 16282-1, PN-EN 16798-3; MPZP § 6 pkt 13 | Urządzenia z wbudowaną kondensacją oparów (bez okapu kanałowego), wyciąg klasy ETA 2 do centrali, bez wyrzutu na dach; lada SW.08↔SW.07; dostawy poza godzinami pracy | rewizja_spec | rozdz. 6, 10, E-I-3 |
| F2-program-biura-10 | DROBNY (DROB.) | F2 program | Szablon umeblowania: biurka przodem do okna w pokojach 3-os. | `rzuty.py`, gałąź else w `draw_furniture` | rozp. MPiPS z 1.12.1998; PN-EN 12464-1 | Biurka 1,6 × 0,8 m prostopadle do elewacji (2 + 1), krzesła narysowane | agent_rzutow | rzuty 1–6 |
| F3-garaz-technika-07 | DROBNY (IST.) | F3 garaż | Agregat bez wyrzutu powietrza chłodnicy; żaluzje 8 m² w licu 7,07 m grożą recyrkulacją | potrzeba 8–12 m³/s; wlot i wylot ≤ 3–4 m od siebie; okno lok. 6 w WS 5 na ok. 124,0 | wymagania producentów zespołów prądotwórczych; MPZP § 6 pkt 13; rozp. o hałasie | Chłodnica wyniesiona przy dry-coolerze na kond. 4 (żaluzje 2 × 12 m²), blokada wzajemna pracy; na kond. 1 tylko 2 + 2 m² żaluzji z tłumikami ≥ 25 dB; moc 250–350 kVA w opisie | rewizja_spec | rozdz. 6, 10, E-I-3 |
| F3-garaz-technika-08 | DROBNY (IST.) | F3 garaż | 58 sond GPC „wierconych z dna” przebija przesłonę z glin | 58 × 91 m od 110,90; 6,6 m różnicy do ZWG 117,00; warunki pod gliną nieznane | PN-EN 1997-1 p. 2.4.7.4–2.4.7.5 | Wiertnice niskie pod stropem −1, orurowanie z prewenterem, płuczka obciążona, iniekcja od dołu; otwór pilotażowy ok. 100 m z piezometrami (razem z TRT) | rewizja_spec | rozdz. 5, 16.5, E-I-2; +0,2–0,3 mln |
| F3-garaz-technika-09 | DROBNY (DROB.) | F3 garaż | Przy krawędzi stropu nad rampą wewnętrzną 2,15 m w pionie < 2,20 m | `internal_ramp()` liczy płytę 0,30 m, JSON ma 0,35 m | WT § 102 pkt 1 | Cofnąć krawędź otworu o 0,30–0,50 m; w skrypcie płyta 0,35 m; ogranicznik skrajni 2,10 m | rewizja_spec | `_rewizja_parking.py`, przekrój A-A |
| F3-garaz-technika-10 | DROBNY (DROB.) | F3 garaż | 31 stanowisk 0,00 m od słupa; 5 stanowisk 0,15 m od ściany | `stalls_in_row`: początki 8,1k + 0,3, słupy 0,60 m | WT § 104 ust. 3 pkt 1–2 | Słupy na −1/−2 ≤ 0,40 m w kierunku u (np. 0,40 × 0,90 m), słupy 0,60 × 0,35 obrócone; zmiana przekroju w stropie nad −1; rząd równoległy odsunąć o 0,15 m | rewizja_spec | `_rewizja_parking.py`, rzuty −1/−2 |

---

## 2. Szczegóły ustaleń

Układy współrzędnych są takie jak w ustaleniach: (u, v) to układ wieży, (s, d) to układ skrzydła (s od granicy z Maz. 19 wzdłuż Mazowieckiej, d od lica ulicznego). „v1” i „v2” oznaczają weryfikację 1 i 2.

### 2.1. KRYTYCZNE

#### S3-ppoz-01 – Klatki A, B, C bez prawidłowych drzwi w modelu i na rzutach 1:200
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · S3 ppoż. · agent_rzutow · grupa G2*

- **Dowód.** Drzwi wzięto z `budynek.json`, a stronę drzwi ustalono przesunięciem ±0,35 m wzdłuż normalnej. Obejrzano też powiększenia `rzut_1` i `rzut_P`.
  - Na −2, −1 i ANT model nie ma ani jednych drzwi. Na P jest 19 drzwi, na S 10, ale żadne nie prowadzą do trzonów.
  - Kond. 1, 2 i 4: klatka B ma drzwi (28,15; 0,75) wprost na korytarz, a przedsionek B ma drzwi (27,75; 9,65) tylko na korytarz. Między przedsionkiem a klatką drzwi nie ma.
  - Kond. 3: drzwi ma tylko przedsionek B.
  - Kond. 5: klatka A ma drzwi wprost na korytarz (8,55; 19,85).
  - Kond. 6: klatka A ma dwoje drzwi do przedsionka, a przedsionek nie ma wyjścia na korytarz.
  - Klatka C nie ma drzwi na żadnej kondygnacji.

  Przyczyną jest `doors_for()` w `tools/model_pomieszczen.py` (l. 1818, „jedne drzwi na pomieszczenie”). V12-OPEN 1 zmienia geometrię trzonów, ale nie logikę drzwi, więc tego błędu nie usunie. Dodatkowo słup 0,60 × 0,35 m (u 24,0–24,6; v 8,53–8,88) stoi 0,25 m przed licem zach. przedsionka B. Drzwi w tym licu miałyby ≤ 0,88 m w świetle, czyli mniej niż 0,9 m. Szerokość 0,9 m drzwi przedsionków to błąd modelu: spec. v1.2 daje na S i ANT 1,2 m, a dla 354 os. na dwie klatki potrzeba 1,06 m.
- **Wymaganie.** WT § 246 ust. 1 (budynek W: klatki obudowane, oddzielone przedsionkiem); § 232 ust. 3–4 (drzwi przedsionka EI 30 od korytarza i E 30 do klatki); § 253 ust. 2 (dźwig R przez przedsionek); § 280 ust. 1 (przedsionek między garażem a klatką); § 239 ust. 3; § 242 ust. 1.
- **Poprawka.** Generować trzony i drzwi z `koncepcja.json` v1.2 (`rdzenie.*.uklad_uv`, `sklad`), w tym samym przebiegu co V12-OPEN 1.
  - Na każdej kondygnacji od −2 do S: korytarz → przedsionek (EI 30) → klatka (E 30), a szyb R → przedsionek.
  - Usunąć drzwi z klatki B prosto na korytarz (KW.x.06) i z klatki A prosto na korytarz (KW.5.05).
  - Na −1 i −2: przedsionek A ma drzwi wsch. do garażu, przedsionek B północne (S3-ppoz-04).
  - Przedsionek B ma drzwi wyłącznie w licu pn. v 9,90 (u ok. 25,2–26,4), nigdy w licu zach.
  - Szerokości w świetle: ≥ 1,0 m na kondygnacjach biurowych, ≥ 1,2 m na S i ANT oraz w wyjściu z klatki na zewnątrz na P (§ 68, § 239 ust. 4); drzwi zewnętrzne holu klatki A +50 % (§ 256 ust. 6).
  - Testy w `budynek.json['testy']`: każda klatka osiągalna z korytarza wyłącznie przez przedsionek na każdej kondygnacji; każde pomieszczenie ma ≥ 1 drzwi albo jest otwartą wnęką; przed drzwiami pole 1,5 × 1,5 m wolne od słupów.
- **Ryzyko.** Plansze P3–P5 pokazują budynek wysoki, w którym żadna klatka nie jest dostępna albo dostęp omija przedsionek. Rzeczoznawca ppoż. odrzuci taki rzut, a sąd odczyta to jako brak kontroli nad projektem. Bez testu błąd wróci przy każdej regeneracji modelu.

#### S3-ppoz-02 – Parter: klatki A i B przez jeden hol; klatka C i M1 bez wyjścia
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · S3 ppoż. · rewizja_spec · grupa G6*

- **Dowód (dane v1.2).**
  - Według `rdzenie.A.sklad` przedsionek A ma drzwi pd. do Hali.
  - Trzon B (u 24,85–31,10 × v 0,50–9,90) otaczają: od pd. segment z rampą (posadzka rampy pod trzonem ok. −2,0…−2,6), od wsch. P1, P2 i szacht, od pn. Hala i kancelaria (u 28,0–33,25 × v 10,05–16,9), od zach. Hala. Obie klatki wychodzą więc do jednego holu.
  - Klatka C ma tylko drzwi przedsionka z korytarza (lico d 8,40). M1 na P nie ma drzwi zewnętrznych i jest odcięty bramą.
  - Skutki: z końca skrzydła na kond. 1–4 (s ok. 1) do przedsionka A jest ok. 55–65 m w jednym kierunku (limit 30 m dla ZL III), a MDS na 260 os. na −1 traci jedyną klatkę z wyjściem.
- **Wymaganie.** WT § 256 ust. 6: ewakuacja przez hol jest dopuszczalna tylko z jednej klatki. Potwierdza to odpowiedź Organizatora (Wyj. 20 odp. 78), a ppoz.md podaje to w D9 i jako typowy błąd w pkt 16.7. Ponadto § 246 ust. 1, § 250 ust. 1 (zabezpieczenie przed zejściem do podziemia), § 256 ust. 2 oraz rozp. MSWiA z 2009 r. § 12 ust. 4.
- **Poprawka.**
  - (a) Przez Halę wychodzi tylko klatka A, z warunkami § 256 ust. 6. Wszystkie drzwi do Hali mają klasę EI 30 (także nowe połączenia, K-14), a łącznik do foyer zamyka się drzwiami EI 30 na elektrotrzymaczach.
  - (b) Klatka B: drzwi 1,2 m z podestu parteru (v ok. 5,9–7,4) w licu zach. u 24,85, poniżej słupa. Za nimi korytarz EI 60 o szer. 1,6 m: odcinek u 21,0–24,85 × v 5,8–7,4 i odcinek u 19,4–21,0 × v 0–7,4, razem ok. 11 m i ok. 18 m² zabrane z Hali. Drzwi zewnętrzne ≥ 1,2 m otwierają się na zewnątrz w licu pd. między filarami u 18,9 i 21,6, na dziedziniec 119,25.
  - (c) Klatka C: drzwi 1,2 m z podestu parteru w licu d = 15 (s ok. 5,0–6,5), poza pasem EI 60 z S3-ppoz-10. Korytarz KW.P.16 dostaje drzwi 1,2 m do bramy. Po obniżeniu M1 (F1-komunikacja-10) stopnie są zbędne (K-13).
  - (d) W klatkach A i B na P drzwi E 30 albo barierka przy biegu w dół (§ 250 ust. 1).
- **Ryzyko.** Niezgodność wprost z odpowiedzią Organizatora, widoczna na planszy P3. Bez poprawki (c) cała ewakuacja skrzydła i MDS jest wadliwa. Korytarz z pkt (b) koliduje z pokojem cichym z F1-komunikacja-01 i zbliża się do osi Hali na 1,34 m. Rozstrzygnięcia są w K-4 i K-5. Koszt < 0,1 mln zł, bryła bez zmian.

#### S3-ppoz-03 – Sale konferencyjne 200 os. (2 × 100) i 80 os. bez wymaganych wyjść
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · S3 ppoż. · rewizja_spec · grupa G1 (wdrożenie łączne – pakiet G1 przy F1-komunikacja-02)*

- **Dowód.**
  - SK.01 (205,2 m², 200 os.) ma jedne drzwi 1,6 m do klina KW.P.15, który nie ma innych drzwi.
  - SK.02 (95,9 m², 80 os.) i reżyserki SK.03 i SK.04 nie mają drzwi.
  - Spec. v1.2 (rozdz. 6, `parter.skrzydlo`) nie określa wyjść. Znane P-D5 dotyczy tylko powierzchni sali.
  - Lico od Mazowieckiej stoi na granicy, a chodnik ma 118,33–118,70. Drzwi otwierane na zewnątrz nie mogą otwierać się nad pasem drogowym, więc jedynym kierunkiem jest dziedziniec. Teren przy licu d = 15 ma tam 118,84–119,02.
  - Drzewa D897 i nr 60 są usuwane (G-I-2), D886 zostaje.
- **Wymaganie.** WT § 238: ≥ 2 wyjścia w odstępie ≥ 5 m z pomieszczenia dla > 50 os. Każda połowa sali po podziale ścianą mobilną jest osobnym pomieszczeniem. Ponadto § 239 (0,6 m na 100 os., drzwi otwierane na zewnątrz) i § 236 ust. 4. Teza zgłoszenia, że cały parter musi spełniać wymagania ZL I, jest przesadzona, ale nie zmienia wyniku.
- **Poprawka.** Pakiet G1 (opis przy F1-komunikacja-02).
- **Ryzyko.** Zgromadzenia > 50 os. bez drugiego wyjścia to błąd, który rzeczoznawca wskazuje jako pierwszy. Koszt ok. 7 drzwi i spoczników, ok. 0,10–0,15 mln zł, liczony raz dla G1.

#### S3-ppoz-04 – Garaż −2: jedno faktyczne wyjście i przejście > 40 m bez tryskaczy
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · S3 ppoż. · rewizja_spec*

- **Dowód.**
  - (1) Z końców stanowisk skrzydła na −2 (s 12,4; d 0,75–14,25) do drzwi przedsionka A jest 45,3–50,4 m w linii prostej, a do przedsionka B ≥ 47,6 m (`audyt_kf/gp/park2.py`). Droga rzeczywista ma ≥ 50 m (weryfikacja 1: 41,2–51,4 m od środka stanowiska, ok. 54 m od dalszego końca).
  - (2) Do przedsionka B na −2 nie da się wejść zgodnie z przepisami. Od pn. (v 9,9) i wsch. (u 31,1) przylega maszynownia GPC (rect_uv 24,85–34,6 × 9,9–16,6 oraz 31,1–34,6 × 0,6–9,9). Od zach. słup (24,0–24,6; 8,53–8,88) zostawia szczelinę ok. 0,88 m < 0,9 m, bez pola manewrowego. W efekcie −2 (2 101 m², 40 stanowisk, ukrycie ≤ 300 os.) ma faktycznie jedno wyjście, przez klatkę A. Na −1 wejście od pn. jest możliwe przez wolny pas v 9,9–11,6.
  - Rezygnacja ze stanowisk w skrzydle daje 103 < 106 m.p., więc odpada.
- **Wymaganie.** WT § 278: przejście ≤ 40 m. Zwiększenie o 50 % przysługuje tylko przy tryskaczach albo samoczynnym oddymianiu, a według ppoz.md rozdz. 8 nie przy wentylacji strumieniowej. Ponadto ≥ 2 wyjścia, § 239 ust. 3 oraz V12-OPEN 3 (ukrycie).
- **Poprawka.**
  - (1) Na −2 drzwi EI 30 1,0 m w licu pn. przedsionka B (u ok. 25,2–26,2). Pole 1,5 × 1,5 m przed nimi wyciąć z GPC (ok. 2,3 m², maszynownia z 97,3 do ok. 95 m²). Dalej wolnym pasem u 22,5–24,85 × v 9,9–11,4 do drogi łącznika (u 16,5–22,5), bez utraty stanowisk. Na −1 analogiczne drzwi północne.
  - (2) Dla −1 i −2 zadeklarować samoczynną wentylację oddymiającą kanałową sterowaną z SSP (limit 60 m): kanały ≤ 0,70 m pod płytą (2,70 − 0,70 = 2,00 m, minimum z § 102), kurtyny dymowe, wyrzut w szachcie B po odciążeniu (S3-ppoz-07). Dopłata ok. 0,15–0,25 mln zł.
  - (3) Wariant odporny, gdyby rzeczoznawca nie przyjął oddymiania przy 2,70 m: tryskacze OH2 tylko w garażu (także pod platformami stackerów), ok. 0,45 mln, plus zbiornik większy o ok. 45 m³ (ok. 0,15 mln), razem ok. 0,6 mln. Ten wariant zamyka też ryzyko EV i stackerów.
- **Ryzyko.** Dwie niezgodności z przepisem na planszy P3. Wybór (2) albo (3) decyduje o wielkości zbiornika ppoż. (K-6), obciążeniu szachtu B (S3-ppoz-07) i o tym, czy wolno stawiać ładowarki na platformach (F3-garaz-technika-03). Poprawka (1) razem z rampą 6,0 m z F3-garaz-technika-01 obniża powierzchnię GPC do ok. 76 m² (K-11).

#### F1-komunikacja-02 – Strefa konferencyjna bez dojścia z holu i bez wyjść
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · F1 komunikacja · rewizja_spec · grupa G1 (prowadzący)*

- **Dowód.**
  - Spec. v1.2: strefa foyer przylega do lica wieży tylko w v 4,6–16,0, a „łącznik do foyer” (v 21–29,2) sąsiaduje z bistro. Sala 80 sąsiaduje wyłącznie z bramą i salą 200, więc wewnątrz budynku dostępna jest tylko przez salę 200.
  - Model: SK.06 nie łączy się z halą; jedyne drzwi na obwodzie foyer prowadzą do PR.01, SW.05, SW.08, SK.05 i SK.07. Wejście konferencyjne w dziobie prowadzi przez salę bistro.
  - Wynika to z terenu: chodnik przy s 46–50 ma 119,03–119,06, a przy s 58 119,18 (NMT), więc spec. (h) dopuszcza tam wejście tylko w dziobie. Główną drogą gości musi być hala.
- **Wymaganie.** WT § 238 i § 239 ust. 2 pkt 3; program rozdz. 8 („SK bezpośrednio przy holu”, niezależne użytkowanie sal; PU s. 8–9). Teza zgłoszenia, że sala ZL I nie może być drogą dla drugiej sali, nie ma podstawy w WT.
- **Poprawka – pakiet G1** (rozstrzygnięcie redakcyjne łączące S3-ppoz-03, F1-komunikacja-02 i F2-program-biura-01; kolejność sal wg F1-02, metoda osadzenia drzwi wg F2-01):
  1. **Kolejność w skrzydle od Maz. 19:**
     - M1;
     - brama (s 12,15–16,20);
     - sala 200: s 16,35–32,85, 231 m² brutto, reżyserka jako wnęka 2,5 × 4,0 m, netto ok. 221 m² ≥ 220 m² (zamyka P-D5);
     - sala 80: s 33,0–40,6 × d 0,5–12,4, 90,4 m², z kuluarem 1,95 m (d 12,55–14,5) od foyer do drzwi sali 200;
     - foyer od s 40,8, z szatnią 20 m² i reżyserką sali 80; magazyn mebli na −1.

     Konstrukcyjnie zmiana jest neutralna: płyty 0,40 m o rozpiętości 14,2 m nie mają słupów pośrednich.
  2. **Ściana mobilna** sali 200 na filarze konstrukcyjnym s 24,30, a nie w szybie (por. F2-01: s 31,5 trafia w okno 30,79–31,99). Połowy mają ok. 7,95 i 8,40 m szerokości.
  3. **Wyjścia.** Drzwi otwierane na zewnątrz. W miejscu okna: skrzydło 1,0 m (≥ 0,9 m w świetle) przy zewnętrznym ościeżu i kwatera stała 0,20 m. Przy takim osadzeniu drzwi w modułach k i k+3 dzieli w świetle 5,28 m.
     - połowa pd. sali 200: drzwi na dziedziniec w module s 22,69 oraz drzwi do bramy w ścianie s 16,35 (d ok. 12–13, przedsionek 1,5 m z 3 stopniami po 0,135 m, jak w F2-01), odstęp ok. 6,8 m. Wariant ten omija strefę korzeni D886 (s 15,8; d 17,3). Wariant z drugim wyjściem na dziedziniec w module s 16,61 wymaga zgody arborysty, bo podest wypada ok. 1,1 m od pnia;
     - połowa pn.: drzwi na dziedziniec w module s 26,74 i drzwi do kuluaru w ścianie s 32,85, odstęp ok. 5,2 m;
     - sala 80: drzwi do foyer (ściana s 40,6) i do kuluaru (ściana d 12,4), odstęp ≥ 5 m;
     - reżyserki dostają drzwi do foyer albo kuluaru; usunąć drzwi PR.01→SK.06 i SW.05→SK.06; SW.08 otworzyć na salę bistro.
  4. **Teren.** Przed drzwiami dziedzińcowymi spoczniki 1,5 × 1,5 m na 119,28 (próg ≤ 2 cm) i chodnik albo taras ze spadkiem ≤ 4–5 % do terenu 118,85–119,03, na stropie pasa −1 i w pasie po usuniętych drzewach 60, 61, 62, 67 (G-I-2). W każdej sali przynajmniej jedno wyjście bez progu. Dalej ewakuacja przez bramę ogrodową do Mazowieckiej: 4,05 m wobec 0,6 m × 2,8 = 1,7 m.
  5. **Hala–foyer.** Przejście 2,95 m w świetle w pasie u 0,5–8,15 × v 8,9–11,85, między licem słupa v 8,70 a ścianą pd. trzonu A (v 11,85), z drzwiami EI 30 na elektrotrzymaczach (K-14).
     - rowerownia: v 0,5–6,5 (45,9 m²);
     - PR.02: v 6,5–8,5 (15,3 m²) (K-2);
     - WC konferencyjne: v 12,45–20,85 (F2-program-biura-02).

     Drugie połączenie: otwór ≥ 1,8 m foyer–bistro i dwuskrzydłowe drzwi SW.07→SW.01b 1,8 m (F2-01). Wejście w dziobie opisać jako boczne.
  6. **Widownia i testy.** 200 i 80 krzeseł w blokach ≤ 16 miejsc w rzędzie, przejścia 1,2 m, rozstaw rzędów 0,90 m. Test generatora: pomieszczenie dla > 50 os. ma ≥ 2 wyjścia w odstępie ≥ 5 m w świetle krawędzi.
- **Ryzyko.** Bez G1 centrum konferencyjne nie spełnia programu ani WT. Wariant z F2-01 przy dawnej kolejności sal zostawia salę 80 bez wewnętrznego dostępnego połączenia z foyer: tylko z dziedzińca albo bramy ze stopniami. Dlatego redakcja przyjmuje kolejność z F1-02.

#### F1-komunikacja-10 – Parter M1 niedostępny bez schodów
*Waga: KRYTYCZNY (zgł. ISTOTNY; podwyższono w weryfikacji 2) · F1 komunikacja · rewizja_spec · grupy G6, G7*

- **Dowód (spec. v1.2, nie tylko model).**
  - Brama (s 12,15–16,20) zajmuje całą głębokość parteru (d 0–15) na wysokość 4,80 m. Posadzka bramy ma 118,70–118,90, a M1 119,30, czyli uskok 0,40–0,60 m (ok. 0,49 m przy KW.P.16).
  - Spec. (h) dopuszcza wejścia tylko tam, gdzie różnica wynosi ≤ 0,15 m. Lista 8 wejść nie obejmuje M1, a chodnik Mazowieckiej przy M1 ma 118,62–118,69.
  - V12-I5C usunęła szyb C1. W efekcie DW (2 pokoje po 3 stanowiska), technicy (3 stanowiska) i socjal są dostępni tylko po schodach.
  - Klatka C (także dla MDS na 260 os.) wychodzi na zewnątrz tylko korytarzem M1 do bramy, przez ten sam uskok.
- **Wymaganie.** Regulamin III.1.8: R-036 (wejścia z poziomu chodnika bez schodów) i R-037 (pełna dostępność poza pomieszczeniami technicznymi); WT § 54 ust. 2.
- **Poprawka.**
  1. Obniżyć posadzkę parteru M1 (s 0–12,15) do poziomu bramy przy drzwiach: ok. 118,82–118,85 (−0,45…−0,48 m). Wejście z bramy bez progu (≤ 2 cm), drzwi automatyczne z kontrolą dostępu (F1-07).
  2. Na −1 pod M1 zostaje ok. 3,20 m w świetle zamiast 3,65 m, co wystarcza dla magazynu MDS, trzonu C i dróg. Pod M1 nie ma rzędów stackerów.
  3. Klatka C:
     - −1/P = 3,75 m: 2 × 11 stopni po 17,05 cm;
     - P/1 = 5,25 m: 30 stopni po 17,5 cm w trzech biegach 10+10+10;
     - przy obniżeniu −0,48 m: 31 stopni po 17,03 cm (11+10+10), długość 2,80 + 3,00 = 5,80 m.
  4. Od Mazowieckiej cokół zostaje jako element elewacji.
  5. Pierwszą jednostkę stackerów pod bramą (s 12,2–17,2) skreślić. Strata jest wspólna z S1-konstrukcja-08 (−2 m.p.), liczona raz.
- **Ryzyko.** To niezgodność z obligatoryjnym wymaganiem regulaminu na poziomie koncepcji. Wariant „DW na kond. 1” jest niewykonalny, bo pojemność elewacyjna to 218 jednostek przy 216 zajętych. Koszt pomijalny.

#### F2-program-biura-01 – Centrum konferencyjne w modelu: brak drzwi, foyer jest wyspą, zawyżona widownia
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · F2 program · agent_rzutow · grupa G1*

- **Dowód.**
  - Na P jest 19 drzwi, z czego żadne nie należy do SK.02. Uwaga modelu przy SK.02 („wejście z bramy ogrodowej i z sali 200”) nie trafiła do generatora drzwi.
  - SK.01 ma jedne drzwi 1,6 m do KW.P.15 (14,46 m²), które nie mają innych drzwi; lico v = 0 jest pełne. Połowa pd. sali po podziale nie ma żadnego wyjścia.
  - Z foyer wychodzi się dziś tylko przez rowerownię PR.01 (wejście nr 6) albo zaplecze bistro SW.08. Wnęka wejścia konferencyjnego dotyka wyłącznie SW.07, 5,32 m od SK.06.
  - Szablon „chairs” w `rzuty.py` rysuje w SK.01 336 krzeseł (16 rzędów × 21), a w SK.02 126, bez przejść i z prześwitem 0,46 m.
- **Wymaganie.** WT § 238; ppoz.md 5.5 (stosować § 261: ≤ 16 miejsc między przejściami).
- **Poprawka.** W modelu i generatorze wdrożyć pakiet G1. Ograniczenia geometryczne z weryfikacji 2:
  - okna dziedzińcowe leżą w modułach co 2,025 m (np. s 16,61 / 18,64 / 20,66 / 22,69 / 24,71 / 26,74 / …);
  - przy drzwiach osadzonych w środku otworu odstęp w świetle spada do 4,875 m < 5 m, dlatego skrzydło trzeba osadzić przy ościeżu;
  - ścianki i ściana mobilna stają na filarze albo na słupku (por. F2-program-biura-03).

  Szablon widowni: 200 i 80 krzeseł w blokach ≤ 16, przejścia 1,2 m. Test: „pomieszczenie > 50 os. ⇒ ≥ 2 wyjścia w odstępie ≥ 5 m w świetle krawędzi”.
- **Ryzyko.** Rzut P pokazuje 336 miejsc w sali „na 200 os.”, co jest sprzeczne z opisem i z ppoz.md. Kosztów konstrukcyjnych nie ma, bo słupy i nadproża w skrzydle zostają.

#### F3-garaz-technika-01 – Rampy jednopasowe z sygnalizacją wahadłową niezgodne z WT § 103
*Waga: KRYTYCZNY (zgł. KRYTYCZNY) · F3 garaż · rewizja_spec*

- **Dowód.**
  - WT 2002 (t.j. Dz.U. 2022 poz. 1225, kopia lokalna) § 103 ust. 2: przy ponad 25 samochodach na kondygnacji wymagana jest pochylnia dwukierunkowa ≥ 5,5 m albo dwie jednopasmowe ≥ 2,7 m (na wjazd i na wyjazd). Ust. 3 dopuszcza jedną pochylnię jednopasmową z sygnalizacją tylko do 25 samochodów.
  - Projekt ma 70 m.p. (73 pozycje) na −1 i 40 na −2, a rampa uliczna (3,5 m, „wahadłowa”) i wewnętrzna (3,5 m) są jednopasowe.
  - Weryfikacja I-1 sama zaleciła rampę jednopasową, G-I-1 ją przyjął, a E-K-1 zaksięgował oszczędność −0,15 mln. Problem nie był więc wcześniej znany.
  - Brama stoi 0,50–0,60 m od granicy, krawężnik 4,84–5,42 m od bramy, więc auto o długości 4,74 m czekające na zielone zajmuje cały chodnik bulwaru.
- **Wymaganie.** WT § 103 ust. 2–3; projekt WT § 101 ust. 2–3 brzmi identycznie.
- **Poprawka.**
  1. Rampa uliczna dwukierunkowa 5,5 m (6,0 m w świetle odbojów). Brama ≥ 6,0 m cofnięta 1,5–2,0 m za lico, z ukośnymi ościeżami. Pas −1 pod dziedzińcem lokalnie poszerzony (u ok. 8–22) do v −7,35: +30,7 m² i ok. 19 m ściany szczelinowej. Drzewa nr 3 i 4 zostają 5,85 i 6,66 m od lica, czyli bez kolizji.
  2. Parter segmentu – wariant zalecany: parterowe poszerzenie segmentu o 1,5 m na pd. (ściana bez otworów 3,08 m od dz. 10/2 ≥ 3,0 m wg WT § 12; wysokość ok. 5 m, bez poszerzania wyższych kondygnacji ze względu na zapas § 13 wobec WS 5). Pas parteru rośnie do ok. 55 m² i mieści trafo 21 m² (drzwi od Wybrzeża), przedsionek T z przyjęciem towaru 12–15 m² i korytarz.
     - Rozdzielnię nn z SZR przenieść na kond. 1 segmentu jako odrębną strefę (WT § 212 ust. 9).
     - [red., K-7] BESS na kond. 1 tylko przy pojemności ≤ 60 kWh (proj. WT § 312); przy 100 kWh BESS zostaje na parterze.
     - Wariant bez zmiany bryły: trafo nad rampą w zach. końcu segmentu (u 21–25,7).
  3. Kondygnacja −2. Rampa wewnętrzna 6,0 m wymaga przeniesienia centrali S z podziemia na kond. 1 i odtworzenia ok. 19 m² GPC (K-11, K-12). Alternatywa dopuszczona przez § 103 ust. 1: dźwig samochodowy w kieszeni u 34,6–38,5 (szyb ok. 3,4 × 6,6 m, ok. 40 pojazdów/h, w szczycie kolejka 2–4 aut). Zwalnia ok. 34 m² na −1 i ok. 51 m² na −2.
  4. Nie zakładać odstępstwa z art. 9 Pb.
- **Ryzyko.** To decyzja przekrojowa. Wpływa na parter segmentu (S3-ppoz-08, -09, F3-05, F3-06), konstrukcję segmentu nad bramą (S1-06, K-8), kieszeń wsch. wieży (S1-01, K-17), maszynownię GPC (S3-ppoz-04) i koszt. Szacunek ok. +0,65 mln: +0,15 cofnięcia dźwigni „rampy jednopasowe”, ok. 0,25 poszerzenia pasa, ok. 0,25 poszerzenia parteru. Ustalenie liczy zapas z v1.1 (0,82 mln), a obowiązuje 1,01 mln (K-19).

### 2.2. ISTOTNE

#### S1-konstrukcja-01 – Sala Sejmiku: ruszt dachu, antresola i galeria bez drogi obciążeń
*Waga: ISTOTNY (zgł. KRYTYCZNY) · S1 konstrukcja · kondygnacja_S2*

- **Dowód (spec. v1.2, JSON `kondygnacja_sejmiku`, `kondygnacja_S2.md` pkt 9.7; skrypty `audyt_kf/weryfikacja_S1.py`, `kf2/kf2_obl.py`).**
  - Rozdz. 5 i JSON `siatka.wieza.dach_S` mówią: „rozpiętość 19,5 m … oparty na ścianach trzonów, ścianie pd. sali i filarach łuku; słupy wewnętrzne kończą się na stropie S”. 19,5 m to szerokość sali z v1.0. W S-3 sala ma u 22,0–39,5 × v 12,6–29,2, a S2 pkt 9.7 opisuje inny układ: kratownice wsch.–zach. 17,5 m na podciągu 10 m nad otworem galerii. Opisy są sprzeczne.
  - Trzony do sali nie sięgają: A kończy się na u ≤ 15,50, B na v ≤ 9,90.
  - Ściana pd. (v 12,30–12,60) stoi 3,75 / 3,55 m od osi v 8,70 / 16,00, a ściana zach. (u 21,70–22,00) 5,65 / 2,45 m od osi u 16,2 / 24,3. Obie stoją na płycie 0,28 m poza liniami słupów kond. 6.
  - Ściana żelbetowa działa jak belka-ściana, więc krytyczne są nieokreślone podpory końcowe. Przy dachu 7,9 kN/m² w SGN, kratownicach pn.–pd. 17,25 m, antresoli i ciężarze ściany obciążenie to ok. 172 kN/m na 24,2 m, czyli reakcja ok. 2,1 MN na każdym końcu.
  - Wsch. koniec (39,5; 12,45) leży 3,25 m od słupa łuku 0° i 3,75 m od (40; 8,70), a końce podciągu galerii (21,85; 12,6) i (21,85; 22,65) wypadają na samej płycie (ok. 390 kN każdy).
  - Płyta 0,28 m ma nośność ok. 230 kNm/m przy As 2 500 mm²/m i takich sił skupionych nie przeniesie.
- **Wymaganie.** Ciągłość drogi obciążeń do fundamentu (PN-EN 1990 p. 2.1; PN-EN 1992-1-1 p. 5.1); siły skupione i przebicie (PN-EN 1992-1-1 p. 6.4); opis konstrukcji obowiązkowy w części opisowej (R-117 b); klasa B: R 120 dla głównej konstrukcji.
- **Poprawka.**
  1. Kratownice dachu S tylko w kierunku pn.–pd., na całej szerokości u 15,5–39,5, od lica pd. (v 12,45) do elewacji pn. (v 29,70) i łuku. Rozpiętość ≤ 17,25 m (L/h = 10,8). Pn. końce oprzeć na stalowej belce obwodowej w pasie attyki, na słupach R 13,5 (co 3,53 m) i na słupie (24,3; 29,7).
  2. Ściana zach. sali przestaje być podporą: wykonać ją jako lekką przegrodę akustyczną, a podciąg 10 m z S2 pkt 9.7 skreślić. Kratownica lub Vierendeel „nad balustradą” weszłaby w otwór galerii, w którym oczy rzędów są na +32,10 i +33,00.
  3. Ściana pd. jako żelbetowa belka-ściana 0,30–0,35 m na u 15,5–39,7 (24,2 m).
     - wysokość czynna od nadproży (+29,70) do pasa górnego kratownic (+35,75) ok. 6,0 m, L/h ok. 4;
     - cięgno ok. 2,4 MN (ok. 12 Ø25 albo 2 kable) w paśmie +29,70…+30,90;
     - VEd ok. 2,1 MN wobec VRd,max ok. 9 MN;
     - podpory: ściana trzonu A u = 15,50 (lokalnie 0,30 m) oraz nowy słup 0,60 × 0,60 m w filarze elewacji wsch. (v ok. 12,5–13,5), ciągły do płyty −2. Na −1 i −2 słup stoi w strefie ściany szczelinowej u 39,4–40,0;
     - drzwi dolne leżą poniżej cięgna; drzwi galeria–korytarz (17,5; +30,90) leżą w strefie podporowej i trzeba je obramować.
  4. W rozdz. 5 i JSON `dach_S` wpisać nowy opis podpór. Tarczę i słup dorysować na przekrojach A-A i B-B.
- **Ryzyko.** Brak drogi obciążeń w najbardziej eksponowanym elemencie budynku. Wagę obniżono, bo poprawka mieści się w istniejących ścianach i nie zmienia rzędnych. Koordynacja: kanały EIS z S3-ppoz-07 nie mogą przechodzić przez cięgno (K-9), a słup na −1/−2 nie może zwężać rampy 6,0 m (K-17). Koszt ok. 0,1–0,2 mln.

#### S1-konstrukcja-03 – Pierścień R 7,0 bez przejęcia; słupy w osi Bramy
*Waga: ISTOTNY (zgł. ISTOTNY) · S1 konstrukcja · rewizja_spec · grupa G5*

- **Dowód (`audyt_kf/kf2/hala_os.py`, `luk_rozp.py`).**
  - Rozdz. 5 i JSON `siatka.wieza.luk`: słupy co 15° na R 13,5 i R 7,0, bez informacji, że pierścień R 7,0 kończy się nad parterem.
  - `budynek.json`: 7 słupów R 7,0 na kond. 1–6, zero na P, −1 i −2. Daje to ok. 1,5–1,6 MN na słup, razem ok. 10,4–11 MN do przejęcia na +4,65. Przejęcia w spec. nie ma, a byłoby sprzeczne z 4,37 m w świetle Hali i z zapisem „bez belek transferowych” garażu v1.1. Sprowadzone w dół, 6 z 7 słupów trafiłoby w drogę A2 (v 16,6–22,6).
  - Na osi Hali (drzwi w łuku: u 33,78; v 23,48) stoją: słup R 13,5/45° (35,55; 25,25) 2,50 m przed drzwiami, 0,02 m od osi; słup R 7,0/45° (30,95; 20,65) 4,0 m za drzwiami; słup siatki v1.1 (32,40; 23,15) 1,21 m za drzwiami, 0,74 m od osi, czyli w świetle wiatrołapu. To pogorszenie wprowadziło przesunięcie osi v 21,60 → 23,15.
  - W pasie ±3 m od osi stoją też słupy (24,3; 16,0) i (16,2; 8,70), 1,34 i 1,83 m od osi. Zapis rozdz. 11 „oś bez przeszkód ≥ 6 m” jest więc nieprawdziwy.
- **Wymaganie.** PN-EN 1990 p. 2.1; spójność z tab. 4.2; idea „prostej osi most → ogród” (rozdz. 1, 2 poz. 15); rozdz. 11; ścieżka prowadząca wolna od przeszkód (dostepnosc.md, PN-ISO 21542).
- **Poprawka.**
  1. Usunąć pierścień R 7,0 na wszystkich kondygnacjach; ściany korytarza łukowego zostają działowe.
  2. Usunąć słup (32,40; 23,15) na poziomach od −2 do 6. W garażu zwalnia to rząd R4 bez utraty miejsc.
  3. Usunąć słup R 13,5/45°. Największe puste koło w strefie łuku rośnie z 5,39 do 6,13 m, co odpowiada przęsłu ok. 8,7 m, czyli granicy płyt 0,28 m. Przęsło podcienia 30°–60° (cięciwa 6,99 m) przenosi belka ok. 0,45 × 0,90 m w granitowym nadprożu (rozdz. 3 poz. 10), a na kond. 1–6 belka w paśmie ceramiki 1,30 m.
  4. Rozdz. 11: „pas osi ≥ 2,0 m wolny od przeszkód; słupy (24,3; 16,0) i (16,2; 8,70) jako kolumnada”. Test pasa opisano w K-5.
  5. Poprawić rozdz. 5, JSON `luk`, rzuty P, 1–6, −1, −2, przekroje oraz kadry W3 i W6.
- **Ryzyko.** Słup tuż za wejściem głównym i filar przed nim w osi Bramy widać na rzucie P i w kadrach. Sąd złożony z architektów to wytknie. Bez poprawki zostaje albo palisada słupów z kolizją w garażu, albo nieopisane przejęcie ok. 10 MN.

#### S1-konstrukcja-08 – Strop nad −1 wyżej niż posadzka bramy ogrodowej
*Waga: ISTOTNY (zgł. ISTOTNY) · S1 konstrukcja · rewizja_spec · grupa G7*

- **Dowód.**
  - (a) Strop nad −1 ma wierzch −0,15 = 119,15 (tab. 4.2, zakres „całość”; JSON `kondygnacje[-1]`). Kondygnacja −1 obejmuje skrzydło od s ok. 1,2, a −2 zaczyna się od s 12,15, czyli dokładnie pod bramą (s 12,15–16,20).
  - Posadzka bramy ma 118,70 → 118,90 (rozdz. 2 poz. 9; rozdz. 11: spadek ≤ 2 %), czyli leży 0,25–0,45 m poniżej wierzchu konstrukcji. W opisanej postaci rozwiązanie jest niewykonalne.
  - Uskok do ≤ 118,45 zostawia na −1 2,95 m w świetle, mniej niż 3,50 m wymagane dla stackerów. W rzędzie skrzydła (`STACK_ROWS_M1`, sd 12,2–54,0) mieści się wtedy 7 jednostek zamiast 8, czyli −2 m.p. Bilans spada ze 110 do 108, a pogłębienie −1 jest niemożliwe, bo pod spodem jest −2.
  - (b) Przy drzwiach ogrodowych nawierzchnia na 119,28 zostawia nad stropem tylko 0,13 m.
  - Części (c) i (d) zgłoszenia odrzucono: na stropie pasa przewidziano taras bez nasadzeń, a strop 0,40 m ma L/h 34–35.
- **Wymaganie.** Wykonalność warstw nad stropem podziemia (hydroizolacja białej wanny, warstwa drenażowa, nawierzchnia); wysokość pod stackerami ≥ 3,50 m (JSON `stackery.wys_w_swietle_min_m`); bilans MPZP § 13.
- **Poprawka.**
  1. Uskok stropu nad −1 w pasie s 12,15–16,20 × d 0–15 do wierzchu ≤ 118,45 (granit 0,08 + podsypka 0,05 + warstwa ochronno-drenażowa 0,07 + spadek). Ściany albo belki uskoku dać w osiach portalu s 12,15 i 16,20.
  2. Rząd stackerów zach. zacząć od s ≥ 16,5 (7 jednostek). Bilans 108 m.p. wpisać do rozdz. 12, rozdz. 16 pkt 10, JSON i F.15.
  3. Strop pasa dziedzińca ze spadkiem konstrukcyjnym 1,5 % od lica wieży (119,15 → 119,08), nawierzchnia na 119,28 przy drzwiach ogrodowych; nad stackerami R1 zostaje ≥ 3,55 m.
  4. W tab. 4.2 dodać wiersz „strop −1 pod bramą ogrodową: wierzch 118,45” i pokazać uskok na przekroju przez bramę.
- **Ryzyko.** Strata 2 miejsc zjada połowę zapasu bilansu (rozdz. 5.5). Rzędne stropu trzeba ujednolicić z F1-komunikacja-10 (strop pod M1 ok. 118,70) i F3-garaz-technika-03 (R1) – K-18.

#### S3-ppoz-07 – Brak szachtów wentylacji pożarowej w trzonach; szacht B przeciążony
*Waga: ISTOTNY (zgł. ISTOTNY) · S3 ppoż. · rewizja_spec*

- **Dowód.**
  - Trzon A (`rdzenie.A.uklad_uv`): wnętrze 6,70 × 8,55 m wypełniają w 100 % A1, A2, R (v 18,05–20,60), klatka i przedsionek (v 12,05–17,85) oraz ścianka 0,20 m. Na szachty nadciśnienia, oddymiania korytarzy i pionów, które wymienia rozdz. 5, zostaje 0 m². Spec. 10 umieszcza tymczasem „wentylatory oddymiania korytarzy w szachtach trzonów A i B”.
  - Szacht B ma 2,15 × 3,20 = 6,88 m² brutto, ok. 6,0 m² netto. Obciążenie (szacunek inżynierski):
    - oddymianie garażu −1: ok. 23 m³/s, 2,3 m² przy 10 m/s, plus obudowa EI 120;
    - wyrzutnia zbiorcza: ok. 21 m³/s, 2,6–3,0 m²;
    - piony centrali S: ok. 1,4 m²;
    - spaliny: ok. 0,2 m²;
    - nadciśnienie klatki i przedsionka B: ok. 0,5 m².

    Razem ok. 7,0–7,5 m² netto, czyli więcej niż mieści szacht.
  - Oddymianie korytarzy kond. 1–6 oraz nadciśnienie przedsionków A i A' i szybu R nie mają trasy, bo S-3 nie przepuszcza żadnego pionu poza szachtem B (D8). Zarzut braku maszynowni odrzucono: wentylatory mogą stać w szachcie.
- **Wymaganie.** WT § 246 ust. 2 i § 253 ust. 4 (zapobieganie zadymieniu klatek, przedsionków i szybu R); § 247 ust. 1 (drogi poziome w budynku W); § 277 ust. 4; § 270 (E600S/EIS, F400/F600).
- **Poprawka.**
  1. W szachcie B zostawić oddymianie garażu (EI 120), spaliny agregatu, piony centrali S oraz nadciśnienie klatki i przedsionka B: ok. 4,4 m², z przegrodami ok. 5,2 m² ≤ 6,88 m².
  2. Nowy szacht SZ-1 ok. 5 m² (np. 2,2 × 2,3 m) w strefie środkowej, ciągły od P do S, z dwiema komorami:
     - wentylacja pożarowa ok. 2,0 m²: wielopunktowe nadciśnienie klatki A, przedsionków A i A' oraz szybu R, oddymianie i napowietrzanie korytarzy kond. 1–6;
     - wyrzutnia zbiorcza ok. 2,8 m².
  3. Lokalizacja SZ-1:
     - na S w obrysie WC PHS.05a/b (u 17,1–21,7 × v 12,5–20,85), WC zmniejszone z 42,5 do ok. 37,5 m² (≥ 35 m² programu);
     - wentylatory F400 w szachcie na poziomie S;
     - na kond. 1–5 kosztem strefy centrali piętrowej, na P kosztem komfortki (21,4 → ok. 16 m²).

     Potem przeliczyć bilans S (`_s2_geometria.py`).
  4. [red., K-9] Kanały EIS z SZ-1 na stronę pd. muszą przejść przez tarczę pd. sali (S1-konstrukcja-01). Zaproponowana trasa „pod stropem antresoli nad kuluarem” (ok. +29,80…+30,60) leży dokładnie w paśmie cięgna tarczy (+29,70…+30,90). Przejścia dopuszczalne są tylko w środkowej tercji rozpiętości i powyżej cięgna.
- **Ryzyko.** Bez szachtu rzeczoznawca nie przyjmie wentylacji pożarowej budynku W. Uwaga do listy „sprawdzone i poprawne”: wniosek F3, że szacht B jest wystarczający, dotyczy tylko zestawu bez wyrzutni zbiorczej i bez nadciśnienia.

#### S3-ppoz-08 – Brak zbiornika i pompowni wody ppoż.
*Waga: ISTOTNY (zgł. ISTOTNY) · S3 ppoż. · rewizja_spec · grupa G3*

- **Dowód.**
  - Ani spec. v1.2, ani `_rewizja_parking.py` (`LEVELS.plant`) nie mają zbiornika ani pompowni wody ppoż. Zdanie „pompowni tryskaczowej nie ma” (E-I-4) pominęło hydranty.
  - Rachunek: najwyższe zawory 52 na S leżą na 147,95 m n.p.m., a przyłącze ok. 117,5, czyli 30,5 m słupa wody (ok. 0,30 MPa). Do tego 0,20 MPa na zaworze, straty przy 10 dm³/s (DN 80, z kształtkami) ok. 0,08 MPa oraz zawór antyskażeniowy i wodomierz ok. 0,05–0,1 MPa. Razem ok. 0,6–0,65 MPa na przyłączu, więcej niż typowe 0,3–0,45 MPa w sieci.
  - Zawory na −2 (113,45) dostałyby ok. 0,69 MPa, czyli na granicy maksimum 0,7 MPa.
- **Wymaganie.** Rozp. MSWiA z 7.06.2010: § 19 ust. 6 (zawory 52 w budynku W), § 22 (≥ 0,2 MPa, ≤ 0,7 MPa), § 23 pkt 3 lit. a (4 zawory jednocześnie), § 24 ust. 2–5 (zapas ≥ 100 m³; 50 m³ przy sieci ≥ 10 dm³/s; 25 m³ przy ≥ 15 dm³/s i nasadzie 75 mm). Ust. 4 dotyczy tylko ZL IV. WT § 212 ust. 9: zbiorniki i pompy ppoż. jako odrębna strefa pożarowa.
- **Poprawka.** Zbiornik 25 m³ (warunek: MPWiK potwierdza ≥ 15 dm³/s, nasada 75 mm w elewacji wsch. przy wejściu PSP) albo 50 m³ przy 10–15 dm³/s. Zestaw pomp 1+1 (10 dm³/s × ok. 0,65 MPa), odrębna strefa REI 120 z drzwiami EI 60, reduktory albo strefowanie na −2. Na PZT 2 hydranty zewnętrzne DN 80, a w F.14.B pozycja ok. 0,25–0,30 mln zł.
  - [red., K-6] Lokalizacja z ustalenia (pas pd. segmentu na P, ok. 16 m² wolne) przestaje istnieć po rampie z F3-garaz-technika-01, bo pas spada do ok. 26,7 m² netto. Wariantem bazowym jest klin −2 z F3-garaz-technika-04.
- **Ryzyko.** To niezgodność z rozporządzeniem, choć bez wpływu na bryłę. Wariant z tryskaczami (S3-ppoz-04 pkt 3) zwiększa zbiornik o ok. 45 m³.

#### S3-ppoz-10 – Okna skrzydła przy ścianie oddzielenia od Maz. 19
*Waga: ISTOTNY (zgł. ISTOTNY) · S3 ppoż. · rewizja_spec*

- **Dowód.**
  - W `budynek.json` na kondygnacjach P–4 pierwsze okno leży w s 0,41–1,61 m zarówno od ulicy (d = 0), jak i od dziedzińca (d = 15). To samo daje `tools/elewacje.py` (oś 2,025 m, filar 0,825 m). Pełny pas między granicą a otworem ma więc tylko 0,41 m.
  - „Pierwsza oś cofnięta 0,30 m” nie wysuwa ściany oddzielenia poza lica obu budynków, bo fasada Maz. 19 leży w tej samej płaszczyźnie. Wysunięcie od ulicy jest niemożliwe (granica z dz. 8/8, zakaz nadwieszeń).
  - Po usunięciu pierwszego okna pokój 24 m² ma 1,20 × 2,35 = 2,82 m² szkła, mniej niż wymagane 3,0 m².
- **Wymaganie.** WT § 235 ust. 2 (wysunięcie 0,3 m albo pionowy pas ≥ 2 m EI 60 na całej wysokości); § 272 ust. 3; ppoz.md 11.2 (D14: cały pas po naszej stronie); WT § 57.
- **Poprawka.** Pierwsza oś (s 0,41–1,61) na obu licach P–4 jako przeszklenie stałe EI 60 (szkło i rama klasyfikowane, A1/A2). Filary i wypełnienia w pasie s 0–2,0 m jako NRO EI 60. Szkło EI 60 liczy się do pasa i do powierzchni okien wg § 57, a rytm 2,025 m zostaje. Opisać na elewacji 1:200 jako pas ppoż. wg § 235 ust. 2. Drzwi z klatki C (S3-ppoz-02) umieścić przy s ≥ 2,0.
- **Ryzyko.** Niezgodność z przepisem na styku z zabytkową kamienicą, widoczna na elewacji. Koszt ok. 28 m² szkła EI 60, ok. 0,12–0,15 mln zł.

#### F1-komunikacja-01 – Oś Hali i wejście ogrodowe zablokowane przez WC
*Waga: ISTOTNY (zgł. KRYTYCZNY) · F1 komunikacja · agent_rzutow · grupa G5*

- **Dowód (`budynek.json` kond. P, shapely).**
  - Oś z `koncepcja.json parter.os` biegnie od (u 33,78; v 23,48) do (u 10,0; v 0,0) i ma 33,42 m długości. Przecina blok WC PHS.04 (37,3 m²) na ok. 5,6 m, a pas osi ±3 m przecina go na 22,9 m².
  - Wnęka „Wejście ogrodowe” (u 8,6–11,4) styka się wyłącznie z PHS.04 i otwiera się do kieszeni zamkniętej skośną ścianą PHS.04 i ścianą rowerowni. Ścieżka FON przechodzi przez WC.
  - Pokój cichy SW.06 leży 0,86 m od osi.
  - Spec. v1.2 jest poprawna, bo WC konferencyjne umieszcza w strefie foyer. Błąd leży w modelu i na planszy P3.
- **Wymaganie.** Idea konkursowa: Brama jako przejście most → ogród, „z progu widać drzewa” (rozdz. 1, rozdz. 2 poz. 15); rozdz. 11; kadry W6 i W10. Wagę obniżono, bo przepis nie jest naruszony: Hala ma inne wyjścia.
- **Poprawka.**
  1. Usunąć PHS.04 i włączyć do Hali pas u 8,3–15,5 × v 0,5–11,85.
  2. WC konferencyjne w pasie wieży u 0,5–8,15 × v 12,45–20,85 (wg F2-program-biura-02, nie 38 m² wg ustalenia – K-3).
  3. SW.06 (16 m²) poza pasem osi i poza korytarzem klatki B. [red., K-4] Lokalizacja u 21,0–24,7 × v 0,5–6,5 z ustalenia koliduje z korytarzem EI 60 z S3-ppoz-02 (2,6 m² wspólne) i po przycięciu zostaje zamknięta. Przyjąć wariant alternatywny ustalenia: strona pn.-zach. osi przy bloku WC.
  4. Za drzwiami ogrodowymi pole 1,5 × 1,5 m poza skrzydłem drzwi; pas FON w osi.
  5. Test generatora pasa osi wg K-5; porównać kadry W6/W10 z rzutem.
- **Ryzyko.** Plansza P3 przeczy idei konkursowej, rozdz. 11 i kadrom. Wejście nr 5 prowadzi donikąd. To pierwsza poprawka do wykonania wśród istotnych.

#### F1-komunikacja-03 – Przerwany pierścień korytarza na kond. 1–4
*Waga: ISTOTNY (zgł. KRYTYCZNY) · F1 komunikacja · agent_rzutow · grupa G2 (część c)*

- **Dowód (`f03.py`, `f03_dist2.py`, Dijkstra na siatce 0,1 m).**
  - Na kond. 1–4 przy u 21,5–22,5 korytarz istnieje tylko w ramieniu pn. (v 21,18–22,98). Ramię pd. zajmują wieloboki resztkowe: na kond. 1 serwerownia IT.01 (37,7 m², 17 wierzchołków, L z ramieniem 1,21 × 14,2 m), na 2 pokój socjalny, na 3 archiwum PZGiK, na 4 pokój socjalny i budki.
  - Skutki: odległość do WC DOS.16 77,8 m, DOS.15 73,3 m (limit 75 m); do holu A1/A2 94,9 m. Po dodaniu brakującego odcinka korytarza (u 21,4–23,1) maksimum do WC spada do ok. 44 m, a do holu A do 58,8 m.
  - Ślepa odnoga 23–26 m wynika głównie ze starego układu trzonu A (znane V12-OPEN 1). Po przeliczeniu na v1.2 skróci się do ok. 8–10 m.
  - Część c, drzwi trzonów, pokrywa się z S3-ppoz-01, ale jest szersza: na żadnej kondygnacji nie ma drzwi klatka ↔ przedsionek (poza A na kond. 6), a klatka C nigdzie nie łączy się z przedsionkiem C.
- **Wymaganie.** Spec. rozdz. 6 (pierścień 1,80 m); rozp. w sprawie ogólnych przepisów bhp (Dz.U. 2003 poz. 1650) zał. 3: ustęp ≤ 75 m od stanowiska; WT § 256 ust. 2–3 (bez zwiększeń, bo tryskaczy nie ma); WT § 246 ust. 1.
- **Poprawka.**
  1. Drzwi trzonów jak w S3-ppoz-01.
  2. Zakazać pomieszczeniom resztkowym zajmowania pasa pierścienia (1,80 m) i łącznika do holu P1/P2.
  3. Na kond. 1 zwarta serwerownia 50 m² + UPS 15 m²; na kond. 2–4 archiwum i pokoje socjalne jako prostokąty (F2-program-biura-04).
  4. Przeliczyć ślepe końce (≤ 20 m poziomo) i dojścia 30/60 m. Drugi zespół WC przy trzonie B nie jest potrzebny.
- **Ryzyko.** Rzuty P4/P5 w obecnym stanie rzeczoznawca ppoż. odrzuci. Wagę obniżono, bo spec. jest poprawna, a błąd siedzi w generatorze.

#### F2-program-biura-02 – WC konferencyjne za małe i w złym miejscu
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · agent_rzutow*

- **Dowód.**
  - PHS.04 ma 37,3 m² i jest obróconym czworobokiem w Hali (u 8,27–15,52 × v 0,5–9,05). Wnęka wejścia nr 5 styka się wyłącznie z nim.
  - Potrzeba przyborów dla 280 os. (WT § 84 w brzmieniu z dostepnosc.md): 7 misek dla kobiet, 5 misek i 5 pisuarów dla mężczyzn, 14 umywalek, 2 kabiny dostępne, czyli ok. 55–60 m². W 37,3 m² mieści się ok. 55–60 % potrzeb.
  - Spec. rozdz. 6 umieszcza WC przy foyer, ale się tam nie mieści: przy WC 50 m² foyer spadłoby do ok. 47 m² < 60 m².
  - Część dotycząca PHS.02 (9,26 m² wobec ≥ 30 m²) jest już znana (P-I3).
- **Wymaganie.** WT § 84 ust. 2–3 (w brzmieniu przyjętym w `dostepnosc_checklista_projektowa.md` E8); program PHS.04: „liczba przyborów dostosowana do maks. liczby użytkowników (280 os.)” (PU s. 10).
- **Poprawka (bilans powierzchni zerowy).**
  1. Pas u 0,5–8,15 × v 12,45–20,85 (64,3 m² brutto, ok. 58 m² netto) na WC konferencyjne: 7 K, 5 M + 5 pisuarów, 2 kabiny dostępne, umywalki. Wejście z foyer przez istniejący otwór (u 0,5; v 13,25), piony przy trzonie A. PPT.05 przenieść na −1 (D4), SW.04 i SW.05 do łącznika (D15).
  2. [red., K-2] PR.02 (15 m²) nie w v 10,35–12,3, jak w ustaleniu, bo tam biegnie przejście hala–foyer z G1 (11,5 m² kolizji). Przyjąć v 6,5–8,5 (15,3 m²), a rowerownię v 0,5–6,5 (45,9 m²). 50 rowerów mieści się w 2 rzędach stojaków dwupoziomowych: 2 × 2,0 + 3,0 = 7,0 ≤ 7,65 m głębokości, 25 rowerów na rząd przy 0,40 m na rower i poziom daje 5,0 ≤ 6,0 m długości. Do potwierdzenia doborem stojaków.
  3. [red., K-1] Propozycję z ustalenia, by w miejscu PHS.04 zrobić prostokątne PHS.02 (u 11,6–15,5 × v 0,5–9,0), odrzucono. Prostokąt przecina oś Hali na 5,48 m (27,7 m² w pasie ±3 m), czyli odtwarza wadę F1-komunikacja-01. PHS.02 ≥ 30 m² (P-I3) musi leżeć poza pasem osi. Po stronie pd.-wsch. osi, między drzwiami ogrodowymi a korytarzem klatki B, poza pasem zostaje tylko 10,6 m². Realna jest więc tylko strona pn.-zach., przy trzonie A, wspólnie z komfortką (P-I3), szachtem SZ-1 (S3-ppoz-07) i ewentualnie SW.06. To wymaga jednego rzutu z testem.
  4. Dawne PHS.02 (9,3 m²) przeznaczyć na pomieszczenie porządkowe i PD parteru (F2-program-biura-07).
  5. Poprawić F.15.B.
- **Ryzyko.** W przerwie konferencji WC obsłużą tylko połowę potrzeb. Wejście z ogrodu przez toaletę jest widoczne na rzucie.

#### F2-program-biura-03 – Ścianki między pokojami trafiają w szyby
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · rewizja_spec*

- **Dowód.**
  - Policzono 60 próbek na okno. Na kond. 1–6 84 okna leżą w dwóch pomieszczeniach naraz, z czego 56 dzieli dwa biura.
  - Wieża: ścianki stoją w osiach 0,45 + 4,05j, a środki okien 1,65 m w 1,35 + 2,70k (`windows_for`). Ścianka 4,50 trafia w okno 3,225–4,875 0,45 m od słupka (podział 1,225 / 0,10 / 0,325 m), więc prawe skrzydło obsługuje dwa pokoje i nie może się otwierać. Ścianki 8,55 / 16,65 / 24,75 mieszczą się w filarze, ale tylko 0,025 m od ramy.
  - Skrzydło od dziedzińca: podział 0,40 / 0,72 m. Elewacja uliczna jest zgodna.
  - Biura mają odsłonięty strop TABS (V12-KOSZT), więc styk ścianki z elewacją jest główną drogą bocznego przenoszenia dźwięku.
- **Wymaganie.** Własna zasada spec. rozdz. 8: „partycje w filarach lub słupkach”; izolacyjność R'A1 między pokojami (PN-B-02151-3:2015-10).
- **Poprawka.** Dodatkowy słupek w linii ścianki:
  - wieża: skrzydło otwierane 0,825 m oraz kwatery stałe 0,45 / 0,375 m przedzielone słupkiem w osi ścianki;
  - skrzydło budynku: kwatera stała 0,40 m i skrzydło 0,72 m;
  - przyłącze akustyczne ścianki do słupka, osobna kaseta ZIP dla każdej części.

  Warunek 1:8 zostaje spełniony: (1,65 + 0,325) × 2,45 = 4,8 m² ≥ 3,0 m². W rozdz. 8 dopisać słupek dodatkowy; zaktualizować elewacje 1:200 i przekrój 1:50. Przesunięcie słupów na siatkę 0,45 + 8,10k jest niewykonalne, bo siatkę wyznaczają garaż, pale i kratownice S. Ten sam błąd dotyczy ścianki SK.02/SK.01 i ściany mobilnej (G1).
- **Ryzyko.** Brak izolacyjności i wspólna osłona przeciwsłoneczna dla dwóch pokoi. To błąd koordynacji, który widać na rzutach i przekroju 1:50. Koszt ok. 0,1 mln.

#### F2-program-biura-04 – Serwerownia i archiwa w pionie z pokojami socjalnymi; strop biurowy pod UPS
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · agent_rzutow*

- **Dowód (`g3.py`).**
  - IT.01 ma nad sobą w 100 % pokój socjalny PS.01f. PP.02 ma pod sobą w 87 % PS.01f, a nad sobą w 56 % PS.01l. PP.03 leży w 100 % między pokojami socjalnymi PS.01e i PS.01k. Instalacje biegną w warstwie podłogi, więc odpływy z kond. 2 i 4 przechodzą tuż nad płytą stropu tych pomieszczeń.
  - Kształt: pas L szer. 1,33 m, który przecina też okno. Powierzchnie: IT.01 37,7 m² (spec. 50), PP.02 42,85 m² (M.01: 48), PP.04 20,9 m² (M.01: 24).
  - Obciążenie obliczeniowe pola 8,10 × 7,30 m przy płycie 0,28 m: biuro 18,2 kN/m², serwerownia 23,8 (+31 %), UPS VRLA 30,6 (+68 %), archiwum 34,4 (+89 %). Wzmocnienie płyty (D15) przewidziano dotąd tylko pod archiwum.
- **Wymaganie.** PN-EN 50600-2-1 i ANSI/TIA-942 (nad salą IT bez instalacji wodnych; obciążenie ≥ 7,2–12 kN/m², pod baterie UPS ≥ 12 kN/m²); PN-ISO 11799 (magazyn archiwalny nie pod pomieszczeniami mokrymi); PN-EN 1991-1-1 (kategoria B 3,0 kN/m² nie obejmuje IT); program IT.01 i M.01 (R-213).
- **Poprawka.**
  - (a) Pokoje socjalne z kond. 2 i 4 przenieść do pasa zach. przy pionach WC. Nad i pod IT.01, PP.02 i PP.03 zostaną tylko pomieszczenia suche.
  - (b) IT.01 jako prostokąt o szer. ≥ 5,0 m i ≥ 45 m² powierzchni szafowej, z rampą albo przedsionkiem na poziomie podłogi podniesionej (rampa 1:12 ma ok. 5,4 m), bez okna. PP.02 ≥ 48 m², PP.04 ≥ 24 m², prostokątne. Pas 1,33 m oddać na piony instalacyjne (E-I-3).
  - (c) W rozdz. 5 i `siatka.strop` jedna strefa wzmocniona (płyta 0,40 m z belkami albo głowicami, zbrojenie na przebicie przy słupach 0,60 × 0,35) w tych samych polach pod archiwami, serwerownią i UPS. To ok. 120 m² ponad D15, < 0,06 mln zł.
- **Ryzyko.** Zalanie sali IT albo archiwum PZGiK z pokoju socjalnego; niedowymiarowany strop pod baterie. Rzeczoznawca branżowy wskaże to jako błąd.

#### F2-program-biura-05 – Stałe stanowiska pracy bez wymaganego światła dziennego
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · agent_rzutow*

- **Dowód (`g6.py`).**
  - DOS.19 (26,53 m², 3 stanowiska) nie ma okien. Jego jedyne lico zewnętrzne to odcinek styku skrzydło/wieża długości 3,83 m, pełny na rzucie.
  - DI.08: 2,67 m² szkła na 24,09 m², czyli 0,111 < 0,125.
  - GW.06 i GW.07 na kond. 3 leżą w narożu wklęsłym. Przy wymaganych 10,4 i 17,5 m (§ 13) w sektorze 60° są przeszkody już w 1,7–10,1 m. Łamie to własną zasadę (g) i G-D-9; na kond. 1, 2 i 4 w tym miejscu są magazynki.
  - SW.02 (kancelaria, 3 stałe stanowiska) to zamknięte pomieszczenie bez okien.
- **Wymaganie.** WT § 57 ust. 1–2; § 58 (samo światło sztuczne tylko za zgodą PWIS i OIP); rozp. bhp z 26.09.1997 § 26 ust. 1; WT § 13 ust. 1 pkt 1 lit. a–b i ust. 4.
- **Poprawka.**
  - (a) Lico styku na kond. 1–4. [red., K-10] Wariant z ustalenia, 2 okna 1,20 m + filar 0,825 m + ościeża 2 × 0,30 = 3,825 m, wypełnia całe lico. Nie zostawia miejsca na słup narożny (s 34,18; d 15,00), którego wymaga belka pasmowa z S1-konstrukcja-04. Przyjąć jedno okno systemu wieży 1,65 × 2,45 m = 4,04 m² obok słupa: 1,65 + 0,60 + 2 × 0,30 = 2,85 ≤ 3,83 m. To spełnia DOS.19 (wymagane 3,32 m²) i DI.08 (3,01 m²). Skrzydło wchodzi w sektor 60° dopiero po ok. 23–25 m.
  - (b) GW.06 i GW.07 przenieść na miejsca PP.01l (32 m²) oraz PP.01m + PP.3.16. Naroże wklęsłe na kond. 3 oddać magazynkom.
  - (c) Kancelaria jako otwarta lada w doświetlonej części Hali z zapleczem w DK II. Otwiera to kieszeń u 31,1–33,4 × v 7,45–10,05 (D16, F1-komunikacja-05). [red., K-14] Lada w Hali, która jest holem ewakuacyjnym klatki A, wymaga potwierdzenia rzeczoznawcy. Wariant bezpieczny to kancelaria przy elewacji Wybrzeża obok DK II.
- **Ryzyko.** Formalna niezgodność z WT § 57 i § 13. Wady są lokalne, a naprawa nie zmienia bryły.

#### F2-program-biura-07 – „Pomieszczenia-szczeliny” w strefie środkowej
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · agent_rzutow*

- **Dowód (`g7.py`, polylabel).**
  - Na kond. 1–6 jest 31 pomieszczeń o szerokości wpisanej < 1,6 m, w tym 21 o szerokości ≤ 1,0 m. Przykład z kond. 4: pięć szczelin obok siebie (DZ.OCZ, DKD.OCZ, CZ.OCZ, IT.02f, PP.05g) o szer. 0,79–0,99 m w pasie 5,2 × 6,15 m.
  - Żadne z nich nie ma drzwi, więc pomieszczenia są nie tylko za wąskie, ale i niedostępne.
  - W pasie 0,98 m nie zmieści się szafa 19" z wolną przestrzenią 1,0 m z przodu i 0,6 m z tyłu ani zlew wylewowy z wózkiem.
  - Na P nie ma pomieszczenia porządkowego ani PD. Model ma 8 PD, program 12. Brak PD i pomieszczenia porządkowego na S jest już znany (K2).
- **Wymaganie.** Program: PP.06 „na każdym piętrze, dostęp do wody”, IT.02 „PD na każdej kondygnacji”, OCZ (R-212); ANSI/TIA-569 i ISO/IEC 14763-2.
- **Poprawka.** Przepodział bez zmiany powierzchni: sąsiednie szczeliny połączyć i podzielić strefę środkową w poprzek na dwa pasy ok. 3,0 m, każdy otwarty na własny korytarz. Na kond. 4:
  - PD 2,0 × 3,0 m i pomieszczenie porządkowe 2,0 × 3,0 m;
  - wspólna wnęka oczekiwania CZ/DKD/DZ 3,1 × 3,0 m;
  - wnęka MFP 3,1 × 3,0 m.

  Analogicznie na kond. 1–3, 5 i 6. Na P pomieszczenie porządkowe i PD w dawnym PHS.02. Test generatora: pomieszczenie pomocnicze szer. ≥ 1,8 m, PD ≥ 2,0 × 3,0 m, każde z drzwiami albo jako otwarta wnęka.
- **Ryzyko.** Program spełniony tylko nominalnie. To ta sama klasa błędu, którą `weryfikacja_program` K2 uznała na S za istotną.

#### F2-program-biura-08 – Pomieszczenia bez drzwi i sekretariaty bez połączenia z gabinetami
*Waga: ISTOTNY (zgł. ISTOTNY) · F2 program · agent_rzutow · grupa G2*

- **Dowód (`drzwi2.py`, `sekr.py`).**
  - Na P–6 jest 51 pomieszczeń bez własnych drzwi:
    - 20 pokoi na łuku, w tym gabinet Przewodniczącego KS.01 (35,3 m² wobec 48 m² w spec.);
    - SN.01d (59,9 m², 30 os.), KS.05a, IT.03;
    - na P: SK.02–SK.04 i PPT.05;
    - pomieszczenia techniczne segmentu (trafo, rozdzielnia, BESS, odpady);
    - wszystkie PD, pomieszczenia porządkowe, MFP i OCZ.
  - Z 10 sekretariatów tylko DST.02 ma drzwi do gabinetu. GW.04, CZ.03, DZ.08 i KS.10 nie sąsiadują nawet z gabinetem swojej komórki.
  - Przyczyna: reguła generatora „jedne drzwi do komunikacji”.
- **Wymaganie.** Program („Sekretariat – pokój obok gabinetów dyrekcji, połączony drzwiami”, PU s. 5); R-212; WT § 236–237 (wyjście z każdego pomieszczenia na drogę ewakuacyjną).
- **Poprawka.**
  1. Drzwi 0,9 m z pokoi na łuku do korytarza pierścieniowego. Wejście do KS.01 z holu przez KS.03, a KS.02 dostępne tylko z gabinetu.
  2. Drzwi SN.01d i KS.05a.
  3. Drzwi sekretariat–gabinet w każdej parze. Zamiany: GW.03↔GW.04, CZ.02↔CZ.03, DZ.08 obok DZ.07, KS.10 obok KS.07.
  4. Trafo: drzwi zewnętrzne od Wybrzeża ≥ 1,4 m, dwuskrzydłowe (wymiana transformatora). BESS: drzwi EI 120-C. Rozdzielnia i odpady: drzwi do pasa obsługi i dźwigu T.
  5. Testy w `budynek.json['testy']`: „każde pomieszczenie poza szachtem ma ≥ 1 drzwi lub jest otwartą wnęką” oraz „sekretariat ma drzwi do gabinetu tej samej komórki”.
- **Ryzyko.** Na rzucie kond. 6 gabinet Przewodniczącego nie ma wejścia. Fachowy sąd to zauważy.

#### F3-garaz-technika-02 – Brak pętli dróg na −1; zawracanie u stopy rampy
*Waga: ISTOTNY (zgł. KRYTYCZNY) · F3 garaż · rewizja_spec*

- **Dowód.**
  - Jedyny pierścień dróg (A1 – łącznik – A2E – pas nad trzonem A – A2W – A3 – A1) jest przerwany w pasie 1,75 m (v 20,85–22,60), który w v1.2 jest przedsionkiem dźwigów A1/A2.
  - Auto zjeżdżające rampą na zachód (stopa u 14,78) dociera do łącznika wsch., do A2E i do rampy na −2 tylko po zawróceniu o 180°. Dotyczy to 40 pozycji na −2 i 13 we wsch. części −1, razem 53 ze 113.
  - Symulacja obwiedni pojazdu 4,74 × 1,76 m (rozstaw osi 2,70 m, R zewn. 5,86 m; `v2/uturn.py`): obwiednia sięga v 7,48, a linia stanowisk R2 leży na 6,60 (ok. 2,9 m² nakładania), więc manewr wymaga cofania.
  - Korekty zgłoszenia: zawrót wymaga ok. 10,6 m, a nie 11,7 m; drzwi A1/A2 na −1/−2 wychodzą do przedsionka 7,20 × 1,75 m, nie na ścianę.
- **Wymaganie.** WT § 104 ust. 1 (droga manewrowa „dostosowana do warunków ruchu”); zasady projektowania garaży (obwiednie pojazdu miarodajnego, np. EAR 2005 / RAS-K-1). Przepis nie zakazuje manewru wprost, dlatego wagę obniżono.
- **Poprawka.**
  1. Zatoka do zawracania naprzeciw stopy rampy: usunąć trójkę R2 na u 8,4–15,9 × v 6,6–11,6 na −1 (jednostka stackera + 1 stanowisko, −5 pozycji). Wolny pas v −4,05…11,60 (15,65 m) pozwala zawrócić jednym łukiem. Przy rampie dwukierunkowej z F3-garaz-technika-01 wystarcza przesunięcie toru o 0,6 m.
  2. Na −2 ostatnie 3 m rampy wewnętrznej bez odboju od zach.
  3. Pętla wokół trzonu A jest droższa (przeniesienie 93 m² pomieszczeń, −2 do −4 stanowisk). Pomysł z weryfikacji 1, by A1/A2 otwierały się na pd. do przedsionka A, jest geometrycznie niewykonalny.
- **Ryzyko.** Bilans spada do 103 < 106 (rozdz. 5.5), więc kompensacja jest konieczna. Wskazane źródło to −2 pod M1 (+6, variant4.py) za ok. 0,4–0,6 mln. Wiąże się to ze skutkami opisanymi w K-15.

#### F3-garaz-technika-03 – Stackery zależne: OzN, EV i wysokość R1
*Waga: ISTOTNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec · grupa G7*

- **Dowód (`stk.py`).**
  - Na −1 jest 41 stanowisk na posadzce, z czego 32 tworzą 16 jednostek stackerów zależnych, a wolnych zostaje 9. Najbliższe trzonu B jest 9,0 m od niego.
  - Spec. i JSON (`miejsca_opis`: „−1 … w tym 6 OzN”) umieszczają 6 stanowisk OzN 3,6 m na −1 przy trzonach. W tym układzie oznacza to rozbiórkę ok. 3 jednostek, czyli ok. −9 pozycji, a `ozn()` liczy −3. Bilans opisany w spec. daje więc 101–104 < 106.
  - EV: 55 punktów wobec 46 stanowisk niezależnych, więc ≥ 9 ładowarek musiałoby stanąć na platformach w garażu bez tryskaczy.
  - R1 leży pod stropem pasa dziedzińca. JSON podaje wierzch −0,15 dla całego −1, a G-K-2 −0,77 przy rampie. Przy wierzchu ≤ 118,85 R1 ma 3,45 m < 3,50 m.
  - Słabsze części zgłoszenia: platforma 2,30 m (praktyka producentów) i projekt WT (nie obowiązuje). Uznanie miejsc zależnych w § 13 MPZP to ryzyko, nie pewna niezgodność.
- **Wymaganie.** MPZP § 13 („co najmniej”); WT § 21; ppoz.md rozdz. 8 (ładowanie EV – wytyczne).
- **Poprawka.**
  1. Sześć stanowisk OzN na −2 przy trzonach A i B, gdzie wszystkie stanowiska są niezależne (−3 pozycje, jak w skrypcie). Opis: −1 73 (41 + 32), −2 37, w tym 6 OzN. Po zatoce z F3-02 na −1 zostaje 68.
  2. Punkty EV wyłącznie na stanowiskach niezależnych (ok. 45–46), brakujące ok. 9–10 jako trasy kablowe (art. 12a ustawy o elektromobilności). Bez ładowarek na platformach, dopóki garaż jest bez tryskaczy.
  3. [red., K-18] Ujednolicić rzędną stropu pasa wg S1-konstrukcja-08 (119,15 → 119,08, nawierzchnia 119,28). R1 zachowuje wtedy stackera (≥ 3,55 m).
  4. W F.15.C wariant ostrożny: 78 m.p. na posadzce + 32 zależne, z adnotacją o przydziale parami.
- **Ryzyko.** Deklaracja „110 ≥ 106 (zapas 4)” nie wynika z opisanego układu. Przy kontroli bilansu sąd albo organ może odrzucić miejsca zależne.

#### F3-garaz-technika-04 – Brak zbiornika ppoż., pompowni, węzła i przepompowni w bilansie podziemia
*Waga: ISTOTNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec · grupy G3, G4*

- **Dowód.**
  - Rozp. MSWiA 2010 (t.j. Dz.U. 2023 poz. 822): § 24 ust. 2 – budynek W wymaga zapasu ≥ 100 m³ wody wyłącznie ppoż. Redukcja do 50 m³ z ust. 3 pkt 1 lit. b odpada, bo garaż ma > 750 m². Ust. 3 pkt 3 pozwala zejść do 50 m³ przy sieci ≥ 10 dm³/s i do 25 m³ przy ≥ 15 dm³/s z nasadą 75 mm (ust. 5). Ust. 4 dotyczy tylko ZL IV.
  - E-I-4 usunął pompownię i zbiornik razem z tryskaczami.
  - Program przewiduje IT.10 (węzeł cieplny 15–30 m²) i IT.11, a w podziemiu brakuje węzła.
  - Klin −2 ma 25,7 m² brutto, ale jest trójkątny: tylko 14,8 m² ma szer. ≥ 2,0 m, a 8,7 m² szer. ≥ 2,5 m (`v2/wedge2.py`). Weryfikacja 1 przydzieliła klin −1 dwa razy, węzłowi i odpadom.
- **Wymaganie.** Rozp. MSWiA 2010 § 22 ust. 3, § 23 pkt 3 lit. a, § 24; WT § 212 ust. 9; WT § 102 pkt 5 (wpusty z osadnikami), § 281 (zakaz studzienek w garażu).
- **Poprawka (spójny przydział miejsca).**
  - (a) Klin −2 przy drodze A4 i szybie T jako jedna odrębna strefa pożarowa (EI/REI 120): zbiornik ok. 24–25 m³ w pasie 1,5–2,5 m przy ścianie pd. (u 28–34, 2,0 m wody) oraz pompownia ok. 8 m² (u 34–36,9). Pompy z napływem, wejście z A4 i dźwigiem T, zasilanie także z agregatu. To rozwiązanie na granicy wykonalności. Przy 50 m³ trzeba poświęcić ok. 2 stanowiska na −2 albo przestrzeń zwolnioną przez dźwig samochodowy.
  - (b) Klin −1 przy T: pomieszczenie odpadów (F3-garaz-technika-05).
  - (c) Węzeł IT.10 (15–20 m²) w pasie u 31,1–33,4 na −1, wolnym po przeniesieniu centrali S.
  - (d) Przepompownie ścieków jako zestawy kompaktowe albo jedna przepompownia wg S2-posadowienie-07.
  - (e) Nasada 75 mm w elewacji od Wybrzeża; potwierdzenie wydajności sieci przez MPWiK.
  - (f) Koszt ok. +0,2–0,3 mln. Pozycja 7.2 (60 zł/m²) obejmuje tylko hydranty i zawory.
- **Ryzyko.** Zob. S3-ppoz-08 i K-6. Zasada „technika krytyczna nad 119,0” (E-I-4) przy lokalizacji na −2 wymaga jawnego uzasadnienia.

#### F3-garaz-technika-05 – Brak drogi dostaw i odpadów do dźwigu T; brak strefy IT.15
*Waga: ISTOTNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec*

- **Dowód (`conn.py`, `v2/uv_-1.png`).**
  - Korytarz do T na −1 (u 22,6–36,8 × v −6,4…−4,25) leży na pd. od rampy. Na u 14,8–21,0 między odbojem rampy (v −4,05) a ścianą pasa (v −4,40) zostaje 0,35 m, a rampa jest tam 0–1,1 m nad posadzką. Na wschodzie korytarz łączy się z garażem tylko przez pomieszczenie przyłącza i centralę S. Opisana trasa „dostawy rampą na −1, dalej korytarzem do T” jest więc niewykonalna.
  - Pomieszczenie odpadów 24 m² w M1 przy trzonie C nie ma drogi wywozu. Rampa ma 18 %, a w trzonie C jest tylko szyb w stanie surowym.
  - Strefy przyjęcia towaru IT.15 (15–30 m², od Wybrzeża, z poziomu terenu) nie ma.
- **Wymaganie.** PU s. 15 i 17, `program.yaml`: IT.15 – przyjęcie towaru z poziomu terenu z windą; IT.14 – łatwy dostęp dla firm odbierających. Rozp. (WE) 852/2004 zał. II rozdz. VI: dostawy żywności nie przez pomieszczenie odpadów.
- **Poprawka.**
  1. Dostawy z poziomu terenu przez przedsionek T z drzwiami od Wybrzeża. Przyjęcie towaru 12–15 m² jest wykonalne dopiero po parterowym poszerzeniu segmentu (F3-garaz-technika-01 pkt 2). Bez poszerzenia mieści się tylko przedsionek ok. 7 m², poniżej minimum programu.
  2. Pomieszczenie odpadów IT.14 (ok. 18–20 m²) w klinie −1 przy przystanku T, dostępne dźwigiem T. Z M1 usunąć odpady.
  3. Z opisu usunąć „dostawy rampą na −1 i korytarzem”. Po zmianie rampy na dwukierunkową korytarz −1 i tak znika.
- **Ryzyko.** Wymóg PU nie jest spełniony. Odpady i dostawy jechałyby dźwigami osobowymi przez hol.

#### F3-garaz-technika-06 – Brak drogi wewnętrznej do odbioru osób i drobnych dostaw
*Waga: ISTOTNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec*

- **Dowód.**
  - PU s. 16–17: „Projekt musi obejmować: … wewnętrzną drogę dojazdową, przeznaczoną wyłącznie na potrzeby obsługi obiektu – w tym odbioru osób oraz niewielkich dostaw”.
  - Wyj. 4 odp. 20: droga na dz. 10/2 ma być łącznikiem z tą drogą. Rejestr R-214 klasyfikuje to jako OBLIGATORYJNE-merytoryczne, a kryterium oceny 1a wymienia „dojazd dz. 10/2”.
  - Spec. poz. 13 mówi „Dz. 10/2 nie jest używana przez nasz ruch”, a na terenie nie ma miejsca zatrzymania pojazdu.
  - Audyt kompletności wskazał tylko brak opisu na PZT.
- **Wymaganie.** PU s. 16–17; Wyj. 4 odp. 20; R-214; WT § 19 (odległości stanowisk postojowych). Kiss&ride ≤ 50 m według M.13 to zalecenie.
- **Poprawka.**
  - Droga jednokierunkowa 3,0–3,5 m z dz. 10/2 w pasie pd. od segmentu, tylko dla obsługi obiektu.
  - Na końcu miejsce krótkotrwałego zatrzymania na odbiór osób, taxi i drobne dostawy. Nie nazywać go stanowiskiem postojowym, bo wtedy obowiązują odległości z § 19 ust. 1–2. Stanowiska OzN zostają w garażu.
  - Zawracanie na placu typu T na styku z dz. 10/2 albo wyjazd przez dz. 10/2 (uzgodnienie z zarządcą).
  - Skrzynki rozsączające E-I-9 (przykrycie ok. 0,40 m) dobrać w klasie SLW 30 albo obniżyć; bilans retencji przeliczyć.
  - Na PZT opisać powiązanie z dz. 10/2.
  - [red., K-16] Po parterowym poszerzeniu segmentu z F3-01 pas ma 3,1 m, więc droga może mieć tylko 3,0 m, bez opaski.
- **Ryzyko.** Brak elementu, którego PU wymaga wprost, w ocenianym kryterium.

### 2.3. DROBNE

#### S1-konstrukcja-04 – Klin skrzydła przy wieży bez drugiej linii podpór
*Waga: DROBNY (zgł. ISTOTNY) · S1 konstrukcja · rewizja_spec*

- **Dowód.**
  - Lico dziedzińcowe skrzydła kończy się w (s 34,18; d 15,00), a dalej krawędzią skrzydła jest lico zach. wieży od (35,86; 18,44) do (62,52; 5,34). Głębokość d = 15 skrzydło osiąga dopiero przy s = 42,86.
  - W klinie s 34,2–42,9 płyta 0,40 m przęsłowałaby do 18,4 m (L/h ok. 46) zamiast deklarowanych 14,20 m.
  - Na całym styku (26,7 m) płyta skrzydła opiera się na linii u = 0 wieży, gdzie słupy stoją co 8,70 / 7,30 / 7,15 / 6,55 m. Reakcja 120–160 kN/m daje w pasie u = 0 M ok. 0,9–1,2 MNm, więcej niż pas płyty 0,28 m (ok. 230 kNm/m).
- **Wymaganie.** PN-EN 1992-1-1 p. 7.4 (SGU); spójność z opisem rozdz. 5.
- **Poprawka.**
  1. Belka pasmowa sprężona ok. 1,2 × 0,60 m, dł. 9,5 m, między słupem narożnym (s 34,18; d 15,00) a słupem wieży (0; 8,70), tuż za ścianą wsch. sali 200. Na −1 belka zwisa 0,20 m, co zostawia ok. 3,45 m nad rzędem klina (bez stackerów).
  2. Na linii u = 0 w stropach P–4 pas nośny: płyta skrzydła przedłużona ok. 2,0 m w głąb wieży, z kablami pasmowymi.
  3. W rozdz. 5 dopisać oba elementy.
- **Ryzyko.** Konstruktor uzupełni to w PB, a sąd tego nie zobaczy. [red., K-10] Słup narożny ogranicza okno w licu styku (F2-program-biura-05). W pakiecie G1 w tym miejscu leżą sala 80 (d ≤ 12,4) i kuluar (d 12,55–14,5). Belka (d ok. 14,6–15,0) biegnie wtedy w pasie przy licu dziedzińcowym, poza salami, więc obie sale zachowują strop bez belek.

#### S1-konstrukcja-06 – Segment: płyta, taras, układ słupów przy bramie
*Waga: DROBNY (zgł. ISTOTNY) · S1 konstrukcja · rewizja_spec*

- **Dowód.**
  - Segment zajmuje u 21,0–40,0, krawędź pn. v −0,05, ściana pd. od v −7,12 do −10,60. Przęsła pn.–pd. mają więc 7,07–10,55 m.
  - (a) Spec. podaje „płyta 0,28 m” bez zapisu, że jest sprężona. Jako żelbetowa wymagałaby ok. 0,45–0,6 m (tab. 7.4N). Jako sprężona jest do przyjęcia na kond. 1–4, ale nie pod tarasem (L/h 37,7).
  - (b) Przy „słupach co 4,05 m” brama 4,0 m jest niemożliwa (między słupami 0,60 m zostaje 3,45 m).
  - (c) Rampa przechodzi na −1 pod licem zach. segmentu, więc słupy tego lica w pasie rampy nie mogą zejść do fundamentu.
  - Tab. 4.2 podaje dla kond. 4 2,87 m w świetle, co odpowiada płycie 0,18 m.
  - Brama 6,0 m i słup na v −8,15 z ustalenia pochodziły z v1.0.
- **Wymaganie.** PN-EN 1992-1-1 tab. 7.4N, p. 7.4.2; ciągłość drogi obciążeń nad otworem bramy; WT § 72.
- **Poprawka.** Rozdz. 5: płyty sprężone 0,28 m na kond. 1–4 i 0,35 m w stropodachu-tarasie (wierzch +19,10); kond. 4 ma wtedy 2,70 m w świetle (≥ 2,5 m), a tab. 4.2 trzeba poprawić. Podpora pn.: słupy wieży v = 0 i ciągłość płyty. Pod dry-coolerem na kond. 4 wzmocniony strop, tak jak pod agregatem.
  - [red., K-8] Położenia słupów z weryfikacji 2 (lico wsch. v ok. −4,75 i −8,80, lico zach. v ok. −4,60) dobrano dla bramy 4,0 m i rampy 3,5 m. Po F3-garaz-technika-01 (brama ≥ 6,0 m, rampa 6,0 m, v −0,15…−6,4):
    - lico wsch.: słup dopiero przy v ≤ −6,7;
    - lico zach.: tylko narożnik SW (−7,12);
    - belki krawędziowe ok. 6,7 m i 7,1 m na każdej kondygnacji i pod tarasem;
    - żaden słup nie może stanąć w świetle bramy, bo wtedy wraca przejęcie z ustalenia (M ok. 1,5 MNm, belka h ok. 1,0 m).
- **Ryzyko.** Niespójny opis konstrukcji segmentu i tab. 4.2. Bez skoordynowania z F3-01 słup trafi w nową bramę.

#### S2-posadowienie-01 – Brak III kategorii geotechnicznej i warunku DGI
*Waga: DROBNY (zgł. KRYTYCZNY) · S2 posadowienie · rewizja_spec*

- **Dowód.**
  - Główna teza zgłoszenia (ściany 18 m) dotyczyła v1.0. Obecnie ściany mają 0,60 m × 19 m na 222,6 m obwodu. Przekroje A-A i B-B rysują spód na 99,75, a wcięcie w gliny wynosi 2,1–2,7 m w O-01…O-04 (1,8–2,0 m licząc od terenu minus 19 m).
  - Prawdziwa jest druga część. 129,9 m z 237,6 m obwodu −1 (115,1 m ściany i 14,85 m iniekcji przy Maz. 19) leży na pd. od O-03 (n < 40,75), gdzie otwory O-05…O-09 skończyły się w pospółkach na 103,67–104,22 (K-01).
  - Spec. pisze bez zastrzeżeń „wcięte w gliny” i nie podaje III kategorii geotechnicznej (przesądzają ją 2 kondygnacje podziemne) ani DGI.
  - 58 sond GPC przebija glinę, która jest dnem szczelnego boksu (F3-garaz-technika-08).
- **Wymaganie.** Rozp. w sprawie ustalania geotechnicznych warunków posadawiania (Dz.U. 2012 poz. 463) § 4 ust. 3 pkt 3 lit. e i § 7 ust. 3; analiza posadowienia w części opisowej (formularze_tabele.md: zał. 3 pkt 2 ppkt 2 lit. b).
- **Poprawka.**
  - Zostawić 19 m. W rozdz. 5 i 16, JSON `obudowa` i opisie etap2 dopisać: III kategoria; DGI wg § 7 ust. 3; na pd. odcinku (ok. 130 m) strop glin nierozpoznany (K-01); głębokość 19 m obowiązuje pod warunkiem wcięcia ≥ 2 m w ciągłą QpB, potwierdzonego w DGI.
  - Zakres DGI: 3 otwory 25–30 m (rejon O-07/O-08, O-09, O-06), CPTu w osi ścian co ok. 20 m, piezometry z obserwacją sezonową. Otwory próbne TRT wykonać z opróbowaniem jako rozpoznanie pod gliną.
  - Gdyby DGI wymusiło +2 m na pd. odcinku: ok. 0,30–0,32 mln.
- **Ryzyko.** Luka w analizie posadowienia. Wydłużenie wszystkich ścian do 20–21 m nie ma oparcia w danych.

#### S2-posadowienie-05 – Przesłona z iniekcji przy Maz. 19
*Waga: DROBNY (zgł. ISTOTNY) · S2 posadowienie · rewizja_spec*

- **Dowód.**
  - Model kosztów v1.1 liczy osobno 17 kolumn Ø 1,2 × 19 m (przesłona) i 19 kolumn × 6 m (podbicie), więc przesłanka „jeden element jako podbicie i przesłona” jest częściowo fałszywa. Kondygnacja −2 jest 12,1 m od Maz. 19, a wykop przy kamienicy ma głębokość −1 (spód płyty 114,10, czyli 1,9–2,3 m pod ławami).
  - Prawdziwe są dwie rzeczy:
    - (1) rozdz. 5, JSON i opis nie podają głębokości ani wcięcia ściany iniekcyjnej;
    - (2) 17 kolumn na 15 m daje rozstaw 0,94 m i zakład 0,26 m, a rozejście sąsiednich kolumn na 19 m przy odchyłce 1–2 % sięga 0,38–0,76 m. Okna przesłony otwierają się od ok. 7,5–15 m głębokości, akurat przy O-08, gdzie stropu glin nie znamy.
  - CPTu O-08 pokazuje humus i namuł (qc 0,7 MPa) na 115,7–116,7, więc ława Maz. 19 prawdopodobnie leży na gruncie organicznym.
  - Ryzyko dla WS 5 jest małe (ok. 1,3 H, osiadanie 4–9 mm). Nabrzeże jest poza wpływem.
- **Wymaganie.** PN-EN 12716 (tolerancje, kontrola wypiętrzeń); PN-EN 1538; PN-EN 1997-1 p. 2.4.9 i 9.8; Prawo budowlane art. 5 ust. 1 pkt 9.
- **Poprawka.** Zapisać:
  - przesłona: kolumny Ø 1,2 m do 99,75 (≥ 2 m w QpB), rozstaw ≤ 0,75 m (21 kolumn na 15 m: zakład 0,45 m), odchylenie każdego otworu mierzone inklinometrem ≤ 1 %, pole próbne 3 kolumn;
  - podbicie: osobne kolumny ok. 6 m, wykonywane najpierw, po odkrywkach; ciągły pomiar wypiętrzeń z progiem wstrzymania ok. 3 mm (PN-EN 12716);
  - do monitoringu dopisać WS 5;
  - z modelu pomieszczeń usunąć „rezerwę połączenia z Maz. 19” na −1.

  Koszt ok. +0,05 mln, a wariant podwójnego rzędu ok. +0,24 mln.
- **Ryzyko.** Nieszczelność białej wanny przy zabytkowej kamienicy albo wypiętrzenie jej ławy. [red., K-15] Przy kompensacji miejsc przez −2 pod M1 wykop −2 zbliża się do Maz. 19 na ok. 1,2 m i schodzi ok. 6 m poniżej ław. To ustalenie trzeba wtedy przeprojektować.

#### S2-posadowienie-07 – Brak przepompowni ścieków i separatora; deszczówka na −2
*Waga: DROBNY (zgł. ISTOTNY) · S2 posadowienie · agent_rzutow · grupa G4*

- **Dowód.**
  - Zarzut o pomieszczeniu 8,74 m² dla zbiornika deszczówki dotyczył modelu v1.0. W v1.1 zbiornik ma 27 m² × 1,85 m.
  - Prawdziwe jest to, że w `docs/` i `model/*.json` nie ma przepompowni ścieków, separatora ani osadnika. Jedyna „pompownia” to odwodnienie bramy.
  - Odbiorniki leżą poniżej dna kanałów: na −1 (115,10) sanitariaty MDS, pralnia i MBR, na −2 (112,10) WC ukrycia. Dna studni mają 116,5–117,9, a właz ulicy 118,5–119,3 wyznacza poziom zalewania.
  - Zbiornik deszczówki na −2 nie może mieć przelewu grawitacyjnego.
- **Wymaganie.** PN-EN 12056-4 (przepompownia z pętlą przeciwzalewową; zawór zwrotny nie wystarcza dla MDS i ukrycia); PN-EN 858-1/2 (praktyka i warunki przyłączenia); PN-EN 81-72 (odwodnienie podszybia dźwigu R).
- **Poprawka.** Jedna przepompownia 6–8 m² na −2 w strefie pn. od trzonu A (rect_uv 8,30–16,0 × 21,0–29,1). Ta strefa leży w pionie z sanitariatami −1 i WC ukrycia −2, więc zbiera je grawitacyjnie.
  - zbiornik pompowy 1,5 × 1,5 m, pompy 1+1, obniżenie płyty o ok. 1,0 m;
  - rurociąg tłoczny z pętlą ≥ 119,50;
  - zasilanie z agregatu;
  - do tej samej studni MBR, GPC i podszybie R;
  - w garażu wpusty z osadnikiem i separatorem, przy stopie rampy studzienka z pompą;
  - deszczówka: filtr i przelew-rozdzielacz w studni zewnętrznej do skrzynek rozsączających.

  Koszt ok. 0,1 mln.
- **Ryzyko.** Cofka na −2 przy awarii pompy i brak odpływu z ukrycia. Bez konfliktu z garażem.

#### S3-ppoz-09 – Trafo pod pokojem biurowym; SZR bez wydzielenia
*Waga: DROBNY (zgł. ISTOTNY) · S3 ppoż. · rewizja_spec*

- **Dowód.**
  - Kondygnacja P ma 4,80 m, cokół 0,30 m, transformator żywiczny 630 kVA ok. 1,9–2,2 m. Odległość do posadzki pokoju na kond. 1 wynosi 2,3–2,6 m < 2,8 m, a bez cokołu 2,6–2,9 m.
  - W opisie brakuje wydzielenia rozdzielni z SZR jako odrębnej strefy.
  - Pozostałe zarzuty to dobra praktyka: BESS 100 kWh w EI 120 jest poniżej progu 300 kWh, a skupienie źródeł zasilania nie jest zakazane.
- **Wymaganie.** WT § 182 (stacja ≥ 2,8 m od pomieszczeń na stały pobyt ludzi; ppoz.md 7.6); WT § 212; § 183.
- **Poprawka.** Jednostkę na kond. 1 segmentu nad komorą trafo przeznaczyć na pomieszczenie bez stałego pobytu: magazynek 24 m² albo falowniki i rozdzielnice DC. Pokój biurowy przenieść w miejsce magazynka (bilans 43/43 bez zmian). W opisie: trafo i rozdzielnia z SZR jako odrębne strefy REI 120 / EI 60, obwody ppoż. przed wyłącznikiem pożarowym.
  - [red., K-7] Przy F3-garaz-technika-01 nad trafo może trafić rozdzielnia z SZR przeniesiona na kond. 1, co jednocześnie spełnia § 182. BESS na kond. 1 tylko przy ≤ 60 kWh.
- **Ryzyko.** Formalna niezgodność z § 182, którą łatwo usunąć. Koszt 0.

#### F1-komunikacja-05 – Strefowanie dźwigów i analiza ruchu
*Waga: DROBNY (zgł. ISTOTNY) · F1 komunikacja · rewizja_spec*

- **Dowód.**
  - Główna przesłanka zgłoszenia jest nieaktualna: w v1.2 P1 i P2 obsługują kond. 1–6, a C1 usunięto. Piętra obsługują więc A1, A2, P1, P2 (4 × 1 600 kg) i R.
  - Zostaje strefowanie na P: lobby P1/P2 nie łączy się z Halą (D16).
  - Rachunek (`lift.py`, ok. 340 os. nad P, popyt 12–15 %): same A1 i A2 dają INT ok. 46–51 s, AWT ok. 20–25 s, a z R w grupie INT ok. 31–34 s. Wynik zgłoszenia (62 s) zakłada obciążenie 80 % i brak P1/P2.
  - Analiza przepustowości to wymaganie etapu WPK (F.01 zał. 3), a w konkursie wymaga się tylko I.11.
- **Wymaganie.** CIBSE Guide D:2020 (INT ≤ 30–40 s); ISO 8100-32:2020; F.15.C I.11.
- **Poprawka.** Bez nowego szybu:
  - R w grupie A w ruchu normalnym;
  - przejście ≥ 1,5 m z lobby P1/P2 do Hali przez kieszeń u 31,1–33,4 × v 7,45–10,05, z bramką kart (po przeniesieniu kancelarii wg F2-program-biura-05, a przejście z drzwiami EI 30 wg K-14);
  - sterowanie docelowe;
  - tabela ruchu w opisie;
  - I.11 = 5 dźwigów osobowych + T.
- **Ryzyko.** Słaby wynik według CIBSE na etapie WPK. Czwarty szyb byłby nieproporcjonalny.

#### F1-komunikacja-07 – Brak matrycy stref dostępu
*Waga: DROBNY (zgł. ISTOTNY) · F1 komunikacja · rewizja_spec*

- **Dowód.**
  - V1.2 (rozdz. 7.4) rozwiązuje tylko poziom S: P1 bez przystanku S, P2 na klucz, kontrola na drzwiach przedsionków A i A'.
  - Brak matrycy dla pozostałych poziomów:
    - A1/A2 otwierają się na publiczny łącznik na P i jadą do Z3 i Z4;
    - P1/P2 mają przystanki 1–6 na korytarzach biurowych, a P2 także −2/−1;
    - parter M1 i klatka C są dostępne z całodobowej bramy ogrodowej.
  - Drzwi PR.01→SK.06 to artefakt modelu objęty G1.
- **Wymaganie.** Program rozdz. 7, strefy Z1–Z6 (PU s. 14).
- **Poprawka.** Dopisać do rozdz. 5 i 7 oraz do schematu ruchu (P2) matrycę:
  - P1/P2: przystanki 1–6 i −1/−2 tylko z kartą, publiczność wyłącznie na trasie P ↔ +30,90;
  - A1/A2/R: czytniki w kabinach;
  - drzwi z klatek A, B i C: wejście na kartę, wyjście swobodne zwalniane przez SSP;
  - drzwi M1 od bramy (po F1-komunikacja-10): kontrola dostępu z wideodomofonem do centrum monitoringu w łączniku.
- **Ryzyko.** Ochrona nie ma zasady rozdziału stref. Poprawka to tylko tekst i osprzęt.

#### F2-program-biura-09 – Bistro: wyciąg i zaplecze
*Waga: DROBNY (zgł. ISTOTNY) · F2 program · rewizja_spec*

- **Dowód.**
  - SW.08 ma jedyne drzwi do SK.06, a z salą SW.07 styka się na ok. 6 m bez otworu.
  - Wątek wyciągu kontynuuje znane I-3. Nowa jest krytyka zapisu E-I-3 „wyciąg z odzyskiem do instalacji ogólnej”: powietrze z okapu (ETA 4) nie może iść przez wymiennik obrotowy.
  - Poprawka (b) ze zgłoszenia, czyli wyrzut nad dachem skrzydła, łamie MPZP § 6 pkt 13.
  - Sala 68 m² wobec 62 m² w spec. nie jest problemem.
- **Wymaganie.** PN-EN 16282-1, PN-EN 16798-3; MPZP § 6 pkt 13.
- **Poprawka.**
  1. W rozdz. 6 i 10 oraz w E-I-3: tylko urządzenia z wbudowaną kondensacją oparów i filtrem tłuszczu, bez frytownic i grilli. Wyciąg z zaplecza klasy ETA 2 do centrali parteru, odzysk płytowy albo glikolowy, bez wyrzutu na dach.
  2. Lada wydawcza albo drzwi SW.08↔SW.07; drzwi do foyer zostają jako służbowe.
  3. Dostawy poza godzinami pracy: −1 → A1/A2 → łącznik → bistro.
- **Ryzyko.** Tłuszcz w centrali ogólnej. Poprawka to tylko opis.

#### F2-program-biura-10 – Biurka przodem do okna
*Waga: DROBNY (zgł. DROBNY) · F2 program · agent_rzutow*

- **Dowód.** `tools/rzuty.py`, `draw_furniture`: dla pokoju 3,95 m nie jest spełniony warunek 3 × 1,6 ≤ Lb − 0,2, więc działa gałąź else. Biurka 1,5 × 0,8 m stoją równolegle do elewacji, 0,55 m od lica, drugi rząd 2,3 m dalej, krzeseł nie narysowano. Tak wyglądają wszystkie pokoje 24 m² na rzutach 1–6.
- **Wymaganie.** Rozp. MPiPS z 1.12.1998 (ograniczenie olśnienia); PN-EN 12464-1 (kierunek patrzenia równoległy do okna). To zalecenia.
- **Poprawka.** Biurka 1,6 × 0,8 m prostopadle do elewacji, 2 przy jednej ścianie i 1 przy drugiej, w strefie 0,2–1,8 m od okna. Między frontami biurek zostaje 2,35 m. W pokojach GW 32 m² po 2 biurka przy każdej ścianie. Narysować krzesła.
- **Ryzyko.** Fachowy sędzia zauważy olśnienie na stanowiskach z monitorami.

#### F3-garaz-technika-07 – Agregat: brak wyrzutu powietrza chłodnicy
*Waga: DROBNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec*

- **Dowód.**
  - Spec. i E-I-3 podają tylko „żaluzje 8 m² w licu zach. segmentu, kond. 1” i spaliny szachtem B. Wyrzutu powietrza chłodnicy nie wskazano.
  - Przy 8–12 m³/s (I-3) 8 m² żaluzji akustycznych wystarcza na jeden kierunek.
  - Lico 7,07 × 3,75 m mieści też wylot kanału trafo, więc grozi recyrkulacja ciepłego powietrza.
  - Okno lok. 6 w WS 5 ma parapet ok. 124,0, na wysokości żaluzji.
- **Wymaganie.** Wymagania producentów zespołów prądotwórczych; MPZP § 6 pkt 13; rozp. w sprawie dopuszczalnych poziomów hałasu (Wyj. 3 odp. 13: lokal 6).
- **Poprawka.** Chłodnica wyniesiona w pomieszczeniu dry-coolera na kond. 4, na jego żaluzjach 2 × 12 m², z blokadą wzajemną, jeśli dry-cooler nie jest zasilany z agregatu. Na kond. 1 zostaje ok. 2 + 2 m² żaluzji z tłumikami ≥ 25 dB w stronę WS 5. W opisie podać moc z bilansu odbiorów ppoż. (oddymianie garażu, nadciśnienie 3 klatek, dźwig R, pompownia ppoż., IT): ok. 250–350 kVA.
- **Ryzyko.** Spadek mocy albo wyłączenie agregatu w czasie pożaru. Gdy rozdzielnia i BESS trafią na kond. 1 (F3-01), pomieszczenie agregatu musi być zwarte, co przemawia za chłodnicą wyniesioną.

#### F3-garaz-technika-08 – Sondy GPC przebijają przesłonę z glin
*Waga: DROBNY (zgł. ISTOTNY) · F3 garaż · rewizja_spec*

- **Dowód.**
  - Według geotechnika.md gliny QpB (strop 101,8–103,4) są dnem szczelnej obudowy, odwodnienie jest tylko wewnętrzne, a czwartorzędu nie przewiercono do 30 m.
  - Spec. przewiduje „wiercenie z dna”: 58 otworów po 91 m od 110,90. Każdy otwór przebija przesłonę przy różnicy ok. 6,6 m między ZWG 117,00 a dnem ok. 110,4.
  - Glina ma ≥ 7 m pod dnem, więc stateczność dna (UPL) nie jest zagrożona. Ryzyko to wypływ przez otwór w czasie wiercenia.
  - Wysokość robocza pod stropem −1 przy wykopie rozpartym stropami (G-I-3) wynosi ok. 3,9 m.
- **Wymaganie.** PN-EN 1997-1 p. 2.4.7.4–2.4.7.5 (UPL, HYD); ochrona wód.
- **Poprawka.** W opisie zamiast „wiercenie z dna” zapisać: wiertnice niskie (maszt ≤ 3,5 m), orurowanie z prewenterem, płuczka obciążona, iniekcja cementowo-bentonitowa od dołu i kontrola każdego otworu. Przed PB otwór pilotażowy ok. 100 m z piezometrami poziomów pod gliną, połączony z TRT. Wydajność wiercenia spadnie o 30–40 %, koszt wzrośnie o ok. 0,2–0,3 mln.
- **Ryzyko.** Przebicie hydrauliczne przez otwór w fazie budowy. Uwaga: S2-posadowienie-08 (ten sam temat) odrzucono w weryfikacji jako znany; obowiązuje to ustalenie (rozdz. 4).

#### F3-garaz-technika-09 – Skrajnia przy krawędzi stropu nad rampą wewnętrzną
*Waga: DROBNY (zgł. DROBNY) · F3 garaż · rewizja_spec*

- **Dowód.** `internal_ramp()` przyjmuje płytę 0,30 m, a JSON (`kondygnacje[-2].strop_nad`) 0,35 m (−4,20 / −4,55). Przy krawędzi otworu (x = 15,39 m) wysokość w pionie wynosi 2,15 m, a prostopadle do spadku 18 % 2,12 m. Rampa uliczna ma 2,30 m w pionie i spełnia WT.
- **Wymaganie.** WT § 102 pkt 1 (2,2 m w świetle konstrukcji).
- **Poprawka.** Krawędź otworu cofnąć o 0,30 m (2,20 m w pionie) albo o 0,50 m (2,20 m prostopadle). W skrypcie przyjąć płytę 0,35 m. Przed bramą ogranicznik skrajni 2,10 m, w opisie limit pojazdów dostawczych 2,10 m. Przy dźwigu samochodowym (F3-01) problem znika.
- **Ryzyko.** Lokalna niezgodność z WT na rysunku przekroju.

#### F3-garaz-technika-10 – Stanowiska przy słupach i ścianach
*Waga: DROBNY (zgł. DROBNY) · F3 garaż · rewizja_spec*

- **Dowód (`v2/clear.py`).**
  - Stanowiska zaczynają się na 8,1k + 0,3, a słupy w osiach u mają 0,60 m, więc odstęp od lica słupa wynosi 0,00 m. Słup leży < 0,10 m od dłuższej krawędzi w 31 stanowiskach (15 na −1, 16 na −2).
  - W R2 słup osi v 8,70 wypada w strefie drzwi.
  - 5 stanowisk równoległych w skrzydle stoi 0,15 m od ściany szczelinowej.
- **Wymaganie.** WT § 104 ust. 3 pkt 2 (≥ 0,1 m od słupa i swobodne otwarcie drzwi); § 104 ust. 3 pkt 1 (≥ 0,3 m od ściany).
- **Poprawka.** Na −1/−2 słupy o wymiarze w kierunku u ≤ 0,40 m: np. 0,40 × 0,90 m (to samo pole przekroju) albo zespolone 0,40 × 0,60 z rdzeniem HEM. Słupy 0,60 × 0,35 obrócić. Zmianę przekroju przenieść w stropie nad −1. Prześwit 7,70 m ≥ 7,50 + 2 × 0,10 m. Rząd równoległy odsunąć o 0,15 m (droga A3 5,85 m ≥ 5,0 m).
- **Ryzyko.** Niezgodność z WT w 36 stanowiskach. Liczba miejsc się nie zmienia.

---

## 3. Sprawdzone i poprawne

Skrót list potwierdzeń z soczewek. Zastrzeżenia redakcyjne do tych list zebrano na końcu rozdziału.

**S1 – konstrukcja**
- Słupy obwodowe wieży (elewacje pd., pn., wsch., łuk R 13,5) przechodzą z kond. 1–6 na P bez przejęć. W podcieniu Bramy stoją wolno, a na −1 i −2 trafiają w ściany szczelinowe albo w ścianę uskoku u = 0.
- 12 słupów siatki jest ciągłych od kond. 6 do −2 (dane v1.0); trzony A i B sięgają od −2 do S.
- Filary elewacyjne 1,05 m co 2,70 m: konstrukcyjny jest co trzeci (8,10 m); na kond. 6 i S filary są ciągłe.
- Sala 200 os. w części skrzydła o trakcie 15,0 m: płyta sprężona 0,40 m na 14,2 m (L/h 35,5) bez przejęć; 4,25 m w świetle zgodne z 4.2.
- Drgania stropu skrzydła: f1 ok. 3,3 Hz, ap/g ok. 0,14 % < 0,5 % (AISC DG11).
- Ruszt dachu S: L/h 12,2 przy 19,5 m; warstwy 0,45 m mieszczą się, zapas MPZP 1,06 m zostaje.
- Wysokości kondygnacji w świetle (3,32 / 3,20 / 4,37 / 4,25 / 6,85 m) spójne z 4.2; korytarze z kanałami ≥ 2,2 m (WT § 242).
- Posadowienie skompensowane: wieża netto ok. 0 kPa, skrzydło ok. +20 kPa; mała różnica osiadań; płyta wieży na pospółkach QpIa1.
- Wypór wieży spełniony (173 kPa wobec 59–79 kPa); pas bez nadbudowy kotwiony mikropalami.
- Stateczność: trzony ok. 20 m od siebie, mimośród 2,9 / 1,3 m przy rzucie 40 × 29,7 m; wieża krępa (H/B ok. 1,25).
- Klasa B osiągalna: R 120, stropy REI 60, dach R 30.
- Pochylnia 18 % ≤ 20 % (WT § 70).
- Konstrukcyjne przyczyny deficytu miejsc w modelu v1.0 potwierdzone (13,4 m w świetle skrzydła wobec 16,0 m dla 2 rzędów).

**S2 – posadowienie**
- Geometria podziemia zgodna ze spec. w stanie v1.0 (obwód −1 244,65 m; pow. −1 2 337,2 m², −2 1 426,2 m²).
- Wypór globalny z dużym zapasem (ok. 334 MN wobec 153 MN przy 119,0) i lokalnie w strefach z nadziemiem.
- Pas dziedzińca bez nadbudowy: kotwienie wymagane i wykonalne (siła ok. 1,0–2,6 MN).
- Skrzydło nie stoi na nasypach: spód płyty ok. 114,55 poniżej spągu nasypów; piaski ID 0,6–0,7.
- Nośność i osiadania płyt: ok. 12–13 mm, różnica 1–3 mm.
- Przebicie dna przez gliny mało prawdopodobne (korek ok. 480 kPa wobec ok. 280 kPa) – pod warunkiem wcięcia przesłony.
- Wypór płyty wieży w fazie budowy rozwiązywalny (pale na rozciąganie albo odwodnienie wewnętrzne) – trzeba to zapisać.
- Przyczółek Mostu Grunwaldzkiego (54 m) i tory (50 m) poza strefą wpływu wykopu.
- Zasada „odwodnienie tylko wewnątrz przesłony wciętej w gliny” właściwa.
- Poziomy wody 117,0 i 119,0 przyjęte ostrożnie; parter 119,30 nad 119,0.
- Odpływ grawitacyjny z parteru możliwy (119,30 > 117,2–117,7).
- Wieża rozpoznana 4 otworami 30 m – wystarcza na etap konkursu.

**S3 – ppoż.**
- Budynek W (posadzka S +27,30 > 25 m, dźwig R obowiązkowy; wysokość ok. 36,6 m, z podziemiem ok. 43,8 m < 55 m), klasa B.
- Strefy pożarowe < 2 500 m² na kondygnacjach; garaż 4 365 m² < 5 000 m² bez tryskaczy.
- Dwie klatki w wieży 20 m od siebie; przedsionki A, B, C ≥ 1,4 × 1,4 m.
- Szerokość biegów dla S: 1,98 m ≤ 3,20 m.
- Dojścia na S, kond. 5–6 i w segmencie w limitach, w segmencie po usunięciu nieprawidłowych drzwi klatki B.
- Korytarze kond. 1–6 ≥ 1,40 m.
- Pasy międzykondygnacyjne ≥ 0,8 m; powyżej 25 m granit i wełna A1; BIPV elewacyjne ≤ 25 m.
- Brama garażu a okna kond. 1 (≥ 1,5 m, § 279).
- Brama ogrodowa 4,05 × 4,80 m spełnia wymagania przejazdu pożarowego.
- Odległości od sąsiadów: WS 5 10,58 m (≥ 8 m); gzyms skrzydła ≤ attyki Maz. 19.
- Drogi pożarowe Wybrzeża i Mazowieckiej w zakresie 5–15 m. Zastrzeżenie: elewacja pn. wieży (15–34 m) opiera się na wykładni „pierzei”, do potwierdzenia z rzeczoznawcą.
- Dźwig R: szyb 2,10 × 2,55 m, obsługa −2…S, przedsionek z MOE (po dodaniu drzwi z S3-ppoz-01).
- BESS na parterze w EI 120 w progach projektu WT § 310–312.
- Hala ma 4,37 m, więc może przyjąć drogę z jednej klatki, jeśli zostanie oddzielona (S3-ppoz-02 a).
- Połączenia garażu z trzonami przez przedsionki; dźwigi otwierające się na garaż wymagają drzwi EI 60 (§ 280 ust. 2) – do wpisania w opis.

**F1 – komunikacja**
- Hala: szerokość w świetle 7,06–15,9 m prostopadle do osi na odcinku s 2–24 m.
- A1/A2 i R mają możliwe drzwi na każdym przystanku; R otwiera się do przedsionka A; kabina R przyjmuje nosze.
- Ruch w dniu sesji wystarczający (70 os. A1/A2 w ok. 3,2 min, 30 os. P2 w ok. 4,4 min), bez rezerwy po stronie publicznej.
- Rozdział radni / publiczność na S prawidłowy co do zasady.
- Liczba stopni w biegu ≤ 17 przy każdej wysokości kondygnacji; biegi klatek A i B 1,60 m.
- Korytarze kond. 1–6 ciągłe przy ≥ 1,6 m, nominalnie 1,80 m.
- Skrzydło kond. 1–4: dwa połączenia z wieżą; ślepy koniec ok. 3–4 m; WC ≤ 33 m.
- Kond. 5–6: dojścia ≤ 25,5 m, WC ≤ 29,4 m, dźwigi ≤ 32 m.
- Dojścia na kond. 1–4 do przedsionka A ≤ 60 m przy dwóch kierunkach.
- WC z kabiną dostępną na każdej kondygnacji; hol przed A1/A2 ≥ 3,6 m.
- Liczba dźwigów osobowych w dominancie (5) zgodna z szacunkiem programu.

**F2 – program biur**
- 187 pokoi (179 × 24 + 8 × 32 m²), 1 pokój = 1 komórka, podział DRA zgodny z Wyj. 17 odp. 70.
- Wymiary netto ≥ 24,0 m²; BHP 8,0 m²/os., 26,7 m³/os.; wysokość ≥ 3,0 m.
- WT § 57 w 192 pomieszczeniach biurowych: mediana 0,231; poza DOS.19, DI.08 i KS.04a spełnione.
- Głębokość pokoi 6,10 m: kryterium głębokości granicznej 3,58 ≤ 4,0; DF śr. ok. 2 %.
- WC na kondygnacjach biurowych wystarczające; kabina dostępna na każdej kondygnacji.
- Liczności programu (pokoje socjalne, magazynki, sale narad, komfortka) zgodne.
- Centrale piętrowe 25 m² mieszczą ok. 7 000 m³/h.
- Elastyczność skrzydła (14,2 m bez słupów, moduł 1,35 m) – pod warunkiem F2-program-biura-03.
- Gabinety dyrekcji pionu 8 obok siebie (Wyj. 10 odp. 62); archiwa i pracownia GW na kondygnacji GW (R-213).
- Parter: pokoje DK II i DW z oknami; szatnia i foyer w zakresach programu.

**F3 – garaż i technika**
- Rampy 18 % z przejściami 9 % ≤ 20 %; długości 25,22 m i 19,67 m.
- Brama 4,0 m ≥ 2,3 m; odstęp do okien ≥ 1,5 m.
- Wysokości −1 3,65 m i −2 2,65 m ≥ 2,2 m; drogi 6,0 m; stanowiska 2,5 × 5,0 m, OzN 3,6 × 5,0 m; liczba OzN 6 ≥ 4,4.
- Wymagana liczba miejsc 106 / 108 (MPZP § 13) policzona poprawnie.
- Zjazd z 6KDB/2 zgodny z MPZP § 26 ust. 3.
- Rowerownia 50 stanowisk na 90 m² mieści się; wjazd od dziedzińca (Wyj. 7 odp. 32).
- BESS w EI 120 na parterze zgodny z proj. WT § 312 ust. 1–2 pkt 2.
- Technika krytyczna nad 119,0; UPS i serwerownia na kond. 1.
- Wyrzutnie w pasie lameli od pd. zgodne z MPZP § 6 pkt 13.
- Szacht B mieści oddymianie garażu, spaliny i 3 piony centrali S (zob. zastrzeżenie niżej).
- Wypór na −2 pod skrzydłem spełniony; mikropale pod pasem spójne.
- Dźwig T 2 000 kg z kabiną 1,5 × 2,7 m wystarcza (palety, pojemniki 1 100 l).
- EV: 55 punktów = 50 %; rezerwa mocy 407 kW do uwzględnienia w przyłączu.
- Przyłącze wody pod rampą: 2,8–3,4 m ≥ 2,0 m; centrala S 40 m² mieści się w kieszeni (przed F3-01).
- Agregat na wzmocnionym stropie kond. 1 konstrukcyjnie wykonalny.

**Zastrzeżenia redakcyjne do list „sprawdzone i poprawne”**
1. Część pozycji S1 i S2 opisuje geometrię v1.0. Dotyczy to: siatki v 0 / 8,1 / 21,6; garażu −1 3,25 m i −2 2,75 m; obwodu 244,6 × 18 m; pasa dziedzińca 174,3 m² i mikropali 175 m².

   Obowiązuje v1.1/v1.2: siatka v 0 / 8,70 / 16,00 / 23,15 / 29,70; −1 3,65 m, −2 2,65–2,70 m; ściany 222,6 × 19 m i 15 m iniekcji; pas 5,0 m, 124,5 m², mikropale 121,5 m². Wnioski się nie zmieniają.
2. Ruszt S: po S1-konstrukcja-01 rozpiętość wynosi ≤ 17,25 m (L/h 10,8). Ocena warstw i zapasu MPZP pozostaje aktualna.
3. Garaż −1/−2 w strefie 5 000 m². Lista S3 twierdzi, że −2 pod M1 „by się już nie zmieścił”. Arytmetycznie 4 365 + ok. 147 m² daje ok. 4 512 m² < 5 000 m² (`spojnosc.py`). Przed przyjęciem kompensacji z F3-garaz-technika-02 trzeba to potwierdzić, razem z poszerzeniem pasa z F3-01 (ok. +31 m² na −1). Zob. K-15.
4. Wniosek F3, że szacht B jest wystarczający, dotyczy zestawu bez wyrzutni zbiorczej i bez nadciśnienia. Z pełnym zestawem szacht jest przeciążony (S3-ppoz-07). Zapis „ok. 4 m²” w P-I5 jest zaniżony; rzeczywiście szacht ma 6,88 m².
5. „BESS 150 kWh” w listach S3 i F3 to stan v1.1. W v1.2 BESS ma 100 kWh (V12-KOSZT). Na parterze oba warianty są zgodne z progami proj. WT, na kond. 1 tylko ≤ 60 kWh (K-7).
6. Wysokość −1 3,65 m nie obowiązuje pod M1 po F1-komunikacja-10 (ok. 3,20 m) ani pod bramą po S1-konstrukcja-08 (2,95 m).
7. „Centrala S mieści się w kieszeni” traci aktualność przy rampie wewnętrznej 6,0 m (F3-01, K-12). „Rowerownia 50 stanowisk na 90 m²” – po G1 rowerownia ma 45,9 m² (K-2).
8. Dojścia w segmencie (S3) i do przedsionka A (F1) są poprawne pod warunkiem usunięcia drzwi klatki B na korytarz (S3-ppoz-01).

---

## 4. Odrzucone w weryfikacji

| ID | Tytuł (skrót) | Powód odrzucenia |
|---|---|---|
| S1-konstrukcja-02 | Strefa środkowa wieży: przęsło 13,5 m na płycie 0,28 m, przebicie przy słupach | Znane (weryfikacje / rejestr v1.1–v1.2). |
| S1-konstrukcja-05 | Dylatacja wieża–skrzydło nierozstrzygnięta; „wspólna płyta” niemożliwa | Znane (weryfikacja_geometria D-3, G-D-3). |
| S1-konstrukcja-07 | Ściany szczelinowe 18 m słabo wcięte w gliny | Dotyczy v1.0. W v1.1/v1.2 ściany mają 19 m, wcięcie 1,8–2,0 m (O-01…O-04), co jest zgodne z geotechnika.md rozdz. 4. Brak rozpoznania na pd. to znane K-01 (zadanie DGI). Ujęte jako luka opisu w S2-posadowienie-01. |
| S1-konstrukcja-09 | Kond. 6: półka stropu i spód poza izolacją, filary wolnostojące | Przeczy mu przekrój 1:50 korony: filar ma ścianę-słup żelbetową, czoła stropów przykrywa wełna 260 mm. Zostaje zwykły mostek na uskoku przegrody, do bilansu w PB. |
| S2-posadowienie-02 | Brak systemu podparcia obudowy i kolejności robót (metoda stropowa) | Znane (G-I-3: wykop rozparty stropami). |
| S2-posadowienie-03 | Uskok −1/−2 pod linią podporową na styku wieża–skrzydło | Znane (pozycja „ściana na uskoku −1/−2” w E-K-1, D-3). |
| S2-posadowienie-04 | Pale CFA bez uzasadnienia przy kompensacji ok. 85–87 % | Rachunek kompensacji poprawny, ale płyta palowo-fundamentowa jest zalecana przez geotechnika.md rozdz. 5 i ma uzasadnienie (osiadania względne, pale energetyczne, kotwienie w fazie budowy). To optymalizacja, nie błąd. |
| S2-posadowienie-06 | Strop nad −1 pod dziedzińcem bez miejsca na warstwy i zieleń | Oparte na v1.0 (pas 7 m, 174,3 m²). W v1.1 na stropie jest tylko taras bez nasadzeń (rozdz. 9), a drzewa są poza stropem; warstwy wykonalne. Część dotyczącą bramy ogrodowej ujęto w S1-konstrukcja-08. |
| S2-posadowienie-08 | Sondy GPC przebijają gliny, wiercenie z dna pod naporem | Weryfikacja: znane. Uwaga redakcyjna: ten sam temat potwierdzono jako nowy w F3-garaz-technika-08 (I-2 dotyczyło lokalizacji pola i art. 86 PGiG). W rejestrze obowiązuje F3-08. |
| S2-posadowienie-09 | Efekt bariery boksu a zwierciadło przy Maz. 19 i WS 5 | Skutek ±0,03–0,09 m mieści się w wahaniach naturalnych (±0,5 m). Przy wysokich stanach Maz. 19 jest po stronie obniżenia. Ocena należy do DGI i operatu wodnoprawnego. |
| S2-posadowienie-10 | Niespójności rysunków i JSON; obrys ścian przy narożu NW wieży | Znane. |
| S3-ppoz-05 | Kond. 1–4: ślepy korytarz pd. 19–28 m | Weryfikacja: znane (V12-OPEN 1, przebudowa trzonu A). Uwaga: skutek przerwania pierścienia (WC 73–78 m) ujęto w F1-komunikacja-03. |
| S3-ppoz-06 | Klatki A i C nie mieszczą biegów 1,60 m i spoczników; MOE w przedsionkach | Znane (V12-I5A/B, V12-OPEN 2). |
| F1-komunikacja-04 | Klatki A i C (na P także B) nie mieszczą biegów zgodnych z WT § 68–69 | Znane (j.w.). |
| F1-komunikacja-06 | P1 i T a przystanki na S i antresoli; „dwa publiczne dźwigi” to faktycznie P2 | Znane (P-I5, V12-DZW, rozdz. 7.4 v1.2). |
| F1-komunikacja-08 | Dostawy: brak strefy przyjęcia z poziomu terenu, dźwig T przez lobby | Weryfikacja: znane (P-I5). Uwaga: brak IT.15 i drogi do T w geometrii v1.1 ujęto w F3-garaz-technika-05. |
| F1-komunikacja-09 | Bistro i bar Sejmiku bez drogi zaopatrzenia | Trasy 40–55 m wynikały z modelu v1.0 (T w trzonie B). W v1.2 droga: −1 → A1/A2 → łącznik → bistro (ok. 8–12 m). Relacja „dostawy → bistro” to wniosek autora programu, nie wymóg PU. |
| F1-komunikacja-11 | Dźwigi otwierają się do garażu bez przedsionków i drzwi EI 60 | Znane (lista „sprawdzone” S3: drzwi przystankowe EI 60 wg § 280 ust. 2 do wpisania w opis). |
| F2-program-biura-06 | Okna kond. 5 na zach. licu wieży zasypie worek śnieżny | Fałszywa przesłanka. Kordon granitowy +19,80–20,85 sprawia, że dolna krawędź okien leży na +20,85, czyli 0,45–0,65 m nad pokryciem skrzydła (`elewacje.py`, `przekroje.py`). Worek śnieżny to przypadek obciążenia w PB. |
| F3-garaz-technika-11 | Ochrona przed zalaniem niespójna (zapora 120,30, progi 119,30–119,60) | Żaden wymóg nie jest naruszony: poziom miarodajny ok. 119,0, teren poza Q10/Q1/Q0,2 %. Zapora to dodatkowy zapas na jedynym otworze spadkowym. |

Razem odrzucono 20 ustaleń: 12 jako już znane, 8 merytorycznie (nieaktualna wersja, fałszywa przesłanka albo brak naruszenia wymagania).

---

## 5. Kolejność wdrożenia i powiązania między poprawkami

### 5.1. Decyzje blokujące (przed jakimkolwiek rysunkiem)

| Nr | Decyzja | Warianty | Od niej zależą |
|---|---|---|---|
| D-1 | Rampy i obsługa −2 (F3-garaz-technika-01) | Rampa uliczna dwukierunkowa 5,5 m (bez alternatywy). Obsługa −2: (a) rampa wewnętrzna 6,0 m – zabiera ok. 19 m² GPC, wymaga przeniesienia centrali S na kond. 1, zostawia słup S1-01 przy krawędzi rampy; (b) dźwig samochodowy (§ 103 ust. 1) – kolejka 2–4 aut w szczycie, zwalnia ok. 34 m² na −1 i ok. 51 m² na −2, niewyceniony. Parter segmentu: poszerzenie 1,5 m (zalecane) albo wariant bez zmiany bryły. | S1-06 (K-8), S3-08/F3-04 (K-6), S3-09 i BESS (K-7), F3-05, F3-06 (K-16), F3-07, S3-04 (K-11), K-12, K-17, F3-09, koszt |
| D-2 | Strategia ppoż. garażu (S3-ppoz-04) | (a) samoczynna wentylacja oddymiająca kanałowa (+0,15–0,25 mln); (b) tryskacze OH2 w garażu (ok. 0,6 mln) | wielkość zbiornika (+45 m³ przy b), obciążenie szachtu B (S3-07), ładowarki EV na platformach (F3-03), moc agregatu (F3-07) |
| D-3 | Układ parteru skrzydła i M1 | Pakiet G1 (kolejność: brama, sala 200, sala 80, foyer) + obniżenie M1 (F1-10) + uskok stropu pod bramą (S1-08) | F2-02, F2-03 (ściana mobilna, ścianki w oknach), S3-02 c (K-13), S3-10, K-2, K-3, K-14, K-18, bilans miejsc |
| D-4 | Kompensacja miejsc postojowych (rozdz. 5.5) | −2 pod M1 (+6, ok. 0,4–0,6 mln) – jedyne źródło wskazane w audycie; inne do znalezienia przez `rewizja_spec` | S2-01 (DGI przy O-08), S2-05 (wykop przy Maz. 19), S3-04 (klatka C do −2 jako drugie wyjście – K-15), strefa 5 000 m² |
| D-5 | Konstrukcja sali Sejmiku (S1-konstrukcja-01) | Tarcza pd. + słup elewacji wsch. (zalecane) | S3-07 (K-9), F3-01 (K-17); niezależna od D-1…D-4, można zacząć od razu |

### 5.2. Zalecana kolejność wdrożenia

**Faza 0 – decyzje D-1…D-5** (koordynator + `rewizja_spec`, `kondygnacja_S2`).

**Faza 1 – specyfikacja i JSON** (`rewizja_spec`, `kondygnacja_S2`):
1. Garaż i segment: F3-garaz-technika-01 → S1-konstrukcja-06 (K-8) → F3-05 → S3-ppoz-09 i BESS (K-7) → S3-ppoz-08 + F3-04 (K-6) → F3-06 (K-16) → F3-07.
2. Garaż – ewakuacja i układ: S3-ppoz-04 (drzwi B na −2/−1, D-2) → S3-ppoz-07 (szachty; K-9 z S1-01) → F3-03 → F3-02 (zatoka) → F3-09, F3-10 → bilans miejsc (5.5) → tab. 12, rozdz. 16 pkt 10, F.15.C.
3. Sala Sejmiku: S1-konstrukcja-01 (`kondygnacja_S2`) → przekroje A-A i B-B, z uwzględnieniem K-9 i K-17.
4. Oś Hali: S1-konstrukcja-03 → rozdz. 11 (K-5) → przekazanie do `agent_rzutow` (F1-01).
5. Parter: S3-ppoz-02 → pakiet G1 (S3-03 / F1-02) → F1-komunikacja-10 + S1-konstrukcja-08 (K-13, K-18) → S3-ppoz-10 → F1-05, F1-07, F2-09.
6. Teksty bez wpływu na układ: S1-konstrukcja-04 (K-10), F2-program-biura-03, S2-posadowienie-01, S2-posadowienie-05, F3-garaz-technika-08.

**Faza 2 – generator i model** (`agent_rzutow`), jeden przebieg razem z V12-OPEN 1:
1. Drzwi trzonów (S3-ppoz-01, F1-03 c, F2-08) – najpierw, bo zależą od nich wszystkie rzuty.
2. Strefa środkowa kond. 1–6: pierścień (F1-03), IT i archiwa (F2-04), szczeliny (F2-07), SZ-1 (S3-07).
3. Parter wg fazy 1: F1-01, F2-01, F2-02, F2-05 (K-1…K-4, K-10, K-14).
4. Okna i elewacje: lico styku (F2-05, K-10), pas EI 60 (S3-10), słupki (F2-03); meble (F2-10).
5. Kondygnacje −1 i −2 z `_rewizja_parking.py` po F3-01…F3-04 i F3-10; przepompownia (S2-07).
6. Jeden pakiet testów w `budynek.json['testy']`:
   - każda klatka osiągalna wyłącznie przez przedsionek, na każdej kondygnacji;
   - każde pomieszczenie ma ≥ 1 drzwi albo jest otwartą wnęką;
   - pomieszczenie dla > 50 os. ma ≥ 2 wyjścia w odstępie ≥ 5 m w świetle;
   - sekretariat ma drzwi do gabinetu;
   - pomieszczenie pomocnicze ma szer. ≥ 1,8 m, PD ≥ 2,0 × 3,0 m;
   - pas pierścienia 1,80 m jest wolny;
   - pas osi Hali wg K-5;
   - przed drzwiami pole 1,5 × 1,5 m bez słupów;
   - ślepe odcinki ≤ 20 m poziomo, dojścia ≤ 60 m;
   - WC ≤ 75 m od stanowiska.

**Faza 3 – rysunki i tabele:**
- rzuty P, −1, −2, 1–6, S (P3–P5);
- przekroje A-A i B-B oraz nowy przekrój przez bramę ogrodową (P6);
- elewacje: brama ≥ 6,0 m cofnięta, pas EI 60 przy Maz. 19, słupki dodatkowe;
- PZT: droga wewnętrzna z dz. 10/2, spoczniki i taras przy skrzydle, 2 hydranty, nasada 75 mm;
- F.15.A–C (PU, I.11 = 5 + T, bilans miejsc z wariantem ostrożnym), F.14.B (koszt);
- opis etap2 (posadowienie i III kategoria, ppoż. garażu, matryca stref);
- kadry W3, W6, W10.

### 5.3. Macierz powiązań

| Zmiana | Wpływa na | Charakter |
|---|---|---|
| F3-01 rampa 5,5 m i brama ≥ 6,0 m | S1-06, S3-08, S3-09, F3-05, F3-06, F3-07, E-K-1 | konflikty K-6, K-7, K-8, K-16; koszt +0,65 mln |
| F3-01 obsługa −2 rampą 6,0 m | GPC (S3-04), centrala S → kond. 1 (F2-04, S3-07), słup S1-01 | K-11, K-12, K-17; dźwig samochodowy usuwa wszystkie trzy |
| S3-04 oddymianie albo tryskacze | S3-07, S3-08/F3-04, F3-03, F3-07 | przy tryskaczach zbiornik +45 m³, EV na platformach dopuszczalne |
| S1-03 usunięcie słupów | F1-01, rozdz. 11, garaż R4, kadry W3/W6 | K-5; konstrukcyjnie bez przejęć |
| Pakiet G1 | F2-02, F2-03, PR.01/PR.02, S3-02 (Hala jako hol), PZT, P-D5, S1-04 (belka przy foyer) | K-2, K-3, K-14 |
| F1-10 + S1-08 (rzędne stropu nad −1) | stackery (−2 m.p.), klatka C, S3-02 c, S3-10, F3-03 R1 | K-13, K-18 |
| S3-02 korytarz klatki B | F1-01 (SW.06), pas osi Hali, PHS.02 | K-1, K-4, K-5 |
| S1-01 tarcza pd. sali | S3-07 (kanały EIS), drzwi galerii, F3-01 (słup przy rampie) | K-9, K-17 |
| F3-02 zatoka i kompensacja | bilans miejsc, S2-01, S2-05, S3-04, strefa 5 000 m² | K-15 |
| S1-04 belka pasmowa i słup narożny | F2-05 (okno w licu styku) | K-10 |
| S3-07 szacht SZ-1 | strefa pn.-zach. Hali (komfortka, PHS.02, SW.06), WC PHS.05 na S (≥ 35 m²), kond. 1 | K-1, K-9, K-12 |
| F2-04 strefa wzmocniona stropu | siatka stropów, koszt | < 0,06 mln |
| S2-07 / F3-04 | jedna przepompownia na −2, separator, przelew deszczówki | bez kolizji z garażem |

### 5.4. Konflikty między poprawkami wykryte przy redakcji i ich rozstrzygnięcia

Sprawdzenia liczbowe: `/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/audyt_kf/redakcja/spojnosc.py`.

- **K-1. PHS.02 a oś Hali (F2-02 pkt 3 ↔ F1-01, idea).** Prostokąt u 11,6–15,5 × v 0,5–9,0 przecina oś na 5,48 m (27,7 m² w pasie ±3 m), czyli odtwarza wadę PHS.04 (ok. 5,6–5,8 m). Lokalizację odrzucono. Po stronie pd.-wsch. osi, między drzwiami ogrodowymi a korytarzem klatki B, poza pasem ±3 m zostaje tylko 10,6 m². PHS.02 ≥ 30 m² (P-I3) da się więc umieścić tylko po stronie pn.-zach., przy trzonie A. Tę samą strefę zajmują komfortka (P-I3), SZ-1 (S3-07) i ewentualnie SW.06, więc potrzebny jest jeden wspólny rzut z testem pasa osi.
- **K-2. PR.02 a przejście hala–foyer (F2-02 pkt 2 ↔ F1-02).** Nakładanie wynosi 11,5 m². Rozstrzygnięcie: rowerownia v 0,5–6,5 (45,9 m², 50 rowerów w 2 rzędach stojaków dwupoziomowych: 7,0 ≤ 7,65 m głębokości, 5,0 ≤ 6,0 m długości rzędu), PR.02 v 6,5–8,5 (15,3 m²), przejście v 8,9–11,85, WC konferencyjne v 12,45–20,85.
- **K-3. Wielkość WC konferencyjnych (F1-01 ok. 37–38 m² ↔ F2-02 ok. 55–60 m²).** Przyjęto F2-02, bo tylko ono liczy przybory dla 280 os.: cały pas v 12,45–20,85 (64,3 m² brutto). Szatnie i WC personelu przenieść wg D4 (PPT.05 na −1, w strefie MDS i sanitariatów, bez zajmowania stanowisk), natryski rowerzystów do PR.02.
- **K-4. Pokój cichy SW.06 a korytarz klatki B (F1-01 pkt 4 ↔ S3-02 b).** SW.06 w u 21,0–24,7 × v 0,5–6,5 nakłada się na korytarz EI 60 na 2,6 m². Po przycięciu do v 0,5–5,6 (18,9 m²) jest zamknięty: od zach. i pn. korytarzem ewakuacyjnym, od wsch. trzonem B, od pd. elewacją. Dostęp byłby tylko z chronionego korytarza, co jest niedopuszczalne. Rozstrzygnięcie: SW.06 wg wariantu alternatywnego F1-01, po stronie pn.-zach. osi. Kieszeń u 21,0–24,85 × v 0,5–5,8 (ok. 20 m²) włączyć do korytarza albo przestawić trasę korytarza wzdłuż lica pd. (v 0,5–2,1) tak, by nie tworzył zamkniętej kieszeni. Decyzja na rzucie.
- **K-5. Pas osi Hali (test ±3 m z F1-01 ↔ S3-02, S1-03).** Narożnik korytarza klatki B leży 1,34 m od osi (s = 11,9 m od drzwi ogrodowych), słupy (24,3; 16,0) 1,34 m (s 21,4) i (16,2; 8,70) 1,83 m (s 10,5). Pas ±3 m na całej długości jest więc niewykonalny. Rozstrzygnięcie: rozdz. 11 wg S1-03 – „pas osi ≥ 2,0 m wolny od przeszkód”, faktycznie ok. 2,6 m. Test generatora: pas ±1,0 m wolny na całej długości, a pas ±3 m wolny od pomieszczeń na pierwszych 6 m od drzwi w łuku i od drzwi ogrodowych.
- **K-6. Lokalizacja zbiornika i pompowni ppoż. (S3-08 ↔ F3-04 ↔ F3-01).** Wolne ok. 16 m² w pasie pd. segmentu na P (S3-08) znika przy rampie dwukierunkowej: pas spada do ok. 26,7 m² netto, z czego 15,7 m² o szer. ≥ 2,0 m, przy programie ok. 83 m². Rozstrzygnięcie: wariant bazowy to klin −2 z F3-04, jako odrębna strefa REI 120, z dostępem z drogi A4 i dźwigiem T i zasilaniem z agregatu. Zbiornik 25 m³ jest na granicy. Przy 50 m³ albo przy tryskaczach (+45 m³) trzeba poświęcić ok. 2 stanowiska na −2 albo przestrzeń zwolnioną przez dźwig samochodowy. Odstępstwo od zasady E-I-4 („technika krytyczna nad 119,0”) trzeba jawnie uzasadnić w opisie: pomieszczenie jest wewnątrz białej wanny z otworami ≥ 120,30.
- **K-7. BESS na kond. 1 (F3-01 pkt 2 ↔ proj. WT § 312).** Lista „sprawdzone” S3 i F3 oraz proposed_fix samego F3-01 przyjmują, że magazyn > 60 kWh może stać tylko na pierwszej kondygnacji nadziemnej. Rozstrzygnięcie: BESS na kond. 1 tylko przy ≤ 60 kWh. V1.2 ma 100 kWh, więc zmniejszenie wymaga korekty bilansu energii; w przeciwnym razie BESS zostaje na parterze poszerzonego segmentu. Rozdzielnia z SZR na kond. 1 nad komorą trafo jednocześnie spełnia § 182 (S3-09).
- **K-8. Słupy segmentu a nowa brama (S1-06 ↔ F3-01).** Położenia słupów z S1-06 (v ok. −4,60 / −4,75 / −8,80) dobrano dla bramy 4,0 m i rampy 3,5 m. Przy bramie ≥ 6,0 m i rampie 6,0 m (v −0,15…−6,4) słup lica wsch. może stanąć dopiero przy v ≤ −6,7, a lico zach. ma tylko narożnik SW (−7,12). Potrzebne są belki krawędziowe ok. 6,7 m i ok. 7,1 m na każdej kondygnacji i pod tarasem. Żaden słup nie może stać w świetle bramy (wtedy przejęcie M ok. 1,5 MNm, belka h ok. 1,0 m). Cofnięcie bramy o 1,5–2,0 m tworzy podcień pod segmentem, który trzeba pokazać na elewacji i przekroju.
- **K-9. Kanały EIS a cięgno tarczy sali (S3-07 ↔ S1-01).** Trasa „pod stropem antresoli nad kuluarem” (kuluar 3,30 m zmniejszony do ≥ 2,50 m, czyli kanały ok. +29,80…+30,60) leży w paśmie cięgna tarczy (+29,70…+30,90). Rozstrzygnięcie: przejścia kanałów przez tarczę tylko w środkowej tercji rozpiętości (u ok. 23,5–31,5), powyżej cięgna, obramowane i ujęte w obliczeniu tarczy (`kondygnacja_S2`). SZ-1 nie może naruszać strefy podporowej przy trzonie A (u 15,5–17,5), w której są już drzwi galerii (17,5; +30,90).
- **K-10. Okno w licu styku a słup narożny (F2-05 ↔ S1-04).** Wariant 2 × 1,20 m + filar 0,825 m + ościeża wypełnia całe 3,83 m. Rozstrzygnięcie: jedno okno systemu wieży 1,65 × 2,45 m = 4,04 m² obok słupa narożnego (1,65 + 0,60 + 2 × 0,30 = 2,85 ≤ 3,83 m). Spełnia to DOS.19 (3,32 m²) i DI.08 (3,01 m²).
- **K-11. Maszynownia GPC (S3-04 ↔ F3-01).** Pole przed drzwiami przedsionka B zabiera ok. 2,3 m², a rampa wewnętrzna 6,0 m ok. 19 m², więc GPC spada z 97,3 do ok. 76 m² wobec wymaganych 95 m². Przy rampie 6,0 m trzeba odtworzyć ok. 19–21 m², np. kosztem stanowisk. Dźwig samochodowy zwalnia ok. 51 m² na −2.
- **K-12. Strefa środkowa kond. 1 (F3-01 ↔ F2-04 ↔ S3-07).** Przy rampie wewnętrznej 6,0 m na kond. 1 trafia centrala S 40 m², obok IT.01 ≥ 45–50 m² + UPS 15 m² (F2-04), centrali piętrowej 25 m², szachtu SZ-1 ok. 5 m² i pionu 1,33 m. Przed przyjęciem rampy 6,0 m trzeba przeliczyć bilans kond. 1. Dźwig samochodowy usuwa potrzebę przenoszenia centrali S.
- **K-13. Stopnie przy klatce C (S3-02 c ↔ F1-10).** Po obniżeniu posadzki M1 do ok. 118,82–118,85 stopnie przy drzwiach klatki C (4 stopnie do 118,6) i przy KW.P.16 (3 stopnie do bramy) są zbędne albo zostaje najwyżej 1 stopień lub pochylnia. Klatkę C przeliczyć wg F1-10 (P/1: 31 × 17,03 cm w 3 biegach). Drzwi klatki C poza pasem EI 60 (s ≥ 2,0; S3-10).
- **K-14. Hala jako hol ewakuacyjny klatki A (S3-02 a ↔ F1-01, F1-02, F1-05, F2-02, F2-05).** Według § 256 ust. 6 hol ma być oddzielony od dróg poziomych i pomieszczeń. Każde nowe połączenie z Halą potrzebuje więc drzwi EI 30, na elektrotrzymaczach tam, gdzie mają stać otwarte: przejście do foyer, przejście z lobby P1/P2, WC i PHS.02, SW.06. Otwarta lada kancelarii w Hali (F2-05 c) wymaga potwierdzenia rzeczoznawcy. Wariant bezpieczny to kancelaria przy elewacji Wybrzeża obok DK II.
- **K-15. Kompensacja −2 pod M1 (F3-02) – skutki.**
  - (i) Strefa garażu: ok. 4 365 + 147 = ok. 4 512 m² < 5 000 m² (§ 277 ust. 1). Lista S3 twierdzi przeciwnie, więc trzeba to potwierdzić razem z poszerzeniem pasa z F3-01.
  - (ii) Wykop −2 zbliża się do Maz. 19 na ok. 1,2 m i schodzi ok. 6 m poniżej ław 116,0–116,4. Podbicie i przesłona z S2-05 wymagają przeprojektowania, a DGI w rejonie O-08 (S2-01) staje się warunkiem.
  - (iii) Możliwa korzyść, niezweryfikowana: przedłużenie klatki C z przedsionkiem EI 30 do −2 dałoby części −2 pod skrzydłem drugie wyjście w odległości < 40 m (S3-04), niezależnie od D-2, i mogłoby zastąpić szyb awaryjny ukrycia z V12F-RYZ R2 (0,27 mln).
- **K-16. Droga wewnętrzna a poszerzenie segmentu (F3-06 ↔ F3-01).** Po poszerzeniu pas ma 3,1 m, więc mieści drogę 3,0 m bez opaski. Droga 3,5 m wymaga wariantu F3-01 bez zmiany bryły.
- **K-17. Słup elewacji wsch. a rampa wewnętrzna 6,0 m (S1-01 ↔ F3-01).** Słup 0,60 × 0,60 m na −1/−2 musi mieścić się w grubości ściany szczelinowej (u 39,4–40,0). Rampa 6,0 m w świetle odbojów sięga u 39,4, więc każdy wysięg pilastra zwęża ją poniżej 5,5 m (§ 103 ust. 2).
- **K-18. Rzędne stropu nad −1 (S1-08 ↔ F3-03 ↔ G-K-2 ↔ F1-10).** Przyjąć S1-08: strop pasa dziedzińca 119,15 → 119,08 ze spadkiem 1,5 %, nawierzchnia 119,28. Jest to możliwe, bo na stropie jest taras bez nasadzeń (rozdz. 9; S2-06 odrzucone), a R1 zachowuje stackera. W JSON `kondygnacje[-1].strop_nad` wpisać jedną rzędną z wyjątkami: pod bramą 118,45, pod M1 ok. 118,70 (F1-10), ogon rampy −0,77 (G-K-2).
- **K-19. Zapas kosztowy (F3-01 ↔ V12F-KOSZT).** F3-01 liczy z zapasem 0,82 mln z v1.1 (E-K-1). Obowiązuje V12F-KOSZT: 148,99 mln, zapas 1,01 mln przy rezerwie 5 % i 2,43 mln przy rezerwie 4 %.

### 5.5. Bilans miejsc postojowych po poprawkach

| Krok | Zmiana | Stan | Źródło |
|---|---|---|---|
| v1.2: 113 pozycji minus 3 za 6 OzN | – | 110 | PARK, V12F-BIL |
| Uskok stropu pod bramą ogrodową / M1 obniżony | −2 | 108 | S1-08, F1-10 |
| Zatoka do zawracania u stopy rampy (−1) | −5 | 103 | F3-02 |
| OzN na −2 zamiast na −1 | 0 (opis „OzN na −1” dawałby ok. −6 więcej) | 103 | F3-03 |
| R1 przy stropie pasa wg S1-08 | 0 (−2, gdyby wierzch stropu ≤ 118,85) | 103 | F3-03, K-18 |
| Zbiornik ppoż. 25 m³ w klinie −2 | 0 (−2 przy 50 m³ albo tryskaczach) | 103 | F3-04, K-6 |
| Drzwi pn. przedsionka B, słupy 0,40 m, stopa rampy dwukierunkowej | 0 / do przeliczenia skryptem po F3-01 | 103 | S3-04, F3-10, F3-01 |
| **Wymagane (MPZP § 13)** | | **106** (108 przy odczycie ostrożnym) | V12F-BIL |
| **Deficyt** | | **−3** (−5) | |
| Kompensacja: −2 pod M1 | +6 | 109 | F3-02 (`variant4.py`), K-15 |

Wniosek: bez kompensacji projekt nie spełnia MPZP § 13. Z −2 pod M1 bilans wynosi 109 ≥ 106, a przy odczycie ostrożnym zapas to 1. Warianty z −2 (zbiornik 50 m³, R1 bez stackera) wyczerpują ten zapas, więc rzędne stropu (K-18) i wydajność sieci (MPWiK) trzeba ustalić przed zamknięciem bilansu.

### 5.6. Koszt poprawek (szacunki z ustaleń, z KS i rezerwą)

| Pozycja | mln zł |
|---|---|
| S1-konstrukcja-01 (tarcza, słup) | 0,10–0,20 |
| S2-posadowienie-01 (warunkowo, +2 m ścian po DGI) | 0,00–0,32 |
| S2-posadowienie-05 (dodatkowe kolumny) | 0,05 |
| S2-posadowienie-07 (przepompownia, separator) | 0,10 |
| S3-ppoz-02 (korytarz klatki B, drzwi) | 0,05–0,10 |
| G1: S3-03 / F1-02 / F2-01 (drzwi, spoczniki) | 0,10–0,15 |
| S3-ppoz-04 – oddymianie kanałowe garażu | 0,15–0,25 |
| G3: S3-08 / F3-04 (zbiornik, pompownia, hydranty) | 0,20–0,30 |
| S3-ppoz-10 (szkło EI 60) | 0,12–0,15 |
| F2-program-biura-03 (słupki dodatkowe) | 0,10 |
| F2-program-biura-04 (strefa wzmocniona) | 0,06 |
| F3-garaz-technika-01 (rampa, poszerzenia) | 0,65 |
| F3-garaz-technika-02 – kompensacja −2 pod M1 | 0,40–0,60 |
| F3-garaz-technika-08 (technologia wiercenia GPC) | 0,20–0,30 |
| **Razem** | **ok. 2,28–3,33** |
| Wariant tryskaczy w garażu zamiast oddymiania | +0,35–0,45 |
| Niewycenione | szacht SZ-1 (S3-07), droga wewnętrzna i skrzynki SLW 30 (F3-06), chłodnica wyniesiona (F3-07), DCS i kontrola dostępu (F1-05, F1-07), dźwig samochodowy (D-1 b) |

Wniosek: pakiet przekracza zapas 1,01 mln przy rezerwie 5 %. Przy rezerwie 4 % (zapas 2,43 mln; E-K-1 dopuszcza ≥ 4 %) mieści się tylko wariant dolny. Rewizja kosztowa musi więc przed następną wersją specyfikacji wybrać kombinację:
- obniżenie rezerwy do 4 %;
- dźwignię rezerwową (filary pd. wieży w ceramice −0,23);
- oddymianie zamiast tryskaczy;
- K-15 iii zamiast R2 (szyb awaryjny, 0,27).
