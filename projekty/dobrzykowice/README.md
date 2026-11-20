# Bliźniak — Dobrzykowice, dz. 341/318 (koncepcja): rzuty w standardzie aihouse

Przerysowanie rzutów z pliku **`Projekt_wersja_15_10_2026.dwg`** (koncepcja z 15.10.2026, AutoCAD, rysunek w cm,
z archiwum `projekt_Dobrzykowice_15_10_2026.zip`) do modelu `budynek.yaml` i wygenerowanie arkuszy silnikiem
`lamela.views` — tym samym, który rysuje komplet „Domu LAMELA” w tym repozytorium.

| Plik | Zawartość |
|---|---|
| `rysunki/PK-AR-01_rzut_parteru.{dwg,pdf,png,dxf}` | rzut parteru 1:50, arkusz 420×700 |
| `rysunki/PK-AR-02_rzut_pietra.{dwg,pdf,png,dxf}` | rzut piętra 1:50, arkusz 420×700 |
| `rysunki/tom_widoki.pdf` | tom ze spisem rysunków; `raport_widokow.json` — raport QA silnika |
| `model/budynek.yaml`, `model/wyposazenie.yaml` | **generowane** przez `narzedzia/buduj_model.py` (nie edytować ręcznie) |
| `model/arkusze.yaml` | układ arkuszy, tabliczka, uwagi |
| `narzedzia/buduj_model.py` | geometria lokalu 1 z DWG + odbicie lustrzane na lokal 2, dobór otwierania drzwi |
| `narzedzia/kontrola_zgodnosci.py` | porównanie linii ścian DWG z licami ścian modelu |

Plików źródłowych (DWG, zrzut JSON) nie ma w repozytorium — plik PZT z tego samego archiwum zawiera w ukrytych
warstwach dane osobowe z EGiB.

## Regeneracja
```bash
PYTHONPATH=src python3 projekty/dobrzykowice/narzedzia/buduj_model.py
PYTHONPATH=src python3 tools/generuj_widoki.py --budynek projekty/dobrzykowice/model/budynek.yaml \
    --arkusze projekty/dobrzykowice/model/arkusze.yaml --wyposazenie projekty/dobrzykowice/model/wyposazenie.yaml \
    --out projekty/dobrzykowice/rysunki
```

### DWG
Pliki `*.dwg` (format AutoCAD 2018, AC1032) powstają z arkuszy DXF darmowym **ODA File Converter 27.10**
(Open Design Alliance) z audytem: `narzedzia/eksport_dwg.sh <katalog_ODAFileConverter>`.
Przestrzeń modelu w **metrach** (`$INSUNITS = 6`; DWG źródłowy był w cm), arkusz „Arkusz PK-AR-0x” w przestrzeni papieru
z rzutnią 1:50, ramką, tabliczką, legendami i zestawieniem; warstwy w standardzie aihouse (`A-SCIANY-KONSTR`,
`A-SCIANY-IZOL`, `A-SCIANY-DZIAL`, `A-DRZWI`, `A-OKNA`, `A-SCHODY`, `A-MEBLE`, `A-SANITARNE`, `A-WYMIARY`, `A-OSIE`,
`A-OPISY`, `A-POMIESZCZENIA`, `R-RAMKA`, `R-TABLICZKA` …).
Kontrola (20.11.2026): konwersja zwrotna DWG → DXF daje identyczne liczby obiektów modelu według typu i warstwy
(parter 3037, piętro 3658), identyczne teksty (377 / 447) i zasięg; niezależny odczyt LibreDWG — 0 nieznanych encji.

## Metoda
* Odczyt DWG: LibreDWG (build WASM `@mlightcad/libredwg-web` 0.8.4) → JSON; współrzędne linii ścian, bloków drzwi,
  mebli i elewacji (wysokości okien).
* Układ modelu (konwencja `docs/SCHEMAT_MODELU.md`): oś A = oś ściany frontowej, oś 1 = oś szczytu lokalu 1;
  `X = (x − 3216,2)/100` (rzut piętra), `X = (x − 1914,3)/100` (rzut parteru), `Y = (y − 4098,1)/100`.
* Rzuty w DWG są lustrzane względem osi podwójnej ściany wspólnej (pozycje drzwi zgodne co do milimetra), więc lokal 1
  jest zdefiniowany jawnie, a lokal 2 = odbicie `Y' = 17,730 − Y` (pomieszczenia x.0y → x.1y).
* Drzwi: zawias i strona otwierania odczytane z bloków drzwi w DWG; pola `strona`/`kierunek` dobrane przez emulację
  `plan._swing_side` i `plan._hinge`, tak aby generator narysował je jak w oryginale.
* Orientacja: azymut osi +Y = 150,9° — z mapy do celów projektowych (front z wejściami na NE, do drogi na dz. 341/305).

## Przyjęcia (w DWG brak opisów — do weryfikacji przez projektanta)
* Materiały: mur 24 cm i ścianki 12 cm jako silikat, ocieplenie 20 cm EPS; grubości warstw zgodne z DWG
  (24 + 20 cm, ściana między lokalami 2 × 24 cm), tynki pominięte, żeby wymiary zgadzały się z oryginałem.
* Funkcje pomieszczeń przyjęte z wyposażenia; pomieszczenie 3,62 × 5,60 m z otworem 2,60 m od posadzki — **garaż**
  (zgodnie z bramą 270 × 226 cm na elewacji frontowej K06).
* Wysokości: kondygnacje 3,06 / 2,79 m, w świetle 2,70 / 2,55 m, schody 17 × 18 × 26 cm (z przekroju);
  okna piętra parapet 0,85 / wys. 1,40 m (elewacja tylna), okno kuchni 1,03 / 1,33 m, przeszklenia parteru 2,39 m.
* Rzędna ±0,000 = 121,30 m n.p.m. — orientacyjnie (teren ok. 121,1 m wg mapy PZK-GZ.430.7408.2025).
* Dodane (brak w DWG): drzwi do garażu i do pom. gospodarczego, balustrady otworu schodowego na piętrze.
* Pominięte: szacht instalacyjny 0,70 × 0,20 m przy szczycie, okrągły element ø 1,2 m w holu piętra.
* Kanały wentylacyjne i komin — jako bryły (`slupy`) przez obie kondygnacje.

## Ograniczenia
* Bez rzutu dachu, przekrojów i elewacji: silnik obsługuje tylko dachy płaskie budynku (dach w DWG — dwuspadowy ≈ 30°).
  Dla tego zestawu dodano do silnika opcję `przekroje_na_rzutach` (domyślnie `true`), żeby rzuty nie miały śladów
  nieistniejących przekrojów.
* Walidacja modelu: 0 błędów; ostrzeżenia — filary przy wnękach wejściowych (celowo ściana symetryczna 20 + 24 + 20 cm)
  oraz drzwi do garażu przy węźle ściany (kontrola przyjmuje strefę ±0,32 m; faktyczne lico jest 0,11 m od otworu).

## Kontrola zgodności z DWG (20.11.2026, tolerancja ±1,5 cm)
| | Linie ścian DWG w obrębie ścian modelu | Lica ścian modelu na liniach DWG |
|---|---|---|
| Parter | 159,9 z 174,4 m (91,7 %) | 88,0 z 90,1 m (97,7 %) |
| Piętro | 186,7 z 205,7 m (90,8 %) | 115,9 z 116,1 m (99,9 %) |

Reszta linii DWG to elementy nieścienne: biegi i krawędź otworu schodowego (rysowane symbolem silnika), pominięty
szacht, symbol bramy, znacznik pod rzutem. Reszta lic modelu: węgarki w ociepleniu przy oknach (DWG ich nie rysuje)
i krótkie odcinki muru przy dodanych drzwiach.
