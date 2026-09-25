"""Symbole wyposażenia (model/wyposazenie.yaml) do rzutów marketingowych — układ lokalny elementu:
x wzdłuż szerokości (−w/2…w/2), y w głąb pomieszczenia (−d/2 = strona ściany … +d/2), metry."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString

from .svg import Arkusz, _n, macierz


def _r(x0, y0, x1, y1, cls="", rx=0.0):
    k = f' class="{cls}"' if cls else ""
    r = f' rx="{rx:.3f}"' if rx else ""
    return (f'<rect{k} x="{min(x0, x1):.3f}" y="{min(y0, y1):.3f}" width="{abs(x1 - x0):.3f}" '
            f'height="{abs(y1 - y0):.3f}"{r}/>')


def _c(x, y, r, cls=""):
    k = f' class="{cls}"' if cls else ""
    return f'<circle{k} cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}"/>'


def _e(x, y, rx, ry, cls=""):
    k = f' class="{cls}"' if cls else ""
    return f'<ellipse{k} cx="{x:.3f}" cy="{y:.3f}" rx="{rx:.3f}" ry="{ry:.3f}"/>'


def _l(x0, y0, x1, y1, cls=""):
    k = f' class="{cls}"' if cls else ""
    return f'<line{k} x1="{x0:.3f}" y1="{y0:.3f}" x2="{x1:.3f}" y2="{y1:.3f}"/>'


def symbol(typ: str, w: float, d: float, it: dict) -> list[str]:
    """Elementy SVG symbolu w układzie lokalnym (y lokalne = głębokość; ściana przy y = −d/2)."""
    a, b = w / 2, d / 2
    out = [_r(-a, -b, a, b, "fb", 0.02)]
    if typ == "lozko":
        n = 2 if w >= 1.3 else 1
        pw = (w - 0.1 * (n + 1)) / n
        for i in range(n):
            x0 = -a + 0.1 + i * (pw + 0.1)
            out.append(_r(x0, -b + 0.06, x0 + pw, -b + 0.34, "fd", 0.05))
        out.append(_l(-a, -b + 0.5, a, -b + 0.5, "fl"))
        out.append(_l(-a, -b + 0.5, -a + min(0.45, w / 3), -b + 0.8, "fl"))
    elif typ == "sofa":
        out.append(_r(-a, -b, a, -b + 0.22, "fd"))
        out += [_r(-a, -b, -a + 0.18, b, "fd"), _r(a - 0.18, -b, a, b, "fd")]
        n = max(2, round((w - 0.36) / 0.8))
        for i in range(1, n):
            x = -a + 0.18 + i * (w - 0.36) / n
            out.append(_l(x, -b + 0.22, x, b, "fl"))
    elif typ == "stol":
        n = int(it.get("krzesla") or 0)
        per = max(1, n // 2)
        for s in (-1, 1):
            for i in range(per):
                x = -a + (i + 0.5) * w / per
                y0 = s * (b + 0.08)
                out.append(_r(x - 0.22, y0, x + 0.22, y0 + s * 0.42, "fd", 0.06))
        out.append(_r(-a, -b, a, b, "fb", 0.02))
    elif typ in ("wyspa", "blat_wyspa"):
        out.append(_l(-a + 0.04, -b + 0.04, a - 0.04, -b + 0.04, "fl"))
    elif typ == "plyta":
        for sx in (-1, 1):
            for sy in (-1, 1):
                out.append(_c(sx * a / 2, sy * b / 2, min(a, b) / 2.6, "fl"))
    elif typ == "zlew":
        out.append(_r(-a + 0.07, -b + 0.08, a - 0.07, b - 0.06, "fl", 0.06))
        out.append(_c(0, -b + 0.14, 0.025, "fl"))
    elif typ in ("wc",):
        out = [_r(-a, -b, a, -b + 0.17, "fb", 0.02), _e(0, 0.06, a * 0.9, b * 0.62, "fb")]
    elif typ in ("umywalka", "umywalka_blat"):
        n = 2 if w >= 1.1 else 1
        for i in range(n):
            x = -a + (i + 0.5) * w / n
            out.append(_e(x, 0.02, min(0.24, w / n / 2 - 0.06), b * 0.6, "fl"))
    elif typ == "prysznic":
        out += [_l(-a, -b, a, b, "fl"), _l(-a, b, a, -b, "fl"), _c(0, 0, 0.04, "fd")]
    elif typ == "wanna":
        out.append(_r(-a + 0.06, -b + 0.06, a - 0.06, b - 0.06, "fl", 0.25))
        out.append(_c(-a + 0.25, 0, 0.03, "fd"))
    elif typ == "szafa":
        out.append(_l(-a, 0, a, 0, "fl"))
        out.append(_l(-a, -b, a, b, "fh"))
    elif typ == "biurko":
        out.append(_r(-0.22, b + 0.05, 0.22, b + 0.47, "fd", 0.08))
    elif typ in ("pralka", "suszarka"):
        out.append(_c(0, 0.03, min(a, b) * 0.66, "fl"))
    elif typ == "zasobnik":
        out = [_c(0, 0, min(a, b), "fb")]
    elif typ in ("lodowka", "rekuperator", "pompa_ciepla", "urzadzenie", "zmywarka"):
        out += [_l(-a, -b, a, b, "fh"), _l(-a, b, a, -b, "fh")]
    return out


def rysuj(ark: Arkusz, it: dict):
    """Dodaje element wyposażenia do arkusza rzutu (grupa <g class="fu"> z macierzą lokalną)."""
    typ = str(it.get("typ"))
    if typ == "blat" and it.get("linia"):
        g = LineString(it["linia"]).buffer(float(it.get("gl", 0.6)) * float(it.get("strona", 1)), single_sided=True,
                                           cap_style=2)
        ark.geom(g, "fu-blat")
        return
    if not it.get("xy") or not it.get("wym"):
        return
    w, d = (float(q) for q in it["wym"])
    ang = math.radians(float(it.get("obrot", 0)))
    ey = np.array([math.cos(ang), math.sin(ang)])          # od ściany do pomieszczenia
    ex = np.array([ey[1], -ey[0]])                          # wzdłuż ściany
    c = np.asarray(it["xy"], float) + (0 if typ in ("stol", "wyspa", "plyta") else ey * d / 2)
    tt = f"<title>{it.get('opis') or typ}</title>" if it.get("opis") else ""
    ark.raw(f'<g class="fu" transform="{macierz(ark, c, ex, ey)}">{tt}{"".join(symbol(typ, w, d, it))}</g>')


__all__ = ["rysuj", "symbol", "_n"]
