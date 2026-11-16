"""Minimal, precise SVG drawing engine for competition drawings (vector, print-ready).

Model coordinates are metres in the project's local grid (e = east, n = north); paper units are millimetres.
A View maps a model window to a paper rectangle at a given scale (1:scale). SVG y grows downward, model n upward.
"""
from __future__ import annotations
import html, math
from dataclasses import dataclass, field

FONT = "Inter, 'Inter Display', 'DejaVu Sans', sans-serif"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


@dataclass
class View:
    e0: float            # model window min east
    n0: float            # model window min north
    e1: float
    n1: float
    scale: float         # 1:scale
    rot_deg: float = 0.0 # rotation of model about window centre (for drawings aligned to building axes)

    @property
    def w_mm(self):
        return (self.e1 - self.e0) * 1000.0 / self.scale

    @property
    def h_mm(self):
        return (self.n1 - self.n0) * 1000.0 / self.scale

    def p(self, e, n):
        if self.rot_deg:
            cx, cy = (self.e0 + self.e1) / 2, (self.n0 + self.n1) / 2
            a = math.radians(self.rot_deg)
            de, dn = e - cx, n - cy
            e, n = cx + de * math.cos(a) - dn * math.sin(a), cy + de * math.sin(a) + dn * math.cos(a)
        return ((e - self.e0) * 1000.0 / self.scale, (self.n1 - n) * 1000.0 / self.scale)

    def mm(self, metres):
        return metres * 1000.0 / self.scale


@dataclass
class Svg:
    w_mm: float
    h_mm: float
    parts: list = field(default_factory=list)
    defs: list = field(default_factory=list)
    _id: int = 0

    def uid(self, p="id"):
        self._id += 1
        return f"{p}{self._id}"

    def add(self, s):
        self.parts.append(s)

    def group(self, inner: str, attrs: str = ""):
        self.parts.append(f"<g {attrs}>{inner}</g>")

    # primitives (paper mm) ------------------------------------------------
    @staticmethod
    def path_d(pts, close=True):
        if not pts:
            return ""
        d = "M" + " L".join(f"{x:.3f},{y:.3f}" for x, y in pts)
        return d + (" Z" if close else "")

    def poly(self, pts, fill="none", stroke="#000", sw=0.18, close=True, extra=""):
        self.add(f'<path d="{self.path_d(pts, close)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.3f}" '
                 f'stroke-linejoin="round" stroke-linecap="round" {extra}/>')

    def multipoly(self, rings_list, fill="none", stroke="#000", sw=0.18, extra=""):
        """rings_list: list of rings (each a list of points); uses evenodd so holes work."""
        d = " ".join(self.path_d(r, True) for r in rings_list if r)
        if d:
            self.add(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw:.3f}" '
                     f'stroke-linejoin="round" {extra}/>')

    def line(self, a, b, stroke="#000", sw=0.18, dash=None, extra=""):
        da = f'stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" stroke="{stroke}" '
                 f'stroke-width="{sw:.3f}" stroke-linecap="round" {da} {extra}/>')

    def circle(self, c, r, fill="none", stroke="#000", sw=0.18, extra=""):
        self.add(f'<circle cx="{c[0]:.3f}" cy="{c[1]:.3f}" r="{r:.3f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.3f}" {extra}/>')

    def text(self, xy, s, size=2.5, anchor="start", weight=400, fill="#1d1d1b", rot=0.0, family=FONT, extra="", ls=0.0):
        tr = f'transform="rotate({rot:.2f} {xy[0]:.3f} {xy[1]:.3f})"' if rot else ""
        lsp = f'letter-spacing="{ls}"' if ls else ""
        self.add(f'<text x="{xy[0]:.3f}" y="{xy[1]:.3f}" font-family="{family}" font-size="{size:.3f}" font-weight="{weight}" '
                 f'text-anchor="{anchor}" fill="{fill}" {lsp} {tr} {extra}>{esc(s)}</text>')

    def image(self, xy, w, h, href, extra='preserveAspectRatio="xMidYMid slice"'):
        self.add(f'<image x="{xy[0]:.3f}" y="{xy[1]:.3f}" width="{w:.3f}" height="{h:.3f}" href="{esc(href)}" {extra}/>')

    def hatch(self, name, spacing=1.2, angle=45, stroke="#000", sw=0.08, bg="none"):
        pid = f"h_{name}"
        self.defs.append(
            f'<pattern id="{pid}" patternUnits="userSpaceOnUse" width="{spacing}" height="{spacing}" patternTransform="rotate({angle})">'
            + (f'<rect width="{spacing}" height="{spacing}" fill="{bg}"/>' if bg != "none" else "")
            + f'<line x1="0" y1="0" x2="0" y2="{spacing}" stroke="{stroke}" stroke-width="{sw}"/></pattern>')
        return f"url(#{pid})"

    def render(self, extra_style="") -> str:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w_mm:.3f}mm" height="{self.h_mm:.3f}mm" viewBox="0 0 {self.w_mm:.3f} {self.h_mm:.3f}">'
                + (f"<style>{extra_style}</style>" if extra_style else "")
                + "<defs>" + "".join(self.defs) + "</defs>" + "".join(self.parts) + "</svg>")


# helpers for model → paper ------------------------------------------------
def model_poly(svg: Svg, v: View, pts, **kw):
    svg.poly([v.p(*p) for p in pts], **kw)


def model_rings(svg: Svg, v: View, geom, **kw):
    """Draw a shapely Polygon/MultiPolygon (with holes) in model coords."""
    from shapely.geometry import Polygon, MultiPolygon
    polys = [geom] if isinstance(geom, Polygon) else list(getattr(geom, "geoms", []))
    for pg in polys:
        if pg.is_empty:
            continue
        rings = [[v.p(*c) for c in pg.exterior.coords]] + [[v.p(*c) for c in r.coords] for r in pg.interiors]
        svg.multipoly(rings, **kw)


def north_arrow(svg: Svg, xy, size=12, rot_deg=0.0):
    x, y = xy
    a = math.radians(rot_deg)
    def r(dx, dy):
        return (x + dx * math.cos(a) - dy * math.sin(a), y + dx * math.sin(a) + dy * math.cos(a))
    svg.circle((x, y), size * 0.5, stroke="#1d1d1b", sw=0.25)
    svg.poly([r(0, -size * 0.62), r(size * 0.16, size * 0.25), r(0, size * 0.12), r(-size * 0.16, size * 0.25)], fill="#1d1d1b", stroke="none")
    tx, ty = r(0, -size * 0.75)
    svg.text((tx, ty), "N", size=size * 0.28, anchor="middle", weight=600)


def scale_bar(svg: Svg, xy, scale, metres=(0, 5, 10, 20), h=1.6, label=True):
    x, y = xy
    total = metres[-1]
    L = total * 1000.0 / scale
    for i in range(len(metres) - 1):
        x0 = x + metres[i] * 1000.0 / scale
        x1 = x + metres[i + 1] * 1000.0 / scale
        svg.poly([(x0, y), (x1, y), (x1, y + h), (x0, y + h)], fill="#1d1d1b" if i % 2 == 0 else "#ffffff", stroke="#1d1d1b", sw=0.2)
    for m in metres:
        svg.text((x + m * 1000.0 / scale, y + h + 3.0), f"{m}", size=2.2, anchor="middle")
    if label:
        svg.text((x + L + 3, y + h), f"m   1:{int(scale)}", size=2.4, weight=500)
