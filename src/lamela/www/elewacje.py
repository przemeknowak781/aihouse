"""Elewacje (rzut prostokątny brył IR, malarz, kolory materiałów z modelu) i przekroje (cięcie brył IR płaszczyzną
pionową z ``model/arkusze.yaml: przekroje`` albo ``views.section.auto_sections``) — inline SVG strony www."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import LineString

from .dane import fm
from .svg import Arkusz

POMIN = {"terrain", "vegetation", "context", "vehicle", "road", "fence", "furniture", "stair_step", "landing",
         "pavement", "railing"}
# strona: (u(x, y), głębokość(x, y) — mniejsza = bliżej widza, opis)
KIER = {
    "S": (lambda x, y: x, lambda x, y: y, "południowa (ogrodowa)"),
    "N": (lambda x, y: -x, lambda x, y: -y, "północna (od ulicy)"),
    "E": (lambda x, y: y, lambda x, y: -x, "wschodnia"),
    "W": (lambda x, y: -y, lambda x, y: x, "zachodnia"),
}


def _kolor(m, kod: str) -> str:
    mat = m.material(kod) if kod else None
    k = (mat.kolor if mat is not None else None) or (mat.raw.get("kolor") if mat is not None else None)
    return k or "#bdbdbd"


def _widoczny(m, p) -> bool:
    if p.kind in POMIN or p.meta.get("group") in ("otoczenie", "fundamenty", "teren"):
        return False
    if p.kind == "wall" and p.meta.get("wall"):
        w = m.sciana(p.meta["wall"])
        if w is not None and w.ext_side is None:
            return False
    if p.kind in ("door_leaf", "frame", "glass") and p.meta.get("opening"):
        o = m.otwor(p.meta["opening"])
        if o is not None and o.sciana is not None and o.sciana.ext_side is None:
            return False
    return True


def _poziomy(ark: Arkusz, D: dict, u_lab: float, z_top: float):
    for k in D["model"].kondygnacje:
        z = k.rzedna
        ark.line([(ark.u0 + 0.2, z), (ark.u1 - 0.2, z)], "lv")
        ark.text(u_lab, z, f"{k.id}  {'±' if abs(z) < 1e-6 else '+'}{fm(abs(z))}", "lv-t", anchor="start", dy=-8)
    ark.line([(ark.u0 + 0.2, z_top), (ark.u1 - 0.2, z_top)], "lv lv-top")
    ark.text(u_lab, z_top, f"+{fm(z_top)}", "lv-t", anchor="start", dy=-8)


def elewacja(D: dict, strona: str, okno_u: tuple, z_range: tuple) -> str:
    m, ir = D["model"], D["ir"]
    fu, fd, opis = KIER[strona]
    ark = Arkusz(okno_u[0], z_range[0], okno_u[1], z_range[1], klasa="rys rys-elew", tytul=f"Elewacja {opis}")
    items = []
    for p in ir.prisms:
        if not _widoczny(m, p) or p.z1 < -0.6:
            continue
        us = [fu(x, y) for x, y in p.polygon]
        ds = [fd(x, y) for x, y in p.polygon]
        items.append((min(ds), min(us), max(us), p))
    items.sort(key=lambda t: -t[0])
    z_top = max((t[3].z1 for t in items), default=0.0)
    for _d, u0, u1, p in items:
        if u1 - u0 < 1e-3 or p.z1 - p.z0 < 1e-3:
            continue
        if p.kind == "glass":
            ark.rect(u0, p.z0, u1, p.z1, "e-gl")
        else:
            cls = "e e-lam" if p.kind == "lamella" else "e"
            ark.rect(u0, max(p.z0, -0.6), u1, p.z1, cls, f' fill="{_kolor(m, p.material)}"')
    # teren wzdłuż lica (przed elewacją)
    if ir.terrain is not None:
        x0, y0, x1, y1 = m.bbox()
        if strona in ("S", "N"):
            yy = (y0 - 1.5) if strona == "S" else (y1 + 1.5)
            pts = [(fu(x, yy), ir.terrain.height_at(x, yy)) for x in np.linspace(x0 - 4, x1 + 4, 60)]
        else:
            xx = (x1 + 1.5) if strona == "E" else (x0 - 1.5)
            pts = [(fu(xx, y), ir.terrain.height_at(xx, y)) for y in np.linspace(y0 - 4, y1 + 4, 60)]
        pts.sort()
        poly = [(pts[0][0], z_range[0])] + pts + [(pts[-1][0], z_range[0]), (pts[0][0], z_range[0])]
        ark.path(ark.d_ring(poly), "gr")
        ark.line(pts, "gr-l")
    _poziomy(ark, D, okno_u[0] + 0.25, z_top)
    return ark.svg(id_=f"elew-{strona}", aria=f"Elewacja {opis}", min_szer=640)


def przekroje_def(m, arkusze: Path | None) -> list[dict]:
    """Płaszczyzny przekrojów z konfiguracji arkuszy PB (spójność z PAB), awaryjnie — automatyczne."""
    f = Path(arkusze) if arkusze else None
    if f and f.exists():
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        if raw.get("przekroje"):
            return list(raw["przekroje"])
    from ..views.section import auto_sections
    return auto_sections(m)


def przekroj(D: dict, sec: dict, z_range: tuple, margines: float = 3.0) -> str:
    """Przekrój: elementy przecięte (konstrukcja / izolacja / szkło — kolory z tokenów), widok za płaszczyzną
    (jasny, malarz), teren wzdłuż płaszczyzny, poziomy kondygnacji i wysokości w świetle z modelu."""
    m, ir = D["model"], D["ir"]
    big = 200.0
    if "x" in sec:
        c, ax = float(sec["x"]), "x"
        sgn = 1 if str(sec.get("patrz", "E")) == "E" else -1
        line = LineString([(c, -big), (c, big)])

        def U(x, y):
            return -y * sgn

        def dist(x, y):
            return (x - c) * sgn
    else:
        c, ax = float(sec["y"]), "y"
        sgn = 1 if str(sec.get("patrz", "N")) == "N" else -1
        line = LineString([(-big, c), (big, c)])

        def U(x, y):
            return x * sgn

        def dist(x, y):
            return (y - c) * sgn
    x0, y0, x1, y1 = m.bbox()
    us = [U(x, y) for x in (x0, x1) for y in (y0, y1)]
    ark = Arkusz(min(us) - margines, z_range[0], max(us) + margines, z_range[1], klasa="rys rys-prz",
                 tytul=f"Przekrój {sec.get('id', '')}-{sec.get('id', '')}")
    far, cut = [], []
    for p in ir.prisms:
        if p.kind in POMIN or p.meta.get("group") in ("otoczenie", "teren"):
            continue
        g = p.shape()
        if g.intersects(line):
            seg = g.intersection(line)
            for s in [seg] if seg.geom_type == "LineString" else [q for q in getattr(seg, "geoms", [])
                                                                   if q.geom_type == "LineString"]:
                vals = [U(*q) for q in s.coords]
                cut.append((min(vals), max(vals), p))
            continue
        ds = [dist(x, y) for x, y in p.polygon]
        if min(ds) > 0.001 and _widoczny(m, p):
            vals = [U(x, y) for x, y in p.polygon]
            far.append((min(ds), min(vals), max(vals), p))
    if ir.terrain is not None:
        ts = np.linspace(ark.u0 - 1, ark.u1 + 1, 120)
        pts = []
        for t in ts:
            xy = (c, -t * sgn) if ax == "x" else (t * sgn, c)
            pts.append((t, ir.terrain.height_at(*xy)))
        poly = [(pts[0][0], z_range[0])] + pts + [(pts[-1][0], z_range[0]), (pts[0][0], z_range[0])]
        ark.path(ark.d_ring(poly), "gr gr-prz")
    far.sort(key=lambda t: -t[0])
    for _d, u0, u1, p in far:
        ark.rect(u0, p.z0, u1, p.z1, "bey-gl" if p.kind == "glass" else "bey")
    for u0, u1, p in cut:
        if u1 - u0 < 1e-4:
            continue
        mat = m.material(p.material)
        fun = str((mat.raw if mat is not None else {}).get("funkcja") or "")
        if p.kind == "glass":
            cls = "ct-gl"
        elif p.kind == "insulation" or fun == "izolacja":
            cls = "ct-ins"
        elif p.kind in ("lamella", "frame", "door_leaf"):
            cls = "ct-fr"
        elif p.kind in ("terrace",):
            cls = "ct-ter"
        else:
            cls = "ct"
        ark.rect(u0, p.z0, u1, p.z1, cls)
    if ir.terrain is not None:
        ark.line(pts, "gr-l")
    z_top = max((p.z1 for _a, _b, p in cut + [(0, 0, q) for *_r, q in far]), default=0.0)
    _poziomy(ark, D, ark.u0 + 0.25, z_top)
    # wysokości w świetle kondygnacji (z modelu) — przy lewej krawędzi budynku w przekroju
    ub = min(u0 for u0, _u1, p in cut if p.kind == "wall") if any(p.kind == "wall" for *_x, p in cut) else ark.u0
    for k in m.kondygnacje:
        if k.wys_w_swietle:
            zc = k.rzedna + k.wys_w_swietle / 2
            ark.text(ub + 1.2, zc, f"h = {fm(k.wys_w_swietle)} m", "prz-h", anchor="start")
    sid = str(sec.get("id", ""))
    return ark.svg(id_=f"prz-{sid}", aria=f"Przekrój {sid}-{sid}", min_szer=640)
