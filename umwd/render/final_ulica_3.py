# -*- coding: utf-8 -*-
"""Render finalny ujęcia „ulica-3” (Wybrzeże i wieża nad Odrą – z Mostu Grunwaldzkiego) – nakładka na wspólną
nakładkę finałową zestawu ``render/ujecia_finalne_korekty.py`` (→ ``ujecia_poprawki_kontekstu.py`` →
``ujecia_dodatkowe.py``), bez edycji modułów wspólnych; uruchomienie i argumenty jak ``ujecia_finalne_korekty.py``::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/final_ulica_3.py \
        --id ulica-3 --szer 2000 --probki 64 --out umwd/docs/60_wizualizacje/img/extra/E_ulica-3.jpg

``--surowy PNG`` (opcja tej nakładki): obraz bierze się z zachowanego surowego PNG renderu (ten sam kadr i scena),
a render służy tylko passom (Depth, Mist, Object Index) – wystarczy ``--probki 1``; potem mgła i postprodukcja.
Raport kontroli zachowuje próbki i czas renderu, z którego pochodzi surowy PNG (``post_z_surowego``).

Warunki wspólne zestawu (z ``ujecia_finalne_korekty.py``, przy budowie sceny od zera): lamele korony łuku wg v1.1
(21 szt. 0,35 × 0,60 m, rozstawy 1,35 / 0,675 m w ciągu Fibonacciego), sitodruk 30 % na szkle korony, w dzień ciepłe
oprawy ×0,12; klucz ``woda`` wpisu JSON (chropowatość, fale, barwa wody).

Poprawki tego ujęcia wg uwag jurorów (po zbudowaniu / wczytaniu sceny, idempotentnie):

1. **Barka w lewym dole** – uproszczone „białe pudło” z ``context._barka`` (środek (131,5; 81,0), 30 × 9 m) zastąpione
   barką-restauracją z detalem z ``render/final_zlota_godzina_3.py`` (ta sama barka co w ujęciu zlota-godzina-3:
   ciemny kadłub, przeszklony salon z wnętrzem, markiza, relingi, taras z parasolami i donicami, cumy, kładka).
   Funkcje są importowane bez łańcucha nakładek tamtego ujęcia (łańcuch ``U.zbuduj_scene`` przywracany po imporcie).
   Z tamtej nakładki także: zmarszczka wody (oś widzenia tego ujęcia) i wyrównanie uskoku lica muru nabrzeża
   (pionowa smuga cienia), trzech pieszych na bulwarze przy nabrzeżu.
2. **Druga barka (pd., (145; 27), 20 × 7 m)** – jeśli wchodzi w kadr, też byłaby „pudłem”: ``"barka_pd": "usun"``
   w JSON usuwa jej ściany z obiektu ``barki`` (przystań w głębi, 110 m od kamery).
3. **Lekka mgła nad wodą** (``post_przed.mgla.tryb = 'woda'``) – krok przed wspólną postprodukcją: z passu Depth
   (Cycles zapisuje go dla pierwszej powierzchni o alfie ≥ 0,5 – szkło i puste pola kart liści są pomijane; pass Mist
   uśrednia się przez przezroczystości i za szybami daje „daleko”) i kierunków promieni kamery odtwarzane jest
   położenie punktu w każdym pikselu; grubość optyczna mgły to całka gęstości ρ(h) = ρ0·exp(−h / Hs) (h – wysokość
   nad zwierciadłem wody) wzdłuż promienia, mnożona przez rampę odległości (``rampa_m``, domyślnie 55 → 130 m –
   mgła „w głębi”, pierwszy plan bez zmian); transmisja T = exp(−τ), wynik = obraz·T + barwa mgły·(1 − T). Barwa –
   ciepła biel o luminancji nieba przy horyzoncie (rano mgła oświetlona nisko stojącym słońcem).
4. **Kontrola dodatkowa** (raport ``korekty.kontrola_ulica3``): kąt pylonu pd. i łańcucha po stronie kamery od osi
   kadru, elementy mostu w kadrze (wierzchołki siatek mostu rzutowane na kadr, widoczne promieniem), rzut barki
   z detalem i drugiej barki na kadr, ludzie w kadrze (rzut głowy, widoczność).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import bmesh  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

import ujecia_finalne_korekty as FK  # noqa: E402  (warunki wspólne zestawu; importuje ujecia_poprawki_kontekstu)
from umwd.render.context import MostUklad  # noqa: E402

U = FK.U
# funkcje barki / zmarszczki / muru z nakładki zlota-godzina-3 – bez jej łańcucha (przywrócenie po imporcie)
_zb0, _wb0 = U.zbuduj_scene, U.wczytaj_blend
import final_zlota_godzina_3 as ZG3  # noqa: E402
U.zbuduj_scene, U.wczytaj_blend = _zb0, _wb0

Z_WODA = ZG3.Z_WODA
BARKA_PD = dict(c=(145.0, 27.0), rot=-12.0, L=20.0, B=7.0)
UJECIE = {}


def _wpis():
    return FK.UJECIA_WYBRANE[0] if FK.UJECIA_WYBRANE else {}


# ============================================================================================== scena
def usun_barke_pd():
    ob = bpy.data.objects.get('barki')
    if ob is None:
        return 0
    R = ZG3.Rama(BARKA_PD['c'], BARKA_PD['rot'], Z_WODA)
    Mw = ob.matrix_world
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    fs = []
    for f in bm.faces:
        p = Mw @ f.calc_center_median()
        u, w = R.lok(p.x, p.y)
        if abs(u) < BARKA_PD['L'] / 2 + 0.5 and abs(w) < BARKA_PD['B'] / 2 + 0.5:
            fs.append(f)
    bmesh.ops.delete(bm, geom=fs, context='FACES')
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    print('[ulica-3] druga barka (pd.) usunięta: %d ścian' % len(fs))
    return len(fs)


def popraw_scene():
    k = _wpis()
    ZG3.wyrownaj_uskok_muru()
    ZG3.barka_restauracja()
    ZG3.zmarszczka_wody(az_osi=float(k.get('os_zmarszczki', 197.0)))
    ZG3.piesi_bulwar()
    if k.get('barka_pd') == 'usun':
        usun_barke_pd()


_zb, _wb = U.zbuduj_scene, U.wczytaj_blend


def zbuduj_scene(*a, **k):
    r = _zb(*a, **k)
    popraw_scene()
    return r


def wczytaj_blend(*a, **k):
    r = _wb(*a, **k)
    popraw_scene()
    return r


U.zbuduj_scene, U.wczytaj_blend = zbuduj_scene, wczytaj_blend


# ============================================================================================== mgła nad wodą
def kierunki_pikseli(sc, cam, W, H):
    """Jednostkowe kierunki promieni (H, W, 3) w układzie świata – jak U._kierunek_kadru, wektorowo."""
    a, b, c, d = [np.array(v) for v in cam.data.view_frame(scene=sc)]
    fx = (np.arange(W) + 0.5) / W
    fy = 1.0 - (np.arange(H) + 0.5) / H
    dol = c[None, :] + (b - c)[None, :] * fx[:, None]          # (W, 3)
    gora = d[None, :] + (a - d)[None, :] * fx[:, None]
    q = dol[None, :, :] + (gora - dol)[None, :, :] * fy[:, None, None]
    R = np.array(cam.matrix_world.to_3x3())
    v = q @ R.T
    return v / np.linalg.norm(v, axis=2, keepdims=True)


_pp = FK.post_przed
_komp = FK._kompozytor


def _kompozytor_p(sc, prefix):
    """Jak FK._kompozytor (Mist, Object Index) + pass Depth: Cycles zapisuje go (próbka 0) dla pierwszej powierzchni
    o alfie ≥ 0,5 – szkło (Transparent ~90 %) i puste pola kart liści są pomijane, więc odległość jest wiarygodna także
    za szybami i w koronach drzew (pass Mist uśrednia się przez przezroczystości – za szkłem daje „daleko”)."""
    passy = _komp(sc, prefix)
    vl = sc.view_layers[0]
    vl.use_pass_z = True
    ng = sc.compositing_node_group
    rl = next(n for n in ng.nodes if n.bl_idname == 'CompositorNodeRLayers')
    fo = next(n for n in ng.nodes if n.bl_idname == 'CompositorNodeOutputFile')
    wyj = {o.name: o for o in rl.outputs}
    g = next((wyj[x] for x in ('Depth', 'Z') if x in wyj), None)
    if g is None:
        raise RuntimeError('RLayers bez passu Depth (wyjścia: %s)' % list(wyj))
    fo.file_output_items.new('FLOAT', 'glebia')
    ng.links.new(g, fo.inputs['glebia'])
    passy['glebia'] = U.PNG_DIR / ('%sglebia.exr' % prefix)
    return passy


FK._kompozytor = _kompozytor_p
SUROWY = {'png': None}          # --surowy PNG: post z zachowanego surowego renderu (ten sam kadr i scena)


def _smooth(x, a, b):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _post_przed_p(png, passy, cfg, raport):
    mg = (cfg or {}).get('mgla') or {}
    if mg.get('tryb') != 'woda':
        return _pp(png, passy, cfg, raport)
    import shutil
    from PIL import Image
    from scipy import ndimage
    png = Path(png)
    if SUROWY['png']:
        shutil.copyfile(SUROWY['png'], png)
        raport['surowy_z_renderu'] = str(SUROWY['png'])
    shutil.copyfile(png, png.with_name(png.stem + '_surowy.png'))
    a = np.asarray(Image.open(png).convert('RGB'), dtype=np.float32) / 255.0
    H, W = a.shape[:2]
    lin = FK._s2l(a)
    idx = FK._wczytaj_exr(passy['idx'])
    if idx.shape != a.shape[:2]:
        raise RuntimeError('passy %s ≠ obraz %s' % (idx.shape, a.shape[:2]))
    sc = bpy.context.scene
    cam = sc.camera
    loc = np.array(cam.matrix_world.translation)
    fwd = np.array(cam.matrix_world.to_3x3() @ Vector((0, 0, -1)))
    kier = kierunki_pikseli(sc, cam, W, H)
    dmax = float(mg.get('dmax', 800.0))
    if 'glebia' in passy and Path(passy['glebia']).exists():
        zg = FK._wczytaj_exr(passy['glebia'])                   # głębia wzdłuż osi kamery
        niebo = zg > 1e5
        D = np.minimum(zg / np.maximum(kier @ fwd, 1e-3), dmax)
        zrodlo = 'Depth (pierwsza powierzchnia o alfie ≥ 0,5)'
    else:                                                       # zgodność wstecz – pass Mist
        mist = FK._wczytaj_exr(passy['mgla'])
        start, gleb = float(mg.get('start', 0.0)), float(mg.get('glebokosc', 1500.0))
        niebo = (mist > 0.9999) & (idx < 0.5)
        D = np.minimum(start + mist * gleb, dmax)
        zrodlo = 'Mist'
    D = np.where(niebo, dmax, D)
    zp = loc[2] + D * kier[..., 2]
    Hs, rho0 = float(mg.get('Hs', 3.0)), float(mg.get('rho0', 0.0045))
    hc = max(loc[2] - Z_WODA, 0.0)
    hp = np.maximum(zp - Z_WODA, 0.0)
    ec, ep = math.exp(-hc / Hs), np.exp(-hp / Hs)
    dz = hc - hp
    with np.errstate(divide='ignore', invalid='ignore'):
        tau = np.where(np.abs(dz) > 1e-3, Hs * D / dz * (ep - ec), D * ec) * rho0
    tau = np.maximum(np.nan_to_num(tau), 0.0)
    # mgła „w głębi”: pierwszy plan (woda pod obiektywem, barka, nabrzeże) bez zmian – rampa odległości
    d0, d1 = (float(x) for x in mg.get('rampa_m', (55.0, 130.0)))
    tau = tau * _smooth(D, d0, d1)
    T = ndimage.gaussian_filter(np.exp(-tau), 1.0)
    # barwa mgły: luminancja nieba tuż nad horyzontem (mediana), ciepła biel
    pas = niebo & (kier[..., 2] > 0.005) & (kier[..., 2] < 0.06)
    if pas.sum() < 50:
        pas = niebo
    Lh = float(np.median(FK._lum(lin)[pas])) if pas.any() else 0.6
    barwa = np.array(mg.get('barwa', [1.0, 0.965, 0.92]), dtype=np.float32)
    fog = barwa / float(FK._lum(barwa[None, None, :])[0, 0]) * Lh * float(mg.get('jasnosc', 0.95))
    lin = lin * T[..., None] + fog[None, None, :] * (1.0 - T[..., None])
    out = (FK._l2s(lin) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(png)
    woda = np.abs(idx - FK.IDX_WODY) < 0.5
    f = 1 - T
    info = {'mgla_woda': dict(zrodlo_odleglosci=zrodlo, Hs_m=Hs, rho0_1_m=rho0, rampa_m=[d0, d1], dmax_m=dmax,
                              barwa_lin=[round(float(x), 4) for x in fog],
                              luminancja_nieba_przy_horyzoncie=round(Lh, 4),
                              udzial_mgly_max=round(float(f.max()), 3),
                              udzial_mgly_p50_woda=round(float(np.median(f[woda])), 3) if woda.any() else None,
                              udzial_mgly_p95_woda=round(float(np.percentile(f[woda], 95)), 3) if woda.any() else None,
                              kadr_mgla_powyzej_5proc=round(float((f > 0.05).mean()), 3),
                              kadr_mgla_powyzej_15proc=round(float((f > 0.15).mean()), 3))}
    # kontrola odtworzenia położenia: piksel w środku kadru (promień ray_cast ↔ głębia z passu)
    jc, ic = H // 2, W // 2
    P = loc + D[jc, ic] * kier[jc, ic]
    dg = bpy.context.evaluated_depsgraph_get()
    hit, pos, *_ = sc.ray_cast(dg, Vector(loc), Vector(kier[jc, ic]))
    info['mgla_woda']['srodek_kadru_pass_vs_promien_m'] = [round(float(D[jc, ic]), 2),
                                                            round(float((pos - Vector(loc)).length), 2) if hit else None]
    info['mgla_woda']['srodek_kadru_punkt'] = [round(float(x), 2) for x in P]
    raport.update(info)
    print('[ulica-3] mgła nad wodą: %s' % json.dumps(info, ensure_ascii=False))


FK.post_przed = _post_przed_p


# ============================================================================================== kontrola dodatkowa
def _w_kadrze(sc, cam, p):
    from bpy_extras.object_utils import world_to_camera_view
    v = world_to_camera_view(sc, cam, Vector(p))
    return v, (v.z > 0 and 0 <= v.x <= 1 and 0 <= v.y <= 1)


def kontrola_ulica3(sc):
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation.copy()
    fwd = cam.matrix_world.to_3x3() @ Vector((0, 0, -1))
    az_osi = math.degrees(math.atan2(fwd.x, fwd.y)) % 360
    a, b, c, d = cam.data.view_frame(scene=sc)
    # pół-kąty poziome kadru (z przesunięciem obiektywu)
    hl = math.degrees(math.atan2(-c.x, -c.z))
    hp = math.degrees(math.atan2(b.x, -b.z))
    out = dict(az_osi_deg=round(az_osi, 2), pol_kat_lewo_deg=round(hl, 2), pol_kat_prawo_deg=round(hp, 2))
    M = MostUklad()

    def kat(p):
        az = math.degrees(math.atan2(p[0] - loc.x, p[1] - loc.y)) % 360
        return round((az - az_osi + 180) % 360 - 180, 2)

    # pylon pd. – noga po stronie kamery (x ujemne): narożniki cokołu
    nar = [M.W(sb, -(M.X_PYL + aa), 0) for sb in (-2.6, 2.6) for aa in (0.0, 5.72)]
    out['pylon_pd_kat_od_osi_deg'] = sorted(kat(p) for p in nar)
    # łańcuch / kratownica po stronie kamery: płaszczyzna x ≈ −9,6 od s = 0 do s = 120
    lan = [kat(M.W(s, -9.6, 0)) for s in range(0, 121, 5)]
    out['lancuch_kratownica_kat_od_osi_deg'] = dict(min=min(lan, key=abs), zakres=[min(lan), max(lan)])
    # elementy mostu w kadrze: wierzchołki siatek mostu (próbka) widoczne z kamery
    w_kadrze, widoczne, najbl = 0, 0, None
    for ob in [o for o in sc.objects if o.type == 'MESH' and o.name.startswith('most_')]:
        me = ob.data
        krok = max(1, len(me.vertices) // 20000)
        Mw = ob.matrix_world
        for i in range(0, len(me.vertices), krok):
            p = Mw @ me.vertices[i].co
            v, wk = _w_kadrze(sc, cam, p)
            if not wk:
                continue
            w_kadrze += 1
            dd = p - loc
            hit, pos, nrm, ii, obh, mx = sc.ray_cast(dg, loc, dd.normalized(), distance=dd.length - 0.05)
            if not hit:
                widoczne += 1
                if najbl is None or dd.length < najbl[0]:
                    najbl = (round(dd.length, 2), ob.name, round(v.x, 3), round(v.y, 3))
    out['most_wierzcholki_w_kadrze'] = dict(w_rzucie=w_kadrze, widoczne=widoczne, najblizszy_widoczny=najbl)
    # barki
    for nazwa in ('ZG3_barka',):
        ob = bpy.data.objects.get(nazwa)
        if ob is None:
            continue
        xs, ys, n_in, n = [], [], 0, 0
        from bpy_extras.object_utils import world_to_camera_view
        for i in range(0, len(ob.data.vertices), max(1, len(ob.data.vertices) // 3000)):
            pw = ob.matrix_world @ ob.data.vertices[i].co
            if pw.z < Z_WODA + 0.01:          # część podwodna kadłuba – niewidoczna
                continue
            v = world_to_camera_view(sc, cam, pw)
            n += 1
            if v.z > 0:
                xs.append(v.x)
                ys.append(v.y)
                n_in += int(0 <= v.x <= 1 and 0 <= v.y <= 1)
        out['barka_z_detalem'] = dict(x0=round(min(xs), 3), x1=round(max(xs), 3), y0=round(min(ys), 3),
                                      y1=round(max(ys), 3), udzial_wierzcholkow_w_kadrze=round(n_in / max(n, 1), 3))
    R = ZG3.Rama(BARKA_PD['c'], BARKA_PD['rot'], Z_WODA)
    pts = [R.P(u, w, v) for u in (-10, 10) for w in (-3.5, 3.5) for v in (0.0, 3.8)]
    vs = [_w_kadrze(sc, cam, p) for p in pts]
    out['barka_pd_rzut'] = dict(x=[round(min(v.x for v, _ in vs), 3), round(max(v.x for v, _ in vs), 3)],
                                y=[round(min(v.y for v, _ in vs), 3), round(max(v.y for v, _ in vs), 3)],
                                naroza_w_kadrze=sum(int(wk) for _, wk in vs))
    # ludzie w kadrze (głowa widoczna)
    ludzie = []
    for ob in [o for o in sc.objects if o.name.startswith('czlowiek') and not o.hide_render]:
        bb = [ob.matrix_world @ Vector(cc) for cc in ob.bound_box]
        top = max(bb, key=lambda q: q.z)
        glowa = Vector((sum(q.x for q in bb) / 8, sum(q.y for q in bb) / 8, top.z - 0.12))
        v, wk = _w_kadrze(sc, cam, glowa)
        if not wk:
            continue
        dd = glowa - loc
        hit, pos, nrm, ii, obh, mx = sc.ray_cast(dg, loc, dd.normalized(), distance=dd.length - 0.3)
        if not hit:
            ludzie.append((ob.name, round(v.x, 3), round(v.y, 3), round(dd.length, 1)))
    out['ludzie_widoczni'] = dict(liczba=len(ludzie), lista=ludzie[:40])
    # udziały obiektów w kadrze (siatka 48 × 32) – mur nabrzeża, woda, barka, niebo …
    licz = {}
    nx, ny = 48, 32
    for j in range(ny):
        for i in range(nx):
            dd = U._kierunek_kadru(cam, sc, (i + 0.5) / nx, (j + 0.5) / ny)
            hit, pos, nrm, ii, obh, mx = sc.ray_cast(dg, loc, dd)
            nm = obh.name if hit else 'niebo'
            if nm.startswith('czlowiek'):
                nm = 'ludzie'
            elif nm.startswith(('drzewo', 'krzew', 'szpaler')) or any(s in nm for s in ('liscie', 'galezie', 'pien')):
                nm = 'drzewa/krzewy'
            elif nm.startswith(('wieza', 'skrzydlo', 'segment')):
                nm = 'budynek:' + nm.split('_')[0]
            licz[nm] = licz.get(nm, 0) + 1
    out['udzialy_obiektow'] = {kk: round(v / (nx * ny), 3) for kk, v in sorted(licz.items(), key=lambda t: -t[1])[:14]}
    return out


_ru = U.render_ujecia


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    out_jpg = Path(out_jpg)
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    prev = None
    if SUROWY['png'] and plik_r.exists():          # raport renderu, z którego pochodzi surowy PNG
        prev = json.loads(plik_r.read_text(encoding='utf-8'))
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    kor = r.setdefault('korekty', {})
    try:
        kor['kontrola_ulica3'] = kontrola_ulica3(sc)
        print('[ulica-3] kontrola: %s' % json.dumps(kor['kontrola_ulica3'], ensure_ascii=False))
    except Exception as e:          # kontrola pomocnicza – nie przerywa
        kor['kontrola_ulica3'] = dict(blad=repr(e))
        print('[ulica-3] kontrola – błąd: %r' % (e,))
    if SUROWY['png'] and not a.kontrola_tylko:
        cz = r.setdefault('czasy_s', {})
        r['post_z_surowego'] = dict(surowy_png=str(SUROWY['png']), probki_passow=a.probki,
                                    render_passow_s=cz.get('render_s'), postprodukcja_s=cz.get('postprodukcja_s'),
                                    opis='passy (Depth, Mist, Object Index) z renderu 1 próbki tego samego kadru i sceny; '
                                         'obraz – surowy PNG renderu finalnego (próbki i czas niżej)')
        if prev:
            r['probki'] = prev.get('probki', r.get('probki'))
            cz['render_s'] = prev.get('czasy_s', {}).get('render_s')
            kor['czas_calkowity_renderu_s'] = prev.get('korekty', {}).get('czas_calkowity_renderu_s',
                                                                           prev.get('korekty', {}).get('czas_calkowity_s'))
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p


def main():
    if '--surowy' in sys.argv:
        i = sys.argv.index('--surowy')
        SUROWY['png'] = Path(sys.argv[i + 1]).resolve()
        if not SUROWY['png'].exists():
            raise SystemExit('brak pliku %s' % SUROWY['png'])
        del sys.argv[i:i + 2]
    FK.main()


if __name__ == '__main__':
    main()
