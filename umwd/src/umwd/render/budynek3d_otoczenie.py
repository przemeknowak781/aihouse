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


# ============================================================================================== plan zagospodarowania
# Położenia elementów jak na planszy zagospodarowania (tools/zagospodarowanie.py) – 3D zgodne z rysunkiem.
PLAN = dict(
    # wg tools/zagospodarowanie.py (v1.1, 17.11) – geometria planszy zagospodarowania
    slad_1934=[(63.4, 79.6), (75.0, 81.0), (86.0, 81.9), (93.5, 81.6), (98.6, 79.6)],   # ślad pierzei z 1934 r.
    lawa_okragla=((105.54, 75.73), 2.2),          # R 16,5 m od środka łuku – poza podcieniem (korekta 17.11)
    lipy=[(66.0, 79.4), (71.5, 80.3), (77.0, 81.0), (82.5, 81.6)],                       # szpaler 4 lip
    drzewa_pas=[(95.9, 35.6), (88.75, 35.5)],                                            # u wylotu pasa od bulwaru
    drzewa_ogrod=[(87.25, 31.25), (94.75, 29.75), (87.5, 26.75), (86.5, 19.25), (95.25, 17.25), (91.25, 15.0),
                  (94.75, 7.75), (90.0, 3.75), (94.75, -0.25), (88.75, -5.75), (75.75, -6.25), (71.1, -6.2),
                  (80.75, 35.25), (71.5, 33.0)],                                         # 14 w ogrodzie (v1.1)
    lawa_pas=[(98.5, 38.0), (104.0, 38.3), (104.0, 38.9), (98.5, 38.6)],
    ogrod_deszczowy=[[(87.14, 17.46), (87.26, 17.98), (87.71, 18.26), (89.6, 17.93), (91.16, 18.24), (92.2, 18.85),
                      (93.18, 19.95), (94.38, 20.8), (94.92, 20.86), (95.36, 20.49), (96.14, 0.63), (95.85, 0.04),
                      (90.93, 0.01), (90.59, 0.28), (90.4, 2.12), (89.97, 3.81), (91.56, 5.43), (92.48, 6.97),
                      (92.93, 8.76), (92.84, 10.57), (92.22, 12.28), (91.13, 13.75), (89.67, 14.82), (87.47, 15.68)],
                     [(89.0, 32.75), (89.21, 31.47), (89.58, 30.57), (90.12, 29.98), (90.98, 29.52), (91.77, 29.4),
                      (92.73, 29.59), (94.22, 30.68), (94.94, 30.4), (95.29, 24.04), (94.98, 23.44), (94.21, 23.43),
                      (93.18, 24.11), (92.2, 25.21), (91.16, 25.82), (89.99, 26.11), (88.05, 26.03), (87.21, 27.13),
                      (87.1, 28.24), (87.36, 29.73), (87.12, 31.2), (87.23, 32.54), (87.67, 32.96), (88.55, 32.99)]],
    plac_zabaw=[(90.6, -6.0), (96.3, -5.8), (96.3, -0.6), (90.6, -0.6)],
    pergola=None,                                      # brak w v1.1
    sciezki=[[(86.4, 38.6), (85.9, 31.0), (85.9, 24.0), (84.2, 19.5), (83.9, 14.0), (83.7, 9.0), (86.2, 4.0),
              (86.9, -1.0), (85.8, -4.7), (79.7, -4.75), (75.9, -4.2), (70.4, -3.4)],
             [(86.9, -1.0), (90.6, -2.6)],
             [(66.95, 20.3), (70.15, 34.6)],
             [(97.6, 36.9), (95.6, 37.6), (95.2, 40.6)]],
    sciezki_szer=1.8,
    # taras ogrodowy na stropie pasa −1 i zadaszenie BIPV wzdłuż elewacji pd. wieży (układ wieży u, v; v < 0 – ogród)
    taras_uv=(-3.90, -5.0, 21.0, 0.0),
    zadaszenie_uv=(0.5, -4.0, 20.5, 0.0), zadaszenie_h=4.0,
    drzewa_rzeka_n=(16.0, 24.0, 32.0, 40.0, 48.0, 56.0),   # 6 drzew na chodniku od rzeki (1,4 m od krawężnika)
)


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
    # taras ogrodowy (strop pasa −1) – posadzka granitowa jak plac
    sp_ = B.spec
    u0, v0, u1, v1 = PLAN['taras_uv']
    taras = Polygon([sp_.z_uv(u0, v0), sp_.z_uv(u1, v0), sp_.z_uv(u1, v1), sp_.z_uv(u0, v1)]).buffer(0)
    taras = taras.intersection(inw).difference(foot)
    plac = unary_union([plac, taras])
    # ścieżki ogrodu (cegła z wykopu) wg planszy zagospodarowania
    ogrod_poly = inw.difference(foot)
    sciezki = unary_union([LineString(l).buffer(PLAN['sciezki_szer'] / 2, cap_style=2) for l in PLAN['sciezki']])
    sciezki = sciezki.intersection(ogrod_poly).difference(plac.buffer(-0.05))
    # ogródki (zachowane, 29 drzew) – ścieżki je omijają
    try:
        ogr = Polygon(site['granice']['ogrodki_przydomowe']['pts']).buffer(0)
        sciezki = sciezki.difference(ogr.buffer(0.1))
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
        deszcz = unary_union([Polygon(r) for r in PLAN['ogrod_deszczowy']]).intersection(inw).difference(foot)
        zabawa = Polygon(PLAN['plac_zabaw']).intersection(inw).difference(foot)
        _przebuduj_trawnik(B, ctx, kon, unary_union([plac, sciezki, foot, brama, deszcz, zabawa]), plac)
        _ogrod(B, ctx, coll, deszcz, zabawa, zf)
    # --- drzewa
    if ctx is not None:
        _drzewa(B, ctx, coll, foot, skwer, plac)
    # --- ława okrągła przy łuku, ława w pasie od bulwaru, ślad pierzei 1934, stojaki rowerowe
    G = Geo()
    c, rr = PLAN['lawa_okragla']
    c = _lawa_poza_lukiem(B, ctx, c, rr)
    ring = Point(*c).buffer(rr, 64).difference(Point(*c).buffer(rr - 0.5, 64))
    zc = float(zf([c[0]], [c[1]])[0])
    G.pryzma(ring, zc - 0.3, zc + 0.45, 'granit')
    G.pryzma(Point(*c).buffer(rr - 0.5, 48), zc - 0.2, zc + 0.02, 'sedum')
    q = Polygon(PLAN['lawa_pas'])
    zq = float(zf([q.centroid.x], [q.centroid.y])[0])
    G.pryzma(q, zq - 0.3, zq + 0.45, 'granit')
    _slad_1934(B, G, zf)
    _stojaki(B, G, zf)
    _zadaszenie_bipv(B, coll, zf)
    if B.o.get('ludzie'):
        wozek(B, coll, zf)
    G.obiekt('lawy_slad1934_stojaki', coll, B.mat, B.DZ)
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


def _lawa_poza_lukiem(B, ctx, c, rr):
    """Ława okrągła z planszy leży w pierścieniu podcienia (R 11–14) – przesunięcie promieniowe poza lico łuku
    (R 14 + 0,3 m + promień ławy), a gdy wchodzi w jezdnię – obrót wokół środka łuku w stronę placu."""
    cx, cy = B.spec.luk['srodek']
    R = B.spec.luk['R_zewn']
    v = np.array(c) - np.array([cx, cy])
    a0 = math.atan2(v[1], v[0])
    rad = R + 0.3 + rr
    jezd = getattr(ctx, 'jezdnie_poly', None) if ctx is not None else None
    for da in np.radians(np.arange(0, 60, 3)):
        p = (cx + rad * math.cos(a0 + da), cy + rad * math.sin(a0 + da))
        if jezd is None or not Point(*p).buffer(rr + 0.3).intersects(jezd):
            return p
    return (cx + rad * math.cos(a0), cy + rad * math.sin(a0))


def _drzewa_rzeka(ctx):
    """6 drzew na chodniku od rzeki (Wybrzeże): 1,4 m za krawężnikiem wsch. (jak w tools/zagospodarowanie.py)."""
    U = ctx.site['ulice_i_sytuacja']
    kr = unary_union([LineString(it['pts']) for it in U['krawezniki'] if len(it.get('pts', [])) >= 2])
    out = []
    for nn in PLAN['drzewa_rzeka_n']:
        x = kr.intersection(LineString([(123.5, nn), (131.6, nn)]))
        if not x.is_empty:
            out.append((x.bounds[2] + 1.4, nn))
    return out


def _slad_1934(B, G, zf, szer=0.60, listwa=0.06):  # noqa: C901
    """Ślad pierzei z 1934 r. w posadzce Placu Mostowego: pas ciemniejszego granitu 0,60 m z listwą z brązu
    w osi i tablicą z planem kwartału (brąz) na zach. końcu."""
    L = LineString(PLAN['slad_1934'])
    pas = L.buffer(szer / 2, cap_style=2, join_style=2).difference(B.foot)
    lis = L.buffer(listwa / 2, cap_style=2, join_style=2).difference(B.foot)
    from umwd.render.context import siatka_drapowana
    for geom, mat, dz in ((pas.difference(lis), 'granit:ciemny', 0.004), (lis, 'litery', 0.006)):
        V, F = siatka_drapowana(geom, lambda e, n, dz=dz: zf(e, n) + dz, cell=0.5, skirt=0.02)
        for f in F:
            pts = [V[i] for i in f]
            G.face(pts, [(p[0], p[1]) for p in pts], mat)
    p0, p1 = np.array(PLAN['slad_1934'][0]), np.array(PLAN['slad_1934'][1])
    t = (p1 - p0) / np.linalg.norm(p1 - p0)
    nrm = np.array([-t[1], t[0]])
    c = p0 + t * 1.6 + nrm * 1.0
    tab = Polygon([c - t * 0.6 - nrm * 0.4, c + t * 0.6 - nrm * 0.4, c + t * 0.6 + nrm * 0.4, c - t * 0.6 + nrm * 0.4])
    zt = float(zf([c[0]], [c[1]])[0])
    G.pryzma(tab, zt - 0.05, zt + 0.008, 'litery')


def _stojaki(B, G, zf, n=10, rozstaw=1.0, h=0.85, szer=0.70, rura=0.05):
    """Stojaki rowerowe (U, stal nierdzewna → metal) dla gości: 10 szt. (20 rowerów) na Placu Mostowym, równolegle
    do elewacji pn. wieży, 2,8 m od lica (rząd przy zach. części placu)."""
    sp = B.spec
    for k in range(n):
        u = 1.2 + k * rozstaw
        a = np.array(sp.z_uv(u, 29.7 + 2.8 - szer / 2))
        b = np.array(sp.z_uv(u, 29.7 + 2.8 + szer / 2))
        z0 = float(zf([a[0]], [a[1]])[0])
        for p in (a, b):
            G.pryzma(Point(*p).buffer(rura / 2, 8), z0 - 0.2, z0 + h, 'metal')
        lin = LineString([a, b]).buffer(rura / 2, cap_style=2)
        G.pryzma(lin, z0 + h - rura, z0 + h, 'metal')


def _zadaszenie_bipv(B, coll, zf):
    """Zadaszenie BIPV tarasu ogrodowego wzdłuż elewacji pd. wieży (u 0,5–20,5, głęb. 4,0 m, h ≈ 4,0 m; 80 m², 13 kWp):
    słupy stalowe Ø 0,16 m co 4 m przy krawędzi ogrodowej, belka krawędziowa i belki poprzeczne do elewacji (grafit),
    moduły szkło-szkło z ogniwami (prześwit między ogniwami – cień ażurowy na tarasie)."""
    sp = B.spec
    u0, v0, u1, v1 = PLAN['zadaszenie_uv']
    h = PLAN['zadaszenie_h']
    G = Geo()
    Gs = Geo()
    z0 = float(zf([sp.z_uv((u0 + u1) / 2, v0)[0]], [sp.z_uv((u0 + u1) / 2, v0)[1]])[0])
    n = int(round((u1 - u0) / 4.0))
    for i in range(n + 1):
        u = u0 + (u1 - u0) * i / n
        e, nn = sp.z_uv(u, v0 + 0.15)
        G.pryzma(Point(e, nn).buffer(0.08, 12), z0, z0 + h - 0.22, 'metal')
        # belka poprzeczna (do elewacji)
        a, b = sp.z_uv(u, v0 + 0.05), sp.z_uv(u, v1 - 0.02)
        G.pryzma(LineString([a, b]).buffer(0.06, cap_style=2), z0 + h - 0.22, z0 + h - 0.04, 'metal')
    # belka krawędziowa
    a, b = sp.z_uv(u0 - 0.1, v0 + 0.15), sp.z_uv(u1 + 0.1, v0 + 0.15)
    G.pryzma(LineString([a, b]).buffer(0.09, cap_style=2), z0 + h - 0.26, z0 + h - 0.02, 'metal')
    # moduły (1,0 × 1,6 m) – szkło z ogniwami
    nu = int((u1 - u0) / 1.0)
    for i in range(nu):
        for j in range(2):
            ua, ub = u0 + i * 1.0 + 0.01, u0 + (i + 1) * 1.0 - 0.01
            va, vb = v0 + 0.25 + j * 1.85, v0 + 0.25 + (j + 1) * 1.85 - 0.02
            pts = [(*sp.z_uv(ua, va), z0 + h), (*sp.z_uv(ub, va), z0 + h), (*sp.z_uv(ub, vb), z0 + h), (*sp.z_uv(ua, vb), z0 + h)]
            Gs.face(pts, [(ua, va), (ub, va), (ub, vb), (ua, vb)], 'bipv_szklo')
    G.obiekt('zadaszenie_bipv_konstrukcja', coll, B.mat, B.DZ)
    Gs.obiekt('zadaszenie_bipv_moduly', coll, B.mat, B.DZ)
    B.info['zadaszenie_bipv'] = dict(u=(u0, u1), glebokosc=round(v1 - v0, 2), h=h, moduly=nu * 2)


def _ogrod(B, ctx, coll, deszcz, zabawa, zf):
    """Ogród deszczowy (niecka −0,25 m z roślinnością wilgociolubną i kamieniami na brzegu), plac zabaw (piasek,
    drewniana konstrukcja), pergola przy murze kamienic."""
    from umwd.render import context
    G = Geo()
    if not deszcz.is_empty:
        z = lambda e, n: ctx.teren.z(e, n) - B.DZ
        from umwd.render.context import siatka_drapowana
        V, F = siatka_drapowana(deszcz.buffer(-0.4), lambda e, n: z(e, n) - 0.22, cell=1.0, skirt=0.25)
        for f in F:
            pts = [V[i] for i in f]
            G.face(pts, [(p[0], p[1]) for p in pts], 'ogrod_deszczowy')
        V, F = siatka_drapowana(deszcz.difference(deszcz.buffer(-0.4)), lambda e, n: z(e, n) - 0.05, cell=0.5,
                                skirt=0.25)
        for f in F:
            pts = [V[i] for i in f]
            G.face(pts, [(p[0], p[1]) for p in pts], 'zwir')
        # kępy traw i bylin (prototypy krzewów kontekstu, małe)
        P = context._prototypy(ctx)
        x0, y0, x1, y1 = deszcz.bounds
        rng = np.random.default_rng(31)
        for i in range(70):
            q = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
            if not deszcz.buffer(-0.6).contains(q):
                continue
            pr = P['krzew'][i % len(P['krzew'])][0]
            context._instancja(coll, pr, (q.x, q.y, ctx.teren.z1(q.x, q.y) - 0.2), rng.uniform(0, 6.28),
                               rng.uniform(0.25, 0.45), 'deszczowy_%d' % i)
    if not zabawa.is_empty:
        zc = zabawa.centroid
        z0 = float(ctx.teren.z1(zc.x, zc.y) - B.DZ)
        G.pryzma(zabawa, z0 - 0.3, z0 + 0.04, 'piasek')
        # drewniana konstrukcja: 4 słupy, podest, daszek
        c = np.array([zc.x, zc.y])
        for dx, dy in ((-1.0, -0.8), (1.0, -0.8), (1.0, 0.8), (-1.0, 0.8)):
            G.pryzma(Point(*(c + [dx, dy])).buffer(0.07, 6), z0, z0 + 2.4, 'wn_drewno:jasne')
        G.pryzma(Point(*c).buffer(1.15, 4), z0 + 1.0, z0 + 1.08, 'wn_drewno:jasne')
        G.pryzma(Point(*c).buffer(1.25, 4), z0 + 2.4, z0 + 2.48, 'wn_drewno:jasne')
    if not PLAN.get('pergola'):
        G.obiekt('ogrod_deszczowy_plac_zabaw', coll, B.mat, B.DZ)
        return
    x, y0, krok, n = PLAN['pergola']
    zp = float(ctx.teren.z1(x, y0 + krok * n / 2) - B.DZ)
    for k in range(n):
        G.pryzma(Point(x, y0 + k * krok).buffer(0.08, 4), zp - 0.3, zp + 2.6, 'wn_drewno')
    G.pryzma(LineString([(x, y0 - 0.3), (x, y0 + krok * (n - 1) + 0.3)]).buffer(0.08, cap_style=2), zp + 2.6,
             zp + 2.78, 'wn_drewno')
    for k in range(int(krok * (n - 1) / 0.6) + 1):
        yy = y0 + k * 0.6
        G.pryzma(LineString([(x - 1.2, yy), (x + 0.3, yy)]).buffer(0.03, cap_style=2), zp + 2.78, zp + 2.86, 'wn_drewno')
    G.obiekt('ogrod_deszczowy_plac_zabaw', coll, B.mat, B.DZ)


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
    # nowe (plansza zagospodarowania): 4 lipy wzdłuż śladu 1934, 2 w pasie od bulwaru, 6 w ogrodzie, 6 przy rzece
    nowe = list(PLAN['lipy']) + list(PLAN['drzewa_pas']) + list(PLAN['drzewa_ogrod']) + _drzewa_rzeka(ctx)
    n_now = 0
    for i, (e, n) in enumerate(nowe):
        pt = Point(e, n)
        if foot.buffer(1.5).contains(pt) or not ctx.ramka.contains(pt):
            continue
        typ = 'male' if (i < 6 or i >= 12) else ('srednie' if i % 2 else 'male')
        sk = 1.25 if i < 4 else (1.1 if typ == 'male' else 0.6)
        pr = P[typ][i % len(P[typ])][0]
        context._instancja(coll, pr, (e, n, ctx.teren.z1(e, n) + 0.1), B.rng.uniform(0, 6.28), sk, 'drzewo_nowe_%d' % i)
        n_now += 1
    B.info['drzewa'] = {'zachowane_w_OI': n_zach, 'nowe': n_now}


# ============================================================================================== ludzie
def _prototyp_czlowieka(nazwa, H=1.75, chod=0.0, plaszcz=0.36, kobieta=False, seed=0, torba=False, poza=''):
    """Sylwetka człowieka w jesiennym okryciu, z metaballi (gładka bryła), skonwertowana do siatki.

    Proporcje wg kanonu 7,5 głowy; płaszcz/kurtka w kształcie litery A do wysokości ``plaszcz``·H (0,36 – płaszcz
    do kolan, 0,50 – kurtka do bioder), nogi widoczne poniżej, ręce przy tułowiu (lekki wymach w chodzie).
    Atrybut ``fv`` = wysokość / H (strefy materiału: buty, spodnie, okrycie, skóra, włosy), ``sk`` = 1 dla dłoni
    (skóra). ``poza``: '' (ręce wzdłuż tułowia), 'telefon' (prawe przedramię uniesione – telefon/ulotka),
    'kieszen' (lewa dłoń w kieszeni – łokieć odwiedziony), 'oba' (obie)."""
    from mathutils import Quaternion, Vector
    dlonie = []
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
        if side > 0 and poza in ('telefon', 'oba'):
            # przedramię uniesione przed tułów, dłoń na wys. ~1,15 H
            lok = ram + Vector((side * 0.05 * s, 0.06 * s, -0.27 * s))
            dl = lok + Vector((-side * 0.10 * s, 0.20 * s, 0.10 * s))
        if side < 0 and poza in ('kieszen', 'oba'):
            # dłoń w kieszeni płaszcza: łokieć odwiedziony, dłoń przy biodrze (schowana w okryciu)
            lok = ram + Vector((side * 0.055 * s, -0.04 * s, -0.28 * s))
            dl = Vector((side * (bark - 0.01) * s, 0.05 * s, 0.99 * s))
        kapsula(ram, lok, 0.058 * s)
        kapsula(lok, dl, 0.05 * s)
        pd = dl + Vector((0, 0, -0.04 * s)) if not (side > 0 and poza in ('telefon', 'oba')) else dl + Vector((0, 0.02 * s, 0))
        el('BALL', pd[:], 0.045 * s)
        if not (side < 0 and poza in ('kieszen', 'oba')):
            dlonie.append((np.array(pd[:]), 0.075 * s))
        if side > 0 and poza in ('telefon', 'oba'):
            el('ELLIPSOID', (pd + Vector((0, 0.03 * s, 0.03 * s)))[:], 0.05 * s, sx=0.5, sy=0.18, sz=1.0, stiff=3.0)
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
        sk = np.zeros(len(V), np.float32)
        for c, r in dlonie:
            sk = np.maximum(sk, (np.linalg.norm(V - c, axis=1) < r).astype(np.float32))
        c_ = me.attributes.new('sk', 'FLOAT', 'POINT')
        c_.data.foreach_set('value', sk)
        # włosy: tył głowy powyżej karku (z przodu twarz)
        wl = ((V[:, 2] > 1.56 * s) & (V[:, 1] < 0.0)).astype(np.float32)
        d_ = me.attributes.new('wl', 'FLOAT', 'POINT')
        d_.data.foreach_set('value', wl)
    for p in me.polygons:
        p.use_smooth = True
    return me


def _krzywe(action):
    """F-krzywe akcji (bpy 5.x: warstwy/kanały; starsze: action.fcurves)."""
    if hasattr(action, 'fcurves') and action.fcurves:
        return list(action.fcurves)
    out = []
    for lay in getattr(action, 'layers', []):
        for st in lay.strips:
            for cb in getattr(st, 'channelbags', []):
                out += list(cb.fcurves)
    return out


def _torus(R, r, n=40, m=8):
    """Torus w płaszczyźnie XZ (oś obrotu Y) – koło wózka. Zwraca (V, F)."""
    V, F = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        for j in range(m):
            b = 2 * math.pi * j / m
            rr = R + r * math.cos(b)
            V.append((rr * math.cos(a), r * math.sin(b), rr * math.sin(a)))
    for i in range(n):
        for j in range(m):
            a, b2 = i * m + j, ((i + 1) % n) * m + j
            F.append((a, b2, ((i + 1) % n) * m + (j + 1) % m, i * m + (j + 1) % m))
    return V, F


def _rura(G, a, b, r, mat, n=6):
    """Rura (graniastosłup n-kątny) między punktami 3D a i b."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    if L < 1e-6:
        return
    d /= L
    t = np.cross(d, [0, 0, 1.0]) if abs(d[2]) < 0.95 else np.cross(d, [1.0, 0, 0])
    t /= np.linalg.norm(t)
    w = np.cross(d, t)
    ring = [t * math.cos(2 * math.pi * i / n) * r + w * math.sin(2 * math.pi * i / n) * r for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        G.face([tuple(a + ring[i]), tuple(a + ring[j]), tuple(b + ring[j]), tuple(b + ring[i])], [(0, 0)] * 4, mat)


def _petla(G, pierscienie, mat):
    """Powierzchnia z pierścieni o tej samej liczbie punktów (zamknięta w obwodzie) + wieka."""
    for r0, r1 in zip(pierscienie[:-1], pierscienie[1:]):
        n = len(r0)
        for i in range(n):
            j = (i + 1) % n
            G.face([r0[i], r0[j], r1[j], r1[i]], [(0, 0)] * 4, mat)
    G.face(pierscienie[0][::-1], [(0, 0)] * len(pierscienie[0]), mat)
    G.face(pierscienie[-1], [(0, 0)] * len(pierscienie[-1]), mat)


def _pierscien(dl, sz, z, r, dx=0.0, n_luk=4):
    """Zaokrąglony prostokąt (długość wzdłuż x, szerokość wzdłuż y) na wysokości z, środek w (dx, 0)."""
    pts = []
    r = min(r, dl / 2 - 1e-3, sz / 2 - 1e-3)
    for cx, cy, a0 in ((dl / 2 - r, sz / 2 - r, 0), (-dl / 2 + r, sz / 2 - r, 90), (-dl / 2 + r, -sz / 2 + r, 180),
                       (dl / 2 - r, -sz / 2 + r, 270)):
        for k in range(n_luk + 1):
            a = math.radians(a0 + 90 * k / n_luk)
            pts.append((dx + cx + r * math.cos(a), cy + r * math.sin(a), z))
    return pts


def samochod(B, coll, poz, kier, z, nazwa='auto', seed=0):
    """Samochód osobowy (kompakt/sedan ~4,4 × 1,8 × 1,47 m): nadwozie i kabina z pierścieni zaokrąglonych
    prostokątów (lakier, szyby), koła z oponami i felgami, światła. Lokalnie przód +x."""
    rng = np.random.default_rng(seed)
    G = Geo()
    dl, sz = 4.35 + rng.uniform(-0.25, 0.25), 1.80
    # nadwozie: pierścienie od progu do linii okien (lekko zwężane, zaokrąglone narożniki)
    nad = [_pierscien(dl - 0.10, sz - 0.06, 0.30, 0.30), _pierscien(dl, sz, 0.42, 0.34),
           _pierscien(dl, sz, 0.78, 0.36), _pierscien(dl - 0.18, sz - 0.08, 0.96, 0.38)]
    _petla(G, nad, 'auto')
    # kabina (szyby) – zbieżna ku górze, przesunięta ku tyłowi, dach lakierowany
    kab = [_pierscien(dl * 0.62, sz - 0.14, 0.96, 0.30, dx=-0.18), _pierscien(dl * 0.44, sz - 0.36, 1.38, 0.24, dx=-0.30)]
    _petla(G, kab, 'auto_szyba')
    dach = [_pierscien(dl * 0.44, sz - 0.36, 1.375, 0.24, dx=-0.30), _pierscien(dl * 0.42, sz - 0.40, 1.44, 0.22, dx=-0.30)]
    _petla(G, dach, 'auto')
    # koła
    for xk in (dl / 2 - 0.80, -dl / 2 + 0.75):
        for yk in (sz / 2 - 0.12, -sz / 2 + 0.12):
            rg = [[(xk + 0.33 * math.cos(2 * math.pi * i / 20), yk + dy, 0.33 + 0.33 * math.sin(2 * math.pi * i / 20))
                   for i in range(20)] for dy in (-0.11, 0.11)]
            _petla(G, rg, 'guma')
            fe = [[(xk + 0.20 * math.cos(2 * math.pi * i / 16), yk + (0.115 if yk > 0 else -0.115),
                    0.33 + 0.20 * math.sin(2 * math.pi * i / 16)) for i in range(16)]]
            G.face(fe[0] if yk > 0 else fe[0][::-1], [(0, 0)] * 16, 'metal')
    # światła: przód (jasne), tył (czerwone – materiał „litery” przyciemniony zastąpiony ciemnym lakierem)
    for yy in (sz / 2 - 0.30, -sz / 2 + 0.30):
        G.pryzma(Polygon([(dl / 2 - 0.02, yy - 0.18), (dl / 2 + 0.005, yy - 0.18), (dl / 2 + 0.005, yy + 0.18),
                          (dl / 2 - 0.02, yy + 0.18)]), 0.70, 0.80, 'metal')
        G.pryzma(Polygon([(-dl / 2 - 0.005, yy - 0.20), (-dl / 2 + 0.02, yy - 0.20), (-dl / 2 + 0.02, yy + 0.20),
                          (-dl / 2 - 0.005, yy + 0.20)]), 0.78, 0.88, 'ludzie:okrycie_jasne')
    ob = G.obiekt(nazwa, coll, B.mat, 0.0)
    ob.location = (float(poz[0]), float(poz[1]), float(z))
    ob.rotation_euler = (0, 0, math.atan2(kier[1], kier[0]))
    return ob


def rowerzysta(B, coll, poz, kier, z, nazwa='rowerzysta', seed=0):
    """Rowerzysta: rower miejski (koła 28\", rama, kierownica, siodełko) i jadąca postać z metaballi
    (tułów pochylony, ręce na kierownicy, nogi na pedałach). Lokalnie jazda wzdłuż +y."""
    from mathutils import Vector
    G = Geo()
    Vt, Ft = _torus(0.34, 0.018, 32, 6)
    for oy in (-0.53, 0.53):
        Vs = [(vy, vx + oy, vz + 0.36) for vx, vy, vz in Vt]
        for f in Ft:
            G.face([Vs[i] for i in f], [(0, 0)] * len(f), 'guma')
    tyl, przod = np.array([0, -0.53, 0.36]), np.array([0, 0.53, 0.36])
    supp = np.array([0, -0.12, 0.30])           # suport
    sio = np.array([0, -0.24, 0.88])            # pod siodełkiem
    ster = np.array([0, 0.40, 0.92])            # główka ramy
    for a, b in ((supp, sio), (supp, ster), (sio + [0, 0.02, -0.06], ster + [0, -0.02, -0.06]), (sio, tyl),
                 (supp, tyl), (ster, przod), (ster, ster + [0, -0.06, 0.16])):
        _rura(G, a, b, 0.016, 'metal')
    _rura(G, ster + [-0.28, -0.06, 0.16], ster + [0.28, -0.06, 0.16], 0.013, 'metal')        # kierownica
    G.pryzma(Polygon([(-0.08, -0.33), (0.08, -0.33), (0.05, -0.12), (-0.05, -0.12)]), 0.90, 0.95, 'guma')  # siodło
    ob = G.obiekt(nazwa + '_rower', coll, B.mat, 0.0)
    # postać
    mb = bpy.data.metaballs.new(nazwa + '_mb')
    mb.resolution = mb.render_resolution = 0.018
    mb.threshold = 0.6

    def el(typ, co, r, sx=None, sy=None, sz=None, rot=None):
        e = mb.elements.new(type=typ)
        e.co = co
        e.radius = r
        e.stiffness = 4.0
        if sx:
            e.size_x = sx
        if sy:
            e.size_y = sy
        if sz:
            e.size_z = sz
        if rot is not None:
            e.rotation = rot
        return e

    def kaps(a, b, r):
        a, b = Vector(a), Vector(b)
        q = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
        el('CAPSULE', ((a + b) / 2)[:], r / 0.78, sx=(b - a).length / 2, rot=q)
    biodro = Vector((0, -0.22, 1.00))
    bark = Vector((0, 0.10, 1.48))
    for sx, (kol, sto) in ((-0.11, ((-0.11, 0.05, 0.78), (-0.11, -0.02, 0.24))), (0.11, ((0.11, 0.0, 1.02), (0.11, 0.0, 0.52)))):
        kaps((sx, biodro.y, biodro.z), kol, 0.075)
        kaps(kol, sto, 0.055)
        el('ELLIPSOID', (sto[0], sto[1] + 0.05, sto[2] - 0.03), 0.06 / 0.78, sx=0.6, sy=1.5, sz=0.6)
    for t in np.linspace(0, 1, 5):
        c = biodro.lerp(bark, t)
        el('ELLIPSOID', c[:], (0.17 + 0.03 * t) / 0.78, sy=0.65, sz=0.75)
    el('BALL', (0, 0.16, 1.58), 0.05 / 0.78)
    el('ELLIPSOID', (0, 0.22, 1.69), 0.10 / 0.78, sx=0.8, sy=0.95, sz=1.1)
    el('ELLIPSOID', (0, 0.20, 1.73), 0.10 / 0.78, sx=0.86, sy=0.92, sz=0.8)
    for sx in (-1, 1):
        dl_ = (sx * 0.25, 0.34, 1.08)
        kaps((sx * 0.20, 0.10, 1.44), (sx * 0.24, 0.24, 1.22), 0.05)
        kaps((sx * 0.24, 0.24, 1.22), dl_, 0.044)
    tmp = bpy.data.objects.new(nazwa + '_tmp', mb)
    bpy.context.scene.collection.objects.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.metaballs.remove(mb)
    V = np.array([v.co[:] for v in me.vertices])
    H = 1.80
    a_ = me.attributes.new('fv', 'FLOAT', 'POINT')
    a_.data.foreach_set('value', (V[:, 2] / H).astype(np.float32))
    b_ = me.attributes.new('fu', 'FLOAT', 'POINT')
    b_.data.foreach_set('value', np.full(len(V), 0.55, np.float32))
    sk = np.zeros(len(V), np.float32)
    for sx in (-1, 1):
        sk = np.maximum(sk, (np.linalg.norm(V - np.array([sx * 0.25, 0.34, 1.08]), axis=1) < 0.07).astype(np.float32))
    c_ = me.attributes.new('sk', 'FLOAT', 'POINT')
    c_.data.foreach_set('value', sk)
    for pl in me.polygons:
        pl.use_smooth = True
    me.materials.append(B.mat('ludzie'))
    os_ = bpy.data.objects.new(nazwa, me)
    coll.objects.link(os_)
    rot = math.atan2(kier[1], kier[0]) - math.pi / 2
    for o in (ob, os_):
        o.location = (float(poz[0]), float(poz[1]), float(z))
        o.rotation_euler = (0, 0, rot)
    return os_


def _prototyp_siedzacego(nazwa, siedzisko=0.46, dlonie=None, kobieta=False, seed=0):
    """Postać siedząca (metaballe) – radny przy pulpicie / widz na galerii. Początek układu: posadzka pod
    siedziskiem, przód +y. ``dlonie`` – punkty dłoni (domyślnie na pulpicie 0,75 m przed sobą). Atrybuty jak
    w ``_prototyp_czlowieka`` (fv, fu, sk)."""
    from mathutils import Vector
    rng = np.random.default_rng(seed)
    s = rng.uniform(0.94, 1.04)
    zs = siedzisko + 0.08
    if dlonie is None:
        dlonie = ((-0.19, 0.42, 0.78), (0.19, 0.40, 0.78))
    mb = bpy.data.metaballs.new(nazwa)
    mb.resolution = mb.render_resolution = 0.018
    mb.threshold = 0.6

    def el(typ, co, r, sx=None, sy=None, sz=None, rot=None):
        e = mb.elements.new(type=typ)
        e.co = co
        e.radius = r
        e.stiffness = 4.0
        if sx:
            e.size_x = sx
        if sy:
            e.size_y = sy
        if sz:
            e.size_z = sz
        if rot is not None:
            e.rotation = rot
        return e

    def kaps(a, b, r):
        a, b = Vector(a), Vector(b)
        q = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
        el('CAPSULE', ((a + b) / 2)[:], r / 0.78, sx=(b - a).length / 2, rot=q)
    pochyl = rng.uniform(-0.04, 0.06)
    for sx in (-0.11, 0.11):
        kaps((sx, -0.02, zs), (sx, 0.42 * s, zs - 0.02), 0.085)                       # uda
        kaps((sx, 0.44 * s, zs - 0.04), (sx, 0.50 * s, 0.10), 0.058)                  # podudzia
        el('ELLIPSOID', (sx, 0.56 * s, 0.05), 0.065 / 0.78, sx=0.6, sy=1.45, sz=0.6)   # stopy
    for i, (zz, rx) in enumerate(((0.10, 0.19), (0.28, 0.20), (0.44, 0.21), (0.56, 0.20))):
        el('ELLIPSOID', (0, -0.04 + pochyl * zz * 2, zs + zz * s), rx * s / 0.78, sy=0.62, sz=0.7)
    hz = zs + 0.68 * s
    el('BALL', (0, -0.02 + pochyl, hz), 0.05 / 0.78)
    el('ELLIPSOID', (0, pochyl + 0.01, hz + 0.11 * s), 0.10 * s / 0.78, sx=0.8, sy=0.95, sz=1.1)
    el('ELLIPSOID', (0, pochyl - 0.01, hz + 0.15 * s), 0.10 * s / 0.78, sx=0.86, sy=0.92,
       sz=0.8 if not kobieta else 1.0)
    if kobieta:
        el('ELLIPSOID', (0, pochyl - 0.05, hz + 0.05), 0.08 / 0.78, sx=1.05, sy=0.6, sz=1.3)
    bark_z = zs + 0.54 * s
    for (sx, d) in zip((-1, 1), dlonie):
        ram = (sx * 0.21, -0.02 + pochyl, bark_z)
        dl_ = Vector(d)
        lok = (Vector(ram) + dl_) / 2 + Vector((sx * 0.06, -0.10, -0.12))
        kaps(ram, lok[:], 0.055)
        kaps(lok[:], dl_[:], 0.046)
        el('BALL', dl_[:], 0.045 / 0.78)
    tmp = bpy.data.objects.new(nazwa + '_mb', mb)
    bpy.context.scene.collection.objects.link(tmp)
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.metaballs.remove(mb)
    me.name = nazwa
    V = np.array([v.co[:] for v in me.vertices])
    H = hz + 0.25 * s
    fv = V[:, 2] / H
    fv = np.where(V[:, 2] < zs + 0.02, 0.2, fv)            # nogi – strefa spodni
    a_ = me.attributes.new('fv', 'FLOAT', 'POINT')
    a_.data.foreach_set('value', fv.astype(np.float32))
    b_ = me.attributes.new('fu', 'FLOAT', 'POINT')
    b_.data.foreach_set('value', np.full(len(V), (zs + 0.02) / H, np.float32))
    sk = np.zeros(len(V), np.float32)
    for d in dlonie:
        sk = np.maximum(sk, (np.linalg.norm(V - np.array(d), axis=1) < 0.075).astype(np.float32))
    c_ = me.attributes.new('sk', 'FLOAT', 'POINT')
    c_.data.foreach_set('value', sk)
    # włosy: tył i boki głowy (za płaszczyzną twarzy) powyżej linii karku
    wl = ((V[:, 2] > hz + 0.06) & (V[:, 1] < pochyl - 0.01)).astype(np.float32)
    d_ = me.attributes.new('wl', 'FLOAT', 'POINT')
    d_.data.foreach_set('value', wl)
    for pl in me.polygons:
        pl.use_smooth = True
    return me


def wozek(B, coll, zf, poz=None, kier=None, nazwa=''):
    """Osoba na wózku wjeżdżająca samodzielnie do Bramy Mostowej (oś przekątna, przed drzwiami głównymi R 11):
    wózek aktywny (koła Ø 0,60 m, obręcze, kółka przednie, rama), sylwetka siedząca z metaballi.
    ``poz`` (e, n) i ``kier`` (wektor kierunku jazdy) – ustawienie dowolne (np. przy niskiej ladzie w hali)."""
    from mathutils import Vector
    sp = B.spec
    cx, cy = sp.luk['srodek']
    R11 = sp.podcien_R
    if poz is None:
        # pozycja: w podcieniu między kolumnami 45° i 60° (kąt łuku liczony od elewacji wsch.), jazda wzdłuż
        # podcienia ku drzwiom w osi 45° – z placu (W3) widoczna z boku, między kolumnami
        kat = B.o.get('wozek_kat_luku', 52.0)
        pk = np.subtract(sp.z_uv(26.0 + 14.0 * math.cos(math.radians(kat)), 15.7 + 14.0 * math.sin(math.radians(kat))),
                         (cx, cy))
        a_r = math.atan2(pk[1], pk[0])
        kier_n = np.array([math.cos(a_r), math.sin(a_r)])
        p = np.array([cx, cy]) + kier_n * (R11 + 1.4)
        kier_ruchu = np.array([-kier_n[1], kier_n[0]]) * (1.0 if kat < 45.0 else -1.0)   # stycznie, ku osi 45°
    else:
        p = np.asarray(poz, float)
        kier_ruchu = np.asarray(kier, float) / np.linalg.norm(kier)
    z = float(zf([p[0]], [p[1]])[0])
    mat = B.mat('ludzie:okrycie_jasne')      # kontrastowe okrycie (rdzawa kurtka) – czytelne na tle szklenia
    # wózek – lokalnie: przód +y, koła po bokach x = ±0,30
    Vt, Ft = _torus(0.30, 0.018)
    Vo, Fo = _torus(0.27, 0.008)
    Vk, Fk = _torus(0.07, 0.02, 16, 6)
    G = Geo()
    for sx in (-0.31, 0.31):
        for V, F, (oy, oz), mt in ((Vt, Ft, (0.0, 0.30), 'wn_ciemne'), (Vo, Fo, (0.0, 0.30), 'metal'),
                                   (Vk, Fk, (0.42, 0.09), 'wn_ciemne')):
            # torus z _torus leży w XZ – obrót do płaszczyzny YZ (koło toczy się wzdłuż +y, oś wzdłuż x)
            Vs = [(x + sx + (0.025 if mt == 'metal' else 0) * np.sign(sx), y + oy, zz + oz) for x, y, zz in
                  [(vy, vx, vz) for vx, vy, vz in V]]
            for f in F:
                G.face([Vs[i] for i in f], [(0, 0)] * len(f), mt)
    # rama i siedzisko
    for a, b in (((-0.27, -0.05, 0.50), (-0.27, 0.42, 0.50)), ((0.27, -0.05, 0.50), (0.27, 0.42, 0.50)),
                 ((-0.27, 0.42, 0.50), (-0.27, 0.42, 0.12)), ((0.27, 0.42, 0.50), (0.27, 0.42, 0.12)),
                 ((-0.27, -0.08, 0.50), (-0.27, -0.12, 0.92)), ((0.27, -0.08, 0.50), (0.27, -0.12, 0.92))):
        L = LineString([a[:2], b[:2]])
        z0, z1 = min(a[2], b[2]), max(a[2], b[2])
        if L.length < 0.01:
            G.pryzma(Point(a[:2]).buffer(0.014, 6), z0, z1, 'metal')
        else:
            G.pryzma(L.buffer(0.014, cap_style=2), z0, z0 + 0.03, 'metal')
    G.pryzma(Polygon([(-0.25, -0.05), (0.25, -0.05), (0.25, 0.38), (-0.25, 0.38)]), 0.50, 0.54, 'wn_ciemne')
    ob = G.obiekt('wozek' + nazwa, coll, B.mat, 0.0)
    # sylwetka siedząca (metaballe)
    mb = bpy.data.metaballs.new('siedzacy')
    mb.resolution = mb.render_resolution = 0.018
    mb.threshold = 0.6

    def el(typ, co, r, sx=None, sy=None, sz=None, rot=None):
        e = mb.elements.new(type=typ)
        e.co = co
        e.radius = r
        e.stiffness = 4.0
        if sx:
            e.size_x = sx
        if sy:
            e.size_y = sy
        if sz:
            e.size_z = sz
        if rot is not None:
            e.rotation = rot
        return e

    def kaps(a, b, r):
        a, b = Vector(a), Vector(b)
        q = Vector((1, 0, 0)).rotation_difference((b - a).normalized())
        el('CAPSULE', ((a + b) / 2)[:], r / 0.78, sx=(b - a).length / 2, rot=q)
    for sx in (-0.11, 0.11):
        kaps((sx, 0.0, 0.62), (sx, 0.42, 0.60), 0.085)          # uda
        kaps((sx, 0.44, 0.58), (sx, 0.48, 0.16), 0.06)          # podudzia
        el('ELLIPSOID', (sx, 0.54, 0.12), 0.07 / 0.78, sx=0.6, sy=1.4, sz=0.6)
    for zz, rx in ((0.70, 0.19), (0.88, 0.20), (1.04, 0.21), (1.16, 0.20)):
        el('ELLIPSOID', (0, -0.03, zz), rx / 0.78, sy=0.62, sz=0.7)
    el('BALL', (0, -0.02, 1.27), 0.05 / 0.78)
    el('ELLIPSOID', (0, 0.0, 1.38), 0.10 / 0.78, sx=0.8, sy=0.95, sz=1.1)
    el('ELLIPSOID', (0, -0.02, 1.42), 0.10 / 0.78, sx=0.86, sy=0.92, sz=0.8)
    for sx in (-1, 1):
        kaps((sx * 0.21, -0.02, 1.14), (sx * 0.27, 0.05, 0.86), 0.055)
        kaps((sx * 0.27, 0.05, 0.86), (sx * 0.31, 0.12, 0.62), 0.046)
    tmp = bpy.data.objects.new('siedzacy_mb', mb)
    bpy.context.scene.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.metaballs.remove(mb)
    V = np.array([v.co[:] for v in me.vertices])
    H = 1.50
    a_ = me.attributes.new('fv', 'FLOAT', 'POINT')
    fv = V[:, 2] / H
    fv = np.where(fv < 0.42, np.minimum(fv, 0.30) * 0 + 0.2, fv)          # nogi (siedzące) – strefa spodni
    a_.data.foreach_set('value', fv.astype(np.float32))
    b_ = me.attributes.new('fu', 'FLOAT', 'POINT')
    b_.data.foreach_set('value', np.full(len(V), 0.45, np.float32))
    sk = np.zeros(len(V), np.float32)
    for sx in (-1, 1):
        sk = np.maximum(sk, (np.linalg.norm(V - np.array([sx * 0.31, 0.12, 0.62]), axis=1) < 0.075).astype(np.float32))
    c_ = me.attributes.new('sk', 'FLOAT', 'POINT')
    c_.data.foreach_set('value', sk)
    for pl in me.polygons:
        pl.use_smooth = True
    me.materials.append(mat)
    os_ = bpy.data.objects.new('osoba_na_wozku' + nazwa, me)
    coll.objects.link(os_)
    rot = math.atan2(kier_ruchu[1], kier_ruchu[0]) - math.pi / 2     # przodem w kierunku jazdy (+y lokalnie)
    for o in (ob, os_):
        o.location = (p[0], p[1], z + B.DZ)
        o.rotation_euler = (0, 0, rot)
    B.info['wozek' + nazwa] = [round(float(p[0]), 2), round(float(p[1]), 2)]


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
    pozy = ('', 'kieszen', 'telefon', '', 'kieszen', '', '', 'oba', '', 'telefon')
    for i, (H, chod, pl, kob, tb) in enumerate(warianty):
        poza = pozy[i] if (chod == 0 or pozy[i] == 'kieszen') else ''
        me = _prototyp_czlowieka('czlowiek_%d' % i, H, chod, pl, kob, seed=i, torba=tb, poza=poza)
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
    # postaci „scenariuszowe”: piesi z mostu ku Bramie Mostowej i wzdłuż podcienia (skala wejścia głównego)
    cx, cy = B.spec.luk['srodek']
    for kat, rr in ((12.0, 16.5), (20.0, 15.2), (21.0, 15.8), (38.0, 17.5), (67.0, 16.4), (63.0, 19.5), (80.0, 16.2)):
        pk = np.subtract(B.spec.z_uv(26.0 + 14.0 * math.cos(math.radians(kat)), 15.7 + 14.0 * math.sin(math.radians(kat))),
                         (cx, cy))
        q = (cx + pk[0] / 14.0 * rr, cy + pk[1] / 14.0 * rr)
        if obszar.buffer(0.5).contains(Point(q)) and all(math.dist(q, w) > 1.2 for w in poz):
            poz.append(q)
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
    # ludzie fotograficzni (Skalgubbar, billboardy) – gdy wycinki są w build/skalgubbar (uwagi 17.11)
    from umwd.render import budynek3d_ludzie_foto as lf
    if B.o.get('ludzie_foto', True) and lf.dostepne():
        n_f = B.o.get('ludzie_foto_liczba', 22)
        poz_f = poz[:n_f]
        ogrod = Polygon([(55, -10), (100, -10), (100, 38), (55, 38)])
        for i, p in enumerate(poz_f):
            z = float(zf([p[0]], [p[1]])[0]) if plac.contains(Point(p)) else (
                float(ctx.teren.z1(p[0], p[1]) - B.DZ + 0.03) if ctx is not None else 0.0)
            rodzaje = ('rodzina', 'para', 'pieszy', 'stoi') if ogrod.contains(Point(p)) else \
                ('pieszy', 'urzednik', 'stoi', 'para')
            lf.postac(coll, lf.wybierz(rng, rodzaje), p, z + B.DZ, 'foto_czlowiek_%02d' % i, rng=rng)
        B.info['ludzie'] = len(poz_f)
        B.info['ludzie_foto'] = True
        B.info['czasy_s']['ludzie'] = round(time.time() - t0, 1)
        return
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
        if idzie and B.o.get('ruch_ludzi', True):
            # subtelne rozmycie ruchu (ok. 1/20 s przy 1,3 m/s ≈ 7 cm): klatki 0–2, migawka 1 klatka
            v = np.array([math.cos(kier), math.sin(kier)]) * B.o.get('ruch_ludzi_m', 0.07)
            for f in (0, 1, 2):
                ob.location = (p[0] + v[0] * (f - 1), p[1] + v[1] * (f - 1), z + B.DZ)
                ob.keyframe_insert('location', frame=f)
            if ob.animation_data and ob.animation_data.action:
                for fc in _krzywe(ob.animation_data.action):
                    for kp in fc.keyframe_points:
                        kp.interpolation = 'LINEAR'
            B.sc.render.use_motion_blur = True
            B.sc.render.motion_blur_shutter = 1.0
            B.sc.frame_set(1)
    B.info['ludzie'] = len(poz)
    B.info['czasy_s']['ludzie'] = round(time.time() - t0, 1)
