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


def nazwa_lamel(det: Detal, lm: dict) -> str:
    """Nazwa materiału lamel bez wymiarów zapisanych w nazwie („Lamele … 40×80” → „Lamele …”)."""
    import re
    n = det.mat_info(lm.get("mat", "DREWNO_TERMO"))[0]
    n = re.sub(r"\s*\d+\s*[×x]\s*\d+\s*(mm)?\s*,?", "", n).strip(" ,—-")
    return skrot_nazwy(n, 40)


def tekst(det: Detal, mat: str, d: float | None = None, dopisek: str = "") -> str:
    n, _l, _k = det.mat_info(mat)
    s = skrot_nazwy(n)
    return s + (f" — {mm(d)} mm" if d else "") + (f" {dopisek}" if dopisek else "")


# ================================================================================================ D — cokół
@rodzaj("cokol", "WZ-08")
def detal_cokol(m, opts: dict) -> Detal:
    """Cokół: ściana zewnętrzna na płycie fundamentowej z XPS (żebro pod ścianą), izolacja obwodowa, opaska."""
    det = Detal(m, "D-01", "Cokół — ściana na płycie fundamentowej", ("WZ-08",), 10)
    sz = przegroda_typu(m, "WZ-08", "sciana_zewn", "SZ1")
    pd = przegroda_typu(m, "WZ-08", "podloga_na_gruncie", "POD-0")
    f = fundament_pod(m)
    tz = teren(m)
    y_cok = tz + 0.30                                      # górna krawędź strefy cokołowej (≥ 30 cm nad terenem)
    xL, xR, yT, yB = -0.30, float(opts.get("_xR", 0.72)), float(opts.get("_yT", 0.50)), float(opts.get("_yB", -1.05))
    det.okno = (xL, yB, xR, yT)
    W = det.warstwy(pd)
    ki = next(i for i, w in enumerate(W) if w["konstr"])
    y_pl = -sum(w["d"] for w in W[:ki])                    # wierzch płyty
    t_pl = W[ki]["d"]
    y_spod = y_pl - t_pl
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    zb = f["zebro"]
    b_z, h_z = float(zb.get("b", 0.6)), float(zb.get("h", 0.3))
    xps = next((w for w in W[ki + 1:] if w["d"] >= 0.05), None)
    d_x = xps["d"] if xps else 0.20
    m_x = xps["mat"] if xps else "XPS300"
    pod = [w for w in W[ki + 1:] if w["d"] >= 0.05 and w is not xps]
    d_p = pod[0]["d"] if pod else 0.0
    y_zb = y_spod - h_z
    # 1) grunt i opaska (najniższy priorytet — elementy budynku nadpisują)
    det.rect(xL - 0.5, yB - 0.1, xR + 0.1, tz, "GRUNT")
    det.rect(x_out, tz - 0.20, x_out + 0.50, tz, "ZWIR_16")
    # 2) ściana (od wnętrza): tynk od posadzki, mur od wierzchu płyty, izolacja i wyprawa od strefy cokołowej
    zak = {w["idx"]: (y_pl if i <= ks else y_cok, yT) for i, w in enumerate(Ws)}
    zak[Ws[0]["idx"]] = (0.0, yT)
    sc = det.stos_v(sz, 0.0, y_pl, yT, zakres=zak)
    # 3) podłoga i płyta do lica konstrukcji (konwencja A2), żebro, izolacje pod płytą
    zakres = {w["idx"]: (xL - 0.5, 0.0) for w in W[:ki]}
    for w in W[:ki]:
        if w["d"] < 0.006:
            zakres[w["idx"]] = (xL - 0.5, xs1)              # membrana SBS pod murem (izolacja pozioma)
    zakres[W[ki]["idx"]] = (xL - 0.5, xs1)
    for w in W[ki + 1:]:
        zakres[w["idx"]] = (xL - 0.5, xs1 - b_z)
    st = det.stos_h(pd, xL - 0.5, 0.0, 0.0, zakres=zakres)
    det.rect(xs1 - b_z, y_zb, xs1, y_spod, W[ki]["mat"], konstr=True)                 # żebro płyty pod ścianą
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 - b_z, y_spod - d_x, m_x)               # XPS przy żebrze
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 + d_x, y_zb, m_x)                       # XPS pod żebrem
    det.rect(xs1, y_zb, xs1 + d_x, y_cok, m_x)                                        # XPS na czole płyty i cokole
    if pod:
        det.rect(xs1 - b_z - d_x, y_zb - d_x - d_p, xs1 + d_x, y_zb - d_x, pod[0]["mat"])
    det.cienka([(xs1 - b_z - d_x, y_zb - d_x), (xs1 + d_x, y_zb - d_x)], "FOLIA_PE", "G")
    det.rect(xs1 + d_x, tz - 0.15, x_out, y_cok, "TYNK_SIL" if "TYNK_SIL" in m.materialy else Ws[-1]["mat"])
    # 4) izolacja obwodowa (spadek 2 % od budynku), geowłóknina opaski
    ob = f["obwodowa"]
    d_n, D_n, gl = float(ob.get("d_n", 0.10)), float(ob.get("D", 1.0)), float(ob.get("glebokosc", 0.45))
    mat_o = ob.get("mat", "XPS300")
    x_g = xs1 + d_x
    det.poly([(x_g, tz - gl), (x_g + D_n, tz - gl - 0.02 * D_n), (x_g + D_n, tz - gl - d_n - 0.02 * D_n),
              (x_g, tz - gl - d_n)], mat_o)
    det.cienka([(x_out + 0.50, tz), (x_out + 0.50, tz - 0.20), (x_out, tz - 0.20)], "GEOWL", "G")
    # 5) 4 linie
    y_m = next((0.5 * (a + b) for a, b, w in st if w["d"] < 0.006 and "SBS" in w["mat"]), y_pl + 0.0025)
    det.linia("H", [(xs1 + 0.003, y_zb), (xs1 + 0.003, y_m), (xs1 + 0.003, y_cok)],
              "hydroizolacja pionowa (masa KMB / papa SBS) na czole płyty i cokole muru do +30 cm nad terenem")
    det.linia("S", [(0.0015, yT), (0.0015, y_pl - 0.004), (xL, y_pl - 0.004)], "tynk wewn. do płyty ŻB")
    det.linia("P", [(xL, y_m + 0.004), (0.0, y_m + 0.004)], "membrana SBS — bariera pary i radonu")
    for p1, p2 in (((0.0, yT), (x_out, yT)), ((xL, yB), (xR, yB)), ((xL, 0.0), (xL, yB)), ((xR, tz), (xR, yB))):
        det.przerwa(p1, p2)
    # 6) opisy (prawa kolumna, od zewnątrz do wewnątrz)
    det.opis_stosu(sc, "y", 0.30, odwroc=True, tytul=f"{sz} — ściana zewnętrzna")
    det.opis([(xs1 + d_x / 2, tz + 0.12)], [f"{tekst(det, m_x, d_x)} — strefa cokołowa do +30 cm nad terenem, "
                                            "wyprawa mozaikowa na masie uszczelniającej"])
    det.opis([(xs1 + 0.003, y_spod - 0.05)], ["izolacja pionowa KMB / papa SBS na czole płyty, połączona "
                                              "z membraną SBS na płycie (pod murem)"])
    det.opis([(x_out + 0.30, tz - 0.10)], ["opaska żwirowa 16/32, szer. 50 cm, gr. 20 cm na geowłókninie; spadek "
                                           "terenu ≥ 2 % na 1,5–2 m"])
    det.opis([(x_g + 0.20, tz - gl - d_n / 2 - 0.004)],
             [f"izolacja obwodowa XPS {mm(d_n)} mm × {D_n:.2f} m (przeciwprzemarzaniowa), spadek 2 %".replace(".", ",")])
    top = [(a, b, w) for a, b, w in st[:ki + 1]]
    det.opis_stosu(top, "x", -0.18, odwroc=True, wyjscie=(-0.18, yB - 0.03), tytul=f"{pd} — podłoga na gruncie")
    det.opis([(xs1 - b_z / 2 + 0.05, y_zb - d_x / 2), (xs1 - b_z / 2 + 0.05, y_zb - d_x - d_p / 2)],
             [f"pod płytą i żebrem: {tekst(det, m_x, d_x)}, folia PE 0,2 mm", f"{tekst(det, pod[0]['mat'], d_p)}"
              if pod else "podsypka"])
    det.opis([(xs1 - b_z / 2 - 0.08, (y_spod + y_zb) / 2)], [f"żebro płyty {int(round(b_z * 100))}×"
                                                             f"{int(round(h_z * 100))} cm pod ścianą (wg PT-K)"])
    # 7) wymiary, rzędne, spadek
    det.wymiar([(a, yT) for a, _b, _w in sc] + [(sc[-1][1], yT)], yT + 0.06, "h")
    det.wymiar([(x_out, tz), (x_out, y_cok)], x_out + 0.05, "v")
    det.rzedna((xL + 0.06, 0.0), 0.0, "zero", "right")
    det.rzedna((xR - 0.03, tz), tz, "wyk", "left")
    det.spadek((x_out + 0.10, tz + 0.03), (x_out + 0.28, tz + 0.026), 2.0)
    det.pom = dict(sc=sc, x_out=x_out, xs1=xs1, d_x=d_x, tz=tz, y_cok=y_cok, x_g=x_g, gl=gl, d_n=d_n, D_n=D_n,
                   xL=xL, xR=xR, yT=yT, yB=yB, y_pl=y_pl)
    det.uwagi.append("drenażu opaskowego nie projektuje się — decyzja w modelu działki (DR-0, W-285): piaski "
                     "średnie, ZWG ≈ 3,8 m p.p.t. (uzasadnienie: REKOMENDACJE mostków, rozdz. C)")
    det.uwagi.append("żebro płyty licowane z czołem płyty (lico konstrukcji muru — audyt A2 K-1); w modelu żebro "
                     "osiowe 0,60 m — do ujednolicenia w PT-K")
    return det


# ================================================================================================ D — okno
def okno_reprezentatywne(m, kod_sz: str = "SZ1"):
    """Okno w ścianie `kod_sz` z parapetem (> 5 cm) i nadprożem z sekcji `belki` (uwagi „nadproże otworu …”)."""
    ok = [o for o in m.otwory() if o.sciana is not None and o.sciana.przegroda_kod == kod_sz and o.typ == "okno"
          and (o.parapet or 0.0) > 0.05]
    ok.sort(key=lambda o: (-o.szer * o.wys, o.id))
    for o in ok:
        b = next((b for b in m.belki() if o.id in str(b.get("uwagi", ""))), None)
        if b is not None:
            return o, b
    return (ok[0], None) if ok else (None, None)


def osadzenie(m, kod_sz: str) -> tuple[float, float]:
    try:
        from ..obliczenia.mostki2d.katalog import osadzenie_z_modelu
        o = osadzenie_z_modelu(m, kod_sz)
        return float(o["d_f"]), float(o["wsuniecie"])
    except Exception:      # pragma: no cover
        return 0.09, 0.05


def opis_stolarki(m, o) -> str:
    if o is None:
        return "stolarka"
    sym = (getattr(o, "raw", None) or {}).get("symbol")
    st = ((m.raw.get("stolarka") or {}).get(sym) or {}) if sym else {}
    u = st.get("U_w") or st.get("U_D")
    return (f"{sym or o.typ} {o.szer:.2f}×{o.wys:.2f} m".replace(".", ",")
            + (f", U = {u:.2f} W/(m²K)".replace(".", ",") if u else "") + " — wyrób przykładowy")


@rodzaj("okno", "WZ-11N", "WZ-11P", "WZ-11")
def detal_okno(m, opts: dict) -> Detal:
    """Osadzenie okna w ścianie z ETICS — ciepły montaż: podokiennik (dół) i nadproże (góra), przekrój pionowy
    z przerwą; taśmy paroszczelna / paroprzepuszczalna, parapety, izolacja ościeża z zakładem na ramę."""
    sz = przegroda_typu(m, "WZ-11N", "sciana_zewn", "SZ1")
    o, bl = okno_reprezentatywne(m, sz)
    H = float(o.wys) if o is not None else 1.50
    det = Detal(m, "D-02", "Okno — ciepły montaż (podokiennik i nadproże)", ("WZ-11P", "WZ-11N", "WZ-11"), 5)
    d_f, ws = osadzenie(m, sz)
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    xf0, xf1 = xs1 - ws, xs1 - ws + d_f                  # rama: `ws` w murze, reszta w ociepleniu
    g = 0.015                                            # szczelina montażowa [ZAŁ]
    hf = 0.11                                            # wysokość profilu ościeżnicy + skrzydła [ZAŁ, b_f]
    D = H - 0.62                                         # przesunięcie części górnej (przerwa widoku)
    y0, y1 = -0.28, 0.20                                 # część dolna
    zak = {w["idx"]: (y0, 0.0) for w in Ws}
    kx = next(i for i, w in enumerate(Ws) if i > ks and w["d"] >= 0.05)
    zak[Ws[kx]["idx"]] = (y0, -0.02)
    for w in Ws[kx + 1:]:
        zak[w["idx"]] = (y0, -0.02)
    sc = det.stos_v(sz, 0.0, y0, 0.0, zakres=zak)
    # podokiennik: profil XPS, pianka, parapety, rama
    det.poly([(xs1, -0.02), (x_out, -0.02), (x_out, 0.026), (xf1, 0.035), (xf1, g), (xs1, g)], "PROFIL_XPS")
    det.rect(xf0, 0.0, xs1, g, "PIANKA")
    det.rect(-0.03, 0.0, xf0 - 0.004, 0.025, "PARAPET_WEWN")
    det.rect(xf0, g, xf1, g + hf, "RAMA_ALU")
    xg = (xf0 + xf1) / 2
    det.rect(xg - 0.024, g + hf - 0.02, xg + 0.024, y1, "SZYBA3")
    det.obrobka([(xf1 - 0.006, 0.047), (xf1, 0.038), (x_out + 0.04, 0.027), (x_out + 0.04, 0.0)], strona=1)
    det.linia("H", [(xf1 + 0.0015, 0.05), (xf1 + 0.0015, 0.0355), (x_out + 0.004, 0.0265), (x_out + 0.004, -0.035)],
              "taśma / membrana pod parapetem")
    det.linia("T_in", [(xf0 - 0.0015, g + 0.03), (xf0 - 0.0015, 0.0015), (xf0 - 0.05, 0.0015)])
    det.linia("T_out", [(xf1 + 0.0035, g + 0.04), (xf1 + 0.0035, g)])
    det.linia("S", [(0.0015, y0), (0.0015, 0.0008), (xf0 - 0.05, 0.0008)])
    # nadproże (część górna przesunięta o D w dół)
    yH = H - D
    zak2 = {w["idx"]: (yH, yH + 0.34) for w in Ws}
    zak2[Ws[0]["idx"]] = (yH, yH + 0.34)
    sc2 = det.stos_v(sz, 0.0, yH, yH + 0.34, zakres=zak2)
    hb = float(bl.get("h", 0.24)) if bl else 0.24
    bb = float(bl.get("b", 0.18)) if bl else 0.18
    det.rect(xs1 - bb, yH, xs1, yH + hb, "ZB_C25" if "ZB_C25" in m.materialy else Ws[ks]["mat"], konstr=True)
    det.rect(0.0, yH - 0.012, xf0 - 0.004, yH, Ws[0]["mat"])                      # tynk na nadprożu
    det.rect(xf0, yH - g, xs1, yH, "PIANKA")
    det.rect(xf0, yH - g - hf, xf1, yH - g, "RAMA_ALU")
    det.rect(xg - 0.024, yH - 0.29, xg + 0.024, yH - g - hf + 0.02, "SZYBA3")
    iz = Ws[kx]["mat"]
    det.rect(xs1, yH - g, x_out, yH, iz)                                             # EPS nad ramą (pas 15 mm)
    det.rect(xf1 - 0.03, yH - g - 0.045, x_out, yH - g, iz)                          # izolacja nadproża z zakładem
    det.rect(xf1 - 0.03, yH - g - 0.051, x_out, yH - g - 0.045, Ws[-1]["mat"])        # wyprawa podsufitki ościeża
    det.obrobka([(xf1 - 0.03, yH - g - 0.051), (x_out + 0.004, yH - g - 0.051), (x_out + 0.004, yH - g - 0.03)],
                kapinos=False)
    det.linia("T_in", [(xf0 - 0.0015, yH - g - 0.03), (xf0 - 0.0015, yH - 0.0125), (xf0 - 0.05, yH - 0.0125)])
    det.linia("T_out", [(xf1 + 0.0015, yH - g - 0.045), (xf1 + 0.0015, yH - g + 0.0015), (xs1 + 0.02, yH - g + 0.0015)])
    det.linia("S", [(0.0015, yH + 0.34), (0.0015, yH - 0.0135), (xf0 - 0.05, yH - 0.0135)])
    det.polaczenie("S", [(xf0, g + 0.03), (xf0, yH - g - 0.03)])
    det.polaczenie("H", [(xf1, g + 0.04), (xf1, yH - g - 0.045)])
    # osłona (kaseta nadstawna przed licem ETICS — bez kasety w ociepleniu)
    if getattr(o, "oslona", None) and o.oslona not in ("brak", None):
        det.kontur([(x_out + 0.02, yH - 0.20), (x_out + 0.16, yH - 0.20), (x_out + 0.16, yH - 0.05),
                    (x_out + 0.02, yH - 0.05)])
        det.opis([(x_out + 0.09, yH - 0.125)], [f"osłona ({o.oslona.replace('_', ' ')}) — kaseta nadstawna PRZED "
                                                 "licem ETICS na konsolach z przekładką (bez kasety w ociepleniu)"])
    for p1, p2 in (((xf0 - 0.02, y1), (xf1 + 0.02, y1)), ((xf0 - 0.02, yH - 0.29), (xf1 + 0.02, yH - 0.29)),
                   ((0.0, y0), (x_out, y0)), ((0.0, yH + 0.34), (x_out, yH + 0.34))):
        det.przerwa(p1, p2)
    # opisy
    det.opis([(xg, y1 - 0.03)], [opis_stolarki(m, o),
                                 f"rama {mm(d_f)} mm: {mm(ws)} mm w murze, {mm(d_f - ws)} mm w ociepleniu (ciepły montaż)"])
    det.opis([(x_out + 0.02, 0.027)], ["parapet zewn. — blacha powlekana / Al 1,0 mm, spadek ≥ 5 %, okapnik 40 mm "
                                       "przed licem, zaślepki boczne na taśmie"])
    det.opis([(x_out - 0.05, 0.005)], ["profil nośny parapetu z XPS (w strefie ocieplenia) + taśma pod parapetem "
                                       "wywinięta na lico ocieplenia"])
    det.opis([(xf1 + 0.0035, g + 0.02)], ["taśma paroprzepuszczalna / rozprężna (zewn.) na obwodzie ramy"])
    det.opis([(xs1 - 0.02, g / 2)], [f"szczelina montażowa {mm(g)} mm — pianka PUR niskoprężna"])
    det.opis([(xf0 - 0.0015, g + 0.015)], ["taśma paroszczelna (wewn.) na obwodzie ramy — połączona z tynkiem"])
    det.opis([(-0.015, 0.0125)], ["parapet wewn. 20 mm na kleju, nawis 30 mm"])
    det.opis_stosu(sc, "y", -0.18, odwroc=True, tytul=f"{sz} — ściana zewnętrzna")
    det.opis([(xs1 - bb / 2, yH + hb / 2)], [f"nadproże ŻB {bl['id'] if bl else ''} {int(bb * 1000)}×{int(hb * 1000)} "
                                             "(wg PT-K)"])
    det.opis([(xf1 + 0.05, yH - g - 0.022)], [f"izolacja nadproża {skrot_nazwy(det.mat_info(iz)[0], 22)} 45 mm "
                                              "z zakładem 30 mm na ramę, profil narożny z okapnikiem"])
    det.opis([(xf0 - 0.0015, yH - g - 0.015)], ["taśma paroszczelna (wewn.) — tynk nadproża do taśmy"])
    # wymiary
    det.wymiar([(0.0, y0), (xs1 - (xs1 - Ws[0]["d"]), y0), (xf0, y0), (xs1, y0), (xf1, y0), (x_out - Ws[-1]["d"], y0),
                (x_out, y0)], y0 - 0.035, "h")
    det.wymiar([(0.0, y0), (x_out, y0)], y0 - 0.065, "h")
    det.uwagi.append("okno w warstwie ocieplenia zgodnie z symulacją WZ-11/11N/11P (ψ_oi ≈ 0,01 W/(m·K)); montaż "
                     "warstwowy: szczelniej od wewnątrz niż od zewnątrz (taśma paroszczelna / paroprzepuszczalna)")
    return det


# ================================================================================================ pomocnicze — płyta
def plyta_fund(det: Detal, pd: str, xs1: float, xL: float, xR: float, yB: float, tz: float,
               x_podl: float = 0.0, x_sbs: float | None = None) -> dict:
    """Grunt, płyta fundamentowa z żebrem pod ścianą (lico = xs1), izolacje pod płytą i na czole (do y_cok=tz+0,30
    — wywołujący może nadpisać), warstwy podłogi `pd` od posadzki y = 0 do x_podl. Zwraca wymiary pomocnicze."""
    m = det.model
    f = fundament_pod(m)
    W = det.warstwy(pd)
    ki = next(i for i, w in enumerate(W) if w["konstr"])
    y_pl = -sum(w["d"] for w in W[:ki])
    t_pl = W[ki]["d"]
    y_spod = y_pl - t_pl
    zb = f["zebro"]
    b_z, h_z = float(zb.get("b", 0.6)), float(zb.get("h", 0.3))
    xps = next((w for w in W[ki + 1:] if w["d"] >= 0.05), None)
    d_x = xps["d"] if xps else 0.20
    m_x = xps["mat"] if xps else "XPS300"
    pod = [w for w in W[ki + 1:] if w["d"] >= 0.05 and w is not xps]
    d_p = pod[0]["d"] if pod else 0.0
    y_zb = y_spod - h_z
    det.rect(xL - 0.5, yB - 0.1, xR + 0.1, tz, "GRUNT")
    zak = {w["idx"]: (xL - 0.5, x_podl) for w in W[:ki]}
    for w in W[:ki]:
        if w["d"] < 0.006:
            zak[w["idx"]] = (xL - 0.5, x_sbs if x_sbs is not None else xs1)
    zak[W[ki]["idx"]] = (xL - 0.5, xs1)
    for w in W[ki + 1:]:
        zak[w["idx"]] = (xL - 0.5, xs1 - b_z)
    st = det.stos_h(pd, xL - 0.5, x_podl, 0.0, zakres=zak)
    det.rect(xs1 - b_z, y_zb, xs1, y_spod, W[ki]["mat"], konstr=True)
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 - b_z, y_spod - d_x, m_x)
    det.rect(xs1 - b_z - d_x, y_zb - d_x, xs1 + d_x, y_zb, m_x)
    if pod:
        det.rect(xs1 - b_z - d_x, y_zb - d_x - d_p, xs1 + d_x, y_zb - d_x, pod[0]["mat"])
    det.cienka([(xs1 - b_z - d_x, y_zb - d_x), (xs1 + d_x, y_zb - d_x)], "FOLIA_PE", "G")
    y_m = next((0.5 * (a + b) for a, b, w in st if w["d"] < 0.006 and w["funkcja"] in
                ("przeciwwilgociowa", "hydroizolacja")), None)
    return dict(W=W, ki=ki, y_pl=y_pl, t_pl=t_pl, y_spod=y_spod, b_z=b_z, h_z=h_z, d_x=d_x, m_x=m_x, pod=pod,
                d_p=d_p, y_zb=y_zb, st=st, y_m=y_m, obwodowa=f["obwodowa"])


def opis_pod_plyta(det: Detal, P: dict, xs1: float):
    det.opis([(xs1 - P["b_z"] / 2 + 0.05, P["y_zb"] - P["d_x"] / 2),
              (xs1 - P["b_z"] / 2 + 0.05, P["y_zb"] - P["d_x"] - P["d_p"] / 2)],
             [f"pod płytą i żebrem: {tekst(det, P['m_x'], P['d_x'])}, folia PE 0,2 mm",
              tekst(det, P["pod"][0]["mat"], P["d_p"]) if P["pod"] else "podsypka"])


# ================================================================================================ D — próg HS
@rodzaj("prog_hs", "WZ-11T")
def detal_prog_hs(m, opts: dict) -> Detal:
    """Próg drzwi HS bezprogowy na płycie parteru: profil progowy termoizolacyjny na podwalinie XPS/PUR-GF,
    membrana SBS płyty wywinięta pod profil + taśma EPDM, odwodnienie liniowe przed progiem, taras z deski."""
    det = Detal(m, "D-03", "Próg drzwi HS bezprogowy z odwodnieniem liniowym", ("WZ-11T",), 10)
    sz = przegroda_typu(m, "WZ-11T", "sciana_zewn", "SZ1")
    pd = przegroda_typu(m, "WZ-11T", "podloga_na_gruncie", "POD-0")
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    d_f, ws = osadzenie(m, sz)
    xf0, xf1 = xs1 - ws, xs1 - ws + d_f
    tar = next((t for t in m.raw.get("tarasy") or [] if "HS" in str(t.get("nawierzchnia", "")) + str(t.get("uwagi", ""))),
               (m.raw.get("tarasy") or [{}])[0])
    y_tar = float(tar.get("rzedna", -0.02))
    tz = teren(m)
    xL, xR, yT, yB = -0.30, 1.05, 0.40, -1.00
    det.okno = (xL, yB, xR, yT)
    P = plyta_fund(det, pd, xs1, xL, xR, yB, tz, x_podl=xf0, x_sbs=xs1)
    y_pl = P["y_pl"]
    xp1 = xf1 + 0.03
    det.rect(xs1, P["y_zb"], xs1 + P["d_x"], y_pl, P["m_x"])                          # XPS na czole płyty
    det.rect(xp1, y_pl, xs1 + P["d_x"], -0.06, P["m_x"])                              # XPS pod krawędzią tarasu
    det.rect(xf0, y_pl, xp1, 0.0, "PODWALINA")
    det.rect(xf0, 0.0, xf1, 0.10, "RAMA_ALU")
    xg = (xf0 + xf1) / 2
    det.rect(xg - 0.024, 0.08, xg + 0.024, yT, "SZYBA3")
    # odwodnienie liniowe i taras
    xk0, xk1 = xs1 + P["d_x"] + 0.01, xs1 + P["d_x"] + 0.13
    det.rect(xs1 + P["d_x"], -0.30, xR + 0.1, -0.10, "KRUSZYWO")
    det.poly([(xk0, y_tar), (xk1, y_tar), (xk1, -0.14), (xk0, -0.14)], "KORYTKO")
    det.otwor(xk0 + 0.015, -0.12, xk1 - 0.015, y_tar - 0.005)
    det.rect(xk1 + 0.01, y_tar - 0.025, xR + 0.1, y_tar, "DESKA_KOMP")
    for xl in (xk1 + 0.10, xk1 + 0.50):
        det.rect(xl, y_tar - 0.065, xl + 0.06, y_tar - 0.025, "LEGAR")
        det.kontur([(xl + 0.01, y_tar - 0.065), (xl + 0.01, -0.10), (xl + 0.05, -0.10), (xl + 0.05, y_tar - 0.065)],
                   zamkniety=False, pen=0.25)
    det.cienka([(xs1 + P["d_x"], -0.30), (xR + 0.1, -0.30)], "GEOWL", "G")
    # 4 linie
    y_m = P["y_m"] or (y_pl + 0.0025)
    det.linia("H", [(xs1 + 0.003, P["y_zb"]), (xs1 + 0.003, y_m), (xp1 + 0.002, y_m), (xp1 + 0.002, 0.0)],
              "membrana SBS płyty wywinięta na podwalinę pod profil progowy (≥ 15 cm nad płytą)")
    det.linia("T_out", [(xp1 + 0.003, -0.02), (xp1 + 0.003, 0.003), (xf1 + 0.002, 0.003), (xf1 + 0.002, 0.04)])
    det.linia("T_in", [(xf0 - 0.0015, 0.04), (xf0 - 0.0015, y_m - 0.003)])
    det.linia("S", [(xL, y_pl - 0.004), (xf0 - 0.0015, y_pl - 0.004)])
    det.linia("P", [(xL, y_m + 0.004), (xf0 - 0.0015, y_m + 0.004)])
    det.polaczenie("H", [(xf1, 0.003), (xf1, yT)])
    for p1, p2 in (((xf0 - 0.02, yT), (xf1 + 0.02, yT)), ((xL, yB), (xR, yB)), ((xL, 0.0), (xL, yB)),
                   ((xR, y_tar), (xR, yB))):
        det.przerwa(p1, p2)
    # opisy
    det.opis([(xg, 0.25)], [opis_stolarki(m, next((o for o in m.otwory() if o.typ == "drzwi_przesuwne_HS"), None)),
                            "próg termiczny ≤ 20 mm, rama na podwalinie (ciepły montaż)"])
    det.opis([(xf1 + 0.002, 0.02)], ["taśma EPDM / paroprzepuszczalna: podwalina–rama, zakład ≥ 50 mm na membranę"])
    det.opis([(xp1 - 0.03, (y_pl + 0.0) / 2)], ["podwalina progowa XPS 300 / PUR-GF λ ≤ 0,05 (nośna) — wys. "
                                                f"{mm(-y_pl)} mm, na płycie"])
    det.opis([(xs1 + 0.1, (y_pl - 0.06) / 2 - 0.04)], [f"{tekst(det, P['m_x'], P['d_x'])} — czoło płyty i strefa "
                                                         "pod krawędzią tarasu"])
    det.opis([((xk0 + xk1) / 2, -0.10)], ["odwodnienie liniowe przed progiem (OL-2) z rusztem, na całą szerokość "
                                          "drzwi, spadek dna 0,5 % → KD-W / opaska"])
    det.opis([(xk1 + 0.3, y_tar - 0.012)], ["taras T1: deska kompozytowa 25 mm na legarach i wspornikach "
                                            "regulowanych, szczeliny 5 mm; spadek podłoża 2 % od budynku"])
    det.opis([(xk1 + 0.62, -0.20)], ["podbudowa z kruszywa 0/31,5 na geowłókninie (drenująca)"])
    det.opis_stosu(P["st"][:P["ki"] + 1], "x", -0.18, odwroc=True, wyjscie=(-0.18, yB - 0.03),
                   tytul=f"{pd} — podłoga na gruncie")
    opis_pod_plyta(det, P, xs1)
    det.rzedna((xL + 0.06, 0.0), 0.0, "zero", "right")
    det.rzedna((xR - 0.05, y_tar), y_tar, "wyk", "left")
    det.spadek((xk1 + 0.12, -0.085), (xk1 + 0.40, -0.091), 2.0)
    det.uwagi.append("próg bezbarierowy: wywinięcie hydroizolacji 15 cm ponad płytę (pod profil), przed drzwiami "
                     "odwodnienie liniowe na całą szerokość — DIN 18531-5 / wytyczne DAFA (redukcja wysokości progu "
                     "przy zapewnionym odpływie); spadek podłoża tarasu 2 % od budynku")
    return det


# ================================================================================================ pomocnicze — dach
def dach_wg(m, kod_przegrody: str) -> dict:
    return next((d for d in m.dachy() if d.get("przegroda") == kod_przegrody), (m.dachy() or [{}])[0])


def sciana_przy(m, xy, z: float) -> str | None:
    """Przegroda ściany zewnętrznej kondygnacji pod poziomem z (wierzch) najbliższej punktowi rzutu."""
    from shapely.geometry import LineString, Point
    best = None
    for s_ in m.sciany():
        if s_.typ != "sciana_zewn":
            continue
        k = m.kondygnacja(s_.kond)
        if not (k.rzedna - 0.3 <= z <= k.rzedna + k.wys_kondygnacji + 0.5):
            continue
        d = LineString([tuple(s_.p1), tuple(s_.p2)]).distance(Point(xy))
        if best is None or d < best[0]:
            best = (d, s_.przegroda_kod)
    return best[1] if best else None


def stos_dachu(det: Detal, kod: str, x0: float, x1: float, d_klin: float | None, zakres: dict | None = None):
    """Warstwy nad płytą stropodachu `kod` (od płyty w górę) z grubością klina d_klin; płyta y ∈ [−t, 0]."""
    W = det.warstwy(kod)
    ki = next(i for i, w in enumerate(W) if w["konstr"])
    grub = {w["idx"]: d_klin for w in W[:ki] if w.get("klin") and d_klin is not None}
    nad = [w for w in W[:ki]]
    y = 0.0
    out = []
    for w in reversed(nad):
        d = grub.get(w["idx"], w["d"])
        xa, xb = (zakres or {}).get(w["idx"], (x0, x1))
        if d < 0.006:
            det.cienka([(xa, y + d / 2), (xb, y + d / 2)], w["mat"])
        else:
            det.rect(xa, y, xb, y + d, w["mat"], os=((xa, y), (xb, y)))
        det._rejestr(kod, w, d)
        out.append((y + d, y, w))
        y += d
    return list(reversed(out)), y, W[ki]


def attyka_korona(m, kod_at: str) -> float:
    """Grubość izolacji korony attyki z nazwy przegrody („PIR 4 cm na koronie”), inaczej 0,05 m [ZAŁ]."""
    import re
    n = (m.przegroda(kod_at).nazwa or "") if m.przegroda(kod_at) else ""
    r = re.search(r"(\d+(?:[.,]\d+)?)\s*cm na koronie", n)
    return float(r.group(1).replace(",", ".")) / 100.0 if r else 0.05


def rysuj_attyke(det: Detal, sz: str, kod_d: str, kod_at: str, h_att: float, d_klin: float | None,
                 xL: float, yB: float, y_sr: float, hydro: bool = True) -> dict:
    """Ściana `sz` (lico wewn. x = 0) pod płytą dachu, płyta do lica konstrukcji, warstwy dachu, attyka AT
    (izolacja wewn. + konstrukcja w osi muru + izolacja ściany ciągła), korona z izolacją i obróbką."""
    m = det.model
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs0 = sum(w["d"] for w in Ws[:ks])
    xs1 = xs0 + Ws[ks]["d"]
    x_out = sum(w["d"] for w in Ws)
    Wd = det.warstwy(kod_d)
    kd = next(i for i, w in enumerate(Wd) if w["konstr"])
    t = Wd[kd]["d"]
    suf = sum(w["d"] for w in Wd[kd + 1:])
    Wa = det.warstwy(kod_at)
    ka = next(i for i, w in enumerate(Wa) if w["konstr"])
    iw = Wa[ka - 1] if ka > 0 else None
    d_iw = iw["d"] if iw else 0.10
    y_cap = y_sr + h_att                       # korona attyki (wys. nad pokryciem średnim)
    d_cap = attyka_korona(m, kod_at)
    y_p = y_cap - d_cap
    zak = {w["idx"]: (yB, -t) if i <= ks else (yB, y_cap) for i, w in enumerate(Ws)}
    sc = det.stos_v(sz, 0.0, yB, -t, zakres=zak)
    det.rect(xL, -t, xs1, 0.0, Wd[kd]["mat"], konstr=True)                         # płyta do lica konstrukcji
    det._rejestr(kod_d, Wd[kd], t)
    y = -t
    for w in Wd[kd + 1:]:
        det.rect(xL, y - w["d"], 0.0, y, w["mat"])
        det._rejestr(kod_d, w, w["d"])
        y -= w["d"]
    stos, y_top, _pl = stos_dachu(det, kod_d, xL, xs0 - d_iw, d_klin)
    det.rect(xs0, 0.0, xs1, y_p, Wa[ka]["mat"], konstr=True)                       # attyka ŻB w osi muru
    det._rejestr(kod_at, Wa[ka], xs1 - xs0)
    if iw:
        det.rect(xs0 - d_iw, 0.0, xs0, y_p, iw["mat"])
        det._rejestr(kod_at, iw, d_iw)
    det.rect(xs0 - d_iw, y_p, x_out, y_cap, iw["mat"] if iw else Ws[ks + 1]["mat"])  # izolacja korony
    x_iw = xs0 - d_iw
    memb = next((w for a, b, w in stos if w["funkcja"] == "hydroizolacja"), None)
    y_memb = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "hydroizolacja"), y_top)
    if hydro:
        det.linia("H", [(xL, y_memb), (x_iw - 0.002, y_memb), (x_iw - 0.002, y_cap + 0.002),
                        (x_out + 0.002, y_cap + 0.002), (x_out + 0.002, y_cap - 0.05)],
                  "hydroizolacja wywinięta na attykę i koronę")
    y_par = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "paroizolacja"), 0.002)
    det.linia("P", [(xL, y_par), (x_iw - 0.002, y_par), (x_iw - 0.002, y_top + 0.05)],
              "paroizolacja wywinięta na attykę ponad izolację dachu")
    det.linia("S", [(0.0015, yB), (0.0015, -t - suf - 0.002), (xL, -t - suf - 0.002)])
    rz = 0.05 * (x_out + 0.035 - (x_iw - 0.03))
    det.obrobka([(x_iw - 0.03, y_cap - 0.07), (x_iw - 0.03, y_cap + 0.006), (x_out + 0.035, y_cap + 0.006 + rz),
                 (x_out + 0.035, y_cap - 0.05)], strona=1)
    return dict(sc=sc, xs0=xs0, xs1=xs1, x_out=x_out, t=t, y_top=y_top, y_cap=y_cap, y_p=y_p, x_iw=x_iw,
                stos=stos, memb=memb, y_memb=y_memb, iw=iw)


def _klin_w(m, dach: dict, xy) -> tuple[float | None, dict]:
    """(grubość warstwy spadkowej w punkcie, poziomy) — z `mostki2d.zestawienie.poziomy_dachu`."""
    from ..obliczenia.mostki2d.zestawienie import poziomy_dachu
    pz = poziomy_dachu(m, dach, xy)
    p = m.przegroda(dach["przegroda"])
    raw = (p.raw or {}).get("warstwy") or []
    kl = next((r.get("klin") for r in raw if isinstance(r, dict) and r.get("klin")), None)
    if kl is None:
        return None, pz
    d = min(float(kl["d_max"]), float(kl["d_min"]) + float(dach.get("spadek") or 0.02) * pz["odl_wpustu"])
    return d, pz


# ================================================================================================ D — attyka z przelewem
@rodzaj("attyka_przelew", "WZ-01")
def detal_attyka_przelew(m, opts: dict) -> Detal:
    """Attyka stropodachu bryły A w przekroju przez przelew awaryjny: rzędna dna przelewu wg kryterium
    ≥ pokrycie przy wpuście + 0,03 m (i nie niżej niż pokrycie lokalne), wywinięcie ≥ 15 cm."""
    from ..obliczenia.mostki2d.zestawienie import poziomy_przelewow
    kod_d = przegroda_typu(m, "WZ-01", "stropodach", "SD1")
    dach = dach_wg(m, kod_d)
    pr = [p for p in poziomy_przelewow(m) if p["dach"] == dach["id"]]
    pa = min(pr, key=lambda p: p["pokrycie_lok"]) if pr else None
    xy = pa["xy"] if pa else dach["obrys"][0]
    z0 = float(dach["plyta"]["wierzch"])
    sz = sciana_przy(m, xy, z0) or przegroda_typu(m, "WZ-01", "sciana_zewn", "SZ1")
    att = dach.get("attyka") or {}
    kod_at = att.get("przegroda", "AT1")
    d_kl, pz = _klin_w(m, dach, xy)
    det = Detal(m, "D-04", f"Attyka dachu {dach['id']} — przelew awaryjny", ("WZ-01",), 10, z0=z0)
    y_sr = m.przegroda(kod_d).d_nad_konstr()
    xL, yB = -0.75, -0.62
    A = rysuj_attyke(det, sz, kod_d, kod_at, float(att.get("wys_nad_pokryciem", 0.25)), d_kl, xL, yB, y_sr, hydro=False)
    h = float(pa["h"]) if pa else 0.10
    y_d = (pa["zalecane"] if pa else z0 + A["y_top"] + 0.03) - z0
    x_iw, x_out, y_cap = A["x_iw"], A["x_out"], A["y_cap"]
    det.okno = (xL, yB, x_out + 0.30, y_cap + 0.10)
    det.otwor(x_iw - 0.01, y_d, x_out + 0.16, y_d + h)
    det.rect(x_iw - 0.07, y_d - 0.004, x_out + 0.12, y_d, "PRZELEW")
    det.rect(x_iw, y_d + h, x_out + 0.12, y_d + h + 0.003, "PRZELEW")
    det.obrobka([(x_out + 0.12, y_d - 0.004), (x_out + 0.12, y_d - 0.02)], kapinos=False)
    ym = A["y_memb"]
    det.linia("H", [(xL, ym), (x_iw - 0.07, ym), (x_iw - 0.07, y_d - 0.004), (x_iw - 0.01, y_d - 0.004)],
              "membrana wklejona w kołnierz przelewu")
    det.linia("H", [(x_iw - 0.002, y_d + h + 0.003), (x_iw - 0.002, y_cap + 0.002), (x_out + 0.002, y_cap + 0.002),
                    (x_out + 0.002, y_cap - 0.05)])
    det.polaczenie("H", [(x_iw - 0.01, y_d - 0.004), (x_iw - 0.002, y_d + h + 0.003)])
    for p1, p2 in (((0.0, yB), (x_out, yB)), ((xL, 0.3), (xL, -A["t"] - 0.02))):
        det.przerwa(p1, p2)
    det.opis_stosu(A["sc"], "y", -0.45, odwroc=True, tytul=f"{sz} — ściana zewnętrzna")
    det.opis_stosu(A["stos"], "x", -0.45, wyjscie=(-0.45, y_cap + 0.06),
                   tytul=f"{kod_d} — stropodach (izolacja spadkowa)")
    det.opis([(A["xs0"] + 0.09, A["y_p"] - 0.08)], [f"attyka {kod_at}: ŻB {mm(A['xs1'] - A['xs0'])} mm w osi muru, "
                                                   f"izolacja wewn. {mm(A['iw']['d']) if A['iw'] else '—'} mm i korony "
                                                   f"{mm(attyka_korona(m, kod_at))} mm"])
    det.opis([(x_out + 0.02, y_cap + 0.012)], ["obróbka korony — blacha powlekana 0,7 mm, spadek 5 % do dachu, "
                                              "okapniki 30–40 mm, na klamrach"])
    if pa:
        det.opis([(x_out + 0.08, y_d + h / 2)],
                 [f"przelew awaryjny {pa['opis'].split(' — ')[0].replace('przelew ', '')} "
                  f"{int(float(opts.get('szer', 0.20)) * 1000)}×{int(h * 1000)} mm — dno "
                  f"{fmt_z(pa['zalecane'])} (model {fmt_z(pa['dno'])})",
                  f"pokrycie przy wpuście {fmt_z(pa['pokrycie_wpust'])}, w miejscu przelewu {fmt_z(pa['pokrycie_lok'])}:"
                  f" dno ≥ pokrycie przy wpuście + 30 mm i ≥ pokrycie lokalne (W-142)"])
    det.rzedna((x_out + 0.22, y_d), y_d, "konstr", "left", tekst=fmt_z(z0 + y_d))
    det.rzedna((x_iw - 0.30, A["y_top"]), A["y_top"], "wyk", "left")
    det.rzedna((x_out + 0.22, y_cap), y_cap, "wyk", "left")
    det.rzedna((xL + 0.05, 0.0), 0.0, "konstr", "right")
    det.wymiar([(x_iw - 0.12, A["y_top"]), (x_iw - 0.12, y_cap)], x_iw - 0.16, "v",
               labels=[f"{mm(y_cap - A['y_top'])} ≥ 150"])
    det.spadek((x_iw - 0.12, A["y_top"] + 0.04), (x_iw - 0.40, A["y_top"] + 0.035), 2.0)
    det.uwagi.append("rzędne przelewów awaryjnych D1: dno = pokrycie przy wpuście + 0,03…0,05 m, nie niżej niż pokrycie "
                     "lokalne (tabela R-W2 w REKOMENDACJE mostków); wywinięcia ≥ 15 cm ponad warstwę wierzchnią (DAFA)")
    return det


def fmt_z(z: float) -> str:
    from ..draft import fmt
    return fmt.level(z)


# ================================================================================================ D — attyka z wpustem bocznym
@rodzaj("attyka_wpust", "WZ-02")
def detal_attyka_wpust(m, opts: dict) -> Detal:
    """Attyka dachu P1 w przekroju przez wpust attykowy (boczny) i rurę spustową zewnętrzną z lejem."""
    kod_d = przegroda_typu(m, "WZ-02", "stropodach", "SD2")
    dach = dach_wg(m, kod_d)
    wp = (dach.get("wpusty") or [{}])[0]
    xy = wp.get("xy", dach["obrys"][0]) if isinstance(wp, dict) else wp
    rs = next((r for r in dach.get("rury_spustowe") or [] if r.get("trasa") == "zewn"), {})
    z0 = float(dach["plyta"]["wierzch"])
    sz = sciana_przy(m, xy, z0) or przegroda_typu(m, "WZ-02", "sciana_zewn", "SZ1")
    att = dach.get("attyka") or {}
    kod_at = att.get("przegroda", "AT1")
    d_kl, pz = _klin_w(m, dach, xy)
    det = Detal(m, "D-05", f"Attyka dachu {dach['id']} — wpust boczny i rura spustowa", ("WZ-02",), 10, z0=z0)
    y_sr = m.przegroda(kod_d).d_nad_konstr()
    xL, yB = -0.70, -0.75
    A = rysuj_attyke(det, sz, kod_d, kod_at, float(att.get("wys_nad_pokryciem", 0.25)), d_kl, xL, yB, y_sr, hydro=False)
    x_iw, x_out, y_cap, ym = A["x_iw"], A["x_out"], A["y_cap"], A["y_memb"]
    dn = float(rs.get("dn", 100)) / 1000.0 if rs else 0.10
    y0w = ym - 0.004
    det.otwor(x_iw - 0.01, y0w, x_out + 0.02, y0w + dn + 0.01)                      # przejście wpustu przez attykę
    det.rect(x_iw - 0.12, y0w - 0.003, x_out + 0.02, y0w, "WPUST")
    det.rect(x_iw, y0w + dn + 0.007, x_out + 0.02, y0w + dn + 0.01, "WPUST")
    xr0, xr1 = x_out + 0.03, x_out + 0.03 + max(0.20, 1.6 * dn)                      # lej (rura zbiorcza)
    det.rect(xr0, y0w - 0.25, xr0 + 0.003, y0w + dn + 0.10, "RURA_MET")
    det.rect(xr1 - 0.003, y0w - 0.25, xr1, y0w + dn + 0.10, "RURA_MET")
    det.rect(xr0, y0w - 0.253, xr1, y0w - 0.25, "RURA_MET")
    xc = (xr0 + xr1) / 2
    det.rect(xc - dn / 2, yB, xc - dn / 2 + 0.002, y0w - 0.253, "RURA_MET")
    det.rect(xc + dn / 2 - 0.002, yB, xc + dn / 2, y0w - 0.253, "RURA_MET")
    det.kontur([(x_out, y0w - 0.35), (xc - dn / 2, y0w - 0.35)], zamkniety=False, pen=0.5)   # obejma dystansowa
    det.linia("H", [(xL, ym), (x_iw - 0.12, ym), (x_iw - 0.12, y0w - 0.003), (x_iw - 0.01, y0w - 0.003)],
              "membrana wklejona w kołnierz wpustu")
    det.linia("H", [(x_iw - 0.002, y0w + dn + 0.01), (x_iw - 0.002, y_cap + 0.002), (x_out + 0.002, y_cap + 0.002),
                    (x_out + 0.002, y_cap - 0.05)])
    det.polaczenie("H", [(x_iw - 0.01, y0w - 0.003), (x_iw - 0.002, y0w + dn + 0.01)])
    det.okno = (xL, yB, xr1 + 0.05, y_cap + 0.10)
    det.przerwa((0.0, yB), (x_out, yB))
    det.przerwa((xc - dn / 2 - 0.02, yB), (xc + dn / 2 + 0.02, yB))
    det.przerwa((xL, 0.3), (xL, -A["t"] - 0.02))
    det.opis_stosu(A["stos"], "x", -0.42, wyjscie=(-0.42, y_cap + 0.06), tytul=f"{kod_d} — stropodach")
    det.opis_stosu(A["sc"], "y", -0.55, odwroc=True, tytul=f"{sz} — ściana zewnętrzna")
    det.opis([(x_iw - 0.08, y0w - 0.0015)], [f"wpust attykowy (boczny) DN{int(dn * 1000)} z kołnierzem, podgrzewany "
                                             f"— {str(wp.get('opis', '')).split(' — ')[0] if isinstance(wp, dict) else ''}"])
    det.opis([(xr1 - 0.01, y0w + 0.03)], [f"lej spustowy + rura {rs.get('id', '')} DN{int(dn * 1000)} na obejmach "
                                          "dystansowych przed licem ETICS (bez wnęki w ociepleniu)"])
    det.opis([((x_out + xc - dn / 2) / 2, y0w - 0.35)], ["obejma z kotwą w murze przez ocieplenie — mostek punktowy "
                                                         "(χ ≈ 0,002 W/K, jak łącznik ETICS)"])
    det.opis([(A["xs0"] + 0.09, A["y_p"] - 0.06)], [f"attyka {kod_at} (ŻB w osi muru, izolacja z 3 stron)"])
    det.rzedna((x_iw - 0.35, A["y_top"]), A["y_top"], "wyk", "left")
    det.rzedna((xr1 + 0.02, y_cap), y_cap, "wyk", "left")
    det.wymiar([(x_iw - 0.10, A["y_top"]), (x_iw - 0.10, y_cap)], x_iw - 0.14, "v",
               labels=[f"{mm(y_cap - A['y_top'])} ≥ 150"])
    prz = (dach.get("przelewy_awaryjne") or [{}])[0]
    det.uwagi.append(f"dach {dach['id']}: przelew awaryjny {str(prz.get('opis', '')).split(' — ')[0]} w attyce (poza "
                     "przekrojem, rozwiązanie jak detal D-04); rura spustowa do kolektora KD → zbiornik retencyjny "
                     "(detal D-07)")
    return det


# ================================================================================================ D — wpust dachowy
@rodzaj("wpust", "WZ-15")
def detal_wpust(m, opts: dict) -> Detal:
    """Wpust dachowy wewnętrzny (podgrzewany) w stropodachu z izolacją spadkową: przejście przez paroizolację,
    izolację i hydroizolację (kołnierze), rura spustowa w izolowanym szachcie."""
    dach = next((d for d in m.dachy() if any(r.get("trasa") == "wewn_szacht" for r in d.get("rury_spustowe") or [])),
                m.dachy()[0])
    kod_d = dach["przegroda"]
    r = next(r for r in dach.get("rury_spustowe") or [] if r.get("trasa") == "wewn_szacht")
    wp = (dach.get("wpusty") or [{}])[int(r.get("od_wpustu", 0))]
    xy = wp.get("xy") if isinstance(wp, dict) else wp
    z0 = float(dach["plyta"]["wierzch"])
    d_kl, pz = _klin_w(m, dach, xy)
    det = Detal(m, "D-06", f"Wpust dachowy {str(wp.get('opis', 'WP')).split(' — ')[0]} i rura {r.get('id')}",
                ("WZ-15",), 10, z0=z0)
    dn = float(r.get("dn", 100)) / 1000.0
    ro = dn / 2 + 0.005
    Wd = det.warstwy(kod_d)
    kd = next(i for i, w in enumerate(Wd) if w["konstr"])
    t = Wd[kd]["d"]
    xL, xR, yB = -0.55, 0.55, -0.80
    det.okno = (xL, yB, xR, 0.45)
    det.rect(xL, -t, xR, 0.0, Wd[kd]["mat"], konstr=True)
    det._rejestr(kod_d, Wd[kd], t)
    y = -t
    for w in Wd[kd + 1:]:
        det.rect(xL, y - w["d"], -0.36, y, w["mat"])
        det.rect(0.36, y - w["d"], xR, y, w["mat"])
        det._rejestr(kod_d, w, w["d"])
        y -= w["d"]
    stos, y_top, _pl = stos_dachu(det, kod_d, xL, xR, d_kl)
    ym = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "hydroizolacja"), y_top)
    yp = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "paroizolacja"), 0.002)
    det.otwor(-(ro - 0.005), yB, ro - 0.005, y_top + 0.10)                           # przelot rury
    det.rect(-ro - 0.025, -t, -ro, 0.0, "ZAPRAWA")
    det.rect(ro, -t, ro + 0.025, 0.0, "ZAPRAWA")
    for sgn in (-1, 1):                                                              # korpus wpustu / rura
        det.rect(sgn * ro, yB, sgn * (ro - 0.005), ym + 0.004, "WPUST")
        det.rect(sgn * ro, yB, sgn * (ro + 0.020), -t - 0.01, "OTULINA")
    det.rect(-0.20, yp - 0.004, 0.20, yp, "WPUST")                                   # kołnierz paroizolacji
    det.rect(-0.25, ym - 0.004, -ro, ym, "WPUST")                                    # kołnierz hydroizolacji
    det.rect(ro, ym - 0.004, 0.25, ym, "WPUST")
    det.kontur([(-0.10, ym), (-0.08, ym + 0.12), (0.08, ym + 0.12), (0.10, ym)], zamkniety=False, pen=0.35)
    for sgn in (-1, 1):
        det.kontur([(sgn * (ro + 0.012) + 0.006 * np.cos(a), ym - 0.03 + 0.006 * np.sin(a))
                    for a in np.linspace(0, 2 * np.pi, 13)], pen=0.35)
    gk = "GK10" if "GK10" in m.przegrody else None
    if gk:
        det.stos_v(gk, -0.36, yB, -t - 0.012, kier=-1)
        det.stos_v(gk, 0.36, yB, -t - 0.012, kier=+1)
    det.linia("H", [(xL, ym), (-0.25, ym), (-ro, ym)])
    det.linia("H", [(ro, ym), (xR, ym)])
    det.polaczenie("H", [(-ro, ym), (ro, ym)])
    det.linia("P", [(xL, yp), (-0.20, yp), (-ro, yp)])
    det.linia("P", [(ro, yp), (xR, yp)])
    det.polaczenie("P", [(-ro, yp), (ro, yp)])
    det.linia("S", [(xL, -t - 0.002), (-0.36, -t - 0.002)])
    det.linia("S", [(0.36, -t - 0.002), (xR, -t - 0.002)])
    det.polaczenie("S", [(-0.36, -t - 0.002), (0.36, -t - 0.002)])
    for p1, p2 in (((xL, yB), (xR, yB)), ((xL, y_top), (xL, -t)), ((xR, y_top), (xR, -t))):
        det.przerwa(p1, p2)
    det.opis_stosu(stos, "x", 0.45, wyjscie=(0.45, y_top + 0.12), tytul=f"{kod_d} — stropodach")
    det.opis([(0.0, ym + 0.12)], ["kosz ochronny (liściołap)"])
    det.opis([(0.18, ym - 0.002)], [f"wpust dachowy DN{int(dn * 1000)} z grzałką, kołnierz dociskowy membrany "
                                    "(nadstawka w warstwie izolacji)"])
    det.opis([(ro + 0.012, ym - 0.03)], ["kabel grzejny wpustu (sterowanie termostatem)"])
    det.opis([(0.15, yp - 0.002)], ["kołnierz paroizolacji — wklejony w paroizolację z Al (szczelność powietrzna)"])
    det.opis([(ro + 0.012, -t / 2)], ["przejście przez płytę: tuleja / otwór wiercony, wypełnienie zaprawą "
                                      "(ognioodporne wg PT-K)"])
    det.opis([(ro + 0.01, -t - 0.20)], [f"rura spustowa {r.get('id')} DN{int(dn * 1000)} w otulinie 20 mm "
                                        f"(przeciwroszeniowa, akustyczna) — {r.get('opis', '')[:60]}"])
    if gk:
        det.opis([(0.40, -t - 0.35)], [f"obudowa szachtu {gk} (EI 30)"])
    det.rzedna((-0.30, y_top), y_top, "wyk", "left")
    det.rzedna((xL + 0.08, 0.0), 0.0, "konstr", "right")
    det.spadek((-0.28, y_top + 0.10), (-0.14, y_top + 0.10), 2.0)
    det.spadek((0.28, y_top + 0.10), (0.14, y_top + 0.10), 2.0)
    det.opis([(-0.30, y_top + 0.002)], [f"pokrycie przy wpuście {fmt_z(z0 + y_top)} (izolacja spadkowa d_min)"])
    det.uwagi.append("wpusty i przejścia instalacji przez przegrody zewnętrzne — mostki punktowe χ (WZ-15, wartości "
                     "typowe); kołnierze paroizolacji i hydroizolacji wpustu — ciągłość 4 linii")
    return det


# ================================================================================================ D — wspornik bryły A
@rodzaj("wspornik_A", "WZ-07", "WZ-07a", "WZ-16", "WZ-16a", "WZ-05")
def detal_wspornik_A(m, opts: dict) -> Detal:
    """Krawędź wspornika bryły A: ściana lekka na belce krawędziowej, strop nad powietrzem z ociepleniem spodu
    i podsufitką (jedna płaszczyzna — audyt A2 I-5), płyta PL-2 przez łącznik termoizolacyjny, lamele."""
    from ..obliczenia.mostki2d.katalog_dod import krawedzie_stropu_zewn
    kody = wpis(m, "WZ-07").get("przegrody") or []
    st = next((s for s in m.stropy() if s.get("sufit") in kody and s.get("sufit") in m.przegrody), None) or \
        next(s for s in m.stropy() if s.get("sufit") in m.przegrody)
    kr = [k for k in krawedzie_stropu_zewn(m, st) if k["typ"] == "a"]
    k = max(kr, key=lambda k_: (k_["belka_rodzaj"] == "krawedziowa", k_["L"]))
    z0, t = float(st["wierzch"]), float(st["grubosc"])
    det = Detal(m, "D-08", f"Wspornik bryły A — krawędź {st['id']}"
                           + (f" z płytą {k['wsp']['id']}" if k["wsp"] else ""), ("WZ-07a", "WZ-16a"), 10, z0=z0)
    sz, pod, suf = k["sciana"], st.get("podloga"), st.get("sufit")
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs0 = sum(w["d"] for w in Ws[:ks])
    xs1 = xs0 + Ws[ks]["d"]
    x_out = sum(w["d"] for w in Ws)
    bb, hb = (k["belka"][0], k["belka"][1]) if k["belka"] else (Ws[ks]["d"], 0.0)
    Wp = det.warstwy(pod)
    kp = next((i for i, w in enumerate(Wp) if w["konstr"]), len(Wp))
    y_f = sum(w["d"] for w in Wp[:kp])                                  # warstwy podłogi nad płytą
    xL, xR, yT, yB = -0.45, 1.00, 0.85, -0.56
    det.okno = (xL, yB, xR, yT)
    ws_ = k["wsp"]
    t_w = float(ws_["grubosc"]) if ws_ else t
    # ściana lekka: warstwy wewn. od podłogi, szkielet od belki, zewn. od wierzchu płyty wspornikowej
    zak = {}
    for i, w in enumerate(Ws):
        zak[w["idx"]] = (y_f, yT) if i < ks else ((hb, yT) if i == ks else (0.0, yT))
    sc = det.stos_v(sz, 0.0, 0.0, yT, zakres=zak)
    det.stos_h(pod, xL, xs0, y_f, do=kp)
    det.rect(xL, -t, xs1, 0.0, st.get("mat", "ZB_C25"), konstr=True)
    det.rect(xs1 - bb, 0.0, xs1, hb, k["belka"][2] if k["belka"] else st.get("mat"), konstr=True, grupa="belka")
    lac_d = 0.08
    if ws_:
        det.rect(xs1, -t_w, xs1 + lac_d, 0.0, "LACZNIK")
        det.poly([(xs1 + lac_d, 0.0), (xR + 0.05, -0.02 * (xR + 0.05 - xs1 - lac_d)), (xR + 0.05, -t_w),
                  (xs1 + lac_d, -t_w)], ws_.get("mat", "ZB_C30"), konstr=True)
    # sufit nad powietrzem: wełna do lica ocieplenia ściany, pustka wentylowana, podsufitka ciągła pod płytą PL-2
    Wsf = det.warstwy(suf)
    w_iz = next(w for w in Wsf if w["konstr"] or w["mat"].startswith("WELNA"))
    y_w = -t - w_iz["d"]
    det.poly([(xL, -t), (xs1, -t), (xs1, -t_w), (x_out, -t_w), (x_out, y_w), (xL, y_w)], w_iz["mat"])
    det._rejestr(suf, w_iz, w_iz["d"])
    y = y_w
    for w in Wsf[Wsf.index(w_iz) + 1:]:
        if "PUSTKA" in w["mat"] or "pustka" in det.mat_info(w["mat"])[0].lower():
            for xb in (xL + 0.10, 0.35, 0.80):
                det.rect(xb, y - w["d"], xb + 0.05, y, "RUSZT")
        elif w["d"] < 0.006:
            det.cienka([(xL, y - w["d"] / 2), (xR + 0.05, y - w["d"] / 2)], w["mat"])
        else:
            det.rect(xL, y - w["d"], xR + 0.05, y, w["mat"])
        det._rejestr(suf, w, w["d"])
        y -= w["d"]
    y_ps = y
    # lamele (widok) i membrany
    lm = next((l_ for l_ in m.raw.get("lamele") or [] if float(l_.get("odsuniecie", 0)) > 0), {})
    xl0 = x_out + float(lm.get("odsuniecie", 0.15))
    det.kontur([(xl0, 0.0), (xl0 + float(lm.get("h", 0.08)), 0.0), (xl0 + float(lm.get("h", 0.08)), yT),
                (xl0, yT)], pen=0.35)
    det.kontur([(x_out, 0.12), (xl0, 0.12)], zamkniety=False, pen=0.5)
    det.linia("H", [(xR + 0.05, 0.002 - 0.02 * (xR + 0.05 - xs1 - lac_d)), (xs1 + lac_d, 0.002), (x_out + 0.002, 0.002),
                    (x_out + 0.002, 0.18)], "membrana płyty wywinięta na ścianę ≥ 15 cm pod membranę fasadową")
    det.linia("S", [(xs0 - 0.0075, yT), (xs0 - 0.0075, 0.004), (xL, 0.004)])
    det.linia("P", [(xs0 - 0.012, yT), (xs0 - 0.012, y_f)])
    det.linia("T_in", [(xs0 - 0.012, y_f + 0.06), (xs0 - 0.012, y_f + 0.002), (xs0 + 0.002, y_f + 0.002)])
    for p1, p2 in (((0.0, yT), (x_out, yT)), ((xL, yB + 0.08), (xL, y_f)), ((xR, 0.02), (xR, y_ps))):
        det.przerwa(p1, p2)
    # opisy
    det.opis_stosu(sc, "y", 0.62, odwroc=True, tytul=f"{sz} — ściana lekka (szkielet)")
    det.opis([(xl0 + 0.04, 0.45)], [f"{nazwa_lamel(det, lm)} {int(float(lm.get('b', 0.04)) * 1000)}×"
                                    f"{int(float(lm.get('h', 0.08)) * 1000)} co "
                                    f"{int(float(lm.get('rozstaw', 0.12)) * 1000)} mm (widok) na ruszcie — detal D-12"])
    if k["belka"]:
        det.opis([(xs1 - bb / 2, hb / 2)], [f"belka krawędziowa {k['belka'][3]} ŻB {int(bb * 1000)}×"
                                            f"{int(round((hb + t) * 1000))} (odwrócona) — wg PT-K"])
    if ws_:
        det.opis([(xs1 + lac_d / 2, -t_w / 2)], [f"łącznik termoizolacyjny (ETA) w strefie ocieplenia — przykł. "
                                                 f"{int(lac_d * 1000)} mm; zalecany 120 mm (REKOMENDACJE A)"])
        det.opis([(0.85, -0.12)], [f"płyta {ws_['id']} ŻB C30/37 {int(t_w * 1000)} mm, wierzch = wierzch stropu "
                                   "(A2), spadek 2 % do czoła, membrana TPO; rynna ukryta za blendą"])
    det.opis_stosu(det_stos_pod(det, suf, t, y_w), "x", -0.30, odwroc=False, wyjscie=(-0.30, yB - 0.02),
                   tytul=f"{suf} — sufit nad powietrzem zewnętrznym")
    det.opis([(0.65, (y_ps - t_w) / 2 - 0.05)], ["podsufitka jedna płaszczyzna pod wspornikiem A i pasem PL-2, "
                                                  f"spód {fmt_z(det.z0 + y_ps)}; czoło PL-2 obudowane blendą do "
                                                  "spodu podsufitki (audyt A2 I-5)"])
    det.opis_stosu([(a, b, w) for a, b, w in det_stos_pod(det, pod, y_f, 0.0)][:kp + 1], "x", -0.20,
                   wyjscie=(-0.20, yT + 0.03), tytul=f"{pod} — podłoga")
    det.wymiar([(a, yT) for a, _b, _w in sc] + [(sc[-1][1], yT)], yT + 0.05, "h")
    det.wymiar([(xL + 0.03, -t), (xL + 0.03, y_w), (xL + 0.03, y_ps)], xL - 0.03, "v")
    det.rzedna((xL + 0.06, y_f), y_f, "wyk", "right")
    det.rzedna((xL + 0.06, 0.0), 0.0, "konstr", "right")
    det.uwagi.append("wspornik bryły A: ocieplenie spodu stropu ST2Z ciągłe od ETICS ściany P1 do lica ocieplenia ściany "
                     "lekkiej, podsufitka wentylowana (szczelina 40 mm, kratki na obwodzie)")
    return det


def det_stos_pod(det: Detal, kod: str, y_top: float, y_bot: float) -> list:
    """Stos (y_góra, y_dół, warstwa) przegrody poziomej `kod` od y_top w dół — tylko do opisu (bez rysowania)."""
    out, y = [], y_top
    for w in det.warstwy(kod):
        out.append((y, y - w["d"], w))
        y -= w["d"]
    return out


# ================================================================================================ D — okap PL-E nad HS
@rodzaj("okap", "WZ-04")
def detal_okap(m, opts: dict) -> Detal:
    """Płyta wysunięta (okap) nad przeszkleniem HS: łącznik termoizolacyjny, spadek 2 % od budynku, rynna ukryta
    za blendą czołową z kapinosem, podsufitka z kasetą osłony (poza ociepleniem), nadproże HS."""
    from ..obliczenia.mostki2d.katalog_dod import plyta_pod_wspornikiem, wspornik_z_nazwy
    e = wpis(m, "WZ-04")
    wsp = (wspornik_z_nazwy(m, e.get("nazwa", "PL-E")) or [m.wsporniki()[0]])[0]
    st, _r = plyta_pod_wspornikiem(m, wsp)
    z0 = float(st["wierzch"]) if st else float(wsp["wierzch"])
    t = float(st["grubosc"]) if st else 0.22
    t_w = float(wsp["grubosc"])
    from shapely.geometry import Polygon as _P
    P = _P(wsp["obrys"])
    xs_ = [q[0] for q in wsp["obrys"]]
    wys = round(max(0.5, min(2.0, (max(xs_) - min(xs_)) if max(xs_) - min(xs_) < 3 else 1.5)), 2)
    wys = 1.5 if any(abs(q[0] - min(xs_)) < 1e-6 for q in wsp["obrys"]) else wys
    sz = przegroda_typu(m, "WZ-04", "sciana_zewn", "SZ1")
    pod = st.get("podloga") if st else "POD-1"
    det = Detal(m, "D-09", f"Okap {wsp['id']} {wys:.2f} m nad przeszkleniem HS".replace(".", ","), ("WZ-04",), 10,
                z0=z0)
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    d_f, ws_ = osadzenie(m, sz)
    xf0, xf1 = xs1 - ws_, xs1 - ws_ + d_f
    Wp = det.warstwy(pod)
    kp = next(i for i, w in enumerate(Wp) if w["konstr"])
    y_f = sum(w["d"] for w in Wp[:kp])
    xL, yT, yB = -0.40, 0.75, -0.62
    lac = 0.08
    front = x_out + wys
    D = front - 0.34 - 0.92                                   # przesunięcie części czołowej (przerwa widoku)
    t_front = -0.02 * (front - xs1 - lac)
    # ściana P1 nad okapem: XPS cokołowy 30 cm w strefie rozbryzgu
    kx = next(i for i, w in enumerate(Ws) if i > ks and w["d"] >= 0.05)
    zak = {w["idx"]: ((y_f, yT) if i < ks else (0.0, yT) if i == ks else (0.30, yT)) for i, w in enumerate(Ws)}
    sc = det.stos_v(sz, 0.0, 0.0, yT, zakres=zak)
    det.rect(xs1, 0.0, x_out, 0.30, "XPS300" if "XPS300" in m.materialy else Ws[kx]["mat"])
    det.stos_h(pod, xL, 0.0, y_f, do=kp)
    det.rect(xL, -t, xs1, 0.0, st.get("mat", "ZB_C25") if st else "ZB_C25", konstr=True)
    det.rect(xL, -t - 0.01, xf0 - 0.004, -t, Ws[0]["mat"])                          # tynk sufitu P0
    det.rect(xs1, -t, xs1 + lac, 0.0, "LACZNIK")
    mw = wsp.get("mat", "ZB_C30")
    x_cut = 0.92
    det.poly([(xs1 + lac, 0.0), (x_cut, -0.02 * (x_cut - xs1 - lac)), (x_cut, -t_w), (x_out, -t_w), (x_out, -t),
              (xs1 + lac, -t)], mw, konstr=True)
    x0f = front - 0.34 - D
    det.poly([(x0f, t_front + 0.02 * 0.34), (front - D, t_front), (front - D, -t_w), (x0f, -t_w)], mw, konstr=True)
    # nadproże HS: rama, izolacja pod okapem, taśmy
    yh = -t - 0.015
    det.rect(xf0, yh - 0.11, xf1, yh, "RAMA_ALU")
    xg = (xf0 + xf1) / 2
    det.rect(xg - 0.024, yB, xg + 0.024, yh - 0.09, "SZYBA3")
    det.rect(xf0, yh, xs1, -t, "PIANKA")
    det.rect(xf1 - 0.03, -t_w - 0.05, x_out, -t, Ws[kx]["mat"])
    det.rect(xs1, yh, xf1 + 0.001, -t, Ws[kx]["mat"])
    det.obrobka([(xf1 - 0.03, -t_w - 0.052), (x_out + 0.004, -t_w - 0.052), (x_out + 0.004, -t_w - 0.03)],
                kapinos=False)
    det.linia("T_in", [(xf0 - 0.0015, yh - 0.03), (xf0 - 0.0015, -t - 0.012), (xf0 - 0.05, -t - 0.012)])
    det.linia("T_out", [(xf1 + 0.0015, yh - 0.05), (xf1 + 0.0015, yh + 0.0015), (xs1 + 0.02, yh + 0.0015)])
    # podsufitka z kasetą osłony, blenda, rynna ukryta
    y_s = -t_w - 0.07
    det.kontur([(x_out + 0.03, -t_w), (x_out + 0.03, y_s - 0.07), (x_out + 0.17, y_s - 0.07), (x_out + 0.17, -t_w)],
               zamkniety=False, pen=0.35)
    det.rect(x_out + 0.17, y_s - 0.012, x_cut, y_s, "CZOLO_WLOKNO")
    det.rect(x0f, y_s - 0.012, front - D, y_s, "CZOLO_WLOKNO")
    for xb in (x_out + 0.35, x_cut - 0.1, x0f + 0.1):
        det.rect(xb, y_s, xb + 0.05, -t_w, "RUSZT")
    xfr = front - D
    det.rect(xfr, y_s - 0.012, xfr + 0.012, t_front + 0.11, "CZOLO_WLOKNO")
    det.obrobka([(xfr - 0.13, t_front + 0.07), (xfr - 0.12, t_front + 0.003), (xfr - 0.015, t_front + 0.003),
                 (xfr - 0.015, t_front + 0.10), (xfr + 0.02, t_front + 0.10 + 0.002), (xfr + 0.02, t_front + 0.07)],
                strona=1)
    det.obrobka([(xfr, y_s - 0.012), (xfr + 0.02, y_s - 0.012)], strona=1)
    det.linia("H", [(xfr - 0.12, t_front + 0.004), (x0f, t_front + 0.02 * 0.34 + 0.002)])
    det.linia("H", [(x_cut, -0.02 * (x_cut - xs1 - lac) + 0.002), (xs1 + lac, 0.002), (x_out + 0.002, 0.002),
                    (x_out + 0.002, 0.17)], "membrana okapu wywinięta na ścianę ≥ 15 cm (pod XPS cokołowy)")
    det.polaczenie("H", [(x_cut, -0.02 * (x_cut - xs1 - lac) + 0.002), (x0f, t_front + 0.02 * 0.34 + 0.002)])
    det.linia("S", [(0.0015, yT), (0.0015, 0.003), (xL, 0.003)])
    det.linia("S", [(xL, -t - 0.013), (xf0 - 0.05, -t - 0.013)])
    det.polaczenie("S", [(0.0015, 0.003), (0.0015, -t - 0.013)])
    for p1, p2 in (((0.0, yT), (x_out, yT)), ((x_cut, 0.02), (x_cut, y_s - 0.02)), ((x0f, 0.02), (x0f, y_s - 0.02)),
                   ((xf0 - 0.02, yB), (xf1 + 0.02, yB)), ((xL, y_f), (xL, -t - 0.01))):
        det.przerwa(p1, p2)
    # opisy
    det.opis_stosu(sc, "y", 0.55, odwroc=True, tytul=f"{sz} — ściana P1")
    det.opis([(xs1 + 0.1, 0.15)], ["XPS 300 w strefie rozbryzgu 30 cm nad okapem, membrana pod XPS"])
    det.opis([(xs1 + lac / 2, -t / 2)], [f"łącznik termoizolacyjny (ETA) wys. = grubość stropu {mm(t)} mm, "
                                         "przykł. 80 mm; zalecany 120 mm (REKOMENDACJE A)"])
    det.opis([(0.70, -0.15)], [f"okap {wsp['id']} ŻB C30/37 {mm(t_w)} mm (poza licem), wierzch = wierzch stropu, "
                               "spadek 2 % od budynku, membrana TPO"])
    det.opis([(xfr - 0.07, t_front + 0.02)], ["rynna ukryta (korytko ze stali nierdz. / blachy powlekanej 0,7 mm) za "
                                              "blendą, spadek 0,5 % do rury spustowej → KD (REKOMENDACJE R-W1)"])
    det.opis([(xfr + 0.006, y_s + 0.05)], ["blenda czołowa — płyta włóknocementowa 12 mm, obróbka korony "
                                           "i okapnik (kapinos) na spodzie"])
    det.opis([(x_out + 0.10, y_s - 0.035)], ["kaseta screenu ZIP w podsufitce okapu (poza warstwą izolacji)"])
    det.opis([(x_out + 0.50, y_s - 0.006)], ["podsufitka włóknocementowa 12 mm na ruszcie, szczelina wentylowana"])
    det.opis([(xf1 + 0.01, -t_w - 0.025)], ["izolacja nadproża z zakładem 30 mm na ramę HS, profil z okapnikiem"])
    det.opis([(xg, yB + 0.08)], [opis_stolarki(m, next((o for o in m.otwory() if o.typ == "drzwi_przesuwne_HS"
                                                        and o.sciana is not None and o.sciana.przegroda_kod == sz),
                                                       None)), "taśmy: paroszczelna wewn. / paroprzepuszczalna zewn."])
    det.opis_stosu(det_stos_pod(det, pod, y_f, 0.0)[:kp + 1], "x", -0.22, wyjscie=(-0.22, yT + 0.03),
                   tytul=f"{pod} — podłoga P1")
    det.wymiar([(x0f, 0.0), (front - D, 0.0)], 0.08, "h", labels=[f"… {mm(wys)} od lica"])
    det.rzedna((xL + 0.05, y_f), y_f, "wyk", "right")
    det.rzedna((xL + 0.05, 0.0), 0.0, "konstr", "right")
    det.spadek((x_out + 0.10, 0.05), (x_out + 0.40, 0.044), 2.0)
    det.uwagi.append(f"okap {wsp['id']}: w strefie łącznika grubość = grubość stropu ({mm(t)} mm), pogrubienie do "
                     f"{mm(t_w)} mm za licem ocieplenia (nadproże HS na poziomie spodu stropu) — do potwierdzenia "
                     "w PT-K; symulacja WZ-04 z płytą o stałej grubości (wariant ostrożny)")
    return det


# ================================================================================================ D — garaż (WZ-09)
def wezly_garazu_id(m) -> dict:
    """{'plyta'|'dach'|'dach_sciana': id węzła} — podwęzły WZ-09 wg `katalog_dod.wezly_garazu` (bez obliczeń)."""
    from ..obliczenia.mostki2d.katalog_dod import wezly_garazu
    out = {}
    try:
        lst = wezly_garazu(m, wpis(m, "WZ-09")) or []
    except Exception:          # pragma: no cover — geometria nietypowa
        lst = []
    import re
    for w, _L in lst:
        n = w.nazwa or ""
        k = "plyta" if "płycie fundamentowej" in n else "dach_sciana" if "+ ściana" in n else "dach"
        if k not in out:
            out[k] = w.id
            out[k + "_sciany"] = re.findall(r"S\d-\d+", str(w.dane.get("geometria z modelu", "")))
    return out


def sciana_garazu(m, sg: str, ids: list | None):
    """Ściana `sg` węzła (pierwsza z listy id z geometrii węzła; inaczej najdłuższa)."""
    sc = [s for s in m.sciany() if s.przegroda_kod == sg]
    wyb = [s for s in sc if ids and s.id in ids]
    return max(wyb or sc, key=lambda s: s.L)


def zebro_pod(m, s_g) -> dict:
    """Żebro płyty fundamentowej wzdłuż ściany (wspólny odcinek > 1 m)."""
    from shapely.geometry import LineString as _LS
    Ls = _LS([tuple(s_g.p1), tuple(s_g.p2)]).buffer(0.05)
    return next((z for z in (m.fundamenty() or {}).get("elementy") or [] if "os" in z and
                 _LS([tuple(p) for p in z["os"]]).intersection(Ls).length > 1.0), {})


def pas_sufg(m, kod: str | None) -> float:
    import re
    n = (m.przegroda(kod).nazwa or "") if kod and m.przegroda(kod) else ""
    r = re.search(r"pas\w*\s+(\d+(?:[.,]\d+)?)\s*m", n)
    return float(r.group(1).replace(",", ".")) if r else 1.0


@rodzaj("garaz_dach", "WZ-09c", "WZ-09")
def detal_garaz_dach(m, opts: dict) -> Detal:
    """Ściana dom–garaż (oś E) pod stropem ST1 / płytą dachu zielonego D4, ściana P1 domu nad dachem garażu:
    wywinięcie hydroizolacji ≥ 15 cm ponad żwir, opaska żwirowa 0,5 m, XPS w strefie rozbryzgu, pas SUF-G."""
    ids = wezly_garazu_id(m)
    wid = ids.get("dach_sciana") or "WZ-09c"
    e = wpis(m, "WZ-09")
    kody = e.get("przegrody") or []
    sg = next((k for k in kody if m.przegroda(k) and m.przegroda(k).typ.startswith("sciana")
               and m.przegroda(k).typ != "sciana_zewn"), "SWG")
    kd = next((k for k in kody if m.przegroda(k) and m.przegroda(k).typ in ("stropodach", "dach")), "DZ1")
    ksuf = next((k for k in kody if m.przegroda(k) and m.przegroda(k).typ == "strop" and k != "POD-1"), None)
    dach = dach_wg(m, kd)
    s_g = sciana_garazu(m, sg, ids.get("dach_sciana_sciany"))
    st = next((s for s in m.stropy() if s["id"] == "ST1"), m.stropy()[0])
    z0, t_L = float(st["wierzch"]), float(st["grubosc"])
    t_R = float(dach["plyta"]["grubosc"])
    det = Detal(m, "D-10", f"Ściana dom–garaż ({sg}) i dach zielony {dach['id']} przy ścianie domu", (wid,), 10, z0=z0)
    sz = sciana_przy(m, tuple((s_g.p1 + s_g.p2) / 2), z0 + 1.0) or "SZ1"
    Wg, Ws = det.warstwy(sg), det.warstwy(sz)
    kg = next(i for i, w in enumerate(Wg) if w["konstr"])
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs0 = sum(w["d"] for w in Wg[:kg])
    xs1 = xs0 + Wg[kg]["d"]
    xg_out = sum(w["d"] for w in Wg)
    x_iz = sum(w["d"] for w in Ws[:ks + 2])                                # lico izolacji ściany P1
    x_out = sum(w["d"] for w in Ws)
    pod = st.get("podloga") or "POD-1"
    Wp = det.warstwy(pod)
    kp = next((i for i, w in enumerate(Wp) if w["konstr"]), len(Wp))
    y_f = sum(w["d"] for w in Wp[:kp])
    mid = (s_g.p1 + s_g.p2) / 2
    d_kl, _pz = _klin_w(m, dach, tuple(mid - s_g.n * (1 if s_g.wnetrze != "prawa" else -1) * 0.5))
    xL, xR, yB, yT = -0.40, 1.30, -0.80, 1.00
    det.okno = (xL, yB, xR, yT)
    # dach: warstwy nad płytą od lica izolacji ściany P1; substrat zastąpiony żwirem w pasie 0,5 m
    Wd = det.warstwy(kd)
    ksub = next((w["idx"] for w in Wd if "SUBSTR" in w["mat"]), None)
    b_zw = 0.50
    zak = {ksub: (x_iz + b_zw, xR + 0.05)} if ksub is not None else {}
    stos, y_top, _pl = stos_dachu(det, kd, x_iz, xR + 0.05, d_kl, zakres=zak)
    y_sub = next(((a, b) for a, b, w in stos if w["idx"] == ksub), (y_top, y_top - 0.08))
    det.rect(x_iz, y_sub[1], x_iz + b_zw, y_sub[0], "ZWIR_16")
    det.kontur([(x_iz + b_zw, y_sub[1]), (x_iz + b_zw, y_sub[0] + 0.01)], zamkniety=False, pen=0.5)
    y_up = y_top + 0.15                                   # wywinięcie ≥ 15 cm ponad żwir/substrat (DAFA, FLL)
    y_x = y_top + 0.30                                    # strefa rozbryzgu — XPS
    # ściana P1 nad dachem (lico wewn. x = 0), izolacja od wierzchu płyty: XPS do y_x, dalej izolacja ściany
    zs = {w["idx"]: ((y_f, yT) if i < ks else (0.0, yT) if i == ks else (y_x, yT)) for i, w in enumerate(Ws)}
    sc = det.stos_v(sz, 0.0, 0.0, yT, zakres=zs)
    det.rect(xs1, 0.0, x_iz, y_x, "XPS300" if "XPS300" in m.materialy else Ws[ks + 1]["mat"])
    det.rect(x_iz, y_up + 0.005, x_out, y_x, Ws[-1]["mat"])                         # wyprawa mozaikowa cokołu
    det.stos_h(pod, xL, 0.0, y_f, do=kp)
    # płyta ciągła: strop ST1 (dom) / płyta dachu (garaż) — do lica konstrukcji ściany
    det.poly([(xL, 0.0), (xR + 0.05, 0.0), (xR + 0.05, -t_R), (xs1, -t_R), (xs1, -t_L), (xL, -t_L)],
             st.get("mat", "ZB_C25"), konstr=True)
    det._rejestr(kd, next(w for w in Wd if w["konstr"]), t_R)
    det.rect(xL, -t_L - 0.01, 0.0, -t_L, st.get("sufit") if st.get("sufit") in m.materialy else Wg[0]["mat"])
    # ściana dom–garaż pod płytą: izolacja od strony garażu do płyty, pas docieplenia SUF-G
    zg = {w["idx"]: ((yB, -t_L) if i <= kg else (yB, -t_R)) for i, w in enumerate(Wg)}
    Wsg = det.warstwy(ksuf) if ksuf else []
    d_sg = sum(w["d"] for w in Wsg)
    if Wsg:
        zg[Wg[-1]["idx"]] = (yB, -t_R - d_sg)
    scg = det.stos_v(sg, 0.0, yB, -t_R, zakres=zg)
    b_pas = pas_sufg(m, ksuf)
    y = -t_R
    for i, w in enumerate(Wsg):
        xa = xg_out - Wg[-1]["d"] if i == 0 else xg_out
        det.rect(xa, y - w["d"], min(xs1 + b_pas, xR + 0.05), y, w["mat"])
        det._rejestr(ksuf, w, w["d"])
        y -= w["d"]
    return _garaz_dach_linie(det, dict(sc=sc, scg=scg, stos=stos, xs0=xs0, xs1=xs1, xg_out=xg_out, x_iz=x_iz,
                                       x_out=x_out, y_f=y_f, kp=kp, pod=pod, t_L=t_L, t_R=t_R, y_top=y_top,
                                       y_up=y_up, y_x=y_x, b_zw=b_zw, y_sub=y_sub, d_sg=d_sg, b_pas=b_pas,
                                       ksuf=ksuf, kd=kd, sz=sz, sg=sg, xL=xL, xR=xR, yB=yB, yT=yT, d_kl=d_kl,
                                       dach=dach))


def _garaz_dach_linie(det: Detal, g: dict) -> Detal:
    m = det.model
    xL, xR, yB, yT = g["xL"], g["xR"], g["yB"], g["yT"]
    xs1, x_iz, x_out = g["xs1"], g["x_iz"], g["x_out"]
    stos, y_top, y_up = g["stos"], g["y_top"], g["y_up"]
    y_memb = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "hydroizolacja"), y_top)
    y_par = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "paroizolacja"), 0.002)
    y_pir = next((a for a, b, w in stos if w["klin"] or w["mat"].startswith("PIR")), y_top)
    # 4 linie
    det.linia("H", [(xR + 0.05, y_memb), (x_iz + 0.002, y_memb), (x_iz + 0.002, y_up)],
              "papa wierzchnia + bariera przeciwkorzenna wywinięte ≥ 15 cm ponad żwir")
    det.obrobka([(x_iz + 0.002, y_up - 0.03), (x_iz + 0.012, y_up - 0.03), (x_iz + 0.012, y_up + 0.012),
                 (x_iz + 0.004, y_up + 0.02)], kapinos=False)
    det.linia("P", [(xR + 0.05, y_par), (xs1 + 0.002, y_par), (xs1 + 0.002, y_pir + 0.03)],
              "paroizolacja wywinięta na mur ponad izolację dachu")
    det.linia("S", [(0.0015, yT), (0.0015, 0.004), (xL, 0.004)])
    det.linia("S", [(xL, -g["t_L"] - 0.012), (0.0015, -g["t_L"] - 0.012), (0.0015, yB)])
    det.polaczenie("S", [(0.0015, 0.004), (0.0015, -g["t_L"] - 0.012)])
    for p1, p2 in (((0.0, yT), (x_out, yT)), ((xL, yB), (g["xg_out"], yB)), ((xL, g["y_f"]), (xL, -g["t_L"] - 0.01)),
                   ((xR, y_top), (xR, -g["t_R"]))):
        det.przerwa(p1, p2)
    # opisy
    det.opis_stosu(g["sc"], "y", 0.80, odwroc=True, tytul=f"{g['sz']} — ściana P1 domu nad dachem garażu")
    det.opis([(xs1 + 0.10, y_top + 0.24)], ["XPS 300 w strefie rozbryzgu do ≥ 30 cm ponad żwir, wyprawa mozaikowa "
                                            "na masie uszczelniającej"])
    det.opis([(x_iz + 0.008, y_up)], ["listwa dociskowa + uszczelniacz trwale elastyczny, fartuch z blachy nad "
                                      "wywinięciem; wys. ≥ 15 cm ponad żwir (DAFA / FLL)"])
    det.opis([(x_iz + g["b_zw"] / 2, (g["y_sub"][0] + g["y_sub"][1]) / 2)],
             [f"opaska żwirowa 16/32 szer. {mm(g['b_zw'])} mm przy ścianie (strefa bez roślin), obrzeże perforowane"])
    det.opis_stosu([(a, b, w) for a, b, w in stos], "x", xR - 0.12, odwroc=False,
                   tytul=f"{g['kd']} — dach zielony ekstensywny {g['dach']['id']} (klin w przekroju "
                         f"{mm(g['d_kl'] or 0)} mm)")
    det.opis_stosu(g["scg"], "y", -0.62, odwroc=True, tytul=f"{g['sg']} — ściana dom–garaż (szczelna na spaliny)")
    if g["ksuf"]:
        det.opis([(xs1 + 0.55, -g["t_R"] - g["d_sg"] / 2)],
                 [f"{g['ksuf']} — docieplenie spodu płyty pasem {g['b_pas']:.2f} m: ".replace(".", ",")
                  + ", ".join(tekst(det, w["mat"], w["d"]) for w in det.warstwy(g["ksuf"]))])
    det.opis_stosu(det_stos_pod(det, g["pod"], g["y_f"], 0.0)[:g["kp"] + 1], "x", -0.22,
                   wyjscie=(-0.22, yT + 0.03), tytul=f"{g['pod']} — podłoga P1")
    det.opis([(xs1 + 0.40, -g["t_R"] / 2)], ["płyta ŻB ciągła: strop ST1 (dom) / płyta dachu garażu — "
                                             "mostek ograniczony pasem docieplenia (ψ_iu w karcie)"])
    # wymiary, rzędne
    xv = x_iz + g["b_zw"] + 0.10
    det.wymiar([(xv, y_top), (xv, y_up), (xv, g["y_x"])], xv + 0.02, "v")
    det.wymiar([(x_iz, y_top + 0.02), (x_iz + g["b_zw"], y_top + 0.02)], y_top + 0.06, "h")
    det.wymiar([(xs1, -g["t_R"] - g["d_sg"] - 0.05), (min(xs1 + g["b_pas"], xR), -g["t_R"] - g["d_sg"] - 0.05)],
               -g["t_R"] - g["d_sg"] - 0.09, "h")
    det.rzedna((xL + 0.05, g["y_f"]), g["y_f"], "wyk", "right")
    det.rzedna((xL + 0.05, 0.0), 0.0, "konstr", "right")
    det.rzedna((xR - 0.25, y_top), y_top, "wyk", "right")
    det.uwagi.append("dach garażu nieużytkowy; wywinięcia hydroizolacji ≥ 15 cm ponad warstwę wierzchnią (żwir / "
                     "substrat) — wytyczne DAFA (dachy płaskie) i FLL (dachy zielone); pas żwiru 50 cm przy ścianach, "
                     "attykach i wpustach; paroizolacja i bariera przeciwkorzenna wywinięte na mur")
    det.uwagi.append(f"garaż nieogrzewany: ψ_iu węzła (strona garażu) × b_u = 0,8 → H_U (zestawienie H_TB)")
    return det


@rodzaj("garaz_plyta", "WZ-09a")
def detal_garaz_plyta(m, opts: dict) -> Detal:
    """Ściana dom–garaż na ciągłej płycie fundamentowej (żebro wewn.): posadzka domu / garażu, wełna od strony
    garażu, mostek przez płytę — wariant zalecany (XPS pod jastrychem garażu + bloczek izolacyjny) liniami kreskowymi."""
    ids = wezly_garazu_id(m)
    wid = ids.get("plyta") or "WZ-09a"
    e = wpis(m, "WZ-09")
    kody = e.get("przegrody") or []
    sg = next((k for k in kody if m.przegroda(k) and m.przegroda(k).typ.startswith("sciana")
               and m.przegroda(k).typ != "sciana_zewn"), "SWG")
    pd = next((k for k in kody if m.przegroda(k) and m.przegroda(k).typ == "podloga_na_gruncie"), "POD-0")
    pg = next((k for k, p in m.przegrody.items() if p.typ == "podloga_na_gruncie" and k != pd
               and "gara" in (p.nazwa or "").lower()), pd)
    det = Detal(m, "D-11", f"Ściana dom–garaż ({sg}) na płycie fundamentowej", (wid,), 10)
    s_g = sciana_garazu(m, sg, ids.get("plyta_sciany"))
    zb = zebro_pod(m, s_g)
    Wg = det.warstwy(sg)
    kg = next(i for i, w in enumerate(Wg) if w["konstr"])
    xs0 = sum(w["d"] for w in Wg[:kg])
    xs1 = xs0 + Wg[kg]["d"]
    xg = sum(w["d"] for w in Wg)
    W, G = det.warstwy(pd), det.warstwy(pg)
    ki = next(i for i, w in enumerate(W) if w["konstr"])
    kj = next(i for i, w in enumerate(G) if w["konstr"])
    y_pl = -sum(w["d"] for w in W[:ki])
    t_pl = W[ki]["d"]
    y_g = y_pl + sum(w["d"] for w in G[:kj])                       # posadzka garażu (płyta wspólna)
    b_z, h_z = float(zb.get("b", 0.5)), float(zb.get("h", 0.25))
    xps = next((w for w in W[ki + 1:] if w["d"] >= 0.05), None)
    d_x, m_x = (xps["d"], xps["mat"]) if xps else (0.20, "XPS300")
    pod = next((w for w in W[ki + 1:] if w["d"] >= 0.05 and w is not xps), None)
    d_p = pod["d"] if pod else 0.0
    xL, xR, yT, yB = -0.45, 1.05, 0.45, -1.10
    det.okno = (xL, yB, xR, yT)
    xc = (xs0 + xs1) / 2
    y_sp = y_pl - t_pl
    y_zb = y_sp - h_z
    det.rect(xL - 0.5, yB - 0.1, xR + 0.1, y_sp - d_x, "GRUNT")
    # płyta z żebrem (jeden obrys), XPS i podsypka pod płytą i żebrem
    det.poly([(xL - 0.5, y_pl), (xR + 0.1, y_pl), (xR + 0.1, y_sp), (xc + b_z / 2, y_sp), (xc + b_z / 2, y_zb),
              (xc - b_z / 2, y_zb), (xc - b_z / 2, y_sp), (xL - 0.5, y_sp)], W[ki]["mat"], konstr=True)
    det._rejestr(pd, W[ki], t_pl)
    det.poly([(xL - 0.5, y_sp), (xc - b_z / 2, y_sp), (xc - b_z / 2, y_zb), (xc + b_z / 2, y_zb), (xc + b_z / 2, y_sp),
              (xR + 0.1, y_sp), (xR + 0.1, y_sp - d_x), (xc + b_z / 2 + d_x, y_sp - d_x),
              (xc + b_z / 2 + d_x, y_zb - d_x), (xc - b_z / 2 - d_x, y_zb - d_x), (xc - b_z / 2 - d_x, y_sp - d_x),
              (xL - 0.5, y_sp - d_x)], m_x)
    if xps:
        det._rejestr(pd, xps, d_x)
    def prof(d):
        return [(xL - 0.5, y_sp - d), (xc - b_z / 2 - d, y_sp - d), (xc - b_z / 2 - d, y_zb - d),
                (xc + b_z / 2 + d, y_zb - d), (xc + b_z / 2 + d, y_sp - d), (xR + 0.1, y_sp - d)]
    if pod:
        det.poly(prof(d_x) + list(reversed(prof(d_x + d_p))), pod["mat"])
        det._rejestr(pd, pod, d_p)
    det.cienka(prof(d_x), "FOLIA_PE", "G")
    # posadzki: dom (membrana SBS pod murem do lica konstrukcji), garaż od lica ściany
    zak = {w["idx"]: (xL - 0.5, 0.0) for w in W[:ki]}
    for w in W[:ki]:
        if w["d"] < 0.006:
            zak[w["idx"]] = (xL - 0.5, xs1)
    st = det.stos_h(pd, xL - 0.5, 0.0, 0.0, zakres=zak, do=ki)
    y = y_g
    for w in G[:kj]:
        if w["d"] < 0.006:
            det.cienka([(xg, y - w["d"] / 2), (xR + 0.1, y - w["d"] / 2)], w["mat"])
        else:
            det.rect(xg, y - w["d"], xR + 0.1, y, w["mat"])
        det._rejestr(pg, w, w["d"])
        y -= w["d"]
    zs = {w["idx"]: ((0.0, yT) if i < kg else (y_pl, yT) if i == kg else (y_pl, yT)) for i, w in enumerate(Wg)}
    sc = det.stos_v(sg, 0.0, y_pl, yT, zakres=zs)
    return _garaz_plyta_opisy(det, dict(sg=sg, pd=pd, pg=pg, sc=sc, st=st, ki=ki, kj=kj, xs0=xs0, xs1=xs1, xg=xg,
                                        y_pl=y_pl, y_g=y_g, y_sp=y_sp, y_zb=y_zb, b_z=b_z, h_z=h_z, xc=xc, d_x=d_x,
                                        m_x=m_x, d_p=d_p, pod=pod, xL=xL, xR=xR, yT=yT, yB=yB, zb=zb))


def _garaz_plyta_opisy(det: Detal, g: dict) -> Detal:
    xL, xR, yT, yB = g["xL"], g["xR"], g["yT"], g["yB"]
    xs0, xs1, xg, y_pl, y_g = g["xs0"], g["xs1"], g["xg"], g["y_pl"], g["y_g"]
    st = g["st"]
    y_m = next(((a + b) / 2 for a, b, w in st if w["d"] < 0.006), y_pl + 0.0025)
    det.linia("S", [(0.0015, yT), (0.0015, y_pl - 0.004), (xL, y_pl - 0.004)], "tynk wewn. do płyty ŻB")
    det.linia("P", [(xL, y_m + 0.004), (xs1, y_m + 0.004)], "membrana SBS — bariera pary i radonu pod murem")
    # wariant zalecany (REKOMENDACJE A): XPS pod jastrychem garażu pasem 1,0 m + bloczek izolacyjny w 1. warstwie
    h_bl = 0.24
    det.kontur([(xs0, y_pl), (xs0, y_pl + h_bl), (xs1, y_pl + h_bl), (xs1, y_pl)], zamkniety=False, pen=0.35,
               lt="KRESKOWA")
    det.kontur([(min(xg + 1.0, xR), y_g - 0.05), (xg, y_g - 0.05), (xg, y_g - 0.15), (min(xg + 1.0, xR), y_g - 0.15),
                (min(xg + 1.0, xR), y_g - 0.05)], zamkniety=False, pen=0.35, lt="KRESKOWA")
    for p1, p2 in (((0.0, yT), (xg, yT)), ((xL, yB), (xR, yB)), ((xL, 0.0), (xL, yB)), ((xR, y_g), (xR, yB))):
        det.przerwa(p1, p2)
    det.opis_stosu(g["sc"], "y", 0.30, odwroc=True, tytul=f"{g['sg']} — ściana dom–garaż (szczelna na spaliny)")
    det.opis_stosu(st[:g["ki"] + 1], "x", -0.22, odwroc=False, wyjscie=(-0.22, yT + 0.03),
                   tytul=f"{g['pd']} — podłoga domu")
    Gs = det_stos_pod(det, g["pg"], y_g, 0.0)[:g["kj"]]
    det.opis_stosu(Gs, "x", xR - 0.12, odwroc=False, tytul=f"{g['pg']} — posadzka garażu (bez izolacji termicznej, "
                                                          "płyta wspólna z domem)")
    det.opis([(xg + 0.45, y_g - 0.10)], ["WARIANT ZALECANY (linie kreskowe): XPS 300 100 mm pod jastrychem garażu "
                                         "pasem 1,0 m od ściany (jastrych dociążony 50 mm na XPS — wg PT-K) "
                                         "— REKOMENDACJE mostków, rozdz. A (WZ-09a)"])
    det.opis([((xs0 + xs1) / 2, y_pl + 0.12)], ["WARIANT ZALECANY: 1. warstwa muru z bloczka izolacyjnego "
                                                "(beton komórkowy 400, λ ≈ 0,10–0,24 — wg nośności PT-K)"])
    det.opis([(g["xc"] + 0.12, (g["y_sp"] + g["y_zb"]) / 2)],
             [f"żebro płyty {int(round(g['b_z'] * 100))}×{int(round(g['h_z'] * 100))} cm pod ścianą "
              f"({g['zb'].get('id', 'wg PT-K')})"])
    det.opis([(g["xc"] + g["b_z"] / 2 + 0.2, g["y_sp"] - g["d_x"] / 2)],
             [f"pod płytą: {tekst(det, g['m_x'], g['d_x'])} ciągły (dom i garaż), folia PE, "
              + (tekst(det, g["pod"]["mat"], g["d_p"]) if g["pod"] else "podsypka")])
    det.rzedna((xL + 0.06, 0.0), 0.0, "zero", "right")
    det.rzedna((xR - 0.30, y_g), y_g, "wyk", "right")
    det.rzedna((xL + 0.06, y_pl), y_pl, "konstr", "right")
    det.uwagi.append("płyta fundamentowa ciągła pod ścianą dom–garaż — mostek konstrukcyjny ψ_iu (strona garażu × "
                     "b_u); stan wg modelu = linie ciągłe, wariant zalecany = linie kreskowe (decyzja PT-K/Inwestor)")
    det.uwagi.append("posadzka garażu: jastrych spadkowy 0,8 % do bramy — grubość przy ścianie wg modelu "
                     f"({mm(y_g - y_pl)} mm); garaż bez membrany na płycie (płyta wodoszczelna W8 wg PT-K)")
    return det


# ================================================================================================ D — lamele (rzut)
@rodzaj("lamele", "WZ-13")
def detal_lamele(m, opts: dict) -> Detal:
    """Przekrój poziomy (rzut) ściany SZ2 z lamelami na wysokości konsoli: konsola z przekładką termiczną przez
    wełnę fasadową, mankiet na membranie, rygiel, lamele pionowe; mostek punktowy χ (WZ-13)."""
    sz = przegroda_typu(m, "WZ-13", "sciana_zewn", "SZ2")
    lm = next((l_ for l_ in m.raw.get("lamele") or [] if float(l_.get("odsuniecie", 0)) > 0), {})
    b, h = float(lm.get("b", 0.04)), float(lm.get("h", 0.08))
    roz, ods = float(lm.get("rozstaw", 0.12)), float(lm.get("odsuniecie", 0.15))
    det = Detal(m, "D-12", f"Lamele elewacyjne {sz} — konsola rusztu (rzut)", ("WZ-13",), 5)
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    xL, xR, yB, yT = -0.08, x_out + ods + h + 0.05, 0.0, 0.60
    det.okno = (xL, yB, xR, yT)
    det.rect(xL - 0.1, yB - 0.05, 0.0, yT + 0.05, "POWIETRZE") if "POWIETRZE" in m.materialy else None
    sc = det.stos_v(sz, 0.0, yB - 0.05, yT + 0.05)
    yk = 0.30                                                  # oś konsoli
    xl0 = x_out + ods                                          # lico tylne lamel
    xr0, xr1 = xl0 - 0.05, xl0                                 # rygiel 50 mm (głęb.) w szczelinie
    det.rect(xr0, yB - 0.05, xr1, yT + 0.05, "RYGIEL")
    det.rect(xs1, yk - 0.05, xs1 + 0.010, yk + 0.05, "PRZEKLADKA")
    det.rect(xs1 + 0.010, yk - 0.05, xs1 + 0.016, yk + 0.05, "KONSOLA")
    det.rect(xs1 + 0.016, yk - 0.003, xr0, yk + 0.003, "KONSOLA")
    det.kontur([(xs1 + 0.010, yk), (xs1 - 0.09, yk)], zamkniety=False, pen=0.5)             # kotwa
    det.kontur([(xs1 - 0.09, yk - 0.006), (xs1 - 0.09, yk + 0.006)], zamkniety=False, pen=0.35)
    y = yB + 0.03
    while y + b <= yT + 0.001:
        det.rect(xl0, y, xl0 + h, y + b, lm.get("mat", "DREWNO_TERMO"))
        det.kontur([(xr1, y + b / 2), (xl0 + 0.035, y + b / 2)], zamkniety=False, pen=0.25)   # wkręt od tyłu
        y += roz
    # 4 linie: szczelność (tynk wewn.), wiatro-/wodoizolacja fasadowa z mankietem na konsoli
    x_m = x_out - Ws[-1]["d"] / 2
    det.linia("S", [(0.0015, yB), (0.0015, yT)], "tynk wewn. — warstwa szczelna")
    det.linia("H", [(x_m, yB), (x_m, yk - 0.02)])
    det.linia("H", [(x_m, yk + 0.02), (x_m, yT)])
    det.linia("T_out", [(x_m, yk - 0.03), (x_m + 0.004, yk - 0.03), (x_m + 0.004, yk - 0.004), (x_out + 0.02, yk - 0.004)])
    det.linia("T_out", [(x_m, yk + 0.03), (x_m + 0.004, yk + 0.03), (x_m + 0.004, yk + 0.004), (x_out + 0.02, yk + 0.004)])
    det.polaczenie("H", [(x_out + 0.02, yk - 0.004), (x_out + 0.02, yk + 0.004)])        # mankiet wokół konsoli
    for p1, p2 in (((xL, yB), (xR, yB)), ((xL, yT), (xR, yT))):
        det.przerwa(p1, p2)
    # opisy
    det.opis_stosu(sc, "y", 0.52, odwroc=True, tytul=f"{sz} — ściana bryły A za lamelami")
    det.opis([(xs1 + 0.005, yk + 0.035)], ["przekładka termoizolacyjna 10 mm (PA / EPDM) pod stopą konsoli"])
    det.opis([(xs1 + 0.10, yk + 0.003)], ["konsola ze stali nierdz. / alu z przekładką — przez wełnę fasadową, "
                                          "wełna docięta szczelnie wokół; rozstaw ≤ 1,0 m na 2 ryglach"])
    det.opis([(xs1 - 0.05, yk)], ["kotwa (tuleja / kotwa chemiczna) w bloczku silikatowym — wg ETA producenta"])
    det.opis([(x_out + 0.012, yk - 0.004)], ["mankiet EPDM / taśma uszczelniająca membranę wokół konsoli"])
    det.opis([((xr0 + xr1) / 2, 0.10)], ["rygiel aluminiowy 50 mm (poziomy, 2 szt. na wysokości kondygnacji)"])
    det.opis([(xl0 + h / 2, yB + 0.03 + b / 2)],
             [f"{nazwa_lamel(det, lm)} {mm(b)}×{mm(h)} co {mm(roz)} mm, pionowe; wkręty nierdz. od tyłu przez rygiel"])
    det.opis([((x_out + xr0) / 2, 0.45)], [f"szczelina wentylowana {mm(xr0 - x_out)} mm (wlot / wylot z siatką "
                                           "przeciw owadom na dole i u góry)"])
    det.wymiar([(a, yT) for a, _b, _w in sc] + [(x_out, yT), (xr0, yT), (xl0, yT), (xl0 + h, yT)], yT + 0.03, "h")
    det.wymiar([(xl0 + h, yB + 0.03), (xl0 + h, yB + 0.03 + b), (xl0 + h, yB + 0.03 + roz)], xl0 + h + 0.025, "v")
    det.uwagi.append("mostek punktowy konsoli: χ wg deklaracji producenta (wartość w zestawieniu H_TB — dane "
                     "przykładowe do potwierdzenia wyrobem); liczba konsol z długości linii lamel × 2 rygle / 1,0 m")
    det.uwagi.append("rzut na wysokości konsoli — rozstaw konsol i rygli wg obliczeń statycznych rusztu (PT-K / "
                     "dostawca systemu)")
    return det


# ================================================================================================ D — wyłaz / świetlik
@rodzaj("wylaz", "WYL1", "SW1")
def detal_wylaz(m, opts: dict) -> Detal:
    """Wyłaz dachowy / świetlik na cokole ocieplonym (h z modelu) w stropodachu: krawędź otworu w płycie, cokół
    z izolacją ciągłą z izolacją dachu, membrana wywinięta na cokół pod obróbkę ramy, paroizolacja i warstwa
    szczelna wywinięte na cokół (taśma do ramy)."""
    import re
    el = next((w for w in m.wsporniki() if w["id"] == opts.get("element", "WYL1")), None) or \
        next(w for w in m.wsporniki() if w["id"] in ("WYL1", "SW1"))
    from shapely.geometry import Polygon as _P, Point as _Pt
    c = _P(el["obrys"]).centroid
    dach = next((d for d in m.dachy() if _P(d["obrys"]).contains(_Pt(c.x, c.y))), m.dachy()[0])
    kd = dach["przegroda"]
    r = re.search(r"cokole[^,;]*?h\s*(\d+[.,]\d+)", str(el.get("uwagi", "")))
    h_c = float(r.group(1).replace(",", ".")) if r else 0.30
    nazwa = "Wyłaz dachowy" if el["id"].startswith("WYL") else "Świetlik"
    det = Detal(m, "D-13", f"{nazwa} {el['id']} — cokół ocieplony h {h_c:.2f} m".replace(".", ","), (), 10,
                z0=float(dach["plyta"]["wierzch"]))
    d_kl, _pz = _klin_w(m, dach, (c.x, c.y))
    Wd = det.warstwy(kd)
    kk = next(i for i, w in enumerate(Wd) if w["konstr"])
    t = Wd[kk]["d"]
    xL, xR, yB, yT = -0.40, 0.95, -0.42, 0.0
    b_s, b_c = 0.018, 0.10                                   # sklejka / rdzeń cokołu (kaseta ocieplona)
    x_c1 = b_c + b_s                                         # lico zewn. cokołu (od krawędzi otworu x = 0)
    stos, y_top, _pl = stos_dachu(det, kd, x_c1, xR + 0.05, d_kl)
    y_cap = y_top + h_c
    yT = y_cap + 0.20
    det.okno = (xL, yB, xR, yT)
    det.rect(0.0, -t, xR + 0.05, 0.0, Wd[kk]["mat"], konstr=True)
    det._rejestr(kd, Wd[kk], t)
    y = -t
    for w in Wd[kk + 1:]:
        det.rect(-0.012, y - w["d"], xR + 0.05, y, w["mat"])
        det._rejestr(kd, w, w["d"])
        y -= w["d"]
    det.rect(-0.0125, y, 0.0, 0.0, "GK" if "GK" in m.materialy else Wd[-1]["mat"])       # obudowa ościeża
    det.rect(0.0, 0.0, b_c, y_cap, "OSCIEZNICA")
    det.rect(b_c, 0.0, x_c1, y_cap, "SKLEJKA")
    det.rect(-0.0125, 0.0, 0.0, y_cap, "GK" if "GK" in m.materialy else Wd[-1]["mat"])
    # rama wyłazu / świetlika i klapa (ocieplona) — wyrób systemowy
    det.rect(-0.03, y_cap, x_c1 + 0.01, y_cap + 0.07, "RAMA_ALU")
    det.rect(xL - 0.05, y_cap + 0.07, x_c1 + 0.01, y_cap + 0.13, "OSCIEZNICA" if el["id"].startswith("WYL")
             else "SZYBA3")
    det.obrobka([(x_c1 + 0.03, y_cap + 0.10), (x_c1 + 0.03, y_cap - 0.06)], strona=1)
    # 4 linie
    y_memb = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "hydroizolacja"), y_top)
    y_par = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "paroizolacja"), 0.002)
    det.linia("H", [(xR + 0.05, y_memb), (x_c1 + 0.002, y_memb), (x_c1 + 0.002, y_cap - 0.01),
                    (x_c1 + 0.012, y_cap - 0.01)], "membrana wywinięta na cokół pod obróbkę ramy")
    det.linia("P", [(xR + 0.05, y_par), (x_c1 + 0.002, y_par), (x_c1 + 0.002, y_top + 0.04)],
              "paroizolacja wywinięta na cokół ponad izolację dachu")
    det.linia("S", [(xR + 0.05, -t - 0.012), (-0.014, -t - 0.012), (-0.014, y_cap - 0.02)])
    det.linia("T_in", [(-0.014, y_cap - 0.04), (-0.014, y_cap + 0.002), (0.02, y_cap + 0.002)])
    det.polaczenie("H", [(x_c1 + 0.012, y_cap - 0.01), (x_c1 + 0.03, y_cap + 0.10)])
    for p1, p2 in (((xR, -t - 0.03), (xR, y_top + 0.02)), ((xL, y_cap + 0.07), (xL, y_cap + 0.13))):
        det.przerwa(p1, p2)
    det.opis_stosu([(a, b, w) for a, b, w in stos], "x", xR - 0.12, odwroc=False,
                   tytul=f"{kd} — stropodach (klin w przekroju {mm(d_kl or 0)} mm)")
    det.opis([(b_c / 2, y_top + 0.10)], [f"cokół systemowy ocieplony (kaseta PIR {mm(b_c)} mm + sklejka "
                                         f"wodoodporna 18 mm), wys. {mm(h_c)} mm ponad pokrycie (≥ 150 mm — DAFA)"])
    det.opis([(x_c1 + 0.03, y_cap + 0.03)], ["obróbka ramy (fartuch) z okapnikiem, zakład ≥ 50 mm na membranę"])
    det.opis([(x_c1 * 0.5, y_cap + 0.035)], [f"rama {'wyłazu' if el['id'].startswith('WYL') else 'świetlika'} {el['id']} (wyrób systemowy, U ≤ 1,1), "
                                             "taśma paroszczelna rama–obudowa od wewnątrz"])
    det.opis([(-0.20, y_cap + 0.10)], ["klapa ocieplona (wyłaz 0,90 × 0,90 m w świetle, W-065)"
                                       if el["id"].startswith("WYL") else "przeszklenie świetlika (VSG) wg producenta"])
    det.opis([(-0.006, -t / 2)], ["obudowa ościeża GK 12,5 mm na kleju, taśma szczelna do tynku sufitu"])
    det.opis([(0.4, -t / 2)], [f"płyta stropodachu ŻB {mm(t)} mm — krawędź otworu (wymian wg PT-K)"])
    det.wymiar([(x_c1 + 0.08, y_top), (x_c1 + 0.08, y_cap)], x_c1 + 0.10, "v")
    det.rzedna((xR - 0.30, y_top), y_top, "wyk", "right")
    det.rzedna((xR - 0.30, 0.0), 0.0, "konstr", "right")
    det.uwagi.append(f"{el['id']}: cokół h {mm(h_c)} mm ≥ 150 mm ponad pokrycie (wytyczne DAFA), izolacja cokołu "
                     "ciągła z izolacją dachu; mostek liniowy krawędzi cokołu uwzględniony w U wyrobu (EN ISO 12567-2 / "
                     "deklaracja producenta)")
    return det


# ================================================================================================ D — rura spustowa
def rura_zewn(m, rid: str | None = None) -> tuple[dict, dict]:
    """(rura spustowa zewnętrzna z modelu, dach) — pierwsza z trasą 'zewn' (albo o id rid)."""
    for d in m.dachy():
        for r in d.get("rury_spustowe") or []:
            if (rid and r.get("id") == rid) or (not rid and r.get("trasa") == "zewn"):
                return r, d
    return {}, {}


@rodzaj("rura_cokol", "RS")
def detal_rura_cokol(m, opts: dict) -> Detal:
    """Rura spustowa zewnętrzna przy cokole: obejmy na elementach montażowych ETICS (bez przebicia izolacji do muru),
    czyszczak nad terenem, przejście do PVC-U w opasce, przejście przez izolację obwodową, kolano i odpływ do KD."""
    import re
    r, d = rura_zewn(m, opts.get("rura"))
    det = detal_cokol(m, {"_xR": 1.40, "_yT": 0.85, "_yB": -1.30})
    det.id, det.tytul = "D-07", f"Rura spustowa {r.get('id', 'RS')} przy cokole — czyszczak i odpływ do KD"
    P = det.pom
    x_out, tz, xR, yT, yB = P["x_out"], P["tz"], P["xR"], P["yT"], P["yB"]
    det.opisy = [o for o in det.opisy if (o.tytul or "").startswith(("SZ", "POD")) or
                 any(k in " ".join(o.teksty) for k in ("izolacja obwodowa",))]
    det.wymiary, det.przerwy, det.spadki = [], [], []
    det.okno = (P["xL"], yB, xR, yT)
    dn = float(r.get("dn", 100)) / 1000.0
    ro = dn / 2 + 0.005                                        # promień zewn. PVC 110 / rury 100
    xa = x_out + 0.035 + ro                                    # oś rury (odsunięcie od lica ETICS 35 mm)
    mc = re.search(r"czyszczak\s*(\d+[.,]\d+)\s*m", str(r.get("opis", "")))
    h_cz = float(mc.group(1).replace(",", ".")) if mc else 0.5
    y_c0, y_c1 = tz + h_cz - 0.12, tz + h_cz + 0.12            # czyszczak
    y_k = tz - 0.85                                            # oś odejścia poziomego (≥ h_z 0,8 m pod XPS)
    rk = 0.12                                                  # promień kolana (oś)
    # pustka rury (odjęta od gruntu, opaski, XPS) i ścianki rury
    y_x0 = tz - P["gl"] - P["d_n"]
    det.otwor(xa - ro, y_x0 - 0.005, xa + ro, tz + 0.01)        # przejście przez opaskę i XPS (niżej — grunt)
    for sx in (-1, 1):
        det.kontur([(xa + sx * (ro - 0.005), yT), (xa + sx * (ro - 0.005), y_c1)], zamkniety=False, pen=0.5)
        det.kontur([(xa + sx * ro, y_c0), (xa + sx * ro, y_k + rk)], zamkniety=False, pen=0.5)
    import numpy as np
    for rr in (rk + ro, rk - ro):
        a = np.linspace(np.pi, 1.5 * np.pi, 16)
        det.kontur([(xa + rk + rr * np.cos(t_), y_k + rk + rr * np.sin(t_)) for t_ in a], zamkniety=False, pen=0.5)
    for sy in (-1, 1):
        det.kontur([(xa + rk, y_k + sy * ro), (xR, y_k + sy * ro - 0.02 * (xR - xa - rk))],
                   zamkniety=False, pen=0.5)
    det.kontur([(xa - ro - 0.006, y_c0), (xa + ro + 0.006, y_c0), (xa + ro + 0.006, y_c1), (xa - ro - 0.006, y_c1)],
               pen=0.5)
    det.kontur([(xa + ro + 0.006, y_c0 + 0.03), (xa + ro + 0.02, y_c0 + 0.03), (xa + ro + 0.02, y_c1 - 0.03),
                (xa + ro + 0.006, y_c1 - 0.03)], zamkniety=False, pen=0.35)
    # otulina nad XPS obwodowym, uszczelnienie przejścia przez XPS
    y_x1 = tz - P["gl"]
    for sx in (-1, 1):
        det.rect(xa + sx * ro, tz - 0.02, xa + sx * (ro + 0.02), y_x1, "OTULINA")
        det.rect(xa + sx * ro, y_x0, xa + sx * (ro + 0.008), y_x1, "PIANKA")
    # obejma dystansowa na elemencie montażowym ETICS
    y_o = yT - 0.18
    x_iz0 = P["xs1"]
    det.rect(x_iz0, y_o - 0.035, x_out - 0.01, y_o + 0.035, "PIANKA")
    det.kontur([(x_out - 0.06, y_o), (xa - ro, y_o)], zamkniety=False, pen=0.5)
    det.kontur([(xa - ro - 0.004, y_o - 0.015), (xa - ro - 0.004, y_o + 0.015)], zamkniety=False, pen=0.7)
    det.kontur([(xa + ro + 0.004, y_o - 0.015), (xa + ro + 0.004, y_o + 0.015)], zamkniety=False, pen=0.7)
    return _rura_opisy(det, dict(r=r, d=d, xa=xa, ro=ro, y_c0=y_c0, y_c1=y_c1, y_k=y_k, rk=rk, y_o=y_o, h_cz=h_cz,
                                 y_x0=y_x0, y_x1=y_x1, x_iz0=x_iz0))


def _rura_opisy(det: Detal, g: dict) -> Detal:
    m = det.model
    P = det.pom
    r, xa, ro, tz = g["r"], g["xa"], g["ro"], P["tz"]
    zb = ((getattr(getattr(m, "dz", None), "raw", None) or {}).get("retencja") or {}).get("zbiornik") or {}
    import re
    kol = re.search(r"kolektor\s+(KD-\w+)", str(r.get("opis", "")))
    kol = kol.group(1) if kol else "KD"
    det.opis([(xa + ro, g["y_o"] + 0.08)], [f"rura spustowa {r.get('id', 'RS')} DN{int(r.get('dn', 100))} "
                                           "(stal powlekana / tytan-cynk), obejmy co ≤ 2,0 m"])
    det.opis([((g["x_iz0"] + P["x_out"]) / 2, g["y_o"])], ["element montażowy ETICS (walec z twardej pianki PU, "
                                                           "klejony do muru) — obejma bez przebicia izolacji"])
    det.opis([(xa + ro + 0.02, (g["y_c0"] + g["y_c1"]) / 2)],
             [f"czyszczak (rewizja z klapką i osadnikiem) {g['h_cz']:.2f} m nad terenem".replace(".", ",")])
    det.opis([(xa + ro, tz + 0.06)], ["złączka rura spustowa / PVC-U KD 110 SN8 z uszczelką, w opasce żwirowej"])
    det.opis([(xa + ro + 0.01, tz - 0.25)], ["otulina PE 20 mm w strefie nad izolacją obwodową"])
    det.opis([(xa + ro + 0.004, (g["y_x0"] + g["y_x1"]) / 2)],
             ["przejście przez XPS obwodowy: otwór dopasowany, szczelina wypełniona pianką niskoprężną"])
    det.opis([(xa + g["rk"] + 0.25, g["y_k"])],
             [f"kolano 87° + PVC-U 110, i ≥ 2 % → kolektor {kol} PVC 160 → "
              + (f"zbiornik retencyjny {str(zb.get('V', '')).replace('.', ',')} m³" if zb else "zbiornik retencyjny (PZT)")])
    sc, yT = P["sc"], P["yT"]
    det.wymiar([(a, yT) for a, _b, _w in sc] + [(sc[-1][1], yT), (xa - ro, yT), (xa + ro, yT)], yT + 0.06, "h")
    det.wymiar([(xa + ro + 0.10, g["y_k"]), (xa + ro + 0.10, tz), (xa + ro + 0.10, tz + g["h_cz"])],
               xa + ro + 0.12, "v")
    for o in det.opisy:                      # odnośnik warstw ściany — między obejmą a czyszczakiem
        if (o.tytul or "").startswith("SZ"):
            yy = (g["y_c1"] + g["y_o"]) / 2
            o.pts = [(p_[0], yy) for p_ in o.pts]
    for p1, p2 in (((0.0, P["yT"]), (P["x_out"], P["yT"])), ((P["xL"], P["yB"]), (P["xR"], P["yB"])),
                   ((P["xL"], 0.0), (P["xL"], P["yB"])), ((P["xR"], tz), (P["xR"], P["yB"]))):
        det.przerwa(p1, p2)
    det.spadek((P["x_out"] + 0.62, tz + 0.03), (P["x_out"] + 0.80, tz + 0.026), 2.0)
    det.uwagi.append(f"{r.get('id', 'RS')}: {r.get('opis', '')}; odpływ do zbiornika — sieć KD wg PZT / PT-IS "
                     "(zagłębienie ≥ h_z 0,8 m lub w strefie izolacji obwodowej)")
    return det


# ================================================================================================ D — próg DZ2 garażu
def teren_projektowany(m, xy) -> float | None:
    """Rzędna terenu projektowanego (względna) w punkcie układu budynku — z modelu działki (TIN), albo None."""
    if getattr(m, "dz", None) is None:
        return None
    try:
        from types import SimpleNamespace
        from .site_data import SiteData
        s = SiteData(SimpleNamespace(model=m, cfg={}))
        h = s.H_proj(s.P([tuple(xy)]))
        return None if h is None else float(h[0]) - s.zero_abs
    except Exception:          # pragma: no cover — model działki niepełny
        return None


@rodzaj("prog_dz2", "DZ2")
def detal_prog_dz2(m, opts: dict) -> Detal:
    """Drzwi boczne garażu (nieogrzewany) przy terenie podniesionym: próg na podwalinie, uszczelnienie KMB/EPDM
    wywinięte pod profil, odwodnienie liniowe przed drzwiami na całą szerokość, nawierzchnia ze spadkiem od budynku."""
    sym = opts.get("symbol", "DZ2")
    o = next((o for o in m.otwory() if o.raw.get("symbol") == sym), None)
    sz = o.sciana.przegroda_kod if o is not None and o.sciana is not None else "SZ1"
    gar = next((p for p in m.pomieszczenia("P0") if (p.raw or {}).get("rodzaj") == "garaz"), None)
    z_f = float((gar.raw or {}).get("rzedna", -0.10)) if gar is not None else -0.10
    pg = (gar.raw or {}).get("podloga", "POD-G") if gar is not None else "POD-G"
    tz_abs = None
    if o is not None and o.sciana is not None:
        s_ = o.sciana
        t_ = (s_.p2 - s_.p1) / max(s_.L, 1e-9)
        mid = s_.p1 + t_ * (float(o.raw.get("odl", 0)) + float(o.szer) / 2)
        n_out = s_.n * (1 if s_.wnetrze == "prawa" else -1)
        tz_abs = teren_projektowany(m, mid + n_out * 0.6)
    tz = (tz_abs if tz_abs is not None else teren(m)) - z_f          # teren wzgl. posadzki garażu (y = 0)
    det = Detal(m, "D-14", f"Próg drzwi {sym} garażu — odwodnienie liniowe i uszczelnienie", (), 10, z0=z_f)
    Ws = det.warstwy(sz)
    ks = next(i for i, w in enumerate(Ws) if w["konstr"])
    xs1 = sum(w["d"] for w in Ws[:ks + 1])
    x_out = sum(w["d"] for w in Ws)
    d_f, ws = osadzenie(m, sz)
    xf0, xf1 = xs1 - ws, xs1 - ws + d_f
    xL, xR, yT, yB = -0.30, 1.00, 0.35, -1.00
    det.okno = (xL, yB, xR, yT)
    P = plyta_fund(det, pg, xs1, xL, xR, yB, tz, x_podl=xf0, x_sbs=xs1)
    y_pl = P["y_pl"]
    xp1 = xf1 + 0.03
    y_kr = min(tz, -0.03)                                    # ruszt odwodnienia (≥ 3 cm poniżej progu)
    det.rect(xs1, P["y_zb"], xs1 + P["d_x"], y_pl, P["m_x"])                          # XPS na czole płyty
    det.rect(xp1, y_pl, xs1 + P["d_x"], -0.005, P["m_x"])                             # XPS przed podwaliną
    det.rect(xf0, y_pl, xp1, 0.0, "PODWALINA")
    det.rect(xf0, 0.0, xf1, 0.08, "RAMA_ALU")
    det.rect(xf0 + 0.015, 0.08, xf0 + 0.06, yT, "SKLEJKA")                               # skrzydło (przekrój)
    xk0, xk1 = xs1 + P["d_x"] + 0.005, xs1 + P["d_x"] + 0.135
    det.poly([(xk0, y_kr), (xk1, y_kr), (xk1, y_kr - 0.14), (xk0, y_kr - 0.14)], "KORYTKO")
    det.otwor(xk0 + 0.012, y_kr - 0.125, xk1 - 0.012, y_kr - 0.004)
    x_n = xk1 + 0.005
    det.poly([(x_n, y_kr - 0.003), (xR + 0.1, y_kr - 0.003 - 0.02 * (xR + 0.1 - x_n)),
              (xR + 0.1, y_kr - 0.053 - 0.02 * (xR + 0.1 - x_n)), (x_n, y_kr - 0.053)], "PLYTA_BET")
    det.poly([(x_n, y_kr - 0.053), (xR + 0.1, y_kr - 0.053 - 0.02 * (xR + 0.1 - x_n)),
              (xR + 0.1, y_kr - 0.33 - 0.02 * (xR + 0.1 - x_n)), (xs1 + P["d_x"], y_kr - 0.33),
              (xs1 + P["d_x"], y_kr - 0.14), (x_n, y_kr - 0.14)], "KRUSZYWO")
    return _prog_dz2_opisy(det, dict(P=P, sz=sz, pg=pg, sym=sym, o=o, xs1=xs1, x_out=x_out, xf0=xf0, xf1=xf1, xp1=xp1,
                                     y_kr=y_kr, xk0=xk0, xk1=xk1, x_n=x_n, tz=tz, z_f=z_f, tz_abs=tz_abs,
                                     xL=xL, xR=xR, yT=yT, yB=yB))


def _prog_dz2_opisy(det: Detal, g: dict) -> Detal:
    m = det.model
    P, xs1, xf0, xf1, xp1, y_kr = g["P"], g["xs1"], g["xf0"], g["xf1"], g["xp1"], g["y_kr"]
    xL, xR, yT, yB = g["xL"], g["xR"], g["yT"], g["yB"]
    y_pl = P["y_pl"]
    h_c = -g["tz"]                                                    # cokół: posadzka – teren (model)
    det.linia("H", [(xs1 + 0.003, P["y_zb"]), (xs1 + 0.003, y_pl + 0.002), (xp1 + 0.002, y_pl + 0.002),
                    (xp1 + 0.002, 0.0)], "KMB / taśma EPDM: czoło płyty → podwalina → pod profil progowy")
    det.linia("T_out", [(xp1 + 0.003, -0.02), (xp1 + 0.003, 0.003), (xf1 + 0.002, 0.003), (xf1 + 0.002, 0.04)])
    det.polaczenie("H", [(xf1, 0.003), (xf1, yT)])
    det.linia("S", [(xL, y_pl - 0.004), (xf0 - 0.0015, y_pl - 0.004)])
    det.linia("T_in", [(xf0 - 0.0015, 0.04), (xf0 - 0.0015, y_pl - 0.004)])
    for p1, p2 in (((xf0, yT), (xf1 + 0.02, yT)), ((xL, yB), (xR, yB)), ((xL, 0.0), (xL, yB)), ((xR, y_kr), (xR, yB))):
        det.przerwa(p1, p2)
    o = g["o"]
    det.opis([((xf0 + xf1) / 2, 0.25)], [f"drzwi {g['sym']} {o.szer:.2f} × {o.wys:.2f} m (garaż nieogrzewany), "
                                         "próg z uszczelką szczotkową / opadającą".replace(".", ",") if o else "drzwi"])
    det.opis([(xf1 + 0.002, 0.02)], ["taśma EPDM rama–podwalina, zakład ≥ 50 mm na KMB czoła płyty"])
    det.opis([(xp1 - 0.03, y_pl / 2)], [f"podwalina progowa XPS 300 / PUR-GF — wys. {mm(-y_pl)} mm"])
    det.opis([((g["xk0"] + g["xk1"]) / 2, y_kr - 0.03)],
             ["odwodnienie liniowe przed drzwiami na całą szerokość (+ 0,20 m z każdej strony), ruszt klasy B125, "
              f"≥ 30 mm poniżej progu, odpływ → kolektor KD-E (ZALECENIE — brak w modelu działki)"])
    det.opis([(g["x_n"] + 0.35, y_kr - 0.03 - 0.02 * 0.35)],
             ["nawierzchnia z płyt betonowych 50 mm na podsypce, spadek ≥ 2 % od budynku"])
    det.opis([(g["x_n"] + 0.55, y_kr - 0.20)], ["podbudowa z kruszywa 0/31,5 (drenująca) na geowłókninie"])
    det.opis([(xs1 + 0.003, P["y_zb"] + 0.05)], ["izolacja pionowa KMB na czole płyty (bez membrany na płycie "
                                                 "garażu — POD-G)"])
    det.opis_stosu(P["st"][:P["ki"] + 1], "x", -0.18, odwroc=True, wyjscie=(-0.18, yB - 0.03),
                   tytul=f"{g['pg']} — posadzka garażu")
    det.rzedna((xL + 0.06, 0.0), 0.0, "wyk", "right")
    det.rzedna((xR - 0.05, g["tz"]), g["tz"], "wyk", "left",
               tekst=None)
    det.wymiar([(xp1 + 0.25, g["tz"]), (xp1 + 0.25, 0.0)], xp1 + 0.27, "v")
    det.spadek((g["x_n"] + 0.10, y_kr + 0.02), (g["x_n"] + 0.30, y_kr + 0.016), 2.0)
    zr = "teren projektowany z modelu działki (TIN)" if g["tz_abs"] is not None else "teren wg energia.rzedna_terenu"
    det.uwagi.append(f"{g['sym']}: posadzka garażu {fmt_z(g['z_f'])}, {zr} {fmt_z(g['z_f'] + g['tz'])} → cokół "
                     f"{mm(h_c)} mm < 150 mm (DIN 18533-1 / 18531-5: ≥ 150 mm; redukcja do ≥ 50 mm tylko z "
                     "odwodnieniem liniowym przed drzwiami) — wymagane odwodnienie liniowe + spadek 2 % od budynku; "
                     "alternatywa: obniżenie terenu przed DZ2 o ≥ 0,10 m (niecka NT-E) — REKOMENDACJE R-W4")
    return det
