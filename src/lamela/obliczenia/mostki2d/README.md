# `lamela.obliczenia.mostki2d` — mostki cieplne 2D (PN-EN ISO 10211:2017)

Symulacja numeryczna węzłów (brief sekcja 9 pkt 2; W-248, W-250): L_2D, ψ_e/ψ_i, θ_si,min, f_Rsi, mapy temperatur,
wektory strumienia, raport Markdown, H_TB. Solver zwalidowany na przypadkach 1 i 2 zał. C ISO 10211
(`projekt/08_obliczenia/mostki2d/walidacja_ISO10211.md`).

```bash
PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d walidacja --out projekt/08_obliczenia/mostki2d
PYTHONPATH=src python3 -m lamela.obliczenia.mostki2d katalog --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
    --out projekt/08_obliczenia/mostki2d/katalog [--tylko WZ-C1,WZ-R1] [--teren -0.30]
PYTHONPATH=src python3 tools/test_mostki2d.py [--szybko]
```

## API

```python
from lamela.obliczenia.mostki2d import *
from lamela.model import load_model
m = load_model("model/budynek.yaml")
sz = warstwy_z_modelu(m, "SZ1")                                # [Warstwa(mat: Material(kod, lam, …), d, konstrukcyjna)]
wz = wezel_attyka(sz, warstwy_z_modelu(m, "SD-D1"), h_nad_pokryciem=0.30)
w = oblicz_wezel(wz, katalog_wykresow="out/rys")               # WynikWezla
w.psi_glowne.psi_e, w.psi_glowne.psi_i, w.psi_glowne.L2D       # W/(m·K)
w.f["theta_si_min"], w.f["f_Rsi"], w.fRsi_ok                   # R_si = 0,25; f_Rsi,min z wymagania.yaml (W-248)
w.L                                                            # {(grupa_a, grupa_b): L_ab} — 3 temperatury (garaż)
raport_katalogu([w, ...], "out/katalog.md", "Tytuł", dlugosci={"WZ-R1": 38.4})   # + H_TB = Σ ψ_e·l
```

| Moduł | Zawartość |
|---|---|
| `geometria.py` | `Material`, `Warstwa`, `Obszar` (wielobok shapely + materiał; kolejność = priorytet), `Strefa` (θ, rodzaj wewn/zewn/nieogrz, grupa, R_s: liczba / słownik kierunkowy ISO 6946 / 0 = temperatura zadana), `ElementFlankujacy` (U z warstw lub podane, l_e, l_i, albo `wezel_ref` — podmodel, np. okno), `Wezel`; `lambda_eq_pustki` (ISO 6946 zał. D, także małe pustki), `material_rama`/`material_szyba` (λ_eq z U_f/U_g), `U_podlogi_13370`, `warstwy_z_modelu`; węzły: `wezel_sciana_1d`, `wezel_naroznik_zewnetrzny`, `wezel_wspornik` (płyta wspornikowa z łącznikiem λ_eq / ciągła / `wysieg=0` — strop pośredni), `wezel_attyka` (+ blok termiczny), `wezel_oscieze_okna` (`w_izolacji` / `czesciowo` / `w_murze`), `wezel_cokol` (ława z murem fundamentowym lub płyta fundamentowa, grunt λ = 2,0, obszar 0,5b/2,5b/2,5b), `wezel_garaz` (3 temperatury; izolacja ciągła / przerwana), `wezel_rura_spustowa` (wnęka w ETICS) |
| `siatka.py` | siatka prostokątna przez wszystkie wierzchołki, zagęszczenie geometryczne (h_min, h_max, r, n_min), `podwojona()`, `klasyfikuj` |
| `solver.py` | `ModelMOS(wezel, siatka, tryb="psi"/"fRsi")` — MOS, średnia harmoniczna λ, Robin h = 1/R_s, SuperLU; iteracyjny wybór R_si (0,10/0,13/0,17) wg kierunku strumienia; `Rozwiazanie`: `T`, `q_brzeg`, `theta_pow`, `Phi_grup()`, `bilans()`, `temperatura(x, y)`, `strumien_komorek()` |
| `wyniki.py` | `oblicz_wezel` (siatka n → 2n [→ 4n] do zmiany Φ < 1 %, macierz L, ψ, f_Rsi, g, θ krytyczne), wykresy, `raport_wezla`, `raport_katalogu`, `zestawienie_HTB` |
| `walidacja.py` | ISO 10211 zał. C: przypadek 1 (28 punktów), przypadek 2 (A…I + Φ); A1 ściana 1D, A2 Fourier, A3 naroże izotermiczne; `raport_walidacji` |
| `katalog.py` | `katalog_z_modelu(model)` — węzły typowe z przegród modelu; `dlugosci_z_modelu` — długości do H_TB [INT] |

## Konwencje i założenia
* Wnętrze po stronie x < 0 (przekroje pionowe: lico wewn. ściany x = 0, posadzka/płyta y = 0); rzuty: `przekroj="poziomy"`
  (wszystkie R_si „poziomo”). Płaszczyzny odcięcia: max(1 m, 3·d) — adiabatyczne.
* ψ_e — wymiary zewnętrzne (ściany do wierzchu dachu / z grubością stropu, dach do lica zewn. ściany), ψ_i — wewnętrzne.
  Cokół: ściana od poziomu posadzki (oba systemy), podłoga U wg ISO 13370 z B' = b [INT]. Okno: ψ_inst = L_2D − U·l −
  L_2D,okna (model okna bez ściany).
* Dane przykładowe: łącznik termoizolacyjny λ_eq = 0,09 W/(m·K), d = 80 mm (`LACZNIK_PRZYKLAD`), okno z
  `obliczenia/dane/wyroby_przykladowe.yaml`, ściana garażu SIL 24 cm, θ_u z b_u = 0,8, teren −0,30 [ZAŁ].
* Wartości domyślne ψ ISO 14683 (`PSI_DOMYSLNE_14683`) — orientacyjne [NZW], tekst normy niedostępny (R6-32, D-19).

## Ograniczenia
* 2D (mostki liniowe); mostki punktowe χ (konsole lamel, kotwy, narożniki 3D) — wymagają modelu 3D.
* Krawędzie ukośne aproksymowane schodkowo (siatka prostokątna).
* Rama okna jako materiał zastępczy (λ_eq z U_f) — nie zastępuje obliczeń ramy wg ISO 10077-2; ψ_g poza zakresem.
* Ustalony przepływ ciepła (bez pojemności cieplnej i transportu wilgoci); ocena pleśni — kryterium f_Rsi.
