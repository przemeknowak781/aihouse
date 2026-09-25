# -*- coding: utf-8 -*-
"""W3 - dane przekrojow (wspolrzedne y, z w ukladzie budynku). A-A: x = 8,10 (os widoku, pustka); B-B: x = 5,80 (klatka, latarnia)."""
import model_w3 as M
P = M.POZ
ST1, ST2, ST2L, ST3, ST = P["ST1"], P["ST2"], P["ST2L"], P["ST3"], M.SCHODY

# rodzaje: 'zb' - zelbet ciety, 'mur' - mur ciety, 'ins' - izolacja/warstwy, 'gl' - szklo ciete, 'wid' - widok (kontur), 'zie' - dach zielony
COMMON = [
    ("ins", -0.30, 11.60, -0.45, -0.15, "płyta fund./podbeton + XPS"), ("zb", -0.30, 11.60, -0.30, -0.15, ""),
    ("ins", -0.20, 11.50, -0.15, 0.0, "posadzka P0 z ogrz. podł."),
    ("zb", -0.30, 0.30, -1.10, -0.30, "ława/stopa"), ("zb", 5.10, 5.70, -1.10, -0.30, "ława"),
    ("zb", 8.60, 9.20, -1.10, -0.30, "ława"), ("zb", 11.00, 11.60, -1.10, -0.30, "ława"),
    # sciany grzbietowa (3) i pn. (4) na P1; strop ST2 i ST3; attyki
    ("zb", 1.20, 9.20, ST2[0], ST2[1], "ST2"), ("zb", -1.20, 1.20, ST2L[0], ST2L[1], "ST2L loggia"),
    ("ins", -0.30, 1.20, ST2L[1], 6.28, "taras: izol. spadkowa + deska"),
    ("zb", -1.20, 9.20, ST3[0], ST3[1], "ST3"), ("ins", -0.30, 8.90, ST3[1], P["dach_P2_warstwy"], "PIR spadkowy + membrana"),
    ("mur", 8.60, 9.20, P["dach_P2_warstwy"], P["attyka_P2"], "attyka"), ("mur", -0.30, -0.05, P["dach_P2_warstwy"], P["attyka_P2"], ""),
    ("lam", -0.44, -0.36, 5.90, 9.10, "lamele"),
    ("zb", 11.20, 11.60, ST1[0], P["attyka_P0"], "attyka skrzydła"), ("zie", 9.20, 11.20, ST1[1], P["dach_P0_warstwy"], "dach zielony"),
    ("zb", 11.60, 12.80, 2.80, 3.05, "daszek"),
]
SEC = {
    "A": dict(x=8.10, tytul="PRZEKRÓJ A-A (x = 8,10 — oś widoku: wejście → hol → jadalnia pod pustką → ogród)", el=COMMON + [
        ("gl", -0.08, 0.08, 0.0, 2.75, "HS kw. 4"), ("zb", -1.30, 0.30, ST1[0] - 0.25, ST1[1], "okap E + podciąg PD-1"),
        ("zb", -1.30, -0.30, 3.45, 3.65, "rama C"), ("zb", -1.30, -0.30, 5.15, 5.35, ""), ("gl", -0.08, 0.08, 3.65, 5.15, "boks C"),
        ("mur", -0.30, 0.30, 3.00, 3.65, ""), ("mur", -0.30, 0.30, 5.15, 5.70, ""),
        ("zb", 4.00, 9.20, ST1[0], ST1[1], "ST1"), ("mur", 5.20, 5.60, 2.60, ST1[0], "nadproże"),
        ("gl", 8.87, 8.93, 0.0, 2.80, "przegroda szklana"), ("zb", 8.60, 9.20, 2.55, ST1[0], "PD-4"),
        ("zb", 9.20, 9.60, ST1[0], ST1[1], ""), ("zb", 11.0, 11.20, ST1[0], ST1[1], ""), ("gl", 9.60, 11.00, 3.05, 3.35, "SW2"),
        ("mur", 11.00, 11.60, 2.40, ST1[0], ""), ("gl", 11.25, 11.35, 0.0, 2.40, "drzwi wejśc."),
        ("mur", 5.20, 5.60, ST1[1], ST2[0], "oś 3"), ("mur", 8.60, 9.20, ST1[1], 4.65, ""), ("gl", 8.85, 8.95, 4.65, 5.25, ""),
        ("mur", 8.60, 9.20, 5.25, ST2[0], ""), ("bal", 3.90, 4.10, ST1[1], 4.15, "balustrada"),
        ("mur", 0.90, 1.35, 6.28, 6.60, ""), ("mur", 0.90, 1.35, 6.30 + 2.60, ST3[0], ""), ("wid", 0.90, 1.35, 6.60, 8.90, "przeszkl. (widok)"),
        ("mur", 5.20, 5.60, ST2[1], ST3[0], "oś 3"), ("mur", 8.60, 9.20, ST2[1], 7.80, ""), ("gl", 8.85, 8.95, 7.80, 8.60, ""),
        ("mur", 8.60, 9.20, 8.60, ST3[0], ""),
    ], pom=[(2.2, 1.3, "JADALNIA (pustka)\nh = 5,70 / 5,95"), (7.2, 1.3, "HOL\nh = 2,80"), (10.1, 1.1, "WIATROŁAP\nświetlik SW2"),
            (6.8, 4.4, "GALERIA / ŁAZ."), (2.5, 4.4, "pustka"), (0.5, 7.3, "loggia"), (3.4, 7.3, "SYPIALNIA"), (7.0, 7.3, "ŁAZIENKA")]),
    "B": dict(x=5.80, tytul="PRZEKRÓJ B-B (x = 5,80 — klatka schodowa pod latarnią SW1)", el=COMMON + [
        ("gl", -0.08, 0.08, 0.0, 2.75, "kw. 3"), ("zb", -1.30, 0.30, ST1[0] - 0.25, ST1[1], "okap E + PD-1"),
        ("zb", -1.30, -0.30, 3.45, 3.65, ""), ("zb", -1.30, -0.30, 5.15, 5.35, ""), ("gl", -0.08, 0.08, 3.65, 5.15, "boks C"),
        ("mur", -0.30, 0.30, 3.00, 3.65, ""), ("mur", -0.30, 0.30, 5.15, 5.70, ""),
        ("zb", 4.00, 5.40, ST1[0], ST1[1], "ST1"), ("zb", 8.80, 11.60, ST1[0], ST1[1], ""), ("mur", 5.20, 5.60, 2.60, ST1[0], ""),
        ("mur", 8.60, 9.20, 0.0, ST1[0], "oś 4"), ("mur", 11.00, 11.60, 0.0, ST1[0], "ściana pn."),
        ("bal", 3.90, 4.10, ST1[1], 4.15, "balustrada"), ("mur", 5.20, 5.60, ST1[1] + 2.60, ST2[0], ""),
        ("mur", 8.60, 9.20, ST1[1], 8.20, "oś 4 (nadbudowa)"), ("gl", 8.85, 8.95, 8.20, 8.90, ""), ("mur", 8.60, 9.20, 8.90, ST3[0], ""),
        ("zb", 1.20, 5.40, ST2[0], ST2[1], ""), ("mur", 5.20, 5.60, ST2[1] + 2.60, ST3[0], ""), ("gl", 0.90, 1.35, 6.28, 8.90, "drzwi loggii"),
        ("gl", 5.70, 8.60, ST3[1] + 0.10, ST3[1] + 0.40, "latarnia SW1"),
    ], pom=[(2.3, 1.3, "JADALNIA\n(pustka)"), (10.0, 1.3, "PRZEDPOKÓJ\nGOŚCINNY"), (2.5, 4.4, "pustka"), (3.0, 7.3, "HOL P2"),
            (7.3, 8.3, "latarnia")]),
}
STAIRS_IN = ["B", "A"]  # biegi: w B-B ciete (pas wsch.), w A-A w widoku (za scianka C)
