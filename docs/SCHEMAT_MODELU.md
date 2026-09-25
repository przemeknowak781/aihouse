# Schemat modelu budynku (jedno źródło prawdy)

Pliki: `model/budynek.yaml` (budynek), `model/dzialka.yaml` (działka, teren, zagospodarowanie).
Pakiet Pythona: `src/lamela/` — `model.py` (wczytanie + walidacja + geometria pochodna), `ir.py` (reprezentacja pośrednia brył).

## 1. Konwencje
* Jednostki: metry (m), stopnie; kąty dodatnie przeciwnie do ruchu wskazówek zegara.
* Układ współrzędnych budynku: **x → wschód, y → północ, z → góra**. Początek: przecięcie osi konstrukcyjnych **A** i **1**
  (oś A = najbardziej zachodnia oś nośna bryły głównej, oś 1 = najbardziej południowa). Rzędne `z` względne: **±0,00 = posadzka
  wykończona parteru**; rzędna bezwzględna ±0,00 w `budynek.yaml: uklad.zero_abs` (m n.p.m., PL-EVRF2007-NH).
* Osie konstrukcyjne przechodzą przez **środek warstwy konstrukcyjnej** ścian nośnych.
* Wieloboki: listy `[x, y]`, obieg przeciwny do ruchu wskazówek zegara (CCW), bez powtórzenia pierwszego punktu.
* Identyfikatory: kondygnacje `P0, P1, P2`; ściany `S<kond>-<nr>` (np. `S0-07`); otwory `O<kond>-<nr>`; pomieszczenia `<kond>.<nr>`
  (np. `0.05`); stropy `ST<n>`; dachy `D<n>`; słupy `SL<n>`; belki/podciągi `B<n>`, nadproża `N<n>`, wieńce `W<n>`; schody `SCH<n>`.

## 2. `budynek.yaml` — sekcje
```yaml
meta: {nazwa: "Dom LAMELA", wersja: "1.0", data: "2026-09-25"}
uklad: {zero_abs: 101.65, azymut_osi_y: 0.0}   # azymut osi +y względem północy geogr. (0 = +y na N)
osie:
  x: {A: 0.00, B: 3.90, ...}      # nazwa osi → współrzędna x
  y: {"1": 0.00, "2": 4.80, ...}  # nazwa osi → współrzędna y
kondygnacje:
  - {id: P0, nazwa: Parter, rzedna: 0.00, wys_kondygnacji: 3.15, wys_w_swietle: 2.80, podloga: POD-0}
materialy:        # kod → parametry fizyczne i graficzne
  SIL18: {nazwa: "Bloczek wapienno-piaskowy 18 cm, kl. 20", lambda: 0.77, rho: 1800, cp: 840, mu: 15,
          kreskowanie: MUR_SILIKAT, kolor: "#d9d4ca"}
przegrody:        # kod → układ warstw
  SZ1:
    nazwa: "Ściana zewnętrzna nośna, ETICS"
    typ: sciana_zewn          # sciana_zewn | sciana_wewn_nosna | scianka_dzialowa | strop | stropodach | podloga_na_gruncie | plyta_fund | taras | attyka
    warstwy:                  # ściany: od WNĘTRZA do ZEWNĄTRZ; poziome: od GÓRY do DOŁU
      - {mat: TYNK_GIPS, d: 0.015}
      - {mat: SIL18, d: 0.18, konstrukcyjna: true}
      - {mat: EPS031, d: 0.20}
      - {mat: TYNK_SIL, d: 0.007}
sciany:
  - id: S0-01
    kond: P0
    przegroda: SZ1
    os: [[0.00, 0.00], [13.20, 0.00]]   # oś (środek) warstwy konstrukcyjnej
    wnetrze: lewa        # po której stronie osi (idąc od punktu 1 do 2) jest wnętrze; dla ścian wewn.: srodek (warstwy symetrycznie)
    z_od: null           # null = wierzch płyty konstrukcyjnej pod kondygnacją
    z_do: null           # null = spód stropu nad kondygnacją; liczba = rzędna względna
otwory:
  - id: O0-01
    sciana: S0-01
    symbol: OP1          # typ w zestawieniu stolarki (ten sam symbol = ten sam wyrób)
    typ: okno            # okno | fix | drzwi | drzwi_przesuwne_HS | drzwi_zewn | brama | otwor
    odl: 1.00            # od punktu początkowego osi ściany do krawędzi otworu w świetle muru [m]
    szer: 2.40           # w świetle muru
    wys: 2.70            # w świetle muru
    parapet: 0.00        # rzędna dolnej krawędzi otworu względem posadzki kondygnacji
    otwieranie: {strona: lewa|prawa, kierunek: do_wewn|na_zewn, rodzaj: RU|R|U|F|HS|PSK}
    oslona: zaluzja_zewn|roleta_zewn|screen_zip|brak
pomieszczenia:
  - id: "0.01"
    kond: P0
    nazwa: Wiatrołap
    punkt: [x, y]        # punkt wewnątrz — wielobok liczony z lic ścian wykończonych
    wielobok: null       # opcjonalnie jawny (strefy otwartej przestrzeni)
    kategoria: ruchu     # wg PN-ISO 9836:2015 (podstawowa | pomocnicza | ruchu | techniczna)  -> patrz rejestr wymagań
    pobyt_ludzi: false   # pomieszczenie przeznaczone na stały pobyt ludzi (wymagania WT dot. oświetlenia, wysokości)
    posadzka: GRES
    sciany_wyk: TYNK_MAL
    sufit: TYNK_MAL
    temp: 20             # temperatura obliczeniowa [°C] (PN-EN 12831-1 / WT §134)
    went: {wyw: 30, naw: 0}   # m³/h
stropy:
  - {id: ST1, nad: P0, wierzch: 2.95, grubosc: 0.20, obrys: [[..]], otwory: [[[..]]], podloga: POD-1, sufit: TYNK_GIPS}
dachy:
  - {id: D1, obrys: [[..]], plyta: {wierzch: 9.10, grubosc: 0.20}, przegroda: SD1, spadek: 0.02,
     attyka: {wys_nad_pokryciem: 0.30, szer: 0.25}, wpusty: [[x, y]], rzygacze: []}
wsporniki_plyty:  # płyty D, okapy
  - {id: PL-D, obrys: [[..]], wierzch: 3.05, grubosc: 0.22, przegroda: TAR1, lacznik_termiczny: true}
slupy:  [{id: SL1, xy: [x, y], przekroj: "RK 120x120x8", mat: STAL_S355, z_od: -0.30, z_do: 2.93}]
belki:  [{id: B1, os: [[..],[..]], b: 0.25, h: 0.40, spod: 2.73, mat: ZB_C30}]
fundamenty:
  typ: lawy | plyta
  elementy: [{id: L1, os: [[..],[..]], b: 0.60, h: 0.30, spod: -1.10}]
schody:
  - id: SCH1
    z_kond: P0
    na_kond: P1
    liczba_stopni: 18      # liczba podnóżków (wysokości)
    wys_stopnia: 0.175
    szer_stopnia: 0.28     # głębokość (s)
    biegi: [{start: [x, y], kierunek: [dx, dy], szer: 1.00, stopni: 9}]
    spoczniki: [{obrys: [[..]], rzedna: 1.575}]
balustrady: [{id: BL1, polilinia: [[x, y, z]...], wys: 1.10, typ: "szkło klejone VSG 44.2 / stal"}]
lamele:
  - {id: LAM-S, elewacja: S, linia: [[x, y], [x, y]], z_od: 6.05, z_do: 9.45, rozstaw: 0.12, b: 0.04, h: 0.08,
     odsuniecie: 0.15, mat: DREWNO_TERMO}
tarasy: [{id: T1, obrys: [[..]], rzedna: -0.02, nawierzchnia: "deska kompozytowa na legarach"}]
```

## 3. `dzialka.yaml` — sekcje
```yaml
uklad: {przesuniecie: [dx, dy], obrot: 0.0}   # transformacja budynek → układ działki (początek = narożnik SW działki)
dzialka: {nr: "123/4", obreb: "0005 Przykładowo", pow: 1500, obrys: [[..]]}
sasiedzi: [{nr, obrys, zabudowa: [[..]], opis}]
droga: {symbol: 1KDD, linie_rozgraniczajace: [[..]], jezdnia: [[..]], nawierzchnia: "asfalt"}
linia_zabudowy: [[..],[..]]
teren: {punkty: [[x, y, H], ...], warstwice_co: 0.10}
utwardzenia: [{id, obrys, nawierzchnia, spadek}]
zielen: [{id, obrys, typ: trawnik|rabata|zywoplot}]
drzewa: [{xy, gat, sr_korony, istn: true|false, do_wyciecia: false}]
ogrodzenie: [{linia, wys, typ}]
bramy: [{xy, szer, typ: przesuwna|furtka}]
miejsca_postojowe: [{obrys, typ: wiata|zewn}]
odpady: {obrys, opis}
uzbrojenie:
  istniejace: [{branza: woda|kan_sanit|en|tele|gaz, linia: [[..]], opis: "PE110"}]
  projektowane: [{branza, linia: [[..]], opis, dl: 12.5}]
retencja: {zbiornik: {xy, V: 5.0}, rozsaczanie: {obrys, V: 2.0}}
obszar_oddzialywania: {opis: "..."}
```

## 4. Reprezentacja pośrednia (IR) — `src/lamela/ir.py`
Każdy element fizyczny rozwiązywany jest do listy **pryzm** (bryła = wielobok podstawy × zakres z):
```python
@dataclass
class Prism:
    id: str                 # identyfikator elementu źródłowego + sufiks części (np. "S0-01#3")
    kind: str               # wall | slab | roof | parapet | insulation | column | beam | footing | stair_step | landing |
                            # railing | lamella | frame | glass | door_leaf | canopy | terrace | pavement | fence | terrain | furniture
    polygon: list           # [(x, y), ...] CCW, układ budynku [m]
    z0: float               # rzędna spodu (względem ±0,00)
    z1: float               # rzędna wierzchu
    material: str           # kod materiału (kolor 3D, kreskowanie w przekroju)
    level: str | None       # P0/P1/P2/None
    meta: dict              # np. {"layer": "EPS031", "opening": "O0-01"}
```
Ściany z otworami rozbijane są na pryzmy (pas podokienny, nadproże, filary); ościeżnice/szyby jako osobne pryzmy.
Teren = siatka trójkątów (osobna struktura `TerrainMesh`). IR zasila: model 3D (glTF), przekroje (cięcie płaszczyzną),
elewacje (rzut prostokątny z usuwaniem linii niewidocznych), kontrolę kolizji.

## 5. Konwencje WYMAGANE przez narzędzia (rdzeń `lamela.model/ir`, generatory `lamela.views`) — obowiązkowe
1. **Odsłonięte fragmenty stropów** (nieprzykryte wyższą kondygnacją — np. strop nad parterem poza obrysem P1, strop nad P1 poza
   obrysem P2) zapisuj jako elementy **`dachy`** z przegrodą stropodachu/dachu zielonego, attyką i spadkiem — nie jako `stropy`
   (inaczej brak warstw, attyki i spadku na przekroju i rzucie dachu). **Dach garażu = osobny element `dachy`.**
2. **Otwory** nie mogą leżeć w węźle ściany dochodzącej — zachowaj ≥ 0,10 m od lica ściany prostopadłej.
3. **Schody**: `biegi[].start` = środek krawędzi pierwszego podnóżka (początek biegu), `kierunek` = wektor wejścia; tylko biegi proste.
4. **Kreskowania materiałów** (`materialy.*.kreskowanie`) — wyłącznie kody silnika (PN-B-01030 + R4):
   `ZELBET, BETON, BETON_LEKKI, BETON_LEKKI_ZBROJONY, BETON_KOMORKOWY, MUR_CERAMIKA, MUR_SILIKAT, DREWNO_POPRZ, DREWNO_WZDL, SKLEJKA,
   PLYTA_DREWNOPOCHODNA, STAL, IZOL_MIEKKA (wełna), IZOL_TWARDA (EPS), IZOL_XPS, IZOL_PIR, IZOL_PRZECIWWODNA, IZOL_PRZECIWWILGOCIOWA,
   PAROIZOLACJA, MEMBRANA_PAROPRZEP, SZKLO, TWORZYWO, TYNK, PLYTA_GK, JASTRYCH, PLYTKI, GRUNT_RODZIMY, NASYP, PIASEK, ZWIR, POSPOLKA, HUMUS`.
   Styropian/EPS = `IZOL_TWARDA` (nie miękka); wylewka = `JASTRYCH`.
5. **Wyposażenie** (meble, sanitariaty, kuchnia) w osobnym pliku `model/wyposazenie.yaml` (format: patrz komentarz w
   `model/test/wyposazenie_testowe.yaml`). **Arkusze** — `model/arkusze.yaml` (patrz `lamela.views.sheets`).
6. Numeracja pomieszczeń na rysunkach: parter = 1.xx, I piętro = 2.xx, II piętro = 3.xx (R4 / PN-EN ISO 4157) — identyfikatory w modelu
   mogą pozostać 0.xx/1.xx/2.xx; generator przenumeruje (przełącznik `numeracja_pomieszczen`).
7. Rzędne na rysunkach AR z 3 miejscami po przecinku (PN-B-01025); PZT — 2 miejsca, wymiary w PZT z dokładnością 0,01 m.
8. **Obrysy płyt, dachów i attyk (audyt A2 K-1, 25.09.2026).** Krawędź `stropy`/`dachy` nad ścianą zewnętrzną niższej kondygnacji
   = **lico warstwy konstrukcyjnej** tej ściany (nie lico ocieplenia) — rdzeń przedłuża warstwy zewnętrzne ściany (ETICS/wełna) na czoło
   płyty i attyki, więc izolacja jest ciągła. Krawędź płyty/dachu przy ścianie **wyższej** kondygnacji (uskok bryły) = lico zewnętrzne
   ściany wyższej (płyta ciągła pod jej ociepleniem; dach dochodzi do lica ocieplenia). Rdzeń nie przedłuża warstw zewnętrznych ściany
   na wysokość płyty, jeśli płyta przechodzi przed licem w inny strop/dach na tym samym poziomie (wspornik stropu, dach przy uskoku).
   `attyka.szer` = grubość warstwy konstrukcyjnej attyki (w osi muru); `attyka.przegroda` (np. AT1) podaje warstwy: przed konstrukcją —
   izolacja od strony dachu (IR: pas „izolacja_attyki”), za konstrukcją — ocieplenie czoła (IR dodaje je tylko tam, gdzie ocieplenie
   ściany nie dochodzi do korony). Końce attyki prostopadłe do ściany wyższej dochodzą do jej lica (usuwany jest tylko pas równoległy).
   Płyty wysunięte `wsporniki_plyty` zaczynają się od lica ocieplenia; pas lico konstrukcji…lico ocieplenia = strefa łącznika
   termoizolacyjnego (ETA) w płaszczyźnie izolacji ściany; wierzch płyty wysuniętej = wierzch stropu (pogrubienie od spodu).

## 6. Rozszerzenia dla wody, izolacji i mostków (wymaganie Inwestora 25.09.2026 — obowiązkowe)
```yaml
dachy:
  - id: D1
    ...
    wpusty: [{xy: [x, y], dn: 100, podgrzewany: true}]
    przelewy_awaryjne: [{xy: [x, y], sciana_attyki: N|S|E|W, szer: 0.20, wys: 0.10, rzedna_dna: 9.45}]
    rury_spustowe: [{id: RS1, od_wpustu: 0, trasa: wewn_szacht|zewn, xy_pion: [x, y], dn: 100, do: zbiornik|niecka|kanal}]
    spadki: [{od: [x, y], do: [x, y], spadek: 0.02}]     # izolacja spadkowa — kierunki do wpustów
przegrody:
  # KAŻDA przegroda zewnętrzna ma pełne warstwy: paroizolacja / szczelność powietrzna, hydroizolacja (gdzie dotyczy),
  # warstwy spadkowe, drenażowe, geowłóknina, bariera przeciwkorzenna (dach zielony) — z materiałem i grubością.
wezly:            # katalog węzłów cieplno-wilgotnościowych (do detali i symulacji ISO 10211)
  - {id: WZ-01, nazwa: "Attyka stropodachu D1", typ: attyka, przegrody: [SD1, SZ1], polozenie: [[x, y, z], ...], dlugosc: 38.4}
dzialka.yaml:
  odwodnienia: [{id: OL1, typ: liniowe|opaska_zwirowa|drenaz_opaskowy|niecka, linia/obrys: [...], spadek: 0.01, odbiornik: ...}]
  teren: {punkty_projektowane: [[x, y, H], ...]}          # rzędne projektowane terenu (spadki od budynku ≥ 2 %)
```

## 7. Dane wymagane przez obliczenia fizyki budowli i EP (`lamela.obliczenia.fizyka_energia`) — uzupełnić w modelu
Pełna lista: docstring `src/lamela/obliczenia/energia/__init__.py`. Braki są raportowane, ale projekt ma być KOMPLETNY:
* **materialy:** `lambda` (obliczeniowa), `mu` lub `sd` (membrany), `rho`, `cp`; `funkcja` gdy klasyfikacja niejednoznaczna.
* **przegrody (zewnętrzne — pełne warstwy):** paroizolacja na płycie stropodachu; izolacja przeciwwilgociowa/przeciwwodna podłogi na
  gruncie / płyty; dach zielony: substrat, geowłóknina, warstwa drenażowa, bariera przeciwkorzenna (lub hydroizolacja odporna na
  korzenie); izolacja spadkowa: `klin: {d_min, d_max}`; ruszty/warstwy niejednorodne: `frakcje`.
* **pomieszczenia:** `temp` (°C; łazienki 24), garaż `ogrzewane: false`, `went: {naw, wyw}` [m³/h], `rodzaj`.
* **stropy:** podział na części: nad ogrzewanym / nad garażem / nad powietrzem zewnętrznym; `sufit` = kod przegrody z ociepleniem spodu —
  OBOWIĄZKOWY nad garażem i pod wspornikiem P2 (strop nad powietrzem).
* **dachy:** przegroda z pełnymi warstwami, `wpusty`, `przelewy_awaryjne`, `rury_spustowe`, `spadek`.
* **otwory:** `symbol`, `oslona`; sekcja **`stolarka.<symbol>`**: `wyrob`, `U_g`, `U_f`, `psi_g`, szer. ram, `g_n`, `U_D` (drzwi) — dane
  przykładowe typowych wyrobów (bez nazw handlowych, „lub równoważny”); ten sam symbol = ten sam wymiar.
* **wezly:** `id`, `typ` (aliasy mostki2d: R_attyka, GF_cokol, …), `dlugosc` lub `liczba`, `przegrody`.
* **energia:** `n50`, `osoby`, `pojemnosc` (klasa), `wezly_wyniki` (plik z symulacji mostków), `grunt.izolacja_obwodowa {typ, D, d_n, lam_n}`,
  `wentylacja {centrala, czerpnia: [x,y,z], wyrzutnia: [x,y,z], wywiewki_kanalizacyjne: [[x,y,z]]}`, `ogrzewanie {zrodlo: moce A−15/A−7/A2,
  SCOP_35, COP_cwu}`, `cwu {zasobnik, cyrkulacja}`, `pv {moduly, P_modul_Wp (Σ ≤ 6,5 kWp), azymut, nachylenie}`, `garaz {stanowiska,
  otwory_went_m2 ≥ 0,08}`, `capex_A`, `capex_B` (analiza alternatyw).

## 8. Dane wymagane przez obliczenia instalacji (`lamela.obliczenia.instalacje`, lista: `instalacje.DANE_WYMAGANE`)
* **model/wyposazenie.yaml:** przybory sanitarne z typem z katalogu `przybory.KATALOG`: `bidet, pisuar, pralka, prysznic, suszarka,
  umywalka, umywalka_blat, wanna, wc, wpust_podlogowy, wpust_podlogowy_100, zawor_czerpalny, zawor_ogrodowy, zlew, zlewik, zmywarka`
  — z punktem na licu ściany i obrotem; urządzenia z mocą (płyta, piekarnik, zmywarka, pralka, suszarka, lodówka…).
* **model/instalacje.yaml (nowy):** `osoby`; `lokalizacje` (RG, wodomierz, zasobnik c.w.u., rozdzielacze o.p. per kondygnacja, ZKP,
  studzienka rewizyjna, czerpnia, jednostka zewn. PC — ≥ 6,0 m od granicy, w osłonie lamelowej); `piony` (trasy); `wyroby` (karty
  przykładowe: PC — moce/COP/SCOP/L_WA, PV — moduł/falownik, wpusty, k_v, Δp wodomierza); opcjonalnie `przybory_dodatkowe`.
* **dachy[]:** `wpusty`, `przelewy_awaryjne`, `rury_spustowe` (odbiornik: zbiornik/niecka), warstwy dachu zielonego.
* **dzialka.yaml:** rzędne projektowane terenu, ZWG, rodzaj gruntu, położenie zbiornika i niecki; **otwory:** flaga `bezprogowe: true`
  dla HS, brama garażowa.

## 9. Dane wymagane przez obliczenia konstrukcyjne (`lamela.obliczenia.konstrukcja`)
* `schody[].plyta.grubosc` (demo: 15 cm nie przechodzi ugięcia — biblioteka wymaga ≥ 17 cm dla typowego biegu), `stropy[].mat` (klasa betonu),
  `belki[].przekroj` (belki stalowe, np. „HEB 200”, „RK 120x120x6”), `materialy[].ciezar` [kN/m³] (opcjonalnie), `fundamenty.elementy[].mat`.
* Sekcje w budynek.yaml: `konstrukcja: {klasa_konsekwencji: CC2, okres_uzytkowania: 50, ...}` i `geotechnika: {kategoria: II, grunt: {rodzaj,
  phi, gamma, M0, I_D}, ZWG: -3.8}` (propozycja R5 pkt 3.11).
* **Posadowienie:** zagłębienie ław/stóp **D ≥ 1,0 m** poniżej terenu (W-284) i ≥ h_z = 0,8 m — sprawdzić przy rzędnych terenu projektowanego;
  alternatywnie płyta fundamentowa na XPS z uzasadnieniem.
* **Ściany-tarcze i wsporniki tarczowe** (wspornik P2) — moduł `lamela.obliczenia.konstrukcja.tarcze` (MES płaskiego stanu naprężenia +
  model kratownicowy STM wg PN-EN 1992-1-1 p. 5.6.4/6.5). Ściana jest liczona jako tarcza, gdy ma pole `tarcza: true` albo automatycznie:
  warstwa konstrukcyjna żelbetowa i pod ścianą brak ciągłej podpory (ściany poniżej bez otworów + słupy < 95 % długości). `tarcza: false`
  wyłącza. Opcje (słownik): `tarcza: {beton: C30/37, ekspozycja: XC3, siatka: 0.10, tylko_docisk: true}` (podpory jednostronne — domyślnie). Dane pobierane z modelu:
  oś, z_od/z_do, grubość i materiał warstwy konstrukcyjnej (klasa betonu z nazwy materiału, np. „Żelbet C30/37”), otwory ściany,
  podpory = współliniowe ściany nośne poniżej (z_do w zakresie z_od − 0,6 … z_od; odcinki bez ich otworów; sztywność k = E·t/h) i słupy
  pod osią; obciążenia = reakcje płyt nad tarczą (krawędź górna), płyty pod tarczą poza ścianami poniżej (płyta podwieszona — krawędź
  dolna), ściany wyżej, belki oparte na ścianie. Tarcze podparte wyłącznie na ścianach poprzecznych — poza zakresem (analiza indywidualna).
