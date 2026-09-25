"""Dane tabelaryczne instalacji elektrycznych nN (przewody Cu, PVC 70 °C) i aparatury.

* **Obciążalność prądowa długotrwała I_z** — PN-HD 60364-5-52:2011 zał. B, tabl. B.52.2 (2 żyły obciążone)
  i B.52.4 (3 żyły obciążone), izolacja PVC, Cu, temp. żyły 70 °C, otoczenie 30 °C (w powietrzu) / 20 °C (w gruncie,
  ρ_gr = 2,5 K·m/W); sposoby ułożenia A1, A2, B1, B2, C, D1 (kabel w rurze w ziemi), D2 (bezpośrednio w ziemi), E.
  Wartości wg IEC 60364-5-52:2009 (literatura) — **[NZW]** (rejestr R7 Nierozstrz. 13).
* **Współczynniki poprawkowe** — tabl. B.52.14 (temperatura powietrza, PVC), B.52.15 (temperatura gruntu, PVC),
  B.52.17 (grupowanie — wiązki / przewody na powierzchni) [NZW].
* **Rezystancje żył Cu** klasy 1/2 w 20 °C [Ω/km] — PN-EN 60228 (R7-E08) [NZW]; α_Cu = 0,00393 1/K;
  reaktancja przewodów wielożyłowych ≈ 0,08 mΩ/m [W].
* **Wyłączniki nadprądowe** (PN-EN 60898-1): prąd zadziałania wyzwalacza elektromagnetycznego (górna granica)
  I_a = 5·I_n (B), 10·I_n (C), 20·I_n (D) — czas wyłączenia ≤ 0,1 s < 0,4 s; prąd zadziałania I₂ = 1,45·I_n
  (warunek I₂ ≤ 1,45·I_z sprowadza się do I_n ≤ I_z). Bezpieczniki gG: I₂ = 1,6·I_n (I_n ≥ 16 A).
"""
from __future__ import annotations

PRZEKROJE = [1.5, 2.5, 4.0, 6.0, 10.0, 16.0, 25.0, 35.0]
R20 = {1.5: 12.1, 2.5: 7.41, 4.0: 4.61, 6.0: 3.08, 10.0: 1.83, 16.0: 1.15, 25.0: 0.727, 35.0: 0.524}   # Ω/km
X_KABLA = 0.08e-3     # Ω/m
ALFA_CU = 0.00393

# I_z [A]: metoda → liczba żył obciążonych → {przekrój: I_z}
IZ = {
    "A1": {2: [14.5, 19.5, 26, 34, 46, 61, 80, 99], 3: [13.5, 18, 24, 31, 42, 56, 73, 89]},
    "A2": {2: [14, 18.5, 25, 32, 43, 57, 75, 92], 3: [13, 17.5, 23, 29, 39, 52, 68, 83]},
    "B1": {2: [17.5, 24, 32, 41, 57, 76, 101, 125], 3: [15.5, 21, 28, 36, 50, 68, 89, 110]},
    "B2": {2: [16.5, 23, 30, 38, 52, 69, 90, 111], 3: [15, 20, 27, 34, 46, 62, 80, 99]},
    "C": {2: [19.5, 27, 36, 46, 63, 85, 112, 138], 3: [17.5, 24, 32, 41, 57, 76, 96, 119]},
    "D1": {2: [22, 29, 37, 46, 60, 78, 99, 119], 3: [18, 24, 30, 38, 50, 64, 82, 98]},
    "D2": {2: [22, 28, 38, 48, 64, 83, 110, 132], 3: [19, 24, 33, 41, 54, 70, 92, 110]},
    "E": {2: [22, 30, 40, 51, 70, 94, 119, 148], 3: [18.5, 25, 34, 43, 60, 80, 101, 126]},
}
OPIS_METOD = {
    "A1": "przewody jednożyłowe w rurze w ścianie izolowanej cieplnie",
    "A2": "przewód wielożyłowy w rurze w ścianie izolowanej cieplnie",
    "B1": "przewody jednożyłowe w rurze na/w ścianie",
    "B2": "przewód wielożyłowy w rurze na/w ścianie (w stropie w rurze osłonowej)",
    "C": "przewód wielożyłowy bezpośrednio na ścianie / pod tynkiem (YDYp)",
    "D1": "kabel wielożyłowy w rurze osłonowej w ziemi",
    "D2": "kabel wielożyłowy bezpośrednio w ziemi",
    "E": "przewód wielożyłowy w powietrzu (korytko perforowane)",
}
K_TEMP_POWIETRZE = {10: 1.22, 15: 1.17, 20: 1.12, 25: 1.06, 30: 1.00, 35: 0.94, 40: 0.87, 45: 0.79, 50: 0.71}
K_TEMP_GRUNT = {10: 1.10, 15: 1.05, 20: 1.00, 25: 0.95, 30: 0.89}
K_GRUPOWANIE = {1: 1.00, 2: 0.80, 3: 0.70, 4: 0.65, 5: 0.60, 6: 0.57, 7: 0.54, 8: 0.52, 9: 0.50}
SZEREG_IN = [6, 10, 13, 16, 20, 25, 32, 40, 50, 63]
MNOZNIK_IA = {"B": 5.0, "C": 10.0, "D": 20.0}


def iz(metoda: str, n_obc: int, s: float) -> float:
    """I_z [A] z tablicy (bez współczynników poprawkowych)."""
    return float(IZ[metoda][3 if n_obc >= 3 else 2][PRZEKROJE.index(s)])


def k_temp(metoda: str, theta: float) -> float:
    tab = K_TEMP_GRUNT if metoda.startswith("D") else K_TEMP_POWIETRZE
    ks = sorted(tab)
    theta = min(max(theta, ks[0]), ks[-1])
    for a, b in zip(ks, ks[1:]):
        if a <= theta <= b:
            t = (theta - a) / (b - a)
            return tab[a] * (1 - t) + tab[b] * t
    return tab[ks[-1]]


def k_grup(n: int) -> float:
    return K_GRUPOWANIE.get(n, 0.45 if n >= 12 else 0.50)


def r_zyly(s: float, theta: float = 20.0) -> float:
    """Rezystancja żyły Cu [Ω/m] w temperaturze θ."""
    return R20[s] / 1000.0 * (1.0 + ALFA_CU * (theta - 20.0))
