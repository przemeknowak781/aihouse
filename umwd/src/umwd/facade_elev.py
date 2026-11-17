"""Orthographic elevations from façade 'faces' described in local coordinates (s along the façade, z up).

A Face is a polyline (in CCW building order → s grows left→right for a viewer facing the façade) with
2D elements (rects / lines) in (s, z). draw_faces() projects all faces onto the plane perpendicular to the
viewing azimuth, clips curved faces to the part that faces the viewer and paints far→near (painter).
Pure python + Svg (no bpy).
"""
from __future__ import annotations
import math
from .runs import Run

INK = "#1f1d1a"


def frame(view_az):
    a = math.radians(view_az)
    d = (math.sin(a), math.cos(a))      # viewing direction
    r = (d[1], -d[0])                   # screen right
    return d, r


class Face:
    def __init__(self, pts, z0, z1, name="", fill="#ffffff", outline=True, depth_bias=0.0):
        self.pts = [tuple(p) for p in pts]
        self.run = Run(self.pts)
        self.L = self.run.L
        self.z0, self.z1 = z0, z1
        self.name = name
        self.curved = len(self.pts) > 2
        self.els = []
        self.depth_bias = depth_bias
        if fill is not None:
            self.rect(0, self.L, z0, z1, fill=fill, stroke=INK if outline else "none", sw=0.18)

    # ---- element builders (s, z in metres)
    def rect(self, s0, s1, z0, z1, fill="none", stroke="none", sw=0.08, op=1.0, extra=""):
        s0, s1 = max(0.0, min(s0, s1)), min(self.L, max(s0, s1))
        if s1 - s0 > 1e-4 and z1 - z0 > 1e-4:
            self.els.append(("rect", s0, s1, z0, z1, fill, stroke, sw, op, extra))

    def hline(self, s0, s1, z, stroke=INK, sw=0.08, dash=None):
        s0, s1 = max(0.0, s0), min(self.L, s1)
        if s1 > s0:
            self.els.append(("hline", s0, s1, z, z, None, stroke, sw, 1.0, dash))

    def vline(self, s, z0, z1, stroke=INK, sw=0.08):
        if 0 <= s <= self.L:
            self.els.append(("vline", s, s, z0, z1, None, stroke, sw, 1.0, None))

    def circle(self, s, z, r, fill="#7d8f63", op=0.6):
        if 0 <= s <= self.L:
            self.els.append(("circle", s, s, z, z, fill, "none", r, op, None))

    def text(self, s, z, txt, size=1.6, fill=INK, weight=600, ls=0.6):
        self.els.append(("text", s, s, z, z, fill, txt, size, weight, ls))


def _samples(face, s0, s1, step):
    n = max(1, int(math.ceil((s1 - s0) / step)))
    return [s0 + (s1 - s0) * k / n for k in range(n + 1)]


def draw_faces(svg, faces, view_az, P, facing_tol=0.03, cut=None, debug=False):
    """P(u, z) -> paper (x, y). cut: only geometry with depth (p·d) >= cut is drawn (section plane).
    Returns (u_min, u_max) of drawn content."""
    d, r = frame(view_az)

    def U(face, s):
        (x, y), _ = face.run.at(s)
        return x * r[0] + y * r[1]

    def facing(face, s):
        (x, y), (tx, ty) = face.run.at(s)
        nx, ny = ty, -tx
        if cut is not None and x * d[0] + y * d[1] < cut:
            return False
        return nx * d[0] + ny * d[1] < -facing_tol

    def depth(face):
        ss = _samples(face, 0, face.L, 1.0)
        vis = [s for s in ss if facing(face, s)] or ss
        return sum(face.run.at(s)[0][0] * d[0] + face.run.at(s)[0][1] * d[1] for s in vis) / len(vis) + face.depth_bias

    vis_faces = [f for f in faces if any(facing(f, s) for s in _samples(f, 0, f.L, 0.5))]
    vis_faces.sort(key=lambda f: -depth(f))
    umin, umax = 1e9, -1e9
    for f in vis_faces:
        for el in f.els:
            kind, s0, s1, z0, z1, fill, stroke, sw, op, extra = el
            if kind == "text":
                if facing(f, s0):
                    x, y = P(U(f, s0), z0)
                    svg.text((x, y), stroke, size=sw, anchor="middle", weight=op, fill=fill, ls=extra)
                continue
            if kind == "circle":
                if facing(f, s0):
                    x, y = P(U(f, s0), z0)
                    svg.circle((x, y), sw * (P(1, 0)[0] - P(0, 0)[0]), fill=fill, stroke="none", extra=f'fill-opacity="{op}"')
                continue
            if kind == "vline":
                if facing(f, s0):
                    svg.line(P(U(f, s0), z0), P(U(f, s0), z1), stroke=stroke, sw=sw)
                continue
            step = 0.25 if (f.curved or cut is not None) else (s1 - s0)
            ss = _samples(f, s0, s1, step)
            mask = [facing(f, s) for s in ss]
            # contiguous facing chunks
            chunks, cur = [], []
            for s, m in zip(ss, mask):
                if m:
                    cur.append(s)
                elif cur:
                    chunks.append(cur); cur = []
            if cur:
                chunks.append(cur)
            for ch in chunks:
                if len(ch) == 1:
                    continue
                us = [U(f, s) for s in ch]
                umin, umax = min(umin, *us), max(umax, *us)
                if kind == "hline":
                    svg.poly([P(u, z0) for u in us], fill="none", stroke=stroke, sw=sw, close=False,
                             extra=(f'stroke-dasharray="{extra}"' if extra else ""))
                else:
                    pts = [P(u, z0) for u in us] + [P(u, z1) for u in reversed(us)]
                    ex = (f'fill-opacity="{op}" ' if op < 1 else "") + (extra or "") + ' stroke-linejoin="round"'
                    svg.poly(pts, fill=fill, stroke=stroke, sw=sw, extra=ex)
    if debug:
        for f in vis_faces:
            sm = f.L / 2
            x, y = P(U(f, sm), (f.z0 + f.z1) / 2)
            svg.text((x, y), f.name, size=3, anchor="middle", fill="#d00")
    return umin, umax


def u_of(view_az, e, n):
    _, r = frame(view_az)
    return e * r[0] + n * r[1]
