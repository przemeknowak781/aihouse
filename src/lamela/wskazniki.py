"""Wskaźniki zagospodarowania działki (MPZP, PZT) — JEDYNE źródło wartości w projekcie „Dom LAMELA”.

``wskazniki(model, ir=None, opcje=None) -> dict`` — każda pozycja to słownik
``{"wartosc", "jedn", "podstawa", "metoda", ...szczegóły}``; klucze: ``pow_dzialki``, ``pow_zabudowy``,
``pow_zabudowy_kontrolna``, ``udzial_zabudowy``, ``udzial_zabudowy_kontrolny``, ``pow_utwardzona``, ``pow_tarasow``,
``pow_opaski``, ``pbc``, ``pbc_rezerwa_dach``, ``udzial_pbc``, ``udzial_pbc_z_rezerwa``, ``pow_kondygnacji``,
``suma_pow_kondygnacji``, ``suma_pow_kondygnacji_nadziemnych``, ``intensywnosc``, ``intensywnosc_nadziemna``,
``wysokosc_zabudowy``, ``wysokosc_WT6``, ``kondygnacje_nadziemne``, ``miejsca_postojowe``, ``kat_dachu``;
pod kluczem ``_geom`` — geometrie shapely (układ działki) do rysunków (pokrycie terenu, PBC, obrysy).

Definicje (cytaty dosłowne: ``docs/10_podstawy_prawne/weryfikacja_upzp_art2_definicje.md``): ustawa o planowaniu
i zagospodarowaniu przestrzennym, t.j. Dz.U. 2026 poz. 538, art. 2 pkt 28–35; RPB § 14 pkt 4 (t.j. Dz.U. 2022
poz. 1679 ze zm.) — zestawienie powierzchni w PZT; WT § 6 (wysokość budynku) i § 3 pkt 15 (poziom terenu = przyjęta
w projekcie rzędna terenu).

Metoda wysokości zabudowy (upzp art. 2 pkt 30 lit. a): ``H = z_top − t_śr``, gdzie ``z_top`` — najwyżej położony
punkt budynku na dachu, ścianie lub attyce (wyłączenia ZAMKNIĘTE: komin, nadbudówka maszynowni dźwigu lub innego
pomieszczenia technicznego, wyjście z klatki schodowej — czerpnia, wyrzutnia, wywiewka, PV, wyłaz, świetlik są
WLICZANE), ``t_śr = (t_min + t_max) / 2`` — średnia z najniższego i najwyższego poziomu terenu na obwodzie rzutu
poziomego ścian zewnętrznych budynku; w każdym punkcie obwodu przyjmuje się NIŻSZĄ z rzędnych: terenu istniejącego
(interpolacja liniowa TIN) i projektowanego (TIN punktów projektowanych w zasięgu ≤ 2,0 m od najbliższego punktu).

Porównanie z ``tools/audyt_wt.py`` (audytor A1, wersja z 25.09.2026): audyt podaje wysokość zabudowy liczoną od
``t_min`` (najniższego punktu terenu) — to BŁĄD METODY względem pkt 30 lit. a (odniesieniem jest średnia z min. i maks.);
wartość „od średniej” audyt podaje pomocniczo, ale z ``t_śr = (min(dolnych) + min(górnych)) / 2`` (inna agregacja
istn./proj.). Ten moduł liczy wg definicji; różnice raportuje ``tools/test_wskazniki.py`` (audyt NIE jest poprawiany).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

UPZP = "upzp (t.j. Dz.U. 2026 poz. 538)"
POD = {
    "28": f"{UPZP} art. 2 pkt 28",
    "29": f"{UPZP} art. 2 pkt 29 lit. a",
    "30": f"{UPZP} art. 2 pkt 30 lit. a",
    "31": f"{UPZP} art. 2 pkt 31 lit. a",
    "32": f"{UPZP} art. 2 pkt 32 lit. a",
    "33": f"{UPZP} art. 2 pkt 33",
    "34": f"{UPZP} art. 2 pkt 34",
    "35": f"{UPZP} art. 2 pkt 35 lit. a",
    "RPB14": "RPB § 14 pkt 4 (t.j. Dz.U. 2022 poz. 1679, zm. Dz.U. 2023 poz. 2405)",
    "WT6": "WT § 6, § 3 pkt 15, § 8 pkt 1 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB)",
    "WT18": "WT § 18, § 21 ust. 1; MPZP",
}
TYPY_WEJSC = ("drzwi_zewn", "drzwi_przesuwne_HS", "brama")
PROMIEN_PROJ = 2.0     # [m] zasięg rzędnych projektowanych od najbliższego punktu projektowanego
WYWIEWKA_NAD_POKR = 0.50   # [m] założenie, gdy w modelu brak rzędnej wylotu wywiewki (PN-EN 12056-2 — praktyka)


def _poz(wartosc, jedn, podstawa, metoda, **kw) -> dict:
    d = dict(wartosc=wartosc, jedn=jedn, podstawa=podstawa, metoda=metoda)
    d.update(kw)
    return d


def _ring(v):
    try:
        return [(float(p[0]), float(p[1])) for p in v] if isinstance(v, (list, tuple)) and len(v) >= 3 else None
    except (TypeError, ValueError, IndexError):
        return None


def _poly(v):
    r = _ring(v)
    if r is None:
        return None
    g = Polygon(r)
    return g if g.is_valid else shapely.make_valid(g)


class Teren:
    """Rzędne terenu [m n.p.m.] w układzie działki: istniejący (TIN liniowy, poza otoczką — płaszczyzna MNK),
    projektowany (TIN punktów projektowanych, tylko ≤ ``PROMIEN_PROJ`` od najbliższego punktu), ``nizsza``."""

    def __init__(self, teren: dict):
        from scipy.interpolate import LinearNDInterpolator
        t = teren or {}
        self.ist = np.asarray([p for p in (t.get("punkty") or []) if len(p) >= 3], float).reshape(-1, 3)
        self.proj = np.asarray([p for p in (t.get("punkty_projektowane") or []) if len(p) >= 3], float).reshape(-1, 3)
        self._fi = self._fp = None
        if len(self.ist) >= 3:
            self._fi = LinearNDInterpolator(self.ist[:, :2], self.ist[:, 2])
            A = np.c_[self.ist[:, :2], np.ones(len(self.ist))]
            self._ci = np.linalg.lstsq(A, self.ist[:, 2], rcond=None)[0]
        if len(self.proj) >= 3:
            self._fp = LinearNDInterpolator(self.proj[:, :2], self.proj[:, 2])

    def istn(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        if self._fi is None:
            return np.full(len(xy), np.nan)
        z = np.asarray(self._fi(xy), float).reshape(-1)
        bad = ~np.isfinite(z)
        z[bad] = self._ci[0] * xy[bad, 0] + self._ci[1] * xy[bad, 1] + self._ci[2]
        return z

    def projekt(self, xy):
        xy = np.asarray(xy, float).reshape(-1, 2)
        if len(self.proj) == 0:
            return np.full(len(xy), np.nan)
        d = np.min(np.hypot(xy[:, None, 0] - self.proj[None, :, 0], xy[:, None, 1] - self.proj[None, :, 1]), axis=1)
        if self._fp is not None:
            z = np.asarray(self._fp(xy), float).reshape(-1)
        else:
            z = np.full(len(xy), np.nan)
        nn = np.argmin(np.hypot(xy[:, None, 0] - self.proj[None, :, 0], xy[:, None, 1] - self.proj[None, :, 1]), axis=1)
        z = np.where(np.isfinite(z), z, self.proj[nn, 2])
        return np.where(d <= PROMIEN_PROJ, z, np.nan)

    def nizsza(self, xy):
        a, b = self.istn(xy), self.projekt(xy)
        return np.where(np.isfinite(b), np.minimum(a, b), a), a, b


# ------------------------------------------------------------------------------------------------ geometria
def numery_kondygnacji(model) -> dict:
    """Numer kondygnacji wg PN-B-01025 (najbliższa ±0,00 = 1) — jak ``views.common.storey_numbers``."""
    ks = list(model.kondygnacje)
    if not ks:
        return {}
    i0 = min(range(len(ks)), key=lambda i: abs(ks[i].rzedna))
    return {k.id: (i - i0 + 1 if i >= i0 else i - i0) for i, k in enumerate(ks)}


def geometria(model) -> dict:
    """Geometrie w układzie działki: działka, obrysy kondygnacji, rzut ścian (pkt 35), płyty wysunięte, tarasy,
    utwardzenia, opaska, zieleń, zbiornik, niecka."""
    from .model import make_polygon
    dz = model.dz
    raw = (dz.raw if dz is not None else {}) or {}
    u = raw.get("uklad") or {}
    a = math.radians(float(u.get("obrot") or 0.0))
    t = u.get("przesuniecie") or [0.0, 0.0]
    aff = [math.cos(a), -math.sin(a), math.sin(a), math.cos(a), float(t[0]), float(t[1])]
    G = lambda g: affinity.affine_transform(g, aff)       # noqa: E731
    P = lambda xy: np.asarray(dz.do_dzialki(np.asarray(xy, float)), float)   # noqa: E731
    plot = _poly((raw.get("dzialka") or {}).get("obrys")) or Polygon()
    nums = numery_kondygnacji(model)
    storeys = {}
    for k in model.kondygnacje:
        g = model.obrys_kondygnacji(k.id)
        if g is not None and not g.is_empty:
            storeys[k.id] = G(g)
    nadz = [k.id for k in model.kondygnacje if nums.get(k.id, 1) >= 1 and k.id in storeys]
    k0 = next((k for k in nadz if nums.get(k) == 1), nadz[0] if nadz else None)
    p0 = storeys.get(k0, Polygon())
    fp = unary_union([storeys[k] for k in nadz]) if nadz else Polygon()
    plyty = []
    for it in list(model.wsporniki()) + list(model.dachy()):
        if _ring(it.get("obrys")):
            g = G(make_polygon(it["obrys"]))
            if g.difference(fp.buffer(0.02, join_style=2)).area >= 0.05:
                plyty.append((str(it.get("id")), g))
    tarasy = [(str(x.get("id")), G(make_polygon(x["obrys"]))) for x in model.tarasy() if _ring(x.get("obrys"))]
    utw = [(str(x.get("id")), _poly(x.get("obrys")), str(x.get("nawierzchnia") or ""))
           for x in raw.get("utwardzenia") or [] if isinstance(x, dict) and _poly(x.get("obrys")) is not None]
    ziel = [(str(x.get("id")), _poly(x.get("obrys")), str(x.get("typ") or ""))
            for x in raw.get("zielen") or [] if isinstance(x, dict) and _poly(x.get("obrys")) is not None]
    # opaska żwirowa: pas między obrysem przyziemia a linią 'obrys' (szer.), bez tarasów i utwardzeń
    opaska = []
    for o in raw.get("odwodnienia") or []:
        if isinstance(o, dict) and o.get("typ") == "opaska_zwirowa" and o.get("obrys"):
            w = float(o.get("szer") or 0.5)
            band = p0.buffer(w + 0.01, join_style=2).difference(p0)
            try:
                band = band.intersection(LineString(o["obrys"]).buffer(w * 1.05, cap_style=2, join_style=2))
            except Exception:  # noqa: BLE001
                pass
            cut = [g for _i, g in tarasy] + [g for _i, g, _n in utw]
            band = band.difference(unary_union(cut)) if cut else band
            opaska.append((str(o.get("id")), unary_union([q for q in getattr(band, "geoms", [band])
                                                          if q.area > 0.05])))
    rt = raw.get("retencja") or {}
    zb = rt.get("zbiornik") if isinstance(rt.get("zbiornik"), dict) else None
    niecka = _poly((rt.get("rozsaczanie") or {}).get("obrys")) if isinstance(rt.get("rozsaczanie"), dict) else None
    return dict(raw=raw, plot=plot, storeys=storeys, nadz=nadz, k0=k0, p0=p0, footprint=fp, plyty=plyty,
                tarasy=tarasy, utw=utw, ziel=ziel, opaska=opaska, zbiornik=zb, niecka=niecka, G=G, P=P, aff=aff)


def _pokrycie(model, d: dict) -> tuple:
    """(z_min, z_śr, z_max) wierzchu pokrycia dachu [m wzgl. ±0,00] — z klinem izolacji spadkowej (``klin``)."""
    pl = d.get("plyta") or {}
    w = float(pl.get("wierzch", 0.0))
    p = model.przegroda(str(d.get("przegroda")))
    if p is None or not p.ma_oznaczona_konstr:
        return (w, w, w)
    nad = p.d_nad_konstr()
    dmin = dmax = dd = None
    for war in (p.raw or {}).get("warstwy") or []:
        if isinstance(war, dict) and isinstance(war.get("klin"), dict):
            dmin, dmax, dd = float(war["klin"]["d_min"]), float(war["klin"]["d_max"]), float(war["d"])
    if dmin is None:
        return (w + nad, w + nad, w + nad)
    return (w + nad - dd + dmin, w + nad, w + nad - dd + dmax)


def punkty_najwyzsze(model, ir=None) -> list[tuple]:
    """Kandydaci najwyższego punktu budynku (z względne, element, źródło, założenie?) — wszystkie elementy na dachu,
    ścianach i attykach (wyłączenia pkt 30 lit. a: komin, nadbudówka techniczna, wyjście z klatki — brak w modelu)."""
    out = []
    for d in model.dachy():
        zmin, zsr, zmax = _pokrycie(model, d)
        att = d.get("attyka") if isinstance(d.get("attyka"), dict) else None
        out.append((zmax, f"pokrycie dachu {d.get('id')} (maks., klin)", "budynek.yaml: dachy", False))
        if att:
            out.append((zsr + float(att.get("wys_nad_pokryciem", 0.0)), f"attyka dachu {d.get('id')}",
                        "budynek.yaml: dachy[].attyka", False))
    for w in model.wsporniki():
        if w.get("wierzch") is not None:
            out.append((float(w["wierzch"]), f"{w.get('id')} (płyta/świetlik/wyłaz)", "budynek.yaml: wsporniki_plyty",
                        False))
    for lm in model.lamele():
        if lm.get("z_do") is not None:
            out.append((float(lm["z_do"]), f"lamele {lm.get('id')}", "budynek.yaml: lamele", False))
    for b in model.balustrady():
        pl = b.get("polilinia") or []
        if pl and len(pl[0]) >= 3:
            out.append((max(float(q[2]) for q in pl) + float(b.get("wys") or 0.0), f"balustrada {b.get('id')}",
                        "budynek.yaml: balustrady", False))
    went = ((model.raw.get("energia") or {}).get("wentylacja") or {})
    for kk in ("czerpnia", "wyrzutnia"):
        v = went.get(kk)
        if isinstance(v, (list, tuple)) and len(v) >= 3:
            out.append((float(v[2]), f"{kk} wentylacji (dachowa)", "budynek.yaml: energia.wentylacja", False))
    roof_top = max((_pokrycie(model, d)[1] for d in model.dachy()), default=0.0)
    for i, v in enumerate(went.get("wywiewki_kanalizacyjne") or []):
        if isinstance(v, (list, tuple)) and len(v) >= 3:
            out.append((float(v[2]), f"wywiewka kanalizacyjna {i + 1}", "budynek.yaml: energia.wentylacja", False))
        elif isinstance(v, (list, tuple)) and len(v) >= 2:
            out.append((roof_top + WYWIEWKA_NAD_POKR, f"wywiewka kanalizacyjna {i + 1} (z = pokrycie + "
                        f"{WYWIEWKA_NAD_POKR:.2f} m — ZAŁOŻENIE, brak rzędnej w modelu)",
                        "budynek.yaml: energia.wentylacja.wywiewki_kanalizacyjne [x, y] — brak z", True))
    pv = (model.raw.get("energia") or {}).get("pv") or {}
    if isinstance(pv, dict) and pv.get("z_max") is not None:
        out.append((float(pv["z_max"]), "moduły PV (górna krawędź)", "budynek.yaml: energia.pv.z_max", False))
    if ir is not None:
        try:
            kinds_out = {"vegetation", "context", "vehicle", "road", "fence", "pavement", "terrain"}
            bp = [p for p in ir.prisms if p.kind not in kinds_out and p.meta.get("group") != "otoczenie"]
            if bp:
                p = max(bp, key=lambda q: q.z1)
                out.append((float(p.z1), f"bryła IR {p.id} ({p.kind})", "IR (lamela.ir)", False))
        except Exception:  # noqa: BLE001
            pass
    return out


def obwod_punkty(fp, krok=0.25) -> np.ndarray:
    """Punkty na obwodzie rzutu poziomego ścian zewnętrznych (co ``krok`` m, wszystkie pierścienie zewnętrzne)."""
    pts = []
    for pg in getattr(fp, "geoms", [fp]):
        if pg.is_empty:
            continue
        pts.append(np.asarray(shapely.segmentize(pg.exterior, krok).coords)[:-1])
    return np.vstack(pts) if pts else np.zeros((0, 2))


# ------------------------------------------------------------------------------------------------ wskaźniki
def wskazniki(model, ir=None, opcje: dict | None = None) -> dict:
    """Wskaźniki zagospodarowania — patrz docstring modułu. ``ir`` (opcjonalnie) — dodatkowy kandydat najwyższego
    punktu z brył IR; ``opcje``: ``{"wylaczenia_pbc": [...]}`` (identyfikatory utwardzeń liczonych jako PBC — brak)."""
    g = geometria(model)
    raw = g["raw"]
    A = float(g["plot"].area)
    z0 = float(model.zero_abs)
    out = {}
    out["pow_dzialki"] = _poz(A, "m²", "dzialka.yaml: dzialka.obrys (ewidencja: pole 'pow')",
                              "pole wieloboku obrysu działki (shapely)", pow_ewid=(raw.get("dzialka") or {}).get("pow"))
    fp, p0 = g["footprint"], g["p0"]
    out["pow_zabudowy"] = _poz(float(fp.area), "m²", f"{POD['35']}; {POD['RPB14']} lit. a",
                               "suma rzutu poziomego budynku po zewnętrznym obrysie ścian zewnętrznych wszystkich "
                               "kondygnacji nadziemnych (lico ocieplenia; wspornik bryły wyższej kondygnacji wliczony); "
                               "tarasy naziemne, okapy, płyty wysunięte — nie wliczane")
    pl = unary_union([fp] + [q for _i, q in g["plyty"]]) if g["plyty"] else fp
    out["pow_zabudowy_kontrolna"] = _poz(float(pl.area), "m²", "wariant kontrolny (R8-R8, W-030) — informacyjnie",
                                         "rzut ścian zewnętrznych + rzut płyt wspornikowych, okapów i daszków "
                                         f"({', '.join(i for i, _q in g['plyty'])})")
    out["udzial_zabudowy"] = _poz(fp.area / A if A else 0.0, "–", POD["35"], "pow_zabudowy / pow_dzialki")
    out["udzial_zabudowy_kontrolny"] = _poz(pl.area / A if A else 0.0, "–", "wariant kontrolny",
                                            "pow_zabudowy_kontrolna / pow_dzialki")
    # pokrycie terenu (nie-PBC)
    utw = unary_union([q for _i, q, _n in g["utw"]]) if g["utw"] else Polygon()
    tar = unary_union([q for _i, q in g["tarasy"]]).difference(p0) if g["tarasy"] else Polygon()
    op = unary_union([q for _i, q in g["opaska"]]) if g["opaska"] else Polygon()
    zb = g["zbiornik"]
    zb_poly, zb_zal = None, False
    if zb and zb.get("xy") is not None:
        if _poly(zb.get("obrys")) is not None:
            zb_poly = _poly(zb["obrys"])
        elif zb.get("sr"):
            zb_poly = Point(zb["xy"]).buffer(float(zb["sr"]) / 2.0)
        else:           # jak audyt A1 (W-031): rzut ≈ max(2,0; V/1,6) m² — ZAŁOŻENIE przy braku wymiarów
            a_ = max(2.0, float(zb.get("V") or 5.0) / 1.6)
            zb_poly, zb_zal = Point(zb["xy"]).buffer(math.sqrt(a_ / math.pi)), True
    od = _poly((raw.get("odpady") or {}).get("obrys")) if isinstance(raw.get("odpady"), dict) else None
    cover = unary_union([q for q in (p0, utw, tar, op, zb_poly, od) if q is not None and not q.is_empty])
    out["pow_utwardzona"] = _poz(float(utw.difference(p0).area), "m²", f"{POD['RPB14']} lit. b",
                                 "drogi, dojścia, place, stanowiska (utwardzenia z dzialka.yaml, bez części pod "
                                 "budynkiem) — w tym nawierzchnie ażurowe (nie PBC)",
                                 elementy={i: round(q.area, 2) for i, q, _n in g["utw"]})
    out["pow_tarasow"] = _poz(float(tar.area), "m²", f"{POD['RPB14']} lit. a (tarasy naziemne — poza pow. zabudowy)",
                              "tarasy i podesty naziemne (budynek.yaml: tarasy) poza obrysem parteru")
    out["pow_opaski"] = _poz(float(op.area), "m²", "odwodnienia: opaska_zwirowa",
                             "pas żwiru między obrysem parteru a linią opaski, bez tarasów i utwardzeń — nie PBC")
    # PBC: teren zapewniający naturalną wegetację (zieleń modelu) poza pokryciem; dach zielony — rezerwa 50 %
    ziel = [q for _i, q, t in g["ziel"] if t in ("trawnik", "rabata", "zywoplot", "łąka", "laka", "ogrod")]
    green = unary_union(ziel).intersection(g["plot"]) if ziel else g["plot"]
    if g["niecka"] is not None:
        green = unary_union([green, g["niecka"].intersection(g["plot"])])
    pbc_g = green.difference(cover)
    out["pbc"] = _poz(float(pbc_g.area), "m²", POD["28"],
                      "teren zieleni modelu (trawnik, rabaty, żywopłoty, niecka chłonna) minus: parter, tarasy, "
                      "utwardzenia (także ażurowe), opaska żwirowa, pojemniki, teren nad zbiornikiem"
                      + (" (rzut ZAŁOŻONY — brak wymiarów zbiornika)" if zb_zal else ""))
    gr = []
    for d in model.dachy():
        p = model.przegroda(str(d.get("przegroda")))
        mats = [w.mat for w in p.warstwy] if p else []
        sub = any("SUBSTR" in str(mc).upper() or "substrat" in ((model.material(mc).nazwa or "").lower()
                                                                if model.material(mc) else "") for mc in mats)
        if (sub or "ziel" in (p.nazwa.lower() if p else "")) and _ring(d.get("obrys")):
            from .model import make_polygon
            q = g["G"](make_polygon(d["obrys"], d.get("otwory") or []))
            if q.area >= 10.0:
                gr.append((str(d.get("id")), q))
    rez = 0.5 * sum(q.area for _i, q in gr)
    out["pbc_rezerwa_dach"] = _poz(rez, "m²", f"{POD['28']} (50 % stropodachów z wegetacją, ≥ 10 m²)",
                                   "50 % rzutu dachów zielonych — REZERWA, nie wliczana do spełnienia wskaźnika",
                                   dachy=[i for i, _q in gr])
    out["udzial_pbc"] = _poz(pbc_g.area / A if A else 0.0, "–", POD["29"], "pbc / pow_dzialki (bez rezerwy)")
    out["udzial_pbc_z_rezerwa"] = _poz((pbc_g.area + rez) / A if A else 0.0, "–", POD["29"],
                                       "(pbc + pbc_rezerwa_dach) / pow_dzialki — informacyjnie")
    g.update(cover=cover, pbc=pbc_g, zbiornik_poly=zb_poly)
    return _wskazniki_cd(model, ir, g, out, A, z0)


def _wskazniki_cd(model, ir, g, out, A, z0) -> dict:
    raw = g["raw"]
    T = Teren(raw.get("teren") or {})
    nums = numery_kondygnacji(model)
    pk = {k: float(q.area) for k, q in g["storeys"].items()}
    out["pow_kondygnacji"] = _poz(pk, "m²", POD["33"], "obrys zewnętrzny ścian zewnętrznych każdej kondygnacji "
                                  "(model.obrys_kondygnacji), bez balkonów, loggii i tarasów")
    nadz = g["nadz"]
    s_all = sum(pk.values())
    s_nadz = sum(pk[k] for k in nadz)
    out["suma_pow_kondygnacji"] = _poz(s_all, "m²", POD["31"], "Σ pow. wszystkich kondygnacji")
    out["suma_pow_kondygnacji_nadziemnych"] = _poz(s_nadz, "m²", POD["32"], "Σ pow. kondygnacji nadziemnych")
    out["intensywnosc"] = _poz(s_all / A if A else 0.0, "–", POD["31"], "suma_pow_kondygnacji / pow_dzialki")
    out["intensywnosc_nadziemna"] = _poz(s_nadz / A if A else 0.0, "–", POD["32"],
                                         "suma_pow_kondygnacji_nadziemnych / pow_dzialki")
    # --- teren na obwodzie rzutu ścian zewnętrznych (niższa z istn./proj. w każdym punkcie)
    Q = obwod_punkty(g["footprint"], 0.25)
    tn, ti, tp = T.nizsza(Q)
    ok = np.isfinite(tn)
    i_min, i_max = int(np.nanargmin(np.where(ok, tn, np.nan))), int(np.nanargmax(np.where(ok, tn, np.nan)))
    t_min, t_max = float(tn[i_min]), float(tn[i_max])
    t_sr = (t_min + t_max) / 2.0
    # kondygnacje nadziemne (pkt 34): zagłębienie ≤ połowy wysokości w świetle
    kn = []
    for k in model.kondygnacje:
        zf = z0 + float(k.rzedna)
        zag = max(0.0, t_max - zf)
        hsw = float(k.wys_w_swietle or k.wys_kondygnacji or 0.0)
        kn.append(dict(id=k.id, zaglebienie=round(zag, 3), polowa_wys=round(hsw / 2.0, 3),
                       nadziemna=zag <= hsw / 2.0 + 1e-9))
    out["kondygnacje_nadziemne"] = _poz(sum(1 for q in kn if q["nadziemna"]), "szt.", POD["34"],
                                        "kondygnacja niezagłębiona poniżej przylegającego terenu (maks. rzędna terenu "
                                        "na obwodzie) o więcej niż połowę wysokości w świetle", kondygnacje=kn)
    # --- najwyższy punkt
    cand = punkty_najwyzsze(model, ir)
    zt, el, src, zal = max(cand, key=lambda c: c[0])
    pewne = [c for c in cand if not c[3]]
    zt2 = max(pewne, key=lambda c: c[0]) if pewne else None
    H = z0 + zt - t_sr
    out["wysokosc_zabudowy"] = _poz(
        H, "m", POD["30"],
        "H = z_top − t_śr; z_top — najwyższy punkt budynku na dachu/ścianie/attyce (wyłączenia zamknięte: komin, "
        "nadbudówka maszynowni dźwigu lub innego pomieszczenia technicznego, wyjście z klatki; czerpnia, wyrzutnia, "
        "wywiewka, PV, wyłaz, świetlik — wliczane); t_śr = (t_min + t_max) / 2 na obwodzie rzutu ścian zewnętrznych, "
        "w każdym punkcie niższa z rzędnych terenu istniejącego/projektowanego",
        element=el, zrodlo=src, zalozenie=zal, z_top=zt, z_top_abs=z0 + zt, t_min=t_min, t_max=t_max, t_sr=t_sr,
        p_t_min=Q[i_min].tolist(), p_t_max=Q[i_max].tolist(),
        bez_zalozen=(z0 + zt2[0] - t_sr, zt2[1]) if zt2 and zal else None,
        od_t_min_A1=z0 + zt - t_min,
        kandydaci=sorted([(round(c[0], 3), c[1]) for c in cand], reverse=True)[:8])
    # --- WT § 6: teren (niższa z istn./proj.) przy najniżej położonym wejściu → wierzch najwyższego stropodachu
    wej = []
    k0 = g["k0"]
    for o in model.otwory():
        if o.typ not in TYPY_WEJSC or o.kond != k0 or o.kierunek_zewn is None:
            continue
        c = o.srodek + np.asarray(o.kierunek_zewn) * (abs(o.sciana.face_t(o.sciana.ext_side)) + 0.6)
        q = g["P"](c)
        h, _a, _b = T.nizsza(q)
        wej.append((float(h[0]), o.id, o.typ))
    zs = max(((_pokrycie(model, d)[2], str(d.get("id"))) for d in model.dachy()), default=(None, None))
    if wej and zs[0] is not None:
        h_we, o_we, t_we = min(wej)
        Hwt = z0 + zs[0] - h_we
        out["wysokosc_WT6"] = _poz(Hwt, "m", POD["WT6"],
                                   "od poziomu terenu (niższa z rzędnych istn./proj., 0,6 m przed licem) przy najniżej "
                                   "położonym wejściu (drzwi, HS, brama parteru) do górnej powierzchni najwyżej "
                                   "położonego stropodachu z warstwami (maks. klina), bez attyk",
                                   wejscie=o_we, typ_wejscia=t_we, H_teren=h_we, z_top=zs[0], dach=zs[1],
                                   grupa="N" if Hwt <= 12.0 else "SW")
    mp = [x for x in raw.get("miejsca_postojowe") or [] if isinstance(x, dict)]
    out["miejsca_postojowe"] = _poz(len(mp), "szt.", POD["WT18"], "stanowiska z dzialka.yaml: miejsca_postojowe",
                                    garaz=sum(1 for x in mp if str(x.get("typ")) in ("garaz", "wiata")),
                                    zewn=sum(1 for x in mp if str(x.get("typ")) == "zewn"))
    sp = [float(d.get("spadek") or 0.0) for d in model.dachy()]
    out["kat_dachu"] = _poz(math.degrees(math.atan(max(sp))) if sp else None, "°", "MPZP (geometria dachu)",
                            "atan(maks. spadku dachów z budynek.yaml)")
    out["_geom"] = dict(footprint=g["footprint"], p0=g["p0"], cover=g["cover"], pbc=g["pbc"],
                        plyty=g["plyty"], zbiornik=g["zbiornik_poly"], teren=T, obwod=Q)
    return out


def tabela(w: dict) -> list[tuple]:
    """Wiersze (klucz, wartość, jednostka, podstawa, metoda) do raportów tekstowych."""
    rows = []
    for k, v in w.items():
        if k.startswith("_") or not isinstance(v, dict):
            continue
        rows.append((k, v["wartosc"], v["jedn"], v["podstawa"], v["metoda"]))
    return rows
