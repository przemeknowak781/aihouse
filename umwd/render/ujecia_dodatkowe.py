# -*- coding: utf-8 -*-
"""Dodatkowe (nadprogramowe) ujęcia budynku „BRAMA I LATARNIA” – render sterowany plikiem JSON kamer.

Scena: kontekst 3D (jesień, obszar inwestycji pusty) + budynek z ``budynek3d`` (API: docs/60_wizualizacje/budynek_3d.md),
światło ``budynek3d.swiatlo_dzienne(czas)``; o zmierzchu dodatkowo latarnie uliczne (emisja kloszy + reflektory
punktowe) i udział zapalonych opraw biurowych. Przed renderem – kontrola kamery (w bryle? w koronie drzewa? co
zasłania kadr, ile kadru zajmuje budynek, czy widać Bramę Mostową i koronę, czy tło nie wychodzi poza modelowany
świat) zapisywana od razu jako ``<plik>_kontrola.json`` obok obrazu. Render Cycles + OIDN → PNG (``build/ujecia_dodatkowe``)
→ ``tools/postprodukcja.py --preset P`` → JPG q95 (domyślnie ``docs/60_wizualizacje/img/extra/<id>_<szer>.jpg``).

Plik kamer (domyślnie ``docs/60_wizualizacje/ujecia_dodatkowe.json``)::

    {"ujecia": [{"id": "...", "cam": {"e":, "n":, "z":}, "target": {"e":, "n":, "z":}, "lens_mm": 24,
                 "shift_x": 0, "shift_y": 0.28, "aspect": 1.5, "czas": "2026-10-23 14:30 CEST",
                 "ludzie": true, "preset": "dzien|lot|zmierzch|wnetrze"}]}

z – rzędna względna budynku (±0,00 = 119,30 m n.p.m.; w scenie Z = z + DZ, DZ = 0,05), chyba że w punkcie podano
``"z_od": "teren"`` (z nad podłożem) albo ``"scena"`` (Z sceny). Pozostałe klucze opcjonalne – patrz ``_pola`` w JSON.

Uruchomienie (po jednym procesie naraz – maszyna 4-rdzeniowa)::

    /home/user/aihouse/.venv-render/bin/python -I /home/user/aihouse/umwd/render/ujecia_dodatkowe.py \
        --id plac_mostowy [--id ...] [--json PATH] [--szer 480] [--probki 16] [--out PATH] [--bez-ludzi] \
        [--kontrola-tylko] [--blend scena.blend] [--lista]

``--blend PATH``: jeśli plik istnieje – scena (kontekst + budynek, bez kamer i świateł) jest wczytywana z niego
(oszczędza ok. 15 s budowy); jeśli nie istnieje – scena jest budowana od zera i zapisywana pod tą ścieżką.
Bez ``--blend`` – zawsze budowa od zera (zalecane po każdej zmianie modelu).
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

UMWD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UMWD / 'src'))

import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402
from shapely.geometry import Point, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from umwd.render import blib, context, budynek3d  # noqa: E402

JSON_DOMYSLNY = UMWD / 'docs' / '60_wizualizacje' / 'ujecia_dodatkowe.json'
OUT_DOMYSLNY = UMWD / 'docs' / '60_wizualizacje' / 'img' / 'extra'
PNG_DIR = UMWD / 'build' / 'ujecia_dodatkowe'
POSTPRODUKCJA = UMWD / 'tools' / 'postprodukcja.py'
KONCEPCJA = UMWD / 'model' / 'koncepcja.json'
SITE = UMWD / 'model' / 'site.json'
PRESETY = ('dzien', 'lot', 'zmierzch', 'wnetrze')
LOOK = 'AgX - Medium High Contrast'

# zasięg modelowanego świata (context.py): ramka mapy – teren z e-mapy, sąsiedzi LOD3, budynki LOD2+, most, zieleń,
# ulica; dalej – ortofotomapa M.11.A jako płaski teren (e ≈ −1016…+998, n ≈ −557…+834) z 26 prostymi bryłami
# (e −239…464, n −150…445) i drzewami z maski (r ≤ 430 m od (85; 40)); poza ortofotomapą – płaszczyzna z mgłą.
RAMKA_SZCZEGOLOWA = (10.665, -35.52, 151.959, 148.089)
ORTOFOTO = (-1016.0, -557.0, 998.0, 834.0)
BRYLY_DALSZE = (-239.0, -150.0, 464.0, 445.0)


# ============================================================================================== JSON kamer
def _aspect(a):
    if a is None:
        return 1.5
    if isinstance(a, str):
        if ':' in a:
            w, h = a.split(':')
            return float(w) / float(h)
        return float(a.replace(',', '.'))
    return float(a)


def wczytaj_ujecia(path):
    d = json.loads(Path(path).read_text(encoding='utf-8'))
    return d.get('ujecia', [])


def normalizuj(u):
    """Uzupełnia wartości domyślne i sprawdza poprawność wpisu ujęcia."""
    k = dict(u)
    for pole in ('id', 'cam', 'target', 'czas'):
        if pole not in k:
            raise SystemExit('ujęcie %s: brak pola %r' % (k.get('id', '?'), pole))
    k['preset'] = k.get('preset', 'dzien')
    if k['preset'] not in PRESETY:
        raise SystemExit('ujęcie %s: preset %r – dozwolone %s' % (k['id'], k['preset'], '|'.join(PRESETY)))
    k['lens_mm'] = float(k.get('lens_mm', 24))
    k['shift_x'] = float(k.get('shift_x', 0.0))
    k['shift_y'] = k.get('shift_y', 0.0)
    k['aspect'] = _aspect(k.get('aspect'))
    k['ludzie'] = bool(k.get('ludzie', True))
    k['poziom'] = bool(k.get('poziom', k['preset'] != 'lot'))
    for p in ('cam', 'target'):
        q = dict(k[p])
        q.setdefault('z_od', 'zero')
        if q['z_od'] not in ('zero', 'teren', 'scena'):
            raise SystemExit('ujęcie %s: %s.z_od = %r (zero|teren|scena)' % (k['id'], p, q['z_od']))
        k[p] = q
    return k


# ============================================================================================== scena
def zbuduj_scene(ludzie, opts_bud=None):
    t0 = time.time()
    sc = blib.reset()
    kon = context.build_context(sc, {'pora_roku': 'jesien', 'obszar_inwestycji': 'pusty'})
    t_kon = time.time() - t0
    t1 = time.time()
    o = {'kontekst': kon, 'ludzie': ludzie}
    o.update(opts_bud or {})
    bud = budynek3d.build_building(sc, o)
    t_bud = time.time() - t1
    return sc, kon, bud, {'kontekst_s': round(t_kon, 1), 'budynek_s': round(t_bud, 1)}


def wczytaj_blend(path):
    t0 = time.time()
    bpy.ops.wm.open_mainfile(filepath=str(path))
    sc = bpy.context.scene
    for ob in [o for o in sc.objects if o.type in ('CAMERA', 'LIGHT')]:
        bpy.data.objects.remove(ob)
    return sc, {'wczytanie_blend_s': round(time.time() - t0, 1)}


def obiekty_trawy():
    return [ob for ob in bpy.data.objects
            if any(md.type == 'NODES' and md.node_group and md.node_group.name.startswith('K_trawa_GN')
                   for md in ob.modifiers)]


def mapa_kategorii():
    """Nazwa obiektu → kategoria (do statystyki promieni kadru)."""
    kat = {}
    kol = {'K_teren': 'teren', 'K_woda': 'woda', 'K_sasiedzi': 'zabudowa_kontekstu', 'K_budynki': 'zabudowa_kontekstu',
           'K_most': 'most', 'K_zielen': 'drzewa', 'K_ulica': 'ulica', 'K_dalsze': 'dalsze_otoczenie'}
    for c in bpy.data.collections:
        k = kol.get(c.name.split('.')[0])
        if k:
            for ob in c.all_objects:
                kat[ob.name] = k
    root = bpy.data.collections.get('BUDYNEK')
    if root is not None:
        for c in root.children:
            k = 'zagospodarowanie' if c.name.startswith('zagospodarowanie') else 'budynek'
            for ob in c.all_objects:
                kat[ob.name] = k
    return kat


def kategoria(nazwa, kat):
    n = nazwa.lower()
    if n.startswith('teren_poza_ortofoto'):
        return 'poza_swiatem'
    if n.startswith('teren_dalszy_ortofoto'):
        return 'ortofoto_plaskie'
    if any(s in n for s in ('liscie', 'galezie', 'pien', 'kora', 'konar', 'krzew', 'igl')):
        return 'drzewa'
    if 'kepka' in n or 'trawa' in n:
        return 'teren'
    if n.startswith('czlowiek'):
        return 'ludzie'
    if n.startswith('posadzk'):
        return 'teren'
    return kat.get(nazwa, 'inne')


# ============================================================================================== światło
def latarnie(sc, wlacz, moc_W=50.0):
    """Latarnie uliczne (context.py: obiekty 'latarnia_*', materiał 'K_klosz', oprawa na wysięgniku 1,5 m,
    ok. 8,1 m nad cokołem): emisja kloszy (ciepłe 3000 K, siła 60) + reflektor punktowy pod każdą oprawą
    (moc_W – moc Blendera; ≈ 8000 lm w stożku 125°, ok. 40 lx pod latarnią). Klosze latarń mostowych też świecą.
    wlacz=False – klosze bez emisji, reflektory usunięte (kolejne ujęcie dzienne w tym samym procesie)."""
    for ob in [o for o in sc.objects if o.name.startswith('UJ_latarnia')]:
        bpy.data.objects.remove(ob)
    m = bpy.data.materials.get('K_klosz')
    if m is not None and m.node_tree:
        if 'UJ_emisja' not in m.node_tree.nodes:
            nb = blib.NodeBuilder(m)
            b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.15)
            nb.set(b, 'Base Color', (0.85, 0.85, 0.80))
            nb.set(b, 'Emission Color', (1.0, 0.76, 0.50))
            v = nb.n('ShaderNodeValue')
            v.name = 'UJ_emisja'
            nb.l(v, b.inputs['Emission Strength'])
            nb.output(b)
        m.node_tree.nodes['UJ_emisja'].outputs[0].default_value = 60.0 if wlacz else 0.0
    if not wlacz:
        return 0
    n = 0
    hx, hz = 1.5, 7.7 + 0.55 - 0.12            # koniec wysięgnika (context._latarnia_proto)
    for ob in list(sc.objects):
        if ob.type != 'MESH' or not ob.name.startswith('latarnia_'):
            continue
        p = ob.matrix_world @ Vector((hx + 0.2, 0.0, hz - 0.12))
        ld = bpy.data.lights.new('UJ_latarnia_%d' % n, 'SPOT')
        ld.energy = moc_W
        ld.color = (1.0, 0.78, 0.55)
        ld.spot_size = math.radians(125)
        ld.spot_blend = 0.6
        ld.shadow_soft_size = 0.15
        lo = bpy.data.objects.new('UJ_latarnia_%d' % n, ld)
        lo.location = p
        lo.rotation_euler = (0.0, 0.0, 0.0)    # reflektor świeci w −Z
        sc.collection.objects.link(lo)
        n += 1
    return n


def ustaw_swiatlo(sc, k):
    """swiatlo_dzienne + korekty presetu (zmierzch: ekspozycja po zachodzie, latarnie, udział opraw biur)."""
    ekspo = k.get('ekspozycja')
    sw = budynek3d.swiatlo_dzienne(sc, k['czas'], ekspozycja=ekspo, chmury=k.get('chmury', 0.35))
    el = sw['el']
    if ekspo is None and el < 0:
        # kalibracja: el = 0° → −1,2 EV (API), el = −5,8° → +0,6 EV (W9, błękitna godzina, przyjęte w testach)
        ekspo = round(-1.2 - 0.31 * max(el, -9.0), 2)
        sc.view_settings.exposure = ekspo
        sw['ekspozycja'] = ekspo
        sw['ekspozycja_zrodlo'] = 'kalibracja zmierzchu (W9)'
    if k.get('udzial_opraw') is not None:
        m_l = bpy.data.materials.get('B_wn_lampa')
        if m_l is not None and m_l.node_tree and 'udzial' in m_l.node_tree.nodes:
            m_l.node_tree.nodes['udzial'].outputs[0].default_value = float(k['udzial_opraw'])
            sw['udzial_opraw'] = float(k['udzial_opraw'])
    else:
        sw['udzial_opraw'] = 1.0 if el > 3 else 0.35
    wl = k.get('latarnie', k['preset'] == 'zmierzch' or el < 3)
    sw['latarnie'] = latarnie(sc, bool(wl))
    return sw


# ============================================================================================== kamera
def podloze(sc, dg, e, n, z_start=400.0, pomin=('drzewa', 'ludzie', 'ulica'), kat=None):
    """Z podłoża w punkcie (e, n): promień z góry, z pominięciem drzew, ludzi i drobnych elementów ulicy."""
    o = Vector((e, n, z_start))
    d = Vector((0, 0, -1))
    for _ in range(40):
        hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, o, d)
        if not hit:
            return None, None
        if kategoria(ob.name, kat or {}) in pomin:
            o = pos + d * 0.02
            continue
        return pos.z, ob.name
    return None, None


def punkt_sceny(sc, dg, q, DZ, kat):
    z_od = q.get('z_od', 'zero')
    if z_od == 'scena':
        return Vector((q['e'], q['n'], q['z']))
    if z_od == 'teren':
        zt, _ = podloze(sc, dg, q['e'], q['n'], kat=kat)
        if zt is None:
            raise SystemExit('brak podłoża pod punktem (%.1f; %.1f)' % (q['e'], q['n']))
        return Vector((q['e'], q['n'], zt + q['z']))
    return Vector((q['e'], q['n'], q['z'] + DZ))


def ustaw_kamere(sc, k, loc, cel):
    shift_y = k['shift_y']
    if isinstance(shift_y, str) and shift_y == 'auto':
        shift_y = blib.auto_shift_for_target(loc, cel, k['lens_mm'], 36.0, 1.0 / k['aspect']) if k['poziom'] else 0.0
    cam = blib.camera(sc, tuple(loc), tuple(cel), lens_mm=k['lens_mm'], shift_x=k['shift_x'], shift_y=float(shift_y),
                      level=k['poziom'], name='UJ_' + k['id'])
    cam.data.sensor_fit = 'AUTO'              # ogniskowa i przesunięcia liczone dla dłuższego boku kadru
    cam.data.clip_start = 0.05 if k['preset'] == 'wnetrze' else 0.2
    cam.data.clip_end = 6000.0
    k['shift_y_uzyte'] = round(float(shift_y), 4)
    return cam


# ============================================================================================== kontrola
def _obwiednia_proto(coll, cache):
    """(R_poziome, z_korony_0, z_korony_1) prototypu drzewa w jego układzie (skala 1)."""
    if coll.name in cache:
        return cache[coll.name]
    xs, zs_k, zs = [], [], []
    for ob in coll.all_objects:
        if ob.type != 'MESH':
            continue
        korona = any(s in ob.name for s in ('liscie', 'galezie', 'igl'))
        for c in ob.bound_box:
            v = ob.matrix_world @ Vector(c) - Vector(coll.instance_offset)
            zs.append(v.z)
            if korona:
                xs.append(max(abs(v.x), abs(v.y)))
                zs_k.append(v.z)
    if not xs:
        r = (0.0, 0.0, 0.0)
    else:
        r = (max(xs), min(zs_k), max(zs_k))
    cache[coll.name] = r
    return r


def _kierunek_kadru(cam, sc, fx, fy):
    a, b, c, d_ = cam.data.view_frame(scene=sc)     # P-góra, P-dół, L-dół, L-góra (z przesunięciem obiektywu)
    q = c.lerp(b, fx).lerp(d_.lerp(a, fx), fy)
    return (cam.matrix_world.to_3x3() @ q).normalized()


def obrysy_bryl():
    k = json.loads(KONCEPCJA.read_text(encoding='utf-8'))
    out = {}
    for b in k['bryly']:
        d = b.get('dach', {})
        zt = (d.get('attyka') or d.get('gzyms_attyka') or {}).get('wzgl', 21.0)
        out[b['id']] = (Polygon(b['obrys_ccw']).buffer(0), float(zt))
    luk = k['bryly'][0].get('luk', {})
    return out, luk


def kontrola(sc, cam, k, DZ, kat, cel):
    """Kontrola położenia kamery i treści kadru. Zwraca słownik raportu (uwagi = problemy do poprawy)."""
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation.copy()
    uwagi, info = [], []
    bryly, luk = obrysy_bryl()
    p = Point(loc.x, loc.y)
    # 1) w bryle projektowanej?
    for bid, (P, zt) in bryly.items():
        if P.buffer(0.3).contains(p) and loc.z < zt + DZ + 0.5 and k['preset'] != 'wnetrze':
            uwagi.append('KAMERA W OBRYSIE BRYŁY %s (z = %.2f < attyka %.2f)' % (bid, loc.z - DZ, zt))
    # 2) wewnątrz zamkniętej geometrii (promienie w 26 kierunkach trafiają w tylne ściany) + najbliższa przeszkoda
    kier = [Vector((x, y, z)).normalized() for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1)
            if (x, y, z) != (0, 0, 0)]
    tyl, traf, najbl = {}, 0, (1e9, None)
    for d in kier:
        hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d, distance=60.0)
        if not hit:
            continue
        dist = (pos - loc).length
        if dist < najbl[0]:
            najbl = (dist, ob.name)
        if kategoria(ob.name, kat) in ('drzewa', 'ludzie', 'teren'):
            continue
        traf += 1
        if nrm.dot(d) > 0.05:
            tyl[ob.name] = tyl.get(ob.name, 0) + 1
    if tyl and sum(tyl.values()) >= max(8, 0.6 * traf) and k['preset'] != 'wnetrze':
        uwagi.append('KAMERA WEWNĄTRZ GEOMETRII (%s – %d z %d promieni trafia w tylne ściany)'
                     % (max(tyl, key=tyl.get), sum(tyl.values()), traf))
    if najbl[1] is not None and najbl[0] < 0.5:
        uwagi.append('PRZESZKODA TUŻ PRZY KAMERZE: %s %.2f m' % (najbl[1], najbl[0]))
    # 3) drzewa: pień / korona (obwiednie prototypów × skala instancji)
    cache = {}
    for ob in bpy.data.objects:
        if ob.instance_type != 'COLLECTION' or ob.instance_collection is None:
            continue
        if not ob.name.startswith(('drzewo', 'szpaler', 'krzew')):
            continue
        R, zk0, zk1 = _obwiednia_proto(ob.instance_collection, cache)
        s = ob.scale[0]
        dxy = math.hypot(ob.location.x - loc.x, ob.location.y - loc.y)
        dz = loc.z - ob.location.z
        if dxy < 0.6 and dz < zk1 * s:
            uwagi.append('KAMERA W PNIU / PRZY PNIU %s (%.2f m)' % (ob.name, dxy))
        elif R > 0 and dxy < 0.75 * R * s and zk0 * s - 0.3 < dz < zk1 * s:
            uwagi.append('KAMERA W KORONIE %s (%.1f m od pnia, R korony ≈ %.1f m)' % (ob.name, dxy, R * s))
    # 4) oko nad podłożem
    zt, ob_p = podloze(sc, dg, loc.x, loc.y, z_start=loc.z - 0.05, kat=kat)
    oko = None if zt is None else round(loc.z - zt, 2)
    if oko is not None and k['preset'] in ('dzien', 'zmierzch') and loc.z - DZ < 15 and not 1.0 <= oko <= 2.2:
        info.append('oko %.2f m nad podłożem (%s) – typowo 1,5–1,7 m' % (oko, ob_p))
    # 5) promienie kontrolne (jak testy_budynek.py)
    promienie = []
    for fx, fy, opis in ((0.5, 0.5, 'oś'), (0.15, 0.2, 'L-dół'), (0.85, 0.2, 'P-dół'), (0.15, 0.8, 'L-góra'),
                         (0.85, 0.8, 'P-góra'), (0.5, 0.15, 'dół')):
        d = _kierunek_kadru(cam, sc, fx, fy)
        hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d)
        if hit:
            dist = (pos - loc).length
            promienie.append('%s: %s %.1f m' % (opis, ob.name, dist))
            if dist < 2.0:
                uwagi.append('BLISKA PRZESZKODA (%s): %s %.1f m' % (opis, ob.name, dist))
        else:
            promienie.append('%s: niebo' % opis)
    # 6) siatka promieni 24 × 16 → udziały kategorii w kadrze, zasłonięcie pierwszego planu
    nx, ny = 24, 16
    licz, blisko = {}, {}
    for j in range(ny):
        for i in range(nx):
            d = _kierunek_kadru(cam, sc, (i + 0.5) / nx, (j + 0.5) / ny)
            hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d)
            kt = kategoria(ob.name, kat) if hit else 'niebo'
            licz[kt] = licz.get(kt, 0) + 1
            if hit and (pos - loc).length < 6.0 and kt not in ('teren', 'zagospodarowanie', 'woda'):
                blisko[ob.name] = blisko.get(ob.name, 0) + 1
    N = nx * ny
    udzialy = {kk: round(v / N, 3) for kk, v in sorted(licz.items(), key=lambda t: -t[1])}
    if udzialy.get('budynek', 0) < 0.08 and k['preset'] != 'wnetrze':
        uwagi.append('BUDYNEK ZAJMUJE TYLKO %.0f %% KADRU (promienie)' % (100 * udzialy.get('budynek', 0)))
    zasl = sum(blisko.values()) / N
    if zasl > 0.15:
        uwagi.append('PIERWSZY PLAN (< 6 m) ZASŁANIA %.0f %% KADRU: %s' % (
            100 * zasl, ', '.join('%s %d' % t for t in sorted(blisko.items(), key=lambda t: -t[1])[:4])))
    if udzialy.get('poza_swiatem', 0) > 0.005:
        uwagi.append('KADR SIĘGA POZA ORTOFOTOMAPĘ (pusta płaszczyzna): %.1f %% kadru' % (100 * udzialy['poza_swiatem']))
    if udzialy.get('ortofoto_plaskie', 0) > 0.10:
        info.append('płaska ortofotomapa (bez zabudowy 3D) zajmuje %.0f %% kadru – tło poza ramką mapy'
                    % (100 * udzialy['ortofoto_plaskie']))
    # 7) bryły w kadrze (rzut naroży obrysów na ±0,00 i na attyce; x, y ∈ [0, 1] = kadr, y od dołu)
    nazwy = {'W': 'wieża', 'M': 'skrzydło', 'S': 'segment'}
    bk = {}
    for bid, (P, ztop) in bryly.items():
        xs, ys, za, ys_top = [], [], 0, []
        for (x, y) in list(P.exterior.coords)[:-1]:
            for z in (0.0, ztop):
                v = world_to_camera_view(sc, cam, Vector((x, y, z + DZ)))
                if v.z <= 0:
                    za += 1
                    continue
                xs.append(v.x)
                ys.append(v.y)
                if z > 0 and 0 <= v.x <= 1:
                    ys_top.append(v.y)
        if not xs:
            bk[nazwy.get(bid, bid)] = None
            continue
        b = dict(x0=round(min(xs), 3), x1=round(max(xs), 3), y0=round(min(ys), 3), y1=round(max(ys), 3))
        b['rzut_w_kadrze'] = not (b['x1'] < 0 or b['x0'] > 1 or b['y1'] < 0 or b['y0'] > 1)
        b['uciete'] = [s_ for s_, c in (('lewo', b['x0'] < 0), ('prawo', b['x1'] > 1), ('dół', b['y0'] < 0),
                                        ('góra', bool(ys_top) and max(ys_top) > 1)) if c]
        if za:
            b['naroza_za_kamera'] = za
        bk[nazwy.get(bid, bid)] = b
    w = bk.get('wieża')
    if w and 'góra' in w['uciete'] and k['preset'] not in ('wnetrze',):
        info.append('attyka wieży (narożnik bliższy kamerze) wychodzi poza górną krawędź kadru')
    # 8) punkty kluczowe na łuku (Brama Mostowa, korona, attyka) i cel: w kadrze? widoczne?
    kl = {}
    if luk:
        c0 = Vector((*luk['srodek'], 0.0))
        a0 = math.atan2(luk['poczatek'][1] - luk['srodek'][1], luk['poczatek'][0] - luk['srodek'][0])
        a1 = math.atan2(luk['koniec'][1] - luk['srodek'][1], luk['koniec'][0] - luk['srodek'][0])
        am = (a0 + a1) / 2
        R = luk['R_zewn'] + 0.35
        u = Vector((math.cos(am), math.sin(am), 0.0))
        for nazwa, z in (('Brama Mostowa – napis (+5,2)', 5.2), ('korona – lamele łuku (+31,7)', 31.7),
                         ('attyka wieży (+37,2)', 37.2)):
            kl[nazwa] = Vector((c0.x + R * u.x, c0.y + R * u.y, z + DZ))
    kl['cel kamery'] = cel
    pk = {}
    for nazwa, P3 in kl.items():
        v = world_to_camera_view(sc, cam, P3)
        w_kadrze = v.z > 0 and 0 <= v.x <= 1 and 0 <= v.y <= 1
        d = P3 - loc
        hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d.normalized(), distance=d.length - 0.6)
        pk[nazwa] = dict(w_kadrze=bool(w_kadrze), x=round(v.x, 3), y=round(v.y, 3),
                         widoczny=not hit, zaslania=(ob.name if hit else None),
                         odl_m=round(d.length, 1))
    # 9) horyzont (dla kamery poziomej)
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    fwd.z = 0
    hor = None
    if fwd.length > 1e-6:
        v = world_to_camera_view(sc, cam, loc + fwd.normalized() * 2000.0)
        hor = round(v.y, 3)
    # 10) zasięg świata
    e0, n0, e1, n1 = RAMKA_SZCZEGOLOWA
    if not (e0 <= loc.x <= e1 and n0 <= loc.y <= n1):
        info.append('kamera poza ramką mapy (e %.0f–%.0f, n %.0f–%.0f): z tej strony teren to ortofotomapa, '
                    'zabudowa – proste bryły' % (e0, e1, n0, n1))
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).z))))
    if not k['poziom'] and abs(pitch) > 3 and k['preset'] != 'lot':
        info.append('kamera nachylona %.1f° – piony zbiegają się (poziom = false)' % pitch)
    return dict(uwagi=uwagi, info=info, promienie=promienie, udzialy_kadru=udzialy,
                zaslona_pierwszego_planu=round(zasl, 3), najblizsza_przeszkoda=dict(obiekt=najbl[1], odl_m=round(najbl[0], 2)),
                oko_nad_podlozem_m=oko, podloze=ob_p, budynek_w_kadrze=bk, punkty_kluczowe=pk,
                horyzont_y=hor, pochylenie_deg=round(pitch, 2))


# ============================================================================================== render
def render_ujecia(sc, k, a, DZ, kat, czasy, out_jpg):
    dg = bpy.context.evaluated_depsgraph_get()
    W = int(a.szer)
    H = int(round(W / k['aspect']))
    adapt = 0.03 if a.probki < 64 else 0.012
    blib.render_settings(sc, W, H, samples=a.probki, adaptive=adapt, exposure=-4.3, look=LOOK, max_bounces=8,
                         clamp_indirect=8.0)
    sc.cycles.transparent_max_bounces = 24
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.use_persistent_data = True
    # ludzie: ukrycie sylwetek, gdy ujęcie ich nie chce
    pokaz = k['ludzie'] and not a.bez_ludzi
    sylwetki = [ob for ob in sc.objects if ob.name.startswith('czlowiek_')]
    for ob in sylwetki:
        ob.hide_render = not pokaz
    if pokaz and not sylwetki:
        print('[ujecia] UWAGA: scena nie ma sylwetek ludzi (zbudowana/zapisana z --bez-ludzi)')
        pokaz = False
    for ob in [o for o in sc.objects if o.type == 'CAMERA' and o.name.startswith('UJ_')]:
        bpy.data.objects.remove(ob)
    loc = punkt_sceny(sc, dg, k['cam'], DZ, kat)
    cel = punkt_sceny(sc, dg, k['target'], DZ, kat)
    cam = ustaw_kamere(sc, k, loc, cel)
    trawa = obiekty_trawy()
    if trawa:
        from umwd.render import trawa as tr
        tr.ustaw_kamere(trawa, cam)
        # promienie kontroli idą przez depsgraf podglądu: bez setek tysięcy instancji kępek (render – show_render)
        for ob in trawa:
            for md in ob.modifiers:
                if md.type == 'NODES' and md.node_group and md.node_group.name.startswith('K_trawa_GN'):
                    md.show_viewport = False
    sw = ustaw_swiatlo(sc, k)
    bpy.context.view_layer.update()
    t0 = time.time()
    kon = kontrola(sc, cam, k, DZ, kat, cel)
    t_kon = time.time() - t0
    raport = dict(id=k['id'], opis=k.get('opis', ''), preset=k['preset'], czas=k['czas'], slonce=sw,
                  kamera=dict(loc=[round(x, 3) for x in loc], cel=[round(x, 3) for x in cel],
                              z_wzgl_kamery=round(loc.z - DZ, 3), lens_mm=k['lens_mm'], shift_x=k['shift_x'],
                              shift_y=k['shift_y_uzyte'], poziom=k['poziom'], rozdzielczosc=[W, H],
                              sensor_fit='AUTO (36 mm na dłuższym boku)'),
                  ludzie=pokaz, probki=a.probki, czasy_s=dict(czasy, kontrola_s=round(t_kon, 1)), **kon)
    out_jpg = Path(out_jpg)
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding='utf-8')
    print('[ujecia] %s  słońce az %.1f° el %.1f°  ekspozycja %.2f  latarnie %d' % (
        k['id'], sw['az'], sw['el'], sw['ekspozycja'], sw['latarnie']))
    print('         uwagi: %s' % ('; '.join(kon['uwagi']) or 'brak'))
    if kon['info']:
        print('         info: %s' % '; '.join(kon['info']))
    print('         udziały kadru: %s' % ', '.join('%s %.0f%%' % (kk, 100 * v) for kk, v in kon['udzialy_kadru'].items()))
    for nazwa, v in kon['punkty_kluczowe'].items():
        print('         %-32s w kadrze: %-3s  widoczny: %-3s %s' % (nazwa, 'tak' if v['w_kadrze'] else 'nie',
                                                                    'tak' if v['widoczny'] else 'nie',
                                                                    ('(zasłania %s)' % v['zaslania']) if v['zaslania'] else ''))
    print('         raport kontroli → %s' % plik_r)
    if a.kontrola_tylko:
        return raport
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    png = PNG_DIR / (out_jpg.stem + '.png')
    sc.render.filepath = str(png)
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    t_r = time.time() - t1
    print('[ujecia] %s: render %.1f s → %s' % (k['id'], t_r, png))
    t2 = time.time()
    pp = subprocess.run([sys.executable, '-I', str(POSTPRODUKCJA), str(png), str(out_jpg), '--preset', k['preset']],
                        capture_output=True, text=True)
    t_p = time.time() - t2
    if pp.returncode != 0:
        print(pp.stderr)
        raport['postprodukcja_blad'] = pp.stderr[-2000:]
    raport['czasy_s'].update(render_s=round(t_r, 1), postprodukcja_s=round(t_p, 1))
    raport['png'] = str(png)
    raport['jpg'] = str(out_jpg) if pp.returncode == 0 else None
    plik_r.write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding='utf-8')
    print('[ujecia] %s: postprodukcja (%s) %.1f s → %s' % (k['id'], k['preset'], t_p, out_jpg))
    return raport


def main():
    ap = argparse.ArgumentParser(description='Dodatkowe ujęcia budynku UMWD sterowane plikiem JSON kamer.')
    ap.add_argument('--json', default=str(JSON_DOMYSLNY), help='plik kamer (domyślnie %(default)s)')
    ap.add_argument('--id', nargs='+', help='identyfikator(y) ujęcia; kilka – jedna budowa sceny, rendery po kolei')
    ap.add_argument('--szer', type=int, default=480, help='szerokość obrazu [px] (podgląd ≤ 480)')
    ap.add_argument('--probki', type=int, default=16, help='próbki Cycles (podgląd ≤ 16)')
    ap.add_argument('--out', default=None, help='plik JPG (jedno ujęcie) albo katalog; domyślnie img/extra/<id>_<szer>.jpg')
    ap.add_argument('--bez-ludzi', action='store_true', help='bez sylwetek ludzi (podglądy)')
    ap.add_argument('--kontrola-tylko', action='store_true', help='tylko kontrola kamery i raport, bez renderu')
    ap.add_argument('--blend', default=None, help='scena .blend: wczytaj, jeśli istnieje; inaczej zbuduj i zapisz')
    ap.add_argument('--lista', action='store_true', help='wypisz ujęcia z pliku JSON i zakończ')
    a = ap.parse_args()
    wszystkie = wczytaj_ujecia(a.json)
    if a.lista or not a.id:
        for u in wszystkie:
            print('%-24s %-9s %s  %s' % (u.get('id'), u.get('preset', 'dzien'), u.get('czas', ''), u.get('opis', '')))
        if not a.id:
            print('(podaj --id ID)')
        return
    po_id = {u['id']: u for u in wszystkie}
    brak = [i for i in a.id if i not in po_id]
    if brak:
        raise SystemExit('brak ujęć %s w %s; dostępne: %s' % (brak, a.json, ', '.join(po_id)))
    ujecia = [normalizuj(po_id[i]) for i in a.id]
    ludzie = (not a.bez_ludzi) and any(u['ludzie'] for u in ujecia)
    opts_bud = {}
    lampy = {u.get('lampy') for u in ujecia if u.get('lampy') is not None}
    if len(lampy) == 1:
        opts_bud['lampy'] = float(lampy.pop())
    t0 = time.time()
    if a.blend and Path(a.blend).exists():
        sc, czasy = wczytaj_blend(a.blend)
        czasy['zrodlo_sceny'] = str(a.blend)
    else:
        sc, kon, bud, czasy = zbuduj_scene(ludzie, opts_bud)
        czasy['zrodlo_sceny'] = 'budowa od zera'
        if a.blend:
            bpy.ops.wm.save_as_mainfile(filepath=str(Path(a.blend).resolve()))
            czasy['zapis_blend'] = str(a.blend)
    czasy['scena_s'] = round(time.time() - t0, 1)
    print('[ujecia] scena: %s' % json.dumps(czasy, ensure_ascii=False))
    DZ = budynek3d.Spec(str(KONCEPCJA)).DZ
    kat = mapa_kategorii()
    out = Path(a.out) if a.out else OUT_DOMYSLNY
    for k in ujecia:
        if a.out and len(ujecia) == 1 and out.suffix.lower() in ('.jpg', '.jpeg'):
            jpg = out
        else:
            jpg = out / ('%s_%d.jpg' % (k['id'], a.szer))
        render_ujecia(sc, k, a, DZ, kat, czasy, jpg)
    print('[ujecia] razem %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
