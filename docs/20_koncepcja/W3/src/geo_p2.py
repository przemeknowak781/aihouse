# -*- coding: utf-8 -*-
"""W3 - II PIETRO P2 (+6,30): bryla A (x -1,0...12,0; lico szklane pokoi w osi 1' y = 1,20, loggia y -0,15...1,20 za lamelami)
+ nadbudowa nad klatka i lazienka (x 4,05...9,65, y 5,40...8,90) z latarnia swietlna nad schodami."""
from shapely.geometry import box
from base_w3 import W, O, R, E, SZACHT_SI, SCH_X, SCH_Y

SCIANY_P2 = [
    W("S2-01", "P2", "SZL", (-1.0, 1.2), (12, 1.2), E, E, "lico pd. pokoi (oś 1') - lekka ściana/przeszklenia za loggią; na uskoku ST2/ST2L"),
    W("S2-02", "P2", "SZ1", (12, 1.2), (12, 5.4), E, E, "ściana wsch."),
    W("S2-03", "P2", "SZ1", (12, 5.4), (9.65, 5.4), E, 0, "ściana pn. bryły A (nad dachem P1)"),
    W("S2-04", "P2", "SZ1", (9.65, 5.4), (9.65, 8.9), 0, E, "nadbudowa - ściana wsch."),
    W("S2-05", "P2", "SZ1", (9.65, 8.9), (4.05, 8.9), E, E, "nadbudowa - ściana pn."),
    W("S2-06", "P2", "SZ1", (4.05, 8.9), (4.05, 5.4), E, 0, "nadbudowa - ściana zach."),
    W("S2-07a", "P2", "SZ1", (4.05, 5.4), (0, 5.4), 0, 0, "ściana pn. bryły A (oś 3)"),
    W("S2-07b", "P2", "SZL", (0, 5.4), (-1.0, 5.4), 0, E, "ściana pn. na wsporniku 1,0 m (lekka)"),
    W("S2-08", "P2", "SZL", (-1.0, 5.4), (-1.0, 1.2), E, E, "ściana zach. na wsporniku 1,0 m (lekka, oś A')"),
    W("S2-09", "P2", "SW18", (4.05, 5.4), (9.65, 5.4), 0, 0, "oś 3 wewn. (klatka, łazienka)"),
    W("S2-10", "P2", "SW18", (6.4, 5.4), (6.4, 8.9), 0, 0, "oś C - klatka/łazienka"),
    W("S2-11", "P2", "DZ12", (4.05, 1.2), (4.05, 5.4), 0, 0, "gabinet / hol"),
    W("S2-12", "P2", "DZ12", (6.4, 1.2), (6.4, 5.4), 0, 0, "hol / garderoba"),
    W("S2-13", "P2", "DZ12", (8.0, 1.2), (8.0, 5.4), 0, 0, "garderoba / sypialnia"),
]

OTWORY_P2 = [
    O("O2-01", "S2-01", -0.80, 3.85, "okno", 2.60, 0.0, "HS-P2", kw=2, podz=[1.55], hs=[2],
      uw="gabinet - przeszklenie na loggię (HS, W-098: D-17); za lamelami"),
    O("O2-02", "S2-01", 4.35, 6.20, "okno", 2.60, 0.0, "DL1", kw=2, podz=[5.30], hs=[2], uw="hol - wyjście na loggię"),
    O("O2-03", "S2-01", 6.65, 7.75, "okno", 1.60, 0.85, "OP2", uw="garderoba - na loggię"),
    O("O2-04", "S2-01", 8.25, 11.75, "okno", 2.60, 0.0, "HS-P2", kw=2, podz=[10.00], hs=[1], uw="sypialnia - przeszklenie na loggię (HS)"),
    O("O2-05", "S2-08", 2.00, 4.60, "okno", 1.80, 0.60, "OP1", uw="gabinet - zachód (okno na wsporniku), dolna część stała VSG"),
    O("O2-06", "S2-02", 2.00, 4.40, "okno", 1.60, 0.85, "OE2", uw="sypialnia - wschód (poranne słońce)"),
    O("O2-07", "S2-05", 7.40, 8.80, "okno", 0.80, 1.50, "ON2", uw="łazienka rodziców"),
    O("O2-08", "S2-05", 4.40, 6.00, "okno", 1.70, 0.90, "ON3", uw="okno klatki (pn.) - nad biegami P1-P2"),
    O("O2-09", "S2-11", 4.00, 4.90, "drzwi", 2.05, 0.0, "D1", "b", "-x", "gabinet"),
    O("O2-10", "S2-12", 4.00, 4.90, "drzwi", 2.05, 0.0, "D1", "b", "+x", "garderoba = przedpokój apartamentu"),
    O("O2-11", "S2-13", 4.00, 4.90, "drzwi", 2.05, 0.0, "D1", "b", "+x", "sypialnia"),
    O("O2-12", "S2-09", 4.155, 6.295, "otwor", 2.60, 0.0, "", uw="wyjście z biegu 4; balustrada nad biegiem 3"),
    O("O2-13", "S2-09", 7.00, 7.80, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka rodziców (z garderoby)"),
]

POM_P2 = [
    R("2.01", "Hol", "P2", (4.125, 1.305, 6.325, 5.295), "ruchu", posadzka="dąb", uw="klapa na dach 0,9x0,9 + drabina składana; wyjście na loggię"),
    R("2.02", "Gabinet / pokój", "P2", (-0.895, 1.305, 3.975, 5.295), "podstawowa", True, 8.0, "dąb", "wspornik 1,0 m na zachód"),
    R("2.03", "Garderoba (przedpokój apartamentu)", "P2", (6.475, 1.305, 7.925, 5.295), "pomocnicza", posadzka="dąb"),
    R("2.04", "Sypialnia rodziców", "P2", (8.075, 1.305, 11.895, 5.295), "podstawowa", True, 14.0, "dąb", "okna S (loggia) i E"),
    R("2.05", "Łazienka rodziców", "P2", box(6.505, 5.505, 9.545, 8.795).difference(SZACHT_SI), "pomocnicza", posadzka="gres",
      uw="prysznic walk-in, wanna wolnostojąca, 2 umywalki, WC"),
    R("2.06", "Przestrzeń nad klatką (latarnia)", "P2", (SCH_X[0], SCH_Y[0], SCH_X[1], SCH_Y[1]), "pustka", posadzka="-",
      uw="nie wlicza się do PU (rzut biegów liczony na P0 i P1)"),
]
OKNA_POM_P2 = {"2.02": ["O2-01", "O2-05"], "2.04": ["O2-04", "O2-06"]}
