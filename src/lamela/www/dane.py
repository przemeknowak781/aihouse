"""Dane strony www wyliczane WYŁĄCZNIE z modelu (budynek.yaml, dzialka.yaml, wyposazenie.yaml) i modułów obliczeń.

``zbierz(budynek, dzialka, wyposazenie) -> dict`` — słownik ``D`` z wartościami liczbowymi i opisem metody/podstawy;
teksty strony formatują je funkcjami ``fm``/``fm_m2`` (zapis polski, 2 miejsca po przecinku jak w RPB).
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from ..ir import build_ir
from ..model import load_model, make_polygon
from ..wskazniki import wskazniki

KLATKI = ("klatka schodowa",)          # jak tools/podglad_modelu.py (bilans W-316)
NBSP = " "


def fm(v, n: int = 2) -> str:
    """Liczba w zapisie polskim: separator tysięcy — wąska spacja niełamiąca, przecinek dziesiętny."""
    if v is None:
        return "—"
    s = f"{float(v):,.{n}f}".replace(",", "X").replace(".", ",").replace("X", NBSP)
    return s.replace("-", "−")


def fm_m2(v, n: int = 2) -> str:
    return f"{fm(v, n)}{NBSP}m²"


# ------------------------------------------------------------------------------------------------ powierzchnie
def powierzchnie(m) -> dict:
    """Zestawienie pomieszczeń i PU wg RPB § 20 / PN-ISO 9836 (rejestr W-316): PU bez klatek schodowych, garażu
    i pomieszczeń technicznych; waga wysokości w świetle ≥ 2,20 → 100 %, 1,40–2,20 → 50 %, < 1,40 → 0 %."""
    wiersze, pu, gar, tech, klat = [], {}, 0.0, 0.0, 0.0
    for r in m.pomieszczenia():
        rodz = str(r.raw.get("rodzaj") or "")
        nm = r.nazwa.lower()
        if any(s in nm for s in KLATKI):
            grupa = "klatka"
            klat += r.pow_netto
        elif rodz == "garaz" or "garaż" in nm:
            grupa = "garaz"
            gar += r.pow_netto
        elif r.kategoria == "techniczna":
            grupa = "techniczne"
            tech += r.pow_netto
        else:
            grupa = "PU"
            pu[r.kond] = pu.get(r.kond, 0.0) + r.pow_zaliczona
        wiersze.append(dict(id=r.id, kond=r.kond, nazwa=r.nazwa, kat=r.kategoria, A=round(r.pow_netto, 2),
                            h=round(r.wysokosc or 0.0, 2), wsp=r.wsp_wysokosci, A_zal=round(r.pow_zaliczona, 2),
                            grupa=grupa, pobyt=bool(r.pobyt_ludzi), rodzaj=rodz))
    return dict(pomieszczenia=wiersze, PU=round(sum(pu.values()), 2), PU_kond={k: round(v, 2) for k, v in pu.items()},
                garaz=round(gar, 2), techniczne=round(tech, 2), klatki=round(klat, 2),
                netto=round(sum(w["A"] for w in wiersze), 2),
                metoda="RPB § 20 ust. 1 pkt 4 / PN-ISO 9836 (W-316): suma pow. netto pomieszczeń z wagą wysokości "
                       "w świetle (≥ 2,20 m — 100 %, 1,40–2,20 m — 50 %, < 1,40 m — 0 %), bez klatek schodowych, "
                       "garażu i pomieszczeń technicznych (wykazane osobno)")


def _poz(w, k):
    v = w.get(k) or {}
    return v.get("wartosc"), v


# ------------------------------------------------------------------------------------------------ WT § 12
def _krawedzie(poly) -> list:
    """Odcinki obrysu z normalną zewnętrzną (obrys CCW → normalna = obrót kierunku o −90°)."""
    from shapely.geometry.polygon import orient
    out = []
    for pg in getattr(poly, "geoms", [poly]):
        c = list(orient(pg, 1.0).exterior.coords)
        for a, b in zip(c[:-1], c[1:]):
            d = np.subtract(b, a)
            L = float(np.hypot(*d))
            if L < 0.05:
                continue
            n = np.array([d[1], -d[0]]) / L
            out.append((np.array(a), np.array(b), n, L))
    return out


def dzialka_minimalna(m) -> dict:
    """Minimalne wymiary prostokątnej działki z gabarytów i odległości od granic wg WT § 12 (rejestr W-001…W-006).

    Metoda: każdy odcinek lica zewnętrznego każdej kondygnacji (płaszczyzna uskoku = odrębna ściana, W-001) dostaje
    wymaganie 4,00 m, gdy ma okna/drzwi (ust. 1 pkt 1), lub 3,00 m bez otworów (ust. 1 pkt 2); płyty wysunięte,
    okapy, daszek wejścia i tarasy — 1,50 m (ust. 6, ostrożnie także tarasy naziemne). Od strony drogi odległości
    § 12 nie obowiązują (ust. 10) — przyjęto odległość linii zabudowy z modelu działki (MPZP). Wynik: najmniejszy
    prostokąt granic spełniający wszystkie wymagania przy orientacji budynku jak w modelu."""
    lim = {"W": [], "E": [], "S": [], "N": []}

    def dodaj(strona, wart, opis, d):
        lim[strona].append((wart, opis, d))
    for k in m.kondygnacje:
        ob = m.obrys_kondygnacji(k.id)
        if ob.is_empty:
            continue
        otw = [o for o in m.otwory(kond=k.id) if o.kierunek_zewn is not None and o.sciana.typ == "sciana_zewn"
               and o.typ not in ("otwor",)]
        for a, b, n, L in _krawedzie(ob):
            seg = LineString([tuple(a), tuple(b)])
            ma = any(float(np.dot(o.kierunek_zewn, n)) > 0.9 and
                     seg.distance(Point(*(o.srodek[:2] + o.kierunek_zewn * (abs(o.sciana.face_t(o.sciana.ext_side)) + 0.01)))) < 0.6
                     for o in otw)
            d = 4.0 if ma else 3.0
            opis = f"lico {k.id} {'z oknami/drzwiami' if ma else 'bez otworów'}"
            for strona, ok, wsp in (("W", n[0] < -0.9, min(a[0], b[0])), ("E", n[0] > 0.9, max(a[0], b[0])),
                                    ("S", n[1] < -0.9, min(a[1], b[1])), ("N", n[1] > 0.9, max(a[1], b[1]))):
                if ok:
                    dodaj(strona, wsp, opis, d)
    inne = [(w.get("id"), w.get("obrys"), "płyta/okap") for w in m.wsporniki()]
    inne += [(t.get("id"), t.get("obrys"), "taras") for t in m.tarasy()]
    inne += [(d.get("id"), d.get("obrys"), "dach/okap") for d in m.dachy()]
    for i, ob, rodz in inne:
        try:
            g = make_polygon(ob)
        except Exception:  # noqa: BLE001
            continue
        x0, y0, x1, y1 = g.bounds
        for strona, wsp in (("W", x0), ("E", x1), ("S", y0), ("N", y1)):
            dodaj(strona, wsp, f"{rodz} {i}", 1.5)
    return _prostokat(m, lim)


def _prostokat(m, lim: dict) -> dict:
    for lm in m.lamele():
        ln = lm.get("linia") or []
        st = str(lm.get("elewacja") or "")
        if len(ln) < 2 or st not in lim:
            continue
        off = float(lm.get("odsuniecie") or 0.0) + float(lm.get("h") or 0.0)
        xs, ys = [p[0] for p in ln], [p[1] for p in ln]
        wsp = {"W": min(xs) - off, "E": max(xs) + off, "S": min(ys) - off, "N": max(ys) + off}[st]
        d = max((q[2] for q in lim[st] if "P2" in q[1]), default=4.0)
        lim[st].append((wsp, f"lamele {lm.get('id')} (jak lico, które osłaniają)", d))
    dz = m.dz
    raw = dz.raw if dz is not None else {}
    d_lz, zrodlo_lz = None, None
    lz, droga = raw.get("linia_zabudowy"), (raw.get("droga") or {}).get("linie_rozgraniczajace")
    if lz and droga:
        d_lz = float(LineString(lz).distance(Polygon(droga)))
        zrodlo_lz = "dzialka.yaml: linia_zabudowy ↔ droga.linie_rozgraniczajace (MPZP)"
    W = min(lim["W"], key=lambda q: q[0] - q[2])
    E = max(lim["E"], key=lambda q: q[0] + q[2])
    S = min(lim["S"], key=lambda q: q[0] - q[2])
    Nmax = max(lim["N"], key=lambda q: q[0])
    xW, xE, yS = W[0] - W[2], E[0] + E[2], S[0] - S[2]
    yN = Nmax[0] + (d_lz if d_lz is not None else 0.0)
    ref = None
    if dz is not None and dz.obrys is not None:
        x0, y0, x1, y1 = dz.obrys.bounds
        ref = dict(szer=round(x1 - x0, 2), gl=round(y1 - y0, 2), pow=round(float(dz.obrys.area), 2))
    return dict(szer=round(xE - xW, 2), gl=round(yN - yS, 2), pow=round((xE - xW) * (yN - yS), 1),
                W=dict(el=W[1], d=W[2]), E=dict(el=E[1], d=E[2]), S=dict(el=S[1], d=S[2]),
                N=dict(el=Nmax[1], d=d_lz, zrodlo=zrodlo_lz), ramka=[xW, yS, xE, yN], referencyjna=ref,
                metoda=dzialka_minimalna.__doc__.split("\n\n", 1)[1].strip())


def orientacja(m) -> dict:
    """Powierzchnia przeszkleń na kierunkach świata (stolarka ścian zewnętrznych, wszystkie kondygnacje) — podstawa
    zalecenia orientacji; strona drogi i wejścia — z modelu działki i otworów drzwi zewnętrznych."""
    azy = float((m.raw.get("uklad") or {}).get("azymut_osi_y") or 0.0)
    kier = {"N": 0.0, "E": 0.0, "S": 0.0, "W": 0.0}
    wejscie = None
    for o in m.otwory():
        if o.kierunek_zewn is None or o.sciana.typ != "sciana_zewn" or o.typ in ("otwor", "brama"):
            continue
        az = (math.degrees(math.atan2(o.kierunek_zewn[0], o.kierunek_zewn[1])) + azy) % 360
        k = "NESW"[int(((az + 45) % 360) // 90)]
        if o.typ in ("okno", "fix", "drzwi_przesuwne_HS"):
            kier[k] += o.szer * o.wys
        if o.typ == "drzwi_zewn" and o.kond == m.kondygnacje[0].id and (wejscie is None or o.szer > wejscie[1]):
            wejscie = (k, o.szer)
    droga = None
    dz = m.dz
    if dz is not None and (dz.raw.get("droga") or {}).get("linie_rozgraniczajace") and dz.obrys is not None:
        c = Polygon(dz.raw["droga"]["linie_rozgraniczajace"]).centroid
        p = dz.obrys.centroid
        az = (math.degrees(math.atan2(c.x - p.x, c.y - p.y)) + azy) % 360
        droga = "NESW"[int(((az + 45) % 360) // 90)]
    return dict(azymut_osi_y=azy, przeszklenia={k: round(v, 1) for k, v in kier.items()},
                najwiecej=max(kier, key=kier.get), wejscie=wejscie[0] if wejscie else None, droga=droga)


# ------------------------------------------------------------------------------------------------ fizyka i energia
PRZEGRODY_POKAZ = ("SZ1", "SZ2", "SZL", "SD1", "SD2", "DZ1", "POD-0", "SWG", "SUF-ZEW")
FUNKCJA_LINII = {"izolacja": "izolacja", "hydroizolacja": "hydro", "przeciwwilgociowa": "hydro",
                 "paroizolacja": "szczelnosc", "szczelnosc": "szczelnosc", "wiatroizolacja": "zewn"}


def energia(m) -> dict:
    """Charakterystyka energetyczna i U przegród z modułu fizyki (``lamela.obliczenia.fizyka_energia``).
    Moduł NIE wyznacza klasy energetycznej — strona podaje EP i EP_max, bez klasy."""
    from ..obliczenia.fizyka_energia import oblicz_wszystko, wyniki_json
    R = oblicz_wszystko(m)
    js = wyniki_json(R)
    w = R["ep"]
    U = {}
    for key, v in js["U"].items():      # pierwsza rola z wymaganiem (kolejność modułu: grunt/nieogrz. przed zewn.)
        kod, rola = key.split("|")[0], key.split("|")[-1]
        if v.get("U_max") is not None and kod not in U:
            U[kod] = dict(U=v["U"], U_max=v["U_max"], rola=rola)
    for s in m.stropy():                # strop nad powietrzem zewn. → U przypisane przegrodzie sufitu (np. SUF-ZEW)
        if str(s.get("id")) in U and s.get("sufit") and m.przegroda(str(s["sufit"])) is not None:
            U.setdefault(str(s["sufit"]), U[str(s["id"])])
    stol = m.raw.get("stolarka") or {}
    okna = [o["U_w"] for o in js["okna"].values() if o.get("U_w") and
            str((stol.get(o.get("symbol")) or {}).get("wyrob") or "").startswith(("okno", "fix", "HS"))]
    braki = {k: v for k, v in (js.get("ciaglosc_braki") or {}).items() if v}
    alt = [dict(nazwa=k, **{kk: v[kk] for kk in ("EP", "EK", "spelnia", "U_oze")}) for k, v in js["EP"].items()]
    return dict(EP=w.EP, EP_max=w.EP_max, EU=js["EP"][w.system.nazwa]["EU"], EK=js["EP"][w.system.nazwa]["EK"],
                U_oze=js["EP"][w.system.nazwa]["U_oze"], E_CO2_t=js["EP"][w.system.nazwa]["E_CO2_t"],
                system=w.system.nazwa, A_f=js["A_f"], Phi_HL_kW=js["Phi_HL_W"] / 1000.0, H_TB=js["H_TB"],
                went_m3h=js["wentylacja_m3h"], U=U, Uw_min=min(okna) if okna else None,
                Uw_max=max(okna) if okna else None, n_okien=len(okna), ciaglosc_braki=braki,
                ciaglosc_n=len(js.get("ciaglosc_braki") or {}), alternatywy=alt, klasa=None,
                zrodlo="lamela.obliczenia.fizyka_energia (PN-EN ISO 6946/13370/13789/52016-1, metodologia ŚCHE)")


def przegrody(m, U: dict) -> list:
    """Przegrody zewnętrzne z warstwami (materiał, grubość, funkcja „linii”, kolor z modelu) i U z modułu fizyki."""
    out = []
    for kod in PRZEGRODY_POKAZ:
        p = m.przegroda(kod)
        if p is None:
            continue
        ws = []
        for w in p.warstwy:
            mat = m.material(w.mat)
            wr = next((x for x in (p.raw.get("warstwy") or []) if isinstance(x, dict) and x.get("mat") == w.mat), {})
            fun = str(wr.get("funkcja") or (mat.raw if mat is not None else {}).get("funkcja") or "")
            ws.append(dict(mat=w.mat, nazwa=(mat.nazwa if mat else w.mat), d=w.d,
                           kolor=(mat.raw.get("kolor") if mat is not None else None) or "#cccccc",
                           linia=FUNKCJA_LINII.get(fun) or ("konstr" if getattr(w, "konstrukcyjna", False) else ""),
                           lam=getattr(mat, "lambda_", None) if mat else None))
        u = U.get(kod) or {}
        out.append(dict(kod=kod, nazwa=p.nazwa, typ=p.typ, d=round(sum(w["d"] for w in ws), 3), warstwy=ws,
                        U=u.get("U"), U_max=u.get("U_max")))
    return out


def instalacje(m) -> dict:
    en = m.raw.get("energia") or {}
    lib = {}
    f = Path(__file__).resolve().parents[1] / "obliczenia" / "dane" / "wyroby_przykladowe.yaml"
    if f.exists():
        raw = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        for v in raw.values():
            if isinstance(v, dict):
                lib.update({k: x for k, x in v.items() if isinstance(x, dict)})
    og, went, pv, cwu = en.get("ogrzewanie") or {}, en.get("wentylacja") or {}, en.get("pv") or {}, en.get("cwu") or {}
    pc, reku = lib.get(og.get("zrodlo"), {}), lib.get(went.get("centrala"), {})
    kwp = (pv.get("moduly") or 0) * (pv.get("P_modul_Wp") or 0) / 1000.0
    return dict(pc_opis=pc.get("opis"), pc_P=pc.get("P_Am7W35_kW"), pc_SCOP=pc.get("SCOP_35"),
                t_zas=og.get("temp_zasilania"), reku_opis=reku.get("opis"), reku_V=reku.get("V_nom_m3h"),
                reku_eta=reku.get("eta_t"), pv_kWp=kwp, pv_n=pv.get("moduly"), pv_Wp=pv.get("P_modul_Wp"),
                pv_az=pv.get("azymut"), pv_nach=pv.get("nachylenie"), cwu_V=cwu.get("V_projekt_dm3"),
                n50=en.get("n50"), osoby=en.get("osoby"), garaz_stanowiska=(en.get("garaz") or {}).get("stanowiska"))
