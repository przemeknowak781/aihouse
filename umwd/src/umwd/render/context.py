# -*- coding: utf-8 -*-
"""Kontekst urbanistyczny 3D dla wizualizacji konkursowych budynku UMWD (Wrocław, róg ul. Mazowieckiej
i Wybrzeża J. Słowackiego, przy Moście Grunwaldzkim) – Blender (bpy 5.2) / Cycles.

Moduł buduje OTOCZENIE projektowanego budynku (sam budynek dokłada inny moduł):

* ``K_teren``      – teren z NMT (pikiety M.02 → TIN), podział nawierzchni wg e-mapy (jezdnie: asfalt / kostka
                     granitowa, chodniki: płyty betonowe / kostka, trawniki, schody), krawężniki granitowe;
* ``K_woda``       – Odra/Oława (płaszczyzna wody z falami i odbiciami), mury nabrzeża z parapetem i balustradą,
                     skarpa nad Oławą;
* ``K_sasiedzi``   – Mazowiecka 19 i Wybrzeże J. Słowackiego 5 w LOD3 (osie okien, kondygnacje, gzymsy,
                     boniowanie, naczółki, attyka, okna wcięte z ramami i szybą), wg inwentaryzacji M.07/M.08 i zdjęć;
* ``K_budynki``    – pozostałe budynki z ramki mapy w LOD2+ (bryła, siatka okien wciętych, gzyms, dach);
* ``K_most``       – Most Grunwaldzki: pylony z łukiem portalu, kamienna okładzina, odtworzone hełmy (M.11.F),
                     pomost z kratownicami, łańcuchy nośne, wieszaki, odciągi z blokami kotwiącymi;
* ``K_zielen``     – drzewa z site.json (instancje prototypów z ``drzewa.py``), szpaler wzdłuż bulwaru, krzewy;
* ``K_ulica``      – latarnie, słupki, ogrodzenia, szyny tramwajowe z siecią trakcyjną, oznakowanie poziome;
* ``K_dalsze``     – dalsze otoczenie: ortofotomapa M.11.A (georeferencja automatyczna do linii działek),
                     woda poza ramką z brzegami, proste bryły ważniejszych budynków, drzewa wg maski zieleni.

Układ współrzędnych: X = e (wschód), Y = n (północ) – układ lokalny ``site.json`` (e = Y2000 − 6 433 500,
n = X2000 − 5 664 100); Z = H − 119,25 m (H w PL-EVRF2007-NH).

Użycie (venv z bpy; ``-I`` ignoruje PYTHONPATH, więc moduł sam dopisuje ``src`` do ``sys.path``)::

    /home/user/aihouse/.venv-render/bin/python -I /home/user/aihouse/umwd/src/umwd/render/context.py --podglad

albo w skrypcie::

    import sys; sys.path.insert(0, '/home/user/aihouse/umwd/src')
    from umwd.render import blib, context
    sc = blib.reset()
    info = context.build_context(sc, {'pora_roku': 'jesien'})

Dokumentacja (źródła wymiarów, założenia, braki): ``docs/60_wizualizacje/kontekst_3d.md``.
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
import zlib  # noqa: E402

import shapely  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box as sbox  # noqa: E402
from shapely.ops import unary_union, polygonize_full  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402
from scipy.interpolate import LinearNDInterpolator  # noqa: E402
from scipy.spatial import cKDTree  # noqa: E402

from umwd.render import blib, drzewa  # noqa: E402
from umwd.render.blib import NodeBuilder  # noqa: E402

# ============================================================================================== stałe i ścieżki
UMWD = Path(__file__).resolve().parents[3]
SITE_JSON = UMWD / 'model' / 'site.json'
CACHE = UMWD / 'build' / 'kontekst_cache'
DOCS_IMG = UMWD / 'docs' / '60_wizualizacje' / 'img'
_M11 = (UMWD / '00_materialy' / '_rozpak' / '5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026'
        / 'M.11. KONTEKST HISTORYCZNY' / 'M.11. KONTEKST HISTORYCZNY')
ORTO_PLIK = _M11 / 'M.11.A. KONTEKST Ortofotomapa 01 B.png'
# Georeferencja ortofotomapy 01 B (2405×1679 px): dopasowanie (skala, obrót, przesunięcie) linii działek
# GESDZI z site.json do niebieskich linii ewidencyjnych na obrazie (minimalizacja odległości – transformata
# odległości; mediana odchyłki 0,0 px, p90 0,1 px; 0,847 m/px). px = s·R(θ)·[e,n] + t, oś y obrazu w dół.
ORTO_GEOREF = dict(px_na_m=1.180840858392133, rot_rad=-0.013635372314671514,
                   tx=1211.0649202344587, ty=1003.0167952149188)

Z0 = 119.25          # H [m n.p.m.] odpowiadające Z = 0
H_WODA = 115.5       # zwierciadło Odry/Oławy (przyjęte; wody gruntowe M.05: 115,07–115,95; pkt e-mapy 115,7)

DOMYSLNE = dict(
    site_json=str(SITE_JSON),
    cache_dir=str(CACHE),
    pora_roku='jesien',            # 'jesien' (29.10, jak zdjęcia M.10/F.17) | 'lato'
    obszar_inwestycji='pusty',     # 'pusty' – bez drzew/ogrodzeń/ogródków w obszarze inwestycji | 'istniejacy'
    H_woda=H_WODA,
    teren=True, woda=True, sasiedzi=True, budynki=True, most=True, helmy=True,
    zielen=True, ulica=True, dalsze=True,
    ortofoto=True, dalsze_bryly=True, dalsze_drzewa=True,
    okna_szczytu_maz19=True,       # okna w ścianie szczytowej Mazowieckiej 19 (do zamurowania wg M.07)
    gestosc_lisci=1.0,
    seed=7,
)

BOX_F = [(4, 5, 7, 6), (0, 2, 3, 1), (0, 4, 6, 2), (1, 3, 7, 5), (0, 1, 5, 4), (2, 6, 7, 3)]


# ============================================================================================== geometria – narzędzia
class Geo:
    """Akumulator geometrii: wierzchołki, ściany, klucz materiału na ścianę i atrybut 'rnd' (np. firanki)."""

    def __init__(self):
        self.V, self.F, self.M, self.R = [], [], [], []

    def add(self, verts, faces, m, rnd=0.0):
        o = len(self.V)
        self.V.extend(verts)
        for f in faces:
            self.F.append([o + i for i in f])
            self.M.append(m)
            self.R.append(rnd)

    def poly(self, pts, m, rnd=0.0):
        self.add(list(pts), [list(range(len(pts)))], m, rnd)

    def polyn(self, pts, nrm, m, rnd=0.0):
        """Wielokąt płaski z wymuszoną orientacją normalnej (nrm – wektor w świecie)."""
        P = np.asarray(pts, float)
        c = np.zeros(3)
        for i in range(len(P)):
            c += np.cross(P[i], P[(i + 1) % len(P)])
        if np.dot(c, nrm) < 0:
            pts = list(pts)[::-1]
        self.poly(pts, m, rnd)

    def belka(self, p, q, w, h, m, up=(0, 0, 1)):
        """Prostopadłościan wzdłuż odcinka p→q (przekrój w×h, 'h' wzdłuż kierunku zbliżonego do up)."""
        p, q = np.asarray(p, float), np.asarray(q, float)
        d = q - p
        L = np.linalg.norm(d)
        if L < 1e-6:
            return
        d /= L
        a = np.cross(d, up)
        if np.linalg.norm(a) < 1e-6:
            a = np.cross(d, (1, 0, 0))
        a /= np.linalg.norm(a)
        b = np.cross(a, d)
        vs = []
        for t in (p, q):
            for (sa, sb) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                vs.append(tuple(t + a * sa * w / 2 + b * sb * h / 2))
        F = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
        self.add(vs, F, m)

    def obiekt(self, name, ctx, coll, smooth=False):
        if not self.F:
            return None
        keys = []
        for k in self.M:
            if k not in keys:
                keys.append(k)
        slot = {k: i for i, k in enumerate(keys)}
        attrs = {'rnd': self.R} if any(r != 0.0 for r in self.R) else None
        ob = blib.mesh_from_arrays(name, self.V, self.F, [slot[k] for k in self.M],
                                   [ctx.mat(k) for k in keys], coll, smooth=smooth, face_attrs=attrs)
        return ob


class Ramka:
    """Lokalny układ ściany: u wzdłuż ściany (p0→p1), v w górę (od z0), w na zewnątrz (prawa strona dla
    wielokąta CCW). Układ (u, v, w) jest prawoskrętny."""

    def __init__(self, p0, p1, z0):
        self.x0, self.y0 = float(p0[0]), float(p0[1])
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        self.L = math.hypot(dx, dy)
        self.tx, self.ty = dx / self.L, dy / self.L
        self.nx, self.ny = self.ty, -self.tx
        self.z0 = z0

    def P(self, u, v, w=0.0):
        return (self.x0 + u * self.tx + w * self.nx, self.y0 + u * self.ty + w * self.ny, self.z0 + v)

    def box(self, g, u0, u1, v0, v1, w0, w1, m, rnd=0.0):
        vs = [self.P(u, v, w) for w in (w0, w1) for v in (v0, v1) for u in (u0, u1)]
        g.add(vs, BOX_F, m, rnd)

    def quad(self, g, u0, u1, v0, v1, w, m, rnd=0.0):
        g.add([self.P(u0, v0, w), self.P(u1, v0, w), self.P(u1, v1, w), self.P(u0, v1, w)], [(0, 1, 2, 3)], m, rnd)

    def profil(self, g, u0, u1, v, prof, m, konce=True):
        """Gzyms: profil [(w, dv), ...] (od lica ściany na dole, na zewnątrz i z powrotem do lica u góry)
        wyciągnięty wzdłuż u ∈ [u0, u1]."""
        for (w0, d0), (w1, d1) in zip(prof[:-1], prof[1:]):
            g.add([self.P(u0, v + d0, w0), self.P(u1, v + d0, w0), self.P(u1, v + d1, w1), self.P(u0, v + d1, w1)],
                  [(0, 1, 2, 3)], m)
        if konce:
            g.poly([self.P(u0, v + d, w) for (w, d) in prof], m)
            g.poly([self.P(u1, v + d, w) for (w, d) in prof][::-1], m)

    def wielokat(self, g, pts_uv, w, m, przod=True):
        """Płaski wielokąt (u, v) na głębokości w; przod=True → normalna +w."""
        pts = [self.P(u, v, w) for (u, v) in pts_uv]
        g.polyn(pts, (self.nx, self.ny, 0.0) if przod else (-self.nx, -self.ny, 0.0), m)

    def pryzma(self, g, pts_uv, w0, w1, m):
        """Pryzma z wielokąta (u, v) wyciągniętego w ∈ [w0, w1] (np. naczółek)."""
        n = len(pts_uv)
        self.wielokat(g, pts_uv, w1, m, True)
        for i in range(n):
            a, b = pts_uv[i], pts_uv[(i + 1) % n]
            q = [self.P(a[0], a[1], w0), self.P(b[0], b[1], w0), self.P(b[0], b[1], w1), self.P(a[0], a[1], w1)]
            # normalna boczna: prostopadła do krawędzi w płaszczyźnie (u, v), na zewnątrz wielokąta
            cu = sum(p[0] for p in pts_uv) / n
            cv = sum(p[1] for p in pts_uv) / n
            mu, mv = (a[0] + b[0]) / 2 - cu, (a[1] + b[1]) / 2 - cv
            nrm = np.array([self.tx * mu, self.ty * mu, mv])
            g.polyn(q, nrm, m)


def _ring_ccw(pts):
    P = Polygon(pts)
    if not P.exterior.is_ccw:
        pts = list(pts)[::-1]
    return [tuple(p) for p in pts]


def _inset_ring(pts, d):
    """Pierścień przesunięty do wnętrza o d (dwusieczne; dla wielokąta CCW)."""
    n = len(pts)
    out = []
    for i in range(n):
        p0, p1, p2 = np.array(pts[i - 1]), np.array(pts[i]), np.array(pts[(i + 1) % n])
        e1 = p1 - p0
        e2 = p2 - p1
        e1 /= np.linalg.norm(e1)
        e2 /= np.linalg.norm(e2)
        n1 = np.array([-e1[1], e1[0]])
        n2 = np.array([-e2[1], e2[0]])
        b = n1 + n2
        nb = np.linalg.norm(b)
        b = n1 if nb < 1e-6 else b / nb
        c = max(float(np.dot(b, n1)), 0.35)
        out.append(tuple(p1 + b * d / c))
    return out


def _poly_parts(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    if hasattr(g, 'geoms'):
        out = []
        for x in g.geoms:
            out.extend(_poly_parts(x))
        return out
    return []


def triangulacja(geom, cell=None):
    """Triangulacja (Multi)Polygon: przycięcie do siatki komórek (gęstość wierzchołków do drapowania na NMT)
    i triangulacja Delaunaya z ograniczeniami. Zwraca (V2 (n,2), F (m,3)) ze zgrzanymi wierzchołkami."""
    parts = _poly_parts(geom)
    tris = []
    for P in parts:
        if P.area < 1e-4:
            continue
        if cell:
            x0, y0, x1, y1 = P.bounds
            xs = np.arange(math.floor(x0 / cell) * cell, x1 + cell, cell)
            ys = np.arange(math.floor(y0 / cell) * cell, y1 + cell, cell)
            cells = [sbox(x, y, x + cell, y + cell) for x in xs[:-1] for y in ys[:-1]]
            if len(cells) > 1:
                pieces = shapely.intersection(np.array(cells, dtype=object), P)
            else:
                pieces = [P]
        else:
            pieces = [P]
        for pc in pieces:
            for q in _poly_parts(pc):
                if q.area < 1e-5:
                    continue
                c = list(q.exterior.coords)
                if len(c) == 5 and not q.interiors and abs(q.area - Polygon(c).minimum_rotated_rectangle.area) < 1e-6:
                    tris.append((c[0], c[1], c[2]))
                    tris.append((c[0], c[2], c[3]))
                    continue
                T = shapely.constrained_delaunay_triangles(q)
                for t in getattr(T, 'geoms', []):
                    cc = list(t.exterior.coords)[:3]
                    tris.append(tuple(cc))
    if not tris:
        return np.zeros((0, 2)), np.zeros((0, 3), int)
    A = np.array(tris).reshape(-1, 2)
    key = np.round(A * 1000).astype(np.int64)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    V = A[idx]
    F = inv.reshape(-1, 3)
    # orientacja CCW (normalne w górę)
    a, b, c = V[F[:, 0]], V[F[:, 1]], V[F[:, 2]]
    cr = (b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])
    F[cr < 0] = F[cr < 0][:, [0, 2, 1]]
    F = F[np.abs(cr) > 1e-9]
    return V, F


def _krawedzie_brzegowe(F):
    """Krawędzie brzegowe siatki trójkątów (użyte przez jedną ścianę), z orientacją zgodną ze ścianą."""
    E = np.concatenate([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]])
    k = np.sort(E, axis=1)
    _, inv, cnt = np.unique(k, axis=0, return_inverse=True, return_counts=True)
    return E[cnt[inv] == 1]


def siatka_drapowana(geom, zfun, cell=1.5, skirt=0.25):
    """Siatka powierzchni (Multi)Polygon drapowana na funkcji z(e, n) + fartuch w dół na brzegach (maskuje
    szczeliny między warstwami nawierzchni o różnych przesunięciach). Zwraca (V3, faces)."""
    V2, F = triangulacja(geom, cell)
    if len(F) == 0:
        return np.zeros((0, 3)), []
    z = zfun(V2[:, 0], V2[:, 1])
    V = np.c_[V2, z]
    faces = [tuple(f) for f in F]
    if skirt:
        B = _krawedzie_brzegowe(F)
        nv = len(V)
        ub = np.unique(B)
        low = {int(i): nv + j for j, i in enumerate(ub)}
        Vl = V[ub].copy()
        Vl[:, 2] -= skirt
        V = np.vstack([V, Vl])
        for a, b in B:
            faces.append((int(b), int(a), low[int(a)], low[int(b)]))
    return V, faces


# ============================================================================================== teren (NMT)
class Teren:
    """Model wysokościowy: TIN z pikiet terenowych M.02 (bez pikiet wykluczonych) + punkty wysokościowe e-mapy
    (uzupełnienie poza zasięgiem pomiaru, m.in. dojazd do mostu). Poza zasięgiem: IDW z łagodnym powrotem do
    poziomu bazowego (119,3 m) w odległości kilkudziesięciu metrów."""

    def __init__(self, site):
        T = site['teren']
        excl = {p['nr'] for p in T['pikiety_wykluczone_z_NMT']}
        pts = [(p[1], p[2], p[3]) for p in T['pikiety'] if p[4] == 1 and p[0] not in excl]
        for p in T['punkty_wysokosciowe_emapy']:
            if p['H'] < 117.5:      # punkty u podnóża nabrzeża / przy wodzie
                continue
            pts.append((p['e'], p['n'], p['H']))
        A = np.array(pts, float)
        _, ui = np.unique(np.round(A[:, :2], 2), axis=0, return_index=True)
        A = A[np.sort(ui)]
        self.A = A
        self.lin = LinearNDInterpolator(A[:, :2], A[:, 2])
        self.kd = cKDTree(A[:, :2])
        self.Hbaz = 119.3

    def H(self, e, n):
        e = np.atleast_1d(np.asarray(e, float))
        n = np.atleast_1d(np.asarray(n, float))
        h = self.lin(e, n)
        bad = np.isnan(h)
        if bad.any():
            d, i = self.kd.query(np.c_[e[bad], n[bad]], k=6)
            w = 1.0 / np.maximum(d, 0.5) ** 2
            hn = (self.A[i, 2] * w).sum(1) / w.sum(1)
            f = np.exp(-np.maximum(d[:, 0] - 3.0, 0) / 45.0)
            h[bad] = self.Hbaz + (hn - self.Hbaz) * f
        return h

    def z(self, e, n):
        return self.H(e, n) - Z0

    def z1(self, e, n):
        return float(self.z([e], [n])[0])


# ============================================================================================== materiały
class Materialy:
    """Rejestr materiałów proceduralnych (tworzone przy pierwszym użyciu)."""

    def __init__(self, ctx):
        self.ctx = ctx
        self.c = {}

    def __call__(self, name):
        if name in self.c:
            return self.c[name]
        f = getattr(self, 'm_' + name.split(':')[0], None)
        m = bpy.data.materials.new('K_' + name)
        if f is None:
            raise KeyError('brak materiału ' + name)
        f(m, *name.split(':')[1:])
        self.c[name] = m
        return m

    # ---------------------------------------------------------------- pomocnicze
    @staticmethod
    def uv_sciana(nb):
        """Wektor (u, v, 0) w metrach: dla ścian pionowych u = rzut na poziomą styczną, v = Z; dla poziomych (x, y)."""
        geo = nb.n('ShaderNodeNewGeometry')
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(geo.outputs['Position'], sp.inputs[0])
        sn = nb.n('ShaderNodeSeparateXYZ')
        nb.l(geo.outputs['True Normal'], sn.inputs[0])
        hl = nb.math('ADD', nb.math('SQRT', nb.math('ADD', nb.math('MULTIPLY', sn.outputs[0], sn.outputs[0]),
                                                      nb.math('MULTIPLY', sn.outputs[1], sn.outputs[1]))), 1e-4)
        u = nb.math('DIVIDE', nb.math('SUBTRACT', nb.math('MULTIPLY', sp.outputs[1], sn.outputs[0]),
                                      nb.math('MULTIPLY', sp.outputs[0], sn.outputs[1])), hl)
        vert = nb.math('LESS_THAN', nb.math('ABSOLUTE', sn.outputs[2]), 0.7)
        x = nb.mix(vert, sp.outputs[0], u, dtype='FLOAT')
        y = nb.mix(vert, sp.outputs[1], sp.outputs[2], dtype='FLOAT')
        cb = nb.n('ShaderNodeCombineXYZ')
        nb.l(x, cb.inputs[0])
        nb.l(y, cb.inputs[1])
        return cb.outputs[0]

    @staticmethod
    def _ramp(nb, fac, c0, c1, p0=0.0, p1=1.0):
        r = nb.n('ShaderNodeValToRGB')
        r.color_ramp.elements[0].position = p0
        r.color_ramp.elements[1].position = p1
        r.color_ramp.elements[0].color = (*c0, 1)
        r.color_ramp.elements[1].color = (*c1, 1)
        nb.l(fac, r.inputs['Fac'])
        return r.outputs['Color']

    @staticmethod
    def mgla_fac(nb, D=2600.0):
        cd = nb.n('ShaderNodeCameraData')
        return nb.math('SUBTRACT', 1.0, nb.math('EXPONENT', nb.math('DIVIDE', cd.outputs['View Distance'], -D)))

    @staticmethod
    def mgla(nb, col, D=2600.0, kolor=(0.42, 0.50, 0.62)):
        """(zgodność) – zwraca kolor bez zmian; mgłę dodaje mgla_shader()."""
        return col

    def mgla_shader(self, nb, shader, D=3200.0, kolor=(0.50, 0.60, 0.76), moc=0.2):
        """Perspektywa powietrzna: mieszanie shadera z emisją w barwie nieba przy horyzoncie wg odległości."""
        em = nb.n('ShaderNodeEmission', Strength=moc)
        nb.set(em, 'Color', kolor)
        mx = nb.n('ShaderNodeMixShader')
        nb.l(self.mgla_fac(nb, D), mx.inputs['Fac'])
        nb.l(shader.outputs[0] if hasattr(shader, 'outputs') else shader, mx.inputs[1])
        nb.l(em.outputs[0], mx.inputs[2])
        return mx

    def _bsdf(self, nb, color, rough=0.6, metal=0.0, spec=0.5, normal=None):
        b = nb.n('ShaderNodeBsdfPrincipled')
        nb.set(b, 'Base Color', color)
        nb.set(b, 'Roughness', rough)
        nb.set(b, 'Metallic', metal)
        if 'Specular IOR Level' in b.inputs:
            nb.set(b, 'Specular IOR Level', spec)
        if normal is not None:
            nb.l(normal, b.inputs['Normal'])
        return b

    def _plain(self, m, color, rough=0.5, metal=0.0, spec=0.5):
        nb = NodeBuilder(m)
        nb.output(self._bsdf(nb, color, rough, metal, spec))

    def _noise_mat(self, m, c0, c1, scale=2.0, rough=0.7, bump=0.15, fine=40.0, finebump=0.1, metal=0.0):
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        nz = nb.n('ShaderNodeTexNoise', Scale=scale, Detail=6.0, Roughness=0.6)
        nb.l(uv, nz.inputs['Vector'])
        col = self._ramp(nb, nz.outputs['Fac'], c0, c1, 0.3, 0.7)
        nf = nb.n('ShaderNodeTexNoise', Scale=fine, Detail=4.0)
        nb.l(uv, nf.inputs['Vector'])
        bmp = nb.n('ShaderNodeBump', Strength=finebump, Distance=0.01)
        nb.l(nf.outputs['Fac'], bmp.inputs['Height'])
        nb.output(self._bsdf(nb, col, rough, metal, normal=bmp.outputs['Normal']))

    def _uklad_cegiel(self, m, bw, bh, mortar, c1, c2, cm, rough=0.75, bump=0.3, var=0.25, scale_noise=3.0,
                      wet_z=None, offset=0.5):
        """Wzór bloków/kostki/płyt (Brick Texture) we współrzędnych uv_sciana (metry)."""
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        br = nb.n('ShaderNodeTexBrick', {'offset': offset, 'squash': 1.0}, Scale=1.0)
        nb.set(br, 'Brick Width', bw)
        nb.set(br, 'Row Height', bh)
        nb.set(br, 'Mortar Size', mortar)
        nb.set(br, 'Mortar Smooth', 0.15)
        nb.set(br, 'Bias', 0.0)
        nb.set(br, 'Color1', c1)
        nb.set(br, 'Color2', c2)
        nb.set(br, 'Mortar', cm)
        nb.l(uv, br.inputs['Vector'])
        nz = nb.n('ShaderNodeTexNoise', Scale=scale_noise, Detail=6.0)
        nb.l(uv, nz.inputs['Vector'])
        col = nb.mix(var, br.outputs['Color'], nz.outputs['Color'], blend='MULTIPLY')
        if wet_z is not None:
            geo = nb.n('ShaderNodeNewGeometry')
            sz = nb.n('ShaderNodeSeparateXYZ')
            nb.l(geo.outputs['Position'], sz.inputs[0])
            wet = nb.math('LESS_THAN', sz.outputs[2], wet_z)
            col = nb.mix(nb.math('MULTIPLY', wet, 0.65), col, (0.035, 0.045, 0.025), blend='MIX')
        bmp = nb.n('ShaderNodeBump', Strength=bump, Distance=0.02, props={'invert': True})
        nb.l(br.outputs['Fac'], bmp.inputs['Height'])
        nb.output(self._bsdf(nb, col, rough, normal=bmp.outputs['Normal']))

    # ---------------------------------------------------------------- nawierzchnie
    def m_asfalt(self, m):
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        n1 = nb.n('ShaderNodeTexNoise', Scale=0.35, Detail=4.0)
        nb.l(uv, n1.inputs['Vector'])
        col = self._ramp(nb, n1.outputs['Fac'], (0.032, 0.032, 0.034), (0.07, 0.068, 0.066), 0.35, 0.7)
        n2 = nb.n('ShaderNodeTexNoise', Scale=90.0, Detail=2.0)
        nb.l(uv, n2.inputs['Vector'])
        r = nb.math('ADD', nb.math('MULTIPLY', n1.outputs['Fac'], 0.25), 0.62)
        bmp = nb.n('ShaderNodeBump', Strength=0.25, Distance=0.004)
        nb.l(n2.outputs['Fac'], bmp.inputs['Height'])
        nb.output(self._bsdf(nb, col, r, normal=bmp.outputs['Normal']))

    def m_kostka_granit(self, m):   # jezdnia z kostki granitowej (Mazowiecka, Wybrzeże Słowackiego)
        self._uklad_cegiel(m, 0.17, 0.115, 0.012, (0.21, 0.20, 0.17), (0.15, 0.145, 0.125), (0.08, 0.075, 0.065),
                           rough=0.72, bump=0.45, var=0.4, scale_noise=7.0)

    def m_kostka_bet(self, m):
        self._uklad_cegiel(m, 0.2, 0.1, 0.006, (0.30, 0.29, 0.27), (0.25, 0.24, 0.23), (0.17, 0.165, 0.16),
                           rough=0.8, bump=0.25, var=0.3, scale_noise=5.0)

    def m_plyty_bet(self, m):
        self._uklad_cegiel(m, 0.5, 0.5, 0.005, (0.36, 0.35, 0.33), (0.31, 0.30, 0.29), (0.2, 0.19, 0.18),
                           rough=0.82, bump=0.2, var=0.35, scale_noise=1.5, offset=0.0)

    def m_zwir(self, m):
        self._noise_mat(m, (0.24, 0.21, 0.17), (0.36, 0.33, 0.28), scale=6.0, rough=0.95, fine=120.0, finebump=0.4)

    def m_ziemia(self, m):
        self._noise_mat(m, (0.07, 0.055, 0.04), (0.15, 0.12, 0.085), scale=1.2, rough=0.95, fine=30.0, finebump=0.3)

    def m_plac_zabaw(self, m):
        self._noise_mat(m, (0.30, 0.26, 0.18), (0.42, 0.37, 0.27), scale=3.0, rough=0.95, fine=150.0, finebump=0.3)

    def m_trawa(self, m):
        """Trawnik: zmienność barwy w 3 skalach (kępy, płaty, prześwity ziemi), mikrorelief; jesienią opadłe liście."""
        jes = self.ctx.opts['pora_roku'] == 'jesien'
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        n1 = nb.n('ShaderNodeTexNoise', Scale=0.18, Detail=5.0, Roughness=0.6)
        nb.l(uv, n1.inputs['Vector'])
        if jes:
            col = self._ramp(nb, n1.outputs['Fac'], (0.045, 0.075, 0.012), (0.12, 0.13, 0.02), 0.32, 0.72)
        else:
            col = self._ramp(nb, n1.outputs['Fac'], (0.03, 0.07, 0.01), (0.07, 0.13, 0.02), 0.32, 0.72)
        n2 = nb.n('ShaderNodeTexNoise', Scale=1.6, Detail=8.0, Roughness=0.7)
        nb.l(uv, n2.inputs['Vector'])
        col = nb.mix(0.55, col, n2.outputs['Color'], blend='OVERLAY')
        # prześwity ziemi / wydeptane płaty
        n4 = nb.n('ShaderNodeTexNoise', Scale=0.6, Detail=6.0)
        nb.l(uv, n4.inputs['Vector'])
        ziem = nb.math('MULTIPLY', nb.math('GREATER_THAN', n4.outputs['Fac'], 0.66), 0.55)
        col = nb.mix(ziem, col, (0.07, 0.055, 0.035))
        if jes:   # opadłe liście – rozproszone plamy
            n3 = nb.n('ShaderNodeTexNoise', Scale=0.9, Detail=6.0)
            nb.l(uv, n3.inputs['Vector'])
            v = nb.n('ShaderNodeTexVoronoi', Scale=55.0)
            nb.l(uv, v.inputs['Vector'])
            f = nb.math('MULTIPLY', nb.math('MULTIPLY', nb.math('SUBTRACT', n3.outputs['Fac'], 0.45), 3.0),
                        nb.math('LESS_THAN', v.outputs['Distance'], 0.22))
            f = nb.math('MINIMUM', nb.math('MAXIMUM', f, 0.0), 1.0)
            leaf = self._ramp(nb, v.outputs['Distance'], (0.28, 0.10, 0.02), (0.33, 0.22, 0.05))
            col = nb.mix(nb.math('MULTIPLY', f, 0.45), col, leaf)
        nf = nb.n('ShaderNodeTexNoise', Scale=220.0, Detail=2.0)
        nb.l(uv, nf.inputs['Vector'])
        nv = nb.n('ShaderNodeTexVoronoi', Scale=60.0)
        nb.l(uv, nv.inputs['Vector'])
        h = nb.math('ADD', nf.outputs['Fac'], nb.math('MULTIPLY', nv.outputs['Distance'], 0.8))
        bmp = nb.n('ShaderNodeBump', Strength=0.9, Distance=0.015)
        nb.l(h, bmp.inputs['Height'])
        rr = nb.math('ADD', nb.math('MULTIPLY', n2.outputs['Fac'], 0.15), 0.82)
        nb.output(self._bsdf(nb, col, rr, spec=0.25, normal=bmp.outputs['Normal']))

    def m_granit(self, m):          # krawężniki, cokoły
        self._noise_mat(m, (0.17, 0.165, 0.16), (0.28, 0.27, 0.26), scale=6.0, rough=0.6, fine=60.0, finebump=0.15)

    def m_schody(self, m):
        self._uklad_cegiel(m, 1.0, 0.3, 0.008, (0.28, 0.27, 0.26), (0.25, 0.24, 0.23), (0.15, 0.15, 0.14), rough=0.75,
                           bump=0.2, var=0.2)

    def m_beton(self, m):
        self._noise_mat(m, (0.25, 0.245, 0.235), (0.36, 0.35, 0.335), scale=1.5, rough=0.85, fine=50.0, finebump=0.1)

    def m_mur_nabrzeza(self, m):    # kamienny mur nabrzeża, zawilgocony przy wodzie
        zw = self.ctx.z_woda
        self._uklad_cegiel(m, 1.1, 0.42, 0.015, (0.19, 0.175, 0.15), (0.15, 0.14, 0.12), (0.10, 0.095, 0.085),
                           rough=0.85, bump=0.5, var=0.35, scale_noise=1.0, wet_z=zw + 0.7)

    def m_cegla(self, m):
        self._uklad_cegiel(m, 0.25, 0.065, 0.01, (0.30, 0.12, 0.07), (0.22, 0.09, 0.055), (0.32, 0.30, 0.27),
                           rough=0.85, bump=0.3, var=0.3)

    def m_woda(self, m):
        nb = NodeBuilder(m)
        geo = nb.n('ShaderNodeNewGeometry')
        mp = nb.n('ShaderNodeMapping', Scale=(1.0, 2.2, 1.0))
        nb.l(geo.outputs['Position'], mp.inputs['Vector'])
        n1 = nb.n('ShaderNodeTexNoise', Scale=0.55, Detail=5.0, Roughness=0.55)
        nb.l(mp.outputs[0], n1.inputs['Vector'])
        n2 = nb.n('ShaderNodeTexNoise', Scale=3.5, Detail=3.0)
        nb.l(geo.outputs['Position'], n2.inputs['Vector'])
        h = nb.math('ADD', n1.outputs['Fac'], nb.math('MULTIPLY', n2.outputs['Fac'], 0.35))
        bmp = nb.n('ShaderNodeBump', Strength=0.22, Distance=0.05)
        nb.l(h, bmp.inputs['Height'])
        n3 = nb.n('ShaderNodeTexNoise', Scale=0.02, Detail=2.0)
        nb.l(geo.outputs['Position'], n3.inputs['Vector'])
        col = self._ramp(nb, n3.outputs['Fac'], (0.03, 0.045, 0.038), (0.05, 0.065, 0.05), 0.3, 0.7)
        b = self._bsdf(nb, col, 0.035, spec=0.5, normal=bmp.outputs['Normal'])
        nb.set(b, 'IOR', 1.33)
        nb.output(self.mgla_shader(nb, b, D=4500.0, moc=0.15))

    # ---------------------------------------------------------------- elewacje
    def m_tynk(self, m, hexcol='a0a0a0', brud='0.25', bonio='0'):
        """Tynk: kolor bazowy (hex sRGB), brud (zacieki pionowe, plamy), opcjonalne boniowanie (rozstaw w m)."""
        c = tuple((int(hexcol[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))
        brud = float(brud)
        bon = float(bonio)
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        n1 = nb.n('ShaderNodeTexNoise', Scale=0.6, Detail=6.0, Roughness=0.55)
        nb.l(uv, n1.inputs['Vector'])
        dk = tuple(x * 0.82 for x in c)
        lt = tuple(min(1.0, x * 1.08) for x in c)
        col = self._ramp(nb, n1.outputs['Fac'], dk, lt, 0.3, 0.7)
        # zacieki: szum rozciągnięty w pionie
        mp = nb.n('ShaderNodeMapping', Scale=(1.0, 0.08, 1.0))
        nb.l(uv, mp.inputs['Vector'])
        n2 = nb.n('ShaderNodeTexNoise', Scale=2.0, Detail=4.0)
        nb.l(mp.outputs[0], n2.inputs['Vector'])
        st = nb.math('MULTIPLY', nb.math('MAXIMUM', nb.math('SUBTRACT', n2.outputs['Fac'], 0.5), 0.0), 2.0 * brud)
        col = nb.mix(st, col, tuple(x * 0.55 for x in c))
        n3 = nb.n('ShaderNodeTexNoise', Scale=0.35, Detail=6.0)
        nb.l(uv, n3.inputs['Vector'])
        pl = nb.math('MULTIPLY', nb.math('GREATER_THAN', n3.outputs['Fac'], 0.66), brud * 0.8)
        col = nb.mix(pl, col, tuple(x * 0.7 for x in c))
        rough = 0.88
        nf = nb.n('ShaderNodeTexNoise', Scale=70.0, Detail=3.0)
        nb.l(uv, nf.inputs['Vector'])
        h = nb.math('MULTIPLY', nf.outputs['Fac'], 0.3)
        if bon > 0:
            sv = nb.n('ShaderNodeSeparateXYZ')
            nb.l(uv, sv.inputs[0])
            fr = nb.math('FRACT', nb.math('DIVIDE', sv.outputs[1], bon))
            gro = nb.math('LESS_THAN', fr, 0.045 / bon)
            col = nb.mix(nb.math('MULTIPLY', gro, 0.75), col, tuple(x * 0.35 for x in c))
            h = nb.math('SUBTRACT', h, nb.math('MULTIPLY', gro, 1.0))
        bmp = nb.n('ShaderNodeBump', Strength=0.35, Distance=0.02)
        nb.l(h, bmp.inputs['Height'])
        nb.output(self._bsdf(nb, col, rough, spec=0.35, normal=bmp.outputs['Normal']))

    def m_szklo(self, m):
        """Szyba okienna widziana z zewnątrz: ciemne wnętrze + odbicia; atrybut 'rnd' → firanki / rolety."""
        nb = NodeBuilder(m)
        att = nb.n('ShaderNodeAttribute', {'attribute_name': 'rnd', 'attribute_type': 'GEOMETRY'})
        cur = nb.math('GREATER_THAN', att.outputs['Fac'], 0.62)
        col = nb.mix(cur, (0.012, 0.014, 0.016), (0.30, 0.29, 0.26))
        tint = nb.math('MULTIPLY', att.outputs['Fac'], 0.012)
        b = self._bsdf(nb, col, 0.03, spec=0.9)
        nb.set(b, 'IOR', 1.52)
        if 'Coat Weight' in b.inputs:
            nb.set(b, 'Coat Weight', 1.0)
            nb.set(b, 'Coat Roughness', 0.02)
        nb.output(b)
        _ = tint

    def m_rama(self, m, hexcol='e8e6e0'):
        c = tuple((int(hexcol[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))
        self._plain(m, c, 0.45)

    def m_drzwi(self, m):
        self._noise_mat(m, (0.05, 0.028, 0.016), (0.09, 0.05, 0.028), scale=8.0, rough=0.55, fine=40.0, finebump=0.05)

    def m_blacha(self, m):
        self._plain(m, (0.16, 0.16, 0.16), 0.45, 0.7)

    def m_papa(self, m):
        self._noise_mat(m, (0.05, 0.05, 0.05), (0.09, 0.09, 0.088), scale=1.0, rough=0.92, fine=60.0, finebump=0.2)

    def m_dach_szary(self, m):
        self._noise_mat(m, (0.14, 0.14, 0.145), (0.22, 0.22, 0.225), scale=0.6, rough=0.7, fine=30.0, finebump=0.1)

    def m_dachowka(self, m):
        self._uklad_cegiel(m, 0.3, 0.17, 0.01, (0.48, 0.12, 0.035), (0.40, 0.095, 0.03), (0.2, 0.06, 0.02),
                           rough=0.6, bump=0.6, var=0.25, scale_noise=2.0)

    def m_kamien_cokol(self, m):
        self._uklad_cegiel(m, 0.9, 0.45, 0.008, (0.30, 0.27, 0.22), (0.26, 0.235, 0.19), (0.2, 0.19, 0.17),
                           rough=0.8, bump=0.3, var=0.3)

    def m_piaskowiec(self, m):      # boniowany cokół M17
        self._uklad_cegiel(m, 1.2, 0.5, 0.025, (0.46, 0.38, 0.26), (0.42, 0.35, 0.24), (0.25, 0.21, 0.15),
                           rough=0.8, bump=0.6, var=0.25)

    # ---------------------------------------------------------------- most
    def m_granit_pylon(self, m):
        self._uklad_cegiel(m, 1.05, 0.52, 0.012, (0.40, 0.34, 0.27), (0.32, 0.28, 0.23), (0.42, 0.39, 0.34),
                           rough=0.78, bump=0.55, var=0.4, scale_noise=1.8)

    def m_granit_jasny(self, m):
        self._uklad_cegiel(m, 0.7, 0.9, 0.01, (0.46, 0.40, 0.32), (0.40, 0.355, 0.29), (0.44, 0.41, 0.36),
                           rough=0.75, bump=0.4, var=0.3, offset=0.0)

    def m_nisza(self, m):
        self._plain(m, (0.012, 0.012, 0.012), 0.9)

    def m_stal_most(self, m):       # jasnoniebieska farba konstrukcji mostu
        self._noise_mat(m, (0.24, 0.42, 0.62), (0.30, 0.50, 0.70), scale=3.0, rough=0.42, fine=40.0, finebump=0.03)

    def m_stal_ciemna(self, m):
        self._plain(m, (0.035, 0.038, 0.04), 0.4, 0.8)

    def m_stal_ocynk(self, m):
        self._plain(m, (0.42, 0.42, 0.42), 0.38, 1.0)

    def m_szyny(self, m):
        self._plain(m, (0.55, 0.54, 0.52), 0.22, 1.0)

    def m_farba_biala(self, m):
        self._noise_mat(m, (0.62, 0.62, 0.6), (0.78, 0.78, 0.76), scale=4.0, rough=0.55, fine=80.0, finebump=0.05)

    def m_klosz(self, m):
        nb = NodeBuilder(m)
        b = self._bsdf(nb, (0.85, 0.85, 0.8), 0.15)
        nb.output(b)

    def m_siatka(self, m):
        """Siatka ogrodzeniowa: przezroczystość wg proceduralnej kraty."""
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(uv, sp.inputs[0])
        a = nb.math('LESS_THAN', nb.math('FRACT', nb.math('DIVIDE', sp.outputs[0], 0.06)), 0.12)
        b = nb.math('LESS_THAN', nb.math('FRACT', nb.math('DIVIDE', sp.outputs[1], 0.06)), 0.12)
        wire = nb.math('MAXIMUM', a, b)
        met = self._bsdf(nb, (0.10, 0.12, 0.10), 0.45, 0.6)
        tr = nb.n('ShaderNodeBsdfTransparent')
        mx = nb.n('ShaderNodeMixShader')
        nb.l(wire, mx.inputs['Fac'])
        nb.l(tr.outputs[0], mx.inputs[1])
        nb.l(met.outputs[0], mx.inputs[2])
        nb.output(mx)

    def m_bryla_dalsza(self, m, hexcol='b8b2a8'):
        """Proste bryły dalszego otoczenia: tynk + proceduralna siatka okien (u co 3,2 m, kondygnacje co 3,4 m)."""
        c = tuple((int(hexcol[i:i + 2], 16) / 255.0) ** 2.2 for i in (0, 2, 4))
        nb = NodeBuilder(m)
        uv = self.uv_sciana(nb)
        sp = nb.n('ShaderNodeSeparateXYZ')
        nb.l(uv, sp.inputs[0])
        geo = nb.n('ShaderNodeNewGeometry')
        sn = nb.n('ShaderNodeSeparateXYZ')
        nb.l(geo.outputs['True Normal'], sn.inputs[0])
        vert = nb.math('LESS_THAN', nb.math('ABSOLUTE', sn.outputs[2]), 0.7)
        fu = nb.math('FRACT', nb.math('DIVIDE', sp.outputs[0], 3.2))
        fv = nb.math('FRACT', nb.math('DIVIDE', nb.math('ADD', sp.outputs[1], 0.0), 3.4))
        wu = nb.math('MULTIPLY', nb.math('GREATER_THAN', fu, 0.28), nb.math('LESS_THAN', fu, 0.72))
        wv = nb.math('MULTIPLY', nb.math('GREATER_THAN', fv, 0.30), nb.math('LESS_THAN', fv, 0.78))
        win = nb.math('MULTIPLY', nb.math('MULTIPLY', wu, wv), vert)
        gl = nb.math('GREATER_THAN', sp.outputs[1], 1.2)    # parter bez okien poniżej 1,2 m wzgl. Z=0
        win = nb.math('MULTIPLY', win, gl)
        n1 = nb.n('ShaderNodeTexNoise', Scale=0.2, Detail=3.0)
        nb.l(uv, n1.inputs['Vector'])
        wall = self._ramp(nb, n1.outputs['Fac'], tuple(x * 0.85 for x in c), c, 0.3, 0.7)
        roof = (0.11, 0.11, 0.11)
        base = nb.mix(vert, roof, wall)
        col = nb.mix(win, base, (0.02, 0.025, 0.03))
        rgh = nb.mix(win, 0.85, 0.08, dtype='FLOAT')
        nb.output(self.mgla_shader(nb, self._bsdf(nb, col, rgh, spec=0.6)))

    def m_ortofoto(self, m):
        nb = NodeBuilder(m)
        tex = nb.n('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(self.ctx.orto_tex), check_existing=True)
        tex.interpolation = 'Cubic'
        uvn = nb.n('ShaderNodeUVMap')
        nb.l(uvn.outputs[0], tex.inputs['Vector'])
        hs = nb.n('ShaderNodeHueSaturation')
        if self.ctx.opts['pora_roku'] == 'jesien':
            nb.set(hs, 'Hue', 0.475)
            nb.set(hs, 'Saturation', 1.1)
        else:
            nb.set(hs, 'Saturation', 1.1)
        nb.set(hs, 'Value', 0.5)
        bc = nb.n('ShaderNodeBrightContrast', Bright=0.0, Contrast=0.18)
        nb.l(tex.outputs['Color'], bc.inputs['Color'])
        nb.l(bc.outputs[0], hs.inputs['Color'])
        nb.output(self.mgla_shader(nb, self._bsdf(nb, hs.outputs[0], 0.92, spec=0.2)))

    def m_teren_daleki(self, m):
        nb = NodeBuilder(m)
        geo = nb.n('ShaderNodeNewGeometry')
        nz = nb.n('ShaderNodeTexNoise', Scale=0.012, Detail=6.0)
        nb.l(geo.outputs['Position'], nz.inputs['Vector'])
        col = self._ramp(nb, nz.outputs['Fac'], (0.05, 0.055, 0.04), (0.11, 0.105, 0.09), 0.35, 0.7)
        nb.output(self.mgla_shader(nb, self._bsdf(nb, col, 0.95, spec=0.2)))


# ============================================================================================== kontekst budowy
class Kontekst:
    def __init__(self, scene, opts):
        self.sc = scene
        self.opts = dict(DOMYSLNE)
        self.opts.update(opts or {})
        self.site = json.load(open(self.opts['site_json'], encoding='utf-8'))
        self.z_woda = self.opts['H_woda'] - Z0
        self.teren = Teren(self.site)
        self.mat = Materialy(self)
        self.rng = np.random.default_rng(self.opts['seed'])
        self.cache = Path(self.opts['cache_dir'])
        self.cache.mkdir(parents=True, exist_ok=True)
        self.info = {'czasy_s': {}, 'obiekty': {}}
        self.root = bpy.data.collections.new('KONTEKST')
        scene.collection.children.link(self.root)
        self.kol = {}
        fr = self.site['crs']['ramka_mapy']['pts']
        self.ramka = Polygon(fr)
        self.inwest = Polygon(self.site['granice']['obszar_inwestycji']['pts'])
        self.budynki_poly = [Polygon(b['pts']).buffer(0) for b in self.site['budynki']['items']]
        self.woda_poly = None
        self.jezdnie_poly = None

    def coll(self, name):
        if name not in self.kol:
            c = bpy.data.collections.new(name)
            self.root.children.link(c)
            self.kol[name] = c
        return self.kol[name]

    def czas(self, nazwa, t0):
        self.info['czasy_s'][nazwa] = round(time.time() - t0, 1)


# ============================================================================================== woda – geometria brzegu
def _brzeg(site):
    """Linia brzegu (lądu) od pn. ramki do pd.: nabrzeże GSSWWP (Odra, potem Oława) + linia wody przy skarpie."""
    W = site['woda']['linia_brzegu']
    odra = [tuple(p) for p in W[2]['pts']]
    olawa = [tuple(p) for p in W[0]['pts']]
    i = next(k for k, p in enumerate(odra) if abs(p[0] - 123.4) < 0.2 and abs(p[1] - 76.0) < 0.2)
    j = next(k for k, p in enumerate(olawa) if abs(p[0] - 123.4) < 0.2 and abs(p[1] - 76.0) < 0.2)
    mur = odra[:i + 1] + olawa[j + 1:]           # do (139,7; 30,4) – mur nabrzeża
    # dalej ku pd.: skarpa nad Oławą (linia wody ~2–3 m od górnej krawędzi skarpy GSSZSN), WWP (140,6; −29,4)
    woda_skarpa = [(140.4, 24.0), (140.7, 8.0), (141.2, -4.3), (141.0, -20.6), (140.6, -29.4), (139.3, -35.52)]
    gora_skarpy = [(136.3, 30.2), (136.3, 23.2), (137.1, 7.9), (138.0, -4.3), (137.9, -20.6), (136.2, -35.52)]
    return mur, woda_skarpa, gora_skarpy


def _woda_ramka(ctx):
    mur, ws, gs = _brzeg(ctx.site)
    fr = ctx.ramka.bounds
    ring = mur + ws + [(fr[2], fr[1]), (fr[2], fr[3]), (mur[0][0], fr[3])]
    P = Polygon(ring).buffer(0)
    return P.intersection(ctx.ramka)


# ============================================================================================== nawierzchnie
_SZER = {'jezdnia': ('kostka_granit', -0.05), 'jezdnia_mb': ('asfalt', -0.05), 'jezdnia_kb': ('kostka_granit', -0.05),
         'jezdnia_i': ('kostka_granit', -0.05), 'chodnik_bt': ('plyty_bet', 0.06), 'chodnik_kb': ('kostka_bet', 0.06),
         'chodnik_mb': ('asfalt', 0.06), 'chodnik_zw': ('zwir', 0.04), 'chodnik_i': ('plyty_bet', 0.06),
         'trawnik': ('trawa', 0.03), 'teren': ('trawa', 0.03), 'plac_zabaw': ('plac_zabaw', 0.05),
         'schody': ('schody', 0.10), 'ziemia': ('ziemia', 0.02), 'podworze': ('kostka_bet', 0.04)}

# ręczne korekty klasyfikacji (punkt wewnątrz pola → klasa); weryfikacja: ortofotomapa M.11.A 03, zdjęcia M.09
_KOREKTY = [
    ((86.0, 60.0), 'trawnik'),        # trawnik obszaru inwestycji / skweru (dz. 9/1, 10/3)
    ((20.0, 20.0), 'trawnik'),        # trawnik na zach. od Mazowieckiej (zdjęcie F.17.B)
    ((25.0, 50.0), 'trawnik'),
    ((25.0, 85.0), 'trawnik'),
    ((22.0, 130.0), 'trawnik'),
    ((75.0, 118.0), 'trawnik'),       # zieleń przy przyczółku (krzewy)
    ((95.0, 105.0), 'trawnik'),
    ((75.0, 10.0), 'trawnik'),        # ogródki (stan istniejący – trawa/ziemia)
    ((63.0, 120.0), 'chodnik_bt'),
]


def _linie_e_mapy(site):
    W = site['warstwy_emapy_surowe']['warstwy']
    lines = []
    for k in ('kraweznik', 'jezdnia', 'chodnik', 'obszar_utwardzony', 'trawnik', 'GSSKOA', 'GSLKRW', 'GSSKOD',
              'GSSUTR', 'GSSSCK', 'plac_zabaw', 'GSSDSO', 'GSLDSO', 'GSSZMO', 'GSSIPD'):
        for o in W[k]['obiekty']:
            if 'pts' not in o or len(o['pts']) < 2:
                continue
            p = o['pts'] + ([o['pts'][0]] if o.get('z') == 1 else [])
            lines.append(LineString(p))
    return lines


def _przedluz_wolne_konce(lines, frame, maxd=4.0, maxd_frame=12.0):
    """Przedłużenie wiszących końców linii (do najbliższego przecięcia) – domyka pola nawierzchni."""
    M = unary_union(lines)
    segs = list(M.geoms) if hasattr(M, 'geoms') else [M]
    from collections import Counter
    cnt = Counter()
    for g in segs:
        cs = list(g.coords)
        cnt[tuple(np.round(cs[0], 4))] += 1
        cnt[tuple(np.round(cs[-1], 4))] += 1
    tree = STRtree(segs)
    ext = []
    fb = frame.exterior
    for g in segs:
        cs = list(g.coords)
        for (a, b) in ((cs[0], cs[1]), (cs[-1], cs[-2])):
            if cnt[tuple(np.round(a, 4))] != 1:
                continue
            dx, dy = a[0] - b[0], a[1] - b[1]
            L = math.hypot(dx, dy)
            if L < 1e-6:
                continue
            dx /= L
            dy /= L
            md = maxd_frame if fb.distance(Point(a)) < maxd_frame else maxd
            ray = LineString([(a[0] + dx * 1e-3, a[1] + dy * 1e-3), (a[0] + dx * md, a[1] + dy * md)])
            best = None
            for j in tree.query(ray):
                h = segs[j]
                if h is g:
                    continue
                x = ray.intersection(h)
                if x.is_empty:
                    continue
                pts = [x] if x.geom_type == 'Point' else [p for p in getattr(x, 'geoms', [x]) if p.geom_type == 'Point']
                for p in pts:
                    dd = Point(a).distance(p)
                    if best is None or dd < best[0]:
                        best = (dd, p)
            if best:
                ext.append(LineString([a, (best[1].x, best[1].y)]))
    return ext


def klasyfikacja_nawierzchni(ctx):
    """Pola nawierzchni: poligonizacja krawędzi e-mapy (BDOT500 + pomiar NMT) z domknięciem wiszących końców,
    klasyfikacja wg opisów nawierzchni (j.kb., ch.bt., …), trawników, schodów i reguł. Zwraca {klasa: geom}."""
    site = ctx.site
    lines = _linie_e_mapy(site)
    for b in site['budynki']['items']:
        lines.append(LineString(b['pts'] + [b['pts'][0]]))
    mur, ws, gs = _brzeg(site)
    lines.append(LineString(mur + ws))
    lines.append(ctx.ramka.exterior)
    ext = _przedluz_wolne_konce(lines, ctx.ramka)
    polys, *_ = polygonize_full(unary_union(lines + ext))
    faces = [p for p in polys.geoms if p.area > 0.05]
    U = site['ulice_i_sytuacja']
    labels = [(Point(t['e'], t['n']), t['tekst']) for t in U['nawierzchnie_opisy']]
    traw = [Polygon(o['pts']).buffer(0) for o in U['trawniki'] if o.get('zamknieta') and len(o['pts']) > 2]
    schody = [Polygon(o['pts']).buffer(0) for o in U['schody_terenowe'] if o.get('zamknieta') and len(o['pts']) > 2]
    plac = [Polygon(o['pts']).buffer(0) for o in U['plac_zabaw'] if len(o['pts']) > 2]
    woda = ctx.woda_poly
    bud = unary_union(ctx.budynki_poly)
    klasy = {}

    def dodaj(k, g):
        klasy.setdefault(k, []).append(g)

    for f in faces:
        c = f.representative_point()
        if woda is not None and woda.contains(c):
            continue
        if bud.contains(c):
            continue
        k = None
        for pt, korekta in [(Point(p), kk) for p, kk in _KOREKTY]:
            if f.contains(pt):
                k = korekta
        if k is None:
            lab = [t for p, t in labels if f.contains(p)]
            jl = [t for t in lab if t.startswith('j.')]
            if jl:                      # jezdnia ma pierwszeństwo (pole może obejmować przyległy chodnik)
                lab = [max(set(jl), key=jl.count)]
            if lab and not (f.area > 900 and not lab[0].startswith('j')):
                t = lab[0]
                if t.startswith('j.'):
                    k = {'j.kb.': 'jezdnia_kb', 'j.mb.': 'jezdnia_mb'}.get(t, 'jezdnia_i')
                else:
                    t2 = t.replace('ch.', '')
                    k = {'bt.': 'chodnik_bt', 'kb.': 'chodnik_kb', 'mb.': 'chodnik_mb', 'zw.': 'chodnik_zw'}.get(
                        t2, 'chodnik_i')
        if k is None:
            if any(s.contains(c) for s in schody):
                k = 'schody'
            elif any(p.contains(c) for p in plac):
                k = 'plac_zabaw'
            elif any(t.contains(c) for t in traw):
                k = 'trawnik'
            elif f.area / max(f.length, 1e-6) < 0.9:      # wąskie pasy – ścieżki/chodniki
                k = 'chodnik_bt'
            else:
                k = 'teren'
        dodaj(k, f)
    out = {k: unary_union(v) for k, v in klasy.items()}
    # skarpa nad Oławą – osobna klasa (pochyła)
    sk = Polygon(gs + ws[::-1]).buffer(0)
    out = {k: g.difference(sk) for k, g in out.items()}
    out['skarpa'] = sk.intersection(ctx.ramka)
    if ctx.opts['obszar_inwestycji'] == 'pusty':
        # obszar inwestycji: teren wyrównany – trawa (bez ogródków, ścieżek wewnętrznych)
        inw = ctx.inwest
        for k in list(out):
            if k not in ('jezdnia_kb', 'jezdnia_mb', 'skarpa'):
                out[k] = out[k].difference(inw)
        out['trawnik'] = unary_union([out.get('trawnik', Polygon()), inw.difference(unary_union(ctx.budynki_poly))])
    ctx.jezdnie_poly = unary_union([g for k, g in out.items() if k.startswith('jezdnia')])
    return out


def zbuduj_teren(ctx):
    t0 = time.time()
    coll = ctx.coll('K_teren')
    kl = klasyfikacja_nawierzchni(ctx)
    ctx.info['nawierzchnie_m2'] = {k: round(g.area, 1) for k, g in kl.items()}
    mur, ws, gs = _brzeg(ctx.site)
    L_gora = LineString(gs)
    L_woda = LineString(ws)
    for k, g in kl.items():
        if g.is_empty:
            continue
        mat, dz = _SZER.get(k, ('trawa', 0.03))
        if k == 'skarpa':
            def zf(e, n):
                pts = shapely.points(np.c_[e, n])
                d1 = shapely.distance(pts, L_gora)
                d2 = shapely.distance(pts, L_woda)
                t = d1 / np.maximum(d1 + d2, 1e-6)
                zt = ctx.teren.z(e, n) + 0.02
                return zt + (ctx.z_woda - 0.4 - zt) * np.clip(t, 0, 1) ** 1.3
            V, F = siatka_drapowana(g, zf, cell=1.0, skirt=0.0)
        else:
            V, F = siatka_drapowana(g, lambda e, n, dz=dz: ctx.teren.z(e, n) + dz, cell=1.5, skirt=0.25)
        if len(F):
            blib.mesh_from_arrays('teren_' + k, V, F, mats=[ctx.mat(mat)], coll=coll)
    # krawężniki: suma buforów linii krawężników (bez dublowania warstw BDOT500 i pomiaru)
    W = ctx.site['warstwy_emapy_surowe']['warstwy']
    kl_lines = []
    for lay in ('kraweznik', 'GSLKRW'):
        for o in W[lay]['obiekty']:
            if 'pts' in o and len(o['pts']) >= 2:
                kl_lines.append(LineString(o['pts']).buffer(0.075, cap_style='flat'))
    kr = unary_union(kl_lines)
    if ctx.woda_poly is not None:
        kr = kr.difference(ctx.woda_poly.buffer(0.3))
    kr = kr.difference(unary_union(ctx.budynki_poly).buffer(0.2))
    if ctx.opts['obszar_inwestycji'] == 'pusty':
        kr = kr.difference(ctx.inwest.buffer(-0.5))
    kr = shapely.segmentize(kr, 1.0)
    V2, F = triangulacja(kr, None)
    if len(F):
        zt = ctx.teren.z(V2[:, 0], V2[:, 1]) + 0.085
        V = np.c_[V2, zt]
        faces = [tuple(f) for f in F]
        B = _krawedzie_brzegowe(F)
        nv = len(V)
        ub = np.unique(B)
        low = {int(i): nv + j for j, i in enumerate(ub)}
        Vl = V[ub].copy()
        Vl[:, 2] -= 0.3
        V = np.vstack([V, Vl])
        for a, b in B:
            faces.append((int(b), int(a), low[int(a)], low[int(b)]))
        blib.mesh_from_arrays('kraweznik', V, faces, mats=[ctx.mat('granit')], coll=coll)
    # mury terenowe (mur pomiędzy podwórzem Mazowieckiej 19 a działką; wys. ~2 m wg pikiet koron muru)
    g = Geo()
    for o in W['GSSDSO']['obiekty']:
        if 'pts' not in o or len(o['pts']) < 3:
            continue
        P = Polygon(o['pts']).buffer(0)
        if P.area < 1.0 or P.area > 30.0:
            continue
        if ctx.woda_poly is not None and P.distance(ctx.woda_poly) < 1.0:
            continue
        _pryzma_drapowana(ctx, g, P, -0.3, 2.0, 'cegla')
    g.obiekt('mury_terenowe', ctx, coll)
    ctx.czas('teren', t0)


def _pryzma_drapowana(ctx, g, P, dz0, dz1, m, top_flat=False):
    """Pryzma z wielokąta P (shapely) od terenu+dz0 do terenu+dz1 (lub poziomo przy top_flat)."""
    P = shapely.segmentize(P, 1.0)
    for part in _poly_parts(P):
        ring = _ring_ccw(list(part.exterior.coords)[:-1])
        e = np.array([p[0] for p in ring])
        n = np.array([p[1] for p in ring])
        z = ctx.teren.z(e, n)
        zt = (np.full_like(z, z.max() + dz1) if top_flat else z + dz1)
        zb = z + dz0
        k = len(ring)
        V2, F = triangulacja(part, None)
        if len(F):
            zz = ctx.teren.z(V2[:, 0], V2[:, 1])
            ztop = (np.full(len(V2), z.max() + dz1) if top_flat else zz + dz1)
            g.add([(V2[i, 0], V2[i, 1], ztop[i]) for i in range(len(V2))], [tuple(f) for f in F], m)
        for i in range(k):
            j = (i + 1) % k
            g.add([(e[i], n[i], zb[i]), (e[j], n[j], zb[j]), (e[j], n[j], zt[j]), (e[i], n[i], zt[i])],
                  [(0, 1, 2, 3)], m)


# ============================================================================================== woda i nabrzeże
def zbuduj_wode(ctx):
    t0 = time.time()
    coll = ctx.coll('K_woda')
    zw = ctx.z_woda
    # płaszczyzna wody: obejmuje obszar ortofotomapy (rzeki poza ramką) – pod lądem jest niewidoczna
    E0, E1, N0, N1 = -1100.0, 1200.0, -900.0, 900.0
    blib.mesh_from_arrays('woda', [(E0, N0, zw), (E1, N0, zw), (E1, N1, zw), (E0, N1, zw)], [(0, 1, 2, 3)],
                          mats=[ctx.mat('woda')], coll=coll)
    mur, ws, gs = _brzeg(ctx.site)
    g = Geo()
    # mur nabrzeża (lico od strony wody), od korony (teren) do dna poniżej zwierciadła
    P = shapely.segmentize(LineString(mur), 1.5)
    pts = list(P.coords)
    e = np.array([p[0] for p in pts])
    n = np.array([p[1] for p in pts])
    zt = ctx.teren.z(e, n) + 0.02
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        d = np.array([b[0] - a[0], b[1] - a[1], 0.0])
        left = np.array([-d[1], d[0], 0.0])      # strona wody (wsch.)
        q = [(a[0], a[1], zw - 2.0), (b[0], b[1], zw - 2.0), (b[0], b[1], zt[i + 1]), (a[0], a[1], zt[i])]
        g.polyn(q, left, 'mur_nabrzeza')
    # parapet (GSSDSO wzdłuż nabrzeża, ~0,4 m) – kamień 0,6 m + balustrada stalowa
    W = ctx.site['warstwy_emapy_surowe']['warstwy']
    for o in W['GSSDSO']['obiekty']:
        if 'pts' not in o or len(o['pts']) < 10:
            continue
        Pp = Polygon(o['pts']).buffer(0)
        _pryzma_drapowana(ctx, g, Pp, -0.2, 0.62, 'granit')
        # balustrada: słupki co 2 m + pochwyt
        i0 = next(k for k, p in enumerate(mur) if p[1] < 109)
        cl = LineString(mur[i0:])
        cl = cl.intersection(Pp.buffer(0.5))
        for line in ([cl] if cl.geom_type == 'LineString' else list(getattr(cl, 'geoms', []))):
            if line.length < 2:
                continue
            line = line.offset_curve(-0.2)
            if line.is_empty or line.geom_type != 'LineString':
                continue
            dd = np.arange(0, line.length, 2.0)
            pp = [line.interpolate(x) for x in dd]
            zz = ctx.teren.z(np.array([p.x for p in pp]), np.array([p.y for p in pp])) + 0.62
            for p, z in zip(pp, zz):
                g.belka((p.x, p.y, z), (p.x, p.y, z + 0.5), 0.05, 0.05, 'stal_ciemna')
            for (p, z), (q, z2) in zip(list(zip(pp, zz))[:-1], list(zip(pp, zz))[1:]):
                g.belka((p.x, p.y, z + 0.5), (q.x, q.y, z2 + 0.5), 0.06, 0.04, 'stal_ciemna')
                g.belka((p.x, p.y, z + 0.25), (q.x, q.y, z2 + 0.25), 0.02, 0.02, 'stal_ciemna')
    g.obiekt('nabrzeze', ctx, coll)
    # barka-restauracja przy nabrzeżu (ortofotomapa M.11.A: ok. e 121–141, n 62–100) – uproszczona
    gb = Geo()
    _barka(ctx, gb, (131.5, 81.0), math.radians(-20.0), 30.0, 9.0)
    _barka(ctx, gb, (145.0, 27.0), math.radians(-12.0), 20.0, 7.0, dach_pv=True)
    gb.obiekt('barki', ctx, coll)
    ctx.czas('woda', t0)


def _barka(ctx, g, c, rot, L, B, dach_pv=False):
    zw = ctx.z_woda
    R = Ramka((c[0] - math.sin(rot) * L / 2, c[1] - math.cos(rot) * L / 2),
              (c[0] + math.sin(rot) * L / 2, c[1] + math.cos(rot) * L / 2), zw)
    R.box(g, 0, L, -0.6, 0.9, -B / 2, B / 2, 'stal_ciemna')
    R.box(g, 1.0, L - 1.0, 0.9, 1.0, -B / 2 + 0.2, B / 2 - 0.2, 'drzwi')
    R.box(g, 3.0, L - 6.0, 1.0, 3.6, -B / 2 + 1.0, B / 2 - 1.0, 'tynk:dcdcd6:0.1:0')
    R.box(g, 2.6, L - 5.6, 3.6, 3.8, -B / 2 + 0.7, B / 2 - 0.7, 'stal_ocynk' if dach_pv else 'blacha')
    if not dach_pv:
        for k in range(3):
            u = 5 + k * (L - 10) / 2
            R.box(g, u - 0.05, u + 0.05, 1.0, 3.2, B / 2 - 0.6, B / 2 - 0.5, 'stal_ciemna')


# ============================================================================================== elewacje LOD3/LOD2
class Otwor:
    __slots__ = ('u0', 'u1', 'v0', 'v1', 'typ', 'd', 'szpr', 'rama')

    def __init__(self, uc, w, v0, v1, typ='okno', d=0.22, szpr='T', rama='rama'):
        self.u0, self.u1, self.v0, self.v1 = uc - w / 2, uc + w / 2, v0, v1
        self.typ, self.d, self.szpr, self.rama = typ, d, szpr, rama


def sciana(g, R, u0, u1, v0, v1, otwory, strefy, rng, m_osc=None):
    """Lico ściany z otworami (siatka punktów podziału), ościeża, okna (rama, szprosy, szyba) lub drzwi.
    strefy: [(v_od, v_do, materiał)] – materiał lica w pasach wysokości."""
    U = {u0, u1}
    V = {v0, v1}
    for o in otwory:
        U.update((max(u0, o.u0), min(u1, o.u1)))
        V.update((max(v0, o.v0), min(v1, o.v1)))
    for (a, b, _) in strefy:
        if v0 < a < v1:
            V.add(a)
        if v0 < b < v1:
            V.add(b)
    U = sorted(U)
    V = sorted(V)

    def mat_v(v):
        for (a, b, m) in strefy:
            if a <= v < b:
                return m
        return strefy[-1][2]

    for i in range(len(U) - 1):
        uc = (U[i] + U[i + 1]) / 2
        for j in range(len(V) - 1):
            vc = (V[j] + V[j + 1]) / 2
            if any(o.u0 < uc < o.u1 and o.v0 < vc < o.v1 for o in otwory):
                continue
            R.quad(g, U[i], U[i + 1], V[j], V[j + 1], 0.0, mat_v(vc))
    for o in otwory:
        okno(g, R, o, m_osc or mat_v((o.v0 + o.v1) / 2), rng)


def okno(g, R, o, m_osc, rng):
    d = o.d
    u0, u1, v0, v1 = o.u0, o.u1, o.v0, o.v1
    tn = np.array([R.tx, R.ty, 0.0])
    nn = np.array([R.nx, R.ny, 0.0])
    # ościeża
    g.polyn([R.P(u0, v0, 0), R.P(u0, v0, -d), R.P(u0, v1, -d), R.P(u0, v1, 0)], tn, m_osc)
    g.polyn([R.P(u1, v0, 0), R.P(u1, v0, -d), R.P(u1, v1, -d), R.P(u1, v1, 0)], -tn, m_osc)
    g.polyn([R.P(u0, v1, 0), R.P(u1, v1, 0), R.P(u1, v1, -d), R.P(u0, v1, -d)], (0, 0, -1), m_osc)
    if o.typ != 'drzwi':
        g.polyn([R.P(u0, v0, 0), R.P(u1, v0, 0), R.P(u1, v0, -d), R.P(u0, v0, -d)], (0, 0, 1), m_osc)
    rnd = float(rng.random())
    fw = 0.065
    w0, w1 = -d, -d + 0.07
    rm = o.rama
    if o.typ == 'slepe':
        R.quad(g, u0, u1, v0, v1, -d, m_osc)
        return
    if o.typ == 'drzwi':
        vt = v1 - 0.55 if (v1 - v0) > 2.9 else v1
        R.box(g, u0, u1, v0, vt, -d - 0.02, -d + 0.05, 'drzwi')
        # podział skrzydeł + płyciny
        uc = (u0 + u1) / 2
        R.box(g, uc - 0.02, uc + 0.02, v0, vt, -d + 0.05, -d + 0.07, 'drzwi')
        for (a, b) in ((u0 + 0.12, uc - 0.12), (uc + 0.12, u1 - 0.12)):
            if b - a > 0.2:
                R.box(g, a, b, v0 + 0.3, v0 + 1.0, -d + 0.05, -d + 0.08, 'drzwi')
                R.box(g, a, b, v0 + 1.25, vt - 0.25, -d + 0.05, -d + 0.08, 'drzwi')
        if vt < v1:
            R.box(g, u0, u1, vt, vt + 0.08, w0, w1, rm)
            R.quad(g, u0 + 0.05, u1 - 0.05, vt + 0.08, v1 - 0.05, -d + 0.03, 'szklo', rnd * 0.5)
            R.box(g, u0, u1, v1 - 0.05, v1, w0, w1, rm)
        return
    # rama okienna
    R.box(g, u0, u0 + fw, v0, v1, w0, w1, rm)
    R.box(g, u1 - fw, u1, v0, v1, w0, w1, rm)
    R.box(g, u0 + fw, u1 - fw, v0, v0 + fw, w0, w1, rm)
    R.box(g, u0 + fw, u1 - fw, v1 - fw, v1, w0, w1, rm)
    R.quad(g, u0 + fw, u1 - fw, v0 + fw, v1 - fw, -d + 0.035, 'szklo', rnd)
    wb = 0.05
    uc = (u0 + u1) / 2
    if o.szpr in ('T', '+', '2'):
        vt = v0 + (v1 - v0) * (0.72 if o.szpr == 'T' else 0.5)
        if o.szpr in ('T', '2'):
            R.box(g, uc - wb / 2, uc + wb / 2, v0 + fw, vt if o.szpr == 'T' else v1 - fw, w0 + 0.01, w1, rm)
        if o.szpr in ('T', '+'):
            R.box(g, u0 + fw, u1 - fw, vt - wb / 2, vt + wb / 2, w0 + 0.01, w1, rm)
        if o.szpr == '+':
            R.box(g, uc - wb / 2, uc + wb / 2, v0 + fw, v1 - fw, w0 + 0.01, w1, rm)
    # parapet zewnętrzny (blacha)
    R.box(g, u0 - 0.04, u1 + 0.04, v0 - 0.04, v0, -d + 0.02, 0.07, 'blacha')


def obramienie(g, R, o, b=0.12, t=0.04, m='rama'):
    R.box(g, o.u0 - b, o.u0, o.v0 - 0.02, o.v1 + b, 0, t, m)
    R.box(g, o.u1, o.u1 + b, o.v0 - 0.02, o.v1 + b, 0, t, m)
    R.box(g, o.u0, o.u1, o.v1, o.v1 + b, 0, t, m)


def naczolek(g, R, o, typ, m, wys=0.6, wysieg=0.14, nad=0.12):
    """Naczółek nad oknem: 'tr' – trójkątny, 'luk' – odcinkowy, 'prosty' – gzyms nadokienny."""
    a, b = o.u0 - 0.22, o.u1 + 0.22
    vb = o.v1 + nad
    R.box(g, a, b, vb, vb + 0.12, 0, wysieg, m)
    R.box(g, a + 0.04, b - 0.04, vb - 0.06, vb, 0, wysieg * 0.7, m)
    if typ == 'tr':
        R.pryzma(g, [(a, vb + 0.12), (b, vb + 0.12), ((a + b) / 2, vb + 0.12 + wys)], 0, wysieg, m)
    elif typ == 'luk':
        pts = [(a, vb + 0.12)]
        for k in range(1, 8):
            th = math.pi * (1 - k / 8)
            pts.append(((a + b) / 2 + (b - a) / 2 * math.cos(th), vb + 0.12 + wys * 0.75 * math.sin(th)))
        pts.append((b, vb + 0.12))
        R.pryzma(g, pts, 0, wysieg, m)


def _gz(over, h):
    """Prosty profil gzymsu (wysięg over, wysokość h)."""
    return [(0.0, 0.0), (over * 0.3, 0.0), (over * 0.3, h * 0.25), (over, h * 0.55), (over, h * 0.85),
            (over * 1.05, h * 0.9), (over * 1.05, h), (0.0, h)]


def _pas(over, h):
    return [(0.0, 0.0), (over, 0.0), (over, h), (0.0, h)]


# ---------------------------------------------------------------------------------------------- Mazowiecka 19
def kamienica_maz19(ctx, g):
    """Mazowiecka 19 (1880) – LOD3 wg inwentaryzacji M.07 (03.2021): elewacja frontowa (s. 12), boczna (s. 13),
    tylna (s. 14), przekrój A-A (s. 10). Wysokości v [m] względem chodnika przed frontem (H 118,51)."""
    rng = ctx.rng
    b = next(x for x in ctx.site['budynki']['items'] if x['nazwa'] == 'Mazowiecka 19')
    P = [tuple(p) for p in b['pts']]   # 0 NE (tył/szczyt), 1 NW (front/szczyt), 2 SW (front), 3 SE (tył), 4 E
    zr = 118.51 - Z0
    vb = -0.9
    T_M = 'tynk:b1a998:0.5:0'           # tynk szarobeżowy, zabrudzony, z ubytkami (zdjęcie F.17.B)
    T_B = 'tynk:a89f8e:0.5:0.6'         # boniowanie pasowe
    T_C = 'kamien_cokol'
    TOP = 21.8                          # korona murka attykowego (≈140,31 m n.p.m.)
    # ---- front (zach.) u od narożnika pn. (szczyt) – rysunek s. 12, skala pozioma 1,80 cm/px
    R = Ramka(P[1], P[2], zr)
    k = R.L / 17.81
    ax = [x * k for x in (1.71, 3.74, 5.92, 8.05, 10.26, 12.51, 14.47, 16.31)]
    par = [x * k for x in (1.73, 3.73, 5.72, 10.47, 12.52, 14.47, 16.31)]
    ot = [Otwor(u, 1.02, 1.48, 3.57) for u in par]
    ot.append(Otwor(8.15 * k, 1.42, 0.28, 3.40, typ='drzwi', d=0.35))
    pietra = [(5.20, 7.05, 1.06, 'T'), (8.80, 10.85, 1.08, 'T'), (12.47, 14.22, 1.04, 'T'), (15.94, 17.43, 0.94, 'T'),
              (19.50, 19.92, 0.76, '2')]
    for (a, c, w, s) in pietra:
        for u in ax:
            ot.append(Otwor(u, w, a, c, szpr=s, d=0.25))
    strefy = [(vb, 0.86, T_C), (0.86, 4.50, T_B), (4.50, 8.78, T_M), (8.78, 15.50, T_B), (15.50, TOP + 1, T_M)]
    sciana(g, R, 0, R.L, vb, TOP, ot, strefy, rng)
    # dekoracja
    R.profil(g, 0, R.L, 4.50, _gz(0.28, 0.62), T_M)                     # gzyms nad parterem
    for u in ax:                                                            # I p.: edikule z kolumienkami
        o = Otwor(u, 1.06, 5.20, 7.05)
        R.box(g, o.u0 - 0.22, o.u0 - 0.05, 5.12, 7.27, 0, 0.12, T_M)
        R.box(g, o.u1 + 0.05, o.u1 + 0.22, 5.12, 7.27, 0, 0.12, T_M)
        R.box(g, o.u0 - 0.32, o.u1 + 0.32, 7.27, 7.80, 0, 0.16, T_M)
        R.box(g, o.u0 - 0.12, o.u1 + 0.12, 7.95, 8.62, 0, 0.04, T_M)      # płycina pod oknem II p.
    R.profil(g, 0, R.L, 8.70, _pas(0.07, 0.10), T_M)
    for u in ax:                                                            # II p.: opaski + naczółki łukowe
        o = Otwor(u, 1.08, 8.80, 10.85)
        obramienie(g, R, o, 0.11, 0.05, T_M)
        naczolek(g, R, o, 'luk', T_M, wys=0.55)
    R.profil(g, 0, R.L, 11.86, _gz(0.16, 0.58), T_M)                     # gzyms podokienny III p.
    for u in ax:                                                            # III p.: naczółki trójkątne
        o = Otwor(u, 1.04, 12.47, 14.22)
        obramienie(g, R, o, 0.11, 0.05, T_M)
        naczolek(g, R, o, 'tr', T_M, wys=0.75)
    R.profil(g, 0, R.L, 15.40, _pas(0.08, 0.20), T_M)
    for u in ax:                                                            # IV p.: opaski
        obramienie(g, R, Otwor(u, 0.94, 15.94, 17.43), 0.09, 0.04, T_M)
    piers = [0.18] + [(ax[i] + ax[i + 1]) / 2 for i in range(len(ax) - 1)] + [R.L - 0.18]
    for u in piers:                                                         # lizeny IV p.
        R.box(g, u - 0.17, u + 0.17, 15.60, 17.83, 0, 0.06, T_M)
    R.profil(g, 0, R.L, 17.83, _pas(0.09, 0.46), T_M)                     # belkowanie
    for i in range(len(ax) - 1):                                            # płyciny fryzu attykowego
        R.box(g, ax[i] + 0.55, ax[i + 1] - 0.55, 18.75, 20.05, 0, 0.025, T_M)
    R.profil(g, 0, R.L, 20.33, [(0, 0), (0.12, 0), (0.12, 0.12), (0.30, 0.18), (0.30, 0.30), (0.62, 0.40),
                                (0.62, 0.58), (0.66, 0.62), (0.66, 0.65), (0, 0.65)], T_M)
    R.box(g, -0.05, R.L, TOP, TOP + 0.06, -0.05, 0.05, 'blacha')
    # ---- szczyt (pn.) – s. 13; u od narożnika tylnego (wsch.) do frontu
    R = Ramka(P[0], P[1], zr)
    k = R.L / 15.95
    ot = []
    if ctx.opts['okna_szczytu_maz19']:
        for uc, rows in ((0.85, (19.85, 16.62, 12.98, 9.25)), (6.42, (19.85, 16.62)), (14.9, (19.85, 16.62, 12.98, 9.25))):
            for vc in rows:
                ot.append(Otwor(uc * k, 0.55, vc - 0.32, vc + 0.32, szpr='2', d=0.2))
        for vc, w, h in ((16.95, 0.6, 0.45), (13.58, 0.6, 0.65), (9.98, 0.5, 0.55), (6.53, 0.5, 0.6)):
            ot.append(Otwor(8.36 * k, w, vc - h / 2, vc + h / 2, szpr='none', d=0.2))
    sciana(g, R, 0, R.L, vb, TOP, ot, [(vb, TOP + 1, 'tynk:b9b2a6:0.45:0')], rng)
    R.profil(g, R.L - 0.7, R.L, 20.33, [(0, 0), (0.3, 0.1), (0.62, 0.4), (0.62, 0.65), (0, 0.65)], T_M)
    R.box(g, -0.05, R.L + 0.05, TOP, TOP + 0.06, -0.05, 0.05, 'blacha')
    # pozostałość muru dawnej zabudowy przy szczycie (wys. ok. 5,4 m, „fragment muru”, s. 13)
    R.box(g, 0.35, 15.0 * k, vb, 5.30, 0.0, 0.42, 'tynk:8f8a80:0.6:0')
    R.box(g, 0.30, 15.0 * k + 0.05, 5.30, 5.36, -0.02, 0.48, 'blacha')
    # ---- tył (wsch.) – s. 14; u od pd. (Mazowiecka 17); wysokości względem podwórza (−0,42 wzgl. chodnika)
    R = Ramka(P[3], P[4], zr - 0.42)
    k = R.L / 13.73
    ot = []
    rows = [(1.97, 3.94), (5.84, 7.84), (9.50, 11.27), (13.13, 14.86), (16.80, 18.20)]
    for uc in (1.08, 3.11, 9.30, 11.70):
        for (a, c) in rows:
            ot.append(Otwor(uc * k, 1.0, a, c, szpr='T', d=0.22))
        ot.append(Otwor(uc * k, 0.62, 19.80, 20.20, szpr='2', d=0.2))
    for (a, c) in ((3.76, 5.64), (7.40, 9.40), (11.00, 13.00), (14.60, 16.60), (18.20, 20.10)):
        ot.append(Otwor(6.36 * k, 1.29, a, c, szpr='+', d=0.22))
    ot.append(Otwor(6.36 * k, 1.0, 0.0, 2.30, typ='drzwi', d=0.25))
    sciana(g, R, 0, R.L, vb + 0.42, TOP + 0.42, ot, [(vb, 0.9, T_C), (0.9, 30, 'tynk:bdb5a7:0.45:0')], rng)
    R.profil(g, 0, R.L, 20.75, _gz(0.25, 0.30), 'tynk:bdb5a7:0.45:0')
    R.box(g, -0.05, R.L + 0.05, TOP + 0.42, TOP + 0.48, -0.05, 0.05, 'blacha')
    # krótki uskok 4→0 i ściana pd. (szczyt przy Mazowieckiej 17 – widoczny ponad niższym dachem)
    for (pa, pb) in ((P[4], P[0]), (P[2], P[3])):
        R = Ramka(pa, pb, zr)
        R.quad(g, 0, R.L, vb, TOP, 0.0, 'tynk:a8a196:0.5:0')
    # ---- dach płaski z murkiem attykowym i kominami
    ring = _ring_ccw(P)
    inn = _inset_ring(ring, 0.30)
    _dach_plaski(g, ring, inn, zr + 20.95, zr + TOP, 'papa', 'tynk:beb6a8:0.35:0')
    R = Ramka(P[1], P[2], zr)
    for (u, w) in ((2.6, -3.0), (5.3, -6.5), (10.4, -3.2), (15.6, -2.6), (8.2, -11.0)):
        _komin(g, R, u, w, zr + 20.95, 1.7)
    ctx.info['obiekty']['Mazowiecka 19'] = 'LOD3, attyka %.2f m n.p.m.' % (118.51 + TOP)


def _komin(g, R, u, w, z, h, sx=0.65, sy=1.25):
    R2 = Ramka(R.P(u - sx / 2, 0, w)[:2], R.P(u + sx / 2, 0, w)[:2], z)
    R2.box(g, 0, sx, 0, h, -sy / 2, sy / 2, 'cegla')
    R2.box(g, -0.06, sx + 0.06, h, h + 0.12, -sy / 2 - 0.06, sy / 2 + 0.06, 'beton')


def _dach_plaski(g, ring, inn, z_dach, z_murek, m_dach, m_murek):
    g.poly([(x, y, z_dach) for (x, y) in inn], m_dach)
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        a, b = ring[i], ring[j]
        c, d = inn[i], inn[j]
        g.add([(a[0], a[1], z_murek), (b[0], b[1], z_murek), (d[0], d[1], z_murek), (c[0], c[1], z_murek)],
              [(0, 1, 2, 3)], m_murek)
        g.add([(c[0], c[1], z_dach), (c[0], c[1], z_murek), (d[0], d[1], z_murek), (d[0], d[1], z_dach)],
              [(0, 1, 2, 3)], m_murek)


def _dach_kopertowy(g, ring, z0, d, h, m, m_okap='blacha', okap=0.35):
    """Dach kopertowy/mansardowy przybliżony: pierścień okapu → pierścień wewnętrzny (odsunięty o d, wyżej o h)
    → płaska kalenica. Działa dla wielokątów wypukłych lub prawie wypukłych."""
    out = _inset_ring(ring, -okap)
    inn = _inset_ring(ring, d)
    if not Polygon(inn).is_valid or Polygon(inn).area < 1.0 or not Polygon(inn).exterior.is_ccw:
        inn = _inset_ring(ring, d * 0.5)
        h *= 0.5
        if not Polygon(inn).is_valid or not Polygon(inn).exterior.is_ccw:
            g.poly([(x, y, z0) for (x, y) in ring], m)
            return
    n = len(ring)
    for i in range(n):
        j = (i + 1) % n
        a, b = out[i], out[j]
        c, dd = inn[i], inn[j]
        g.add([(a[0], a[1], z0 - 0.05), (b[0], b[1], z0 - 0.05), (dd[0], dd[1], z0 + h), (c[0], c[1], z0 + h)],
              [(0, 1, 2, 3)], m)
        g.add([(a[0], a[1], z0 - 0.25), (b[0], b[1], z0 - 0.25), (b[0], b[1], z0 - 0.05), (a[0], a[1], z0 - 0.05)],
              [(0, 1, 2, 3)], m_okap)
    g.poly([(x, y, z0 + h) for (x, y) in inn], m)
    g.poly([(x, y, z0 - 0.25) for (x, y) in out][::-1], m_okap)


# ---------------------------------------------------------------------------------------------- Wybrzeże Słowackiego 5
def kamienica_ws5(ctx, g):
    """Wybrzeże J. Słowackiego 5 – LOD3: osie okien z rzutów M.08 (2001, skany 1:100) i zdjęcia F.17.A
    (7 osi od frontu, wejście w osi pn.), okno w ścianie szczytowej na I p. (0,90×1,14 m, M.08)."""
    rng = ctx.rng
    NW, SW, SE, NE = (101.98, 28.52), (102.61, 10.72), (118.626, 10.917), (118.16, 29.46)
    zr = float(ctx.teren.z([120.3], [20.0])[0])      # chodnik przed frontem
    vb = -0.9
    T_G = 'tynk:cfcfc9:0.25:0'           # jasnoszary tynk pięter (zdjęcie F.17.A)
    T_P = 'tynk:aaa595:0.3:0.55'         # boniowany parter, beżowoszary
    T_T = 'tynk:a9a59c:0.45:0'           # elewacja tylna / szczyt
    TOP = 19.8
    # ---- front (wsch.) od pd. do pn.
    R = Ramka(SE, NE, zr)
    ax = [1.9, 4.3, 6.75, 9.25, 11.6, 14.0, 16.4]
    ot = [Otwor(u, 1.2, 1.40, 3.60, d=0.28) for u in ax[:6]]
    ot.append(Otwor(ax[6], 1.35, 0.15, 3.65, typ='drzwi', d=0.40))
    for (a, c, w) in ((5.70, 8.00, 1.2), (9.40, 11.50, 1.2), (12.90, 14.90, 1.15), (16.60, 17.90, 1.05)):
        for u in ax:
            ot.append(Otwor(u, w, a, c, szpr='T', d=0.26))
    strefy = [(vb, 0.80, 'kamien_cokol'), (0.80, 4.40, T_P), (4.40, TOP + 1, T_G)]
    sciana(g, R, 0, R.L, vb, TOP, ot, strefy, rng)
    R.profil(g, 0, R.L, 4.40, _gz(0.26, 0.55), T_G)
    for v in (5.55, 9.25, 12.75, 16.45):
        R.profil(g, 0, R.L, v, _pas(0.07, 0.12), T_G)
    piers = [0.45] + [(ax[i] + ax[i + 1]) / 2 for i in range(len(ax) - 1)] + [R.L - 0.45]
    for u in piers:
        R.box(g, u - 0.16, u + 0.16, 4.95, 16.30, 0, 0.07, T_G)
    for u in ax:
        o = Otwor(u, 1.2, 5.70, 8.00)
        obramienie(g, R, o, 0.12, 0.05, T_G)
        naczolek(g, R, o, 'prosty', T_G)
        o = Otwor(u, 1.2, 9.40, 11.50)
        obramienie(g, R, o, 0.12, 0.05, T_G)
        naczolek(g, R, o, 'luk', T_G, wys=0.5)
        o = Otwor(u, 1.15, 12.90, 14.90)
        obramienie(g, R, o, 0.11, 0.05, T_G)
        naczolek(g, R, o, 'tr', T_G, wys=0.62)
        obramienie(g, R, Otwor(u, 1.05, 16.60, 17.90), 0.09, 0.04, T_G)
    R.profil(g, 0, R.L, 18.20, _pas(0.06, 0.35), T_G)
    R.profil(g, 0, R.L, 18.60, [(0, 0), (0.10, 0), (0.10, 0.12), (0.30, 0.2), (0.30, 0.32), (0.55, 0.45),
                                (0.55, 0.62), (0.58, 0.66), (0.58, 0.72), (0, 0.72)], T_G)
    # ---- tył (zach.) od pn. do pd. (rzut I p.: 6 osi + okno klatki schodowej w połowie kondygnacji)
    R = Ramka(NW, SW, zr)
    ot = []
    for u in (2.21, 3.71, 6.41, 12.51, 14.68, 16.35):
        for (a, c) in ((1.60, 3.45), (5.90, 7.75), (9.60, 11.45), (13.10, 14.95), (16.60, 18.00)):
            ot.append(Otwor(u, 1.19, a, c, szpr='T', d=0.22))
    for (a, c) in ((3.60, 5.20), (7.90, 9.50), (11.50, 13.10), (15.00, 16.60)):
        ot.append(Otwor(9.31, 0.67, a, c, szpr='none', d=0.22))
    ot.append(Otwor(9.31, 1.1, 0.0, 2.3, typ='drzwi', d=0.25))
    sciana(g, R, 0, R.L, vb, TOP, ot, [(vb, 0.6, 'kamien_cokol'), (0.6, 40, T_T)], rng)
    R.profil(g, 0, R.L, 18.85, _gz(0.30, 0.45), T_T)
    # ---- szczyt (pn.) od frontu (wsch.) do tyłu
    R = Ramka(NE, NW, zr)
    sciana(g, R, 0, R.L, vb, TOP, [Otwor(7.35, 0.90, 5.90, 7.04, szpr='2', d=0.22)], [(vb, 0.6, 'kamien_cokol'),
                                                                                      (0.6, 40, T_T)], rng)
    R.profil(g, 0, 0.7, 18.60, [(0, 0), (0.3, 0.1), (0.55, 0.45), (0.58, 0.72), (0, 0.72)], T_G)
    # ---- ściana pd. (wspólna z nr 6)
    R = Ramka(SW, SE, zr)
    R.quad(g, 0, R.L, vb, TOP, 0.0, T_T)
    ring = _ring_ccw([NW, SW, SE, NE])
    _dach_kopertowy(g, ring, zr + TOP, 5.0, 2.2, 'dach_szary', okap=0.05)
    R = Ramka(SE, NE, zr)
    for (u, w) in ((3.0, -6.5), (8.0, -7.5), (12.5, -6.0), (16.0, -8.5), (5.5, -10.5)):
        _komin(g, R, u, w, zr + TOP + 1.0, 2.0)
    ctx.info['obiekty']['Wybrzeże Słowackiego 5'] = 'LOD3, gzyms ok. %.1f m n.p.m.' % (Z0 + zr + 19.3)


# ---------------------------------------------------------------------------------------------- LOD2+
# parametry budynków LOD2 (wysokości wg liczby kondygnacji EGiB i zdjęć F.17/M.09/M.10)
_LOD2 = {
    'Wybrzeze J. Slowackiego 6': dict(gzyms=19.6, kond=5, dach=('kop', 5.0, 2.2), tynk='9a978e', bonio=0.55, oc='a3a096'),
    'Wybrzeze J. Slowackiego 7': dict(gzyms=19.6, kond=5, dach=('kop', 5.0, 2.2), tynk='a69a88', bonio=0.0, oc='a39787'),
    'Wybrzeze J. Slowackiego 8': dict(gzyms=19.6, kond=5, dach=('kop', 5.0, 2.2), tynk='a89c8a', bonio=0.0, oc='a39787'),
    'Wybrzeze J. Slowackiego 9': dict(gzyms=15.0, kond=4, dach=('plaski',), tynk='c4c0b6', bonio=0.0, oc='bcb8ae'),
    'Mazowiecka 17': dict(gzyms=16.8, kond=4, dach=('kop', 6.0, 6.2), tynk='dddbd3', bonio=0.0, oc='dcd9d0',
                          cokol=('piaskowiec', 4.6), m_dach='dachowka'),
    'i1': dict(gzyms=3.6, kond=1, dach=('plaski',), tynk='9b968c', bonio=0.0, okna=False),
    't1': dict(gzyms=3.4, kond=1, dach=('plaski',), tynk='9b968c', bonio=0.0, okna=False),
}


def _klucz_lod2(b):
    if b['nazwa']:
        return b['nazwa']
    return b['etykieta']


def budynek_lod2(ctx, g, b, wszystkie):
    rng = ctx.rng
    key = _klucz_lod2(b)
    prm = _LOD2.get(key, dict(gzyms=b.get('wysokosc_szac_m', 18.0) - 1.5, kond=b.get('kondygnacje_nadziemne', 5),
                              dach=('plaski',), tynk='b0aba0', bonio=0.0))
    poly = Polygon(b['pts']).buffer(0).simplify(0.35)
    ring = _ring_ccw(list(poly.exterior.coords)[:-1])
    zt = ctx.teren.z(np.array([p[0] for p in ring]), np.array([p[1] for p in ring]))
    zr = float(zt.mean())
    vb = float(zt.min() - zr) - 0.6
    H = prm['gzyms']
    T = 'tynk:%s:0.35:0' % prm['tynk']
    TB = 'tynk:%s:0.35:%s' % (prm['tynk'], prm['bonio']) if prm.get('bonio') else T
    TO = 'tynk:%s:0.45:0' % prm.get('oc', prm['tynk'])
    inne = [Polygon(x['pts']).buffer(0) for x in wszystkie if x is not b]
    fr = ctx.ramka.exterior
    n = len(ring)
    kond = prm['kond']
    hp = 4.3 if kond > 1 else H
    hk = (H - hp - 0.9) / max(kond - 1, 1)
    for i in range(n):
        p0, p1 = ring[i], ring[(i + 1) % n]
        R = Ramka(p0, p1, zr)
        if R.L < 0.3:
            continue
        mid = R.P(R.L / 2, 0, 0.45)
        wspolna = any(q.contains(Point(mid[0], mid[1])) for q in inne)
        ciecie = fr.distance(Point((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)) < 0.3
        if wspolna or ciecie or R.L < 3.0 or not prm.get('okna', True):
            R.quad(g, 0, R.L, vb, H, 0.0, TO)
            continue
        front = R.L > 12.0 and ('Mazowiecka' in key or 'Slowackiego' in key)
        strefy = [(vb, 0.7, 'kamien_cokol')]
        if prm.get('cokol'):
            strefy.append((0.7, prm['cokol'][1], prm['cokol'][0]))
            strefy.append((prm['cokol'][1], 99, T))
        else:
            strefy.append((0.7, hp, TB))
            strefy.append((hp, 99, T if front else TO))
        rozst = 2.75 if front else 3.0
        na = max(1, int((R.L - 1.6) / rozst) + 1)
        span = (na - 1) * rozst
        us = [R.L / 2 - span / 2 + k * rozst for k in range(na)]
        ot = []
        for u in us:
            if kond > 1:
                ot.append(Otwor(u, 1.2, 1.3, 3.4, d=0.24))
            for kk in range(kond - 1):
                v0 = hp + 0.5 + kk * hk + 0.85
                ot.append(Otwor(u, 1.2 if front else 1.1, v0, v0 + min(1.9, hk - 1.2), szpr='T', d=0.22))
        if front and kond > 1 and na > 2:   # brama/wejście w jednej osi
            j = na // 2 if 'Mazowiecka 17' in key else 0
            ot = [o for o in ot if not (abs((o.u0 + o.u1) / 2 - us[j]) < 0.1 and o.v0 < 3.5)]
            ot.append(Otwor(us[j], 1.6 if 'Mazowiecka 17' in key else 1.3, 0.1, 3.6, typ='drzwi', d=0.35))
        sciana(g, R, 0, R.L, vb, H, ot, strefy, rng)
        if front:
            R.profil(g, 0, R.L, hp, _gz(0.2, 0.45), T)
            R.profil(g, 0, R.L, H - 0.75, _gz(0.45, 0.75), T)
            for kk in range(kond - 1):
                R.profil(g, 0, R.L, hp + 0.5 + kk * hk + 0.75, _pas(0.05, 0.1), T)
        elif kond > 1:
            R.profil(g, 0, R.L, H - 0.45, _gz(0.25, 0.45), TO)
    d = prm['dach']
    if d[0] == 'plaski':
        inn = _inset_ring(ring, 0.3)
        _dach_plaski(g, ring, inn, zr + H - 0.3, zr + H + 0.5, 'papa', TO)
    else:
        _dach_kopertowy(g, ring, zr + H, d[1], d[2], prm.get('m_dach', 'dach_szary'), okap=0.1)
        if prm.get('m_dach') == 'dachowka':       # lukarny w połaci frontowej (M17 – zdjęcie F.17.B)
            for i in range(n):
                p0, p1 = ring[i], ring[(i + 1) % n]
                R = Ramka(p0, p1, zr + H)
                if R.L > 12 and not any(q.contains(Point(*R.P(R.L / 2, 0, 0.45)[:2])) for q in inne) \
                        and fr.distance(Point(*R.P(R.L / 2, 0, 0)[:2])) > 0.5:
                    for u in np.arange(2.5, R.L - 2.0, 3.2):
                        R.box(g, u - 0.6, u + 0.6, 0.6, 2.2, -1.6, -0.5, T)
                        R.box(g, u - 0.75, u + 0.75, 2.2, 2.4, -1.7, -0.35, 'dachowka')
                        R.quad(g, u - 0.4, u + 0.4, 0.8, 1.9, -0.49, 'szklo', float(rng.random()))
        R0 = Ramka(ring[0], ring[1], zr + H)
        for k in range(3):
            _komin(g, R0, R0.L * (0.25 + 0.25 * k), -d[1] - 0.5, zr + H + d[2] * 0.5, d[2] * 0.6 + 0.8)
    ctx.info['obiekty'][key] = 'LOD2, gzyms %.1f m n.p.m.' % (Z0 + zr + H)


def zbuduj_budynki(ctx):
    t0 = time.time()
    items = ctx.site['budynki']['items']
    if ctx.opts['sasiedzi']:
        coll = ctx.coll('K_sasiedzi')
        g = Geo()
        kamienica_maz19(ctx, g)
        g.obiekt('Mazowiecka_19_LOD3', ctx, coll)
        g = Geo()
        kamienica_ws5(ctx, g)
        g.obiekt('Wybrzeze_Slowackiego_5_LOD3', ctx, coll)
    if ctx.opts['budynki']:
        coll = ctx.coll('K_budynki')
        for b in items:
            if b['nazwa'] in ('Mazowiecka 19', 'Wybrzeze J. Slowackiego 5'):
                continue
            g = Geo()
            budynek_lod2(ctx, g, b, items)
            nm = (_klucz_lod2(b) or 'budynek').replace(' ', '_').replace('.', '')
            g.obiekt(nm + '_LOD2', ctx, coll)
    ctx.czas('budynki', t0)


# ============================================================================================== Most Grunwaldzki
class MostUklad:
    """Układ mostu: s wzdłuż osi (az. 70,4°), x w lewo (ku pn.-zach.), z bezwzględne (Z).
    Początek: środek między wewnętrznymi licami pylonów pd. (bloki GSSIPD e-mapy: (93,90; 136,58))."""
    O = np.array([93.90, 136.575])
    AZ = math.radians(70.4)
    L = 126.6            # rozstaw osi pylonów (literatura, historia.md)
    Z_POM = 2.50         # nawierzchnia przy pylonach (≈121,75 m n.p.m. – pkt e-mapy 121,66–121,77)
    X_PYL = 8.25         # wewnętrzne lico pylonu (16,50 m w świetle, M.11.F)

    def __init__(self):
        self.u = np.array([math.sin(self.AZ), math.cos(self.AZ)])
        self.vl = np.array([-self.u[1], self.u[0]])

    def W(self, s, x, z):
        p = self.O + s * self.u + x * self.vl
        return (float(p[0]), float(p[1]), float(z))

    def zpom(self, s):
        t = np.clip(s / self.L, 0, 1)
        return self.Z_POM + 1.0 * 4 * t * (1 - t)


def _pylon_noga(g, M, sg, s0, helmy=True):
    """Noga pylonu (sg=+1 lewa/pn.-zach., −1 prawa/pd.-wsch.). Profil wg przekroju D-D (M.11.F, 28,3 px/m):
    cokół 5,72×5,2 m do 3,6 m; trzon 5,5 m do 9,8 m; wklęsłe przejście do 3,57 m (14,2 m); wieża do 21,3 m;
    gzyms, latarnia z prześwitami 21,6–22,9 m, gzyms 23,5 m; hełm (ostrosłup ścięty) do 25,2 m, daszek 25,55 m,
    iglica do 26,2 m (wysokości nad chodnikiem)."""
    z0 = M.Z_POM
    lv = [(-6.0, 0, 5.72, 2.6), (3.6, 0, 5.72, 2.6), (3.6, 0, 5.86, 2.68), (3.85, 0, 5.86, 2.68), (3.85, 0, 5.5, 2.45),
          (9.8, 0, 5.5, 2.45)]
    for k in range(1, 7):
        t = k / 6
        lv.append((9.8 + 4.4 * t, 0, 3.57 + 1.93 * (1 - t) ** 2, 1.85 + 0.6 * (1 - t) ** 2))
    lv += [(21.3, 0, 3.57, 1.85), (21.3, -0.1, 3.67, 1.95), (21.65, -0.1, 3.67, 1.95), (21.65, 0, 3.57, 1.85),
           (22.9, 0, 3.57, 1.85), (22.9, -0.15, 3.72, 2.0), (23.5, -0.15, 3.72, 2.0)]
    if helmy:
        ac = 1.785
        for (z, w) in ((23.5, 3.62), (24.1, 3.30), (24.7, 2.75), (25.2, 2.2)):
            lv.append((z, ac - w / 2, ac + w / 2, w / 2 + 0.05))
    else:
        lv.append((23.6, 0.1, 3.47, 1.75))

    def P(a, b, z):
        return M.W(s0 + b, sg * (M.X_PYL + a), z0 + z)

    rings = []
    for (z, a0, a1, hb) in lv:
        rings.append([P(a0, -hb, z), P(a1, -hb, z), P(a1, hb, z), P(a0, hb, z)])
    m = 'granit_pylon'
    for r0, r1 in zip(rings[:-1], rings[1:]):
        for i in range(4):
            j = (i + 1) % 4
            q = [r0[i], r0[j], r1[j], r1[i]]
            c = np.mean(np.array(r0 + r1), axis=0)
            mq = np.mean(np.array(q), axis=0)
            nrm = mq - c
            nrm[2] = 0
            g.polyn(q, nrm, m)
    g.polyn(rings[0], (0, 0, -1), m)
    top = rings[-1]
    if helmy:
        ap = P(1.785, 0, 25.55)
        for i in range(4):
            j = (i + 1) % 4
            g.polyn([top[i], top[j], ap], np.mean([top[i], top[j]], axis=0) - np.array(P(1.785, 0, 25.2)), 'granit_jasny')
        c = P(1.785, 0, 25.5)
        g.belka(c, (c[0], c[1], c[2] + 0.75), 0.07, 0.07, 'stal_ciemna')
        g.belka((c[0], c[1], c[2] + 0.35), (c[0], c[1], c[2] + 0.5), 0.2, 0.2, 'stal_ciemna')
    else:
        g.polyn(top, (0, 0, 1), m)
    # nisza z łożyskiem łańcucha (ściany prostopadłe do osi), płaskorzeźba, prześwity latarni
    for sb in (-1, 1):
        hb = 1.85 * sb + 0.015 * sb

        def F(a, z):
            return P(a, hb, z)
        nrm = np.array(M.W(sb, 0, 0)) - np.array(M.W(0, 0, 0))
        pts = [F(0.335, 14.9), F(3.235, 14.9)]
        for k in range(9):
            th = math.pi * k / 8
            pts.append(F(1.785 + 1.45 * math.cos(th), 17.85 + 1.45 * math.sin(th)))
        g.polyn(pts, nrm, 'nisza')
        hb2 = (2.45 * sb) + 0.03 * sb
        q = [P(0.3, hb2, 4.2), P(3.2, hb2, 4.2), P(3.2, hb2, 8.6), P(0.3, hb2, 8.6)]
        g.polyn(q, nrm, 'granit_jasny')
        for a in (0.9, 1.785, 2.67):
            q = [P(a - 0.17, hb, 21.8), P(a + 0.17, hb, 21.8), P(a + 0.17, hb, 22.75), P(a - 0.17, hb, 22.75)]
            g.polyn(q, nrm, 'nisza')
    for (a, sa) in ((3.57 + 0.015, 1), (-0.015, -1)):
        for b in (-0.9, 0.0, 0.9):
            q = [P(a, b - 0.17, 21.8), P(a, b + 0.17, 21.8), P(a, b + 0.17, 22.75), P(a, b - 0.17, 22.75)]
            nrm = (np.array(M.W(0, sg * sa, 0)) - np.array(M.W(0, 0, 0)))
            g.polyn(q, nrm, 'nisza')
    # latarnia na wysięgniku (wewnętrzne lico, ~8,9 m – rysunek M.11.F)
    for b in (-1.2, 1.2):
        a0 = P(0.0, b, 8.9)
        a1 = P(-1.15, b, 8.9)
        g.belka(a0, a1, 0.08, 0.12, 'stal_ciemna')
        g.belka(P(-1.15, b, 8.9), P(-1.15, b, 8.5), 0.05, 0.05, 'stal_ciemna')
        g.belka(P(-1.15, b, 8.5), P(-1.15, b, 7.9), 0.3, 0.3, 'klosz')
        g.belka(P(-1.15, b, 8.5), P(-1.15, b, 8.62), 0.42, 0.42, 'stal_ciemna')


def _portal(g, M, s0):
    """Łuk portalu z belką i naczółkiem między nogami pylonu (grubość 2,4 m): wezgłowia 8,9 m, klucz 15,9 m,
    korona belki 19,5 m, naczółek do 21,3 m (nad chodnikiem), tablica z napisem 16,0–17,5 m."""
    z0 = M.Z_POM
    X = M.X_PYL
    zs, zk, zt = 8.9, 15.9, 19.5
    arc = [(X * math.cos(th), zs + (zk - zs) * math.sin(th)) for th in np.linspace(math.pi, 0, 25)]
    poly2 = arc + [(X, zt), (-X, zt)]
    m = 'granit_pylon'
    for sb in (-1.2, 1.2):
        V2, F = triangulacja(Polygon(poly2), None)
        nrm = np.array(M.W(sb, 0, 0)) - np.array(M.W(0, 0, 0))
        for f in F:
            pts = [M.W(s0 + sb, V2[i, 0], z0 + V2[i, 1]) for i in f]
            g.polyn(pts, nrm, m)
        # archiwolta (pierścień klińców) – lekko wysunięta
        arc2 = [(x * (1 + 0.9 / X), zs + (z - zs) * (1 + 0.9 / (zk - zs))) for (x, z) in arc]
        sd = sb + 0.06 * np.sign(sb)
        for (a, b), (c, d) in zip(zip(arc[:-1], arc[1:]), zip(arc2[:-1], arc2[1:])):
            q = [M.W(s0 + sd, a[0], z0 + a[1]), M.W(s0 + sd, b[0], z0 + b[1]), M.W(s0 + sd, d[0], z0 + d[1]),
                 M.W(s0 + sd, c[0], z0 + c[1])]
            g.polyn(q, nrm, 'granit_jasny')
        # tablica z napisem, fryz z otworami
        ds = sb + 0.05 * np.sign(sb)
        g.polyn([M.W(s0 + ds, -3.0, z0 + 16.0), M.W(s0 + ds, 3.0, z0 + 16.0), M.W(s0 + ds, 3.0, z0 + 17.5),
                 M.W(s0 + ds, -3.0, z0 + 17.5)], nrm, 'granit_jasny')
        for xx in (-7.0, -5.6, -4.2, 4.2, 5.6, 7.0):
            g.polyn([M.W(s0 + ds, xx - 0.35, z0 + 18.0), M.W(s0 + ds, xx + 0.35, z0 + 18.0),
                     M.W(s0 + ds, xx + 0.35, z0 + 18.45), M.W(s0 + ds, xx - 0.35, z0 + 18.45)], nrm, 'nisza')
    for (a, b) in zip(arc[:-1], arc[1:]):
        q = [M.W(s0 - 1.2, a[0], z0 + a[1]), M.W(s0 + 1.2, a[0], z0 + a[1]), M.W(s0 + 1.2, b[0], z0 + b[1]),
             M.W(s0 - 1.2, b[0], z0 + b[1])]
        mx = (a[0] + b[0]) / 2
        mz = (a[1] + b[1]) / 2
        cen = np.array(M.W(s0, 0, z0 + zs))
        g.polyn(q, cen - np.array(M.W(s0, mx, z0 + mz)), m)
    g.polyn([M.W(s0 - 1.2, -X, z0 + zt), M.W(s0 + 1.2, -X, z0 + zt), M.W(s0 + 1.2, X, z0 + zt),
             M.W(s0 - 1.2, X, z0 + zt)], (0, 0, 1), m)
    # gzyms koronujący belkę
    for sb in (-1, 1):
        g.belka(M.W(s0 + sb * 1.25, -X, z0 + 19.35), M.W(s0 + sb * 1.25, X, z0 + 19.35), 0.3, 0.32, 'granit_jasny')
    # naczółek
    tri = [(-2.83, zt), (2.83, zt), (0.0, 21.3)]
    for sb in (-1.0, 1.0):
        nrm = np.array(M.W(sb, 0, 0)) - np.array(M.W(0, 0, 0))
        g.polyn([M.W(s0 + sb, x, z0 + z) for (x, z) in tri], nrm, m)
    for (a, b) in ((tri[0], tri[2]), (tri[2], tri[1])):
        q = [M.W(s0 - 1.0, a[0], z0 + a[1]), M.W(s0 + 1.0, a[0], z0 + a[1]), M.W(s0 + 1.0, b[0], z0 + b[1]),
             M.W(s0 - 1.0, b[0], z0 + b[1])]
        g.polyn(q, (0, 0, 1), 'granit_jasny')
    g.belka(M.W(s0, -0.7, z0 + zt + 0.55), M.W(s0, 0.7, z0 + zt + 0.55), 1.1, 1.1, 'granit_jasny', up=(0, 0, 1))


def zbuduj_most(ctx):
    t0 = time.time()
    coll = ctx.coll('K_most')
    M = MostUklad()
    helmy = ctx.opts['helmy']
    # portal pd. w układzie świata; portal pn. – ta sama siatka obrócona o 180° wokół środka przęsła
    g = Geo()
    for sg in (1, -1):
        _pylon_noga(g, M, sg, 0.0, helmy)
    _portal(g, M, 0.0)
    ob = g.obiekt('most_portal_pd', ctx, coll)
    ob2 = bpy.data.objects.new('most_portal_pn', ob.data)
    coll.objects.link(ob2)
    c = np.array(M.W(M.L / 2, 0, 0))
    ob2.matrix_world = (Matrix.Translation((c[0], c[1], 0)) @ Matrix.Rotation(math.pi, 4, 'Z')
                        @ Matrix.Translation((-c[0], -c[1], 0)))
    # pomost
    g = Geo()
    ss = np.linspace(2.6, M.L - 2.6, 48)
    for a, b in zip(ss[:-1], ss[1:]):
        za, zb = M.zpom(a), M.zpom(b)
        for (x0, x1, dz, mm) in ((-6.05, 6.05, 0.0, 'asfalt'), (6.05, 8.25, 0.15, 'plyty_bet'),
                                 (-8.25, -6.05, 0.15, 'plyty_bet'), (8.25, 9.9, 0.15, 'stal_most'),
                                 (-9.9, -8.25, 0.15, 'stal_most')):
            g.polyn([M.W(a, x0, za + dz), M.W(b, x0, zb + dz), M.W(b, x1, zb + dz), M.W(a, x1, za + dz)], (0, 0, 1), mm)
        for (x, sgn) in ((6.05, -1), (-6.05, 1)):
            g.polyn([M.W(a, x, za), M.W(b, x, zb), M.W(b, x, zb + 0.15), M.W(a, x, za + 0.15)],
                    np.array(M.W(0, sgn, 0)) - np.array(M.W(0, 0, 0)), 'granit')
        for sx in (-1, 1):
            g.polyn([M.W(a, 9.9 * sx, za + 0.15), M.W(b, 9.9 * sx, zb + 0.15), M.W(b, 9.9 * sx, zb - 1.3),
                     M.W(a, 9.9 * sx, za - 1.3)], np.array(M.W(0, sx, 0)) - np.array(M.W(0, 0, 0)), 'stal_most')
        g.polyn([M.W(a, -9.9, za - 1.3), M.W(b, -9.9, zb - 1.3), M.W(b, 9.9, zb - 1.3), M.W(a, 9.9, za - 1.3)],
                (0, 0, -1), 'stal_most')
        for xr in (-1.28 - 0.7175, -1.28 + 0.7175, 1.28 - 0.7175, 1.28 + 0.7175):
            g.belka(M.W(a, xr, za + 0.012), M.W(b, xr, zb + 0.012), 0.07, 0.03, 'szyny')
    # kratownice usztywniające (płaszczyzny x = ±9,6) – pas górny +2,3 m, dolny −0,3 m, krzyżulce co 4,85 m
    XT = 9.6
    sk = np.arange(2.6, M.L - 2.5, 4.85)
    for sx in (-1, 1):
        x = sx * XT
        for a, b in zip(sk[:-1], sk[1:]):
            za, zb = M.zpom(a), M.zpom(b)
            g.belka(M.W(a, x, za + 2.3), M.W(b, x, zb + 2.3), 0.35, 0.4, 'stal_most')
            g.belka(M.W(a, x, za - 0.3), M.W(b, x, zb - 0.3), 0.35, 0.4, 'stal_most')
            g.belka(M.W(a, x, za - 0.3), M.W(b, x, zb + 2.3), 0.22, 0.22, 'stal_most')
            g.belka(M.W(a, x, za + 2.3), M.W(b, x, zb - 0.3), 0.15, 0.15, 'stal_most')
        for a in sk:
            za = M.zpom(a)
            g.belka(M.W(a, x, za - 0.3), M.W(a, x, za + 2.3), 0.25, 0.25, 'stal_most')
    # łańcuchy (pasma nośne): siodło 19,6 m (nisza pylonu), zwis do 0,5 m nad pasem górnym w środku przęsła
    zs = M.Z_POM + 17.1
    zmid = M.zpom(M.L / 2) + 2.3 + 0.55
    f = zs - zmid
    sc = np.linspace(0, M.L, 61)
    zc = zs - f * 4 * (sc / M.L) * (1 - sc / M.L)
    for sx in (-1, 1):
        x = sx * XT
        for i in range(len(sc) - 1):
            g.belka(M.W(sc[i], x, zc[i]), M.W(sc[i + 1], x, zc[i + 1]), 0.55, 0.85, 'stal_most')
        # wieszaki
        for a in sk[1:-1]:
            zca = zs - f * 4 * (a / M.L) * (1 - a / M.L)
            g.belka(M.W(a, x, zca - 0.4), M.W(a, x, M.zpom(a) + 2.5), 0.08, 0.08, 'stal_most')
        # odciągi do bloków kotwiących (GSSIPD: ok. 19 m za osią pylonu)
        for (s_p, s_a) in ((0.0, -19.0), (M.L, M.L + 19.0)):
            za = ctx.teren.z1(*M.W(s_a, sx * 10.2, 0)[:2]) + 0.6 if s_p == 0 else M.Z_POM + 0.3
            g.belka(M.W(s_p, x, zs), M.W(s_a, sx * 10.2, za), 0.55, 0.85, 'stal_most')
            g.belka(M.W(s_a - 1.0, sx * 10.2, za - 0.8), M.W(s_a + 1.2, sx * 10.2, za + 0.8), 1.1, 1.2, 'stal_most')
    # przyczółki (mur od strony rzeki pod pomostem)
    ua = (float(M.u[0]), float(M.u[1]), 0.0)
    for (s_a, s_b) in ((2.6, 5.5), (M.L - 5.5, M.L - 2.6)):
        sm_ = (s_a + s_b) / 2
        g.belka(M.W(sm_, -10.0, M.Z_POM - 0.8), M.W(sm_, 10.0, M.Z_POM - 0.8), s_b - s_a, 1.4, 'granit_pylon')
        g.belka(M.W(sm_, 0, ctx.z_woda - 2.0), M.W(sm_, 0, M.Z_POM - 1.4), 21.0, s_b - s_a + 2.0, 'mur_nabrzeza', up=ua)
    # bloki kotwiące – obrysy GSSIPD (granitowe postumenty)
    W = ctx.site['warstwy_emapy_surowe']['warstwy']
    for o in W['GSSIPD']['obiekty']:
        if 'pts' in o and o.get('z') == 1 and len(o['pts']) == 6:
            _pryzma_drapowana(ctx, g, Polygon(o['pts']).buffer(0), -0.3, 0.9, 'granit_pylon')
    g.obiekt('most_pomost_lancuchy', ctx, coll)
    ctx.info['obiekty']['Most Grunwaldzki'] = 'portal z hełmami' if helmy else 'portal bez hełmów (stan obecny)'
    ctx.czas('most', t0)


# ============================================================================================== zieleń
def _prototypy(ctx):
    if hasattr(ctx, '_proto'):
        return ctx._proto
    pora = ctx.opts['pora_roku']
    kora = drzewa.mat_kora('K_kora')
    lis = drzewa.mat_liscie('K_liscie_' + pora, pora)
    igl = drzewa.mat_liscie('K_igly', pora, iglaste=True)
    gest = ctx.opts['gestosc_lisci'] * (0.85 if pora == 'jesien' else 1.0)
    P = {}
    for nm, typ, seeds in (('duze', 'lisc_duze', (11, 12)), ('srednie', 'lisc_srednie', (21, 22, 23)),
                           ('male', 'lisc_male', (31, 32)), ('topola', 'topola', (41,)), ('iglaste', 'iglaste', (51, 52)),
                           ('krzew', 'krzew', (61, 62))):
        P[nm] = []
        for sd in seeds:
            c, d = drzewa.utworz_prototyp('%s_%d' % (nm, sd), typ, sd, kora, igl if typ == 'iglaste' else lis, gest)
            P[nm].append((c, d))
    ctx._proto = P
    return P


def _instancja(coll, proto, loc, rot, skala, name):
    e = bpy.data.objects.new(name, None)
    e.instance_type = 'COLLECTION'
    e.instance_collection = proto
    e.location = loc
    e.rotation_euler = (0.0, 0.0, rot)
    e.scale = (skala, skala, skala)
    coll.objects.link(e)
    return e


def zbuduj_zielen(ctx):
    t0 = time.time()
    coll = ctx.coll('K_zielen')
    P = _prototypy(ctx)
    rng = ctx.rng
    pusty = ctx.opts['obszar_inwestycji'] == 'pusty'
    Z = ctx.site['zielen']
    # drzewa z pomiaru (numery z dwoma punktami → jedno drzewo)
    drz = {}
    for t in Z['drzewa']:
        drz.setdefault(t['nr'], []).append(t)
    n = 0
    pozycje = []
    for nr, ts in drz.items():
        e = float(np.mean([t['e'] for t in ts]))
        nn = float(np.mean([t['n'] for t in ts]))
        t = ts[0]
        if pusty and (t['w_obszarze_inwestycji'] or ctx.inwest.contains(Point(e, nn))):
            continue
        h = zlib.crc32(nr.encode()) % 1000 / 1000.0
        if nr in ('E07', 'E12'):
            typ, sk = 'topola', 1.0 + 0.1 * h
        elif t['typ'] == 'iglaste':
            typ, sk = 'iglaste', 0.75 + 0.35 * h
        elif nr.startswith('E'):
            typ, sk = ('duze' if h > 0.45 else 'srednie'), 0.85 + 0.3 * h
        else:
            typ, sk = ('srednie' if h > 0.35 else 'duze'), 0.7 + 0.35 * h
        pr = P[typ][int(h * 97) % len(P[typ])][0]
        z = ctx.teren.z1(e, nn)
        _instancja(coll, pr, (e, nn, z), rng.uniform(0, 6.28), sk, 'drzewo_' + nr)
        pozycje.append((e, nn))
        n += 1
    # szpaler młodych drzew wzdłuż bulwaru (Wybrzeże Słowackiego, strona rzeki; zdjęcia F.17.A, ortofoto 03)
    mur, ws, gs = _brzeg(ctx.site)
    linia = LineString([(126.5, 74.0), (130.0, 60.0), (133.5, 45.0), (134.6, 33.0)] +
                       [(x - 1.8, y) for (x, y) in gs[1:]])
    kd = cKDTree(np.array(pozycje)) if pozycje else None
    for d in np.arange(2.0, linia.length, 8.0):
        p = linia.interpolate(d + rng.uniform(-0.6, 0.6))
        if kd is not None and kd.query([p.x, p.y])[0] < 4.5:
            continue
        if not ctx.ramka.contains(p):
            continue
        pr = P['male'][int(d) % len(P['male'])][0]
        _instancja(coll, pr, (p.x, p.y, ctx.teren.z1(p.x, p.y)), rng.uniform(0, 6.28), rng.uniform(0.9, 1.25),
                   'szpaler_%d' % int(d))
        n += 1
    # krzewy: zakrzewienia (obrysy pomiaru) – wypełnienie co ~1,7 m
    nk = 0
    for zk in Z['zakrzaczenia']:
        if len(zk['pts']) < 4:
            continue
        Pz = Polygon(zk['pts']).buffer(0)
        if Pz.area < 2.0:
            continue
        if pusty and ctx.inwest.buffer(0.5).contains(Pz.representative_point()):
            continue
        x0, y0, x1, y1 = Pz.bounds
        for x in np.arange(x0, x1, 1.7):
            for y in np.arange(y0, y1, 1.7):
                q = Point(x + rng.uniform(-0.6, 0.6), y + rng.uniform(-0.6, 0.6))
                if Pz.contains(q):
                    pr = P['krzew'][nk % 2][0]
                    _instancja(coll, pr, (q.x, q.y, ctx.teren.z1(q.x, q.y)), rng.uniform(0, 6.28),
                               rng.uniform(0.8, 1.3), 'krzew_%d' % nk)
                    nk += 1
    ctx.info['drzewa_w_ramce'] = n
    ctx.info['krzewy'] = nk
    ctx.czas('zielen', t0)


# ============================================================================================== ulica
def _latarnia_proto(ctx):
    g = Geo()
    # słup stożkowy 8 m, wysięgnik 1,4 m, oprawa
    k = 8
    for i in range(k):
        a0, a1 = 2 * math.pi * i / k, 2 * math.pi * (i + 1) / k
        r0, r1 = 0.085, 0.05
        g.add([(r0 * math.cos(a0), r0 * math.sin(a0), -0.3), (r0 * math.cos(a1), r0 * math.sin(a1), -0.3),
               (r1 * math.cos(a1), r1 * math.sin(a1), 8.0), (r1 * math.cos(a0), r1 * math.sin(a0), 8.0)],
              [(0, 1, 2, 3)], 'stal_ocynk')
    g.belka((0, 0, 7.9), (1.4, 0, 8.15), 0.06, 0.06, 'stal_ocynk')
    g.belka((1.1, 0, 8.12), (1.75, 0, 8.18), 0.28, 0.12, 'stal_ciemna')
    g.belka((1.15, 0, 8.04), (1.7, 0, 8.1), 0.22, 0.03, 'klosz')
    g.belka((0, 0, -0.3), (0, 0, 0.5), 0.22, 0.22, 'stal_ocynk')
    me = blib.mesh_from_arrays('latarnia_proto', g.V, g.F, [0] * len(g.F), [], None)
    keys = []
    for kk in g.M:
        if kk not in keys:
            keys.append(kk)
    me.data.polygons.foreach_set('material_index', [keys.index(kk) for kk in g.M])
    for kk in keys:
        me.data.materials.append(ctx.mat(kk))
    return me.data


def zbuduj_ulice(ctx):
    t0 = time.time()
    coll = ctx.coll('K_ulica')
    W = ctx.site['warstwy_emapy_surowe']['warstwy']
    U = ctx.site['ulice_i_sytuacja']
    pusty = ctx.opts['obszar_inwestycji'] == 'pusty'
    bud = unary_union(ctx.budynki_poly)
    jezd = ctx.jezdnie_poly if ctx.jezdnie_poly is not None else Polygon()
    M = MostUklad()
    pylony = [Point(*M.W(0, sg * 11.15, 0)[:2]).buffer(4.5) for sg in (1, -1)]
    # latarnie (GUPELA e-mapy + pomiar), bez duplikatów
    pts = [tuple(o['p']) for o in W['GUPELA']['obiekty'] if 'p' in o] + \
          [tuple(o['p']) for o in W['latarnie']['obiekty'] if 'p' in o]
    uniq = []
    for p in pts:
        if all(math.dist(p, q) > 1.5 for q in uniq):
            uniq.append(p)
    lp = _latarnia_proto(ctx)
    nl = 0
    for p in uniq:
        pt = Point(p)
        if not ctx.ramka.contains(pt) or bud.contains(pt) or (ctx.woda_poly and ctx.woda_poly.contains(pt)):
            continue
        if any(pl.contains(pt) for pl in pylony) or jezd.contains(pt):
            continue
        q = jezd.exterior.interpolate(jezd.exterior.project(pt)) if jezd.geom_type == 'Polygon' else None
        if jezd.geom_type == 'MultiPolygon':
            best = min(jezd.geoms, key=lambda gg: gg.distance(pt))
            q = best.exterior.interpolate(best.exterior.project(pt))
        rot = math.atan2(q.y - p[1], q.x - p[0]) if q is not None else 0.0
        ob = bpy.data.objects.new('latarnia_%d' % nl, lp)
        ob.location = (p[0], p[1], ctx.teren.z1(*p) + 0.05)
        ob.rotation_euler = (0, 0, rot)
        coll.objects.link(ob)
        nl += 1
    g = Geo()
    # słupki stalowe wzdłuż linii słupków (pomiar)
    ns = 0
    for o in U['slupki']:
        L = LineString(o['pts'])
        for d in np.arange(0.0, L.length + 0.01, 1.4):
            p = L.interpolate(d)
            z = ctx.teren.z1(p.x, p.y) + 0.06
            g.belka((p.x, p.y, z - 0.2), (p.x, p.y, z + 0.85), 0.08, 0.08, 'stal_ciemna')
            ns += 1
    # ogrodzenia (siatka na słupkach 1,5 m)
    for o in U['ogrodzenia']:
        pts_ = o['pts']
        if len(pts_) < 2:
            continue
        L = LineString(pts_)
        if pusty and ctx.inwest.buffer(-0.3).intersection(L).length > 0.5 * L.length:
            continue
        L = shapely.segmentize(L, 2.5)
        cs = list(L.coords)
        zz = ctx.teren.z(np.array([c[0] for c in cs]), np.array([c[1] for c in cs]))
        for (a, za), (b, zb) in zip(zip(cs[:-1], zz[:-1]), zip(cs[1:], zz[1:])):
            g.belka((a[0], a[1], za - 0.2), (a[0], a[1], za + 1.55), 0.06, 0.06, 'stal_ciemna')
            g.belka((a[0], a[1], za + 1.5), (b[0], b[1], zb + 1.5), 0.04, 0.04, 'stal_ciemna')
            d = np.array([b[0] - a[0], b[1] - a[1], 0.0])
            nrm = np.array([-d[1], d[0], 0.0])
            g.polyn([(a[0], a[1], za + 0.05), (b[0], b[1], zb + 0.05), (b[0], b[1], zb + 1.5), (a[0], a[1], za + 1.5)],
                    nrm, 'siatka')
        g.belka((cs[-1][0], cs[-1][1], zz[-1] - 0.2), (cs[-1][0], cs[-1][1], zz[-1] + 1.55), 0.06, 0.06, 'stal_ciemna')
    # szyny tramwajowe (osie GSLTTK) + sieć trakcyjna
    for o in U['tory_tramwajowe']:
        L = shapely.segmentize(LineString(o['pts']), 2.0)
        for off in (-0.7175, 0.7175):
            Lo = L.offset_curve(off)
            cs = list(Lo.coords)
            zz = ctx.teren.z(np.array([c[0] for c in cs]), np.array([c[1] for c in cs])) - 0.035
            for (a, za), (b, zb) in zip(zip(cs[:-1], zz[:-1]), zip(cs[1:], zz[1:])):
                g.belka((a[0], a[1], za), (b[0], b[1], zb), 0.07, 0.03, 'szyny')
        cs = list(L.coords)
        zz = ctx.teren.z(np.array([c[0] for c in cs]), np.array([c[1] for c in cs]))
        for (a, za), (b, zb) in zip(zip(cs[:-1], zz[:-1]), zip(cs[1:], zz[1:])):
            g.belka((a[0], a[1], za + 5.6), (b[0], b[1], zb + 5.6), 0.015, 0.015, 'stal_ciemna')
    tory = [LineString(o['pts']) for o in U['tory_tramwajowe']]
    if len(tory) == 2:
        sr = tory[0]
        for d in np.arange(5.0, sr.length - 1.0, 32.0):
            p = sr.interpolate(d)
            q = tory[1].interpolate(tory[1].project(p))
            mpt = np.array([(p.x + q.x) / 2, (p.y + q.y) / 2])
            nd = np.array([q.x - p.x, q.y - p.y])
            sp = float(np.linalg.norm(nd))
            if sp < 1.0 or sp > 6.0:
                continue
            nd /= sp
            for sgn in (-1, 1):
                base = mpt + nd * sgn * (sp / 2 + 2.9)
                if not ctx.ramka.contains(Point(*base)) or bud.contains(Point(*base)):
                    continue
                z = ctx.teren.z1(*base)
                g.belka((base[0], base[1], z - 0.3), (base[0], base[1], z + 7.4), 0.2, 0.2, 'stal_ciemna')
                end = mpt - nd * sgn * (sp / 2)
                g.belka((base[0], base[1], z + 6.6), (end[0], end[1], z + 6.3), 0.07, 0.07, 'stal_ciemna')
    # oznakowanie poziome: przejście dla pieszych przez Mazowiecką przy skwerze (zdjęcie M.09 360_45m)
    for (c, az, Lp) in (((59.3, 89.5), 101.0, 12.0),):
        _zebra(ctx, g, c, az, Lp, jezd)
    g.obiekt('mala_architektura', ctx, coll)
    ctx.info['latarnie'] = nl
    ctx.info['slupki'] = ns
    ctx.czas('ulica', t0)


def _zebra(ctx, g, c, az, L, jezd, w=4.0):
    """Pasy przejścia: kierunek przejścia az [°]; pasy 0,5 m co 1,0 m, przycięte do jezdni."""
    a = math.radians(az)
    d = np.array([math.sin(a), math.cos(a)])
    nrm = np.array([-d[1], d[0]])
    for k in np.arange(-L / 2, L / 2, 1.0):
        p0 = np.array(c) + d * k
        rect = Polygon([p0 - nrm * w / 2, p0 + d * 0.5 - nrm * w / 2, p0 + d * 0.5 + nrm * w / 2, p0 + nrm * w / 2])
        s = rect.intersection(jezd.buffer(-0.3))
        for part in _poly_parts(s):
            V2, F = triangulacja(part, None)
            if len(F):
                z = ctx.teren.z(V2[:, 0], V2[:, 1]) - 0.05 + 0.012
                g.add([(V2[i, 0], V2[i, 1], z[i]) for i in range(len(V2))], [tuple(f) for f in F], 'farba_biala')


# ============================================================================================== dalsze otoczenie
def _orto_px(e, n):
    s, th, tx, ty = ORTO_GEOREF['px_na_m'], ORTO_GEOREF['rot_rad'], ORTO_GEOREF['tx'], ORTO_GEOREF['ty']
    c, sn = math.cos(th), math.sin(th)
    x = s * (c * e - sn * n) + tx
    y = -s * (sn * e + c * n) + ty
    return x, y


def _orto_local(x, y):
    s, th, tx, ty = ORTO_GEOREF['px_na_m'], ORTO_GEOREF['rot_rad'], ORTO_GEOREF['tx'], ORTO_GEOREF['ty']
    a = (np.asarray(x) - tx) / s
    b = -(np.asarray(y) - ty) / s
    c, sn = math.cos(th), math.sin(th)
    return c * a + sn * b, -sn * a + c * b


def przygotuj_ortofoto(ctx):
    """Usunięcie niebieskich linii ewidencyjnych z ortofotomapy (wypełnienie najbliższym pikselem + rozmycie),
    maska wody (ciemne, mało nasycone, duże spójne obszary) i maska koron drzew. Wyniki w cache."""
    from PIL import Image
    from scipy import ndimage
    tex = ctx.cache / 'orto01B_czysta.jpg'
    mw = ctx.cache / 'orto01B_woda.npy'
    md = ctx.cache / 'orto01B_drzewa.npy'
    if tex.exists() and mw.exists() and md.exists():
        return tex, np.load(mw), np.load(md)
    im = np.asarray(Image.open(ORTO_PLIK).convert('RGB')).astype(np.float32)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    linie = (B > R + 30) & (B > G + 3) & (B > 110)
    linie = ndimage.binary_dilation(linie, iterations=1)
    _, ind = ndimage.distance_transform_edt(linie, return_indices=True)
    out = im[ind[0], ind[1]]
    bl = np.stack([ndimage.uniform_filter(out[..., k], 3) for k in range(3)], -1)
    out[linie] = bl[linie]
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(tex, quality=92)
    R, G, B = out[..., 0], out[..., 1], out[..., 2]
    lum = 0.3 * R + 0.59 * G + 0.11 * B
    mx = np.max(out, -1)
    mn = np.min(out, -1)
    sat = (mx - mn) / np.maximum(mx, 1)
    woda = (lum < 72) & (sat < 0.42)
    woda = ndimage.binary_opening(woda, iterations=2)
    woda = ndimage.binary_closing(woda, iterations=3)
    lab, nlab = ndimage.label(woda)
    sizes = ndimage.sum(woda, lab, range(1, nlab + 1))
    keep = np.zeros(nlab + 1, bool)
    keep[1:] = sizes > 6000
    woda = keep[lab]
    # zalanie małych dziur (łodzie, barki, cienie mostów) – bez wysp
    dz = ndimage.binary_fill_holes(woda) & ~woda
    lab2, n2 = ndimage.label(dz)
    if n2:
        s2 = ndimage.sum(dz, lab2, range(1, n2 + 1))
        small = np.zeros(n2 + 1, bool)
        small[1:] = s2 < 900
        woda = woda | small[lab2]
    exg = 2 * G - R - B
    std = ndimage.generic_filter(lum, np.std, size=5) if False else np.sqrt(np.maximum(
        ndimage.uniform_filter(lum ** 2, 5) - ndimage.uniform_filter(lum, 5) ** 2, 0))
    drz = (exg > 18) & (lum < 112) & (std > 9.0) & ~woda
    drz = ndimage.binary_opening(drz, iterations=1)
    np.save(mw, woda)
    np.save(md, drz)
    return tex, woda, drz


def zbuduj_dalsze(ctx):
    t0 = time.time()
    coll = ctx.coll('K_dalsze')
    tex, woda_m, drz_m = przygotuj_ortofoto(ctx)
    ctx.orto_tex = tex
    import contourpy
    from scipy import ndimage
    H, Wd = woda_m.shape
    # kontury wody (piksele → układ lokalny)
    sm = ndimage.gaussian_filter(woda_m.astype(np.float32), 1.2)
    cg = contourpy.contour_generator(z=sm, line_type='SeparateCode' if False else 'Separate')
    polys = []
    for ln in cg.lines(0.5):
        if len(ln) < 8:
            continue
        e, n = _orto_local(ln[:, 0], ln[:, 1])
        P = Polygon(np.c_[e, n]).buffer(0)
        if P.area > 500:
            polys.append(P.simplify(0.8))
    woda_d = unary_union(polys) if polys else Polygon()
    # zasięg dalszego terenu (prostokąt w obrębie ortofotomapy)
    cx, cy = _orto_local(np.array([2.0, Wd - 2.0, Wd - 2.0, 2.0]), np.array([2.0, 2.0, H - 2.0, H - 2.0]))
    ex = Polygon(np.c_[cx, cy])
    woda_d = woda_d.intersection(ex)
    # w ramce obowiązuje geometria z e-mapy
    rk = ctx.ramka
    woda_d = woda_d.difference(rk).union(ctx.woda_poly if ctx.woda_poly is not None else Polygon())
    lad = ex.difference(woda_d).difference(rk)
    ctx.woda_dalsza = woda_d
    if ctx.opts['ortofoto']:
        V2, F = triangulacja(lad, 12.0)
        z = ctx.teren.z(V2[:, 0], V2[:, 1]) - 0.03
        V = np.c_[V2, z]
        ob = blib.mesh_from_arrays('teren_dalszy_ortofoto', V, F, mats=[ctx.mat('ortofoto')], coll=coll)
        px, py = _orto_px(V2[:, 0], V2[:, 1])
        uv = np.c_[px / Wd, 1.0 - py / H]
        me = ob.data
        uvl = me.uv_layers.new(name='UVMap')
        loops_v = np.zeros(len(me.loops), np.int32)
        me.loops.foreach_get('vertex_index', loops_v)
        uvl.data.foreach_set('uv', uv[loops_v].astype(np.float32).ravel())
        # brzegi wody poza ramką – pionowe skarpy/mury od terenu do dna
        g = Geo()
        for P in _poly_parts(woda_d.difference(rk.buffer(0.5))):
            for ring in [P.exterior] + list(P.interiors):
                cs = list(shapely.segmentize(ring, 4.0).coords)
                e = np.array([c[0] for c in cs])
                n = np.array([c[1] for c in cs])
                zz = ctx.teren.z(e, n) - 0.03
                for i in range(len(cs) - 1):
                    a, b = cs[i], cs[i + 1]
                    if rk.buffer(0.2).contains(Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)):
                        continue
                    mid = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                    d = np.array([b[0] - a[0], b[1] - a[1], 0.0])
                    nrm = np.array([-d[1], d[0], 0.0])
                    test = Point(mid.x + nrm[0] * 0.05, mid.y + nrm[1] * 0.05)
                    if not P.contains(test):
                        nrm = -nrm
                    g.polyn([(a[0], a[1], ctx.z_woda - 2.0), (b[0], b[1], ctx.z_woda - 2.0), (b[0], b[1], zz[i + 1]),
                             (a[0], a[1], zz[i])], nrm, 'mur_nabrzeza')
        g.obiekt('brzegi_dalsze', ctx, coll)
        # teren poza ortofotomapą (do horyzontu, z perspektywą powietrzną)
        outer = sbox(-6000, -6000, 6000, 6000).difference(ex)
        V2, F = triangulacja(outer, None)
        blib.mesh_from_arrays('teren_poza_ortofoto', np.c_[V2, np.full(len(V2), 0.0)], F,
                              mats=[ctx.mat('teren_daleki')], coll=coll)
    if ctx.opts['dalsze_bryly']:
        g = Geo()
        nb = 0
        for (nm, pts, h, kol, m_dach) in BRYLY_DALSZE:
            P = Polygon(pts).buffer(0)
            if P.intersects(rk.buffer(-0.5)):
                P = P.difference(rk)
            for part in _poly_parts(P):
                ring = _ring_ccw(list(part.exterior.coords)[:-1])
                e = np.array([p[0] for p in ring])
                n = np.array([p[1] for p in ring])
                z = ctx.teren.z(e, n)
                zb, zt = float(z.min()) - 0.5, float(z.mean()) + h
                m = 'bryla_dalsza:%s' % kol
                k = len(ring)
                for i in range(k):
                    j = (i + 1) % k
                    g.add([(e[i], n[i], zb), (e[j], n[j], zb), (e[j], n[j], zt), (e[i], n[i], zt)], [(0, 1, 2, 3)], m)
                V2, F = triangulacja(part, None)
                g.add([(V2[i, 0], V2[i, 1], zt) for i in range(len(V2))], [tuple(f) for f in F], m_dach)
                nb += 1
        g.obiekt('bryly_dalsze', ctx, coll)
        ctx.info['bryly_dalsze'] = nb
    if ctx.opts['dalsze_drzewa']:
        P = _prototypy(ctx)
        rng = np.random.default_rng(ctx.opts['seed'] + 5)
        # próbkowanie maski koron w siatce ~6,5 m, w promieniu 430 m od działki
        E, N = np.meshgrid(np.arange(-380.0, 520.0, 7.5), np.arange(-380.0, 480.0, 7.5))
        E = E.ravel() + rng.uniform(-2.5, 2.5, E.size)
        N = N.ravel() + rng.uniform(-2.5, 2.5, N.size)
        ok = np.hypot(E - 85, N - 40) < 430
        x0, y0, x1, y1 = rk.bounds
        ok &= ~((E > x0 - 2) & (E < x1 + 2) & (N > y0 - 2) & (N < y1 + 2))
        X, Y = _orto_px(E, N)
        Xi, Yi = np.round(X).astype(int), np.round(Y).astype(int)
        ok &= (Xi >= 0) & (Xi < Wd) & (Yi >= 0) & (Yi < H)
        ok[ok] &= drz_m[Yi[ok], Xi[ok]]
        bryly = unary_union([Polygon(b[1]).buffer(1.0) for b in BRYLY_DALSZE]) if BRYLY_DALSZE else Polygon()
        if not woda_d.is_empty:
            ok[ok] &= ~shapely.contains_xy(woda_d, E[ok], N[ok])
        if not bryly.is_empty:
            ok[ok] &= ~shapely.contains_xy(bryly, E[ok], N[ok])
        E, N = E[ok], N[ok]
        Zs = ctx.teren.z(E, N)
        nd = 0
        for ee, nn, zz in zip(E, N, Zs):
            r = rng.random()
            typ = 'duze' if r < 0.35 else ('srednie' if r < 0.85 else 'iglaste')
            pr = P[typ][int(r * 100) % len(P[typ])][0]
            _instancja(coll, pr, (float(ee), float(nn), float(zz)), rng.uniform(0, 6.28), rng.uniform(0.75, 1.15),
                       'drzewo_d_%d' % nd)
            nd += 1
        ctx.info['drzewa_dalsze'] = nd
    ctx.czas('dalsze', t0)


# Bryły dalszego otoczenia (poza ramką mapy): obrysy przybliżone z ortofotomapy M.11.A (01 B, po georeferencji),
# dokładność ok. ±2–3 m; wysokości [m] szacowane z liczby kondygnacji na zdjęciach F.17/M.09/M.10 i modelu SIP
# (M.11.C). Kolor tynku – orientacyjny. (nazwa, obrys [(e, n)], wysokość nad terenem, kolor hex sRGB)
BRYLY_DALSZE = [
    # --- na pd. od ramki (kwartał Mazowiecka – Wybrzeże Słowackiego)
    ('Mazowiecka 17 – skrzydło frontowe (cd.)', [(34.05, -35.5), (47.5, -35.5), (31.0, -80.0), (17.8, -80.0)], 19.0,
     'dddbd3', 'dachowka'),
    ('Mazowiecka 17 – oficyny', [(50.0, -36.5), (76.0, -37.0), (72.0, -60.0), (46.0, -58.0)], 15.0, 'c9c4ba', 'papa'),
    ('oficyna pd.', [(40.0, -60.0), (70.0, -62.0), (66.0, -80.0), (36.0, -78.0)], 14.0, 'c2bcb0', 'papa'),
    ('pawilon', [(52.0, -86.0), (77.0, -86.0), (77.0, -97.0), (52.0, -97.0)], 6.5, 'd8d6d0', 'papa'),
    ('Wybrzeże Słowackiego 10–11', [(104.5, -26.6), (120.5, -26.1), (121.3, -55.0), (103.0, -55.0)], 19.6, 'a69a88',
     'dach_szary'),
    ('kwartał pd. – budynek', [(88.0, -56.0), (102.0, -56.0), (103.0, -92.0), (88.0, -92.0)], 17.0, 'b0aaa0', 'papa'),
    ('Wybrzeże Słowackiego 12–14 (UMWD)', [(104.0, -57.0), (122.0, -57.0), (124.5, -150.0), (100.0, -150.0)], 22.0,
     'dedcd6', 'dach_szary'),
    ('kwartał pd. – budynek 2', [(86.0, -97.0), (99.0, -97.0), (99.0, -150.0), (86.0, -150.0)], 18.0, 'bdb7ad', 'papa'),
    # --- na pn.-zach. (pl. Powstańców Warszawy)
    ('DUW – skrzydło nadrzeczne i pierzeje', [(-110.0, 293.0), (-60.0, 288.0), (-25.0, 273.0), (0.0, 256.0),
                                               (20.0, 236.0), (35.0, 213.0), (45.0, 190.0), (52.0, 165.0), (55.0, 143.0),
                                               (36.0, 142.0), (34.0, 160.0), (27.0, 185.0), (16.0, 208.0), (0.0, 228.0),
                                               (-20.0, 245.0), (-50.0, 260.0), (-93.0, 266.0), (-93.0, 215.0),
                                               (-110.0, 212.0)], 24.0, 'c8c4ba', 'dach_szary'),
    ('DUW – skrzydło pd.-zach.', [(-93.0, 215.0), (-60.0, 182.0), (-28.0, 150.0), (36.0, 142.0), (34.0, 160.0),
                                  (-18.0, 166.0), (-48.0, 196.0), (-80.0, 228.0), (-93.0, 228.0)], 24.0, 'c8c4ba',
     'dach_szary'),
    ('DUW – skrzydło środkowe', [(-62.0, 218.0), (-30.0, 225.0), (-25.0, 252.0), (-58.0, 258.0)], 18.0, 'c8c4ba',
     'dach_szary'),
    ('Muzeum Narodowe', [(-239.0, 310.0), (-191.0, 361.0), (-137.0, 316.0), (-182.0, 265.0)], 22.0, '9a5a44',
     'dachowka'),
    # --- pn. brzeg Odry (pl. Grunwaldzki)
    ('pn. brzeg – budynek A', [(226.0, 265.0), (280.0, 265.0), (282.0, 302.0), (228.0, 302.0)], 20.0, 'b9b5ab', 'papa'),
    ('pn. brzeg – zespół B', [(170.0, 297.0), (228.0, 297.0), (228.0, 347.0), (170.0, 347.0)], 16.0, 'd0ccc2', 'papa'),
    ('pn. brzeg – budynek C', [(244.0, 350.0), (298.0, 350.0), (298.0, 398.0), (244.0, 398.0)], 20.0, 'aaa59b', 'papa'),
    ('pn. brzeg – budynek D', [(160.0, 380.0), (220.0, 380.0), (220.0, 422.0), (160.0, 422.0)], 22.0, 'c4c0b6', 'papa'),
    ('pn. brzeg – budynek E', [(298.0, 272.0), (352.0, 272.0), (352.0, 314.0), (298.0, 314.0)], 18.0, 'b3aea4', 'papa'),
    ('pn. brzeg – budynek F', [(358.0, 290.0), (412.0, 290.0), (412.0, 332.0), (358.0, 332.0)], 18.0, 'bcb7ad', 'papa'),
    ('pn. brzeg – budynek G', [(100.0, 375.0), (150.0, 375.0), (150.0, 445.0), (100.0, 445.0)], 25.0, '9f9b93', 'papa'),
    # --- wsch. brzeg (Wybrzeże Wyspiańskiego)
    ('wsch. brzeg – 1', [(302.0, 78.0), (338.0, 78.0), (338.0, 114.0), (302.0, 114.0)], 18.0, 'c6c0b4', 'papa'),
    ('wsch. brzeg – 2', [(314.0, 24.0), (350.0, 24.0), (350.0, 60.0), (314.0, 60.0)], 18.0, 'bfb9ad', 'papa'),
    ('wsch. brzeg – 3', [(320.0, -24.0), (368.0, -24.0), (368.0, 12.0), (320.0, 12.0)], 16.0, 'c9c3b8', 'papa'),
    ('wsch. brzeg – 4', [(344.0, -66.0), (392.0, -66.0), (392.0, -30.0), (344.0, -30.0)], 15.0, 'b8b2a6', 'papa'),
    ('wsch. brzeg – 5', [(374.0, -102.0), (422.0, -102.0), (422.0, -66.0), (374.0, -66.0)], 15.0, 'c2bcb0', 'papa'),
    ('wsch. brzeg – 6', [(404.0, 6.0), (464.0, 6.0), (464.0, 78.0), (404.0, 78.0)], 20.0, 'd6d3cc', 'papa'),
    ('wsch. brzeg – 7', [(326.0, 120.0), (380.0, 120.0), (380.0, 150.0), (326.0, 150.0)], 20.0, 'b5b0a6', 'papa'),
]


# ============================================================================================== główna funkcja
def build_context(scene, opts=None):
    """Buduje w scenie kolekcję ``KONTEKST`` z kolekcjami składowymi (patrz opis modułu).

    opts (słownik, wszystkie klucze opcjonalne – patrz ``DOMYSLNE``):
        pora_roku: 'jesien' | 'lato'; obszar_inwestycji: 'pusty' | 'istniejacy';
        teren, woda, sasiedzi, budynki, most, helmy, zielen, ulica, dalsze, ortofoto, dalsze_bryly, dalsze_drzewa: bool;
        okna_szczytu_maz19: bool; H_woda: float [m n.p.m.]; gestosc_lisci: float; seed: int; site_json, cache_dir.
    Zwraca słownik: {'kolekcje': {nazwa: Collection}, 'info': {...czasy, liczby obiektów, założenia...}}.
    """
    ctx = Kontekst(scene, opts)
    o = ctx.opts
    ctx.woda_poly = _woda_ramka(ctx)
    if o['teren']:
        zbuduj_teren(ctx)
    else:
        ctx.jezdnie_poly = Polygon()
    if o['woda']:
        zbuduj_wode(ctx)
    if o['sasiedzi'] or o['budynki']:
        zbuduj_budynki(ctx)
    if o['most']:
        zbuduj_most(ctx)
    if o['zielen']:
        zbuduj_zielen(ctx)
    if o['ulica']:
        zbuduj_ulice(ctx)
    if o['dalsze']:
        zbuduj_dalsze(ctx)
    ctx.info['Z0'] = Z0
    ctx.info['H_woda'] = o['H_woda']
    ctx.info['pora_roku'] = o['pora_roku']
    scene['umwd_kontekst_info'] = json.dumps(ctx.info, ensure_ascii=False)
    return {'kolekcje': dict(ctx.kol), 'info': ctx.info, 'ctx': ctx}


# ============================================================================================== podgląd (render testowy)
KAMERY = {
    # nazwa: (pozycja [e, n, wysokość nad terenem lub Z bezwzględne], cel, ogniskowa mm, poziomowanie, shift_y, rozdz.)
    'lot_ptaka_pnwsch': dict(loc=(185.0, 245.0, 135.0), abs_z=True, target=(82.0, 35.0, 0.0), lens=26.0, level=False,
                             shift_y=0.0, res=(1000, 625), czas='2025-10-29 11:40'),
    'skwer_pd': dict(loc=(80.5, 74.5, 1.65), abs_z=False, target=(82.0, 10.0, 8.0), lens=22.0, level=True,
                     shift_y=0.13, res=(960, 640), czas='2025-10-29 14:00'),
    'mazowiecka_pn': dict(loc=(27.5, -31.0, 1.65), abs_z=False, target=(52.0, 60.0, 8.0), lens=24.0, level=True,
                          shift_y=0.10, res=(960, 640), czas='2025-10-29 14:00'),
}


def ustaw_kamere(ctx_or_teren, sc, nazwa):
    k = KAMERY[nazwa]
    ter = ctx_or_teren.teren if hasattr(ctx_or_teren, 'teren') else ctx_or_teren
    x, y, z = k['loc']
    if not k['abs_z']:
        z = ter.z1(x, y) + z
    tx, ty, tz = k['target']
    tz = ter.z1(tx, ty) + tz if not k['abs_z'] else tz
    cam = blib.camera(sc, (x, y, z), (tx, ty, tz), lens_mm=k['lens'], level=k['level'], shift_y=k['shift_y'],
                      name='K_' + nazwa)
    sc.render.resolution_x, sc.render.resolution_y = k['res']
    return cam


def export_preview(out_dir=None, opts=None, kamery=None, samples=28, data_godzina='2025-10-29 11:40', jpg_q=88,
                   prefix='context_test_'):
    """Render testowy kontekstu z kamer KAMERY do ``docs/60_wizualizacje/img/context_test_<kamera>.jpg``
    (≤ 1 MB). Zwraca {kamera: (ścieżka, czas_s)} oraz info z budowy."""
    import datetime
    from umwd.sun import sun_position, TZ
    from PIL import Image
    out_dir = Path(out_dir or DOCS_IMG)
    out_dir.mkdir(parents=True, exist_ok=True)
    sc = blib.reset()
    t0 = time.time()
    res = build_context(sc, opts)
    t_build = time.time() - t0
    ctx = res['ctx']
    # azymut Słońca w układzie siatki: az + 0,738° (zbieżność południków γ = −0,738°, geometria.md § 2.2)
    blib.render_settings(sc, 960, 640, samples=samples, adaptive=0.02, exposure=-0.25, look='AgX - Base Contrast')
    wyniki = {}
    for nm in (kamery or list(KAMERY)):
        for o in [o for o in sc.objects if o.type == 'LIGHT']:
            bpy.data.objects.remove(o)
        dt = datetime.datetime.strptime(KAMERY[nm].get('czas', data_godzina), '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
        az, el = sun_position(dt)
        blib.sky_and_sun(sc, az + 0.738, el, sun_strength=6.0, sky_strength=0.18)
        ustaw_kamere(ctx, sc, nm)
        png = out_dir / ('_tmp_%s.png' % nm)
        sc.render.filepath = str(png)
        t1 = time.time()
        bpy.ops.render.render(write_still=True)
        dtr = time.time() - t1
        jpg = out_dir / ('%s%s.jpg' % (prefix, nm))
        im = Image.open(png).convert('RGB')
        q = jpg_q
        while True:
            im.save(jpg, quality=q, optimize=True)
            if jpg.stat().st_size <= 1_000_000 or q < 50:
                break
            q -= 6
        png.unlink()
        wyniki[nm] = (str(jpg), round(dtr, 1))
        print('[kontekst] %s: %.1f s → %s' % (nm, dtr, jpg))
    print('[kontekst] budowa sceny %.1f s' % t_build)
    return wyniki, res['info'], round(t_build, 1)


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser(description='Kontekst 3D UMWD – render podglądu')
    ap.add_argument('--podglad', action='store_true', help='render 3 kamer do docs/60_wizualizacje/img')
    ap.add_argument('--kamery', nargs='*', default=None)
    ap.add_argument('--probki', type=int, default=28)
    ap.add_argument('--pora', default='jesien')
    ap.add_argument('--obszar', default='pusty')
    ap.add_argument('--out', default=None)
    ap.add_argument('--blend', default=None, help='zapisz scenę .blend')
    ap.add_argument('--bez-dalszych', action='store_true')
    a = ap.parse_args()
    op = {'pora_roku': a.pora, 'obszar_inwestycji': a.obszar}
    if a.bez_dalszych:
        op['dalsze'] = False
    if a.podglad:
        w, info, tb = export_preview(a.out, op, a.kamery, samples=a.probki)
        print(json.dumps({'wyniki': w, 'budowa_s': tb, 'info': info}, ensure_ascii=False, indent=1))
    else:
        sc = blib.reset()
        r = build_context(sc, op)
        print(json.dumps(r['info'], ensure_ascii=False, indent=1))
    if a.blend:
        bpy.ops.wm.save_as_mainfile(filepath=a.blend)
