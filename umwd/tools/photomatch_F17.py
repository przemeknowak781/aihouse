#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photomatch_F17.py - kalibracja kamer (photomatch) dla zdjec lotniczych F.17.A i F.17.B (konkurs UMWD, Wroclaw)
oraz parametry kamery Blendera do wklejenia renderu projektowanego budynku w zdjecia.

Odtwarza:
  * model/kamery_F17.json                                  - kamery A i B (pinhole), punkty kontrolne, bledy, Blender
  * docs/60_wizualizacje/img/photomatch_F17{A,B}_*.jpg     - obrazy kontrolne (nakladki rzutow, render testowy)

Metoda (szczegoly: docs/60_wizualizacje/photomatch_F17.md):
  1. Kadr: F.17 = kadr z panoramy 8000x5632 px (M.10 = ta sama panorama zmniejszona do 4000x2816).
     Transformacja M.10 -> F.17 (F = s*M + t) z korelacji fazowej 77 latek (--kadr przelicza od nowa).
  2. Model: kamera otworkowa (prostoliniowa), punkt glowny w srodku panoramy (M.10: 2000, 1408),
     niewiadome: polozenie (e, n, H), yaw (azymut siatki osi), pitch, roll, ogniskowa f [px M.10].
  3. Obserwacje: punkty i linie (krawedzie pionowe budynkow, krawezniki pomiarowe 3D) z mapy M.02 i NMT,
     horyzont; dla A dodatkowo punkty wiazace z korelacji ortofotoplanow A/B (wzgledem rozwiazanej kamery B).
  4. Najmniejsze kwadraty (scipy.optimize.least_squares, soft_l1), slaba wiez GPS (sigma 10 m),
     odrzucanie odstajacych (|r|/sigma > 3,5), walidacja krzyzowa leave-one-out dla punktow recznych.
  5. Parametry Blendera (sensor_fit HORIZONTAL, 36 mm, shift_x/shift_y z polozenia punktu glownego w kadrze F.17),
     z = H - 119,25 (+-0,00 = 119,25 m n.p.m.).
  6. --render: test w bpy (Workbench): bryly Mazowiecka 19 i Wybrzeze Slowackiego 5-8, teren NMT, krawezniki,
     granice; nalozenie na zdjecie + kontrola numeryczna world_to_camera_view vs model otworkowy.

Uzycie (pliki organizatora traktowane jako niezaufane - uruchamiac z -I):
  /home/user/aihouse/.venv-render/bin/python -I tools/photomatch_F17.py [--kadr] [--render] [--no-img]
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.optimize import least_squares

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[1]
SITE_P = ROOT / 'model' / 'site.json'
OUT_JSON = ROOT / 'model' / 'kamery_F17.json'
IMG_DIR = ROOT / 'docs' / '60_wizualizacje' / 'img'
M10_DIR = ROOT / '00_materialy/_rozpak/5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026/M.10. ZDJĘCIA OTOCZENIA/M.10. ZDJĘCIA OTOCZENIA'
F17_DIR = ROOT / '00_materialy/_rozpak/3.Zalaczniki_Formalne_F.01-F.17_PDF'
FILES = {
    'A': (M10_DIR / 'DJI_20251029113800_0009_D.jpg', F17_DIR / 'F.17.A_widok z lotu ptaka od strony wschodniej_wer.01.jpg'),
    'B': (M10_DIR / 'DJI_20251029115736_0025_D.jpg', F17_DIR / 'F.17.B_widok z lotu ptaka od strony zachodniej_wer.01.jpg'),
}
Z0 = 119.25            # +-0,00 = 119,25 m n.p.m. (os z Blendera = H - Z0)
MW, MH = 4000, 2816    # M.10 (panorama 8000x5632 zmniejszona x0,5)
PP_M = (2000.0, 1408.0)  # punkt glowny = srodek panoramy (wsp. ciagle, piksel i = [i, i+1))
# wynik --kadr (korelacja fazowa, 73/77 latek, RMS 0,04/0,06 px F); wsp. ciagle
KADR = {'A': dict(s=2.49999, tx=-660.02, ty=-1380.05, W=8470, H=4475, rms_px=0.04, n=73),
        'B': dict(s=2.50016, tx=-570.00, ty=-1455.29, W=7962, H=4505, rms_px=0.06, n=77)}
GPS = {'A': (356.39, 24.10), 'B': (-44.55, -27.06)}   # EXIF/XMP DJI -> PL-2000/6 -> uklad lokalny
EXIF = {'A': dict(czas='2025-10-29 11:38:00 CET', gps_lokalnie=[356.39, 24.10], rel_alt=87.8, abs_alt_dji=219.739,
                  gimbal_yaw=-89.2, gimbal_pitch=-12.9, flight_yaw=-74.0),
        'B': dict(czas='2025-10-29 11:57:36 CET', gps_lokalnie=[-44.55, -27.06], rel_alt=50.7, abs_alt_dji=182.639,
                  gimbal_yaw=39.2, gimbal_pitch=-11.4, flight_yaw=54.4)}

# ------------------------------------------------------------------------------------------------ obserwacje
# typ 'pt'  : X = [e, n, H], uvF = [x, y] w pikselach pliku F.17 (wsp. ciagle), sigma [px F]
# typ 'line': X = polilinia 3D (lista lub 'kraw3d:i' = site.json krawezniki_pomiar_NMT[i]); uvF = punkty lezace
#             na obrazie tej linii (residuum = odleglosc prostopadla); sigma [px F]
# typ 'hor' : horyzont, uvM w px M.10, eps = pozorna elewacja linii horyzontu [deg], sigma [px M.10]
OBS = {
    'B': [
        dict(id='latarnia_63.3_72.5', typ='pt', X=[63.295, 72.549, 119.36], uvF=[3810, 2472], sigma=2.0,
             zr='podstawa slupa; M.02 warstwa latarnie (pomiar), H z NMT'),
        dict(id='latarnia_58.2_48.8', typ='pt', X=[58.153, 48.766, 119.04], uvF=[4226, 2632], sigma=2.0,
             zr='podstawa slupa; M.02 latarnie (pomiar), H z NMT'),
        dict(id='latarnia_48.2_23.8', typ='pt', X=[48.183, 23.84, 118.60], uvF=[4721, 2936], sigma=6.0,
             zr='podstawa slupa (czesciowo zaslonieta); M.02 latarnie (pomiar), H z NMT'),
        dict(id='latarnia_78.6_83.5', typ='pt', X=[78.59, 83.52, 119.34], uvF=[3860, 2347], sigma=4.0,
             zr='podstawa slupa; e-mapa GUPELA (GESUT), H z NMT'),
        dict(id='latarnia_46.0_87.7', typ='pt', X=[45.98, 87.68, 119.79], uvF=[3183, 2512], sigma=3.0,
             zr='podstawa slupa; e-mapa GUPELA, H z NMT'),
        dict(id='latarnia_27.1_87.1', typ='pt', X=[27.08, 87.13, 120.02], uvF=[2733, 2657], sigma=4.0,
             zr='podstawa slupa; e-mapa GUPELA, H z NMT'),
        dict(id='latarnia_61.8_135.0', typ='pt', X=[61.8, 134.97, 121.22], uvF=[2791, 2222], sigma=5.0,
             zr='podstawa slupa; e-mapa GUPELA, H z NMPT GUGiK (poza NMT)'),
        dict(id='Maz19_naroze_NW_pion', typ='line', X=[[48.842, 9.683, 118.66], [48.842, 9.683, 140.0]],
             uvF=[[5198, 2650], [5183, 2950]], sigma=3.0, zr='krawedz pionowa naroza obrysu EGiB'),
        dict(id='Maz19_naroze_SW_pion', typ='line', X=[[44.644, -8.377, 118.48], [44.644, -8.377, 140.0]],
             uvF=[[5880, 2900], [5850, 3280]], sigma=3.0, zr='krawedz pionowa (styk z Mazowiecka 17), obrys EGiB'),
        dict(id='Maz19_attyka_NW', typ='pt', X=[48.842, 9.683, 140.25], uvF=[5208, 2283], sigma=4.0,
             zr='naroze attyki, H = 140,25 (M.07)'),
        dict(id='Maz19_attyka_SW', typ='pt', X=[44.644, -8.377, 140.25], uvF=[5920, 2422], sigma=4.0,
             zr='naroze attyki, H = 140,25 (M.07)'),
        dict(id='Maz19_podstawa_NW', typ='pt', X=[48.842, 9.683, 118.66], uvF=[5181, 3048], sigma=5.0,
             zr='styk naroza z chodnikiem, H z NMT'),
        dict(id='Maz17_UMWD_lico_podstawa', typ='line', X=[[44.644, -8.377, 118.48], [38.817, -24.358, 118.45]],
             uvF=[[6050, 3405], [6590, 3663]], sigma=6.0, zr='styk elewacji Mazowiecka 17 z chodnikiem'),
        dict(id='kraweznik_wewn_Mazowiecka', typ='line', X='kraw3d:1', uvF=[[4100, 2684], [4700, 2950]], sigma=5.0,
             zr='kraweznik wsch. ul. Mazowieckiej, M.02 model terenu (3D)'),
        dict(id='horyzont', typ='hor', uvM=[[400, 1068], [1500, 1072], [2500, 1080], [3600, 1081]], eps=-0.17, sigma=6.0,
             zr='linia dalekiego horyzontu (las/teren ~10-30 km), elewacja pozorna -0,17 deg'),
        dict(id='UW_naroze_E_gzyms', typ='pt', X=[48.8, 178.8, 136.8], uvF=[1950, 1866], sigma=15.0,
             zr='Urzad Wojewodzki, naroze gzymsu wg NMPT (niepewne) - tylko kontrola', uzyj=False),
    ],
    'A': [
        dict(id='WS5_naroze_NE_dach', typ='pt', X=[118.6, 29.4, 140.2], uvF=[3243, 2380], sigma=6.0,
             zr='naroze krawedzi dachu Wybrzeze Slowackiego 5; e,n,H z NMPT (krawedz gzymsu)'),
        dict(id='WS5_naroze_NE_pion', typ='line', X=[[118.2, 29.3, 119.2], [118.2, 29.3, 140.0]],
             uvF=[[3243, 2450], [3245, 2650]], sigma=4.0, zr='krawedz pionowa naroza NE (obrys EGiB)'),
        dict(id='WS5_naroze_SE_dach', typ='pt', X=[118.9, 10.9, 140.2], uvF=[2905, 2393], sigma=8.0,
             zr='styk dachow WS5/WS6 nad elewacja; NMPT'),
        dict(id='kraweznik_Mazowiecka_wsch', typ='line', X='kraw3d:1', uvF=[[3750, 2402], [3950, 2400]], sigma=4.0,
             zr='kraweznik wsch. ul. Mazowieckiej (granica trawnika), M.02 model terenu (3D)'),
        dict(id='horyzont', typ='hor', uvM=[[400, 1061], [1500, 1066], [2500, 1078], [3600, 1076]], eps=-0.30, sigma=6.0,
             zr='linia dalekiego horyzontu, elewacja pozorna -0,30 deg'),
    ],
}
# Punkty wiazace A: korelacja (NCC, latki 6x6 m) ortofotoplanow terenu 0,1 m z F.17.A i F.17.B (na NMT),
# wzgledem kamery B. (e, n, H, x_F, y_F, NCC).  Patrz opis.
TIES_A = [
    (48.5, 100.5, 120.237, 4112.23, 2330.29, 0.59), (50.5, 100.5, 120.055, 4119.96, 2338.97, 0.45),
    (46.5, 98.5, 120.188, 4085.81, 2329.30, 0.57), (48.5, 98.5, 120.078, 4092.27, 2333.51, 0.59),
    (50.5, 98.5, 119.904, 4099.74, 2338.63, 0.55), (46.5, 96.5, 120.075, 4066.80, 2329.84, 0.46),
    (48.5, 96.5, 119.989, 4074.08, 2334.06, 0.51), (50.5, 96.5, 119.877, 4080.47, 2339.08, 0.53),
    (50.5, 94.5, 119.885, 4061.55, 2339.10, 0.47), (58.5, 90.5, 119.592, 4048.92, 2365.75, 0.67),
    (60.5, 90.5, 119.554, 4054.92, 2371.48, 0.64), (62.5, 90.5, 119.530, 4060.13, 2377.33, 0.49),
    (86.5, 88.5, 119.315, 4111.49, 2463.04, 0.47), (86.5, 86.5, 119.311, 4087.68, 2463.41, 0.65),
    (52.5, 82.5, 119.565, 3957.10, 2357.95, 0.49), (44.5, 80.5, 119.787, 3913.09, 2337.08, 0.48),
    (52.5, 80.5, 119.538, 3934.44, 2358.53, 0.49), (52.5, 78.5, 119.504, 3912.42, 2358.53, 0.56),
    (54.5, 78.5, 119.441, 3917.57, 2364.44, 0.45), (52.5, 76.5, 119.462, 3890.66, 2359.04, 0.55),
    (54.5, 76.5, 119.384, 3896.28, 2364.64, 0.65), (56.5, 76.5, 119.379, 3902.54, 2370.38, 0.51),
    (76.5, 72.5, 119.340, 3903.17, 2430.46, 0.46), (78.5, 72.5, 119.325, 3910.70, 2436.42, 0.47),
    (62.5, 70.5, 119.325, 3843.89, 2389.75, 0.51), (64.5, 70.5, 119.336, 3849.74, 2395.64, 0.46),
    (62.5, 68.5, 119.293, 3822.52, 2390.42, 0.55), (64.5, 68.5, 119.297, 3828.62, 2396.23, 0.50),
    (36.5, 46.5, 118.824, 3475.72, 2316.82, 0.57), (38.5, 46.5, 118.857, 3479.99, 2322.39, 0.56),
    (40.5, 46.5, 118.843, 3486.69, 2328.04, 0.58), (42.5, 46.5, 118.768, 3492.68, 2333.65, 0.47),
    (30.5, 44.5, 118.778, 3437.60, 2299.79, 0.45), (32.5, 44.5, 118.744, 3443.49, 2305.33, 0.56),
    (34.5, 44.5, 118.836, 3449.60, 2310.89, 0.64), (36.5, 44.5, 118.812, 3454.18, 2316.68, 0.62),
    (38.5, 44.5, 118.841, 3458.76, 2322.52, 0.59), (40.5, 44.5, 118.864, 3465.31, 2328.13, 0.60),
    (42.5, 44.5, 118.758, 3470.33, 2333.75, 0.50), (30.5, 42.5, 118.759, 3416.54, 2299.86, 0.57),
    (32.5, 42.5, 118.756, 3422.26, 2305.42, 0.65), (34.5, 42.5, 118.808, 3427.86, 2311.03, 0.67),
    (36.5, 42.5, 118.786, 3432.79, 2316.79, 0.59), (38.5, 42.5, 118.809, 3436.61, 2322.68, 0.54),
    (40.5, 42.5, 118.811, 3442.72, 2328.34, 0.56), (42.5, 42.5, 118.734, 3448.02, 2333.97, 0.46),
    (50.5, 42.5, 118.632, 3471.65, 2356.43, 0.57), (56.5, 42.5, 118.776, 3482.00, 2373.81, 0.64),
    (30.5, 40.5, 118.734, 3395.18, 2299.94, 0.50), (32.5, 40.5, 118.735, 3401.37, 2305.49, 0.54),
    (34.5, 40.5, 118.796, 3407.22, 2311.13, 0.52), (36.5, 40.5, 118.749, 3411.80, 2316.88, 0.46),
    (38.5, 40.5, 118.787, 3415.38, 2322.77, 0.48), (40.5, 40.5, 118.796, 3420.34, 2328.48, 0.52),
    (54.5, 40.5, 118.706, 3458.68, 2367.98, 0.72), (56.5, 40.5, 118.744, 3463.37, 2373.65, 0.60),
    (52.5, 38.5, 118.666, 3442.06, 2362.37, 0.54),
]
TIE_SIGMA = 8.0
for e, n, h, x, y, c in TIES_A:
    OBS['A'].append(dict(id='wiaz_%.1f_%.1f' % (e, n), typ='pt', X=[e, n, h], uvF=[x, y], sigma=TIE_SIGMA,
                         zr='punkt wiazacy z korelacji ortofotoplanow A/B (NCC %.2f)' % c, wiazacy=True))

START = {'A': dict(C=[357.5, 20.8, 203.9], yaw=287.7, pitch=-12.06, roll=-0.42, f=1627.0),
         'B': dict(C=[-42.6, -25.8, 166.6], yaw=56.75, pitch=-12.31, roll=-0.04, f=1538.0)}
FREE = ['e', 'n', 'H', 'yaw', 'pitch', 'roll', 'f']

# ------------------------------------------------------------------------------------------------ dane
SITE = json.load(open(SITE_P, encoding='utf-8'))
_g = SITE['teren']['siatka_NMT']
NMT = np.array([[np.nan if v is None else v for v in row] for row in _g['H_wiersze_od_n0']], float)
NE0, NN0, NK = _g['e0'], _g['n0'], _g['krok_m']


def H_nmt(e, n):
    fx = (e - NE0) / NK; fy = (n - NN0) / NK
    ix, iy = int(math.floor(fx)), int(math.floor(fy))
    if 0 <= ix < NMT.shape[1] - 1 and 0 <= iy < NMT.shape[0] - 1:
        q = NMT[iy:iy + 2, ix:ix + 2]
        if not np.isnan(q).any():
            tx, ty = fx - ix, fy - iy
            return float(q[0, 0] * (1 - tx) * (1 - ty) + q[0, 1] * tx * (1 - ty) + q[1, 0] * (1 - tx) * ty + q[1, 1] * tx * ty)
    pk = np.array([[p[1], p[2], p[3]] for p in SITE['teren']['pikiety'] if p[4] == 1] +
                  [[p['e'], p['n'], p['H']] for p in SITE['teren']['punkty_wysokosciowe_emapy']])
    d = np.hypot(pk[:, 0] - e, pk[:, 1] - n); i = np.argsort(d)[:6]; w = 1 / np.maximum(d[i], 0.5) ** 2
    return float(np.sum(w * pk[i, 2]) / w.sum())


def kraw3d(i):
    o = SITE['ulice_i_sytuacja']['krawezniki_pomiar_NMT'][i]
    return np.c_[np.array(o['pts'], float), np.array(o['z'], float)]


# ------------------------------------------------------------------------------------------------ kamera
def rot_matrix(yaw, pitch, roll):
    """wiersze: osie kamery (x w prawo, y w dol, z do przodu) w ukladzie (e, n, H).
    yaw = azymut siatki osi optycznej (od osi n, zgodnie z zegarem), pitch + w gore, roll + = obrot obrazu przeciwnie do zegara"""
    y, p, r = map(math.radians, (yaw, pitch, roll))
    fwd = np.array([math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)])
    right0 = np.array([math.cos(y), -math.sin(y), 0.0])
    up0 = np.cross(right0, fwd)
    right = math.cos(r) * right0 - math.sin(r) * up0
    up = math.sin(r) * right0 + math.cos(r) * up0
    return np.vstack([right, -up, fwd])


def project_M(P, cam):
    P = np.atleast_2d(np.asarray(P, float))
    Xc = (P - np.array(cam['C'])) @ rot_matrix(cam['yaw'], cam['pitch'], cam['roll']).T
    z = Xc[:, 2]
    x = Xc[:, 0] / z; y = Xc[:, 1] / z
    k1 = cam.get('k1', 0.0); d = 1 + k1 * (x * x + y * y)
    return np.c_[cam.get('cx', PP_M[0]) + cam['f'] * x * d, cam.get('cy', PP_M[1]) + cam['f'] * y * d], z > 0


def M2F(uv, key):
    k = KADR[key]; uv = np.asarray(uv, float)
    return np.c_[k['s'] * uv[:, 0] + k['tx'], k['s'] * uv[:, 1] + k['ty']]


def F2M(uv, key):
    k = KADR[key]; uv = np.asarray(uv, float)
    return np.c_[(uv[:, 0] - k['tx']) / k['s'], (uv[:, 1] - k['ty']) / k['s']]


def project_F(P, cam, key):
    uv, ok = project_M(P, cam)
    return M2F(uv, key), ok


def densify(P, step=0.25):
    P = np.asarray(P, float); out = [P[0]]
    for a, b in zip(P[:-1], P[1:]):
        k = max(1, int(np.linalg.norm(b[:2] - a[:2]) / step))
        for t in np.linspace(0, 1, k + 1)[1:]:
            out.append(a + (b - a) * t)
    return np.array(out)


def signed_dist(p, Q):
    a = Q[:-1]; b = Q[1:]; ab = b - a
    t = np.clip(((p - a) * ab).sum(1) / np.maximum((ab ** 2).sum(1), 1e-12), 0, 1)
    c = a + ab * t[:, None]; d = np.hypot(*(c - p).T); i = int(np.argmin(d))
    return d[i] * np.sign(ab[i, 0] * (p[1] - a[i, 1]) - ab[i, 1] * (p[0] - a[i, 0]))


def residual(o, cam, key):
    """residuum w px F (dla 'hor' w px M.10)"""
    if o['typ'] == 'pt':
        uv, _ = project_F([o['X']], cam, key)
        return uv[0] - np.array(o['uvF'], float)
    if o['typ'] == 'line':
        P = kraw3d(int(o['X'].split(':')[1])) if isinstance(o['X'], str) else np.array(o['X'], float)
        Q, ok = project_F(densify(P), cam, key)
        return np.array([signed_dist(np.array(p, float), Q[ok]) for p in o['uvF']])
    if o['typ'] == 'hor':
        R = rot_matrix(cam['yaw'], cam['pitch'], cam['roll'])
        uv = np.array(o['uvM'], float)
        x = (uv[:, 0] - cam.get('cx', PP_M[0])) / cam['f']; y = (uv[:, 1] - cam.get('cy', PP_M[1])) / cam['f']
        D = np.c_[x, y, np.ones_like(x)] @ R
        el = np.degrees(np.arctan2(D[:, 2], np.hypot(D[:, 0], D[:, 1])))
        return np.radians(el - o['eps']) * cam['f']
    raise ValueError(o['typ'])


def make_cam(x, base, free=FREE):
    c = dict(base); c['C'] = list(base['C'])
    for k, v in zip(free, x):
        if k in 'enH':
            c['C']['enH'.index(k)] = float(v)
        else:
            c[k] = float(v)
    return c


def solve(key, obs, cam0, free=FREE, gps_sigma=10.0, loss='soft_l1'):
    use = [o for o in obs if o.get('uzyj', True)]

    def fun(x):
        cam = make_cam(x, cam0, free)
        r = [np.atleast_1d(residual(o, cam, key)) / o['sigma'] for o in use]
        r.append(np.array([(cam['C'][0] - GPS[key][0]) / gps_sigma, (cam['C'][1] - GPS[key][1]) / gps_sigma]))
        return np.concatenate(r)
    x0 = [{'e': cam0['C'][0], 'n': cam0['C'][1], 'H': cam0['C'][2]}.get(k, cam0.get(k, 0.0)) for k in free]
    sol = least_squares(fun, x0, loss=loss, f_scale=1.5, x_scale='jac')
    cam = make_cam(sol.x, cam0, free)
    J = sol.jac; dof = max(1, len(sol.fun) - len(x0))
    s2 = max(1.0, float((sol.fun ** 2).sum()) / dof)
    cov = np.linalg.inv(J.T @ J) * s2
    return cam, dict(zip(free, np.sqrt(np.diag(cov)).tolist())), cov


def stats(key, cam, obs):
    rows = []; e_pt = []; e_ln = []
    for o in obs:
        r = np.atleast_1d(residual(o, cam, key))
        if o['typ'] == 'hor':
            r = r * KADR[key]['s']
        row = dict(id=o['id'], typ=o['typ'], uzyty=o.get('uzyj', True), sigma_px=o['sigma'] * (KADR[key]['s'] if o['typ'] == 'hor' else 1))
        if o['typ'] == 'pt':
            row.update(dx=round(float(r[0]), 1), dy=round(float(r[1]), 1), blad_px=round(float(np.hypot(*r)), 1))
            if o.get('uzyj', True):
                (e_pt if not o.get('wiazacy') else e_pt).append(float(np.hypot(*r)))
        else:
            row.update(residua_px=[round(float(v), 1) for v in r], rms_px=round(float(np.sqrt(np.mean(r ** 2))), 1))
            if o.get('uzyj', True) and o['typ'] == 'line':
                e_ln.extend(r.tolist())
        rows.append(row)
    rp = float(np.sqrt(np.mean(np.square(e_pt)))) if e_pt else None
    rl = float(np.sqrt(np.mean(np.square(e_ln)))) if e_ln else None
    return rows, rp, rl


def solve_robust(key, verbose=True):
    obs = OBS[key]
    cam0 = dict(START[key]); cam0['cx'], cam0['cy'] = PP_M
    for it in range(3):
        cam, std, cov = solve(key, obs, cam0)
        changed = False
        for o in obs:
            if not o.get('uzyj', True) or o['typ'] == 'hor':
                continue
            r = np.atleast_1d(residual(o, cam, key)) / o['sigma']
            if np.max(np.abs(r)) > 3.5:
                o['uzyj'] = False; o['odrzucony'] = 'residuum %.1f sigma' % np.max(np.abs(r)); changed = True
        cam0 = cam
        if not changed:
            break
    cam, std, cov = solve(key, obs, cam0)
    # leave-one-out dla obserwacji recznych (bez punktow wiazacych)
    loo = []
    for o in obs:
        if not o.get('uzyj', True) or o.get('wiazacy') or o['typ'] == 'hor':
            continue
        o['uzyj'] = False
        c2, _, _ = solve(key, obs, cam)
        o['uzyj'] = True
        r = np.atleast_1d(residual(o, c2, key))
        loo.append(dict(id=o['id'], blad_px=round(float(np.hypot(*r) if o['typ'] == 'pt' else np.sqrt(np.mean(r ** 2))), 1)))
    if verbose:
        print(key, {k: (round(v, 4) if not isinstance(v, list) else [round(q, 3) for q in v]) for k, v in cam.items()})
        print('   std', {k: round(v, 3) for k, v in std.items()})
    return cam, std, cov, loo


# ------------------------------------------------------------------------------------------------ kadr (opcjonalnie)
def wyznacz_kadr(key):
    """F = s*M + t (podobienstwo) z korelacji fazowej latek; zwraca s, t w wsp. ciaglych"""
    from scipy import fft
    def gray(p):
        return np.asarray(Image.open(p).convert('L'), dtype=np.float32)
    def hp(a, s=2.0):
        return a - ndimage.gaussian_filter(a, 8 * s)
    def pc(a, b):
        w = np.hanning(a.shape[0])[:, None] * np.hanning(a.shape[1])[None, :]
        R = fft.fft2(a * w) * np.conj(fft.fft2(b * w)); R /= np.abs(R) + 1e-9
        r = np.real(fft.ifft2(R)); iy, ix = np.unravel_index(np.argmax(r), r.shape); ny, nx = r.shape
        def sub(c, m, p):
            dn = m - 2 * c + p
            return 0.5 * (m - p) / dn if dn != 0 else 0.0
        sy = iy + sub(r[iy, ix], r[(iy - 1) % ny, ix], r[(iy + 1) % ny, ix])
        sx = ix + sub(r[iy, ix], r[iy, (ix - 1) % nx], r[iy, (ix + 1) % nx])
        return (sx - nx if sx > nx / 2 else sx), (sy - ny if sy > ny / 2 else sy), r.max()
    M = gray(FILES[key][0]); F = gray(FILES[key][1]); H, W = F.shape
    s0 = 2.5
    Fs = np.asarray(Image.fromarray(F).resize((int(round(W / s0)), int(round(H / s0))), Image.BILINEAR), dtype=np.float32)
    a = hp(M); b = np.zeros_like(a); b[:Fs.shape[0], :Fs.shape[1]] = hp(Fs)
    sx, sy, _ = pc(a, b)
    s, rot, tx, ty = s0, 0.0, -sx * s0, -sy * s0
    for _ in range(4):
        pm, pf = [], []
        for fy in np.linspace(0.08, 0.92, 7):
            for fx in np.linspace(0.06, 0.94, 11):
                xf, yf = fx * W, fy * H
                c, si = math.cos(rot), math.sin(rot)
                dx, dy = (xf - tx) / s, (yf - ty) / s
                xm, ym = c * dx + si * dy, -si * dx + c * dy
                ps = 160; x0, y0 = int(xm - ps / 2), int(ym - ps / 2)
                if x0 < 0 or y0 < 0 or x0 + ps > M.shape[1] or y0 + ps > M.shape[0]:
                    continue
                pM = M[y0:y0 + ps, x0:x0 + ps]
                yy, xx = np.mgrid[y0:y0 + ps, x0:x0 + ps].astype(float)
                XF = s * (c * xx - si * yy) + tx; YF = s * (si * xx + c * yy) + ty
                oy, ox = int(YF.min()) - 8, int(XF.min()) - 8
                sub = ndimage.gaussian_filter(F[oy:int(YF.max()) + 9, ox:int(XF.max()) + 9], s * 0.45)
                pF = ndimage.map_coordinates(sub, [YF - oy, XF - ox], order=1).astype(np.float32)
                if pM.std() < 4:
                    continue
                ddx, ddy, pk = pc(hp(pM, 0.5), hp(pF, 0.5))
                if pk < 0.08:
                    continue
                pm.append((xm + ddx, ym + ddy)); pf.append((xf, yf))
        pm, pf = np.array(pm), np.array(pf)
        A = np.zeros((2 * len(pm), 4)); L = np.zeros(2 * len(pm))
        A[0::2] = np.c_[pm[:, 0], -pm[:, 1], np.ones(len(pm)), np.zeros(len(pm))]
        A[1::2] = np.c_[pm[:, 1], pm[:, 0], np.zeros(len(pm)), np.ones(len(pm))]
        L[0::2], L[1::2] = pf[:, 0], pf[:, 1]
        x, *_ = np.linalg.lstsq(A, L, rcond=None)
        res = np.hypot(*(A @ x - L).reshape(-1, 2).T); ok = res < max(3 * np.median(res), 1.0)
        x, *_ = np.linalg.lstsq(A[np.repeat(ok, 2)], L[np.repeat(ok, 2)], rcond=None)
        res = np.hypot(*(A @ x - L).reshape(-1, 2).T)
        s = float(np.hypot(x[0], x[1])); rot = float(math.atan2(x[1], x[0])); tx, ty = float(x[2]), float(x[3])
    rms = float(np.sqrt(np.mean(res[ok] ** 2)))
    # indeksy -> wsp. ciagle: F_c = s*M_c + t + 0.5*(1-s)
    return dict(s=round(s, 5), tx=round(tx + 0.5 * (1 - s), 2), ty=round(ty + 0.5 * (1 - s), 2), W=W, H=H,
                obrot_deg=round(math.degrees(rot), 4), rms_px=round(rms, 3), n=int(ok.sum()))


# ------------------------------------------------------------------------------------------------ Blender
def euler_xyz(R):
    """macierz obrotu (kolumny = osie lokalne w swiecie) -> Euler XYZ Blendera (R = Rz @ Ry @ Rx)"""
    sy = -R[2, 0]
    y = math.asin(max(-1.0, min(1.0, sy)))
    x = math.atan2(R[2, 1], R[2, 2]); z = math.atan2(R[1, 0], R[0, 0])
    return x, y, z


def blender_params(cam, key):
    k = KADR[key]; W, H = k['W'], k['H']
    fF = cam['f'] * k['s']
    cxF = k['s'] * cam.get('cx', PP_M[0]) + k['tx']; cyF = k['s'] * cam.get('cy', PP_M[1]) + k['ty']
    Rw = rot_matrix(cam['yaw'], cam['pitch'], cam['roll'])        # wiersze: right, down, fwd
    Rbl = np.c_[Rw[0], -Rw[1], -Rw[2]]                              # kolumny: X=right, Y=up, Z=-fwd
    ex, ey, ez = euler_xyz(Rbl)
    sw = 36.0
    out = dict(
        rozdzielczosc=[W, H], pixel_aspect=1.0, sensor_fit='HORIZONTAL', sensor_width_mm=sw,
        lens_mm=round(fF / W * sw, 4), f_px_F17=round(fF, 2),
        shift_x=round((W / 2 - cxF) / W, 6), shift_y=round((cyF - H / 2) / W, 6),
        punkt_glowny_px_F17=[round(cxF, 2), round(cyF, 2)],
        location_z_wzgl_0=[round(cam['C'][0], 3), round(cam['C'][1], 3), round(cam['C'][2] - Z0, 3)],
        location_H_bezwzgl=[round(cam['C'][0], 3), round(cam['C'][1], 3), round(cam['C'][2], 3)],
        rotation_euler_XYZ_rad=[round(ex, 6), round(ey, 6), round(ez, 6)],
        rotation_euler_XYZ_deg=[round(math.degrees(ex), 4), round(math.degrees(ey), 4), round(math.degrees(ez), 4)],
        rotation_matrix_world=[[round(v, 7) for v in row] for row in Rbl.tolist()],
        clip_start=1.0, clip_end=5000.0,
        hfov_deg=round(2 * math.degrees(math.atan(W / 2 / fF)), 3),
        uwagi='Kamera PERSP, bez dystorsji. Uklad sceny: X = e, Y = n (uklad lokalny PL-2000/6 - 6433500 / 5664100), '
              'Z = H - 119,25 (wariant location_z_wzgl_0) albo Z = H (location_H_bezwzgl). Render w mniejszej '
              'rozdzielczosci: ta sama proporcja (resolution_percentage) - lens/shift bez zmian. '
              'Kadr F.17 jest asymetryczny wzgledem osi optycznej, dlatego shift_x/shift_y != 0.')
    return out


# ------------------------------------------------------------------------------------------------ obrazy kontrolne
COL = dict(kraw=(255, 230, 0), kraw3d=(255, 140, 0), tory=(255, 0, 255), brzeg=(0, 160, 255), inwest=(255, 0, 0),
           wydzA=(255, 0, 255), bud0=(255, 70, 70), budT=(60, 255, 60), budV=(80, 180, 255), obs=(0, 255, 255), proj=(255, 0, 0))


def layers():
    S = SITE; U = S['ulice_i_sytuacja']; out = []
    def add(nm, pts, closed=False, z=None):
        P = [list(p) for p in pts] + ([list(pts[0])] if closed else [])
        Z = [H_nmt(p[0], p[1]) for p in P] if z is None else list(z) + ([z[0]] if closed else [])
        out.append((nm, np.c_[np.array(P, float), np.array(Z, float)]))
    for o in U['krawezniki']:
        add('kraw', o['pts'], o.get('zamknieta', False))
    for o in U['krawezniki_pomiar_NMT']:
        add('kraw3d', o['pts'], False, o['z'])
    for o in U['tory_tramwajowe']:
        add('tory', o['pts'])
    for o in S['woda']['linia_brzegu']:
        add('brzeg', o['pts'])
    add('inwest', S['granice']['obszar_inwestycji']['pts'], True)
    add('wydzA', S['granice']['wydzielenie_A_mpzp']['pts'], True)
    return out


# wysokosc gornej krawedzi (attyka / gzyms): Mazowiecka 19 wg M.07; pozostale wg NMPT GUGiK (percentyl 90 dachu)
TOP_H = {'Mazowiecka 19': 140.25, 'Wybrzeze J. Slowackiego 5': 140.05, 'Wybrzeze J. Slowackiego 6': 140.05,
         'Wybrzeze J. Slowackiego 7': 140.07, 'Wybrzeze J. Slowackiego 8': 140.10, 'Wybrzeze J. Slowackiego 9': 134.1}


def buildings(only=None):
    out = []
    for b in SITE['budynki']['items']:
        nm = b['nazwa'] or b['etykieta']
        if only and nm not in only:
            continue
        H0 = b['teren_wokol_H']['srednia']
        Ht = TOP_H.get(nm, b.get('attyka_szac_H') or b['gora_szac_H'])
        out.append((nm, np.array(b['pts'], float), H0, Ht))
    return out


def draw_overlay(img, cam, key, scale, off, obs=None, width=2, bld_only=None):
    d = ImageDraw.Draw(img)
    def tr(P):
        uv, ok = project_F(densify(P, 0.5), cam, key)
        return [((x - off[0]) * scale, (y - off[1]) * scale) for x, y in uv[ok]]
    for nm, P in layers():
        q = tr(P)
        if len(q) > 1:
            d.line(q, fill=COL[nm], width=width if nm in ('inwest', 'wydzA') else max(1, width - 1))
    for nm, pts, H0, Ht in buildings(bld_only):
        P = np.vstack([pts, pts[:1]])
        d.line(tr(np.c_[P, np.full(len(P), H0)]), fill=COL['bud0'], width=max(1, width - 1))
        d.line(tr(np.c_[P, np.full(len(P), Ht)]), fill=COL['budT'], width=max(1, width - 1))
        for p in pts:
            d.line(tr(np.array([[p[0], p[1], H0], [p[0], p[1], Ht]])), fill=COL['budV'], width=1)
    if obs:
        for o in obs:
            if o['typ'] != 'pt' or o.get('wiazacy'):
                continue
            x, y = o['uvF']; X, Y = (x - off[0]) * scale, (y - off[1]) * scale
            uv, _ = project_F([o['X']], cam, key); px, py = (uv[0, 0] - off[0]) * scale, (uv[0, 1] - off[1]) * scale
            r = 6
            d.ellipse([X - r, Y - r, X + r, Y + r], outline=COL['obs'], width=2)
            d.line([(px - r, py), (px + r, py)], fill=COL['proj'], width=2); d.line([(px, py - r), (px, py + r)], fill=COL['proj'], width=2)
    return img


def legend(img, lines):
    d = ImageDraw.Draw(img)
    h = 14 * len(lines) + 8
    d.rectangle([0, img.size[1] - h, 560, img.size[1]], fill=(0, 0, 0))
    for i, (t, c) in enumerate(lines):
        d.text((6, img.size[1] - h + 4 + 14 * i), t, fill=c)


def save_jpg(img, path, max_mb=1.5):
    q = 88
    while True:
        img.save(path, quality=q, optimize=True)
        if os.path.getsize(path) <= max_mb * 1e6 or q < 50:
            break
        q -= 6


def control_images(key, cam):
    F = Image.open(FILES[key][1]).convert('RGB'); W, H = F.size
    leg = [('zolty/pomaranczowy: krawezniki (e-mapa / pomiar 3D M.02)', COL['kraw']),
           ('czerwony: obrysy budynkow - podstawa; zielony: gora (attyka/gzyms); niebieski: naroza', COL['bud0']),
           ('czerwony gruby: obszar inwestycji (M.04); magenta gruby: wydzielenie A (MPZP); niebieski: brzeg', COL['inwest']),
           ('cyjan kolko: pomiar na zdjeciu; czerwony krzyz: rzut punktu z modelu', COL['obs']),
           ('F.17.%s - kamera z model/kamery_F17.json (tools/photomatch_F17.py)' % key, (255, 255, 255))]
    sc = 2400 / W
    im = F.resize((2400, int(H * sc)), Image.LANCZOS)
    draw_overlay(im, cam, key, sc, (0, 0), OBS[key], width=2,
                 bld_only=['Mazowiecka 19', 'Mazowiecka 17', 'Wybrzeze J. Slowackiego 5', 'Wybrzeze J. Slowackiego 6',
                           'Wybrzeze J. Slowackiego 7', 'Wybrzeze J. Slowackiego 8', 'Wybrzeze J. Slowackiego 9'])
    legend(im, leg)
    p1 = IMG_DIR / ('photomatch_F17%s_nakladka.jpg' % key); save_jpg(im, p1)
    # wycinek terenu inwestycji 1:1 (pol rozdzielczosci F.17)
    crop = {'A': (2700, 1900, 4700, 2900), 'B': (2900, 1900, 6100, 3500)}[key]
    sc2 = 0.75 if key == 'A' else 0.5
    c = F.crop(crop); c = c.resize((int(c.size[0] * sc2), int(c.size[1] * sc2)), Image.LANCZOS)
    draw_overlay(c, cam, key, sc2, crop[:2], OBS[key], width=2)
    legend(c, leg)
    p2 = IMG_DIR / ('photomatch_F17%s_teren.jpg' % key); save_jpg(c, p2)
    return [str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT))]


# ------------------------------------------------------------------------------------------------ test w Blenderze
def blender_test(key, cam, bp, pct=50):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector, Euler
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:
        sc.render.engine = 'BLENDER_WORKBENCH'
        sh = sc.display.shading
        sh.light = 'FLAT'; sh.color_type = 'OBJECT'; sh.show_object_outline = True; sh.object_outline_color = (0, 0, 0)
    except Exception:
        sc.render.engine = 'CYCLES'; sc.cycles.samples = 8
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = bp['rozdzielczosc']
    sc.render.resolution_percentage = pct
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    cd = bpy.data.cameras.new('F17' + key); co = bpy.data.objects.new('F17' + key, cd); sc.collection.objects.link(co)
    cd.type = 'PERSP'; cd.sensor_fit = 'HORIZONTAL'; cd.sensor_width = bp['sensor_width_mm']; cd.lens = bp['lens_mm']
    cd.shift_x = bp['shift_x']; cd.shift_y = bp['shift_y']; cd.clip_start = bp['clip_start']; cd.clip_end = bp['clip_end']
    co.location = Vector(bp['location_z_wzgl_0']); co.rotation_mode = 'XYZ'; co.rotation_euler = Euler(bp['rotation_euler_XYZ_rad'], 'XYZ')
    sc.camera = co

    def mesh_obj(name, verts, faces, color):
        me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
        ob = bpy.data.objects.new(name, me); sc.collection.objects.link(ob); ob.color = color
        return ob

    def prism(name, pts, h0, h1, color):
        n = len(pts)
        V = [(p[0], p[1], h0 - Z0) for p in pts] + [(p[0], p[1], h1 - Z0) for p in pts]
        Fc = [list(range(n))[::-1], list(range(n, 2 * n))] + [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
        return mesh_obj(name, V, Fc, color)

    def tube(name, P, r, color):
        cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = r; cu.bevel_resolution = 1
        sp = cu.splines.new('POLY'); sp.points.add(len(P) - 1)
        for i, p in enumerate(P):
            sp.points[i].co = (p[0], p[1], p[2] - Z0 + r, 1.0)
        ob = bpy.data.objects.new(name, cu); sc.collection.objects.link(ob); ob.color = color
        return ob

    cols = {'Mazowiecka 19': (1.0, 0.25, 0.2, 1), 'Wybrzeze J. Slowackiego 5': (0.2, 0.5, 1.0, 1),
            'Wybrzeze J. Slowackiego 6': (0.2, 0.9, 0.9, 1), 'Wybrzeze J. Slowackiego 7': (0.9, 0.3, 0.9, 1),
            'Wybrzeze J. Slowackiego 8': (1.0, 0.9, 0.2, 1)}
    for nm, pts, H0, Ht in buildings(list(cols)):
        prism(nm, pts, H0 - 0.3, Ht, cols[nm])
    # teren: siatka NMT (1 m), tylko pelne oczka
    V, Fc, idx = [], [], {}
    ny, nx = NMT.shape
    for iy in range(ny):
        for ix in range(nx):
            if not np.isnan(NMT[iy, ix]):
                idx[(iy, ix)] = len(V); V.append((NE0 + ix * NK, NN0 + iy * NK, NMT[iy, ix] - Z0 - 0.05))
    for iy in range(ny - 1):
        for ix in range(nx - 1):
            q = [(iy, ix), (iy, ix + 1), (iy + 1, ix + 1), (iy + 1, ix)]
            if all(k in idx for k in q):
                Fc.append([idx[k] for k in q])
    mesh_obj('teren_NMT', V, Fc, (0.55, 0.55, 0.5, 1))
    for i, o in enumerate(SITE['ulice_i_sytuacja']['krawezniki_pomiar_NMT']):
        tube('kraweznik_%d' % i, np.c_[np.array(o['pts']), np.array(o['z'])], 0.12, (1.0, 0.55, 0.0, 1))
    for nm, c in (('obszar_inwestycji', (1, 0, 0, 1)), ('wydzielenie_A_mpzp', (1, 0, 1, 1))):
        pts = SITE['granice'][nm]['pts'] + [SITE['granice'][nm]['pts'][0]]
        P = densify(np.c_[np.array(pts), [H_nmt(*p) for p in pts]], 1.0)
        P[:, 2] = [H_nmt(p[0], p[1]) for p in P]
        tube(nm, P, 0.18, c)
    tmp = IMG_DIR / ('_render_F17%s.png' % key)
    sc.render.filepath = str(tmp)
    bpy.ops.render.render(write_still=True)
    # kontrola numeryczna: Blender world_to_camera_view vs model otworkowy
    dmax = 0.0; W, H = bp['rozdzielczosc']
    pts = [o['X'] for o in OBS[key] if o['typ'] == 'pt'] + [[p[0], p[1], H0] for _, pp, H0, _ in buildings(list(cols)) for p in pp]
    for X in pts:
        v = world_to_camera_view(sc, co, Vector((X[0], X[1], X[2] - Z0)))
        xb, yb = v.x * W, (1 - v.y) * H
        uv, _ = project_F([X], cam, key)
        dmax = max(dmax, float(np.hypot(xb - uv[0, 0], yb - uv[0, 1])))
    # zlozenie z fotografia
    R = Image.open(tmp).convert('RGBA'); os.remove(tmp)
    ph = Image.open(FILES[key][1]).convert('RGB').resize(R.size, Image.LANCZOS)
    a = np.asarray(R).astype(float) / 255.0; p = np.asarray(ph).astype(float) / 255.0
    al = a[..., 3:4] * 0.5
    comp = p * (1 - al) + a[..., :3] * al
    out = Image.fromarray((np.clip(comp, 0, 1) * 255).astype(np.uint8))
    full = out.resize((2400, int(out.size[1] * 2400 / out.size[0])), Image.LANCZOS)
    legend(full, [('Render testowy Blender (bpy, Workbench) kamera F.17.%s: bryly Maz. 19 i Wybrz. Slowackiego 5-8,' % key, (255, 255, 255)),
                  ('teren NMT, krawezniki pomiarowe (pomaranczowe), obszar inwestycji (czerwony), wydzielenie A (magenta); alfa 50%', (255, 255, 255))])
    p1 = IMG_DIR / ('photomatch_F17%s_render_test.jpg' % key); save_jpg(full, p1)
    crop = {'A': (2700, 1900, 4700, 2900), 'B': (3300, 1950, 6300, 3450)}[key]
    f = pct / 100.0
    c = out.crop(tuple(int(v * f) for v in crop))
    if c.size[0] > 1600:
        c = c.resize((1600, int(c.size[1] * 1600 / c.size[0])), Image.LANCZOS)
    p2 = IMG_DIR / ('photomatch_F17%s_render_test_teren.jpg' % key); save_jpg(c, p2)
    return dict(silnik=sc.render.engine, rozdzielczosc_renderu=[int(W * f), int(H * f)],
                max_roznica_blender_vs_model_px=round(dmax, 3), obrazy=[str(p1.relative_to(ROOT)), str(p2.relative_to(ROOT))])


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kadr', action='store_true', help='przelicz transformacje M.10 -> F.17 z obrazow')
    ap.add_argument('--render', action='store_true', help='test w Blenderze (bpy) + obrazy kontrolne renderu')
    ap.add_argument('--no-img', action='store_true', help='bez obrazow kontrolnych')
    a = ap.parse_args()
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    if a.kadr:
        for k in 'AB':
            KADR[k].update(wyznacz_kadr(k)); print('kadr', k, KADR[k])
    prev = json.load(open(OUT_JSON, encoding='utf-8')) if OUT_JSON.exists() else {}
    out = dict(
        opis='Kamery (photomatch) zdjec F.17.A i F.17.B - model otworkowy, uklad lokalny e = Y2000 - 6433500, '
             'n = X2000 - 5664100, H w PL-EVRF2007-NH; generator tools/photomatch_F17.py; opis docs/60_wizualizacje/photomatch_F17.md',
        konwencje=dict(
            piksele='wspolrzedne ciagle: lewy gorny rog obrazu = (0,0), srodek piksela i = i+0,5; y w dol',
            M10='M.10 = panorama DJI 8000x5632 zmniejszona do 4000x2816; punkt glowny (2000, 1408)',
            kadr='F.17 = s * M.10 + t (bez obrotu i deformacji)',
            yaw='azymut siatki (od osi +n, zgodnie z ruchem wskazowek zegara) osi optycznej',
            pitch='kat osi optycznej nad poziomem (+ w gore)', roll='obrot wokol osi optycznej (+ = obraz obrocony przeciwnie do zegara)',
            rzut='[x, y, z]_kam = R (P - C); u = cx + f x/z; v = cy + f y/z (R: wiersze = prawo, dol, przod)',
            z_blender='z = H - 119,25 (+-0,00 = 119,25 m n.p.m.)'),
        kamery={})
    for key in 'AB':
        cam, std, cov, loo = solve_robust(key)
        rows, rp, rl = stats(key, cam, OBS[key])
        man = [r for r in rows if not r['id'].startswith('wiaz_')]
        ties = [r for r in rows if r['id'].startswith('wiaz_') and r['uzyty']]
        man_pt = [r['blad_px'] for r in man if r['typ'] == 'pt' and r['uzyty']]
        bp = blender_params(cam, key)
        R = rot_matrix(cam['yaw'], cam['pitch'], cam['roll'])
        k = KADR[key]
        entry = dict(
            zdjecie=str(FILES[key][1].relative_to(ROOT)), klatka_M10=str(FILES[key][0].relative_to(ROOT)),
            exif=EXIF[key],
            kadr_M10_do_F17=dict(s=k['s'], tx=k['tx'], ty=k['ty'], rms_px=k['rms_px'], n_latek=k['n'],
                                 F17_rozmiar=[k['W'], k['H']],
                                 okno_F17_w_panoramie_8000x5632=[round(-k['tx'] / k['s'] * 2, 1), round(-k['ty'] / k['s'] * 2, 1),
                                                                round((k['W'] - k['tx']) / k['s'] * 2, 1), round((k['H'] - k['ty']) / k['s'] * 2, 1)],
                                 uwaga='F.17 = panorama 8000x5632 powiekszona x1,25 i przycieta (M.10 = panorama x0,5, stad s = 2,5)'),
            pinhole=dict(f_px_M10=round(cam['f'], 2), f_px_F17=round(cam['f'] * k['s'], 2), f_px_panorama8000=round(cam['f'] * 2, 2),
                         cx_cy_px_M10=list(PP_M), cx_cy_px_F17=bp['punkt_glowny_px_F17'], k1=0.0,
                         rozmiar_F17=[k['W'], k['H']],
                         hfov_panorama8000_deg=round(2 * math.degrees(math.atan(2000 / cam['f'])), 2),
                         vfov_panorama8000_deg=round(2 * math.degrees(math.atan(1408 / cam['f'])), 2),
                         hfov_F17_deg=bp['hfov_deg'],
                         ogniskowa_ekw_35mm_pozioma=round(36 * cam['f'] / 4000, 2)),
            poza=dict(C_e_n_H=[round(v, 3) for v in cam['C']], C_PL2000=[round(cam['C'][0] + 6433500, 3), round(cam['C'][1] + 5664100, 3)],
                      yaw_deg=round(cam['yaw'], 4), pitch_deg=round(cam['pitch'], 4), roll_deg=round(cam['roll'], 4),
                      R_swiat_do_kamery=[[round(v, 7) for v in row] for row in R.tolist()],
                      odchylenia_std={kk: round(v, 3) for kk, v in std.items()},
                      wysokosc_nad_startem_wg_EXIF=round(cam['C'][2] - EXIF[key]['rel_alt'], 2),
                      roznica_DJI_abs_alt_m=round(EXIF[key]['abs_alt_dji'] - cam['C'][2], 2),
                      roznica_od_GPS_m=[round(cam['C'][0] - GPS[key][0], 2), round(cam['C'][1] - GPS[key][1], 2)]),
            bledy=dict(rms_punkty_reczne_px_F17=round(float(np.sqrt(np.mean(np.square(man_pt)))), 2) if man_pt else None,
                       rms_linie_px_F17=round(rl, 2) if rl else None,
                       rms_punkty_wiazace_px_F17=round(float(np.sqrt(np.mean(np.square([r['blad_px'] for r in ties])))), 2) if ties else None,
                       rms_wszystkie_punkty_px_F17=round(rp, 2) if rp else None,
                       loo_punkty_reczne_px_F17=loo,
                       rms_loo_px_F17=round(float(np.sqrt(np.mean(np.square([l['blad_px'] for l in loo])))), 2) if loo else None,
                       prog_wymagany_px=round(0.003 * k['W'], 1)),
            obserwacje=[dict(o, **{kk: v for kk, v in r.items() if kk not in ('id', 'typ')}) for o, r in zip(OBS[key], rows)],
            blender=bp)
        if not a.no_img:
            entry['obrazy_kontrolne'] = control_images(key, cam)
        if a.render:
            entry['test_blender'] = blender_test(key, cam, bp)
        elif prev.get('kamery', {}).get(key, {}).get('test_blender'):
            entry['test_blender'] = prev['kamery'][key]['test_blender']
        out['kamery'][key] = entry
        print(key, 'RMS reczne %.2f px, linie %s px, wiazace %s px, LOO %s px' % (
            entry['bledy']['rms_punkty_reczne_px_F17'] or -1, entry['bledy']['rms_linie_px_F17'],
            entry['bledy']['rms_punkty_wiazace_px_F17'], entry['bledy']['rms_loo_px_F17']))
        print('   blender', {kk: bp[kk] for kk in ('lens_mm', 'shift_x', 'shift_y', 'location_z_wzgl_0', 'rotation_euler_XYZ_deg')})
    a_, b_ = out['kamery']['A']['poza'], out['kamery']['B']['poza']
    out['kontrola_spojnosci'] = dict(
        roznica_wysokosci_kamer_m=round(a_['C_e_n_H'][2] - b_['C_e_n_H'][2], 2),
        roznica_wysokosci_wg_EXIF_rel_alt_m=round(EXIF['A']['rel_alt'] - EXIF['B']['rel_alt'], 2),
        wysokosc_startu_drona_A_B_m=[a_['wysokosc_nad_startem_wg_EXIF'], b_['wysokosc_nad_startem_wg_EXIF']],
        przesuniecie_DJI_abs_alt_A_B_m=[a_['roznica_DJI_abs_alt_m'], b_['roznica_DJI_abs_alt_m']])
    with open(OUT_JSON, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print('zapisano', OUT_JSON)


if __name__ == '__main__':
    main()
