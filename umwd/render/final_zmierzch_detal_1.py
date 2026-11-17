# -*- coding: utf-8 -*-
"""Render finalny ujęcia „zmierzch-detal-1” (Latarnia przez gałęzie – błękitna godzina od pn.-zach.) – nakładka na
wspólną nakładkę finałową zestawu ``render/ujecia_finalne_korekty.py`` (→ ``ujecia_poprawki_kontekstu.py`` →
``ujecia_dodatkowe.py``), bez edycji modułów wspólnych; uruchomienie i argumenty jak ``ujecia_finalne_korekty.py``::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_zmierzch_detal_1.py \
        --id zmierzch-detal-1 --szer 2000 --probki 64 \
        --out umwd/docs/60_wizualizacje/img/extra/E_zmierzch-detal-1.jpg

Warunki wspólne zestawu (z ``ujecia_finalne_korekty.py``, przy budowie sceny od zera): lamele korony łuku wg v1.1
(0,35 × 0,60 m, rozstawy 1,35 / 0,675 m w ciągu Fibonacciego, 21 szt.), sitodruk 30 % na szkle korony łuku.

Dodatkowe klucze wpisu JSON obsługiwane przez tę nakładkę (wszystkie opcjonalne):

* ``"sila_nieba": 6.5`` – mnożnik kopuły nieba w ``budynek3d.swiatlo_dzienne`` (jak W9 w ``testy_budynek.py``):
  więcej chłodnego światła nieba na kamieniu względem ciepłych opraw; ekspozycję podaje się wtedy wprost
  (``"ekspozycja"``, wartość bezwzględna).
* ``"liscie_drobne": {"promien_m": 32, "k": 4, "f": 0.5, "szer": 0.55, "margines_deg": 4}`` – drzewa i krzewy, których
  korona wchodzi w kadr bliżej niż ``promien_m`` od kamery, dostają kopię prototypu z drobnymi liśćmi: każda karta
  liścia („rombik” ok. 0,23 m z ``drzewa.py``) zastąpiona przez ``k`` liści o długości ``f`` × karta, z maską alfa
  kształtu liścia (owal zaostrzony, ogonek u nasady), rozsianych w obrębie karty, z losowym obrotem i pochyleniem.
  Pole liści ≈ pole kart (korona tak samo gęsta i ciemna), krawędź korony czyta się jak koronka, nie „konfetti”.
  Prototypy dalszych drzew bez zmian.
* pomiar luminancji (zawsze, po renderze): promienie przez siatkę 96 × 120 pikseli → klasy (granit, ceramika,
  szkło korony, szkło biur, drzewa, niebo, …) i luminancja obrazu po postprodukcji w tych pikselach (mediana, p90,
  różnica EV szkło korony – granit); wynik w ``<plik>_kontrola.json`` (``pomiar_luminancji``).
* sylwetki ludzi w kadrze (rzut i widoczność głowy) – ``ludzie_w_kadrze`` w raporcie kontroli.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import ujecia_finalne_korekty as FK  # noqa: E402  (warunki wspólne zestawu; importuje ujecia_poprawki_kontekstu)
from umwd.render import budynek3d  # noqa: E402

U = FK.U
BIEZACE = {}           # wpis ujęcia renderowanego w tej chwili (ustawiany w ustaw_swiatlo)
RAPORT_LISCI = {}


# ============================================================================================== (1) siła nieba
_sd = budynek3d.swiatlo_dzienne


def _swiatlo_dzienne_p(sc, czas, *a, **k):
    s = BIEZACE.get('sila_nieba')
    if s is not None and 'sila_nieba' not in k:
        k['sila_nieba'] = float(s)
    r = _sd(sc, czas, *a, **k)
    r['sila_nieba'] = float(k.get('sila_nieba', 1.0))
    return r


budynek3d.swiatlo_dzienne = _swiatlo_dzienne_p

_us = U.ustaw_swiatlo


def _ustaw_swiatlo_p(sc, k):
    BIEZACE.clear()
    BIEZACE.update(k)
    sw = _us(sc, k)
    mn = k.get('oprawy_cieple_mnoznik')
    if mn is not None:
        sw['oprawy_cieple'] = FK.sciemnij_oprawy(float(mn))
        sw['oprawy_cieple_mnoznik'] = float(mn)
    return sw


U.ustaw_swiatlo = _ustaw_swiatlo_p


# ============================================================================================== (2) drobne liście
def _mat_alfa(m0):
    """Kopia materiału liści z maską alfa kształtu liścia (UV: u wzdłuż liścia od ogonka, v w poprzek)."""
    nazwa = m0.name + '_alfa'
    m = bpy.data.materials.get(nazwa)
    if m is not None:
        return m
    m = m0.copy()
    m.name = nazwa
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    out = next(n for n in N if n.type == 'OUTPUT_MATERIAL')
    src = out.inputs['Surface'].links[0].from_socket
    uv = N.new('ShaderNodeUVMap')
    uv.uv_map = 'UVLisc'
    sp = N.new('ShaderNodeSeparateXYZ')
    L.new(uv.outputs['UV'], sp.inputs[0])

    def M(op, a, b=None):
        n = N.new('ShaderNodeMath')
        n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                L.new(x, n.inputs[i])
        return n.outputs[0]
    u, v = sp.outputs[0], sp.outputs[1]
    # blaszka: u 0,10–1,00; półszerokość 0,5·sin(π·t)^0,7·(1,1 − 0,35·t), t = (u − 0,1)/0,9 (nasada zaokrąglona,
    # wierzchołek zaostrzony); ogonek: u 0–0,12, |v − 0,5| < 0,035
    t = M('MAXIMUM', M('MINIMUM', M('DIVIDE', M('SUBTRACT', u, 0.10), 0.90), 1.0), 0.0)
    w = M('MULTIPLY', M('MULTIPLY', M('POWER', M('SINE', M('MULTIPLY', t, math.pi)), 0.7),
                        M('SUBTRACT', 1.10, M('MULTIPLY', t, 0.35))), 0.5)
    dv = M('ABSOLUTE', M('SUBTRACT', v, 0.5))
    blaszka = M('MULTIPLY', M('LESS_THAN', dv, w), M('GREATER_THAN', u, 0.10))
    ogonek = M('MULTIPLY', M('LESS_THAN', dv, 0.035), M('LESS_THAN', u, 0.12))
    alfa = M('MAXIMUM', blaszka, ogonek)
    tr = N.new('ShaderNodeBsdfTransparent')
    mx = N.new('ShaderNodeMixShader')
    L.new(alfa, mx.inputs['Fac'])
    L.new(tr.outputs[0], mx.inputs[1])
    L.new(src, mx.inputs[2])
    L.new(mx.outputs[0], out.inputs['Surface'])
    return m


def _siatka_drobna(ob_l, cfg, seed):
    """Nowa siatka liści: każda karta → k liści z UV (maska alfa w materiale)."""
    me = ob_l.data
    nf = len(me.polygons)
    nv = len(me.vertices)
    co = np.empty(nv * 3, np.float32)
    me.vertices.foreach_get('co', co)
    co = co.reshape(-1, 3)
    tot = np.empty(nf, np.int32)
    me.polygons.foreach_get('loop_total', tot)
    if nf == 0 or not np.all(tot == 4):
        return None
    vi = np.empty(nf * 4, np.int32)
    me.polygons.foreach_get('vertices', vi)
    Q = co[vi].reshape(nf, 4, 3).astype(np.float64)
    rnd = np.zeros(nf, np.float32)
    if 'lisc_rnd' in me.attributes:
        me.attributes['lisc_rnd'].data.foreach_get('value', rnd)
    v0, v1, v2, v3 = Q[:, 0], Q[:, 1], Q[:, 2], Q[:, 3]
    C = (v1 + v3) / 2.0
    s = np.linalg.norm(v1 - v3, axis=1) / 0.60                       # rozmiar karty (drzewa.py: L2 = 0,30)
    th = v0 - C
    th /= np.maximum(np.linalg.norm(th, axis=1, keepdims=True), 1e-9)
    bh = v1 - C
    bh -= th * np.sum(bh * th, axis=1, keepdims=True)
    bh /= np.maximum(np.linalg.norm(bh, axis=1, keepdims=True), 1e-9)
    nh = np.cross(th, bh)
    k = int(cfg.get('k', 4))
    f = float(cfg.get('f', 0.5))
    szer = float(cfg.get('szer', 0.55))
    rng = np.random.default_rng(seed)
    n = nf * k
    Ci = np.repeat(C, k, 0)
    si = np.repeat(s, k, 0)
    ti, bi, ni = np.repeat(th, k, 0), np.repeat(bh, k, 0), np.repeat(nh, k, 0)
    a_, c_, e_ = rng.uniform(-1, 1, n), rng.uniform(-1, 1, n), rng.normal(0, 1, n)
    P = Ci + (ti * a_[:, None] * 0.50 + bi * c_[:, None] * 0.38 + ni * e_[:, None] * 0.10) * si[:, None]
    ang = rng.uniform(0, 2 * math.pi, n)
    ux = ti * np.cos(ang)[:, None] + bi * np.sin(ang)[:, None]
    n2 = ni + rng.normal(0, 0.45, (n, 3))
    n2 /= np.maximum(np.linalg.norm(n2, axis=1, keepdims=True), 1e-9)
    ux -= n2 * np.sum(ux * n2, axis=1, keepdims=True)
    ux /= np.maximum(np.linalg.norm(ux, axis=1, keepdims=True), 1e-9)
    wx = np.cross(n2, ux)
    Ll = (f * 1.02 * si * rng.uniform(0.75, 1.25, n))[:, None]       # karta: 0,62 + 0,40 = 1,02 · s
    Lw = Ll * szer
    p0 = P - ux * Ll * 0.5 - wx * Lw * 0.5
    p1 = P + ux * Ll * 0.5 - wx * Lw * 0.5
    p2 = P + ux * Ll * 0.5 + wx * Lw * 0.5
    p3 = P - ux * Ll * 0.5 + wx * Lw * 0.5
    V = np.stack([p0, p1, p2, p3], 1).reshape(-1, 3).astype(np.float32)
    me2 = bpy.data.meshes.new(ob_l.name + '_drobne')
    me2.vertices.add(len(V))
    me2.vertices.foreach_set('co', V.ravel())
    me2.loops.add(n * 4)
    me2.loops.foreach_set('vertex_index', np.arange(n * 4, dtype=np.int32))
    me2.polygons.add(n)
    me2.polygons.foreach_set('loop_start', np.arange(0, n * 4, 4, dtype=np.int32))
    me2.update(calc_edges=True)
    uvl = me2.uv_layers.new(name='UVLisc')
    uvl.data.foreach_set('uv', np.tile(np.array([0, 0, 1, 0, 1, 1, 0, 1], np.float32), n))
    at = me2.attributes.new('lisc_rnd', 'FLOAT', 'FACE')
    r2 = np.clip(np.repeat(rnd, k) + rng.normal(0, 0.06, n), 0, 1).astype(np.float32)
    at.data.foreach_set('value', r2)
    for msl in ob_l.material_slots:
        me2.materials.append(_mat_alfa(msl.material) if msl.material else None)
    return me2, dict(karty=int(nf), liscie=int(n), rozmiar_karty_m=round(float(np.median(s)) * 1.02, 3),
                     dlugosc_liscia_m=round(float(np.median(Ll)), 3))


def _proto_drobny(proto, cfg, cache):
    if proto.name.endswith('_drobne'):
        return proto, None
    if proto.name in cache:
        return cache[proto.name]
    nowa = bpy.data.collections.new(proto.name + '_drobne')
    nowa.instance_offset = proto.instance_offset
    info = {}
    for ob in proto.objects:
        if ob.name.endswith('_liscie') and ob.type == 'MESH':
            wyn = _siatka_drobna(ob, cfg, seed=len(cache) + 11)
            if wyn is None:
                nowa.objects.link(ob)
                continue
            me2, info = wyn
            ob2 = bpy.data.objects.new(ob.name + '_drobne', me2)
            ob2.matrix_world = ob.matrix_world
            ob2.visible_shadow = ob.visible_shadow
            nowa.objects.link(ob2)
        else:
            nowa.objects.link(ob)
    cache[proto.name] = (nowa, info)
    return nowa, info


def liscie_drobne():
    wpisy = FK.UJECIA_WYBRANE
    if not wpisy or not wpisy[0].get('liscie_drobne'):
        return
    k = wpisy[0]
    cfg = dict(k['liscie_drobne'])
    t0 = time.time()
    ce, cn = float(k['cam']['e']), float(k['cam']['n'])
    az_osi = math.atan2(k['target']['e'] - ce, k['target']['n'] - cn)
    asp = U._aspect(k.get('aspect'))
    lens = float(k.get('lens_mm', 24))
    pol_szer = math.atan((36.0 * min(1.0, asp)) / 2 / lens)          # sensor AUTO: 36 mm na dłuższym boku
    sx = float(k.get('shift_x', 0.0))
    marg = math.radians(float(cfg.get('margines_deg', 4.0)))
    Rmax = float(cfg.get('promien_m', 32.0))
    cache, wybrane = {}, []
    obwiednie = {}
    for ob in list(bpy.data.objects):
        if ob.instance_type != 'COLLECTION' or ob.instance_collection is None:
            continue
        if not ob.name.startswith(('drzewo', 'szpaler', 'krzew')) and 'drzew' not in ob.name:
            continue
        dx, dy = ob.location.x - ce, ob.location.y - cn
        d = math.hypot(dx, dy)
        if d > Rmax or d < 0.5:
            continue
        pr = ob.instance_collection
        if pr.name not in obwiednie:
            obwiednie[pr.name] = U._obwiednia_proto(pr, {})
        R = obwiednie[pr.name][0] * ob.scale[0]
        dang = (math.atan2(dx, dy) - az_osi + math.pi) % (2 * math.pi) - math.pi
        pol_korony = math.atan2(R, d) if d > R else math.pi / 2
        # kadr poziomo: [−pol_szer + shift, +pol_szer + shift] (kompas: dodatni kąt = w prawo)
        lewa, prawa = -pol_szer + sx * 2 * pol_szer, pol_szer + sx * 2 * pol_szer
        if dang + pol_korony < lewa - marg or dang - pol_korony > prawa + marg:
            continue
        nowa, info = _proto_drobny(pr, cfg, cache)
        ob.instance_collection = nowa
        wybrane.append(dict(obiekt=ob.name, prototyp=pr.name, odl_m=round(d, 1),
                            kat_od_osi_deg=round(math.degrees(dang), 1), R_korony_m=round(R, 1)))
    RAPORT_LISCI.clear()
    RAPORT_LISCI.update(cfg=cfg, drzewa=wybrane,
                        prototypy={kk: v[1] for kk, v in cache.items()}, czas_s=round(time.time() - t0, 1))
    print('[zd1] drobne liście: %d instancji, prototypy %s (%.1f s)' % (
        len(wybrane), ', '.join('%s %s' % (kk, v[1]) for kk, v in cache.items()), time.time() - t0))
    for w in wybrane:
        print('      %(obiekt)-16s %(prototyp)-14s %(odl_m)5.1f m  kąt %(kat_od_osi_deg)+6.1f°  R %(R_korony_m)4.1f m' % w)


_zb, _wb = U.zbuduj_scene, U.wczytaj_blend


def zbuduj_scene(*a, **k):
    r = _zb(*a, **k)
    liscie_drobne()
    return r


def wczytaj_blend(*a, **k):
    r = _wb(*a, **k)
    liscie_drobne()
    return r


U.zbuduj_scene, U.wczytaj_blend = zbuduj_scene, wczytaj_blend


# ============================================================================================== (3) raport: ludzie, luminancja
def ludzie_w_kadrze(sc):
    from bpy_extras.object_utils import world_to_camera_view
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation
    out = []
    for ob in sc.objects:
        if not ob.name.startswith('czlowiek') or ob.hide_render:
            continue
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        zmax = max(p.z for p in bb)
        c = sum(bb, Vector()) / 8
        glowa = Vector((c.x, c.y, zmax - 0.12))
        v = world_to_camera_view(sc, cam, glowa)
        if not (v.z > 0 and -0.02 <= v.x <= 1.02 and -0.02 <= v.y <= 1.02):
            continue
        d = glowa - loc
        hit, pos, nrm, i_, obh, mx = sc.ray_cast(dg, loc, d.normalized(), distance=d.length + 0.3)
        widoczny = bool(hit and obh is not None and obh.name.startswith('czlowiek'))
        vy0 = world_to_camera_view(sc, cam, Vector((c.x, c.y, min(p.z for p in bb)))).y
        out.append(dict(obiekt=ob.name, x=round(v.x, 3), y=round(v.y, 3), wys_kadru=round(v.y - vy0, 4),
                        odl_m=round(d.length, 1), glowa_widoczna=widoczny,
                        zaslania=(None if widoczny or not hit else obh.name)))
    return out


def _klasa_materialu(nazwa_ob, mat):
    n = (nazwa_ob or '').lower()
    m = (mat or '').lower()
    if m.startswith('b_'):                       # materiały budynku: prefiks „B_” (budynek3d.Materialy)
        m = m[2:]
    if any(s in n for s in ('liscie', 'galezie', 'krzew')):
        return 'drzewa'
    if n.startswith('czlowiek'):
        return 'ludzie'
    if 'korona' in m and 'szklo' in m:
        return 'szklo_korony'
    if 'lamele_korony' in m:
        return 'lamele_korony'
    if m.startswith('szklo'):
        return 'szklo_biur_parteru'
    if 'granit' in m or m.startswith('gr:') or m.startswith('gr_'):
        return 'granit'
    if m.startswith('cer'):
        return 'ceramika'
    if m.startswith(('al:', 'al_', 'metal')):
        return 'metal'
    return 'inne:' + (m.split(':')[0] if m else n.split('_')[0])


def pomiar_luminancji(sc, jpg, nx=96, ny=120):
    """Luminancja obrazu wynikowego (sRGB → liniowo) w pikselach klas trafionych promieniem kamery."""
    from PIL import Image
    im = np.asarray(Image.open(jpg).convert('RGB'), dtype=np.float32) / 255.0
    lin = np.where(im <= 0.04045, im / 12.92, ((im + 0.055) / 1.055) ** 2.4)
    Lum = 0.2126 * lin[..., 0] + 0.7152 * lin[..., 1] + 0.0722 * lin[..., 2]
    H, W = Lum.shape
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation
    klasy = {}
    for j in range(ny):
        for i in range(nx):
            fx, fy = (i + 0.5) / nx, (j + 0.5) / ny
            d = U._kierunek_kadru(cam, sc, fx, fy)
            hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d)
            if not hit:
                kl = 'niebo'
            else:
                mat = None
                try:
                    oe = ob.evaluated_get(dg)
                    me = oe.data
                    if hasattr(me, 'polygons') and 0 <= idx < len(me.polygons):
                        mi = me.polygons[idx].material_index
                        if mi < len(oe.material_slots) and oe.material_slots[mi].material:
                            mat = oe.material_slots[mi].material.name
                except Exception:
                    mat = None
                kl = _klasa_materialu(ob.name, mat)
            px, py = int(fx * W), int((1 - fy) * H)
            y0, y1, x0, x1 = max(0, py - 1), min(H, py + 2), max(0, px - 1), min(W, px + 2)
            klasy.setdefault(kl, []).append(float(Lum[y0:y1, x0:x1].mean()))
    out = {}
    for kl, v in sorted(klasy.items(), key=lambda t: -len(t[1])):
        a = np.array(v)
        out[kl] = dict(udzial=round(len(a) / (nx * ny), 3), mediana=round(float(np.median(a)), 4),
                       p90=round(float(np.percentile(a, 90)), 4))
    def ev(a, b, ka='mediana', kb='mediana'):
        if a in out and b in out and out[b][kb] > 0:
            return round(math.log2(max(out[a][ka], 1e-6) / out[b][kb]), 2)
        return None
    out['_EV'] = {'szklo_korony(p90) − granit(mediana)': ev('szklo_korony', 'granit', 'p90'),
                  'szklo_korony(mediana) − granit(mediana)': ev('szklo_korony', 'granit'),
                  'niebo − drzewa (mediany)': ev('niebo', 'drzewa'),
                  'niebo − granit (mediany)': ev('niebo', 'granit'),
                  'szklo_korony(p90) − szklo_biur(p90)': ev('szklo_korony', 'szklo_biur_parteru', 'p90', 'p90')}
    return out


_ru = U.render_ujecia


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    out_jpg = Path(out_jpg)
    try:
        r['ludzie_w_kadrze'] = ludzie_w_kadrze(sc)
    except Exception as e:
        r['ludzie_w_kadrze'] = repr(e)
    r['liscie_drobne'] = dict(RAPORT_LISCI)
    if r.get('jpg') and Path(r['jpg']).exists() and not FK.ARGS_EXTRA.wycinek:
        t0 = time.time()
        try:
            r['pomiar_luminancji'] = pomiar_luminancji(sc, r['jpg'])
        except Exception as e:
            r['pomiar_luminancji'] = repr(e)
        print('[zd1] pomiar luminancji (%.1f s): %s' % (time.time() - t0, json.dumps(
            r['pomiar_luminancji'].get('_EV') if isinstance(r['pomiar_luminancji'], dict) else r['pomiar_luminancji'],
            ensure_ascii=False)))
    vis = [p for p in r['ludzie_w_kadrze'] if isinstance(p, dict) and p['glowa_widoczna']] \
        if isinstance(r['ludzie_w_kadrze'], list) else []
    print('[zd1] ludzie w kadrze: %d (głowa widoczna: %d) %s' % (
        len(r['ludzie_w_kadrze']) if isinstance(r['ludzie_w_kadrze'], list) else -1, len(vis),
        '; '.join('%s x %.2f y %.2f %.0f m' % (p['obiekt'], p['x'], p['y'], p['odl_m']) for p in vis[:8])))
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p

if __name__ == '__main__':
    FK.main()
