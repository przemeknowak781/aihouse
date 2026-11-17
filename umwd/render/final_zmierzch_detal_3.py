# -*- coding: utf-8 -*-
"""Render finalny ujęcia „zmierzch-detal-3” (Żabie ujęcie – dziób łuku i latarnia) – nakładka na
``render/final_zmierzch_detal_1.py`` (siła nieba, ciepłe oprawy, pomiar luminancji, ludzie w kadrze) → wspólna nakładka
finałowa ``render/ujecia_finalne_korekty.py`` (lamele korony łuku v1.1, sitodruk) → ``ujecia_poprawki_kontekstu.py`` →
``ujecia_dodatkowe.py``. Pliki wspólne nieruszane; uruchomienie i argumenty jak ``ujecia_finalne_korekty.py``::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_zmierzch_detal_3.py \
        --id zmierzch-detal-3 --szer 2000 --probki 64 \
        --out umwd/docs/60_wizualizacje/img/extra/E_zmierzch-detal-3.jpg

Klucze wpisu JSON obsługiwane dodatkowo przez tę nakładkę (opcjonalne):

* ``"winieta": {"ev": 0.30, "d0": 0.60, "d1": 1.42, "srodek_y": 0.55, "dol_ev": 0.40, "dol_zasieg": 0.30}`` – krok
  przed ``tools/postprodukcja.py`` (na surowym PNG, w świetle liniowym): delikatna winieta eliptyczna (spadek do
  ``ev`` EV przy odległości ``d1`` od środka kadru, od ``d0``; środek na wysokości ``srodek_y`` od dołu) i lekkie
  przyciemnienie dolnej krawędzi (``dol_ev`` EV przy krawędzi, zanik smoothstep do ``dol_zasieg`` wysokości kadru) –
  wzrok idzie w górę ku koronie. Surowy PNG zostaje jako ``<plik>_surowy.png``. Preset ``zmierzch`` dokłada swoją
  słabą winietę (0,12). ``"niebo_ev": -0.6`` – filtr połówkowy z maską nieba (piksele bez trafienia: pass Mist = 1
  i Object Index = 0, krawędź rozmyta 0,8 px): niebo przyciemnione o podaną liczbę EV, budynek (z odbiciami nieba
  w szkle) bez zmian – ekspozycja ustawiona na elewację, niebo zostaje granatowe (odpowiednik filtra ND grad).
* raport (zawsze): ``latarnie_w_kadrze`` – rzut obwiedni latarń ulicznych (``latarnia_*``) na kadr (czy głowica
  wchodzi w kadr, najwyższy punkt obwiedni w kadrze); ``pomiar_zd3`` – różnice EV elewacji (ceramika, granit, okna
  biur) względem szkła korony, gradient nieba (pas przy górnej krawędzi vs pas tuż nad attyką), barwa nieba sRGB.
"""
from __future__ import annotations

import json
import math
import shutil
import sys
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import final_zmierzch_detal_1 as ZD1  # noqa: E402  (importuje ujecia_finalne_korekty → poprawki kontekstu → dodatkowe)

FK = ZD1.FK
U = FK.U


# ============================================================================================== (1) winieta / dół kadru
def _smooth(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def winieta(png, cfg, raport, passy=None):
    from PIL import Image
    png = Path(png)
    shutil.copyfile(png, png.with_name(png.stem + '_surowy.png'))
    a = np.asarray(Image.open(png).convert('RGB'), dtype=np.float32) / 255.0
    lin = FK._s2l(a)
    H, W = a.shape[:2]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    fy = 1.0 - (yy + 0.5) / H                                  # wysokość od dołu kadru (0…1)
    fx = (xx + 0.5) / W
    cy = float(cfg.get('srodek_y', 0.55))
    d = np.sqrt(((fx - 0.5) / 0.5) ** 2 + ((fy - cy) / 0.5) ** 2)
    d0, d1 = float(cfg.get('d0', 0.60)), float(cfg.get('d1', 1.42))
    ev_v = float(cfg.get('ev', 0.30)) * _smooth((d - d0) / max(1e-6, d1 - d0))
    zas = float(cfg.get('dol_zasieg', 0.30))
    ev_b = float(cfg.get('dol_ev', 0.40)) * (1.0 - _smooth(fy / max(1e-6, zas)))
    ev = ev_v + ev_b
    lin = lin * (2.0 ** (-ev))[..., None]
    nev = cfg.get('niebo_ev')
    if nev and passy:
        # filtr połówkowy z maską nieba: piksele bez trafienia (Mist = 1, Object Index = 0), krawędź rozmyta 0,8 px
        from scipy import ndimage
        mist = FK._wczytaj_exr(passy['mgla'])
        idx = FK._wczytaj_exr(passy['idx'])
        if mist.shape != (H, W):
            raise RuntimeError('passy %s ≠ obraz %s' % (mist.shape, (H, W)))
        m = ndimage.gaussian_filter(((mist > 0.9999) & (idx < 0.5)).astype(np.float32), 0.8)
        lin = lin * (2.0 ** (float(nev) * m))[..., None]
        raport['niebo_maska_udzial'] = round(float((m > 0.5).mean()), 3)
    out = (FK._l2s(lin) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(png)
    raport.update(cfg=cfg, ev_naroze_gorne=round(float(ev[0, 0]), 3), ev_naroze_dolne=round(float(ev[-1, 0]), 3),
                  ev_dol_srodek=round(float(ev[-1, W // 2]), 3), ev_korona_y071=round(float(ev[int(0.29 * H), W // 2]), 3))
    print('[zd3] winieta: %s' % json.dumps(raport, ensure_ascii=False))


class _Shim3:
    """U.subprocess.run(postprodukcja) → winieta na surowym PNG, potem łańcuch nakładki finałowej (post_przed, preset)."""

    def __init__(self, inner):
        self.inner, self.cfg, self.raport, self.passy = inner, None, {}, None

    def run(self, args, **kw):
        if self.cfg and str(U.POSTPRODUKCJA) in [str(x) for x in args]:
            try:
                winieta(args[3], self.cfg, self.raport, self.passy)
            except Exception as e:
                self.raport['blad'] = repr(e)
                print('[zd3] winieta – błąd: %r' % (e,))
        return self.inner.run(args, **kw)


SHIM3 = _Shim3(U.subprocess)
U.subprocess = SHIM3


# ============================================================================================== (2) raport
def latarnie_w_kadrze(sc):
    from bpy_extras.object_utils import world_to_camera_view
    cam = sc.camera
    loc = cam.matrix_world.translation
    out = []
    for ob in sc.objects:
        if ob.type != 'MESH' or not ob.name.startswith('latarnia_'):
            continue
        bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        vs = [world_to_camera_view(sc, cam, p) for p in bb]
        przed = [v for v in vs if v.z > 0]
        if not przed:
            continue
        w_kadrze = any(-0.0 <= v.x <= 1.0 and 0.0 <= v.y <= 1.0 for v in przed)
        xs = [v.x for v in przed]
        ymax = max(v.y for v in przed)
        c = sum(bb, Vector()) / 8
        d = math.hypot(c.x - loc.x, c.y - loc.y)
        if d > 40:
            continue
        out.append(dict(obiekt=ob.name, odl_poz_m=round(d, 1), z_gora=round(max(p.z for p in bb), 2),
                        x0=round(min(xs), 3), x1=round(max(xs), 3), y_max=round(ymax, 3), w_kadrze=bool(w_kadrze)))
    out.sort(key=lambda t: t['odl_poz_m'])
    return out


def pomiar_zd3(jpg, pl):
    from PIL import Image
    out = {}
    if isinstance(pl, dict):
        def g(kl, kk):
            return pl.get(kl, {}).get(kk)

        def ev(a, ka, b, kb):
            va, vb = g(a, ka), g(b, kb)
            if va and vb:
                return round(math.log2(max(va, 1e-6) / max(vb, 1e-6)), 2)
            return None
        out['EV'] = {
            'szklo_korony(p90) − ceramika(mediana)': ev('szklo_korony', 'p90', 'ceramika', 'mediana'),
            'szklo_korony(p90) − granit(mediana)': ev('szklo_korony', 'p90', 'granit', 'mediana'),
            'szklo_korony(mediana) − ceramika(mediana)': ev('szklo_korony', 'mediana', 'ceramika', 'mediana'),
            'szklo_korony(mediana) − granit(mediana)': ev('szklo_korony', 'mediana', 'granit', 'mediana'),
            'szklo_korony(p90) − szklo_biur(p90)': ev('szklo_korony', 'p90', 'szklo_biur_parteru', 'p90'),
            'niebo(mediana) − granit(mediana)': ev('niebo', 'mediana', 'granit', 'mediana'),
            'niebo(mediana) − ceramika(mediana)': ev('niebo', 'mediana', 'ceramika', 'mediana'),
        }
    im = np.asarray(Image.open(jpg).convert('RGB'), dtype=np.float32) / 255.0
    H, W = im.shape[:2]
    lin = FK._s2l(im)
    L = FK._lum(lin)

    def pas(y0, y1, x0=0.0, x1=1.0):
        r0, r1 = int((1 - y1) * H), int((1 - y0) * H)
        c0, c1 = int(x0 * W), int(x1 * W)
        blk = im[r0:r1, c0:c1].reshape(-1, 3)
        return float(np.median(L[r0:r1, c0:c1])), [round(float(v) * 255) for v in np.median(blk, axis=0)]
    lg, cg = pas(0.95, 1.0)
    la, ca = pas(0.83, 0.87, 0.30, 0.70)
    out['niebo'] = dict(gora_luminancja=round(lg, 4), gora_sRGB=cg, nad_attyka_luminancja=round(la, 4),
                        nad_attyka_sRGB=ca, gradient_EV=round(math.log2(max(la, 1e-6) / max(lg, 1e-6)), 2))
    ld, cd = pas(0.0, 0.05, 0.25, 0.75)
    l35, c35 = pas(0.0, 0.35)
    out['dol_kadru'] = dict(pas_0_5proc_luminancja=round(ld, 4), pas_0_5proc_sRGB=cd,
                            dolne_35proc_luminancja=round(l35, 4), dolne_35proc_sRGB=c35)
    return out


_ru = U.render_ujecia


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    out_jpg = Path(out_jpg)
    SHIM3.cfg = None if FK.ARGS_EXTRA.wycinek else k.get('winieta')
    SHIM3.raport = {}
    SHIM3.passy = None
    if SHIM3.cfg and SHIM3.cfg.get('niebo_ev') and not k.get('post_przed') and not a.kontrola_tylko:
        SHIM3.passy = FK._kompozytor(sc, out_jpg.stem + '_pass3_')     # Mist + Object Index → maska nieba
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    try:
        r['latarnie_w_kadrze'] = latarnie_w_kadrze(sc)
    except Exception as e:
        r['latarnie_w_kadrze'] = repr(e)
    if isinstance(r['latarnie_w_kadrze'], list):
        wk = [x for x in r['latarnie_w_kadrze'] if x['w_kadrze']]
        print('[zd3] latarnie w kadrze: %s; najbliższe: %s' % (
            ', '.join(x['obiekt'] for x in wk) or 'brak',
            '; '.join('%(obiekt)s %(odl_poz_m).1f m y_max %(y_max).3f x %(x0).2f…%(x1).2f' % x
                      for x in r['latarnie_w_kadrze'][:4])))
    r['winieta'] = dict(SHIM3.raport)
    if r.get('jpg') and Path(r['jpg']).exists() and not FK.ARGS_EXTRA.wycinek:
        try:
            r['pomiar_zd3'] = pomiar_zd3(r['jpg'], r.get('pomiar_luminancji'))
        except Exception as e:
            r['pomiar_zd3'] = repr(e)
        print('[zd3] pomiar: %s' % json.dumps(r['pomiar_zd3'], ensure_ascii=False))
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p

if __name__ == '__main__':
    FK.main()
