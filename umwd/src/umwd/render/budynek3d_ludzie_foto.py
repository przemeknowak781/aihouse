# -*- coding: utf-8 -*-
"""Ludzie fotograficzni (wycinki z alfą) jako billboardy obracane do kamery – zamiast sylwetek proceduralnych.

Źródło: **Skalgubbar** (https://skalgubbar.se, Teodor Javanaud Emdén). Licencja (strona „Read me”, odczyt
17.11.2026): bezpłatnie dla każdego do ożywiania wizualizacji niezrealizowanej architektury, także komercyjnie;
architektura ma być w centrum uwagi; nie wolno używać jako samodzielnych obrazów ani w reklamie produktów; inne
użycie niż zaludnianie wizualizacji architektury nie jest objęte licencją. Pliki pobierane WYŁĄCZNIE do
``build/skalgubbar/`` (katalog ignorowany przez git) – nie są częścią repozytorium i nie są redystrybuowane.

Postać = 3 obiekty:
* płaszczyzna widoczna (obraz RGBA, rozmiar wg wysokości postaci 1,62–1,85 m), obracana do kamery wokół osi Z
  (``zwroc_do_kamery``), nie rzuca cienia;
* duplikat tylko-cieniowy, obracany prostopadle do kierunku słońca – cień z sylwetki zdjęcia;
* miękki cień kontaktowy (AO) pod stopami – elipsa z gradientem przezroczystości.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import bpy

from umwd.render.budynek3d import UMWD

KATALOG_DIR = UMWD / 'build' / 'skalgubbar'
CACHE_DIR = KATALOG_DIR / '_przyciete'

# (plik bez prefiksu, wysokość najwyższej postaci w kadrze [m], rodzaj)
KATALOG = [
    ('142_h_walking', 1.83, 'pieszy'),
    ('260_a_in_a_suit', 1.84, 'urzednik'),
    ('261_d_walking_with_bag', 1.80, 'pieszy'),
    ('262_g_watching_winter', 1.78, 'stoi'),
    ('318_a_checking_messages_in_majorna', 1.80, 'urzednik'),
    ('2_f_standing_winter', 1.68, 'stoi'),
    ('307_P_on_winter_walk', 1.70, 'pieszy'),
    ('3_a_standing_winter', 1.62, 'stoi'),
    ('44_a_standing_winter', 1.66, 'stoi'),
    ('241_d_suit_standing', 1.82, 'urzednik'),
    ('254_c_walking_stroller', 1.82, 'rodzina'),
    ('263_e_e_in_the_rain', 1.68, 'rodzina'),
    ('249_p_a_walking_wind', 1.72, 'para'),
    ('323_e_and_t_walking_to_a_restaurant', 1.74, 'para'),
    ('309_m_walking_s_the_dog', 1.75, 'pieszy'),
    ('342_m_is_winter_cycling_his_electric_bike', 1.72, 'rower'),
    ('331_g_walking_with_his_bike', 1.72, 'rower'),
    ('144_h_bike', 1.80, 'rower_prowadzi'),
]


def dostepne():
    return [k for k in KATALOG if (KATALOG_DIR / ('skalgubbar_%s.png' % k[0])).exists()]


def _obraz(nazwa, max_h=1400):
    """Przycięty do obrysu alfy i przeskalowany wycinek (cache w build/skalgubbar/_przyciete) → bpy Image."""
    from PIL import Image
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    src = KATALOG_DIR / ('skalgubbar_%s.png' % nazwa)
    dst = CACHE_DIR / ('%s.png' % nazwa)
    if not dst.exists():
        im = Image.open(src).convert('RGBA')
        im = im.crop(im.getbbox())
        if im.height > max_h:
            im = im.resize((max(1, int(im.width * max_h / im.height)), max_h), Image.LANCZOS)
        im.save(dst)
    img = bpy.data.images.get(dst.name) or bpy.data.images.load(str(dst), check_existing=True)
    img.alpha_mode = 'STRAIGHT'
    return img


def _material(nazwa, img, tryb):
    key = 'LF_%s_%s' % (tryb, nazwa)
    m = bpy.data.materials.get(key)
    if m:
        return m
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tex = nt.nodes.new('ShaderNodeTexImage')
    tex.image = img
    tex.interpolation = 'Cubic'
    tex.extension = 'CLIP'
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(tex.outputs['Alpha'], mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    if tryb == 'cien':
        d = nt.nodes.new('ShaderNodeBsdfDiffuse')
        d.inputs['Color'].default_value = (0.05, 0.05, 0.05, 1)
        nt.links.new(d.outputs[0], mix.inputs[2])
    else:
        # zdjęcie ma własne światło: rozproszenie + część przeświecająca (strona w cieniu nie gaśnie do czerni)
        b = nt.nodes.new('ShaderNodeBsdfPrincipled')
        b.inputs['Roughness'].default_value = 0.85
        b.inputs['Specular IOR Level'].default_value = 0.2
        nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
        tl = nt.nodes.new('ShaderNodeBsdfTranslucent')
        nt.links.new(tex.outputs['Color'], tl.inputs['Color'])
        m2 = nt.nodes.new('ShaderNodeMixShader')
        m2.inputs['Fac'].default_value = 0.35
        nt.links.new(b.outputs[0], m2.inputs[1])
        nt.links.new(tl.outputs[0], m2.inputs[2])
        nt.links.new(m2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m


def _material_ao():
    m = bpy.data.materials.get('LF_kontakt_ao')
    if m:
        return m
    m = bpy.data.materials.new('LF_kontakt_ao')
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['UV'], sep.inputs[0])

    def M(op, a, b=None):
        n = nt.nodes.new('ShaderNodeMath')
        n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs[0]
    dx = M('SUBTRACT', sep.outputs[0], 0.5)
    dy = M('SUBTRACT', sep.outputs[1], 0.5)
    r = M('MULTIPLY', M('SQRT', M('ADD', M('MULTIPLY', dx, dx), M('MULTIPLY', dy, dy))), 2.0)
    a = M('MULTIPLY', M('POWER', M('MAXIMUM', M('SUBTRACT', 1.0, r), 0.0), 2.0), 0.55)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    d = nt.nodes.new('ShaderNodeBsdfDiffuse')
    d.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1)
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(a, mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(d.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m


def _plaszczyzna(nazwa, w, h, lustro=False):
    """Płaszczyzna w lokalnym XZ (szer. w, wys. h), podstawa w (0,0,0), front w stronę −Y; UV 0–1."""
    me = bpy.data.meshes.new(nazwa)
    V = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, 0, h), (-w / 2, 0, h)]
    me.from_pydata(V, [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UVMap')
    u0, u1 = (1.0, 0.0) if lustro else (0.0, 1.0)
    for li, (u, v) in enumerate(((u0, 0), (u1, 0), (u1, 1), (u0, 1))):
        uv.data[li].uv = (u, v)
    return me


def postac(coll, wpis, poz, z, nazwa, rng=None, lustro=None, skala=1.0):
    """Tworzy postać fotograficzną (płaszczyzna + cień + AO) w punkcie (e, n) na wysokości z (w scenie)."""
    rng = rng or np.random.default_rng(0)
    plik, H, rodzaj = wpis
    img = _obraz(plik)
    w_px, h_px = img.size
    H = H * skala * rng.uniform(0.97, 1.03)
    W = H * w_px / h_px
    if lustro is None:
        lustro = bool(rng.random() < 0.5)
    me = _plaszczyzna(nazwa, W, H, lustro)
    me.materials.append(_material(plik, img, 'foto'))
    ob = bpy.data.objects.new(nazwa, me)
    ob.location = (float(poz[0]), float(poz[1]), float(z))
    ob.visible_shadow = False
    ob['billboard'] = 'kamera'
    coll.objects.link(ob)
    mc = me.copy()
    mc.materials.clear()
    mc.materials.append(_material(plik, img, 'cien'))
    oc = bpy.data.objects.new(nazwa + '_cien', mc)
    oc.location = ob.location
    oc.visible_camera = False
    oc.visible_diffuse = False
    oc.visible_glossy = False
    oc.visible_transmission = False
    oc.visible_volume_scatter = False
    oc['billboard'] = 'slonce'
    coll.objects.link(oc)
    # cień kontaktowy (elipsa 0,9 × 0,45 m, dla rowerów/wózków dłuższa)
    dl = 1.9 if rodzaj in ('rower', 'rower_prowadzi', 'rodzina') else 0.9
    ma = bpy.data.meshes.new(nazwa + '_ao')
    ma.from_pydata([(-dl / 2, -0.25, 0), (dl / 2, -0.25, 0), (dl / 2, 0.25, 0), (-dl / 2, 0.25, 0)], [], [(0, 1, 2, 3)])
    uv = ma.uv_layers.new(name='UVMap')
    for li, (u, v) in enumerate(((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[li].uv = (u, v)
    ma.materials.append(_material_ao())
    oa = bpy.data.objects.new(nazwa + '_ao', ma)
    oa.location = (float(poz[0]), float(poz[1]), float(z) + 0.006)
    oa.visible_shadow = False
    oa.visible_diffuse = False
    oa.visible_glossy = False
    oa['billboard'] = 'kamera_ao'
    coll.objects.link(oa)
    return ob


def zwroc_do_kamery(cam_loc, az_slonca_siatki=None):
    """Obraca billboardy: płaszczyzny widoczne i AO – frontem do kamery (wokół Z), cieniowe – prostopadle do słońca."""
    n = 0
    for ob in bpy.data.objects:
        t = ob.get('billboard')
        if not t:
            continue
        if t in ('kamera', 'kamera_ao'):
            dx, dy = cam_loc[0] - ob.location.x, cam_loc[1] - ob.location.y
        elif az_slonca_siatki is not None:
            a = math.radians(az_slonca_siatki)
            dx, dy = math.sin(a), math.cos(a)
        else:
            continue
        ob.rotation_euler = (0.0, 0.0, math.atan2(dx, -dy))
        n += 1
    return n


def wybierz(rng, rodzaje=None):
    kat = dostepne()
    if rodzaje:
        k2 = [k for k in kat if k[2] in rodzaje]
        kat = k2 or kat
    return kat[int(rng.integers(len(kat)))] if kat else None
