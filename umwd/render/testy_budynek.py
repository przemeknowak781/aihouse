# -*- coding: utf-8 -*-
"""Rendery testowe budynku UMWD w kontekście 3D (jesień, obszar inwestycji „pusty” + budynek z budynek3d).

Kamery z ``model/koncepcja.json`` (W3 – Brama Mostowa, W4 – relacja z Wybrzeżem Słowackiego 5, W5 – relacja
z Mazowiecką 19, W9 – latarnia z Mostu Grunwaldzkiego, W10 – Ogród Województwa) + widok kontrolny z lotu ptaka.
Pora dnia wg specyfikacji kadru. Przed renderem: kontrola położenia kamery (w bryle? w koronie drzewa?
co zasłania oś widzenia?). Wynik: ``docs/60_wizualizacje/img/budynek_test_<kamera>.jpg`` (≤ 1 MB).

Uruchomienie::

    /home/user/aihouse/.venv-render/bin/python -I /home/user/aihouse/umwd/render/testy_budynek.py \
        [--kamery W3 W4 ...] [--probki 32] [--szer 1000] [--blend scena.blend] [--bez-ludzi]
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

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402
from shapely.geometry import Point  # noqa: E402

from umwd.render import blib, context, budynek3d  # noqa: E402

OUT = UMWD / 'docs' / '60_wizualizacje' / 'img'

# kamery dodatkowe (nie ma ich w koncepcja.json) – tylko do kontroli bryły
KAMERY_DODATKOWE = {
    'detal_podcien': dict(opis='Detal: podcień Bramy Mostowej z napisem, kolumny, okładziny (kontrola materiałów)',
                          kamera_e_n_z=(118.0, 70.0, 1.62), cel_e_n_z=(103.4, 74.1, 3.6), lens_mm=35, shift_y=0.12,
                          poziom=True, czas='2026-10-23 09:40 CEST'),
    'plac_mostowy': dict(opis='Plac Mostowy (skwer 9/2) od pn.-zach.: elewacja pn. z podcieniem, łuk, lipy, dziób skrzydła',
                         kamera_e_n_z=(68.0, 99.0, 1.62), cel_e_n_z=(88.0, 72.0, 12.0), lens_mm=24, shift_y=0.28,
                         poziom=True, czas='2026-10-23 14:30 CEST'),
    'lot_ptaka': dict(opis='Kontrolny widok z lotu ptaka od pn.-wsch. (dachy, bryła, relacja z mostem)',
                      kamera_e_n_z=(178.0, 168.0, 72.0), cel_e_n_z=(88.0, 50.0, 8.0), lens_mm=30, shift_y=0.0,
                      poziom=False, czas='2025-10-29 11:40 CET'),
}
# proporcje kadrów = proporcje pól na planszach (tools/plansze_etap2.py, b.add(...) w mm) – plansza nie przycina
# obrazu; szerokości minimalne wersji finalnych (300 dpi planszy) wg koordynatora 17.11
PROPORCJE_PLANSZ = {'W3': 578 / 400, 'W6': 578 / 196, 'W4': 480 / 256, 'W5': 464 / 338.67}
SZEROKOSC_FINALNA = {'W3': 5800, 'W6': 5000, 'W4': 4000, 'W5': 4000, 'W1': 5800, 'W2': 4000}
# korekty kadrów (z uzasadnieniem) – stosowane, gdy kamera ze specyfikacji nie pokazuje wymaganej treści
KOREKTY = {
    # W3 (decyzja koordynatora 17.11): stanowisko z poziomu człowieka ≥ 30 m od lica łuku, z którego widać Bramę
    # Mostową (podcień z napisem w nadprożu) i całą koronę z attyką. Przy 24 mm i kadrze 3:2 rozpiętość
    # posadzka podcienia → attyka (+37,2) mieści się dopiero z ≥ 38 m – tam oś przecinają istniejące krzewy
    # przyczółka mostu (krzew_61/62, poza granicą opracowania, zostają). Przeszukanie promieni (drzwi, kolumny, napis
    # w 9 kierunkach łuku + attyka) dało czyste stanowisko na skraju chodnika przy schodach przyczółka (109,0; 107,5),
    # 33,1 m od lica łuku. Kadr w proporcji pola planszy 578 × 400 mm (1,445 : 1): ogniskowa 20 mm z przesunięciem
    # 0,276 (piony zachowane, posadzka podcienia z zapasem, ~2,5 m nieba nad attyką).
    # Wariant 24 mm z 37 m (107,5; 112,3; shift 0,26) – krzewy zasłaniają prawą część podcienia (patrz budynek_3d.md).
    # Krzew istniejący 5 m na pd.-wsch. od stanowiska (poza osią widzenia, prawy dolny róg) – niewidoczny dla kamery
    # (cień zostaje): fotograf stoi tuż przed nim; z 1 m dalej na zach. ten sam krzew zasłaniałby podcień.
    'W3': dict(kamera_e_n_z=(109.0, 107.5, 2.67), cel_e_n_z=(103.4, 74.1, 16.0), lens_mm=20, shift_y=0.276,
               ukryj_krzewy_m=7.0),
    # W4, W5: kadr w proporcji pól planszy (1,875 / 1,37) – przy ogniskowej z JSON gzyms-attyka segmentu (W4)
    # i styk gzymsu skrzydła z gzymsem Mazowieckiej 19 (W5) wypadały poza górną krawędź; szerszy obiektyw i shift.
    'W4': dict(lens_mm=21, shift_y=0.18),
    'W5': dict(lens_mm=24, shift_y=0.24),
    # W9: punkt (126; 152) leży na jezdni mostu, 3,8 m od osi; z chodnika widok przecinają krzyżulce kratownicy
    # (płaszczyzny ±9,6 m). Pozycja dobrana przeszukaniem promieni na drzewie BVH mostu (117 promieni kadru bez trafień w kratownicę,
    # łańcuchy i wieszaki): 38 m od portalu pd. (JSON: 35 m), 9,3 m od osi – tuż przy płaszczyźnie kratownicy
    # (±9,6 m), oś widzenia przechodzi przez górny trójkąt krzyżulców. Oko 1,6 m nad chodnikiem (+4,05).
    # Przesunięcie obiektywu tak, by cel (+26 m) był w środku kadru (kamera pozioma, piony zachowane).
    'W9': dict(kamera_e_n_z=(132.82, 140.57, 4.05), shift_y=0.351, ekspozycja=0.6),
    # W6 – Hala Obywatelska (SW.01c wg model/budynek.json, szczegółowe wnętrze: budynek3d_hala.py). Oś 211,7°
    # z koncepcja.json nie jest w budynek.json drożna na całej długości: narożnik SW.02 0,45 m od osi (a ≈ 8,7 m),
    # przejście SW.06 / trzony 3,9 m (a ≈ 16–19 m), narożnik PHS.04 na osi (a = 25,5 m), koniec osi w PHS.04.
    # Z punktu koncepcji (na osi) przeszklenie ogrodowe widać tylko przez szczelinę – stanowisko przesunięto
    # o 3 m w prawo od osi (a = 3 m od drzwi Bramy Mostowej), kadr na środek ściany ogrodowej holu (x 87,3–94,9):
    # całe przeszklenie ogrodowe i drzewa ogrodu widoczne przez przejście.
    # Pole planszy 578 × 196 mm (2,95 : 1) – panorama prostoliniowa 16 mm (97° w poziomie), piony zachowane.
    'W6': dict(kamera_e_n_z=(97.73, 70.59, 1.60), cel_e_n_z=(89.90, 45.60, 1.60), lens_mm=16, shift_y=0.04,
               wnetrze=True, preset='wnetrze', ekspozycja=-0.35, plik='W6_hol_test.jpg'),
    # W10 – widok ogrodowy (decyzja koordynatora 17.11, zamiast kadru z koncepcja.json: punkt (78; 17) stoi pod
    # koronami zachowanych drzew). Stanowisko przy wsch. krawędzi placu zabaw (97,0; −6,0), w obszarze inwestycji,
    # ok. 50 m od lica pd. wieży: przeszukanie promieni (85 punktów lica pd. wieży) – brak roślinności w pierwszych
    # metrach przed obiektywem; korony zachowanych drzew ogrodu (D776, D778, D708…) w planie środkowym, wieża ponad
    # nimi. W pierwszym planie plac zabaw i ogród deszczowy. 24 mm, shift 0,17 (attyka z zapasem, posadzka od ~6 m).
    # Ogród w cieniu koron i kamienic przez większość dnia (22.10: ≤ 19 % placu zabaw w słońcu) – ekspozycja +0,7 EV.
    'W10': dict(kamera_e_n_z=(97.0, -6.0, 1.01), cel_e_n_z=(93.5, 45.0, 18.0), lens_mm=24, shift_y=0.17, ekspozycja=-3.6),
}


def kamera_z_json(spec, kid):
    if kid in KAMERY_DODATKOWE:
        k = dict(KAMERY_DODATKOWE[kid])
        k['id'] = kid
        return k
    k = next(dict(c) for c in spec.kamery if c['id'] == kid)
    k.update(KOREKTY.get(kid, {}))
    k.setdefault('poziom', True)
    return k


def kontrola_kamery(sc, B, kam, k, ctx):
    """Sprawdza: czy kamera stoi w bryle budynku/kontekstu, w koronie drzewa, co trafia promień osi i narożników
    kadru (obiekt, odległość). Zwraca listę uwag."""
    uwagi = []
    loc = kam.location
    p = Point(loc.x, loc.y)
    if B.foot.buffer(0.3).contains(p):
        uwagi.append('KAMERA W OBRYSIE BUDYNKU')
    for ob in bpy.data.objects:
        if ob.instance_type == 'COLLECTION' and ob.instance_collection is not None and (
                ob.name.startswith('drzewo') or ob.name.startswith('szpaler') or ob.name.startswith('krzew')):
            d = math.hypot(ob.location.x - loc.x, ob.location.y - loc.y)
            R = 7.2 * ob.scale[0] if 'duze' in ob.instance_collection.name else 4.0 * ob.scale[0]
            if d < 0.8:
                uwagi.append('KAMERA PRZY PNIU %s (%.1f m)' % (ob.name, d))
            elif d < R * 0.7 and loc.z > ob.location.z + 2.5:
                uwagi.append('kamera w koronie %s (%.1f m od pnia)' % (ob.name, d))
    dg = bpy.context.evaluated_depsgraph_get()
    cd = kam.data
    W, H = sc.render.resolution_x, sc.render.resolution_y
    fr = cd.view_frame(scene=sc)
    M = kam.matrix_world
    trafienia = []
    for fx, fy, opis in ((0.5, 0.5, 'oś'), (0.15, 0.2, 'L-dół'), (0.85, 0.2, 'P-dół'), (0.15, 0.8, 'L-góra'),
                         (0.85, 0.8, 'P-góra'), (0.5, 0.15, 'dół')):
        # punkt na płaszczyźnie kadru (lokalnie): interpolacja narożników view_frame (z uwzględnieniem shift)
        a, b, c, d_ = fr        # P-góra, P-dół, L-dół, L-góra
        top = d_.lerp(a, fx)
        bot = c.lerp(b, fx)
        q = bot.lerp(top, fy)
        kier = (M.to_3x3() @ q).normalized()
        hit, pos, nrm, idx, ob, mx = sc.ray_cast(dg, M.translation, kier)
        if hit:
            trafienia.append('%s: %s %.1f m' % (opis, ob.name if ob else '?', (pos - M.translation).length))
            if (pos - M.translation).length < 2.0:
                uwagi.append('BLISKA PRZESZKODA (%s): %s %.1f m' % (opis, ob.name, (pos - M.translation).length))
        else:
            trafienia.append('%s: niebo' % opis)
    return uwagi, trafienia


def preset_postprodukcji(k, sw):
    """Preset ``tools/postprodukcja.py``: jawny w kamerze (``preset``) albo z wysokości słońca i kamery."""
    if k.get('preset'):
        return k['preset']
    if sw['el'] < 6.0:
        return 'zmierzch'
    return 'lot' if k['kamera_e_n_z'][2] > 25.0 else 'dzien'


def zapisz_jpg(png, jpg, q=93, preset=None):
    """PNG → JPG ≤ 1 MB; ostatni krok: wspólna postprodukcja kompletu (``tools/postprodukcja.py``, preset)."""
    from PIL import Image
    im = Image.open(png).convert('RGB')
    if preset:
        sys.path.insert(0, str(UMWD / 'tools'))
        import postprodukcja
        im = postprodukcja.process(im, postprodukcja.PRESETS[preset])
    while True:
        im.save(jpg, quality=q, optimize=True)
        if Path(jpg).stat().st_size <= 1_000_000 or q < 50:
            break
        q -= 5
    Path(png).unlink()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kamery', nargs='*', default=['W3', 'W4', 'W5', 'W9', 'plac_mostowy', 'lot_ptaka'])
    ap.add_argument('--probki', type=int, default=32)
    ap.add_argument('--szer', type=int, default=1000)
    ap.add_argument('--blend', default=None)
    ap.add_argument('--bez-ludzi', action='store_true')
    ap.add_argument('--bez-wnetrz', action='store_true')
    ap.add_argument('--look', default='AgX - Medium High Contrast')
    ap.add_argument('--prefix', default='budynek_test_')
    ap.add_argument('--out', default=str(OUT))
    ap.add_argument('--tylko-kontrola', action='store_true', help='bez renderu – tylko kontrola kamer')
    ap.add_argument('--odbicia', default='m09_30', help="środowisko odbić: m09_30|m09_40|m09_45|brak")
    ap.add_argument('--bez-postprodukcji', action='store_true', help='bez kroku tools/postprodukcja.py')
    ap.add_argument('--wycinek', nargs=4, type=float, default=None, metavar=('X0', 'X1', 'Y0', 'Y1'),
                    help='render tylko wycinka kadru (ułamki szerokości/wysokości, y od dołu) – kontrola detalu')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    sc = blib.reset()
    kon = context.build_context(sc, {'pora_roku': 'jesien', 'obszar_inwestycji': 'pusty'})
    t_kon = time.time() - t0
    t1 = time.time()
    hala = any(KOREKTY.get(kid, {}).get('wnetrze') for kid in a.kamery)
    bud = budynek3d.build_building(sc, {'kontekst': kon, 'ludzie': not a.bez_ludzi, 'wnetrza': not a.bez_wnetrz,
                                        'hala_szczegolowa': hala})
    t_bud = time.time() - t1
    B = bud['budynek']
    print('[testy] kontekst %.1f s, budynek %.1f s' % (t_kon, t_bud))
    print(json.dumps(bud['info'], ensure_ascii=False))
    blib.render_settings(sc, a.szer, int(a.szer * 2 / 3), samples=a.probki, adaptive=0.03, exposure=-4.3,
                         look=a.look, max_bounces=8, clamp_indirect=8.0)
    sc.cycles.transparent_max_bounces = 24
    sc.render.use_persistent_data = True
    raport = {'kontekst_s': round(t_kon, 1), 'budynek_s': round(t_bud, 1), 'info': bud['info'], 'kamery': {}}
    for kid in a.kamery:
        k = kamera_z_json(B.spec, kid)
        DZ = B.DZ
        x, y, z = k['kamera_e_n_z']
        tx, ty, tz = k['cel_e_n_z']
        cam = blib.camera(sc, (x, y, z + DZ), (tx, ty, tz + DZ), lens_mm=k['lens_mm'], level=k.get('poziom', True),
                          shift_y=k.get('shift_y', 0.0), name='K_' + kid)
        cam.data.clip_start = 0.2
        ukryte = []
        if k.get('ukryj_krzewy_m'):
            for ob in bpy.data.objects:
                if ob.instance_type == 'COLLECTION' and ob.instance_collection is not None and \
                        'krzew' in ob.instance_collection.name and ob.visible_camera and \
                        math.hypot(ob.location.x - x, ob.location.y - y) < k['ukryj_krzewy_m']:
                    ob.visible_camera = False
                    ukryte.append(ob)
        prop = k.get('proporcje', PROPORCJE_PLANSZ.get(kid, 1.5))
        sc.render.resolution_x = a.szer
        sc.render.resolution_y = int(round(a.szer / prop))
        context.ustaw_kamere_trawy(kon, cam)
        sw = budynek3d.swiatlo_dzienne(sc, k['czas'], ekspozycja=k.get('ekspozycja'),
                                       odbicia=None if a.odbicia == 'brak' else a.odbicia)
        uwagi, traf = kontrola_kamery(sc, B, cam, k, kon['ctx'])
        print('[testy] %s  %s  słońce az %.1f° el %.1f°  ekspozycja %.2f' % (kid, k['czas'], sw['az'], sw['el'],
                                                                             sw['ekspozycja']))
        print('        uwagi: %s' % ('; '.join(uwagi) or 'brak'))
        print('        promienie: %s' % ' | '.join(traf))
        wpis = dict(czas=k['czas'], slonce=sw, uwagi=uwagi, promienie=traf, opis=k.get('opis', ''))
        if not a.tylko_kontrola:
            png = out / ('_tmp_%s.png' % kid)
            sc.render.filepath = str(png)
            if a.wycinek:
                sc.render.use_border = sc.render.use_crop_to_border = True
                (sc.render.border_min_x, sc.render.border_max_x,
                 sc.render.border_min_y, sc.render.border_max_y) = a.wycinek
            t2 = time.time()
            bpy.ops.render.render(write_still=True)
            dt = time.time() - t2
            jpg = out / ('%s%s%s.jpg' % (a.prefix, kid, '_wycinek' if a.wycinek else ''))
            if k.get('plik'):
                jpg = out / (k['plik'].replace('.jpg', '_wycinek.jpg') if a.wycinek else k['plik'])
            preset = None if a.bez_postprodukcji else preset_postprodukcji(k, sw)
            zapisz_jpg(png, jpg, preset=preset)
            wpis.update(render_s=round(dt, 1), plik=str(jpg), postprodukcja=preset)
            print('[testy] %s: %.1f s → %s' % (kid, dt, jpg))
        for ob in ukryte:
            ob.visible_camera = True
        if ukryte:
            wpis['ukryte_krzewy'] = [o.name for o in ukryte]
        raport['kamery'][kid] = wpis
    # raport kumulowany (przebiegi po jednej kamerze dopisują swoje wpisy)
    plik_r = UMWD / 'build' / 'budynek_test_raport.json'
    try:
        stary = json.loads(plik_r.read_text(encoding='utf-8'))
        stary['kamery'].update(raport['kamery'])
        raport['kamery'] = stary['kamery']
    except Exception:
        pass
    plik_r.write_text(json.dumps(raport, ensure_ascii=False, indent=1), encoding='utf-8')
    if a.blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.blend)
    print('[testy] razem %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
