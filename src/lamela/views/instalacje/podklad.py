"""Podkład architektoniczny rzutów instalacji: rzut AR z ``plan.PlanBuilder`` (bez opisów, wymiarów i kreskowań)
przerysowany cienko na szaro na warstwach ``I-PODKLAD*`` (osobne warstwy DXF — do wyłączenia w CAD), wypełnienie
ścian przeciętych jasnoszare, osie konstrukcyjne i własne (zwięzłe) opisy pomieszczeń.

Rzuty AR nie są modyfikowane — generator rzutu jest uruchamiany z wyłączoną metodą ``annotate`` na kopii rzutni."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from ...draft import symbols as S
from ...draft.core import PArc, PFill, PLine, PText, Viewport
from ..common import Placer, clean, label_point, room_label
from .wspolne import H_M, H_S

KEEP_STRUCT = {"A-SCIANY-KONSTR", "A-STROPY", "A-FUNDAMENTY", "A-SCIANY-DZIAL"}
KEEP_LAYERS = {"A-SCIANY-IZOL", "A-SCIANY-WYK", "A-WARSTWY", "A-IZOL-WODNA"}
KEEP_VIEW = {"A-OKNA", "A-DRZWI", "A-WIDOK", "A-NAD-CIECIEM", "A-NIEWIDOCZNE", "A-SCHODY", "A-SYMBOLE"}
DROP = {"A-KRESKOWANIE", "A-WYMIARY", "A-OPISY", "A-POMIESZCZENIA", "A-OSIE", "A-PRZEKROJE", "A-RZEDNE", "A-MASKA"}


@dataclass
class Podklad:
    kid: str | None
    z_floor: float = 0.0
    cut_region: object = None          # ściany/słupy przecięte (bez otworów)
    struct: object = None              # warstwy konstrukcyjne
    outline: object = None             # obrys kondygnacji (lico zewnętrzne)
    rooms: list = field(default_factory=list)
    walls: list = field(default_factory=list)
    pb: object = None                  # PlanBuilder (pomocniczo: strona otwierania drzwi)
    extent: tuple | None = None


def _restyle(prims, scale, meble=True, urzadzenia=False, widok=0.13):
    out = []
    w_k = 0.25 if scale <= 50 else 0.18
    for p in prims:
        ly = p.layer
        if ly in DROP or isinstance(p, PText):
            continue
        if ly == "S-URZADZENIA" and not urzadzenia:
            continue
        if ly == "A-MEBLE" and not meble:
            continue
        q = copy.copy(p)
        from ...draft import styles
        if q.lt is None and not isinstance(q, PFill):
            lt0 = styles.layer(ly).linetype
            q.lt = None if lt0 == "CIAGLA" else lt0
        if isinstance(q, PFill):
            q.layer = "I-PODKLAD-WYPELN"
            q.fill = "#cfcfcf" if q.fill.lower() in ("#000000", "#000") else ("#ffffff" if q.fill.lower() in (
                "#ffffff", "#fff") else "#e0e0e0")
            q.color = None
        elif ly in KEEP_STRUCT:
            q.layer, q.pen, q.color = "I-PODKLAD-SCIANY", w_k, None
        elif ly in KEEP_LAYERS:
            q.layer, q.pen, q.color = "I-PODKLAD-SCIANY", 0.13, None
        elif ly in ("A-OKNA", "A-DRZWI", "A-SANITARNE"):
            q.layer, q.pen, q.color = "I-PODKLAD", 0.18 if isinstance(q, PLine) else 0.13, None
        elif ly == "A-MEBLE":
            q.layer, q.pen, q.color = "I-PODKLAD", 0.13, "#b8b8b8"
        else:
            q.layer, q.pen, q.color = "I-PODKLAD", widok, ("#777777" if widok > 0.13 else None)
        out.append(q)
    return out


def _cache(ctx) -> dict:
    c = getattr(ctx, "_inst_podklad", None)
    if c is None:
        c = {}
        ctx._inst_podklad = c
    return c


def rzut(vp, ctx, kid: str, meble: bool = True, urzadzenia: bool = False) -> Podklad:
    """Rysuje podkład rzutu kondygnacji ``kid`` do ``vp``; zwraca geometrię pomocniczą (obszar ścian, pomieszczenia)."""
    from ..plan import PlanBuilder
    key = ("rzut", kid, vp.scale)
    cache = _cache(ctx)
    if key not in cache:
        tmp = Viewport(vp.scale, "podklad")
        pb = PlanBuilder(tmp, ctx, kid, {"wymiary_wewnetrzne": False, "opisy_nad": False})
        pb.annotate = lambda: None          # podkład: bez wymiarów, opisów pomieszczeń i stolarki, osi, przekrojów
        pb.run()
        cache[key] = (tmp.prims, pb)
    prims, pb = cache[key]
    pod = Podklad(kid, pb.z_floor, pb.cut_region, pb.struct, pb.outline, pb.rooms, pb.cut_walls, pb)
    if not pb.cut_region.is_empty:
        vp.fill(pb.cut_region, "I-PODKLAD-WYPELN", "#e4e4e4", z=3)
    vp.prims.extend(_restyle(prims, vp.scale, meble=meble, urzadzenia=urzadzenia))
    pod.extent = vp.extents()
    return pod


def dach(vp, ctx) -> Podklad:
    """Podkład rzutu dachu (widok z góry z usuwaniem linii niewidocznych — ``plan.draw_roof_plan``)."""
    from ..plan import draw_roof_plan
    key = ("dach", vp.scale)
    cache = _cache(ctx)
    if key not in cache:
        tmp = Viewport(vp.scale, "podklad")
        draw_roof_plan(tmp, ctx, {})
        cache[key] = tmp.prims
    prims = [p for p in cache[key] if p.layer not in ("A-SYMBOLE",)]
    vp.prims.extend(_restyle(prims, vp.scale, meble=False, widok=0.18))
    m = ctx.model
    outl = unary_union([m.obrys_kondygnacji(k.id) for k in m.kondygnacje])
    pod = Podklad(None, 0.0, Polygon(), Polygon(), clean(outl), [], [], None)
    pod.extent = vp.extents()
    return pod


def placer_for(vp, pod: Podklad) -> Placer:
    """Rejestr kolizji z podkładem: ściany przecięte (obszar), linie podkładu (niska waga — napisy mogą je
    przecinać, ale preferowane są miejsca wolne)."""
    pl = Placer(vp.k)
    if pod.cut_region is not None and not pod.cut_region.is_empty:
        pl.add(pod.cut_region, "area", 0.8)
    pl.add_prims([p for p in vp.prims if isinstance(p, (PLine, PArc)) and p.layer == "I-PODKLAD"], w_line=0.12)
    return pl


def opisy_pomieszczen(vp, placer, ctx, pod: Podklad, extra: dict | None = None, skip=()):
    """Opisy pomieszczeń: numer (PN-B-01025, pogrubiony) + nazwa + wiersze dodatkowe branży (np. temperatura,
    strumień powietrza). Umieszczane po treści instalacji — w miejscu o najmniejszej kolizji w obrysie pomieszczenia."""
    extra = extra or {}
    mode = ctx.opt("numeracja_pomieszczen", "iso")
    for r in sorted(pod.rooms, key=lambda r: -r.pow_netto):
        if r.id in skip:
            continue
        pg = r.polygon
        nm = r.nazwa if len(r.nazwa) <= 26 else r.nazwa[:25].rstrip() + "…"
        num = room_label(ctx.model, r.id, mode)
        c = label_point(pg)
        bounds = pg.buffer(-0.02)
        for lines in ([num, nm] + list(extra.get(r.id, [])), [num] + list(extra.get(r.id, [])), [num]):
            if pg.area < 1.0 and len(lines) > 1:
                continue
            pos = _room_block(vp, placer, c, lines, bounds, last=(len(lines) == 1))
            if pos is not None:
                break


def _room_block(vp, placer, c, lines, bounds, last=False):
    from ...draft import text as T
    k = vp.k
    hs = [H_M] + [H_S] * (len(lines) - 1)
    lh = [h * 1.6 * k for h in hs]
    Htot = sum(lh)
    cands = [tuple(c)]
    for r in (2.5, 5.0, 8.0, 12.0, 17.0, 23.0):
        for j in range(12):
            a = 2 * np.pi * j / 12
            q = (c[0] + np.cos(a) * r * k, c[1] + np.sin(a) * r * k)
            if bounds.contains(Point(q)):
                cands.append(q)

    def fn(cv, q):
        y = q[1] + Htot / 2
        for i, (s, h) in enumerate(zip(lines, hs)):
            y -= lh[i]
            cv.text((q[0], y + 0.3 * h * k), s, h, 0.0, "center", "baseline", "I-POMIESZCZENIA",
                    style="bold" if i == 0 else "normal", mask=0.3)
            if i == 0:
                w = T.width(s, h, "bold") * k
                cv.line((q[0] - w / 2, y + 0.3 * h * k - 0.6 * k), (q[0] + w / 2, y + 0.3 * h * k - 0.6 * k),
                        "I-POMIESZCZENIA", pen=0.18)
    pos, cost = placer.place(vp, fn, cands, penalty_step=0.01, bounds=bounds, max_cost=None if last else 3.0)
    return pos


def osie(vp, ctx, ext=None, off_mm: float = 9.0, r_mm: float = 3.5, zakres: bool = False):
    """Osie konstrukcyjne z modelu (linia punktowa, kółka z oznaczeniem u dołu i z lewej strony rysunku).
    ``zakres`` — tylko osie przecinające narysowaną treść (± 0,35 m, jak na rzutach AR ``plan._axes``); bez tego
    osie całego budynku (np. osie garażu na rzucie II piętra poszerzają rzutnię o pusty pas)."""
    m = ctx.model
    k = vp.k
    e = ext or vp.extents()
    if e is None:
        return
    x0, y0, x1, y1 = e
    ax = (getattr(m, "osie", None) or {})
    tol = 0.35

    def _w(v, a, b):
        return not zakres or a - tol <= v <= b + tol
    for nm, x in (ax.get("x") or {}).items():
        if not _w(x, x0, x1):
            continue
        S.axis_line(vp, (x, y0 - off_mm * k), (x, y1 + 2.0 * k), str(nm), bubbles="start", r_mm=r_mm, h=H_M,
                    layer="I-OSIE")
    for nm, y in (ax.get("y") or {}).items():
        if not _w(y, y0, y1):
            continue
        S.axis_line(vp, (x0 - off_mm * k, y), (x1 + 2.0 * k, y), str(nm), bubbles="start", r_mm=r_mm, h=H_M,
                    layer="I-OSIE")
