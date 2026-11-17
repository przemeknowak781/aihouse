# Weryfikacja PROGRAMU i FUNKCJI – „BRAMA I LATARNIA” (synteza 1.0)

Weryfikator adwersaryjny · 17.11.2026 · przedmiot: `koncepcja_wybrana.md` (rozdz. 4–7, 11, 12) i `model/koncepcja.json`
wobec `20_program/program.yaml`, Wyj. 21 odp. 84–85 (wszystkie pomieszczenia Sejmiku z PU s. 5–7 na kondygnacji sali; wyjątek: Kancelaria),
`10_regulamin/wyjasnienia_streszczenie.md`, `40_prawo/ppoz.md`, `wt_kluczowe.md`, `dostepnosc.md`.
Specyfikacji nie edytowano. Nie korzystano z informacji o rzeczywistych pracach ani wynikach konkursu.

**Dowód obliczeniowy:** `docs/20_koncepcja/_weryfikacja_program.py` (uruchomienie z katalogu `umwd/`: `python3 docs/20_koncepcja/_weryfikacja_program.py`).
Skrypt czyta tylko JSON/YAML i liczy w shapely w układzie (u, v) wieży (u = az. 76,3°, v = az. 346,3°; początek SW obszaru A).
Numery sekcji skryptu podano przy każdym błędzie: [S1a] itd.

---

## 0. Werdykt

Kondygnacja Sejmiku **nie mieści programu** w zadeklarowanej formie. Bilans „zamyka się” wyłącznie dlatego, że:
- bar i szatnia stoją w holu, któremu zostaje 5,8 m² wolnej podłogi;
- salą multimedialną nazwano przejście za galerią o szerokości 1,25 m;
- trzy pomieszczenia nie mają drzwi na komunikację;
- 44 stanowisk nie da się ustawić w podanym układzie rzędów.

Na kondygnacjach biurowych suma 187 pokoi i podział na departamenty się zgadzają. **Kondygnacja 6 jest jednak przepełniona o 1–2 pokoje**, a deklarowana „rezerwa 3,2 jedn.” nie istnieje tam, gdzie jest potrzebna.

| Waga | Liczba |
|---|---:|
| KRYTYCZNE | 3 |
| ISTOTNE | 8 |
| DROBNE | 16 |

## 1. Co jest zgodne (sprawdzone)

- **187 pokoi** = 179 × 24 + 8 × 32 (GW). Suma `ceil(n/3)` / `ceil(n/4)` liczona per komórka zał. 1 jest zgodna z `program.yaml`.
- Departamenty są **niedzielone**, zakaz mieszania działów spełniony (P: DK II 2 + DW 2; 1: DOS 38; 2: DI 25 + DST 13; 3: DGP 24 + GW 11; 4: pion 8 = 34; 5: DSS 19; 6: KS 8 + DRA 11).
- **GW z archiwami 48 + 24 i pracownią 24 na tej samej kondygnacji** (3) – Wyj. 6 odp. 26 ✔.
- Liczebności: 6 sal narad po 60 m², 15 pokoi socjalnych, 20 magazynków, 10 miejsc oczekiwania (9 + KS.06) ✔.
- **Komfortka** 12 m², 3,0 × 4,0 m, ≈ 13,9 m od drzwi w łuku (≤ 20 m) ✔.
- **Wysokości w świetle:**
  - biura wieży 3,32 m, skrzydła 3,20 m (≥ 3,0 m, WT § 72);
  - parter 4,37 / 4,25 m, sala obrad 6,85 m, komisje 4,90 m;
  - kuluar pod antresolą i antresola po 3,25 m (≥ 2,2 m);
  - garaż −1 3,25 m, −2 2,75 m ✔.
- Strefy pożarowe ≤ 2 500 m² (1–4: 2 160; P: 2 003; S z antresolą: 1 215) ✔.
- Dwie klatki A i B z przedsionkami w wieży (odstęp 20 m) i klatka C w skrzydle ✔.
- Dźwig R (PN-EN 81-72/76) w trzonie A, −2…S ✔.
- Ślepe końce kuluaru ≤ 10 m (ZL I) ✔. Dojścia z sali do klatek ≤ 26 m (≤ 40 m przy dwóch kierunkach) ✔.
- Publiczność: płyta 70 + galeria 30 = 100. Na galerii 3 miejsca dla wózków, wśród gości 2 ✔.
- Prezydium przy pełnej ścianie pd., czyli nie pod światło (z zastrzeżeniem I1) ✔.
- Antresola stanowi 6,1 % rzutu ✔. Wszystkie pomieszczenia zamknięte S leżą formalnie na poziomie głównym ✔.
- Parking: 109 m.p. ≥ 101 (PU 8 400) i ≥ 103 (PU programowe 8 582) ✔ (por. D2).
- Ściany wewnętrzne i zewnętrzne razem stanowią 9,0 % PC poziomu S ✔ (por. D1: ściany wewnętrzne są za cienkie).

---

## 2. Błędy KRYTYCZNE

### K1. Trzy pomieszczenia kondygnacji Sejmiku bez dostępu z komunikacji / bez drogi ewakuacyjnej [S1a]

**Dowód** (styk z KUL lub SWD.02 przez ścianę ≤ 0,20 m, wynik skryptu):

| Pomieszczenie | Obrys (u; v) | Styk z komunikacją | Sąsiedzi |
|---|---|---:|---|
| **SWD.11b** klub radnych 30 os. | u 31,25–39,50 × v 0,50–7,10 | **0,00 m** | trzon B, PHS.05c, SWD.07 |
| **PHS.05a** WC męskie z toaletą dostępną | u 15,65–19,85 × v 16,45–19,30 | **0,00 m** | trzon A, SWD.04, SWD.15, **sala obrad** |
| **PHS.05c** toaleta publiczności | u 31,25–35,00 × v 7,25–9,90 | geometrycznie 4,25 m, ale spec.: „dostęp **wyłącznie dźwigiem P2**” | – |

Skutki:
- Do klubu na 30 osób wchodzi się przez toaletę publiczną albo przez pokój matki z dzieckiem.
- Do WC męskiego wchodzi się z sali obrad albo przez reżyserkę.
- Z toalety publiczności (w tym dostępnej) nie ma wyjścia na drogę ewakuacyjną. Dźwig osobowy nie jest drogą ewakuacyjną (WT § 237, § 256), więc osoba na wózku zostaje w pożarze uwięziona.
- Spec. pisze, że „kuluar łączy … wszystkie komisje i kluby”, co jest nieprawdą dla SWD.11b.

**Poprawka:**
1. Pas u 31,25–39,50 × v 7,25–9,90 dzielimy tak:
   - **dojście 1,50 m** u 31,25–32,75 (z KUL do SWD.11b, drzwi 1,0 m w ścianie v 7,10);
   - **SWD.07** u 32,90–37,25 (11,5 m²);
   - **pomieszczenie porządkowe + PD** u 37,40–39,50 (5,6 m²; dziś na S ich brak, por. K2).
2. **PHS.05c likwidujemy.** Toaleta publiczności (dostępna, 2,2 × 2,5 m) trafia na antresolę przy P1/P2, u 37,0–39,5 × v 10,05–12,30. Jest to jedyna zamknięta kabina na antresoli, co trzeba opisać na planszy.
   Jeżeli PHS.05c ma zostać, potrzebne są drzwi ewakuacyjne do KUL z kontrolą dostępu i alarmem.
3. **WC męskie z wejściem z korytarza pn.:**
   - WC M: u 15,65–19,85 × v 16,20–20,85 (19,5 m²), drzwi do korytarza pn. (v 21,0);
   - reżyserka SWD.04 zostaje w pasie u 15,65–19,85 × v 12,45–16,05 (15,1 m²);
   - SWD.15 jest pozycją nieobowiązkową, więc z niej rezygnujemy (S-2).

### K2. Bilans kondygnacji Sejmiku się nie zamyka; hol reprezentacyjny praktycznie nie istnieje [S1b, S1c, S6]

**Dowód:**
1. **SWD.02 = 79,9 m²** składa się z trzech części:
   - narożnik NW 47,8 m² (7,65 × 6,25 m);
   - **pasaż zach. 15,8 m² o szerokości 1,50 m**;
   - **korytarz pn. 16,4 m² o szerokości 1,40 m**.

   Spec. ustawia w narożniku NW bar SWD.05 (30 m²) i szatnię SWD.06 (12 m²), więc **wolnego holu zostaje 5,8 m²**. W tym miejscu ma powstać obowiązkowa wizualizacja nr 7 (Wyj. 21 odp. 82).
2. Program SWD.02 + SWD.05 + SWD.06 = **205 m²** (minimum zakresów 162 m²), a w rzucie jest 79,9 m², czyli **deficyt 125 m²** (82 m² do minimum).
   Spec. porównuje „hol 79,9 + kuluar 87,8 = 167,7 ✔ (150)”, ale pomija, że bar i szatnia stoją w tych samych 79,9 m². Kuluar ma 2,25 m szerokości i jest drogą ewakuacyjną.
3. **SWD.03 „sala multimedialna / poczekalnia gości” = ANT-F 37,7 m²**, z czego 20,0 m² to pas o szerokości 1,25 m na długości 16,0 m. Jest to przejście za dwoma rzędami galerii i droga ewakuacyjna 30 osób.
   Jest otwarty na salę, więc głośniki „sali multimedialnej” grają do sali obrad. Funkcja z PU s. 6 (ekran, głośniki, 20 os.) nie jest spełniona.
4. **Przestrzeń przed dźwigami:**
   - A1/A2 (kadr W7 „przy dźwigach A”, (u 13,0; v 21,7)) otwierają się na korytarz pn. o szerokości **1,40 m**, podczas gdy WT § 195 wymaga ≥ 1,6 m, a M.13 s. 170 – 3,6 m;
   - P1/P2 na antresoli: ANT-F ma 1,25 m, do 1. rzędu galerii jest **1,55 m** (WT § 195: ≥ 1,6 m);
   - drzwi sali na zachód (wejście radnych i gości, ZL I, > 50 os.) otwierają się na ten sam korytarz 1,40 m.
5. Na S brakuje **pomieszczenia porządkowego i PD** (PP.06, IT.02: „na każdej kondygnacji”; tabela 7.1 ich nie ma). Brakuje też szachtu wyrzutni zbiorczej, która ma dojść do „pasa nad komisjami” (por. D8).
6. Ściany wewnętrzne mają średnio 0,151 m (36,8 m² na 244 m). Przy 0,30 m dla ścian sali (ściana pd. jest nośna pod ruszt 19,5 m) i 0,20 m dla pozostałych potrzeba ≈ 52 m², czyli **+15 m²** (D1).
7. Suma programu SWD + PHS.05 = 1 094 m² netto. W rzucie jest 916 m², przy czym bar i szatnia liczone są podwójnie: jako pomieszczenia i jako hol.

**Skutek:** podstawowy wymóg Wyj. 21 odp. 85 jest spełniony tylko formalnie. Hol reprezentacyjny (wizualizacja 7), przestrzeń gastronomiczna, szatnia i sala multimedialna nie mają realnej powierzchni. Sędziowie J1, J2 i J4 wytknęli to K5 („bilans się nie zamyka”) i wada wraca w nowej postaci.

**Poprawka – wariant S-2** [S7d]. Bilans zamyka się z zapasem **0,6 m²** przy wszystkich salach na dolnych granicach zakresów, co pokazuje, że rzut S w A jest na granicy wykonalności.

Poziom główny (wnętrze 1 080,1 m²):

| Element | m² |
|---|---:|
| Trzony A + B (dźwig T przeniesiony do segmentu, por. I5) | 119,2 |
| SWD.01 sala obrad (4 rzędy, por. K3) | 283,0 |
| SWD.04 (v 12,45–16,05) | 15,1 |
| SWD.07 (u 32,90–37,25) | 11,5 |
| SWD.08 | 90,0 |
| SWD.09 | 54,0 |
| SWD.10 | 16,0 |
| SWD.11 | 108,0 |
| SWD.12 | 60,0 |
| SWD.13 | 36,0 |
| SWD.14 | 20,0 |
| WC: K 18,4 m² (u 17,0–19,85 × v 22,75–29,2) + M 19,5 m² (u 15,65–19,85 × v 16,20–20,85) + 2,1 | 40,0 |
| Pomieszczenie porządkowe + PD (u 37,40–39,50) | 5,6 |
| Dojście do SWD.11b | 4,0 |
| Hol dolny: narożnik NW + pasaż + korytarz pn. poszerzony do **1,60 m** (SWD.13, SWD.14 i WC K przesunięte o 0,20 m na pn.); szatnia SWD.06 jako lada | 82,3 |
| KUL | 87,8 |
| Ściany wewnętrzne | 47,0 |
| **Razem** | **1 079,5** |

Antresola +30,90 = **179,8 m² (16 % rzutu, w całości otwarta)**:
- pas nad kuluarem ANT-F 37,7 m²;
- **galeria zachodnia** u 15,65–21,0 × v 12,45–20,85, 44,9 m² (por. I1; zastępuje galerię pd.);
- **nowa płyta NW u 0,5–8,15 × v 12,45–22,95 (80,3 m²)** nad SWD.12a/b i pasażem (kluby mają pod nią 3,25 m w świetle, czyli ≥ 3,0 m);
- kładka nad kuluarem u 8,15–15,65 (16,9 m²).

Na antresoli mieszczą się:
- galeria 44,9 m²;
- **bar SWD.05 30 m²** (otwarty, przyłącza nad SWD.12);
- **strefa multimedialna SWD.03 30 m²** (ekran i nagłośnienie kierunkowe);
- WC publiczne 5,6 m²;
- hol górny 69,3 m².

**Hol RU = 70,3 + 69,3 = 139,6 m²** (min 120). Przy ścianach 52 m² zamiast 47 m² brakuje ≈ 4 m². Wtedy zaplecza nagrań trzeba zmniejszyć do 2 × 8 m², a reżyserkę do 15 m².
Wymogu M.13 (3,6 m przed dźwigami) na S nie da się spełnić. Trzeba go opisać jako świadome odstępstwo z uzasadnieniem.

### K3. Sala obrad: 44 stałe stanowiska z pochylniami i miejscami dla wózków nie mieszczą się w układzie R 4,8 / 6,9 / 9,0 m [S2, S7a]

**Dowód.** Ognisko F = (30,0; 13,4) leży 9,5 m od ściany wsch. (u 39,5) i 10,0 m od zach. (u 20,0). Łuk R 13,5 m przybliża się do F na 10,6 m (φ = 30°) i 11,5 m (φ = 45°).

Założenia:
- rząd 3 ma linię krzeseł R 9,0, oparcie +0,45–0,50 m, przejście za rzędem 1,2 m;
- w każdym rzędzie jest miejsce dla wózka 1,5 m (rząd 1: dwa miejsca);
- po obu końcach rzędów są przejścia z pochylniami po 1,4 m (spec.: „pochylnie boczne”).

Wyniki:
- Wolny sektor rzędu 3 to φ 32,5°–159,0°, czyli łuk **19,9 m**. Przy przejściu 0,9 m: 21,8 m.
- Potrzeba **22,5 m** przy pulpicie 1,0 m i **26,1 m** przy typowym 1,2 m.
- Układ ze specyfikacji daje **40 stanowisk** przy pulpicie 1,0 m (9 + 15 + 16) i **35** przy 1,2 m. Wymagane są 44.
- Spec. rozkłada 19 miejsc na półokręgu π·9,0 = 28,3 m, czego ściana wsch. i łuk nie dopuszczają.
- Rząd 1 z dwoma miejscami dla wózków i przejściami wymaga ≈ 180°, więc jego końce wchodzą w strefę prezydium.
- Dla mediów (8) i gości (12) spec. nie wskazuje miejsca.

**Poprawka:**
- **4 rzędy wokół F = (29,5; 13,4), R 4,8 / 6,6 / 8,4 / 10,2 m, na +0,15 / +0,30 / +0,45 / +0,60.** Rzędy 1–3 w sektorze 12°–168°, rząd 4 w sektorze 43°–143°.
- Pojemność przy pulpicie 1,2 m: **8 + 12 + 16 + 12 = 48** (44 stałe + 4 rezerwy), w każdym rzędzie miejsce dla wózka.
- Pochylnie boczne 5 % (4 × 3,0 m) biegną skośnie w przejściach przy końcach rzędów.
- Media i goście (20 os.): sektor NW płyty u 20–26 × v 22–29,2 oraz pas za rzędem 4 (φ 60°–120°).
- Prezydium, mównica, PJM i obsługa kancelaryjna: strefa R < 3,9 m od F przy ścianie pd.
- Kadr W8 trzeba przeliczyć.

---

## 3. Błędy ISTOTNE

### I1. Galeria publiczności nad prezydium: brak obserwacji prezydium i mówcy; z 2. rzędu nic nie widać; radni pod światło [S2]

Galeria ma wymiary u 21–37 × v 11,45–13,45 i wysięg 1,0 m nad salę, więc **przykrywa pas prezydium** (v 12,45–~14,2). Skutki:
- Publiczność nie widzi prezydium i ma mówcę przy mównicy pod sobą, widząc tylko czubek jego głowy. PU s. 6 / Wyj. 4 odp. 18 wymagają „obserwacji i przysłuchiwania się obradom”.
- Radnych publiczność widzi **na tle przeszklenia 22 × 6,6 m**. To ta sama wada „pod światło”, którą sędziowie wytknęli K5, tylko przeniesiona na publiczność i kamery (spec. sama przyznaje, że do ujęć radnych trzeba opuszczać rolety 5 %).
- **Płaska galeria z 2 rzędami co 1,0 m:** kąt patrzenia z 2. rzędu na radnych to ≈ 28° w dół, więc linia wzroku trafia w głowy 1. rzędu (0,53 m pod okiem przy głowach +0,10 m nad okiem). Potrzebny jest podest ≥ 0,45–0,6 m.
- Miejsce dla wózka (0,9 × 1,4 m) i 2. rząd nie mieszczą się w głębokości 2,0 m.

**Poprawka (rekomendowana): galeria zachodnia** na antresoli nad SWD.04 i WC M:
- obrys u 15,65–21,0 × v 12,45–20,85 (44,9 m²), wysięg 1,0 m nad salę do u 21,0;
- 2 rzędy, 2. rząd na podeście +0,45 m;
- w 1. rzędzie 3 miejsca dla wózków + 3 dla opiekunów.

Efekty:
- Publiczność widzi prezydium z boku (≈ 60°), twarz mówcy oraz radnych z ukosa (en trois-quarts), a panoramę z boku.
- Galeria przylega do lica wsch. trzonu A, więc **klatkę A wystarczy wyprowadzić do +30,90** i galeria dostaje drugą drogę ewakuacyjną (por. I4).
- Godło przechodzi na ścianę pd.
- Pas nad kuluarem (v 10,05–12,30) zostaje foyer o szerokości 2,25 m, więc warunek WT § 195 przed P1/P2 jest spełniony.

### I2. Kondygnacja 6 przepełniona, „rezerwa 3,2 jedn.” pozorna [S3, S7b]

**Dowód.** Jednostka to 4,05 m elewacji przy głębokości 6,10 m. Sala narad 7,60 m odpowiada 1,88 j., magazynek głęboki 2,70 m – 0,667 j.

| Kond. | Potrzeba | Pojemność | Zapas |
|---|---:|---:|---:|
| 1 | 41,88 | 43 | +1,12 |
| 2 | 42,88 | 43 | **+0,12** |
| 3 | 42,75 | 43 | **+0,25** |
| 4 | 41,88 | 43 | +1,12 |
| 5 | 23,54 | 24 | +0,46 |
| 6 | **25,00** | 24 | **−1,00** |

Na kondygnacji 6 zapotrzebowanie tworzą: KS 8 + DRA 11 + gabinet Przewodniczącego 40 m² z asystentem 14,5 m² (łuk) + 3 gabinety Wiceprzewodniczących po 30 m².

Liczenie dyskretne: łuk (≈ 100 m²) mieści Przewodniczącego z asystentem, 1 pokój i miejsce oczekiwania z zapleczem. Pozostaje 20 j. prostych dla 3 gabinetów × 4,92 m + n × 4,05 m, więc **n = 16, czyli 17 pokoi zamiast 19 (brak 2)**. Przy gabinetach Wiceprzewodniczących po 24 m² brakuje 1 pokoju.

Pojemność wieży 24 j. wymaga przydziału narożników z zapasem **0,05 m** na elewacji pd. (S1 = 24,35 m na 6 j.).
Ryzyko nr 3 ze spec. („zamiana 3 pokoi … rezerwa 3,2 jedn.”) nie ma pokrycia: na kondygnacjach 2–3 zapas wynosi 0,12–0,25 j.

**Poprawka** (zgodna z Wyj. 17 odp. 70 i Wyj. 10 odp. 62: gabinety dyrektorów DRA zostają razem na 6):
- **DRA.5.SAM (2 pokoje samodzielnych stanowisk) → kond. 5 przy trzonie A.**
- Z kond. 5 przenosimy 3 magazynki głębokie: 1 na kond. 1, 2 na kond. 4. Na kond. 4 jeden magazynek standardowy zamieniamy na głęboki.

| Kond. | Po poprawce | Zapas |
|---|---:|---:|
| 1 | 42,54 | +0,46 |
| 2 | 42,88 | +0,12 |
| 3 | 42,75 | +0,25 |
| 4 | 42,88 | +0,12 |
| 5 | 23,54 | +0,46 |
| 6 | 23,00 | +1,00 (dyskretnie: 16 × 4,05 + 3 × 4,92 = 79,55 ≤ 81,0 m) |

Magazynki: 12 standardowych + 8 głębokich = 20. W opisie trzeba usunąć zdanie o rezerwie 3,2 j.

### I3. WC: −157 m² wobec programu; na S zespół dla ~315 osób ma 35 m² [S4]

- Spec. podaje PU „WC 260 m²”, a program PHS przewiduje **417 m²**, czyli **−157 m² (−38 %)**.
- WC przy holu P ma 19 m² (PHS.02: min 24).
- Po odjęciu P, komfortki, konferencji i S na 10 zespołów kondygnacji 1–6 zostaje **15,4 m²/zespół** (PHS.01: 28, zakres 22–40). Wystarcza to co najwyżej na 1 toaletę dostępną + 2 K + 1 M + 1 pisuar.
- Kondygnacja Sejmiku (program 9.2: ≈ 315 os.):
  - PHS.05a 12,0 m² (z toaletą dostępną zostaje ≈ 7 m² na 1 miskę i 1 pisuar), do tego bez dostępu (K1);
  - PHS.05b 13,3 m² w pasie o szerokości **2,0 m**: kabina dostępna z transferem obustronnym (M.13: 0,9 m z każdej strony) wymaga ≥ 2,2 m;
  - PHS.05c 9,9 m² jest niedostępne (K1).
  - Potrzeba ≈ 4 K + 3 M + 3 pisuarów + 2 toalet dostępnych, czyli **≈ 40–45 m²**.

**Poprawka:**
- S: WC K 18,4 m² + WC M 19,5 m², każde z kabiną dostępną (lokalizacja jak w S-2, K2), oraz publiczna toaleta dostępna 5,6 m² na antresoli.
- P: WC ogólnodostępne ≥ 30 m² kosztem strefy WC i komfortki u 15,65–21,0 × v 15,0–20,85 (31 m² → 42 m², zabrane z hali).
- Kondygnacje 1–4: zespoły ≥ 24 m² (miejsce jest w nieoświetlonym pasie zach. wieży, ≈ 181 m² na kondygnację).
- Kondygnacje 5–6: zespół ≥ 26 m².
- W bilansie spec. ująć PU WC ≥ 380 m².

### I4. Otwarte schody z antresoli w kuluarze; antresola „otwarta na kuluar” [opis 7.3, ppoz.md 5.3]

- Schody 3,60 m (21 stopni, 2 biegi ze spocznikiem, ≈ 7,2 m) w kuluarze o szerokości 2,25 m zostawiają **≈ 0,95 m**, a WT § 242 wymaga ≥ 1,4 m (M.13: 1,8 m).
- Biegną od u 15,65 na zachód, czyli wzdłuż lica pd. trzonu A (u 8,3–15,5), gdzie są drzwi przedsionka klatki A i ewentualnie dźwigów.
- Spec. pisze, że antresola jest „w całości otwarta na salę i kuluar”. To łączy drogę ewakuacyjną (kuluar) z pomieszczeniem ZL I przez pustkę, wbrew § 241 i § 247.

**Poprawka:**
- Schody usunąć.
- Drugą drogę z antresoli poprowadzić **klatką A wyprowadzoną do +30,90** (galeria zachodnia, I1).
- Kuluar obudować EI 30 z drzwiami dymoszczelnymi.
- Zespół sala + antresola + hol dwukondygnacyjny NW potraktować jako jedną strefę dymową z oddymianiem mechanicznym. Kuluar zabezpieczyć przed zadymieniem.

### I5. Trzony za małe; kabiny i holy windowe niezgodne z PN-EN 81-20 i M.13 [S6]

- **Trzon B** ma obrys 6,25 × 9,4 m, wnętrze ≈ 5,75 × 8,9 m. Ma pomieścić klatkę (2 × 1,60 + 0,20 = 3,40 × 6,2 m + MOE), przedsionek 2,4 × 3,0, P1, P2 i T (2 000 kg).
  - Trzy szyby 2,85 + 2,85 + 3,2 + ściany = 9,3 m nie mieszczą się na 8,9 m, a szyb T (2,2 m) nie mieści się w pasie 2,15 m obok klatki.
  - Szacunek: potrzeba ≈ 64 m², jest 58,75 m², **brak ≈ 5 m²**. Trzon A jest na granicy (61 / 60,5 m²).
- **P1/P2 „1 275 kg, kabina 1,4 × 2,4 m”:** 3,36 m² > 2,95 m² (maksimum dla 1 275 kg wg PN-EN 81-20). M.13 s. 172 wymaga kabiny nieprzelotowej 1,5 × 2,1 m.
- Przed dźwigami M.13 wymaga 3,6 m (lub wnęki ≥ 2 m szerokości). Spec. ma 1,80 m na piętrach, 2,25 m w kuluarze S, 1,40 m w korytarzu S i 1,25–1,55 m na antresoli (dwie ostatnie poniżej WT § 195, por. K2).
- A1/A2 otwierają się na pd. na parterze (hala), a na S na pn. (W7). Wymaga to kabin przelotowych, czego spec. nie podaje.

**Poprawka:**
- **Dźwig T przenieść do segmentu:** własny szyb u 21,5–24,5 × v −0,5…−3,7, przystanki −1…4. Bar S obsługuje A2 (poza sesją) albo P1.
- Trzon B = klatka + przedsionek + P1 + P2, ≈ 55 m² ≤ 58,75 m² ✔.
- P1, P2, A1, A2: **1 600 kg, kabiny 1,5 × 2,1 m**, A1/A2 przelotowe.
- Na kondygnacjach 1–6: wnęki windowe 1,6 m obok korytarza 2,0 m (razem 3,6 m) w strefie środkowej.

### I6. MDS 560 os. bez wyjść zapasowych i bez sanitariatów; brak WC dostępnego na −1/−2 [S5, S7c]

- Wymóg: MDS ≥ PU/15 = 560 os. Rozp. MSWiA (Dz.U. 2025 poz. 932) § 6 (wg `ppoz.md` rozdz. 13) wymaga:
  - **3 wyjść ewakuacyjnych** (ceil(560/200));
  - **2 wyjść zapasowych poza strefą zagruzowania** (H/3 = 12,5 m od wieży);
  - w wariancie „2 klatki ≥ 15 m” pojemność jest ograniczona do **≤ 300 os.**
- Spec. ma klatki A i B (20 m) + rampę, czyli wariant ograniczony do 300 osób.
- Brak sanitariatów MDS / ukrycia (PPM.04). Spec. ma tylko „magazyn MDS 20 m²”.
- Brak toalety dostępnej na −1, choć jest tam 6 miejsc OzN (WT § 86 dla kondygnacji dostępnej, M.13 „na każdej kondygnacji”).

**Poprawka:**
- −2 (ukrycie) ≤ 300 os.: wyjścia klatkami A i B.
- −1 (MDS) 260 os.: klatka C, rampa oraz **szyb wyjścia zapasowego w (e 91,75; n 32,00)** z tunelem 5,6 m od obrysu −1.
  - Odległości: 12,6 m od wieży (≥ 12,5), 19,3 m od skrzydła, 8,4 m od segmentu, 8,5 m od najbliższego drzewa, poza ogródkami (sprawdzone na `site.json`).
- **Sanitariaty MDS 30 m²** na −1 przy trzonie A (2 WC + 1 toaleta dostępna + umywalki, woda awaryjna), pełniące też funkcję WC dostępnego garażu.
- Koszt do wyceny w F.14.B (szyb, tunel, sanitariaty: rząd kilkuset tys. zł, w zapasie 3,8 mln).

### I7. Ryzyko wykładni Wyj. 21 odp. 85 bez planu B

Gabinety Przewodniczącego i Wiceprzewodniczących oraz 2 sale po 20 os. leżą na kond. 6. Streszczenie wyjaśnień (§ 3 pkt 12) zaleca podejście ostrożne: te pomieszczenia na kondygnacji sali. Przy wykładni ostrożnej S musiałaby przyjąć dodatkowe ≈ 250 m² netto, a S-2 ma zapas 0,6 m², więc **koncepcja nie ma wariantu awaryjnego**.

**Poprawka:**
- Na planszy P5 i w opisie podać jawne uzasadnienie: PU s. 7 opisuje te pomieszczenia „w tej strefie” (KS), a Organizator pisze o „Kancelarii Sejmiku, opisanej na str. 7”.
- Pokazać bezpośrednie połączenie kond. 6 ↔ S (A1/A2 i klatka A, ≤ 15 m od gabinetu Przewodniczącego do holu S).
- W ryzykach resztkowych dodać pozycję „wykładnia KS”.

### I8. Dwie sale spotkań KS na 20 os. (2 × 44 m²) bez okien – ta sama wada, za którą sędziowie zganili K5 (korekta nr 8)

Na kond. 6 nie ma jednostek elewacyjnych, którymi dałoby się to naprawić (I2).

**Poprawka:**
- Przynajmniej jedna sala przy elewacji kosztem przeniesienia wydziału DRA 5.3 (4 pokoje) na kond. 5 i sali narad z kond. 5 do strefy środkowej z doświetleniem pośrednim. Wymaga to ponownego bilansu I2.
- Albo: obie sale z przeszkleniem do pokoi narożnych i świetlikiem pośrednim, z jawnym uzasadnieniem w opisie (sale okresowego użytku, uzgodnienie z PWIS).

---

## 4. Błędy DROBNE

| # | Błąd | Dowód | Poprawka |
|---|---|---|---|
| D1 | Ściany wewnętrzne S mają średnio **0,151 m** (36,8 m² = 3,2 % PC). Ściana pd. sali dźwiga ruszt 19,5 m, antresolę i galerię, a narysowano ją jako 0,15 m. Ściany komisji i klubów (poufność, Rw ≥ 50 dB) też mają 0,15 m. | [S1] 244 m ścian; przy 0,30 / 0,20 m potrzeba ≈ 52 m² (+15 m²; razem 10,3 % PC) | Ściana pd. sali żelbetowa 0,30 m, przegrody sal 0,20 m. Ująć w S-2 (K2). |
| D2 | Wymagany parking podany jako „99”. | 12/1000 × (8 400 − 92) + 6/1000 × 92 = 100,2, czyli **101**; program: 103; z holami: **110 > 109** | Poprawić na 101. Wariant „z holami” 110 pokryć przez +1 m.p. na −2 (pas 7 m) albo jawnie przyjąć PU bez RU. |
| D3 | Pokoje socjalne „do 30 os.” | Kond. 1: 97 os. na 3 × 30; kond. 6: 34 os. na 1 × 30 | Kond. 1: 4. pokój socjalny 24 m² w nieoświetlonym pasie zach. wieży. Kond. 6: drugi pokój socjalny 12–24 m² w strefie środkowej. Razem 17 („około 15” wg PU). |
| D4 | Zaplecze sanitarne rowerowni na −1. | PR.02: „bezpośrednie sąsiedztwo” | Przenieść do u 0,5–8,15 × v 12,45–20,85 (P) w miejsce szatni personelu. Szatnie personelu przenieść na −1. |
| D5 | Sala 200 os.: 226,8 m² zawiera 2 reżyserki po 10 m². | Netto **206,8 < 220** (min SK.01) | Reżyserki wydzielić poza obrys sali, np. s 39,6–40,9 kosztem foyer (80 → 66 m², min 60). |
| D6 | Jedna mównica z blatem 0,75–0,80 m. | M.13 s. 220: mównica stojąca 1,0–1,2 m i siedząca 0,75–0,80 m | Mównica z regulacją 0,75–1,20 m albo dwie mównice. |
| D7 | Wentylacja wyporowa „spod rzędów” bez plenum (warstwa posadzki S tylko 0,15 m). Obniżenie płyty o 0,4 m daje pod salą na kond. 6 **2,92 m < 3,0 m** (sale 20 os.). | Rzędne 4.2 | Plenum w podestach rzędów (+0,15…+0,60 przy 4 rzędach), nawiew przez stopnie. Płyty nie obniżać. |
| D8 | Szachty zbiorcze czerpni (kond. 1) i wyrzutni (korona S) oraz piony central P i S z −1 nie występują w rzutach ani w bilansie S. | ≈ 41 000 m³/h, czyli 2 × ≈ 2,3 m² na kondygnację; wyrzutnia musi przejść przez pas pd. S | Szachty w trzonie B (po przeniesieniu T) i w strefie środkowej. Ująć w bilansie S. |
| D9 | MOE 0,9 × 1,4 m. | `dostepnosc.md` pkt 8 zaleca 1,5 × 1,5 m poza biegiem; projekt WT przewiduje 1,5 × 3,0 m | Pole 1,5 × 1,5 m na podestach (wpływa na I5). |
| D10 | Taras nad Oławą: wykończenie +19,80 = posadzka kond. 5, strop segmentu +19,50. | 0,30 m nie wystarcza na izolację, spadki, nawierzchnię, retencję 10 m³ i donice | Strop segmentu obniżyć do +19,10. Segment na kond. 4 ma wtedy 2,87 m w świetle (pokoje ≤ 3 os.: ≥ 2,5 m ✔). |
| D11 | Pomieszczenia głębokie (sale narad 7,90 m, GW 8,10 m, magazynki 9,25 m) przecinają pas korytarza 6,10 \| 1,80 m. Przy trzonie A korytarz pn. jest wtedy zablokowany (v 19,3–21,1 wobec trzonu do v 20,85). Magazynek 2,6 m szerokości jest słabo „zamienny na biuro”. | 4.2 / 6 spec. | GW głębokie tylko na elewacji pd. (u 0–21, 5–6 szt.) i wsch. (v 9,9–15,7). Magazynki standardowe 4,05 × 6,10 m tam, gdzie I2 daje zapas. |
| D12 | JSON skrzydła niepoprawny: kolec (68,766; 64,397) → (68,372; 63,74) → (68,766; 64,397), a nos inny niż w MD ((63,840; 68,701) → (67,494; 69,592)). | [S0] polygon invalid; wcięcie ≈ 2,6 m² przy narożu NW wieży | Ujednolicić obrys JSON z MD, usunąć kolec. |
| D13 | SWD.15 ma 5,9 m² (< 6). SWD.10a dostępne tylko przez salę komisji 50 os. | [S1a, S1c] | SWD.15 pominąć (pozycja nieobowiązkowa, S-2). SWD.10a: dopuszczalne, opisać. |
| D14 | PHS.05b ma 2,0 m szerokości. | Kabina dostępna z transferem obustronnym wymaga ≥ 2,2 m | Jak w S-2 (WC K 2,85 × 6,45 m). |
| D15 | Archiwum PZGiK (szafy jezdne 12–15 kN/m²) na płycie 0,28 m o rozpiętości 8,1 m bez wzmocnienia. Centrum monitoringu (stałe stanowisko 24/7) w nieoświetlonym pasie zach. wieży na P. | 6 spec.; WT § 57, bhp | Strefa płyty 0,40 m z belkami pod archiwum, gaszenie gazem. Monitoring przenieść do pasa przy łączniku od skweru (u 0,5–13,35 × v 21–29,2, okna pn.). |
| D16 | „Dojście z drogi pożarowej do dźwigu R ok. 37 m”. Lobby Wejścia Obywatelskiego (u 31,25–39,5 × v 0,5–7,45) nie łączy się z halą: kieszeń u 31,1–33,4 × v 7,45–10,05 zamykają kancelaria i DK II (szczeliny 0,15 m). | Jedyna trasa prowadzi przez Bramę Mostową: ≈ 19 m na zewnątrz + ≈ 21 m w hali + 3 m przedsionka ≈ **43 m** (≤ 50 ✔) | Poprawić liczbę i opis trasy. Rozważyć przejście 1,5 m z lobby do hali. |

---

## 5. Tabela kontrolna (zakres zlecenia → wynik)

| Pozycja | Wynik |
|---|---|
| Kondygnacja Sejmiku mieści program z powierzchniami | **NIE** (K2). Hol 79,9 m² zawiera bar i szatnię; SWD.03 to korytarz; PD i pomieszczenie porządkowe nie istnieją. |
| Netto vs PC, korytarze/kuluary, ściany ≥ 8–10 % | PC 1 145,8 m²; wnętrze 1 080,1 m²; pomieszczenia 836,3 m²; trzony 119,2 m²; komunikacja KUL 87,8 + korytarze holu 32,2 = 120 m² (10,5 %); ściany 9,0 % PC (wewnętrzne 3,2 %, za cienkie – D1) |
| 44 stałe stanowiska + media + PJM + publiczność ≤ 100 | 100 ✔. **44 + pochylnie + wózki się nie mieszczą** (K3). Media i goście bez miejsca. |
| Dostęp pochylniami | Zasada ✔ (5 %). Geometria ✗ (K3). |
| Prezydium nie pod światło | ✔. Publiczność nie widzi prezydium, radni pod światło dla publiczności (I1). |
| 187 pokoi i rozbicie na departamenty, bez mieszania działów | ✔ suma i podział. **Kond. 6 brakuje 1–2 pokoi** (I2). |
| GW z archiwum na tej samej kondygnacji | ✔ (kond. 3). Płyta pod archiwum (D15). |
| 6 sal narad / 15 socjalnych / 20 magazynków | ✔ liczba. Socjalne na kond. 1 i 6 za małe (D3). Sale KS bez okien (I8). |
| WC na każdej kondygnacji | 1–6, P, S ✔ (WC M na S bez dostępu – K1). −1/−2 ✗ (I6). Powierzchnie −157 m² (I3). |
| Komfortka | ✔ |
| Ewakuacja: 2 klatki z przedsionkami, dojścia 30/60 (ZL III), ZL I | Klatki ✔, dojścia ✔. Pomieszczenia bez wyjścia (K1), schody w kuluarze (I4), trzony za małe (I5). |
| Dźwig dla ekip ratowniczych | ✔ (R w trzonie A; trasa ≈ 43 m – D16) |
| MDS w garażu | ✗ (I6) |
| Garaż ≥ minimum MPZP | ✔ 109 ≥ 101/103. Rachunek „99” błędny (D2). |
| Wysokości kondygnacji (biura ≥ 2,5–3,0 m) | ✔ 3,32 / 3,20 m. Ryzyka: plenum sali (D7), taras (D10). |

## 6. Kolejność poprawek

1. K1 + K2 + K3 + I1 + I4 razem, jako jeden rzut S-2. Zmiany: antresola 180 m², galeria zachodnia, klatka A do +30,90, 4 rzędy, przeplanowanie WC i dojść.
2. I5: dźwig T do segmentu, kabiny 1 600 kg 1,5 × 2,1 m (warunek S-2).
3. I2 + I8: przesunięcia między kondygnacjami 1, 4, 5 i 6.
4. I3 i I6: WC, MDS, szyb (91,75; 32,00).
5. Drobne: liczby w opisie (D2, D16), JSON (D12), detale (D7, D10, D15).

## Załącznik – kluczowe wyniki skryptu

```
SWD.02 = 79.9 m²: narożnik NW 47.8 m² + pasaż 15.8 m² (1,50) + korytarz pn. 16.4 m² (1,40); wolny hol po barze i szatni = 5.8 m²
Program SWD.02+05+06 = 205 m² (min 162); w rzucie 79.9 → deficyt 125 m² (do minimum 82)
SWD.11b / PHS.05a: styk z komunikacją 0.00 m → BRAK DOSTĘPU
Rząd 3 (R 9,0): wolny sektor 32.5°–159.0° → łuk 19.9 m; wymagane 22.5 (pulpit 1,0) / 26.1 (1,2) → NIE MIEŚCI
SPEC 3 rzędy: 40 (1,0) / 35 (1,2) stanowisk; POPRAWKA 4 rzędy: 56 / 48
kond. 6: potrzeba 25.00 j. / 24 → −1.00; po poprawce 23.00 / 24
WC: program 417 m², spec. 260 → −157 m²; 15.4 m²/zespół
Parking: 100.2 → 101 (spec. 99); MDS 560 os. → 3 wyjścia + 2 zapasowe (H/3 = 12.5 m)
Trzon B: ≈ 63.8 m² potrzebne vs 58.75 m²
S-2: poziom główny 1 079.5 / 1 080.1 m²; antresola 179.8 m² (16 %); hol RU 139.6 m²
```
