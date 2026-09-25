"""Generator DETALI architektonicznych (projekt techniczny, PT) — typ widoku `detal` rejestru `sheets.VIEW_TYPES`.

Widok: ``{typ: detal, wezel: WZ-08}`` albo ``{typ: detal, rodzaj: cokol}``, podziałka 1:10 lub 1:5 (``skala``).
Geometria warstw z przegród modelu (`detale_geom.Detal.stos_v/stos_h` — grubości, materiały, kliny), kreskowania
materiałów wg PN-B-01030:2000 (aktualna) i PN-EN ISO 128-3:2023 (zastąpiła wycofane PN-ISO 128-50), opisy warstw
odnośnikami w kolumnach poza rysunkiem (od zewnątrz do wewnątrz, grubości w mm — bez kolizji z założenia układu:
kolumny poza obrysem treści, bloki opisów układane bez nakładania), wymiary [mm], rzędne, spadki, obróbki
z kapinosami, taśmy i membrany; zasada **„4 linii”** kolorami: hydroizolacja — niebieska, szczelność powietrzna —
czerwona przerywana, paroizolacja — fioletowa, izolacja cieplna — obrys pomarańczowy, z oceną „ciągłość zachowana /
uwaga” (karta mostka + ciągłość linii na rysunku); w polu opisu ψ i f_Rsi z karty mostka
(`projekt/08_obliczenia/mostki/zestawienie_mostkow.json`).

Rodzaje detali — `detale_katalog.RODZAJE` (id węzła → rodzaj: `detale_katalog.WEZEL_RODZAJ`). Raport modułu (kontrola
grubości z przegrodami modelu, kolizje opisów, ciągłość linii) — `raport_detali()`; zapisywany do pliku
`wspolne.raport_detali` konfiguracji arkuszy przy każdym wygenerowanym detalu.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, fmt, styles
from ..draft import text as T
from ..draft.core import PLine, PText, Viewport, text_items
from ..draft.elements import CutSet
from ..draft.geom import polygons_of
from .common import IR_MATS, hatch_code
from .detale_geom import CIENKA, DET_MATS, Detal
from .sheets import register_view

ROOT = Path(__file__).resolve().parents[3]
H_OPIS = 1.8          # [mm] pismo opisów warstw (PN-EN ISO 3098: 1,8)
WIERSZ = 3.1          # [mm] odstęp wierszy opisu
H_WYM = 1.8           # [mm] liczby wymiarowe detalu

# ---------------------------------------------------------------------------------------------- warstwy rysunku
KOLORY = {"H": "#1565c0", "S": "#d32f2f", "P": "#7b1fa2", "I": "#ef6c00", "W": "#455a64", "G": "#757575",
          "T_in": "#7b1fa2", "T_out": "#1565c0"}
_WARSTWY = [  # nazwa, opis, rola, rodzaj linii, ACI, kolor wydruku, z
    ("A-DET-HYDRO", "Detal — hydroizolacja / ochrona przed wodą (linia niebieska)", "gruba", "CIAGLA", 5, KOLORY["H"], 24),
    ("A-DET-SZCZEL", "Detal — szczelność powietrzna (czerwona przerywana)", "srednia", "KRESKOWA", 1, KOLORY["S"], 24),
    ("A-DET-PARO", "Detal — paroizolacja / kontrola pary (fioletowa)", "srednia", "CIAGLA", 6, KOLORY["P"], 24),
    ("A-DET-IZOL", "Detal — obrys izolacji cieplnej (pomarańczowy)", "srednia", "CIAGLA", 30, KOLORY["I"], 23),
    ("A-DET-TASMA", "Detal — taśmy uszczelniające (paroszczelne / paroprzepuszczalne)", "gruba", "CIAGLA", 6, None, 25),
    ("A-DET-MEMBRANY", "Detal — membrany wiatroizolacyjne, włókniny, bariery", "cienka", "PUNKTOWA_KROTKA", 8,
     KOLORY["W"], 23),
    ("A-DET-OBROBKI", "Detal — obróbki blacharskie, okapniki, rynny", "srednia", "CIAGLA", 7, None, 23),
    ("A-DET-PRZERWA", "Detal — linie przerwania", "cienka", "CIAGLA", 8, None, 22),
    ("A-DET-OPIS", "Detal — pole opisu (wyniki mostków, ocena 4 linii)", "cienka", "CIAGLA", 2, None, 26),
]
for _n, _o, _r, _lt, _aci, _rgb, _z in _WARSTWY:
    styles.LAYERS.setdefault(_n, styles.LayerDef(_n, _o, _r, _lt, _aci, _rgb, True, _z))
for _k, (_nm, _h, _kind, _lam) in DET_MATS.items():          # nazwy materiałów detali w legendzie kreskowań
    IR_MATS.setdefault(_k, (_nm, "#d0d0d0", _h))

# pióra [mm] (szereg ISO 128-2) i rodzaje linii 4 linii / taśm
STYL = {"H": ("A-DET-HYDRO", 0.7, "CIAGLA"), "S": ("A-DET-SZCZEL", 0.5, "KRESKOWA"),
        "P": ("A-DET-PARO", 0.5, "CIAGLA"), "W": ("A-DET-MEMBRANY", 0.35, "PUNKTOWA_KROTKA"),
        "G": ("A-DET-MEMBRANY", 0.25, "KRESKOWA_DROBNA"), "T_in": ("A-DET-TASMA", 1.0, "CIAGLA"),
        "T_out": ("A-DET-TASMA", 1.0, "KROPKOWA")}
LEGENDA_4 = [("H", "hydroizolacja / izolacja przeciwwodna i przeciwwilgociowa (ochrona przed wodą)"),
             ("S", "warstwa szczelności powietrznej (tynk wewn., płyta ŻB, OSB, membrana, taśmy)"),
             ("P", "paroizolacja / kontrola pary (folia, papa z Al, membrana sd ≥ 10 m)"),
             ("I", "izolacja cieplna — obrys ciągłej warstwy izolacji (test „ołówka”)"),
             ("T_in", "taśma paroszczelna (od wewnątrz — ciepły montaż)"),
             ("T_out", "taśma paroprzepuszczalna / uszczelnienie zewnętrzne (ciepły montaż, próg)"),
             ("W", "membrana wiatroizolacyjna paroprzepuszczalna"),
             ("G", "geowłóknina, bariera przeciwkorzenna, mata drenażowa")]

KIND_CUT = {"konstr": "konstr", "izol": "izol", "wyk": "wyk", "warstwa": "warstwa", "grunt": "grunt", "stal": "stal",
            "dzial": "dzial"}


def _hc(model, mat: str) -> str:
    if mat in DET_MATS:
        return DET_MATS[mat][1]
    return hatch_code(model, mat)


def _okno(det: Detal):
    if det.okno is None:
        return None
    return box(*det.okno)


def rysuj_elementy(vp: Viewport, det: Detal) -> dict:
    """Elementy przecięte (kreskowanie + kontury), warstwy cienkie, linie 4 linii, taśmy, obróbki, obrys izolacji.
    Zwraca {hatch_mats, izolacja (geometria), linie (rodzaj → [LineString])}."""
    m = det.model
    ok = _okno(det)
    cs = CutSet()
    hm: dict = {}
    for i, c in enumerate(det.czesci):
        g = c.poly if ok is None else c.poly.intersection(ok)
        if g.is_empty or g.area < 1e-10:
            continue
        hc = _hc(m, c.mat)
        cs.add(g, hc, KIND_CUT.get(c.kind, "warstwa"), priority=100 + i, axis=c.os, group=c.grupa or c.mat)
        hm.setdefault(hc, [])
        if c.mat not in hm[hc]:
            hm[hc].append(c.mat)
    res = cs.draw(vp, merge_thin_mm=0.0)
    # obrys izolacji cieplnej (pomarańczowy) — suma elementów izolacyjnych po rozstrzygnięciu nakładania
    iz = [g for it, g in res if it.kind == "izol"]
    izol = unary_union(iz) if iz else Polygon()
    if not izol.is_empty:
        inset = izol.buffer(-0.45 * vp.k, join_style=2)
        for pg in polygons_of(inset):
            vp.geom(pg, "A-DET-IZOL", pen=0.5, color=KOLORY["I"], z=23.5)
    linie: dict = {}
    def _lin(rodz, P, ly=None):
        if ok is not None:
            g = LineString(P).intersection(ok)
            parts = [np.asarray(a.coords) for a in getattr(g, "geoms", [g]) if not a.is_empty and a.length > 0]
        else:
            parts = [np.asarray(P)]
        ly_, pen, lt = STYL[rodz]
        for a in parts:
            vp.polyline(a, ly or ly_, pen=pen, lt=lt, color=KOLORY.get(rodz), z=24.5 if rodz in "HSP" else 24.0)
            linie.setdefault(rodz, []).append(LineString(a))
    for P, mat, rodz, _op in det.cienkie:
        _lin(rodz if rodz in STYL else "G", P)
    for rodz, P, _op in det.linie:
        _lin(rodz, P)
    for P, _op in det.obrobki:
        vp.polyline(P, "A-DET-OBROBKI", pen=0.5, color="#000000", z=24.2)
    for p1, p2 in det.przerwy:
        linia_przerwania(vp, p1, p2)
    return {"hatch_mats": hm, "izolacja": izol, "linie": linie}


def linia_przerwania(vp: Viewport, p1, p2, amp_mm: float = 2.0):
    """Linia przerwania (cienka z zygzakiem w środku, PN-EN ISO 128-2 — linia 01.1 z zygzakiem)."""
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = B - A
    L = float(np.linalg.norm(d))
    if L <= 0:
        return
    u = d / L
    n = np.array([-u[1], u[0]])
    k = vp.k
    e = 2.0 * k
    M = (A + B) / 2
    a = amp_mm * k
    pts = [A - u * e, M - u * a, M - u * a * 0.3 + n * a, M + u * a * 0.3 - n * a, M + u * a, B + u * e]
    vp.polyline(pts, "A-DET-PRZERWA", pen=0.25, color="#000000", z=24.0)


def rysuj_adnotacje(vp: Viewport, det: Detal):
    """Wymiary [mm], rzędne, spadki, znaki (poziom wody, strzałki)."""
    for pts, at, kier, labels in det.wymiary:
        dims.dim_chain(vp, pts, at, kier, unit_="mm", h=H_WYM, labels=labels)
    for pt, z, kind, strona, tekst in det.rzedne:
        dims.level_section(vp, pt, det.z0 + z, kind=kind, side=strona, text=tekst, h=H_WYM)
    for a, b, pct, tekst in det.spadki:
        dims.slope(vp, a, b, pct, text=tekst, h=H_WYM)
    for rodz, d in det.znaki:
        if rodz == "woda":           # poziom wody / nawierzchni — trójkąt odwrócony z kreskami (PN-B-01025)
            P = np.asarray(d["pt"], float)
            k = vp.k
            s = 1.8 * k
            vp.polygon([P, P + np.array([-s, s * 1.2]), P + np.array([s, s * 1.2])], "A-SYMBOLE", pen=0.25,
                       color=KOLORY["H"])
            for j, w in enumerate((1.0, 0.6)):
                y = P[1] - (0.9 + 0.8 * j) * k
                vp.line((P[0] - s * w, y), (P[0] + s * w, y), "A-SYMBOLE", pen=0.25, color=KOLORY["H"])
            if d.get("tekst"):
                vp.text(P + np.array([2.6 * k, 0.4 * k]), d["tekst"], H_WYM, layer="A-SYMBOLE", color=KOLORY["H"],
                        mask=0.3)
        elif rodz == "strzalka":      # kierunek spływu / przepływu
            dims.slope(vp, d["a"], d["b"], None, text=d.get("tekst", ""), h=H_WYM)


# ---------------------------------------------------------------------------------------------- opisy (odnośniki)
def _zawin(s: str, w_mm: float, h: float = H_OPIS) -> list[str]:
    if T.width(s, h) <= w_mm:
        return [s]
    out, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if T.width(t, h) > w_mm and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def rysuj_opisy(vp: Viewport, det: Detal, bbox, szer_mm: float = 62.0) -> list:
    """Odnośniki opisów w kolumnach poza obrysem treści `bbox` (x0, y0, x1, y1 [m]). Bloki układane od góry według
    rzędnej wyjścia odnośnika, bez nakładania (odstęp ≥ 1,2 mm); kolano odnośnika na krawędzi treści + 3 mm.
    Zwraca [(tekst, prostokąt napisu)] do kontroli kolizji."""
    k = vp.k
    x0, y0, x1, y1 = bbox
    boxes = []
    for strona in ("R", "L"):
        its = [o for o in det.opisy if o.strona == strona]
        if not its:
            continue
        bloki = []
        for o in its:
            wiersze = []
            for t in o.teksty:
                wiersze += [(t, j) for j, t in enumerate(_zawin(t, szer_mm))]
            y_w = (o.wyjscie[1] if o.wyjscie else o.pts[0][1])
            n = len(wiersze) + (1 if o.tytul else 0)
            bloki.append(dict(o=o, wiersze=wiersze, y=y_w, h=n * WIERSZ * k))
        bloki.sort(key=lambda b: -b["y"])
        # układ 1D: góra bloku = y wyjścia + pół wiersza, bez nakładania — przesuwanie w dół, potem korekta w górę
        gap = 1.2 * k
        tops = []
        for b in bloki:
            t = b["y"] + 0.5 * WIERSZ * k
            if tops and t > tops[-1] - bloki[len(tops) - 1]["h"] - gap:
                t = tops[-1] - bloki[len(tops) - 1]["h"] - gap
            tops.append(t)
        # przesunięcie całej kolumny w górę, gdy średnio poniżej wyjść (równoważenie)
        sr = float(np.mean([tops[i] - (b["y"] + 0.5 * WIERSZ * k) for i, b in enumerate(bloki)]))
        if sr < 0:
            lift = min(-sr, max(0.0, (y1 + 4 * k) - tops[0]))
            tops = [t + lift for t in tops]
        x_k = (x1 + 3.0 * k) if strona == "R" else (x0 - 3.0 * k)
        x_c = (x1 + 9.0 * k) if strona == "R" else (x0 - 9.0 * k)
        sg = 1.0 if strona == "R" else -1.0
        for b, top in zip(bloki, tops):
            o = b["o"]
            P = [np.asarray(p, float) for p in o.pts]
            with vp.on("A-OPISY"):
                if len(P) > 1:
                    vp.polyline(P, pen=0.18)
                for p in P:
                    vp.dot(p, 0.7, "A-OPISY")
                start = P[0]
                path = [start]
                if o.wyjscie is not None:
                    path.append(np.asarray(o.wyjscie, float))
                y_e = path[-1][1]
                path.append(np.array([x_k, y_e]))
                y_txt = top - (1.0 + (1 if o.tytul else 0)) * WIERSZ * k + 0.9 * k
                path.append(np.array([x_c - sg * 1.5 * k, y_txt + 0.5 * H_OPIS * k]))
                path.append(np.array([x_c, y_txt + 0.5 * H_OPIS * k]))
                vp.polyline(path, pen=0.18)
                y = top - WIERSZ * k + 0.9 * k
                if o.tytul:
                    p = vp.text((x_c + sg * 1.0 * k, y), o.tytul, H_OPIS, ha="left" if sg > 0 else "right",
                                style="bold")
                    boxes.append((o.tytul, Polygon(text_items(p, k)[1])))
                    y -= WIERSZ * k
                for t, j in b["wiersze"]:
                    xt = x_c + sg * (1.0 + (2.0 if j else 0.0)) * k
                    p = vp.text((xt, y), t, H_OPIS, ha="left" if sg > 0 else "right")
                    boxes.append((t, Polygon(text_items(p, k)[1])))
                    y -= WIERSZ * k
    return boxes


def rysuj_pole_opisu(vp: Viewport, det: Detal, bbox, wiersze: list[tuple[str, str | None]]):
    """Pole opisu pod rysunkiem: wyniki mostka (ψ, f_Rsi) i ocena 4 linii (kolor statusu)."""
    k = vp.k
    x0, y0 = bbox[0], bbox[1] - 7.0 * k
    for j, (t, kol) in enumerate(wiersze):
        vp.text((x0, y0 - j * 3.2 * k), t, H_OPIS, layer="A-DET-OPIS", color=kol, style="bold" if j == 0 else "normal")
