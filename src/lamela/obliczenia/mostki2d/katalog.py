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


# --------------------------------------------------------------------------------------------------
# Katalog demonstracyjny (warianty porównawcze) i katalog z sekcji `wezly` modelu
# --------------------------------------------------------------------------------------------------
# kolejność i warianty katalogu demonstracyjnego: węzły wymagane (brief 9.2) + warianty porównawcze
KOLEJNOSC_DEMO = ["WZ-R1", "WZ-B0", "WZ-B1", "WZ-W0", "WZ-W2", "WZ-W1", "WZ-N1", "WZ-N2", "WZ-P1", "WZ-GF2",
                  "WZ-GF1", "WZ-GF1B", "WZ-C1", "WZ-G1", "WZ-G2", "WZ-RS1", "WZ-IF1", "WZ-T1", "WZ-T2", "WZ-T3"]
# pary/grupy do porównań w raporcie: (tytuł, [id], komentarz)
POROWNANIA_DEMO = [
    ("Płyta wspornikowa: bez łącznika vs z łącznikiem termoizolacyjnym", ["WZ-B0", "WZ-B1"],
     "łącznik przerywa płytę w płaszczyźnie izolacji — linia izolacji ciągła, ψ spada kilkukrotnie"),
    ("Ościeże okna: montaż w murze vs „ciepły montaż” w warstwie izolacji", ["WZ-W0", "WZ-W1", "WZ-W2"],
     "porównywać ψ_e (ψ montażu, okno po ramie); ψ_oi zawiera korektę U_w·x0 (okno w świetle otworu w murze). We "
     "wszystkich wariantach izolacja ościeża zachodzi na ramę 3 cm — bez zakładu ψ_e montażu w murze rośnie ok. "
     "dwukrotnie (0,030 → 0,067 W/(m·K) dla okna domyślnego). f_Rsi wszystkich wariantów ≫ 0,72"),
    ("Cokół: płyta fundamentowa vs ława (z gruntem), blok termiczny", ["WZ-GF2", "WZ-GF1", "WZ-GF1B"],
     "przy ławie linia izolacji domyka się przez mur fundamentowy i grunt; blok termiczny u podstawy muru ją zamyka"),
    ("Dom – garaż nieogrzewany: izolacja ciągła vs ściana garażu w ociepleniu", ["WZ-G1", "WZ-G2"],
     "ściana garażu dochodząca do muru domu przerywa ETICS"),
]


def _warstwy_plyty_fundamentowej(model, kod_pod: str | None) -> list[G.Warstwa]:
    """Warstwy „ciepłej” płyty fundamentowej [ZAŁ]: wykończenie i jastrych z podłogi modelu, płyta ŻB 0,25 m,
    XPS 0,20 m pod płytą (izolacja nośna), podsypka 0,15 m — gdy model nie ma przegrody płyty fundamentowej."""
    mats = getattr(model, "materialy", {})
    w: list[G.Warstwa] = []
    if kod_pod:
        for x in G.warstwy_z_modelu(model, kod_pod):
            if x.konstrukcyjna:
                break
            if x.mat.lam > 0.1:          # wykończenia (bez izolacji nad płytą)
                w.append(x)
    zb = G.material_z_modelu(model, "ZB_C30") if "ZB_C30" in mats else G.MATERIALY_DOMYSLNE["ZB"]
    xps = G.material_z_modelu(model, "XPS300") if "XPS300" in mats else G.MATERIALY_DOMYSLNE["XPS"]
    pias = G.material_z_modelu(model, "PIASEK") if "PIASEK" in mats else G.MATERIALY_DOMYSLNE["GRUNT"]
    return w + [G.Warstwa(zb, 0.25, True), G.Warstwa(xps, 0.20), G.Warstwa(pias, 0.15)]


def katalog_demonstracyjny(model, y_teren: float = -0.30) -> list[G.Wezel]:
    """Katalog demonstracyjny: węzły z `katalog_z_modelu` + warianty porównawcze: ościeże „w murze” (WZ-W0), cokół
    na płycie fundamentowej (WZ-GF2 — gdy model ma ławy) albo na ławie (WZ-GF1 — gdy płytę), cokół z blokiem
    termicznym (WZ-GF1B); płyta wspornikowa bez łącznika (WZ-B0) — z `katalog_z_modelu`, gdy model ma łącznik. Kolejność: `KOLEJNOSC_DEMO`."""
    wz = {w.id: w for w in katalog_z_modelu(model, y_teren=y_teren)}
    kod_sz = _pierwsza_przegroda(model, "sciana_zewn")
    sz = G.warstwy_z_modelu(model, kod_sz)
    osad = osadzenie_z_modelu(model, kod_sz)
    okp = {k: v for k, v in _okna_param(_okno(), osad).items() if k != "wsuniecie"}
    wz["WZ-W0"] = G.wezel_oscieze_okna(sz, polozenie="w_murze", id="WZ-W0", **okp,
                                       nazwa="Ościeże okna — montaż w murze (rama w licu zewn. muru, izolacja z zakładem 3 cm)")
    kp = _pierwsza_przegroda(model, "podloga_na_gruncie")
    B, _ = B_prim(model)
    fund = model.fundamenty() or {}
    el = (fund.get("elementy") or [{}])[0]
    lawa = (el.get("b", 0.60), el.get("h", 0.30), el.get("spod", -1.10))
    if kp:
        if fund.get("typ") == "plyta":
            wz.setdefault("WZ-GF2", wz.pop("WZ-GF1", None))
            wz["WZ-GF1"] = G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), fundament="lawa", lawa=lawa, b=B,
                                         y_teren=y_teren, id="WZ-GF1",
                                         nazwa="Cokół — ściana / podłoga na gruncie / ława (wariant porównawczy)")
        else:
            wz["WZ-GF2"] = G.wezel_cokol(sz, _warstwy_plyty_fundamentowej(model, kp), fundament="plyta", b=B,
                                         y_teren=y_teren, id="WZ-GF2",
                                         nazwa="Cokół — płyta fundamentowa na XPS (wariant porównawczy) [ZAŁ]")
            wz["WZ-GF2"].dane["warstwy podłogi — źródło"] = (
                "[ZAŁ] wariant porównawczy: wykończenie z przegrody " + kp + ", płyta ŻB 0,25 m na XPS 0,20 m "
                "(hydroizolacja pod płytą na XPS — na detalu)")
        wz["WZ-GF1B"] = G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), fundament="lawa", lawa=lawa, b=B,
                                      y_teren=y_teren, id="WZ-GF1B",
                                      blok_termiczny=(G.MATERIALY_DOMYSLNE["BET_KOM_400"], 0.24),
                                      nazwa="Cokół — ława + blok termiczny (beton komórkowy 400) w 1. warstwie muru")
    out = [wz[k] for k in KOLEJNOSC_DEMO if wz.get(k) is not None]
    out += [w for k, w in wz.items() if k not in KOLEJNOSC_DEMO and w is not None]
    return out


ALIASY_WEZLOW = {  # typ z sekcji `wezly` (także aliasy fizyka.mostki / PSI_DOMYSLNE_14683) → budowniczy
    "attyka": "attyka", "R_attyka": "attyka",
    "naroznik_wypukly": "naroze", "naroze": "naroze", "naroznik": "naroze", "C_naroze_zewn": "naroze",
    "strop_posredni": "strop", "IF_strop": "strop",
    "plyta_wspornikowa": "wspornik_bez", "B_balkon": "wspornik_bez",
    "plyta_wspornikowa_lacznik": "wspornik", "wspornik": "wspornik",
    "oscieze": "oscieze", "W_oscieze": "oscieze", "nadproze": "nadproze", "podokiennik": "podokiennik",
    "sciana_grunt": "cokol", "cokol": "cokol", "GF_cokol": "cokol",
    "polaczenie_nieogrz": "garaz", "garaz": "garaz",
    "rura_spustowa": "rura_spustowa", "prog": "prog",
}


def wezly_z_sekcji(model, y_teren: float = -0.30) -> tuple[list[G.Wezel], dict[str, float], list[str],
                                                              dict[str, list[str]]]:
    """Węzły z sekcji `wezly` modelu (`docs/SCHEMAT_MODELU.md` p. 6–7): {id, nazwa, typ, przegrody, dlugosc|liczba,
    wariant (prog: grunt|strop|wspornik; oscieze: w_izolacji|w_murze|czesciowo), parametry (skalary → argumenty
    budowniczego)}. Zwraca (węzły, długości z modelu, pominięte [opis], przegrody węzłów {id: [kody]})."""
    wpisy = model.raw.get("wezly") if isinstance(getattr(model, "raw", None), dict) else None
    if not isinstance(wpisy, list):
        return [], {}, ["brak sekcji `wezly` w modelu"], {}
    przeg = getattr(model, "przegrody", {})

    def typ_p(k):
        p = przeg.get(k)
        return None if p is None else (p.typ if hasattr(p, "typ") else p.get("typ"))

    def pierwsza(kody, *typy):
        for k in kody:
            if typ_p(k) in typy:
                return k
        for t in typy:
            k = _pierwsza_przegroda(model, t)
            if k:
                return k
        return None

    B, _ = B_prim(model)
    st = (model.stropy() or [None])[0]
    zb = "ZB_C30" if "ZB_C30" in model.materialy else None
    mat = (G.material_z_modelu(model, st.get("mat") or zb) if st and (st.get("mat") or zb)
           else G.MATERIALY_DOMYSLNE["ZB"])
    pod = G.warstwy_z_modelu(model, st["podloga"]) if st and st.get("podloga") else []
    suf = _sufit(model, st.get("sufit")) if st else []
    out, dl, pom, kody_w = [], {}, [], {}
    for e in wpisy:
        wid, typ = str(e.get("id")), str(e.get("typ", ""))
        rodz = ALIASY_WEZLOW.get(typ)
        kody = [str(k) for k in (e.get("przegrody") or [])]
        par = {k: v for k, v in (e.get("parametry") or {}).items() if isinstance(v, (int, float, str, bool))}
        nz = e.get("nazwa")
        # węzły budowane z geometrii modelu (katalog_dod: wsporniki, strop nad powietrzem, garaż) — podwęzły a, b, …
        try:
            from .katalog_dod import zbuduj
            dod = zbuduj(model, e, y_teren=y_teren)
        except ValueError as ex:
            pom.append(f"{wid}: nie zbudowano węzła z geometrii modelu ({ex}) — obsługa ogólna")
            dod = None
        if dod:
            L_geo = sum(L for _w, L in dod) or 1.0
            for w, L in dod:
                out.append(w)
                kody_w[w.id] = kody
                w.dane["długość z geometrii modelu [m]"] = round(L, 2)
                if e.get("dlugosc") is not None:     # długość wpisu modelu dzielona proporcjonalnie do geometrii
                    dl[w.id] = round(float(e["dlugosc"]) * L / L_geo, 3)
            continue
        if rodz is None:
            pom.append(f"{wid}: typ „{typ}” nieobsługiwany w modelu 2D (mostek punktowy χ / węzeł 3D) — pominięty")
            continue
        kod_sz = pierwsza(kody, "sciana_zewn")
        if kod_sz is None:
            pom.append(f"{wid}: brak przegrody typu sciana_zewn — pominięty")
            continue
        sz = G.warstwy_z_modelu(model, kod_sz)
        osad = osadzenie_z_modelu(model, kod_sz)
        okp = {k: v for k, v in _okna_param(_okno(), osad).items() if k != "wsuniecie"}
        pol = e.get("wariant") or ("czesciowo" if osad["wsuniecie"] > 1e-6 else "w_izolacji")
        kw = dict(id=wid, **({"nazwa": nz} if nz else {}))
        try:
            if rodz == "attyka":
                kod_d = pierwsza(kody, "stropodach", "dach")
                d = next((x for x in model.dachy() if x.get("przegroda") == kod_d), (model.dachy() or [{}])[0])
                att = d.get("attyka") or {}
                from .katalog_dod import blok_attyki_z_modelu
                w = G.wezel_attyka(sz, G.warstwy_z_modelu(model, kod_d),
                                   h_nad_pokryciem=par.pop("h_nad_pokryciem", att.get("wys_nad_pokryciem", 0.30)),
                                   blok_attyki=blok_attyki_z_modelu(att), **par, **kw)
            elif rodz == "naroze":
                w = G.wezel_naroznik_zewnetrzny(sz, **par, **kw)
            elif rodz in ("strop", "wspornik", "wspornik_bez"):
                if st is None:
                    raise ValueError("brak stropu w modelu")
                wsp = (model.wsporniki() or [{}])[0]
                wys = 0.0 if rodz == "strop" else float(par.pop("wysieg", 1.5))
                lac = None if rodz != "wspornik" else G.LACZNIK_PRZYKLAD
                w = G.wezel_wspornik(sz, float(wsp.get("grubosc", st["grubosc"])) if wys else st["grubosc"], mat,
                                     pod, suf, wysieg=wys, lacznik=lac, **par, **kw)
            elif rodz in ("oscieze", "nadproze", "podokiennik"):
                f = {"oscieze": G.wezel_oscieze_okna, "nadproze": G.wezel_nadproze,
                     "podokiennik": G.wezel_podokiennik}[rodz]
                w = f(sz, polozenie=pol, wsuniecie=osad["wsuniecie"], **okp, **par, **kw)
            elif rodz in ("cokol", "prog"):
                wariant = e.get("wariant") or "grunt"
                kp = pierwsza(kody, "podloga_na_gruncie")
                fund = model.fundamenty() or {}
                el = (fund.get("elementy") or [{}])[0]
                kw_c: dict[str, Any] = {"y_teren": float(par.pop("y_teren", y_teren)), "b": B}
                if fund.get("typ") == "plyta":
                    kw_c["fundament"] = "plyta"
                else:
                    kw_c.update(fundament="lawa", lawa=(el.get("b", 0.60), el.get("h", 0.30), el.get("spod", -1.10)))
                ok_hs = _okno("HS_ALU_3sz")
                prog = {"U_f": ok_hs["U_f"], "b_f": ok_hs["b_f"], "U_g": ok_hs["U_g"], "d_f": osad["d_f"],
                        "wsuniecie": osad["wsuniecie"], "zrodlo": ok_hs["zrodlo"]}
                if rodz == "cokol":
                    w = G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), **kw_c, **par, **kw)
                elif wariant == "grunt":
                    w = G.wezel_cokol(sz, G.warstwy_z_modelu(model, kp), prog=prog, **kw_c, **par, **kw)
                else:
                    if st is None:
                        raise ValueError("brak stropu w modelu")
                    wys = 1.0 if wariant == "wspornik" else 0.0
                    w = G.wezel_prog_strop(sz, st["grubosc"], mat, pod, suf, wysieg=wys, prog=prog, **par, **kw)
            elif rodz == "garaz":
                kg = next((k for k in kody if k != kod_sz and typ_p(k) and typ_p(k).startswith("sciana")), None)
                wg = (G.warstwy_z_modelu(model, kg) if kg else
                      [G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015),
                       G.Warstwa(G.MATERIALY_DOMYSLNE["SIL24"], 0.24, True),
                       G.Warstwa(G.MATERIALY_DOMYSLNE["TYNK_CEM"], 0.015)])
                w = G.wezel_garaz(sz, wg, przerwa_izolacji=bool(par.pop("przerwa_izolacji", False)), **par, **kw)
            elif rodz == "rura_spustowa":
                w = G.wezel_rura_spustowa(sz, **par, **kw)
            else:   # pragma: no cover
                raise ValueError(rodz)
        except (TypeError, ValueError, KeyError) as ex:
            pom.append(f"{wid}: nie zbudowano węzła ({ex})")
            continue
        out.append(w)
        kody_w[wid] = kody
        if e.get("dlugosc") is not None:
            dl[wid] = float(e["dlugosc"])
    return out, dl, pom, kody_w
