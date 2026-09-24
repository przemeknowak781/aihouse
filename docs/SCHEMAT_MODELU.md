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
