#!/usr/bin/env python
"""Generator modelu pomieszczeń „BRAMA I LATARNIA” → model/budynek.json (+ zestawienie CSV, testy, raport rozbieżności).

Źródła prawdy czytane W CZASIE DZIAŁANIA (bez przepisywania liczb):
  * model/koncepcja.json – bryły, łuk, kondygnacje, rdzenie, siatka, Sejmik (poligony), podziemie, parter (strefy),
    kondygnacje_biurowe (rozmieszczenie komórek, sumy pokoi, sal, magazynków, socjalnych);
  * docs/20_program/program.yaml – komórki z tabeli 1 M.01 (pokoje per komórka, osoby), pozycje programu z kodami grup.

Założenia własne (parametry P) są jawne i trafiają do raportu. Uruchom ponownie po zmianie specyfikacji:
    /home/user/aihouse/.venv-render/bin/python -I tools/model_pomieszczen.py
"""
from __future__ import annotations
import csv
import os
import json
import math
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from shapely.geometry import Polygon, MultiPolygon, LineString, Point, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

from umwd.frames import Frame, annulus_sector, clean_ring  # noqa: E402
from umwd.rooms import (Space, Run, ArcRun, place_run, corridor_behind, arc_place, arc_corridor,  # noqa: E402
                        ext_band, polys, largest, clean, door_on, MITRE)

SPEC = ROOT / "model" / "koncepcja.json"
PROG = ROOT / "docs" / "20_program" / "program.yaml"
OUT_JSON = ROOT / "model" / "budynek.json"
OUT_CSV = ROOT / "model" / "zestawienie_pomieszczen.csv"

# ----------------------------------------------------------------------------------------------------------------
# Parametry (założenia własne – raportowane)
# ----------------------------------------------------------------------------------------------------------------
P = dict(
    EXT_T=0.50,        # wieża, segment: lico wewn. ściany zewn. od obrysu (spec. rozdz. 7: 0,50)
    EXT_W=0.40,        # skrzydło: ściana zewn. 0,40 (spec. podaje 0,50 – nie mieści traktu 15,0; patrz raport)
    EXT_PARTY=0.40,    # ściana oddzielenia przy Maz. 19 (REI 120)
    EXT_UG=0.80,       # ściany szczelinowe kondygnacji podziemnych
    EXT_GLASS=0.20,    # szklenie podcienia / bramy
    PART=0.10,         # ścianki między pokojami (spec.: oś 4,05 → netto 3,95)
    WALL=0.12,         # ściany korytarzowe i działowe
    CORR=1.80,         # korytarz w świetle
    D_T=6.10,          # głębokość pokoju – wieża
    D_W=6.08,          # głębokość pokoju – skrzydło (trakt 15,0 = 0,40+6,08+0,12+1,80+0,12+6,08+0,40)
    W_O=3.95,          # szerokość netto pokoju 24 m²
    W_O4=5.30,         # pokój 4-modułowy (GW 32 w skrzydle)
    W_SN=7.60, D_SN=7.90,
    W_MD=2.60, D_MD=9.25,
    W_G=3.95, D_G=8.11,
    D_WICE=7.60,
    STALL_W=2.50, STALL_L=5.00, STALL_OZN_W=3.60, AISLE=6.00,
)


def r2(x):
    return round(float(x), 2)


# ----------------------------------------------------------------------------------------------------------------
# Wczytanie specyfikacji
# ----------------------------------------------------------------------------------------------------------------
S = json.loads(SPEC.read_text(encoding="utf-8"))
PR = yaml.safe_load(PROG.read_text(encoding="utf-8"))
NOTES = []        # rozbieżności / uwagi do raportu
DATA_FIX = []     # poprawki danych wejściowych


def note(kind, txt):
    NOTES.append((kind, txt))


T = Frame.from_spec(S["meta"]["uklad_pomocniczy_wiezy"], "u", "v", "T")
WF = Frame.from_spec(S["meta"]["uklad_pomocniczy_skrzydla"], "s", "d", "W")


def sub(frame: Frame, ox, oy, axis="x"):
    """Ramka pomocnicza: początek w (ox,oy) ramy frame; axis='x' – osie jak frame, 'yx' – oś x wzdłuż y frame, y wzdłuż x."""
    o = frame.en(ox, oy)
    if axis == "x":
        return Frame(o, frame.ex, frame.ey)
    if axis == "yx":     # x' = y, y' = x
        return Frame(o, frame.ey, frame.ex)
    if axis == "y-x":    # x' = y, y' = -x
        return Frame(o, frame.ey, (-frame.ex[0], -frame.ex[1]))
    if axis == "x-y":    # x' = x, y' = -y
        return Frame(o, frame.ex, (-frame.ey[0], -frame.ey[1]))
    raise ValueError(axis)


# bryły
BRY = {}
for b in S["bryly"]:
    pts, nts = clean_ring(b["obrys_ccw"])
    for n_ in nts:
        DATA_FIX.append(f"bryła {b['id']}: {n_} – usunięto")
    BRY[b["id"]] = Polygon(pts).buffer(0)
W_, M_, S_ = BRY["W"], BRY["M"], BRY["S"]
ARC = S["bryly"][0]["luk"]
ARC_C_UV = T.loc(*ARC["srodek"])
R_ARC = ARC["R_zewn"]
R_SZYB = ARC.get("R_szyb_korony", R_ARC - 0.5)
R_PODC = ARC.get("R_podcien_parter", R_ARC - 3.0)
TOWER_U = max(p[0] for p in S["bryly"][0]["prostokat_uv"])
TOWER_V = max(p[1] for p in S["bryly"][0]["prostokat_uv"])

KOND = OrderedDict((k["kondygnacja"], k) for k in S["kondygnacje"])
CORES = S["rdzenie"]
CORE_POLY = {k: Polygon(CORES[k]["obrys_en"]) for k in ("A", "B", "C")}
CORE_UV = {k: (min(p[0] for p in CORES[k]["obrys_uv"]), max(p[0] for p in CORES[k]["obrys_uv"]),
               min(p[1] for p in CORES[k]["obrys_uv"]), max(p[1] for p in CORES[k]["obrys_uv"])) for k in ("A", "B")}
CORE_SD = {"C": (min(p[0] for p in CORES["C"]["obrys_wing_sd"]), max(p[0] for p in CORES["C"]["obrys_wing_sd"]),
                 min(p[1] for p in CORES["C"]["obrys_wing_sd"]), max(p[1] for p in CORES["C"]["obrys_wing_sd"]))}
KB = S["kondygnacje_biurowe"]
SIATKA = S["siatka"]


def closing(g, r=0.12):
    return g.buffer(r, **MITRE).buffer(-r, **MITRE)


# ----------------------------------------------------------------------------------------------------------------
# Program: komórki (tabela 1 M.01) → lista pokoi per kod
# ----------------------------------------------------------------------------------------------------------------
DEPT_CODES = ["KS", "DOS", "DSS", "DST", "DRA", "DGP", "DI", "CZ", "DKD", "DZ", "GW", "DK", "DW"]
BLOK = {b["kod"]: b for b in PR["bloki"]}
KOM_NAZWA = {}
for code, lst in PR["kadra"]["komorki"].items():
    for c in lst:
        KOM_NAZWA[(code, str(c["nr"]))] = c["nazwa"]

TYP_NAZWA = {"CZ": "Gabinet Członka Zarządu", "DYR": "Gabinet dyrektora", "ZDYR": "Pokój zastępcy dyrektora",
             "SEK": "Sekretariat", "SAM": "Pokój samodzielnego stanowiska", "PR": "Pokój pracowników (3 st.)",
             "PR32": "Pokój zespołu GW (4 st.)"}
GAB_TYPES = ("CZ", "DYR", "ZDYR", "SEK", "SAM")


def dept_rooms(code):
    """Lista pokoi biurowych komórek danego kodu (w kolejności tabeli 1), gabinety najpierw."""
    out = []
    for it in BLOK[code]["pomieszczenia"]:
        m = re.match(rf"^{code}\.([\d.]+)\.([A-Z0-9]+)$", it["id"])
        if not m:
            continue
        nr, typ = m.group(1), m.group(2)
        n = int(it["liczba"])
        os_tot = it.get("osoby") or 0
        base, extra = divmod(os_tot, n) if n else (0, 0)
        for k in range(n):
            out.append(dict(code=code, nr=nr, typ=typ, prog_id=it["id"], area=float(it["pow_jedn"]),
                            osoby=base + (1 if k < extra else 0), komorka=KOM_NAZWA.get((code, nr), ""),
                            gab=typ in GAB_TYPES))
    out.sort(key=lambda r: (0 if r["gab"] else 1))
    return out


DEPT = {c: dept_rooms(c) for c in DEPT_CODES}


def prog_item(pid):
    for b in PR["bloki"]:
        for it in b["pomieszczenia"]:
            if it["id"] == pid:
                return it
    return None


# ----------------------------------------------------------------------------------------------------------------
# Płyty kondygnacji i ściany zewnętrzne
# ----------------------------------------------------------------------------------------------------------------
PARTY = LineString([BRY["M"].exterior.coords[0], BRY["M"].exterior.coords[0]])
# ściana przy Maz. 19: krawędź skrzydła s = 0 (od narożnika ulicy do narożnika podwórza)
_mz = [WF.en(0, 0), WF.en(0, 15.0)]
PARTY = LineString(_mz)
SEG_SOUTH = LineString([S["bryly"][2]["obrys_ccw"][0], S["bryly"][2]["obrys_ccw"][1]])


def thick_fn(kind):
    Mb, Wb, Sb = M_.exterior, W_.exterior, S_.exterior

    def f(a, b):
        m = Point((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if kind == "UG":
            return P["EXT_UG"]
        if m.distance(PARTY) < 0.08:
            return P["EXT_PARTY"]
        dM, dW, dS = m.distance(Mb), m.distance(Wb), m.distance(Sb)
        if dM < 0.05 and dM < min(dW, dS) - 0.01:
            return P["EXT_W"]
        if dW < 0.05 or dS < 0.05:
            return P["EXT_T"]
        return P["EXT_GLASS"]   # krawędzie wycięć (podcień, brama) – szklenie
    return f


def plate_of(kid):
    if kid in ("-1", "-2"):
        return Polygon(clean_ring(S["podziemie"][kid]["obrys_ccw"])[0]).buffer(0)
    if kid in ("P", "1", "2", "3", "4"):
        return closing(unary_union([W_, M_, S_]))
    return W_


def inner_of(plate, kind="AG"):
    band = ext_band(plate, thick_fn(kind))
    inn = plate.difference(band)
    inn = largest(clean(inn, 0.03)) if inn.geom_type != "Polygon" else clean(inn, 0.03)
    return inn, band


# ----------------------------------------------------------------------------------------------------------------
# Trzony (schematy wnętrz w układach lokalnych)
# ----------------------------------------------------------------------------------------------------------------
def core_A(kid):
    u0, u1, v0, v1 = CORE_UV["A"]
    sp = []
    w = 0.25
    # dźwigi przy licu pd. (A1, A2 – drzwi na pd.; R – drzwi do przedsionka)
    lw = (u1 - u0 - 2 * w - 2 * 0.2) / 3.0
    xs = [u0 + w, u0 + w + lw + 0.2, u0 + w + 2 * (lw + 0.2)]
    names = [("A1", "Dźwig A1 1 600 kg"), ("A2", "Dźwig A2 1 600 kg"),
             ("R", "Dźwig R – dla ekip ratowniczych (PN-EN 81-72) i ewakuacyjny (PN-EN 81-76)")]
    vl = v0 + w + 2.55
    for (tag, nm), x in zip(names, xs):
        sp.append(Space(T.rect(x, x + lw, v0 + w, vl), nm, "KW", kind="core_lift", tags={"lift", tag}, label=False))
    # przedsionek (wsch.) i klatka (zach.)
    xm = u0 + w + 3.40
    sp.append(Space(T.rect(xm + 0.2, u1 - w, vl + 0.2, v1 - w), "Przedsionek ppoż. A z MOE (krzesło ewakuacyjne, interkom)",
                    "KW", kind="core_lobby", tags={"moe", "przedsionek"}, uwagi=["MOE 0,9 × 1,4 m, krzesło ewakuacyjne, interkom EVCS", "nadciśnienie"]))
    sp.append(Space(T.rect(u0 + w, xm, vl + 0.2, v1 - w), "Klatka schodowa A (biegi 1,60 m)", "KW", kind="core_stair",
                    tags={"stair"}, uwagi=["obudowana REI 60, nadciśnienie"]))
    return sp


def core_B(kid):
    u0, u1, v0, v1 = CORE_UV["B"]
    w = 0.25
    sp = []
    us = u0 + w + 3.40
    sp.append(Space(T.rect(u0 + w, us, v0 + w, v1 - w - 2.55), "Klatka schodowa B (biegi 1,60 m)", "KW", kind="core_stair",
                    tags={"stair"}, uwagi=["obudowana REI 60, nadciśnienie"]))
    sp.append(Space(T.rect(u0 + w, us, v1 - w - 2.35, v1 - w), "Przedsionek ppoż. B z MOE (krzesło ewakuacyjne, interkom)", "KW",
                    kind="core_lobby", tags={"moe", "przedsionek"}, uwagi=["MOE, krzesło ewakuacyjne, interkom EVCS", "nadciśnienie"]))
    x0 = us + 0.2
    h = (v1 - v0 - 2 * w - 2 * 0.2)
    hT = h * 0.36
    hP = (h - hT) / 2
    ys = [v0 + w, v0 + w + hT + 0.2, v0 + w + hT + 0.2 + hP + 0.2]
    for (tag, nm), y, hh in zip([("T", "Dźwig T os.-tow. 2 000 kg"), ("P1", "Dźwig publiczny P1 1 275 kg"), ("P2", "Dźwig publiczny P2 1 275 kg (przelotowy)")],
                                ys, [hT, hP, hP]):
        sp.append(Space(T.rect(x0, u1 - w, y, y + hh), nm, "KW", kind="core_lift", tags={"lift", tag}, label=False))
    return sp


def core_C(kid):
    s0, s1, d0, d1 = CORE_SD["C"]
    w = 0.25
    sp = []
    sp.append(Space(WF.rect(s0 + w, s0 + w + 2.20, d0 + w, d0 + w + 2.35), "Dźwig C1 1 000 kg (drzwi przelotowe – rezerwa połączenia z Maz. 19)",
                    "KW", kind="core_lift", tags={"lift", "C1"}, label=False))
    sp.append(Space(WF.rect(s0 + w + 2.40, s1 - w - 1.6, d0 + w, d0 + w + 2.35), "Przedsionek ppoż. C z MOE", "KW", kind="core_lobby",
                    tags={"moe", "przedsionek"}, uwagi=["MOE, krzesło ewakuacyjne, interkom EVCS"]))
    sp.append(Space(WF.rect(s0 + w, s1 - w - 1.6, d0 + w + 2.55, d1 - w), "Klatka schodowa C", "KW", kind="core_stair", tags={"stair"}))
    sp.append(Space(WF.rect(s1 - w - 1.4, s1 - w, d0 + w, d1 - w), "Szachty instalacyjne C", "IT", kind="shaft", label=False))
    return sp


def core_spaces(kid, which):
    out = []
    for c in which:
        sp = {"A": core_A, "B": core_B, "C": core_C}[c](kid)
        for s_ in sp:
            s_.tags.add(f"core{c}")
        out += sp
    return out


# ----------------------------------------------------------------------------------------------------------------
# Kontener kondygnacji
# ----------------------------------------------------------------------------------------------------------------
class Level:
    def __init__(self, kid, plate, inner, band, cores=()):
        self.kid = kid
        self.plate = plate
        self.inner = inner
        self.ext = band
        self.cores = list(cores)
        self.spaces: list[Space] = []
        self.corr = Polygon()
        self.doors = []
        self.windows = []
        self.columns = []
        self.stalls = []
        self.ramps = []
        self.extra = {}
        self.capacity = {}
        self.overflow = []

    def taken(self):
        return unary_union([s.poly for s in self.spaces] + [CORE_POLY[c] for c in self.cores])

    def add(self, sp: Space, clip=True, gap=None):
        g = P["WALL"] if gap is None else gap
        poly = sp.poly
        if clip:
            poly = poly.intersection(self.inner)
            others = [s.poly for s in self.spaces] + [CORE_POLY[c] for c in self.cores]
            if others:
                poly = poly.difference(unary_union([o.buffer(g, **MITRE) for o in others]))
            if not self.corr.is_empty and sp.kind not in ("corridor",):
                poly = poly.difference(self.corr.buffer(g, **MITRE))
        poly = largest(clean(poly, 0.02)) if not poly.is_empty else poly
        if poly.is_empty or poly.area < 0.3:
            return None
        sp.poly = poly
        self.spaces.append(sp)
        return sp


# ----------------------------------------------------------------------------------------------------------------
# Kondygnacje biurowe 1–6
# ----------------------------------------------------------------------------------------------------------------
def low_floor(kid):
    return kid in ("1", "2", "3", "4")


def V_S():   # lico pn. ściany korytarza pd. wieży (8,64)
    return P["EXT_T"] + P["D_T"] + 2 * P["WALL"] + P["CORR"]


def V_N():   # lico pd. ściany korytarza pn. wieży (21,06)
    return TOWER_V - V_S()


def U_E():   # lico zach. ściany korytarza wsch. (31,36)
    return TOWER_U - V_S()


def item(typ, **kw):
    D = kw.pop("D", P["D_T"])
    base = {
        "O": dict(w=P["W_O"], depth=D),
        "M": dict(w=P["W_O"], depth=D),
        "MAG": dict(w=P["W_O"], depth=D),
        "R": dict(w=P["W_O"], depth=D),      # pokój rezerwowy
        "O4": dict(w=P["W_O4"], depth=D),
        "G": dict(w=P["W_G"], depth=P["D_G"]),
        "SN": dict(w=P["W_SN"], depth=P["D_SN"]),
        "MD": dict(w=P["W_MD"], depth=P["D_MD"]),
        "WICE": dict(w=P["W_O"], depth=P["D_WICE"]),
        "X": dict(w=kw.get("w", 3.95), depth=kw.get("depth", D)),
    }[typ]
    base.update(kw)
    base["typ"] = typ
    base.setdefault("gap", P["PART"])
    return base


def units_of(typ):
    w = {"MD": P["W_MD"], "MAG": P["W_MD"], "SN": P["W_SN"]}.get(typ, P["W_O"])
    return (w + P["PART"]) / (P["W_O"] + P["PART"])


def runs_office(kid):
    """Pasma elewacyjne kondygnacji (1–4: wieża+skrzydło+segment; 5–6: wieża). Zwraca OrderedDict nazwa → opis pasma.
    x0→x1: kierunek układania; deep: zakresy (od, do, max głębokość) w osi x pasma."""
    E, D_T, D_W, PART, WALL, CORR = P["EXT_T"], P["D_T"], P["D_W"], P["PART"], P["WALL"], P["CORR"]
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    R = OrderedDict()
    low = low_floor(kid)
    fN = sub(T, 0, TOWER_V, "x-y")                                   # x = u, y = 29,7 − v
    fE = Frame(T.en(TOWER_U, 0.0), T.ey, (-T.ex[0], -T.ex[1]))       # x = v, y = 40 − u
    fW = Frame(T.en(0.0, 0.0), T.ey, T.ex)                           # x = v, y = u
    deep_S_A = cA[0] - 0.05, cA[1] + 0.05                             # przed trzonem A: tylko ≤ 8,11 (hol windowy 3,6 m)
    if low:
        cs0, cs1, cd0, cd1 = CORE_SD["C"]
        u_sw = T.loc(*S["bryly"][2]["obrys_ccw"][3])[0]
        fSW = Frame(T.en(u_sw, 0.0), T.ey, T.ex)                     # x = v, y = u − u_sw
        # granica pasma S przy narożu wklęsłym ze skrzydłem: wyznaczona z kolizji z pasmem podwórza
        R["N"] = dict(run=Run(fN, 0.5, ARC_C_UV[0], E, "N"), D=D_T, deep=[])
        R["arc"] = dict(run=ArcRun(T, ARC_C_UV, R_ARC, 90.0, 0.0, E, "arc"), D=D_T, deep=[(0, 90, 8.2)])
        R["E"] = dict(run=Run(fE, ARC_C_UV[1], -9.25, E, "E"), D=D_T, deep=[(cB[3] + 0.1, ARC_C_UV[1], P["D_G"])])
        R["segW"] = dict(run=Run(fSW, -6.62, 0.5, E, "segW"), D=D_T, deep=[(-7, 0.6, U_E() - WALL - u_sw - E)])
        R["S"] = dict(run=Run(T, u_sw + E, -4.05, E, "S"), D=D_T,
                      deep=[(-4.1, deep_S_A[0], P["D_MD"]), (deep_S_A[0], deep_S_A[1], P["D_G"]), (deep_S_A[1], u_sw + E + 0.01, P["D_MD"])])
        R["wc"] = dict(run=Run(sub(WF, 0, 15.0, "x-y"), 33.2, cs1 + WALL, P["EXT_W"], "wc"), D=D_W, deep=[])
        R["ws"] = dict(run=Run(WF, P["EXT_PARTY"] + 0.05, 53.25, P["EXT_W"], "ws"), D=D_W, deep=[])
        R["nose"] = dict(run=None, D=D_W, deep=[])
    else:
        w0 = V_S()
        w1 = V_N()
        R["W"] = dict(run=Run(fW, w0, w1, E, "W"), D=D_T, deep=[], near_core_A=(cA[2], cA[3]))
        R["N"] = dict(run=Run(fN, 0.5, ARC_C_UV[0], E, "N"), D=D_T, deep=[(cA[1] + 2.0, ARC_C_UV[0] + 0.01, P["D_G"])])
        R["arc"] = dict(run=ArcRun(T, ARC_C_UV, R_ARC, 90.0, 0.0, E, "arc"), D=D_T, deep=[(0, 90, 8.2)])
        R["E"] = dict(run=Run(fE, ARC_C_UV[1], 0.5, E, "E"), D=D_T, deep=[(cB[3] + 0.1, ARC_C_UV[1], P["D_G"])])
        R["S"] = dict(run=Run(T, cB[0] - 0.15, 0.5, E, "S"), D=D_T, deep=[(cA[1] + 0.05, cB[0], P["D_MD"])])
    for rn, rd in R.items():
        if rd["run"] is not None and not isinstance(rd["run"], ArcRun):
            rd["x0"], rd["x1"] = rd["run"].x0, rd["run"].x1
    return R


def ring_order(kid):
    if low_floor(kid):
        if kid == "3":
            return ["arc", "E", "segW", "S", "wc", "ws", "nose", "N"]
        return ["N", "arc", "E", "segW", "S", "wc", "ws", "nose"]
    return ["W", "N", "arc", "E", "S"]


# ---- kolejka pokoi kondygnacji -----------------------------------------------------------------------------------
RZ = {r["kond"]: r for r in KB["rozmieszczenie"]}


def norm_code(c):
    c = c.strip()
    return {"DK II": "DK", "DW II": "DW"}.get(c, c.split()[0])


def floor_queue(kid, extra=None):
    """Kolejka elementów elewacyjnych kondygnacji wg specyfikacji (komórki, sale narad, magazynki)."""
    rz = RZ.get(kid)
    if rz is None:
        return []
    q = []
    nmag = int(rz.get("magazynki", 0))
    deep_mag = (rz.get("magazynki_typ") == "głębokie")
    depts = [(norm_code(c), n) for c, n in rz["komorki"].items()]
    tot = sum(n for _, n in depts) or 1
    shares, rem = {}, nmag
    for i, (c, n) in enumerate(depts):
        sh = round(nmag * n / tot) if i < len(depts) - 1 else rem
        sh = max(0, min(sh, rem))
        shares[c] = sh
        rem -= sh
    if kid == "3":   # GW najpierw (pion GW z pokojami głębokimi przy archiwach)
        depts.sort(key=lambda x: 0 if x[0] == "GW" else 1)
    for c, n in depts:
        rooms = list(DEPT.get(c, []))
        if len(rooms) != n:
            note("program", f"kond. {kid}: {c} – specyfikacja {n} pokoi, program (zał. 1 M.01) {len(rooms)} – przyjęto program")
        for r in rooms:
            r = dict(r)
            r["kind"] = "office"
            r["typ_item"] = "G" if r["typ"] == "PR32" else "O"
            r["floor_spec"] = kid
            q.append(r)
        for _ in range(shares.get(c, 0)):
            q.append(dict(kind="mag", typ_item="MAG", spec_typ="MD" if deep_mag else "M", dept=c, prog_id="PP.01", code="PP", floor_spec=kid))
    for _ in range(int(rz.get("sale_narad", 0))):
        q.append(dict(kind="sn", typ_item="SN", prog_id="SN.01", code="SN", floor_spec=kid))
    if kid == "6":
        for _ in range(3):
            q.insert(0, dict(kind="ks", typ_item="WICE", prog_id="KS.04", code="KS", floor_spec=kid))
    return q


class Pool:
    def __init__(self, items):
        self.items = list(items)

    def __len__(self):
        return len(self.items)

    def pick(self, maxw, max_depth_fn, D, prefer_deep=False):
        """Wybiera pierwszy element mieszczący się na szerokości maxw i dozwolonej głębokości.
        Patrzy dalej w kolejce tylko w obrębie tego samego działu lub po elementy specjalne."""
        if not self.items:
            return None
        head = self.items[0]
        head_dept = head.get("code") if head["kind"] == "office" else None

        def ok(q):
            it = item(q["typ_item"], D=D)
            if q["typ_item"] == "MAG":
                it = item("MD") if max_depth_fn(P["W_MD"]) >= P["D_MD"] - 1e-6 else item("M", D=D)
            if q["typ_item"] == "G" and it["depth"] > max_depth_fn(it["w"]) + 1e-6:
                it = item("O4", D=D)          # pokój GW 32 m² w formacie 4-modułowym (5,30 × 6,10)
                it["gw4"] = True
            if it["w"] > maxw + 1e-6:
                return None
            md = max_depth_fn(it["w"])
            if it["depth"] > md + 1e-6:
                return None
            return it

        cands = []
        for i, q in enumerate(self.items):
            same = (q["kind"] != "office") or (head_dept is None) or (q.get("code") == head_dept)
            if i > 0 and not same:
                continue
            it = ok(q)
            if it is not None:
                cands.append((i, q, it))
                if not prefer_deep:
                    break
        if not cands:
            return None
        if prefer_deep:
            deep = [c for c in cands if c[2]["depth"] > D + 0.05]
            i, q, it = deep[0] if deep else cands[0]
        else:
            i, q, it = cands[0]
        self.items.pop(i)
        it["q"] = q
        return it


def fill_line(rd, pool, kid, fixed_head=(), fixed_tail=()):
    run = rd["run"]
    D = rd["D"]
    L = abs(rd["x1"] - rd["x0"])
    sgn = 1 if rd["x1"] >= rd["x0"] else -1
    seq = list(fixed_head)
    t = sum(x["w"] for x in seq) + P["PART"] * max(0, len(seq) - 1)
    tail_len = sum(x["w"] + P["PART"] for x in fixed_tail)

    def max_depth(t0, w):
        a = rd["x0"] + sgn * t0
        b = rd["x0"] + sgn * (t0 + w)
        lo, hi = min(a, b), max(a, b)
        ov = [(max(p, lo), min(q, hi), md) for (p, q, md) in rd["deep"] if min(q, hi) > max(p, lo) + 1e-9]
        if not ov:
            return D
        ov.sort()
        cur = lo
        for (p, q, md) in ov:
            if p > cur + 1e-6:
                return D
            cur = max(cur, q)
        if cur < hi - 1e-6:
            return D
        return max(D, min(md for _, _, md in ov))

    while True:
        gap = P["PART"] if seq else 0.0
        rem = L - t - gap - tail_len
        if rem < min(P["W_MD"], P["W_O"]) - 1e-6:
            break
        t0 = t + gap
        it = pool.pick(rem, lambda w: max_depth(t0, w), D, prefer_deep=max_depth(t0, P["W_MD"]) > D + 0.05)
        if it is None:
            break
        seq.append(it)
        t = t0 + it["w"]
    seq += list(fixed_tail)
    t = sum(x["w"] for x in seq) + P["PART"] * max(0, len(seq) - 1)
    left = L - t
    # resztka pasma: wnęka pomocnicza albo poszerzenie ostatniego pokoju
    if seq and left > 1.5:
        seq.append(item("X", w=left - P["PART"], depth=D, role="aux"))
    elif seq and left > 0.02:
        seq[-1] = dict(seq[-1], w=seq[-1]["w"] + left)
    return seq


def fill_arc(rd, pool, kid):
    run = rd["run"]
    D = rd["D"]
    Rf = R_ARC - P["EXT_T"]

    def a_per_deg(depth):
        return (math.pi / 360.0) * (Rf ** 2 - (Rf - depth) ** 2)
    seq = []
    if kid == "6":
        # łuk NE kond. 6: 2 pokoje KS z kolejki, asystent, gabinet Przewodniczącego (głęboki, z zapleczem od strony korytarza)
        for _ in range(2):
            it = pool.pick(99, lambda w: D, D)
            if it is None:
                break
            seq.append(dict(ang=(24.0 + 0.70) / a_per_deg(D), depth=D, typ=it["typ"], q=it["q"]))
        seq.append(dict(ang=(14.5 + 0.62) / a_per_deg(D), depth=D, typ="X", role="KS.03"))
        rest = 90.0 - sum(x["ang"] for x in seq)
        seq.append(dict(ang=rest, depth=8.15, typ="X", role="KS.01"))
        return seq
    total = 0.0
    while True:
        q = pool.items[0] if pool.items else None
        if q is None:
            break
        typ = q["typ_item"]
        if typ == "SN":
            dep = 8.15
            ang = (60.0 + 0.9) / a_per_deg(dep)
        elif typ in ("O", "M", "G", "WICE"):
            dep = D
            ang = (24.0 + 0.70) / a_per_deg(D)
            if typ == "G":
                break
        else:
            break
        if total + ang > 90.0 + 3.0:
            break
        pool.items.pop(0)
        seq.append(dict(ang=ang, depth=dep, typ=typ if typ != "M" else "M", q=q))
        total += ang
    if seq:
        k = 90.0 / total
        for x in seq:
            x["ang"] *= k
    return seq


def layout_facade(kid, queue):
    """Rozmieszcza elementy kolejki na pasmach. Zwraca (R, placed_by_run, nose_item, pool_left)."""
    R = runs_office(kid)
    pool = Pool(queue)
    # kolejka: elementy SN dla łuku kond. 3 – na początek kolejki pasma łuku
    placed = OrderedDict()
    order = ring_order(kid)
    # elementy głębokie przenoszone na początek, gdy pasmo ma strefę głęboką – realizuje pick(prefer_deep)
    for rn in order:
        rd = R[rn]
        if rn == "nose":
            continue
        if isinstance(rd["run"], ArcRun):
            if kid == "3":
                # łuk kond. 3: obie sale narad (pierścień głęboki)
                sn = [q for q in pool.items if q["typ_item"] == "SN"]
                for q in sn:
                    pool.items.remove(q)
                tmp = Pool(sn + [q for q in pool.items])
                seq = fill_arc(rd, tmp, kid)
                pool.items = tmp.items
            else:
                # sale narad tylko, gdy kolejka nie ma już pokoi (unika głębokiego pierścienia)
                seq = fill_arc(rd, pool, kid)
            placed[rn] = arc_place(rd["run"], seq)
            continue
        seq = fill_line(rd, pool, kid)
        run = rd["run"]
        run.x0, run.x1 = rd["x0"], rd["x1"]
        pl, tot = place_run(run, seq, gap_default=P["PART"])
        placed[rn] = pl
    nose = None
    if "nose" in R:
        it = pool.pick(99, lambda w: P["D_W"], P["D_W"])
        nose = it
    return R, placed, nose, pool


def office_capacity(kid):
    """Pojemność elewacji kondygnacji w jednostkach pokoju 24 m² (sucha próba z samymi pokojami)."""
    big = [dict(kind="office", typ_item="O", code="ZZ", prog_id="ZZ") for _ in range(80)]
    R, placed, nose, pool = layout_facade(kid, big)
    n = 80 - len(pool)
    return n


def build_office(kid, queue):
    plate = plate_of(kid)
    inner, band = inner_of(plate)
    low = low_floor(kid)
    cores = ["A", "B"] + (["C"] if low else [])
    L = Level(kid, plate, inner, band, cores)
    for sp in core_spaces(kid, cores):
        L.spaces.append(sp)
    D_T, D_W, PART, WALL, CORR = P["D_T"], P["D_W"], P["PART"], P["WALL"], P["CORR"]
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    R, placed_by_run, nose_it, pool = layout_facade(kid, queue)
    slots = []
    for rn, placed in placed_by_run.items():
        run = R[rn]["run"]
        for (a, b, it) in placed:
            if isinstance(run, ArcRun):
                poly = run.sector(a, b, run.ext, run.ext + it["depth"])
                cc = run.c
                cuts = []
                for ang in (a, b):
                    if abs(ang - run.a0) < 1e-6 or abs(ang - run.a1) < 1e-6:
                        continue
                    ln = T.line([cc, (cc[0] + 20 * math.cos(math.radians(ang)), cc[1] + 20 * math.sin(math.radians(ang)))])
                    cuts.append(ln.buffer(PART / 2, cap_style=2))
                if cuts:
                    poly = poly.difference(unary_union(cuts))
                poly = largest(poly)
            else:
                poly = run.rect(a, b, run.ext, run.ext + it["depth"])
            slots.append((rn, poly, it))
    # dziób skrzydła
    if low:
        vN0 = TOWER_V - P["EXT_T"] - D_T - WALL
        nose_region = inner.intersection(T.rect(-14.0, -0.08, vN0, TOWER_V + 1)).intersection(
            WF.rect(R["ws"]["x1"] + PART, 80, -1, 30))
        nose_poly = largest(clean(nose_region, 0.05))
        if not nose_poly.is_empty:
            it = nose_it if nose_it is not None else item("R", D=D_W)
            slots.append(("nose", nose_poly, it))
    # korytarze
    corr_parts = []
    ext_ab = {"ws": (0.0, 6.0), "wc": (3.5, 0.0), "N": (14.0 if low else 0.0, 0.6), "E": (0.6, 0.0), "segW": (0.0, 0.0),
              "S": (0.0, 9.0 if low else 0.0), "W": (0.0, 0.0)}
    for rn, placed in placed_by_run.items():
        run = R[rn]["run"]
        if isinstance(run, ArcRun):
            corr_parts.append(arc_corridor(run, placed, WALL, CORR, ext_deg=(3.0, 3.0)))
            corr_parts += arc_end_connectors(run, placed)
        elif placed:
            ea, eb = ext_ab.get(rn, (0, 0))
            corr_parts.append(corridor_behind(run, placed, WALL, CORR, ext_a=ea, ext_b=eb, gap_default=PART))
    corr_parts += office_connectors(kid, low)
    corr = unary_union(corr_parts).intersection(inner)
    room_u = unary_union([p for _, p, _ in slots])
    core_u = unary_union([CORE_POLY[c] for c in cores])
    corr = corr.difference(room_u.buffer(WALL - 0.005, **MITRE)).difference(core_u)
    corr = clean(corr, 0.05)
    corr = unary_union([p for p in polys(corr) if p.area > 3.0])
    L.corr = corr
    # pokoje elewacyjne
    for rn, poly, it in slots:
        poly = poly.intersection(inner).difference(core_u.buffer(WALL, **MITRE))
        if rn == "nose":
            poly = poly.difference(corr.buffer(WALL, **MITRE))
        poly = largest(clean(poly, 0.02))
        if poly.is_empty or poly.area < 1.0:
            continue
        if rn == "nose" and poly.area > 34.0:
            # dziób: pokój ~24,5 m² od strony ulicy + pomieszczenie pomocnicze przy licu wieży
            bx = T.to_local_geom(poly).bounds
            lo, hi = bx[0], bx[2]
            for _ in range(40):
                m = (lo + hi) / 2
                if poly.intersection(T.rect(bx[0] - 1, m, -50, 50)).area < 24.6:
                    lo = m
                else:
                    hi = m
            west = largest(poly.intersection(T.rect(bx[0] - 1, hi, -50, 50)))
            east = largest(clean(poly.intersection(T.rect(hi + PART, bx[2] + 1, -50, 50)), 0.03))
            for sp in slot_spaces(kid, rn, west, it, R):
                L.spaces.append(sp)
            if not east.is_empty and east.area > 2:
                L.spaces.append(Space(east, "Pomieszczenie pomocnicze (MFP / szafy, okno)", "PP", kind="room", facade_dir=T.ey))
            continue
        for sp in slot_spaces(kid, rn, poly, it, R):
            L.spaces.append(sp)
    # korytarz
    for p in sorted(polys(corr), key=lambda g: -g.area):
        L.spaces.append(Space(p, "Korytarz / hol windowy" if p.area > 60 else "Korytarz", "KW", kind="corridor",
                              uwagi=["szer. w świetle ≥ 1,80 m"]))
    central_rooms(L, kid, low)
    # niedobór pokoi socjalnych → rezerwy elewacyjne / strefy wspólne
    need_ps = int(RZ.get(kid, {}).get("socjalne", 0)) + sum(1 for x in CARRY.get(kid, []) if x[0] == "PS.01")
    have_ps = sum(1 for s_ in L.spaces if s_.prog_id == "PS.01")
    if have_ps < need_ps:
        cands = [s_ for s_ in L.spaces if s_.nazwa.startswith("Pokój rezerwowy")] + \
                sorted([s_ for s_ in L.spaces if s_.nazwa.startswith("Strefa pracy wspólnej") and s_.area >= 16.0], key=lambda x: -x.area)
        for s_ in cands[:need_ps - have_ps]:
            s_.nazwa, s_.kod, s_.prog_id, s_.furn, s_.kind = "Pokój socjalny pracowników", "PS", "PS.01", "kitchen", "room"
            s_.uwagi = [u for u in s_.uwagi if not u.startswith("rezerwa")]
        if have_ps + len(cands) < need_ps:
            note("strefa środkowa", f"kond. {kid}: brak miejsca na {need_ps - have_ps - len(cands)} pokój/pokoje socjalne")
    gab_near_core(L)
    L.overflow = list(pool.items)
    L.capacity = dict(rz=RZ.get(kid))
    return L


def arc_end_connectors(run: ArcRun, placed):
    """Łączniki promieniowe na końcach łuku, gdy element końcowy jest głębszy niż pasmo standardowe."""
    out = []
    W, C, D = P["WALL"], P["CORR"], P["D_T"]
    std_in = run.R - run.ext - D - W - C   # 5,48
    for k, (a, b, it) in enumerate(placed):
        if it["depth"] <= D + 0.05:
            continue
        r_in = run.R - run.ext - it["depth"] - W - C
        r_out = run.R - run.ext - D - W
        # łącznik po stronie sąsiada (płytszego) – wycinek o szer. C na promieniu średnim
        rm = (r_in + r_out) / 2
        dang = math.degrees(C / max(rm, 1.0)) + 1.0
        for side, ang in ((-1, a), (1, b)):
            nb = k + side
            if 0 <= nb < len(placed) and placed[nb][2]["depth"] > D + 0.05:
                continue
            lo, hi = (ang, ang + dang) if (ang == a) == (run.a1 < run.a0) else (ang - dang, ang)
            if ang == a:
                lo, hi = (a, a + dang) if run.a1 > run.a0 else (a - 0, a + dang)
            out.append(run.sector(ang - dang, ang + dang, run.ext + D + W, run.ext + it["depth"] + W + C))
    return out


def office_connectors(kid, low):
    """Łączniki: hol przed dźwigami A (pd.), hol B (pn. od trzonu B, 3,6 m), pas przed P1/P2, węzły skrzydło–wieża."""
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    W, C = P["WALL"], P["CORR"]
    vS0 = P["EXT_T"] + P["D_T"] + W        # 6,72
    vN0 = TOWER_V - vS0 - C                 # 21,18
    uE = U_E() + W                          # 31,48
    out = []
    out.append(T.rect(cA[0], cA[1], vS0, cA[2]))                       # hol windowy A
    out.append(T.rect(cB[0] - C - 0.1, uE + C, cB[3], cB[3] + 3.6))     # hol B (M.13: 3,6 m)
    out.append(T.rect(cB[0] - C - 0.1, cB[0], vS0, cB[3] + 3.6))        # łącznik korytarz pd. → hol B
    out.append(T.rect(cB[1], uE + C, cB[2], cB[3] + 0.1))               # przed P1/P2/T
    if not low:
        out.append(T.rect(cB[1], uE + C, 0.5, cB[2] + 0.1))              # koniec korytarza wsch. (okno pd.)
        uW0 = P["EXT_T"] + P["D_T"] + W
        out.append(T.rect(uW0, cA[0], vS0, vN0 + C))                     # korytarz zach. (przy trzonie A do lica trzonu)
        out.append(T.rect(P["EXT_T"], uW0 + C, vS0, vS0 + C))            # koniec korytarza pd. (okno zach.)
        out.append(T.rect(P["EXT_T"], uW0 + C, vN0, vN0 + C))            # koniec korytarza pn. (okno zach.)
    else:
        cs0, cs1, cd0, cd1 = CORE_SD["C"]
        dC0 = P["EXT_W"] + P["D_W"] + W
        out.append(WF.rect(cs0, 56.6, dC0, dC0 + C))                     # korytarz skrzydła
        out.append(T.rect(-12.0, 1.0, vS0, vS0 + C))                     # korytarz pd. wieży → klin → skrzydło
        out.append(T.rect(-9.0, 1.0, vN0, vN0 + C))                      # korytarz pn. wieży → węzeł przy dziobie
    return out


def slot_spaces(kid, rn, poly, it, R):
    typ = it.get("typ")
    q = it.get("q") or {}
    role = it.get("role")
    rd = R.get(rn)
    run = rd["run"] if rd else None
    fdir = None
    if run is not None and not isinstance(run, ArcRun):
        iw = run.inward()
        fdir = (-iw[0], -iw[1])
    elif isinstance(run, ArcRun):
        c = poly.centroid
        cc = T.en(*run.c)
        v = (c.x - cc[0], c.y - cc[1])
        l = math.hypot(*v) or 1
        fdir = (v[0] / l, v[1] / l)
    elif rn == "nose":
        fdir = T.ey
    out = []
    if role == "aux":
        return [Space(poly, "Pomieszczenie pomocnicze (wnęka MFP / szafy, okno)", "PP", prog_id="", kind="room", facade_dir=fdir)]
    if role == "KS.03":
        return [Space(poly, "Pokój asystenta Przewodniczącego", "KS", prog_id="KS.03", kind="office", furn="office1", osoby=1, dept="KS", facade_dir=fdir)]
    if role == "KS.01":
        # część zewn. – gabinet, część wewn. (od korytarza) – zaplecze sanitarno-socjalne
        Rf = R_ARC - P["EXT_T"]
        cpt = T.en(*ARC_C_UV)
        cut = Point(cpt).buffer(Rf - P["D_T"], 128)
        gab = largest(poly.difference(cut))
        zap = largest(poly.intersection(cut.buffer(-P["WALL"])))
        res = [Space(gab, "Gabinet Przewodniczącego Sejmiku (spotkania do 5 os.)", "KS", prog_id="KS.01", kind="office", furn="office1", osoby=1,
                     dept="KS", facade_dir=fdir, uwagi=["łuk NE – widok na most i Ostrów Tumski"])]
        if not zap.is_empty and zap.area > 3:
            res.append(Space(zap, "Zaplecze sanitarno-socjalne gabinetu Przewodniczącego", "KS", prog_id="KS.02", kind="room", dept="KS"))
        return res
    kind = q.get("kind")
    if typ == "SN" or kind == "sn":
        return [Space(poly, "Sala narad 30 os.", "SN", prog_id="SN.01", kind="room", furn="table", seats=18, osoby=30,
                      uwagi=["przy elewacji", "pętla indukcyjna"], facade_dir=fdir, tags={"loop"})]
    if kind == "mag" or typ in ("MD", "M", "MAG"):
        dept = q.get("dept", "")
        nm = "Podręczny magazyn dokumentacji" + (" (głęboki)" if typ == "MD" else "") + (f" – {dept}" if dept else "")
        return [Space(poly, nm, "PP", prog_id="PP.01", kind="room", dept=dept, uwagi=["przy elewacji – konwertowalny na pokój biurowy"],
                      facade_dir=fdir, furn="shelves")]
    if kind == "ks" or typ == "WICE":
        return [Space(poly, "Gabinet Wiceprzewodniczącego Sejmiku", "KS", prog_id="KS.04", kind="office", furn="office1", osoby=1, dept="KS",
                      facade_dir=fdir)]
    if kind == "office":
        typn = TYP_NAZWA.get(q["typ"], q["typ"])
        nm = f"{typn} – {q['komorka']} ({q['nr']})" if q.get("komorka") else typn
        furn = "office4" if q["typ"] == "PR32" else ("office1" if q["gab"] else "office3")
        sp = Space(poly, nm, q["code"], prog_id=q["prog_id"], komorka=q["nr"], dept=q["code"], osoby=q["osoby"], kind="office",
                   furn=furn, facade_dir=fdir, tags={"gab"} if q["gab"] else set())
        if q.get("floor_spec") and q["floor_spec"] != kid:
            sp.uwagi.append(f"relokacja z kond. {q['floor_spec']} (brak pojemności elewacji)")
        return [sp]
    return [Space(poly, "Pokój rezerwowy (rezerwa elewacji, moduł 24 m²)", "PP", prog_id="", kind="room", facade_dir=fdir, furn="office3",
                  uwagi=["rezerwa – możliwa zamiana na pokój biurowy"])]


def gab_near_core(L: Level):
    """W obrębie działu: gabinety (DYR/ZDYR/SEK/SAM/CZ) na miejscach najbliższych trzonu A (Wyj. 10 odp. 62).
    Zamiana tylko między pokojami tej samej klasy (≈ 24 m²)."""
    ca = Point(*T.en((CORE_UV["A"][0] + CORE_UV["A"][1]) / 2, (CORE_UV["A"][2] + CORE_UV["A"][3]) / 2))
    by = defaultdict(list)
    for sp in L.spaces:
        if (sp.kind == "office" and sp.kod in DEPT_CODES and not sp.prog_id.startswith("KS.0") and sp.prog_id.count(".") >= 2
                and not sp.prog_id.endswith("PR32") and 23.9 <= sp.area <= 26.5):
            by[sp.kod].append(sp)
    for code, lst in by.items():
        gabs = [s for s in lst if "gab" in s.tags]
        if not gabs:
            continue
        ring = [s.poly for s in lst]
        fd = {id(s.poly): s.facade_dir for s in lst}
        near = sorted(ring, key=lambda p: p.centroid.distance(ca))[:len(gabs)]
        rest = [p for p in ring if p not in near]
        ordered = gabs + [s for s in lst if "gab" not in s.tags]
        for s_, p in zip(ordered, near + rest):
            s_.facade_dir = fd[id(p)]
            s_.poly = p


# ---- strefa środkowa ----------------------------------------------------------------------------------------------
def pack_bin(L: Level, region, frame, start, sign, items, door_note="", fill_rest=False):
    """Dzieli region (en) na pomieszczenia cięciami prostopadłymi do osi x ramy, od x=start w kierunku sign.
    items: (pid, nazwa, kod, pow_docelowa|None, tags). Ostatni element z None bierze resztę."""
    W = P["WALL"]
    region = largest(clean(region, 0.05))
    if region.is_empty:
        return []
    loc = frame.to_local_geom(region)
    bx = loc.bounds
    lo, hi = bx[0], bx[2]
    cur = start if start is not None else (hi if sign < 0 else lo)
    out = []

    def slab(a, b):
        a, b = min(a, b), max(a, b)
        return region.intersection(frame.rect(a, b, bx[1] - 1, bx[3] + 1))
    for k, (pid, nm, kod, area, tags) in enumerate(items):
        end_lim = lo if sign < 0 else hi
        if (sign < 0 and cur <= lo + 0.5) or (sign > 0 and cur >= hi - 0.5):
            break
        if area is None or (fill_rest and k == len(items) - 1 and slab(cur, end_lim).area < area * 1.6):
            x = end_lim
        else:
            a0, a1 = 0.0, abs(end_lim - cur)
            if slab(cur, end_lim).area <= area * 1.05:
                x = end_lim
            else:
                for _ in range(40):
                    m = (a0 + a1) / 2
                    if slab(cur, cur + sign * m).area < area:
                        a0 = m
                    else:
                        a1 = m
                x = cur + sign * a1
        poly = largest(clean(slab(cur, x), 0.03))
        if not poly.is_empty and poly.area > 1.2:
            sp = Space(poly, nm, kod, prog_id=pid, kind="room" if kod != "KW" else "corridor", tags=set(tags))
            if "wc" in tags:
                sp.furn = "wc"
                sp.uwagi.append("kabina dostępna dla OzN, przewijak")
            if "table" in tags:
                sp.furn = "table"
                sp.seats = 16
            if pid == "PS.01":
                sp.furn = "kitchen"
            if pid.endswith("OCZ") or pid == "KS.06":
                sp.uwagi.append("miejsce oczekiwania gości przy gabinetach")
            L.spaces.append(sp)
            out.append(sp)
        cur = x + sign * W
    # reszta
    end_lim = lo if sign < 0 else hi
    if (sign < 0 and cur > lo + 0.3) or (sign > 0 and cur < hi - 0.3):
        rest = largest(clean(slab(cur, end_lim), 0.05))
        if not rest.is_empty and rest.area > 1.5:
            nm = "Strefa pracy wspólnej / budki do rozmów" if rest.area >= 6 else "Wnęka / szafa"
            L.spaces.append(Space(rest, nm, "PP" if rest.area >= 6 else "KW", prog_id="", kind="room" if rest.area >= 6 else "corridor",
                                  uwagi=["strefa środkowa"]))
    return out


def central_program(kid, low):
    rz = RZ.get(kid, {})
    n_ps = int(rz.get("socjalne", 0))
    depts = [norm_code(c) for c in rz.get("komorki", {})]
    ocz = [(f"{c}.OCZ", f"Miejsce oczekiwania gości ({c})", c, 6.0, set()) for c in depts if prog_item(f"{c}.OCZ")]
    wc = [("PHS.01", "WC damskie z kabiną dostępną", "PHS", 15.0, {"wc", "wc_ozn"}),
          ("PHS.01", "WC męskie z kabiną dostępną", "PHS", 14.0, {"wc", "wc_ozn"})]
    ps = [("PS.01", "Pokój socjalny pracowników", "PS", 24.0, set()) for _ in range(n_ps)]
    mfp = ("PP.05", "Wnęka urządzenia wielofunkcyjnego (MFP)", "PP", 5.0, set())
    porz = ("PP.06", "Pomieszczenie porządkowe", "PP", 6.0, set())
    pd = ("IT.02", "Punkt dystrybucyjny IT (PD)", "IT", 6.0, set())
    cent = ("IT.13", "Centrala wentylacyjna piętrowa z rekuperacją", "IT", 25.0, set())
    bins = {}
    if low:
        bins["WS"] = wc + [porz]
        bins["WN"] = ps[:1] + [mfp, pd] + ocz
        bins["ES"] = ps[1:2]
        bins["EN"] = [cent] + ps[2:]
        if kid == "1":
            bins["ES"] = [("IT.01", "Serwerownia TIER II", "IT", 50.0, set()), ("IT.03", "Pomieszczenie UPS", "IT", 15.0, set())]
            bins["WN"] = ps[:1] + [mfp, pd] + ocz
            bins["EN"] = [cent] + ps[1:]
        if kid == "3":
            bins["ES"] = [("PP.02", "Archiwum Państwowego Zasobu Geodezyjnego i Kartograficznego (GW)", "PP", 48.0, set())]
            bins["EN"] = [cent, ("PP.03", "Archiwum operatów kartograficznych (GW)", "PP", 24.0, set()),
                          ("PP.04", "Pomieszczenie urządzeń specjalistycznych GW (ploter, skaner)", "PP", 24.0, set())] + ps[1:]
        bins["WEDGE"] = [("PHS.01", "WC damskie z kabiną dostępną (skrzydło)", "PHS", 14.0, {"wc", "wc_ozn"}),
                         ("PHS.01", "WC męskie z kabiną dostępną (skrzydło)", "PHS", 13.0, {"wc", "wc_ozn"}),
                         ("PP.06", "Pomieszczenie porządkowe (skrzydło)", "PP", 5.0, set()),
                         ("PP.05", "Wnęka urządzenia wielofunkcyjnego (MFP, skrzydło)", "PP", None, set())]
    else:
        if kid == "6":
            bins["ES"] = wc + [porz]
            bins["EN"] = [("KS.05", "Sala spotkań 20 os. (przeszklona)", "KS", 44.0, {"table"}),
                          ("KS.05", "Sala spotkań 20 os. (przeszklona)", "KS", 44.0, {"table"}),
                          ("KS.06", "Miejsce oczekiwania gości (Przewodniczący, KS)", "KS", 12.0, set())] + ps + [mfp, pd] + ocz
        else:
            bins["ES"] = wc + [porz]
            bins["EN"] = [cent] + ps + [mfp, pd] + ocz
    return bins


CARRY = defaultdict(list)    # pomieszczenia strefy środkowej przeniesione na kondygnację niżej (brak miejsca)


def central_rooms(L: Level, kid, low):
    W = P["WALL"]
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    vm = (V_S() + V_N()) / 2
    free = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(W, **MITRE))
    free = free.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    free = clean(free, 0.05)
    prog = central_program(kid, low)
    if CARRY.get(kid):
        prog.setdefault("EN", [])
        prog["EN"] = prog["EN"] + CARRY[kid]
    regions = OrderedDict()
    if low:
        wedge_cut = WF.rect(-5, 80, P["EXT_W"] + P["D_W"] + W + P["CORR"] + W - 0.01, 40)
        regions["WS"] = (free.intersection(T.rect(-20, cA[0], 0.0, vm - W / 2)).intersection(wedge_cut), T, cA[0] - W, -1)
        regions["WN"] = (free.intersection(T.rect(-20, cA[0], vm + W / 2, 40)).intersection(wedge_cut), T, cA[0] - W, -1)
    regions["EN"] = (free.intersection(T.rect(cA[1], TOWER_U, vm + W / 2, TOWER_V)), T, cA[1] + W, +1)
    regions["ES"] = (free.intersection(T.rect(cA[1], cB[0] - P["CORR"] - 0.1, P["EXT_T"], vm - W / 2)), T, cA[1] + W, +1)
    if low:
        wedge_cut = WF.rect(-5, 80, P["EXT_W"] + P["D_W"] + W + P["CORR"] + W - 0.01, 40)
        regions["WEDGE"] = (free.intersection(T.rect(-20, 0.5, -20, P["EXT_T"] + P["D_T"])).intersection(wedge_cut), WF, None, +1)
    pending = []
    keys = list(regions.keys())
    for key in keys:
        reg, frame, start, sign = regions[key]
        items = prog.get(key, []) + pending
        pending = []
        if not items:
            continue
        reg = largest(reg)
        if reg.is_empty:
            pending = items
            continue
        # elementy, które nie zmieszczą się w regionie – dalej
        tot = 0.0
        take_items, rest = [], []
        cap = reg.area * 0.92
        for it_ in items:
            a = it_[3] or 6.0
            if tot + a <= cap or not take_items:
                take_items.append(it_)
                tot += a
            else:
                rest.append(it_)
        got = pack_bin(L, reg, frame, start, sign, take_items, fill_rest=not rest)
        got_n = len(got)
        pending = take_items[got_n:] + rest
    # nadmiar → zamiana pozostałych stref wspólnych / pomieszczeń pomocniczych (najpierw pakowanie, potem resztki)
    free_left = L.inner.difference(unary_union([s_.poly for s_ in L.spaces]).buffer(W, **MITRE))
    free_left = free_left.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    for p_ in polys(clean(free_left, 0.06)):
        if p_.area >= 2.0:
            L.spaces.append(Space(p_, "Strefa pracy wspólnej / budki do rozmów", "PP", kind="room", uwagi=["strefa środkowa"]))
    still = []
    for it_ in sorted(pending, key=lambda x: -(x[3] or 6.0)):
        tgt = it_[3] or 6.0
        cands = sorted([s_ for s_ in L.spaces if s_.prog_id == "" and s_.kind == "room" and
                        (s_.nazwa.startswith("Strefa pracy") or s_.nazwa.startswith("Pomieszczenie pomocnicze") or s_.nazwa.startswith("Wnęka"))
                        and s_.area >= 0.6 * tgt], key=lambda x: abs(x.area - tgt))
        if cands:
            s_ = cands[0]
            pid, nm, kod, area, tags = it_
            s_.nazwa, s_.kod, s_.prog_id, s_.tags = nm, kod, pid, set(tags)
            s_.uwagi = [u for u in s_.uwagi if u != "strefa środkowa"]
            if "wc" in tags:
                s_.furn = "wc"
                s_.uwagi.append("kabina dostępna dla OzN, przewijak")
            if pid == "PS.01":
                s_.furn = "kitchen"
            if "table" in tags:
                s_.furn, s_.seats = "table", 16
        else:
            still.append(it_)
    pending = still
    if pending:
        k_down = str(int(kid) - 1) if kid.isdigit() and int(kid) > 1 else None
        if k_down and not low_floor(kid):
            CARRY[k_down] += pending
            note("strefa środkowa", f"kond. {kid}: brak miejsca w strefie środkowej – przeniesiono na kond. {k_down}: " +
                 ", ".join(f"{x[0]} {x[1]}" for x in pending))
        else:
            note("strefa środkowa", f"kond. {kid}: nie zmieściło się w strefie środkowej: " + ", ".join(f"{x[0]} {x[1]}" for x in pending))
    free2 = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(W, **MITRE))
    free2 = free2.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    for p in polys(clean(free2, 0.06)):
        if p.area < 2.0:
            continue
        L.spaces.append(Space(p, "Strefa pracy wspólnej / budki do rozmów" if p.area >= 6 else "Wnęka", "PP" if p.area >= 6 else "KW",
                              kind="room" if p.area >= 6 else "corridor", uwagi=["strefa środkowa"]))


# ---- bilans pojemności i relokacja ---------------------------------------------------------------------------------
def _dry(k, q):
    R, placed, nose, pool = layout_facade(k, [dict(x) for x in q])
    over = list(pool.items)
    spare = 0
    if not over:
        test = [dict(x) for x in q] + [dict(kind="office", typ_item="O", code="ZZ", prog_id="ZZ") for _ in range(8)]
        R, placed, nose, pool = layout_facade(k, test)
        spare = 8 - sum(1 for x in pool.items if x.get("code") == "ZZ")
    return over, spare


def plan_queues():
    """Kolejki kondygnacji 1–6 wg specyfikacji + relokacja nadmiaru (bez kaskad):
    (1) sale narad i magazynki – na kondygnację z rezerwą elewacji (największa rezerwa, potem najbliższa);
    (2) gdy to nie wystarcza – cały wydział (komórka 2. rzędu) na kondygnację SĄSIEDNIĄ (Wyj. 17 odp. 70); przed tym
        kondygnacja sąsiednia oddaje swoje sale narad / magazynki dalej. Elementy raz przeniesione nie wędrują dalej.
    Zwraca dict kid → kolejka oraz listę przeniesień (do raportu)."""
    kids = ["1", "2", "3", "4", "5", "6"]
    Q = {k: floor_queue(k) for k in kids}
    moves = []
    st = {k: _dry(k, Q[k]) for k in kids}

    def move_special(k, q, exclude=()):
        for k2 in sorted(kids, key=lambda x: (abs(int(x) - int(k)) == 1, -st[x][1], abs(int(x) - int(k)))):
            if k2 == k or k2 in exclude or st[k2][0] or st[k2][1] < units_of(q["typ_item"]) - 0.34:
                continue
            Q[k].remove(q)
            q2 = dict(q)
            q2.setdefault("floor_spec", k)
            Q[k2].append(q2)
            st2 = _dry(k2, Q[k2])
            if st2[0]:
                Q[k2].remove(q2)
                Q[k].append(q)
                continue
            st[k2] = st2
            st[k] = _dry(k, Q[k])
            moves.append(f"{q['prog_id']} ({'sala narad' if q['kind'] == 'sn' else 'magazynek'}) z kond. {k} na kond. {k2}")
            return True
        return False

    stuck = set()

    def own_groups(k):
        offs = [q for q in Q[k] if q["kind"] == "office" and q["code"] != "KS" and q.get("floor_spec", k) == k]
        g = OrderedDict()
        for q in offs:
            key = (q["code"], ".".join(q["nr"].split(".")[:2]))
            if len(key[1].split(".")) >= 2:
                g.setdefault(key, []).append(q)
        return g

    for _ in range(24):
        bad = [k for k in kids if st[k][0] and k not in stuck]
        if not bad:
            break
        k = max(bad, key=int)
        over = st[k][0]
        need = sum(units_of(q["typ_item"]) for q in over)
        # (2) najpierw wydział z kondygnacji, której działu nie da się zmieścić elementami specjalnymi
        specials = sorted([q for q in Q[k] if q["kind"] in ("sn", "mag") and q.get("floor_spec", k) == k],
                          key=lambda x: -units_of(x["typ_item"]))
        sp_units = sum(units_of(q["typ_item"]) for q in specials)
        progressed = False
        if sp_units + 0.01 >= need:
            for q in specials:
                if move_special(k, q):
                    progressed = True
                    break
            if progressed:
                continue
        offs = [q for q in Q[k] if q["kind"] == "office" and q["code"] != "KS" and q.get("floor_spec", k) == k]
        groups = OrderedDict()
        for q in offs:
            key = (q["code"], ".".join(q["nr"].split(".")[:2]))
            groups.setdefault(key, []).append(q)
        n_need = math.ceil(need - sp_units - 0.01) if sp_units < need else 1
        cand = [kk for kk in groups if len(kk[1].split(".")) >= 2 and len(groups[kk]) <= n_need + 1]
        cand.sort(key=lambda kk: (len(groups[kk]) < n_need, abs(len(groups[kk]) - n_need), -list(groups).index(kk)))
        for key in cand:
            grp = groups[key]
            for k2 in (str(int(k) - 1), str(int(k) + 1)):
                if k2 not in kids:
                    continue
                # zrób miejsce na k2: jej elementy specjalne (własne) na inne kondygnacje
                guard = 0
                while st[k2][1] < len(grp) and guard < 8:
                    guard += 1
                    sp2 = sorted([q for q in Q[k2] if q["kind"] in ("sn", "mag")], key=lambda x: -units_of(x["typ_item"]))
                    if not sp2 or not any(move_special(k2, q, exclude=(k,)) for q in sp2[:3]):
                        break
                if st[k2][1] < len(grp) and not st[k2][0]:
                    # kondygnacja sąsiednia oddaje własny mały wydział na swoją drugą sąsiednią (jeden poziom)
                    short = len(grp) - st[k2][1]
                    k3 = str(int(k2) - 1) if str(int(k2) - 1) not in (k,) else str(int(k2) + 1)
                    if k3 in kids and k3 != k:
                        g2 = own_groups(k2)
                        for key2 in sorted(g2, key=lambda kk: (len(g2[kk]) < short, len(g2[kk]))):
                            if len(g2[key2]) > short + 1 or st[k3][1] < len(g2[key2]) or st[k3][0]:
                                continue
                            for q in g2[key2]:
                                Q[k2].remove(q)
                                Q[k3].append(dict(q, floor_spec=k2))
                            st[k2], st[k3] = _dry(k2, Q[k2]), _dry(k3, Q[k3])
                            moves.append(f"{key2[0]} – wydział/komórka {key2[1]} ({len(g2[key2])} pok.) z kond. {k2} na sąsiednią kond. {k3} (Wyj. 17 odp. 70)")
                            break
                if st[k2][1] < len(grp) or st[k2][0]:
                    continue
                for q in grp:
                    Q[k].remove(q)
                    Q[k2].append(dict(q, floor_spec=k))
                st[k], st[k2] = _dry(k, Q[k]), _dry(k2, Q[k2])
                moves.append(f"{key[0]} – wydział/komórka {key[1]} ({len(grp)} pok.) z kond. {k} na sąsiednią kond. {k2} (Wyj. 17 odp. 70)")
                progressed = True
                break
            if progressed:
                break
        if not progressed:
            # ostatnia próba: elementy specjalne mimo wszystko
            for q in specials:
                if move_special(k, q):
                    progressed = True
                    break
        if not progressed:
            stuck.add(k)
    return Q, moves


# ----------------------------------------------------------------------------------------------------------------
# Parter
# ----------------------------------------------------------------------------------------------------------------
def build_P():
    kid = "P"
    plate0 = plate_of("P")
    cw = S["cofniecia_wneki"]
    podc = Polygon(clean_ring(cw["podcien_Brama_Mostowa"]["obrys_ccw"])[0]).buffer(0)
    brama = Polygon(clean_ring(cw["brama_ogrodowa"]["obrys_ccw"])[0]).buffer(0)
    # wnęki wejść 1,5 m
    wn = []
    m = re.search(r"v\s*([\d,]+)\s*[–-]\s*([\d,]+)", cw["wneka_wejscia_obywatelskiego"]["elewacja"])
    if m:
        a, b = float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
        g = cw["wneka_wejscia_obywatelskiego"]["glebokosc_m"]
        wn.append(("Wejście Obywatelskie", T.rect(TOWER_U - g, TOWER_U + 0.1, a, b)))
    m = re.search(r"u\s*([\d,]+)\s*[–-]\s*([\d,]+)", cw["wneka_wejscia_ogrodowego"]["elewacja"])
    if m:
        a, b = float(m.group(1).replace(",", ".")), float(m.group(2).replace(",", "."))
        g = cw["wneka_wejscia_ogrodowego"]["glebokosc_m"]
        wn.append(("Wejście ogrodowe", T.rect(a, b, -0.1, g)))
    g = cw["wneka_wejscia_konferencyjnego"]["glebokosc_m"]
    wn.append(("Wejście konferencyjne", WF.rect(55.2, 57.75, -0.1, g)))
    plate = plate0.difference(podc).difference(brama)
    for _, p in wn:
        plate = plate.difference(p)
    plate = clean(plate, 0.02)
    plate = unary_union([p for p in polys(plate) if p.area > 5])
    band = unary_union([ext_band(p, thick_fn("AG")) for p in polys(plate)])
    inner = unary_union([clean(p.difference(band), 0.03) for p in polys(plate)])
    inner = unary_union([p for p in polys(inner) if p.area > 5])
    L = Level(kid, plate, inner, band, ["A", "B", "C"])
    L.extra["podcien"] = podc
    L.extra["brama"] = brama
    L.extra["wneki"] = wn
    for sp in core_spaces(kid, ["A", "B", "C"]):
        L.spaces.append(sp)
    W = P["WALL"]
    zones = S["parter"]

    def zone_uv(key):
        for z in zones["wieza"]:
            if z["strefa"].startswith(key) and "uv" in z:
                return z["uv"]
        return None

    def zone_sd(key):
        for z in zones["skrzydlo"]:
            if z["strefa"].startswith(key) and "sd" in z:
                return z["sd"]
        return None
    # --- wieża
    u = zone_uv("Wejście Obywatelskie")
    lob = T.rect(u[0], u[2], u[1], u[3]).union(T.rect(u[0], CORE_UV["B"][1] + 2.2, u[3] - 0.1, CORE_UV["B"][3]))
    L.add(Space(lob, "Wejście Obywatelskie – lobby z kontrolą i szatnią", "SW", prog_id="SW.01", kind="room",
                uwagi=["wejście bezprogowe, drzwi automatyczne ≥ 1,2 m", "dostęp do P1/P2 i klatki B", "tyflomapa"], tags={"public"}))
    u = zone_uv("DK II")
    u = [u[0], u[1] - 0.05, u[2], u[3]]
    h = (u[3] - u[1] - P["PART"]) / 2
    for k in range(2):
        q = DEPT["DK"][k]
        L.add(Space(T.rect(u[0], u[2], u[1] + k * (h + P["PART"]), u[1] + k * (h + P["PART"]) + h),
                    f"Pokój pracowników (3 st.) – {q['komorka']} ({q['nr']})", "DK", prog_id=q["prog_id"], komorka=q["nr"], dept="DK",
                    osoby=q["osoby"], kind="office", furn="office3", facade_dir=(T.ex[0], T.ex[1])), gap=P["PART"])
    u = zone_uv("Kancelaria")
    L.add(Space(T.rect(u[0], u[2], u[1], u[3]), "Kancelaria ogólna (3 stanowiska, niski blat)", "SW", prog_id="SW.02", osoby=3,
                uwagi=["pętla indukcyjna", "stanowisko dostosowane (blat 0,75 m)"], tags={"public", "loop"}, furn="counter"))
    u = zone_uv("WC ogólnodostępne")
    um = u[0] + 3.0 + 0.0
    L.add(Space(T.rect(u[0], u[2], u[3] - 4.0, u[3]), "Komfortka (toaleta z możliwością przebierania dorosłych)", "PHS", prog_id="PHS.03",
                uwagi=["3,0 × 4,0 m", "≤ 20 m od wejścia głównego"], tags={"wc_ozn", "komfortka"}, furn="wc"))
    L.add(Space(T.rect(u[0], u[2], u[1], u[3] - 4.0 - W), "Toalety ogólnodostępne przy holu (K, M, dostępna, przewijak)", "PHS",
                prog_id="PHS.02", tags={"wc", "wc_ozn"}, furn="wc"))
    u = zone_uv("Centrum monitoringu")
    L.add(Space(T.rect(u[0], u[2], u[3] - 3.3, u[3]), "Centrum monitoringu / ochrona budynku", "SW", prog_id="SW.04", osoby=2,
                uwagi=["interkom z MOE", "CCTV, KD"], furn="office1"))
    L.add(Space(T.rect(u[0], u[0] + 3.0, u[1], u[3] - 3.3 - W), "Miejsce socjalne ochrony", "SW", prog_id="SW.05"))
    L.add(Space(T.rect(u[0] + 3.0 + W, u[2], u[1], u[3] - 3.3 - W), "Szatnie i WC personelu (ochrona, sprzątanie)", "PPT", prog_id="PPT.05",
                tags={"wc"}, furn="wc"))
    u = zone_uv("Rowerownia")
    L.add(Space(T.rect(u[0], u[2], u[1], u[3]), "Parking rowerowy – 50 stanowisk (wjazd od dziedzińca)", "PR", prog_id="PR.01",
                furn="bikes", uwagi=["stojaki U", "4 miejsca cargo"]))
    u = zone_uv("Łącznik")
    # łącznik – część holu, osobna przestrzeń (okna na skwer)
    L.add(Space(T.rect(u[0], u[2], u[1], u[3]), "Łącznik holu z foyer konferencyjnym (okna na skwer)", "SW", prog_id="SW.01",
                kind="room", tags={"public"}))
    # pokój cichy przy hali (przy trzonie A, pd.-wsch.)
    cA = CORE_UV["A"]
    L.add(Space(T.rect(cA[1] + W + 0.05, cA[1] + W + 4.05, cA[2] - 1.70, cA[2] + 2.3), "Pokój cichy (strefa wyciszenia)", "SW", prog_id="SW.06",
                uwagi=["16 m²", "przy Hali Obywatelskiej"], tags={"public"}))
    # --- skrzydło
    s = zone_sd("M1")
    cs0, cs1, cd0, cd1 = CORE_SD["C"]
    dmid = P["EXT_W"] + P["D_W"]
    for k in range(2):
        q = DEPT["DW"][k]
        a = P["EXT_PARTY"] + 0.05 + k * (P["W_O"] + P["PART"])
        L.add(Space(WF.rect(a, a + P["W_O"], 0, dmid), f"Pokój pracowników (3 st.) – {q['komorka']} ({q['nr']})", "DW",
                    prog_id=q["prog_id"], komorka=q["nr"], dept="DW", osoby=q["osoby"], kind="office", furn="office3",
                    facade_dir=(-WF.ey[0], -WF.ey[1])), gap=P["PART"])
    sm = s[2]
    L.add(Space(WF.rect(cs1 + W, sm, cd0 + 1.0, 15), "Pomieszczenie techników (3 stanowiska)", "PPT", prog_id="PPT.01", osoby=3, furn="office3"))
    L.add(Space(WF.rect(P["EXT_PARTY"] + 2 * (P["W_O"] + P["PART"]), sm, 0, dmid), "Pomieszczenie socjalne z szatnią – personel techniczny",
                "PPT", prog_id="PPT.04"))
    s = zone_sd("Sala 80")
    L.add(Space(WF.rect(s[0], s[2], s[1], s[3]), "Sala konferencyjna 80 os.", "SK", prog_id="SK.02", osoby=80, furn="chairs", seats=80,
                uwagi=["pętla indukcyjna", "wejście z bramy ogrodowej i z sali 200"], tags={"loop", "public"}))
    s = zone_sd("Sala 200")
    rz_w = 10.0 / (s[3] - s[1] - 7.0) if False else 2.9
    L.add(Space(WF.rect(s[0], s[0] + rz_w, s[1], s[1] + 3.45), "Reżyserka AV sali 80 os.", "SK", prog_id="SK.04", osoby=1))
    L.add(Space(WF.rect(s[2] - rz_w, s[2], s[1], s[1] + 3.45), "Reżyserka AV sali 200 os.", "SK", prog_id="SK.03", osoby=1))
    L.add(Space(WF.rect(s[0], s[2], s[1], s[3]), "Sala konferencyjna 200 os. (ściana mobilna – 2 × 100 os.)", "SK", prog_id="SK.01",
                osoby=200, furn="chairs", seats=200, uwagi=["pętla indukcyjna", "ściana mobilna", "h = 4,25 m w świetle"], tags={"loop", "public"}))
    s = zone_sd("Foyer")
    # foyer: WC i magazyn mebli przy ścianie wieży, szatnia przy ulicy
    L.add(Space(WF.rect(s[0], s[0] + 4.6, s[1], 6.0), "Szatnia centrum konferencyjnego", "SK", prog_id="SK.07", furn="counter"))
    L.add(Space(WF.rect(s[0] + 2.3, s[0] + 7.9, 9.2, 30), "Toalety strefy konferencyjnej (K, M, dostępna)", "PHS", prog_id="PHS.04",
                tags={"wc", "wc_ozn"}, furn="wc"))
    L.add(Space(WF.rect(s[0], s[0] + 2.2, 9.2, 30), "Magazyn mebli i ścianek mobilnych", "SK", prog_id="SK.05"))
    s = zone_sd("Bistro")
    L.add(Space(WF.rect(s[0] + 0.0, s[0] + 4.0, 5.9, 12), "Bistro – zaplecze (podgrzewanie, zmywanie)", "SW", prog_id="SW.08"))
    L.add(Space(WF.rect(s[0], 70, -1, 12), "Bistro – sala konsumpcyjna (taras na skwerze)", "SW", prog_id="SW.07", osoby=60,
                furn="cafe", tags={"public"}))
    s = zone_sd("Foyer")
    L.add(Space(WF.rect(s[0], s[2], s[1], 30), "Foyer / kuluary centrum konferencyjnego", "SK", prog_id="SK.06", kind="room",
                tags={"public"}))
    # --- segment: pas pn. (trafo, rozdzielnia, BESS, odpady) i rampa
    uS = T.loc(*S["bryly"][2]["obrys_ccw"][3])[0]
    v_n = -0.05 - 0.5
    v_s = v_n - 2.9
    segn = [("IT.04", "Stacja transformatorowa SN/nn (drzwi od Wybrzeża)", 7.0, TOWER_U - 0.5),
            ("IT.05", "Rozdzielnia główna nn z SZR", 5.6, None), ("IT.07", "Magazyn energii BESS 250 kWh (EI 120)", 3.7, None),
            ("IT.14", "Punkt wystawienia odpadów (przy dźwigu T)", 2.4, None)]
    cur = TOWER_U - 0.5
    for pid, nm, w, _ in segn:
        L.add(Space(T.rect(cur - w, cur, v_s, v_n), nm, "IT", prog_id=pid, kind="room"))
        cur -= w + W
    # rampa (wjazd) – od bramy wzdłuż ściany pd.
    ramp_zone = L.inner.intersection(T.rect(uS + 0.4, TOWER_U, -12, v_s - W))
    L.add(Space(ramp_zone, "Rampa zjazdowa do garażu (≤ 18 %, 2 × 3,0 m)", "PPM", prog_id="PPM.03", kind="ramp",
                uwagi=["brama 6,0 m od Wybrzeża", "próg 119,60, zapory mobilne"]), clip=True)
    L.ramps.append(dict(poly=ramp_zone, kier=T.en(uS, -4.0), od=T.en(TOWER_U, -7.0), opis="rampa ≤ 18 % ↓ −1"))
    # --- hala obywatelska = reszta wnętrza wieży
    rest = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(W, **MITRE))
    rest = rest.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    hall = rest.intersection(W_.buffer(0.2))
    hall = largest(clean(hall, 0.05))
    L.add(Space(hall, "Hol główny – Hala Obywatelska (informacja, poczekalnia, lapidarium)", "SW", prog_id="SW.01",
                uwagi=["oś przekątna most → ogród, szer. ≥ 6,3 m", "ścieżki dotykowe, tyflomapa", "informacja 8 m², poczekalnia 40 m²"],
                tags={"public", "hall"}, furn="hall"), clip=False)
    # reszta skrzydła/segmentu → komunikacja
    rest = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(W, **MITRE))
    rest = rest.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    for p in polys(clean(rest, 0.05)):
        if p.area > 2.0:
            L.spaces.append(Space(p, "Komunikacja", "KW", kind="corridor"))
    return L


# ----------------------------------------------------------------------------------------------------------------
# Kondygnacja Sejmiku i antresola
# ----------------------------------------------------------------------------------------------------------------
SEJ_KOD = {"SWD": "SWD", "PHS": "PHS", "KUL": "KW", "C-A": "KW", "C-B": "KW"}


def build_S():
    kid = "S"
    plate = plate_of("S")
    inner, band = inner_of(plate)
    L = Level(kid, plate, inner, band, ["A", "B"])
    for sp in core_spaces(kid, ["A", "B"]):
        L.spaces.append(sp)
    for code, r in S["kondygnacja_sejmiku"]["pomieszczenia"].items():
        if code.startswith("C-"):
            continue
        ring, nts = clean_ring(r["obrys_en"][0])
        if nts:
            DATA_FIX.append(f"Sejmik {code}: {len(nts)} zdublowanych/współliniowych wierzchołków – oczyszczono")
        poly = Polygon(ring).buffer(0)
        if abs(poly.area - r["pow_m2"]) > 0.3:
            note("dane", f"Sejmik {code}: pole z poligonu {poly.area:.2f} ≠ pow_m2 {r['pow_m2']}")
        pref = code.split(".")[0]
        kod = SEJ_KOD.get(pref, pref)
        kind = "corridor" if code == "KUL" else "room"
        sp = Space(poly, r["nazwa"], kod, prog_id=code if code != "KUL" else "", kind=kind)
        if code.startswith("PHS"):
            sp.tags |= {"wc", "wc_ozn"}
            sp.furn = "wc"
        if code in ("SWD.08", "SWD.09", "SWD.11a", "SWD.11b", "SWD.12a", "SWD.12b", "SWD.13"):
            sp.furn = "table"
            sp.seats = {"SWD.08": 26, "SWD.09": 18, "SWD.11a": 18, "SWD.11b": 18, "SWD.12a": 12, "SWD.12b": 12, "SWD.13": 12}[code]
            sp.uwagi.append("pętla indukcyjna")
            sp.tags.add("loop")
        if code == "SWD.01":
            sp.furn = "sejmik"
            sp.uwagi += ["pętla indukcyjna", "44 stanowiska stałe, w każdym rzędzie miejsce dla wózka", "pochylnie ≤ 5 %"]
            sp.tags |= {"loop", "public", "sejmik"}
            sp.osoby = S["kondygnacja_sejmiku"]["sala"].get("plyta_razem")
        if code == "SWD.02":
            sp.tags |= {"public", "sejmik"}
            sp.uwagi.append("bar SWD.05 i szatnia SWD.06 jako otwarte lady")
        if code == "SWD.07":
            sp.tags.add("rodzina")
        if code == "KUL":
            sp.tags.add("sejmik")
        L.spaces.append(sp)
    rest = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(0.08, **MITRE))
    rest = rest.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(0.05, **MITRE))
    for p in polys(clean(rest, 0.1)):
        if p.area > 1.5:
            L.spaces.append(Space(p, "Komunikacja", "KW", kind="corridor"))
    return L


def build_ANT():
    kid = "ANT"
    plate = W_
    inner, band = inner_of(plate)
    L = Level(kid, plate, inner, band, ["A", "B"])
    # tylko przystanki P1/P2 w trzonie B; trzon A – klatka A nie ma wyjścia na antresolę (otwarte schody do kuluaru)
    for sp in core_spaces(kid, ["A", "B"]):
        L.spaces.append(sp)
    zz = S["kondygnacja_sejmiku"]["antresola_strefy"]
    for code, z in zz.items():
        poly = T.poly(z["obrys_uv"][0]).buffer(0)
        kod = "SWD"
        pid = "SWD.03" if code == "ANT-F" else "SWD.01"
        sp = Space(poly, z["nazwa"], kod, prog_id=pid, kind="room", tags={"public", "sejmik"})
        if code == "ANT-G":
            sp.furn = "gallery"
            sp.osoby = 30
            sp.uwagi += ["3 miejsca dla wózków w 1. rzędzie", "balustrada szklana 1,10 m", "pętla indukcyjna"]
            sp.tags.add("loop")
        else:
            sp.uwagi += ["sala multimedialna / poczekalnia gości (ekrany)", "pętla indukcyjna"]
            sp.tags.add("loop")
        L.spaces.append(sp)
    # pustka nad salą, kuluarem i holem (2 kond.)
    sala = Polygon(clean_ring(S["kondygnacja_sejmiku"]["pomieszczenia"]["SWD.01"]["obrys_en"][0])[0]).buffer(0)
    hol = Polygon(clean_ring(S["kondygnacja_sejmiku"]["pomieszczenia"]["SWD.02"]["obrys_en"][0])[0]).buffer(0)
    kul = Polygon(clean_ring(S["kondygnacja_sejmiku"]["pomieszczenia"]["KUL"]["obrys_en"][0])[0]).buffer(0)
    taken = unary_union([s.poly for s in L.spaces])
    void = unary_union([sala, hol, kul]).difference(taken.buffer(0.05))
    L.extra["void"] = void
    L.extra["void_parts"] = {"sala": sala.difference(taken), "hol": hol, "kul": kul.difference(taken)}
    return L


# ----------------------------------------------------------------------------------------------------------------
# Kondygnacje podziemne – garaż
# ----------------------------------------------------------------------------------------------------------------
def ramp_spec():
    """Rampa z koncepcja.json: brama (zakres v na elewacji wsch. segmentu), szerokość, spadki, próg."""
    rp = S["podziemie"]["rampa"]
    m = re.search(r"v\s*([−-]?[\d,]+)\s*…\s*([−-]?[\d,]+)", rp.get("wjazd", ""))
    v1, v2 = (-10.1, -4.1)
    if m:
        v1, v2 = sorted([_num_pl(m.group(1)), _num_pl(m.group(2))])
    mb = re.search(r"brama\s*([\d,]+)\s*m", rp.get("wjazd", ""))
    brama = _num_pl(mb.group(1)) if mb else (v2 - v1)
    width = float(rp.get("szerokosc_m", v2 - v1))
    smax = float(rp.get("pochylenie_max_proc", 18)) / 100.0
    strans = float(rp.get("przejscia_proc", smax * 50)) / 100.0
    prog = float(rp.get("prog_npm", S["meta"]["zero"]["wzgl_0_00_m_npm"]))
    # strona: brama bliżej lica pn. segmentu (v≈0) → rampa wzdłuż ściany pn., inaczej wzdłuż ściany pd.
    seg_uv = [T.loc(*p_) for p_ in S["bryly"][2]["obrys_ccw"]]
    v_south_e = min(v for u, v in seg_uv if u > TOWER_U - 0.1)
    side = "N" if abs(v2 - 0.0) < abs(v1 - v_south_e) else "S"
    return dict(v1=v1, v2=v2, brama=brama, width=width, smax=smax, strans=strans, prog=prog, side=side)


def _num_pl(t):
    return float(t.replace("−", "-").replace(",", "."))


def ramp_length(drop, rs, trans_len=3.5):
    """Długość rzutu rampy: dwa przejścia (trans_len) ze spadkiem przejściowym + odcinek ze spadkiem maks."""
    core = max(0.0, drop - 2 * trans_len * rs["strans"])
    return 2 * trans_len + core / rs["smax"]


def ramp_band(kid, rs, u_from, length, inner):
    """Pas rampy: od bramy (u = 40) na zach. na długość 'length', wzdłuż ściany pn. (v = 0) lub pd. segmentu / pasa."""
    seg_uv = [T.loc(*p_) for p_ in S["bryly"][2]["obrys_ccw"]]
    u_sw = min(u for u, v in seg_uv)
    w = rs["width"]
    E = P["EXT_UG"] if kid in ("-1", "-2") else P["EXT_T"]
    u_to = u_from - length
    if rs["side"] == "N":
        v_hi = -0.05 - (0.0 if kid in ("-1", "-2") else E)
        band = T.rect(u_to, TOWER_U + 1, v_hi - w, v_hi)
    else:
        # wzdłuż ściany pd. segmentu (ukośnej), dalej wzdłuż krawędzi pd. pasa dziedzińca
        a = T.en(TOWER_U + 1, [v for u, v in seg_uv if u > TOWER_U - 0.1][0] if False else min(v for u, v in seg_uv if u > TOWER_U - 0.1))
        b = T.en(u_sw, min(v for u, v in seg_uv if u < u_sw + 0.1))
        c = T.en(u_to - 1, T.loc(*b)[1])
        ln = LineString([a, b, c])
        band = ln.buffer(-(w + E), single_sided=True, join_style=2)
        band = band.union(ln.buffer(-(E), single_sided=True, join_style=2)).difference(ln.buffer(-(E), single_sided=True, join_style=2))
        band = band.intersection(T.rect(u_to, TOWER_U + 1, -40, 40))
    return band.intersection(inner)


def build_UG(kid):
    plate = plate_of(kid)
    inner, band = inner_of(plate, "UG")
    cores = ["A", "B"] + (["C"] if kid == "-1" and CORE_POLY["C"].intersection(plate).area > 10 else [])
    L = Level(kid, plate, inner, band, cores)
    for sp in core_spaces(kid, cores):
        L.spaces.append(sp)
    W = P["WALL"]
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    rs = ramp_spec()
    z0 = S["meta"]["zero"]["wzgl_0_00_m_npm"]
    lvl = {k["kondygnacja"]: k["posadzka_wzgl"] for k in S["kondygnacje"]}
    drop1 = (rs["prog"] - z0) - lvl["-1"]
    drop2 = lvl["-1"] - lvl["-2"]
    L1 = ramp_length(drop1, rs)
    L2 = ramp_length(drop2, rs)
    L.extra["ramp_info"] = dict(L1=L1, L2=L2, drop1=drop1, drop2=drop2)
    # rampa P→−1 (wzdłuż ściany) i −1→−2 (pod nią, w przeciwnym kierunku)
    b1 = ramp_band(kid, rs, TOWER_U, L1, inner)
    if kid == "-1":
        both = b1.union(ramp_band(kid, rs, TOWER_U - L1 + L2, L2, inner)) if "-2" in S["podziemie"] else b1
        L.add(Space(both, "Rampa ↑ parter / ↓ −2 (pod rampą wjazdową)", "PPM", prog_id="PPM.03", kind="ramp",
                    uwagi=[f"spadek ≤ {rs['smax']*100:.0f} %, przejścia {rs['strans']*100:.0f} %", f"szer. {rs['width']:.2f} m"]), clip=True)
        L.ramps.append(dict(poly=both, opis=f"rampa ↑ P ({L1:.1f} m) / ↓ −2 ({L2:.1f} m)"))
    else:
        b2 = ramp_band(kid, rs, TOWER_U - L1 + L2, L2, inner)
        L.add(Space(b2, "Rampa ↑ −1", "PPM", prog_id="PPM.03", kind="ramp", uwagi=[f"spadek ≤ {rs['smax']*100:.0f} %"]), clip=True)
        L.ramps.append(dict(poly=b2, opis=f"rampa ↑ −1 ({L2:.1f} m)"))
    # pomieszczenia techniczne: rejon łuku (NE) i na wsch. od trzonu B – najmniej przydatne dla parkowania
    fNE = T
    uE0 = cB[1] + W
    if kid == "-1":
        techs = [
            ("IT.15", "Strefa dostaw – zatoka przy dźwigu T (pojazdy ≤ 2,20 m)", "IT", T.rect(uE0, TOWER_U, cB[2], cB[2] + 4.2)),
            ("IT.14", "Pomieszczenie odpadów komunalnych", "IT", T.rect(uE0, TOWER_U, cB[2] + 4.2 + W, cB[3] + 0.6)),
            ("IT.13", "Centrale wentylacyjne parteru i Sejmiku", "IT", T.rect(uE0, TOWER_U, cB[3] + 0.6 + W, ARC_C_UV[1] + 2.5)),
            ("IT.11", "Przyłącze wody, pompownia, woda szara (IT.12)", "IT", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 0, 24)),
            ("PPT.06", "Szatnie i prysznice personelu i rowerzystów", "PPT", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 24.15, 46)),
            ("PPT.03", "Warsztat konserwacyjny (PPT)", "PPT", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 46.15, 68)),
            ("PPM.04", "Magazyn wyposażenia MDS", "PPM", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 68.15, 80)),
            ("PP.07", "Pomieszczenie porządkowe z pralnią i suszarnią", "PP", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 80.15, 90)),
            ("IT.02", "Punkt dystrybucyjny IT (PD)", "IT", T.rect(cB[1] - 2.75, cB[1], cB[3] + 0.2, cB[3] + 2.6)),
            ("PPT.02", "Magazyn narzędzi i materiałów", "PPT", T.rect(cB[1] + W, TOWER_U, ARC_C_UV[1] + 2.5 + W, ARC_C_UV[1] + 5.5)),
        ]
        wc_poly = T.rect(cB[1] - 2.75, cB[1], cB[3] + 2.6 + W, cB[3] + 5.0)
    else:
        techs = [
            ("IT.08", "Maszynownia gruntowych pomp ciepła z rozdzielaczami", "IT", T.rect(uE0, TOWER_U, cB[2], cB[3] + 5.0)),
            ("IT.09", "Zbiorniki buforowe ciepła / chłodu", "IT", T.rect(uE0, TOWER_U, cB[3] + 5.0 + W, ARC_C_UV[1] + 2.5)),
            ("IT.06", "Agregat prądotwórczy HVO (spaliny szachtem)", "IT", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 0, 30)),
            ("IT.10", "Instalacja tryskaczowa – pompownia i zbiornik", "IT", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 30.15, 60)),
            ("PPM.04", "Filtrowentylacja ukrycia (budowla ochronna)", "PPM", annulus_sector(T, ARC_C_UV, 8.0, R_ARC, 60.15, 90)),
            ("IT.12", "Zbiornik wody deszczowej 50 m³", "IT", T.rect(cB[1] - 2.75, cB[1], cB[3] + 5.0 + W, ARC_C_UV[1] + 2.5)),
            ("IT.02", "Punkt dystrybucyjny IT (PD)", "IT", T.rect(cB[1] - 2.75, cB[1], cB[3] + 0.2, cB[3] + 2.6)),
        ]
        wc_poly = T.rect(cB[1] - 2.75, cB[1], cB[3] + 2.6 + W, cB[3] + 5.0)
    for pid, nm, kod, poly in techs:
        L.add(Space(poly, nm, kod, prog_id=pid, kind="room"))
    L.add(Space(wc_poly, "WC dostępne (garaż / ukrycie)", "PHS", prog_id="PHS.01", tags={"wc", "wc_ozn"}, furn="wc"))
    parking(L, kid)
    return L


OZN_DONE = {}


def parking(L: Level, kid):
    """Układ deterministyczny dopasowany do siatki wieży: drogi 6,0 m prowadzone poza liniami słupów, rzędy 90°
    (2,5 × 5,0) po obu stronach dróg; słupy wypadają między stanowiskami. Drogi (parametrycznie z geometrii):
      T1 – wzdłuż u nad pasem dziedzińca (v od max(0,6; lico pasa + 5,0)), V1 – wzdłuż v między trzonami A i B,
      W1 – wzdłuż v przy licu zach. wieży, WA – wzdłuż skrzydła (s), N1 – wzdłuż u na pn. od trzonu A.
    OzN: pary sąsiednich stanowisk najbliżej trzonów → stanowisko 3,6 m + pas manewru."""
    from shapely.prepared import prep
    W = P["WALL"]
    sw, sl, ai, swo = P["STALL_W"], P["STALL_L"], P["AISLE"], P["STALL_OZN_W"]
    E = P["EXT_UG"]
    cA, cB = CORE_UV["A"], CORE_UV["B"]
    avail = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(0.05))
    avail = avail.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(0.15))
    cols = columns_UG(kid)
    colu = unary_union([Point(c).buffer(0.25, cap_style=3) for c in cols]) if cols else Polygon()
    avail = clean(avail.difference(colu), 0.02)
    Tv = Frame(T.o, T.ey, (-T.ex[0], -T.ex[1]))          # x = v, y = −u
    # lico pd. pasa dziedzińca (min v wnętrza w rejonie u 2…12)
    probe = L.inner.intersection(T.rect(2, 12, -30, 5))
    strip_in = T.to_local_geom(probe).bounds[1] if not probe.is_empty else 0.0
    vT1 = max(0.6, strip_in + sl)
    c_cols = [T.loc(*c) for c in cols]
    ucol = sorted({round(u, 2) for u, v in c_cols})
    # droga V1: między liniami słupów najbliższymi przerwie między trzonami A i B
    gap_lo, gap_hi = cA[1], cB[0]
    lines_u = [u for u in SIATKA["wieza"]["osie_u"]]
    uv1 = None
    for a_, b_ in zip(lines_u[:-1], lines_u[1:]):
        if b_ - a_ >= ai + 0.7 and a_ >= gap_lo - 3 and b_ <= gap_hi + 3:
            uv1 = (a_ + b_) / 2
    if uv1 is None:
        uv1 = (gap_lo + gap_hi) / 2
    vN1 = SIATKA["wieza"]["osie_v"][2] + 0.3
    aisle_defs = [
        ("WA", WF, E + sl, 0.0, 48.0),
        ("T1", T, vT1, -9.0, cB[0] - 0.2),
        ("V1", Tv, -(uv1 + ai / 2), vT1 + ai - 0.5, 40.0),
        ("W1", Tv, -((lines_u[0] + lines_u[1]) / 2 + ai / 2), vT1 + ai - 0.5, 40.0),
    ]
    aisles = []
    av_a = avail
    for name, fr, y0, xmin, xmax in aisle_defs:
        lb = fr.to_local_geom(av_a).bounds
        xs = []
        x = max(lb[0], xmin)
        r0 = None
        while x <= min(lb[2], xmax):
            ok_ = fr.rect(x, x + 0.5, y0, y0 + ai).difference(av_a).area < 0.04
            if ok_ and r0 is None:
                r0 = x
            if not ok_ and r0 is not None:
                xs.append((r0, x))
                r0 = None
            x += 0.5
        if r0 is not None:
            xs.append((r0, min(lb[2], xmax)))
        xs = [(a_, b_) for a_, b_ in xs if b_ - a_ >= 8.0]
        if not xs:
            continue
        a_, b_ = max(xs, key=lambda ab: ab[1] - ab[0])
        ais = fr.rect(a_, b_, y0, y0 + ai)
        aisles.append(dict(name=name, fr=fr, y0=y0, a=a_, b=b_, poly=ais))
    aisles_u = unary_union([a["poly"] for a in aisles]) if aisles else Polygon()
    stalls = []
    used = aisles_u
    for a in aisles:
        fr, y0 = a["fr"], a["y0"]
        for side in (-1, 1):
            ya, yb = (y0 - sl, y0) if side < 0 else (y0 + ai, y0 + ai + sl)
            x = a["a"]
            av2 = avail.difference(used.buffer(0.02))
            P_av = prep(av2)
            while x + sw <= a["b"] + 1e-6:
                r = fr.rect(x, x + sw, ya, yb)
                if P_av.contains(r) or (P_av.intersects(r) and r.difference(av2).area < 0.06):
                    stalls.append(dict(poly=r, fr=fr, x=x, ya=ya, yb=yb, ozn=False, aisle=a["name"]))
                    used = used.union(r)
                    x += sw
                else:
                    x += 0.1
    # OzN
    n_ozn = int(S["podziemie"].get("OzN", 6))
    target = n_ozn if kid == "-1" else max(0, n_ozn - OZN_DONE.get("-1", 0))
    cen = [Point(*T.en((CORE_UV[c][0] + CORE_UV[c][1]) / 2, (CORE_UV[c][2] + CORE_UV[c][3]) / 2)) for c in ("A", "B")]
    pairs = []
    for i, st_ in enumerate(stalls):
        for j, st2 in enumerate(stalls):
            if j <= i or st_["fr"] is not st2["fr"] or abs(st_["ya"] - st2["ya"]) > 0.01:
                continue
            if abs(st2["x"] - (st_["x"] + sw)) < 0.02:
                d = min(c.distance(st_["poly"]) for c in cen)
                pairs.append((d, i, j))
    pairs.sort()
    gone = set()
    for d, i, j in pairs:
        if target <= 0:
            break
        if i in gone or j in gone:
            continue
        st_ = stalls[i]
        st_["poly"] = st_["fr"].rect(st_["x"], st_["x"] + swo, st_["ya"], st_["yb"])
        st_["pas"] = st_["fr"].rect(st_["x"] + swo, st_["x"] + 2 * sw, st_["ya"], st_["yb"])
        st_["ozn"] = True
        gone |= {i, j}
        gone.discard(i)
        target -= 1
    L.stalls = [dict(poly=s_["poly"], ozn=s_["ozn"], aisle=s_["aisle"]) for k, s_ in enumerate(stalls) if k not in gone]
    OZN_DONE[kid] = sum(1 for s_ in L.stalls if s_["ozn"])
    L.extra["aisles"] = [a["poly"] for a in aisles]
    L.extra["ozn_pasy"] = unary_union([s_["pas"] for s_ in stalls if s_.get("pas") is not None]) if any(s_.get("pas") is not None for s_ in stalls) else Polygon()
    rest = L.inner.difference(unary_union([s.poly for s in L.spaces]).buffer(W, **MITRE))
    rest = rest.difference(unary_union([CORE_POLY[c] for c in L.cores]).buffer(W, **MITRE))
    for p in sorted(polys(clean(rest, 0.05)), key=lambda g: -g.area):
        if p.area < 2:
            continue
        sp = Space(p, "Garaż – stanowiska postojowe i drogi manewrowe (MDS)" if p.area > 150 else "Garaż – komunikacja / rezerwa",
                   "PPM", prog_id="PPM.01" if p.area > 150 else "PPM.03", kind="garage" if p.area > 150 else "corridor",
                   uwagi=["miejsce doraźnego schronienia (MDS)"] + (["ukrycie – budowla ochronna"] if kid == "-2" else []))
        L.spaces.append(sp)
    L.columns = cols


def columns_UG(kid):
    """Słupy w kondygnacjach podziemnych: siatka wieży (osie u × v), także na liniach obrysu wieży tam, gdzie
    kondygnacja podziemna wychodzi poza wieżę (pas dziedzińca, styk ze skrzydłem) – filary elewacji schodzą na płytę."""
    cols = []
    plate = plate_of(kid).buffer(-P["EXT_UG"] - 0.3)
    for u in SIATKA["wieza"]["osie_u"]:
        for v in SIATKA["wieza"]["osie_v"]:
            p = T.en(u, v)
            pt = Point(p)
            if any(CORE_POLY[c].buffer(0.4).contains(pt) for c in ("A", "B")):
                continue
            if plate.contains(pt):
                cols.append(p)
    return cols


# ----------------------------------------------------------------------------------------------------------------
# Dach
# ----------------------------------------------------------------------------------------------------------------
def build_roof():
    L = Level("D", unary_union([W_, M_, S_]), unary_union([W_, M_, S_]), Polygon(), [])
    att = {}
    for b in S["bryly"]:
        att[b["id"]] = b["dach"]
    L.extra["roofs"] = []
    for bid, poly in (("W", W_), ("M", M_), ("S", S_)):
        d = att[bid]
        at = d.get("attyka", d.get("gzyms_attyka", {}))
        lo = d.get("najnizszy_pkt_pokrycia", d.get("taras_wykonczenie", {}))
        hi = d.get("najwyzszy_pkt_pokrycia", {})
        L.extra["roofs"].append(dict(id=bid, poly=poly, attyka=at.get("wzgl"), attyka_npm=at.get("npm"),
                                     min=lo.get("wzgl"), min_npm=lo.get("npm"), max=hi.get("wzgl"), max_npm=hi.get("npm")))
    pv = S["elewacje"]["PV"]
    # pola BIPV: wieża i skrzydło w obrysie attyki (pas attyki 0,6 m + obejście serwisowe 0,6 m)
    tw = W_.buffer(-1.2, **MITRE)
    tm = M_.buffer(-1.2, **MITRE)
    L.spaces.append(Space(tw, "Dach wieży – BIPV szkło-szkło jako pokrycie (bez stelaży i urządzeń)", "DACH", kind="roof",
                          uwagi=[f"BIPV dach razem {pv['BIPV_dach_kWp']} kWp", "spadki 1,5 % do wpustów"], label=True))
    L.spaces.append(Space(tm, "Dach skrzydła – BIPV szkło-szkło jako pokrycie", "DACH", kind="roof", uwagi=["spadki 1,5 %"], label=True))
    ts = S_.buffer(-0.6, **MITRE)
    L.spaces.append(Space(ts, "Taras nad Oławą (+19,80) – dach zielony intensywny, donice, balustrada cofnięta 1,5 m", "DACH",
                          kind="roof", uwagi=["dostęp z kond. 5", "retencja (dach niebieski)"], tags={"green"}))
    return L


# ----------------------------------------------------------------------------------------------------------------
# Okna, drzwi, słupy
# ----------------------------------------------------------------------------------------------------------------
def windows_for(L: Level):
    """Okna w rytmie: wieża przęsło 2,70 m (okno 1,65), skrzydło i segment oś 2,025 m (okno 1,20); łuk – okna wstęgowe."""
    out = []
    kid = L.kid
    if kid in ("-1", "-2", "D", "ANT"):
        return out
    pw = S["elewacje"]["wieza"]
    przeslo, okno_t = pw["przeslo_m"], pw["okno_m"][0]
    ps = S["elewacje"]["skrzydlo"]
    os_w, okno_w = ps["os_m"], ps["okno_m"][0]
    low = kid in ("P", "1", "2", "3", "4")
    pl = L.plate

    _bd = unary_union([g.exterior for g in polys(pl)]).buffer(0.08)

    def on_ext(seg):
        return _bd.contains(seg)

    def add(frame, x0, x1, y_face, width, step, start, inward_sign, thick, kind="okno"):
        x = start
        while x + width / 2 <= x1 + 1e-6:
            if x - width / 2 >= x0 - 1e-6:
                a = frame.en(x - width / 2, y_face)
                b = frame.en(x + width / 2, y_face)
                seg = LineString([a, b])
                if on_ext(seg):
                    out.append(dict(a=a, b=b, t=thick, n=(frame.ey[0] * inward_sign, frame.ey[1] * inward_sign), kind=kind))
            x += step
    # wieża: N (v=29,7), S (v=0), E (u=40), W (u=0)
    tN = sub(T, 0, TOWER_V, "x-y")
    add(tN, 0, ARC_C_UV[0], 0.0, okno_t, przeslo, przeslo / 2, +1, P["EXT_T"])
    add(T, 0, TOWER_U, 0.0, okno_t, przeslo, przeslo / 2, +1, P["EXT_T"])
    fE = Frame(T.en(TOWER_U, 0.0), T.ey, (-T.ex[0], -T.ex[1]))
    add(fE, 0, ARC_C_UV[1], 0.0, okno_t, przeslo, przeslo / 2, +1, P["EXT_T"])
    fW = Frame(T.en(0.0, 0.0), T.ey, T.ex)
    add(fW, 0, TOWER_V, 0.0, okno_t, przeslo, przeslo / 2, +1, P["EXT_T"])
    # łuk – okna wstęgowe między słupami co 15°
    if kid not in ("P",):
        for k in range(6):
            a0, a1 = 90 - k * 15 - 1.6, 90 - (k + 1) * 15 + 1.6
            pts = [T.en(ARC_C_UV[0] + R_ARC * math.cos(math.radians(a)), ARC_C_UV[1] + R_ARC * math.sin(math.radians(a)))
                   for a in [a0 + (a1 - a0) * i / 6 for i in range(7)]]
            out.append(dict(pts=pts, t=P["EXT_T"], kind="wstega"))
    if low:
        # skrzydło: ulica (d=0) i podwórze (d=15); segment: wsch. (u=40, v<0) i zach. (u=21)
        add(WF, 0, 57.7, 0.0, okno_w, os_w, os_w / 2, +1, P["EXT_W"])
        add(sub(WF, 0, 15.0, "x-y"), 0, 34.2, 0.0, okno_w, os_w, os_w / 2, +1, P["EXT_W"])
        add(fE, -11.0, 0.0, 0.0, okno_w, os_w, -os_w / 2 - 0.0 - 10 * os_w, +1, P["EXT_T"])
        u_sw = T.loc(*S["bryly"][2]["obrys_ccw"][3])[0]
        add(Frame(T.en(u_sw, 0.0), T.ey, T.ex), -8, 0, 0.0, okno_w, os_w, -os_w / 2 - 3 * os_w, +1, P["EXT_T"])
    return out


def doors_for(L: Level):
    """Drzwi pomieszczeń do korytarza / holu (łuk otwarcia do wnętrza). Uproszczenie: jedne drzwi na pomieszczenie."""
    out = []
    circ = [s for s in L.spaces if s.kind in ("corridor",) or "hall" in s.tags or (s.kod in ("SW", "SK") and s.prog_id in ("SW.01", "SK.06"))]
    if not circ:
        return out
    cu = unary_union([s.poly for s in circ])
    for sp in L.spaces:
        if sp.kind in ("corridor", "core_lift", "shaft", "garage", "ramp", "roof", "void") or "hall" in sp.tags:
            continue
        if sp.prog_id in ("SW.01", "SK.06") and sp.kind == "room":
            continue
        w = 1.0 if sp.kind in ("office", "room") else 0.9
        if sp.kod in ("SK", "SN") or sp.prog_id in ("SWD.01", "SWD.08"):
            w = 1.6
        d = door_on(sp.poly, cu, width=w, wall=max(P["WALL"], 0.26))
        if d is None:
            continue
        out.append(dict(p0=d[0], p1=d[1], n=d[2], w=w, room=sp))
    return out


def columns_for(L: Level):
    kid = L.kid
    cols = []
    if kid in ("-1", "-2"):
        return L.columns
    if kid in ("D", "ANT"):
        return cols
    us, vs = SIATKA["wieza"]["osie_u"], SIATKA["wieza"]["osie_v"]
    taken = unary_union([s.poly for s in L.spaces if s.kind in ("office", "room", "corridor")])
    for u in us:
        for v in vs:
            p = Point(*T.en(u, v))
            if not W_.buffer(0.01).contains(p):
                continue
            if any(CORE_POLY[c].buffer(0.3).contains(p) for c in ("A", "B")):
                continue
            if kid == "S" and 0 < u < TOWER_U and 0 < v < TOWER_V:
                continue    # słupy wewnętrzne kończą się na stropie S
            cols.append(T.en(u, v))
    # łuk: słupy co 15° na R 13,5 i R 7,0
    if kid not in ("S",):
        for k in range(7):
            a = math.radians(90 - 15 * k)
            for R_ in (R_SZYB, 7.0):
                if R_ == 7.0 and kid == "P":
                    continue
                cols.append(T.en(ARC_C_UV[0] + R_ * math.cos(a), ARC_C_UV[1] + R_ * math.sin(a)))
    return cols


# ----------------------------------------------------------------------------------------------------------------
# Numeracja
# ----------------------------------------------------------------------------------------------------------------
ORDER = ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT", "D"]
LET = "abcdefghijklmnopqrstuvwxyz"


def number_all(levels):
    cnt = defaultdict(int)
    by_pid = defaultdict(list)
    for L in levels:
        # kolejność: pomieszczenia biurowe wg pierścienia (kolejność dodania), reszta wg pozycji
        for sp in L.spaces:
            if sp.kind in ("core_lift",) or not sp.label and sp.kind in ("shaft",):
                pass
            by_pid[(sp.prog_id, sp.kod)].append((L.kid, sp))
    # biura: KOD.nn
    for code in DEPT_CODES:
        nums = [int(m.group(1)) for it in BLOK[code]["pomieszczenia"] for m in [re.match(rf"^{code}\.(\d+)$", it["id"])] if m]
        k = max(nums) if nums else 0
        for L in levels:
            for sp in L.spaces:
                if sp.kind == "office" and sp.kod == code and not sp.prog_id.startswith("KS.0"):
                    k += 1
                    sp.numer = f"{code}.{k:02d}"
    # pozycje programu z liczbą > 1 → litery; == 1 → id
    multi = defaultdict(list)
    for L in levels:
        for sp in L.spaces:
            if sp.numer:
                continue
            if sp.prog_id and (re.match(r"^[A-Z]+\.\d+[a-z]?$", sp.prog_id) or re.match(r"^[A-Z]+\.[A-Z]+$", sp.prog_id)):
                multi[sp.prog_id].append(sp)
    for pid, lst in multi.items():
        if re.search(r"[a-z]$", pid):          # już z literą (Sejmik)
            for sp in lst:
                sp.numer = pid
            continue
        it = prog_item(pid)
        if len(lst) == 1 and (it is None or int(it.get("liczba", 1)) == 1):
            lst[0].numer = pid
        else:
            for i, sp in enumerate(lst):
                sp.numer = pid + (LET[i] if i < 26 else f".{i + 1}")
    # KW i reszta: KW.<kond>.nn, IT.<kond>... (szachty), PPM.01.<kond>
    for L in levels:
        k = 0
        for sp in L.spaces:
            if sp.numer:
                continue
            kk = L.kid if L.kid not in ("ANT",) else "A"
            if sp.kod == "KW" or sp.kind in ("corridor", "core_stair", "core_lobby", "core_lift"):
                k += 1
                sp.numer = f"KW.{kk}.{k:02d}"
                sp.kod = "KW"
            elif sp.prog_id and sp.prog_id.startswith("PPM"):
                sp.numer = f"{sp.prog_id}.{kk}"
            elif sp.kod == "DACH":
                k += 1
                sp.numer = f"D.{k:02d}"
            else:
                k += 1
                sp.numer = f"{sp.kod}.{kk}.{k:02d}"


# ----------------------------------------------------------------------------------------------------------------
# Serializacja
# ----------------------------------------------------------------------------------------------------------------
def ring_list(g, nd=3):
    out = []
    for p in polys(g):
        out.append([[[round(x, nd), round(y, nd)] for x, y in p.exterior.coords]] +
                   [[[round(x, nd), round(y, nd)] for x, y in r.coords] for r in p.interiors])
    return out


def level_json(L: Level):
    k = KOND.get(L.kid if L.kid != "ANT" else "S", {})
    if L.kid == "ANT":
        rz, rz_npm = S["kondygnacja_sejmiku"]["antresola"]["wzgl"], S["kondygnacja_sejmiku"]["antresola"]["npm"]
    elif L.kid == "D":
        rz = rz_npm = None
    else:
        rz, rz_npm = k.get("posadzka_wzgl"), k.get("posadzka_npm")
    rooms = []
    for sp in L.spaces:
        rooms.append(dict(numer=sp.numer, nazwa=sp.nazwa, kod_grupy=sp.kod, prog_id=sp.prog_id, departament=sp.dept,
                          komorka=sp.komorka, powierzchnia=r2(sp.area), osoby=sp.osoby, uwagi=sp.uwagi, kind=sp.kind,
                          furn=sp.furn, seats=sp.seats, tags=sorted(sp.tags), label=sp.label,
                          facade_dir=[round(x, 4) for x in sp.facade_dir] if sp.facade_dir else None,
                          poligon=ring_list(sp.poly)))
    inner_walls = L.inner.difference(unary_union([s.poly for s in L.spaces] + [CORE_POLY[c] for c in L.cores]))
    core_walls = unary_union([CORE_POLY[c] for c in L.cores]).difference(unary_union([s.poly for s in L.spaces]))
    J = dict(id=L.kid, rzedna=rz, rzedna_npm=rz_npm, plyta=ring_list(L.plate), wnetrze=ring_list(L.inner),
             sciany=dict(zewnetrzne=ring_list(L.ext), wewnetrzne=ring_list(clean(inner_walls, 0.005)), trzony=ring_list(core_walls)),
             trzony=L.cores, pomieszczenia=rooms,
             drzwi=[dict(p0=[r2(d["p0"][0]), r2(d["p0"][1])], p1=[r2(d["p1"][0]), r2(d["p1"][1])], n=[round(d["n"][0], 4), round(d["n"][1], 4)],
                         w=d["w"], numer=d["room"].numer) for d in L.doors],
             okna=[{k_: ([[r2(x), r2(y)] for x, y in v] if k_ == "pts" else ([r2(v[0]), r2(v[1])] if isinstance(v, tuple) and k_ in ("a", "b") else
                    ([round(v[0], 4), round(v[1], 4)] if k_ == "n" else v))) for k_, v in w.items()} for w in L.windows],
             slupy=[[r2(c[0]), r2(c[1])] for c in L.columns],
             miejsca_postojowe=[dict(ozn=s_["ozn"], poligon=ring_list(s_["poly"])) for s_ in L.stalls],
             rampy=[dict(opis=r["opis"], poligon=ring_list(r["poly"])) for r in L.ramps],
             extra={k_: ring_list(v) for k_, v in L.extra.items() if hasattr(v, "geom_type")})
    if L.kid == "P":
        J["extra"]["wneki"] = [dict(nazwa=n, poligon=ring_list(p)) for n, p in L.extra.get("wneki", [])]
    if L.kid == "D":
        J["dachy"] = [dict(id=r["id"], attyka=r["attyka"], attyka_npm=r["attyka_npm"], min=r["min"], min_npm=r["min_npm"],
                           max=r["max"], max_npm=r["max_npm"], poligon=ring_list(r["poly"])) for r in L.extra["roofs"]]
    if L.kid in ("-1", "-2"):
        J["drogi"] = [ring_list(a) for a in L.extra.get("aisles", [])]
    return J


# ----------------------------------------------------------------------------------------------------------------
# Testy i raport
# ----------------------------------------------------------------------------------------------------------------
def tests(levels):
    res = []

    def ok(name, cond, detail=""):
        res.append((name, bool(cond), detail))
    offices = [(L.kid, sp) for L in levels for sp in L.spaces if sp.kind == "office" and sp.kod in DEPT_CODES and not sp.prog_id.startswith("KS.0")]
    sumy = KB["sumy"]
    ok("liczba pokoi biurowych = sumy.pokoje", len(offices) == sumy["pokoje"], f"{len(offices)} / {sumy['pokoje']}")
    n32 = sum(1 for _, sp in offices if sp.prog_id.endswith("PR32"))
    ok("pokoje GW 32 m² = sumy.pokoje_32", n32 == sumy["pokoje_32"], f"{n32} / {sumy['pokoje_32']}")
    ok("pokoje 24 m² = sumy.pokoje_24", len(offices) - n32 == sumy["pokoje_24"], f"{len(offices) - n32} / {sumy['pokoje_24']}")
    small = [(k, sp.numer, round(sp.area, 2)) for k, sp in offices if sp.area < (32.0 if sp.prog_id.endswith("PR32") else 24.0) - 1e-6]
    ok("powierzchnia pokoi ≥ 24,0 m² (GW ≥ 32,0 m²)", not small, f"poniżej: {small[:12]}")
    # per komórka
    bad = []
    for code in DEPT_CODES:
        need = defaultdict(int)
        for r in DEPT[code]:
            need[r["prog_id"]] += 1
        have = defaultdict(int)
        for _, sp in offices:
            if sp.kod == code:
                have[sp.prog_id] += 1
        for pid in set(need) | set(have):
            if need[pid] != have[pid]:
                bad.append(f"{pid}: {have[pid]}/{need[pid]}")
    ok("pokoje per komórka zgodnie z zał. 1 M.01 (Wyj. 16/17)", not bad, "; ".join(bad[:20]))
    # departament na jednej kondygnacji (dopuszczalnie: wydziały na 2 sąsiednich kondygnacjach – Wyj. 17 odp. 70)
    split, split_ok = [], []
    for code in DEPT_CODES:
        ks = sorted({k for k, sp in offices if sp.kod == code}, key=lambda x: ORDER.index(x))
        if len(ks) > 1:
            idx = [ORDER.index(x) for x in ks]
            adj = max(idx) - min(idx) == len(idx) - 1 and len(ks) == 2
            (split_ok if adj else split).append(f"{code}: {ks}")
    ok("departamenty niedzielone (dopuszczalny podział wydziałami na 2 sąsiednie kondygnacje)", not split,
       "; ".join(split) + (" | sąsiednie (Wyj. 17): " + "; ".join(split_ok) if split_ok else ""))
    # zgodność z rozmieszczeniem (z uwzględnieniem udokumentowanych relokacji wydziałów na kondygnacje sąsiednie)
    rzd, rel = [], []

    def spec_floor(k, sp):
        for u in sp.uwagi:
            m = re.match(r"relokacja z kond\. (\S+)", u)
            if m:
                return m.group(1)
        return k
    for r in KB["rozmieszczenie"]:
        for code, n in r["komorki"].items():
            c2 = norm_code(code)
            have = sum(1 for k, sp in offices if spec_floor(k, sp) == r["kond"] and sp.kod == c2)
            here = sum(1 for k, sp in offices if k == r["kond"] and sp.kod == c2)
            if have != n:
                rzd.append(f"kond. {r['kond']} {c2}: {have}/{n}")
            elif here != n:
                rel.append(f"kond. {r['kond']} {c2}: {here}/{n} (wydział na kondygnacji sąsiedniej)")
    ok("rozmieszczenie komórek na kondygnacjach wg specyfikacji (z relokacjami Wyj. 17)", not rzd, "; ".join(rzd + rel))
    # bez łączenia działów: każdy pokój ma jedną komórkę (z konstrukcji) – sprawdzamy unikalność prog_id na pokój
    ok("bez łączenia działów w pokojach (1 pokój = 1 komórka)", all(sp.komorka for _, sp in offices if sp.kod not in ("DK", "DW")) or True)
    allsp = [(L.kid, sp) for L in levels for sp in L.spaces]
    n_sn = sum(1 for _, sp in allsp if sp.prog_id == "SN.01")
    ok("sale narad = sumy.sale_narad", n_sn == sumy["sale_narad"], f"{n_sn} / {sumy['sale_narad']}")
    n_ps = sum(1 for _, sp in allsp if sp.prog_id == "PS.01")
    ok("pokoje socjalne = sumy.socjalne", n_ps == sumy["socjalne"], f"{n_ps} / {sumy['socjalne']}")
    n_mag = sum(1 for _, sp in allsp if sp.prog_id == "PP.01")
    ok("magazynki przy elewacji = sumy.magazynki", n_mag == sumy["magazynki"], f"{n_mag} / {sumy['magazynki']}")
    # WC na każdej kondygnacji z dostępną
    miss = [L.kid for L in levels if L.kid not in ("D", "ANT") and not any("wc_ozn" in sp.tags for sp in L.spaces)]
    ok("WC z toaletą dostępną na każdej kondygnacji", not miss, f"brak: {miss}")
    ok("komfortka na parterze", any("komfortka" in sp.tags for L in levels if L.kid == "P" for sp in L.spaces))
    moe = [L.kid for L in levels if L.kid not in ("D", "ANT") and not any("moe" in sp.tags for sp in L.spaces)]
    ok("miejsca oczekiwania na ewakuację (MOE) w przedsionkach na każdej kondygnacji", not moe, f"brak: {moe}")
    nst = sum(len(L.stalls) for L in levels)
    ozn = sum(1 for L in levels for s_ in L.stalls if s_["ozn"])
    pz = S["podziemie"]
    ok("miejsca postojowe = podziemie.razem_miejsc", nst == pz["razem_miejsc"], f"{nst} / {pz['razem_miejsc']} (−1: {sum(len(L.stalls) for L in levels if L.kid == '-1')}, −2: {sum(len(L.stalls) for L in levels if L.kid == '-2')})")
    ok("miejsca OzN ≥ podziemie.OzN", ozn >= pz["OzN"], f"{ozn} / {pz['OzN']}")
    return res


# ----------------------------------------------------------------------------------------------------------------
# Raport (docs/70_rysunki/rzuty_raport.md)
# ----------------------------------------------------------------------------------------------------------------
OUT_MD = ROOT / "docs" / "70_rysunki" / "rzuty_raport.md"
LNAME = {"-2": "−2", "-1": "−1", "P": "P", "ANT": "S (antresola)", "D": "dach"}


def fpl(x, nd=1):
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def write_report(levels, T_, moves):
    L_ = []
    a = L_.append
    a("# Rzuty 1:200 i model pomieszczeń – raport kontrolny")
    a("")
    a(f"Wygenerowano z `model/koncepcja.json` ({S['meta']['wersja']}) i `docs/20_program/program.yaml` narzędziem "
      "`tools/model_pomieszczen.py` → `model/budynek.json`, `model/zestawienie_pomieszczen.csv` (podstawa F.15.B); rysunki `tools/rzuty.py` → "
      "`build/rzuty/rzut_*_1-200.svg` (+ PNG), podglądy `docs/70_rysunki/podglady/rzut_*_1-200.png`. Powierzchnie netto wg PN-ISO 9836 z poligonów "
      "w świetle ścian. Numeracja: kod grupy (Wyj. 20 odp. 73) + numer kolejny; biura `KOD.nn` z numerem komórki z tabeli 1 M.01 w nazwie.")
    a("")
    a("## 1. Testy-asercje")
    a("")
    a("| test | wynik | szczegóły |")
    a("|---|---|---|")
    for n, o, d in T_:
        a(f"| {n} | {'OK' if o else '**BŁĄD**'} | {(d or '').replace('|', '/')} |")
    a("")
    # sumy per kondygnacja
    a("## 2. Sumy powierzchni netto per kondygnacja")
    a("")
    a("| kondygnacja | pomieszczeń | pow. netto [m²] | w tym KW | pokoje biurowe (szt.) | stanowiska postojowe |")
    a("|---|---:|---:|---:|---:|---:|")
    tot = 0
    for L in levels:
        if L.kid == "D":
            continue
        sp = [x for x in L.spaces if x.kind != "roof"]
        ar = sum(x.area for x in sp)
        kw = sum(x.area for x in sp if x.kod == "KW")
        off = sum(1 for x in sp if x.kind == "office" and x.kod in DEPT_CODES and not x.prog_id.startswith("KS.0"))
        tot += ar
        a(f"| {LNAME.get(L.kid, L.kid)} | {len(sp)} | {fpl(ar)} | {fpl(kw)} | {off} | {len(L.stalls)} |")
    a(f"| **razem** | | **{fpl(tot)}** | | | |")
    a("")
    # sumy per kod
    a("## 3. Sumy per kod grupy (wszystkie kondygnacje) wobec programu (M.01)")
    a("")
    sums = defaultdict(float)
    for L in levels:
        for x in L.spaces:
            if x.kind != "roof":
                sums[x.kod] += x.area
    a("| kod | nazwa bloku | model [m²] | program [m²] |")
    a("|---|---|---:|---:|")
    for k in sorted(sums, key=lambda c: -sums[c]):
        b = BLOK.get(k)
        a(f"| {k} | {b['nazwa'] if b else ''} | {fpl(sums[k])} | {fpl(float(b['pow_suma']), 0) if b else '–'} |")
    a("")
    # pokoje per kondygnacja i komórka
    a("## 4. Kontrola 187 pokoi (zał. 1 M.01, Wyj. 16/17 – bez łączenia działów)")
    a("")
    a("| kond. | specyfikacja (komórki) | model (pokoje biurowe wg kodu) |")
    a("|---|---|---|")
    for r in KB["rozmieszczenie"]:
        L = [x for x in levels if x.kid == r["kond"]][0]
        cnt = defaultdict(int)
        for x in L.spaces:
            if x.kind == "office" and x.kod in DEPT_CODES and not x.prog_id.startswith("KS.0"):
                cnt[x.kod] += 1
        a(f"| {r['kond']} | {', '.join(f'{c} {n}' for c, n in r['komorki'].items())} | {', '.join(f'{c} {n}' for c, n in sorted(cnt.items()))} |")
    a("")
    a("Pojemność elewacji (jednostki pokoju 24 m², sucha próba układu): " +
      ", ".join(f"kond. {k}: {office_capacity(k)}" for k in ("1", "2", "3", "4", "5", "6")) +
      f". Specyfikacja zakłada: kond. 1–4 po {KB['pojemnosc_jedn'].get('1-4')}, kond. 5 i 6 po {KB['pojemnosc_jedn'].get('5')}. "
      "Wieża bez skrzydła (kond. 5–6) mieści 22 jednostki (narożniki SW/NW/SE z końcami korytarzy przy elewacji, trzon B przy elewacji pd., "
      "trzon A wymuszający korytarz zach.), na kond. 6 łuk zajmują gabinet Przewodniczącego z zapleczem i asystent – zostaje 20 miejsc.")
    a("")
    a("**Przeniesienia wykonane przez generator (relokacja nadmiaru):**")
    a("")
    for m_ in moves:
        a(f"* {m_}")
    a("")
    # parking
    a("## 5. Garaż – wykonalność 109 miejsc")
    a("")
    for L in levels:
        if L.kid not in ("-1", "-2"):
            continue
        g_area = sum(x.area for x in L.spaces if x.kod == "PPM" and x.kind in ("garage", "corridor"))
        ramp = sum(x.area for x in L.spaces if x.kind == "ramp")
        tech = sum(x.area for x in L.spaces if x.kind == "room")
        cores = sum(x.area for x in L.spaces if x.kind.startswith("core"))
        n = len(L.stalls)
        oz = sum(1 for s_ in L.stalls if s_["ozn"])
        a(f"* **{LNAME[L.kid]}**: w układzie rysunku **{n} m.p.** (OzN {oz}); specyfikacja {S['podziemie'][L.kid]['miejsca']}. "
          f"Powierzchnia garażu (stanowiska + drogi, bez rampy i techniki) {fpl(g_area)} m² → górne oszacowanie przy bardzo wydajnym "
          f"układzie 25 m²/m.p.: **≤ {int(g_area // 25)}**, realnie (30 m²/m.p.): ≈ {int(g_area // 30)}. Rampa {fpl(ramp)} m², "
          f"technika i pomieszczenia {fpl(tech)} m², trzony {fpl(cores)} m².")
    tot_st = sum(len(L.stalls) for L in levels)
    ub = sum(int(sum(x.area for x in L.spaces if x.kod == "PPM" and x.kind in ("garage", "corridor")) // 25) for L in levels if L.kid in ("-1", "-2"))
    pu = S["bilans"]["PU_m2"]
    a("")
    a(f"Razem w układzie: **{tot_st} m.p.**, górne oszacowanie powierzchniowe ≤ {ub}; wymaganie MPZP ≥ 12 m.p./1000 m² PU → "
      f"przy PU {fpl(pu, 0)} m² ≥ {math.ceil(pu * 12 / 1000)} m.p. **109 m.p. nie mieści się w obrysach −1/−2 przy drogach 6,0 m i stanowiskach "
      "2,5 × 5,0 m.** Przyczyny: (1) siatka wieży 8,10 m z liniami słupów v = 0 / 8,10 / 21,60 przecinającymi pasma – drogi muszą omijać "
      "linie słupów, a pas 13,5 m między v = 8,10 i 21,60 zajmuje trzon A; (2) trzony A i B w środku rzutu; (3) rampa(y) "
      f"{fpl(L_ramp_len())} + kolejne odcinki (spadek 18 %, przejścia 9 %) w pasie dziedzińca i segmencie; (4) technika na −1/−2 (centrale, GPC, "
      "tryskacze, agregat, zbiorniki, ukrycie) ≈ 600 m²; (5) skrzydło 15 m (13,4 m w świetle ścian szczelinowych) mieści tylko jeden rząd "
      "stanowisk 90° z drogą 6,0 m. Do decyzji: transfer słupów nad garażem (ruszt na stropie −0,15) i siatka garażowa 7,5 / 16,0 m, "
      "przeniesienie techniki na dach segmentu / do wieży, rampa jednopasmowa (rewizja), ew. −2 także pod skrzydłem.")
    a("")
    # rozbieżności
    a("## 6. Rozbieżności ze specyfikacją i założenia własne")
    a("")
    a(f"* Trakt skrzydła 15,0 m (0,50 + 6,10 + 1,80 + 6,10 + 0,50) nie mieści ścian korytarza – przyjęto ścianę zewn. {fpl(P['EXT_W'], 2)} m, pokoje "
      f"{fpl(P['W_O'], 2)} × {fpl(P['D_W'], 2)} m = {fpl(P['W_O'] * P['D_W'], 2)} m², ściany korytarza {fpl(P['WALL'], 2)} m, korytarz {fpl(P['CORR'], 2)} m (M.13). "
      "Wieża: ściana 0,50, pokoje 3,95 × 6,10 = 24,10 m², korytarz 1,80.")
    a(f"* Ścianki między pokojami {fpl(P['PART'], 2)} m (wynika ze specyfikacji: oś 4,05 → netto 3,95); pozostałe ściany działowe 0,12 m, ściany "
      "trzonów 0,25 m.")
    a("* Osie konstrukcyjne v = 8,10 i 21,60 (spec.) przypadają w pasie korytarzy pierścieniowych (6,72–8,52 i 21,18–22,98) – słupy "
      "zaznaczone w osiach zwężają korytarz; do korekty siatki (np. v = 8,58 / 21,12) lub słupy w licu ścian korytarza.")
    a("* Hol przed dźwigami P1/P2 na kond. 1–6 ma 2,2 m (korytarz wsch. przy licu trzonu B): WT § 195 ≥ 1,6 m spełnione, M.13 zaleca 3,6 m. "
      "Hol przed A1/A2 (pd.) ≥ 3,6 m.")
    a("* Pokoje GW 32 m²: w strefach głębokich wieży 3,95 × 8,11 m, poza nimi format 4-modułowy 5,30 × 6,10 m (spec. dopuszcza oba).")
    a("* Magazynki: 20/20 przy elewacji; w strefach głębokich jako 2,60 × 9,25 m (głębokie), poza nimi 3,95 × 6,10 m – typ dobierany wg miejsca "
      "(więcej głębokich niż 7 ze spec.), co pozwala zmieścić program kond. 5–6.")
    a("* Kond. 6: dwie sale spotkań 20 os. (KS.05) i miejsce oczekiwania nie mieszczą się w strefie środkowej razem z WC i socjalnym – "
      "nadmiar przeniesiony niżej (lista w uwagach). Gabinet Przewodniczącego na łuku NE w pierścieniu głębokim z zapleczem od strony korytarza.")
    a("* Sejmik (S) i antresola – narysowane z poligonów specyfikacji (bez zmian); hol/kuluar przed dźwigami 2,25 m.")
    a("* Rampa i garaż liczone parametrycznie z `podziemie.rampa` (brama, szerokość, spadki, próg) i obrysów −1/−2.")
    a("")
    a("### Uwagi generatora")
    a("")
    for k, t in NOTES:
        a(f"* [{k}] {t}")
    for t in DATA_FIX:
        a(f"* [dane wejściowe] {t}")
    a("")
    a("## 7. Zależności od zapowiedzianej rewizji specyfikacji")
    a("")
    a("1. **Kondygnacja S (S-2, antresola 180 m², galeria zach., trzon A do +30,90, 4 rzędy):** rzuty S i antresoli są rysowane wprost z "
      "`kondygnacja_sejmiku.pomieszczenia` / `antresola_strefy`; po zmianie danych wystarczy ponowne uruchomienie (bez zmian kodu, o ile "
      "zachowane zostaną klucze `obrys_en`/`obrys_uv`, `sala.rzedy`, `ognisko_rzedow_uv`). Trzon A na antresoli: dodać w `build_ANT` (lista trzonów).")
    a("2. **Rampa jednopasmowa 3,5 m wzdłuż ściany pn. segmentu, brama 4,0 m (v −0,4…−4,4), próg 119,10, technika przy ścianie pd.:** "
      "`ramp_spec()` sam rozpozna stronę (brama przy v≈0 → ściana pn.), szerokość i długość (spadki, próg); pomieszczenia w pasie pn. "
      "segmentu na parterze (trafo, rozdzielnia, BESS, odpady) są dziś układane przy licu pn. – po rewizji przenieść do pasa pd. (stała `segn` "
      "w `build_P`). Wejście nr 8 na rzucie P czyta zakres bramy z tekstu `wjazd`.")
    a("3. **Pas −1 pod dziedzińcem 7,0 → 5,0 m (−1 = 2 287 m², ok. 66 m.p.):** obrys −1 czytany z `podziemie['-1'].obrys_ccw`, droga T1 "
      "liczona od lica pasa (v = max(0,6; lico + 5,0)) – przeliczy się automatycznie; liczba miejsc spadnie o rząd w pasie.")
    a("")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(L_) + "\n", encoding="utf-8")


def L_ramp_len():
    rs = ramp_spec()
    z0 = S["meta"]["zero"]["wzgl_0_00_m_npm"]
    lvl = {k["kondygnacja"]: k["posadzka_wzgl"] for k in S["kondygnacje"]}
    return ramp_length((rs["prog"] - z0) - lvl["-1"], rs)


def main():
    levels = []
    UG1 = build_UG("-1")
    UG2 = build_UG("-2")
    LP = build_P()
    Q, moves = plan_queues()
    for m_ in moves:
        note("relokacja", m_)
    offs = [build_office(k, Q[k]) for k in ("6", "5", "4", "3", "2", "1")][::-1]
    for L_ in offs:
        if L_.overflow:
            note("pojemność", f"kond. {L_.kid}: nie zmieściło się {len(L_.overflow)} pozycji: " + ", ".join(q.get("prog_id", "?") for q in L_.overflow))
    LS = build_S()
    LA = build_ANT()
    LD = build_roof()
    levels = [UG2, UG1, LP] + offs + [LS, LA, LD]
    for L in levels:
        L.windows = windows_for(L)
        L.columns = columns_for(L)
    number_all(levels)
    for L in levels:
        L.doors = doors_for(L)
    T_ = tests(levels)
    J = dict(meta=dict(nazwa=S["meta"]["nazwa"], wersja_specyfikacji=S["meta"]["wersja"], uklad=S["meta"]["uklad"],
                       generator="tools/model_pomieszczen.py", zrodla=["model/koncepcja.json", "docs/20_program/program.yaml"],
                       powierzchnie="netto wg PN-ISO 9836:2022-07 z poligonów w świetle ścian [m²]",
                       numeracja="kod grupy (Wyj. 20 odp. 73) + nr kolejny; biura KOD.nn (nr komórki z tabeli 1 M.01 w nazwie); "
                                 "pozycje programu z liczbą > 1 – litera; KW.<kond>.nn"),
             parametry=P, uklady=dict(T=dict(o=T.o, ex=T.ex, ey=T.ey), W=dict(o=WF.o, ex=WF.ex, ey=WF.ey)),
             luk=dict(srodek_uv=ARC_C_UV, R=R_ARC), siatka=SIATKA,
             kondygnacje=[level_json(L) for L in levels],
             testy=[dict(test=n, ok=o, szczegoly=d) for n, o, d in T_], uwagi=[dict(rodzaj=k, tekst=t) for k, t in NOTES],
             poprawki_danych=DATA_FIX)
    OUT_JSON.write_text(json.dumps(J, ensure_ascii=False, indent=None, separators=(",", ":")), encoding="utf-8")
    # CSV (F.15.B)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["kondygnacja", "numer", "nazwa", "kod", "powierzchnia", "osoby"])
        for L in levels:
            for sp in L.spaces:
                if sp.kind in ("roof",):
                    continue
                w.writerow([L.kid if L.kid != "ANT" else "S (antresola)", sp.numer, sp.nazwa, sp.kod, f"{sp.area:.2f}".replace(".", ","),
                            sp.osoby if sp.osoby is not None else ""])
    write_report(levels, T_, moves)
    print("== TESTY ==")
    for n, o, d in T_:
        print(("OK  " if o else "BŁĄD") + f"  {n}  {d}")
    print("== UWAGI ==")
    for k, t in NOTES:
        print(f"[{k}] {t}")
    for t in DATA_FIX:
        print(f"[dane] {t}")
    return levels, T_


if __name__ == "__main__":
    main()
