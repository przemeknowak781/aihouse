# Projekt techniczny — PT-3 IS (instalacje sanitarne) — tom 3 z 4

*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_IS.py`; wersja wiążąca: PDF. Pełne obliczenia (raporty bibliotek `lamela.obliczenia`) — w PDF.*

*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny `lamela.dokumenty`; pełna treść w PDF]*

# Opis techniczny — instalacje sanitarne (§ 23 RPB)

## Stan opracowania i sprawy otwarte — rejestr wymagań, sekcja E

Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z 2026-09-25 06:48) i bibliotek obliczeniowych
`lamela.obliczenia` uruchamianych przy każdym generowaniu tomu — każda liczba w tomie pochodzi z modelu albo
z obliczeń. Działka, MPZP, warunki gruntowo-wodne i warunki przyłączenia są [DANE PRZYKŁADOWE – FIKCYJNE]; parametry urządzeń
przyjęto z kart **wyrobów przykładowych** (oznaczenie [DANE PRZYKŁADOWE – FIKCYJNE] lub [ZAŁ]) — dopuszcza się wyroby równoważne
spełniające parametry wymagane podane w rozdziale „Zasadnicze urządzenia”.

**Tabela 1. Wynik sprawdzeń obliczeniowych PT-3 IS**

| Obszar obliczeń | Warunków | Spełnione | Niespełnione | Informacyjne |
|---|---|---|---|---|
| Instalacja wodociągowa i c.w.u. | 12 | 12 | 0 | 0 |
| Kanalizacja sanitarna | 33 | 33 | 0 | 0 |
| Wody opadowe i retencja | 64 | 64 | 0 | 0 |
| Drenaż i odwodnienie powierzchniowe | 18 | 7 | 0 | 11 |
| Ogrzewanie (PC, podłogówka, bufor, naczynia, hałas) | 67 | 61 | 0 | 6 |
| Wentylacja mechaniczna (bilans, centrala, czerpnia/wyrzutnia) | 12 | 12 | 0 | 0 |
| Charakterystyka energetyczna (EP ≤ EP_max; wariant z PV i bez PV) | 2 | 2 | 0 | 0 |

Warunki informacyjne — wartości podawane bez kryterium (np. moc ścian grzewczych uzupełniających).

*Źródło: lamela.obliczenia.sanitarne, lamela.obliczenia.energia — uruchomienie przy generowaniu tomu*

**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status aktualizuje się przy ponownym generowaniu):

1. Arkusze IS wygenerowano przed ostatnią zmianą modelu — przed wydaniem wygenerować ponownie (tools/generuj_widoki.py --arkusze model/arkusze_is.yaml).
2. Pompa ciepła — dwa różne zestawy danych przykładowych: moduł energii (dobór, EP) P(A−7/W35) = 8,0 kW, SCOP₃₅ = 4,50; moduł ogrzewania (PC-R290-07 (przykład)) P(A−7/W35) = 6,2 kW, SCOP₃₅ = 4,70, L_WA = 57 dB — ujednolicić w `instalacje.wyroby.PC` (DTR/DWU wybranego wyrobu) i przeliczyć EP, punkt biwalentny i hałas.
3. `instalacje.wyroby` w modelu puste — obliczenia na danych przykładowych bibliotek (PC, centrala wentylacyjna, wodomierz Δp(Q3), zawór EA k_v, wpusty) [DANE PRZYKŁADOWE – FIKCYJNE]; zastąpić danymi DTR/DWU wyrobów wybranych przez wykonawcę (wyroby równoważne).
4. Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji `projekt:` w model/budynek.yaml; pola oznaczone jako do uzupełnienia (strona tytułowa, oświadczenie).

> PODGLĄD — obliczenia odczytane z pamięci podręcznej; wersja nie do wydania.

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
* § 23 pkt 5, 6 i 12 — nie dotyczy (budynek mieszkalny, nie liniowy); § 23 pkt 4a — nie dotyczy (W-231);
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

**Obciążenie cieplne.** Projektowe obciążenie cieplne budynku Φ_HL = **7,41 kW**
(PN-EN 12831, θ_e = −18 °C, średnia roczna θ_m,e = 7,9 °C; W-150, W-151),
z dodatkiem na c.w.u. Φ_W = 1,25 kW. Temperatury wewnętrzne wg WT § 134 ust. 2 (model
`pomieszczenia[].temp`); garaż nieogrzewany (θ_u = −10,6 °C).

**Źródło ciepła.** Pompa ciepła powietrze–woda typu monoblok na czynniku naturalnym R290 (W-155) —
dane urządzenia przykładowego „PC-R290-07 (przykład)” [DANE PRZYKŁADOWE – FIKCYJNE]: moc grzewcza P(A−7/W35) =
6,2 kW, SCOP (35 °C) = 4,70, η_s = 185 %,
poziom mocy akustycznej L_WA = 57 dB (tryb nocny 52 dB). Układ
monoenergetyczny: punkt biwalentny θ_biv = **−9,7 °C**, grzałka elektryczna
6,0 kW pokrywa 0,04 % rocznego zapotrzebowania (bilans godzinowy
TMY Poznań). Jednostka zewnętrzna: jednostka zewn. PC monoblok R290 w osłonie lamelowej z ekranem akustycznym od tarasu; 7,0 m od granicy E (≥ 6,0 — W-024); strefa R290 1,0 m bez otworów, wpustów i studzienek (W-156). Skropliny —
studnia chłonna skroplin PC (żwir, ≥ 0,8 m p.p.t.), poza strefą R290 (W-146). Moduł hydrauliczny, zasobnik c.w.u. i bufor —
pomieszczenie techniczne parteru.

**Instalacja ogrzewcza.** Ogrzewanie podłogowe wodne niskotemperaturowe: θ_V = **35 °C**,
Δθ = 5 K, rura 16×2,0 mm (PE-X/PE-RT z barierą
antydyfuzyjną), 26 pętli w 22 pomieszczeniach (długość pętli ≤ 100 m,
Δp pętli ≤ 25 kPa). Rozdzielacze kondygnacyjne: P0: 1 rozdzielacz, 12 pętli, 649 kg/h, Δp_max 24,1 kPa; P1: 1 rozdzielacz, 7 pętli, 290 kg/h, Δp_max 23,0 kPa; P2: 1 rozdzielacz, 7 pętli, 497 kg/h, Δp_max 15,4 kPa.
Uzupełniające ściany grzewcze wodne (model `instalacje.grzejniki`): 0.03 — 80 W, 0.09 — 280 W, 1.05 — 150 W, 1.07 — 180 W, 2.04 — 180 W, 2.06 — 200 W.
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
ISO ePM1 50 % (nawiew), ISO Coarse 60 % (wywiew), moc wentylatorów 102 W. Lokalizacja: P2 — centrala wentylacyjna 450 m³/h, η_t 85 % — na podstawie antywibracyjnej, połączenia elastyczne, tłumiki na 4 króćcach; L w pokojach ≤ wartości PN-B-02151-2 do sprawdzenia w PT-IS (A3 I-8; W-232).
Kanał główny Ø250 mm; przewody powietrza zewnętrznego i wyrzutowego izolowane cieplnie
z paroizolacją (W-168); tłumiki akustyczne na króćcach centrali; skropliny do kanalizacji przez syfon
z zamknięciem wodnym. Czerpnia na wys. 10,0 m, wyrzutnia na wys.
10,0 m (odległości wg WT § 152 — sprawdzenia w obliczeniach).
Garaż — wentylacja naturalna, bez połączenia z centralą (Garaż 0.13: otwory wentylacji naturalnej ≥ 0,04 m²/stanowisko (WT § 108 ust. 1 pkt 1); Garaż 0.13: bez podłączenia do rekuperacji (R6 3.5)).

**Tabela 2. Strumienie powietrza wentylacji mechanicznej**

| Pomieszczenie | Nawiew [m³/h] | Wywiew [m³/h] | Podstawa |
|---|---|---|---|
| 0.03 WC gościnne | 0,00 | 30,00 | wydzielony WC |
| 0.05 Spiżarnia | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| 0.06 Salon + jadalnia + kuchnia | 90,00 | 50,00 | kuchnia z kuchenką elektryczną, > 3 osób |
| 0.09 Łazienka gościnna (natrysk) | 0,00 | 50,00 | łazienka |
| 0.10 Pokój gościnny / gabinet | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 0.12 Pomieszczenie techniczne | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| 1.02 Pokój rodzinny / biblioteka (boks C) | 50,00 | 0,00 | pokój — rozdział nawiewu |
| 1.03 Pokój dziecka 1 | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 1.04 Pokój dziecka 2 | 40,00 | 0,00 | pokój — rozdział nawiewu |
| 1.05 Łazienka dzieci (wanna) | 0,00 | 50,00 | łazienka |
| 1.07 WC z natryskiem | 0,00 | 50,00 | łazienka |
| 1.08 Pralnia z suszarnią | 0,00 | 40,00 | pralnia ≥ 2 h⁻¹ |
| 2.02 Sypialnia rodziców | 60,00 | 0,00 | pokój — rozdział nawiewu |
| 2.04 Łazienka rodziców | 0,00 | 50,00 | łazienka |
| 2.05 Gabinet / pokój gościnny okazjonalny | 45,00 | 0,00 | pokój — rozdział nawiewu |
| 2.07 Pom. techniczne (centrala rekuperacyjna, wyłaz na dach) | 0,00 | 15,00 | pomieszczenie pomocnicze bezokienne |
| Razem | 365,00 | 365,00 | bilans ±10 % |

*Źródło: model/budynek.yaml (pomieszczenia[].went); lamela.obliczenia.energia.wentylacja*

### Instalacja wodociągowa wody zimnej i ciepłej — § 23 pkt 7 lit. e RPB; W-130…W-137

Zasilanie z sieci wodociągowej przyłączem (PZT); wodomierz główny **DN25 Q3=6.3** w pomieszczeniu
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
przykanalik **DN150 i = 0.02** ze studzienką rewizyjną: studzienka rewizyjna z tworzywa PP DN425 z kinetą przelotową, właz żeliwny B125 [ZAŁ], głębokość
1,17 m, 6,2 m od granicy. Rzędne dna (wzgl. ±0,000):
pion K3 −0,99 m; pion K2 −1,29 m; pion K1 −1,42 m; wyjście z budynku −1,48 m; studzienka (dno wlotu) −1,54 m.
Zabezpieczenie przed cofką (WT § 124, W-140): Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy) — spełnione.
Skropliny centrali wentylacyjnej i wpust podłogowy pomieszczenia technicznego — przez syfony z zamknięciem
wodnym (syfon wpustu z zabezpieczeniem przed wyschnięciem). Materiały: rury i kształtki PP-HT wewnątrz,
PVC-U lite SN8 pod posadzką i na przykanaliku (przykładowe — lub równoważne).

### Odprowadzenie i zagospodarowanie wód opadowych, drenaż — § 23 pkt 7 lit. e RPB; W-142…W-146, W-018, W-019

**Odwodnienie dachów** (PN-EN 12056-3, r = 0,046 l/(s·m²); W-142): 9 pól dachowych
o łącznej powierzchni **249,0 m²**, Q = **11,46 l/s**; 14 wpustów
dachowych (podgrzewane) i przelewy awaryjne w attykach; dach zielony ekstensywny
(D4 59,1 m²). Rury spustowe wewnętrzne
(szacht SI) i zewnętrzne → kolektory deszczowe PVC-U: kolektor KD-W PVC 160 (RS3, RS4, RS1/RS2 z SI); kolektor KD-E PVC 160 (RS5 dach garażu, RS6 z pom. technicznego); przelew zbiornika DN160 do niecki chłonnej.

**Retencja — wariant bazowy (W-145).** Szczelny zbiornik **5,0 m³** (≤ 5 m³ — nie
jest urządzeniem wodnym) z osadnikiem i filtrem, pompą do podlewania ogrodu (pokrycie zapotrzebowania
na podlewanie 100 %; bilans IMGW 1991–2020) i przelewem do niecki chłonnej
(ogród deszczowy). Powierzchnia zredukowana zlewni A_red = 210,0 m²; wymagana objętość niecki
(PANDa 2050, C = 10 lat, f_b = 1,2; W-143) V_min = **5,71 m³**; niecka w modelu
(dzialka.yaml): 8,4 m³, głębokość 0,30 m — czas opróżniania
1,6 h (≤ 24 h). Deszczówka — instalacja odrębna, bez połączenia z wodociągiem (W-136).
Odwodnienia liniowe przy drzwiach bez progu i przed bramą garażu (14 korytek
wg obliczeń); woda z podjazdu i garażu przez osadnik z separatorem — nie do zbiornika retencyjnego.
Skrzynki rozsączające — wyłącznie wariant opcjonalny po stanowisku PGW Wody Polskie (D-05).

**Drenaż opaskowy: NIEWYMAGANY** (W1.1-E (wilgoć gruntowa, woda nienaporowa)).
Grunt: piaski średnie, k_f = 3,00·10⁻⁴ m/s (wartość typowa [W]; wymagane badania — E-04) Zwierciadło wody gruntowej 3,80 m p.p.t.; spód fundamentu −0,85 m (wzgl. ±0,00), teren przy budynku średnio −0,29 m → głębokość posadowienia 0,56 m; ZWG 3,24 m poniżej spodu fundamentu. Pomieszczenia poniżej terenu: brak (budynek niepodpiwniczony, posadzka parteru nad terenem) Grunt silnie przepuszczalny (k_f > 10⁻⁴ m/s) i ZWG ≥ 0,5 m pod fundamentem — woda opadowa infiltruje pionowo, nie powstaje woda zastoiskowa przy ścianach; wystarcza izolacja przeciwwilgociowa. Zalecenia: Odwodnienie powierzchniowe: profilowanie terenu ze spadkiem ≥ 2 % od budynku na pasie ≥ 2,0 m (rzędne projektowane w dzialka.yaml: teren.punkty_projektowane) — wymagane niezależnie od drenażu. Opaska żwirowa szer. 0,5 m wokół budynku (żwir płukany 16/32 mm na geowłókninie, obrzeże), spadek od ściany; chroni cokół przed rozbryzgiem i ułatwia kontrolę izolacji [W].

## Powiązania instalacji z sieciami zewnętrznymi i punkty pomiarowe — § 23 pkt 8 RPB

**Tabela 4. Powiązania z sieciami i odbiornikami zewnętrznymi (dane działki — [DANE PRZYKŁADOWE – FIKCYJNE])**

| Medium | Sieć zewnętrzna / odbiornik | Przyłącze / przewód | Długość [m] |
|---|---|---|---|
| woda | wodociąg PE 110 (ul. Lipowa) | przyłącze PE 40, przykrycie ≥ 1,20 m (W-141), pod podjazdem i płytą garażu w rurze osłonowej, wodomierz w pom. 0.12 | 18,80 |
| ścieki bytowe | kanalizacja sanitarna PVC 200, dno ≈ 99,20 | przykanalik PVC-U 160, i ≥ 2 %, studzienka rewizyjna SR1 Ø425 (x 13,0; y 43,8) — wyjście z płyty pod ścianą pn. (piony K1, K2) | 13,90 |
| wody opadowe | zagospodarowanie na działce (retencja) | kolektor KD-W PVC 160 (RS3, RS4, RS1/RS2 z SI) | 34,80 |
| wody opadowe | zagospodarowanie na działce (retencja) | kolektor KD-E PVC 160 (RS5 dach garażu, RS6 z pom. technicznego) | 31,60 |
| wody opadowe | zagospodarowanie na działce (retencja) | przelew zbiornika DN160 do niecki chłonnej | 6,20 |
| wody opadowe | zagospodarowanie na działce (retencja) | OL-1 (i OL-4 kanałem wzdłuż podjazdu) → separator SEP-1 → niecka NT-E (PVC 160) | 3,30 |
| wody opadowe | zagospodarowanie na działce (retencja) | RS7 (rynny zach. PL-E i PL-2) → KD-W, PVC 110 | 3,20 |
| wody opadowe | zagospodarowanie na działce (retencja) | RS8 (rynny PL-E pd. i PL-D) + OL-6 (próg DZ3) → KD-E, PVC 110 | 4,10 |
| wody opadowe | zagospodarowanie na działce (retencja) | OL-5 (próg DZ2 garażu) → KD-E, PVC 110 (woda czysta z podestu — nie z posadzki garażu) | 0,80 |

*Źródło: model/dzialka.yaml — uzbrojenie istniejące i projektowane*

**Punkty pomiarowe:** wodomierz główny DN25 Q3=6.3 (odczyt gestora sieci; W-131); licznik
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
(WT § 134 ust. 2; model `pomieszczenia[].temp`): **16 °C** — 6 pomieszczeń: 0.01, 0.05, 0.15, 0.16, 0.12, 2.07; **20 °C** — 22 pomieszczeń: 0.02, 0.03, 0.04, 0.06, 0.07, 0.08, 0.10, 0.11, 1.01, 1.02, 1.03, 1.04, 1.06, 1.08, 2.01, 2.02, 2.03, 2.05, 2.06, 0.14, 1.09, 2.08; **24 °C** — 0.09 Łazienka gościnna (natrysk), 1.05 Łazienka dzieci (wanna), 1.07 WC z natryskiem, 2.04 Łazienka rodziców. Powietrze zewnętrzne ≥ 20 m³/h na osobę
(5 os.), wywiew wg PN-83/B-03430/Az3 (W-161, W-162). Szczelność budynku n50 = 1,0 h⁻¹ [ZAŁ]
(cel projektowy — potwierdzić próbą ciśnieniową, W-249); sprawność odzysku ciepła η_v = 0,85.

### Zestawienie wyników i dobór urządzeń — § 23 pkt 8 lit. b RPB

**Podstawowe wyniki** (tabela w PDF):

* Projektowe obciążenie cieplne budynku Φ_HL: 7,41 kW (—; PN-EN 12831 [W-151])
* Pompa ciepła PC-R290-07 (przykład): moc P(A−7/W35): 6,2 kW (—; [DANE PRZYKŁADOWE – FIKCYJNE])
* Pokrycie mocy przy θ_e: P_PC + P_grzałki ≥ Φ_HL + Φ_W: 10,55 kW (≥ 8,66 kW; PN-EN 12831 / VDI 4645 [W] [W-155])
* Punkt biwalentny: −9,7 °C (≤ −7,0 °C; VDI 4645 / praktyka [ZAŁ] [W-155])
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
* Dachy: A / Q (r = 0,046 l/(s·m²)): 249,0 m² / 11,46 l/s  (—; PN-EN 12056-3 [W-142])
* Pojemność szczelnego zbiornika (bez zgłoszenia): 5,0 m³ (≤ 5,0 m³; W-145: PB art. 29 ust. 2 pkt 36 (5–15 m³ — zgłoszenie, ust. 1 pkt 38) [W-145])
* Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia): 5,85 m³ (≥ 5,71 m³; Aquanet 2024 wzór (1), f_b [W-143])
* Niecka: czas opróżniania: 1,6 h (≤ 24,0 h; W-143: Aquanet 2024 zał. C [zalozenie] [W-143])

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
**wariant A0 bez PV podano jawnie** — oba warianty sprawdzono względem EP_max. Dane urządzeń (SCOP, η_t,
moce pomocnicze) z kart wyrobów przykładowych [DANE PRZYKŁADOWE – FIKCYJNE] — przed wydaniem do realizacji zastąpić danymi
deklarowanymi wybranych wyrobów (W-242) i przeliczyć.

### Bilans mocy urządzeń elektrycznych i zużywających inne rodzaje energii — § 23 pkt 11 lit. a RPB

**Tabela 5. Bilans mocy — odbiorniki ≥ 0,5 kW (instalacje stałe budynku)**

| Odbiornik | Grupa | P [kW] | Faz |
|---|---|---|---|
| Oświetlenie P0 | oswietlenie | 0,56 | 1 |
| Gniazda P0: 0.10 Pokój gościnny / gabinet, 0.08 Przedpokój gościnny, 0.14 Szacht instalacyjny SI, 0.04 Klatka schodowa, 0.16 Schowek pod spocznikiem (h < 1,40), 0.07 Pas komunikacyjny przy schodach, 0.05 Spiżarnia, 0.15 Schowek pod schodami (h 1,40–2,20), 0.02 Hol, 0.01 Wiatrołap, 0.11 Przedsionek gospodarczy | gniazda | 2,00 | 1 |
| Gniazda P1: 1.04 Pokój dziecka 2, 1.03 Pokój dziecka 1, 1.09 Szacht instalacyjny SI, 1.01 Hol, 1.06 Klatka schodowa | gniazda | 2,00 | 1 |
| Gniazda P1: 1.02 Pokój rodzinny / biblioteka (boks C) | gniazda | 2,00 | 1 |
| Gniazda P2: 2.02 Sypialnia rodziców, 2.03 Garderoba (przedpokój apartamentu), 2.08 Szacht instalacyjny SI, 2.06 Klatka schodowa (wyjście z biegu 2, pustka), 2.01 Hol | gniazda | 2,00 | 1 |
| Gniazda P2: 2.05 Gabinet / pokój gościnny okazjonalny | gniazda | 2,00 | 1 |
| Gniazda kuchenne 1 (0.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 |
| Gniazda kuchenne 2 (0.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 |
| Gniazda łazienki (0.03 WC gościnne) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (0.09 Łazienka gościnna (natrysk)) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (1.05 Łazienka dzieci (wanna)) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (1.07 WC z natryskiem) | gniazda_lazienka | 2,00 | 1 |
| Gniazda łazienki (2.04 Łazienka rodziców) | gniazda_lazienka | 2,00 | 1 |
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
| Moc zainstalowana (wszystkie odbiorniki) |  | 71,43 |  |
| Moc szczytowa z układem ograniczania mocy (DLM) |  | 26,21 |  |

Moc przyłączeniowa 27 kW, zabezpieczenie przedlicznikowe 40 A — PT-4 IE. Budynek nie ma urządzeń zużywających paliwa (gaz, olej, biomasa) ani urządzeń technologicznych.

*Źródło: lamela.obliczenia.elektryka.bilans (odczyt; obliczenia PT-4 IE)*

### Właściwości cieplne przegród zewnętrznych — § 23 pkt 11 lit. b RPB; W-243, W-244

**Tabela 6. Współczynniki przenikania ciepła przegród obudowy (szczegóły — PT-1 AR)**

| Przegroda | Rodzaj | U [W/(m²·K)] | U_max [W/(m²·K)] | Spełnia |
|---|---|---|---|---|
| DZ1 | dach | 0,13 | 0,15 | tak |
| SD1 | dach | 0,11 | 0,15 | tak |
| SD2 | dach | 0,12 | 0,15 | tak |
| POD-0 | podloga grunt | 0,11 | 0,30 | tak |
| SWG | sciana nieogrz | 0,27 | 0,30 | tak |
| SZ1 | sciana zewn | 0,17 | 0,20 | tak |
| SZ2 | sciana zewn | 0,17 | 0,20 | tak |
| SZL | sciana zewn | 0,10 | 0,20 | tak |
| ST2Z | strop zewn | 0,13 | 0,15 | tak |

Mostki cieplne: H_TB = 30,7 W/K (Ψ z symulacji PN-EN ISO 10211 — projekt/08_obliczenia/mostki); U podłogi na gruncie wg PN-EN ISO 13370.

*Źródło: lamela.obliczenia.energia.obudowa; WT zał. 2 pkt 1.1–1.2*

### Parametry sprawności energetycznej instalacji — § 23 pkt 11 lit. c RPB

**Tabela 7. Sprawności cząstkowe systemów (wariant projektowy A)**

| Instalacja | Wytwarzanie η_g | Akumulacja η_s | Przesył η_d | Regulacja η_e | Łącznie η_tot |
|---|---|---|---|---|---|
| Ogrzewanie | 4,50 | 1,00 | 0,96 | 0,89 | 3,84 |
| Ciepła woda użytkowa | 3,20 | 0,93 | 0,60 | — | 1,78 |

Źródło ogrzewania: SCOP = 4,50 (PN-EN 14825, dane przykładowe z karty katalogowej typowej pompy ciepła powietrze–woda R290 klasy A+++ (35 °C) 7–8 kW (lub równoważna)); η_H,e = 0,89 (tab. 3 lp. 6b), η_H,d = 0,96 (tab. 6 lp. 3a), η_H,s = 1,00 (tab. 8 lp. 3)

C.w.u.: COP_cwu = 3,20 (PN-EN 16147); η_W,s = 0,929 (strata zasobnika 55 W); η_W,d = 0,60 (tab. 12 lp. 6.1a — cyrkulacja z ograniczeniem czasu pracy)

Wentylacja: odzysk ciepła η_oc = 0,85; pomocnicze: pompa obiegowa ogrzewania podłogowego (EC) 25 W; sterownik/grzałka tacy PC (poza SCOP) 15 W; wentylatory centrali (P = SFP·q) 102 W

Moduł ogrzewania (bilans godzinowy TMY): SCOP obliczeniowy 4,09 (deklarowany 4,70), η_H,e = 0,89, η_H,d = 0,96 — do ujednolicenia z EP po wyborze wyrobu.

*Źródło: lamela.obliczenia.energia.ep — metodologia tab. 2, 3, 6, 8, 12, 14*

### Wskaźniki EP, EK, EU, udział OZE — spełnienie wymagań — § 23 pkt 11 lit. d RPB; WT § 328–329 (W-240)

**Tabela 8. Charakterystyka energetyczna — wariant projektowy, wariant bez PV, alternatywy i wrażliwość [kWh/(m²·rok)]**

| Wariant | EU | EK | EP | EP_max | U_OZE [%] | E_CO2 [t/rok] | EP ≤ EP_max |
|---|---|---|---|---|---|---|---|
| A: PC R290 + PV + rekuperacja | 41,17 | 23,14 | 35,59 | 70,00 | 74,71 | 2,07 | tak |
| A0: PC R290 + rekuperacja, bez PV | 41,17 | 23,14 | 57,85 | 70,00 | 57,62 | 3,36 | tak |
| B: kocioł gazowy kondensacyjny + rekuperacja | 41,17 | 70,55 | 88,25 | 70,00 | 0,00 | 4,44 | NIE |
| C: PC — wartości domyślne metodologii, bez PV | 41,17 | 32,67 | 81,69 | 70,00 | 47,81 | 4,74 | NIE |
| A (n50 = 4 h⁻¹ — brak próby szczelności) | 55,13 | 26,85 | 44,14 | 70,00 | 74,96 | 2,56 | tak |

A — wariant projektowy (z PV); A0 — ten sam budynek i instalacje bez PV; B, C — analiza alternatyw (RPB § 20 ust. 1 pkt 10, PAB); ostatnie wiersze — wrażliwość (szczelność, Ψ).

*Źródło: lamela.obliczenia.energia.ep (metodologia Dz.U. 2015 poz. 376 ze zm.)*

> Wariant projektowy A: EP = **35,6** kWh/(m²·rok) ≤ EP_max = 70,0 — wymaganie spełnione. Wariant A0 bez PV: EP = **57,9** kWh/(m²·rok) ≤ EP_max — wymaganie spełnione także bez instalacji PV.

### Obliczenia: charakterystyka energetyczna — wariant A — W-240…W-242

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.energia.ep]*

Dane do świadectwa charakterystyki energetycznej (centralny rejestr) przekazuje się po zakończeniu budowy na podstawie wyrobów wbudowanych i wyniku próby szczelności (W-251; PB art. 57 ust. 1 pkt 6a).

## Dane dotyczące warunków ochrony przeciwpożarowej — § 23 pkt 10 RPB

Budynek mieszkalny jednorodzinny: kategoria zagrożenia ludzi **ZL IV** (WT §209 ust. 2 pkt 4), grupa wysokości
**N** (WT §8 pkt 1), 3 kondygnacje nadziemne — zwolniony
z wymagań klasy odporności pożarowej (WT §213 pkt 1 lit. a; W-211). W zakresie PT-3 IS:

* przejścia instalacji przez stropy i ściany — bez wymagań odporności ogniowej przepustów (brak wymagań
  klasy odporności elementów, jw.); przejścia uszczelnione akustycznie i szczelnie powietrznie (W-249);
* przewody wentylacyjne z materiałów palnych dopuszczalne w budynku jednorodzinnym jednolokalowym (W-168);
  centrala w wydzielonym pomieszczeniu technicznym;
* pompa ciepła z czynnikiem palnym R290 (klasa A3 wg PN-EN 378-1+A1:2021-03): jednostka zewnętrzna poza
  budynkiem, strefa bezpieczeństwa wg DTR (typowo 1,0 m) wolna od otworów, wpustów, studzienek i źródeł
  zapłonu (W-156) — sprawdzenie w obliczeniach ogrzewania; instalacja wewnętrzna wyłącznie wodna (monoblok);
* brak instalacji gazowej i urządzeń spalania paliw — nie występują przewody spalinowe;
* zaopatrzenie w wodę do zewnętrznego gaszenia pożaru: najbliższy hydrant zewnętrzny DN80 (ul. Lipowa) — zaopatrzenie ppoż. (W-217) [do potwierdzenia] (dane PZT) — instalacja
  wodociągowa budynku nie pełni funkcji przeciwpożarowej (brak hydrantów wewnętrznych — nie wymagane).

## Zasadnicze urządzenia — parametry wymagane — § 23 pkt 9 RPB; PB art. 10

Urządzenia określono **parametrami wymaganymi**. Wyroby przywołane w obliczeniach są przykładowe — dopuszcza
się wyroby równoważne o parametrach nie gorszych, wprowadzone do obrotu zgodnie z PB art. 10 (deklaracja
właściwości użytkowych / deklaracja zgodności, oznakowanie CE lub znak budowlany B). Zamiana wyrobu wymaga
ponownego przeliczenia EP, punktu biwalentnego i hałasu (generator tomu przelicza je z modelu).

**Tabela 9. Zasadnicze urządzenia instalacji sanitarnych**

| Urządzenie | Parametry wymagane | Podstawa |
|---|---|---|
| Pompa ciepła powietrze–woda, monoblok | czynnik naturalny R290 (GWP < 150); P(A−15/W35) ≥ 5,0 kW i pokrycie Φ_HL + Φ_W = 8,66 kW przy θ_e z grzałką ≤ 6 kW; SCOP₃₅ ≥ 4,7; η_s ≥ 125 %; L_WA ≤ 57 dB (tryb nocny niżej); regulacja pogodowa, sterowanie zależne od zapotrzebowania | W-155, W-156, W-024; (UE) 2024/573, 813/2013 |
| Zasobnik c.w.u. z wężownicą | V ≥ 400 dm³, wężownica ≥ 1,8 m² (dla PC), grzałka do dezynfekcji, grupa bezpieczeństwa, izolacja fabryczna | W-133, W-134; PN-EN 16147+A1:2023-06 |
| Bufor c.o. (szeregowy) | V ≥ 80 dm³, izolowany | obliczenia ogrzewania |
| Naczynia wzbiorcze przeponowe | c.o. ≥ 18 dm³ (p₀ 0,83 bar); c.w.u. ≥ 50 dm³ (p₀ 3,8 bar), przepływowe | PN-B-02414:1999 (powołana w WT) [W-154] |
| Rozdzielacze ogrzewania podłogowego | P0: 12 obwodów, przepływomierze, siłowniki 230 V/24 V NC; P1: 7 obwodów, przepływomierze, siłowniki 230 V/24 V NC; P2: 7 obwodów, przepływomierze, siłowniki 230 V/24 V NC | W-152, W-154 |
| Centrala wentylacyjna z odzyskiem ciepła | V_max ≥ 435 m³/h przy sprężu instalacji; η_t ≥ 85 %; SFP ≤ 1,90 kW/(m³/s); SEC klasa ≥ A; by-pass 100 %; filtry ISO ePM1 50 % (nawiew), ISO Coarse (wywiew); L_WA wg PN-B-02151-2 w pokojach | W-160…W-169; (UE) 1253/2014; PN-EN 13141-7+A1:2026-05 |
| Zestaw wodomierzowy | wodomierz DN25 Q3=6.3 (lub wg warunków gestora), zawory, filtr, EA; reduktor ciśnienia wymagany | W-131, W-130; PN-EN 1717 |
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
| 1 | Odwodnienie powierzchni IZ-ST2Z | wspornik, A = 5,7 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 2 | Odwodnienie powierzchni PL-2 | taras, A = 23,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 3 | Odwodnienie powierzchni PL-3 | taras, A = 23,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 4 | Odwodnienie powierzchni PL-C1 | wspornik, A = 9,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 5 | Odwodnienie powierzchni PL-C2 | wspornik, A = 9,8 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 6 | Odwodnienie powierzchni PL-D | wspornik, A = 6,1 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 7 | Odwodnienie powierzchni PL-DA | taras, A = 3,0 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 8 | Odwodnienie powierzchni PL-E | taras, A = 23,7 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 9 | Odwodnienie powierzchni PS-A | wspornik, A = 14,1 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 10 | Odwodnienie powierzchni SW1 | wspornik, A = 2,8 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 11 | Odwodnienie powierzchni WYL1 | wspornik, A = 1,2 m² — brak wpustów/rzygaczy w modelu; w obliczeniach przyjęto wpust propozycyjny | PT-IS-07 |
| 12 | Ogrzewanie — pomieszczenia z niedoborem mocy podłogi | 0.03 WC gościnne: gęstość strumienia ≤ q_G (θ_F ≤ 29 °C); 0.03 WC gościnne: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.06 Salon + jadalnia + kuchnia: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.09 Łazienka gościnna (natrysk): gęstość strumienia ≤ q_G (θ_F ≤ 33 °C); 0.09 Łazienka gościnna (natrysk): moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.10 Pokój gościnny / gabinet: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.11 Przedsionek gospodarczy: moc podłogi przy θ_V,des (T = 10 cm) ≥ Φ_HL; 0.12 Pomieszczenie techniczne: gęstość strumienia ≤ q_G (θ_F ≤ 25 °C) | PT-IS-09, PT-IS-10, PT-IS-11 |
| 13 | Ogrzewanie — pompa ciepła | sprawdzenie niespełnione: Moc nominalna PC (zakaz F-gazów dotyczy ≤ 12 kW — czynnik R290, GWP₁₀₀ = 0,02) (rozp. (UE) 2024/573 zał. IV pkt 8 lit. b) | PT-IS-09, PT-IS-10, PT-IS-11 |
| 14 | Pion/szacht wentylacyjny (SUP, ETA) | brak w modelu szachtu wentylacyjnego (szacht SI zajęty przez piony wod.-kan. i deszczowe) — przyjęto lokalizację proponowaną algorytmicznie | PT-IS-12, PT-IS-13, PT-IS-14 |
| 15 | Piony c.o. (zasilanie rozdzielaczy P1, P2) | brak tras pionów c.o. w instalacje.yaml — przyjęto pion proponowany przy rozdzielaczu R-P1 | PT-IS-09, PT-IS-10, PT-IS-11 |
| 16 | Przelewy awaryjne / wpusty | sprawdzenie niespełnione: Pole D1: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | PT-IS-07, PT-IS-08 |
| 17 | Strumienie powietrza pomieszczeń (went) | rozbieżność modelu z bilansem wentylacji (moduł energii, PN-83/B-03430/Az3), nawiew/wywiew [m³/h]: 0.15: model 0/0 → bilans 0/15; 0.16: model 0/0 → bilans 0/15; 0.10: model 40/0 → bilans 52/0; 1.02: model 40/0 → bilans 119/0; 1.03: model 40/0 → bilans 55/0; 1.04: model 40/0 → bilans 52/0; 2.02: model 50/0 → bilans 90/0; 2.05: model 40/0 → bilans 68/0; 2.07: model 0/0 → bilans 0/15 — na rysunku przyjęto wartości większe | PT-IS-12, PT-IS-13, PT-IS-14 |
| 18 | Trasy przewodów (woda, kanalizacja, c.o., wentylacja) | model nie zawiera przebiegów przewodów — trasy wyznaczono algorytmicznie (ortogonalnie, przy ścianach, z pionów/rozdzielaczy do przyborów) | PT-IS-01, PT-IS-02, PT-IS-03, PT-IS-04, PT-IS-05, PT-IS-06, PT-IS-07, PT-IS-08, PT-IS-09, PT-IS-10, PT-IS-11, PT-IS-12, PT-IS-13, PT-IS-14 |
| 19 | Zasobnik c.w.u. — pojemność | wyposazenie.yaml: 300 dm³, obliczenia (PN-EN 12831-3 / zapotrzebowanie): 400 dm³ — na rysunku wartość z obliczeń | PT-IS-01, PT-IS-02, PT-IS-03 |
| 20 | instalacje.piony — rodzaj pionu | lista pionów zawiera rury spustowe (RS…) bez pola `rodzaj`; biblioteka grupowania pionów traktowała je jako piony wod.-kan. — w obliczeniach do rysunków odfiltrowane | PT-IS-01, PT-IS-02, PT-IS-03, PT-IS-04, PT-IS-05, PT-IS-06, PT-IS-07, PT-IS-08, PT-IS-09, PT-IS-10, PT-IS-11, PT-IS-12, PT-IS-13, PT-IS-14 |
| 21 | instalacje.wyroby | brak danych wyrobów (DTR/DWU) — obliczenia na danych przykładowych bibliotek (PC, wodomierz ∆p(Q3), EA k_v, wpusty, centrala went., moduł PV, falownik) | PT-IS-01, PT-IS-02, PT-IS-03, PT-IS-04, PT-IS-05, PT-IS-06, PT-IS-07, PT-IS-08, PT-IS-09, PT-IS-10, PT-IS-11, PT-IS-12, PT-IS-13, PT-IS-14 |

Pozycje wyznaczone algorytmicznie są na rysunkach oznaczone znacznikiem braku danych (linia kreskowa purpurowa, warstwa I-BRAKI). Pozycje nieaktualne wobec bieżących obliczeń — patrz „Stan opracowania i sprawy otwarte”.

*Źródło: projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md*

Uwagi kontroli arkuszy (raport_widokow.json):

* instalacje (obliczenia): Piony deszczowe RS1, RS2, RS6 wyłączone z grupowania pionów wod.-kan. (w modelu `instalacje.piony` bez pola `rodzaj`).

## Część rysunkowa — wykaz rysunków

| Nr | Tytuł | Skala | Format | Uwagi |
|---|---|---|---|---|
| PT-IS-01 | INSTALACJA WODOCIĄGOWA — RZUT PARTERU | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-02 | INSTALACJA WODOCIĄGOWA — RZUT I PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-03 | INSTALACJA WODOCIĄGOWA — RZUT II PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-04 | KANALIZACJA SANITARNA — RZUT PARTERU | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-05 | KANALIZACJA SANITARNA — RZUT I PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-06 | KANALIZACJA SANITARNA — RZUT II PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-07 | ODWODNIENIE DACHÓW — RZUT DACHU | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-08 | ODWODNIENIE DACHÓW — RZUT PARTERU (RURY SPUSTOWE) | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-09 | OGRZEWANIE — RZUT PARTERU | 1:50 | A1 | brak pliku — strona zastępcza |
| PT-IS-10 | OGRZEWANIE — RZUT I PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-11 | OGRZEWANIE — RZUT II PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-12 | WENTYLACJA MECHANICZNA — RZUT PARTERU | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-13 | WENTYLACJA MECHANICZNA — RZUT I PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-14 | WENTYLACJA MECHANICZNA — RZUT II PIĘTRA | 1:50 | A3x3 | brak pliku — strona zastępcza |
| PT-IS-15 | KANALIZACJA SANITARNA — ROZWINIĘCIE PIONÓW | — | A3x3 | brak pliku — strona zastępcza |
| PT-IS-16 | INSTALACJA WODOCIĄGOWA — ROZWINIĘCIE (AKSONOMETRIA) | — | A3x3 | brak pliku — strona zastępcza |
| PT-IS-17 | SCHEMAT POMPY CIEPŁA, C.O. I C.W.U. | — | A3x3 | brak pliku — strona zastępcza |
