# Rdzeń modelu i pipeline 3D — `src/lamela`

Jedno źródło prawdy: `model/budynek.yaml` + `model/dzialka.yaml` (kontrakt: `docs/SCHEMAT_MODELU.md`).
Z modelu powstają: walidacja, geometria pochodna (warstwy ścian, pomieszczenia, wskaźniki), reprezentacja pośrednia
(IR — pryzmy), model 3D (glTF/OBJ), rendery i podgląd www. Uruchamianie zawsze z `PYTHONPATH=src`.

| Moduł | Zawartość |
|---|---|
| `lamela/model.py` | wczytanie YAML, walidacja zgodności ze schematem, geometria pochodna, API zapytań, wskaźniki PN-ISO 9836 |
| `lamela/ir.py` | IR: `Prism`, `Mesh`, `TerrainMesh`, `IR`; `build_ir(model)` — cały budynek + działka |
| `lamela/model3d/` | `export_glb`, `export_obj` (trimesh), materiały PBR (`materials.py`), tekstury proceduralne (`textures.py`) |
| `lamela/sun.py` | położenie Słońca (NOAA/Meeus) dla Poznania, czas Europe/Warsaw |
| `lamela/pipeline.py` | CLI: walidacja → wskaźniki → IR → glTF/OBJ → rendery → www |
| `tools/render3d/` | renderer three.js (headless Chromium, Playwright): `render.py`, `render.html`, `render.js` |
| `www/model3d/index.html` | interaktywny podgląd (three.js z CDN) |
| `tools/test_pipeline.py` | test automatyczny na modelu `model/test/*.yaml` |

## Polecenia

```bash
# walidacja + zestawienie powierzchni (tekst)
PYTHONPATH=src python3 -m lamela.model model/budynek.yaml model/dzialka.yaml

# pełny pipeline (rendery 2400×1500, kopia modelu do podglądu www)
PYTHONPATH=src python3 -m lamela.pipeline --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
    --out projekt/07_model_3D/wstepne --www www/model3d
#   opcje: --views abcdefg  --size 2400x1500  --bez-renderow  --strict  --nazwa dom_lamela

# same rendery z gotowego .glb
PYTHONPATH=src python3 tools/render3d/render.py --glb plik.glb --out katalog [--views ace] [--size 2400x1500]

# test automatyczny (pełny ok. 3–4 min; --szybko bez przeglądarki ok. 10 s)
PYTHONPATH=src python3 tools/test_pipeline.py [--szybko] [--pelne-rendery]

# jednorazowo: biblioteki renderera
cd tools/render3d && npm install          # three, n8ao, postprocessing → node_modules (ignorowane przez git)
```

## `model.py` — API

```python
from lamela.model import load_model
m = load_model("model/budynek.yaml", "model/dzialka.yaml", strict=True)   # ModelValidationError przy BŁĘDACH
m.problemy / m.bledy / m.ostrzezenia / m.raport_walidacji()              # Problem(poziom, miejsce, opis)
m.kondygnacje, m.kondygnacja("P1"), m.materialy, m.material("SIL18"), m.przegroda("SZ1")
m.sciany("P0"), m.sciana("S0-01"), m.otwory(sciana="S0-01"), m.otwory(kond="P1"), m.otwor("O0-01")
m.pomieszczenia("P0"), m.pomieszczenie("0.01")
m.stropy(), m.dachy(), m.wsporniki(), m.slupy(), m.belki(), m.fundamenty(), m.schody(), m.balustrady(),
m.lamele(), m.tarasy(), m.plyty()                                         # surowe słowniki / płyty z rzędnymi
m.wolna_przestrzen("P0")          # zamknięte obszary między licami ścian wykończonych (shapely)
m.obrys_kondygnacji("P0", lico="zewn"|"konstr")
m.pow_zabudowy()                  # {"budynek", "z_plytami", "wielobok"}
m.kubatura_brutto()               # {"razem", "skladniki"}
m.zestawienie_powierzchni()       # wiersze pomieszczeń + sumy kategorii (PU = podstawowa + pomocnicza)
m.pow_brutto_kondygnacji(), m.kond_poziomu(z), m.kond_z_od("P1"), m.bbox()
m.dz                              # Dzialka: do_budynku(xy), do_dzialki(xy), obrys, teren_punkty(), z_wzgl(H)
```

**Sciana**: `p1, p2, L, u, n` (wersor osi i normalna lewa), `pt(s, t)`, `st(p)`, `warstwy` (lista
`WarstwaSciany`: `mat, d, t0, t1, konstrukcyjna, strona, ranga, klasa, polygon, z0, z1`), `polygon` (suma warstw),
`z_od, z_do` (rozwiązane `null`), `ext_side`, `face_t(side, "k"|"all")`, `polaczenia` (`{0|1: {"typ": L|T|ciagla|wezel|wolny, "z": [id…]}}`), `otwory`.

**Otwor**: `s0, s1` (wzdłuż osi od punktu 1), `z0, z1` (rzędne względne), `p0, p1, srodek` (punkty na osi, układ
globalny), `kierunek_zewn`, `oscieze` (zakres t przez całą grubość), `footprint` (rzut), `narozniki_3d(t)`,
`rama_t` (położenie ramy w grubości ściany).

**Pomieszczenie**: `polygon` (z lic wykończonych), `polygon_podlogi` (minus otwory stropu pod pomieszczeniem),
`pow_netto`, `obwod`, `wysokosc` (spód płyty nad pomieszczeniem − wykończenie sufitu − rzędna), `wsp_wysokosci`,
`pow_zaliczona`, `kubatura_netto`, `zrodlo` (`punkt` | `wielobok`).

### Walidacja
Poziomy: **BLAD** (model niespójny — `strict=True` przerywa), **OSTRZEZENIE**, **INFO** (np. pole spoza schematu).
Sprawdzane m.in.: wymagane sekcje i pola wraz z typami (lista pól w `F` w `model.py`), unikalność i konwencja
identyfikatorów, identyfikatory pomieszczeń zapisane jako liczby (YAML gubi końcowe zera), odwołania
(kondygnacje, przegrody, materiały warstw, ściany otworów, przegrody podłóg/dachów/wsporników, materiały słupów/belek/lamel),
typ przegrody ściany, jedna warstwa konstrukcyjna, zerowe osie, nakładające się osie ścian współliniowych,
**otwory poza ścianą (w poziomie i w pionie)**, **nakładające się otwory**, otwór w strefie węzła ściany dochodzącej,
orientacja CCW i poprawność wieloboków, otwory stropów w obrysie, spójność schodów (suma stopni, h·n = Δrzędnych),
lamele (rozstaw > b), spójność rzędnych (wierzch stropu + podłoga = rzędna; `wys_w_swietle` vs wyliczona),
pomieszczenia niezamknięte, punkt w ścianie, nakładające się pomieszczenia, **nakładające się płyty** (strop/dach/wspornik
w tym samym zakresie z — zdublowana geometria), działka (obrys, pole, punkty terenu), **budynek w granicach działki**.

### Konwencje geometryczne (ustalone w rdzeniu — uzupełniają schemat)
* **Warstwy ściany**: kolejność w przegrodzie od wnętrza do zewnątrz; oś = środek warstwy konstrukcyjnej;
  `wnetrze: lewa|prawa` — strona wnętrza względem kierunku p1→p2; `srodek` — pierwsza warstwa po lewej.
  Brak warstwy `konstrukcyjna: true` → najgrubsza (ostrzeżenie).
* **Łączenie naroży** (na kondygnacji, ściany o nakładających się zakresach z):
  * **L** (końce osi w jednym punkcie lub osie przesunięte, ale końce leżą w sobie nawzajem): warstwa konstrukcyjna
    łączona doczołowo — ściana o wyższym priorytecie (grubsza konstrukcja → typ zewn. > nośna > działowa → dłuższa)
    przechodzi do zewnętrznego lica konstrukcji drugiej; pozostałe warstwy ścinane po **dwusiecznej** (izolacja z izolacją,
    tynk z tynkiem). Gdy strony zewnętrzne są niezgodne (np. ściana zewn. z działową) — połączenie doczołowe wszystkich warstw.
  * **T** (koniec osi wewnątrz grubości innej ściany, także gdy oś kończy się na licu): konstrukcja dochodzi do lica
    konstrukcji ściany przelotowej, pozostałe warstwy — do jej lica wykończonego; tynk ściany przelotowej jest przerywany.
  * **ciągła** (współliniowe) — cięcie prostopadłe; **węzeł** ≥3 ścian — para współliniowa przechodzi, reszta jak T;
    **X** (osie krzyżujące się we wnętrzach) — rozstrzyga porządkowanie.
  * Porządkowanie końcowe: warstwy konstrukcyjne → przyległe → dalsze; każda kolejna minus zajęte (brak zakładek);
    współrzędne przyciągane do siatki 1 µm (brak szczelin numerycznych). Test: suma pól = pole sumy, brak otworów < 0,3 m².
* **Rzędne ścian** `null`: `z_od` = wierzch płyty konstrukcyjnej pod kondygnacją (strop `nad` = kondygnacja niższa; dla
  najniższej: rzędna − warstwy podłogi nad warstwą konstrukcyjną), `z_do` = spód najniższej płyty (strop kondygnacji, dach,
  wspornik) nad osią ściany.
* **Warstwy zewnętrzne ścian zewnętrznych** (ETICS) przedłużane: w górę na czoło płyty, gdy krawędź płyty jest w licu
  ściany (do wierzchu płyty stropu, do wierzchu attyki dachu); przy płycie wysuniętej (okap) — bez przedłużenia;
  najniższa kondygnacja — 0,30 m w dół (strefa cokołu); ściana stojąca na krawędzi wspornika bez ściany pod spodem — w dół
  do spodu płyty.
* **Pomieszczenia**: wolna przestrzeń kondygnacji = obwiednia minus suma warstw ścian (bez otworów) i słupów; obszar
  zamknięty zawierający `punkt`. Jawny `wielobok` jest **przycinany do lic wykończonych** (można go podać w osiach).
  Wysokość = spód płyty nad pomieszczeniem − wykończenie sufitu (kod materiału: 1 cm; kod przegrody: jej grubość; dach:
  warstwy pod konstrukcją) − rzędna. Opcjonalne pole `wys` pomieszczenia nadpisuje wysokość.
* **PN-ISO 9836:2015**: powierzchnia netto z lic wykończonych, bez otworów w stropie (> klatka schodowa liczona na
  kondygnacji dolnej); współczynnik wysokości 100 % (h ≥ 2,20 m), 50 % (1,40–2,20 m), 0 % (< 1,40 m) — zasada zaliczania
  z praktyki krajowej **[do potwierdzenia w rejestrze wymagań]**; kategorie: podstawowa, pomocnicza, ruchu, techniczna.
  **Powierzchnia zabudowy** — suma rzutów obrysów zewnętrznych kondygnacji (wspornikowe bryły wyższych kondygnacji
  wliczone; płyty/daszki/okapy nie) + wariant informacyjny z płytami. **Kubatura brutto** — przestrzenie kondygnacji
  (obrys zewn. × od wierzchu płyty do spodu płyty) + płyty stropów/dachów w obrysie (z warstwami dachu, bez attyk) +
  warstwa konstrukcyjna podłogi na gruncie.
* **Schody**: `start` = środek krawędzi pierwszego podnóżka (oś biegu), `kierunek` = kierunek wchodzenia, `stopni` =
  liczba podnóżków biegu (liczba stopni = podnóżki − 1; ostatni podnóżek wchodzi na spocznik/strop). Kolejny bieg zaczyna
  się na rzędnej końca poprzedniego.
* **Lamele**: `linia` — lico elewacji; lamele (b wzdłuż linii × h w poprzek) odsunięte o `odsuniecie` ku stronie
  `elewacja` (S/N/E/W/SE/…), wycentrowane na linii z rozstawem osiowym `rozstaw`; + 2 rygle stalowe.
* **Stolarka**: rama przy licu zewn. warstwy konstrukcyjnej (5 cm w głąb, 4 cm w izolacji), kwatery automatyczne
  (okno ≤ 1,6 m, fix/HS ≤ 3,0 m; HS min. 2) lub opcjonalne pole `kwatery` otworu; parapety zewn. i wewn., okładziny ościeży.
* **Płyty w 3D**: spód części płyty wysuniętej poza obrys kondygnacji niżej dostaje podsufitkę (tynk elewacyjny);
  attyka biegnie po krawędzi obrysu dachu (oprócz odcinków przy ścianach wyższych kondygnacji) z okładziną i obróbką.
  Dach na poziomie stropu wyższej kondygnacji (np. dach garażu) należy do grupy tej kondygnacji; dach nad najwyższą
  kondygnacją — do grupy `dach`. Stropy należą do grupy kondygnacji, której są podłogą.
* **Działka**: współrzędne `dzialka.yaml` w układzie działki; `uklad.przesuniecie/obrot` = transformacja budynek → działka
  (`p_d = R·p_b + t`). Rzędne terenu `H` bezwzględne → względne `H − zero_abs`.

### Rozszerzenia opcjonalne (poza schematem; rdzeń je rozpoznaje, schemat ich nie wymaga)
`otwory[].kwatery` (liczba kwater), `pomieszczenia[].wys` (wysokość w świetle), `stropy[].mat`, `dachy[].mat`,
`dachy[].otwory`, `wsporniki_plyty[].mat`, `wsporniki_plyty[].attyka`, `schody[].mat`, `tarasy[].grubosc`,
`materialy[].pbr` (`kolor, szorstkosc, metal, alpha, tekstura, uv` — wygląd 3D), `sasiedzi[].wys`, `sasiedzi[].dach: plaski`,
`drzewa[].wys`, `zielen[].wys`, `bramy[].kierunek`, `bramy[].wys`, `miejsca_postojowe[].auto: false`.
Fundament: element z `obrys` (+`h`, `spod`) = płyta; z `os` = ława/stopa.

## `ir.py` — reprezentacja pośrednia

```python
from lamela.ir import build_ir, Prism, Mesh, TerrainMesh
ir = build_ir(m, otoczenie=True, auta=True, ramy=True)
ir.prisms / ir.meshes / ir.terrain / ir.meta
ir.summary(), ir.by_kind("glass"), ir.by_level("P1"), ir.by_group("dach"), ir.element("S0-01"), ir.bounds(),
ir.section(z)          # przekrój poziomy: [(pryzma, wielobok)]
ir.terrain.height_at(x, y)
```
`Prism(id, kind, polygon, z0, z1, material, level, meta, holes)` — `id` = element + `#n`; `meta`: `group` (P0/P1/…,
dach, fundamenty, otoczenie), `layer`, `wall`, `opening`, `part` (pelna/filar/podokienny/nadproze/miedzy, oscieze_*,
plyta, posadzka, sufit, pokrycie, attyka, obrobka, …), `klasa`, `room`.
Rodzaje (`kind`): wall, insulation, slab, roof, parapet (attyki, obróbki), column, beam, footing (ławy, stopy, ściany
fundamentowe), stair_step, landing, railing, lamella, frame, glass, door_leaf, canopy, terrace, pavement, fence, road,
vegetation, context (budynki sąsiednie), vehicle. `Mesh` — bryły trójkątowe (korony drzew, auta, dachy sąsiadów).
`TerrainMesh` — Delaunay (scipy) z punktów wysokościowych + zagęszczenia 1 m (działka) / 5 m (otoczenie), wycięcie pod
obrysem parteru; poza otoczką punktów — płaszczyzna trendu dopasowana w sposób ciągły.

## `model3d` — glTF / OBJ
`export_glb(ir, "x.glb", model=m)` — trimesh; oś Y w górę (X = x, Y = z, Z = −y). Hierarchia węzłów:
`LAMELA / budynek / {fundamenty, P0, P1, …, dach}`, `LAMELA / teren`, `LAMELA / otoczenie`; węzeł elementu (np. `S0-01`)
z siatkami per materiał (`S0-01|SIL18`). `extras` węzłów: `id, rola, group, kind, material, castShadow`; `extras`
sceny: metadane IR (kondygnacje, pomieszczenia, działka). Materiały PBR z `materials.py` (szkło — BLEND, alfa 0,26;
tekstury proceduralne: drewno, deski, parkiet, trawa, kostka, płyty, asfalt, beton, tynk, liście, sedum).
`export_obj(ir, "x.obj", model=m)` → `.obj + .mtl + tekstury`.

Warstwy-pustki (kod/nazwa: PUSTKA, SZCZELINA, POWIETRZE, AIR) są w IR (przekroje), ale nie trafiają do glTF/OBJ.

## Podgląd www (`www/model3d/`)
`index.html` + `model.glb` (kopiowany przez `lamela.pipeline --www www/model3d`); three.js 0.186.1 z cdn.jsdelivr.net.
Działa z dowolnego serwera plików statycznych (np. `python3 -m http.server` w katalogu repozytorium →
`http://localhost:8000/www/model3d/`); inny model: `index.html?model=ścieżka.glb`. Otwarty z dysku (file://)
przeglądarka blokuje pobranie .glb — strona pokazuje wtedy wybór pliku / upuszczenie pliku.
Funkcje: OrbitControls, przełączniki grup (fundamenty, P0…Pn, dach, teren, otoczenie), widoki (ogród, ulica, lotniczy,
z góry), rozsunięcie kondygnacji, przekrój płaszczyzną (pozioma / pionowa W–E / N–S, suwak, odwrócenie), dzień/wieczór
(światła pomieszczeń z metadanych, świecące szyby), cienie, identyfikacja elementu po kliknięciu (id, materiał, rzędna),
układ responsywny (telefon: panel dolny, zwijany).

## Rendery (`tools/render3d`)
Widoki (PNG 2400×1500, render 2× + Lanczos): a) lotniczy SE (21.03 12:00), b) lotniczy SW (21.06 15:00), c) poziom oczu
z ogrodu — elewacja płd. (21.06 15:00, obiektyw przesuwny), d) od ulicy (21.06 19:30), e) aksonometria rozwarstwiona
kondygnacji z podpisami, f) elewacja płd. ortogonalna (pas terenu), g) nasłonecznienie 3×3 (21.03/21.06/21.12 × 9/12/15).
Oświetlenie: DirectionalLight z pozycją Słońca (`lamela.sun`), HemisphereLight, środowisko PMREM z nieba gradientowego,
cienie PCF soft 4096², N8AO (SSAO), ACES + sRGB, mgła. Parametry każdego renderu: `rendery.json`.

## Znane ograniczenia
* Ściany tylko prostoliniowe (oś = 2 punkty); ściany łukowe — do rozbicia na odcinki.
* Dachy wyłącznie płaskie (spadek zapisany, geometria pozioma); attyka pomijana wzdłuż ścian wyższych kondygnacji.
* Otwory prostokątne; brak nadproży/wieńców jako osobnych elementów (N/W w belkach — jeśli podane).
* Schody proste (biegi prostoliniowe + spoczniki); balustrady pochyłe aproksymowane schodkowo (pryzmy).
* Przekroje w podglądzie www bez „zaślepek” (widoczne wnętrza brył).
* Otoczenie: drzewa, auta i budynki sąsiednie — bryły uproszczone; teren bez skarp/murów oporowych (TIN z punktów).
* Rendery programowe (SwiftShader, CPU): komplet 7 widoków 2400×1500 + siatka nasłonecznienia ≈ 9–10 min.
* Test podglądu www podmienia w przeglądarce testowej adresy CDN na lokalne `node_modules/three` (ta sama wersja) —
  sandbox nie ufa CA proxy; adresy CDN sprawdzane osobno (HTTP 200).
* Współczynniki wysokości PN-ISO 9836 — do potwierdzenia w rejestrze wymagań; kubatura/zabudowa — interpretacja
  opisana wyżej (MPZP może definiować inaczej).
