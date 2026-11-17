"""Orthographic elevation drawings (SVG) from façade-run volumes — painter's algorithm, competition graphics.

volume = {"name", "poly": [(e,n)...], "z0", "z1", "spec": façade spec (as render.facade2), "cornice": (h, colour),
          "fill": wall colour, "levels": [(z, h)...]}
view: azimuth (deg, from north clockwise) of the direction the VIEWER LOOKS; elevation plane ⟂ to it.
Output coordinates: u along the plane (left→right as seen by the viewer), z up; scaled 1:scale in mm.
"""
from __future__ import annotations
import math
from .runs import ccw, runs_of, Run
from .svg import Svg

INK = "#1f1d1a"


def frame(view_az):
    a = math.radians(view_az)
    d = (math.sin(a), math.cos(a))                 # viewing direction (into the drawing)
    r = (d[1], -d[0])                              # screen right
    return d, r


def project_volume(vol, view_az):
    d, r = frame(view_az)
    sp = vol["spec"]
    poly = ccw([tuple(p) for p in vol["poly"]])
    items = []
    for ri, pts in enumerate(runs_of(poly, sp.get("curve_angle", 25.0))):
        run = Run(pts)
        if run.L < 0.3:
            continue
        # facing test using the run's mid tangent: outward normal = right of tangent
        (mx, my), (tx, ty) = run.at(run.L / 2)
        nx, ny = ty, -tx
        # for curved runs check several samples
        samples = [run.at(run.L * k / 8) for k in range(9)]
        facing = any((p[1][1] * d[0] - p[1][0] * d[1]) < -1e-3 for p in samples)  # normal·d < 0 → facing viewer
        if not facing:
            continue
        depth = sum(((p[0][0]) * d[0] + (p[0][1]) * d[1]) for p in samples) / len(samples)
        items.append((depth, ri, run))
    return items


def draw(svg: Svg, vols, view_az, scale, ox, oy, z_ref=0.0, u_min=None, show_glass=True, hatch_glass="#3b3a38"):
    """Draw volumes; (ox, oy) = paper position of (u=u_min, z=z_ref) baseline. Returns (u_min, u_max, z_max)."""
    d, r = frame(view_az)
    k = 1000.0 / scale
    allruns = []
    for v in vols:
        for depth, ri, run in project_volume(v, view_az):
            allruns.append((depth, v, run))
    if not allruns:
        return None
    us = [p[0] * r[0] + p[1] * r[1] for _, v, run in allruns for p in run.pts]
    if u_min is None:
        u_min = min(us)
    def P(u, z):
        return (ox + (u - u_min) * k, oy - (z - z_ref) * k)
    allruns.sort(key=lambda t: -t[0])            # far first
    zmax = 0
    for depth, v, run in allruns:
        sp = v["spec"]; z0, z1 = v["z0"], v["z1"]; zmax = max(zmax, z1 + sp.get("cornice_h", 0))
        U = lambda s: (run.at(s)[0][0] * r[0] + run.at(s)[0][1] * r[1])
        # wall silhouette of the run
        ss = run.strip(0, run.L, 0.5)
        uu = [U(s) for s in ss]
        u0, u1 = min(uu), max(uu)
        svg.poly([P(u0, z0), P(u1, z0), P(u1, z1), P(u0, z1)], fill=v.get("fill", "#ffffff"), stroke=INK, sw=0.18)
        bay_t = sp.get("bay", 2.7); nb = max(1, round(run.L / bay_t)); bay = run.L / nb
        pw = min(sp.get("pier_w", 1.0), bay * 0.6)
        levels = [(zf, h) for zf, h in sp.get("levels", []) if z0 - 1e-6 <= zf < z1 - 1e-6]
        if show_glass and run_is_glazed(sp, v, run):
            for kb in range(nb):
                q0, q1 = kb * bay + pw / 2, (kb + 1) * bay - pw / 2
                if q1 - q0 < 0.1:
                    continue
                a0, a1 = sorted((U(q0), U(q1)))
                if a1 - a0 < 0.05:
                    continue
                for zf, h in levels:
                    ground = abs(zf - z0) < 0.01
                    zb = zf + (sp.get("ground_glass_sill", 0.0) if ground else sp.get("sill", 0.9))
                    zt = min(zf + h - sp.get("head", 0.35), z1 - sp.get("head", 0.35) * 0.5)
                    if zt - zb > 0.3:
                        svg.poly([P(a0, zb), P(a1, zb), P(a1, zt), P(a0, zt)], fill=hatch_glass, stroke="none",
                                 extra='fill-opacity="0.78"')
        # pier edges (vertical lines)
        for kb in range(nb + 1):
            for s in (kb * bay - pw / 2, kb * bay + pw / 2):
                if 0 < s < run.L:
                    u = U(s)
                    svg.line(P(u, z0), P(u, z1), stroke=INK, sw=0.07)
        # floor lines (thin)
        for zf, h in levels:
            if zf > z0 + 0.01:
                svg.line(P(u0, zf), P(u1, zf), stroke="#8a857e", sw=0.05)
        # cornice
        ch = sp.get("cornice_h", 0)
        if ch:
            svg.poly([P(u0, z1), P(u1, z1), P(u1, z1 + ch), P(u0, z1 + ch)], fill=v.get("cornice_fill", "#ffffff"), stroke=INK, sw=0.18)
    return u_min, max(us), zmax


def run_is_glazed(sp, v, run):
    return not v.get("blind", False)


def level_marks(svg: Svg, scale, x, oy, z_ref, marks, side="left"):
    """Elevation level markers: marks = [(z_rel, label)]."""
    k = 1000.0 / scale
    for z, lab in marks:
        y = oy - (z - z_ref) * k
        svg.poly([(x, y), (x - 1.6, y - 1.6), (x + 1.6, y - 1.6)], fill=INK, stroke="none")
        svg.line((x - 3, y), (x + 3, y), stroke=INK, sw=0.15)
        svg.text((x - 4 if side == "left" else x + 4, y - 0.6), lab, size=2.0, anchor="end" if side == "left" else "start")
