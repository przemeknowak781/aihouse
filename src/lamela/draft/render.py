"""Renderer PDF (wektorowy, dokładna podziałka) i PNG (podgląd) — matplotlib + PyMuPDF.

* Rozmiar strony PDF = format arkusza [mm] (1 mm = 72/25,4 pt), oś figury pokrywa całą stronę — skala wydruku
  jest więc dokładna (1 m w 1:100 = 10,0 mm).
* Grubości linii w mm → pt; wzory linii w mm (niezależne od grubości: ``lines.scale_dashes = False``).
* Czcionki TrueType osadzane (``pdf.fonttype = 42``) — napisy wyszukiwalne, poprawne polskie znaki.
* PNG powstaje przez rasteryzację PDF (PyMuPDF) — podgląd jest identyczny z PDF.
"""
from __future__ import annotations

import math
from pathlib import Path as FsPath

import matplotlib
import numpy as np
from matplotlib.backends.backend_pdf import FigureCanvasPdf, PdfPages
from matplotlib.collections import LineCollection, PathCollection
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path

from . import styles, text as T
from .core import PArc, PFill, PLine, PText, text_items, z_of
from .geom import arc_pts

MM2PT = 72.0 / 25.4
RC = {
    "pdf.fonttype": 42,
    "lines.scale_dashes": False,
    "path.simplify": False,
    "pdf.compression": 6,
    "axes.unicode_minus": False,
}


def _aci_rgb(aci: int) -> str:
    try:
        from ezdxf.colors import aci2rgb
        r, g, b = aci2rgb(aci)
        if (r, g, b) in ((255, 255, 255),):
            return "#000000"
        return "#%02x%02x%02x" % (r, g, b)
    except Exception:  # pragma: no cover
        return "#000000"


def prim_color(p, mode: str) -> str:
    if p.color:
        return p.color
    ld = styles.layer(p.layer)
    if mode == "mono":
        return "#000000"
    if mode == "screen":
        return _aci_rgb(ld.aci)
    return ld.plot_rgb or "#000000"


def dash_pts(lt_name: str | None, layer: str, lt_scale: float = 1.0):
    name = lt_name or styles.layer(layer).linetype
    lt = styles.LINETYPES.get(name)
    if lt is None or not lt.pattern:
        return None
    seq = []
    for x in lt.pattern:
        v = abs(x) * lt_scale * MM2PT
        if x == 0:
            v = 0.001
        seq.append(v)
    return (0.0, tuple(seq))


class _Ctx:
    def __init__(self, ax, mode):
        self.ax = ax
        self.mode = mode
        self.clips = {}

    def clip_patch(self, clip):
        if clip is None:
            return None
        key = tuple(round(c, 4) for c in clip)
        if key not in self.clips:
            x0, y0, x1, y1 = clip
            self.clips[key] = Rectangle((x0, y0), x1 - x0, y1 - y0, transform=self.ax.transData,
                                        facecolor="none", edgecolor="none")
        return self.clips[key]


def _xf_pts(xf, pts):
    return pts if xf is None else xf(pts)


def build_figure(sheet, mode: str = "branze") -> Figure:
    """Buduje figurę matplotlib odwzorowującą arkusz 1:1 (jednostki danych = mm)."""
    W, H = sheet.width, sheet.height
    with matplotlib.rc_context(RC):
        fig = Figure(figsize=(W / 25.4, H / 25.4), dpi=72)
        fig.patch.set_facecolor("white")
        ax = fig.add_axes((0, 0, 1, 1))
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.set_axis_off()
        ctx = _Ctx(ax, mode)

        items = []
        order = 0
        for vp, canvas in sheet.iter_layers():
            xf = vp.xf if vp is not None else None
            clip = vp.clip if vp is not None else None
            for p in canvas.prims:
                if not styles.layer(p.layer).plot:
                    continue
                z = z_of(p)
                if isinstance(p, PText) and p.mask > 0:
                    _items, box = text_items(p, canvas.k)
                    items.append((z - 0.05, order, PFill(p.layer, rings=[box], fill="#ffffff"), xf, clip, canvas))
                    order += 1
                items.append((z, order, p, xf, clip, canvas))
                order += 1
        items.sort(key=lambda t: (t[0], t[1]))

        batch = []   # linie o wspólnym stylu
        bkey = None

        def flush():
            nonlocal batch, bkey
            if not batch:
                return
            lw, color, dash, clip = bkey
            lc = LineCollection(batch, linewidths=lw * MM2PT, colors=color, capstyle="round", joinstyle="round",
                                antialiaseds=True)
            if dash is not None:
                lc.set_linestyle(dash)
            cp = ctx.clip_patch(clip)
            if cp is not None:
                lc.set_clip_path(cp)
            ax.add_collection(lc)
            batch = []
            bkey = None

        for z, _o, p, xf, clip, canvas in items:
            if isinstance(p, (PLine, PArc)):
                lw = canvas.pen_mm(p.pen, p.layer)
                color = prim_color(p, mode)
                dash = dash_pts(p.lt, p.layer, p.lt_scale)
                if isinstance(p, PLine):
                    pts = p.pts
                    if p.closed:
                        pts = np.vstack([pts, pts[:1]])
                else:
                    if p.full:
                        pts = arc_pts(p.c, p.r, 0.0, 360.0, 3.0)
                    else:
                        pts = arc_pts(p.c, p.r, p.a0, p.a1, 3.0)
                pts = _xf_pts(xf, pts)
                key = (round(lw, 4), color, dash, clip)
                if key != bkey:
                    flush()
                    bkey = key
                batch.append(pts)
            elif isinstance(p, PFill):
                flush()
                verts, codes = [], []
                for ring in p.rings:
                    r = _xf_pts(xf, ring)
                    if len(r) < 3:
                        continue
                    verts.extend(r.tolist())
                    verts.append(r[0].tolist())
                    codes.extend([Path.MOVETO] + [Path.LINETO] * (len(r) - 1) + [Path.CLOSEPOLY])
                if not verts:
                    continue
                color = p.fill if p.fill else prim_color(p, mode)
                patch = PathPatch(Path(verts, codes), facecolor=color, edgecolor="none", linewidth=0,
                                  antialiased=True)
                cp = ctx.clip_patch(clip)
                if cp is not None:
                    patch.set_clip_path(cp)
                ax.add_patch(patch)
            elif isinstance(p, PText):
                flush()
                runs, _box = text_items(p, canvas.k)
                color = prim_color(p, mode)
                for xy, s, hh in runs:
                    if not s:
                        continue
                    q = _xf_pts(xf, xy.reshape(1, 2))[0]
                    fp = FontProperties(fname=T.font_file(p.style), size=T.em_mm(hh, p.style) * MM2PT)
                    t = ax.text(q[0], q[1], s, fontproperties=fp, rotation=p.rot, rotation_mode="anchor",
                                ha="left", va="baseline", color=color)
                    cp = ctx.clip_patch(clip)
                    if cp is not None:
                        t.set_clip_path(cp)
        flush()
    return fig


def to_pdf(sheet, path, mode: str = "branze", title: str | None = None) -> str:
    fig = build_figure(sheet, mode)
    meta = {"Title": title or sheet.meta.get("title", "Rysunek"), "Creator": "lamela.draft",
            "Subject": sheet.meta.get("subject", "")}
    with matplotlib.rc_context(RC):
        FigureCanvasPdf(fig)
        fig.savefig(str(path), format="pdf", metadata=meta)
    return str(path)


def pdf_to_png(pdf_path, png_path, dpi: int = 200, page: int = 0) -> str:
    import pymupdf
    doc = pymupdf.open(str(pdf_path))
    pix = doc[page].get_pixmap(dpi=dpi, alpha=False)
    pix.set_dpi(dpi, dpi)
    pix.save(str(png_path))
    doc.close()
    return str(png_path)


def to_png(sheet, path, dpi: int = 200, mode: str = "branze") -> str:
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        tmp = f.name
    to_pdf(sheet, tmp, mode)
    pdf_to_png(tmp, path, dpi)
    FsPath(tmp).unlink(missing_ok=True)
    return str(path)


def sheets_to_pdf(sheets, path, mode: str = "branze", title: str | None = None) -> str:
    """Tom: wiele arkuszy (różne formaty) w jednym pliku PDF."""
    with matplotlib.rc_context(RC):
        with PdfPages(str(path), metadata={"Title": title or "Tom rysunków", "Creator": "lamela.draft"}) as pdf:
            for sh in sheets:
                fig = build_figure(sh, mode)
                FigureCanvasPdf(fig)
                pdf.savefig(fig)
    return str(path)
