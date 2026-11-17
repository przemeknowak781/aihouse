# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku (S, +27,30) z antresolą (+30,90) – szczegółowe wnętrza do wizualizacji W7 (hol sali Sejmiku)
i W8 (sala obrad z galerią publiczności).

Geometria z ``model/koncepcja.json`` → ``kondygnacja_sejmiku`` (spec v1.2, S-3), w układzie (u, v) wieży:

* pomieszczenia S i antresoli (``obrys_uv``) → ściany = wnętrze kondygnacji minus pomieszczenia (wielokąty są
  „w świetle ścian”); na poziomie antresoli bryła pełna poza przestrzeniami otwartymi (hol górny, sala
  multimedialna, bar, galeria, korytarz publiczny, hol dźwigów), pustką holu, schodami i salą (2 kondygnacje);
* sala obrad SWD.01 (6,85 m w świetle): 4 rzędy łukowe wokół ogniska F (u 27,5; v 15,2) z ``rzedy[].obrys_uv``
  (podesty +0,00/0,09/0,18/0,27, pulpity, fotele wg ``linia_siedzisk_R`` i liczby miejsc, miejsca dla wózków
  na zach. końcach), prezydium (stół 6,0 m przy pełnej ścianie pd.), mównica w ognisku, ekrany, flagi, napis
  z mosiądzu, sufit z bafli dębowych, ściany pd. i zach. z dębu;
* galeria publiczności SWD.01g (zach., u 15,5–22,0, +30,90): rząd 1 (+0,00, 8 miejsc), podest rzędu 2 (+0,90,
  9 miejsc) z balustradą szklaną 0,70 m, stopnie z foyer, zatoka 3 miejsc dla wózków, balustrada szklana 1,10 m na
  cokole 0,20 m w licu u 22,00;
* hol reprezentacyjny SWD.02/SWD.02g: pustka 2-kondygnacyjna NW (okna pn. i zach. – elewacja), schody
  reprezentacyjne w pustce (21 × 17,14 cm, 11 + 10, spocznik 1,5 m, bieg 2,0 m, od u 10,92 do 4,1), balustrady
  szklane krawędzi antresoli, szatnia, posadzka z lastryka, sufit z lameli dębowych;
* ludzie: radni w fotelach (sesja), prezydium, mówca, publiczność na galerii (W8); goście w holu (W7).
"""
from __future__ import annotations

import math

import numpy as np
import bpy
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union

from umwd.render.budynek3d import Geo

CIEPLE = (1.0, 0.80, 0.58)


def _czesci(g):
    if g is None or g.is_empty:
        return []
    return [g] if isinstance(g, Polygon) else [p for p in getattr(g, 'geoms', []) if isinstance(p, Polygon)]


class Sejmik:
    def __init__(self, B):
        self.B = B
        sp = B.spec
        self.sp = sp
        self.K = sp.K['kondygnacja_sejmiku']
        kd = sp.kondygnacje('W')
        kS = next(k for k in kd if k['nazwa'] == 'S')
        self.F = kS['F']
        self.suf = kS['sufit']
        self.za = self.K['antresola']['wzgl']
        self.info = {}

    # ------------------------------------------------------------------ pomocnicze
    def uv(self, u, v):
        return self.sp.z_uv(u, v)

    def P(self, ring_uv):
        """Wielokąt z listy (u, v) lub z [[ring], [hole]...] / [[[ring]...]]."""
        r = ring_uv
        while isinstance(r[0][0], (list, tuple)):
            r = r[0]
        return Polygon([self.uv(*p) for p in r]).buffer(0)

    def pom(self, kod):
        r = self.K['pomieszczenia'].get(kod) or self.K['antresola_pomieszczenia'].get(kod)
        if r is None:
            return Polygon()
        # wielokąty złożone (kilka pierścieni zewnętrznych) – suma
        obr = r['obrys_uv']
        if isinstance(obr[0][0][0], (list, tuple)):
            return unary_union([Polygon([self.uv(*p) for p in pg[0]]).buffer(0) for pg in obr])
        return unary_union([Polygon([self.uv(*p) for p in ring]).buffer(0) for ring in obr])

    def kier_uv(self, du, dv):
        a = np.array(self.uv(du, dv)) - np.array(self.uv(0, 0))
        return a / max(np.linalg.norm(a), 1e-9)

    def lampy(self, punkty, z, moc, kat, nazwa, typ='SPOT', rozmiar=0.05, cel=None, barwa=CIEPLE):
        from mathutils import Vector
        for i, p in enumerate(punkty):
            ld = bpy.data.lights.new('%s_%02d' % (nazwa, i), typ)
            ld.energy = moc
            ld.color = barwa
            if typ == 'SPOT':
                ld.spot_size = math.radians(kat)
                ld.spot_blend = 0.6
                ld.shadow_soft_size = rozmiar
            elif typ == 'AREA':
                ld.shape = 'DISK'
                ld.size = rozmiar
            else:
                ld.shadow_soft_size = rozmiar
            ob = bpy.data.objects.new(ld.name, ld)
            ob.location = (p[0], p[1], z + self.B.DZ)
            if cel is not None:
                c = cel[i] if isinstance(cel, list) else cel
                v = Vector((c[0] - p[0], c[1] - p[1], c[2] - z))
                ob.rotation_euler = v.to_track_quat('-Z', 'Y').to_euler()
            self.coll.objects.link(ob)

    # ------------------------------------------------------------------ budowa
    def buduj(self, G, Wp, g):
        B = self.B
        sp = self.sp
        self.coll = B.kol['wnetrza']
        self.Gs = Geo()                                           # szkło balustrad (osobny obiekt)
        F, suf, za = self.F, self.suf, self.za
        wn = Wp.buffer(-g - 0.04, join_style=2)                 # wnętrze kondygnacji (za szkłem/ościeżami)
        self.wn = wn
        # strop dachu (sufit sali i holu 2-kond.)
        G.pryzma(wn, suf, sp.dach['W']['pokrycie'] - 0.03, 'wn_sufit', mat_gora='beton', dno=False)
        # ---- przestrzenie
        S_kody = [k for k in self.K['pomieszczenia']]
        S_pom = {k: self.pom(k) for k in S_kody}
        ANT_kody = list(self.K['antresola_pomieszczenia'])
        A_pom = {k: self.pom(k) for k in ANT_kody}
        self.sala = S_pom['SWD.01'].intersection(wn)
        pustka = self.P(self.K['pustka_holu']['obrys_uv']).intersection(wn)
        schody = self.P(self.K['schody_reprezentacyjne']['obrys_uv']).intersection(wn)
        self.pustka, self.schody_p = pustka, schody
        dwukond = unary_union([self.sala, pustka, schody]).buffer(0)
        ant_otw = unary_union([A_pom[k] for k in ('SWD.02g', 'SWD.03', 'SWD.05', 'SWD.01g')]).intersection(wn)
        ant_zamk = unary_union([A_pom[k] for k in ('KW.A.01', 'PHS.05c', 'KW.A.02', 'KW.A.03')]).intersection(wn)
        ant_pod = unary_union([ant_otw, ant_zamk]).difference(dwukond).buffer(0)
        self.ant_otw = ant_otw
        # ---- posadzki S: lastryko (hol, kuluar, łączniki), parkiet dębowy (sala), reszta – kamień
        hol = unary_union([S_pom[k] for k in ('SWD.02', 'KW.S.01', 'KW.S.03', 'SWD.06', 'KUL', 'KW.S.04')]).intersection(wn)
        G.pryzma(hol.buffer(0.08, join_style=2).intersection(wn), F, F + 0.006, 'wn_terrazzo', boki=False, dno=False)
        G.pryzma(self.sala.buffer(0.05, join_style=2).intersection(wn), F, F + 0.006, 'wn_drewno', boki=False, dno=False)
        # ---- ściany S (wnętrze minus pomieszczenia); pod antresolą otwartą tylko do spodu stropu antresoli
        S_wszystkie = unary_union(list(S_pom.values()) + [pustka, schody]).buffer(0)
        sciany = wn.difference(S_wszystkie.buffer(0.005)).buffer(-0.01).buffer(0.01)
        trzony = unary_union([S_pom['C-A'], S_pom['C-B']])
        for P_ in _czesci(sciany.difference(trzony)):
            if P_.area < 0.02:
                continue
            pod = P_.intersection(ant_otw)
            reszta = P_.difference(ant_otw)
            for q in _czesci(pod):
                G.pryzma(q, F, za - 0.30, 'wn_tynk', gora=False, dno=False)
            for q in _czesci(reszta):
                G.pryzma(q, F, suf, 'wn_tynk', gora=False, dno=False)
        # trzony pełne (okładzina dębowa)
        for q in _czesci(trzony.intersection(wn)):
            G.pryzma(q, F, suf, 'wn_drewno:jasne', gora=False, dno=False)
        # pomieszczenia zamknięte S (poza salą, holem) – sufit 3,3 m (widok przez drzwi)
        # ---- antresola: strop (spód tynk, wierzch lastryko), bryła pełna nad salami komisji itp., ściany zamkniętych
        G.pryzma(ant_pod, za - 0.30, za, 'wn_terrazzo', mat_dol='wn_sufit')
        masa = wn.difference(unary_union([ant_pod, dwukond]).buffer(0.01)).buffer(-0.02).buffer(0.02)
        for q in _czesci(masa):
            if q.area > 0.05:
                G.pryzma(q, za - 0.30, suf, 'wn_tynk', gora=False)
        for k in ('KW.A.01', 'PHS.05c', 'KW.A.02', 'KW.A.03'):
            pk = A_pom[k]
            ring = pk.buffer(0.14, join_style=2).difference(pk).difference(ant_zamk.difference(pk))
            ring = ring.intersection(wn).difference(self.sala.buffer(-0.01))
            for q in _czesci(ring):
                G.pryzma(q, za, suf, 'wn_tynk', gora=False, dno=False)
        self.sciany_sali(G)
        self.sufity(G)
        self.schody(G)
        self.balustrady_antresoli(G)
        self.rzedy(G)
        self.prezydium(G)
        self.galeria(G)
        self.hol_wyposazenie(G)
        self.swiatla()
        if B.o.get('ludzie', True):
            self.ludzie()
        self.Gs.obiekt('sejmik_szklo_balustrad', self.coll, B.mat, B.DZ)
        B.info['sejmik'] = self.info

    def sciany_sali(self, G):
        """Ściany sali: pd. (pełna, prezydium) i zach. – okładzina dębowa z listew; nad galerią otwarcie z balustradą."""
        F, suf, za = self.F, self.suf, self.za
        sala = self.sala
        uv = self.uv
        # okładzina 0,05 m od strony sali na ścianach pd. (v 12,6) i zach. (u 22,0)
        for (a, b, n) in (((22.0, 12.6), (34.0, 12.6), (0, 1)), ((22.0, 12.6), (22.0, 29.2), (1, 0))):
            L = LineString([uv(*a), uv(*b)])
            pas = L.buffer(0.06, cap_style=2).intersection(sala.buffer(0.07))
            if pas.is_empty:
                continue
            if a[0] == b[0]:
                # ściana zach.: do +30,90 (pod galerią – WC), wyżej otwarcie galerii (v 12,6–22,65), dalej pełna
                for q in _czesci(pas):
                    G.pryzma(q, F, za + 0.20, 'wn_drewno')
                gor = LineString([uv(22.0, 22.65), uv(22.0, 29.2)]).buffer(0.06, cap_style=2).intersection(sala.buffer(0.07))
                for q in _czesci(gor):
                    G.pryzma(q, za + 0.20, suf, 'wn_drewno')
            else:
                # listwy pionowe dębowe co 0,09 m na ścianie pd.
                k = np.array(uv(*b)) - np.array(uv(*a))
                Lk = float(np.linalg.norm(k))
                k /= Lk
                nn = self.kier_uv(0, 1)
                G.pryzma(Polygon([np.array(uv(*a)) + nn * 0.005, np.array(uv(*b)) + nn * 0.005,
                                  np.array(uv(*b)) + nn * 0.015, np.array(uv(*a)) + nn * 0.015]), F, suf, 'wn_ciemne',
                         gora=False, dno=False)
                for x in np.arange(0.05, Lk - 0.04, 0.09):
                    c = np.array(uv(*a)) + k * x + nn * 0.035
                    q = Polygon([c - k * 0.03 - nn * 0.02, c + k * 0.03 - nn * 0.02, c + k * 0.03 + nn * 0.02,
                                 c - k * 0.03 + nn * 0.02])
                    G.pryzma(q, F + 0.10, suf - 0.02, 'wn_drewno:jasne', gora=False, dno=False)

    def sufity(self, G):
        """Sala: bafle dębowe (pasy co 0,30 m wzdłuż v) + oprawy pierścieniowe; hol 2-kond. i antresola: lamele
        dębowe co 0,15 m (jak w Hali Obywatelskiej); pod antresolą – tynk z downlightami."""
        suf, za = self.suf, self.za
        uv = self.uv
        for u in np.arange(22.2, 39.6, 0.30):
            pas = Polygon([uv(u, 12.6), uv(u + 0.06, 12.6), uv(u + 0.06, 29.5), uv(u, 29.5)]).intersection(self.sala)
            for q in _czesci(pas):
                G.pryzma(q, suf - 0.45, suf, 'wn_drewno:jasne', gora=False)
        # lamele holu górnego (pustka + antresola otwarta)
        strefa = unary_union([self.pustka, self.schody_p, self.ant_otw.difference(self.sala)]).buffer(0)
        for v in np.arange(12.0, 29.6, 0.15):
            pas = Polygon([uv(0, v), uv(22.0, v), uv(22.0, v + 0.05), uv(0, v + 0.05)]).intersection(strefa)
            for q in _czesci(pas):
                if q.area > 0.003:
                    G.pryzma(q, suf - 0.24, suf - 0.12, 'wn_drewno:jasne', gora=False)
        G.pryzma(strefa, suf - 0.03, suf - 0.01, 'wn_ciemne', gora=False, boki=False)
        self.strefa_holu = strefa

    def schody(self, G):
        """Schody reprezentacyjne: od u 10,92 (+0,00) do u 4,1 (+3,60), bieg 2,0 m (v 24,6–26,6); stopnie dębowe na
        płycie z betonu architektonicznego (bieg „zawieszony” w pustce), balustrady szklane z pochwytem mosiężnym."""
        F, za = self.F, self.za
        uv = self.uv
        h = (za - F) / 21.0
        v0, v1 = 24.6, 26.6
        u = 10.92
        z = F
        stopnie = []
        for i in range(11):
            stopnie.append((u, u - 0.28 if i < 10 else u - 0.0, z + h * (i + 1)))
            if i < 10:
                u -= 0.28
        # spocznik
        u_sp0 = 10.92 - 10 * 0.28
        u_sp1 = u_sp0 - 1.5
        z_sp = F + 11 * h
        u2 = u_sp1
        for i in range(10):
            stopnie.append((u2, u2 - 0.28, z_sp + h * (i + 1)))
            u2 -= 0.28
        for (ua, ub, zt) in stopnie[:10] + stopnie[11:]:
            q = Polygon([uv(ua, v0), uv(ub, v0), uv(ub, v1), uv(ua, v1)])
            G.pryzma(q, zt - 0.05, zt, 'wn_drewno:jasne')
            G.pryzma(q.buffer(-0.0001), zt - h, zt - 0.05, 'beton', gora=False, dno=False)
        G.pryzma(Polygon([uv(u_sp0, v0), uv(u_sp1, v0), uv(u_sp1, v1), uv(u_sp0, v1)]), z_sp - 0.25, z_sp, 'beton',
                 mat_gora='wn_drewno:jasne')
        # policzki (płyta biegu) – ukośne płyty betonowe pod stopniami
        for (ua, ub, za0, za1) in ((10.92, u_sp0, F, z_sp), (u_sp1, 4.1, z_sp, za)):
            for vv in (v0, v1 - 0.08):
                pts = [(*uv(ua, vv), za0 - 0.25), (*uv(ub, vv), za1 - 0.25), (*uv(ub, vv), za1 + 0.02),
                       (*uv(ua, vv), za0 + 0.02)]
                G.face(pts, [(0, 0)] * 4, 'beton')
                pts2 = [(*uv(ua, vv + 0.08), za0 - 0.25), (*uv(ua, vv + 0.08), za0 + 0.02), (*uv(ub, vv + 0.08), za1 + 0.02),
                        (*uv(ub, vv + 0.08), za1 - 0.25)]
                G.face(pts2, [(0, 0)] * 4, 'beton')
            # spód biegu
            G.face([(*uv(ua, v0), za0 - 0.25), (*uv(ua, v1), za0 - 0.25), (*uv(ub, v1), za1 - 0.25),
                    (*uv(ub, v0), za1 - 0.25)], [(0, 0)] * 4, 'beton')
        # balustrady szklane 1,10 z pochwytem
        for vv in (v0 + 0.03, v1 - 0.03):
            for (ua, ub, za0, za1) in ((10.92, u_sp0, F, z_sp), (u_sp0, u_sp1, z_sp, z_sp), (u_sp1, 4.1, z_sp, za)):
                pts = [(*uv(ua, vv), za0 + 0.05), (*uv(ub, vv), za1 + 0.05), (*uv(ub, vv), za1 + 1.10),
                       (*uv(ua, vv), za0 + 1.10)]
                self.Gs.face(pts, [(0, 0)] * 4, 'szklo:balustrada')
                a3 = np.array([*uv(ua, vv), za0 + 1.10])
                b3 = np.array([*uv(ub, vv), za1 + 1.10])
                from umwd.render.budynek3d_otoczenie import _rura
                _rura(G, a3, b3, 0.022, 'mosiadz', n=8)
        self.info['schody'] = dict(stopnie=21, h=round(h, 4), spocznik_m=1.5)

    def balustrady_antresoli(self, G):
        """Balustrady szklane 1,10 m (cokół 0,10 m, pochwyt mosiężny) na krawędziach antresoli nad pustką holu."""
        from umwd.render.budynek3d_otoczenie import _rura
        za = self.za
        kraw = self.ant_otw.difference(self.sala.buffer(0.05)).boundary.intersection(
            unary_union([self.pustka, self.schody_p]).buffer(0.08))
        segs = []
        for ln in (getattr(kraw, 'geoms', [kraw])):
            if ln.geom_type != 'LineString':
                continue
            c = list(ln.coords)
            segs += list(zip(c[:-1], c[1:]))
        L = 0.0
        for a, b in segs:
            if math.dist(a, b) < 0.05:
                continue
            q = LineString([a, b]).buffer(0.05, cap_style=2)
            G.pryzma(q, za, za + 0.10, 'wn_drewno')
            self.Gs.face([(a[0], a[1], za + 0.10), (b[0], b[1], za + 0.10), (b[0], b[1], za + 1.06), (a[0], a[1], za + 1.06)],
                         [(0, 0)] * 4, 'szklo:balustrada')
            _rura(G, (a[0], a[1], za + 1.10), (b[0], b[1], za + 1.10), 0.025, 'mosiadz', n=8)
            L += math.dist(a, b)
        self.info['balustrady_antresoli_m'] = round(L, 1)

    def rzedy(self, G):
        """4 rzędy łukowe wokół F: podesty (obrys z JSON), pulpity (pas 0,55 m przy łuku R), fotele co 1,0 m na
        linii siedzisk; zach. koniec rzędu – miejsce dla wózka (bez fotela)."""
        F = self.F
        S = self.K['sala']
        fu, fv = S['ognisko_rzedow_uv']
        self.Fp = np.array(self.uv(fu, fv))
        self.fotele = []
        for r in S['rzedy']:
            R, h = r['R'], r['rzedna']
            pod = self.P(r['obrys_uv']).intersection(self.sala)
            if h > 0:
                G.pryzma(pod, F, F + h, 'wn_drewno', mat_gora='wn_tkanina')
            else:
                G.pryzma(pod, F, F + 0.008, 'wn_tkanina', boki=False, dno=False)
            a0, a1 = [math.radians(x) for x in r['sektor_deg']]
            # pulpit (blat 0,75 m + panel czołowy)
            luk = Point(*self.Fp).buffer(R + 0.55, 128).difference(Point(*self.Fp).buffer(R, 128))
            pulpit = luk.intersection(pod.buffer(0.05)).intersection(self._sektor(R + 2, a0, a1))
            for q in _czesci(pulpit):
                G.pryzma(q, F + h + 0.72, F + h + 0.76, 'wn_drewno:jasne')
                G.pryzma(q.difference(Point(*self.Fp).buffer(R + 0.06, 128)), F + h, F + h + 0.72, 'wn_drewno',
                         gora=False, dno=False)
            # fotele
            Rs = r['linia_siedzisk_R']
            n = r['miejsc']
            dl = (a1 - a0) * Rs
            krok = min(1.0, dl / n)
            for i in range(n):
                a = a0 + (i + 0.5) * krok / Rs
                p = self._uv_kat(Rs, a)
                kier_do_F = (self.Fp - p) / np.linalg.norm(self.Fp - p)
                wozek = (i == n - 1) and r.get('w_tym_dla_wozka')
                self.fotele.append((p, kier_do_F, F + h, wozek, R))
                if not wozek:
                    self._fotel(G, p, kier_do_F, F + h)
        self.info['stanowiska'] = len(self.fotele)

    def _uv_kat(self, R, a):
        """Punkt na łuku R wokół F pod kątem a mierzonym w układzie (u, v) od osi +u."""
        fu, fv = self.K['sala']['ognisko_rzedow_uv']
        return np.array(self.uv(fu + R * math.cos(a), fv + R * math.sin(a)))

    def _sektor(self, R, a0, a1):
        fu, fv = self.K['sala']['ognisko_rzedow_uv']
        pts = [self.uv(fu, fv)] + [self.uv(fu + R * math.cos(a), fv + R * math.sin(a))
                                   for a in np.linspace(a0, a1, 48)]
        return Polygon(pts)

    def _fotel(self, G, p, kier, z, kolor='wn_tkanina'):
        """Fotel obrotowy: siedzisko 0,50 × 0,48 na 0,46, oparcie, kolumna i podstawa."""
        k = np.asarray(kier, float)
        n = np.array([-k[1], k[0]])
        c = np.asarray(p, float)

        def prost(cc, dl, sz):
            return Polygon([cc - k * dl / 2 - n * sz / 2, cc + k * dl / 2 - n * sz / 2, cc + k * dl / 2 + n * sz / 2,
                            cc - k * dl / 2 + n * sz / 2])
        G.pryzma(prost(c, 0.48, 0.50), z + 0.40, z + 0.47, kolor)
        G.pryzma(prost(c - k * 0.26, 0.07, 0.48), z + 0.47, z + 1.05, kolor)
        G.pryzma(Point(*c).buffer(0.025, 8), z + 0.05, z + 0.40, 'metal', gora=False, dno=False)
        G.pryzma(Point(*c).buffer(0.30, 5).difference(Point(*c).buffer(0.26, 5)), z, z + 0.05, 'metal')

    def prezydium(self, G):
        """Prezydium: stół 6,0 × 0,85 m przy ścianie pd. (4 fotele), mównica w ognisku F (blat regulowany), ekrany
        po bokach, flagi PL i UE, napis z mosiądzu na ścianie z listew dębowych."""
        F = self.F
        uv = self.uv
        fu, fv = self.K['sala']['ognisko_rzedow_uv']
        ku, kv = self.kier_uv(1, 0), self.kier_uv(0, 1)
        c = np.array(uv(fu + 1.0, 14.0))
        st = Polygon([c - ku * 3.0 - kv * 0.42, c + ku * 3.0 - kv * 0.42, c + ku * 3.0 + kv * 0.42, c - ku * 3.0 + kv * 0.42])
        G.pryzma(st, F + 0.72, F + 0.76, 'wn_drewno:jasne')
        G.pryzma(st.buffer(-0.04).difference(st.buffer(-0.04).buffer(-0.03)), F, F + 0.72, 'wn_drewno', gora=False)
        self.prez = []
        for x in (-2.1, -0.7, 0.7, 2.1):
            p = c + ku * x - kv * 0.75
            self._fotel(G, p, kv, F, kolor='wn_ciemne')
            self.prez.append(p)
        # mównica
        m = self.Fp
        G.pryzma(Point(*m).buffer(0.32, 6), F, F + 1.05, 'wn_drewno:jasne', mat_gora='granit:ciemny')
        G.pryzma(Point(*(m + kv * 0.05)).buffer(0.012, 6), F + 1.05, F + 1.40, 'metal')          # mikrofon
        self.mownica = m
        # ekrany (2,4 × 1,35 m) na ścianie pd.
        for x in (-5.3, 4.3):
            e = c + ku * x - kv * 1.33
            q = Polygon([e - ku * 0.95, e + ku * 0.95, e + ku * 0.95 + kv * 0.05, e - ku * 0.95 + kv * 0.05])
            if self.sala.buffer(0.3).contains(Point(*e)):
                G.pryzma(q, F + 2.3, F + 3.4, 'wn_ciemne')
                pk = [np.array(p_) for p_ in list(q.exterior.coords)[:4]]
                ee = [x + kv * 0.056 for x in (e - ku * 0.92, e + ku * 0.92)]
                G.face([(ee[0][0], ee[0][1], F + 2.33), (ee[1][0], ee[1][1], F + 2.33), (ee[1][0], ee[1][1], F + 3.37),
                        (ee[0][0], ee[0][1], F + 3.37)], [(0, 0), (1, 0), (1, 1), (0, 1)], 'ekran')
        # flagi PL i UE na masztach przy prezydium
        for x, typ in ((-3.3, 'pl'), (3.3, 'ue')):
            pm = c + ku * x - kv * 0.9
            G.pryzma(Point(*pm).buffer(0.02, 8), F, F + 2.6, 'mosiadz')
            G.pryzma(Point(*pm).buffer(0.15, 16), F, F + 0.04, 'mosiadz')
            for j, (z0, z1, mat) in enumerate(((F + 1.55, F + 2.0, 'flaga_pl_czerwien' if typ == 'pl' else 'flaga_ue'),
                                               (F + 2.0, F + 2.45, 'flaga_pl_biel' if typ == 'pl' else 'flaga_ue'))):
                pts = []
                for t in np.linspace(0, 1, 9):
                    off = kv * 0.06 * math.sin(t * 5.0) + ku * (0.03 + 0.85 * t) * (1 if x < 0 else -1) * 0 + kv * 0.0
                    pts.append(pm + ku * (0.03 + 0.80 * t * (-1 if x > 0 else 1)) + off)
                for a, b in zip(pts[:-1], pts[1:]):
                    G.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], [(0, 0)] * 4, mat)
        # napis z mosiądzu nad prezydium
        try:
            from umwd.render.budynek3d_hala import Hala
            Hala.napis_scienny(self, G, 'SEJMIK WOJEWÓDZTWA DOLNOŚLĄSKIEGO', np.array(uv(fu + 1.0, 12.6)) + kv * 0.06 - ku * 4.6,
                               ku, kv, F + 4.2, h=0.26)
        except Exception as ex:
            self.info['napis_blad'] = str(ex)

    def galeria(self, G):
        """Galeria publiczności (zach., +30,90): rząd 1 (8 miejsc, +0,00), podest rzędu 2 (+0,90, 9 miejsc) ze
        stopniami, zatoka 3 miejsc dla wózków, balustrada szklana 1,10 m na cokole 0,20 m w licu u 22,00."""
        from umwd.render.budynek3d_otoczenie import _rura
        za = self.za
        Gl = self.K['sala']['galeria_publicznosci']
        uv = self.uv
        ku, kv = self.kier_uv(1, 0), self.kier_uv(0, 1)
        G.pryzma(self.P(Gl['obrys_uv']), za - 0.30, za + 0.005, 'wn_drewno', mat_dol='wn_sufit')
        G.pryzma(self.P(Gl['podest_uv']), za, za + 0.90, 'wn_drewno', mat_gora='wn_tkanina')
        st = Gl['stopnie_uv']
        u0, u1 = 17.3, 19.1
        for i in range(6):
            ua = u0 + (u1 - u0) * i / 6
            q = Polygon([uv(ua, 13.6), uv(u1, 13.6), uv(u1, 14.6), uv(ua, 14.6)])
            G.pryzma(q, za, za + 0.15 * (i + 1), 'wn_drewno')
        # balustrada czołowa u 22,00: cokół 0,20 + szkło 1,10 + pochwyt
        a, b = uv(22.0, 12.6), uv(22.0, 22.65)
        G.pryzma(LineString([a, b]).buffer(0.10, cap_style=2), za, za + 0.20, 'wn_drewno')
        self.Gs.face([(a[0], a[1], za + 0.20), (b[0], b[1], za + 0.20), (b[0], b[1], za + 1.10), (a[0], a[1], za + 1.10)],
                     [(0, 0)] * 4, 'szklo:balustrada')
        _rura(G, (a[0], a[1], za + 1.12), (b[0], b[1], za + 1.12), 0.025, 'mosiadz', n=8)
        # balustrada przednia podestu (szkło 0,70) i boczne 1,10
        for (pa, pb, hh) in (((20.9, 13.5), (20.9, 18.3), 0.70), ((20.9, 18.3), (19.1, 18.3), 1.10)):
            a, b = uv(*pa), uv(*pb)
            self.Gs.face([(a[0], a[1], za + 0.90), (b[0], b[1], za + 0.90), (b[0], b[1], za + 0.90 + hh),
                          (a[0], a[1], za + 0.90 + hh)], [(0, 0)] * 4, 'szklo:balustrada')
            _rura(G, (a[0], a[1], za + 0.92 + hh), (b[0], b[1], za + 0.92 + hh), 0.02, 'mosiadz', n=8)
        # fotele: rząd 1 (u_oka 21,2 → fotel u 21,35) 8 miejsc v 13,5–17,9; rząd 2 na podeście (u 20,4 → 20,55), 9 × 0,52
        self.widzowie = []
        for i in range(8):
            v = 13.9 + i * 0.55
            p = np.array(uv(21.35, v))
            self._fotel(G, p, ku, za, kolor='wn_tkanina')
            self.widzowie.append((p, ku, za))
        for i in range(9):
            v = 13.85 + i * 0.52
            p = np.array(uv(20.25, v))
            self._fotel(G, p, ku, za + 0.90, kolor='wn_tkanina')
            self.widzowie.append((p, ku, za + 0.90))
        self.wozki_galeria = [np.array(uv(21.2, (pg[0][1] + pg[1][1]) / 2)) for pg in Gl['miejsca_wozki_uv']]
        self.info['galeria'] = dict(fotele=17, wozki=3)

    def hol_wyposazenie(self, G):
        """Hol: lada szatni (4,1 m), ławy dębowe przy oknach pustki, rośliny, bar na antresoli."""
        F, za = self.F, self.za
        uv = self.uv
        ku, kv = self.kier_uv(1, 0), self.kier_uv(0, 1)
        # lada szatni SWD.06 (u 1,85–4,9, v 23,3–27,4) – wzdłuż krawędzi wsch.
        a = np.array(uv(4.75, 23.6))
        q = Polygon([a, a + kv * 3.5, a + kv * 3.5 - ku * 0.55, a - ku * 0.55])
        G.pryzma(q, F, F + 1.02, 'wn_drewno:jasne', mat_gora='granit:ciemny')
        # ławy przy oknach pn. pustki
        for u in (2.0, 7.0):
            c = np.array(uv(u + 1.2, 28.5))
            G.pryzma(Polygon([c - ku * 1.2 - kv * 0.25, c + ku * 1.2 - kv * 0.25, c + ku * 1.2 + kv * 0.25,
                              c - ku * 1.2 + kv * 0.25]), F + 0.40, F + 0.45, 'wn_drewno')
            for e in (-1.0, 1.0):
                G.pryzma(Polygon([c + ku * (e - 0.04) - kv * 0.22, c + ku * (e + 0.04) - kv * 0.22,
                                  c + ku * (e + 0.04) + kv * 0.22, c + ku * (e - 0.04) + kv * 0.22]), F, F + 0.40, 'metal')
        # bar SWD.05 (antresola): lada 3,5 m
        b0 = np.array(uv(16.0, 23.4))
        q = Polygon([b0, b0 + ku * 3.5, b0 + ku * 3.5 + kv * 0.6, b0 + kv * 0.6])
        G.pryzma(q, za, za + 1.05, 'wn_drewno:jasne', mat_gora='granit:ciemny')

    def swiatla(self):
        """Sala: pierścienie wiszące (emisja) + lampy powierzchniowe nad rzędami (rzeczywiste światło ~500 lx);
        prezydium doświetlone z przodu (spoty z sufitu przed rzędem 1); hol: downlighty pod antresolą,
        oprawy liniowe w lamelach pustki, akcenty na schodach."""
        F, suf, za = self.F, self.suf, self.za
        G = Geo()
        uv = self.uv
        # pierścienie (Ø 1,6 m) nad rzędami
        pkt = []
        for R in (5.5, 8.5):
            for a in np.radians(np.linspace(30, 110, 4 if R < 7 else 5)):
                pkt.append(self._uv_kat(R, a))
        for p in pkt:
            ring = Point(*p).buffer(0.80, 48).difference(Point(*p).buffer(0.72, 48))
            G.pryzma(ring, suf - 2.45, suf - 2.40, 'wn_lampa:cieple')
            for k in range(3):
                a = 2 * math.pi * k / 3
                q = p + np.array([math.cos(a), math.sin(a)]) * 0.76
                G.pryzma(Point(*q).buffer(0.004, 4), suf - 2.40, suf - 0.45, 'metal', gora=False, dno=False)
        G.obiekt('sejmik_oprawy', self.coll, self.B.mat, self.B.DZ)
        self.lampy(pkt, suf - 2.50, self.B.o.get('sejmik_moc_pierscien', 260.0), 0, 'sala_pierscien', typ='AREA',
                   rozmiar=1.5)
        # prezydium – światło frontowe (spoty z sufitu nad rzędem 1, skierowane na stół)
        fu, fv = self.K['sala']['ognisko_rzedow_uv']
        cel = (*uv(fu + 1.0, 13.8), F + 1.2)
        zr = [self._uv_kat(4.0, math.radians(a)) for a in (45, 70, 95)]
        self.lampy(zr, suf - 0.5, 120.0, 40, 'prezydium_front', cel=cel)
        # hol: downlighty pod antresolą (spód stropu za − 0,30) i w lamelach pustki
        pod = self.ant_otw.difference(self.sala.buffer(0.2)).buffer(-0.6)
        dl = []
        x0, y0, x1, y1 = self.wn.bounds
        for u in np.arange(0.8, 22.0, 2.4):
            for v in np.arange(12.6, 29.5, 2.4):
                p = np.array(uv(u, v))
                if pod.contains(Point(*p)) and not self.strefa_holu.contains(Point(*p)):
                    dl.append(p)
        self.lampy(dl, za - 0.33, 55.0, 110, 'hol_dl')
        dl2 = [np.array(uv(u, v)) for u in np.arange(1.2, 12.4, 2.2) for v in np.arange(23.8, 29.2, 2.0)
               if self.pustka.buffer(-0.4).contains(Point(*uv(u, v)))]
        self.lampy(dl2, suf - 0.30, 170.0, 90, 'pustka_dl')
        # antresola – downlighty w lamelach
        dl3 = [np.array(uv(u, v)) for u in np.arange(2.0, 21.5, 2.6) for v in np.arange(13.0, 29.0, 2.6)
               if self.ant_otw.difference(self.sala).buffer(-0.5).contains(Point(*uv(u, v)))
               and not self.pustka.contains(Point(*uv(u, v)))]
        self.lampy(dl3, suf - 0.30, 65.0, 100, 'antresola_dl')
        self.info['lampy'] = dict(pierscienie=len(pkt), hol=len(dl) + len(dl2) + len(dl3))

    def ludzie(self):
        """Sesja: radni w fotelach (ok. 85 % miejsc), prezydium (4), mówca przy mównicy, publiczność na galerii
        (ok. 13), osoba na wózku na galerii; hol: kilka osób (W7)."""
        from umwd.render import budynek3d_otoczenie as oto
        B = self.B
        mat = B.mat('ludzie')
        rng = np.random.default_rng(B.o['seed'] + 31)
        protos = []
        for i in range(6):
            me = oto._prototyp_siedzacego('siedzacy_%d' % i, kobieta=(i % 2 == 1), seed=70 + i)
            me.materials.append(mat)
            protos.append(me)
        widz = []
        for i in range(3):
            me = oto._prototyp_siedzacego('widz_%d' % i, kobieta=(i == 1), seed=90 + i,
                                          dlonie=((-0.16, 0.22, 0.62), (0.16, 0.22, 0.62)))
            me.materials.append(mat)
            widz.append(me)
        n = 0

        def postaw(me, p, kier, z, nazwa):
            ob = bpy.data.objects.new(nazwa, me)
            self.coll.objects.link(ob)
            ob.location = (float(p[0]), float(p[1]), float(z) + B.DZ)
            ob.rotation_euler = (0, 0, math.atan2(kier[1], kier[0]) - math.pi / 2)
            return ob
        for i, (p, kier, z, wozek, R) in enumerate(self.fotele):
            if wozek or rng.random() > 0.86:
                continue
            postaw(protos[rng.integers(len(protos))], p - kier * 0.05, kier, z, 'radny_%02d' % i)
            n += 1
        ku, kv = self.kier_uv(1, 0), self.kier_uv(0, 1)
        for i, p in enumerate(self.prez):
            postaw(protos[i % len(protos)], p, kv, self.F, 'prezydium_%d' % i)
        # mówca (stojący) przy mównicy – przodem do sali
        me = oto._prototyp_czlowieka('mowca', 1.76, 0.0, 0.5, False, seed=81, poza='')
        me.materials.append(mat)
        do_sali = -(self.mownica - np.array(self.uv(28.5, 14.0)))
        do_sali = do_sali / np.linalg.norm(do_sali)
        postaw(me, self.mownica - do_sali * 0.45, do_sali, self.F, 'mowca')
        nw = 0
        for i, (p, kier, z) in enumerate(self.widzowie):
            if rng.random() > 0.72:
                continue
            postaw(widz[rng.integers(len(widz))], p - kier * 0.05, kier, z, 'widz_%02d' % i)
            nw += 1
        oto.wozek(B, self.coll, lambda e, nn: np.full(len(e), self.za), poz=self.wozki_galeria[1], kier=ku, nazwa='_galeria')
        # hol (W7): goście stojący i idący, osoba na schodach
        stoj = []
        for i, (H, chod, pl, kob, tb, pz) in enumerate(((1.78, 0.0, 0.42, False, False, 'kieszen'),
                                                        (1.66, 0.0, 0.36, True, True, 'telefon'),
                                                        (1.82, 0.30, 0.50, False, False, ''),
                                                        (1.70, 0.28, 0.40, True, False, ''))):
            me = oto._prototyp_czlowieka('hol_s_%d' % i, H, chod, pl, kob, seed=110 + i, torba=tb, poza=pz)
            me.materials.append(mat)
            stoj.append(me)
        z_sp = self.F + 11 * (self.za - self.F) / 21
        miejsca = [((3.0, 28.3), (0.3, 1), self.F), ((3.7, 27.9), (-0.8, 0.6), self.F), ((9.6, 28.3), (-1, 0.2), self.F),
                   ((14.5, 21.8), (-1, 0.1), self.F), ((18.6, 21.7), (1, 0), self.F),
                   ((7.37, 25.6), (-1, 0), z_sp), ((13.0, 26.0), (0, -1), self.za), ((13.8, 26.5), (-1, -0.4), self.za),
                   ((17.6, 24.6), (0, -1), self.za)]
        hol_S = unary_union([self.pom(k) for k in ('SWD.02', 'KW.S.01', 'KW.S.03')] + [self.pustka]).buffer(-0.3)
        ant_ok = self.ant_otw.difference(self.sala).buffer(-0.3)
        nh = 0
        for i, ((u, v), (du, dv), z) in enumerate(miejsca):
            p = np.array(self.uv(u, v))
            strefa = self.schody_p.buffer(0.1) if abs(z - z_sp) < 0.01 else (hol_S if z < self.za - 0.5 else ant_ok)
            if not strefa.contains(Point(*p)):
                continue
            k = self.kier_uv(du, dv)
            postaw(stoj[i % len(stoj)], p, k, z, 'hol_gosc_%d' % i)
            nh += 1
        self.info['ludzie'] = dict(radni=n, prezydium=len(self.prez), widzowie=nw, hol=nh)
