# -*- coding: utf-8 -*-
"""Render finalny ujęcia „zlota-godzina-5” (Pierwsze światło – teleobiektyw znad Odry od pd.-wsch.) – nakładka na
nakładkę ujęcia ``render/final_zlota_godzina_3.py`` (z niej: model barki-restauracji z detalem, zmarszczka wody,
wyrównany uskok muru nabrzeża) i dalej na wspólną nakładkę finałową ``render/ujecia_finalne_korekty.py``
(→ ``ujecia_poprawki_kontekstu.py`` → ``ujecia_dodatkowe.py``), bez edycji modułów wspólnych. Uruchomienie i argumenty
jak ``ujecia_finalne_korekty.py`` (w tym ``--wycinek``)::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_zlota_godzina_5.py \
        --id zlota-godzina-5 --szer 2000 --probki 64 \
        --out umwd/docs/60_wizualizacje/img/extra/E_zlota-godzina-5.jpg

Warunki wspólne zestawu (z ``ujecia_finalne_korekty.py``, przy budowie sceny od zera): lamele korony łuku wg v1.1
(21 szt.), sitodruk 30 % na szkle korony, w dzień ciepłe oprawy ×0,12.

Poprawki tego ujęcia wg uwag jurorów (po zbudowaniu / wczytaniu sceny, idempotentnie):

1. **Barki z detalem** (juror 2: „barki jak w zlota-godzina-3”): barka-restauracja (131,5; 81,0) – model z
   ``final_zlota_godzina_3.barka_restauracja``; druga barka (145,0; 27,0; 20 × 7 m, w kadrze bliżej i większa) –
   uproszczone pudło z ``context._barka`` zastąpione domem pływającym wg zdjęcia F.17.A: ciemny ponton z odbojnicą,
   pomost obiegowy z relingiem, dom z elewacją z szaroniebieskich desek (pionowy rytm) i pasem paneli w kolorze
   cegły / rdzy od strony nurtu, okna i przeszklone drzwi we wnękach z ościeżami, biała attyka, dach z modułami PV,
   cumy i kładka do nabrzeża.
2. **Gmach DUW za mostem w LOD2** (juror 2: dach i podział okien; juror 3: gzyms, siatka okien, przyciemnienie):
   prosty blok z ``context.BRYLY_DALSZE`` (3 obrysy „DUW – …”, płaski dach na 24 m) zastąpiony bryłą wg zdjęcia F.17.A:
   lica tynkowane (jasny, ciepły tynk – albedo ok. 0,42, nieco ciemniej niż granit wieży), cokół kamienny, 6 rzędów
   okien we wnękach 0,25 m (rytm 2,5 m, parter wyższy, okienka piwnic w cokole), fryz i gzyms wieńczący z wysięgiem
   0,55 m, dach spłaszczony z blachy tytan-cynk (spadek 28°, płaska kalenica), w odcieniu szaroniebieskim jak na
   zdjęciu. Ok. 400 m od kamery – czytelny rytm okien i gzyms zamiast „pudełka”.
3. **Piesi na bulwarze przy lewej krawędzi** (juror 2: 2–3 sylwetki): chodnik bulwaru za ogrodzeniem skarpy
   (e ≈ 135,3–135,9; n 15–20) – jedna osoba idąca na pn. i para idąca na pd.
4. **Perspektywa powietrzna – poranna mgiełka nad Odrą** (jurorzy 1 i 3): krok przed wspólną postprodukcją,
   tryb ``post_przed.mgla.tryb = "zamglenie_poranne"``: piksele zmieszane z barwą zamglenia (barwa nieba tuż nad
   linią zabudowy, mediana z tego kadru) z udziałem ``sila``·w, w = Mist (0 przy ``start`` m, 1 przy
   ``start + glebokosc`` m) ** ``wykladnik``; niebo bez zmian. Start 285 m – wieża (230 m), segment, skrzydło i portal
   mostu (265–280 m) zostają ostre, gmach DUW (330–450 m) i dalekie tło cofają się.
5. **Zmarszczka wody** (``final_zlota_godzina_3.zmarszczka_wody``, grzbiety w poprzek osi widzenia 302°) i wyrównany
   uskok lica muru nabrzeża – jak w zlota-godzina-3.

Kamera wg głosowania jurorów: stanowisko (301; −40; oko 1,65 m), 70 mm (jurorzy 2 i 3), oś 302° (jurorzy 2 i 3),
shift_y 0,05 → 0,09 (jurorzy 1 i 3 – więcej nieba nad attyką, woda ok. 36 %), kadr 3 : 2, pora 2026-10-20 08:07 CEST.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import final_zlota_godzina_3 as ZG3  # noqa: E402  (barka z detalem, zmarszczka wody, uskok muru; importuje FK)
from umwd.render import blib  # noqa: E402

FK = ZG3.FK
U = FK.U
# ZG3 opakowuje budowę sceny własnym zestawem poprawek (w tym piesi zlota-godzina-3) – wracamy do opakowania FK
# i wywołujemy wybrane funkcje ZG3 samodzielnie (popraw_scene poniżej).
U.zbuduj_scene, U.wczytaj_blend = ZG3._zb, ZG3._wb

Z_WODA = ZG3.Z_WODA
AZ_OSI = 302.0
RAPORT = {}


# ============================================================================================== geometria z UV
class Geo2:
    """Siatka z materiałem na ścianę, UV na narożnik ściany i atrybutem ``los`` (FACE) – szkło okien."""

    def __init__(self):
        self.V, self.F, self.M, self.UV, self.L = [], [], [], [], []

    def add(self, vs, m, uv=None, los=0.0):
        b = len(self.V)
        self.V += [tuple(map(float, v)) for v in vs]
        self.F.append(tuple(range(b, b + len(vs))))
        self.M.append(m)
        self.UV.append(uv or [(0.0, 0.0)] * len(vs))
        self.L.append(float(los))

    def tri(self, V3, F3, m):
        b = len(self.V)
        self.V += [tuple(map(float, v)) for v in V3]
        for f in F3:
            self.F.append(tuple(b + int(i) for i in f))
            self.M.append(m)
            self.UV.append([(0.0, 0.0)] * 3)
            self.L.append(0.0)

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
        idx = np.array([slot[k] for k in self.M], dtype=np.int32)
        me.polygons.foreach_set('material_index', idx)
        uvl = me.uv_layers.new(name='UVMap')
        uv = np.array([c for f in self.UV for c in f], dtype=np.float32).ravel()
        uvl.data.foreach_set('uv', uv)
        at = me.attributes.new('los', 'FLOAT', 'FACE')
        at.data.foreach_set('value', np.array(self.L, dtype=np.float32))
        ob = bpy.data.objects.new(nazwa, me)
        coll.objects.link(ob)
        return ob


def sciana(g, P, L, H, otwory, m_sc, m_osc, d=0.2, rng=None):
    """Ściana płaska z prostokątnymi otworami. P(a, z, gl) → punkt świata (a wzdłuż ściany 0…L, z w górę 0…H,
    gl – w głąb muru). Lico pocięte siatką granic otworów; każdy otwór: 4 ościeża głębokości d i szyba (materiał
    z otworu) z UV 0–1 i losową wartością ``los``. otwory: [(a0, a1, z0, z1, m_szyba)]."""
    A = sorted({0.0, float(L)} | {o[0] for o in otwory} | {o[1] for o in otwory})
    Z = sorted({0.0, float(H)} | {o[2] for o in otwory} | {o[3] for o in otwory})
    for i in range(len(A) - 1):
        am = (A[i] + A[i + 1]) / 2
        w_kol = [o for o in otwory if o[0] < am < o[1]]
        for j in range(len(Z) - 1):
            zm = (Z[j] + Z[j + 1]) / 2
            if any(o[2] < zm < o[3] for o in w_kol):
                continue
            g.add([P(A[i], Z[j], 0), P(A[i + 1], Z[j], 0), P(A[i + 1], Z[j + 1], 0), P(A[i], Z[j + 1], 0)], m_sc)
    for (a0, a1, z0, z1, ms) in otwory:
        g.add([P(a0, z0, 0), P(a0, z1, 0), P(a0, z1, d), P(a0, z0, d)], m_osc)
        g.add([P(a1, z0, 0), P(a1, z0, d), P(a1, z1, d), P(a1, z1, 0)], m_osc)
        g.add([P(a0, z1, 0), P(a1, z1, 0), P(a1, z1, d), P(a0, z1, d)], m_osc)
        g.add([P(a0, z0, 0), P(a0, z0, d), P(a1, z0, d), P(a1, z0, 0)], m_osc)
        g.add([P(a0, z0, d), P(a1, z0, d), P(a1, z1, d), P(a0, z1, d)], ms,
              uv=[(0, 0), (1, 0), (1, 1), (0, 1)], los=(rng.random() if rng is not None else 0.5))


# ============================================================================================== materiały
def _mat(nazwa):
    return bpy.data.materials.get(nazwa) or bpy.data.materials.new(nazwa)


def m_tynk(nazwa, kolor, skala=0.08, zm=0.07, rough=0.88, cokol=None):
    """Tynk / kamień z niską zmiennością tonu (plamy, zacieki pionowe); cokol=(z_gora, kolor) – ciemniejszy pas."""
    m = _mat(nazwa)
    nb = blib.NodeBuilder(m)
    geo = nb.n('ShaderNodeNewGeometry')
    mp = nb.n('ShaderNodeMapping', Scale=(1.0, 1.0, 0.25))       # plamy wydłużone w pionie (zacieki)
    nb.l(geo.outputs['Position'], mp.inputs['Vector'])
    nz = nb.n('ShaderNodeTexNoise', Scale=skala * 4.0, Detail=5.0)
    nb.l(mp.outputs[0], nz.inputs['Vector'])
    c0 = tuple(x * (1 - zm) for x in kolor)
    c1 = tuple(min(1.0, x * (1 + zm)) for x in kolor)
    col = nb.mix(nz.outputs['Fac'], c0, c1)
    if cokol:
        sz = nb.n('ShaderNodeSeparateXYZ')
        nb.l(geo.outputs['Position'], sz.inputs[0])
        nb_c = nb.math('LESS_THAN', sz.outputs[2], cokol[0])
        col = nb.mix(nb_c, col, cokol[1])
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=rough)
    nb.l(col, b.inputs['Base Color'])
    nb.output(b)
    return m


def m_okno(nazwa, rama=(0.50, 0.50, 0.47), szklo=(0.010, 0.012, 0.015), szpros=True, rygiel=0.70, ramka=0.07):
    """Okno na prostokącie UV 0–1: rama obwodowa, słupek w osi, rygiel; szyba ciemna z odbiciem (Fresnel);
    atrybut ``los`` – część okien z jaśniejszą firanką / żaluzją za szybą."""
    m = _mat(nazwa)
    nb = blib.NodeBuilder(m)
    uv = nb.n('ShaderNodeUVMap')
    uv.uv_map = 'UVMap'
    sp = nb.n('ShaderNodeSeparateXYZ')
    nb.l(uv.outputs['UV'], sp.inputs[0])
    u, v = sp.outputs[0], sp.outputs[1]
    rk = nb.math('MAXIMUM', nb.math('LESS_THAN', nb.math('MINIMUM', u, nb.math('SUBTRACT', 1.0, u)), ramka),
                 nb.math('LESS_THAN', nb.math('MINIMUM', v, nb.math('SUBTRACT', 1.0, v)), ramka * 0.8))
    if szpros:
        rk = nb.math('MAXIMUM', rk, nb.math('LESS_THAN', nb.math('ABSOLUTE', nb.math('SUBTRACT', u, 0.5)), 0.035))
    if rygiel:
        rk = nb.math('MAXIMUM', rk, nb.math('LESS_THAN', nb.math('ABSOLUTE', nb.math('SUBTRACT', v, rygiel)), 0.03))
    at = nb.n('ShaderNodeAttribute')
    at.attribute_type = 'GEOMETRY'
    at.attribute_name = 'los'
    fir = nb.math('LESS_THAN', at.outputs['Fac'], 0.22)
    sz = nb.mix(nb.math('MULTIPLY', fir, nb.math('GREATER_THAN', v, 0.25)), szklo, (0.12, 0.115, 0.10))
    col = nb.mix(rk, sz, rama)
    rgh = nb.mix(rk, 0.06, 0.5, dtype='FLOAT')
    b = nb.n('ShaderNodeBsdfPrincipled')
    nb.l(col, b.inputs['Base Color'])
    nb.l(rgh, b.inputs['Roughness'])
    nb.output(b)
    return m


def m_plain(nazwa, kolor, rough=0.5, metal=0.0, coat=0.0, szum=None):
    m = _mat(nazwa)
    nb = blib.NodeBuilder(m)
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=rough, Metallic=metal)
    if szum:
        tc = nb.n('ShaderNodeTexCoord')
        nz = nb.n('ShaderNodeTexNoise', Scale=szum[0], Detail=4.0)
        nb.l(tc.outputs['Object'], nz.inputs['Vector'])
        nb.set(b, 'Base Color', nb.mix(nz.outputs['Fac'], tuple(x * (1 - szum[1]) for x in kolor),
                                       tuple(min(1.0, x * (1 + szum[1])) for x in kolor)))
    else:
        nb.set(b, 'Base Color', kolor)
    if coat:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.06
    nb.output(b)
    return m


def m_deski(nazwa, kolor, rozstaw=0.15, zm=0.10):
    """Okładzina z desek pionowych (fug ciemniejszych co ``rozstaw`` m wzdłuż ściany – kierunek z UV-świata)."""
    m = _mat(nazwa)
    nb = blib.NodeBuilder(m)
    geo = nb.n('ShaderNodeNewGeometry')
    sp = nb.n('ShaderNodeSeparateXYZ')
    nb.l(geo.outputs['Position'], sp.inputs[0])
    sn = nb.n('ShaderNodeSeparateXYZ')
    nb.l(geo.outputs['True Normal'], sn.inputs[0])
    a = nb.math('SUBTRACT', nb.math('MULTIPLY', sp.outputs[1], sn.outputs[0]), nb.math('MULTIPLY', sp.outputs[0], sn.outputs[1]))
    fr = nb.math('FRACT', nb.math('DIVIDE', a, rozstaw))
    fuga = nb.math('LESS_THAN', fr, 0.10)
    cid = nb.math('FLOOR', nb.math('DIVIDE', a, rozstaw))
    wn = nb.n('ShaderNodeTexWhiteNoise', props={'noise_dimensions': '1D'})
    nb.l(cid, wn.inputs['W'])
    k = nb.math('ADD', 1.0 - zm, nb.math('MULTIPLY', wn.outputs['Value'], 2 * zm))
    cc = nb.n('ShaderNodeCombineColor')
    for i in range(3):
        nb.l(nb.math('MULTIPLY', k, kolor[i]), cc.inputs[i])
    col = nb.mix(fuga, cc.outputs[0], tuple(x * 0.45 for x in kolor))
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.7)
    nb.l(col, b.inputs['Base Color'])
    nb.output(b)
    return m


# ============================================================================================== (1) barka PV
def _usun_sciany_barki(R, L, B):
    ob = bpy.data.objects.get('barki')
    if ob is None:
        return 0
    Mw = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    fs = []
    for f in bm.faces:
        p = Mw @ f.calc_center_median()
        u, w = R.lok(p.x, p.y)
        if abs(u) < L / 2 + 0.5 and abs(w) < B / 2 + 0.5:
            fs.append(f)
    bmesh.ops.delete(bm, geom=fs, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return len(fs)


def barka_pv(c=(145.0, 27.0), rot=-12.0, L=20.0, B=7.0):
    """Dom pływający z dachem PV (zdjęcie F.17.A, barka przy nabrzeżu na pd. od restauracji)."""
    if bpy.data.objects.get('ZG5_barka_pv') is not None:
        return 0
    R = ZG3.Rama(c, rot, Z_WODA)
    usun = _usun_sciany_barki(R, L, B)
    M = ZG3.materialy_barki()
    M['deski'] = m_deski('ZG5_deski_szaroniebieskie', (0.135, 0.165, 0.195), rozstaw=0.16)
    M['panel'] = m_plain('ZG5_panel_ceglany', (0.34, 0.095, 0.040), 0.55, szum=(1.5, 0.12))
    M['attyka'] = m_plain('ZG5_attyka_biala', (0.68, 0.68, 0.65), 0.45)
    M['osc'] = m_plain('ZG5_oscieze_barki', (0.05, 0.055, 0.06), 0.5, metal=0.3)
    M['okno'] = m_okno('ZG5_okno_barki', rama=(0.04, 0.042, 0.045), szpros=False, rygiel=0.0, ramka=0.05)
    M['drzwi'] = m_okno('ZG5_drzwi_barki', rama=(0.04, 0.042, 0.045), szpros=True, rygiel=0.0, ramka=0.06)
    M['pv'] = m_plain('ZG5_pv', (0.018, 0.026, 0.055), 0.35, coat=1.0)
    M['ponton'] = m_plain('ZG5_ponton', (0.030, 0.032, 0.036), 0.5, szum=(1.0, 0.15))
    g = ZG3.Geo()
    g2 = Geo2()
    rng = np.random.default_rng(55)
    hb = 0.55
    # ponton ze skośnymi końcami
    prof = [(-L / 2 + 0.4, -0.6), (L / 2 - 0.4, -0.6), (L / 2, 0.0), (L / 2, hb), (-L / 2, hb), (-L / 2, 0.0)]
    vs = [R.P(u, w, v) for w in (-B / 2, B / 2) for (u, v) in prof]
    n = len(prof)
    fs = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    fs += [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    g.add(vs, fs, 'ponton')
    for s in (-1, 1):
        ZG3.box(g, R, -L / 2, L / 2, s * B / 2, s * (B / 2 + 0.12), 0.22, 0.42, 'odbojnica')
        ZG3.box(g, R, s * L / 2, s * (L / 2 + 0.12), -B / 2, B / 2, 0.22, 0.42, 'odbojnica')
    ZG3.box(g, R, -L / 2 + 0.03, L / 2 - 0.03, -B / 2 + 0.03, B / 2 - 0.03, hb, hb + 0.05, 'poklad')
    z0 = hb + 0.05
    hu0, hu1, hw, H = -9.0, 9.0, 2.85, 3.05
    # ściany domu (a wzdłuż, z od pokładu, gl w głąb); prawa normalna kierunku obejścia = na zewnątrz
    sciany = [
        # od nurtu (+w): z pd. na pn.; lewa część – deski z oknami, prawa – panele ceglane z drzwiami
        (lambda a, z, gl: R.P(hu0 + a, hw - gl, z0 + z), hu1 - hu0),
        # pn. koniec (+u): z +w na −w
        (lambda a, z, gl: R.P(hu1 - gl, hw - a, z0 + z), 2 * hw),
        # od nabrzeża (−w): z pn. na pd.
        (lambda a, z, gl: R.P(hu1 - a, -hw + gl, z0 + z), hu1 - hu0),
        # pd. koniec (−u): z −w na +w
        (lambda a, z, gl: R.P(hu0 + gl, -hw + a, z0 + z), 2 * hw),
    ]
    okna = [
        [(0.8, 2.6, 0.85, 2.35, 'okno'), (3.4, 5.2, 0.85, 2.35, 'okno'), (6.0, 7.8, 0.85, 2.35, 'okno'),
         (9.6, 10.8, 0.05, 2.35, 'drzwi'), (12.4, 14.4, 0.85, 2.35, 'okno'), (15.6, 16.8, 0.05, 2.35, 'drzwi')],
        [(1.6, 4.1, 0.85, 2.35, 'okno')],
        [(1.2, 3.0, 1.10, 2.35, 'okno'), (5.0, 6.8, 1.10, 2.35, 'okno'), (10.0, 11.2, 0.05, 2.35, 'drzwi'),
         (13.0, 14.8, 1.10, 2.35, 'okno')],
        [(0.9, 2.1, 0.05, 2.35, 'drzwi'), (2.9, 5.0, 0.85, 2.35, 'okno')],
    ]
    for (P, Ls), ot in zip(sciany, okna):
        sciana(g2, P, Ls, H, [(a0, a1, zz0, zz1, ms) for (a0, a1, zz0, zz1, ms) in ot], 'deski', 'osc', d=0.14,
               rng=rng)
    # pas paneli ceglanych od nurtu (a 8,6–18,0) – nakładka 2 cm przed licem desek, z otworami drzwi i okna
    Pn = sciany[0][0]
    for (a0, a1) in ((8.6, 9.6), (10.8, 12.4), (14.4, 15.6), (16.8, 18.0)):
        g2.add([Pn(a0, 0.0, -0.02), Pn(a1, 0.0, -0.02), Pn(a1, H, -0.02), Pn(a0, H, -0.02)], 'panel')
    for (a0, a1) in ((12.4, 14.4),):
        g2.add([Pn(a0, 0.0, -0.02), Pn(a1, 0.0, -0.02), Pn(a1, 0.85, -0.02), Pn(a0, 0.85, -0.02)], 'panel')
        g2.add([Pn(a0, 2.35, -0.02), Pn(a1, 2.35, -0.02), Pn(a1, H, -0.02), Pn(a0, H, -0.02)], 'panel')
    for (a0, a1) in ((9.6, 10.8), (15.6, 16.8)):
        g2.add([Pn(a0, 2.35, -0.02), Pn(a1, 2.35, -0.02), Pn(a1, H, -0.02), Pn(a0, H, -0.02)], 'panel')
    # dach, attyka biała, moduły PV (2 rzędy × 16, nachylenie 8° ku pd.-wsch.)
    ZG3.box(g, R, hu0 - 0.06, hu1 + 0.06, -hw - 0.06, hw + 0.06, H + z0 - 0.02, H + z0 + 0.05, 'osc')
    for (u0_, u1_, w0_, w1_) in ((hu0 - 0.08, hu1 + 0.08, hw - 0.12, hw + 0.08), (hu0 - 0.08, hu1 + 0.08, -hw - 0.08, -hw + 0.12),
                                 (hu0 - 0.08, hu0 + 0.12, -hw - 0.08, hw + 0.08), (hu1 - 0.12, hu1 + 0.08, -hw - 0.08, hw + 0.08)):
        ZG3.box(g, R, u0_, u1_, w0_, w1_, H + z0 - 0.05, H + z0 + 0.32, 'attyka')
    zp = H + z0 + 0.10
    for rw in (-1.35, 1.35):
        for kk in range(16):
            uk = hu0 + 0.35 + kk * 1.07
            w0_, w1_ = rw - 0.82, rw + 0.82
            pa = [R.P(uk, w0_, zp), R.P(uk + 1.02, w0_, zp), R.P(uk + 1.02, w1_, zp + 0.23), R.P(uk, w1_, zp + 0.23)]
            g.add(pa, [(0, 1, 2, 3)], 'pv')
    # reling pomostu (0,9 m) i kładka do nabrzeża (u ≈ −3)
    e = 0.10
    obw = [(-L / 2 + e, -B / 2 + e), (L / 2 - e, -B / 2 + e), (L / 2 - e, B / 2 - e), (-L / 2 + e, B / 2 - e),
           (-L / 2 + e, -B / 2 + e)]
    for (ua, wa), (ub, wb) in zip(obw[:-1], obw[1:]):
        dl = math.hypot(ub - ua, wb - wa)
        nk = max(1, int(round(dl / 1.6)))
        for kk in range(nk):
            t = kk / nk
            ZG3.pret(g, R.P(ua + (ub - ua) * t, wa + (wb - wa) * t, z0), R.P(ua + (ub - ua) * t, wa + (wb - wa) * t, z0 + 0.9),
                     0.02, 'inox')
        for vv, rr in ((0.9, 0.025), (0.5, 0.009)):
            ZG3.pret(g, R.P(ua, wa, z0 + vv), R.P(ub, wb, z0 + vv), rr, 'inox')
    linia = ZG3._linia_nabrzeza(R)
    for (uk, uq) in ((-L / 2 + 0.8, -L / 2 - 2.5), (L / 2 - 0.8, L / 2 + 2.5)):
        wq, zq = ZG3._w_nabrzeza(linia, uq)
        a = R.P(uk, -B / 2 + 0.4, z0 + 0.3)
        bq = R.P(uq, wq - 0.3, 0.0)
        bq = (bq[0], bq[1], zq + 0.2)
        ZG3.walec(g, R.P(uk, -B / 2 + 0.4, 0.0), 0.11, R.z0 + z0, R.z0 + z0 + 0.35, 'rama', n=8)
        pts = ZG3.lancuchowa(a, bq, 0.4, n=10)
        for p, q in zip(pts[:-1], pts[1:]):
            ZG3.pret(g, p, q, 0.025, 'lina', n=4)
    uk_ = -3.0
    wq, zq = ZG3._w_nabrzeza(linia, uk_)
    w0_, w1_, zz0, zz1 = -B / 2, wq - 0.2, R.z0 + z0, zq + 0.02
    for du in (-0.6, 0.6):
        a = R.P(uk_ + du, w0_, 0.0)
        b = R.P(uk_ + du, w1_, 0.0)
        ZG3.pret(g, (a[0], a[1], zz0 + 1.0), (b[0], b[1], zz1 + 1.0), 0.03, 'inox', n=4)
        for t in np.linspace(0, 1, 4):
            p = np.array(a) + (np.array(b) - np.array(a)) * t
            zt = zz0 + (zz1 - zz0) * t
            ZG3.pret(g, (p[0], p[1], zt), (p[0], p[1], zt + 1.0), 0.022, 'inox', n=4)
    pa, pb = R.P(uk_ - 0.6, w0_, 0.0), R.P(uk_ + 0.6, w0_, 0.0)
    pc, pd = R.P(uk_ + 0.6, w1_, 0.0), R.P(uk_ - 0.6, w1_, 0.0)
    g.add([(pa[0], pa[1], zz0), (pb[0], pb[1], zz0), (pc[0], pc[1], zz1), (pd[0], pd[1], zz1)], [(0, 1, 2, 3)], 'rama')
    # donice z jesienną zielenią na pomoście pd. (jak na zdjęciu: zieleń wokół barki)
    for (uk, wk) in ((-9.6, 2.6), (-9.6, -2.2), (9.6, 2.6)):
        ZG3.box(g, R, uk - 0.25, uk + 0.25, wk - 0.35, wk + 0.35, z0, z0 + 0.45, 'corten')
        for _ in range(9):
            r = rng.uniform(0.10, 0.18)
            ZG3.kula(g, R.P(uk + rng.uniform(-0.2, 0.2), wk + rng.uniform(-0.3, 0.3), z0 + 0.45 + r * 0.6 + rng.uniform(0, 0.3)),
                     r, 'lisc', nu=6, nv=4)
    coll = bpy.data.collections.get('ZG3_barka') or bpy.data.collections.new('ZG3_barka')
    if coll.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(coll)
    o1 = g.obiekt('ZG5_barka_pv', M, coll)
    o2 = g2.obiekt('ZG5_barka_pv_sciany', M, coll)
    n_sc = len(o1.data.polygons) + len(o2.data.polygons)
    RAPORT['barka_pv'] = dict(srodek=list(c), obrot_deg=rot, L=L, B=B, scian=n_sc, usunieto_scian_uproszczonej=usun)
    print('[zg5] barka z dachem PV: %d ścian (usunięto %d ścian uproszczonej barki)' % (n_sc, usun))
    return n_sc


# ============================================================================================== (2) DUW LOD2
DUW = dict(rytm=2.5, szer_okna=1.20, rzedy=[(2.0, 4.3), (5.4, 7.4), (8.7, 10.7), (12.0, 14.0), (15.3, 17.3),
                                            (18.6, 20.4)],
           piwnica=(0.55, 1.05, 0.85), cokol=1.5, fryz=(21.0, 21.8), gzyms=(21.8, 22.5), wysieg_fryzu=0.10,
           wysieg_gzymsu=0.55, dach_h=3.4, dach_spadek=28.0, gl_okna=0.25,
           tynk=(0.43, 0.405, 0.35), cokol_kol=(0.27, 0.26, 0.245), gzyms_kol=(0.46, 0.435, 0.38),
           dach_kol=(0.22, 0.245, 0.265))


def _pierscienie(P):
    """Pierścienie wielokąta (zewn. CCW, wewn. CW) – po prawej stronie kierunku obejścia jest zewnątrz bryły."""
    from shapely.geometry.polygon import orient
    out = []
    for part in ([P] if P.geom_type == 'Polygon' else list(P.geoms)):
        part = orient(part, 1.0)
        out.append(list(part.exterior.coords)[:-1])
        for r in part.interiors:
            out.append(list(r.coords)[:-1])
    return out


def _sciany_pierscienia(g, P, z0, z1, m):
    for ring in _pierscienie(P):
        k = len(ring)
        for i in range(k):
            (x0, y0), (x1, y1) = ring[i], ring[(i + 1) % k]
            g.add([(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)], m)


def _plaszczyzna(g, P, z, m, w_dol=False):
    from umwd.render import context as C
    V2, F = C.triangulacja(P, None)
    if len(F) == 0:
        return
    F = F[:, ::-1] if w_dol else F
    g.tri([(x, y, z) for x, y in V2], F, m)


def duw_lod2():
    if bpy.data.objects.get('ZG5_DUW') is not None:
        return 0
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    import shapely
    from umwd.render import context as C
    polys = [Polygon(p).buffer(0) for (nm, p, h, kol, md) in C.BRYLY_DALSZE if nm.startswith('DUW')]
    F = unary_union(polys).buffer(0.05, join_style=2).buffer(-0.05, join_style=2).simplify(0.05)
    ob = bpy.data.objects.get('bryly_dalsze')
    if ob is None:
        return 0
    # usunięcie prostych brył DUW z obiektu bryly_dalsze (ściany i dach), odczyt rzędnych
    strefa = F.buffer(0.6)
    Mw = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    usun, zs = [], []
    for f in bm.faces:
        c = Mw @ f.calc_center_median()
        if strefa.contains(Point(c.x, c.y)):
            usun.append(f)
            zs += [(Mw @ v.co).z for v in f.verts]
    bmesh.ops.delete(bm, geom=usun, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    zb, zt = min(zs), max(zs)
    zg = zt - 24.0                     # teren (średnia z obrysu) – context: zt = mean(z) + 24
    p = DUW
    M = {'tynk': m_tynk('ZG5_duw_tynk', p['tynk'], cokol=(zg + p['cokol'], p['cokol_kol'])),
         'osc': m_tynk('ZG5_duw_oscieze', tuple(x * 0.86 for x in p['tynk']), zm=0.04),
         'gzyms': m_tynk('ZG5_duw_gzyms', p['gzyms_kol'], zm=0.05),
         'okno': m_okno('ZG5_duw_okno', rama=(0.52, 0.52, 0.49)),
         'piwnica': m_okno('ZG5_duw_piwnica', rama=(0.20, 0.20, 0.19), szpros=False, rygiel=0.0),
         'dach': m_plain('ZG5_duw_dach', p['dach_kol'], rough=0.48, metal=0.30, szum=(0.05, 0.10))}
    g = Geo2()
    rng = np.random.default_rng(1945)
    a, wo = p['rytm'], p['szer_okna']
    z_sciany = p['fryz'][0]
    n_okien = 0
    for ring in _pierscienie(F):
        k = len(ring)
        for i in range(k):
            (x0, y0), (x1, y1) = ring[i], ring[(i + 1) % k]
            L = math.hypot(x1 - x0, y1 - y0)
            if L < 1e-3:
                continue
            tx, ty = (x1 - x0) / L, (y1 - y0) / L
            nx, ny = ty, -tx                                     # na zewnątrz (prawa normalna)

            def P(s, z, gl, x0=x0, y0=y0, tx=tx, ty=ty, nx=nx, ny=ny):
                return (x0 + tx * s - nx * gl, y0 + ty * s - ny * gl, zb + z)

            nb_ = int((L - 1.6) // a)
            otw = []
            if nb_ >= 1:
                s0 = (L - (nb_ - 1) * a) / 2
                for j in range(nb_):
                    sc_ = s0 + j * a
                    for (r0, r1) in p['rzedy']:
                        otw.append((sc_ - wo / 2, sc_ + wo / 2, zg - zb + r0, zg - zb + r1, 'okno'))
                    pw = p['piwnica']
                    otw.append((sc_ - pw[2] / 2, sc_ + pw[2] / 2, zg - zb + pw[0], zg - zb + pw[1], 'piwnica'))
                n_okien += nb_ * len(p['rzedy'])
            sciana(g, P, L, z_sciany + zg - zb, otw, 'tynk', 'osc', d=p['gl_okna'], rng=rng)
    # fryz i gzyms wieńczący
    Ff = F.buffer(p['wysieg_fryzu'], join_style=2)
    Fg = F.buffer(p['wysieg_gzymsu'], join_style=2)
    _sciany_pierscienia(g, Ff, zg + p['fryz'][0], zg + p['fryz'][1], 'gzyms')
    _plaszczyzna(g, Ff.difference(F), zg + p['fryz'][0], 'gzyms', w_dol=True)
    _sciany_pierscienia(g, Fg, zg + p['gzyms'][0], zg + p['gzyms'][1], 'gzyms')
    _plaszczyzna(g, Fg.difference(Ff), zg + p['gzyms'][0], 'gzyms', w_dol=True)
    # dach spłaszczony: z = gzyms + min(h, tg(spadek)·odległość od okapu) – siatka 1,5 m
    V2, Ft = C.triangulacja(Fg, 1.5)
    d = shapely.distance(Fg.boundary, shapely.points(V2[:, 0], V2[:, 1]))
    zr = zg + p['gzyms'][1] + np.minimum(p['dach_h'], math.tan(math.radians(p['dach_spadek'])) * d)
    g.tri(np.c_[V2, zr], Ft, 'dach')
    coll = next((c for c in bpy.data.collections if c.name.split('.')[0] == 'K_dalsze'), bpy.context.scene.collection)
    o = g.obiekt('ZG5_DUW', M, coll)
    RAPORT['duw'] = dict(scian=len(o.data.polygons), okien=n_okien, teren_z=round(zg, 2),
                         gzyms_z=round(zg + p['gzyms'][1], 2), kalenica_z=round(zg + p['gzyms'][1] + p['dach_h'], 2),
                         usunieto_scian_bloku=len(usun), obwod_m=round(F.length, 1), pole_m2=round(F.area, 1),
                         parametry={k: v for k, v in p.items()})
    print('[zg5] DUW LOD2: %d ścian, %d okien, gzyms %.2f, kalenica %.2f (usunięto %d ścian bloku)'
          % (len(o.data.polygons), n_okien, zg + p['gzyms'][1], zg + p['gzyms'][1] + p['dach_h'], len(usun)))
    return len(o.data.polygons)


# ============================================================================================== (3) piesi
PIESI_BULWAR = (
    # (e, n, kierunek [° kompas], indeks prototypu) – chodnik bulwaru za ogrodzeniem skarpy, lewa krawędź kadru
    (135.75, 15.4, 352.0, 2),
    (135.35, 19.7, 171.0, 5),
    (135.95, 20.2, 172.0, 7),
)


def piesi_bulwar():
    if bpy.data.objects.get('czlowiek_bulwar5_0') is not None:
        return 0
    proto = [bpy.data.meshes.get('czlowiek_%d' % i) for i in range(10)]
    if not any(proto):
        print('[zg5] brak prototypów ludzi (scena bez ludzi) – piesi na bulwarze pominięci')
        return 0
    sc = bpy.context.scene
    dg = bpy.context.evaluated_depsgraph_get()
    kat = U.mapa_kategorii()
    coll = bpy.data.collections.get('ZG3_barka') or sc.collection
    n = 0
    for i, (e, nn, kier, ip) in enumerate(PIESI_BULWAR):
        me = proto[ip] or next(p_ for p_ in proto if p_)
        zt, _ = U.podloze(sc, dg, e, nn, kat=kat)
        if zt is None:
            continue
        ob = bpy.data.objects.new('czlowiek_bulwar5_%d' % i, me)
        coll.objects.link(ob)
        ob.location = (e, nn, zt + 0.01)
        ob.rotation_euler = (0.0, 0.0, -math.radians(kier))
        n += 1
    print('[zg5] piesi na bulwarze: %d' % n)
    return n


def popraw_scene():
    ZG3.wyrownaj_uskok_muru()
    ZG3.barka_restauracja()
    barka_pv()
    duw_lod2()
    ZG3.zmarszczka_wody(az_osi=AZ_OSI)
    piesi_bulwar()


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


# ============================================================================================== (4) zamglenie poranne
_pp = FK.post_przed


def _post_przed_p(png, passy, cfg, raport):
    """``mgla.tryb == 'zamglenie_poranne'``: mieszanie z barwą zamglenia = mediana barwy nieba w pasie tuż nad linią
    zabudowy (z tego kadru), udział ``sila``·w, w = Mist ** wykladnik (niebo w = 0); lekkie odbarwienie ``desat``·w."""
    mg = (cfg or {}).get('mgla') or {}
    if mg.get('tryb') != 'zamglenie_poranne':
        return _pp(png, passy, cfg, raport)
    import shutil
    from PIL import Image
    from scipy import ndimage
    png = Path(png)
    shutil.copyfile(png, png.with_name(png.stem + '_surowy.png'))
    a = np.asarray(Image.open(png).convert('RGB'), dtype=np.float32) / 255.0
    lin = FK._s2l(a)
    mist = FK._wczytaj_exr(passy['mgla'])
    idx = FK._wczytaj_exr(passy['idx'])
    if mist.shape != a.shape[:2]:
        raise RuntimeError('passy %s ≠ obraz %s' % (mist.shape, a.shape[:2]))
    H, W = mist.shape
    niebo = (mist > 0.9999) & (idx < 0.5)
    # pas nieba nad linią zabudowy: w każdej kolumnie najniższe piksele nieba (do 4 % wysokości kadru nad nimi)
    pas = np.zeros_like(niebo)
    gl = int(0.04 * H)
    for x in range(0, W, 2):
        col = niebo[:, x]
        if not col.any():
            continue
        dol = np.nonzero(col)[0].max()             # wiersze od góry – najniższy piksel nieba
        pas[max(0, dol - gl):dol + 1, x] = col[max(0, dol - gl):dol + 1]
    if pas.sum() < 200:
        pas = niebo
    haze = np.median(lin[pas], axis=0) * float(mg.get('jasnosc', 1.0))
    w = np.clip(mist, 0, 1) ** float(mg.get('wykladnik', 1.0))
    w = np.where(niebo, 0.0, w)
    w = ndimage.gaussian_filter(w, 0.8)
    al = float(mg.get('sila', 0.35)) * w
    lin = lin * (1.0 - al[..., None]) + al[..., None] * haze[None, None, :]
    ds = float(mg.get('desat', 0.0))
    if ds:
        Lm = FK._lum(lin)[..., None]
        lin = Lm + (lin - Lm) * (1.0 - ds * w[..., None])
    out = (FK._l2s(lin) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(png)
    raport.update({'zamglenie_udzial_kadru_w>0.3': round(float((w > 0.3).mean()), 3),
                   'zamglenie_barwa_lin': [round(float(x), 4) for x in haze],
                   'zamglenie_max_udzial': round(float(al.max()), 3),
                   'zamglenie_pas_nieba_px': int(pas.sum())})
    print('[zg5] zamglenie: w>0,3 na %.1f %% kadru, barwa %s, max udział %.2f'
          % (100 * (w > 0.3).mean(), haze.round(3), al.max()))


FK.post_przed = _post_przed_p


# ============================================================================================== raport kontroli
def _rzut(sc, cam, pts):
    from bpy_extras.object_utils import world_to_camera_view
    uv = [world_to_camera_view(sc, cam, Vector(p)) for p in pts]
    uv = [v for v in uv if v.z > 0]
    if not uv:
        return None
    return dict(x0=round(min(v.x for v in uv), 3), x1=round(max(v.x for v in uv), 3),
                y0=round(min(v.y for v in uv), 3), y1=round(max(v.y for v in uv), 3))


def kontrola_zg5(sc):
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation.copy()
    out = {}
    for nm in ('ZG5_DUW', 'ZG5_barka_pv', 'ZG3_barka'):
        ob = bpy.data.objects.get(nm)
        if ob is None:
            continue
        vs = ob.data.vertices
        krok = max(1, len(vs) // 3000)
        out[nm] = _rzut(sc, cam, [ob.matrix_world @ vs[i].co for i in range(0, len(vs), krok)])
    piesi = {}
    for ob in [o for o in sc.objects if o.name.startswith('czlowiek_bulwar5_')]:
        p0 = ob.location
        r = _rzut(sc, cam, [p0, p0 + Vector((0, 0, 1.7))])
        wid = {}
        for nazwa, h in (('glowa', 1.6), ('piers', 1.3), ('pas', 0.95), ('kolana', 0.5)):
            P3 = p0 + Vector((0, 0, h))
            d = P3 - loc
            hit, pos, nrm, i_, obh, mx = sc.ray_cast(dg, loc, d.normalized(), distance=d.length + 0.5)
            wid[nazwa] = obh.name if hit else None
        piesi[ob.name] = dict(kadr=r, trafienie_promienia=wid, odl_m=round((p0 - loc).length, 1))
    out['piesi_bulwar'] = piesi
    # siatka promieni: udział obiektów dodanych w tym ujęciu
    nx, ny = 48, 32
    licz = {}
    for j in range(ny):
        for i in range(nx):
            d = U._kierunek_kadru(cam, sc, (i + 0.5) / nx, (j + 0.5) / ny)
            hit, pos, nrm, i_, obh, mx = sc.ray_cast(dg, loc, d)
            if hit and obh.name.startswith(('ZG5_', 'ZG3_')):
                k = obh.name.replace('_sciany', '')
                licz[k] = licz.get(k, 0) + 1
    out['udzial_kadru'] = {k: round(v / (nx * ny), 4) for k, v in licz.items()}
    return out


_ru = U.render_ujecia


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    out_jpg = Path(out_jpg)
    try:
        r.setdefault('korekty', {})['zg5'] = dict(RAPORT, kontrola=kontrola_zg5(sc))
    except Exception as e:  # raport pomocniczy – nie przerywa
        r.setdefault('korekty', {})['zg5'] = dict(RAPORT, blad=repr(e))
    print('[zg5] kontrola: %s' % json.dumps(r['korekty']['zg5'].get('kontrola', {}), ensure_ascii=False))
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p

if __name__ == '__main__':
    FK.main()
