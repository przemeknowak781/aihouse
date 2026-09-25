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


# ------------------------------------------------------------------------------------------------ rzuty: wspólne
NOSNE = ("sciana_zewn", "sciana_wewn_nosna")


def _przekroj_slupa(txt: str) -> tuple[float, float]:
    """Wymiary przekroju słupa w rzucie [m] z opisu („RK 120x120x8”, „150x1000”, „HEB 200”)."""
    m = re.findall(r"(\d+(?:[.,]\d+)?)", str(txt or ""))
    v = [float(a.replace(",", ".")) for a in m]
    if len(v) >= 2 and v[1] > 20:
        return v[0] / 1000.0, v[1] / 1000.0
    if v:
        return v[0] / 1000.0, v[0] / 1000.0
    return 0.12, 0.12


def sciany_pod(m, z_spod: float, tol: float = 0.4) -> list:
    """Ściany nośne pod płytą: górna krawędź w [z_spod − tol, z_spod + 0,05] (kondygnacja poniżej)."""
    return [w for w in m.sciany() if w.typ in NOSNE and z_spod - tol <= w.z_do <= z_spod + 0.06
            and w.z_od < z_spod - 1.0]


def rysuj_sciany(vp, ctx, sciany, res: KResult, placer: Placer | None = None, otwory: bool = True,
                 obrys_only: bool = False, pen: str = "gruba"):
    """Warstwy konstrukcyjne ścian w przekroju (kreskowanie wg materiału modelu), otwory — linie kreskowe."""
    m = ctx.model
    for w in sciany:
        k = w.warstwa_konstr
        g = k.polygon
        if g is None or g.is_empty:
            continue
        hc = hatch_code(m, k.mat)
        if not obrys_only:
            H.hatch(vp, g, hc)
            _hm_add(res, hc, k.mat)
        vp.geom(g, L_OBR, pen=pen if not obrys_only else "cienka")
        if placer is not None:
            placer.add(g, "area", 0.6)
        if otwory:
            for o in w.otwory:
                for s_ in (o.s0, o.s1):
                    a, b = w.pt(s_, k.t0), w.pt(s_, k.t1)
                    vp.line(a, b, L_OBR, pen="cienka")
                a0, a1 = w.pt(o.s0, 0.0), w.pt(o.s1, 0.0)
                vp.line(a0, a1, L_OBR, pen="cienka", lt="KRESKOWA")


def rysuj_slupy(vp, m, z_lo: float, z_hi: float, placer: Placer | None = None) -> list:
    """Słupy o górze w [z_lo, z_hi] — przekrój zaczerniony (stal) / kreskowany (żelbet)."""
    out = []
    for c in m.slupy():
        if not (z_lo <= float(c["z_do"]) <= z_hi):
            continue
        a, b = _przekroj_slupa(c.get("przekroj"))
        x, y = c["xy"]
        g = box(x - a / 2, y - b / 2, x + a / 2, y + b / 2)
        mat = m.material(str(c.get("mat"))) if c.get("mat") else None
        if mat is not None and (mat.kreskowanie or "").upper() == "STAL":
            vp.fill(g, L_OBR, "#000000", z=23)
        else:
            H.hatch(vp, g, "ZELBET")
        vp.geom(g, L_OBR, pen="gruba")
        if placer is not None:
            placer.add(g.buffer(0.05), "area", 1.0)
        out.append((c, g))
    return out


def osie_i_wymiary(vp, ctx, bounds, placer: Placer | None = None, sides=("dol", "lewo"), extra: dict | None = None):
    """Osie konstrukcyjne (kółka na końcach) + łańcuchy: osie i wymiar całkowity obrysu (``bounds``) na stronach
    ``sides``; ``extra`` — {strona: [współrzędne]} dodatkowy (pierwszy) łańcuch, np. krawędzie płyt/żeber."""
    m = ctx.model
    k = vp.k
    X0, Y0, X1, Y1 = bounds
    offs = {}
    for side in ("dol", "gora", "lewo", "prawo"):
        chains = []
        key = "x" if side in ("dol", "gora") else "y"
        lo, hi = (X0, X1) if key == "x" else (Y0, Y1)
        if side in sides:
            if extra and extra.get(side):
                ch = sorted({round(v, 4) for v in extra[side] if lo - 1e-6 <= v <= hi + 1e-6} | {round(lo, 4), round(hi, 4)})
                if len(ch) > 2:
                    chains.append(ch)
            ax = sorted({round(float(v), 4) for v in (m.osie.get(key) or {}).values() if lo - 0.05 <= float(v) <= hi + 0.05})
            if len(ax) >= 2:
                chains.append(ax)
            chains.append([lo, hi])
        base = {"dol": Y0, "gora": Y1, "lewo": X0, "prawo": X1}[side]
        sg = 1.0 if side in ("prawo", "gora") else -1.0
        off = 10.0
        n0 = len(vp.prims)
        for ch in chains:
            pos = base + sg * off * k
            if side in ("dol", "gora"):
                dims.dim_h(vp, ch, pos, base, mask=0.3, layer=L_WYM)
            else:
                dims.dim_v(vp, ch, pos, base, mask=0.3, layer=L_WYM)
            off += 7.0
        offs[side] = base + sg * (off - 7.0 + 4.0) * k if chains else base + sg * 6.0 * k
        if placer is not None:
            placer.add_prims(vp.prims[n0:])
    y_lo, y_hi = offs["dol"] - 3 * k, offs["gora"] + 3 * k
    x_lo, x_hi = offs["lewo"] - 3 * k, offs["prawo"] + 3 * k
    n0 = len(vp.prims)
    for name, x in (m.osie.get("x") or {}).items():
        if X0 - 0.35 <= x <= X1 + 0.35:
            S.axis_line(vp, (x, y_lo), (x, y_hi), str(name), "both", layer=L_OSI)
    for name, y in (m.osie.get("y") or {}).items():
        if Y0 - 0.35 <= y <= Y1 + 0.35:
            S.axis_line(vp, (x_lo, y), (x_hi, y), str(name), "both", layer=L_OSI)
    if placer is not None:
        placer.add_prims(vp.prims[n0:], w_line=0.2)
    return offs


# ------------------------------------------------------------------------------------------------ pręty w rzucie
def _unit(v):
    v = np.asarray(v, float)
    n = float(np.hypot(*v))
    return v / n if n > 1e-12 else np.array([1.0, 0.0])


def opis_grupy(g: KD.GrupaPr) -> str:
    t = f"{g.n} Ø{g.pret.fi}"
    if g.s:
        t += f" co {g.s / 10:g}"
    return t + f" l={g.pret.L_mm / 10:g}"


def etykieta(vp, placer: Placer, p_ref, u, tekst: str, nr: int | None, h: float = 2.5, offs=(1.6, 5.5, 10.0),
             ts=(0.0,), bounds=None, layer: str = L_OPI):
    """Opis równoległy do kierunku ``u`` przy punkcie ``p_ref`` (numer pozycji w okręgu + tekst); położenie
    z najmniejszą kolizją (Placer); przy odsunięciu > 3 mm — odnośnik z kropką na pręcie."""
    k = vp.k
    u = _unit(u)
    if u[0] < -1e-9 or (abs(u[0]) < 1e-9 and u[1] < 0):
        u = -u
    n = np.array([-u[1], u[0]])
    rot = math.degrees(math.atan2(u[1], u[0]))
    r_mm = 2.6 if (nr or 0) < 10 else 3.0
    wt = text_w(tekst, h) + (2 * r_mm + 1.0 if nr is not None else 0.0)
    cands = []
    for off in offs:
        for t in ts:
            for sd in (1, -1):
                cands.append((t, sd, off))

    def draw(c, cand):
        t, sd, off = cand
        p = np.asarray(p_ref, float) + u * t
        base = p + n * sd * (off + (h / 2 if sd > 0 else h / 2 + 0.6)) * k - u * wt / 2 * k
        x = base.copy()
        if nr is not None:
            _nr_poz(c, x + u * r_mm * k, nr, h, layer)
            x = x + u * (2 * r_mm + 1.0) * k
        c.text(x, tekst, h, rot, "left", "middle", layer)
        if off > 3.0:
            q = p + n * sd * (off - 0.8) * k
            c.line(p, q, layer, pen="cienka")
            c.dot(p, 0.9, layer)
    best, cost = placer.place(vp, draw, cands, penalty_step=0.4, bounds=bounds)
    return best, cost


def rysuj_grupe(vp, placer: Placer, g: KD.GrupaPr, h: float = 2.5, opis: bool = True, bounds=None):
    """Pręt reprezentatywny (linia gruba, odgięcia rozłożone w płaszczyźnie rysunku), linia rozkładu (cienka,
    znaczniki 45° na końcach, kółko na przecięciu), opis: liczba Ø rozstaw długość + nr pozycji."""
    k = vp.k
    a, b = np.asarray(g.linia[0], float), np.asarray(g.linia[1], float)
    u = _unit(b - a)
    n = np.array([-u[1], u[0]])
    vp.line(a, b, L_ZBR, pen=PEN_PRET)
    legs = []
    if g.pret.ksztalt in ("11", "21"):
        leg = (g.pret.wym[-1] if g.pret.ksztalt == "11" else g.pret.wym[0]) / 1000.0
        for end, on in ((a, g.haki[0]), (b, g.haki[1])):
            if on:
                vp.line(end, end + n * leg, L_ZBR, pen=PEN_PRET)
                legs.append(LineString([end, end + n * leg]))
    ln = LineString([a, b])
    placer.add_lines(ln, w=0.8, buf_mm=0.5)
    for lg in legs:
        placer.add_lines(lg, w=0.8, buf_mm=0.5)
    r0, r1 = np.asarray(g.rozklad[0], float), np.asarray(g.rozklad[1], float)
    if np.hypot(*(r1 - r0)) > 0.05:
        v = _unit(r1 - r0)
        vp.line(r0, r1, L_OPI, pen="cienka")
        d45 = (v + np.array([-v[1], v[0]])) / math.sqrt(2) * 1.1 * k
        for e in (r0, r1):
            vp.line(e - d45, e + d45, L_OPI, pen="cienka")
        X = ln.intersection(LineString([r0, r1]))
        if not X.is_empty and X.geom_type == "Point":
            vp.circle((X.x, X.y), 0.7 * k, L_OPI, pen="cienka")
        placer.add_lines(LineString([r0, r1]), w=0.4, buf_mm=0.35)
    if opis:
        L = float(np.hypot(*(b - a)))
        mid = (a + b) / 2
        ts = [0.0] + [s_ * f * L for f in (0.18, 0.32) for s_ in (-1, 1)]
        return etykieta(vp, placer, mid, u, opis_grupy(g), g.pret.nr, h, ts=ts, bounds=bounds)
    return None, 0.0


def kolizje_napisow(vp, tol_mm2: float = 0.8) -> int:
    """Liczba par nakładających się napisów w rzutni (kontrola „etykiety bez kolizji”)."""
    from .common import prim_shapes
    t, _l, _f = prim_shapes([p for p in vp.prims if p.layer not in ("R-LEGENDA",)], vp.k)
    if len(t) < 2:
        return 0
    import shapely
    tree = shapely.STRtree(t)
    n = 0
    k2 = vp.k * vp.k
    for i, g in enumerate(t):
        for j in tree.query(g):
            if j <= i:
                continue
            if g.intersects(t[j]) and g.intersection(t[j]).area / k2 > tol_mm2:
                n += 1
    return n


# ------------------------------------------------------------------------------------------------ płyty: obrysy
def rysuj_plyty(vp, lv: KD.Poziom, placer: Placer, pen="gruba", opisy: bool = True):
    """Obrysy płyt poziomu (linia gruba), otwory (przekątne), opis elementu: id, h, beton, poz. obliczeń."""
    k = vp.k
    for e in lv.elementy:
        vp.geom(e.poly.exterior, L_OBR, pen=pen)
        for ring in e.poly.interiors:
            c = np.asarray(ring.coords)
            vp.polyline(c, L_OBR, closed=True, pen=pen)
            x0, y0, x1, y1 = Polygon(ring).bounds
            vp.line((x0, y0), (x1, y1), L_OBR, pen="cienka")
            vp.line((x0, y1), (x1, y0), L_OBR, pen="cienka")
        placer.add_lines(e.poly.boundary, w=0.6, buf_mm=0.6)
        for ring in e.poly.interiors:
            placer.add(Polygon(ring).buffer(0.02), "area", 0.8)


def _opis_elementu(vp, placer, e: KD.ElementPl, h: float = 2.5, extra: str = ""):
    txt = f"{e.id} (poz. {e.poz}): h = {_cm(e.h)} cm, {e.beton}, {e.eksp}" + extra
    from shapely.ops import polylabel
    try:
        pg = max(getattr(e.poly, "geoms", [e.poly]), key=lambda q: q.area)
        c = polylabel(pg, 0.02)
        p = np.array([c.x, c.y])
    except Exception:  # noqa: BLE001
        p = np.array(e.poly.representative_point().coords[0])
    x0, y0, x1, y1 = e.poly.bounds
    u = np.array([1.0, 0.0]) if (x1 - x0) >= (y1 - y0) else np.array([0.0, 1.0])
    ts = [0.0] + [s_ * f * max(x1 - x0, y1 - y0) for f in (0.2, 0.35) for s_ in (-1, 1)]
    etykieta(vp, placer, p, u, txt, None, h, offs=(0.0, 4.0, 8.0), ts=ts, bounds=e.poly.buffer(0.3), layer=L_OPS)


def _stopka_materialow(D: KD.DaneKonstr, elementy, fis: list[int]) -> list[str]:
    """Uwagi materiałowe (beton, stal, otulina, ekspozycja, zakotwienia i zakłady z biblioteki — 8.4, 8.7)."""
    from ..obliczenia.konstrukcja import zelbet
    from ..obliczenia.konstrukcja.materialy import Beton
    out = []
    grp = {}
    for e in elementy:
        grp.setdefault((e.beton, e.eksp, e.c_nom), []).append(e.id)
    for (bt, ex, c), ids in grp.items():
        out.append(f"{', '.join(ids)}: beton {bt}, klasa ekspozycji {ex}, otulina nominalna c_nom = {c:.0f} mm "
                   f"(c_min,dur wg PN-EN 1992-1-1 tabl. 4.4N, klasa konstrukcji S4, Δc_dev = 10 mm — 4.4.1.3 + NA).")
    bt = sorted({e.beton for e in elementy})[0] if elementy else "C25/30"
    zz = []
    for fi in sorted(set(fis)):
        z = zelbet.zakotwienie(fi, Beton.z_parametrow(bt))
        zz.append(f"Ø{fi}: l_bd = {z.l_bd / 10:.0f} cm, l₀ = {z.l_0 / 10:.0f} cm")
    if zz:
        out.append(f"Zakotwienia i zakłady prętów prostych ({bt}, dobre warunki przyczepności, 50 % prętów łączonych w "
                   f"przekroju; PN-EN 1992-1-1 8.4, 8.7, (8.3), (8.10)): " + "; ".join(zz) + ". W warunkach „innych” "
                   "(górne pręty płyt gr. > 25 cm) długości ×1/0,7.")
    return out
