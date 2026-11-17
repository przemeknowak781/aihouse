#!/usr/bin/env python3
"""Plansze Etapu I (opracowanie studialne) – 2 × 100×70 cm wg sugerowanego układu F.16.
Rysunki wstawiane w skali rzeczywistej (SVG w mm → szerokość w mm), wizualizacje jako pliki z docs/60_wizualizacje.
Wynik: build/plansze/etap1_P{1,2}.html/.pdf/.png  (podgląd PNG 3000 px; wersja 300 dpi przy eksporcie końcowym)
"""
import sys, re, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.board import Board, M, W, H, ACC, img, caption

OUT = ROOT / "build" / "plansze"
OUT.mkdir(parents=True, exist_ok=True)
R = "../rysunki/"
V = "../../docs/60_wizualizacje/img/"
TITLE = "BRAMA I LATARNIA"
MOTTO = "Siedziba Urzędu Marszałkowskiego i Sejmiku Województwa Dolnośląskiego · opracowanie studialne"


def svg_size(name):
    t = (ROOT / "build" / "rysunki" / name).read_text(encoding="utf-8")[:600]
    m = re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', t)
    return float(m.group(1)), float(m.group(2))


def drawing(name, scale_fit=None):
    w, h = svg_size(name)
    s = scale_fit or 1.0
    return f'<img src="{R}{name}" style="width:{w * s:.2f}mm;height:{h * s:.2f}mm;display:block">', w * s, h * s


def pick(*cands):
    for c in cands:
        if (ROOT / "docs" / "60_wizualizacje" / "img" / c).exists():
            return V + c
    return None


def label(num, title, sub=""):
    return (f'<div style="font-size:11pt;font-weight:600;letter-spacing:0.6pt;text-transform:uppercase">'
            f'<span style="color:{ACC};margin-right:2mm">{num}</span>{title}</div>'
            + (f'<div class="cap" style="margin-top:0.6mm">{sub}</div>' if sub else ""))


def board1():
    b = Board(1, 2, TITLE, MOTTO).header()
    top = M + 26
    # perspective 1 (F.17.A) – left top
    p1 = pick("W1_F17A_final.jpg", "photomatch_F17A_nakladka.jpg")
    b.add(M, top, 578, 376, img(p1))
    b.add(M, top + 378, 578, 12, label("1", "Perspektywa z lotu ptaka od wschodu", "na zdjęciu F.17.A; poza granicą opracowania stan istniejący"))
    # perspective 2 (F.17.B) – right top
    p2 = pick("W2_F17B_final.jpg", "photomatch_F17B_nakladka.jpg")
    b.add(612, top, 366, 262, img(p2))
    b.add(612, top + 264, 366, 12, label("2", "Perspektywa z lotu ptaka od zachodu", "na zdjęciu F.17.B"))
    # site plan 1:500 – right bottom
    sp, w, h = drawing("zagospodarowanie_1-500.svg")
    b.add(612 + (366 - w) / 2, 700 - M - h, w, h, sp)
    # equinox shading – left bottom (additional graphics)
    sh, w2, h2 = drawing("naslonecznienie.svg", 0.84)
    b.add(M, 700 - M - h2, w2, h2, sh)
    # section 1:500 – bottom middle
    sc, w3, h3 = drawing("przekroj_AA_1-500.svg", 1.0)
    b.add(M + 254, 700 - M - h3 - 6, w3, h3, sc)
    b.add(M + 254 + 40, 700 - M - 6, 240, 8, label("3", "Przekrój charakterystyczny A-A 1:500", ""))
    return b


def board2():
    b = Board(2, 2, TITLE, MOTTO).header()
    top = M + 26
    # plans 1:500 – 7 levels, 4 × 2 grid (left top)
    ids = ["-2", "-1", "P", "1", "5", "6", "S"]
    x0, y0 = M, top
    for i, lid in enumerate(ids):
        d, w, h = drawing(f"rzut_bloki_{lid}_1-500.svg")
        cx = x0 + (i % 4) * 146
        cy = y0 + (i // 4) * 196
        b.add(cx, cy, w, h, d)
    b.add(x0 + 3 * 146 + 4, y0 + 196 + 6, 138, 60, label("4", "Rzuty kondygnacji 1:500", "bloki funkcjonalne i ich powierzchnie netto (PN-ISO 9836); kondygnacje 1–4 o jednakowym układzie na jednym rzucie, z rozmieszczeniem departamentów")
          + '<div style="margin-top:3mm;font-size:9pt">N ↑ · skala 1:500</div>')
    # perspective 3 (bridge) – right top
    p3 = pick("W10_most_final.jpg", "budynek_test_W9.jpg", "budynek_test_W10.jpg")
    b.add(612, top, 366, 300, img(p3))
    b.add(612, top + 302, 366, 12, label("5", "Perspektywa 3 – sylweta wieży Sejmiku w kontekście Mostu Grunwaldzkiego", ""))
    # elevations 1:500 – left bottom
    e1, we, he = drawing("elewacja_E_1-500.svg")
    e2, ww, hw = drawing("elewacja_W_1-500.svg")
    ye = top + 2 * 196 + 6
    b.add(M, ye, we, he, e1)
    b.add(M + we + 8, ye, ww, hw, e2)
    b.add(M, ye + he + 2, 578, 10, label("6", "Rozwinięcia elewacyjne 1:500 – Wybrzeże J. Słowackiego (z budynkiem nr 5) i ul. Mazowiecka (z budynkiem nr 19)", ""))
    # axonometry – right bottom (diagram, fitted)
    ax_w, ax_h = svg_size("aksonometria_funkcjonalna.svg")
    s = min(366 / ax_w, 300 / ax_h)
    a, w4, h4 = drawing("aksonometria_funkcjonalna.svg", s)
    b.add(612 + (366 - w4) / 2, 700 - M - h4, w4, h4, a)
    return b


def render(b, name):
    html = OUT / f"{name}.html"
    b.save(html)
    js = ROOT / "tools" / "plansze" / "html2pdf.js"
    subprocess.run(["node", str(js), str(html), str(OUT / f"{name}.pdf"), "1000", "700", "--png", str(OUT / f"{name}.png"), "--pngw", "3000"],
                   check=True, cwd=str(ROOT / "tools" / "plansze"), capture_output=True)
    return OUT / f"{name}.png"


if __name__ == "__main__":
    print(render(board1(), "etap1_P1"))
    print(render(board2(), "etap1_P2"))
