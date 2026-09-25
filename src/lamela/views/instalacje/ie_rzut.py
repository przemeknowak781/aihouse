"""IE-O / IE-G / IE-T — rzuty instalacji elektrycznych: oświetlenie (oprawy, łączniki, obwody), gniazda wtyczkowe
i zasilania urządzeń, teletechnika (światłowód, LAN, TV, AP Wi-Fi, wideodomofon, SSWiN).

Obwody, zabezpieczenia, przewody: ``lamela.obliczenia.elektryka`` (bilans → obwody). Model nie zawiera punktów
elektrycznych — rozmieszczenie ALGORYTMICZNE (opis w uwagach arkusza): oprawy w siatce ≈ 3 m w obrysie pomieszczeń,
łączniki przy drzwiach od strony klamki (0,15 m od ościeżnicy, h = 1,10 m), gniazda przy łóżkach, biurkach, blatach
i przyborach oraz równomiernie wzdłuż ścian (bez otworów okiennych/drzwiowych), liczba wg praktyki (PN-HD 60364-5-52,
DIN 18015-2 — praktyka branżowa)."""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import substring, unary_union

from ...draft import symbols as S
from ...draft.geom import dir_deg, perp, polygons_of
from ..common import label_point
from .baza import Rysunek
from .is_co import paski
from .wspolne import BRAK, H_S, num, table_block

MOKRE = ("lazienka", "wc")


class RysE(Rysunek):
    br = "IE"

    def prepare(self):
        self.podklad(meble=True, urzadzenia=True)
        self.siatka(extra_pts=[], sciany=2.0, przy_scianie=0.7, poza=4.0)
        self.obw = self.W.obwody.obwody
        self.rooms = [r for r in self.pod.rooms if r.polygon is not None and r.polygon.area > 0.6
                      and "szacht" not in r.nazwa.lower()]
        self._doors = self._drzwi()
        self.circuits_used = set()

    # --------------------------------------------------------------------------------------------- pomieszczenia
    def rodzaj(self, r) -> str:
        rd = str(r.raw.get("rodzaj") or "")
        nm = r.nazwa.lower()
        if "łazienk" in nm or rd == "lazienka":
            return "lazienka"
        if nm.startswith("wc") or rd == "wc":
            return "wc"
        if "garaż" in nm or rd == "garaz":
            return "garaz"
        if "techn" in nm or rd == "techniczne":
            return "techniczne"
        if "kuchni" in nm or rd == "kuchnia":
            return "kuchnia"
        if "pralni" in nm or rd == "pralnia":
            return "pralnia"
        if "klatka" in nm:
            return "klatka"
        if r.kategoria == "ruchu" or rd == "komunikacja":
            return "komunikacja"
        if r.kategoria == "podstawowa":
            return "pokoj"
        return "pomocnicze"

    def _drzwi(self):
        """Drzwi/przejścia kondygnacji: (ściana, otwór, pomieszczenie +n, pomieszczenie −n)."""
        out = []
        for w in self.m.sciany(self.kid):
            for o in w.otwory:
                if o.typ not in ("drzwi", "drzwi_zewn", "otwor", "drzwi_przesuwne_HS"):
                    continue
                mid = (o.s0 + o.s1) / 2
                rp = self._room_pt(w.pt(mid, w.t_max + 0.3))
                rm = self._room_pt(w.pt(mid, w.t_min - 0.3))
                out.append((w, o, rp, rm))
        return out

    def _room_pt(self, pt):
        P = Point(float(pt[0]), float(pt[1]))
        for r in self.pod.rooms:
            if r.polygon is not None and r.polygon.buffer(0.02).contains(P):
                return r
        return None

    def przy_drzwiach(self, r, off=0.15):
        """Punkty na licu ściany przy drzwiach do pomieszczenia r od strony klamki: [(pos, rot, drzwi)]."""
        from ..plan import PlanBuilder
        out = []
        for w, o, rp, rm in self._doors:
            if r not in (rp, rm):
                continue
            side = 1 if rp is r else -1
            hinge = "a"
            try:
                sw = self.pod.pb._swing_side(w, o)
                hinge = PlanBuilder._hinge(w, sw, str((o.otwieranie or {}).get("strona", "lewa")))
            except Exception:
                pass
            t = w.t_max if side > 0 else w.t_min
            rot = math.degrees(math.atan2(*(w.n * side)[::-1]))
            cands = [o.s1 + 0.08 + off, o.s0 - 0.08 - off] if hinge == "a" else [o.s0 - 0.08 - off, o.s1 + 0.08 + off]
            for s in cands:
                q = w.pt(s, t)
                if 0.1 < s < w.L - 0.1 and r.polygon.buffer(0.05).contains(Point(q)) and \
                        self.pod.cut_region.buffer(-0.01).distance(Point(q + w.n * side * 0.08)) > 0.03:
                    out.append((q, rot, o))
                    break
        return out

    def wzdluz_scian(self, r, n, exclude=(), zbl=0.35, parapet_max=0.5):
        """n punktów równomiernie wzdłuż lic ścian pomieszczenia (bez drzwi, okien o niskim parapecie, naroży
        i stref ``exclude``) → [(pos, rot)]."""
        if n <= 0:
            return []
        pg = orient(max(polygons_of(r.polygon), key=lambda g: g.area), 1.0)
        ring = LineString(pg.exterior.coords)
        bad = []
        for w in self.m.sciany(self.kid):
            for o in w.otwory:
                if o.typ in ("okno", "fix") and o.parapet > parapet_max:
                    continue
                bad.append(o.footprint.buffer(0.2, join_style=2))
        for c in pg.exterior.coords:
            bad.append(Point(c).buffer(zbl))
        for e in exclude:
            bad.append(Point(e).buffer(0.8))
        free = ring.difference(unary_union(bad)) if bad else ring
        segs = [g for g in getattr(free, "geoms", [free]) if not g.is_empty and g.length > 0.25]
        if not segs:
            return []
        tot = sum(g.length for g in segs)
        out = []
        for i in range(n):
            target = tot * (i + 0.5) / n
            acc = 0.0
            for g in segs:
                if acc + g.length >= target:
                    d = target - acc
                    P = np.asarray(g.interpolate(d).coords[0])
                    Q = np.asarray(g.interpolate(min(g.length, d + 0.01)).coords[0])
                    Pm = np.asarray(g.interpolate(max(0.0, d - 0.01)).coords[0])
                    t = Q - Pm
                    t = t / (np.hypot(*t) or 1.0)
                    nrm = np.array([-t[1], t[0]])          # CCW → wnętrze po lewej
                    out.append((P, math.degrees(math.atan2(nrm[1], nrm[0]))))
                    break
                acc += g.length
        return out

    def obwod_dla(self, r, typ, grupa=None):
        for o in self.obw:
            od = o.odb
            if od.typ_obwodu != typ or (grupa and od.grupa != grupa):
                continue
            if r is not None and r.id in (od.pomieszczenia or []):
                return o
        return None

    def wyp(self, typ=None, szuk=None):
        out = []
        for e in self.W.dane.wyposazenie:
            if str(e.get("kond")) != self.kid:
                continue
            if typ and e.get("typ") != typ:
                continue
            if szuk and szuk not in str(e.get("opis", "")).lower():
                continue
            out.append(e)
        return out

    def chain(self, pts, key, layer="E-TRASY"):
        """Połączenie punktów jednego obwodu w pomieszczeniu (przewody w tynku/stropie) — linia cienka."""
        for a, b in zip(pts[:-1], pts[1:]):
            path = self.g.route(np.asarray(a, float), np.asarray(b, float), key, other=1.0, reuse=0.6, turn=0.2,
                                margin=2.0)
            self.pipe(path, "WZ", layer=layer, pen="b_cienka", lt="CIAGLA", color=None)
            self.g.mark(path, key)

    def circuit_tag(self, pos, oid, extra=None):
        lines = [oid] + ([extra] if extra else [])
        self.tag(pos, lines, "E-OPISY", radii=(3.5, 5.5, 8.0, 11.0), n_ang=12, style="bold")
        self.circuits_used.add(oid)

    def tabela_obwodow(self, typy):
        rows = []
        for o in self.obw:
            if o.odb.id not in self.circuits_used:
                continue
            rows.append([o.odb.id, o.odb.nazwa[:52], o.zab, o.przewod, num(o.L, 1), num(o.dU_calk, 2),
                         o.odb.faza.replace("L1L2L3", "3f"), o.odb.rcd.split(" (")[0][:26]])
        if rows:
            self.res.column_blocks.append(("obw", table_block(
                "OBWODY NA ARKUSZU (lamela.obliczenia.elektryka.obwody)",
                [("Obw.", 11), ("Odbiorniki", 62), ("Zab.", 14), ("Przewód", 22), ("L [m]", 12), ("∆U [%]", 13),
                 ("Faza", 10), ("RCD", 36)], rows,
                align=["left", "left", "center", "left", "right", "right", "center", "left"])))

    def rg(self):
        """Rozdzielnica główna RG i WLZ (na parterze)."""
        e = next((e for e in self.W.dane.wyposazenie if "rozdzielnica" in str(e.get("opis", "")).lower()), None)
        if e is None or str(e.get("kond")) != self.kid:
            return None
        rot = float(e.get("obrot", 90.0))
        w, d = (e.get("wym") or [0.8, 0.25])[:2]
        self.sym(S.panel, np.asarray(e["xy"], float), rot, w=float(w), d=float(d), label="RG")
        wl = self.W.obwody.wlz
        self.tag(np.asarray(e["xy"], float), [f"RG — rozdzielnica główna (schemat — arkusz schematu RG), TN-S",
                                               f"WLZ {wl['przewod']} z ZKP, L = {num(wl['L'], 1)} m, "
                                               f"∆U = {num(wl['dU'], 2)} %; SPD T1+T2"], "E-OPISY", style="bold")
        self.leg.sym(lambda c, p: S.panel(c, p - np.array([0, 1.5]), 90.0, w=8.0, d=3.0, label=""),
                     "RG — rozdzielnica główna (PN-EN IEC 61439-3)")
        return np.asarray(e["xy"], float)


# ================================================================================================ IE-O oświetlenie
class RysO(RysE):
    kod = "IE-O"

    def run(self):
        self.prepare()
        self.leg.line("E-TRASY", "przewody obwodów oświetlenia YDYp 3×1,5 / 4×1,5 (w tynku, w stropie) — połączenia "
                      "punktów (przebieg schematyczny)", pen="b_cienka")
        for r in self.rooms:
            self.pomieszczenie(r)
        if self.kid == self.kids[0]:
            self.zewnetrzne()
            self.rg()
        self.opisy()
        self.tabela_obwodow(("oswietlenie",))
        return self.finish()

    def punkty_opraw(self, r):
        pg = r.polygon.buffer(-0.5, join_style=2)
        if pg.is_empty:
            pg = r.polygon.buffer(-0.2, join_style=2)
        if pg.is_empty:
            return []
        pg = max(polygons_of(pg), key=lambda g: g.area)
        x0, y0, x1, y1 = pg.bounds
        L, B = max(x1 - x0, y1 - y0), min(x1 - x0, y1 - y0)
        if L / max(B, 0.3) > 2.5:
            n = max(1, round(L / 3.0))
        else:
            n = max(1, math.ceil(pg.area / 15.0))
        return [label_point(p) for p in paski(pg, n) if not p.is_empty]

    def pomieszczenie(self, r):
        rd = self.rodzaj(r)
        ob = self.obwod_dla(r, "oswietlenie")
        oid = ob.odb.id if ob else "L?"
        pts = self.punkty_opraw(r)
        kind = "downlight" if rd in MOKRE else "sufit"
        lights = []
        for q in pts:
            if rd == "garaz":
                self.sym(S.light_linear, q - np.array([0.6, 0.0]), q + np.array([0.6, 0.0]))
            else:
                self.sym(S.light, q, kind, s_mm=4.0)
            lights.append(q)
        # oświetlenie nad umywalką (kinkiet) i pod szafkami kuchennymi
        for e in self.wyp():
            if e.get("typ") in ("umywalka", "umywalka_blat") and r.polygon.buffer(0.3).contains(Point(e["xy"])):
                q = np.asarray(e["xy"], float)
                self.sym(S.light, q, "kinkiet", rot=float(e.get("obrot", 90)), s_mm=3.5)
                lights.append(q + dir_deg(float(e.get("obrot", 90))) * 0.1)
            if e.get("typ") == "blat" and r.polygon.buffer(0.3).contains(Point(e["linia"][0])):
                a, b = np.asarray(e["linia"][0], float), np.asarray(e["linia"][-1], float)
                t = (b - a) / (np.hypot(*(b - a)) or 1.0)
                nrm = np.array([-t[1], t[0]]) * float(e.get("strona", 1.0))
                self.sym(S.light_linear, a + t * 0.2 + nrm * 0.25, b - t * 0.2 + nrm * 0.25)
                lights.append(a + t * 0.2 + nrm * 0.25)
        if not lights:
            return
        sw = self.przy_drzwiach(r) or self.przy_drzwiach(r, off=0.05)
        if not sw:                         # przejście bez drzwi / wąskie pomieszczenie: punkt ściany najbliżej wejścia
            wl = self.wzdluz_scian(r, 6, zbl=0.2, parapet_max=9.0)
            dz = [np.asarray(o.srodek) for w, o, rp, rm in self._doors if r in (rp, rm)]
            if wl:
                ref = dz[0] if dz else lights[0]
                q, rot = min(wl, key=lambda t: float(np.hypot(*(t[0] - ref))))
                sw = [(q, rot, None)]
        if not sw:
            return
        many = len(sw) > 1 and rd in ("komunikacja", "klatka")
        kinds = ["schodowy", "schodowy"] if many else (["swiecznikowy"] if len(lights) > 2 and rd not in MOKRE else ["1"])
        pts_sw = []
        for (q, rot, o), kd in zip(sw, kinds):
            self.sym(S.switch, q, rot, kind=kd, ip44=rd in ("garaz", "techniczne"), s_mm=3.0)
            pts_sw.append(q + dir_deg(rot) * 0.1)
        self.chain([pts_sw[0]] + sorted(lights, key=lambda p: np.hypot(*(p - pts_sw[0]))), f"L:{r.id}")
        if len(pts_sw) > 1:
            self.chain([pts_sw[1], lights[0]], f"L:{r.id}")
        self.circuit_tag(lights[0], oid)
        self.leg.sym(lambda c, p: S.light(c, p, "sufit", s_mm=4.0), "oprawa oświetleniowa sufitowa (PN-EN 60617-11-15)")
        if rd in MOKRE:
            self.leg.sym(lambda c, p: S.light(c, p, "downlight", s_mm=4.0),
                         "oprawa wpuszczana (downlight) IP44 — strefy łazienek wg PN-HD 60364-7-701")
            self.leg.sym(lambda c, p: S.light(c, p - np.array([0, 1.5]), "kinkiet", rot=90.0, s_mm=3.5),
                         "wypust / oprawa ścienna (kinkiet), nad lustrem IP44")
        self.leg.sym(lambda c, p: S.switch(c, p - np.array([0, 1.5]), 90.0, kind="1", s_mm=3.0),
                     "łącznik jednobiegunowy, h = 1,10 m (IP44 — zaczerniony)")
        if "swiecznikowy" in kinds:
            self.leg.sym(lambda c, p: S.switch(c, p - np.array([0, 1.5]), 90.0, kind="swiecznikowy", s_mm=3.0),
                         "łącznik świecznikowy (dwuobwodowy)")
        if many:
            self.leg.sym(lambda c, p: S.switch(c, p - np.array([0, 1.5]), 90.0, kind="schodowy", s_mm=3.0),
                         "łącznik schodowy (przełącznik dwukierunkowy)")
        if rd == "garaz" or any(e.get("typ") == "blat" for e in self.wyp()):
            self.leg.sym(lambda c, p: S.light_linear(c, p - np.array([6, 0]), p + np.array([6, 0])),
                         "oprawa liniowa LED (garaż IP65; pod szafkami kuchennymi)")

    def zewnetrzne(self):
        ob = next((o for o in self.obw if o.odb.typ_obwodu == "oswietlenie" and "zewn" in o.odb.nazwa.lower()), None)
        for w in self.m.sciany(self.kid):
            if w.ext_side is None:
                continue
            for o in w.otwory:
                if o.typ not in ("drzwi_zewn", "drzwi_przesuwne_HS"):
                    continue
                es = w.ext_side
                s = o.s1 + 0.35 if o.s1 + 0.35 < w.L - 0.2 else o.s0 - 0.35
                q = w.pt(s, w.face_t(es, "all"))
                rot = math.degrees(math.atan2(*(w.n * es)[::-1]))
                self.sym(S.light, q, "kinkiet", rot=rot, s_mm=3.5)
                if ob is not None:
                    self.circuit_tag(q + w.n * es * 0.15, ob.odb.id, "IP44, czujnik zmierzchowy" if
                                     o.typ == "drzwi_zewn" else None)

    def opisy(self):
        self.notes += [
            "Instalacja oświetlenia wg PN-HD 60364 (seria), WT § 180–186 i § 64 (oświetlenie wejścia); natężenie "
            "oświetlenia wg PN-EN 12464-1 (wartości zalecane); obwody i zabezpieczenia z obliczeń "
            "(lamela.obliczenia.elektryka): wyłączniki nadprądowe B10, RCBO/RCD 30 mA.",
            "Rozmieszczenie opraw i łączników wyznaczono algorytmicznie (model nie zawiera punktów elektrycznych): "
            "oprawy w siatce ok. 3 m w obrysie pomieszczenia, łączniki przy drzwiach od strony klamki 0,15 m od "
            "ościeżnicy na h = 1,10 m; typy opraw — do uzgodnienia z Inwestorem (projekt oświetlenia wnętrz).",
            "Przewody YDYp 3×1,5 (4×1,5 łączniki schodowe/świecznikowe) w tynku i w warstwach stropu, w strefach "
            "instalacyjnych; w łazienkach osprzęt poza strefami 0–1 wg PN-HD 60364-7-701, IP44 w strefie 2.",
        ]


# ================================================================================================ IE-G gniazda
class RysG(RysE):
    kod = "IE-G"

    def run(self):
        self.prepare()
        self.leg.line("E-TRASY", "przewody obwodów gniazd YDYp 3×2,5 (5×2,5 — 3f) — połączenia punktów (przebieg "
                      "schematyczny w tynku / w posadzce)", pen="b_cienka")
        self.leg.sym(lambda c, p: S.socket(c, p - np.array([0, 1.5]), 90.0, n=2, s_mm=3.0),
                     "gniazdo wtyczkowe podwójne ze stykiem ochronnym, h = 0,30 m (kuchnia nad blatem 1,10 m)")
        self.leg.sym(lambda c, p: S.socket(c, p - np.array([0, 1.5]), 90.0, n=1, ip44=True, s_mm=3.0),
                     "gniazdo bryzgoszczelne IP44 (łazienki h = 1,20 m, garaż, pom. techniczne, zewnętrzne)")
        self.leg.sym(lambda c, p: S.junction_box(c, p, s_mm=1.8), "wypust / puszka przyłączeniowa urządzenia "
                     "zasilanego na stałe (opis: obwód, urządzenie, moc)")
        for r in self.rooms:
            self.pomieszczenie(r)
        if self.kid == self.kids[0]:
            self.zewnetrzne()
            self.rg()
        self.oslony()
        self.opisy()
        self.tabela_obwodow(("gniazda", "staly"))
        return self.finish()

    def _gn(self, pts, r, oid, ip44=False, n=2, label=None):
        out = []
        for q, rot in pts:
            self.sym(S.socket, q, rot, n=n, ip44=ip44, s_mm=3.0)
            out.append(q + dir_deg(rot) * 0.08)
        if out and oid:
            c = np.asarray(r.polygon.centroid.coords[0])
            out.sort(key=lambda p: math.atan2(p[1] - c[1], p[0] - c[0]))
            self.chain(out, f"G:{r.id}:{oid}")
            self.circuit_tag(out[0], oid, label)
        return out

    def _dedyk(self, grupa_or_nazwa, q, rot=None, txt=None, phases=1):
        o = next((o for o in self.obw if o.odb.grupa == grupa_or_nazwa or grupa_or_nazwa in o.odb.nazwa.lower()), None)
        if o is None:
            return
        q = np.asarray(q, float)
        if rot is None:
            self.sym(S.junction_box, q, s_mm=1.8)
        else:
            self.sym(S.socket, q, rot, n=1, phases=phases, s_mm=3.0)
        self.circuit_tag(q, o.odb.id, txt or f"{o.odb.nazwa.split('(')[0].strip()} {num(o.odb.P, 1)} kW")

    def pomieszczenie(self, r):
        rd = self.rodzaj(r)
        wy = [e for e in self.wyp() if r.polygon.buffer(0.35).contains(Point(e.get("xy") or e.get("linia", [[0, 0]])[0]))]
        anchors = []
        ob = self.obwod_dla(r, "gniazda")
        oid = ob.odb.id if ob else None
        if rd in ("pokoj", "kuchnia", "pomocnicze", "komunikacja"):
            for e in wy:
                t, xy, rot = e.get("typ"), np.asarray(e.get("xy") or [0, 0], float), float(e.get("obrot", 90))
                d = dir_deg(rot)
                tt = perp(d)
                w0 = float((e.get("wym") or [1.0])[0])
                if t == "lozko":
                    anchors += [(xy + tt * (w0 / 2 + 0.25), rot), (xy - tt * (w0 / 2 + 0.25), rot)]
                elif t == "biurko":
                    anchors.append((xy + tt * (w0 / 2 - 0.2), rot))
                elif t == "sofa":
                    anchors.append((xy + tt * (w0 / 2 + 0.25), rot))
        if rd == "kuchnia":
            self._kuchnia(r, wy)
            ob = next((o for o in self.obw if o.odb.grupa == "gniazda_kuchnia" and r.id in o.odb.pomieszczenia), None)
            ob2 = [o for o in self.obw if o.odb.grupa == "gniazda_kuchnia" and r.id in o.odb.pomieszczenia]
            oid = ob2[-1].odb.id if ob2 else oid
        target = {"pokoj": 3 + int(r.pow_netto // 10), "kuchnia": 2 + int(r.pow_netto // 15),
                  "komunikacja": max(1, int(r.polygon.length // 7)), "pomocnicze": 1}.get(rd, 0)
        if rd in ("pokoj", "kuchnia", "komunikacja", "pomocnicze"):
            excl = [a[0] for a in anchors] + [np.asarray(p, float) for e in wy if e.get("typ") == "blat"
                                              for p in e["linia"]]
            fill = self.wzdluz_scian(r, max(0, target - len(anchors)), exclude=excl)
            self._gn(anchors + fill, r, oid)
        elif rd == "lazienka":
            pts = []
            for e in wy:
                if e.get("typ") in ("umywalka", "umywalka_blat"):
                    rot = float(e.get("obrot", 90))
                    tt = perp(dir_deg(rot))
                    w0 = float((e.get("wym") or [0.6])[0])
                    pts.append((np.asarray(e["xy"], float) + tt * (w0 / 2 + 0.3), rot))
            self._gn(pts[:1], r, oid, ip44=True)
        elif rd in ("garaz", "techniczne"):
            o = next((o for o in self.obw if "garażu" in o.odb.nazwa.lower() and o.odb.typ_obwodu == "gniazda"), None)
            self._gn(self.wzdluz_scian(r, 2), r, o.odb.id if o else None, ip44=True, n=1)
            if rd == "garaz":
                q = label_point(r.polygon)
                self._dedyk("ev", self.wzdluz_scian(r, 1, zbl=1.0)[0][0] if self.wzdluz_scian(r, 1) else q,
                            txt="ładowarka EV (wallbox) 11 kW, RCD typ B / RDC-DD")
                br = next((o for o in self.m.otwory(kond=self.kid) if o.typ == "brama"), None)
                if br is not None:
                    self._dedyk("bramy garażowej", br.srodek + br.sciana.n * br.sciana.sgn_int * 0.4,
                                txt="napęd bramy garażowej")
            else:
                for e in wy:
                    op = str(e.get("opis", "")).lower()
                    xy = np.asarray(e.get("xy") or [0, 0], float)
                    if e.get("typ") == "pompa_ciepla":
                        self._dedyk("sterowanie", xy, txt="sterownik PC, pompy, listwy ogrz. podł.")
                    elif "cwu" in op or "c.w.u" in op:
                        self._dedyk("grzalka", xy, txt="grzałka zasobnika / PC 3f")
                    elif "rozdzielnica" in op:
                        self._dedyk("pv", xy + np.array([0.6, 0.0]), txt="falownik PV 3f (AC)")
                        self._dedyk("tele", xy + np.array([-0.6, 0.0]), txt="RACK / ONT / SSWiN")
        elif rd == "pralnia":
            for e in wy:
                if e.get("typ") in ("pralka", "suszarka"):
                    self._dedyk(e["typ"], np.asarray(e["xy"], float), float(e.get("obrot", 90)),
                                txt=f"{e['typ']} (gniazdo IP44)")
        for e in wy:
            if e.get("typ") == "rekuperator":
                self._dedyk("went", np.asarray(e["xy"], float), txt="centrala wentylacyjna")

    def _kuchnia(self, r, wy):
        g = [o for o in self.obw if o.odb.grupa == "gniazda_kuchnia" and r.id in o.odb.pomieszczenia]
        for e in wy:
            if e.get("typ") != "blat":
                continue
            a, b = np.asarray(e["linia"][0], float), np.asarray(e["linia"][-1], float)
            L = float(np.hypot(*(b - a)))
            t = (b - a) / (L or 1.0)
            nrm = np.array([-t[1], t[0]]) * float(e.get("strona", 1.0))
            rot = math.degrees(math.atan2(nrm[1], nrm[0]))
            busy = [np.asarray(x["xy"], float) for x in wy if x.get("typ") in ("zlew", "urzadzenie", "lodowka")]
            pts = []
            for s in np.arange(0.4, L - 0.2, 1.1):
                q = a + t * s
                if all(float(np.hypot(*(q - bb))) > 0.45 for bb in busy):
                    pts.append((q, rot))
            for i, (q, rr) in enumerate(pts):
                o = g[i % len(g)] if g else None
                self.sym(S.socket, q, rr, n=2, s_mm=3.0)
                if o is not None and i < len(g):
                    self.circuit_tag(q + nrm * 0.08, o.odb.id, "nad blatem h = 1,10 m" if i == 0 else None)
            self.chain([q + nrm * 0.08 for q, _ in pts], f"G:{r.id}:blat")
        for e in wy:
            t = e.get("typ")
            xy = np.asarray(e.get("xy") or [0, 0], float)
            rot = float(e.get("obrot", 90))
            if t == "plyta":
                self._dedyk("płyta", xy, txt="płyta indukcyjna 3f — puszka w wyspie")
            elif t == "zmywarka":
                self._dedyk("zmywarka", xy, rot)
            elif t == "urzadzenie" and "piekarnik" in str(e.get("opis", "")).lower():
                self._dedyk("piekarnik", xy, rot)
            elif t == "lodowka" and g:
                self.sym(S.socket, xy, rot, n=1, s_mm=3.0)
