# -*- coding: utf-8 -*-
"""Hala Obywatelska (SW.01c, parter wieży) – szczegółowe wnętrze do wizualizacji W6.

Geometria z ``model/budynek.json`` (kondygnacja P: wielokąt SW.01c, ściany wewnętrzne i trzony, drzwi, słupy),
oś przekątna z ``model/koncepcja.json`` (``parter.wieza[0].os``: Brama Mostowa → ogród, 211,7°, szer. ≥ 6,3 m).
Budowane w ``Budynek.wnetrza()`` przy opcji ``hala_szczegolowa=True`` (zamiast schematycznego holu parteru):

* posadzka: pas osi 6,3 m z granitu płomieniowanego (płyty w układzie osi), reszta – lastryko z kruszywa
  z gruzu rozbiórkowego (pola 1,20 m, listwy mosiężne); ścieżka dotykowa (pasy prowadzące 0,30 m z ryflami)
  od drzwi Bramy Mostowej osią do drzwi ogrodowych, odgałęzienia do informacji i tyflomapy;
* ściany i trzony z budynek.json (tynk / okładzina dębowa trzonów, cokół granitowy), skrzydła drzwi;
* słupy Ø 0,56 m (beton architektoniczny), sufit z lameli dębowych wzdłuż osi na ciemnym tle akustycznym,
  oprawy downlight 3000 K (lampy punktowe Cycles – rzeczywiste oświetlenie wnętrza);
* informacja (8 m²) z niską ladą 0,76 m (dostępność) i wyższą 1,05 m, tyflomapa przy wejściu;
* lapidarium – fragmenty kamieniarki kwartału (gzyms, bęben kolumny, kapitel, tralki, płyta z inskrypcją)
  na cokołach z oświetleniem akcentowym; poczekalnia (40 m²) przy przeszkleniu ogrodowym: ławy dębowe;
* rośliny w donicach (fikusy – proceduralne), ludzie (prototypy z ``budynek3d_otoczenie``), osoba na wózku przy
  niskiej ladzie.

Rozbieżność danych (zgłoszona koordynatorowi): koniec osi z koncepcja.json (84,32; 43,12) leży wg budynek.json
w PHS.04 (toalety strefy konferencyjnej); ściana ogrodowa holu to odcinek x 87,3–94,9 (u 13,2–21,0 elewacji pd.).
Drzwi ogrodowe hali przyjęto w środku tej ściany (ZALOZENIA['wejscie_ogrodowe_hali_S']), ścieżka dotykowa
skręca do nich z osi.
"""
from __future__ import annotations

import json
import math

import numpy as np
import bpy
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box as sbox
from shapely.ops import unary_union

from umwd.render.budynek3d import Geo, UMWD

BUDYNEK_JSON = UMWD / 'model' / 'budynek.json'

LAMPA_BARWA = (1.0, 0.80, 0.58)          # ~3000 K


def _mp(poly):
    """'poligon' z budynek.json ([[[zewn], [otwór]…], …] – multipoligon albo [[zewn], [otwór]…] – poligon)
    → shapely (Multi)Polygon."""
    if poly and poly[0] and poly[0][0] and isinstance(poly[0][0][0], (int, float)):
        poly = [poly]
    czesci = []
    for pg in poly:
        if not pg or len(pg[0]) < 3:
            continue
        P = Polygon(pg[0], [r for r in pg[1:] if len(r) >= 3]).buffer(0)
        if not P.is_empty:
            czesci.append(P)
    return unary_union(czesci) if czesci else Polygon()


def _czesci(g):
    if g.is_empty:
        return []
    return [g] if isinstance(g, Polygon) else [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]


class Hala:
    def __init__(self, B):
        self.B = B
        J = json.loads(BUDYNEK_JSON.read_text(encoding='utf-8'))
        self.P = next(k for k in J['kondygnacje'] if k['id'] == 'P')
        self.pom = {r['numer']: _mp(r['poligon']) for r in self.P['pomieszczenia']}
        self.H = self.pom['SW.01c']
        try:
            os_ = next(s['os'] for s in B.spec.K['parter']['wieza'] if 'os' in s)
        except Exception:
            os_ = {'od': [101.863, 71.566], 'do': [84.321, 43.124], 'min_szer_m': 6.3}
        self.od = np.array(os_['od'], float)
        self.do = np.array(os_['do'], float)
        self.szer_osi = float(os_.get('min_szer_m', 6.3))
        d = self.do - self.od
        self.dl = float(np.linalg.norm(d))
        self.d = d / self.dl
        self.lewo = np.array([-self.d[1], self.d[0]])
        self.suf = B.spec.kondygnacje('W')[0]['sufit']
        # drzwi ogrodowe: środek przęsła elewacji pd. z ZALOZENIA (u) – punkt na licu i normalna do wnętrza
        A = np.array(B.spec.K['bryly'][0]['obrys_ccw'][0], float)
        Bp = np.array(B.spec.K['bryly'][0]['obrys_ccw'][1], float)
        t = (Bp - A) / np.linalg.norm(Bp - A)
        u0, u1 = B.Z.get('wejscie_ogrodowe_hali_S', (15.9, 18.3))
        self.drzwi_ogr = A + t * (u0 + u1) / 2
        self.n_wew = np.array([-t[1], t[0]])            # do wnętrza (na pn.)
        self.info = {'powierzchnia_m2': round(self.H.area, 1)}
        self.obiekty = []

    # ------------------------------------------------------------------ pomocnicze
    def a_l(self, a, l):
        """Punkt w układzie osi: a – odległość od drzwi Bramy Mostowej wzdłuż osi, l – w lewo (patrząc ku ogrodowi)."""
        return self.od + self.d * a + self.lewo * l

    def uv_osi(self, x, y):
        q = np.array([x, y]) - self.od
        return float(q @ self.d), float(q @ self.lewo)

    def plyta(self, G, geom, z, mat, uv='osi', cell=1.2):
        """Pozioma płyta (górna powierzchnia) z triangulacją i fu/fv w układzie osi (albo świata)."""
        from umwd.render.context import triangulacja
        if geom.is_empty:
            return
        V2, F = triangulacja(geom, cell)
        for f in F:
            pts = [V2[k] for k in f]
            if (pts[1][0] - pts[0][0]) * (pts[2][1] - pts[0][1]) - (pts[1][1] - pts[0][1]) * (pts[2][0] - pts[0][0]) < 0:
                pts = [pts[0], pts[2], pts[1]]
            uvs = [self.uv_osi(*p) if uv == 'osi' else (p[0], p[1]) for p in pts]
            G.face([(p[0], p[1], z) for p in pts], uvs, mat)

    def prostokat(self, c, kier, dl, szer):
        """Prostokąt o środku c, osi długiej ``kier`` (wektor), długości dl i szerokości szer."""
        k = np.asarray(kier, float)
        k = k / np.linalg.norm(k)
        n = np.array([-k[1], k[0]])
        c = np.asarray(c, float)
        return Polygon([c - k * dl / 2 - n * szer / 2, c + k * dl / 2 - n * szer / 2,
                        c + k * dl / 2 + n * szer / 2, c - k * dl / 2 + n * szer / 2])

    # ------------------------------------------------------------------ budowa
    def buduj(self, G):
        B = self.B
        self.coll = B.kol['wnetrza']
        self.posadzka(G)
        self.sciany(G)
        self.slupy(G)
        self.sufit(G)
        self.informacja(G)
        self.lapidarium(G)
        self.poczekalnia(G)
        self.informacja_mosiezna(G)
        self.rosliny()
        if B.o.get('ludzie', True):
            self.ludzie()
        B.info['hala_obywatelska'] = self.info

    def posadzka(self, G):
        H = self.H
        pas = LineString([self.od - self.d * 2, self.do]).buffer(self.szer_osi / 2, cap_style=2).intersection(H)
        reszta = H.difference(pas)
        linia = LineString([self.od - self.d * 2, self.do])
        obr = pas.difference(linia.buffer(self.szer_osi / 2 - 0.30, cap_style=2))
        srodek = pas.difference(obr)
        self.plyta(G, srodek, 0.0, 'granit')
        self.plyta(G, obr, 0.0, 'granit:ciemny')
        self.plyta(G, reszta, 0.0, 'wn_terrazzo')
        self.info['posadzka_m2'] = {'granit_os': round(pas.area, 1), 'lastryko': round(reszta.area, 1)}
        # ścieżka dotykowa: wejście → oś → skręt do drzwi ogrodowych; odgałęzienia: informacja, tyflomapa
        a_skret = 17.0
        p_wej = self.a_l(0.8, 0.0)
        p_skret = self.a_l(a_skret, 0.0)
        p_ogr = self.drzwi_ogr + self.n_wew * 1.0
        self.p_info = self.a_l(9.0, -3.0)
        self.p_tyflo = self.a_l(2.4, 1.9)
        trasy = [[p_wej, p_skret, p_ogr],
                 [self.a_l(8.0, 0.0), self.a_l(8.0, -1.75)],
                 [self.a_l(2.4, 0.0), self.a_l(2.4, 1.45)]]
        dl = 0.0
        for tr in trasy:
            for a, b in zip(tr[:-1], tr[1:]):
                k = b - a
                L = float(np.linalg.norm(k))
                k = k / L
                n = np.array([-k[1], k[0]])
                c0, c1 = a - k * 0.15, b + k * 0.15
                q = [c0 - n * 0.15, c1 - n * 0.15, c1 + n * 0.15, c0 + n * 0.15]
                uvs = [(-0.15, 0.0), (-0.15, L), (0.15, L), (0.15, 0.0)]
                # ryfle wzdłuż kierunku ruchu: fu = współrzędna poprzeczna
                G.face([(p[0], p[1], 0.004) for p in q], uvs, 'wn_dotyk')
                for i in range(4):
                    p, r = q[i], q[(i + 1) % 4]
                    G.face([(p[0], p[1], 0.0), (r[0], r[1], 0.0), (r[0], r[1], 0.004), (p[0], p[1], 0.004)],
                           [(0, 0)] * 4, 'wn_dotyk')
                dl += L
        self.info['sciezka_dotykowa_m'] = round(dl, 1)

    def sciany(self, G):
        B = self.B
        sc = self.P['sciany']
        Wp = B.poly['W'].buffer(-0.3)
        n = 0
        for klucz, mat in (('wewnetrzne', 'wn_tynk'), ('trzony', 'wn_drewno:jasne')):
            for w in sc.get(klucz, []):
                g = _mp(w).intersection(Wp)
                for P in _czesci(g):
                    if P.area < 0.01:
                        continue
                    G.pryzma(P, 0.0, self.suf, mat, gora=False, dno=False)
                    # cokół granitowy 0,10 m (lekko wysunięty) od strony holu
                    if P.distance(self.H) < 0.4:
                        ck = P.buffer(0.012, join_style=2).difference(P.buffer(-0.001))
                        G.pryzma(ck, 0.0, 0.10, 'granit:ciemny', gora=True, dno=False)
                    n += 1
        # skrzydła drzwi od strony holu (dąb, ościeżnica metalowa)
        nd = 0
        for d in self.P['drzwi']:
            p0, p1 = np.array(d['p0']), np.array(d['p1'])
            c = (p0 + p1) / 2
            if not self.H.buffer(1.0).contains(Point(c)):
                continue
            k = p1 - p0
            w = float(np.linalg.norm(k))
            ram = self.prostokat(c, k, w + 0.12, 0.30)
            lis = self.prostokat(c, k, w, 0.28)
            G.pryzma(ram.difference(self.prostokat(c, k, w, 0.40)), 0.0, 2.52, 'metal', gora=True, dno=False)
            G.pryzma(lis, 0.0, 2.45, 'wn_drewno', gora=False, dno=False)
            G.pryzma(self.prostokat(c, k, w + 0.12, 0.30), 2.45, 2.52, 'metal', gora=False, dno=True)
            nd += 1
        self.info['sciany_obiekty'] = n
        self.info['drzwi'] = nd

    def slupy(self, G):
        n = 0
        for s in self.P['slupy']:
            c = Point(s)
            if self.H.buffer(0.35).contains(c):
                G.pryzma(c.buffer(0.28, 32), 0.0, self.suf, 'beton', gora=False, dno=False)
                G.pryzma(c.buffer(0.30, 32), 0.0, 0.08, 'granit:ciemny', gora=True, dno=False)
                n += 1
        self.info['slupy'] = n

    def sufit(self, G):
        """Lamele dębowe 0,05 × 0,12 co 0,15 m wzdłuż osi, tło akustyczne ciemne, downlighty w siatce osi."""
        H = self.H.buffer(-0.02, join_style=2)
        z0, z1 = self.suf - 0.26, self.suf - 0.14
        self.plyta(G, H, self.suf - 0.03, 'wn_ciemne', uv='swiat', cell=None)
        # odwrócenie płyty tła (normalna w dół): ściany Geo dwustronne w Cycles – wystarczy
        xs = [self.uv_osi(*p) for p in H.exterior.coords]
        a_min, a_max = min(p[0] for p in xs) - 1, max(p[0] for p in xs) + 1
        l_min, l_max = min(p[1] for p in xs) - 1, max(p[1] for p in xs) + 1
        n = 0
        for l in np.arange(l_min, l_max, 0.15):
            pas = Polygon([self.a_l(a_min, l), self.a_l(a_max, l), self.a_l(a_max, l + 0.05), self.a_l(a_min, l + 0.05)])
            for P in _czesci(pas.intersection(H)):
                if P.area < 0.005:
                    continue
                G.pryzma(P, z0, z1, 'wn_drewno:jasne', gora=False, dno=True)
                n += 1
        # downlighty: siatka 2,4 (wzdłuż osi) × 1,8 m (w poprzek), w szczelinach lameli
        lampy = []
        for a in np.arange(math.floor(a_min / 2.4) * 2.4 + 1.2, a_max, 2.4):
            for l in np.arange(math.floor(l_min / 1.8) * 1.8 + 0.9 + 0.025, l_max, 1.8):
                p = self.a_l(a, l)
                if self.H.buffer(-0.9).contains(Point(p)):
                    lampy.append(p)
        for p in lampy:
            G.pryzma(Point(p).buffer(0.075, 16), z0 - 0.005, z0, 'wn_lampa:cieple', gora=False, dno=True)
        self.lampy_punktowe(lampy, z0 - 0.02, moc=self.B.o.get('hala_moc_lampy', 55.0), kat=110.0, nazwa='downlight')
        self.info['lamele'] = n
        self.info['downlight'] = len(lampy)

    def lampy_punktowe(self, punkty, z, moc, kat, nazwa, cel=None, barwa=LAMPA_BARWA, promien=0.04):
        from mathutils import Vector
        for i, p in enumerate(punkty):
            ld = bpy.data.lights.new('%s_%02d' % (nazwa, i), 'SPOT')
            ld.energy = moc
            ld.color = barwa
            ld.spot_size = math.radians(kat)
            ld.spot_blend = 0.6
            ld.shadow_soft_size = promien
            ob = bpy.data.objects.new(ld.name, ld)
            ob.location = (p[0], p[1], z + self.B.DZ)
            if cel is not None:
                c = cel[i] if isinstance(cel, (list, tuple)) and len(cel) == len(punkty) and hasattr(cel[i], '__len__') else cel
                v = Vector((c[0] - p[0], c[1] - p[1], (c[2] if len(c) > 2 else 0.5) - z))
                ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
            self.coll.objects.link(ob)

    def informacja(self, G):
        """Lada informacji: dąb jasny, blat granitowy; niska część 0,76 m (od strony wejścia) i wyższa 1,05 m;
        za ladą stanowisko; tyflomapa przy wejściu (pulpit z brązu 0,60 × 0,45 nachylony 30°)."""
        c = self.p_info
        k = self.d
        n = self.lewo
        # niska część (1,2 m) bliżej wejścia, wysoka (2,2 m) dalej; głębokość 0,75
        niska = self.prostokat(c - k * 1.15, k, 1.2, 0.75)
        wysoka = self.prostokat(c + k * 0.55, k, 2.2, 0.75)
        G.pryzma(niska.buffer(-0.03), 0.10, 0.73, 'wn_drewno:jasne', gora=False, dno=False)
        G.pryzma(niska.buffer(-0.04), 0.0, 0.10, 'wn_ciemne', gora=False, dno=False)
        G.pryzma(niska, 0.73, 0.76, 'granit:ciemny')
        G.pryzma(wysoka.buffer(-0.03), 0.10, 1.02, 'wn_drewno:jasne', gora=False, dno=False)
        G.pryzma(wysoka.buffer(-0.04), 0.0, 0.10, 'wn_ciemne', gora=False, dno=False)
        G.pryzma(wysoka, 1.02, 1.05, 'granit:ciemny')
        # blat roboczy za ladą (0,75) i monitor
        G.pryzma(self.prostokat(c + k * 0.55 - n * 0.55, k, 2.0, 0.45), 0.72, 0.75, 'wn_biurko')
        G.pryzma(self.prostokat(c + k * 0.3 - n * 0.6, k, 0.55, 0.04), 0.80, 1.12, 'wn_ciemne')
        # napis „INFORMACJA” – pas mosiężny na froncie lady (bez tekstu – czytelny pas)
        G.pryzma(self.prostokat(c + k * 0.55 + n * 0.385, k, 1.6, 0.012), 0.80, 0.88, 'litery')
        # lampy wiszące nad ladą (3 × walec świecący)
        for i, a in enumerate((-0.9, 0.2, 1.3)):
            p = c + k * a
            G.pryzma(Point(p).buffer(0.13, 24), 2.55, 2.85, 'wn_lampa:cieple', gora=True, dno=True)
            G.pryzma(Point(p).buffer(0.006, 6), 2.85, self.suf - 0.26, 'metal', gora=False, dno=False)
        self.lampy_punktowe([c + k * a for a in (-0.9, 0.2, 1.3)], 2.5, moc=30.0, kat=120.0, nazwa='lada')
        # tyflomapa
        t = self.p_tyflo
        G.pryzma(Point(t).buffer(0.04, 12), 0.0, 0.85, 'metal', gora=True, dno=False)
        pl = self.prostokat(t, self.lewo, 0.6, 0.45)
        V = [np.array(p) for p in list(pl.exterior.coords)[:4]]
        zc = 0.95
        pts = []
        for p in V:
            r = float((p - t) @ self.d)          # nachylenie ku wejściu (w stronę −d)
            pts.append((p[0], p[1], zc - r * math.tan(math.radians(30))))
        G.face(pts, [(0, 0), (0.6, 0), (0.6, 0.45), (0, 0.45)], 'litery')
        G.face([(x, y, z - 0.02) for x, y, z in pts[::-1]], [(0, 0)] * 4, 'metal')
        self.info['informacja'] = [round(float(c[0]), 2), round(float(c[1]), 2)]

    def lapidarium(self, G):
        """Lapidarium wzdłuż ściany kancelarii (SW.02) po lewej stronie przejścia – fragmenty kamieniarki kwartału
        (pierzeja 1934): gzyms, bęben kolumny, kapitel, tralki balustrady, płyta z inskrypcją; cokoły z granitu
        ciemnego, oświetlenie akcentowe."""
        sw02 = self.pom.get('SW.02')
        if sw02 is None or sw02.is_empty:
            return
        # odcinek ściany SW.02 najbliższy osi, od strony holu
        kraw = None
        best = 1e9
        c = list(sw02.exterior.coords)
        for a, b in zip(c[:-1], c[1:]):
            L = LineString([a, b])
            if L.length < 3.0:
                continue
            mid = np.array(L.interpolate(0.5, normalized=True).coords[0])
            d = abs(float((mid - self.od) @ self.lewo))
            if self.H.buffer(0.6).contains(Point(mid)) and d < best:
                best, kraw = d, (np.array(a), np.array(b))
        if kraw is None:
            return
        a, b = kraw
        # początek odcinka po stronie przeciwnej do drzwi kancelarii (drzwi zostają wolne)
        dsw = next((d for d in self.P['drzwi'] if d.get('numer') == 'SW.02'), None)
        if dsw is not None:
            cd = (np.array(dsw['p0']) + np.array(dsw['p1'])) / 2
            if np.linalg.norm(cd - a) < np.linalg.norm(cd - b):
                a, b = b, a
        k = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([-k[1], k[0]])
        if self.H.contains(Point((a + b) / 2 + nrm * 0.8)) is False:
            nrm = -nrm
        L = float(np.linalg.norm(b - a))
        # wielokąty pomieszczeń są „w świetle ścian” – lico od strony holu leży o grubość ściany dalej
        t_sc = float(self.H.distance(Point((a + b) / 2)))
        a, b = a + nrm * t_sc, b + nrm * t_sc
        szary = 'wn_piaskowiec:szary'
        akcent = []
        # rozmieszczenie wzdłuż ściany (od a): pozycja s, głębokość od ściany
        def P(s, t):
            return a + k * s + nrm * t
        # 1) gzyms (fragment 1,8 m) na długim cokole
        s0 = 0.3
        G.pryzma(self.prostokat(P(s0 + 1.1, 0.55), k, 2.4, 0.7), 0.0, 0.42, 'granit:ciemny')
        prof = [(0.0, 0.0), (0.42, 0.0), (0.42, 0.08), (0.36, 0.10), (0.36, 0.16), (0.24, 0.20), (0.22, 0.30),
                (0.10, 0.34), (0.08, 0.40), (0.0, 0.40)]
        Vb = []
        for sx in (s0 + 0.2, s0 + 2.0):
            ring = []
            for t_, z_ in prof:
                p = P(sx, 0.35 + t_ - 0.21)
                ring.append((p[0], p[1], 0.42 + z_))
            Vb.append(ring)
        for i in range(len(prof)):
            j = (i + 1) % len(prof)
            G.face([Vb[0][i], Vb[1][i], Vb[1][j], Vb[0][j]], [(0, 0), (1.8, 0), (1.8, 0.1), (0, 0.1)], 'wn_piaskowiec')
        G.face(Vb[0][::-1], [(0, 0)] * len(prof), 'wn_piaskowiec')
        G.face(Vb[1], [(0, 0)] * len(prof), 'wn_piaskowiec')
        akcent.append((P(s0 + 1.1, 0.5), 0.7))
        # 2) bęben kolumny (Ø 0,7, h 0,75) z kanelurami (wielokąt gwiaździsty)
        s1 = s0 + 3.05
        G.pryzma(self.prostokat(P(s1, 0.55), k, 1.0, 1.0), 0.0, 0.30, 'granit:ciemny')
        kan = Polygon([tuple(P(s1, 0.55) + np.array([math.cos(2 * math.pi * i / 48), math.sin(2 * math.pi * i / 48)])
                             * (0.35 if i % 2 == 0 else 0.33)) for i in range(48)])
        G.pryzma(kan, 0.30, 1.05, 'wn_piaskowiec')
        akcent.append((P(s1, 0.55), 0.7))
        # 3) kapitel na wysokim cokole (abakus + echinus + woluty – tory)
        s2 = s1 + 1.35
        G.pryzma(self.prostokat(P(s2, 0.5), k, 0.7, 0.7), 0.0, 1.0, 'granit:ciemny')
        G.pryzma(Point(P(s2, 0.5)).buffer(0.24, 32), 1.0, 1.12, szary)
        G.pryzma(Point(P(s2, 0.5)).buffer(0.30, 32), 1.12, 1.22, szary)
        G.pryzma(self.prostokat(P(s2, 0.5), k, 0.78, 0.66), 1.22, 1.32, szary)
        G.pryzma(self.prostokat(P(s2, 0.5), k, 0.86, 0.86), 1.32, 1.40, szary)
        for sg in (-1, 1):
            cc = P(s2 + sg * 0.36, 0.5)
            G.pryzma(Point(cc).buffer(0.11, 24).difference(Point(cc).buffer(0.04, 12)), 1.08, 1.30, szary)
        akcent.append((P(s2, 0.5), 1.25))
        # 4) tralki balustrady (4 szt.) na belce – gdy ściana dość długa (inaczej przy przeszkleniu ogrodowym)
        s3 = s2 + 1.5
        if s3 + 0.75 > L - 1.6:
            tt = np.array([self.n_wew[1], -self.n_wew[0]])
            c3 = self.drzwi_ogr + self.n_wew * 1.1 - tt * 2.2
            k3, n3 = tt, self.n_wew
            s3 = None
        else:
            c3, k3, n3 = P(s3, 0.45), k, nrm
        G.pryzma(self.prostokat(c3, k3, 1.5, 0.5), 0.0, 0.25, 'granit:ciemny')
        G.pryzma(self.prostokat(c3, k3, 1.4, 0.32), 0.25, 0.37, 'wn_piaskowiec')
        prof_t = [(0.0, 0.07), (0.06, 0.07), (0.10, 0.05), (0.22, 0.10), (0.36, 0.12), (0.46, 0.06), (0.52, 0.045),
                  (0.58, 0.07), (0.62, 0.07)]
        for i in range(4):
            cc = c3 + k3 * (-0.51 + i * 0.34)
            for (z_a, r_a), (z_b, r_b) in zip(prof_t[:-1], prof_t[1:]):
                G.pryzma(Point(cc).buffer((r_a + r_b) / 2, 20), 0.37 + z_a, 0.37 + z_b, 'wn_piaskowiec')
        G.pryzma(self.prostokat(c3, k3, 1.4, 0.30), 0.99, 1.09, 'wn_piaskowiec')
        if s3 is not None:
            akcent.append((c3, 0.8))
        # 5) płyta z inskrypcją oparta o ścianę
        s4 = (s3 if s3 is not None else s2 - 0.15) + 1.5
        if s4 + 0.7 < L - 1.4:
            base = P(s4, 0.22)
            G.pryzma(self.prostokat(P(s4, 0.3), k, 1.3, 0.45), 0.0, 0.12, 'granit:ciemny')
            pl = [P(s4 - 0.6, 0.30), P(s4 + 0.6, 0.30), P(s4 + 0.6, 0.12), P(s4 - 0.6, 0.12)]
            zz = [(0.12, 0.12, 1.02, 1.02)]
            G.face([(pl[0][0], pl[0][1], 0.12), (pl[1][0], pl[1][1], 0.12), (pl[2][0], pl[2][1], 1.02),
                    (pl[3][0], pl[3][1], 1.02)], [(0, 0), (1.2, 0), (1.2, 0.9), (0, 0.9)], szary)
            akcent.append((base, 0.6))
        # tablica informacyjna lapidarium (pulpit)
        tb = P(-0.3 if s0 > 0.6 else 0.3, 0.9)
        G.pryzma(Point(tb).buffer(0.03, 8), 0.0, 1.0, 'metal', gora=True, dno=False)
        G.pryzma(self.prostokat(tb, k, 0.5, 0.03), 1.0, 1.35, 'wn_biurko')
        # oświetlenie akcentowe (spoty z sufitu, odsunięte od ściany 1,4 m)
        zrod = [P(float((p - a) @ k), 1.6) for p, _ in akcent]
        cele = [(p[0], p[1], h) for p, h in akcent]
        self.lampy_punktowe(zrod, self.suf - 0.3, moc=45.0, kat=36.0, nazwa='lapidarium', cel=cele, promien=0.02)
        self.info['lapidarium'] = {'eksponaty': len(akcent), 'sciana': 'SW.02 (zach.)'}

    def poczekalnia(self, G):
        """Poczekalnia przy przeszkleniu ogrodowym: dwie ławy dębowe 2,8 × 0,5 m (h 0,45) wzdłuż elewacji."""
        t = np.array([self.n_wew[1], -self.n_wew[0]])
        for sdl in (-2.2, 2.6):
            c = self.drzwi_ogr + self.n_wew * 2.6 + t * sdl
            if not self.H.buffer(-0.4).contains(self.prostokat(c, t, 2.8, 0.5)):
                continue
            G.pryzma(self.prostokat(c, t, 2.8, 0.5), 0.40, 0.45, 'wn_drewno')
            for e in (-1.1, 1.1):
                G.pryzma(self.prostokat(c + t * e, t, 0.08, 0.44), 0.0, 0.40, 'metal')
        self.info['poczekalnia'] = 'ławy przy przeszkleniu ogrodowym'

    def napis_scienny(self, G, tekst, p0, kier, nrm, z, h=0.16, mat='mosiadz', odstep=1.25, do_konca=False):
        """Litery z mosiądzu (gr. 12 mm, 8 mm od ściany) – tekst od p0 wzdłuż ``kier``, lico ściany ``nrm``."""
        from pathlib import Path
        cu = bpy.data.curves.new('napis_sc', 'FONT')
        cu.body = tekst
        f = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        if Path(f).exists():
            cu.font = bpy.data.fonts.load(f, check_existing=True)
        cu.size = h / 0.73
        cu.space_character = odstep
        cu.extrude = 0.006
        cu.resolution_u = 4
        ob = bpy.data.objects.new('napis_sc_tmp', cu)
        self.B.sc.collection.objects.link(ob)
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)
        k = np.asarray(kier, float) / np.linalg.norm(kier)
        n = np.asarray(nrm, float)
        if do_konca and len(me.vertices):
            # p0 = koniec tekstu (wyrównanie do prawej)
            p0 = np.asarray(p0, float) - k * max(v.co.x for v in me.vertices)
        V = []
        for v in me.vertices:
            q = np.asarray(p0, float) + k * v.co.x + n * (0.014 + v.co.z)
            V.append((q[0], q[1], z + v.co.y))
        for pl in me.polygons:
            G.face([V[i] for i in pl.vertices], [(0, 0)] * len(pl.vertices), mat)
        bpy.data.meshes.remove(me)

    def informacja_mosiezna(self, G):
        """System informacji: litery mosiężne na ścianie pn. bloku kancelarii (widocznej od Bramy Mostowej) i pas
        z nazwą hali nad przejściem; tablica kierunkowa przy przejściu."""
        sw02 = self.pom.get('SW.02')
        dk02 = self.pom.get('DK.02')
        blok = unary_union([g for g in (sw02, dk02) if g is not None and not g.is_empty])
        if blok.is_empty:
            return
        # krawędź bloku zwrócona ku drzwiom Bramy Mostowej (najbliższa od, długość ≥ 3 m)
        best = None
        for P in _czesci(blok.buffer(0.15, join_style=2)):
            c = list(P.exterior.coords)
            for a, b in zip(c[:-1], c[1:]):
                a, b = np.array(a), np.array(b)
                L = float(np.linalg.norm(b - a))
                if L < 3.0:
                    continue
                mid = (a + b) / 2
                k = (b - a) / L
                n = np.array([k[1], -k[0]])
                if not self.H.contains(Point(mid + n * 0.5)):
                    n = -n
                if not self.H.contains(Point(mid + n * 0.5)):
                    continue
                do_od = self.od - mid
                dd = float(np.linalg.norm(do_od))
                if dd > 14.0 or float(n @ do_od) < 0.5 * dd:
                    continue                          # ściana nie zwrócona ku wejściu
                if best is None or L > best[0]:
                    best = (L, a, b, k, n, L)
        if best is None:
            return
        _, a, b, k, n, L = best
        # tekst czytany od lewej patrząc na ścianę: kierunek k tak, by (k, n) był prawoskrętny względem patrzącego
        if k[0] * n[1] - k[1] * n[0] > 0:
            a, b, k = b, a, -k
        a, b = a - n * 0.15, b - n * 0.15             # z bufora 0,15 na lico wewnętrzne pomieszczenia
        t_sc = float(self.H.distance(Point((a + b) / 2)))
        a, b = a + n * t_sc, b + n * t_sc             # lico od strony holu (wielokąty „w świetle ścian”)
        L = float(np.linalg.norm(b - a))
        # okładzina z listew dębowych 0,05 × 0,04 co 0,10 m (ciągłość z sufitem lamelowym), tło ciemne
        z_top = self.suf - 0.26
        G.pryzma(self.prostokat((a + b) / 2 + n * 0.006, k, L - 0.02, 0.012), 0.10, z_top, 'wn_ciemne', gora=False,
                 dno=False)
        for x in np.arange(0.05, L - 0.04, 0.09):
            c = a + k * x + n * 0.032
            G.pryzma(self.prostokat(c, k, 0.06, 0.04), 0.10, z_top, 'wn_drewno:jasne', gora=False, dno=False)
        # napisy wyrównane do narożnika od strony przejścia (koniec b), 0,7 m od narożnika
        self.napis_scienny(G, 'HALA OBYWATELSKA', b - k * 0.7 + n * 0.054, k, n, 2.62, h=0.24, do_konca=True)
        self.napis_scienny(G, 'INFORMACJA · KANCELARIA · LAPIDARIUM · OGRÓD', b - k * 0.7 + n * 0.054, k, n,
                           2.26, h=0.10, odstep=1.12, do_konca=True)
        self.info['informacja_mosiezna'] = 'litery mosiężne na ścianie bloku SW.02/DK.02 (h 0,22 / 0,10 m)'

    # ------------------------------------------------------------------ rośliny i ludzie
    def _fikus(self, nazwa, H=2.6, R=0.75, n=1400, seed=0):
        rng = np.random.default_rng(seed)
        G = Geo()
        # pień i gałęzie
        G.pryzma(Point(0, 0).buffer(0.045, 10), 0.55, H * 0.55, 'wn_drewno')
        zc = H * 0.66
        for i in range(n):
            # punkt w elipsoidzie korony (gęściej przy powierzchni)
            v = rng.normal(size=3)
            v /= np.linalg.norm(v)
            r = rng.uniform(0.55, 1.0) ** 0.5
            c = np.array([v[0] * R * r, v[1] * R * r, zc + v[2] * R * 0.85 * r])
            # liść 0,11 × 0,05 m, losowa orientacja (lekko ku górze)
            a = rng.normal(size=3)
            a[2] = abs(a[2]) * 0.3
            a /= np.linalg.norm(a)
            b = np.cross(a, rng.normal(size=3))
            b /= np.linalg.norm(b)
            L, W = 0.11 * rng.uniform(0.8, 1.2), 0.05
            p = [c, c + a * L * 0.5 + b * W * 0.5, c + a * L, c + a * L * 0.5 - b * W * 0.5]
            G.face([tuple(q) for q in p], [(0, 0)] * 4, 'wn_lisc', rnd=float(rng.random()))
        # donica (beton, Ø 0,9, h 0,55) i ziemia
        G.pryzma(Point(0, 0).buffer(0.45, 32).difference(Point(0, 0).buffer(0.41, 32)), 0.0, 0.55, 'beton')
        G.pryzma(Point(0, 0).buffer(0.41, 32), 0.0, 0.50, 'wn_ciemne', boki=False, dno=False)
        return G.obiekt(nazwa, self.coll, self.B.mat, 0.0)

    def rosliny(self):
        """Fikusy w donicach: przy słupach holu frontowego i przy przeszkleniu ogrodowym (poza osią i ścieżką)."""
        pas = LineString([self.od, self.do]).buffer(self.szer_osi / 2 + 0.6)
        kand = []
        for s in self.P['slupy']:
            if self.H.buffer(0.35).contains(Point(s)):
                for kq in (self.lewo, -self.lewo, self.d, -self.d):
                    p = np.array(s) + kq * 1.0
                    if self.H.buffer(-0.7).contains(Point(p)) and not pas.contains(Point(p)):
                        kand.append(p)
                        break
        t = np.array([self.n_wew[1], -self.n_wew[0]])
        for sdl in (-4.3, 4.6):
            p = self.drzwi_ogr + self.n_wew * 1.2 + t * sdl
            if self.H.buffer(-0.6).contains(Point(p)):
                kand.append(p)
        if not kand:
            return
        proto = self._fikus('fikus_proto', seed=11)
        proto.location = (kand[0][0], kand[0][1], self.B.DZ)
        rng = np.random.default_rng(5)
        for i, p in enumerate(kand[1:]):
            ob = proto.copy()
            ob.name = 'fikus_%02d' % i
            s = rng.uniform(0.85, 1.15)
            ob.scale = (s, s, s)
            ob.rotation_euler = (0, 0, rng.uniform(0, 2 * math.pi))
            ob.location = (p[0], p[1], self.B.DZ)
            self.coll.objects.link(ob)
        self.info['rosliny'] = len(kand)

    def ludzie(self):
        """Ludzie w hali: przy ladzie (pracownik, interesant), osoba na wózku przy niskiej ladzie, piesi osią,
        zwiedzający lapidarium, rodzic z dzieckiem przy poczekalni."""
        from umwd.render import budynek3d_otoczenie as oto
        B = self.B
        mat = B.mat('ludzie')
        k, n = self.d, self.lewo
        c = self.p_info
        # (pozycja, kierunek patrzenia/ruchu, wariant prototypu (H, chód, płaszcz, kobieta, torba), ruch)
        t_ogr = np.array([self.n_wew[1], -self.n_wew[0]])
        osoby = [
            (c + k * 0.55 - n * 0.75, n, (1.72, 0.0, 0.50, True, False, 'kieszen'), False),  # pracownik informacji
            (c + k * 0.9 + n * 0.85, -n, (1.80, 0.0, 0.36, False, True, ''), False),         # interesant
            (self.a_l(17.5, 0.9), k, (1.83, 0.30, 0.50, False, False, ''), True),            # idący ku ogrodowi
            (self.a_l(10.6, 2.0), None, (1.76, 0.0, 0.42, False, False, 'kieszen'), False),  # lapidarium
            (self.a_l(11.3, 1.6), None, (1.62, 0.0, 0.36, True, True, 'telefon'), False),
            (self.drzwi_ogr + self.n_wew * 3.6 + t_ogr * 0.6, None, (1.74, 0.0, 0.40, True, False, ''), False),
            (self.drzwi_ogr + self.n_wew * 3.3 + t_ogr * 1.1, None, (1.15, 0.30, 0.50, False, False, ''), False),
        ]
        rng = np.random.default_rng(B.o['seed'] + 7)
        n_ok = 0
        for i, (p, kier, (H, chod, pl, kob, tb, poza), ruch) in enumerate(osoby):
            if not self.H.buffer(-0.3).contains(Point(p)):
                continue
            me = oto._prototyp_czlowieka('hala_czlowiek_%d' % i, H, chod, pl, kob, seed=40 + i, torba=tb, poza=poza)
            me.materials.append(mat)
            ob = bpy.data.objects.new('hala_czlowiek_%02d' % i, me)
            self.coll.objects.link(ob)
            if kier is None:
                # zwiedzający: przodem do najbliższego eksponatu / przeszklenia
                kier = (np.array(self.drzwi_ogr) - p) if i >= 5 else n
            kat = math.atan2(kier[1], kier[0]) + rng.normal(0, 0.15)
            ob.rotation_euler = (0, 0, kat - math.pi / 2)
            ob.location = (p[0], p[1], B.DZ)
            if ruch and B.o.get('ruch_ludzi', True):
                v = np.array([math.cos(kat), math.sin(kat)]) * 0.5 * B.o.get('ruch_ludzi_m', 0.07)
                for f in (0, 1, 2):
                    ob.location = (p[0] + v[0] * (f - 1), p[1] + v[1] * (f - 1), B.DZ)
                    ob.keyframe_insert('location', frame=f)
                if ob.animation_data and ob.animation_data.action:
                    for fc in oto._krzywe(ob.animation_data.action):
                        for kp in fc.keyframe_points:
                            kp.interpolation = 'LINEAR'
                B.sc.render.use_motion_blur = True
                B.sc.render.motion_blur_shutter = 1.0
                B.sc.frame_set(1)
            n_ok += 1
        # osoba na wózku przy niskiej ladzie (przodem do lady)
        p_w = c - k * 1.15 + n * 0.95
        oto.wozek(B, self.coll, lambda e, nn: np.zeros(len(e)), poz=p_w, kier=-n, nazwa='_hala')
        self.info['ludzie'] = n_ok + 1
