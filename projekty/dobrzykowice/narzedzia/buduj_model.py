#!/usr/bin/env python3
"""Generator modelu (budynek.yaml, wyposazenie.yaml, arkusze.yaml) bliźniaka w Dobrzykowicach — dz. 341/318.

Źródło geometrii: plik Projekt_wersja_15_10_2026.dwg (koncepcja, 15.10.2026; rysunek w cm), odczytany LibreDWG.
Rzuty są lustrzane względem osi ściany wspólnej, więc LOKAL 1 (od szczytu NW, Y ≈ 0…8,865) jest zdefiniowany jawnie,
a LOKAL 2 powstaje przez odbicie Y' = 17,730 − Y (numery pomieszczeń x.0y → x.1y).

Układ modelu (konwencja aihouse, docs/SCHEMAT_MODELU.md): metry; X — w poprzek budynku (front z wejściami X < 0, ogród
X > 10), Y — wzdłuż budynku; początek = przecięcie osi ściany frontowej (A) i szczytowej lokalu 1 (1); osie przez środek
warstwy konstrukcyjnej. Przeliczenie z DWG: X = (x − 3216,2)/100 (rzut piętra), X = (x − 1914,3)/100 (rzut parteru),
Y = (y − 4098,1)/100. Azymut osi +Y ≈ 150,9° (z mapy do celów projektowych: front budynku na NE, do drogi 341/305).

Drzwi: zawias i strona otwierania odtworzone z bloków drzwi w DWG; pola `strona`/`kierunek` dobierane tak, aby generator
rzutów (lamela.views.plan) narysował je tak samo (emulacja `_swing_side` i `_hinge`).

Użycie (z katalogu repozytorium):
    PYTHONPATH=src python3 projekty/dobrzykowice/narzedzia/buduj_model.py
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
OUT = Path(__file__).resolve().parents[1] / "model"

Y_MIR = 17.730          # 2 × 8,865 — oś odbicia = środek podwójnej ściany wspólnej
DATA = "2026-11-20"


def my(y):
    return round(Y_MIR - y, 4)


# ============================================================================ materiały i przegrody
MATERIALY = {
    "MUR24": {"nazwa": "Mur konstrukcyjny 24 cm — przyjęto bloczek silikatowy (do potwierdzenia)", "lambda": 0.77,
              "rho": 1800, "cp": 840, "mu": 15, "kreskowanie": "MUR_SILIKAT", "kolor": "#d9d4ca"},
    "MUR12": {"nazwa": "Ścianka działowa 12 cm — przyjęto bloczek silikatowy (do potwierdzenia)", "lambda": 0.77,
              "rho": 1800, "cp": 840, "mu": 15, "kreskowanie": "MUR_SILIKAT", "kolor": "#d9d4ca"},
    "EPS20": {"nazwa": "Ocieplenie 20 cm — przyjęto styropian EPS (do potwierdzenia)", "lambda": 0.031, "rho": 15,
              "cp": 1450, "mu": 30, "kreskowanie": "IZOL_TWARDA", "kolor": "#8f9296"},
    "KANAL": {"nazwa": "Kanały wentylacyjne / komin (pustaki systemowe — do ustalenia)", "lambda": 1.0, "rho": 1800,
              "cp": 840, "mu": 50, "kreskowanie": "BETON", "kolor": "#bdb8ae"},
    "BETON": {"nazwa": "Beton (płyta podłogi — przyjęto)", "lambda": 2.0, "rho": 2400, "cp": 1000, "mu": 130,
              "kreskowanie": "BETON", "kolor": "#b9b6ae"},
    "ZELBET": {"nazwa": "Żelbet (stropy — przyjęto)", "lambda": 2.3, "rho": 2500, "cp": 1000, "mu": 130,
               "kreskowanie": "ZELBET", "kolor": "#b9b6ae"},
    "JASTRYCH": {"nazwa": "Jastrych (przyjęto)", "lambda": 1.0, "rho": 2000, "cp": 1000, "mu": 50,
                 "kreskowanie": "JASTRYCH", "kolor": "#c9c5bb"},
    "EPS_POD": {"nazwa": "Izolacja termiczna podłogi (przyjęto)", "lambda": 0.035, "rho": 20, "cp": 1450, "mu": 60,
                "kreskowanie": "IZOL_TWARDA", "kolor": "#9cc7a4"},
    "EPS_AKU": {"nazwa": "Izolacja akustyczna (przyjęto)", "lambda": 0.040, "rho": 12, "cp": 1450, "mu": 30,
                "kreskowanie": "IZOL_TWARDA", "kolor": "#e9e7df"},
    "DU": {"nazwa": "do ustalenia", "lambda": 1.0, "rho": 2000, "cp": 1000, "mu": 50, "kreskowanie": "PLYTKI",
           "kolor": "#cfc9bf"},
}
PRZEGRODY = {
    "SZ1": {"nazwa": "Ściana zewnętrzna: mur 24 cm + ocieplenie 20 cm (warstwy wg DWG, materiały przyjęte)",
            "typ": "sciana_zewn",
            "warstwy": [{"mat": "MUR24", "d": 0.24, "konstrukcyjna": True}, {"mat": "EPS20", "d": 0.20}]},
    "SZ2": {"nazwa": "Filar przy wnęce wejściowej: ocieplenie 20 + mur 24 + ocieplenie 20 cm", "typ": "sciana_zewn",
            "warstwy": [{"mat": "EPS20", "d": 0.20}, {"mat": "MUR24", "d": 0.24, "konstrukcyjna": True},
                        {"mat": "EPS20", "d": 0.20}]},
    "SW1": {"nazwa": "Ściana wewnętrzna nośna / ściana lokalu przy ścianie wspólnej: mur 24 cm",
            "typ": "sciana_wewn_nosna", "warstwy": [{"mat": "MUR24", "d": 0.24, "konstrukcyjna": True}]},
    "SD1": {"nazwa": "Ścianka działowa 12 cm", "typ": "scianka_dzialowa",
            "warstwy": [{"mat": "MUR12", "d": 0.12, "konstrukcyjna": True}]},
    "POD-0": {"nazwa": "Podłoga na gruncie (grubości wg przekroju w DWG, materiały przyjęte)", "typ": "podloga_na_gruncie",
              "warstwy": [{"mat": "DU", "d": 0.02}, {"mat": "JASTRYCH", "d": 0.07}, {"mat": "EPS_POD", "d": 0.15},
                          {"mat": "BETON", "d": 0.20, "konstrukcyjna": True}]},
    "POD-1": {"nazwa": "Podłoga na stropie (warstwy nad płytą, przyjęte)", "typ": "strop",
              "warstwy": [{"mat": "DU", "d": 0.02}, {"mat": "JASTRYCH", "d": 0.06}, {"mat": "EPS_AKU", "d": 0.04}]},
}

# ============================================================================ geometria lokalu 1
# Ściany wspólne dla obu lokali (front, tył, ściana frontowa garaży) — bez odbicia.
SCIANY_WSPOLNE = [
    # parter
    dict(kond="P0", przegroda="SZ1", os=[[0.0, 4.885], [0.0, 12.845]], wnetrze="prawa", tag="front_garaze"),
    dict(kond="P0", przegroda="SZ1", os=[[10.24, 0.0], [10.24, Y_MIR]], wnetrze="lewa", tag="tyl"),
    # piętro
    dict(kond="P1", przegroda="SZ1", os=[[0.0, 0.0], [0.0, Y_MIR]], wnetrze="prawa", tag="front"),
    dict(kond="P1", przegroda="SZ1", os=[[10.24, 0.0], [10.24, Y_MIR]], wnetrze="lewa", tag="tyl"),
]
# Ściany lokalu 1 (odbijane do lokalu 2).
SCIANY_L1 = [
    # --- parter: obwód
    dict(kond="P0", przegroda="SZ1", os=[[0.883, 0.0], [10.24, 0.0]], wnetrze="lewa", tag="szczyt"),
    dict(kond="P0", przegroda="SZ1", os=[[0.883, 0.0], [0.883, 4.885]], wnetrze="prawa", tag="wneka"),
    dict(kond="P0", przegroda="SZ2", os=[[0.883, 0.0], [-0.32, 0.0]], wnetrze="srodek", tag="filar"),
    dict(kond="P0", przegroda="SZ1", os=[[0.883, 4.885], [0.0, 4.885]], wnetrze="prawa", tag="wneka_pn"),
    # --- parter: ściany nośne wewnętrzne
    dict(kond="P0", przegroda="SW1", os=[[0.883, 4.885], [5.84, 4.885]], wnetrze="srodek", tag="nosna_y"),
    dict(kond="P0", przegroda="SW1", os=[[5.84, 0.0], [5.84, 8.745]], wnetrze="srodek", tag="nosna_x"),
    dict(kond="P0", przegroda="SW1", os=[[0.0, 8.745], [10.24, 8.745]], wnetrze="srodek", tag="wspolna"),
    # --- parter: działowe
    dict(kond="P0", przegroda="SD1", os=[[0.883, 1.902], [5.84, 1.902]], wnetrze="srodek", tag="d_gosp_wc"),
    dict(kond="P0", przegroda="SD1", os=[[3.43, 0.0], [3.43, 1.902]], wnetrze="srodek", tag="d_gosp_wc_x"),
    dict(kond="P0", przegroda="SD1", os=[[3.654, 1.902], [3.654, 3.805]], wnetrze="srodek", tag="d_wiatrolap_x"),
    dict(kond="P0", przegroda="SD1", os=[[0.883, 3.805], [3.654, 3.805]], wnetrze="srodek", tag="d_wiatrolap_y"),
    # --- piętro: szczyt i ściana przy ścianie wspólnej
    dict(kond="P1", przegroda="SZ1", os=[[0.0, 0.0], [10.24, 0.0]], wnetrze="lewa", tag="szczyt"),
    dict(kond="P1", przegroda="SW1", os=[[0.0, 8.745], [10.24, 8.745]], wnetrze="srodek", tag="wspolna"),
    # --- piętro: działowe
    dict(kond="P1", przegroda="SD1", os=[[2.583, 0.0], [2.583, 3.805]], wnetrze="srodek", tag="p_lazienka_x"),
    dict(kond="P1", przegroda="SD1", os=[[2.583, 1.902], [5.412, 1.902]], wnetrze="srodek", tag="p_lazienka2_y"),
    dict(kond="P1", przegroda="SD1", os=[[5.412, 0.0], [5.412, 1.902]], wnetrze="srodek", tag="p_lazienka2_x"),
    dict(kond="P1", przegroda="SD1", os=[[0.0, 3.805], [6.496, 3.805]], wnetrze="srodek", tag="p_hol_pd"),
    dict(kond="P1", przegroda="SD1", os=[[0.0, 5.825], [4.36, 5.825]], wnetrze="srodek", tag="p_pokoj7_y"),
    dict(kond="P1", przegroda="SD1", os=[[4.36, 5.825], [4.36, 8.745]], wnetrze="srodek", tag="p_pokoj7_x"),
    dict(kond="P1", przegroda="SD1", os=[[4.36, 7.168], [6.496, 7.168]], wnetrze="srodek", tag="p_wneka_y"),
    dict(kond="P1", przegroda="SD1", os=[[6.496, 3.363], [6.496, 7.168]], wnetrze="srodek", tag="p_pokoje_x"),
    dict(kond="P1", przegroda="SD1", os=[[6.496, 3.363], [10.24, 3.363]], wnetrze="srodek", tag="p_sypialnia_y"),
    dict(kond="P1", przegroda="SD1", os=[[6.496, 5.825], [10.24, 5.825]], wnetrze="srodek", tag="p_pokoje_y"),
]

# Otwory: sciana=tag; odl liczone od pierwszego punktu osi; dla drzwi: zawias (a = koniec s0, b = s1) i strona otwierania
# względem normalnej lewej ściany (+1/−1) — odczytane z bloków drzwi w DWG (lokal 1).
O_L1 = [
    # parter
    dict(sciana="szczyt", kond="P0", symbol="OK1", typ="okno", odl=6.04, szer=1.40, wys=1.33, parapet=1.03),
    dict(sciana="wneka", kond="P0", symbol="DZ1", typ="drzwi_zewn", odl=2.613, szer=1.02, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1),
    dict(sciana="nosna_y", kond="P0", symbol="D1", typ="drzwi", odl=0.23, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1, uwaga="brak bloku drzwi w DWG — dodano"),
    dict(sciana="nosna_x", kond="P0", symbol="OT1", typ="otwor", odl=2.465, szer=2.30, wys=2.30, parapet=0.0),
    dict(sciana="d_gosp_wc", kond="P0", symbol="D2", typ="drzwi", odl=0.22, szer=0.90, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=-1, uwaga="brak bloku drzwi w DWG — dodano"),
    dict(sciana="d_gosp_wc", kond="P0", symbol="D1", typ="drzwi", odl=3.475, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1),
    dict(sciana="d_wiatrolap_x", kond="P0", symbol="D1", typ="drzwi", odl=0.819, szer=0.92, wys=2.10, parapet=0.0,
         zawias="b", strona_otw=-1),
    dict(sciana="d_wiatrolap_y", kond="P0", symbol="D1", typ="drzwi", odl=0.227, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1),
    # piętro
    dict(sciana="szczyt", kond="P1", symbol="O5", typ="okno", odl=5.823, szer=0.95, wys=1.40, parapet=0.90),
    dict(sciana="p_lazienka2_y", kond="P1", symbol="D1", typ="drzwi", odl=0.819, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1),
    dict(sciana="p_hol_pd", kond="P1", symbol="D1", typ="drzwi", odl=0.25, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=+1),
    dict(sciana="p_hol_pd", kond="P1", symbol="D3", typ="drzwi", odl=5.296, szer=0.98, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=-1),
    dict(sciana="p_pokoj7_y", kond="P1", symbol="D1", typ="drzwi", odl=1.71, szer=0.92, wys=2.10, parapet=0.0,
         zawias="b", strona_otw=+1),
    dict(sciana="p_pokoje_x", kond="P1", symbol="D1", typ="drzwi", odl=1.327, szer=0.92, wys=2.10, parapet=0.0,
         zawias="b", strona_otw=-1),
    dict(sciana="p_pokoje_x", kond="P1", symbol="D1", typ="drzwi", odl=2.629, szer=0.92, wys=2.10, parapet=0.0,
         zawias="a", strona_otw=-1),
]
# Otwory w ścianach wspólnych (front / tył): podane dla lokalu 1 w Y; dla lokalu 2 przeliczane odbiciem.
O_WSPOLNE_L1 = [
    # parter — front garaży (oś od Y = 4,885): brama
    dict(sciana="front_garaze", kond="P0", symbol="BR1", typ="brama", y0=5.675, szer=2.60, wys=2.25, parapet=0.0),
    # parter — tył
    dict(sciana="tyl", kond="P0", symbol="OP1", typ="okno", y0=0.823, szer=0.91, wys=2.39, parapet=0.0),
    dict(sciana="tyl", kond="P0", symbol="HS1", typ="drzwi_przesuwne_HS", y0=2.709, szer=3.00, wys=2.39, parapet=0.0),
    # piętro — front
    dict(sciana="front", kond="P1", symbol="O1", typ="okno", y0=2.41, szer=0.90, wys=1.40, parapet=0.85),
    dict(sciana="front", kond="P1", symbol="O2", typ="okno", y0=4.534, szer=1.00, wys=1.40, parapet=0.85),
    dict(sciana="front", kond="P1", symbol="O3", typ="okno", y0=6.546, szer=1.25, wys=1.40, parapet=0.85),
    # piętro — tył
    dict(sciana="tyl", kond="P1", symbol="O4", typ="okno", y0=0.823, szer=2.20, wys=1.40, parapet=0.85),
    dict(sciana="tyl", kond="P1", symbol="O2", typ="okno", y0=4.102, szer=1.00, wys=1.40, parapet=0.85),
    dict(sciana="tyl", kond="P1", symbol="O3", typ="okno", y0=6.375, szer=1.25, wys=1.40, parapet=0.85),
]

POMIESZCZENIA_L1 = [
    ("0.01", "P0", "Wiatrołap", (2.3, 2.85), "ruchu", False),
    ("0.02", "P0", "Pom. gospodarcze", (2.0, 0.9), "pomocnicza", False),
    ("0.03", "P0", "WC", (4.4, 1.0), "pomocnicza", False),
    ("0.04", "P0", "Hol ze schodami", (4.7, 2.9), "ruchu", False),
    ("0.05", "P0", "Garaż", (3.0, 7.0), "pomocnicza", False),
    ("0.06", "P0", "Salon z kuchnią i jadalnią", (8.0, 4.4), "podstawowa", True),
    ("1.01", "P1", "Hol", (3.0, 5.2), "ruchu", False),
    ("1.02", "P1", "Łazienka", (1.2, 1.6), "pomocnicza", False),
    ("1.03", "P1", "Sypialnia z garderobą", (7.8, 1.6), "podstawowa", True),
    ("1.04", "P1", "Łazienka przy sypialni", (4.4, 1.0), "pomocnicza", False),
    ("1.05", "P1", "Pokój", (8.3, 4.6), "podstawowa", True),
    ("1.06", "P1", "Pokój z garderobą", (8.3, 7.2), "podstawowa", True),
    ("1.07", "P1", "Pokój", (2.0, 7.2), "podstawowa", True),
]

# kanały wentylacyjne i komin (bryły przez obie kondygnacje) — z DWG (X, Y środka; wymiary w mm A×B)
SLUPY_L1 = [((3.085, 1.6615), "496x361"), ((5.5985, 1.6615), "243x361"), ((6.26, 8.4235), "600x403")]

WYPOSAZENIE_L1 = [
    # parter
    dict(kond="P0", typ="blat", linia=[[5.96, 2.47], [5.96, 0.12], [10.06, 0.12]], gl=0.60, strona=1, gorne=False),
    dict(kond="P0", typ="blat", linia=[[7.81, 1.74], [10.10, 1.74]], gl=0.65, strona=1, gorne=False),  # półwysep
    dict(kond="P0", typ="stol", xy=[8.815, 4.38], obrot=0, wym=[1.68, 0.93], krzesla=6),
    dict(kond="P0", typ="sofa", xy=[8.635, 8.625], obrot=270, wym=[2.33, 0.94]),
    dict(kond="P0", typ="sofa", xy=[10.12, 6.86], obrot=180, wym=[1.34, 1.02]),
    dict(kond="P0", typ="szafa", xy=[5.96, 6.695], obrot=0, wym=[1.47, 0.42]),
    dict(kond="P0", typ="wc", xy=[4.86, 0.12], obrot=90, wym=[0.45, 0.65]),
    dict(kond="P0", typ="umywalka", xy=[5.72, 1.095], obrot=180, wym=[0.60, 0.43]),
    dict(kond="P0", typ="szafa", xy=[2.795, 1.962], obrot=90, wym=[1.49, 0.56]),
    # piętro
    dict(kond="P1", typ="wanna", xy=[0.12, 1.24], obrot=0, wym=[2.16, 0.90]),
    dict(kond="P1", typ="wc", xy=[2.523, 0.97], obrot=180, wym=[0.45, 0.65]),
    dict(kond="P1", typ="pralka", xy=[2.523, 2.015], obrot=180, wym=[0.60, 0.60]),
    dict(kond="P1", typ="umywalka_blat", xy=[2.523, 3.01], obrot=180, wym=[1.38, 0.61]),
    dict(kond="P1", typ="wc", xy=[2.643, 0.965], obrot=0, wym=[0.45, 0.65]),
    dict(kond="P1", typ="umywalka", xy=[3.855, 0.12], obrot=90, wym=[0.81, 0.42]),
    dict(kond="P1", typ="prysznic", xy=[4.87, 0.12], obrot=90, wym=[0.88, 1.28]),
    dict(kond="P1", typ="lozko", xy=[8.375, 0.12], obrot=90, wym=[1.60, 2.00]),
    dict(kond="P1", typ="biurko", xy=[5.472, 0.86], obrot=0, wym=[0.92, 0.51]),
    dict(kond="P1", typ="szafa", xy=[2.643, 2.63], obrot=0, wym=[1.06, 0.53]),
    dict(kond="P1", typ="szafa", xy=[3.905, 3.745], obrot=270, wym=[2.41, 0.54]),
    dict(kond="P1", typ="szafa", xy=[3.54, 5.885], obrot=90, wym=[1.46, 0.54]),
    dict(kond="P1", typ="biurko", xy=[0.795, 8.625], obrot=270, wym=[1.19, 0.53]),
    dict(kond="P1", typ="lozko", xy=[4.30, 8.15], obrot=180, wym=[0.82, 1.96]),
    dict(kond="P1", typ="biurko", xy=[9.37, 3.423], obrot=90, wym=[1.22, 0.53]),
    dict(kond="P1", typ="sofa", xy=[9.145, 5.765], obrot=270, wym=[1.85, 0.66]),
    dict(kond="P1", typ="biurko", xy=[9.135, 5.885], obrot=90, wym=[1.21, 0.56]),
    dict(kond="P1", typ="lozko", xy=[10.12, 8.14], obrot=180, wym=[0.90, 2.00]),
    dict(kond="P1", typ="szafa", xy=[4.42, 7.915], obrot=0, wym=[1.31, 0.57]),
    dict(kond="P1", typ="szafa", xy=[5.475, 8.625], obrot=270, wym=[0.83, 0.35]),
]


# ============================================================================ budowa modelu
def mirror_wall(w):
    m = copy.deepcopy(w)
    m["os"] = [[p[0], my(p[1])] for p in w["os"]]
    m["wnetrze"] = {"lewa": "prawa", "prawa": "lewa"}.get(w["wnetrze"], w["wnetrze"])
    return m


def build():
    sciany, otwory, by_tag = [], [], {}
    nr = {"P0": 0, "P1": 0}

    def add_wall(w, lokal):
        k = w["kond"]
        nr[k] += 1
        wid = f"S{k[1]}-{nr[k]:02d}"
        rec = {"id": wid, "kond": k, "przegroda": w["przegroda"], "os": [[round(a, 4), round(b, 4)] for a, b in w["os"]],
               "wnetrze": w["wnetrze"], "z_od": None, "z_do": None}
        sciany.append(rec)
        by_tag[(k, w["tag"], lokal)] = rec
        return rec

    for w in SCIANY_WSPOLNE:
        add_wall(w, "W")
    for w in SCIANY_L1:
        add_wall(w, 1)
    for w in SCIANY_L1:
        add_wall(mirror_wall(w), 2)

    onr = {"P0": 0, "P1": 0}

    def add_opening(sc, o, odl, lokal, zawias=None, strona_otw=None):
        k = sc["kond"]
        onr[k] += 1
        rec = {"id": f"O{k[1]}-{onr[k]:02d}", "sciana": sc["id"], "symbol": o["symbol"], "typ": o["typ"],
               "odl": round(odl, 4), "szer": o["szer"], "wys": o["wys"], "parapet": o["parapet"]}
        if o["typ"] in ("okno",):
            rec["otwieranie"] = {"strona": "lewa", "kierunek": "do_wewn", "rodzaj": "RU"}
        if o["typ"] == "drzwi_przesuwne_HS":
            rec["otwieranie"] = {"strona": "prawa", "kierunek": "do_wewn", "rodzaj": "HS"}
        if zawias is not None:
            rec["otwieranie"] = {"strona": "lewa", "kierunek": "do_wewn", "rodzaj": "R"}
            rec["_zawias"], rec["_strona_otw"] = zawias, strona_otw
        otwory.append(rec)
        return rec

    # otwory w ścianach lokali
    for lokal in (1, 2):
        for o in O_L1:
            sc = by_tag[(o["kond"], o["sciana"], lokal)]
            so = o.get("strona_otw")
            if so is not None and lokal == 2:
                so = -so                     # odbicie zmienia stronę względem normalnej lewej ściany
            add_opening(sc, o, o["odl"], lokal, o.get("zawias"), so)
    # otwory w ścianach wspólnych (odl = odległość od pierwszego punktu osi)
    for lokal in (1, 2):
        for o in O_WSPOLNE_L1:
            sc = by_tag[(o["kond"], o["sciana"], "W")]
            y0 = o["y0"] if lokal == 1 else my(o["y0"] + o["szer"])
            odl = y0 - sc["os"][0][1]
            add_opening(sc, o, odl, lokal)

    pom = []
    for lokal in (1, 2):
        for pid, k, nazwa, pt, kat, pobyt in POMIESZCZENIA_L1:
            if lokal == 2:
                a, b = pid.split(".")
                pid = f"{a}.{int(b) + 10:02d}"
                pt = (pt[0], my(pt[1]))
            pom.append({"id": pid, "kond": k, "nazwa": nazwa, "punkt": [round(pt[0], 4), round(pt[1], 4)],
                        "wielobok": None, "kategoria": kat, "pobyt_ludzi": pobyt, "posadzka": "DU",
                        "sciany_wyk": "DU", "sufit": "DU"})

    slupy, n = [], 0
    for lokal in (1, 2):
        for (x, y), prz in SLUPY_L1:
            n += 1
            slupy.append({"id": f"SL{n}", "xy": [x, y if lokal == 1 else my(y)], "przekroj": prz, "mat": "KANAL",
                          "z_od": 0.0, "z_do": 5.85})

    obrys = [[-0.12, -0.12], [10.36, -0.12], [10.36, Y_MIR + 0.12], [-0.12, Y_MIR + 0.12]]
    otw_sch = [[1.38, 3.865], [5.18, 3.865], [5.18, 4.765], [1.38, 4.765]]
    otw_sch2 = [[x, my(y)] for x, y in reversed(otw_sch)]
    budynek = {
        "meta": {"nazwa": "Bliźniak — Dobrzykowice, dz. 341/318 (koncepcja, przerysowanie z DWG)", "wersja": "0.1",
                 "data": DATA},
        "uklad": {"zero_abs": 121.30, "azymut_osi_y": 150.9},
        "osie": {"x": {"A": 0.0, "B": 0.883, "C": 5.84, "D": 10.24},
                 "y": {"1": 0.0, "2": 4.885, "3": 8.745, "4": 8.985, "5": 12.845, "6": Y_MIR}},
        "kondygnacje": [
            {"id": "P0", "nazwa": "Parter", "rzedna": 0.0, "wys_kondygnacji": 3.06, "wys_w_swietle": 2.70,
             "podloga": "POD-0"},
            {"id": "P1", "nazwa": "Piętro", "rzedna": 3.06, "wys_kondygnacji": 2.79, "wys_w_swietle": 2.55,
             "podloga": "POD-1"},
        ],
        "materialy": MATERIALY,
        "przegrody": PRZEGRODY,
        "sciany": sciany,
        "otwory": otwory,
        "pomieszczenia": pom,
        "stropy": [
            {"id": "ST1", "nad": "P0", "wierzch": 2.94, "grubosc": 0.24, "obrys": obrys, "otwory": [otw_sch, otw_sch2],
             "podloga": "POD-1", "mat": "ZELBET"},
            {"id": "ST2", "nad": "P1", "wierzch": 5.85, "grubosc": 0.24, "obrys": obrys, "mat": "ZELBET"},
        ],
        "slupy": slupy,
        "schody": [
            {"id": "SCH1", "z_kond": "P0", "na_kond": "P1", "liczba_stopni": 17, "wys_stopnia": 0.18,
             "szer_stopnia": 0.26, "biegi": [{"start": [5.54, 4.315], "kierunek": [-1, 0], "szer": 0.90, "stopni": 17}]},
            {"id": "SCH2", "z_kond": "P0", "na_kond": "P1", "liczba_stopni": 17, "wys_stopnia": 0.18,
             "szer_stopnia": 0.26, "biegi": [{"start": [5.54, my(4.315)], "kierunek": [-1, 0], "szer": 0.90,
                                              "stopni": 17}]},
        ],
        "balustrady": [
            {"id": "BL1", "polilinia": [[1.38, 4.765, 3.06], [5.18, 4.765, 3.06], [5.18, 3.865, 3.06]], "wys": 1.10,
             "typ": "balustrada otworu schodowego (dodana — brak w DWG)"},
            {"id": "BL2", "polilinia": [[1.38, my(4.765), 3.06], [5.18, my(4.765), 3.06], [5.18, my(3.865), 3.06]],
             "wys": 1.10, "typ": "balustrada otworu schodowego (dodana — brak w DWG)"},
        ],
    }
    wypos = []
    for lokal in (1, 2):
        for it in WYPOSAZENIE_L1:
            r = copy.deepcopy(it)
            if lokal == 2:
                if r["typ"] == "blat":
                    r["linia"] = [[x, my(y)] for x, y in r["linia"]]
                    r["strona"] = -r["strona"]
                else:
                    r["xy"] = [r["xy"][0], my(r["xy"][1])]
                    r["obrot"] = (-r["obrot"]) % 360
            wypos.append(r)
    return budynek, wypos


# ============================================================================ drzwi: dobór strona/kierunek (emulacja plan.py)
def fix_doors(budynek_path: Path, budynek: dict):
    from shapely.geometry import Point
    from lamela.model import load_model
    m = load_model(budynek_path, None, strict=False)
    walls = {w.id: w for w in m.sciany()}
    rooms = {k: m.pomieszczenia(k) for k in ("P0", "P1")}

    def room_at(kond, pt):
        P = Point(float(pt[0]), float(pt[1]))
        for r in rooms[kond]:
            if r.polygon is not None and r.polygon.buffer(0.02).contains(P):
                return r
        return None

    door_cnt = {}
    for w in m.sciany():
        for o in w.otwory:
            if o.typ not in ("drzwi", "otwor", "drzwi_zewn", "drzwi_przesuwne_HS"):
                continue
            mid = (o.s0 + o.s1) / 2
            for t in (w.t_max + 0.35, w.t_min - 0.35):
                rr = room_at(w.kond, w.pt(mid, t))
                if rr is not None:
                    door_cnt[rr.id] = door_cnt.get(rr.id, 0) + 1

    def score(r):
        if r is None:
            return (9, 9, 0.0)
        return (door_cnt.get(r.id, 0), 1 if r.kategoria == "ruchu" else 0, r.pow_netto)

    log = []
    for rec in budynek["otwory"]:
        if "_zawias" not in rec:
            continue
        w = walls[rec["sciana"]]
        want_swing, want_hinge = rec.pop("_strona_otw"), rec.pop("_zawias")
        s0, s1 = rec["odl"], rec["odl"] + rec["szer"]
        if w.ext_side is not None:
            into = w.sgn_int
        else:
            mid = (s0 + s1) / 2
            rp, rm = room_at(w.kond, w.pt(mid, w.t_max + 0.35)), room_at(w.kond, w.pt(mid, w.t_min - 0.35))
            into = 1 if score(rp) <= score(rm) else -1
        kier = "do_wewn" if want_swing == into else "na_zewn"
        nsw = w.n * want_swing
        f = -nsw
        left = np.array([-f[1], f[0]])
        on_b = (w.u @ left) > 0
        hinge_lewa = "b" if on_b else "a"
        strona = "lewa" if hinge_lewa == want_hinge else "prawa"
        rec["otwieranie"] = {"strona": strona, "kierunek": kier, "rodzaj": "R"}
        log.append(f"{rec['id']} ({rec['sciana']}): zawias {want_hinge}, strona normalnej {want_swing:+d} → {strona}/{kier}")
    return log


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    budynek, wypos = build()
    bp = OUT / "budynek.yaml"
    hdr = ("# PLIK GENEROWANY: projekty/dobrzykowice/narzedzia/buduj_model.py — nie edytować ręcznie.\n"
           "# Bliźniak Dobrzykowice (dz. 341/318): geometria rzutów przerysowana z Projekt_wersja_15_10_2026.dwg;\n"
           "# materiały, wykończenia i część wysokości otworów PRZYJĘTE (w DWG brak opisów) — patrz README projektu.\n")

    def dump(path, data, header):
        txt = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=140, default_flow_style=None)
        path.write_text(header + txt, encoding="utf-8")

    tmp = copy.deepcopy(budynek)
    for o in tmp["otwory"]:
        o.pop("_zawias", None), o.pop("_strona_otw", None)
    dump(bp, tmp, hdr)                       # 1. przebieg — model do wyznaczenia pomieszczeń
    log = fix_doors(bp, budynek)             # 2. strona/kierunek drzwi wg DWG
    dump(bp, budynek, hdr)
    dump(OUT / "wyposazenie.yaml", {"wyposazenie": wypos},
         "# PLIK GENEROWANY (buduj_model.py) — wyposażenie wg DWG (symbole silnika lamela.views.plan).\n")
    print(f"Zapisano {bp} ({len(budynek['sciany'])} ścian, {len(budynek['otwory'])} otworów, "
          f"{len(budynek['pomieszczenia'])} pomieszczeń) i wyposazenie.yaml ({len(wypos)} elementów)")
    for line in log:
        print("  drzwi:", line)


if __name__ == "__main__":
    main()
