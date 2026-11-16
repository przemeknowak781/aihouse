# Metodyka wizualizacji konkursowych — UMWD Wrocław, Etap II

Data opracowania i dostępu do źródeł internetowych: **2026-11-16**. Język roboczy: polski.
Zakres: jak zrobić 8+ wizualizacji (w tym 2 fotomatchingi na F.17.A/F.17.B) najwyższej jakości, w naszych warunkach: Blender 5.2.4 LTS (bpy w `/home/user/aihouse/.venv-render`), Cycles CPU 4 rdzenie, 15 GB RAM, Python/PIL/OpenCV (systemowy `python3`, cv2 5.0).

**Zakaz Inwestora przestrzegany:** nie wyszukiwano i nie otwierano żadnych materiałów o wynikach ani pracach z tego konkursu. Wszystkie wnioski wynikają z Regulaminu, materiałów Organizatora, ogólnej wiedzy o wizualizacji/fotografii i badań naukowych.

**Legenda oznaczeń**
- **[F]** fakt ze źródła (źródło w nawiasie, lista na końcu),
- **[P]** pomiar/test własny wykonany w tej sesji (reprodukowalny, skrypty w scratchpadzie),
- **[S]** źródło wtórne (portal branżowy, blog praktyka), oznaczone jako takie,
- **[W]** wniosek / rekomendacja (interpretacja, nie fakt).

---

## 0. Najważniejsze decyzje (TL;DR dla orkiestratora)

1. **[F] Wymagane 8 wizualizacji o ściśle określonej treści** (Regulamin rozdz. VII ust. 2 pkt 2 lit. g); dowolna technika „pod warunkiem zachowania czytelności i jednoznaczności”. Wiz. 1 i 2 *na zdjęciach* F.17.A/F.17.B; poza granicą opracowania pokazujemy **stan obecny ze zdjęć** (Wyjaśnienia nr 09, odp. 61). **[W]** Nie dodawać więc np. planowanych hełmów Mostu Grunwaldzkiego (M.11.F) ani „upiększać” otoczenia poza granicą.
2. **[P] Zdjęcia F.17 to nie surowe klatki:** DJI FC8282 (f = 6,72 mm, ekw. 24 mm), zrobione 29.10.2025 o 11:38 i 11:57, ale **przetworzone w Photoshopie** (szerokość 8470/7962 px > natywne 8064 px matrycy 48 Mpx → upscaling/kadrowanie) i **z wyprostowanymi pionami** mimo pochylenia gimbala −12,9°/−11,4°. **[W]** EXIF-owa ogniskowa i kąt pochylenia NIE opisują geometrii obrazu → kamerę trzeba **wyliczyć z punktów kontrolnych** (model „poziomy aparat + przesunięcie obiektywu”), a metadane GPS/yaw traktować tylko jako wartości startowe.
3. **[P] Słońce na zdjęciach:** A (11:38 CET): azymut **180,7°**, wysokość **25,3°**; B (11:57 CET): **185,8° / 25,1°** (algorytm NOAA, zgodny z modułem `umwd/sun.py`). Panorama 360° (11:48) pokazuje tarczę słońca → służy do orientacji panoramy względem północy.
4. **[W] Rodzina obrazów:** wszystkie widoki zewnętrzne w **tej samej porze roku co zdjęcia — złota polska jesień (koniec października)**, jedna paleta i jeden grading. Pory dnia: późne przedpołudnie/popołudnie dla elewacji S/W, **błękitna godzina (ok. 16:50–17:15 CET pod koniec października) dla elewacji od Odry (północnej) i dla „latarni” sali Sejmiku**.
5. **[W] Kamera „ludzka”: wysokość 1,6 m, poziomo (perspektywa dwupunktowa), piony pionowe przez przesunięcie obiektywu (shift), ogniskowe 24–35 mm ekw. (HFOV 74–54°)**; 24 mm tylko w ciasnych ulicach (Mazowiecka). Wnętrza 20–24 mm (HFOV 84–74°), nigdy szerzej niż 18 mm.
6. **[P] Kalibracja światła (Blender 5.2, niebo Multiple Scattering, siła tła 1,0, słońce 25°):** słońce z dysku nieba ≡ lampa Sun o sile **≈117 W/m²**, kolor liniowy ≈ **(1,00; 0,80; 0,55)**; stosunek słońce:niebo na poziomej płaszczyźnie ≈ **4,5 : 1** (przy 10°: 1,7 : 1; przy 45°: 7 : 1); biała płaszczyzna ma radiancję ≈ 20 → **ekspozycja ≈ −4,3 EV**. Niebo Multiple Scattering daje sensowny zmierzch do ok. −6…−9° (Single Scattering gaśnie szybciej).
7. **[P] Krytyczne błędy do poprawienia w `umwd/src/umwd/render/blib.py`** (sekcja 11.6): `sky.sun_rotation` liczone jako `90° − az` jest **niezgodne** z konwencją Blendera 5.2 (test: `sun_rotation` = azymut kompasowy, zgodnie z ruchem wskazówek od +Y=N ku +X=E); domyślna lampa Sun 4 W/m² przy niebie o sile 1,0 daje stosunek słońce:niebo ≈ 0,15 : 1 (płaskie, prawie bez cieni); `max(el, 0.5)` blokuje niebo zmierzchowe.
8. **[P] Wydajność CPU (4 rdzenie):** prosta scena ≈ **50 s na megapiksel na 100 próbek** (z OIDN); path guiding +60% czasu. **[W]** Realne sceny 3–6× wolniej → hero 4700×3150 px: ok. 1–2 h; wnętrze 3150×2100 px z path guiding: ok. 1,5–3 h; komplet: ok. 12–20 h CPU.
9. **[W] Rozdzielczość:** obrazy na planszy wystarczy renderować z efektywną gęstością **180–200 ppi w skali wydruku** (ostrość wzroku 1′ → 175 ppi przy 0,5 m, 87 ppi przy 1 m), a planszę złożyć w 300 dpi (wymóg). Fotomatchingi renderować **w natywnej rozdzielczości zdjęcia, tylko w obszarze budynku** (render region).
10. **[W] Fotomatching w Blenderze:** model kontekstu (z mapy do celów projektowych + wysokości z inwentaryzacji M.07/M.08 i NMT) jako **Shadow Catcher** (cienie od nowego budynku + automatyczne zasłanianie), pass „Shadow Catcher” włączony, kompozycja `plate_lin × ShadowCatcher + CG` w przestrzeni liniowej, transformacja widoku **Standard** dla ujęć na zdjęciu (żeby nie „rozjechać” zdjęcia), dopasowanie kolorów po próbkach referencyjnych ze zdjęcia (np. nasłoneczniona biała elewacja Urzędu Wojewódzkiego ≈ sRGB 217/209/196).
11. **[W] Odbicia w szkle = prawdziwe otoczenie:** panoramy M.09 (30/40/45 m) jako środowisko widoczne tylko w promieniach odbitych (Light Path), a w sali Sejmiku jako **rzeczywisty widok z okien z właściwej wysokości** — lokalni sędziowie rozpoznają widok.
12. **[F]/[W] Dostępność widoczna na obrazach:** program (M.01) wymaga m.in. wejścia z poziomu terenu, dostępnych stanowisk radnych/prezydium/mównicy, miejsca tłumacza PJM, tyflomap w holu → każda z wiz. 3, 6, 7, 8 pokazuje przynajmniej jeden czytelny, nienachalny element dostępności (osoba na wózku wjeżdżająca samodzielnie, niski blat informacji, ścieżki prowadzące, stanowisko tłumacza PJM).
13. **[F]/[W] Wiarygodność > efekciarstwo:** badania jury pokazują, że obrazy są narzędziem retoryki i bywają „rozbrajane” przez sędziów (Merikoski 2020; Svensson 2012), a ostateczny wybór zapada na podstawie reakcji emocjonalnych (Kazemian & Rönn 2009, cyt. za Merikoski 2020). **[W]** Strategia: emocjonalne, piękne obrazy, ale **geometrycznie i oświetleniowo uczciwe**, zgodne co do piętra/rytmu z rysunkami — Sąd złożony głównie z architektów SARP i Architekta Miasta wychwyci rozbieżności.
14. **[W] Generatywne edycje obrazu** tylko do drobnych poprawek sztafażu (ludzie w tle, liście), nigdy do geometrii architektury; po każdej edycji usunąć metadane (w tym C2PA) — wymóg anonimowości (Regulamin rozdz. VII ust. 3 pkt 4 lit. d).
15. **[W] Zawsze startować skrypty od `bpy.ops.wm.read_factory_settings(use_empty=True)`** — [P] w module bpy domyślna scena zawiera kostkę w środku układu i kamera w (0,0,0) renderuje czerń (sprawdzone).

---

## 1. Wymagania Regulaminu dotyczące wizualizacji [F]

Źródło: `00_materialy/tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt`, rozdz. VII ust. 2 pkt 2 lit. g–j oraz ust. 3; wyjaśnienia nr 08, 09, 14, 20, 21.

| Nr | Treść wymagana | Uwagi [W] |
|---|---|---|
| 1 | widok z lotu ptaka od wschodu, relacje z obiektami istniejącymi, **wykonany na zdjęciu F.17.A** | kamera ~271 m na wschód od terenu, wysokość względna 87,8 m; budynek w środku kadru, mały (dalszy plan) |
| 2 | widok z lotu ptaka od zachodu, **na zdjęciu F.17.B** | kamera ~142 m na WSW, wysokość względna 50,7 m; teren w pierwszym/środkowym planie — **najważniejszy fotomatching** |
| 3 | główna strefa wejściowa z poziomu człowieka | wejście „widoczne w bryle”, z poziomu terenu (M.01) |
| 4 | powiązanie z budynkiem **Wybrzeże J. Słowackiego 5** | inwentaryzacja M.08 = wysokości gzymsów, rytm okien |
| 5 | powiązanie z budynkiem **Mazowiecka 19** | inwentaryzacja M.07 |
| 6 | hol główny | „reprezentacyjny”, orientacja w przestrzeni (M.01; wyjaśnienia nr 21, odp. 81–82) |
| 7 | hol sali Sejmiku | jw. |
| 8 | sala Sejmiku | ≤100 osób, układ amfiteatralny z podwyższanymi rzędami, strefy: radni (36), prezydium, zarząd (5), goście, media, obsługa, **tłumacze języka migowego**; stałe stanowiska z tabletami i mikrofonami; dostępność dla OzN; publiczność z oddzielnym wejściem, może być wizualnie oddzielona; transmisja obrad (M.01, s. 5–6) |

**Etap I (Opracowanie studialne, rozdz. V ust. 2 pkt 2 lit. e) [F]:** min. 3 perspektywy — nr 1 zbieżna z F.17.A „(lub wklejona na to zdjęcie)”, nr 2 zbieżna z F.17.B (w Regulaminie omyłkowo „od strony wschodniej”), **nr 3: dowolny widok z poziomu człowieka pokazujący sylwetę budynku w kontekście Mostu Grunwaldzkiego**; forma może być szkicowa. **[W]** Perspektywa nr 3 Etapu I = naturalny kandydat na hero Etapu II (np. z bulwaru po drugiej stronie Odry lub z przyczółka mostu, 28–35 mm, błękitna godzina lub jesienne popołudnie); ten sam model kamery fotomatchingu z Etapu I wykorzystać w Etapie II.

Dodatkowo [F]:
- „Dla wizualizacji … dopuszcza się dowolną technikę graficzną w tym wizualizacje komputerowe, rysunki perspektywiczne odręczne, kolaże itp., pod warunkiem zachowania czytelności i jednoznaczności dla potrzeb oceny przez Sąd”.
- Wyjaśnienia nr 09, odp. 61: w obszarze poza „Granicą opracowania” (M.04) wizualizacje z lotu ptaka mają przedstawiać **stan obecny zgodny ze zdjęciami F.17.A i F.17.B**.
- Plansze składane jako TIFF/JPG 100×70 cm @300 dpi oraz jako wydruki na sztywnym podkładzie; uzasadnienie wymogu wydruku: zachowanie „odcieni kolorystycznych, grubości linii” (rozdz. VII ust. 3 pkt 1 lit. b) → **kolor obrazów musi być sprawdzony na wydruku próbnym** (szczegóły w `plansze_metodyka.md`).
- Pliki pozbawione metadanych mogących zdeanonimizować autora (rozdz. VII ust. 3 pkt 4 lit. d).
- Kryteria oceny (rozdz. VIII ust. 1): równoważne — efektywność funkcji, trafność wpisania w tkankę, atrakcyjność i oryginalność, rozwiązania proekologiczne, dostępność i inkluzywność; drugorzędnie realność ekonomiczna. **[W]** Każda wizualizacja powinna „pracować” na co najmniej dwa kryteria (tabela w sekcji 3).

---

## 2. Analiza materiałów Organizatora pod kątem wizualizacji [P]

### 2.1 Zdjęcia lotnicze F.17.A i F.17.B (EXIF + XMP DJI)

| Parametr | F.17.A (od wschodu) | F.17.B (od zachodu) |
|---|---|---|
| Rozmiar pliku obrazu | 8470 × 4475 px (proporcja 1,893) | 7962 × 4505 px (1,767) |
| Aparat | DJI, model kamery FC8282 | jw. |
| Ogniskowa / ekw. 35 mm / przysłona | 6,72 mm / 24 mm / f/1,7 | jw. |
| Czas / ISO | 1/3200 s / 160 | 1/3000 s / 100 |
| Data i godzina | 2025-10-29 11:38:00 | 2025-10-29 11:57:36 |
| Oprogramowanie | Adobe Photoshop 27.0 (edycja 3.11.2025) | jw. |
| GPS (WGS-84) | 51,108317 N; 17,055470 E | 51,107810 N; 17,049755 E |
| PL-2000 strefa 6 (EPSG:2177), pyproj | E 6 433 856,4; N 5 664 124,1 | E 6 433 455,4; N 5 664 072,9 |
| Wysokość względna (od startu) | +87,8 m | +50,7 m |
| Wysokość „absolutna” DJI | 219,7 m | 182,6 m |
| Gimbal yaw / pitch / roll | −89,2° (patrzy na W) / −12,9° / 0 | +39,2° (patrzy na NE) / −11,4° / 0 |
| Odległość i azymut kamera → teren* | ~271 m, 271° (teren ≈ w środku kadru) | ~142 m, 66° (teren ~27° w prawo od osi gimbala) |

\* Środek terenu przybliżony z współrzędnych drzew z operatu (M.02 `zieleń/mazowiecka_drzewa.txt`, układ PL-2000: X≈5 664 130, Y≈6 433 585) — do zastąpienia środkiem granicy z M.04.

Wnioski:
- **[W]** Model FC8282 — z ekwiwalentu 24 mm i f = 6,72 mm wynika crop 3,57 → przekątna matrycy ≈ 12,1 mm, czyli matryca 1/1,3″ (szer. ≈ 9,7 mm przy 4:3); najpewniej kamera szerokokątna DJI Air 3 (identyfikacja niepotwierdzona — wyszukiwanie wskazało tylko serię DJI Air). Natywna klatka 8064 px → plik 8470 px oznacza **przeskalowanie** (widoczne też „malarskie” wyostrzenie liści przy powiększeniu — typowe dla AI-upscalingu/odszumiania).
- **[P]** Na wycinkach przy krawędziach kadru A piony budynków są praktycznie pionowe. Przy pochyleniu −12,9° i ogniskowej natywnej piony przy krawędzi kadru odchylałyby się o kilka stopni → **zdjęcia mają skorygowaną perspektywę pionową** (lub są panoramą o rzucie zachowującym piony). **[W]** Najlepszy model kamery do dopasowania: **aparat poziomy (pitch = 0, roll = 0) + pionowe przesunięcie obiektywu (shift_y < 0)** + nieznana ogniskowa i położenie punktu głównego. Szacunek: horyzont w A leży ok. 29% wysokości od góry → shift_y ≈ (0,29·H − 0,5·H)/W ≈ −0,11 (do precyzyjnego wyliczenia).
- **[W]** Wysokości DJI są niespójne (absolutna 219,7 m elipsoidalna/barometryczna vs teren ~117–118 m n.p.m. i względna 87,8 m) → wysokość kamery wyznaczyć z punktów kontrolnych; GPS (±2–5 m) i yaw jako wartości startowe/regularyzacja.

### 2.2 Pomiar kolorów i tonacji zdjęć (cele dla gradingu wstawki) [P]

Średnie sRGB z obszarów zdjęcia (po przeskalowaniu do szer. 1400 px):

| Próbka | sRGB | luma |
|---|---|---|
| B: nasłoneczniona jasna elewacja Urzędu Wojewódzkiego (lewa krawędź) | 217 / 209 / 196 | 210 |
| B: trawa w słońcu | 105 / 112 / 25 | 104 |
| B: asfalt w słońcu | 137 / 129 / 123 | 130 |
| B: niebo w górnej części | 6 / 145 / 226 | 121 |
| B: niebo przy horyzoncie | 152 / 191 / 214 | 184 |
| A: woda Odry | 76 / 76 / 49 | 74 |
| A: niebo górne / przy horyzoncie | 27/150/237 ; 162/202/226 | 130 ; 195 |
| Średnie nasycenie HSV (0–255) | A: 100; B: 104 | — |
| Percentyle luminancji p5/p95 | A: 22/213; B: 29/218 | — |

**[W]** Zdjęcia mają mocno „podkręcony” wygląd HDR drona: niebo cyjanowo-niebieskie z kanałem R ≈ 0, bardzo nasycona zieleń/żółcień, silny kontrast lokalny i wyostrzenie. Wstawka CG z neutralnym gradingiem będzie wyglądała na „wklejoną”. Trzeba dopasować: nasycenie (+15–30% względem neutralnego renderu), czerń (p5 ≈ 22–29), biel elewacji (≈ 210 luma, ciepła), wyostrzenie i mikrokontrast (sekcja 8.6).

### 2.3 Panoramy 360° (M.09) i zdjęcia otoczenia (M.10)

- [P] Trzy panoramy equirectangular 6000×3000 px z wysokości 30, 40 i 45 m (opis w `M.09._ZDJĘCIA_360_STOPNI.txt`, podglądy na kuula.co), wykonane 29.10.2025 11:48–11:52. Na panoramie 40 m widać tarczę słońca (wiersz odpowiada wys. ≈ 27°, zgodnie z obliczonymi ~25°).
- **[W] Zastosowania:** (1) obrót panoramy względem północy przez dopasowanie piksela słońca do azymutu z NOAA (dla 11:48 CET ≈ 183°); (2) środowisko odbić w szkle elewacji w obu fotomatchingach i w ujęciach naziemnych (tylko promienie glossy — LDR, słońce przepalone, więc **nie do oświetlenia**); (3) **widok z okien sali Sejmiku i holu Sejmiku z prawidłowej wysokości** (sala na najwyższej kondygnacji ok. 35–45 m — wybrać panoramę najbliższą wysokości oka w sali).
- [F] M.10: zdjęcia z drona z tego samego dnia (2016–4000 px) — referencje materiałów i drzew; M.11 ortofotomapy i widoki 3D SIP — kontekst do modelu.

### 2.4 Słońce dla Wrocławia — tabela robocza [P]

Algorytm NOAA (`umwd/src/umwd/sun.py`, zgodny z niezależnym obliczeniem). Azymut od północy zgodnie z ruchem wskazówek zegara.

| Data i godzina (czas lokalny) | Azymut | Wysokość | Komentarz [W] |
|---|---|---|---|
| 29.10.2025 09:30 CET | 147,5° | 19,8° | elewacje SE |
| **29.10.2025 11:38 CET (F.17.A)** | **180,7°** | **25,3°** | obowiązuje w wiz. 1 |
| **29.10.2025 11:57 CET (F.17.B)** | **185,8°** | **25,1°** | obowiązuje w wiz. 2 |
| 29.10.2025 13:00 | 202,3° | 22,7° | |
| 29.10.2025 14:30 | 224,0° | 15,0° | ciepłe, niskie światło na elewacje SW |
| 29.10.2025 15:30 | 236,8° | 7,8° | złota godzina (elewacje W) |
| 29.10.2025 16:00 | 242,9° | 3,8° | |
| 29.10.2025 16:45 | 251,7° | −2,8° | |
| 29.10.2025 17:00 | 254,6° | −5,1° | **błękitna godzina** |
| 29.10.2025 17:15 | 257,4° | −7,4° | koniec błękitnej godziny |
| 21.06.2026 20:30 CEST | 302,9° | 4,5° | jedyna pora z bezpośrednim słońcem na elewacji północno-zachodniej |
| 22.09.2026 16:00 CEST | 235,9° | 24,6° | |

[F] Złota godzina to umownie słońce od −6° do +6°, błękitna godzina od −4° do −8° (timeanddate.com — zaznacza brak oficjalnej definicji).

**[W] Orientacja elewacji (do potwierdzenia na M.02):** Odra płynie tu w przybliżeniu ze wschodu na zachód (kamera A na wschodzie patrzy na zachód wzdłuż rzeki), więc pierzeja od Wybrzeża Słowackiego jest zwrócona mniej więcej na **północ**. W październiku i w południe (zdjęcia!) elewacja od Odry jest w cieniu. Wynikają z tego trzy uczciwe strategie dla widoków od rzeki/mostu: (a) błękitna godzina z rozświetlonymi wnętrzami (ciepłe okna na chłodnym niebie — najlepiej działa dla elewacji północnej i sali Sejmiku jako „latarni”), (b) miękkie światło pochmurnego dnia, (c) letni wieczór (21.06 ok. 20:30 CEST) z niskim słońcem z NW — ale to łamie spójność pory roku. **Rekomendacja: (a)** dla jednego „emocjonalnego” ujęcia od rzeki; pozostałe ujęcia naziemne październikowe w słońcu z kierunku zgodnego z rzeczywistą orientacją.

---

## 3. Strategia zestawu: jedna „rodzina obrazów” [W]

Zasada: wszystkie obrazy wyglądają, jakby zrobił je jeden fotograf jednego jesiennego dnia (plus jeden wieczór). Spójność: pora roku, kolor drzew, ubiór ludzi, temperatura barwowa, kontrast, ziarno, proporcje kadrów.

| Wiz. | Pora / światło | Kadr i kamera | Kryteria, na które „pracuje” |
|---|---|---|---|
| 1 F.17.A | 29.10, 11:38, słońce z obliczeń, zdjęcie | kadr zdjęcia (ew. lekkie przycięcie, bez zmiany proporcji o >10%) | wpisanie w tkankę, skala dominanty 45 m wobec panoramy miasta i Ostrowa Tumskiego |
| 2 F.17.B | 29.10, 11:57 | kadr zdjęcia; projekt w pierwszym planie — najwięcej detalu (dachy, zieleń, ludzie ~70 px wysokości w pełnej rozdz.) | wpisanie, zieleń/retencja, dostępność terenu, funkcja parteru |
| 3 wejście | 29.10 ok. 14:30–15:30 (jeśli wejście od S/W) lub błękitna godzina (jeśli od N) | 1,6 m, 24–28 mm, shift_y 0,10–0,25, horyzont w dolnej 1/3 | dostępność (wejście z poziomu terenu, wózek), reprezentacyjność |
| 4 Słowackiego 5 | październik, światło skośne podkreślające gzymsy i relief | 1,6 m, 28–35 mm, ujęcie wzdłuż pierzei (linie gzymsów jako linie prowadzące) | trafność wpisania (ciągłość gzymsów, rytm, materiał) |
| 5 Mazowiecka 19 | październik, popołudnie | 1,6 m, 24–28 mm (ciasna ulica) | jw. + skala ulicy |
| 6 hol główny | dzień, światło dzienne + ciepłe sztuczne 3000–3500 K | 1,5–1,6 m, 20–24 mm, widoczny punkt informacji i kierunek do wind | funkcja, orientacja, dostępność |
| 7 hol Sejmiku | późne popołudnie / zmierzch z widokiem na Odrę (panorama 40–45 m) | 1,6 m, 20–24 mm | reprezentacyjność, widok miasta |
| 8 sala Sejmiku | dzień, kontrolowane światło dzienne, sesja w toku | z tyłu/z galerii publiczności, oś symetrii (perspektywa jednopunktowa) 20–24 mm | funkcja, demokracja/jawność, akustyka, dostępność |
| (opc.) 9 | błękitna godzina od Mostu Grunwaldzkiego / bulwaru | 1,6 m, 28–35 mm, długi czas naświetlania (rozmyte światła tramwaju) | atrakcyjność, „latarnia” Sejmiku |

**[W] Dlaczego jesień, a nie wiosna:** wiz. 1–2 muszą być październikowe (zdjęcia); mieszanie pór roku w jednym zestawie osłabia wiarygodność i „rodzinność”. Złota jesień z żółtymi koronami (klony, lipy, topole widoczne na zdjęciach) jest atrakcyjna i lokalnie charakterystyczna dla wrocławskich bulwarów. Ryzyko: nagie drzewa wyglądają smutno → używać fazy „koniec października” (korony częściowo żółte, część zielona) zgodnie ze zdjęciami.

---

## 4. Kompozycja i kamera

### 4.1 Zasady (źródła)

- [S] Alex Hogrefe (Visualizing Architecture, artykuł w Architizer „7 Rules for Composing Powerful Architectural Perspectives”): horyzont widoków z poziomu oka w **dolnej tercji**; ważne elementy na liniach/punktach trójpodziału; **piony równoległe** („Two Point Perspective” przed renderem); **„Don’t be a giant” — kamera ok. 6 stóp (≈1,8 m)**; jeśli wyżej, to wyraźnie (25–30 stóp ≈ 8–9 m, np. z balkonu/tarasu); perspektywa jednopunktowa daje spokój i monumentalność; „podejdź bliżej i opowiedz jedną rzecz”.
- [S] Lasse Rode (Studio XOIO) na blogu Ronena Bekermana (2013): unikać ogniskowych krótszych niż 30 mm, zwykle 35–55 mm; plany: pierwszy, środkowy, dalszy; tylko najjaśniejszy punkt blisko bieli, inne „białe” powierzchnie ok. 190–220 (8 bit); lekkie ziarno uwiarygadnia; postprodukcja minimalna, raczej odejmować niż dodawać.
- [S] D5 Render (poradnik kamer): typowa wysokość oka 1,5–1,8 m; wnętrza 1,5–1,7 m.
- [F] Blender Manual (Cameras): *shift* „pozwala korygować punkty zbiegu”; poziome linie pozostają poziome przy przesunięciu, a skośne przy obrocie kamery; „użycie shift jest równoważne wyrenderowaniu obrazu z większym polem widzenia i przycięciu go poza środkiem”.
- [F] Canon (fotografia architektury, obiektywy TS-E) i praktyka fotografii architektury: aparat wypoziomowany + przesunięcie obiektywu do góry zamiast odchylania (wtórnie, z wyników wyszukiwania; strona Canon zwróciła 403).
- [F] Vishwanath, Girshick & Banks (2005, *Nature Neuroscience* 8(10):1401–1410): system wzrokowy kompensuje oglądanie obrazu z „niewłaściwego” miejsca dzięki szacowaniu orientacji powierzchni obrazu, ale autorzy opisują też **postrzegane zniekształcenia obrazów szerokokątnych** (znane z abstraktu/omówień; pełnego tekstu nie czytano). **[W]** Na planszy oglądanej z 0,5–1,5 m zniekształcenia brzegów kadrów <24 mm (HFOV >74°) będą widoczne — trzymać 24–35 mm na zewnątrz.

### 4.2 Parametry do zastosowania [W]

Pole widzenia dla matrycy 36 × 24 mm [P, obliczenia]:

| Ogniskowa | HFOV | VFOV (3:2) | Zastosowanie |
|---|---|---|---|
| 18 mm | 90,0° | 67,4° | tylko awaryjnie we wnętrzu |
| 20 mm | 84,0° | 61,9° | hol główny, sala Sejmiku |
| 24 mm | 73,7° | 53,1° | wejście, ciasna ulica, hol |
| 28 mm | 65,5° | 46,4° | ujęcia ulicy, relacje z kamienicami |
| 35 mm | 54,4° | 37,8° | widok od rzeki/mostu, detal elewacji |
| 50 mm | 39,6° | 27,0° | detal / kadr „teleobiektywowy” z drugiego brzegu |

**Przesunięcie obiektywu — wzór.** Dla poziomej kamery punkt o wysokości Δh nad okiem w odległości poziomej D pada na matrycę w odległości y = f·Δh/D od środka. W Blenderze `shift_y` wyraża się w jednostkach większego wymiaru kadru (dla kadru poziomego: szerokości matrycy), więc aby górna krawędź kadru (pół-wysokość h_s/2) objęła punkt:
`shift_y ≥ (f·Δh/D − h_s/2) / sensor_width`.
Przykład: dominanta 45 m, oko 1,6 m (Δh = 43,4 m), 24 mm, matryca 36×24: przy D = 60 m → y = 17,4 mm, h_s/2 = 12 mm → **shift_y ≥ 0,15**; przy D = 40 m → 26 mm → shift_y ≥ 0,39 (za dużo — górne partie się „rozciągają”; lepiej świadomie uciąć dominantę albo cofnąć kamerę). **Praktyczny limit shift_y ≈ 0,30** (odpowiada ±11–12 mm prawdziwego obiektywu TS na 36 mm).

**Kadry:** zewnętrzne 3:2 lub 16:9; hero może być 2:1 (pasuje do proporcji zdjęć lotniczych 1,77–1,89); wnętrza 3:2 lub 4:3. Ustalić proporcje razem z siatką planszy (patrz `plansze_metodyka.md`) **przed** renderem.

**Kompozycja (lista):** linie prowadzące (krawędź bulwaru, gzymsy pierzei, linie tramwajowe, posadzka holu) prowadzą do wejścia/dominanty; pierwszy plan jako rama (gałęzie z żółtymi liśćmi, balustrada mostu, fragment kamienicy) — 5–15% kadru, częściowo nieostry lub w cieniu; wejście lub dominanta na punkcie trójpodziału; niebo zajmuje 25–40% kadru w ujęciach z dominantą; jeden punkt kulminacji (najjaśniejszy/najbardziej kontrastowy) = to, co chcemy pokazać.

---

## 5. Światło i atmosfera

### 5.1 Fakty techniczne Blender 5.2 [F]/[P]

- [F] Typy nieba (Sky Texture): **Single Scattering** (ulepszony model Nishity, „legacy”), **Multiple Scattering** (García Liñán, „najdokładniejszy”, domyślny w 5.2), Preetham i Hosek/Wilkie (legacy, do usunięcia). Single i Multiple są bardzo jasne (fizycznie) — obniżyć ekspozycję w Color Management. Parametry: Sun Elevation, Sun Rotation, Altitude, Air, Aerosols, Ozone, Sun Disc/Size/Intensity. [P] w bpy 5.2.4: `sky_type ∈ {SINGLE_SCATTERING, MULTIPLE_SCATTERING, PREETHAM, HOSEK_WILKIE}`, `aerosol_density` (nie `dust_density`).
- [P] **Konwencja `sun_rotation`:** test renderów (4 kierunki kamery) — `sun_rotation = 0` → słońce na +Y, `90°` → +X, `180°` → −Y, `270°` → −X. Przy X = wschód, Y = północ: **`sun_rotation = radians(azymut_kompasowy)`**.
- [P] Zmierzch: Multiple Scattering przy wysokości słońca −6° wciąż daje jasne, użyteczne niebo (średnia jasność kadru ~1/7 dziennej przy Standard), −9° ~1/14; Single Scattering przy −6° już prawie czarne. → **błękitna godzina: Multiple Scattering, el −4…−7°**, plus sztuczne oświetlenie wnętrz.
- [F] Transformacje widoku: Standard, ACES 1.3, ACES 2.0, Khronos PBR Neutral, **AgX** (16,5 stopnia dynamiki, „bardziej fotorealistyczna” niż Filmic, desaturuje prześwietlone kolory), Filmic (przestarzały), False Color (mapa ekspozycji). Looks dla AgX: Punchy, Greyscale, Very High … Very Low Contrast. Ekspozycja w stopniach: `out = render × 2^exposure`. [P] w 5.2 dostępny też balans bieli w `view_settings` (`use_white_balance`, `white_balance_temperature`).
- [F] Principled BSDF ma tryb **Thin Wall** („przydatny do cienkich struktur, takich jak papier, liście i szyby okienne”).

### 5.2 Kalibracja słońca i nieba [P]

Test: pozioma biała płaszczyzna Lambert (albedo 1), niebo Multiple Scattering, siła tła 1,0, radiancja liniowa:

| Wys. słońca | całość | samo niebo (G) | udział słońca (G) | słońce:niebo | ekwiwalent lampy Sun | kolor słońca (lin., R=1) |
|---|---|---|---|---|---|---|
| 10° | 7,4/6,3/5,6 | 2,33 | 3,99 | 1,7 : 1 | 72 W/m² | 1,00 / 0,67 / 0,30 |
| 25° | 21,5/19,1/16,7 | 3,51 | 15,63 | 4,5 : 1 | **117 W/m²** | **1,00 / 0,80 / 0,55** |
| 45° | 38,0/34,4/30,6 | 4,31 | 30,07 | 7,0 : 1 | 133 W/m² | 1,00 / 0,85 / 0,65 |

Rekomendacje [W]:
1. **Najprościej i fizycznie spójnie:** `sun_disc = True` (słońce z nieba), bez lampy Sun; cienie miękkie wg `sun_size` (domyślnie ≈0,545°).
2. Jeśli potrzebna lampa Sun (np. kontrola cieni, linking): `sun_disc = False`, lampa o sile ≈117 W/m² i kolorze (1,0; 0,80; 0,55) przy 25° (interpolować wg tabeli), `angle = 0,53°`; albo proporcjonalnie zmniejszyć siłę tła nieba.
3. **Ekspozycja startowa dzień słoneczny: −4,0…−4,5 EV** (szara karta 18% ≈ środkowa szarość), dopracować w widoku False Color.
4. Spójność z fotomatchingiem: te same proporcje słońce:niebo w ujęciach naziemnych z października (el 7–25°) → cienie wyraźne, ale z niebieskawym wypełnieniem (niebo daje ~20–35% światła na płaszczyznach w cieniu).

### 5.3 Atmosfera [W]

- Perspektywa powietrzna (mgiełka) — z passu **Mist** w kompozycji (tani na CPU), nie z wolumetrii; dla aerial: 3–8% rozjaśnienia i desaturacji obiektów >300 m. Dla wstawek: dopasować do ciemności cieni sąsiednich budynków na zdjęciu (zamiast „na oko”).
- Chmury: w ujęciach naziemnych niebo z prawdziwej fotografii HDRI (Poly Haven, licencja **CC0** — [F] „You can use our assets for any purpose… do not need to give credit”), wybrać HDRI z cumulusami podobnymi do zdjęć F.17 i obrócić tak, by słońce na HDRI pokrywało się z obliczonym kierunkiem; alternatywnie niebo proceduralne + osobna płaszczyzna tła z chmurami tylko dla kamery.
- Błękitna godzina: niebo el −5°, białe balanse ok. 4500–5000 K, wnętrza 3000 K, oświetlenie zewnętrzne 3000 K; czas naświetlania „długi” — smugi świateł tramwaju/rowerów (motion blur lub post), woda Odry jako lustro z odbiciem rozświetlonej sali Sejmiku.
- Precedens historyczny: zmierzchowe fotografie modernizmu (np. Julius Shulman, Case Study House #22, 1960) — wiedza ogólna, bez weryfikacji źródłowej w tej sesji.

---

## 6. Materiały, szkło, zieleń

### 6.1 PBR i nieregularność [W] (+ [F] dane)

- Albedo realnych materiałów w zakresie ~0,04–0,85 (liniowo); nigdy czysta biel 1,0. [F] Baza physicallybased.info (API, wartości liniowe wg serwisu — do weryfikacji): beton 0,51; cegła (0,262; 0,095; 0,061); marmur (0,83; 0,79; 0,75); piasek (0,44; 0,39; 0,23); aluminium metal (0,92; 0,92; 0,92); stal nierdzewna (0,67; 0,64; 0,60); szkło IOR 1,52; „gray card” jako wzorzec.
- Każdy materiał ma choćby minimalną zmienność: szum roughness 0,05–0,15, zmienność odcienia między elementami prefabrykowanymi ±3–5% (losowanie po ID obiektu/ściany), zabrudzenia w dolnej strefie cokołu i pod parapetami (maska AO/pointiness), krawędzie fazowane 0,5–2 cm (Bevel w shaderze lub geometrii), by łapały światło.
- Skala tekstur sprawdzana na referencji 1,8 m (człowiek) i module materiału (cegła 25×6,5 cm, płyta kamienna 60–120 cm).
- Kontekst lokalny: tynki kamienic Przedmieścia Oławskiego w ciepłych beżach/ochrach, ceglane/ceramiczne detale, czerwone dachówki (widoczne na zdjęciach) — paleta elewacji projektu ma być z nimi w dialogu (decyzja projektowa poza tym dokumentem).

### 6.2 Szkło i okna [W]

- Szyby jako pojedyncze płaszczyzny z Principled BSDF **Thin Wall** (Transmission 1, IOR 1,52, roughness 0–0,02) lub prosty shader „architektoniczny” (mix Glass/Transparent dla promieni cienia: Light Path → Is Shadow Ray), aby słońce wpadało do wnętrz bez kaustyk.
- **Odbicia = prawdziwe otoczenie:** środowisko z panoram M.09 podpięte tylko pod promienie glossy (Light Path → Is Glossy Ray miesza Background(panorama) z Background(niebo)); obrócone wg słońca na panoramie (sekcja 2.3).
- **Puste czarne okna to najczęstszy „zdradzacz” CG.** Za każdym oknem w kadrze: sufit z oprawami (świecącymi w błękitnej godzinie), zarys mebli, zróżnicowane rolety/żaluzje (20–40% okien częściowo zasłoniętych), różne temperatury i natężenia światła. W dali wystarcza „interior mapping”/płaszczyzna z teksturą wnętrza 1–3 m za szybą.
- Lekkie zniekształcenie odbić (falowanie tafli — szum normalnych o bardzo małej amplitudzie, różny kąt dla tafli) odróżnia realne szkło od lustra.

### 6.3 Zieleń [W]

- **Pora roku zgodna ze zdjęciami (koniec października):** mieszanka koron żółtych (klon zwyczajny, lipa, topola), pomarańczowo-czerwonych (klony), zielonych (część drzew, iglaki — np. świerki kłujące widoczne na F.17.A) i kilku prawie bezlistnych; liście na trawnikach i chodnikach w miejscach pod drzewami.
- Gatunki brać z operatu dendrologicznego M.06 (PDF/DWG; plik tekstowy w `tekst/` nie zawiera listy gatunków) i ze zdjęć M.10; nowe nasadzenia — młode drzewa (obwód 16–20 cm, wys. 4–6 m) z palami/kotwami w ujęciach z bliska (realizm).
- Technika: Geometry Nodes (`Distribute Points on Faces` + `Instance on Points`) z 3–6 wariantami drzewa na gatunek, losowy obrót i skala ±15%; liście jako płaszczyzny z alfą → `transparent_max_bounces` ≥ 16. Trawa: pas pierwszoplanowy geometrią, dalej tekstura.

---

## 7. Ludzie i życie [W] (+ [S])

- [S] Krytyka „scalies” (Gizmodo; Dezeen — artykuł niedostępny 403, treść wg wyników wyszukiwania; Iconeye; The Site Magazine): biblioteki sztafażu są mało zróżnicowane; wizualizacje powinny pokazywać m.in. osoby z kulami, na wózkach, z ograniczonym wzrokiem. Nie ma badania ilościowego wpływu na jury — traktować jako normę dobrej praktyki, nie dowód.
- **Liczebność (heurystyka):** ujęcia naziemne 8–25 osób w środkowym planie, 0–3 częściowo w pierwszym planie (nieostre lub z rozmyciem ruchu), grupy 2–3 osoby, kierunek ruchu w stronę wejścia; budynek pozostaje bohaterem. Aerial B: 30–80 postaci (przy ~142 m i pełnej rozdzielczości człowiek ma kilkadziesiąt pikseli). Hol: 10–20 osób. Sala Sejmiku: sesja w toku — prezydium + ok. 60% miejsc radnych, kilka osób w strefie mediów i na galerii.
- **Zróżnicowanie:** wiek (seniorzy, rodzice z wózkiem, młodzież), płeć, sylwetki; **1 osoba na wózku w wiz. 3 (wjeżdża samodzielnie przez drzwi wejścia z poziomu terenu)**, w wiz. 6 (przy obniżonym blacie punktu informacji, obok tyflomapy i ścieżki prowadzącej), w wiz. 8 (stanowisko radnego/radnej dostępne z poziomu przejścia); w wiz. 8 widoczne stanowisko tłumacza PJM w kadrze kamery transmisji. Rowery (Wrocław ma silną kulturę rowerową) — 1–3 rowerzystów na bulwarze.
- **Spójność:** ubiór październikowy (płaszcze, kurtki, szaliki); cienie postaci zgodne ze słońcem; nikt nie patrzy w obiektyw; brak pozowanych „biznesmenów z teczkami” w nadmiarze.
- **Źródła modeli:** MPFB 2 (MakeHuman Plugin for Blender; [S] kod GPL-3.0, dołączone zasoby CC0, eksport modeli MakeHuman jako CC0 — sprawdzić oryginalny LICENSE przed użyciem) — 3D ludzie dają poprawne cienie/odbicia w średnim planie; z bliska ewentualnie wycięte postaci 2D z licencją pozwalającą na użycie lub ostrożne edycje generatywne (sekcja 10.4).

---

## 8. Fotomatching na F.17.A i F.17.B — procedura krok po kroku

### 8.1 Zasada [F]
- Blender: obiekt z opcją **Mask → Shadow Catcher** „otrzymuje tylko promienie cienia”, oddziałuje z obiektami CG przez światło pośrednie; **z włączonym passem Shadow Catcher przechwytywane są wszystkie interakcje światła pośredniego** (bez passu — przybliżenie). Pass „Shadow Catcher”: „można przemnożyć z istniejącym materiałem filmowym”. Obiekt może też być **Holdout** (wycina alfę). Film → Transparent; opcje `film_transparent_glass` i `film_transparent_roughness` [P].
- fSpy (fspy.io, samouczek): kamera z dwóch punktów zbiegu (prostokąt) + opcjonalnie punkt główny ręcznie lub z trzeciego punktu zbiegu; **dystorsja obiektywu nie jest modelowana**; kadrowanie asymetryczne przesuwa punkt główny; importer do Blendera (GPL-3.0; brak informacji o zgodności z 4.x/5.x). **[W]** fSpy to aplikacja GUI — w naszym środowisku bezgłowym zastępujemy ją **rozwiązaniem numerycznym (PnP z ograniczeniami)** w Pythonie (scipy + OpenCV z systemowego `python3`).

### 8.2 Model kontekstu (proxy) [W]
1. Lokalny układ: X = E − E0, Y = N − N0 (np. E0 = 6 433 500, N0 = 5 664 000) — **koniecznie lokalne zero**, bo float32 w Blenderze przy współrzędnych rzędu 6,4·10⁶ m traci precyzję do decymetrów. Zgodnie z konwencją `blib.py` (X = E, Y = N, Z = góra).
2. Teren: NMT z `M.02/model terenu/mazowiecka_pikiety do nmt.txt` (siatka TIN), w granicy opracowania — teren projektowany (CG), poza nią — Shadow Catcher.
3. Budynki istniejące: obrysy z mapy do celów projektowych + wysokości (inwentaryzacje M.07, M.08 dla kamienic sąsiednich; pozostałe z SIP 3D/ortofoto/pomiaru z panoram) jako bryły LOD1–2 → Shadow Catcher (otrzymują cień od nowego budynku i same go zasłaniają tam, gdzie są przed nim).
4. Drzewa przed budynkiem: maska z obrazu (ręcznie/półautomatycznie), drzewa poza kadrem budynku pomijamy.

### 8.3 Wyznaczenie kamery [W]
1. **Punkty kontrolne (≥10 na zdjęcie, rozproszone, najlepiej wokół terenu):** narożniki gzymsów i cokołów kamienic Mazowiecka 19 / Wybrzeże Słowackiego 5 (wysokości z inwentaryzacji), narożniki Urzędu Wojewódzkiego, pylony i węzły Mostu Grunwaldzkiego, krawężniki/punkty z mapy zasadniczej (X, Y, H z mapy). Współrzędne pikseli mierzyć na pełnej rozdzielczości (8470/7962 px).
2. **Model 1 (rekomendowany, piony skorygowane):** kamera pozioma; niewiadome: Xc, Yc, Zc, azymut ψ, ogniskowa w pikselach F, punkt główny (cx, cy). Rzut: d = P − C; r = (cos ψ, −sin ψ, 0), u = (0, 0, 1), fwd = (sin ψ, cos ψ, 0); `u_px = cx + F·(d·r)/(d·fwd)`, `v_px = cy − F·(d·u)/(d·fwd)`. Minimalizacja `scipy.optimize.least_squares` z regularyzacją położenia do GPS (σ ≈ 5 m) i ψ do yaw gimbala (σ ≈ 5°).
3. **Model 2 (kontrolny):** pełny pinhole z pitch/roll (OpenCV `solvePnP`/`calibrateCamera` z jednym współczynnikiem dystorsji k1). Wybrać model o mniejszym RMS; **cel RMS < 3 px** przy 8k (≈0,04% szerokości). Systematyczny „wachlarz” residuów → dystorsja/rzut panoramiczny → dopasować **lokalnie** (punkty tylko w promieniu ~25% kadru wokół terenu) albo z k1 i zrobić render nieskorygowany + `cv2.remap` z tą samą dystorsją.
4. **Konwersja do Blendera:** `sensor_fit = 'HORIZONTAL'`, `sensor_width = 36`, `lens = F·36/W`; rotacja `(90° + pitch, roll, −ψ)` (dla modelu 1: `(90°, 0, −ψ)`; [P] kamera z `rotation_euler = (90°, 0, 0)` patrzy na +Y, dodatni obrót Z skręca w lewo); `shift_x = (W/2 − cx)/W`, `shift_y = (cy − H/2)/W` (jednostki: większy wymiar kadru — **znaki zweryfikować renderem testowym**: nakładka krawędzi proxy na zdjęcie, różnice < 3 px).
5. Rozdzielczość renderu = rozdzielczość zdjęcia; renderować tylko region budynku (Render Region + Crop), co przy kadrze A (budynek ok. 10–20% wysokości kadru — szacunek [W]) skraca czas kilkukrotnie.

### 8.4 Światło we wstawce [W]
- Słońce: azymut/wysokość z sekcji 2.4 (A: 180,7°/25,3°; B: 185,8°/25,1°) — **zweryfikować na cieniach istniejących obiektów** (słupy, drzewa, kamienice) przez wyrenderowanie cienia proxy i porównanie z cieniem na zdjęciu; korekta ±2° dopuszczalna (zegar drona, refrakcja, korekty w Photoshopie).
- Niebo: Multiple Scattering + ewentualnie panorama M.09 w odbiciach.
- **Kalibracja „białej karty” na zdjęciu:** wymodelować w proxy fragment nasłonecznionej jasnej elewacji Urzędu Wojewódzkiego (albedo ~0,65–0,75), wyrenderować bez Shadow Catchera i dobrać ekspozycję/balans, aż jego sRGB ≈ 217/209/196 (±3%); to samo dla ściany w cieniu (proporcja światło/cień). Dopiero potem renderować nowy budynek.

### 8.5 Kompozycja (compositing) [W]
- Dla ujęć na zdjęciu: **View Transform = Standard** (zdjęcie wchodzi jako sRGB → liniowo → wraca bez zmian), CG eksponowane tak, by jego światła nie przekraczały ~1,0 (miękki „bark” dodać później w gradingu całego obrazu).
- Formuła (liniowo): `wynik = zdjęcie_lin × ShadowCatcher + CG_combined(premultiplied)`, następnie maska pierwszego planu (drzewa/latarnie przed budynkiem) nakładana ze zdjęcia na wierzch.
- Wewnątrz granicy opracowania usuwamy istniejące elementy, które projekt zastępuje (trawnik, ścieżki, ewentualnie drzewa do wycinki wg projektu) — teren w granicy renderowany w całości jako CG; granica przejścia CG/zdjęcie wzdłuż krawężników/krawędzi, nie przez środek trawnika.
- Poza granicą: **bez zmian** (stan obecny — wyjaśnienia nr 09).

### 8.6 Dopasowanie do „charakteru” zdjęcia [W]
- Nasycenie wstawki zwiększyć do poziomu sąsiednich budynków (średnie nasycenie zdjęć ~100/255).
- Czerń: najciemniejsze cienie CG nie ciemniejsze niż cienie sąsiednich kamienic w tej samej odległości (p5 zdjęć 22–29).
- Ostrość: zdjęcia mają silne wyostrzenie po upscalingu — porównać energię krawędzi (np. wariancja Laplasjanu) w oknie 512 px na istniejącym budynku i na wstawce; dopasować unsharp mask (promień 1,5–2,5 px przy 8k, 60–120%).
- Ziarno/szum: luminancyjny, σ ≈ 1–2 poziomy (8 bit), zgodny ze zdjęciem; bez aberracji chromatycznej (zdjęcia ich praktycznie nie mają po obróbce).
- Ludzie, samochody na nowych placach/drogach w granicy — w tej samej skali i kierunku cieni co na zdjęciu.

---

## 9. Wnętrza: hol główny, hol Sejmiku, sala Sejmiku [W] (+ [F] program)

**Wspólne:** światło dzienne (niebo + słońce przez okna, portale w otworach — [P] `light.cycles.is_portal` dostępne) + sztuczne 3000–3500 K w przestrzeniach reprezentacyjnych; ekspozycja tak, by widok za oknem nie był przepalony (AgX pomaga, ale okna nadal 1,5–2,5 EV jaśniejsze od wnętrza — tak wygląda prawdziwa fotografia); path guiding włączony (CPU). Kamera 1,5–1,6 m, poziomo, 20–24 mm, piony pionowe.

**Hol główny (wiz. 6):** [F] M.01: hol to węzeł komunikacyjny i przestrzeń reprezentacyjna, z poziomu terenu, ze strefami: kancelaria ogólna (3 stanowiska), punkt informacyjny, ochrona, recepcja/poczekalnia, toalety; obok bistro; „łatwa orientacja w przestrzeni”; tyflomapy w holu. **[W] W kadrze:** wejście (skąd przyszliśmy) lub kierunek do wind/schodów, punkt informacyjny jako pierwszy punkt orientacyjny, światło dzienne z góry/z boku, materiał „ciepły” (drewno, kamień) z widoczną chłonnością akustyczną (lamele, perforacje), ścieżki prowadzące w posadzce w kontrastowym odcieniu, ludzie w ruchu.

**Hol sali Sejmiku (wiz. 7):** reprezentacyjny „foyer obywatelskie”, widok na Odrę/Ostrów Tumski z wysokości 30–45 m (panorama M.09 właściwej wysokości jako tło okien), późne popołudnie lub zmierzch; dostęp z wind dla większej grupy (M.01: „szybkie przemieszczanie się większej liczby osób”).

**Sala Sejmiku (wiz. 8):** [F] M.01: do 100 osób, amfiteatr z podwyższanymi rzędami, strefy radnych, prezydium, zarządu, gości, mediów, obsługi i **tłumaczy PJM**; stałe stanowiska z systemem głosowania, tabletami, mikrofonami; dostępność stanowisk radnych, prezydium i mównicy dla OzN; publiczność z oddzielnym wejściem; transmisja i nagrywanie. **[W] W kadrze:** oś symetrii (perspektywa jednopunktowa) na prezydium; widoczne podwyższenia rzędów i przejścia bez schodów do co najmniej jednego rzędu; galeria publiczności (np. za szklaną przegrodą); stanowisko tłumacza PJM; **prezydium nie na tle przeszklenia bez osłon** (przeciwświatło niszczy obraz transmisji — argument funkcjonalny zrozumiały dla Marszałka/Sekretarza); światło dzienne z góry lub z boku z kontrolą olśnienia; akustyka widoczna w materiałach (drewniane lamele, tkaniny, panele perforowane); symbolika zgodna z protokołem (miejsce na flagi/herb) — bez przesady.

---

## 10. Postprodukcja i spójna paleta [W]

### 10.1 Kolejność (Python: numpy/PIL; lub kompozytor Blendera)
1. Render 16-bit PNG (AgX) lub EXR wielowarstwowy (passy: Mist, Shadow Catcher, Cryptomatte/Object Index dla masek).
2. Normalizacja ekspozycji i balansu bieli do wspólnego wzorca (szara karta w scenie).
3. Wspólna krzywa tonalna (łagodne S), wspólny „look” dla wszystkich ujęć zewnętrznych (jedna funkcja/LUT), wariant wnętrzowy z tą samą paletą.
4. Kontrast lokalny („clarity”): unsharp mask promień 50–100 px, 10–20%.
5. Mgiełka z passu Mist: 3–8% dla dalekich planów.
6. Bloom/glare tylko na najjaśniejszych punktach (Glare node Fog Glow/Bloom, próg ≥1,0, bardzo delikatnie).
7. Winieta 5–12% (eliptyczna, miękka) — w 5.2 brak gotowego węzła Vignette w kompozytorze [P] (dostępne m.in. Glare, Lensdist, Ellipse Mask), więc w numpy.
8. Skalowanie do rozdzielczości druku (Lanczos), potem wyostrzenie pod druk (promień 1–2 px, 50–100%).
9. Ziarno luminancyjne σ ≈ 1–1,5/255 (ujednolica CG i zdjęcia, zapobiega bandingowi nieba).
10. Eksport 8-bit sRGB, **bez metadanych** (sekcja 10.4).

### 10.2 Paleta zestawu
- Światła: ciepłe (ok. 5000–5500 K „look”), cienie lekko chłodne (niebieskawe wypełnienie nieba) — naturalne dla słonecznego października.
- Kolory dominujące z kontekstu: ochry i beże tynków, czerwienie dachówek, żółcie jesiennych koron, oliwkowa zieleń Odry (zdjęcie: woda ≈ 76/76/49), błękit nieba. Akcent = materiał projektu.
- Nasycenie: ujęcia naziemne umiarkowane (bliżej naturalnego), aerial dopasowane do „podkręconych” zdjęć — różnica ma być mała; kontrolować w histogramie nasycenia całego zestawu obok siebie.
- [S] Lasse Rode: tylko najjaśniejszy punkt blisko bieli; „białe” elewacje 190–220/255.

### 10.3 Rozmiary obrazów pod planszę [W]
Ostrość wzroku 1′ łuku [P, obliczenie]: 0,5 m → 175 ppi; 0,7 m → 125 ppi; 1,0 m → 87 ppi.

| Rola na planszy | Wymiar druku (przykład) | Docelowo 200 ppi | Minimum 150 ppi |
|---|---|---|---|
| Hero | 60 × 40 cm | 4724 × 3150 px | 3543 × 2362 px |
| Wiz. średnia | 40 × 27 cm | 3150 × 2126 px | 2362 × 1594 px |
| Wiz. mała | 30 × 20 cm | 2362 × 1575 px | 1772 × 1181 px |
| Fotomatch A/B | ~60 cm szer. | natywnie 8470/7962 px (≈330–360 ppi) | — |

Plansza jest składana w 300 dpi — obrazy o mniejszej gęstości skalować Lanczosem do docelowego rozmiaru w pikselach planszy (bez „pikselozy” — tylko kontrola ostrości z 0,5 m na wydruku próbnym).

### 10.4 Edycje generatywne i anonimowość [W]
- Dozwolone do: dopracowania sztafażu w średnim/dalekim planie, liści, nieba; zakazane do geometrii, materiałów i proporcji architektury (ryzyko niezgodności z rysunkami — Sąd porównuje).
- Każdy fragment po edycji obejrzeć w 100% (dłonie, twarze, napisy, szprychy rowerów).
- **Usuwać wszystkie metadane** (EXIF, XMP, IPTC, C2PA/„Content Credentials”, nazwy autorów w profilach ICC); Regulamin rozdz. VII ust. 3 pkt 4 lit. d: metadane deanonimizujące mogą skutkować niedopuszczeniem pracy.

---

## 11. Ustawienia Blender Cycles 5.2 na CPU (4 rdzenie)

### 11.1 Fakty [F]/[P]
- [F] Adaptive sampling: próg szumu typowo 0,1–0,001; 0 = automatyczny; Min Samples 0 = automatycznie.
- [F] Denoising: OpenImageDenoise „zwykle najwyższa jakość”; passy wejściowe „co najmniej Albedo”, najlepiej Albedo + Normal; Prefilter Accurate = więcej detalu; Quality High.
- [F] Path guiding: **tylko CPU**, pomaga gdy dotarcie do światła jest trudne (np. pokój oświetlony przez mały otwór); „zwykle 128–256 próbek treningowych wystarcza”.
- [F] Light tree: lepsze próbkowanie wielu świateł (np. setki opraw w holu), kosztem dłuższej próbki.
- [P] Domyślne w bpy 5.2.4: samples 4096, adaptive 0,01, denoiser OIDN, prefilter ACCURATE, quality HIGH, passy RGB_ALBEDO_NORMAL, max_bounces 12 (diffuse 4, glossy 4, transmission 12, transparent 8), clamp indirect 10, filtr Blackman-Harris 1,5 px, auto tile 2048, path guiding wyłączony, light tree włączony.
- [P] Benchmark (prosta scena: 30 brył, szyba Thin Wall, niebo + słońce, 960×540, 64 spp, OIDN): **16,7 s ⇒ ≈50 s na (MPx × 100 spp)**; z path guiding 27,1 s (+62%).

### 11.2 Presety [W]

| Parametr | Draft (kompozycja) | Mid (akceptacja) | Final zewn. | Final wnętrze | Fotomatch |
|---|---|---|---|---|---|
| Rozdzielczość | 1200 px szer. | 2400 px | 3500–4800 px | 3150–3600 px | natywna zdjęcia, Render Region |
| Max samples | 32 | 128 | 512 | 1024 | 512 |
| Adaptive threshold | 0,1 | 0,05 | 0,015–0,02 | 0,01–0,02 | 0,015 |
| Min samples | 0 | 16 | 32 | 64 | 32 |
| Denoise | OIDN, Albedo | OIDN, Albedo+Normal, Accurate | jw., Quality High | jw. | jw. |
| Path guiding | nie | nie | nie (zwykle) | **tak**, training 128 | nie |
| Max / diffuse / glossy / transmission | 4/2/2/4 | 8/3/4/8 | 8/3/4/8 | 12/6/6/8 | 8/3/4/8 |
| Transparent bounces | 8 | 16 | 16–24 (liście) | 16 | 16 |
| Clamp direct / indirect | 0 / 5 | 0 / 6 | 0 / 6–10 | 0 / 3–6 | 0 / 6 |
| Caustics refl./refr. | off | off | off | off | off |
| Filter glossy | 1,0 | 1,0 | 0,5 | 0,5 | 0,5 |
| Time limit (bezpiecznik) | 3 min | 15 min | 2–3 h | 3–4 h | 1–2 h |
| View transform | AgX | AgX | AgX (+ look Base/Medium High Contrast) | AgX | **Standard** |
| Wyjście | PNG 8 | PNG 16 | PNG 16 + EXR passy | PNG 16 + EXR | EXR multilayer (Combined, Shadow Catcher, Mist) |

Dodatkowo: `render.use_persistent_data = True` przy serii ujęć z jednej sceny; `Simplify` (ograniczenie subdivision/instancji) w draftach; `film_transparent` dla fotomatchingu; wyłączyć stamp/metadane renderu.

### 11.3 Budżet czasu (szacunek) [W]
Na bazie [P] 50 s/(MPx·100 spp) × współczynnik złożoności 3–6 (roślinność, szkło, wiele świateł) × średnia faktyczna liczba próbek przy adaptive (~50–70% maksimum):

| Obraz | MPx | śr. spp | Szacunek |
|---|---|---|---|
| Hero 4724×3150 | 14,9 | ~250 | 1,0–2,0 h |
| Zewn. 3150×2126 | 6,7 | ~250 | 0,5–1,0 h |
| Wnętrze 3150×2126 z guiding | 6,7 | ~500 | 1,5–3,0 h |
| Fotomatch, region ~3000×2000 z 8k | 6,0 | ~250 | 0,5–1,0 h |

Komplet 8–9 obrazów: ok. 12–20 h CPU → renderować nocą sekwencyjnie, wcześniej drafty 1200 px (≈5–15 min) do akceptacji kompozycji. W razie braku czasu: render w 2/3 rozdzielczości + Lanczos ×1,5 (efektywnie ~130 ppi dla hero — akceptowalne od ~0,7 m).

### 11.4 Niebo, HDRI, roślinność [W]
- Niebo: Multiple Scattering (`air_density` 1, `aerosol_density` 1–2 dla lekkiej mgiełki miejskiej, `ozone_density` 1), `altitude` 120 m (teren) — dla aerial altitude = wysokość kamery.
- HDRI Poly Haven (CC0) do chmur w tle i odbić w ujęciach naziemnych; panoramy M.09 do odbić w okolicy terenu.
- Roślinność proceduralna w Geometry Nodes ([P] dostępne `DistributePointsOnFaces`, `InstanceOnPoints`, `RealizeInstances`); instancje (nie realizować!) — oszczędza RAM.

### 11.5 Wyjścia i zarządzanie kolorem [W]
- Ujęcia zwykłe: AgX → 16-bit PNG; grading w Pythonie.
- Fotomatching: Standard + kompozycja liniowa (sekcja 8.5).
- Jeden profil wyjściowy dla wszystkich: sRGB.

### 11.6 Pułapki wykryte w tej sesji [P]
1. **Domyślna scena modułu bpy** (kostka w (0,0,0)) — renderowała czerń; zawsze `bpy.ops.wm.read_factory_settings(use_empty=True)` (`blib.reset()` to robi — używać).
2. **`blib.sky_and_sun()`**: `sky.sun_rotation = radians(90 − az)` daje niebo z innym kierunkiem słońca niż lampa (np. az 180°: lampa z południa, niebo z zachodu). Poprawnie: `sky.sun_rotation = radians(az)`.
3. **`blib.sky_and_sun()`**: domyślnie `sun_strength = 4`, `sky_strength = 1`, `sun_disc = False` → słońce ~30× za słabe względem nieba (stosunek ~0,15 : 1 zamiast ~4,5 : 1 przy 25°) → płaskie światło bez cieni. Poprawnie: `sun_disc = True` bez lampy albo lampa ≈ 117 W/m² (25°) z kolorem z tabeli 5.2.
4. **`blib.sky_and_sun()`**: `max(el_deg, 0.5)` uniemożliwia niebo zmierzchowe; atrybut `dust_density` nie istnieje w 5.2 (jest `aerosol_density`).
5. Czcionki Inter w systemie to OTF/CFF — ReportLab nie osadza CFF (dotyczy plansz, patrz `plansze_metodyka.md`).

---

## 12. Co mówią badania o percepcji obrazów architektury (i czego nie mówią)

- [F] **Bates-Brkljac (2009)**, *Design Studies* 30(4):415–437, doi:10.1016/j.destud.2008.10.005 — wg omówień wtórnych (abstraktu nie zweryfikowano): obrazy komputerowe oceniane jako dokładniejsze i bardziej realistyczne niż tradycyjne rysunki; różnice percepcji między architektami a nie-architektami. **[W]** Sąd jest mieszany (architekci + Marszałek, Sekretarz) → fotorealizm jest bezpiecznym wyborem dla części nie-architektonicznej, a uczciwość geometrii — dla architektów.
- [F] **Merikoski (2020)**, „Sights beyond Illusions: Towards Commensurable Competition Proposals”, *Nordic Journal of Architectural Research* 32(1):9–32 (pełny tekst przeczytany): retoryka wizualna w obrazach konkursowych jest celowa, ma „uwieść jury” i utrudnia porównanie prac; metoda warstwowego przerysowania kluczowych cech ujawniła iluzje — nawet architekci w jury zrozumieli perswazyjny wpływ obrazów; jury łatwo zawęża grupę najlepszych, trudniej wybiera zwycięzcę.
- [F] **Kazemian & Rönn (2009)**, *Building Research & Information* 37(2):176–186 (cytowane za Merikoski 2020, s. 26; pracy nie czytano): ostateczny wybór zwycięzcy zapada na podstawie reakcji emocjonalnych, po testowaniu prac pytaniami o zgodność z kryteriami.
- [F] **Svensson (2012)**, „Architectural Persuasion: On Quality Assessment in an Architectural Competition”, *NJAR* 24(1) (abstrakt): dyskusje jury oscylują między wizją, rzeczywistym problemem/miejscem i tym, jak projekt będzie wyglądał zbudowany w realnym otoczeniu; decyzja w kontekście emocjonalnym.
- [S] **Lavdas, Salingaros & Sussman (2021)**, *Applied Sciences* 11(13):6197, doi:10.3390/app11136197 (oprogramowanie 3M-VAS przewidujące fiksacje) oraz **Rosas i in. (2023)**, *Applied Sciences* 13(21):12071 (eye-tracking budynków obywatelskich) — wg wyników wyszukiwania (pełnych tekstów nie pobrano, MDPI 403): uwagę przyciągają elementy o wyraźnej strukturze (wejścia, okna, detal), słabo — puste, jednorodne płaszczyzny i powtarzalne szklane elewacje. Istnieje krytyka metody VAS. **[W]** Hipoteza robocza, nie dowód: w kadrze wejście i detal elewacji mają być czytelne; unikać kadrów zdominowanych przez pustą płaszczyznę.
- **Czego brak:** nie znaleziono kontrolowanych badań pokazujących, że konkretny styl renderu (pora dnia, liczba ludzi, kolor) zwiększa szanse w konkursie. Zalecenia z sekcji 3–10 to synteza praktyki i zasad fotografii, nie wynik eksperymentów. „Statystyczna przewaga kadrów pionowych” spotkana w wynikach wyszukiwania (strona wydarzenia „Influence Charrette”) — bez danych, odrzucona.

---

## 13. Lista kontrolna jakości

### 13.1 Każdy obraz
- [ ] Treść zgodna z Regulaminem (nr wizualizacji, wymagany obiekt w kadrze: wejście / Słowackiego 5 / Mazowiecka 19 / hol / hol Sejmiku / sala).
- [ ] Geometria zgodna z rysunkami: liczba kondygnacji, rytm okien, wysokości gzymsów, materiały, wejście w tym samym miejscu co na rzucie parteru (nakładka krawędzi z modelu).
- [ ] Piony pionowe (odchyłka < 0,3°), horyzont poziomy; wysokość kamery 1,5–1,7 m (lub uzasadniony punkt wysoki).
- [ ] Ogniskowa ≥ 24 mm na zewnątrz, ≥ 20 mm we wnętrzu; brak rozciągniętych brzegów.
- [ ] Kierunek słońca zgodny z orientacją i porą (tabela 2.4); w wiz. 1–2 zgodny z cieniami na zdjęciu.
- [ ] Pora roku: koniec października (korony, liście na ziemi, ubiór).
- [ ] Brak pustych czarnych okien; wnętrza za szybami zróżnicowane.
- [ ] Odbicia w szkle pokazują wiarygodne otoczenie (panoramy M.09/HDRI), nie jednolity gradient.
- [ ] Materiały: brak „plastikowej” jednorodności, krawędzie łapią światło, skala tekstur poprawna.
- [ ] Ludzie: skala, cienie, kontakt z podłożem, różnorodność, min. 1 element dostępności (wiz. 3, 6, 7, 8), nikt nie patrzy w obiektyw.
- [ ] Ekspozycja: brak przepaleń poza źródłami światła i słońcem; czernie nie zalane (sprawdzić False Color).
- [ ] Szum po denoisingu niewidoczny w 100%; brak „rozmazanych” tekstur (jeśli są — więcej próbek lub Prefilter Accurate).
- [ ] Grading zgodny z „rodziną” (porównanie obok innych obrazów w jednej siatce).
- [ ] Rozdzielczość ≥ 150 ppi (cel 200) w skali wydruku.
- [ ] Metadane usunięte; nazwy plików neutralne.

### 13.2 Fotomatching (dodatkowo)
- [ ] RMS dopasowania kamery < 3 px; nakładka krawędzi proxy na zdjęcie bez widocznych przesunięć.
- [ ] Cienie od nowego budynku na terenie i sąsiednich budynkach (Shadow Catcher) zgodne kierunkiem i miękkością z cieniami na zdjęciu.
- [ ] Obiekty pierwszego planu (drzewa, latarnie) poprawnie przesłaniają budynek.
- [ ] Biel/czerń/nasycenie/ostrość/ziarno wstawki = sąsiednie budynki na zdjęciu.
- [ ] Poza granicą opracowania: stan obecny, bez zmian (bez hełmów mostu, bez dodatkowej zieleni).

### 13.3 Zestaw
- [ ] 8 wymaganych + ew. 1–2 dodatkowe; każdy obraz pracuje na ≥ 2 kryteria oceny.
- [ ] Jedna pora roku, spójna paleta, jeden typ ziarna, spójne proporcje kadrów z siatką planszy.
- [ ] Wydruk próbny 1:1 fragmentów i całej planszy w A3: kolory i cienie czytelne (wydruk ciemnieje — w razie potrzeby podnieść cienie o 0,1–0,2 EV dla wersji do druku).

---

## 14. Ryzyka i kwestie otwarte

1. **Geometria zdjęć F.17** (skorygowane piony, upscaling, możliwy rzut panoramiczny) — dopasowanie może wymagać modelu z przesunięciem punktu głównego lub lokalnego dopasowania; zarezerwować czas.
2. **Godzina zdjęć** — założono zegar drona w czasie lokalnym CET (po zmianie czasu 26.10.2025); przy CEST azymut byłby ~165° → weryfikacja na cieniach obowiązkowa.
3. **Orientacja elewacji** (pierzeja od Odry ≈ północna) — do potwierdzenia na M.02; od niej zależy dobór pory dnia dla wiz. 3–5.
4. **Wysokość panoram M.09 względem terenu** (30/40/45 m — od czego liczone?) — przyjąć do widoków z sali Sejmiku najbliższą wysokości oka w sali; sprawdzić linię horyzontu.
5. **Czas renderu** na 4 rdzeniach CPU — szacunki ±50%; pierwsze finalne ujęcie zmierzyć i zaktualizować harmonogram.
6. **Licencje sztafażu** (ludzie, drzewa) — używać CC0 (Poly Haven, MPFB/MakeHuman — sprawdzić LICENSE) lub własnych modeli.
7. **Błędy w `blib.py`** (sekcja 11.6) — do poprawienia przed jakimkolwiek finalnym renderem.

---

## 15. Źródła (dostęp: 2026-11-16)

**Materiały Organizatora (lokalnie, `/home/user/aihouse/umwd/00_materialy/`)**
- Regulamin Konkursu SARP nr 1089, tekst jednolity 13.02.2026 — `tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt` (rozdz. VII ust. 2–3, rozdz. VIII ust. 1).
- Wyjaśnienia treści Regulaminu nr 08 (odp. 42, 43, 55), nr 09 (odp. 61), nr 14 (odp. 67), nr 20 (odp. 76), nr 21 (odp. 79–82) — `tekst/1089_Wyjasnienia_tresci_Regulaminu_nr_XX-sig.txt`.
- M.01 Program użytkowy (zatwierdzony 11.2025) — `tekst/Program_użytkowy_budynku_administracyjnego_UWMD_zatwierdzony_11_2025.txt`.
- F.17.A, F.17.B — `_rozpak/3.Zalaczniki_Formalne_F.01-F.17_PDF/F.17.*.jpg` (EXIF/XMP odczytane PIL).
- M.09 panoramy 360° — `_rozpak/5_.../M.09. ZDJĘCIA 360 ST/`; M.10 zdjęcia otoczenia; M.02 drzewa i NMT; M.04 mapa schematyczna; M.06 operat dendrologiczny.

**Dokumentacja oficjalna oprogramowania**
- Blender Manual (latest/5.3): Object → Visibility (Shadow Catcher, Ray Visibility) — https://docs.blender.org/manual/en/latest/render/cycles/object_settings/object_data.html
- Blender Manual: Render Passes (Shadow Catcher, Mist, Denoising Data) — https://docs.blender.org/manual/en/latest/render/layers/passes.html
- Blender Manual: Cycles Sampling (adaptive, denoising, path guiding, light tree) — https://docs.blender.org/manual/en/latest/render/cycles/render_settings/sampling.html
- Blender Manual: Displays and Views (AgX, Standard, False Color, Looks, Exposure) — https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html
- Blender Manual: Sky Texture Node — https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/sky.html
- Blender Manual: Cameras (Shift, Sensor Fit) — https://docs.blender.org/manual/en/latest/render/cameras.html
- Blender Manual: Principled BSDF (Thin Wall) — https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/principled.html
- Blender Manual: Cycles Film (Transparent Glass) — https://docs.blender.org/manual/en/latest/render/cycles/render_settings/film.html
- bpy 5.2.4 LTS — introspekcja właściwości i testy renderów w tej sesji ([P]).
- fSpy — https://fspy.io/ oraz https://fspy.io/tutorial/ ; importer: https://github.com/stuffmatic/fSpy-Blender
- Poly Haven License (CC0) — https://polyhaven.com/license
- Physically Based (baza parametrów materiałów, API) — https://api.physicallybased.info/materials
- MakeHuman — licencja: https://static.makehumancommunity.org/about/license.html ; MPFB: https://extensions.blender.org/add-ons/mpfb/ (informacje z wyników wyszukiwania, do weryfikacji)
- timeanddate.com: Blue hour — https://www.timeanddate.com/astronomy/blue-hour.html ; Golden hour — https://www.timeanddate.com/astronomy/golden-hour.html

**Publikacje naukowe**
- Legge, G. E., & Bigelow, C. A. (2011). Does print size matter for reading? A review of findings from vision science and typography. *Journal of Vision*, 11(5):8, 1–22. doi:10.1167/11.5.8 (abstrakt i wstęp przeczytane) — wykorzystane w `plansze_metodyka.md`.
- Merikoski, T. (2020). Sights beyond Illusions: Towards Commensurable Competition Proposals. *Nordic Journal of Architectural Research*, 32(1), 9–32. https://acris.aalto.fi/ws/portalfiles/portal/43329614/1188_655138_1_PB.pdf (pełny tekst).
- Svensson, C. (2012). Architectural Persuasion: On Quality Assessment in an Architectural Competition. *Nordic Journal of Architectural Research*, 24(1). https://arkitekturforskning.net/na/article/view/20 (abstrakt).
- Kazemian, R., & Rönn, M. (2009). Finnish architectural competitions: structure, criteria and judgement process. *Building Research & Information*, 37(2), 176–186 (cyt. wtórnie za Merikoski 2020).
- Bates-Brkljac, N. (2009). Assessing perceived credibility of traditional and computer generated architectural representations. *Design Studies*, 30(4), 415–437. doi:10.1016/j.destud.2008.10.005 (ustalenia wg źródeł wtórnych).
- Vishwanath, D., Girshick, A. R., & Banks, M. S. (2005). Why pictures look right when viewed from the wrong place. *Nature Neuroscience*, 8(10), 1401–1410 (abstrakt/omówienia).
- Lavdas, A. A., Salingaros, N. A., & Sussman, A. (2021). Visual Attention Software: A New Tool for Understanding the “Subliminal” Experience of the Built Environment. *Applied Sciences*, 11(13), 6197. doi:10.3390/app11136197 (wg wyników wyszukiwania).
- Rosas, H. J., Sussman, A., Sekely, A. C., & Lavdas, A. A. (2023). Using Eye Tracking to Reveal Responses to the Built Environment and Its Constituents. *Applied Sciences*, 13(21), 12071 (wg wyników wyszukiwania; strona MDPI 403).

**Źródła wtórne / praktyka (oznaczone [S])**
- Hogrefe, A. „7 Rules for Composing Powerful Architectural Perspectives”, Architizer Journal — https://architizer.com/blog/practice/tools/the-art-of-rendering-perspectives/
- Rode, L. „Photographic Approach in Architectural Visualization”, ronenbekerman.com, 26.03.2013 — https://www.ronenbekerman.com/photographic-approach-in-architectural-visualisation/
- D5 Render, „Camera setting tips must known for archviz” — https://d5render.com/posts/camera-setting-tips-must-known-for-archviz (wg wyników wyszukiwania)
- Gizmodo, „The Secret Lives of the Tiny People In Architectural Renderings” — https://gizmodo.com/the-secret-lives-of-the-tiny-people-in-architectural-re-1660746735 ; Dezeen (403) — https://www.dezeen.com/?p=1256413 ; Iconeye — https://www.iconeye.com/opinion/architectural-visualisations-representative-diverse-populations (wg wyników wyszukiwania)
- Designboom, wywiad z MIR (2021): „we think of our images more like emotions than stories” — https://www.designboom.com/architecture/visualization-studio-mir-interview-trond-greve-andersen-mats-andersen-06-02-2021/ (wg wyników wyszukiwania)
- Chaos, „Composition and camera tips for a beautiful render” (R. Eloy, 2025) — przekierowanie, treści nie uzyskano.
