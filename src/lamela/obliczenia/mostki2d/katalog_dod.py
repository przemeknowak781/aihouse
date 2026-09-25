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


def styk_wspornika(model, wsp: dict, kondy_dol: list[str]) -> LineString:
    """Linia styku płyty wspornikowej z obrysem zewnętrznym kondygnacji (pierwszej z `kondy_dol` albo niższej)."""
    P = Polygon(wsp["obrys"])
    for kid in kondy_dol or [model.kondygnacje[-1].id]:
        try:
            obr = model.obrys_kondygnacji(kid, lico="zewn")
            return P.intersection(obr.exterior.buffer(0.02)).buffer(0.0) if False else \
                P.boundary.intersection(obr.buffer(0.02))
        except Exception:
            continue
    return P.boundary
