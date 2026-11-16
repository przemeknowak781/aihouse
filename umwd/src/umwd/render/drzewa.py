# -*- coding: utf-8 -*-
"""Proceduralne drzewa do wizualizacji kontekstu (bpy 5.2 / Cycles).

Każdy typ drzewa to prototyp: siatka gałęzi (rurki z ubytkiem średnicy wzdłuż osi, rozgałęzienia rekurencyjne
ograniczone obwiednią korony) + siatka liści (małe czworokąty-„rombiki” rozsiane przy końcach gałązek).
Prototypy są instancjonowane (collection instance) w punktach drzew z ``site.json`` – geometria liczona raz.

Liście mają atrybut ścian ``lisc_rnd`` (0–1), a shader dodatkowo korzysta z ``Object Info > Random`` (losowość
na instancję) – dzięki temu korony różnią się barwą (jesień: od zielonożółtej przez żółtą do pomarańczowej i
rdzawej, jak na zdjęciach z drona z 29.10.2025; lato: odcienie zieleni).

Typy: ``lisc_duze`` (lipa/klon/kasztanowiec ~19 m), ``lisc_srednie`` (~13 m), ``lisc_male`` (młode drzewo
szpaleru ~7 m), ``topola`` (topola włoska – kolumnowa ~24 m, jak przy Wybrzeżu Słowackiego), ``iglaste``
(świerk ~14 m), ``krzew`` (zakrzewienie ~2,5 m).
"""
from __future__ import annotations

import math
import numpy as np

GOLD = math.radians(137.508)

TYPY = {
    # H – wysokość, cb – podstawa korony, R – promień korony, rt – promień pnia u podstawy,
    # n1 – liczba konarów, ksztalt – obwiednia, liscie – liczba liści, ls – rozmiar liścia (m)
    'lisc_duze': dict(H=19.0, cb=3.6, R=7.2, rt=0.36, n1=9, ksztalt='owal', liscie=19000, ls=0.21, n2=6, n3=4),
    'lisc_srednie': dict(H=13.0, cb=2.8, R=4.8, rt=0.22, n1=7, ksztalt='owal', liscie=12000, ls=0.18, n2=5, n3=4),
    'lisc_male': dict(H=7.0, cb=2.2, R=1.9, rt=0.09, n1=6, ksztalt='jajo', liscie=4200, ls=0.13, n2=4, n3=3),
    'topola': dict(H=24.0, cb=2.2, R=3.0, rt=0.38, n1=26, ksztalt='kolumna', liscie=17000, ls=0.16, n2=4, n3=3),
    'iglaste': dict(H=14.0, cb=0.8, R=3.1, rt=0.25, ksztalt='stozek', liscie=9000, ls=0.30),
    'krzew': dict(H=2.4, cb=0.0, R=1.5, rt=0.03, n1=8, ksztalt='polkula', liscie=3800, ls=0.12, n2=4, n3=2),
}


def _norm(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.maximum(n, 1e-9)


def _rot(v, axis, ang):
    """Obrót wektora v wokół osi (Rodrigues)."""
    axis = axis / max(np.linalg.norm(axis), 1e-9)
    c, s = math.cos(ang), math.sin(ang)
    return v * c + np.cross(axis, v) * s + axis * np.dot(axis, v) * (1 - c)


def _perp(d):
    a = np.array([0.0, 0.0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    p = np.cross(d, a)
    return p / np.linalg.norm(p)


class _Obwiednia:
    """Obwiednia korony: promień poziomy dopuszczalny na wysokości z (oś pionowa przez 0,0)."""

    def __init__(self, ksztalt, H, cb, R):
        self.k, self.H, self.cb, self.R = ksztalt, H, cb, R

    def r(self, z):
        t = (z - self.cb) / max(self.H - self.cb, 1e-6)
        if t < 0 or t > 1:
            return 0.0
        if self.k == 'owal':
            return self.R * math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2)) * (0.75 + 0.25 * (1 - t))
        if self.k == 'kolumna':
            return self.R * (math.sin(math.pi * min(1.0, t * 1.05)) ** 0.55) * (1.0 - 0.35 * t)
        if self.k == 'jajo':
            return self.R * 1.25 * (t ** 0.55) * ((1 - t) ** 0.45) * 1.6
        if self.k == 'polkula':
            return self.R * math.sqrt(max(0.0, 1 - t * t))
        if self.k == 'stozek':
            return self.R * (1 - t) ** 0.95
        return self.R

    def inside(self, p):
        return math.hypot(p[0], p[1]) <= self.r(p[2])

    def dist(self, p, d, maxd):
        """Odległość wzdłuż kierunku d do wyjścia poza obwiednię (krok 0,25 m)."""
        s = 0.0
        while s < maxd:
            q = p + d * s
            if not self.inside(q) and s > 0.3:
                return s
            s += 0.25
        return maxd


def _tube(pts, radii, sides):
    """Rurka wzdłuż łamanej (transport równoległy ramek). Zwraca (V, F)."""
    pts = np.asarray(pts, float)
    k = len(pts)
    if k < 2:
        return np.zeros((0, 3)), []
    T = np.zeros_like(pts)
    T[1:-1] = pts[2:] - pts[:-2]
    T[0] = pts[1] - pts[0]
    T[-1] = pts[-1] - pts[-2]
    T = _norm(T)
    Nn = _perp(T[0])
    ang = np.linspace(0, 2 * math.pi, sides, endpoint=False)
    V = []
    for i in range(k):
        if i > 0:
            # transport ramki
            b = np.cross(T[i - 1], T[i])
            if np.linalg.norm(b) > 1e-6:
                th = math.acos(max(-1.0, min(1.0, float(np.dot(T[i - 1], T[i])))))
                Nn = _rot(Nn, b, th)
        B = np.cross(T[i], Nn)
        ring = pts[i] + radii[i] * (np.outer(np.cos(ang), Nn) + np.outer(np.sin(ang), B))
        V.append(ring)
    V = np.concatenate(V)
    F = []
    for i in range(k - 1):
        a0, b0 = i * sides, (i + 1) * sides
        for j in range(sides):
            j1 = (j + 1) % sides
            F.append((a0 + j, a0 + j1, b0 + j1, b0 + j))
    # zaślepka końca
    F.append(tuple(range((k - 1) * sides + sides - 1, (k - 1) * sides - 1, -1)))
    return V, F


class _Gen:
    def __init__(self, typ, seed, gestosc=1.0):
        self.p = dict(TYPY[typ])
        self.typ = typ
        self.rng = np.random.default_rng(seed)
        self.g = gestosc
        P = self.p
        self.env = _Obwiednia(P['ksztalt'], P['H'], P['cb'], P['R'])
        self.V, self.F = [], []
        self.nv = 0
        self.leaf_sites = []   # (punkt, kierunek gałązki, waga)

    def add_tube(self, pts, radii, sides):
        V, F = _tube(pts, radii, sides)
        if len(V) == 0:
            return
        self.V.append(V)
        self.F.extend([tuple(i + self.nv for i in f) for f in F])
        self.nv += len(V)

    # ------------------------------------------------------------------ drzewa liściaste
    def galaz(self, p0, d, L, r0, r1, lvl, tropizm):
        rng = self.rng
        nseg = max(3, int(L / (0.45 if lvl < 2 else 0.3)))
        step = L / nseg
        pts = [p0.copy()]
        dirs = [d.copy()]
        p = p0.copy()
        for i in range(nseg):
            jit = rng.normal(0, 0.12 if lvl else 0.05, 3)
            d = _norm(d + jit + np.array([0, 0, tropizm]))
            p = p + d * step
            pts.append(p.copy())
            dirs.append(d.copy())
        pts = np.array(pts)
        radii = np.linspace(r0, r1, len(pts))
        sides = (9, 6, 4, 3)[min(lvl, 3)]
        if r0 > 0.006:
            self.add_tube(pts, radii, sides)
        return pts, np.array(dirs), radii

    def lisciaste(self):
        P, rng, env = self.p, self.rng, self.env
        H, cb, R = P['H'], P['cb'], P['R']
        kol = P['ksztalt'] == 'kolumna'
        krzew = P['ksztalt'] == 'polkula'
        # pień (przewodnik)
        Ht = H * (0.93 if kol else (0.0 if krzew else 0.72))
        if not krzew:
            lean = rng.normal(0, 0.03, 2)
            d0 = _norm(np.array([lean[0], lean[1], 1.0]))
            trunk, tdirs, trad = self.galaz(np.zeros(3), d0, Ht, P['rt'], P['rt'] * (0.18 if kol else 0.35), 0, 0.02)
            # odziomek (szersza nasada)
            base = np.array([[0, 0, -0.2], [0, 0, 0.0], [0, 0, 0.35]])
            self.add_tube(base, np.array([P['rt'] * 1.45, P['rt'] * 1.3, P['rt'] * 1.05]), 9)
        n1 = P['n1']
        az0 = rng.uniform(0, 2 * math.pi)
        for i in range(n1):
            if krzew:
                st = np.array([rng.normal(0, 0.25), rng.normal(0, 0.25), 0.0])
                a = math.radians(rng.uniform(10, 45))
                r0 = rng.uniform(0.015, 0.03)
                zc = 0.0
            else:
                t = (i + rng.uniform(0.1, 0.9)) / n1
                zc = cb + t * (Ht - cb) * (0.98 if kol else 1.0)
                k = int(np.clip(zc / max(Ht, 1e-6) * (len(trunk) - 1), 0, len(trunk) - 1))
                st = trunk[k]
                if kol:
                    a = math.radians(rng.uniform(8, 22))
                else:
                    a = math.radians(np.interp(t, [0, 1], [68, 30]) + rng.normal(0, 7))
                r0 = trad[k] * rng.uniform(0.55, 0.75)
            az = az0 + i * GOLD + rng.normal(0, 0.25)
            d = np.array([math.sin(a) * math.cos(az), math.sin(a) * math.sin(az), math.cos(a)])
            L = env.dist(st, d, 2.2 * R + H) * (0.92 if not krzew else 1.0)
            if krzew:
                L = max(L, 0.8)
            if L < 0.6:
                continue
            pts1, dirs1, rad1 = self.galaz(st, d, L, r0, r0 * 0.25, 1, 0.05 if not kol else 0.15)
            self.odgalezienia(pts1, dirs1, rad1, 2, L)
        # dodatkowe pędy wierzchołkowe (domknięcie korony u góry)
        if not krzew and not kol:
            for j in range(3):
                d = _norm(np.array([rng.normal(0, 0.35), rng.normal(0, 0.35), 1.0]))
                st = trunk[-1]
                L = env.dist(st, d, H) * 0.9
                if L > 0.6:
                    pts1, dirs1, rad1 = self.galaz(st, d, L, trad[-1] * 0.8, trad[-1] * 0.2, 1, 0.05)
                    self.odgalezienia(pts1, dirs1, rad1, 2, L)

    def odgalezienia(self, pts, dirs, rad, lvl, Lp):
        P, rng, env = self.p, self.rng, self.env
        n = P['n2'] if lvl == 2 else P['n3']
        if lvl > 3:
            return
        k = len(pts)
        for i in range(n):
            t = rng.uniform(0.25, 0.97)
            idx = int(t * (k - 1))
            st = pts[idx]
            d = dirs[idx]
            ax = _rot(_perp(d), d, rng.uniform(0, 2 * math.pi))
            a = math.radians(rng.uniform(30, 55))
            dn = _norm(_rot(d, ax, a) + np.array([0, 0, 0.12]))
            Lc = Lp * (0.55 if lvl == 2 else 0.5) * (1.1 - 0.6 * t) + rng.uniform(0.2, 0.5)
            Lc = min(Lc, env.dist(st, dn, Lc + 0.5) + 0.35)
            if Lc < 0.25:
                continue
            r0 = rad[idx] * 0.6
            pts2, dirs2, rad2 = self.galaz(st, dn, Lc, r0, r0 * 0.3, lvl, -0.02 if lvl == 3 else 0.02)
            if lvl < 3:
                self.odgalezienia(pts2, dirs2, rad2, lvl + 1, Lc)
                # liście także na zewnętrznej połowie gałęzi 2. rzędu
                for q in range(len(pts2) // 2, len(pts2)):
                    self.leaf_sites.append((pts2[q], dirs2[q], 0.6))
            else:
                for q in range(1, len(pts2)):
                    self.leaf_sites.append((pts2[q], dirs2[q], 1.0))

    # ------------------------------------------------------------------ iglaste (świerk)
    def iglaste(self):
        P, rng = self.p, self.rng
        H, cb, R = P['H'], P['cb'], P['R']
        trunk = np.array([[0, 0, z] for z in np.linspace(-0.2, H, 14)])
        trunk[:, :2] += np.cumsum(rng.normal(0, 0.015, (14, 2)), axis=0)
        self.add_tube(trunk, np.linspace(P['rt'] * 1.2, 0.02, 14), 8)
        z = cb
        az0 = rng.uniform(0, 6.28)
        w = 0
        while z < H - 0.25:
            t = (z - cb) / (H - cb)
            Lb = R * (1 - t) ** 0.95 + 0.25
            nb = 6 if t < 0.85 else 4
            for j in range(nb):
                az = az0 + w * 0.5 + j * 2 * math.pi / nb + rng.normal(0, 0.2)
                droop = math.radians(np.interp(t, [0, 1], [-25, 10]) + rng.normal(0, 6))
                d = np.array([math.cos(az) * math.cos(droop), math.sin(az) * math.cos(droop), math.sin(droop)])
                st = np.array([0, 0, z]) + 0.0
                pts, dirs, rad = self.galaz(st, d, Lb, max(0.012, P['rt'] * 0.25 * (1 - t)), 0.006, 2, 0.035)
                for q in range(1, len(pts)):
                    self.leaf_sites.append((pts[q], dirs[q], 1.0 + 0.6 * (1 - q / len(pts))))
            z += rng.uniform(0.38, 0.55)
            w += 1

    # ------------------------------------------------------------------ liście
    def liscie(self):
        P, rng = self.p, self.rng
        if not self.leaf_sites:
            return np.zeros((0, 3)), np.zeros((0, 4), int), np.zeros(0)
        S = np.array([s[0] for s in self.leaf_sites])
        D = np.array([s[1] for s in self.leaf_sites])
        Wt = np.array([s[2] for s in self.leaf_sites])
        nl = int(P['liscie'] * self.g)
        idx = rng.choice(len(S), size=nl, p=Wt / Wt.sum())
        igl = self.typ == 'iglaste'
        spread = 0.16 if igl else 0.30
        C = S[idx] + rng.normal(0, spread, (nl, 3))
        Dd = D[idx]
        size = P['ls'] * rng.uniform(0.7, 1.3, nl)
        if igl:
            # „łapki” igieł: wydłużone karty wzdłuż gałązki, lekko pochylone
            t = _norm(Dd + rng.normal(0, 0.35, (nl, 3)))
            up = np.array([0.0, 0.0, 1.0])
            b = _norm(np.cross(t, up) + rng.normal(0, 0.3, (nl, 3)))
            L1, L2 = 0.65, 0.18
        else:
            # normalna liścia: losowa z przewagą „na zewnątrz i w górę”
            out = C.copy()
            out[:, 2] = (C[:, 2] - (P['cb'] + P['H']) * 0.5) * 0.6
            nrm = _norm(_norm(out) * 0.6 + rng.normal(0, 0.8, (nl, 3)) + np.array([0, 0, 0.5]))
            a = _norm(np.cross(nrm, rng.normal(0, 1, (nl, 3))))
            t = a
            b = _norm(np.cross(nrm, t))
            L1, L2 = 0.62, 0.30
        s = size[:, None]
        v0 = C + t * s * L1
        v1 = C + b * s * L2
        v2 = C - t * s * (L1 * 0.65)
        v3 = C - b * s * L2
        V = np.stack([v0, v1, v2, v3], axis=1).reshape(-1, 3)
        F = np.arange(nl * 4).reshape(nl, 4)
        rnd = rng.random(nl)
        return V, F, rnd

    def wynik(self):
        if self.p['ksztalt'] == 'stozek':
            self.iglaste()
        else:
            self.lisciaste()
        LV, LF, LR = self.liscie()
        GV = np.concatenate(self.V) if self.V else np.zeros((0, 3))
        return dict(gal_V=GV, gal_F=self.F, lis_V=LV, lis_F=LF, lis_rnd=LR, H=self.p['H'], R=self.p['R'])


def generuj(typ, seed=1, gestosc=1.0):
    """Zwraca słownik z tablicami geometrii prototypu drzewa (gałęzie + liście)."""
    return _Gen(typ, seed, gestosc).wynik()


# ---------------------------------------------------------------------------------------------- materiały / bpy
def mat_kora(name='kora'):
    import bpy
    from umwd.render.blib import NodeBuilder
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nb = NodeBuilder(m)
    tc = nb.n('ShaderNodeTexCoord')
    nz = nb.n('ShaderNodeTexNoise', Scale=9.0, Detail=8.0, Roughness=0.65)
    nb.l(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nb.n('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.035, 0.030, 0.026, 1)
    ramp.color_ramp.elements[1].color = (0.13, 0.115, 0.10, 1)
    nb.l(nz.outputs['Fac'], ramp.inputs['Fac'])
    bsdf = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.9)
    nb.l(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bmp = nb.n('ShaderNodeBump', Strength=0.6, Distance=0.02)
    nb.l(nz.outputs['Fac'], bmp.inputs['Height'])
    nb.l(bmp.outputs['Normal'], bsdf.inputs['Normal'])
    nb.output(bsdf)
    return m


def mat_liscie(name, pora='jesien', iglaste=False):
    """Materiał liści: paleta wg pory roku; losowość na liść (atrybut lisc_rnd) i na drzewo (Object Info)."""
    import bpy
    from umwd.render.blib import NodeBuilder
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nb = NodeBuilder(m)
    att = nb.n('ShaderNodeAttribute', {'attribute_name': 'lisc_rnd', 'attribute_type': 'GEOMETRY'})
    oi = nb.n('ShaderNodeObjectInfo')
    if iglaste:
        pal = [(0.0, (0.012, 0.035, 0.012)), (0.5, (0.025, 0.06, 0.02)), (1.0, (0.05, 0.08, 0.03))]
        f = nb.math('ADD', nb.math('MULTIPLY', att.outputs['Fac'], 0.7), nb.math('MULTIPLY', oi.outputs['Random'], 0.3))
    else:
        if pora == 'lato':
            pal = [(0.0, (0.045, 0.10, 0.018)), (0.4, (0.07, 0.15, 0.025)), (0.75, (0.12, 0.20, 0.035)),
                   (1.0, (0.16, 0.22, 0.04))]
            f = nb.math('ADD', nb.math('MULTIPLY', att.outputs['Fac'], 0.55), nb.math('MULTIPLY', oi.outputs['Random'], 0.45))
        else:
            # jesień (29.10): zielonożółte → żółte → pomarańczowe → rdzawe; mało zielonych
            pal = [(0.0, (0.10, 0.16, 0.025)), (0.22, (0.30, 0.30, 0.03)), (0.45, (0.55, 0.38, 0.03)),
                   (0.68, (0.62, 0.22, 0.025)), (0.88, (0.36, 0.10, 0.02)), (1.0, (0.22, 0.08, 0.025))]
            # kolor drzewa: losowy na instancję, rozrzut liści wokół niego
            f = nb.math('ADD', nb.math('MULTIPLY', oi.outputs['Random'], 0.85),
                        nb.math('MULTIPLY', nb.math('SUBTRACT', att.outputs['Fac'], 0.5), 0.35))
            f = nb.math('MINIMUM', nb.math('MAXIMUM', f, 0.0), 1.0)
    ramp = nb.n('ShaderNodeValToRGB')
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = pal[0][0], (*pal[0][1], 1)
    els[1].position, els[1].color = pal[-1][0], (*pal[-1][1], 1)
    for pos, col in pal[1:-1]:
        e = els.new(pos)
        e.color = (*col, 1)
    nb.l(f, ramp.inputs['Fac'])
    bsdf = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.55)
    nb.l(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.35
    tr = nb.n('ShaderNodeBsdfTranslucent')
    nb.l(ramp.outputs['Color'], tr.inputs['Color'])
    mixs = nb.n('ShaderNodeMixShader', Fac=0.28)
    nb.l(bsdf.outputs[0], mixs.inputs[1])
    nb.l(tr.outputs[0], mixs.inputs[2])
    nb.output(mixs)
    return m


def utworz_prototyp(nazwa, typ, seed, mat_kora_, mat_lisc, gestosc=1.0):
    """Tworzy kolekcję-prototyp (niepodpiętą do sceny) z obiektami gałęzi i liści. Zwraca (kolekcja, dane)."""
    import bpy
    from umwd.render.blib import mesh_from_arrays
    d = generuj(typ, seed, gestosc)
    coll = bpy.data.collections.new('proto_' + nazwa)
    if len(d['gal_V']):
        mesh_from_arrays(nazwa + '_galezie', d['gal_V'], d['gal_F'], mats=[mat_kora_], coll=coll, smooth=True)
    if len(d['lis_V']):
        ob = mesh_from_arrays(nazwa + '_liscie', d['lis_V'], d['lis_F'], mats=[mat_lisc], coll=coll,
                              face_attrs={'lisc_rnd': d['lis_rnd']})
        ob.visible_shadow = True
    return coll, d
