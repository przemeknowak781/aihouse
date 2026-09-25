# `lamela.obliczenia.mostki2d` — mostki cieplne 2D (PN-EN ISO 10211:2017)

Symulacja numeryczna węzłów (brief sekcja 9 pkt 2; W-248, W-250): L_2D, ψ_oi/ψ_e/ψ_i, θ_si,min, f_Rsi, mapy
temperatur, wektory strumienia, raport Markdown, H_TB (ψ_oi — system wymiarów projektu), eksport JSON dla
`fizyka.mostki`. Solver zwalidowany na przypadkach 1 i 2 zał. C ISO 10211 (także niezależność od siatki) i przypadkach
analitycznych; uwagi weryfikacji niezależnej i poprawki — `projekt/08_obliczenia/mostki2d/walidacja_ISO10211.md`.

```bash
PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d walidacja --out projekt/08_obliczenia/mostki2d
PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d katalog --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
    --out projekt/08_obliczenia/mostki2d/katalog [--tylko WZ-C1,WZ-R1] [--teren -0.30]
PYTHONPATH=src python3 tools/test_mostki2d.py [--szybko]
# katalog kart węzłów (ciągłość izolacji, woda/wilgoć, ocena; PNG + Markdown): sekcja `wezly` modelu albo katalog
# demonstracyjny z wariantami porównawczymi (model bez `wezly`, --demo)
PYTHONPATH=src python3 tools/katalog_mostkow.py [--budynek model/budynek.yaml] [--dzialka …] [--out …] [--tylko …] [--demo]
```

## API

```python
from lamela.obliczenia.mostki2d import *
from lamela.model import load_model
m = load_model("model/budynek.yaml")
sz = warstwy_z_modelu(m, "SZ1")                                # [Warstwa(mat: Material(kod, lam, …), d, konstrukcyjna)]
wz = wezel_attyka(sz, warstwy_z_modelu(m, "SD-D1"), h_nad_pokryciem=0.30)
w = oblicz_wezel(wz, katalog_wykresow="out/rys")               # WynikWezla
w.psi_glowne.psi_oi, w.psi_glowne.psi_e, w.psi_glowne.psi_i     # W/(m·K); ψ_oi — do H_TB (energia.bryla)
w.f["theta_si_min"], w.f["f_Rsi"], w.fRsi_ok                   # R_si = 0,25; f_Rsi,min z wymagania.yaml (W-248)
w.L                                                            # {(grupa_a, grupa_b): L_ab} — 3 temperatury (garaż)
raport_katalogu([w, ...], "out/katalog.md", "Tytuł", dlugosci={"WZ-R1": 35.2})   # + H_TB = Σ ψ_oi·l_oi
eksport_wynikow([w, ...], dlugosci, "out/wyniki_mostki2d.json")  # {id: {psi_oi, psi_e, psi_i, f_rsi, dlugosc_oi, typ}}
```

| Moduł | Zawartość |
|---|---|
| `geometria.py` | `Material`, `Warstwa`, `Obszar` (wielobok shapely + materiał; kolejność = priorytet), `Strefa` (θ, rodzaj wewn/zewn/nieogrz, grupa, R_s: liczba / słownik kierunkowy ISO 6946 / 0 = temperatura zadana), `ElementFlankujacy` (U z warstw lub podane, l_e, l_i, l_oi, albo `wezel_ref` — podmodel, np. okno), `Wezel`; `lambda_eq_pustki` (ISO 6946 zał. D, także małe pustki), `material_rama`/`material_szyba` (λ_eq z U_f/U_g), `U_podlogi_13370`, `warstwy_z_modelu`; węzły: `wezel_sciana_1d`, `wezel_naroznik_zewnetrzny`, `wezel_wspornik` (płyta wspornikowa z łącznikiem λ_eq / ciągła / `wysieg=0` — strop pośredni), `wezel_attyka` (+ blok termiczny; warstwa wentylowana → błąd), `wezel_oscieze_okna` (`w_izolacji` / `czesciowo` / `w_murze`), `wezel_nadproze` (nadproże ŻB, opcjonalnie kaseta żaluzji/screenu w ociepleniu), `wezel_podokiennik` (parapet wewn. + obróbka zewn. z okapnikiem), `wezel_prog_strop` (próg okna/drzwi do podłogi na stropie lub płycie wspornikowej z łącznikiem), `wezel_cokol` (ława z murem fundamentowym lub płyta fundamentowa, grunt λ = 2,0, obszar 0,5b/2,5b/2,5b; `prog=` — próg drzwi na płycie parteru), `wezel_garaz` (3 temperatury; izolacja ciągła / przerwana), `wezel_rura_spustowa` (wnęka w ETICS); `U_w_okna` (ISO 10077-1) |
| `siatka.py` | siatka prostokątna przez wszystkie wierzchołki (przyciąganie do 1 µm), zagęszczenie geometryczne (h_min, h_max, r, n_min; iloraz komórek na liniach granicznych ≤ 2; h_min ≤ grubość cienkich warstw o λ ≥ 1), `podwojona()`, `klasyfikuj` + `kontroluj_pustki` (szczeliny i zamknięte pustki → ValueError) |
| `solver.py` | `ModelMOS(wezel, siatka, tryb="psi"/"fRsi")` — MOS, średnia harmoniczna λ, Robin h = 1/R_s, SuperLU; iteracyjny wybór R_si (0,10/0,13/0,17) wg kierunku strumienia; `Rozwiazanie`: `T`, `q_brzeg`, `theta_pow`, `Phi_grup()`, `bilans()`, `temperatura(x, y)` (w wierzchołkach — średnia ważona λ), `theta_si_min()` (środki ścian + wierzchołki powierzchni), `strumien_komorek()` |
| `wyniki.py` | `oblicz_wezel` (siatka n → 2n [→ 4n] do zmiany Φ < 1 % i zmiany ψ ≤ max(1 %; 0,001); bilans < 10⁻⁴ wymuszany; macierz L, ψ_oi/ψ_e/ψ_i, f_Rsi, g, θ krytyczne), wykresy, `raport_wezla`, `raport_katalogu`, `zestawienie_HTB(system="oi")`, `eksport_wynikow` |
| `walidacja.py` | ISO 10211 zał. C: przypadek 1 (28 punktów), przypadek 2 (A…I + Φ; także na siatce zgrubnej); A1 ściana 1D, A2 Fourier, A3 naroże izotermiczne; `kontrole_poprawek`; `raport_walidacji` (+ sekcja „Weryfikacja niezależna i poprawki”) |
| `karta.py` | `ciaglosc_izolacji` („test ołówka” na siatce: najkrótsza droga przez materiały λ > 0,12 z wnętrza na zewnątrz — mostek konstrukcyjny / przez grunt), `kontrola_wody` (hydro/przeciwwilgociowa, paro/szczelność, spadki, obróbki, wpusty, przelewy, rury spustowe, drenaż — z warstw przegród i `dachy[]`, `dzialka.odwodnienia`), `ocena_wezla` (BEZMOSTKOWY / DOBRY / DO POPRAWY / ZŁY / NIE SPEŁNIA), `rysuj_karte` (przekrój z materiałami i liniami „4 linii” z `Wezel.linie` + mapa temperatur), `raport_kart` |
| `katalog.py` | `katalog_z_modelu(model)` — węzły typowe z przegród modelu (osadzenie okien z `rama_t`, b = B'); `otwory_zewnetrzne` (tylko ściany `sciana_zewn`); `dlugosci_z_modelu` — długości do H_TB w systemie oi [INT]; `katalog_demonstracyjny` (+ warianty: ościeże w murze, płyta fundamentowa, blok termiczny, wspornik bez łącznika); `wezly_z_sekcji` (sekcja `wezly` modelu → węzły, `ALIASY_WEZLOW`, `wariant`, `parametry`, `dlugosc`) |

## Konwencje i założenia
* Wnętrze po stronie x < 0 (przekroje pionowe: lico wewn. ściany x = 0, posadzka/płyta y = 0); rzuty: `przekroj="poziomy"`
  (wszystkie R_si „poziomo”). Płaszczyzny odcięcia: max(1 m, 3·d) — adiabatyczne.
* **ψ_oi — wymiary wewnętrzne całkowite (system projektu: `energia.bryla`, `fizyka.mostki`; H_TB)**: wysokości „od
  podłogi do podłogi” (strop pośredni, wspornik, próg: ψ_oi = ψ_e), pod dachem do spodu płyty (attyka), długości po
  licach wewnętrznych (naroże, cokół: ψ_oi = ψ_i), okna w świetle otworu w murze (ościeże/nadproże/podokiennik:
  ściana do krawędzi otworu + korekta U_w·x0). ψ_e — wymiary zewnętrzne, ψ_i — wewnętrzne (do porównań z ISO 14683).
  Cokół: ściana od poziomu posadzki, podłoga U wg ISO 13370 z B' = A/(0,5·P) [INT]. Okno: ψ_inst = L_2D − U·l −
  L_2D,okna (model okna bez ściany).
* Długości H_TB (`dlugosci_z_modelu`): tylko otwory w ścianach zewnętrznych; ościeża boczne 2·wys (WZ-W1), nadproża
  szer (WZ-N1; z żaluzją/screenem — WZ-N2, kaseta podtynkowa [ZAŁ]), podokienniki szer (parapet > 5 cm, WZ-P1),
  progi szer (parter WZ-T1, okna do podłogi na stropie WZ-T2, drzwi na płytę wspornikową WZ-T3); IF1/GF1/B1 pomniejszone
  o progi.
* Dane przykładowe: łącznik termoizolacyjny λ_eq = 0,09 W/(m·K), d = 80 mm (`LACZNIK_PRZYKLAD`), okno z
  `obliczenia/dane/wyroby_przykladowe.yaml`, ściana garażu SIL 24 cm, θ_u z b_u = 0,8, teren −0,30 [ZAŁ].
* Wartości domyślne ψ ISO 14683 (`PSI_DOMYSLNE_14683`) — orientacyjne [NZW], tekst normy niedostępny (R6-32, D-19).

## Ograniczenia
* 2D (mostki liniowe); mostki punktowe χ (konsole lamel, kotwy, narożniki 3D, wpusty dachowe i rzygacze w attyce,
  przejścia rur spustowych) — wymagają modelu 3D lub deklaracji wyrobu.
* Przegrody z warstwą powietrza dobrze wentylowaną (dach/elewacja wentylowana) — `wezel_attyka` zgłasza błąd.
* Przekroje progów i podokienników: spadki (parapet zewn., płyta balkonu) pominięte; kaseta osłony traktowana jako
  przestrzeń zewnętrzna (wariant ostrożny).
* Krawędzie ukośne aproksymowane schodkowo (siatka prostokątna).
* Rama okna jako materiał zastępczy (λ_eq z U_f) — nie zastępuje obliczeń ramy wg ISO 10077-2; ψ_g poza zakresem.
* `Wezel.linie` (membrany, taśmy, obróbki, drenaż, rura spustowa) — tylko rysunek (schemat wymagań detalu), cieplnie
  pominięte; lista kontrolna wody opiera się na danych modelu — brak danych = pozycja „BRAK”.
* Ustalony przepływ ciepła (bez pojemności cieplnej i transportu wilgoci); ocena pleśni — kryterium f_Rsi.
