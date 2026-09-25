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
``okno: [x0, y0, x1, y1]`` (układ działki), ``otoczenie`` [m] (PZT-01, domyślnie 25), ``margines`` [m],
``linia_plyt: PUNKTOWA|KRESKOWA``, ``pikiety_co`` [m] (PZT-01: min. odstęp opisywanych rzędnych mapy),
``rzedne_proj_co`` [m] (PZT-02: min. odstęp opisywanych rzędnych projektowanych, domyślnie 2,0; 0 — wszystkie),
``rzedne_proj_co_rowne`` [m] (PZT-02: min. odstęp opisów tej samej rzędnej, domyślnie 5,0),
``warstwice: true``, ``warstwice_projektowane: false`` (PZT-02), ``mpzp: {...}`` (limity, gdy brak w modelu; także
``wspolne.mpzp``), ``odleglosci_min: {"e-t": [0.5, "źródło"]}`` i ``retencja_min: {budynek: 3.0, granica: 2.0,
drzewo: 1.0}`` (PZT-03/PZT-02), ``podklad: true``, ``zielen: true``, ``szer_tabel`` [mm] (PZT-01).
Tabele zestawień rysowane są w rzutni obok rysunku (pismo 2,5 mm), legenda i uwagi — w kolumnie opisowej arkusza.
Wskaźniki MPZP — wyłącznie z ``lamela.wskazniki`` (jedno źródło). Braki danych: ``braki_md`` /
``python3 -m lamela.views.site --braki projekt/02_PZT/BRAKI_DANYCH.md``.
Konfiguracja arkuszy: ``model/arkusze_pzt.yaml``; CLI: ``tools/generuj_widoki.py --arkusze model/arkusze_pzt.yaml``.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import Point, box
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
            "wg zał. 4 rozp. w sprawie BDOT500 i mapy zasadniczej (Dz.U. 2021 poz. 1385; oba akty zweryfikowane w ELI 25.09.2026 — status: obowiązujące).")


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
    """Liczba z dokładnością 0,01 (zaokrąglenie połówkowe w górę — bez błędu reprezentacji binarnej)."""
    return fmt.num(fmt.round_half_up(round(float(v) * 100.0, 6)) / 100.0, 2)


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
    gar = [q["poly"] for q in s.miejsca if q["poly"].difference(s.p0).area < 0.1]
    main = s.p0.difference(unary_union(gar).convex_hull.buffer(0.3)) if gar else s.p0
    main = max(getattr(main, "geoms", [main]), key=lambda q: q.area)
    c0 = label_point(main)
    cands = [p for p in spiral(c0, 1.2 * k * 2, 6, 8) if inner.contains(Point(p))] or [tuple(c0)]

    bx = s.p0.bounds
    c1 = np.array([(bx[0] + bx[2]) / 2.0, label_point(s.p0)[1]])
    cands = [p for p in spiral(c1, 1.0 * k * 2, 6, 8) if inner.contains(Point(p))] or [tuple(c1)]

    from ..draft import text as T
    fun = ["bud. mieszk. jednorodz."]
    if T.width(fun[0], h) > (bx[2] - bx[0]) / k - 5.0:
        fun = ["bud. mieszk.", "jednorodz."]

    def fn(cv, p):
        S.building_label(cv, p, s.zero_abs, rom, h=h, layer="Z-OPISY")
        for i, t_ in enumerate(reversed(fun)):
            cv.text(np.asarray(p) + np.array([0.0, h * (1.6 + 1.45 * i) * k]), t_, h, 0.0, "center", "baseline",
                    "Z-OPISY")
    g0 = len(lab.pl.geoms)
    lab.pl.place(lab.vp, fn, cands, penalty_step=0.01, bounds=s.p0.buffer(-1.0 * k))
    lab.bump(g0)
    return c0


def _label_garage(lab, s):
    """Opis garażu wewnątrz obrysu (stanowiska postojowe w garażu — WT § 18, MPZP)."""
    g = [q["poly"] for q in s.miejsca if q["poly"].difference(s.p0).area < 0.1]
    if not g:
        return
    U = unary_union(g).convex_hull
    old_b = lab.bounds
    lab.bounds = U.buffer(0.2)
    lab.label(np.asarray(U.centroid.coords[0]), ["garaż", f"{len(g)} × P"], D.H, dists=(0.0, 0.5, 1.0, 1.5),
              leader_from=99)
    lab.bounds = old_b


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
    vp.text((x0 + 2.0 * k, top - 5.0 * k), "MAPA DO CELÓW PROJEKTOWYCH — PODKŁAD PRZYKŁADOWY", 3.5, 0.0,
            "left", "baseline", "Z-MAPA-RAMKA", style="bold")
    for i, s_ in enumerate(ls):
        vp.text((x0 + 2.0 * k, top - (5.0 + 4.5 + i * D.H * 1.45) * k), s_, D.H, 0.0, "left", "baseline",
                "Z-MAPA-RAMKA")
    return top


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
            D.draw_contours(vp, s, win, used, exclude=_contour_mask(s))
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
    D.draw_pc(vp, s, used)
    D.draw_fence(vp, s, used)
    D.draw_plot_boundary(vp, s, used)
    D.draw_building_line(vp, s, used, win)
    for sx in [x for x in s.sieci if not x.istn]:
        g = D.clip(sx.geom.difference(s.p0), win)
        if g is not None:
            D.utility(vp, g, sx, pen=0.5, flow=False)
            used.add(f"proj_{sx.branza}")
            for q in (sx.geom.coords[0], sx.geom.coords[-1]):
                if any(E.istn and E.branza == sx.branza and E.geom.distance(Point(q)) < 0.05 for E in s.sieci):
                    D.cross_mark(vp, q, color=sx.kolor)
                    used.add("wlaczenie")
    D.draw_objects(vp, s, used, win)
    D.draw_building(vp, s, used, slab_lt=str(opts.get("linia_plyt", "PUNKTOWA")).upper())
    D.register_all(lab)
    # --- opisy i wymiary (kolejność = priorytet)
    _labels_building(lab, s, W)
    used.add("zero")
    he, _src = s.teren_przy_wejsciu()          # rzędna terenu przy wejściu głównym (PN-B-01027 poz. 1.8)
    if he is not None and s.wejscie_gl is not None:
        D.spot(lab, s.wejscie_gl["pt"] + s.wejscie_gl["out"] * 0.6, he, projected=True,
               dists=(1.0, 2.5, 4.0, 6.0, 9.0))
        used.add("spot_proj")
    lab.area(s.footprint, 3.0)
    _dims_plan(lab, s, used)
    _labels_project(lab, s, W, used, detail=False)
    if opts.get("podklad", True):
        D.label_base_map(vp, s, lab, win, used, opts, contours=opts.get("warstwice", True))
        _spots_map(lab, s, win, used, float(opts.get("pikiety_co", 9.0)))
    lab.fix_overlaps()
    top = _frame_and_note(vp, wb, used)
    # --- tabele obok mapy (w rzutni — pismo 2,5 mm)
    x_t = wb[2] + 8.0 * k
    t1 = _tab_wskazniki(s, W)
    r1 = D.vp_table(vp, x_t, top, t1["cols"], t1["rows"], t1["title"], align=t1["align"], notes=t1["notes"],
                    max_w_mm=float(opts.get("szer_tabel", 176.0)))
    t2 = _tab_odleglosci(s)
    D.vp_table(vp, x_t, r1[1] - 6.0 * k, t2["cols"], t2["rows"], t2["title"], align=t2["align"], notes=t2["notes"],
               max_w_mm=float(opts.get("szer_tabel", 176.0)))
    res = SiteResult(site=s, braki=s.braki)
    res.column_blocks = [("legenda", D.legend_block(used, order=LEGEND_ORDER_PLAN)), ("oo", _block_oo(s))]
    res.notes = _notes_plan(s, W, zj_todo, lab)
    res.dane = dict(wskazniki={k_: v for k_, v in W.items() if k_ not in ("cover", "green")}, okno=wb)
    if lab.failed:
        ctx.note("PZT-01", f"nie umieszczono {len(lab.failed)} opisów: {[f[0] for f in lab.failed][:8]}")
    return vp, res, title


def _contour_mask(s):
    """Obszar bez warstwic podkładu: budynki (istniejące i projektowany) oraz poza zasięgiem pikiet (+2 m)."""
    from shapely.geometry import MultiPoint
    hull = MultiPoint([tuple(p[:2]) for p in s.pkt_ist]).convex_hull.buffer(2.0) if len(s.pkt_ist) >= 3 else None
    parts = [s.footprint.buffer(0.3)] + [x["bud"] for x in s.sasiedzi if x["bud"] is not None]
    m = unary_union(parts)
    if hull is not None:
        m = unary_union([m, box(-1e4, -1e4, 1e4, 1e4).difference(hull)])
    return m


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
        if detail and any(r["droga"] for r in sel):
            sel = []                      # od drogi — wymiarowana linia zabudowy (6,00 + odległość lica)
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
    if not detail:            # na PZT-02 gabaryty w łańcuchach obrysu (_chains)
        D.place_dim(lab, (x0, y0), (x1, y0), shifts=offs)
        D.place_dim(lab, (x1, y0), (x1, y1), shifts=offs)
    # odległości od budynków sąsiednich (informacyjnie — WT § 271)
    side_nb = {g["sasiad"] for g in s.granice if not g["droga"]}
    for x in s.sasiedzi:
        if x["bud"] is None or detail or x["nr"] not in side_nb:
            continue
        a, b = nearest_points(s.footprint, x["bud"])
        if a.distance(b) > 30.0:
            continue
        D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_a=s.footprint.boundary, on_b=x["bud"].boundary,
                    avoid=unary_union([s.footprint, x["bud"]]), span=12.0, step=0.5)


def _short(txt, n=28):
    t = str(txt or "").split(" — ")[0].split(";")[0].strip()
    return t if len(t) <= n else t[:n - 1].rstrip() + "…"


def _labels_project(lab, s, W, used, detail=False, utilities=True):
    """Opisy elementów projektu (priorytet przed opisami podkładu)."""
    k = lab.k
    h = D.H
    if detail:
        R = s.plot.buffer(0.3)
    else:                   # działka z otoczeniem 12 m, bez pasa drogowego i terenu po drugiej stronie drogi
        R = s.plot.buffer(12.0, join_style=2)
        if lab.bounds is not None:
            R = R.intersection(lab.bounds)
        if s.droga["pas"] is not None:
            R = R.difference(s.droga["pas"].buffer(0.3))
            R = max((q for q in getattr(R, "geoms", [R]) if q.intersects(s.plot)), key=lambda q: q.area, default=R)
    L = lambda *a_, **kw: lab.label_in(R, *a_, **kw)   # noqa: E731 — opisy projektu poza pasem drogowym
    # działka: numer i powierzchnia
    free = s.plot.difference(s.footprint.buffer(4.0)).buffer(-3.0)
    anchor = np.asarray((free if not free.is_empty else s.plot).representative_point().coords[0])
    L(anchor, [f"dz. nr {s.nr}", f"P = {m2(s.plot.area)}"], 3.5, "Z-OPISY", ["bold", "normal"],
              dists=(0.0, 3.0, 6.0, 10.0, 15.0, 22.0), leader_from=99)
    if s.linia_zabudowy is not None:
        lz = s.linia_zabudowy
        a0 = np.asarray(lz.interpolate(min(1.0, lz.length * 0.05)).coords[0])
        lab.label(a0, ["nieprzekraczalna linia", "zabudowy (MPZP)"], h, "Z-LZ", color="#c00000",
                  dists=(3.0, 6.0, 10.0, 15.0, 20.0),
                  dirs=None if detail else [(-1, 1), (-1, -1), (-1, 0), (0, -1), (1, -1)],
                  leader_from=2.0, leader_color="#c00000")
    for t in s.tarasy:
        pg = t["poly"].difference(s.p0)
        if pg.area > 4.0:
            L(np.asarray(pg.representative_point().coords[0]), ["taras" if "desk" in t["naw"] else
                                                                        "podest"], h, dists=(0.0, 1.5, 4.0, 8.0))
    for u in s.utwardzenia:
        nm = _short(u["raw"].get("nawierzchnia"), 22)
        if u["poly"].area < 3.0 or "fundament" in nm or "pojemnik" in nm:
            continue
        L(np.asarray(u["poly"].representative_point().coords[0]), [nm], h, dists=(0.0, 1.5, 4.0, 8.0, 12.0))
    for q in s.miejsca:
        if q["poly"].difference(s.p0).area < 0.1:
            continue
        L(np.asarray(q["poly"].centroid.coords[0]), ["P"], h, style="bold", dists=(0.0, 1.0, 2.5),
                  own=q["poly"].exterior)
    if s.odpady and s.odpady["poly"] is not None:
        L(np.asarray(s.odpady["poly"].centroid.coords[0]), ["odpady"], h, dot=True,
                  dists=(1.0, 2.5, 4.0, 6.0, 9.0, 12.0))
    if s.pc is not None:
        L(np.asarray(s.pc["body"].centroid.coords[0]),
          ["PC (R290)"] if detail else ["PC — jedn. zewn.", f"strefa R290 r = {mm(s.pc['r'])} m"], h, dot=True)
    kr = [e for e in getattr(s, "elem_zewn", []) if e["typ"] == "kratownica_pnacza"]
    if kr:                                                     # K-13 — jeden opis dla wszystkich paneli kratownicy
        g = unary_union([e["geom"] for e in kr])
        q = np.asarray(g.interpolate(0.15, normalized=True).coords[0]) if g.geom_type == "LineString" else \
            np.asarray(g.representative_point().coords[0])
        L(q, ["zielona ściana (pnącza", "na kratownicy)"] if detail else ["zielona ściana"], h, dists=(1.0, 2.5, 4.0, 6.0))
    if s.zbiornik:
        V = s.zbiornik.get("V")
        L(s.zbiornik["xy"], [f"zbiornik retencyjny V = {fmt.num(float(V), 1)} m³" if V else "zbiornik"], h,
                  dot=True, dists=(3.0, 5.0, 8.0, 12.0))
    if s.rozsaczanie and s.rozsaczanie["poly"] is not None:
        r = s.rozsaczanie
        txt = ["niecka chłonna", f"{m2(r['poly'].area)}" + (f", V = {fmt.num(float(r['V']), 1)} m³" if r["V"] else "")]
        L(np.asarray(r["poly"].centroid.coords[0]), txt, h, dists=(0.0, 3.0, 6.0, 10.0))
    for t in s.drzewa:
        nm = t["id"] + " " + t["gat"].split()[0] + (" (istn.)" if t["istn"] else "")
        r_mm = t["d"] / 2.0 / k
        L(t["xy"], [nm], h, dists=(0.8, 2.0, r_mm * 0.75, r_mm + 1.0, r_mm + 3.0, r_mm + 6.0, r_mm + 10.0),
                  leader_from=2.5, own=Point(t["xy"]).buffer(t["d"] / 2.0).exterior)
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
            (L if s.plot.buffer(1.0).contains(Point(o.xy)) else lab.label)(o.xy, txt, h, dot=False,
                                                                          dists=(1.5, 3.0, 5.0, 8.0, 12.0))
    for sx in [x for x in s.sieci if not x.istn] if utilities else []:
        g = sx.geom.difference(s.p0) if not s.p0.is_empty else sx.geom
        parts = sorted(getattr(g, "geoms", [g]), key=lambda q: -q.length)
        if not parts or parts[0].is_empty:
            continue
        lab.along(parts[0], sx.lit, h, "Z-SIECI-PROJ", sx.kolor, n=1, max_cost=3.0)


def _spots_map(lab, s, win, used, every=9.0):
    """Pikiety terenu istniejącego na podkładzie (wybór co ≥ ``every`` m; narożniki działki w pierwszej kolejności)."""
    P = s.pkt_ist
    if not len(P):
        return
    corners = s.corners
    pri = [0 if min(np.hypot(*(p[:2] - q)) for q in corners) < 0.05 else 1 for p in P]
    order = sorted(range(len(P)), key=lambda i: (pri[i], P[i, 1], P[i, 0]))
    chosen = []
    for i in order:
        p = P[i]
        if not win.buffer(-2.0 * lab.k).contains(Point(p[:2])) or s.footprint.buffer(0.5).contains(Point(p[:2])):
            continue
        if any(np.hypot(*(p[:2] - q[:2])) < every - 1e-6 for q in chosen):
            continue
        chosen.append(p)
    for p in chosen:
        pos, _c = D.spot(lab, p[:2], p[2], projected=False, max_cost=3.0)
        if pos is not None:
            used.add("spot_ist")


def _ok(v):
    return "TAK" if v else "NIE"


def _tab_wskazniki(s, W):
    L = s.mpzp or {}
    A = W["A"]
    rows = [["Powierzchnia działki nr " + s.nr, m2(A), "—", ""]]
    mz = L.get("max_udzial_zabudowy")
    rows.append(["Pow. zabudowy (upzp art. 2 pkt 35)", m2(W["zab"]),
                 f"≤ {m2(mz * A)}" if mz else "—", _ok(W["udzial_zab"] <= mz) if mz else ""])
    rows.append(["Udział pow. zabudowy", fmt.percent(W["udzial_zab"] * 100, 2),
                 f"≤ {fmt.percent(mz * 100, 0)}" if mz else "—", _ok(W["udzial_zab"] <= mz) if mz else ""])
    rows.append(["– z płytami i okapami (kontrolnie)", f"{m2(W['zab_pl'])} ({fmt.percent(W['zab_pl'] / A * 100, 2)})",
                 "informacyjnie", _ok(W["zab_pl"] / A <= mz) if mz else ""])
    rows.append(["Drogi, dojścia, place", m2(W["utw"]), "—", ""])
    rows.append(["Tarasy naziemne, podesty", m2(W["tarasy"]), "—", ""])
    if W["opaska"]:
        rows.append(["Opaska żwirowa", m2(W["opaska"]), "—", ""])
    mp = L.get("min_udzial_pbc")
    rows.append(["PBC (upzp art. 2 pkt 28)", f"{m2(W['pbc'])} ({fmt.percent(W['pbc_udzial'] * 100, 2)})",
                 f"≥ {m2(mp * A)} ({fmt.percent(mp * 100, 0)})" if mp else "—",
                 _ok(W["pbc_udzial"] >= mp) if mp else ""])
    if W["pbc_dach"]:
        rows.append([f"– z 50 % dachu ziel. {', '.join(W['dachy_ziel'])} (rezerwa)",
                     f"{m2(W['pbc'] + W['pbc_dach'])} ({fmt.percent(W['pbc_z_dachem'] * 100, 2)})", "informacyjnie", ""])
    it = L.get("intensywnosc")
    kk = "+".join(W["kond"])
    rows.append([f"Pow. kondygnacji nadz. ({kk})", m2(W["suma_kond"]),
                 f"{m2(it[0] * A)}–{m2(it[1] * A)}" if it else "—",
                 _ok(it[0] * A <= W["suma_kond"] <= it[1] * A) if it else ""])
    rows.append(["Nadziemna intensywność zabudowy", fmt.num(W["intens"], 3),
                 f"{fmt.num(it[0], 2)}–{fmt.num(it[1], 2)}" if it else "—",
                 _ok(it[0] <= W["intens"] <= it[1]) if it else ""])
    mh = L.get("max_wysokosc")
    if W["wys_zab"] is not None:
        rows.append(["Wysokość zabudowy (art. 2 pkt 30)", f"{mm(W['wys_zab'])} m", f"≤ {mm(mh)} m" if mh else "—",
                     _ok(W["wys_zab"] <= mh) if mh else ""])
    if W["wt"]:
        rows.append(["Wysokość budynku (WT § 6)", f"{mm(W['wt']['H'])} m", "N: ≤ 12,00 m", _ok(W["wt"]["H"] <= 12.0)])
    mk = L.get("max_kondygnacji")
    rows.append(["Kondygnacje nadziemne", str(W["n_kond"]), f"≤ {mk}" if mk else "—",
                 _ok(W["n_kond"] <= mk) if mk else ""])
    mpk = L.get("min_miejsc_postojowych")
    nm = W["miejsca"]["garaz"] + W["miejsca"]["zewn"]
    rows.append(["Miejsca postojowe (garaż + zewn.)", f"{W['miejsca']['garaz']} + {W['miejsca']['zewn']}",
                 f"≥ {mpk}" if mpk else "—", _ok(nm >= mpk) if mpk else ""])
    if W["dach_spadek_deg"] is not None:
        rows.append(["Dach — kąt nachylenia", f"{fmt.num(W['dach_spadek_deg'], 1)}° (płaski)",
                     str(L.get("dach") or "—"), _ok(W["dach_spadek_deg"] <= 12.0) if L.get("dach") else ""])
    spr = linia_zabudowy_spr(s)
    if spr:
        prz = ", ".join(nm_ for nm_, _v in spr["przekroczenia"]) or "brak"
        rows.append(["Lico ścian od linii zabudowy", f"{mm(spr['d'])} m", "nie przekraczać",
                     _ok(spr["ok"])])
        rows.append(["Elementy poza linią zabudowy", prz, str(L.get("wysuniecia") or "—"), ""])
    zr = {"model": "dzialka.yaml: dzialka.mpzp",
          "konfiguracja": "konfiguracja arkuszy (brief § 3) — BRAK W MODELU [DO UZUPEŁNIENIA]",
          "brak": "BRAK [DO UZUPEŁNIENIA]"}[s.mpzp_zrodlo]
    h = W["wys"]
    bz = h.get("bez_zalozen")
    notes = [f"MPZP: {s.mpzp_txt or '—'}. Limity: {zr}.",
             "Wartości z modułu lamela.wskazniki (jedyne źródło; definicje upzp art. 2 pkt 28–35, t.j. Dz.U. 2026 "
             "poz. 538): PBC bez nawierzchni ażurowych, opaski, pojemników i terenu nad zbiornikiem; dach zielony "
             "(≥ 10 m²) w 50 % — tylko rezerwa.",
             f"Wysokość zabudowy = z_top {mm(h['z_top_abs'])} ({h['element']}) − t_śr {mm(h['t_sr'])} "
             f"(t_min {mm(h['t_min'])}, t_max {mm(h['t_max'])} na obwodzie rzutu ścian zewn.; w każdym punkcie niższa "
             "z rzędnych terenu istniejącego/projektowanego)"
             + (f"; bez założenia: {mm(bz[0])} m ({bz[1]})." if bz else "."),
             (f"WT § 6: od terenu przy wejściu {W['wt']['wejscie']} ({mm(W['wt']['H_ent'])}) do wierzchu stropodachu "
              f"{W['wt']['dach']} (bez attyki) — grupa {W['wt']['grupa']}." if W["wt"] else "")]
    return dict(title="ZESTAWIENIE POWIERZCHNI I WSKAŹNIKÓW ZAGOSPODAROWANIA (RPB § 14 pkt 4, MPZP)",
                cols=[("Wskaźnik / element", 0), ("Projekt", 0), ("MPZP / wymaganie", 0), ("Zgodność", 0)],
                rows=rows, align=["left", "right", "left", "center"], notes=[n for n in notes if n])


def _tab_odleglosci(s):
    rows = []
    for r in odleglosci(s):
        gr = f"{r['strona']} ({r['sasiad']})" if r["sasiad"] else r["strona"]
        el = r["el"] if r["typ"] != "wys" else f"{r['el']} — okap/płyta/taras"
        if r["droga"]:
            wym, ok = "nie dot. (ust. 10)", "—"
        else:
            wym, ok = f"≥ {mm(r['wym'])}", _ok(r["ok"])
        rows.append([gr, el, mm(r["d"]), wym, ok])
    return dict(title="ODLEGŁOŚCI OD GRANIC DZIAŁKI (WT § 12)",
                cols=[("Granica", 0), ("Element (płaszczyzna ściany)", 0), ("Odl. [m]", 0), ("Wymagana [m]", 0),
                      ("Zgodność", 0)], rows=rows, align=["left", "left", "right", "left", "center"],
                notes=["WT § 12 ust. 1: 4,00 m — ściana z oknami/drzwiami, 3,00 m — bez otworów (każda płaszczyzna "
                       "ściany osobno); ust. 6: 1,50 m — okap, taras, daszek; ust. 10: od działki drogowej — nie "
                       "dotyczy. Odległość w poziomie w miejscu najmniejszego oddalenia (§ 9). WT stosowane na "
                       "podstawie art. 102a PB."])


def _block_oo(s):
    oo = (s.raw.get("obszar_oddzialywania") or {}).get("opis") if isinstance(s.raw.get("obszar_oddzialywania"),
                                                                            dict) else None
    lines = [oo or f"Opis obszaru oddziaływania — {D_TODO}.",
             "Podstawa ustalenia (RPB § 18 pkt 1): WT § 12, 13, 19, 23, 28–29, 60, 271 (art. 102a PB); u.d.p. "
             "art. 43; POŚ art. 144 ust. 2 i rozp. MŚ w sprawie dopuszczalnych poziomów hałasu (Dz.U. 2014 poz. 112); "
             "PW art. 234; ustalenia MPZP."]
    return D.text_block_col("OBSZAR ODDZIAŁYWANIA OBIEKTU (PB art. 3 pkt 20; RPB § 14 pkt 8)", lines)


D_TODO = "[DO UZUPEŁNIENIA]"


def _notes_plan(s, W, zj_todo, lab):
    out = ["Układ współrzędnych: lokalny układ działki (x → wschód, y → północ, początek w narożniku A); w projekcie "
           "rzeczywistym — układ PL-2000 strefa 6 z mapy do celów projektowych.",
           "Obrys budynku — lico zewnętrzne ścian parteru na wys. 1,0 m nad terenem; wspornik bryły A (II piętro) — "
           "obrys wyższych kondygnacji; płyty wspornikowe, okapy i daszek — przewieszenia (PN-B-01027 poz. 1.6).",
           "Wody opadowe zagospodarowane w granicach działki: rury spustowe → kolektory KD → zbiornik retencyjny "
           "szczelny → przelew do niecki chłonnej; odwodnienie liniowe przed bramą — brak spływu na drogę "
           "(MPZP; u.d.p. art. 39 ust. 1 pkt 9; WT § 28–29).",
           "Wymiary i rzędne szczegółowe — rys. PZT-02; uzbrojenie i koordynacja sieci — rys. PZT-03."]
    if zj_todo:
        out.append("Zjazd z drogi 1KDD pokazano jako przedłużenie bramy do krawędzi jezdni — geometria zastępcza "
                   f"{D_TODO}: szerokość, skosy/łuki, nawierzchnia i przepust wg zezwolenia zarządcy drogi "
                   "(u.d.p. art. 29 ust. 3a).")
    if s.braki:
        out.append(f"Braki danych modelu ({len(s.braki)} poz.) oznaczono {D_TODO}; wykaz: projekt/02_PZT/BRAKI_DANYCH.md.")
    return out


# ================================================================================================ PZT-02 / PZT-03
def detail_window(s, opts, margin=3.0):
    """Okno rysunków 1:200: działka ± ``margines`` [m], w kierunku drogi — do przeciwnej linii rozgraniczającej."""
    if opts.get("okno"):
        return tuple(float(v) for v in opts["okno"])
    m_ = float(opts.get("margines", margin))
    x0, y0, x1, y1 = s.plot.bounds
    X0, Y0, X1, Y1 = x0 - m_, y0 - m_, x1 + m_, y1 + m_
    pas = s.droga["pas"]
    if pas is not None:
        near = pas.intersection(box(X0, Y0 - 50, X1, Y1 + 50))
        if not near.is_empty and near.distance(s.plot) < 0.1:
            bx0, by0, bx1, by1 = near.bounds
            Y0, Y1 = min(Y0, by0 - 1.0), max(Y1, by1 + 1.0)
    return X0, Y0, X1, Y1


def _draw_context(vp, s, lab, win, used, hatch=True, lawn=False, zone=True, utilities_ist=True):
    """Treść wspólna 1:200: sąsiednie granice, droga, zieleń, nawierzchnie, budynek, ogrodzenie, retencja."""
    for x in s.sasiedzi:
        g = D.clip(x["poly"].exterior, win) if x["poly"] is not None else None
        D.draw_geom(vp, g, "Z-MAPA", pen=0.25, lt="CIAGLA")
    pas, jez = s.droga["pas"], s.droga["jezdnia"]
    if jez is not None and D.clip(jez, win) is not None:
        vp.fill(D.clip(jez, win), "Z-DROGA", "#e6e6e6", z=8.0)
        D.draw_geom(vp, D.clip(jez.exterior, win), "Z-MAPA", pen=0.25, lt="CIAGLA")
        used.add("jezdnia")
    if pas is not None:
        D.draw_geom(vp, D.clip(pas.exterior, win), "Z-DROGA", pen=0.7, lt="CIAGLA", color="#303030")
        used.add("rozgraniczajaca")
    if utilities_ist:
        for sx in [x for x in s.sieci if x.istn]:
            g = D.clip(sx.geom, win)
            if g is not None:
                D.utility(vp, g, sx, existing=True)
                used.add(f"ist_{sx.branza}")
    zj, zj_todo = D.zjazd_poly(s)
    if zj is not None:
        from ..draft import symbols as S
        D.fill_white(vp, zj, z=8.5)
        if hatch:
            S.paving(vp, zj, "drobne", outline=False, band_mm=4.0)
        D.draw_geom(vp, zj, "Z-UTWARDZENIA", pen=0.35, lt="KRESKOWA" if zj_todo else "CIAGLA")
        used.add("zjazd")
    D.draw_green(vp, s, used, lawn=lawn, green=None)
    D.draw_hardscape(vp, s, used, hatch=hatch, opaska_polys=opaska(s))
    D.draw_parking(vp, s, used)
    D.draw_bins(vp, s, used)
    D.draw_retention(vp, s, used)
    if zone:
        D.draw_pc(vp, s, used)
    D.draw_fence(vp, s, used)
    D.draw_plot_boundary(vp, s, used)
    D.draw_building_line(vp, s, used, win)
    return zj_todo


def _rect_dims(lab, pg, h=True, v=True, offs=(3.0, 5.0, 7.0, 10.0)):
    """Wymiary prostokąta (szerokość, długość) ustawiane po stronie o najmniejszej kolizji."""
    if pg is None or pg.is_empty or abs(pg.area - pg.envelope.area) > 0.02 * pg.envelope.area:
        return
    x0, y0, x1, y1 = pg.bounds
    k = lab.k
    if h:
        D.place_dim(lab, (x0, y0), (x1, y0), shifts=[-o * k for o in offs] + [(y1 - y0) + o * k for o in offs])
    if v:
        D.place_dim(lab, (x1, y0), (x1, y1), shifts=[-o * k for o in offs] + [(x1 - x0) + o * k for o in offs])


def _grad(fn, p, e=0.25):
    """Gradient powierzchni (dH/dx, dH/dy) — różnice centralne."""
    x, y = float(p[0]), float(p[1])
    q = np.array([[x + e, y], [x - e, y], [x, y + e], [x, y - e]])
    h = fn(q)
    return np.array([(h[0] - h[1]) / (2 * e), (h[2] - h[3]) / (2 * e)])


def _slopes(lab, s, used):
    """Spadki nawierzchni (wartość z modelu, kierunek wg terenu projektowanego) i kierunki spływu na terenie."""
    k = lab.k
    for u in s.utwardzenia + [dict(id=t["id"], poly=t["poly"].difference(s.p0), raw=dict(spadek=0.02))
                              for t in s.tarasy if "podest" in t["raw"].get("uwagi", "") or "płyt" in t["naw"]]:
        sp = float(u["raw"].get("spadek") or 0.0)
        pg = u["poly"].difference(s.p0)
        if sp <= 0 or pg.is_empty or pg.area < 1.0:
            continue
        c = np.asarray(pg.representative_point().coords[0])
        g = _grad(s.H_proj, c)
        d = -g if np.hypot(*g) > 1e-4 else (c - np.asarray(s.p0.centroid.coords[0]))
        if abs(d[0]) > 2.5 * abs(d[1]):
            d = np.array([np.sign(d[0]), 0.0])
        elif abs(d[1]) > 2.5 * abs(d[0]):
            d = np.array([0.0, np.sign(d[1])])
        L = min(12.0, max(6.0, min(pg.bounds[2] - pg.bounds[0], pg.bounds[3] - pg.bounds[1]) / k * 0.8))
        pos, _c = D.slope_arrow(lab, pg, d, sp, length_mm=L, max_cost=8.0)
        if pos is None:            # mniejsza strzałka, wyższy dopuszczalny koszt (wartość jest też w tabeli)
            pos, _c = D.slope_arrow(lab, pg, d, sp, length_mm=5.0, max_cost=20.0)
        if pos is not None:
            used.add("spadek")
    # kierunki spływu na terenie (spadek terenu projektowanego)
    cover = unary_union([s.p0.buffer(0.2)] + [u["poly"] for u in s.utwardzenia] + [t["poly"] for t in s.tarasy])
    pts = []
    ring = s.p0.buffer(1.25, join_style=2).exterior
    n = max(8, int(ring.length / 5.0))
    pts += [np.asarray(ring.interpolate(i / n, normalized=True).coords[0]) for i in range(n)]
    x0, y0, x1, y1 = s.plot.bounds
    for x in np.arange(x0 + 6.0, x1 - 3.0, 9.0):
        for y in np.arange(y0 + 5.0, y1 - 3.0, 9.0):
            pts.append(np.array([x, y]))
    free = s.plot.buffer(-1.5).difference(cover.buffer(0.8))
    for p in pts:
        if not free.contains(Point(p)):
            continue
        g = _grad(s.H_proj, p)
        if np.hypot(*g) < 2e-3:
            continue
        pg = Point(p).buffer(3.0)
        pos, _c = D.slope_arrow(lab, pg.intersection(free), -g, float(np.hypot(*g)), length_mm=8.0, max_cost=3.0)
        if pos is not None:
            used.add("splyw")


def _drain_labels(lab, s):
    h = D.H
    from .site_data import line as _line
    for o in s.odwodnienia:
        g = o["geom"] if o["geom"] is not None and o["geom"].length > 0.05 else \
            (_line(o["pts"]) if o["typ"] == "opaska_zwirowa" else None)
        if g is None or g.is_empty:
            continue
        if o["typ"] in ("liniowe", "opaska_zwirowa") or (o["typ"] == "niecka" and o["geom"] is not None):
            txt = [o["id"]]           # typ, długość, spadek i odbiornik — w tabeli „Odwodnienie powierzchniowe”
        else:
            continue
        anchors = [np.asarray(g.interpolate(f, normalized=True).coords[0]) if hasattr(g, "interpolate") else
                   np.asarray(g.representative_point().coords[0]) for f in (0.5, 0.3, 0.7, 0.15, 0.85)]
        lab.label(anchors, txt, h, "Z-ODWODNIENIE", dists=(2.0, 4.0, 7.0, 10.0, 14.0), leader_from=1.5, dot=True)
    for r in s.rury:
        lab.label(r["xy"], [r["id"]], h, "Z-ODWODNIENIE", dists=(1.2, 2.5, 4.0, 6.0), leader_from=2.4)


def _chains(lab, s):
    """Łańcuchy wymiarowe obrysu budynku: pd. — taras / płyty / wspornik / parter; pn. — narożniki parteru;
    wsch. i zach. — narożniki parteru i wyższych kondygnacji."""
    from ..draft import dims
    k = lab.k
    x0, y0, x1, y1 = s.p0.bounds
    C = np.asarray(s.p0.exterior.coords)
    groups = [g for g in (unary_union([t["poly"] for t in s.tarasy]) if s.tarasy else None, s.slab_union, s.upper)
              if g is not None and not g.is_empty]
    xs_s = sorted({round(float(g.bounds[0]), 3) for g in groups} | {round(x0, 3), round(x1, 3)})
    xs_n = sorted({round(float(q[0]), 3) for q in C if abs(q[1] - y1) < 0.8})
    ys_w = sorted({round(float(q[1]), 3) for q in C if abs(q[0] - x0) < 0.05} |
                  ({round(float(s.upper.bounds[3]), 3)} if not s.upper.is_empty else set()))
    ys_e = sorted({round(float(q[1]), 3) for q in C if abs(q[0] - x1) < 0.05})
    ymin_all = min([y0] + [g.bounds[1] for g in groups])
    xmin_all = min([x0] + [g.bounds[0] for g in groups])

    def chain(pts, direction, base, sgn):
        def fn(cv, off):
            at = base + sgn * off * k
            if direction == "h":
                dims.dim_chain(cv, [(x, base) for x in pts], (0.0, at), "h", layer="Z-WYMIARY", h=D.H, unit_="m",
                               tick_pen=0.18, ext_len=(1.5, 1.5), overshoot_mm=1.5, tick_mm=2.5, mask=0.3,
                               labels=[_lab_m(b - a) for a, b in zip(pts[:-1], pts[1:])])
            else:
                dims.dim_chain(cv, [(base, y) for y in pts], (at, 0.0), "v", layer="Z-WYMIARY", h=D.H, unit_="m",
                               tick_pen=0.18, ext_len=(1.5, 1.5), overshoot_mm=1.5, tick_mm=2.5, mask=0.3,
                               labels=[_lab_m(b - a) for a, b in zip(pts[:-1], pts[1:])])
        if len(pts) >= 2:
            g0 = len(lab.pl.geoms)
            lab.pl.place(lab.vp, fn, [4.0, 6.0, 8.0, 10.0, 13.0, 16.0], penalty_step=0.3)
            lab.bump(g0)
    chain(xs_s, "h", ymin_all, -1.0)
    chain(xs_n, "h", y1, +1.0)
    chain(ys_w, "v", xmin_all, -1.0)
    chain(ys_e, "v", x1, +1.0)


def _lab_m(v):
    return fmt.num(fmt.round_half_up(round(abs(v) * 100.0, 6)) / 100.0, 2)


def _levels(lab, s, used, all_existing=True, projected=True, existing=True, co=2.0, co_rowne=5.0):
    """Rzędne: projektowane (punkty modelu, tarasy/podesty), istniejące (siatka pikiet — poza strefą zmian terenu,
    gdzie obowiązują rzędne projektowane)."""
    if projected:
        _levels_proj(lab, s, used, co, co_rowne)
    if not existing:
        return
    zone = s.strefa_zmian.buffer(0.5) if not s.strefa_zmian.is_empty else None
    for p in s.pkt_ist:
        if lab.bounds is not None and not lab.bounds.contains(Point(p[:2])):
            continue
        if s.p0.buffer(0.2).contains(Point(p[:2])) or (zone is not None and zone.contains(Point(p[:2]))):
            continue
        pos, _c = D.spot(lab, p[:2], p[2], projected=False, max_cost=None if all_existing else 4.0,
                         dists=(0.6, 1.5, 3.0, 5.0, 8.0))
        if pos is not None:
            used.add("spot_ist")


def proj_do_opisu(P, co=2.0, co_rowne=5.0):
    """Rzędne projektowane do opisu na rysunku. Model może podawać gęsty TIN (np. pierścienie co 0,25 m wokół
    budynku — definicja ukształtowania terenu), a opisuje się punkty charakterystyczne: najpierw rzędne rzadkie
    (podesty, dojścia, niecki), potem powtarzalne (pierścienie); punkt jest pomijany, gdy leży bliżej niż ``co`` [m]
    od już wybranego albo bliżej niż ``co_rowne`` od wybranego o tej samej opisywanej rzędnej (0,01 m).
    ``co`` ≤ 0 — wszystkie punkty (dawne zachowanie)."""
    P = np.asarray(P, float).reshape(-1, 3)
    if len(P) == 0 or co <= 0:
        return P
    hr = np.round(P[:, 2], 2)
    _u, inv, cnt = np.unique(hr, return_inverse=True, return_counts=True)
    order = sorted(range(len(P)), key=lambda i: (cnt[inv[i]], i))
    sel = []
    for i in order:
        x, y = P[i, 0], P[i, 1]
        if all(not (d < co or (d < co_rowne and hr[j] == hr[i])) for j in sel
               for d in (float(np.hypot(P[j, 0] - x, P[j, 1] - y)),)):
            sel.append(i)
    return P[sorted(sel)]


def _levels_proj(lab, s, used, co=2.0, co_rowne=5.0):
    for t in s.tarasy:
        if t["rz"] is None:
            continue
        pg = t["poly"].difference(s.p0)
        if pg.area < 0.5:
            continue
        D.spot(lab, np.asarray(pg.representative_point().coords[0]), s.zero_abs + float(t["rz"]), projected=True)
    for p in proj_do_opisu(s.pkt_proj, co, co_rowne):
        pos, _c = D.spot(lab, p[:2], p[2], projected=True, dists=(0.6, 1.5, 3.0, 5.0, 8.0, 11.0, 14.0))
        if pos is not None:
            used.add("spot_proj")


def view_szczegoly(ctx, spec, scale, opts):
    """PZT-02: PLAN SZCZEGÓŁOWY — WYMIARY I RZĘDNE (1:200)."""
    title = spec.get("tytul_widoku") or spec.get("tytul") or "PLAN SZCZEGÓŁOWY — WYMIARY I RZĘDNE"
    vp = Viewport(scale, title)
    k = vp.k
    s = _site(ctx, opts)
    used = set()
    wb = detail_window(s, opts)
    win = box(*wb)
    lab = D.Labeler(vp, bounds=win)
    zj_todo = _draw_context(vp, s, lab, win, used, hatch=False, lawn=False, zone=False, utilities_ist=False)
    if opts.get("warstwice", True):
        D.draw_contours(vp, s, win, used, exclude=_contour_mask(s))
    if opts.get("warstwice_projektowane", False):
        D.draw_contours(vp, s, win, used, projected=True, exclude=s.footprint.buffer(0.2))
    D.draw_drainage(vp, s, used, detail=True)
    D.draw_downpipes(vp, s, used)
    D.draw_building(vp, s, used, slab_lt=str(opts.get("linia_plyt", "PUNKTOWA")).upper())
    tycz = punkty_tyczenia(s)
    for nm, p in tycz:
        D.tyczenie_mark(vp, p)
    if tycz:
        used.add("tyczenie")
    vp.rect(*wb, "Z-MAPA-RAMKA", pen=0.25, lt="CIAGLA")
    D.register_all(lab)
    W = wskazniki(s)
    _labels_building(lab, s, W)
    used.add("zero")
    _label_garage(lab, s)
    for nm, p in tycz:
        lab.label(p, [nm], D.H, "Z-TYCZENIE", style="bold", dists=(1.2, 2.5, 4.0, 6.0, 9.0), leader_from=3.0,
                  dirs=[(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)])
    _dims_plan(lab, s, used, detail=True)
    _chains(lab, s)
    for u in s.utwardzenia:
        if u["poly"].area > 3.0 and not any(w_ in str(u["raw"].get("nawierzchnia", "")) for w_ in
                                            ("fundament", "pojemnik")):
            _rect_dims(lab, u["poly"])
    zew = [q for q in s.miejsca if q["poly"].difference(s.p0).area > 0.1]
    if zew:
        _rect_dims(lab, zew[0]["poly"], offs=(2.0, 4.0, 6.0))
    for b in s.bramy:
        d = b["kier"]
        D.place_dim(lab, b["xy"] - d * b["szer"] / 2, b["xy"] + d * b["szer"] / 2,
                    shifts=[-3.0 * k, 3.0 * k, -5.0 * k, 5.0 * k, -7.0 * k])
    if s.pc is not None:
        g = next((g_ for g_ in s.granice if g_["strona"] == "E"), None)
        if g is not None:
            a, b = nearest_points(s.pc["body"], g["seg"])
            D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_a=s.pc["body"].boundary, on_b=g["seg"], span=2.0, step=0.1)
    for nm, geom in (("ZB", (s.zbiornik or {}).get("draw_poly")), ("NCH", (s.rozsaczanie or {}).get("poly"))):
        if geom is None:
            continue
        a, b = nearest_points(geom, s.footprint)
        D.place_dim(lab, (a.x, a.y), (b.x, b.y), span=2.0, step=0.25)
        gw = min(s.granice, key=lambda g_: g_["seg"].distance(geom))
        a, b = nearest_points(geom, gw["seg"])
        D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_b=gw["seg"], span=3.0, step=0.25)
    _levels(lab, s, used, existing=False, co=float(opts.get("rzedne_proj_co", 2.0)),
            co_rowne=float(opts.get("rzedne_proj_co_rowne", 5.0)))
    _drain_labels(lab, s)
    _labels_project(lab, s, W, used, detail=True, utilities=False)
    _levels(lab, s, used, projected=False)
    _slopes(lab, s, used)
    lab.fix_overlaps()
    # tabele obok rysunku
    x_t = wb[2] + 8.0 * k
    r1 = D.vp_table(vp, x_t, wb[3], **_tab_tyczenie(s, tycz))
    r2 = D.vp_table(vp, x_t, r1[1] - 6.0 * k, **_tab_rzedne(s, W))
    r3 = D.vp_table(vp, x_t, r2[1] - 6.0 * k, **_tab_odwodnienie(s))
    r3 = D.vp_table(vp, x_t, r3[1] - 6.0 * k, **_tab_nawierzchnie(s))
    D.vp_table(vp, x_t, r3[1] - 6.0 * k, **_tab_retencja(koordynacja(s, opts.get("odleglosci_min"),
                                                                     opts.get("retencja_min")), s))
    res = SiteResult(site=s, braki=s.braki)
    res.column_blocks = [("legenda", D.legend_block(used))]
    res.notes = _notes_szczegoly(s, zj_todo)
    if lab.failed:
        ctx.note("PZT-02", f"nie umieszczono {len(lab.failed)} opisów: {[f[0] for f in lab.failed][:8]}")
    return vp, res, title


def _tab_tyczenie(s, tycz):
    rows = [[nm, mm(p[0]), mm(p[1]), "narożnik obrysu parteru"] for nm, p in tycz]
    for i, p in enumerate(s.corners):
        rows.append([chr(ord("A") + i), mm(p[0]), mm(p[1]), "punkt graniczny działki"])
    return dict(title="WYKAZ PUNKTÓW TYCZENIA I GRANICZNYCH", cols=[("Pkt", 0), ("x [m]", 0), ("y [m]", 0), ("Opis", 0)],
                rows=rows, align=["center", "right", "right", "left"],
                notes=["Układ lokalny działki: początek — narożnik A, x → wschód, y → północ. W projekcie rzeczywistym "
                       "współrzędne w układzie PL-2000 (X — północ, Y — wschód) z mapy do celów projektowych; tyczenie "
                       "— geodeta uprawniony (PB art. 43 ust. 1)."], max_w_mm=120.0)


def _tab_rzedne(s, W):
    z0 = s.zero_abs
    rows = [["±0,00 — posadzka parteru", mm(z0)]]
    for t in s.tarasy:
        if t["rz"] is not None:
            rows.append([f"{t['id']} — {_short(t['naw'], 18)}", mm(z0 + float(t["rz"]))])
    h, src = s.teren_przy_wejsciu()
    if h is not None:
        rows.append(["teren proj. przy wejściu głównym", mm(h)])
    wz = W["wys"]
    rows.append(["teren na obwodzie ścian — min.", mm(wz["t_min"])])
    rows.append(["teren na obwodzie ścian — maks.", mm(wz["t_max"])])
    rows.append(["najwyższy punkt budynku", mm(wz["z_top_abs"])])
    if s.zwg is not None:
        rows.append(["zwierciadło wody gruntowej (ZWG)", mm(float(s.zwg))])
    return dict(title="RZĘDNE CHARAKTERYSTYCZNE [m n.p.m.]", cols=[("Poziom", 0), ("Rzędna", 0)], rows=rows,
                align=["left", "right"], max_w_mm=120.0,
                notes=["Rzędne projektowane terenu: spadek ≥ 2 % od budynku; na granicach działki rzędne istniejące "
                       "(bez zmiany spływu na działki sąsiednie — WT § 29, PW art. 234)."])


def _tab_odwodnienie(s):
    rows = []
    for o in s.odwodnienia:
        if o["typ"] == "drenaz_opaskowy":
            continue
        g = o["geom"]
        wym = f"L = {mm(g.length)} m" if g is not None and g.length > 0.05 else \
            (f"A = {m2(o['poly'].area)}" if o["poly"] is not None and o["typ"] != "opaska_zwirowa" else
             f"b = {mm(float(o['szer'] or 0))} m")
        sp = f"{fmt.num(float(o['spadek']) * 100, 1)} %" if o["spadek"] else "—"
        typ = {"liniowe": "liniowe", "niecka": "niecka", "opaska_zwirowa": "opaska żwir."}.get(o["typ"], o["typ"])
        rows.append([o["id"], typ, wym, sp, _short(o["odb"], 20) or "—"])
    notes = [f"{o['id']}: {o['opis']}" for o in s.odwodnienia if o["typ"] == "drenaz_opaskowy"]
    return dict(title="ODWODNIENIE POWIERZCHNIOWE", cols=[("Ozn.", 0), ("Typ", 0), ("Wymiar", 0), ("Spadek", 0),
                                                           ("Odbiornik", 0)],
                rows=rows, align=["left", "left", "right", "right", "left"], notes=notes, max_w_mm=120.0)


def _tab_nawierzchnie(s):
    rows = []
    for u in s.utwardzenia:
        sp = float(u["raw"].get("spadek") or 0.0)
        rows.append([u["id"], _short(u["raw"].get("nawierzchnia"), 26), m2(u["poly"].difference(s.p0).area),
                     f"{fmt.num(sp * 100, 1)} %" if sp else "—"])
    for t in s.tarasy:
        rows.append([t["id"], _short(t["naw"], 26), m2(t["poly"].difference(s.p0).area),
                     f"rz. {mm(s.zero_abs + float(t['rz']))}" if t["rz"] is not None else "—"])
    return dict(title="NAWIERZCHNIE UTWARDZONE I TARASY", cols=[("Ozn.", 0), ("Nawierzchnia", 0), ("Pow.", 0),
                                                                 ("Spadek", 0)],
                rows=rows, align=["left", "left", "right", "right"], max_w_mm=120.0,
                notes=["Kierunek spadku — strzałki na rysunku (od budynku, do odwodnień liniowych i niecek)."])


def _notes_szczegoly(s, zj_todo):
    out = ["Wymiary obrysu — lico zewnętrzne ścian parteru (1,0 m nad terenem); odległości od granic w miejscu "
           "najmniejszego oddalenia (WT § 9), z dokładnością 0,01 m (RPB § 15 ust. 3 w brzmieniu Dz.U. 2026 poz. 597, "
           "od 5.11.2026 — stosowane).",
           "Rzędne terenu istniejącego — z mapy (przykładowej); projektowanego — z modelu (dzialka.yaml: "
           "teren.punkty_projektowane); spadki nawierzchni wg modelu, kierunek wg terenu projektowanego; kierunki "
           "spływu na trawnikach — wg spadku terenu projektowanego (interpolacja).",
           "Wody opadowe z nawierzchni i dachów — na teren własny, do niecek i zbiornika (WT § 28 ust. 2); zakaz "
           "zmiany spływu w kierunku działek sąsiednich (WT § 29) i odprowadzania na drogę (u.d.p. art. 39).",
           "Punkty tyczenia — narożniki obrysu zewnętrznego ścian parteru; współrzędne w wykazie obok rysunku."]
    if zj_todo:
        out.append(f"Zjazd — geometria zastępcza {D_TODO} (wg zezwolenia zarządcy drogi).")
    if s.braki:
        out.append(f"Braki danych modelu oznaczono {D_TODO}; wykaz: projekt/02_PZT/BRAKI_DANYCH.md.")
    return out


def _util_labels(lab, s, used):
    """Opisy sieci projektowanych (litera wzdłuż + opis z długością) i istniejących (w pasie drogowym)."""
    h = D.H
    for sx in [x for x in s.sieci if not x.istn]:
        g = sx.geom.difference(s.p0) if not s.p0.is_empty else sx.geom
        parts = sorted(getattr(g, "geoms", [g]), key=lambda q: -q.length)
        if not parts or parts[0].is_empty:
            continue
        for part in parts[:2]:
            lab.along(part, sx.lit, h, "Z-SIECI-PROJ", sx.kolor, n=2 if part.length > 8 else 1, max_cost=6.0,
                      mask=0.25)
        L = sx.geom.length
        txt = [f"{_sid(sx)} — {D.short_desc(sx.opis, 34)}", f"L = {mm(L)} m" + (
            f" (model: {mm(float(sx.dl))} m)" if sx.dl is not None and abs(float(sx.dl) - L) > 0.05 else "")]
        anchors = [np.asarray(parts[0].interpolate(f, normalized=True).coords[0]) for f in (0.5, 0.35, 0.65, 0.2, 0.8)]
        lab.label(anchors, txt, h, "Z-SIECI-PROJ", color=sx.kolor, dists=(3.0, 6.0, 9.0, 13.0, 18.0),
                  leader_from=2.0, dot=True)
    for sx in [x for x in s.sieci if x.istn]:           # opisy sieci istniejących — w tabeli obok rysunku
        g = D.clip(sx.geom, lab.bounds)
        if g is None:
            continue
        for part in getattr(g, "geoms", [g]):
            lab.along(part, sx.lit, h, "Z-SIECI-IST", sx.kolor, n=3, max_cost=10.0, mask=0.2)


def _inst_points(vp, lab, s, used):
    """Punkty instalacji w budynku (wodomierz, rozdzielnica) — symbol i opis."""
    k = vp.k
    names = {"wodomierz": ("WM", "wodomierz (w budynku)"), "RG": ("RG", "rozdzielnica główna RG")}
    done = []
    for key, (sym, txt) in names.items():
        p = s.inst.get(key)
        if p is None:
            continue
        n0 = lab.mark()
        from ..draft import text as T
        a, b = (T.width(sym, D.H) / 2.0 + 0.6) * k, (D.H / 2.0 + 0.6) * k
        D.fill_white(vp, box(p[0] - a, p[1] - b, p[0] + a, p[1] + b), z=21.0)
        vp.rect(p[0] - a, p[1] - b, p[0] + a, p[1] + b, "Z-UZBROJENIE", pen=0.35)
        vp.text(p, sym, D.H, 0.0, "center", "middle", "Z-UZBROJENIE")
        used.add("inst_" + key)
        lab.reg(n0)
        done.append((p, txt))
    for p, txt in done:
        lab.label(p, [txt], D.H, "Z-UZBROJENIE", dists=(4.0, 6.0, 9.0, 12.0), leader_from=2.0, dot=False)


def view_uzbrojenie(ctx, spec, scale, opts):
    """PZT-03: RYSUNEK KOORDYNACYJNY UZBROJENIA TERENU (1:200)."""
    title = spec.get("tytul_widoku") or spec.get("tytul") or "RYSUNEK KOORDYNACYJNY UZBROJENIA TERENU"
    vp = Viewport(scale, title)
    k = vp.k
    s = _site(ctx, opts)
    used = set()
    wb = detail_window(s, opts, 2.5)
    win = box(*wb)
    lab = D.Labeler(vp, bounds=win)
    K = koordynacja(s, opts.get("odleglosci_min"), opts.get("retencja_min"))
    zj_todo = _draw_context(vp, s, lab, win, used, hatch=False, lawn=False, zone=True, utilities_ist=True)
    D.draw_drainage(vp, s, used, detail=True)
    D.draw_downpipes(vp, s, used)
    D.draw_building(vp, s, used, slab_lt=str(opts.get("linia_plyt", "PUNKTOWA")).upper(), pen_outline=1.0)
    D.draw_utilities(vp, s, used, win, inside=s.p0)
    D.draw_objects(vp, s, used, win)
    for i, x in enumerate(K["skrzyzowania"]):
        vp.circle(x["p"], 1.2 * k, "Z-KOLIZJE", pen=0.25)
        used.add("skrzyzowanie")
    kol = [c_ for c_ in K["kolizje"]]
    for i, c_ in enumerate(kol):
        vp.circle(c_["p"], 2.6 * k, "Z-KOLIZJE", pen=0.5)
        used.add("kolizja")
    vp.rect(*wb, "Z-MAPA-RAMKA", pen=0.25, lt="CIAGLA")
    D.register_all(lab)
    _labels_building(lab, s, wskazniki(s))
    used.add("zero")
    _inst_points(vp, lab, s, used)
    for i, c_ in enumerate(kol):
        lab.label(c_["p"], [f"K{i + 1}"], D.H, "Z-KOLIZJE", style="bold", dists=(3.0, 4.5, 6.5, 9.0),
                  leader_from=3.5, leader_color=None)
    for i, x in enumerate(K["skrzyzowania"]):
        lab.label(x["p"], [f"S{i + 1}"], D.H, "Z-KOLIZJE", dists=(1.5, 3.0, 5.0, 8.0), leader_from=2.4)
    # wymiary: odległości między sieciami (projektowane, < 3 m), sieć–drzewo, retencja
    for r in K["pary"]:
        if r["b"].istn or r["d"] > r["req"] + 1.0:
            continue
        a, b = nearest_points(r["a"].geom, r["b"].geom)
        if D.place_dim(lab, (a.x, a.y), (b.x, b.y), on_a=r["a"].geom, on_b=r["b"].geom, span=4.0, step=0.25,
                       max_cost=10.0) is not None:
            used.add("wymiar")
    for r in K["drzewa"]:
        if r["d"] < r["req"] + 2.0:
            a, b = nearest_points(r["a"].geom, Point(r["t"]["xy"]))
            D.place_dim(lab, (a.x, a.y), (b.x, b.y), shifts=[0.0])
    for r in K.get("budynek", []):
        if r["d"] < 2.0 and r["d"] > 0.05:
            D.place_dim(lab, r["p1"], r["p2"], on_a=r["a"].geom, on_b=s.footprint.boundary, span=3.0, step=0.25,
                        max_cost=10.0)
    _util_labels(lab, s, used)
    for o in s.obiekty.values():
        if win.contains(Point(o.xy)) and not o.id.upper().startswith("PC"):
            lab.label(o.xy, [o.id], D.H, dists=(2.0, 3.5, 5.0, 7.0, 10.0), leader_from=1.8, dot=False)
    if s.pc is not None:
        lab.label(np.asarray(s.pc["body"].centroid.coords[0]), ["PC — jedn. zewn. (R290)",
                                                                f"strefa r = {mm(s.pc['r'])} m"], D.H, dot=True,
                  dists=(3.0, 6.0, 9.0, 13.0))
    if s.zbiornik:
        lab.label(s.zbiornik["xy"], [f"ZB — zbiornik {fmt.num(float(s.zbiornik['V'] or 0), 1)} m³",
                                     f"wym. i rzędne {D_TODO}"], D.H, dot=True, dists=(4.0, 7.0, 10.0, 14.0))
    if s.rozsaczanie and s.rozsaczanie["poly"] is not None:
        lab.label(np.asarray(s.rozsaczanie["poly"].centroid.coords[0]), ["NCH — niecka chłonna"], D.H,
                  dists=(0.0, 3.0, 6.0))
    for r in s.rury:
        lab.label(r["xy"], [r["id"]], D.H, "Z-ODWODNIENIE", dists=(1.2, 2.5, 4.0, 6.0), leader_from=2.4)
    for t in s.drzewa:
        if win.contains(Point(t["xy"])):
            lab.label(t["xy"], [t["id"]], D.H, dists=(0.8, 2.0, 4.0), leader_from=2.5, max_cost=6.0)
    lab.fix_overlaps()
    x_t = wb[2] + 8.0 * k
    y = wb[3]
    for t in (_tab_przylacza(s), _tab_obiekty(s, win), _tab_koord(K), _tab_skrzyz(K), _tab_kolizje(K)):
        r = D.vp_table(vp, x_t, y, **t)
        y = r[1] - 5.0 * k
    res = SiteResult(site=s, braki=s.braki)
    res.column_blocks = [("legenda", D.legend_block(used))]
    res.notes = _notes_uzbrojenie(s, K, zj_todo)
    res.dane = dict(koordynacja=dict(pary=[(r["a"].lit, r["b"].lit, round(r["d"], 3), r["req"], r["ok"])
                                           for r in K["pary"]], kolizje=[c_["opis"] for c_ in kol],
                                     skrzyzowania=len(K["skrzyzowania"])))
    if lab.failed:
        ctx.note("PZT-03", f"nie umieszczono {len(lab.failed)} opisów: {[f[0] for f in lab.failed][:8]}")
    return vp, res, title


def _tab_przylacza(s):
    rows = []
    for x in [q for q in s.sieci if not q.istn]:
        L = x.geom.length
        rows.append([_sid(x), BRANZE.get(x.branza, ("", x.branza))[1].split(" / ")[-1], D.short_desc(x.opis, 30),
                     mm(L), mm(float(x.dl)) if x.dl is not None else "—"])
    for x in [q for q in s.sieci if q.istn]:
        rows.append([_sid(x), "istniejąca (mapa)", D.short_desc(x.opis, 30), "—", "—"])
    return dict(title="SIECI I PRZYŁĄCZA — PROJEKTOWANE I ISTNIEJĄCE",
                cols=[("Ozn.", 0), ("Sieć", 0), ("Opis", 0), ("L [m]", 0), ("L model [m]", 0)],
                rows=rows, align=["left", "left", "left", "right", "right"], max_w_mm=150.0,
                notes=["L — długość trasy w rzucie (z częścią pod budynkiem, linia kreskowa); średnice, spadki i "
                       f"rzędne dna przewodów {D_TODO} (RPB § 15 ust. 2 pkt 11 — brak w modelu)."])


def _sid(x):
    """Oznaczenie sieci w tabelach: litera + numer kolejny w branży (np. kd2); istniejące — z „ist.”."""
    return f"{x.lit}{x.nr}" + (" ist." if x.istn else "") if getattr(x, "nr", None) else x.lit + (" ist." if x.istn else "")


def _tab_istn(s):
    rows = [[x.lit, D.short_desc(x.opis, 44)] for x in s.sieci if x.istn]
    return dict(title="SIECI ISTNIEJĄCE (wg mapy)", cols=[("Ozn.", 0), ("Opis", 0)], rows=rows or [["—", "brak"]],
                align=["center", "left"], max_w_mm=150.0)


def _tab_obiekty(s, win):
    rows = [[o.id, D.short_desc(o.opis, 52)] for o in s.obiekty.values()]
    rows += [[r["id"], f"rura spustowa DN{r['dn']} ({'zewn.' if r['trasa'] == 'zewn' else 'w szachcie'}) z dachu "
                       f"{r['dach']}"] for r in s.rury]
    return dict(title="OBIEKTY UZBROJENIA I ODWODNIENIA", cols=[("Ozn.", 0), ("Opis", 0)], rows=rows,
                align=["center", "left"], max_w_mm=150.0)


def _tab_koord(K):
    rows = []
    for r in K["pary"]:
        st = "TAK" if r["ok"] else ("warunk." if r.get("warunkowo") else "NIE")
        nm = f"{_sid(r['a'])} – {_sid(r['b'])}"
        rows.append([nm, mm(r["d"]), mm(r["req"]), str(r["src"]).replace(" [SPRAWDŹ]", "*"), st])
    for r in K["drzewa"]:
        rows.append([f"{_sid(r['a'])} – {r['t']['id']} (pień)", mm(r["d"]), mm(r["req"]), "od pnia*",
                     "TAK" if r["ok"] else "NIE"])
    for r in K.get("budynek", []):
        rows.append([f"{_sid(r['a'])} – budynek", mm(r["d"]), "—", "informacyjnie (lico ściany)", "—"])
    if not rows:
        rows.append(["—", "", "", "brak zbliżeń < 3 m", ""])
    return dict(title="KOORDYNACJA — ODLEGŁOŚCI POZIOME MIĘDZY SIECIAMI",
                cols=[("Para sieci", 0), ("d [m]", 0), ("min [m]", 0), ("Źródło wymagania", 0), ("Zgodność", 0)],
                rows=rows, align=["left", "right", "right", "left", "center"], max_w_mm=150.0,
                notes=["* wartości minimalne wg zasad wiedzy technicznej (N SEP-E-004, praktyka projektowa) — NIE są "
                       "przepisem: WT § 26–28 określają tylko wymagania ogólne uzbrojenia działki; do potwierdzenia w "
                       "warunkach przyłączenia gestorów [SPRAWDŹ]. „warunk.” — dopuszczalne przy rurach osłonowych."])


def _tab_skrzyz(K):
    rows = [[f"S{i + 1}", f"{_sid(x['a'])} × {_sid(x['b'])}", mm(x["p"][0]),
             mm(x["p"][1])] for i, x in enumerate(K["skrzyzowania"])]
    if not rows:
        rows = [["—", "brak skrzyżowań", "", ""]]
    return dict(title="SKRZYŻOWANIA SIECI", cols=[("Nr", 0), ("Sieci", 0), ("x [m]", 0), ("y [m]", 0)], rows=rows,
                align=["center", "left", "right", "right"], max_w_mm=150.0,
                notes=[f"Odstępy pionowe na skrzyżowaniach — wg warunków gestorów sieci {D_TODO} (brak rzędnych "
                       "przewodów w modelu); kable w rurach osłonowych w obrębie skrzyżowań."])


def _tab_kolizje(K):
    rows = [[f"K{i + 1}", c_["typ"], c_["opis"].replace(".", ","), "warunk." if c_.get("warunkowo") else "KOLIZJA"]
            for i, c_ in enumerate(K["kolizje"])]
    notes = [f"K{i + 1}: {c_.get('uwaga') or c_.get('src', '')}" for i, c_ in enumerate(K["kolizje"])]
    if not rows:
        rows = [["—", "brak kolizji", "", ""]]
    return dict(title="KOLIZJE I ZBLIŻENIA", cols=[("Nr", 0), ("Rodzaj", 0), ("Opis", 0), ("Ocena", 0)], rows=rows,
                align=["center", "left", "left", "center"], notes=notes, max_w_mm=150.0)


def _tab_retencja(K, s):
    rows = [[r["el"], r["od"], mm(r["d"]), mm(r["req"]), "TAK" if r["ok"] else "NIE"] for r in K["retencja"]]
    if s.pc is not None:
        rows.append(["strefa R290", "otwory, wpusty, studzienki", "—", f"r = {mm(s.pc['r'])}",
                     "TAK" if not K["r290"] else "NIE"])
    return dict(title="ODLEGŁOŚCI URZĄDZEŃ RETENCJI I PC", cols=[("Element", 0), ("Od", 0), ("d [m]", 0),
                                                                  ("min [m]", 0), ("Zgodność", 0)],
                rows=rows, align=["left", "left", "right", "right", "center"], max_w_mm=150.0,
                notes=["Wymagania retencji — założenia projektowe (R8 pkt 3.5, W-144/W-145; nie przepis); zbiornik "
                       "— odległość od środka (brak wymiarów w modelu); strefa R290 — W-156 (wytyczne producenta)."])


def _notes_uzbrojenie(s, K, zj_todo):
    out = ["Oznaczenia sieci — kolory i litery wg mapy zasadniczej (zał. 4 rozp. w sprawie BDOT500 i mapy zasadniczej, "
           "Dz.U. 2021 poz. 1385): w — wodociąg, ks — kanalizacja sanitarna, kd — kanalizacja deszczowa, "
           "e — elektroenergetyczna, t — telekomunikacyjna, g — gazowa; istniejące — linia cienka (wg mapy), "
           "projektowane — gruba; w budynku/pod płytą — kreskowa; „×” — włączenie do sieci.",
           "Przyłącza w granicach działki nie podlegają naradzie koordynacyjnej ZUD (PGiK art. 28b); roboty w pasie "
           "drogowym 1KDD — za zezwoleniem zarządcy drogi (u.d.p. art. 40).",
           f"Skrzyżowań: {len(K['skrzyzowania'])}; zbliżeń poniżej wartości minimalnych: "
           f"{sum(1 for c_ in K['kolizje'] if c_['typ'] == 'zbliżenie sieci')} (tabela „Kolizje i zbliżenia”).",
           "Wody opadowe: rury spustowe RS → kolektory kd → zbiornik ZB → przelew do niecki chłonnej NCH; "
           "odwodnienia liniowe OL → kolektory kd (WT § 28 ust. 2)."]
    for o in s.odwodnienia:
        if o["typ"] == "drenaz_opaskowy":
            out.append(f"Drenaż opaskowy {o['id']}: {o['opis']}")
    if s.braki:
        out.append(f"Braki danych modelu ({len(s.braki)} poz.) — {D_TODO}; wykaz: projekt/02_PZT/BRAKI_DANYCH.md.")
    return out


# ================================================================================================ rejestracja
register_view("pzt_plan", view_plan, "plan zagospodarowania", qa="PZT")
register_view("pzt_szczegoly", view_szczegoly, "plan szczegółowy", qa="PZT")
register_view("pzt_uzbrojenie", view_uzbrojenie, "rysunek koordynacyjny", qa="PZT")


# ================================================================================================ braki danych
def braki_md(ctx, opts=None) -> str:
    """Wykaz braków danych modelu dla PZT (Markdown) — ``projekt/02_PZT/BRAKI_DANYCH.md``."""
    import datetime as _dt
    s = SiteData(ctx, opts or {})
    W = wskazniki(s)
    items = list(s.braki)
    h = W["wys"]
    if h.get("zalozenie"):
        from .site_data import Brak
        items.append(Brak("budynek.yaml: energia.wentylacja.wywiewki_kanalizacyjne[] — rzędna z",
                          f"rzędna wylotu wywiewki kanalizacyjnej (element najwyższy dla wysokości zabudowy, upzp "
                          f"art. 2 pkt 30 lit. a) — przyjęto wierzch pokrycia + 0,50 m; bez założenia "
                          f"H = {mm(h['bez_zalozen'][0])} m", "wywiewki_kanalizacyjne: [[5.57, 6.2, 10.05]]  # [x, y, z]",
                          "PZT-01 (tabela wskaźników), lamela.wskazniki"))
    pv = ((s.m.raw.get("energia") or {}).get("pv") or {})
    if isinstance(pv, dict) and pv and pv.get("z_max") is None:
        from .site_data import Brak
        items.append(Brak("budynek.yaml: energia.pv.z_max", "rzędna górnej krawędzi modułów PV (element wliczany do "
                          "wysokości zabudowy) — obecnie tylko w tekście 'uwagi'", "pv: {..., z_max: 9.78}",
                          "PZT-01, lamela.wskazniki"))
    L = ["# PZT — braki danych w modelu (dzialka.yaml / budynek.yaml)", "",
         f"Wygenerowano: {_dt.date.today().isoformat()} — `lamela.views.site.braki_md` (generator rysunków PZT). "
         "Model NIE był edytowany; na rysunkach PZT-01…03 elementy oparte na danych zastępczych oznaczono "
         f"**{D_TODO}**. Proponowane formaty pól — zgodne z `docs/SCHEMAT_MODELU.md` §3 (dzialka.yaml) i §6 "
         "(rozszerzenia wody/odwodnienia).", "",
         "Regeneracja: `PYTHONPATH=src python3 -m lamela.views.site --braki projekt/02_PZT/BRAKI_DANYCH.md`", "",
         "| # | Pole modelu | Czego brakuje / do czego potrzebne | Proponowany format pola | Rysunki |",
         "|---|---|---|---|---|"]
    esc = lambda t: str(t).replace("|", "\\|")      # noqa: E731 — kreska pionowa w komórce tabeli Markdown
    for i, b in enumerate(items):
        L.append(f"| {i + 1} | `{esc(b.pole)}` | {esc(b.opis)} | `{esc(b.propozycja)}` | {esc(b.arkusze)} |")
    L += ["", "## Założenia przyjęte na rysunkach do czasu uzupełnienia", "",
          "* Limity MPZP — z konfiguracji `model/arkusze_pzt.yaml: wspolne.mpzp` (brief § 3, fikcyjny MPZP 3MN).",
          "* Zjazd — przedłużenie bramy przesuwnej do krawędzi jezdni ze skosami 1,0 m (linia kreskowa).",
          "* Zbiornik retencyjny — symbol umowny 7 × 4 mm (PN-B-01027 poz. 6); do PBC wyłączono rzut ≈ max(2,0; V/1,6) "
          "m² (jak audyt A1).",
          "* Strefa R290 — promień odczytany z tekstu 'opis' obiektu PC-JZ (1,0 m).",
          "* Liczba kondygnacji budynków sąsiednich — odczytana z tekstu 'opis' (opis BDOT500 „m2”).",
          "* Minimalne odległości między sieciami — zasady wiedzy technicznej z `arkusze_pzt.yaml` (nie przepis).", ""]
    return "\n".join(L)


if __name__ == "__main__":      # PYTHONPATH=src python3 -m lamela.views.site --braki projekt/02_PZT/BRAKI_DANYCH.md
    import argparse
    from pathlib import Path as _P
    from ..ir import build_ir
    from ..model import load_model
    from .sheets import load_config, make_context
    ap = argparse.ArgumentParser()
    ap.add_argument("--budynek", default="model/budynek.yaml")
    ap.add_argument("--dzialka", default="model/dzialka.yaml")
    ap.add_argument("--arkusze", default="model/arkusze_pzt.yaml")
    ap.add_argument("--braki", default="projekt/02_PZT/BRAKI_DANYCH.md")
    a = ap.parse_args()
    _m = load_model(a.budynek, a.dzialka, strict=False)
    _cfg = load_config(a.arkusze, _m)
    _ctx = make_context(_m, build_ir(_m, otoczenie=True, auta=False), _cfg, [], src=a.budynek)
    _P(a.braki).parent.mkdir(parents=True, exist_ok=True)
    _P(a.braki).write_text(braki_md(_ctx), encoding="utf-8")
    print(f"zapisano {a.braki}")
