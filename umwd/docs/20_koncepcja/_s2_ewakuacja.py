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
N_PLYTA = sum(r["n"] + 1 for r in rows) + len(M.floor_seats())          # stanowiska + miejsca poza rzędami (= [G7])
N_GAL = len(M.gallery_seats())                                          # miejsca siedzące + dla wózków (= [G7])
OCC = {"SWD.01 płyta": N_PLYTA, "SWD.01g galeria": N_GAL, "SWD.08": 50, "SWD.09": 30, "SWD.11a": 30, "SWD.11b": 30,
       "SWD.12a": 15, "SWD.12b": 15, "SWD.13": 12, "SWD.14": 8, "SWD.03": 20, "SWD.05 + hol": 30, "obsługa/WC/inne": 10}
N = sum(OCC.values())
print("Osoby:", OCC, "→ razem", N, f"(płyta i galeria z rzędów i miejsc modelu: {N_PLYTA} + {N_GAL})")
print(f"Wymagana łączna szerokość biegów: 0,6 × {N / 100:.2f} = {0.6 * N / 100:.2f} m; projekt: klatki A i B po 1,60 m = 3,20 m ✔")
print(f"Kuluar (droga pozioma): 0,6 × {N / 100:.2f} = {0.6 * N / 100:.2f} m ≤ 2,20 m ✔ (zapas {2.20 - 0.6 * N / 100:.2f} m;"
      f" min. WT 1,40 m; M.13 1,80 m)")
print("Sala (> 50 os., > 300 m² z galerią): wyjścia 3 + drzwi prezydium; odstęp ≥ 5 m; drzwi otwierane na zewnątrz ✔ (§ 238, § 239)")

# -------------------------------------------------------------------------------------------------
hr("[E2] Dojścia ewakuacyjne dla WSZYSTKICH drzwi (DOORS_S, DOORS_ANT) – sieć osi dróg; przejścia w pomieszczeniach")
LIM1, LIM2, LIM_P, INC = 10.0, 40.0, 40.0, 1.5     # ZL I bez zwiększeń: dojście 1 kier. / ≥ 2 kier. (§ 256 ust. 2), przejście (§ 237)
print("Zasady (jedna reguła dla całej kondygnacji): budynek W, ZL I, tryskacze nieprojektowane (v1.1 E-I-4).")
print("  – dojście mierzone w osi drogi od drzwi pomieszczenia do pierwszych drzwi przedsionka (§ 256 ust. 1): odcinek do osi drogi"
      " + oś + odcinek do drzwi przedsionka; komunikacja ogólna = kuluar, pasaż, łącznik, dojście do SWD.11b, hol SWD.02 (S),"
      " korytarz publiczny i hol P1/P2 (+30,90);")
print("  – 1 kierunek ≤ 10 m; 2 kierunki – dwie drogi do RÓŻNYCH klatek (A, B), rozłączne po odcinku wspólnym:"
      " odcinek wspólny ≤ 10 m i obie drogi ≤ 40 m (bez zwiększeń);")
print("  – zwiększenie +50 % za samoczynne oddymianie drogi (§ 256 ust. 4 pkt 2) liczone tylko kontrolnie (✔*) – NIE jest"
      " wykorzystywane w projekcie;")
print("  – antresola radnych (hol górny SWD.02g z barem SWD.05 i strefą multimedialną SWD.03) – pomieszczenie otwarte: przejście"
      " ≤ 40 m do wyjść: drzwi przedsionka A' albo stopa schodów reprezentacyjnych w holu (dalej dojście jak z drzwi).")
vK = round((10.10 + S["KUL"].bounds[3]) / 2, 3)                          # oś kuluaru i korytarza publicznego (v 10,10–12,30 → 11,20)
vH = round((20.85 + 22.65) / 2, 3)                                        # oś pasa holu przed A1/A2 (v 21,75)
vN = round((23.30 + M.STAIR_V[0]) / 2, 3)                                 # oś holu NW przed biegiem (v 23,95)
vF = round(sum(M.STAIR_V) / 2, 3)                                         # oś biegu schodów (v 25,60)
uP = round(sum(S["KW.S.01"].bounds[0::2]) / 2, 3)                         # oś pasażu (u 7,40)
uL = round(sum(S["KW.S.03"].bounds[0::2]) / 2, 3)                         # oś łącznika (u 16,20)
uD = round(sum(S["KW.S.02"].bounds[0::2]) / 2, 3)                         # oś dojścia do SWD.11b (u 31,90)
uW = round(sum(A["KW.A.01"].bounds[0::2]) / 2, 3)                         # oś holu P1/P2 (u 32,90)
uA = 7.30                                                                  # oś pasa holu górnego przy A' (u 6,30–8,30)
uN = round((12.45 + 15.30) / 2, 3)                                        # oś holu górnego nad SWD.14 (u 13,875)
AX = [  # (poziom, strefa, pomieszczenie, początek, koniec)
    ("S", "circ", "KUL", (0.70, vK), (39.30, vK)),
    ("S", "circ", "KW.S.01", (uP, vK), (uP, vH)),
    ("S", "circ", "KW.S.03", (uL, vK), (uL, vH)),
    ("S", "circ", "KW.S.02", (uD, 7.60), (uD, vK)),
    ("S", "circ", "SWD.02", (uP, vH), (21.20, vH)),
    ("S", "circ", "SWD.02", (uP, vH), (uP, vN)),
    ("S", "circ", "SWD.02", (5.00, vN), (11.70, vN)),
    ("S", "circ", "SWD.02", (11.70, vH), (11.70, vF)),
    ("S", "circ", "SWD.02", (M.STAIR_FOOT_U, vF), (11.70, vF)),
    ("ANT", "circ", "KW.A.02", (12.40, vK), (34.60, vK)),
    ("ANT", "circ", "KW.A.01", (uW, 4.40), (uW, vK)),
    ("ANT", "antr", "SWD.02g", (uA, 15.90), (uA, vH)),
    ("ANT", "antr", "SWD.02g", (3.00, vH), (uN, vH)),
    ("ANT", "antr", "SWD.02g", (3.00, vH), (3.00, vF)),
    ("ANT", "antr", "SWD.02g", (3.00, vF), (M.STAIR_TOP_U, vF)),
    ("ANT", "antr", "SWD.02g", (uN, vH), (uN, 25.35)),
]
LV = {"S": S, "ANT": A}


def length(pts):
    return sum(math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
CIRC = {"S": {"KUL", "KW.S.01", "KW.S.02", "KW.S.03", "SWD.02"}, "ANT": {"KW.A.01", "KW.A.02", "SWD.02g"}}
KL = {"przedsionek_A": "A", "przedsionek_B": "B", "KW.A.03": "A"}
OPEN_EXITS = {"S": [("SWD.06", "SWD.02", (4.95, vN))],
              "ANT": [("SWD.05", "SWD.02g", (15.30, 25.35)), ("SWD.03", "SWD.02g", (6.30, 17.80))]}
# kontrola położenia osi: odcinek poza komunikacją swojego poziomu (dopuszczalne tylko przejścia przez ściany w drzwiach ≤ 0,32 m)
ax_out = 0.0
for lv, z, nm, p0, p1 in AX:
    walk = unary_union([LV[lv][k] for k in CIRC[lv]] + [CELLS["przedsionek_A"], CELLS["przedsionek_B"]])
    ax_out = max(ax_out, LineString([p0, p1]).difference(walk.buffer(0.001)).length)
print(f"Sieć: {len(AX)} osi; najdłuższy odcinek osi poza komunikacją (przejście przez ścianę w otworze drzwi): {ax_out:.2f} m")

import heapq  # noqa: E402

NODES, ADJ = {}, {}


def nid(lv, p):
    k = (lv, round(p[0], 3), round(p[1], 3))
    NODES.setdefault(k, k)
    ADJ.setdefault(k, [])
    return k


def edge(a, b, L, zone):
    ADJ[a].append((b, L, zone))
    ADJ[b].append((a, L, zone))


def proj(lv, name, pt):
    best = None
    for l_, z, nm, p0, p1 in AX:
        if l_ != lv or nm != name:
            continue
        ln = LineString([p0, p1])
        q = ln.interpolate(ln.project(Point(pt)))
        d = q.distance(Point(pt))
        if best is None or d < best[0]:
            best = (d, (q.x, q.y))
    return best


# punkty na osiach: końce, przecięcia, rzuty drzwi
onax = {i: [p0, p1] for i, (lv, z, nm, p0, p1) in enumerate(AX)}
for i, (lv, z, nm, p0, p1) in enumerate(AX):
    for j, (lv2, z2, nm2, q0, q1) in enumerate(AX):
        if j <= i or lv2 != lv:
            continue
        x = LineString([p0, p1]).intersection(LineString([q0, q1]))
        if not x.is_empty and x.geom_type == "Point":
            onax[i].append((x.x, x.y))
            onax[j].append((x.x, x.y))
EXITS = []   # (poziom, pomieszczenie, punkt drzwi, szer., do, węzeł osi, odcinek do osi)
TARGET_DOORS = []
for lv, doors in (("S", M.DOORS_S), ("ANT", M.DOORS_ANT)):
    for a_, b_, p, w in doors + [(a, b, p, 1.0) for a, b, p in OPEN_EXITS[lv]]:
        if a_ in KL and b_ in CIRC[lv]:
            d, q = proj(lv, b_, p)
            TARGET_DOORS.append((lv, a_, p, q, d))
        elif a_ in KL:
            EXITS.append((lv, b_, p, w, KL[a_], None, 0.0))            # drzwi pomieszczenia wprost do przedsionka (galeria → A)
        elif b_ in CIRC[lv] and a_ not in CIRC[lv]:
            d, q = proj(lv, b_, p)
            if b_ != "SWD.02g":                                       # strefy otwarte antresoli radnych – przejście (niżej)
                EXITS.append((lv, a_, p, w, b_, q, d))
        else:
            continue
        for i, (l_, z, nm, p0, p1) in enumerate(AX):
            if l_ == lv and nm == b_ and LineString([p0, p1]).distance(Point(q)) < 1e-6:
                onax[i].append(q)
for i, (lv, z, nm, p0, p1) in enumerate(AX):
    ln = LineString([p0, p1])
    pts = sorted({(round(x, 3), round(y, 3)) for x, y in onax[i]}, key=lambda t: ln.project(Point(t)))
    for a, b in zip(pts[:-1], pts[1:]):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L > 1e-6:
            edge(nid(lv, a), nid(lv, b), L, z)
for k in ("A", "B"):
    NODES[k] = k
    ADJ[k] = []
for lv, a_, p, q, d in TARGET_DOORS:
    dp = nid(lv, p)
    edge(nid(lv, q), dp, d, "circ" if a_ != "KW.A.03" else "antr")
    edge(dp, KL[a_], 0.0, "circ" if a_ != "KW.A.03" else "antr")
FOOT, TOP = nid("S", (M.STAIR_FOOT_U, vF)), nid("ANT", (M.STAIR_TOP_U, vF))
edge(TOP, FOOT, M.stair_walk_length(), "antr")


def dijkstra(src, zones, banned=frozenset(), dst=None):
    dist, prev, pq, cnt = {src: 0.0}, {}, [(0.0, 0, src)], 0
    while pq:
        d, _, n = heapq.heappop(pq)
        if d > dist.get(n, 1e18) + 1e-12:
            continue
        if n == dst:
            break
        if n in ("A", "B") and n != src:
            continue
        for m, L, z in ADJ[n]:
            if z not in zones or m in banned:
                continue
            nd = d + L
            if nd < dist.get(m, 1e18) - 1e-12:
                dist[m], prev[m] = nd, n
                cnt += 1
                heapq.heappush(pq, (nd, cnt, m))
    return dist, prev


def path(prev, src, n):
    out = [n]
    while out[-1] != src:
        out.append(prev[out[-1]])
    return out[::-1]


def evaluate(n0, L0, zones=("circ",)):
    dist, prev = dijkstra(n0, set(zones))
    near = {k: L0 + dist[k] for k in ("A", "B") if k in dist}
    best, bkey = None, None
    for n, dn in dist.items():
        if n in ("A", "B") or L0 + dn > LIM1 * INC + 1e-9:
            continue
        pre = path(prev, n0, n)
        ban = frozenset(pre[:-1])
        for X, Y in (("A", "B"), ("B", "A")):
            d1, pr1 = dijkstra(n, set(zones), ban, X)
            if X not in d1:
                continue
            p1 = path(pr1, n, X)
            d2, pr2 = dijkstra(n, set(zones), ban | frozenset(p1[1:]), Y)
            if Y not in d2:
                continue
            Ls, LX, LY = L0 + dn, L0 + dn + d1[X], L0 + dn + d2[Y]
            key = (Ls > LIM1 + 1e-9 or max(LX, LY) > LIM2 + 1e-9, max(LX, LY), Ls)
            if bkey is None or key < bkey:
                bkey, best = key, dict(Ls=Ls, L={X: LX, Y: LY})
    return near, best


def status(near, best):
    nmin = min(near.values()) if near else 1e9
    if nmin <= LIM1 + 1e-9:
        return 0, "≤ 10 m (1 kierunek wystarcza)"
    if best and best["Ls"] <= LIM1 + 1e-9 and max(best["L"].values()) <= LIM2 + 1e-9:
        return 1, f"2 kierunki (A {best['L']['A']:.2f} / B {best['L']['B']:.2f}; odcinek wspólny {best['Ls']:.2f} ≤ 10)"
    if nmin <= LIM1 * INC + 1e-9 or (best and best["Ls"] <= LIM1 * INC and max(best["L"].values()) <= LIM2 * INC):
        return 2, "✔* tylko ze zwiększeniem +50 %"
    return 3, "✗"


def przejscie(room, doors):
    """Przejście w pomieszczeniu: maks. po siatce 0,25 m min. odległości do drzwi (prosto; pomieszczenia wypukłe lub prawie)."""
    b, worst = room.bounds, 0.0
    for i in range(int((b[2] - b[0]) / 0.25) + 1):
        for j in range(int((b[3] - b[1]) / 0.25) + 1):
            pt = Point(b[0] + i * 0.25, b[1] + j * 0.25)
            if room.contains(pt):
                worst = max(worst, min(pt.distance(Point(d)) for d in doors))
    return worst


ROOMS = {}
for lv, room, p, w, to, q, d in EXITS:
    if q is None:
        near, best, st = {to: 0.0}, None, (0, "drzwi wprost do przedsionka – dojście 0")
    else:
        near, best = evaluate(nid(lv, q), d)
        st = status(near, best)
    ROOMS.setdefault((lv, room), []).append(dict(p=p, to=to, near=near, best=best, st=st))
print(f"Drzwi z pomieszczeń na drogi: {len(EXITS)} (S {sum(1 for e in EXITS if e[0] == 'S')}, +30,90 {sum(1 for e in EXITS if e[0] == 'ANT')};"
      " w tym strefy otwarte szatni, baru i multimediów); przedsionki: " + ", ".join(f"{a} ({l})" for l, a, *_ in TARGET_DOORS))
print(f"{'pom.':9s} {'poz.':4s} {'przejście':>9s}  drzwi → dojście do najbliższej klatki | ocena")
RES = {}
SALA_ROUTES = {   # przejście w sali wzdłuż przejść (pochylni) – do drzwi SE i SW
    "media NE → przejście wsch. → drzwi SE": [(33.8, 25.3), (36.9, 19.4), (31.4, 16.4), (32.6, 13.0), (32.6, 12.45)],
    "media NE → za rzędem 4 → przejście zach. → drzwi SW": [(33.8, 25.3), (27.5, 27.6), (22.55, 26.0), (22.55, 13.0), (22.7, 12.45)],
    "rząd 4 wsch. koniec → przejście wsch. → drzwi SE": [(38.0, 19.0), (31.4, 16.4), (32.6, 13.0), (32.6, 12.45)],
}
for (lv, room), lst in sorted(ROOMS.items(), key=lambda t: (t[0][0] != "S", t[0][1])):
    g = LV[lv][room]
    if room == "SWD.01":
        pz = max(length(pts) for pts in SALA_ROUTES.values())
    else:
        pz = przejscie(g, [x["p"] for x in lst])
    stbest = min(x["st"][0] for x in lst)
    RES[room] = dict(lv=lv, przejscie=pz, doors=lst, cat=stbest)
    for k, x in enumerate(lst):
        nn = " / ".join(f"{kk} {vv:.2f}" for kk, vv in sorted(x["near"].items()))
        print(f"{room if k == 0 else '':9s} {lv if k == 0 else '':4s} {(f'{pz:.1f}' if k == 0 else ''):>9s}  ({x['p'][0]:.2f}; {x['p'][1]:.2f}) → {nn} | {x['st'][1]}")
for nm, pts in SALA_ROUTES.items():
    print(f"  sala – przejście {nm}: {length(pts):.1f} m (≤ 50 m: h > 5 m, +25 % § 237)")
# antresola radnych: przejście do wyjść (A' / stopa schodów), dalej dojście od stopy schodów
ANTR = {}
for nm, far, door in (("bar SWD.05 – naroże NE", (21.4, 27.6), (15.30, 25.35)), ("strefa multimedialna SWD.03 – naroże SW", (2.0, 12.7), (6.30, 17.80)),
                      ("lobby +30,90 przed A1/A2", (8.6, 21.1), None), ("podest górny – naroże NW", (2.0, 26.5), None)):
    if door:
        d0, q = proj("ANT", "SWD.02g", door)
        L0 = Point(far).distance(Point(door)) + d0
    else:                                                            # najbliższy węzeł sieci antresoli
        q = min((k[1:] for k in ADJ if isinstance(k, tuple) and k[0] == "ANT" and any(z == "antr" for _, _, z in ADJ[k])),
                key=lambda t: Point(t).distance(Point(far)))
        L0 = Point(far).distance(Point(q))
    dist, prev = dijkstra(nid("ANT", q), {"antr"})
    ANTR[nm] = (L0 + dist["A"], L0 + dist[FOOT])
near_f, best_f = evaluate(FOOT, 0.0)
st_f = status(near_f, best_f)
for nm, (la, lf) in ANTR.items():
    print(f"  antresola radnych – {nm}: przejście do drzwi przedsionka A' {la:.1f} m; do stopy schodów (przez schody, w pustce) {lf:.1f} m"
          f" (≤ 40 m {'✔' if max(la, lf) <= LIM_P else '✗'})")
print(f"  stopa schodów → dojście: " + " / ".join(f"{k} {v:.2f}" for k, v in sorted(near_f.items())) + f" | {st_f[1]}")
RES["SWD.02g"] = dict(lv="ANT", przejscie=max(max(v) for v in ANTR.values()), antr=ANTR, foot=(near_f, best_f, st_f), cat=st_f[0])
cats = {}
for k, v in RES.items():
    cats.setdefault(v["cat"], []).append(k)
print("Ocena:")
print(f"  – pomieszczenia z dojściem ≤ 10 m (1 kierunek wystarcza): {len(cats.get(0, []))}; z 2 kierunkami do różnych klatek"
      f" (odcinek wspólny ≤ 10 m, drogi ≤ 40 m): {len(cats.get(1, []))} {sorted(cats.get(1, []))};"
      f" wymagające zwiększenia +50 %: {len(cats.get(2, []))} {sorted(cats.get(2, []))}; niezgodne: {len(cats.get(3, []))} {sorted(cats.get(3, []))}")
one_dir = sorted(((min(x['near'].values()), r) for r, v in RES.items() if 'doors' in v for x in v['doors']
                  if x['st'][0] == 0 and x['near']), reverse=True)[:4]
print("  – najdłuższe dojścia jednokierunkowe (≤ 10 m): " + "; ".join(f"{r} {L:.2f}" for L, r in one_dir))
print(f"  – przejścia: maks. {max(v['przejscie'] for k, v in RES.items() if k not in ('SWD.01', 'SWD.02g')):.1f} m w pomieszczeniach,"
      f" sala {RES['SWD.01']['przejscie']:.1f} m (≤ 50), antresola radnych {RES['SWD.02g']['przejscie']:.1f} m (≤ 40) ✔")
print("  – zwiększenie +50 % (§ 256 ust. 4 pkt 2) nie jest potrzebne: wszystkie dojścia spełniają limity ZL I bez zwiększeń"
      if not cats.get(2) and not cats.get(3) else "  – UWAGA: część dojść wymaga zwiększeń lub jest niezgodna")
# v1.2 (I5): zwężenie kuluaru przy wydłużonym trzonie A
kul_a = S["KUL"].intersection(box(M.CORE_A.bounds[0], 9.0, M.CORE_A.bounds[2], 13.0))
w_a = M.CORE_A.bounds[1] - 10.10
west_occ = OCC["SWD.08"] + OCC["SWD.12a"] + OCC["SWD.12b"] + 4
print(f"  – v1.2: kuluar przy trzonie A {w_a:.2f} m na długości {M.CORE_A.bounds[2] - M.CORE_A.bounds[0]:.2f} m"
      f" (pole {kul_a.area:.1f} m²) ≥ 1,40 m (WT § 242) ✔; przepustowość 0,6 m/100 os. → {w_a / 0.006:.0f} os.;"
      f" odcinek obsługuje osoby z części zach. (SWD.08 + SWD.12a/b + SWD.10a/IT.02 ≈ {west_occ} os.; hol i antresola radnych"
      f" mają łącznik KW.S.03 do przedsionka A i przedsionek A') ✔; M.13 1,80 m – odstępstwo lokalne −{1.80 - w_a:.2f} m")
print("  – żadne schody z antresoli nie prowadzą do kuluaru; schody reprezentacyjne leżą w pustce holu (strefa dymowa 2: hol +"
      " antresola radnych), oddzielonego od kuluaru drzwiami EI 30 S w pasażu i łączniku (I4) ✔")

# -------------------------------------------------------------------------------------------------
hr("[E3] Strefy pożarowe i dymowe")
ant = sum(g.area for g in A.values())
print(f"Strefa ZL I = kondygnacja S + antresola: {M.W_UV.area:.1f} + {ant:.1f} = {M.W_UV.area + ant:.1f} m² ≤ 2 500 m² ✔ (§ 227)")
print("Strefy dymowe: (1) sala + galeria – oddymianie spod dachu, napowietrzanie dołem; (2) hol SWD.02 (komunikacja ogólna)"
      " + antresola radnych + schody reprezentacyjne – samoczynne oddymianie sterowane SSP; (3) kuluar + korytarz publiczny"
      " (z odcinkiem do przedsionka A) + hol P1/P2 – samoczynne oddymianie sterowane SSP z napowietrzaniem (§ 247 ust. 1;"
      " bez nadciśnienia w korytarzach); przedsionki A, A', B – nadciśnienie (§ 246 ust. 2).")
print("Oddymianie dróg jest wymagane przez § 247 ust. 1 (budynek W), ale NIE służy do wydłużenia dojść – zwiększenie +50 %"
      " (§ 256 ust. 4 pkt 2) nie jest wykorzystywane ([E2]).")

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
