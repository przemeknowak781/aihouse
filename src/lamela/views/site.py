"""Generator rysunków PROJEKTU ZAGOSPODAROWANIA DZIAŁKI (PZT) — typy widoków rejestrowane w ``lamela.views.sheets``:

* ``pzt_plan``        — PLAN ZAGOSPODAROWANIA DZIAŁKI (1:500) na podkładzie mapy do celów projektowych (tu SYNTETYCZNEJ,
  rysowanej z ``dzialka.yaml``), obrys budynku, odległości od granic, linia zabudowy, komunikacja, zieleń, retencja,
  PC ze strefą R290, ogrodzenie, przyłącza; kolumna: legenda, tabela wskaźników MPZP (liczona z modelu — shapely),
  odległości od granic (WT § 12), obszar oddziaływania,
* ``pzt_szczegoly``   — PLAN SZCZEGÓŁOWY — WYMIARY I RZĘDNE (1:200): wymiary i odległości (0,01 m), rzędne terenu
  istniejącego/projektowanego, spadki, kierunki spływu, odwodnienie, punkty tyczenia (wykaz współrzędnych),
* ``pzt_uzbrojenie``  — RYSUNEK KOORDYNACYJNY UZBROJENIA TERENU (1:200/1:250): sieci istniejące i projektowane (kolory
  i litery wg mapy zasadniczej), obiekty, odległości między sieciami i od budynku/drzew, skrzyżowania, kolizje.

Opcje widoku (``opcje`` w konfiguracji arkusza — wszystkie opcjonalne):
``okno: [x0, y0, x1, y1]`` (układ działki), ``margines`` [m], ``linia_plyt: PUNKTOWA|KRESKOWA``,
``pikiety_co`` [m] (PZT-01: min. odstęp opisywanych rzędnych mapy), ``warstwice: true``,
``warstwice_projektowane: false``, ``mpzp: {...}`` (limity, gdy brak w modelu), ``odleglosci_min: {"e-t": [0.5, "źródło"]}``,
``retencja_min: {budynek: 3.0, granica: 2.0, drzewo: 1.0}``, ``podklad: true`` (PZT-01), ``zielen: true``.
Konfiguracja arkuszy: ``model/arkusze_pzt.yaml``; CLI: ``tools/generuj_widoki.py --arkusze model/arkusze_pzt.yaml``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import nearest_points, unary_union

from ..draft import fmt
from ..draft.core import Viewport
from . import site_draw as D
from .sheets import register_view
from .site_data import (BRANZE, SiteData, koordynacja, linia_zabudowy_spr, odleglosci, opaska, punkty_tyczenia,
                        wskazniki)

UNITS = "Wymiary i odległości w m (dokładność 0,01 m), rzędne w m n.p.m. (PL-EVRF2007-NH)."
MAPA_TXT = ("PODKŁAD PRZYKŁADOWY — mapa do celów projektowych fikcyjna [DANE PRZYKŁADOWE – FIKCYJNE], narysowana "
            "z modelu działki (dzialka.yaml); w projekcie rzeczywistym — aktualna mapa do celów projektowych "
            "wg art. 34 ust. 3 pkt 1 PB (z klauzulą urzędową lub oświadczeniem geodety — art. 34b PB), treść "
            "i opis mapy wg § 32–33 rozp. w sprawie standardów technicznych (t.j. Dz.U. 2022 poz. 1670), znaki "
            "wg zał. 4 rozp. w sprawie BDOT500 i mapy zasadniczej (Dz.U. 2021 poz. 1385) [SPRAWDŹ numer w ELI].")


@dataclass
class SiteResult:
    notes: list = field(default_factory=list)
    column_blocks: list = field(default_factory=list)
    north: bool = True
    units_note: str = UNITS
    hatch_mats: dict = field(default_factory=dict)
    rooms: list | None = None
    site: SiteData | None = None
    braki: list = field(default_factory=list)
    dane: dict = field(default_factory=dict)


def m2(v):
    return fmt.num(v, 2) + " m²"


def mm(v):
    return fmt.num(v, 2)


def _site(ctx, opts) -> SiteData:
    s = SiteData(ctx, opts)
    for b in s.braki:
        ctx.note("PZT — brak danych", f"{b.pole}: {b.opis.split(' — ')[0]}")
    return s


def _labels_building(lab, s, W, h=D.H):
    """Opis budynku (PN-B-01027 poz. 1.8): „±0,00=101,65”, liczba kondygnacji nadziemnych w kółku, funkcja."""
    from ..draft import symbols as S
    k = lab.k
    rom = ["", "I", "II", "III", "IV", "V", "VI"][min(6, W["n_kond"])]
    inner = s.p0.buffer(-3.0 * k)
    from .common import label_point, spiral
    c0 = label_point(s.p0)
    cands = [p for p in spiral(c0, 1.2 * k * 2, 6, 8) if inner.contains(Point(p))] or [tuple(c0)]

    def fn(cv, p):
        S.building_label(cv, p, s.zero_abs, rom, h=h, layer="Z-OPISY")
        cv.text(np.asarray(p) + np.array([0.0, (h * 1.5) * k]), "bud. mieszk. jednorodz.", h, 0.0, "center",
                "baseline", "Z-OPISY")
    lab.pl.place(lab.vp, fn, cands, penalty_step=0.01)


def _frame_and_note(vp, win_b, used):
    """Ramka podkładu i opis „PODKŁAD PRZYKŁADOWY…” nad ramką (poza treścią mapy)."""
    from ..draft.sheet import wrap
    k = vp.k
    x0, y0, x1, y1 = win_b
    vp.rect(x0, y0, x1, y1, "Z-MAPA-RAMKA", pen=0.5, lt="CIAGLA")
    used.add("mapa_ramka")
    Wmm = (x1 - x0) / k - 4.0
    ls = wrap(MAPA_TXT, Wmm, D.H)
    top = y1 + (4.0 + len(ls) * D.H * 1.45 + 5.0) * k
    vp.rect(x0, y1 + 1.5 * k, x1, top, "Z-MAPA-RAMKA", pen=0.35, lt="CIAGLA")
    vp.text((x0 + 2.0 * k, top - 5.0 * k), "MAPA DO CELÓW PROJEKTOWYCH — PODKŁAD PRZYKŁADOWY (FIKCYJNY)", 3.5, 0.0,
            "left", "baseline", "Z-MAPA-RAMKA", style="bold")
    for i, s_ in enumerate(ls):
        vp.text((x0 + 2.0 * k, top - (5.0 + 4.5 + i * D.H * 1.45) * k), s_, D.H, 0.0, "left", "baseline",
                "Z-MAPA-RAMKA")


def view_plan(ctx, spec, scale, opts):
    """PZT-01: PLAN ZAGOSPODAROWANIA DZIAŁKI na podkładzie mapy (1:500)."""
    title = spec.get("tytul_widoku") or spec.get("tytul") or "PLAN ZAGOSPODAROWANIA DZIAŁKI"
    vp = Viewport(scale, title)
    k = vp.k
    s = _site(ctx, opts)
    used = set()
    wb = D.map_window(s, opts, float(opts.get("margines", 4.0)))
    win = box(*wb)
    lab = D.Labeler(vp, bounds=win.buffer(-0.8 * k, join_style=2))
    W = wskazniki(s)
    op = opaska(s)
    # --- podkład (mapa syntetyczna)
    if opts.get("podklad", True):
        D.draw_base_map(vp, s, lab, win, used, opts)
        if opts.get("warstwice", True):
            D.draw_contours(vp, s, win, used, exclude=s.footprint.buffer(0.3))
    # --- projekt
    zj, zj_todo = D.zjazd_poly(s)
    if zj is not None:
        from ..draft import symbols as S
        D.fill_white(vp, zj, z=8.5)
        S.paving(vp, zj, "drobne", outline=False, band_mm=2.0)
        D.draw_geom(vp, zj, "Z-UTWARDZENIA", pen=0.35, lt="KRESKOWA" if zj_todo else "CIAGLA")
        used.add("zjazd")
    if opts.get("zielen", True):
        D.draw_green(vp, s, used, green=W["green"])
    D.draw_hardscape(vp, s, used, opaska_polys=op)
    D.draw_parking(vp, s, used)
    D.draw_bins(vp, s, used)
    D.draw_retention(vp, s, used)
    D.draw_drainage(vp, s, used)
    D.draw_pc(vp, s, used)
    D.draw_fence(vp, s, used)
    corners = D.draw_plot_boundary(vp, s, used)
    D.draw_building_line(vp, s, used, win)
    D.draw_utilities(vp, s, used, win, inside=s.p0)
    D.draw_objects(vp, s, used, win)
    D.draw_building(vp, s, used, slab_lt=str(opts.get("linia_plyt", "PUNKTOWA")).upper())
    D.register_all(lab)
    # --- opisy i wymiary (kolejność = priorytet)
    _labels_building(lab, s, W)
    used.add("zero")
    _dims_plan(lab, s, used)
    _labels_project(lab, s, W, used, detail=False)
    if opts.get("podklad", True):
        D.label_base_map(vp, s, lab, win, used, opts, contours=opts.get("warstwice", True))
        _spots_map(lab, s, win, used, float(opts.get("pikiety_co", 9.0)))
    _frame_and_note(vp, wb, used)
    res = SiteResult(site=s, braki=s.braki)
    res.column_blocks = [("legenda", D.legend_block(used, order=LEGEND_ORDER_PLAN)),
                         ("wskazniki", _block_wskazniki(s, W)),
                         ("odleglosci", _block_odleglosci(s)),
                         ("oo", _block_oo(s))]
    res.notes = _notes_plan(s, W, zj_todo, lab)
    res.dane = dict(wskazniki={k_: v for k_, v in W.items() if k_ not in ("cover", "green")}, okno=wb)
    return vp, res, title


LEGEND_ORDER_PLAN = ["mapa_ramka", "granica", "rozgraniczajaca", "jezdnia", "bud_sasiedni", "linia_zabudowy",
                     "budynek", "bud_wyzsze", "bud_plyty", "zero", "wejscie", "wjazd", "zjazd"]


def _el_geoms(s, row):
    """Geometrie elementu z wiersza odległości: (linia, na której leży koniec, wielobok do omijania)."""
    if row["typ"] in ("otw", "bez"):
        kid = row["el"].split()[1]
        g = s.storeys.get(kid, s.footprint)
        return g.boundary, s.footprint
    pg = next((x["poly"] for x in s.slabs + s.tarasy if x["id"] == row["el"]), None)
    if pg is None:
        return None, s.footprint
    return pg.boundary, unary_union([pg, s.footprint])


def _dims_plan(lab, s, used, detail=False):
    """Wymiary PZT: odległości od granic (WT § 12), linia zabudowy, gabaryty obrysu, odległości od budynków sąsiednich."""
    rows = odleglosci(s)
    by = {}
    for r in rows:
        by.setdefault(r["granica"], {})[r["typ"]] = r
    for gi, rr in by.items():
        walls = [r for t_, r in rr.items() if t_ in ("otw", "bez")]
        wmin = min((r["d"] for r in walls), default=1e9)
        sel = [rr["otw"]] if "otw" in rr else []
        if "bez" in rr and rr["bez"]["d"] < wmin + 1e-6 and "otw" not in rr:
            sel.append(rr["bez"])
        if "bez" in rr and "otw" in rr and rr["bez"]["d"] < rr["otw"]["d"] - 0.01 and detail:
            sel.append(rr["bez"])
        if "wys" in rr and (rr["wys"]["d"] < wmin - 0.01) and (detail or not rr["wys"]["droga"]):
            sel.append(rr["wys"])
        seg = next(g["seg"] for g in s.granice if g["i"] == gi)
        for r in sel:
            on_a, avoid = _el_geoms(s, r)
            place_ok = D.place_dim(lab, r["p_el"], r["p_gr"], on_a=on_a, on_b=seg, avoid=avoid, span=14.0,
                                   step=0.25 if detail else 0.5)
            used.add("wymiar")
            r["narysowany"] = place_ok is not None
    # linia zabudowy — odległość od linii rozgraniczającej drogi
    lz = s.linia_zabudowy
    if lz is not None and s.droga["pas"] is not None:
        a, b = nearest_points(lz, s.droga["pas"].exterior)
        on_b = s.droga["pas"].exterior
        D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_a=lz, on_b=on_b, avoid=s.footprint, span=16.0, step=0.5,
                    prefer=-12.0)
        spr = linia_zabudowy_spr(s)
        if detail and spr:
            D.place_dim(lab, spr["p_b"], spr["p_l"], on_a=s.footprint.boundary, on_b=lz, avoid=s.footprint,
                        span=10.0, step=0.25)
    # gabaryty obrysu parteru (poza budynkiem)
    x0, y0, x1, y1 = s.p0.bounds
    k = lab.k
    offs = [-(v * k) for v in (7, 9, 11, 13, 15, 18)]
    D.place_dim(lab, (x0, y0), (x1, y0), shifts=offs if lab.k > 0.3 else [-v for v in (1.5, 2, 2.5, 3, 3.5)])
    D.place_dim(lab, (x1, y0), (x1, y1), shifts=offs if lab.k > 0.3 else [-v for v in (1.5, 2, 2.5, 3, 3.5)])
    # odległości od budynków sąsiednich (informacyjnie — WT § 271)
    for x in s.sasiedzi:
        if x["bud"] is None or detail:
            continue
        a, b = nearest_points(s.footprint, x["bud"])
        if a.distance(b) > 30.0:
            continue
        D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_a=s.footprint.boundary, on_b=x["bud"].boundary,
                    avoid=unary_union([s.footprint, x["bud"]]), span=12.0, step=0.5)


def _short(txt, n=28):
    t = str(txt or "").split(" — ")[0].split(";")[0].strip()
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def _labels_project(lab, s, W, used, detail=False):
    """Opisy elementów projektu (priorytet przed opisami podkładu)."""
    k = lab.k
    h = D.H
    # działka: numer i powierzchnia
    free = s.plot.difference(s.footprint.buffer(4.0)).buffer(-3.0)
    anchor = np.asarray((free if not free.is_empty else s.plot).representative_point().coords[0])
    lab.label(anchor, [f"dz. nr {s.nr}", f"P = {m2(s.plot.area)}"], 3.5, "Z-OPISY", ["bold", "normal"],
              dists=(0.0, 3.0, 6.0, 10.0, 15.0, 22.0), leader_from=99)
    if s.linia_zabudowy is not None:
        lab.along(s.linia_zabudowy, "nieprzekraczalna linia zabudowy (MPZP)", h, "Z-LZ", "#c00000", n=1,
                  offset_mm=2.4, max_cost=8.0)
    for t in s.tarasy:
        pg = t["poly"].difference(s.p0)
        if pg.area > 4.0:
            lab.label(np.asarray(pg.representative_point().coords[0]), ["taras" if "desk" in t["naw"] else
                                                                        "podest"], h, dists=(0.0, 1.5, 4.0, 8.0))
    for u in s.utwardzenia:
        nm = _short(u["raw"].get("nawierzchnia"), 22)
        if u["poly"].area < (3.0 if not detail else 1.0) or "fundament" in nm or "pojemnik" in nm:
            continue
        lab.label(np.asarray(u["poly"].representative_point().coords[0]), [nm], h, dists=(0.0, 1.5, 4.0, 8.0, 12.0))
    for q in s.miejsca:
        if q["poly"].difference(s.p0).area < 0.1:
            continue
        lab.label(np.asarray(q["poly"].centroid.coords[0]), ["P"], h, style="bold", dists=(0.0, 1.0, 2.5),
                  max_cost=3.0)
    nga = sum(1 for q in s.miejsca if q["poly"].difference(s.p0).area < 0.1)
    if nga and s.wjazdy:
        w = s.wjazdy[0]
        lab.label(w["pt"] - w["out"] * 2.0, [f"garaż — {nga} st. post."], h, dists=(0.0, 1.5, 3.0, 5.0))
    if s.odpady and s.odpady["poly"] is not None:
        lab.label(np.asarray(s.odpady["poly"].centroid.coords[0]), ["pojemniki na odpady"], h, dot=True)
    if s.pc is not None:
        lab.label(np.asarray(s.pc["body"].centroid.coords[0]),
                  ["PC — jedn. zewn.", f"strefa R290 r = {mm(s.pc['r'])} m"], h, dot=True)
    if s.zbiornik:
        V = s.zbiornik.get("V")
        lab.label(s.zbiornik["xy"], [f"zbiornik retencyjny V = {fmt.num(float(V), 1)} m³" if V else "zbiornik"], h,
                  dot=True, dists=(3.0, 5.0, 8.0, 12.0))
    if s.rozsaczanie and s.rozsaczanie["poly"] is not None:
        r = s.rozsaczanie
        txt = ["niecka chłonna", f"{m2(r['poly'].area)}" + (f", V = {fmt.num(float(r['V']), 1)} m³" if r["V"] else "")]
        lab.label(np.asarray(r["poly"].centroid.coords[0]), txt, h, dists=(0.0, 3.0, 6.0, 10.0))
    for t in s.drzewa:
        nm = t["id"] + " " + t["gat"].split()[0] + (" (istn.)" if t["istn"] else "")
        lab.label(t["xy"], [nm], h, dists=(0.8, 2.0, 4.0, 7.0), leader_from=2.5, max_cost=10.0)
    for o in s.obiekty.values():
        idu = o.id.upper()
        if idu.startswith("PC"):
            continue
        if idu.startswith("HYD"):
            d = Point(o.xy).distance(s.plot)
            txt = ["Hp DN80" if "80" in o.opis else "Hp", f"(≈ {fmt.num(d, 1)} m od działki)"]
        else:
            txt = [o.id]
        if lab.bounds is None or lab.bounds.contains(Point(o.xy)):
            lab.label(o.xy, txt, h, dot=False, dists=(1.5, 3.0, 5.0, 8.0, 12.0))
    for b in s.bramy:
        nm = "furtka" if b["typ"] == "furtka" else "brama przesuwna"
        lab.label(b["xy"], [f"{nm} {mm(b['szer'])}"], h, dists=(3.0, 5.0, 8.0, 12.0), leader_from=2.5,
                  dirs=[(0, -1), (1, -1), (-1, -1), (1, 0), (-1, 0)])
    for sx in [x for x in s.sieci if not x.istn]:
        g = sx.geom.difference(s.p0) if not s.p0.is_empty else sx.geom
        parts = sorted(getattr(g, "geoms", [g]), key=lambda q: -q.length)
        if not parts or parts[0].is_empty:
            continue
        lab.along(parts[0], sx.lit, h, "Z-SIECI-PROJ", sx.kolor, n=1, max_cost=3.0)
