"""Katalog węzłów z modelu budynku (`lamela.model`) i długości do H_TB.

Z modelu pobierane są przegrody (warstwy, λ materiałów), grubości płyt, ławy, attyki; dane stolarki i łączników —
z `obliczenia/dane/wyroby_przykladowe.yaml` (DANE PRZYKŁADOWE); ściana garażu i rzędna terenu — założenia [ZAŁ],
gdy model ich nie definiuje. Katalog odpowiada liście węzłów z briefu (sekcja 9 pkt 2): naroża, strop pośredni,
płyty wspornikowe (łącznik termoizolacyjny + wariant porównawczy bez przerwy), attyka, ościeża (osadzenie z modelu
i „ciepły montaż”), nadproża (z kasetą osłony — gdy model ją przewiduje), podokienniki z parapetami, progi (parter
na gruncie, okna do podłogi na stropie, drzwi na płytę wspornikową), cokół, połączenie z garażem nieogrzewanym, rura
spustowa w ociepleniu. Długości do H_TB — w systemie wymiarów wewnętrznych całkowitych (ψ_oi), jak `energia.bryla`.
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


OSLONY_Z_KASETA = ("zaluzja_zewn", "screen_zip", "roleta_zewn", "roleta")   # kaseta w ociepleniu [ZAŁ: podtynkowa]


def _okno(nazwa: str = "okno_PVC_3sz") -> dict[str, Any]:
    d = {"U_f": 0.95, "b_f": 0.115, "U_g": 0.50, "psi_g": 0.0, "zrodlo": "[ZAŁ]"}
    try:
        from ..wspolne import wyrob
        w = wyrob("stolarka", nazwa)
        if w:
            d.update({k: w[k] for k in ("U_f", "b_f", "U_g", "psi_g") if k in w})
            d["zrodlo"] = f"{w.get('status', '')} {w.get('zrodlo', '')}".strip()
    except Exception:   # pragma: no cover
        pass
    return d


def _okna_param(ok: dict[str, Any], osadzenie: dict[str, float]) -> dict[str, Any]:
    return dict(U_f=ok["U_f"], b_f=ok["b_f"], U_g=ok["U_g"], psi_g=ok.get("psi_g", 0.0), d_f=osadzenie["d_f"],
                wsuniecie=osadzenie["wsuniecie"], zrodlo_okna=ok["zrodlo"])


def otwory_zewnetrzne(model) -> list:
    """Otwory (okna, drzwi, HS, fix) w ścianach o przegrodzie typu `sciana_zewn` — tylko te tworzą węzły obudowy
    cieplnej (PN-EN ISO 14683: H_TB = Σ ψ·l po węzłach obudowy). Otwory w ścianach wewnętrznych i działowych oraz
    `typ: otwor` (przejścia bez stolarki) są pomijane (weryfikacja niezależna — uwaga dot. długości WZ-W1)."""
    out = []
    for o in model.otwory():
        sc = o.sciana
        kod = getattr(sc, "przegroda_kod", None)
        try:
            p = model.przegroda(kod)
            typ = p.typ if hasattr(p, "typ") else p.get("typ")
        except Exception:   # pragma: no cover
            typ = None
        if typ == "sciana_zewn" and o.typ != "otwor":
            out.append(o)
    return out


def osadzenie_z_modelu(model, kod_sz: str) -> dict[str, float]:
    """Położenie ramy w grubości ściany z modelu (`Otwor.rama_t` — pierwszy otwór ściany zewn.): głębokość ramy d_f
    i wsunięcie w mur (od lica zewn. warstwy konstrukcyjnej do lica wewn. ramy). Brak danych → 0,082 m / 0,05 m."""
    out = {"d_f": 0.082, "wsuniecie": 0.05, "zrodlo": "[ZAŁ] (brak rama_t w modelu)"}
    for o in otwory_zewnetrzne(model):
        rt = getattr(o, "rama_t", None)
        sc = o.sciana
        if not rt or sc is None or getattr(sc, "przegroda_kod", None) != kod_sz:
            continue
        ws = [w for w in sc.warstwy if getattr(w, "konstrukcyjna", False)]
        if not ws:
            continue
        t0, t1 = min(ws[0].t0, ws[0].t1), max(ws[0].t0, ws[0].t1)
        ext = getattr(sc, "ext_side", -1)
        if ext < 0:
            ws_ = max(rt) - t0
        else:
            ws_ = t1 - min(rt)
        out = {"d_f": round(abs(rt[1] - rt[0]), 4), "wsuniecie": round(ws_, 4),
               "zrodlo": f"model: Otwor.rama_t otworu {o.id} (rama {abs(rt[1] - rt[0]) * 100:.1f} cm, "
                         f"{ws_ * 100:.1f} cm w murze)"}
        break
    return out


def B_prim(model) -> tuple[float, str]:
    """Wymiar charakterystyczny podłogi B' = A/(0,5·P) (PN-EN ISO 13370) z obrysu zewnętrznego parteru [INT]."""
    obr = model.obrys_kondygnacji(model.kondygnacje[0].id, lico="zewn")
    A, P = float(obr.area), float(obr.length)
    return A / (0.5 * P), f"B' = A/(0,5·P) = {A:.2f}/(0,5·{P:.2f}) = {A / (0.5 * P):.2f} m (obrys zewn. parteru) [INT]"


def _nad_wspornikiem(model, o) -> bool:
    from shapely.geometry import Point, Polygon
    pt = Point(o.srodek[0], o.srodek[1]) if getattr(o, "srodek", None) is not None else None
    if pt is None:
        return False
    for wsp in model.wsporniki():
        if Polygon(wsp["obrys"]).distance(pt) < 0.6:
            return True
    return False


def katalog_z_modelu(model, sciana: str | None = None, y_teren: float = -0.30,
                     warstwy_sciany_garazu: list[G.Warstwa] | None = None, b: float | None = None) -> list[G.Wezel]:
    """Węzły typowe dla przegród modelu. Zwraca listę `Wezel` (id WZ-…). b — szerokość do modelu gruntu i B' w
    PN-EN ISO 13370 (domyślnie B' = A/(0,5·P) z modelu)."""
    kod_sz = sciana or _pierwsza_przegroda(model, "sciana_zewn")
    sz = G.warstwy_z_modelu(model, kod_sz)
    out: list[G.Wezel] = [G.wezel_naroznik_zewnetrzny(sz, id="WZ-C1")]
    zb_kod = "ZB_C30" if "ZB_C30" in model.materialy else None
    osad = osadzenie_z_modelu(model, kod_sz)
    ok = _okno()
    okp = _okna_param(ok, osad)
    otw = otwory_zewnetrzne(model)
    # strop pośredni + wspornik
    stropy = model.stropy()
    st = stropy[0] if stropy else None
    pod = suf = []
    mat = G.MATERIALY_DOMYSLNE["ZB"]
    if st:
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
    # krawędzie otworów: ościeża (boki), nadproża, podokienniki, progi
    polozenie = "czesciowo" if osad["wsuniecie"] > 1e-6 else "w_izolacji"
    kw = {k: v for k, v in okp.items() if k != "wsuniecie"}
    out.append(G.wezel_oscieze_okna(sz, polozenie=polozenie, wsuniecie=osad["wsuniecie"], id="WZ-W1", **kw,
                                    nazwa=f"Ościeże okna — osadzenie wg modelu ({osad['zrodlo']})"))
    out.append(G.wezel_oscieze_okna(sz, polozenie="w_izolacji", id="WZ-W2", **kw,
                                    nazwa="Ościeże okna — ciepły montaż w warstwie izolacji (wariant zalecany)"))
    out.append(G.wezel_nadproze(sz, polozenie=polozenie, wsuniecie=osad["wsuniecie"], id="WZ-N1", **kw))
    if any(getattr(o, "oslona", None) in OSLONY_Z_KASETA for o in otw):
        out.append(G.wezel_nadproze(sz, polozenie=polozenie, wsuniecie=osad["wsuniecie"], kaseta=(0.20, 0.15),
                                    id="WZ-N2", **kw))
    if any((o.parapet or 0.0) > 0.05 for o in otw):
        out.append(G.wezel_podokiennik(sz, polozenie=polozenie, wsuniecie=osad["wsuniecie"], id="WZ-P1", **kw))
    kp = model.kondygnacje[0].podloga
    k0 = model.kondygnacje[0].id
    progi = [o for o in otw if (o.parapet or 0.0) <= 0.05]
    ok_hs = _okno("HS_ALU_3sz")
    prog_par = {"U_f": ok_hs["U_f"], "b_f": ok_hs["b_f"], "U_g": ok_hs["U_g"], "psi_g": ok_hs.get("psi_g", 0.0),
                "d_f": osad["d_f"], "wsuniecie": osad["wsuniecie"], "zrodlo": ok_hs["zrodlo"]}
    B, _ = B_prim(model)
    b_ = b if b is not None else B
    # cokół (+ próg na gruncie)
    if kp:
        fund = model.fundamenty() or {}
        el = (fund.get("elementy") or [{}])[0]
        kw_c: dict[str, Any] = {"y_teren": y_teren, "b": b_}
        if fund.get("typ") == "plyta":
            kw_c["fundament"] = "plyta"
        else:
            kw_c.update(fundament="lawa", lawa=(el.get("b", 0.60), el.get("h", 0.30), el.get("spod", -1.10)))
        out.append(G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), id="WZ-GF1", **kw_c))
        if any(o.kond == k0 for o in progi):
            out.append(G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), id="WZ-T1", prog=prog_par, **kw_c))
    if st and any(o.kond != k0 and not _nad_wspornikiem(model, o) for o in progi):
        out.append(G.wezel_prog_strop(sz, st["grubosc"], mat, pod, suf, wysieg=0.0, prog=prog_par, id="WZ-T2"))
    if st and any(o.kond != k0 and _nad_wspornikiem(model, o) for o in progi):
        wsp = model.wsporniki()[0]
        lac = G.LACZNIK_PRZYKLAD if wsp.get("lacznik_termiczny") else None
        out.append(G.wezel_prog_strop(sz, wsp.get("grubosc", st["grubosc"]), mat, pod, suf, wysieg=1.0, lacznik=lac,
                                      prog=prog_par, id="WZ-T3"))
    # garaż
    wg = warstwy_sciany_garazu or [G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015),
                                   G.Warstwa(G.MATERIALY_DOMYSLNE["SIL24"], 0.24, True),
                                   G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015)]
    out.append(G.wezel_garaz(sz, wg, przerwa_izolacji=False, id="WZ-G1"))
    out.append(G.wezel_garaz(sz, wg, przerwa_izolacji=True, id="WZ-G2"))
    # rura spustowa
    out.append(G.wezel_rura_spustowa(sz, id="WZ-RS1"))
    return out


def _obrys_wewn(model, kond_id: str, D: float):
    """Obrys po licach wewnętrznych ścian zewnętrznych ≈ obrys zewn. pomniejszony o grubość ściany (mitre) [INT]."""
    obr = model.obrys_kondygnacji(kond_id, lico="zewn")
    return obr.buffer(-D, join_style=2)


def dlugosci_z_modelu(model, sciana: str | None = None) -> tuple[dict[str, float], list[str]]:
    """Długości węzłów do H_TB w systemie WEWNĘTRZNYM CAŁKOWITYM (zgodnym z ψ_oi i `energia.bryla`) [INT]
    + opis sposobu liczenia. Otwory — tylko w ścianach zewnętrznych, wymiary w świetle otworu (szer × wys):
    ościeża boczne 2·wys, nadproża szer (z kasetą osłony: WZ-N2), podokienniki szer (parapet > 5 cm), progi szer
    (parter: WZ-T1; wyżej: na stropie WZ-T2, na płycie wspornikowej WZ-T3)."""
    uw = []
    d: dict[str, float] = {}
    kod_sz = sciana or _pierwsza_przegroda(model, "sciana_zewn")
    D = G.grubosc(G.warstwy_z_modelu(model, kod_sz))
    k0 = model.kondygnacje[0]
    obr = model.obrys_kondygnacji(k0.id, lico="zewn")
    # wysokość wewnętrzna całkowita: od poziomu posadzki parteru do spodu płyty dachu
    dachy = model.dachy()
    h = sum(k.wys_kondygnacji for k in model.kondygnacje)
    if dachy:
        dd = dachy[0]
        h = dd["plyta"]["wierzch"] - dd["plyta"]["grubosc"] - k0.rzedna
    naroza = sum(1 for _ in _naroza_wypukle(obr))
    d["WZ-C1"] = naroza * h
    uw.append(f"WZ-C1: {naroza} naroży wypukłych × h_oi = {h:.2f} m (posadzka parteru → spód płyty dachu)")
    otw = otwory_zewnetrzne(model)
    progi = [o for o in otw if (o.parapet or 0.0) <= 0.05]
    l_T1 = sum(o.szer for o in progi if o.kond == k0.id)
    l_T3 = sum(o.szer for o in progi if o.kond != k0.id and _nad_wspornikiem(model, o))
    l_T2 = sum(o.szer for o in progi if o.kond != k0.id and not _nad_wspornikiem(model, o))
    wsp_l = 0.0
    for wsp in model.wsporniki():
        from shapely.geometry import Polygon
        wsp_l += float(Polygon(wsp["obrys"]).intersection(obr.exterior).length)
    if model.wsporniki():
        d["WZ-B1"] = max(0.0, wsp_l - l_T3)
        uw.append(f"WZ-B1: styk płyt wspornikowych z elewacją ≈ {wsp_l:.2f} m − progi na płycie {l_T3:.2f} m")
    if model.stropy():
        obw_i = 0.0
        for st in model.stropy():
            nad = [k for k in model.kondygnacje if k.rzedna > model.kondygnacja(st["nad"]).rzedna]
            kid = nad[0].id if nad else st["nad"]
            obw_i += float(_obrys_wewn(model, kid, D).length)
        d["WZ-IF1"] = max(0.0, obw_i - wsp_l - l_T2)
        uw.append(f"WZ-IF1: obwód po licach wewn. {obw_i:.2f} m − wsporniki {wsp_l:.2f} m − progi okien do podłogi "
                  f"{l_T2:.2f} m")
    if dachy:
        kt = model.kondygnacje[-1].id
        d["WZ-R1"] = float(_obrys_wewn(model, kt, D).length)
        uw.append(f"WZ-R1: obwód po licach wewn. kondygnacji {kt} {d['WZ-R1']:.2f} m")
    d["WZ-GF1"] = max(0.0, float(_obrys_wewn(model, k0.id, D).length) - l_T1)
    uw.append(f"WZ-GF1: obwód po licach wewn. parteru − progi {l_T1:.2f} m")
    l_bok = sum(2 * o.wys for o in otw)
    l_N1 = sum(o.szer for o in otw if getattr(o, "oslona", None) not in OSLONY_Z_KASETA)
    l_N2 = sum(o.szer for o in otw if getattr(o, "oslona", None) in OSLONY_Z_KASETA)
    l_P1 = sum(o.szer for o in otw if (o.parapet or 0.0) > 0.05)
    d["WZ-W1"] = l_bok
    d["WZ-N1"] = l_N1
    if l_N2:
        d["WZ-N2"] = l_N2
    if l_P1:
        d["WZ-P1"] = l_P1
    for k_, v in (("WZ-T1", l_T1), ("WZ-T2", l_T2), ("WZ-T3", l_T3)):
        if v:
            d[k_] = v
    uw.append(f"otwory w ścianach zewn. ({len(otw)} szt.; pominięto otwory w ścianach wewn./działowych): ościeża "
              f"boczne WZ-W1 {l_bok:.2f} m, nadproża WZ-N1 {l_N1:.2f} m, z kasetą osłony WZ-N2 {l_N2:.2f} m, "
              f"podokienniki WZ-P1 {l_P1:.2f} m, progi WZ-T1/T2/T3 {l_T1:.2f}/{l_T2:.2f}/{l_T3:.2f} m")
    uw.append("WZ-RS1 (rura spustowa we wnęce ETICS): brak w modelu (odwodnienie dachu wpustem wewnętrznym / rury "
              "przed licem elewacji) — l = 0")
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
