# -*- coding: utf-8 -*-
"""W3 - I PIETRO P1 (+3,15): sciany, otwory, pomieszczenia. Pustka nad jadalnia: x 4,50...8,40, y 0,15...4,00."""
from shapely.geometry import box
from base_w3 import W, O, R, E, SZACHT_SI, SZACHT_S2, SCH_X, SCH_Y

PUSTKA = box(4.50, 0.15, 8.40, 4.00)   # otwor w ST1 (jadalnia 2-kondygnacyjna); krawedz pd. = podciag PD-1 w ST1 (y -0,15...0,15)

SCIANY_P1 = [
    W("S1-01", "P1", "SZ1", (0, 0), (12, 0), E, E, "ściana pd. bryły B: pełna 0...4,5 i 11,7...12, boks C 4,5...11,7 na słupkach SLC w osiach 6,9 / 9,3"),
    W("S1-02", "P1", "SZ1", (12, 0), (12, 8.9), E, E, "ściana wsch. (oś E)"),
    W("S1-03", "P1", "SZ1", (12, 8.9), (0, 8.9), E, E, "ściana pn. (oś 4)"),
    W("S1-04", "P1", "SZ1", (0, 8.9), (0, 0), E, E, "ściana zach. (oś A) - pod wspornikiem P2"),
    W("S1-05", "P1", "SW18", (0, 5.4), (12, 5.4), 0, 0, "ściana grzbietowa (oś 3)"),
    W("S1-06", "P1", "SW18", (4.05, 5.4), (4.05, 8.9), 0, 0, "oś B"),
    W("S1-07", "P1", "SW18", (6.4, 5.4), (6.4, 8.9), 0, 0, "oś C - na podciągu PD-C w ST1"),
    W("S1-08", "P1", "SW18", (9.65, 5.4), (9.65, 8.9), 0, 0, "oś D"),
    W("S1-09", "P1", "DZL", (0, 4.0), (4.5, 4.0), 0, 0, "pokój dziecka 1 / galeria"),
    W("S1-10", "P1", "DZL", (4.5, 0), (4.5, 4.0), 0, 0, "pokój dziecka 1 / pustka - na podciągu PD-2 (oś B')"),
]

OTWORY_P1 = [
    O("O1-01", "S1-01", 4.50, 11.70, "boks", 1.50, 0.50, "BC1", kw=3, podz=[6.90, 9.30],
      uw="boks C: 3 kwatery 2,40 m, szkło 3,65...5,15, dolna część stała VSG do 0,85 (W-097); przed pustką i pokojem rodzinnym"),
    O("O1-02", "S1-04", 1.00, 3.00, "okno", 1.50, 0.85, "OZ3", uw="pokój dziecka 1 - zachód"),
    O("O1-03", "S1-04", 6.10, 8.10, "okno", 1.50, 0.85, "OZ3", uw="pokój dziecka 2 - zachód"),
    O("O1-04", "S1-02", 1.00, 3.40, "okno", 1.50, 0.85, "OE1", uw="pokój rodzinny - wschód, widok na dach zielony garażu"),
    O("O1-05", "S1-03", 7.40, 8.80, "okno", 0.60, 1.50, "ON2", uw="łazienka"),
    O("O1-06", "S1-03", 10.30, 11.40, "okno", 0.60, 1.50, "ON2", uw="pralnia"),
    O("O1-07", "S1-03", 4.40, 6.00, "okno", 2.40, 0.40, "ON3", uw="okno klatki (spocznik 4,725) - światło pn. w rdzeniu"),
    O("O1-08", "S1-05", 1.20, 2.10, "drzwi", 2.05, 0.0, "D1", "a", "+y", "pokój dziecka 2"),
    O("O1-09", "S1-05", 4.155, 6.295, "otwor", 2.60, 0.0, "", uw="klatka schodowa - wyjście biegu 2 i wejście na bieg 3"),
    O("O1-10", "S1-05", 7.10, 7.90, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka (na zewnątrz)"),
    O("O1-11", "S1-05", 10.00, 10.80, "drzwi", 2.05, 0.0, "D1", "b", "+y", "pralnia"),
    O("O1-12", "S1-09", 2.60, 3.50, "drzwi", 2.05, 0.0, "D1", "a", "-y", "pokój dziecka 1"),
]

POM_P1 = [
    R("1.01", "Galeria nad pustką (hol)", "P1", box(0.105, 4.0625, 8.40, 5.295), "ruchu", posadzka="dąb",
      uw="balustrada szklana 1,00 m wzdłuż pustki; od pd. światło boksu C"),
    R("1.02", "Pokój rodzinny / biblioteka (boks C)", "P1", (8.40, 0.105, 11.895, 5.295), "podstawowa", True, 16.0, "dąb",
      "otwarty na galerię i pustkę (balustrada), wyjście schodów"),
    R("1.03", "Pokój dziecka 1", "P1", (0.105, 0.105, 4.4375, 3.9375), "podstawowa", True, 12.0, "dąb", "z szafą wnękową"),
    R("1.04", "Pokój dziecka 2", "P1", (0.105, 5.505, 3.945, 8.795), "podstawowa", True, 12.0, "dąb"),
    R("1.05", "Klatka schodowa", "P1", (SCH_X[0], SCH_Y[0], SCH_X[1], SCH_Y[1]), "ruchu", posadzka="dąb"),
    R("1.06", "Łazienka", "P1", box(6.505, 5.505, 9.545, 8.795).difference(SZACHT_SI), "pomocnicza", posadzka="gres",
      uw="wanna + prysznic + 2 umywalki + WC"),
    R("1.07", "Pralnia z suszarnią", "P1", box(9.755, 5.505, 11.895, 8.795).difference(SZACHT_S2), "pomocnicza", posadzka="gres"),
]
OKNA_POM_P1 = {"1.02": ["O1-01", "O1-04"], "1.03": ["O1-02"], "1.04": ["O1-03"]}
# udzial boksu C przypadajacy na pokoj rodzinny (x 8,40...11,70) - do kontroli 1/8
BOKS_UDZIAL = {"1.02": (8.40, 11.70)}
