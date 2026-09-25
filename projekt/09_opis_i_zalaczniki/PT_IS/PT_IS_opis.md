# Projekt techniczny — PT-3 IS (instalacje sanitarne) — tom 3 z 4

*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_IS.py`; wersja wiążąca: PDF. Pełne obliczenia (raporty bibliotek `lamela.obliczenia`) — w PDF.*

*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny `lamela.dokumenty`; pełna treść w PDF]*

# Opis techniczny — instalacje sanitarne (§ 23 RPB)

## Stan opracowania i sprawy otwarte — rejestr wymagań, sekcja E

Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z 2026-09-25 10:33) i bibliotek obliczeniowych
`lamela.obliczenia` uruchamianych przy każdym generowaniu tomu — każda liczba w tomie pochodzi z modelu albo
z obliczeń. Działka, MPZP, warunki gruntowo-wodne i warunki przyłączenia są [DANE PRZYKŁADOWE – FIKCYJNE]; parametry urządzeń
przyjęto z kart **wyrobów przykładowych** (oznaczenie [DANE PRZYKŁADOWE – FIKCYJNE] lub [ZAŁ]) — dopuszcza się wyroby równoważne
spełniające parametry wymagane podane w rozdziale „Zasadnicze urządzenia”.

**Tabela 1. Wynik sprawdzeń obliczeniowych PT-3 IS**

| Obszar obliczeń | Warunków | Spełnione | Niespełnione | Informacyjne |
|---|---|---|---|---|
| Instalacja wodociągowa i c.w.u. | 12 | 12 | 0 | 0 |
| Kanalizacja sanitarna | 33 | 33 | 0 | 0 |
| Wody opadowe i retencja | 120 | 120 | 0 | 0 |
| Drenaż i odwodnienie powierzchniowe | 20 | 6 | 0 | 14 |
| Ogrzewanie (PC, podłogówka, bufor, naczynia, hałas) | 68 | 62 | 0 | 6 |
| Wentylacja mechaniczna (bilans, centrala, czerpnia/wyrzutnia) | 12 | 12 | 0 | 0 |
| Charakterystyka energetyczna (EP ≤ EP_max; wariant z PV i bez PV) | 2 | 2 | 0 | 0 |

Warunki informacyjne — wartości podawane bez kryterium (np. moc ścian grzewczych uzupełniających).

*Źródło: lamela.obliczenia.sanitarne, lamela.obliczenia.energia — uruchomienie przy generowaniu tomu*

Numeracja pomieszczeń w tomie — jak na arkuszach i w PT-1 AR (PN-B-01025, W-314): numer kondygnacji (parter = 1, I piętro = 2, II piętro = 3), kropka, numer kolejny. Identyfikatory modelu (`model/budynek.yaml`) mają parter = 0 — numer w tomie = identyfikator modelu + 1 w części przed kropką.

**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status aktualizuje się przy ponownym generowaniu):

1. `instalacje.wyroby` w modelu puste — obliczenia na danych przykładowych bibliotek (PC, centrala wentylacyjna, wodomierz Δp(Q3), zawór EA k_v, wpusty) [DANE PRZYKŁADOWE – FIKCYJNE]; zastąpić danymi DTR/DWU wyrobów wybranych przez wykonawcę (wyroby równoważne).
2. Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji `projekt:` w model/budynek.yaml; pola oznaczone jako do uzupełnienia (strona tytułowa, oświadczenie).

## Przedmiot, zakres i podstawy opracowania — § 23 RPB

**Przedmiot.** Projekt techniczny instalacji sanitarnych budynku mieszkalnego jednorodzinnego
„Dom LAMELA” — działka ewid. nr 123/4, obręb 0005 „Przykładowo”, gm. Przykładowo (fikcyjna): ogrzewanie wodne
płaszczyznowe zasilane pompą ciepła powietrze–woda z automatyczną regulacją temperatury, wentylacja mechaniczna
nawiewno-wywiewna z odzyskiem ciepła, instalacja wody zimnej i ciepłej, kanalizacja sanitarna, odprowadzenie
i zagospodarowanie wód opadowych (retencja), odwodnienie powierzchniowe, charakterystyka energetyczna budynku.

**Zakres wg RPB (rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, Dz.U. 2020
poz. 1609, t.j. Dz.U. 2022 poz. 1679 ze zm.):**

* § 23 pkt 7 lit. a — instalacje ogrzewcze z urządzeniami automatycznie regulującymi temperaturę oddzielnie
  w poszczególnych pomieszczeniach; lit. d — wentylacja mechaniczna; lit. e — instalacje wodociągowe
  i kanalizacyjne (w tym wody opadowe);
* § 23 pkt 7 lit. b i c (chłodzenie, klimatyzacja) — nie dotyczy: w modelu brak instalacji chłodzenia (`energia.chlodzenie`);
  lit. f (gaz) — nie dotyczy: budynek bez instalacji gazowej (źródło ciepła elektryczne — pompa ciepła);
  lit. g–i — tom PT-4 IE; lit. j (instalacje ochrony przeciwpożarowej) — nie dotyczy (dom jednorodzinny);
* § 23 pkt 8 — powiązanie z sieciami zewnętrznymi i punkty pomiarowe, założenia (lit. a — parametry klimatu
  wewnętrznego), obliczenia i dobór urządzeń (lit. b — moce cieplne i elektryczne);
* § 23 pkt 9 — zasadnicze urządzenia (pompa ciepła, zasobnik c.w.u., bufor, centrala wentylacyjna, zbiornik
  retencyjny); § 23 pkt 10 — dane ppoż. stosownie do zakresu; § 23 pkt 11 lit. a–d — charakterystyka energetyczna;
* § 23 pkt 5 — nie dotyczy; § 23 pkt 6 — nie dotyczy (budynek mieszkalny, nie obiekt liniowy); § 23 pkt 4a —
  nie dotyczy (W-231);
* § 23 pkt 12 (dodany Dz.U. 2026 poz. 597 § 1 pkt 6) — nie dotyczy: PZT i PAB nie przewidują budowli
  ochronnej ani miejsca doraźnego schronienia (PAB § 20 ust. 1 pkt 14 — n/d);
* § 24 pkt 3 i pkt 4 lit. a — rzuty i schematy instalacji (część rysunkowa).

**Podstawy prawne i techniczne (rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`).**
Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.); warunki techniczne (WT 2002; t.j. Dz.U. 2022 poz. 1225
ze zm.) — stosowane na podstawie art. 102a PB; metodologia charakterystyki energetycznej (Dz.U. 2015 poz. 376
ze zm., ost. 2023 poz. 697); rozporządzenia (UE) 2024/573 (F-gazy), 813/2013 (ekoprojekt PC), 1253/2014
(centrale wentylacyjne); rozporządzenie w sprawie dopuszczalnych poziomów hałasu w środowisku (t.j. Dz.U. 2014
poz. 112); Prawo wodne (t.j. Dz.U. 2025 poz. 960 ze zm.). Normy: PN-EN 12831:2006 (wycof., powołana w WT)
i kontrolnie PN-EN 12831-1:2017-08; PN-B-03430:1983/Az3:2000 (wycof., wiąże przez WT); PN-B-01706:1992
(wycof., powołana w WT) i kontrolnie PN-EN 806-1…-5; PN-EN 1717:2003 / PN-EN 1717+A1:2026-09;
PN-EN 12056-1…-5:2002; PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10;
PN-EN 14825:2022-11; PN-EN 16147+A1:2023-06; PN-EN 13141-7+A1:2026-05; PN-EN 378-1+A1:2021-03;
wytyczne operatora Aquanet S.A. (zał. C, 2024) z opadem PANDa 2050 i normami opadowymi IMGW 1991–2020.
Metody obliczeniowe bibliotek powołujące normy spoza tabeli A.3 rejestru (np. PN-EN 1264 — ogrzewanie
płaszczyznowe, PN-EN 12828 — naczynia, PN-EN 1253-2 — wpusty) oznaczono w obliczeniach [NZW] — status wydań
do potwierdzenia przed wydaniem do realizacji.

**Materiały wyjściowe:** PZT i PAB (tom I), PT-1 AR (przegrody, U), PT-2 BO (przejścia przez płytę i stropy),
PT-4 IE (zasilanie urządzeń), model `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`,
`wyposazenie.yaml`, dane klimatyczne Poznań (TMY, WMO 12330). Tom jest zgodny z PZT i PAB oraz rozstrzygnięciami
dotyczącymi zamierzenia budowlanego (oświadczenie projektanta).

## Opis instalacji — § 23 pkt 7 RPB

### Źródło ciepła i instalacja ogrzewcza z automatyczną regulacją temperatury — § 23 pkt 7 lit. a RPB; W-150…W-156

**Obciążenie cieplne.** Projektowe obciążenie cieplne budynku Φ_HL = **7,48 kW**
(PN-EN 12831, θ_e = −18 °C, średnia roczna θ_m,e = 7,9 °C; W-150, W-151),
z dodatkiem na c.w.u. Φ_W = 1,25 kW. Temperatury wewnętrzne wg WT § 134 ust. 2 (model
`pomieszczenia[].temp`); garaż nieogrzewany (θ_u = −10,6 °C).

**Źródło ciepła.** Pompa ciepła powietrze–woda typu monoblok na czynniku naturalnym R290 (W-155) —
dane urządzenia przykładowego „PC-R290-07 (przykład)” [DANE PRZYKŁADOWE – FIKCYJNE]: moc grzewcza P(A−7/W35) =
6,2 kW, SCOP (35 °C) = 4,70, η_s = 185 %,
poziom mocy akustycznej L_WA = 57 dB (tryb nocny 52 dB). Układ
monoenergetyczny: punkt biwalentny θ_biv = **−9,6 °C**, grzałka elektryczna
6,0 kW pokrywa 0,04 % rocznego zapotrzebowania (bilans godzinowy
TMY Poznań). Jednostka zewnętrzna: jednostka zewn. PC monoblok R290 w osłonie lamelowej z ekranem akustycznym od tarasu; strefa R290 1,0 m bez otworów, wpustów i studzienek (W-156); odległość od granicy (działka sąsiednia 123/5) **7,60 m** (geometria modelu — ta sama wartość w obliczeniu hałasu i w sprawdzeniu odległości). Skropliny —
studnia chłonna skroplin PC (żwir, ≥ 0,8 m p.p.t.), poza strefą R290 (W-146). Moduł hydrauliczny, zasobnik c.w.u. i bufor —
pomieszczenie techniczne parteru.

**Instalacja ogrzewcza.** Ogrzewanie podłogowe wodne niskotemperaturowe: θ_V = **35 °C**,
Δθ = 5 K, rura 16×2,0 mm (PE-X/PE-RT z barierą
antydyfuzyjną), 27 pętli w 22 pomieszczeniach (długość pętli ≤ 100 m,
Δp pętli ≤ 25 kPa). Rozdzielacze kondygnacyjne: P0: 2 rozdzielacz, 13 pętli, 674 kg/h, Δp_max 14,3 kPa; P1: 1 rozdzielacz, 7 pętli, 297 kg/h, Δp_max 23,6 kPa; P2: 1 rozdzielacz, 7 pętli, 560 kg/h, Δp_max 17,9 kPa.
Uzupełniające ściany grzewcze wodne (model `instalacje.grzejniki`): 1.03 — 80 W, 1.09 — 280 W, 2.05 — 150 W, 2.07 — 180 W, 3.04 — 180 W, 3.06 — 200 W.
Bufor szeregowy 80 dm³ (odszranianie i minimalny czas pracy sprężarki przy zamkniętych
pętlach), naczynie wzbiorcze przeponowe c.o. 18 dm³, zawór bezpieczeństwa
3,0 bar. Przewody PC ↔ budynek: PE-RT/Al/PE-RT 32×3,0, izolacja wewnątrz
30 mm, na zewnątrz 60 mm z płaszczem UV.

**Automatyczna regulacja (§ 23 pkt 7 lit. a–c RPB, WT § 135 ust. 7–10, W-152).** Regulacja pogodowa temperatury
zasilania (krzywa grzewcza sterownika PC, czujnik zewnętrzny) oraz regulacja **oddzielnie w każdym
pomieszczeniu**: termostat pokojowy + siłowniki termoelektryczne na pętlach rozdzielacza (sterownik listwowy
z funkcją sterowania zależną od zapotrzebowania). Pomieszczenia bez stałego pobytu ludzi (komunikacja,
schowki) — regulacja strefowa z pomieszczeniem sąsiednim. Hydrauliczne zrównoważenie pętli — nastawy
przepływu na rozdzielaczach (tabela pętli w obliczeniach).

### Wentylacja mechaniczna nawiewno-wywiewna z odzyskiem ciepła — § 23 pkt 7 lit. d RPB; W-160…W-169

Wentylacja mechaniczna zrównoważona z odzyskiem ciepła (WT § 148 ust. 2 — w pomieszczeniach z wentylacją
mechaniczną bez wentylacji grawitacyjnej; W-160). Strumienie wg PN-83/B-03430/Az3 i WT § 149: nawiew
Σ = **365 m³/h**, wywiew Σ = **365 m³/h** (minimum wywiewu 362 m³/h,
minimum powietrza zewnętrznego 100 m³/h = 20 m³/h × 5 os.); tryb okresowy (kuchnia)
435 m³/h. Nawiew do pokoi, wywiew z kuchni, łazienek, WC, pralni i pomieszczeń bezokiennych;
przepływ powietrza przez podcięcia/kratki drzwi. Bilans: strumienie z modelu (`pomieszczenia[].went`) — sprawdzone: minima, bilans ±10 %, 20 m³/h·os..

**Centrala** (urządzenie przykładowe — lub równoważne; [DANE PRZYKŁADOWE – FIKCYJNE]): Centrala nawiewno-wywiewna z przeciwprądowym wymiennikiem płytowym, wentylatory EC, by-pass 100 %;
wydajność nominalna 450 m³/h (maks. 500 m³/h), sprawność odzysku
η_t = 85 %, SFP = 0,50 kW/(m³/s) (limit WT 1,90),
klasa SEC A (SEC = −40 kWh/(m²·a); (UE) 1253/2014), filtry
ISO ePM1 50 % (nawiew), ISO Coarse 60 % (wywiew), moc wentylatorów 102 W. Lokalizacja: P2 — centrala wentylacyjna 450 m³/h, η_t 85 %, 0,15 m od ściany (króćce ODA/ETA — V3) — na podstawie antywibracyjnej, połączenia elastyczne, tłumiki na 4 króćcach; L w pokojach ≤ wartości PN-B-02151-2 do sprawdzenia w PT-IS (A3 I-8; W-232).
Kanał główny Ø250 mm; przewody powietrza zewnętrznego i wyrzutowego izolowane cieplnie
z paroizolacją (W-168); tłumiki akustyczne na króćcach centrali; skropliny do kanalizacji przez syfon
z zamknięciem wodnym. Czerpnia na wys. 6,9 m, wyrzutnia na wys.
10,0 m (odległości wg WT § 152 — sprawdzenia w obliczeniach).
Garaż — wentylacja naturalna, bez połączenia z centralą (Garaż 1.13: otwory wentylacji naturalnej ≥ 0,04 m²/stanowisko (WT § 108 ust. 1 pkt 1); Garaż 1.13: bez podłączenia do rekuperacji (R6 3.5)).

**Tabela 2. Strumienie powietrza wentylacji mechanicznej**

| Pomieszczenie | Nawiew [m³/h] | Wywiew [m³/h] | Podstawa |
|---|---|---|---|
| 1.03 WC gościnne | 0,00 | 30,00 | wydzielony WC |
| 1.05 Spiżarnia | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| 1.06 Salon + jadalnia + kuchnia | 90,00 | 50,00 | kuchnia z kuchenką elektryczną, > 3 osób |
| 1.09 Łazienka gościnna (natrysk) | 0,00 | 50,00 | łazienka |
| 1.10 Pokój gościnny / gabinet | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 1.12 Pomieszczenie techniczne | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| 2.02 Pokój rodzinny / biblioteka (boks C) | 50,00 | 0,00 | pokój — rozdział nawiewu |
| 2.03 Pokój dziecka 1 | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 2.04 Pokój dziecka 2 | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 2.05 Łazienka dzieci (wanna) | 0,00 | 50,00 | łazienka |
| 2.07 WC z natryskiem | 0,00 | 50,00 | łazienka |
| 2.08 Pralnia z suszarnią | 0,00 | 40,00 | pralnia ≥ 2 h⁻¹ |
| 3.02 Sypialnia rodziców | 60,00 | 0,00 | pokój — rozdział nawiewu |
| 3.04 Łazienka rodziców | 0,00 | 50,00 | łazienka |
| 3.05 Gabinet / pokój gościnny okazjonalny | 45,00 | 0,00 | pokój — rozdział nawiewu |
| 3.07 Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| Razem | 365,00 | 365,00 | bilans ±10 % |

*Źródło: model/budynek.yaml (pomieszczenia[].went); lamela.obliczenia.energia.wentylacja*

### Instalacja wodociągowa wody zimnej i ciepłej — § 23 pkt 7 lit. e RPB; W-130…W-137

Zasilanie z sieci wodociągowej przyłączem (PZT); wodomierz główny **DN25, Q3 = 6,3 m³/h** w pomieszczeniu
technicznym parteru (W-131), za nim filtr, zawór antyskażeniowy EA (PN-EN 1717) i
reduktor ciśnienia (nastawa 400 kPa).
Przybory (23): pralka ×1, prysznic ×3, suszarka ×1, umywalka ×3, umywalka_blat ×2, wanna ×1, wc ×5, wpust_podlogowy ×1, zawor_ogrodowy ×2, zlew ×3, zmywarka ×1. Zapotrzebowanie:
Q_d,śr = 0,60 m³/d, Q_h,max = 0,15 m³/h; przepływ obliczeniowy
q = **1,128 dm³/s** (W-132); wymagane ciśnienie przed wodomierzem p_wym = **329 kPa**
(punkt krytyczny: PRY18 prysznic (c.w.u.)); ciśnienie w punktach czerpalnych 0,05–0,60 MPa (W-130).
Przewody: PE-RT/Al/PE-RT, PE100 (materiał przykładowy — lub równoważny o klasie ciśnienia i temperatury nie niższej;
wyroby w kontakcie z wodą do spożycia — W-137); prowadzenie w bruzdach i przestrzeniach instalacyjnych,
piony w szachcie SI.

**Ciepła woda użytkowa.** Zasobnik c.w.u. **400 dm³** z wężownicą o powierzchni
1,8 m² ogrzewany pompą ciepła (czas ładowania 2,9 h); zapotrzebowanie
V_d = 367 dm³/d (55 °C). Cyrkulacja: czasowa (W-134). Dezynfekcja termiczna
≥ 70 °C w punktach (zasobnik 75 °C, co 7 dni —
526 kWh/a) z termostatycznym zaworem mieszającym (W-133). Grupa bezpieczeństwa
zasobnika, naczynie przeponowe c.w.u. 50 dm³. Izolacja cieplna przewodów c.w.u.,
cyrkulacji i c.o. wg WT zał. 2 pkt 1.5 (W-135).

**Tabela 3. Zabezpieczenia przed przepływem zwrotnym (PN-EN 1717)**

| Miejsce | Kategoria cieczy | Zabezpieczenie | Podstawa |
|---|---|---|---|
| Za wodomierzem głównym (całe przyłącze) | 2 | EA DN25 (zawór antyskażeniowy kontrolowany) | WT §115 ust. 2; PN-EN 1717 tabl. 2–3; wymagania gestora (typ może być podwyższony w warunkach) |
| Zasilanie zasobnika c.w.u. (woda zmieniona temperaturowo) | 2 | EA w grupie bezpieczeństwa + zawór bezpieczeństwa + naczynie przeponowe c.w.u. | PN-EN 1717; PN-B-02440:1976 (powołana w WT, wycof.) |
| Napełnianie/uzupełnianie instalacji c.o. (woda z inhibitorami) | 3 | CA (zawór antyskażeniowy o strefach różnych ciśnień) + odłączany wąż napełniający | PN-EN 1717 — kat. 3 (przy glikolu toksycznym kat. 4 → BA) |
| Zawory ogrodowe (wąż, możliwy kontakt z nawozami) | 3 (4) | HA/HD — zawór ze złączką do węża z zabezpieczeniem; przy dozownikach nawozów kat. 4 → BA / przerwa | PN-EN 1717; R6 §3.6 |
| Pralka, zmywarka | 3 | zabezpieczenie wbudowane w urządzenie (PN-EN 61770) | PN-EN 1717 |
| Instalacja wody deszczowej (jeśli uzupełniana z wodociągu) | 5 | AA/AB — przerwa powietrzna; instalacje rozdzielone (bez połączenia) | WT §126 ust. 3 (W-136) |

*Źródło: lamela.obliczenia.sanitarne.woda*

### Kanalizacja sanitarna — § 23 pkt 7 lit. e RPB; W-138…W-140

Kanalizacja grawitacyjna, system I wg PN-EN 12056-2 (K = 0,5): ΣDU = **20,6 l/s**,
Q_ww = 0,5·√ΣDU = **2,27 l/s** (W-138). Piony: K1 DN100 — wywiewka ponad dach; K2 DN100 — zawór napowietrzający PN-EN 12380 (dozwolony); K3 DN70 — wywiewka ponad dach; wentylacja pionów wg WT § 125 (W-139).
Przewody odpływowe pod posadzką parteru (w płycie fundamentowej — przejścia wg PT-2 BO) do wyjścia z budynku,
przykanalik **DN150 i = 2,0 %** ze studzienką rewizyjną: studzienka rewizyjna z tworzywa PP DN425 z kinetą przelotową, właz żeliwny B125 [ZAŁ], głębokość
1,17 m, 6,2 m od granicy. Rzędne dna (wzgl. ±0,000):
pion K3 −0,99 m; pion K2 −1,29 m; pion K1 −1,42 m; wyjście z budynku −1,48 m; studzienka (dno wlotu) −1,54 m.
Zabezpieczenie przed cofką (WT § 124, W-140): Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy) — spełnione.
Skropliny centrali wentylacyjnej i wpust podłogowy pomieszczenia technicznego — przez syfony z zamknięciem
wodnym (syfon wpustu z zabezpieczeniem przed wyschnięciem). Materiały: rury i kształtki PP-HT wewnątrz,
PVC-U lite SN8 pod posadzką i na przykanaliku (przykładowe — lub równoważne).

### Odprowadzenie i zagospodarowanie wód opadowych, drenaż — § 23 pkt 7 lit. e RPB; W-142…W-146, W-018, W-019

**Odwodnienie dachów** (PN-EN 12056-3, r = 0,046 l/(s·m²); W-142): 9 pól odwadnianych o łącznej
powierzchni **249,0 m²**, Q = **12,51 l/s**:
dachy z attyką (D1, D2, D3, D4) — wpusty dachowe podgrzewane, razem 6 szt.,
i przelewy awaryjne w attykach; płyty okapowe i wspornikowe (PL-E, PL-DA, PL-2, PL-3, PL-D) — rynny
ukryte za blendą czołową (PT-1 AR), wyloty rynien podgrzewane, razem 8 szt., i przelewy (rzygacze)
w blendzie. Dach zielony ekstensywny
(D4 59,1 m²). Rury spustowe wewnętrzne
(szacht SI) i zewnętrzne → kolektory deszczowe PVC-U: kolektor KD-W PVC 160 (RS3, RS4, RS1/RS2 z SI); kolektor KD-E PVC 160 (RS5 dach garażu, RS6 z pom. technicznego); przelew zbiornika DN160 do niecki chłonnej.

**Retencja — wariant bazowy (W-145).** Szczelny zbiornik **5,0 m³** (≤ 5 m³ — nie
jest urządzeniem wodnym) z osadnikiem i filtrem, pompą do podlewania ogrodu (pokrycie zapotrzebowania
na podlewanie 100 %; bilans IMGW 1991–2020) i przelewem do niecki chłonnej
(ogród deszczowy). Powierzchnia zredukowana zlewni A_red = 210,0 m²; wymagana objętość niecki
(PANDa 2050, C = 10 lat, f_b = 1,2; W-143) V_min = **5,08 m³**. Niecka przyjęta
— model (dzialka.yaml: retencja.rozsaczanie): A_n = **28,0 m²**, głębokość
0,30 m, V = **8,40 m³** ≥ V_min (minimalna powierzchnia
z doboru 19,5 m²) — czas opróżniania 1,0 h (≤ 24 h). Deszczówka — instalacja odrębna, bez połączenia z wodociągiem (W-136).
Odwodnienia liniowe przy drzwiach bez progu i przed bramą garażu (16 korytek
wg obliczeń); woda z podjazdu i garażu przez osadnik z separatorem — nie do zbiornika retencyjnego.
Skrzynki rozsączające — wyłącznie wariant opcjonalny po stanowisku PGW Wody Polskie (D-05).

**Drenaż opaskowy: NIEWYMAGANY** (W1.1-E (wilgoć gruntowa, woda nienaporowa)).
Grunt: piaski średnie, k_f = 3,00·10⁻⁴ m/s (wartość typowa [W]; wymagane badania — E-04) Zwierciadło wody gruntowej 3,80 m p.p.t.; spód fundamentu −1,05 m (wzgl. ±0,00), teren przy budynku średnio −0,29 m → głębokość posadowienia 0,76 m; ZWG 3,04 m poniżej spodu fundamentu. Pomieszczenia poniżej terenu: brak (budynek niepodpiwniczony, posadzka parteru nad terenem) Grunt silnie przepuszczalny (k_f > 10⁻⁴ m/s) i ZWG ≥ 0,5 m pod fundamentem — woda opadowa infiltruje pionowo, nie powstaje woda zastoiskowa przy ścianach; wystarcza izolacja przeciwwilgociowa. Zalecenia: Odwodnienie powierzchniowe: profilowanie terenu ze spadkiem ≥ 2 % od budynku na pasie ≥ 2,0 m (rzędne projektowane w dzialka.yaml: teren.punkty_projektowane) — wymagane niezależnie od drenażu. Opaska żwirowa szer. 0,5 m wokół budynku (żwir płukany 16/32 mm na geowłókninie, obrzeże), spadek od ściany; chroni cokół przed rozbryzgiem i ułatwia kontrolę izolacji [W].

## Powiązania instalacji z sieciami zewnętrznymi i punkty pomiarowe — § 23 pkt 8 RPB

**Tabela 4. Powiązania z sieciami i odbiornikami zewnętrznymi (dane działki — [DANE PRZYKŁADOWE – FIKCYJNE])**

| Medium | Sieć zewnętrzna / odbiornik | Przyłącze / przewód | Długość [m] |
|---|---|---|---|
| woda | wodociąg PE 110 (ul. Lipowa) | przyłącze PE 40, przykrycie ≥ 1,20 m (W-141), pod podjazdem i płytą garażu w rurze osłonowej, wodomierz w pom. 1.12 | 18,80 |
| ścieki bytowe | kanalizacja sanitarna PVC 200, dno ≈ 99,20 | przykanalik PVC-U 160, i ≥ 2 %, studzienka rewizyjna SR1 Ø425 (x 13,0; y 43,8) — wyjście z płyty pod ścianą pn. (piony K1, K2) | 13,90 |
| wody opadowe | zagospodarowanie na działce (retencja) | kolektor KD-W PVC 160 (RS3, RS4, RS1/RS2 z SI) | 34,80 |
| wody opadowe | zagospodarowanie na działce (retencja) | kolektor KD-E PVC 160 (RS5 dach garażu, RS6 z pom. technicznego) | 31,60 |
| wody opadowe | zagospodarowanie na działce (retencja) | przelew zbiornika DN160 do niecki chłonnej | 6,20 |
| wody opadowe | zagospodarowanie na działce (retencja) | OL-1 (i OL-4 kanałem wzdłuż podjazdu) → separator SEP-1 → niecka NT-E (PVC 160) | 3,30 |
| wody opadowe | zagospodarowanie na działce (retencja) | RS7 (rynny zach. PL-E i PL-2) → KD-W, PVC 110 | 3,20 |
| wody opadowe | zagospodarowanie na działce (retencja) | RS8 (rynny PL-E pd. i PL-D) + OL-6 (próg DZ3) → KD-E, PVC 110 | 4,10 |
| wody opadowe | zagospodarowanie na działce (retencja) | OL-7 / OL-7a (próg bramy, filarki, wnęka wejścia) → separator SEP-1, PVC 110 (wydanie, V1-02) | 2,30 |
| wody opadowe | zagospodarowanie na działce (retencja) | OL-5 (próg DZ2 garażu) → KD-E, PVC 110 (woda czysta z podestu — nie z posadzki garażu) | 0,80 |

*Źródło: model/dzialka.yaml — uzbrojenie istniejące i projektowane*

**Punkty pomiarowe:** wodomierz główny DN25, Q3 = 6,3 m³/h (odczyt gestora sieci; W-131); licznik
energii elektrycznej w ZKP (PT-4 IE) — pompa ciepła i grzałka zasilane z instalacji budynku (moce elektryczne
— rozdział „Charakterystyka energetyczna”, bilans mocy). Sieć gazowa: gazociąg PE 63 — NIE wykorzystywany (dom all-electric) —
budynek bez przyłącza gazowego. Sieć ciepłownicza — brak (oświadczenie projektanta instalacyjnego w ZL; W-158).
Parametry sieci (ciśnienie dyspozycyjne i maksymalne, rzędna kanału) przyjęto jako założenia [ZAŁ] — do
potwierdzenia w warunkach przyłączenia gestorów sieci (D-23): ciśnienie dyspozycyjne
0,35 MPa, maksymalne 0,60 MPa.

## Założenia, obliczenia i dobór urządzeń — § 23 pkt 8 lit. a–b RPB

### Parametry klimatu zewnętrznego i wewnętrznego — § 23 pkt 8 lit. a RPB; W-150, W-161

Klimat zewnętrzny: θ_e = −18 °C (strefa II, W-150), θ_m,e = 7,9 °C; dane
godzinowe TMY Poznań (WMO 12330) do bilansu pompy ciepła i charakterystyki energetycznej. Klimat wewnętrzny
(WT § 134 ust. 2; model `pomieszczenia[].temp`): **16 °C** — 6 pomieszczeń: 1.01, 1.05, 1.15, 1.16, 1.12, 3.07; **20 °C** — 22 pomieszczeń: 1.02, 1.03, 1.04, 1.06, 1.07, 1.08, 1.10, 1.11, 2.01, 2.02, 2.03, 2.04, 2.06, 2.08, 3.01, 3.02, 3.03, 3.05, 3.06, 1.14, 2.09, 3.08; **24 °C** — 1.09 Łazienka gościnna (natrysk), 2.05 Łazienka dzieci (wanna), 2.07 WC z natryskiem, 3.04 Łazienka rodziców. Powietrze zewnętrzne ≥ 20 m³/h na osobę
(5 os.), wywiew wg PN-83/B-03430/Az3 (W-161, W-162). Szczelność budynku n50 = 1,0 h⁻¹ [ZAŁ]
(cel projektowy — potwierdzić próbą ciśnieniową, W-249); sprawność odzysku ciepła η_v = 0,85.

### Zestawienie wyników i dobór urządzeń — § 23 pkt 8 lit. b RPB

**Podstawowe wyniki** (tabela w PDF):

* Projektowe obciążenie cieplne budynku Φ_HL: 7,48 kW (—; PN-EN 12831 [W-151])
* Pompa ciepła PC-R290-07 (przykład): moc P(A−7/W35): 6,2 kW (—; [DANE PRZYKŁADOWE – FIKCYJNE])
* Pokrycie mocy przy θ_e: P_PC + P_grzałki ≥ Φ_HL + Φ_W: 10,55 kW (≥ 8,73 kW; PN-EN 12831 / VDI 4645 [W] [W-155])
* Punkt biwalentny: −9,6 °C (≤ −7,0 °C; VDI 4645 / praktyka [ZAŁ] [W-155])
* Udział grzałki w pokryciu Q_H: 0,0004  (≤ 0,0500; [ZAŁ] [W-155])
* Sezonowa efektywność η_s (35 °C): 1,85  (≥ 1,25; rozp. (UE) 813/2013 zał. II [W-155])
* Moc nominalna PC (R290 — rozp. (UE) 2024/573): 7,4 kW (≤ 12,0 kW; rozp. (UE) 2024/573 zał. IV pkt 8 lit. b [W-155])
* Temperatura zasilania ogrzewania podłogowego: 35 °C (≤ 35 °C; W-153: R6 3.4 [zalozenie] [W-153])
* Bufor c.o. / naczynie wzbiorcze c.o.: 80 / 18 dm³ (—; obliczenia (rozdz. Ogrzewanie))
* Poziom mocy akustycznej jednostki zewn.: 57 dB(A) (≤ 70 dB(A); rozp. (UE) 813/2013 zał. II pkt 3 [W-155])
* Hałas PC w nocy na granicy (działka sąsiednia 123/5): 26,4 dB(A) (≤ 40,0 dB(A); Dz.U. 2014 poz. 112 tab. 1 lp. 2a (L_Aeq,N) [W-024])
* Hałas PC w dzień na granicy (działka sąsiednia 123/5): 31,4 dB(A) (≤ 50,0 dB(A); Dz.U. 2014 poz. 112 (L_Aeq,D) [W-024])
* Odległość jednostki PC od granicy z działką sąsiednią (MN): 7,6 m (≥ 6,0 m; W-024 (dla LAMELA: granica E) [ZAŁ] [W-024])
* Strefa bezpieczeństwa R290 (1,0 m + wymiar urządzenia ≈ 0,4 m): otwory w strefie: 0 szt. (= 0 szt.; PN-EN 378-1; DTR (W-156) — brak [W-156])
* Wentylacja: nawiew / wywiew: 365 / 365 m³/h (≥ 100 / ≥ 362; WT § 149 [W-161, W-162])
* Centrala: wydajność maks. ≥ strumień okresowy: 500 m³/h (≥ 435 m³/h; PN-83/B-03430/Az3)
* SFP nawiewu / wywiewu [kW/(m³/s)]: 0,50 / 0,50  (≤ 1,90 / ≤ 1,30; WT § 154 ust. 10–11 [W-164])
* Przepływ obliczeniowy ≤ Q3 wodomierza: 4,06 m³/h (≤ 6,30 m³/h; PN-EN ISO 4064 / MID [W-131])
* Wymagane ciśnienie w sieci ≤ ciśnienie dyspozycyjne: 0,329 MPa (≤ 0,350 MPa; warunki gestora [ZAŁ p_dysp] [W-130])
* Ciśnienie statyczne w punkcie ≤ 0,60 MPa (WT §114): 0,40 MPa (≤ 0,60 MPa; WT §114 ust. 1 [W-130])
* Pojemność zasobnika ≥ minimalna: 400 dm³ (≥ 367 dm³;  [W-133])
* Temperatura dezynfekcji w punktach: 70 °C (w zakresie 70–80 °C; WT §120 ust. 2a [W-133])
* Kanalizacja: ΣDU / Q_ww: 20,6 / 2,27 l/s (—; PN-EN 12056-2 [W-138])
* Przykanalik: napełnienie h/d: 0,21  (≤ 0,70; PN-EN 12056-2 zał. B (tabl. B.2) [W-138])
* Przykanalik: prędkość przy Q_ww (samooczyszczanie): 0,83 m/s (≥ 0,70 m/s; praktyka [ZAŁ] — informacyjnie przy małych Q (spłukiwanie miską ustępową) [W-138])
* Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy): 0,00 m (> −0,31 m; WT §124; PN-EN 12056-1 — inaczej zamknięcie przeciwzalewowe PN-EN 13564-1 lub przepompownia PN-EN 12056-4 [W-140])
* Dachy: A / Q (r = 0,046 l/(s·m²)): 249,0 m² / 12,51 l/s  (—; PN-EN 12056-3 [W-142])
* Pojemność szczelnego zbiornika (bez zgłoszenia): 5,0 m³ (≤ 5,0 m³; W-145: PB art. 29 ust. 2 pkt 36 (5–15 m³ — zgłoszenie, ust. 1 pkt 38) [W-145])
* Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia): 8,40 m³ (≥ 5,08 m³; Aquanet 2024 wzór (1), f_b [W-143])
* Niecka: czas opróżniania: 1,0 h (≤ 24,0 h; W-143: Aquanet 2024 zał. C [zalozenie] [W-143])

### Obliczenia: obciążenie cieplne pomieszczeń i budynku — PN-EN 12831; W-150, W-151

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.energia.obciazenie_cieplne]*

### Obliczenia: pompa ciepła, ogrzewanie podłogowe, bufor, naczynia, hałas — W-152…W-156, W-024

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.sanitarne.ogrzewanie]*

### Obliczenia: wentylacja — bilans powietrza i dobór centrali — W-160…W-169

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.energia.wentylacja]*

### Obliczenia: instalacja wodociągowa i c.w.u. — W-130…W-137

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.sanitarne.woda]*

### Obliczenia: kanalizacja sanitarna — W-138…W-141

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.sanitarne.kanalizacja]*

### Obliczenia: wody opadowe, retencja (IMGW, PANDa) — PN-EN 12056-3; W-142…W-146

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.sanitarne.deszczowa]*

### Obliczenia: drenaż i odwodnienie powierzchniowe — W-019

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.sanitarne.drenaz]*

## Charakterystyka energetyczna budynku — § 23 pkt 11 RPB; W-240…W-251

Charakterystykę energetyczną opracowano wg metodologii (Dz.U. 2015 poz. 376 ze zm., ost. 2023 poz. 697; W-241)
dla A_f = 262,4 m² (bez garażu nieogrzewanego), metodą miesięczną z danymi klimatycznymi Poznań.
Wariant projektowy **A** obejmuje instalację fotowoltaiczną (projektowaną w PT-4 IE); ponieważ energia z PV
liczona jest tylko w części autokonsumowanej, a instalacja PV może nie zostać wykonana razem z budynkiem,
**wariant A0 bez PV podano jawnie** — oba warianty sprawdzono względem EP_max. EP policzono dla urządzeń
zaprojektowanych w tym tomie — pompy ciepła PC-R290-07 (przykład) (dobór w obliczeniach ogrzewania) i zasobnika
c.w.u. 400 dm³ z dezynfekcją termiczną (obliczenia wody); dane liczbowe tych
urządzeń (SCOP, COP_cwu, strata postojowa), centrali (η_t, SFP) i moce pomocnicze są danymi wyrobów
przykładowych [DANE PRZYKŁADOWE – FIKCYJNE] — po wyborze wyrobów zastąpić danymi deklarowanymi (W-242), a generator tomu
przeliczy EP, punkt biwalentny i hałas.

### Bilans mocy urządzeń elektrycznych i zużywających inne rodzaje energii — § 23 pkt 11 lit. a RPB

**Tabela 5. Bilans mocy — odbiorniki ≥ 0,5 kW (instalacje stałe budynku)**

| Odbiornik | Grupa | P [kW] | Faz |
|---|---|---|---|
| Oświetlenie P0 | oswietlenie | 0,56 | 1 |
| Gniazda P0: 1.10 Pokój gościnny / gabinet, 1.08 Przedpokój gościnny, 1.14 Szacht instalacyjny SI, 1.04 Klatka schodowa, 1.16 Schowek pod spocznikiem (h < 1,40), 1.07 Pas komunikacyjny przy schodach, 1.05 Spiżarnia, 1.15 Schowek pod schodami (h 1,40–2,20), 1.02 Hol, 1.01 Wiatrołap, 1.11 Przedsionek gospodarczy | gniazda | 2,00 | 1 |
| Gniazda P1: 2.04 Pokój dziecka 2, 2.03 Pokój dziecka 1, 2.09 Szacht instalacyjny SI, 2.01 Hol, 2.06 Klatka schodowa | gniazda | 2,00 | 1 |
| Gniazda P1: 2.02 Pokój rodzinny / biblioteka (boks C) | gniazda | 2,00 | 1 |
| Gniazda P2: 3.02 Sypialnia rodziców, 3.03 Garderoba (przedpokój apartamentu), 3.08 Szacht instalacyjny SI, 3.06 Klatka schodowa (wyjście z biegu 2, pustka), 3.01 Hol | gniazda | 2,00 | 1 |
| Gniazda P2: 3.05 Gabinet / pokój gościnny okazjonalny | gniazda | 2,00 | 1 |
| Gniazda kuchenne 1 (1.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 |
| Gniazda kuchenne 2 (1.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 |
| Gniazda łazienki (1.03 WC gościnne) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (1.09 Łazienka gościnna (natrysk)) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (2.05 Łazienka dzieci (wanna)) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (2.07 WC z natryskiem) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (3.04 Łazienka rodziców) | gniazda_lazienka | 2,00 | 1 |
| Gniazda garażu / pom. technicznego (IP44) | gniazda | 2,00 | 1 |
| Gniazda zewnętrzne (taras, ogród; IP44/IP54) | zewn | 2,00 | 1 |
| Płyta indukcyjna | gotowanie | 7,40 | 3 |
| Piekarnik | gotowanie | 3,50 | 1 |
| Zmywarka | agd | 2,20 | 1 |
| Pralka | agd | 2,20 | 1 |
| Suszarka | agd | 2,50 | 1 |
| Pompa ciepła — jednostka zewnętrzna (PC-R290-07 (przykład)) | pc | 2,67 | 1 |
| Grzałka rezerwowa PC / zasobnika c.w.u. (6,0 kW) | grzalka | 6,00 | 3 |
| Ładowarka EV 11 kW (3f) — garaż; przewód na 22 kW | ev | 11,00 | 3 |
| Brama wjazdowa, furtka, wideodomofon (linia ogrodzenia) | napedy | 0,50 | 1 |
| Pompa zbiornika wody deszczowej (podlewanie) | pompa | 0,80 | 1 |
| Napędy osłon przeciwsłonecznych (19 szt.) | napedy | 1,90 | 1 |
| Moc zainstalowana (wszystkie odbiorniki) |  | 71,34 |  |
| Moc szczytowa z układem ograniczania mocy (DLM) |  | 24,85 |  |

Moc przyłączeniowa 27 kW, zabezpieczenie przedlicznikowe 40 A — PT-4 IE. Budynek nie ma urządzeń zużywających paliwa (gaz, olej, biomasa) ani urządzeń technologicznych.

*Źródło: lamela.obliczenia.elektryka.bilans (odczyt; obliczenia PT-4 IE)*

### Właściwości cieplne przegród zewnętrznych — § 23 pkt 11 lit. b RPB; W-243, W-244

**Tabela 6. Współczynniki przenikania ciepła przegród i stolarki obudowy (szczegóły — PT-1 AR)**

| Przegroda | Rodzaj | U [W/(m²·K)] | U_max [W/(m²·K)] | Spełnia |
|---|---|---|---|---|
| DZ1 | dach | 0,13 | 0,15 | tak |
| SD1 | dach | 0,11 | 0,15 | tak |
| SD2 | dach | 0,12 | 0,15 | tak |
| POD-0 | podloga grunt | 0,11 | 0,30 | tak |
| SWG | sciana nieogrz | 0,27 | 0,30 | tak |
| SZ1 | sciana zewn | 0,17 | 0,20 | tak |
| SZ2 | sciana zewn | 0,18 | 0,20 | tak |
| SZL | sciana zewn | 0,11 | 0,20 | tak |
| ST2Z | strop zewn | 0,14 | 0,15 | tak |
| BC1 | okno (okno) | 0,78 | 0,90 | tak |
| DG1 | drzwi (drzwi) | 1,10 | 1,30 | tak |
| DZ1 | drzwi (drzwi_zewn) | 0,90 | 1,30 | tak |
| DZ3 | drzwi (drzwi_zewn) | 1,00 | 1,30 | tak |
| FX1 | okno (fix) | 0,64 | 0,90 | tak |
| FX2 | okno (fix) | 0,61 | 0,90 | tak |
| FX3 | okno (fix) | 0,87 | 0,90 | tak |
| HS1 | okno (drzwi_przesuwne_HS) | 0,84 | 0,90 | tak |
| HS2 | okno (drzwi_przesuwne_HS) | 0,82 | 0,90 | tak |
| OE1 | okno (okno) | 0,75 | 0,90 | tak |
| ON1 | okno (okno) | 0,89 | 0,90 | tak |
| ON2 | okno (okno) | 0,88 | 0,90 | tak |
| ON3 | okno (okno) | 0,86 | 0,90 | tak |
| ON4 | okno (okno) | 0,82 | 0,90 | tak |
| OP1 | okno (okno) | 0,71 | 0,90 | tak |
| OP2 | okno (okno) | 0,77 | 0,90 | tak |
| OP3 | okno (okno) | 0,74 | 0,90 | tak |
| OZ1 | okno (okno) | 0,81 | 0,90 | tak |

Stolarka — największe U_w/U_D danego symbolu (wymiary z modelu). Mostki cieplne: H_TB = 32,0 W/K (Ψ z symulacji PN-EN ISO 10211 — projekt/08_obliczenia/mostki); U podłogi na gruncie wg PN-EN ISO 13370.

*Źródło: lamela.obliczenia.energia.obudowa; WT zał. 2 pkt 1.1–1.2*

### Parametry sprawności energetycznej instalacji — § 23 pkt 11 lit. c RPB

**Tabela 7. Sprawności cząstkowe systemów (wariant projektowy A)**

| Instalacja | Wytwarzanie η_g | Akumulacja η_s | Przesył η_d | Regulacja η_e | Łącznie η_tot |
|---|---|---|---|---|---|
| Ogrzewanie | 4,09 | 1,00 | 0,96 | 0,89 | 3,49 |
| Ciepła woda użytkowa | 3,20 | 0,91 | 0,60 | — | 1,74 |

Źródło ogrzewania: SCOP = 4,09 (PN-EN 14825, PC-R290-07 (przykład) — dobór w module ogrzewania; do EP min(SCOP deklarowany 4,70; SCOP z bilansu godzinowego TMY 4,09)); η_H,e = 0,89 (tab. 3 lp. 6b), η_H,d = 0,96 (tab. 6 lp. 3a), η_H,s = 1,00 (tab. 8 lp. 3)

C.w.u.: COP_cwu = 3,20 (PN-EN 16147); η_W,s = 0,906 (zasobnik 400 dm³, strata postojowa 75 W); η_W,d = 0,60 (bez cyrkulacji w EP — `energia.cwu.cyrkulacja` modelu; wartość zachowawcza)

Wentylacja: odzysk ciepła η_oc = 0,85; pomocnicze: pompa obiegowa ogrzewania podłogowego (EC) 25 W; sterownik/grzałka tacy PC (poza SCOP) 15 W; wentylatory centrali (P = SFP·q) 102 W

Pompa ciepła w EP — urządzenie z projektu (PC-R290-07 (przykład), moduł ogrzewania): η_H,g = SCOP = 4,09 = min(SCOP₃₅ deklarowany 4,70; SCOP z bilansu godzinowego TMY 4,09) — wartość ostrożna; udział grzałki 0,04 % (ten sam bilans godzinowy).

Zasobnik c.w.u. w EP — z projektu (moduł wody): V = 400 dm³, strata postojowa 75 W (strata postojowa ≤ 75 W — przeskalowana z danych przykładowych 250 dm³ / 55 W wg V^(2/3) [ZAŁ]; wymaganie dla wyrobu); dezynfekcja termiczna 526 kWh/rok (moduł wody: co 7 dni, zasobnik 400 dm³ do 75 °C + pętla) — energia elektryczna grzałki doliczona do c.w.u.

*Źródło: lamela.obliczenia.energia.ep — metodologia tab. 2, 3, 6, 8, 12, 14*

### Wskaźniki EP, EK, EU, udział OZE — spełnienie wymagań — § 23 pkt 11 lit. d RPB; WT § 328–329 (W-240)

**Tabela 8. Charakterystyka energetyczna — wariant projektowy, wariant bez PV, alternatywy i wrażliwość [kWh/(m²·rok)]**

| Wariant | EU | EK | EP | EP_max | U_OZE [%] | E_CO2 [t/rok] | EP ≤ EP_max |
|---|---|---|---|---|---|---|---|
| A: PC R290 + PV + rekuperacja | 41,64 | 25,21 | 40,32 | 70,00 | 73,96 | 2,34 | tak |
| A0: PC R290 + rekuperacja, bez PV | 41,64 | 25,21 | 63,02 | 70,00 | 58,30 | 3,66 | tak |
| B: kocioł gazowy kondensacyjny + rekuperacja | 41,64 | 71,13 | 88,90 | 70,00 | 0,00 | 4,47 | NIE |
| C: PC — wartości domyślne metodologii, bez PV | 41,64 | 32,86 | 82,15 | 70,00 | 47,91 | 4,77 | NIE |
| A (n50 = 4 h⁻¹ — brak próby szczelności) | 55,67 | 29,29 | 49,79 | 70,00 | 74,09 | 2,89 | tak |

A — wariant projektowy (z PV); A0 — ten sam budynek i instalacje bez PV; B, C — analiza alternatyw (RPB § 20 ust. 1 pkt 10, PAB); ostatnie wiersze — wrażliwość (szczelność, Ψ).

*Źródło: lamela.obliczenia.energia.ep (metodologia Dz.U. 2015 poz. 376 ze zm.)*

> Wariant projektowy A: EP = **40,3** kWh/(m²·rok) ≤ EP_max = 70,0 — wymaganie spełnione. Wariant A0 bez PV: EP = **63,0** kWh/(m²·rok) ≤ EP_max — wymaganie spełnione także bez instalacji PV.

### Obliczenia: charakterystyka energetyczna — wariant A — W-240…W-242

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.energia.ep]*

Dane do świadectwa charakterystyki energetycznej (centralny rejestr) przekazuje się po zakończeniu budowy na podstawie wyrobów wbudowanych i wyniku próby szczelności (W-251; PB art. 57 ust. 1 pkt 6a).

## Dane dotyczące warunków ochrony przeciwpożarowej — § 23 pkt 10 RPB

Budynek mieszkalny jednorodzinny: kategoria zagrożenia ludzi **ZL IV** (WT §209 ust. 2 pkt 4), grupa wysokości
**N** (WT §8 pkt 1), 3 kondygnacje nadziemne — zwolniony
z wymagań klasy odporności pożarowej (WT §213 pkt 1 lit. a; W-211). W zakresie PT-3 IS:

* izolacje cieplne i akustyczne instalacji wodociągowej, kanalizacyjnej i ogrzewczej wykonać w sposób
  zapewniający **nierozprzestrzenianie ognia** (WT § 267 ust. 8; W-215): otuliny przewodów wody zimnej,
  c.w.u., cyrkulacji i c.o. (także przewodów PC ↔ budynek wewnątrz budynku), izolacja akustyczna pionów
  kanalizacyjnych i rur spustowych w szachcie. Zwolnienie z § 213 WT obejmuje tylko wymagania § 212 i § 216,
  więc tego wymagania nie znosi;
* przejścia instalacji przez stropy i ściany — przepusty bez wymaganej klasy odporności ogniowej (EI), bo
  elementy budynku nie mają wymaganej klasy odporności ogniowej (zwolnienie jw.); przejścia uszczelnić
  akustycznie i szczelnie powietrznie (W-249) materiałami nierozprzestrzeniającymi ognia. Uwaga na arkuszach PT-IS-03, PT-IS-04, PT-IS-05 „… ppoż. wg klasy stropu” oznacza w tym budynku: stropy nie mają wymaganej klasy odporności ogniowej, więc przepusty ogniochronne (opaski, kołnierze) nie są wymagane; obowiązuje uszczelnienie jak wyżej.
* przewody wentylacyjne z materiałów palnych dopuszczalne w budynku jednorodzinnym jednolokalowym (W-168);
  centrala w wydzielonym pomieszczeniu technicznym;
* pompa ciepła z czynnikiem palnym R290 (klasa A3 wg PN-EN 378-1+A1:2021-03): jednostka zewnętrzna poza
  budynkiem, strefa bezpieczeństwa wg DTR (typowo 1,0 m) wolna od otworów, wpustów, studzienek i źródeł
  zapłonu (W-156) — sprawdzenie w obliczeniach ogrzewania; instalacja wewnętrzna wyłącznie wodna (monoblok);
* brak instalacji gazowej i urządzeń spalania paliw — nie występują przewody spalinowe;
* zaopatrzenie w wodę do zewnętrznego gaszenia pożaru: najbliższy hydrant zewnętrzny DN80 (ul. Lipowa) — zaopatrzenie ppoż. (W-217) [do potwierdzenia] [DANE PRZYKŁADOWE – FIKCYJNE] (dane PZT) — instalacja
  wodociągowa budynku nie pełni funkcji przeciwpożarowej (brak hydrantów wewnętrznych — nie wymagane).

## Zasadnicze urządzenia — parametry wymagane — § 23 pkt 9 RPB; PB art. 10

Urządzenia określono **parametrami wymaganymi**. Wyroby przywołane w obliczeniach są przykładowe — dopuszcza
się wyroby równoważne o parametrach nie gorszych, wprowadzone do obrotu zgodnie z PB art. 10 (deklaracja
właściwości użytkowych / deklaracja zgodności, oznakowanie CE lub znak budowlany B). Zamiana wyrobu wymaga
ponownego przeliczenia EP, punktu biwalentnego i hałasu (generator tomu przelicza je z modelu).

**Tabela 9. Zasadnicze urządzenia instalacji sanitarnych**

| Urządzenie | Parametry wymagane | Podstawa |
|---|---|---|
| Pompa ciepła powietrze–woda, monoblok | czynnik naturalny R290 (GWP < 150); P(A−15/W35) ≥ 5,0 kW (jak urządzenie przyjęte w obliczeniach) i pokrycie Φ_HL + Φ_W = 8,73 kW przy θ_e z grzałką ≤ 6 kW; SCOP₃₅ ≥ 4,7; η_s ≥ 125 %; L_WA ≤ 57 dB (tryb nocny niżej); regulacja pogodowa, sterowanie zależne od zapotrzebowania | W-155, W-156, W-024; (UE) 2024/573, 813/2013 |
| Zasobnik c.w.u. z wężownicą | V ≥ 400 dm³, wężownica ≥ 1,8 m² (dla PC), strata postojowa ≤ 75 W (wartość przyjęta w EP), grzałka do dezynfekcji, grupa bezpieczeństwa, izolacja fabryczna | W-133, W-134; PN-EN 16147+A1:2023-06 |
| Bufor c.o. (szeregowy) | V ≥ 80 dm³, izolowany | obliczenia ogrzewania |
| Naczynia wzbiorcze przeponowe | c.o. ≥ 18 dm³ (p₀ 0,83 bar); c.w.u. ≥ 50 dm³ (p₀ 3,8 bar), przepływowe | PN-B-02414:1999 (powołana w WT) [W-154] |
| Rozdzielacze ogrzewania podłogowego | P0: 13 obwodów, przepływomierze, siłowniki 230 V/24 V NC; P1: 7 obwodów, przepływomierze, siłowniki 230 V/24 V NC; P2: 7 obwodów, przepływomierze, siłowniki 230 V/24 V NC | W-152, W-154 |
| Centrala wentylacyjna z odzyskiem ciepła | V_max ≥ 435 m³/h przy sprężu instalacji; η_t ≥ 85 %; SFP ≤ 1,90 kW/(m³/s); SEC klasa ≥ A; by-pass 100 %; filtry ISO ePM1 50 % (nawiew), ISO Coarse (wywiew); L_WA wg PN-B-02151-2 w pokojach | W-160…W-169; (UE) 1253/2014; PN-EN 13141-7+A1:2026-05 |
| Zestaw wodomierzowy | wodomierz DN25, Q3 = 6,3 m³/h (lub wg warunków gestora), zawory, filtr, EA; reduktor ciśnienia wymagany | W-131, W-130; PN-EN 1717 |
| Zbiornik retencyjny wód opadowych | szczelny, V = 5,0 m³ (≤ 5 m³), osadnik, filtr, pompa zatapialna do podlewania, przelew do niecki, właz z zabezpieczeniem | W-145; PW art. 16 pkt 65 lit. f |

Dane liczbowe urządzeń przykładowych: [DANE PRZYKŁADOWE – FIKCYJNE].

*Źródło: model (instalacje.yaml, wyposazenie.yaml, dzialka.yaml); lamela.obliczenia*

## Próby, badania i odbiory — PB art. 57 ust. 1; C.3 rejestru

Roboty wykonywać zgodnie z PT, instrukcjami producentów wyrobów i zasadami wiedzy technicznej; odbiory
częściowe przed zakryciem (przewody w posadzkach, bruzdach, pod płytą) z wpisem do dziennika budowy.

1. **Instalacja wodociągowa** — próba szczelności przed zakryciem przewodów (kontrolnie PN-EN 806-4;
   ciśnienie próbne wg instrukcji systemu rur, nie niższe niż 1,5 × ciśnienie robocze); płukanie
   i dezynfekcja; badanie jakości wody przed oddaniem do użytkowania; protokół nastawy reduktora
   i sprawdzenia zaworu EA (PN-EN 1717).
2. **Kanalizacja sanitarna** — próba szczelności przewodów pod posadzką i przykanalika przed zasypaniem
   (PN-EN 1610:2015-10), sprawdzenie spadków i rzędnych (inwentaryzacja geodezyjna przyłącza),
   próba drożności pionów i działania zaworów napowietrzających.
3. **Ogrzewanie podłogowe** — próba ciśnieniowa pętli przed wylaniem jastrychu (instalacja pod ciśnieniem
   w trakcie wylewania), wygrzewanie jastrychu wg protokołu, regulacja hydrauliczna (nastawy przepływów
   rozdzielaczy wg tabeli pętli), sprawdzenie działania termostatów i siłowników w każdym pomieszczeniu.
4. **Pompa ciepła** — montaż i uruchomienie przez serwis upoważniony przez producenta (czynnik R290),
   sprawdzenie strefy bezpieczeństwa, odprowadzenia skroplin i zabezpieczenia przed zamarzaniem; protokół
   uruchomienia z nastawami krzywej grzewczej i programu dezynfekcji c.w.u.
5. **Wentylacja mechaniczna** — sprawdzenie szczelności i czystości przewodów, pomiar i regulacja
   strumieni powietrza na nawiewnikach i wywiewnikach (tolerancja ±10 % wartości projektowych — tabela
   strumieni), pomiar poziomu dźwięku w pokojach (PN-B-02151-2:2018-01), protokół regulacji.
6. **Wody opadowe** — próba szczelności zbiornika i przewodów deszczowych, sprawdzenie przelewów awaryjnych
   dachów, działania niecki (czas opróżniania) i odwodnień liniowych.
7. **Szczelność budynku** — próba ciśnieniowa n50 (PN-EN ISO 9972) przed wykończeniem; wynik warunkuje
   przyjętą wartość n50 = 1,0 h⁻¹ w charakterystyce energetycznej (W-249).
8. **Dokumentacja odbiorowa** — protokoły prób i badań, DWU/deklaracje wbudowanych wyrobów, DTR i karty
   gwarancyjne urządzeń, instrukcja obsługi instalacji dla użytkownika, dokumentacja powykonawcza (PT
   z naniesionymi zmianami), dane do świadectwa charakterystyki energetycznej (C.3 rejestru).

## Dane do uzupełnienia i uzgodnienia międzybranżowe — rejestr wymagań, sekcje D i E

Uzgodnienia: PT-1 AR (przejścia przez przegrody, szachty, wyłaz), PT-2 BO (przejścia przez płytę fundamentową i stropy, podstawy urządzeń), PT-4 IE (zasilanie PC, grzałki, centrali, sterowników; połączenia wyrównawcze rur metalowych). Braki modelu zgłoszone przez generator rysunków IS (`projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md`, stan z dnia generowania rysunków):

**Tabela 10. Braki danych modelu — rysunki IS**

| Lp. | Element | Brak / stan w modelu | Arkusze |
|---|---|---|---|
| 1 | Pion/szacht wentylacyjny (SUP, ETA) | brak w modelu szachtu wentylacyjnego (szacht SI zajęty przez piony wod.-kan. i deszczowe) — przyjęto lokalizację proponowaną algorytmicznie | PT-IS-08, PT-IS-09 |
| 2 | Piony c.o. (zasilanie rozdzielaczy P1, P2) | brak tras pionów c.o. w instalacje.yaml — przyjęto pion proponowany przy rozdzielaczu R-P1 | PT-IS-06, PT-IS-07 |
| 3 | Trasy przewodów (woda, kanalizacja, c.o., wentylacja) | model nie zawiera przebiegów przewodów — trasy wyznaczono algorytmicznie (ortogonalnie, przy ścianach, z pionów/rozdzielaczy do przyborów) | PT-IS-01…09 |
| 4 | instalacje.piony — rodzaj pionu | lista pionów zawiera rury spustowe (RS…) bez pola rodzaj; biblioteka grupowania pionów traktowała je jako piony wod.-kan. — w obliczeniach do rysunków odfiltrowane | PT-IS-01…09 |
| 5 | instalacje.wyroby | brak danych wyrobów (DTR/DWU) — obliczenia na danych przykładowych bibliotek (PC, wodomierz ∆p(Q3), EA k_v, wpusty, centrala went., moduł PV, falownik) | PT-IS-01…09 |

Pozycje wyznaczone algorytmicznie są na rysunkach oznaczone znacznikiem braku danych (linia kreskowa purpurowa, warstwa I-BRAKI). Pozycje nieaktualne wobec bieżących obliczeń — patrz „Stan opracowania i sprawy otwarte”.

*Źródło: projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md*

Uwagi kontroli arkuszy (raport_widokow.json):

* instalacje (obliczenia): Piony deszczowe RS1, RS2, RS6 wyłączone z grupowania pionów wod.-kan. (w modelu `instalacje.piony` bez pola `rodzaj`).

## Część rysunkowa — wykaz rysunków

| Nr | Tytuł | Skala | Format | Uwagi |
|---|---|---|---|---|
| PT-IS-01 | INSTALACJA WODOCIĄGOWA — RZUT PARTERU | 1:50 | nst. 610×510 |  |
| PT-IS-02 | INSTALACJA WODOCIĄGOWA — RZUTY I PIĘTRA I II PIĘTRA | 1:50 | nst. 1130×297 |  |
| PT-IS-03 | KANALIZACJA SANITARNA — RZUT PARTERU | 1:50 | nst. 594×480 |  |
| PT-IS-04 | KANALIZACJA SANITARNA — RZUTY I PIĘTRA I II PIĘTRA | 1:50 | nst. 1130×297 |  |
| PT-IS-05 | ODWODNIENIE DACHÓW — RZUT DACHU I RZUT PARTERU | 1:50 | nst. 594×810 |  |
| PT-IS-06 | OGRZEWANIE — RZUT PARTERU | 1:50 | nst. 594×450 |  |
| PT-IS-07 | OGRZEWANIE — RZUTY I PIĘTRA I II PIĘTRA | 1:50 | nst. 1310×297 |  |
| PT-IS-08 | WENTYLACJA MECHANICZNA — RZUT PARTERU | 1:50 | nst. 594×450 |  |
| PT-IS-09 | WENTYLACJA MECHANICZNA — RZUTY I PIĘTRA I II PIĘTRA | 1:50 | nst. 1310×297 |  |
| PT-IS-10 | KANALIZACJA I WODOCIĄG — ROZWINIĘCIA | — | nst. 1410×297 |  |
| PT-IS-11 | SCHEMAT POMPY CIEPŁA, C.O. I C.W.U. | — | nst. 510×420 |  |
