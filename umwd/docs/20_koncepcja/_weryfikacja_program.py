# -*- coding: utf-8 -*-
"""Weryfikacja PROGRAMU i FUNKCJI koncepcji „Brama i Latarnia” (raport: weryfikacja_program.md).

Uruchomienie:  python3 docs/20_koncepcja/_weryfikacja_program.py   (z katalogu umwd/)
Dane: model/koncepcja.json, docs/20_program/program.yaml. Skrypt niczego nie zapisuje.
"""
import json, math, yaml
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union

K = json.load(open('model/koncepcja.json'))
P = yaml.safe_load(open('docs/20_program/program.yaml'))

def hr(t):
    print('\n' + '=' * 100 + '\n' + t + '\n' + '=' * 100)

# --------------------------------------------------------------------------------------------
# 0. Układy
# --------------------------------------------------------------------------------------------
E0, N0 = 74.606, 40.756
cu, su = 0.97155, 0.23684
def en2uv(e, n):
    de, dn = e - E0, n - N0
    return (cu * de + su * dn, -su * de + cu * dn)
def uv2en(u, v):
    return (E0 + cu * u - su * v, N0 + su * u + cu * v)

W_en = Polygon(K['bryly'][0]['obrys_ccw'])
W_uv = Polygon([en2uv(*p) for p in K['bryly'][0]['obrys_ccw']])
M_en = Polygon(K['bryly'][1]['obrys_ccw'])
S_en = Polygon(K['bryly'][2]['obrys_ccw'])

hr('0. Bryły – kontrola danych JSON')
print(f'Wieża: pole {W_en.area:8.2f} (JSON 1145,83)   valid={W_en.is_valid}')
print(f'Skrzydło: pole {M_en.area:8.2f} (JSON/MD 847,00)  valid={M_en.is_valid}  (obrys ma kolec 68,766/64,397→68,372/63,74→68,766/64,397)')
print(f'Segment: pole {S_en.area:8.2f} (JSON 167,40)')
# narożnik NW skrzydła wg MD: (63,840; 68,701) → (67,494; 69,592); w JSON go nie ma
print('MD: skrzydło (63,840;68,701)→(67,494;69,592)→(74,557;40,744); JSON: łuk do (68,326;66,196) → wcięcie przy narożu NW wieży:')
gap = Polygon([(63.84, 68.701), (67.494, 69.592), (68.326, 66.196)]).difference(M_en).difference(W_en)
print(f'   pole „wcięcia” między skrzydłem z JSON a narożem NW wieży ≈ {gap.area:.1f} m²')

# --------------------------------------------------------------------------------------------
# 1. Kondygnacja Sejmiku – pomieszczenia
# --------------------------------------------------------------------------------------------
hr('1. Kondygnacja Sejmiku – bilans i kontrola geometrii')
S = K['kondygnacja_sejmiku']['pomieszczenia']
R = {k: Polygon(v['obrys_uv'][0]).buffer(0) for k, v in S.items()}
inner = W_uv.buffer(-0.5, join_style=2)
print(f'Wnętrze wieży (lico wewn. 0,50 m): {inner.area:.1f} m² (spec. 1 080,1); ściany zewn. {W_uv.area-inner.area:.1f} (spec. 65,7)')
tot = 0
for k, p in R.items():
    tot += p.area
    out = p.difference(inner).area
    if out > 0.05:
        print(f'  ! {k} wystaje poza lico wewn. o {out:.2f} m²')
ov = []
keys = list(R)
for i in range(len(keys)):
    for j in range(i + 1, len(keys)):
        a = R[keys[i]].intersection(R[keys[j]]).area
        if a > 0.01: ov.append((keys[i], keys[j], round(a, 2)))
print('Nakładania pomieszczeń:', ov or 'brak')
walls_int = inner.area - unary_union(list(R.values())).area
print(f'Suma pomieszczeń + trzony + KUL: {tot:.1f} m²; ściany wewnętrzne (reszta) {walls_int:.1f} m² = {walls_int/W_uv.area*100:.1f} % PC; '
      f'ściany razem {(walls_int + W_uv.area-inner.area):.1f} m² = {(walls_int + W_uv.area-inner.area)/W_uv.area*100:.1f} % PC')

# długość ścian wewnętrznych (osie) – połowa sumy obwodów kawałków minus część na licu zewn.
L_all = sum(p.length for p in R.values())
L_ext = sum(p.boundary.intersection(inner.boundary.buffer(0.02)).length for p in R.values())
L_int = (L_all - L_ext) / 2
print(f'Długość ścian wewnętrznych ≈ {L_int:.0f} m → średnia grubość w spec. = {walls_int/L_int:.3f} m')
# realistyczne grubości: ściany sali (nośna pd. pod ruszt 19,5 m + akustyka) 0,30; ściany komisji/klubów/korytarzy (Rw≥50 dB, EI 30) 0,20; reszta 0,12–0,15
sala_walls = R['SWD.01'].boundary.difference(inner.boundary.buffer(0.3)).length
real = sala_walls * 0.30 + (L_int - sala_walls) * 0.20
print(f'   z tego ściany sali (bez łuku) ≈ {sala_walls:.0f} m; przy 0,30 (sala) / 0,20 (pozostałe): {real:.0f} m² '
      f'→ brakuje ≈ {real - walls_int:.0f} m² (ściany razem {(real + W_uv.area-inner.area)/W_uv.area*100:.1f} % PC)')

# --- dostęp do komunikacji
hr('1a. Dostęp pomieszczeń do komunikacji (KUL, SWD.02) – styk ≥ 0,9 m przez ścianę ≤ 0,20 m')
circ = unary_union([R['KUL'], R['SWD.02']])
for k, p in R.items():
    if k in ('KUL', 'SWD.02'): continue
    L = p.buffer(0.2, join_style=2).boundary.intersection(circ.buffer(0.001)).length
    shared_rooms = [o for o in R if o != k and o not in ('KUL', 'SWD.02') and p.buffer(0.2, join_style=2).intersection(R[o]).area > 0.05]
    flag = 'OK' if L >= 0.9 else 'BRAK DOSTĘPU Z KOMUNIKACJI'
    print(f'  {k:8s} {S[k]["nazwa"][:46]:46s} styk z komunikacją {L:5.2f} m  → {flag}; sąsiedzi: {",".join(shared_rooms)}')

# --- hol
hr('1b. Hol reprezentacyjny SWD.02 – z czego się składa')
hol = R['SWD.02']
nw = hol.intersection(box(0.5, 22.95, 8.15, 29.2)).area
pas = hol.intersection(box(6.65, 12.45, 8.15, 22.95)).area
kor = hol.intersection(box(8.15, 21.0, 19.85, 22.4)).area
print(f'SWD.02 = {hol.area:.1f} m²: narożnik NW {nw:.1f} m² (7,65 × 6,25) + pasaż zach. {pas:.1f} m² (szer. 1,50) + korytarz pn. {kor:.1f} m² (szer. 1,40)')
print(f'W narożniku NW spec. umieszcza bar SWD.05 (30) i szatnię SWD.06 (12) → wolny hol = {nw-42:.1f} m²')
prog = {p['id']: p for b in P['bloki'] if b['kod'] in ('SWD', 'PHS') for p in b['pomieszczenia']}
need = prog['SWD.02']['pow_laczna'] + prog['SWD.05']['pow_laczna'] + prog['SWD.06']['pow_laczna']
need_min = prog['SWD.02']['zakres_pow_jedn'][0] + prog['SWD.05']['zakres_pow_jedn'][0] + prog['SWD.06']['zakres_pow_jedn'][0]
print(f'Program SWD.02+05+06 = {need} m² (minimum zakresów {need_min}); w rzucie {hol.area:.1f} → deficyt {need-hol.area:.0f} m² (do minimum {need_min-hol.area:.0f})')
print(f'Nawet z kuluarem ({R["KUL"].area:.1f}): {hol.area+R["KUL"].area:.1f} < {need_min} (minimum) – a kuluar to droga ewakuacyjna')
antF = Polygon(K['kondygnacja_sejmiku']['antresola_strefy']['ANT-F']['obrys_uv'][0])
print(f'SWD.03 „sala multimedialna” = ANT-F {antF.area:.1f} m²; pas o szerokości 1,25 m na długości 16,0 m ({antF.intersection(box(21,10.05,37,11.3)).area:.1f} m²) = przejście za 2 rzędami galerii')
# przestrzeń przed dźwigami
print('Przed dźwigami A1/A2 (lico pn. trzonu A, v 20,85) → korytarz pn. v 21,0–22,4 = 1,40 m (WT §195: ≥ 1,6 m; M.13 s.170: 3,6 m)')
print('Przed P1/P2 na antresoli (lico pn. trzonu B, v 9,9) → ANT-F v 10,05–11,30 = 1,25 m, do 1. rzędu galerii (v 11,45) 1,55 m (WT §195: ≥ 1,6 m)')

# --- program vs rzut
hr('1c. Program SWD/PHS.05 vs rzut')
cmp = [('SWD.01', ['SWD.01']), ('SWD.02', ['SWD.02']), ('SWD.03', []), ('SWD.04', ['SWD.04']), ('SWD.05', []), ('SWD.06', []),
       ('SWD.07', ['SWD.07']), ('SWD.08', ['SWD.08']), ('SWD.09', ['SWD.09']), ('SWD.10', ['SWD.10a', 'SWD.10b']),
       ('SWD.11', ['SWD.11a', 'SWD.11b']), ('SWD.12', ['SWD.12a', 'SWD.12b']), ('SWD.13', ['SWD.13']), ('SWD.14', ['SWD.14']),
       ('SWD.15', ['SWD.15']), ('PHS.05', ['PHS.05a', 'PHS.05b', 'PHS.05c'])]
extra = {'SWD.03': antF.area, 'SWD.05': 30.0, 'SWD.06': 12.0}
sp = sm = 0
for pid, rooms in cmp:
    pr = prog[pid]
    a = sum(R[r].area for r in rooms) + extra.get(pid, 0)
    zmin = pr['zakres_pow_jedn'][0] * pr['liczba']
    sp += pr['pow_laczna']; sm += a
    note = '' if a >= zmin - 0.05 else '  < MIN'
    if pid in extra: note += '  (bez własnej powierzchni: w holu / na antresoli)'
    print(f'  {pid:7s} program {pr["pow_laczna"]:6.1f} (min {zmin:6.1f})  rzut {a:6.1f}{note}')
print(f'  RAZEM program {sp:.0f} m² netto / rzut {sm:.0f} m² (z barem i szatnią liczonymi podwójnie)')

# --------------------------------------------------------------------------------------------
# 2. Sala obrad – czy 44 stanowiska + pochylnie mieszczą się w rzucie
# --------------------------------------------------------------------------------------------
hr('2. Sala obrad – geometria rzędów (ognisko F = (30,0; 13,4))')
sala = R['SWD.01']
F = Point(30.0, 13.4)
def t_wall(phi):
    d = (math.cos(math.radians(phi)), math.sin(math.radians(phi)))
    ln = LineString([(F.x, F.y), (F.x + 40 * d[0], F.y + 40 * d[1])])
    x = ln.intersection(sala.exterior)
    pts = [x] if x.geom_type == 'Point' else list(getattr(x, 'geoms', []))
    return min(F.distance(p) for p in pts)
need_r3 = 9.0 + 0.5 + 1.2   # linia krzeseł R 9,0, oparcie +0,5, przejście za rzędem 1,2 m (ZL I, wózek)
ok = [phi for phi in [x * 0.5 for x in range(0, 361)] if t_wall(phi) >= need_r3]
lo, hi = min(ok), max(ok)
arc = math.radians(hi - lo) * 9.0
print(f'Rząd 3 (R 9,0): wolne od ścian w zakresie φ {lo:.1f}°–{hi:.1f}° = {hi-lo:.1f}° → łuk {arc:.1f} m')
for w in (1.0, 1.2):
    req = 18 * w + 1.5 + 2 * 1.5   # 18 pulpitów + 1 miejsce dla wózka 1,5 m + 2 przejścia/pochylnie boczne po 1,5 m
    print(f'   wymagane przy pulpicie {w:.1f} m: 18×{w:.1f} + wózek 1,5 + 2 pochylnie/przejścia 1,5 = {req:.1f} m → {"MIEŚCI" if req <= arc else "NIE MIEŚCI (brak " + format(req-arc, ".1f") + " m)"}')
print(f'   (spec. rozkłada 19 miejsc na półokręgu π·9,0 = {math.pi*9:.1f} m, czego ściana wsch. u 39,5 i łuk R 13,5 nie dopuszczają)')
for phi in (0, 15, 30, 45, 60, 90, 135, 150, 165, 180):
    print(f'   φ={phi:3d}°  odległość F→ściana {t_wall(phi):5.2f} m')
gal_cant = box(21.0, 12.45, 37.0, 13.45)
print(f'Galeria nad salą: v 12,45–13,45 (wysięg 1,0 m) – nad pasem prezydium (pulpit prezydium v ≈ 12,45–14,2): publiczność nie widzi prezydium ani twarzy mówcy przy mównicy.')
# widoczność z 2. rzędu galerii (płaska galeria)
eye2, head1, dx = 1.15, 1.25, 1.0   # oko rząd 2 / czubek głowy rząd 1 / odstęp rzędów
ang = math.degrees(math.atan((3.60 + 1.15 - 1.20) / (1.9 + 4.8)))
print(f'Płaska galeria, 2 rzędy co 1,0 m: kąt patrzenia z rzędu 2 na rząd 1 radnych ≈ {ang:.0f}° w dół → linia przechodzi '
      f'{math.tan(math.radians(ang))*dx:.2f} m pod okiem w miejscu rzędu 1, a głowy rzędu 1 są +0,10 m nad okiem → brak widoczności (wymagany podest ≥ 0,45–0,6 m)')

# --------------------------------------------------------------------------------------------
# 3. Kondygnacje biurowe – pojemność elewacyjna vs zapotrzebowanie
# --------------------------------------------------------------------------------------------
hr('3. Kondygnacje biurowe – jednostki elewacyjne 4,05 m (głęb. 6,10)')
U_NARAD = 7.60 / 4.05; U_MAG_STD = 1.0; U_MAG_G = 2.70 / 4.05
cap = {'1': 43, '2': 43, '3': 43, '4': 43, '5': 24, '6': 24}
dem = {
    '1': 38 + U_NARAD + 3 * U_MAG_G,
    '2': 38 + U_NARAD + 3 * U_MAG_STD,
    '3': 35 + 2 * U_NARAD + 4 * U_MAG_STD,
    '4': 34 + U_NARAD + 6 * U_MAG_STD,
    '5': 19 + U_NARAD + 4 * U_MAG_G,
    '6': 19 + (40 + 14.5) / 24.1 + 3 * 30 / 24.1,
}
for k in cap:
    print(f'  kond. {k}: potrzeba {dem[k]:5.2f} j. / pojemność {cap[k]} → zapas {cap[k]-dem[k]:+.2f}')
print(f'  Σ potrzeba {sum(dem.values()):.1f} + parter 4 = {sum(dem.values())+4:.1f} j. / 224 (spec.: zajęte 220,8, rezerwa 3,2)')
print('  Kond. 6: Przewodniczący 40 + asystent 14,5 na łuku i 3 Wiceprzewodniczących po 30 przy elewacji → przekroczenie ≈ 1 j.')
# pojemność kond. 5/6 (sama wieża): obwody segmentów elewacji, narożniki wypukłe
segs = {'S1 (u 0,5–24,85)': 24.35, 'S2 (u 31,1–39,5)': 8.40, 'E (v 0,5–15,7)': 15.20, 'N (u 0,5–26)': 25.50, 'W (v 0,5–29,2)': 28.70}
best = None
import itertools
for nw, sw, se in itertools.product(['N', 'W'], ['W', 'S1'], ['S2', 'E']):
    L = dict(segs)
    for corner, owner in (('NW', nw), ('SW', sw), ('SE', se)):
        other = {'NW': {'N': 'W', 'W': 'N'}, 'SW': {'W': 'S1', 'S1': 'W'}, 'SE': {'S2': 'E', 'E': 'S2'}}[corner][owner]
        key = [k for k in L if k.startswith(other)][0]
        L[key] -= 6.10
    n = sum(int(max(0, v) // 4.05) for v in L.values()) + 4   # + łuk 4
    if best is None or n > best[0]: best = (n, nw, sw, se, {k: round(v, 2) for k, v in L.items()})
print(f'  Wieża (kond. 5–6) – najlepszy przydział narożników: {best[0]} j. ({best[4]}) – zapas długości w S1 {best[4]["S1 (u 0,5–24,85)"] - 6*4.05:.2f} m')

# --------------------------------------------------------------------------------------------
# 4. Osoby na kondygnacjach, pokoje socjalne, WC
# --------------------------------------------------------------------------------------------
hr('4. Osoby / pokoje socjalne (PS.01: do 30 os.) / WC')
kom = P['kadra']['komorki']
os_ = {d: sum(r['razem'] for r in rows) for d, rows in kom.items()}
fl = {'1': ['DOS'], '2': ['DI', 'DST'], '3': ['DGP', 'GW'], '4': ['CZ', 'DKD', 'DZ'], '5': ['DSS'], '6': ['KS', 'DRA']}
soc = {'1': 3, '2': 3, '3': 3, '4': 3, '5': 2, '6': 1}
for k, deps in fl.items():
    n = sum(os_[d] for d in deps)
    print(f'  kond. {k}: {n:3d} os. ({"+".join(deps)}), socjalne {soc[k]} × 30 = {soc[k]*30} → {"OK" if soc[k]*30 >= n else "ZA MAŁO (potrzeba " + str(math.ceil(n/30)) + ")"}')
wc_prog = sum(p['pow_laczna'] for b in P['bloki'] if b['kod'] == 'PHS' for p in b['pomieszczenia'])
wc_spec = 260
print(f'  WC: program PHS {wc_prog} m², spec. „WC 260” → deficyt {wc_prog-wc_spec} m² ({(wc_prog-wc_spec)/wc_prog*100:.0f} %)')
rest = 260 - 19 - 12 - 40 - (R['PHS.05a'].area + R['PHS.05b'].area + R['PHS.05c'].area)
print(f'  Na 10 zespołów kond. 1–6 zostaje {rest:.0f} m² = {rest/10:.1f} m²/zespół (program PHS.01: 28, zakres 22–40)')

# --------------------------------------------------------------------------------------------
# 5. Parking, MDS
# --------------------------------------------------------------------------------------------
hr('5. Parking (MPZP §13) i MDS')
PU = 8400; gastro = 92
mp = 12 * (PU - gastro) / 1000 + 6 * gastro / 1000
print(f'  12/1000 × (8 400 − 92) + 6/1000 × 92 = {mp:.1f} → {math.ceil(mp)} m.p. (spec. podaje 99); program (PU 8 582) 103; z holami 110; zapewniono 109')
mds = PU / 15
print(f'  MDS ≥ PU/15 = {mds:.0f} os.; rozp. MSWiA 2025 poz. 932 §6: wyjścia ewakuacyjne ceil({mds:.0f}/200) = {math.ceil(mds/200)}, '
      f'zapasowe ceil({mds:.0f}/400) = {math.ceil(mds/400)} poza strefą zagruzowania (H/3 = {37.62/3:.1f} m od wieży); '
      f'wariant „2 klatki ≥ 15 m” dopuszcza ≤ 300 os.')

# --------------------------------------------------------------------------------------------
# 6. Trzony
# --------------------------------------------------------------------------------------------
hr('6. Trzony A i B – minimalna powierzchnia (szacunek)')
klatka = (2 * 1.60 + 0.20) * (1.60 + 3.0 + 1.60) + 1.5 * 1.5   # bieg 1,60 (M.13), spoczniki 1,60, MOE 1,5×1,5 (dostepnosc.md)
przeds = 2.4 * 3.0
szyb = {'1600 kg (1,4×2,4)': 2.10 * 2.85, '1275 kg (1,4×2,4)': 2.10 * 2.85, '1000 kg (1,1×2,1)': 1.80 * 2.60, '2000 kg (1,5×2,7)': 2.20 * 3.20}
sz = 4.5
A_net = klatka + przeds + 2 * szyb['1600 kg (1,4×2,4)'] + szyb['1000 kg (1,1×2,1)'] + sz
B_net = klatka + przeds + 2 * szyb['1275 kg (1,4×2,4)'] + szyb['2000 kg (1,5×2,7)'] + sz
for nm, net, have in (('A', A_net, 60.48), ('B', B_net, 58.75)):
    gross = net * 1.18   # ściany REI 60 0,20–0,25 m ≈ 18 %
    print(f'  Trzon {nm}: netto ≈ {net:.1f} m², z ścianami ≈ {gross:.1f} m² vs obrys {have} m² → {"OK" if gross <= have else "BRAK " + format(gross-have, ".0f") + " m²"}')
print('  Uwaga: kabina 1,4×2,4 m = 3,36 m² > maks. powierzchnia dla 1 275 kg wg PN-EN 81-20 (2,95 m²); M.13 s.172 wymaga 1,5×2,1 m (nieprzelotowa)')

# --------------------------------------------------------------------------------------------
# 7. Kontrola proponowanych poprawek
# --------------------------------------------------------------------------------------------
hr('7a. Poprawka sali: 4 rzędy wokół F = (29,5; 13,4), R 4,8 / 6,6 / 8,4 / 10,2 (+0,15…+0,60)')
def rows(Fp, Rs, w, aisle=1.4, wc=1.5, phimin=12, phimax=168):
    global F
    F = Point(*Fp); res = []
    for i, Rr in enumerate(Rs):
        need = Rr + 0.45 + (1.2 if i == len(Rs) - 1 else 0.7)
        ok = [p / 2 for p in range(phimin * 2, phimax * 2 + 1) if t_wall(p / 2) >= need]
        lo, hi = min(ok), max(ok)
        arcl = math.radians(hi - lo) * Rr
        res.append((Rr, lo, hi, round(arcl, 1), int((arcl - 2 * aisle - wc) // w) + 1))
    return res
for w in (1.0, 1.2):
    r = rows((30.0, 13.4), [4.8, 6.9, 9.0], w)
    print(f'  SPEC 3 rzędy, pulpit {w}: ' + ', '.join(f'R{x[0]}: {x[4]}' for x in r) + f' → razem {sum(x[4] for x in r)} (wymagane 44)')
    r = rows((29.5, 13.4), [4.8, 6.6, 8.4, 10.2], w)
    print(f'  POPRAWKA 4 rzędy, pulpit {w}: ' + ', '.join(f'R{x[0]} φ{x[1]:.0f}–{x[2]:.0f}°: {x[4]}' for x in r) + f' → razem {sum(x[4] for x in r)}')
F = Point(30.0, 13.4)

hr('7b. Poprawka rozmieszczenia (kond. 1, 4, 5, 6)')
new = {
    '1': 38 + U_NARAD + 4 * U_MAG_G,
    '2': 38 + U_NARAD + 3 * U_MAG_STD,
    '3': 35 + 2 * U_NARAD + 4 * U_MAG_STD,
    '4': 34 + U_NARAD + 5 * U_MAG_STD + 3 * U_MAG_G,
    '5': 19 + 2 + U_NARAD + 1 * U_MAG_G,          # + DRA.5.SAM ×2
    '6': 17 + (40 + 14.5) / 24.1 + 3 * 30 / 24.1,   # KS 8 + DRA 9
}
for k in cap:
    print(f'  kond. {k}: {new[k]:5.2f} / {cap[k]} → zapas {cap[k]-new[k]:+.2f}')
print(f'  kond. 6 dyskretnie: 16 pokoi × 4,05 + 3 gabinety Wice × 4,92 = {16*4.05 + 3*30/6.10:.2f} m ≤ 20 j. × 4,05 = 81,0 m; łuk: Przew. 40 + asyst. 14,5 + 1 pokój + OCZ/zaplecze 20 ≈ 99 m² ≤ 100 m²')
mags = 4 + 3 + 4 + 5 + 3 + 1
print(f'  magazynki: kond.1 4 gł., kond.2 3 std, kond.3 4 std, kond.4 5 std + 3 gł., kond.5 1 gł. = {mags} (12 std + 8 gł.)')

hr('7c. Poprawka MDS: szyb wyjścia zapasowego')
s_ = json.load(open('model/site.json'))
Pt = Point(91.75, 32.00)
U1 = Polygon(K['podziemie']['-1']['obrys_ccw'])
trees = [Point(t['e'], t['n']) for t in s_['zielen']['drzewa'] if t.get('w_obszarze_inwestycji')]
ogr = Polygon(s_['granice']['ogrodki_przydomowe']['pts'])
print(f'  (91,75; 32,00): od wieży {Pt.distance(W_en):.1f} m (≥ 12,5), od skrzydła {Pt.distance(M_en.buffer(0)):.1f} m (≥ 7,3), od segmentu {Pt.distance(S_en):.1f} m (≥ 7,1), '
      f'od najbliższego drzewa {min(Pt.distance(t) for t in trees):.1f} m, w ogródkach: {ogr.contains(Pt)}, tunel od obrysu −1: {Pt.distance(U1):.1f} m')

hr('7d. Poprawka S-2 – bilans poziomu głównego (wnętrze 1 080,1 m²) przy wszystkich salach na dolnych granicach')
s2 = {'trzony A+B (T przeniesiony do segmentu)': 119.2, 'SWD.01 sala (4 rzędy)': 283.0, 'SWD.04 (v 12,45–16,05)': 15.1, 'SWD.07 (u 32,90–37,25)': 11.5,
      'SWD.08': 90.0, 'SWD.09': 54.0, 'SWD.10a/b': 16.0, 'SWD.11a/b': 108.0, 'SWD.12a/b': 60.0, 'SWD.13': 36.0, 'SWD.14': 20.0,
      'PHS.05: K 18,4 (u 17,0–19,85×v 22,75–29,2) + M 19,5 (u 15,65–19,85×v 16,20–20,85) + 2,1': 40.0, 'PP.06 porządkowe + IT.02 PD (u 37,40–39,50)': 5.6, 'dojście do SWD.11b': 4.0,
      'hol dolny: narożnik NW 47,8 + pasaż 15,8 + korytarz pn. 1,60×11,7 (z szatnią SWD.06 12)': 82.3, 'KUL': 87.8, 'ściany wewn. (0,20/0,30)': 47.0}
tot2 = sum(s2.values())
for k, v in s2.items(): print(f'  {k:85s} {v:7.1f}')
print(f'  RAZEM {tot2:.1f} m² vs 1 080,1 → {"mieści się" if tot2 <= 1080.1 else "przekroczenie"} ({1080.1-tot2:+.1f} m²)')
ant = {'galeria zachodnia u 15,65–21,0 × v 12,45–20,85 (zamiast pd.)': 44.9, 'bar SWD.05 (strefa otwarta)': 30.0, 'SWD.03 strefa multimedialna': 30.0,
       'WC publiczne dostępne (kabina 2,2×2,5)': 5.6, 'hol górny / foyer / dojścia': 69.3}
print(f'  Kontrola: ANT-F 37,7 + galeria zach. 44,9 + płyta NW 80,3 + kładka 16,9 = {37.7+44.9+80.3+16.9:.1f} m²')
print(f'  Antresola: {sum(ant.values()):.1f} m² ({sum(ant.values())/W_uv.area*100:.0f} % rzutu): pas ANT-F 37,7 + galeria zach. 44,9 + nowa płyta NW u 0,5–8,15 × v 12,45–22,95 (80,3) + kładka nad kuluarem u 8,15–15,65 (16,9)')
hol_ru = 82.3 - 12 + ant['hol górny / foyer / dojścia']
print(f'  Hol (RU) = dolny bez szatni {82.3-12:.1f} + górny {ant["hol górny / foyer / dojścia"]:.1f} = {hol_ru:.1f} m² (program 150, min 120)')
