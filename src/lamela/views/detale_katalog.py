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
    det = Detal(m, "D-01", "Cokół — ściana na płycie fundamentowej", ("WZ-08",), 10)
    sz = przegroda_typu(m, "WZ-08", "sciana_zewn", "SZ1")
    pd = przegroda_typu(m, "WZ-08", "podloga_na_gruncie", "POD-0")
    f = fundament_pod(m)
    tz = teren(m)
    y_cok = tz + 0.30                                      # górna krawędź strefy cokołowej (≥ 30 cm nad terenem)
    xL, xR, yT, yB = -0.30, 0.72, 0.50, -1.05
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
                 xL: float, yB: float, y_sr: float) -> dict:
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
    det.linia("H", [(xL, y_memb), (x_iw - 0.002, y_memb), (x_iw - 0.002, y_cap + 0.002), (x_out + 0.002, y_cap + 0.002),
                    (x_out + 0.002, y_cap - 0.05)], "hydroizolacja wywinięta na attykę i koronę")
    y_par = next(((a + b) / 2 for a, b, w in stos if w["funkcja"] == "paroizolacja"), 0.002)
    det.linia("P", [(xL, y_par), (x_iw - 0.002, y_par), (x_iw - 0.002, y_top + 0.05)],
              "paroizolacja wywinięta na attykę ponad izolację dachu")
    det.linia("S", [(0.0015, yB), (0.0015, -t - suf - 0.002), (xL, -t - suf - 0.002)])
    rz = 0.05 * (x_out + 0.035 - (x_iw - 0.03))
    det.obrobka([(x_iw - 0.03, y_cap - 0.07), (x_iw - 0.03, y_cap + 0.006), (x_out + 0.035, y_cap + 0.006 + rz),
                 (x_out + 0.035, y_cap - 0.05)], strona=1)
    return dict(sc=sc, xs0=xs0, xs1=xs1, x_out=x_out, t=t, y_top=y_top, y_cap=y_cap, y_p=y_p, x_iw=x_iw,
                stos=stos, memb=memb, y_memb=y_memb, iw=iw)
