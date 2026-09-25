"""Pomocnicza geometria 2D (numpy + shapely)."""
from __future__ import annotations

import math
from typing import Iterable, Sequence

import numpy as np
from shapely.geometry import (GeometryCollection, LinearRing, LineString, MultiLineString, MultiPolygon,
                              Point, Polygon, box)
from shapely.geometry.base import BaseGeometry

Pt = tuple[float, float]


def P(x, y=None) -> np.ndarray:
    if y is None:
        return np.asarray(x, dtype=float)
    return np.array([x, y], dtype=float)


def arr(pts) -> np.ndarray:
    a = np.asarray(pts, dtype=float)
    if a.ndim == 1:
        a = a.reshape(-1, 2)
    return a


def length(v) -> float:
    return float(math.hypot(v[0], v[1]))


def unit(v) -> np.ndarray:
    v = np.asarray(v, dtype=float)
    n = math.hypot(v[0], v[1])
    return v / n if n > 0 else np.array([1.0, 0.0])


def perp(v) -> np.ndarray:
    """Wektor prostopadły (obrót o +90°)."""
    return np.array([-v[1], v[0]], dtype=float)


def dir_deg(a_deg: float) -> np.ndarray:
    a = math.radians(a_deg)
    return np.array([math.cos(a), math.sin(a)])


def angle_deg(v) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def rot(pts, ang_deg: float, origin=(0.0, 0.0)) -> np.ndarray:
    a = math.radians(ang_deg)
    c, s = math.cos(a), math.sin(a)
    p = arr(pts) - origin
    return np.column_stack([p[:, 0] * c - p[:, 1] * s, p[:, 0] * s + p[:, 1] * c]) + origin


def readable_angle(a_deg: float) -> float:
    """Kąt napisu tak, by był czytelny od dołu lub od prawej strony arkusza (PN-EN ISO 129-1)."""
    a = (a_deg + 180.0) % 360.0 - 180.0  # (-180, 180]
    if a > 90.0 + 1e-6:
        a -= 180.0
    elif a <= -90.0 + 1e-6:
        a += 180.0
    return a


class Xf:
    """Przekształcenie afiniczne 2D: p' = M·p + t."""

    __slots__ = ("m", "t")

    def __init__(self, m=None, t=None):
        self.m = np.eye(2) if m is None else np.asarray(m, dtype=float)
        self.t = np.zeros(2) if t is None else np.asarray(t, dtype=float)

    @staticmethod
    def make(origin=(0.0, 0.0), rot_deg: float = 0.0, scale: float = 1.0, mirror: bool = False) -> "Xf":
        a = math.radians(rot_deg)
        c, s = math.cos(a), math.sin(a)
        m = np.array([[c, -s], [s, c]]) * scale
        if mirror:
            m = m @ np.array([[-1.0, 0.0], [0.0, 1.0]])
        return Xf(m, origin)

    def __call__(self, pts) -> np.ndarray:
        p = arr(pts)
        return p @ self.m.T + self.t

    def pt(self, x, y) -> np.ndarray:
        return self.m @ np.array([x, y], dtype=float) + self.t

    def vec(self, v) -> np.ndarray:
        return self.m @ np.asarray(v, dtype=float)

    def __matmul__(self, other: "Xf") -> "Xf":
        return Xf(self.m @ other.m, self.m @ other.t + self.t)

    @property
    def angle(self) -> float:
        return math.degrees(math.atan2(self.m[1, 0], self.m[0, 0]))

    @property
    def scale(self) -> float:
        return math.sqrt(abs(np.linalg.det(self.m)))

    @property
    def mirrored(self) -> bool:
        return np.linalg.det(self.m) < 0


def arc_pts(c, r: float, a0: float, a1: float, max_seg_deg: float = 5.0) -> np.ndarray:
    """Punkty łuku (stopnie, CCW od a0 do a1)."""
    if a1 < a0:
        a1 += 360.0
    n = max(2, int(math.ceil((a1 - a0) / max_seg_deg)) + 1)
    t = np.radians(np.linspace(a0, a1, n))
    return np.column_stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)])


def circle_pts(c, r: float, n: int = 72) -> np.ndarray:
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    return np.column_stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)])


def rect_pts(x0, y0, x1, y1) -> np.ndarray:
    return np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]], dtype=float)


def rect_c(cx, cy, w, h) -> np.ndarray:
    return rect_pts(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def to_polygon(obj) -> BaseGeometry:
    if isinstance(obj, BaseGeometry):
        return obj
    a = arr(obj)
    return Polygon(a)


def polygons_of(g: BaseGeometry) -> list[Polygon]:
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        out = []
        for gg in g.geoms:
            out.extend(polygons_of(gg))
        return out
    return []


def lines_of(g: BaseGeometry) -> list[np.ndarray]:
    """Lista tablic punktów z (Multi)LineString / GeometryCollection."""
    if g is None or g.is_empty:
        return []
    if isinstance(g, LineString):
        return [np.asarray(g.coords)]
    if isinstance(g, LinearRing):
        return [np.asarray(g.coords)]
    if isinstance(g, (MultiLineString, GeometryCollection)):
        out = []
        for gg in g.geoms:
            out.extend(lines_of(gg))
        return out
    if isinstance(g, Polygon):
        out = [np.asarray(g.exterior.coords)]
        out += [np.asarray(i.coords) for i in g.interiors]
        return out
    if isinstance(g, MultiPolygon):
        out = []
        for gg in g.geoms:
            out.extend(lines_of(gg))
        return out
    return []


def strip_frame(poly: Polygon):
    """Oś główna paska (warstwy): (środek, kierunek długi u, kierunek poprzeczny v, długość L, grubość t).

    Wyznaczana z minimalnego prostokąta opisanego — pozwala generować wzory zależne od kierunku warstwy
    (wężyk wełny, zygzak styropianu, pas izolacji przeciwwodnej) niezależnie od orientacji.
    """
    mrr = poly.minimum_rotated_rectangle
    c = np.asarray(mrr.exterior.coords)[:4]
    e1 = c[1] - c[0]
    e2 = c[2] - c[1]
    if length(e1) >= length(e2):
        u, L, v, t = unit(e1), length(e1), unit(e2), length(e2)
    else:
        u, L, v, t = unit(e2), length(e2), unit(e1), length(e1)
    # orientacja kanoniczna: u w prawo (lub w górę), v = perp(u)
    if u[0] < -1e-9 or (abs(u[0]) < 1e-9 and u[1] < 0):
        u = -u
    v = perp(u)
    ctr = c.mean(axis=0)
    return ctr, u, v, L, t


def bbox_of(arrays: Iterable[np.ndarray]):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for a in arrays:
        if len(a) == 0:
            continue
        xs0.append(a[:, 0].min())
        xs1.append(a[:, 0].max())
        ys0.append(a[:, 1].min())
        ys1.append(a[:, 1].max())
    if not xs0:
        return None
    return (min(xs0), min(ys0), max(xs1), max(ys1))


def stable_seed(*vals) -> int:
    """Deterministyczne ziarno RNG z liczb (np. obrys) — powtarzalne wzory losowe (piasek, żwir)."""
    h = 1469598103934665603
    for v in vals:
        for x in np.asarray(v, dtype=float).ravel():
            h ^= int(round(float(x) * 1000.0)) & 0xFFFFFFFF
            h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return h % (2 ** 32)
