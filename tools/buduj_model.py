#!/usr/bin/env python3
"""Parametryczny generator modelu „Dom LAMELA” — KONCEPCJA OSTATECZNA (synteza).

Baza: wariant W2 (ocena J1/J2 — średnia 72,7 pkt; W1 70,7; W3 66,0) + przeszczepy z W1/W3 + WSZYSTKIE poprawki
obowiązkowe sędziów J1–J3 (docs/20_koncepcja/ocena_J*.md). Jedno źródło prawdy: skrypt zapisuje
  model/budynek.yaml, model/dzialka.yaml, model/wyposazenie.yaml, model/instalacje.yaml
(schemat: docs/SCHEMAT_MODELU.md; rdzeń: src/lamela/model.py). Liczby w opisie koncepcji pochodzą z modelu
(tools/podglad_modelu.py → docs/20_koncepcja/final/bilans.md).

Uruchomienie:  python3 tools/buduj_model.py   (potem: PYTHONPATH=src python3 -m lamela.model model/budynek.yaml model/dzialka.yaml)

Układ: x → wschód, y → północ, z → góra; (0,0) = przecięcie osi A i 1; ±0,00 = posadzka P0 = 101,65 m n.p.m.
Moduł wymiarowy osi: 0,125 m (bloczki silikatowe 1/8-modułowe); otwory w wielokrotnościach 0,05 m (tam, gdzie możliwe);
współrzędne zaokrąglane do 0,005 m.
"""
from __future__ import annotations

import math
from pathlib import Path

import yaml
from shapely.geometry import Polygon, box
from shapely.geometry.polygon import orient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "model"

# =====================================================================================================================
# 1. PARAMETRY — osie, poziomy, grubości (wszystkie wymiary w m)
# =====================================================================================================================
X = {"A'": -1.120, "A": 0.000, "B": 3.875, "C": 5.875, "M": 7.190, "D": 8.500, "D'": 9.875, "E": 12.000,
     "P": 14.875, "F": 18.375}
Y = {"1": 0.000, "2": 2.875, "H": 3.750, "3": 5.125, "4": 8.750, "5": 9.375}

ZERO_ABS = 101.65                      # ±0,00 = posadzka P0 [m n.p.m., PL-EVRF2007-NH]
H_KOND = 3.15                          # wysokość kondygnacji P0, P1
PODL = 0.15                            # warstwy podłogi nad płytą (z ogrzewaniem podłogowym)
T_STR = 0.22                           # grubość stropów ST1, ST2 i płyty stropodachu P2
Z_P1, Z_P2 = 3.15, 6.30                # rzędne posadzek
Z_ST1, Z_ST2, Z_ST3 = Z_P1 - PODL, Z_P2 - PODL, 9.30   # wierzch płyt konstrukcyjnych
Z_DG = 3.00                            # wierzch płyty dachu garażu / pasa gospodarczego (= ST1)
T_DG = 0.24                            # grubość płyty dachu garażu (dwukierunkowa 6,375 × 6,50 m)
Z_PLYTA_F = -PODL                      # wierzch płyty fundamentowej (−0,15)
T_PLYTA_F = 0.25

# połowa grubości ścian od osi (warstwa konstrukcyjna 0,18 m + wykończenia)
KZ = 0.09          # połowa warstwy konstrukcyjnej 18 cm
EXT = 0.30         # lico zewnętrzne SZ1/SZ2 od osi: 0,09 + 0,20 + 0,01
INT = 0.105        # lico wewnętrzne ściany 18 cm od osi (0,09 + tynk 0,015)
FD = 0.075         # lico ścianki działowej 12 cm (0,06 + 0,015)
GAR = 0.22         # lico ściany dom–garaż od strony garażu (0,09 + wełna 0,12 + tynk 0,01)

# lica wykończone używane w rzutach / pomieszczeniach
XA_i, XE_i = X["A"] + INT, X["E"] - INT                      # 0,105 / 11,895
Y1_i, Y3_s, Y3_n, Y4_i = Y["1"] + INT, Y["3"] - INT, Y["3"] + INT, Y["4"] - INT   # 0,105 / 5,02 / 5,23 / 8,645
XC_w, XC_e = X["C"] - INT, X["C"] + INT                      # 5,77 / 5,98
XD_w, XD_e = X["D"] - INT, X["D"] + INT                      # 8,395 / 8,605
XM_w, XM_e = X["M"] - 0.06, X["M"] + 0.06                    # 7,13 / 7,25 (ścianka środkowa 12 cm, bez tynku — silikat licowy)

# schody (identyczne SCH1 i SCH2, jedne nad drugimi) — WT §68–69, W-090/W-091
H_ST, S_ST, N_BIEG = 0.175, 0.28, 9                       # h, s, liczba podnóżków w biegu
Y_SCH0 = Y3_n                                              # pierwszy podnóżek (lico ściany osi 3 od pn.)
Y_SPOCZ = round(Y_SCH0 + (N_BIEG - 1) * S_ST, 4)          # krawędź spocznika (7,47)
B1_X0, B1_X1 = XC_e, XM_w                                  # bieg 1 (pas zachodni) 5,98–7,13 = 1,15 m
B2_X0, B2_X1 = XM_e, XD_w                                  # bieg 2 (pas wschodni) 7,25–8,395 = 1,145 m

# szacht instalacyjny SI (pion K1 Ø110, RS1/RS2 DN100, kanały reku) — w świetle 0,40 × 1,12 m
SI = (5.370, Y3_n, 5.770, 6.350)

# poziomy elementów zewnętrznych (krawędzie płyt — „warstwy” sylwety S)
Z_OKAP_E = (2.75, 3.05)        # okap E (ST1) — płyta pogrubiona 30 cm
Z_RAMA_D = (3.65, 3.85)        # linia D: dolny pas ramy C = wierzch attyki garażu +3,85
Z_RAMA_G = (5.35, 5.55)        # górny pas ramy C
Z_OKAP_2 = (5.95, 6.25)        # krawędź ST2 (spód bryły A)
Z_OKAP_3 = (9.08, 9.40)        # krawędź ST3 (stropodach bryły A)


def r(v: float, n: int = 4) -> float:
    v = round(float(v), n)
    return 0.0 if v == 0 else v


def P(*pts) -> list:
    """Wielobok CCW z zaokrągleniem."""
    poly = orient(Polygon(pts), 1.0)
    c = list(poly.exterior.coords)[:-1]
    return [[r(x), r(y)] for x, y in c]


def R(x0, y0, x1, y1) -> list:
    return P((x0, y0), (x1, y0), (x1, y1), (x0, y1))


def seg_len(p1, p2) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


# =====================================================================================================================
# 2. MATERIAŁY — λ obliczeniowa [W/(m·K)], ρ [kg/m³], c_p [J/(kg·K)], μ [-] (albo sd [m] dla membran)
#    Źródła wartości typowych: PN-EN ISO 10456:2009 tab. 3 i 4 (wartości projektowe materiałów budowlanych),
#    PN-EN 1745:2012 zał. A (wyroby murowe), deklaracje właściwości użytkowych (DWU) typowych wyrobów danej klasy
#    — „lub równoważne”; przed PT zastąpić DWU wybranych wyrobów. Kreskowania: kody silnika (SCHEMAT p. 5.4).
# =====================================================================================================================
MAT = [
    # --- konstrukcja
    ("ZB_C25", dict(nazwa="Żelbet C25/30, B500SP (stropy, płyta fundamentowa, ściany)", **{"lambda": 2.30}, rho=2400, cp=1000, mu=130,
                    kreskowanie="ZELBET", kolor="#b9b6ae", ciezar=25.0), "PN-EN ISO 10456 tab. 3: beton zbrojony 1 % stali λ 2,3; μ 80/130"),
    ("ZB_C30", dict(nazwa="Żelbet C30/37 XC4/XF1 (krawędzie płyt wysuniętych, attyki, belki)", **{"lambda": 2.50}, rho=2500, cp=1000, mu=130,
                    kreskowanie="ZELBET", kolor="#b4b1a9", ciezar=25.0), "PN-EN ISO 10456 tab. 3: beton zbrojony 2 % stali λ 2,5"),
    ("SIL18", dict(nazwa="Bloczek wapienno-piaskowy (silikat) 18 cm, kl. 20, gr. 1, na zaprawie cienkowarstwowej", **{"lambda": 0.90}, rho=1800, cp=1000, mu=15,
                   kreskowanie="MUR_SILIKAT", kolor="#d9d4ca", ciezar=18.0), "PN-EN 1745 zał. A (ρ 1800, P=50 %) λ ≈ 0,8–1,0 → 0,90 z zapasem; μ 5/25 (PN-EN ISO 10456)"),
    ("SIL12", dict(nazwa="Bloczek wapienno-piaskowy 12 cm, kl. 15 (ścianki działowe, licowy w klatce)", **{"lambda": 0.90}, rho=1800, cp=1000, mu=15,
                   kreskowanie="MUR_SILIKAT", kolor="#dcd7cd", ciezar=18.0), "jw."),
    ("STAL_S355", dict(nazwa="Stal konstrukcyjna S355 (słupy RK, rama boksu C), cynkowana ogniowo + malowana proszkowo RAL 7016", **{"lambda": 50.0},
                       rho=7850, cp=450, mu=1000000, kreskowanie="STAL", kolor="#383e42", ciezar=78.5), "PN-EN ISO 10456 tab. 3: stal λ 50"),
    ("RAMA_C", dict(nazwa="Rama boksu C: ruszt stalowy ocynkowany w okładzinie z blachy aluminiowej RAL 7016 (pusta w środku)", **{"lambda": 50.0},
                    rho=1200, cp=450, mu=1000000, kreskowanie="STAL", kolor="#3b4044", ciezar=6.0), "lekka rama — przeszczep J2 z W1; ρ zastępcza przekroju"),
    ("DREWNO_KVH", dict(nazwa="Drewno konstrukcyjne KVH C24 (szkielet lekkiej ściany A')", **{"lambda": 0.13}, rho=450, cp=1600, mu=50,
                        kreskowanie="DREWNO_POPRZ", kolor="#c9a36b", ciezar=4.2), "PN-EN ISO 10456 tab. 3: drewno iglaste 450 kg/m³ λ 0,12–0,13; μ 20/50"),
    # --- izolacje
    ("EPS031", dict(nazwa="Styropian grafitowy EPS 031 (ETICS, NRO w systemie)", **{"lambda": 0.031}, rho=15, cp=1450, mu=40, kreskowanie="IZOL_TWARDA",
                    kolor="#8f9296", funkcja="izolacja"), "DWU typowego EPS 70-031 (PN-EN 13163); μ 20–40 → 40"),
    ("EPS038", dict(nazwa="Styropian podłogowy EPS 100-038 (pod jastrychem)", **{"lambda": 0.038}, rho=18, cp=1450, mu=40, kreskowanie="IZOL_TWARDA",
                    kolor="#ececec", funkcja="izolacja"), "DWU typowego EPS 100 (PN-EN 13163)"),
    ("EPS_T", dict(nazwa="Styropian elastyfikowany EPS T (akustyczny, pod jastrychem)", **{"lambda": 0.040}, rho=12, cp=1450, mu=20, kreskowanie="IZOL_TWARDA",
                   kolor="#f1efe6", funkcja="izolacja"), "DWU typowego EPS T 30 (PN-EN 13163)"),
    ("XPS300", dict(nazwa="Polistyren ekstrudowany XPS 300 (pod płytą fundamentową, cokół, izolacja obwodowa)", **{"lambda": 0.036}, rho=32, cp=1450, mu=150,
                    kreskowanie="IZOL_XPS", kolor="#9cc7a4", funkcja="izolacja"), "DWU typowego XPS 300 λ_D 0,034–0,036 (PN-EN 13164); w gruncie przyjęto 0,036"),
    ("PIR022", dict(nazwa="Płyty PIR z okładziną (izolacja spadkowa stropodachów)", **{"lambda": 0.022}, rho=32, cp=1400, mu=60, kreskowanie="IZOL_PIR",
                    kolor="#d8c98a", funkcja="izolacja"), "DWU typowego PIR (PN-EN 13165) λ_D 0,022"),
    ("WELNA_FAS", dict(nazwa="Wełna mineralna fasadowa (elewacja wentylowana bryły A, A1)", **{"lambda": 0.035}, rho=60, cp=1030, mu=1, kreskowanie="IZOL_MIEKKA",
                       kolor="#e7d9a2", funkcja="izolacja"), "DWU typowej wełny fasadowej (PN-EN 13162) λ_D 0,034–0,035"),
    ("WELNA_035", dict(nazwa="Wełna mineralna 035 (szkielet, docieplenia, ściana dom–garaż)", **{"lambda": 0.035}, rho=40, cp=1030, mu=1, kreskowanie="IZOL_MIEKKA",
                       kolor="#efe3b0", funkcja="izolacja"), "PN-EN 13162, DWU typowego wyrobu"),
    # --- membrany i warstwy funkcyjne
    ("PAROIZ_AL", dict(nazwa="Paroizolacja bitumiczna z wkładką Al (na płycie stropodachów)", **{"lambda": 0.23}, rho=1100, cp=1000, sd=1500.0, mu=375000,
                       kreskowanie="PAROIZOLACJA", kolor="#3a3a3a", funkcja="paroizolacja"), "DWU typowej papy paroizolacyjnej z Al, sd ≥ 1500 m"),
    ("MEMB_TPO", dict(nazwa="Membrana dachowa TPO 1,5 mm, mocowana mechanicznie (hydroizolacja stropodachów)", **{"lambda": 0.20}, rho=1000, cp=1000, mu=100000,
                      kreskowanie="IZOL_PRZECIWWODNA", kolor="#6e7275", funkcja="hydroizolacja"), "DWU typowej membrany TPO; μ ~ 10⁵"),
    ("PAPA_SBS", dict(nazwa="Hydroizolacja 2 × papa SBS (podkładowa + wierzchniego krycia, dach zielony)", **{"lambda": 0.23}, rho=1100, cp=1000, mu=20000,
                      kreskowanie="IZOL_PRZECIWWODNA", kolor="#2f3032", funkcja="hydroizolacja"), "PN-EN 13707, DWU; PN-EN ISO 10456 tab. 4 bitum λ 0,23"),
    ("BARIERA_KORZ", dict(nazwa="Bariera przeciwkorzenna PE-HD 0,5 mm (PN-EN 13948)", **{"lambda": 0.40}, rho=950, cp=1800, mu=100000,
                          kreskowanie="TWORZYWO", kolor="#1f4f35", funkcja="bariera_korzenna"), "PN-EN ISO 10456: PE-HD λ 0,40"),
    ("MEMB_SBS_POD", dict(nazwa="Izolacja przeciwwilgociowa i przeciwradonowa: membrana SBS 4 mm na płycie fundamentowej", **{"lambda": 0.23}, rho=1100, cp=1000,
                          mu=20000, kreskowanie="IZOL_PRZECIWWILGOCIOWA", kolor="#2f3032", funkcja="przeciwwilgociowa"), "PN-EN 13969, DWU"),
    ("FOLIA_PE", dict(nazwa="Folia PE 0,2 mm (warstwa rozdzielająca)", **{"lambda": 0.33}, rho=950, cp=1800, mu=100000, kreskowanie="PAROIZOLACJA",
                      kolor="#5d6d7e", funkcja="paroizolacja"), "PN-EN ISO 10456: PE λ 0,33"),
    ("MEMB_WIATR", dict(nazwa="Membrana fasadowa wiatroizolacyjna UV-stabilna, czarna (sd ≈ 0,02 m)", **{"lambda": 0.17}, rho=600, cp=1000, sd=0.02, mu=40,
                        kreskowanie="MEMBRANA_PAROPRZEP", kolor="#1d1d1d", funkcja="wiatroizolacja"), "DWU typowej membrany fasadowej UV (PN-EN 13859-2)"),
    ("MEMB_PAROSZ", dict(nazwa="Membrana paroszczelna (warstwa szczelności powietrznej w ścianie szkieletowej), sd ≥ 10 m", **{"lambda": 0.17}, rho=600, cp=1000,
                         sd=10.0, mu=25000, kreskowanie="PAROIZOLACJA", kolor="#2e7d32", funkcja="paroizolacja"), "PN-EN 13984, DWU"),
    ("MATA_DREN", dict(nazwa="Mata drenażowo-retencyjna HDPE 25 mm (dach zielony)", **{"lambda": 0.50}, rho=80, cp=1800, mu=1, kreskowanie="TWORZYWO",
                       kolor="#4a4a4a", funkcja="drenaz"), "DWU typowej maty drenażowej (pustki — λ zastępcza, poza obliczeniem U)"),
    ("GEOWL", dict(nazwa="Geowłóknina filtracyjna PP 150 g/m²", **{"lambda": 0.50}, rho=150, cp=1800, mu=1, kreskowanie="TWORZYWO", kolor="#bdbdbd",
                   funkcja="geowloknina"), "PN-EN 13252, DWU"),
    ("WLOKN_OCHR", dict(nazwa="Włóknina ochronna PP 300 g/m²", **{"lambda": 0.50}, rho=150, cp=1800, mu=1, kreskowanie="TWORZYWO", kolor="#a7a7a7",
                        funkcja="geowloknina"), "PN-EN 13252, DWU"),
    ("SUBSTRAT", dict(nazwa="Substrat ekstensywny 8 cm z matą rozchodnikową (sedum)", **{"lambda": 0.80}, rho=1100, cp=1500, mu=5, kreskowanie="HUMUS",
                      kolor="#6d8b3a", funkcja="substrat", ciezar=14.0), "FLL / DWU typowego substratu; ciężar w stanie nasyconym ≈ 1,4 t/m³"),
    ("ZWIR_16", dict(nazwa="Żwir płukany 16/32 mm (balast dachu P1, opaska przy attyce)", **{"lambda": 2.00}, rho=1700, cp=1000, mu=1, kreskowanie="ZWIR",
                     kolor="#bdb6a4", ciezar=17.0), "PN-EN ISO 10456 tab. 3: żwir λ 2,0"),
    ("PIASEK", dict(nazwa="Podsypka piaskowa zagęszczona (I_s ≥ 0,98)", **{"lambda": 2.00}, rho=1900, cp=1000, mu=50, kreskowanie="PIASEK",
                    kolor="#d8c7a0"), "PN-EN ISO 10456 tab. 3: piasek λ 2,0"),
    ("PUSTKA_WENT", dict(nazwa="Pustka wentylowana 40 mm (ruszt lamel)", **{"lambda": 0.25}, rho=1.2, cp=1000, mu=1, kreskowanie="POSPOLKA",
                         kolor="#ffffff"), "PN-EN ISO 6946 p. 6.9: pustka dobrze wentylowana — warstwy zewnętrzne pomijane, R_se = R_si"),
    # --- wykończenia
    ("TYNK_GIPS", dict(nazwa="Tynk gipsowy maszynowy 1,5 cm", **{"lambda": 0.40}, rho=1200, cp=1000, mu=10, kreskowanie="TYNK", kolor="#f3f1ec"),
     "PN-EN ISO 10456 tab. 3: tynk gipsowy 1200 kg/m³ λ 0,43 → 0,40 (DWU)"),
    ("TYNK_CW", dict(nazwa="Tynk cementowo-wapienny 1,5 cm (garaż, pom. techniczne)", **{"lambda": 0.82}, rho=1850, cp=1000, mu=15, kreskowanie="TYNK",
                     kolor="#e9e6df"), "PN-EN 1745 / PN-EN ISO 10456: zaprawa 1800 kg/m³ λ 0,82"),
    ("TYNK_SIL", dict(nazwa="ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (biały / jasnoszary NCS S 1500-N)", **{"lambda": 0.80}, rho=1700, cp=1000, mu=50,
                      kreskowanie="TYNK", kolor="#f5f4f0"), "DWU typowego systemu ETICS (ETA)"),
    ("GK", dict(nazwa="Płyta gipsowo-kartonowa 12,5 mm (GKB / GKBI w łazienkach)", **{"lambda": 0.25}, rho=700, cp=1000, mu=10, kreskowanie="PLYTA_GK",
                kolor="#eeeeee"), "PN-EN ISO 10456 tab. 3: płyta gipsowa λ 0,25"),
    ("OSB", dict(nazwa="Płyta OSB/3 15 mm (usztywnienie i warstwa szczelności ściany A')", **{"lambda": 0.13}, rho=600, cp=1700, mu=200,
                 kreskowanie="PLYTA_DREWNOPOCHODNA", kolor="#d8b27a"), "PN-EN ISO 10456 tab. 3: OSB 650 kg/m³ λ 0,13; μ 30/50 (przyjęto 200 — DWU)"),
    ("DWD16", dict(nazwa="Płyta drewnopochodna wiatroizolacyjna DWD/MDF.RWH 16 mm", **{"lambda": 0.10}, rho=550, cp=1700, mu=11,
                   kreskowanie="PLYTA_DREWNOPOCHODNA", kolor="#b7925c"), "DWU typowej płyty DWD λ 0,10, μ 11"),
    ("JASTRYCH", dict(nazwa="Jastrych cementowy CT-C25-F5 z wężownicą ogrzewania podłogowego", **{"lambda": 1.20}, rho=2000, cp=1000, mu=50,
                      kreskowanie="JASTRYCH", kolor="#c9c5bb", ciezar=22.0), "PN-EN ISO 10456 tab. 3: jastrych 2000 kg/m³ λ 1,35 → 1,20 (DWU)"),
    ("DESKA_DEB", dict(nazwa="Deska warstwowa dębowa 15 mm, klejona", **{"lambda": 0.18}, rho=700, cp=1600, mu=50, kreskowanie="DREWNO_WZDL",
                       kolor="#b58a5a"), "PN-EN ISO 10456 tab. 3: drewno liściaste 700 kg/m³ λ 0,18"),
    ("GRES", dict(nazwa="Płytki gresowe 60×120 na kleju C2TE S1", **{"lambda": 1.30}, rho=2300, cp=840, mu=200, kreskowanie="PLYTKI",
                  kolor="#cfc9bf"), "PN-EN ISO 10456 tab. 3: ceramika λ 1,3"),
    ("HYDRO_PODPL", dict(nazwa="Hydroizolacja podpłytkowa (masa uszczelniająca + taśmy), strefy mokre", **{"lambda": 0.20}, rho=1400, cp=1000, mu=3000,
                         kreskowanie="IZOL_PRZECIWWODNA", kolor="#3f7fbf", funkcja="hydroizolacja"), "PN-EN 14891, DWU"),
    ("PLYTKI_SC", dict(nazwa="Płytki ścienne ceramiczne (łazienki, WC, pralnia — do 2,0 m / do sufitu w natryskach)", **{"lambda": 1.30}, rho=2300, cp=840,
                       mu=200, kreskowanie="PLYTKI", kolor="#e3ded6"), "jw."),
    ("ZYWICA", dict(nazwa="Posadzka żywiczna epoksydowa antypoślizgowa R11 (garaż)", **{"lambda": 0.20}, rho=1400, cp=1000, mu=10000,
                    kreskowanie="TWORZYWO", kolor="#8c8f91"), "DWU typowej posadzki żywicznej"),
    ("SUF_GK", dict(nazwa="Sufit podwieszany GK (strefy kanałów wentylacji)", **{"lambda": 0.25}, rho=700, cp=1000, mu=10, kreskowanie="PLYTA_GK",
                    kolor="#f2f2f2"), "jw. GK"),
    ("PODSUF", dict(nazwa="Podsufitka zewnętrzna: płyta włóknocementowa 12 mm na ruszcie, RAL 7016", **{"lambda": 0.35}, rho=1500, cp=1000, mu=50,
                    kreskowanie="PLYTA_GK", kolor="#474b4f"), "DWU typowej płyty włóknocementowej"),
    ("SZKLO_VSG", dict(nazwa="Ścianka szklana VSG 2 × 8 mm w ramie aluminiowej (wiatrołap / hol)", **{"lambda": 1.00}, rho=2500, cp=750, mu=1000000,
                       kreskowanie="SZKLO", kolor="#bcd9e6"), "PN-EN ISO 10456 tab. 3: szkło λ 1,0"),
    # --- elewacja, zagospodarowanie
    ("DREWNO_TERMO", dict(nazwa="Lamele elewacyjne 40×80 mm, drewno termojesion (klasa 1 trwałości), olejowane", **{"lambda": 0.13}, rho=600, cp=1600, mu=50,
                          kreskowanie="DREWNO_POPRZ", kolor="#9b6b41", pbr={"kolor": "#9b6b41", "szorstkosc": 0.8, "tekstura": "drewno"}),
     "PN-EN ISO 10456 tab. 3: drewno 600 kg/m³ λ 0,13 (lamele poza izolacją — bez wpływu na U)"),
    ("DAB_LAMELA", dict(nazwa="Lamele dębowe 30×60 mm (ekran komunikacji P0, h 2,10 m)", **{"lambda": 0.18}, rho=700, cp=1600, mu=50,
                        kreskowanie="DREWNO_POPRZ", kolor="#b58a5a"), "jw."),
]


# =====================================================================================================================
# 3. PRZEGRODY — ściany: od WNĘTRZA do ZEWNĄTRZ; poziome: od GÓRY do DOŁU (brief §9: pełne warstwy, „4 linie”)
# =====================================================================================================================
def L(mat, d, **kw):
    return dict(mat=mat, d=d, **kw)


PRZ = {
    # ---------------- ściany
    "SZ1": dict(nazwa="Ściana zewnętrzna nośna: silikat 18 + ETICS EPS 031 20 cm (U ≈ 0,15)", typ="sciana_zewn", warstwy=[
        L("TYNK_GIPS", 0.015, funkcja="szczelnosc_powietrzna"), L("SIL18", 0.18, konstrukcyjna=True), L("EPS031", 0.20), L("TYNK_SIL", 0.010)]),
    "SZ2": dict(nazwa="Ściana zewnętrzna bryły A (P2) za lamelami: silikat 18 + wełna fasadowa 20 cm + membrana UV-stabilna (czarna); "
                      "szczelina wentylowana ok. 11 cm i lamele na ruszcie — element `lamele` (U ≈ 0,16)", typ="sciana_zewn", warstwy=[
        L("TYNK_GIPS", 0.015, funkcja="szczelnosc_powietrzna"), L("SIL18", 0.18, konstrukcyjna=True), L("WELNA_FAS", 0.20),
        L("MEMB_WIATR", 0.010)]),
    "SZL": dict(nazwa="Ściana zewnętrzna lekka A' (na wsporniku P2): szkielet KVH 45×200 z wełną + OSB (szczelność) + DWD + membrana UV + "
                      "pustka wentylowana; bez funkcji nośnej dla stropodachu (U ≈ 0,15)", typ="sciana_zewn", warstwy=[
        L("GK", 0.025), L("WELNA_035", 0.05, frakcje=[{"mat": "WELNA_035", "udzial": 0.9}, {"mat": "DREWNO_KVH", "udzial": 0.1}]),
        L("OSB", 0.015, funkcja="paroizolacja"),
        L("WELNA_035", 0.20, konstrukcyjna=True, frakcje=[{"mat": "WELNA_035", "udzial": 0.88}, {"mat": "DREWNO_KVH", "udzial": 0.12}]),
        L("DWD16", 0.016), L("WELNA_FAS", 0.060), L("MEMB_WIATR", 0.004)]),
    "SW18": dict(nazwa="Ściana wewnętrzna nośna: silikat 18, tynk gipsowy obustronnie", typ="sciana_wewn_nosna", warstwy=[
        L("TYNK_GIPS", 0.015), L("SIL18", 0.18, konstrukcyjna=True), L("TYNK_GIPS", 0.015)]),
    "SWZB": dict(nazwa="Ściana wewnętrzna nośna żelbetowa 18 cm (trzon klatki na P0 — usztywnienie w kierunku x, J2)", typ="sciana_wewn_nosna", warstwy=[
        L("TYNK_GIPS", 0.015), L("ZB_C25", 0.18, konstrukcyjna=True), L("TYNK_GIPS", 0.015)]),
    "SWG": dict(nazwa="Ściana nośna dom–garaż nieogrzewany: silikat 18 + wełna 12 cm od strony garażu + tynk (U ≈ 0,24 ≤ 0,30; szczelna na spaliny)",
                typ="sciana_wewn_nosna", warstwy=[
        L("TYNK_GIPS", 0.015), L("SIL18", 0.18, konstrukcyjna=True), L("WELNA_035", 0.12), L("TYNK_CW", 0.01)]),
    "SC12": dict(nazwa="Ścianka środkowa klatki schodowej: silikat 12 licowy (P0–P2)", typ="scianka_dzialowa", warstwy=[
        L("SIL12", 0.12, konstrukcyjna=True)]),
    "DZ12": dict(nazwa="Ścianka działowa: silikat 12 + tynk gipsowy obustronnie (R'w ≥ 45 dB)", typ="scianka_dzialowa", warstwy=[
        L("TYNK_GIPS", 0.015), L("SIL12", 0.12, konstrukcyjna=True), L("TYNK_GIPS", 0.015)]),
    "GK10": dict(nazwa="Obudowa szachtu SI: 2 × GKF 12,5 + profil CW 50 z wełną + 2 × GKF 12,5 (EI 30)", typ="scianka_dzialowa", warstwy=[
        L("GK", 0.025), L("WELNA_035", 0.05, konstrukcyjna=True), L("GK", 0.025)]),
    "SGL": dict(nazwa="Ścianka szklana wiatrołap/hol: VSG w ramie aluminiowej z drzwiami szklanymi 0,90 m", typ="scianka_dzialowa", warstwy=[
        L("SZKLO_VSG", 0.05, konstrukcyjna=True)]),
    "AT1": dict(nazwa="Attyka: żelbet 18 cm (wieniec podniesiony), izolacja z 3 stron (EPS 031 10 cm od dachu, ETICS od zewnątrz, PIR 4 cm na koronie), "
                      "obróbka blacharska ze spadkiem do dachu, wywinięcie membrany ≥ 0,15 m", typ="attyka", warstwy=[
        L("PIR022", 0.10), L("ZB_C30", 0.18, konstrukcyjna=True), L("EPS031", 0.20), L("TYNK_SIL", 0.005)]),
    # ---------------- podłogi i stropy (warstwy nad płytą = 0,15 m)
    "POD-0": dict(nazwa="Podłoga na płycie fundamentowej (P0): deska/gres, jastrych z ogrzewaniem podł., EPS 100, membrana SBS (przeciwwilgociowa, "
                        "przeciwradonowa), płyta ŻB 25 cm, XPS 300 20 cm, folia PE, podsypka (U ≈ 0,14)", typ="podloga_na_gruncie", warstwy=[
        L("DESKA_DEB", 0.015), L("JASTRYCH", 0.065), L("EPS038", 0.065), L("MEMB_SBS_POD", 0.005), L("ZB_C25", 0.25, konstrukcyjna=True),
        L("XPS300", 0.20), L("FOLIA_PE", 0.0002), L("PIASEK", 0.20)]),
    "POD-0L": dict(nazwa="Podłoga na płycie (P0) — łazienki, WC, przedsionek, pom. techniczne: gres na hydroizolacji podpłytkowej", typ="podloga_na_gruncie",
                   warstwy=[L("GRES", 0.012), L("HYDRO_PODPL", 0.003), L("JASTRYCH", 0.065), L("EPS038", 0.065), L("MEMB_SBS_POD", 0.005),
                            L("ZB_C25", 0.25, konstrukcyjna=True), L("XPS300", 0.20), L("FOLIA_PE", 0.0002), L("PIASEK", 0.20)]),
    "POD-G": dict(nazwa="Posadzka garażu (nieogrzewany): żywica R11 na warstwie wyrównawczej, spadek 1,5 % do bramy, płyta ŻB 25 cm na XPS 20 cm",
                  typ="podloga_na_gruncie", warstwy=[
        L("ZYWICA", 0.003), L("JASTRYCH", 0.047), L("ZB_C25", 0.25, konstrukcyjna=True), L("XPS300", 0.20), L("FOLIA_PE", 0.0002), L("PIASEK", 0.20)]),
    "POD-1": dict(nazwa="Strop międzykondygnacyjny: deska dębowa, jastrych z ogrzewaniem podł., EPS 100, EPS T (akustyczny), płyta ŻB 22 cm, tynk",
                  typ="strop", warstwy=[
        L("DESKA_DEB", 0.015), L("JASTRYCH", 0.065), L("EPS038", 0.040), L("EPS_T", 0.030), L("ZB_C25", 0.22, konstrukcyjna=True), L("TYNK_GIPS", 0.010)]),
    "POD-1L": dict(nazwa="Strop międzykondygnacyjny — łazienki, WC, pralnia: gres na hydroizolacji podpłytkowej", typ="strop", warstwy=[
        L("GRES", 0.012), L("HYDRO_PODPL", 0.003), L("JASTRYCH", 0.065), L("EPS038", 0.040), L("EPS_T", 0.030), L("ZB_C25", 0.22, konstrukcyjna=True),
        L("TYNK_GIPS", 0.010)]),
    "SUF-ZEW": dict(nazwa="Sufit pod stropem nad powietrzem zewnętrznym (wspornik bryły A): wełna 20 cm na kołkach + podsufitka włóknocementowa "
                          "na ruszcie z pustką wentylowaną (U stropu ≈ 0,15)", typ="strop", warstwy=[
        L("WELNA_035", 0.20, konstrukcyjna=True), L("PUSTKA_WENT", 0.04, pustka="dw"), L("PODSUF", 0.012)]),
    "SUF-G": dict(nazwa="Docieplenie spodu stropu garażu pasem 1,0 m przy ścianach osi E i 2 (wełna 10 cm + płyta) — ograniczenie mostka (J2)",
                  typ="strop", warstwy=[L("WELNA_035", 0.10, konstrukcyjna=True), L("TYNK_CW", 0.01)]),
    # ---------------- dachy (dach ciepły, izolacja spadkowa — wartość d = średnia klina)
    "SD1": dict(nazwa="Stropodach bryły A (P2): membrana TPO, PIR spadkowy 12–32 cm (śr. 22), paroizolacja z Al, płyta ŻB 22 cm, tynk; "
                      "spadek ≥ 2 % do wpustów WP1/WP2 (U ≈ 0,10)", typ="stropodach", warstwy=[
        L("MEMB_TPO", 0.002), L("PIR022", 0.22, klin={"d_min": 0.12, "d_max": 0.32, "ksztalt": "prostokat"}), L("PAROIZ_AL", 0.004),
        L("ZB_C25", 0.22, konstrukcyjna=True), L("TYNK_GIPS", 0.010)]),
    "SD2": dict(nazwa="Stropodach nad P1 (pola pn. poza bryłą A): żwir 5 cm, włóknina, membrana TPO, PIR spadkowy 14–26 cm, paroizolacja, płyta ŻB 22 cm "
                      "(U ≈ 0,11)", typ="stropodach", warstwy=[
        L("ZWIR_16", 0.05), L("WLOKN_OCHR", 0.004), L("MEMB_TPO", 0.002), L("PIR022", 0.20, klin={"d_min": 0.14, "d_max": 0.26, "ksztalt": "prostokat"}),
        L("PAROIZ_AL", 0.004), L("ZB_C25", 0.22, konstrukcyjna=True), L("TYNK_GIPS", 0.010)]),
    "DZ1": dict(nazwa="Dach zielony ekstensywny NIEUŻYTKOWY nad garażem (pom. nieogrzewane) i pasem gospodarczym: substrat 8 cm, geowłóknina, mata "
                      "drenażowa, włóknina, bariera przeciwkorzenna, 2 × papa SBS, PIR spadkowy 12–24 cm, paroizolacja, płyta ŻB 24 cm "
                      "(dwukierunkowa); opaska żwirowa 0,5 m przy attykach i wpustach (U ≈ 0,12)", typ="stropodach", warstwy=[
        L("SUBSTRAT", 0.080), L("GEOWL", 0.002), L("MATA_DREN", 0.025), L("WLOKN_OCHR", 0.004), L("BARIERA_KORZ", 0.0005), L("PAPA_SBS", 0.0095),
        L("PIR022", 0.18, klin={"d_min": 0.12, "d_max": 0.24, "ksztalt": "prostokat"}), L("PAROIZ_AL", 0.004), L("ZB_C25", 0.24, konstrukcyjna=True)]),
    "OK1": dict(nazwa="Płyta wysunięta (okap, daszek, krawędź ST2/ST3): obróbka/membrana ze spadkiem 2 % od budynku, płyta ŻB C30/37 z łącznikiem "
                      "termoizolacyjnym (ETA), podsufitka z okapnikiem", typ="taras", warstwy=[
        L("MEMB_TPO", 0.002), L("ZB_C30", 0.30, konstrukcyjna=True), L("PODSUF", 0.012)]),
}


# =====================================================================================================================
# 4. ŚCIANY — oś = środek warstwy konstrukcyjnej; ściany zewnętrzne obiegane CCW (wnętrze po lewej)
# =====================================================================================================================
SC: list[dict] = []


def W(sid, kond, prz, p1, p2, wn="srodek", uwagi=None, z_od=None, z_do=None):
    d = {"id": sid, "kond": kond, "przegroda": prz, "os": [[r(p1[0]), r(p1[1])], [r(p2[0]), r(p2[1])]], "wnetrze": wn,
         "z_od": z_od, "z_do": z_do}
    if uwagi:
        d["uwagi"] = uwagi
    SC.append(d)
    return d


xA, xA2, xB, xC, xM, xD, xD2, xE, xP, xF = (X[k] for k in ("A", "A'", "B", "C", "M", "D", "D'", "E", "P", "F"))
y1, y2, yH, y3, y4, y5 = (Y[k] for k in ("1", "2", "H", "3", "4", "5"))
Y_GP = 6.425        # ścianka przedpokój gościnny / łazienka gościnna (P0)
Y_HW = 6.625        # ścianka hol / WC + wiatrołap (P0)
Y_SI = 6.400        # ścianka pn. szachtu SI (P1, P2)
X_SI = 5.320        # ścianka zach. szachtu SI
X_BG = 3.575        # ścianka sypialnia / garderoba (P2)
Y_TH = 2.625        # ścianka pom. techn. / hol (P2)

# ---- P0 (parter): część mieszkalna 12,00 × 8,75 m w osiach + garaż z pasem gospodarczym 6,375 × 9,375 m (oś E–F)
W("S0-01", "P0", "SZ1", (xA, y1), (xE, y1), "lewa", "fasada pd. strefy dziennej — przeszklenie E (5 kwater) na słupach SL1–SL4 + belka B1")
W("S0-02", "P0", "SZ1", (xE, y1), (xF, y1), "lewa", "ściana pd. pasa gospodarczego (bryła G, pełna) z drzwiami gospodarczymi w systemie fasady E")
W("S0-03", "P0", "SZ1", (xF, y1), (xF, y5), "lewa", "ściana wsch. garażu = pion D (narożnik 18,975 m od lica zach. bryły B)")
W("S0-04", "P0", "SZ1", (xF, y5), (xE, y5), "lewa", "ściana pn. garażu z bramą segmentową")
W("S0-05", "P0", "SZ1", (xE, y5), (xE, y4), "lewa", "odcinek zach. garażu (przy daszku wejścia)")
W("S0-06", "P0", "SZ1", (xE, y4), (xA, y4), "lewa", "ściana pn. — wejście główne, okno łazienki gościnnej")
W("S0-07", "P0", "SZ1", (xA, y4), (xA, y1), "lewa", "ściana zach. — drzwi HS na taras zach., okno pokoju gościnnego")
W("S0-08", "P0", "SW18", (xA, y3), (xC, y3), uwagi="ściana grzbietowa (oś 3), odcinek zach.")
W("S0-09", "P0", "DZ12", (xM, y3), (xD, y3), uwagi="ścianka spiżarni pod biegiem 2 (strop nad nią — belka B8 w osi 3)")
W("S0-10", "P0", "SW18", (xD, y3), (xE, y3), uwagi="ściana grzbietowa (oś 3), odcinek wsch. — otwór hol/strefa dzienna")
W("S0-11", "P0", "SW18", (xB, y3), (xB, y4), uwagi="oś B")
W("S0-12", "P0", "SWZB", (xC, y3), (xC, y4), uwagi="oś C — ściana trzonu klatki, żelbet (sztywność P0 w kier. x)")
W("S0-13", "P0", "SWZB", (xD, y3), (xD, y4), uwagi="oś D — ściana trzonu klatki, żelbet")
W("S0-14", "P0", "SC12", (xM, y3), (xM, Y_SPOCZ), uwagi="ścianka środkowa schodów")
W("S0-15", "P0", "SW18", (xE, y1), (xE, y2), uwagi="oś E — kuchnia / przedsionek gospodarczy")
W("S0-16", "P0", "SWG", (xE, y2), (xE, y4), "lewa", "oś E — dom / garaż (izolacja od garażu, szczelna)")
W("S0-17", "P0", "SWG", (xF, y2), (xE, y2), "lewa", "oś 2 — pas gospodarczy / garaż (izolacja od garażu, szczelna)")
W("S0-18", "P0", "DZ12", (xP, y1), (xP, y2), uwagi="przedsionek / pom. techniczne")
W("S0-19", "P0", "DZ12", (xB, Y_GP), (xC, Y_GP), uwagi="przedpokój gościnny / łazienka gościnna")
W("S0-20", "P0", "DZ12", (xD, Y_HW), (xD2, Y_HW), uwagi="hol / WC")
W("S0-21", "P0", "SGL", (xD2, Y_HW), (xE, Y_HW), uwagi="przeszklona ścianka wiatrołap / hol z drzwiami szklanymi (przeszczep z W3)")
W("S0-22", "P0", "DZ12", (xD2, Y_HW), (xD2, y4), uwagi="WC / wiatrołap")
W("S0-23", "P0", "GK10", (X_SI, y3), (X_SI, Y_GP), uwagi="obudowa szachtu SI")

# ---- P1 (I piętro — bryła B)
W("S1-01", "P1", "SZ1", (xA, y1), (xE, y1), "lewa", "ściana pd. bryły B na belce B1; boks C (3 kwatery) w ramie")
W("S1-02", "P1", "SZ1", (xE, y1), (xE, y4), "lewa", "ściana wsch. (oś E)")
W("S1-03", "P1", "SZ1", (xE, y4), (xA, y4), "lewa", "ściana pn.")
W("S1-04", "P1", "SZ1", (xA, y4), (xA, y1), "lewa", "ściana zach. — okna pokoi dzieci")
W("S1-05", "P1", "SW18", (xA, y3), (xC, y3), uwagi="oś 3, odcinek zach.")
W("S1-06", "P1", "SW18", (xD, y3), (xE, y3), uwagi="oś 3, odcinek wsch. (między C i D — otwarcie klatki, belka B9)")
W("S1-07", "P1", "SW18", (xB, y3), (xB, y4), uwagi="oś B")
W("S1-08", "P1", "SW18", (xC, y3), (xC, y4), uwagi="oś C — klatka")
W("S1-09", "P1", "SW18", (xD, y3), (xD, y4), uwagi="oś D — klatka")
W("S1-10", "P1", "SC12", (xM, y3), (xM, Y_SPOCZ), uwagi="ścianka środkowa schodów")
W("S1-11", "P1", "DZ12", (xA, yH), (xE, yH), uwagi="hol / pokój dziecka 1 i pokój rodzinny")
W("S1-12", "P1", "DZ12", (xB, y1), (xB, yH), uwagi="pokój dziecka 1 / pokój rodzinny")
W("S1-13", "P1", "DZ12", (xD2, y3), (xD2, y4), uwagi="WC z natryskiem / pralnia (nad ścianką S0-22)")
W("S1-14", "P1", "GK10", (X_SI, y3), (X_SI, Y_SI), uwagi="obudowa szachtu SI")
W("S1-15", "P1", "GK10", (X_SI, Y_SI), (xC, Y_SI), uwagi="obudowa szachtu SI")

# ---- P2 (II piętro — bryła A w lamelach, wspornik 1,12 m w osi / 1,00 m lico–lico na zachód; nadbudowa B–D od pn.)
W("S2-01", "P2", "SZ2", (xA2, y1), (xE, y1), "lewa", "ściana pd. bryły A za lamelami; odc. A'–A na wsporniku (belka B4)")
W("S2-02", "P2", "SZ2", (xE, y1), (xE, y3), "lewa", "ściana wsch. bryły A za lamelami")
W("S2-03", "P2", "SZ1", (xE, y3), (xD, y3), "lewa", "ściana pn. bryły A nad dachem P1 (pole wsch.)")
W("S2-04", "P2", "SZ1", (xD, y3), (xD, y4), "lewa", "nadbudowa klatki i łazienki — ściana wsch.")
W("S2-05", "P2", "SZ1", (xD, y4), (xB, y4), "lewa", "nadbudowa — ściana pn. (okno klatki, okno łazienki)")
W("S2-06", "P2", "SZ1", (xB, y4), (xB, y3), "lewa", "nadbudowa — ściana zach.")
W("S2-07", "P2", "SZ1", (xB, y3), (xA2, y3), "lewa", "ściana pn. bryły A nad dachem P1 (pole zach.); odc. A'–A na wsporniku (belka B5)")
W("S2-08", "P2", "SZL", (xA2, y3), (xA2, y1), "lewa", "ściana zach. lekka na wsporniku (belka krawędziowa B3), za lamelami")
W("S2-09", "P2", "SW18", (xB, y3), (xM, y3), uwagi="oś 3 — łazienka / garderoba; zamknięcie pustki nad biegiem 1")
W("S2-10", "P2", "SW18", (xC, y3), (xC, y4), uwagi="oś C — klatka")
W("S2-11", "P2", "SC12", (xM, y3), (xM, Y_SPOCZ), uwagi="ścianka środkowa schodów (do stropodachu)")
W("S2-12", "P2", "DZ12", (X_BG, y1), (X_BG, y3), uwagi="sypialnia / garderoba")
W("S2-13", "P2", "DZ12", (xC, y1), (xC, y3), uwagi="garderoba / hol i pom. techniczne")
W("S2-14", "P2", "DZ12", (xD, y1), (xD, y3), uwagi="hol / gabinet")
W("S2-15", "P2", "DZ12", (xC, Y_TH), (xD, Y_TH), uwagi="pom. techniczne / hol")
W("S2-16", "P2", "GK10", (X_SI, y3), (X_SI, Y_SI), uwagi="obudowa szachtu SI")
W("S2-17", "P2", "GK10", (X_SI, Y_SI), (xC, Y_SI), uwagi="obudowa szachtu SI")


# =====================================================================================================================
# 5. OTWORY — położenie podawane w układzie globalnym (zakres x dla ścian równoległych do x, zakres y — do y);
#    odl liczona od punktu początkowego osi ściany. Otwór ≥ 0,10 m od lica ściany prostopadłej (SCHEMAT p. 5.2).
#    Drzwi do pokoi/łazienek/WC: otwór w murze ≥ 0,90 × 2,10 m (≥ 0,80 × 2,00 w świetle ościeżnicy — WT §75, §79, J1);
#    łazienki i WC otwierane NA ZEWNĄTRZ lub przesuwne, z kratką/podcięciem ≥ 0,022 m² (WT §79, W-059).
# =====================================================================================================================
OT: list[dict] = []
_SC = {s["id"]: s for s in SC}


def O(oid, sid, a, b, typ, sym, wys, parapet=0.0, otw=None, oslona=None, **kw):
    s = _SC[sid]
    (x1, y1_), (x2, y2_) = s["os"]
    if abs(y2_ - y1_) < 1e-9:          # ściana równoległa do x
        c1, c2 = x1, x2
    else:
        c1, c2 = y1_, y2_
    lo, hi = min(a, b), max(a, b)
    odl = (lo - c1) if c2 > c1 else (c1 - hi)
    d = {"id": oid, "sciana": sid, "symbol": sym, "typ": typ, "odl": r(odl), "szer": r(hi - lo), "wys": r(wys), "parapet": r(parapet)}
    if otw:
        d["otwieranie"] = otw
    if oslona:
        d["oslona"] = oslona
    d.update(kw)
    OT.append(d)
    return d


def ow(rodzaj="R", kierunek="do_wewn", strona="lewa", **kw):
    return {"strona": strona, "kierunek": kierunek, "rodzaj": rodzaj, **kw}


HS = ow("HS", "do_wewn", "prawa")
RU = ow("RU")
# ---- P0 — przeszklenie E: kwatery 1,90 / 1,90 / 2,335 / 2,335 / 2,93 (x 0,30–2,20–4,10–6,435–8,77–11,70); słupy SL1–SL4 w osiach
#      podziałów; SL3/SL4 w jednej linii ze słupkami boksu C (przeszczep J2); HS w kwaterach 3 i 4 (bezprogowe)
E_KW = [0.30, 2.20, 4.10, 6.435, 8.77, 11.70]
O("O0-01", "S0-01", E_KW[0], E_KW[1], "fix", "FX1", 2.75, 0.0, oslona="screen_zip", uwagi="przeszklenie E — kwatera 1")
O("O0-02", "S0-01", E_KW[1], E_KW[2], "fix", "FX1", 2.75, 0.0, oslona="screen_zip", uwagi="przeszklenie E — kwatera 2")
O("O0-03", "S0-01", E_KW[2], E_KW[3], "drzwi_przesuwne_HS", "HS1", 2.75, 0.0, HS, "screen_zip", bezprogowe=True, uwagi="kwatera 3 — HS salon")
O("O0-04", "S0-01", E_KW[3], E_KW[4], "drzwi_przesuwne_HS", "HS1", 2.75, 0.0, HS, "screen_zip", bezprogowe=True, uwagi="kwatera 4 — HS jadalnia")
O("O0-05", "S0-01", E_KW[4], E_KW[5], "fix", "FX2", 2.75, 0.0, oslona="screen_zip", uwagi="przeszklenie E — kwatera 5 (kuchnia)")
O("O0-06", "S0-02", 12.35, 13.25, "drzwi_zewn", "DZ3", 2.75, 0.0, ow("R", "na_zewn"), "screen_zip",
  uwagi="drzwi gospodarcze przeszklone w systemie i podziale fasady E (przeszczep J2) — pas E czytany ≈ 12,85 m; pod okapem E")
O("O0-07", "S0-04", 12.75, 17.75, "brama", "BR1", 2.25, -0.10, ow("segmentowa", "do_wewn"),
  uwagi="brama segmentowa 5,00 × 2,25 m w świetle, kratki went. ≥ 0,08 m² (W-111, W-115); posadzka garażu −0,10")
O("O0-08", "S0-03", 4.90, 5.90, "drzwi_zewn", "DZ2", 2.10, 0.0, ow("R", "na_zewn"), uwagi="drzwi boczne garażu (rowery, ogród) — 5,70 m od granicy E")
O("O0-09", "S0-06", 10.05, 11.15, "drzwi_zewn", "DZ1", 2.40, 0.0, ow("R", "do_wewn", "prawa"),
  uwagi="drzwi wejściowe 1,10 × 2,40 w murze (≥ 0,90 × 2,00 w świetle ościeżnicy), próg ≤ 0,02 (W-055); pod daszkiem")
O("O0-10", "S0-06", 11.25, 11.60, "fix", "FX3", 2.40, 0.0, oslona="brak", uwagi="doświetle boczne drzwi wejściowych, VSG mleczne (przeszczep z W3)")
O("O0-11", "S0-07", 1.20, 3.60, "drzwi_przesuwne_HS", "HS2", 2.75, 0.0, HS, "screen_zip", bezprogowe=True,
  uwagi="HS salonu na taras zach. pod okapem 1,50 m (przeszczep J2 z W1/W3)")
O("O0-12", "S0-07", 5.80, 7.60, "okno", "OZ1", 1.50, 0.90, RU, "zaluzja_zewn", uwagi="pokój gościnny — zachód")
O("O0-13", "S0-06", 4.30, 5.10, "okno", "ON1", 0.60, 1.60, ow("U"), "brak", uwagi="łazienka gościnna — okno wysokie")
O("O0-14", "S0-08", 4.20, 5.10, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="salon → przedpokój gościnny")
O("O0-15", "S0-11", 5.33, 6.23, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="przedpokój → pokój gościnny")
O("O0-16", "S0-19", 4.20, 5.10, "drzwi", "D2P", 2.10, 0.0, ow("przesuwne", "na_zewn", przesuwne=True),
  uwagi="łazienka gościnna — drzwi przesuwne naścienne (WT §79 ust. 1), podcięcie ≥ 0,022 m²")
O("O0-17", "S0-09", 7.40, 8.20, "drzwi", "D3", 2.00, 0.0, ow("R", "do_wewn"), uwagi="spiżarnia pod biegiem 2 (przeszczep J2)")
O("O0-18", "S0-10", 8.90, 10.40, "otwor", "OT1", 2.40, 0.0, uwagi="hol → pas komunikacyjny przy schodach / strefa dzienna")
O("O0-19", "S0-20", 8.71, 9.61, "drzwi", "D2", 2.10, 0.0, ow("R", "na_zewn"), uwagi="WC gościnne — na zewnątrz, kratka ≥ 0,022 m²")
O("O0-20", "S0-21", 10.15, 11.05, "drzwi", "DS1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="drzwi szklane VSG w osi wejścia (x ≈ 10,60)")
O("O0-21", "S0-15", 0.35, 1.25, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"),
  uwagi="przedsionek → kuchnia; przesunięte do fasady (przeszczep J1) — ciągła zabudowa kuchni y 1,40–5,02")
O("O0-22", "S0-17", 13.60, 14.50, "drzwi", "DG1", 2.10, 0.0, ow("R", "do_wewn"),
  uwagi="garaż → przedsionek: szczelne, samozamykacz, U ≤ 1,3 (W-113, W-244)")
O("O0-23", "S0-18", 1.60, 2.50, "drzwi", "D4", 2.10, 0.0, ow("R", "do_wewn"),
  uwagi="pom. techniczne dostępne z domu przez przedsionek (poprawka J2)")

# ---- P1
O("O1-01", "S1-01", 4.10, 11.105, "okno", "BC1", 1.50, 0.70, ow("RU"), "screen_zip", kwatery=3,
  uwagi="boks C — 3 kwatery 2,335 m w ramie wysuniętej 1,00 m; dolna część stała VSG do 0,85 m (W-097); słupki SLC1/SLC2 nad SL3/SL4")
O("O1-02", "S1-02", 1.20, 2.70, "okno", "OE1", 1.50, 0.85, RU, "zaluzja_zewn", uwagi="pokój rodzinny — wschód (parapet +4,00 > attyka garażu +3,85)")
O("O1-03", "S1-03", 4.30, 5.20, "okno", "ON2", 0.60, 1.60, ow("U"), "brak", uwagi="łazienka dzieci")
O("O1-04", "S1-03", 10.40, 11.60, "okno", "ON3", 0.60, 1.60, ow("U"), "brak", uwagi="pralnia")
O("O1-05", "S1-04", 6.00, 7.80, "okno", "OZ1", 1.50, 0.90, RU, "zaluzja_zewn", uwagi="pokój dziecka 2 — zachód")
O("O1-06", "S1-04", 1.00, 2.80, "okno", "OZ1", 1.50, 0.90, RU, "zaluzja_zewn", uwagi="pokój dziecka 1 — zachód (elewacja pd. bryły B pełna)")
O("O1-07", "S1-11", 2.60, 3.50, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="pokój dziecka 1")
O("O1-08", "S1-11", 6.00, 8.40, "otwor", "OT2", 2.40, 0.0, uwagi="hol → pokój rodzinny (galeria przy schodach)")
O("O1-09", "S1-05", 2.60, 3.50, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="pokój dziecka 2")
O("O1-10", "S1-05", 4.20, 5.10, "drzwi", "D2", 2.10, 0.0, ow("R", "na_zewn"), uwagi="łazienka dzieci — na zewnątrz")
O("O1-11", "S1-06", 8.71, 9.61, "drzwi", "D2", 2.10, 0.0, ow("R", "na_zewn"), uwagi="WC z natryskiem — na zewnątrz (pion K2 nad WC P0)")
O("O1-12", "S1-06", 10.15, 11.05, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="pralnia z suszarnią")

# ---- P2 (okna od pd./zach./wsch. za lamelami; parapet 0,60 — dolna część stała VSG do 0,85 m, skrzydła do wewnątrz — W-097/W-098)
O("O2-01", "S2-01", 0.00, 3.00, "okno", "OP1", 2.00, 0.60, ow("RU"), "screen_zip", uwagi="sypialnia — południe (za lamelami)")
O("O2-02", "S2-01", 4.10, 5.30, "okno", "OP2", 1.75, 0.85, RU, "screen_zip", uwagi="garderoba — południe")
O("O2-03", "S2-01", 9.00, 11.40, "okno", "OP3", 2.00, 0.60, ow("RU"), "screen_zip", uwagi="gabinet — południe")
O("O2-04", "S2-08", 1.30, 3.70, "okno", "OP3", 2.00, 0.60, ow("RU"), "screen_zip", uwagi="sypialnia — zachód (ściana lekka, za lamelami)")
O("O2-05", "S2-02", 1.90, 3.10, "okno", "OP2", 1.75, 0.85, RU, "screen_zip", uwagi="gabinet — wschód")
O("O2-06", "S2-05", 4.30, 5.20, "okno", "ON2", 0.60, 1.60, ow("U"), "brak", uwagi="łazienka rodziców")
O("O2-07", "S2-05", 6.40, 8.10, "okno", "ON4", 1.50, 0.90, ow("U"), "brak", uwagi="klatka schodowa — północ (nad biegami)")
O("O2-08", "S2-12", 3.90, 4.80, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="garderoba → sypialnia")
O("O2-09", "S2-13", 3.90, 4.80, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="hol → garderoba (przedpokój apartamentu)")
O("O2-10", "S2-09", 4.20, 5.10, "drzwi", "D2", 2.10, 0.0, ow("R", "na_zewn"), uwagi="garderoba → łazienka rodziców (na zewnątrz)")
O("O2-11", "S2-14", 3.90, 4.80, "drzwi", "D1", 2.10, 0.0, ow("R", "do_wewn"), uwagi="hol → gabinet")
O("O2-12", "S2-15", 6.20, 7.10, "drzwi", "D4", 2.10, 0.0, ow("R", "do_wewn"), uwagi="hol → pom. techniczne (centrala reku, wyłaz na dach)")


# =====================================================================================================================
# 6. POMIESZCZENIA — kategoria wg PN-ISO 9836:2022 (podstawowa | pomocnicza | ruchu | techniczna); temp. obliczeniowa θ_int
#    wg WT §134 / PN-EN 12831-1 NA (pokoje, kuchnia, hol 20 °C; łazienki 24 °C; pom. gosp./techn. 16 °C; garaż nieogrzewany);
#    wentylacja: wywiew min. wg PN-83/B-03430/Az3:2000 (kuchnia z kuchenką elektr. > 3 os. 50 m³/h, łazienka 50, WC 30,
#    pom. bezokienne 15, pralnia ≥ 2 h⁻¹); nawiew do pokoi — bilans zrównoważony (Σnaw = Σwyw), ≥ 20 m³/h·os. (W-161)
# =====================================================================================================================
PM: list[dict] = []


def PMS(pid, kond, nazwa, punkt=None, wiel=None, kat="podstawowa", pobyt=False, posadzka="DESKA_DEB", sciany="TYNK_GIPS",
        sufit="TYNK_GIPS", temp=20, naw=0, wyw=0, rodzaj=None, podloga=None, **kw):
    d = {"id": pid, "kond": kond, "nazwa": nazwa, "punkt": [r(punkt[0]), r(punkt[1])] if punkt else None,
         "wielobok": [[r(a), r(b)] for a, b in wiel] if wiel else None, "kategoria": kat, "pobyt_ludzi": pobyt,
         "posadzka": posadzka, "sciany_wyk": sciany, "sufit": sufit, "temp": temp, "went": {"naw": naw, "wyw": wyw}}
    if rodzaj:
        d["rodzaj"] = rodzaj
    if podloga:
        d["podloga"] = podloga
    d.update(kw)
    PM.append(d)


# pas komunikacyjny przy schodach (ekran z lamel h 2,10 m wzdłuż y = 3,80 — przeszczep J1 z W3)
PAS = (5.90, 3.85, 8.90, Y3_s)
# ---- P0
PMS("0.01", "P0", "Wiatrołap", (10.9, 7.6), kat="ruchu", posadzka="GRES", temp=16, rodzaj="komunikacja", podloga="POD-0L",
    uwagi="szklana przegroda z drzwiami w osi wejścia; ławka")
PMS("0.02", "P0", "Hol", (10.0, 5.9), kat="ruchu", posadzka="GRES", temp=20, rodzaj="komunikacja", podloga="POD-0L", uwagi="szafa wejściowa 0,60 m przy ścianie E")
PMS("0.03", "P0", "WC gościnne", (9.2, 7.6), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", sufit="SUF_GK", temp=20, wyw=30, rodzaj="wc",
    podloga="POD-0L", uwagi="szer. 1,195 m ≥ 0,90 (W-060); wentylacja mechaniczna")
PMS("0.04", "P0", "Klatka schodowa", None, [(XC_e, Y3_s), (B1_X1, Y3_s), (B1_X1, Y_SPOCZ), (XC_e, Y_SPOCZ)], kat="ruchu", temp=20, rodzaj="komunikacja",
    uwagi="bieg 1 SCH1; wyłączona z PU (W-316)")
PMS("0.05", "P0", "Spiżarnia (pod schodami)", None, [(B2_X0, Y3_n), (B2_X1, Y3_n), (B2_X1, Y4_i), (XC_e, Y4_i), (XC_e, Y_SPOCZ), (B2_X0, Y_SPOCZ)],
    kat="pomocnicza", posadzka="GRES", temp=16, wyw=15, rodzaj="pomocnicze", podloga="POD-0L", wys=1.90,
    uwagi="wysokość zmienna 2,77 → 1,39 m pod biegiem 2 i spocznikiem — PU liczona w 50 % (wys. zastępcza 1,90; W-316)")
PMS("0.06", "P0", "Salon + jadalnia + kuchnia", None,
    [(XA_i, Y1_i), (XE_i, Y1_i), (XE_i, Y3_s), (PAS[2], Y3_s), (PAS[2], PAS[1]), (PAS[0], PAS[1]), (PAS[0], Y3_s), (XA_i, Y3_s)],
    kat="podstawowa", pobyt=True, temp=20, naw=100, wyw=50, rodzaj="kuchnia",
    uwagi="strefa dzienna; kuchnia z wyspą — zabudowa ciągła przy ścianie osi E (y 1,30–5,02, przeszczep J1); wywiew okap 50/120 m³/h")
PMS("0.07", "P0", "Pas komunikacyjny przy schodach", None, [(PAS[0], PAS[1]), (PAS[2], PAS[1]), (PAS[2], PAS[3]), (PAS[0], PAS[3])], kat="ruchu",
    temp=20, rodzaj="komunikacja", uwagi="wydzielony ekranem z lamel h 2,10 m (LAM-P0); dojście hol → stopa schodów bez przechodzenia przez strefę mebli")
PMS("0.08", "P0", "Przedpokój gościnny", (4.6, 5.8), kat="ruchu", temp=20, rodzaj="komunikacja")
PMS("0.09", "P0", "Łazienka gościnna (natrysk)", (4.8, 7.6), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", sufit="SUF_GK", temp=24, wyw=50,
    rodzaj="lazienka", podloga="POD-0L")
PMS("0.10", "P0", "Pokój gościnny / gabinet", (1.9, 6.9), kat="podstawowa", pobyt=True, temp=20, naw=40, rodzaj="pokoj")
PMS("0.11", "P0", "Przedsionek gospodarczy", (13.4, 1.4), kat="ruchu", posadzka="GRES", temp=20, rodzaj="komunikacja", podloga="POD-0L",
    uwagi="garaż → przedsionek → kuchnia ≈ 6 m; szafa na odzież i obuwie; drzwi do ogrodu")
PMS("0.12", "P0", "Pomieszczenie techniczne", (16.6, 1.4), kat="techniczna", posadzka="GRES", sciany="TYNK_CW", temp=16, wyw=15, rodzaj="techniczne",
    podloga="POD-0L", uwagi="moduł hydrauliczny PC R290 (monoblok zewn.), zasobnik CWU 300 l, bufor 100 l, rozdzielacze, RG, wodomierz; dostęp z przedsionka")
PMS("0.13", "P0", "Garaż 2-stanowiskowy", (15.3, 6.2), kat="pomocnicza", posadzka="ZYWICA", sciany="TYNK_CW", sufit="TYNK_CW", temp=None,
    rodzaj="garaz", podloga="POD-G", ogrzewane=False,
    uwagi="w świetle 6,05 × 6,175 m (≥ 5,60 × 6,00; W-112); nieogrzewany, wentylacja naturalna ≥ 0,08 m² (W-115); posadzka −0,10, spadek 1,5 % do bramy")
# ---- P1
PMS("1.01", "P1", "Hol", None, [(XA_i, yH + FD), (XE_i, yH + FD), (XE_i, Y3_s), (XD_w, Y3_s), (XD_w, Y3_n), (XC_e, Y3_n), (XC_e, Y3_s), (XA_i, Y3_s)],
    kat="ruchu", temp=20, rodzaj="komunikacja")
PMS("1.02", "P1", "Pokój rodzinny / biblioteka (boks C)", (8.0, 1.8), kat="podstawowa", pobyt=True, temp=20, naw=40, rodzaj="pokoj")
PMS("1.03", "P1", "Pokój dziecka 1", (1.9, 1.8), kat="podstawowa", pobyt=True, temp=20, naw=40, rodzaj="pokoj")
PMS("1.04", "P1", "Pokój dziecka 2", (1.9, 6.9), kat="podstawowa", pobyt=True, temp=20, naw=40, rodzaj="pokoj")
PMS("1.05", "P1", "Łazienka dzieci (wanna)", (4.6, 7.5), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", sufit="SUF_GK", temp=24, wyw=50,
    rodzaj="lazienka", podloga="POD-1L")
PMS("1.06", "P1", "Klatka schodowa", None, [(XC_e, Y3_n), (XD_w, Y3_n), (XD_w, Y4_i), (XC_e, Y4_i)], kat="ruchu", temp=20, rodzaj="komunikacja",
    uwagi="wyłączona z PU (W-316)")
PMS("1.07", "P1", "WC z natryskiem", (9.2, 7.0), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", sufit="SUF_GK", temp=24, wyw=50, rodzaj="lazienka",
    podloga="POD-1L", uwagi="nad WC P0 — pion K2 (zawór napowietrzający, K1 wentylowany ponad dach)")
PMS("1.08", "P1", "Pralnia z suszarnią", (10.9, 7.0), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", temp=20, wyw=40, rodzaj="pralnia",
    podloga="POD-1L", uwagi="zmniejszona do ≈ 6,6 m² (przeszczep J1); wywiew ≥ 2 h⁻¹")
# ---- P2
PMS("2.01", "P2", "Hol", None, [(xC + FD, Y_TH + FD), (xD - FD, Y_TH + FD), (xD - FD, Y3_s), (xC + FD, Y3_s)], kat="ruchu", temp=20, rodzaj="komunikacja")
PMS("2.02", "P2", "Sypialnia rodziców", (1.3, 2.4), kat="podstawowa", pobyt=True, temp=20, naw=50, rodzaj="pokoj",
    uwagi="naroże S+W nad wspornikiem; okna za lamelami")
PMS("2.03", "P2", "Garderoba (przedpokój apartamentu)", (4.7, 2.4), kat="pomocnicza", temp=20, wyw=0, rodzaj="pomocnicze")
PMS("2.04", "P2", "Łazienka rodziców", (4.6, 7.5), kat="pomocnicza", posadzka="GRES", sciany="PLYTKI_SC", sufit="SUF_GK", temp=24, wyw=50,
    rodzaj="lazienka", podloga="POD-1L", uwagi="nad łazienkami P1 i P0 (pion SI)")
PMS("2.05", "P2", "Gabinet / pokój", (10.2, 2.4), kat="podstawowa", pobyt=True, temp=20, naw=40, rodzaj="pokoj")
PMS("2.06", "P2", "Klatka schodowa (wyjście z biegu 2, pustka)", None, [(XC_e, Y3_s), (XD_w, Y3_s), (XD_w, Y4_i), (XC_e, Y4_i)], kat="ruchu",
    temp=20, rodzaj="komunikacja", uwagi="świetlik SW1 nad spocznikiem, okno pn. ON4; wyłączona z PU")
PMS("2.07", "P2", "Pom. techniczne (centrala rekuperacyjna, wyłaz na dach)", (7.2, 1.3), kat="techniczna", posadzka="GRES", temp=16,
    rodzaj="techniczne", podloga="POD-1L", uwagi="centrala 450 m³/h; wyłaz 0,90 × 0,90 m z drabiną (W-065)")


# =====================================================================================================================
# 7. STROPY, DACHY (z attykami, spadkami, wpustami, przelewami awaryjnymi, rurami spustowymi), PŁYTY WYSUNIĘTE
#    Konwencja SCHEMAT p. 5.1: odsłonięte fragmenty stropów = `dachy`; dach garażu = osobny element `dachy`.
# =====================================================================================================================
OB_P1 = R(-EXT, -EXT, xE + EXT, y4 + EXT)                                          # −0,30…12,30 × −0,30…9,05
OB_P2 = P((xA2 - 0.18, -EXT), (xE + EXT, -EXT), (xE + EXT, y3 + EXT), (xD + EXT, y3 + EXT), (xD + EXT, y4 + EXT),
          (xB - EXT, y4 + EXT), (xB - EXT, y3 + EXT), (xA2 - 0.18, y3 + EXT))
OTW_SCH = R(XC_e, Y3_n, XD_w, Y4_i)                                                 # otwór klatki w ST1/ST2
X2o = xA2 - 0.18                                                                     # lico zach. bryły A (−1,30)

STROPY = [
    {"id": "ST1", "nad": "P0", "wierzch": Z_ST1, "grubosc": T_STR, "obrys": OB_P1, "otwory": [OTW_SCH], "podloga": "POD-1", "sufit": "TYNK_GIPS",
     "mat": "ZB_C25", "uwagi": "strop nad P0 (część mieszkalna): N–S, ciągły 2-przęsłowy B1 (oś 1) – oś 3 – oś 4, rozpiętości 5,125 / 3,625 m"},
    {"id": "ST2", "nad": "P1", "wierzch": Z_ST2, "grubosc": T_STR,
     "obrys": P((-EXT, -EXT), (xE + EXT, -EXT), (xE + EXT, y3 + EXT), (xD + EXT, y3 + EXT), (xD + EXT, y4 + EXT), (xB - EXT, y4 + EXT),
                (xB - EXT, y3 + EXT), (-EXT, y3 + EXT)),
     "otwory": [OTW_SCH], "podloga": "POD-1", "sufit": "TYNK_GIPS", "mat": "ZB_C25",
     "uwagi": "strop nad P1 pod bryłą A i nadbudową; pola pn. poza bryłą A — dachy D2/D3"},
    {"id": "ST2Z", "nad": "P1", "wierzch": Z_ST2, "grubosc": T_STR, "obrys": R(X2o, -EXT, -EXT, y3 + EXT), "podloga": "POD-1", "sufit": "SUF-ZEW",
     "mat": "ZB_C25", "uwagi": "strop P2 nad powietrzem zewnętrznym (wspornik bryły A 1,00 m lico–lico): E–W oś A – belka B3, docieplenie spodu"},
]

WP = lambda x, y, dn=100, grz=True, **kw: {"xy": [r(x), r(y)], "dn": dn, "podgrzewany": grz, **kw}          # noqa: E731
PA = lambda x, y, sc, dno, **kw: {"xy": [r(x), r(y)], "sciana_attyki": sc, "szer": 0.20, "wys": 0.10, "rzedna_dna": r(dno), **kw}  # noqa: E731

DACHY = [
    {"id": "D1", "obrys": OB_P2, "plyta": {"wierzch": Z_ST3, "grubosc": T_STR}, "przegroda": "SD1", "spadek": 0.02,
     "attyka": {"wys_nad_pokryciem": 0.25, "szer": 0.25, "przegroda": "AT1"},
     "otwory": [R(6.10, 7.55, 8.30, 8.55), R(6.70, 0.90, 7.60, 1.80)],
     "wpusty": [WP(5.57, 5.45, opis="WP1 — nad szachtem SI (najniższy punkt spadków)"),
                WP(4.40, 8.35, opis="WP2 — przy attyce pn. nadbudowy; podejście w stropie łazienki P2 do SI")],
     "przelewy_awaryjne": [PA(5.00, y4 + EXT, "N", 9.48, opis="przelew PA1 — attyka pn. nadbudowy (na dach D2/teren)"),
                           PA(2.00, y3 + EXT, "N", 9.52, opis="przelew PA2 — na dach D2 (pole zach., z własnym wpustem)"),
                           PA(10.60, y3 + EXT, "N", 9.52, opis="przelew PA3 — na dach D3 (pole wsch., z własnym wpustem)")],
     "rury_spustowe": [{"id": "RS1", "od_wpustu": 0, "trasa": "wewn_szacht", "xy_pion": [5.57, 5.45], "dn": 100, "do": "zbiornik",
                        "opis": "w izolowanym szachcie SI (otulina 20 mm, izolacja akustyczna), pod płytą do kolektora KD-W"},
                       {"id": "RS2", "od_wpustu": 1, "trasa": "wewn_szacht", "xy_pion": [5.57, 5.85], "dn": 100, "do": "zbiornik",
                        "opis": "w szachcie SI; podejście poziome DN100 w suficie podwieszanym łazienki P2 (izolowane)"}],
     "spadki": [{"od": [X2o, -EXT], "do": [5.57, 5.45], "spadek": 0.02}, {"od": [xE + EXT, -EXT], "do": [5.57, 5.45], "spadek": 0.02},
                {"od": [xD + EXT, y4 + EXT], "do": [4.40, 8.35], "spadek": 0.02}],
     "uwagi": "stropodach bryły A: PV ≤ 6,5 kWp na niskich stelażach (≤ +9,78, nie ponad attykę); świetlik SW1 2,20 × 1,00 nad spocznikiem; "
              "wyłaz 0,90 × 0,90 w pom. 2.07; czerpnia i wyrzutnia reku (≥ 0,40 m nad pokryciem), wywiewka K1 nad SI"},
    {"id": "D2", "obrys": R(-EXT, y3 + EXT, xB - EXT, y4 + EXT), "plyta": {"wierzch": Z_ST2, "grubosc": T_STR}, "przegroda": "SD2", "spadek": 0.02,
     "attyka": {"wys_nad_pokryciem": 0.25, "szer": 0.25, "przegroda": "AT1"},
     "wpusty": [WP(0.40, y4 - 0.05, opis="wpust attykowy (boczny) WP3 — narożnik NW")],
     "przelewy_awaryjne": [PA(-EXT, 7.20, "W", 6.46, opis="przelew PA4 — attyka zach.")],
     "rury_spustowe": [{"id": "RS3", "od_wpustu": 0, "trasa": "zewn", "xy_pion": [0.40, y4 + EXT + 0.06], "dn": 100, "do": "zbiornik",
                        "opis": "zewnętrzna na elewacji pn., czyszczak 0,5 m nad terenem, kolektor KD-W"}],
     "spadki": [{"od": [xB - EXT, y3 + EXT], "do": [0.40, y4 - 0.05], "spadek": 0.02}],
     "uwagi": "dach nad P1 (pole zach.), żwirowy, nieużytkowy"},
    {"id": "D3", "obrys": R(xD + EXT, y3 + EXT, xE + EXT, y4 + EXT), "plyta": {"wierzch": Z_ST2, "grubosc": T_STR}, "przegroda": "SD2", "spadek": 0.02,
     "attyka": {"wys_nad_pokryciem": 0.25, "szer": 0.25, "przegroda": "AT1"},
     "wpusty": [WP(9.20, y4 - 0.05, opis="wpust attykowy (boczny) WP4 — przy attyce pn.")],
     "przelewy_awaryjne": [PA(xE + EXT, 7.20, "E", 6.46, opis="przelew PA5 — attyka wsch. (awaryjnie na dach D4)")],
     "rury_spustowe": [{"id": "RS4", "od_wpustu": 0, "trasa": "zewn", "xy_pion": [9.20, y4 + EXT + 0.06], "dn": 100, "do": "zbiornik",
                        "opis": "zewnętrzna na elewacji pn. obok daszku wejścia, czyszczak, kolektor KD-W"}],
     "spadki": [{"od": [xE + EXT, y3 + EXT], "do": [9.20, y4 - 0.05], "spadek": 0.02}],
     "uwagi": "dach nad P1 (pole wsch.), żwirowy, nieużytkowy"},
    {"id": "D4", "obrys": P((xE + EXT, -EXT), (xF + EXT, -EXT), (xF + EXT, y5 + EXT), (xE - EXT, y5 + EXT), (xE - EXT, y4 + EXT), (xE + EXT, y4 + EXT)),
     "plyta": {"wierzch": Z_DG, "grubosc": T_DG}, "przegroda": "DZ1", "spadek": 0.02,
     "attyka": {"wys_nad_pokryciem": 0.545, "szer": 0.25, "przegroda": "AT1"},
     "wpusty": [WP(18.05, 9.05, opis="WP5 — garaż, narożnik NE, studzienka kontrolna w opasce żwirowej"),
                WP(17.95, 0.35, opis="WP6 — pas gospodarczy, narożnik SE (poza strefą R290)")],
     "przelewy_awaryjne": [PA(xF + EXT, 6.50, "E", 3.36, opis="przelew PA6 — attyka wsch. (garaż)"),
                           PA(xF + EXT, 2.40, "E", 3.36, opis="przelew PA7 — attyka wsch. (pas gosp.; > 1 m od jedn. PC)")],
     "rury_spustowe": [{"id": "RS5", "od_wpustu": 0, "trasa": "zewn", "xy_pion": [xF + EXT + 0.06, 9.05], "dn": 100, "do": "zbiornik",
                        "opis": "zewnętrzna w narożu NE, czyszczak, kolektor KD-E"},
                       {"id": "RS6", "od_wpustu": 1, "trasa": "wewn_szacht", "xy_pion": [17.95, 0.35], "dn": 100, "do": "zbiornik",
                        "opis": "w pom. technicznym 0.12 (obudowa izolowana), pod płytą do kolektora KD-E"}],
     "spadki": [{"od": [xE + EXT, 4.5], "do": [18.05, 9.05], "spadek": 0.02}, {"od": [xE + EXT, 1.2], "do": [17.95, 0.35], "spadek": 0.02}],
     "uwagi": "dach zielony ekstensywny NIEUŻYTKOWY nad garażem i pasem gospodarczym (bez tarasu, bez wyjścia — decyzja Inwestora); "
              "attyka pd. +3,85 = linia D do narożnika garażu; opaska żwirowa 0,5 m przy attykach i wpustach"},
]

WSP = [
    {"id": "PL-E", "obrys": P((-1.80, -1.30), (13.80, -1.30), (13.80, -EXT), (-EXT, -EXT), (-EXT, y3), (-1.80, y3)), "wierzch": Z_OKAP_E[1],
     "grubosc": Z_OKAP_E[1] - Z_OKAP_E[0], "przegroda": "OK1", "lacznik_termiczny": True, "mat": "ZB_C30",
     "uwagi": "E — okap ST1: 1,00 m pd. (x −1,80…13,80, także nad drzwiami gospodarczymi) i 1,50 m zach.; łączniki termoizolacyjne (ETA)"},
    {"id": "PL-DA", "obrys": R(9.40, y4 + EXT, xE - EXT, 10.35), "wierzch": 3.05, "grubosc": 0.25, "przegroda": "OK1", "lacznik_termiczny": True,
     "mat": "ZB_C30", "uwagi": "daszek nad wejściem 2,30 × 1,30 m (≥ drzwi + 1,0 × ≥ 1,0 — W-057); 0,95 m za linią zabudowy"},
    {"id": "PL-C1", "obrys": R(3.60, -1.30, 12.60, -EXT), "wierzch": Z_RAMA_D[1], "grubosc": 0.20, "mat": "RAMA_C", "lacznik_termiczny": True,
     "uwagi": "rama boksu C — pas dolny = linia D (+3,65…+3,85), lekka rama stalowa w okładzinie na konsolach punktowych z przekładką (J2)"},
    {"id": "PL-C2", "obrys": R(3.60, -1.30, 13.45, -EXT), "wierzch": Z_RAMA_G[1], "grubosc": 0.20, "mat": "RAMA_C", "lacznik_termiczny": True,
     "uwagi": "rama boksu C — pas górny (+5,35…+5,55), przedłużony na wschód do x 13,45 (szkic: 13,76 m od lica B)"},
    {"id": "PL-2", "obrys": P((-2.40, -1.30), (12.60, -1.30), (12.60, -EXT), (X2o, -EXT), (X2o, y3 + EXT), (-2.40, y3 + EXT)),
     "wierzch": Z_OKAP_2[1], "grubosc": Z_OKAP_2[1] - Z_OKAP_2[0], "przegroda": "OK1", "lacznik_termiczny": True, "mat": "ZB_C30",
     "uwagi": "krawędź ST2 — spód bryły A: wysunięcie 1,00 m pd., 1,10 m zach. (od lica A), 0,30 m wsch."},
    {"id": "PL-3", "obrys": P((-2.40, -1.30), (12.60, -1.30), (12.60, y3 + EXT), (xE + EXT, y3 + EXT), (xE + EXT, -EXT), (X2o, -EXT), (X2o, y3 + EXT),
                              (-2.40, y3 + EXT)),
     "wierzch": Z_OKAP_3[1], "grubosc": Z_OKAP_3[1] - Z_OKAP_3[0], "przegroda": "OK1", "lacznik_termiczny": True, "mat": "ZB_C30",
     "uwagi": "krawędź ST3 — stropodach bryły A: 1,00 m pd., 1,10 m zach., 0,30 m wsch.; attyka cofnięta w licu ściany"},
]


# =====================================================================================================================
# 8. SŁUPY, BELKI, NADPROŻA, FUNDAMENTY, SCHODY, BALUSTRADY/POCHWYTY, LAMELE, TARASY
# =====================================================================================================================
Z_SPOD_ST1 = Z_ST1 - T_STR           # 2,78
SLUPY = [{"id": f"SL{i + 1}", "xy": [r(x), 0.0], "przekroj": "RK 120x120x8", "mat": "STAL_S355", "z_od": Z_PLYTA_F, "z_do": Z_SPOD_ST1,
          "uwagi": "słup fasady E w szprosie przeszklenia; podpora belki B1"} for i, x in enumerate(E_KW[1:5])]
SLUPY += [{"id": f"SL{5 + i}", "xy": [r(x), 0.0], "przekroj": "RK 100x100x6", "mat": "STAL_S355", "z_od": Z_RAMA_D[1], "z_do": Z_RAMA_G[0],
           "uwagi": "słupek boksu C w szprosie (w jednej linii ze słupem fasady E — przeszczep J2), podpora nadproża B2"}
          for i, x in enumerate(E_KW[3:5])]
SLUPY += [{"id": f"SL{7 + i}", "xy": [r(x), -0.80], "przekroj": "150x1000", "mat": "RAMA_C", "z_od": Z_RAMA_D[1], "z_do": Z_RAMA_G[0],
           "uwagi": "bok ramy boksu C (płaskownik w okładzinie) przy krawędzi przeszklenia"} for i, x in enumerate((4.025, 11.18))]

BELKI = [
    {"id": "B1", "os": [[0.0, 0.0], [xE, 0.0]], "b": 0.25, "h": 1.07, "spod": Z_SPOD_ST1, "mat": "ZB_C30",
     "uwagi": "podciąg fasady E, odwrócony (+2,78…+3,85 = parapet boksu C); przęsła 2,20/1,90/2,335/2,335/3,23 na SL1–SL4 i ścianach A, E"},
    {"id": "B2", "os": [[3.85, 0.0], [11.355, 0.0]], "b": 0.25, "h": r(Z_ST2 - Z_RAMA_G[0]), "spod": Z_RAMA_G[0], "mat": "ZB_C30",
     "uwagi": "nadproże boksu C 25×80, 3 przęsła 2,335 m na słupkach SL5/SL6"},
    {"id": "B3", "os": [[xA2, 0.0], [xA2, y3]], "b": 0.20, "h": 0.60, "spod": r(Z_ST2 - T_STR), "mat": "ZB_C30",
     "uwagi": "belka krawędziowa ST2 w osi A' (odwrócona, pod parapetem okna O2-04) — niesie lekką ścianę A' i okap PL-2; oparta na końcach B4/B5"},
    {"id": "B4", "os": [[xA2, 0.0], [xB, 0.0]], "b": 0.18, "h": 0.80, "spod": r(Z_ST2 - T_STR), "mat": "ZB_C30",
     "uwagi": "belka wspornikowa w osi 1 (w licu ściany P2, pod parapetem O2-01 +6,90): wspornik 1,12 m na ścianie A, przęsło zakotwienia A–B 3,875 m"},
    {"id": "B5", "os": [[xA2, y3], [xB, y3]], "b": 0.18, "h": 0.80, "spod": r(Z_ST2 - T_STR), "mat": "ZB_C30",
     "uwagi": "belka wspornikowa w osi 3 (w ścianie pn. P2): wspornik 1,12 m, zakotwienie A–B"},
    {"id": "B6", "os": [[xA2, 0.0], [xA2, y3]], "b": 0.20, "h": 0.40, "spod": r(Z_ST3 - T_STR - 0.18), "mat": "ZB_C30",
     "uwagi": "belka krawędziowa ST3 w osi A' (nad oknem O2-04) — okap zach. stropodachu; oparta na narożach ścian osi 1 i 3"},
    {"id": "B7", "os": [[12.50, y5], [17.95, y5]], "b": 0.25, "h": r(Z_DG - 2.15), "spod": 2.15, "mat": "ZB_C30",
     "uwagi": "nadproże bramy garażu (rozp. 5,00 m w świetle)"},
    {"id": "B8", "os": [[xC, y3], [xD, y3]], "b": 0.25, "h": 0.50, "spod": r(Z_ST1 - 0.50), "mat": "ZB_C25",
     "uwagi": "podciąg ST1 w osi 3 nad wejściem na schody (C–D, 2,625 m); prześwit nad stopą biegu 1 ≥ 2,30 m"},
    {"id": "B9", "os": [[xC, y3], [xD, y3]], "b": 0.25, "h": 0.50, "spod": r(Z_ST2 - 0.50), "mat": "ZB_C25",
     "uwagi": "podciąg ST2 w osi 3 nad wyjściem ze schodów P1 (C–D)"},
]
# nadproża otworów ≥ 1,50 m w ścianach murowanych (pozostałe — prefabrykowane nadproża systemowe / wieniec)
_nadp = 0
for o in OT:
    s = _SC[o["sciana"]]
    if s["przegroda"] not in ("SZ1", "SZ2", "SW18", "SWG") or o["szer"] < 1.45 or o["id"] in ("O0-01", "O0-02", "O0-03", "O0-04", "O0-05", "O1-01", "O0-07"):
        continue
    kz = {"P0": 0.0, "P1": Z_P1, "P2": Z_P2}[s["kond"]]
    top = kz + o["parapet"] + o["wys"]
    spod_pl = {"P0": Z_SPOD_ST1, "P1": Z_ST2 - T_STR, "P2": Z_ST3 - T_STR}[s["kond"]]
    if spod_pl - top < 0.12:
        continue                                              # otwór pod wieńcem — nadprożem jest wieniec/płyta
    (ax, ay), (bx, by) = s["os"]
    L_ = seg_len((ax, ay), (bx, by))
    ux, uy = (bx - ax) / L_, (by - ay) / L_
    s0, s1 = o["odl"] - 0.20, o["odl"] + o["szer"] + 0.20
    _nadp += 1
    BELKI.append({"id": f"N{_nadp}", "os": [[r(ax + ux * s0), r(ay + uy * s0)], [r(ax + ux * s1), r(ay + uy * s1)]], "b": 0.18,
                  "h": r(min(0.24, spod_pl - top)), "spod": r(top), "mat": "ZB_C25", "uwagi": f"nadproże otworu {o['id']} ({o['szer']:.2f} m), oparcie 0,20 m"})

# ---- fundamenty: PŁYTA FUNDAMENTOWA na XPS (uzasadnienie — koncepcja.md p. 5.4)
OB_P0 = P((-EXT, -EXT), (xF + EXT, -EXT), (xF + EXT, y5 + EXT), (xE - EXT, y5 + EXT), (xE - EXT, y4 + EXT), (-EXT, y4 + EXT))
OB_PF = P((-0.10, -0.10), (xF + 0.10, -0.10), (xF + 0.10, y5 + 0.10), (xE - 0.10, y5 + 0.10), (xE - 0.10, y4 + 0.10), (-0.10, y4 + 0.10))
FUND_EL = [{"id": "PF1", "obrys": OB_PF, "spod": r(Z_PLYTA_F - T_PLYTA_F), "h": T_PLYTA_F, "mat": "ZB_C25",
            "uwagi": "płyta fundamentowa ŻB 25 cm C25/30 XC2 na XPS 300 20 cm; krawędź do lica konstrukcji, XPS pionowy 20 cm na czole płyty"}]
_zi = 0
for s in SC:
    if s["kond"] != "P0" or s["przegroda"] not in ("SZ1", "SW18", "SWZB", "SWG"):
        continue
    _zi += 1
    zew = s["przegroda"] == "SZ1"
    FUND_EL.append({"id": f"ZF{_zi}", "os": s["os"], "b": 0.60 if zew else 0.50, "h": 0.30 if zew else 0.25,
                    "spod": r(Z_PLYTA_F - T_PLYTA_F - (0.30 if zew else 0.25)), "mat": "ZB_C25",
                    "uwagi": f"pogrubienie (żebro) płyty pod ścianą {s['id']}" + (" — krawędź z izolacją obwodową XPS (PN-EN ISO 13793)" if zew else "")})
for sl in SLUPY[:4]:
    x, y = sl["xy"]
    FUND_EL.append({"id": f"SF{sl['id'][2:]}", "os": [[r(x - 0.005), y], [r(x + 0.005), y]], "b": 1.00, "h": 0.45, "spod": r(Z_PLYTA_F - T_PLYTA_F - 0.45),
                    "mat": "ZB_C25", "uwagi": f"pogrubienie płyty 1,0 × 1,0 m pod słupem {sl['id']} (przebicie)"})
FUND = {"typ": "plyta", "elementy": FUND_EL,
        "izolacja_obwodowa": {"typ": "pozioma", "D": 1.00, "d_n": 0.10, "mat": "XPS300", "glebokosc": 0.45,
                              "opis": "izolacja przeciwprzemarzaniowa XPS 10 cm × 1,00 m (garaż 1,20 m) wokół płyty, spadek 2 % od budynku"},
        "uwagi": "posadowienie bezpośrednie na piaskach średnich (I_D ≈ 0,6), niewysadzinowych; ZWG ≈ 3,8 m p.p.t. — drenaż opaskowy zbędny (W-285); "
                 "zdjęcie humusu 0,4 m, podsypka zagęszczona; uziom otokowy w gruncie pod XPS (W-286/W-187)"}

# ---- schody SCH1 (P0→P1) i SCH2 (P1→P2): dwubiegowe, 2 × 9 podnóżków 17,5 / 28 cm (2h + s = 0,63 m), biegi 1,15 / 1,145 m
def schody(sid, z_k, na_k, z0):
    return {"id": sid, "z_kond": z_k, "na_kond": na_k, "liczba_stopni": 2 * N_BIEG, "wys_stopnia": H_ST, "szer_stopnia": S_ST,
            "biegi": [{"start": [r((B1_X0 + B1_X1) / 2), Y_SCH0], "kierunek": [0, 1], "szer": r(B1_X1 - B1_X0), "stopni": N_BIEG},
                      {"start": [7.82, Y_SPOCZ], "kierunek": [0, -1], "szer": r(B2_X1 - B2_X0), "stopni": N_BIEG}],
            "spoczniki": [{"obrys": R(XC_e, Y_SPOCZ, XD_w, Y4_i), "rzedna": r(z0 + N_BIEG * H_ST)}],
            "plyta": {"grubosc": 0.18}, "mat": "ZB_C25",
            "uwagi": "płyty biegów ŻB 18 cm oparte na ścianach C/D i ściance środkowej; stopnie dębowe; prześwit nad biegiem ≈ 2,75 m (≥ 2,00)"}


SCHODY = [schody("SCH1", "P0", "P1", 0.0), schody("SCH2", "P1", "P2", Z_P1)]


def pochwyty(z0, n):
    """Jeden pochwyt ciągły wokół ścianki środkowej (bieg 1 → obejście końca ścianki → bieg 2), oś pochwytu 0,071 m od lica
    (0,05 m odstępu + Ø42/2 — W-096); szerokość użytkowa biegu 1,15 − 0,092 = 1,058 m ≥ 1,00 (W-091)."""
    xw, xe = XM_w - 0.071, XM_e + 0.071
    zs = z0 + N_BIEG * H_ST
    ye = r(Y_SPOCZ + 0.071)
    return [{"id": f"BL{n}", "polilinia": [[r(xw), Y_SCH0, r(z0 + H_ST)], [r(xw), Y_SPOCZ, r(zs)], [r(xw), ye, r(zs)], [r(xe), ye, r(zs)],
                                          [r(xe), Y_SPOCZ, r(zs + H_ST)], [r(xe), Y3_n, r(z0 + 2 * N_BIEG * H_ST)]],
             "wys": 0.90, "typ": "pochwyt stal nierdzewna Ø42 na wspornikach, ciągły wokół ścianki środkowej (W-095/W-096); "
                                 "od strony ścian C/D — ściany pełne, brak krawędzi otwartej"}]


BALUSTRADY = pochwyty(0.0, 1) + pochwyty(Z_P1, 2)

LAMELE = [
    {"id": "LAM-S", "elewacja": "S", "linia": [[X2o, -EXT], [xE + EXT, -EXT]], "z_od": Z_OKAP_2[1], "z_do": Z_OKAP_3[0], "rozstaw": 0.12, "b": 0.04,
     "h": 0.08, "odsuniecie": 0.15, "mat": "DREWNO_TERMO", "uwagi": "bryła A — pionowe lamele na 2 ryglach, konsole z przekładką (χ); stała osłona okien P2"},
    {"id": "LAM-W", "elewacja": "W", "linia": [[X2o, -EXT], [X2o, y3 + EXT]], "z_od": Z_OKAP_2[1], "z_do": Z_OKAP_3[0], "rozstaw": 0.12, "b": 0.04,
     "h": 0.08, "odsuniecie": 0.15, "mat": "DREWNO_TERMO", "uwagi": "czoło wspornika bryły A"},
    {"id": "LAM-E", "elewacja": "E", "linia": [[xE + EXT, -EXT], [xE + EXT, y3 + EXT]], "z_od": 6.20, "z_do": Z_OKAP_3[0], "rozstaw": 0.12, "b": 0.04,
     "h": 0.08, "odsuniecie": 0.15, "mat": "DREWNO_TERMO", "uwagi": "czoło wsch. bryły A"},
    {"id": "LAM-P0", "elewacja": "S", "linia": [[5.90, 3.80], [8.70, 3.80]], "z_od": 0.0, "z_do": 2.10, "rozstaw": 0.10, "b": 0.03, "h": 0.06,
     "odsuniecie": 0.0, "mat": "DAB_LAMELA", "uwagi": "ekran wewnętrzny P0 wydzielający pas komunikacyjny przy schodach (przeszczep J1 z W3)"},
]

TARASY = [
    {"id": "T1", "obrys": P((-3.30, -3.30), (xE + EXT, -3.30), (xE + EXT, -EXT), (-EXT, -EXT), (-EXT, y3), (-3.30, y3)), "rzedna": -0.02,
     "nawierzchnia": "deska kompozytowa na legarach i wspornikach regulowanych, szczeliny 5 mm; odwodnienie liniowe przy progach HS", "grubosc": 0.05,
     "uwagi": "taras ogrodowy w kształcie L (pd. przed E pod okapem 1,00 m, zach. pod okapem 1,50 m) — 4,30 m od granicy zach."},
    {"id": "T2", "obrys": R(9.40, y4 + EXT, xE - EXT, 10.35), "rzedna": -0.02, "nawierzchnia": "płyty betonowe 60×60 na podsypce, spadek 2 % od drzwi",
     "grubosc": 0.08, "uwagi": "podest wejścia głównego pod daszkiem (bez stopni — cokół przejęty rzędną terenu)"},
    {"id": "T3", "obrys": R(12.20, -1.30, 13.50, -EXT), "rzedna": -0.02, "nawierzchnia": "płyty betonowe 60×60, spadek 2 % od drzwi", "grubosc": 0.08,
     "uwagi": "podest drzwi gospodarczych pod okapem E"},
]


# =====================================================================================================================
# 9. STOLARKA (dane przykładowe typowych wyrobów, „lub równoważne”), WĘZŁY (katalog do symulacji ISO 10211), ENERGIA,
#    KONSTRUKCJA, GEOTECHNIKA
# =====================================================================================================================
STOLARKA = {
    "FX1": {"wyrob": "fix_ALU_3sz", "opis": "przeszklenie stałe ALU 3-szybowe, 1,90 × 2,75 m, VSG od wewn. (strefa uderzeń)", "U_w": 0.75, "g_n": 0.50},
    "FX2": {"wyrob": "fix_ALU_3sz", "opis": "przeszklenie stałe ALU 3-szybowe, 2,93 × 2,75 m", "U_w": 0.73, "g_n": 0.50},
    "FX3": {"wyrob": "fix_ALU_3sz", "opis": "doświetle drzwi wejściowych 0,35 × 2,40 m, VSG mleczne", "U_w": 0.85, "g_n": 0.40},
    "HS1": {"wyrob": "HS_ALU_3sz", "opis": "drzwi podnoszono-przesuwne ALU 2,335 × 2,75 m, próg termiczny bezprogowy, odwodnienie liniowe", "U_w": 0.85, "g_n": 0.50},
    "HS2": {"wyrob": "HS_ALU_3sz", "opis": "drzwi HS ALU 2,40 × 2,75 m (taras zach.)", "U_w": 0.85, "g_n": 0.50},
    "BC1": {"wyrob": "okno_ALU_3sz", "opis": "boks C: 3 kwatery 2,335 × 1,50 m (środkowa RU), dolna część stała VSG do 0,85 m", "U_w": 0.80, "g_n": 0.50},
    "OZ1": {"wyrob": "okno_ALU_3sz", "opis": "okno RU 1,80 × 1,50 m", "U_w": 0.80, "g_n": 0.50},
    "OE1": {"wyrob": "okno_ALU_3sz", "opis": "okno RU 1,50 × 1,50 m", "U_w": 0.80, "g_n": 0.50},
    "ON1": {"wyrob": "okno_PVC_3sz", "opis": "okno uchylne 0,80 × 0,60 m, szkło mleczne", "U_w": 0.90, "g_n": 0.50},
    "ON2": {"wyrob": "okno_PVC_3sz", "opis": "okno uchylne 0,90 × 0,60 m, szkło mleczne", "U_w": 0.90, "g_n": 0.50},
    "ON3": {"wyrob": "okno_PVC_3sz", "opis": "okno uchylne 1,20 × 0,60 m", "U_w": 0.88, "g_n": 0.50},
    "ON4": {"wyrob": "okno_ALU_3sz", "opis": "okno klatki 1,70 × 1,50 m (P2), uchylne do wewn.", "U_w": 0.80, "g_n": 0.50},
    "OP1": {"wyrob": "okno_ALU_3sz", "opis": "okno P2 3,00 × 2,00 m, parapet 0,60 — dolna część stała VSG do 0,85, skrzydła do wewn. (W-097/098)",
            "U_w": 0.78, "g_n": 0.50},
    "OP2": {"wyrob": "okno_ALU_3sz", "opis": "okno P2 1,20 × 1,75 m, skrzydło RU do wewn.", "U_w": 0.82, "g_n": 0.50},
    "OP3": {"wyrob": "okno_ALU_3sz", "opis": "okno P2 2,40 × 2,00 m, parapet 0,60 — dolna część stała VSG do 0,85", "U_w": 0.79, "g_n": 0.50},
    "DZ1": {"wyrob": "drzwi_zewn", "opis": "drzwi wejściowe ALU ocieplone 1,10 × 2,40 w murze (światło ościeżnicy ≥ 0,96 × 2,33), próg ≤ 2 cm", "U_D": 0.90},
    "DZ2": {"wyrob": "drzwi_zewn", "opis": "drzwi boczne garażu 1,00 × 2,10 (garaż nieogrzewany)", "U_D": 1.30},
    "DZ3": {"wyrob": "drzwi_zewn", "opis": "drzwi gospodarcze przeszklone ALU 0,90 × 2,75 w systemie fasady E, otwierane na zewn.", "U_D": 1.00},
    "BR1": {"wyrob": "brama_segmentowa", "opis": "brama segmentowa ocieplona 5,00 × 2,25 m, napęd, kratki went. ≥ 0,08 m²", "U_D": 1.50},
    "DG1": {"wyrob": "drzwi_dom_garaz", "opis": "drzwi garaż–dom stalowe ocieplone, szczelne, z samozamykaczem 0,90 × 2,10", "U_D": 1.10},
    "D1": {"opis": "drzwi wewnętrzne pełne 0,90 × 2,10 w murze (światło ościeżnicy ≥ 0,80 × 2,00), bez progu"},
    "D2": {"opis": "drzwi łazienkowe/WC 0,90 × 2,10, otwierane na zewnątrz, z tuleją/podcięciem ≥ 0,022 m²"},
    "D2P": {"opis": "drzwi przesuwne naścienne 0,90 × 2,10 (łazienka gościnna), szczelina ≥ 0,022 m²"},
    "D3": {"opis": "drzwi spiżarni 0,80 × 2,00 z kratką"},
    "D4": {"opis": "drzwi pom. technicznego 0,90 × 2,10 z kratką, akustyczne R_w ≥ 32 dB"},
    "DS1": {"opis": "drzwi szklane VSG 0,90 × 2,10 w ściance wiatrołapu, oznakowane (W-067)"},
    "OT1": {"opis": "otwór 1,50 × 2,40 bez stolarki"}, "OT2": {"opis": "otwór 2,40 × 2,40 bez stolarki"},
}

# ---- długości węzłów z geometrii
_hot = Polygon(R(-EXT, -EXT, xE + EXT, y4 + EXT)).union(Polygon(R(xE + EXT, -EXT, xF + EXT, y2)))
_gar = Polygon(R(xE - EXT, y2, xF + EXT, y5 + EXT))
L_COKOL = r(_hot.exterior.difference(_gar.buffer(0.05)).length, 2)
L_GAR = r(2 * ((y4 - y2) + (xF - xE)), 2)
L_ATT_D1 = r(Polygon(OB_P2).exterior.length, 2)
L_ATT_P1 = r((y4 - y3) * 2 + (xB - EXT + EXT) + (xE + EXT - xD - EXT), 2)
L_ATT_D4 = r((xF - xE) + (y2 + EXT), 2)


def _obwod_otw(zewn_only=True):
    tot = 0.0
    for o in OT:
        s = _SC[o["sciana"]]
        if zewn_only and s["przegroda"] not in ("SZ1", "SZ2", "SZL"):
            continue
        if o["typ"] in ("otwor", "brama") or s["id"] in ("S0-03", "S0-04", "S0-05"):
            continue
        tot += 2 * (o["szer"] + o["wys"])
    return r(tot, 2)


WEZLY = [
    {"id": "WZ-01", "nazwa": "Attyka stropodachu bryły A (D1)", "typ": "attyka", "przegrody": ["SD1", "AT1", "SZ2", "SZ1"], "dlugosc": L_ATT_D1},
    {"id": "WZ-02", "nazwa": "Attyki dachów P1 (D2, D3) — poza ścianami bryły A", "typ": "attyka", "przegrody": ["SD2", "AT1", "SZ1"], "dlugosc": L_ATT_P1},
    {"id": "WZ-03", "nazwa": "Attyka dachu zielonego nad pasem gospodarczym (linia D, część ogrzewana)", "typ": "attyka", "przegrody": ["DZ1", "AT1", "SZ1"],
     "dlugosc": L_ATT_D4},
    {"id": "WZ-04", "nazwa": "Okap E (PL-E) i daszek wejścia — łącznik termoizolacyjny", "typ": "plyta_wspornikowa_lacznik", "przegrody": ["OK1", "POD-1", "SZ1"],
     "dlugosc": r(12.6 + 5.425 + 1.5 + 2.30, 2)},
    {"id": "WZ-05", "nazwa": "Krawędź ST2 (PL-2) — łącznik termoizolacyjny pod bryłą A", "typ": "plyta_wspornikowa_lacznik", "przegrody": ["OK1", "POD-1", "SZ2"],
     "dlugosc": r(12.6 + 1.0 + (y3 + 2 * EXT), 2)},
    {"id": "WZ-06", "nazwa": "Krawędź ST3 (PL-3) — łącznik termoizolacyjny przy attyce bryły A", "typ": "plyta_wspornikowa_lacznik",
     "przegrody": ["OK1", "SD1", "SZ2"], "dlugosc": r(13.6 + 2 * (y3 + 2 * EXT), 2)},
    {"id": "WZ-07", "nazwa": "Strop P2 nad powietrzem zewnętrznym (ST2Z) — krawędzie wspornika bryły A", "typ": "strop_zewn_krawedz",
     "przegrody": ["POD-1", "SUF-ZEW", "SZL", "SZ1"], "dlugosc": r(2 * (y3 + 2 * EXT) + 2.0, 2)},
    {"id": "WZ-08", "nazwa": "Cokół: ściana zewn. – płyta fundamentowa na XPS (część ogrzewana)", "typ": "sciana_grunt", "przegrody": ["SZ1", "POD-0"],
     "dlugosc": L_COKOL},
    {"id": "WZ-09", "nazwa": "Połączenia dom–garaż nieogrzewany (ściany osi E i 2 z płytą i stropem; docieplenie pasem 1,0 m — SUF-G)",
     "typ": "polaczenie_nieogrz", "przegrody": ["SWG", "POD-0", "DZ1", "SUF-G"], "dlugosc": L_GAR},
    {"id": "WZ-10", "nazwa": "Strop pośredni ST1/ST2 – ściana zewn. z ETICS ciągłym (wieniec)", "typ": "strop_posredni", "przegrody": ["POD-1", "SZ1"],
     "dlugosc": r(2 * (12.6 + 9.35) - 12.6 - 5.425 + 2 * (xE - xD + y4 - y3) + 2 * (xB + y4 - y3), 2)},
    {"id": "WZ-11", "nazwa": "Ościeża, nadproża, podokienniki i progi — ciepły montaż w warstwie izolacji", "typ": "oscieze", "przegrody": ["SZ1", "SZ2", "SZL"],
     "dlugosc": _obwod_otw()},
    {"id": "WZ-12", "nazwa": "Narożniki wypukłe ścian zewnętrznych", "typ": "naroznik_wypukly", "przegrody": ["SZ1", "SZ2"],
     "dlugosc": r(4 * 3.15 + 2 * 3.15 + 4 * 3.15 + 6 * 3.00, 2)},
    {"id": "WZ-13", "nazwa": "Konsole rusztu lamel (przekładka termiczna)", "typ": "konsola_lamel", "przegrody": ["SZ2", "SZL"],
     "liczba": int(round(2 * (13.6 + 2 * (y3 + 2 * EXT)) / 1.0))},
    {"id": "WZ-14", "nazwa": "Konsole ramy boksu C i pasa D (punktowe, przekładka termiczna)", "typ": "kotwa", "przegrody": ["SZ1"], "liczba": 10},
    {"id": "WZ-15", "nazwa": "Przejścia instalacji przez przegrody zewnętrzne (wywiewka K1, czerpnia, wyrzutnia, PC, wpusty, przyłącza)",
     "typ": "przejscie_instalacji", "przegrody": ["SD1", "DZ1", "SZ1", "POD-0"], "liczba": 16},
    {"id": "WZ-16", "nazwa": "Belki wspornikowe B4/B5 i belka B3 w linii izolacji wspornika bryły A (ciągłość wełny pod ST2Z)",
     "typ": "strop_zewn_krawedz", "przegrody": ["SZ1", "SZL", "SUF-ZEW"], "dlugosc": r(2 * 1.12, 2)},
]

ENERGIA = {
    "n50": 1.0, "osoby": 5, "pojemnosc": "ciezka", "chlodzenie": False, "psi_wariant": "domyslna",
    "grunt": {"typ": "piasek", "lambda": 2.0, "izolacja_obwodowa": {"typ": "pozioma", "D": 1.0, "d_n": 0.10, "lam_n": 0.036}},
    "wentylacja": {"centrala": "RVU_450", "czerpnia": [11.40, 1.00, 9.95], "wyrzutnia": [1.80, 3.00, 10.00], "wyrzut": "pionowy",
                   "zestaw_zblokowany": False, "wywiewki_kanalizacyjne": [[5.57, 6.20]], "rzedna_terenu": -0.25,
                   "uwagi": "czerpnia i wyrzutnia dachowe ≥ 0,40 m nad pokryciem; czerpnia ≥ 6 m od wywiewki K1 (7,8 m) i ≥ 6 m od wyrzutni "
                            "(9,8 m); wyrzutnia ≥ 3 m od krawędzi dachu (W-166, W-167); K2 zakończony zaworem napowietrzającym (W-139)"},
    "ogrzewanie": {"zrodlo": "PC_R290_monoblok", "temp_zasilania": 35,
                   "uwagi": "PC powietrze–woda monoblok R290 (W-155), moduł hydrauliczny w pom. 0.12; ogrzewanie podłogowe z regulacją pokojową (W-152)"},
    "cwu": {"zasobnik": "Z250", "V_projekt_dm3": 300, "cyrkulacja": False,
            "uwagi": "projektowo zasobnik 300 dm³ (brief) — w bibliotece dane przykładowe Z250; zastąpić DWU wyrobu"},
    "pv": {"moduly": 15, "P_modul_Wp": 430, "azymut": 180, "nachylenie": 10, "PR": 0.80,
           "uwagi": "Σ 6,45 kWp ≤ 6,5 kWp (W-194, art. 29 ust. 4 pkt 3 lit. c PB); niskie stelaże na D1, górna krawędź ≤ +9,78 (nie ponad attykę)"},
    "garaz": {"stanowiska": 2, "otwory_went_m2": 0.10, "n_went": 1.0},
}

KONSTRUKCJA = {
    "klasa_konsekwencji": "CC2", "klasa_niezawodnosci": "RC2", "K_FI": 1.0, "okres_uzytkowania": 50, "klasa_konstrukcji": "S4",
    "beton": {"stropy_sciany": "C25/30 XC1 c_nom 25 mm", "fundament": "C25/30 XC2 c_nom 35 mm (50 mm od gruntu)",
              "krawedzie_wysuniete": "C30/37 XC4+XF1 c_nom 40 mm"},
    "stal_zbrojeniowa": "B500SP", "mur": "silikat kl. 20 gr. 1, zaprawa cienkowarstwowa, kat. wykonania A (f_d = 4,50 MPa, W-270)",
    "obciazenia": {"snieg": "strefa 2, s_k = 0,90 kN/m², zaspy przy uskokach (D4 przy P1, D2/D3 przy P2) + sytuacja wyjątkowa B2 (W-264)",
                   "wiatr": "strefa 1, q_p(h ≤ 11 m) = 0,71 kN/m² (W-265)", "dach_zielony": "substrat nasycony ≈ 1,4 kN/m² (stałe)",
                   "uzytkowe": "stropy kat. A 2,0 kN/m², schody 4,0 kN/m², dachy kat. H 0,4 kN/m² (W-263)"},
    "wsporniki": "EQU: 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb (W-262); ugięcie końca ≤ wysięg/125 (W-268); łączniki termoizolacyjne z ETA (W-272); "
                 "szczelina dylatacyjna nad stolarką pod krawędzią okapu E i ramy C",
    "sciezka_obciazen_wspornika_A": "lekka ściana A' → belka B3 → końce belek wspornikowych B4/B5 (osie 1 i 3, w licu ścian P2) → ściana A P1 "
                                     "(podpora) i przęsło zakotwienia A–B dociążone ścianami P2 i stropem; ST3 w osi A' na belce B6 opartej na narożach ścian",
}
GEOTECHNIKA = {"kategoria": "II", "grunt": {"rodzaj": "piasek średni (MSa), średniozagęszczony", "I_D": 0.6, "phi": 33, "gamma": 18.5, "M0": 80000},
               "ZWG": -3.8, "h_z": 0.8, "humus": 0.4,
               "uwagi": "opinia geotechniczna + dokumentacja badań podłoża (≥ 3 sondowania do 6 m) + projekt geotechniczny (W-280…W-282)"}


# =====================================================================================================================
# 10. ZŁOŻENIE budynek.yaml + zapis (czytelny YAML: sekcje blokowo, elementy w stylu flow, komentarze źródłowe)
# =====================================================================================================================
META = {"nazwa": "Dom LAMELA", "wersja": "1.0", "data": "2026-09-25", "stadium": "koncepcja ostateczna (synteza W2 + przeszczepy W1/W3 + poprawki J1–J3)",
        "autor": "(do uzupełnienia — projektant z uprawnieniami bez ograniczeń)", "zrodlo": "tools/buduj_model.py (model parametryczny)",
        "uwagi": "WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) w brzmieniu do 19.09.2026, stosowane na podstawie art. 102a PB (oświadczenie Inwestora)"}
KOND = [
    {"id": "P0", "nazwa": "Parter", "rzedna": 0.0, "wys_kondygnacji": H_KOND, "wys_w_swietle": r(Z_SPOD_ST1 - 0.01), "podloga": "POD-0"},
    {"id": "P1", "nazwa": "I piętro", "rzedna": Z_P1, "wys_kondygnacji": H_KOND, "wys_w_swietle": r(Z_ST2 - T_STR - Z_P1 - 0.01), "podloga": "POD-1"},
    {"id": "P2", "nazwa": "II piętro", "rzedna": Z_P2, "wys_kondygnacji": r(Z_ST3 - Z_P2), "wys_w_swietle": r(Z_ST3 - T_STR - Z_P2 - 0.01), "podloga": "POD-1"},
]


def fl(o) -> str:
    t = yaml.safe_dump(o, default_flow_style=True, allow_unicode=True, width=10 ** 6, sort_keys=False).strip()
    if t.endswith("\n..."):
        t = t[:-4].strip()
    return t


def blk(o, ind=0) -> str:
    t = yaml.safe_dump(o, default_flow_style=None, allow_unicode=True, width=150, sort_keys=False)
    return "\n".join((" " * ind + ln) if ln else ln for ln in t.rstrip().split("\n"))


def lista(nazwa, elementy, grupuj=None, kom=None) -> list[str]:
    out = [f"{nazwa}:"] if elementy else [f"{nazwa}: []"]
    if kom:
        out.insert(0, f"# {kom}")
    last = object()
    for e in elementy:
        g = grupuj(e) if grupuj else None
        if g != last and g is not None:
            out.append(f"  # --- {g}")
        last = g
        out.append(f"  - {fl(e)}")
    return out


def zapisz_budynek(path: Path):
    L_ = ["# Model budynku „Dom LAMELA” — KONCEPCJA OSTATECZNA (jedno źródło prawdy; schemat: docs/SCHEMAT_MODELU.md).",
          "# PLIK GENEROWANY skryptem tools/buduj_model.py — NIE EDYTOWAĆ RĘCZNIE (zmiany wprowadzać w parametrach skryptu).",
          "# Układ: x → wschód, y → północ, z → góra; (0,0) = oś A × oś 1; ±0,00 = posadzka P0. Wymiary w m.", ""]
    L_ += ["meta: " + fl(META), "uklad: " + fl({"zero_abs": ZERO_ABS, "azymut_osi_y": 0.0}), "osie:",
           "  x: " + fl({k: r(v) for k, v in X.items()}) + "   # A' = oś lekkiej ściany wspornika; M = ścianka środkowa schodów; D' = ścianka WC",
           "  y: " + fl({k: r(v) for k, v in Y.items()}) + "   # H = ścianka holu P1", ""]
    L_ += lista("kondygnacje", KOND) + [""]
    L_ += ["# Materiały — wartości typowe (λ obliczeniowa, ρ, c_p, μ lub sd); źródło w komentarzu każdej pozycji", "materialy:"]
    for k, d, zr in MAT:
        L_.append(f"  {k}: {fl(d)}   # {zr}")
    L_ += ["", "# Przegrody — ściany od wnętrza do zewnątrz; poziome od góry do dołu (brief §9: pełne warstwy)", "przegrody:"]
    for k, d in PRZ.items():
        L_.append(f"  {k}:")
        L_.append(f"    nazwa: {fl(d['nazwa'])}")
        L_.append(f"    typ: {d['typ']}")
        L_.append("    warstwy:")
        for w in d["warstwy"]:
            L_.append(f"      - {fl(w)}")
    L_ += [""] + lista("sciany", SC, lambda e: e["kond"])
    L_ += [""] + lista("otwory", OT, lambda e: e["id"][:2].replace("O", "P"))
    L_ += [""] + lista("pomieszczenia", PM, lambda e: e["kond"])
    L_ += [""] + lista("stropy", STROPY)
    L_ += [""] + lista("dachy", DACHY, kom="odsłonięte fragmenty stropów = dachy (SCHEMAT p. 5.1); D1 — stropodach bryły A (pierwszy = dach główny)")
    L_ += [""] + lista("wsporniki_plyty", WSP)
    L_ += [""] + lista("slupy", SLUPY) + [""] + lista("belki", BELKI)
    L_ += ["", "fundamenty:", f"  typ: {FUND['typ']}", f"  izolacja_obwodowa: {fl(FUND['izolacja_obwodowa'])}", f"  uwagi: {fl(FUND['uwagi'])}"]
    L_ += ["  " + x for x in lista("elementy", FUND["elementy"])]
    L_ += [""] + lista("schody", SCHODY) + [""] + lista("balustrady", BALUSTRADY) + [""] + lista("lamele", LAMELE) + [""] + lista("tarasy", TARASY)
    L_ += ["", "# Stolarka — dane PRZYKŁADOWE typowych wyrobów (klucze: src/lamela/obliczenia/dane/wyroby_przykladowe.yaml), „lub równoważne”",
           "stolarka:"] + [f"  {k}: {fl(v)}" for k, v in STOLARKA.items()]
    L_ += ["", "# Katalog węzłów cieplno-wilgotnościowych (brief §9.2; symulacja PN-EN ISO 10211 — src/lamela/obliczenia/mostki2d)"]
    L_ += lista("wezly", WEZLY)
    L_ += ["", "energia:"] + ["  " + ln for ln in blk(ENERGIA).split("\n")]
    L_ += ["", "konstrukcja:"] + ["  " + ln for ln in blk(KONSTRUKCJA).split("\n")]
    L_ += ["", "geotechnika:"] + ["  " + ln for ln in blk(GEOTECHNIKA).split("\n")]
    path.write_text("\n".join(L_) + "\n", encoding="utf-8")


# =====================================================================================================================
# 11. DZIAŁKA (układ działki: początek = narożnik SW działki 123/4; budynek → działka: p_d = p_b + T)
# =====================================================================================================================
T_DZ = (7.60, 32.70)          # lico zach. P0 7,30 m od granicy W; linia zabudowy y_b = 11,30; ogród pd. ≈ 32 m
DZ_W, DZ_H = 32.0, 50.0


def d(x, y):
    return [r(x + T_DZ[0], 3), r(y + T_DZ[1], 3)]


def Rd(x0, y0, x1, y1):
    return [d(*p) for p in R(x0, y0, x1, y1)]


def H_ist(xp, yp):
    """Teren istniejący (brief §2): płaszczyzna przez rzędne narożników SW 101,10; SE 101,25; NW 101,40; NE 101,55."""
    return round(101.10 + 0.30 * yp / 50.0 + 0.15 * xp / 32.0, 2)


def teren_punkty():
    pts = []
    xs = [0, 5, 10, 15, 20, 25, 30, 32]
    ys = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    for yp in ys:
        for xp in xs:
            pts.append([xp, yp, H_ist(xp, yp)])
    for xp, yp in [(-10, 0), (-10, 25), (-10, 50), (42, 0), (42, 25), (42, 50), (-10, 60), (16, 60), (42, 60), (16, 55)]:
        pts.append([xp, yp, H_ist(max(-10, min(42, xp)), min(yp, 50)) + (0.08 if yp > 50 else 0.0)])
    return [[r(a, 2), r(b, 2), r(c, 2)] for a, b, c in pts]


def teren_projekt():
    """Rzędne projektowane (bezwzględne): cokół ≥ 0,30 m (pierścień 0,5 m = 101,35) poza strefami drzwi; spadek ≥ 2 % na 1,5 m od budynku;
    przy drzwiach — podesty −0,02 z odwodnieniem liniowym; na granicach E, W, S rzędne istniejące (W-019)."""
    P_ = []
    ring = Polygon(OB_P0).buffer(0.5, join_style=2)
    ring2 = Polygon(OB_P0).buffer(2.0, join_style=2)
    for poly, dz in ((ring, 0.0), (ring2, -0.03)):
        c = list(poly.exterior.coords)[:-1]
        dense = []
        for (x0, y0), (x1, y1) in zip(c, c[1:] + c[:1]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) // 3.0))
            dense += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
        for x, y in dense:
            if x > xF + EXT + 0.2 or (y > y4 + EXT + 0.2 and x > xE - 0.5):       # garaż/podjazd — strefa wyższa (wjazd bez stopni)
                h = 101.47
            else:
                h = 101.35
            P_.append([r(x + T_DZ[0], 2), r(y + T_DZ[1], 2), r(h + dz, 2)])
    spec = [((10.60, 9.60), 101.63, "podest wejścia"), ((10.60, 10.40), 101.60, "odwodnienie liniowe OL-3"),
            ((10.60, 13.50), 101.52, "dojście"), ((10.60, 17.10), 101.47, "furtka (spadek do posesji)"),
            ((15.50, 9.95), 101.53, "próg bramy / fartuch"), ((15.50, 10.30), 101.50, "odwodnienie liniowe OL-1"),
            ((15.50, 13.50), 101.55, "grzbiet podjazdu"), ((15.50, 16.90), 101.47, "odwodnienie liniowe OL-4 przy bramie"),
            ((6.00, -0.60), 101.32, "pod tarasem (żwir)"), ((6.00, -4.00), 101.28, "za tarasem"), ((-4.00, 2.00), 101.30, "za tarasem zach."),
            ((16.80, -1.05), 101.40, "fundament jednostki PC"), ((20.50, 4.50), 101.40, "niecka trawiasta wsch. (odpływ na pd.)"),
            ((5.00, 11.30), 101.31, "niecka trawiasta pn. (odpływ na zach.)")]
    for (x, y), h, _ in spec:
        P_.append([r(x + T_DZ[0], 2), r(y + T_DZ[1], 2), h])
    return P_


DZIALKA = {
    "uklad": {"przesuniecie": [T_DZ[0], T_DZ[1]], "obrot": 0.0},
    "dzialka": {"nr": "123/4", "obreb": "0005 Przykładowo", "gmina": "Przykładowo (fikcyjna)", "adres": "ul. Lipowa (fikcyjna)", "pow": 1600.0,
                "obrys": R(0, 0, DZ_W, DZ_H), "mpzp": "uchwała nr XII/123/2024 Rady Gminy Przykładowo z 21.03.2024 — teren 3MN (fikcyjny)"},
    "sasiedzi": [
        {"nr": "123/3", "obrys": R(-32, 0, 0, 50), "zabudowa": R(-20, 22, -8, 32), "opis": "dom jednorodzinny, 2 kondygnacje, dach dwuspadowy (≥ 8 m od granicy)", "wys": 8.5},
        {"nr": "123/5", "obrys": R(32, 0, 64, 50), "zabudowa": R(40, 24, 52, 35), "opis": "dom jednorodzinny parterowy z poddaszem (≥ 8 m od granicy)", "wys": 7.5},
        {"nr": "130", "obrys": R(-32, -40, 64, 0), "zabudowa": [], "opis": "teren rolny (R IVb) — niezabudowany"},
        {"nr": "118/2", "obrys": R(-10, 60, 22, 95), "zabudowa": R(2, 70, 14, 80), "opis": "dom jednorodzinny, dach płaski", "wys": 6.8, "dach": "plaski"},
        {"nr": "118/3", "obrys": R(22, 60, 54, 95), "zabudowa": R(30, 72, 42, 82), "opis": "dom jednorodzinny, dach dwuspadowy", "wys": 8.0},
    ],
    "droga": {"symbol": "1KDD", "nazwa": "ul. Lipowa (fikcyjna), klasa D", "linie_rozgraniczajace": R(-40, 50, 72, 60), "jezdnia": R(-40, 52.25, 72, 57.75),
              "nawierzchnia": "asfalt"},
    "linia_zabudowy": [[0.0, 44.0], [32.0, 44.0]],
    "teren": {"punkty": teren_punkty(), "warstwice_co": 0.10, "punkty_projektowane": teren_projekt(), "ZWG": 97.60,
              "grunt": "0,0–0,4 ziemia urodzajna; piaski średnie I_D ≈ 0,6; ZWG ≈ 3,8 m p.p.t."},
    "utwardzenia": [
        {"id": "U1", "obrys": Rd(xE + EXT, y5 + EXT, xF + EXT, 17.30), "nawierzchnia": "podjazd — kostka betonowa 8 cm grafit na podbudowie (2,5 t)", "spadek": 0.015},
        {"id": "U2", "obrys": Rd(9.95, 10.35, 11.25, 17.30), "nawierzchnia": "dojście — płyty betonowe 60×60 cm, szer. 1,30 m", "spadek": 0.02},
        {"id": "U3", "obrys": Rd(11.25, 10.35, xE + EXT, 11.35), "nawierzchnia": "łącznik dojście–podjazd — płyty betonowe", "spadek": 0.02},
        {"id": "U4", "obrys": Rd(6.40, 15.90, 9.60, 17.20), "nawierzchnia": "stanowisko pojemników — płyty betonowe (osłona z lamel)", "spadek": 0.02},
        {"id": "U5", "obrys": Rd(16.10, -1.45, 17.50, -0.65), "nawierzchnia": "fundament jednostki zewn. PC na wibroizolacji", "spadek": 0.0},
        {"id": "U6", "obrys": Rd(13.50, -1.30, 14.40, -0.30), "nawierzchnia": "ścieżka gospodarcza — płyty w trawie (ażur, poza PBC)", "spadek": 0.02},
    ],
    "zielen": [
        {"id": "Z1", "obrys": R(0, 0, DZ_W, DZ_H), "typ": "trawnik"},
        {"id": "Z2", "obrys": R(0.3, 0.3, 1.3, 49.0), "typ": "zywoplot", "wys": 1.8},
        {"id": "Z3", "obrys": R(30.7, 0.3, 31.7, 45.0), "typ": "zywoplot", "wys": 1.8},
        {"id": "Z4", "obrys": R(1.3, 0.3, 30.7, 1.3), "typ": "zywoplot", "wys": 1.6},
        {"id": "Z5", "obrys": Rd(1.00, 10.40, 9.60, 11.10), "typ": "rabata"},
        {"id": "Z6", "obrys": Rd(-6.80, 11.60, 6.20, 16.60), "typ": "rabata", "wys": 0.6},
    ],
    "drzewa": [
        {"id": "DR1", "xy": d(5.0, -19.0), "gat": "lipa drobnolistna (soliter na osi ogrodu)", "sr_korony": 7.0, "istn": False, "do_wyciecia": False, "wys": 10.0},
        {"id": "DR2", "xy": d(-5.0, -8.0), "gat": "klon polny (cień letni tarasu zach.)", "sr_korony": 5.0, "istn": False, "do_wyciecia": False, "wys": 8.0},
        {"id": "DR3", "xy": d(-4.5, -14.0), "gat": "grab pospolity", "sr_korony": 4.5, "istn": False, "do_wyciecia": False, "wys": 7.0},
        {"id": "DR4", "xy": d(16.0, -14.0), "gat": "jabłoń", "sr_korony": 4.0, "istn": False, "do_wyciecia": False, "wys": 5.0},
        {"id": "DR5", "xy": d(20.5, -26.0), "gat": "brzoza brodawkowata (istniejąca, zachowana)", "sr_korony": 4.0, "istn": True, "do_wyciecia": False, "wys": 12.0},
        {"id": "DR6", "xy": d(-4.5, -27.0), "gat": "sosna zwyczajna (istniejąca, zachowana)", "sr_korony": 4.5, "istn": True, "do_wyciecia": False, "wys": 11.0},
        {"id": "DR7", "xy": d(21.5, 14.8), "gat": "grab kolumnowy (zieleń przy wjeździe)", "sr_korony": 2.0, "istn": False, "do_wyciecia": False, "wys": 6.0},
    ],
    "ogrodzenie": [
        {"linia": [[0.0, 50.0], [17.60, 50.0]], "wys": 1.50, "typ": "od drogi: ażurowe, sztachety stalowe pionowe grafit, bez prefabrykatów betonowych (MPZP)"},
        {"linia": [[18.60, 50.0], [20.30, 50.0]], "wys": 1.50, "typ": "ażurowe; wnęka ZK w słupku stalowym"},
        {"linia": [[25.90, 50.0], [32.0, 50.0]], "wys": 1.50, "typ": "ażurowe (tor najazdu bramy przesuwnej)"},
        {"linia": [[32.0, 50.0], [32.0, 0.0], [0.0, 0.0], [0.0, 50.0]], "wys": 1.50, "typ": "panele siatkowe zgrzewane grafit z żywopłotem"},
    ],
    "bramy": [{"xy": [23.10, 50.0], "szer": 5.60, "typ": "przesuwna", "kierunek": [1.0, 0.0], "wys": 1.50},
              {"xy": [18.10, 50.0], "szer": 1.00, "typ": "furtka", "wys": 1.50}],
    "miejsca_postojowe": [
        {"id": "MP1", "obrys": Rd(12.40, 3.20, 15.10, 9.10), "typ": "garaz"},
        {"id": "MP2", "obrys": Rd(15.30, 3.20, 18.00, 9.10), "typ": "garaz"},
        {"id": "MP3", "obrys": Rd(12.90, 11.90, 15.40, 16.90), "typ": "zewn", "auto": False},
        {"id": "MP4", "obrys": Rd(15.60, 11.90, 18.10, 16.90), "typ": "zewn", "auto": False},
    ],
    "odpady": {"obrys": Rd(6.40, 15.90, 9.60, 17.20), "opis": "osłona z lamel na 4 pojemniki 240 l (segregacja), przy furtce; odległości wg WT §23 ust. 4 "
                                                             "nieokreślone dla zabudowy jednorodzinnej (W-016)"},
}

ZBIORNIK = d(4.00, -7.00)
NIECKA = Rd(1.00, -17.00, 7.00, -13.00)
DZIALKA.update({
    "uzbrojenie": {
        "istniejace": [
            {"branza": "woda", "linia": [[-40, 54.0], [72, 54.0]], "opis": "wodociąg PE 110 (ul. Lipowa)"},
            {"branza": "kan_sanit", "linia": [[-40, 55.6], [72, 55.6]], "opis": "kanalizacja sanitarna PVC 200, dno ≈ 99,20"},
            {"branza": "en", "linia": [[-40, 51.0], [72, 51.0]], "opis": "kabel nN 0,4 kV (OSD)"},
            {"branza": "tele", "linia": [[-40, 51.4], [72, 51.4]], "opis": "kanalizacja teletechniczna / światłowód"},
            {"branza": "gaz", "linia": [[-40, 58.5], [72, 58.5]], "opis": "gazociąg PE 63 — NIE wykorzystywany (dom all-electric)"},
        ],
        "projektowane": [
            {"branza": "woda", "linia": [[23.0, 54.0], [23.0, 44.0], [23.0, 35.2]], "opis": "przyłącze PE 40, przykrycie ≥ 1,20 m (W-141), pod podjazdem i płytą garażu "
             "w rurze osłonowej, wodomierz w pom. 0.12", "dl": 18.8},
            {"branza": "kan_sanit", "linia": [[13.0, 41.75], [13.0, 43.80], [13.0, 55.6]], "opis": "przykanalik PVC-U 160, i ≥ 2 %, studzienka rewizyjna SR1 Ø425 "
             "(x 13,0; y 43,8) — wyjście z płyty pod ścianą pn. (piony K1, K2)", "dl": 13.9},
            {"branza": "en", "linia": [[19.40, 51.0], [19.40, 49.80], [19.40, 43.20], [24.60, 43.20], [24.60, 35.20]],
             "opis": "ZKP w linii ogrodzenia (pole odczytowe ≥ 0,48 m nad terenem) → WLZ YKY 5×16 do RG w pom. 0.12, rura osłonowa pod podjazdem/garażem",
             "dl": 18.2},
            {"branza": "tele", "linia": [[19.70, 51.4], [19.70, 43.50], [24.90, 43.50], [24.90, 35.20]], "opis": "2 × HDPE Ø40 + mikrokabel światłowodowy (W-196)",
             "dl": 21.3},
            {"branza": "kan_deszcz", "linia": [[16.80, 42.40], [4.00, 42.40], [4.00, 29.00], ZBIORNIK], "opis": "kolektor KD-W PVC 160 (RS3, RS4, RS1/RS2 z SI)",
             "dl": 34.8},
            {"branza": "kan_deszcz", "linia": [[26.40, 41.75], [27.20, 41.75], [27.20, 28.20], [ZBIORNIK[0], 28.20], ZBIORNIK],
             "opis": "kolektor KD-E PVC 160 (RS5 dach garażu, RS6 z pom. technicznego)", "dl": 31.6},
            {"branza": "kan_deszcz", "linia": [ZBIORNIK, [10.60, 22.00], d(4.00, -13.00)], "opis": "przelew zbiornika DN160 do niecki chłonnej", "dl": 6.2},
        ],
        "obiekty": [
            {"id": "ZKP", "xy": [19.40, 49.80], "opis": "złącze kablowo-pomiarowe we wnęce ogrodzenia, PWP przy wejściu (W-190)"},
            {"id": "SR1", "xy": [13.00, 43.80], "opis": "studzienka rewizyjna kanalizacji Ø425 (poza garażem — W-118)"},
            {"id": "PC-JZ", "xy": d(16.80, -1.05), "opis": "jednostka zewn. PC monoblok R290 w osłonie lamelowej z ekranem akustycznym od tarasu; "
             "7,0 m od granicy E (≥ 6,0 — W-024); strefa R290 1,0 m bez otworów, wpustów i studzienek (W-156)"},
            {"id": "SK-PC", "xy": d(16.80, -2.90), "opis": "studnia chłonna skroplin PC (żwir, ≥ 0,8 m p.p.t.), poza strefą R290 (W-146)"},
            {"id": "HYDR", "xy": [-30.0, 56.0], "opis": "najbliższy hydrant zewnętrzny DN80 (ul. Lipowa) — zaopatrzenie ppoż. (W-217) [do potwierdzenia]"},
        ],
    },
    "retencja": {
        "zbiornik": {"xy": ZBIORNIK, "V": 5.0, "opis": "szczelny zbiornik PE 5,0 m³ z osadnikiem i filtrem, pompa do podlewania, przelew DN160 do niecki; "
                     "≥ 3,0 m od budynku, ≥ 2,0 m od granic (W-145: wariant bazowy, nie jest urządzeniem wodnym)"},
        "rozsaczanie": {"obrys": NIECKA, "V": 7.2, "typ": "niecka", "glebokosc": 0.30,
                        "opis": "niecka chłonna (ogród deszczowy) 24 m², głęb. 0,30 m, ≥ 3,0 m od fundamentów, ≥ 2,0 m od granic, ≥ 1,0 m od drzew (W-144)"},
    },
    "odwodnienia": [
        {"id": "OL-1", "typ": "liniowe", "linia": [d(xE + EXT + 0.2, 10.30), d(xF + EXT - 0.2, 10.30)], "spadek": 0.005, "odbiornik": "KD-E",
         "opis": "odwodnienie liniowe przed bramą garażu (W-019)"},
        {"id": "OL-2", "typ": "liniowe", "linia": [d(0.30, -EXT - 0.10), d(11.70, -EXT - 0.10)], "spadek": 0.005, "odbiornik": "opaska / KD-W",
         "opis": "odwodnienie liniowe przy progach HS (bezprogowe) pod deską tarasu"},
        {"id": "OL-2W", "typ": "liniowe", "linia": [d(-EXT - 0.10, 1.10), d(-EXT - 0.10, 3.70)], "spadek": 0.005, "odbiornik": "KD-W",
         "opis": "odwodnienie liniowe przy HS zach."},
        {"id": "OL-3", "typ": "liniowe", "linia": [d(9.50, 10.40), d(11.60, 10.40)], "spadek": 0.005, "odbiornik": "KD-W", "opis": "odwodnienie liniowe podestu wejścia"},
        {"id": "OL-4", "typ": "liniowe", "linia": [d(xE + EXT + 0.2, 16.90), d(xF + EXT - 0.2, 16.90)], "spadek": 0.005, "odbiornik": "KD-E",
         "opis": "odwodnienie liniowe przy bramie wjazdowej — woda nie spływa na drogę (MPZP, u.d.p. art. 39)"},
        {"id": "OZ-1", "typ": "opaska_zwirowa", "obrys": [[r(x + T_DZ[0], 3), r(y + T_DZ[1], 3)] for x, y in
                                                          list(Polygon(OB_P0).buffer(0.5, join_style=2).exterior.coords)[:-1]],
         "szer": 0.50, "opis": "opaska żwirowa 16/32 szer. 0,5 m na geowłókninie wokół budynku (poza tarasem, podestami i podjazdem)"},
        {"id": "NT-N", "typ": "niecka", "linia": [d(-3.60, 11.30), d(11.00, 11.30)], "spadek": 0.005, "odbiornik": "KD-W",
         "opis": "płytka niecka trawiasta przed elewacją pn. (przechwyt spływu od drogi), spadek na zachód"},
        {"id": "NT-E", "typ": "niecka", "linia": [d(20.60, 9.00), d(20.60, -4.00)], "spadek": 0.006, "odbiornik": "ogród pd.",
         "opis": "płytka niecka trawiasta wzdłuż elewacji wsch. garażu (teren od granicy E wyższy), spadek na południe"},
        {"id": "NCH-1", "typ": "niecka", "obrys": NIECKA, "odbiornik": "grunt (piaski, ZWG 3,8 m p.p.t.)", "opis": "niecka chłonna — przelew zbiornika"},
        {"id": "DR-0", "typ": "drenaz_opaskowy", "linia": [], "opis": "NIE PROJEKTUJE SIĘ — piaski przepuszczalne, ZWG ≈ 3,8 m p.p.t., posadowienie ≈ 0,5 m p.p.t. "
         "(W-285); ochrona płyty: XPS + membrana SBS, opaska żwirowa i spadki terenu"},
    ],
    "obszar_oddzialywania": {"opis": "Obszar oddziaływania obiektu mieści się w całości w granicach działki 123/4 (PB art. 3 pkt 20): odległości od granic "
                             "≥ 4,0 m (ściany z otworami ≥ 5,70 m, płyty ≥ 5,20 m), przesłanianie i nasłonecznienie sąsiednich budynków (≥ 8 m od granic) "
                             "bez ograniczeń (WT §13, §60), hałas PC ≤ 40 dB(A) nocą na granicy (W-024), wody opadowe zagospodarowane na działce "
                             "(PW art. 234), brak odprowadzania na drogę."},
})


# =====================================================================================================================
# 12. WYPOSAŻENIE (meble, sanitariaty, kuchnia, urządzenia) i INSTALACJE (lokalizacje, piony) — format: model/test/*.yaml
# =====================================================================================================================
def F(kond, typ, xy, obrot, wym, **kw):
    return {"kond": kond, "typ": typ, "xy": [r(xy[0]), r(xy[1])], "obrot": obrot, "wym": list(wym), **kw}


XBS = XC_w     # lico wsch. łazienek pionu SI (5,77)
WYP = [
    # ---- P0
    F("P0", "szafa", (XE_i, 7.67), 180, (1.90, 0.60), opis="szafa wiatrołapu"),
    F("P0", "szafa", (XE_i, 5.89), 180, (1.30, 0.60), opis="szafa wejściowa"),
    F("P0", "wc", (9.20, Y4_i), -90, (0.40, 0.60)), F("P0", "umywalka", (XD_e, 7.60), 0, (0.45, 0.30)),
    F("P0", "prysznic", (XB_i := xB + INT, 8.10), 0, (1.00, 0.90)), F("P0", "wc", (XBS, 7.20), 180, (0.40, 0.60)),
    F("P0", "umywalka", (XBS, 8.20), 180, (0.60, 0.45)),
    F("P0", "lozko", (2.20, Y4_i), -90, (1.60, 2.00)), F("P0", "biurko", (XA_i, 6.10), 0, (1.20, 0.60)),
    F("P0", "szafa", (1.90, Y3_n), 90, (1.80, 0.60)),
    F("P0", "sofa", (2.30, 3.40), -90, (2.80, 0.95), opis="salon — widok na ogród"),
    F("P0", "stol", (6.60, 2.10), 0, (2.20, 1.00), krzesla=8),
    F("P0", "wyspa", (9.80, 2.70), 90, (2.20, 1.00), opis="wyspa z płytą indukcyjną i okapem"),
    {"kond": "P0", "typ": "blat", "linia": [[XE_i, 1.40], [XE_i, Y3_s]], "gl": 0.6, "strona": 1, "gorne": True},
    F("P0", "zlew", (XE_i, 2.60), 180, (0.80, 0.50)), F("P0", "zmywarka", (XE_i, 1.90), 180, (0.60, 0.58)),
    F("P0", "plyta", (10.30, 2.70), 90, (0.80, 0.52), opis="płyta indukcyjna na wyspie"),
    F("P0", "lodowka", (XE_i, 4.60), 180, (0.60, 0.65)), F("P0", "urzadzenie", (XE_i, 3.90), 180, (0.60, 0.60), opis="piekarnik + mikrofala w słupku"),
    F("P0", "szafa", (XD_w, 6.20), 180, (1.60, 0.40), opis="regały spiżarni"),
    F("P0", "szafa", (xE + INT, 2.00), 0, (1.40, 0.60), opis="szafa przedsionka (odzież, obuwie)"),
    F("P0", "szafa", (14.00, Y1_i), 90, (1.30, 0.35), opis="szafka na obuwie"),
    F("P0", "pompa_ciepla", (15.60, y2 - INT), -90, (0.60, 0.40), opis="moduł hydrauliczny PC R290 (monoblok zewn.)"),
    F("P0", "zasobnik", (16.55, y2 - INT), -90, (0.70, 0.70), opis="zasobnik CWU 300 dm³"),
    F("P0", "zasobnik", (17.50, y2 - INT), -90, (0.55, 0.55), opis="bufor 100 dm³"),
    F("P0", "urzadzenie", (xP + FD, 0.90), 0, (0.80, 0.25), opis="rozdzielnica główna RG"),
    F("P0", "urzadzenie", (xF - INT, 1.20), 180, (0.40, 0.20), opis="wodomierz + zawór antyskażeniowy (PN-EN 1717)"),
    F("P0", "urzadzenie", (16.00, Y1_i), 90, (0.80, 0.15), opis="rozdzielacz ogrzewania podłogowego P0"),
    F("P0", "zlewik", (xF - INT, 2.20), 180, (0.50, 0.40)),
    F("P0", "szafa", (xF - INT, 8.00), 180, (2.40, 0.60), opis="rowery i sprzęt ogrodowy — strefa przednia przy ścianie osi F (przeszczep J1)"),
    # ---- P1
    F("P1", "lozko", (xB - FD, 1.20), 180, (0.90, 2.00)), F("P1", "biurko", (XA_i, 1.90), 0, (1.40, 0.70)),
    F("P1", "szafa", (1.20, yH - FD), -90, (1.80, 0.60)),
    F("P1", "lozko", (2.60, Y4_i), -90, (0.90, 2.00)), F("P1", "biurko", (XA_i, 6.90), 0, (1.40, 0.70)),
    F("P1", "szafa", (xB - INT, 7.30), 180, (1.80, 0.60)),
    F("P1", "sofa", (7.20, 2.60), -90, (2.60, 0.95), opis="pokój rodzinny — widok przez boks C"),
    F("P1", "szafa", (4.95, yH - FD), -90, (1.90, 0.40), opis="regał biblioteki"),
    F("P1", "biurko", (XE_i, 1.95), 180, (1.40, 0.70)),
    F("P1", "wanna", (4.875, Y4_i), -90, (1.70, 0.75)), F("P1", "wc", (5.55, Y_SI + 0.05), 90, (0.40, 0.60)),
    F("P1", "umywalka_blat", (XB_i, 7.20), 0, (0.90, 0.50)),
    F("P1", "prysznic", (9.20, Y4_i), -90, (1.19, 0.90)), F("P1", "wc", (xD2 - FD, 7.20), 180, (0.40, 0.60)),
    F("P1", "umywalka", (XD_e, 6.40), 0, (0.50, 0.35)),
    F("P1", "pralka", (xD2 + FD, 8.20), 0, (0.60, 0.60)), F("P1", "suszarka", (xD2 + FD, 7.55), 0, (0.60, 0.60)),
    F("P1", "zlewik", (XE_i, 8.20), 180, (0.50, 0.40)), F("P1", "szafa", (XE_i, 6.40), 180, (1.60, 0.60), opis="szafa gospodarcza"),
    F("P1", "urzadzenie", (XE_i, 4.40), 180, (0.80, 0.15), opis="rozdzielacz ogrzewania podłogowego P1 (w holu)"),
    # ---- P2
    F("P2", "lozko", (1.30, Y3_s), -90, (1.80, 2.00)),
    F("P2", "szafa", (X_BG + FD, 2.00), 0, (3.00, 0.60)), F("P2", "szafa", (xC - FD, 2.00), 180, (3.00, 0.60)),
    F("P2", "prysznic", (4.875, Y4_i), -90, (1.79, 1.00)), F("P2", "wc", (5.55, Y_SI + 0.05), 90, (0.40, 0.60)),
    F("P2", "umywalka_blat", (XB_i, 7.10), 0, (1.20, 0.50), opis="umywalka podwójna"),
    F("P2", "biurko", (10.20, Y1_i), 90, (1.80, 0.80)), F("P2", "szafa", (xD + FD, 2.00), 0, (2.40, 0.40), opis="regał"),
    F("P2", "sofa", (XE_i, 3.80), 180, (2.00, 0.90), opis="sofa rozkładana (pokój 5. osoby / gościa)"),
    F("P2", "rekuperator", (xC + FD, 1.30), 0, (1.20, 0.70), opis="centrala wentylacyjna 450 m³/h, η_t 85 %"),
    F("P2", "urzadzenie", (xD - FD, 1.30), 180, (0.80, 0.15), opis="rozdzielacz ogrzewania podłogowego P2"),
]
INSTAL = {
    "osoby": 5,
    "lokalizacje": {
        "RG": [xP + FD + 0.1, 0.90, "P0"], "wodomierz": [xF - INT - 0.1, 1.20, "P0"], "zasobnik": [16.55, 2.40, "P0"],
        "rozdzielacze_co": {"P0": [16.00, 0.30], "P1": [11.80, 4.40], "P2": [8.35, 1.30]},
        "ZKP": [r(19.40 - T_DZ[0]), r(49.80 - T_DZ[1])], "studzienka": [r(13.00 - T_DZ[0]), r(43.80 - T_DZ[1])],
        "czerpnia": [11.40, 1.00, 9.95], "wyrzutnia": [1.80, 3.00, 10.00],
        "pompa_ciepla_jz": {"xy": [16.80, -1.05], "ustawienie": "wolnostojaca", "odl_granica_E": 7.0},
    },
    "piony": [{"id": "K1", "xy": [5.57, 6.20], "opis": "pion kanalizacyjny Ø110 w SI, wywiewka ponad dach D1"},
              {"id": "K2", "xy": [9.70, 8.52], "opis": "pion Ø110 (WC P0, WC z natryskiem i pralnia P1), zawór napowietrzający PN-EN 12380"},
              {"id": "RS1", "xy": [5.57, 5.45], "opis": "rura spustowa DN100 w SI"}, {"id": "RS2", "xy": [5.57, 5.85], "opis": "rura spustowa DN100 w SI"},
              {"id": "RS6", "xy": [17.95, 0.35], "opis": "rura spustowa DN100 w pom. technicznym"}],
    "przybory_dodatkowe": [{"kond": "P0", "typ": "zawor_ogrodowy", "xy": [1.00, -EXT], "obrot": -90},
                           {"kond": "P0", "typ": "zawor_ogrodowy", "xy": [xF + EXT, 7.50], "obrot": 0},
                           {"kond": "P0", "typ": "wpust_podlogowy", "xy": [16.00, 1.60], "obrot": 0}],
    "wyroby": {},
}


# =====================================================================================================================
# 13. ZAPIS
# =====================================================================================================================
def zapisz_dzialka(path: Path):
    D = DZIALKA
    L_ = ["# Działka 123/4 — model zagospodarowania (jedno źródło prawdy). PLIK GENEROWANY: tools/buduj_model.py — nie edytować ręcznie.",
          "# Układ działki: początek = narożnik SW działki, x → wschód, y → północ [m]; rzędne H bezwzględne [m n.p.m., PL-EVRF2007-NH].",
          f"# Transformacja budynek → działka: p_d = p_b + {list(T_DZ)} (lico zach. P0 7,30 m od granicy W; linia zabudowy 6,00 m od drogi).", ""]
    L_ += ["uklad: " + fl(D["uklad"]), "dzialka: " + fl(D["dzialka"])]
    L_ += lista("sasiedzi", D["sasiedzi"]) + ["droga: " + fl(D["droga"]), "linia_zabudowy: " + fl(D["linia_zabudowy"]), "teren:",
                                               f"  warstwice_co: {D['teren']['warstwice_co']}", f"  ZWG: {D['teren']['ZWG']}",
                                               f"  grunt: {fl(D['teren']['grunt'])}"]
    L_ += ["  " + x for x in lista("punkty", D["teren"]["punkty"], kom="teren istniejący (siatka 5 m + otoczenie)")]
    L_ += ["  " + x for x in lista("punkty_projektowane", D["teren"]["punkty_projektowane"],
                                   kom="rzędne projektowane: cokół ≥ 0,30 m, spadek ≥ 2 % od budynku (brief §9.6, W-019)")]
    for k in ("utwardzenia", "zielen", "drzewa", "ogrodzenie", "bramy", "miejsca_postojowe"):
        L_ += lista(k, D[k])
    L_ += ["odpady: " + fl(D["odpady"]), "uzbrojenie:"]
    for k in ("istniejace", "projektowane", "obiekty"):
        L_ += ["  " + x for x in lista(k, D["uzbrojenie"][k])]
    L_ += ["retencja:", "  zbiornik: " + fl(D["retencja"]["zbiornik"]), "  rozsaczanie: " + fl(D["retencja"]["rozsaczanie"])]
    L_ += lista("odwodnienia", D["odwodnienia"]) + ["obszar_oddzialywania: " + fl(D["obszar_oddzialywania"])]
    path.write_text("\n".join(L_) + "\n", encoding="utf-8")


def zapisz_wyposazenie(path: Path):
    L_ = ["# Wyposażenie „Dom LAMELA” (meble, sanitariaty, kuchnia, urządzenia) — PLIK GENEROWANY: tools/buduj_model.py.",
          "# Format: model/test/wyposazenie_testowe.yaml (xy — punkt na licu ściany w osi elementu; obrot — kierunek od ściany do pomieszczenia)."]
    L_ += lista("wyposazenie", WYP, lambda e: e["kond"])
    path.write_text("\n".join(L_) + "\n", encoding="utf-8")


def zapisz_instalacje(path: Path):
    L_ = ["# Dane instalacyjne „Dom LAMELA” (SCHEMAT p. 8) — PLIK GENEROWANY: tools/buduj_model.py. Współrzędne w układzie budynku.", "instalacje:"]
    L_ += ["  " + ln for ln in blk(INSTAL).split("\n")]
    path.write_text("\n".join(L_) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    zapisz_budynek(OUT / "budynek.yaml")
    zapisz_dzialka(OUT / "dzialka.yaml")
    zapisz_wyposazenie(OUT / "wyposazenie.yaml")
    zapisz_instalacje(OUT / "instalacje.yaml")
    print(f"zapisano: model/budynek.yaml ({len(SC)} ścian, {len(OT)} otworów, {len(PM)} pomieszczeń, {len(BELKI)} belek), "
          f"model/dzialka.yaml, model/wyposazenie.yaml ({len(WYP)} el.), model/instalacje.yaml")


if __name__ == "__main__":
    main()


# =====================================================================================================================
# 9. STOLARKA (dane przykładowe typowych wyrobów, „lub równoważne”), montaż, osłony, progi — wytyczne symulacji mostków 2D
#    (koordynator, katalog projekt/08_obliczenia/demo_test/mostki): (1) ciepły montaż — rama wsunięta ≤ 5 cm w mur, 4 cm w
#    warstwie izolacji, izolacja ościeża z zakładem 3 cm na ramę; (2) BEZ kaset rolet w ociepleniu — kasety w okapach/ramie C/
#    szczelinie lamel albo nadstawne przed licem ETICS; (5) progi HS/wejścia — profil progowy termoizolacyjny na podwalinie
#    z XPS/PUR-GF + odwodnienie liniowe.
# =====================================================================================================================
STOLARKA = {
    "FX1": dict(wyrob="fix_ALU_3sz", opis="Przeszklenie stałe fasady E 1,90 × 2,75 m, Al z przekładką, 3 szyby, VSG od wewn.", U_w_max=0.9, g_n=0.50),
    "FX2": dict(wyrob="fix_ALU_3sz", opis="Przeszklenie stałe fasady E 2,93 × 2,75 m (kuchnia)", U_w_max=0.9, g_n=0.50),
    "FX3": dict(wyrob="fix_ALU_3sz", opis="Doświetle boczne drzwi wejściowych 0,545 × 2,40 m, VSG satynowane", U_w_max=0.9, g_n=0.50),
    "HS1": dict(wyrob="HS_ALU_3sz", opis="Drzwi podnoszono-przesuwne HS 2,335 × 2,75 m, próg termiczny ≤ 2 cm", U_w_max=0.9, g_n=0.50),
    "HS2": dict(wyrob="HS_ALU_3sz", opis="Drzwi HS 2,40 × 2,75 m — taras zachodni", U_w_max=0.9, g_n=0.50),
    "BC1": dict(wyrob="okno_ALU_3sz", opis="Boks C: okno 3-kwaterowe 7,005 × 1,50 m, skrzydła RU, dolna część stała VSG 44.2 do 0,85 m", U_w_max=0.9, g_n=0.50),
    "OZ1": dict(wyrob="okno_PVC_3sz", opis="Okno 1,80 × 1,50 m RU (zachód)", U_w_max=0.9, g_n=0.50),
    "OE1": dict(wyrob="okno_PVC_3sz", opis="Okno 1,50 × 1,50 m RU (wschód, pokój rodzinny)", U_w_max=0.9, g_n=0.50),
    "OP1": dict(wyrob="okno_ALU_3sz", opis="Okno 3,00 × 2,00 m za lamelami, parapet 0,60, dolna część stała VSG do 0,85 m, skrzydła do wewn. (W-098)", U_w_max=0.9, g_n=0.50),
    "OP2": dict(wyrob="okno_ALU_3sz", opis="Okno 1,20 × 1,75 m za lamelami, skrzydła do wewn.", U_w_max=0.9, g_n=0.50),
    "OP3": dict(wyrob="okno_ALU_3sz", opis="Okno 2,40 × 2,00 m za lamelami, parapet 0,60, dolna część stała VSG do 0,85 m", U_w_max=0.9, g_n=0.50),
    "ON1": dict(wyrob="okno_PVC_3sz", opis="Okno wysokie 0,80 × 0,60 m U (łazienka gościnna)", U_w_max=0.9, g_n=0.50),
    "ON2": dict(wyrob="okno_PVC_3sz", opis="Okno wysokie 0,90 × 0,60 m U (łazienki P1/P2)", U_w_max=0.9, g_n=0.50),
    "ON3": dict(wyrob="okno_PVC_3sz", opis="Okno wysokie 1,20 × 0,60 m U (pralnia)", U_w_max=0.9, g_n=0.50),
    "ON4": dict(wyrob="okno_PVC_3sz", opis="Okno 1,70 × 1,50 m U (klatka schodowa, północ)", U_w_max=0.9, g_n=0.50),
    "DZ1": dict(wyrob="drzwi_zewn", opis="Drzwi wejściowe 1,10 × 2,40 w murze (≥ 0,90 × 2,00 w świetle ościeżnicy), próg ≤ 0,02, U_D ≤ 1,1", U_D=0.90),
    "DZ2": dict(wyrob="drzwi_zewn", opis="Drzwi boczne garażu 1,00 × 2,10, stalowe ocieplone", U_D=1.30),
    "DZ3": dict(wyrob="drzwi_zewn", opis="Drzwi gospodarcze przeszklone 0,90 × 2,75 w systemie fasady E, otwierane na zewnątrz", U_D=1.10),
    "BR1": dict(wyrob="brama_segmentowa", opis="Brama segmentowa ocieplona 5,00 × 2,25 m z kratkami went. ≥ 0,08 m²", U_D=1.50),
    "DG1": dict(wyrob="drzwi_dom_garaz", opis="Drzwi garaż–dom 0,90 × 2,10, stalowe ocieplone, uszczelka, samozamykacz (W-113)", U_D=1.10),
    "D1": dict(opis="Drzwi wewnętrzne 0,90 × 2,10 w murze (≈ 0,80 × 2,00 w świetle ościeżnicy), bez progu (WT §75)"),
    "D2": dict(opis="Drzwi łazienek/WC 0,90 × 2,10 w murze, otwierane na zewnątrz, podcięcie/kratka ≥ 0,022 m² (WT §79)"),
    "D2P": dict(opis="Drzwi przesuwne naścienne łazienki 0,90 × 2,10, szczelina ≥ 0,022 m² (WT §79 ust. 1)"),
    "D3": dict(opis="Drzwi spiżarni 0,80 × 2,00"),
    "D4": dict(opis="Drzwi pom. technicznych 0,90 × 2,10, pełne, akustyczne R_w ≥ 32 dB (WT §96)"),
    "DS1": dict(opis="Drzwi szklane VSG 0,90 × 2,10 w ściance szklanej wiatrołapu (oznakowanie kontrastowe — WT §295)"),
    "OT1": dict(opis="Otwór 1,50 × 2,40 bez stolarki"),
    "OT2": dict(opis="Otwór 2,40 × 2,40 bez stolarki"),
}
MONTAZ = ("ciepły montaż: rama wsunięta 5 cm w mur, 4 cm w warstwie ocieplenia; izolacja ościeża z zakładem 3 cm na ramę; taśma paroszczelna "
          "od wewnątrz, paroprzepuszczalna od zewnątrz; parapet zewn. z okapnikiem na profilu nośnym z XPS (bez przerywania izolacji)")
OSL_MONTAZ = {
    "S0-01": "screen ZIP — kaseta w podsufitce okapu PL-E (poza warstwą izolacji), prowadnice przy słupach fasady",
    "S0-02": "screen ZIP — kaseta w podsufitce okapu PL-E",
    "S0-07": "screen ZIP — kaseta w podsufitce okapu zach. PL-E (1,50 m)",
    "S1-01": "screen ZIP — kaseta w pasie górnym ramy C (PL-C2), poza izolacją",
    "S2-01": "screen ZIP w szczelinie wentylowanej za lamelami, kaseta nadstawna przed membraną pod okapem PL-3 (bez podcięcia wełny)",
    "S2-02": "jw. — szczelina za lamelami",
    "S2-08": "jw. — szczelina za lamelami",
}
for o in OT:
    s = _SC[o["sciana"]]
    if s["przegroda"] in ("SZ1", "SZ2", "SZL") and o["typ"] != "otwor":
        o["montaz"] = MONTAZ
        if o.get("oslona") and o["oslona"] != "brak":
            o["oslona_montaz"] = OSL_MONTAZ.get(s["id"], "kaseta elewacyjna nadstawna PRZED licem ETICS (bez kasety w ociepleniu), "
                                                         "prowadnice na konsolach dystansowych z przekładką")
        if o["parapet"] <= 0.001 and o["typ"] in ("drzwi_przesuwne_HS", "drzwi_zewn", "fix"):
            o["prog"] = {"profil": "próg termiczny ≤ 0,02 m (HS/drzwi) na podwalinie progowej z XPS 300 / PUR-GF (λ ≤ 0,05) na płycie",
                         "odwodnienie_liniowe": s["kond"] == "P0" and s["przegroda"] == "SZ1",
                         "hydroizolacja": "wywinięcie membrany SBS płyty ≥ 0,15 m pod profil + taśma EPDM"}


# =====================================================================================================================
# 10. KATALOG WĘZŁÓW (`wezly`) — typy wg ALIASY_WEZLOW (mostki2d.katalog) / PSI_DOMYSLNE (fizyka.mostki); długości z geometrii
# =====================================================================================================================
def _dl_otworow():
    osc = nad = pod = prog0 = 0.0
    for o in OT:
        s = _SC[o["sciana"]]
        if s["przegroda"] not in ("SZ1", "SZ2", "SZL") or o["typ"] in ("otwor",):
            continue
        if o["typ"] == "brama":
            continue
        osc += 2 * o["wys"]
        nad += o["szer"]
        if o["parapet"] > 0.05:
            pod += o["szer"]
        else:
            prog0 += o["szer"]
    return osc, nad, pod, prog0


def _naroza(poly_pts, h):
    pg = orient(Polygon(poly_pts), 1.0)
    c = list(pg.exterior.coords)[:-1]
    n = 0
    for i in range(len(c)):
        a, b, d = c[i - 1], c[i], c[(i + 1) % len(c)]
        cross = (b[0] - a[0]) * (d[1] - b[1]) - (b[1] - a[1]) * (d[0] - b[0])
        n += 1 if cross > 0 else 0
    return n * h


_osc, _nad, _pod, _prog = _dl_otworow()
OB_P0_OGRZ = P((-EXT, -EXT), (xF + EXT, -EXT), (xF + EXT, y2 + 0.10), (xE + 0.22, y2 + 0.10), (xE + 0.22, y4 + EXT), (-EXT, y4 + EXT))
_obw_p0 = Polygon(OB_P0_OGRZ).length - (y4 + EXT - y2 - 0.10) - (xF - xE)          # bez odcinków przy garażu (wewn.)
WEZLY = [
    {"id": "WZ-R1", "nazwa": "Attyka stropodachu D1 (bryła A) — ściana SZ2 za lamelami, płyta wysunięta PL-3 na łączniku", "typ": "attyka",
     "przegrody": ["SZ2", "SD1", "AT1"], "dlugosc": r(Polygon(OB_P2).length, 2), "parametry": {"h_nad_pokryciem": 0.25}},
    {"id": "WZ-R2", "nazwa": "Attyka dachów D2/D3 nad P1 (styk ze ścianą P2 — cokolik izolacji ≥ 0,30 m ponad pokrycie)", "typ": "attyka",
     "przegrody": ["SZ1", "SD2", "AT1"], "dlugosc": r(2 * (xB - EXT + EXT) + 2 * (y4 - y3) + (xE - xD), 2)},
    {"id": "WZ-R3", "nazwa": "Attyka dachu zielonego D4 (garaż, pas gospodarczy) — linia D +3,85", "typ": "attyka",
     "przegrody": ["SZ1", "DZ1", "AT1"], "dlugosc": r(Polygon(DACHY[3]["obrys"]).length - (y4 + EXT - (-EXT)), 2),
     "parametry": {"h_nad_pokryciem": 0.545}},
    {"id": "WZ-IF1", "nazwa": "Strop pośredni ST1/ST2 z wieńcem — ETICS ciągły", "typ": "strop_posredni", "przegrody": ["SZ1", "POD-1"],
     "dlugosc": r(2 * (12.6 + 9.35) - 1.0 + Polygon(OB_P2).length - 13.6, 2)},
    {"id": "WZ-B1", "nazwa": "Okap E (PL-E) — płyta 30 cm na łączniku termoizolacyjnym (ETA), spadek 2 % od budynku, okapnik", "typ": "plyta_wspornikowa_lacznik",
     "przegrody": ["SZ1", "OK1"], "dlugosc": r((13.80 + EXT) + (y3 + EXT), 2), "parametry": {"wysieg": 1.5}},
    {"id": "WZ-B2", "nazwa": "Krawędź ST2 (PL-2) pod bryłą A — łącznik termoizolacyjny", "typ": "plyta_wspornikowa_lacznik",
     "przegrody": ["SZ1", "OK1"], "dlugosc": r((xE + EXT - X2o) + (y3 + 2 * EXT), 2), "parametry": {"wysieg": 1.1}},
    {"id": "WZ-B3", "nazwa": "Krawędź stropodachu ST3 (PL-3) — łącznik termoizolacyjny, attyka cofnięta", "typ": "plyta_wspornikowa_lacznik",
     "przegrody": ["SZ2", "OK1"], "dlugosc": r((xE + EXT - X2o) + 2 * (y3 + 2 * EXT), 2), "parametry": {"wysieg": 1.1}},
    {"id": "WZ-B4", "nazwa": "Daszek nad wejściem PL-DA — łącznik termoizolacyjny", "typ": "plyta_wspornikowa_lacznik", "przegrody": ["SZ1", "OK1"],
     "dlugosc": 2.30, "parametry": {"wysieg": 1.3}},
    {"id": "WZ-B5", "nazwa": "Rama boksu C — konsole punktowe ze stali nierdzewnej z przekładką termiczną (2 pasy × 9 szt.)", "typ": "kotwa",
     "przegrody": ["SZ1"], "liczba": 18},
    {"id": "WZ-Z1", "nazwa": "Strop ST2Z nad powietrzem zewn. (wspornik bryły A) — styk ze ścianą osi A, docieplenie spodu 20 cm", "typ": "strop_zewn_krawedz",
     "przegrody": ["SZ1", "SUF-ZEW"], "dlugosc": r(y3 + 2 * EXT + 2 * 1.0, 2)},
    {"id": "WZ-C1", "nazwa": "Narożniki zewnętrzne ścian (wypukłe)", "typ": "naroznik_wypukly", "przegrody": ["SZ1"],
     "dlugosc": r(_naroza(OB_P0_OGRZ, 3.00) + _naroza(OB_P1, 3.15) + _naroza(OB_P2, 3.15), 2)},
    {"id": "WZ-W1", "nazwa": "Ościeża okien/drzwi — ciepły montaż (rama 5 cm w murze, 4 cm w izolacji, zakład izolacji 3 cm)", "typ": "oscieze",
     "przegrody": ["SZ1"], "dlugosc": r(_osc, 2), "wariant": "czesciowo"},
    {"id": "WZ-N1", "nazwa": "Nadproża — bez kaset osłon w ociepleniu (kasety w okapach / ramie C / nadstawne)", "typ": "nadproze",
     "przegrody": ["SZ1"], "dlugosc": r(_nad, 2), "wariant": "czesciowo"},
    {"id": "WZ-P1", "nazwa": "Podokienniki — parapet zewn. na profilu z XPS, okapnik", "typ": "podokiennik", "przegrody": ["SZ1"],
     "dlugosc": r(_pod, 2), "wariant": "czesciowo"},
    {"id": "WZ-T1", "nazwa": "Progi HS i drzwi na płycie P0 — profil progowy termoizolacyjny na podwalinie XPS/PUR-GF, odwodnienie liniowe",
     "typ": "prog", "przegrody": ["SZ1", "POD-0"], "dlugosc": r(_prog, 2), "wariant": "grunt"},
    {"id": "WZ-GF1", "nazwa": "Cokół — płyta fundamentowa na XPS 20 cm, XPS na czole płyty i cokole (izolacja ciągła)", "typ": "sciana_grunt",
     "przegrody": ["SZ1", "POD-0"], "dlugosc": r(_obw_p0 - _prog, 2), "parametry": {"y_teren": -0.25}},
    {"id": "WZ-G1", "nazwa": "Dom–garaż (pion): ściana SWG dochodzi do ściany zewn. — ETICS ciągły po zewnątrz całego P0, garaż buforem wewnątrz obudowy",
     "typ": "polaczenie_nieogrz", "przegrody": ["SZ1", "SWG"], "dlugosc": 6.00, "parametry": {"przerwa_izolacji": False}},
    {"id": "WZ-G2", "nazwa": "Dom–garaż (poziom): strop ST1/D4 ciągły nad ścianą SWG — docieplenie spodu stropu garażu pasem 1,0 m (SUF-G)",
     "typ": "polaczenie_nieogrz", "przegrody": ["SZ1", "SWG", "SUF-G"], "dlugosc": r((y4 - y2) + (xF - xE), 2)},
    {"id": "WZ-G3", "nazwa": "Dom–garaż (posadzka): dylatacja posadzki XPS 3 cm w osi SWG, płyta ciągła na XPS", "typ": "polaczenie_nieogrz",
     "przegrody": ["SWG", "POD-0", "POD-G"], "dlugosc": r((y4 - y2) + (xF - xE), 2)},
    {"id": "WZ-L1", "nazwa": "Konsole rusztu lamel (stal nierdzewna, przekładka termiczna)", "typ": "konsola_lamel", "przegrody": ["SZ2", "SZL"],
     "liczba": int(2 * ((xE + EXT - X2o) + 2 * (y3 + 2 * EXT)) / 0.80)},
    {"id": "WZ-S1", "nazwa": "Słupy stalowe fasady E w płaszczyźnie przeszklenia (w ciepłej strefie, obudowane profilem termicznym)", "typ": "slup",
     "przegrody": ["SZ1"], "dlugosc": r(4 * (Z_SPOD_ST1 - 0.0) * 0.10, 2)},
    {"id": "WZ-I1", "nazwa": "Przejścia instalacji przez przegrody zewn. (mankiety paroszczelne/EPDM)", "typ": "przejscie_instalacji",
     "przegrody": ["SZ1", "SD1", "POD-0"], "liczba": 14},
]


# =====================================================================================================================
# 11. ENERGIA, KONSTRUKCJA, GEOTECHNIKA, META
# =====================================================================================================================
Z_DACH_D1 = r(Z_ST3 + 0.002 + 0.22 + 0.004)            # wierzch warstw D1 (śr.) ≈ +9,526
ENERGIA = {
    "n50": 1.0, "osoby": 5, "pojemnosc": "ciezka", "chlodzenie": False, "psi_wariant": "domyslna",
    "wezly_wyniki": "projekt/08_obliczenia/mostki2d/wyniki_mostki.json",
    "grunt": {"typ": "piasek", "lambda": 2.0, "G_w": 1.0,
              "izolacja_obwodowa": {"typ": "pozioma", "D": 1.00, "d_n": 0.10, "lam_n": 0.036}},
    "wentylacja": {"centrala": "RVU_450", "czerpnia": [8.20, 2.90, 10.10], "wyrzutnia": [8.20, 2.90, 10.10], "wyrzut": "pionowy",
                   "zestaw_zblokowany": True, "wywiewki_kanalizacyjne": [[4.30, 8.30]], "rzedna_terenu": -0.25,
                   "uwagi": "czerpnio-wyrzutnia dachowa zblokowana (certyfikowana) ≥ 0,40 m nad pokryciem, ≥ 3,0 m od krawędzi dachu z oknami, "
                            "6,7 m od wywiewki K1 (W-166/W-167); pion K2 — zawór napowietrzający (K1 wentylowany ponad dach)"},
    "ogrzewanie": {"zrodlo": "PC_R290_monoblok", "temp_zasilania": 35, "pompy_W": 25,
                   "uwagi": "monoblok R290 (W-155) — jednostka zewn. przy ścianie pd. pasa gospodarczego, 7,1 m od granicy E (W-024), "
                            "strefa R290 1,0 m bez otworów (W-156); moduł hydrauliczny w pom. 0.12"},
    "cwu": {"zasobnik": "Z250", "cyrkulacja": {"moc_W": 5.0, "h_doba": 6.0}, "dezynfekcja_kWh_rok": 272,
            "uwagi": "projekt: zasobnik 300 dm³ (klasa B, strata ≤ 65 W) + bufor 100 dm³ — w EP dane przykładowe Z250 do wyboru wyrobu"},
    "pv": {"moduly": 15, "P_modul_Wp": 430, "azymut": 180, "nachylenie": 12, "PR": 0.80, "autokonsumpcja": "symulacja",
           "uwagi": "15 × 430 Wp = 6,45 kWp ≤ 6,5 kWp (W-194); stelaże niskie ≤ +9,78 (nie ponad attykę D1)"},
    "garaz": {"stanowiska": 2, "otwory_went_m2": 0.10, "n_went": 0.5},
}
KONSTRUKCJA = {
    "klasa_konsekwencji": "CC2", "klasa_niezawodnosci": "RC2", "K_FI": 1.0, "okres_uzytkowania": 50, "klasa_konstrukcji": "S4",
    "eurokody": "1. generacja z NA (W-260)",
    "beton": {"stropy_sciany_plyta": "C25/30 XC1/XC2", "krawedzie_wysuniete_attyki_belki": "C30/37 XC4+XF1", "stal": "B500SP (W-269)"},
    "mur": "silikat kl. 20 gr. 1, zaprawa cienkowarstwowa, f_d = 4,50 MPa (klasa wykonania A, W-270)",
    "sciezka_obciazen": [
        "Stropy ST1/ST2 jednokierunkowe N–S (22 cm): oś 1 (B1 / ściana) – oś 3 – oś 4; rozpiętości 5,125 / 3,625 m; płyta ciągła.",
        "Fasada pd. P0: belka odwrócona B1 25×107 na słupach RK120 SL1–SL4 (w szprosach) i ścianach A, E; przęsła ≤ 3,23 m.",
        "Boks C: nadproże B2 na słupkach SL5/SL6 w jednej linii pionowej z SL3/SL4 (siły skupione nad podporami B1).",
        "Wspornik bryły A (1,12 m w osi): belki wspornikowe ŻB B4 (oś 1) i B5 (oś 3) 18×80 w licu ścian P2 (pod parapetami), "
        "zakotwione w przęśle A–B 3,875 m dociążonym ścianami P2 i stropem ST3; belka krawędziowa B3 (oś A') podparta na końcach B4/B5 "
        "niesie lekką ścianę SZL (≤ 1,0 kN/m²) i okap PL-2; ST3 nad wspornikiem na belce B6. Brak ścian-tarcz — elementy prętowe "
        "sprawdzalne (SCHEMAT p. 9). EQU: 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb (W-262), ugięcie końca ≤ l/125 (W-268).",
        "Dach garażu D4: płyta 24 cm dwukierunkowa na ścianach E, F, oś 2 i oś 5 (6,375 × 6,50 m), l/d ≈ 27; zaspa przy uskoku do bryły B "
        "μ_w ≤ 4,0 (W-264), sytuacja wyjątkowa B2, dach zielony nasycony ≈ 1,6 kN/m².",
        "Trzon klatki: ściany C i D na P0 żelbetowe 18 cm (sztywność w kierunku x przy przeszklonej fasadzie pd. — J2), P1–P2 silikat.",
        "Płyty wysunięte ≤ 1,50 m na łącznikach termoizolacyjnych z ETA (W-272); rama C lekka stalowa na konsolach punktowych.",
    ],
}
GEOTECHNIKA = {"kategoria": "II", "grunt": {"rodzaj": "piasek średni, średniozagęszczony", "I_D": 0.6, "phi": 33.0, "gamma": 18.5, "M0": 80000},
               "ZWG": -3.8, "h_z": 0.8, "humus": 0.4,
               "uwagi": "opinia geotechniczna + dokumentacja badań (≥ 3 sondowania CPT/DPL do ≥ 6 m) + projekt geotechniczny (W-281/W-282)"}
META = {"nazwa": "Dom LAMELA", "wersja": "2.0 — koncepcja ostateczna (synteza W2 + przeszczepy W1/W3 + poprawki J1–J3)", "data": "2026-09-25",
        "autor": "Główny projektant — dane do uzupełnienia (brief §7 p. 4)", "zrodlo": "tools/buduj_model.py (model parametryczny)",
        "stadium": "koncepcja", "podstawa_WT": "WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) stosowane na podstawie art. 102a PB — W-A.1"}


# =====================================================================================================================
# 12. ZAPIS budynek.yaml
# =====================================================================================================================
class _Dumper(yaml.SafeDumper):
    pass


def _repr_float(dumper, v):
    if v != v or v in (float("inf"), float("-inf")):
        return dumper.represent_scalar("tag:yaml.org,2002:float", ".nan")
    t = f"{v:.4f}".rstrip("0")
    if t.endswith("."):
        t += "0"
    return dumper.represent_scalar("tag:yaml.org,2002:float", t)


def _repr_list(dumper, v):
    flow = all(not isinstance(x, (dict,)) for x in v) and (len(v) <= 12 or all(not isinstance(x, list) for x in v))
    return dumper.represent_sequence("tag:yaml.org,2002:seq", v, flow_style=flow)


_Dumper.add_representer(float, _repr_float)
_Dumper.add_representer(list, _repr_list)


def dump(path: Path, data: dict, naglowek: str):
    txt = yaml.dump(data, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=180, default_flow_style=False)
    path.write_text(naglowek + txt, encoding="utf-8")


def budynek() -> dict:
    materialy = {}
    for kod, d, zr in MAT:
        dd = dict(d)
        dd["zrodlo"] = zr
        materialy[kod] = dd
    kond = [
        {"id": "P0", "nazwa": "Parter", "rzedna": 0.0, "wys_kondygnacji": H_KOND, "wys_w_swietle": 2.77, "podloga": "POD-0"},
        {"id": "P1", "nazwa": "I piętro", "rzedna": Z_P1, "wys_kondygnacji": H_KOND, "wys_w_swietle": 2.77, "podloga": "POD-1"},
        {"id": "P2", "nazwa": "II piętro", "rzedna": Z_P2, "wys_kondygnacji": r(Z_ST3 - Z_P2), "wys_w_swietle": 2.77, "podloga": "POD-1"},
    ]
    return {
        "meta": META,
        "uklad": {"zero_abs": ZERO_ABS, "azymut_osi_y": 0.0, "uklad_wysokosci": "PL-EVRF2007-NH",
                  "opis": "x → wschód, y → północ; (0,0) = oś A × oś 1; ±0,00 = posadzka P0"},
        "osie": {"x": {k: r(v) for k, v in X.items()}, "y": {k: r(v) for k, v in Y.items()}},
        "kondygnacje": kond,
        "materialy": materialy,
        "przegrody": PRZ,
        "stolarka": STOLARKA,
        "sciany": SC,
        "otwory": OT,
        "pomieszczenia": PM,
        "stropy": STROPY,
        "dachy": DACHY,
        "wsporniki_plyty": WSP,
        "slupy": SLUPY,
        "belki": BELKI,
        "fundamenty": FUND,
        "schody": SCHODY,
        "balustrady": BALUSTRADY,
        "lamele": LAMELE,
        "tarasy": TARASY,
        "wezly": WEZLY,
        "energia": ENERGIA,
        "konstrukcja": KONSTRUKCJA,
        "geotechnika": GEOTECHNIKA,
    }


NAGLOWEK_B = ("# Dom LAMELA — MODEL BUDYNKU (jedno źródło prawdy). PLIK GENEROWANY: tools/buduj_model.py — nie edytować ręcznie.\n"
              "# Schemat: docs/SCHEMAT_MODELU.md; koncepcja: docs/20_koncepcja/koncepcja.md. Układ: x→E, y→N, (0,0)=A×1, ±0,00=101,65 m n.p.m.\n"
              "# Wartości materiałowe — typowe (PN-EN ISO 10456, PN-EN 1745, DWU typowych wyrobów, „lub równoważne”) — pole `zrodlo`.\n")

if __name__ == "__main__" and "--tylko-budynek" in __import__("sys").argv:
    OUT.mkdir(exist_ok=True)
    dump(OUT / "budynek.yaml", budynek(), NAGLOWEK_B)
    print("zapisano", OUT / "budynek.yaml")
