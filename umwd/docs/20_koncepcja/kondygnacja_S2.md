# Kondygnacja Sejmiku S-2 (+27,30) z antresolą (+30,90) – wariant „hol z galerią”

**Opracowanie scalone w v1.2 z `koncepcja_wybrana.md` (rozdz. 7) i `model/koncepcja.json["kondygnacja_sejmiku"]`** · 17.11.2026
**v1.2 (scalenie):** trzony wg poprawki I5 (`_v12_trzony.py`): trzon A wydłużony o 0,60 m na pd. (v 11,85–20,85; klatka A 3,40 × 5,80 m, przedsionek A 3,05 × 5,80 m; kuluar przy trzonie A 1,80 m), klatka B 3,40 × 6,64 m i przedsionek B 3,40 × 2,06 m; ewakuacja przeliczona bez tryskaczy (v1.1: nieprojektowane). Liczby niżej – stan po scaleniu (wydruki `_s2_*.py` po zmianie `_s2_model.py`).
**v1.2b (decyzje po scaleniu, `_v12b_decyzje.py`, `koncepcja_wybrana.md` rozdz. 17):** ściany klatek wzdłuż biegów 0,25 m z wnękami pochwytów (M.13 pkt 6 – 1,61 m w świetle poręczy; przedsionek A 3,05 m, szyby P1/P2 +0,05 m); ściana kuluaru od pd. 0,15 m (kuluar 2,25 m, przy trzonie A 1,80 m); łącznik KW.S.03 z polem mijania 1,80 × 2,00 m przed drzwiami przedsionka A (PHS.05a −0,80 m²); P2 bez przystanku na S; stopnie galerii 1,40 m.
**v1.2b-fix (po weryfikacji v1.2b):** pochwyty Ø 35 mm we wnękach 0,09 × 0,30 m (w pasie wnęki 0,16 m żelbetu – REI 120 ściany nośnej trzonu; 1,61 m w świetle poręczy bez zmian); drzwi przedsionek A → klatka A na S i +30,90 przy ścianie czołowej spocznika – otwór v 12,05–13,20 (w świetle 1,05 m = 0,6 m/100 os. × 175 os.), bieg przychodzący na S i +30,90 w pasie wsch. – przedłużenie pochwytu 0,30 m (M.13 Balustrady pkt 6) v 13,25–13,55 (S) i 13,53–13,83 (+30,90) bez kolizji z drzwiami; drzwi A' → klatka (ściana zach., +30,90) w pasie bez biegu – bez przedłużenia (`_v12_trzony.py` [T7]); stopnie galerii w świetle poręczy 1,23 m.
**v1.2 – poprawki po weryfikacji scalenia (17.11.2026):** schody reprezentacyjne w całości w pustce holu (otwór w antresoli, spocznik 1,50, pole 1,53 m przed stopą; test prześwitu [G2]); galeria z zatoką +0,00 dla wózków i podestem rzędu 2 z przejściem tylnym (20 + 3 miejsca; test kolizji i osiągalności [G2], linie wzroku [S3]); dojścia ewakuacyjne liczone dla wszystkich drzwi, bez zwiększeń (drzwi przedsionka B w u 27,80, zamiana PP.06 ↔ SWD.07, drzwi SWD.12a w u 5,70, toaleta publiczności na końcu korytarza, korytarz publiczny do przedsionka A, hol jako komunikacja ogólna – [E2]); przedsionek A' 2,50 × 3,00 m i test MOE [E6]; pełny otwór drzwi w [G3]. Rejestr: sekcja „v1.2 – poprawki po weryfikacji scalenia”.
Przedmiot: usunięcie błędów K1, K2, K3, I1, I4 (oraz D1, D6, D9, D13, D14 i części I3, I5) z `weryfikacja_program.md`.
Poprawkę weryfikatora „S-2” potraktowano jako hipotezę, sprawdzono ją i porównano z wariantami (rozdz. 2). Przyjęto wariant **S-3 „hol z galerią”**: zachowuje szkielet S-2, ale inaczej rozwiązuje galerię, górny hol i rozdzielenie publiczności od radnych.
Nie korzystano z żadnych informacji o rzeczywistych pracach ani wynikach konkursu. Źródła: wyłącznie materiały repozytorium.

**Pliki**
* `kondygnacja_S2.json` – dane do scalenia w strukturze `kondygnacja_sejmiku` (poligony uv i en, rzędy, galeria, drzwi, układ trzonów, bilans).
* `img/s2_plan.png` – rzuty S i antresoli.
* `img/s2_przekroj.png` – przekrój linii wzroku z galerii.

**Dowody (uruchomienie z katalogu `umwd/`):**

| Skrypt | Zakres | Sekcje wydruku |
|---|---|---|
| `python3 docs/20_koncepcja/_s2_model.py` | geometria (jedno źródło) | – |
| `python3 docs/20_koncepcja/_s2_geometria.py` | poprawność, kolizje (w tym prześwit nad schodami, miejsca galerii), drzwi (pełny otwór), bilans, eksport JSON | [G1]–[G8] |
| `python3 docs/20_koncepcja/_s2_sala.py` | rzędy, pochylnie, linie wzroku, poufność, olśnienie, warianty | [S1]–[S7] |
| `python3 docs/20_koncepcja/_s2_ewakuacja.py` | ewakuacja (dojścia dla wszystkich drzwi), dźwigi, holy windowe, MOE | [E1]–[E6] |
| `python3 docs/20_koncepcja/_s2_rzut.py` | PNG | – |

Wszystkie liczby w tekście pochodzą z tych wydruków (shapely 2.2, układ uv wieży z `koncepcja.json`).

![Rzuty S i antresoli](img/s2_plan.png)

---

## 1. Decyzja projektowa w skrócie

1. **Sala obrad** pozostaje w narożu NE pod łukiem („Latarnia”). Ma 4 łukowe rzędy wokół mównicy w F = (27,50; 15,20), na podestach +0,00 / +0,09 / +0,18 / +0,27.
   * Przewyższenie 0,09 m na rozstaw 1,80 m daje dokładnie 5,0 %. Dzięki temu oba przejścia (wsch. promieniowe i zach. wzdłuż ściany sali) są pochylniami ≤ 5 % bez spoczników i bez traconych łuków na rampy styczne.
   * **47 stałych stanowisk:** 43 standardowe + 4 dla wózków, po jednym w każdym rzędzie przy pochylni.
   * Prezydium i mównica stoją na posadzce, przy pełnej ścianie pd.
2. **Galeria publiczności** (20 miejsc + 3 dla wózków) leży na antresoli **nad WC K/M i łącznikiem wsch.**, w pasie między trzonem A a salą (u 15,5–22,0 × v 12,6–22,65).
   * Do sali otwiera się balustradą szklaną 1,10 m na cokole 0,20 m. Ma 2 strome rzędy: rząd 1 na +0,00 (8 miejsc) i rząd 2 na podeście +0,90 (9 miejsc, przejście tylne 1,00 m), a na pn. końcu zatokę +0,00 z 3 miejscami dla wózków i 3 miejscami opiekunów, połączoną z foyer bez stopni.
   * Publiczność wchodzi z Wejścia Obywatelskiego dźwigami P1/P2: przystanek +30,90 → hol P1/P2 → chroniony korytarz nad kuluarem → galeria. Strefy radnych nie przecina.
   * Drogi ewakuacyjne z galerii prowadzą do przedsionka A (klatka A przedłużona do +30,90) i do przedsionka B (klatka B przedłużona do +30,90).
3. **Hol reprezentacyjny ma dwa poziomy.**
   * Dolny: pustka 2-kond. w narożu NW (okna pn. 1,65 × 5,0 na Ostrów Tumski i zach. na pl. Społeczny), hol dźwigów A1/A2 i szatnia.
   * Górny: antresola radnych z barem SWD.05 i strefą multimedialną SWD.03.
   * Poziomy łączą otwarte schody reprezentacyjne w pustce holu (bieg 2,0 m, 11 + 10 stopni, spocznik 1,50 m; nad całym biegiem otwarta przestrzeń – prześwit ≥ 3,26 m) i dźwigi A1/A2 (drzwi pn. także na +30,90).
   * Wolna podłoga holu wynosi **77,6 + 79,1 = 156,6 m²**. Szatnia (12,5 m²) i bar (32,0 m²) są liczone osobno.
4. **Wszystkie pomieszczenia zamknięte programu leżą na poziomie głównym** i mają drzwi na komunikację:
   * 4 kluby;
   * 2 sale komisji z zapleczami;
   * wspólna sala radnych;
   * pokój socjalny;
   * reżyserka;
   * pokój matki z dzieckiem;
   * magazyn;
   * WC K i M (każde z kabiną dostępną);
   * pomieszczenie porządkowe;
   * PD.

   Na antresoli są tylko strefy otwarte, galeria i dojścia publiczności. Zamknięte przegrodami są hol P1/P2, korytarz publiczny, toaleta publiczności i przedsionek A' (rozdz. 7).
5. **Elewacje bez zmian.** Antresola jest wszędzie odsunięta ≥ 1,35 m od lica elewacji; w pasie przyelewacyjnym jest jej 0,00 m² [G6]. Okna 1,65 × 4,20 m (pd., zach.) i 1,65 × 5,00 m (pn.) zachowują pełną wysokość.
   * Jedyna zmiana jest niewidoczna z zewnątrz: pierwsze 2,4 m łuku przy reżyserce (φ 0–10°) dostaje szkło nieprzezierne za lamelami [S5].
6. **Trzony (v1.2, I5):** trzon A wydłużony o 0,60 m na pd. (v 11,85–20,85), trzon B bez zmiany obrysu. Układ wewnętrzny:
   * trzon A: dźwigi A1/A2 (1 600 kg, kabina 1,5 × 2,1) w pasie pn. z drzwiami na pn.; dźwig R z drzwiami do przedsionka A; klatka A 3,40 × 5,80 m i przedsionek A 3,05 × 5,80 m w pasie pd. (v1.2b: ściana klatki 0,25 m z wnęką pochwytu);
   * trzon B: dźwig T przeniesiony do segmentu, P1/P2 (1 600 kg) z drzwiami wsch., szachty w miejscu T; klatka B 3,40 × 6,64 m, przedsionek B 3,40 × 2,06 m.

   Biegi i spoczniki na wszystkich kondygnacjach – `_v12_trzony.py`; rozdz. 9.

---

## 2. Weryfikacja hipotezy S-2 i porównanie wariantów

| Kryterium | v1.0 (spec.) | S-2 (weryfikator) | **S-3 (przyjęty)** | Dowód |
|---|---|---|---|---|
| Galeria – położenie | pd., nad prezydium | zach. nad reżyserką/WC | zach. nad WC K/M i łącznikiem wsch., między trzonem A a salą | [S3], [S6] |
| Kąt patrzenia na prezydium (0° = na wprost) | ~180° (nad głową) | 56°–90° (mediana 77°) | **35°–86° (mediana 64°)** | [S3] |
| Linia wzroku galerii (C ≥ 60 mm) | nie | nie sprawdzano (płaskie rzędy co 1,0 m) | **C ≥ 158 mm** do wszystkich 4 członków prezydium i mówcy; zapas nad cokołem ≥ 289 mm; nad balustradą podestu ≥ 36 mm | [S3] |
| Galeria w łuku NE (za radnymi, widok frontalny) | – | – | odrzucona: przy głęb. 2,5 / 3,3 m mieści się tylko 38 / 31 stanowisk; 1-rzędowa (głęb. 1,5 m) nie mieści miejsc dla wózków (wymagają ≥ 2,6 m → ≤ 38 stanowisk) | [S6] |
| Stanowiska radnych | 44 deklarowane (40 możliwe) | 48 (bez geometrii pochylni) | **47 = 43 + 4 dla wózków** z geometrią przejść 5 % | [S1] |
| Antresola | 69,7 m² | 179,8 m² | **293,0 m²** (radni 150,9 + publiczność 142,1) | [G6] |
| Rozdział publiczność / radni na antresoli | – | wspólna płyta (galeria + bar + hol górny) | dwie oddzielne antresole przedzielone ścianą i pustką sali | [G6], rys. |
| Dostęp do baru/hol górny | – | tylko dźwig lub klatka ppoż. | schody reprezentacyjne w pustce holu (cały bieg pod otwartą przestrzenią) + A1/A2 | [G2], rys. |
| Płyta nad klubami zach. a okna 4,20 m | – | płyta do elewacji (kolizja z oknami) | wycofanie 1,35 m, okna bez zmian | [G6] |
| Hol (bez szatni i baru) | 5,8 m² realnie | 139,6 m² (70,3 + 69,3) | **156,6 m²** (77,6 + 79,1) | [G4] |
| WC na S | 25,3 m² + PHS.05c bez wyjścia | 40 m² | **41,4 m²**: K 17,6 (v1.2b: wnęka pola mijania łącznika) + M 18,4 (kabiny dostępne 2,2 m) + publiczna 5,5 | [G4] |
| Ściany wewn. – średnio | 0,151 m | 47 m² (szac.) | **0,222 m** (100 % ≥ 0,18 m; ściany sali 0,30 m) | [G5] |
| M.13: 3,6 m przed dźwigami | nie | „nie da się” | **A1/A2 ≥ 3,75 m (A2 7,00–8,35 m); P1/P2 na +30,90 3,60 m** – od lica trzonu, bez biegu schodów | [E5] |

**Wnioski z weryfikacji S-2.** Kierunek S-2 jest słuszny: antresola ~ 2–3 × większa, klatka A do +30,90, 4 rzędy, galeria zach. Rozwiązanie S-2 ma jednak cztery słabości:
* mieszanie publiczności z barem i holem radnych na jednej płycie;
* bar osiągalny tylko dźwigiem lub klatką ewakuacyjną;
* płytę antresoli wchodzącą w okna 4,20 m klubów zach.;
* płaskie rzędy galerii bez sprawdzenia linii wzroku.

S-3 usuwa te słabości. Kosztem jest większa antresola (rozdz. 9, pkt 3).

---

## 3. Pomieszczenia i bilans powierzchni (netto z poligonów, PN-ISO 9836) [G4]

| Kod | Pomieszczenie | Poziom | Pow. [m²] | Program [m²] | Zakres | Δ [m²] |
|---|---|---|---:|---:|---|---:|
| SWD.01 | Sala obrad – płyta (47 stanowisk, prezydium, mównica, goście 12, media 8, obsługa 4, PJM 2) | S | 232,0 | | | |
| SWD.01g | Galeria publiczności (część SWD.01): rząd 1 +0,00 – 8, rząd 2 +0,90 – 9, zatoka – 3 miejsca dla wózków + 3 opiekunów (20 + 3) | ANT | 65,3 | | | |
| **SWD.01** | **razem** | | **297,3** | 320 | 280–380 ✔ | −22,7 |
| SWD.02 | Hol reprezentacyjny – poziom dolny (pustka 2-kond. NW ze schodami, hol dźwigów, pas pn.) | S | 77,6 | | | |
| SWD.02g | Hol reprezentacyjny – poziom górny (antresola radnych) | ANT | 79,1 | | | |
| **SWD.02** | **razem (wolna podłoga, bez szatni i baru)** | | **156,6** | 150 | 120–220 ✔ | +6,6 |
| SWD.03 | Sala multimedialna / poczekalnia gości – strefa otwarta na antresoli holu, 20 miejsc, ekran, głośniki kierunkowe, pętla | ANT | 32,3 | 40 | 30–60 ✔ | −7,7 |
| SWD.04 | Reżyserka (przeszklenie zach. na prezydium, pn. na rzędy) | S | 17,6 | 20 | 15–30 ✔ | −2,4 |
| SWD.05 | Przestrzeń socjalno-gastronomiczna (bar z przyłączami) | ANT | 32,0 | 40 | 30–60 ✔ | −8,0 |
| SWD.06 | Szatnia – lada 4,1 m + wieszaki (otwarta na hol, 1,35 m od okna) | S | 12,5 | 15 | 12–20 ✔ | −2,5 |
| SWD.07 | Pokój matki z dzieckiem (naroże E, okna wsch.) | S | 11,8 | 10 | 8–12 ✔ | +1,8 |
| SWD.08 | Sala komisji 50 os. | S | 90,5 | 100 | 90–120 ✔ | −9,5 |
| SWD.09 | Sala komisji 30 os. | S | 54,3 | 60 | 54–72 ✔ | −5,7 |
| SWD.10a | Zaplecze nagrań komisji 50 os. (okno do SWD.08, drzwi do kuluaru) | S | 8,7 | 10 | 8–12 ✔ | −1,3 |
| SWD.10b | Zaplecze nagrań komisji 30 os. (okno do SWD.09, drzwi do kuluaru) | S | 8,7 | 10 | 8–12 ✔ | −1,3 |
| SWD.11a | Klub radnych 30 os. (1) | S | 54,5 | 60 | 54–72 ✔ | −5,5 |
| SWD.11b | Klub radnych 30 os. (2), naroże SE (okna pd. i wsch.) | S | 55,4 | 60 | 54–72 ✔ | −4,6 |
| SWD.12a | Klub radnych 15 os. (1) (okno zach.; drzwi przy wsch. końcu ściany pd.) | S | 30,2 | 36 | 30–40 ✔ | −5,8 |
| SWD.12b | Klub radnych 15 os. (2) (okno zach.) | S | 30,2 | 36 | 30–40 ✔ | −5,8 |
| SWD.13 | Wspólna sala radnych (okno pn. – Ostrów Tumski) | S | 36,2 | 48 | 36–60 ✔ | −11,8 |
| SWD.14 | Pokój socjalny radnych (aneks kuchenny, okno pn.) | S | 20,0 | 24 | 20–30 ✔ | −4,0 |
| SWD.15 | Magazyn podręczny (pod spocznikiem i górnym biegiem schodów, h 1,7–2,6 m) | S | 6,0 | 10 | 6–15 ✔ | −4,0 |
| PHS.05a | WC damskie: kabina dostępna 2,2 × 2,5 + 2 kabiny + umywalki | S | 17,6 | | | |
| PHS.05b | WC męskie: kabina dostępna 2,2 × 2,5 + kabina + 2 pisuary + umywalki | S | 18,4 | | | |
| PHS.05c | Toaleta dostępna publiczności (wsch. koniec korytarza publicznego, przy holu P1/P2) | ANT | 5,5 | | | |
| **PHS.05** | **razem** | | **41,4** | 45 | 35–60 ✔ | −3,6 |
| PP.06 | Pomieszczenie porządkowe (1,60 × 2,60 m) | S | 4,2 | 6 | 4–8 ✔ | −1,8 |
| IT.02 | Punkt dystrybucyjny IT (przy zapleczach nagrań) | S | 4,8 | 6 | 4–10 ✔ | −1,2 |
| | **Suma programu (SWD + PHS.05 + PP.06 + IT.02)** | | **1 005,2** | 1 106 | min 928 | **+77,2 nad minimum** |

Wszystkie pozycje mieszczą się w zakresach programu (SWD.01 i SWD.02 liczone łącznie z częścią na antresoli). Projekt jest o 100,8 m² poniżej sumy wartości środkowych programu i o 77,2 m² nad sumą dolnych granic. S-2 miało przy wszystkich minimach zapas 0,6 m².

**Bilans poziomu S [G5]:**

| Składnik | m² |
|---|---:|
| Pomieszczenia (z salą, holem i szatnią) | 791,0 |
| Komunikacja: kuluar 85,5 + pasaż 15,4 + łącznik 12,8 + dojście 4,2 + dolny bieg schodów 5,6 | 123,4 |
| Trzony (A 64,8 – v1.2; B 58,8) | 123,6 |
| Ściany wewnętrzne | 42,2 |
| **Wnętrze od lica wewnętrznego** | **1 080,2** |
| Ściany zewnętrzne | 65,6 |
| **PC poziomu S** | **1 145,8** |

Ściany zewn. i wewn. stanowią 9,6 % PC.

**Antresola +30,90 [G6]: 293,0 m², czyli 25,6 % rzutu wieży.**

| Część | Składniki | m² |
|---|---|---:|
| Radni | hol górny 79,1 + bar 32,0 + strefa multimedialna 32,3 + przedsionek A' 7,5 | 150,9 |
| Publiczność | galeria 65,3 + hol P1/P2 22,0 + korytarz 49,4 + WC 5,5 | 142,1 |

Zamknięte przegrodami: hol P1/P2 21,96 + korytarz publiczny 49,35 + toaleta 5,50 + przedsionek A' 7,50 = **84,31 m² = 28,8 % antresoli** (54 % części publicznej). Otwarte: galeria i hol górny z barem i strefą multimedialną – 208,70 m².

**Schody reprezentacyjne [G2]:** 21 st. × 17,14 cm (11 + 10), 19 stopnic × 0,28 + spocznik 1,50 = 6,82 m; stopa u 10,92 (S), wierzch u 4,10 (+30,90), bieg 2,0 m. Rzut biegu 13,64 m² w całości w pustce (pod płytą antresoli 0,00 m²) – otwór w antresoli u 8,30–10,92 × v 24,60–27,85, podest górny skrócony do u 4,10; najmniejszy prześwit nad linią krawędzi stopni 3,26 m. Płaskie pole przed stopą 1,53 m, przed wierzchem ≥ 1,50 m. Przed korektą (v1.2 przed weryfikacją) bieg u 5,10–12,30 stał w 8,0 m² pod płytą antresoli (prześwit 1,41–1,59 m) i miał 0,15 m przed stopą.

Pod antresolą jest 3,30 m w świetle (kluby, WC, pasaż, sala wspólna, pokój socjalny – ≥ 3,0 m wg WT § 72). Nad nią do spodu kratownic jest 3,25 m.

---

## 4. Opis kondygnacji

**Poziom S (+27,30).**
* **Pas pd. (okna 1,65 × 4,20 m):**
  * SWD.08 i SWD.09 z zapleczami nagrań SWD.10a/b (okna do sal, drzwi do kuluaru) oraz PD przy zapleczach;
  * klub SWD.11a przy trzonie B;
  * w narożu SE klub SWD.11b z dojściem 1,6 × 2,6 m z kuluaru (przewężenie miejscowe ≤ 5 m – M.13; v1.2b: P2 bez przystanku na S), obok pomieszczenie porządkowe (1,60 × 2,60 m) i pokój matki z dzieckiem (4,80 × 2,45 m, okna wsch.) – drzwi obu przy zach. końcu (u 33,70 i 35,20), dojście do przedsionka B ≤ 10 m.
* **Kuluar 2,25 m** (przy trzonie A 1,80 m na 7,20 m – v1.2b: ściana od pd. 0,15 m) łączy klatki A i B i jest drogą chronioną (EI 30, drzwi S, oddymianie). Jego końce zach. i wsch. mają pełną wysokość z oknami; środkowa część (u 12,15–34,70) ma 3,30 m pod korytarzem publicznym, a odcinek u 34,90–37,40 – pod toaletą publiczności.
* **Pas zach.:** kluby 15 os. z oknami zach. (drzwi SWD.12a w u 5,70 – przy wsch. końcu ściany pd.) oraz pasaż 1,8 m wzdłuż trzonu A (kuluar ↔ hol).
* **Między trzonem A a salą:** łącznik 1,4 m z polem mijania 1,80 × 2,00 m przed drzwiami przedsionka A (v1.2b; przewężenia 3,30 i 3,25 m ≤ 5 m) oraz WC K i WC M, oba z drzwiami do holu.
* **Pas pn.:** pokój socjalny i wspólna sala radnych z oknami 1,65 × 5,0 m. Dalej na zachód hol: w narożu NW pustka 2-kond. z oknami pn. i zach., szatnia, schody reprezentacyjne (cały bieg w pustce, stopa u 10,92 z płaskim polem 1,53 m), a pod spocznikiem i górnym biegiem magazyn.
* **Hol dźwigów A1/A2:** drzwi pn. dźwigów otwierają się wprost do holu (kadr W7); wolna głębokość od lica trzonu przed A1 3,75 m (do biegu schodów), przed A2 8,35 m [E5].
* **Sala:** wejście główne radnych i gości z holu (NW, 1,6 m); wyjścia SW (1,2 m) i SE (1,6 m) do kuluaru; drzwi prezydium (1,0 m) za stołem. Reżyserka zajmuje naroże SE sali i ma przeszklenie na prezydium i na twarze radnych.

**Antresola +30,90.**
* **Część radnych** (górny hol, otwarty na pustkę holu krawędzią 21,8 m):
  * bar nad salą wspólną, z widokiem przez okna pn.;
  * strefa multimedialna nad klubami (z dala od sali obrad, za ścianą 0,30 m i pustką holu; głośniki kierunkowe, pętla, napisy);
  * przedsionek A' 2,50 × 3,00 m – drugie wejście do klatki A (drzwi pn. w u 7,70, drzwi do klatki 1,0 m przy spoczniku);
  * nad biegiem schodów – otwór w płycie (u 8,30–10,92 × v 24,60–27,85), lobby przed A1/A2 3,75 m (A1) / 7,00 m (A2).
* **Część publiczna:**
  * hol P1/P2 (3,6 × 6,1 m);
  * korytarz EI 30 nad kuluarem z drzwiami do przedsionków B (u 27,80) i A (u 13,70 – odcinek zach. nad kuluarem przy trzonie A) oraz toaletą dostępną na wsch. końcu;
  * galeria z foyer (przedsionek A otwiera się na foyer), podestem rzędu 2 i zatoką dla wózków.

Galeria jest przedzielona od baru ścianą (v 22,65–22,85) i jest otwarta tylko na salę (krawędź 10,2 m).

---

## 5. Sala obrad – stanowiska, pochylnie, linie wzroku [S1]–[S7]

| Rząd | Krawędź pulpitu R | Podest | Sektor | Stanowiska | Wózek |
|---|---:|---:|---|---:|---|
| 1 | 4,50 m | +0,00 | 23,8°–121,3° | 7 + 1 | koniec zach., na posadzce |
| 2 | 6,30 m | +0,09 | 21,4°–113,5° | 10 + 1 | koniec zach., przy pochylni |
| 3 | 8,10 m | +0,18 | 20,1°–108,9° | 12 + 1 | jw. |
| 4 | 9,90 m | +0,27 | 19,2°–105,8° | 14 + 1 | jw. |
| **Razem** | | | | **43 + 4 = 47** (44 + 3 rezerwy) | pole 0,9 × 1,4 w każdym module ✔ |

* **Moduł stanowiska:** 1,00 m na linii siedzisk. Pulpit 0,60 m, za oparciami 0,85 m, rozstaw rzędów 1,80 m.
* **Prezydium** (4 os., stół 6,0 m) i **obsługa kancelaryjna** (2 + 2 przy końcach stołu) są na +0,00. **Mównica** stoi w F, ma blat regulowany 0,75–1,20 m (D6) i pętlę. **PJM** jest przy mównicy, w kadrze kamery. Odległość mównica – 1. rząd: 5,40 m (płyta na kamery).
* **Goście** (12, dwa rzędy w strefie NW za rzędem 4, przy drzwiach z holu) i **media** (8, łuk R 11,95 m za rzędem 4).
* **Płyta:** 47 + 4 + 4 + 2 + 12 + 8 = 77 miejsc (wymagane 70). Galeria: 20 + 3 dla wózków. Razem 100 [G7].
* **Pochylnie [S1]:**
  * przejście wsch. promieniowe 1,30 m – nachylenie 0,09/1,80 = **5,00 %**;
  * przejście zach. wzdłuż ściany sali – odcinki 3,90 / 4,39 / **4,61 %**, długość 8,61 m (< 9 m, podesty rzędów pełnią rolę spoczników);
  * szerokość przejścia 1,30 m = płaszczyzna ruchu 1,20 m między krawężnikami 0,07 m; poręcze 0,75 i 0,90 m w rozstawie **1,05 m w świetle** (WT § 71 ust. 1: 1,0–1,1 m);
  * równolegle przejście płaskie 1,10 m (drzwi z holu ↔ drzwi SW).
* **Linie wzroku radnych [S2]:**
  * do mówcy stojącego (1,60): C ≥ 111 mm (39/39 ✔);
  * do mówcy na wózku: 31/39 linii z C ≥ 60 mm lub linią między głowami;
  * do siedzącego prezydium: 125/156, min C nad rzędem przed 39 mm.

  Rzędy leżą na różnych promieniach, więc stanowiska są przestawione względem siebie, a linie na prezydium przechodzą przez wolną płytę. Pozostałe przypadki (C 39–60 mm) to linie skośne przy skrajnym stanowisku sąsiada. Uzupełnieniem są ekrany na pulpitach (standard systemu obrad).
* **Galeria – układ (v1.2 po weryfikacji, [G2]):** od balustrady (lico u 22,00; szkło 1,10 m na cokole pełnym 0,20 m):
  * **rząd 1 na +0,00** (u 20,90–21,90): 8 miejsc × 0,52 m, siedzisko 0,50 + przejście 0,45 m przed kolanami; dostęp przejściem 0,90 m od pd. (v 12,60–13,50) z foyer – rząd z dostępem z jednej strony ma ≤ 8 miejsc (zasada § 261);
  * **podest +0,90** (u 19,10–20,90 × v 13,50–18,30): rząd 2 – 9 miejsc (siedzisko 0,50 + 0,30 na nogi) i przejście tylne 1,00 m; 6 stopni 0,15 × 0,30 z foyer, szer. 1,40 m (v1.2b; w świetle poręczy 1,23 ≥ 1,20 – M.13; pochwyty Ø 35 mm); na krawędzi podestu przed rzędem 2 balustrada szklana 0,70 m (WT § 298 ust. 7), na bokach i z tyłu – balustrady (razem 11,8 mb); prześwit nad podestem do spodu kratownic 2,35 m;
  * **zatoka +0,00 na pn. końcu** (v 18,30–22,65): 3 miejsca dla wózków 0,90 × 1,40 przy balustradzie, każde z miejscem opiekuna obok i polem manewrowym 1,5 × 1,5 m, połączona z foyer bez stopni.
  * Test [G2]: miejsca +0,00 ∩ podest/stopnie 0,0000 m²; wszystkie miejsca osiągalne od obu drzwi galerii (rząd 1 przejściem ≥ 0,45 m – 8/8; opiekunowie 3/3; wózki – pole manewrowe wolne i przejście ≥ 0,90 m bez stopni 3/3; rząd 2 z przejścia tylnego 9/9). Wcześniejszy układ (v1.2 przed weryfikacją: podest rzędu 2 na całej długości, wózki i rząd 1 za nim) dawał kolizje 0,45 m² na każde miejsce dla wózka i rząd 1 bez dojścia – usunięty.
* **Galeria – linie wzroku [S3]:** oczy 1,20 m; oko rzędu 1 i wózków u 21,20, rzędu 2 u 20,40 (+0,90).
  * Do 4 członków prezydium: C rzędu 2 nad rzędem 1 ≥ **158 mm** (36/36); do przewodniczącego i wiceprzewodniczącego ≥ 333 mm.
  * Do mówcy siedzącego/stojącego: ≥ 393 / 438 mm.
  * Zapas nad cokołem 0,20 m ≥ 289 mm. Wyżej linia przechodzi przez szkło antyrefleksyjne balustrady 1,10 m (prześwit ≤ 0,12 m, WT § 298 ust. 2). Rząd 2 nad balustradą krawędzi podestu (0,70 m): zapas ≥ 36 mm we wszystkich przypadkach.
  * Głowy radnych nie leżą na liniach wzroku.
  * Kąt na prezydium: 35°–86° (mediana 64°), odległość 6,3–10,9 m. Miejsca dla wózków są w pn. części galerii (widok bardziej od przodu).
* **Poufność głosowania [S4]:** ekrany pulpitów odchylone ≤ 15° od pionu, z filtrem 4-kierunkowym ±30°. Najmniejszy kąt normalna ekranu – oko na galerii (siedzący i stojący przy balustradzie) wynosi **39,5°** – poza stożkiem filtra ✔. Do tego tryb głosowania tajnego w systemie.
* **Światło z przodu [S5]:** radni patrzą na prezydium przy pełnej ścianie pd.; szkło łuku i okna pn. są za nimi.
  * Najmniejszy kąt kierunek patrzenia – szkło: **51,1°** (pole centralne ±45° wolne ✔).
  * W polu 45°–60° jest tylko wsch. odcinek łuku, przez lamele promieniowe 0,25 × 0,60 co 0,90 m widać ≤ 29 % szkła.
  * Okno wsch. sali leży za reżyserką. Odcinek łuku φ 0–10° – szkło nieprzezierne za lamelami.
  * Prezydium patrzy na pn. (okna w polu ±71°, ≥ 10,7 m): lamele, rolety screen 5 %, światło TV. Galeria jest z boku, poza tłem radnych.

![Przekrój linii wzroku](img/s2_przekroj.png)

---

## 6. Ewakuacja, strefy, dźwigi [E1]–[E6]

* **Osoby i szerokości:** maks. 350 os. (płyta 77 i galeria 23 – z rzędów i miejsc modelu) → biegi 0,6 × 3,50 = 2,10 m ≤ 2 × 1,60 m ✔; kuluar 2,10 m ≤ 2,25 m ✔ (zapas 0,15 m); przy trzonie A 1,80 m (przepustowość 300 os.; odcinek obsługuje ≈ 84 os. z części zach.) ✔.
* **Sala:** 3 wyjścia + drzwi prezydium, odstęp ≥ 5 m, drzwi otwierane na zewnątrz.
* **Strefa ZL I:** S + antresola = 1 145,8 + 293,0 = **1 438,8 m² ≤ 2 500 m²** ✔.
* **Strefy dymowe [E3]:**
  1. sala + galeria – oddymianie spod dachu, napowietrzanie dołem;
  2. hol SWD.02 (komunikacja ogólna) + antresola radnych + schody reprezentacyjne – samoczynne oddymianie sterowane SSP;
  3. kuluar + korytarz publiczny + hol P1/P2 – samoczynne oddymianie sterowane SSP z napowietrzaniem (§ 247 ust. 1; bez nadciśnienia w korytarzach).

  Przedsionki A, A', B – nadciśnienie (§ 246 ust. 2). Oddymianie dróg jest wymagane przez § 247 ust. 1, ale nie służy do wydłużenia dojść.
* **Przedsionki i MOE [E6]** – MOE 1,5 × 1,5 m poza torem ewakuacji 1,2 m (prosta od drzwi wejściowych do drzwi klatki) i poza polem otwierania skrzydeł (test geometryczny, siatka 0,05 m):
  * A 3,05 × 5,80 m (S i +30,90; drzwi pd., wsch., R, klatka – v1.2b-fix: drzwi do klatki 1,15 m w v 12,05–13,20 przy ścianie czołowej spocznika) – MOE w narożu NW (S: u 12,20–13,70 × v 15,60–17,10; +30,90: v 14,95–16,45);
  * A' **2,50 × 3,00 m** (u 5,80–8,30; kosztem SWD.03: 33,8 → 32,3 m²) – drzwi pn. 1,2 m w u 7,70, drzwi do klatki 1,0 m w v 12,55–13,55 (przy spoczniku v 12,05–13,55) – MOE u 5,80–7,30 × v 12,50–14,00;
  * B 3,40 × 2,06 m – drzwi z kuluaru (S) i korytarza (+30,90) w **u 27,80**, drzwi do klatki w u 27,80 – MOE w narożu SW (u 25,10–26,60 × v 7,59–9,09).

  Przed korektą (A' 2,00 × 3,00 m z drzwiami do klatki 1,2 m w v 12,20–13,40 i drzwi B w u 27,0) MOE nie mieściło się poza torem w A' ani w B.
* **Bez schodów z antresoli do kuluaru (I4).** Kuluar jest obudowany EI 30. Hol z antresolą radnych oddzielają od niego drzwi EI 30 S w pasażu i łączniku.

**Dojścia [E2]** (ZL I, budynek W, tryskacze nieprojektowane – v1.1; **bez zwiększeń**):
* przejście 40 m; w pomieszczeniach > 5 m (sala, hol) +25 % → 50 m;
* dojście: 1 kierunek 10 m; 2 kierunki 40 m – dwie drogi do różnych klatek (A, B), rozłączne po odcinku wspólnym ≤ 10 m; zwiększenie +50 % za samoczynne oddymianie (§ 256 ust. 4 pkt 2) liczone tylko kontrolnie i niewykorzystywane;
* dojścia policzono dla wszystkich 27 drzwi pomieszczeń z `DOORS_S` i `DOORS_ANT` (oraz stref otwartych) najkrótszymi drogami po sieci osi: kuluar (v 11,20), pasaż, łącznik, dojście do SWD.11b, **hol SWD.02 jako komunikacja ogólna**, korytarz publiczny i hol P1/P2; antresola radnych – pomieszczenie otwarte z wyjściami: drzwi przedsionka A' i schody do holu.

| Pomieszczenie (drzwi) | Przejście [m] | Dojście do klatki [m] | Ocena |
|---|---:|---|---|
| Sala SWD.01 – drzwi SE / SW / prezydium / NW | 25,5 (≤ 50) | B 7,35 / B 7,65 (A 10,90) / B 2,75 / 2 kierunki A 31,95 i B 29,10 | ≤ 10 |
| Galeria SWD.01g – drzwi do przedsionka A / na korytarz | 9,4 | 0 / A 5,70 (B 12,85) | ≤ 10 |
| Antresola radnych (bar NE) → drzwi A' / → stopa schodów | 24,5 / 35,3 (≤ 40) | od stopy schodów: A 26,43 / B 32,58 (wspólny 2,43) | 2 kierunki |
| Toaleta publiczności PHS.05c | 2,5 | B 8,30 | ≤ 10 |
| SWD.11b / SWD.07 / SWD.04 / PP.06 – wsch. koniec kuluaru | 9,9 / 4,8 / 5,3 / 2,5 | B 9,40 / 9,90 / 9,75 / 8,40 | ≤ 10 |
| SWD.12a (drzwi u 5,70) | 7,1 | A 9,85 | ≤ 10 |
| SWD.12b (drzwi na pasaż) | 6,2 | A 17,10 / B 31,80 (wspólny 1,00) | 2 kierunki |
| SWD.08 – drzwi u 8,0 / u 4,0 | 9,8 | A 7,55 / A 29,80 i B 26,30 (wspólny 4,60) | ≤ 10 |
| WC M PHS.05b / szatnia SWD.06 / magazyn SWD.15 (z holu) | 8,1 / 4,4 / 2,2 | A 31,60 i B 28,75 (5,30) / A 19,30 i B 36,90 (4,65) / A 18,30 i B 35,90 (3,65) | 2 kierunki |
| SWD.09, SWD.10a/b, IT.02, SWD.11a, SWD.13, SWD.14, WC K PHS.05a | ≤ 10,7 | 2,60–8,85 | ≤ 10 |

**Wynik [E2]:** 17 pomieszczeń z dojściem ≤ 10 m (1 kierunek wystarcza), 5 z dwoma kierunkami do różnych klatek (PHS.05b, SWD.06, SWD.12b, SWD.15, antresola radnych); **0 dojść jednokierunkowych > 10 m, 0 wymagających zwiększeń, 0 niezgodnych**. Najdłuższe dojścia jednokierunkowe: SWD.12a 9,90; SWD.07 9,85; SWD.04 9,75; SWD.11b 9,35 m (v1.2b). Obie ślepe części kuluaru oceniono jedną regułą. Poprzednia wersja (ręczna lista dróg) pomijała SWD.07, SWD.04, SWD.12a i SWD.12b i opierała trzy dojścia na zwiększeniu +50 %; usunięto to przesunięciem drzwi przedsionka B (u 27,0 → 27,80), zamianą PP.06 ↔ SWD.07, przeniesieniem drzwi SWD.12a (u 3,4 → 5,70) i toalety publiczności na wsch. koniec korytarza oraz przedłużeniem korytarza publicznego do przedsionka A (drugi kierunek na +30,90).

Galeria (osoby na wózkach) ma MOE w przedsionku A z dźwigiem ewakuacyjnym R (przystanek +30,90) oraz MOE w przedsionku B.

**Dźwigi [E4]** (PN-EN 81-20, tabl. 6 – maks. pole kabiny):

| Dźwig | Udźwig | Kabina | Pole kabiny / maks. | Szyb |
|---|---:|---|---|---|
| A1, A2 | 1 600 kg | 1,5 × 2,1 | 3,15 / 3,56 m² ✔ | 2,25 × 2,55 |
| P1, P2 | 1 600 kg | 1,5 × 2,1 (drzwi na boku 2,1 m) | 3,15 / 3,56 m² ✔ | 2,15 × 2,65 |
| R | 1 000 kg | 1,1 × 2,1 (PN-EN 81-72/76) | 2,31 / 2,40 m² ✔ | 1,80 × 2,55 |

Kabina P1/P2 z v1.0 (1 275 kg, 1,4 × 2,4 = 3,36 m² > 2,95 m²) była niezgodna.

**Holy windowe [E5]** (wolna głębokość prostokąta o szerokości drzwi 1,10 m mierzona od lica trzonu; bieg schodów nie jest wliczany):

| Dźwig | Przystanek | Wolna głębokość przed drzwiami | Wymóg |
|---|---|---:|---|
| A1 / A2 | S | 3,75 m (do biegu schodów) / 8,35 m | M.13 3,6 m ✔ (zapas 0,15) |
| A1 / A2 | +30,90 | 3,75 m (do otworu nad biegiem) / 7,00 m | M.13 3,6 m ✔ (zapas 0,15) |
| P1/P2 | +30,90 | 3,60 m | M.13 3,6 m ✔ |
| P2 | – (v1.2b: bez przystanku na S; dostawy baru dźwigami A1/A2/R) | – | – |

Poprzednia wartość „5,95 m” była górnym limitem pętli pomiarowej (119 × 0,05) z biegiem schodów wliczonym do wolnej podłogi – poprawiono w `_s2_ewakuacja.py` [E5]. P1 nie zatrzymuje się na S. Publiczność nie może wysiąść w strefie radnych.

---

## 7. Dostępność (wyróżniki S-3)

* **Galeria** ma 3 miejsca dla wózków 0,9 × 1,4 m z miejscami dla opiekunów obok, w zatoce +0,00 na pn. końcu, z polami manewrowymi 1,5 × 1,5 m i przejściem ≥ 0,90 m bez stopni od drzwi z korytarza publicznego i od przedsionka A [G2]. Toaleta dostępna (5,5 m²) ma drzwi z korytarza publicznego na jego wsch. końcu, przy holu P1/P2. Dźwig P1/P2 ma kabinę 1,5 × 2,1 m.
* **Sala:** 4 stanowiska dla wózków (po jednym w każdym rzędzie) przy pochylniach ≤ 5 %. Prezydium i mównica są bez stopni, mównica regulowana 0,75–1,20 m.
* **WC K i M** mają kabiny dostępne 2,2 m szerokości (D14) z przewijakami w przedsionkach. Pokój matki z dzieckiem nie jest w toalecie.
* **Antresola radnych** jest dostępna dźwigami A1/A2 (drzwi pn. na +30,90). MOE w przedsionku A' (test [E6]).
* **Szatnia:** lada z częścią niską 0,75–0,80 m.

**Zamknięte przegrody na +30,90 [G6]:**
* hol dźwigów P1/P2 – 21,96 m² (dojście publiczności);
* korytarz publiczny EI 30 – 49,35 m² (droga ewakuacyjna i dojście do galerii);
* toaleta publiczności – 5,50 m², jedyne zamknięte pomieszczenie użytkowe;
* przedsionek A' – 7,50 m², element klatki.

Razem 84,31 m² = 28,8 % antresoli (w części publicznej 76,81 z 142,14 m² = 54 %). Wszystkie pomieszczenia zamknięte programu (rozdz. 1 pkt 4) leżą na poziomie głównym S. Zasada Wyj. 21 odp. 85 jest więc spełniona także przy wykładni ostrożnej. Antresola w rozumieniu WT § 3 pkt 19 to galeria i hol górny z barem i strefą multimedialną (208,70 m²), otwarte na salę i pustkę holu.

---

## 8. Uwagi weryfikatora – sposób rozwiązania

| # | Uwaga (skrót) | Rozwiązanie w S-3 | Dowód |
|---|---|---|---|
| **K1** | Pomieszczenia bez drzwi na komunikację | SWD.11b: dojście 1,6 m z kuluaru. WC K i M: oba z drzwiami do holu. PHS.05c na antresoli, na wsch. końcu korytarza publicznego (dojście do przedsionka B 8,30 m). SWD.07 i PP.06 zamienione (drzwi przy zach. końcu, dojścia ≤ 10 m). SWD.10a/b: oba z drzwiami do kuluaru. Kontrola: brak pomieszczeń bez drzwi; każdy otwór w całości w ścianie wspólnej (42/42). | [G3], [E2] |
| **K2** | Bilans się nie zamyka; hol to 5,8 m²; SWD.03 to korytarz; brak PD i porządkowego | Hol 156,6 m² wolnej podłogi + szatnia 12,5 + bar 32,0 (osobne poligony). SWD.03 to strefa 32,3 m² na 20 os., poza ciągiem komunikacyjnym i oddzielona od sali. PP.06 i IT.02 na S. Wszystkie pozycje w zakresach, +78 m² nad sumą minimów. Ściany 0,22 m (D1). | [G4], [G5] |
| **K3** | 44 stanowisk się nie mieści | 4 rzędy, 47 stanowisk (43 + 4 dla wózków). Przejścia 5,0 % / ≤ 4,61 %. Media i goście mają miejsca. | [S1] |
| **I1** | Galeria nad prezydium – brak widoku; radni pod światło | Galeria zach. nad WC i łącznikiem, 2 strome rzędy i zatoka dla wózków: C ≥ 158 mm do całego prezydium i mówcy, kąt mediana 64°. Prezydium na tle pełnej ściany, radni z oknami za plecami (min. 51°). Galeria w łuku sprawdzona i odrzucona. | [S3], [S5], [S6] |
| **I4** | Otwarte schody w kuluarze; antresola otwarta na kuluar | Schody usunięte z kuluaru. Kuluar EI 30, korytarz publiczny nad nim zamknięty. Schody reprezentacyjne tylko w pustce holu (osobna strefa dymowa; cały bieg pod otwartą przestrzenią). Klatki A i B przedłużone do +30,90 (przedsionki A, A', B). | [E2], [E3], [E6] |
| I3 (część S) | WC na S za małe | 41,4 m² (K 17,6 + M 18,4 + publiczna 5,5), kabiny dostępne w K i M | [G4] |
| I5 (część S) | Kabiny i holy windowe; trzony za małe | 1 600 kg / 1,5 × 2,1 m (A1, A2, P1, P2). Holy A1/A2 ≥ 3,75 m (od lica trzonu, bez biegu schodów), P1/P2 3,60 m. Dźwig T w segmencie. v1.2: klatka A 3,40 × 5,80 m (trzon A wydłużony o 0,60 m na pd.), klatka B 3,40 × 6,64 m – 2 lub 3 biegi na kondygnacji, stopnie ≤ 17,5 × 28 cm | [E4], [E5], `_v12_trzony.py` |
| D1 | Ściany za cienkie | Ściany sali 0,30 m (pd. i zach., pod kratownice), przegrody 0,20 m; średnio 0,222 m | [G5] |
| D6 | Jedna mównica 0,75–0,80 | Mównica regulowana 0,75–1,20 m, pod blatem 0,90 × 0,67 × 0,60 m | [S7] |
| D7 | Wentylacja wyporowa bez plenum | Nawiew z cokołów pulpitów, kanały w podestach rzędów (+0,09…+0,27) i w warstwie posadzki 0,15 m. Płyty nie obniżamy. Do weryfikacji branżowej. | – |
| D8 | Szachty wyrzutni/czerpni | Szachty w komórce trzonu B po dźwigu T (2,15 × 3,20 m) | JSON `trzony_uklad` |
| D9 | MOE 0,9 × 1,4 | Pola 1,5 × 1,5 m w przedsionkach A, A' (2,50 × 3,00 m), B (drzwi w u 27,80) – poza torem 1,2 m i polem otwierania skrzydeł, test geometryczny na S i +30,90 | [E6] |
| D13 | SWD.15 < 6 m²; SWD.10a tylko przez salę | SWD.15 6,0 m² pod spocznikiem i górnym biegiem schodów; SWD.10a z drzwiami do kuluaru | [G3], [G4] |
| D14 | WC 2,0 m szerokości | WC K i M po 2,20 m (kabina dostępna z transferem obustronnym) | [G4] |

---

## 9. Pozycje nierozwiązane, ryzyka i uwagi do scalenia

1. **Układ trzonu A (I5) – rozwiązany w v1.2** (`_v12_trzony.py` [T2]): obrys 7,20 × 9,00 m (wydłużenie o 0,60 m na pd.);
   * pas pn.: A1, A2, R (drzwi A1/A2 na pn. na wszystkich kondygnacjach – zmiana względem `budynek.json`, gdzie dźwigi otwierają się na pd.; na kond. 1–6 przed nimi korytarz pn. 2,15 m);
   * pas pd.: klatka A 3,40 × 5,80 m + przedsionek 3,05 × 5,80 m z drzwiami pd. (kuluar) i wsch. (łącznik; na +30,90 galeria).

   Klatka dwubiegowa na kondygnacjach 3,75 m (22 st. 17,05 × 28 cm) wymaga 5,80 m; na −1/P i P/1 – 3 biegi (spocznik parteru na końcu pn.). Na parterze hol A1/A2 trafia do łącznika pn. (u 0,5–13,35 × v 21–29,2).
2. **Trzon B (I5):** dźwig T w segmencie, drzwi wsch. P1/P2 na P i +30,90; v1.2 – klatka B 3,40 × 6,64 m (2 biegi także na P, 2 × 14 st.), przedsionek B 3,40 × 2,06 m.
3. **Wielkość antresoli: 293,0 m² (25,6 % rzutu)**, z czego 71,3 m² to hol P1/P2 i korytarz publiczny.
   * Skutki (v1.2, `_v12_koszt.py`): PC nadziemna 14 387,8 m² (+223,3 wobec v1.0; +113,3 ponad rezerwę v1.1); koszt +0,47 mln (antresola) +0,11 (klatka A do +30,90, balustrady z krawędziami podestu galerii) +0,12 (trzony I5); po dźwigniach niewidocznych na planszach 148,99 mln, zapas 1,01 mln przy rezerwie 5 %.
   * Zamknięte przegrodami są dojścia publiczności (hol P1/P2, korytarz), toaleta i przedsionek A' – 84,31 m² = 28,8 % antresoli [G6]. Wykładnię WT § 3 pkt 19 warto przedstawić jako uzgodnienie z rzeczoznawcą ppoż.
4. **Płyta sali ma 232,0 m²** (z galerią 297,3 m²), czyli 3,3 m² na osobę płyty. Jest wystarczająca, ale ciasna. Trzecie przejście czy dodatkowe miejsca dla mediów nie są możliwe bez utraty stanowisk.
5. **Linie wzroku radnych do siedzącego prezydium:** 31 ze 156 linii ma C 39–60 mm (linie skośne przy sąsiednim stanowisku). Akceptowalne przy ekranach na pulpitach; lepszy wynik dałoby przewyższenie 0,10 m przy rozstawie 2,0 m, ale kosztem ≈ 3–5 stanowisk.
6. **Szerokości wg M.13 (1,8 m) – v1.2b:** kuluar przy trzonie A 1,80 m (ściana 0,15 m); łącznik wsch. 1,40 m z polem mijania 1,80 × 2,00 m (przewężenia ≤ 5 m – M.13 korytarze pkt 2.2–3); dojście do SWD.11b 1,60 × 2,60 m – przewężenie miejscowe ≤ 5 m; przystanek służbowy P2 usunięty. Na S nie ma odstępstw od M.13 (pozostałe odstępstwa budynku: `koncepcja_wybrana.md` rozdz. 17).
7. **Szczegóły branżowe:**
   * strefa multimedialna otwarta – głośniki kierunkowe, ustroje na suficie antresoli;
   * plenum nawiewu (D7);
   * podciąg stalowy 10 m nad otworem galerii w ścianie zach. sali (kratownice 17,5 m oparte na nim i na łuku);
   * kontrola dostępu na drzwiach przedsionków A i A' (strefa publiczna i radnych), zwalniana przez SSP.
8. **I7** (wykładnia „Kancelaria Sejmiku”) pozostaje otwarte. S-3 ma 78 m² zapasu nad minimum, co nie wystarcza na ≈ 250 m² gabinetów KS i sal 20 os. Uzasadnienie pozostaje w opisie (bez zmian w tym opracowaniu).
9. **Scalenie JSON (wykonane w v1.2 – `_v12_scalenie.py`):**
   * zastąpić `kondygnacja_sejmiku` treścią `kondygnacja_S2.json` (klucze `posadzka`, `antresola`, `sala`, `pomieszczenia` – z `C-A`, `C-B` – oraz nowe: `antresola_pomieszczenia`, `pustka_holu`, `trzony_uklad`, `drzwi`, `bilans`);
   * dotychczasowy klucz `antresola_strefy` zastępuje `antresola_pomieszczenia`;
   * w rozdz. 7 MD przenieść tabele z rozdz. 3 i 5;
   * kadr W7 – z holu dźwigów A1/A2 na pn. ku pustce, schodom i oknom na Ostrów Tumski;
   * kadr W8 przeliczyć dla rzędów R 4,5–9,9 m.
10. **Hol SWD.02 jako komunikacja ogólna (wykładnia dla rzeczoznawcy ppoż.):** na niej opiera się drugi kierunek ewakuacji z SWD.12b, szatni, magazynu i WC M oraz dojście od stopy schodów reprezentacyjnych ([E2]). Hol jest oddzielony od kuluaru drzwiami EI 30 S i stanowi strefę dymową 2 z samoczynnym oddymianiem; ma otwarte strefy szatni (S) oraz baru i multimediów (antresola). Bez tej wykładni SWD.12b ma tylko dojście jednokierunkowe 17,05 m (> 10 m) i wymagałby drugiego wyjścia z klubu.
