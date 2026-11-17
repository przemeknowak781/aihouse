#!/usr/bin/env python3
"""Elewacje 1:200 (Etap II, R.VII ust.2 pkt2 lit.c) — z koncepcja.json (obrysy, kondygnacje, porządki elewacyjne rozdz. 8)
oraz sąsiadów (sasiedzi.json, site.json). Rysunek tonalny: granit / ceramika (4 odcienie posesji) / metal / szkło,
cienie ościeży (światło z lewej góry), linie MPZP (18–25 m poza A; 35–45 m w strefie A), rzędne.

Wynik: build/rysunki/elewacja_{E,N,W,S,Sd}_1-200.svg + docs/70_rysunki/podglady/elewacje_1-200.png (podgląd zbiorczy).
"""
import sys, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.svg import Svg
from umwd.facade_elev import Face, draw_faces, u_of, INK
from umwd.siteplan import load_site, poly_of
from umwd.runs import ccw

K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
SAS = json.loads((ROOT / "model" / "sasiedzi.json").read_text(encoding="utf-8"))
S = load_site()
Z0 = 119.30
SCALE = 200
DEBUG = '--debug' in sys.argv
k = 1000.0 / SCALE

# ---------------------------------------------------------------- palette (NCS → sRGB approximations)
G = "#e7e2d9"        # granit strzegomski płomieniowany, S 1502-Y
C = {"M1": "#dccfbf", "M2": "#e2cdb4", "M3": "#e9e0d2", "M4": "#d9c2ad", "SEG": "#e4d4c0", "LUK": "#ebe2d5"}
ME = "#4a4541"       # aluminium anodowane, grafitowy brąz RAL 8019
GL = "#7b8792"       # szkło neutralne R ≤ 12 %
GLD = "#3d434a"      # szkło w cieniu / podcień
REC = "#2e2b29"      # głęboki cień (kond. 6, podcień)
NB_F, NB_S, NB_W = "#f2f0ec", "#8d877f", "#d9dcdf"   # sąsiedzi: tło, kreska, okna

LEV = {"P": 0.0, "1": 4.80, "2": 8.55, "3": 12.30, "4": 16.05, "5": 19.80, "6": 23.55, "S": 27.30}
FLOORS_W = [4.80, 8.55, 12.30, 16.05]       # skrzydło/segment kondygnacje 1–4
B = {b["id"]: b for b in K["bryly"]}
W_PTS, M_PTS, S_PTS = (B[i]["obrys_ccw"] for i in ("W", "M", "S"))


def window(F, s0, w, z0, h, reveal=0.35, fill=GL, mull=True, transom=None):
    F.rect(s0, s0 + w, z0, z0 + h, fill=fill, stroke=INK, sw=0.06)
    sh = min(reveal * 0.75, h * 0.3)
    F.rect(s0, s0 + w, z0 + h - sh, z0 + h, fill=INK, op=0.32)
    F.rect(s0, s0 + min(reveal * 0.6, w * 0.35), z0, z0 + h - sh, fill=INK, op=0.26)
    if mull and w > 1.4:
        F.vline(s0 + w / 2, z0, z0 + h, stroke=ME, sw=0.07)
    if transom:
        F.hline(s0, s0 + w, z0 + transom, stroke=ME, sw=0.06)


# ---------------------------------------------------------------- wing / segment: "porządek kamieniczny"
def kamienica_upper(F, s_lo, s_hi, tint, relief=0.0, axis=2.025, win=(1.2, 2.4), sill=0.9, anchor="hi", floors=FLOORS_W):
    F.rect(s_lo, s_hi, 4.80, 20.15, fill=tint, stroke="none")
    n = int(round((s_hi - s_lo) / axis + 1e-6))
    cs = [(s_hi - (j + 0.5) * axis) if anchor == "hi" else (s_lo + (j + 0.5) * axis) for j in range(n)]
    for c in cs:
        for zf in floors:
            window(F, c - win[0] / 2, win[0], zf + sill, win[1], reveal=0.35, mull=False, transom=1.75)
        if relief > 0:      # pier relief: thin cast shadow right of each pier
            F.rect(c + win[0] / 2, c + win[0] / 2 + relief * 0.9, 4.80, 20.15, fill=INK, op=0.10)
    return cs


def cokol(F, s_lo, s_hi, z_g, plinth=0.0, step=4.05, pier=0.825, anchor="hi", gate=None, doors=()):
    """Granite ground storey: piers every 4.05 m, full-height shop windows with transom at +3.47 (122.77 = Maz.19 band)."""
    F.rect(s_lo, s_hi, z_g, 4.80, fill=G, stroke="none")
    n = int(round((s_hi - s_lo) / step + 1e-6))
    for j in range(n):
        a, b = (s_hi - (j + 1) * step, s_hi - j * step) if anchor == "hi" else (s_lo + j * step, s_lo + (j + 1) * step)
        a0, b0 = max(a + pier / 2, s_lo), min(b - pier / 2, s_hi)
        if gate and a >= gate[0] - 0.01 and b <= gate[1] + 0.01:
            continue
        zb = z_g + plinth
        window(F, a0, b0 - a0, zb, 4.45 - zb, reveal=0.35, transom=3.47 - zb, mull=False)
    if gate:
        F.rect(gate[0] + pier / 2 * 0, gate[1], z_g, 4.45, fill=REC, stroke=INK, sw=0.08)
        for q in range(1, 14):
            x = gate[0] + (gate[1] - gate[0]) * q / 14
            F.vline(x, z_g + 0.1, 3.9, stroke="#b8b0a4", sw=0.05)
        F.hline(gate[0], gate[1], 3.9, stroke="#b8b0a4", sw=0.08)
    for (a, b, h, lab) in doors:
        F.rect(a, b, z_g, z_g + h, fill=ME, stroke=INK, sw=0.07)
        for q in range(1, int(h / 0.3)):
            F.hline(a + 0.05, b - 0.05, z_g + q * 0.3, stroke="#6b645e", sw=0.03)
    # kordon 124,10 (granit 0,35 m) and pier joints
    F.rect(s_lo, s_hi, 4.45, 4.80, fill=G, stroke=INK, sw=0.09)
    F.rect(s_lo, s_hi, 4.30, 4.45, fill=INK, op=0.18)


def gzyms(F, s_lo, s_hi):
    F.rect(s_lo, s_hi, 19.88, 20.15, fill=INK, op=0.22)      # cast shadow of 0.30 m projection
    F.rect(s_lo, s_hi, 20.15, 20.85, fill=G, stroke=INK, sw=0.12)
    F.hline(s_lo, s_hi, 20.78, stroke=ME, sw=0.08)


def wing_west():
    pts = M_PTS[3:34]                       # (68.33,66.2) → nose R3.5 → (48.84, 9.68)
    F = Face(pts, -1.0, 20.85, "M-W", fill=G)
    L = F.L
    segs = [("M1", 12.15, 0.0), ("M2", 16.2, 0.08), ("M3", 16.2, 0.15), ("M4", 12.15, 0.08)]
    hi = L
    for name, ln, rel in segs:
        kamienica_upper(F, hi - ln, hi, C[name], rel)
        hi -= ln
    naroze_hi = hi
    kamienica_upper(F, 0.35, naroze_hi, C["M4"], 0.08)
    z_g = -0.85
    gate = (L - 12.15 - 4.05, L - 12.15)
    cokol(F, 0, L, z_g, plinth=0.0, gate=gate)
    F.rect(L - 12.15, L, z_g, z_g + 0.70, fill=G, stroke=INK, sw=0.07)       # cokół pełny 0,70 (M1, chodnik 118,60)
    hi = L
    for name, ln, rel in segs[:-1]:
        hi -= ln
        F.rect(hi - 0.10, hi + 0.10, 4.80, 20.15, fill=ME, stroke="none")     # fuga 0,20 m między posesjami
    F.rect(naroze_hi - 0.10, naroze_hi + 0.10, 4.80, 20.15, fill=ME, stroke="none")
    gzyms(F, 0, L)
    return F


def wing_east():
    F1 = Face(M_PTS[34:36], -1.0, 20.85, "M-E", fill=G)
    kamienica_upper(F1, 0.0, F1.L, C["M3"], 0.0, anchor="lo")
    cokol(F1, 0, F1.L, -0.6, anchor="lo")
    gzyms(F1, 0, F1.L)
    F2 = Face(M_PTS[35:37], -1.0, 20.85, "M-Es", fill=G)
    kamienica_upper(F2, 0.0, F2.L, C["M3"], 0.0, anchor="lo")
    cokol(F2, 0, F2.L, -0.4, anchor="lo")
    gzyms(F2, 0, F2.L)
    return [F1, F2]


def segment_faces():
    p = S_PTS
    E = Face([p[1], p[2]], -1.0, 20.85, "S-E", fill=G)
    L = E.L
    m = (L - 5 * 2.025) / 2
    kamienica_upper(E, m, L - m, C["SEG"], 0.0, anchor="lo")
    E.rect(0, m, 4.8, 20.15, fill=C["SEG"]); E.rect(L - m, L, 4.8, 20.15, fill=C["SEG"])
    zg = -0.25
    E.rect(0, L, zg, 4.45, fill=G)
    # weryfikacja K-2 / I-1: rampa jednopasowa 3,5 m przy ścianie pn. segmentu → brama 4,0 m na v −0,4…−4,4 (s = L−4,4 … L−0,4),
    # próg w poziomie chodnika 119,10 + zapora samoczynna; drzwi trafo / rozdzielni / odpadów w części pd. (pełna ściana pd.)
    g0, g1 = L - 4.4, L - 0.4
    E.rect(g0, g1, zg, zg + 4.0, fill=ME, stroke=INK, sw=0.08)
    for q in range(1, 13):
        E.hline(g0 + 0.05, g1 - 0.05, zg + q * 0.3, stroke="#6b645e", sw=0.03)
    doors = [(0.75, 1.95), (2.55, 3.55), (4.15, 5.15)]          # trafo (1,2) · rozdzielnia nn (1,0) · odpady (1,0)
    for a, b in doors:
        E.rect(a, b, zg, zg + 2.4, fill=ME, stroke=INK, sw=0.07)
        for q in range(1, 8):
            E.hline(a + 0.05, b - 0.05, zg + q * 0.3, stroke="#6b645e", sw=0.03)
    for a in [0.75, 1.95, 2.55, 3.55, 4.15, 5.15, g0, g1]:
        E.vline(a, zg, 4.45, stroke=INK, sw=0.08)
    E.rect(0, L, 4.45, 4.80, fill=G, stroke=INK, sw=0.09)
    gzyms(E, 0, L)
    Wf = Face([p[3], p[0]], -1.0, 20.85, "S-W", fill=G)
    m = (Wf.L - 3 * 2.025) / 2
    kamienica_upper(Wf, m, Wf.L - m, C["SEG"], 0.0, anchor="lo")
    Wf.rect(0, m, 4.8, 20.15, fill=C["SEG"]); Wf.rect(Wf.L - m, Wf.L, 4.8, 20.15, fill=C["SEG"])
    cokol(Wf, m, Wf.L - m, -0.35, anchor="lo")
    gzyms(Wf, 0, Wf.L)
    Sf = Face([p[0], p[1]], -1.0, 20.85, "S-S", fill=C["SEG"])                # ściana pełna: relief ceramiczny + pnącza
    for q in range(int(Sf.L / 0.45)):
        Sf.vline(q * 0.45 + 0.2, 4.8, 19.9, stroke="#c9b49c", sw=0.05)
    Sf.rect(0, Sf.L, -1.0, 4.8, fill=G, stroke=INK, sw=0.08)
    import random
    rnd = random.Random(7)
    for q in range(13):                      # pnącza (winobluszcz) na linkach co 1,45 m
        s = 0.8 + q * 1.45
        h = 9.0 + 8.0 * abs(math.sin(q * 1.3 + 0.4))
        Sf.vline(s, 0.6, min(19.4, h), stroke="#6b7a55", sw=0.06)
        for _ in range(int(h * 7)):
            zz = rnd.uniform(0.6, min(19.4, h)); taper = 1.0 - (zz / (h + 2.0)) * 0.6
            Sf.circle(s + rnd.gauss(0, 0.55 * taper), zz, rnd.uniform(0.18, 0.42) * taper,
                      fill=rnd.choice(("#6f8456", "#7f9462", "#5f7448", "#8c9d6c")), op=0.55)
    gzyms(Sf, 0, Sf.L)
    return [E, Wf, Sf]


# ---------------------------------------------------------------- tower: "wielki porządek"
def tower_bays(F, piers, crown, podcien=None, entries=(), louvres=None, zg=-0.2, kordon=True):
    """piers: sorted list of (s0, s1). Bays between consecutive piers get windows."""
    F.rect(0, F.L, zg, 36.2, fill=ME, stroke="none")
    for (a0, a1), (b0, b1) in zip(piers[:-1], piers[1:]):
        a, b = a1, b0
        if b - a < 0.3:
            continue
        w = min(1.65, b - a)
        c0 = (a + b) / 2 - w / 2
        # ground floor
        in_pod = podcien and a >= podcien[0] - 0.01 and b <= podcien[1] + 0.01
        if in_pod:
            F.rect(a, b, zg, 4.8, fill=REC, op=0.92)
            F.rect(a + 0.15, b - 0.15, zg, 3.9, fill=GLD, stroke="#5d646b", sw=0.05)
        else:
            window(F, a + 0.08, b - a - 0.16, zg, 4.40 - zg, reveal=0.6, transom=3.4 - zg)
        for (e0, e1, lab) in entries:
            if e0 < b and e1 > a:
                F.rect(max(a, e0), min(b, e1), zg, 3.2, fill=REC, op=0.9)
                F.rect(max(a, e0) + 0.2, min(b, e1) - 0.2, zg, 2.9, fill="#c9a96b", op=0.55, stroke=INK, sw=0.05)
        # floors 1–5
        for f in ("1", "2", "3", "4", "5"):
            zf = LEV[f]
            sill = 0.9
            if f == "5" and kordon:
                F.rect(a, b, 19.80, 20.85, fill=G, stroke=INK, sw=0.07)
                sill = 1.05
            if louvres and f == "1" and louvres[0] <= a and b <= louvres[1]:
                F.rect(c0, c0 + w, zf + 0.3, zf + 3.35, fill="#5e5853", stroke=INK, sw=0.05)
                for q in range(1, 18):
                    F.hline(c0, c0 + w, zf + 0.3 + q * 0.17, stroke="#2c2926", sw=0.03)
                continue
            window(F, c0, w, zf + sill, 2.45, reveal=0.6)
        # floor 6 — "kondygnacja cienia"
        F.rect(a, b, 23.55, 27.30, fill=REC)
        F.rect(a + 0.1, b - 0.1, 23.85, 26.95, fill=GLD, stroke="#5d646b", sw=0.04)
        F.rect(a, b, 26.75, 27.30, fill=INK, op=0.35)
        # crown S
        if crown == "hall":
            F.rect(a, b, 27.3, 36.2, fill=G)
            window(F, c0, w, 28.0, 5.0, reveal=0.6, transom=2.5)
        elif crown == "komisje_lamele":
            F.rect(a, b, 27.3, 36.2, fill=G)
            window(F, c0, w, 28.0, 4.2, reveal=0.6, transom=2.6)
            F.rect(a, b, 32.9, 35.8, fill=GLD)
            q = a + 0.06
            while q < b - 0.2:
                F.rect(q, q + 0.25, 32.9, 35.8, fill=C["LUK"], stroke="#b9ad9c", sw=0.03)
                q += 0.42
        else:
            F.rect(a, b, 27.3, 36.2, fill=G)
            window(F, c0, w, 28.0, 4.2, reveal=0.6, transom=2.6)
    for (p0, p1) in piers:
        F.rect(p0, p1, zg, 36.2, fill=G, stroke=INK, sw=0.1)
        F.rect(p1, min(F.L, p1 + 0.22), 4.8 if not podcien else zg, 36.2, fill=INK, op=0.13)   # pier cast shadow
    F.rect(0, F.L, 36.2, 37.2, fill=G, stroke=INK, sw=0.12)
    F.rect(0, F.L, 37.05, 37.2, fill=ME, stroke="none")


def pier_grid(L, start_pairs, massive=()):
    """start_pairs: list of pier centres; massive: list of (s0,s1) heavy piers (override overlaps)."""
    pr = [(c - 0.525, c + 0.525) for c in start_pairs]
    out = []
    for p in pr:
        if any(p[1] > m0 - 0.05 and p[0] < m1 + 0.05 for m0, m1 in massive):
            continue
        out.append((max(0, p[0]), min(L, p[1])))
    out += list(massive)
    return sorted(out)


def tower_faces():
    p = W_PTS
    i_arc0, i_arc1 = 2, 26          # (109.75,65.48) … (92.83,75.77)
    # East (Wybrzeże): s from south (113.47,50.23) to arc start
    E = Face([p[1], p[2]], -1.0, 37.2, "W-E", fill=G)
    piersE = pier_grid(E.L, [0.525] + [0.525 + 2.7 * j for j in range(1, 5)], massive=[(E.L - 2.2, E.L)])
    tower_bays(E, piersE, "hall", entries=[(1.40, 6.80, "Wejście Obywatelskie")], zg=-0.15)   # v 1,40–6,80 (wnęka 1,5 m przy trzonie B)
    # Arc R14
    A = Face(p[i_arc0:i_arc1 + 1], -1.0, 37.2, "W-luk", fill=G)
    A.rect(0, A.L, -0.15, 4.8, fill=REC, op=0.95)
    A.rect(0, A.L, -0.15, 3.9, fill=GLD, op=0.9)
    for kk in range(1, 6):
        s = 14.0 * math.radians(15 * kk)
        A.rect(s - 0.3, s + 0.3, -0.15, 4.8, fill=G, stroke=INK, sw=0.08)
    for f in ("1", "2", "3", "4", "5"):
        zf = LEV[f]
        A.rect(0, A.L, zf, zf + 1.30, fill=(G if f == "1" else C["LUK"]), stroke=INK, sw=0.08)   # nad podcieniem: granitowe nadproże z napisem
        A.rect(0, A.L, zf + 1.30, zf + 3.75, fill=GL, stroke=INK, sw=0.06)
        A.rect(0, A.L, zf + 3.25, zf + 3.75, fill=INK, op=0.25)
        q = 1.35
        while q < A.L:
            A.vline(q, zf + 1.30, zf + 3.75, stroke=ME, sw=0.05)
            q += 1.35
    A.rect(0, A.L, 23.55, 27.30, fill=REC)
    A.rect(0, A.L, 27.30, 36.2, fill="#5a6570")
    q = 0.2
    while q < A.L - 0.2:
        A.rect(q, q + 0.25, 27.30, 36.2, fill=C["LUK"], stroke="#a99d8c", sw=0.03)
        q += 0.90
    A.rect(0, A.L, 36.2, 37.2, fill=G, stroke=INK, sw=0.12)
    A.rect(0, A.L, 37.05, 37.2, fill=ME, stroke="none")
    # North (Plac Mostowy): s from arc end (east) to NW corner; u = 26.0 − s
    N = Face([p[i_arc1], p[27]], -1.0, 37.2, "W-N", fill=G)
    Lu = N.L
    centres = [Lu - (0.525 + 2.7 * j) for j in range(0, 9)]
    piersN = pier_grid(Lu, centres, massive=[(0.0, 1.7)])
    tower_bays(N, piersN, "hall", podcien=(0.0, 12.5), entries=[(2.0, 5.0, "wejście od skweru")], zg=-0.1)
    # West (above the wing + free 3.5 m at the north end): s from NW corner (north) to SW corner
    Wf = Face([p[27], p[0]], -1.0, 37.2, "W-W", fill=G)
    piersW = pier_grid(Wf.L, [0.525 + 2.7 * j for j in range(0, 11)] + [Wf.L - 0.525])
    tower_bays(Wf, piersW, "komisje", zg=-0.1)
    # South (garden): s = u from SW (74.61,40.76) to SE (113.47,50.23)
    Sf = Face([p[0], p[1]], -1.0, 37.2, "W-S", fill=G)
    piersS = pier_grid(Sf.L, [0.525 + 2.7 * j for j in range(0, 15)], massive=[(37.8, 40.0)])   # filar narożny SE 2,2 m
    tower_bays(Sf, piersS, "komisje_lamele", entries=[(8.6, 11.4, "wejście ogrodowe"), (3.0, 4.6, "rowerownia")],
               louvres=(2.0, 12.0), zg=-0.35)
    return [E, A, N, Wf, Sf]


# ---------------------------------------------------------------- neighbours
def merge_collinear(pts, tol_deg=12.0, min_len=0.6):
    """Drop vertices where the outline turns by < tol (survey outlines are split into many short edges)."""
    changed = True
    pts = list(pts)
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            h1 = math.atan2(b[1] - a[1], b[0] - a[0]); h2 = math.atan2(c[1] - b[1], c[0] - b[0])
            turn = abs(math.degrees((h2 - h1 + math.pi) % (2 * math.pi) - math.pi))
            if turn < tol_deg or math.dist(a, b) < min_len * 0.3:
                pts.pop(i); changed = True
                break
    return pts


def neighbour_faces(names):
    faces = []
    for b in S["budynki"]["items"]:
        if b.get("nazwa") not in names or b.get("czesciowy_przyciety_ramka"):
            continue
        pg = poly_of(b)
        pts = merge_collinear(ccw(list(pg.exterior.coords)[:-1]))
        zt = b.get("gora_szac_H", Z0 + b.get("wysokosc_szac_m", 20)) - Z0
        zg = b["teren_wokol_H"]["min"] - Z0
        n = len(pts)
        for i in range(n):
            a, c = pts[i], pts[(i + 1) % n]
            L = math.dist(a, c)
            if L < 0.4:
                continue
            F = Face([a, c], zg, zt, b["nazwa"], fill=NB_F, outline=False)
            F.rect(0, L, zg, zt, fill="none", stroke=NB_S, sw=0.12)
            nax = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))
            nrm = (math.degrees(math.atan2(c[1] - a[1], -(c[0] - a[0]))) + 360) % 360
            gable = L < 8 or any(abs(((nrm - g + 180) % 360) - 180) < 8 for g in ())
            if b["nazwa"] == "Mazowiecka 19" and abs(L - 15.78) < 0.3:
                gable = True
            if b["nazwa"].startswith("Wybrzeze J. Slowackiego 5") and abs(L - 16.26) < 0.4:
                gable = True
            if not gable:
                nax_ = int(L / 2.3)
                m = (L - nax_ * 2.3) / 2
                floors = [zg + 0.8 + 3.75 * j for j in range(int((zt - zg - 2.5) / 3.75))]
                for j in range(nax_):
                    s0 = m + j * 2.3 + 0.64
                    for zf in floors:
                        F.rect(s0, s0 + 1.02, zf + 0.9, zf + 2.9 if zf > zg + 1 else zf + 2.7, fill=NB_W, stroke=NB_S, sw=0.05)
                F.hline(0, L, zt - 2.4, stroke=NB_S, sw=0.08)
                F.hline(0, L, zg + 4.2, stroke=NB_S, sw=0.06)
            faces.append(F)
    return faces


# ---------------------------------------------------------------- drawing
def ground_profile(view_az, pts):
    pr = sorted((u_of(view_az, e, n), z - Z0) for e, n, z in pts)
    return pr


def draw_cut(svg, view_az, cut, P):
    """Section profile where the vertical plane p·d = cut intersects the proposal volumes: outline + slabs."""
    from shapely.geometry import Polygon, LineString
    from umwd.facade_elev import frame
    d, r = frame(view_az)
    c0 = (d[0] * cut, d[1] * cut)
    line = LineString([(c0[0] - r[0] * 400, c0[1] - r[1] * 400), (c0[0] + r[0] * 400, c0[1] + r[1] * 400)])
    vols = [(W_PTS, 37.2, 36.2, [4.8, 8.55, 12.3, 16.05, 19.8, 23.55, 27.3]), (M_PTS, 20.85, 19.8, FLOORS_W), (S_PTS, 20.85, 19.5, FLOORS_W)]
    for pts, top, roof, floors in vols:
        x = Polygon(pts).buffer(0).intersection(line)
        segs = [x] if x.geom_type == "LineString" else list(getattr(x, "geoms", []))
        for sg in segs:
            if sg.is_empty or sg.length < 0.3:
                continue
            us = [u_of(view_az, *c) for c in sg.coords]
            ua, ub = min(us), max(us)
            svg.poly([P(ua, -0.15), P(ub, -0.15), P(ub, top), P(ua, top)], fill="#f3f1ed", stroke="none")
            hp = svg.hatch("ciecie", spacing=1.6, angle=45, stroke="#cfc9c0", sw=0.08)
            svg.poly([P(ua, -0.15), P(ub, -0.15), P(ub, top), P(ua, top)], fill=hp, stroke="none")
            for zf in floors + [roof]:
                svg.poly([P(ua, zf - 0.28), P(ub, zf - 0.28), P(ub, zf), P(ua, zf)], fill=INK, stroke="none")
            svg.poly([P(ua, -0.15), P(ub, -0.15), P(ub, top), P(ua, top)], fill="none", stroke=INK, sw=0.5)
            svg.poly([P(ua, -3.75), P(ub, -3.75), P(ub, -0.15), P(ua, -0.15)], fill=INK, stroke="none", extra='fill-opacity="0.85"')


def elevation(name, title, sub, view_az, faces, ground_pts, mpzp, levels, u_pad=6.0, out_w=None, cut=None, debug=False):
    pad_l, pad_r, pad_t, pad_b = 34, 12, 22, 26
    from umwd.facade_elev import frame
    dd, _ = frame(view_az)
    us = []
    for F in faces:
        for (x, y) in F.pts:
            if cut is None or x * dd[0] + y * dd[1] >= cut - 0.5:
                us.append(u_of(view_az, x, y))
    u0, u1 = min(us) - u_pad, max(us) + u_pad
    W = pad_l + (u1 - u0) * k + pad_r
    H = pad_t + 48 * k + pad_b
    svg = Svg(W, H)
    oy = pad_t + 46 * k

    def P(u, z):
        return (pad_l + (u - u0) * k, oy - z * k)

    # sky-light background band (very subtle) for legibility of the silhouette
    draw_faces(svg, faces, view_az, P, cut=cut, debug=debug)
    if cut is not None:
        draw_cut(svg, view_az, cut, P)
    # ground
    gp = ground_profile(view_az, ground_pts)
    gp = [(u0, gp[0][1])] + gp + [(u1, gp[-1][1])]
    poly = [P(u, z) for u, z in gp] + [P(u1, -4.0), P(u0, -4.0)]
    svg.poly(poly, fill="#ffffff", stroke="none")
    hp = svg.hatch("grunt", spacing=0.9, angle=45, stroke="#9a948c", sw=0.07)
    band = [P(u, z) for u, z in gp] + [P(u, z - 0.9) for u, z in reversed(gp)]
    svg.poly(band, fill=hp, stroke="none")
    svg.poly([P(u, z) for u, z in gp], fill="none", stroke=INK, sw=0.45, close=False)
    # MPZP limits
    for (ua, ub, z, lab, side) in mpzp:
        a, b = P(ua, z), P(ub, z)
        svg.line(a, b, stroke="#a8483a", sw=0.22, dash="2.2,1.0")
        if side == "r":
            svg.text((b[0] + 1.2, b[1] + 0.8), lab, size=1.9, fill="#a8483a")
        else:
            svg.text((a[0] - 1.2, a[1] + 0.8), lab, size=1.9, fill="#a8483a", anchor="end")
    # level marks
    x = pad_l - 8
    for z, lab in levels:
        y = P(0, z)[1]
        svg.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
        svg.line((x - 2.2, y), (pad_l - 2, y), stroke=INK, sw=0.12)
        svg.text((x - 2.6, y - 0.4), lab, size=1.85, anchor="end")
    # titles
    svg.text((pad_l, 9), title, size=4.2, weight=600)
    svg.text((pad_l, 14.5), sub, size=2.3, fill="#4d4842")
    # scale bar 0–10 m
    sx, sy = pad_l, H - 9
    for i in range(5):
        svg.poly([(sx + i * 2 * k, sy), (sx + (i + 1) * 2 * k, sy), (sx + (i + 1) * 2 * k, sy + 1.2), (sx + i * 2 * k, sy + 1.2)],
                 fill=INK if i % 2 == 0 else "#ffffff", stroke=INK, sw=0.12)
    for i, t in enumerate(("0", "2", "4", "6", "8", "10 m")):
        svg.text((sx + i * 2 * k, sy + 4.0), t, size=1.8, anchor="middle")
    svg.text((sx + 10 * k + 10, sy + 1.2), "1:200", size=2.2, weight=600)
    out = ROOT / "build" / "rysunki" / f"elewacja_{name}_1-200.svg"
    out.write_text(svg.render(), encoding="utf-8")
    return svg, out


def main():
    TW = tower_faces()
    WG = [wing_west()] + wing_east()
    SG = segment_faces()
    ours = TW + WG + SG
    A_min, A_max = 154.44 - Z0, 163.88 - Z0       # strefa A: 35 m nad najwyższym terenem w A, 45 m nad najniższym
    O_min, O_max = 137.41 - Z0, 143.33 - Z0       # poza A: 18 / 25 m
    LEVELS = [(37.20, "+37,20 attyka (156,50)"), (36.20, "+36,20"), (27.30, "+27,30 sala Sejmiku"), (23.55, "+23,55"),
              (20.85, "+20,85 gzyms (140,15)"), (19.80, "+19,80"), (4.80, "+4,80"), (0.0, "±0,00 = 119,30 m n.p.m.")]
    res = []

    def spans(az, near_out=None):
        tw = [u_of(az, *p) for p in W_PTS]
        ot = [u_of(az, *p) for p in list(S_PTS) + list(M_PTS)]
        t0, t1 = min(tw), max(tw); o0, o1 = min(ot), max(ot)
        out = []
        if o0 < t0 - 0.5:
            out.append((o0 - 4, t0, "l"))
        if o1 > t1 + 0.5:
            out.append((t1, o1 + 4, "r"))
        lines = [(t0, t1, A_min, "MPZP min. 35,0 m (strefa A)", "r"), (t0, t1, A_max, "MPZP maks. 45,0 m (strefa A)", "r")]
        for (x0, x1, side) in out:
            lines += [(x0, x1, O_min, "18,0 m (poza A)", side), (x0, x1, O_max, "25,0 m (poza A)", side)]
        return lines

    az = 256.3
    res.append(elevation("E", "ELEWACJA WSCHODNIA", "od Wybrzeża J. Słowackiego i Odry · z kamienicami Wybrzeże J. Słowackiego 5 i 6", az,
                         ours + neighbour_faces({"Wybrzeze J. Slowackiego 5", "Wybrzeze J. Slowackiego 6"}),
                         [(118.3, 10.0, 118.85), (118.3, 28.2, 119.0), (115.98, 39.93, 118.91), (113.48, 50.18, 119.18), (109.75, 65.48, 119.44), (104.0, 76.0, 119.40)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 166.3
    res.append(elevation("N", "ELEWACJA PÓŁNOCNA", "od Placu Mostowego i przyczółka Mostu Grunwaldzkiego", az, ours + neighbour_faces({"Wybrzeze J. Slowackiego 5"}),
                         [(61.25, 66.05, 119.41), (67.57, 69.61, 119.41), (92.83, 75.77, 119.44), (109.75, 65.48, 119.44), (116.0, 40.0, 119.18), (118.5, 28.0, 119.0)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 102.4
    res.append(elevation("W", "ELEWACJA ZACHODNIA", "od ul. Mazowieckiej · z kamienicami Mazowiecka 19 i 17 (pierzeja)", az,
                         ours + neighbour_faces({"Mazowiecka 19", "Mazowiecka 17"}),
                         [(40.0, -25.0, 118.45), (44.64, -8.38, 118.51), (48.84, 9.68, 118.40), (61.25, 66.05, 119.41), (64.0, 72.0, 119.45)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 346.3
    res.append(elevation("S", "ELEWACJA POŁUDNIOWA", "od Ogrodu Województwa (w przekroju przez ogród, bez kamienic w pierwszym planie)", az, ours,
                         [(63.5, 6.49, 118.70), (74.61, 40.76, 118.95), (96.69, 38.81, 118.95), (113.47, 50.23, 119.0), (118.3, 40.0, 119.0)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 282.4
    res.append(elevation("Sd", "ELEWACJA SKRZYDŁA OD OGRODU", "elewacja wschodnia skrzydła w przekroju przez ogród · z oficyną kamienicy Mazowiecka 19", az,
                         ours + neighbour_faces({"Mazowiecka 19"}),
                         [(64.0, -8.0, 118.53), (63.5, 6.49, 118.70), (70.84, 39.84, 118.95), (74.0, 45.0, 118.95), (90.0, 46.0, 119.0)],
                         [], LEVELS, cut=-80.0, debug=DEBUG))
    # combined preview
    total_h = sum(s.h_mm for s, _ in res) + 10
    max_w = max(s.w_mm for s, _ in res)
    body = ""
    for s, _ in res:
        body += f'<div style="margin:0 0 4mm 0">{s.render()}</div>'
    html = ROOT / "docs" / "70_rysunki" / "podglady" / "elewacje_1-200.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{max_w+10:.0f}mm {total_h+10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{body}</body></html>', encoding="utf-8")
    print(f"{max_w + 10:.0f} {total_h + 10:.0f}")


if __name__ == "__main__":
    main()
