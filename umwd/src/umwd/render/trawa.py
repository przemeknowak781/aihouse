# -*- coding: utf-8 -*-
"""Trawa 3D dla widoków z poziomu człowieka (bpy 5.2 / Cycles).

Kępki źdźbeł (prototyp: kilkanaście zakrzywionych, zwężających się źdźbeł) są rozpraszane modyfikatorem
Geometry Nodes na powierzchniach trawników. Gęstość zależy od odległości od aktywnej kamery
(pełna do ``r0``, liniowo do zera w ``r1``) – blisko kamery widać źdźbła, dalej wystarcza tekstura trawnika
(dopasowana barwą). Po zmianie kamery należy wywołać ``ustaw_kamere(obiekty, kamera)``.

Rozpraszanie tylko na ścianach poziomych (normalna z > 0,5) – fartuchy siatek terenu są pomijane.
"""
from __future__ import annotations

import math
import numpy as np


def kepka(seed=1, n=14, h=(0.07, 0.13), w=0.006, r=0.035, lean=(0.15, 0.6)):
    """Siatka kępki trawy: n źdźbeł (pasma z 3 segmentów, zwężające się do ostrza). Zwraca (V, F, h_attr)."""
    rng = np.random.default_rng(seed)
    V, F, H = [], [], []
    for _ in range(n):
        bx, by = rng.normal(0, r, 2)
        az = rng.uniform(0, 2 * math.pi)
        hh = rng.uniform(*h)
        ln = rng.uniform(*lean)
        ww = w * rng.uniform(0.7, 1.3)
        d = np.array([math.cos(az), math.sin(az), 0.0])
        side = np.array([-d[1], d[0], 0.0])
        # orientacja płaszczyzny źdźbła losowa wokół osi
        tw = rng.uniform(-0.6, 0.6)
        side = side * math.cos(tw) + d * math.sin(tw)
        o = len(V)
        segs = 3
        for k in range(segs + 1):
            t = k / segs
            # łuk: wychylenie rośnie z kwadratem wysokości
            p = np.array([bx, by, 0.0]) + d * (ln * hh * t * t) + np.array([0, 0, hh * (t - 0.25 * ln * t * t)])
            wk = ww * (1 - t) ** 0.8
            if k < segs:
                V.append(tuple(p - side * wk / 2))
                V.append(tuple(p + side * wk / 2))
                H += [t, t]
            else:
                V.append(tuple(p))
                H.append(1.0)
        for k in range(segs - 1):
            a = o + 2 * k
            F.append((a, a + 1, a + 3, a + 2))
        a = o + 2 * (segs - 1)
        F.append((a, a + 1, a + 2))
    return np.array(V), F, np.array(H)


def mat_trawa_3d(name='K_trawa_3d', pora='jesien'):
    import bpy
    from umwd.render.blib import NodeBuilder
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    nb = NodeBuilder(m)
    att = nb.n('ShaderNodeAttribute', {'attribute_name': 'h', 'attribute_type': 'GEOMETRY'})
    oi = nb.n('ShaderNodeObjectInfo')
    r = nb.n('ShaderNodeValToRGB')
    if pora == 'jesien':
        pal = [(0.0, (0.035, 0.06, 0.012)), (0.55, (0.075, 0.11, 0.02)), (0.8, (0.12, 0.13, 0.03)),
               (0.93, (0.22, 0.19, 0.07)), (1.0, (0.30, 0.25, 0.11))]
    else:
        pal = [(0.0, (0.03, 0.065, 0.01)), (0.6, (0.06, 0.12, 0.02)), (1.0, (0.10, 0.16, 0.03))]
    els = r.color_ramp.elements
    els[0].position, els[0].color = pal[0][0], (*pal[0][1], 1)
    els[1].position, els[1].color = pal[-1][0], (*pal[-1][1], 1)
    for p, c in pal[1:-1]:
        e = els.new(p)
        e.color = (*c, 1)
    nb.l(oi.outputs['Random'], r.inputs['Fac'])
    # ciemniejsza nasada (samocień w darni), jaśniejsze końce
    g = nb.math('ADD', nb.math('MULTIPLY', nb.math('POWER', att.outputs['Fac'], 0.7), 0.75), 0.35)
    cc = nb.n('ShaderNodeCombineColor')
    nb.l(g, cc.inputs[0])
    nb.l(g, cc.inputs[1])
    nb.l(g, cc.inputs[2])
    col = nb.mix(1.0, r.outputs['Color'], cc.outputs[0], blend='MULTIPLY')
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=0.5)
    nb.l(col, b.inputs['Base Color'])
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value = 0.4
    tr = nb.n('ShaderNodeBsdfTranslucent')
    nb.l(col, tr.inputs['Color'])
    mx = nb.n('ShaderNodeMixShader', Fac=0.3)
    nb.l(b.outputs[0], mx.inputs[1])
    nb.l(tr.outputs[0], mx.inputs[2])
    nb.output(mx)
    return m


def prototyp(name, seed, mat, **kw):
    import bpy
    from umwd.render.blib import mesh_from_arrays
    V, F, H = kepka(seed, **kw)
    ob = mesh_from_arrays(name, V, F, mats=[mat], coll=None, point_attrs={'h': H})
    return ob


def node_group(name='K_trawa_GN'):
    """Drzewo GN: rozproszenie kępek z gęstością zależną od odległości od kamery."""
    import bpy
    ng = bpy.data.node_groups.get(name)
    if ng:
        return ng
    ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')
    I = ng.interface
    I.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    s_cam = I.new_socket('Kamera', in_out='INPUT', socket_type='NodeSocketObject')
    s_k = I.new_socket('Kepka', in_out='INPUT', socket_type='NodeSocketObject')
    s_d = I.new_socket('Gestosc', in_out='INPUT', socket_type='NodeSocketFloat')
    s_r0 = I.new_socket('R0', in_out='INPUT', socket_type='NodeSocketFloat')
    s_r1 = I.new_socket('R1', in_out='INPUT', socket_type='NodeSocketFloat')
    s_sk = I.new_socket('Skala', in_out='INPUT', socket_type='NodeSocketFloat')
    s_sd = I.new_socket('Seed', in_out='INPUT', socket_type='NodeSocketInt')
    s_d.default_value, s_r0.default_value, s_r1.default_value, s_sk.default_value = 400.0, 10.0, 35.0, 1.0
    I.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    N, L = ng.nodes, ng.links
    gi = N.new('NodeGroupInput')
    go = N.new('NodeGroupOutput')
    oc = N.new('GeometryNodeObjectInfo')
    oc.transform_space = 'RELATIVE'
    L.new(gi.outputs['Kamera'], oc.inputs['Object'])
    pos = N.new('GeometryNodeInputPosition')
    dist = N.new('ShaderNodeVectorMath')
    dist.operation = 'DISTANCE'
    L.new(pos.outputs[0], dist.inputs[0])
    L.new(oc.outputs['Location'], dist.inputs[1])
    mr = N.new('ShaderNodeMapRange')
    mr.clamp = True
    L.new(dist.outputs['Value'], mr.inputs['Value'])
    L.new(gi.outputs['R0'], mr.inputs['From Min'])
    L.new(gi.outputs['R1'], mr.inputs['From Max'])
    mr.inputs['To Min'].default_value = 1.0
    mr.inputs['To Max'].default_value = 0.0
    dm = N.new('ShaderNodeMath')
    dm.operation = 'MULTIPLY'
    L.new(mr.outputs['Result'], dm.inputs[0])
    L.new(gi.outputs['Gestosc'], dm.inputs[1])
    nrm = N.new('GeometryNodeInputNormal')
    sz = N.new('ShaderNodeSeparateXYZ')
    L.new(nrm.outputs[0], sz.inputs[0])
    cmp = N.new('FunctionNodeCompare')
    cmp.data_type = 'FLOAT'
    cmp.operation = 'GREATER_THAN'
    L.new(sz.outputs['Z'], cmp.inputs[0])
    cmp.inputs[1].default_value = 0.5
    dp = N.new('GeometryNodeDistributePointsOnFaces')
    dp.distribute_method = 'RANDOM'
    L.new(gi.outputs['Geometry'], dp.inputs['Mesh'])
    L.new(cmp.outputs[0], dp.inputs['Selection'])
    L.new(dm.outputs[0], dp.inputs['Density'])
    L.new(gi.outputs['Seed'], dp.inputs['Seed'])
    ok = N.new('GeometryNodeObjectInfo')
    ok.transform_space = 'ORIGINAL'
    L.new(gi.outputs['Kepka'], ok.inputs['Object'])
    if 'As Instance' in ok.inputs:
        ok.inputs['As Instance'].default_value = True
    rr = N.new('FunctionNodeRandomValue')
    rr.data_type = 'FLOAT_VECTOR'
    rr.inputs['Min'].default_value = (0.0, 0.0, 0.0)
    rr.inputs['Max'].default_value = (0.0, 0.0, 6.2832)
    rs = N.new('FunctionNodeRandomValue')
    rs.data_type = 'FLOAT'
    rs.inputs['Min'].default_value = 0.65
    rs.inputs['Max'].default_value = 1.45
    sm = N.new('ShaderNodeMath')
    sm.operation = 'MULTIPLY'
    L.new(rs.outputs['Value'], sm.inputs[0])
    L.new(gi.outputs['Skala'], sm.inputs[1])
    io = N.new('GeometryNodeInstanceOnPoints')
    L.new(dp.outputs['Points'], io.inputs['Points'])
    L.new(ok.outputs['Geometry'], io.inputs['Instance'])
    L.new(rr.outputs[0], io.inputs['Rotation'])
    L.new(sm.outputs[0], io.inputs['Scale'])
    j = N.new('GeometryNodeJoinGeometry')
    L.new(io.outputs['Instances'], j.inputs[0])
    L.new(gi.outputs['Geometry'], j.inputs[0])
    L.new(j.outputs[0], go.inputs[0])
    return ng


def _ustaw_wejscie(md, nazwa, wartosc):
    """Ustawia wartość wejścia modyfikatora GN (bpy 5.x: md.properties.inputs.<id>.value; starsze: md[id])."""
    ident = next(sk.identifier for sk in md.node_group.interface.items_tree
                 if getattr(sk, 'in_out', '') == 'INPUT' and sk.name == nazwa)
    props = getattr(md, 'properties', None)
    if props is not None and hasattr(props, 'inputs'):
        getattr(props.inputs, ident).value = wartosc
    else:
        md[ident] = wartosc


def dodaj(ob, kepka_ob, gestosc=400.0, r0=10.0, r1=35.0, skala=1.0, seed=0):
    """Dodaje modyfikator trawy do obiektu (siatki trawnika)."""
    ng = node_group()
    md = ob.modifiers.new('trawa_3d', 'NODES')
    md.node_group = ng
    _ustaw_wejscie(md, 'Kepka', kepka_ob)
    _ustaw_wejscie(md, 'Gestosc', float(gestosc))
    _ustaw_wejscie(md, 'R0', float(r0))
    _ustaw_wejscie(md, 'R1', float(r1))
    _ustaw_wejscie(md, 'Skala', float(skala))
    _ustaw_wejscie(md, 'Seed', int(seed))
    return md


def ustaw_kamere(obiekty, kamera):
    """Przypisuje kamerę (środek strefy gęstej trawy) modyfikatorom trawy na podanych obiektach."""
    for ob in obiekty:
        for md in ob.modifiers:
            if md.type == 'NODES' and md.node_group and md.node_group.name.startswith('K_trawa_GN'):
                _ustaw_wejscie(md, 'Kamera', kamera)
                ob.update_tag()
