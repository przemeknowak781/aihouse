"""Pomocnicze SVG dla rysunków strony www: układ „arkusza” (metry → jednostki SVG = cm, oś y w górę → w dół),
ścieżki z geometrii shapely, elementy z klasami CSS (kolory z tokenów strony — rysunki działają w obu motywach)."""
from __future__ import annotations

from html import escape

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon

S = 100.0          # jednostek SVG na metr (1 j. = 1 cm)


def _n(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Arkusz:
    """Rzutnia: ``u`` poziomo (m), ``v`` pionowo w górę (m); okno [u0, v0, u1, v1] z marginesem."""

    def __init__(self, u0, v0, u1, v1, klasa="rys", tytul="", opis=""):
        self.u0, self.v0, self.u1, self.v1 = u0, v0, u1, v1
        self.klasa, self.tytul, self.opis = klasa, tytul, opis
        self.el: list[str] = []
        self.defs: list[str] = []

    # --- układ
    def X(self, u):
        return (u - self.u0) * S

    def Y(self, v):
        return (self.v1 - v) * S

    def pt(self, u, v):
        return f"{_n(self.X(u))} {_n(self.Y(v))}"

    # --- ścieżki
    def d_ring(self, coords) -> str:
        c = [tuple(q[:2]) for q in coords]
        if len(c) < 2:
            return ""
        zam = c[0] == c[-1]
        return "M" + " L".join(self.pt(u, v) for u, v in (c[:-1] if zam else c)) + ("Z" if zam else "")

    def d_geom(self, g) -> str:
        out = []
        for p in polys(g):
            out.append(self.d_ring(p.exterior.coords))
            out += [self.d_ring(i.coords) for i in p.interiors]
        return "".join(out)

    def d_line(self, coords) -> str:
        return "M" + " L".join(self.pt(u, v) for u, v in coords)

    # --- elementy
    def path(self, d: str, cls: str, extra: str = ""):
        if d:
            self.el.append(f'<path class="{cls}" d="{d}"{extra}/>')

    def geom(self, g, cls: str, extra: str = ""):
        self.path(self.d_geom(g), cls, extra)

    def line(self, coords, cls: str, extra: str = ""):
        self.path(self.d_line(coords), cls, extra)

    def rect(self, u0, v0, u1, v1, cls: str, extra: str = ""):
        x, y = self.X(min(u0, u1)), self.Y(max(v0, v1))
        w, h = abs(u1 - u0) * S, abs(v1 - v0) * S
        if w > 0.05 and h > 0.05:
            self.el.append(f'<rect class="{cls}" x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"{extra}/>')

    def text(self, u, v, txt: str, cls: str, anchor: str = "middle", dy: float = 0.0, extra: str = ""):
        self.el.append(f'<text class="{cls}" x="{_n(self.X(u))}" y="{_n(self.Y(v) + dy)}" '
                       f'text-anchor="{anchor}"{extra}>{escape(str(txt))}</text>')

    def raw(self, s: str):
        self.el.append(s)

    def svg(self, id_: str = "", aria: str = "", min_szer: int | None = None) -> str:
        w, h = (self.u1 - self.u0) * S, (self.v1 - self.v0) * S
        attrs = f' id="{id_}"' if id_ else ""
        style = f' style="min-width:{min_szer}px"' if min_szer else ""
        tit = f"<title>{escape(aria or self.tytul)}</title>" if (aria or self.tytul) else ""
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg class="{self.klasa}"{attrs} viewBox="0 0 {_n(w)} {_n(h)}" role="img" '
                f'aria-label="{escape(aria or self.tytul)}"{style} xmlns="http://www.w3.org/2000/svg">'
                f'{tit}{defs}{"".join(self.el)}</svg>')


def polys(g) -> list:
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        return [p for x in g.geoms for p in polys(x)]
    return []


def macierz(ark: Arkusz, c, ex, ey) -> str:
    """transform="matrix(...)" dla układu lokalnego: początek c (m), wersory ex (szerokość), ey (głębokość) —
    współrzędne lokalne w metrach."""
    a, b = S * ex[0], -S * ex[1]
    cc, d = S * ey[0], -S * ey[1]
    e, f = ark.X(c[0]), ark.Y(c[1])
    return f'matrix({a:.3f} {b:.3f} {cc:.3f} {d:.3f} {e:.1f} {f:.1f})'
