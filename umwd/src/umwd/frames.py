"""Układy lokalne budynku (u,v – wieża; s,d – skrzydło) czytane z model/koncepcja.json.

Formuły w koncepcja.json mają postać tekstową, np. "74,606 + 0,97155·u − 0,23684·v" – parsujemy je w czasie działania,
żeby zmiana specyfikacji przenosiła się automatycznie do modelu pomieszczeń i rysunków.
"""
from __future__ import annotations
import math
import re
from dataclasses import dataclass
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

_NUM = r"[−-]?\s*\d+(?:[.,]\d+)?"


def _num(s: str) -> float:
    return float(s.replace("−", "-").replace(" ", "").replace(",", "."))


def parse_affine(expr: str, a: str, b: str):
    """'74,606 + 0,97155·u − 0,23684·v' -> (c, ka, kb)."""
    t = expr.replace("−", "-").replace("·", "*").replace(" ", "")
    t = re.sub(r"(\d),(\d)", r"\1.\2", t)
    c = ka = kb = 0.0
    for sign, val, var in re.findall(r"([+-]?)(\d+(?:\.\d+)?)(?:\*?([a-z]))?", t):
        x = float(val) * (-1.0 if sign == "-" else 1.0)
        if var == a:
            ka += x
        elif var == b:
            kb += x
        else:
            c += x
    return c, ka, kb


@dataclass
class Frame:
    """Ortonormalny układ lokalny: P_en = o + x·ex + y·ey."""
    o: tuple
    ex: tuple
    ey: tuple
    name: str = ""

    @classmethod
    def from_spec(cls, spec: dict, a: str, b: str, name=""):
        ce, kea, keb = parse_affine(spec["e"], a, b)
        cn, kna, knb = parse_affine(spec["n"], a, b)
        ex = (kea, kna)
        ey = (keb, knb)
        # renormalizacja (współczynniki podane z 5 miejscami)
        lx = math.hypot(*ex)
        ex = (ex[0] / lx, ex[1] / lx)
        ey = (-ex[1], ex[0]) if (ex[0] * ey[1] - ex[1] * ey[0]) > 0 else (ex[1], -ex[0])
        return cls((ce, cn), ex, ey, name)

    def en(self, x, y):
        return (self.o[0] + x * self.ex[0] + y * self.ey[0], self.o[1] + x * self.ex[1] + y * self.ey[1])

    def loc(self, e, n):
        de, dn = e - self.o[0], n - self.o[1]
        return (de * self.ex[0] + dn * self.ex[1], de * self.ey[0] + dn * self.ey[1])

    def rect(self, x0, x1, y0, y1) -> Polygon:
        return Polygon([self.en(x0, y0), self.en(x1, y0), self.en(x1, y1), self.en(x0, y1)])

    def poly(self, pts) -> Polygon:
        return Polygon([self.en(x, y) for x, y in pts])

    def pt(self, x, y) -> Point:
        return Point(*self.en(x, y))

    def line(self, pts) -> LineString:
        return LineString([self.en(x, y) for x, y in pts])

    def angle_deg(self):
        """Kąt osi x układu względem osi e (w stopniach, przeciwnie do ruchu wskazówek)."""
        return math.degrees(math.atan2(self.ex[1], self.ex[0]))

    def to_local_geom(self, g):
        from shapely.ops import transform
        return transform(lambda e, n, z=None: self._loc_arr(e, n), g)

    def to_en_geom(self, g):
        from shapely.ops import transform
        return transform(lambda x, y, z=None: self._en_arr(x, y), g)

    def _loc_arr(self, e, n):
        import numpy as np
        e = np.asarray(e, dtype=float); n = np.asarray(n, dtype=float)
        de, dn = e - self.o[0], n - self.o[1]
        return (de * self.ex[0] + dn * self.ex[1], de * self.ey[0] + dn * self.ey[1])

    def _en_arr(self, x, y):
        import numpy as np
        x = np.asarray(x, dtype=float); y = np.asarray(y, dtype=float)
        return (self.o[0] + x * self.ex[0] + y * self.ey[0], self.o[1] + x * self.ex[1] + y * self.ey[1])


def annulus_sector(frame: Frame, c, r0, r1, a0, a1, n=48) -> Polygon:
    """Wycinek pierścienia w układzie frame (c – środek w (x,y) lokalnych), kąty w stopniach (od osi x, CCW)."""
    k = max(4, int(abs(a1 - a0) / 90.0 * n))
    outer = [(c[0] + r1 * math.cos(math.radians(a0 + (a1 - a0) * i / k)), c[1] + r1 * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]
    inner = [(c[0] + r0 * math.cos(math.radians(a1 - (a1 - a0) * i / k)), c[1] + r0 * math.sin(math.radians(a1 - (a1 - a0) * i / k))) for i in range(k + 1)]
    if r0 <= 1e-6:
        inner = [c]
    return frame.poly(outer + inner)


def clean_ring(pts, tol=1e-3):
    """Usuwa zdublowane wierzchołki i 'kolce' (A→B→A) z pierścienia; zwraca listę punktów i listę uwag."""
    notes = []
    p = [tuple(x) for x in pts]
    out = []
    for q in p:
        if out and math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) < tol:
            notes.append(f"zdublowany wierzchołek {q}")
            continue
        out.append(q)
    changed = True
    while changed and len(out) > 3:
        changed = False
        for i in range(len(out)):
            a, b, c = out[i - 1], out[i], out[(i + 1) % len(out)]
            if math.hypot(a[0] - c[0], a[1] - c[1]) < tol:
                notes.append(f"kolec (A→B→A) w wierzchołku {b}")
                # usuń b i c (powrót do a)
                idx = sorted([i, (i + 1) % len(out)], reverse=True)
                for j in idx:
                    out.pop(j)
                changed = True
                break
            # współliniowe z cofnięciem
            v1 = (b[0] - a[0], b[1] - a[1]); v2 = (c[0] - b[0], c[1] - b[1])
            cr = v1[0] * v2[1] - v1[1] * v2[0]
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            if abs(cr) < 1e-6 and dot < 0:
                notes.append(f"cofnięcie współliniowe w {b}")
                out.pop(i)
                changed = True
                break
    return out, notes
