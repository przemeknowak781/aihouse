# -*- coding: utf-8 -*-
"""Wariant W2 koncepcji Domu LAMELA - FUNKCJA / EKONOMIA / KONSTRUKCJA.
Jedno źródło prawdy dla rysunków i opisu wariantu (układ budynku: x->E, y->N, z->gora, 0,0 = osie A/1).
Wszystkie wymiary w metrach."""
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
import math

# ------------------------------------------------------------------ osie
OSIE_X = {"A'": -1.000, "A": 0.000, "B": 3.875, "C": 6.095, "D": 8.425, "E": 12.000, "F": 18.400}
OSIE_Y = {"1": 0.000, "2": 2.600, "3": 4.800, "4": 8.400, "5": 9.000}

# ------------------------------------------------------------------ typy scian: (odsuniecie lica po stronie 'lewej'/wnetrza, po stronie 'prawej')
TYPY = {
    "SZ1":  dict(nazwa="ściana zewn. nośna: tynk 1,5 + silikat 18 + EPS grafit/welna 20 + tynk 1 cm", L=0.105, R=0.300, kol="#8c8c8c"),
    "SZL":  dict(nazwa="ściana zewn. lekka P2 (wspornik): szkielet stal/drewno + welna 20 + płyta, gr. 40,5 cm", L=0.105, R=0.300, kol="#b0a58c"),
    "SW18": dict(nazwa="ściana wewn. nośna: silikat 18 + 2x tynk 1,5", L=0.105, R=0.105, kol="#8c8c8c"),
    "SWG":  dict(nazwa="ściana nośna dom/garaż: tynk 1,5 + silikat 18 + welna 12 + tynk 1 (U~0,28)", L=0.105, R=0.220, kol="#8c8c8c"),
    "SC12": dict(nazwa="ścianka środkowa schodów: silikat 12 (fair-faced)", L=0.060, R=0.060, kol="#a9a9a9"),
    "DZ12": dict(nazwa="ścianka działowa: silikat 12 + 2x tynk 1,5", L=0.075, R=0.075, kol="#c8c8c8"),
}

# ------------------------------------------------------------------ poziomy
POZ = dict(zero_abs=101.65, P0=0.00, P1=3.15, P2=6.30, wys_kond=3.15, podl=0.15,
           ST1=(2.80, 3.00), ST2=(5.95, 6.15), ST3=(9.10, 9.32), STG=(2.76, 3.00),
           dach_P2_warstwy=9.60, attyka_P2=9.80, dach_P1_warstwy=6.50, attyka_P1=6.70,
           dach_G_warstwy=3.35, attyka_G=3.85, lawa_spod=-1.10)

# ------------------------------------------------------------------ sciany: id, kond, typ, p1, p2, ext(start,koniec)
# kierunek osi dobrany tak, by wnetrze (dla SZ1/SWG: strona 'L') lezalo po lewej
def W(i, k, t, p1, p2, e1=0.0, e2=0.0, uw=""):
    return dict(id=i, kond=k, typ=t, p1=p1, p2=p2, ext=(e1, e2), uw=uw)

E = 0.30  # przedluzenie w narozu zewnetrznym
SCIANY = [
    # ---------------- P0
    W("S0-01", "P0", "SZ1", (0, 0), (12, 0), E, 0, "fasada pd. strefy dziennej: przeszklenie 5 kwater na słupach stalowych SL1-SL4 + belka B1"),
    W("S0-02", "P0", "SZ1", (12, 0), (18.4, 0), 0, E, "ściana pd. strefy gospodarczej (pełna - bryła G)"),
    W("S0-03", "P0", "SZ1", (18.4, 0), (18.4, 9.0), E, E, "ściana wsch. garażu (pion D)"),
    W("S0-04", "P0", "SZ1", (18.4, 9.0), (12, 9.0), E, E, "ściana pn. garażu z brama"),
    W("S0-05", "P0", "SZ1", (12, 9.0), (12, 8.4), E, 0, "ściana zach. garażu - odcinek zewn."),
    W("S0-06", "P0", "SZ1", (12, 8.4), (0, 8.4), 0, E, "ściana pn. częśći mieszkalnej"),
    W("S0-07", "P0", "SZ1", (0, 8.4), (0, 0), E, E, "ściana zach. (os A)"),
    W("S0-08", "P0", "SW18", (0, 4.8), (12, 4.8), 0, 0, "ściana grzbietowa (os 3)"),
    W("S0-09", "P0", "SW18", (3.875, 4.8), (3.875, 8.4), 0, 0, "os B"),
    W("S0-10", "P0", "SW18", (6.095, 4.8), (6.095, 8.4), 0, 0, "os C - klatka schodowa"),
    W("S0-11", "P0", "SW18", (8.425, 4.8), (8.425, 8.4), 0, 0, "os D - klatka schodowa"),
    W("S0-12", "P0", "SW18", (12, 0), (12, 2.6), 0, 0, "os E - kuchnia/przedsionek"),
    W("S0-13", "P0", "SWG", (12, 2.6), (12, 8.4), 0, 0, "os E - dom/garaż (ocieplona od garażu)"),
    W("S0-14", "P0", "SWG", (18.4, 2.6), (12, 2.6), 0, 0, "os 2 - strefa gosp./garaż"),
    W("S0-15", "P0", "SC12", (7.26, 4.8), (7.26, 7.145), 0, 0, "ścianka środkowa schodów"),
    W("S0-16", "P0", "DZ12", (3.875, 6.275), (6.095, 6.275)),
    W("S0-17", "P0", "DZ12", (8.425, 6.375), (12, 6.375)),
    W("S0-18", "P0", "DZ12", (9.675, 6.375), (9.675, 8.4)),
    W("S0-19", "P0", "DZ12", (14.275, 0), (14.275, 2.6)),
    W("S0-20", "P0", "DZ12", (15.475, 0), (15.475, 2.6)),
    # ---------------- P1
    W("S1-01", "P1", "SZ1", (0, 0), (12, 0), E, E, "ściana pd. bryły B, otwor boksu C na belce B1"),
    W("S1-02", "P1", "SZ1", (12, 0), (12, 8.4), E, E, "ściana wsch. (os E)"),
    W("S1-03", "P1", "SZ1", (12, 8.4), (0, 8.4), E, E, "ściana pn."),
    W("S1-04", "P1", "SZ1", (0, 8.4), (0, 0), E, E, "ściana zach. (os A)"),
    W("S1-05", "P1", "SW18", (0, 4.8), (12, 4.8), 0, 0, "ściana grzbietowa (os 3)"),
    W("S1-06", "P1", "SW18", (3.875, 4.8), (3.875, 8.4), 0, 0, "os B"),
    W("S1-07", "P1", "SW18", (6.095, 4.8), (6.095, 8.4), 0, 0, "os C"),
    W("S1-08", "P1", "SW18", (8.425, 4.8), (8.425, 8.4), 0, 0, "os D"),
    W("S1-09", "P1", "SC12", (7.26, 4.8), (7.26, 7.145), 0, 0, "ścianka środkowa schodów"),
    W("S1-10", "P1", "DZ12", (3.875, 0), (3.875, 3.575), 0, 0.075),
    W("S1-11", "P1", "DZ12", (0, 3.575), (3.875, 3.575), 0, 0.075),
    # ---------------- P2
    W("S2-01", "P2", "SZ1", (-1, 0), (12, 0), E, E, "ściana pd. bryły A; odc. x -1,0...2,0 żelbetowa ściana-tarcza"),
    W("S2-02", "P2", "SZ1", (12, 0), (12, 4.8), E, E, "ściana wsch."),
    W("S2-03", "P2", "SZ1", (12, 4.8), (8.425, 4.8), E, 0, "ściana pn. bryły A (nad dachem P1)"),
    W("S2-04", "P2", "SZ1", (8.425, 4.8), (8.425, 8.4), 0, E, "nadbudowa klatki/łazienki - ściana wsch."),
    W("S2-05", "P2", "SZ1", (8.425, 8.4), (3.875, 8.4), E, E, "nadbudowa - ściana pn."),
    W("S2-06", "P2", "SZ1", (3.875, 8.4), (3.875, 4.8), E, 0, "nadbudowa - ściana zach."),
    W("S2-07", "P2", "SZ1", (3.875, 4.8), (-1, 4.8), 0, E, "ściana pn. bryły A; odc. x -1,0...2,0 żelbetowa ściana-tarcza"),
    W("S2-08", "P2", "SZL", (-1, 4.8), (-1, 0), E, E, "ściana zach. na wsporniku 1,0 m (lekka)"),
    W("S2-09", "P2", "SW18", (3.875, 4.8), (8.425, 4.8), 0, 0, "os 3 wewn."),
    W("S2-10", "P2", "SW18", (6.095, 4.8), (6.095, 8.4), 0, 0, "os C"),
    W("S2-11", "P2", "SC12", (7.26, 4.8), (7.26, 7.145), 0, 0, "ścianka środkowa schodów"),
    W("S2-12", "P2", "DZ12", (3.675, 0), (3.675, 4.8)),
    W("S2-13", "P2", "DZ12", (6.125, 0), (6.125, 4.8)),
    W("S2-14", "P2", "DZ12", (8.395, 0), (8.395, 4.8)),
    W("S2-15", "P2", "DZ12", (6.125, 2.725), (8.395, 2.725)),
]

# ------------------------------------------------------------------ otwory: sciana, a, b (wspolrzedne wzdluz sciany: x dla scian poziomych, y dla pionowych),
# typ, wys, parapet (wzgl. posadzki kondygnacji), symbol, zawias ('a'/'b'), kierunek otwierania ('+x','-x','+y','-y')
def O(i, s, a, b, typ, wys, par=0.0, sym="", zaw=None, kier=None, uw="", kw=1):
    return dict(id=i, sciana=s, a=a, b=b, szer=round(b - a, 3), typ=typ, wys=wys, par=par, sym=sym, zaw=zaw, kier=kier, uw=uw, kw=kw)

OTWORY = [
    # ---------------- P0
    O("O0-01", "S0-01", 0.30, 11.70, "fasada", 2.75, 0.0, "FS1", uw="przeszklenie E: 5 kwater po 2,28 m (kw. 2 i 4 - drzwi HS), słupki SL1-SL4 w szprosach", kw=5),
    O("O0-02", "S0-07", 1.20, 3.60, "okno", 2.15, 0.45, "OZ1", uw="okno zach. salonu (siedzisko), pod okapem 1,5 m"),
    O("O0-03", "S0-07", 5.50, 7.30, "okno", 1.50, 0.90, "OZ2", uw="pokój gościnny"),
    O("O0-04", "S0-06", 10.20, 11.30, "drzwi_zewn", 2.40, 0.0, "DZ1", "a", "-y", "drzwi wejściowe 110x240 (w świetle ościeżnicy >= 0,90x2,00), prog <= 2 cm"),
    O("O0-05", "S0-04", 12.75, 17.75, "brama", 2.25, 0.0, "BR1", uw="brama segmentowa 500x225, kratki went. >= 0,08 m2"),
    O("O0-06", "S0-03", 5.00, 5.90, "drzwi_zewn", 2.10, 0.0, "DZ2", "a", "-x", "drzwi boczne garażu (rowery, ogród)"),
    O("O0-07", "S0-08", 4.20, 5.10, "otwor", 2.10, 0.0, "", uw="przejście do przedpokóju gościnnego"),
    O("O0-08", "S0-08", 6.20, 7.20, "otwor", 2.55, 0.0, "", uw="wejście na bieg 1 schodów"),
    O("O0-09", "S0-08", 7.40, 8.20, "drzwi", 2.00, 0.0, "D3", "a", "+y", "schowek pod schodami"),
    O("O0-10", "S0-08", 8.80, 10.20, "otwor", 2.40, 0.0, "", uw="hol - strefa dzienna"),
    O("O0-11", "S0-09", 5.10, 6.00, "drzwi", 2.05, 0.0, "D1", "a", "-x", "pokój gościnny"),
    O("O0-12", "S0-16", 4.20, 5.00, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka gościnna (na zewnątrz, kratka)"),
    O("O0-13", "S0-17", 10.30, 11.20, "drzwi", 2.05, 0.0, "D1", "b", "-y", "wiatrołap - hol"),
    O("O0-14", "S0-17", 8.70, 9.50, "drzwi", 2.05, 0.0, "D2", "a", "-y", "WC (na zewnątrz, kratka)"),
    O("O0-15", "S0-12", 1.00, 1.90, "drzwi", 2.05, 0.0, "D1", "a", "+x", "kuchnia - przedsionek gosp."),
    O("O0-16", "S0-14", 12.50, 13.40, "drzwi", 2.05, 0.0, "DG1", "a", "+y", "przedsionek - garaż: szczelne, samozamykacz, U<=1,3"),
    O("O0-17", "S0-14", 16.60, 17.50, "drzwi", 2.05, 0.0, "DG1", "b", "+y", "pom. techniczne - garaż"),
    O("O0-19", "S0-02", 12.25, 13.15, "drzwi_zewn", 2.40, 0.0, "DZ3", "a", "-y", "drzwi gospodarcze przeszklone przedsionek - ogród/taras (otwierane na zewnątrz)"),
    O("O0-18", "S0-19", 1.10, 1.90, "drzwi", 2.05, 0.0, "D3", "a", "+x", "spiżarnia"),
    # ---------------- P1
    O("O1-01", "S1-01", 4.10, 11.10, "boks", 1.50, 0.70, "BC1", uw="boks C: 3 kwatery 2,33 m, dolna część stała VSG do 0,85 m (K-17), słupki w szprosach", kw=3),
    O("O1-02", "S1-02", 1.60, 2.80, "okno", 1.50, 0.85, "OE1", uw="pokój rodzinny - widok na dach zielony"),
    O("O1-03", "S1-03", 4.40, 5.30, "okno", 0.60, 1.50, "ON1", uw="łazienka - okno doświetlające"),
    O("O1-04", "S1-03", 10.00, 11.20, "okno", 0.60, 1.50, "ON2", uw="pralnia"),
    O("O1-05", "S1-04", 5.70, 7.50, "okno", 1.50, 0.85, "OZ2", uw="pokój dziecka 2"),
    O("O1-06", "S1-04", 0.90, 2.70, "okno", 1.50, 0.85, "OZ2", uw="pokój dziecka 1 (elewacja pd. bryły B pełna jak w szkicu)"),
    O("O1-07", "S1-05", 2.70, 3.60, "drzwi", 2.05, 0.0, "D1", "a", "+y", "pokój dziecka 2"),
    O("O1-08", "S1-05", 4.20, 5.00, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka (na zewnątrz)"),
    O("O1-09", "S1-05", 6.20, 8.32, "otwor", 2.55, 0.0, "", uw="klatka schodówa - oba biegi"),
    O("O1-10", "S1-05", 9.00, 9.90, "drzwi", 2.05, 0.0, "D1", "b", "+y", "pralnia"),
    O("O1-11", "S1-11", 2.70, 3.60, "drzwi", 2.05, 0.0, "D1", "a", "-y", "pokój dziecka 1"),
    # ---------------- P2
    O("O2-01", "S2-01", 0.20, 3.20, "okno", 2.00, 0.60, "OP1", uw="sypialnia; za lamelami; dolna część stała do 0,85; skrzydła do wewnątrz (K-16)"),
    O("O2-02", "S2-01", 4.30, 5.50, "okno", 1.75, 0.85, "OP2", uw="garderoba; za lamelami"),
    O("O2-03", "S2-01", 8.90, 11.30, "okno", 2.00, 0.60, "OP1", uw="gabinet; za lamelami"),
    O("O2-04", "S2-02", 1.80, 3.00, "okno", 1.75, 0.85, "OP2", uw="gabinet - wschod"),
    O("O2-05", "S2-05", 6.40, 8.10, "okno", 1.50, 0.90, "ON3", uw="okno nad klatka schodówa (północ)"),
    O("O2-06", "S2-05", 4.30, 5.20, "okno", 0.80, 1.50, "ON1", uw="łazienka rodziców"),
    O("O2-07", "S2-08", 1.20, 3.60, "okno", 2.00, 0.60, "OP1", uw="sypialnia - zachod"),
    O("O2-08", "S2-09", 4.20, 5.00, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka rodziców (na zewnątrz)"),
    O("O2-09", "S2-09", 7.32, 8.32, "otwor", 2.40, 0.0, "", uw="wyjście z biegu 2 schodów"),
    O("O2-10", "S2-12", 3.40, 4.20, "drzwi", 2.05, 0.0, "D1", "b", "-x", "sypialnia"),
    O("O2-11", "S2-13", 3.30, 4.10, "drzwi", 2.05, 0.0, "D1", "b", "-x", "garderoba (wejście do apartamentu)"),
    O("O2-12", "S2-14", 3.30, 4.20, "drzwi", 2.05, 0.0, "D1", "b", "+x", "gabinet"),
    O("O2-13", "S2-15", 6.60, 7.40, "drzwi", 2.05, 0.0, "D3", "a", "-y", "pom. techniczne (rekuperator, wyłaz na dach)"),
]

# ------------------------------------------------------------------ pomieszczenia (lica wykonczone): id, nazwa, kond, wielobok/prostokat, kategoria, pobyt, min
def R(i, n, k, geo, kat, pobyt=False, minimum=None, posadzka="", uw=""):
    if isinstance(geo, tuple) and len(geo) == 4:
        poly = box(*geo)
    else:
        poly = geo
    return dict(id=i, nazwa=n, kond=k, poly=poly, kat=kat, pobyt=pobyt, min=minimum, posadzka=posadzka, uw=uw)

SI = box(5.59, 4.905, 5.99, 5.605)       # szacht instalacyjny SI (pion kan. K1 + kanaly went.)
S2 = box(8.53, 7.90, 8.90, 8.295)        # pion kan. K2 (pralnia/WC)
SCHODY_RDZEN = box(6.20, 4.905, 8.32, 8.295)
SCIANKA = box(7.20, 4.905, 7.32, 7.145)
BIEG_W = box(6.20, 4.905, 7.20, 7.145)
BIEG_E = box(7.32, 4.905, 8.32, 7.145)
SPOCZNIK = box(6.20, 7.145, 8.32, 8.295)

POMIESZCZENIA = [
    # P0
    R("0.01", "Wiatrołap", "P0", (9.75, 6.45, 11.895, 8.295), "ruchu", posadzka="gres", uw="szafa wnękowa 0,6 m"),
    R("0.02", "Hol", "P0", (8.53, 4.905, 11.895, 6.30), "ruchu", posadzka="gres"),
    R("0.03", "WC gościnne", "P0", (8.53, 6.45, 9.60, 8.295), "pomocnicza", posadzka="gres", uw="szer. 1,07 >= 0,90 (B-17)"),
    R("0.04", "Klatka schodówa", "P0", unary_union([BIEG_W, SPOCZNIK]), "ruchu", posadzka="dąb"),
    R("0.05", "Schowek pod schodami", "P0", BIEG_E, "pomocnicza", posadzka="dąb", uw="wys. zmienna 1,37-2,77 m"),
    R("0.06", "Salon + jadalnia + kuchnia", "P0", (0.105, 0.105, 11.895, 4.695), "podstawowa", True, 50.0, "dąb/gres", "strefa otwarta; kuchnia z wyspą przy ścianie E"),
    R("0.07", "Przedpokój gościnny", "P0", box(3.98, 4.905, 5.99, 6.20).difference(SI), "ruchu", posadzka="dąb"),
    R("0.08", "Łazienka gościnna (prysznic)", "P0", (3.98, 6.35, 5.99, 8.295), "pomocnicza", posadzka="gres"),
    R("0.09", "Pokój gościnny / gabinet", "P0", (0.105, 4.905, 3.77, 8.295), "podstawowa", True, 8.0, "dąb"),
    R("0.10", "Przedsionek gospodarczy", "P0", (12.105, 0.105, 14.20, 2.495), "ruchu", posadzka="gres", uw="ławka, buty, zlew gosp."),
    R("0.11", "Spiżarnia", "P0", (14.35, 0.105, 15.40, 2.495), "pomocnicza", posadzka="gres"),
    R("0.12", "Pomieszczenie techniczne", "P0", (15.55, 0.105, 18.295, 2.495), "techniczna", minimum=6.0, posadzka="gres",
      uw="PC split (jedn. wewn.), zasobnik CWU 300 l, bufor, rozdzielacze, rozdzielnica RG, wodomierz"),
    R("0.13", "Garaż 2-stanowiskowy", "P0", (12.22, 2.82, 18.295, 8.895), "garaż", posadzka="posadzka żywiczna", uw="w świetle 6,08 x 6,08 m"),
    # P1
    R("1.01", "Hol", "P1", (0.105, 3.65, 8.32, 4.695), "ruchu", posadzka="dąb"),
    R("1.02", "Pokój rodzinny / biblioteka (boks C)", "P1", unary_union([box(3.95, 0.105, 11.895, 3.65), box(8.32, 3.65, 11.895, 4.695)]), "podstawowa", True, 16.0, "dąb"),
    R("1.03", "Pokój dziecka 1", "P1", (0.105, 0.105, 3.80, 3.50), "podstawowa", True, 12.0, "dąb"),
    R("1.04", "Pokój dziecka 2", "P1", (0.105, 4.905, 3.77, 8.295), "podstawowa", True, 12.0, "dąb"),
    R("1.05", "Łazienka", "P1", box(3.98, 4.905, 5.99, 8.295).difference(SI), "pomocnicza", posadzka="gres"),
    R("1.06", "Klatka schodówa", "P1", SCHODY_RDZEN.difference(SCIANKA), "ruchu", posadzka="dąb"),
    R("1.07", "Pralnia z suszarnią", "P1", box(8.53, 4.905, 11.895, 8.295).difference(S2), "pomocnicza", posadzka="gres"),
    # P2
    R("2.01", "Hol", "P2", (6.20, 2.80, 8.32, 4.695), "ruchu", posadzka="dąb"),
    R("2.02", "Sypialnia rodziców", "P2", (-0.895, 0.105, 3.60, 4.695), "podstawowa", True, 14.0, "dąb"),
    R("2.03", "Garderoba", "P2", (3.75, 0.105, 6.05, 4.695), "pomocnicza", posadzka="dąb"),
    R("2.04", "Łazienka rodziców", "P2", box(3.98, 4.905, 5.99, 8.295).difference(SI), "pomocnicza", posadzka="gres"),
    R("2.05", "Gabinet", "P2", (8.47, 0.105, 11.895, 4.695), "podstawowa", True, 8.0, "dąb"),
    R("2.06", "Pom. techn. (reku + wyłaz)", "P2", (6.20, 0.105, 8.32, 2.65), "techniczna", posadzka="gres", uw="klapa 0,9x0,9 + drabina (K-20, K-21)"),
]

# ------------------------------------------------------------------ schody (SCH1: P0->P1, SCH2: P1->P2; identyczne, jedna nad druga)
SCHODY = dict(h=0.175, s=0.28, n_podn=18, biegi=2, stopni_w_biegu=9, szer=1.00,
              bieg_W=dict(x=(6.20, 7.20), y0=4.905, kier=+1),      # bieg 1: w gore ku polnocy
              spocznik=dict(x=(6.20, 8.32), y=(7.145, 8.295)),
              bieg_E=dict(x=(7.32, 8.32), y0=7.145, kier=-1),      # bieg 2: w gore ku poludniowi, wyjscie przy scianie osi 3
              gr_plyty_biegu=0.18)

# ------------------------------------------------------------------ elementy zewn. (wysuniecia plyt, rama C, lamele) - rzuty
PLYTY = [
    dict(id="E-okap", opis="ST1: okap pd. strefy dziennej (linia E) - wysunięcie 1,00 m", poly=box(-1.80, -1.30, 12.60, -0.30), z=(2.75, 3.05), lacznik=True),
    dict(id="E-okap-W", opis="ST1: okap zach. - wysunięcie 1,50 m", poly=box(-1.80, -0.30, -0.30, 4.80), z=(2.75, 3.05), lacznik=True),
    dict(id="daszek", opis="ST1: daszek nad wejściem 2,80 x 1,30 m (K-12)", poly=box(9.50, 8.70, 12.30, 10.00), z=(2.80, 3.05), lacznik=True),
    dict(id="C-dol", opis="rama C - płyta dolna (linia D) wysunięcie 1,00 m", poly=box(3.60, -1.30, 12.60, -0.30), z=(3.65, 3.85), lacznik=True),
    dict(id="C-gora", opis="rama C - płyta górna wysunięcie 1,00 m", poly=box(3.60, -1.30, 12.60, -0.30), z=(5.35, 5.55), lacznik=True),
    dict(id="ST2-okap", opis="ST2: krawędź pd. + zach. (spód bryły A) - wysunięcie 1,00 / 1,10 m", poly=unary_union([box(-2.40, -1.30, 12.60, -0.30), box(-2.40, -0.30, -1.30, 5.10)]), z=(5.95, 6.25), lacznik=True),
    dict(id="ST3-okap", opis="ST3: stropodach bryły A - wysunięcie pd. 1,00, zach. 1,10, wsch. 0,30 m", poly=unary_union([box(-2.40, -1.30, 12.60, -0.30), box(-2.40, -0.30, -1.30, 5.10), box(12.30, -0.30, 12.60, 5.10)]), z=(9.10, 9.42), lacznik=True),
]
LAMELE = dict(x=(-1.30, 12.30), y=-0.45, z=(6.15, 9.10), rozstaw=0.12, b=0.04, h=0.08, mat="drewno termo / aluminium drewnopodobne")
SLUPY = [dict(id=f"SL{i+1}", xy=(0.30 + 2.28 * (i + 1), 0.0), przekroj="RK 120x120x8 S355 w szprosie", z=(0.0, 2.80)) for i in range(4)]
SLUPKI_C = [dict(id=f"SLC{i+1}", xy=(4.10 + 7.0 / 3 * (i + 1), 0.0), przekroj="RK 100x100x6 w szprosie boksu C", z=(3.85, 5.35)) for i in range(2)]

# ------------------------------------------------------------------ dzialka (uklad budynku)
DZ = dict(xw=-7.60, xe=24.40, ys=-32.70, yn=17.30)
LINIA_ZAB = DZ["yn"] - 6.0
H_NAROZ = dict(NW=101.40, NE=101.55, SW=101.10, SE=101.25)

def teren(x, y):
    """Rzędna istniejacego terenu (interpolacja dwuliniowa narożników działki), m n.p.m."""
    fx = (x - DZ["xw"]) / (DZ["xe"] - DZ["xw"])
    fy = (y - DZ["ys"]) / (DZ["yn"] - DZ["ys"])
    s = H_NAROZ["SW"] + fx * (H_NAROZ["SE"] - H_NAROZ["SW"])
    n = H_NAROZ["NW"] + fx * (H_NAROZ["NE"] - H_NAROZ["NW"])
    return s + fy * (n - s)

def teren_wzgl(x, y):
    return teren(x, y) - POZ["zero_abs"]


# ------------------------------------------------------------------ zagospodarowanie (uklad budynku; dzialka x -7,60...24,40, y -32,70...17,30)
TEREN_ELEM = dict(
    podjazd=dict(poly=box(12.30, 9.30, 18.70, 17.30), opis="podjazd - kostka betonowa szara (dojazd do bramy garażu)", typ="utw"),
    dojscie=dict(poly=box(9.80, 8.70, 12.30, 17.30), opis="dojście do wejscia 2,50 m - płyty betonowe", typ="utw"),
    taras=dict(poly=unary_union([box(-1.80, -4.30, 11.70, -0.30), box(-1.80, -0.30, -0.30, 4.80)]), opis="taras ogrodowy -0,05 (deska kompozytowa na legarach / płyty)", typ="utw"),
    sciezka_E=dict(poly=box(18.70, -1.00, 19.60, 9.30), opis="ścieżka żwirowa wzdłuż ściany wsch. (drzwi boczne garażu, jedn. zewn. PC)", typ="utw"),
    smietnik=dict(poly=box(6.60, 16.10, 9.00, 17.20), opis="osłona na pojemniki (4 x 240 l, segregacja) w linii ogrodzenia, drzwiczki od ulicy", typ="utw"),
    pc_plyta=dict(poly=box(19.60, 0.40, 20.60, 1.80), opis="jednostka zewn. pompy ciepła na fundamencie z wibroizolacją", typ="utw"),
    skrzynki=dict(poly=box(-5.50, 14.00, 1.50, 15.20), opis="skrzynki rozsączające 7,0x1,2x0,66 m (V~5,5 m3) - wyłączone z PBC", typ="rozsacz"),
)
MIEJSCA_GOSC = [box(12.90, 10.00, 15.40, 15.00), box(15.60, 10.00, 18.10, 15.00)]
ZBIORNIK = dict(xy=(-2.50, 12.50), wym=(3.0, 2.0), V=6.0, opis="zbiornik retencyjny na deszczówkę 6 m3 (podlewanie ogrodu), przelew do skrzynek")
OGRODZENIE = dict(brama=(12.50, 18.10), furtka=(10.30, 11.30), wys=1.50)
ZK = (11.40, 12.20)          # zlacze kablowo-pomiarowe we wnece ogrodzenia (x od-do)
PRZYLACZA = dict(
    woda=dict(pts=[(16.80, 20.50), (16.80, 9.30), (16.80, 2.40)], opis="przyłącze wody PE 40 od sieci PE 110; wodomierz w pom. techn. 0.12"),
    kan=dict(pts=[(5.00, 8.70), (5.00, 15.00), (5.00, 23.00)], opis="przykanalik PVC 160 do sieci PVC 200; studzienka rewizyjna D425 na dzialce"),
    en=dict(pts=[(11.80, 18.30), (11.80, 17.30), (11.80, 9.40), (12.10, 9.40)], opis="WLZ YKY 5x10 z ZK do rozdzielnicy RG (pom. techn.)"),
    tel=dict(pts=[(12.00, 18.80), (12.00, 17.30), (12.00, 9.40)], opis="światłowód (kanalizacja teletechniczna)"),
    deszcz=dict(pts=[(0.50, 8.70), (0.50, 11.50), (-1.00, 12.50)], opis="kanalizacja deszczowa z rur spustowych elewacji pn. do zbiornika"),
)
SIEC = dict(woda=20.50, kan=23.00, en=18.30, tel=18.80, gaz=26.30, jezdnia=(19.55, 25.05), pas=(17.30, 27.30))
DRZEWA = [(-3.5, -14.0, 4.0), (6.0, -21.0, 5.0), (17.5, -13.0, 4.0), (-4.5, -27.0, 3.5), (20.5, -26.0, 3.5), (2.3, 11.9, 1.4)]

# ------------------------------------------------------------------ geometria pochodna
def wall_poly(w, ext=True):
    t = TYPY[w["typ"]]
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    nx, ny = -uy, ux  # lewa normalna
    e1, e2 = w["ext"] if ext else (0, 0)
    ax, ay = x1 - ux * e1, y1 - uy * e1
    bx, by = x2 + ux * e2, y2 + uy * e2
    return Polygon([(ax + nx * t["L"], ay + ny * t["L"]), (bx + nx * t["L"], by + ny * t["L"]),
                    (bx - nx * t["R"], by - ny * t["R"]), (ax - nx * t["R"], ay - ny * t["R"])])

def wall_by_id(i):
    return next(w for w in SCIANY if w["id"] == i)

def opening_cut(o, margin=0.6):
    w = wall_by_id(o["sciana"])
    (x1, y1), (x2, y2) = w["p1"], w["p2"]
    if abs(y2 - y1) < 1e-9:  # sciana pozioma
        y = y1
        return box(o["a"], y - margin, o["b"], y + margin)
    x = x1
    return box(x - margin, o["a"], x + margin, o["b"])

def outline(kond):
    """Obrys zewnętrzny kondygnacji (lica zewn. scian)."""
    polys = [wall_poly(w) for w in SCIANY if w["kond"] == kond]
    u = unary_union(polys)
    from shapely.geometry import Polygon as P
    ext = P(u.exterior) if u.geom_type == "Polygon" else P(max(u.geoms, key=lambda g: g.area).exterior)
    return ext

def room_area(r):
    return round(r["poly"].area, 2)

def okno_w_swietle(o):
    """Powierzchnia okna w świetle ościeżnic (WT par. 57 ust. 2): otwor muru minus ościeżnica 7 cm z kazdej strony."""
    return max(0.0, (o["szer"] - 0.14) * (o["wys"] - 0.14) - (o["kw"] - 1) * 0.10 * (o["wys"] - 0.14))

# przypisanie okien do pomieszczen (do kontroli 1/8)
OKNA_POM = {
    "0.06": ["O0-01", "O0-02"], "0.09": ["O0-03"],
    "1.02": ["O1-01", "O1-02"], "1.03": ["O1-06"], "1.04": ["O1-05"],
    "2.02": ["O2-01", "O2-07"], "2.05": ["O2-03", "O2-04"],
}

def otwor(i):
    return next(o for o in OTWORY if o["id"] == i)

if __name__ == "__main__":
    for k in ("P0", "P1", "P2"):
        pu = sum(room_area(r) for r in POMIESZCZENIA if r["kond"] == k and r["kat"] != "garaż")
        print(k, "PU", round(pu, 2), "obrys", round(outline(k).area, 2), outline(k).bounds)
    for r in POMIESZCZENIA:
        print(r["id"], r["nazwa"], room_area(r))
