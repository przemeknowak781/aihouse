# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 – sala obrad: rzędy, pochylnie, miejsca dla wózków, linie wzroku (radni i galeria),
poufność głosowania, „światło z przodu”, porównanie wariantów galerii.

Uruchomienie (z katalogu umwd/):  python3 docs/20_koncepcja/_s2_sala.py
Sekcje wydruku [S1]…[S7] są przywoływane w kondygnacja_S2.md.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s2_model as M  # noqa: E402
from shapely.geometry import Point, box, LineString, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402


def hr(t):
    print("\n" + "=" * 96 + "\n" + t + "\n" + "=" * 96)


S = M.level_S()
A = M.level_ANT()
rows, aisles = M.build_rows()
F = M.F
H_ANT = M.Z_ANT - M.Z_S          # 3,60
PRES_PTS = [(F[0] - 2.25 + i * 1.5, 13.25) for i in range(4)]   # oczy członków prezydium (siedzą, 1,20)
PRES_C = (F[0], 13.25)

# -------------------------------------------------------------------------------------------------
hr("[S1] Rzędy, stanowiska, przejścia-pochylnie, miejsca dla wózków")
tot = 0
for r in rows:
    L = math.radians(r["a1"] - r["a0"]) * r["rc"]
    print(f"Rząd {r['k']}: krawędź pulpitu R {r['R']:.2f} m, podest +{r['z']:.2f}, sektor {r['a0']:.1f}°–{r['a1']:.1f}°, "
          f"linia siedzisk {L:.2f} m → {r['n']} stanowisk × {M.DESK_W:.2f} m + 1 dla wózka ({M.WC_W:.2f} m)")
    tot += r["n"] + 1
print(f"Razem stanowisk stałych: {tot} (44 wymagane + {tot - 44} rezerwy); prezydium 4 os. przy stole 6,0 m na +0,00")
# miejsce dla wózka: prostokąt 0,9 × 1,4 mieści się w polu stanowiska i styka z przejściem zach.
for r in rows:
    am = math.radians(sum(r["a_wc"]) / 2)
    rc = r["R"] + 0.75
    c = (F[0] + rc * math.cos(am), F[1] + rc * math.sin(am))
    t = (-math.sin(am), math.cos(am))
    n = (math.cos(am), math.sin(am))
    rect = Polygon([(c[0] + s1 * 0.45 * t[0] + s2 * 0.70 * n[0], c[1] + s1 * 0.45 * t[1] + s2 * 0.70 * n[1])
                    for s1, s2 in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    ok_in = rect.within(r["wc"].buffer(0.02))
    gap = r["wc"].distance(aisles["west_ramp"])
    print(f"  wózek rząd {r['k']}: pole 0,9 × 1,4 w module {ok_in}; odległość od pochylni zach. {gap:.2f} m")
# pochylnie
print(f"Przejście wsch. promieniowe (φ = {aisles['east_phi']:.1f}°, szer. {M.AISLE_W:.2f} m): punkty zrównania co "
      f"{M.PITCH:.2f} m, przewyższenie {M.RISE:.2f} m → nachylenie {M.RISE / M.PITCH * 100:.2f} % (≤ 5 %)")
uc = sum(M.U_RAMP) / 2
vs = []
for r in rows:
    rm = r["R"] + 0.70
    dv = math.sqrt(max(0.0, rm ** 2 - (F[0] - uc) ** 2))
    vs.append(F[1] + dv if rm > abs(F[0] - uc) else None)
print("Przejście zach. (oś u = %.2f): punkty zrównania z podestami rzędów v =" % uc,
      [round(v, 2) if v else "posadzka" for v in vs])
slopes = []
prev = (None, 0.0)
for k, v in enumerate(vs):
    if v is None:
        continue
    if prev[0] is not None:
        slopes.append((M.ROW_Z[k] - prev[1]) / (v - prev[0]))
    prev = (v, M.ROW_Z[k])
if vs[0] is None:
    # od posadzki (v na krawędzi wewn. pasa rzędu 1 + 1,5 m podestu) do rzędu 2
    v0 = aisles["west_ramp"].bounds[1] + 1.5
    slopes.insert(0, (M.ROW_Z[1] - 0.0) / (vs[1] - v0))
print("  nachylenia odcinków:", [f"{s * 100:.2f} %" for s in slopes], "→ max", f"{max(slopes) * 100:.2f} %",
      "✔" if max(slopes) <= 0.0500001 else "✗")
print(f"  długość pochylni zach. {aisles['west_ramp'].bounds[3] - aisles['west_ramp'].bounds[1]:.2f} m (< 9 m bez spocznika "
      f"pośredniego: podesty rzędów pełnią rolę spoczników), poręcze obustronne 0,75 i 0,90 m, krawężnik 0,07 m")

# -------------------------------------------------------------------------------------------------
hr("[S2] Linie wzroku radnych (oczy 1,20 m nad podestem; cel: oczy prezydium 1,20 m / mówca 1,20–1,60 m)")


def c_value(eye, z_eye, target, z_t, row_front):
    """C = wysokość linii wzroku nad okiem osoby z rzędu przed (w miejscu przecięcia okręgu linii siedzisk)."""
    rf = row_front["rc"]
    ex, ey = eye
    tx, ty = target
    # parametr t na odcinku oko→cel, gdzie |P−F| = rf
    best = None
    for i in range(1, 400):
        t = i / 400
        px, py = ex + (tx - ex) * t, ey + (ty - ey) * t
        if abs(math.hypot(px - F[0], py - F[1]) - rf) < 0.03:
            best = t
            break
    if best is None:
        return None
    h_line = z_eye + (z_t - z_eye) * best
    return h_line - (row_front["z"] + M.EYE)


worst = {}
for tgt_name, tgt, zt in (("prezydium (siedzi)", None, M.EYE), ("mówca stojący", F, 1.60), ("mówca na wózku", F, 1.20)):
    cs = []
    cs2 = []
    for k in range(1, 4):
        r = rows[k]
        for (sx, sy) in r["seats"]:
            T = tgt if tgt else min(PRES_PTS, key=lambda p: math.hypot(p[0] - sx, p[1] - sy))
            c1 = c_value((sx, sy), r["z"] + M.EYE, T, zt, rows[k - 1])
            if c1 is not None:
                cs.append(c1)
            if k >= 2:
                c2 = c_value((sx, sy), r["z"] + M.EYE, T, zt, rows[k - 2])
                if c2 is not None:
                    cs2.append(c2)
        if tgt is None:
            for T in PRES_PTS:
                pass
    worst[tgt_name] = (min(cs), min(cs2) if cs2 else None)
    print(f"  cel {tgt_name}: C (rząd przed) min {min(cs) * 1000:.0f} mm; C (2 rzędy przed, stanowiska przestawione o pół modułu) "
          f"min {min(cs2) * 1000:.0f} mm")
print("Stanowiska kolejnych rzędów przesunięte o 0,5 modułu → oko radnego patrzy między głowami rzędu przed;"
      " linia wolna, gdy C(2 rzędy) ≥ 60 mm.")

# -------------------------------------------------------------------------------------------------
hr("[S3] Galeria publiczności – linie wzroku w przekroju (oczy 1,20 m; balustrada 0,70 m + część pozioma 0,50 m)")
gal = M.gallery_seats()
z_par = H_ANT + M.GAL_PARAPET_H            # wierzch balustrady = 4,30 nad posadzką sali
heads = []                                 # głowy radnych (oko + 0,12)
for r in rows:
    for p in r["seats"]:
        heads.append((p[0], p[1], r["z"] + M.EYE + 0.12))
    heads.append((r["wc_pt"][0], r["wc_pt"][1], r["z"] + M.EYE + 0.12))


def line_clear(eye, ze, T, zt):
    """Zwraca: zapas nad balustradą [m], zapas nad głowami radnych [m] (min), C nad rzędami galerii przed [m]."""
    ex, ey = eye
    tx, ty = T
    L = math.hypot(tx - ex, ty - ey)
    # balustrada: przekrój linii z płaszczyzną u = GAL_LEDGE_U0 (początek części poziomej) i u = 22,00
    res_par = 9.0
    for ub in (M.GAL_LEDGE_U0, M.GAL_PARAPET_U[1]):
        if tx != ex:
            t = (ub - ex) / (tx - ex)
            if 0 < t < 1:
                res_par = min(res_par, ze + (zt - ze) * t - z_par)
    # głowy radnych w pasie ±0,25 m od rzutu linii
    ln = LineString([eye, T])
    res_h = 9.0
    for hx, hy, hz in heads:
        p = Point(hx, hy)
        if ln.distance(p) < 0.25:
            t = ln.project(p) / L
            if 0.02 < t < 0.98:
                res_h = min(res_h, ze + (zt - ze) * t - hz)
    return res_par, res_h


gal_rows = {n: [(u, v, h, t) for (u, v, h, t) in gal if abs(u - ue) < 0.3] for n, ue, *_ in M.GAL_ROWS}
summary = []
for tgt_name, T, zt in (("prezydium (4 os.)", None, M.EYE), ("mówca przy mównicy (siedzi/wózek 1,20)", F, 1.20),
                        ("mówca stojący 1,60", F, 1.60)):
    min_par, min_head, min_c = 9, 9, 9
    for (u, v, h, t) in gal:
        targets = PRES_PTS if T is None else [T]
        for TT in targets:
            ze = h - (0.05 if t == "wozek" else 0.0)
            p, hh = line_clear((u, v), ze, TT, zt)
            min_par, min_head = min(min_par, p), min(min_head, hh)
            # C-value nad rzędem galerii przed: oko rzędu n−1 w tym samym v
            for n, ue, dz, *_ in M.GAL_ROWS:
                if abs(u - ue) < 0.3 and n > 1:
                    ue_f = [x for (nn, x, *_) in M.GAL_ROWS if nn == n - 1][0]
                    h_f = H_ANT + [d for (nn, x, d, *_) in M.GAL_ROWS if nn == n - 1][0] + M.EYE
                    tt = (ue_f - u) / (TT[0] - u)
                    min_c = min(min_c, ze + (zt - ze) * tt - h_f)
    summary.append((tgt_name, min_par, min_head, min_c))
    print(f"  cel: {tgt_name:40s} zapas nad balustradą min {min_par * 1000:5.0f} mm | nad głowami radnych min {min_head:5.2f} m"
          f" | C nad rzędem galerii przed min {min_c * 1000:4.0f} mm  {'✔' if min_par > 0.06 and min_c >= 0.06 else '✗'}")
ang = []
for (u, v, h, t) in gal:
    vx, vy = u - PRES_C[0], v - PRES_C[1]
    ang.append(math.degrees(math.atan2(abs(vx), vy)))
print(f"Kąt patrzenia na prezydium od osi stołu (0° = na wprost): {min(ang):.0f}°–{max(ang):.0f}° (mediana "
      f"{sorted(ang)[len(ang) // 2]:.0f}°); odległość {min(math.hypot(u - PRES_C[0], v - PRES_C[1]) for u, v, *_ in gal):.1f}–"
      f"{max(math.hypot(u - PRES_C[0], v - PRES_C[1]) for u, v, *_ in gal):.1f} m")
angs = [math.degrees(math.atan2(abs(u - F[0]), v - F[1])) for u, v, *_ in gal]
print(f"Kąt patrzenia na mówcę przy mównicy (mówca zwrócony na pn.): {min(angs):.0f}°–{max(angs):.0f}°")
print("Porównanie: galeria pd. v1.0 – nad prezydium, mówca widoczny od góry (kąt ~180°, brak widoku twarzy);"
      " galeria zach. S-2 weryfikatora (u 15,65–21,0 × v 12,45–20,85) przy prezydium w F (29,5; 13,4):")
s2 = [(u, v) for u in (17.0, 19.0, 20.5) for v in (13.5, 15.5, 17.5, 19.5)]
a2 = [math.degrees(math.atan2(abs(u - 29.5), v - 13.4)) for u, v in s2]
print(f"   kąt {min(a2):.0f}°–{max(a2):.0f}° (mediana {sorted(a2)[len(a2) // 2]:.0f}°) – miejsca S-3 skupione w pn. części galerii")

# -------------------------------------------------------------------------------------------------
hr("[S4] Poufność głosowania – ekrany pulpitów a oczy publiczności (filtr prywatności 4-kierunkowy ±30°)")
TILT = 15.0       # ekran odchylony od pionu o 15° (normalna 15° nad poziomem, w stronę radnego)
th_min = 180
worst_pair = None
eyes = [(u, v, h) for (u, v, h, t) in gal] + [(21.30, v, H_ANT + 1.65) for v in (16.0, 18.0, 20.0, 22.0)]  # stojący przy balustradzie
for r in rows:
    for i, (sx, sy) in enumerate(r["seats"] + [r["wc_pt"]]):
        a = math.atan2(sy - F[1], sx - F[0])
        # ekran na krawędzi pulpitu (R + 0,30), wys. podest + 0,85
        px, py, pz = F[0] + (r["R"] + 0.30) * math.cos(a), F[1] + (r["R"] + 0.30) * math.sin(a), r["z"] + 0.85
        nx, ny, nz = math.cos(a) * math.cos(math.radians(TILT)), math.sin(a) * math.cos(math.radians(TILT)), math.sin(math.radians(TILT))
        for (ex, ey, ez) in eyes:
            dx, dy, dz = ex - px, ey - py, ez - pz
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            th = math.degrees(math.acos((dx * nx + dy * ny + dz * nz) / d))
            if th < th_min:
                th_min, worst_pair = th, (r["k"], round(sx, 2), round(sy, 2), round(ex, 2), round(ey, 2))
print(f"Najmniejszy kąt między normalną ekranu a linią do oka na galerii: {th_min:.1f}° (rząd/stanowisko/oko: {worst_pair})"
      f" → {'poza stożkiem filtra ±30° ✔' if th_min > 30 else 'w stożku filtra ✗'}")
print("Dodatkowo: tryb głosowania tajnego w systemie (terminal nie wyświetla wyboru), przyciski pod osłoną pulpitu.")

# -------------------------------------------------------------------------------------------------
hr("[S5] Światło z przodu – radni patrzą na prezydium; okna w polu widzenia ±60°?")
win = []
for i in range(0, 91, 3):                                       # szkło łuku (lamele 0,25 × 0,60 co 0,90 przed szkłem)
    a = math.radians(i)
    win.append(("łuk", (M.C_ARC[0] + 13.5 * math.cos(a), M.C_ARC[1] + 13.5 * math.sin(a))))
for u in (22.3, 23.65, 25.0):                                   # okna pn. sali (u 22,0–26,0)
    win.append(("pn.", (u, 29.2)))
mins = []
for r in rows:
    for (sx, sy) in r["seats"] + [r["wc_pt"]]:
        vd = math.atan2(PRES_C[1] - sy, PRES_C[0] - sx)
        mm = 180
        for nm, (wx, wy) in win:
            wd = math.atan2(wy - sy, wx - sx)
            d = abs((math.degrees(wd - vd) + 180) % 360 - 180)
            mm = min(mm, d)
        mins.append(mm)
print(f"Radni (47 stanowisk): najmniejszy kąt między kierunkiem patrzenia na prezydium a oknem: {min(mins):.0f}° "
      f"({'okna poza polem ±60°, światło z tyłu/boku ✔' if min(mins) >= 60 else '✗'}); okno wsch. sali – za reżyserką SWD.04")
mp = []
for (px, py) in PRES_PTS:
    for nm, (wx, wy) in win:
        mp.append(abs(math.degrees(math.atan2(wx - px, wy - py))))
print(f"Prezydium (patrzy na pn.): okna łuku i pn. w polu ±{max(mp):.0f}° od osi, odległość ≥ "
      f"{min(math.hypot(wx - px, wy - py) for px, py in PRES_PTS for _, (wx, wy) in win):.1f} m – szkło za lamelami 0,60 m "
      "(osłona pionowa), rolety screen 5 %, światło TV ≥ 800 lx; galeria publiczności poza polem widzenia prezydium (z boku, zach.).")

# -------------------------------------------------------------------------------------------------
hr("[S6] Warianty galerii – dlaczego nie łuk NE (za radnymi) i nie pd. (nad prezydium)")


def max_rows_seats(gal_r_in):
    """Maks. liczba stanowisk w 4 rzędach przy galerii w łuku o krawędzi R_in od środka łuku (rzędy pod galerią
    niedopuszczalne: poufność, światło). Przeszukanie F, R1 (rozstaw 1,8 m, przejścia 1,3 m, moduł 1,0 m)."""
    best = (0, None)
    zone0 = M.INNER.intersection(M.SALA_BOX).difference(M.SWD04_BOX.buffer(0.2, join_style=2))
    for fu in (26.5, 27.5, 28.5, 29.5):
        for r1 in (3.8, 4.2, 4.6):
            z = zone0.difference(box(fu - 4.6, 12.6, fu + 4.6, 15.6))
            if gal_r_in:
                z = z.intersection(Point(M.C_ARC).buffer(gal_r_in - 0.3, resolution=128))
            z = z.difference(box(22.0, 12.6, 24.4, 29.2))
            n = 0
            for k in range(4):
                R = r1 + k * 1.8
                ok = [a for a in range(5, 176) if M.sector((fu, 15.2), R - 0.05, R + 1.45, a, a + 1, 2).within(z)]
                if not ok:
                    continue
                # najdłuższy ciągły przedział
                runs, cur = [], [ok[0]]
                for a in ok[1:]:
                    if a == cur[-1] + 1:
                        cur.append(a)
                    else:
                        runs.append(cur)
                        cur = [a]
                runs.append(cur)
                run = max(runs, key=len)
                L = math.radians(len(run)) * (R + 0.9) - 1.3 - 0.5
                n += max(0, int(L // 1.0)) + 1
            if n > best[0]:
                best = (n, (fu, r1))
    return best


for rin in (None, 12.0, 11.0, 10.2):
    n, par = max_rows_seats(rin)
    lab = "bez galerii w łuku" if rin is None else f"galeria w łuku, krawędź R {rin:.1f} m (głęb. {13.5 - rin:.1f} m)"
    print(f"  {lab:45s} → maks. {n:2d} stanowisk {'✔' if n >= 44 else '✗ < 44'}  (F_u, R1) = {par}")
print("Galeria pd. (v1.0) przykrywa prezydium – wykluczona (I1). Galeria zach. nad holem dźwigów – przyjęta.")

# -------------------------------------------------------------------------------------------------
hr("[S7] Prezydium, mównica, PJM – dostępność")
print(f"Stół prezydialny {M.PRES.bounds[2] - M.PRES.bounds[0]:.1f} × {M.PRES.bounds[3] - M.PRES.bounds[1]:.2f} m na posadzce +0,00;"
      " dojście bez stopni z kuluaru drzwiami 1,0 m za stołem i z przejść sali; mównica w F na +0,00, blat 0,75–1,20 m,"
      " pod blatem 0,90 × 0,67 × 0,60 m (M.13 s. 220), pętla indukcyjna; tłumacze PJM przy mównicy w kadrze kamery.")
d_rost = min(Point(F).distance(Point(p)) for r in rows[:1] for p in r["seats"])
print(f"Odległość mównica – 1. rząd: {d_rost:.2f} m (wolna płyta na kamery i PJM); prezydium – ściana pd.: tło pełne.")
