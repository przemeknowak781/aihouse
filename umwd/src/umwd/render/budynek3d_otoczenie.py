# -*- coding: utf-8 -*-
"""Zagospodarowanie bliskie budynku UMWD (część modułu ``budynek3d``): posadzki granitowe Placu Mostowego,
podcienia, wnęk i opasek, ścieżki Ogrodu Województwa (cegła z wykopu), przebudowa trawnika kontekstu wokół
posadzek, drzewa zachowane w obszarze inwestycji i nowe nasadzenia, ława przy łuku, proste sylwetki ludzi.

Wymaga wyniku ``context.build_context`` w ``opts['kontekst']`` (teren NMT, trawnik z trawą 3D, prototypy drzew).
Bez kontekstu tworzy tylko płaskie posadzki na ±0,00.
"""
from __future__ import annotations

import json
import math
import time
import zlib

import numpy as np
import bpy
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.ops import unary_union

from umwd.render import blib
from umwd.render.budynek3d import Geo, SITE_JSON


# ============================================================================================== posadzki
def _z_posadzki(B, ctx, strefa0, brama):
    """Funkcja rzędnej posadzki (wzgl. ±0,00): teren + 0,03 m (nawierzchnie kontekstu pod posadzką są wycinane);
    przy budynku (≤ 2,5 m) nie wyżej niż ±0,00 (cokół odsłonięty tam, gdzie teren niższy); przy podcieniu i wnękach
    wejść (≤ 3,5 m) dokładnie ±0,00 (wejścia bez progów); przy bramie ogrodowej – posadzka bramy (−0,40)."""
    DZ = B.DZ
    foot = B.foot
    import shapely

    def zf(e, n):
        e = np.asarray(e, float)
        n = np.asarray(n, float)
        if ctx is None:
            return np.zeros_like(e)
        zt = ctx.teren.z(e, n) - DZ + 0.03
        pts = shapely.points(np.c_[e, n])
        d = shapely.distance(pts, foot)
        w = np.clip(1.0 - d / 2.5, 0.0, 1.0)
        z = zt + (np.minimum(zt, 0.0) - zt) * w
        d0 = shapely.distance(pts, strefa0)
        w0 = np.clip(1.0 - d0 / 3.5, 0.0, 1.0) ** 1.3
        z = z + (0.0 - z) * w0
        db = shapely.distance(pts, brama)
        wb = np.clip(1.0 - db / 3.0, 0.0, 1.0)
        z = z + (-0.40 - z) * wb
        z = np.where(shapely.contains(strefa0, pts), 0.0, z)
        return z
    return zf


def zagospodarowanie(B):
    t0 = time.time()
    kon = B.o.get('kontekst')
    ctx = kon['ctx'] if kon else None
    site = ctx.site if ctx is not None else json.load(open(SITE_JSON, encoding='utf-8'))
    sp = B.spec
    coll = B.kol['zagospodarowanie_bliskie']
    inw = Polygon(site['granice']['obszar_inwestycji']['pts']).buffer(0)
    skwer = Polygon(site['granice']['teren_uzyczony_dz_9_2']['pts']).buffer(0)
    foot = B.foot
    strefa0 = unary_union([sp.podcien.buffer(0.02)] + [w.buffer(0.02) for w in B.wneki_polys])
    brama = sp.brama
    # --- pola posadzek
    opaska = inw.intersection(foot.buffer(2.6, join_style=2)).difference(foot)
    # pas 4,6 m między segmentem a dz. 10/2 (wejście do ogrodu od bulwaru) – w obszarze inwestycji
    pas_seg = inw.intersection(B.poly['S'].buffer(5.2, join_style=2)).difference(foot)
    pas_seg = pas_seg.intersection(Polygon([sp.z_uv(u, v) for u, v in ((18.0, -16.0), (44.0, -16.0), (44.0, -6.0),
                                                                          (18.0, -6.0))]))
    front = None
    if ctx is not None and getattr(ctx, 'jezdnie_poly', None) is not None:
        # chodnik przy elewacjach frontowych (bez pasa trawy między chodnikiem a budynkiem)
        front = foot.buffer(3.0, join_style=2).intersection(ctx.ramka).difference(ctx.jezdnie_poly.buffer(0.45))
        front = front.difference(foot)
    plac = unary_union([skwer.difference(foot), opaska, pas_seg] + ([front] if front is not None else [])).buffer(0)
    plac = unary_union([plac, strefa0])
    if ctx is not None and getattr(ctx, 'jezdnie_poly', None) is not None:
        plac = plac.difference(ctx.jezdnie_poly.buffer(0.3))
    # ścieżki ogrodu (cegła z wykopu): brama ogrodowa → wejście ogrodowe wieży → pas od bulwaru
    bc = brama.centroid
    ogr_d = sp.z_uv(10.0, -1.5)
    pas_c = sp.z_uv(30.0, -13.5)
    pk = [sp.do_uv(*brama.exterior.coords[i]) for i in range(4)]
    wyj_brama = sp.z_uv(max(c[0] for c in pk) + 2.2, sum(c[1] for c in pk) / 4)
    sciezki = unary_union([
        LineString([wyj_brama, sp.z_uv(-2.0, -9.0), sp.z_uv(6.0, -6.0), ogr_d]).buffer(1.2, cap_style=1),
        LineString([ogr_d, sp.z_uv(16.0, -9.0), pas_c, sp.z_uv(44.0, -14.0)]).buffer(1.2, cap_style=1),
    ]).intersection(inw).difference(foot).difference(plac.buffer(-0.05))
    # ogródki (zachowane, 29 drzew) – ścieżki je omijają
    try:
        ogr = Polygon(site['granice']['ogrodki_przydomowe']['pts']).buffer(0)
        sciezki = sciezki.difference(ogr.buffer(0.3))
    except Exception:
        ogr = None
    zf = _z_posadzki(B, ctx, strefa0, brama)
    Gp = Geo()
    from umwd.render.context import siatka_drapowana
    for geom, mat, dz in ((plac, 'bruk', 0.0), (sciezki, 'cegla', -0.03)):
        if geom.is_empty:
            continue
        V, F = siatka_drapowana(geom, lambda e, n, dz=dz: zf(e, n) + dz, cell=1.0, skirt=0.35)
        for f in F:
            pts = [V[i] for i in f]
            Gp.face(pts, [(p[0], p[1]) for p in pts], mat)
    Gp.obiekt('posadzki', coll, B.mat, B.DZ)
    B.info['posadzki_m2'] = {'plac_i_opaski': round(plac.area, 1), 'sciezki': round(sciezki.area, 1)}
    # --- przebudowa trawnika kontekstu (bez trawy pod posadzkami i budynkiem)
    if ctx is not None:
        _przebuduj_trawnik(B, ctx, kon, unary_union([plac, sciezki, foot, brama]), plac)
    # --- drzewa
    if ctx is not None:
        _drzewa(B, ctx, coll, foot, skwer, plac)
    # --- ława okrągła przy łuku i ławy w pasie od bulwaru
    G = Geo()
    c = sp.z_uv(22.0, 35.6)
    ring = Point(*c).buffer(2.4, 64).difference(Point(*c).buffer(1.85, 64))
    zc = float(zf([c[0]], [c[1]])[0])
    G.pryzma(ring, zc - 0.3, zc + 0.45, 'granit')
    for f in (0.50, 0.68):
        p0, p1 = _pas_segmentu(B, f, 2.7), _pas_segmentu(B, f + 0.14, 2.7)
        q = LineString([p0, p1]).buffer(0.25, cap_style=2)
        zq = float(zf([q.centroid.x], [q.centroid.y])[0])
        G.pryzma(q, zq - 0.3, zq + 0.45, 'granit')
    G.obiekt('lawy', coll, B.mat, B.DZ)
    # --- pnącza (winobluszcz na linkach) na ścianie pd. segmentu
    pnacza(B, coll)
    # --- ludzie
    if B.o.get('ludzie'):
        ludzie(B, ctx, coll, plac, zf)
    B.czas('zagospodarowanie', t0)


def _przebuduj_trawnik(B, ctx, kon, wyciecie, plac):
    """Przebudowuje nawierzchnie kontekstu (trawniki z trawą 3D, chodniki, schody) bez obszarów posadzek/budynku;
    usuwa krawężniki wewnątrz posadzek projektu (zostają krawędzie jezdni)."""
    from umwd.render.context import klasyfikacja_nawierzchni, siatka_drapowana, _SZER
    import bmesh
    t0 = time.time()
    kl = klasyfikacja_nawierzchni(ctx)
    B._kl_cache = kl
    wyc = wyciecie.buffer(0.05)
    for klasa, g0 in kl.items():
        if klasa.startswith('jezdnia') or klasa == 'skarpa':
            continue
        nm = 'teren_' + klasa
        ob = bpy.data.objects.get(nm)
        if ob is None or not g0.intersects(wyc):
            continue
        mat, dz = _SZER.get(klasa, ('trawa', 0.03))
        g = g0.difference(wyc)
        V, F = siatka_drapowana(g, lambda e, n, dz=dz: ctx.teren.z(e, n) + dz, cell=1.5, skirt=0.25)
        if not len(F):
            ob.hide_render = True
            continue
        tmp = blib.mesh_from_arrays(nm + '_nowy', V, F, mats=list(ob.data.materials), coll=None)
        stary = ob.data
        ob.data = tmp.data
        bpy.data.objects.remove(tmp)
        if stary.users == 0:
            bpy.data.meshes.remove(stary)
    kr = bpy.data.objects.get('kraweznik')
    if kr is not None:
        import shapely
        wew = plac.buffer(-0.25)
        bm = bmesh.new()
        bm.from_mesh(kr.data)
        usun = []
        cs = np.array([f.calc_center_median()[:2] for f in bm.faces])
        if len(cs):
            ins = shapely.contains(wew, shapely.points(cs))
            usun = [f for f, i in zip(bm.faces, ins) if i]
        if usun:
            bmesh.ops.delete(bm, geom=usun, context='FACES')
            bm.to_mesh(kr.data)
        bm.free()
    B.info['czasy_s']['nawierzchnie_przebudowa'] = round(time.time() - t0, 1)


def pnacza(B, coll, rozstaw=2.9, seed=7):
    """Winobluszcz na linkach ze stali nierdzewnej co 1,45 m na ścianie pd. segmentu (rysunek elewacji S-S):
    wysokość 9–17 m, liście jako małe czworokąty w zwężającym się pasie wokół linki; jesienią czerwone."""
    rng = np.random.default_rng(seed)
    S = B.obrys['S']
    best = None
    for i in range(len(S)):
        a, b = np.array(S[i]), np.array(S[(i + 1) % len(S)])
        d = b - a
        L = float(np.hypot(*d))
        nrm = np.array([d[1], -d[0]]) / L
        if nrm[1] < -0.8 and (best is None or L > best[2]):
            best = (a, d / L, L, nrm)
    a, t, L, nrm = best
    G = Geo()
    up = np.array([0.0, 0.0, 1.0])
    n_l = 0
    for q in range(int((L - 0.8) / rozstaw) + 1):
        sq = 0.8 + q * rozstaw
        if sq > L - 0.5:
            break
        h = 5.5 + 6.0 * abs(math.sin(q * 1.3 + 0.4))     # młode nasadzenia (kilka sezonów)
        base = a + t * sq + nrm * 0.10
        # linka
        p0 = np.array([*(base + nrm * 0.02), 0.6])
        G.face([p0 - np.array([*t * 0.004, 0]), p0 + np.array([*t * 0.004, 0]),
                p0 + np.array([*t * 0.004, h - 0.6]), p0 - np.array([*t * 0.004, 0]) + np.array([0, 0, h - 0.6])],
               [(0, 0)] * 4, 'metal')
        nl = int(h * 48)
        for _ in range(nl):
            zz = rng.uniform(0.4, h) ** 1.0
            taper = 1.0 - (zz / (h + 2.0)) * 0.6
            off = rng.normal(0, 0.32 * taper)
            c = base + t * off + nrm * rng.uniform(0.0, 0.22)
            sz = rng.uniform(0.05, 0.09)
            ang = rng.uniform(0, 2 * math.pi)
            u = t * math.cos(ang) * sz
            v = np.array([*(-t * math.sin(ang) * sz * 0.3 + nrm * rng.uniform(-0.3, 0.3) * sz), 0.0]) + up * math.sin(ang + 1.2) * sz
            uu = np.array([*u, math.cos(ang) * sz * 0.2])
            cc = np.array([*c, zz])
            r = rng.random()
            G.face([cc - uu - v, cc + uu - v, cc + uu + v, cc - uu + v], [(r, 0)] * 4, 'pnacze')
            n_l += 1
    G.obiekt('pnacza_segment', coll, B.mat, B.DZ)
    B.info['pnacza_liscie'] = n_l


def _pas_segmentu(B, frac, odsuniecie):
    """Punkt w pasie 4,6 m między ścianą pd. segmentu a dz. 10/2: ułamek długości ściany i odsunięcie [m]."""
    S = B.obrys['S']
    # najdłuższa krawędź o normalnej na pd. = ściana pd.
    best = None
    for i in range(len(S)):
        a, b = np.array(S[i]), np.array(S[(i + 1) % len(S)])
        d = b - a
        L = float(np.hypot(*d))
        nrm = np.array([d[1], -d[0]]) / L
        if nrm[1] < -0.8 and (best is None or L > best[2]):
            best = (a, d, L, nrm)
    a, d, L, nrm = best
    p = a + d * frac + nrm * odsuniecie
    return (float(p[0]), float(p[1]))


_TYP_R = {'duze': 7.2, 'srednie': 4.8, 'male': 1.9, 'topola': 3.0, 'iglaste': 3.1}


def _drzewa(B, ctx, coll, foot, skwer, plac):
    """Drzewa zachowane w obszarze inwestycji (wg koncepcja.json – bez usuwanych) + nowe nasadzenia."""
    from umwd.render import context
    P = context._prototypy(ctx)
    sp = B.spec
    zag = sp.K['zagospodarowanie']
    usun = set(zag['drzewa_usuniete'])
    drz = {}
    for t in ctx.site['zielen']['drzewa']:
        drz.setdefault(t['nr'], []).append(t)
    n_zach = 0
    for nr, ts in drz.items():
        e = float(np.mean([t['e'] for t in ts]))
        n = float(np.mean([t['n'] for t in ts]))
        t = ts[0]
        if not (t['w_obszarze_inwestycji'] or ctx.inwest.contains(Point(e, n))):
            continue
        if nr in usun:
            continue
        d = foot.distance(Point(e, n))
        if d < 0.6:
            continue
        h = zlib.crc32(nr.encode()) % 1000 / 1000.0
        if t['typ'] == 'iglaste':
            typ, sk = 'iglaste', 0.75 + 0.35 * h
        else:
            typ, sk = ('srednie' if h > 0.35 else 'duze'), 0.7 + 0.35 * h
        # korona nie może wchodzić w elewację (w rzeczywistości cięcia pielęgnacyjne) – zmniejszenie
        R = _TYP_R[typ] * sk
        if d < R * 0.85:
            typ = 'srednie' if d > 2.5 else 'male'
            sk = min(sk, max(0.5, (d + 0.6) / (_TYP_R[typ] * 0.85)))
            if typ == 'male':
                sk = max(0.8, min(1.3, (d + 1.0) / 1.9))
        pr = P[typ][int(h * 97) % len(P[typ])][0]
        context._instancja(coll, pr, (e, n, ctx.teren.z1(e, n)), B.rng.uniform(0, 6.28), sk, 'drzewo_zach_' + nr)
        n_zach += 1
    # nowe: 4 lipy na Placu Mostowym (szpaler w zach. części), 2 w pasie od bulwaru, 6 w ogrodzie
    nowe = [sp.z_uv(u, 35.2) for u in (-3.0, 3.0, 9.0, 15.0)]
    nowe += [_pas_segmentu(B, 0.30, 3.0)]
    nowe += [sp.z_uv(u, v) for u, v in ((-12.0, -6.0), (-6.0, -13.0), (2.0, -16.0), (14.0, -18.0), (20.0, -6.5),
                                         (-14.0, -18.0))]
    n_now = 0
    for i, (e, n) in enumerate(nowe):
        pt = Point(e, n)
        if foot.buffer(1.5).contains(pt) or not ctx.ramka.contains(pt):
            continue
        typ = 'male' if i < 6 else ('srednie' if i % 2 else 'male')
        sk = 1.25 if i < 4 else (1.1 if typ == 'male' else 0.6)
        pr = P[typ][i % len(P[typ])][0]
        context._instancja(coll, pr, (e, n, ctx.teren.z1(e, n) + 0.1), B.rng.uniform(0, 6.28), sk, 'drzewo_nowe_%d' % i)
        n_now += 1
    B.info['drzewa'] = {'zachowane_w_OI': n_zach, 'nowe': n_now}


# ============================================================================================== ludzie
def _prototyp_czlowieka(nazwa, H=1.75, chod=0.0, plaszcz=0.36, kobieta=False, seed=0, torba=False):
    """Sylwetka człowieka w jesiennym okryciu, z metaballi (gładka bryła), skonwertowana do siatki.

    Proporcje wg kanonu 7,5 głowy; płaszcz/kurtka w kształcie litery A do wysokości ``plaszcz``·H (0,36 – płaszcz
    do kolan, 0,50 – kurtka do bioder), nogi widoczne poniżej, ręce przy tułowiu (lekki wymach w chodzie).
    Atrybut ``fv`` = wysokość / H (strefy materiału: buty, spodnie, okrycie, skóra, włosy)."""
    from mathutils import Quaternion, Vector
    rng = np.random.default_rng(seed)
    mb = bpy.data.metaballs.new(nazwa)
    mb.resolution = 0.018
    mb.render_resolution = 0.018
    mb.threshold = 0.6
    s = H / 1.75
    bark = 0.215 if not kobieta else 0.19

    def el(typ, co, r, sx=None, sy=None, sz=None, rot=None, stiff=2.0):
        e = mb.elements.new(type=typ)
        e.co = Vector(co) * 1.0
        e.radius = r
        e.stiffness = stiff
        if sx is not None:
            e.size_x = sx
        if sy is not None:
            e.size_y = sy
        if sz is not None:
            e.size_z = sz
        if rot is not None:
            e.rotation = rot
        return e

    def kapsula(a, b, r, stiff=2.0):
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        q = Vector((1, 0, 0)).rotation_difference(d.normalized())
        return el('CAPSULE', ((a + b) / 2)[:], r, sx=L / 2, rot=q, stiff=stiff)

    # nogi (biodro → kolano → kostka), krok w osi +y
    for side, sg in ((-1, 1), (1, -1)):
        a = chod * sg
        x = side * 0.085 * s
        biodro = Vector((x, 0, 0.90 * s))
        kolano = biodro + Vector((0, math.sin(a) * 0.44 * s, -math.cos(a) * 0.44 * s))
        b = a * (0.25 if sg > 0 else 1.5)
        kost = kolano + Vector((0, math.sin(b) * 0.41 * s, -math.cos(b) * 0.41 * s))
        kost.z = max(kost.z, 0.07 * s)
        kapsula(biodro, kolano, 0.078 * s)
        kapsula(kolano, kost, 0.058 * s)
        el('ELLIPSOID', (kost.x, kost.y + 0.055 * s, 0.045 * s), 0.065 * s, sx=0.65, sy=1.55, sz=0.62)
    # okrycie: elipsoidy od ramion do dołu płaszcza (A)
    z_dol = plaszcz * H
    poz = [(1.42, bark * 1.02, 0.115), (1.30, bark * 0.98, 0.125), (1.15, bark * 0.93, 0.125),
           (1.00, bark * 0.92, 0.13)]
    z = 1.00 * s
    while z - 0.12 * s > z_dol:
        z -= 0.13 * s
        poz.append((z / s, bark * (0.93 + 0.18 * (1.0 - z / s)), 0.135))
    for zz, rx, ry in poz:
        el('ELLIPSOID', (0, 0, zz * s), rx * s, sx=1.0, sy=ry / rx, sz=0.75, stiff=2.2)
    # szyja, głowa z włosami (lekko z tyłu)
    el('BALL', (0, 0.005 * s, 1.52 * s), 0.052 * s)
    el('ELLIPSOID', (0, 0.012 * s, 1.635 * s), 0.10 * s, sx=0.80, sy=0.95, sz=1.12)
    el('ELLIPSOID', (0, -0.012 * s, 1.67 * s), 0.10 * s, sx=0.86, sy=0.92, sz=0.85,
       stiff=1.6 if not kobieta else 1.9)
    if kobieta:
        el('ELLIPSOID', (0, -0.05 * s, 1.56 * s), 0.08 * s, sx=1.05, sy=0.6, sz=1.3, stiff=1.4)
    # ręce: ramię → łokieć → dłoń
    for side, sg in ((-1, -1), (1, 1)):
        a = chod * sg * 0.7
        ram = Vector((side * (bark + 0.02) * s, 0.0, 1.40 * s))
        lok = ram + Vector((side * 0.02 * s, math.sin(a) * 0.29 * s, -math.cos(a) * 0.29 * s))
        dl = lok + Vector((side * 0.005 * s, math.sin(a * 1.4 + 0.12) * 0.26 * s, -math.cos(a * 1.4 + 0.12) * 0.26 * s))
        kapsula(ram, lok, 0.058 * s)
        kapsula(lok, dl, 0.05 * s)
        el('BALL', (dl + Vector((0, 0, -0.04 * s)))[:], 0.045 * s)
    if torba:
        el('ELLIPSOID', ((bark + 0.06) * s, 0.04 * s, 0.98 * s), 0.12 * s, sx=0.45, sy=1.0, sz=0.9)
    ob = bpy.data.objects.new(nazwa + '_mb', mb)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    bpy.data.objects.remove(ob)
    bpy.data.metaballs.remove(mb)
    me.name = nazwa
    V = np.array([v.co[:] for v in me.vertices])
    if len(V):
        fv = V[:, 2] / H
        # strefy: okrycie zaczyna się na wysokości dołu płaszcza (atrybut 'fo' – próg okrycia)
        a = me.attributes.new('fv', 'FLOAT', 'POINT')
        a.data.foreach_set('value', fv.astype(np.float32))
        b = me.attributes.new('fu', 'FLOAT', 'POINT')
        b.data.foreach_set('value', np.full(len(V), plaszcz - 0.01, np.float32))
    for p in me.polygons:
        p.use_smooth = True
    return me


def ludzie(B, ctx, coll, plac, zf):
    """Sylwetki ludzi na chodnikach i posadzkach w pobliżu budynku (ruch wzdłuż elewacji, ku wejściom)."""
    t0 = time.time()
    rng = np.random.default_rng(B.o['seed'] + 101)
    mat = B.mat('ludzie')
    proto = []
    warianty = ((1.81, 0.32, 0.36, False, False), (1.67, 0.28, 0.40, True, True), (1.77, 0.0, 0.50, False, False),
                (1.64, 0.0, 0.36, True, False), (1.85, 0.30, 0.50, False, True), (1.70, 0.30, 0.34, True, False),
                (1.30, 0.30, 0.50, False, False), (1.73, 0.0, 0.38, True, True), (1.79, 0.26, 0.42, False, False),
                (1.62, 0.31, 0.46, True, False))
    for i, (H, chod, pl, kob, tb) in enumerate(warianty):
        me = _prototyp_czlowieka('czlowiek_%d' % i, H, chod, pl, kob, seed=i, torba=tb)
        me.materials.append(mat)
        proto.append((me, chod > 0))
    # strefy ruchu: chodniki kontekstu + posadzki projektu w promieniu 45 m od budynku
    strefy = [plac]
    if ctx is not None:
        from umwd.render.context import klasyfikacja_nawierzchni
        kl = getattr(B, '_kl_cache', None) or klasyfikacja_nawierzchni(ctx)
        B._kl_cache = kl
        for k, g in kl.items():
            if k.startswith('chodnik'):
                strefy.append(g)
    obszar = unary_union(strefy).intersection(B.foot.buffer(45.0)).difference(B.foot.buffer(0.9))
    # unikanie drzew i latarń
    przeszk = []
    for ob in bpy.data.objects:
        if ob.instance_type == 'COLLECTION' and (ob.name.startswith('drzewo') or ob.name.startswith('szpaler')):
            przeszk.append(Point(ob.location.x, ob.location.y).buffer(0.8))
        if ob.name.startswith('latarnia'):
            przeszk.append(Point(ob.location.x, ob.location.y).buffer(0.6))
    if przeszk:
        obszar = obszar.difference(unary_union(przeszk))
    if obszar.is_empty:
        return
    n_cel = B.o.get('ludzie_liczba', 34)
    x0, y0, x1, y1 = obszar.bounds
    poz = []
    proby = 0
    while len(poz) < n_cel and proby < 6000:
        proby += 1
        p = (rng.uniform(x0, x1), rng.uniform(y0, y1))
        if not obszar.contains(Point(p)):
            continue
        if any(math.dist(p, q) < 1.6 for q in poz):
            continue
        poz.append(p)
        # czasem para / grupa
        if rng.random() < 0.3:
            q = (p[0] + rng.uniform(-0.9, 0.9), p[1] + rng.uniform(-0.9, 0.9))
            if obszar.contains(Point(q)):
                poz.append(q)
    import shapely
    kraw = B.foot.boundary
    for i, p in enumerate(poz):
        me, idzie = proto[rng.integers(len(proto))]
        ob = bpy.data.objects.new('czlowiek_%02d' % i, me)
        coll.objects.link(ob)
        z = float(zf([p[0]], [p[1]])[0]) if plac.contains(Point(p)) else (
            float(ctx.teren.z1(p[0], p[1]) - B.DZ + 0.06) if ctx is not None else 0.0)
        ob.location = (p[0], p[1], z + B.DZ)
        # kierunek: równolegle do najbliższej krawędzi budynku (ruch wzdłuż elewacji) ± losowo
        d = kraw.project(Point(p))
        a = kraw.interpolate(d)
        b2 = kraw.interpolate(min(kraw.length, d + 0.5))
        kier = math.atan2(b2.y - a.y, b2.x - a.x)
        if rng.random() < 0.5:
            kier += math.pi
        kier += rng.normal(0, 0.35)
        ob.rotation_euler = (0, 0, kier - math.pi / 2)
    B.info['ludzie'] = len(poz)
    B.info['czasy_s']['ludzie'] = round(time.time() - t0, 1)
