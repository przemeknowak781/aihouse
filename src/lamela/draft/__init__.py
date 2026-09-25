"""lamela.draft — silnik rysunkowy dokumentacji budowlanej (polska praktyka, PN / PN-EN ISO).

Model w METRACH (układ budynku) → rzutnie (Viewport) w podziałce 1:n → arkusz w MILIMETRACH (Sheet) →
DXF (R2018, model + layout z rzutniami), PDF wektorowy (dokładna skala), PNG (podgląd).

Szybki start::

    from lamela.draft import Sheet, TitleBlock, dims, symbols, hatch, elements
    sh = Sheet("A3", title_block=TitleBlock(tytul="RZUT PARTERU", skala="1:50", nr_rysunku="A-01"))
    vp = sh.add_viewport(50, "RZUT PARTERU")
    cs = elements.CutSet()
    elements.ring_layers(cs, [(0, 0), (6, 0), (6, 4), (0, 4)],
                         [("TYNK", .015, "wyk"), ("MUR_SILIKAT", .18, "konstr"), ("IZOL_TWARDA", .2, "izol")])
    cs.draw(vp)
    dims.dim_h(vp, [0, 6], y=-1.2, y_ref=-0.2)
    sh.place(vp, sh.frame[0] + 10, sh.frame[3] - 10, "tl")
    sh.view_title(vp)
    sh.save("wyniki/A-01")      # A-01.dxf, A-01.pdf, A-01.png
"""
from . import dims, elements, fmt, hatch, plot, render, styles, symbols
from .core import Canvas, PArc, PFill, PLine, PText, Viewport
from .sheet import Osoba, Sheet, TitleBlock, control_segment, fold_positions, notes_box, scale_bar, sheet_size, table

__all__ = [
    "Sheet", "TitleBlock", "Osoba", "Viewport", "Canvas", "PLine", "PArc", "PFill", "PText",
    "dims", "elements", "fmt", "hatch", "plot", "render", "styles", "symbols",
    "sheet_size", "fold_positions", "notes_box", "scale_bar", "table", "control_segment",
]
