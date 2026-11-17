# -*- coding: utf-8 -*-
"""Nakładka finałowa na ``render/ujecia_dodatkowe.py`` (przez ``render/ujecia_poprawki_kontekstu.py``): korekty jury
bez edycji plików wspólnych (budynek3d.py, context.py, blib.py …) – wyłącznie opakowanie funkcji po imporcie.
Uruchomienie i argumenty jak ``ujecia_dodatkowe.py`` (+ ``--wycinek X0 X1 Y0 Y1`` – render tylko fragmentu kadru,
ułamki, y od dołu; obraz przycięty do wycinka)::

    nice -n 5 /home/user/aihouse/.venv-render/bin/python -I umwd/render/ujecia_finalne_korekty.py \
        --id zlota-godzina-2 --szer 2000 --probki 64 --out umwd/docs/60_wizualizacje/img/extra/E_zlota-godzina-2.jpg

WARUNKI WSPÓLNE ZESTAWU (zawsze):
 (1) Lamele korony łuku wg ``koncepcja.json`` (elewacje.luk.S, v1.1) i rysunku ``tools/elewacje.py``: lamele
     0,35 × 0,60 m (R 13,40–14,00) w rozstawach 1,35 / 0,675 m w ciągu Fibonacciego, wyśrodkowane na łuku (21 szt.).
     ``budynek3d.Spec`` bierze dziś trzecią liczbę opisu („R 13,40”) jako rozstaw → 2 lamele na łuku. Nakładka
     poprawia ``Spec.lamela`` i podmienia lamele w ``Budynek._wieza_luk`` (przechwycenie ``el`` z materiałem lameli).
     Szkło korony łuku – sitodruk ceramiczny 30 % ton w ton z lamelami (``koncepcja.json``: „sitodruk 30 % na szkle”).
 (2) Ujęcia dzienne (słońce > 3°, preset ≠ zmierzch): ciepłe oprawy (korona, hol, podcień) ściemnione ×0,12 –
     za dnia korona nie jest „ciemnym szkłem z białymi kropkami”.
KOREKTY UJĘCIA (opcjonalne klucze wpisu JSON):
 "woda": {"szorstkosc": 0.02, "fale": 0.12, "barwa": [[r,g,b],[r,g,b]]} – materiał wody (mniej fal i chropowatości
     → czystsze odbicie nieba i portalu; barwa mniej brunatna);
 "tramwaj": {"s0": 6.0, "tor_x": 1.28, "kierunek": -1} – generyczny tramwaj niskopodłogowy (5 członów, 33 m) na
     torze pomostu Mostu Grunwaldzkiego (układ ``context.MostUklad``: s wzdłuż osi od portalu pd., x w lewo);
 "piesi_most": [[s, x, kier], …] – piesi na chodnikach mostu (sylwetki ``budynek3d_otoczenie._prototyp_czlowieka``;
     tylko gdy ludzie włączeni);
 "post_przed": {"woda_cienie_ev": 0.5, "mgla": {"start": 190, "glebokosc": 300, "ev": 0.5, "desat": 0.3}} – krok
     przed ``tools/postprodukcja.py``: rozjaśnienie cieni wody (maska z passu Object Index wody) i perspektywa
     powietrzna dalekiego tła (pass Mist: 0 przy ``start`` m, 1 przy ``start + glebokosc`` m). Surowy PNG zostaje
     jako ``<plik>_surowy.png``.
"""
import argparse
import json
import math
import re
import shutil
import subprocess as _subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, '/home/user/aihouse/umwd/src')
sys.path.insert(0, '/home/user/aihouse/umwd/render')

import bpy  # noqa: E402
import numpy as np  # noqa: E402

import ujecia_poprawki_kontekstu as PK  # noqa: E402  (łata artefaktów context.py + 2 wątki renderu)
from umwd.render import budynek3d  # noqa: E402
from umwd.render.context import MostUklad  # noqa: E402

U = PK.U
KONCEPCJA = U.KONCEPCJA
IDX_WODY = 7
MAT_LAMELI = 'cer:lamele_korony:gladka'
OPRAWY_DZIEN = 0.12


# ============================================================================================== (1) lamele korony
def _parametry_lameli():
    """Z opisu elewacje.luk.S: szer. × głęb., R wewn.–zewn., rozstawy A / B (ciąg Fibonacciego)."""
    k = json.loads(Path(KONCEPCJA).read_text(encoding='utf-8'))
    txt = k['elewacje']['luk']['S']
    f = lambda s: float(s.replace(',', '.'))
    m_wd = re.search(r'(\d+,\d+)\s*×\s*(\d+,\d+)', txt)
    m_r = re.search(r'R\s*(\d+,\d+)\s*[–-]\s*(\d+,\d+)', txt)
    m_ab = re.search(r'rozstaw\w*\s*(\d+,\d+)\s*/\s*(\d+,\d+)', txt)
    w, d = f(m_wd.group(1)), f(m_wd.group(2))
    if m_r:
        d = round(f(m_r.group(2)) - f(m_r.group(1)), 3)
    A, B = f(m_ab.group(1)), f(m_ab.group(2))
    return dict(szer=w, glab=d, A=A, B=B, opis=txt)


LAMELE = _parametry_lameli()


def fib_word(n):
    a, b = 'A', 'AB'
    while len(b) < n:
        a, b = b, b + a
    return b[:n]


def lamele_luku(L, w, A, B):
    """Osie lameli na łuku długości L (jak ``tools/elewacje.lamele_luku``): największa liczba lameli mieszcząca się
    na łuku (zapas ≥ 1 cm od krawędzi – rysunek: 21 szt., 2 cm), rozstawy w ciągu Fibonacciego, układ wyśrodkowany."""
    n = 2
    while True:
        p = [A if c == 'A' else B for c in fib_word(n)]
        if sum(p) + w + 0.02 > L:
            break
        n += 1
    p = [A if c == 'A' else B for c in fib_word(n - 1)]
    s = (L - sum(p)) / 2
    out = [s]
    for q in p:
        s += q
        out.append(s)
    return out


_spec_init = budynek3d.Spec.__init__


def _spec_init_p(self, *a, **k):
    _spec_init(self, *a, **k)
    self.lamela_spec_pierwotna = tuple(self.lamela)
    self.lamela = (LAMELE['szer'], LAMELE['glab'], LAMELE['A'])
    self.lamela_rytm = (LAMELE['A'], LAMELE['B'])


budynek3d.Spec.__init__ = _spec_init_p

_wieza_luk = budynek3d.Budynek._wieza_luk
RAPORT_LAMEL = {}


def _wieza_luk_p(self, G, b, kd, zt, zb):
    el0, szyba0 = self.el, self.szyba
    przechwycone = []

    def el_f(*a, **k):
        mat = a[8] if len(a) > 8 else k.get('mat')
        if mat == MAT_LAMELI:
            przechwycone.append((a, k))
            return None
        return el0(*a, **k)

    def szyba_f(*a, **k):
        a = list(a)
        if len(a) > 7 and a[7] == 'szklo:korona':
            a[7] = 'szklo_sitodruk:korona'
        return szyba0(*a, **k)

    self.el, self.szyba = el_f, szyba_f
    try:
        r = _wieza_luk(self, G, b, kd, zt, zb)
    finally:
        del self.el
        del self.szyba
    if przechwycone:
        a, k = przechwycone[0]
        G_, b_, z0, z1 = a[0], a[1], a[6], a[7]
        w, d = LAMELE['szer'], LAMELE['glab']
        osie = lamele_luku(b_.L, w, LAMELE['A'], LAMELE['B'])
        for sc in osie:
            el0(G_, b_, sc - w / 2, sc + w / 2, -d, 0.0, z0, z1, MAT_LAMELI, **k)
        RAPORT_LAMEL.update(luk_L_m=round(b_.L, 3), lamele_szt=len(osie), szer_m=w, glab_m=d,
                            rozstawy=fib_word(len(osie) - 1).replace('A', 'L').replace('B', 'k'),
                            zapas_krawedzi_m=round(osie[0] - w / 2, 3), przechwycone_ze_Spec=len(przechwycone),
                            spec_pierwotna=list(getattr(self.spec, 'lamela_spec_pierwotna', ())))
        print('[korekty] lamele korony łuku: %d szt. %.2f × %.2f m, rozstawy %.3f/%.3f (Fibonacci), zamiast %d ze Spec'
              % (len(osie), w, d, LAMELE['A'], LAMELE['B'], len(przechwycone)))
    return r


budynek3d.Budynek._wieza_luk = _wieza_luk_p


def _m_szklo_sitodruk(self, m, typ='korona'):
    """Szkło korony łuku z sitodrukiem ceramicznym 30 % ton w ton z lamelami (pokrycie powierzchniowe 30 %)."""
    self.m_szklo(m, typ)
    nt = m.node_tree
    out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL')
    src = out.inputs['Surface'].links[0].from_socket
    base = self._skala(self.spec.barwa('cer_lamele_korony'))
    fr = nt.nodes.new('ShaderNodeBsdfPrincipled')
    fr.inputs['Base Color'].default_value = (*base, 1.0)
    fr.inputs['Roughness'].default_value = 0.55
    mx = nt.nodes.new('ShaderNodeMixShader')
    mx.inputs['Fac'].default_value = 0.30
    nt.links.new(src, mx.inputs[1])
    nt.links.new(fr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])


budynek3d.Materialy.m_szklo_sitodruk = _m_szklo_sitodruk


# ============================================================================================== tramwaj, piesi
class _Siatka:
    def __init__(self):
        self.v, self.f, self.m = [], [], []

    def quad(self, pts, mi):
        i0 = len(self.v)
        self.v += [tuple(p) for p in pts]
        self.f.append(tuple(range(i0, i0 + len(pts))))
        self.m.append(mi)

    def pryzma(self, poly, z0, z1, mi, gora=True, dol=True):
        """Pryzma z wielokąta (lx, ly) CCW."""
        n = len(poly)
        for i in range(n):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
            self.quad([(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)], mi)
        if gora:
            self.quad([(x, y, z1) for x, y in poly], mi)
        if dol:
            self.quad([(x, y, z0) for x, y in reversed(poly)], mi)

    def box(self, x0, x1, y0, y1, z0, z1, mi):
        self.pryzma([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, mi)


def _mat_proste(nazwa, col, rough=0.4, metal=0.0, coat=0.0, emis=None):
    m = bpy.data.materials.get(nazwa) or bpy.data.materials.new(nazwa)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if coat and 'Coat Weight' in b.inputs:
        b.inputs['Coat Weight'].default_value = coat
        b.inputs['Coat Roughness'].default_value = 0.08
    return m


def tramwaj(sc, cfg):
    """Generyczny tramwaj niskopodłogowy (bez barw konkretnego przewoźnika): 5 członów (6,6/6,0/6,6/6,0/6,6 m,
    przeguby 0,30 m), szer. 2,40, wys. pudła 3,10 m + urządzenia dachowe, pantograf na członie środkowym; pas okien
    z ciemnego szkła, drzwi dwuskrzydłowe po obu stronach, fartuch grafitowy. Na torze pomostu, z profilem pomostu."""
    M = MostUklad()
    s0, tor_x, kier = float(cfg.get('s0', 6.0)), float(cfg.get('tor_x', 1.28)), int(cfg.get('kierunek', -1))
    G = _Siatka()
    LAK, SZK, GRF, PRZ, MET, AKC = range(6)
    cz = [(0.0, 6.6), (6.9, 12.9), (13.2, 19.8), (20.1, 26.1), (26.4, 33.0)]
    Ltot, hw = 33.0, 1.20
    zf, zo0, zo1, zd = 0.18, 0.98, 2.50, 3.10
    for i, (a, b) in enumerate(cz):
        nos0, nos1 = (i == 0), (i == len(cz) - 1)
        ch = 0.55
        poly = []
        poly += [(a + ch, -hw)] if nos0 else [(a, -hw)]
        poly += [(b - ch, -hw), (b, -hw + 0.45), (b, hw - 0.45), (b - ch, hw)] if nos1 else [(b, -hw), (b, hw)]
        poly += [(a + ch, hw), (a, hw - 0.45), (a, -hw + 0.45)] if nos0 else [(a, hw)]
        G.pryzma(poly, zf, 0.42, GRF)                         # fartuch
        G.pryzma(poly, 0.42, zd, LAK, dol=False)              # pudło
        G.pryzma([(x * 1.0, y * 0.93) for x, y in poly], zd, zd + 0.10, LAK, dol=False)   # dach
        # pas okien (ciemne szkło, 1,5 cm przed licem) z filarkami
        for sy in (-1, 1):
            y = sy * (hw + 0.015)
            xa, xb = (a + ch + 0.05 if nos0 else a + 0.15), (b - ch - 0.05 if nos1 else b - 0.15)
            q = [(xa, y, zo0), (xb, y, zo0), (xb, y, zo1), (xa, y, zo1)]
            G.quad(q if sy < 0 else q[::-1], SZK)
            G.quad([(xa, y * 1.0005, 0.90), (xb, y * 1.0005, 0.90), (xb, y * 1.0005, 0.96), (xa, y * 1.0005, 0.96)]
                   if sy < 0 else [(xa, y * 1.0005, 0.96), (xb, y * 1.0005, 0.96), (xb, y * 1.0005, 0.90),
                                   (xa, y * 1.0005, 0.90)], AKC)
            nf = max(2, int(round((xb - xa) / 1.75)))
            for j in range(1, nf):
                xc = xa + (xb - xa) * j / nf
                G.box(xc - 0.07, xc + 0.07, y - 0.012 if sy > 0 else y - 0.008, y + 0.008 if sy > 0 else y + 0.012,
                      zo0, zo1, LAK)
            # drzwi dwuskrzydłowe 1,30 m (szkło do posadzki, rama lakierowana)
            xd = (a + b) / 2 + (0.6 if i % 2 else -0.6)
            yd = sy * (hw + 0.022)
            G.box(xd - 0.70, xd + 0.70, min(yd, sy * hw), max(yd, sy * hw), 0.30, 2.42, LAK)
            for xs in (xd - 0.62, xd + 0.02):
                yy = sy * (hw + 0.03)
                q = [(xs, yy, 0.36), (xs + 0.60, yy, 0.36), (xs + 0.60, yy, 2.36), (xs, yy, 2.36)]
                G.quad(q if sy < 0 else q[::-1], SZK)
        # urządzenia dachowe
        if i in (0, 2, 4):
            xm = (a + b) / 2
            G.box(xm - 1.6, xm + 1.6, -0.80, 0.80, zd + 0.10, zd + 0.42, LAK)
    # przeguby (mieszki)
    for (a, b), (c, d) in zip(cz[:-1], cz[1:]):
        G.box(b - 0.02, c + 0.02, -1.08, 1.08, 0.40, 3.0, PRZ)
    # czoła: szyba czołowa i boczne szyby kabiny na fazach
    for (x_n, sg) in ((0.0, 1), (Ltot, -1)):
        x0 = x_n
        xs_ = x0 - sg * 0.012
        q = [(xs_, -0.72, 1.00), (xs_, 0.72, 1.00), (xs_, 0.66, 2.70), (xs_, -0.66, 2.70)]
        G.quad(q if sg < 0 else q[::-1], SZK)
        G.box(min(x0, x0 - sg * 0.06), max(x0, x0 - sg * 0.06), -0.72, 0.72, 0.30, 0.55, GRF)   # zderzak
    # pantograf (rama niska + ramiona do ok. 5,5 m nad główką szyny)
    xm = (cz[2][0] + cz[2][1]) / 2
    G.box(xm - 1.0, xm + 1.0, -0.55, 0.55, zd + 0.10, zd + 0.30, MET)
    for (xa, za, xb, zb) in ((xm - 0.9, zd + 0.30, xm + 0.6, zd + 1.40), (xm + 0.6, zd + 1.40, xm - 0.2, 5.50)):
        for yy in (-0.35, 0.35):
            dx, dz = xb - xa, zb - za
            L = math.hypot(dx, dz)
            nx, nz = -dz / L * 0.03, dx / L * 0.03
            G.quad([(xa - nx, yy - 0.03, za - nz), (xb - nx, yy - 0.03, zb - nz), (xb + nx, yy + 0.03, zb + nz),
                    (xa + nx, yy + 0.03, za + nz)], MET)
    G.box(xm - 0.30, xm - 0.10, -0.85, 0.85, 5.45, 5.52, MET)
    # odwzorowanie: lx wzdłuż jazdy od czoła, ly w lewo od kierunku jazdy → (s, x, z) mostu
    verts = []
    for (lx, ly, lz) in G.v:
        s = s0 - kier * lx
        x = tor_x + kier * ly
        e, n, _ = M.W(s, x, 0.0)
        verts.append((e, n, float(M.zpom(s)) + 0.027 + lz))
    faces = [tuple(reversed(f)) for f in G.f]          # odwzorowanie zmienia skrętność
    me = bpy.data.meshes.new('tramwaj')
    me.from_pydata(verts, [], faces)
    me.update()
    mats = [_mat_proste('UJ_tram_lakier', (0.80, 0.80, 0.78), 0.30, coat=0.6),
            _mat_proste('UJ_tram_szklo', (0.012, 0.014, 0.016), 0.04),
            _mat_proste('UJ_tram_grafit', (0.045, 0.047, 0.05), 0.55),
            _mat_proste('UJ_tram_mieszek', (0.03, 0.03, 0.03), 0.9),
            _mat_proste('UJ_tram_metal', (0.30, 0.31, 0.32), 0.35, metal=0.9),
            _mat_proste('UJ_tram_akcent', (0.30, 0.035, 0.03), 0.35, coat=0.5)]
    for m in mats:
        me.materials.append(m)
    for p, mi in zip(me.polygons, G.m):
        p.material_index = mi
    ob = bpy.data.objects.new('tramwaj_most', me)
    sc.collection.objects.link(ob)
    s_a, s_b = sorted((s0, s0 - kier * Ltot))
    print('[korekty] tramwaj: s %.1f–%.1f, tor x %.2f, kierunek %+d, %d ścian' % (s_a, s_b, tor_x, kier, len(faces)))
    return ob


def piesi_most(sc, lista, seed=7):
    """Piesi na chodnikach mostu (chodnik +0,15 m nad jezdnią; x 6,05–8,25 od osi)."""
    from umwd.render import budynek3d_otoczenie as BO
    mat = bpy.data.materials.get('B_ludzie')
    if mat is None:
        print('[korekty] brak materiału B_ludzie (scena bez ludzi) – piesi na moście pominięci')
        return []
    M = MostUklad()
    warianty = ((1.78, 0.30, 0.38, False, False, ''), (1.66, 0.28, 0.42, True, True, ''),
                (1.82, 0.0, 0.50, False, False, 'telefon'), (1.64, 0.30, 0.36, True, False, ''),
                (1.75, 0.30, 0.50, False, True, ''), (1.69, 0.0, 0.40, True, False, 'kieszen'),
                (1.80, 0.32, 0.45, False, False, ''), (1.60, 0.30, 0.36, True, True, ''))
    kat_osi = math.atan2(M.u[1], M.u[0])
    obs = []
    for i, (s, x, kier) in enumerate(lista):
        H, chod, pl, kob, tb, poza = warianty[(i + seed) % len(warianty)]
        me = BO._prototyp_czlowieka('czlowiek_most_%02d' % i, H, chod, pl, kob, seed=100 + i, torba=tb, poza=poza)
        me.materials.append(mat)
        ob = bpy.data.objects.new('czlowiek_most_%02d' % i, me)
        sc.collection.objects.link(ob)
        e, n, _ = M.W(s, x, 0.0)
        ob.location = (e, n, float(M.zpom(s)) + 0.15)
        kier_r = kat_osi + (0.0 if kier > 0 else math.pi)
        ob.rotation_euler = (0.0, 0.0, kier_r - math.pi / 2)
        obs.append(ob)
    print('[korekty] piesi na moście: %d' % len(obs))
    return obs


# ============================================================================================== woda, oprawy
def popraw_wode(cfg):
    ob = bpy.data.objects.get('woda')
    if ob is None or not ob.data.materials:
        return
    ob.pass_index = IDX_WODY
    if not cfg:
        return
    m = ob.data.materials[0]
    for n in m.node_tree.nodes:
        if n.type == 'BUMP' and 'fale' in cfg:
            n.inputs['Strength'].default_value = float(cfg['fale'])
        elif n.type == 'BSDF_PRINCIPLED' and 'szorstkosc' in cfg:
            n.inputs['Roughness'].default_value = float(cfg['szorstkosc'])
        elif n.type == 'VALTORGB' and 'barwa' in cfg:
            for el, c in zip(n.color_ramp.elements, cfg['barwa']):
                el.color = (*c, 1.0)
    print('[korekty] woda: %s' % json.dumps(cfg))


def sciemnij_oprawy(mnoznik):
    m = bpy.data.materials.get('B_wn_lampa:cieple')
    if m is None:
        return None
    for n in m.node_tree.nodes:
        if n.type == 'EMISSION':
            if 'UJ_moc0' not in m:
                m['UJ_moc0'] = n.inputs['Strength'].default_value
            n.inputs['Strength'].default_value = m['UJ_moc0'] * mnoznik
            return n.inputs['Strength'].default_value
    return None


# ============================================================================================== opakowania U
UJECIE = {}          # bieżący wpis (z JSON), ustawiany w render_ujecia
ARGS_EXTRA = argparse.Namespace(wycinek=None)

_zb = U.zbuduj_scene


def _zbuduj_scene_p(ludzie, opts_bud=None):
    r = _zb(ludzie, opts_bud)
    sc = r[0]
    for k in UJECIA_WYBRANE:
        popraw_wode(k.get('woda'))
        if k.get('tramwaj'):
            tramwaj(sc, k['tramwaj'])
        if k.get('piesi_most') and ludzie:
            piesi_most(sc, k['piesi_most'])
        break
    return r


U.zbuduj_scene = _zbuduj_scene_p

_us = U.ustaw_swiatlo


def _ustaw_swiatlo_p(sc, k):
    sw = _us(sc, k)
    dzien = sw['el'] > 3 and k['preset'] != 'zmierzch'
    sw['oprawy_cieple'] = sciemnij_oprawy(OPRAWY_DZIEN if dzien else 1.0)
    mg = (k.get('post_przed') or {}).get('mgla') or {}
    ms = sc.world.mist_settings
    ms.start = float(mg.get('start', 190.0))
    ms.depth = float(mg.get('glebokosc', 300.0))
    ms.falloff = 'LINEAR'
    if RAPORT_LAMEL:
        sw['lamele_korony'] = dict(RAPORT_LAMEL)
    return sw


U.ustaw_swiatlo = _ustaw_swiatlo_p


def _kompozytor(sc, prefix):
    sc.render.engine = 'CYCLES'          # pass Object Index istnieje tylko w Cycles (render_settings ustawia go później)
    vl = sc.view_layers[0]
    vl.use_pass_mist = True
    vl.use_pass_object_index = True
    sc.render.use_compositing = True
    sc.render.compositor_device = 'CPU'
    ng = bpy.data.node_groups.new('UJ_komp', 'CompositorNodeTree')
    sc.compositing_node_group = ng
    rl = ng.nodes.new('CompositorNodeRLayers')
    rl.scene = sc
    rl.layer = vl.name
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    go = ng.nodes.new('NodeGroupOutput')
    ng.links.new(rl.outputs['Image'], go.inputs[0])
    fo = ng.nodes.new('CompositorNodeOutputFile')
    fo.directory = str(U.PNG_DIR) + '/'
    fo.file_name = prefix
    fo.format.media_type = 'IMAGE'
    fo.format.file_format = 'OPEN_EXR'
    fo.format.color_depth = '32'
    wyj = {o.name: o for o in rl.outputs}
    for nazwa, gniazda in (('mgla', ('Mist',)), ('idx', ('Object Index', 'IndexOB'))):
        g = next((wyj[x] for x in gniazda if x in wyj), None)
        if g is None:
            raise RuntimeError('RLayers bez passu %s (wyjścia: %s)' % (gniazda, list(wyj)))
        fo.file_output_items.new('FLOAT', nazwa)
        ng.links.new(g, fo.inputs[nazwa])
    return {n: U.PNG_DIR / ('%s%s.exr' % (prefix, n)) for n in ('mgla', 'idx')}


def _wczytaj_exr(p):
    im = bpy.data.images.load(str(p))
    im.colorspace_settings.name = 'Non-Color'
    a = np.array(im.pixels[:], dtype=np.float32).reshape(im.size[1], im.size[0], -1)[::-1]
    bpy.data.images.remove(im)
    return a[..., 0]


def _s2l(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def _l2s(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def _lum(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def post_przed(png, passy, cfg, raport):
    """Krok przed wspólną postprodukcją: perspektywa powietrzna (Mist) i rozjaśnienie cieni wody (Object Index)."""
    from PIL import Image
    from scipy import ndimage
    png = Path(png)
    shutil.copyfile(png, png.with_name(png.stem + '_surowy.png'))
    a = np.asarray(Image.open(png).convert('RGB'), dtype=np.float32) / 255.0
    lin = _s2l(a)
    mist = _wczytaj_exr(passy['mgla'])
    idx = _wczytaj_exr(passy['idx'])
    if mist.shape != a.shape[:2]:
        raise RuntimeError('passy %s ≠ obraz %s' % (mist.shape, a.shape[:2]))
    info = {}
    mg = cfg.get('mgla')
    if mg:
        niebo = (mist > 0.9999) & (idx < 0.5)
        w = np.clip(mist, 0, 1) ** float(mg.get('wykladnik', 0.8))
        w = np.where(niebo, float(mg.get('niebo', 0.0)), w)
        w = ndimage.gaussian_filter(w, 0.8)
        lin = lin * (2.0 ** (float(mg.get('ev', 0.5)) * w))[..., None]
        L = _lum(lin)[..., None]
        lin = L + (lin - L) * (1.0 - float(mg.get('desat', 0.3)) * w[..., None])
        info['mgla_udzial_kadru_w>0.3'] = round(float((w > 0.3).mean()), 3)
    ev = cfg.get('woda_cienie_ev')
    if ev:
        mw = ndimage.gaussian_filter((np.abs(idx - IDX_WODY) < 0.5).astype(np.float32), 1.0)
        Ld = _lum(_l2s(lin))
        t = np.clip((Ld - 0.10) / (0.55 - 0.10), 0, 1)
        cien = 1.0 - t * t * (3 - 2 * t)
        lin = lin * (2.0 ** (float(ev) * cien * mw))[..., None]
        info['woda_udzial_kadru'] = round(float((mw > 0.5).mean()), 3)
        info['woda_luma_przed_po'] = [round(float(Ld[mw > 0.5].mean()), 3),
                                      round(float(_lum(_l2s(lin))[mw > 0.5].mean()), 3)]
    out = (_l2s(lin) * 255 + 0.5).astype(np.uint8)
    Image.fromarray(out).save(png)
    raport.update(info)
    print('[korekty] post_przed: %s' % json.dumps(info, ensure_ascii=False))


class _SubprocessShim:
    """U.subprocess.run(postprodukcja) → najpierw post_przed na PNG, potem wspólna postprodukcja."""

    def __init__(self):
        self.passy, self.cfg, self.raport = None, None, {}

    def run(self, args, **kw):
        if self.cfg and self.passy and str(U.POSTPRODUKCJA) in [str(x) for x in args]:
            try:
                post_przed(args[3], self.passy, self.cfg, self.raport)
            except Exception as e:      # brak passów → postprodukcja bez kroku wstępnego
                self.raport['blad'] = repr(e)
                print('[korekty] post_przed – błąd: %r' % (e,))
        return _subprocess.run(args, **kw)


SHIM = _SubprocessShim()
U.subprocess = SHIM

_ru = U.render_ujecia


def rzut_dodatkow(sc):
    """Położenie tramwaju i pieszych na moście w kadrze (x, y ∈ [0, 1], y od dołu) i widoczność środka (promień)."""
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    cam = sc.camera
    dg = bpy.context.evaluated_depsgraph_get()
    loc = cam.matrix_world.translation
    out = {}
    for ob in [o for o in sc.objects if o.name.startswith(('tramwaj_most', 'czlowiek_most_'))]:
        pts = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        uv = [world_to_camera_view(sc, cam, p) for p in pts]
        c = sum(pts, Vector()) / 8.0
        d = c - loc
        hit, pos, nrm, i_, obh, mx = sc.ray_cast(dg, loc, d.normalized(), distance=d.length + 1.0)
        out[ob.name] = dict(x0=round(min(v.x for v in uv), 3), x1=round(max(v.x for v in uv), 3),
                            y0=round(min(v.y for v in uv), 3), y1=round(max(v.y for v in uv), 3),
                            odl_m=round(d.length, 1), srodek_trafia=(obh.name if hit else None))
    return out


def _render_ujecia_p(sc, k, a, DZ, kat, czasy, out_jpg):
    out_jpg = Path(out_jpg)
    SHIM.cfg = k.get('post_przed')
    SHIM.raport = {}
    SHIM.passy = _kompozytor(sc, out_jpg.stem + '_pass_') if SHIM.cfg else None
    if ARGS_EXTRA.wycinek:
        x0, x1, y0, y1 = ARGS_EXTRA.wycinek
        sc.render.use_border = True
        sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = y0, y1
        SHIM.cfg = None                  # passy z wycinka – bez kroku wstępnego (kontrola detalu)
    t0 = time.time()
    r = _ru(sc, k, a, DZ, kat, czasy, out_jpg)
    r['dodatki_w_kadrze'] = rzut_dodatkow(sc)
    r['korekty'] = dict(lamele_korony=dict(RAPORT_LAMEL), oprawy_cieple_moc=r.get('slonce', {}).get('oprawy_cieple'),
                        post_przed=dict(SHIM.raport, cfg=SHIM.cfg), wycinek=ARGS_EXTRA.wycinek,
                        czas_calkowity_s=round(time.time() - t0, 1))
    plik_r = out_jpg.with_name(out_jpg.stem + '_kontrola.json')
    plik_r.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding='utf-8')
    return r


U.render_ujecia = _render_ujecia_p
UJECIA_WYBRANE = []


def main():
    global ARGS_EXTRA
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--wycinek', nargs=4, type=float, default=None)
    ARGS_EXTRA, reszta = ap.parse_known_args()
    sys.argv = [sys.argv[0]] + reszta
    # wpisy wybranych ujęć (do budowy dodatków sceny przed renderem)
    pj = U.JSON_DOMYSLNY
    if '--json' in reszta:
        pj = Path(reszta[reszta.index('--json') + 1])
    ids = []
    if '--id' in reszta:
        i = reszta.index('--id') + 1
        while i < len(reszta) and not reszta[i].startswith('--'):
            ids.append(reszta[i])
            i += 1
    po_id = {u['id']: u for u in U.wczytaj_ujecia(pj)}
    UJECIA_WYBRANE[:] = [po_id[i] for i in ids if i in po_id]
    U.main()


if __name__ == '__main__':
    main()
