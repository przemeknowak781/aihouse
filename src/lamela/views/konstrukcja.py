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


def blok_tabeli(tytul: str, cols, rows, h: float = 1.8, row_h: float = 4.5):
    """Blok kolumny opisowej: prosta tabela z tytułem (zawijanym do szerokości kolumny)."""
    def fn(sh, x, y, w):
        if not rows:
            return y
        ls = wrap(tytul, w, 2.5, "bold")
        for j, t in enumerate(ls):
            sh.text((x, y - 3.0 - j * 3.6), t, 2.5, style="bold", layer="R-OPISY")
        y0 = y - 3.0 - (len(ls) - 1) * 3.6 - 3.0
        sc = w / sum(c[1] for c in cols)
        r = table(sh, x, y0, [(n, cw * sc) for n, cw in cols], rows, h=h, row_h=row_h,
                  align=["center"] + ["left"] * (len(cols) - 1))
        return r[1] - 1.0
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
        tt = tytul if text_w(tytul, 3.5, "bold") <= w else tytul.split(" — ")[0]
        r = table(sh, x, y - 7.0, cols, rows, h=1.8, row_h=rh, title=tt, header_h=7.0,
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
    if g.kawalki > 1:
        t = f"{g.n // g.kawalki}×{g.kawalki} Ø{g.pret.fi}"
    else:
        t = f"{g.n} Ø{g.pret.fi}"
    if g.s:
        t += f" co {g.s / 10:g}"
    t += f" l={g.pret.L_mm / 10:g}"
    if g.kawalki > 1:
        t += f" (zakład {g.l0 * 100:.0f})"
    return t


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
        c.text(x, tekst, h, rot, "left", "middle", layer, mask=0.5)
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
    txt = f"{e.id} (poz. {e.poz}): h = {_cm(e.h)} cm, {e.beton}, {e.eksp}, wierzch {fmt.level(e.wierzch)}" + extra
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


UWAGI_ZBR = [
    "Stal zbrojeniowa B500SP (klasa ciągliwości C, f_yk = 500 MPa) wg PN-H-93220:2018-02 / PN-EN 10080; pręty gięte na "
    "zimno na trzpieniach φ_m ≥ 4φ (φ ≤ 16 mm) i ≥ 7φ (φ > 16 mm) — PN-EN 1992-1-1 tabl. 8.1N; oznaczenia prętów i "
    "kształtów wg PN-EN ISO 3766 (liczba, nr pozycji, Ø, rozstaw [cm], długość rozwinięcia l [cm]).",
    "Otuliny zapewnić podkładkami dystansowymi (rozstaw ≤ 1,0 m, dla siatek górnych — podpórki „kobyłki” ≤ 1,0 m) — "
    "PN-EN 13670 p. 6.5; odchyłka wykonawcza Δc_dev = 10 mm uwzględniona w c_nom (PN-EN 1992-1-1 4.4.1.3 + NA).",
    "Pręty łączyć na zakład l₀ (tabela w stopce zestawienia), styki mijankowo — w jednym przekroju ≤ 50 % prętów; "
    "odstęp w świetle prętów ≥ max(φ; d_g + 5 mm; 20 mm) — PN-EN 1992-1-1 8.2(2), 8.7.2; pręty dolne w strefie "
    "podpory zakotwić ≥ 10φ za licem (9.3.1.2(1) → 9.2.1.5).",
    "Betonowanie: beton wg PN-EN 206+A2 i PN-B-06265 (klasa, ekspozycja, D_max 16 mm, konsystencja S3); pielęgnacja ≥ 7 "
    "dni (klasa pielęgnacji 2 — PN-EN 13670 p. 8.5); przerwy robocze wyłącznie w miejscach uzgodnionych z projektantem.",
    "Rozszalowanie i usunięcie podpór: płyty i belki po uzyskaniu ≥ 70 % f_ck (PN-EN 13670 p. 5.6 i 8.5), wsporniki — "
    "nie wcześniej niż po 28 dniach i po wykonaniu elementów dociążających zaplecze; podpory wtórne do 28 dni.",
    "Zbrojenie wynika z obliczeń statycznych (projekt/04_PT_konstrukcja/obliczenia, numeracja pozycji jak na rysunku); "
    "kontrola A_s,prov ≥ A_s,req — raport kontrola_zbrojenia.md. Pozycje z niespełnionymi warunkami nośności "
    "(wynik „NIE” w raporcie) wymagają zmian przed wydaniem do realizacji.",
]


def _legenda_zbrojenia(warstwa: str) -> list:
    out = [("pret", f"pręt reprezentatywny grupy ({'warstwa dolna' if warstwa == 'dol' else 'warstwa górna'}), "
                    "linia gruba"),
           ("pret_hak", "pręt z odgięciem 90° — odgięcie (ramię) pokazane w płaszczyźnie rysunku"),
           ("rozklad", "linia rozkładu prętów grupy (zasięg), kółko — pręt reprezentatywny"),
           ("poz", "numer pozycji pręta (zestawienie stali)"),
           ("naroze", "strefa zbrojenia narożnego (0,2·l_min) — pręty górą i dołem w 2 kierunkach"),
           ("kreskowa", "ściany / belki / słupy pod płytą (widok zasłonięty)")]
    if warstwa == "gora":
        out.append(("lacznik", "łącznik termoizolacyjny (ETA) — pręty wspornika przez izolację"))
    return out


def widok_zbrojenie_plyt(ctx: ViewContext, spec: dict, scale: float, opts: dict):
    D = KD.dane(ctx)
    lv = D.poziom(spec.get("poziom") or spec.get("kond") or spec.get("plyta"))
    if lv is None:
        raise KeyError(f"brak poziomu płyt '{spec.get('poziom') or spec.get('kond')}' w wynikach obliczeń")
    warstwa = "gora" if str(spec.get("warstwa", "dolna")).lower().startswith("g") else "dol"
    ids = ", ".join(e.id for e in lv.elementy)
    title = spec.get("tytul_widoku") or f"ZBROJENIE {'GÓRNE' if warstwa == 'gora' else 'DOLNE'} PŁYT {ids}"
    vp = Viewport(scale, title)
    res = KResult()
    placer = Placer(vp.k)
    m = ctx.model
    P = prety_poziomu(D, lv)
    rysuj_plyty(vp, lv, placer)
    osie_i_wymiary(vp, ctx, lv.poly.bounds, placer, sides=("dol", "lewo"))
    sc = sciany_pod(m, lv.spod)
    for w in sc:
        g = w.warstwa_konstr.polygon
        if g is not None and not g.is_empty:
            vp.geom(g.intersection(lv.poly.buffer(0.5)), L_OBR, pen="cienka", lt="KRESKOWA")
    for c, g in rysuj_slupy(vp, m, lv.spod - 0.4, lv.spod + 0.05):
        pass
    for b in m.belki():
        top = float(b["spod"]) + float(b["h"])
        if lv.spod - 0.06 <= top <= lv.wierzch + 1.2 and float(b["spod"]) < lv.spod + 0.3:
            (x0, y0), (x1, y1) = b["os"]
            ln = LineString([(x0, y0), (x1, y1)])
            vp.geom(ln.buffer(float(b["b"]) / 2, cap_style=2), L_OBR, pen="cienka", lt="KRESKOWA")
    grupy = P[warstwa]
    bnd = lv.poly.buffer(1.5)
    naroza = {}
    for g in grupy:
        if g.rola == "naroze":
            naroza.setdefault((g.element, g.pole, round(g.zakres.centroid.x, 2), round(g.zakres.centroid.y, 2)), []).append(g)
            continue
    # najpierw rysunek wszystkich prętów (przeszkody), potem opisy — od grup najdłuższych
    for g in grupy:
        if g.rola == "naroze":
            vp.line(g.linia[0], g.linia[1], L_ZBR, pen=0.35)
        else:
            rysuj_grupe(vp, placer, g, opis=False)
    for zone_gs in naroza.values():
        zn = zone_gs[0].zakres
        vp.geom(zn.exterior, L_OPI, pen="cienka", lt="KRESKOWA_DROBNA")
        placer.add_lines(zn.exterior, w=0.3)
    for g in sorted([g for g in grupy if g.rola != "naroze"], key=lambda q: -LineString(q.linia).length):
        a, b = np.asarray(g.linia[0]), np.asarray(g.linia[1])
        L = float(np.hypot(*(b - a)))
        ts = [0.0] + [s_ * f * L for f in (0.18, 0.32) for s_ in (-1, 1)]
        etykieta(vp, placer, (a + b) / 2, b - a, opis_grupy(g), g.pret.nr, 2.5, ts=ts, bounds=bnd)
    wiersze_n = []
    for i, ((el, pole, cx, cy), gs) in enumerate(sorted(naroza.items(), key=lambda t: (-t[0][3], t[0][2])), 1):
        gs = sorted(gs, key=lambda q: q.kier)
        tag = f"N{i}"
        zn = gs[0].zakres
        cands = [(cx, cy)] + [(cx + dx, cy + dy) for dx in (-0.45, 0.45, 0.0) for dy in (0.0, -0.45, 0.45)]

        def draw_tag(c, pos, _t=tag):
            S.tag(c, pos, _t, shape="hex", r_mm=2.4, h=1.8, layer=L_OPI)
        placer.place(vp, draw_tag, cands, penalty_step=0.2)
        nrs = ", ".join(dict.fromkeys(f"{q.pret.nr} ({q.kier})" for q in gs))
        wiersze_n.append([tag, f"{el}/{pole}", _pl(zn.bounds[2] - zn.bounds[0], 2), nrs,
                          f"Ø{gs[0].pret.fi} co {gs[0].s / 10:g}"])
    if wiersze_n:
        res.column_blocks.append(("naroza", blok_tabeli(
            "STREFY ZBROJENIA NAROŻNEGO (górą i dołem, 2 kierunki — PN-EN 1992-1-1 9.3.1.3)",
            [("Strefa", 14.0), ("Pole", 26.0), ("Bok [m]", 16.0), ("Pozycje (kierunek)", 84.0), ("Pręty", 40.0)],
            wiersze_n)))
    for e in lv.elementy:
        _opis_elementu(vp, placer, e)
    # kontrola A_s: zbrojenie narysowane vs wymagane
    nr_ark = spec.get("nr", "")
    for g in grupy:
        w = g.wym
        if w is None:
            continue
        e = next(x for x in lv.elementy if x.id == g.element)
        miejsce = {"przeslo": f"pole {g.pole} — {'dół' if warstwa == 'dol' else 'góra'} {g.kier}",
                   "podpora": f"nad podporą {g.pole} — góra {g.kier}", "wspornik": f"wspornik — góra {g.kier}",
                   "naroze": f"pole {g.pole} — naroże ({'dół' if warstwa == 'dol' else 'góra'} {g.kier})"}[g.rola]
        As_prov = KD.pole_preta(g.pret.fi) * 1000.0 / g.s
        KD.rejestruj(D, e.id, miejsce, e.poz, w.As_req, w.As_min if w.As_req > 0 or warstwa == "dol" else 0.0, As_prov,
                     f"Ø{g.pret.fi} co {g.s / 10:g}", s=g.s, s_max=KD.s_max_plyty(e.h), As_max=0.04 * e.h * 1e6,
                     arkusz=nr_ark, uwagi=("; ".join(e.niesp[:2]) if e.niesp else ""),
                     wymuszone_ok=None)
    fis = sorted({g.pret.fi for g in grupy})
    masa = P["zest"].masa
    res.column_blocks.append(("legenda_k", blok_legendy(_legenda_zbrojenia(warstwa))))
    res.column_blocks.append(("zestawienie", blok_zestawienia(
        P["zest"], f"ZESTAWIENIE STALI — PŁYTY {ids} (warstwy dolna i górna)",
        _stopka_materialow(D, lv.elementy, [p.fi for p in P["zest"].prety]), masa)))
    res.notes += UWAGI_ZBR
    if warstwa == "gora":
        res.notes.append("Warstwa górna: pręty nad podporami — 0,3·l przęsła za osią podpory (≥ l_bd), przy "
                         "krawędzi płyty z odgięciem w wieńcu (ramię = h − 2c); wsporniki — od krawędzi swobodnej przez "
                         "łącznik termoizolacyjny do przęsła zaplecza na max(l_c; l_bd) za podporą (PN-EN 1992-1-1 "
                         "9.3.1.2(2), 9.3.1.4).")
    else:
        res.notes.append("Warstwa dolna: siatka pól wg obliczeń MES (Wood–Armer, obwiednia ULS); pręty kierunku x "
                         "(równoległe do osi x) — warstwa zewnętrzna, kierunek y — wewnętrzna; na podporach pośrednich "
                         "przedłużenie ≥ 10φ za oś podpory, na skrajnych — do krawędzi płyty.")
    n_bad = [e for e in lv.elementy if e.niesp]
    if n_bad:
        res.notes.append("UWAGA — obliczenia (biblioteka) wykazują niespełnione warunki: " + "; ".join(
            f"{e.id} (poz. {e.poz}): {e.niesp[0]}" for e in n_bad[:4]) + " — wymagana zmiana przekroju/zbrojenie na "
            "ścinanie przed wydaniem do realizacji [WYMAGA ANALIZY].")
    kol = kolizje_napisow(vp)
    if kol:
        ctx.note(f"{nr_ark} {title}", f"kolizje napisów: {kol}")
    KD.zapisz_raporty(D, ctx)
    return vp, res, title


def prety_poziomu(D, lv):
    return KD.prety_poziomu(D, lv)


# ------------------------------------------------------------------------------------------------ k_strop
def _belki_poziomu(m, lv) -> list:
    """Belki modelu związane z poziomem płyt: przekrój belki przecina pas [spód płyty; wierzch płyty]."""
    out = []
    for b in m.belki():
        sp, hb = float(b["spod"]), float(b["h"])
        if sp + hb >= lv.spod - 0.06 and sp <= lv.wierzch + 0.06 and LineString(b["os"]).distance(lv.poly) < 0.3:
            out.append(b)
    return out


def _strzalki_pola(vp, placer, pol: KD.PolePl, typ: str, root_dir=None):
    """Kierunek pracy pola: płyta krzyżowo zbrojona — krzyż strzałek, jednokierunkowa (l_max/l_min ≥ 2) — strzałka
    w kierunku krótszym; wspornik — strzałka od zamocowania z kreską utwierdzenia."""
    k = vp.k
    from shapely.ops import polylabel
    try:
        c = polylabel(max(getattr(pol.poly, "geoms", [pol.poly]), key=lambda q: q.area), 0.02)
        C = np.array([c.x, c.y])
    except Exception:  # noqa: BLE001
        C = np.array(pol.poly.representative_point().coords[0])
    x0, y0, x1, y1 = pol.poly.bounds
    lx, ly = x1 - x0, y1 - y0
    dirs = []
    if typ == "wspornik" and root_dir is not None:
        dirs = [np.asarray(root_dir, float)]
    elif max(lx, ly) / max(min(lx, ly), 1e-6) >= 2.0:
        dirs = [np.array([1.0, 0.0]) if lx < ly else np.array([0.0, 1.0])]
    else:
        dirs = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]
    for d in dirs:
        L = min((lx if d[0] else ly) * 0.35, 1.6)
        a, b = C - d * L / 2, C + d * L / 2
        vp.line(a, b, L_OPS, pen="cienka")
        dims.arrowhead(vp, b, d, 2.5, 12, True, L_OPS)
        if typ != "wspornik":
            dims.arrowhead(vp, a, -d, 2.5, 12, True, L_OPS)
        else:
            nn = np.array([-d[1], d[0]])
            vp.line(a - nn * 1.6 * k, a + nn * 1.6 * k, L_OPS, pen="srednia")
        placer.add_lines(LineString([a, b]), w=0.6, buf_mm=1.2)
    return C


def widok_strop(ctx: ViewContext, spec: dict, scale: float, opts: dict):
    D = KD.dane(ctx)
    m = ctx.model
    lv = D.poziom(spec.get("poziom") or spec.get("kond"))
    if lv is None:
        raise KeyError(f"k_strop: brak poziomu płyt '{spec.get('poziom') or spec.get('kond')}' w obliczeniach")
    title = spec.get("tytul_widoku") or f"RZUT KONSTRUKCJI — PŁYTY {', '.join(e.id for e in lv.elementy)}"
    vp = Viewport(scale, title)
    res = KResult(north=True)
    placer = Placer(vp.k)
    k = vp.k
    sc = sciany_pod(m, lv.spod)
    rysuj_sciany(vp, ctx, sc, res, placer)
    sl = rysuj_slupy(vp, m, lv.spod - 0.4, lv.spod + 0.05, placer)
    rysuj_plyty(vp, lv, placer)
    osie_i_wymiary(vp, ctx, lv.poly.bounds, placer, sides=("dol", "lewo", "gora", "prawo"))
    nr_ark = spec.get("nr", "")
    # tarcze (jeżeli analiza je wykryła)
    for wid, wt in (getattr(D.an, "tarcze", {}) or {}).items():
        w = m.sciana(wid)
        if w is None or w.warstwa_konstr.polygon is None:
            continue
        H.hatch(vp, w.warstwa_konstr.polygon, "ZELBET")
        pz = next((q for q in D.an.pos_tarcze if q.ident == wid), None)
        etykieta(vp, placer, w.pt(w.L / 2, 0.0), w.u, f"ściana-tarcza {wid} (poz. {pz.nr if pz else '—'}), "
                 f"t = {_cm(w.warstwa_konstr.d)} cm", None, 2.5, offs=(3.0, 7.0, 11.0), layer=L_OPS)
    # belki
    bel_obl = {b.id: b for b in D.belki}
    for b in _belki_poziomu(m, lv):
        sp, hb = float(b["spod"]), float(b["h"])
        ln = LineString(b["os"])
        g = ln.buffer(float(b["b"]) / 2, cap_style=2)
        odwr = sp + hb > lv.wierzch + 0.05
        vp.geom(g, L_OBR, pen="srednia", lt=None if odwr else "KRESKOWA")
        placer.add(g, "area", 0.5)
        B = bel_obl.get(str(b["id"]))
        txt = f"{b['id']} {_cm(float(b['b']))}×{_cm(hb)}" + (" (odwrócona)" if odwr else "")
        txt += f", poz. {B.poz}" if B else " — brak wymiarowania [WYMAGA ANALIZY]"
        u = np.asarray(b["os"][1], float) - np.asarray(b["os"][0], float)
        etykieta(vp, placer, np.asarray(ln.interpolate(0.5, normalized=True).coords[0]), u, txt, None, 2.5,
                 offs=(float(b["b"]) * 500 / scale * 2 + 1.5, 6.0, 10.0),
                 ts=(0.0, -0.25 * ln.length, 0.25 * ln.length), layer=L_OPS)
    # słupy
    for c, g in sl:
        pz = next((q for q in D.an.pos_slupy if q.ident == str(c["id"])), None)
        etykieta(vp, placer, np.asarray(c["xy"], float) + np.array([0.0, -0.25]), (1.0, 0.0),
                 f"{c['id']} {c.get('przekroj')}" + (f" (poz. {pz.nr})" if pz else ""), None, 1.8,
                 offs=(1.5, 4.0, 7.0), ts=(0.0, -0.4, 0.4), layer=L_OPS)
    # nadproża w ścianach pod płytą
    ids_sc = {w.id for w in sc}
    typy_uz = {}
    for nm, lst in KD.typy_nadprozy(D):
        for n in lst:
            if n.sciana in ids_sc:
                typy_uz.setdefault(nm, []).append(n)
                p = (np.asarray(n.p0) + np.asarray(n.p1)) / 2

                def draw_t(c_, pos, _t=nm):
                    S.tag(c_, pos, _t, shape="rect", r_mm=2.2, h=1.8, layer=L_OPS)
                w = m.sciana(n.sciana)
                cands = [tuple(p + w.n * d) for d in (0.0, 0.3, -0.3, 0.55, -0.55)]
                placer.place(vp, draw_t, cands, penalty_step=0.3)
    # pola, kierunki pracy, łączniki
    for e in lv.elementy:
        for pol in e.pola:
            root = None
            if e.typ == "wspornik":
                inne = unary_union([x.poly for x in lv.elementy if x is not e])
                segs = [q for q in KD.odcinki_proste(e.poly.boundary.intersection(inne.buffer(0.02))) if q.length > 0.3]
                if segs:
                    sg = max(segs, key=lambda q: q.length)
                    (xa, ya), (xb, yb) = sg.coords[0], sg.coords[-1]
                    nrm = np.array([-(yb - ya), xb - xa]) / sg.length
                    if not e.poly.buffer(-0.01).contains(Point(*(np.asarray(sg.interpolate(0.5, normalized=True).coords[0]) + nrm * 0.1))):
                        nrm = -nrm
                    root = nrm
            C = _strzalki_pola(vp, placer, pol, e.typ, root)
            etykieta(vp, placer, C + np.array([0.0, 0.35]), (1.0, 0.0), f"{pol.pole}", None, 2.5, offs=(0.0, 3.0, 6.0),
                     ts=(0.0, -0.4, 0.4), layer=L_OPS)
        _opis_elementu(vp, placer, e)
        if e.lacznik and e.typ == "wspornik":
            _laczniki(vp, placer, D, lv, e, res)
    # kolumna: legenda, nadproża, belki, wieńce
    res.column_blocks.append(("legenda_k", blok_legendy([
        ("slup", "słup stalowy (przekrój) — pod płytą"),
        ("kreskowa", "belka / podciąg pod płytą (widok zasłonięty); linia ciągła — belka odwrócona (nad płytą)"),
        ("lacznik", "łącznik termoizolacyjny płyty wspornikowej (ETA)"),
        ("tekst", "↔ kierunek pracy pola (krzyż — płyta krzyżowo zbrojona); P1… — pola obliczeniowe MES"),
        ("tekst", "NA, NB… — typ nadproża (tabela); ściany pod płytą kreskowane wg materiału")])))
    wiersze = []
    for nm, lst in KD.typy_nadprozy(D):
        if nm not in typy_uz:
            continue
        n0 = lst[0]
        wiersze.append([nm, f"{_cm(n0.b)}×{_cm(n0.h)}", _pl(n0.L, 2), f"{n0.dol[0]}Ø{n0.dol[1]} / 2Ø10",
                        f"Ø{n0.strz[0]} co {n0.strz[1] / 10:g}", ", ".join(x.ids[0] for x in typy_uz[nm])[:44],
                        ", ".join(sorted({x.poz for x in typy_uz[nm]}))[:24]])
    if wiersze:
        res.column_blocks.append(("nadproza", blok_tabeli(
            "NADPROŻA ŻELBETOWE W ŚCIANACH POD PŁYTĄ (z obliczeń; zbrojenie — arkusz nadproży)",
            [("Typ", 10), ("b×h [cm]", 16), ("L [m]", 12), ("dół/góra", 24), ("strzemiona", 22), ("otwory", 60),
             ("poz. obl.", 36)], wiersze)))
    wn = next((w for w in D.wience if lv.idx in w.ids), None)
    res.notes += [
        f"Płyty monolityczne: {', '.join(f'{e.id} h = {_cm(e.h)} cm ({e.beton}, {e.eksp}, c_nom = {e.c_nom:.0f} mm)' for e in lv.elementy)}; "
        f"wierzch konstrukcji {fmt.level(lv.wierzch)} (średnio), rzędne elementów wg przekrojów i modelu.",
        (f"Wieńce ({wn.id}, poz. {wn.poz}): na wszystkich ścianach nośnych pod płytą, szerokość = grubość muru, "
         f"wysokość = grubość płyty, {wn.dol[0] + wn.gora[0]}Ø{wn.dol[1]} + strzemiona Ø{wn.strz[0]} co "
         f"{wn.strz[1] / 10:g} cm, {wn.beton}; {wn.opis.split(';')[-1].strip()} (PN-EN 1992-1-1 9.10.2.2, 8.7).")
        if wn else "Wieńce — brak pozycji w obliczeniach [WYMAGA ANALIZY].",
        "Kierunek pracy pól wg modelu MES płyty (biblioteka — Wood–Armer); pola P… — numeracja komórek siatki podpór "
        "obliczeń (zbrojenie — arkusze zbrojenia dolnego i górnego).",
    ]
    bez = [b for b in _belki_poziomu(m, lv) if str(b["id"]) not in bel_obl]
    if bez:
        res.notes.append("Belki bez wymiarowania w bibliotece (" + ", ".join(str(b["id"]) for b in bez) + ") — "
                         "zbrojenie do obliczenia indywidualnego przed wydaniem do realizacji [WYMAGA ANALIZY].")
    if not getattr(D.an, "tarcze", None):
        res.notes.append("Ściany-tarcze: analiza nie wykryła ścian-tarcz na tym poziomie (moduł tarcze — ściana ŻB "
                         "podparta na < 95 % długości lub pole `tarcza: true`).")
    kol = kolizje_napisow(vp)
    if kol:
        ctx.note(f"{nr_ark} {title}", f"kolizje napisów: {kol}")
    KD.zapisz_raporty(D, ctx)
    return vp, res, title


def _laczniki(vp, placer, D, lv, e: KD.ElementPl, res: KResult):
    """Łączniki termoizolacyjne wzdłuż linii zamocowania wspornika: pas (korpus izolacji ``LACZNIK_T``) po stronie
    płyty zaplecza (w płaszczyźnie izolacji ściany), opis z siłami m_Ed, v_Ed z obliczeń (pole wspornika)."""
    inne = unary_union([x.poly for x in lv.elementy if x is not e])
    segs = [q for q in KD.odcinki_proste(e.poly.boundary.intersection(inne.buffer(0.02))) if q.length >= 1.0]
    pol = max(e.pola, key=lambda p: p.poly.area) if e.pola else None
    for sg in segs:
        (xa, ya), (xb, yb) = sg.coords[0], sg.coords[-1]
        kier = "y" if abs(ya - yb) < 1e-3 else "x"
        mid = np.asarray(sg.interpolate(0.5, normalized=True).coords[0])
        nrm = np.array([-(yb - ya), xb - xa]) / sg.length
        if not e.poly.buffer(-0.01).contains(Point(*(mid + nrm * 0.1))):
            nrm = -nrm
        tl = KD.LACZNIK_T
        band = Polygon([sg.coords[0], sg.coords[-1], tuple(np.asarray(sg.coords[-1]) - nrm * tl),
                        tuple(np.asarray(sg.coords[0]) - nrm * tl)])
        vp.fill(band, L_OBR, "#9a9a9a", z=21)
        vp.geom(band, L_OBR, pen="cienka")
        placer.add(band, "area", 0.8)
        w = pol.warstwy.get("gora_" + kier) if pol else None
        m_ed = f"m_Ed = {_pl(w.M, 1)} kNm/m" if w and w.M else "m_Ed — wg poz."
        sc_ok = pol is not None and not any("Ścinanie" in t for t in pol.niesp)
        v_ed = (f", v_Ed ≤ {_pl(pol.V, 1)} kN/m" if sc_ok and pol.V else ", v_Ed — wg poz. [WYMAGA ANALIZY]")
        txt = f"łącznik termoizol. (ETA), h = {_cm(e.h)} cm: {m_ed}{v_ed} (poz. {e.poz})"
        etykieta(vp, placer, mid + nrm * 0.04, np.asarray(sg.coords[-1]) - np.asarray(sg.coords[0]), txt, None, 2.5,
                 offs=(3.0, 7.0, 12.0), ts=(0.0, -0.25 * sg.length, 0.25 * sg.length), layer=L_OPS)
    if segs:
        res.notes.append(f"{e.id}: łączniki termoizolacyjne ciągłe na całej linii zamocowania — wyrób z Europejską "
                         "Oceną Techniczną (EAD 050001-00-0301) „lub równoważny” (np. typ z prętami ze stali "
                         "nierdzewnej przez izolację gr. 80–120 mm); dobór wg dokumentacji producenta na m_Ed i v_Ed z "
                         "obliczeń, z uwzględnieniem uskoku wierzchu płyt; sprawdzenie ugięcia wspornika z podatnością "
                         "łącznika (W-268, W-272).")


# ------------------------------------------------------------------------------------------------ k_fundamenty
L_UZ = "E-UZIOM"
KOL_UZ = "#b0006a"


def _instalacje(ctx) -> dict:
    """``instalacje.yaml`` obok pliku modelu (piony, przybory — przejścia przez płytę)."""
    import yaml
    from pathlib import Path
    p = Path(ctx.src or "model/budynek.yaml").with_name("instalacje.yaml")
    if not p.exists():
        return {}
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return d.get("instalacje") or {}


BRANZE_PRZYL = {"woda": "wody", "kan_sanit": "kanalizacji sanitarnej", "en": "elektroenergetyczne (WLZ)",
                "tele": "teletechniczne", "gaz": "gazu", "cieplo": "ciepłownicze"}


def _przylacza(ctx, P) -> list:
    """Przyłącza projektowane (dzialka.yaml → uzbrojenie.projektowane) przechodzące przez obrys fundamentu:
    [(branża, punkt przejścia (x, y), opis)] w układzie budynku."""
    m = ctx.model
    dz = getattr(m, "dz", None)
    if dz is None:
        return []
    out = []
    for u in ((dz.raw.get("uzbrojenie") or {}).get("projektowane") or []):
        if str(u.get("branza")) not in BRANZE_PRZYL:
            continue                      # np. kanalizacja deszczowa — rury spustowe poza obrysem
        pts = np.asarray(u.get("linia") or [], float)
        if len(pts) < 2:
            continue
        ln = LineString(dz.do_budynku(pts))
        for end in (Point(ln.coords[0]), Point(ln.coords[-1])):
            if end.distance(P) < 1.0:
                q = P.exterior.interpolate(P.exterior.project(end))
                out.append((str(u.get("branza")), (q.x, q.y), str(u.get("opis") or "")))
                break
    return out


def widok_fundamenty(ctx: ViewContext, spec: dict, scale: float, opts: dict):
    D = KD.dane(ctx)
    m = ctx.model
    fu = m.fundamenty()
    els = fu.get("elementy") or []
    title = spec.get("tytul_widoku") or "RZUT FUNDAMENTÓW"
    vp = Viewport(scale, title)
    res = KResult(north=True)
    placer = Placer(vp.k)
    k = vp.k
    plyty = [e for e in els if "obrys" in e]
    P = unary_union([Polygon(e["obrys"]) for e in plyty]) if plyty else None
    liniowe = [e for e in els if "os" in e]
    geom_l = {str(e["id"]): LineString(e["os"]).buffer(float(e.get("b", 0.6)) / 2, cap_style=3 if LineString(e["os"]).length
                                                        < float(e.get("b", 0.6)) else 2) for e in liniowe}
    allg = unary_union(([P] if P is not None else []) + list(geom_l.values()))
    bnd = allg.bounds
    # izolacja obwodowa (PN-EN ISO 13793)
    iz = fu.get("izolacja_obwodowa") or {}
    if iz and P is not None:
        Dz = float(iz.get("D", 1.0))
        ring = P.buffer(Dz, join_style=2).difference(P)
        vp.geom(P.buffer(Dz, join_style=2).exterior, L_OBR, pen="cienka", lt="KRESKOWA")
        placer.add_lines(P.buffer(Dz, join_style=2).exterior, w=0.4)
        bnd = P.buffer(Dz, join_style=2).bounds
    offs = osie_i_wymiary(vp, ctx, bnd, placer, sides=("dol", "lewo", "gora", "prawo"),
                          extra={"dol": [c[0] for c in (P.exterior.coords if P is not None else [])],
                                 "lewo": [c[1] for c in (P.exterior.coords if P is not None else [])]})
    # ściany parteru (obrys konstrukcji) i słupy
    k0 = m.kondygnacje[0].id
    for w in m.sciany(k0):
        g = w.warstwa_konstr.polygon
        if g is not None and not g.is_empty and w.typ in NOSNE:
            vp.geom(g, L_OBR, pen="cienka")
    for c in m.slupy():
        if float(c["z_od"]) < 0.5:
            a, b = _przekroj_slupa(c.get("przekroj"))
            x, y = c["xy"]
            vp.fill(box(x - a / 2, y - b / 2, x + a / 2, y + b / 2), L_OBR, "#000000", z=23)
    # płyta
    if P is not None:
        vp.geom(P, L_OBR, pen="gruba")
        placer.add_lines(P.boundary, w=0.6, buf_mm=0.6)
    for e in liniowe:
        g = geom_l[str(e["id"])]
        vp.geom(g, L_OBR, pen="srednia", lt="KRESKOWA" if P is not None else None)
        placer.add_lines(g.boundary, w=0.3)
    # opisy elementów
    fz = {z.id: z for z in D.zebra}
    fs = {s_.id: s_ for s_ in D.stopy}
    for e in liniowe:
        eid = str(e["id"])
        ln = LineString(e["os"])
        B, hf, sp = float(e.get("b", 0.6)), float(e.get("h", 0.3)), float(e.get("spod", -0.7))
        poz = (fz.get(eid) or fs.get(eid))
        if ln.length < B:
            txt = f"{eid} {_cm(B)}×{_cm(B)}, spód {fmt.level(sp)}" + (f" (poz. {poz.poz})" if poz else "")
            etykieta(vp, placer, np.asarray(ln.interpolate(0.5, normalized=True).coords[0]) + np.array([0, -B / 2 - 0.1]),
                     (1.0, 0.0), txt, None, 1.8, offs=(1.5, 4.5, 8.0), ts=(0.0, -0.6, 0.6), layer=L_OPS)
            continue
        txt = f"{eid}: b = {_cm(B)} cm, spód {fmt.level(sp)}" + (f" (poz. {poz.poz})" if poz else "")
        u = np.asarray(e["os"][1], float) - np.asarray(e["os"][0], float)
        etykieta(vp, placer, np.asarray(ln.interpolate(0.5, normalized=True).coords[0]), u, txt, None, 2.5,
                 offs=(B * 1000 / scale / 2 + 1.5, B * 1000 / scale / 2 + 5.0), ts=(0.0, -0.25 * ln.length, 0.25 * ln.length,
                                                                                    -0.4 * ln.length, 0.4 * ln.length),
                 layer=L_OPS)
    if P is not None:
        F = D.plyta_f
        e0 = plyty[0]
        top = float(e0.get("spod", -0.4)) + float(e0.get("h", 0.25))
        txt = (f"{e0.get('id')} (poz. {F.poz if F else '—'}): płyta ŻB h = {_cm(float(e0.get('h', 0.25)))} cm, "
               f"{F.beton if F else ''}, {F.eksp if F else ''}; wierzch {fmt.level(top)}, spód {fmt.level(float(e0.get('spod', -0.4)))}")
        from shapely.ops import polylabel
        c0 = polylabel(P if P.geom_type == "Polygon" else max(P.geoms, key=lambda q: q.area), 0.05)
        etykieta(vp, placer, (c0.x, c0.y), (1.0, 0.0), txt, None, 2.5, offs=(0.0, 4.0, 8.0),
                 ts=(0.0, -2.0, 2.0, -4.0, 4.0), layer=L_OPS)
    # przejścia instalacyjne
    inst = _instalacje(ctx)
    n_prz = 0
    if P is not None:
        for pion in inst.get("piony") or []:
            xy = pion.get("xy")
            if xy and P.contains(Point(*xy)):
                n_prz += 1
                _przejscie(vp, placer, xy, f"{pion.get('id')}: {str(pion.get('opis') or '')[:40]}", 0.16)
        for pr in inst.get("przybory_dodatkowe") or []:
            if pr.get("typ") in ("wpust_podlogowy", "odplyw") and P.contains(Point(*pr["xy"])):
                n_prz += 1
                _przejscie(vp, placer, pr["xy"], "wpust podłogowy — przejście DN110", 0.16)
        for br, xy, op in _przylacza(ctx, P):
            n_prz += 1
            _przejscie(vp, placer, xy, f"przyłącze {BRANZE_PRZYL.get(br, br)}: rura osłonowa, przejście szczelne", 0.2)
    # uziom fundamentowy
    if P is not None:
        _uziom(vp, placer, ctx, P, inst, res)
    # ślady przekrojów charakterystycznych
    for nm, eid, frac in _przekroje_fund(ctx, liniowe):
        e = next(x for x in liniowe if str(x["id"]) == eid)
        ln = LineString(e["os"])
        B = float(e.get("b", 0.6))
        c = np.asarray(ln.interpolate(frac, normalized=True).coords[0])
        u = _unit(np.asarray(e["os"][1], float) - np.asarray(e["os"][0], float))
        n = np.array([-u[1], u[0]])
        L_ = B / 2 + (float(iz.get("D", 1.0)) + 0.4 if iz else 0.8)
        S.section_mark(vp, c - n * L_, c + n * L_, nm, look=1.0, h=3.5, end_mm=6.0, arrow_mm=4.0, layer=L_OPS)
        placer.add_lines(LineString([c - n * L_, c + n * L_]), w=0.8, buf_mm=3.0)
    res.column_blocks.append(("legenda_k", blok_legendy([
        ("kreskowa_gruba", "żebra / pogrubienia płyty (pod płytą — widok zasłonięty)"),
        ("kreskowa", "zasięg izolacji obwodowej przeciwprzemarzaniowej XPS (PN-EN ISO 13793)"),
        ("uziom", "uziom otokowy — w gruncie pod warstwą XPS"),
        ("wyrownawczy", "przewód wyrównawczy funkcjonalny w płycie (połączony ze zbrojeniem)"),
        ("zacisk", "wyprowadzenie uziomu / złącze kontrolne (punkt stały uziemienia)"),
        ("przejscie", "przejście instalacyjne przez płytę (tuleja ochronna, szczelne)"),
        ("slup", "słup stalowy (baza na pogrubieniu płyty)")])))
    res.notes += _uwagi_fundamentow(D, m, fu, iz, n_prz)
    kol = kolizje_napisow(vp)
    if kol:
        ctx.note(f"{spec.get('nr', '')} {title}", f"kolizje napisów: {kol}")
    KD.zapisz_raporty(D, ctx)
    return vp, res, title


def _przejscie(vp, placer, xy, txt, r=0.15):
    k = vp.k
    C = np.asarray(xy, float)
    vp.circle(C, r, L_OBR, pen="srednia")
    vp.line(C - [r * 1.4, 0], C + [r * 1.4, 0], L_OBR, pen="cienka")
    vp.line(C - [0, r * 1.4], C + [0, r * 1.4], L_OBR, pen="cienka")
    placer.add(Point(*C).buffer(r * 1.2), "area", 1.0)
    etykieta(vp, placer, C, (1.0, 0.0), txt, None, 1.8, offs=(4.0, 7.0, 10.0), ts=(0.0, -0.6, 0.6, -1.2, 1.2),
             layer=L_OPS)


def _uziom(vp, placer, ctx, P, inst, res: KResult):
    """Uziom fundamentowy przy płycie na izolacji (PN-HD 60364-5-54 p. 542.2, PN-EN 62305-3 p. 5.4.2.2 i E.5.4.3.2):
    otok w gruncie POD warstwą XPS (izolacja odcina płytę od gruntu), przewód wyrównawczy funkcjonalny w płycie
    połączony ze zbrojeniem, połączenia otoku z przewodem wyrównawczym i wyprowadzenia (GSU, złącza kontrolne)."""
    k = vp.k
    m = ctx.model
    fu = m.fundamenty()
    obw = [e for e in fu.get("elementy") or [] if "os" in e and LineString(e["os"]).length > 1.0
           and P.exterior.distance(Point(*LineString(e["os"]).interpolate(0.5, normalized=True).coords[0])) < 0.5]
    d_otok = float(np.median([P.exterior.distance(Point(*LineString(e["os"]).interpolate(0.5, normalized=True).coords[0]))
                              for e in obw])) if obw else 0.3
    otok = P.buffer(-max(d_otok, 0.1), join_style=2).exterior
    wyr = P.buffer(-max(d_otok, 0.1) - 0.25, join_style=2).exterior
    vp.geom(otok, L_UZ, pen=0.5, lt="KRESKOWA", color=KOL_UZ)
    vp.geom(wyr, L_UZ, pen=0.35, lt="PUNKTOWA", color=KOL_UZ)
    placer.add_lines(otok, w=0.5)
    placer.add_lines(wyr, w=0.5)
    # połączenia otok ↔ przewód wyrównawczy w narożach wypukłych obrysu (odstęp ≤ 20 m po obwodzie)
    cs = list(P.exterior.coords)[:-1]
    xs = [c[0] for c in cs]
    ys = [c[1] for c in cs]
    naroza = [(min(xs), min(ys)), (max(xs), min(ys)), (max(xs), max(ys)), (min(xs), max(ys))]
    polacz = []
    for c in naroza:
        a = otok.interpolate(otok.project(Point(*c)))
        b = wyr.interpolate(wyr.project(Point(*c)))
        vp.line((a.x, a.y), (b.x, b.y), L_UZ, pen=0.35, color=KOL_UZ)
        vp.dot((a.x, a.y), 1.0, L_UZ, color=KOL_UZ)
        vp.dot((b.x, b.y), 1.0, L_UZ, color=KOL_UZ)
        polacz.append((a, b))
    L_obw = otok.length
    # wyprowadzenia: GSU przy rozdzielnicy (instalacje.lokalizacje.RG) + złącza kontrolne LPS w narożach
    wypr = []
    rg = (inst.get("lokalizacje") or {}).get("RG")
    if rg:
        q = wyr.interpolate(wyr.project(Point(rg[0], rg[1])))
        wypr.append(((q.x, q.y), "wyprowadzenie do GSU (główna szyna uziemiająca przy RG)"))
    for a, b in polacz:
        wypr.append(((a.x, a.y), "złącze kontrolne — przewód odprowadzający LPS"))
    for i, (xy, txt) in enumerate(wypr):
        C = np.asarray(xy, float)
        vp.circle(C, 1.3 * k, L_UZ, pen=0.35, color=KOL_UZ)
        vp.line(C - np.array([0.9, 0.9]) * k, C + np.array([0.9, 0.9]) * k, L_UZ, pen=0.35, color=KOL_UZ)
        placer.add(Point(*C).buffer(1.6 * k), "area", 1.0)
        if i < 2:
            etykieta(vp, placer, C, (1.0, 0.0), txt, None, 1.8, offs=(4.0, 7.0, 10.0), ts=(0.0, -1.0, 1.0, -2.0, 2.0),
                     layer=L_OPS)
    etykieta(vp, placer, np.asarray(otok.interpolate(0.12, normalized=True).coords[0]), (1.0, 0.0),
             "uziom otokowy: pręt nierdzewny V4A Ø10 w gruncie pod XPS", None, 1.8, offs=(3.0, 6.0, 9.0),
             ts=(0.0, -2.0, 2.0), layer=L_OPS)
    etykieta(vp, placer, np.asarray(wyr.interpolate(0.62, normalized=True).coords[0]), (1.0, 0.0),
             "przewód wyrównawczy funkcjonalny FeZn 30×4 w płycie", None, 1.8, offs=(3.0, 6.0, 9.0),
             ts=(0.0, -2.0, 2.0), layer=L_OPS)
    res.notes.append(
        f"Uziom fundamentowy (PN-HD 60364-5-54 p. 542.2.3, PN-EN 62305-3 p. 5.4.2.2 i E.5.4.3.2; praktyka DIN 18014): "
        f"płyta na XPS jest odizolowana od gruntu — uziom otokowy ze stali nierdzewnej V4A (1.4571) Ø10 mm lub "
        f"30×3,5 mm ułożyć w gruncie POD warstwą XPS wzdłuż żeber obwodowych (obwód ≈ {_pl(L_obw, 1)} m); w płycie "
        f"przewód wyrównawczy funkcjonalny FeZn 30×4 (lub Ø10) połączony ze zbrojeniem co ≤ 2 m (zaciski), oczka ≤ "
        f"20 × 20 m; połączenia otoku z przewodem wyrównawczym (stal nierdzewna przez izolację, szczelnie) w "
        f"{len(polacz)} narożach (odstęp po obwodzie ≤ 20 m); wyprowadzenia (V4A, min. 1,5 m zapasu) do GSU i złączy "
        f"kontrolnych LPS (jeżeli LPS wymagany wg analizy ryzyka PN-EN 62305-2). Połączenia — zaciski wg PN-EN 62561-1; "
        f"pomiar ciągłości i rezystancji przed betonowaniem (protokół). Trasa i wyprowadzenia do uzgodnienia z branżą E.")


def _przekroje_fund(ctx, liniowe) -> list:
    """Przekroje charakterystyczne fundamentu: 1 — żebro obwodowe (najdłuższe przy krawędzi), 2 — żebro wewnętrzne
    (najdłuższe), 3 — pogrubienie pod słupem (pierwsze). Zwraca [(etykieta, id elementu, położenie 0…1)]."""
    D = KD.dane(ctx)
    if "przekroje_fund" in D.cache:
        return D.cache["przekroje_fund"]
    m = ctx.model
    plyty = [Polygon(e["obrys"]) for e in (m.fundamenty().get("elementy") or []) if "obrys" in e]
    P = unary_union(plyty) if plyty else None
    out = []
    dl = [e for e in liniowe if LineString(e["os"]).length >= float(e.get("b", 0.6))]
    if P is not None:
        ob = [e for e in dl if P.exterior.distance(Point(*LineString(e["os"]).interpolate(0.5, normalized=True).coords[0])) < 0.5]
        wn = [e for e in dl if e not in ob]
    else:
        ob, wn = dl, []
    if ob:
        out.append(("1", str(max(ob, key=lambda e: LineString(e["os"]).length)["id"]), 0.3))
    if wn:
        out.append(("2", str(max(wn, key=lambda e: LineString(e["os"]).length)["id"]), 0.5))
    kr = [e for e in liniowe if LineString(e["os"]).length < float(e.get("b", 0.6))]
    if kr:
        out.append(("3", str(kr[0]["id"]), 0.5))
    D.cache["przekroje_fund"] = out
    return out


def _uwagi_fundamentow(D, m, fu, iz, n_prz) -> list:
    geo = m.raw.get("geotechnika") or {}
    gr = geo.get("grunt") or {}
    kon = m.raw.get("konstrukcja") or {}
    out = [
        f"Posadowienie bezpośrednie — {fu.get('uwagi', '')} Kategoria geotechniczna {geo.get('kategoria', '?')}; "
        f"grunt: {gr.get('rodzaj', '?')}, φ' = {gr.get('phi', '?')}°, γ = {gr.get('gamma', '?')} kN/m³, "
        f"M₀ = {gr.get('M0', '?')} kPa; ZWG {fmt.level(float(geo.get('ZWG', 0)))}, h_z = {geo.get('h_z', '?')} m "
        f"(PN-EN 1997-1 + NA; dane wg modelu — do potwierdzenia dokumentacją badań podłoża).",
        f"Beton fundamentu: {(kon.get('beton') or {}).get('fundament', '')}; otulina: wierzch {D.c_fund[0]:.0f} mm, "
        f"spód i czoła (na XPS/podsypce) {D.c_fund[1]:.0f} mm (PN-EN 1992-1-1 4.4.1.3(4) + NA). Stal "
        f"{kon.get('stal_zbrojeniowa', 'B500SP')}. Zbrojenie — arkusz zbrojenia płyty fundamentowej.",
    ]
    if iz:
        out.append(f"Izolacja obwodowa przeciwprzemarzaniowa: {iz.get('opis', '')} — typ {iz.get('typ')}, szerokość "
                   f"D = {_pl(float(iz.get('D', 1.0)), 2)} m, grubość d_n = {_cm(float(iz.get('d_n', 0.1)))} cm "
                   f"({iz.get('mat')}), głębokość {_pl(float(iz.get('glebokosc', 0.45)), 2)} m p.p.t. — "
                   f"PN-EN ISO 13793 (zastępuje wymaganie posadowienia poniżej h_z; uzasadnienie — obliczenia wg "
                   f"normy dla strefy klimatycznej lokalizacji).")
    if n_prz:
        out.append(f"Przejścia instalacyjne ({n_prz}) wykonać w tulejach ochronnych (rury osłonowe PVC/PE osadzone przed "
                   "betonowaniem), szczelnie w warstwie przeciwwilgociowej/przeciwradonowej (kołnierze systemowe); "
                   "położenie wg projektów branż S i E — koordynacja przed betonowaniem.")
    bad = []
    for z in D.zebra + D.stopy:
        if z.niesp:
            bad.append(f"{z.id}: {z.niesp[0]}")
    if bad:
        out.append("UWAGA — obliczenia (biblioteka, model ław/stóp izolowanych) wykazują niespełnione warunki: "
                   + "; ".join(bad[:6]) + ("…" if len(bad) > 6 else "") + ". Model ław nie uwzględnia współpracy z "
                   "płytą i izolacji obwodowej (PN-EN ISO 13793) — wymagana analiza płyty z żebrami na podłożu "
                   "sprężystym i ocena głębokości przemarzania [WYMAGA ANALIZY].")
    if D.plyta_f is not None:
        out += D.plyta_f.uwagi
    return out


# ------------------------------------------------------------------------------------------------ zbrojenie fundamentu
def widok_zbrojenie_fundamentu(ctx: ViewContext, spec: dict, scale: float, opts: dict):
    D = KD.dane(ctx)
    m = ctx.model
    F = D.plyta_f
    PF = KD.prety_fundamentu(D)
    warstwa = "gora" if str(spec.get("warstwa", "dolna")).lower().startswith("g") else "dol"
    title = spec.get("tytul_widoku") or (f"ZBROJENIE {'GÓRNE' if warstwa == 'gora' else 'DOLNE'} PŁYTY FUNDAMENTOWEJ"
                                         + (f" {F.id}" if F else ""))
    vp = Viewport(scale, title)
    res = KResult(north=True)
    placer = Placer(vp.k)
    nr_ark = spec.get("nr", "")
    els = [e for e in (m.fundamenty().get("elementy") or [])]
    P = F.poly if F is not None else unary_union([LineString(e["os"]).buffer(float(e.get("b", 0.6)) / 2)
                                                  for e in els if "os" in e])
    vp.geom(P, L_OBR, pen="gruba")
    placer.add_lines(P.boundary, w=0.6, buf_mm=0.6)
    osie_i_wymiary(vp, ctx, P.bounds, placer, sides=("dol", "lewo"))
    for e in els:
        if "os" not in e:
            continue
        ln = LineString(e["os"])
        B = float(e.get("b", 0.6))
        g = ln.buffer(B / 2, cap_style=3 if ln.length < B else 2)
        vp.geom(g, L_OBR, pen="srednia", lt="KRESKOWA")
        placer.add_lines(g.boundary, w=0.3)
    for g in PF[warstwa]:
        rysuj_grupe(vp, placer, g, opis=False)
    for g in sorted(PF[warstwa], key=lambda q: -LineString(q.linia).length):
        a, b = np.asarray(g.linia[0]), np.asarray(g.linia[1])
        L = float(np.hypot(*(b - a)))
        etykieta(vp, placer, (a + b) / 2, b - a, opis_grupy(g), g.pret.nr, 2.5,
                 ts=[0.0] + [s_ * f * L for f in (0.15, 0.3) for s_ in (-1, 1)], bounds=P.buffer(2.0))
        w = g.wym
        KD.rejestruj(D, F.id, f"siatka {'dolna' if warstwa == 'dol' else 'górna'} {g.kier}", F.poz, w.As_req, w.As_min,
                     KD.pole_preta(g.pret.fi) * 1000 / g.s, f"Ø{g.pret.fi} co {g.s / 10:g}", s=g.s,
                     s_max=KD.s_max_plyty(F.h), As_max=0.04 * F.h * 1e6, arkusz=nr_ark,
                     uwagi="pasmo Winklera bez żeber — patrz uwagi arkusza [WYMAGA ANALIZY]" if F.uwagi else "")
    przek = {eid: nm for nm, eid, _ in _przekroje_fund(ctx, [e for e in els if "os" in e])}
    for Z in D.zebra:
        z = PF["zebra"].get(Z.id)
        if z is None:
            continue
        e = next(x for x in els if str(x.get("id")) == Z.id)
        ln = LineString(e["os"])
        txt = (f"{Z.id}: dołem {z['n_dol']}Ø{z['dol'].fi} (poz. {z['dol'].nr}), górą {z['n_gora']}Ø{z['gora'].fi} "
               f"(poz. {z['gora'].nr}), strz. Ø{z['strz'].fi} co {Z.strz[1] / 10:g} (poz. {z['strz'].nr})"
               + (f" — przekrój {przek[Z.id]}-{przek[Z.id]}" if Z.id in przek else ""))
        u = np.asarray(e["os"][1], float) - np.asarray(e["os"][0], float)
        etykieta(vp, placer, np.asarray(ln.interpolate(0.5, normalized=True).coords[0]), u, txt, None, 1.8,
                 offs=(Z.b * 1000 / scale / 2 + 1.2, Z.b * 1000 / scale / 2 + 4.5),
                 ts=(0.0, -0.3 * ln.length, 0.3 * ln.length), layer=L_OPS)
        As_p = (Z.dol[0] + Z.gora[0]) * KD.pole_preta(Z.dol[1])
        KD.rejestruj(D, Z.id, "żebro — zbrojenie podłużne (dół + góra)", Z.poz, 0.0, Z.As_dol[1], As_p,
                     f"{Z.dol[0]}+{Z.gora[0]} Ø{Z.dol[1]}", jedn="mm²", arkusz=nr_ark,
                     uwagi="; ".join(Z.niesp[:2]))
    for S_ in D.stopy:
        st = PF["stopy"].get(S_.id)
        if st is None:
            continue
        g = box(S_.xy[0] - S_.L / 2, S_.xy[1] - S_.B / 2, S_.xy[0] + S_.L / 2, S_.xy[1] + S_.B / 2)
        placer.add(g, "area", 0.3)
        if warstwa == "dol":
            txt = f"{S_.id}: siatka dołem {st['n1']}+{st['n2']} Ø{S_.siatka.fi} co {S_.siatka.s / 10:g} (poz. {st['x'].nr}, {st['y'].nr})"
            etykieta(vp, placer, (S_.xy[0], S_.xy[1] - S_.B / 2), (1.0, 0.0), txt, None, 1.8, offs=(2.0, 5.0, 8.0),
                     ts=(0.0, -0.8, 0.8), layer=L_OPS)
        w = S_.siatka
        KD.rejestruj(D, S_.id, "pogrubienie — siatka dolna", S_.poz, w.As_req, w.As_min, KD.pole_preta(w.fi) * 1000 / w.s,
                     f"Ø{w.fi} co {w.s / 10:g}", s=w.s, s_max=KD.s_max_plyty(S_.h), arkusz=nr_ark,
                     uwagi="; ".join(S_.niesp[:1]))
    if PF["naroza"] is not None and warstwa == "dol":
        res.notes.append(f"Naroża żeber obwodowych: pręty narożne L (poz. {PF['naroza'].nr}) {PF['naroza'].n} Ø"
                         f"{PF['naroza'].fi}, ramiona l₀ = {PF['naroza'].wym[0] / 10:g} cm — po 2 dołem i 2 górą w każdym "
                         "narożu i na styku żeber (ciągłość zbrojenia podłużnego, PN-EN 1992-1-1 8.7).")
    res.column_blocks.append(("legenda_k", blok_legendy(_legenda_zbrojenia(warstwa)[:4] + [
        ("kreskowa", "żebra i pogrubienia pod płytą (zbrojenie — przekroje 1-1, 2-2, 3-3)")])))
    res.column_blocks.append(("zestawienie", blok_zestawienia(
        PF["zest"], "ZESTAWIENIE STALI — FUNDAMENT (płyta, żebra, pogrubienia)",
        _stopka_fund(D), PF["zest"].masa)))
    res.notes += UWAGI_ZBR[:3] + [
        f"Siatki płyty (dół i góra): Ø{F.dol.fi} co {F.dol.s / 10:g} cm w obu kierunkach — dobór modułu "
        f"(`dobierz_siatke`) z A_s,req/A_s,min biblioteki (poz. {F.poz}); pręty > 12 m łączone na zakład (mijankowo).",
        "Kolejność robót: podsypka zagęszczona (I_s ≥ 0,98) → XPS (płyty układane mijankowo, szczelnie) → folia PE → "
        "zbrojenie żeber i płyty, uziom/przewód wyrównawczy, tuleje przejść → betonowanie płyty z żebrami jednym "
        "zabiegiem (bez przerw roboczych) → pielęgnacja ≥ 7 dni (PN-EN 13670 p. 8.5).",
    ] + (F.uwagi if F is not None else [])
    kol = kolizje_napisow(vp)
    if kol:
        ctx.note(f"{nr_ark} {title}", f"kolizje napisów: {kol}")
    KD.zapisz_raporty(D, ctx)
    return vp, res, title


def _stopka_fund(D) -> list:
    F = D.plyta_f
    out = []
    if F is not None:
        out.append(f"Beton {F.beton}, klasa ekspozycji {F.eksp}; otulina: wierzch {D.c_fund[0]:.0f} mm, spód i boki "
                   f"{D.c_fund[1]:.0f} mm (PN-EN 1992-1-1 tabl. 4.4N + 4.4.1.3(4), NA); stal {KD.GATUNEK}.")
        from ..obliczenia.konstrukcja import zelbet
        from ..obliczenia.konstrukcja.materialy import Beton
        zz = []
        for fi in sorted({p.fi for p in KD.prety_fundamentu(D)["zest"].prety}):
            z = zelbet.zakotwienie(fi, Beton.z_parametrow(F.beton))
            zz.append(f"Ø{fi}: l_bd = {z.l_bd / 10:.0f} cm, l₀ = {z.l_0 / 10:.0f} cm")
        out.append("Zakotwienia/zakłady (8.4, 8.7, dobre warunki, 50 % łączonych): " + "; ".join(zz) + ".")
    return out


# ================================================================================================ rejestracja
def widok_zbrojenie(ctx: ViewContext, spec: dict, scale: float, opts: dict):
    """Dyspozytor typu ``k_zbrojenie``: element = strop | plyta | fundament | belki | nadproza | schody | wsporniki."""
    el = str(spec.get("element", "strop")).lower()
    fn = _ZBROJENIE.get(el)
    if fn is None:
        raise ValueError(f"k_zbrojenie: nieznany element '{el}' ({' | '.join(_ZBROJENIE)})")
    return fn(ctx, spec, scale, opts)


_ZBROJENIE = {"strop": widok_zbrojenie_plyt, "plyta": widok_zbrojenie_plyt, "stropodach": widok_zbrojenie_plyt,
              "fundament": widok_zbrojenie_fundamentu}

register_view("k_zbrojenie", widok_zbrojenie, "rysunek zbrojenia")

register_view("k_strop", widok_strop, "rzut konstrukcji")
register_view("k_fundamenty", widok_fundamenty, "rzut fundamentów")
