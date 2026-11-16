# Zdjęcia F.17.A i F.17.B – metadane, geometria kamery, położenie działki

**Konkurs SARP nr 1089 – UMWD Wrocław** · stan: 2026-11-16

**Pliki:**
- `00_materialy/_rozpak/3.Zalaczniki_Formalne_F.01-F.17_PDF/F.17.A_widok z lotu ptaka od strony wschodniej_wer.01.jpg`;
- `…/F.17.B_widok z lotu ptaka od strony zachodniej_wer.01.jpg`.

**Narzędzia:** metadane odczytano przez `python3 -I` z PIL (EXIF, GPS IFD, XMP). Dopasowanie do oryginałów M.10 wykonano w OpenCV (SIFT i RANSAC). Współrzędne przeliczono w pyproj (WGS-84 → PL-2000 strefa 6, EPSG:2177).

**Podglądy z naniesionym obrysem działki:**
- `docs/10_regulamin/img/F17A_annot.jpg`, `img/F17B_annot.jpg`: skala 2000 px szer.; czerwona linia to widoczna część terenu, pomarańczowa to część zasłonięta, krzyżyk magenta to oś optyczna;
- robocze kadry w `/tmp/claude-0/-home-user-aihouse/3267b8b5-f709-5d54-b008-7221ccbc0b4f/scratchpad/wyj_form/`.

## 0. Znaczenie formalne

- **Etap II, wizualizacja nr 1:** „widok z lotu ptaka od strony wschodniej […] wykonana na zdjęciu, stanowiącym Załącznik nr F.17.A”.
- **Etap II, wizualizacja nr 2:** to samo dla strony zachodniej, na F.17.B (Reg. R.VII ust.2 pkt2 lit.g, s.43).
- **Etap I:** perspektywy nr 1 i 2 miały być „zbieżn[e] z perspektywą widoczną na zdjęciu […] (lub wklejon[e] na to zdjęcie)” (Reg. R.V ust.2 pkt2 lit.e, s.33). Uwaga: w Etapie I perspektywę nr 2 omyłkowo opisano jako „od strony wschodniej”.
- **Wyj. 9 odp. 61:** teren poza „Granicą opracowania studialnego” (M.04) ma na wizualizacjach przedstawiać **stan obecny, zgodny z F.17.A/B**.
- **Wniosek:** kontekstu poza granicą studialną nie wolno retuszować, np. usuwać estakad na pl. Społecznym czy pojazdów na moście. Zmiany dotyczą tylko terenu w granicy.

## 1. Parametry plików

| Parametr | F.17.A (od wschodu) | F.17.B (od zachodu) |
|---|---|---|
| Rozmiar pliku | 26 500 236 B (≈ 26,5 MB) | 25 760 145 B (≈ 25,8 MB) |
| Format / tryb | JPEG, RGB 8 bit | JPEG, RGB 8 bit |
| **Rozdzielczość** | **8470 × 4475 px** (37,9 Mpx; proporcja 1,893) | **7962 × 4505 px** (35,9 Mpx; 1,767) |
| DPI w pliku | 300 × 300 | 300 × 300 |
| Wymiar druku przy 300 dpi | 71,7 × 37,9 cm | 67,4 × 38,1 cm |
| dpi przy szerokości 100 cm | 215 | 202 |
| Profil ICC | sRGB IEC61966-2.1 (3144 B) | sRGB IEC61966-2.1 |
| Obróbka (XMP History) | Lightroom 8.5.1 (zapis 2025-10-29 17:38), następnie Photoshop 27.0 (2025-11-03 08:25) | Lightroom 8.5.1 (2025-10-29 17:38), następnie Photoshop 27.0 (2025-11-03 08:37) |
| Nazwa pliku źródłowego (crs:RawFileName) | DJI_20251029113800_0009_D.JPG | DJI_20251029115736_0025_D.JPG |
| Korekty Lightroom (crs) | Exposure −0,15; Contrast +6; Highlights −40; Shadows +52; Whites +38; Blacks −23; **Dehaze +24**; Vibrance +7; Saturation +17; brak kadrowania, korekcji obiektywu i perspektywy | Exposure −0,10; Contrast +6; Highlights −20; Shadows +54; Whites +5; Blacks −19; **Dehaze +29**; Vibrance +9; Saturation +24; brak kadrowania i korekcji |

*Wniosek dla grafiki:* zdjęcia są mocno „podbite” (dehaze, cienie +50, nasycenie). Rendery wklejane w F.17 trzeba dopasować do tego look'u: kontrast lokalny, nasycenie i jasne cienie. Inaczej budynek będzie wyglądał na „wklejony”.

*Wniosek dla planszy:* przy kadrze na pełną szerokość planszy 100 cm rozdzielczość wynosi ok. 200–215 dpi. To wystarczy dla wydruku wielkoformatowego, ale nie spełnia literalnie 300 dpi dla całej planszy. Plansza jako plik (11811×8268 px) wymaga przeskalowania zdjęcia o ×1,39–1,48 albo kadru mniejszego niż szerokość planszy.

## 2. EXIF / GPS / XMP (DJI)

| Pole | F.17.A | F.17.B |
|---|---|---|
| Make / Model | DJI / FC8282 | DJI / FC8282 |
| Produkt (XMP drone-dji:ProductName) | **Air3** (DJI Air 3) | Air3 |
| Obiektyw | „24.0 mm f/1.7”; FocalLength **6,72 mm**; FocalLengthIn35mmFilm **24**; f/1.7 | j.w. |
| Ekspozycja | 1/3200 s; ISO 160; f/1.7; program normalny; WB auto (XMP WhiteBalanceCCT 5505 K) | 1/3000 s; ISO 100; f/1.7; WB 5542 K |
| Data i czas wykonania | **2025-10-29 11:38:00 (+01:00, CET)** | **2025-10-29 11:57:36 (+01:00)** |
| GPS (EXIF, DMS) | 51°06,49902′ N; 17°03,3282′ E | 51°06,4686′ N; 17°02,9853′ E |
| GPS (XMP, dziesiętnie) | **51,108316679 N; 17,055469768 E** | **51,107810447 N; 17,049754529 E** |
| PL-2000 (EPSG:2177), wyliczone | x = 5 664 124,1; y = 6 433 856,4 | x = 5 664 072,9; y = 6 433 455,4 |
| AbsoluteAltitude (AltitudeType GpsFusionAlt) | 219,739 m | 182,639 m |
| **RelativeAltitude** (nad punktem startu) | **87,8 m** | **50,7 m** |
| GimbalYaw / Pitch / Roll | **−89,2°** (azymut 270,8°) / **−12,9°** / 0,0° | **+39,2°** / **−11,4°** / 0,0° |
| FlightYaw / Pitch / Roll | **−74,0°** (azymut 286,0°) / −4,5° / −5,1° | **+54,4°** / +6,7° / +1,3° |
| IFD0 ImageWidth × ImageLength | 8000 × 5632 (wymiar pliku przed kadrowaniem w Photoshopie) | 8000 × 5632 |
| ExifImageWidth × Height | 8470 × 4475 | 7962 × 4505 |
| DigitalZoomRatio | 1,0 | 1,0 |

Specyfikacja kamery szerokokątnej DJI Air 3 (https://www.dji.com/air-3/specs, dostęp 2026-11-16):
- matryca 1/1,3″ CMOS, 48 Mpx;
- FOV 82°;
- ekwiwalent 24 mm, f/1.7;
- maks. rozmiar zdjęcia 8064×6048.

### 2.1. Wielkości pochodne

| Wielkość | F.17.A | F.17.B | Uwagi |
|---|---|---|---|
| Wysokość punktu startu (Absolute − Relative) | 131,9 m | 131,9 m | **Identyczna:** oba zdjęcia wykonano z jednego startu. |
| Teren działki (pikiety M.02, 800 pkt) | 117,9–121,7 m n.p.m. | j.w. | Plik `M.02/model terenu/mazowiecka_pikiety do nmt.txt`; przyjęto średnio ok. 119,5 m. |
| **Wysokość kamery nad terenem działki** | **≈ 88–100 m** | **≈ 51–63 m** | Dolna wartość zakłada start z poziomu terenu, górna poprawną wysokość GPS. Absolutna wysokość DJI (GPS) bywa obarczona błędem kilkunastu metrów. Wartość trzeba rozstrzygnąć przy dopasowaniu kamery. |
| Odległość pozioma do środka terenu (x 5 664 150; y 6 433 570) | ≈ 288 m | ≈ 138 m | |
| Azymut (geogr.) z kamery na środek terenu | ≈ 274° (prawie dokładnie na zachód) | ≈ 55° (NE) | Zbieżność południków PL-2000 w tym miejscu γ ≈ −0,74°. |
| Słońce w chwili zdjęcia (obliczenie własne, algorytm typu NOAA) | azymut ≈ 180,7°, wysokość ≈ 25,3° | azymut ≈ 185,9°, wysokość ≈ 25,1° | Do ustawienia słońca w renderach: jesień, ok. godz. 11:40–12:00 CET, niebo z cumulusami. |

## 3. Relacja F.17 ↔ oryginały M.10 (ustalone pomiarem)

W `M.10. ZDJĘCIA OTOCZENIA` są pliki o tych samych nazwach co źródła F.17: `DJI_20251029113800_0009_D.jpg` i `DJI_20251029115736_0025_D.jpg`. Mają po 4000 × 2816 px i okrojone metadane: zostały tylko daty (DateTimeOriginal/Digitized, SubsecTime) i Orientation, brak GPS i danych DJI w XMP. <!-- poprawione przez weryfikatora: było „usunięte metadane”; sprawdzono PIL --> Weryfikator potwierdził relację niezależnie: F.17 pomniejszone ÷2,5 i porównane z oknem M.10 (264,552) / (228,582) daje korelację 0,995 (A) i 0,990 (B) przy przesunięciu 0 px. <!-- poprawione przez weryfikatora: kontrola niezależna --> Dopasowanie SIFT i RANSAC (podobieństwo, 3377 i 3510 punktów zgodnych) dało:

| | F.17.A | F.17.B |
|---|---|---|
| Transformacja M.10 → F.17 | skala **2,5000**, obrót 0,00°, przesunięcie (−659,9; −1379,9) px | skala **2,5002**, obrót 0,00°, przesunięcie (−569,9; −1455,2) px |
| Błąd RMS | 0,41 px | 0,32 px |
| Wniosek | F.17.A to **czysty kadr** obrazu 8000×5632 powiększonego ×1,25, czyli ramki 10000×7040 px. Brak warpu i perspektywy. | j.w. |
| Okno F.17 w ramce pełnej 10000×7040 | x 660–9130, y 1380–5855 (ucięto: lewo 660, prawo 870, góra 1380, dół 1185) | x 570–8532, y 1455–5960 (lewo 570, prawo 1468, góra 1455, dół 1080) |
| Okno F.17 w pikselach M.10 (÷2,5) | x 264–3652, y 552–2342 | x 228–3413, y 582–2384 |
| **Środek ramki pełnej, czyli przybliżona oś optyczna, we współrzędnych F.17** | **(4340; 2140)**; środek obrazu to (4235; 2237,5) | **(4430; 2065)**; środek obrazu to (3981; 2252,5) |

Korzyść: M.10 pokazuje szerszy kontekst poza kadrem F.17. Można z niego doczytać obiekty przy krawędziach, np. do maskowania i dopasowania.

## 4. Pole widzenia i orientacja – UWAGA dla photomatchingu

**Ustalenie: efektywne pole widzenia F.17 jest znacznie szersze niż pojedynczej klatki 24 mm.** Wskazują na to cztery niezależne obserwacje:

1. **Format 8000×5632** (proporcja 1,42) nie jest natywnym formatem Air 3 (8064×6048, 4:3). Fora użytkowników DJI podają, że panoramy szerokokątne łączone w dronie mają szerokość 8000 px, np. 8000×5760 (Mavic 3) i 8000×5394 (Mavic 2 Pro):
   - https://mavicpilots.com/threads/mavic-3-9-frame-wide-angle-pano-stitching-issues-anyone-else.122779/post-1389055
   - https://mavicpilots.com/threads/mavic-2-pro-randomly-produces-8000-x-6000-jpg-images.107302/page-2
   (dostęp 2026-11-16; źródła nieoficjalne, niska ranga).
2. **Horyzont:**
   - F.17.A: widoczny horyzont na y ≈ 1265 (x=300), 1290 (x=2500), 1310 (x=4300), 1325 (x=6500), 1310 (x=8100);
   - F.17.B: horyzont na y ≈ 1240–1250 na całej szerokości;
   - przy pitch z EXIF (−12,9° i −11,4°, z poprawką o obniżenie horyzontu 0,2–0,3°) i osi optycznej z §3 wychodzi ogniskowa **f ≈ 3530 px (A) i ≈ 3980 px (B)** w pikselach F.17;
   - dla pojedynczej klatki 24 mm byłoby to ≈ 6900–7200 px.
3. **Kontrola kątowa (A):**
   - bliźniacze wieże katedry na Ostrowie Tumskim są na x ≈ 6430–6490;
   - współrzędne katedry przyjęto z pamięci: ok. 51,1142 N; 17,0464 E (*do weryfikacji*);
   - teren działki jest na x ≈ 3500;
   - różnica azymutów z pozycji kamery ≈ 41° odpowiada f ≈ 3800 px.
4. **Odchylenie yaw.**
   - GimbalYaw i FlightYaw różnią się w obu zdjęciach o tę samą wartość, **15,2°**.
   - Treść obrazu odpowiada kierunkowi osi ≈ **FlightYaw**: A ≈ 286°, B ≈ 54,4°.
   - Dla modelu f = 3750 px, kierunku 286°, pitch −12,9° i pozycji GPS rzut krawędzi terenu w F.17.A wypada w odległości ok. 100–250 px od położenia widocznego na zdjęciu (§5). Wynik jest spójny.
   - *Hipoteza:* EXIF opisuje jedną klatkę składową panoramy, prawdopodobnie skrajną kolumnę siatki 3×3, a nie wirtualną kamerę całego obrazu.

**Kontrola weryfikatora** <!-- poprawione przez weryfikatora: nowa uwaga -->:
- Azymut z kamery A (51,108317 N; 17,055470 E) na katedrę (51,1142 N; 17,0464 E) wynosi ≈ 315,9°, a na środek terenu ≈ 274,5°. Różnica to ≈ 41,4°. Przy osi w x = 4340 i f = 3800 px rzut daje 29,2° + 12,5° = 41,6°. Dla pojedynczej klatki (f ≈ 6940 px) byłoby to tylko ≈ 24°. Obs. 3 jest więc spójna.
- Kierunek osi wyliczony z położenia terenu i katedry w kadrze wynosi ≈ 285–286° (A) i ≈ 53° (B). To zgadza się z FlightYaw (286,0° / 54,4°), a nie z GimbalYaw (270,8° / 39,2°).
- **Zastrzeżenie:** obs. 2 (horyzont) używa pitch z EXIF. Jeśli zgodnie z hipotezą EXIF opisuje jedną klatkę składową, pitch nie musi dotyczyć osi wirtualnej kamery. Obs. 2 nie jest więc w pełni niezależna od hipotezy, a f z horyzontu (3530/3980 px) trzeba traktować jako orientacyjne. Najmocniejszą przesłanką pozostaje obs. 3.

**Wniosek, wysokie prawdopodobieństwo:** podkłady F.17 to panoramy szerokokątne zszyte w dronie. Dlatego:
- **nie wolno ustawiać kamery wizualizacji na 24 mm z EXIF**;
- kamerę trzeba rozwiązać z punktów kontrolnych (fSpy, Blender camera solver albo ręcznie w Blenderze) i sprawdzić odwzorowanie. Panorama może nie być ściśle prostoliniowa: horyzont w F.17.A ugina się o ok. 20 px, choć część tej różnicy może wynikać z rzeźby horyzontu;
- trzeba przewidzieć korektę zniekształceń albo dopasowanie lokalne (warp) przy wklejaniu.

### 4.1. Proponowane parametry startowe kamery (do iteracji)

| Parametr | F.17.A | F.17.B |
|---|---|---|
| Rozdzielczość renderu | 8470 × 4475 | 7962 × 4505 |
| f [px] | ≈ 3750 (± 300) | ≈ 3750 (± 300) |
| Sensor 36 mm (dopasowanie poziome), ogniskowa | **≈ 15,9 mm** | **≈ 17,0 mm** |
| HFOV / VFOV kadru | ≈ 97° / 62° | ≈ 93° / 62° |
| Przesunięcie obiektywu (oś w pkt z §3) | shift_x ≈ −0,012; shift_y ≈ −0,012 (oś 105 px w prawo i 97 px w górę od środka) | shift_x ≈ −0,056; shift_y ≈ −0,024 (oś 449 px w prawo i 187 px w górę) |
| Pozycja (PL-2000) | x 5 664 124,1; y 6 433 856,4; z ≈ 207–220 m n.p.m. (119,5 + 88…100) | x 5 664 072,9; y 6 433 455,4; z ≈ 170–183 m n.p.m. (119,5 + 51…63) |
| Kierunek osi (geogr.) / pitch / roll | ≈ 286° / −12,9° / ≈ 0,3–0,5° (lekki przechył horyzontu) | ≈ 54° / −11,4° / ≈ 0° |

Znak shift zależy od konwencji programu. W Blenderze dodatnie shift_x przesuwa kadr w prawo, więc oś optyczna wypada na lewo od środka. Tu oś ma być na prawo, stąd wartość ujemna. **Do weryfikacji.**

**Punkty kontrolne do rozwiązania kamery** (współrzędne z M.02 DWG/DGN i z pikiet):
- narożniki i gzymsy WS 5, Mazowiecka 19 i Mazowiecka 17;
- przyczółek i pylony Mostu Grunwaldzkiego;
- rotunda (kiosk) przy przyczółku;
- krawędź nabrzeża;
- latarnie;
- dla F.17.A dodatkowo narożniki Urzędu Wojewódzkiego (spoza mapy: ortofoto lub BDOT).

Wymagane minimum to 6–8 punktów rozłożonych na całym kadrze.

## 5. Co widać na zdjęciach i gdzie leży działka

Współrzędne px odnoszą się do **oryginalnej rozdzielczości** pliku: x od lewej, y od góry. Identyfikacja obiektów to *wniosek* z porównania z M.04, ortofotomapą M.11.A (`M.11.A. KONTEKST ortofotomapa 01 A.png`, teren zaznaczony na pomarańczowo) i notatką z wizji. Obrys jest przybliżony, z dokładnością ±50–100 px.

### 5.1. F.17.A – widok z nad prawego (wschodniego) brzegu Odry w kierunku WNW (≈ 286°)

**Kompozycja:**
- pierwszy plan: Odra (dolna lewa połowa) z piaszczystą łachą i zadrzewionym pasem brzegu po lewej; zabudowa i park prawego brzegu (dół i prawa strona);
- plan środkowy: lewy brzeg z terenem inwestycji, Most Grunwaldzki po prawej;
- tło: panorama centrum z Ostrowem Tumskim po prawej; horyzont na y ≈ 1270–1325;
- niebo zajmuje ok. 29% wysokości.

| Obiekt | px (x0–x1, y0–y1) | Uwagi |
|---|---|---|
| **Teren inwestycji – część widoczna** (trawnik z drzewami między szczytem WS 5 a łukiem ul. Wybrzeże Słowackiego) | wielobok **(3264,2400) – (4030,2420) – (4045,2585) – (3264,2705)** | Ok. 780 × 300 px. Dolna krawędź to ulica nadbrzeżna (Wybrzeże Słowackiego, odcinek wzdłuż rzeki). Górna krawędź to ul. Mazowiecka przechodząca w łuk Wybrzeża Słowackiego. Teren jest **mały w kadrze, ok. 9% szerokości**. **Uwaga weryfikatora:** na kadrze trawnik kończy się po prawej ok. x ≈ 3890. Pas x ≈ 3890–4010 to jezdnia łuku Wybrzeża Słowackiego z autobusami. Prawe wierzchołki (4030; 2420) i (4045; 2585) leżą więc prawdopodobnie poza Obszarem inwestycji, ok. 140 px poza deklarowaną tolerancją. Przed photomatchingiem trzeba to sprawdzić z M.04. <!-- poprawione przez weryfikatora --> |
| Teren – część zasłonięta przez WS 5 (podwórze, ogródki) | ok. x 2900–3264, y 2330–2400 | Niewidoczny. Projektowana bryła wyższa niż WS 5 będzie częściowo widoczna nad dachem kamienicy. |
| Wybrzeże Słowackiego 5 (kamienica przy rzece, szczyt północny zwrócony do terenu) | 2904–3253, 2331–2725 | Ściana szczytowa na x ≈ 3253. Kalibrator skali: elewacja ma ok. 290–330 px wysokości. |
| Mazowiecka 19 (szara kamienica, kolorowy mural na szczycie zwróconym do terenu; biały budynek z czerwonym dachem tuż na lewo, x ≈ 2400–2610, to już Mazowiecka 17) <!-- poprawione przez weryfikatora: było „biała”; na kadrze kamienica jest szara, spójnie z opisem F.17.B --> | 2600–2915, 2140–2325 | Okna w szczycie przewidziano do likwidacji (W-004). |
| Mazowiecka 17 (UMWD, czerwony dach) i dalsza pierzeja | ok. 1800–2625, 2137–2381 | |
| Duży biały budynek przy rzece po lewej | ok. 100–1700, 2100–2800 | Prawdopodobnie zabudowa Wybrzeża Słowackiego dalej na południe (*niezweryfikowane*). |
| Most Grunwaldzki – pylon zachodni (przy terenie) | 4537–4800, 2166–2456 | |
| Most Grunwaldzki – pylon wschodni | 6247–6617, 2541–3070 | Pomost x ≈ 4550–6950. |
| Barka-restauracja przy nabrzeżu | 3769–4462, 2625–2869 | Przed terenem, poza granicą. |
| Rotunda (kiosk) przy przyczółku | 4158–4243, 2297–2376 | Dobry punkt kontrolny. |
| Dolnośląski Urząd Wojewódzki | 4394–5347, 1773–2250 | Monumentalna bryła na północ od terenu. |
| Estakady pl. Społecznego (do rozbiórki – zostawić, W-043) | 2438–3675, 1903–2062 | |
| Gmach Poczty Głównej (ceglany wieżowiec) | 3159–3300, 1500–1706 | |
| Katedra (Ostrów Tumski), wieże | 6420–6500, 1260–1420 | |
| Komin elektrociepłowni | 5900–5960, 1130–1400 | |
| Wysokościowiec w budowie z żurawiem | 4235–4395, 1170–1400 | Stan na 29.10.2025. |

**Obserwacje dla wizualizacji nr 1 (*wniosek*):**
- Teren leży w środkowej części kadru, lekko na lewo od osi.
- Dominanta 35–45 m będzie się rysować na tle Urzędu Wojewódzkiego i zieleni pl. Społecznego, poniżej linii horyzontu. Przy kamerze ok. 88–100 m nad terenem, f ≈ 3750 px i dominancie 45 m w środku terenu wierzch dominanty wypadnie około y ≈ 1850–2000 (obliczenie przybliżone).
- Budynek powinien „wyjść” sylwetą ponad WS 5 i domknąć przyczółek mostu.
- Światło pada z południa, więc od strony kamery (wschód) elewacja wschodnia będzie w półcieniu bocznym. Słońce jest nisko (25°), cienie długie i skierowane na północ.

### 5.2. F.17.B – widok z nad zieleńca na zachód od ul. Mazowieckiej w kierunku NE (≈ 54°)

**Kompozycja:**
- pierwszy plan: zieleniec i ścieżki po zachodniej stronie Mazowieckiej (poza terenem inwestycji, w granicy studialnej);
- lewa strona: torowisko i jezdnie pl. Społecznego z tramwajami;
- prawa strona: pierzeja Mazowieckiej 17–19;
- plan środkowy: teren inwestycji i Most Grunwaldzki;
- tło: prawy brzeg z Manhattanem przy pl. Grunwaldzkim; horyzont na y ≈ 1240–1250;
- niebo zajmuje ok. 28% wysokości.

| Obiekt | px | Uwagi |
|---|---|---|
| **Teren inwestycji – część widoczna** (trawnik z drzewami między ul. Mazowiecką a ulicą nadbrzeżną) | wielobok **(3580,2380) – (4700,2200) – (5230,2250) – (5210,3020)** | Klin rozszerzający się ku prawej. Lewa i dolna krawędź to chodnik ul. Mazowieckiej (z parkującymi autami), górna to łuk Wybrzeża Słowackiego z autobusami, prawa to szczyt Mazowieckiej 19. Teren zajmuje ok. 20% szerokości kadru. |
| Teren – część zasłonięta (podwórze za Mazowiecką 19, ogródki, drzewa) | ok. 4800–5300, 2140–2700 | Częściowo widoczne korony drzew przy szczycie Maz. 19. |
| Mazowiecka 19 (szara kamienica, szczyt północny zwrócony do terenu) | 5210–5920, 2180–3300 | Narożnik z terenem na (5210, 3020). |
| Mazowiecka 17 – budynek UMWD (czerwony dach, napis „URZĄD MARSZAŁKOWSKI WOJEWÓDZTWA DOLNOŚLĄSKIEGO”, „DOLNY ŚLĄSK”) | 5860–7962, 2280–4505 | Pierwszy plan po prawej, mocno w perspektywie. Ważny odnośnik skali i stylu. |
| WS 5 i dalsze kamienice przy rzece (widok od tyłu) | 5275–6915, 1840–2190 | |
| ul. Mazowiecka (oś jezdni) | od (3580,2390) do ok. (7000,4300) | Linia zbiegu. Pomocna przy rozwiązaniu kamery. |
| Most Grunwaldzki | 2786–4230, 1543–2189 | Pylon zachodni ok. x 2985–3580. |
| Dolnośląski Urząd Wojewódzki | 0–1940, 1767–2588 | Lewa krawędź. |
| Wieżowce „Manhattanu” przy pl. Grunwaldzkim | 3608–4478, 1170–1543 | Zamykają oś widokową wskazaną na wizji (pkt 6) od drugiej strony. |
| Grupa ok. 20 osób na chodniku przy narożniku Maz. 19 | ok. 4780–5180, 2900–3120 | Leży w granicy terenu i zostanie zasłonięta przez projekt albo ją usuniemy. |

**Obserwacje dla wizualizacji nr 2 (*wniosek*):**
- Kamera jest blisko (≈ 140 m) i nisko (≈ 51–63 m), więc perspektywa będzie silna.
- Bryła o wysokości 25 m (skrzydła) i 35–45 m (dominanta) zasłoni część mostu i Manhattanu. Kamera jest ok. 51–63 m nad terenem, czyli wyżej niż dominanta (45 m). Wierzch dominanty wypadnie więc poniżej horyzontu, ok. y ≈ 1400–1700 (obliczenie przybliżone), i zasłoni część wieżowców Manhattanu albo pylon mostu, zależnie od położenia w strefie A.
- Ten kadr najlepiej pokazuje relację z pierzeją Mazowieckiej i styk z Maz. 19 (W-001, W-005), a także stronę wejściową od pl. Społecznego.
- Słońce z południa (azymut ok. 186°) oświetla elewacje zwrócone na południe i zachód, w tym fasadę od strony kamery. Bok od strony Mazowieckiej będzie dobrze oświetlony.

## 6. Ryzyka i zalecenia

1. **Anonimowość.** Pliki F.17 zawierają rozbudowane metadane: numer seryjny drona, identyfikatory dokumentów Adobe i historię obróbki. Wizualizacje oparte na F.17 trzeba przed wstawieniem do plansz i plików konkursowych pozbawić EXIF i XMP (Reg. R.VII ust.3 pkt4 lit.d, s.47).
2. **Nie korygować F.17 geometrycznie** (bez prostowania pionów i kadrowania przesuwającego kontekst). Wizualizacja ma być „wykonana na zdjęciu”, a kontekst poza granicą studialną ma odpowiadać zdjęciu (W-043).
3. **Rozdzielczość.** Do plansz 300 dpi przy pełnej szerokości 100 cm potrzebne jest powiększenie ×1,4–1,5. Lepiej renderować budynek w rozdzielczości 2× i składać na upscalowanym podkładzie albo dać kadr szerokości ok. 70 cm.
4. **Niepewność wysokości kamery** wynosi kilkanaście metrów (§2.1) i trzeba ją rozstrzygnąć punktami kontrolnymi. Bez tego błąd wysokości dominanty na wizualizacji może sięgnąć kilku metrów, a Sąd zweryfikuje relację z mostem i kamienicami.
5. **Odwzorowanie** może nie być idealnie prostoliniowe (panorama). Przy wklejaniu sprawdzić zbieżność pionów budynku z pionami kamienic na brzegach kadru.
