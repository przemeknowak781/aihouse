"""Weryfikacja geometrii i prawa miejscowego – BRAMA I LATARNIA (synteza 1.0).
Uruchomienie: /home/user/aihouse/.venv-render/bin/python -I weryfikacja_geometria.py umwd/model/site.json umwd/model/koncepcja.json
"""
import json, math, sys
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely.validation import explain_validity
from shapely import contains_xy
from scipy.interpolate import LinearNDInterpolator

S = json.load(open(sys.argv[1])); K = json.load(open(sys.argv[2]))
OI = Polygon(S['granice']['obszar_inwestycji']['pts']); A = Polygon(S['granice']['wydzielenie_A_mpzp']['pts'])
D102 = Polygon(S['granice']['dojazd_dz_10_2']['pts']); OGR = Polygon(S['granice']['ogrodki_przydomowe']['pts'])
B = {b['id']: b for b in K['bryly']}
W = Polygon(B['W']['obrys_ccw']); Mraw = Polygon(B['M']['obrys_ccw']); M = Mraw.buffer(0); Sg = Polygon(B['S']['obrys_ccw'])
P1 = Polygon(K['podziemie']['-1']['obrys_ccw']); P2 = Polygon(K['podziemie']['-2']['obrys_ccw'])
uv = lambda e, n: (0.97155*(e-74.606)+0.23684*(n-40.756), -0.23684*(e-74.606)+0.97155*(n-40.756))
print('== 1. Obrysy / A ==')
print('M valid:', Mraw.is_valid, explain_validity(Mraw))
for nm, g in [('W', W), ('M', M), ('S', Sg), ('-1', P1), ('-2', P2)]:
    print(f'{nm}: pole {g.area:.2f}; poza OI {g.difference(OI).area:.4f}; w A {g.intersection(A).area:.4f}; poza A {g.difference(A).area:.4f}; '
          f'min odl. do granicy OI {g.exterior.distance(OI.exterior):.3f}; do granicy A {g.exterior.distance(A.exterior):.3f}')
for p in S['granice']['wydzielenie_A_mpzp']['pts']:
    print('  narożnik A', p, '(u,v)=', tuple(round(x, 3) for x in uv(*p)))
# tabela M ze specyfikacji (4.1): łuk R3,5 krótszą drogą
c = (64.669, 65.301); p1 = (61.251, 66.053); p2 = (63.840, 68.701)
a0, a1 = math.atan2(p1[1]-c[1], p1[0]-c[0]), math.atan2(p2[1]-c[1], p2[0]-c[0])
arc = [(c[0]+3.5*math.cos(a0+(a1-a0)*i/48), c[1]+3.5*math.sin(a0+(a1-a0)*i/48)) for i in range(49)]
Mspec = Polygon([(48.842, 9.683)]+arc+[(67.494, 69.592), (74.557, 40.744), (70.839, 39.838), (63.498, 6.487)])
print(f'M wg tabeli 4.1: pole {Mspec.area:.2f}, CCW={Mspec.exterior.is_ccw}; M(JSON) {M.area:.2f}; różnica (wcięcie NE) {Mspec.difference(M).area:.2f}')
print('-1 do ogródków', round(P1.distance(OGR), 3), '; obwód -1', round(P1.length, 1))
for z in K['parter']['skrzydlo']:
    if 'en' in z:
        g = Polygon(z['en'])
        if g.intersection(W).area > 0.5:
            print('  strefa parteru skrzydła w wieży/A:', z['strefa'][:30], round(g.intersection(W).area, 1), 'm2')
# lamele korony R13,5 + 0,60
cW = (96.148, 62.167)
cut = LineString([(107.98, 73.93), (105.7, 73.0), (100.63, 77.92)])
print('łuk do ścięcia granicy: R14,0', round(Point(cW).buffer(14.0, 512).distance(cut), 3), '; R14,1', round(Point(cW).buffer(14.1, 512).distance(cut), 3))

print('== 2. Granice (krawędzie OI) ==')
for e in S['granice']['obszar_inwestycji']['krawedzie']:
    L_ = LineString([e['od'], e['do']])
    print(f"  kr.{e['i']:2d} dz.{e['sasiad_dzialka']:6s}: W {L_.distance(W):6.3f}  M {L_.distance(M):6.3f}  S {L_.distance(Sg):6.3f}")
print('  S – dz. 10/2 (poligon):', round(Sg.distance(D102), 3))

print('== 3. Wysokości MPZP (TIN z pikiet + linii nieciągłości; pas 2 m) ==')
T = S['teren']; pts = [(p[1], p[2], p[3]) for p in T['pikiety'] if p[4] == 1]
for l in T['linie_nieciaglosci']:
    pts += [(x, y, z) for (x, y), z in zip(l['pts'], l['z'])]
P = np.array(pts); f = LinearNDInterpolator(P[:, :2], P[:, 2])
def hz(g, s=0.25):
    x0, y0, x1, y1 = g.bounds; X, Y = np.meshgrid(np.arange(x0, x1+s, s), np.arange(y0, y1+s, s)); m = contains_xy(g, X, Y)
    H = f(X[m], Y[m]); H = H[~np.isnan(H)]; return float(H.min()), float(H.max())
G = S['teren']['siatka_NMT']; Hg = np.array([[np.nan if v is None else v for v in r] for r in G['H_wiersze_od_n0']])
ii, jj = np.where(~np.isnan(Hg)); ee = G['e0']+jj*G['krok_m']; nn = G['n0']+ii*G['krok_m']; mk = contains_xy(OI, ee, nn)
OImin, OImax = float(Hg[ii[mk], jj[mk]].min()), float(Hg[ii[mk], jj[mk]].max())
print(f'  OI (siatka NMT site.json): {OImin:.2f} / {OImax:.2f}')
tops = {'W': (155.50, 155.75, 156.50, 35, 45), 'M': (139.50, 139.70, 140.15, 18, 25), 'S': (139.10, 139.10, 140.15, 18, 25)}
for nm, g in [('W', W), ('M', M), ('S', Sg)]:
    lo, hi = hz(g.buffer(2.0)); a, b, att, mn, mx = tops[nm]
    print(f'  {nm}: teren {lo:.2f}/{hi:.2f}; najniższe pokrycie {a-hi:.2f} m (od max OI {a-OImax:.2f}; min {mn}); '
          f'najwyższe pokrycie {b-lo:.2f} (od min OI {b-OImin:.2f}; max {mx}); attyka {att-lo:.2f} (od min OI {att-OImin:.2f})')

print('== 4. § 13 – szczyt pn. WS 5 ==')
G0, G1 = np.array([101.93, 28.52]), np.array([118.16, 29.46]); Lg = np.linalg.norm(G1-G0); t = (G1-G0)/Lg; nv = np.array([-t[1], t[0]])
azn = math.degrees(math.atan2(nv[0], nv[1])) % 360
def wedge(V, az, half=30, R=80):
    return Polygon([tuple(V)]+[(V[0]+R*math.sin(math.radians(az-half+2*half*k/60)), V[1]+R*math.cos(math.radians(az-half+2*half*k/60))) for k in range(61)])
def worst(ob, wall=0.55, tr=None):
    tr = tr or (0.55, Lg-0.55); best = (1e9, None)
    for s in np.arange(tr[0], tr[1]+1e-9, 0.05):
        V = G0+s*t-wall*nv; g = ob.intersection(wedge(V, azn))
        if not g.is_empty and Point(V).distance(g) < best[0]: best = (Point(V).distance(g), tuple(np.round(V, 3)))
    return best
print('  normalna', round(azn, 2), '; dł. szczytu', round(Lg, 2))
for nm, ob in [('S', Sg), ('W', W), ('M', M)]:
    print(f'  {nm}: min odl. w sektorze (całe lico wewn.) =', worst(ob))
sr = float(np.dot(np.array([110.5, 29.0])-G0, t))
print('  okno pokoju lok. 6/6A: S', worst(Sg, tr=(sr, sr))[0], '; W', worst(W, tr=(sr, sr))[0])
for wall in (0.40, 0.70):
    print(f'  wrażliwość: mur {wall} m → S {worst(Sg, wall)[0]:.3f}, W {worst(W, wall)[0]:.3f}')
for Hb in (124.0, 120.0, 119.2):
    print(f'  wymagane dla attyki 140,15 przy H od {Hb}: {(140.15-Hb)/2:.3f} m')

print('== 5. Segment – pas pn. i rampa ==')
d = np.array([115.979-96.694, 39.93-38.813]); Ld = np.linalg.norm(d); nr = np.array([-d[1], d[0]])/Ld
def band(w):
    p0 = np.array([96.694, 38.813])-5*d/Ld; q0 = np.array([115.979, 39.93])+5*d/Ld
    return Polygon([tuple(p0), tuple(q0), tuple(q0+w*nr), tuple(p0+w*nr)])
for lane in (6.5, 3.5):
    r = Sg.difference(band(0.30+lane+0.20)); print(f'  rampa {lane} m: pas pn. brutto {r.area:.1f}, netto ~{r.buffer(-0.3, join_style=2).area:.1f} m2 (program: 21+17+11+7 = 56)')
wl = LineString([tuple(np.array([96.694, 38.813])-50*d/Ld), tuple(np.array([115.979, 39.93])+50*d/Ld)])
print('  szerokość segmentu prostopadle do ściany pd.: wsch.', round(wl.distance(Point(113.48, 50.181)), 2), 'zach.', round(wl.distance(Point(95.02, 45.681)), 2))
print('  NMT chodnik przed bramą ~119,09 ; teren dziedzińca przy wyjściu rampy ~118,93')
Lin = Ld-0.65/math.sin(math.radians(79.6))
for sill in (0.30, -0.20):
    fl = sill-(0.09*3.0+0.18*(Lin-3.0)); print(f'  próg {sill:+.2f}: posadzka rampy przy ścianie zach. {fl:.2f}; wierzch stropu (2,30 + 0,28) {fl+2.58:+.2f} = {119.30+fl+2.58:.2f} m n.p.m.')
fl = 0.30-(0.09*3.0+0.18*(Lin-0.51/0.12-1.0-3.0)); print(f'  próg +0,30 osiągnięty wewnątrz (0,51 m na 12 % + 1 m płaskie): strop {fl+2.58:+.2f} = {119.30+fl+2.58:.2f} m n.p.m.')

print('== 6. Drzewa (M.02) – odl. pnia od ściany -1 ==')
rm = set(K['zagospodarowanie']['drzewa_usuniete'])
for dd in S['zielen']['drzewa']:
    p = Point(dd['e'], dd['n'])
    if OI.contains(p) and dd['nr'] not in rm and P1.distance(p) < 6:
        print(f"  {dd['nr']}: {P1.distance(p):.2f} m (ogródki={dd['w_ogrodkach']})")
M06 = {60: (73.2, 30.9, 6.2, 'Z2'), 58: (77.2, 30.7, 4.2, 'Z1'), 67: (68.6, 26.0, 3.1, 'Z1'), 78: (68.6, 15.6, 3.1, 'Z1')}
for k_, (e_, n_, z_, r_) in M06.items():
    dist = P1.distance(Point(e_, n_)); print(f'  M.06 nr {k_} ({r_}, strefa {z_} m): ściana -1 w odl. {dist:.2f} m → wejście w strefę {max(0, z_-dist):.2f} m')
