# -*- coding: utf-8 -*-
"""Wizualizacje 1 i 2 NA ZDJĘCIACH F.17.A / F.17.B (wymóg R-110): render budynku + łapacz cieni, kompozycja na zdjęciu.

Potok (jedna scena, trzy rendery tej samej kamery z ``model/kamery_F17.json``):

1. **render główny** (Cycles, EXR liniowe): budynek z ``budynek3d`` (bez zagospodarowania – poza obrysem budynku na
   zdjęciu zostaje stan istniejący); kontekst w stanie istniejącym (``obszar_inwestycji='istniejacy'``) jako
   **Shadow Catcher** – teren, woda, budynki, most przyjmują cień i AO nowego budynku i zasłaniają go tam, gdzie
   stoją przed nim; drzewa kontekstu rzucają cień, ale są niewidoczne dla kamery. Słońce i niebo dla czasu
   zdjęcia (29.10.2025 11:38 / 11:57:36 CET), passy: Combined (RGBA) i Shadow Catcher;
2. **maski** (2 próbki, materiał emisyjny): sylwetka samego budynku oraz sylwetka zasłonięta przez drzewa
   (holdout) → obszar, w którym drzewa stoją PRZED budynkiem;
3. **kompozycja (numpy)**: zdjęcie (liniowo) × pass cienia + render budynku; przesłonięcia pierwszego planu
   wzięte ze zdjęcia: piksele roślinności (maska barwna) w poszerzonym obszarze drzew-zastępników przed budynkiem;
   dopasowanie tonalne budynku do zdjęcia (ekspozycja z percentyla, nasycenie jak w obróbce zdjęć +17…24, czerń,
   mgiełka, wyostrzenie po upscalingu, ziarno); na koniec wspólny „look” (``tools/postprodukcja.py``, preset lot).

Rendery próbne: ``--skala 0.333`` (1/3 rozdzielczości pliku). Wynik: ``docs/60_wizualizacje/img/W1_F17A_test.jpg``,
``W2_F17B_test.jpg`` (+ wycinek kontrolny w ``build/fotomatch/``).

Uruchomienie::

    /home/user/aihouse/.venv-render/bin/python -I /home/user/aihouse/umwd/render/fotomatch_F17.py --zdjecie A [--skala 0.333] [--probki 64]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

UMWD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UMWD / 'src'))
sys.path.insert(0, str(UMWD / 'tools'))

import numpy as np  # noqa: E402
import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from PIL import Image, ImageFilter  # noqa: E402
from shapely.geometry import Point  # noqa: E402

from umwd.render import blib, context, budynek3d  # noqa: E402

KAMERY = UMWD / 'model' / 'kamery_F17.json'
OUT_IMG = UMWD / 'docs' / '60_wizualizacje' / 'img'
BUILD = UMWD / 'build' / 'fotomatch'
WYNIK = {'A': 'W1_F17A_test.jpg', 'B': 'W2_F17B_test.jpg'}
WYNIK_FINAL = {'A': 'W1_F17A_final.jpg', 'B': 'W2_F17B_final.jpg'}
# proporcje pól na planszach (tools/plansze_etap2.py): W1 578 × 340 mm, W2 366 × 206 mm – kadr przycinany do pola
PROPORCJE_POLA = {'A': 578 / 340, 'B': 366 / 206}

# dopasowanie tonalne CG do zdjęcia (zdjęcia: Dehaze +24/+29, Saturation +17/+24, Vibrance +7/+9, Shadows +50)
GRADING = {
    # cien_min – jasność pełnego cienia względem słońca na zdjęciu (obróbka Shadows +50 rozjaśnia cienie; pomiar
    # na cieniach istniejących budynków ≈ 0,40–0,45); cien_barwa – ile chłodnej barwy cienia z passu zachować
    # kontakt – siła cienia kontaktowego u podstawy (pod sylwetką budynku), ułamek
    'A': dict(p_jasne=0.92, cel_jasne=0.76, nasycenie=1.10, czern=0.0, mgla=0.03, mgla_kolor=(0.70, 0.76, 0.84),
              wyostrz=70, klarownosc=45, ziarno=0.012, cien_min=0.42, cien_barwa=0.35, kontakt=0.25),
    # B (uwagi koordynatora 17.11): elewacja zbyt czysta i ostra względem sąsiadów w tej odległości – mniej nasycenia,
    # więcej mgiełki, łagodniejsze wyostrzenie; cień mocniejszy (cień na trawniku na zdjęciu ≈ 0,34 słońca);
    # cień kontaktowy u podstawy (budynek nie „pływa” nad trawnikiem i chodnikiem)
    'B': dict(p_jasne=0.92, cel_jasne=0.80, nasycenie=0.96, czern=0.0, mgla=0.07, mgla_kolor=(0.72, 0.78, 0.85),
              wyostrz=35, klarownosc=20, ziarno=0.012, cien_min=0.34, cien_barwa=0.35, kontakt=0.40),
}

# postaci CG przy budynku (ok. 5–15 px w pełnej rozdzielczości – sylwetki z budynek3d_otoczenie): B – chodnik przy
# licu ulicznym skrzydła i brama ogrodowa; A – plac przed Bramą Mostową i chodnik przy segmencie
LUDZIE_FM = {
    'B': dict(lico=((48.84, 9.68), (61.25, 66.05)), s=(0.08, 0.18, 0.27, 0.33, 0.47, 0.58, 0.66, 0.80, 0.90),
              odsuniecie=(1.6, 2.6)),
    'A': dict(lico=((115.98, 39.93), (113.48, 50.18)), s=(0.15, 0.45, 0.62, 0.85), odsuniecie=(1.5, 2.5),
              luk=((12.0, 16.0), (24.0, 15.4), (31.0, 17.5), (52.0, 16.2), (66.0, 15.8), (78.0, 18.0))),
}


def ludzie_fotomatch(B, kon, zdjecie):
    """Kilka sylwetek przy budynku (widoczne w renderze CG, rzucają cień na łapacz cieni)."""
    from umwd.render import budynek3d_otoczenie as oto
    L = LUDZIE_FM.get(zdjecie)
    if not L:
        return 0
    ctx = kon['ctx']
    rng = np.random.default_rng(17)
    mat = B.mat('ludzie')
    proto = []
    for i, (H, chod, pl, kob, tb, pz) in enumerate(((1.80, 0.30, 0.40, False, False, ''), (1.66, 0.28, 0.36, True, True, ''),
                                                    (1.74, 0.0, 0.50, False, False, 'kieszen'),
                                                    (1.62, 0.0, 0.36, True, False, 'telefon'))):
        me = oto._prototyp_czlowieka('fm_czlowiek_%d' % i, H, chod, pl, kob, seed=60 + i, torba=tb, poza=pz)
        me.materials.append(mat)
        proto.append(me)
    poz = []
    a, b = np.array(L['lico'][0]), np.array(L['lico'][1])
    t = (b - a) / np.linalg.norm(b - a)
    n = np.array([-t[1], t[0]])
    if B.foot.contains(Point(*((a + b) / 2 + n * 1.0))):
        n = -n
    for f in L['s']:
        poz.append((a + (b - a) * f + n * rng.uniform(*L['odsuniecie']), t if rng.random() < 0.5 else -t))
    if 'luk' in L:
        cx, cy = B.spec.luk['srodek']
        for kat, rr in L['luk']:
            pk = np.subtract(B.spec.z_uv(26.0 + 14.0 * math.cos(math.radians(kat)), 15.7 + 14.0 * math.sin(math.radians(kat))),
                             (cx, cy))
            q = np.array([cx, cy]) + pk / 14.0 * rr
            poz.append((q, -pk / 14.0))
    for i, (p, kier) in enumerate(poz):
        ob = bpy.data.objects.new('fm_czlowiek_%02d' % i, proto[i % len(proto)])
        B.kol['zagospodarowanie_bliskie'].objects.link(ob)
        ob.location = (float(p[0]), float(p[1]), float(ctx.teren.z1(p[0], p[1])) + 0.03)
        ob.rotation_euler = (0, 0, math.atan2(kier[1], kier[0]) - math.pi / 2 + rng.normal(0, 0.3))
    return len(poz)


def srgb_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_srgb(x):
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def wczytaj_exr(p):
    im = bpy.data.images.load(str(p))
    im.colorspace_settings.name = 'Non-Color'
    a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], 4)[::-1]
    bpy.data.images.remove(im)
    return a


def ustaw_kamere(sc, kam, skala):
    bl = kam['blender']
    cd = bpy.data.cameras.new('F17')
    cd.type = 'PERSP'
    cd.sensor_fit = bl['sensor_fit']
    cd.sensor_width = bl['sensor_width_mm']
    cd.lens = bl['lens_mm']
    cd.shift_x, cd.shift_y = bl['shift_x'], bl['shift_y']
    cd.clip_start, cd.clip_end = bl['clip_start'], bl['clip_end']
    ob = bpy.data.objects.new('F17', cd)
    sc.collection.objects.link(ob)
    ob.location = bl['location_z_wzgl_0']
    ob.rotation_mode = 'XYZ'
    ob.rotation_euler = bl['rotation_euler_XYZ_rad']
    sc.camera = ob
    W, H = bl['rozdzielczosc']
    sc.render.resolution_x, sc.render.resolution_y = int(round(W * skala)), int(round(H * skala))
    sc.render.resolution_percentage = 100
    return ob


def obszar_renderu(sc, cam, B, el, az, margines=0.04):
    """Ramka renderu (border) obejmująca budynek i jego cień na terenie (rzut narożników i ich cieni)."""
    pts = []
    zt = B.spec.dach['W']['attyka'] + B.DZ
    kier = np.array([math.sin(math.radians(az)), math.cos(math.radians(az))])
    dl = 1.0 / max(math.tan(math.radians(el)), 0.05)
    for k, P in B.poly.items():
        zk = B.spec.dach[k]['attyka'] + B.DZ
        for x, y in list(P.exterior.coords):
            pts.append((x, y, -1.0))
            pts.append((x, y, zk))
            s = np.array([x, y]) - kier * zk * dl
            pts.append((s[0], s[1], -1.0))
    uv = np.array([world_to_camera_view(sc, cam, Vector(p))[:2] for p in pts])
    x0, y0 = np.clip(uv.min(0) - margines, 0, 1)
    x1, y1 = np.clip(uv.max(0) + margines, 0, 1)
    return float(x0), float(x1), float(y0), float(y1)


def kompozytor(sc, katalog, prefix):
    """Węzły kompozytora (CPU): zapis passów Combined i Shadow Catcher do EXR 32-bit."""
    sc.render.use_compositing = True
    sc.render.compositor_device = 'CPU'
    ng = bpy.data.node_groups.new('Komp_' + prefix, 'CompositorNodeTree')
    sc.compositing_node_group = ng
    rl = ng.nodes.new('CompositorNodeRLayers')
    fo = ng.nodes.new('CompositorNodeOutputFile')
    fo.directory = str(katalog) + '/'
    fo.file_name = prefix
    fo.format.media_type = 'IMAGE'
    fo.format.file_format = 'OPEN_EXR'
    fo.format.color_depth = '32'
    fo.file_output_items.new('RGBA', 'kolor')
    ng.links.new(rl.outputs['Image'], fo.inputs['kolor'])
    if 'Shadow Catcher' in rl.outputs:
        fo.file_output_items.new('RGBA', 'cien')
        ng.links.new(rl.outputs['Shadow Catcher'], fo.inputs['cien'])
    return ng


# próbki do kalibracji tonalnej: elewacja sąsiada o tej samej orientacji i w tym samym oświetleniu (zdjęcie)
# oraz odpowiadająca jej elewacja budynku (render). Punkty 3D: (e, n) końce lica, zakres Z (= H − 119,25).
KALIBRACJA = {
    # F.17.B: front Mazowieckiej 19 (cień, elewacja zach.) ↔ front skrzydła przy Mazowieckiej (ta sama płaszczyzna)
    'B': dict(ref=((48.84, 9.68), (44.64, -8.38), (0.25, 0.75), (4.0, 14.0)),
              cg=((48.84, 9.68), (61.25, 66.05), (0.06, 0.20), (6.0, 15.0)), wspolczynnik=1.00,
              # lico w słońcu: elewacja pd. wieży nad skrzydłem → jasność jasnej elewacji w słońcu na zdjęciu
              # (Urząd Wojewódzki ≈ 217/209/196, luma ≈ 0,82; ceramika/granit nieco jaśniejsze)
              cg_slonce=((74.61, 40.76), (113.47, 50.23), (0.12, 0.45), (22.0, 34.0)), cel_slonce=0.84),
    # F.17.A: front Wybrzeża Słowackiego 5 (cień, elewacja wsch.) ↔ elewacja wsch. segmentu (ten sam porządek)
    'A': dict(ref=((118.55, 11.5), (118.25, 28.5), (0.2, 0.8), (4.0, 15.0)),
              cg=((115.98, 39.93), (113.48, 50.18), (0.15, 0.85), (6.0, 18.0)), wspolczynnik=0.92),
}


def probka_pikseli(sc, cam, spec, W, H):
    """Wielokąt (piksele) obejmujący rzut fragmentu lica: spec = (p0, p1, (f0, f1), (z0, z1))."""
    from shapely.geometry import MultiPoint
    p0, p1, (f0, f1), (z0, z1) = spec
    pts = []
    for f in np.linspace(f0, f1, 6):
        x = p0[0] + (p1[0] - p0[0]) * f
        y = p0[1] + (p1[1] - p0[1]) * f
        for z in np.linspace(z0, z1, 5):
            c = world_to_camera_view(sc, cam, Vector((x, y, z)))
            pts.append((c.x * W, (1 - c.y) * H))
    return MultiPoint(pts).convex_hull


def maska_wielokata(poly, W, H):
    from PIL import ImageDraw
    m = Image.new('L', (W, H), 0)
    if poly.geom_type == 'Polygon':
        ImageDraw.Draw(m).polygon(list(poly.exterior.coords), fill=255)
    return np.asarray(m) > 0


def maska_roslinnosci(foto_srgb):
    """Miękka maska roślinności na zdjęciu (jesienne korony: żółte, pomarańczowe, zielone, rdzawe; cienie koron)."""
    import colorsys  # noqa: F401
    a = foto_srgb
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    sat = (mx - mn) / np.maximum(mx, 1e-4)
    # odcień: zieleń/żółć/pomarańcz – g lub r dominuje nad b
    ciepl = np.clip(((r + g) * 0.5 - b) * 4.0, 0, 1)
    m = np.clip((sat - 0.22) / 0.18, 0, 1) * ciepl
    # ciemna zieleń/cień korony: niska jasność i g ≥ b
    ciemne = np.clip((0.22 - mx) / 0.12, 0, 1) * np.clip((g - b) * 8.0, 0, 1)
    return np.clip(np.maximum(m, ciemne * 0.8), 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--zdjecie', choices=['A', 'B'], required=True)
    ap.add_argument('--skala', type=float, default=1 / 3)
    ap.add_argument('--probki', type=int, default=64)
    ap.add_argument('--bez-postprodukcji', action='store_true')
    ap.add_argument('--final', action='store_true', help='wersja finalna: pełna rozdzielczość zdjęcia, *_final.jpg')
    ap.add_argument('--bez-kadrowania', action='store_true', help='bez przycięcia do proporcji pola planszy')
    a = ap.parse_args()
    t0 = time.time()
    K = json.load(open(KAMERY, encoding='utf-8'))
    kam = K['kamery'][a.zdjecie]
    BUILD.mkdir(parents=True, exist_ok=True)
    pre = 'F17%s_' % a.zdjecie
    sc = blib.reset()
    kon = context.build_context(sc, {'pora_roku': 'jesien', 'obszar_inwestycji': 'istniejacy', 'trawa_3d': False,
                                     'dalsze': False})
    bud = budynek3d.build_building(sc, {'kontekst': kon, 'zagospodarowanie': False, 'ludzie': False})
    B = bud['budynek']
    n_ludzi = ludzie_fotomatch(B, kon, a.zdjecie)
    t_bud = time.time() - t0
    # ---- kontekst: łapacz cieni (teren, woda, budynki, most, ulica); drzewa – tylko cień
    drzewa, inne = [], []
    for ob in kon['kolekcje'].values():
        for o in ob.all_objects:
            if o.instance_type == 'COLLECTION':
                drzewa.append(o)
            elif o.type == 'MESH':
                inne.append(o)
    for o in inne:
        o.is_shadow_catcher = True
    for o in drzewa:
        # drzewa istniejące są już na zdjęciu (z cieniami) – w renderze głównym niewidoczne i bez cienia
        o.visible_camera = False
        o.visible_glossy = False
        o.visible_shadow = False
    if a.final:
        a.skala = 1.0                                  # pełna rozdzielczość pliku zdjęcia
    cam = ustaw_kamere(sc, kam, a.skala)
    bpy.context.view_layer.update()
    sw = budynek3d.swiatlo_dzienne(sc, kam['exif']['czas'], chmury=0)
    blib.render_settings(sc, sc.render.resolution_x, sc.render.resolution_y, samples=a.probki, adaptive=0.02,
                         exposure=0.0, transparent=True, max_bounces=8, clamp_indirect=8.0)
    sc.view_settings.view_transform = 'Standard'
    sc.view_layers[0].cycles.use_pass_shadow_catcher = True
    sc.cycles.transparent_max_bounces = 24
    x0, x1, y0, y1 = obszar_renderu(sc, cam, B, sw['el'], sw['az'] + 0.738)
    sc.render.use_border = True
    sc.render.use_crop_to_border = False
    sc.render.border_min_x, sc.render.border_max_x = x0, x1
    sc.render.border_min_y, sc.render.border_max_y = y0, y1
    print('[foto] %s: %d×%d, ramka x %.3f–%.3f y %.3f–%.3f, słońce az %.1f el %.1f' % (
        a.zdjecie, sc.render.resolution_x, sc.render.resolution_y, x0, x1, y0, y1, sw['az'], sw['el']))
    # ---- render główny
    kompozytor(sc, BUILD, pre + 'glowny_')
    sc.render.filepath = str(BUILD / (pre + 'glowny.png'))
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    t_r = time.time() - t1
    # ---- maski (emisja, 2 próbki): sam budynek; budynek zasłonięty przez drzewa (holdout)
    em = bpy.data.materials.new('maska_em')
    em.use_nodes = True
    nt = em.node_tree
    nt.nodes.clear()
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Strength'].default_value = 1.0
    o_ = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(e.outputs[0], o_.inputs['Surface'])
    sc.view_layers[0].material_override = em
    sc.cycles.samples = 2
    sc.cycles.use_denoising = False
    sc.view_layers[0].cycles.use_pass_shadow_catcher = False
    for o in inne:
        o.hide_render = True
    for o in drzewa:
        o.visible_camera = True
        o.is_holdout = True
    kompozytor(sc, BUILD, pre + 'maskaT_')
    bpy.ops.render.render(write_still=False)
    for o in drzewa:
        o.hide_render = True
    kompozytor(sc, BUILD, pre + 'maskaB_')
    bpy.ops.render.render(write_still=False)
    t_m = time.time() - t1 - t_r
    # ---- kompozycja
    G = GRADING[a.zdjecie]
    kol = wczytaj_exr(BUILD / (pre + 'glowny_kolor.exr'))
    cien = wczytaj_exr(BUILD / (pre + 'glowny_cien.exr'))[..., :3]
    mT = wczytaj_exr(BUILD / (pre + 'maskaT_kolor.exr'))[..., 3]
    mB = wczytaj_exr(BUILD / (pre + 'maskaB_kolor.exr'))[..., 3]
    Hh, Ww = kol.shape[:2]
    foto = Image.open(UMWD / kam['zdjecie']).convert('RGB').resize((Ww, Hh), Image.LANCZOS)
    f_s = np.asarray(foto, dtype=np.float32) / 255.0
    f_l = srgb_lin(f_s)
    alfa = np.clip(kol[..., 3], 0, 1)
    # drzewa przed budynkiem: zastępniki → poszerzenie → przecięcie z roślinnością na zdjęciu
    drz = np.clip(mB - mT, 0, 1) * (alfa > 0.02)
    r_dil = max(2, int(round(Ww / 450)))
    md = Image.fromarray((drz * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * r_dil + 1))
    md = md.filter(ImageFilter.GaussianBlur(r_dil * 0.6))
    drz_d = np.asarray(md, dtype=np.float32) / 255.0
    veg = maska_roslinnosci(f_s)
    veg = np.asarray(Image.fromarray((veg * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8)),
                     dtype=np.float32) / 255.0
    zasl = np.clip(drz_d * veg * 1.15, 0, 1)
    a_cg = alfa * (1.0 - zasl)
    # cień nowego budynku na zdjęciu (pass Shadow Catcher, gęstość dopasowana)
    sc_ = np.clip(cien, 1e-3, 1.0)
    s_l = np.clip(lum(sc_), 1e-3, 1.0)[..., None]
    s_n = G['cien_min'] + (1.0 - G['cien_min']) * s_l
    sc_ = s_n * (sc_ / s_l) ** G['cien_barwa']
    # poza ramką renderu pass cienia = 0 → bez zmian zdjęcia
    ramka = np.zeros((Hh, Ww), bool)
    ramka[int((1 - y1) * Hh):int((1 - y0) * Hh) + 1, int(x0 * Ww):int(x1 * Ww) + 1] = True
    sc_ = np.where(ramka[..., None], sc_, 1.0)
    # cień kontaktowy: pod dolną krawędzią sylwetki budynku (styk z chodnikiem/trawnikiem) – suma przesunięć maski
    # w dół z wagą wykładniczą, tylko poza budynkiem i w ramce renderu (wiersz 0 = góra obrazu)
    if G.get('kontakt', 0.0) > 0:
        N = max(3, int(round(Hh * 0.004)))
        acc = np.zeros((Hh, Ww), np.float32)
        wsum = 0.0
        for k_ in range(1, N + 1):
            w_ = math.exp(-k_ / (0.45 * N))
            acc[k_:, :] += w_ * alfa[:-k_, :]
            wsum += w_
        kont = np.clip(acc / wsum, 0, 1) * (1.0 - alfa) * ramka
        sc_ = sc_ * (1.0 - G['kontakt'] * kont)[..., None]
    tlo_l = f_l * sc_
    # budynek: kolor prosty, ekspozycja z percentyla jasnych powierzchni, nasycenie, czerń, mgiełka
    rgb = kol[..., :3] / np.maximum(alfa[..., None], 1e-4)
    sel = alfa > 0.98
    gain, wb, k_kompr = 1.0, np.ones(3, np.float32), 0.0
    kal = KALIBRACJA.get(a.zdjecie)
    m_ref = maska_wielokata(probka_pikseli(sc, cam, kal['ref'], Ww, Hh), Ww, Hh)
    m_cg = maska_wielokata(probka_pikseli(sc, cam, kal['cg'], Ww, Hh), Ww, Hh) & sel
    if m_ref.sum() > 100 and m_cg.sum() > 100:
        ref_l = float(np.quantile(lum(f_s)[m_ref], 0.70))          # sRGB zdjęcia – lico ściany (bez okien)
        cg_l = float(np.quantile(lum(rgb)[m_cg], 0.70))            # liniowo renderu – lico ściany
        cel = min(0.90, ref_l * kal['wspolczynnik'])
        gain = float(srgb_lin(np.array(cel)) / max(cg_l, 1e-6))
        # krzywa dwupunktowa y = t/(1 + k·t), t = g·x (cienie liniowe, światła kompresowane jak w obróbce zdjęcia):
        # lico w cieniu → cel (sąsiad), lico w słońcu → cel_slonce; bez próbki słońca k = 0 (sama ekspozycja)
        k_kompr = 0.0
        y_s = float(srgb_lin(np.array(cel)))
        if 'cg_slonce' in kal:
            m_s = maska_wielokata(probka_pikseli(sc, cam, kal['cg_slonce'], Ww, Hh), Ww, Hh) & sel
            if m_s.sum() > 100:
                cs_l = float(np.quantile(lum(rgb)[m_s], 0.70))
                y_h = float(srgb_lin(np.array(kal['cel_slonce'])))
                r_, q_ = cs_l / cg_l, y_h / y_s
                if r_ > q_ * 1.02:
                    k_kompr = (r_ - q_) / (y_h * (r_ - 1.0))
        gain = y_s / (cg_l * max(1.0 - k_kompr * y_s, 0.05))
        # balans bieli: barwa sąsiada (zdjęcie, liniowo) vs barwa lica budynku (render) – częściowo (60 %)
        r_ref = f_l[m_ref].mean(0)
        r_cg = rgb[m_cg].mean(0)
        wb = ((r_ref / lum(r_ref[None])[0]) / (r_cg / lum(r_cg[None])[0])) ** 0.6
        wb = (wb / lum(wb[None])[0])
        wb = np.clip(wb, 0.92, 1.08).astype(np.float32)          # tylko lekka korekta barwy
        print('[foto] kalibracja: sąsiad sRGB %.3f → cel %.3f; gain %.4f, k %.3f; WB %s' % (ref_l, cel, gain, k_kompr,
                                                                                    np.round(wb, 3)))
    elif Lc_ok := (lum(rgb)[sel].size > 200):
        pj = np.quantile(lum(rgb)[sel], G['p_jasne'])
        gain = float(srgb_lin(np.array(G['cel_jasne'])) / max(pj, 1e-5))
    t = rgb * gain * wb
    Lt = np.maximum(lum(t), 1e-6)[..., None]
    cg = lin_srgb(t / (1.0 + k_kompr * Lt))
    Lg = lum(cg)[..., None]
    cg = Lg + (cg - Lg) * G['nasycenie']
    cg = G['czern'] + cg * (1.0 - G['czern'])
    cg = cg * (1 - G['mgla']) + np.array(G['mgla_kolor'], np.float32) * G['mgla']
    cg = np.clip(cg, 0, 1)
    tlo = lin_srgb(tlo_l)
    wyn = cg * a_cg[..., None] + tlo * (1.0 - a_cg[..., None])
    img = Image.fromarray((np.clip(wyn, 0, 1) * 255 + 0.5).astype(np.uint8))
    # wyostrzenie i ziarno tylko w obszarze CG (zdjęcie jest już wyostrzone po upscalingu)
    ost = img.filter(ImageFilter.UnsharpMask(radius=max(3, Ww / 400), percent=G['klarownosc'], threshold=2))
    ost = ost.filter(ImageFilter.UnsharpMask(radius=1.2, percent=G['wyostrz'], threshold=1))
    ost_a = np.asarray(ost, dtype=np.float32) / 255.0
    rng = np.random.default_rng(5)
    ost_a = ost_a + rng.normal(0, G['ziarno'], (Hh, Ww, 1)).astype(np.float32)
    m3 = a_cg[..., None]
    wyn2 = ost_a * m3 + (np.asarray(img, dtype=np.float32) / 255.0) * (1 - m3)
    img = Image.fromarray((np.clip(wyn2, 0, 1) * 255 + 0.5).astype(np.uint8))
    surowy = BUILD / (pre + 'kompozycja.png')
    img.save(surowy)
    # wycinek kontrolny 1:1 (obszar budynku)
    xs = int(x0 * Ww), int(x1 * Ww)
    ys = int((1 - y1) * Hh), int((1 - y0) * Hh)
    img.crop((xs[0], ys[0], xs[1], ys[1])).save(BUILD / (pre + 'wycinek.jpg'), quality=90)
    # kadrowanie do proporcji pola planszy (środek na budynku, w granicach zdjęcia)
    kadr = [0, 0, Ww, Hh]
    if not a.bez_kadrowania:
        pr = PROPORCJE_POLA[a.zdjecie]
        cx, cy = (xs[0] + xs[1]) / 2, (ys[0] + ys[1]) / 2
        if Ww / Hh > pr:
            w2 = int(round(Hh * pr))
            l0 = int(min(max(cx - w2 / 2, 0), Ww - w2))
            kadr = [l0, 0, l0 + w2, Hh]
        else:
            h2 = int(round(Ww / pr))
            t0 = int(min(max(cy - h2 / 2, 0), Hh - h2))
            kadr = [0, t0, Ww, t0 + h2]
        img = img.crop(tuple(kadr))
    if not a.bez_postprodukcji:
        import postprodukcja
        img = postprodukcja.process(img, postprodukcja.PRESETS['lot'])
    out = OUT_IMG / (WYNIK_FINAL if a.final else WYNIK)[a.zdjecie]
    q = 93 if a.final else 92
    while True:
        img.save(out, quality=q, optimize=True)
        if a.final or out.stat().st_size <= 1_500_000 or q < 60:
            break
        q -= 5
    raport = dict(zdjecie=a.zdjecie, rozdzielczosc=[Ww, Hh], skala=a.skala, probki=a.probki, slonce=sw,
                  ramka=[x0, x1, y0, y1], ekspozycja_gain=float(gain), balans_bieli=[float(x) for x in wb],
                  czas_budowy_s=round(t_bud, 1),
                  czas_renderu_s=round(t_r, 1), czas_masek_s=round(t_m, 1), wynik=str(out),
                  udzial_zaslon_drzew=float((zasl * alfa).sum() / max(alfa.sum(), 1)), kadr_px=kadr,
                  ludzie_cg=n_ludzi)
    (BUILD / (pre + 'raport.json')).write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding='utf-8')
    print('[foto]', json.dumps(raport, ensure_ascii=False))


if __name__ == '__main__':
    main()
