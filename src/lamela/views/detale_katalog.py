"""Budowniczy detali PT (architektura) — geometria z przegród i elementów `model/budynek.yaml`.

Każdy budowniczy: fn(model, opts) -> `Detal` (układ lokalny: x w prawo = na zewnątrz, wnętrze x < 0 — o ile opis nie
mówi inaczej; y w górę; `Detal.z0` — rzędna poziomu y = 0 względem ±0,00). Grubości warstw zawsze z modelu
(`Detal.stos_v/stos_h`); elementy wykonawcze spoza modelu (obróbki, taśmy, profile, rynny) — wymiary typowe [ZAŁ]
opisane na rysunku. Konwencja płyt wg audytu A2 (K-1): stropy do lica konstrukcji, wierzch płyt wspornikowych
zrównany ze stropem, łącznik termoizolacyjny w strefie izolacji.

`RODZAJE` — rodzaj → budowniczy; `WEZEL_RODZAJ` — id węzła sekcji `wezly` → rodzaj detalu.
"""
from __future__ import annotations

import numpy as np

from .detale_geom import Detal, mm, skrot_nazwy

RODZAJE: dict = {}
WEZEL_RODZAJ: dict = {}


def rodzaj(nazwa: str, *wezly: str):
    def dec(fn):
        RODZAJE[nazwa] = fn
        for w in wezly:
            WEZEL_RODZAJ.setdefault(w, nazwa)
        return fn
    return dec


# ---------------------------------------------------------------------------------------------- pomocnicze
def wpis(m, wid: str) -> dict:
    return next((e for e in (m.raw.get("wezly") or []) if str(e.get("id")) == wid), {})


def przegroda_typu(m, wid: str, typ: str, domyslna: str | None = None) -> str | None:
    for k in wpis(m, wid).get("przegrody") or []:
        p = m.przegroda(k)
        if p is not None and p.typ == typ:
            return k
    if domyslna and m.przegroda(domyslna) is not None:
        return domyslna
    return next((k for k, p in m.przegrody.items() if p.typ == typ), None)


def grubosc(m, kod: str) -> float:
    return float(sum(w.d for w in m.przegroda(kod).warstwy))


def teren(m) -> float:
    """Rzędna terenu przy budynku [m wzgl. ±0,00] — z modelu (energia.wentylacja.rzedna_terenu), inaczej −0,30."""
    e = (m.raw.get("energia") or {}).get("wentylacja") or {}
    try:
        return float(e.get("rzedna_terenu", -0.30))
    except (TypeError, ValueError):
        return -0.30


def x_konstr(stos) -> tuple[float, float]:
    """(lico wewn., lico zewn.) warstwy konstrukcyjnej ze stosu stos_v."""
    for a, b, w in stos:
        if w["konstr"]:
            return a, b
    return stos[0][0], stos[-1][1]


def x_izol(stos) -> tuple[float, float]:
    """(lico wewn., lico zewn.) warstwy izolacji cieplnej ściany (pierwsza warstwa λ ≤ 0,06 za konstrukcją)."""
    k = next(i for i, (_a, _b, w) in enumerate(stos) if w["konstr"])
    for a, b, w in stos[k + 1:]:
        if w["mat"] in ("EPS031", "WELNA_FAS", "XPS300", "WELNA_035", "PIR022") or "izol" in w.get("funkcja", ""):
            return a, b
    return stos[k][1], stos[-1][1]


def fundament_pod(m, x_os: float = 0.0) -> dict:
    """Płyta fundamentowa i żebro pod ścianą zewnętrzną (pierwsze pogrubienie) z modelu."""
    f = m.fundamenty() or {}
    el = f.get("elementy") or []
    plyta = next((e for e in el if "obrys" in e), {})
    zebro = next((e for e in el if "os" in e and float(e.get("b", 0)) >= 0.5), {})
    return {"plyta": plyta, "zebro": zebro, "obwodowa": f.get("izolacja_obwodowa") or {}}


def tekst(det: Detal, mat: str, d: float | None = None, dopisek: str = "") -> str:
    n, _l, _k = det.mat_info(mat)
    s = skrot_nazwy(n)
    return s + (f" — {mm(d)} mm" if d else "") + (f" {dopisek}" if dopisek else "")


# ================================================================================================ D — cokół
@rodzaj("cokol", "WZ-08")
def detal_cokol(m, opts: dict) -> Detal:
    """Cokół: ściana zewnętrzna na płycie fundamentowej z XPS (żebro pod ścianą), izolacja obwodowa, opaska."""
    det = Detal(m, "D-01", "Cokół — ściana zewn. na płycie fundamentowej z XPS", ("WZ-08",), 10)
    sz = przegroda_typu(m, "WZ-08", "sciana_zewn", "SZ1")
    pd = przegroda_typu(m, "WZ-08", "podloga_na_gruncie", "POD-0")
    f = fundament_pod(m)
    tz = teren(m)
    y_cok = tz + 0.30                                      # górna krawędź strefy cokołowej (≥ 30 cm nad terenem)
    xL, xR, yT, yB = -0.30, 0.72, 0.55, -1.05
    det.okno = (xL, yB, xR, yT)
    W = det.warstwy(pd)
    ki = next(i for i, w in enumerate(W) if w["konstr"])
    y_pl = -sum(w["d"] for w in W[:ki])                    # wierzch płyty
    t_pl = W[ki]["d"]
    # ściana (od wnętrza): tynk i mur od wierzchu płyty, izolacja i wyprawa od górnej krawędzi cokołu
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    zak = {w["idx"]: (y_pl if i <= ks else y_cok, yT) for i, w in enumerate(Ws)}
    zak[Ws[0]["idx"]] = (0.0, yT)
    sc = det.stos_v(sz, 0.0, y_pl, yT, zakres=zak)
    xs0, xs1 = x_konstr(sc)
    xi0, xi1 = x_izol(sc)
    x_out = sc[-1][1]
    # podłoga + płyta do lica konstrukcji (konwencja A2), izolacje pod płytą
    zb = f["zebro"]
    b_z, h_z = float(zb.get("b", 0.6)), float(zb.get("h", 0.3))
    iw = {w["idx"]: w for w in W}
    zakres = {w["idx"]: (xL, 0.0) for w in W[:ki]}
    for w in W[:ki]:
        if w["d"] < 0.006:
            zakres[w["idx"]] = (xL, xs1)                    # membrana SBS pod murem (izolacja pozioma)
    zakres[W[ki]["idx"]] = (xL, xs1)
    for w in W[ki + 1:]:
        zakres[w["idx"]] = (xL, xs1 - b_z)
    st = det.stos_h(pd, xL, 0.0, 0.0, zakres=zakres)
    y_spod = y_pl - t_pl
    det.rect(xs1 - b_z, y_spod - h_z, xs1, y_spod, W[ki]["mat"], konstr=True)        # żebro płyty pod ścianą
    xps = next((w for w in W[ki + 1:] if w["d"] >= 0.05), None)
    d_x = xps["d"] if xps else 0.20
    m_x = xps["mat"] if xps else "XPS300"
    y_zb = y_spod - h_z
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 - b_z, y_spod - d_x, m_x)              # XPS przy żebrze
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 + d_x, y_zb, m_x)                      # XPS pod żebrem
    det.rect(xs1, y_zb, xs1 + d_x, y_cok, m_x)                                       # XPS na czole płyty i cokole
    pod = [w for w in W[ki + 1:] if w["d"] >= 0.05 and w is not xps]
    if pod:
        det.rect(xs1 - b_z - d_x, y_zb - d_x - pod[0]["d"], xs1 + d_x, y_zb - d_x, pod[0]["mat"])
    det.rect(xs1 + d_x, tz - 0.15, x_out, y_cok, "TYNK_SIL" if "TYNK_SIL" in m.materialy else Ws[-1]["mat"])
    # grunt, opaska żwirowa, izolacja obwodowa
    ob = f["obwodowa"]
    d_n, D_n, gl = float(ob.get("d_n", 0.10)), float(ob.get("D", 1.0)), float(ob.get("glebokosc", 0.45))
    mat_o = ob.get("mat", "XPS300")
    x_g = xs1 + d_x
    det.rect(x_out, tz - 0.20, x_out + 0.50, tz, "ZWIR_16")
    det.rect(xs1 - b_z - d_x, yB, xR, tz, "GRUNT")
    det.rect(xL, yB, xs1 - b_z - d_x, y_spod - d_x - (pod[0]["d"] if pod else 0.0), "GRUNT")
    det.poly([(x_g, tz - gl), (x_g + D_n, tz - gl - 0.02 * D_n), (x_g + D_n, tz - gl - d_n - 0.02 * D_n),
              (x_g, tz - gl - d_n)], mat_o)
    det.cienka([(x_out + 0.50, tz), (x_out + 0.50, tz - 0.20), (x_out, tz - 0.20)], "GEOWL", "G")
    # 4 linie: H — membrana SBS na płycie + pod murem + na czole płyty i cokole muru do +30 cm nad terenem
    y_m = next((0.5 * (a + b) for a, b, w in st if w["d"] < 0.006 and "SBS" in w["mat"]), y_pl + 0.0025)
    det.linia("H", [(xs1 + 0.003, y_zb), (xs1 + 0.003, y_m), (xs1 + 0.003, y_cok)],
              "hydroizolacja pionowa (masa KMB / papa SBS) na czole płyty i cokole muru do +30 cm nad terenem")
    det.linia("S", [(0.0015, yT), (0.0015, y_pl - 0.004), (xL, y_pl - 0.004)], "tynk wewn. do płyty ŻB")
    det.linia("P", [(xL, y_m + 0.004), (0.0, y_m + 0.004)], "membrana SBS — bariera pary i radonu")
    # przerwy, opisy
    for p1, p2 in (((xL, yT), (x_out, yT)), ((xL, yB), (xR, yB)), ((xL, yT), (xL, yB)), ((xR, tz), (xR, yB))):
        det.przerwa(p1, p2)
    det.opis_stosu(sc, "y", 0.30, odwroc=True, tytul=f"{sz} — ściana zewnętrzna")
    det.opis([(xs1 + d_x / 2, tz + 0.12)], [f"{tekst(det, m_x, d_x)} — strefa cokołowa do +30 cm nad terenem, "
                                            "wyprawa mozaikowa na masie uszczelniającej"])
    det.opis([(xs1 + 0.003, y_spod - 0.05)], ["izolacja pionowa KMB / SBS połączona z membraną na płycie"])
    det.opis([(x_out + 0.30, tz - 0.10)], ["opaska żwirowa 16/32, szer. 50 cm, gr. 20 cm na geowłókninie; spadek "
                                           "terenu ≥ 2 % na 1,5–2 m"])
    det.opis([(x_g + 0.25, tz - gl - d_n / 2)], [f"izolacja obwodowa {skrot_nazwy(det.mat_info(mat_o)[0], 18)} "
                                                 f"{mm(d_n)} mm × {D_n:.2f} m, spadek 2 %".replace(".", ",")])
    det.opis([(xs1 - b_z / 2, y_spod - h_z / 2)], [f"żebro płyty {int(b_z * 100)}×{int(h_z * 100)} cm pod ścianą "
                                                   "zewn. (konstrukcja wg PT-K)"])
    det.opis_stosu(st, "x", -0.18, odwroc=True, wyjscie=(-0.18, yB - 0.02), tytul=f"{pd} — podłoga na gruncie",
                   pomin_cienkie=False)
    # wymiary, rzędne, spadek
    det.wymiar([(a, yT) for a, _b, _w in sc] + [(sc[-1][1], yT)], yT + 0.06, "h")
    det.wymiar([(x_out, tz), (x_out, y_cok)], x_out + 0.08, "v")
    det.rzedna((xL + 0.08, 0.0), 0.0, "zero", "right")
    det.rzedna((x_out + 0.62, tz), tz, "wyk", "left")
    det.spadek((x_out + 0.05, tz + 0.03), (x_out + 0.30, tz + 0.025), 2.0)
    det.uwagi.append("drenażu opaskowego nie projektuje się — decyzja w modelu działki (DR-0, W-285): piaski "
                     "średnie, ZWG ≈ 3,8 m p.p.t. (uzasadnienie: REKOMENDACJE mostków, rozdz. C)")
    return det
