"""Wspólne narzędzia generatorów widoków: adapter materiałów modelu → oznaczenia silnika, numeracja pomieszczeń,
kontekst widoku (model + IR + konfiguracja) i rozmieszczanie adnotacji bez kolizji (``Placer``).

Adapter jest potrzebny, bo kody kreskowań w ``budynek.yaml`` (np. ``IZOLACJA_TWARDA``, ``MEMBRANA``, ``BRAK``,
``GRUNT_NASYPOWY``) nie pokrywają się 1:1 z kodami wzorów silnika ``lamela.draft.hatch``, a IR używa kodów
pomocniczych (``RAMA_ALU``, ``SZKLO``, ``OBROBKA_BLACH``…), których nie ma w sekcji ``materialy`` modelu.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from shapely.ops import linemerge, unary_union

from ..draft import hatch as H
from ..draft.core import PArc, PFill, PLine, PText, Viewport, text_items
from ..draft.geom import arc_pts, lines_of, polygons_of

# ------------------------------------------------------------------------------------------------ materiały
NO_HATCH = "BRAK_OZN"   # wzór "pusty" (materiały bez oznaczenia — np. płytki, legary): sam kontur


@H.register(NO_HATCH, "bez oznaczenia materiału (sam kontur)", "—")
def _no_hatch(c, poly, layer, **kw):   # pragma: no cover - celowo nic nie rysuje
    return None


# kody kreskowań modelu → kody silnika (poza aliasami ``hatch.ALIASES``)
KRESK_ALIAS = {
    "IZOLACJA_MIEKKA": "IZOL_MIEKKA", "IZOLACJA_TWARDA": "IZOL_TWARDA", "IZOL_XPS": "IZOL_XPS",
    "GRUNT_NASYPOWY": "NASYP", "NASYP": "NASYP", "MUR_CERAM": "MUR_CERAMIKA", "BET_KOM": "BETON_KOMORKOWY",
    "PAROIZOL": "PAROIZOLACJA", "WYLEWKA": "JASTRYCH", "ZAPRAWA": "TYNK", "PODSYPKA": "PIASEK",
    "DREWNO": "DREWNO_POPRZ", "DREWNO_WZDL": "DREWNO_WZDL", "GRUNT": "GRUNT_RODZIMY",
}
MEMBRANE_CODES = ("IZOL_PRZECIWWODNA", "IZOL_PRZECIWWILGOCIOWA", "PAROIZOLACJA", "MEMBRANA_PAROPRZEP")

# kody pomocnicze IR (nie występują w budynek.yaml): nazwa, kolor, kreskowanie w przekroju
IR_MATS = {
    "RAMA_ALU": ("Stolarka — profile aluminiowe, antracyt", "#2b2f33", "STAL"),
    "SZKLO": ("Szkło (szyby zespolone)", "#a9c3cd", "SZKLO"),
    "SZKLO_BAL": ("Balustrada — szkło klejone", "#c9dde2", "SZKLO"),
    "STAL_BAL": ("Stal malowana proszkowo (balustrady, rygle)", "#2c3034", "STAL"),
    "STAL_NIERDZ": ("Stal nierdzewna (pochwyty)", "#b9bdc0", "STAL"),
    "DRZWI_WEWN": ("Drzwi wewnętrzne", "#efece6", NO_HATCH),
    "DRZWI_ZEWN": ("Drzwi zewnętrzne, płycina aluminiowa", "#34383c", NO_HATCH),
    "BRAMA_GAR": ("Brama garażowa segmentowa", "#3a3e42", NO_HATCH),
    "OBROBKA_BLACH": ("Obróbki blacharskie (blacha powlekana)", "#3b3f43", "STAL"),
    "PARAPET_WEWN": ("Parapet wewnętrzny", "#f1f0ec", NO_HATCH),
    "SCHODY": ("Schody — płyta żelbetowa z okładziną", "#c7a276", "ZELBET"),
    "NAW_PODBUDOWA": ("Podbudowa nawierzchni (kruszywo)", "#8d877d", "ZWIR"),
    "NAW_DESKA": ("Deska tarasowa", "#6d5847", NO_HATCH),
    "NAW_KOSTKA": ("Kostka betonowa", "#6c6e71", NO_HATCH),
    "NAW_KOSTKA_JASNA": ("Kostka betonowa jasna", "#a9a59d", NO_HATCH),
    "NAW_PLYTY": ("Płyty betonowe", "#bdb9b0", NO_HATCH),
    "NAW_BETON": ("Beton", "#b3b0a8", "BETON"),
    "NAW_ZWIR": ("Żwir", "#a49e92", "ZWIR"),
}


def material_name(model, code: str) -> str:
    m = model.material(code) if model is not None else None
    if m is not None and m.nazwa:
        return m.nazwa
    if code in IR_MATS:
        return IR_MATS[code][0]
    return code


def material_color(model, code: str) -> str:
    """Kolor materiału do kolorystyki elewacji: ``kolor`` z modelu → kody IR → biblioteka PBR 3D."""
    m = model.material(code) if model is not None else None
    raw = getattr(m, "raw", None) or {}
    if isinstance(raw.get("kolor_elewacji"), str):
        return raw["kolor_elewacji"]
    if m is not None and isinstance(m.kolor, str) and re.match(r"^#[0-9a-fA-F]{6}$", m.kolor):
        return m.kolor
    if code in IR_MATS:
        return IR_MATS[code][1]
    try:
        from ..model3d.materials import pbr_for
        return pbr_for(code, model).color
    except Exception:  # pragma: no cover
        return "#d0d0d0"


def hatch_code(model, code: str) -> str:
    """Kod wzoru kreskowania silnika dla kodu materiału modelu/IR (zawsze poprawny kod ``hatch.PATTERNS``)."""
    m = model.material(code) if model is not None else None
    c = (code or "").upper()
    if m is None:
        if code in IR_MATS:
            return IR_MATS[code][2] or NO_HATCH
        for pat, hc in ((r"SZKL", "SZKLO"), (r"STAL|ALU|BLACH", "STAL"), (r"ZB|ZELBET|BET", "ZELBET"),
                        (r"TYNK", "TYNK"), (r"EPS|STYRO", "IZOL_TWARDA"), (r"XPS", "IZOL_XPS"), (r"PIR", "IZOL_PIR"),
                        (r"WELN|MW", "IZOL_MIEKKA"), (r"SIL", "MUR_SILIKAT"), (r"DREW|DESK", "DREWNO_POPRZ")):
            if re.search(pat, c):
                return hc
        return NO_HATCH
    k = (m.kreskowanie or "").upper().strip()
    name = (m.nazwa or "").lower()
    if k in ("", "BRAK", "NONE", "-"):
        return NO_HATCH
    if k == "MEMBRANA":
        if "paroiz" in name or "PAROIZ" in c or "folia pe" in name:
            return "PAROIZOLACJA"
        if "paroprzep" in name or "wiatroiz" in name:
            return "MEMBRANA_PAROPRZEP"
        return "IZOL_PRZECIWWODNA"
    if k in ("IZOLACJA_TWARDA", "IZOL_TWARDA"):
        if "XPS" in c or "ekstrud" in name:
            return "IZOL_XPS"
        if re.search(r"PIR|PUR", c) or "pir" in name:
            return "IZOL_PIR"
        return "IZOL_TWARDA"
    k = KRESK_ALIAS.get(k, k)
    try:
        return H.resolve(k)
    except KeyError:
        return NO_HATCH


def cut_kind(hc: str, klasa: str | None = None, konstr: bool = False, wall_typ: str | None = None,
             horizontal_struct: bool = False) -> str:
    """Rodzaj elementu w ``CutSet`` (pióro konturu, priorytet)."""
    if hc in MEMBRANE_CODES:
        return "membrana"
    if hc == "STAL":
        return "stal"
    if konstr:
        if wall_typ == "scianka_dzialowa":
            return "dzial"
        return "strop" if horizontal_struct else "konstr"
    if klasa == "izolacja" or hc.startswith("IZOL_"):
        return "izol"
    if klasa == "wykonczenie":
        return "wyk"
    return "warstwa"


def klasa_mat(model, code: str) -> str:
    try:
        return model._klasa_mat(code)
    except Exception:  # pragma: no cover
        return "inna"


def layer_text(model, code: str, d: float) -> str:
    """Opis warstwy przegrody: „nazwa materiału — d cm” (bez powtarzania grubości zawartej w nazwie)."""
    from ..draft import fmt
    name = material_name(model, code)
    cm = d * 100.0
    if cm >= 1.0 - 1e-9:
        dt = fmt.num(cm, 1, strip=True) + " cm"
    else:
        dt = fmt.num(d * 1000.0, 1, strip=True) + " mm"
    if re.search(r"\b" + re.escape(dt.split()[0]) + r"\s*" + dt.split()[1] + r"\b", name):
        return name
    return f"{name} {dt}"


# ------------------------------------------------------------------------------------------------ numeracja
def storey_numbers(model) -> dict:
    """Numer kondygnacji wg PN-B-01025 3.4 / ISO 4157-1: kondygnacja przy terenie = 1 (najbliższa ±0,00),
    kolejne wyżej 2, 3…, niżej −1, −2… Zwraca {id_kondygnacji: numer}."""
    ks = list(model.kondygnacje)
    if not ks:
        return {}
    i0 = min(range(len(ks)), key=lambda i: abs(ks[i].rzedna))
    out = {}
    for i, k in enumerate(ks):
        d = i - i0
        out[k.id] = d + 1 if d >= 0 else d
    return out


def room_label(model, rid: str, mode: str = "iso") -> str:
    """Numer pomieszczenia na rysunku. mode='model' — identyfikator z modelu (np. 0.05); 'iso' — numer kondygnacji
    wg PN-B-01025 + numer kolejny z modelu (0.05 → 1.05, rekomendacja R4 pkt 3.9)."""
    if mode == "model":
        return rid
    r = model.pomieszczenie(rid)
    m = re.match(r"^(-?\d+)\.(\d+)(.*)$", str(rid))
    if r is None or m is None:
        return rid
    n = storey_numbers(model).get(r.kond)
    if n is None:
        return rid
    return f"{n}.{m.group(2)}{m.group(3)}"


def slug(s: str) -> str:
    tr = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
    s = s.translate(tr).lower()
    s = re.sub(r"[^a-z0-9]+", "_", s).strip("_")
    return s[:48]


# ------------------------------------------------------------------------------------------------ kontekst
@dataclass
class ViewContext:
    """Dane wspólne dla wszystkich widoków jednego modelu."""
    model: object
    ir: object
    cfg: dict = field(default_factory=dict)
    furniture: list = field(default_factory=list)       # model/wyposazenie.yaml
    sections: dict = field(default_factory=dict)        # id → definicja przekroju (znormalizowana)
    src: str = ""
    problems: list = field(default_factory=list)        # uwagi generatorów (problemy modelu)

    def opt(self, key, default=None):
        return self.cfg.get(key, default)

    def note(self, where: str, msg: str):
        s = f"{where}: {msg}"
        if s not in self.problems:
            self.problems.append(s)

    @property
    def building_prisms(self):
        """Pryzmy budynku (bez otoczenia; tarasy zaliczone do budynku)."""
        if not hasattr(self, "_bp"):
            kinds_out = {"vegetation", "context", "vehicle", "road", "fence", "pavement", "terrain"}
            self._bp = [p for p in self.ir.prisms if p.kind not in kinds_out and p.meta.get("group") != "otoczenie"]
        return self._bp


def load_furniture(path) -> list:
    """Wyposażenie z ``model/wyposazenie.yaml``: lista {kond, typ, xy, obrot, wym, …} (klucz główny ``wyposazenie``
    albo sama lista)."""
    import yaml
    p = Path(path)
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("wyposazenie") or data.get("elementy") or []
    return [d for d in (data or []) if isinstance(d, dict)]


# ------------------------------------------------------------------------------------------------ geometria
def as_lines(g) -> list[np.ndarray]:
    """Łamane (tablice punktów) z dowolnej geometrii liniowej/powierzchniowej, scalone (linemerge)."""
    if g is None or g.is_empty:
        return []
    ls = []
    for a in lines_of(g):
        if len(a) >= 2:
            ls.append(LineString(a))
    if not ls:
        return []
    try:
        mg = linemerge(MultiLineString(ls))
    except Exception:
        mg = MultiLineString(ls)
    return [a for a in lines_of(mg) if len(a) >= 2]


def draw_lines(c, g, layer, pen=None, lt=None, min_len: float = 0.0, color=None, z=None):
    """Rysuje geometrię liniową (po scaleniu) — pomija odcinki krótsze niż ``min_len`` [m]."""
    n = 0
    for a in as_lines(g):
        if min_len and LineString(a).length < min_len:
            continue
        c.polyline(a, layer, pen=pen, lt=lt, color=color, z=z)
        n += 1
    return n


def poly_of(obj) -> Polygon | MultiPolygon:
    if isinstance(obj, (Polygon, MultiPolygon)):
        return obj
    return Polygon(obj)


def clean(g, tol: float = 1e-7):
    if g is None or g.is_empty:
        return Polygon()
    try:
        g = shapely.make_valid(g)
    except Exception:
        g = g.buffer(0)
    polys = [p for p in polygons_of(g) if p.area > tol]
    if not polys:
        return Polygon()
    return unary_union(polys)


def label_point(poly, tol: float = 0.02) -> np.ndarray:
    """Punkt najdalszy od brzegu (biegun niedostępności) — do opisów pomieszczeń i materiałów."""
    try:
        pg = max(polygons_of(poly), key=lambda p: p.area)
        from shapely.ops import polylabel
        p = polylabel(pg, tolerance=tol)
        return np.array([p.x, p.y])
    except Exception:
        c = poly.representative_point()
        return np.array([c.x, c.y])


# ------------------------------------------------------------------------------------------------ kolizje adnotacji
def prim_shapes(prims, k: float, line_buf_mm: float = 0.35, text_pad_mm: float = 0.0):
    """Obrysy prymitywów: (napisy [Polygon], linie [Polygon — pas wokół linii], wypełnienia [Polygon])."""
    texts, lines, fills = [], [], []
    b = line_buf_mm * k
    for p in prims:
        if isinstance(p, PText):
            _it, bx = text_items(p, k)
            g = Polygon(bx)
            texts.append(g.buffer(text_pad_mm * k, join_style=2) if text_pad_mm else g)
        elif isinstance(p, PLine):
            pts = p.pts if not p.closed else np.vstack([p.pts, p.pts[:1]])
            if len(pts) >= 2:
                lines.append(LineString(pts).buffer(b, cap_style=2, join_style=2))
        elif isinstance(p, PArc):
            pts = arc_pts(p.c, p.r, 0.0, 360.0, 10.0) if p.full else arc_pts(p.c, p.r, p.a0, p.a1, 10.0)
            lines.append(LineString(pts).buffer(b))
        elif isinstance(p, PFill):
            try:
                fills.append(Polygon(p.rings[0]).buffer(0))
            except Exception:
                pass
    return texts, lines, fills


class Placer:
    """Rejestr zajętych obszarów rzutni (współrzędne modelu) i wybór położeń adnotacji o najmniejszej kolizji.

    Kategorie przeszkód: 'area' (elementy przecięte, symbole — napisy nie mogą na nie wchodzić), 'text' (napisy,
    także dla linii nowych adnotacji), 'line' (linie rysunku — kolizja tylko z napisami, z wagą)."""

    def __init__(self, k: float):
        self.k = k
        self.geoms: list = []
        self.cat: list = []
        self.w: list = []
        self._tree = None
        self._n_tree = 0

    def add(self, geom, cat: str = "area", w: float = 1.0):
        for g in polygons_of(geom) if not isinstance(geom, (LineString, MultiLineString)) else [geom.buffer(0.3 * self.k)]:
            if g.is_empty or g.area <= 0:
                continue
            self.geoms.append(g)
            self.cat.append(cat)
            self.w.append(w)

    def add_lines(self, geom, w: float = 0.4, buf_mm: float = 0.3):
        if geom is None or geom.is_empty:
            return
        g = geom.buffer(buf_mm * self.k, cap_style=2, join_style=2)
        self.add(g, "line", w)

    def add_prims(self, prims, w_text: float = 1.0, w_line: float = 0.5, w_fill: float = 1.0):
        t, l, f = prim_shapes(prims, self.k)
        for g in t:
            self.add(g, "text", w_text)
        for g in l:
            self.add(g, "line", w_line)
        for g in f:
            self.add(g, "area", w_fill)

    def _query(self, g):
        if self._tree is None or self._n_tree != len(self.geoms):
            self._tree = shapely.STRtree(self.geoms) if self.geoms else None
            self._n_tree = len(self.geoms)
        if self._tree is None:
            return []
        return self._tree.query(g)

    def cost(self, texts, lines=(), fills=()) -> float:
        """Koszt kolizji [mm² papieru] nowych napisów (z wszystkim) i linii/wypełnień (z napisami)."""
        k2 = self.k * self.k
        c = 0.0
        base = {"text": 4.0, "area": 2.0, "line": 1.0}
        for g in texts:
            for i in self._query(g):
                gi = self.geoms[i]
                if gi.intersects(g):
                    a = gi.intersection(g).area / k2
                    if a < 0.02:
                        continue
                    c += (base[self.cat[i]] + a * (3.0 if self.cat[i] == "text" else 1.0)) * self.w[i]
        for g in list(lines) + list(fills):
            for i in self._query(g):
                if self.cat[i] != "text":
                    continue
                gi = self.geoms[i]
                if gi.intersects(g):
                    a = gi.intersection(g).area / k2
                    if a < 0.02:
                        continue
                    c += (1.0 + a) * self.w[i] * 0.6
        return c

    def trial_cost(self, vp: Viewport, draw_fn, cand, bounds=None) -> tuple[float, list]:
        tmp = Viewport(vp.scale)
        draw_fn(tmp, cand)
        t, l, f = prim_shapes(tmp.prims, vp.k, line_buf_mm=0.2, text_pad_mm=0.6)
        c = self.cost(t, l, f)
        if bounds is not None:
            B = bounds
            for g in t:
                if not B.contains(g):
                    c += 50.0 + g.difference(B).area / (self.k * self.k) * 5.0
        return c, tmp.prims

    def place(self, vp: Viewport, draw_fn, candidates, penalty_step: float = 0.05, bounds=None,
              max_cost: float | None = None, register: bool = True):
        """Rysuje adnotację ``draw_fn(canvas, cand)`` w najlepszym z ``candidates`` (kolejność = preferencja).
        Zwraca (wybrany kandydat, koszt) lub (None, koszt) gdy koszt > max_cost (wtedy nic nie rysuje)."""
        best, best_c = None, None
        for i, cand in enumerate(candidates):
            c, _ = self.trial_cost(vp, draw_fn, cand, bounds)
            c += i * penalty_step
            if best_c is None or c < best_c - 1e-9:
                best, best_c = cand, c
            if c <= i * penalty_step + 1e-6:
                break
        if best is None or (max_cost is not None and best_c > max_cost):
            return None, best_c
        n0 = len(vp.prims)
        draw_fn(vp, best)
        if register:
            self.add_prims(vp.prims[n0:])
        return best, best_c


def rect_candidates(center, dxs, dys):
    out = []
    for dy in dys:
        for dx in dxs:
            out.append((center[0] + dx, center[1] + dy))
    out.sort(key=lambda p: (p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2)
    return out


def spiral(center, step: float, n_rings: int = 4, per_ring: int = 8):
    """Kandydaci położenia: środek, potem pierścienie wokół (preferencja: blisko środka)."""
    out = [tuple(center)]
    for r in range(1, n_rings + 1):
        m = per_ring * r
        for i in range(m):
            a = 2 * math.pi * i / m
            out.append((center[0] + math.cos(a) * step * r, center[1] + math.sin(a) * step * r))
    return out
