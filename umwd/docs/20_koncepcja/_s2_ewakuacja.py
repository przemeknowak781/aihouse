# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 – ewakuacja (budynek W, ZL I), szerokości, klatki, dźwigi i holy windowe.

Uruchomienie (z katalogu umwd/):  python3 docs/20_koncepcja/_s2_ewakuacja.py
Sekcje [E1]…[E6] przywołuje kondygnacja_S2.md. Podstawa: ppoz.md rozdz. 5 (WT § 237, 238, 239, 242, 246, 256),
dostepnosc.md (M.13 s. 170–173), PN-EN 81-20 tabl. 6 (maks. pole kabiny wg udźwigu).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s2_model as M  # noqa: E402
from shapely.geometry import Point, LineString, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402


def hr(t):
    print("\n" + "=" * 96 + "\n" + t + "\n" + "=" * 96)


S = M.level_S()
A = M.level_ANT()
rows, aisles = M.build_rows()
CELLS = {**M.CORE_A_CELLS, **M.CORE_B_CELLS}

# -------------------------------------------------------------------------------------------------
hr("[E1] Liczba osób (maks. jednoczesna) i szerokości klatek (WT § 68: 0,6 m / 100 os.)")
OCC = {"SWD.01 płyta": 70, "SWD.01g galeria": 34, "SWD.08": 50, "SWD.09": 30, "SWD.11a": 30, "SWD.11b": 30,
       "SWD.12a": 15, "SWD.12b": 15, "SWD.13": 12, "SWD.14": 8, "SWD.03": 20, "SWD.05 + hol": 30, "obsługa/WC/inne": 10}
N = sum(OCC.values())
print("Osoby:", OCC, "→ razem", N)
print(f"Wymagana łączna szerokość biegów: 0,6 × {N / 100:.2f} = {0.6 * N / 100:.2f} m; projekt: klatki A i B po 1,60 m = 3,20 m ✔")
print(f"Kuluar (droga pozioma): 0,6 × {N / 100:.2f} = {0.6 * N / 100:.2f} m ≤ 2,20 m ✔ (min. WT 1,40 m; M.13 1,80 m)")
print("Sala (> 50 os., > 300 m² z galerią): wyjścia 3 + drzwi prezydium; odstęp ≥ 5 m; drzwi otwierane na zewnątrz ✔ (§ 238, § 239)")

# -------------------------------------------------------------------------------------------------
hr("[E2] Długości przejść (w pomieszczeniu) i dojść (od drzwi pomieszczenia do drzwi przedsionka) – ZL I, budynek W")
LIM = {"przejscie": 40.0, "przejscie_h5": 40.0 * 1.25, "dojscie_1": 10.0, "dojscie_1_odd": 15.0,
       "dojscie_2": 40.0, "dojscie_2_odd": 60.0}
print("Limity (v1.1/v1.2: tryskacze NIEPROJEKTOWANE – rejestr v1.1 E-I-4): przejście 40 m (sala/hol h > 5 m: +25 % → 50 m);"
      " dojście ZL I: 1 kierunek 10 m, ≥ 2 kierunki 40 m; kuluar i korytarz publiczny z samoczynnym oddymianiem"
      " sterowanym SSP → +50 % (§ 256 ust. 3: 15 / 60 m; wykładnia do potwierdzenia z rzeczoznawcą ppoż., ppoz.md 5.3).")
walk_S = unary_union([g for g in S.values()] + [CELLS["przedsionek_A"], CELLS["przedsionek_B"]])
walk_A = unary_union([g for g in A.values()] + [CELLS["przedsionek_A"], CELLS["przedsionek_B"]])


def length(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))


def check(pts, walk):
    ln = LineString(pts)
    return ln.difference(walk.buffer(0.32)).length      # ściany przekraczane tylko w drzwiach (≤ 0,30 m)


ROUTES = [
    # nazwa, poziom, przejście (do drzwi pomieszczenia / wyjścia na drogę), dojście (do drzwi przedsionka), cel
    ("Sala: media NE → przejście wsch. → drzwi SE → kuluar → przedsionek B", "S",
     [(33.8, 25.3), (36.9, 19.4), (31.4, 16.4), (32.6, 13.0), (32.6, 12.45)], [(32.6, 12.45), (32.6, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("Sala: media NE → za rzędem 4 → przejście zach. → drzwi SW → kuluar → przedsionek A", "S",
     [(33.8, 25.3), (27.5, 27.6), (22.55, 26.0), (22.55, 13.0), (22.7, 12.45)], [(22.7, 12.45), (22.7, 11.2), (13.7, 11.2), (13.7, 11.85)], "A"),
    ("Sala: rząd 4 wsch. koniec → przejście wsch. → drzwi SE → przedsionek B", "S",
     [(38.0, 19.0), (31.4, 16.4), (32.6, 13.0), (32.6, 12.45)], [(32.6, 12.45), (32.6, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("Galeria: rząd 2 pn. koniec → foyer → przedsionek A (+30,90)", "ANT",
     [(20.4, 22.3), (19.2, 22.3), (17.0, 17.0), (15.5, 15.6)], [], "A"),
    ("Galeria: rząd 2 pn. koniec → korytarz publiczny → przedsionek B (+30,90)", "ANT",
     [(20.4, 22.3), (19.2, 22.3), (17.5, 13.0), (17.5, 12.45)], [(17.5, 12.45), (17.5, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("WC publiczności PHS.05c → hol P1/P2 → korytarz → przedsionek B (+30,90)", "ANT",
     [(36.8, 4.3), (34.8, 5.3)], [(34.8, 5.3), (32.9, 6.5), (32.9, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("Antresola radnych: bar NE → hol górny → przedsionek A' (+30,90)", "ANT",
     [(21.4, 27.6), (13.0, 24.0), (7.3, 21.0), (7.3, 15.5)], [], "A"),
    ("Antresola radnych: bar NE → schody reprezentacyjne → hol → łącznik → kuluar → przedsionek B", "ANT/S",
     [(21.4, 27.6), (13.0, 25.6), (5.4, 25.6), (12.3, 25.6), (13.0, 22.0), (16.2, 21.0), (16.2, 12.3)],
     [(16.2, 12.3), (16.2, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("Hol: naroże NW → pasaż zach. → kuluar → przedsionek A", "S",
     [(0.9, 28.8), (7.4, 22.5), (7.4, 20.85)], [(7.4, 20.85), (7.4, 11.2), (13.7, 11.2), (13.7, 11.85)], "A"),
    ("Hol: naroże NW → łącznik wsch. → przedsionek A (drzwi wsch.)", "S",
     [(0.9, 28.8), (11.0, 23.6), (16.2, 21.4), (16.2, 20.85)], [(16.2, 20.85), (16.2, 16.6), (15.5, 16.6)], "A"),
    ("SWD.13: naroże NE → drzwi → łącznik → przedsionek A", "S",
     [(21.4, 28.9), (17.2, 23.2), (17.2, 22.75)], [(17.2, 22.75), (16.2, 21.4), (16.2, 16.6), (15.5, 16.6)], "A"),
    ("SWD.08: naroże SW → drzwi → kuluar → przedsionek A", "S",
     [(0.9, 0.9), (4.0, 9.7), (4.0, 10.0)], [(4.0, 10.0), (4.0, 11.2), (13.7, 11.2), (13.7, 11.85)], "A"),
    ("SWD.08: naroże SW → drzwi → kuluar → przedsionek B", "S",
     [(0.9, 0.9), (8.0, 9.7), (8.0, 10.0)], [(8.0, 10.0), (8.0, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("SWD.11b: naroże SE → dojście → kuluar → przedsionek B", "S",
     [(39.2, 0.9), (31.9, 7.0), (31.9, 7.2)], [(31.9, 7.2), (31.9, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
    ("SWD.11b: naroże SE → dojście → kuluar → przedsionek A", "S",
     [(39.2, 0.9), (31.9, 7.0), (31.9, 7.2)], [(31.9, 7.2), (31.9, 11.2), (13.7, 11.2), (13.7, 11.85)], "A"),
    ("PP.06 (koniec kuluaru wsch.) → przedsionek B", "S",
     [(39.2, 9.6), (38.4, 10.0)], [(38.4, 10.0), (38.4, 11.2), (27.0, 11.2), (27.0, 9.9)], "B"),
]
res = {}
for nm, lvl, pr, dj, tgt in ROUTES:
    walk = walk_A if lvl.startswith("ANT") and lvl != "ANT/S" else walk_S
    if lvl == "ANT/S":
        off = 0.0
    else:
        off = check(pr + dj[1:], walk) if dj else check(pr, walk)
    lp = length(pr)
    if lvl == "ANT/S":
        lp += math.hypot(7.2, 3.6) - 7.2          # bieg schodów: długość po linii biegu
    ld = length(dj) if dj else 0.0
    res[nm] = (lp, ld)
    print(f"  {nm}\n     przejście {lp:5.1f} m, dojście {ld:5.1f} m → klatka {tgt}" + (f"   (poza komunikacją {off:.2f} m)" if off > 0.01 else ""))
print("Ocena:")
print("  – sala: dwa kierunki (klatki A i B), przejście ≤ %.1f m (≤ 50 m dla h > 5 m, bez tryskaczy), dojście ≤ %.1f m (≤ 40 m) ✔"
      % (max(res[k][0] for k in res if k.startswith("Sala")), max(res[k][1] for k in res if k.startswith("Sala"))))
print("  – galeria: dwie niezależne drogi – przedsionek A (%.1f m) i przedsionek B (%.1f m) ✔"
      % (sum(res["Galeria: rząd 2 pn. koniec → foyer → przedsionek A (+30,90)"]),
         sum(res["Galeria: rząd 2 pn. koniec → korytarz publiczny → przedsionek B (+30,90)"])))
print("  – antresola radnych: przedsionek A' → klatka A (%.1f m) oraz schody reprezentacyjne → hol → kuluar → klatka B"
      " (%.1f m) ✔" % (sum(res["Antresola radnych: bar NE → hol górny → przedsionek A' (+30,90)"]),
                      sum(res["Antresola radnych: bar NE → schody reprezentacyjne → hol → łącznik → kuluar → przedsionek B"])))
dead = 38.4 - 27.0
print(f"  – ślepy odcinek kuluaru wsch. (od drzwi przedsionka B do PP.06): {dead:.1f} m > 10 m, ≤ 15 m przy samoczynnym"
      " oddymianiu kuluaru (§ 256 ust. 3, bez tryskaczy) ✔*; zach. część kuluaru ma drugi kierunek przez pasaż i hol do"
      " łącznika/przedsionka A ✔")
one_dir = {k: v[1] for k, v in res.items() if k.startswith(("PP.06", "WC publiczności", "SWD.11b: naroże SE → dojście → kuluar → przedsionek B"))}
print("  – dojścia jednokierunkowe > 10 m (wymagają +50 % za samoczynne oddymianie drogi; limit 15 m):",
      {k[:40]: round(v, 1) for k, v in one_dir.items()}, "– wszystkie ≤ 15 m ✔*")
# v1.2 (I5): zwężenie kuluaru przy wydłużonym trzonie A
kul_a = S["KUL"].intersection(box(M.CORE_A.bounds[0], 9.0, M.CORE_A.bounds[2], 13.0))
w_a = M.CORE_A.bounds[1] - 10.10
west_occ = OCC["SWD.08"] + OCC["SWD.12a"] + OCC["SWD.12b"] + 4
print(f"  – v1.2: kuluar przy trzonie A {w_a:.2f} m na długości {M.CORE_A.bounds[2] - M.CORE_A.bounds[0]:.2f} m"
      f" (pole {kul_a.area:.1f} m²) ≥ 1,40 m (WT § 242) ✔; przepustowość 0,6 m/100 os. → {w_a / 0.006:.0f} os.;"
      f" odcinek obsługuje osoby z części zach. (SWD.08 + SWD.12a/b + SWD.10a/IT.02 ≈ {west_occ} os.; hol i antresola radnych"
      f" mają łącznik KW.S.03 do przedsionka A i przedsionek A') ✔; M.13 1,80 m – odstępstwo lokalne −{1.80 - w_a:.2f} m")
print("  – żadne schody z antresoli nie prowadzą do kuluaru; schody reprezentacyjne leżą w holu (strefa dymowa hol +"
      " antresola radnych, oddymianie mechaniczne), oddzielonym od kuluaru drzwiami EI 30 S w pasażu i łączniku (I4) ✔")

# -------------------------------------------------------------------------------------------------
hr("[E3] Strefy pożarowe i dymowe")
ant = sum(g.area for g in A.values())
print(f"Strefa ZL I = kondygnacja S + antresola: {M.W_UV.area:.1f} + {ant:.1f} = {M.W_UV.area + ant:.1f} m² ≤ 2 500 m² ✔ (§ 227)")
print("Strefy dymowe: (1) sala + galeria – oddymianie spod dachu, napowietrzanie dołem; (2) hol + antresola radnych;"
      " (3) kuluar i korytarz publiczny nad nim – drogi chronione (EI 30, drzwi S, oddymianie/nadciśnienie § 247);"
      " przedsionki A, A', B – nadciśnienie.")

# -------------------------------------------------------------------------------------------------
hr("[E4] Dźwigi – kabiny wg PN-EN 81-20 (tabl. 6: maks. pole kabiny) i M.13 s. 172")
TAB6 = {1000: 2.40, 1275: 2.95, 1350: 3.10, 1425: 3.25, 1600: 3.56}
for nm, load, (w, d), shaft in (("A1", 1600, (1.5, 2.1), M.CORE_A_CELLS["A1"]), ("A2", 1600, (1.5, 2.1), M.CORE_A_CELLS["A2"]),
                                ("P1", 1600, (1.5, 2.1), M.CORE_B_CELLS["P1"]), ("P2", 1600, (1.5, 2.1), M.CORE_B_CELLS["P2"]),
                                ("R", 1000, (1.1, 2.1), M.CORE_A_CELLS["R"])):
    a = w * d
    b = shaft.bounds
    sw, sd = b[2] - b[0], b[3] - b[1]
    print(f"  {nm}: {load} kg, kabina {w:.1f} × {d:.1f} = {a:.2f} m² ≤ {TAB6[load]:.2f} m² (tabl. 6) {'✔' if a <= TAB6[load] else '✗'};"
          f" szyb w świetle {sw:.2f} × {sd:.2f} m – luz {max(sw, sd) - d:.2f} m / {min(sw, sd) - w:.2f} m"
          f" (drzwi + przeciwwaga boczna)")
print("  P1/P2 1 275 kg z kabiną 1,4 × 2,4 (v1.0): 3,36 m² > 2,95 m² ✗ → zmiana na 1 600 kg (I5). M.13: kabina ≥ 1,5 × 2,1 ✔.")

# -------------------------------------------------------------------------------------------------
hr("[E5] Holy windowe – głębokość wolnej przestrzeni przed drzwiami (WT § 195 ≥ 1,6 m; M.13 ≥ 3,6 m)")
CIRC_S = unary_union([S[k] for k in ("SWD.02", "KUL", "KW.S.01", "KW.S.02", "KW.S.03", "KW.S.04")])
CIRC_A = unary_union([A[k] for k in ("SWD.02g", "KW.A.01", "KW.A.02")])


def depth(pt, d, free, w=M.DOOR_W_LIFT):
    """Największa głębokość prostokąta (szer. drzwi) przed drzwiami mieszczącego się w przestrzeni komunikacji."""
    nx, ny = -d[1], d[0]
    best = 0.0
    for i in range(1, 120):
        dd = i * 0.05
        q = [(pt[0] + nx * w / 2, pt[1] + ny * w / 2), (pt[0] - nx * w / 2, pt[1] - ny * w / 2),
             (pt[0] - nx * w / 2 + d[0] * dd, pt[1] - ny * w / 2 + d[1] * dd), (pt[0] + nx * w / 2 + d[0] * dd, pt[1] + ny * w / 2 + d[1] * dd)]
        from shapely.geometry import Polygon
        if Polygon(q).buffer(-0.01).within(free):
            best = dd
        else:
            break
    return best


for lift, pt, d, levels in M.LIFT_DOORS:
    for lv in levels:
        free = CIRC_S if lv.startswith("S") else CIRC_A
        p0 = (pt[0] + d[0] * 0.26, pt[1] + d[1] * 0.26) if lift.startswith("A") else (pt[0] + d[0] * 0.01, pt[1] + d[1] * 0.01)
        dep = depth(p0, d, free)
        need = 3.6 if lv != "S*" else 1.6
        print(f"  {lift} na {lv:4s}: głębokość wolna {dep:.2f} m {'✔ M.13 3,6' if dep >= 3.6 else ('✔ WT 1,6 (przystanek służbowy)' if dep >= 1.6 else '✗')}")
bA = M.CORE_A_CELLS["przedsionek_A"].bounds
print(f"  R: drzwi do przedsionka A (S i +30,90) – pole 1,5 × 1,5 m (MOE) w przedsionku {bA[2] - bA[0]:.2f} × {bA[3] - bA[1]:.2f} m ✔")

# -------------------------------------------------------------------------------------------------
hr("[E6] Klatki i przedsionki na S i +30,90; MOE (dostepnosc.md pkt 8, D9)")
for nm in ("przedsionek_A", "przedsionek_B"):
    g = CELLS[nm]
    b = g.bounds
    print(f"  {nm}: {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} m = {g.area:.1f} m², MOE 1,5 × 1,5 m poza torem 1,2 m: "
          f"{'✔' if min(b[2] - b[0], b[3] - b[1]) >= 2.4 or (b[2] - b[0]) * (b[3] - b[1]) >= 2.25 + 1.2 * 2.4 else '✗'}")
g = A["KW.A.03"]
b = g.bounds
print(f"  przedsionek A' (+30,90): {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} m = {g.area:.1f} m² (MOE 1,5 × 1,5 przy ścianie trzonu)")
print("  Klatka A i klatka B przedłużone do +30,90 (podest antresoli); klatka A: przedsionek A (drzwi wsch. na galerię)"
      " i przedsionek A' (drzwi pn. z antresoli radnych) – drzwi z kontrolą dostępu, zwalniane przez SSP.")
bk = M.CORE_A_CELLS["klatka_A"].bounds
bkB = M.CORE_B_CELLS["klatka_B"].bounds
print(f"  v1.2 (I5): klatka A {bk[2] - bk[0]:.2f} × {bk[3] - bk[1]:.2f} m (trzon A wydłużony o 0,60 m na pd.), klatka B"
      f" {bkB[2] - bkB[0]:.2f} × {bkB[3] - bkB[1]:.2f} m – biegi, stopnie i spoczniki na każdej kondygnacji: _v12_trzony.py.")
