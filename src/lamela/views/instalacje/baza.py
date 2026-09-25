"""Klasa bazowa rysunku instalacji na podkładzie: podkład, siatka tras, rejestr kolizji, legenda, braki danych,
opisy pomieszczeń, osie, uwagi — wspólne dla branż IS-* i IE-*."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from ...draft import symbols as S
from ...draft.geom import dir_deg, perp
from ..common import clean
from . import podklad as P
from .trasy import siatka_kondygnacji
from .wspolne import BRAK, H_S, InstResult, Legenda, braki_of, label_along, tag_leader, text_collisions


class Rysunek:
    br = "IS"                    # IS | IE (plik braków)
    kod = ""                     # np. IS-W

    def __init__(self, vp, ctx, W, kid, spec, opts):
        self.vp, self.ctx, self.W, self.kid, self.spec, self.opts = vp, ctx, W, kid, spec, dict(opts or {})
        self.m = ctx.model
        self.k = vp.k
        self.res = InstResult(north=True)
        self.leg = Legenda()
        self.nr = str(spec.get("nr", ""))
        self.notes: list[str] = []
        self.room_extra: dict = {}
        self.pod = None
        self.pl = None
        self.g = None
        self.kids = [k.id for k in self.m.kondygnacje]
        self.dach = str(kid).lower() == "dach"
        self.z_floor = self.m.kondygnacja(kid).rzedna if not self.dach else None

    # --------------------------------------------------------------------------------------------- podkład
    def podklad(self, meble=True, urzadzenia=False):
        if self.dach:
            self.pod = P.dach(self.vp, self.ctx)
        else:
            self.pod = P.rzut(self.vp, self.ctx, self.kid, meble=meble, urzadzenia=urzadzenia)
        self.pl = P.placer_for(self.vp, self.pod)
        self.leg.line("I-PODKLAD-SCIANY", "podkład architektoniczny (rzut AR — ściany przecięte, stolarka, "
                      "wyposażenie) — linie cienkie szare", pen=0.25)
        return self.pod

    def szachty(self):
        out = []
        for r in self.m.pomieszczenia(self.kid if not self.dach else self.kids[0]):
            if "szacht" in (r.nazwa or "").lower() and r.polygon is not None:
                out.append(r.polygon)
        return out

    def siatka(self, extra_pts=(), **kw):
        pts = np.array([p for p in extra_pts] or [[0, 0]], float)
        eb = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()) if len(extra_pts) else None
        self.g = siatka_kondygnacji(self.pod, eb, szachty=self.szachty(), **kw)
        return self.g

    # --------------------------------------------------------------------------------------------- pomocnicze
    def brak(self, element, opis, fmt_=""):
        braki_of(self.ctx).add(self.br, element, opis, fmt_, self.nr)

    def room_at(self, pt, kid=None, tol=0.3):
        kid = kid or self.kid
        p = Point(pt)
        best, d = None, 1e9
        for r in self.m.pomieszczenia(kid):
            if r.polygon is None:
                continue
            dd = r.polygon.distance(p)
            if dd < d:
                best, d = r, dd
        return best if d <= tol else None

    def reg(self, n0, w_text=1.0, w_line=0.5, w_fill=1.0):
        """Rejestruje prymitywy od indeksu n0 w module kolizji."""
        self.pl.add_prims(self.vp.prims[n0:], w_text=w_text, w_line=w_line, w_fill=w_fill)

    def pipe(self, path, medium, pen=None, lt=None, layer=None, color=None, reg=True):
        vp = self.vp
        n0 = len(vp.prims)
        ly, _d, lt0 = S.media(medium)
        vp.polyline(np.asarray(path, float), layer or ly, pen=pen, lt=lt if lt is not None else lt0, color=color)
        if reg:
            self.pl.add_lines(LineString([tuple(p) for p in path]), w=0.6)
        return n0

    def label(self, path, text, layer, h=H_S, color=None, **kw):
        return label_along(self.vp, self.pl, path, text, layer, h=h, color=color, **kw)

    def tag(self, anchor, lines, layer, h=H_S, color=None, **kw):
        return tag_leader(self.vp, self.pl, anchor, lines, layer, h=h, color=color, **kw)

    def sym(self, fn, *a, reg=True, **kw):
        n0 = len(self.vp.prims)
        fn(self.vp, *a, **kw)
        if reg:
            self.reg(n0, w_line=1.0)
        return n0

    def storey_name(self, kid=None):
        from ..sheets import storey_title
        kid = kid or self.kid
        return "RZUT DACHU" if str(kid).lower() == "dach" else storey_title(self.m, kid)

    def kond_above(self, kid=None):
        kid = kid or self.kid
        i = self.kids.index(kid)
        return self.kids[i + 1] if i + 1 < len(self.kids) else None

    def kond_below(self, kid=None):
        kid = kid or self.kid
        i = self.kids.index(kid)
        return self.kids[i - 1] if i > 0 else None

    # --------------------------------------------------------------------------------------------- zakończenie
    def finish(self, notes_extra=(), rooms=True):
        if rooms and not self.dach and self.pod is not None and self.pod.rooms:
            P.opisy_pomieszczen(self.vp, self.pl, self.ctx, self.pod, self.room_extra)
        P.osie(self.vp, self.ctx)
        self.res.column_blocks.insert(0, ("legenda", self.leg.block()))
        self.res.notes = list(self.notes) + list(notes_extra)
        self.res.kolizje = text_collisions(self.vp)
        if self.res.kolizje:
            self.ctx.note(f"arkusz {self.nr}", f"kolizje napisów: {self.res.kolizje}")
        return self.res
