# -*- coding: utf-8 -*-
"""Model 3D projektowanego budynku UMWD i Sejmiku Województwa Dolnośląskiego („BRAMA I LATARNIA”)
– Blender (bpy 5.2) / Cycles.

Źródło prawdy: ``model/koncepcja.json`` – czytany w czasie działania (obrysy brył, łuk narożnika, kondygnacje,
rzędne, cofnięcia i wnęki, rytmy i materiały elewacji, kamery). Liczby, których w JSON nie ma (np. wysokości okien
korony, głębokości płycin), są stałymi w ``ZALOZENIA`` z odwołaniem do opisu ``docs/20_koncepcja/koncepcja_wybrana.md``.

Kolekcje (dzieci kolekcji ``BUDYNEK``):

* ``wieza``      – Wieża Sejmiku: wielki porządek granitowych filarów 1,05 m co 2,70 m (+4,80…+37,20), okna
                   1,65 × 2,45 m z ościeżem 0,60 m i płycinami z metalu, kordon granitowy +19,80–20,85,
                   kondygnacja 6 „cienia” (szkło 0,40 m za licem), korona S; łuk R 14: podcień (szklenie R 11)
                   z kolumnami co 15°, pasma ceramiczne 1,30 m + okna wstęgowe 2,45 m, korona z lamelami
                   0,25 × 0,60 m co 0,90 m przed szkłem; napis w nadprożu Bramy Mostowej;
* ``skrzydlo``   – Skrzydło Mazowieckie: porządek kamieniczny (oś 2,025 m, filar 0,825, okna 1,2 × 2,4 m), cztery
                   „posesje” M1–M4 (odcień ceramiki, relief filarów, faktura), szczeliny między posesjami, cokół
                   z witrynami i naświetlem, kordon, gzyms-attyka, brama ogrodowa 4,05 m, dziób NW;
* ``segment``    – Segment Wybrzeża (ten sam porządek; brama garażu, ściana pd. z reliefem);
* ``dachy``      – dachy płaskie za attyką: BIPV (ciemne moduły) + pas zieleni ekstensywnej; taras segmentu;
* ``wnetrza``    – stropy, sufity z lampami liniowymi, ścianki, biurka, rolety (biura); hol parteru i korona
                   Sejmiku z ciepłym, bogatszym wnętrzem;
* ``zagospodarowanie_bliskie`` – posadzki granitowe (Plac Mostowy, podcień, brama, opaski), ścieżki ogrodu,
                   trawnik przebudowany wokół posadzek, drzewa zachowane i nowe, ława, sylwetki ludzi (opcja).

Układ: X = e, Y = n (lokalny ``site.json``); Z = H − 119,25 (jak ``context.py``). Budynek: ±0,00 = 119,30 m n.p.m.,
więc Z = z_wzgl + 0,05 (przesunięcie stosowane przy tworzeniu siatek).

Użycie::

    import sys; sys.path.insert(0, '/home/user/aihouse/umwd/src')
    from umwd.render import blib, context, budynek3d
    sc = blib.reset()
    kon = context.build_context(sc, {'pora_roku': 'jesien', 'obszar_inwestycji': 'pusty'})
    bud = budynek3d.build_building(sc, {'kontekst': kon})

Dokumentacja: ``docs/60_wizualizacje/budynek_3d.md``.
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
import zlib
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import bpy  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon, LineString, Point  # noqa: E402
from shapely.geometry.polygon import orient  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from umwd.render import blib  # noqa: E402
from umwd.render.blib import NodeBuilder  # noqa: E402

UMWD = Path(__file__).resolve().parents[3]
KONCEPCJA = UMWD / 'model' / 'koncepcja.json'
SASIEDZI = UMWD / 'model' / 'sasiedzi.json'
SITE_JSON = UMWD / 'model' / 'site.json'
Z0_KONTEKST = 119.25          # H odpowiadające Z = 0 w context.py

# ============================================================================================== założenia
# Wartości NIEOBECNE w koncepcja.json (projektowe, wg koncepcja_wybrana.md §4, §8 lub dobór wizualny).
ZALOZENIA = dict(
    z_podstawy=-1.6,            # spód elementów elewacji (poniżej terenu – brak szczelin przy terenie)
    gzyms_wysieg=0.30,          # wysięg gzymsu skrzydła/segmentu „w obrysie” → lico trzonu 0,30 m za obrysem (§8)
    gzyms_wys=1.40,             # gzyms-attyka granitowy 1,40 m (fryz + gzyms), spód części wysuniętej z JSON (§8)
    kordon_skrzydla_h=0.35,     # kordon granitowy 0,35 m (§8)
    m1_pierwsza_os_cofn=0.30,   # M1: pierwsza oś cofnięta 0,30 m (§8)
    fuga_posesji_szer=0.20,     # szczelina między posesjami 0,20 m, cofnięta 0,15 m (§8)
    fuga_posesji_cofn=0.15,
    plycina_wiezy_gl=0.25,      # płycina metalowa wieży – głębokość lica płyciny za licem filara (dobór)
    parter_szklo_wieza=0.35,    # witryny parteru wieży – głębokość szkła (dobór; jak ościeże skrzydła)
    parter_szklo_skrzydlo=0.30, # witryny cokołu skrzydła/segmentu
    korona_parapet=0.70,        # parapet okien korony nad posadzką S (+28,00; tools/elewacje.py)
    attyka_obrobka=0.15,        # obróbka attyki z ciemnego metalu 0,15 m (§8)
    luk_slupy_szer=0.60,        # kolumny podcienia na łuku: 0,60 m stycznie (tools/elewacje.py), osie na R 13,5
    luk_slupy_gl=0.60,          # … i 0,60 m promieniowo (dobór)
    luk_slupek_co=1.35,         # słupki okien wstęgowych łuku co 1,35 m (moduł; tools/elewacje.py)
    wieza_parapet=0.90,         # parapet okien wieży 0,90 m nad posadzką (tools/elewacje.py; kond. 5 – nad kordonem)
    kond6_szklo=(0.30, 3.40),   # kond. 6: szkło od F+0,30 do F+3,40 (tools/elewacje.py)
    korona_wypelnienie_gl=0.10, # wypełnienie granitowe korony między filarami – cofnięcie (dobór)
    korona_okno_hala=5.0, korona_rygiel_hala=2.5,          # okna holu/hali 1,65 × 5,0 m (§8; elewacje pn. i wsch.)
    korona_okno_komisje=4.2, korona_rygiel_komisje=2.6,    # okna komisji/klubów 1,65 × 4,20 m (§8)
    korona_typ={'N': 'hala', 'E': 'hala', 'W': 'komisje', 'S': 'komisje_lamele'},   # wg tools/elewacje.py
    korona_lamele=(32.9, 35.8, 0.25, 0.42),   # pas lameli nad oknami komisji od dziedzińca: z0, z1, szer., rozstaw
    czerpnie_kond1_S=(2.0, 12.0),             # żaluzje czerpni zamiast okien kond. 1, elewacja pd., u 2–12 m
    wejscie_rowerowni_S=(3.0, 4.6),           # drzwi rowerowni w elewacji pd. (u)
    gzyms_wysieg_ulica=0.0,     # rewizja 17.11: na elewacjach < 0,30 m od granicy gzyms bez wysięgu …
    fryz_cofniecie=0.15,        # … a cień daje fryz cofnięty o 0,15 m pod gzymsem
    gzyms_wysieg_pn=0.25,       # elewacja pn. skrzydła (dziób) – wysięg maks. 0,25 m
    brama_garazu_v=(-4.4, -0.4),  # rewizja 17.11 (weryfikacja K-2/I-1): brama 4,0 m przy ścianie pn. segmentu
    brama_garazu_prog_npm=119.10,
    drzwi_segmentu=((0.75, 1.95), (2.55, 3.55), (4.15, 5.15)),   # trafo, rozdzielnia nn, odpady – od narożnika pd.
    drzwi_segmentu_h=2.40,
    napis='SEJMIK WOJEWÓDZTWA DOLNOŚLĄSKIEGO',   # napis w granitowym nadprożu Bramy Mostowej (§3 p.10)
    napis_h=0.40,
    glebokosc_pokoju=6.10,      # głębokość pokoi (trakt) – tylna ściana wnętrz (§6)
    brama_garazu_h=4.00,        # wysokość bramy garażu (tools/elewacje.py)
    nos_wejscie_szer=3.60,      # wejście konferencyjne w dziobie NW – szerokość wnęki (dobór)
    drzwi_w=1.90, drzwi_h=2.70,  # drzwi wejść (dobór)
)

# RAL → sRGB (wartości przybliżone, tablice RAL)
RAL_SRGB = {'8019': (61, 54, 53), '7016': (56, 62, 66), '9002': (215, 215, 205)}


# ============================================================================================== kolory NCS
def ncs_srgb(kod):
    """Przybliżona konwersja NCS (np. 'S 1505-Y20R', 'S 1502-Y', 'S 2000-N') → sRGB 0–255 (algorytm wg w3color.js).
    Dokładność ok. ±5 jednostek – wystarczająca do wizualizacji; barwy docelowe trzeba sprawdzić na wydruku."""
    t = kod.upper().replace('NCS', '').replace(' ', '').lstrip('S')
    m = re.match(r'^(\d{2})(\d{2})-(N|[YRBG])(\d{2})?([YRBG])?$', t)
    if not m:
        raise ValueError('nieznany kod NCS: %s' % kod)
    black, chroma = int(m.group(1)), int(m.group(2))
    bc = m.group(3)
    pc = int(m.group(4) or 0)
    if bc == 'N':
        g = int((1 - black / 100) * 255)
        return (g, g, g)
    black = 1.05 * black - 5.25
    if bc == 'Y' and pc <= 60:
        red = 1.0
    elif (bc == 'Y' and pc > 60) or (bc == 'R' and pc <= 80):
        f = pc - 60 if bc == 'Y' else pc + 40
        red = (math.sqrt(14884 - f * f) - 22) / 100
    elif (bc == 'R' and pc > 80) or bc == 'B':
        red = 0.0
    else:
        f = pc - 170
        red = (math.sqrt(33800 - f * f) - 70) / 100
    if bc == 'Y' and pc <= 80:
        blue = 0.0
    elif (bc == 'Y' and pc > 80) or (bc == 'R' and pc <= 60):
        f = (pc - 80) + 20.5 if bc == 'Y' else (pc + 20) + 20.5
        blue = (104 - math.sqrt(11236 - f * f)) / 100
    elif (bc == 'R' and pc > 60) or (bc == 'B' and pc <= 80):
        f = (pc - 60) - 60 if bc == 'R' else (pc + 40) - 60
        blue = (math.sqrt(10000 - f * f) - 10) / 100
    elif (bc == 'B' and pc > 80) or (bc == 'G' and pc <= 40):
        f = (pc - 80) - 131 if bc == 'B' else (pc + 20) - 131
        blue = (122 - math.sqrt(19881 - f * f)) / 100
    else:
        blue = 0.0
    if bc == 'Y':
        green = (85 - 17 / 20 * pc) / 100
    elif bc == 'R' and pc <= 60:
        green = 0.0
    elif bc == 'R':
        f = (pc - 60) + 35
        green = (67.5 - math.sqrt(5776 - f * f)) / 100
    elif bc == 'B' and pc <= 60:
        f = pc - 68.5
        green = (6.5 + math.sqrt(7044.5 - f * f)) / 100
    elif (bc == 'B' and pc > 60) or (bc == 'G' and pc <= 60):
        green = 0.9
    else:
        green = (90 - (pc - 60) / 8) / 100
    f1 = (red + green + blue) / 3
    r2 = (f1 - red) * (100 - chroma) / 100 + red
    g2 = (f1 - green) * (100 - chroma) / 100 + green
    b2 = (f1 - blue) * (100 - chroma) / 100 + blue
    mx = max(r2, g2, b2)
    k = (100 - black) / 100 / mx
    return tuple(int(max(0, min(255, c * k * 255))) for c in (r2, g2, b2))


def srgb_lin(c):
    """sRGB 0–255 → liniowe 0–1."""
    out = []
    for v in c:
        v = v / 255.0
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def _liczby(txt):
    """Liczby z tekstu w zapisie polskim (przecinek dziesiętny; minus − lub -)."""
    t = txt.replace('−', '-').replace('–', ' ').replace('…', ' ')
    return [float(x.replace(',', '.')) for x in re.findall(r'-?\d+(?:,\d+)?', t)]


def _hash01(*a):
    return (zlib.crc32(repr(a).encode()) % 100003) / 100003.0


# ============================================================================================== specyfikacja
class Spec:
    """Odczyt i interpretacja ``koncepcja.json``."""

    def __init__(self, path=KONCEPCJA):
        K = json.load(open(path, encoding='utf-8'))
        self.K = K
        self.zero = float(K['meta']['zero']['wzgl_0_00_m_npm'])
        self.DZ = self.zero - Z0_KONTEKST
        self.B = {b['id']: b for b in K['bryly']}
        self.uv = self._uklad(K['meta']['uklad_pomocniczy_wiezy'], 'u', 'v')
        self.sd = self._uklad(K['meta']['uklad_pomocniczy_skrzydla'], 's', 'd')
        # kondygnacje nadziemne
        self.kond = [k for k in K['kondygnacje'] if k['posadzka_wzgl'] >= 0]
        sg = K['siatka']
        self.t_stropu = {'W': _liczby(sg['wieza']['strop'])[0], 'M': _liczby(sg['skrzydlo']['strop'])[0],
                         'S': _liczby(sg['segment']['strop'])[0]}
        E = K['elewacje']
        self.E = E
        self.osc = K['cofniecia_wneki']['oscieza']
        # dachy (wysokości względne)
        bw, bm, bs = self.B['W']['dach'], self.B['M']['dach'], self.B['S']['dach']
        self.dach = {
            'W': dict(pokrycie=bw['najnizszy_pkt_pokrycia']['wzgl'], pokrycie_max=bw['najwyzszy_pkt_pokrycia']['wzgl'],
                      attyka=bw['attyka']['wzgl']),
            'M': dict(pokrycie=bm['najnizszy_pkt_pokrycia']['wzgl'], pokrycie_max=bm['najwyzszy_pkt_pokrycia']['wzgl'],
                      attyka=bm['gzyms_attyka']['wzgl'], strop=bm['strop_wierzch']),
            'S': dict(pokrycie=bs['taras_wykonczenie']['wzgl'], pokrycie_max=bs['taras_wykonczenie']['wzgl'],
                      attyka=bs['attyka']['wzgl'], strop=bs['strop_wierzch']),
        }
        self.sala_h = K['kondygnacja_sejmiku']['sala']['wys_w_swietle_m']
        self.antresola = K['kondygnacja_sejmiku']['antresola']['wzgl']
        # linie skrzydła (m n.p.m. → wzgl.)
        L = E['skrzydlo']['linie']
        self.linie = {k.replace('_npm', ''): v - self.zero for k, v in L.items()}
        # kordon wieży – z opisu materiału G („kordon +19,80–20,85”)
        g = next(m for m in E['materialy'] if m['id'] == 'G')['gdzie']
        mm = re.search(r'kordon\s*\+?(\d+,\d+)\s*[–-]\s*(\d+,\d+)', g)
        self.kordon_wiezy = (float(mm.group(1).replace(',', '.')), float(mm.group(2).replace(',', '.')))
        # łuk
        self.luk = self.B['W']['luk']
        ls = sg['wieza']['luk']
        self.luk_slupy_deg = float(re.search(r'co\s*(\d+)\s*°', ls).group(1))
        self.luk_slupy_R = _liczby(ls.split('R =')[1])[0]
        # „pasma ceramiczne 1,30 m + okna wstęgowe 2,45 m” → [1.30, 2.45]
        lp = [x for x in _liczby(E['luk']['1-6']) if x > 0.5]
        self.luk_pas, self.luk_okno = lp[0], lp[1]
        la = _liczby(E['luk']['S'])
        self.lamela = (la[0], la[1], la[2])          # szer. × głęb., rozstaw
        self.podcien_R = self.luk['R_podcien_parter']
        self.szyba_korony_R = self.luk['R_szyb_korony']
        # cofnięcia
        CW = K['cofniecia_wneki']
        self.podcien = Polygon(CW['podcien_Brama_Mostowa']['obrys_ccw']).buffer(0)
        self.podcien_gl = CW['podcien_Brama_Mostowa']['glebokosc_m']
        self.brama = Polygon(CW['brama_ogrodowa']['obrys_ccw']).buffer(0)
        self.brama_h = CW['brama_ogrodowa']['wysokosc_m']
        self.wneki = []
        for k, w in CW.items():
            if not k.startswith('wneka_'):
                continue
            opis = w.get('elewacja') or w.get('miejsce') or ''
            self.wneki.append(dict(id=k, opis=opis, gl=w['glebokosc_m']))
        # materiały – barwy
        self.ncs = {}
        for m in E['materialy']:
            if m['id'] == 'G':
                self.ncs['granit'] = m['NCS']
            elif m['id'] == 'C':
                for k, v in m['NCS'].items():
                    self.ncs['cer_' + k] = v
            elif m['id'] == 'Me':
                self.ral_metal = re.search(r'(\d{4})', m['RAL']).group(1)
        self.szklo = E['szklo']
        # rampa (brama garażu w segmencie)
        rw = K['podziemie']['rampa']['wjazd']
        vv = _liczby(rw.split(' v ')[-1]) if ' v ' in rw else [-4.1, -10.1]
        self.brama_garazu_v = (min(vv), max(vv))
        self.kamery = K['kamery']

    @staticmethod
    def _uklad(d, a, b):
        """Parsuje wzory 'e = e0 + k·a − k·b' → macierz przekształcenia."""
        def wsp(expr):
            s = expr.replace('−', '-').replace(' ', '')
            terms = re.findall(r'([+-]?[\d,]+)(·[a-z])?', s)
            c0, ca, cb = 0.0, 0.0, 0.0
            for num, var in terms:
                v = float(num.replace(',', '.'))
                if not var:
                    c0 = v
                elif var[1] == a:
                    ca = v
                elif var[1] == b:
                    cb = v
            return c0, ca, cb
        e0, ea, eb = wsp(d['e'])
        n0, na, nb = wsp(d['n'])
        A = np.array([[ea, eb], [na, nb]])
        return dict(o=np.array([e0, n0]), A=A, Ai=np.linalg.inv(A))

    def do_uv(self, e, n, uk=None):
        uk = uk or self.uv
        return tuple(uk['Ai'] @ (np.array([e, n]) - uk['o']))

    def z_uv(self, u, v, uk=None):
        uk = uk or self.uv
        return tuple(uk['o'] + uk['A'] @ np.array([u, v]))

    NAZWY_BRYL = {'W': 'wieza', 'M': 'skrzydlo', 'S': 'segment'}

    def kondygnacje(self, bryla):
        """Lista kondygnacji nadziemnych bryły: dict(nazwa, F, H, sufit (spód stropu nad), Fn (posadzka wyżej
        lub pokrycie dachu)). Obsługuje oba formaty JSON: ``zakres`` jako tekst ('all'/'wieza') lub lista brył,
        strop jako ``strop_wierzch_wzgl`` (kondygnacji wyżej) lub ``strop_nad`` (z polami ``spod_*``)."""
        nm = self.NAZWY_BRYL[bryla]

        def w_zakresie(z):
            if isinstance(z, str):
                return z in ('all', 'calosc') or z == nm
            return nm in z or 'calosc' in z
        ks = [k for k in self.kond if w_zakresie(k['zakres'])]
        out = []
        t = self.t_stropu[bryla]
        klucze = {'W': ('spod_wieza', 'wieza_spod'), 'M': ('spod_skrzydlo', 'dach_skrzydla_spod', 'skrzydlo_spod'),
                  'S': ('spod_segment', 'dach_segmentu_spod', 'segment_spod', 'spod_wieza')}[bryla]
        for i, k in enumerate(ks):
            F = k['posadzka_wzgl']
            ostatnia = i + 1 >= len(ks)
            Fn = self.dach[bryla]['pokrycie'] if ostatnia else ks[i + 1]['posadzka_wzgl']
            sufit = None
            so = k.get('strop_nad')
            if isinstance(so, dict):
                for kk in klucze:
                    if kk in so:
                        sufit = so[kk]
                        break
                if sufit is None:
                    w = so.get('wierzch') or so.get('wieza_wierzch')
                    if w is not None:
                        sufit = w - t
            elif isinstance(k.get('dach'), dict):
                sufit = k['dach'].get('rusz_spod')
            if sufit is None:
                if not ostatnia and 'strop_wierzch_wzgl' in ks[i + 1]:
                    sufit = ks[i + 1]['strop_wierzch_wzgl'] - t
                elif bryla == 'W':
                    sufit = F + self.sala_h
                else:
                    sufit = self.dach[bryla]['strop'] - t
            out.append(dict(nazwa=k['kondygnacja'], F=F, H=k['wysokosc_kondygnacji'], sufit=sufit, Fn=Fn))
        return out

    def barwa(self, klucz):
        if klucz == 'metal':
            return srgb_lin(RAL_SRGB.get(self.ral_metal, (61, 54, 53)))
        return srgb_lin(ncs_srgb(self.ncs[klucz]))


# ============================================================================================== obrysy i biegi elewacji
def oczysc_obrys(pts, tol=0.01):
    """Usuwa duplikaty, „kolce” (zawrócenia), wierzchołki współliniowe; orientacja CCW."""
    P = [tuple(map(float, p)) for p in pts]
    out = []
    for p in P:
        if not out or math.dist(p, out[-1]) > tol:
            out.append(p)
    if len(out) > 1 and math.dist(out[0], out[-1]) <= tol:
        out.pop()
    zm = True
    while zm and len(out) > 3:
        zm = False
        n = len(out)
        for i in range(n):
            a, b, c = out[i - 1], out[i], out[(i + 1) % n]
            if math.dist(a, c) <= tol:              # kolec a→b→a
                for j in sorted([i, (i + 1) % n], reverse=True):
                    out.pop(j)
                zm = True
                break
            h0 = math.atan2(b[1] - a[1], b[0] - a[0])
            h1 = math.atan2(c[1] - b[1], c[0] - b[0])
            d = abs(math.degrees((h1 - h0 + math.pi) % (2 * math.pi) - math.pi))
            if d > 175.0 or d < 0.3:
                out.pop(i)
                zm = True
                break
    A = sum(out[i][0] * out[(i + 1) % len(out)][1] - out[(i + 1) % len(out)][0] * out[i][1] for i in range(len(out)))
    return out if A > 0 else out[::-1]


def _okrag(P):
    """Dopasowanie okręgu (Kasa) → (cx, cy, R, max_odchyłka)."""
    P = np.asarray(P, float)
    A = np.c_[2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))]
    b = (P ** 2).sum(1)
    c, *_ = np.linalg.lstsq(A, b, rcond=None)
    cx, cy = c[0], c[1]
    R = math.sqrt(c[2] + cx * cx + cy * cy)
    d = np.abs(np.hypot(P[:, 0] - cx, P[:, 1] - cy) - R)
    return cx, cy, R, float(d.max())


class Bieg:
    """Bieg elewacji: łamana (prosta lub gęsto teselowany łuk) z parametryzacją długością s i odsunięciem t
    (t > 0 na zewnątrz, t < 0 do wnętrza). Wierzchołki przesuwane wzdłuż wektorów ukośnych (miter) – elementy
    sąsiednich biegów stykają się bez szczelin i nakładek widocznych z zewnątrz."""

    def __init__(self, pts, miters, luk=None, idx=0):
        self.P = np.asarray(pts, float)
        self.Mi = np.asarray(miters, float)
        d = self.P[1:] - self.P[:-1]
        ln = np.hypot(d[:, 0], d[:, 1])
        self.cum = np.r_[0.0, np.cumsum(ln)]
        self.L = float(self.cum[-1])
        self.T = d / ln[:, None]
        self.N = np.c_[self.T[:, 1], -self.T[:, 0]]
        self.luk = luk                 # (cx, cy, R) dla łuku
        self.krzywy = luk is not None or len(self.P) > 2
        self.idx = idx
        self.pokrycie = []             # [(s0, s1, z_pokrycia)]
        self.nazwa = ''
        az = math.degrees(math.atan2(self.N.mean(0)[0], self.N.mean(0)[1])) % 360
        self.az_normalnej = az

    def _seg(self, s):
        i = int(np.searchsorted(self.cum, s, side='right') - 1)
        i = max(0, min(len(self.P) - 2, i))
        l = self.cum[i + 1] - self.cum[i]
        f = 0.0 if l < 1e-12 else (s - self.cum[i]) / l
        return i, f

    def pt(self, s, t=0.0):
        i, f = self._seg(s)
        A = self.P[i] + self.Mi[i] * t
        B = self.P[i + 1] + self.Mi[i + 1] * t
        return A + (B - A) * f

    def normalna(self, s):
        i, _ = self._seg(s)
        return self.N[i]

    def styczna(self, s):
        i, _ = self._seg(s)
        return self.T[i]

    def probki(self, s0, s1, maks=None):
        ss = [s0] + [c for c in self.cum if s0 + 1e-6 < c < s1 - 1e-6] + [s1]
        if maks:
            out = [ss[0]]
            for a, b in zip(ss[:-1], ss[1:]):
                n = max(1, int(math.ceil((b - a) / maks)))
                out += [a + (b - a) * k / n for k in range(1, n + 1)]
            ss = out
        return ss

    def zakres_z_polygonu(self, poly, t_test=-0.6, krok=0.05):
        """Przedziały s, w których punkty pt(s, t_test) leżą w wielokącie."""
        out, cur = [], None
        ss = np.arange(0.0, self.L + 1e-9, krok)
        for s in ss:
            p = self.pt(s, t_test)
            w = poly.contains(Point(p[0], p[1]))
            if w and cur is None:
                cur = s
            if not w and cur is not None:
                out.append((cur, s - krok))
                cur = None
        if cur is not None:
            out.append((cur, self.L))
        return [(a, b) for a, b in out if b - a > 0.2]


def biegi_obrysu(pts, luki_json=(), dlugi=2.0, deg=0.5):
    """Dzieli obrys na biegi: krawędzie ≥ ``dlugi`` → biegi proste; ciągi krótkich krawędzi → biegi krzywe
    (łuki: dopasowanie okręgu/łuk z JSON i ponowna teselacja co ``deg`` stopni). Zwraca listę Bieg."""
    P = oczysc_obrys(pts)
    n = len(P)
    L = [math.dist(P[i], P[(i + 1) % n]) for i in range(n)]
    dl = [l >= dlugi for l in L]
    start = next(i for i in range(n) if dl[i] and not dl[i - 1]) if not all(dl) else 0
    if all(dl):
        start = 0
    grupy, i, cnt = [], start, 0
    while cnt < n:
        if dl[i % n]:
            grupy.append([i % n])
            i += 1
            cnt += 1
        else:
            g = []
            while cnt < n and not dl[i % n]:
                g.append(i % n)
                i += 1
                cnt += 1
            grupy.append(g)
    biegi_pts, luki = [], []
    for g in grupy:
        pp = [P[g[0]]] + [P[(e + 1) % n] for e in g]
        luk = None
        if len(g) >= 3:
            kand = []
            for lj in luki_json:
                c, R = lj['srodek'], lj['R_zewn']
                dmax = max(abs(math.dist(q, c) - R) for q in pp)
                kand.append((dmax, (c[0], c[1], R)))
            cx, cy, R, dmax = _okrag(pp)
            kand.append((dmax, (cx, cy, R)))
            dmax, (cx, cy, R) = min(kand)
            if dmax < 0.02:
                a0 = math.atan2(pp[0][1] - cy, pp[0][0] - cx)
                a1 = math.atan2(pp[-1][1] - cy, pp[-1][0] - cx)
                # kierunek zgodny z kolejnością punktów
                am = math.atan2(pp[len(pp) // 2][1] - cy, pp[len(pp) // 2][0] - cx)
                da = (a1 - a0) % (2 * math.pi)
                dm = (am - a0) % (2 * math.pi)
                if dm > da:
                    da = da - 2 * math.pi
                k = max(2, int(math.ceil(abs(math.degrees(da)) / deg)))
                pp = [pp[0]] + [(cx + R * math.cos(a0 + da * j / k), cy + R * math.sin(a0 + da * j / k))
                                for j in range(1, k)] + [pp[-1]]
                luk = (cx, cy, R, a0, da)
        biegi_pts.append(pp)
        luki.append(luk)
    # globalna lista wierzchołków (do wektorów ukośnych)
    G = []
    for pp in biegi_pts:
        G += pp[:-1]
    m = len(G)
    Garr = np.asarray(G)

    def nrm(a, b):
        d = b - a
        d = d / max(np.hypot(*d), 1e-12)
        return np.array([d[1], -d[0]])
    miters = []
    for i in range(m):
        a, b, c = Garr[i - 1], Garr[i], Garr[(i + 1) % m]
        n0, n1 = nrm(a, b), nrm(b, c)
        den = 1.0 + float(n0 @ n1)
        mv = (n0 + n1) / max(den, 0.15)
        miters.append(mv)
    out, k = [], 0
    for bi, pp in enumerate(biegi_pts):
        cnt = len(pp)
        idxs = [(k + j) % m for j in range(cnt)]
        b = Bieg(pp, [miters[j] for j in idxs], luk=luki[bi], idx=bi)
        out.append(b)
        k += cnt - 1
    return out


# ============================================================================================== akumulator geometrii
class Geo:
    """Akumulator siatki: wierzchołki (współrzędne względne ±0,00), ściany, klucz materiału, gładkość,
    atrybuty wierzchołków ``fu``/``fv`` (współrzędne tekstur okładzin w metrach) i ``rnd`` (losowość elementu)."""

    def __init__(self):
        self.V, self.F, self.M, self.S = [], [], [], []
        self.U, self.W, self.R = [], [], []

    def _v(self, p, u, w, r):
        self.V.append((float(p[0]), float(p[1]), float(p[2])))
        self.U.append(u)
        self.W.append(w)
        self.R.append(r)
        return len(self.V) - 1

    def face(self, pts, uvs, mat, smooth=False, rnd=0.0):
        ids = [self._v(p, uv[0], uv[1], rnd) for p, uv in zip(pts, uvs)]
        self.F.append(ids)
        self.M.append(mat)
        self.S.append(smooth)

    def siatka(self, rows, uvs, mat, smooth=False, rnd=0.0, zamk_u=False):
        """Siatka czworokątów: rows[i][j] punkt 3D, uvs[i][j] (u, v); czworokąty (i,j)-(i,j+1)-(i+1,j+1)-(i+1,j)."""
        nr, nc = len(rows), len(rows[0])
        ids = [[self._v(rows[i][j], uvs[i][j][0], uvs[i][j][1], rnd) for j in range(nc)] for i in range(nr)]
        for i in range(nr - 1):
            for j in range(nc - 1):
                self.F.append([ids[i][j], ids[i][j + 1], ids[i + 1][j + 1], ids[i + 1][j]])
                self.M.append(mat)
                self.S.append(smooth)

    def box(self, b, s0, s1, t0, t1, z0, z1, mat, rs=None, rz=None, rnd=None, maks=None, sciany='wszystkie'):
        """Prostopadłościan „wzdłuż biegu”: s0..s1 (długość), t0..t1 (odsunięcie, t0 < t1), z0..z1."""
        if s1 - s0 < 1e-4 or t1 - t0 < 1e-4 or z1 - z0 < 1e-4:
            return
        rs = s0 if rs is None else rs
        rz = z0 if rz is None else rz
        rnd = _hash01(b.idx, round(s0, 2), round(z0, 2), mat) if rnd is None else rnd
        ss = b.probki(s0, s1, maks)
        O = [b.pt(s, t1) for s in ss]
        I = [b.pt(s, t0) for s in ss]
        gl = b.krzywy
        su = [s - rs for s in ss]
        # zewnętrzna (t1) i wewnętrzna (t0)
        if sciany in ('wszystkie', 'zew'):
            self.siatka([[(*p, z0) for p in O], [(*p, z1) for p in O]],
                        [[(u, z0 - rz) for u in su], [(u, z1 - rz) for u in su]], mat, gl, rnd)
        if sciany == 'wszystkie':
            self.siatka([[(*p, z0) for p in I[::-1]], [(*p, z1) for p in I[::-1]]],
                        [[(u, z0 - rz) for u in su[::-1]], [(u, z1 - rz) for u in su[::-1]]], mat, gl, rnd)
            # góra i dół
            self.siatka([[(*p, z1) for p in I], [(*p, z1) for p in O]],
                        [[(u, t0) for u in su], [(u, t1) for u in su]], mat, False, rnd)
            self.siatka([[(*p, z0) for p in O], [(*p, z0) for p in I]],
                        [[(u, t1) for u in su], [(u, t0) for u in su]], mat, False, rnd)
            # czoła
            a, c = I[0], O[0]
            self.face([(*a, z0), (*c, z0), (*c, z1), (*a, z1)],
                      [(0, z0 - rz), (t1 - t0, z0 - rz), (t1 - t0, z1 - rz), (0, z1 - rz)], mat, False, rnd)
            a, c = I[-1], O[-1]
            self.face([(*a, z0), (*a, z1), (*c, z1), (*c, z0)],
                      [(0, z0 - rz), (0, z1 - rz), (t1 - t0, z1 - rz), (t1 - t0, z0 - rz)], mat, False, rnd)

    def plat(self, b, s0, s1, t, z0, z1, mat, rs=None, rz=None, maks=None, smooth=None):
        """Pojedyncza powierzchnia pionowa wzdłuż biegu (np. szyba) na odsunięciu t."""
        if s1 - s0 < 1e-4:
            return
        rs = s0 if rs is None else rs
        rz = z0 if rz is None else rz
        ss = b.probki(s0, s1, maks)
        O = [b.pt(s, t) for s in ss]
        su = [s - rs for s in ss]
        self.siatka([[(*p, z0) for p in O], [(*p, z1) for p in O]],
                    [[(u, z0 - rz) for u in su], [(u, z1 - rz) for u in su]], mat,
                    b.krzywy if smooth is None else smooth, _hash01(b.idx, round(s0, 2), round(z0, 2)))

    def poziom(self, b, s0, s1, t0, t1, z, mat, gora=True, maks=None):
        """Pozioma powierzchnia wzdłuż biegu."""
        ss = b.probki(s0, s1, maks)
        O = [b.pt(s, t1) for s in ss]
        I = [b.pt(s, t0) for s in ss]
        su = [s - s0 for s in ss]
        if gora:
            self.siatka([[(*p, z) for p in I], [(*p, z) for p in O]], [[(u, t0) for u in su], [(u, t1) for u in su]],
                        mat, False)
        else:
            self.siatka([[(*p, z) for p in O], [(*p, z) for p in I]], [[(u, t1) for u in su], [(u, t0) for u in su]],
                        mat, False)

    def pryzma(self, geom, z0, z1, mat, mat_gora=None, mat_dol=None, dno=True, gora=True, boki=True, cell=None,
               mat_boki=None):
        """Pryzma z (Multi)Polygon (z otworami): boki + wieka (triangulacja z ograniczeniami)."""
        from umwd.render.context import triangulacja
        parts = [geom] if isinstance(geom, Polygon) else list(getattr(geom, 'geoms', []))
        for P in parts:
            if P.is_empty or P.area < 1e-4:
                continue
            P = orient(P, 1.0)
            if boki:
                for ring in [P.exterior] + list(P.interiors):
                    c = list(ring.coords)
                    acc = 0.0
                    for a, b in zip(c[:-1], c[1:]):
                        l = math.dist(a, b)
                        if l < 1e-5:
                            continue
                        self.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)],
                                  [(acc, z0), (acc + l, z0), (acc + l, z1), (acc, z1)], mat_boki or mat)
                        acc += l
            if gora or dno:
                V2, F = triangulacja(P, cell)
                for f in F:
                    a, b, c = V2[f[0]], V2[f[1]], V2[f[2]]
                    if gora:
                        self.face([(a[0], a[1], z1), (b[0], b[1], z1), (c[0], c[1], z1)],
                                  [(a[0], a[1]), (b[0], b[1]), (c[0], c[1])], mat_gora or mat)
                    if dno:
                        self.face([(a[0], a[1], z0), (c[0], c[1], z0), (b[0], b[1], z0)],
                                  [(a[0], a[1]), (c[0], c[1]), (b[0], b[1])], mat_dol or mat)

    def obiekt(self, name, coll, mats, dz=0.0):
        """Tworzy obiekt Blendera; mats: funkcja klucz → materiał."""
        if not self.F:
            return None
        V = np.asarray(self.V, np.float32)
        V[:, 2] += dz
        klucze = sorted(set(self.M))
        ki = {k: i for i, k in enumerate(klucze)}
        tot = np.fromiter((len(f) for f in self.F), np.int32, len(self.F))
        flat = np.fromiter((i for f in self.F for i in f), np.int32, int(tot.sum()))
        start = np.zeros(len(tot), np.int32)
        start[1:] = np.cumsum(tot)[:-1]
        me = bpy.data.meshes.new(name)
        me.vertices.add(len(V))
        me.vertices.foreach_set('co', V.ravel())
        me.loops.add(len(flat))
        me.loops.foreach_set('vertex_index', flat)
        me.polygons.add(len(tot))
        me.polygons.foreach_set('loop_start', start)
        me.polygons.foreach_set('material_index', np.fromiter((ki[k] for k in self.M), np.int32, len(self.M)))
        me.polygons.foreach_set('use_smooth', np.asarray(self.S, bool))
        for nm, arr in (('fu', self.U), ('fv', self.W), ('rnd', self.R)):
            a = me.attributes.new(nm, 'FLOAT', 'POINT')
            a.data.foreach_set('value', np.asarray(arr, np.float32))
        me.update(calc_edges=True)
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        for k in klucze:
            me.materials.append(mats(k))
        return ob


# ============================================================================================== materiały
class Materialy:
    """Materiały proceduralne budynku. Klucze: 'granit', 'cer:<ton>:<faktura>', 'metal', 'szklo:<typ>', 'wn_*' …"""

    def __init__(self, spec, opts):
        self.spec = spec
        self.o = opts
        self.c = {}

    def __call__(self, key):
        if key in self.c:
            return self.c[key]
        czesci = key.split(':')
        f = getattr(self, 'm_' + czesci[0], None)
        if f is None:
            raise KeyError('brak materiału ' + key)
        m = bpy.data.materials.new('B_' + key)
        f(m, *czesci[1:])
        self.c[key] = m
        return m

    # ---------------------------------------------------------------- węzły pomocnicze
    @staticmethod
    def _attr(nb, name):
        return nb.n('ShaderNodeAttribute', {'attribute_name': name, 'attribute_type': 'GEOMETRY'}).outputs['Fac']

    def _kafle(self, nb, w, h, jw, losowe_przes=True, przes=0.5, uv=None):
        """Wzór płyt/kafli na (fu, fv): zwraca (maska_kafla 1/0, los_kafla 0–1, frac_u 0–1, los_rzedu)."""
        if uv is None:
            fu, fv = self._attr(nb, 'fu'), self._attr(nb, 'fv')
        else:
            fu, fv = uv
        rn = self._attr(nb, 'rnd')
        row = nb.math('FLOOR', nb.math('DIVIDE', fv, h))
        wr = nb.n('ShaderNodeTexWhiteNoise', {'noise_dimensions': '3D'})
        cr = nb.n('ShaderNodeCombineXYZ')
        nb.l(row, cr.inputs[0])
        nb.l(nb.math('MULTIPLY', rn, 17.3), cr.inputs[1])
        cr.inputs[2].default_value = 3.1
        nb.l(cr.outputs[0], wr.inputs['Vector'])
        if losowe_przes:
            shift = nb.math('MULTIPLY', wr.outputs['Value'], w)
        else:
            shift = nb.math('MULTIPLY', nb.math('FRACT', nb.math('MULTIPLY', row, przes)), w)
        uu = nb.math('DIVIDE', nb.math('ADD', fu, shift), w)
        col = nb.math('FLOOR', uu)
        fru = nb.math('SUBTRACT', uu, col)
        vv = nb.math('SUBTRACT', nb.math('DIVIDE', fv, h), row)
        du = nb.math('MULTIPLY', nb.math('MINIMUM', fru, nb.math('SUBTRACT', 1.0, fru)), w)
        dv = nb.math('MULTIPLY', nb.math('MINIMUM', vv, nb.math('SUBTRACT', 1.0, vv)), h)
        d = nb.math('MINIMUM', du, dv)
        mr = nb.n('ShaderNodeMapRange', {'interpolation_type': 'SMOOTHSTEP'})
        nb.l(d, mr.inputs['Value'])
        mr.inputs['From Min'].default_value = jw * 0.5 - 0.0012
        mr.inputs['From Max'].default_value = jw * 0.5 + 0.0012
        wn = nb.n('ShaderNodeTexWhiteNoise', {'noise_dimensions': '3D'})
        cc = nb.n('ShaderNodeCombineXYZ')
        nb.l(col, cc.inputs[0])
        nb.l(row, cc.inputs[1])
        nb.l(nb.math('MULTIPLY', rn, 31.7), cc.inputs[2])
        nb.l(cc.outputs[0], wn.inputs['Vector'])
        return mr.outputs['Result'], wn.outputs['Value'], fru, wr.outputs['Value']

    @staticmethod
    def _rgb(nb, c):
        n = nb.n('ShaderNodeRGB')
        n.outputs[0].default_value = (*c, 1.0)
        return n.outputs[0]

    def _skala(self, c, k=None):
        k = self.o.get('albedo', 0.84) if k is None else k
        return tuple(min(0.95, x * k) for x in c)

    # ---------------------------------------------------------------- kamień
    def m_granit(self, m, wariant=''):
        """Granit strzegomski jasny płomieniowany: płyty 1,20 × 0,75 m, spoiny 4 mm, zmienność płyt, ziarno
        (kwarc/skaleń/biotyt), lekkie zabrudzenie strefy cokołowej."""
        nb = NodeBuilder(m)
        base = self._skala(self.spec.barwa('granit'), self.o.get('albedo_granit', 0.70))
        if wariant == 'ciemny':
            base = tuple(x * 0.55 for x in base)
        mask, los, fru, _ = self._kafle(nb, 1.20, 0.75, 0.005)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=95.0, Detail=3.0, Roughness=0.6)
        nb.l(pos, nz.inputs['Vector'])
        vor = nb.n('ShaderNodeTexVoronoi', Scale=260.0)
        nb.l(pos, vor.inputs['Vector'])
        spk = nb.math('LESS_THAN', vor.outputs['Distance'], 0.16)
        ton = nb.math('ADD', 0.93, nb.math('MULTIPLY', nb.math('SUBTRACT', los, 0.5), 0.12))
        gr = nb.math('ADD', 0.86, nb.math('MULTIPLY', nz.outputs['Fac'], 0.28))
        k = nb.math('MULTIPLY', ton, gr)
        k = nb.math('MULTIPLY', k, nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY', spk, 0.55)))
        # makro: delikatne „chmury” barwy w kamieniu
        nm = nb.n('ShaderNodeTexNoise', Scale=1.3, Detail=4.0)
        nb.l(pos, nm.inputs['Vector'])
        k = nb.math('MULTIPLY', k, nb.math('ADD', 0.95, nb.math('MULTIPLY', nm.outputs['Fac'], 0.1)))
        # strefa cokołowa: lekkie zabrudzenie do Z ≈ 0,7 m
        sz = nb.n('ShaderNodeSeparateXYZ')
        nb.l(pos, sz.inputs[0])
        brud = nb.math('SUBTRACT', 1.0, nb.math('MULTIPLY', nb.math('MAXIMUM', nb.math('SUBTRACT', 0.75, sz.outputs[2]), 0.0), 0.16),
                       clamp=True)
        k = nb.math('MULTIPLY', k, brud)
        c0 = self._rgb(nb, base)
        col = nb.n('ShaderNodeMix', {'data_type': 'RGBA', 'blend_type': 'MULTIPLY'})
        col.inputs[0].default_value = 1.0
        nb.l(c0, col.inputs[6])
        cc = nb.n('ShaderNodeCombineColor')
        for i in range(3):
            nb.l(k, cc.inputs[i])
        nb.l(cc.outputs[0], col.inputs[7])
        jcol = tuple(x * 0.42 for x in base)
        out = nb.mix(mask, jcol, col.outputs[2])
        b = nb.n('ShaderNodeBsdfPrincipled')
        nb.l(out, b.inputs['Base Color'])
        nb.l(nb.math('ADD', 0.56, nb.math('MULTIPLY', nz.outputs['Fac'], 0.16)), b.inputs['Roughness'])
        b.inputs['Specular IOR Level'].default_value = 0.45
        bm1 = nb.n('ShaderNodeBump', Strength=0.12, Distance=0.0015)
        nb.l(nz.outputs['Fac'], bm1.inputs['Height'])
        bm2 = nb.n('ShaderNodeBump', Strength=0.6, Distance=0.004)
        nb.l(mask, bm2.inputs['Height'])
        nb.l(bm1.outputs['Normal'], bm2.inputs['Normal'])
        nb.l(bm2.outputs['Normal'], b.inputs['Normal'])
        nb.output(b)

    def m_bruk(self, m, wariant=''):
        """Posadzka granitowa zewnętrzna (płyty 0,60 × 1,20 m w osiach wieży, płomieniowane, z opadłymi liśćmi)."""
        nb = NodeBuilder(m)
        base = self._skala(self.spec.barwa('granit'), self.o.get('albedo_bruk', 0.52))
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(pos, sp.inputs[0])
        A = self.spec.uv['Ai']
        o = self.spec.uv['o']
        x = nb.math('SUBTRACT', sp.outputs[0], float(o[0]))
        y = nb.math('SUBTRACT', sp.outputs[1], float(o[1]))
        u = nb.math('ADD', nb.math('MULTIPLY', x, float(A[0, 0])), nb.math('MULTIPLY', y, float(A[0, 1])))
        v = nb.math('ADD', nb.math('MULTIPLY', x, float(A[1, 0])), nb.math('MULTIPLY', y, float(A[1, 1])))
        if wariant == 'kostka':
            mask, los, fru, _ = self._kafle(nb, 0.20, 0.10, 0.008, uv=(u, v))
        else:
            mask, los, fru, _ = self._kafle(nb, 1.20, 0.60, 0.006, uv=(u, v))
        nz = nb.n('ShaderNodeTexNoise', Scale=60.0, Detail=3.0)
        nb.l(pos, nz.inputs['Vector'])
        ton = nb.math('ADD', 0.9, nb.math('MULTIPLY', los, 0.18))
        k = nb.math('MULTIPLY', ton, nb.math('ADD', 0.88, nb.math('MULTIPLY', nz.outputs['Fac'], 0.24)))
        nm = nb.n('ShaderNodeTexNoise', Scale=0.35, Detail=5.0)
        nb.l(pos, nm.inputs['Vector'])
        k = nb.math('MULTIPLY', k, nb.math('ADD', 0.9, nb.math('MULTIPLY', nm.outputs['Fac'], 0.18)))
        cc = nb.n('ShaderNodeCombineColor')
        for i in range(3):
            nb.l(k, cc.inputs[i])
        col = nb.mix(1.0, self._rgb(nb, base), cc.outputs[0], blend='MULTIPLY')
        col = nb.mix(mask, tuple(x * 0.45 for x in base), col)
        # jesienne liście (rzadkie plamki)
        lv = nb.n('ShaderNodeTexVoronoi', Scale=7.0)
        nb.l(pos, lv.inputs['Vector'])
        ln = nb.n('ShaderNodeTexNoise', Scale=0.8, Detail=2.0)
        nb.l(pos, ln.inputs['Vector'])
        lis = nb.math('MULTIPLY', nb.math('LESS_THAN', lv.outputs['Distance'], 0.075),
                      nb.math('GREATER_THAN', ln.outputs['Fac'], 0.52))
        lcol = nb.mix(lv.outputs['Color'], (0.30, 0.13, 0.03), (0.42, 0.28, 0.05))
        col = nb.mix(lis, col, lcol)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.72)
        nb.l(col, b.inputs['Base Color'])
        bm = nb.n('ShaderNodeBump', Strength=0.5, Distance=0.004)
        nb.l(mask, bm.inputs['Height'])
        nb.l(bm.outputs['Normal'], b.inputs['Normal'])
        nb.output(b)

    # ---------------------------------------------------------------- ceramika
    def m_cer(self, m, ton='M3', faktura='gladka'):
        """Ceramika glazurowana półmatowa – profile ekstrudowane 1,20 × 0,30 m (spoiny 6 mm), zmienność płytek,
        faktury: gładka / ryflowana co 0,135 m / glazura cieniowana."""
        nb = NodeBuilder(m)
        base = self._skala(self.spec.barwa('cer_' + ton))
        h = 0.325 if ton in ('luk', 'lamele_korony') else 0.30
        mask, los, fru, losr = self._kafle(nb, 1.20, h, 0.006)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        ton_k = nb.math('ADD', 0.955, nb.math('MULTIPLY', los, 0.09))
        if faktura == 'cieniowana':
            ton_k = nb.math('MULTIPLY', ton_k, nb.math('ADD', 0.93, nb.math('MULTIPLY', fru, 0.10)))
        nm = nb.n('ShaderNodeTexNoise', Scale=0.6, Detail=3.0)
        nb.l(pos, nm.inputs['Vector'])
        ton_k = nb.math('MULTIPLY', ton_k, nb.math('ADD', 0.97, nb.math('MULTIPLY', nm.outputs['Fac'], 0.06)))
        cc = nb.n('ShaderNodeCombineColor')
        for i in range(3):
            nb.l(ton_k, cc.inputs[i])
        col = nb.mix(1.0, self._rgb(nb, base), cc.outputs[0], blend='MULTIPLY')
        # delikatne przesunięcie barwy płytki (cieplej/chłodniej)
        wc = tuple(min(1, x * f) for x, f in zip(base, (1.03, 1.0, 0.95)))
        col = nb.mix(nb.math('MULTIPLY', losr, 0.35), col, wc)
        normal = None
        if faktura == 'ryflowana':
            fu = self._attr(nb, 'fu')
            sn = nb.math('SINE', nb.math('MULTIPLY', fu, 2 * math.pi / 0.135))
            rf = nb.math('MULTIPLY', nb.math('ADD', sn, 1.0), 0.5)
            col = nb.mix(nb.math('MULTIPLY', nb.math('SUBTRACT', 1.0, rf), 0.12), col, tuple(x * 0.7 for x in base))
            bmr = nb.n('ShaderNodeBump', Strength=0.35, Distance=0.006)
            nb.l(rf, bmr.inputs['Height'])
            normal = bmr.outputs['Normal']
        col = nb.mix(mask, tuple(x * 0.30 for x in base), col)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.36)
        nb.l(col, b.inputs['Base Color'])
        b.inputs['Specular IOR Level'].default_value = 0.5
        b.inputs['Coat Weight'].default_value = 0.10
        b.inputs['Coat Roughness'].default_value = 0.12
        rn = nb.n('ShaderNodeTexNoise', Scale=4.0, Detail=2.0)
        nb.l(pos, rn.inputs['Vector'])
        nb.l(nb.math('ADD', 0.30, nb.math('MULTIPLY', rn.outputs['Fac'], 0.12)), b.inputs['Roughness'])
        bm = nb.n('ShaderNodeBump', Strength=0.55, Distance=0.005)
        nb.l(mask, bm.inputs['Height'])
        if normal is not None:
            nb.l(normal, bm.inputs['Normal'])
        nb.l(bm.outputs['Normal'], b.inputs['Normal'])
        nb.output(b)

    # ---------------------------------------------------------------- metal
    def m_metal(self, m, wariant=''):
        """Aluminium anodowane – grafitowy brąz (RAL 8019), satynowe."""
        nb = NodeBuilder(m)
        c = self.spec.barwa('metal')
        k = 2.4 if wariant != 'fuga' else 1.2
        base = tuple(min(1, x * k) for x in c)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=2.5, Detail=3.0)
        nb.l(pos, nz.inputs['Vector'])
        b = nb.n('ShaderNodeBsdfPrincipled', Metallic=0.85)
        nb.set(b, 'Base Color', base)
        nb.l(nb.math('ADD', 0.30, nb.math('MULTIPLY', nz.outputs['Fac'], 0.12)), b.inputs['Roughness'])
        nb.output(b)

    def m_litery(self, m):
        """Litery napisu – wypełnienie z brązu patynowanego (czytelne jak wykute)."""
        nb = NodeBuilder(m)
        b = nb.n('ShaderNodeBsdfPrincipled', Metallic=0.8, Roughness=0.42)
        nb.set(b, 'Base Color', (0.16, 0.11, 0.065))
        nb.output(b)

    # ---------------------------------------------------------------- szkło
    def m_szklo(self, m, typ='biuro'):
        """Szkło architektoniczne (pojedyncza tafla): mieszanie Transparent/Glossy wg Fresnela (Schlick, R0 ≈ 0,07
        dla pakietu), promienie cienia przechodzą (słońce we wnętrzach), lekkie falowanie tafli."""
        nb = NodeBuilder(m)
        tv = {'biuro': self.spec.szklo['biura']['Tvis'], 'korona': self.spec.szklo['korona']['Tvis'],
              'parter': 0.74, 'balustrada': 0.85}.get(typ, 0.62)
        tint = (tv * 0.97, tv * 1.0, tv * 0.985)
        R0 = 0.09 if typ != 'balustrada' else 0.05
        lw = nb.n('ShaderNodeLayerWeight', Blend=0.5)
        f5 = nb.math('POWER', lw.outputs['Facing'], 5.0)
        r = nb.math('ADD', R0, nb.math('MULTIPLY', f5, 1.0 - R0), clamp=True)
        tr = nb.n('ShaderNodeBsdfTransparent')
        nb.set(tr, 'Color', tint)
        gl = nb.n('ShaderNodeBsdfGlossy', Roughness=0.015)
        nb.set(gl, 'Color', (0.95, 0.96, 0.97))
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=0.45, Detail=1.0)
        nb.l(pos, nz.inputs['Vector'])
        bm = nb.n('ShaderNodeBump', Strength=0.025, Distance=0.05)
        nb.l(nz.outputs['Fac'], bm.inputs['Height'])
        nb.l(bm.outputs['Normal'], gl.inputs['Normal'])
        mx = nb.n('ShaderNodeMixShader')
        nb.l(r, mx.inputs['Fac'])
        nb.l(tr.outputs[0], mx.inputs[1])
        nb.l(gl.outputs[0], mx.inputs[2])
        lp = nb.n('ShaderNodeLightPath')
        tr2 = nb.n('ShaderNodeBsdfTransparent')
        nb.set(tr2, 'Color', tuple(x * 0.92 for x in tint))
        mx2 = nb.n('ShaderNodeMixShader')
        nb.l(lp.outputs['Is Shadow Ray'], mx2.inputs['Fac'])
        nb.l(mx.outputs[0], mx2.inputs[1])
        nb.l(tr2.outputs[0], mx2.inputs[2])
        nb.output(mx2)

    # ---------------------------------------------------------------- wnętrza
    def _proste(self, m, col, rough=0.8, metal=0.0, spec=0.5):
        nb = NodeBuilder(m)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
        nb.set(b, 'Base Color', col)
        b.inputs['Specular IOR Level'].default_value = spec
        nb.output(b)

    def m_wn_sufit(self, m):
        self._proste(m, (0.70, 0.69, 0.66), 0.9)

    def m_wn_sciana(self, m):
        nb = NodeBuilder(m)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.85)
        oi = nb.n('ShaderNodeObjectInfo')
        rn = self._attr(nb, 'rnd')
        c = nb.mix(rn, (0.62, 0.60, 0.56), (0.74, 0.71, 0.66))
        nb.l(c, b.inputs['Base Color'])
        nb.output(b)

    def m_wn_podloga(self, m):
        self._proste(m, (0.30, 0.28, 0.25), 0.8)

    def m_wn_kamien(self, m):
        """Posadzka holu – jasny kamień polerowany półmat."""
        self._proste(m, (0.46, 0.44, 0.40), 0.28)

    def m_wn_drewno(self, m, wariant=''):
        """Drewno (dąb) – okładziny holu i sali Sejmiku, z usłojeniem."""
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(pos, sp.inputs[0])
        cmb = nb.n('ShaderNodeCombineXYZ')
        nb.l(nb.math('MULTIPLY', sp.outputs[0], 1.0), cmb.inputs[0])
        nb.l(nb.math('MULTIPLY', sp.outputs[1], 1.0), cmb.inputs[1])
        nb.l(nb.math('MULTIPLY', sp.outputs[2], 14.0), cmb.inputs[2])
        wv = nb.n('ShaderNodeTexWave', {'wave_type': 'BANDS'}, Scale=3.0, Distortion=6.0, Detail=3.0)
        nb.l(cmb.outputs[0], wv.inputs['Vector'])
        c0, c1 = ((0.30, 0.17, 0.08), (0.46, 0.29, 0.14)) if wariant != 'jasne' else ((0.42, 0.29, 0.17), (0.58, 0.42, 0.26))
        col = nb.mix(wv.outputs['Fac'], c0, c1)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.45)
        nb.l(col, b.inputs['Base Color'])
        nb.output(b)

    def m_wn_lampa(self, m, wariant=''):
        """Oprawa liniowa – emisja (dzień: 4000 K; ciepłe wnętrza: 3000 K)."""
        nb = NodeBuilder(m)
        e = nb.n('ShaderNodeEmission')
        moc = self.o.get('lampy', 1.0)
        if wariant == 'cieple':
            nb.set(e, 'Color', (1.0, 0.78, 0.52))
            e.inputs['Strength'].default_value = 30.0 * moc
        else:
            # biura: udział zapalonych opraw (węzeł 'udzial' – zmieniany przez swiatlo_dzienne o zmierzchu)
            nb.set(e, 'Color', (1.0, 0.93, 0.84))
            ud = nb.n('ShaderNodeValue')
            ud.name = 'udzial'
            ud.outputs[0].default_value = 1.0
            wl = nb.math('LESS_THAN', self._attr(nb, 'rnd'), ud.outputs[0])
            nb.l(nb.math('MULTIPLY', wl, 24.0 * moc), e.inputs['Strength'])
        nb.output(e)

    def m_wn_biurko(self, m):
        self._proste(m, (0.62, 0.60, 0.56), 0.5)

    def m_wn_ciemne(self, m):
        self._proste(m, (0.035, 0.035, 0.038), 0.5)

    def m_wn_tkanina(self, m):
        self._proste(m, (0.16, 0.10, 0.07), 0.9)

    def m_roleta(self, m):
        """Roleta ZIP (screen 5 %) – częściowo przezierna tkanina."""
        nb = NodeBuilder(m)
        d = nb.n('ShaderNodeBsdfDiffuse')
        nb.set(d, 'Color', (0.11, 0.105, 0.10))
        tr = nb.n('ShaderNodeBsdfTransparent')
        nb.set(tr, 'Color', (0.25, 0.25, 0.25))
        mx = nb.n('ShaderNodeMixShader')
        mx.inputs['Fac'].default_value = 0.22
        nb.l(d.outputs[0], mx.inputs[1])
        nb.l(tr.outputs[0], mx.inputs[2])
        nb.output(mx)

    def m_beton(self, m):
        self._proste(m, (0.42, 0.41, 0.39), 0.85)

    # ---------------------------------------------------------------- dachy
    def m_bipv(self, m):
        """Moduły BIPV szkło-szkło: ciemne ogniwa z delikatną siatką, szkło o niskim odbiciu."""
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        sp_ = nb.n('ShaderNodeSeparateXYZ')
        nb.l(pos, sp_.inputs[0])
        mask, los, fru, _ = self._kafle(nb, 0.166, 0.166, 0.004, losowe_przes=False, przes=0.0,
                                        uv=(sp_.outputs[0], sp_.outputs[1]))
        col = nb.mix(mask, (0.05, 0.055, 0.065), (0.010, 0.014, 0.026))
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.16)
        nb.l(col, b.inputs['Base Color'])
        b.inputs['Specular IOR Level'].default_value = 0.35
        nb.output(b)

    def m_sedum(self, m):
        """Zieleń ekstensywna (rozchodniki, trawy) – jesienna mozaika zieleni i czerwieni."""
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=3.5, Detail=6.0, Roughness=0.7)
        nb.l(pos, nz.inputs['Vector'])
        n2 = nb.n('ShaderNodeTexNoise', Scale=40.0, Detail=3.0)
        nb.l(pos, n2.inputs['Vector'])
        r = nb.n('ShaderNodeValToRGB')
        els = r.color_ramp.elements
        els[0].position, els[0].color = 0.25, (0.06, 0.09, 0.025, 1)
        els[1].position, els[1].color = 0.8, (0.22, 0.08, 0.04, 1)
        e = els.new(0.5)
        e.color = (0.13, 0.13, 0.04, 1)
        nb.l(nz.outputs['Fac'], r.inputs['Fac'])
        col = nb.mix(nb.math('MULTIPLY', n2.outputs['Fac'], 0.5), r.outputs['Color'], (0.05, 0.05, 0.03))
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.95)
        nb.l(col, b.inputs['Base Color'])
        bm = nb.n('ShaderNodeBump', Strength=0.8, Distance=0.03)
        nb.l(n2.outputs['Fac'], bm.inputs['Height'])
        nb.l(bm.outputs['Normal'], b.inputs['Normal'])
        nb.output(b)

    def m_zwir(self, m):
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=80.0, Detail=2.0)
        nb.l(pos, nz.inputs['Vector'])
        col = nb.mix(nz.outputs['Fac'], (0.22, 0.21, 0.19), (0.42, 0.40, 0.37))
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.95)
        nb.l(col, b.inputs['Base Color'])
        nb.output(b)

    def m_deska(self, m):
        """Taras: deski drewniane (modrzew) 0,14 m."""
        nb = NodeBuilder(m)
        mask, los, fru, _ = self._kafle(nb, 2.4, 0.145, 0.008)
        col = nb.mix(los, (0.20, 0.13, 0.08), (0.30, 0.20, 0.12))
        col = nb.mix(mask, (0.04, 0.03, 0.02), col)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.7)
        nb.l(col, b.inputs['Base Color'])
        nb.output(b)

    def m_cegla(self, m):
        """Ścieżki ogrodu – cegła z rozbiórki (z wykopu) w wątku jodełkowym uproszczonym."""
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(pos, sp.inputs[0])
        mask, los, fru, _ = self._kafle(nb, 0.25, 0.12, 0.012, uv=(sp.outputs[0], sp.outputs[1]))
        col = nb.mix(los, (0.20, 0.075, 0.04), (0.36, 0.15, 0.08))
        col = nb.mix(mask, (0.30, 0.28, 0.25), col)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.85)
        nb.l(col, b.inputs['Base Color'])
        nb.output(b)

    def m_ogrod_deszczowy(self, m):
        """Ogród deszczowy: mozaika traw (słoma, rdza), bylin (zieleń, fiolet), wilgotna gleba."""
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=1.8, Detail=6.0, Roughness=0.65)
        nb.l(pos, nz.inputs['Vector'])
        r = nb.n('ShaderNodeValToRGB')
        els = r.color_ramp.elements
        els[0].position, els[0].color = 0.3, (0.05, 0.06, 0.03, 1)
        els[1].position, els[1].color = 0.75, (0.30, 0.22, 0.10, 1)
        e = els.new(0.5)
        e.color = (0.12, 0.13, 0.05, 1)
        e = els.new(0.62)
        e.color = (0.14, 0.07, 0.12, 1)
        nb.l(nz.outputs['Fac'], r.inputs['Fac'])
        n2 = nb.n('ShaderNodeTexNoise', Scale=30.0, Detail=3.0)
        nb.l(pos, n2.inputs['Vector'])
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.9)
        nb.l(nb.mix(nb.math('MULTIPLY', n2.outputs['Fac'], 0.4), r.outputs['Color'], (0.04, 0.035, 0.025)),
             b.inputs['Base Color'])
        bm = nb.n('ShaderNodeBump', Strength=0.9, Distance=0.05)
        nb.l(n2.outputs['Fac'], bm.inputs['Height'])
        nb.l(bm.outputs['Normal'], b.inputs['Normal'])
        nb.output(b)

    def m_piasek(self, m):
        nb = NodeBuilder(m)
        pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
        nz = nb.n('ShaderNodeTexNoise', Scale=25.0, Detail=4.0)
        nb.l(pos, nz.inputs['Vector'])
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.95)
        nb.l(nb.mix(nz.outputs['Fac'], (0.42, 0.34, 0.22), (0.55, 0.46, 0.32)), b.inputs['Base Color'])
        nb.output(b)

    def m_pnacze(self, m):
        """Liście winobluszczu jesienią: karmin – bordo – pomarańcz (losowo na liść wg ``fu``), przeświecanie."""
        nb = NodeBuilder(m)
        r = nb.n('ShaderNodeValToRGB')
        els = r.color_ramp.elements
        els[0].position, els[0].color = 0.0, (0.16, 0.012, 0.010, 1)
        els[1].position, els[1].color = 1.0, (0.40, 0.11, 0.02, 1)
        e = els.new(0.45)
        e.color = (0.30, 0.025, 0.015, 1)
        e = els.new(0.85)
        e.color = (0.22, 0.10, 0.02, 1)
        nb.l(self._attr(nb, 'fu'), r.inputs['Fac'])
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.55)
        nb.l(r.outputs['Color'], b.inputs['Base Color'])
        b.inputs['Subsurface Weight'].default_value = 0.0
        tr = nb.n('ShaderNodeBsdfTranslucent')
        nb.l(r.outputs['Color'], tr.inputs['Color'])
        mx = nb.n('ShaderNodeMixShader')
        mx.inputs['Fac'].default_value = 0.3
        nb.l(b.outputs[0], mx.inputs[1])
        nb.l(tr.outputs[0], mx.inputs[2])
        nb.output(mx)

    def m_ludzie(self, m, wariant='0'):
        """Sylwetki ludzi: strefy wg wysokości względnej ``fv`` (buty, spodnie, okrycie od progu ``fu``, skóra,
        włosy); barwy okryć jesiennych losowane per obiekt (Object Info → Random)."""
        nb = NodeBuilder(m)
        oi = nb.n('ShaderNodeObjectInfo')
        rnd = oi.outputs['Random']
        r1 = nb.n('ShaderNodeValToRGB')
        r1.color_ramp.interpolation = 'CONSTANT'
        pal = [(0.0, (0.030, 0.034, 0.050)), (0.12, (0.20, 0.035, 0.03)), (0.24, (0.36, 0.22, 0.09)),
               (0.36, (0.035, 0.05, 0.10)), (0.48, (0.09, 0.10, 0.05)), (0.58, (0.40, 0.27, 0.05)),
               (0.68, (0.13, 0.13, 0.14)), (0.78, (0.25, 0.10, 0.06)), (0.88, (0.50, 0.46, 0.40))]
        els = r1.color_ramp.elements
        els[0].position, els[0].color = pal[0][0], (*pal[0][1], 1)
        els[1].position, els[1].color = pal[-1][0], (*pal[-1][1], 1)
        for pp, c in pal[1:-1]:
            e = els.new(pp)
            e.color = (*c, 1)
        nb.l(rnd, r1.inputs['Fac'])
        okr = r1.outputs['Color']
        f7 = nb.math('FRACT', nb.math('MULTIPLY', rnd, 7.31))
        f13 = nb.math('FRACT', nb.math('MULTIPLY', rnd, 13.7))
        f5 = nb.math('FRACT', nb.math('MULTIPLY', rnd, 5.13))
        spodnie = nb.mix(f7, (0.02, 0.022, 0.03), (0.06, 0.08, 0.13))
        skora = nb.mix(f13, (0.30, 0.17, 0.11), (0.62, 0.43, 0.32))
        wlosy = nb.mix(f5, (0.018, 0.014, 0.012), (0.33, 0.24, 0.14))
        hz = self._attr(nb, 'fv')
        prog = self._attr(nb, 'fu')
        c = nb.mix(nb.math('GREATER_THAN', hz, 0.035), (0.02, 0.018, 0.017), spodnie)
        c = nb.mix(nb.math('GREATER_THAN', hz, prog), c, okr)
        c = nb.mix(nb.math('GREATER_THAN', hz, 0.862), c, skora)
        c = nb.mix(nb.math('GREATER_THAN', hz, 0.935), c, wlosy)
        b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.8)
        nb.l(c, b.inputs['Base Color'])
        b.inputs['Sheen Weight'].default_value = 0.4
        b.inputs['Sheen Roughness'].default_value = 0.5
        nb.output(b)


# ============================================================================================== budowa
class Budynek:
    def __init__(self, scene, opts):
        self.sc = scene
        self.o = dict(DOMYSLNE)
        self.o.update(opts or {})
        self.spec = Spec(self.o['koncepcja'])
        self.Z = dict(ZALOZENIA)
        self.Z.update(self.o.get('zalozenia', {}))
        self.mat = Materialy(self.spec, self.o)
        self.DZ = self.spec.DZ
        self.info = {'czasy_s': {}, 'obiekty': {}, 'uwagi': []}
        self.rng = np.random.default_rng(self.o['seed'])
        root = bpy.data.collections.new('BUDYNEK')
        scene.collection.children.link(root)
        self.root = root
        self.kol = {}
        for k in ('wieza', 'skrzydlo', 'segment', 'dachy', 'wnetrza', 'zagospodarowanie_bliskie'):
            c = bpy.data.collections.new(k)
            root.children.link(c)
            self.kol[k] = c
        # obrysy (oczyszczone)
        self.obrys = {k: oczysc_obrys(b['obrys_ccw']) for k, b in self.spec.B.items()}
        self.poly = {k: Polygon(v) for k, v in self.obrys.items()}
        self.foot = unary_union([p.buffer(0.06, join_style=2) for p in self.poly.values()]).buffer(-0.06, join_style=2)
        # sąsiedzi (do pokrycia elewacji)
        self.sasiedzi = []
        try:
            S = json.load(open(SASIEDZI, encoding='utf-8'))
            for b in S['budynki']:
                if b['id'] == 'mazowiecka_19':
                    z = 140.24 - self.spec.zero
                    self.sasiedzi.append((Polygon(b['obrys_egib_en']).buffer(0), z))
        except Exception as e:      # pragma: no cover
            self.info['uwagi'].append('brak sasiedzi.json: %s' % e)
        kon = self.o.get('kontekst')
        if kon is not None:
            self.oi = kon['ctx'].inwest
        else:
            self.oi = Polygon(json.load(open(SITE_JSON, encoding='utf-8'))['granice']['obszar_inwestycji']['pts'])
        self.wysokosc_dachu = {k: self.spec.dach[k]['pokrycie'] for k in ('W', 'M', 'S')}
        self.wysokosc_attyki = {k: self.spec.dach[k]['attyka'] for k in ('W', 'M', 'S')}

    # ---------------------------------------------------------------- narzędzia
    def czas(self, nazwa, t0):
        self.info['czasy_s'][nazwa] = round(time.time() - t0, 1)

    def pokrycie(self, b, bryla):
        """Przedziały biegu zasłonięte przez inne bryły / sąsiadów: [(s0, s1, z_pokrycia)]."""
        zrodla = [(self.poly[k].buffer(0.03), self.wysokosc_dachu[k]) for k in self.poly if k != bryla]
        zrodla += [(p.buffer(0.03), z) for p, z in self.sasiedzi]
        krok = 0.05
        ss = np.arange(krok / 2, b.L, krok)
        zz = []
        for s in ss:
            p = b.pt(s, 0.0) + b.normalna(s) * 0.15
            P = Point(p[0], p[1])
            z = None
            for poly, zt in zrodla:
                if poly.contains(P):
                    z = zt if z is None else max(z, zt)
            zz.append(z)
        out = []
        cur = None
        for s, z in zip(ss, zz):
            if cur is not None and (z is None or abs(z - cur[2]) > 1e-6):
                out.append((cur[0], s - krok / 2, cur[2]))
                cur = None
            if z is not None and cur is None:
                cur = [s - krok / 2, None, z]
        if cur is not None:
            out.append((cur[0], b.L, cur[2]))
        out = [(max(0.0, a), min(b.L, c), z) for a, c, z in out]
        # domknięcie końców (pokrycie sięgające ~końca biegu)
        res = []
        for a, c, z in out:
            if a < 0.08:
                a = 0.0
            if b.L - c < 0.08:
                c = b.L
            res.append((a, c, z))
        return res

    def przytnij(self, b, s0, s1, z0, z1):
        """Dzieli element wg pokrycia: zwraca listę (s0, s1, z0, z1) części widocznych."""
        kaw = [(s0, s1)]
        out = []
        for a, c, zc in b.pokrycie:
            nowe = []
            for p, q in kaw:
                if q <= a or p >= c:
                    nowe.append((p, q))
                    continue
                if p < a:
                    nowe.append((p, a))
                if q > c:
                    nowe.append((c, q))
                lo, hi = max(p, a), min(q, c)
                if z1 > zc + 1e-6:
                    out.append((lo, hi, max(z0, zc), z1))
            kaw = nowe
        out += [(p, q, z0, z1) for p, q in kaw]
        return [(p, q, a, c) for p, q, a, c in out if q - p > 0.01 and c - a > 0.005]

    def el(self, G, b, s0, s1, t0, t1, z0, z1, mat, rs=None, rz=None, rnd=None, przytnij=True, maks=None):
        if not przytnij:
            G.box(b, s0, s1, t0, t1, z0, z1, mat, rs, rz, rnd, maks)
            return
        for p, q, a, c in self.przytnij(b, s0, s1, z0, z1):
            G.box(b, p, q, t0, t1, a, c, mat, rs if rs is not None else s0, rz if rz is not None else z0, rnd, maks)

    def szyba(self, G, b, s0, s1, t, z0, z1, mat, przytnij=True):
        for p, q, a, c in (self.przytnij(b, s0, s1, z0, z1) if przytnij else [(s0, s1, z0, z1)]):
            G.plat(b, p, q, t, a, c, mat, maks=0.4 if b.krzywy else None)

    def widoczne(self, b, s0, s1, z0, z1):
        return bool(self.przytnij(b, s0, s1, z0, z1))

    @staticmethod
    def filary(qmin, qmax, P, w, okno, osie0=0.0):
        """Przedziały filarów (oś co P od osie0, szerokość w) w [qmin, qmax]; skrajne luki < okno+0,1 → filar."""
        k0 = math.floor((qmin - osie0 - w) / P)
        k1 = math.ceil((qmax - osie0 + w) / P)
        out = []
        for k in range(k0, k1 + 1):
            a = osie0 + k * P
            lo, hi = max(qmin, a - w / 2), min(qmax, a + w / 2)
            if hi - lo > 0.02:
                out.append([lo, hi])
        if not out:
            return [[qmin, qmin + w / 2], [qmax - w / 2, qmax]]
        if out[0][0] - qmin > 1e-6:
            if out[0][0] - qmin < okno + 0.1:
                out[0][0] = qmin
            else:
                out.insert(0, [qmin, qmin + w / 2])
        if qmax - out[-1][1] > 1e-6:
            if qmax - out[-1][1] < okno + 0.1:
                out[-1][1] = qmax
            else:
                out.append([qmax - w / 2, qmax])
        return out

    @staticmethod
    def q_na_s(b, q0, kier):
        """Funkcja q → s dla biegu prostego: s = (q − q0)·kier (kier = ±1)."""
        return lambda q: (q - q0) * kier

    # ================================================================ okna (wspólne)
    def okno(self, G, b, s0, s1, t_szkla, z0, z1, typ='biuro', slupek=True, powiew=None, rama=0.06,
             slupek_w=0.07, rygiel=None, roleta=True, wewn_do=None, przytnij=True):
        """Okno: szyba (2 kwatery ze słupkiem w osi), rama obwodowa z metalu, opcjonalny rygiel (z), roleta ZIP."""
        if przytnij and not self.widoczne(b, s0, s1, z0, z1):
            return
        tz = t_szkla
        Gs, Gr = self.Gszklo, G
        self.szyba(Gs, b, s0 + rama * 0.5, s1 - rama * 0.5, tz, z0 + rama * 0.5, z1 - rama * 0.5, 'szklo:' + typ, przytnij)
        tr0, tr1 = tz - 0.035, tz + 0.035
        m = 'metal'
        self.el(Gr, b, s0, s0 + rama, tr0, tr1, z0, z1, m, przytnij=przytnij)
        self.el(Gr, b, s1 - rama, s1, tr0, tr1, z0, z1, m, przytnij=przytnij)
        self.el(Gr, b, s0 + rama, s1 - rama, tr0, tr1, z0, z0 + rama, m, przytnij=przytnij)
        self.el(Gr, b, s0 + rama, s1 - rama, tr0, tr1, z1 - rama, z1, m, przytnij=przytnij)
        if slupek:
            sm = (s0 + s1) / 2
            self.el(Gr, b, sm - slupek_w / 2, sm + slupek_w / 2, tr0 - 0.01, tr1, z0 + rama, z1 - rama, m,
                    przytnij=przytnij)
        if rygiel is not None:
            self.el(Gr, b, s0 + rama, s1 - rama, tr0 - 0.005, tr1, rygiel - 0.035, rygiel + 0.035, m, przytnij=przytnij)
        if roleta and self.rng.random() < self.o['rolety']:
            fr = self.rng.uniform(0.15, 0.75)
            zr = z1 - rama - (z1 - z0 - 2 * rama) * fr
            self.el(self.Gwn, b, s0 + rama, s1 - rama, tz + 0.05, tz + 0.06, zr, z1 - rama, 'roleta', przytnij=przytnij)
            self.el(Gr, b, s0 + rama, s1 - rama, tz + 0.045, tz + 0.075, zr - 0.04, zr, m, przytnij=przytnij)
        if wewn_do is not None and wewn_do < tz - 0.04:
            # parapet i nadproże wewnętrzne (domykają widok między szybą a krawędzią stropu)
            self.el(self.Gwn, b, s0, s1, wewn_do, tz - 0.035, z0 - 0.03, z0 + 0.0, 'wn_sciana', przytnij=przytnij)
            self.el(self.Gwn, b, s0, s1, wewn_do, tz - 0.035, z1, z1 + 0.03, 'wn_sufit', przytnij=przytnij)

    def witryna(self, G, b, s0, s1, t_szkla, z0, z1, naswietle=None, podzial=None, drzwi=None, typ='parter',
                przytnij=True):
        """Witryna parteru: szyba, rama, słupki co ``podzial`` (lub w osi), rygiel naświetla, drzwi (s_c, szer.)."""
        if s1 - s0 < 0.2:
            return
        rama = 0.07
        L = s1 - s0
        n = max(1, int(round(L / podzial))) if podzial else 2
        tz = t_szkla
        self.szyba(self.Gszklo, b, s0, s1, tz, z0, z1, 'szklo:' + typ, przytnij)
        tr0, tr1 = tz - 0.04, tz + 0.04
        m = 'metal'
        self.el(G, b, s0, s1, tr0, tr1, z0, z0 + rama, m, przytnij=przytnij)
        self.el(G, b, s0, s1, tr0, tr1, z1 - rama, z1, m, przytnij=przytnij)
        cuts = [s0 + L * k / n for k in range(n + 1)]
        for k, c in enumerate(cuts):
            w = rama if k in (0, n) else 0.06
            a, bb = (c, c + w) if k == 0 else ((c - w, c) if k == n else (c - w / 2, c + w / 2))
            self.el(G, b, a, bb, tr0 - 0.02, tr1, z0, z1, m, przytnij=przytnij)
        if naswietle is not None and naswietle < z1 - 0.2:
            self.el(G, b, s0, s1, tr0 - 0.02, tr1, naswietle - 0.04, naswietle + 0.04, m, przytnij=przytnij)
        if drzwi:
            for sc, w in drzwi:
                hz = min(self.Z['drzwi_h'], (naswietle or z1) - 0.05)
                for a, bb in ((sc - w / 2, sc - w / 2 + 0.06), (sc - 0.03, sc + 0.03), (sc + w / 2 - 0.06, sc + w / 2)):
                    self.el(G, b, a, bb, tr0 - 0.05, tr1 + 0.01, z0, hz, m, przytnij=przytnij)
                self.el(G, b, sc - w / 2, sc + w / 2, tr0 - 0.05, tr1 + 0.01, hz - 0.06, hz, m, przytnij=przytnij)
                # pochwyty
                for d in (-0.12, 0.12):
                    self.el(G, b, sc + d - 0.015, sc + d + 0.015, tr1 + 0.01, tr1 + 0.06, z0 + 0.9, z0 + 2.0, m,
                            przytnij=przytnij)

    # ================================================================ WIEŻA
    def wieza(self):
        t0 = time.time()
        sp, Z = self.spec, self.Z
        G = Geo()
        self.Gszklo = Geo()
        self.Gwn = Geo()
        E = sp.E['wieza']
        P, w = E['przeslo_m'], E['filar_m']
        okw, okh = E['okno_m']
        f_od, f_do = E['filary_ciagle_od_do_wzgl']
        g = sp.osc['wieza_m']
        g6 = sp.osc['kondygnacja_6_szklo_za_licem_filarow_m']
        kd = sp.kondygnacje('W')
        Fk = {k['nazwa']: k for k in kd}
        att = sp.dach['W']['attyka']
        obr = Z['attyka_obrobka']
        zt = att - obr                      # wierzch attyki pod obróbką
        z_att0 = sp.dach['W']['pokrycie']   # dół pasa attyki (= najniższe pokrycie dachu)
        zb = Z['z_podstawy']
        biegi = biegi_obrysu(self.obrys['W'], [sp.luk])
        self.biegi_W = biegi
        for b in biegi:
            b.pokrycie = self.pokrycie(b, 'W')
        # identyfikacja biegów: łuk + elewacje wg azymutu normalnej w układzie (u, v)
        az_u = math.degrees(math.atan2(sp.uv['A'][0, 0], sp.uv['A'][1, 0])) % 360   # kierunek +u
        strony = {'E': az_u, 'N': (az_u - 90) % 360, 'W': (az_u + 180) % 360, 'S': (az_u + 90) % 360}
        for b in biegi:
            if b.luk is not None:
                b.nazwa = 'luk'
            else:
                b.nazwa = min(strony, key=lambda k: abs((b.az_normalnej - strony[k] + 180) % 360 - 180))
        # wnęki wejść (z opisu „wsch. wieży, v 1,40–6,80”)
        wneki = {}
        for wn in sp.wneki:
            o = wn['opis']
            if 'wieży' not in o:
                continue
            strona = {'wsch': 'E', 'pd': 'S', 'zach': 'W', 'pn': 'N'}[o.split('.')[0].strip()]
            liczby = _liczby(o.split(',', 1)[1]) if ',' in o else []
            os_ = 'v' if ' v ' in o else 'u'
            wneki.setdefault(strona, []).append((os_, min(liczby), max(liczby), wn['gl']))
        lin = sp.linie
        z_nasw = lin['naswietle_parteru']
        par = Fk['P']
        z_lintel0 = par['sufit']             # spód stropu nad parterem
        kor0, kor1 = sp.kordon_wiezy
        self.podcien_polys = [sp.podcien]
        self.wneki_polys = []
        for b in biegi:
            if b.nazwa == 'luk':
                self._wieza_luk(G, b, kd, zt, zb)
                continue
            # współrzędna lokalna q (u lub v) wzdłuż biegu
            p0 = b.pt(0.0)
            u0, v0 = sp.do_uv(*p0)
            tu = b.styczna(b.L / 2)
            du = sp.uv['Ai'] @ tu
            if abs(du[0]) > abs(du[1]):
                q0, kier, os_ = u0, (1 if du[0] > 0 else -1), 'u'
            else:
                q0, kier, os_ = v0, (1 if du[1] > 0 else -1), 'v'
            qs = lambda q: (q - q0) * kier
            qa, qb = sorted([q0, q0 + kier * b.L])
            # siatka filarów jak na rysunkach (tools/elewacje.py): filar licowany z narożnikiem odniesienia
            # (wsch.: v = 0; pn./pd.: u = 0; zach.: v = 29,70), oś co 2,70 m; filar masywny przy łuku/narożniku
            osie0 = (qb - w / 2) if b.nazwa == 'W' else (qa + w / 2)
            fil = self.filary(qa, qb, P, w, okw, osie0)
            fil_s = sorted([sorted([qs(a), qs(c)]) for a, c in fil])
            q_of_s = (lambda s, q0=q0, kier=kier: q0 + s * kier)
            przesla = [(fil_s[i][1], fil_s[i + 1][0]) for i in range(len(fil_s) - 1) if fil_s[i + 1][0] - fil_s[i][1] > 0.3]
            # zakresy specjalne parteru: podcień (z wielokąta), wnęki (z opisu)
            spec_z = []
            for a, c in b.zakres_z_polygonu(sp.podcien, t_test=-1.0):
                spec_z.append((a, c, sp.podcien_gl, 'podcien'))
            for (osw, lo, hi, gl) in wneki.get(b.nazwa, []):
                if osw != os_:
                    continue
                a, c = sorted([qs(lo), qs(hi)])
                spec_z.append((max(0, a), min(b.L, c), gl, 'wneka'))
                ring = [b.pt(s, 0.02) for s in b.probki(a, c)] + [b.pt(s, -gl) for s in b.probki(a, c)[::-1]]
                self.wneki_polys.append(Polygon(ring).buffer(0))
            # ---- filary (parter + ciągłe od +4,80)
            for a, c in fil_s:
                self.el(G, b, a, c, -g - 0.06, 0.0, zb, z_lintel0, 'granit', rz=0.0)
                zz = [f_od] + [k['F'] for k in kd if k['F'] > f_od + 0.01] + [z_att0]
                for z0_, z1_ in zip(zz[:-1], zz[1:]):
                    self.el(G, b, a, c, -g - 0.06, 0.0, z0_, z1_, 'granit', rz=z0_)
            # ---- nadproże/pas nad parterem (ciągły) i attyka granitowa (ciągła, nad filarami)
            self.el(G, b, 0.0, b.L, -g - 0.02, 0.0, z_lintel0, f_od, 'granit')
            self.el(G, b, 0.0, b.L, -g - 0.02, 0.0, z_att0, zt, 'granit')
            # ---- cokół (pod witrynami), poza zakresami specjalnymi
            wolne = [(0.0, b.L)]
            for a, c, gl, typ in spec_z:
                nowe = []
                for p, q in wolne:
                    if c <= p or a >= q:
                        nowe.append((p, q))
                        continue
                    if a > p:
                        nowe.append((p, a))
                    if c < q:
                        nowe.append((c, q))
                wolne = nowe
            gp = Z['parter_szklo_wieza']
            for p, q in wolne:
                self.el(G, b, p, q, -gp - 0.02, 0.0, zb, 0.0, 'granit', rz=0.0)
            # ---- parter: przęsła zwykłe
            for s0, s1 in przesla:
                if any(not (s1 <= a or s0 >= c) for a, c, _, _ in spec_z):
                    continue
                self.el(G, b, s0, s1, -gp, 0.0, 0.0, 0.05, 'granit', rz=0.0)
                drz = []
                wr = Z['wejscie_rowerowni_S']
                if b.nazwa == 'S' and wr[0] <= q_of_s((s0 + s1) / 2) <= wr[1] + 0.6:
                    drz = [((s0 + s1) / 2, 1.30)]
                self.witryna(G, b, s0, s1, -gp, 0.05, z_lintel0, naswietle=z_nasw, podzial=None, drzwi=drz)
            # ---- zakresy specjalne (podcień, wnęki): szklenie cofnięte, podsufitka, ściany czołowe
            for a, c, gl, typ in spec_z:
                drzwi = []
                if typ == 'wneka' or (typ == 'podcien' and c - a > 6):
                    sc = (a + c) / 2 if typ == 'wneka' else a + 0.5 * (c - a)
                    if typ == 'podcien':
                        # wejście od skweru (podcień pn., u 21–24) – środek zakresu u 22,5
                        sc = qs(22.5) if a <= qs(22.5) <= c else (a + c) / 2
                    drzwi = [(sc, Z['drzwi_w'])]
                self.witryna(G, b, a, c, -gl, 0.0, z_lintel0, naswietle=z_nasw, podzial=1.35, drzwi=drzwi)
                # podsufitka z oprawami
                self.el(G, b, a, c, -gl, -g - 0.02, z_lintel0 - 0.06, z_lintel0, 'wn_sufit')
                for sl in np.arange(a + 0.9, c - 0.5, 2.7):
                    self.el(G, b, sl - 0.6, sl + 0.6, -gl * 0.55 - 0.05, -gl * 0.55 + 0.05, z_lintel0 - 0.075,
                            z_lintel0 - 0.06, 'wn_lampa:cieple')
                # ściany czołowe wnęki (jeśli koniec nie jest bokiem biegu)
                for e, sgn in ((a, -1), (c, 1)):
                    if 0.05 < e < b.L - 0.05:
                        e0, e1 = (e - 0.3, e) if sgn < 0 else (e, e + 0.3)
                        self.el(G, b, e0, e1, -gl - 0.05, -g - 0.06, 0.0, z_lintel0, 'granit', rz=0.0)
            # ---- kondygnacje 1–6 i korona
            for s0, s1 in przesla:
                self._wieza_przeslo(G, b, s0, s1, kd, Fk, g, g6, okh, kor0, kor1, zt, q_c=q_of_s((s0 + s1) / 2))
        # obróbka attyki i attyka (pierścień)
        Wp = self.poly['W']
        ring = Wp.difference(Wp.buffer(-g - 0.1, join_style=2))
        G.pryzma(ring, zt, att, 'metal')
        self.G_W = G
        ob = G.obiekt('wieza_elewacje', self.kol['wieza'], self.mat, self.DZ)
        self.Gszklo.obiekt('wieza_szklo', self.kol['wieza'], self.mat, self.DZ)
        self.Gwn.obiekt('wieza_rolety_parapety', self.kol['wnetrza'], self.mat, self.DZ)
        self.czas('wieza', t0)
        return ob

    def _wieza_przeslo(self, G, b, s0, s1, kd, Fk, g, g6, okh, kor0, kor1, zt, q_c=None):
        """Przęsło wieży na kondygnacjach 1–6 i w koronie S (wg ``tools/elewacje.py``: parapet 0,90; kond. 5 nad
        kordonem; kond. 6 – pas cienia 0,40 m za licem; korona: okna hali 5,0 m lub komisji 4,2 m, lamele pd.)."""
        Z = self.Z
        gp = Z['plycina_wiezy_gl']
        m = 'metal'
        sill = Z['wieza_parapet']
        poprz = None
        cz = Z['czerpnie_kond1_S']
        czerpnia = b.nazwa == 'S' and q_c is not None and cz[0] <= q_c <= cz[1]
        F_S = Fk['S']['F']
        for k in kd:
            nm = k['nazwa']
            if nm in ('P', 'S'):
                continue
            F = k['F']
            if nm == '6':
                # „kondygnacja cienia”: szkło i metal 0,40 m za licem filarów, od posadzki kond. 6 do korony
                self.el(G, b, s0, s1, -gp - 0.03, -gp, poprz, F, m)
                self.el(G, b, s0, s1, -g6, -gp + 0.02, F - 0.03, F, m)                  # półka dolna
                a, c = Z['kond6_szklo']
                self.el(G, b, s0, s1, -g6 - 0.03, -g6, F, F + a, m)
                self.okno(G, b, s0, s1, -g6, F + a, F + c, wewn_do=-g - 0.05)
                self.el(G, b, s0, s1, -g6 - 0.03, -g6, F + c, F_S, m)
                self.el(G, b, s0, s1, -g6, -Z['korona_wypelnienie_gl'], F_S, F_S + 0.03, m)   # podsufitka
                poprz = None
                continue
            zo0 = F + sill
            z_d = F if nm == '1' else poprz
            if kor0 - 0.01 <= F <= kor1:
                # kordon granitowy między filarami (w linii gzymsu skrzydła); okno nad kordonem
                self.el(G, b, s0, s1, -gp - 0.03, -gp, z_d, kor0, m)
                self.el(G, b, s0, s1, -g - 0.02, 0.0, kor0, kor1, 'granit', rz=kor0)
                zo0 = kor1
            else:
                self.el(G, b, s0, s1, -gp - 0.03, -gp, z_d, zo0, m)
                self.el(G, b, s0, s1, -g, -gp + 0.035, zo0 - 0.03, zo0, m)             # parapet Al z kapinosem
            zo1 = zo0 + okh
            self.el(G, b, s0, s1, -g, -gp, zo1, zo1 + 0.02, m)                          # podsufitka ościeża
            if czerpnia and nm == '1':
                # żaluzja czerpni (tylko od dziedzińca) zamiast okna
                self.el(G, b, s0, s1, -g - 0.03, -g, zo0, zo1, 'metal:fuga')
                for zz in np.arange(zo0 + 0.1, zo1 - 0.05, 0.17):
                    self.el(G, b, s0, s1, -g, -g + 0.06, zz - 0.035, zz, m)
            else:
                self.okno(G, b, s0, s1, -g, zo0, zo1)
            poprz = zo1
        # ---- korona S
        typ = Z['korona_typ'].get(b.nazwa, 'komisje')
        z_att0 = self.spec.dach['W']['pokrycie']
        gw = Z['korona_wypelnienie_gl']
        z_par = F_S + Z['korona_parapet']
        h = Z['korona_okno_hala'] if typ == 'hala' else Z['korona_okno_komisje']
        ryg = Z['korona_rygiel_hala'] if typ == 'hala' else Z['korona_rygiel_komisje']
        ztop = z_par + h
        self.el(G, b, s0, s1, -g - 0.02, -gw, F_S + 0.03, z_par, 'granit', rz=F_S)
        self.el(G, b, s0, s1, -g, -gw + 0.035, z_par - 0.03, z_par, m)
        self.okno(G, b, s0, s1, -g, z_par, ztop, typ='korona', rygiel=z_par + ryg, roleta=False, wewn_do=-g - 0.06)
        self.el(G, b, s0, s1, -g, -gw, ztop, ztop + 0.02, m)
        if typ == 'komisje_lamele':
            zl0, zl1, lw, lr = Z['korona_lamele']
            self.el(G, b, s0, s1, -g - 0.02, -gw, ztop + 0.02, zl0, 'granit', rz=ztop)
            self.el(G, b, s0, s1, -g - 0.03, -g, zl0, zl1, 'metal:fuga')
            self.el(G, b, s0, s1, -g, -gw, zl0 - 0.02, zl0, m)
            self.el(G, b, s0, s1, -g, -gw, zl1, zl1 + 0.02, m)
            q = s0 + 0.06
            while q + lw < s1 - 0.02:
                self.el(G, b, q, q + lw, -0.40, -gw - 0.02, zl0, zl1, 'cer:lamele_korony:gladka', rz=zl0)
                q += lr
            self.el(G, b, s0, s1, -g - 0.02, -gw, zl1 + 0.02, z_att0, 'granit', rz=zl1)
        else:
            self.el(G, b, s0, s1, -g - 0.02, -gw, ztop + 0.02, z_att0, 'granit', rz=ztop)

    def _wieza_luk(self, G, b, kd, zt, zb):
        """Łuk narożnika R 14 (wg ``tools/elewacje.py``): podcień z kolumnami co 15° i szkleniem na R 11; pas
        granitowy nad podcieniem z napisem (4,80–6,10); kond. 1–5 – pasmo ceramiczne 1,30 m (F…F+1,30) i okno
        wstęgowe (F+1,30…F+3,75, słupki co 1,35 m); kond. 6 – pas cienia 0,40 m; korona – lamele 0,25 × 0,60 co
        0,90 m (R 13,4–14,0) przed szkłem; attyka granitowa."""
        sp, Z = self.spec, self.Z
        R = b.luk[2]
        g = sp.osc['wieza_m']
        g6 = sp.osc['kondygnacja_6_szklo_za_licem_filarow_m']
        Fk = {k['nazwa']: k for k in kd}
        z_l0 = Fk['P']['sufit']
        gl = R - sp.podcien_R
        m_c = 'cer:luk:gladka'
        pas = sp.luk_pas
        z_att0 = sp.dach['W']['pokrycie']
        # ---- parter: kolumny co 15° (R 13,5), szklenie R 11, podsufitka drewniana z oprawami
        a0, da = b.luk[3], b.luk[4]
        deg = sp.luk_slupy_deg
        nk = int(round(abs(math.degrees(da)) / deg))
        ws, wg = Z['luk_slupy_szer'], Z['luk_slupy_gl']
        tc = -(R - sp.luk_slupy_R)
        for i in range(1, nk):
            sc = b.L * i / nk
            self.el(G, b, sc - ws / 2, sc + ws / 2, tc - wg / 2, min(0.0, tc + wg / 2), zb, z_l0, 'granit', rz=0.0)
        smid = b.L / 2
        self.witryna(G, b, 0.0, b.L, -gl, 0.0, z_l0, naswietle=sp.linie['naswietle_parteru'], podzial=1.4,
                     drzwi=[(smid - 1.0, Z['drzwi_w']), (smid + 1.0, Z['drzwi_w'])])
        self.el(G, b, 0.0, b.L, -gl, -g - 0.02, z_l0 - 0.06, z_l0, 'wn_drewno:jasne', maks=0.5)
        for ang in np.arange(0.5, nk, 0.5):
            sc = b.L * ang / nk
            self.el(G, b, sc - 0.35, sc + 0.35, -gl * 0.5 - 0.05, -gl * 0.5 + 0.05, z_l0 - 0.075, z_l0 - 0.06,
                    'wn_lampa:cieple')
        # ---- kond. 1–5: pasmo (kond. 1: granit z napisem) + okno wstęgowe
        F6 = Fk['6']['F']
        nazwy = [k['nazwa'] for k in kd if k['nazwa'] not in ('P', 'S') and k['F'] < F6 - 0.01]
        for i, nm in enumerate(nazwy):
            k = Fk[nm]
            F = k['F']
            zo0, zo1 = F + pas, (Fk[nazwy[i + 1]]['F'] if i + 1 < len(nazwy) else F6)
            if i == 0:
                self.el(G, b, 0.0, b.L, -g - 0.02, 0.0, z_l0, zo0, 'granit', maks=0.3)
                self.napis(b, (z_l0 + zo0) / 2)
            else:
                self.el(G, b, 0.0, b.L, -g - 0.02, 0.0, F, zo0, m_c, maks=0.3, rz=F)
            self.el(G, b, 0.0, b.L, -g, 0.0, zo0 - 0.02, zo0, 'metal', maks=0.3)          # obróbka parapetu
            self.szyba(self.Gszklo, b, 0.0, b.L, -g, zo0, zo1, 'szklo:biuro')
            self.el(G, b, 0.0, b.L, -g - 0.04, -g + 0.03, zo0, zo0 + 0.06, 'metal', maks=0.3)
            self.el(G, b, 0.0, b.L, -g - 0.04, -g + 0.03, zo1 - 0.06, zo1, 'metal', maks=0.3)
            # strefa stropu za szkłem (shadow box)
            self.el(self.Gwn, b, 0.0, b.L, -g - 0.09, -g - 0.06, k['sufit'], zo1, 'metal:fuga', maks=0.3)
            ns = max(2, int(round(b.L / Z['luk_slupek_co'])))
            for j in range(1, ns):
                sc = b.L * j / ns
                self.el(G, b, sc - 0.035, sc + 0.035, -g - 0.05, -g + 0.04, zo0, zo1, 'metal')
            for j in range(ns):
                if self.rng.random() < self.o['rolety'] * 0.6:
                    sa, sb = b.L * j / ns + 0.04, b.L * (j + 1) / ns - 0.04
                    zr = k['sufit'] - (k['sufit'] - zo0 - 0.1) * self.rng.uniform(0.2, 0.7)
                    self.el(self.Gwn, b, sa, sb, -g - 0.05, -g - 0.04, zr, k['sufit'], 'roleta')
        # ---- kond. 6: pas cienia (0,40 m) – ciągły z elewacjami prostymi
        F_S = Fk['S']['F']
        a, c = Z['kond6_szklo']
        self.el(G, b, 0.0, b.L, -g, -g6 + 0.02, F6, F6 + 0.03, 'metal', maks=0.3)
        self.el(G, b, 0.0, b.L, -g6 - 0.03, -g6, F6 + 0.03, F6 + a, 'metal', maks=0.3)
        self.szyba(self.Gszklo, b, 0.0, b.L, -g6, F6 + a, F6 + c, 'szklo:biuro')
        self.el(G, b, 0.0, b.L, -g6 - 0.03, -g6, F6 + c, F_S, 'metal', maks=0.3)
        ns = max(2, int(round(b.L / Z['luk_slupek_co'])))
        for j in range(1, ns):
            sc = b.L * j / ns
            self.el(G, b, sc - 0.035, sc + 0.035, -g6 - 0.05, -g6 + 0.04, F6 + a, F6 + c, 'metal')
        self.el(self.Gwn, b, 0.0, b.L, -g - 0.05, -g6 - 0.035, F6 + a - 0.03, F6 + a, 'wn_sciana', maks=0.3)
        self.el(self.Gwn, b, 0.0, b.L, -g - 0.05, -g6 - 0.035, Fk['6']['sufit'], F6 + c, 'metal:fuga', maks=0.3)
        # ---- korona: szkło (R szyb ≤ 13,4) za lamelami 0,25 × 0,60 co 0,90; płyta ciemna w strefie dachu
        lw, lg, lr = sp.lamela
        t_sz = min(-(R - sp.szyba_korony_R), -lg - 0.03)
        z_sala = Fk['S']['sufit']
        self.szyba(self.Gszklo, b, 0.0, b.L, t_sz, F_S, z_sala, 'szklo:korona')
        nm_ = max(2, int(round(abs(math.degrees(da)) / 7.5)))
        for j in range(nm_ + 1):
            sc = b.L * j / nm_
            self.el(G, b, max(0, sc - 0.04), min(b.L, sc + 0.04), t_sz - 0.06, t_sz + 0.02, F_S, z_sala, 'metal')
        self.el(G, b, 0.0, b.L, t_sz - 0.03, t_sz + 0.01, z_sala, z_att0, 'metal:fuga', maks=0.3)
        self.el(G, b, 0.0, b.L, t_sz, -g6 + 0.02, F_S - 0.03, F_S, 'metal', maks=0.3)
        nl = max(2, int(round(b.L / lr)))
        for j in range(nl):
            sc = b.L * (j + 0.5) / nl
            self.el(G, b, sc - lw / 2, sc + lw / 2, -lg, 0.0, F_S, z_att0, 'cer:lamele_korony:gladka', rz=F_S)
        # attyka granitowa (ciągła z attyką elewacji prostych)
        self.el(G, b, 0.0, b.L, -g - 0.02, 0.0, z_att0, zt, 'granit', maks=0.3)

    def napis(self, b, zc):
        """Napis w granitowym nadprożu Bramy Mostowej – litery wzdłuż łuku (od lewej do prawej patrząc z zewnątrz)."""
        txt = self.Z['napis']
        if not txt:
            return
        cu = bpy.data.curves.new('napis', 'FONT')
        cu.body = txt
        for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                  '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'):
            if Path(f).exists():
                try:
                    cu.font = bpy.data.fonts.load(f, check_existing=True)
                    break
                except Exception:
                    pass
        cu.size = self.Z['napis_h'] / 0.73
        cu.space_character = 1.35
        cu.extrude = 0.004
        cu.align_x = 'CENTER'
        cu.align_y = 'CENTER'
        ob = bpy.data.objects.new('napis_tmp', cu)
        self.sc.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        V = np.array([v.co[:] for v in me.vertices])
        Gn = Geo()
        smid = b.L / 2
        Vn = []
        for x, y, z in V:
            p = b.pt(smid + x, 0.002 + z)
            Vn.append((p[0], p[1], zc + y))
        for poly in me.polygons:
            ids = list(poly.vertices)
            Gn.face([Vn[i] for i in ids], [(0, 0)] * len(ids), 'litery')
        bpy.data.meshes.remove(me)
        Gn.obiekt('napis_brama_mostowa', self.kol['wieza'], self.mat, self.DZ)

    # ================================================================ SKRZYDŁO i SEGMENT (porządek kamieniczny)
    def kamieniczny(self, bryla):
        t0 = time.time()
        sp, Z = self.spec, self.Z
        G = Geo()
        self.Gszklo = Geo()
        self.Gwn = Geo()
        Es = sp.E['skrzydlo']
        os_, fw = Es['os_m'], Es['filar_m']
        okw, okh = Es['okno_m']
        sill = Es['parapet_m']
        osc = sp.osc['skrzydlo_i_segment_m']
        kd = sp.kondygnacje(bryla)
        Fk = {k['nazwa']: k for k in kd}
        lin = sp.linie
        z_nasw = lin['naswietle_parteru']
        z_kor1 = lin['kordon']
        z_kor0 = z_kor1 - Z['kordon_skrzydla_h']
        z_gz0 = lin['spod_gzymsu']
        z_att = sp.dach[bryla]['attyka']
        z_fr0 = z_att - Z['gzyms_wys']
        zb = Z['z_podstawy']
        par = Fk['P']
        z_suf_p = par['sufit']
        gp = Z['parter_szklo_skrzydlo']
        granica_oi = self.oi.exterior
        biegi = biegi_obrysu(self.obrys[bryla])
        for b in biegi:
            b.pokrycie = self.pokrycie(b, bryla)
        setattr(self, 'biegi_' + bryla, biegi)
        # posesje
        seg = Es['segmenty_m']
        granice = [0.0]
        for k in ('M1', 'M2', 'M3', 'M4'):
            granice.append(granice[-1] + seg[k])
        relief = Es['relief_filarow_m']
        faktury = {'M1': 'gladka', 'M2': 'ryflowana', 'M3': 'cieniowana', 'M4': 'ryflowana'}

        def posesja(q):
            for i, k in enumerate(('M1', 'M2', 'M3', 'M4')):
                if q < granice[i + 1] - 1e-6:
                    return k
            return 'M4'
        sd = sp.sd
        brama_poly = sp.brama if bryla == 'M' else None
        self.brama_biegi = getattr(self, 'brama_biegi', [])
        for b in biegi:
            if b.pokrycie and all(c - a >= b.L - 0.1 and zc >= z_att - 0.01 for a, c, zc in b.pokrycie):
                # elewacja w całości zasłonięta – ściana ślepa (do attyki)
                self.el(G, b, 0.0, b.L, -0.40, 0.0, zb, z_att, 'beton', przytnij=False)
                continue
            # ślepe fragmenty zasłonięte (do wysokości pokrycia)
            for a, c, zc in b.pokrycie:
                self.el(G, b, a, c, -0.40, 0.0, zb, min(zc, z_att), 'beton', przytnij=False)
            # ---- wysięg gzymsu (rewizja 17.11): przy granicy (< 0,30 m) bez wysięgu, dziób pn. 0,25, inne 0,30
            d_gr = min(granica_oi.distance(Point(*b.pt(sx, 0.0))) for sx in np.linspace(0, b.L, 9))
            if bryla == 'M' and b.krzywy:
                wys = Z['gzyms_wysieg_pn']
            elif d_gr < 0.30:
                wys = Z['gzyms_wysieg_ulica']
            else:
                wys = Z['gzyms_wysieg']
            tg = -wys - 0.75                   # głębokość tylnej ściany elementów trzonu
            ulica = bryla == 'M' and len(b.P) == 2 and b.L > 30 and d_gr < 0.30
            # ---- układ osi
            if bryla == 'M' and b.luk is None and len(b.P) == 2 and b.L > 30:
                # elewacja frontowa lub dziedzińcowa: osie od styku z Mazowiecką 19 (s = 0 skrzydła)
                p0, p1 = b.P[0], b.P[-1]
                s_a = sp.do_uv(*p0, uk=sd)[0]
                s_b = sp.do_uv(*p1, uk=sd)[0]
                kier = 1 if s_b > s_a else -1
                q0 = s_a
                qs = lambda q, q0=q0, kier=kier: (q - q0) * kier
                qa, qb = sorted([s_a, s_b])
                posesje = ulica
                osie0 = 0.0
                os_b = os_
            elif bryla == 'S':
                # segment: osie 2,025 m wycentrowane na elewacji (tools/elewacje.py)
                qa, qb = 0.0, b.L
                qs = lambda q: q
                n = max(1, int((b.L - 0.4) / os_))
                os_b = os_
                osie0 = (b.L - n * os_) / 2
                posesje = False
                q0, kier = 0.0, 1
            else:
                qa, qb = 0.0, b.L
                qs = lambda q: q
                n = max(1, int(round(b.L / os_)))
                os_b = b.L / n
                osie0 = 0.0
                posesje = bryla == 'M' and b.krzywy
                q0, kier = 0.0, 1
            fil = self.filary(qa, qb, os_b, fw, okw, osie0)
            fil_s = sorted([sorted([qs(a), qs(c)]) for a, c in fil])
            if ulica:
                # posesja wg współrzędnej s układu skrzydła (front od Mazowieckiej)
                ton = (lambda s, b=b: posesja(sp.do_uv(*b.pt(s, 0.0), uk=sd)[0]))
            elif bryla == 'M':
                ton = (lambda s, kr=b.krzywy: 'M4' if kr else 'M3')      # dziób – M4; dziedziniec – M3 (rysunki)
            else:
                ton = (lambda s: 'segment')
            # brama ogrodowa (zakres z wielokąta)
            brama_z = b.zakres_z_polygonu(brama_poly, t_test=-0.8) if brama_poly is not None else []
            # wnęka wejścia konferencyjnego w dziobie NW (bieg krzywy skrzydła)
            wneka_z = []
            if bryla == 'M' and b.krzywy and b.luk is None:
                wneka_z = [(b.L / 2 - Z['nos_wejscie_szer'] / 2, b.L / 2 + Z['nos_wejscie_szer'] / 2,
                            next(w['gl'] for w in sp.wneki if 'skrzydła' in w['opis']))]
                ring = [b.pt(s, 0.02) for s in b.probki(*wneka_z[0][:2])] + \
                       [b.pt(s, -wneka_z[0][2]) for s in b.probki(*wneka_z[0][:2])[::-1]]
                self.wneki_polys.append(Polygon(ring).buffer(0))
            # brama garażu (segment, elewacja wsch.)
            garaz_z = []
            if bryla == 'S' and abs(((b.az_normalnej - (math.degrees(math.atan2(sp.uv['A'][0, 0], sp.uv['A'][1, 0])) % 360)) + 180) % 360 - 180) < 20:
                # v (układ wieży) → s biegu
                v_a = sp.do_uv(*b.P[0])[1]
                v_b = sp.do_uv(*b.P[-1])[1]
                kv = 1 if v_b > v_a else -1
                lo, hi = Z['brama_garazu_v'] if Z.get('brama_garazu_v') else sp.brama_garazu_v
                garaz_z = [tuple(sorted([(lo - v_a) * kv, (hi - v_a) * kv]))]
            sciana_pd_seg = bryla == 'S' and abs(((b.az_normalnej - (math.degrees(math.atan2(sp.uv['A'][0, 0], sp.uv['A'][1, 0])) % 360 + 90)) + 180) % 360 - 180) < 25
            # ---- PARTER (cokół): filary granitowe co 2 osie, witryny z naświetlem, kordon
            n_os = max(1, int(round((qb - qa) / os_b)))
            os_p = 2 * os_b if (n_os % 2 == 0 or n_os > 12) else os_b       # filary cokołu co 2 osie (4,05 m)
            fil_p = self.filary(qa, qb, os_p, fw, os_p - fw - 0.2, osie0) if not garaz_z else []
            fil_ps = sorted([sorted([qs(a), qs(c)]) for a, c in fil_p])
            spec_p = [(a, c, 'brama') for a, c in brama_z] + [(a, c, 'wneka') for a, c, _ in wneka_z]
            if garaz_z:
                # elewacja wsch. segmentu: parter pełny z granitu, brama garażu 4,0 m (pn.) i drzwi techniczne (pd.)
                self._parter_obslugi(G, b, garaz_z[0], z_kor0)
                fil_ps = []
            for a, c in fil_ps:
                # filary bramy ogrodowej: portal granitowy (filar przecięty przez otwór bramy – zostaje poza nim)
                for p, q in self._odejmij([(a, c)], [(x, y) for x, y, _ in spec_p]):
                    self.el(G, b, p, q, -0.70, 0.0, zb, z_kor0, 'granit', rz=0.0)
            przesla_p = [(fil_ps[i][1], fil_ps[i + 1][0]) for i in range(len(fil_ps) - 1)
                         if fil_ps[i + 1][0] - fil_ps[i][1] > 0.3]
            # kordon (ciągły) + pas nadproża witryn (nad bramą – nadproże portalu)
            self.el(G, b, 0.0, b.L, -0.72, 0.0, z_kor0, z_kor1, 'granit')
            wolne = self._odejmij([(0.0, b.L)], [(x, y) for x, y, _ in spec_p])
            if not garaz_z:
                for p, q in self._odejmij([(0.0, b.L)], [(x, y) for x, y, t in spec_p if t == 'brama']):
                    self.el(G, b, p, q, -0.72, -0.05, z_suf_p, z_kor0, 'granit')
                for p, q in wolne:
                    self.el(G, b, p, q, -gp - 0.02, 0.0, zb, 0.0, 'granit', rz=0.0)
            for s0, s1 in przesla_p:
                kaw = self._odejmij([(s0, s1)], [(x, y) for x, y, _ in spec_p])
                for p, q in kaw:
                    if sciana_pd_seg:
                        self.el(G, b, p, q, -0.70, -0.02, 0.0, z_suf_p, 'granit', rz=0.0)
                        continue
                    self.el(G, b, p, q, -gp, 0.0, 0.0, 0.08, 'granit', rz=0.0)
                    self.witryna(G, b, p, q, -gp, 0.08, z_suf_p, naswietle=z_nasw, podzial=None)
            for a, c, typ in spec_p:
                if typ == 'brama':
                    self._brama_ogrodowa(G, b, a, c, z_suf_p, z_kor0)
                else:
                    gl = wneka_z[0][2]
                    self.witryna(G, b, a, c, -gl, 0.0, z_suf_p, naswietle=z_nasw, podzial=1.2,
                                 drzwi=[((a + c) / 2, Z['drzwi_w'])])
                    self.el(G, b, a, c, -gl, -0.70, z_suf_p - 0.06, z_suf_p, 'wn_sufit')
                    self.el(G, b, a, c, -gl, -0.05, -0.3, 0.0, 'bruk')
                    for e in (a, c):
                        self.el(G, b, e - 0.15, e + 0.15, -gl - 0.05, -0.70, 0.0, z_suf_p, 'granit', rz=0.0)
            # ---- TRZON (kond. 1–4): filary ceramiczne, płyciny, okna; szczeliny między posesjami
            granice_s = sorted([qs(x) for x in granice[1:]]) if ulica else []
            granice_s = [x for x in granice_s if 0.5 < x < b.L - 0.5]
            m1_s = None
            if ulica:
                # M1 – pierwsza oś przy Maz. 19 cofnięta
                m1_s = sorted([qs(0.0), qs(os_ - fw / 2)])
            kond = [k for k in kd if k['nazwa'] != 'P']

            def lico(s):
                """(lico filara, lico płyciny) dla s."""
                t_f = -wys
                t_p = -wys - relief.get(ton(s), 0.0) if posesje else -wys       # relief: cofnięcie płycin
                if sciana_pd_seg:
                    t_p = -wys - 0.12
                if m1_s and m1_s[0] - 1e-6 <= s <= m1_s[1] + 1e-6:
                    t_f -= Z['m1_pierwsza_os_cofn']
                    t_p -= Z['m1_pierwsza_os_cofn']
                return t_f, t_p
            # filary (z podziałem na szczeliny posesji)
            fw2 = Z['fuga_posesji_szer'] / 2
            for a, c in fil_s:
                kaw = [(a, c)]
                for gs in granice_s:
                    if a < gs < c:
                        kaw = self._odejmij(kaw, [(gs - fw2, gs + fw2)])
                        self.el(G, b, gs - fw2, gs + fw2, tg, -wys - Z['fuga_posesji_cofn'], z_kor1, z_fr0, 'metal:fuga')
                for p, q in kaw:
                    if m1_s and p < m1_s[1] - 1e-6 < q:
                        parts = [(p, m1_s[1]), (m1_s[1], q)]
                    else:
                        parts = [(p, q)]
                    for pp, qq in parts:
                        tf, _ = lico((pp + qq) / 2)
                        mt = 'cer:%s:%s' % (ton((pp + qq) / 2), faktury.get(ton((pp + qq) / 2), 'gladka'))
                        for k in kond:
                            z1_ = k['Fn'] if k is not kond[-1] else z_fr0
                            self.el(G, b, pp, qq, tg, tf, k['F'], min(z1_, z_fr0), mt, rz=k['F'])
            przesla = [(fil_s[i][1], fil_s[i + 1][0]) for i in range(len(fil_s) - 1) if fil_s[i + 1][0] - fil_s[i][1] > 0.3]
            for s0, s1 in przesla:
                tf, tp = lico((s0 + s1) / 2)
                tgl = tf - osc
                mt = 'cer:%s:%s' % (ton((s0 + s1) / 2), faktury.get(ton((s0 + s1) / 2), 'gladka'))
                if sciana_pd_seg:
                    # ściana pd. segmentu – pełna, relief ceramiczny (pilastry 0,12 m) + fugi z metalu
                    self.el(G, b, s0, s1, tg, tp, z_kor1, z_fr0, mt, rz=z_kor1)
                    for e in (s0, s1):
                        self.el(G, b, e - 0.015, e + 0.015, tg, tp + 0.005, z_kor1, z_fr0, 'metal:fuga')
                    continue
                poprz = z_kor1
                for k in kond:
                    F = k['F']
                    zo0 = F + sill
                    zo1 = zo0 + okh
                    if zo1 > z_fr0 - 0.05:
                        zo1 = z_fr0 - 0.05
                    self.el(G, b, s0, s1, tg, tp, poprz, zo0, mt, rz=F if poprz > F - 1e-6 else poprz)
                    self.el(G, b, s0, s1, tgl, tp + 0.035, zo0 - 0.03, zo0, 'metal')        # parapet Al
                    self.el(G, b, s0, s1, tgl, tp, zo1, zo1 + 0.02, 'metal')                 # nadproże
                    # ościeża (boki) – ceramika (przy płycinach cofniętych względem filarów)
                    self.okno(G, b, s0, s1, tgl, zo0, zo1, typ='biuro', slupek=False, rygiel=zo0 + okh * 0.70,
                              wewn_do=min(tgl - 0.08, -0.75))
                    poprz = zo1
                self.el(G, b, s0, s1, tg, tp, poprz, z_fr0, mt, rz=poprz)
            # ---- fryz i gzyms-attyka (granit, ciągłe); przy granicy: architraw w licu + fryz cofnięty 0,15 m
            mk = 0.35 if b.krzywy else None
            if wys < 0.01:
                z_fr1 = z_gz0 - 0.35
                self.el(G, b, 0.0, b.L, tg, 0.0, z_fr0, z_fr1, 'granit', maks=mk)
                self.el(G, b, 0.0, b.L, tg, -Z['fryz_cofniecie'], z_fr1, z_gz0, 'granit', maks=mk)
            else:
                self.el(G, b, 0.0, b.L, tg, -wys, z_fr0, z_gz0, 'granit', maks=mk)
            self.el(G, b, 0.0, b.L, tg, 0.0, z_gz0, z_att - 0.05, 'granit', maks=mk)
            self.el(G, b, 0.0, b.L, -0.07, 0.0, z_gz0 - 0.03, z_gz0, 'granit', maks=mk)     # kapinos
            self.el(G, b, 0.0, b.L, tg, 0.0, z_att - 0.05, z_att, 'metal', maks=mk)
        nm = {'M': 'skrzydlo', 'S': 'segment'}[bryla]
        ob = G.obiekt(nm + '_elewacje', self.kol[nm], self.mat, self.DZ)
        self.Gszklo.obiekt(nm + '_szklo', self.kol[nm], self.mat, self.DZ)
        self.Gwn.obiekt(nm + '_rolety_parapety', self.kol['wnetrza'], self.mat, self.DZ)
        self.czas(nm, t0)
        return ob

    def _parter_obslugi(self, G, b, brama, z_kor0):
        """Parter elewacji wsch. segmentu (rysunek elewacji, rewizja 17.11): pełny granit, brama garażu 4,0 m
        (żaluzja stalowa, próg w poziomie chodnika 119,10), drzwi trafo / rozdzielni / odpadów w części pd."""
        Z = self.Z
        zp = Z['brama_garazu_prog_npm'] - self.spec.zero
        hb = Z['brama_garazu_h']
        hd = Z['drzwi_segmentu_h']
        otw = [(brama[0], brama[1], hb, 0.40)] + [(a, c, hd, 0.18) for a, c in Z['drzwi_segmentu']]
        for p, q in self._odejmij([(0.0, b.L)], [(a, c) for a, c, _, _ in otw]):
            self.el(G, b, p, q, -0.70, 0.0, Z['z_podstawy'], z_kor0, 'granit', rz=0.0)
        for a, c, h, gl in otw:
            self.el(G, b, a, c, -0.70, 0.0, zp + h, z_kor0, 'granit', rz=zp + h)
            self.el(G, b, a, c, -0.70, 0.0, Z['z_podstawy'], zp, 'granit', rz=0.0)
            self.el(G, b, a, c, -gl - 0.04, -gl, zp, zp + h, 'metal:fuga')
            for zz in np.arange(zp + 0.30, zp + h - 0.05, 0.30 if gl < 0.3 else 0.15):
                self.el(G, b, a + 0.03, c - 0.03, -gl, -gl + 0.02, zz - 0.02, zz, 'metal')
            self.el(G, b, a, c, -gl, 0.0, zp + h, zp + h + 0.02, 'metal')

    @staticmethod
    def _odejmij(kaw, wyc):
        for a, c in wyc:
            nowe = []
            for p, q in kaw:
                if c <= p or a >= q:
                    nowe.append((p, q))
                    continue
                if a > p:
                    nowe.append((p, a))
                if c < q:
                    nowe.append((c, q))
            kaw = nowe
        return [(p, q) for p, q in kaw if q - p > 0.01]

    def _brama_ogrodowa(self, G, b, a, c, z_suf_p, z_kor0):
        """Portal bramy ogrodowej na elewacji: nadproże granitowe nad otworem (posadzka w poziomie chodnika)."""
        z_b = self.spec.brama_h
        # poziom posadzki bramy: chodnik (pikiety) – wg JSON brama ma 4,80 m wysokości od chodnika 118,70
        z0 = -0.60
        z_top = z0 + z_b
        z_top = min(z_top, z_suf_p)
        # nadproże portalu (granit) – węgary portalu tworzą połówki filarów cokołu po obu stronach otworu
        self.el(G, b, a, c, -0.72, 0.0, z_top, z_kor0, 'granit', rz=z_top)
        self.el(G, b, a, c, -0.72, -0.02, z_top - 0.02, z_top, 'metal')

    # ================================================================ wnętrza
    def wnetrza(self):
        t0 = time.time()
        sp, Z = self.spec, self.Z
        G = Geo()
        gd = Z['glebokosc_pokoju']
        rng = self.rng
        # ---------------- WIEŻA
        Wp = self.poly['W']
        kd = sp.kondygnacje('W')
        g = sp.osc['wieza_m']
        hall = Wp.buffer(-Z['parter_szklo_wieza'] - 0.03, join_style=2)
        for pp in self.podcien_polys + self.wneki_polys:
            hall = hall.difference(pp.buffer(0.03, join_style=2))
        hall = hall.difference(self.poly['M'].buffer(0.1)).difference(self.poly['S'].buffer(0.1))
        # parter wieży: posadzka holu, sufit, trzony A i B, słupy, lada informacji, lapidarium
        G.pryzma(hall, -0.4, 0.0, 'wn_kamien', boki=False, dno=False)
        suf = kd[0]['sufit']
        rdz = []
        for k in ('A', 'B'):
            r = sp.K['rdzenie'][k]
            rp = Polygon(r['obrys_en']).buffer(0)
            rdz.append(rp)
            G.pryzma(rp, 0.0, suf, 'wn_drewno', gora=False, dno=False)
        # słupy w siatce (u, v) wieży
        osu = sp.K['siatka']['wieza']['osie_u']
        osv = sp.K['siatka']['wieza']['osie_v']
        for u in osu[1:-1]:
            for v in osv[1:-1]:
                e, n = sp.z_uv(u, v)
                c = Point(e, n).buffer(0.25, 16)
                if hall.contains(c) and not any(r.intersects(c) for r in rdz):
                    G.pryzma(c, 0.0, suf, 'beton', gora=False, dno=False)
        # sufit holu z oprawami (ciepłe) – siatka co 2,7 m w układzie (u, v)
        for u in np.arange(1.35, 40, 2.7):
            for v in np.arange(1.35, 29.7, 2.7):
                e, n = sp.z_uv(u, v)
                c = Point(e, n).buffer(0.22, 8)
                if hall.contains(c):
                    G.pryzma(c, suf - 0.03, suf - 0.005, 'wn_lampa:cieple', boki=True, dno=True, gora=False)
        # lada informacji (niska) przy osi przekątnej
        e, n = sp.z_uv(27.5, 19.5)
        lada = Point(e, n).buffer(1.6, 24).difference(Point(e, n).buffer(0.9, 24))
        lada = lada.intersection(Polygon([(e, n), (e + 5, n), (e + 5, n + 5), (e, n + 5)]))
        G.pryzma(lada.buffer(0), 0.0, 0.90, 'wn_drewno:jasne')
        # lapidarium – ściana witryn przy trzonie A (świecące gabloty)
        A = rdz[0]
        lp = A.buffer(0.6, join_style=2).difference(A.buffer(0.1, join_style=2))
        G.pryzma(lp, 0.0, 0.9, 'wn_kamien')
        G.pryzma(lp, 0.9, 2.3, 'wn_lampa:cieple', gora=False, dno=False)
        # strop nad parterem (spód = sufit holu i podcienia)
        G.pryzma(Wp.buffer(-g - 0.03, join_style=2), suf, kd[1]['F'], 'wn_sufit', mat_gora='wn_podloga')
        self._ring(G, 'W', Wp, kd[1:], g, gd, rng)
        self._korona(G, Wp, kd, g)
        # ---------------- SKRZYDŁO, SEGMENT
        for br in ('M', 'S'):
            Pp = self.poly[br]
            kdb = sp.kondygnacje(br)
            osc = Z['gzyms_wysieg'] + sp.osc['skrzydlo_i_segment_m']
            podl = Pp.buffer(-Z['parter_szklo_skrzydlo'] - 0.03, join_style=2)
            if br == 'M':
                podl = podl.difference(sp.brama.buffer(0.05, join_style=2))
                for pp in self.wneki_polys:
                    podl = podl.difference(pp.buffer(0.03, join_style=2))
            G.pryzma(podl, -0.4, 0.0, 'wn_kamien', boki=False, dno=False)
            suf = kdb[0]['sufit']
            jadro = Pp.buffer(-gd - 0.6, join_style=2)
            if br == 'M':
                jadro = jadro.difference(sp.brama.buffer(0.3))
            if not jadro.is_empty:
                G.pryzma(jadro, 0.0, suf, 'wn_sciana', gora=False, dno=False)
            for c in self._siatka_lamp(podl.difference(jadro.buffer(0.3)), 2.6):
                G.pryzma(c, suf - 0.03, suf - 0.005, 'wn_lampa', gora=False)
            self._ring(G, br, Pp, kdb[1:], osc, gd, rng)
            # strop nad parterem
            G.pryzma(Pp.buffer(-0.73, join_style=2), suf, kdb[1]['F'], 'wn_sufit', mat_gora='wn_podloga')
        # brama ogrodowa – przejście: ściany, podsufitka z oprawami, posadzka (pochylona)
        self._brama_wnetrze(G)
        G.obiekt('wnetrza', self.kol['wnetrza'], self.mat, self.DZ)
        self.czas('wnetrza', t0)

    @staticmethod
    def _siatka_lamp(geom, krok, r=0.2):
        if geom.is_empty:
            return []
        x0, y0, x1, y1 = geom.bounds
        out = []
        for x in np.arange(x0 + krok / 2, x1, krok):
            for y in np.arange(y0 + krok / 2, y1, krok):
                c = Point(x, y).buffer(r, 8)
                if geom.contains(c):
                    out.append(c)
        return out

    def _ring(self, G, br, Pp, kd, g, gd, rng):
        """Biura przy elewacji: stropy (sufit/posadzka), tylna ściana (jądro), ścianki co 4,05 m, lampy liniowe
        równoległe do elewacji, biurka z monitorami i krzesłami."""
        sp, Z = self.spec, self.Z
        biegi = getattr(self, 'biegi_' + br)
        zew = Pp.buffer(-g - 0.03, join_style=2)
        jadro = Pp.buffer(-g - gd, join_style=2)
        for i, k in enumerate(kd):
            if k['nazwa'] == 'S':
                break
            F, suf = k['F'], k['sufit']
            ostatnia = i + 1 >= len(kd)
            # strop nad kondygnacją (sufit + posadzka wyżej); nad ostatnią – poniżej pokrycia dachu (bez nakładania)
            nast = k['Fn'] - 0.08 if ostatnia else kd[i + 1]['F']
            korona_wyzej = (not ostatnia) and kd[i + 1]['nazwa'] == 'S'
            G.pryzma(zew, suf, nast, 'wn_sufit', mat_gora='wn_kamien' if korona_wyzej else 'wn_podloga')
            if not jadro.is_empty:
                G.pryzma(jadro, F, suf, 'wn_sciana', gora=False, dno=False)
            for b in biegi:
                if b.L < 2.0:
                    continue
                vis = self.przytnij(b, 0.0, b.L, F + 1.0, suf)
                if not vis:
                    continue
                for s_a, s_b, _, _ in vis:
                    if s_b - s_a < 1.5:
                        continue
                    # lampy liniowe (2 rzędy), co ok. 1,6 m
                    for tl in (-g - 1.7, -g - 4.0):
                        for sl in np.arange(s_a + 0.9, s_b - 0.6, 1.7):
                            G.box(b, sl - 0.6, sl + 0.6, tl - 0.05, tl + 0.05, suf - 0.06, suf - 0.02, 'wn_lampa',
                                  maks=0.5 if b.krzywy else None)
                    # ścianki działowe co 4,05 m
                    for sw in np.arange(s_a + 4.05, s_b - 0.5, 4.05):
                        G.box(b, sw - 0.06, sw + 0.06, -g - gd, -g - 0.05, F, suf, 'wn_sciana')
                    # biurka (po 2 na pokój), monitory, krzesła
                    for sr in np.arange(s_a + 2.0, s_b - 1.0, 4.05):
                        if rng.random() < 0.12:
                            continue
                        for ds in (-0.95, 0.95):
                            s0 = sr + ds - 0.75
                            t_b = -g - rng.uniform(1.1, 1.6)
                            G.box(b, s0, s0 + 1.5, t_b - 0.4, t_b + 0.4, F + 0.70, F + 0.74, 'wn_biurko',
                                  maks=0.5 if b.krzywy else None)
                            for sl in (s0 + 0.05, s0 + 1.40):
                                G.box(b, sl, sl + 0.05, t_b - 0.35, t_b + 0.35, F, F + 0.70, 'wn_ciemne')
                            if rng.random() < 0.8:
                                G.box(b, s0 + 0.45, s0 + 1.05, t_b - 0.32, t_b - 0.29, F + 0.80, F + 1.15, 'wn_ciemne')
                            if rng.random() < 0.7:
                                G.box(b, s0 + 0.5, s0 + 1.0, t_b - 0.95, t_b - 0.5, F + 0.45, F + 0.52, 'wn_ciemne')
                                G.box(b, s0 + 0.5, s0 + 1.0, t_b - 1.0, t_b - 0.95, F + 0.52, F + 1.0, 'wn_ciemne')

    def _korona(self, G, Wp, kd, g):
        """Korona Sejmiku: sala obrad (ciepłe wnętrze widoczne zza lamel), hol pn., ściany z drewna, sufit
        z bafli, rzędy łukowe, galeria publiczności, kuluar."""
        sp, Z = self.spec, self.Z
        kS = next(k for k in kd if k['nazwa'] == 'S')
        F, suf = kS['F'], kS['sufit']
        zew = Wp.buffer(-0.68, join_style=2)
        # strop dachu (od sufitu sali do pokrycia)
        G.pryzma(zew, suf, sp.dach['W']['pokrycie'] - 0.03, 'wn_drewno:jasne', mat_gora='beton')
        # trzony
        for k in ('A', 'B'):
            rp = Polygon(sp.K['rdzenie'][k]['obrys_en']).buffer(0)
            G.pryzma(rp, F, suf, 'wn_drewno', gora=False, dno=False)
        uv = sp.z_uv
        # ściana pd. sali (pełna, prezydium) i zach. (drewno perforowane)
        sala_v0, sala_u0 = 12.45, 20.0
        wall_s = Polygon([uv(sala_u0, sala_v0 - 0.25), uv(39.6, sala_v0 - 0.25), uv(39.6, sala_v0), uv(sala_u0, sala_v0)])
        wall_w = Polygon([uv(sala_u0 - 0.25, sala_v0), uv(sala_u0, sala_v0), uv(sala_u0, 29.3), uv(sala_u0 - 0.25, 29.3)])
        for wp in (wall_s, wall_w):
            G.pryzma(wp.intersection(zew), F, suf, 'wn_drewno')
        # godło nad prezydium (brąz) – na balustradzie galerii; tu płaskorzeźba na ścianie
        e, n = uv(30.0, sala_v0 + 0.02)
        # rzędy łukowe wokół ogniska (u 30,0; v 13,4)
        ogn = sp.K['kondygnacja_sejmiku']['sala']['ognisko_rzedow_uv']
        cx, cy = uv(*ogn)
        sala = Polygon([uv(sala_u0, sala_v0), uv(40, sala_v0), uv(40, 29.7), uv(sala_u0, 29.7)]).intersection(zew)
        for r in sp.K['kondygnacja_sejmiku']['sala']['rzedy']:
            R, h = r['R'], r['rzedna']
            pod = Point(cx, cy).buffer(R + 1.0, 64).difference(Point(cx, cy).buffer(R - 0.6, 64)).intersection(sala)
            if pod.is_empty:
                continue
            G.pryzma(pod, F, F + h, 'wn_tkanina')
            st = Point(cx, cy).buffer(R + 0.15, 64).difference(Point(cx, cy).buffer(R - 0.45, 64)).intersection(sala)
            G.pryzma(st.buffer(0), F + h, F + h + 0.76, 'wn_drewno')
        # galeria (antresola) z balustradą
        za = sp.antresola
        gal = Polygon([uv(21.0, 11.45), uv(37.0, 11.45), uv(37.0, 13.45), uv(21.0, 13.45)])
        G.pryzma(gal, za - 0.30, za, 'wn_drewno:jasne')
        G.pryzma(Polygon([uv(21.0, 13.40), uv(37.0, 13.40), uv(37.0, 13.45), uv(21.0, 13.45)]), za, za + 1.1,
                 'wn_ciemne')
        # sufit z bafli drewnianych (pasy co 0,3 m wzdłuż v) + oprawy ciepłe
        for u in np.arange(sala_u0 + 0.2, 39.6, 0.30):
            pas = Polygon([uv(u, sala_v0), uv(u + 0.06, sala_v0), uv(u + 0.06, 29.5), uv(u, 29.5)]).intersection(zew)
            if not pas.is_empty:
                G.pryzma(pas, suf - 0.45, suf, 'wn_drewno:jasne', gora=False)
        for u in np.arange(sala_u0 + 1.5, 39.0, 3.0):
            for v in np.arange(sala_v0 + 1.5, 29.0, 3.0):
                c = Point(*uv(u, v)).buffer(0.30, 12)
                if zew.contains(c):
                    G.pryzma(c, suf - 1.2, suf - 1.15, 'wn_lampa:cieple', gora=False)
        # hol i kuluar – ciepłe oprawy, posadzka kamienna (już), ściany drewna na trzonach
        hol = zew.difference(sala.buffer(0.3))
        for c in self._siatka_lamp(hol, 2.8, 0.25):
            G.pryzma(c, suf - 0.04, suf - 0.01, 'wn_lampa:cieple', gora=False)
        # pokoje komisji (pd./zach.) – stoły
        for (u0, u1, v0, v1) in ((0.5, 10.65, 0.5, 9.9), (12.9, 18.8, 0.5, 9.9), (18.95, 24.7, 0.5, 9.9),
                                 (31.25, 39.5, 0.5, 7.1)):
            uc, vc = (u0 + u1) / 2, (v0 + v1) / 2
            st = Polygon([uv(uc - (u1 - u0) * 0.3, vc - 0.7), uv(uc + (u1 - u0) * 0.3, vc - 0.7),
                          uv(uc + (u1 - u0) * 0.3, vc + 0.7), uv(uc - (u1 - u0) * 0.3, vc + 0.7)])
            G.pryzma(st, F + 0.70, F + 0.75, 'wn_drewno')

    def _brama_wnetrze(self, G):
        sp = self.spec
        Bp = sp.brama
        z0, zt = -0.60, -0.60 + sp.brama_h
        zt = min(zt, sp.kondygnacje('M')[0]['sufit'])
        G.pryzma(Bp.buffer(0.02, join_style=2), -1.0, z0, 'bruk', boki=False, dno=False)
        ring = Bp.buffer(0.35, join_style=2).difference(Bp)
        ring = ring.intersection(self.poly['M'].buffer(-0.3, join_style=2))
        G.pryzma(ring, z0, zt, 'granit', mat_gora='wn_sufit')
        G.pryzma(Bp.buffer(0.3, join_style=2).intersection(self.poly['M'].buffer(-0.05)), zt, zt + 0.25, 'wn_sufit')
        c = Bp.centroid
        for d in np.linspace(-6, 6, 5):
            L = LineString([(c.x, c.y), (c.x + 1, c.y)])
        # oprawy w osi przejścia
        cc = list(Bp.minimum_rotated_rectangle.exterior.coords)
        e01 = np.subtract(cc[1], cc[0])
        e12 = np.subtract(cc[2], cc[1])
        dl = e01 if np.hypot(*e01) > np.hypot(*e12) else e12
        dl = dl / np.hypot(*dl)
        for t in np.arange(-6.0, 6.5, 2.0):
            p = np.array([c.x, c.y]) + dl * t
            G.pryzma(Point(*p).buffer(0.2, 10), zt - 0.03, zt - 0.005, 'wn_lampa:cieple', gora=False)

    # ================================================================ dachy
    def dachy(self):
        t0 = time.time()
        sp, Z = self.spec, self.Z
        G = Geo()
        for br, wew in (('W', sp.osc['wieza_m'] + 0.02), ('M', 0.68), ('S', 0.68)):
            Pp = self.poly[br]
            zr = sp.dach[br]['pokrycie']
            inner = Pp.buffer(-wew, join_style=2)
            if br != 'W':
                inner = inner.difference(self.poly['W'].buffer(0.3))
            G.pryzma(inner, zr - 0.6, zr, 'beton', boki=False, dno=False)
            if br == 'S':
                # taras nad Oławą: deski, donice z zielenią, balustrada szklana cofnięta 1,5 m
                taras = inner.buffer(-1.5, join_style=2)
                G.pryzma(inner.difference(taras.buffer(0.1)), zr, zr + 0.35, 'beton', mat_gora='sedum')
                G.pryzma(taras.buffer(0.1), zr, zr + 0.06, 'deska')
                ring = taras.buffer(0.12, join_style=2).difference(taras.buffer(0.08, join_style=2))
                ring = ring.difference(self.poly['W'].buffer(0.6))
                G.pryzma(ring, zr + 0.06, zr + 1.16, 'szklo:balustrada')
                G.pryzma(ring.buffer(0.02), zr + 1.16, zr + 1.20, 'metal')
                continue
            # pas zieleni ekstensywnej przy attyce + pole BIPV
            pas = 1.2
            zielen = inner.difference(inner.buffer(-pas, join_style=2))
            G.pryzma(zielen, zr, zr + 0.10, 'beton', mat_gora='sedum', dno=False)
            pole = inner.buffer(-pas - 0.4, join_style=2)
            G.pryzma(inner.buffer(-pas, join_style=2).difference(pole), zr, zr + 0.04, 'zwir', dno=False)
            if pole.is_empty:
                continue
            # moduły 1,0 × 1,7 m w osiach bryły (wieża: u, v; skrzydło: s, d)
            uk = sp.uv if br == 'W' else sp.sd
            x0, y0, x1, y1 = pole.bounds
            cnr = [sp.do_uv(x, y, uk) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
            us = [c[0] for c in cnr]
            vs = [c[1] for c in cnr]
            mod_a, mod_b, gap = 1.70, 1.00, 0.025
            for u in np.arange(min(us), max(us), mod_a + gap):
                for v in np.arange(min(vs), max(vs), mod_b + gap):
                    q = Polygon([sp.z_uv(u, v, uk), sp.z_uv(u + mod_a, v, uk), sp.z_uv(u + mod_a, v + mod_b, uk),
                                 sp.z_uv(u, v + mod_b, uk)])
                    if pole.contains(q):
                        G.pryzma(q, zr + 0.06, zr + 0.10, 'metal', mat_gora='bipv', dno=False)
        G.obiekt('dachy', self.kol['dachy'], self.mat, self.DZ)
        self.czas('dachy', t0)


# ============================================================================================== światło
# Kalibracja słońce/niebo (wizualizacje_metodyka.md §5.2, pomiar w bpy 5.2): niebo Multiple Scattering o sile 1,0;
# lampa Sun równoważna tarczy słońca: wysokość → (W/m², barwa liniowa).
_KALIBRACJA_SLONCA = [(-1.0, 0.0, (1.0, 0.45, 0.15)), (3.0, 25.0, (1.0, 0.52, 0.18)), (10.0, 72.0, (1.0, 0.67, 0.30)),
                      (25.0, 117.0, (1.0, 0.80, 0.55)), (45.0, 133.0, (1.0, 0.85, 0.65)), (90.0, 140.0, (1.0, 0.88, 0.72))]


def _interp_slonce(el):
    T = _KALIBRACJA_SLONCA
    if el <= T[0][0]:
        return 0.0, T[0][2]
    for (e0, w0, c0), (e1, w1, c1) in zip(T[:-1], T[1:]):
        if el <= e1:
            f = (el - e0) / (e1 - e0)
            return w0 + (w1 - w0) * f, tuple(a + (b - a) * f for a, b in zip(c0, c1))
    return T[-1][1], T[-1][2]


# Panoramy 360° M.09 (29.10.2025, 11:48–11:52 CET) – środowisko odbić. u_slonca: kolumna tarczy słońca (pomiar),
# azymut słońca wg NOAA dla 11:50 CET = 183,9° (+0,738° w siatce) → obrót panoramy wokół osi Z.
_M09 = UMWD / '00_materialy' / '_rozpak' / '5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026' / \
    'M.09. ZDJĘCIA 360 ST' / 'M.09. ZDJĘCIA 360 ST'
PANORAMY_M09 = {'m09_30': (_M09 / '360_30m.jpg', 0.6090), 'm09_40': (_M09 / '360_40m_2.jpg', 0.6117),
                'm09_45': (_M09 / '360_45m.jpg', 0.6003)}
AZ_SLONCA_M09 = 183.90 + 0.738


def _obrot_panoramy(u_slonca, az_slonca=AZ_SLONCA_M09):
    """Kąt obrotu wektora (węzeł Mapping, oś Z) tak, by kolumna słońca panoramy wypadła na azymut słońca.
    Blender (equirect): u = atan2(d.y, −d.x)/2π + 0,5; obrót CCW o θ zmniejsza azymut kompasowy o θ."""
    a = (u_slonca - 0.5) * 2 * math.pi
    az_p = math.degrees(math.atan2(-math.cos(a), math.sin(a))) % 360      # azymut kierunku o danym u
    return math.radians(az_slonca - az_p)


def dodaj_odbicia_panoramy(sc, klucz='m09_30', sila=12.0):
    """Panorama M.09 jako środowisko widoczne TYLKO w promieniach odbitych (Light Path → Is Glossy Ray):
    szkło, metal, woda odbijają prawdziwe miasto; oświetlenie i tło kadru zostają z nieba fizycznego.
    Zwraca węzeł obrazu lub None (brak pliku)."""
    if klucz in PANORAMY_M09:
        plik, u_s = PANORAMY_M09[klucz]
    else:
        plik, u_s = Path(klucz), 0.5
    if not Path(plik).exists():
        return None
    nt = sc.world.node_tree
    out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputWorld')
    src = out.inputs['Surface'].links[0].from_socket
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Rotation'].default_value = (0.0, 0.0, _obrot_panoramy(u_s))
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(str(plik), check_existing=True)
    env.image.colorspace_settings.name = 'sRGB'
    nt.links.new(mp.outputs['Vector'], env.inputs['Vector'])
    bg2 = nt.nodes.new('ShaderNodeBackground')
    bg2.inputs['Strength'].default_value = sila
    nt.links.new(env.outputs['Color'], bg2.inputs['Color'])
    lp = nt.nodes.new('ShaderNodeLightPath')
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Glossy Ray'], mx.inputs['Fac'])
    nt.links.new(src, mx.inputs[1])
    nt.links.new(bg2.outputs['Background'], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return env


def czas_kamery(txt):
    """'2026-10-23 09:40 CEST[, …]' → datetime ze strefą Europe/Warsaw."""
    import datetime
    from umwd.sun import TZ
    m = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}:\d{2})', txt)
    return datetime.datetime.strptime(m.group(1) + ' ' + m.group(2), '%Y-%m-%d %H:%M').replace(tzinfo=TZ)


def swiatlo_dzienne(sc, czas, ekspozycja=None, sila_slonca=1.0, sila_nieba=1.0, aerozole=1.6, chmury=0.35,
                    wb=None, odbicia=None, odbicia_sila=12.0):
    """Niebo fizyczne (Multiple Scattering, ``sun_rotation`` = azymut kompasowy w siatce) + lampa Sun wg kalibracji
    (bez tarczy na niebie – cienie kontrolowane lampą). Azymut siatki = azymut geograficzny + 0,738°.
    ``odbicia``: 'm09_30' | 'm09_40' | 'm09_45' | ścieżka panoramy – środowisko tylko dla promieni odbitych.
    Zwraca dict(az, el, ekspozycja). ``czas``: datetime lub tekst z koncepcja.json."""
    from mathutils import Vector
    from umwd.sun import sun_position
    dt = czas_kamery(czas) if isinstance(czas, str) else czas
    az, el = sun_position(dt)
    azs = az + 0.738
    for o in [o for o in sc.objects if o.type == 'LIGHT' and o.name.startswith('Slonce')]:
        bpy.data.objects.remove(o)
    w = bpy.data.worlds.new('Swiat')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get('Background') or nt.nodes.new('ShaderNodeBackground')
    out = nt.nodes.get('World Output') or nt.nodes.new('ShaderNodeOutputWorld')
    sky = nt.nodes.new('ShaderNodeTexSky')
    sky.sky_type = 'MULTIPLE_SCATTERING'
    sky.sun_disc = False
    sky.sun_elevation = math.radians(el)
    sky.sun_rotation = math.radians(azs)
    sky.altitude = 120.0
    sky.air_density = 1.0
    sky.aerosol_density = aerozole
    sky.ozone_density = 1.0
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = sila_nieba
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    E, col = _interp_slonce(el)
    if E > 0:
        ld = bpy.data.lights.new('Slonce', 'SUN')
        ld.energy = E * sila_slonca
        ld.color = col
        ld.angle = math.radians(0.53)
        so = bpy.data.objects.new('Slonce', ld)
        sc.collection.objects.link(so)
        a, e = math.radians(azs), math.radians(el)
        so.rotation_euler = Vector((math.sin(a) * math.cos(e), math.cos(a) * math.cos(e),
                                    math.sin(e))).to_track_quat('Z', 'Y').to_euler()
    if chmury:
        from umwd.render import context
        context.dodaj_chmury(sc, pokrycie=chmury)
    if odbicia:
        # odbicia z panoramy M.09 (tylko promienie odbite); o zmierzchu przyciemnione proporcjonalnie do nieba
        dodaj_odbicia_panoramy(sc, odbicia, odbicia_sila * (1.0 if el > 8 else max(0.04, (el + 6.0) / 14.0)))
    # o zmierzchu „reszta budynku milknie”: zapalona tylko część opraw biurowych (korona i hol – w pełni)
    m_l = bpy.data.materials.get('B_wn_lampa')
    if m_l is not None and m_l.node_tree and 'udzial' in m_l.node_tree.nodes:
        m_l.node_tree.nodes['udzial'].outputs[0].default_value = 1.0 if el > 3 else 0.35
    if ekspozycja is None:
        # dzień: ok. −4,3 EV (biała płaszczyzna ≈ 20); zmierzch: jaśniej
        ekspozycja = -4.3 if el > 12 else (-3.9 if el > 4 else (-3.0 if el > 0 else -1.2 + 0.25 * el))
    sc.view_settings.exposure = ekspozycja
    if wb is not None:
        sc.view_settings.use_white_balance = True
        sc.view_settings.white_balance_temperature = wb
    return dict(az=round(az, 2), el=round(el, 2), ekspozycja=round(ekspozycja, 2), czas=dt.isoformat())


DOMYSLNE = dict(
    koncepcja=str(KONCEPCJA),
    kontekst=None,                 # wynik context.build_context (teren, trawnik, prototypy drzew)
    wnetrza=True,
    dachy=True,
    zagospodarowanie=True,
    ludzie=True,
    rolety=0.25,                   # udział okien z opuszczoną roletą ZIP
    lampy=1.0,                     # mnożnik jasności opraw we wnętrzach
    albedo=0.84,                   # skala albedo ceramiki (barwa NCS → odbicie fizyczne)
    albedo_granit=0.70,
    albedo_bruk=0.52,
    seed=3,
)


def build_building(scene, opts=None):
    """Buduje model budynku w scenie. Zwraca {'kolekcje': {...}, 'info': {...}, 'budynek': Budynek}.

    opts (wszystkie opcjonalne, patrz ``DOMYSLNE``): kontekst – słownik z ``context.build_context`` (potrzebny do
    posadzek drapowanych na terenie, przebudowy trawnika i drzew); wnetrza, dachy, zagospodarowanie, ludzie: bool;
    rolety: udział rolet; lampy: mnożnik opraw; albedo*: skale albedo; zalozenia: nadpisanie ``ZALOZENIA``.
    """
    B = Budynek(scene, opts)
    B.wneki_polys = []
    B.wieza()
    B.kamieniczny('M')
    B.kamieniczny('S')
    if B.o['wnetrza']:
        B.wnetrza()
    if B.o['dachy']:
        B.dachy()
    if B.o['zagospodarowanie']:
        from umwd.render import budynek3d_otoczenie as oto
        oto.zagospodarowanie(B)
    for k, c in B.kol.items():
        B.info['obiekty'][k] = len(c.objects)
    scene['umwd_budynek_info'] = json.dumps(B.info, ensure_ascii=False)
    return {'kolekcje': dict(B.kol), 'info': B.info, 'budynek': B}
