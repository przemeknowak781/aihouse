"""Węzły sekcji `wezly` modelu budowane z GEOMETRII modelu (uzupełnienie `katalog.wezly_z_sekcji`).

Dla typów, których ogólne odwzorowanie (`katalog.ALIASY_WEZLOW`) nie oddaje geometrii budynku:

* płyty wspornikowe z łącznikiem (`plyta_wspornikowa_lacznik`) — płyta wskazana identyfikatorem w nazwie węzła
  (np. „PL-2”), strop / stropodach, do którego przylega (rzędna wierzchu), ściany pod i nad płytą z rzutów
  kondygnacji (przegroda o największej długości wzdłuż krawędzi płyty); przy stropodachu — attyka + okap;
* krawędzie stropu nad powietrzem zewnętrznym (`strop_zewn_krawedz`) — strop z sufitem typu „nad powietrzem”
  (przegroda sufitu z listy węzła), krawędzie z rzutu: (a) ściana na krawędzi (z belką odwróconą i płytą
  wspornikową, jeśli przylegają), (b) krawędź nad ścianą niższej kondygnacji; węzeł z „belk” w nazwie — krawędzie
  z belkami w linii ściany;
* połączenia z pomieszczeniem nieogrzewanym (`polaczenie_nieogrz`), gdy przegroda oddzielająca nie jest ścianą
  zewnętrzną: (a) ściana na płycie fundamentowej, (b) pod płytą dachu zielonego obu stron, (c) pod stropem ze
  ścianą zewnętrzną wyższej kondygnacji na płycie.

`zbuduj(model, wpis, y_teren)` → lista (Wezel, długość z geometrii [m]) albo None (typ poza zakresem modułu).
Długości — z geometrii modelu (odcinki krawędzi / osi ścian); `dlugosc` wpisu modelu dzielona jest proporcjonalnie
w `katalog.wezly_z_sekcji`.
"""
from __future__ import annotations

from shapely.geometry import LineString, Polygon

from . import geometria as G
from . import wezly_dod as D

TOL_Z = 0.35       # [m] tolerancja rzędnych (wierzch płyty ↔ poziom kondygnacji)
TOL_XY = 0.45      # [m] odległość osi ściany od krawędzi płyty (oś — lico zewn. ≈ 0,30 m)


def _typ_p(model, kod):
    p = model.przegrody.get(kod)
    return None if p is None else p.typ


def _mat(model, kod, domyslny="ZB"):
    try:
        return G.material_z_modelu(model, kod) if kod else G.MATERIALY_DOMYSLNE[domyslny]
    except Exception:
        return G.MATERIALY_DOMYSLNE[domyslny]


def _W(model, kod):
    return G.warstwy_z_modelu(model, kod) if kod else []


def kond_przy(model, z: float, gdzie: str) -> list[str]:
    """Kondygnacje pod poziomem z ('dol': wierzch kondygnacji ≈ z) albo nad nim ('gora': rzędna ≈ z)."""
    out = []
    for k in model.kondygnacje:
        zz = k.rzedna + k.wys_kondygnacji if gdzie == "dol" else k.rzedna
        if abs(zz - z) <= TOL_Z:
            out.append(k.id)
    return out


def sciany_wzdluz(model, geom, kondy, typy=("sciana_zewn",), tol=TOL_XY) -> dict[str, float]:
    """{kod przegrody: długość osi ścian leżącej w odległości ≤ tol od `geom`} dla ścian kondygnacji `kondy`."""
    out: dict[str, float] = {}
    g = geom.buffer(tol)
    for s in model.sciany():
        if s.kond not in kondy or (typy and s.typ not in typy):
            continue
        L = LineString([tuple(s.p1), tuple(s.p2)]).intersection(g).length
        if L > 0.3:
            out[s.przegroda_kod] = out.get(s.przegroda_kod, 0.0) + L
    return out


def _max(d: dict):
    return max(d, key=d.get) if d else None


def wspornik_z_nazwy(model, nazwa: str) -> list[dict]:
    ws = [w for w in model.wsporniki() if w.get("lacznik_termiczny") and str(w["id"]) in (nazwa or "")]
    return ws or [w for w in model.wsporniki() if w.get("lacznik_termiczny") and w.get("przegroda")][:1]


def plyta_pod_wspornikiem(model, wsp: dict) -> tuple[dict | None, str]:
    """(strop | dach, rodzaj 'strop'|'dach') przylegający do płyty wspornikowej (wierzch ± TOL_Z, styk w rzucie)."""
    P = Polygon(wsp["obrys"])
    z = float(wsp["wierzch"])
    best = None
    for st in model.stropy():
        if abs(float(st["wierzch"]) - z) <= TOL_Z and Polygon(st["obrys"]).distance(P) < 0.05:
            d = abs(float(st["wierzch"]) - z)
            if best is None or d < best[0]:
                best = (d, st, "strop")
    for dd in model.dachy():
        pl = dd.get("plyta") or {}
        if pl and abs(float(pl["wierzch"]) - z) <= TOL_Z and Polygon(dd["obrys"]).distance(P) < 0.05:
            d = abs(float(pl["wierzch"]) - z)
            if best is None or d < best[0] - 1e-9:
                best = (d, dd, "dach")
    return (best[1], best[2]) if best else (None, "")


def styk_wspornika(model, wsp: dict, z: float) -> float:
    """Długość styku płyty wspornikowej z obrysem zewnętrznym kondygnacji nad nią (albo pod nią) [m]."""
    P = Polygon(wsp["obrys"])
    for kid in kond_przy(model, z, "gora") + kond_przy(model, z, "dol"):
        try:
            obr = model.obrys_kondygnacji(kid, lico="zewn")
        except Exception:
            continue
        L = P.boundary.intersection(obr.buffer(0.02)).length
        if L > 0.3:
            return float(L)
    return float(P.boundary.length / 2)


def _sufit(model, kod):
    if not kod:
        return []
    if kod in model.przegrody:
        return G.warstwy_z_modelu(model, kod)
    return [G.Warstwa(G.material_z_modelu(model, kod), 0.01)]


def _mat_konstr(model, kod_przegrody, domyslny="ZB"):
    p = model.przegroda(kod_przegrody) if kod_przegrody else None
    if p is not None and p.idx_konstr is not None:
        return _mat(model, p.warstwy[p.idx_konstr].mat, domyslny)
    return G.MATERIALY_DOMYSLNE[domyslny]


# ---------------------------------------------------------------------------------------------- płyty wspornikowe
def wezel_plyty_wspornikowej(model, e: dict):
    ws = wspornik_z_nazwy(model, e.get("nazwa", ""))
    if not ws:
        return None
    wsp = ws[0]
    plyta, rodz = plyta_pod_wspornikiem(model, wsp)
    if plyta is None:
        return None
    P = Polygon(wsp["obrys"])
    if rodz == "dach":
        z, t = float(plyta["plyta"]["wierzch"]), float(plyta["plyta"]["grubosc"])
    else:
        z, t = float(plyta["wierzch"]), float(plyta["grubosc"])
    k_dol, k_gora = kond_przy(model, z, "dol"), kond_przy(model, z, "gora")
    L_styk = styk_wspornika(model, wsp, z)
    wysieg = round(min(1.5, max(0.5, P.area / max(L_styk, 1e-6))), 2)
    sc_dol = _max(sciany_wzdluz(model, P, k_dol))
    sc_gora = _max(sciany_wzdluz(model, P, k_gora))
    lac = G.LACZNIK_PRZYKLAD
    kw = dict(t_wsp=float(wsp["grubosc"]), dy_wsp=round(float(wsp["wierzch"]) - z, 4),
              mat_wsp=_mat(model, wsp.get("mat")), wysieg=wysieg, lacznik=lac, id=str(e["id"]), nazwa=e.get("nazwa"))
    if rodz == "dach":
        att = plyta.get("attyka") or {}
        if not sc_dol or not att.get("przegroda"):
            return None
        w = D.wezel_attyka_wspornik(_W(model, sc_dol), _W(model, plyta["przegroda"]), _W(model, att["przegroda"]),
                                    h_nad_pokryciem=float(att.get("wys_nad_pokryciem", 0.30)), **kw)
        opis = f"{wsp['id']} przy dachu {plyta['id']} ({plyta['przegroda']}), attyka {att['przegroda']}, ściana {sc_dol}"
    else:
        if not sc_gora:
            return None
        w = D.wezel_wspornik_ogolny(_W(model, sc_gora), _W(model, sc_dol) if sc_dol else None, t,
                                    _mat(model, plyta.get("mat")), podloga=_W(model, plyta.get("podloga")),
                                    sufit=_sufit(model, plyta.get("sufit")), pod="wewn" if sc_dol else "zewn", **kw)
        opis = f"{wsp['id']} przy stropie {plyta['id']}, ściana dolna {sc_dol}, górna {sc_gora}"
    w.dane["geometria z modelu"] = (f"{opis}; wysięg zastępczy A/L = {wysieg} m; styk z obrysem {L_styk:.2f} m; "
                                    f"łącznik: dane przykładowe (ETA do uzupełnienia)")
    return [(w, L_styk)]


# ---------------------------------------------------------------------------------------------- strop nad powietrzem
def _krawedzie(poly: Polygon):
    c = list(poly.exterior.coords)
    for a, b in zip(c[:-1], c[1:]):
        if LineString([a, b]).length > 0.05:
            yield LineString([a, b])


def krawedzie_stropu_zewn(model, st: dict) -> list[dict]:
    """Krawędzie stropu nad powietrzem: {typ 'a'|'b', L, sciana, belka, belka_rodzaj, wsp} (sygnatury węzłów)."""
    Q = Polygon(st["obrys"])
    z, t = float(st["wierzch"]), float(st["grubosc"])
    k_dol, k_gora = kond_przy(model, z, "dol"), kond_przy(model, z, "gora")
    out = []
    for ed in _krawedzie(Q):
        dol = sciany_wzdluz(model, ed, k_dol, tol=0.35)
        if dol:
            out.append(dict(typ="b", L=ed.length, sciana=_max(dol), belka=None, belka_rodzaj=None, wsp=None))
            continue
        gora = _max(sciany_wzdluz(model, ed, k_gora, tol=0.35))
        belka, rodz_b = None, None
        for b in model.belki():
            ax = LineString(b["os"])
            if ax.distance(ed) <= TOL_XY and ax.intersection(ed.buffer(TOL_XY)).length > 0.3 \
                    and abs(float(b["spod"]) - (z - t)) < 0.06 and float(b["spod"]) + float(b["h"]) > z + 0.05:
                belka = (float(b["b"]), round(float(b["spod"]) + float(b["h"]) - z, 3), b.get("mat"), b["id"])
                rodz_b = "wspornikowa" if ax.length > ax.intersection(ed.buffer(TOL_XY)).length + 0.5 else "krawedziowa"
                break
        wsp = None
        for w in model.wsporniki():
            if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z \
                    and Polygon(w["obrys"]).intersection(ed.buffer(0.02)).length > 0.3:
                wsp = w
                break
        out.append(dict(typ="a", L=ed.length, sciana=gora, belka=belka, belka_rodzaj=rodz_b, wsp=wsp))
    return out


def wezly_stropu_zewn(model, e: dict):
    kody = [str(k) for k in (e.get("przegrody") or [])]
    st = next((s for s in model.stropy() if s.get("sufit") in kody and s.get("sufit") in model.przegrody), None)
    if st is None:
        return None
    belkowy = "belk" in (e.get("nazwa") or "").lower()
    kr = [k for k in krawedzie_stropu_zewn(model, st)
          if (k["typ"] == "a" and (k["belka_rodzaj"] == "wspornikowa") == belkowy) or (k["typ"] == "b" and not belkowy)]
    grupy: dict[tuple, dict] = {}
    for k in kr:
        sig = (k["typ"], k["sciana"], k["belka"][:2] if k["belka"] else None, k["wsp"]["id"] if k["wsp"] else None)
        grupy.setdefault(sig, dict(k, L=0.0))["L"] += k["L"]
    z, t = float(st["wierzch"]), float(st["grubosc"])
    mat = _mat(model, st.get("mat"))
    pod = _W(model, st.get("podloga"))
    suf = _sufit(model, st.get("sufit"))
    out = []
    for n, (sig, k) in enumerate(sorted(grupy.items(), key=lambda it: -it[1]["L"])):
        wid = f"{e['id']}{'abcdefgh'[n]}"
        if k["typ"] == "b":
            if not k["sciana"]:
                continue
            w = D.wezel_przegroda_w_linii(_W(model, k["sciana"]), t, mat, ("wewn", pod), ("wewn", pod),
                                          ("wewn", []), ("zewn", suf), id=wid, typ="strop_zewn_krawedz",
                                          nazwa=f"{e.get('nazwa')} — krawędź nad ścianą {k['sciana']} niższej kondygnacji")
        else:
            if not k["sciana"]:
                continue
            ws = k["wsp"]
            kw = {}
            if ws is not None:
                kw = dict(t_wsp=float(ws["grubosc"]), dy_wsp=round(float(ws["wierzch"]) - z, 4),
                          mat_wsp=_mat(model, ws.get("mat")), wysieg=1.0, lacznik=G.LACZNIK_PRZYKLAD)
            else:
                kw = dict(wysieg=0.0)
            bl = k["belka"]
            w = D.wezel_wspornik_ogolny(_W(model, k["sciana"]), None, t, mat, podloga=pod, sufit=suf, pod="zewn",
                                        belka=(bl[0], bl[1]) if bl else None,
                                        mat_belki=_mat(model, bl[2]) if bl else None, id=wid, **kw,
                                        nazwa=f"{e.get('nazwa')} — ściana {k['sciana']} na krawędzi"
                                              + (f", belka {bl[3]}" if bl else "")
                                              + (f", płyta {ws['id']} (łącznik)" if ws is not None else ""))
        w.dane["geometria z modelu"] = (f"strop {st['id']} (sufit {st.get('sufit')}); krawędzie typu "
                                        f"{'ściana na krawędzi' if k['typ'] == 'a' else 'nad ścianą niższej kondygnacji'}"
                                        f" — łącznie {k['L']:.2f} m")
        out.append((w, k["L"]))
    return out or None


# ---------------------------------------------------------------------------------------------- dom – garaż
def _pas(nazwa: str, domyslna: float = 1.0) -> float:
    import re
    m_ = re.search(r"pas\w*\s+([0-9]+(?:[.,][0-9]+)?)\s*m", nazwa or "")
    return float(m_.group(1).replace(",", ".")) if m_ else domyslna


def _nad_punktem(model, xy, z_max: float):
    """(rodzaj 'strop'|'dach', element) — płyta nad punktem rzutu o wierzchu ≤ z_max (najniższa taka)."""
    from shapely.geometry import Point
    best = None
    for st in model.stropy():
        if Polygon(st["obrys"]).buffer(1e-6).contains(Point(xy)) and float(st["wierzch"]) <= z_max:
            if best is None or float(st["wierzch"]) < best[0]:
                best = (float(st["wierzch"]), "strop", st)
    for dd in model.dachy():
        pl = dd.get("plyta") or {}
        if pl and Polygon(dd["obrys"]).buffer(1e-6).contains(Point(xy)) and float(pl["wierzch"]) <= z_max:
            if best is None or float(pl["wierzch"]) < best[0] - 1e-9:
                best = (float(pl["wierzch"]), "dach", dd)
    return (best[1], best[2]) if best else (None, None)


def wezly_garazu(model, e: dict):
    kody = [str(k) for k in (e.get("przegrody") or [])]
    kg = next((k for k in kody if (_typ_p(model, k) or "").startswith("sciana") and _typ_p(model, k) != "sciana_zewn"),
              None)
    if kg is None:
        return None
    sciany = [s for s in model.sciany() if s.przegroda_kod == kg]
    if not sciany:
        return None
    k0 = min(model.kondygnacje, key=lambda k: k.rzedna)
    pod_dom = next((k for k in kody if _typ_p(model, k) == "podloga_na_gruncie"), None)
    pod_gar = next((k for k, p in model.przegrody.items() if p.typ == "podloga_na_gruncie" and k != pod_dom
                    and "gara" in (p.nazwa or "").lower()), pod_dom)
    kod_suf = next((k for k in kody if _typ_p(model, k) == "strop" and k not in ("POD-1",)), None)
    pas = _pas(model.przegroda(kod_suf).nazwa if kod_suf else "", 1.0)
    out = []
    L_sc = sum(s.L for s in sciany)
    if pod_dom and (model.fundamenty() or {}).get("typ") == "plyta":
        w = D.wezel_garaz_plyta(_W(model, kg), _W(model, pod_dom), _W(model, pod_gar), id=f"{e['id']}a",
                                nazwa=f"Ściana dom–garaż ({kg}) na płycie fundamentowej ({pod_dom} / {pod_gar})")
        out.append((w, L_sc))
    # połączenia pod płytą — wg rodzaju płyty nad stroną domu (lewą) i garażu (prawą)
    warianty: dict[tuple, list] = {}
    for s in sciany:
        mid = (s.p1 + s.p2) / 2
        n_in = s.n * (1 if s.wnetrze != "prawa" else -1)       # strona pierwszej warstwy (dom)
        z_top = s.z_do if s.z_do else k0.rzedna + k0.wys_kondygnacji
        rl, el = _nad_punktem(model, mid + n_in * 0.6, z_top + 0.5)
        rp, ep = _nad_punktem(model, mid - n_in * 0.6, z_top + 0.5)
        if ep is None or el is None:
            continue
        line = LineString([tuple(s.p1), tuple(s.p2)])
        k_gora = kond_przy(model, float(el["wierzch"] if rl == "strop" else el["plyta"]["wierzch"]), "gora")
        sg = _max(sciany_wzdluz(model, line, k_gora, typy=("sciana_zewn",), tol=0.1))
        key = (rl, el["id"], rp, ep["id"], sg)
        warianty.setdefault(key, []).append(s)
    for n, (key, lst) in enumerate(sorted(warianty.items(), key=lambda it: -sum(s.L for s in it[1]))):
        rl, idl, rp, idp, sg = key
        el = next(x for x in (model.stropy() + model.dachy()) if x["id"] == idl)
        ep = next(x for x in (model.stropy() + model.dachy()) if x["id"] == idp)
        def strona(r, x):
            if r == "strop":
                return ("wewn", _W(model, x.get("podloga"))), float(x["grubosc"]), _mat(model, x.get("mat")), \
                    _sufit(model, x.get("sufit"))
            return ("zewn", _W(model, x["przegroda"])), float(x["plyta"]["grubosc"]), \
                _mat_konstr(model, x["przegroda"]), []
        gl, tl, ml, sl = strona(rl, el)
        gp, tp, _mp, _sp = strona(rp, ep)
        dol_p = ("nieogrz", _W(model, kod_suf), pas) if kod_suf else ("nieogrz", [])
        if gp[0] == "zewn" and kod_suf:   # w dachu nad garażem warstwy dachu bez sufitu; pas docieplenia pod płytą
            gp = ("zewn", [w for w in gp[1] if not w.konstrukcyjna and gp[1].index(w) < _idx_k(gp[1])])
        if gl[0] == "zewn":
            gl = ("zewn", [w for w in gl[1] if gl[1].index(w) < _idx_k(gl[1])])
        wid = f"{e['id']}{'bcdefg'[n]}"
        w = D.wezel_przegroda_w_linii(_W(model, kg), tl, ml, gl, gp, ("wewn", sl), dol_p,
                                      sciana_gora=_W(model, sg) if sg else None, t_plyty_prawa=tp, id=wid,
                                      typ="garaz",
                                      nazwa=f"Ściana {kg} pod płytą: dom — {el['id']}"
                                            + (f" + ściana {sg}" if sg else "") + f", garaż — {ep['id']}"
                                            + (f", pas docieplenia {kod_suf} {pas} m" if kod_suf else ""))
        L = sum(s.L for s in lst)
        w.dane["geometria z modelu"] = f"ściany {', '.join(s.id for s in lst)} (Σ {L:.2f} m)"
        out.append((w, L))
    return out or None


def _idx_k(warstwy) -> int:
    return G.indeks_konstrukcyjnej(warstwy)


def zbuduj(model, e: dict, y_teren: float = -0.30):
    """Węzły dla wpisu sekcji `wezly` (lista (Wezel, długość geometryczna)) albo None — obsługa ogólna."""
    typ = str(e.get("typ", ""))
    try:
        if typ in ("plyta_wspornikowa_lacznik", "wspornik"):
            return wezel_plyty_wspornikowej(model, e)
        if typ == "strop_zewn_krawedz":
            return wezly_stropu_zewn(model, e)
        if typ in ("polaczenie_nieogrz", "garaz"):
            return wezly_garazu(model, e)
    except (KeyError, ValueError, TypeError, StopIteration) as ex:   # geometria nietypowa → obsługa ogólna
        raise ValueError(f"katalog_dod: {ex}") from ex
    return None
