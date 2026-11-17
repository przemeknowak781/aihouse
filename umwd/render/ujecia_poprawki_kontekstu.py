# -*- coding: utf-8 -*-
"""Nakładka na umwd/render/ujecia_dodatkowe.py (bez edycji wspólnych plików; uruchomienie i argumenty jak ujecia_dodatkowe.py,
np. ``python -I render/ujecia_poprawki_kontekstu.py --id zlota-godzina-3 --szer 480 --probki 16 --bez-ludzi``).
Tymczasowe obejście dwóch artefaktów context.py – do usunięcia po ich poprawce w context.zbuduj_dalsze.

(1) Po zbudowaniu / wczytaniu sceny usuwa
z obiektu 'brzegi_dalsze' pionowe ściany stojące w nurcie wzdłuż granicy ramki mapy (artefakt context.zbuduj_dalsze:
krawędzie pierścienia wody wzdłuż rk.buffer(0.5) nie są pomijane, bo test używa rk.buffer(0.2) – ściana ~3,8 m nad
lustrem wody wzdłuż e = 152,5 i n = 148,6).
(2) Usuwa fałszywą groblę pod Mostem Grunwaldzkim: maska wody z ortofotomapy uznaje pomost/cień mostu za ląd –
pas teren_dalszy_ortofoto 12–20 m w poprzek Odry z pionowymi ścianami brzegi_dalsze (z poziomu wody widoczny pod mostem).
(3) Render na 2 wątkach (maszyna współdzielona)."""
import sys
sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')
import bpy
import bmesh
from shapely.geometry import box, Point
import ujecia_dodatkowe as U


def usun_sciane_ramki():
    ob = bpy.data.objects.get('brzegi_dalsze')
    if ob is None:
        return 0
    ring = box(*U.RAMKA_SZCZEGOLOWA).buffer(0.5, join_style='mitre').exterior
    M = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    usun = []
    for f in bm.faces:
        c = M @ f.calc_center_median()
        if ring.distance(Point(c.x, c.y)) < 0.35:
            usun.append(f)
    bmesh.ops.delete(bm, geom=usun, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    print('[render_zg] usunięto %d ścian brzegi_dalsze wzdłuż granicy ramki (artefakt w nurcie)' % len(usun))
    return len(usun)


def usun_groble_pod_mostem(s0=6.0, s1=114.0, x_max=22.0):
    """Maska wody z ortofotomapy uznaje cień / pomost Mostu Grunwaldzkiego za ląd: w poprzek Odry pod pomostem
    powstaje pas 'teren_dalszy_ortofoto' (12–20 m) z pionowymi ścianami 'brzegi_dalsze' – z poziomu wody i z brzegów
    widoczny pod mostem jako grobla. Usuwa ściany siatek w korytarzu osi mostu (s0…s1, |x| ≤ x_max) poza ramką."""
    import math
    from shapely.geometry import Polygon
    O = (93.90, 136.575)
    az = math.radians(70.4)
    u = (math.sin(az), math.cos(az))
    vl = (-u[1], u[0])
    W = lambda s, x: (O[0] + s * u[0] + x * vl[0], O[1] + s * u[1] + x * vl[1])
    P = Polygon([W(s0, -x_max), W(s1, -x_max), W(s1, x_max), W(s0, x_max)])
    rk = box(*U.RAMKA_SZCZEGOLOWA)
    razem = 0
    for nazwa, bufor in (('teren_dalszy_ortofoto', 0.0), ('brzegi_dalsze', 1.0)):
        ob = bpy.data.objects.get(nazwa)
        if ob is None:
            continue
        PP = P.buffer(bufor) if bufor else P
        M = ob.matrix_world
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        usun = []
        for f in bm.faces:
            c = M @ f.calc_center_median()
            pt = Point(c.x, c.y)
            if PP.contains(pt) and not rk.contains(pt):
                usun.append(f)
        bmesh.ops.delete(bm, geom=usun, context='FACES')
        bm.to_mesh(ob.data)
        bm.free()
        ob.data.update()
        razem += len(usun)
        print('[render_zg] %s: usunięto %d ścian w korytarzu pod Mostem Grunwaldzkim (fałszywa grobla)' % (nazwa, len(usun)))
    return razem


def popraw_kontekst():
    usun_sciane_ramki()
    usun_groble_pod_mostem()


_zb, _wb = U.zbuduj_scene, U.wczytaj_blend


def zbuduj_scene(*a, **k):
    r = _zb(*a, **k)
    popraw_kontekst()
    return r


def wczytaj_blend(*a, **k):
    r = _wb(*a, **k)
    popraw_kontekst()
    return r


U.zbuduj_scene, U.wczytaj_blend = zbuduj_scene, wczytaj_blend

_ru = U.render_ujecia


def render_ujecia(sc, *a, **k):
    # maszyna współdzielona (4 rdzenie, równolegle renderują inni) – render na 2 wątkach
    sc.render.threads_mode = 'FIXED'
    sc.render.threads = 2
    return _ru(sc, *a, **k)


U.render_ujecia = render_ujecia

if __name__ == '__main__':
    U.main()
