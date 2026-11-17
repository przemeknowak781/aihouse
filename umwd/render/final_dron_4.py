# -*- coding: utf-8 -*-
"""Render finalny ujęcia „dron-4” (ogród i dziedziniec od pd.-zach., w tle Most Grunwaldzki i Odra) – nakładka na
wspólną nakładkę finałową zestawu ``render/ujecia_finalne_korekty.py`` (→ ``ujecia_poprawki_kontekstu.py`` →
``ujecia_dodatkowe.py``), bez edycji modułów wspólnych; uruchomienie i argumenty jak ``ujecia_finalne_korekty.py``::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_dron_4.py \
        --id dron-4 --szer 2000 --probki 64 --out umwd/docs/60_wizualizacje/img/extra/E_dron-4.jpg

Warunki wspólne zestawu (z ``ujecia_finalne_korekty.py``, przy budowie sceny od zera): lamele korony łuku wg v1.1,
sitodruk 30 % na szkle korony, w dzień ciepłe oprawy ×0,12; perspektywa powietrzna z klucza ``post_przed.mgla``
wpisu JSON (pass Mist).

Poprawki tego ujęcia wg uwag jurorów:

1. **Dach BIPV – lekki połysk z odbiciem nieba** (dotąd „czarna płyta”): materiał ``bipv`` (moduły szkło-szkło na
   dachach wieży i skrzydła) dostaje warstwę szkła osłonowego (coat: IOR 1,52, chropowatość 0,05 – odbicie nieba
   wg Fresnela, przy kącie patrzenia z drona ok. 53° od normalnej ~6 %), ogniwa ciemnogranatowe zamiast czarnych
   (ogniwa monokrystaliczne z powłoką AR), drobne różnice tonu i nachylenia między modułami (szum w skali modułu –
   odbicie nieba „łamie się” na polach modułów jak na zdjęciach dachów PV), jaśniejsze spoiny siatki ogniw.
   Podmiana ``Materialy.m_bipv`` przed budową sceny (zadaszenie BIPV ogrodu – ``m_bipv_szklo`` – bez zmian).
2. **Odcienie ceramiki posesji M1–M4 – kontrola** (barw NIE zmieniamy – to decyzja projektowa z ``koncepcja.json``):
   po renderze średnia barwa pikseli lica ulicznego każdej posesji (promienie przez siatkę pikseli, trafienie
   w ścianę z materiałem ``cer:Mx``) w pliku JPG → sRGB, CIELAB, ΔE76 między sąsiednimi posesjami; wynik w raporcie
   kontroli (``korekty.ceramika_posesji``) obok wartości z konwersji NCS → sRGB. Także średnia barwa dachu BIPV.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import numpy as np  # noqa: E402

import ujecia_finalne_korekty as FK  # noqa: E402  (warunki wspólne zestawu; importuje ujecia_poprawki_kontekstu)
from umwd.render import budynek3d  # noqa: E402
from umwd.render.blib import NodeBuilder  # noqa: E402

U = FK.U

# ============================================================================================== (1) BIPV
BIPV = dict(ogniwo=(0.018, 0.027, 0.056), spoina=(0.075, 0.080, 0.090), szorstkosc_ogniw=0.38,
            coat_ior=1.52, coat_szorstkosc=0.05, zmiennosc_tonu=0.30, nachylenie_bump=0.035, skala_modulu=0.55)


def _m_bipv_polysk(self, m):
    """Moduły BIPV szkło-szkło: ogniwa ciemnogranatowe pod szkłem osłonowym (coat) – odbicie nieba wg Fresnela."""
    nb = NodeBuilder(m)
    pos = nb.n('ShaderNodeNewGeometry').outputs['Position']
    sp_ = nb.n('ShaderNodeSeparateXYZ')
    nb.l(pos, sp_.inputs[0])
    mask, los, fru, _ = self._kafle(nb, 0.166, 0.166, 0.006, losowe_przes=False, przes=0.0,
                                    uv=(sp_.outputs[0], sp_.outputs[1]))
    col = nb.mix(mask, BIPV['spoina'], BIPV['ogniwo'])
    # zmienność modułów (partie ogniw): szum w skali modułu 1,70 × 1,00 m
    nm = nb.n('ShaderNodeTexNoise', Scale=BIPV['skala_modulu'], Detail=0.0)
    nb.l(pos, nm.inputs['Vector'])
    k = nb.math('ADD', 1.0 - BIPV['zmiennosc_tonu'] / 2, nb.math('MULTIPLY', nm.outputs['Fac'], BIPV['zmiennosc_tonu']))
    cc = nb.n('ShaderNodeCombineColor')
    for i in range(3):
        nb.l(k, cc.inputs[i])
    col = nb.mix(1.0, col, cc.outputs[0], blend='MULTIPLY')
    b = nb.n('ShaderNodeBsdfPrincipled', Roughness=BIPV['szorstkosc_ogniw'])
    nb.l(col, b.inputs['Base Color'])
    b.inputs['Specular IOR Level'].default_value = 0.25          # ogniwa z powłoką AR pod szkłem
    b.inputs['Coat Weight'].default_value = 1.0                  # szkło osłonowe 3,2 mm
    b.inputs['Coat IOR'].default_value = BIPV['coat_ior']
    b.inputs['Coat Roughness'].default_value = BIPV['coat_szorstkosc']
    # drobne odchyłki nachylenia tafli między modułami → odbicie nieba „łamie się” na polach
    nn = nb.n('ShaderNodeTexNoise', Scale=BIPV['skala_modulu'] * 1.3, Detail=0.0)
    nb.l(pos, nn.inputs['Vector'])
    bm = nb.n('ShaderNodeBump', Strength=BIPV['nachylenie_bump'], Distance=1.0)
    nb.l(nn.outputs['Fac'], bm.inputs['Height'])
    nb.l(bm.outputs['Normal'], b.inputs['Coat Normal'])
    nb.output(b)


budynek3d.Materialy.m_bipv = _m_bipv_polysk


# ============================================================================================== (2) kontrola barw
def _lab(rgb255):
    lin = [((c / 255.0) / 12.92) if c / 255.0 <= 0.04045 else (((c / 255.0) + 0.055) / 1.055) ** 2.4 for c in rgb255]
    r, g, b = lin
    X = 0.4124 * r + 0.3576 * g + 0.1805 * b
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    Z = 0.0193 * r + 0.1192 * g + 0.9505 * b
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(X / 0.95047), f(Y), f(Z / 1.08883)
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def _de(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def pomiar_barw(sc, jpg, krok=2):
    """Średnia barwa pikseli JPG trafiających w materiały ceramiki posesji (cer:M1…M4) i BIPV (promienie przez
    środki pikseli co ``krok`` px w obwiedni skrzydła i wieży z raportu kontroli)."""
    from PIL import Image
    im = np.asarray(Image.open(jpg).convert('RGB'), dtype=np.float64)
    H, W = im.shape[:2]
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation.copy()
    mats_cache = {}
    sumy, licz = {}, {}
    for j in range(0, H, krok):
        fy = 1.0 - (j + 0.5) / H
        for i in range(0, W, krok):
            fx = (i + 0.5) / W
            d = U._kierunek_kadru(cam, sc, fx, fy)
            hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, loc, d)
            if not hit or ob.type != 'MESH':
                continue
            key = (ob.name, idx)
            me = ob.data
            if idx >= len(me.polygons):
                continue
            mi = me.polygons[idx].material_index
            mn = me.materials[mi].name if mi < len(me.materials) and me.materials[mi] else ''
            if mn.startswith('B_cer:M'):
                k = mn.split(':')[1]
                # tylko lico uliczne (normalna ku zach.-pn.-zach., az ≈ 282°)
                az = math.degrees(math.atan2(nrm.x, nrm.y)) % 360
                if not (250 < az < 315):
                    continue
            elif mn == 'B_bipv':
                k = 'BIPV_' + ob.name
            else:
                continue
            sumy[k] = sumy.get(k, 0) + im[j, i]
            licz[k] = licz.get(k, 0) + 1
    out = {}
    for k in sorted(sumy):
        c = sumy[k] / licz[k]
        out[k] = dict(piksele_probki=licz[k], srgb=[round(float(x), 1) for x in c],
                      lab=[round(x, 1) for x in _lab(c)])
    de = {}
    for a, b in (('M1', 'M2'), ('M2', 'M3'), ('M3', 'M4')):
        if a in out and b in out:
            de['%s-%s' % (a, b)] = round(_de(out[a]['lab'], out[b]['lab']), 1)
    spec = budynek3d.Spec(str(U.KONCEPCJA))
    ncs = {}
    for k in ('M1', 'M2', 'M3', 'M4'):
        rgb = budynek3d.ncs_srgb(spec.ncs['cer_' + k])
        ncs[k] = dict(ncs=spec.ncs['cer_' + k], srgb=list(rgb), lab=[round(x, 1) for x in _lab(rgb)])
    de_ncs = {'%s-%s' % (a, b): round(_de(ncs[a]['lab'], ncs[b]['lab']), 1)
              for a, b in (('M1', 'M2'), ('M2', 'M3'), ('M3', 'M4'))}
    return dict(w_obrazie=out, dE76_sasiednie_w_obrazie=de, ncs_konwersja=ncs, dE76_sasiednie_ncs=de_ncs,
                krok_px=krok)


_ru = U.render_ujecia


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    out_jpg = Path(out_jpg)
    kor = r.setdefault('korekty', {})
    kor['bipv'] = dict(BIPV, opis='szkło osłonowe (coat) z odbiciem nieba, ogniwa ciemnogranatowe, zmienność modułów')
    if not a.kontrola_tylko and out_jpg.exists() and not FK.ARGS_EXTRA.wycinek:
        try:
            kor['ceramika_posesji'] = pomiar_barw(sc, out_jpg, krok=2 if a.szer <= 1000 else 4)
            print('[dron-4] barwy: %s' % json.dumps(kor['ceramika_posesji']['dE76_sasiednie_w_obrazie']))
        except Exception as e:      # pomiar pomocniczy – nie przerywa
            kor['ceramika_posesji'] = dict(blad=repr(e))
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p

if __name__ == '__main__':
    FK.main()
