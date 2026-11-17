"""Competition board composer — HTML/CSS at exact physical size (1000×700 mm, landscape, white background).

Design system (from docs/50_research/plansze_metodyka.md):
  * margins 22 mm; 12-column grid, gutter 8 mm; baseline 5 mm
  * typography: Inter Display (titles, light/regular), Inter (text); sizes: board title 42 pt, section 20 pt,
    body 11–12 pt (legible from ~1.5 m), captions 9.5 pt; numbers tabular
  * colour: warm black #1d1b18 text, one accent (terracotta #a8483a) for numbering & key lines; drawings monochrome
  * every board: top band with board number (1/8 … 8/8), board title, small motto; NO author identification (anonymity)
Usage: Board(n, total, title).add(html_block_at(x_mm, y_mm, w_mm, h_mm, inner_html)) → .html() → html2pdf.js
"""
from __future__ import annotations
import html as _h
from pathlib import Path

W, H, M = 1000.0, 700.0, 22.0
COLS, GUT = 12, 8.0
ACC = "#a8483a"
INK = "#1d1b18"

CSS = f"""
@page {{ size: {W}mm {H}mm; margin: 0 }}
html, body {{ margin: 0; padding: 0; background: #ffffff; }}
.board {{ width: {W}mm; height: {H}mm; position: relative; overflow: hidden; background: #fff; color: {INK};
          font-family: 'Inter', 'DejaVu Sans', sans-serif; font-feature-settings: 'tnum' 1, 'ss01' 1; }}
.blk {{ position: absolute; box-sizing: border-box; }}
.num {{ font-family: 'Inter Display', 'Inter'; font-weight: 300; font-size: 54pt; letter-spacing: -1pt; color: {ACC}; line-height: 1; }}
.btitle {{ font-family: 'Inter Display', 'Inter'; font-weight: 400; font-size: 30pt; letter-spacing: -0.3pt; line-height: 1.05; }}
.motto {{ font-family: 'Inter Display', 'Inter'; font-weight: 300; font-size: 15pt; color: #57524b; line-height: 1.25; }}
h2 {{ font-family: 'Inter Display', 'Inter'; font-weight: 500; font-size: 17pt; margin: 0 0 3mm 0; letter-spacing: 0.1pt; }}
h2 .k {{ color: {ACC}; font-weight: 600; margin-right: 2mm; }}
h3 {{ font-family: 'Inter'; font-weight: 600; font-size: 11.5pt; margin: 0 0 1.5mm 0; text-transform: uppercase; letter-spacing: 0.8pt; }}
p, li {{ font-size: 11.5pt; line-height: 1.42; margin: 0 0 2.2mm 0; }}
.small, .small p, .small li {{ font-size: 9.6pt; line-height: 1.38; }}
.cap {{ font-size: 9.6pt; color: #4d4842; line-height: 1.3; margin-top: 1.8mm; }}
.cap b {{ color: {INK}; font-weight: 600; }}
.rule {{ position: absolute; height: 0; border-top: 0.6mm solid {INK}; }}
.rule.thin {{ border-top-width: 0.25mm; }}
.img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.imgc {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
table.t {{ border-collapse: collapse; width: 100%; font-size: 9.6pt; }}
table.t td, table.t th {{ border-bottom: 0.2mm solid #cfcac2; padding: 1.1mm 1.5mm; text-align: left; vertical-align: top; }}
table.t th {{ font-weight: 600; border-bottom: 0.4mm solid {INK}; }}
table.t td.r, table.t th.r {{ text-align: right; }}
.tag {{ display: inline-block; font-size: 9pt; font-weight: 600; color: #fff; background: {ACC}; padding: 0.4mm 1.6mm; border-radius: 0.6mm; margin-right: 1.5mm; }}
"""


def col_x(c):
    """x [mm] of the left edge of column c (0-based)."""
    cw = (W - 2 * M - (COLS - 1) * GUT) / COLS
    return M + c * (cw + GUT)


def col_w(n):
    cw = (W - 2 * M - (COLS - 1) * GUT) / COLS
    return n * cw + (n - 1) * GUT


class Board:
    def __init__(self, n, total, title, motto=""):
        self.n, self.total, self.title, self.motto = n, total, title, motto
        self.blocks = []

    def add(self, x, y, w, h, inner, cls="", style=""):
        self.blocks.append(f'<div class="blk {cls}" style="left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm;height:{h:.2f}mm;{style}">{inner}</div>')
        return self

    def rule(self, x, y, w, thin=False):
        self.blocks.append(f'<div class="rule{" thin" if thin else ""}" style="left:{x:.2f}mm;top:{y:.2f}mm;width:{w:.2f}mm"></div>')
        return self

    def header(self):
        # board number + title band (no author info)
        self.add(M, M - 4, 60, 22, f'<div class="num">{self.n}<span style="font-size:22pt;color:#9a948c">/{self.total}</span></div>')
        self.add(M + 62, M - 1, 520, 20, f'<div class="btitle">{_h.escape(self.title)}</div>')
        if self.motto:
            self.add(W - M - 330, M, 330, 20, f'<div class="motto" style="text-align:right">{_h.escape(self.motto)}</div>')
        self.rule(M, M + 19.5, W - 2 * M)
        return self

    def html(self):
        return ('<!doctype html><html lang="pl"><head><meta charset="utf-8"><style>' + CSS + '</style></head><body><div class="board">'
                + "".join(self.blocks) + "</div></body></html>")

    def save(self, path):
        Path(path).write_text(self.html(), encoding="utf-8")
        return path


def img(src, contain=False):
    return f'<img class="{"imgc" if contain else "img"}" src="{_h.escape(str(src))}">'


def caption(num, title, text=""):
    return f'<div class="cap"><b>{_h.escape(str(num))} {_h.escape(title)}</b>{" — " + _h.escape(text) if text else ""}</div>'
