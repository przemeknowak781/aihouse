"""Rysunek zbrojenia słupów żelbetowych w murze (trzpieni) — arkusz PT-BO (typ ``k_zbrojenie``, ``element: slupy``).

Dane wyłącznie z obliczeń ``lamela.obliczenia.konstrukcja`` (pozycje słupów: ``dane["zbrojenie"]``, ``dane["strzemiona"]``,
wymiary z modelu). Słupy o tym samym przekroju, zbrojeniu i wysokości — jeden rysunek (lista w tytule). Widok: elewacja
trzpienia (pręty podłużne z zakładem nad głowicą/zakotwieniem w fundamencie, strzemiona zagęszczone przy końcach
— PN-EN 1992-1-1 9.5.3(4)), przekrój A-A (pręty, strzemię), zestawienie stali; rejestracja w kontroli zbrojenia.
"""
from __future__ import annotations

import math
import re

from shapely.geometry import Point, box

from ..draft import hatch as H
from ..draft.core import Viewport
from . import konstrukcja_dane as KD
from .common import Placer

L_OBR, L_ZBR, L_OPI, L_OPS = "K-KONSTR", "K-ZBROJENIE", "K-ZBROJENIE-OPIS", "A-OPISY"


def _grupy(D):
    m = D.an.m
    out = {}
    for pz in D.an.pos_slupy:
        zb = pz.dane.get("zbrojenie")
        if not zb:
            continue
        c = next(c_ for c_ in m.slupy() if str(c_["id"]) == pz.ident)
        from ..obliczenia.konstrukcja.pozycje import _wymiary_slupa
        a, b = _wymiary_slupa(str(c.get("przekroj")))
        L = float(c["z_do"]) - float(c["z_od"])
        key = (round(min(a, b), 3), round(max(a, b), 3), zb, pz.dane.get("strzemiona"), round(L, 2))
        out.setdefault(key, []).append((pz, c))
    return out


def widok_zbrojenie_slupow(ctx, spec: dict, scale: float, opts: dict):
    from .konstrukcja import KResult, blok_zestawienia, etykieta
    from ..obliczenia.konstrukcja.materialy import pole_preta
    D = KD.dane(ctx)
    nr_ark = spec.get("nr", "")
    title = spec.get("tytul_widoku") or "ZBROJENIE SŁUPÓW ŻELBETOWYCH W MURZE"
    vp = Viewport(scale, title)
    placer = Placer(vp.k)
    k = vp.k
    res = KResult()
    zest = KD.Zestawienie()
    c_nom = 30.0
    X = 0.0
    for (h, b, zb, strz, L), lst in _grupy(D).items():
        n_fi = KD.n_fi(zb) or (4, 12)
        fs = KD.fi_s(strz) or (6, 180.0)
        s_red = float(re.findall(r"co (\d+(?:,\d+)?) cm", strz or "")[-1].replace(",", ".")) * 10 if strz and "co" in strz else fs[1]
        n, fi = n_fi
        c = c_nom / 1000.0
        ids = ", ".join(str(q[1]["id"]) for q in lst)
        poz = ", ".join(q[0].nr for q in lst)
        l0 = 0.60                                  # zakład/zakotwienie nad głowicą i w fundamencie [m] (≥ l₀, l_bd — 8.4, 8.7)
        p_l = zest.dodaj(KD.Pret(fi, "00", ((L + l0) * 1000,), n * len(lst), ids, "podłużne"))
        ns = int(math.ceil(L / (fs[1] / 1000.0))) + 1 + 2 * int(math.ceil(max(b, 0.3) / (s_red / 1000.0)))
        p_s = zest.dodaj(KD.Pret(fs[0], "51", ((b - 2 * c) * 1000, (h - 2 * c) * 1000), ns * len(lst), ids, "strzemię"))
        # elewacja (dłuższy bok b w płaszczyźnie rysunku)
        x0, y0 = X, 0.0
        g = box(x0, y0, x0 + b, y0 + L)
        H.hatch(vp, g, "ZELBET")
        vp.geom(g, L_OBR, pen="gruba")
        k_bok = n // 2
        xs = [x0 + c + fs[0] / 1000 + fi / 2000 + i * (b - 2 * (c + fs[0] / 1000) - fi / 1000) / max(k_bok - 1, 1)
              for i in range(k_bok)]
        for xx in xs:
            vp.line((xx, y0 - 0.35), (xx, y0 + L + l0 - 0.35), L_ZBR, pen=0.5)
        yy, zag = y0 + 0.05, max(b, 0.30)
        while yy <= y0 + L - 0.05:
            vp.line((x0 + c, yy), (x0 + b - c, yy), L_ZBR, pen=0.25)
            dz = s_red / 1000.0 if (yy - y0 < zag or y0 + L - yy < zag) else fs[1] / 1000.0
            yy += dz
        etykieta(vp, placer, (xs[len(xs) // 2], y0 + 0.6 * L), (0, 1), f"{n} Ø{fi} l={p_l.L_mm / 10:g}", p_l.nr, 2.5,
                 offs=(b * 1000 / vp.scale + 4.0, 10.0))
        etykieta(vp, placer, (x0 + b / 2, y0 + 0.3 * L), (0, 1), f"Ø{fs[0]} co {fs[1] / 10:g} (przy końcach co {s_red / 10:g})",
                 p_s.nr, 2.5, offs=(b * 1000 / vp.scale + 4.0, 14.0))
        vp.text((x0, y0 + L + l0 + 6 * k), f"{ids} — słup ŻB {h * 100:.0f} × {b * 100:.0f} cm, L = {L:.2f} m (poz. {poz})".replace(".", ","),
                3.0, 0, "left", "baseline", L_OPS, style="bold")
        # przekrój A-A
        sx, sy = x0, y0 - 0.35 - 14 * k - h
        gs = box(sx, sy, sx + b, sy + h)
        H.hatch(vp, gs, "ZELBET")
        vp.geom(gs, L_OBR, pen="gruba")
        vp.rect(sx + c + fs[0] / 2000, sy + c + fs[0] / 2000, sx + b - c - fs[0] / 2000, sy + h - c - fs[0] / 2000, L_ZBR, pen=0.35)
        for xx in xs:
            for yb in (sy + c + fs[0] / 1000 + fi / 2000, sy + h - c - fs[0] / 1000 - fi / 2000):
                vp.fill(Point(xx - x0 + sx, yb).buffer(max(fi / 2000, 0.45 * k), 16), L_ZBR, "#000000")
        vp.text((sx + b / 2, sy - 6 * k), "A-A", 3.0, 0, "center", "baseline", L_OPS, style="bold")
        placer.add(box(x0 - 2 * k, sy - 8 * k, x0 + b + 60 * k, y0 + L + l0 + 10 * k), "area", 1.0)
        As = n * pole_preta(fi)
        As_min = max(0.002 * h * b * 1e6, 4 * pole_preta(12))
        for pz, cc in lst:
            KD.rejestruj(D, str(cc["id"]), "podłużne (symetryczne, M_Rd(N_Ed) ≥ M_Ed — 5.8.8)", pz.nr, As, As_min, As,
                         f"{n}Ø{fi}", jedn="mm²", As_max=0.04 * h * b * 1e6, arkusz=nr_ark,
                         uwagi="; ".join(KD.warunki_niespelnione(pz.wyniki)[:2]), wymuszone_ok=pz.ok)
        X += b + 75 * k
    res.column_blocks.append(("zestawienie", blok_zestawienia(zest, "ZESTAWIENIE STALI — SŁUPY ŻB", [
        "Beton C30/37, XC1, c_nom = 30 mm; stal B500SP. Trzpienie betonowane po wymurowaniu ścian (strzępia muru, "
        "kotwy stalowe co 2 warstwy) lub w szalunku przed murowaniem; pręty podłużne ciągłe przez wieniec/belkę "
        "(zakład l₀ ≥ 50φ), zakotwione w pogrubieniu płyty fundamentowej (l_bd)."], None)))
    res.notes += [
        "Słupy żelbetowe w murze (trzpienie) w węzłach obciążeń skupionych — wymiarowanie: obliczenia statyczne, poz. 8 "
        "(ściskanie mimośrodowe z efektami II rzędu — metoda nominalnej krzywizny, PN-EN 1992-1-1 5.8.8).",
        "Strzemiona zagęszczone (0,6·s) na długości ≥ większego wymiaru przekroju przy głowicy i podstawie (9.5.3(4)); "
        "pręty podłużne w narożach strzemion (9.5.3(6)).",
        "Słupy o tym samym przekroju, zbrojeniu i wysokości — jeden rysunek (lista w tytule); liczby sztuk w zestawieniu łącznie.",
    ]
    KD.zapisz_raporty(D, ctx)
    return vp, res, title
