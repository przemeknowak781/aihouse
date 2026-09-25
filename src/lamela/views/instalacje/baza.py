"""Klasa bazowa rysunku instalacji na podkładzie: podkład, siatka tras, rejestr kolizji, legenda, braki danych,
opisy pomieszczeń, osie, uwagi — wspólne dla branż IS-* i IE-*."""
from __future__ import annotations


import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import unary_union

from ...draft import symbols as S
from ...draft.geom import perp
from . import podklad as P
from .trasy import siatka_kondygnacji
from .wspolne import H_S, InstResult, Legenda, braki_of, label_along, tag_leader, text_collisions


ZRODLA_OZN = {
    "IS": "Oznaczenia instalacji sanitarnych — praktyka branżowa (PN-B-01410, PN-B-01411, PN-B-01430 — normy wycofane, "
          "bez następcy); armatura i urządzenia wg PN-EN ISO 10628-2 / PN-EN ISO 14617; rodzaje powietrza wg "
          "PN-EN 16798-3 (ODA, SUP, ETA, EHA). Obowiązuje legenda na arkuszu.",
    "IE": "Symbole instalacji elektrycznych wg IEC 60617 (baza IEC; PN-EN 60617 — wycofana, stosowana jako praktyka "
          "branżowa) i PN-EN ISO 14617; oznaczenia teletechniczne — praktyka branżowa. Obowiązuje legenda na arkuszu.",
}


class Rysunek:
    br = "IS"                    # IS | IE (plik braków)
    kod = ""                     # np. IS-W

    def __init__(self, vp, ctx, W, kid, spec, opts):
        self.vp, self.ctx, self.W, self.kid, self.spec, self.opts = vp, ctx, W, kid, spec, dict(opts or {})
        self.m = ctx.model
        self.k = vp.k
        self.res = InstResult(north=True)
        self.leg = Legenda(zrodlo=ZRODLA_OZN.get(self.br, ""))
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
        meble = bool(self.opts.get("meble", meble))
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

    def siatka(self, extra_pts=(), nieogrzewane: float = 0.0, **kw):
        pts = np.array([p for p in extra_pts] or [[0, 0]], float)
        eb = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max()) if len(extra_pts) else None
        self.g = siatka_kondygnacji(self.pod, eb, szachty=self.szachty(), **kw)
        if nieogrzewane and not self.dach:
            for r in self.m.pomieszczenia(self.kid):
                if r.polygon is not None and (r.raw.get("ogrzewane") is False or r.temp is None):
                    self.g.add(r.polygon.buffer(-0.02), add=nieogrzewane)
        return self.g

    # --------------------------------------------------------------------------------------------- dane modelu
    def obroty(self) -> dict:
        """(kond, x, y) → obrót przyboru/urządzenia (kierunek od ściany do pomieszczenia)."""
        out = {}
        d = self.W.dane
        for e in list(d.wyposazenie) + list(d.inst.get("przybory_dodatkowe") or []):
            if e.get("xy"):
                out[(str(e.get("kond", "P0")), round(float(e["xy"][0]), 3), round(float(e["xy"][1]), 3))] = \
                    float(e.get("obrot", 90.0))
        return out

    def obrot(self, kond, xy, default=90.0):
        if not hasattr(self, "_rot"):
            self._rot = self.obroty()
        return self._rot.get((str(kond), round(float(xy[0]), 3), round(float(xy[1]), 3)), default)

    def linie_dzialki(self, branza: str) -> list:
        """Projektowane uzbrojenie z ``dzialka.yaml`` (branża woda|kan_sanit|kan_deszcz|en|tele) w układzie budynku."""
        dz = self.W.dane.dzialka or {}
        D = dz.get("transform")
        out = []
        if D is None:
            return out
        for u in (dz.get("uzbrojenie") or {}).get("projektowane", []) or []:
            if u.get("branza") == branza and u.get("linia"):
                out.append((np.array(D.ring_bud(u["linia"]), float), u))
        return out

    def sciany_union(self, kids):
        key = ("sciany",) + tuple(kids)
        c = getattr(self.ctx, "_inst_geom", None)
        if c is None:
            c = self.ctx._inst_geom = {}
        if key not in c:
            c[key] = unary_union([w.polygon for kid in kids for w in self.m.sciany(kid) if w.polygon is not None])
        return c[key]

    def pion_punkty(self, pid, xy, kids, n=3, step=0.12, avoid=()):
        """Położenia n przewodów pionu obok punktu ``xy`` (np. Wz/Wc/Cyrk obok pionu kanalizacyjnego) — poza
        ścianami wszystkich kondygnacji pionu, ≥ 0,12 m od innych pionów; wynik wspólny dla wszystkich arkuszy."""
        c = getattr(self.ctx, "_inst_piony", None)
        if c is None:
            c = self.ctx._inst_piony = {}
        key = (pid, n)
        if key in c:
            return c[key]
        walls = self.sciany_union(kids).buffer(0.02)
        xy = np.asarray(xy, float)
        best = None
        for d in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            d = np.array(d, float)
            t = perp(d)
            for dist in (0.16, 0.22, 0.30):
                pts = [xy + d * dist + t * (i - (n - 1) / 2) * step for i in range(n)]
                sc = sum(10.0 for q in pts if walls.contains(Point(q))) + dist
                sc += sum(5.0 for q in pts for a in avoid if float(np.hypot(*(q - np.asarray(a)))) < 0.11)
                if best is None or sc < best[0]:
                    best = (sc, pts)
        c[key] = best[1]
        return best[1]

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

    def braki_wspolne(self):
        """Braki danych wspólne dla rysunków IS (piony bez rodzaju, trasy, dane wyrobów)."""
        if self.W.korekty:
            self.brak("instalacje.piony — rodzaj pionu", "lista pionów zawiera rury spustowe (RS…) bez pola `rodzaj`; "
                      "biblioteka grupowania pionów traktowała je jako piony wod.-kan. — w obliczeniach do rysunków "
                      "odfiltrowane", "piony: [{id, xy, rodzaj: kanalizacja|deszczowa|woda|co|wentylacja|teletechnika, "
                      "kond: [P0, …], opis}]")
        self.brak("Trasy przewodów (woda, kanalizacja, c.o., wentylacja)", "model nie zawiera przebiegów przewodów — "
                  "trasy wyznaczono algorytmicznie (ortogonalnie, przy ścianach, z pionów/rozdzielaczy do przyborów)",
                  "instalacje.trasy: [{medium: Wz|Wc|Cyrk|Ks|Z|P|SUP|ETA, kond, linia: [[x, y], …], dn, z}]")
        if not (self.W.dane.inst.get("wyroby") or {}):
            self.brak("instalacje.wyroby", "brak danych wyrobów (DTR/DWU) — obliczenia na danych przykładowych bibliotek "
                      "(PC, wodomierz ∆p(Q3), EA k_v, wpusty, centrala went., moduł PV, falownik)",
                      "wyroby: {PC: {P_A7W35, COP, SCOP_35, L_WA}, wodomierz: {DN, Q3, dp_Q3}, EA: {kv}, "
                      "centrala: {V_nom, eta_t, SFP}, PV: {modul: {...}, falownik: {...}}}")

    # --------------------------------------------------------------------------------------------- zakończenie
    def finish(self, notes_extra=(), rooms=True):
        rooms = rooms and bool(self.opts.get("opisy_pomieszczen", True))
        if rooms and not self.dach and self.pod is not None and self.pod.rooms:
            P.opisy_pomieszczen(self.vp, self.pl, self.ctx, self.pod, self.room_extra)
        P.osie(self.vp, self.ctx)
        self.res.column_blocks.insert(0, ("legenda", self.leg.block()))
        from ...draft import fmt
        self.res.units_note = (f"Średnice przewodów w mm (d_z×s — rury wielowarstwowe, Ø/DN — kanalizacja, kanały "
                               f"wentylacyjne), przekroje żył w mm², odległości i rzędne w m; ±0,000 = "
                               f"{fmt.level_abs(self.m.zero_abs)} m n.p.m. (PL-EVRF2007-NH).")
        self.res.notes = list(self.notes) + list(notes_extra)
        self.res.kolizje = text_collisions(self.vp)
        if self.res.kolizje:
            self.ctx.note(f"arkusz {self.nr}", f"kolizje napisów: {self.res.kolizje}")
        return self.res
