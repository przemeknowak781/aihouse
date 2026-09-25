"""Zestawienie mostków cieplnych budynku (sekcja `wezly` modelu + węzły wykryte w geometrii):

* `dlugosci_geometryczne(model, wezly)` — długości liniowych mostków policzone z GEOMETRII modelu (obrysy
  kondygnacji, dachy, płyty wspornikowe, stropy, ściany, otwory, pomieszczenia) — niezależnie od pola `dlugosc`
  sekcji `wezly`; każdy odcinek krawędzi obudowy przypisany do jednego węzła (bez podwójnego liczenia);
* `mostki_punktowe(model)` — χ i liczby mostków punktowych (konsole lamel, kotwy, przejścia instalacji);
* `ocena_4_linii(...)` — ciągłość „4 linii” (izolacja cieplna, hydroizolacja, szczelność powietrzna, paroizolacja
  / kontrola pary) dla karty węzła;
* `raport_zestawienia(...)` — Markdown: tabela węzłów, porównanie długości model ↔ geometria, H_TB.

System wymiarów: wewnętrzne całkowite (ψ_oi, `energia.bryla`); długości po krawędziach obrysu zewnętrznego
(przyjęcie [INT] — różnica ≤ grubość ściany na narożach, pomijalna wobec dokładności ψ).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from .katalog_dod import (TOL_Z, _krawedzie, _max, _pom_pod, kond_przy, krawedzie_stropu_zewn, nieogrzewane,
                          sciany_wzdluz, wspornik_z_nazwy)

KROK = 0.125     # [m] krok próbkowania krawędzi obrysów


def _probki(ed: LineString, krok: float = KROK):
    """Odcinki krawędzi (s0, s1, punkt środkowy, wersor, normalna) co `krok`."""
    c = np.asarray(ed.coords)
    u = (c[-1] - c[0]) / ed.length
    n = np.array([-u[1], u[0]])
    N = max(1, int(round(ed.length / krok)))
    for k in range(N):
        s0, s1 = k * ed.length / N, (k + 1) * ed.length / N
        yield s0, s1, c[0] + u * (s0 + s1) / 2, u, n


def _do_wnetrza(P: Polygon, pm, n) -> np.ndarray:
    return n if P.buffer(1e-6).contains(Point(pm + n * 0.2)) else -n


def _ogrzewane_pod(model, xy, z: float) -> bool | None:
    """Czy pod płytą (wierzch z) w punkcie rzutu jest pomieszczenie ogrzewane (None — brak pomieszczenia)."""
    rs = [_pom_pod(model, xy + np.array(d), z) for d in ((0, 0), (0.3, 0), (-0.3, 0), (0, 0.3), (0, -0.3))]
    rs = [r for r in rs if r is not None]
    if not rs:
        return None
    return not (sum(map(nieogrzewane, rs)) * 2 >= len(rs))


def _ogrzewane_w(model, kid: str, xy) -> bool | None:
    for r in model.pomieszczenia(kid):
        g = getattr(r, "polygon", None)
        if g is not None and g.buffer(0.05).contains(Point(xy)):
            return not nieogrzewane(r)
    return None


def _wsporniki_lacznik(model, z: float) -> list[Polygon]:
    return [Polygon(w["obrys"]) for w in model.wsporniki()
            if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]


def _blisko(pt, polys, tol=0.06) -> bool:
    p = Point(pt)
    return any(P.distance(p) <= tol for P in polys)


def _pokrycie(model, ed: LineString, kondy, typy=("sciana_zewn",), tol=0.35) -> list[tuple[float, float, str]]:
    """Przedziały [s0, s1] krawędzi `ed` pokryte osiami ścian równoległych (kondygnacje `kondy`)."""
    c = np.asarray(ed.coords)
    u = (c[-1] - c[0]) / ed.length
    out = []
    for s in model.sciany():
        if s.kond not in kondy or (typy and s.typ not in typy):
            continue
        if abs(u[0] * s.u[1] - u[1] * s.u[0]) > 0.17:
            continue
        ax = LineString([tuple(s.p1), tuple(s.p2)])
        if ax.distance(ed) > tol:
            continue
        a, b = sorted([float(np.dot(s.p1 - c[0], u)), float(np.dot(s.p2 - c[0], u))])
        a, b = max(a, 0.0), min(b, ed.length)
        if b - a > 0.05:
            out.append((a - tol, b + tol, s.przegroda_kod))   # przedłużenie o grubość — naroża
    return out


def _w(przedz, s) -> str | None:
    for a, b, k in przedz:
        if a - 1e-9 <= s <= b + 1e-9:
            return k
    return None


def klasyfikuj_obwod(model) -> dict[tuple, float]:
    """Długości odcinków obudowy wg kategorii: ('attyka', dach) | ('wsp', id płyty) | ('dach_sciana', dach) |
    ('strop_posredni', strop) | ('cokol',) | ('prog',). Próbkowanie krawędzi co KROK [INT]."""
    L: dict[tuple, float] = {}
    add = lambda k, v: L.__setitem__(k, L.get(k, 0.0) + v)
    # --- A. krawędzie dachów
    for d in model.dachy():
        pl = d.get("plyta") or {}
        if not pl:
            continue
        z = float(pl["wierzch"])
        P = Polygon(d["obrys"])
        wsp = [(w["id"], Polygon(w["obrys"])) for w in model.wsporniki()
               if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]
        for ed in _krawedzie(P):
            gora = _pokrycie(model, ed, kond_przy(model, z, "gora"))
            for s0, s1, pm, u, n in _probki(ed):
                n_in = _do_wnetrza(P, pm, n)
                ogrz = _ogrzewane_pod(model, pm + n_in * 0.6, z)
                if not ogrz:
                    continue
                if _w(gora, (s0 + s1) / 2):
                    add(("dach_sciana", d["id"]), s1 - s0)
                    continue
                wid = next((i for i, W in wsp if W.distance(Point(pm)) <= 0.06), None)
                add(("wsp", wid) if wid else ("attyka", d["id"]), s1 - s0)
    # --- B. krawędzie stropów pośrednich (obrys kondygnacji nad stropem)
    for st in model.stropy():
        z = float(st["wierzch"])
        if st.get("sufit") in model.przegrody:          # strop nad powietrzem — węzły WZ-07/16 (katalog_dod)
            continue
        k_g, k_d = kond_przy(model, z, "gora"), kond_przy(model, z, "dol")
        if not k_g or not k_d:
            continue
        obr = model.obrys_kondygnacji(k_g[0], lico="zewn")
        Q = Polygon(st["obrys"]).buffer(0.05)
        dachy = [Polygon(d_["obrys"]) for d_ in model.dachy()
                 if d_.get("plyta") and abs(float(d_["plyta"]["wierzch"]) - z) <= TOL_Z]
        wsp = [(w["id"], Polygon(w["obrys"])) for w in model.wsporniki()
               if w.get("lacznik_termiczny") and w.get("przegroda") and abs(float(w["wierzch"]) - z) <= TOL_Z]
        for ed in _krawedzie(obr):
            if not Q.contains(ed.interpolate(0.5, normalized=True)):
                continue
            dol = _pokrycie(model, ed, k_d)
            for s0, s1, pm, u, n in _probki(ed):
                if not _w(dol, (s0 + s1) / 2):
                    continue
                n_in = _do_wnetrza(obr, pm, n)
                if _ogrzewane_pod(model, pm + n_in * 0.6, z) is False:
                    continue
                wid = next((i for i, W in wsp if W.distance(Point(pm)) <= 0.06), None)
                if wid:
                    add(("wsp", wid), s1 - s0)
                elif _blisko(pm, dachy):
                    continue                                   # dach – ściana (część A)
                else:
                    add(("strop_posredni", st["id"]), s1 - s0)
    # --- C. obwód parteru (cokół / progi)
    k0 = min(model.kondygnacje, key=lambda k: k.rzedna)
    obr0 = model.obrys_kondygnacji(k0.id, lico="zewn")
    progi = []
    for o in model.otwory(kond=k0.id):
        sc = o.sciana
        if sc is None or sc.typ != "sciana_zewn" or o.typ in ("otwor", "brama") or (o.parapet or 0.0) > 0.05:
            continue
        c_ = np.asarray(o.srodek)
        if _ogrzewane_w(model, k0.id, c_ + sc.n * sc.sgn_int * 0.6) is False:
            continue
        progi.append((c_, float(o.szer), sc.u))
    for ed in _krawedzie(obr0):
        prev = None
        for s0, s1, pm, u, n in _probki(ed):
            n_in = _do_wnetrza(obr0, pm, n)
            ogrz = None
            for a in (0.5, 0.8, 1.2):
                for b in (0.0, 0.3, -0.3, 0.6, -0.6):
                    ogrz = _ogrzewane_w(model, k0.id, pm + n_in * a + u * b)
                    if ogrz is not None:
                        break
                if ogrz is not None:
                    break
            ogrz = prev if ogrz is None else ogrz          # naroża / ściany wewnętrzne — jak próbka poprzednia
            prev = ogrz
            if not ogrz:
                continue
            jest_prog = any(abs(float(np.dot(pm - c_, uu))) <= w / 2 and
                            abs(float(np.dot(pm - c_, np.array([-uu[1], uu[0]])))) <= 0.45 for c_, w, uu in progi)
            add(("prog",) if jest_prog else ("cokol",), s1 - s0)
    return L


def naroza_wypukle(model) -> tuple[float, list[str]]:
    """Σ (liczba naroży wypukłych obrysu ogrzewanego kondygnacji × wysokość kondygnacji) [m] + opis."""
    tot, op = 0.0, []
    for k in model.kondygnacje:
        obr = model.obrys_kondygnacji(k.id, lico="zewn")
        c = np.asarray(obr.exterior.coords)[:-1]
        ccw = obr.exterior.is_ccw
        n = 0
        for i in range(len(c)):
            a, b, e = c[i - 1], c[i], c[(i + 1) % len(c)]
            cr = (b[0] - a[0]) * (e[1] - b[1]) - (b[1] - a[1]) * (e[0] - b[0])
            if abs(cr) < 1e-9 or (cr > 0) != ccw:
                continue
            u1 = (a - b) / np.linalg.norm(a - b)
            u2 = (e - b) / np.linalg.norm(e - b)
            bis = (u1 + u2) / np.linalg.norm(u1 + u2)
            og = [_ogrzewane_w(model, k.id, b + bis * r) for r in (0.8, 1.2, 1.8)]
            og = [x for x in og if x is not None]
            if og and og[0]:
                n += 1
        tot += n * k.wys_kondygnacji
        op.append(f"{k.id}: {n} × {k.wys_kondygnacji:.2f} m")
    return tot, op


def otwory_obudowy(model) -> list:
    """Otwory (stolarka) w ścianach zewnętrznych pomieszczeń ogrzewanych (bez bram, przejść i garażu)."""
    out = []
    for o in model.otwory():
        sc = o.sciana
        if sc is None or sc.typ != "sciana_zewn" or o.typ in ("otwor", "brama"):
            continue
        c_ = np.asarray(o.srodek)
        og = [_ogrzewane_w(model, o.kond, c_ + sc.n * sc.sgn_int * a) for a in (0.5, 0.9, 1.4)]
        og = [x for x in og if x is not None]
        if og and not og[0]:
            continue
        out.append(o)
    return out


def dlugosci_geometryczne(model, wezly) -> dict[str, tuple[float, str]]:
    """{id węzła: (długość z geometrii [m], opis)} — dla węzłów katalogu (lista `Wezel`)."""
    wpisy = {str(e.get("id")): e for e in (model.raw.get("wezly") or [])}
    L = klasyfikuj_obwod(model)
    out: dict[str, tuple[float, str]] = {}
    przeg_dachu = {d["id"]: d["przegroda"] for d in model.dachy()}
    wsp_uw = {w["id"]: (w.get("uwagi") or "") for w in model.wsporniki()}
    otw = otwory_obudowy(model)
    k0 = min(model.kondygnacje, key=lambda k: k.rzedna).id
    for w in wezly:
        e = wpisy.get(w.id) or wpisy.get(w.id.rstrip("abcdefgh")) or {}
        typ = str(e.get("typ", ""))
        nz = (e.get("nazwa") or w.nazwa or "")
        if "długość z geometrii modelu [m]" in w.dane and typ not in ("plyta_wspornikowa_lacznik", "wspornik"):
            out[w.id] = (float(w.dane["długość z geometrii modelu [m]"]), w.dane.get("geometria z modelu", ""))
            continue
        if typ == "attyka":
            kody = set(e.get("przegrody") or [])
            ks = [k for k in L if k[0] == "attyka" and przeg_dachu.get(k[1]) in kody]
            out[w.id] = (sum(L[k] for k in ks), "attyki nad pomieszczeniami ogrzewanymi, bez odcinków z płytą "
                                                 "wspornikową i ze ścianą wyższą: " + ", ".join(
                f"{k[1]} {L[k]:.2f}" for k in ks))
        elif typ in ("plyta_wspornikowa_lacznik", "wspornik"):
            ids = [i for i in wsp_uw if i in nz]
            if "daszek" in nz.lower():
                ids += [i for i, u in wsp_uw.items() if "daszek" in u.lower() and i not in ids]
            ks = [k for k in L if k[0] == "wsp" and k[1] in ids]
            out[w.id] = (sum(L[k] for k in ks), "styk płyt z obudową (bez krawędzi stropu nad powietrzem): "
                         + ", ".join(f"{k[1]} {L[k]:.2f}" for k in ks))
        elif typ == "strop_posredni":
            ks = [k for k in L if k[0] == "strop_posredni"]
            out[w.id] = (sum(L[k] for k in ks), "ściana zewn. nad i pod stropem, bez płyt wspornikowych, dachów i "
                                                 "garażu: " + ", ".join(f"{k[1]} {L[k]:.2f}" for k in ks))
        elif typ in ("sciana_grunt", "cokol"):
            out[w.id] = (L.get(("cokol",), 0.0), "obwód parteru pomieszczeń ogrzewanych bez progów")
        elif typ == "prog":
            out[w.id] = (L.get(("prog",), 0.0), "szerokości otworów drzwiowych/HS parteru (parapet ≤ 5 cm)")
        elif typ in ("naroznik_wypukly", "naroze"):
            v, op = naroza_wypukle(model)
            out[w.id] = (v, "naroża wypukłe obrysu ogrzewanego × wys. kondygnacji: " + "; ".join(op))
        elif typ == "oscieze":
            out[w.id] = (sum(2 * o.wys for o in otw), f"2 × wysokość {len(otw)} otworów w ścianach zewn. części "
                                                        f"ogrzewanej")
        elif typ == "nadproze":
            out[w.id] = (sum(o.szer for o in otw), "szerokości otworów")
        elif typ == "podokiennik":
            pp = [o for o in otw if (o.parapet or 0.0) > 0.05]
            out[w.id] = (sum(o.szer for o in pp), f"szerokości {len(pp)} okien z parapetem > 5 cm")
        elif w.id.startswith("WZ-X"):
            kod = next((przeg_dachu[k[1]] for k in L if k[0] == "dach_sciana" and f"({przeg_dachu[k[1]]})" in w.nazwa),
                       None)
            ks = [k for k in L if k[0] == "dach_sciana" and przeg_dachu.get(k[1]) == kod]
            out[w.id] = (sum(L[k] for k in ks), "krawędzie dachów pod ścianą wyższej kondygnacji: "
                         + ", ".join(f"{k[1]} {L[k]:.2f}" for k in ks))
    progi_wyzej = [o for o in otw if (o.parapet or 0.0) <= 0.05 and o.kond != k0]
    if progi_wyzej:
        out["_uwaga_progi"] = (sum(o.szer for o in progi_wyzej),
                               "progi okien/drzwi do podłogi na kondygnacjach wyższych — przypisane do WZ-11P [INT]")
    return out


def mostki_punktowe(model) -> list[dict]:
    """[{id, nazwa, n, chi, zrodlo, opis_n}] — mostki punktowe z sekcji `wezly` (liczba z geometrii, gdy możliwe)."""
    from ..fizyka.mostki import CHI_DOMYSLNE
    try:
        from ..wspolne import wyrob
        wl = wyrob("laczniki", "lamele_wspornik") or {}
    except Exception:
        wl = {}
    out = []
    for e in model.raw.get("wezly") or []:
        typ = str(e.get("typ", ""))
        if typ not in CHI_DOMYSLNE:
            continue
        chi, op = CHI_DOMYSLNE[typ]
        zr = "fizyka.mostki.CHI_DOMYSLNE [NZW]"
        n = float(e.get("liczba") or 0)
        opis_n = "liczba z modelu (sekcja `wezly`)"
        if typ == "konsola_lamel":
            if wl.get("chi"):
                chi, zr = float(wl["chi"]), f"{wl.get('status', '')} {wl.get('zrodlo', '')}".strip()
            Ls = 0.0
            for lm in model.raw.get("lamele") or []:
                ln = LineString(lm["linia"])
                if float(lm.get("odsuniecie", 0.0)) > 0.0:       # lamele przed elewacją (ekran wewn. pominięty)
                    Ls += ln.length
            n_g = round(Ls * 2 / 1.0)
            opis_n = f"Σ długości linii lamel {Ls:.2f} m × 2 rygle / rozstaw konsol 1,0 m [ZAŁ] = {n_g}"
            n = n_g
        out.append(dict(id=str(e["id"]), nazwa=str(e.get("nazwa", "")), n=n, chi=chi, zrodlo=zr, opis_n=opis_n))
    return out


# ================================================================================================ 4 linie
LINIE4 = {"I": "izolacja cieplna", "H": "hydroizolacja / ochrona przed wodą", "S": "szczelność powietrzna",
          "P": "paroizolacja / kontrola pary"}
ROLA_P = {"sciana_zewn": "sciana_zewn", "stropodach": "dach", "attyka": None, "sciana_wewn_nosna": "sciana_nieogrz",
          "strop": None, "podloga_na_gruncie": None, "taras": None}


def _glaser(model, kod: str, cache: dict):
    if kod in cache:
        return cache[kod]
    p = model.przegroda(kod)
    rola = ROLA_P.get(p.typ) if p is not None else None
    r = None
    if rola:
        try:
            from ..fizyka import kondensacja as KD
            from ..fizyka.u_przegrody import warstwy_przegrody
            w, Rsi, Rse = KD.warstwy_glaser(warstwy_przegrody(model, kod), model.materialy, rola=rola)
            r = KD.glaser(w, Rsi, Rse, theta_i=20.0, klasa=3, kod=kod, rola=rola)
        except Exception:      # pragma: no cover
            r = None
    cache[kod] = r
    return r


def _funkcje(model, kod) -> set[str]:
    """Funkcje warstw przegrody (`fizyka.warstwy.funkcja_warstwy` + pole `funkcja` warstw modelu); tynk wewnętrzny
    (pierwsza warstwa ściany) = warstwa szczelności powietrznej."""
    p = model.przegroda(kod)
    out: set[str] = set()
    if p is None:
        return out
    try:
        from ..fizyka.warstwy import funkcja_warstwy, mat_props
        for j_, w in enumerate(p.warstwy):
            f = funkcja_warstwy(mat_props(model.materialy, w.mat), {"mat": w.mat, "d": w.d})
            out.add(str(f))
            if f == "tynk" and j_ == 0:
                out.add("szczelnosc_powietrzna")
    except Exception:      # pragma: no cover
        pass
    raw = (p.raw or {}).get("warstwy") or []
    out |= {str(w.get("funkcja")) for w in raw if isinstance(w, dict) and w.get("funkcja")}
    return out


def ocena_4_linii(model, wezel, wynik: dict, kody: list[str], cache: dict | None = None) -> dict:
    """{'I'|'H'|'S'|'P': (status 'OK'|'UWAGA'|'BRAK', opis), 'ciaglosc': 'zachowana'|'uwaga: …'}"""
    cache = {} if cache is None else cache
    typ = wezel.typ
    out = {}
    # I — izolacja cieplna (test ołówka z karty)
    droga = wynik.get("droga_mostka") or []
    if wynik.get("izolacja_ciagla"):
        out["I"] = ("OK", "ciągła — brak drogi przez materiały λ > 0,12 z wnętrza na zewnątrz")
    elif droga and droga[-1] == "GRUNT":
        out["I"] = ("UWAGA", "domyka się przez grunt: " + " → ".join(droga))
    else:
        out["I"] = ("BRAK" if typ != "garaz" else "UWAGA", "przerwana: " + " → ".join(droga)
                    + (" (płyta ciągła do strefy nieogrzewanej — mostek konstrukcyjny)" if typ == "garaz" else ""))
    # H — hydroizolacja
    br = [t for t in (wynik.get("woda_braki") or []) if "izolacji" not in t]
    uw = [t for t in (wynik.get("woda_uwagi") or []) if "izolacji" not in t]
    lin = {ln["rodzaj"] for ln in wezel.linie}
    niskie = [ln["opis"] for ln in wezel.linie if "< WYMAGANE" in ln.get("opis", "")]
    if br or niskie:
        out["H"] = ("BRAK", "; ".join(br + niskie))
    elif uw:
        out["H"] = ("UWAGA", "; ".join(uw))
    elif lin & {"hydro", "przeciwwilg"}:
        out["H"] = ("OK", "; ".join(ln["opis"] for ln in wezel.linie if ln["rodzaj"] in ("hydro", "przeciwwilg"))[:220])
    else:
        out["H"] = ("OK", "węzeł poza strefą wody stojącej — wyprawa / okładzina elewacji ciągła")
    # S — szczelność powietrzna
    fun = set().union(*[_funkcje(model, k) for k in kody]) if kody else set()
    if typ in ("oscieze", "nadproze", "podokiennik", "prog"):
        out["S"] = ("OK", "tynk wewn. do ramy + taśma paroszczelna (od wewn.) na obwodzie ramy — wymaganie detalu")
    elif typ == "garaz":
        out["S"] = ("OK", "tynk ciągły po stronie domu + uszczelnienie styków z płytą (szczelność gazowa WT § 106)")
    elif "szczelnosc_powietrzna" in fun or "paroizolacja" in fun:
        out["S"] = ("OK", "warstwa szczelna ciągła: " + ", ".join(sorted(fun & {"szczelnosc_powietrzna", "paroizolacja"}))
                    + (" + płyta ŻB (połączenia taśmą)" if typ in ("attyka", "wspornik", "strop_zewn_krawedz") else ""))
    else:
        out["S"] = ("UWAGA", "brak oznaczonej warstwy szczelności w przegrodach węzła")
    # P — paroizolacja / kontrola pary (Glaser przegród węzła)
    ocen = []
    for k in kody:
        r = _glaser(model, k, cache)
        if r is not None:
            ocen.append((k, r.dopuszczalna, r.ocena))
    if any(not ok for _k, ok, _o in ocen):
        out["P"] = ("BRAK", "; ".join(f"{k}: {o}" for k, ok, o in ocen if not ok))
    elif ocen:
        out["P"] = ("OK", "Glaser (PN-EN ISO 13788): " + "; ".join(f"{k} — {o}" for k, _ok, o in ocen))
    else:
        out["P"] = ("OK", "przegrody węzła bez ryzyka kondensacji (wewnętrzne / na gruncie)")
    zle = [f"{LINIE4[k]}: {out[k][1]}" for k in "IHSP" if out[k][0] != "OK"]
    out["ciaglosc"] = "zachowana" if not zle else "uwaga — " + "; ".join(zle)
    return out


# ================================================================================================ przelewy
def poziomy_dachu(model, dach: dict, xy) -> dict:
    """Rzędne w punkcie rzutu dachu [m]: wierzch płyty, hydroizolacja (pokrycie) i wierzch warstw nad nią; grubość
    warstwy spadkowej d = d_min + spadek·(odległość od najbliższego wpustu) ≤ d_max [INT — powierzchnia stożkowa]."""
    p = model.przegroda(dach["przegroda"])
    pl = dach["plyta"]
    z0 = float(pl["wierzch"])
    ki = p.idx_konstr
    raw = (p.raw or {}).get("warstwy") or []
    wp = [np.asarray(w["xy"] if isinstance(w, dict) else w, float) for w in dach.get("wpusty") or []]
    dist = min((float(np.linalg.norm(np.asarray(xy, float) - q)) for q in wp), default=0.0)
    sp = float(dach.get("spadek") or 0.02)
    z = z0
    z_memb = None
    nad = list(range(ki - 1, -1, -1))           # od płyty w górę
    for j in nad:
        w = p.warstwy[j]
        kl = raw[j].get("klin") if j < len(raw) and isinstance(raw[j], dict) else None
        d = float(w.d)
        if kl:
            d = min(float(kl["d_max"]), float(kl["d_min"]) + sp * dist)
        z += d
        f = str((raw[j].get("funkcja") if j < len(raw) and isinstance(raw[j], dict) else "") or "")
        m_ = model.material(w.mat)
        fm = str(((getattr(m_, "raw", None) or {}).get("funkcja")) or "")
        if "hydro" in f or "hydro" in fm:
            z_memb = z
    return {"plyta": z0, "pokrycie": z_memb if z_memb is not None else z, "wierzch": z, "odl_wpustu": dist}


def poziomy_przelewow(model) -> list[dict]:
    """Kontrola rzędnych przelewów awaryjnych: dno ≥ pokrycie przy wpuście + 0,03 m (W-142 / J2 5.1: 30–50 mm),
    dno ≥ pokrycie lokalne (przelew nie może leżeć pod pokryciem), górna krawędź otworu ≤ wierzch wywinięć (pokrycie
    lokalne + 0,15 m, DAFA) i ≤ korona attyki."""
    out = []
    for d in model.dachy():
        att = d.get("attyka") or {}
        wp = [w["xy"] if isinstance(w, dict) else w for w in d.get("wpusty") or []]
        if not wp:
            continue
        pw = min((poziomy_dachu(model, d, q) for q in wp), key=lambda r: r["pokrycie"])
        p = model.przegroda(d["przegroda"])
        z_korona = float(d["plyta"]["wierzch"]) + p.d_nad_konstr() + float(att.get("wys_nad_pokryciem", 0.0))
        for pa in d.get("przelewy_awaryjne") or []:
            lok = poziomy_dachu(model, d, pa["xy"])
            dno = float(pa["rzedna_dna"])
            h = float(pa.get("wys", 0.10))
            dno_min = max(pw["pokrycie"] + 0.03, lok["pokrycie"])
            dno_max = min(pw["pokrycie"] + 0.05, lok["pokrycie"] + 0.15 - h, z_korona - h - 0.05)
            dno_max = max(dno_max, dno_min)
            ok = dno_min - 1e-3 <= dno <= dno_max + 1e-3
            out.append(dict(dach=d["id"], opis=str(pa.get("opis", "")), xy=pa["xy"], dno=dno, h=h,
                            pokrycie_wpust=pw["pokrycie"], pokrycie_lok=lok["pokrycie"], wierzch_lok=lok["wierzch"],
                            korona=z_korona, dno_min=dno_min, dno_max=dno_max, ok=ok,
                            zalecane=round(min(max(dno, dno_min), dno_max), 3)))
    return out
