# Projekt techniczny — PT-4 IE+BT (instalacje elektryczne i telekomunikacyjne) — tom 4 z 4

*Źródło Markdown części opisowej — generowane przez `tools/dokumenty/tom_PT_IE.py`; wersja wiążąca: PDF. Pełne obliczenia (raporty bibliotek `lamela.obliczenia.elektryka`) i tabele wyników — w PDF.*

*[Oświadczenie projektanta PT (art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 PB) — blok formalny `lamela.dokumenty`; pełna treść w PDF]*

# Opis techniczny — instalacje elektryczne (§ 23 RPB)

## Stan opracowania i sprawy otwarte — rejestr wymagań, sekcja E

Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z 2026-09-25 10:33) i bibliotek obliczeniowych
`lamela.obliczenia` (moduły `elektryka`, `energia`, `sanitarne`) uruchamianych przy każdym generowaniu tomu —
każda liczba w tomie pochodzi z modelu albo z obliczeń. Działka, MPZP, warunki gruntowe i **warunki przyłączenia
do sieci** są [DANE PRZYKŁADOWE – FIKCYJNE]; parametry urządzeń przyjęto z kart **wyrobów przykładowych** ([ZAŁ]) — dopuszcza się
wyroby równoważne spełniające parametry wymagane podane w rozdziale „Wyroby i parametry wymagane”.

**Tabela 1. Wynik sprawdzeń obliczeniowych PT-4 IE**

| Obszar obliczeń | Warunków | Spełnione | Niespełnione | Informacyjne |
|---|---|---|---|---|
| Bilans mocy, moc przyłączeniowa, podział na fazy | 9 | 8 | 0 | 1 |
| WLZ, obwody, zabezpieczenia, ∆U, samoczynne wyłączenie, SPD, PWP | 117 | 114 | 0 | 1 |
| Instalacja fotowoltaiczna (≤ 6,5 kWp) | 12 | 12 | 0 | 0 |
| Ocena ryzyka piorunowego, uziom, połączenia wyrównawcze | 3 | 2 | 0 | 1 |

Warunki informacyjne — wartości podawane bez kryterium (np. moc szczytowa bez zarządzania mocą).

*Źródło: lamela.obliczenia.elektryka — uruchomienie przy generowaniu tomu*

**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status aktualizuje się przy ponownym generowaniu):

1. Uwagi na arkuszach PT-IE-01, PT-IE-02, PT-IE-03 przywołują PN-EN 12464-1 bez daty wydania (w tomie: PN-EN 12464-1:2012, powołana w WT) — status i wydanie wg rozdz. „Przedmiot, zakres i podstawy opracowania”; poprawić uwagę w generatorze rysunków.
2. Uwagi na arkuszach PT-IE-12, PT-IE-13 przywołują PN-HD 60364-5-534 (wycofana; zastąpiona przez PN-HD 60364-5-53:2022-10) — status i wydanie wg rozdz. „Przedmiot, zakres i podstawy opracowania”; poprawić uwagę w generatorze rysunków.
3. Opis trasy WLZ w modelu działki (uzbrojenie projektowane „en”) podaje YKY 5×16, obliczenia — YKY 5×25; w tomie obowiązuje przekrój z obliczeń — poprawić opis w modelu i ponownie wygenerować rysunki PZT (tom I).
4. `instalacje.wyroby` w modelu puste — moduł PV, falownik, pompa ciepła i aparatura przyjęte z danych przykładowych bibliotek [DANE PRZYKŁADOWE – FIKCYJNE]; zastąpić danymi DTR/DWU wyrobów wybranych przez wykonawcę (wyroby równoważne spełniające parametry wymagane — rozdz. „Wyroby”).
5. Dane osobowe (Inwestor, projektanci, nr uprawnień, pracownia) — brak sekcji `projekt:` w model/budynek.yaml; pola oznaczone jako do uzupełnienia (strona tytułowa, oświadczenie).
6. Warunki przyłączenia OSD (E-05) — nieuzyskane; moc przyłączeniowa, typ zabezpieczenia przedlicznikowego, impedancja pętli zwarcia Z_Q i prąd zwarciowy w ZKP, rozdział PEN przyjęte jako [ZAŁ]; po otrzymaniu warunków przeliczyć obwody (D-12, W-192, E-05).

## Przedmiot, zakres i podstawy opracowania — § 23 RPB

**Przedmiot.** Projekt techniczny instalacji elektrycznych budynku mieszkalnego jednorodzinnego
„Dom LAMELA” — działka ewid. nr 123/4, obręb 0005 „Przykładowo”, gm. Przykładowo (fikcyjna): zasilanie z sieci nN
(złącze kablowo-pomiarowe, wewnętrzna linia zasilająca), rozdzielnica główna, instalacje oświetlenia, gniazd
wtyczkowych i zasilania urządzeń (w tym pompy ciepła, centrali wentylacyjnej, punktu ładowania pojazdu
elektrycznego), mikroinstalacja fotowoltaiczna, ochrona przeciwporażeniowa i przeciwprzepięciowa, uziemienia
i połączenia wyrównawcze, ocena ryzyka piorunowego, instalacje telekomunikacyjne (przyłącze światłowodowe,
okablowanie strukturalne, RTV/SAT, SSWiN, wideodomofon), przeciwpożarowy wyłącznik prądu, bilans mocy.

**Autorzy i specjalności.** Tom obejmuje dwie specjalności uprawnień budowlanych: instalacyjną w zakresie
sieci, instalacji i urządzeń elektrycznych i elektroenergetycznych (PB art. 15a ust. 22) — wszystkie rozdziały
i arkusze z wyjątkiem wymienionych dalej; instalacyjną
w zakresie sieci, instalacji i urządzeń telekomunikacyjnych (PB art. 15a ust. 18 — telekomunikacja przewodowa
wraz z infrastrukturą telekomunikacyjną) — rozdz. „Instalacje telekomunikacyjne” i arkusze
PT-IE-07, PT-IE-08, PT-IE-09. Współautorów z zakresem opracowania wymieniono na stronie tytułowej
i w oświadczeniu projektanta (PB art. 34 ust. 3e). Tom obejmujący więcej niż jedną specjalność ma w nazwie pliku
symbol **WB** (zał. 1 RPB); oznaczenie tomu w odesłaniach innych tomów: PT-4.

**Zakres wg RPB (rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, Dz.U. 2020
poz. 1609, t.j. Dz.U. 2022 poz. 1679 ze zm.):**

* § 23 pkt 7 lit. g — instalacje elektroenergetyczne; lit. h — instalacje telekomunikacyjne (W-196);
  lit. i — instalacja piorunochronna (analiza ryzyka, W-191); lit. j (instalacje ochrony przeciwpożarowej) —
  nie dotyczy: budynek ZL IV bez instalacji i urządzeń ppoż. wymaganych przepisami (PWP i czujki dymu — rozdz.
  „Dane dotyczące warunków ochrony przeciwpożarowej”); lit. a–f — tom PT-3 IS;
* § 23 pkt 8 — powiązanie instalacji z siecią elektroenergetyczną i telekomunikacyjną wraz z punktami
  pomiarowymi, założenia i wyniki obliczeń, dobór urządzeń; lit. b — moc elektryczna urządzeń ogrzewczych
  i wentylacyjnych;
* § 23 pkt 10 — dane dotyczące warunków ochrony przeciwpożarowej stosownie do zakresu tomu;
* § 23 pkt 11 lit. a — bilans mocy urządzeń elektrycznych stanowiących stałe wyposażenie budynku (bez urządzeń
  technologicznych — budynek mieszkalny); lit. b–d — tom PT-3 IS (charakterystyka energetyczna);
* § 23 pkt 1–5 i 9 — nie dotyczy tomu (konstrukcja, geotechnika, przegrody, urządzenia instalacji sanitarnych —
  PT-1 AR, PT-2 BO, PT-3 IS); § 23 pkt 4a — nie dotyczy (W-231); § 23 pkt 6 — nie dotyczy (budynek
  mieszkalny, nie obiekt liniowy);
* § 23 pkt 12 (dodany Dz.U. 2026 poz. 597 § 1 pkt 6) — nie dotyczy: PZT i PAB nie przewidują budowli
  ochronnej ani miejsca doraźnego schronienia (PAB § 20 ust. 1 pkt 14 — n/d);
* § 24 pkt 4 lit. b — rzuty instalacji elektroenergetycznych, telekomunikacyjnych i piorunochronnej, schemat
  rozdzielnicy głównej, uziom i połączenia wyrównawcze (część rysunkowa).

**Podstawy prawne (rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`, sekcja A.2).**
Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.); § 180–§ 192 rozporządzenia MI z 12.04.2002 w sprawie
warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (WT; t.j. Dz.U. 2022 poz. 1225 ze zm.),
stosowanego na podstawie art. 102a ust. 1 i 2 PB w związku z oświadczeniem Inwestora z dnia
[DO UZUPEŁNIENIA: data oświadczenia Inwestora (art. 102a PB)]; rozporządzenie MSWiA w sprawie ochrony
przeciwpożarowej budynków (ROPoż; t.j. Dz.U. 2023 poz. 822, zm. Dz.U. 2024 poz. 1716); Prawo energetyczne
(t.j. Dz.U. 2026 poz. 43 ze zm.), ustawa o OZE (t.j. Dz.U. 2026 poz. 68), rozporządzenie systemowe (RSys;
t.j. Dz.U. 2025 poz. 919 ze zm.); ustawa o elektromobilności (t.j. Dz.U. 2026 poz. 1243); rozporządzenia (UE)
2024/1309 (art. 10 — infrastruktura światłowodowa), 2016/631 (NC RfG), dyrektywa (UE) 2024/1275 (EPBD,
nietransponowana — stosowana dobrowolnie).

**Normy (sekcja A.3 rejestru).** PN-HD 60364-1:2010; -4-41:2017-09; -4-42:2011; -4-43:2024-04; -4-443:2016-03;
-5-52:2011; -5-53:2022-10; -5-54:2011; -6:2016-07; -7-701:2025-02; -7-712:2016-05; -7-714:2012; -7-722:2019-01;
PN-EN 62305-1…-4:2008/2011/2012 (wycofane; wydania powołane w zał. 1 WT — stosowane) i PN-EN IEC
62305-1…-4:2025-09 (aktualne, wersja angielska — rozdz. „Ocena ryzyka piorunowego”); PN-EN 12464-1:2012
(natężenie oświetlenia; wydanie powołane w zał. 1 WT lp. 41); PN-EN IEC 61643-11:2026-04;
PN-EN 62446-1:2016-08; PN-EN 50549-1:2019-02; PN-EN 50618:2015-03; PN-EN 50173-4:2018-07; PN-EN 50174-2:2018-08;
PN-EN 50310:2016-09; PN-EN 14604:2006; PN-EN IEC 61439-3:2025-09; PN-EN 61082-1:2015-03. Normy wycofane
przywoływane wyłącznie z podaniem statusu: PN-HD 60364-5-534:2012/2016-04 (zastąpiona przez PN-HD
60364-5-53:2022-10 — dobór SPD wg wydania aktualnego), PN-86/E-05003/01 (źródło historycznej mapy N_G —
dane informacyjne). Wartości tablicowe
z literatury (obciążalności wg PN-HD 60364-5-52 zał. B, spadki napięć wg N SEP-E-002) oznaczono w obliczeniach
[NZW] — do potwierdzenia z tekstem norm przed wydaniem do realizacji (D-19).

**Materiały wyjściowe:** PZT i PAB (tom I), PT-1 AR, PT-2 BO (zbrojenie i uziom), PT-3 IS (moc pompy ciepła,
centrali, grzałki; charakterystyka energetyczna), model `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`,
`wyposazenie.yaml` (stan z 2026-09-25 10:33); dane PVGIS 5.3 (JRC) dla Poznania. Warunki przyłączenia OSD — [DANE PRZYKŁADOWE – FIKCYJNE]
(moc przyłączeniowa i parametry sieci jako [ZAŁ], E-05).

## Zasilanie i powiązanie z siecią elektroenergetyczną — § 23 pkt 8 RPB; W-192, W-193

**Źródło zasilania.** Sieć nN 0,4 kV operatora systemu dystrybucyjnego (układ TN-C) — kabel w ulicy wg PZT.
Przyłącze kablowe i złącze kablowo-pomiarowe (ZKP) wykonuje OSD na podstawie warunków przyłączenia
[DO UZUPEŁNIENIA: nr i data warunków przyłączenia OSD]. ZKP: złącze kablowo-pomiarowe we wnęce ogrodzenia, PWP przy wejściu (W-190).
Pole odczytowe licznika ≥ 0,48 m nad terenem (W-192).

**Parametry przyłączenia [ZAŁ — do potwierdzenia w warunkach przyłączenia, [DANE PRZYKŁADOWE – FIKCYJNE]]:** moc przyłączeniowa
**27 kW**, zabezpieczenie przedlicznikowe **C40**
(3-fazowe), grupa przyłączeniowa V (≤ 1 kV, ≤ 40 kW — RSys § 3 ust. 1 pkt 5), pomiar bezpośredni, licznik
3-fazowy dwukierunkowy (mikroinstalacja PV — zgłoszenie do OSD, W-194); impedancja pętli zwarcia w ZKP
Z_Q = 0,30 Ω, prąd zwarciowy w ZKP ≤ 6 kA.

**Wewnętrzna linia zasilająca (WLZ)** ZKP → RG: kabel **YKY 5×25** 0,6/1 kV, długość obliczeniowa
L = 28,3 m (trasa w terenie wg PZT 18,2 m + podejście w budynku i zapasy), obciążalność
I_z = 82,0 A (metoda D1), spadek napięcia przy prądzie zabezpieczenia przedlicznikowego
∆U = 0,37 % (temperatura robocza). Kabel w ziemi na głębokości ≥ 0,7 m w piasku z taśmą ostrzegawczą
niebieską, pod utwardzeniami i przy wejściu do budynku w rurze osłonowej; przejście przez ścianę/płytę poniżej
terenu gazoszczelne (W-214). Trasa w terenie: ZKP w linii ogrodzenia (pole odczytowe ≥ 0,48 m nad terenem) → WLZ YKY 5×25 do RG w pom. 0.12, rura osłonowa pod podjazdem/garażem.

**Układ sieci w budynku: TN-S** — oddzielne przewody ochronny PE i neutralny N w obwodach rozdzielczych
i odbiorczych (WT § 183 ust. 1 pkt 2). Rozdział PEN — preferowany w ZKP z WLZ 5-żyłowym (wymaga zgody OSD);
wariant zapasowy: WLZ 4-żyłowy (PEN) i rozdział w RG na głównej szynie uziemiającej (D-12, W-193).
Punkt rozdziału PEN uziemić (połączenie z GSU i uziomem).

**Rozdzielnica główna RG** — 0.12 Pomieszczenie techniczne (współrzędne w modelu: 15,05; 0,90; P0),
obudowa wg PN-EN IEC 61439-3, stopień ochrony ≥ IP40 (pomieszczenie suche), rezerwa miejsca ≥
20 % modułów. Aparat główny: rozłącznik izolacyjny 3P z wyzwalaczem przeciwpożarowego
wyłącznika prądu (PWP); ochronniki przepięć typu 1+2 (T1+T2) na wejściu; zabezpieczenia obwodów odbiorczych —
wyłączniki nadprądowo-różnicowoprądowe (RCBO) i wyłączniki nadprądowe z RCD (obwody 3-fazowe).

## Instalacje elektroenergetyczne — § 23 pkt 7 lit. g RPB; WT § 180–§ 192; W-180…W-190

Instalację podzielono na **35 obwodów odbiorczych** wydzielonych zgodnie z WT § 188 ust. 2:
oświetlenie — 5, gniazda ogólnego przeznaczenia (w tym garaż i gniazda zewnętrzne) —
7, gniazda kuchenne — 2, gniazda w łazienkach — 5,
odbiorniki wymagające indywidualnego zabezpieczenia — 16. Przyporządkowanie obwodów do faz wyrównuje obciążenie
(asymetria mocy szczytowej 0,4 %). Zestawienie obwodów — tabela poniżej; pełne
obliczenia (I_B, I_z, ∆U, Z_s, I_k1) — rozdz. „Obliczenia”; schemat — arkusz PT-IE-14.

**Tabela 2. Obwody odbiorcze rozdzielnicy głównej RG**

| Obw. | Przeznaczenie | Faza | P [kW] | Zabezp. | Ochrona różnicowoprądowa | Przewód | L [m] | ∆U_c [%] |
|---|---|---|---|---|---|---|---|---|
| L1 | Oświetlenie P0 | L1 | 0,56 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 15,82 | 0,79 |
| L2 | Oświetlenie P1 | L2 | 0,43 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 15,89 | 0,70 |
| L3 | Oświetlenie P2 | L3 | 0,33 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 27,77 | 0,81 |
| L4 | Oświetlenie garażu i pom. technicznego | L1 | 0,26 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 5,52 | 0,44 |
| L5 | Oświetlenie zewnętrzne (wejście, elewacje, taras) | L1 | 0,20 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 16,78 | 0,53 |
| G1 | Gniazda P0: 0.10 Pokój gościnny / gabinet, 0.08 Przedpokój gościnny… | L1 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 5,56 | 1,02 |
| G2 | Gniazda P1: 1.04 Pokój dziecka 2, 1.03 Pokój dziecka 1, 1.09 Szacht i… | L3 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×4 | 22,83 | 1,97 |
| G3 | Gniazda P1: 1.02 Pokój rodzinny / biblioteka (boks C) | L2 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 15,89 | 2,22 |
| G4 | Gniazda P2: 2.02 Sypialnia rodziców, 2.03 Garderoba (przedpokój apart… | L1 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 22,29 | 2,96 |
| G5 | Gniazda P2: 2.05 Gabinet / pokój gościnny okazjonalny | L3 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 17,07 | 2,35 |
| G6 | Gniazda kuchenne 1 (0.06 Salon + jadalnia + kuchnia) | L1 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 15,82 | 2,21 |
| G7 | Gniazda kuchenne 2 (0.06 Salon + jadalnia + kuchnia) | L3 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 15,82 | 2,21 |
| G8 | Gniazda łazienki (0.03 WC gościnne) | L2 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 18,14 | 2,48 |
| G9 | Gniazda łazienki (0.09 Łazienka gościnna (natrysk)) | L1 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×4 | 23,22 | 1,99 |
| G10 | Gniazda łazienki (1.05 Łazienka dzieci (wanna)) | L3 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×4 | 25,84 | 2,18 |
| G11 | Gniazda łazienki (1.07 WC z natryskiem) | L2 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 20,41 | 2,74 |
| G12 | Gniazda łazienki (2.04 Łazienka rodziców) | L1 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×4 | 28,99 | 2,40 |
| G13 | Gniazda garażu / pom. technicznego (IP44) | L2 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 5,52 | 1,01 |
| G14 | Gniazda zewnętrzne (taras, ogród; IP44/IP54) | L3 | 2,00 | B16 | RCBO typ A 30 mA | YDYp 3×4 | 27,55 | 2,30 |
| D1 | Płyta indukcyjna | L1L2L3 | 7,40 | 3P B16 | RCD 4P 40 A/30 mA typ A | YDYp 5×2,5 | 11,34 | 0,80 |
| D2 | Piekarnik | L2 | 3,50 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 15,82 | 2,11 |
| D3 | Zmywarka | L3 | 2,20 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 7,99 | 0,90 |
| D4 | Pralka | L2 | 2,20 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 21,03 | 1,77 |
| D5 | Suszarka | L3 | 2,50 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 20,25 | 1,92 |
| D6 | Pompa ciepła — jednostka zewnętrzna (PC-R290-07 (przykład)) | L1 | 2,67 | C16 | RCD typ F/B 30 mA wg DTR (falownik sprężarki) | YDYp 3×2,5 | 9,44 | 1,15 |
| D7 | Grzałka rezerwowa PC / zasobnika c.w.u. (6,0 kW) | L1L2L3 | 6,00 | 3P B10 | RCD 4P 40 A/30 mA typ A | YDYp 5×2,5 | 6,60 | 0,57 |
| D8 | Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego | L3 | 0,30 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 6,60 | 0,47 |
| D9 | Rekuperator (V ≈ 365 m³/h) | L2 | 0,10 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 20,48 | 0,47 |
| D10 | Falownik PV 3f (6,0 kW AC) | L1L2L3 | 6,00 | 3P B16 | RCD typ B 30 mA (lub wg 712.530.3.101 — DTR falownika) | YDYp 5×2,5 | 3,00 | 0,46 |
| D11 | Ładowarka EV 11 kW (3f) — garaż; przewód na 22 kW | L1L2L3 | 11,00 | 3P C20 | własny RCD typ B 30 mA lub A-EV + RDC-DD 6 mA DC | YDY 5×6 | 9,57 | 0,59 |
| D12 | Napęd bramy garażowej | L3 | 0,30 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 13,41 | 0,57 |
| D13 | Brama wjazdowa, furtka, wideodomofon (linia ogrodzenia) | L3 | 0,50 | B16 | RCBO typ A 30 mA | YKY 3×2,5 | 23,22 | 0,70 |
| D14 | Teletechnika: ONT, router, szafka RACK, SSWiN | L2 | 0,20 | B16 | RCBO typ A 30 mA | YDYp 3×2,5 | 3,00 | 0,39 |
| D15 | Pompa zbiornika wody deszczowej (podlewanie) | L1 | 0,80 | B16 | RCBO typ A 30 mA | YKY 3×2,5 | 25,74 | 0,95 |
| D16 | Napędy osłon przeciwsłonecznych (19 szt.) | L2 | 1,90 | B10 | RCBO typ A 30 mA | YDYp 3×1,5 | 3,00 | 0,66 |

∆U_c — spadek napięcia od ZKP do najdalszego odbiornika obwodu (WLZ + obwód), temperatura robocza żył.

*Źródło: lamela.obliczenia.elektryka.obwody (obwody z modelu: pomieszczenia, wyposażenie, instalacje.yaml)*

### Oświetlenie — WT § 64, § 102, § 188 ust. 2, § 189; W-183

Obwody oświetleniowe: L1 — Oświetlenie P0 (B10, YDYp 3×1,5), L2 — Oświetlenie P1 (B10, YDYp 3×1,5), L3 — Oświetlenie P2 (B10, YDYp 3×1,5), L4 — Oświetlenie garażu i pom. technicznego (B10, YDYp 3×1,5), L5 — Oświetlenie zewnętrzne (wejście, elewacje, taras) (B10, YDYp 3×1,5).
Oprawy LED (moc obliczeniowa wg wskaźnika z obliczeń bilansu), w pomieszczeniach mieszkalnych łączniki
wieloobwodowe; w pokoju o powierzchni do 20 m² co najmniej jeden wypust oświetleniowy, w większym — co najmniej
dwa (W-183). Oświetlenie zewnętrzne wejścia do budynku (WT § 64) i oświetlenie garażu (WT § 102) na obwodach
wydzielonych; oprawy zewnętrzne ≥ IP44 (PN-HD 60364-7-714). Obwody oświetleniowe chronione RCD 30 mA
(PN-HD 60364-4-41:2017-09 p. 411.3.4 — lokal jednego gospodarstwa domowego). Rozmieszczenie — arkusze
PT-IE-01, PT-IE-02, PT-IE-03.

### Gniazda wtyczkowe, łazienki — WT § 188 ust. 2; PN-HD 60364-7-701:2025-02; W-181, W-189

Gniazda wtyczkowe 16 A z bolcem ochronnym, w obwodach 16 A (przekroje 2,5–4 mm² dobrane z warunku spadku
napięcia), każdy obwód z RCD I_∆n = 30 mA typu A (typ AC niedopuszczalny, W-181). Gniazda kuchenne — dwa obwody
wydzielone; gniazda zewnętrzne i w garażu ≥ IP44. Łazienki (0.03 WC gościnne; 0.09 Łazienka gościnna (natrysk; 1.05 Łazienka dzieci (wanna; 1.07 WC z natryskiem; 2.04 Łazienka rodziców) — obwody wydzielone;
osprzęt w strefach 1–2 co najmniej IPX4, bez gniazd i łączników w strefach 0–2 (wymiary stref wg
PN-HD 60364-7-701:2025-02; W-189); miejscowe połączenia wyrównawcze — wg tej normy (przy instalacjach
z tworzyw sztucznych zwykle niewymagane). Rozmieszczenie — arkusze PT-IE-04, PT-IE-05, PT-IE-06.

### Zasilanie urządzeń — § 23 pkt 8 lit. b RPB; WT § 188 ust. 2

**Tabela 3. Urządzenia zasilane z obwodów wydzielonych**

| Obw. | Urządzenie | P [kW] | Fazy | I_B [A] | Zabezp. | Przewód | Ochrona różnicowoprądowa |
|---|---|---|---|---|---|---|---|
| D1 | Płyta indukcyjna | 7,40 | 3 | 10,68 | 3P B16 | YDYp 5×2,5 | RCD 4P 40 A/30 mA typ A |
| D2 | Piekarnik | 3,50 | 1 | 15,22 | B16 | YDYp 3×2,5 | RCBO typ A 30 mA |
| D3 | Zmywarka | 2,20 | 1 | 10,07 | B16 | YDYp 3×2,5 | RCBO typ A 30 mA |
| D4 | Pralka | 2,20 | 1 | 10,07 | B16 | YDYp 3×2,5 | RCBO typ A 30 mA |
| D5 | Suszarka | 2,50 | 1 | 11,44 | B16 | YDYp 3×2,5 | RCBO typ A 30 mA |
| D6 | Pompa ciepła — jednostka zewnętrzna (PC-R290-07 (przykład)) | 2,67 | 1 | 12,22 | C16 | YDYp 3×2,5 | RCD typ F/B 30 mA wg DTR (falownik sprężarki) |
| D7 | Grzałka rezerwowa PC / zasobnika c.w.u. (6,0 kW) | 6,00 | 3 | 8,66 | 3P B10 | YDYp 5×2,5 | RCD 4P 40 A/30 mA typ A |
| D8 | Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego | 0,30 | 1 | 1,37 | B10 | YDYp 3×1,5 | RCBO typ A 30 mA |
| D9 | Rekuperator (V ≈ 365 m³/h) | 0,10 | 1 | 0,47 | B10 | YDYp 3×1,5 | RCBO typ A 30 mA |
| D10 | Falownik PV 3f (6,0 kW AC) | 6,00 | 3 | 8,66 | 3P B16 | YDYp 5×2,5 | RCD typ B 30 mA (lub wg 712.530.3.101 — DTR falownika) |
| D11 | Ładowarka EV 11 kW (3f) — garaż; przewód na 22 kW | 11,00 | 3 | 16,04 | 3P C20 | YDY 5×6 | własny RCD typ B 30 mA lub A-EV + RDC-DD 6 mA DC |
| D12 | Napęd bramy garażowej | 0,30 | 1 | 1,37 | B10 | YDYp 3×1,5 | RCBO typ A 30 mA |
| D13 | Brama wjazdowa, furtka, wideodomofon (linia ogrodzenia) | 0,50 | 1 | 2,29 | B16 | YKY 3×2,5 | RCBO typ A 30 mA |
| D14 | Teletechnika: ONT, router, szafka RACK, SSWiN | 0,20 | 1 | 0,92 | B16 | YDYp 3×2,5 | RCBO typ A 30 mA |
| D15 | Pompa zbiornika wody deszczowej (podlewanie) | 0,80 | 1 | 3,66 | B16 | YKY 3×2,5 | RCBO typ A 30 mA |
| D16 | Napędy osłon przeciwsłonecznych (19 szt.) | 1,90 | 1 | 8,70 | B10 | YDYp 3×1,5 | RCBO typ A 30 mA |

Moc pompy ciepła, grzałki i centrali wentylacyjnej — z doboru w PT-3 IS (moduły ogrzewania i wentylacji); typ RCD dla urządzeń z przekształtnikami (PC, falownik PV, ładowarka EV) — wg DTR.

*Źródło: lamela.obliczenia.elektryka.bilans (odbiorniki z modelu) i obwody*

### Przewody, osprzęt, sposób wykonania — WT § 183 ust. 1 pkt 8–9, § 187; W-184, W-198

Przewody o żyłach miedzianych (WT § 183 ust. 1 pkt 9), izolacja 450/750 V; w ścianach pod tynkiem (grubość tynku
nad przewodem ≥ 5 mm), w stropach monolitycznych i w warstwach posadzkowych — w rurach osłonowych umożliwiających
wymianę przewodów (WT § 187); trasy równoległe do krawędzi ścian i stropów (WT § 183 ust. 1 pkt 8); przekrój
minimalny 1,5 mm² (obwody siłowe i oświetleniowe). Kable w ziemi YKY 0,6/1 kV w rurach osłonowych. Przejścia
przez przegrody oddzielenia pożarowego — nie występują (jedna strefa pożarowa). Puszki instalacyjne w ścianach
z płyt g-k i w warstwie izolacji — szczelne powietrznie (ciągłość warstwy szczelności — PT-1 AR).
Zaleca się urządzenia do detekcji zwarć łukowych (AFDD, PN-HD 60364-4-42) w obwodach sypialni (W-198 —
zalecenie, nieobowiązkowe).

## Mikroinstalacja fotowoltaiczna — PN-HD 60364-7-712:2016-05; W-194

**Zakres i status formalny.** 15 modułów o mocy 430 Wp — moc zainstalowana
**6,45 kWp** (suma mocy z tabliczek modułów) ≤ 6,5 kWp,
falownik 3-fazowy 6,0 kW ≤ 6,5 kW — mikroinstalacja (≤
50 kW) przyłączana na zgłoszenie do OSD (Pr. energ. art. 7 ust. 8d4); przy mocy
≤ 6,5 kW bez uzgodnienia z rzeczoznawcą ds. zabezpieczeń przeciwpożarowych
i zawiadomienia PSP (PB art. 29 ust. 4 pkt 3 lit. c; W-194). Moc mikroinstalacji ≤ mocy przyłączeniowej
(27 kW). Magazyn energii — nie przewiduje się (rezerwa w RG).

**Rozmieszczenie.** Dach D1 (płaski, powierzchnia 87,4 m², użytkowa po odjęciu
strefy brzegowej 47,2 m²), układ EW10; moduły nie wystają ponad attykę
(0,35 m). Konstrukcja balastowa bez przebijania pokrycia (obciążenie dachu — PT-2 BO;
zabezpieczenie przed wiatrem wg PN-EN 1991-1-4). Rozmieszczenie — arkusze PT-IE-10, PT-IE-11.

**Łańcuchy i strona DC.** 2 łańcuchy
(8 + 7 modułów; po jednym na wejście MPPT) — maksymalne napięcie łańcucha w temperaturze minimalnej
U_oc,max = 350 V, zakres napięć MPP 196–298 V
(mieści się w zakresie MPPT falownika 160–950 V);
bez bezpieczników łańcuchowych (jeden łańcuch na MPPT).
Przewody DC H1Z2Z2-K (PN-EN 50618) 10 mm², trasa dach → falownik L = 21,9 m,
prowadzone parami (małe pętle indukcyjne), w osłonach odpornych na UV; spadek napięcia DC 0,62 %.
SPD DC typ 2, U_CPV ≥ 350 V (klasa 1000 V DC) przy falowniku — wbudowany w falownik (sprawdzić DTR); rozłącznik izolacyjny DC ≥ 350 V, ≥ 17,5 A (zwykle wbudowany w falownik). Długość krytyczna DC dla SPD L_crit = 63,9 m.

**Strona AC.** Obwód D10 w RG: 3P B16, YDYp 5×2,5,
RCD typ B 30 mA (lub wg 712.530.3.101 — DTR falownika). Falownik z certyfikatem zgodności z NC RfG (rozp. (UE) 2016/631) i nastawami wg
PN-EN 50549-1 oraz wymagań OSD; zabezpieczenie przed pracą wyspową wbudowane. Przeciwpożarowy wyłącznik prądu
odcina stronę AC falownika; strona DC pozostaje pod napięciem — tabliczki ostrzegawcze przy RG, PWP i falowniku.
Konstrukcja PV uziemiona w jednym punkcie i połączona z GSU (712.444.5.5.101).

**Produkcja energii** (PVGIS 5.3, Poznań): E = 5 610 kWh/rok; autokonsumpcja (bilans godzinowy)
65,1 %, pokrycie zużycia 32,9 %; energia PV zużyta przez
systemy techniczne (ogrzewanie, c.w.u., pomocnicze) 2 453
kWh/rok — wartości informacyjne doboru instalacji. Charakterystyka energetyczna (PT-3 IS) przyjmuje wg
metodologii świadectw produkcję E_PV = 4 985 kWh/rok i energię zużytą przez systemy techniczne
E_PV,sys = 2 339 kWh/rok (inne dane klimatyczne i model autokonsumpcji); dla wskaźnika EP
wiążące są wartości PT-3 IS. Odbiór: PN-EN 62446-1 (rozdz. „Próby”).

## Punkt ładowania pojazdu elektrycznego — PN-HD 60364-7-722:2019-01; W-195

Obowiązek wyposażenia budynku jednorodzinnego w punkt ładowania nie wynika z ustawy o elektromobilności (W-195).
Projektuje się **obwód wydzielony D11** — Ładowarka EV 11 kW (3f) — garaż; przewód na 22 kW: moc 11,0 kW, I_B = 16,0 A,
zabezpieczenie 3P C20, przewód YDY 5×6 (L = 9,6 m, ∆U_c = 0,59 %), ochrona
różnicowoprądowa: własny RCD typ B 30 mA lub A-EV + RDC-DD 6 mA DC. Punkt ładowania (tryb 3, PN-EN IEC 61851-1) objęty dynamicznym zarządzaniem mocą
(DLM) — ograniczenie prądu ładowania przy przekroczeniu mocy przyłączeniowej (rozdz. „Bilans mocy”). Obwód nie
może pracować w układzie TN-C; osobny RCD dla każdego punktu przyłączenia (722.531.2).

Miejsca postojowe w PZT: 4 (MP1 — garaż, MP2 — garaż, MP3 — zewnętrzne, MP4 — zewnętrzne).
Przy liczbie miejsc > 3 dyrektywa EPBD (UE) 2024/1275 art. 14 ust. 4 — nietransponowana, stosowana dobrowolnie — przewiduje okablowanie wstępne ≥ 50 % miejsc (tu 2) i kanały kablowe dla pozostałych: projektuje się rurę osłonową do miejsc zewnętrznych i rezerwę w RG na drugi punkt ładowania.

## Instalacje telekomunikacyjne — § 23 pkt 7 lit. h RPB; rozp. (UE) 2024/1309 art. 10; W-196

**Autor.** Rozdział i arkusze PT-IE-07, PT-IE-08, PT-IE-09 opracowuje współautor tomu ze specjalnością
instalacyjną w zakresie sieci, instalacji i urządzeń telekomunikacyjnych bez ograniczeń (PB art. 15a ust. 18)
— [DO UZUPEŁNIENIA: imię i nazwisko, nr uprawnień]; zasilanie urządzeń teletechnicznych z instalacji
elektrycznej (obwód, zabezpieczenie) i połączenia wyrównawcze — projektant instalacji elektrycznych.

**Przyłącze światłowodowe.** Budynek wyposaża się w infrastrukturę fizyczną przystosowaną do sieci światłowodowej
i okablowanie światłowodowe do punktu zakończenia sieci (rozp. (UE) 2024/1309 art. 10 ust. 1 — wniosek o pozwolenie
na budowę po 12.02.2026; W-196). Kanalizacja od granicy działki do budynku: 2 × HDPE Ø40 + mikrokabel światłowodowy (W-196), długość
21,3 m (wg PZT); wprowadzenie do budynku gazoszczelne (W-214). Kabel światłowodowy jednomodowy
≥ 2 włókna, złącza SC/APC, tłumienie toru ≤
1,2 dB (dobra praktyka — W-196). Punkt zakończenia sieci (ONT)
w szafie teleinformatycznej; przyłącze wykonuje operator wg warunków technicznych
[DO UZUPEŁNIENIA: operator i nr warunków technicznych przyłączenia telekomunikacyjnego].

**Instalacja wewnętrzna.** Okablowanie strukturalne w topologii gwiazdy od szafy teleinformatycznej (RACK):
skrętka kat. 6A U/FTP do gniazd RJ45, punkty dostępowe Wi-Fi zasilane PoE, instalacja RTV/SAT, wideodomofon
i system sygnalizacji włamania i napadu (SSWiN, stopień 2 wg PN-EN 50131-1) — wg PN-EN 50173-4:2018-07
(okablowanie w domach) i PN-EN 50174-2:2018-08 (instalowanie), połączenia wyrównawcze wg PN-EN 50310:2016-09.
Przewody w rurach osłonowych, w odległości ≥ 0,1 m od przewodów elektroenergetycznych (albo z przegrodą);
obudowa szafy objęta połączeniami wyrównawczymi (WT § 183 ust. 1a pkt 8). Zasilanie szafy: obwód
D14 (B16, YDYp 3×2,5). Światłowód dielektryczny nie wymaga
SPD; linie miedziane wchodzące do budynku (antena, wideodomofon) — SPD na wejściu. Rozmieszczenie — arkusze
PT-IE-07, PT-IE-08, PT-IE-09.

## Instalacja piorunochronna, uziom i połączenia wyrównawcze — § 23 pkt 7 lit. i RPB; WT § 53 ust. 2, § 184; W-187, W-188, W-191

### Ocena ryzyka piorunowego — PN-EN 62305-2:2008 (zał. 1 WT); W-191

Potrzebę instalacji piorunochronnej (WT § 53 ust. 2, § 184 ust. 3) oceniono metodą analizy ryzyka utraty życia
R1 wg PN-EN 62305-2:2008 (norma wycofana; wydanie powołane w zał. 1 WT, stosowane na podstawie art. 102a PB;
ryzyko tolerowane i klasy ryzyka pożaru — jak w wydaniu PN-EN 62305-2:2012, również wycofanym): wysokość budynku
H = 10,23 m, powierzchnia zbierania wyładowań A_D = 4 281 m², gęstość wyładowań
N_G = 1,8 1/(km²·rok) [NZW] (dane SEP z mapy PN-86/E-05003/01 — norma wycofana, dane
historyczne; aktualizacja z danych systemu detekcji wyładowań — do potwierdzenia), liczba wyładowań w obiekt N_D = 0,0077 1/rok, w linię zasilającą
N_L = 0,0180 1/rok; ryzyko tolerowane R_T = 1,00·10⁻⁵ 1/rok. Klasę ryzyka pożaru przyjęto z gęstości
obciążenia ogniowego (progi 400 / 800 MJ/m²)
— rozstrzygające są oba warianty klasy.

**Tabela 4. Ryzyko R1 w scenariuszach ochrony**

| Scenariusz | Klasa pożarowa | R1 [1/rok] | R1 ≤ R_T |
|---|---|---|---|
| brak ochrony | zwykłe | 5,14·10⁻⁶ | tak |
| brak ochrony | wysokie | 2,83·10⁻⁵ | NIE |
| SPD typ 1 (LPL III–IV) — projektowane (W-186) | zwykłe | 1,72·10⁻⁶ | tak |
| SPD typ 1 (LPL III–IV) — projektowane (W-186) | wysokie | 9,47·10⁻⁶ | tak |
| SPD T1 + gaśnica (r_p = 0,5) | zwykłe | 1,29·10⁻⁶ | tak |
| SPD T1 + gaśnica (r_p = 0,5) | wysokie | 5,16·10⁻⁶ | tak |
| LPS IV + SPD T1 | zwykłe | 4,88·10⁻⁷ | tak |
| LPS IV + SPD T1 | wysokie | 2,69·10⁻⁶ | tak |
| LPS III + SPD T1 | zwykłe | 3,34·10⁻⁷ | tak |
| LPS III + SPD T1 | wysokie | 1,84·10⁻⁶ | tak |

*Źródło: lamela.obliczenia.elektryka.odgromowa*

> Decyzja: LPS NIEWYMAGANY (R1 ≤ R_T przy SPD T1 dla obu klas obciążenia ogniowego). Uziom wykonuje się z wyprowadzeniami pod przewody odprowadzające (rezerwa na LPS klasy IV); w RG ochronniki przepięć typu 1+2 (warunek scenariusza).

**Wydanie aktualne PN-EN IEC 62305-2:2025-09 — sprawdzenie kontrolne pominięto (uzasadnienie).** Rejestr
wymagań (A.1 pkt 5) przewiduje stosowanie wydania powołanego w WT obok wydania aktualnego. Sprawdzenia
kontrolnego wg wydania 2025 nie wykonano, ponieważ: (1) obowiązek wykonania instalacji piorunochronnej wynika
z WT § 53 ust. 2 i § 184 ust. 3 w związku z normą powołaną w zał. 1 WT — rozstrzyga ocena wykonana powyżej;
(2) PN-EN IEC 62305-2:2025-09 jest dostępna wyłącznie w języku angielskim, a jej metodyka nie jest ujęta
w obliczeniach projektu (rejestr R7-A05, D-13) — obliczenie „kontrolne” bez tekstu normy nie byłoby
sprawdzeniem; (3) rozwiązania tomu nie zależą od wyniku: uziom z wyprowadzeniami pod przewody odprowadzające,
ochronniki typu 1+2 w RG oraz parametry LPS klasy IV (podrozdział „Parametry LPS (rezerwa)”)
pozwalają wykonać LPS bez zmian konstrukcji i instalacji. Jeżeli ocena wg wydania 2025 wykaże R1 > R_T,
LPS wykonuje się wg podrozdziału „Parametry LPS (rezerwa)” —
[DO UZUPEŁNIENIA: decyzja projektanta o sprawdzeniu wg PN-EN IEC 62305-2:2025-09 przed realizacją].

### Uziom — WT § 184 ust. 1; PN-HD 60364-5-54 zał. C; W-187

Typ: **otokowy w gruncie (fundament izolowany termicznie — PN-HD 60364-5-54 zał. C.2)**. Materiał: drut/płaskownik Cu 50 mm² lub StCu Ø10 mm lub StSt 30×3,5 mm, ≥ 0,5 m w gruncie, ≥ 1 m od ścian [ZAŁ]. Średnica zastępcza obrysu D = 17,89 m, rezystancja
orientacyjna R ≈ 14,9 Ω (rezystywność gruntu [ZAŁ]) — wartość do potwierdzenia pomiarem po wykonaniu.
Wyprowadzenia: GSU w pomieszczeniu technicznym (≥ 16 mm² Cu, W-188); ZKP / rozdział PEN (jeśli wymaga OSD); 4 wyprowadzenia w narożnikach/co ≤ 15 m pod przewody odprowadzające LPS (rezerwa); konstrukcja PV (połączenie wyrównawcze, jeden punkt). Przy uziomie w betonie: otulina ≥
5 cm, płaskownik na sztorc mocowany do zbrojenia co ≤
2,0 m (W-187; koordynacja z PT-2 BO).
Plan uziomu — arkusz PT-IE-12.

### Połączenia wyrównawcze — WT § 183 ust. 1 pkt 7, ust. 1a; PN-HD 60364-5-54; W-188

**Tabela 5. Połączenia wyrównawcze główne i miejscowe**

| Element | Miejsce | Przekrój / uwagi |
|---|---|---|
| Główna szyna uziemiająca (GSU) | pomieszczenie techniczne, przy RG | przewód uziemiający ≥ 16 mm² Cu (W-188) |
| Wodociąg metalowy (przed/za wodomierzem — mostek) | zestaw wodomierzowy | ≥ 6 mm² Cu (tylko przy rurach przewodzących) |
| Rury c.o./c.w.u. metalowe, zasobnik, bufor | pom. techniczne | ≥ 6 mm² Cu |
| Kanały wentylacyjne metalowe, obudowa rekuperatora | — | ≥ 6 mm² Cu (WT §183 ust. 1a) |
| Zbrojenie fundamentów / płyty | zaciski przyłączeniowe | ≥ 16 mm² Cu / Ø10 Fe |
| Konstrukcja PV (uziemienie funkcjonalne, jeden punkt) | dach | wg DTR i 5-54 (≥ 6 mm² Cu) (712.444.5.5.101) |
| Obudowa szafki teletechnicznej / RACK | — | ≥ 6 mm² Cu (WT §183 ust. 1a pkt 8) |
| Łazienki — miejscowe połączenia wyrównawcze | łazienki | wg PN-HD 60364-7-701:2025-02 (przy tworzywach zwykle niewymagane) |
| Balustrady, lamele stalowe/aluminiowe na elewacji, stolarka metalowa przy zwodach | — | przy LPS — w strefie odstępu separacyjnego |

Przewód uziemiający ≥ 16 mm² Cu; przewody wyrównawcze główne ≥ 6 mm² Cu i nie więcej niż 25 mm² Cu (W-188).

*Źródło: lamela.obliczenia.elektryka.odgromowa*

### Parametry LPS (rezerwa) — PN-EN 62305-3:2011 (wycofana, powołana w WT)

Gdyby Inwestor zdecydował o wykonaniu LPS (np. po zmianie wyposażenia lub klasy pożarowej): klasa
IV, oczka zwodów 20 × 20 m (III: 15 × 15 m), promień kuli toczącej 60 m (III: 45 m), przewody odprowadzające:
klasa III — 4, klasa IV — 3; odstęp separacyjny instalacji na dachu (PV)
od zwodów s ≈ 0,27 m [NZW]. zwody poziome na attykach i w oczkach na dachach płaskich; iglice przy wywiewkach/czerpniach/PV; przewody odprowadzające w elewacji (pod okładziną w rurach niepalnych) do złączy kontrolnych i uziomu otokowego Arkusz PT-IE-13 pokazuje wyprowadzenia
uziomu i połączenia wyrównawcze na dachu.

## Ochrona przeciwporażeniowa i przeciwprzepięciowa — WT § 183 ust. 1 pkt 3, 10; PN-HD 60364-4-41, -4-443; W-181, W-182, W-186

**Ochrona podstawowa** — izolacja części czynnych, obudowy i osłony (PN-HD 60364-4-41 zał. A).
**Ochrona przy uszkodzeniu** — samoczynne wyłączenie zasilania w układzie TN-S: dla obwodów odbiorczych
230 V czas wyłączenia ≤ 0,4 s (tabl. 41.1), sprawdzony
warunkiem I_k1 ≥ I_a (I_a — prąd zadziałania członu zwarciowego wyłącznika: 5·I_n dla B, 10·I_n dla C).
Najmniejszy zapas: obwód D11 — I_k1 = 528 A ≥ I_a = 200 A
(I_k1/I_a = 2,64); największa impedancja pętli zwarcia: obwód L3 —
Z_s = 1,132 Ω (temperatura żył 70 °C, c_min = 0,95). **Ochrona uzupełniająca** — urządzenia
różnicowoprądowe I_∆n ≤ 30 mA w obwodach gniazd ≤ 32 A,
oświetlenia, łazienek i urządzeń na zewnątrz (411.3.3–411.3.4, W-181); typ AC niedopuszczalny.
Zastosowane rodzaje: RCBO typ A 30 mA — 30 obwodów; RCD 4P 40 A/30 mA typ A — 2 obwody; RCD typ F/B 30 mA wg DTR (falownik sprężarki) — 1 obwód; RCD typ B 30 mA (lub wg 712.530.3.101 — DTR falownika) — 1 obwód; własny RCD typ B 30 mA lub A-EV + RDC-DD 6 mA DC — 1 obwód.
Połączenia wyrównawcze — rozdz. „Instalacja piorunochronna, uziom i połączenia wyrównawcze”.

**Selektywność** (WT § 183 ust. 1 pkt 5): przeciążeniowa zapewniona (I_n zabezpieczenia przedlicznikowego / I_n
obwodu ≥ 1,6); zwarciowa — częściowa, do granicy wynikającej z tabel producenta aparatów (zestawienie w obliczeniach
obwodów); aparat główny RG — rozłącznik (nie wyzwala przy zwarciu).

**Ochrona przed przepięciami** (WT § 183 ust. 1 pkt 10 — obowiązkowa; PN-HD 60364-4-443:2016-03 p. 443.5):
obliczeniowy poziom ryzyka CRL = f_env/(L_P·N_g) = 315 < 1 000
(f_env = 170, L_P = 0,30 km, N_g = 1,8) — ochrona wymagana także
z warunku normy. W RG: SPD typ 1+2 (T1+T2), I_imp ≥ 12,5 kA/biegun, U_p ≤ 1,5 kV, U_c ≥ 275 V; układ 3+1 (TN-S) lub 4+0 przy rozdziale PEN w RG. Dalej: SPD typ 2 DC przy falowniku (U_CPV ≥ U_oc,max łańcucha) — jeśli nie wbudowany w falownik; SPD na wejściu linii miedzianych / antenowych (światłowód dielektryczny — bez SPD); ochrona lokalna T3 przy RACK i sterowniku PC (opcjonalnie).
Kategorie wytrzymałości udarowej: złącze — IV (6 kV), RG i oprzewodowanie — III (4 kV), odbiorniki — II (2,5 kV),
elektronika chroniona — I (1,5 kV); U_p ochronników w RG ≤ 2,5 kV (W-186).

## Bilans mocy — § 23 pkt 11 lit. a RPB; § 23 pkt 8 lit. b RPB; W-192

Bilans obejmuje urządzenia elektryczne stanowiące stałe wyposażenie budowlano-instalacyjne budynku; urządzeń
technologicznych nie ma (budynek mieszkalny jednorodzinny). Moc szczytową wyznaczono ze współczynników
jednoczesności k_j [ZAŁ] dla grup odbiorników; mikroinstalacja PV (generacja) nie pomniejsza bilansu poboru.

**Tabela 6. Bilans mocy — grupy odbiorników**

| Grupa odbiorników | Obwody | P_i [kW] | k_j | P_s [kW] | DLM |
|---|---|---|---|---|---|
| oświetlenie | L1, L2, L3, L4, L5 | 1,77 | 0,70 | 1,24 | — |
| gniazda ogólne | G1, G2, G3, G4, G5, G13 | 12,00 | 0,20 | 2,40 | — |
| gniazda kuchenne | G6, G7 | 4,00 | 0,50 | 2,00 | — |
| gniazda w łazienkach | G8, G9, G10, G11, G12 | 10,00 | 0,30 | 3,00 | — |
| gniazda zewnętrzne | G14 | 2,00 | 0,30 | 0,60 | — |
| gotowanie | D1, D2 | 10,90 | 0,60 | 6,54 | — |
| AGD (zmywarka, pralka, suszarka) | D3, D4, D5 | 6,90 | 0,60 | 4,14 | — |
| pompa ciepła | D6 | 2,67 | 1,00 | 2,67 | — |
| grzałka rezerwowa | D7 | 6,00 | 1,00 | 6,00 | tak |
| sterowanie ogrzewania | D8 | 0,30 | 1,00 | 0,30 | — |
| wentylacja mechaniczna | D9 | 0,10 | 1,00 | 0,10 | — |
| ładowanie EV | D11 | 11,00 | 1,00 | 11,00 | tak |
| napędy (bramy, osłony) | D12, D13, D16 | 2,70 | 0,30 | 0,81 | — |
| teletechnika | D14 | 0,20 | 1,00 | 0,20 | — |
| pompa wody deszczowej | D15 | 0,80 | 0,30 | 0,24 | — |
| Razem (bez zarządzania mocą) |  | 71,34 | — | 41,24 |  |

*Źródło: lamela.obliczenia.elektryka.bilans (odbiorniki z modelu i z doboru urządzeń PT-3 IS)*

**Tabela 7. Moc elektryczna urządzeń ogrzewczych i wentylacyjnych (§ 23 pkt 8 lit. b)**

| Urządzenie | Obwód | P_el [kW] | Fazy |
|---|---|---|---|
| Pompa ciepła — jednostka zewnętrzna (PC-R290-07 (przykład)) | D6 | 2,67 | 1 |
| Grzałka rezerwowa PC / zasobnika c.w.u. (6,0 kW) | D7 | 6,00 | 3 |
| Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego | D8 | 0,30 | 1 |
| Rekuperator (V ≈ 365 m³/h) | D9 | 0,10 | 1 |

Centrala wentylacyjna: moc wentylatorów P = SFP·V przy strumieniu projektowym — ta sama wartość co w doborze centrali w PT-3 IS.

*Źródło: dobór urządzeń — PT-3 IS; bilans — PT-4*

**Moc szczytowa bez zarządzania mocą** P_s = 41,2 kW > moc przyłączeniowa 27 kW —
**wymagane dynamiczne zarządzanie mocą (DLM)**: ograniczenie prądu ładowania EV i blokada grzałki rezerwowej
przy przekroczeniu mocy (pomiar prądów faz za licznikiem, sterownik DLM w RG). **Nastawa DLM** z zapasem
regulacji z = 5 % [ZAŁ] (czas reakcji, histereza): moc P_lim = 25,01 kW,
prąd fazowy I_nast = 38,0 A (przy zabezpieczeniu 40 A). **Moc szczytowa z DLM**
P_s,DLM = P_nst + w·P_st = 24,24 + 0,036·17,00 = 24,85 kW ≤
27 kW, gdzie w — współczynnik ograniczenia odbiorników sterowanych, ten sam w mocy całkowitej
i w podziale na fazy (tabela niżej); prąd szczytowy I_B = 37,8 A ≤ 40 A
(zabezpieczenie przedlicznikowe). Kontrolnie wg N SEP-E-002 (30 kVA + ogrzewanie elektryczne):
37,2 kW [NZW]. Moc przyłączeniowa 27 kW ≤ 40 kW
(grupa V) — do wniosku o warunki przyłączenia.

**Tabela 8. Podział mocy szczytowej (z DLM) na fazy**

| Faza | P_s [kW] | I [A] |
|---|---|---|
| L1 | 8,30 | 38,00 |
| L2 | 8,27 | 37,86 |
| L3 | 8,27 | 37,86 |

Moc faz z DLM (ten sam współczynnik w = 0,036); suma faz = P_s,DLM = 24,85 kW. Prąd najbardziej obciążonej fazy 38,0 A ≤ nastawa DLM 38,0 A < 40 A. Asymetria (max − min)/średnia = 0,4 %; cos φ = 0,95.

## Obliczenia — § 23 pkt 8 RPB — założenia, wyniki, dobór

Obliczenia wykonano bibliotekami `lamela.obliczenia.elektryka` na bieżącym modelu (łącznie 141 warunków
sprawdzających). Zestawienie wyników rozstrzygających — tabela poniżej; w obwodach odbiorczych pokazano obwód
z najmniejszym zapasem dla każdego kryterium. Pełne obliczenia z wzorami, danymi i wszystkimi warunkami — kolejne podrozdziały.

*[Tabela wyników sprawdzeń rozstrzygających — w PDF]*

### Obliczenia: bilans mocy — § 23 pkt 11 lit. a RPB

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.elektryka.bilans]*

### Obliczenia: WLZ, obwody, zabezpieczenia, spadki napięć, samoczynne wyłączenie, SPD, PWP — PN-HD 60364-4-41, -4-43, -4-443, -5-52

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.elektryka.obwody]*

### Obliczenia: instalacja fotowoltaiczna — PN-HD 60364-7-712

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.elektryka.pv]*

### Obliczenia: ocena ryzyka piorunowego, uziom — PN-EN 62305-2:2008 (zał. 1 WT)

*[Pełna treść obliczeń — w PDF; źródło: lamela.obliczenia.elektryka.odgromowa]*

## Dane dotyczące warunków ochrony przeciwpożarowej — § 23 pkt 10 RPB; WT § 183 ust. 2–4; ROPoż § 4 ust. 2 pkt 2, § 28a

**Klasyfikacja** (PAB): budynek mieszkalny jednorodzinny, kategoria zagrożenia ludzi ZL IV, grupa wysokości N;
jedną strefę pożarową tworzy cały budynek z garażem (WT § 226 ust. 1; W-212).

**Przeciwpożarowy wyłącznik prądu — sprawdzenie warunku WT § 183 ust. 2.** Przepis wymaga PWP „w strefach
pożarowych o kubaturze przekraczającej 1000 m³ lub zawierających strefy zagrożone wybuchem” (brzmienie z t.j.
Dz.U. 2022 poz. 1225). Kubatura strefy = kubatura brutto budynku z modelu (PN-ISO 9836; W-069):
V = 1 354,40 m³ (P0 578,05, P1 345,18, P2 283,63, płyta ST1 26,78, płyta ST2 21,49, płyta ST2Z 2,05, płyta D1 44,14, płyta D2 8,43, płyta D3 7,69, płyta D4 36,98); próg 1 000 m³ → warunek **spełniony — PWP wymagany**;
stref zagrożonych wybuchem brak. ROPoż § 4 ust. 2 pkt 2 wyłącza z obowiązku wyposażania obiektów w PWP
właścicieli budynków mieszkalnych jednorodzinnych — rozbieżność interpretacyjna (D-04). **Decyzja: PWP
projektuje się** (spełnia obie interpretacje, W-190).

**Rozwiązanie PWP:** przycisk w obudowie z szybką, przy wejściu głównym do budynku lub przy ZKP, oznakowany znakiem
„Przeciwpożarowy wyłącznik prądu” (WT § 183 ust. 3); działa na wyzwalacz aparatu głównego RG (rozłącznik
z wyzwalaczem wzrostowym z kontrolą ciągłości obwodu albo wyzwalaczem zanikowym [ZAŁ]) i odcina wszystkie obwody
budynku, w tym stronę AC falownika PV — w budynku nie ma instalacji, których funkcjonowanie jest niezbędne podczas
pożaru. Zadziałanie PWP nie powoduje samoczynnego załączenia innego źródła energii (WT § 183 ust. 4); falownik PV
wyłącza się po zaniku napięcia sieci (zabezpieczenie przed pracą wyspową). Strona DC PV pozostaje pod napięciem —
oznakowanie ostrzegawcze przy RG, PWP i falowniku oraz informacja dla służb ratowniczych przy ZKP.

**Pozostałe dane ppoż. w zakresie tomu:** mikroinstalacja PV 6,45 kWp ≤
6,5 kWp — bez obowiązku uzgodnienia z rzeczoznawcą ds. zabezpieczeń
przeciwpożarowych i zawiadomienia PSP (W-194, W-218); autonomiczne czujki dymu (PN-EN 14604) — co najmniej
1 w lokalu (ROPoż § 28a ust. 1; Dz.U. 2024 poz. 1716), w projekcie w komunikacji
każdej kondygnacji i w sypialniach [ZAŁ] (W-197); czujka tlenku węgla — nie dotyczy (brak spalania paliw,
§ 28a ust. 3); przejścia instalacji przez ściany zewnętrzne i płytę poniżej terenu gazoszczelne (W-214); osprzęt
nie montowany bezpośrednio na podłożu palnym bez osłony (ROPoż § 4 ust. 1 pkt 10); rozdzielnice i PWP dostępne
(ROPoż § 4 ust. 1 pkt 18 lit. f). Instalacje ochrony przeciwpożarowej (§ 23 pkt 7 lit. j) — nie występują.

## Wyroby i parametry wymagane — PB art. 10; wyroby przykładowe — lub równoważne

Tom nie wskazuje nazw handlowych. Parametry urządzeń przyjęte w obliczeniach pochodzą z kart **wyrobów
przykładowych** bibliotek obliczeniowych [DANE PRZYKŁADOWE – FIKCYJNE]; wykonawca może zastosować dowolny wyrób spełniający parametry
wymagane z tabeli, wprowadzony do obrotu zgodnie z przepisami o wyrobach budowlanych / o systemie oceny zgodności
(DWU, deklaracja zgodności UE). Po wyborze wyrobów dane DTR wprowadzić do `model/instalacje.yaml` (`wyroby`)
i przeliczyć tom (E-13).

**Tabela 9. Wyroby — parametry wymagane (wyroby przykładowe — lub równoważne)**

| Wyrób | Parametry wymagane |
|---|---|
| Rozdzielnica główna RG | PN-EN IEC 61439-3; ≥ IP40; rezerwa miejsca ≥ 20 % modułów; szyna PE/N oddzielna (TN-S) |
| Wyłączniki nadprądowe, RCBO, RCD | PN-EN 60898-1, PN-EN 61009-1, PN-EN 61008-1; zdolność łączeniowa I_cn ≥ 6 kA; charakterystyki i prądy znamionowe wg zestawienia obwodów; RCD typ A (min.), typ F/B dla urządzeń z przekształtnikami wg DTR |
| Ochronniki przepięć (SPD) | PN-EN IEC 61643-11:2026-04; SPD typ 1+2 (T1+T2), I_imp ≥ 12,5 kA/biegun, U_p ≤ 1,5 kV, U_c ≥ 275 V; układ 3+1 (TN-S) lub 4+0 przy rozdziale PEN w RG |
| Przewody i kable | YDYp / YDY 450/750 V (Cu); WLZ YKY 5×25 0,6/1 kV w ziemi; H1Z2Z2-K (PN-EN 50618:2015-03) 10 mm² po stronie DC PV; przekroje obwodów odbiorczych wg zestawienia obwodów |
| Moduł fotowoltaiczny | P_max ≥ 430 Wp; U_oc ≤ 38,9 V; I_sc ≤ 14,0 A; wymiary ≤ 1,722 × 1,134 m; PN-EN IEC 61215, PN-EN IEC 61730 |
| Falownik PV 3-fazowy | P_AC ≤ 6,0 kW; U_DC,max ≥ 1 000 V; zakres MPPT obejmujący 196–298 V; ≥ 2 wejścia MPPT; I_MPPT ≥ 16,0 A; certyfikat NC RfG (lista PTPiREE); PN-EN 50549-1; SPD DC i rozłącznik DC wbudowane lub zewnętrzne |
| Punkt ładowania EV | tryb 3, PN-EN IEC 61851-1; 11 kW 3f; wejście DLM (ograniczenie prądu); detekcja prądu stałego RDC-DD 6 mA albo RCD typ B |
| Czujki dymu | autonomiczne, PN-EN 14604; zasilanie bateryjne 10-letnie lub sieciowe z podtrzymaniem [ZAŁ] |
| Uziom, przewody wyrównawcze | drut/płaskownik Cu 50 mm² lub StCu Ø10 mm lub StSt 30×3,5 mm, ≥ 0,5 m w gruncie, ≥ 1 m od ścian [ZAŁ] |

*Źródło: lamela.obliczenia.elektryka (dane przykładowe wyrobów), rejestr wymagań A.3*

## Próby, pomiary i odbiory — PN-HD 60364-6:2016-07; PN-EN 62446-1; W-199

Sprawdzenie odbiorcze instalacji wg PN-HD 60364-6:2016-07 przed przekazaniem do użytkowania: oględziny;
ciągłość przewodów ochronnych i połączeń wyrównawczych; rezystancja izolacji (500 V DC, ≥ 1 MΩ); samoczynne
wyłączenie zasilania — pomiar impedancji pętli zwarcia w najdalszym punkcie każdego obwodu; działanie i czas
zadziałania RCD; kolejność faz; spadek napięcia (wyrywkowo); działanie PWP (odcięcie wszystkich obwodów, w tym AC
falownika); rezystancja uziemienia (wartość orientacyjna z obliczeń R ≈ 14,9 Ω).
Mikroinstalacja PV — wg PN-EN 62446-1 (ciągłość, U_oc i I_sc łańcuchów, rezystancja izolacji DC, dokumentacja
systemu). Tor światłowodowy — pomiar tłumienności (≤ 1,2 dB),
okablowanie strukturalne — pomiary kat. 6A (PN-EN 50173-4). Protokoły badań instalacji dołącza się do
zawiadomienia o zakończeniu budowy (PB art. 57 ust. 1 pkt 4 lit. a).

**Tabela 10. Największa dopuszczalna impedancja pętli zwarcia (t ≤ 0,4 s)**

| Zabezpieczenie | I_a [A] | Z_s,max = U₀/I_a [Ω] |
|---|---|---|
| B10 | 50,00 | 4,60 |
| B16 | 80,00 | 2,88 |
| C16 | 160,00 | 1,44 |
| C20 | 200,00 | 1,15 |

Wartość zmierzoną w temperaturze otoczenia porównać z Z_s,max z uwzględnieniem wzrostu rezystancji przewodów w temperaturze pracy (PN-HD 60364-6); wartości obliczeniowe Z_s obwodów — rozdz. „Obliczenia”.

## Braki danych i zgodność części rysunkowej — rejestr wymagań E.1–E.2

**Tabela 11. Braki danych modelu wykazane przy generowaniu rysunków (BRAKI_DANYCH.md)**

| Lp. | Element | Brak / stan w modelu | Arkusze |
|---|---|---|---|
| 1 | PV — rozmieszczenie modułów | w polu użytkowym dachu D1 zmieszczono 10 z 15 modułów (odsunięcia od krawędzi, otworów, czerpni/wyrzutni) | PT-IE-10 |
| 2 | PV — trasa DC | brak w modelu trasy przewodów DC i przepustu dachowego — przyjęto trasę po dachach (poza drogami ewakuacyjnymi) do pom. technicznego | PT-IE-10 |
| 3 | Punkty instalacji elektrycznych i teletechnicznych | model nie zawiera położeń opraw, łączników, gniazd i punktów teletechnicznych — rozmieszczenie algorytmiczne (opis w uwagach arkuszy) | PT-IE-01, PT-IE-02, PT-IE-03, PT-IE-04, PT-IE-05, PT-IE-06, PT-IE-07, PT-IE-08, PT-IE-09, PT-IE-11, PT-IE-12 |
| 4 | Trasy teletechniczne (pion, RACK) | brak w modelu pionu/tras teletechnicznych — przyjęto pion proponowany (wspólna lokalizacja z pionem wentylacyjnym) | PT-IE-07, PT-IE-08, PT-IE-09 |

**Założenia projektowe do potwierdzenia [ZAŁ]** (z obliczeń):

* DLM (dynamiczne zarządzanie mocą): ograniczenie mocy ładowarki EV i blokada grzałki PC przy przekroczeniu mocy przyłączeniowej; nastawa DLM 95 % granicy (moc przyłączeniowa, prąd zabezpieczenia przedlicznikowego) — zapas regulacji na czas reakcji i histerezę [ZAŁ].
* Moduł: PV-430 TOPCon (dane przykładowe); falownik: FAL-6K-3P (dane przykładowe) [ZAŁ — zastąpić DTR wybranych wyrobów, E-13].
* Obwody gniazd: moc umowna 2,0 kW/obwód; oświetlenie LED 5 W/m² [ZAŁ].
* Temperatura otoczenia 30 °C (powietrze), 20 °C (grunt); grupowanie 2 obwodów (k = 0,80) [ZAŁ].
* Współczynniki jednoczesności: oswietlenie 0,7, gniazda 0,2, gniazda_kuchnia 0,5, gniazda_lazienka 0,3, gotowanie 0,6, agd 0,6, pc 1,0, grzalka 1,0, went 1,0, sterowanie 1,0, ev 1,0, zewn 0,3, tele 1,0, napedy 0,3, pompa 0,3, pv 0,0 [ZAŁ].
* Z_Q w ZKP = 0,30 Ω (R/X ≈ 0,9/0,44), I_k,max w ZKP ≤ 6 kA [ZAŁ — dane z warunków przyłączenia OSD].

### Zgodność rysunków z bieżącymi obliczeniami

Kontrola automatyczna nie wykazała rozbieżności między arkuszami a bieżącymi obliczeniami.

Uwagi generatora arkuszy (raport_widokow.json):

* instalacje (obliczenia): Piony deszczowe RS1, RS2, RS6 wyłączone z grupowania pionów wod.-kan. (w modelu `instalacje.piony` bez pola `rodzaj`).

## Część rysunkowa — wykaz rysunków

| Nr | Tytuł | Skala | Format | Uwagi |
|---|---|---|---|---|
| PT-IE-01 | INSTALACJA OŚWIETLENIA — RZUT PARTERU | 1:50 | nst. 594×440 |  |
| PT-IE-02 | INSTALACJA OŚWIETLENIA — RZUT I PIĘTRA | 1:50 | nst. 690×297 |  |
| PT-IE-03 | INSTALACJA OŚWIETLENIA — RZUT II PIĘTRA | 1:50 | nst. 570×297 |  |
| PT-IE-04 | GNIAZDA I ZASILANIE URZĄDZEŃ — RZUT PARTERU | 1:50 | nst. 594×500 |  |
| PT-IE-05 | GNIAZDA I ZASILANIE URZĄDZEŃ — RZUT I PIĘTRA | 1:50 | A2 |  |
| PT-IE-06 | GNIAZDA I ZASILANIE URZĄDZEŃ — RZUT II PIĘTRA | 1:50 | nst. 420×450 |  |
| PT-IE-07 | TELETECHNIKA — RZUT PARTERU | 1:50 | nst. 594×470 |  |
| PT-IE-08 | TELETECHNIKA — RZUT I PIĘTRA | 1:50 | nst. 690×297 |  |
| PT-IE-09 | TELETECHNIKA — RZUT II PIĘTRA | 1:50 | nst. 570×297 |  |
| PT-IE-10 | INSTALACJA FOTOWOLTAICZNA — RZUT DACHU | 1:50 | nst. 594×440 |  |
| PT-IE-11 | INSTALACJA FOTOWOLTAICZNA — RZUT PARTERU (FALOWNIK, SPD) | 1:50 | nst. 594×440 |  |
| PT-IE-12 | UZIOM I POŁĄCZENIA WYRÓWNAWCZE — RZUT PARTERU | 1:50 | nst. 610×480 |  |
| PT-IE-13 | OCHRONA ODGROMOWA I WYRÓWNANIE POTENCJAŁÓW — RZUT DACHU | 1:50 | nst. 594×440 |  |
| PT-IE-14 | SCHEMAT ROZDZIELNICY GŁÓWNEJ RG | — | nst. 870×297 |  |
