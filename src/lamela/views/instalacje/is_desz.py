"""IS-D — odwodnienie dachów: wpusty (DN, podgrzewanie), przelewy awaryjne, rury spustowe, spadki (``dachy[]`` modelu,
SCHEMAT § 6) z obliczeniami ``lamela.obliczenia.sanitarne.deszczowa`` (pola, Q, przepustowość wpustów i przelewów);
na rzucie parteru — rury spustowe, czyszczaki i włączenia do kolektorów KD (``dzialka.yaml``: uzbrojenie projektowane
kan_deszcz), odwodnienia liniowe przy budynku."""
from __future__ import annotations

import re

import numpy as np
from shapely.geometry import LineString, Polygon

from ...draft import dims, fmt, symbols as S
from ...draft.dims import arrowhead
from .baza import Rysunek
from .trasy import Siatka
from .wspolne import BRAK, num, table_block


def _ident(opis, default):
    m = re.match(r"^\s*(?:[\w ]*?\()?\s*([A-Z]{2}\d+)", str(opis or ""))
    if m:
        return m.group(1)
    m = re.search(r"\b((?:WP|PA|RS)\d+)\b", str(opis or ""))
    return m.group(1) if m else default


class RysD(Rysunek):
    kod = "IS-D"

    def run(self):
        self.podklad(meble=False)
        self.pola = {p.id: p for p in self.W.deszczowa.pola}
        self.leg.line("S-DESZCZ", "Kd — kanalizacja deszczowa: rury spustowe, podejścia od wpustów (PVC-U/PP, DN wg "
                      "obliczeń); linia kreskowa długa", lt="KRESKA_DLUGA")
        if self.dach:
            self.dachy()
        else:
            self.parter()
        self.opisy()
        self.braki_wspolne()
        return self.finish(rooms=not self.dach)

    # --------------------------------------------------------------------------------------------- dach
    def dachy(self):
        m = self.m
        n_wp = 0
        for d in m.dachy():
            try:
                poly = Polygon(d["obrys"])
            except Exception:
                continue
            did = str(d.get("id", ""))
            pole = self.pola.get(did)
            for sp in d.get("spadki") or []:
                a, b = np.asarray(sp["od"], float), np.asarray(sp["do"], float)
                L = float(np.hypot(*(b - a)))
                if L < 1.0:
                    continue
                u = (b - a) / L
                c = a + (b - a) * 0.45
                n0 = len(self.vp.prims)
                dims.slope(self.vp, c - u * 0.8, c + u * 0.8, float(sp.get("spadek", d.get("spadek", 0.02))) * 100,
                           layer="S-OPISY", h=1.8)
                self.reg(n0)
            wp = [w if isinstance(w, dict) else {"xy": w} for w in (d.get("wpusty") or [])]
            if not wp:
                self.brak(f"Dach {did}: wpusty", "brak wpustów w modelu (dachy[].wpusty)",
                          "wpusty: [{xy: [x, y], dn: 100, podgrzewany: true, opis}]")
            for i, w in enumerate(wp):
                n_wp += 1
                q = np.asarray(w["xy"], float)
                self.sym(S.floor_drain, q, 0.25, layer="S-DESZCZ", label=None)
                wid = _ident(w.get("opis"), f"WP{n_wp}")
                txt = [f"{wid} — wpust dachowy DN{w.get('dn', 100)}" + (", podgrzewany" if w.get("podgrzewany") else "")]
                self.tag(q, txt, "S-OPISY", style="bold")
            for j, p in enumerate(d.get("przelewy_awaryjne") or []):
                self.przelew(d, p, j)
            if not d.get("przelewy_awaryjne"):
                self.brak(f"Dach {did}: przelewy awaryjne", "brak przelewów awaryjnych (PN-EN 12056-3 p. 7)",
                          "przelewy_awaryjne: [{xy, sciana_attyki: N|S|E|W, szer, wys, rzedna_dna}]")
            for r in d.get("rury_spustowe") or []:
                self.rura(d, r, wp)
            if pole is not None:
                inner = poly.buffer(-0.3, join_style=2)
                from ..common import label_point
                from .wspolne import text_block
                lines = [f"DACH {did} — {pole.typ}", f"A = {num(pole.A, 1)} m², Q = {num(pole.Q, 2)} l/s",
                         f"pokrycie {fmt.level(pole.rzedna)}"]
                text_block(self.vp, self.pl, label_point(inner if not inner.is_empty else poly), lines, "S-OPISY",
                           bounds=inner if not inner.is_empty else None)
        # propozycje obliczeń (płyty wspornikowe, tarasy, świetliki) — brak odwodnienia w modelu
        for p in self.W.deszczowa.pola:
            for w in p.wpusty:
                if not w.get("propozycja"):
                    continue
                q = np.asarray(w["xy"], float)
                self.sym(S.floor_drain, q, 0.2, layer="I-BRAKI", label=None)
                self.tag(q, [f"{BRAK} odwodnienie {p.id} ({p.typ}, A = {num(p.A, 1)} m²)",
                             "wpust/rzygacz proponowany w obliczeniach"], "I-BRAKI", color="#b0008a")
                self.brak(f"Odwodnienie powierzchni {p.id}", f"{p.typ}, A = {num(p.A, 1)} m² — brak wpustów/rzygaczy "
                          "w modelu; w obliczeniach przyjęto wpust propozycyjny", "element `dachy` (SCHEMAT p. 5.1) albo "
                          "`wsporniki_plyty[].odwodnienie: {typ: wpust|rzygacz|okap, xy, dn, do}`")
        self.leg.sym(lambda c, p: S.floor_drain(c, p, 5.0, layer="S-DESZCZ", label=None),
                     "wpust dachowy (DN100, z grzałką — podgrzewany), wymiar rzeczywisty kosza")
        self.leg.sym(lambda c, p: dims.slope(c, p - np.array([6.0, 0.0]), p + np.array([6.0, 0.0]), 2.0,
                                             layer="S-OPISY", h=1.8), "spadek połaci (izolacja spadkowa) do wpustów")

    def przelew(self, d, p, j):
        vp = self.vp
        q = np.asarray(p["xy"], float)
        side = str(p.get("sciana_attyki", "N")).upper()
        u = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}.get(side, (0, 1))
        u = np.array(u, float)
        t = np.array([-u[1], u[0]])
        at = float((d.get("attyka") or {}).get("szer", 0.25))
        w = float(p.get("szer", 0.2))
        a, b = q - u * at - t * w / 2, q + u * 0.05 + t * w / 2
        n0 = len(vp.prims)
        vp.polygon([a, a + u * (at + 0.05), b, b - u * (at + 0.05)], "S-DESZCZ", pen="srednia", lt="CIAGLA")
        vp.line(q, q + u * 0.45, "S-DESZCZ", pen="cienka", lt="CIAGLA")
        arrowhead(vp, q + u * 0.45, u, 2.0, 14, True, "S-DESZCZ")
        self.reg(n0)
        pid = _ident(p.get("opis"), f"PA{j + 1}")
        self.tag(q + u * 0.3, [f"{pid} — przelew awaryjny {num(100 * w, 0)}×{num(100 * float(p.get('wys', 0.1)), 0)} cm",
                               f"dno {fmt.level(float(p.get('rzedna_dna', 0)))}"], "S-OPISY")
        self.leg.sym(lambda c, pp: (c.polygon([pp + np.array([-2.0, -1.5]), pp + np.array([2.0, -1.5]),
                                               pp + np.array([2.0, 1.5]), pp + np.array([-2.0, 1.5])], "S-DESZCZ",
                                              pen="srednia", lt="CIAGLA"),
                                    arrowhead(c, pp + np.array([6.0, 0.0]), np.array([1.0, 0.0]), 2.0, 14, True,
                                              "S-DESZCZ")),
                     "przelew awaryjny w attyce (PN-EN 12056-3 p. 7) — kierunek wypływu")

    def rura(self, d, r, wp):
        q = np.asarray(r.get("xy_pion") or (wp[int(r.get("od_wpustu", 0))]["xy"] if wp else (0, 0)), float)
        i = int(r.get("od_wpustu", 0))
        if wp and i < len(wp):
            w = np.asarray(wp[i]["xy"], float)
            if float(np.hypot(*(w - q))) > 0.05:
                path = [w, np.array([q[0], w[1]]), q] if abs(w[0] - q[0]) > 0.02 and abs(w[1] - q[1]) > 0.02 \
                    else [w, q]
                self.pipe(path, "KD", lt="KRESKOWA")
                self.label(path, f"Kd DN{r.get('dn', 100)} — podejście " + ("w suficie podwieszanym (izolowane)"
                                                                            if r.get("trasa") == "wewn_szacht"
                                                                            else "poziome"), "S-OPISY")
        self.sym(S.riser, q, None, "KD", s_mm=2.8)
        rid = str(r.get("id", "RS"))
        dest = {"zbiornik": "zbiornik retencyjny", "niecka": "niecka chłonna", "kanal": "kanał"}.get(
            str(r.get("do")), str(r.get("do")))
        trasa = "w szachcie / wewnątrz budynku" if str(r.get("trasa", "")).startswith("wewn") else "zewnętrzna"
        self.tag(q, [f"{rid} — rura spustowa DN{r.get('dn', 100)}, {trasa}", f"→ {dest}"], "S-OPISY", style="bold")
        self.leg.sym(lambda c, p: S.riser(c, p, None, "KD", s_mm=2.8), "rura spustowa (pion deszczowy)")

    # --------------------------------------------------------------------------------------------- parter
    def parter(self):
        m = self.m
        rury = [(d, r) for d in m.dachy() for r in (d.get("rury_spustowe") or [])]
        kd = self.linie_dzialki("kan_deszcz")
        outl = self.pod.outline
        box_ = outl.buffer(3.0, join_style=2)
        lines = []
        for arr_, u in kd:
            ln = LineString(arr_).intersection(box_)
            for g in getattr(ln, "geoms", [ln]):
                if g.is_empty or g.length < 0.2:
                    continue
                a = np.asarray(g.coords)
                self.pipe(a, "KD", pen="gruba", lt="KRESKA_DLUGA")
                self.label(a, (u.get("opis") or "kolektor KD").split("(")[0].strip() + " — dalej wg PZT", "S-OPISY")
                lines.append(LineString(a))
        if not kd:
            self.brak("Kolektory deszczowe", "brak tras kolektorów KD w dzialka.yaml",
                      "uzbrojenie.projektowane: [{branza: kan_deszcz, linia, opis, dl}]")
        x0, y0, x1, y1 = box_.bounds
        g2 = Siatka((x0, y0, x1, y1))
        tgt = None
        if lines:
            from shapely.ops import unary_union
            tgt = g2.mask(unary_union(lines).buffer(0.06))
        for d, r in rury:
            q = np.asarray(r.get("xy_pion") or (0, 0), float)
            self.sym(S.riser, q, None, "KD", s_mm=2.8)
            wewn = str(r.get("trasa", "")).startswith("wewn")
            txt = [f"{r.get('id', 'RS')} DN{r.get('dn', 100)} z dachu {d.get('id', '')}"]
            if wewn:
                txt.append("wyjście pod płytą do kolektora")
                self.sym(S.cleanout, q + np.array([0.15, -0.15]), 0.0, s_mm=2.2, label="")
            else:
                txt.append("czyszczak 0,5 m nad terenem, osadnik")
                self.sym(S.cleanout, q + np.array([0.15, 0.15]), 0.0, s_mm=2.2, label="")
            self.tag(q, txt, "S-OPISY", style="bold")
            if tgt is not None and tgt.any():
                path = g2.route(q, None, "KDP", turn=1.5, targets=tgt, margin=6.0)
                if len(path) >= 2:
                    self.pipe(path, "KD", lt="KRESKOWA")
        self.leg.sym(lambda c, p: S.riser(c, p, None, "KD", s_mm=2.8), "rura spustowa (pion deszczowy)")
        self.leg.sym(lambda c, p: S.cleanout(c, p, 0.0, s_mm=2.2, label=""), "czyszczak rury spustowej / rewizja")
        self.leg.line("S-DESZCZ", "przewody deszczowe pod płytą i w gruncie (PVC-U SN8) — linia kreskowa",
                      lt="KRESKOWA")
        # odwodnienia liniowe przy budynku (dzialka.yaml)
        D = (self.W.dane.dzialka or {}).get("transform")
        for o in (self.W.dane.dzialka or {}).get("odwodnienia") or []:
            if o.get("typ") != "liniowe" or not o.get("linia") or D is None:
                continue
            a = np.array(D.ring_bud(o["linia"]), float)
            if not LineString(a).intersects(box_):
                continue
            n0 = len(self.vp.prims)
            ln = LineString(a)
            for off in (-0.06, 0.06):
                g = ln.offset_curve(off)
                self.vp.polyline(np.asarray(g.coords), "S-DESZCZ", pen="cienka", lt="CIAGLA")
            self.reg(n0)
            self.tag(a[len(a) // 2], [f"{o.get('id', '')} odwodnienie liniowe → {o.get('odbiornik', '')}"], "S-OPISY")
            self.leg.sym(lambda c, p: (c.line(p + np.array([-6, 0.9]), p + np.array([6, 0.9]), "S-DESZCZ",
                                              pen="cienka", lt="CIAGLA"),
                                       c.line(p + np.array([-6, -0.9]), p + np.array([6, -0.9]), "S-DESZCZ",
                                              pen="cienka", lt="CIAGLA")),
                         "odwodnienie liniowe (korytko z rusztem) wg dzialka.yaml")

    # --------------------------------------------------------------------------------------------- opisy
    def opisy(self):
        ds = self.W.deszczowa
        d = ds.do_dict()
        self.notes += [
            "Odwodnienie dachów wg PN-EN 12056-3 i WT § 28, § 29; natężenie deszczu wg modelu PANDa (IMGW) — "
            "lamela.obliczenia.sanitarne.deszczowa; wody opadowe zagospodarowane na działce (zbiornik retencyjny + "
            "niecka chłonna), bez odprowadzania do kanalizacji sanitarnej.",
            "Wpusty dachowe z grzałką (podgrzewane), z kołnierzem do membrany/papy i koszem liściowym; przelewy "
            "awaryjne w attykach — dno przelewu powyżej poziomu pokrycia przy wpuście (odpływ normalny przez wpusty).",
            "Rury spustowe wewnętrzne w izolacji termicznej i akustycznej (otulina ≥ 20 mm); przejścia przez stropy "
            "z uszczelnieniem ppoż. wg klasy stropu.",
            f"Dachy: A = {num(d['A_dachow_m2'], 1)} m², Q = {num(d['Q_dachy_l_s'], 2)} l/s; zbiornik "
            f"{num(d['V_zbiornika_m3'], 1)} m³, niecka {num(d['niecka_A_m2'], 1)} m².",
        ]
        bad = [w for w in ds.warunki if w.ok is False]
        for w in bad[:4]:
            self.notes.append(f"SPRAWDZENIE NIESPEŁNIONE (obliczenia): {w.opis} — {w.wartosc if not isinstance(w.wartosc, float) else num(w.wartosc, 3)} "
                              f"{w.op} {w.limit if not isinstance(w.limit, float) else num(w.limit, 3)} {w.jedn} "
                              f"({w.podstawa}) — do korekty w modelu.")
            self.brak("Przelewy awaryjne / wpusty", f"sprawdzenie niespełnione: {w.opis}", "dachy[].przelewy_awaryjne"
                      "[].rzedna_dna > rzędna pokrycia przy wpuście")
        rows = [[p.id, p.typ, num(p.A, 1), num(p.Q, 2), str(p.n_wpustow), num(p.Q_wpustow, 2), num(p.Q_przelewow, 2),
                 num(100 * p.h_spietrzenia, 1)] for p in ds.pola if not any(w.get("propozycja") for w in p.wpusty)]
        self.res.column_blocks.append(("desz", table_block(
            "WYNIKI OBLICZEŃ — ODWODNIENIE DACHÓW (PN-EN 12056-3)",
            [("Pole", 14), ("Typ", 20), ("A [m²]", 18), ("Q [l/s]", 18), ("wpustów", 18), ("Q_wp [l/s]", 22),
             ("Q_przel. [l/s]", 24), ("h_spiętrz. [cm]", 26)], rows,
            align=["left", "left", "right", "right", "right", "right", "right", "right"])))
