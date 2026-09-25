# -*- coding: utf-8 -*-
"""W3 - PARTER P0 (+-0,00): sciany, otwory, pomieszczenia."""
from shapely.geometry import box
from shapely.ops import unary_union
from base_w3 import W, O, R, E, SZACHT_SI, SZACHT_S2, SCH_X, SCH_Y

SCIANY_P0 = [
    W("S0-01", "P0", "SZ1", (0, 0), (12, 0), E, E, "fasada pd. strefy dziennej (E): 5 kwater na słupach stalowych SL1-SL4 + podciąg w ST1; filar narożny 0...1,0 m"),
    W("S0-02", "P0", "SZ1", (12, 0), (12, 4.8), E, 0, "ściana wsch. kuchni (drzwi na patio poranne)"),
    W("S0-03", "P0", "SZ1", (12, 4.8), (18.4, 4.8), 0, E, "ściana pd. garażu (od patio; pełna, zielona fasada)"),
    W("S0-04", "P0", "SZ1", (18.4, 4.8), (18.4, 11.3), E, E, "ściana wsch. garażu = pion D"),
    W("S0-05", "P0", "SZ1", (18.4, 11.3), (0, 11.3), E, E, "ściana pn. garażu i skrzydła wejściowego (brama, drzwi wejściowe)"),
    W("S0-06", "P0", "SZ1", (0, 11.3), (0, 0), E, E, "ściana zach. (oś A)"),
    W("S0-07", "P0", "SWG", (12, 4.8), (12, 11.3), 0, 0, "oś E - dom/garaż (ocieplona od garażu, szczelna)"),
    W("S0-08", "P0", "SW18", (0, 5.4), (12, 5.4), 0, 0, "ściana grzbietowa (oś 3) - otwory: stopa schodów, wylot holu"),
    W("S0-09a", "P0", "SW18", (0, 8.9), (6.4, 8.9), 0, 0, "oś 4 - pod ścianą pn. P1"),
    W("S0-09b", "P0", "SK", (6.4, 8.9), (9.65, 8.9), 0, 0, "oś 4 - przeszklona przegroda wiatrołap/hol (nad nią podciąg PD-4 w ST1)"),
    W("S0-09c", "P0", "SW18", (9.65, 8.9), (12, 8.9), 0, 0, "oś 4 - pom. techn./przedsionek"),
    W("S0-10", "P0", "SW18", (4.05, 5.4), (4.05, 8.9), 0, 0, "oś B - pokój gościnny/klatka"),
    W("S0-11", "P0", "SW18", (9.65, 5.4), (9.65, 11.3), 0, 0, "oś D - hol/pom. techn., wiatrołap/przedsionek"),
    W("S0-12", "P0", "DZ12", (2.55, 8.9), (2.55, 11.3), 0, 0, "łazienka gościnna / przedpokój"),
    W("S0-13", "P0", "DZ12", (2.55, 9.9), (3.95, 9.9), 0, 0, "WC gościnne"),
    W("S0-14", "P0", "DZ12", (3.95, 9.9), (3.95, 11.3), 0, 0, "WC gościnne"),
    W("S0-15", "P0", "DZ12", (6.4, 8.9), (6.4, 11.3), 0, 0, "przedpokój gościnny / wiatrołap"),
    W("S0-16", "P0", "DZ12", (10.6, 4.0), (12, 4.0), 0, 0, "spiżarnia"),
    W("S0-17", "P0", "DZ12", (10.6, 4.0), (10.6, 5.4), 0, 0, "spiżarnia"),
    W("S0-18", "P0", "LAM", (6.4, 5.4), (6.4, 8.9), 0, 0, "ekran z lamel drewnianych klatka/hol (nad nim podciąg PD-C w ST1 pod ścianą C na P1)"),
]

OTWORY_P0 = [
    O("O0-01", "S0-01", 1.00, 11.85, "fasada", 2.75, 0.0, "FS1", kw=5, podz=[2.60, 4.50, 6.90, 9.30], hs=[2, 4],
      uw="przeszklenie E: kwatery 1,60/1,90/2,40/2,40/2,55 m (rytm szkicu narastający ku wsch.), HS w kw. 2 (salon) i 4 (oś wejścia)"),
    O("O0-02", "S0-06", 1.20, 4.40, "okno", 2.75, 0.0, "HS-W", uw="przeszklenie zach. salonu z drzwiami HS na taras zach. pod okapem 1,5 m"),
    O("O0-03", "S0-06", 6.30, 8.10, "okno", 1.50, 0.90, "OZ2", uw="pokój gościnny"),
    O("O0-04", "S0-02", 0.90, 2.10, "drzwi_zewn", 2.40, 0.0, "DZ2", "b", "-x", "drzwi przeszklone kuchnia - patio poranne"),
    O("O0-05", "S0-05", 7.45, 8.55, "drzwi_zewn", 2.40, 0.0, "DZ1", "a", "-y", "drzwi wejściowe 110x240 na osi widoku (x = 8,00)"),
    O("O0-06", "S0-05", 8.75, 9.40, "okno", 2.40, 0.10, "ON4", uw="doświetlenie boczne wiatrołapu (szkło mleczne)"),
    O("O0-07", "S0-05", 12.70, 17.70, "brama", 2.25, 0.0, "BR1", uw="brama segmentowa 500x225, kratki went. >= 0,08 m2"),
    O("O0-08", "S0-04", 5.60, 6.50, "drzwi_zewn", 2.10, 0.0, "DZ3", "a", "-x", "drzwi boczne garażu (rowery, ogród)"),
    O("O0-09", "S0-05", 0.80, 1.70, "okno", 0.60, 1.60, "ON1", uw="łazienka gościnna"),
    O("O0-10", "S0-05", 10.30, 11.30, "okno", 0.60, 1.60, "ON1", uw="przedsionek gospodarczy"),
    O("O0-11", "S0-08", 5.295, 6.295, "otwor", 2.60, 0.0, "", uw="stopa biegu 1 (P0->P1)"),
    O("O0-12", "S0-08", 6.95, 9.545, "otwor", 2.60, 0.0, "", uw="wylot holu do strefy dziennej - oś widoku"),
    O("O0-13", "S0-09a", 0.80, 1.60, "drzwi", 2.05, 0.0, "D2", "a", "-y", "łazienka gościnna (z pokoju gościnnego)"),
    O("O0-14", "S0-09a", 3.00, 3.90, "drzwi", 2.05, 0.0, "D1", "b", "-y", "pokój gościnny"),
    O("O0-15", "S0-09b", 7.55, 8.45, "drzwi", 2.10, 0.0, "DS1", "a", "-y", "drzwi szklane wiatrołap - hol (na osi)"),
    O("O0-16", "S0-09c", 10.10, 11.00, "drzwi", 2.05, 0.0, "D1", "a", "-y", "pom. techniczne"),
    O("O0-17", "S0-11", 9.80, 10.70, "drzwi", 2.05, 0.0, "D1", "b", "+x", "wiatrołap - przedsionek gosp."),
    O("O0-18", "S0-07", 9.40, 10.30, "drzwi", 2.05, 0.0, "DG1", "a", "-x", "garaż - przedsionek: szczelne, samozamykacz, U<=1,3"),
    O("O0-19", "S0-13", 2.75, 3.55, "drzwi", 2.05, 0.0, "D2", "a", "-y", "WC gościnne (na zewnątrz)"),
    O("O0-20", "S0-15", 9.30, 10.80, "otwor", 2.30, 0.0, "", uw="przedpokój gościnny / garderoba - wiatrołap"),
    O("O0-21", "S0-17", 4.35, 5.15, "drzwi", 2.05, 0.0, "D3", "a", "-x", "spiżarnia"),
]

SPIZ = box(10.675, 4.075, 11.895, 5.295)
POM_P0 = [
    R("0.01", "Salon + jadalnia + kuchnia", "P0", box(0.105, 0.105, 11.895, 5.295).difference(box(10.525, 3.925, 11.895, 5.295)),
      "podstawowa", True, 50.0, "dąb/gres", "jadalnia pod pustką 2-kondygnacyjną (oś B'-C'), kuchnia z wyspą przy ścianie E"),
    R("0.02", "Spiżarnia", "P0", SPIZ, "pomocnicza", posadzka="gres"),
    R("0.03", "Pokój gościnny / gabinet", "P0", (0.105, 5.505, 3.945, 8.795), "podstawowa", True, 8.0, "dąb"),
    R("0.04", "Klatka schodowa", "P0", (SCH_X[0], SCH_Y[0], SCH_X[1], SCH_Y[1]), "ruchu", posadzka="dąb"),
    R("0.05", "Hol (oś światła)", "P0", box(6.44, 5.505, 9.545, 8.87).difference(SZACHT_SI), "ruchu", posadzka="dąb"),
    R("0.06", "Pomieszczenie techniczne", "P0", box(9.755, 5.505, 11.895, 8.795).difference(SZACHT_S2), "techniczna", minimum=6.0, posadzka="gres", uw=
      "PC split (hydrobox), zasobnik CWU 300 l, bufor 100 l, centrala wentylacyjna, rozdzielacze, RG, wodomierz"),
    R("0.07", "Wiatrołap / hol wejściowy", "P0", (6.475, 8.93, 9.545, 11.195), "ruchu", posadzka="gres", uw="świetlik 1,2x2,0 m w stropodachu skrzydła"),
    R("0.08", "Przedsionek gospodarczy", "P0", (9.755, 9.005, 11.895, 11.195), "ruchu", posadzka="gres", uw="garaż - dom; szafa na buty/kurtki robocze"),
    R("0.09", "Łazienka gościnna (prysznic)", "P0", (0.105, 9.005, 2.475, 11.195), "pomocnicza", posadzka="gres"),
    R("0.10", "WC gościnne", "P0", (2.625, 9.975, 3.875, 11.195), "pomocnicza", posadzka="gres", uw="szer. 1,25 >= 0,90 (W-060)"),
    R("0.11", "Przedpokój gościnny / garderoba", "P0", unary_union([box(2.625, 9.005, 6.325, 9.825), box(4.025, 9.825, 6.325, 11.195)]),
      "ruchu", posadzka="dąb", uw="szafy wnękowe 0,6 m wzdłuż ściany pn."),
    R("0.12", "Garaż 2-stanowiskowy", "P0", (12.22, 4.905, 18.295, 11.195), "garaż", posadzka="posadzka żywiczna", uw="w świetle 6,08 x 6,29 m"),
]
OKNA_POM_P0 = {"0.01": ["O0-01", "O0-02"], "0.03": ["O0-03"]}
