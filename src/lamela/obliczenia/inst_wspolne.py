"""Elementy wspólne biblioteki obliczeń instalacji (``lamela.obliczenia.sanitarne``, ``lamela.obliczenia.elektryka``).

Zawartość:
* formatowanie liczb (przecinek dziesiętny), kroki obliczeń (:class:`Krok` — opis, wzór, podstawienie, wynik, podstawa)
  i warunki (:class:`Warunek` — wartość, relacja, limit, podstawa, identyfikator wymagania W-xxx),
  składanie raportu markdown (:class:`Raport`);
* odczyt wymagań liczbowych z ``docs/10_podstawy_prawne/wymagania.yaml`` (:func:`wym`) — wartości z rejestru mają
  pierwszeństwo przed stałymi wpisanymi w modułach;
* dane klimatyczne i opadowe (``inst_dane/``): PANDa 2050 C10 (Aquanet 2024), normy opadowe IMGW 1991–2020, PVGIS 5.3
  (miesięczne, godzinowe 2019, TMY) — z metadanymi źródła i datą pobrania;
* wyciąg danych z modelu (``model/budynek.yaml`` + ``dzialka.yaml`` + ``wyposazenie.yaml`` + ``instalacje.yaml``)
  do struktury :class:`DaneBudynku`, na której pracują moduły obliczeniowe.

Oznaczenia statusu wartości (jak w rejestrze wymagań): [NZW] — niezweryfikowana w tekście normy (źródło wtórne),
[ZAŁ] — założenie projektowe / dana przykładowa, [INT] — interpretacja, [W] — źródło wtórne (literatura),
[UPR] — uproszczenie przyjęte w bibliotece.

Kontrakt danych z modułów fizyki budowli / energii (budowane równolegle — ``lamela.obliczenia.fizyka``, ``energia``):
funkcja :func:`phi_hl_z` przyjmuje projektowe obciążenie cieplne pomieszczeń w dowolnej z postaci: ``dict {id: W}``,
obiekt z atrybutem ``pomieszczenia`` (lista obiektów/słowników z polami ``id`` i ``phi_HL``/``Phi_HL``/``phi_hl``/
``fi_HL``/``Q``) albo z metodą ``per_pomieszczenie()``, lista takich rekordów, ścieżka do pliku YAML/JSON.
Analogicznie :func:`wentylacja_z` — strumienie powietrza (``{id: {"naw": m³/h, "wyw": m³/h}}`` lub suma).
"""
from __future__ import annotations

import csv
import gzip
import io
import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

MINUS = "−"
REPO = Path(__file__).resolve().parents[3]
DANE = Path(__file__).resolve().parent / "inst_dane"
WYMAGANIA_YAML = REPO / "docs" / "10_podstawy_prawne" / "wymagania.yaml"

G = 9.81          # m/s²
RHO_W = 1000.0    # kg/m³ (woda, obliczenia hydrauliczne)
C_W = 4.19        # kJ/(kg·K)


# ==================================================================================================
# Formatowanie
# ==================================================================================================
def f(x: Any, nd: int = 2) -> str:
    """Liczba z przecinkiem dziesiętnym: ``f(12.345) → '12,35'``; napisy bez zmian; None → '—'."""
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if isinstance(x, bool):
        return "tak" if x else "nie"
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if math.isinf(xf):
        return "∞"
    if math.isnan(xf):
        return "—"
    s = f"{xf:.{nd}f}" if nd > 0 else f"{round(xf):d}"
    s = s.replace(".", ",")
    if s.startswith("-"):
        body = s[1:]
        if set(body) <= set("0,"):
            return body
        s = MINUS + body
    return s


def fa(x: Any, sig: int = 3) -> str:
    """Liczba z automatyczną liczbą miejsc (≈ ``sig`` cyfr znaczących), notacja ×10⁻ⁿ dla małych wartości."""
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    xf = float(x)
    if xf == 0:
        return "0"
    ax = abs(xf)
    if ax < 1e-3 or ax >= 1e7:
        e = int(math.floor(math.log10(ax)))
        m = xf / 10 ** e
        sup = str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
        return f"{f(m, max(sig - 1, 0))}·10{sup}"
    nd = max(0, sig - 1 - int(math.floor(math.log10(ax))))
    return f(xf, min(nd, 4))


def proc(x: float, nd: int = 1) -> str:
    return f(100.0 * x, nd) + " %"


def tabela(naglowki: list[str], wiersze: list[list], wyrownanie: str | None = None) -> str:
    """Tabela markdown. ``wyrownanie`` — napis z liter l/c/r dla kolumn (domyślnie: 1. kolumna l, reszta r)."""
    n = len(naglowki)
    wyr = wyrownanie or ("l" + "r" * (n - 1))
    sep = {"l": ":---", "c": ":---:", "r": "---:"}
    out = ["| " + " | ".join(str(h) for h in naglowki) + " |",
           "|" + "|".join(sep.get(c, "---") for c in wyr[:n].ljust(n, "r")) + "|"]
    for w in wiersze:
        cells = [(c if isinstance(c, str) else (str(c) if isinstance(c, int) and not isinstance(c, bool) else f(c)))
                 for c in w]
        cells += [""] * (n - len(cells))
        out.append("| " + " | ".join(c.replace("|", "\\|").replace("\n", " ") for c in cells[:n]) + " |")
    return "\n".join(out)


# ==================================================================================================
# Kroki, warunki, raport
# ==================================================================================================
@dataclass
class Krok:
    """Krok obliczeń: ``opis: wzór = podstawienie = wynik [jedn]`` (+ podstawa normowa)."""
    opis: str
    wzor: str = ""
    podst: str = ""
    wynik: Any = None
    jedn: str = ""
    podstawa: str = ""
    nd: int = 2

    def md(self) -> str:
        parts = [p for p in (self.wzor, self.podst) if p]
        w = self.wynik if isinstance(self.wynik, str) else (f(self.wynik, self.nd) if self.wynik is not None else "")
        rhs = " = ".join(parts)
        if w:
            rhs = (rhs + " = " if rhs else "") + f"**{w}**" + (f" {self.jedn}" if self.jedn else "")
        s = f"* {self.opis}" + (f": {rhs}" if rhs else "")
        if self.podstawa:
            s += f" — _{self.podstawa}_"
        return s


@dataclass
class Warunek:
    """Warunek sprawdzający. ``op``: '<=', '>=', '<', '>', 'zakres' (limit = (a, b)), '==' lub 'info'."""
    opis: str
    wartosc: Any
    op: str
    limit: Any
    jedn: str = ""
    podstawa: str = ""
    id: str = ""            # W-xxx z rejestru
    uwagi: str = ""
    nd: int = 2

    @property
    def ok(self) -> bool | None:
        v, L = self.wartosc, self.limit
        if self.op == "info" or v is None or L is None:
            return None
        try:
            if self.op == "<=":
                return v <= L + 1e-12
            if self.op == ">=":
                return v >= L - 1e-12
            if self.op == "<":
                return v < L
            if self.op == ">":
                return v > L
            if self.op == "zakres":
                return L[0] - 1e-12 <= v <= L[1] + 1e-12
            if self.op == "==":
                return v == L
        except TypeError:
            return None
        return None

    @property
    def status(self) -> str:
        return {True: "SPEŁNIONY", False: "**NIESPEŁNIONY**", None: "informacyjnie"}[self.ok]

    def _fv(self, v):
        if isinstance(v, (tuple, list)):
            return "–".join(f(x, self.nd) for x in v)
        return f(v, self.nd) if not isinstance(v, str) else v

    def wiersz(self) -> list:
        lim = self._fv(self.limit)
        rel = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "zakres": "∈", "==": "=", "info": ""}.get(self.op, self.op)
        return [self.id or "", self.opis, f"{self._fv(self.wartosc)} {self.jedn}".strip(),
                f"{rel} {lim} {self.jedn}".strip() if self.op != "info" else "—", self.status,
                (self.podstawa + (f"; {self.uwagi}" if self.uwagi else "")).strip("; ")]


def tabela_warunkow(warunki: list[Warunek]) -> str:
    return tabela(["ID", "Warunek", "Wartość", "Wymaganie", "Wynik", "Podstawa / uwagi"],
                  [w.wiersz() for w in warunki], "llrrll")


class Raport:
    """Budowniczy raportu markdown (nagłówki, akapity, tabele, kroki obliczeń, warunki, źródła)."""

    def __init__(self, tytul: str, podtytul: str = ""):
        self.linie: list[str] = [f"# {tytul}", ""]
        if podtytul:
            self.linie += [podtytul, ""]
        self.zrodla: list[str] = []
        self.warunki: list[Warunek] = []

    def h(self, poziom: int, tekst: str):
        self.linie += [f"{'#' * poziom} {tekst}", ""]
        return self

    def p(self, tekst: str):
        self.linie += [tekst, ""]
        return self

    def lista(self, pozycje: list[str]):
        self.linie += [f"* {x}" for x in pozycje] + [""]
        return self

    def tab(self, naglowki, wiersze, wyrownanie=None):
        self.linie += [tabela(naglowki, wiersze, wyrownanie), ""]
        return self

    def kroki(self, kroki: list[Krok]):
        self.linie += [k.md() for k in kroki] + [""]
        return self

    def war(self, warunki: list[Warunek], dopisz: bool = True):
        if not warunki:
            return self
        self.linie += [tabela_warunkow(warunki), ""]
        if dopisz:
            self.warunki += warunki
        return self

    def img(self, alt: str, plik: str):
        self.linie += [f"![{alt}]({plik})", ""]
        return self

    def zrodlo(self, *z: str):
        for x in z:
            if x not in self.zrodla:
                self.zrodla.append(x)
        return self

    def md(self) -> str:
        out = list(self.linie)
        if self.warunki:
            nie = [w for w in self.warunki if w.ok is False]
            out += ["## Podsumowanie sprawdzeń", "",
                    f"Warunków: {len(self.warunki)}; spełnionych: {sum(1 for w in self.warunki if w.ok)}; "
                    f"niespełnionych: {len(nie)}; informacyjnych: {sum(1 for w in self.warunki if w.ok is None)}.", ""]
            if nie:
                out += ["Niespełnione:", ""] + [f"* {w.id + ' — ' if w.id else ''}{w.opis}: {w._fv(w.wartosc)} "
                                                 f"{w.jedn} (wymaganie {w.op} {w._fv(w.limit)} {w.jedn})" for w in nie] + [""]
        if self.zrodla:
            out += ["## Źródła", ""] + [f"{i}. {z}" for i, z in enumerate(self.zrodla, 1)] + [""]
        return "\n".join(out).rstrip() + "\n"

    def zapisz(self, sciezka) -> Path:
        p = Path(sciezka)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(self.md(), encoding="utf-8")
        return p


# ==================================================================================================
# Wymagania (wymagania.yaml)
# ==================================================================================================
_WYM_CACHE: dict | None = None


def wymagania(sciezka=None) -> dict:
    """Wczytuje ``wymagania.yaml`` (słownik sekcji). Brak pliku → pusty słownik (moduły mają wartości zastępcze)."""
    global _WYM_CACHE
    if sciezka is None and _WYM_CACHE is not None:
        return _WYM_CACHE
    import yaml
    p = Path(sciezka) if sciezka else WYMAGANIA_YAML
    try:
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except (OSError, Exception):
        d = {}
    if sciezka is None:
        _WYM_CACHE = d
    return d


def wym(sekcja: str, klucz: str, domyslna=None, pelny: bool = False):
    """Wartość wymagania ``sekcja.klucz`` z ``wymagania.yaml`` (pole ``wartosc``); ``pelny=True`` → cały wpis."""
    e = (wymagania().get(sekcja) or {}).get(klucz)
    if e is None:
        return ({"wartosc": domyslna, "zrodlo": "wartość zastępcza modułu (brak w wymagania.yaml)", "id": None}
                if pelny else domyslna)
    if pelny:
        return e
    return e.get("wartosc", domyslna) if isinstance(e, dict) else e


def wym_zrodlo(sekcja: str, klucz: str) -> str:
    e = wym(sekcja, klucz, pelny=True)
    s = e.get("zrodlo", "") if isinstance(e, dict) else ""
    i = e.get("id") if isinstance(e, dict) else None
    st = e.get("status") if isinstance(e, dict) else None
    return (f"{i}: " if i else "") + s + (f" [{st}]" if st and st != "zweryfikowane" else "")


# ==================================================================================================
# Dane klimatyczne / opadowe / PV (inst_dane)
# ==================================================================================================
def _json(nazwa: str) -> dict:
    return json.loads((DANE / nazwa).read_text(encoding="utf-8"))


def panda_c10() -> dict:
    """PANDa 2050 C10 Poznań (Aquanet 2024, tab. 3): {'t_min_q': [[t, q], ...], 'zrodlo': ...}."""
    return _json("panda2050_poznan_c10.json")


def opady_imgw() -> dict:
    """Normy opadowe IMGW-PIB 1991–2020, Poznań (miesięczne sumy [mm], suma roczna)."""
    return _json("imgw_poznan_opady_1991_2020.json")


def pvgis_miesiecznie() -> dict:
    return _json("pvgis_poznan_miesiecznie.json")


def _csv_gz(nazwa: str) -> tuple[list[str], list[list[str]]]:
    txt = gzip.decompress((DANE / nazwa).read_bytes()).decode("utf-8")
    rows = [r for r in csv.reader(io.StringIO(txt)) if r and not r[0].startswith("#")]
    return rows[0], rows[1:]


def pvgis_godzinowo() -> dict:
    """PVGIS seriescalc 2019 (UTC), moc [W] z 1 kWp dla wariantów S15/E10/W10 i T2m [°C]."""
    h, rows = _csv_gz("pvgis_poznan_2019_godzinowo.csv.gz")
    arr = np.array([[float(x) for x in r[1:]] for r in rows])
    return {"czas": [r[0] for r in rows], **{k: arr[:, i] for i, k in enumerate(h[1:])}}


def tmy() -> dict:
    """TMY Poznań (PVGIS 5.3): T2m [°C], G_h [W/m²] — 8760 h (UTC)."""
    h, rows = _csv_gz("pvgis_tmy_poznan.csv.gz")
    arr = np.array([[float(x) for x in r[1:]] for r in rows])
    return {"czas": [r[0] for r in rows], **{k: arr[:, i] for i, k in enumerate(h[1:])}}


# ==================================================================================================
# Dane z modelu
# ==================================================================================================
@dataclass
class Pom:
    id: str
    nazwa: str
    kond: str
    pow: float
    wys: float
    temp: float | None
    kategoria: str
    polygon: Any
    centroid: tuple
    z: float                      # rzędna posadzki kondygnacji
    went: dict = field(default_factory=dict)

    @property
    def rodzaj(self) -> str:
        """Rodzaj funkcjonalny z nazwy: lazienka|wc|kuchnia|pralnia|garaz|techniczne|sypialnia|pokoj|ruchu|inne."""
        n = self.nazwa.lower()
        for klucz, slowa in (("garaz", ("garaż", "garaz")), ("lazienka", ("łazien", "lazien")),
                             ("wc", ("wc", "toalet")), ("kuchnia", ("kuch",)), ("pralnia", ("pralni",)),
                             ("techniczne", ("techn", "kotłown")), ("sypialnia", ("sypial",)),
                             ("ruchu", ("hol", "koryt", "wiatroł", "klatk", "komunik")),
                             ("garderoba", ("garderob", "spiżar", "schowek"))):
            if any(s in n for s in slowa):
                return klucz
        if self.kategoria == "ruchu":
            return "ruchu"
        return "pokoj" if self.kategoria == "podstawowa" else "inne"

    @property
    def ogrzewane(self) -> bool:
        return self.temp is not None and self.temp >= 16 and self.rodzaj != "garaz"


@dataclass
class Dach:
    id: str
    obrys: Any                     # shapely Polygon (układ budynku)
    pole: float
    typ: str                       # 'plaski' | 'zielony' | 'taras' | 'wspornik'
    przegroda: str
    przegroda_nazwa: str
    rzedna: float                  # wierzch pokrycia (≈ wierzch płyty + warstwy) [m, względna]
    attyka_wys: float | None
    spadek: float | None
    wpusty: list = field(default_factory=list)          # [{xy, dn, podgrzewany}]
    przelewy: list = field(default_factory=list)        # [{xy, sciana_attyki, szer, wys, rzedna_dna}]
    rury_spustowe: list = field(default_factory=list)   # [{id, od_wpustu, trasa, xy_pion, dn, do}]
    spadki: list = field(default_factory=list)
    warstwy: list = field(default_factory=list)         # [(mat, d, nazwa_mat)]


@dataclass
class DaneBudynku:
    """Dane wejściowe obliczeń instalacji wyciągnięte z modelu (jedno źródło prawdy: ``model/*.yaml``)."""
    nazwa: str
    zrodla: dict
    kondygnacje: list                 # [{"id", "rzedna", "wys"}]
    pomieszczenia: list[Pom]
    dachy: list[Dach]
    obrysy: dict                      # kond → Polygon (lico zewn.)
    obrys_zabudowy: Any               # Polygon (suma obrysów)
    H_max: float                      # najwyższy punkt budynku (attyka) [m, względna]
    kubatura: float
    pow_zabudowy: float
    wyposazenie: list
    inst: dict                        # model/instalacje.yaml (sekcja 'instalacje')
    dzialka: dict                     # {'obrys', 'teren', 'droga', 'sasiedzi', 'uzbrojenie', 'retencja', 'odwodnienia', ...}
    zero_abs: float
    model: Any = None
    uwagi: list = field(default_factory=list)

    # ---- zapytania
    def pom(self, pid: str) -> Pom | None:
        return next((p for p in self.pomieszczenia if p.id == pid), None)

    def kond(self, kid: str) -> dict | None:
        return next((k for k in self.kondygnacje if k["id"] == kid), None)

    def rzedna(self, kid: str) -> float:
        k = self.kond(kid)
        return float(k["rzedna"]) if k else 0.0

    def pom_w_punkcie(self, kid: str, xy, tol: float = 0.35) -> Pom | None:
        """Pomieszczenie kondygnacji zawierające punkt (z tolerancją — punkty na licu ściany)."""
        from shapely.geometry import Point
        P = Point(float(xy[0]), float(xy[1]))
        best, dbest = None, 1e9
        for r in self.pomieszczenia:
            if r.kond != kid or r.polygon is None:
                continue
            d = r.polygon.distance(P)
            if d < dbest:
                best, dbest = r, d
        return best if dbest <= tol else None

    @property
    def A_f(self) -> float:
        """Powierzchnia o regulowanej temperaturze (pomieszczenia ogrzewane)."""
        return sum(p.pow for p in self.pomieszczenia if p.ogrzewane)

    @property
    def osoby(self) -> int:
        return int(self.inst.get("osoby") or wym("wentylacja", "liczba_osob", 5) or 5)

    def lok(self, klucz: str):
        """Lokalizacja z ``instalacje.lokalizacje`` → (x, y, kond) albo None."""
        v = (self.inst.get("lokalizacje") or {}).get(klucz)
        if v is None:
            return None
        if isinstance(v, dict):
            xy = v.get("xy")
            return (float(xy[0]), float(xy[1]), v.get("kond", "P0"))
        return (float(v[0]), float(v[1]), v[2] if len(v) > 2 else "P0")

    def teren_z(self, xy, projektowany: bool = True) -> float:
        """Rzędna terenu (względna) w punkcie — interpolacja IDW z punktów działki (brak → −0,30 m); gdy
        ``projektowany`` i w ``dzialka.yaml`` są ``teren.punkty_projektowane`` — z rzędnych projektowanych."""
        pts = self.dzialka.get("teren_proj") if projektowany and self.dzialka.get("teren_proj") is not None else None
        if pts is None:
            pts = self.dzialka.get("teren")
        if pts is None or len(pts) == 0:
            return -0.30
        d = np.hypot(pts[:, 0] - xy[0], pts[:, 1] - xy[1])
        if d.min() < 1e-6:
            return float(pts[d.argmin(), 2])
        w = 1.0 / d ** 2
        return float((w * pts[:, 2]).sum() / w.sum())

    def dystans_do_granicy(self, xy) -> float:
        from shapely.geometry import Point
        ob = self.dzialka.get("obrys")
        if ob is None:
            return float("nan")
        return float(ob.exterior.distance(Point(xy[0], xy[1])))

    def dystans_do_sasiada(self, xy) -> float:
        from shapely.geometry import Point
        s = self.dzialka.get("sasiedzi_zabudowa") or []
        if not s:
            return float("nan")
        return float(min(g.distance(Point(xy[0], xy[1])) for g in s))


ZIELONY_SLOWA = ("ziel", "sedum", "substrat", "wegetac", "roślin", "rozchodn", "przeciwkorzen")


def _typ_dachu(przegroda, mats: dict) -> str:
    if przegroda is None:
        return "plaski"
    txt = (przegroda.nazwa or "").lower() + " " + " ".join(
        (w.mat + " " + str((mats.get(w.mat).nazwa if mats.get(w.mat) else ""))).lower() for w in przegroda.warstwy)
    if any(s in txt for s in ZIELONY_SLOWA):
        return "zielony"
    if przegroda.typ == "taras" or "taras" in txt:
        return "taras"
    return "plaski"


def _yaml(p):
    import yaml
    if p is None:
        return None
    pp = Path(p)
    if not pp.exists():
        return None
    return yaml.safe_load(pp.read_text(encoding="utf-8"))


def dane_z_modelu(budynek, dzialka=None, wyposazenie=None, instalacje=None, strict: bool = False) -> DaneBudynku:
    """Wczytuje model i buduje :class:`DaneBudynku`.

    ``budynek`` — ścieżka ``budynek.yaml`` albo obiekt ``lamela.model.Model``; ``wyposazenie`` — ścieżka
    ``wyposazenie.yaml`` (domyślnie plik obok budynku, jeśli istnieje); ``instalacje`` — ścieżka ``instalacje.yaml``
    (proponowany plik modelu: lokalizacje RG/wodomierza/PC, przybory uzupełniające, trasy pionów, dane wyrobów)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    from lamela.model import Model, load_model, make_polygon

    zr = {}
    if isinstance(budynek, Model):
        m = budynek
        zr["budynek"] = getattr(m, "src_b", "Model")
    else:
        m = load_model(str(budynek), str(dzialka) if dzialka else None, strict=strict)
        zr["budynek"] = str(budynek)
        if dzialka:
            zr["dzialka"] = str(dzialka)
        if wyposazenie is None:
            cand = Path(budynek).with_name("wyposazenie.yaml")
            wyposazenie = cand if cand.exists() else None
    furn = []
    if wyposazenie:
        d = _yaml(wyposazenie)
        if isinstance(d, dict):
            d = d.get("wyposazenie") or d.get("elementy") or []
        furn = [x for x in (d or []) if isinstance(x, dict)]
        zr["wyposazenie"] = str(wyposazenie)
    inst = {}
    if instalacje:
        d = _yaml(instalacje) or {}
        inst = d.get("instalacje", d) if isinstance(d, dict) else {}
        zr["instalacje"] = str(instalacje)

    kond = [{"id": k.id, "rzedna": float(k.rzedna), "wys": float(k.wys_kondygnacji), "nazwa": k.nazwa}
            for k in m.kondygnacje]
    rz = {k["id"]: k["rzedna"] for k in kond}
    poms = []
    for r in m.pomieszczenia():
        if r.polygon is None or r.polygon.is_empty:
            continue
        c = r.polygon.representative_point() if not r.polygon.centroid.within(r.polygon) else r.polygon.centroid
        poms.append(Pom(id=r.id, nazwa=r.nazwa, kond=r.kond, pow=float(r.pow_netto), wys=float(r.wysokosc or 2.6),
                        temp=(float(r.temp) if r.temp is not None else None), kategoria=r.kategoria,
                        polygon=r.polygon, centroid=(float(c.x), float(c.y)), z=rz.get(r.kond, 0.0),
                        went=dict(r.went or {})))
    mats = m.materialy
    dachy = []
    for d in m.dachy():
        if not d.get("obrys"):
            continue
        P = make_polygon(d["obrys"])
        prz = m.przegroda(str(d.get("przegroda"))) if d.get("przegroda") else None
        pl = d.get("plyta") or {}
        wierzch = float(pl.get("wierzch", 0.0))
        d_nad = prz.d_nad_konstr() if prz is not None else 0.0
        at = d.get("attyka") or {}
        wp = []
        for w in d.get("wpusty") or []:
            if isinstance(w, dict):
                wp.append({"xy": tuple(w.get("xy", (0, 0))), "dn": w.get("dn"), "podgrzewany": w.get("podgrzewany")})
            else:
                wp.append({"xy": tuple(w), "dn": None, "podgrzewany": None})
        dachy.append(Dach(id=str(d.get("id")), obrys=P, pole=float(P.area), typ=_typ_dachu(prz, mats),
                          przegroda=str(d.get("przegroda")), przegroda_nazwa=(prz.nazwa if prz else ""),
                          rzedna=wierzch + d_nad, attyka_wys=(float(at["wys_nad_pokryciem"]) if at.get("wys_nad_pokryciem") is not None else None),
                          spadek=d.get("spadek"), wpusty=wp, przelewy=list(d.get("przelewy_awaryjne") or []),
                          rury_spustowe=list(d.get("rury_spustowe") or []), spadki=list(d.get("spadki") or []),
                          warstwy=[(w.mat, w.d, mats.get(w.mat).nazwa if mats.get(w.mat) else w.mat)
                                   for w in (prz.warstwy if prz else [])]))
    for w in m.wsporniki():
        if not w.get("obrys"):
            continue
        P = make_polygon(w["obrys"])
        prz = m.przegroda(str(w.get("przegroda"))) if w.get("przegroda") else None
        wierzch = float(w.get("wierzch", 0.0))
        dachy.append(Dach(id=str(w.get("id")), obrys=P, pole=float(P.area),
                          typ=("taras" if (prz is not None and prz.typ == "taras") else "wspornik"),
                          przegroda=str(w.get("przegroda")), przegroda_nazwa=(prz.nazwa if prz else ""),
                          rzedna=wierzch, attyka_wys=None, spadek=w.get("spadek"),
                          wpusty=[{"xy": tuple(x.get("xy")), "dn": x.get("dn"), "podgrzewany": x.get("podgrzewany")}
                                  if isinstance(x, dict) else {"xy": tuple(x), "dn": None, "podgrzewany": None}
                                  for x in (w.get("wpusty") or [])],
                          przelewy=list(w.get("przelewy_awaryjne") or []), rury_spustowe=list(w.get("rury_spustowe") or []),
                          warstwy=[(x.mat, x.d, mats.get(x.mat).nazwa if mats.get(x.mat) else x.mat)
                                   for x in (prz.warstwy if prz else [])]))
    obrysy = {k["id"]: m.obrys_kondygnacji(k["id"]) for k in kond}
    zab = unary_union([g for g in obrysy.values() if g is not None and not g.is_empty]) if obrysy else Polygon()
    tops = [dd.rzedna + (dd.attyka_wys or 0.0) for dd in dachy if dd.typ != "wspornik" and dd.typ != "taras"]
    H_max = max(tops) if tops else (kond[-1]["rzedna"] + kond[-1]["wys"] if kond else 3.0)

    dz = {"obrys": None, "teren": np.zeros((0, 3)), "sasiedzi_zabudowa": [], "droga": {}, "uzbrojenie": {},
          "retencja": {}, "odwodnienia": [], "bramy": [], "utwardzenia": [], "zielen": [], "raw": {}}
    if getattr(m, "dz", None) is not None and m.dz.raw:
        D = m.dz
        dz["raw"] = D.raw
        dz["obrys"] = D.obrys
        dz["teren"] = D.teren_punkty()
        pp = ((D.raw.get("teren") or {}).get("punkty_projektowane") or [])
        if pp:
            arr = np.asarray(pp, float)
            dz["teren_proj"] = np.column_stack([D.do_budynku(arr[:, :2]), arr[:, 2] - D.zero_abs])
        dz["sasiedzi_zabudowa"] = [D.poly_bud(s["zabudowa"]) for s in D.lista("sasiedzi") if s.get("zabudowa")]
        dr = D.raw.get("droga") or {}
        dz["droga"] = {k: D.poly_bud(v) for k, v in dr.items() if k in ("linie_rozgraniczajace", "jezdnia") and v}
        dz["uzbrojenie"] = D.raw.get("uzbrojenie") or {}
        dz["retencja"] = D.raw.get("retencja") or {}
        dz["odwodnienia"] = D.lista("odwodnienia")
        dz["bramy"] = [{**b, "xy_bud": tuple(D.do_budynku(b["xy"]))} for b in D.lista("bramy") if b.get("xy")]
        dz["utwardzenia"] = [{**u, "poly": D.poly_bud(u["obrys"])} for u in D.lista("utwardzenia") if u.get("obrys")]
        dz["zielen"] = [{**z, "poly": D.poly_bud(z["obrys"])} for z in D.lista("zielen") if z.get("obrys")]
        dz["transform"] = D
    raw = getattr(m, "raw", None) or {}
    nazwa = (raw.get("meta") or {}).get("nazwa") or zr.get("budynek", "budynek")
    try:
        zero_abs = float((raw.get("uklad") or {}).get("zero_abs", 0.0))
    except (TypeError, ValueError):
        zero_abs = 0.0
    dane = DaneBudynku(nazwa=str(nazwa), zrodla=zr, kondygnacje=kond, pomieszczenia=poms, dachy=dachy, obrysy=obrysy,
                       obrys_zabudowy=zab, H_max=float(H_max), kubatura=float(m.kubatura_brutto()["razem"]),
                       pow_zabudowy=float(m.pow_zabudowy()["budynek"]), wyposazenie=furn, inst=inst, dzialka=dz,
                       zero_abs=zero_abs, model=m)
    if not inst:
        dane.uwagi.append("Brak pliku instalacje.yaml — lokalizacje RG, wodomierza, jednostki PC i trasy pionów "
                          "przyjęto automatycznie (patrz założenia w raportach).")
    return dane


# ==================================================================================================
# Dane z modułów fizyki/energii (kontrakt) — obciążenie cieplne i wentylacja
# ==================================================================================================
_PHI_KEYS = ("phi_HL", "Phi_HL", "phi_hl", "fi_HL", "PhiHL", "Φ_HL", "phi", "Q_HL", "obciazenie", "Q")
_ID_KEYS = ("id", "pomieszczenie", "pom", "room", "id_pom")


def _get(o, keys):
    for k in keys:
        if isinstance(o, dict) and k in o:
            return o[k]
        if hasattr(o, k):
            return getattr(o, k)
    return None


def phi_hl_z(zrodlo) -> dict[str, float] | None:
    """Normalizuje projektowe obciążenie cieplne pomieszczeń do ``{id_pomieszczenia: Φ_HL [W]}`` (patrz docstring
    modułu). Zwraca None, gdy źródła brak."""
    if zrodlo is None:
        return None
    if isinstance(zrodlo, (str, Path)):
        p = Path(zrodlo)
        d = json.loads(p.read_text(encoding="utf-8")) if p.suffix == ".json" else _yaml(p)
        return phi_hl_z(d)
    if isinstance(zrodlo, dict):
        if all(isinstance(v, (int, float)) for v in zrodlo.values()):
            return {str(k): float(v) for k, v in zrodlo.items()}
        for k in ("pomieszczenia", "per_pomieszczenie", "obciazenie_cieplne", "phi_HL"):
            if k in zrodlo:
                return phi_hl_z(zrodlo[k])
        return None
    if hasattr(zrodlo, "per_pomieszczenie") and callable(zrodlo.per_pomieszczenie):
        return phi_hl_z(zrodlo.per_pomieszczenie())
    if hasattr(zrodlo, "pomieszczenia"):
        return phi_hl_z(zrodlo.pomieszczenia)
    if isinstance(zrodlo, (list, tuple)):
        out = {}
        for r in zrodlo:
            i, v = _get(r, _ID_KEYS), _get(r, _PHI_KEYS)
            if i is not None and v is not None:
                out[str(i)] = float(v)
        return out or None
    return None


def wentylacja_z(zrodlo, dane: DaneBudynku | None = None) -> dict:
    """Strumienie powietrza: ``{"suma_naw": m³/h, "suma_wyw": m³/h, "pom": {id: {"naw", "wyw"}}, "zrodlo": str}``.
    Źródło: wynik modułu wentylacji (słownik/obiekt z ``pomieszczenia``) albo pola ``went`` pomieszczeń modelu."""
    pom = {}
    src = "model (pola went pomieszczeń)"
    if zrodlo is not None:
        if isinstance(zrodlo, (int, float)):
            return {"suma_naw": float(zrodlo), "suma_wyw": float(zrodlo), "pom": {}, "zrodlo": "wartość zadana"}
        rows = zrodlo.get("pomieszczenia", zrodlo) if isinstance(zrodlo, dict) else getattr(zrodlo, "pomieszczenia", zrodlo)
        if isinstance(rows, dict):
            for k, v in rows.items():
                if isinstance(v, dict):
                    pom[str(k)] = {"naw": float(v.get("naw", 0) or 0), "wyw": float(v.get("wyw", 0) or 0)}
        elif isinstance(rows, (list, tuple)):
            for r in rows:
                i = _get(r, _ID_KEYS)
                if i is not None:
                    pom[str(i)] = {"naw": float(_get(r, ("naw", "V_naw", "nawiew")) or 0),
                                   "wyw": float(_get(r, ("wyw", "V_wyw", "wywiew")) or 0)}
        src = "moduł wentylacji"
    elif dane is not None:
        for p in dane.pomieszczenia:
            pom[p.id] = {"naw": float(p.went.get("naw", 0) or 0), "wyw": float(p.went.get("wyw", 0) or 0)}
    sn = sum(v["naw"] for v in pom.values())
    sw = sum(v["wyw"] for v in pom.values())
    return {"suma_naw": sn, "suma_wyw": sw, "pom": pom, "zrodlo": src}


# ==================================================================================================
# Geometria pomocnicza
# ==================================================================================================
def manhattan(a, b) -> float:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def interp_loglog(x: float, xs, ys) -> float:
    """Interpolacja log-log (ekstrapolacja liniowa w log-log poza zakresem)."""
    xs = np.asarray(xs, float)
    ys = np.asarray(ys, float)
    lx, ly = np.log(xs), np.log(ys)
    t = math.log(x)
    if t <= lx[0]:
        i = 0
    elif t >= lx[-1]:
        i = len(lx) - 2
    else:
        i = int(np.searchsorted(lx, t) - 1)
    k = (ly[i + 1] - ly[i]) / (lx[i + 1] - lx[i])
    return float(math.exp(ly[i] + k * (t - lx[i])))


def ceil_to(x: float, szereg) -> float | None:
    """Najmniejsza wartość z szeregu ≥ x (None, gdy brak)."""
    for s in sorted(szereg):
        if s >= x - 1e-9:
            return s
    return None
