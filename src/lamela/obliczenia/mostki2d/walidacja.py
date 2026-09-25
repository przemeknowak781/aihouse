"""Walidacja solvera mostki2d — PN-EN ISO 10211:2017 zał. C (przypadki referencyjne 2D) + przypadki analityczne.

Metoda 2D jest „dokładną metodą ustaloną 2D” w rozumieniu ISO 10211, jeśli daje wyniki zgodne z przypadkami 1 i 2
zał. C z tolerancją: temperatury ± 0,1 K, strumień ± 0,1 W/m (przypadek 2).

Przypadek 1 — połowa kwadratowej kolumny (BC = 2·AB), zadane temperatury powierzchni: AB = 20 °C, BC i CD = 0 °C,
AD — oś symetrii (adiabatyczna). Rozwiązanie analityczne w 28 węzłach siatki równomiernej (4 × 7).
Przypadek 2 — mostek 2D z 4 materiałami (λ = 1,15; 0,12; 0,029; 230 W/(m·K)); AB: 0 °C, R_se = 0,06;
HI: 20 °C, R_si = 0,11; temperatury w punktach A…I i całkowity strumień 9,5 W/m.

Źródła danych referencyjnych (tekst normy niedostępny — dane z dokumentów walidacyjnych programów, zgodne ze sobą):
* Physibel, „Validation of the program BISCO according to ISO 10211” (Knowledge Base, 2020/2026) — rysunki C.1/C.2
  normy z tabelą 28 temperatur przypadku 1 oraz wymiarami, λ, warunkami brzegowymi i wynikami przypadku 2:
  https://www.physibel.be/uploads/knowledge_bases/document/40/A2-Validation_BISCO_EN10211.pdf
* SimScale, „Thermal Bridge Case 2 — Insulated Wall” (współrzędne punktów A…M, λ, warunki, wyniki referencyjne):
  https://www.simscale.com/docs/validation-cases/thermal-bridge-case-2/
* QuickField, „ISO 10211:2007 test case A.2” (wymiary 5 / 1,5 / 6 / 33,5 / 13,5 / 500 mm, λ, R_s, wyniki):
  https://quickfield.com/advanced/iso_10211_2007_case2.htm

Przypadki analityczne dodatkowe:
* A1 — ściana warstwowa 1D z warunkami Robina: U = 1/(R_si + Σd/λ + R_se), temperatury na stykach warstw (dokładne);
* A2 — przypadek 1 porównany z szeregiem Fouriera (bez zaokrągleń tabeli);
* A3 — naroże 90° o stałej grubości t z izotermicznymi powierzchniami: przewodność kształtu S = (a + b)/t + ΔS,
  ΔS ≈ 0,559 (kwadrat narożny „0,56 kwadratu” — rozwiązanie odwzorowaniem konforemnym, np. Hall 1967;
  wzór przybliżony Langmuira–Adamsa–Stevensa 0,54) — sprawdzenie z tolerancją 0,01.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from shapely.geometry import box

from .geometria import Material, Obszar, Strefa, Warstwa, Wezel, U_warstw  # noqa: F401
from .siatka import siatka_dla_wezla
from .solver import ModelMOS

# --------------------------------------------------------------------------------------------------
# Dane referencyjne
# --------------------------------------------------------------------------------------------------
PRZYPADEK1_TABELA = [          # wiersze od AB (góra) w dół, kolumny od BC (lewa) do osi AD
    [9.7, 13.4, 14.7, 15.1],
    [5.3, 8.6, 10.3, 10.8],
    [3.2, 5.6, 7.0, 7.5],
    [2.0, 3.6, 4.7, 5.0],
    [1.3, 2.3, 3.0, 3.2],
    [0.7, 1.4, 1.8, 1.9],
    [0.3, 0.6, 0.8, 0.9],
]
PRZYPADEK2_PUNKTY = {          # [mm] (x od osi symetrii AH, y od HI)
    "A": (0.0, 47.5), "B": (500.0, 47.5), "C": (0.0, 41.5), "D": (15.0, 41.5), "E": (500.0, 41.5),
    "F": (0.0, 36.5), "G": (15.0, 36.5), "H": (0.0, 0.0), "I": (500.0, 0.0),
}
PRZYPADEK2_T = {"A": 7.1, "B": 0.8, "C": 7.9, "D": 6.3, "E": 0.8, "F": 16.4, "G": 16.3, "H": 16.8, "I": 18.3}
PRZYPADEK2_PHI = 9.5
TOL_T = 0.1
TOL_PHI = 0.1
ZRODLA = [
    ("Physibel — Validation of the program BISCO according to ISO 10211 (rys. C.1, C.2 normy z danymi)",
     "https://www.physibel.be/uploads/knowledge_bases/document/40/A2-Validation_BISCO_EN10211.pdf"),
    ("SimScale — Thermal Bridge Case 2 (ISO 10211 zał. C, przypadek 2)",
     "https://www.simscale.com/docs/validation-cases/thermal-bridge-case-2/"),
    ("QuickField — ISO 10211:2007 test case A.2", "https://quickfield.com/advanced/iso_10211_2007_case2.htm"),
    ("WUFI — Two-dimensional test cases of ISO 10211 (opis przypadku 1)",
     "https://wufi.de/en/2015/04/09/two-dimensional-test-cases-of-iso-10211/"),
]


@dataclass
class WynikWalidacji:
    nazwa: str
    ok: bool
    max_odch_T: float | None = None
    odch_phi: float | None = None
    tolerancja: str = ""
    wiersze: list = field(default_factory=list)     # [punkt, ref, obl, odch]
    uwagi: list = field(default_factory=list)
    siatka: str = ""


# --------------------------------------------------------------------------------------------------
# Przypadek 1
# --------------------------------------------------------------------------------------------------
def przypadek1_analityczny(x: float, y: float, AB: float = 1.0, theta: float = 20.0, n_wyr: int = 401) -> float:
    """Kwadrat [0, 2AB]² z górną krawędzią θ, pozostałe 0 °C (pełna kolumna): θ(x, y) = (4θ/π) Σ_{n nieparz.}
    sin(nπx/a)·sinh(nπy/a) / (n·sinh(nπ)), a = 2AB."""
    a = 2 * AB
    s = 0.0
    for n in range(1, n_wyr + 1, 2):
        # sinh(nπy/a)/sinh(nπ) — postać stabilna numerycznie
        r = math.exp(n * math.pi * (y / a - 1)) * (1 - math.exp(-2 * n * math.pi * y / a)) / (1 - math.exp(-2 * n * math.pi))
        s += math.sin(n * math.pi * x / a) * r / n
    return 4 * theta / math.pi * s


def wezel_przypadek1(AB: float = 1.0) -> Wezel:
    mat = Material("BETON_WAL", 2.0, "materiał dowolny (zadane temperatury)")
    H = 2 * AB
    s = 0.05 * AB
    obszary = [Obszar(box(0, 0, AB, H), mat, "kolumna")]
    strefy = [
        Strefa("AB (20 °C)", box(0, H, AB, H + s), 20.0, "wewn", "i", Rs=0.0),
        Strefa("BC (0 °C)", box(-s, 0, 0, H), 0.0, "zewn", "e", Rs=0.0),
        Strefa("CD (0 °C)", box(0, -s, AB, 0), 0.0, "zewn", "e", Rs=0.0),
    ]
    return Wezel("ISO10211-C1", "ISO 10211 zał. C — przypadek 1", "walidacja", obszary, strefy,
                 siatka={"h_min": 0.002 * AB, "h_max": 0.02 * AB, "r": 1.2})


def punkty_przypadek1(AB: float = 1.0) -> dict[str, tuple[float, float]]:
    H = 2 * AB
    pk = {}
    for w in range(7):
        for k in range(4):
            pk[f"{w + 1}.{k + 1}"] = ((k + 1) * AB / 4, H - (w + 1) * AB / 4)
    return pk


def waliduj_przypadek1(h_min: float = 0.002, h_max: float = 0.02) -> tuple[WynikWalidacji, WynikWalidacji]:
    wz = wezel_przypadek1()
    s = siatka_dla_wezla(wz, h_min=h_min, h_max=h_max)
    roz = ModelMOS(wz, s).rozwiaz()
    wiersze, wiersze_a = [], []
    mx = mxa = 0.0
    for (nazwa, (x, y)), ref in zip(punkty_przypadek1().items(), [v for r in PRZYPADEK1_TABELA for v in r]):
        t = roz.temperatura(x, y)
        ta = przypadek1_analityczny(x, y)
        d, da = t - ref, t - ta
        mx, mxa = max(mx, abs(d)), max(mxa, abs(da))
        wiersze.append([nazwa, f"({x:.2f}; {y:.2f})", ref, t, d])
        wiersze_a.append([nazwa, f"({x:.2f}; {y:.2f})", ta, t, da])
    w1 = WynikWalidacji("ISO 10211 zał. C — przypadek 1 (28 punktów, tabela normy)", mx <= TOL_T, mx, None,
                        "Δθ w ± 0,1 K", wiersze, siatka=s.opis())
    w2 = WynikWalidacji("A2 — przypadek 1 vs szereg Fouriera (bez zaokrągleń)", mxa <= 0.02, mxa, None,
                        "Δθ w ± 0,02 K", wiersze_a, siatka=s.opis())
    w1.uwagi.append(f"bilans energii: {roz.bilans():.1e}")
    return w1, w2


# --------------------------------------------------------------------------------------------------
# Przypadek 2
# --------------------------------------------------------------------------------------------------
def wezel_przypadek2() -> Wezel:
    """Geometria (mm): AB = 500 (szerokość), AC = 6 (mat. 1, λ = 1,15, pas 41,5…47,5), CD = 15 i CF = 5 (mat. 2,
    λ = 0,12: x 0…15, y 36,5…41,5), mat. 3 (λ = 0,029) — reszta pasa 36,5…41,5 (x > 15) i obszar 1,5…36,5 poza
    profilem, mat. 4 (λ = 230) — profil: półka górna FG × GJ (x 0…15, y 35…36,5), środnik KL (x 0…1,5), półka dolna
    HI…M (y 0…1,5, cała szerokość; IM = 1,5); EM = 40."""
    mm = 1e-3
    m1 = Material("M1", 1.15, "materiał 1 (λ = 1,15)", "#b9b6ae")
    m2 = Material("M2", 0.12, "materiał 2 (λ = 0,12)", "#b58a5a")
    m3 = Material("M3", 0.029, "materiał 3 (λ = 0,029)", "#e8e060")
    m4 = Material("M4", 230.0, "materiał 4 (λ = 230)", "#9aa3ab")
    W = 500 * mm
    obszary = [
        Obszar(box(0, 1.5 * mm, W, 41.5 * mm), m3, "3"),
        Obszar(box(0, 41.5 * mm, W, 47.5 * mm), m1, "1"),
        Obszar(box(0, 36.5 * mm, 15 * mm, 41.5 * mm), m2, "2"),
        Obszar(box(0, 0, W, 1.5 * mm), m4, "4 — półka dolna"),
        Obszar(box(0, 1.5 * mm, 1.5 * mm, 36.5 * mm), m4, "4 — środnik"),
        Obszar(box(0, 35 * mm, 15 * mm, 36.5 * mm), m4, "4 — półka górna"),
    ]
    s = 5 * mm
    strefy = [
        Strefa("AB (0 °C, R_se = 0,06)", box(0, 47.5 * mm, W, 47.5 * mm + s), 0.0, "zewn", "e", Rs=0.06),
        Strefa("HI (20 °C, R_si = 0,11)", box(0, -s, W, 0), 20.0, "wewn", "i", Rs=0.11),
    ]
    return Wezel("ISO10211-C2", "ISO 10211 zał. C — przypadek 2", "walidacja", obszary, strefy,
                 siatka={"h_min": 0.1 * mm, "h_max": 2 * mm, "r": 1.2})


def waliduj_przypadek2(h_min: float = 0.1e-3, h_max: float = 2e-3) -> WynikWalidacji:
    wz = wezel_przypadek2()
    s = siatka_dla_wezla(wz, h_min=h_min, h_max=h_max)
    roz = ModelMOS(wz, s).rozwiaz()
    wiersze = []
    mx = 0.0
    for p, (x, y) in PRZYPADEK2_PUNKTY.items():
        t = roz.temperatura(x * 1e-3, y * 1e-3)
        d = t - PRZYPADEK2_T[p]
        mx = max(mx, abs(d))
        wiersze.append([p, f"({x:g}; {y:g}) mm", PRZYPADEK2_T[p], t, d])
    phi = roz.Phi_grup()["i"]
    dphi = phi - PRZYPADEK2_PHI
    wiersze.append(["Φ [W/m]", "HI → AB", PRZYPADEK2_PHI, phi, dphi])
    w = WynikWalidacji("ISO 10211 zał. C — przypadek 2 (punkty A…I + strumień)", mx <= TOL_T and abs(dphi) <= TOL_PHI,
                       mx, dphi, "Δθ w ± 0,1 K; ΔΦ w ± 0,1 W/m", wiersze, siatka=s.opis())
    w.uwagi.append(f"bilans energii: {roz.bilans():.1e}; Φ_AB = {-roz.Phi_grup()['e']:.4f} W/m")
    return w


SIATKI_PRZYPADKU2 = [(0.5e-3, 5e-3), (0.1e-3, 2e-3)]      # (h_min, h_max) [m] — siatka zgrubna i walidacyjna


def waliduj_przypadek2_siatki(siatki=SIATKI_PRZYPADKU2) -> WynikWalidacji:
    """Przypadek 2 na siatce zgrubnej (h_min = 0,5 mm) i walidacyjnej (0,1 mm): wynik nie może zależeć od siatki
    (regresja uwagi 1 weryfikacji niezależnej — temperatura w wierzchołku G na styku aluminium/drewno/korek)."""
    wz = wezel_przypadek2()
    wiersze = []
    mx = 0.0
    ok = True
    opis = []
    for h_min, h_max in siatki:
        s = siatka_dla_wezla(wz, h_min=h_min, h_max=h_max)
        roz = ModelMOS(wz, s).rozwiaz()
        for p in ("D", "G"):
            x, y = PRZYPADEK2_PUNKTY[p]
            t = roz.temperatura(x * 1e-3, y * 1e-3)
            d = t - PRZYPADEK2_T[p]
            mx = max(mx, abs(d))
            ok &= abs(d) <= TOL_T
            wiersze.append([p, f"h_min = {h_min * 1000:g} mm ({s.n} kom.)", PRZYPADEK2_T[p], t, d])
        phi = roz.Phi_grup()["i"]
        ok &= abs(phi - PRZYPADEK2_PHI) <= TOL_PHI
        wiersze.append(["Φ [W/m]", f"h_min = {h_min * 1000:g} mm", PRZYPADEK2_PHI, phi, phi - PRZYPADEK2_PHI])
        opis.append(s.opis())
    w = WynikWalidacji("Przypadek 2 — niezależność od siatki (h_min = 0,5 i 0,1 mm; punkty D, G, Φ)", ok, mx, None,
                       "Δθ w ± 0,1 K; ΔΦ w ± 0,1 W/m na każdej siatce", wiersze, siatka=" | ".join(opis))
    w.uwagi.append("Niezależny solver węzłowy (weryfikator): G = 16,334 °C, D = 6,273 °C (zbieżne 13k–210k węzłów). "
                   "Przed poprawką (średnia arytmetyczna rekonstrukcji z 4 komórek wokół wierzchołka) G zależało od "
                   "siatki: 16,108 (h_min 0,5 mm — poza tolerancją) … 16,273 (siatka walidacyjna) … 16,313 °C.")
    return w


# --------------------------------------------------------------------------------------------------
# A1 — ściana warstwowa 1D
# --------------------------------------------------------------------------------------------------
def waliduj_1d() -> WynikWalidacji:
    warstwy = [Warstwa(Material("TG", 0.40), 0.015), Warstwa(Material("SIL", 0.77), 0.18),
               Warstwa(Material("EPS", 0.031), 0.20), Warstwa(Material("TS", 0.70), 0.007)]
    ti, te, Rsi, Rse = 20.0, -18.0, 0.13, 0.04
    x = 0.0
    obszary = []
    for w in warstwy:
        obszary.append(Obszar(box(x, 0, x + w.d, 0.5), w.mat))
        x += w.d
    strefy = [Strefa("wewn", box(-0.05, 0, 0, 0.5), ti, "wewn", "i", Rs=Rsi),
              Strefa("zewn", box(x, 0, x + 0.05, 0.5), te, "zewn", "e", Rs=Rse)]
    wz = Wezel("A1", "ściana 1D", "walidacja", obszary, strefy, przekroj="poziomy",
               siatka={"h_min": 0.001, "h_max": 0.02})
    s = siatka_dla_wezla(wz)
    roz = ModelMOS(wz, s).rozwiaz()
    U = U_warstw(warstwy, Rsi, Rse)
    q = U * (ti - te)
    wiersze = []
    mx = 0.0
    # temperatury: powierzchnia wewn., styki, powierzchnia zewn.
    t_an = ti - q * Rsi
    xs = 0.0
    punkty = [("θ_si", 0.0, t_an)]
    for k, w in enumerate(warstwy):
        t_an -= q * w.R
        xs += w.d
        punkty.append((f"styk {k + 1}/{k + 2}" if k < len(warstwy) - 1 else "θ_se", xs, t_an))
    for nazwa, xp, ta in punkty:
        t = roz.temperatura(xp, 0.25)
        mx = max(mx, abs(t - ta))
        wiersze.append([nazwa, f"x = {xp:.3f}", ta, t, t - ta])
    Ud = roz.Phi_grup()["i"] / 0.5 / (ti - te)
    wiersze.append(["U [W/(m²K)]", "—", U, Ud, Ud - U])
    ok = mx < 1e-6 and abs(Ud - U) < 1e-9
    return WynikWalidacji("A1 — ściana warstwowa 1D (Robin), rozwiązanie dokładne", ok, mx, None,
                          "Δθ w ± 10⁻⁶ K; ΔU w ± 10⁻⁹", wiersze, siatka=s.opis())


# --------------------------------------------------------------------------------------------------
# A3 — naroże z izotermicznymi powierzchniami
# --------------------------------------------------------------------------------------------------
DELTA_S_NAROZA = 0.559        # rozwiązanie konforemne ≈ 0,5587 (literatura: „0,56 kwadratu”; Langmuir 0,54)


def waliduj_naroze(t: float = 0.3, a: float = 1.2, h_min: float = 0.001, h_max: float = 0.02) -> WynikWalidacji:
    mat = Material("M", 1.0)
    # wnętrze: x<0, y<0; ściany grubości t; nogi długości a od naroża wewnętrznego
    geom = box(-a, -a, t, t).difference(box(-a - 1, -a - 1, 0, 0))
    obszary = [Obszar(geom, mat)]
    s_ = 0.05
    strefy = [Strefa("wewn (1 °C)", box(-a, -a, 0, 0), 1.0, "wewn", "i", Rs=0.0),
              Strefa("zewn (0 °C)", box(-a, -a, t + s_, t + s_).difference(box(-a - 1, -a - 1, t, t)), 0.0, "zewn",
                     "e", Rs=0.0)]
    wz = Wezel("A3", "naroże izotermiczne", "walidacja", obszary, strefy, przekroj="poziomy",
               siatka={"h_min": h_min, "h_max": h_max, "r": 1.2})
    s = siatka_dla_wezla(wz)
    roz = ModelMOS(wz, s).rozwiaz()
    S = roz.Phi_grup()["i"]
    dS = S - 2 * a / t
    s2 = s.podwojona()
    roz2 = ModelMOS(wz, s2).rozwiaz()
    dS2 = roz2.Phi_grup()["i"] - 2 * a / t
    ok = abs(dS2 - DELTA_S_NAROZA) <= 0.01
    w = WynikWalidacji("A3 — naroże 90°, powierzchnie izotermiczne: ΔS = S − (a+b)/t", ok, None, None,
                       "ΔS = 0,559 ± 0,01",
                       [["ΔS (siatka n)", f"t = {t}, a = b = {a}", DELTA_S_NAROZA, dS, dS - DELTA_S_NAROZA],
                        ["ΔS (siatka 2n)", "", DELTA_S_NAROZA, dS2, dS2 - DELTA_S_NAROZA]], siatka=s2.opis())
    w.uwagi.append("Wartość odniesienia 0,559 — kwadrat narożny ≈ 0,56 „kwadratu” (odwzorowanie konforemne); "
                   "wzór Langmuira–Adamsa–Stevensa (1919) podaje 0,54 (przybliżenie).")
    return w


# --------------------------------------------------------------------------------------------------
def waliduj_wszystko() -> list[WynikWalidacji]:
    w1, w1a = waliduj_przypadek1()
    return [w1, waliduj_przypadek2(), waliduj_przypadek2_siatki(), waliduj_1d(), w1a, waliduj_naroze()]


# --------------------------------------------------------------------------------------------------
# Kontrole poprawek po weryfikacji niezależnej
# --------------------------------------------------------------------------------------------------
PSI_FIN_REF = 0.03472     # ψ (półmodel) płaskownika stalowego 2 mm w izolacji 0,2 m — niezależny solver węzłowy
                          # weryfikatora (zbieżny: 0,034798 / 0,034746 / 0,034728) [odniesienie numeryczne, nie normowe]


def kontrole_poprawek() -> list[list]:
    """Kontrole numeryczne poprawek (uruchamiane przy każdym raporcie): [nr, zagadnienie, wynik kontroli, ok]."""
    from .geometria import ElementFlankujacy, _nas, strefy_z_dopelnienia, wezel_attyka, wezel_naroznik_zewnetrzny
    from .siatka import podzial
    from .wyniki import fmt_liczba as _f
    from .wyniki import oblicz_wezel
    out = []
    # 2 — szczeliny
    M = Material
    wyn = []
    for gap in (2e-7, 1e-4):
        ob = [Obszar(box(0, 0, 0.18, 1), M("SIL", 0.77)), Obszar(box(0.18 + gap, 0, 0.38, 1), M("EPS", 0.031))]
        st = strefy_z_dopelnienia(ob, box(-0.05, 0, 0.43, 1), [((-0.025, 0.5), _nas("i", 20, "wewn")),
                                                                ((0.405, 0.5), _nas("e", -18, "zewn"))])
        wz = Wezel("szczelina", "t", "t", ob, st, przekroj="poziomy")
        try:
            r = ModelMOS(wz, siatka_dla_wezla(wz)).rozwiaz()
            wyn.append(r.Phi_grup()["i"] / 38.0)
        except ValueError:
            wyn.append(None)
    U1 = 1 / (0.13 + 0.18 / 0.77 + 0.2 / 0.031 + 0.04)
    ok2 = wyn[0] is not None and abs(wyn[0] - U1) < 1e-4 and wyn[1] is None
    out.append(["2", "szczelina między wielobokami 0,2 µm / 0,1 mm (ściana SIL 18 + EPS 20)",
                f"0,2 µm → U_2D = {_f(wyn[0], 4)} (1D: {_f(U1, 4)}; przyciąganie do 1 µm); 0,1 mm → "
                + ("ValueError (szczelina wykryta)" if wyn[1] is None else f"U_2D = {_f(wyn[1], 4)} — NIE WYKRYTO"), ok2])
    # 5 — podział długich odcinków
    try:
        e = podzial(0.0, 20.0, 0.003, 0.003, 1.25, 2)
        out.append(["5", "podzial(0; 20 m; h = 3 mm)", f"{len(e) - 1} komórek, max {_f(max(e[1:] - e[:-1]) * 1000, 3)}"
                    " mm (wcześniej OverflowError)", True])
    except OverflowError:   # pragma: no cover
        out.append(["5", "podzial(0; 20 m; h = 3 mm)", "OverflowError", False])
    # 3 — θ_si,min w wierzchołku (naroże słabo ocieplone: cegła 25 cm + EPS 5 cm, R_si = 0,25)
    wl = [Warstwa(M("TG", 0.4), 0.015), Warstwa(M("CEG", 0.77), 0.25, True), Warstwa(M("EPS", 0.04), 0.05)]
    wz = wezel_naroznik_zewnetrzny(wl, theta_i=20, theta_e=-18)
    t_def = ModelMOS(wz, siatka_dla_wezla(wz), "fRsi").rozwiaz().theta_si_min()[0]
    t_fin = ModelMOS(wz, siatka_dla_wezla(wz, h_min=0.00025), "fRsi").rozwiaz().theta_si_min()[0]
    out.append(["3", "θ_si,min naroża wewn. (h_min 2 mm vs 0,25 mm; odniesienie 10,737 °C)",
                f"{_f(t_def, 3)} / {_f(t_fin, 3)} °C (wcześniej 10,810 / 10,747 — środki ścian komórek)",
                abs(t_def - 10.737) < 0.02 and abs(t_fin - 10.737) < 0.01])
    # 4 — płaskownik stalowy w izolacji (ψ małe — różnica dużych liczb)
    ins, pl = M("INS", 0.035), M("PL", 50.0)
    ob = [Obszar(box(0, 0, 0.5, 0.2), ins), Obszar(box(0, 0, 0.001, 0.2), pl)]
    st = [Strefa("i", box(0, -0.05, 0.5, 0), 20.0, "wewn", "i", Rs=0.13),
          Strefa("e", box(0, 0.2, 0.5, 0.25), -18.0, "zewn", "e", Rs=0.04)]
    fl = [ElementFlankujacy("izolacja", ("i", "e"), 0.5, 0.5, warstwy=[Warstwa(ins, 0.2)])]
    w = oblicz_wezel(Wezel("fin", "płaskownik", "t", ob, st, fl, przekroj="poziomy"))
    d = (w.psi_glowne.psi_e - PSI_FIN_REF) / PSI_FIN_REF
    out.append(["4", "płaskownik stalowy 2 mm przez izolację 0,2 m (półmodel), ψ vs niezależny solver 0,03472",
                f"ψ = {_f(w.psi_glowne.psi_e, 5)} ({_f(100 * d, 1, znak=True)} %; wcześniej −1,5 % po akceptacji siatki), "
                f"siatki {', '.join(str(h[1]) for h in w.siatki)}, zbieżność Φ i ψ: {w.zbieznosc_ok}",
                abs(d) < 0.01 and w.zbieznosc_ok])
    # 7 — przegroda wentylowana w attyce → błąd; 'legary' nie są pustką wentylowaną
    wd = [Warstwa(Material("DESKOW", 0.13), 0.025),
          Warstwa(Material("PW", 0.5, "pustka wentylowana", rodzaj="powietrze_went"), 0.05),
          Warstwa(Material("PIR", 0.022), 0.2), Warstwa(Material("ZB", 2.3), 0.2, True)]
    try:
        wezel_attyka(wl, wd)
        ok7 = False
    except ValueError:
        ok7 = True
    out.append(["7", "attyka z warstwą dobrze wentylowaną", "ValueError (wariant nieobsługiwany — brak niespójności "
                "U/2D)" if ok7 else "brak błędu", ok7])
    return out


def raport_walidacji(wyniki: list[WynikWalidacji] | None = None, plik: str | Path | None = None,
                     weryfikacja: bool = True) -> str:
    from .wyniki import fmt_liczba as f
    wyniki = wyniki or waliduj_wszystko()
    L = ["# Walidacja solvera mostków 2D (`lamela.obliczenia.mostki2d`) — PN-EN ISO 10211:2017 zał. C", "",
         "Metoda: objętości skończone na siatce prostokątnej zagęszczanej przy granicach materiałów, warunki Robina "
         "(h = 1/R_s), rozwiązanie bezpośrednie (scipy.sparse, SuperLU). Kryterium normy dla metody dokładnej 2D: "
         "temperatury ± 0,1 K, strumień ± 0,1 W/m.", "",
         "| Przypadek | Wynik | max. odchyłka θ [K] | odchyłka Φ [W/m] | Tolerancja |", "|---|---|---|---|---|"]
    for w in wyniki:
        L.append(f"| {w.nazwa} | {'**SPEŁNIA**' if w.ok else '**NIE SPEŁNIA**'} | "
                 f"{f(w.max_odch_T, 4) if w.max_odch_T is not None else '—'} | "
                 f"{f(w.odch_phi, 4) if w.odch_phi is not None else '—'} | {w.tolerancja} |")
    for w in wyniki:
        L += ["", f"## {w.nazwa}", "", f"Siatka: {w.siatka}", "",
              "| Punkt | Położenie | Odniesienie | Obliczono | Odchyłka |", "|---|---|---|---|---|"]
        for r in w.wiersze:
            L.append(f"| {r[0]} | {r[1]} | {f(r[2], 4)} | {f(r[3], 4)} | {f(r[4], 4, znak=True)} |")
        for u in w.uwagi:
            L.append(f"\n{u}")
    if weryfikacja:
        L += sekcja_weryfikacji()
    L += ["", "## Źródła danych referencyjnych", ""]
    L += [f"* {n}: {u}" for n, u in ZRODLA]
    L += ["", "Tekst PN-EN ISO 10211:2017 nie był dostępny; dane przypadków 1 i 2 odczytano z rysunków normy "
          "zamieszczonych w raporcie walidacyjnym Physibel i potwierdzono niezależnie (SimScale, QuickField — "
          "identyczne wymiary, λ, warunki i wyniki). Przed wydaniem PT zaleca się porównanie z egzemplarzem normy "
          "(PKN) [NZW — źródło wtórne].", ""]
    txt = "\n".join(L)
    if plik:
        Path(plik).parent.mkdir(parents=True, exist_ok=True)
        Path(plik).write_text(txt, encoding="utf-8")
    return txt


UWAGI_WERYFIKACJI = [
    ("1", "istotna", "Temperatura w wierzchołku siatki na styku materiałów (przypadek 2, punkt G: aluminium / drewno / "
     "korek) liczona jako średnia arytmetyczna rekonstrukcji z 4 komórek — 1. rząd, zależna od siatki (h_min = 0,5 mm: "
     "G = 16,108 °C, poza tolerancją).",
     "`Rozwiazanie.temperatura`: średnia rekonstrukcji ważona λ komórek (dla jednego materiału — bez zmian). "
     "Test regresji: przypadek 2 na siatkach h_min = 0,5 i 0,1 mm (tabela wyżej)."),
    ("2", "istotna", "Szczeliny między wielobokami szersze niż tolerancja scalania (10⁻⁷ m) stawały się pustkami "
     "adiabatycznymi bez ostrzeżenia; bilans energii tylko raportowany.",
     "(a) `siatka.kontroluj_pustki` — ValueError dla zamkniętych pustek wewnętrznych i dla ciągów komórek pustki "
     "ograniczonych z obu stron materiałem/strefą (położenie w komunikacie; `Wezel.dopusc_pustki` — wyjątek dla "
     "celowych wcięć); (b) współrzędne wierzchołków przyciągane do siatki 1 µm; (c) `oblicz_wezel` odrzuca "
     "rozwiązanie z bilansem ≥ 10⁻⁴ (ValueError)."),
    ("3", "drobna", "θ_si,min i f_Rsi tylko w środkach ścian komórek — zawyżone o O(h_min) w narożu wewnętrznym i na "
     "styku ościeża z ramą.",
     "`theta_si_min` sprawdza też wierzchołki łamanej powierzchni (naroża, końce łańcuchów) — temperatura z rekonstrukcji "
     "ważonej λ; współczynniki wagowe g (3 temperatury) w tym samym punkcie."),
    ("4", "drobna", "Cienkie warstwy dobrze przewodzące (blachy, obróbki) — ψ zbieżne tylko w 1. rzędzie; kryterium 1 % "
     "strumienia nie kontroluje błędu ψ.",
     "h_min ≤ grubość najcieńszego obszaru o λ ≥ 1; iloraz sąsiednich komórek na liniach granicznych ≤ 2; dodatkowe "
     "kryterium zbieżności |ΔL_2D| ≤ max(1 % |ψ|; 0,001 W/(m·K)) przy podwojeniu siatki (obok 1 % Φ wg ISO 10211)."),
    ("5", "drobna", "`podzial` — OverflowError dla długich odcinków przy małym h_max (r**k przed ograniczeniem).",
     "Wzrost komórek ograniczany przed potęgowaniem; resztę odcinka wypełniają komórki h_max liczone wprost."),
    ("6", "drobna", "Model gruntu i U podłogi (ISO 13370) z b = 8 m zamiast B' budynku.",
     "`katalog_z_modelu`: b = B' = A/(0,5·P) z obrysu zewnętrznego parteru (model testowy: 4,74 m) [INT]."),
    ("7", "drobna", "Attyka: warstwy dachu nad pustką wentylowaną w modelu 2D, a w U pominięte; „legary” "
     "klasyfikowane jako pustka.",
     "Rozróżnienie 'powietrze' (niewentylowana, λ_eq — w U i w 2D) i 'powietrze_went' (nazwa „…wentylowana” lub pole "
     "`wentylowana`); `wezel_attyka` z warstwą wentylowaną → ValueError (wariant nieobsługiwany); słowo „legar” nie "
     "decyduje o klasyfikacji."),
    ("8", "istotna", "System wymiarów ψ i H_TB niespójny z projektem (`energia.bryla`, `fizyka.mostki` — wymiary "
     "wewnętrzne całkowite, okna w świetle otworu w murze); H_TB = 9,28 W/K liczone z ψ_e.",
     "`ElementFlankujacy.l_oi`, `WynikPsi.psi_oi` (strop pośredni / wspornik / próg: ψ_oi = ψ_e — wysokości „od podłogi "
     "do podłogi”; attyka: ściana do spodu płyty; okna: ściana do krawędzi otworu w murze + korekta U_w·x0 pasa między "
     "krawędzią ramy a otworem); H_TB = Σ ψ_oi·l_oi z długościami w tym samym systemie; eksport "
     "`eksport_wynikow` → {id: {psi_oi, psi_e, psi_i, f_rsi, dlugosc(_oi), typ}} (czytany przez "
     "`fizyka.mostki.wczytaj_wyniki_symulacji` — pierwszeństwo psi_oi). Poprzednie H_TB = 9,28 W/K (ψ_e, długości "
     "zewn., w tym otwory wewnętrzne) — NIEPORÓWNYWALNE, wycofane."),
    ("9", "istotna", "Długość WZ-W1 obejmowała otwory w ścianach wewnętrznych/działowych; pominięte progi; nadproża i "
     "podokienniki liczone jak ościeże.",
     "`otwory_zewnetrzne` — tylko ściany o przegrodzie `sciana_zewn` (bez `typ: otwor`); nowe węzły 2D (przekroje "
     "pionowe): WZ-N1 nadproże, WZ-N2 nadproże z kasetą osłony w ociepleniu (otwory z żaluzją/screenem), WZ-P1 "
     "podokiennik z parapetem wewn. i obróbką zewn., WZ-T1 próg na płycie parteru (grunt), WZ-T2 próg okna do podłogi "
     "na stropie, WZ-T3 próg drzwi na płycie wspornikowej z łącznikiem; długości: ościeża 2·wys, nadproża/podokienniki/"
     "progi szer."),
]


def sekcja_weryfikacji() -> list[str]:
    """Sekcja raportu „Weryfikacja niezależna i poprawki” (uwagi weryfikatorów, poprawki, kontrole numeryczne)."""
    L = ["", "## Weryfikacja niezależna i poprawki", "",
         "Pakiet sprawdzili dwaj niezależni weryfikatorzy: (A) numeryczno-fizyczny — własny solver węzłowy MOS "
         "(vertex-centred), szereg Fouriera przypadku 1 (4001 wyrazów), testy skrajnych kontrastów λ, skalowania, "
         "szczelin, zbieżności katalogu; (B) zgodności z normami PN-EN ISO 10211:2017, 14683:2017, 13788:2013, "
         "6946:2017, 13370:2017 (próbki norm iTeh, dane przypadku 2 z QuickField/SimScale/Physibel). Potwierdzone bez "
         "zmian: przypadek 1 zbieżny w 2. rzędzie do rozwiązania Fouriera; przypadek 2 poza punktem G zgodny z "
         "niezależnym solverem do 0,005 K, Φ = 9,4904 vs 9,4917 W/m; bilans 10⁻¹⁵…3·10⁻⁹; średnia harmoniczna λ i "
         "warunki Robina (ściana 1D ze skrajnymi warstwami — błąd U ≤ 5·10⁻¹⁰); ΔS naroża 0,5587; kierunki R_si, "
         "R_si = 0,25 w przebiegu f_Rsi, długości l_e/l_i; brak pustek w węzłach katalogu; obszar gruntu i "
         "płaszczyzny odcięcia.", "",
         "| Nr | Waga | Uwaga weryfikatora | Poprawka |", "|---|---|---|---|"]
    for nr, waga, uw, pop in UWAGI_WERYFIKACJI:
        L.append(f"| {nr} | {waga} | {uw} | {pop} |")
    L += ["", "**Kontrole numeryczne poprawek** (uruchamiane przy generowaniu raportu):", "",
          "| Uwaga | Kontrola | Wynik | Ocena |", "|---|---|---|---|"]
    for nr, kontrola, wynik, ok in kontrole_poprawek():
        L.append(f"| {nr} | {kontrola} | {wynik} | {'**OK**' if ok else '**BŁĄD**'} |")
    L += ["", "Wynik punktu G przypadku 2 **zależał od siatki** przed poprawką 1 (tolerancja ± 0,1 K spełniona na siatce "
          "walidacyjnej h_min = 0,1 mm częściowo dzięki zaokrągleniu wartości odniesienia 16,3); po poprawce G = "
          "16,334 °C niezależnie od siatki (0,5 mm → 0,025 mm), zgodnie z niezależnym solverem. Odchyłki A (−0,036 K) "
          "i B (−0,039 K) są identyczne w obu solverach — wynikają z zaokrąglenia wartości odniesienia.", "",
          "Wpływ poprawek na katalog (model testowy): f_Rsi zmienia się o ≤ 0,002 (wierzchołki), ψ o ≤ 0,001 W/(m·K) "
          "(siatka), cokół WZ-GF1 z B' = 4,74 m: ψ_oi = ψ_i ≈ 0,21 zamiast 0,20 W/(m·K). Wszystkie węzły z ciągłą "
          "izolacją spełniają f_Rsi ≥ 0,72; wariant porównawczy WZ-B0 (płyta bez łącznika) — f_Rsi ≈ 0,746 "
          "(na granicy, ψ ≈ 0,75 W/(m·K))."]
    return L
