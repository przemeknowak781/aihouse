"""Zapis arkusza do DXF (AutoCAD R2018) — model w metrach + arkusz (layout) w mm z rzutniami VIEWPORT.

* Model (Model space): treść każdej rzutni we współrzędnych budynku [m] (INSUNITS = 6). Rzutnia nr 1 leży
  w miejscu rzeczywistym; kolejne (np. detale w innej skali, z adnotacjami w swojej skali) są przesunięte
  w prawo o pełny zasięg poprzednich + 20 m (patrz ``vp_offsets``).
* Arkusz (Paper space, layout "Arkusz_<nr>"): ramka, tabliczka, legendy w mm; rzutnie VIEWPORT
  z podziałką 1:scale (view_height = wys. rzutni [mm] × scale / 1000).
* Rodzaje linii zdefiniowane w mm papieru; encje modelu mają indywidualny współczynnik skali rodzaju linii
  ``ltscale = scale/1000`` (PSLTSCALE=0), dzięki czemu kreski mają właściwą długość i w modelu, i na wydruku.
* Grubości linii zapisywane jawnie przy encjach (wartości z szeregu ISO) — warstwy mają grubości domyślne.
* Napisy: TEXT ze stylem TrueType Arial (Liberation Sans jest metrycznie zgodna — układ zgodny z PDF),
  indeksy górne wymiarów jako osobne encje TEXT.
* ``mode='flat'``: wszystko w przestrzeni papieru w mm (bez rzutni) — do prostego podglądu/wymiany.
"""
from __future__ import annotations

import math

import ezdxf
import numpy as np
from ezdxf import colors as ezcolors
from ezdxf.enums import TextEntityAlignment

from . import styles
from .core import PArc, PFill, PLine, PText, text_items

_LW_VALID = [0, 5, 9, 13, 15, 18, 20, 25, 30, 35, 40, 50, 53, 60, 70, 80, 90, 100, 106, 120, 140, 158, 200, 211]


def _lw(mm: float) -> int:
    v = int(round(mm * 100))
    return min(_LW_VALID, key=lambda x: abs(x - v))


def _rgb(hexs: str):
    h = hexs.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _setup_doc(doc):
    for lt in styles.LINETYPES.values():
        if not lt.pattern or lt.name in doc.linetypes:
            continue
        pat = [lt.period] + [float(x) for x in lt.pattern]
        doc.linetypes.add(lt.name, pattern=pat, description=lt.description)
    for key, name in styles.DXF_TEXT_STYLES.items():
        if name not in doc.styles:
            doc.styles.add(name, font=styles.DXF_FONTS[key])
    for ld in styles.LAYERS.values():
        if ld.name in doc.layers:
            continue
        lay = doc.layers.add(ld.name, color=ld.aci, linetype=ld.linetype if ld.linetype in doc.linetypes else "Continuous",
                             lineweight=_lw(styles.pen_mm(ld.role, 100)))
        if ld.plot_rgb:
            lay.rgb = _rgb(ld.plot_rgb)
        if not ld.plot:
            lay.dxf.plot = 0
        try:
            lay.description = ld.description
        except Exception:
            pass


def _ensure_layer(doc, name):
    if name not in doc.layers:
        ld = styles.layer(name)
        doc.layers.add(name, color=ld.aci, lineweight=_lw(styles.pen_mm(ld.role, 100)))


def _attribs(doc, p, canvas, ltscale):
    _ensure_layer(doc, p.layer)
    a = {"layer": p.layer, "lineweight": _lw(canvas.pen_mm(p.pen, p.layer))}
    if p.lt:
        a["linetype"] = p.lt if p.lt in doc.linetypes else "Continuous"
    lts = ltscale * getattr(p, "lt_scale", 1.0)
    if abs(lts - 1.0) > 1e-12:
        a["ltscale"] = lts
    if p.color:
        a["true_color"] = ezcolors.rgb2int(_rgb(p.color))
    return a


def _emit(doc, space, canvas, off, ltscale, text_only_paper=False):
    ox, oy = off
    for p in canvas.prims:
        if isinstance(p, PLine):
            pts = p.pts + (ox, oy)
            a = _attribs(doc, p, canvas, ltscale)
            e = space.add_lwpolyline(pts.tolist(), format="xy", close=p.closed, dxfattribs=a)
            if p.lt or styles.layer(p.layer).linetype != "CIAGLA":
                e.dxf.flags = e.dxf.flags | 128  # PLINEGEN: ciągłość wzoru linii na wierzchołkach
        elif isinstance(p, PArc):
            a = _attribs(doc, p, canvas, ltscale)
            c = (p.c[0] + ox, p.c[1] + oy)
            if p.full:
                space.add_circle(c, p.r, dxfattribs=a)
            else:
                space.add_arc(c, p.r, p.a0 % 360.0, p.a1 % 360.0 if (p.a1 % 360.0) != (p.a0 % 360.0) else p.a0 + 360.0,
                              dxfattribs=a)
        elif isinstance(p, PFill):
            _ensure_layer(doc, p.layer)
            h = space.add_hatch(dxfattribs={"layer": p.layer})
            h.set_solid_fill(color=7, style=0, rgb=_rgb(p.fill or "#000000"))
            for i, ring in enumerate(p.rings):
                r = ring + (ox, oy)
                h.paths.add_polyline_path(r.tolist(), is_closed=True,
                                          flags=1 if i == 0 else 0)
        elif isinstance(p, PText):
            _ensure_layer(doc, p.layer)
            runs, box = text_items(p, canvas.k)
            if p.mask > 0:
                h = space.add_hatch(dxfattribs={"layer": "A-MASKA" if canvas.paper is False else p.layer})
                h.set_solid_fill(color=7, style=0, rgb=(255, 255, 255))
                h.paths.add_polyline_path((box + (ox, oy)).tolist(), is_closed=True)
            for xy, s, hh in runs:
                if not s:
                    continue
                a = {"layer": p.layer, "height": hh * canvas.k, "rotation": p.rot,
                     "style": styles.DXF_TEXT_STYLES.get(p.style, "PL_ARIAL")}
                if p.color:
                    a["true_color"] = ezcolors.rgb2int(_rgb(p.color))
                t = space.add_text(s, dxfattribs=a)
                t.set_placement((xy[0] + ox, xy[1] + oy), align=TextEntityAlignment.LEFT)


def vp_offsets(sheet, gap: float = 20.0):
    """Przesunięcia treści rzutni w przestrzeni modelu (pierwsza rzutnia bez przesunięcia)."""
    offs = []
    xmax = None
    for i, vp in enumerate(sheet.viewports):
        e = vp.extents()
        if e is None:
            offs.append((0.0, 0.0))
            continue
        if i == 0 or xmax is None:
            off = (0.0, 0.0)
        else:
            off = (xmax + gap - e[0], 0.0)
        offs.append(off)
        xr = e[2] + off[0]
        xmax = xr if xmax is None else max(xmax, xr)
    return offs


def to_dxf(sheet, path, mode: str = "layout", layout_name: str | None = None) -> str:
    doc = ezdxf.new("R2018", setup=False)
    doc.header["$INSUNITS"] = 6 if mode == "layout" else 4
    doc.header["$MEASUREMENT"] = 1
    doc.header["$LTSCALE"] = 1.0
    doc.header["$PSLTSCALE"] = 0
    doc.header["$LWDISPLAY"] = 1
    doc.header["$DWGCODEPAGE"] = "ANSI_1250"
    _setup_doc(doc)
    msp = doc.modelspace()

    if mode == "flat":
        # wszystko w mm arkusza w przestrzeni modelu
        _emit(doc, msp, sheet, (0.0, 0.0), 1.0)
        for vp in sheet.viewports:
            from .core import Canvas
            flat = Canvas(1.0, 1.0)
            flat.paper = True
            xf = vp.xf
            for p in vp.prims:
                q = _transform_prim(p, xf, vp)
                if q is not None:
                    flat.prims.append(q)
            # piór nie zmieniamy: grubości wg podziałki rzutni
            flat.pen_mm = vp.pen_mm  # type: ignore
            flat.k = 1.0
            _emit(doc, msp, flat, (0.0, 0.0), 1.0)
        doc.saveas(str(path))
        return str(path)

    psp = doc.layouts.get("Layout1")
    name = layout_name or ("Arkusz " + str(sheet.meta.get("nr", ""))).strip()
    try:
        doc.layouts.rename("Layout1", name)
    except Exception:
        pass
    psp = doc.layouts.get(name)
    psp.page_setup(size=(sheet.width, sheet.height), margins=(0, 0, 0, 0), units="mm", offset=(0, 0),
                   rotation=0, scale=1)
    # usuń domyślną rzutnię główną tworzoną przez page_setup (zostaje wymagana rzutnia nr 1)
    _emit(doc, psp, sheet, (0.0, 0.0), 1.0)
    offs = vp_offsets(sheet)
    for vp, off in zip(sheet.viewports, offs):
        _emit(doc, msp, vp, off, vp.k)
        if vp.clip is None:
            continue
        x0, y0, x1, y1 = vp.clip
        w, h = x1 - x0, y1 - y0
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        mc = vp.to_model([[cx, cy]])[0] + off
        v = psp.add_viewport(center=(cx, cy), size=(w, h), view_center_point=(mc[0], mc[1]),
                             view_height=h * vp.k, dxfattribs={"layer": "R-RZUTNIA"})
        try:
            v.dxf.flags = v.dxf.flags | 16384  # zablokowana skala (display locked)
        except Exception:
            pass
    doc.saveas(str(path))
    return str(path)


def _transform_prim(p, xf, vp):
    import copy
    q = copy.copy(p)
    s = 1.0 / vp.k
    if isinstance(p, PLine):
        q.pts = xf(p.pts)
    elif isinstance(p, PFill):
        q.rings = [xf(r) for r in p.rings]
    elif isinstance(p, PArc):
        q.c = xf(p.c.reshape(1, 2))[0]
        q.r = p.r * s
    elif isinstance(p, PText):
        q.pos = xf(p.pos.reshape(1, 2))[0]
    return q
