# -*- coding: utf-8 -*-
"""Render finalny ujęcia „zlota-godzina-3” (Latarnia odbita w Odrze – z łodzi) – nakładka na wspólną nakładkę
finałową zestawu ``render/ujecia_finalne_korekty.py`` (→ ``ujecia_poprawki_kontekstu.py`` → ``ujecia_dodatkowe.py``),
bez edycji modułów wspólnych; uruchomienie i argumenty jak ``ujecia_finalne_korekty.py`` (w tym ``--wycinek``)::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_zlota_godzina_3.py \
        --id zlota-godzina-3 --szer 2000 --probki 64 \
        --out umwd/docs/60_wizualizacje/img/extra/E_zlota-godzina-3.jpg

Warunki wspólne zestawu (z ``ujecia_finalne_korekty.py``, przy budowie sceny od zera): lamele korony łuku wg v1.1
(0,35 × 0,60 m, rozstawy 1,35 / 0,675 m w ciągu Fibonacciego, 21 szt. jak na rysunku elewacji), sitodruk 30 % na szkle
korony, w dzień ciepłe oprawy (korona, hol, podcień) ściemnione ×0,12.

Poprawki tego ujęcia wg uwag jurorów (po zbudowaniu / wczytaniu sceny, idempotentnie):

1. **Barka-restauracja** – uproszczone „białe pudło” z ``context._barka`` (barka przy nabrzeżu, środek (131,5; 81,0),
   30 × 9 m, obrót −20°) zastąpione modelem z detalem wg zdjęcia F.17.A: ciemny stalowy kadłub z odbojnicą i pasem
   linii wodnej, pokład z drewna, przeszklony salon (szprosy, pas cokołu, gzyms), wnętrze ze stołami i ciepłymi
   lampami wiszącymi, markiza nad pokładem bocznym z girlandą żarówek, relingi, górny taras z kioskiem, parasolami
   i donicami z jesienną zielenią, koła ratunkowe, polery, cumy do nabrzeża, kładka. Druga barka (pd.) bez zmian.
2. **Zmarszczka wody** – dodatkowy szum normalnych (amplituda ~2 mm, skala ~0,5 m, grzbiety wydłużone w poprzek
   osi widzenia) na materiale ``K_woda``: odbicie lekko rwie się w pionowe smugi, bez „idealnego lustra”.
3. **Pionowa smuga na murze nabrzeża** (uwaga jurora: „słup” x ≈ 0,40 przecinający cokół wieży) – to cień 0,3-metrowego
   uskoku lica muru w danych brzegu (127,95; 63,03)–(128,9; 61,0); uskok wyrównany do linii sąsiednich odcinków
   (retusz w 3D – znika też jego odbicie w wodzie).
4. **Trzech pieszych na bulwarze** (skala) – na koronie nabrzeża na lewo od barki, za balustradą.
"""
from __future__ import annotations

import json
import math
import sys

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import ujecia_finalne_korekty as FK  # noqa: E402  (warunki wspólne zestawu; importuje ujecia_poprawki_kontekstu)
from umwd.render import blib  # noqa: E402

U = FK.U
KONCEPCJA = U.KONCEPCJA
Z_WODA = 115.5 - 119.25          # context.H_WODA − Z0 (zwierciadło Odry w układzie sceny)
DZ = 0.05


# ============================================================================================== narzędzia geometrii
class Geo:
    """Zbiór wierzchołków / ścian z materiałem (klucz) – jeden obiekt z wieloma slotami."""

    def __init__(self):
        self.V, self.F, self.M = [], [], []

    def add(self, vs, fs, m):
        b = len(self.V)
        self.V += [tuple(map(float, v)) for v in vs]
        self.F += [tuple(b + i for i in f) for f in fs]
        self.M += [m] * len(fs)

    def obiekt(self, nazwa, mats, coll):
        klucze = []
        for k in self.M:
            if k not in klucze:
                klucze.append(k)
        slot = {k: i for i, k in enumerate(klucze)}
        me = bpy.data.meshes.new(nazwa)
        me.from_pydata(self.V, [], self.F)
        me.update()
        for k in klucze:
            me.materials.append(mats[k])
        for p, k in zip(me.polygons, self.M):
            p.material_index = slot[k]
        ob = bpy.data.objects.new(nazwa, me)
        coll.objects.link(ob)
        return ob


class Rama:
    """Układ lokalny barki: u – wzdłuż (ku pn.-pn.-zach.), w – w poprzek (+w ku nurtowi, −w ku nabrzeżu),
    v – w górę od zwierciadła wody."""

    def __init__(self, c, rot_deg, z0):
        r = math.radians(rot_deg)
        self.t = np.array([math.sin(r), math.cos(r)])
        self.n = np.array([self.t[1], -self.t[0]])
        self.c = np.array(c, float)
        self.z0 = z0

    def P(self, u, w, v):
        xy = self.c + self.t * u + self.n * w
        return (xy[0], xy[1], self.z0 + v)

    def lok(self, x, y):
        d = np.array([x, y]) - self.c
        return float(d @ self.t), float(d @ self.n)


_BOX_F = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]


def box(g, R, u0, u1, w0, w1, v0, v1, m):
    vs = [R.P(u, w, v) for v in (v0, v1) for w in (w0, w1) for u in (u0, u1)]
    g.add(vs, _BOX_F, m)


def pret(g, a, b, r, m, n=4):
    """Pręt / lina o przekroju n-kąta (promień r) między punktami a, b (współrzędne sceny)."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-6:
        return
    d /= L
    up = np.array([0, 0, 1.0]) if abs(d[2]) < 0.9 else np.array([1.0, 0, 0])
    e1 = np.cross(d, up)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(d, e1)
    ring = [r * (math.cos(2 * math.pi * k / n) * e1 + math.sin(2 * math.pi * k / n) * e2) for k in range(n)]
    vs = [a + q for q in ring] + [b + q for q in ring]
    fs = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    fs += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    g.add(vs, fs, m)


def kula(g, c, r, m, nu=8, nv=5, sz=1.0):
    vs = [(c[0], c[1], c[2] - r * sz)]
    for j in range(1, nv):
        th = math.pi * j / nv
        for i in range(nu):
            ph = 2 * math.pi * i / nu
            vs.append((c[0] + r * math.sin(th) * math.cos(ph), c[1] + r * math.sin(th) * math.sin(ph),
                       c[2] - r * sz * math.cos(th)))
    vs.append((c[0], c[1], c[2] + r * sz))
    fs = [(0, 1 + (i + 1) % nu, 1 + i) for i in range(nu)]
    for j in range(nv - 2):
        b0, b1 = 1 + j * nu, 1 + (j + 1) * nu
        fs += [(b0 + i, b0 + (i + 1) % nu, b1 + (i + 1) % nu, b1 + i) for i in range(nu)]
    top = len(vs) - 1
    bl = 1 + (nv - 2) * nu
    fs += [(bl + i, bl + (i + 1) % nu, top) for i in range(nu)]
    g.add(vs, fs, m)


def walec(g, c, r, z0, z1, m, n=8):
    vs = [(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n), z)
          for z in (z0, z1) for k in range(n)]
    fs = [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    fs += [tuple(range(n))[::-1], tuple(range(n, 2 * n))]
    g.add(vs, fs, m)


def parasol(g, c, z_dol, z_gora, R, m_tk, m_maszt, otwarty=True, n=16):
    """Parasol kawiarniany: maszt + czasza (stożek z lambrekinem) albo złożony (smukły stożek)."""
    pret(g, (c[0], c[1], z_dol), (c[0], c[1], z_gora + 0.10), 0.025, m_maszt, n=6)
    if otwarty:
        zr = z_gora - 0.45
        vs = [(c[0], c[1], z_gora)]
        vs += [(c[0] + R * math.cos(2 * math.pi * k / n), c[1] + R * math.sin(2 * math.pi * k / n),
                zr - (0.04 if k % 2 else 0.0)) for k in range(n)]
        vs += [(c[0] + R * math.cos(2 * math.pi * k / n), c[1] + R * math.sin(2 * math.pi * k / n), zr - 0.16)
               for k in range(n)]
        fs = [(0, 1 + k, 1 + (k + 1) % n) for k in range(n)]
        fs += [(1 + k, 1 + n + k, 1 + n + (k + 1) % n, 1 + (k + 1) % n) for k in range(n)]
        g.add(vs, fs, m_tk)
    else:
        vs = [(c[0], c[1], z_gora)]
        vs += [(c[0] + 0.16 * math.cos(2 * math.pi * k / 8), c[1] + 0.16 * math.sin(2 * math.pi * k / 8),
                z_gora - 1.5) for k in range(8)]
        vs += [(c[0], c[1], z_gora - 1.7)]
        fs = [(0, 1 + k, 1 + (k + 1) % 8) for k in range(8)] + [(9, 1 + (k + 1) % 8, 1 + k) for k in range(8)]
        g.add(vs, fs, m_tk)


def lancuchowa(a, b, zwis, n=12):
    """Punkty liny/girlandy między a i b ze zwisem (parabola)."""
    a, b = np.array(a, float), np.array(b, float)
    out = []
    for i in range(n + 1):
        t = i / n
        p = a + (b - a) * t
        p[2] -= 4 * zwis * t * (1 - t)
        out.append(p)
    return out


# ============================================================================================== materiały
def _mat(nazwa):
    m = bpy.data.materials.get(nazwa)
    if m is None:
        m = bpy.data.materials.new(nazwa)
    return m


def _principled(nazwa, kolor, rough=0.5, metal=0.0, coat=0.0, szum=None, emisja=None, sila=0.0):
    m = _mat(nazwa)
    nb = blib.NodeBuilder(m)
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
    if szum:
        # zmienność tonu (plamy, zabrudzenia) – szum w przestrzeni obiektu
        tc = nb.n('ShaderNodeTexCoord')
        nz = nb.n('ShaderNodeTexNoise', Scale=szum[0], Detail=4.0)
        nb.l(tc.outputs['Object'], nz.inputs['Vector'])
        c0 = tuple(x * (1 - szum[1]) for x in kolor)
        c1 = tuple(min(1.0, x * (1 + szum[1])) for x in kolor)
        nb.set(b, 'Base Color', nb.mix(nz.outputs['Fac'], c0, c1))
    else:
        nb.set(b, 'Base Color', kolor)
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.08
    if emisja is not None:
        nb.set(b, 'Emission Color', emisja)
        b.inputs['Emission Strength'].default_value = sila
    nb.output(b)
    return m


def materialy_barki():
    M = {}
    # kadłub: ciemna stal malowana (grafit z nutą granatu), linia wodna zabrudzona (glony), zacieki
    m = _mat('ZG3_kadlub')
    nb = blib.NodeBuilder(m)
    geo = nb.n('ShaderNodeNewGeometry')
    sz = nb.n('ShaderNodeSeparateXYZ')
    nb.l(geo.outputs['Position'], sz.inputs[0])
    tc = nb.n('ShaderNodeTexCoord')
    mp = nb.n('ShaderNodeMapping', Scale=(1.0, 1.0, 9.0))
    nb.l(tc.outputs['Object'], mp.inputs['Vector'])
    nz = nb.n('ShaderNodeTexNoise', Scale=1.2, Detail=6.0)
    nb.l(mp.outputs[0], nz.inputs['Vector'])
    baza = nb.mix(nz.outputs['Fac'], (0.018, 0.020, 0.024), (0.034, 0.036, 0.040))
    wl = nb.math('MINIMUM', nb.math('MAXIMUM', nb.math('DIVIDE', nb.math('SUBTRACT', Z_WODA + 0.35, sz.outputs[2]), 0.3),
                                     0.0), 1.0)
    kol = nb.mix(wl, baza, (0.020, 0.024, 0.014))
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.42)
    nb.set(b, 'Base Color', kol)
    b.inputs['Coat Weight'].default_value = 0.25
    b.inputs['Coat Roughness'].default_value = 0.15
    nb.output(b)
    M['kadlub'] = m
    M['odbojnica'] = _principled('ZG3_odbojnica', (0.012, 0.012, 0.012), 0.6)
    M['pasek'] = _principled('ZG3_pasek', (0.50, 0.47, 0.40), 0.4, coat=0.3)
    M['poklad'] = _principled('ZG3_poklad', (0.20, 0.115, 0.06), 0.55, szum=(3.0, 0.25))
    M['rama'] = _principled('ZG3_rama', (0.028, 0.028, 0.030), 0.35, metal=0.7)
    M['inox'] = _principled('ZG3_inox', (0.62, 0.62, 0.60), 0.25, metal=1.0)
    M['biel'] = _principled('ZG3_biel', (0.70, 0.70, 0.67), 0.45, szum=(2.0, 0.06))
    M['drewno_wn'] = _principled('ZG3_drewno_wn', (0.26, 0.14, 0.075), 0.6)
    M['sufit_wn'] = _principled('ZG3_sufit_wn', (0.45, 0.33, 0.22), 0.7)
    M['ciemne_wn'] = _principled('ZG3_ciemne_wn', (0.035, 0.03, 0.028), 0.7)
    M['tkanina_wn'] = _principled('ZG3_tkanina_wn', (0.30, 0.20, 0.13), 0.9)
    M['markiza'] = _principled('ZG3_markiza', (0.020, 0.052, 0.038), 0.85, szum=(0.8, 0.12))
    M['lina'] = _principled('ZG3_lina', (0.42, 0.37, 0.28), 0.9)
    M['corten'] = _principled('ZG3_corten', (0.12, 0.05, 0.025), 0.75, szum=(4.0, 0.2))
    M['pomarancz'] = _principled('ZG3_kolo_ratunkowe', (0.75, 0.16, 0.03), 0.5)
    M['lampa'] = _principled('ZG3_lampa', (0.9, 0.8, 0.6), 0.4, emisja=(1.0, 0.70, 0.42), sila=22.0)
    M['zarowka'] = _principled('ZG3_zarowka', (0.9, 0.8, 0.6), 0.3, emisja=(1.0, 0.66, 0.36), sila=40.0)
    # tkanina parasoli – kremowa, lekko przeświecająca
    m = _mat('ZG3_parasol')
    nb = blib.NodeBuilder(m)
    d = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.85)
    nb.set(d, 'Base Color', (0.72, 0.67, 0.56))
    tr = nb.n('ShaderNodeBsdfTranslucent')
    nb.set(tr, 'Color', (0.60, 0.50, 0.34))
    ms = nb.n('ShaderNodeMixShader')
    ms.inputs[0].default_value = 0.25
    nb.l(d.outputs[0], ms.inputs[1])
    nb.l(tr.outputs[0], ms.inputs[2])
    nb.output(ms)
    M['parasol'] = m
    # liście krzewów w donicach – jesień (oranż, czerwień, żółć, resztki zieleni), barwa per punkt (szum)
    m = _mat('ZG3_lisc')
    nb = blib.NodeBuilder(m)
    tc = nb.n('ShaderNodeTexCoord')
    nz = nb.n('ShaderNodeTexNoise', Scale=2.2, Detail=3.0)
    nb.l(tc.outputs['Object'], nz.inputs['Vector'])
    rp = nb.n('ShaderNodeValToRGB')
    els = rp.color_ramp.elements
    # jesienna mieszanka (stonowana – w niskim słońcu i tak ciepła): bordo, rdza, ochra, oliwka, ciemna zieleń
    els[0].position, els[0].color = 0.30, (0.10, 0.028, 0.016, 1)
    els[1].position, els[1].color = 0.72, (0.030, 0.050, 0.022, 1)
    for pp, cc in ((0.40, (0.15, 0.055, 0.02)), (0.48, (0.13, 0.085, 0.028)), (0.56, (0.055, 0.07, 0.028))):
        e = els.new(pp)
        e.color = (*cc, 1)
    nb.l(nz.outputs['Fac'], rp.inputs['Fac'])
    nf = nb.n('ShaderNodeTexNoise', Scale=26.0, Detail=3.0)
    nb.l(tc.outputs['Object'], nf.inputs['Vector'])
    kol = nb.mix(nb.math('MULTIPLY', nf.outputs['Fac'], 0.7), rp.outputs['Color'], (0.04, 0.025, 0.01), blend='MULTIPLY')
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.85)
    nb.set(b, 'Base Color', kol)
    bm = nb.n('ShaderNodeBump', Strength=1.0, Distance=0.04)
    nb.l(nf.outputs['Fac'], bm.inputs['Height'])
    nb.l(bm.outputs['Normal'], b.inputs['Normal'])
    nb.output(b)
    M['lisc'] = m
    # szkło salonu: pojedyncza tafla – Transparent (przepuszcza też promienie cienia) + Glossy wg Fresnela
    m = _mat('ZG3_szklo')
    nb = blib.NodeBuilder(m)
    fr = nb.n('ShaderNodeLayerWeight', Blend=0.12)
    tp = nb.n('ShaderNodeBsdfTransparent')
    nb.set(tp, 'Color', (0.50, 0.54, 0.52))
    gl = nb.n('ShaderNodeBsdfGlossy', Roughness=0.02)
    nb.set(gl, 'Color', (1.0, 1.0, 1.0))
    mx = nb.n('ShaderNodeMixShader')
    nb.l(nb.math('ADD', nb.math('MULTIPLY', fr.outputs['Fresnel'], 0.9), 0.08), mx.inputs[0])
    nb.l(tp.outputs[0], mx.inputs[1])
    nb.l(gl.outputs[0], mx.inputs[2])
    nb.output(mx)
    M['szklo'] = m
    return M


# ============================================================================================== barka
def _linia_nabrzeza(R):
    """Lico muru nabrzeża w układzie barki: (u, w) wierzchołków korony muru (obiekt 'nabrzeze', materiał muru)."""
    ob = bpy.data.objects.get('nabrzeze')
    if ob is None:
        return None
    me = ob.data
    mi = [i for i, m in enumerate(me.materials) if m and 'mur' in m.name]
    M = ob.matrix_world
    pts = set()
    for p in me.polygons:
        if p.material_index in mi:
            for vi in p.vertices:
                v = M @ me.vertices[vi].co
                if v.z > -2.0:
                    pts.add((round(v.x, 3), round(v.y, 3), round(v.z, 3)))
    uw = [(R.lok(x, y), z) for (x, y, z) in pts]
    uw = [((u, w), z) for ((u, w), z) in uw if -30 < u < 30 and -20 < w < 0]
    uw.sort()
    return uw


def _w_nabrzeza(linia, u):
    """w lica muru (i rzędna korony) dla danego u – najbliższe punkty linii."""
    if not linia:
        return -9.7, 0.2
    best = sorted(linia, key=lambda t: abs(t[0][0] - u))[:2]
    w = float(np.mean([b[0][1] for b in best]))
    z = float(np.mean([b[1] for b in best]))
    return w, z


def barka_restauracja(c=(131.5, 81.0), rot=-20.0, L=30.0, B=9.0):
    """Barka-restauracja z detalem w miejscu uproszczonej barki z context._barka (zdjęcie F.17.A: ciemny kadłub,
    przeszklony salon, górny taras z parasolami, donicami i kioskiem, kładka z nabrzeża)."""
    if bpy.data.objects.get('ZG3_barka') is not None:
        return 0
    # 1) usunięcie uproszczonej barki (ściany obiektu 'barki' w obrysie tej barki)
    ob = bpy.data.objects.get('barki')
    R = Rama(c, rot, Z_WODA)
    usun = 0
    if ob is not None:
        Mw = ob.matrix_world
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        fs = []
        for f in bm.faces:
            p = Mw @ f.calc_center_median()
            u, w = R.lok(p.x, p.y)
            if abs(u) < L / 2 + 0.5 and abs(w) < B / 2 + 0.5:
                fs.append(f)
        usun = len(fs)
        bmesh.ops.delete(bm, geom=fs, context='FACES')
        bm.to_mesh(ob.data)
        bm.free()
        ob.data.update()
    M = materialy_barki()
    g = Geo()
    h_burta = 0.95          # wolna burta (pokład główny nad wodą)
    # 2) kadłub: sześciokąt w (u, v) – skośne dziobnice, dno 0,7 m pod wodą, wyciągnięty w ∈ [−B/2, B/2]
    prof = [(-L / 2 + 0.7, -0.7), (L / 2 - 0.7, -0.7), (L / 2, 0.0), (L / 2, h_burta), (-L / 2, h_burta), (-L / 2, 0.0)]
    vs = [R.P(u, w, v) for w in (-B / 2, B / 2) for (u, v) in prof]
    n = len(prof)
    fs = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    fs += [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    g.add(vs, fs, 'kadlub')
    # odbojnica (czarna listwa) i jasny pasek pod krawędzią pokładu
    for s in (-1, 1):
        box(g, R, -L / 2, L / 2, s * B / 2, s * (B / 2 + 0.12), 0.52, 0.74, 'odbojnica')
        box(g, R, -L / 2 + 0.05, L / 2 - 0.05, s * B / 2, s * (B / 2 + 0.012), 0.80, 0.91, 'pasek')
        box(g, R, s * L / 2, s * (L / 2 + 0.12), -B / 2, B / 2, 0.52, 0.74, 'odbojnica')
    # pokład główny
    box(g, R, -L / 2 + 0.05, L / 2 - 0.05, -B / 2 + 0.05, B / 2 - 0.05, h_burta, h_burta + 0.05, 'poklad')
    v_p = h_burta + 0.05
    # 3) salon przeszklony u ∈ [u0, u1], w ∈ ±ws
    u0, u1, ws = -11.0, 12.0, 3.3
    v_c, v_g, v_f, v_d = v_p + 0.30, 3.20, 3.55, 3.70      # cokół / góra szkła / gzyms / pokład górny
    box(g, R, u0, u1, -ws, ws, v_p, v_c, 'rama')
    for s in (-1, 1):
        g.add([R.P(u0 + 0.05, s * (ws - 0.05), v_c), R.P(u1 - 0.05, s * (ws - 0.05), v_c),
               R.P(u1 - 0.05, s * (ws - 0.05), v_g), R.P(u0 + 0.05, s * (ws - 0.05), v_g)], [(0, 1, 2, 3)], 'szklo')
    for uu in (u0 + 0.05, u1 - 0.05):
        g.add([R.P(uu, -ws + 0.05, v_c), R.P(uu, ws - 0.05, v_c), R.P(uu, ws - 0.05, v_g), R.P(uu, -ws + 0.05, v_g)],
              [(0, 1, 2, 3)], 'szklo')
    nb_ = int(round((u1 - u0) / 1.53))
    for k in range(nb_ + 1):
        uk = u0 + (u1 - u0) * k / nb_
        for s in (-1, 1):
            box(g, R, uk - 0.045, uk + 0.045, s * (ws - 0.10), s * (ws + 0.01), v_c, v_g, 'rama')
    for k in range(5):
        wk = -ws + 2 * ws * k / 4
        for uu in (u0, u1):
            box(g, R, uu - 0.06, uu + 0.06, wk - 0.045, wk + 0.045, v_c, v_g, 'rama')
    for s in (-1, 1):
        box(g, R, u0, u1, s * (ws - 0.10), s * (ws + 0.01), 2.66, 2.72, 'rama')           # ślemię (naświetle)
    box(g, R, u0 - 0.05, u1 + 0.05, -ws - 0.05, ws + 0.05, v_g, v_f, 'rama')          # gzyms
    box(g, R, u0 - 0.30, u1 + 0.30, -ws - 0.30, ws + 0.30, v_f, v_d - 0.03, 'rama')   # płyta tarasu
    box(g, R, u0 - 0.27, u1 + 0.27, -ws - 0.27, ws + 0.27, v_d - 0.03, v_d, 'poklad')
    # wnętrze: sufit drewniany, bar, regał, stoły z krzesłami, lampy wiszące
    box(g, R, u0 + 0.1, u1 - 0.1, -ws + 0.1, ws - 0.1, v_g - 0.04, v_g - 0.02, 'sufit_wn')
    box(g, R, 4.0, 9.0, -2.6, -1.7, v_p, v_p + 1.05, 'drewno_wn')
    box(g, R, 3.9, 9.1, -2.7, -1.6, v_p + 1.05, v_p + 1.10, 'ciemne_wn')
    box(g, R, 4.0, 9.0, -ws + 0.12, -ws + 0.40, v_p, v_g - 0.1, 'ciemne_wn')
    rng = np.random.default_rng(31)
    for wr in (2.35, -0.35):
        for k in range(14):
            uk = u0 + 0.9 + k * 1.62
            if wr < 0 and 3.2 < uk < 9.8:
                continue
            box(g, R, uk - 0.38, uk + 0.38, wr - 0.38, wr + 0.38, v_p + 0.72, v_p + 0.76, 'drewno_wn')
            box(g, R, uk - 0.04, uk + 0.04, wr - 0.04, wr + 0.04, v_p, v_p + 0.72, 'ciemne_wn')
            for du in (-0.55, 0.55):
                if rng.random() < 0.85:
                    box(g, R, uk + du - 0.21, uk + du + 0.21, wr - 0.21, wr + 0.21, v_p + 0.44, v_p + 0.49, 'tkanina_wn')
                    sb = 1 if du > 0 else -1
                    box(g, R, uk + du + sb * 0.17, uk + du + sb * 0.21, wr - 0.21, wr + 0.21, v_p + 0.49, v_p + 0.92,
                        'tkanina_wn')
            p = R.P(uk, wr, 2.62)
            kula(g, p, 0.13, 'lampa', nu=8, nv=4, sz=0.8)
            pret(g, (p[0], p[1], p[2] + 0.1), (p[0], p[1], R.z0 + v_g - 0.04), 0.008, 'ciemne_wn', n=3)
    # 4) markiza nad pokładem bocznym od nurtu (+w) z lambrekinem, ramionami i girlandą żarówek
    wm0, wm1, vm0, vm1 = ws + 0.05, B / 2 - 0.08, 3.28, 2.84
    ua, ub = u0 + 0.2, u1 - 0.2
    g.add([R.P(ua, wm0, vm0), R.P(ub, wm0, vm0), R.P(ub, wm1, vm1), R.P(ua, wm1, vm1)], [(0, 1, 2, 3)], 'markiza')
    g.add([R.P(ua, wm1, vm1), R.P(ub, wm1, vm1), R.P(ub, wm1, vm1 - 0.22), R.P(ua, wm1, vm1 - 0.22)], [(0, 1, 2, 3)],
          'markiza')
    for uu in (ua, ub):
        g.add([R.P(uu, wm0, vm0), R.P(uu, wm1, vm1), R.P(uu, wm1, vm1 - 0.22), R.P(uu, wm0, vm1 - 0.22)],
              [(0, 1, 2, 3)], 'markiza')
    n_ram = int(round((ub - ua) / 2.9))
    us = [ua + (ub - ua) * k / n_ram for k in range(n_ram + 1)]
    for uk in us:
        pret(g, R.P(uk, wm0, vm0 - 0.05), R.P(uk, wm1 - 0.02, vm1 - 0.03), 0.02, 'rama')
        pret(g, R.P(uk, wm1 - 0.03, vm1 - 0.25), R.P(uk, wm1 - 0.03, v_p), 0.03, 'rama', n=6)   # słupek markizy
    for ka, kb in zip(us[:-1], us[1:]):
        pts = lancuchowa(R.P(ka, wm1 - 0.06, vm1 - 0.30), R.P(kb, wm1 - 0.06, vm1 - 0.30), 0.16, n=6)
        for p in pts[:-1]:
            kula(g, p, 0.045, 'zarowka', nu=6, nv=3)
        for a, b in zip(pts[:-1], pts[1:]):
            pret(g, a, b, 0.006, 'ciemne_wn', n=3)
    # 5) relingi: pokład główny (h 1,0 m) i taras górny (h 1,1 m)
    def reling(pts_uw, v0, h, krok=1.5, zamk=True):
        P_ = pts_uw + ([pts_uw[0]] if zamk else [])
        for (ua_, wa_), (ub_, wb_) in zip(P_[:-1], P_[1:]):
            dl = math.hypot(ub_ - ua_, wb_ - wa_)
            nk = max(1, int(round(dl / krok)))
            for k in range(nk + (0 if zamk else 1)):
                t = k / nk
                uu, ww = ua_ + (ub_ - ua_) * t, wa_ + (wb_ - wa_) * t
                pret(g, R.P(uu, ww, v0), R.P(uu, ww, v0 + h), 0.022, 'inox', n=4)
            for vv, rr in ((h, 0.028), (h * 0.55, 0.010), (h * 0.25, 0.010)):
                pret(g, R.P(ua_, wa_, v0 + vv), R.P(ub_, wb_, v0 + vv), rr, 'inox', n=4)
    e = 0.12
    reling([(-L / 2 + e, -B / 2 + e), (L / 2 - e, -B / 2 + e), (L / 2 - e, B / 2 - e), (-L / 2 + e, B / 2 - e)], v_p, 1.0)
    reling([(u0 - 0.2, -ws - 0.2), (u1 + 0.2, -ws - 0.2), (u1 + 0.2, ws + 0.2), (u0 - 0.2, ws + 0.2)], v_d, 1.1)
    # 6) taras górny: kiosk-bar (biały, z pasem okien), parasole, stoliki, donice z jesienną zielenią
    ku0, ku1, kw0, kw1 = 6.6, 11.4, -3.1, 0.3
    box(g, R, ku0, ku1, kw0, kw1, v_d, 5.95, 'biel')
    box(g, R, ku0 - 0.3, ku1 + 0.3, kw0 - 0.3, kw1 + 0.35, 5.95, 6.12, 'biel')
    box(g, R, ku0 + 0.4, ku1 - 0.4, kw1, kw1 + 0.02, 4.55, 5.55, 'rama')
    g.add([R.P(ku0 + 0.5, kw1 + 0.025, 4.62), R.P(ku1 - 0.5, kw1 + 0.025, 4.62), R.P(ku1 - 0.5, kw1 + 0.025, 5.48),
           R.P(ku0 + 0.5, kw1 + 0.025, 5.48)], [(0, 1, 2, 3)], 'szklo')
    box(g, R, ku0 - 0.02, ku0, -1.6, -0.6, v_d, 5.7, 'rama')                       # drzwi kiosku
    for (uk, wk, otw) in ((-8.6, 1.3, True), (-4.2, 0.6, True), (0.3, 1.4, False), (3.9, 0.9, True)):
        p = R.P(uk, wk, 0.0)
        parasol(g, p, R.z0 + v_d, R.z0 + 6.15, 1.45, 'parasol', 'rama', otwarty=otw)
        if otw:
            walec(g, R.P(uk + 0.9, wk - 0.4, 0.0), 0.38, R.z0 + v_d + 0.70, R.z0 + v_d + 0.74, 'drewno_wn', n=10)
            pret(g, R.P(uk + 0.9, wk - 0.4, v_d), R.P(uk + 0.9, wk - 0.4, v_d + 0.70), 0.03, 'rama', n=4)
            for du, dw in ((0.55, 0.25), (1.25, -0.6), (0.4, -1.0)):
                box(g, R, uk + du - 0.2, uk + du + 0.2, wk + dw - 0.2, wk + dw + 0.2, v_d + 0.44, v_d + 0.48, 'rama')
                box(g, R, uk + du - 0.2, uk + du + 0.2, wk + dw + 0.17, wk + dw + 0.2, v_d + 0.48, v_d + 0.88, 'rama')
    def krzew(uc, wc, v0, rx, rw, h, n=18):
        """Krzew w donicy: nieregularna kępa małych brył (różne wielkości, wyższe w środku)."""
        for _ in range(n):
            du, dw = rng.uniform(-rx, rx), rng.uniform(-rw, rw)
            f = 1.0 - (du / rx) ** 2 * 0.6
            r = rng.uniform(0.09, 0.19)
            kula(g, R.P(uc + du, wc + dw, v0 + r * 0.6 + rng.uniform(0.0, h * f)), r, 'lisc', nu=6, nv=4,
                 sz=rng.uniform(0.75, 1.1))
    for uk in (-10.4, -6.3, -2.1, 2.0, 5.6):
        box(g, R, uk - 0.7, uk + 0.7, ws - 0.55, ws - 0.05, v_d, v_d + 0.55, 'corten')
        krzew(uk, ws - 0.30, v_d + 0.55, 0.62, 0.18, 0.55)
    for uk in (-13.8, 13.6):
        box(g, R, uk - 0.45, uk + 0.45, B / 2 - 1.0, B / 2 - 0.45, v_p, v_p + 0.5, 'corten')
        krzew(uk, B / 2 - 0.72, v_p + 0.5, 0.38, 0.18, 0.45, n=12)
    # koła ratunkowe na relingu od nurtu
    for uk in (-13.3, 12.9):
        cc = np.array(R.P(uk, B / 2 - 0.10, v_p + 0.62))
        tt = np.array([R.t[0], R.t[1], 0.0])
        zz = np.array([0, 0, 1.0])
        pr = [cc + 0.30 * (math.cos(2 * math.pi * k / 12) * tt + math.sin(2 * math.pi * k / 12) * zz) for k in range(13)]
        for a, b in zip(pr[:-1], pr[1:]):
            pret(g, a, b, 0.055, 'pomarancz', n=4)
    # 7) polery, cumy do nabrzeża i kładka na taras górny
    linia = _linia_nabrzeza(R)
    for (uk, wk) in ((-L / 2 + 0.9, -B / 2 + 0.55), (L / 2 - 0.9, -B / 2 + 0.55), (-6.0, -B / 2 + 0.45),
                     (6.0, -B / 2 + 0.45), (-L / 2 + 0.9, B / 2 - 0.55), (L / 2 - 0.9, B / 2 - 0.55)):
        walec(g, R.P(uk, wk, 0.0), 0.12, R.z0 + v_p, R.z0 + v_p + 0.38, 'rama', n=8)
    for (uk, wk, uq) in ((-L / 2 + 0.9, -B / 2 + 0.55, -L / 2 - 3.5), (L / 2 - 0.9, -B / 2 + 0.55, L / 2 + 3.5),
                         (-6.0, -B / 2 + 0.45, 2.0), (6.0, -B / 2 + 0.45, -2.0)):
        wq, zq = _w_nabrzeza(linia, uq)
        a = R.P(uk, wk, v_p + 0.32)
        b = R.P(uq, wq - 0.35, 0.0)
        b = (b[0], b[1], zq + 0.25)
        walec(g, (b[0], b[1]), 0.14, zq, zq + 0.45, 'rama', n=8)
        pts = lancuchowa(a, b, 0.35, n=10)
        for p, q in zip(pts[:-1], pts[1:]):
            pret(g, p, q, 0.028, 'lina', n=4)
    # kładka z korony nabrzeża na taras górny (biała, z poręczami) – u ≈ −1,4
    uk_ = -1.4
    wq, zq = _w_nabrzeza(linia, uk_)
    w0_, w1_, z0_, z1_ = -ws - 0.3, wq - 0.2, R.z0 + v_d, zq + 0.02
    for du in (-0.65, 0.65):
        a = R.P(uk_ + du, w0_, 0.0)
        b = R.P(uk_ + du, w1_, 0.0)
        pret(g, (a[0], a[1], z0_ + 1.0), (b[0], b[1], z1_ + 1.0), 0.03, 'biel', n=4)
        pret(g, (a[0], a[1], z0_ + 0.5), (b[0], b[1], z1_ + 0.5), 0.015, 'biel', n=4)
        for t in np.linspace(0, 1, 5):
            p = np.array(a) + (np.array(b) - np.array(a)) * t
            zt = z0_ + (z1_ - z0_) * t
            pret(g, (p[0], p[1], zt), (p[0], p[1], zt + 1.0), 0.025, 'biel', n=4)
    pa, pb = R.P(uk_ - 0.65, w0_, 0.0), R.P(uk_ + 0.65, w0_, 0.0)
    pc, pd = R.P(uk_ + 0.65, w1_, 0.0), R.P(uk_ - 0.65, w1_, 0.0)
    g.add([(pa[0], pa[1], z0_), (pb[0], pb[1], z0_), (pc[0], pc[1], z1_), (pd[0], pd[1], z1_)], [(0, 1, 2, 3)], 'biel')
    coll = bpy.data.collections.get('ZG3_barka') or bpy.data.collections.new('ZG3_barka')
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    ob = g.obiekt('ZG3_barka', M, coll)
    print('[zg3] barka-restauracja z detalem: %d ścian (usunięto %d ścian uproszczonej barki)' % (len(ob.data.polygons), usun))
    return len(ob.data.polygons)


# ============================================================================================== woda, mur, ludzie
def zmarszczka_wody(amp=0.002, skala=0.5, az_osi=260.0):
    """Dodatkowy szum normalnych wody (Bump: wysokość = szum, dystans ~ amplituda); grzbiety wydłużone w poprzek osi
    widzenia (pionowe smugi odbić przy patrzeniu po tafli)."""
    m = bpy.data.materials.get('K_woda')
    if m is None or not m.node_tree:
        return False
    nt = m.node_tree
    if 'ZG3_zmarszczka' in nt.nodes:
        nt.nodes['ZG3_zmarszczka'].inputs['Distance'].default_value = amp * 6.0
        return True
    bump = next((n for n in nt.nodes if n.bl_idname == 'ShaderNodeBump'), None)
    if bump is None:
        return False
    cele = [l.to_socket for l in nt.links if l.from_node == bump]
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    a = math.radians(az_osi)
    # obrót Rz(az): x' = w poprzek osi widzenia, y' = wzdłuż osi (d = (sin az, cos az)); potem skala – grzbiety
    # 2,5 × dłuższe w poprzek osi niż ich rozstaw wzdłuż osi
    mr = nt.nodes.new('ShaderNodeMapping')
    mr.inputs['Rotation'].default_value = (0.0, 0.0, a)
    nt.links.new(geo.outputs['Position'], mr.inputs['Vector'])
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (0.40, 1.0, 1.0)
    nt.links.new(mr.outputs[0], mp.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise')
    nz.inputs['Scale'].default_value = 1.0 / skala
    nz.inputs['Detail'].default_value = 4.0
    nz.inputs['Roughness'].default_value = 0.55
    nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    b2 = nt.nodes.new('ShaderNodeBump')
    b2.name = 'ZG3_zmarszczka'
    b2.inputs['Strength'].default_value = 1.0
    b2.inputs['Distance'].default_value = amp * 6.0          # szum Fac: odchylenie ~0,17 → amplituda ≈ amp
    nt.links.new(nz.outputs['Fac'], b2.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b2.inputs['Normal'])
    for s in cele:
        nt.links.new(b2.outputs['Normal'], s)
    print('[zg3] zmarszczka wody: amplituda ~%.1f mm, skala %.2f m' % (amp * 1000, skala))
    return True


def wyrownaj_uskok_muru(a=(127.95, 63.03), b=(128.6, 60.88), wierzch=((128.21, 63.13), (128.56, 62.07), (128.9, 61.0))):
    """Uskok lica muru nabrzeża 0,3 m (dane brzegu) rzuca w porannym słońcu pionowy cień – z wody czytany jako słup
    przecinający cokół wieży. Wierzchołki wysuniętego odcinka rzutowane na prostą sąsiednich odcinków."""
    ob = bpy.data.objects.get('nabrzeze')
    if ob is None:
        return 0
    A, Bv = np.array(a), np.array(b)
    d = (Bv - A) / np.linalg.norm(Bv - A)
    Mi = ob.matrix_world.inverted()
    Mw = ob.matrix_world
    n = 0
    for v in ob.data.vertices:
        p = Mw @ v.co
        for q in wierzch:
            if abs(p.x - q[0]) < 0.03 and abs(p.y - q[1]) < 0.03:
                t = float((np.array([p.x, p.y]) - A) @ d)
                r = A + d * t
                v.co = Mi @ Vector((r[0], r[1], p.z))
                n += 1
    ob.data.update()
    print('[zg3] uskok lica muru nabrzeża wyrównany (%d wierzchołków)' % n)
    return n


PIESI_BULWAR = (
    # (e, n, kierunek [°, kompas], indeks prototypu) – korona nabrzeża na lewo od barki, za balustradą
    (124.6, 69.0, 340.0, 0),
    (125.3, 68.3, 336.0, 1),
    (125.65, 64.4, 75.0, 3),
)


def piesi_bulwar():
    if bpy.data.objects.get('czlowiek_bulwar_0') is not None:
        return 0
    proto = [bpy.data.meshes.get('czlowiek_%d' % i) for i in range(10)]
    if not any(proto):
        print('[zg3] brak prototypów ludzi (scena bez ludzi) – piesi na bulwarze pominięci')
        return 0
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    kat = U.mapa_kategorii()
    coll = bpy.data.collections.get('ZG3_barka') or bpy.context.scene.collection
    n = 0
    for i, (e, nn, kier, ip) in enumerate(PIESI_BULWAR):
        me = proto[ip] or next(p for p in proto if p)
        zt, _ = U.podloze(sc, dg, e, nn, kat=kat)
        if zt is None:
            continue
        ob = bpy.data.objects.new('czlowiek_bulwar_%d' % i, me)
        coll.objects.link(ob)
        ob.location = (e, nn, zt + 0.01)
        ob.rotation_euler = (0.0, 0.0, -math.radians(kier))      # prototyp idzie w +y; kompas → obrót wokół Z
        n += 1
    print('[zg3] piesi na bulwarze: %d' % n)
    return n


def popraw_scene():
    wyrownaj_uskok_muru()
    barka_restauracja()
    zmarszczka_wody()
    piesi_bulwar()


# ============================================================================================== łańcuch nakładek
_zb, _wb = U.zbuduj_scene, U.wczytaj_blend


def zbuduj_scene(*a, **k):
    r = _zb(*a, **k)
    popraw_scene()
    return r


def wczytaj_blend(*a, **k):
    r = _wb(*a, **k)
    popraw_scene()
    return r


U.zbuduj_scene, U.wczytaj_blend = zbuduj_scene, wczytaj_blend

if __name__ == '__main__':
    FK.main()
