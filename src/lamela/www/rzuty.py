"""Rzuty kondygnacji w wersji marketingowej (inline SVG) z modelu: przekrój poziomy IR na +1,10 nad posadzką
(ściany: konstrukcja/wykończenie + izolacja osobnym tonem), stolarka, drzwi z łukiem otwierania (kierunek i strona
z ``otwory[].otwieranie``), schody, tarasy, płyty nad cięciem (kreska), pomieszczenia (kategoria PN-ISO 9836,
numer, nazwa, pow. netto) i wyposażenie z ``wyposazenie.yaml``."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import Point, Polygon
from shapely.ops import polylabel, unary_union

from . import meble
from .dane import fm
from .svg import Arkusz, polys

CIECIE = 1.10
POMIN = {"terrain", "vegetation", "context", "vehicle", "road", "pavement", "fence", "furniture", "door_leaf"}


def zasieg(m, margines: float = 1.3) -> tuple:
    """Wspólne okno wszystkich rzutów (ta sama skala przy przełączaniu kondygnacji)."""
    g = [m.obrys_kondygnacji(k.id) for k in m.kondygnacje]
    g += [Polygon(t["obrys"]) for t in m.tarasy() if t.get("obrys")]
    g += [Polygon(w["obrys"]) for w in m.wsporniki() if w.get("obrys")]
    x0, y0, x1, y1 = unary_union(g).bounds
    return x0 - margines, y0 - margines - 0.6, x1 + margines, y1 + margines


def _drzwi(ark: Arkusz, m, o, pokoje):
    """Skrzydło + łuk: strona otwierania jak w lamela.views.plan (zewn.: do wnętrza/na zewn.; wewn.: do
    „głębszego” pomieszczenia), zawias wg ``otwieranie.strona``."""
    w = o.sciana
    ow = o.otwieranie or {}
    if ow.get("przesuwne") or str(ow.get("rodzaj", "")).startswith("przesuw"):
        return
    kier = str(ow.get("kierunek", "do_wewn"))
    mid = (o.s0 + o.s1) / 2
    if w.ext_side is not None:
        into = w.sgn_int
    else:
        def ile_drzwi(r):
            return sum(1 for q in m.otwory(kond=o.kond) if q.typ in ("drzwi", "otwor", "drzwi_zewn") and
                       any(r.polygon.buffer(0.05).contains(Point(*q.sciana.pt((q.s0 + q.s1) / 2, t)))
                           for t in (q.sciana.t_max + 0.35, q.sciana.t_min - 0.35)))

        def at(t):
            P = Point(*w.pt(mid, t))
            return next((r for r in pokoje if r.polygon is not None and r.polygon.buffer(0.02).contains(P)), None)
        rp, rm = at(w.t_max + 0.35), at(w.t_min - 0.35)

        def score(r):
            return (9, 9, 0.0) if r is None else (ile_drzwi(r), 1 if r.kategoria == "ruchu" else 0, r.pow_netto)
        into = 1 if score(rp) <= score(rm) else -1
    sw = into if kier != "na_zewn" else -into
    f = -w.n * sw
    left = np.array([-f[1], f[0]])
    on_b = (w.u @ left) > 0
    if str(ow.get("strona", "lewa")) == "prawa":
        on_b = not on_b
    t_face = w.face_t(sw, "all") if w.ext_side is None else w.face_t(sw, "k")
    s_h, s_o = (o.s1, o.s0) if on_b else (o.s0, o.s1)
    H = w.pt(s_h, t_face)
    L = abs(o.s1 - o.s0)
    tip = H + w.n * sw * L
    Oth = w.pt(s_o, t_face)
    n = 12
    a0 = np.arctan2(*(tip - H)[::-1])
    a1 = np.arctan2(*(Oth - H)[::-1])
    da = (a1 - a0 + np.pi) % (2 * np.pi) - np.pi
    arc = [H + L * np.array([math.cos(a0 + da * i / n), math.sin(a0 + da * i / n)]) for i in range(n + 1)]
    ark.line([tuple(H), tuple(tip)], "dr-skrz")
    ark.line([tuple(p) for p in arc], "dr-luk")


def rzut(D: dict, kid: str, okno: tuple) -> dict:
    m, ir = D["model"], D["ir"]
    k = m.kondygnacja(kid)
    zc = k.rzedna + CIECIE
    ark = Arkusz(*okno, klasa="rys rys-rzut", tytul=f"Rzut: {k.nazwa}")
    pokoje = [r for r in m.pomieszczenia(kid) if r.polygon is not None]
    # tarasy i podesty (parter), płyty poniżej cięcia
    if kid == m.kondygnacje[0].id:
        for t in m.tarasy():
            ark.geom(Polygon(t["obrys"]), "ter")
    # pomieszczenia — wypełnienie wg kategorii
    for r in pokoje:
        ark.geom(r.polygon, f"rm rm-{r.kategoria}")
    # schody i spoczniki poniżej/powyżej cięcia
    for p in ir.prisms:
        if p.level == kid and p.kind in ("stair_step", "landing"):
            ark.geom(p.shape(), "st" if p.z1 <= zc + 0.02 else "st st-nad")
    for it in D["wyposazenie"]:
        if str(it.get("kond")) == kid:
            meble.rysuj(ark, it)
    # przekrój poziomy
    wal, ins, lam, gl, fr = [], [], [], [], []
    for p, g in ir.section(zc):
        if p.kind in POMIN or p.meta.get("group") == "otoczenie":
            continue
        if p.kind == "glass":
            gl.append(g)
        elif p.kind in ("frame",):
            fr.append(g)
        elif p.kind == "lamella":
            lam.append(g)
        elif p.kind == "insulation" or (p.kind == "wall" and p.meta.get("klasa") == "izolacja"):
            ins.append(g)
        elif p.kind in ("wall", "column", "parapet", "beam", "railing"):
            wal.append(g)
    for lst, cls in ((ins, "ins"), (wal, "wal"), (lam, "lam"), (gl, "gl"), (fr, "fr")):
        if lst:
            ark.geom(unary_union([q.buffer(0) for q in lst]), cls)
    for o in m.otwory(kond=kid):
        if o.typ in ("drzwi", "drzwi_zewn") and o.sciana is not None:
            try:
                _drzwi(ark, m, o, pokoje)
            except Exception:  # noqa: BLE001 — pojedynczy symbol nie blokuje rysunku
                pass
    # obrysy płyt i brył nad płaszczyzną cięcia
    for sl in m.plyty():
        if k.rzedna + 1.2 < sl["spod"] < k.rzedna + (k.wys_kondygnacji or 3.0) + 0.4 and \
                sl["typ"] in ("wspornik", "dach", "strop"):
            g = sl["poly_full"].difference(m.obrys_kondygnacji(kid).buffer(0.01))
            for q in polys(g):
                if q.area > 0.3:
                    ark.geom(q, "nad")
    _opisy(ark, pokoje)
    _polnoc_skala(ark)
    return dict(svg=ark.svg(id_=f"rzut-{kid}", aria=f"Rzut kondygnacji {k.nazwa} z umeblowaniem", min_szer=680),
                pokoje=[r.id for r in pokoje])


def _punkt_opisu(r) -> Point:
    pt = r.raw.get("punkt")
    g = max(polys(r.polygon), key=lambda q: q.area)
    if pt and g.buffer(-0.25).contains(Point(pt)):
        return Point(pt)
    try:
        return polylabel(g, tolerance=0.02)
    except Exception:  # noqa: BLE001
        return g.representative_point()


def _opisy(ark: Arkusz, pokoje):
    """Numer (+ nazwa i pow. netto, jeśli pomieszczenie ma miejsce na opis) — pełna lista w zestawieniu obok."""
    for r in pokoje:
        c = _punkt_opisu(r)
        g = max(polys(r.polygon), key=lambda q: q.area)
        x0, y0, x1, y1 = g.bounds
        duzy = r.pow_netto >= 6.0 and (x1 - x0) >= 1.9 and (y1 - y0) >= 1.3
        if duzy:
            ark.raw(f'<g class="lb" data-pom="{r.id}">')
            ark.text(c.x, c.y, r.id, "lb-nr", dy=-14)
            nazwa = r.nazwa.split("(")[0].strip()
            ark.text(c.x, c.y, nazwa, "lb-nz", dy=12)
            ark.text(c.x, c.y, f"{fm(r.pow_netto)} m²", "lb-pw", dy=36)
            ark.raw("</g>")
        elif r.pow_netto >= 0.8:
            ark.raw(f'<g class="lb lb-m" data-pom="{r.id}">')
            ark.text(c.x, c.y, r.id, "lb-nr", dy=8)
            ark.raw("</g>")


def _polnoc_skala(ark: Arkusz):
    """Strzałka północy (oś y modelu = północ, azymut osi y z modelu uwzględniany przez orientację rysunku) i podziałka
    liniowa 0–5 m w prawym dolnym narożu okna."""
    u, v = ark.u1 - 1.0, ark.v0 + 0.9
    ark.raw(f'<g class="an" aria-hidden="true">')
    ark.path(f"M{ark.pt(u, v + 1.2)} L{ark.pt(u - 0.28, v + 0.35)} L{ark.pt(u, v + 0.52)} L{ark.pt(u + 0.28, v + 0.35)}Z",
             "an-n")
    ark.text(u, v, "N", "an-t", dy=0)
    x0 = ark.u1 - 7.4
    for i in range(5):
        ark.rect(x0 + i, v + 0.1, x0 + i + 1, v + 0.28, "an-s" + (" an-s2" if i % 2 else ""))
    for i in (0, 1, 5):
        ark.text(x0 + i, v - 0.28, f"{i}", "an-t2")
    ark.text(x0 + 5.35, v - 0.28, "m", "an-t2", anchor="start")
    ark.raw("</g>")
