"""Rdzeń silnika: prymitywy rysunkowe, płótna (arkusz w mm / rzutnia w metrach modelu) i rzutnie.

Zasada: geometria MODELU jest w metrach (układ budynku), arkusz jest w milimetrach. Rzutnia (``Viewport``)
przechowuje prymitywy we współrzędnych modelu i ma podziałkę 1:scale; wszystkie wielkości "papierowe"
(wysokość pisma, rozstaw kreskowania, długość kreski wymiarowej, średnica kółka osi…) przelicza się przez
``c.k`` = jednostki płótna na 1 mm papieru (arkusz: 1.0; rzutnia 1:50: 0.05 m/mm).

Dzięki temu każda funkcja symboli/wymiarów działa identycznie na arkuszu i w rzutni.
"""
from __future__ import annotations

import contextlib
import math
from dataclasses import dataclass, field
from typing import Iterable, Sequence

import numpy as np
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry

from . import styles, text as T
from .geom import Xf, arr, bbox_of, lines_of, polygons_of, rect_pts


# ================================================================================================ prymitywy
@dataclass(eq=False)
class Prim:
    layer: str
    pen: object = None        # rola pióra | mm | None (domyślna rola warstwy)
    lt: str | None = None     # rodzaj linii | None (wg warstwy)
    color: str | None = None  # '#rrggbb' | None (wg warstwy)
    z: float | None = None


@dataclass(eq=False)
class PLine(Prim):
    pts: np.ndarray = None
    closed: bool = False
    lt_scale: float = 1.0


@dataclass(eq=False)
class PArc(Prim):
    c: np.ndarray = None
    r: float = 0.0
    a0: float = 0.0
    a1: float = 360.0
    lt_scale: float = 1.0

    @property
    def full(self) -> bool:
        return abs((self.a1 - self.a0)) >= 360.0 - 1e-9


@dataclass(eq=False)
class PFill(Prim):
    rings: list = None        # [zewnętrzny, otwory...] (tablice punktów)
    fill: str = "#000000"


@dataclass(eq=False)
class PText(Prim):
    pos: np.ndarray = None
    runs: list = None         # [(tekst, wzgl. wysokość, wzgl. podniesienie)]
    h: float = 2.5            # wysokość wielkich liter [mm papieru]
    rot: float = 0.0          # stopnie
    ha: str = "left"
    va: str = "baseline"
    style: str = "normal"
    mask: float = 0.0         # >0: białe tło pod napisem z marginesem [mm]

    @property
    def string(self) -> str:
        return "".join(r[0] for r in self.runs)


def z_of(p: Prim) -> float:
    if p.z is not None:
        return p.z
    ld = styles.layer(p.layer)
    if isinstance(p, PText):
        return 30.0 + ld.z / 100.0
    if isinstance(p, PFill):
        return ld.z - 0.5
    return float(ld.z)


# ================================================================================================ płótno
class Canvas:
    """Wspólny interfejs rysowania (arkusz i rzutnie)."""

    paper: bool = False

    def __init__(self, scale: float, k: float):
        self.scale = float(scale)
        self.k = float(k)
        self.prims: list[Prim] = []
        self._layer = "0"

    # ------------------------------------------------------------------ narzędzia
    def mm(self, v: float) -> float:
        """Wielkość papierowa [mm] -> jednostki płótna."""
        return v * self.k

    def pen_mm(self, pen, layer: str) -> float:
        return styles.pen_mm(pen, self.scale, styles.layer(layer).role, paper=self.paper)

    @contextlib.contextmanager
    def on(self, layer: str):
        """Kontekst warstwy domyślnej: ``with c.on('A-OKNA'): c.line(...)``."""
        old = self._layer
        self._layer = layer
        try:
            yield self
        finally:
            self._layer = old

    def _ly(self, layer):
        return layer if layer is not None else self._layer

    def add(self, prim: Prim) -> Prim:
        self.prims.append(prim)
        return prim

    # ------------------------------------------------------------------ linie
    def line(self, p1, p2, layer=None, pen=None, lt=None, color=None, z=None, lt_scale=1.0):
        return self.add(PLine(self._ly(layer), pen, lt, color, z, arr([p1, p2]), False, lt_scale))

    def polyline(self, pts, layer=None, closed=False, pen=None, lt=None, color=None, z=None, lt_scale=1.0):
        a = arr(pts)
        if len(a) < 2:
            return None
        return self.add(PLine(self._ly(layer), pen, lt, color, z, a, closed, lt_scale))

    def polygon(self, pts, layer=None, **kw):
        return self.polyline(pts, layer, closed=True, **kw)

    def rect(self, x0, y0, x1, y1, layer=None, **kw):
        return self.polyline(rect_pts(x0, y0, x1, y1), layer, closed=True, **kw)

    def lines(self, segs, layer=None, pen=None, lt=None, color=None, z=None):
        """Wiele odcinków/łamanych naraz (np. kreskowanie)."""
        ly = self._ly(layer)
        for s in segs:
            a = arr(s)
            if len(a) >= 2:
                self.prims.append(PLine(ly, pen, lt, color, z, a, False, 1.0))

    def circle(self, c, r, layer=None, pen=None, lt=None, color=None, z=None):
        return self.add(PArc(self._ly(layer), pen, lt, color, z, np.asarray(c, float), float(r), 0.0, 360.0))

    def arc(self, c, r, a0, a1, layer=None, pen=None, lt=None, color=None, z=None):
        """Łuk CCW od a0 do a1 [stopnie]."""
        if a1 < a0:
            a1 += 360.0
        return self.add(PArc(self._ly(layer), pen, lt, color, z, np.asarray(c, float), float(r), float(a0), float(a1)))

    def geom(self, g: BaseGeometry, layer=None, pen=None, lt=None, color=None, z=None):
        """Rysuje obrysy/linie geometrii shapely."""
        for a in lines_of(g):
            closed = len(a) > 2 and np.allclose(a[0], a[-1])
            self.polyline(a[:-1] if closed else a, layer, closed=closed, pen=pen, lt=lt, color=color, z=z)

    # ------------------------------------------------------------------ wypełnienia
    def fill(self, shape, layer=None, color="#000000", z=None):
        """Wypełnienie jednolite: shapely (Multi)Polygon albo lista punktów."""
        if isinstance(shape, BaseGeometry):
            for pg in polygons_of(shape):
                rings = [np.asarray(pg.exterior.coords)[:-1]] + [np.asarray(i.coords)[:-1] for i in pg.interiors]
                self.add(PFill(self._ly(layer), None, None, None, z, rings, color))
        else:
            self.add(PFill(self._ly(layer), None, None, None, z, [arr(shape)], color))

    def dot(self, c, d_mm: float = 0.8, layer=None, color="#000000", z=None):
        """Kropka o średnicy d_mm [mm papieru] (np. zakończenie odnośnika)."""
        from .geom import circle_pts
        self.fill(circle_pts(c, self.mm(d_mm) / 2.0, 24), layer, color, z)

    # ------------------------------------------------------------------ napisy
    def text(self, pos, s, h=2.5, rot=0.0, ha="left", va="baseline", layer=None, style="normal", color=None,
             z=None, mask=0.0, runs=None):
        """Napis; h = wysokość wielkich liter [mm papieru]; rot w stopniach."""
        if runs is None:
            runs = [(str(s), 1.0, 0.0)]
        return self.add(PText(self._ly(layer), None, None, color, z, np.asarray(pos, float), list(runs), float(h),
                              float(rot), ha, va, style, float(mask)))

    def text_width(self, s: str, h: float = 2.5, style: str = "normal") -> float:
        """Szerokość napisu w jednostkach płótna."""
        return T.width(s, h, style) * self.k

    # ------------------------------------------------------------------ zasięg
    def extents(self, layers_excluded: Sequence[str] = ()):
        arrays = []
        for p in self.prims:
            if p.layer in layers_excluded:
                continue
            arrays.extend(prim_points(p, self.k))
        return bbox_of(arrays)


def text_items(p: PText, k: float):
    """Rozmieszczenie przebiegów napisu w układzie płótna.

    Zwraca (lista (xy, tekst, h_mm_papieru), obrys prostokąta napisu (4 punkty) w jednostkach płótna).
    """
    items, (W, top) = T.layout_runs(p.runs, p.h, p.style, p.ha, p.va)
    a = math.radians(p.rot)
    c, s = math.cos(a), math.sin(a)
    out = []
    for (x, y, st, hh) in items:
        X = p.pos[0] + (x * c - y * s) * k
        Y = p.pos[1] + (x * s + y * c) * k
        out.append((np.array([X, Y]), st, hh))
    # prostokąt (od linii bazowej - descent do góry wielkich liter)
    x0 = items[0][0] if items else 0.0
    y_base = items[0][1] if items else 0.0
    dsc = 0.22 * p.h
    loc = np.array([[x0, y_base - dsc], [x0 + W, y_base - dsc], [x0 + W, y_base + top], [x0, y_base + top]])
    if p.mask:
        m = p.mask
        loc = loc + np.array([[-m, -m], [m, -m], [m, m], [-m, m]])
    R = np.array([[c, -s], [s, c]])
    box = p.pos + (loc @ R.T) * k
    return out, box


def prim_points(p: Prim, k: float) -> list[np.ndarray]:
    if isinstance(p, PLine):
        return [p.pts]
    if isinstance(p, PFill):
        return [p.rings[0]]
    if isinstance(p, PArc):
        from .geom import arc_pts
        if p.full:
            return [np.array([[p.c[0] - p.r, p.c[1] - p.r], [p.c[0] + p.r, p.c[1] + p.r]])]
        return [arc_pts(p.c, p.r, p.a0, p.a1, 15)]
    if isinstance(p, PText):
        return [text_items(p, k)[1]]
    return []


# ================================================================================================ rzutnia
class Viewport(Canvas):
    """Rzutnia: fragment modelu (metry) pokazany na arkuszu w podziałce 1:scale.

    Po narysowaniu treści wywołaj ``sheet.place(vp, x, y, anchor)`` (dopasowanie do zawartości) lub podaj
    ``origin_model`` / ``origin_sheet`` / ``clip`` jawnie.
    """

    paper = False

    def __init__(self, scale: float, title: str | None = None, subtitle: str | None = None, name: str | None = None):
        super().__init__(scale, scale / 1000.0)
        self.title = title
        self.subtitle = subtitle
        self.name = name or (title or "RZUTNIA")
        self.origin_model = np.zeros(2)
        self.origin_sheet = np.zeros(2)
        self.clip: tuple | None = None   # (x0, y0, x1, y1) mm arkusza
        self._layer = "A-WIDOK"

    @property
    def xf(self) -> Xf:
        """Model [m] -> arkusz [mm]."""
        f = 1.0 / self.k
        return Xf(np.eye(2) * f, self.origin_sheet - self.origin_model * f)

    def to_sheet(self, pts) -> np.ndarray:
        return self.xf(pts)

    def to_model(self, pts) -> np.ndarray:
        return (arr(pts) - self.origin_sheet) * self.k + self.origin_model

    def set_window(self, model_bbox, sheet_xy, anchor: str = "bl"):
        """Pokazuje okno modelu (x0,y0,x1,y1 [m]) z narożnikiem ``anchor`` w punkcie arkusza ``sheet_xy``."""
        x0, y0, x1, y1 = model_bbox
        w = (x1 - x0) / self.k
        h = (y1 - y0) / self.k
        sx, sy = _anchor_origin(sheet_xy, w, h, anchor)
        self.origin_model = np.array([x0, y0])
        self.origin_sheet = np.array([sx, sy])
        self.clip = (sx, sy, sx + w, sy + h)

    def sheet_extents(self, pad_mm: float = 0.0):
        e = self.extents()
        if e is None:
            return None
        a = self.xf(np.array([[e[0], e[1]], [e[2], e[3]]]))
        return (a[0, 0] - pad_mm, a[0, 1] - pad_mm, a[1, 0] + pad_mm, a[1, 1] + pad_mm)


def _anchor_origin(xy, w, h, anchor):
    x, y = xy
    ax = {"l": 0.0, "c": 0.5, "r": 1.0}
    ay = {"b": 0.0, "m": 0.5, "t": 1.0}
    a = anchor.lower()
    va = a[0] if a[0] in "bmt" else "b"
    ha = a[1] if len(a) > 1 and a[1] in "lcr" else "l"
    return x - ax[ha] * w, y - ay[va] * h


# ================================================================================================ arkusz (baza)
class SheetBase(Canvas):
    """Arkusz: przestrzeń papieru [mm] + lista rzutni. Pełna funkcjonalność w ``sheet.Sheet``."""

    paper = True

    def __init__(self, width: float, height: float):
        super().__init__(1.0, 1.0)
        self.width = float(width)
        self.height = float(height)
        self.viewports: list[Viewport] = []
        self._layer = "R-OPISY"
        self.meta: dict = {}

    def add_viewport(self, scale: float, title: str | None = None, subtitle: str | None = None,
                     name: str | None = None) -> Viewport:
        vp = Viewport(scale, title, subtitle, name)
        self.viewports.append(vp)
        return vp

    def place(self, vp: Viewport, x: float, y: float, anchor: str = "tl", pad: float = 3.0,
              clip_model=None) -> Viewport:
        """Umieszcza rzutnię tak, by prostokąt jej zawartości (lub ``clip_model`` [m]) miał narożnik ``anchor``
        ('tl','tr','bl','br','mc'…) w punkcie (x, y) arkusza [mm]."""
        if clip_model is None:
            e = vp.extents()
            if e is None:
                raise ValueError("Pusta rzutnia")
            pm = pad * vp.k
            clip_model = (e[0] - pm, e[1] - pm, e[2] + pm, e[3] + pm)
        vp.set_window(clip_model, (x, y), anchor)
        return vp

    # wszystkie prymitywy z przekształceniami (dla rendererów)
    def iter_layers(self):
        yield None, self
        for vp in self.viewports:
            yield vp, vp
