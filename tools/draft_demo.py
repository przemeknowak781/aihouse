#!/usr/bin/env python3
"""Demonstracja i test silnika rysunkowego ``lamela.draft``.

Generuje w ``projekt/00_demo_silnika/``:
  (a) DEMO-01 — A3: próbny rzut fragmentu parteru 1:50 (ściany warstwowe, okna, drzwi, HS, schody, łazienka, meble,
      łańcuchy wymiarowe, osie, rzędne, oznaczenia pomieszczeń, przekrój, północ) + zestawienia i legenda,
  (b) DEMO-02 — A3: próbny przekrój 1:50 (fundament, płyta, strop, stropodach z attyką, opis warstw, rzędne)
      + detal attyki 1:20 w drugiej rzutni,
  (c) DEMO-03 — A2: tablica kreskowań materiałów i symboli (legendy),
  oraz tom PDF (spis + 3 arkusze) i raport kontroli skali/rozdzielczości.

Uruchomienie:  PYTHONPATH=src python3 tools/draft_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import Polygon, box

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from lamela.draft import dims, elements as E, fmt, hatch, plot, symbols as S  # noqa: E402
from lamela.draft.sheet import (Sheet, TitleBlock, lettering_sample, lines_legend, notes_box, scale_bar,  # noqa: E402
                                table)

OUT = ROOT / "projekt" / "00_demo_silnika"

TB_COMMON = dict(
    pracownia="PRACOWNIA PROJEKTOWA — nazwa do uzupełnienia",
    pracownia_adres="adres pracowni do uzupełnienia",
    inwestor="(do uzupełnienia)",
    obiekt="Budynek mieszkalny jednorodzinny „Dom LAMELA” — PRÓBA SILNIKA RYSUNKOWEGO (rysunek testowy)",
    lokalizacja="dz. nr ewid. 123/4, obręb 0005 Przykładowo, jedn. ewid. Przykładowo (dane fikcyjne)",
    kategoria="I",
    stadium="PB",
    data="2026-09-25",
    rewizja="0",
)

# ==================================================================================================== model próbny
# osie konstrukcyjne (m) — układ budynku: x → wschód, y → północ
AX = {"A": 0.00, "B": 4.20, "C": 7.20}
AY = {"1": 0.00, "2": 5.70}
SZ1 = [("TYNK", 0.015, "wyk"), ("MUR_SILIKAT", 0.18, "konstr"), ("IZOL_TWARDA", 0.20, "izol"),
       ("TYNK", 0.007, "wyk")]
T_IN, T_STR, T_INS = 0.015, 0.18, 0.20
F_IN = T_STR / 2 + T_IN               # lico wewn. (z tynkiem) od osi
F_STR = T_STR / 2                     # lico muru od osi
F_EXT = T_STR / 2 + T_INS             # lico ocieplenia od osi (wymiary w stanie surowym + ocieplenie)
Y_PART = 2.05                          # oś ścianki działowej łazienka/hol
OPEN = {
    # symbol: (ściana (p1, p2 osi), a, b, wys., parapet)
    "O1": (((0.0, 0.0), (7.2, 0.0)), 1.30, 2.20, 0.90, 1.30),
    "HS1": (((0.0, 0.0), (7.2, 0.0)), 4.80, 6.80, 2.40, 0.00),
    "O2": (((0.0, 0.0), (0.0, 5.7)), 3.90, 5.10, 1.50, 0.90),
    "O3": (((7.2, 0.0), (7.2, 5.7)), 0.90, 2.30, 1.50, 0.85),
    "D1": (((0.0, Y_PART), (4.2, Y_PART)), 2.90, 3.80, 2.05, None),
    "D2": (((4.2, 0.0), (4.2, 5.7)), 2.80, 3.70, 2.05, None),
}


def demo_plan():
    tb = TitleBlock(**TB_COMMON, branza="ARCHITEKTURA (AR)", tytul="RZUT PRÓBNY — FRAGMENT PARTERU", skala="1:50",
                    nr_rysunku="DEMO-01", arkusz="1/3", rodzaj="rzut",
                    rewizje=[("0", "Wydanie do weryfikacji silnika rysunkowego", "2026-09-25")])
    sh = Sheet("A3", title_block=tb)
    vp = sh.add_viewport(50, "RZUT PARTERU (FRAGMENT)")
    k = vp.k

    # ---------------------------------------------------------------- ściany
    cs = E.CutSet()
    ring = [(AX["A"], AY["1"]), (AX["C"], AY["1"]), (AX["C"], AY["2"]), (AX["A"], AY["2"])]
    E.ring_layers(cs, ring, SZ1)
    # ściana nośna w osi B (18 cm + tynki)
    E.wall_layers(cs, (AX["B"], F_STR - 0.01), (AX["B"], AY["2"] - F_STR + 0.01),
                  [("TYNK", 0.015, "wyk"), ("MUR_SILIKAT", 0.18, "konstr"), ("TYNK", 0.015, "wyk")])
    # ścianka działowa 12 cm (ceramika) łazienka / hol
    E.wall_layers(cs, (F_STR - 0.01, Y_PART), (AX["B"] - F_STR + 0.01, Y_PART),
                  [("TYNK", 0.015, "wyk"), ("MUR_CERAMIKA", 0.12, "dzial"), ("TYNK", 0.015, "wyk")], angle=135.0)
    depth = {"D1": 0.09, "D2": 0.12}
    for sym, (wall, a, b, h, sill) in OPEN.items():
        cs.cut_out(E.opening_rect(wall[0], wall[1], a, b, depth.get(sym, 0.35)))
    # szacht instalacyjny w łazience (otwór w stropie — obrys z przekątnymi)
    shaft = [(F_IN, 1.85), (F_IN + 0.30, 1.85), (F_IN + 0.30, Y_PART - 0.075), (F_IN, Y_PART - 0.075)]
    cs.draw(vp)
    S.floor_opening(vp, shaft)

    # ---------------------------------------------------------------- stolarka
    s_int, s_ext = F_IN, -(F_EXT + 0.007)
    # strona wnętrza względem kierunku osi ściany: +1 = po lewej, −1 = po prawej
    inside = {"O1": 1.0, "O2": -1.0, "O3": 1.0}
    for sym in ("O1", "O2", "O3"):
        (p1, p2), a, b, h, sill = OPEN[sym]
        A, B = np.array(p1), np.array(p2)
        d = (B - A) / np.linalg.norm(B - A)
        S.window(vp, A + d * a, A + d * b, s_int, s_ext, frame_in=-0.03, frame_out=-0.115, side=inside[sym])
    (p1, p2), a, b, h, sill = OPEN["HS1"]
    S.sliding_door(vp, (a, 0.0), (b, 0.0), 0.40, side=1.0, kind="HS", fixed="b", frame_pos=-0.05)
    S.door(vp, (2.90, Y_PART), (3.80, Y_PART), 0.15, side=-1.0, hinge="b")          # D1 do łazienki
    S.door(vp, (AX["B"], 2.80), (AX["B"], 3.70), 0.21, side=-1.0, hinge="a")        # D2 do pokoju

    # ---------------------------------------------------------------- schody (dwubiegowe, rzut parteru)
    xL, xR = F_IN + 1.0, F_IN + 1.0 + 8 * 0.28
    y_top = AY["2"] - F_IN
    S.stairs(vp, (xR, y_top - 0.5), 180.0, 1.0, 8, 0.28, 0.175, first_no=1, cut_after=5, total_steps=18,
             side_label=-1.0)
    # spocznik (nad płaszczyzną cięcia — linią kreskową) i bieg 2 (nad cięciem)
    vp.polygon([(F_IN, y_top - 2.1), (xL, y_top - 2.1), (xL, y_top), (F_IN, y_top)], "A-SCHODY", lt="KRESKOWA")
    for i in range(9):
        x = xL + i * 0.28
        vp.line((x, y_top - 2.1), (x, y_top - 1.1), "A-SCHODY", lt="KRESKOWA")
    vp.line((xL, y_top - 2.1), (xR, y_top - 2.1), "A-SCHODY", lt="KRESKOWA")
    vp.line((xL, y_top - 1.05), (xR, y_top - 1.05), "A-SCHODY", pen="srednia")   # balustrada/policzek

    # ---------------------------------------------------------------- wyposażenie
    y_bath_in = Y_PART - 0.075
    S.wc_hung(vp, (F_IN, 1.25), 0.0)
    S.washbasin_counter(vp, (1.35, y_bath_in), -90.0, w=1.2, d=0.5)
    S.washing_machine(vp, (2.35, y_bath_in), -90.0)
    S.shower_walkin(vp, (AX["B"] - F_IN, F_IN + 0.50), 180.0, w=1.0, d=1.05, glass_side="right")
    S.bed(vp, (5.80, AY["2"] - F_IN), -90.0, 1.6, 2.0)
    S.wardrobe(vp, (AX["B"] + F_IN, 4.75), 0.0, 1.5, 0.6, doors="sliding")
    S.desk(vp, (AX["B"] + F_IN, 1.40), 0.0, 1.2, 0.6)

    # ---------------------------------------------------------------- oznaczenia pomieszczeń
    x_b_in = AX["B"] - F_IN
    rooms = [
        ("1.01", "Hol ze schodami", (1.95, 2.95), Polygon([(F_IN, Y_PART + 0.075), (x_b_in, Y_PART + 0.075),
                                                         (x_b_in, AY["2"] - F_IN), (F_IN, AY["2"] - F_IN)]), "gres"),
        ("1.02", "Łazienka", (2.45, 0.80), Polygon([(F_IN, F_IN), (x_b_in, F_IN), (x_b_in, Y_PART - 0.075),
                                                    (F_IN, Y_PART - 0.075)]), "gres"),
        ("1.03", "Pokój", (5.55, 1.62), Polygon([(AX["B"] + F_IN, F_IN), (AX["C"] - F_IN, F_IN),
                                                 (AX["C"] - F_IN, AY["2"] - F_IN), (AX["B"] + F_IN, AY["2"] - F_IN)]),
         "deska"),
    ]
    for nr, name, pos, pg, floor in rooms:
        S.room_tag(vp, pos, nr, name, pg.area, level_z=None if nr == "1.01" else (0.0 if nr != "1.02" else -0.02))
    dims.level_plan(vp, (0.40, 3.22), 0.0, style="x")

    # ---------------------------------------------------------------- osie
    x_min, x_max = AX["A"] - F_EXT, AX["C"] + F_EXT
    y_min, y_max = AY["1"] - F_EXT, AY["2"] + F_EXT
    c1, sp = 10.0 * k, 7.0 * k     # 1. łańcuch 10 mm od obrysu, kolejne co 7 mm (R4 pkt 3.5)
    y_ch = [y_min - c1 - i * sp for i in range(4)]
    x_ch = [x_min - c1 - i * sp for i in range(4)]
    y_ax_bot = y_ch[-1] - 5.0 * k
    x_ax_left = x_ch[-1] - 5.0 * k
    y_top_ch = y_max + c1
    x_right_ch = [x_max + c1]
    for name, x in AX.items():
        S.axis_line(vp, (x, y_ax_bot), (x, y_top_ch + 5.0 * k), name, "both")
    vp.meta_axis = ((AX["B"], y_ax_bot), (AX["B"], y_top_ch + 5.0 * k))
    for name, y in AY.items():
        S.axis_line(vp, (x_ax_left, y), (x_right_ch[-1] + 4.0 * k, y), name, "start")

    # ---------------------------------------------------------------- wymiary zewnętrzne (PN-B-01029)
    # ciągi zewnętrzne (PN-B-01029 / R4 pkt 3.5), od obrysu: 1) otwory i filary, 2) osie otworów i ściany
    # wewnętrzne dochodzące do ściany zewnętrznej, 3) osie konstrukcyjne, 4) wymiar całkowity
    o1, hs = OPEN["O1"], OPEN["HS1"]
    dims.dim_h(vp, [x_min, o1[1], o1[2], hs[1], hs[2], x_max], y_ch[0], y_min)
    dims.dim_h(vp, [x_min, AX["A"] + F_STR, (o1[1] + o1[2]) / 2, AX["B"] - F_STR, AX["B"] + F_STR,
                    (hs[1] + hs[2]) / 2, AX["C"] - F_STR, x_max], y_ch[1], y_min)
    dims.dim_h(vp, list(AX.values()), y_ch[2], y_min)
    dims.dim_h(vp, [x_min, x_max], y_ch[3], y_min)
    o2 = OPEN["O2"]
    dims.dim_v(vp, [y_min, o2[1], o2[2], y_max], x_ch[0], x_min)
    dims.dim_v(vp, [y_min, AY["1"] + F_STR, Y_PART - 0.06, Y_PART + 0.06, (o2[1] + o2[2]) / 2, AY["2"] - F_STR,
                    y_max], x_ch[1], x_min)
    dims.dim_v(vp, list(AY.values()), x_ch[2], x_min)
    dims.dim_v(vp, [y_min, y_max], x_ch[3], x_min)
    # wschód: otwory; północ: osie (ściana bez otworów — ciągi 1–2 pominięte)
    o3 = OPEN["O3"]
    dims.dim_v(vp, [y_min, o3[1], o3[2], y_max], x_right_ch[0], x_max)
    dims.dim_h(vp, list(AX.values()), y_top_ch, y_max)
    # wewnętrzne
    dims.dim_h(vp, [AX["B"] + F_STR, AX["C"] - F_STR], 2.45, 2.2, ext="short")
    dims.dim_v(vp, [AY["1"] + F_STR, AY["2"] - F_STR], 6.55, 6.75, ext="short")
    dims.dim_h(vp, [AX["A"] + F_STR, 2.90, 3.80, AX["B"] - F_STR], Y_PART + 0.34, Y_PART + 0.1, ext="short")

    # ---------------------------------------------------------------- oznaczenia otworów (symbol + ułamek)
    dims.opening_dim(vp, (1.75, F_IN), (1, 0), 0.90, 0.90, 1.30, side=1, symbol="O1", axis_mm=8.0)
    dims.opening_dim(vp, (5.80, F_IN), (1, 0), 2.00, 2.40, None, side=1, symbol="HS1", axis_mm=10.0,
                     symbol_shape="ellipse")
    dims.opening_dim(vp, (F_IN, 4.50), (0, 1), 1.20, 1.50, 0.90, side=-1, symbol="O2", axis_mm=8.0)
    dims.opening_dim(vp, (AX["C"] - F_IN, 1.60), (0, 1), 1.40, 1.50, 0.85, side=1, symbol="O3", axis_mm=8.0)
    # drzwi: tylko symbol (wymiary w zestawieniu otworów — PN-B-01029)
    dims.opening_dim(vp, (3.35, Y_PART - 0.075), (1, 0), None, None, symbol="D1", side=-1, axis_mm=3.0)
    dims.opening_dim(vp, (AX["B"] - F_IN, 3.25), (0, 1), None, None, symbol="D2", side=1, axis_mm=4.0)

    # ---------------------------------------------------------------- przekrój, północ
    S.section_mark(vp, (6.30, y_ax_bot - 5.0 * k), (6.30, y_top_ch + 16 * k), "A", look=1.0)

    x0, y0, x1, y1 = sh.frame
    sh.place(vp, x0 + 3.0, y1 - 3.0, "tl")
    sh.view_title(vp, "RZUT PARTERU — FRAGMENT", dx=2.0)

    # ---------------------------------------------------------------- kolumna prawa: północ, legendy, zestawienia
    fx0, fy0, fx1, fy1 = sh.free_above_title_block()
    fx0 = max(fx0, vp.clip[2] + 1.0)        # kolumna opisowa na prawo od rzutni
    colx = fx0 + 1.0
    S.north_arrow(sh, (fx1 - 14.0, fy1 - 16.0), 15.0, 0.0)
    ytab = fy1 - 6.0
    rows = []
    for nr, name, pos, pg, floor in rooms:
        rows.append([nr, name, floor, fmt.area(pg.area, unit=False)])
    tot = sum(r[3].area for r in rooms)
    rows.append(["", "RAZEM", "", fmt.area(tot, unit=False)])
    r = table(sh, colx, ytab - 4.0, [("Nr", 12), ("Nazwa pomieszczenia", 46), ("Posadzka", 24), ("Pow. [m²]", 22)],
              rows, h=2.5, row_h=5.0, title="ZESTAWIENIE POMIESZCZEŃ", align=["center", "left", "left", "right"])
    rows2 = []
    for sym, (wall, a, b, h, sill) in OPEN.items():
        rows2.append([sym, fmt.dim_text(b - a), fmt.dim_text(h), "—" if sill is None else fmt.dim_text(sill)])
    r2 = table(sh, colx, r[1] - 10.0, [("Symbol", 16), ("Szer. [cm]", 20), ("Wys. [cm]", 20), ("Parapet [cm]", 22)],
               rows2, h=2.5, row_h=5.0, title="ZESTAWIENIE OTWORÓW (w świetle muru)")
    lg = hatch.legend(sh, colx, r2[1] - 4.0, ["MUR_SILIKAT", "MUR_CERAMIKA", "IZOL_TWARDA", "TYNK"], cols=2,
                      col_w=(fx1 - colx) / 2.0, sw=(11.0, 5.5), h=1.8, title="OZNACZENIA MATERIAŁÓW",
                      show_source=False, row_gap=1.6)
    notes = ["Wymiary w cm (mm w indeksie górnym, np. 24⁵ = 24,5 cm), rzędne w m. ±0,000 = posadzka parteru = "
             "101,650 m n.p.m. (PL-EVRF2007-NH).",
             "Otwory: licznik — szerokość, mianownik — wysokość w świetle muru, w nawiasie wysokość parapetu.",
             "Oznaczenia mur silikatowy i EPS/wełna — przyjęte (brak w PN-B-01030), objaśnione w legendzie.",
             "Rysunek testowy silnika — dane nie stanowią projektu."]
    nb = notes_box(sh, fx0, lg[1] - 2.0, fx1 - fx0, notes, "OBJAŚNIENIA I UWAGI", h=1.8)
    scale_bar(sh, (fx0 + 4.0, nb[1] - 9.0), 50, 3.0)
    plot.add_control_marks(sh)
    files = sh.save(OUT / "DEMO-01_rzut_1-50")
    return sh, vp, files


# ==================================================================================================== (b) przekrój
FLOOR_P0 = [("PLYTKI", 0.015, "wyk"), ("JASTRYCH", 0.065, "warstwa"), ("PAROIZOLACJA", 0.002, "membrana"),
            ("IZOL_TWARDA", 0.15, "izol"), ("IZOL_PRZECIWWODNA", 0.005, "membrana"), ("ZELBET", 0.25, "fund"),
            ("BETON", 0.10, "warstwa"), ("PIASEK", 0.20, "grunt")]
FLOOR_P0_TXT = ["Płytki gresowe na kleju 1,5 cm", "Jastrych cementowy z ogrz. podłogowym 6,5 cm",
                "Folia PE 0,2 mm", "Styropian EPS 100-036 15 cm", "Izolacja przeciwwodna (papa termozgrzewalna)",
                "Płyta fundamentowa żelbetowa C30/37 25 cm", "Beton podkładowy C12/15 10 cm",
                "Podsypka piaskowa zagęszczona 20 cm"]
FLOOR_P1 = [("PLYTKI", 0.015, "wyk"), ("JASTRYCH", 0.06, "warstwa"), ("PAROIZOLACJA", 0.002, "membrana"),
            ("IZOL_TWARDA", 0.05, "izol"), ("ZELBET", 0.20, "strop"), ("TYNK", 0.015, "wyk")]
FLOOR_P1_TXT = ["Deska warstwowa / płytki 1,5 cm", "Jastrych anhydrytowy 6 cm", "Folia PE 0,2 mm",
                "Styropian EPS 200 akustyczny 5 cm", "Strop żelbetowy C30/37 20 cm", "Tynk gipsowy 1,5 cm"]
ROOF = [("ZWIR", 0.05, "warstwa"), ("IZOL_PRZECIWWODNA", 0.004, "membrana"), ("IZOL_PIR", 0.22, "izol"),
        ("PAROIZOLACJA", 0.004, "membrana"), ("ZELBET", 0.20, "strop"), ("TYNK", 0.015, "wyk")]
ROOF_TXT = ["Żwir płukany 16/32 mm 5 cm", "Membrana PVC 1,5 mm", "Płyty PIR ze spadkiem 22 cm (min.)",
            "Paroizolacja (papa z wkładką Al)", "Strop żelbetowy C30/37 20 cm", "Tynk gipsowy 1,5 cm"]
WALL_TXT = ["Tynk gipsowy 1,5 cm", "Bloczek wapienno-piaskowy 18 cm", "Styropian grafitowy EPS 031 20 cm",
            "Tynk silikonowy 0,7 cm"]


def draw_section(vp, detail: bool = False):
    """Przekrój przez ścianę zewnętrzną, płytę fundamentową, strop i stropodach z attyką (model 2D: x, z)."""
    k = vp.k
    cs = E.CutSet()
    x_ax = 0.0                                  # oś ściany (x), wnętrze po prawej (+x)
    x_in = x_ax + 0.09 + 0.015                  # lico wewnętrzne
    x_str_o = x_ax - 0.09
    x_ins_o = x_str_o - 0.20
    x_r = 3.7                                   # prawa granica wycinka
    x_l = -3.2                                  # grunt na zewnątrz
    z0, z_p1, z_d = 0.0, 3.15, 6.30             # posadzki ±0,00, +3,15, wierzch stropu dachu
    # --- płyta fundamentowa i podłoga na gruncie (od wierzchu posadzki)
    zf = z0
    lay = E.section_h(cs, x_in, x_r, zf, FLOOR_P0[:5])
    z_slab_top = lay[-1][1]
    # płyta fundamentowa pod ścianą: od lica ocieplenia do x_r
    slab_bot = z_slab_top - 0.25
    cs.add(box(x_ins_o - 0.0, slab_bot, x_r, z_slab_top), "ZELBET", "fund")
    cs.add(box(x_ins_o - 0.0, slab_bot - 0.10, x_r, slab_bot), "BETON", "warstwa")
    cs.add(box(x_ins_o - 0.0 - 0.15, slab_bot - 0.30, x_r, slab_bot - 0.10), "PIASEK", "grunt", outline=False)
    # XPS na obwodzie płyty (ocieplenie cokołu/fundamentu)
    cs.add(box(x_ins_o - 0.12, slab_bot - 0.10, x_ins_o, z_slab_top), "IZOL_XPS", "izol",
           axis=((x_ins_o - 0.06, slab_bot), (x_ins_o - 0.06, z_slab_top)))
    # ściana parteru i piętra (mur + ocieplenie + tynki)
    z_wall_bot = z_slab_top
    z_attic_top = z_d + 0.05 + 0.004 + 0.22 + 0.004 + 0.35
    cs.add(box(x_str_o, z_wall_bot, x_ax + 0.09, z_p1 - 0.28), "MUR_SILIKAT", "konstr")
    cs.add(box(x_str_o, z_p1 - 0.08 - 0.20, x_ax + 0.09, z_p1 - 0.08), "ZELBET", "konstr")   # wieniec
    cs.add(box(x_str_o, z_p1 - 0.08, x_ax + 0.09, z_d - 0.20), "MUR_SILIKAT", "konstr")
    cs.add(box(x_str_o, z_d - 0.20, x_ax + 0.09, z_d), "ZELBET", "konstr")                    # wieniec
    # attyka żelbetowa
    cs.add(box(x_str_o, z_d, x_ax + 0.09, z_attic_top - 0.05), "ZELBET", "konstr")
    cs.add(box(x_ins_o, z_wall_bot + 0.30, x_str_o, z_attic_top - 0.05), "IZOL_TWARDA", "izol",
           axis=((x_ins_o + 0.1, 0.0), (x_ins_o + 0.1, 1.0)))
    cs.add(box(x_ins_o, z_wall_bot, x_str_o, z_wall_bot + 0.30), "IZOL_XPS", "izol",
           axis=((x_ins_o + 0.1, 0.0), (x_ins_o + 0.1, 1.0)))
    cs.add(box(x_ins_o - 0.007, z_wall_bot, x_ins_o, z_attic_top - 0.05), "TYNK", "wyk")
    # ocieplenie attyki od strony dachu i na koronie
    cs.add(box(x_ax + 0.09, z_d + 0.05 + 0.004 + 0.22 + 0.004 - 0.02, x_ax + 0.09 + 0.08, z_attic_top - 0.05),
           "IZOL_TWARDA", "izol", axis=((x_ax + 0.13, 0), (x_ax + 0.13, 1)))
    cs.add(box(x_ins_o, z_attic_top - 0.05, x_ax + 0.09 + 0.08, z_attic_top), "IZOL_TWARDA", "izol")
    # tynk wewnętrzny
    cs.add(box(x_ax + 0.09, z0, x_in, z_p1 - 0.20 - 0.015 - 0.075), "TYNK", "wyk")
    cs.add(box(x_ax + 0.09, z_p1, x_in, z_d - 0.20 - 0.015), "TYNK", "wyk")
    # strop nad parterem i podłoga piętra
    E.section_h(cs, x_in, x_r, z_p1, FLOOR_P1[:4])
    cs.add(box(x_ax + 0.09, z_p1 - 0.075 - 0.20 - 0.002 - 0.05 + 0.05 + 0.0 - 0.0, x_r,
               z_p1 - 0.015 - 0.06 - 0.002 - 0.05), "ZELBET", "strop")
    z_p1_slab_bot = z_p1 - 0.015 - 0.06 - 0.002 - 0.05 - 0.20
    cs.add(box(x_in, z_p1_slab_bot - 0.015, x_r, z_p1_slab_bot), "TYNK", "wyk")
    # stropodach
    z_top = z_d + 0.05 + 0.004 + 0.22 + 0.004
    E.section_h(cs, x_ax + 0.09 + 0.08, x_r, z_top, ROOF[:4])
    cs.add(box(x_ax + 0.09, z_d - 0.20, x_r, z_d), "ZELBET", "strop")
    cs.add(box(x_in, z_d - 0.20 - 0.015, x_r, z_d - 0.20), "TYNK", "wyk")
    # membrana wywinięta na attykę (pionowo)
    cs.add(box(x_ax + 0.09 + 0.08, z_top - 0.005, x_ax + 0.09 + 0.084, z_attic_top), "IZOL_PRZECIWWODNA", "membrana",
           axis=((0, 0), (0, 1)))
    # grunt: zasypka przy ścianie i grunt rodzimy
    z_ground = -0.30
    cs.add(Polygon([(x_l, slab_bot - 0.45), (x_ins_o - 0.12, slab_bot - 0.45), (x_ins_o - 0.12, z_ground),
                    (x_l, z_ground)]), "NASYP", "grunt", outline=False)
    cs.draw(vp)
    # ciągłość membrany na płycie / cokole
    hatch.membrane(vp, [(x_ins_o - 0.12, z_slab_top - 0.0), (x_ins_o - 0.12, z_ground + 0.3)], "przeciwwilgociowa")
    hatch.ground_line(vp, [(x_l, z_ground), (x_ins_o - 0.127, z_ground)])
    # obrys wykopu (linia cienka) i opaska
    vp.line((x_l, slab_bot - 0.45), (x_ins_o - 0.12, slab_bot - 0.45), "A-TEREN", pen="cienka", lt="KRESKOWA")
    # obróbka blacharska attyki
    vp.polyline([(x_ins_o - 0.03, z_attic_top - 0.06), (x_ins_o - 0.03, z_attic_top + 0.01),
                 (x_ax + 0.09 + 0.10, z_attic_top + 0.02), (x_ax + 0.09 + 0.10, z_attic_top - 0.06)], "A-WIDOK",
                pen="srednia")
    if not detail:
        # oś ściany
        S.axis_line(vp, (x_ax, slab_bot - 1.2), (x_ax, z_attic_top + 0.9), "A", "both", 4.0, 3.5)
        # rzędne — kolumna przy krawędzi przekroju (automatyczne rozsuwanie znaczników)
        dims.levels(vp, x_r + 0.25, [(z0, "zero", 101.65), (z_p1, "wyk"), (z_p1_slab_bot, "konstr"),
                                     (z_d, "konstr"), (z_top, "wyk"), (slab_bot - 0.10, "konstr")])
        dims.level_section(vp, (x_l + 0.35, z_ground), z_ground, "wyk", stub_mm=0)
        dims.level_section(vp, (x_ins_o - 0.35, z_attic_top), z_attic_top, "wyk", side="left", stub_mm=0)
        # wymiary pionowe (po lewej): kondygnacje i wysokość całkowita
        xd = x_l - 0.2
        dims.dim_v(vp, [slab_bot - 0.10, z0, z_p1, z_d, z_top, z_attic_top], xd, x_l + 0.5)
        dims.dim_v(vp, [slab_bot - 0.10, z_attic_top], xd - 7 * k, x_l + 0.5)
        # wysokości w świetle
        dims.dim_v(vp, [z0, z_p1_slab_bot - 0.015], 1.0, 1.2, ext="short")
        dims.dim_v(vp, [z_p1, z_d - 0.215], 1.0, 1.2, ext="short")
        # warstwy ściany (wymiar przez przegrodę — napisy z maską)
        dims.dim_h(vp, [x_ins_o - 0.007, x_ins_o, x_str_o, x_ax + 0.09, x_in], 1.55, 1.3, mask=0.3)
        # spadek dachu
        dims.slope(vp, (1.95, z_top + 0.22), (0.75, z_top + 0.22), 2.0)
        # opisy warstw — odnośniki "drabinkowe"
        xl = 2.2
        S.layer_callout(vp, (xl, z_d - 0.12), (xl, z_top + 0.45), ROOF_TXT, h=2.0, row_mm=4.0,
                        title="STROPODACH SD1", marks=[(xl, z_top - 0.03), (xl, z_top - 0.16), (xl, z_d - 0.1)])
        S.layer_callout(vp, (xl, z_p1_slab_bot + 0.05), (xl, z_p1 + 0.35), FLOOR_P1_TXT, h=2.0, row_mm=4.0,
                        title="STROP ST1 / PODŁOGA P1", marks=[(xl, z_p1 - 0.04), (xl, z_p1 - 0.12)])
        S.layer_callout(vp, (xl, slab_bot - 0.22), (xl, z0 + 0.30), FLOOR_P0_TXT, h=2.0, row_mm=4.0,
                        title="PODŁOGA NA GRUNCIE P0", marks=[(xl, z0 - 0.04), (xl, z0 - 0.15), (xl, z0 - 0.4)])
        S.layer_callout(vp, (x_in - 0.005, 4.75), (-0.65, 4.75), list(reversed(WALL_TXT)), side="left", h=2.0,
                        row_mm=4.0, title="ŚCIANA SZ1", marks=[(x_ax, 4.75), (x_ins_o + 0.1, 4.75)])
        S.detail_callout(vp, (x_ax - 0.02, z_attic_top - 0.28), 12.0, "A", leader_to=(x_l + 0.5, z_attic_top + 0.85))
    else:
        dims.dim_h(vp, [x_ins_o - 0.007, x_ins_o, x_str_o, x_ax + 0.09, x_ax + 0.17], z_attic_top + 0.35,
                   z_attic_top + 0.1)
        dims.dim_v(vp, [z_d - 0.2, z_d, z_top, z_attic_top - 0.05, z_attic_top], x_ins_o - 0.25, x_ins_o)
        dims.levels(vp, x_ins_o + 1.9, [(z_top, "wyk"), (z_d, "konstr")])
        dims.slope(vp, (x_ins_o + 1.7, z_top + 0.15), (x_ins_o + 0.9, z_top + 0.15), 2.0)
    return dict(z_attic_top=z_attic_top, x_ins_o=x_ins_o, z_d=z_d, x_r=x_r, slab_bot=slab_bot, x_l=x_l)


def demo_section():
    tb = TitleBlock(**TB_COMMON, branza="ARCHITEKTURA", tytul="PRZEKRÓJ PRÓBNY A-A", skala="1:50, 1:20",
                    nr_rysunku="DEMO-02")
    sh = Sheet("A3", title_block=tb)
    vp = sh.add_viewport(50, "PRZEKRÓJ A-A")
    g = draw_section(vp)
    x0, y0, x1, y1 = sh.frame
    sh.place(vp, x0 + 3.0, y1 - 3.0, "tl")
    sh.view_title(vp, "PRZEKRÓJ A-A (FRAGMENT)")
    # detal A 1:20 — druga rzutnia, ten sam rysunek z adnotacjami w skali detalu
    vd = sh.add_viewport(20, "DETAL A")
    draw_section(vd, detail=True)
    fx0, fy0, fx1, fy1 = sh.free_above_title_block()
    fx0 = max(fx0, vp.clip[2] + 2.0)
    clip = (g["x_ins_o"] - 0.80, g["z_d"] - 0.45, g["x_ins_o"] + 2.3, g["z_attic_top"] + 0.6)
    sh.place(vd, fx0 + 4.0, fy1 - 10.0, "tl", clip_model=clip)
    vd_frame = vd.clip
    sh.rect(*vd_frame, layer="R-OPISY", pen=0.25)
    sh.view_title(vd, "DETAL A — ATTYKA", where="above", dx=0.0)
    notes = ["Rzędne w m względem ±0,00 = 101,65 m n.p.m.; wymiary w cm.",
             "Trójkąt zaczerniony — rzędna wykończenia, niezaczerniony — rzędna konstrukcji, "
             "w połowie zaczerniony — poziom ±0,00 z rzędną bezwzględną.",
             "Rysunek testowy silnika — dane nie stanowią projektu."]
    nb = notes_box(sh, fx0, vd_frame[1] - 12.0, fx1 - fx0, notes, "UWAGI", h=2.0)
    b1 = scale_bar(sh, (fx0 + 4.0, nb[1] - 9.0), 50, 5.0)
    scale_bar(sh, (fx0 + 4.0, b1[1] - 13.0), 20, 2.0)
    plot.add_control_marks(sh)
    files = sh.save(OUT / "DEMO-02_przekroj_1-50")
    return sh, vp, files


# ==================================================================================================== (c) legendy
def demo_legend():
    tb = TitleBlock(**TB_COMMON, branza="WIELOBRANŻOWY", tytul="TABLICA OZNACZEŃ: MATERIAŁY I SYMBOLE",
                    skala="—", nr_rysunku="DEMO-03")
    sh = Sheet("A2", title_block=tb)
    x0, y0, x1, y1 = sh.frame
    codes = list(hatch.PATTERNS)
    lg = hatch.legend(sh, x0 + 8.0, y1 - 8.0, codes, cols=3, col_w=92.0, sw=(18.0, 9.0), h=2.2,
                      title="OZNACZENIA MATERIAŁÓW W PRZEKROJACH (PN-B-01030:2000 + oznaczenia przyjęte)")
    # symbole — siatka komórek
    cells = []

    def cell(title, fn):
        cells.append((title, fn))

    # architektura (symbole umowne w rozmiarze wydruku; wybrane powiększone dla czytelności tablicy)
    cell("Strzałka północy", lambda c, p: S.north_arrow(c, p + (0, -2), 14.0))
    cell("Oś konstrukcyjna", lambda c, p: S.axis_line(c, p + (-14, 0), p + (14, 0), "B", "start", 4.0, 3.5))
    cell("Oznaczenie przekroju", lambda c, p: S.section_mark(c, p + (-18, -3), p + (18, -3), "A", 1.0, 5.0, 7, 5.5))
    cell("Oznaczenie pomieszczenia", lambda c, p: S.room_tag(c, p, "0.05", "Salon", 32.45, level_z=0.0, h=2.5))
    cell("Symbol stolarki", lambda c, p: (S.tag(c, p + (-8, 0), "O1"), S.tag(c, p + (8, 0), "HS1", "ellipse")))
    cell("Rzędna — rzut (X / ramka)", lambda c, p: (dims.level_plan(c, p + (-18, 2), 0.0),
                                                     dims.level_plan(c, p + (10, -4), -0.02, style="box")))
    cell("Rzędne — przekrój (±0,00 / wyk. / konstr.)",
         lambda c, p: dims.levels(c, p[0] - 22, [(p[1] - 6, "zero", 101.65)], nd=2) if False else (
             dims.level_section(c, p + (-22, -8), text="±0,00", kind="zero", abs_z=101.65, stub_mm=3),
             dims.level_section(c, p + (-2, -5), 3.15, "wyk", stub_mm=3),
             dims.level_section(c, p + (15, -5), 2.95, "konstr", stub_mm=3)))
    cell("Spadek / pochylnia", lambda c, p: (dims.slope(c, p + (-22, 3), p + (-4, 3), 2.0),
                                              dims.slope(c, p + (2, -4), p + (22, -4), 6.0, ramp=True)))
    cell("Wejście do budynku (±0,00 / poniżej)", lambda c, p: (S.entrance_arrow(c, p + (-6, 0), 0.0),
                                                               S.entrance_arrow(c, p + (12, 0), 0.0, filled=False)))
    cell("Odnośnik szczegółu", lambda c, p: S.detail_callout(c, p + (-10, 1), 6.0, "A", leader_to=p + (5, -5)))
    cell("Wymiar (cm, mm w indeksie)", lambda c, p: dims.dim_h(c, [p[0] - 22, p[0] - 6, p[0] + 1.5, p[0] + 22],
                                                                p[1] - 2, p[1] - 7,
                                                                labels=[dims.dim_runs(0.245), dims.dim_runs(0.12),
                                                                        dims.dim_runs(0.365)]))
    cell("Otwór w stropie / szacht", lambda c, p: S.floor_opening(c, [p + (-10, -6), p + (10, -6), p + (10, 6),
                                                                       p + (-10, 6)]))
    cell("Drzwi rozwierane", lambda c, p: (c.line(p + (-26, -6), p + (-9, -6), "A-SCIANY-KONSTR"),
                                           c.line(p + (9, -6), p + (26, -6), "A-SCIANY-KONSTR"),
                                           S.door(c, p + (-9, -6), p + (9, -6), 2.0, 1.0, "a")))
    cell("Drzwi przesuwne HS", lambda c, p: (c.line(p + (-26, -2), p + (-12, -2), "A-SCIANY-KONSTR"),
                                             c.line(p + (12, -2), p + (26, -2), "A-SCIANY-KONSTR"),
                                             S.sliding_door(c, p + (-12, -2), p + (12, -2), 5.0, 1.0, "HS", "b",
                                                            frame_depth=3.2)))
    cell("Okno (rama, szyba, parapety)", lambda c, p: (c.line(p + (-26, -1), p + (-10, -1), "A-SCIANY-KONSTR"),
                                                        c.line(p + (10, -1), p + (26, -1), "A-SCIANY-KONSTR"),
                                                        S.window(c, p + (-10, -1), p + (10, -1), 3.0, -5.0, -0.5,
                                                                 -2.2, 1.0, sill_in_over=0.6, sill_out_over=0.8)))
    cell("Schody — bieg z linią cięcia", lambda c, p: S.stairs(c, p + (-24, -1), 0.0, 10.0, 8, 5.6, 3.5, cut_after=5,
                                                               h=2.0, total_steps=18, label_values=(0.175, 0.28)))
    # elektryka (PN-EN 60617) — rozmiar ×1,6
    z = 1.6
    cell("Gniazdo 1f / 2× / IP44 / 3f", lambda c, p: (S.socket(c, p + (-21, -6), 90, s_mm=3 * z),
                                                        S.socket(c, p + (-7, -6), 90, n=2, s_mm=3 * z),
                                                        S.socket(c, p + (7, -6), 90, ip44=True, s_mm=3 * z),
                                                        S.socket(c, p + (19, -6), 90, phases=3, s_mm=3 * z)))
    cell("Łącznik 1-bieg. / 2-bieg. / schodowy", lambda c, p: (S.switch(c, p + (-16, -6), 90, "1", s_mm=3 * z),
                                                                S.switch(c, p + (0, -6), 90, "2", s_mm=3 * z),
                                                                S.switch(c, p + (16, -6), 90, "schodowy", s_mm=3 * z)))
    cell("Oprawa ogólna / kinkiet / ścienna / liniowa", lambda c, p: (
        S.light(c, p + (-21, 0), s_mm=4 * z), S.light(c, p + (-11, -6), "kinkiet", 90, s_mm=4 * z),
        S.light(c, p + (-1, -6), "sciana", 90, s_mm=3.4 * z), S.light_linear(c, p + (9, 0), p + (26, 0), 2.4)))
    cell("Rozdzielnica / puszka / uziemienie", lambda c, p: (S.panel(c, p + (-15, -6), 90, 14, 4.5, "RG"),
                                                              S.junction_box(c, p + (2, 0), 2.4),
                                                              S.earth(c, p + (16, 4), s_mm=3 * z)))
    cell("Czujnik ruchu / dzwonek / wideodomofon", lambda c, p: (S.motion_sensor(c, p + (-16, -6), s_mm=3.2 * z),
                                                                   S.bell(c, p + (0, -6), s_mm=3 * z),
                                                                   S.videophone(c, p + (16, -6), s_mm=3.6 * z)))
    cell("Gniazdo RJ45 / TV / SPD", lambda c, p: (S.data_outlet(c, p + (-19, -6), s_mm=3 * z),
                                                   S.data_outlet(c, p + (-6, -6), label="TV", s_mm=3 * z),
                                                   S.spd(c, p + (8, -3), s_mm=3.5 * z)))
    # sanitarne
    cell("Pion / zawór / zawór zwrotny", lambda c, p: (S.riser(c, p + (-18, 0), "K1", s_mm=4.0),
                                                        c.line(p + (-4, 0), p + (24, 0), "S-WODA"),
                                                        S.valve(c, p + (2, 0), s_mm=5.0),
                                                        S.check_valve(c, p + (16, 0), s_mm=5.0)))
    cell("Wodomierz / filtr / pompa", lambda c, p: (c.line(p + (-26, 0), p + (26, 0), "S-WODA"),
                                                     S.water_meter(c, p + (-14, 0), 6.0), S.filter_(c, p + (0, 0), 5.5),
                                                     S.pump(c, p + (14, 0), 6.0)))
    cell("Rury: W / C / Cy / K", lambda c, p: [S.pipe(c, [p + (-24, 7 - 4.4 * i), p + (24, 7 - 4.4 * i)], m,
                                                      label={"W": "W — woda zimna", "C": "C — CWU",
                                                             "CY": "Cy — cyrkulacja", "K": "K — kanalizacja"}[m],
                                                      h=1.8, label_at=0.5)
                                               for i, m in enumerate(["W", "C", "CY", "K"])])
    cell("Rozdzielacz / zasobnik / pompa ciepła", lambda c, p: (S.manifold(c, p + (-27, -2), n=3, pitch_mm=3.0),
                                                                 S.tank(c, p + (-1, 0), 11.0, "CWU", h=2.0),
                                                                 S.heat_pump(c, p + (17, -4), 0, 13, 8, "PC")))
    cell("Czyszczak / wpust / rewizja", lambda c, p: (S.cleanout(c, p + (-17, 0), s_mm=4.0),
                                                       S.floor_drain(c, p + (0, 0), 6.0),
                                                       S.inspection(c, p + (16, 0), 8, 8)))
    cell("Kratka / anemostat N / W", lambda c, p: (S.grille(c, p + (-18, 0), 0, 10, 4),
                                                    S.anemostat(c, p + (-2, 0), 6, "N"),
                                                    S.anemostat(c, p + (14, 0), 6, "W")))
    cell("Czerpnia / wyrzutnia", lambda c, p: (S.air_terminal(c, p + (-6, -2), 180, "czerpnia", 8),
                                               S.air_terminal(c, p + (6, -2), 0, "wyrzutnia", 8)))
    cell("Rekuperator", lambda c, p: S.recuperator(c, p + (0, -3), 0, 20, 10, label=None))
    cell("Grzejnik / ogrzewanie podłogowe", lambda c, p: (S.radiator(c, p + (-26, 3), p + (-10, 3), 2.5),
                                                          S.floor_heating(c, box(p[0] - 4, p[1] - 8, p[0] + 24,
                                                                                 p[1] + 6), 1.6, 0.8)))
    # teren
    cell("Drzewo istn. / proj. / do wycinki", lambda c, p: (S.tree(c, p + (-17, 0), 11), S.tree(c, p + (0, 0), 11, False),
                                                            S.tree(c, p + (17, 0), 11, remove=True)))
    cell("Drzewo iglaste / krzew / żywopłot", lambda c, p: (S.tree(c, p + (-17, 0), 11, conifer=True),
                                                            S.shrub(c, p + (-3, 0), 6),
                                                            S.hedge(c, [p + (6, 0), p + (26, 0)], 4)))
    cell("Trawnik / kostka / deska", lambda c, p: (S.lawn(c, box(p[0] - 27, p[1] - 7, p[0] - 10, p[1] + 7), 30,
                                                          outline=True),
                                                   S.paving(c, box(p[0] - 8, p[1] - 7, p[0] + 8, p[1] + 7)),
                                                   S.paving(c, box(p[0] + 10, p[1] - 7, p[0] + 27, p[1] + 7), "deska")))
    cell("Słup en. / oświetl. / hydrant / studzienka", lambda c, p: (S.pole(c, p + (-20, 0), s_mm=3),
                                                                     S.pole(c, p + (-10, 0), "osw", s_mm=3),
                                                                     S.hydrant(c, p + (2, 0), 4.0),
                                                                     S.manhole(c, p + (14, 0), 4.0, "Sk")))
    cell("Złącze ZK / skrzynka", lambda c, p: (S.cable_box(c, p + (-10, -3), 0, 12, 4.5, "ZK"),
                                               S.utility_box(c, p + (10, -3), 0, 9, 4, "SW")))
    cell("Granica działki, punkty graniczne", lambda c, p: S.plot_boundary(c, [p + (-24, -6), p + (20, -6),
                                                                               p + (18, 6)], closed=False,
                                                                           point_labels=["12", "13", "14"]))
    cell("Linia zabudowy", lambda c, p: S.building_line(c, p + (-26, -2), p + (26, -2),
                                                         "nieprzekraczalna linia zabudowy"))
    cell("Warstwice / pkt wysokościowe", lambda c, p: (S.contours(c, [([p + (-26, -7), p + (-8, -3), p + (6, -6)],
                                                                         101.5)], label_every=20),
                                                       S.spot_height(c, p + (10, 3), 101.43),
                                                       S.spot_height(c, p + (-16, 4), 101.65, existing=False)))
    cell("Brama przesuwna / furtka", lambda c, p: (S.gate(c, p + (-24, -4), p + (-2, -4)),
                                                   S.gate(c, p + (6, -6), p + (18, -6), "furtka")))

    # rozmieszczenie siatki symboli
    top = lg[1] - 10.0
    sh.text((x0 + 8.0, top), "SYMBOLE GRAFICZNE (PN-B-01025, PN-EN 60617, PN-EN ISO 10628, PN-EN ISO 11091)", 3.5,
            style="bold", layer="R-LEGENDA")
    cw, ch = 66.0, 29.0
    ncol = int((x1 - x0 - 16.0) // cw)
    for i, (title, fn) in enumerate(cells):
        r, cc = divmod(i, ncol)
        cx = x0 + 8.0 + cc * cw
        cy = top - 4.0 - (r + 1) * ch
        sh.rect(cx, cy, cx + cw, cy + ch, layer="R-LEGENDA", pen=0.18)
        sh.text((cx + 1.5, cy + ch - 3.5), title, 2.0, layer="R-LEGENDA")
        fn(sh, np.array([cx + cw / 2, cy + ch / 2 - 2.5]))
    ll = lines_legend(sh, lg[2] + 8.0, y1 - 14.0)
    lettering_sample(sh, lg[2] + 8.0, ll[1] - 10.0, heights=(1.8, 2.5, 3.5, 5.0))
    plot.add_control_marks(sh)
    files = sh.save(OUT / "DEMO-03_legendy")
    return sh, files


# ==================================================================================================== uruchomienie
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {}
    sh_a, vp_a, fa = demo_plan()
    sh_b, vp_b, fb = demo_section()
    sh_c, fc = demo_legend()
    for key, sh, files in (("DEMO-01", sh_a, fa), ("DEMO-02", sh_b, fb), ("DEMO-03", sh_c, fc)):
        report[key] = {"pliki": files, "png": plot.check_png(files["png"], sh)}
    # kontrola skali: oś A → oś B (4,20 m w 1:50 = 84,0 mm) — linia osi w PDF
    # kontrola skali: lico ocieplenia ściany północnej (8,08 m w 1:50 = 161,6 mm) — odcinek konturu w PDF
    x_min, x_max, y_max = AX["A"] - F_EXT, AX["C"] + F_EXT, AY["2"] + F_EXT
    report["DEMO-01"]["skala_lico_N"] = plot.check_scale(fa["pdf"], sh_a, vp_a, (x_min, y_max), (x_max, y_max))
    report["DEMO-01"]["skala_os_B"] = plot.check_scale(fa["pdf"], sh_a, vp_a, *vp_a.meta_axis)
    vol = plot.volume([sh_a, sh_b, sh_c], OUT / "DEMO_tom.pdf", "Tom próbny — silnik rysunkowy")
    report["tom"] = vol
    (OUT / "raport_kontroli.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str),
                                             encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
