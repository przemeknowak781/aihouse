"""lamela.views — generatory widoków rysunkowych z modelu budynku (rzuty, rzut dachu, przekroje, elewacje, arkusze).

Źródło danych: ``model/budynek.yaml`` + ``model/dzialka.yaml`` (``lamela.model.load_model``) i reprezentacja pośrednia
(``lamela.ir.build_ir``); rysowanie: silnik ``lamela.draft`` (DXF + PDF wektorowy + PNG). Uruchamianie z
``PYTHONPATH=src``.

API::

    from lamela.model import load_model
    from lamela.ir import build_ir
    from lamela.draft import Sheet, Viewport
    from lamela import views as V

    m = load_model("model/budynek.yaml", "model/dzialka.yaml", strict=False)
    ir = build_ir(m, otoczenie=True, auta=False)          # otoczenie=True — teren (profil gruntu na przekrojach)
    cfg = V.load_config("model/arkusze.yaml", m)           # None → zestaw domyślny
    ctx = V.make_context(m, ir, cfg, V.load_furniture("model/wyposazenie.yaml"))

    vp = Viewport(50, "RZUT PARTERU");  res = V.draw_plan(vp, ctx, "P0")          # PlanResult
    vp = Viewport(50, "RZUT DACHU");    V.draw_roof_plan(vp, ctx)
    sec = V.normalize_section({"id": "A", "x": 0.6, "patrz": "E"}, m)
    vp = Viewport(50, sec["nazwa"]);    V.draw_section(vp, ctx, sec)               # SectionResult
    vp = Viewport(50, "ELEWACJA S");    V.draw_elevation(vp, ctx, "S")             # ElevationResult

    sh, info = V.build_sheet(ctx, {"nr": "PB-AR-01", "tytul": "RZUT PARTERU", "typ": "rzut", "kond": "P0"}, 1, 10)
    sh.save("wyniki/PB-AR-01_rzut_parteru")                                      # .dxf .pdf .png

    V.generate("model/budynek.yaml", "model/dzialka.yaml", "model/arkusze.yaml", None, "projekt/03_PAB/rysunki")

CLI: ``PYTHONPATH=src python3 tools/generuj_widoki.py --help``.

Moduły: ``plan`` (rzut kondygnacji, rzut dachu, wymiary zewnętrzne/wewnętrzne, osie, znaki przekrojów, wyposażenie),
``section`` (przekrój pionowy, definicje przekrojów, wysokość budynku wg § 6 WT), ``elevation`` (elewacje z usuwaniem
linii niewidocznych i kolorystyką), ``hlr`` (rzutowanie pryzm IR i usuwanie linii niewidocznych), ``sheets``
(konfiguracja YAML — format opisany w docstringu modułu, dobór formatu arkusza, tabliczka, legendy, zapis, QA, tom),
``common`` (adapter materiałów modelu → kreskowania silnika, numeracja pomieszczeń wg PN-B-01025, rozmieszczanie
adnotacji bez kolizji).
"""
from .common import ViewContext, hatch_code, load_furniture, material_color, material_name, room_label
from .elevation import draw_elevation
from .plan import draw_plan, draw_roof_plan
from .section import auto_sections, building_height, draw_section, normalize_section
from .sheets import build_sheet, generate, load_config, make_context

__all__ = [
    "ViewContext", "hatch_code", "load_furniture", "material_color", "material_name", "room_label",
    "draw_plan", "draw_roof_plan", "draw_section", "draw_elevation", "normalize_section", "auto_sections",
    "building_height", "build_sheet", "generate", "load_config", "make_context",
]
