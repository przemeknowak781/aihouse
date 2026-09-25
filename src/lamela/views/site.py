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
