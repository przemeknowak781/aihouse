"""Składanie arkuszy widoków: konfiguracja YAML, dobór formatu, tabliczka z danych modelu, legendy, uwagi, zapis
(DXF + PDF + PNG), kontrola jakości (``plot.qa``) i tom PDF.

Format pliku konfiguracji (np. ``model/arkusze.yaml``; wszystkie pola opcjonalne — brak pliku = zestaw domyślny):

```yaml
wspolne:                         # wartości domyślne dla wszystkich arkuszy
  pracownia: "PRACOWNIA PROJEKTOWA — nazwa do uzupełnienia"
  pracownia_adres: "adres pracowni do uzupełnienia"
  inwestor: "(do uzupełnienia)"
  obiekt: null                   # null → „Budynek mieszkalny jednorodzinny „<meta.nazwa>””
  lokalizacja: null              # null → z dzialka.yaml (nr działki, obręb, adres/gmina jeśli podane)
  kategoria: "I"
  stadium: "PB"                  # PB | PT | PW …
  branza: "ARCHITEKTURA (AR)"
  prefiks_nr: "PB-AR"            # numery arkuszy bez „nr”: <prefiks>-01, -02…
  data: "2026-09-25"             # null → meta.data modelu
  rewizja: "0"
  rewizje: [["0", "Wydanie", "2026-09-25"]]
  skala: 50                      # domyślna podziałka widoków (1:50)
  format: auto                   # auto = ekonomiczny (lamela.views.uklad: ISO 216, wydłużone i niestandardowe H×L)
                                 # | standardowy | klasyczny (dawny dobór) | A3 | A2 | A3x3 … | [H, L] | "780x594"
  wysokosci: [297, 420, 594, 841, 891]   # wysokości arkuszy niestandardowych [mm] (≤ 914 — rolka plotera 36″)
  modul_skladania: auto          # auto (koszt z oceną składania) | 190 (L = 210 + 190·n) | 0 (bez dopasowania)
  kara_niestandard: 0.03         # lekka preferencja formatów ISO przy remisie kosztu
  metryki: true                  # wypełnienie arkusza (metoda tools/metryki_arkuszy.py) w raport_widokow.json
  numeracja_pomieszczen: iso     # iso (parter = 1.xx, PN-B-01025/R4 pkt 3.9) | model (identyfikatory modelu)
  wysokosc_ciecia: 1.10          # płaszczyzna cięcia rzutów nad posadzką [m]
  glebokosc_widoku: 1.5          # zasięg „widoku w dół” na rzutach kondygnacji powyżej parteru [m]
  wymiary_wewnetrzne: true
  kolorystyka: true              # wypełnienia kolorami materiałów na elewacjach
  uwagi: []                      # dodatkowe uwagi na każdym arkuszu
przekroje:                       # definicje przekrojów (patrz lamela.views.section) — brak = automatyczne A-A, B-B
  - {id: A, x: 0.6, patrz: E}
  - {id: B, y: 4.0, patrz: N}
arkusze:                         # brak = komplet: rzuty wszystkich kondygnacji, rzut dachu, przekroje, 4 elewacje
  - {nr: PB-AR-01, tytul: "RZUT PARTERU", typ: rzut, kond: P0}
  - {nr: PB-AR-03, tytul: "RZUT DACHU", typ: dach}
  - {nr: PB-AR-04, typ: przekroj, przekroj: A}
  - {nr: PB-AR-06, typ: elewacja, strona: S, skala: 50, format: A2}
  - {nr: PB-AR-10, tytul: "ELEWACJE", widoki: [{typ: elewacja, strona: N}, {typ: elewacja, strona: S}]}
```
Każdy arkusz: ``nr``, ``tytul``, ``typ`` (rzut | dach | przekroj | elewacja) z parametrami (``kond`` / ``przekroj`` /
``strona``), ``skala``, ``format``, ``uwagi``, ``opcje`` (słownik przekazywany do generatora widoku) albo ``widoki``
(lista widoków na jednym arkuszu).

Format i rozmieszczenie (widoki, bloki kolumny opisowej, tabliczka w prawym dolnym rogu) dobiera wspólny silnik
``lamela.views.uklad`` (ekonomiczne ustawienie na arkuszach — opis parametrów tamże); w ``raport_widokow.json``
każdy arkusz ma: format, wymiary, pole, plan i ocenę składania do A4, wypełnienie oraz kandydatów doboru.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import json
from dataclasses import dataclass
from pathlib import Path

import yaml

from ..draft import fmt, hatch, plot, symbols as S
from ..draft.core import Viewport
from ..draft.sheet import Sheet, TitleBlock, notes_box, scale_bar, sheet_size, table
from ..draft.sheet import wrap as _wrap
from ..draft.sheet import draw_title_block
from ..draft.skladanie import ocena_skladania
from .common import ViewContext, load_furniture, slug
from .elevation import NAMES as EL_NAMES, draw_elevation
from .plan import draw_plan, draw_roof_plan
from .section import auto_sections, draw_section, normalize_section
from . import uklad as U

TB_W = 180.0
FORMATS = ["A3", "A2", "A3x3", "A1", "A3x4", "A2x3", "A0", "A1x3", "A2x4", "A0x2"]
KAT = {"podstawowa": "podst.", "pomocnicza": "pomoc.", "ruchu": "ruchu", "techniczna": "techn."}
ROMAN = ["", "I", "II", "III", "IV", "V", "VI"]

DEFAULTS = dict(
    pracownia="PRACOWNIA PROJEKTOWA — nazwa do uzupełnienia",
    pracownia_adres="adres pracowni do uzupełnienia",
    inwestor="(do uzupełnienia)",
    obiekt=None, lokalizacja=None, kategoria="I", stadium="PB", branza="ARCHITEKTURA (AR)", prefiks_nr="PB-AR",
    data=None, rewizja="0", rewizje=None, skala=50, format="auto", numeracja_pomieszczen="iso",
    wysokosc_ciecia=1.10, glebokosc_widoku=1.5, wymiary_wewnetrzne=True, kolorystyka=True, uwagi=[],
    dpi=150,
)


# ================================================================================================ konfiguracja
def storey_title(model, kid: str) -> str:
    from .common import storey_numbers
    k = model.kondygnacja(kid)
    nm = (k.nazwa or "").lower()
    n = storey_numbers(model).get(kid, 1)
    if "podda" in nm:
        return "RZUT PODDASZA"
    if "piwn" in nm or n < 0:
        return "RZUT PIWNICY"
    if n == 1:
        return "RZUT PARTERU"
    return f"RZUT {ROMAN[n - 1] if n - 1 < len(ROMAN) else n - 1} PIĘTRA"


def default_sheets(model, sections) -> list[dict]:
    out = []
    for k in model.kondygnacje:
        out.append(dict(typ="rzut", kond=k.id, tytul=storey_title(model, k.id)))
    out.append(dict(typ="dach", tytul="RZUT DACHU"))
    for s in sections:
        out.append(dict(typ="przekroj", przekroj=s["id"], tytul=s["nazwa"]))
    for side in ("S", "N", "E", "W"):
        out.append(dict(typ="elewacja", strona=side, tytul=EL_NAMES[side]))
    return out


def load_config(path, model) -> dict:
    """Konfiguracja arkuszy (plik YAML lub None) uzupełniona wartościami domyślnymi."""
    raw = {}
    if path and Path(path).exists():
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    wsp = dict(DEFAULTS)
    wsp.update(raw.get("wspolne") or {})
    meta = getattr(model, "meta", {}) or {}
    if not wsp.get("data"):
        wsp["data"] = str(meta.get("data") or _dt.date.today().isoformat())
    if not wsp.get("obiekt"):
        nm = meta.get("nazwa") or "Dom"
        wsp["obiekt"] = f"Budynek mieszkalny jednorodzinny „{nm}”"
    if not wsp.get("lokalizacja"):
        wsp["lokalizacja"] = location_text(model)
    if wsp.get("rewizje") is None:
        wsp["rewizje"] = [[str(wsp.get("rewizja", "0")), "Wydanie — rysunek wygenerowany z modelu", wsp["data"]]]
    secs_raw = raw.get("przekroje") or auto_sections(model)
    sections = [normalize_section(s, model) for s in secs_raw]
    sheets = raw.get("arkusze") or default_sheets(model, sections)
    pre = wsp.get("prefiks_nr", "PB-AR")
    for i, s in enumerate(sheets):
        s.setdefault("nr", f"{pre}-{i + 1:02d}")
    return dict(wspolne=wsp, przekroje=sections, arkusze=sheets, zrodlo=str(path) if path else None)


def location_text(model) -> str:
    dz = getattr(model, "dz", None)
    raw = (dz.raw if dz is not None else {}) or {}
    d = raw.get("dzialka") or {}
    parts = []
    if d.get("adres"):
        parts.append(str(d["adres"]))
    if d.get("nr"):
        parts.append(f"dz. nr ewid. {d['nr']}")
    if d.get("obreb"):
        parts.append(f"obręb {d['obreb']}")
    for kk in ("gmina", "jednostka", "jedn_ewid"):
        if d.get(kk):
            parts.append(("gm. " if kk == "gmina" else "jedn. ewid. ") + str(d[kk]))
    return ", ".join(parts) if parts else "(lokalizacja — do uzupełnienia w dzialka.yaml)"


# ================================================================================================ widoki
@dataclass
class ViewOut:
    spec: dict
    vp: Viewport
    kind: str
    result: object
    title: str
    w_mm: float = 0.0
    h_mm: float = 0.0


# ------------------------------------------------------------------------------------------------ rejestr typów
# Dodatkowe typy widoków (PZT, instalacje, konstrukcja, detale) rejestrują się w osobnych modułach pakietu
# ``lamela.views`` wywołaniem ``register_view`` — bez edycji ``make_view``/``build_sheet``. Funkcja widoku:
#   fn(ctx: ViewContext, spec: dict, scale: float, opts: dict) -> (Viewport, wynik, tytuł)
# Wynik może mieć atrybuty (wszystkie opcjonalne): ``notes`` (list[str] — uwagi na arkusz), ``column_blocks``
# (list[(nazwa, fn(sh, x, y_top, w) -> y_bottom)] — bloki kolumny opisowej, np. legenda symboli instalacji),
# ``north`` (bool — róża kierunków), ``hatch_mats`` (jak w rzutach), ``rooms`` (tabela pomieszczeń),
# ``units_note`` (str — zastępuje domyślną uwagę „Wymiary w cm…”, np. dla PZT „wymiary i odległości w m”),
# ``bez_skali`` (bool — schemat: tytuł widoku bez podziałki, skala w tabliczce „—”, bez podziałki liniowej).
# ``rodzaj`` — tekst pola „rodzaj rysunku” w tabliczce (np. „plan zagospodarowania”, „rzut instalacji”, „detal”).
# ``qa`` — rodzaj kontroli ``plot.qa`` (np. „PZT”: podziałki do 1:500, pismo ≥ 2,5 mm); None — ze stadium tabliczki.
# Widoki z listy ``widoki`` arkusza dziedziczą ``nr`` arkusza (``spec["nr"]``), jeśli go nie podano.
# Kontrakt bloków kolumny arkusza z kilkoma widokami: bloki wszystkich widoków trafiają do jednej kolumny w kolejności
# widoków. Bloki o tej samej nazwie i identycznej treści (np. ta sama legenda / tabela całego budynku z dwóch rzutów)
# są scalane — zostaje pierwszy. Blok może zależeć od stanu arkusza (np. legenda wspólna rysowana raz: kolejne
# wywołania na tym samym arkuszu nic nie rysują i zwracają ``y_top``) — silnik układu pomija bloki, które w pomiarze
# sekwencyjnym nic nie rysują, a bloki zmieniające wysokość względem pomiaru osobnego łączy z poprzednim
# (``uklad.bloki_z_kolumny``). Blok nie może zakładać, że stanie pod poprzednim blokiem listy.
VIEW_TYPES: dict = {}
VIEW_PLUGINS = ("site", "instalacje", "konstrukcja", "detale")   # moduły lamela.views ładowane przy nieznanym typie


def register_view(typ: str, fn, rodzaj: str = "rysunek", qa: str | None = None):
    VIEW_TYPES[typ] = dict(fn=fn, rodzaj=rodzaj, qa=qa)


def _load_plugins():
    import importlib
    for mod in VIEW_PLUGINS:
        try:
            importlib.import_module(f"{__package__}.{mod}")
        except ModuleNotFoundError as ex:
            if ex.name != f"{__package__}.{mod}":
                raise


def make_view(ctx: ViewContext, spec: dict, scale: float) -> ViewOut:
    typ = spec.get("typ")
    opts = dict(spec.get("opcje") or {})
    if typ not in ("rzut", "dach", "przekroj", "przekrój", "elewacja") and typ not in VIEW_TYPES:
        _load_plugins()
    if typ in VIEW_TYPES:
        vp, res, title = VIEW_TYPES[typ]["fn"](ctx, spec, scale, opts)
    elif typ == "rzut":
        kid = spec["kond"]
        title = spec.get("tytul_widoku") or spec.get("tytul") or storey_title(ctx.model, kid)
        vp = Viewport(scale, title)
        res = draw_plan(vp, ctx, kid, opts)
    elif typ == "dach":
        title = spec.get("tytul_widoku") or spec.get("tytul") or "RZUT DACHU"
        vp = Viewport(scale, title)
        res = draw_roof_plan(vp, ctx, opts)
    elif typ in ("przekroj", "przekrój"):
        sid = str(spec.get("przekroj", "A"))
        sec = ctx.sections.get(sid)
        if sec is None:
            raise KeyError(f"brak definicji przekroju '{sid}' (sekcja 'przekroje')")
        title = spec.get("tytul_widoku") or sec["nazwa"]
        vp = Viewport(scale, title)
        res = draw_section(vp, ctx, sec, opts)
        typ = "przekroj"
    elif typ == "elewacja":
        side = str(spec.get("strona", "S")).upper()
        title = spec.get("tytul_widoku") or EL_NAMES.get(side, f"ELEWACJA {side}")
        vp = Viewport(scale, title)
        res = draw_elevation(vp, ctx, side, opts)
    else:
        raise ValueError(f"nieznany typ widoku '{typ}' (rzut | dach | przekroj | elewacja | {' | '.join(VIEW_TYPES)})")
    e = vp.extents()
    pad = 3.0
    w = (e[2] - e[0]) / vp.k + 2 * pad
    h = (e[3] - e[1]) / vp.k + 2 * pad
    return ViewOut(spec, vp, typ, res, title, w, h)


# ================================================================================================ kolumna opisowa
class Column:
    """Bloki kolumny opisowej nad tabliczką (szer. 180 mm) — rysowane na arkuszu, z pomiarem wysokości."""

    def __init__(self):
        self.blocks = []   # (nazwa, fn(sh, x, y_top, w) -> y_bottom)

    def add(self, name, fn):
        self.blocks.append((name, fn))

    def draw(self, sh, x, y_top, w, gap=5.0):
        y = y_top
        for _n, fn in self.blocks:
            y = fn(sh, x, y, w) - gap
        return y

    def measure(self, w):
        sh = Sheet("A0", draw_frame=False)
        top = 800.0
        y = self.draw(sh, 20.0, top, w)
        return top - y


def _room_table(rows):
    def fn(sh, x, y, w):
        cols = [("Nr", 14.0), ("Nazwa pomieszczenia", 60.0), ("Posadzka", 46.0), ("Kat.", 18.0), ("Wys. [m]", 18.0),
                ("Pow. [m²]", 22.0)]
        f = min(1.0, w / 178.0)                  # blok węższy niż 178 mm (silnik: 177 mm) — kolumny proporcjonalnie
        cols = [(n_, c_ * f) for n_, c_ in cols]
        data = []
        tot = pu = 0.0
        for r in rows:
            data.append([r["nr"], r["nazwa"], r["posadzka"], KAT.get(r["kategoria"], r["kategoria"]),
                         fmt.num(r["wys"], 2) if r.get("wys") else "", fmt.area(r["pow"], unit=False)])
            tot += r["pow"]
            if r["kategoria"] in ("podstawowa", "pomocnicza"):
                pu += r["pow"]
        data.append(["", "RAZEM powierzchnia netto", "", "", "", fmt.area(tot, unit=False)])
        data.append(["", "w tym podstawowa + pomocnicza", "", "", "", fmt.area(pu, unit=False)])
        r = table(sh, x, y - 7.0, cols, data, h=2.5, row_h=5.0, title="ZESTAWIENIE POMIESZCZEŃ",
                  align=["center", "left", "left", "center", "right", "right"], zawijaj=True)
        return r[1]
    return fn


def legend_entries(model, hatch_mats: dict) -> list:
    """Pozycje legendy kreskowań: (kod wzoru, „nazwy materiałów modelu — opis wzoru”)."""
    from .common import material_name
    out = []
    for hc in sorted(hatch_mats):
        pat = hatch.PATTERNS.get(hc)
        if pat is None:
            continue
        desc = pat.name.split(" — ", 1)[1] if " — " in pat.name else ""
        names = []
        for mc in hatch_mats[hc]:
            nm = "grunt rodzimy" if mc == "GRUNT" else material_name(model, mc)
            if nm not in names:
                names.append(nm)
        lab = "; ".join(names[:4]) + ("…" if len(names) > 4 else "")
        if desc:
            lab += f" — {desc}"
        out.append((hc, lab))
    return out


def _hatch_legend(codes):
    def fn(sh, x, y, w):
        if not codes:
            return y
        r = hatch.legend(sh, x, y, codes, cols=2, col_w=w / 2.0, sw=(10.0, 5.0), h=1.8,
                         title="OZNACZENIA MATERIAŁÓW (PN-B-01030 + przyjęte)", show_source=False, row_gap=1.4)
        return r[1]
    return fn


def _lines_legend(entries):
    def fn(sh, x, y, w):
        with sh.on("R-LEGENDA"):
            sh.text((x, y - 3.5), "OZNACZENIA LINII", 3.5, style="bold")
            yy = y - 9.0
            for lt, pen, txt in entries:
                sh.line((x + 1, yy + 0.9), (x + 13, yy + 0.9), "R-LEGENDA", pen=pen, lt=lt)
                ls = _wrap(txt, w - 18.0, 1.8)
                for j, s in enumerate(ls):
                    sh.text((x + 16, yy - j * 2.7), s, 1.8)
                yy -= 2.7 * len(ls) + 1.8
        return yy + 1.0
    return fn


def _material_legend(rows, model):
    def fn(sh, x, y, w):
        if not rows:
            return y
        with sh.on("R-LEGENDA"):
            sh.text((x, y - 3.5), "KOLORYSTYKA I MATERIAŁY ELEWACJI", 3.5, style="bold")
            yy = y - 9.5
            for nr, code, name, col, area in rows:
                S.tag(sh, (x + 3.2, yy + 1.0), str(nr), shape="hex", r_mm=2.6, h=2.5, layer="R-LEGENDA")
                sh.fill([(x + 8, yy - 1.2), (x + 20, yy - 1.2), (x + 20, yy + 3.2), (x + 8, yy + 3.2)], "R-LEGENDA",
                        col, z=6)
                sh.rect(x + 8, yy - 1.2, x + 20, yy + 3.2, layer="R-LEGENDA", pen=0.18)
                txt = f"{name} [{code}]"
                ls = _wrap(txt, w - 50.0, 1.8)
                for j, s in enumerate(ls):
                    sh.text((x + 23, yy + 1.8 - j * 2.6), s, 1.8)
                sh.text((x + w - 2, yy + 1.8), f"{col}", 1.8, ha="right", color="#505050")
                yy -= max(6.0, 2.6 * len(ls) + 2.0)
        return yy + 2.0
    return fn


def _notes(lines):
    def fn(sh, x, y, w):
        r = notes_box(sh, x, y, w, lines, "OBJAŚNIENIA I UWAGI", h=1.8)
        return r[1]
    return fn


def _north(model):
    def fn(sh, x, y, w):
        S.north_arrow(sh, (x + w - 12.0, y - 15.0), 14.0, float(getattr(model, "azymut_osi_y", 0.0) or 0.0))
        return y - 30.0
    return fn


def _scalebar(scale, h: float = 1.8):
    def fn(sh, x, y, w):
        # skale spoza słownika (detale 1:5, 1:10 …) — długość dobiera scale_bar (≤ 125 mm na papierze)
        L = {20: 2.0, 25: 2.0, 50: 5.0, 100: 10.0, 200: 20.0, 250: 25.0, 500: 50.0}.get(int(scale))
        r = scale_bar(sh, (x + 4.0, y - 8.0 - (h - 1.8)), scale, L, h=h)
        return r[1] - 5.0
    return fn


def common_notes(ctx: ViewContext, kinds: set, extra=(), units: str | None = None) -> list[str]:
    m = ctx.model
    w = ctx.cfg
    # ``units`` — własna uwaga o jednostkach z widoku rejestrowanego (np. PZT: wymiary w m z dokł. 0,01 m)
    out = [units or (f"Wymiary w cm (mm w indeksie górnym, np. 24⁵ = 24,5 cm), rzędne w m względem ±0,000 = "
                     f"{fmt.level_abs(m.zero_abs)} m n.p.m. (PL-EVRF2007-NH).")]
    if "rzut" in kinds:
        out.append(f"Rzuty: płaszczyzna cięcia +{fmt.num(float(w.get('wysokosc_ciecia', 1.1)), 2)} m nad posadzką "
                   "kondygnacji. Linią kreskową — elementy nad płaszczyzną cięcia (obrysy płyt i wsporników, brył "
                   "wyższych kondygnacji, otwory w stropie nad, belki); linią cienką — elementy poniżej (widok).")
        out.append("Otwory: licznik — szerokość, mianownik — wysokość w świetle muru, w nawiasie wysokość parapetu; "
                   "symbol stolarki wg zestawienia stolarki.")
        if w.get("numeracja_pomieszczen", "iso") == "iso":
            out.append("Numeracja pomieszczeń wg PN-B-01025 / PN-EN ISO 4157-2: <nr kondygnacji (parter = 1)>.<nr>; "
                       "identyfikator w modelu: <kond>.<nr> (parter = 0).")
        out.append("Drzwi: strona otwierania (lewe/prawe) wg modelu — patrząc od strony, w którą otwiera się skrzydło.")
    if "przekroj" in kinds or "elewacja" in kinds:
        out.append("Rzędne: trójkąt zaczerniony — poziom wykończenia, niezaczerniony — konstrukcji, w połowie "
                   "zaczerniony — poziom ±0,000 z rzędną bezwzględną (PN-B-01025).")
        H = None
        try:
            from .section import building_height
            H = building_height(ctx)
        except Exception:
            pass
        if H:
            out.append(f"Wysokość budynku wg § 6 WT: od terenu przy najniżej położonym wejściu "
                       f"({fmt.level(H['z_ent'])}) do wierzchu stropodachu {H['dach']} ({fmt.level(H['z_top'])}) "
                       f"— H = {fmt.num(H['H'], 2)} m (bez attyk).")
    if "przekroj" in kinds:
        out.append("Opisy warstw: kod i nazwa przegrody z modelu, materiały i grubości wg modelu (od góry / od lewej).")
    if "elewacja" in kinds:
        out.append("Kolorystyka orientacyjna wg kolorów materiałów w modelu (do potwierdzenia wzornikiem RAL/NCS).")
    out += list(w.get("uwagi") or [])
    out += list(extra)
    src = ctx.src or "model/budynek.yaml"
    try:                                  # ścieżka względna repozytorium (bez ścieżek lokalnych na arkuszu)
        src = str(Path(src).resolve().relative_to(Path(__file__).resolve().parents[3]))
    except ValueError:
        src = Path(src).name
    meta = getattr(m, "meta", {}) or {}
    out.append(f"Rysunek wygenerowany automatycznie z modelu {src} (wersja {meta.get('wersja', '?')}, "
               f"{meta.get('data', '?')}) — generatory lamela.views.")
    return out


# ================================================================================================ arkusz
def _title_block(ctx: ViewContext, spec: dict, idx: int, total: int, scale_txt: str, rodzaj: str) -> TitleBlock:
    w = dict(ctx.cfg)
    w.update(spec.get("tabliczka") or {})
    return TitleBlock(pracownia=w["pracownia"], pracownia_adres=w.get("pracownia_adres", ""), inwestor=w["inwestor"],
                      obiekt=w["obiekt"], lokalizacja=w["lokalizacja"], kategoria=str(w.get("kategoria", "")),
                      stadium=str(w.get("stadium", "")), branza=str(w.get("branza", "")),
                      tytul=spec.get("tytul", ""), skala=scale_txt, nr_rysunku=spec["nr"], data=str(w["data"]),
                      rewizja=str(w.get("rewizja", "0")), arkusz=f"{idx}/{total}", rodzaj=rodzaj,
                      rewizje=[tuple(map(str, r)) for r in (w.get("rewizje") or [])],
                      sprawdzenie=bool(w.get("sprawdzenie", True)))


def _arrange(views, gap=12.0, title_h=12.0, avail_w=1e9):
    """Układ widoków: w wierszu, gdy się mieszczą, inaczej w kolumnie. Zwraca (szer., wys., pozycje)."""
    ws = [v.w_mm for v in views]
    hs = [v.h_mm + title_h for v in views]
    row_w = sum(ws) + gap * (len(views) - 1)
    if len(views) == 1 or row_w <= avail_w:
        return row_w, max(hs), "row"
    return max(ws), sum(hs) + gap * (len(views) - 1), "col"


def _przygotuj(ctx: ViewContext, spec: dict) -> dict:
    """Widoki i bloki kolumny opisowej arkusza (wspólne dla układu klasycznego i silnika ``uklad``)."""
    m = ctx.model
    scale = float(spec.get("skala", ctx.cfg.get("skala", 50)))
    vspecs = [dict(vs) for vs in (spec.get("widoki") or [spec])]
    for vs in vspecs:                   # widoki z listy znają numer arkusza (braki danych, uwagi generatorów)
        if spec.get("nr") is not None:
            vs.setdefault("nr", spec["nr"])
    shared_nr = {}                      # wspólna numeracja materiałów elewacji na arkuszu
    for vs in vspecs:
        if vs.get("typ") == "elewacja":
            vs["opcje"] = dict(vs.get("opcje") or {}, _mat_nr=shared_nr)
    views = [make_view(ctx, dict(vs, **({"skala": scale} if "skala" not in vs else {})),
                       float(vs.get("skala", scale))) for vs in vspecs]
    kinds = {v.kind for v in views}
    col = Column()
    if kinds & {"rzut", "dach"} or any(getattr(v.result, "north", False) for v in views):
        col.add("north", _north(m))
    rooms = [r for v in views if v.kind == "rzut" or (v.kind in VIEW_TYPES and getattr(v.result, "rooms", None))
             for r in (v.result.rooms or [])]
    if rooms:
        col.add("rooms", _room_table(rooms))
    hm = {}
    for v in views:
        if v.kind in ("rzut", "przekroj") or v.kind in VIEW_TYPES:
            for hc, mats in (getattr(v.result, "hatch_mats", None) or {}).items():
                hm.setdefault(hc, [])
                for mc in mats:
                    if mc not in hm[hc]:
                        hm[hc].append(mc)
    codes = legend_entries(m, hm)
    if codes:
        col.add("hatch", _hatch_legend(codes))
    if kinds & {"rzut", "dach"}:
        col.add("lines", _lines_legend([
            ("KRESKOWA", 0.35, "elementy nad płaszczyzną cięcia (obrysy płyt, wsporników, brył wyższych kondygnacji)"),
            (None, 0.25, "elementy poniżej płaszczyzny cięcia (widok z góry)"),
            ("PUNKTOWA", 0.25, "osie konstrukcyjne; linia punktowa z pogrubionymi końcami — ślad przekroju")]))
    el_rows = []
    for v in views:
        if v.kind == "elewacja":
            for r in v.result.materials:
                if r[1] not in [x[1] for x in el_rows]:
                    el_rows.append(r)
    if el_rows:
        el_rows = sorted(el_rows, key=lambda r: r[0])
        col.add("mats", _material_legend(el_rows, m))
    for nm, fn in _scal_bloki([b for v in views for b in (getattr(v.result, "column_blocks", None) or [])]):
        col.add(nm, fn)
    extra = list(spec.get("uwagi") or [])
    for v in views:
        extra += [n for n in (getattr(v.result, "notes", None) or []) if n not in extra]
    units = next((getattr(v.result, "units_note", None) for v in views if getattr(v.result, "units_note", None)), None)
    notes = common_notes(ctx, kinds, extra, units=units)
    col.add("notes", _notes(notes))
    skalowane = [v for v in views if not getattr(v.result, "bez_skali", False)]   # schematy: bez podziałki
    if skalowane:
        col.add("scale", _scalebar(skalowane[0].vp.scale))
    rodzaj = {"rzut": "rzut", "dach": "rzut", "przekroj": "przekrój", "elewacja": "elewacja",
              **{k: v["rodzaj"] for k, v in VIEW_TYPES.items()}}[views[0].kind]
    scales = sorted({int(v.vp.scale) for v in skalowane})
    scale_txt = ("1:" + " / 1:".join(str(s) for s in scales)) if scales else "—"
    return dict(views=views, kinds=kinds, col=col, notes=notes, skalowane=skalowane, rodzaj=rodzaj,
                scale_txt=scale_txt)


def _podpis_bloku(fn, w: float = TB_W) -> tuple:
    """Treść bloku narysowanego na arkuszu próbnym (do porównania bloków o tej samej nazwie)."""
    import numpy as np
    sh = Sheet("A0", draw_frame=False)
    yb = fn(sh, 100.0, 5000.0, w)
    out = [round(float(yb), 2)]
    for p in sh.prims:
        g = getattr(p, "pts", None)
        if g is None:
            g = getattr(p, "pos", None)
        if g is None and getattr(p, "rings", None) is not None:
            g = p.rings[0]
        pts = tuple(np.round(np.asarray(g, float).ravel(), 2).tolist()) if g is not None else ()
        out.append((type(p).__name__, p.layer, pts, getattr(p, "string", None) if hasattr(p, "runs") else None,
                    getattr(p, "h", None), getattr(p, "fill", None), getattr(p, "pen", None)))
    return tuple(out)


def _scal_bloki(pary) -> list:
    """Bloki kolumny kilku widoków: blok o tej samej nazwie i identycznej treści co wcześniejszy — pomijany."""
    out, podpisy = [], {}
    nazwy = [nm for nm, _f in pary]
    for nm, fn in pary:
        if nazwy.count(nm) > 1:
            try:
                pp = _podpis_bloku(fn)
            except Exception:                      # noqa: BLE001 — blok niedający się narysować osobno: zostaje
                pp = None
            if pp is not None and pp in podpisy.setdefault(nm, []):
                continue
            if pp is not None:
                podpisy[nm].append(pp)
        out.append((nm, fn))
    return out


def _info(spec, views, fmt_name, scale_txt, W, H, tb_h):
    info = dict(nr=spec["nr"], tytul=spec.get("tytul"), format=fmt_name, typ=[v.kind for v in views],
                skala=scale_txt, widoki=[v.title for v in views],
                qa_kind=next((VIEW_TYPES[v.kind].get("qa") for v in views if v.kind in VIEW_TYPES), None),
                wymiary_mm=[round(W, 1), round(H, 1)], pole_m2=round(W * H / 1e6, 4),
                skladanie=ocena_skladania(W, H, tb_h))
    for v in views:
        if v.kind == "przekroj" or v.kind == "elewacja":
            info["wysokosc_budynku"] = getattr(v.result, "height", None)
    return info


def _place_views(sh, views, positions, tytuly_dx=None):
    """Rzutnie w pozycjach silnika układu; ``tytuly_dx`` — odsunięcie tytułu od lewej krawędzi rzutni (domyślnie
    2 mm; silnik przesuwa tytuł, który trafiłby na znak centrujący)."""
    for i, (v, (x, y)) in enumerate(zip(views, positions)):
        above = v.kind == "przekroj"
        sh.viewports.append(v.vp)
        sh.place(v.vp, x, y, "bl", pad=3.0)
        dx = float(tytuly_dx[i]) if tytuly_dx and i < len(tytuly_dx) else 2.0
        sh.view_title(v.vp, v.title, where="above" if above else "below", dx=dx,
                      scale=not getattr(v.result, "bez_skali", False))


def _tb_h(tb: TitleBlock) -> float:
    """Wysokość tabliczki z tabelą zmian [mm] (pomiar na arkuszu próbnym)."""
    probe = Sheet("A0", draw_frame=False)
    r = draw_title_block(probe, dataclasses.replace(tb, format=tb.format or "A0"))
    return float(r[3] - r[1])


def _arkusz_klasyczny(ctx, spec, idx, total, P, fmt_req: str):
    """Układ klasyczny (dotychczasowy): pierwszy mieszczący się format z FORMATS, kolumna opisowa 180 mm na całą
    wysokość nad tabliczką, widoki w wierszu lub kolumnie. Także zapas, gdy silnik ``uklad`` nic nie zmieści."""
    views, col = P["views"], P["col"]
    col_h = col.measure(TB_W)
    cands = FORMATS if fmt_req.lower() in ("auto", "klasyczny") else [fmt_req]
    chosen = None
    for f in sorted(cands, key=lambda f: sheet_size(f)[0] * sheet_size(f)[1]):
        W, Hh = sheet_size(f)
        tb_top = _tb_height(ctx, spec)
        fx0, fy0, fx1, fy1 = 20.0, 10.0, W - 10.0, Hh - 10.0
        avail_w = (fx1 - TB_W - 8.0) - (fx0 + 6.0)
        avail_h = (fy1 - fy0) - 12.0
        vw, vh, mode = _arrange(views, avail_w=avail_w)
        col_ok = col_h <= (fy1 - fy0 - tb_top) - 6.0
        if vw <= avail_w and vh <= avail_h and col_ok:
            chosen = (f, mode)
            break
    if chosen is None:
        f = cands[-1] if fmt_req.lower() not in ("auto", "klasyczny") else FORMATS[-1]
        W, Hh = sheet_size(f)
        vw, vh, mode = _arrange(views, avail_w=(W - 10.0 - TB_W - 8.0) - 26.0)
        chosen = (f, mode)
        ctx.note(f"arkusz {spec['nr']}", f"widok nie mieści się w formacie {f} — przycięty")
    f, mode = chosen
    tb = _title_block(ctx, spec, idx, total, P["scale_txt"], P["rodzaj"])
    sh = Sheet(f, title_block=tb)
    fx0, fy0, fx1, fy1 = sh.frame
    area = (fx0 + 6.0, fy0 + 6.0, fx1 - TB_W - 8.0, fy1 - 4.0)
    vw, vh, mode = _arrange(views, avail_w=area[2] - area[0])
    cx = (area[0] + area[2]) / 2.0
    cy = (area[1] + area[3]) / 2.0
    if mode == "row":
        x = cx - vw / 2.0
        for v in views:
            above = v.kind == "przekroj"
            y_c = cy + (-6.0 if above else 6.0)
            sh.viewports.append(v.vp)
            sh.place(v.vp, x + v.w_mm / 2.0, y_c, "mc", pad=3.0)
            sh.view_title(v.vp, v.title, where="above" if above else "below", dx=2.0,
                          scale=not getattr(v.result, "bez_skali", False))
            x += v.w_mm + 12.0
    else:
        y = cy + vh / 2.0
        for v in views:
            above = v.kind == "przekroj"
            top = y - (12.0 if above else 0.0)
            sh.viewports.append(v.vp)
            sh.place(v.vp, cx, top, "tc", pad=3.0)
            sh.view_title(v.vp, v.title, where="above" if above else "below", dx=2.0,
                          scale=not getattr(v.result, "bez_skali", False))
            y -= v.h_mm + 12.0 + 12.0
    col.draw(sh, fx1 - TB_W, fy1 - 3.0, TB_W)
    plot.add_control_marks(sh)
    znaki = sh.przytnij_znaki_centrujace()
    tbr = sh.tb_rect or (0, 0, 0, 0)
    info = _info(spec, views, f, P["scale_txt"], sh.width, sh.height, tbr[3] - tbr[1])
    info["uklad"] = dict(tryb="klasyczny", format=f, znaki_centrujace=znaki)
    return sh, info


def _bloki_ukladu(ctx, P) -> list:
    """Bloki kolumny opisowej dla silnika ``uklad``: róża kierunków + podziałka w jednym wierszu nad tabliczką,
    uwagi dzielone na kolumny, pozostałe bloki w kolejności kolumny."""
    col, m = P["col"], ctx.model
    names = [n for n, _f in col.blocks]
    hp = max(1.8, float(U.opcje(ctx.cfg).get("pismo_min", 1.8)))
    sc = P["skalowane"][0].vp.scale if P["skalowane"] else None
    out = []
    if "north" in names or sc:
        nfn = _north(m) if "north" in names else None
        sfn = _scalebar(sc, hp) if sc else None

        def ns(sh, x, y, w, nfn=nfn, sfn=sfn):
            yb = y
            if sfn is not None:
                yb = min(yb, sfn(sh, x, y - (8.0 if nfn is not None else 0.0), w))
            if nfn is not None:
                yb = min(yb, nfn(sh, x, y, w))
            return yb
        # w_min: wiersz może być węższy (róża przesuwa się w lewo — np. gdy prawy znak centrujący H/2 wypada
        # nad tabliczką, arkusze H = 297); podziałka ≤ 125 mm + róża 14 mm
        out.append(U.blok("róża i podziałka" if nfn and sfn else ("róża" if nfn else "podziałka"), ns, U.B_W,
                          kotwica="nad_tabliczka", w_min=155.0 if sfn else 30.0))
    pary = [(nm, fn) for nm, fn in col.blocks if nm not in ("north", "scale", "notes")]
    nm_ = [nm for nm, _f in pary]
    if "hatch" in nm_ and "lines" in nm_:          # legendy kreskowań i linii — jeden blok (weryfikacja C 2.11:
        fh, fl = dict(pary)["hatch"], dict(pary)["lines"]   # legenda linii nie może odrywać się od pozostałych)

        def legendy(sh, x, y, w, fh=fh, fl=fl):
            return fl(sh, x, fh(sh, x, y, w) - 5.0, w)
        pary = [(("hatch + lines", legendy) if nm == "hatch" else (nm, fn)) for nm, fn in pary if nm != "lines"]
    # szerokość bloków U.B_W = 177 mm: lewa krawędź jak tabliczka, 3 mm od prawej ramki (weryfikacja C 2.10)
    out += U.bloki_z_kolumny(pary, U.B_W)     # pomiar sekwencyjny: bloki zależne od poprzednich — razem
    if any(nm == "notes" for nm, _f in col.blocks):
        b = U.Blok("uwagi", None, U.B_W)
        # pismo uwag: ``pismo_min`` (domyślnie 1,8 mm; PZT — 2,5 mm, W-312)
        b.uwagi = U.BlokUwag(P["notes"], "OBJAŚNIENIA I UWAGI", h=hp, w=U.B_W)
        out.append(b)
    return out


def _arkusz_uklad(ctx, spec, idx, total, P, fmt_req):
    """Układ ekonomiczny (``lamela.views.uklad``): dobór formatu (także niestandardowego) i upakowanie. Zwraca None,
    gdy treść nie mieści się w żadnym kandydacie (wtedy układ klasyczny)."""
    views = P["views"]
    o = U.opcje(ctx.cfg, spec)
    tb = _title_block(ctx, spec, idx, total, P["scale_txt"], P["rodzaj"])
    tb_h = _tb_h(tb)
    kiesz = bool(o.get("wolne_obszary", True))
    widoki = [U.widok_z_rzutni(f"{i + 1}. {v.title}", v.vp, v.w_mm, v.h_mm, v.title,
                               skala=not getattr(v.result, "bez_skali", False), podtytul=bool(v.vp.subtitle),
                               nad=v.kind == "przekroj", kieszenie=kiesz) for i, v in enumerate(views)]
    bloki = _bloki_ukladu(ctx, P)
    lay = U.rozmiesc(widoki, bloki, tb_h, o, fmt=fmt_req)
    if lay is None:
        return None
    bledy = U.sprawdz_nakladanie(lay.roz)
    sh = Sheet(lay.sheet_fmt, orientation=lay.orientacja, title_block=tb)
    _place_views(sh, views, lay.roz.widoki, lay.roz.tytuly_dx)
    for b, x, y_top, w in lay.roz.bloki:
        b.fn(sh, x, y_top, w)
    plot.add_control_marks(sh)
    znaki = sh.przytnij_znaki_centrujace()     # znak nie może dotykać treści (widoki nie są od znaków odsuwane)
    bledy += U.kolizje_znakow(sh)
    tbr = sh.tb_rect or lay.roz.tabliczka
    if abs((tbr[3] - tbr[1]) - tb_h) > 0.5:
        bledy.append(f"wysokość tabliczki {tbr[3] - tbr[1]:.1f} ≠ pomiar {tb_h:.1f} mm")
    info = _info(spec, views, lay.nazwa, P["scale_txt"], lay.W, lay.H, tb_h)
    info["uklad"] = dict(lay.info(), bloki=[[n, [round(v, 1) for v in r]] for k, n, r in lay.roz.prostokaty
                                           if k in ("blok", "tabliczka")], kolizje=bledy, znaki_centrujace=znaki)
    if bledy:
        ctx.note(f"arkusz {spec['nr']}", "układ: " + "; ".join(bledy[:3]))
    return sh, info


def build_sheet(ctx: ViewContext, spec: dict, idx: int, total: int):
    """Tworzy arkusz wg ``spec``. Zwraca (Sheet, info). Format i rozmieszczenie: ``lamela.views.uklad`` (tryb
    ekonomiczny — domyślny dla ``format: auto``) albo układ klasyczny (``format: klasyczny``)."""
    P = _przygotuj(ctx, spec)
    fmt_req = spec.get("format", ctx.cfg.get("format", "auto"))
    tryb, _j = U.tryb_formatu(fmt_req)
    if tryb != "klasyczny":
        r = _arkusz_uklad(ctx, spec, idx, total, P, fmt_req)
        if r is not None:
            return r
        ctx.note(f"arkusz {spec['nr']}", f"układ ekonomiczny: treść nie mieści się w formacie {fmt_req} — "
                                         "układ klasyczny")
    return _arkusz_klasyczny(ctx, spec, idx, total, P, _j[0] if tryb == "jawny" else "auto")


def _tb_height(ctx, spec) -> float:
    n_rev = len(ctx.cfg.get("rewizje") or [])
    return 103.0 - 5.0 * 2 + (5.0 * (n_rev + 1) if n_rev else 0.0) + 2.0


# ================================================================================================ generowanie
def make_context(model, ir, cfg: dict, furniture=None, src: str = "") -> ViewContext:
    ctx = ViewContext(model, ir, cfg["wspolne"], furniture or [], {s["id"]: s for s in cfg["przekroje"]}, src)
    return ctx


def generate(budynek, dzialka=None, arkusze=None, wyposazenie=None, out_dir="build/widoki",
             formats=("dxf", "pdf", "png"), dpi: int | None = None, only=None, tom: bool = True,
             log=print) -> dict:
    """Generuje komplet arkuszy z modelu do ``out_dir``. Zwraca raport (także zapisany jako ``raport_widokow.json``)."""
    import time
    from ..ir import build_ir
    from ..model import load_model
    t0 = time.time()
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    m = load_model(budynek, dzialka, strict=False)
    if m.bledy:
        log(f"UWAGA: model ma {len(m.bledy)} błędów walidacji — widoki mogą być niepełne")
    ir = build_ir(m, otoczenie=True, auta=False)
    cfg = load_config(arkusze, m)
    if wyposazenie is None:
        cand = Path(budynek).with_name("wyposazenie.yaml")
        wyposazenie = cand if cand.exists() else None
    furn = load_furniture(wyposazenie) if wyposazenie else []
    ctx = make_context(m, ir, cfg, furn, src=str(budynek))
    dpi = int(dpi or cfg["wspolne"].get("dpi", 150))
    report = dict(model=str(budynek), dzialka=str(dzialka) if dzialka else None, arkusze_cfg=cfg["zrodlo"],
                  wyposazenie=str(wyposazenie) if wyposazenie else None, walidacja=m.raport_walidacji(),
                  przekroje={k: dict(o=[round(float(x), 3) for x in v["o"]], patrz=[round(float(x), 3) for x in v["L"]])
                             for k, v in ctx.sections.items()},
                  arkusze=[], problemy=[])
    sheets = []
    specs = cfg["arkusze"]
    total = len(specs)
    for i, spec in enumerate(specs):
        if only and spec["nr"] not in only:
            continue
        t1 = time.time()
        try:
            sh, info = build_sheet(ctx, spec, i + 1, total)
        except Exception as ex:
            import traceback
            report["arkusze"].append(dict(nr=spec.get("nr"), blad=f"{type(ex).__name__}: {ex}",
                                          slad=traceback.format_exc()[-2000:]))
            log(f"  {spec.get('nr')}: BŁĄD {ex}")
            continue
        base = out / f"{spec['nr']}_{slug(spec.get('tytul') or info['widoki'][0])}"
        files = sh.save(base, formats=formats, dpi=dpi)
        qa = plot.qa(sh, kind=info.get("qa_kind"))
        info.update(pliki=files, qa=qa, czas_s=round(time.time() - t1, 1))
        if "png" in files:
            info["png_kontrola"] = plot.check_png(files["png"], sh, min_dpi=min(150, dpi))
        if "pdf" in files and cfg["wspolne"].get("metryki", True):
            try:                            # wypełnienie arkusza — ta sama metoda co tools/metryki_arkuszy.py
                info["wypelnienie"] = U.wypelnienie_pdf(files["pdf"])
            except Exception as ex:        # noqa: BLE001 — pomiar pomocniczy, nie blokuje generowania
                ctx.note(f"arkusz {spec['nr']}", f"pomiar wypełnienia: {type(ex).__name__}: {ex}")
        report["arkusze"].append(info)
        sheets.append(sh)
        wyp = (info.get("wypelnienie") or {}).get("wypelnienie")
        log(f"  {spec['nr']} {info['tytul']}: {info['format']} ({info['wymiary_mm'][0]:.0f}×{info['wymiary_mm'][1]:.0f}) "
            f"{info['skala']}" + (f", wypełnienie {wyp * 100:.0f} %" if wyp is not None else "")
            + f", składanie {info['skladanie']['ocena']}  QA: "
            f"{'OK' if qa['ok'] else 'BŁĘDY ' + str(len(qa['errors']))}, ostrz. {len(qa['warnings'])}  "
            f"({info['czas_s']} s)")
    if tom and sheets and "pdf" in formats:
        w = cfg["wspolne"]
        toc_tb = TitleBlock(pracownia=w["pracownia"], inwestor=w["inwestor"], obiekt=w["obiekt"],
                            lokalizacja=w["lokalizacja"], kategoria=str(w.get("kategoria", "")),
                            stadium=str(w.get("stadium", "")), branza=str(w.get("branza", "")),
                            tytul="SPIS RYSUNKÓW", skala="—", nr_rysunku=f"{w.get('prefiks_nr', 'PB-AR')}-00",
                            data=str(w["data"]), rodzaj="spis", arkusz="—")
        tp = out / str(w.get("plik_tomu", "tom_widoki.pdf"))
        plot.volume(sheets, tp, str(w.get("tytul_tomu") or "Tom rysunków — widoki z modelu"), toc=True,
                    toc_tb=toc_tb)
        report["tom"] = str(tp)
    ok_ark = [a for a in report["arkusze"] if "blad" not in a and a.get("pole_m2")]
    if ok_ark:                              # zużycie papieru na egzemplarz (ekonomia arkuszy)
        pole = sum(a["pole_m2"] for a in ok_ark)
        wz = [a for a in ok_ark if (a.get("wypelnienie") or {}).get("wypelnienie") is not None]
        report["papier"] = dict(
            arkuszy=len(ok_ark), pole_m2=round(pole, 3), a4_ekw=round(pole / (0.210 * 0.297), 1),
            warstwy_a4=sum(a["skladanie"]["warstwy"] for a in ok_ark),
            skladanie={o: sum(1 for a in ok_ark if a["skladanie"]["ocena"] == o) for o in ("dobre", "poprawne", "słabe")},
            wypelnienie_wazone=(round(sum(a["wypelnienie"]["wypelnienie"] * a["wypelnienie"]["pole_ramki_m2"] for a in wz)
                                      / sum(a["wypelnienie"]["pole_ramki_m2"] for a in wz), 3) if wz else None))
    report["problemy"] = list(ctx.problems)
    report["czas_s"] = round(time.time() - t0, 1)
    (out / "raport_widokow.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str),
                                             encoding="utf-8")
    return report
