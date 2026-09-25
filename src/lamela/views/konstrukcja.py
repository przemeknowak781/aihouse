"""RYSUNKI KONSTRUKCYJNE (PT-BO) generowane z modelu i obliczeń statycznych — typy widoków rejestru ``sheets``:

* ``k_fundamenty`` — rzut fundamentów 1:50: płyta fundamentowa (lub ławy/stopy wg ``fundamenty.elementy``), żebra
  i pogrubienia (linia kreskowa — pod płytą), ściany parteru (obrys), izolacja obwodowa przeciwprzemarzaniowa
  (PN-EN ISO 13793), przejścia instalacyjne (piony, wpusty, przyłącza z ``instalacje.yaml``/``dzialka.yaml``),
  uziom fundamentowy (otok, przewód wyrównawczy funkcjonalny, wyprowadzenia — PN-EN 62305-3, PN-HD 60364-5-54),
  rzędne spodu/wierzchu, osie i wymiary, ślady przekrojów charakterystycznych,
* ``k_strop`` — rzut konstrukcji stropu/stropodachu (grupa płyt liczona wspólnie) 1:50: pozycje obliczeniowe
  (numeracja ``pozycje.py``), płyty (grubość, beton, kierunek pracy pól), ściany i słupy pod płytą (przekrój),
  belki/podciągi/nadproża/wieńce, wsporniki z łącznikami termoizolacyjnymi (siły m_Ed, v_Ed z obliczeń), otwory,
  ściany-tarcze (jeżeli analiza je wykryła),
* ``k_zbrojenie`` — rysunki zbrojenia wg PN-EN ISO 3766: płyty stropowe (warstwa dolna / górna na osobnych
  arkuszach), płyta fundamentowa z żebrami i pogrubieniami, belki i nadproża (widok, przekroje, wyciąg prętów),
  schody, wsporniki; ZESTAWIENIE STALI (kolumna opisowa) — zbrojenie wyłącznie z wyników biblioteki
  (``konstrukcja_dane``) z kontrolą A_s,prov ≥ A_s,req (raport ``kontrola_zbrojenia.md``),
* ``k_przekroj`` — przekroje i szczegóły 1:20–1:10 (węzeł wspornika z łącznikiem termoizolacyjnym, wieniec, oparcie
  stropu na murze silikatowym, żebro płyty fundamentowej, pogrubienie pod słupem).

Geometria wyłącznie z ``ctx.model`` (``budynek.yaml``), wyniki — ``lamela.obliczenia.konstrukcja`` (analiza
uruchamiana raz na kontekst). Konfiguracja arkuszy: ``model/arkusze_bo.yaml``.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, fmt, hatch as H, symbols as S
from ..draft.core import Viewport
from ..draft.sheet import table, wrap
from ..draft.text import width as text_w
from . import konstrukcja_dane as KD
from .common import Placer, ViewContext, hatch_code, material_name
from .sheets import register_view

L_OBR = "K-KONSTR"          # kontury elementów
L_ZBR = "K-ZBROJENIE"       # pręty
L_OPI = "K-ZBROJENIE-OPIS"  # opisy prętów
L_WYM = "K-WYMIARY"
L_OSI = "K-OSIE"
L_OPS = "A-OPISY"
PEN_PRET = 0.7              # pręt reprezentatywny na rzucie 1:50 [mm]
PEN_PRET_DET = 0.5
NORMY = ("PN-EN 1992-1-1:2008 + NA:2010 (+AC, A1:2015)", "PN-EN 1990:2004 + NA", "PN-EN 1991 + NA",
         "PN-EN 1996-1-1 + NA", "PN-EN 1997-1 + NA", "PN-EN 13670:2011", "PN-EN ISO 3766:2006", "PN-EN 10080",
         "PN-H-93220:2018-02 (B500SP)", "PN-EN 206+A2:2021-08", "PN-B-06265:2022-08")


@dataclass
class KResult:
    notes: list = field(default_factory=list)
    column_blocks: list = field(default_factory=list)
    hatch_mats: dict = field(default_factory=dict)
    north: bool = False
    rooms: list = field(default_factory=list)
    units_note: str | None = None


def _pl(x: float, nd: int = 2) -> str:
    return fmt.num(x, nd)


def _cm(x_m: float) -> str:
    """Długość w cm (liczba całkowita lub z połową)."""
    v = x_m * 100.0
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}".replace(".", ",")


def _nr_poz(c, pos, nr: int, h: float = 2.5, layer: str = L_OPI):
    """Numer pozycji pręta w okręgu (PN-EN ISO 3766 p. 5.2 — numer pozycji wyróżniony)."""
    S.tag(c, pos, str(nr), shape="circle", r_mm=2.6 if nr < 10 else 3.0, h=h, layer=layer, pen="cienka")


def _hm_add(res: KResult, hc: str, mat: str):
    res.hatch_mats.setdefault(hc, [])
    if mat not in res.hatch_mats[hc]:
        res.hatch_mats[hc].append(mat)


# ------------------------------------------------------------------------------------------------ kolumna: bloki
def blok_legendy(pozycje: list, tytul: str = "OZNACZENIA NA RYSUNKU"):
    """Legenda symboli rysunku konstrukcyjnego: [(rodzaj, opis)], rodzaj: pret | pret_hak | rozklad | kreskowa |
    punktowa | naroze | lacznik | uziom | przejscie | slup | poz | tekst."""
    def fn(sh, x, y, w):
        with sh.on("R-LEGENDA"):
            sh.text((x, y - 3.5), tytul, 3.5, style="bold")
            yy = y - 9.0
            for rodz, opis in pozycje:
                cx = x + 1.0
                if rodz in ("pret", "pret_hak"):
                    sh.line((cx, yy + 0.9), (cx + 12, yy + 0.9), pen=0.5)
                    if rodz == "pret_hak":
                        sh.line((cx + 12, yy + 0.9), (cx + 12, yy - 0.8), pen=0.5)
                elif rodz == "rozklad":
                    sh.line((cx + 6, yy - 1.2), (cx + 6, yy + 3.0), pen=0.18)
                    for t in (yy - 1.2, yy + 3.0):
                        sh.line((cx + 5.0, t - 0.7), (cx + 7.0, t + 0.7), pen=0.18)
                    sh.circle((cx + 6, yy + 0.9), 0.6, pen=0.18)
                    sh.line((cx, yy + 0.9), (cx + 12, yy + 0.9), pen=0.5)
                elif rodz in ("kreskowa", "punktowa", "kreskowa_gruba"):
                    sh.line((cx, yy + 0.9), (cx + 12, yy + 0.9), pen=0.5 if rodz == "kreskowa_gruba" else 0.25,
                            lt="KRESKOWA" if rodz.startswith("kreskowa") else "PUNKTOWA")
                elif rodz == "naroze":
                    sh.rect(cx + 3, yy - 1.2, cx + 9, yy + 3.0, pen=0.25, lt="KRESKOWA_DROBNA")
                    sh.line((cx + 3, yy - 1.2), (cx + 9, yy + 3.0), pen=0.18)
                elif rodz == "lacznik":
                    sh.fill([(cx, yy), (cx + 12, yy), (cx + 12, yy + 1.8), (cx, yy + 1.8)], "R-LEGENDA", "#9a9a9a")
                    sh.rect(cx, yy, cx + 12, yy + 1.8, pen=0.25)
                elif rodz == "uziom":
                    sh.line((cx, yy + 0.9), (cx + 12, yy + 0.9), pen=0.5, lt="KRESKOWA", color="#b0006a")
                elif rodz == "wyrownawczy":
                    sh.line((cx, yy + 0.9), (cx + 12, yy + 0.9), pen=0.35, lt="PUNKTOWA", color="#b0006a")
                elif rodz == "zacisk":
                    sh.circle((cx + 6, yy + 0.9), 1.3, pen=0.35, color="#b0006a")
                    sh.line((cx + 5.1, yy), (cx + 6.9, yy + 1.8), pen=0.35, color="#b0006a")
                elif rodz == "przejscie":
                    sh.circle((cx + 6, yy + 0.9), 1.5, pen=0.35)
                    sh.line((cx + 4.5, yy + 0.9), (cx + 7.5, yy + 0.9), pen=0.18)
                    sh.line((cx + 6, yy - 0.6), (cx + 6, yy + 2.4), pen=0.18)
                elif rodz == "slup":
                    sh.fill([(cx + 4.5, yy - 0.6), (cx + 7.5, yy - 0.6), (cx + 7.5, yy + 2.4), (cx + 4.5, yy + 2.4)],
                            "R-LEGENDA", "#000000")
                elif rodz == "poz":
                    S.tag(sh, (cx + 6, yy + 0.9), "3", shape="circle", r_mm=2.4, h=2.5, layer="R-LEGENDA")
                elif rodz == "izol":
                    sh.rect(cx, yy - 0.6, cx + 12, yy + 2.4, pen=0.25, lt="KRESKOWA")
                ls = wrap(opis, w - 18.0, 1.8)
                for j, s in enumerate(ls):
                    sh.text((x + 16, yy + 0.2 - j * 2.7), s, 1.8)
                yy -= 2.7 * len(ls) + 2.6
        return yy + 1.0
    return fn


def _szkic_ksztaltu(sh, x, y, w, h, ksztalt: str):
    """Miniatura kształtu pręta (PN-EN ISO 3766) w komórce tabeli: x, y — lewy dolny róg, w × h [mm]."""
    pen = 0.35
    cy = y + h / 2
    if ksztalt == "00":
        sh.line((x, cy), (x + w, cy), pen=pen)
    elif ksztalt == "11":
        sh.polyline([(x, cy + h * 0.3), (x + w, cy + h * 0.3), (x + w, cy - h * 0.3)], pen=pen)
    elif ksztalt == "21":
        sh.polyline([(x, cy - h * 0.3), (x, cy + h * 0.3), (x + w, cy + h * 0.3), (x + w, cy - h * 0.3)], pen=pen)
    elif ksztalt == "51":
        sh.rect(x + w * 0.2, cy - h * 0.32, x + w * 0.8, cy + h * 0.32, pen=pen)
        sh.line((x + w * 0.2, cy + h * 0.32), (x + w * 0.34, cy + h * 0.12), pen=pen)
    elif ksztalt == "26":
        sh.polyline([(x, cy - h * 0.3), (x + w * 0.3, cy - h * 0.3), (x + w * 0.75, cy + h * 0.3), (x + w, cy + h * 0.3)],
                    pen=pen)
    else:
        sh.line((x, cy), (x + w, cy), pen=pen)


def _wym_txt(p: KD.Pret) -> str:
    lit = "abcdef"
    if p.ksztalt == "00":
        return f"a={p.wym[0] / 10:g}"
    return " ".join(f"{lit[i]}={v / 10:g}" for i, v in enumerate(p.wym))


def blok_zestawienia(zest: KD.Zestawienie, tytul: str, stopka: list[str] | None = None, masa_calk: float | None = None):
    """ZESTAWIENIE STALI (PN-EN ISO 3766): poz., Ø, kształt (szkic + wymiary [cm]), długość, liczba, długości łączne
    wg średnic, masa jednostkowa, masa [kg]; stopka — klasa stali, beton, otulina, klasa ekspozycji."""
    def fn(sh, x, y, w):
        if not zest.prety:
            return y
        sr = zest.srednice()
        wd = 13.0 if len(sr) <= 5 else max(9.0, (w - 100.0) / len(sr))
        w_ks = w - (10 + 9 + 15 + 12 + 11) - wd * len(sr)
        cols = [("Poz.", 10.0), ("Ø\n[mm]", 9.0), ("Kształt ISO 3766,\nwymiary [cm]", w_ks), ("Dług.\n[cm]", 15.0),
                ("Liczba\n[szt.]", 12.0), ("Elem.", 11.0)] + [(f"Ø{d}\n[m]", wd) for d in sr]
        rows = []
        for p in zest.prety:
            rows.append([str(p.nr), str(p.fi), "", f"{p.L_mm / 10:g}", str(p.n), p.element.split(",")[0][:6]]
                        + [_pl(p.dl_calk, 2) if p.fi == d else "" for d in sr])
        Ls = zest.dl_wg_srednic()
        ms = zest.masy()
        rows.append(["", "", "Długość całkowita [m]", "", "", ""] + [_pl(Ls[d], 1) for d in sr])
        rows.append(["", "", "Masa jednostkowa [kg/m]", "", "", ""] + [_pl(KD.masa_preta(d), 3) for d in sr])
        rows.append(["", "", "Masa [kg]", "", "", ""] + [_pl(ms[d], 1) for d in sr])
        rows.append(["", "", f"RAZEM stal {KD.GATUNEK} [kg]", "", "", ""] + [""] * (len(sr) - 1) + [_pl(zest.masa, 1)])
        rh = 4.5
        r = table(sh, x, y - 7.0, cols, rows, h=1.8, row_h=rh, title=tytul, header_h=7.0,
                  align=["center", "center", "left", "right", "right", "center"] + ["right"] * len(sr))
        # szkice kształtów + wymiary w kolumnie „Kształt”
        xk = x + 19.0
        yy = y - 7.0 - 7.0
        with sh.on("R-OPISY"):
            for p in zest.prety:
                _szkic_ksztaltu(sh, xk + 1.2, yy - rh + 0.9, 7.0, rh - 1.8, p.ksztalt)
                sh.text((xk + 10.0, yy - rh / 2), f"{p.ksztalt}: {_wym_txt(p)}", 1.8, va="middle")
                yy -= rh
        yb = r[1]
        lines = list(stopka or [])
        if masa_calk is not None:
            lines.append(f"Masa stali całego elementu (warstwy dolna + górna): {_pl(masa_calk, 1)} kg.")
        for s in lines:
            for ln in wrap(s, w, 1.8):
                yb -= 2.8
                sh.text((x, yb), ln, 1.8)
        return yb - 1.0
    return fn
