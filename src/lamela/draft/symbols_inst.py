"""Symbole instalacyjne.

* Elektryczne wg PN-EN 60617 (IEC 60617) — oznaczenia na planach instalacji (rzutach): gniazda, łączniki, oprawy,
  rozdzielnice, puszki, czujniki, dzwonek, wideodomofon, gniazda teletechniczne, uziemienie, SPD.
* Sanitarne wg praktyki (PN-EN ISO 10628 dla armatury, PN-B-01700 dla urządzeń) — piony, zawory, wodomierz,
  filtr, rozdzielacz, pompa, zasobnik, pompa ciepła, rury wg mediów, czyszczak, wpust, rewizja, kratki,
  anemostaty, czerpnia/wyrzutnia, rekuperator, grzejnik, pętle ogrzewania podłogowego.

Symbole umowne mają rozmiar w mm papieru (parametr ``s_mm``); ``rot`` — kierunek "od ściany do pomieszczenia"
(dla symboli przyściennych) lub kierunek przepływu (armatura).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, MultiLineString, Polygon

from . import text as T
from .dims import arrowhead
from .geom import Xf, arr, circle_pts, dir_deg, lines_of, perp, rect_c, rect_pts, to_polygon, unit

__all__ = [
    "socket", "switch", "light", "light_linear", "panel", "junction_box", "motion_sensor", "bell", "videophone",
    "data_outlet", "earth", "spd", "riser", "valve", "check_valve", "water_meter", "filter_", "manifold", "pump",
    "tank", "heat_pump", "pipe", "cleanout", "floor_drain", "inspection", "grille", "anemostat", "air_terminal",
    "recuperator", "radiator", "floor_heating", "MEDIA", "media",
]


def _X(pos, rot_deg, s=1.0):
    return Xf.make(np.asarray(pos, float), rot_deg - 90.0, s)


# ================================================================================================ elektryka
def socket(c, pos, rot=90.0, n: int = 1, earth: bool = True, ip44: bool = False, phases: int = 1,
           s_mm: float = 3.0, layer: str = "E-GNIAZDA", label: str | None = None):
    """Gniazdo wtyczkowe (PN-EN 60617-11: 11-13-01 symbol ogólny — łuk z doprowadzeniem w wierzchołku;
    11-13-04 ze stykiem ochronnym — kreska styczna w wierzchołku łuku; 11-13-02 wielokrotne — kreska ukośna
    na doprowadzeniu z liczbą gniazd). ip44 — gniazdo bryzgoszczelne/hermetyczne (łuk zaczerniony — praktyka);
    phases=3 — gniazdo trójfazowe (opis 3~). pos — punkt na licu ściany, rot — kierunek od ściany."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    r = s * 0.5
    L1 = s * 0.45
    with c.on(layer):
        c.line(xf.pt(0, 0), xf.pt(0, L1))
        t = np.linspace(math.pi, 2 * math.pi, 25)
        pts = xf(np.column_stack([r * np.cos(t), L1 + r + r * np.sin(t)]))
        if ip44:
            c.fill(pts, layer, "#000000")
        c.polyline(pts)
        if earth:
            c.line(xf.pt(-r * 0.9, L1), xf.pt(r * 0.9, L1))
        if n > 1:
            y = L1 * 0.45
            c.line(xf.pt(-0.28 * s, y - 0.14 * s), xf.pt(0.28 * s, y + 0.14 * s), pen="cienka")
            c.text(xf.pt(0.38 * s, y + 0.1 * s), str(n), 1.8, 0.0, "left", "middle")
        lab = label if label is not None else ("3~" if phases == 3 else None)
        if lab:
            c.text(xf.pt(r + 0.5 * s, L1 + r), lab, 1.8, 0.0, "left", "middle")


def switch(c, pos, rot=90.0, kind: str = "1", ip44: bool = False, s_mm: float = 3.0, layer: str = "E-LACZNIKI"):
    """Łącznik (PN-EN 60617-11-14): kind '1' — jednobiegunowy, '2' — dwubiegunowy, 'swiecznikowy' (dwugrupowy),
    'schodowy' (przełącznik dwukierunkowy), 'krzyzowy', 'przycisk' (zwierny, np. dzwonkowy)."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    r = 0.22 * s
    C = (0.0, 0.55 * s)
    with c.on(layer):
        if ip44:
            c.fill(circle_pts(xf.pt(*C), r, 24), layer, "#000000")
        c.circle(xf.pt(*C), r)
        if kind == "przycisk":  # PN-EN 60617 11-14-10: dwa okręgi współśrodkowe
            c.circle(xf.pt(*C), r * 1.7)
            return

        def arm(a_deg, ticks, both=False):
            d = dir_deg(a_deg)
            p0 = np.array(C) + d * r
            p1 = np.array(C) + d * 1.05 * s
            c.line(xf.pt(*p0), xf.pt(*p1))
            n = perp(d)
            for i in range(ticks):
                q = p1 - d * (0.2 * s * i)
                c.line(xf.pt(*q), xf.pt(*(q + n * 0.28 * s)))
            if both:
                q0 = np.array(C) - d * r
                q1 = np.array(C) - d * 1.05 * s
                c.line(xf.pt(*q0), xf.pt(*q1))
                c.line(xf.pt(*q1), xf.pt(*(q1 - n * 0.28 * s)))

        if kind in ("1", "jednobiegunowy"):
            arm(45.0, 1)
        elif kind in ("2", "dwubiegunowy"):
            arm(45.0, 2)
        elif kind in ("swiecznikowy", "świecznikowy", "dwugrupowy"):
            arm(30.0, 1)
            arm(70.0, 1)
        elif kind in ("schodowy",):
            arm(45.0, 1, both=True)
        elif kind in ("krzyzowy", "krzyżowy"):
            arm(45.0, 1, both=True)
            arm(135.0, 1, both=True)
        else:
            raise ValueError(kind)


def light(c, pos, kind: str = "sufit", rot: float = 90.0, s_mm: float = 4.0, layer: str = "E-OSWIETLENIE",
          label: str | None = None):
    """Oprawa oświetleniowa (PN-EN 60617-11-15): 'sufit' — lampa, symbol ogólny: okrąg z krzyżykiem (11-15-03);
    'kinkiet' — wypust ścienny: krzyżyk z kreską przy ścianie (11-15-02); 'sciana' — oprawa ścienna: okrąg
    z krzyżykiem z kreską przy ścianie (praktyka); 'downlight' — oprawa wpuszczana (mały okrąg z kropką);
    'awaryjna' — punkt świetlny zasilany z obwodu specjalnego (duży krzyżyk, 11-15-11) w okręgu.
    Dla 'kinkiet'/'sciana' pos leży na licu ściany, rot — kierunek od ściany."""
    k = c.k
    R = s_mm * k / 2
    P = np.asarray(pos, float)
    if kind == "kinkiet":
        d = dir_deg(rot)
        n = perp(d)
        with c.on(layer):
            c.line(P - n * R * 0.6, P + n * R * 0.6)
            C = P + d * R * 0.7
            a = R * 0.5
            c.line(C - d * a - n * a, C + d * a + n * a)
            c.line(C - d * a + n * a, C + d * a - n * a)
            if label:
                c.text(C + np.array([R + 0.8 * k, R * 0.3]), label, 1.8)
        return
    with c.on(layer):
        if kind == "sciana":
            d = dir_deg(rot)
            n = perp(d)
            C = P + d * (R + 0.8 * k)
            c.line(P - n * R, P + n * R)
            c.line(P, C - d * R)
            P = C
        if kind == "downlight":
            c.circle(P, R * 0.6)
            c.dot(P, 0.9, layer)
        else:
            c.circle(P, R)
            a = R * 0.7071
            c.line(P + [-a, -a], P + [a, a])
            c.line(P + [-a, a], P + [a, -a])
            if kind == "awaryjna":
                t = np.linspace(0, math.pi, 20)
                c.fill(np.column_stack([P[0] + R * np.cos(t), P[1] + R * np.sin(t)]), layer, "#000000")
        if label:
            c.text(P + np.array([R + 0.8 * k, R * 0.3]), label, 1.8)


def light_linear(c, p1, p2, width_mm: float = 1.6, layer: str = "E-OSWIETLENIE", label: str | None = None,
                 body: bool = False):
    """Oprawa liniowa LED / świetlówkowa (PN-EN 60617 11-15-04: odcinek z poprzecznymi kreskami na końcach),
    długość rzeczywista p1–p2; body=True — dodatkowo obrys oprawy."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d) * width_mm * k / 2
    with c.on(layer):
        c.line(A, B, pen="srednia")
        c.line(A - n, A + n, pen="srednia")
        c.line(B - n, B + n, pen="srednia")
        if body:
            c.polygon([A - n * 0.6, B - n * 0.6, B + n * 0.6, A + n * 0.6], pen="b_cienka")
        if label:
            c.text((A + B) / 2 + n * 2.2, label, 1.8, math.degrees(math.atan2(d[1], d[0])), "center", "baseline")


def panel(c, pos, rot=90.0, w: float = 0.6, d: float = 0.15, label: str = "RG", layer: str = "E-ROZDZIELNICE"):
    """Rozdzielnica (prostokąt z przekątną i zaczernionym trójkątem) — wymiary rzeczywiste [m]."""
    xf = _X(pos, rot)
    with c.on(layer):
        q = xf(rect_pts(-w / 2, 0.0, w / 2, d))
        c.polygon(q, pen="srednia")
        c.fill([q[0], q[1], q[2]], layer, "#000000")
        c.text(xf.pt(0, d + 0.8 * c.k + 0.02), label, 2.5, 0.0, "center", "bottom", style="bold")


def junction_box(c, pos, s_mm: float = 1.6, layer: str = "E-ROZDZIELNICE"):
    """Puszka rozgałęźna (mały okrąg zaczerniony)."""
    c.fill(circle_pts(pos, s_mm * c.k / 2, 24), layer, "#000000")
    c.circle(pos, s_mm * c.k / 2, layer)


def motion_sensor(c, pos, rot=90.0, s_mm: float = 3.2, layer: str = "E-LACZNIKI", label: str = "PIR"):
    """Czujnik ruchu (półokrąg z promieniami — oznaczenie uproszczone) z opisem."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        t = np.linspace(0, math.pi, 20)
        c.polygon(xf(np.column_stack([0.45 * s * np.cos(t), 0.45 * s * np.sin(t)])))
        for a in (30, 90, 150):
            d = dir_deg(a)
            c.line(xf.pt(*(d * 0.6 * s)), xf.pt(*(d * 0.95 * s)), pen="cienka")
        c.text(xf.pt(0.0, 1.35 * s), label, 1.8, 0.0, "center", "middle")


def bell(c, pos, rot=90.0, s_mm: float = 3.0, layer: str = "E-TELETECH"):
    """Dzwonek (PN-EN 60617 08-10-06): półokrąg z podstawą."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        c.line(xf.pt(0, 0), xf.pt(0, 0.35 * s))
        t = np.linspace(math.pi, 2 * math.pi, 20)
        c.polyline(xf(np.column_stack([0.5 * s * np.cos(t), 0.35 * s + 0.5 * s + 0.5 * s * np.sin(t)])))
        c.line(xf.pt(-0.5 * s, 0.85 * s), xf.pt(0.5 * s, 0.85 * s))


def videophone(c, pos, rot=90.0, s_mm: float = 3.6, layer: str = "E-TELETECH", label: str = "WD"):
    """Unifon/monitor wideodomofonu (prostokąt z ekranem)."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-0.45 * s, 0.1 * s, 0.45 * s, 1.1 * s)))
        c.polygon(xf(rect_pts(-0.3 * s, 0.45 * s, 0.3 * s, 0.95 * s)), pen="b_cienka")
        c.text(xf.pt(0.0, 1.45 * s), label, 1.8, 0.0, "center", "middle")


def data_outlet(c, pos, rot=90.0, label: str = "RJ45", s_mm: float = 3.0, layer: str = "E-TELETECH"):
    """Gniazdo teletechniczne (PN-EN 60617 11-13-09): trzonek + „bramka” z oznaczeniem (RJ45, TV, SAT, TP)."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        c.line(xf.pt(0, 0), xf.pt(0, 0.4 * s))
        c.polyline(xf([[-0.5 * s, 0.9 * s], [-0.5 * s, 0.4 * s], [0.5 * s, 0.4 * s], [0.5 * s, 0.9 * s]]))
        c.text(xf.pt(0.0, 1.25 * s), label, 1.8, 0.0, "center", "middle")


def earth(c, pos, rot=-90.0, s_mm: float = 3.0, layer: str = "E-ODGROM", label: str | None = None):
    """Uziemienie (PN-EN 60617 02-15-01): trzonek + trzy kreski malejące. rot — kierunek trzonka (w dół = -90)."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        c.line(xf.pt(0, 0), xf.pt(0, 0.6 * s))
        for i, w in enumerate((0.6, 0.4, 0.2)):
            y = 0.6 * s + i * 0.18 * s
            c.line(xf.pt(-w * s, y), xf.pt(w * s, y))
        if label:
            c.text(xf.pt(0.8 * s, 0.8 * s), label, 1.8)


def spd(c, pos, rot=90.0, s_mm: float = 3.5, layer: str = "E-ROZDZIELNICE", label: str = "SPD T1+T2"):
    """Ogranicznik przepięć (SPD): prostokąt z łamaną (warystor) i przyłączem uziemienia."""
    k = c.k
    s = s_mm * k
    xf = _X(pos, rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-0.3 * s, 0.0, 0.3 * s, 1.0 * s)))
        c.polyline(xf([[-0.45 * s, 0.2 * s], [-0.15 * s, 0.2 * s], [0.15 * s, 0.8 * s], [0.45 * s, 0.8 * s]]))
        earth(c, xf.pt(0.0, 0.0), rot + 180.0, s_mm * 0.7, layer)
        c.text(xf.pt(0.55 * s, 0.5 * s), label, 1.8, 0.0, "left", "middle")


# ================================================================================================ sanitarne
MEDIA = {
    # kod: (warstwa, opis, rodzaj linii) — oznaczenia literowe mediów wg praktyki PL (R4 pkt 3.12), zawsze w legendzie
    "WZ": ("S-WODA", "Wz — woda zimna", None),
    "WC": ("S-CWU", "Wc — woda ciepła (CWU)", "KRESKOWA"),
    "CYRK": ("S-CYRK", "Cyrk — cyrkulacja CWU", "PUNKTOWA_KROTKA"),
    "KS": ("S-KANAL", "Ks — kanalizacja sanitarna", None),
    "KD": ("S-DESZCZ", "Kd — kanalizacja deszczowa", "KRESKA_DLUGA"),
    "Z": ("S-OGRZ", "Z — ogrzewanie, zasilanie", None),
    "P": ("S-OGRZ", "P — ogrzewanie, powrót", "KRESKOWA"),
    # rodzaje powietrza wg EN 16798-3 (kod literowy obowiązkowy, kolor pomocniczy)
    "ODA": ("S-WENT", "ODA — powietrze zewnętrzne (czerpane)", "PUNKTOWA_KROTKA"),
    "SUP": ("S-WENT", "SUP — powietrze nawiewane", None),
    "ETA": ("S-WENT", "ETA — powietrze wywiewane", "KRESKOWA"),
    "EHA": ("S-WENT", "EHA — powietrze wyrzutowe", "KRESKOWA"),
}
_MEDIA_ALIAS = {"W": "WZ", "C": "WC", "CY": "CYRK", "K": "KS", "WN": "SUP", "WW": "ETA"}


def media(code: str):
    c_ = code.upper()
    return MEDIA[_MEDIA_ALIAS.get(c_, c_)]


def pipe(c, pts, medium: str = "WZ", label: str | None = None, h: float = 2.5, label_at: float = 0.5,
         pen=None):
    """Przewód instalacji wg medium (warstwa i rodzaj linii z ``MEDIA``) z opisem nad przewodem (np. 'W PE-X 16×2')."""
    ly, _desc, lt = media(medium)
    P = arr(pts)
    c.polyline(P, ly, pen=pen, lt=lt)
    if label:
        ls = LineString(P)
        q = np.asarray(ls.interpolate(label_at, normalized=True).coords)[0]
        # kierunek odcinka w punkcie
        L = ls.length
        q2 = np.asarray(ls.interpolate(min(L, label_at * L + 0.01 * L)).coords)[0]
        q1 = np.asarray(ls.interpolate(max(0.0, label_at * L - 0.01 * L)).coords)[0]
        d = unit(q2 - q1)
        from .geom import readable_angle
        ang = readable_angle(math.degrees(math.atan2(d[1], d[0])))
        up = perp(dir_deg(ang))
        c.text(q + up * 0.8 * c.k, label, h, ang, "center", "baseline", ly)


def riser(c, pos, label: str | None = None, medium: str = "KS", s_mm: float = 2.6, h: float = 2.5):
    """Pion instalacyjny (okrąg + opis, np. „Pion K1 ∅110”)."""
    ly = media(medium)[0]
    R = s_mm * c.k / 2
    c.circle(pos, R, ly, pen="srednia")
    c.dot(pos, 0.7, ly)
    if label:
        c.text(np.asarray(pos) + np.array([R + 0.8 * c.k, R * 0.5]), label, h, 0.0, "left", "baseline", ly)


def valve(c, pos, rot=0.0, s_mm: float = 3.0, layer: str = "S-URZADZENIA", kind: str = "odcinający"):
    """Zawór (PN-EN ISO 10628): dwa trójkąty stykające się wierzchołkami (kierunek osi = rot);
    kind='kulowy' — z kółkiem w środku."""
    k = c.k
    s = s_mm * k / 2
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf([[-s, -0.6 * s], [-s, 0.6 * s], [0, 0]]))
        c.polygon(xf([[s, -0.6 * s], [s, 0.6 * s], [0, 0]]))
        if kind == "kulowy":
            c.fill(circle_pts(xf.pt(0, 0), 0.28 * s, 16), layer, "#000000")


def check_valve(c, pos, rot=0.0, s_mm: float = 3.0, layer: str = "S-URZADZENIA"):
    """Zawór zwrotny: symbol zaworu z zaczernionym trójkątem po stronie odpływu + strzałka kierunku przepływu."""
    k = c.k
    s = s_mm * k / 2
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf([[-s, -0.6 * s], [-s, 0.6 * s], [0, 0]]))
        tri = xf([[s, -0.6 * s], [s, 0.6 * s], [0, 0]])
        c.fill(tri, layer, "#000000")
        c.polygon(tri)
        a0, a1 = xf.pt(-s, 1.2 * s), xf.pt(s, 1.2 * s)
        c.line(a0, a1, pen="b_cienka")
        arrowhead(c, a1, a1 - a0, 1.4, 14, True, layer, pen="b_cienka")


def water_meter(c, pos, rot=0.0, s_mm: float = 4.0, layer: str = "S-URZADZENIA", label: str = "WM"):
    """Wodomierz (okrąg z oznaczeniem, przewód przechodzi przez środek)."""
    R = s_mm * c.k / 2
    with c.on(layer):
        c.fill(circle_pts(pos, R, 36), layer, "#ffffff", z=23.8)
        c.circle(pos, R, pen="srednia", z=23.9)
        c.text(pos, label, 1.8, 0.0, "center", "middle", z=30)


def filter_(c, pos, rot=0.0, s_mm: float = 3.6, layer: str = "S-URZADZENIA"):
    """Filtr (PN-EN ISO 10628): romb z linią kreskową wzdłuż przekątnej."""
    k = c.k
    s = s_mm * k / 2
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        q = xf([[-s, 0], [0, s], [s, 0], [0, -s]])
        c.fill(q, layer, "#ffffff", z=23.8)
        c.polygon(q, z=23.9)
        c.line(xf.pt(0, s), xf.pt(0, -s), lt="KRESKOWA_DROBNA", lt_scale=0.4, pen="b_cienka", z=23.9)


def manifold(c, pos, rot=0.0, n: int = 4, pitch_mm: float = 3.0, layer: str = "S-URZADZENIA", label: str | None = "R"):
    """Rozdzielacz (belka z ``n`` odejściami)."""
    k = c.k
    L = (n + 1) * pitch_mm * k
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(0, -0.6 * k, L, 0.6 * k)), pen="srednia")
        for i in range(n):
            x = (i + 1) * pitch_mm * k
            c.line(xf.pt(x, 0.6 * k), xf.pt(x, 2.4 * k))
        if label:
            c.text(xf.pt(L + 1.0 * k, 0), label, 1.8, 0.0, "left", "middle")


def pump(c, pos, rot=0.0, s_mm: float = 4.0, layer: str = "S-URZADZENIA"):
    """Pompa obiegowa (okrąg z trójkątem wskazującym kierunek tłoczenia)."""
    R = s_mm * c.k / 2
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.fill(circle_pts(pos, R, 36), layer, "#ffffff", z=23.8)
        c.circle(pos, R, z=23.9)
        c.polygon(xf([[-R * 0.55, R * 0.8], [-R * 0.55, -R * 0.8], [R, 0.0]]), z=23.9)


def tank(c, pos, d: float = 0.65, label: str = "CWU 300 l", layer: str = "S-URZADZENIA", h: float = 1.8):
    """Zasobnik/zbiornik pionowy w rzucie (okrąg o średnicy rzeczywistej d [m] + opis)."""
    with c.on(layer):
        c.circle(pos, d / 2, pen="srednia")
        c.circle(pos, d / 2 - 0.04, pen="b_cienka")
        c.text(pos, label, h, 0.0, "center", "middle")


def heat_pump(c, pos, rot=0.0, w: float = 1.10, d: float = 0.45, label: str = "PC", layer: str = "S-URZADZENIA",
              outdoor: bool = True):
    """Pompa ciepła powietrze–woda: jednostka zewnętrzna (prostokąt z wentylatorem) lub wewnętrzna."""
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-w / 2, 0, w / 2, d)), pen="srednia")
        if outdoor:
            r = min(w * 0.3, d * 0.42)
            c.circle(xf.pt(-w * 0.18, d / 2), r, pen="b_cienka")
            for a in range(0, 180, 45):
                v = dir_deg(a + xf.angle) * r
                q = xf.pt(-w * 0.18, d / 2)
                c.line(q - v, q + v, pen="b_cienka")
        c.text(xf.pt(w * 0.25, d / 2), label, 2.5, 0.0, "center", "middle", style="bold")


def cleanout(c, pos, rot=0.0, s_mm: float = 3.0, layer: str = "S-KANAL", label: str = "Cz"):
    """Czyszczak (rewizja na pionie/przewodzie kanalizacyjnym): kwadrat z przekątną + opis."""
    k = c.k
    s = s_mm * k / 2
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        q = xf(rect_pts(-s, -s, s, s))
        c.fill(q, layer, "#ffffff", z=23.8)
        c.polygon(q, pen="cienka", z=23.9)
        c.fill([q[0], q[1], q[2]], layer, "#000000", z=23.9)
        c.text(np.asarray(pos) + np.array([s + 0.8 * k, s]), label, 1.8, 0.0, "left", "bottom")


def floor_drain(c, pos, size: float = 0.15, layer: str = "S-KANAL", label: str | None = "WP"):
    """Wpust podłogowy (kratka kwadratowa z krzyżem) — wymiar rzeczywisty [m]."""
    P = np.asarray(pos, float)
    q = rect_c(P[0], P[1], size, size)
    with c.on(layer):
        c.polygon(q, pen="cienka")
        c.line(q[0], q[2], pen="b_cienka")
        c.line(q[1], q[3], pen="b_cienka")
        c.circle(P, size * 0.28, pen="b_cienka")
        if label:
            c.text(P + np.array([size / 2 + 0.8 * c.k, size / 2]), label, 1.8)


def inspection(c, pos, w: float = 0.3, d: float = 0.3, label: str = "R", layer: str = "S-URZADZENIA"):
    """Drzwiczki rewizyjne (prostokąt linią kreskową + litera)."""
    P = np.asarray(pos, float)
    with c.on(layer):
        c.polygon(rect_c(P[0], P[1], w, d), pen="cienka", lt="KRESKOWA_DROBNA")
        c.text(P, label, 1.8, 0.0, "center", "middle")


def grille(c, pos, rot=0.0, w: float = 0.4, d: float = 0.15, layer: str = "S-WENT", label: str | None = None):
    """Kratka wentylacyjna (prostokąt z lamelami) — wymiar rzeczywisty."""
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2)), pen="cienka")
        for x in np.linspace(-w / 2, w / 2, 7)[1:-1]:
            c.line(xf.pt(x, -d / 2), xf.pt(x, d / 2), pen="b_cienka")
        if label:
            c.text(xf.pt(0, d / 2 + 0.8 * c.k), label, 1.8, 0.0, "center", "bottom")


def anemostat(c, pos, d: float = 0.125, kind: str = "N", layer: str = "S-WENT", flow: str | None = None,
              label_mm: float = 1.0):
    """Anemostat/zawór wentylacyjny: dwa okręgi; kind 'N' — nawiewny (strzałki na zewnątrz), 'W' — wywiewny
    (strzałki do środka); opis przepływu np. '30 m³/h'."""
    k = c.k
    P = np.asarray(pos, float)
    R = max(d / 2, 2.0 * k)
    with c.on(layer):
        c.circle(P, R, pen="cienka")
        c.circle(P, R * 0.45, pen="b_cienka")
        for a in (45, 135, 225, 315):
            v = dir_deg(a)
            if kind.upper() == "N":
                a0, a1 = P + v * R * 0.55, P + v * R * 1.35
            else:
                a0, a1 = P + v * R * 1.45, P + v * R * 0.62
            c.line(a0, a1, pen="b_cienka")
            arrowhead(c, a1, a1 - a0, 1.2, 16, True, layer, pen="b_cienka")
        txt = kind.upper() + (f" {flow}" if flow else "")
        c.text(P + np.array([R * 1.5 + label_mm * k, -R * 0.2]), txt, 1.8, 0.0, "left", "middle")


def air_terminal(c, pos, rot=0.0, kind: str = "czerpnia", w: float = 0.4, layer: str = "S-WENT"):
    """Czerpnia / wyrzutnia powietrza (prostokąt z lamelami + strzałka do/od budynku). rot — kierunek na zewnątrz."""
    k = c.k
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(0.0, -w / 2, 0.08, w / 2)), pen="srednia")
        for y in np.linspace(-w / 2, w / 2, 5)[1:-1]:
            c.line(xf.pt(0.0, y), xf.pt(0.08, y + 0.03), pen="b_cienka")
        L = 6.0 * k
        if kind == "czerpnia":
            a0, a1 = xf.pt(0.08 + L + 0.02, 0), xf.pt(0.10, 0)
            lab = "ODA"
        else:
            a0, a1 = xf.pt(0.10, 0), xf.pt(0.08 + L + 0.02, 0)
            lab = "EHA"
        c.line(a0, a1, pen="cienka")
        arrowhead(c, a1, a1 - a0, 2.0, 12, True, layer)
        c.text((a0 + a1) / 2 + np.array([0.0, 1.0 * k]), lab, 1.8, 0.0, "center", "baseline")


def recuperator(c, pos, rot=0.0, w: float = 0.75, d: float = 0.6, layer: str = "S-WENT", label: str = "REKUPERATOR"):
    """Centrala wentylacyjna z odzyskiem ciepła: prostokąt z krzyżowym wymiennikiem, 4 króćce opisane kodami
    EN 16798-3 (R4 pkt 3.12): ODA — powietrze zewnętrzne, EHA — wyrzutowe, ETA — wywiewane, SUP — nawiewane."""
    k = c.k
    xf = Xf.make(np.asarray(pos, float), rot)
    with c.on(layer):
        c.polygon(xf(rect_pts(-w / 2, -d / 2, w / 2, d / 2)), pen="srednia")
        c.polygon(xf([[0, -d * 0.3], [w * 0.22, 0], [0, d * 0.3], [-w * 0.22, 0]]), pen="cienka")
        c.line(xf.pt(-w * 0.22, 0), xf.pt(w * 0.22, 0), pen="b_cienka")
        c.line(xf.pt(0, -d * 0.3), xf.pt(0, d * 0.3), pen="b_cienka")
        r = min(w, d) * 0.1
        for (x, y, lab) in ((-w / 2 + r * 1.6, d / 2, "ODA"), (w / 2 - r * 1.6, d / 2, "EHA"),
                            (-w / 2 + r * 1.6, -d / 2, "ETA"), (w / 2 - r * 1.6, -d / 2, "SUP")):
            c.circle(xf.pt(x, y + math.copysign(r, y)), r, pen="cienka")
            if y > 0:
                c.text(xf.pt(x, y + 2 * r + 0.8 * k), lab, 1.8, 0.0, "center", "baseline")
            else:
                c.text(xf.pt(x, y - 2 * r - 0.8 * k), lab, 1.8, 0.0, "center", "top")
        if label:
            c.text(xf.pt(0, d / 2 + 2 * r + 3.6 * k), label, 1.8, 0.0, "center", "baseline")


def radiator(c, p1, p2, depth: float = 0.10, side: float = 1.0, layer: str = "S-OGRZ", label: str | None = None):
    """Grzejnik przyścienny (prostokąt wzdłuż lica p1–p2, z zaworem termostatycznym)."""
    k = c.k
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = unit(B - A)
    n = perp(d) * side
    with c.on(layer):
        o = n * 0.04
        c.polygon([A + o, B + o, B + o + n * depth, A + o + n * depth], pen="srednia")
        c.line(A + o + n * depth / 2, B + o + n * depth / 2, pen="b_cienka")
        c.fill(circle_pts(B + o + n * depth / 2 + d * 0.06, 0.8 * k, 16), layer, "#000000")
        if label:
            c.text((A + B) / 2 + n * (depth + 0.04 + 1.0 * k), label, 1.8, 0.0, "center", "bottom")


def floor_heating(c, poly, spacing: float = 0.15, margin: float = 0.12, direction: str = "x", layer: str = "S-OGRZ",
                  label: str | None = None, start=None):
    """Pętla ogrzewania podłogowego (układ meandrowy) wewnątrz wieloboku strefy grzewczej; rozstaw rur [m].

    Zasilanie i powrót prowadzone równolegle (meander podwójny — naprzemiennie ciepła/zimna rura)."""
    k = c.k
    pg = to_polygon(poly).buffer(-margin, join_style=2)
    if pg.is_empty:
        return
    x0, y0, x1, y1 = pg.bounds
    pts = []
    if direction == "x":
        ys = np.arange(y0 + spacing / 2, y1, spacing)
        for i, y in enumerate(ys):
            xa, xb = (x0, x1) if i % 2 == 0 else (x1, x0)
            pts += [(xa, y), (xb, y)]
    else:
        xs = np.arange(x0 + spacing / 2, x1, spacing)
        for i, x in enumerate(xs):
            ya, yb = (y0, y1) if i % 2 == 0 else (y1, y0)
            pts += [(x, ya), (x, yb)]
    if len(pts) < 2:
        return
    ls = LineString(pts)
    for ln in lines_of(ls.intersection(pg)):
        c.polyline(ln, layer, pen="cienka")
    c.geom(pg, layer, pen="b_cienka", lt="KRESKOWA_DROBNA")
    if label:
        cx, cy = pg.centroid.x, pg.centroid.y
        c.text((cx, cy), label, 2.5, 0.0, "center", "middle", layer, mask=0.6)
