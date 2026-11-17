"""Pure-geometry façade runs (no bpy): CCW, run splitting, arc-length parametrisation."""
from __future__ import annotations
import math


def ccw(poly):
    a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
    return poly if a > 0 else poly[::-1]


def runs_of(poly, curve_angle=25.0):
    """Split closed CCW polygon into runs (lists of points incl. both ends)."""
    n = len(poly)
    def heading(i):
        a, b = poly[i], poly[(i + 1) % n]
        return math.atan2(b[1] - a[1], b[0] - a[0])
    turn = []
    for i in range(n):
        h0, h1 = heading(i - 1), heading(i)
        d = math.degrees((h1 - h0 + math.pi) % (2 * math.pi) - math.pi)
        turn.append(abs(d))          # turn at vertex i
    breaks = [i for i in range(n) if turn[i] >= curve_angle]
    if not breaks:
        breaks = [0]
    runs = []
    for k, b0 in enumerate(breaks):
        b1 = breaks[(k + 1) % len(breaks)]
        idx = [b0]
        j = b0
        while True:
            j = (j + 1) % n
            idx.append(j)
            if j == b1:
                break
        runs.append([poly[i] for i in idx])
    return runs


class Run:
    def __init__(self, pts):
        self.pts = pts
        self.cum = [0.0]
        for i in range(1, len(pts)):
            self.cum.append(self.cum[-1] + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]))
        self.L = self.cum[-1]

    def at(self, s):
        s = max(0.0, min(self.L, s))
        for i in range(1, len(self.pts)):
            if s <= self.cum[i] + 1e-9:
                a, b = self.pts[i - 1], self.pts[i]
                l = self.cum[i] - self.cum[i - 1]
                t = 0 if l < 1e-9 else (s - self.cum[i - 1]) / l
                ux, uy = ((b[0] - a[0]) / l, (b[1] - a[1]) / l) if l > 1e-9 else (1, 0)
                return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), (ux, uy)
        a, b = self.pts[-2], self.pts[-1]
        l = max(1e-9, self.cum[-1] - self.cum[-2])
        return b, ((b[0] - a[0]) / l, (b[1] - a[1]) / l)

    def strip(self, s0, s1, seg):
        """Sample points along the run from s0 to s1 (inclusive), including interior vertices."""
        ss = [s0] + [c for c in self.cum if s0 < c < s1] + [s1]
        out = []
        for i in range(len(ss) - 1):
            n = max(1, math.ceil((ss[i + 1] - ss[i]) / seg))
            for k in range(n):
                out.append(ss[i] + (ss[i + 1] - ss[i]) * k / n)
        out.append(s1)
        return out


