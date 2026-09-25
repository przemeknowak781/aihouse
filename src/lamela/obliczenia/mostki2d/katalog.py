"""Katalog węzłów z modelu budynku (`lamela.model`) i długości do H_TB.

Z modelu pobierane są przegrody (warstwy, λ materiałów), grubości płyt, ławy, attyki; dane stolarki i łączników —
z `obliczenia/dane/wyroby_przykladowe.yaml` (DANE PRZYKŁADOWE); ściana garażu i rzędna terenu — założenia [ZAŁ],
gdy model ich nie definiuje. Katalog odpowiada liście węzłów z briefu (sekcja 9 pkt 2): naroża, strop pośredni,
płyty wspornikowe (łącznik termoizolacyjny + wariant porównawczy bez przerwy), attyka, ościeża (osadzenie z modelu
i „ciepły montaż”), cokół, połączenie z garażem nieogrzewanym, rura spustowa w ociepleniu.
"""
from __future__ import annotations

from typing import Any

from . import geometria as G


def _pierwsza_przegroda(model, typ: str) -> str | None:
    for kod, p in getattr(model, "przegrody", {}).items():
        t = p.typ if hasattr(p, "typ") else p.get("typ")
        if t == typ:
            return kod
    return None


def _sufit(model, kod: str | None) -> list[G.Warstwa]:
    if not kod:
        return []
    if kod in getattr(model, "przegrody", {}):
        return G.warstwy_z_modelu(model, kod)
    return [G.Warstwa(G.material_z_modelu(model, kod), 0.01)]


def _okno(nazwa: str = "okno_PVC_3sz") -> dict[str, Any]:
    d = {"U_f": 0.95, "b_f": 0.115, "U_g": 0.50, "zrodlo": "[ZAŁ]"}
    try:
        from ..wspolne import wyrob
        w = wyrob("stolarka", nazwa)
        if w:
            d.update({k: w[k] for k in ("U_f", "b_f", "U_g") if k in w})
            d["zrodlo"] = f"{w.get('status', '')} {w.get('zrodlo', '')}".strip()
    except Exception:   # pragma: no cover
        pass
    return d


def katalog_z_modelu(model, sciana: str | None = None, y_teren: float = -0.30,
                     warstwy_sciany_garazu: list[G.Warstwa] | None = None) -> list[G.Wezel]:
    """Węzły typowe dla przegród modelu. Zwraca listę `Wezel` (id WZ-…)."""
    kod_sz = sciana or _pierwsza_przegroda(model, "sciana_zewn")
    sz = G.warstwy_z_modelu(model, kod_sz)
    out: list[G.Wezel] = [G.wezel_naroznik_zewnetrzny(sz, id="WZ-C1")]
    zb_kod = "ZB_C30" if "ZB_C30" in model.materialy else None
    # strop pośredni + wspornik
    stropy = model.stropy()
    if stropy:
        st = stropy[0]
        pod = G.warstwy_z_modelu(model, st["podloga"]) if st.get("podloga") else []
        suf = _sufit(model, st.get("sufit"))
        mat = G.material_z_modelu(model, st.get("mat") or zb_kod) if (st.get("mat") or zb_kod) else G.MATERIALY_DOMYSLNE["ZB"]
        out.append(G.wezel_wspornik(sz, st["grubosc"], mat, pod, suf, wysieg=0.0, id="WZ-IF1",
                                    nazwa=f"Strop pośredni {st['id']} z wieńcem (ETICS ciągły)"))
        for k, wsp in enumerate(model.wsporniki()):
            xs = [p[0] for p in wsp["obrys"]]
            ys = [p[1] for p in wsp["obrys"]]
            wys = min(1.5, max(0.5, min(max(xs) - min(xs), max(ys) - min(ys))))
            tp = wsp.get("grubosc", st["grubosc"])
            lac = G.LACZNIK_PRZYKLAD if wsp.get("lacznik_termiczny") else None
            out.append(G.wezel_wspornik(sz, tp, mat, pod, suf, wysieg=wys, lacznik=lac, id=f"WZ-B{k + 1}",
                                        nazwa=f"Płyta wspornikowa {wsp['id']} — " +
                                              ("łącznik termoizolacyjny" if lac else "płyta ciągła")))
            if lac is not None and k == 0:
                out.append(G.wezel_wspornik(sz, tp, mat, pod, suf, wysieg=wys, lacznik=None, id="WZ-B0",
                                            nazwa=f"Płyta wspornikowa {wsp['id']} — WARIANT PORÓWNAWCZY bez łącznika"))
    # attyka
    for k, d in enumerate(model.dachy()[:1]):
        att = d.get("attyka") or {}
        out.append(G.wezel_attyka(sz, G.warstwy_z_modelu(model, d["przegroda"]),
                                  h_nad_pokryciem=att.get("wys_nad_pokryciem", 0.30), id=f"WZ-R{k + 1}",
                                  nazwa=f"Attyka dachu {d['id']}"))
    # ościeża
    ok = _okno()
    out.append(G.wezel_oscieze_okna(sz, U_f=ok["U_f"], b_f=ok["b_f"], U_g=ok["U_g"], polozenie="czesciowo",
                                    wsuniecie=0.05, id="WZ-W1", zrodlo_okna=ok["zrodlo"],
                                    nazwa="Ościeże okna — osadzenie wg modelu (5 cm w murze, 4 cm w izolacji)"))
    out.append(G.wezel_oscieze_okna(sz, U_f=ok["U_f"], b_f=ok["b_f"], U_g=ok["U_g"], polozenie="w_izolacji",
                                    id="WZ-W2", zrodlo_okna=ok["zrodlo"],
                                    nazwa="Ościeże okna — ciepły montaż w warstwie izolacji (wariant zalecany)"))
    # cokół
    kp = model.kondygnacje[0].podloga
    if kp:
        fund = model.fundamenty() or {}
        el = (fund.get("elementy") or [{}])[0]
        if fund.get("typ") == "plyta":
            out.append(G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), fundament="plyta", y_teren=y_teren,
                                     id="WZ-GF1"))
        else:
            lawa = (el.get("b", 0.60), el.get("h", 0.30), el.get("spod", -1.10))
            out.append(G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), fundament="lawa", lawa=lawa,
                                     y_teren=y_teren, id="WZ-GF1"))
    # garaż
    wg = warstwy_sciany_garazu or [G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015),
                                   G.Warstwa(G.MATERIALY_DOMYSLNE["SIL24"], 0.24, True),
                                   G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015)]
    out.append(G.wezel_garaz(sz, wg, przerwa_izolacji=False, id="WZ-G1"))
    out.append(G.wezel_garaz(sz, wg, przerwa_izolacji=True, id="WZ-G2"))
    # rura spustowa
    out.append(G.wezel_rura_spustowa(sz, id="WZ-RS1"))
    return out


def dlugosci_z_modelu(model) -> tuple[dict[str, float], list[str]]:
    """Przybliżone długości węzłów do H_TB (wymiary zewnętrzne) [INT] + opis sposobu liczenia."""
    uw = []
    d: dict[str, float] = {}
    obr = model.obrys_kondygnacji(model.kondygnacje[0].id, lico="zewn")
    obw = float(obr.length)
    # wysokość zewnętrzna: od posadzki parteru do wierzchu dachu (płyta + warstwy nad nią)
    dachy = model.dachy()
    h = sum(k.wys_kondygnacji for k in model.kondygnacje)
    if dachy:
        dd = dachy[0]
        w = G.warstwy_z_modelu(model, dd["przegroda"])
        kd = G.indeks_konstrukcyjnej(w)
        h = dd["plyta"]["wierzch"] + G.grubosc(w[:kd])
    naroza = sum(1 for _ in _naroza_wypukle(obr))
    d["WZ-C1"] = naroza * h
    uw.append(f"WZ-C1: {naroza} naroży wypukłych × h = {h:.2f} m (posadzka parteru → wierzch dachu)")
    wsp_l = 0.0
    for wsp in model.wsporniki():
        from shapely.geometry import Polygon
        wsp_l += float(Polygon(wsp["obrys"]).intersection(obr.exterior).length)
    if model.wsporniki():
        d["WZ-B1"] = wsp_l
        uw.append(f"WZ-B1: styk płyt wspornikowych z elewacją ≈ {wsp_l:.2f} m")
    if model.stropy():
        d["WZ-IF1"] = max(0.0, obw * max(1, len(model.stropy())) - wsp_l)
        uw.append(f"WZ-IF1: obwód zewn. {obw:.2f} m × liczba stropów − długość wsporników")
    if dachy:
        from shapely.geometry import Polygon
        d["WZ-R1"] = float(Polygon(dachy[0]["obrys"]).length)
        uw.append(f"WZ-R1: obwód dachu {d['WZ-R1']:.2f} m")
    lw = 0.0
    for o in model.otwory():
        lw += 2 * (o.szer + o.wys) if o.typ not in ("drzwi_przesuwne_HS", "drzwi_zewn") else (2 * o.wys + o.szer)
    d["WZ-W1"] = lw
    uw.append(f"WZ-W1: obwody otworów (drzwi bez progu) {lw:.2f} m — nadproża i podokienniki przyjęto jak ościeże [INT]")
    d["WZ-GF1"] = obw
    uw.append(f"WZ-GF1: obwód zewn. parteru {obw:.2f} m")
    return d, uw


def _naroza_wypukle(poly):
    import numpy as np
    c = np.asarray(poly.exterior.coords)[:-1]
    n = len(c)
    ccw = poly.exterior.is_ccw
    for k in range(n):
        a, b, e = c[k - 1], c[k], c[(k + 1) % n]
        cr = (b[0] - a[0]) * (e[1] - b[1]) - (b[1] - a[1]) * (e[0] - b[0])
        if abs(cr) < 1e-9:
            continue
        if (cr > 0) == ccw:
            yield b
