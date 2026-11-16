#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
site_extract.py - geometria terenu i otoczenia dla konkursu UMWD (Wroclaw, ul. Mazowiecka / Wybrzeze J. Slowackiego).

Odtwarza (deterministycznie) z materialow konkursowych:
  * model/site.json                                   - dane do modelu 3D i rysunkow 1:500 / 1:200
  * docs/30_lokalizacja/img/site_kontrola.png         - kontrolny podglad warstw (siatka 10 m)
  * docs/30_lokalizacja/geometria.md                  - opis metody, dokladnosci, warstw, liczby

Zrodla (zalaczniki merytoryczne, wersja "pop.13.02.2026"):
  M.02  mazowiecka_e-mapa.dwg (mapa do celow projektowych ZGKIKM.TM.6640.4638.2025, 01.10.2025),
        model terenu/mazowiecka_model terenu.dwg, model terenu/mazowiecka_pikiety do nmt.txt,
        zielen/mazowiecka_zielen.dwg, zielen/mazowiecka_drzewa.txt, e-mapa pdf (kontrola)
  M.04  Mapa schematyczna WRO UMWD - M.04.dwg (+ .pdf do niezaleznej kontroli georeferencji)
  M.07  Inwentaryzacja Mazowiecka 19 (s. 9-10: wysokosc / rzedne - wartosci wpisane recznie, patrz BUILDING_NOTES)

Metoda: DWG (AutoCAD 2000) -> JSON przez libredwg skompilowane do WebAssembly (pakiet npm
@mlightcad/libredwg-web@0.8.2, uruchamiany w Node.js, instalowany do katalogu cache z --ignore-scripts).
DGN (MicroStation V8) nie jest czytany - GDAL obsluguje tylko DGN v7; tresc DGN dubluje DWG.

Uklad: PL-2000 strefa 6 (EPSG:2177, X=polnoc, Y=wschod), wysokosci PL-EVRF2007-NH (EPSG:9651).
Uklad lokalny projektu: e = Y - 6433500.00, n = X - 5664100.00 [m].

Uzycie (materialy traktowane jako dane niezaufane - uruchamiac z -I):
  python3 -I tools/site_extract.py [--root /home/user/aihouse/umwd] [--cache DIR] [--no-md] [--no-png]
Wymagania: python3 (numpy, scipy, shapely, matplotlib, pyproj, pymupdf), node>=20 + npm (tylko przy
pierwszej konwersji DWG; potem cache JSON).
"""
import argparse
import collections
import datetime
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from scipy.spatial import Delaunay, cKDTree
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import linemerge, polygonize, unary_union

E0, N0 = 6433500.0, 5664100.0          # poczatek ukladu lokalnego (Y, X w PL-2000/6)
LIBREDWG_PKG = "@mlightcad/libredwg-web@0.8.2"
MAT_SUB = "00_materialy/_rozpak/5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026"
M02_SUB = "M.02 MAPA DO CELÓW PROJEKTOWYCH/M.02 MAPA DO CELÓW PROJEKTOWYCH"
M04_SUB = "M.04. MAPA SCHEMATYCZNA/M.04. MAPA SCHEMATYCZNA"
ROUND = 3

# --------------------------------------------------------------------------------------------
# Slownik warstw e-mapy (kody ZGKiKM Wroclaw). "pewnosc": pewna = potwierdzone opisem/legenda mapy
# lub jednoznaczna trescia; wniosek = interpretacja wlasna z tresci (etykiety, geometria).
# --------------------------------------------------------------------------------------------
LAYER_DICT = {
    "GESDZI": ("EGiB", "granice dzialek ewidencyjnych", "pewna (numery dzialek GESDZI_O)"),
    "GESDZI_O": ("EGiB", "numery dzialek (+ odnosniki)", "pewna"),
    "GESUZY": ("EGiB", "kontury uzytkow gruntowych", "pewna (oznaczenia B, Bi, Bp, Bz, dr, Tp, Wp)"),
    "GESUZY_O": ("EGiB", "oznaczenia uzytkow", "pewna"),
    "GESJOB": ("EGiB", "granica obrebu ewidencyjnego", "pewna (opisy 0022 Poludnie / 0001 Stare Miasto)"),
    "GESJAE": ("EGiB", "granica arkusza mapy ewidencyjnej", "pewna (opisy 'Arkusz nr 2/28')"),
    "GESBZO": ("EGiB", "obrysy budynkow", "pewna (etykiety funkcja+kondygnacje: m5, k5, b4, i1, t1)"),
    "GESBZO_O": ("EGiB", "etykiety budynkow: funkcja + liczba kondygnacji nadziemnych", "pewna"),
    "GESBLO": ("EGiB", "obrys bryly/bloku budynku (czesc o innej liczbie kondygnacji)", "wniosek"),
    "GESBPB": ("EGiB", "linia przerywana w obrysie budynku - przejscie/przejazd bramowy lub nawis", "wniosek"),
    "GESBTO": ("EGiB", "drobny obiekt przy budynku (taras/podest/zejscie)", "wniosek"),
    "GESSCH": ("EGiB", "schody przy budynkach", "wniosek (szrafura schodow)"),
    "GESIPP": ("EGiB", "drobne elementy przy narozach budynkow (przypory/pilastry?)", "wniosek"),
    "GEPPGD": ("EGiB", "punkty graniczne", "pewna"),
    "GEPADR": ("EGiB", "punkty adresowe", "pewna (GEPADR_O)"),
    "GEPADR_O": ("EGiB", "numery porzadkowe", "pewna"),
    "GELULI_O": ("BDOT500", "nazwy ulic / obiektow", "pewna"),
    "GSLKRW": ("BDOT500", "krawezniki", "wniosek (geometria, zgodnosc z warstwa 'kraweznik')"),
    "GSSKOA": ("BDOT500", "krawedzie jezdni", "wniosek (opisy j.kb., j.mb., j.i.)"),
    "GSSKOA_O": ("BDOT500", "nawierzchnia jezdni: j.kb.=kostka bet., j.mb.=masa bitum., j.i.=inna", "wniosek"),
    "GSSKOD": ("BDOT500", "krawedzie chodnikow / ciagow pieszych", "wniosek (opisy ch.bt., ch.kb., ch.mb., ch.zw., ch.i.)"),
    "GSSKOD_O": ("BDOT500", "nawierzchnia chodnika: bt.=beton, kb.=kostka bet., mb.=masa bitum., zw.=zwir, i.=inna", "wniosek"),
    "GSLTTK": ("BDOT500", "tory tramwajowe (osie)", "wniosek (przebieg na Most Grunwaldzki)"),
    "GSLKOG": ("BDOT500", "ogrodzenia (linie + slupki)", "wniosek"),
    "GSSKOG": ("BDOT500", "elementy ogrodzen (bramy/furtki)", "wniosek"),
    "GSSUTR": ("BDOT500", "trawniki / tereny zieleni (obrys + symbole '||')", "wniosek (symbol trawnika)"),
    "GSSZSN": ("BDOT500", "skarpy (nieumocnione) - linia gorna + kreski", "wniosek"),
    "GSSZSU": ("BDOT500", "skarpy umocnione (nabrzeze)", "wniosek"),
    "GSSZMO": ("BDOT500", "mury oporowe / sciany przyczolka", "wniosek"),
    "GSSDSO": ("BDOT500", "mury / budowle liniowe (obrys)", "wniosek"),
    "GSLDSO": ("BDOT500", "mury / budowle liniowe (linia)", "wniosek"),
    "GSSSCK": ("BDOT500", "schody terenowe (szrafura)", "wniosek"),
    "GSSWWP": ("BDOT500", "linia brzegu wod plynacych (Odra, Olawa)", "pewna (opisy rz. Odra / rz. Olawa)"),
    "GSSWWP_O": ("BDOT500", "nazwy rzek", "pewna"),
    "GSSZAD": ("BDOT500", "symbole zadrzewien/zakrzewien (?)", "wniosek - niepewny"),
    "GSSIIN": ("BDOT500", "inne obiekty (opis 'ib')", "wniosek - niepewny"),
    "GSSIPD": ("BDOT500", "podesty/obiekty przy przyczolku mostu", "wniosek - niepewny"),
    "GSSROW": ("BDOT500", "rowek/sciek", "wniosek - niepewny"),
    "GSSOTW": ("BDOT500", "inny obiekt liniowy (PRZER3-1)", "wniosek - niepewny"),
    "GSSBKP": ("BDOT500", "drobna budowla (solid)", "wniosek - niepewny"),
    "GSLTZI": ("BDOT500", "linia zieleni ('it')", "wniosek - niepewny"),
    "GSPRDL": ("BDOT500", "drzewa lisciaste (e-mapa)", "pewna (symbol)"),
    "GSPRDI": ("BDOT500", "drzewa iglaste (e-mapa)", "pewna (symbol)"),
    "GSPWPS": ("BDOT500", "punkty wysokosciowe sytuacyjne (2 miejsca po przecinku)", "wniosek"),
    "GSPWPN": ("BDOT500", "punkty wysokosciowe (1 miejsce po przecinku - terenowe, mniej dokladne)", "wniosek"),
    "GSPSSP": ("osnowa", "punkty osnowy sytuacyjnej (nr 174xx)", "wniosek"),
    "GSPSSH": ("osnowa", "punkty osnowy wysokosciowej (nr 5070, 5260)", "wniosek"),
    "GULWPR": ("GESUT", "przewody wodociagowe (w, wo)", "pewna (etykiety)"),
    "GULKPR": ("GESUT", "przewody kanalizacyjne (k, ks=sanitarna, kd=deszczowa, ko=ogolnosplawna)", "pewna (etykiety)"),
    "GULGPR": ("GESUT", "przewody gazowe (g)", "pewna (etykiety)"),
    "GULEPR": ("GESUT", "przewody elektroenergetyczne (eN=nn, eS=SN)", "pewna (etykiety)"),
    "GULTPR": ("GESUT", "przewody telekomunikacyjne (t)", "pewna (etykiety)"),
    "GULCPR": ("GESUT", "przewod cieplowniczy (c)", "wniosek (kod C)"),
    "GULLOB": ("GESUT", "obudowa/oslona przewodow (kanal, rura oslonowa)", "wniosek - niepewny"),
    "GUSIKP": ("GESUT", "obrysy studni / komor (kregi ok. 1 m, prostokaty)", "wniosek"),
    "GUSESE": ("GESUT", "obiekty elektroenergetyczne (szafy/zlacza, 'proj.e' = projektowane)", "wniosek"),
    "GUSIWZ": ("GESUT", "wlaz/obiekt telekom.", "wniosek"),
    "GUPPRZ": ("GESUT", "punkty z rzednymi uzbrojenia (opisy ulamkowe: gora/dol)", "wniosek"),
    "GUPELA": ("GESUT", "latarnie / slupy oswietleniowe", "wniosek"),
    "GUPESE": ("GESUT", "szafy elektroenergetyczne", "wniosek"),
    "GUPEUT": ("GESUT", "urzadzenia elektroenergetyczne", "wniosek"),
    "GUPGZA": ("GESUT", "zasuwy gazowe", "wniosek"),
    "GUPWZA": ("GESUT", "zasuwy wodociagowe", "wniosek"),
    "GUPWDT": ("GESUT", "hydranty", "wniosek"),
    "GUPWST": ("GESUT", "studnia wodociagowa", "wniosek"),
    "GUPKKS": ("GESUT", "kratki sciekowe (wpusty)", "wniosek"),
    "GUPTSZ": ("GESUT", "szafy telekomunikacyjne", "wniosek"),
    "GUPIWZ": ("GESUT", "wlazy (t, e, k)", "wniosek"),
    "GUPIKP": ("GESUT", "komory/studnie (symbol)", "wniosek"),
    "GUPISN": ("GESUT", "studnie (symbol)", "wniosek"),
    "GUPIST": ("GESUT", "slupy (opis proj.e)", "wniosek"),
    "GUPZCP": ("GESUT", "punkty zalamania/pikiety przewodow", "wniosek - niepewny"),
    "GUPXUT": ("GESUT", "urzadzenie nieokreslone (x)", "wniosek"),
    "GUPSUT": ("GESUT", "urzadzenie (s/ib)", "wniosek - niepewny"),
    "UZPUNE": ("GESUT", "punkty X2M (?)", "wniosek - niepewny"),
    "Warstwa 61": ("MPZP", "nakladka MPZP nr 372/602 (linie rozgraniczajace kolor 204, linie zabudowy i wydzielenie A kolor 230, obiekty dziedzictwa - szrafura 204, granica planow kolor 7)", "pewna (legenda mapy: 'Linie MPZP wrysowano na podstawie podkladu rastrowego ... SIP')"),
    "Warstwa 62": ("ramka", "granica obszaru aktualizacji mapy (linia szrafurowana)", "pewna (opis 3 mapy)"),
    "Warstwa 63": ("ramka", "ramka, wspolrzedne narozy, teksty wektorowe (krzywe), 'BRAK MPZP'", "pewna"),
    "kraweznik": ("pomiar NMT", "krawezniki (pomiar uzupelniajacy wykonawcy mapy)", "pewna (nazwa warstwy)"),
    "jezdnia": ("pomiar NMT", "jezdnie", "pewna"),
    "chodnik": ("pomiar NMT", "chodniki", "pewna"),
    "obszar_utwardzony": ("pomiar NMT", "powierzchnie utwardzone", "pewna"),
    "trawnik": ("pomiar NMT", "trawniki", "pewna"),
    "ogrodzenie": ("pomiar NMT", "ogrodzenia", "pewna"),
    "furtka": ("pomiar NMT", "furtki", "pewna"),
    "plac_zabaw": ("pomiar NMT", "plac zabaw", "pewna"),
    "zakrzaczenie": ("pomiar NMT", "zakrzaczenia ('it')", "pewna"),
    "drzewa_lisciaste": ("pomiar NMT", "drzewa lisciaste (nr D...)", "pewna"),
    "drzewa_iglaste": ("pomiar NMT", "drzewa iglaste (nr I...)", "pewna"),
    "hydranty": ("pomiar NMT", "hydranty", "pewna"),
    "kratki_sciekowe": ("pomiar NMT", "kratki sciekowe", "pewna"),
    "latarnie": ("pomiar NMT", "latarnie", "pewna"),
    "wlazy_duze_prostokatne": ("pomiar NMT", "wlazy prostokatne", "pewna"),
    "wlazy_okragle": ("pomiar NMT", "wlazy okragle", "pewna"),
    "zasuwy": ("pomiar NMT", "zasuwy", "pewna"),
    "txt": ("pomiar NMT", "rzedne pikiet (MTEXT) + symbol punktu", "pewna"),
}

UTIL_TYPES = {
    "GULWPR": "wodociag", "GULKPR": "kanalizacja", "GULGPR": "gaz", "GULEPR": "elektroenergetyka",
    "GULTPR": "telekomunikacja", "GULCPR": "cieplownictwo", "GULLOB": "obudowa/oslona",
}

# Adresy (numery z GEPADR_O) -> ulica. Mazowiecka 17/19 potwierdza M.07; pozostale - wniosek z
# przebiegu numeracji i polozenia frontow (Wybrzeze J. Slowackiego biegnie wzdluz wsch. pierzei).
ADDRESS_STREET = {
    "19": ("Mazowiecka", "pewna (M.07 s.9: kamienica na dz. 11/3)"),
    "17": ("Mazowiecka", "pewna (M.07: 'Mazowiecka 17 - budynek sasiedni')"),
    "21-29": ("Mazowiecka", "wniosek (punkt adresowy na niezabudowanej dz. inwestycyjnej)"),
    "30-34": ("Mazowiecka", "wniosek (zach. pierzeja Mazowieckiej)"),
    "5": ("Wybrzeze J. Slowackiego", "pewna (M.08: Wybrzeze J. Slowackiego 5)"),
    "6": ("Wybrzeze J. Slowackiego", "wniosek"),
    "7": ("Wybrzeze J. Slowackiego", "wniosek"),
    "8": ("Wybrzeze J. Slowackiego", "wniosek"),
    "8a": ("Wybrzeze J. Slowackiego", "wniosek"),
    "9": ("Wybrzeze J. Slowackiego", "wniosek - niepewny (budynek w glebi kwartalu)"),
    "5b": ("Wybrzeze J. Slowackiego", "wniosek (obiekt nad Odra/Olawa)"),
}

# Kody funkcji budynku (etykiety EGiB/BDOT500) - interpretacja wg rozporzadzenia w sprawie BDOT500/mapy
# zasadniczej (2021): litera = funkcja, cyfra = liczba kondygnacji nadziemnych.
BUILDING_FUNC = {
    "m": "mieszkalny", "b": "biurowy", "i": "inny niemieszkalny", "t": "transportu i lacznosci",
    "k": "oswiaty, nauki, kultury lub sportu", "h": "handlowo-uslugowy", "p": "przemyslowy",
    "s": "szpitala/opieki medycznej", "z": "magazynowy/zbiornik",
}

# Dane uzupelniajace z inwentaryzacji (odczyt wizualny - wartosci wpisane, zrodlo podane).
BUILDING_NOTES = {
    "Mazowiecka 19": {
        "zrodlo": "M.07 Inwentaryzacja Mazowiecka 19 (03.2021): s.9 (rzut dachu - opis 'Budynek w liczbach'), s.10 (przekroj A-A)",
        "rok_budowy": 1880,
        "kondygnacje_nadziemne_inwentaryzacja": 6,
        "kondygnacje_podziemne": 1,
        "powierzchnia_zabudowy_m2_inwentaryzacja": 259.00,
        "wysokosc_budynku_wg_opisu_m": "ok. 20",
        "rzedne_wzgledne_przekroj_AA": {"poziom_0.00": "wejscie z ul. Mazowieckiej (parter)", "ul_Mazowiecka": -0.73,
                                        "podworze": -1.15, "spoczniki_klatki": [-0.85, 1.78, 5.51, 9.28, 13.05, 16.79],
                                        "poddasze": 18.30},
        "attyka_wzgl_0.00_m_odczyt_graficzny": 21.0,
        "attyka_dokladnosc_m": 0.3,
        "dach": "plaski/niskospadowy (papa, spadek ok. 5%), murek attykowy od ulicy, kominy murowane ok. +0.9 m nad attyke",
        "sciana_szczytowa": "pln. sciana szczytowa przy granicy z dz. 11/6 (obszar inwestycji); okna w scianie szczytowej przeznaczone do zamurowania w ramach inwestycji towarzyszacej (M.07, strona tytulowa)",
    },
    "Wybrzeze J. Slowackiego 5": {
        "zrodlo": "M.08 Inwentaryzacja Wybrzeze J. Slowackiego 5 (2001) - rzuty (skany), strona tytulowa",
        "sciana_szczytowa": "pln. sciana szczytowa od strony dz. 10/2 (dojazd); okno w scianie szczytowej lokalu na kondygnacji 2 (1 pietro) NIE jest przeznaczone do zamurowania - nalezy uwzglednic (M.08, strona tytulowa)",
    },
}

STOREY_H = 3.75   # m - wysokosc kondygnacji kamienic (z M.07: odstep spocznikow 3.73-3.77 m) - do szacunkow
BASE_RAISE = 0.75  # m - wyniesienie parteru nad chodnik (M.07: ul. Mazowiecka -0.73)
ROOF_ADD = 1.5     # m - attyka/gzyms ponad strop ostatniej kondygnacji (szacunek)


# ============================================================================================
# narzedzia ogolne
# ============================================================================================
def r3(v):
    return round(float(v), ROUND)


def r2(v):
    return round(float(v), 2)


def pts_r(pts, nd=ROUND):
    return [[round(float(x), nd), round(float(y), nd)] for x, y in pts]


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ccw(poly):
    return orient(poly, sign=1.0)


def poly_out(poly, nd=ROUND):
    """Polygon -> lista [e,n] CCW, bez powtorzenia pierwszego punktu."""
    p = ccw(poly)
    c = list(p.exterior.coords)[:-1]
    return pts_r(c, nd)


def azimuth(dx, dy):
    """azymut od polnocy siatki (os n), zgodnie z ruchem wskazowek zegara [deg]"""
    return (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0


def clean_text(t):
    t = re.sub(r"\\[A-Za-z][^;\\]*;", "", t)   # \fArial|b0..;
    t = t.replace("{", "").replace("}", "").replace("\\P", " ")
    return t.strip()


# ============================================================================================
# DWG -> JSON (libredwg WASM w node)
# ============================================================================================
NODE_SCRIPT = r"""
import { readFileSync, writeFileSync } from 'node:fs';
import { Dwg_File_Type, LibreDwg } from '@mlightcad/libredwg-web';
const [,, inp, outp] = process.argv;
const wasmDir = new URL('./node_modules/@mlightcad/libredwg-web/wasm/', import.meta.url).pathname;
const libredwg = await LibreDwg.create(wasmDir);
const dwg = libredwg.dwg_read_data(readFileSync(inp), Dwg_File_Type.DWG);
const db = libredwg.convert(dwg);
writeFileSync(outp, JSON.stringify(db, (k, v) => (typeof v === 'bigint' ? Number(v) : v)));
libredwg.dwg_free(dwg);
"""


def dwg_to_json(dwg_path, cache):
    cache.mkdir(parents=True, exist_ok=True)
    out = cache / ("%s_%s.json" % (re.sub(r"[^A-Za-z0-9_.-]", "_", dwg_path.stem), sha256(dwg_path)[:16]))
    if out.exists() and out.stat().st_size > 0:
        return out
    npm_dir = cache / "npm"
    npm_dir.mkdir(exist_ok=True)
    if not (npm_dir / "node_modules/@mlightcad/libredwg-web/wasm").exists():
        if not (npm_dir / "package.json").exists():
            (npm_dir / "package.json").write_text('{"name":"umwd-dwg","private":true,"type":"module"}\n')
        subprocess.run(["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund", LIBREDWG_PKG],
                       cwd=npm_dir, check=True)
    script = npm_dir / "dwg2json.mjs"
    script.write_text(NODE_SCRIPT)
    subprocess.run(["node", str(script), str(dwg_path), str(out)], check=True, cwd=npm_dir)
    return out


class Dwg:
    """Lekki czytnik JSON z libredwg-web; wspolrzedne lokalne e,n (z przesunieciem dx)."""

    def __init__(self, jpath, dx=0.0, name=""):
        d = json.load(open(jpath, encoding="utf-8"))
        self.name = name
        self.ents = [e for e in d["entities"] if e.get("type") != "VIEWPORT"]
        self.blocks = {b["name"]: b.get("entities", []) for b in d["tables"]["BLOCK_RECORD"]["entries"]}
        self.layers = {l["name"]: l for l in d["tables"]["LAYER"]["entries"]}
        self.header = d.get("header", {})
        self.dx = dx
        self.by_layer = collections.defaultdict(list)
        for e in self.ents:
            self.by_layer[e.get("layer", "")].append(e)

    def xf(self, x, y):
        return (x + self.dx - E0, y - N0)

    # -- geometria pojedynczej encji (lista ksztaltow) ------------------------------------
    def geom(self, e, T=None):
        """Zwraca liste slownikow: {'k':'line'|'point'|'text'|'hatch', 'pts':[[e,n],..], 'closed':bool, 'z':[..]}"""
        T = T or self.xf
        t = e["type"]
        out = []
        if t == "LWPOLYLINE":
            vs = e["vertices"]
            pts = []
            n = len(vs)
            closed = bool(e.get("flag", 0) & 512)
            for i in range(n):
                p1 = vs[i]
                pts.append(T(p1["x"], p1["y"]))
                b = p1.get("bulge", 0) or 0
                if b and (i < n - 1 or closed):
                    p2 = vs[(i + 1) % n]
                    pts.extend(bulge_arc(T(p1["x"], p1["y"]), T(p2["x"], p2["y"]), b)[1:-1])
            if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
                closed = True
                pts = pts[:-1]
            out.append({"k": "line", "pts": pts, "closed": closed})
        elif t in ("POLYLINE3D", "POLYLINE2D", "POLYLINE"):
            vs = e.get("vertices", [])
            pts = [T(v["x"], v["y"]) for v in vs]
            z = [v.get("z", 0.0) for v in vs]
            closed = bool(e.get("flag", 0) & 1)
            out.append({"k": "line", "pts": pts, "closed": closed, "z": z})
        elif t == "LINE":
            a, b = e["startPoint"], e["endPoint"]
            out.append({"k": "line", "pts": [T(a["x"], a["y"]), T(b["x"], b["y"])], "closed": False,
                        "z": [a.get("z", 0.0), b.get("z", 0.0)]})
        elif t == "ARC":
            c, r = e["center"], e["radius"]
            a0, a1 = e["startAngle"], e["endAngle"]
            if a1 < a0:
                a1 += 2 * math.pi
            k = max(4, int((a1 - a0) / (math.pi / 24)))
            pts = [T(c["x"] + r * math.cos(a0 + (a1 - a0) * i / k), c["y"] + r * math.sin(a0 + (a1 - a0) * i / k))
                   for i in range(k + 1)]
            out.append({"k": "line", "pts": pts, "closed": False})
        elif t == "CIRCLE":
            c, r = e["center"], e["radius"]
            pts = [T(c["x"] + r * math.cos(2 * math.pi * i / 48), c["y"] + r * math.sin(2 * math.pi * i / 48))
                   for i in range(48)]
            out.append({"k": "line", "pts": pts, "closed": True})
        elif t == "POINT":
            p = e["position"]
            out.append({"k": "point", "pts": [T(p["x"], p["y"])], "z": [p.get("z", 0.0)]})
        elif t == "INSERT":
            p = e["insertionPoint"]
            out.append({"k": "point", "pts": [T(p["x"], p["y"])], "z": [p.get("z", 0.0)], "block": e.get("name")})
        elif t in ("TEXT", "MTEXT"):
            p = e.get("startPoint") if t == "TEXT" else e.get("insertionPoint")
            rot = e.get("rotation", 0.0) or 0.0
            if t == "MTEXT" and e.get("direction"):
                dd = e["direction"]
                rot = math.atan2(dd.get("y", 0), dd.get("x", 1))
            out.append({"k": "text", "pts": [T(p["x"], p["y"])], "text": clean_text(e.get("text", "")),
                        "h": e.get("textHeight", 1.0), "rot": rot, "halign": e.get("halign", 0),
                        "valign": e.get("valign", 0)})
        elif t == "HATCH":
            for bp in e.get("boundaryPaths", []):
                pts = []
                if "vertices" in bp:
                    pts = [T(v["x"], v["y"]) for v in bp["vertices"]]
                else:
                    for ed in bp.get("edges", []):
                        if ed.get("type") == 1:
                            a = T(ed["start"]["x"], ed["start"]["y"])
                            if not pts or math.dist(pts[-1], a) > 1e-6:
                                pts.append(a)
                            pts.append(T(ed["end"]["x"], ed["end"]["y"]))
                        elif ed.get("type") == 2:
                            c = ed["center"]
                            r = ed["radius"]
                            a0, a1 = ed["startAngle"], ed["endAngle"]
                            ccwf = ed.get("isCCW", 1)
                            if not ccwf:
                                a0, a1 = -a0, -a1
                            if a1 < a0:
                                a1 += 2 * math.pi
                            k = max(4, int((a1 - a0) / (math.pi / 24)))
                            for i in range(k + 1):
                                pts.append(T(c["x"] + r * math.cos(a0 + (a1 - a0) * i / k),
                                             c["y"] + r * math.sin(a0 + (a1 - a0) * i / k)))
                if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
                    pts = pts[:-1]
                if len(pts) >= 3:
                    out.append({"k": "hatch", "pts": pts, "closed": True, "pattern": e.get("patternName")})
        return out

    def insert_T(self, ins):
        p = ins["insertionPoint"]
        sx, sy = ins.get("xScale", 1) or 1, ins.get("yScale", 1) or 1
        rot = ins.get("rotation", 0) or 0
        c, s = math.cos(rot), math.sin(rot)

        def T(x, y):
            X, Y = sx * x, sy * y
            return self.xf(p["x"] + c * X - s * Y, p["y"] + s * X + c * Y)
        return T

    def expand_insert(self, ins):
        T = self.insert_T(ins)
        out = []
        for e in self.blocks.get(ins["name"], []):
            for g in self.geom(e, T):
                g["layer"] = e.get("layer")
                out.append(g)
        return out

    def shapes(self, layer, kinds=("line",), types=None):
        out = []
        for e in self.by_layer.get(layer, []):
            if types and e["type"] not in types:
                continue
            for g in self.geom(e):
                if g["k"] in kinds:
                    g["color"] = e.get("colorIndex")
                    g["ltype"] = e.get("lineType")
                    g["etype"] = e["type"]
                    out.append(g)
        return out


def bulge_arc(p1, p2, b, step=math.pi / 24):
    ang = 4 * math.atan(b)
    ch = math.dist(p1, p2)
    if ch < 1e-9:
        return [p1, p2]
    r = ch / (2 * math.sin(abs(ang) / 2))
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    d = math.sqrt(max(r * r - (ch / 2) ** 2, 0))
    ux, uy = (p2[0] - p1[0]) / ch, (p2[1] - p1[1]) / ch
    sgn = 1 if (b > 0) == (abs(ang) < math.pi) else -1
    cx, cy = mx - sgn * uy * d, my + sgn * ux * d
    a1 = math.atan2(p1[1] - cy, p1[0] - cx)
    k = max(2, int(abs(ang) / step))
    return [(cx + r * math.cos(a1 + ang * i / k), cy + r * math.sin(a1 + ang * i / k)) for i in range(k + 1)]


def text_center(g):
    """Przyblizony srodek tekstu (dla przypisan etykieta -> obiekt)."""
    x, y = g["pts"][0]
    if g.get("halign", 0) == 1 or g.get("valign", 0) == 2:
        return (x, y)
    w = 0.6 * g.get("h", 1.0) * len(g.get("text", ""))
    h = g.get("h", 1.0)
    rot = g.get("rot", 0.0)
    dx, dy = w / 2, h / 2
    return (x + dx * math.cos(rot) - dy * math.sin(rot), y + dx * math.sin(rot) + dy * math.cos(rot))


# ============================================================================================
# ekstrakcja
# ============================================================================================
def determine_m04_shift(em, m4, layer="GESDZI"):
    """Przesuniecie M.04 wzgledem e-mapy: dopasowanie wierzcholkow granic dzialek (ta sama tresc)."""
    a = np.array([p for g in em.shapes(layer) for p in g["pts"]])
    b = np.array([p for g in m4.shapes(layer) for p in g["pts"]])
    d0 = a.mean(0) - b.mean(0)
    t = cKDTree(a)
    dist, idx = t.query(b + d0)
    sh = np.median(a[idx] - b, axis=0)
    dist2, idx2 = t.query(b + sh)
    return sh, float(np.max(dist2)), len(b)


def extract(P, cache):
    J = {k: dwg_to_json(P[k], cache) for k in ("emapa_dwg", "nmt_dwg", "zielen_dwg", "m04_dwg")}
    em = Dwg(J["emapa_dwg"], name="e-mapa")
    nmt = Dwg(J["nmt_dwg"], name="model terenu")
    zl = Dwg(J["zielen_dwg"], name="zielen")
    m4raw = Dwg(J["m04_dwg"], name="M.04")
    sh, resid, nver = determine_m04_shift(em, m4raw)
    m4 = Dwg(J["m04_dwg"], dx=float(sh[0]), name="M.04")
    m4.dx = float(sh[0])   # przesuniecie w osi e (Y); w osi n = sh[1] (0)
    S = {}
    S["_m04_shift"] = {"dE_m": r3(sh[0]), "dN_m": r3(sh[1]), "residual_max_m": r3(resid),
                       "n_vertices": nver, "metoda": "mediana roznic wierzcholkow GESDZI (granice dzialek) M.04 vs e-mapa"}
    S["_sources"] = {k: {"plik": str(P[k].relative_to(P["root"])), "sha256": sha256(P[k])[:16]}
                     for k in P if k.endswith(("_dwg", "_txt", "_pdf"))}

    # ---------------- ramka mapy -----------------------------------------------------------
    frame_m04 = [g for g in m4.shapes("0") if g["closed"] and len(g["pts"]) == 4 and g.get("color") == 18]
    fr = np.array(frame_m04[0]["pts"]) if frame_m04 else None
    frame = box(fr[:, 0].min(), fr[:, 1].min(), fr[:, 0].max(), fr[:, 1].max())
    S["frame"] = frame
    corner_txt = [g["text"] for g in em.shapes("Warstwa 63", kinds=("text",))]
    S["frame_texts"] = corner_txt

    # ---------------- granice konkursowe (M.04) -------------------------------------------
    def big_closed(layer, src=m4, min_area=20.0):
        res = []
        for g in src.shapes(layer, kinds=("line",), types=("LWPOLYLINE",)):
            if g["closed"] or len(g["pts"]) >= 4:
                pol = Polygon(g["pts"])
                if pol.is_valid and pol.area > min_area:
                    res.append(pol)
        return res

    B = {}
    ins = [e for e in m4.by_layer["__Obszar możliwej zabudowy"] if e["type"] == "INSERT"]
    inv = [g for g in m4.expand_insert(ins[0]) if g["k"] == "line"]
    B["obszar_inwestycji"] = Polygon(inv[0]["pts"])
    ins2 = [e for e in m4.by_layer["__Obszar opracowania konkursowego"] if e["type"] == "INSERT"]
    konk_blk = [g for g in m4.expand_insert(ins2[0]) if g["k"] == "line"]
    B["granica_opracowania_konkursowego"] = big_closed("__Obszar opracowania konkursowego")[0]
    B["_konkurs_blok_vs_polilinia_m"] = B["granica_opracowania_konkursowego"].symmetric_difference(
        Polygon(konk_blk[0]["pts"])).area
    B["granica_opracowania_studialnego"] = big_closed("__Obszar opracowania studialnego")[0]
    B["ogrodki_przydomowe"] = unary_union(big_closed("__Obszar istniejących ogródków przydomowych"))
    B["dojazd_10_2"] = big_closed("__Dojazd do wnętrza podwórzowego")[0]
    B["teren_uzyczony_9_2"] = big_closed("__Teren użyczony Województwu Dolnośląskiego")[0]
    # e-mapa: wydzielenie A (szrafura koloru 230 w nakladce MPZP), obiekty dziedzictwa (szrafura 204)
    w61h = em.shapes("Warstwa 61", kinds=("hatch",))
    B["wydzielenie_A_mpzp"] = Polygon([h for h in w61h if h["color"] == 230][0]["pts"])
    B["obiekty_dziedzictwa"] = [Polygon(h["pts"]) for h in w61h if h["color"] == 204]
    w62 = em.shapes("Warstwa 62")
    B["obszar_aktualizacji_mapy"] = Polygon(w62[0]["pts"])
    S["B"] = B

    # ---------------- MPZP: linie ----------------------------------------------------------
    w61 = em.shapes("Warstwa 61", kinds=("line",))
    tri = [g for g in w61 if g["color"] == 230 and len(g["pts"]) == 3]
    lz_seg = [LineString(g["pts"]) for g in w61 if g["color"] == 230 and len(g["pts"]) == 2]
    Apoly = B["wydzielenie_A_mpzp"]
    # odcinki linii zabudowy (bez wewn. krawedzi A); trojkaty -> punkty symboli + kierunek
    lz = linemerge(unary_union(lz_seg))
    lz_lines = [lz] if lz.geom_type == "LineString" else list(lz.geoms)
    lzp = []
    for g in tri:
        c = np.mean(g["pts"], axis=0)
        lzp.append(c)
    # uzupelnienie przerw pod trojkatami: laczymy odcinki lezace w odleglosci < 2.2 m na jednej prostej
    lz_full = bridge_gaps(lz_lines, tol=2.3)
    rozgr = [g for g in w61 if g["color"] == 204]
    gran_plan = [g for g in w61 if g["color"] == 7]
    S["mpzp"] = {"linie_zabudowy": lz_full, "linie_zabudowy_symbole": lzp, "rozgraniczajace": rozgr,
                 "granice_planow": gran_plan,
                 "oznaczenia": [g for g in em.shapes("Warstwa 61", kinds=("text",))]}

    # ---------------- dzialki ---------------------------------------------------------------
    S["parcels"] = parcels(em, frame)
    S["landuse"] = landuse(em, frame)
    S["obreby"] = obreby(em, frame)

    # ---------------- budynki --------------------------------------------------------------
    S["buildings"] = buildings(em, frame)

    # ---------------- ulice, sytuacja --------------------------------------------------------
    S["situation"] = situation(em, nmt)

    # ---------------- drzewa ------------------------------------------------------------------
    S["trees"], S["shrubs"] = trees(P, em, zl)

    # ---------------- teren -----------------------------------------------------------------
    S["terrain"] = terrain(P, em, nmt)

    # ---------------- uzbrojenie --------------------------------------------------------------
    S["utilities"] = utilities(em)

    S["em"], S["nmt"], S["m4"] = em, nmt, m4
    return S


def bridge_gaps(lines, tol=2.3, ang_tol=12.0):
    """Laczy odcinki linii zabudowy przerwane pod symbolami trojkatow (przerwy <= tol, wspolliniowe)."""
    segs = [list(l.coords) for l in lines]
    changed = True
    while changed:
        changed = False
        for i in range(len(segs)):
            for j in range(len(segs)):
                if i == j or not segs[i] or not segs[j]:
                    continue
                a, b = segs[i], segs[j]
                for ea in (0, -1):
                    for eb in (0, -1):
                        pa, pb = a[ea], b[eb]
                        d = math.dist(pa, pb)
                        if 1e-6 < d <= tol:
                            # kierunki koncowek
                            va = np.subtract(a[ea], a[1 if ea == 0 else -2])
                            vg = np.subtract(pb, pa)
                            cosang = np.dot(va, vg) / (np.linalg.norm(va) * np.linalg.norm(vg) + 1e-12)
                            if cosang > math.cos(math.radians(ang_tol)):
                                aa = a if ea == -1 else a[::-1]
                                bb = b if eb == 0 else b[::-1]
                                segs[i] = aa + bb
                                segs[j] = []
                                changed = True
                                break
                        elif d <= 1e-6:
                            aa = a if ea == -1 else a[::-1]
                            bb = b if eb == 0 else b[::-1]
                            segs[i] = aa + bb[1:]
                            segs[j] = []
                            changed = True
                            break
                    if changed:
                        break
                if changed:
                    break
            if changed:
                break
    return [LineString(s) for s in segs if len(s) >= 2]


def label_refpoints(em, layer_o):
    """Etykiety + punkt odniesienia (koniec odnosnika jesli istnieje)."""
    texts = [g for g in em.shapes(layer_o, kinds=("text",))]
    leaders = [g for g in em.shapes(layer_o, kinds=("line",))]
    out = []
    for t in texts:
        p = t["pts"][0]
        ref = text_center(t)
        lead = None
        for L in leaders:
            if math.dist(L["pts"][0], p) < 0.6:
                ref = L["pts"][-1]
                lead = L["pts"]
                break
        out.append({"text": t["text"], "pos": p, "ref": ref, "leader": lead, "rot": t.get("rot", 0)})
    return out


def parcels(em, frame):
    lines = [LineString(g["pts"] + ([g["pts"][0]] if g["closed"] else [])) for g in em.shapes("GESDZI")]
    lines.append(frame.exterior)
    polys = list(polygonize(unary_union(lines)))
    labs = label_refpoints(em, "GESDZI_O")
    res = []
    used = set()
    for pol in polys:
        inside = [l for l in labs if pol.buffer(1e-6).contains(Point(l["ref"]))]
        ident = [l["text"] for l in inside]
        partial = pol.exterior.distance(frame.exterior) < 1e-3 and pol.boundary.intersection(frame.exterior.buffer(1e-3)).length > 0.5
        res.append({"poly": pol, "ids": ident, "partial": bool(partial)})
        used.update(ident)
    unassigned = [l["text"] for l in labs if l["text"] not in used]
    return {"items": res, "labels": labs, "unassigned_labels": unassigned}


def landuse(em, frame):
    lines = [LineString(g["pts"] + ([g["pts"][0]] if g["closed"] else [])) for g in em.shapes("GESUZY")]
    lines += [LineString(g["pts"] + ([g["pts"][0]] if g["closed"] else [])) for g in em.shapes("GESDZI")]
    lines.append(frame.exterior)
    polys = list(polygonize(unary_union(lines)))
    labs = label_refpoints(em, "GESUZY_O")
    res = []
    for pol in polys:
        inside = [l["text"] for l in labs if pol.contains(Point(l["ref"]))]
        res.append({"poly": pol, "ozn": inside})
    return res


def obreby(em, frame):
    lines = [LineString(g["pts"]) for g in em.shapes("GESJOB")] + [frame.exterior]
    polys = list(polygonize(unary_union(lines)))
    labs = [g for g in em.shapes("GESJOB_O", kinds=("text",))]
    out = []
    for pol in polys:
        nm = [l["text"] for l in labs if pol.contains(Point(text_center(l)))]
        out.append({"poly": pol, "name": nm[0] if nm else None})
    return out


def buildings(em, frame):
    shapes = em.shapes("GESBZO")
    closed = [Polygon(g["pts"]) for g in shapes if g["closed"] and len(g["pts"]) >= 3]
    openl = [LineString(g["pts"]) for g in shapes if not g["closed"]]
    # obiekty przy ramce: zamkniecie krawedzia ramki
    partial = []
    if openl:
        cand = list(polygonize(unary_union(openl + [frame.exterior] + [p.exterior for p in closed])))
        for c in cand:
            if c.area > 5 and all(c.intersection(p).area < 0.5 for p in closed) and \
                    c.exterior.distance(frame.exterior) < 1e-3 and c.area < 2000:
                # musi przylegac do linii otwartych
                if any(c.exterior.distance(l) < 1e-3 and c.exterior.intersection(l.buffer(0.01)).length > 2 for l in openl):
                    partial.append(c)
    labels = [g for g in em.shapes("GESBZO_O", kinds=("text",))] + [g for g in em.shapes("GESBLO_O", kinds=("text",))]
    addr_t = [g for g in em.shapes("GEPADR_O", kinds=("text",))]
    addr_p = [g["pts"][0] for g in em.shapes("GEPADR", kinds=("point",))]
    bpb = [Polygon(g["pts"]) if g["closed"] else LineString(g["pts"]) for g in em.shapes("GESBPB")]
    res = []
    for pol, is_partial in [(p, False) for p in closed] + [(p, True) for p in partial]:
        labs = [l["text"] for l in labels if pol.buffer(0.3).contains(Point(text_center(l)))]
        lab = "".join(labs) if is_partial else (labs[0] if labs else "")
        m = re.match(r"^([a-z])(\d*)$", lab)
        func = BUILDING_FUNC.get(m.group(1)) if m else None
        storeys = int(m.group(2)) if (m and m.group(2)) else (1 if m else None)
        # adres: punkt adresowy wewnatrz (bufor 0.6 m) -> najblizszy tekst adresu
        addr = None
        for ap in addr_p:
            if pol.buffer(0.6).contains(Point(ap)):
                tt = min(addr_t, key=lambda t: math.dist(t["pts"][0], ap))
                if math.dist(tt["pts"][0], ap) < 6:
                    addr = tt["text"]
        if addr is None:
            for t in addr_t:
                if pol.contains(Point(t["pts"][0])):
                    addr = t["text"]
        street = ADDRESS_STREET.get(addr, (None, None)) if addr else (None, None)
        res.append({"poly": pol, "label": lab, "func": func, "storeys": storeys, "addr_nr": addr,
                    "street": street[0], "addr_pewnosc": street[1], "partial": is_partial,
                    "przejscia_bramowe": [b for b in bpb if pol.buffer(0.3).contains(b)]})
    return res


def situation(em, nmt):
    out = {}

    def L(layers, src=em, kinds=("line",), min_len=0.0, types=None):
        acc = []
        for lay in layers:
            for g in src.shapes(lay, kinds=kinds, types=types):
                if g["k"] == "line" and LineString(g["pts"] + ([g["pts"][0]] if g.get("closed") else [])).length < min_len:
                    continue
                g["layer"] = lay
                acc.append(g)
        return acc
    out["krawezniki"] = L(["GSLKRW"])
    out["krawezniki_pomiar_NMT"] = L(["kraweznik", "gora_kraweznika"], src=nmt)
    out["jezdnie"] = L(["GSSKOA"])
    out["jezdnie_pomiar_NMT"] = L(["jezdnia"], src=nmt)
    out["chodniki"] = L(["GSSKOD"])
    out["chodniki_pomiar_NMT"] = L(["chodnik", "obszar_utwardzony"], src=nmt)
    out["nawierzchnie_opisy"] = L(["GSSKOA_O", "GSSKOD_O"], kinds=("text",))
    out["tory_tramwajowe"] = L(["GSLTTK"])
    out["trawniki"] = L(["GSSUTR"], types=("LWPOLYLINE",)) + L(["trawnik"], src=nmt)
    out["skarpy"] = L(["GSSZSN", "GSSZSU"])
    out["mury"] = L(["GSSZMO", "GSSDSO", "GSLDSO"])
    out["ogrodzenia"] = L(["GSLKOG", "GSSKOG"]) + L(["ogrodzenie", "furtka"], src=nmt)
    out["schody_terenowe"] = L(["GSSSCK"])
    out["slupki"] = L(["slupki_metalowe", "slupki_drewniane"], src=nmt)
    out["plac_zabaw"] = L(["plac_zabaw"], src=nmt)
    out["szafy"] = L(["szafy_ele_tel_lico"], src=nmt)
    out["woda_linia_brzegu"] = L(["GSSWWP"])
    out["woda_opisy"] = L(["GSSWWP_O"], kinds=("text",))
    out["nazwy_ulic"] = L(["GELULI_O"], kinds=("text",))
    out["inne"] = L(["GSSIIN", "GSSIPD", "GSSROW", "GSSOTW", "GSLTZI", "GSSBKP"]) + L(["GSSBKP"], kinds=("hatch",))
    out["budynki_detale"] = L(["GESBTO", "GESSCH", "GESIPP", "GESBPB"])
    return out


def read_xyz(path, with_h=True):
    rows = []
    for ln in open(path, encoding="utf-8", errors="replace"):
        s = ln.split()
        if len(s) < (4 if with_h else 3):
            continue
        try:
            X, Y = float(s[1]), float(s[2])
            H = float(s[3]) if with_h else None
        except ValueError:
            continue
        rows.append((s[0], Y - E0, X - N0, H))
    return rows


def trees(P, em, zl):
    tx = read_xyz(P["drzewa_txt"], with_h=False)
    items = []
    for nr, e, n, _ in tx:
        items.append({"nr": nr, "e": e, "n": n, "typ": "lisciaste" if nr.startswith("D") else ("iglaste" if nr.startswith("I") else "?"),
                      "zrodlo": "M.02 zielen/mazowiecka_drzewa.txt"})
    # drzewa e-mapy (urzedowe) - polaczenie po polozeniu (<0.30 m)
    em_trees = [(g["pts"][0], "lisciaste") for g in em.shapes("GSPRDL", kinds=("point",))] + \
               [(g["pts"][0], "iglaste") for g in em.shapes("GSPRDI", kinds=("point",))]
    kd = cKDTree(np.array([[t["e"], t["n"]] for t in items]))
    k = 0
    for (p, typ) in em_trees:
        d, i = kd.query(p)
        if d < 0.30:
            items[i]["takze_w_emapie"] = True
            items[i]["dE_emapa_m"] = r3(d)
            continue
        k += 1
        items.append({"nr": "E%02d" % k, "e": p[0], "n": p[1], "typ": typ,
                      "zrodlo": "M.02 e-mapa (warstwa %s) - bez numeru" % ("GSPRDL" if typ == "lisciaste" else "GSPRDI")})
    # kontrola: drzewa w DWG zieleni == txt
    zpts = np.array([g["pts"][0] for lay in ("drzewa_lisciaste", "drzewa_iglaste") for g in zl.shapes(lay, kinds=("point",), types=("POINT",))])
    dz, _ = cKDTree(np.array([[t[1], t[2]] for t in tx])).query(zpts)
    ctrl = {"n_txt": len(tx), "n_dwg_zielen": int(len(zpts)), "max_odchylka_dwg_vs_txt_m": r3(dz.max()),
            "n_numerow_unikalnych": len(set(t[0] for t in tx)),
            "numery_z_dwoma_punktami": sorted([k for k, v in collections.Counter(t[0] for t in tx).items() if v > 1])}
    shrubs = [g for g in zl.shapes("zakrzaczenie")] + [g for g in em.shapes("zakrzaczenie")]
    return {"items": items, "kontrola": ctrl}, shrubs


def terrain(P, em, nmt, step=1.0):
    pk = read_xyz(P["pikiety_txt"])
    pts = np.array([[e, n, h] for _, e, n, h in pk])
    ids = [i for i, *_ in pk]
    # linie nieciaglosci z modelu terenu (3D polilinie z rzedna > 100 m)
    brk = []
    blines = []
    for lay, ents in nmt.by_layer.items():
        for e in ents:
            if e["type"] == "POLYLINE3D":
                g = nmt.geom(e)[0]
                zz = g["z"]
                if min(zz) > 100:
                    blines.append({"layer": lay, "pts": g["pts"], "z": zz, "closed": g["closed"]})
                    for p, z in zip(g["pts"], zz):
                        brk.append([p[0], p[1], z])
    brk = np.array(brk)
    kd = cKDTree(pts[:, :2])
    d, _ = kd.query(brk[:, :2])
    extra = brk[d > 0.05]
    # dedupe extra
    if len(extra):
        _, ui = np.unique(np.round(extra[:, :2], 2), axis=0, return_index=True)
        extra = extra[np.sort(ui)]
    allp = np.vstack([pts, extra])
    tri = Delaunay(allp[:, :2])
    f = LinearNDInterpolator(tri, allp[:, 2])
    e0, e1 = math.floor(allp[:, 0].min()), math.ceil(allp[:, 0].max())
    n0, n1 = math.floor(allp[:, 1].min()), math.ceil(allp[:, 1].max())
    ge = np.arange(e0, e1 + 1e-9, step)
    gn = np.arange(n0, n1 + 1e-9, step)
    GE, GN = np.meshgrid(ge, gn)
    GH = f(GE, GN)
    # usuniecie wezlow w dlugich trojkatach brzegowych (krawedz > 15 m)
    simp = tri.find_simplex(np.c_[GE.ravel(), GN.ravel()])
    longtri = np.zeros(len(tri.simplices), bool)
    for k, s in enumerate(tri.simplices):
        q = allp[s, :2]
        if max(math.dist(q[0], q[1]), math.dist(q[1], q[2]), math.dist(q[0], q[2])) > 15:
            longtri[k] = True
    bad = (simp < 0) | longtri[np.clip(simp, 0, None)]
    GH = GH.ravel()
    GH[bad] = np.nan
    GH = GH.reshape(GE.shape)
    # punkty wysokosciowe e-mapy (do kontroli i poza zasiegiem NMT)
    emh = []
    for lay in ("GSPWPS", "GSPWPN"):
        sym = [g["pts"][0] for g in em.shapes(lay, kinds=("point",))]
        txt = [g for g in em.shapes(lay + "_O", kinds=("text",))]
        if not sym:
            continue
        ks = cKDTree(np.array(sym))
        for t in txt:
            try:
                h = float(t["text"])
            except ValueError:
                continue
            dd, ii = ks.query(t["pts"][0])
            if dd < 2.0:
                emh.append({"e": sym[ii][0], "n": sym[ii][1], "h": h, "layer": lay})
    # rzedne 'txt' (MTEXT pomiaru NMT w e-mapie)
    sym = [g["pts"][0] for g in em.shapes("txt", kinds=("point",))]
    txh = []
    if sym:
        ks = cKDTree(np.array(sym))
        for t in em.shapes("txt", kinds=("text",)):
            try:
                h = float(t["text"])
            except ValueError:
                continue
            dd, ii = ks.query(t["pts"][0])
            if dd < 2.5:
                txh.append({"e": sym[ii][0], "n": sym[ii][1], "h": h})
    # kontrola: punkty DWG modelu terenu vs txt
    dwgp = np.array([[g["pts"][0][0], g["pts"][0][1], g["z"][0]] for g in nmt.shapes("0", kinds=("point",), types=("POINT",))])
    dd, ii = kd.query(dwgp[:, :2])
    ok = dd < 0.02
    ctrl_dwg = {"n_dwg": int(len(dwgp)), "n_zgodnych_xy<2cm": int(ok.sum()),
                "max_dH_zgodnych_m": r3(np.max(np.abs(pts[ii[ok], 2] - dwgp[ok, 2]))) if ok.any() else None,
                "uwaga": "punkty DWG bez odpowiednika w txt: %d (pomijane)" % int((~ok).sum())}
    return {"pikiety": pts, "ids": ids, "extra": extra, "breaklines": blines, "tri": tri, "allp": allp, "f": f,
            "grid": {"e0": float(ge[0]), "n0": float(gn[0]), "step": step, "nx": len(ge), "ny": len(gn), "H": GH},
            "emapa_h": emh, "txt_h": txh, "kontrola_dwg": ctrl_dwg}


UTIL_LABEL_RE = re.compile(r"^(?:(proj)\.)?(\d)?([a-z]+)?([A-Z]*)(\d+)?(?:-(.*))?$")


def parse_util_label(s):
    m = UTIL_LABEL_RE.match(s.strip())
    if not m:
        return {}
    proj, cnt, med, flag, dn, suf = m.groups()
    d = {}
    if proj:
        d["projektowany"] = True
    if cnt:
        d["liczba"] = int(cnt)
    if med:
        d["kod"] = med
    if flag:
        d["atrybut"] = flag
    if dn:
        d["DN_mm"] = int(dn)
    if suf:
        if suf.startswith("niecz"):
            d["nieczynny"] = True
        else:
            d["ref"] = suf
    return d


def utilities(em):
    lines = []
    for lay, typ in UTIL_TYPES.items():
        shp = em.shapes(lay)
        labs = [g for g in em.shapes(lay + "_O", kinds=("text",))]
        ls = [LineString(g["pts"] + ([g["pts"][0]] if g["closed"] else [])) for g in shp]
        lab_of = collections.defaultdict(list)
        for t in labs:
            c = Point(text_center(t))
            if not ls:
                break
            dists = [l.distance(c) for l in ls]
            i = int(np.argmin(dists))
            if dists[i] < 3.0:
                lab_of[i].append(t["text"])
        for i, (g, l) in enumerate(zip(shp, ls)):
            if l.length < 0.05:
                continue
            labels = lab_of.get(i, [])
            parsed = [parse_util_label(x) for x in labels]
            lines.append({"layer": lay, "typ": typ, "pts": g["pts"] + ([g["pts"][0]] if g["closed"] else []),
                          "etykiety": labels, "atrybuty": parsed,
                          "nieczynny": any(p.get("nieczynny") for p in parsed),
                          "projektowany": any(p.get("projektowany") for p in parsed)})
    # punkty uzbrojenia
    pts = []
    for lay in [l for l in LAYER_DICT if l.startswith("GUP")]:
        sym = [g for g in em.shapes(lay, kinds=("point",))]
        for g in sym:
            pts.append({"layer": lay, "opis": LAYER_DICT[lay][1], "e": g["pts"][0][0], "n": g["pts"][0][1]})
    # rzedne uzbrojenia (GUPPRZ): opisy ulamkowe z odnosnikiem -> punkt
    rz = []
    leaders = [g["pts"] for g in em.shapes("GUPPRZ_O", kinds=("line",)) if len(g["pts"]) >= 2]
    texts = [g for g in em.shapes("GUPPRZ_O", kinds=("text",))]
    syms = [g["pts"][0] for g in em.shapes("GUPPRZ", kinds=("point",))]
    ks = cKDTree(np.array(syms)) if syms else None
    used = set()
    for L in leaders:
        x0, y0 = L[0]
        x1 = L[1][0] if len(L) > 1 else x0
        grp = []
        for k, t in enumerate(texts):
            tx, ty = t["pts"][0]
            if k in used:
                continue
            if min(x0, x1) - 0.4 <= tx <= max(x0, x1) + 0.4 and abs(ty - y0) < 1.6:
                grp.append((ty, t["text"], k))
        if not grp:
            continue
        grp.sort(reverse=True)
        for _, _, k in grp:
            used.add(k)
        end = L[-1]
        if ks is not None:
            dd, ii = ks.query(end)
            if dd < 0.5:
                end = syms[ii]
        rz.append({"e": end[0], "n": end[1], "opis": [g[1] for g in grp],
                   "uwaga": "opis ulamkowy: gora/dol (np. rzedna wlazu / dna)" if len(grp) > 1 else ""})
    for k, t in enumerate(texts):
        if k in used or ks is None:
            continue
        dd, ii = ks.query(t["pts"][0])
        if dd < 1.5:
            rz.append({"e": syms[ii][0], "n": syms[ii][1], "opis": [t["text"]], "uwaga": "opis bez odnosnika"})
    return {"lines": lines, "points": pts, "rzedne": rz}


# ============================================================================================
# analizy pochodne
# ============================================================================================
def sample_poly(poly, step=0.5):
    x0, y0, x1, y1 = poly.bounds
    xs = np.arange(math.floor(x0), math.ceil(x1) + 1e-9, step)
    ys = np.arange(math.floor(y0), math.ceil(y1) + 1e-9, step)
    X, Y = np.meshgrid(xs, ys)
    P = np.c_[X.ravel(), Y.ravel()]
    from shapely import contains_xy
    m = contains_xy(poly, P[:, 0], P[:, 1])
    return P[m]


def terrain_stats(T, poly, name):
    P = sample_poly(poly, 0.5)
    H = T["f"](P[:, 0], P[:, 1])
    ok = ~np.isnan(H)
    P, H = P[ok], H[ok]
    if len(H) < 3:
        return {"nazwa": name, "uwaga": "brak pokrycia NMT"}
    A = np.c_[P[:, 0], P[:, 1], np.ones(len(P))]
    coef, *_ = np.linalg.lstsq(A, H, rcond=None)
    gx, gy = coef[0], coef[1]
    g = math.hypot(gx, gy)
    resid = H - A @ coef
    pk = T["pikiety"]
    from shapely import contains_xy
    inside = contains_xy(poly, pk[:, 0], pk[:, 1])
    # spadki lokalne z TIN (trojkaty, ktorych srodek w poligonie)
    allp, tri = T["allp"], T["tri"]
    cen = allp[tri.simplices, :2].mean(axis=1)
    tm = contains_xy(poly, cen[:, 0], cen[:, 1])
    slopes = []
    for s in tri.simplices[tm]:
        q = allp[s]
        v1, v2 = q[1] - q[0], q[2] - q[0]
        nrm = np.cross(v1, v2)
        if abs(nrm[2]) < 1e-9:
            continue
        slopes.append(math.hypot(nrm[0], nrm[1]) / abs(nrm[2]))
    slopes = np.array(slopes) if slopes else np.array([0.0])
    imin, imax = int(np.argmin(H)), int(np.argmax(H))
    return {
        "nazwa": name,
        "pole_m2": r2(poly.area),
        "probkowanie": "siatka 0,5 m, interpolacja liniowa TIN (pikiety + linie nieciaglosci)",
        "n_probek": int(len(H)),
        "H_min": r2(H.min()), "H_min_e_n": pts_r([P[imin]], 1)[0],
        "H_max": r2(H.max()), "H_max_e_n": pts_r([P[imax]], 1)[0],
        "H_srednia": r2(H.mean()), "H_mediana": r2(np.median(H)),
        "deniwelacja_m": r2(H.max() - H.min()),
        "pikiety_w_poligonie": int(inside.sum()),
        "pikiety_H_min": r2(pk[inside, 2].min()) if inside.any() else None,
        "pikiety_H_max": r2(pk[inside, 2].max()) if inside.any() else None,
        "plaszczyzna_regresji": {"spadek_procent": r2(100 * g), "kierunek_spadku_azymut_deg": r1(azimuth(-gx, -gy)),
                                 "odchylenie_std_m": r3(resid.std()), "H_w_centroidzie": r2(coef[0] * poly.centroid.x + coef[1] * poly.centroid.y + coef[2])},
        "spadki_lokalne_TIN_procent": {"mediana": r1(100 * np.median(slopes)), "p90": r1(100 * np.percentile(slopes, 90)),
                                       "max": r1(100 * slopes.max())},
    }


def r1(v):
    return round(float(v), 1)


def edges_info(poly, S, name):
    """Krawedzie poligonu (CCW) z dlugoscia, azymutem i sasiedztwem (dzialka / budynek po stronie zewnetrznej)."""
    p = ccw(poly)
    c = list(p.exterior.coords)
    out = []
    parcels_ = S["parcels"]["items"]
    blds = S["buildings"]
    for i in range(len(c) - 1):
        a, b = c[i], c[i + 1]
        L = math.dist(a, b)
        if L < 0.01:
            continue
        dx, dy = b[0] - a[0], b[1] - a[1]
        # normalna zewnetrzna dla CCW: (dy, -dx)
        nx, ny = dy / L, -dx / L
        m = ((a[0] + b[0]) / 2 + 0.6 * nx, (a[1] + b[1]) / 2 + 0.6 * ny)
        par = [", ".join(q["ids"]) or "?" for q in parcels_ if q["poly"].contains(Point(m))]
        bl = [("%s %s" % (q["street"] or "", q["addr_nr"] or "")).strip() or q["label"] for q in blds
              if q["poly"].buffer(0.35).contains(Point(m))]
        out.append({"i": i, "od": pts_r([a], 2)[0], "do": pts_r([b], 2)[0], "dlugosc_m": r2(L),
                    "azymut_krawedzi_deg": r1(azimuth(dx, dy)), "azymut_normalnej_zewn_deg": r1(azimuth(nx, ny)),
                    "sasiad_dzialka": par[0] if par else None, "sasiad_budynek": bl[0] if bl else None})
    return out


def group_fronts(edges):
    """Grupowanie kolejnych krawedzi o tym samym sasiedztwie."""
    groups = []
    for e in edges:
        key = (e["sasiad_dzialka"], e["sasiad_budynek"])
        if groups and groups[-1]["key"] == key:
            groups[-1]["edges"].append(e)
        else:
            groups.append({"key": key, "edges": [e]})
    if len(groups) > 1 and groups[0]["key"] == groups[-1]["key"]:
        groups[0]["edges"] = groups[-1]["edges"] + groups[0]["edges"]
        groups.pop()
    out = []
    for g in groups:
        L = sum(e["dlugosc_m"] for e in g["edges"])
        out.append({"sasiad_dzialka": g["key"][0], "sasiad_budynek": g["key"][1], "dlugosc_m": r2(L),
                    "od": g["edges"][0]["od"], "do": g["edges"][-1]["do"], "n_krawedzi": len(g["edges"])})
    return out


def shared_walls(bpoly, inv, tol=0.35):
    """Odcinki obrysu budynku lezace na granicy obszaru inwestycji (sciany szczytowe/graniczne)."""
    res = []
    c = list(ccw(bpoly).exterior.coords)
    for i in range(len(c) - 1):
        seg = LineString([c[i], c[i + 1]])
        if seg.length < 0.5:
            continue
        on = seg.intersection(inv.exterior.buffer(tol))
        if on.length > 0.5 * seg.length:
            dx, dy = c[i + 1][0] - c[i][0], c[i + 1][1] - c[i][1]
            L = math.hypot(dx, dy)
            res.append({"od": pts_r([c[i]], 2)[0], "do": pts_r([c[i + 1]], 2)[0], "dlugosc_m": r2(L),
                        "azymut_normalnej_zewn_deg": r1(azimuth(dy / L, -dx / L)),
                        "na_granicy_m": r2(on.length)})
    return res


def ground_level(T, poly, buf=2.0):
    ring = poly.buffer(buf).difference(poly)
    P = sample_poly(ring, 0.5)
    if len(P) == 0:
        return None
    H = T["f"](P[:, 0], P[:, 1])
    H = H[~np.isnan(H)]
    if len(H) == 0:
        return None
    return {"min": r2(H.min()), "srednia": r2(H.mean()), "max": r2(H.max()), "n": int(len(H))}


def check_pdf_georef(P, S):
    """Niezalezna kontrola: wektory PDF M.04 (pymupdf) -> wsp. przez ramke 1:500 -> porownanie z DWG."""
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    doc = pymupdf.open(str(P["m04_pdf"]))
    pg = doc[0]
    dr = pg.get_drawings()
    frame = S["frame"]
    fe0, fn0, fe1, fn1 = frame.bounds
    rects = [d for d in dr if d["rect"].width > 700 and d["rect"].height > 900 and d.get("color") == (0.0, 0.0, 0.0)]
    R = rects[0]["rect"]
    sx = (fe1 - fe0) / R.width
    sy = (fn1 - fn0) / R.height

    def tr(x, y):
        return (fe0 + (x - R.x0) * sx, fn1 - (y - R.y0) * sy)
    res = {"ramka_pdf_pt": [r2(R.x0), r2(R.y0), r2(R.x1), r2(R.y1)],
           "skala_x_m_na_pt": round(sx, 6), "skala_y_m_na_pt": round(sy, 6),
           "skala_teoretyczna_1_500_m_na_pt": round(0.5 * 25.4 / 72, 6)}
    tests = {"obszar_inwestycji": ((1.0, 0.25, 0.0), S["B"]["obszar_inwestycji"]),
             "granica_opracowania_konkursowego": ((0.0, 0.75, 1.0), S["B"]["granica_opracowania_konkursowego"]),
             "teren_uzyczony_9_2": ((0.43, 0.87, 0.0), S["B"]["teren_uzyczony_9_2"])}
    for nm, (col, poly) in tests.items():
        vv = []
        for d in dr:
            c = d.get("color")
            if c is None or max(abs(c[i] - col[i]) for i in range(3)) > 0.02:
                continue
            for it in d["items"]:
                if it[0] == "l":
                    vv += [tr(it[1].x, it[1].y), tr(it[2].x, it[2].y)]
                elif it[0] == "re":
                    r = it[1]
                    vv += [tr(r.x0, r.y0), tr(r.x1, r.y1)]
        # wierzcholki z legendy (poza ramka) pomijamy
        vv = [v for v in vv if frame.contains(Point(v))]
        if not vv:
            continue
        dd = np.array([poly.exterior.distance(Point(v)) for v in vv])
        res[nm] = {"n_wierzcholkow_pdf": len(vv), "odl_do_obrysu_DWG_m": {"mediana": r3(np.median(dd)),
                   "p95": r3(np.percentile(dd, 95)), "max": r3(dd.max())}}
    return res


def control_points(S):
    """Punkty kontrolne georeferencji (niezalezne pary zrodel)."""
    T = S["terrain"]
    out = []
    # (1) drzewa: txt vs DWG zieleni vs e-mapa
    tr = [t for t in S["trees"]["items"] if t.get("takze_w_emapie")]
    for t in tr[:6]:
        out.append({"punkt": "drzewo %s" % t["nr"], "zrodlo_A": "drzewa.txt", "zrodlo_B": "e-mapa DWG (drzewa_* / GSPRD*)",
                    "odchylka_m": t["dE_emapa_m"]})
    # (2) rzedne 'txt' w e-mapie vs pikiety (polozenie + H)
    kd = cKDTree(T["pikiety"][:, :2])
    dd = []
    for p in T["txt_h"]:
        d, i = kd.query([p["e"], p["n"]])
        dd.append((d, abs(T["pikiety"][i, 2] - p["h"])))
    dd = np.array(dd)
    ctrl_txt = {"n": int(len(dd)), "odl_xy_max_m": r3(dd[:, 0].max()) if len(dd) else None,
                "dH_max_m": r3(dd[:, 1].max()) if len(dd) else None}
    # (3) punkty wysokosciowe e-mapy (GSPWPS, niezalezny pomiar urzedowy) vs TIN
    res = []
    for p in T["emapa_h"]:
        h = T["f"](p["e"], p["n"])
        if not np.isnan(h):
            res.append((p["layer"], p["h"] - float(h)))
    r = collections.defaultdict(list)
    for lay, v in res:
        r[lay].append(v)
    ctrl_h = {lay: {"n": len(v), "srednia_m": r3(np.mean(v)), "odch_std_m": r3(np.std(v)), "max_abs_m": r3(np.max(np.abs(v)))}
              for lay, v in r.items()}
    return out, ctrl_txt, ctrl_h


def geodetic_info():
    try:
        from pyproj import CRS, Proj, Transformer
        t = Transformer.from_crs("EPSG:2177", "EPSG:4326", always_xy=False)
        lat, lon = t.transform(N0 + 120, E0 + 85)   # okolice srodka dzialki
        p = Proj("EPSG:2177")
        f = p.get_factors(lon, lat)
        return {"lat": round(lat, 6), "lon": round(lon, 6),
                "zbieznosc_poludnikow_deg": round(f.meridian_convergence, 4),
                "skala_odwzorowania": round(f.meridional_scale, 7),
                "uwaga": ("polnoc siatki (os n) jest obrocona wzgledem polnocy geograficznej o zbieznosc poludnikow; "
                          "azymut geograficzny = azymut siatki + zbieznosc (konwencja pyproj: kat od polnocy geogr. do polnocy siatki)")}
    except Exception as ex:  # noqa
        return {"blad": str(ex)}


# ============================================================================================
# zapis site.json
# ============================================================================================
def build_json(P, S, extras):
    B = S["B"]
    T = S["terrain"]
    inv = B["obszar_inwestycji"]

    def poly_entry(pol, **kw):
        d = {"pts": poly_out(pol), "pole_m2": r2(pol.area), "obwod_m": r2(pol.length)}
        d.update(kw)
        return d

    J = collections.OrderedDict()
    J["meta"] = {
        "opis": "Geometria terenu i otoczenia - konkurs UMWD Wroclaw (dz. 10/3, 11/6, 19/11, 9/1, obreb 0022 Poludnie)",
        "wygenerowano": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "narzedzie": "tools/site_extract.py",
        "zrodla": S["_sources"],
        "mapa": {"nr": "ZGKIKM.TM.6640.4638.2025", "data": "01.10.2025", "skala": "1:500",
                 "protokol_weryfikacji": "ZGKIKM.TM.6640.4638.2025_1_pl z dnia 08.10.2025",
                 "uwagi_z_mapy": ["Uklad wspolrzednych '2000/6'", "Uklad wysokosciowy 'PL-EVRF2007-NH'",
                                  "Obszar aktualizacji oznaczono linia szrafurowana (Warstwa 62)",
                                  "Linie MPZP wrysowano na podstawie podkladu rastrowego z SIP m. Wroclawia (dokladnosc ograniczona)",
                                  "Nie wyklucza sie istnienia w terenie innych, niewykazanych na mapie urzadzen podziemnych"]},
        "konwencje": "wspolrzedne [e, n] w m w ukladzie lokalnym; poligony CCW bez powtorzenia 1. punktu; wysokosci H w m PL-EVRF2007-NH",
    }
    J["crs"] = {
        "uklad_poziomy": "PL-2000 strefa 6 (ETRF2000-PL / CS2000/18, EPSG:2177); X = polnoc, Y = wschod",
        "uklad_wysokosciowy": "PL-EVRF2007-NH (EPSG:9651) - wg opisu mapy M.02 i M.04",
        "lokalny": {"e": "Y - 6433500.00", "n": "X - 5664100.00", "Y0": E0, "X0": N0,
                    "odwrotnie": "Y = e + 6433500.00 ; X = n + 5664100.00", "jednostki": "m"},
        "geodezja": extras["geod"],
        "przesuniecie_M04_DWG": S["_m04_shift"],
        "ramka_mapy": {"pts": poly_out(S["frame"]), "SW_Y_X": [r2(S["frame"].bounds[0] + E0), r2(S["frame"].bounds[1] + N0)],
                       "NE_Y_X": [r2(S["frame"].bounds[2] + E0), r2(S["frame"].bounds[3] + N0)],
                       "opisy_narozy_e-mapa": S["frame_texts"]},
    }
    J["kontrola_georeferencji"] = extras["georef"]

    J["granice"] = {
        "obszar_inwestycji": poly_entry(inv, zrodlo="M.04 DWG, blok '2505_MDCP_Granica możliwej zabudowy' (warstwa '__Obszar możliwej zabudowy'; legenda PDF: 'Obszar inwestycji')",
                                        dzialki="10/3, 11/6, 19/11, 9/1", pole_wg_M01_m2=3729),
        "granica_opracowania_konkursowego": poly_entry(B["granica_opracowania_konkursowego"], zrodlo="M.04 DWG warstwa '__Obszar opracowania konkursowego'",
                                                       roznica_blok_vs_polilinia_m2=r3(B["_konkurs_blok_vs_polilinia_m"])),
        "granica_opracowania_studialnego": poly_entry(B["granica_opracowania_studialnego"], zrodlo="M.04 DWG warstwa '__Obszar opracowania studialnego'",
                                                      uwaga="poligon przyciety do ramki mapy M.04 (zasieg rysunku)"),
        "wydzielenie_A_mpzp": poly_entry(B["wydzielenie_A_mpzp"], zrodlo="e-mapa / M.04 DWG 'Warstwa 61' (szrafura kolor 230); legenda M.04: 'Wydzielenie wewn. A zgodnie z MPZP'; legenda e-mapy opisuje te szrafure jako 'strefa oddzialywania linii zabudowy' (rozbieznosc nazewnicza)",
                                         pole_w_obszarze_inwestycji_m2=r2(B["wydzielenie_A_mpzp"].intersection(inv).area),
                                         dokladnosc="ok. +/-0,3 m (digitalizacja rastra planu 1:1000)"),
        "ogrodki_przydomowe": poly_entry(B["ogrodki_przydomowe"], zrodlo="M.04 DWG '__Obszar istniejących ogródków przydomowych'"),
        "dojazd_dz_10_2": poly_entry(B["dojazd_10_2"], zrodlo="M.04 DWG '__Dojazd do wnętrza podwórzowego'"),
        "teren_uzyczony_dz_9_2": poly_entry(B["teren_uzyczony_9_2"], zrodlo="M.04 DWG '__Teren użyczony Województwu Dolnośląskiego'"),
        "obiekty_dziedzictwa_kulturowego": [poly_entry(p, zrodlo="e-mapa 'Warstwa 61' szrafura kolor 204 (legenda: obiekt dziedzictwa kulturowego)") for p in B["obiekty_dziedzictwa"]],
        "obszar_aktualizacji_mapy": poly_entry(B["obszar_aktualizacji_mapy"], zrodlo="e-mapa 'Warstwa 62'"),
    }
    J["granice"]["obszar_inwestycji"]["krawedzie"] = extras["inv_edges"]
    J["granice"]["obszar_inwestycji"]["fronty"] = extras["inv_fronts"]

    M = S["mpzp"]
    J["mpzp"] = {
        "zrodlo": "e-mapa/M.04 'Warstwa 61' - nakladka planu nr 372 (uchwala XLV/1366/10) wrysowana z rastra SIP; dokladnosc ok. +/-0,3-0,5 m",
        "nieprzekraczalne_linie_zabudowy": [{"pts": pts_r(l.coords), "dlugosc_m": r2(l.length)} for l in M["linie_zabudowy"]],
        "symbole_linii_zabudowy_srodki": pts_r(M["linie_zabudowy_symbole"], 2),
        "linie_rozgraniczajace": [{"pts": pts_r(g["pts"]), "zamknieta": g["closed"]} for g in M["rozgraniczajace"]
                                  if g["etype"] != "HATCH"],
        "granica_planow_372_602": [{"pts": pts_r(g["pts"])} for g in M["granice_planow"]],
        "oznaczenia_terenow": [{"tekst": g["text"], "e": r2(g["pts"][0][0]), "n": r2(g["pts"][0][1])} for g in M["oznaczenia"]
                               if g["text"] != "SL"],
        "uwaga": "teksty 'SL' w warstwie 61 = linie slupkow (legenda e-mapy: 'SL - slupki metalowe i drewniane') - pominiete tutaj, patrz sytuacja.slupki",
    }

    # dzialki
    par = []
    obr = S["obreby"]
    for q in S["parcels"]["items"]:
        pol = q["poly"]
        ob = [o["name"] for o in obr if o["poly"].contains(pol.representative_point())]
        lu = [u for u in S["landuse"] if u["poly"].intersection(pol).area > 0.5 * u["poly"].area]
        luo = sorted(set(sum([u["ozn"] for u in lu], [])))
        par.append({"nr": q["ids"][0] if len(q["ids"]) == 1 else (q["ids"] or None),
                    "etykiety_w_poligonie": q["ids"], "obreb": ob[0] if ob else None, "uzytki": luo,
                    "czesciowa_przycieta_ramka": q["partial"], "pts": poly_out(pol), "pole_geom_m2": r2(pol.area),
                    "w_obszarze_inwestycji_m2": r2(pol.intersection(inv).area)})
    J["dzialki"] = {"uwaga": "pole_geom = pole z geometrii mapy (nie pole ewidencyjne EGiB); dzialki przy ramce przyciete (czesciowa_przycieta_ramka)",
                    "items": par, "etykiety_nieprzypisane": S["parcels"]["unassigned_labels"],
                    "punkty_graniczne": [pts_r(g["pts"], 2)[0] for g in S["em"].shapes("GEPPGD", kinds=("point",))]}

    # budynki
    bl = []
    for q in S["buildings"]:
        pol = q["poly"]
        gl = ground_level(T, pol)
        name = ("%s %s" % (q["street"], q["addr_nr"])) if q["street"] else None
        st = q["storeys"]
        h_est = round(BASE_RAISE + st * STOREY_H + ROOF_ADD, 1) if st else None
        d = {"nazwa": name, "adres_nr": q["addr_nr"], "ulica": q["street"], "adres_pewnosc": q["addr_pewnosc"],
             "etykieta": q["label"], "funkcja": q["func"], "kondygnacje_nadziemne": st,
             "czesciowy_przyciety_ramka": q["partial"], "pts": poly_out(pol), "pole_zabudowy_geom_m2": r2(pol.area),
             "teren_wokol_H": gl,
             "wysokosc_szac_m": h_est,
             "wysokosc_metoda": ("szacunek: %.2f m (parter nad terenem) + n x %.2f m + %.2f m (attyka/gzyms) - DO WERYFIKACJI (zdjecia M.09/M.10, wizja)"
                                 % (BASE_RAISE, STOREY_H, ROOF_ADD)) if st else None,
             "przejscia_bramowe_lub_nawisy": [pts_r(b.exterior.coords if b.geom_type == "Polygon" else b.coords, 2) for b in q["przejscia_bramowe"]],
             "sciany_na_granicy_obszaru_inwestycji": shared_walls(pol, inv)}
        if name and name in BUILDING_NOTES:
            d["inwentaryzacja"] = BUILDING_NOTES[name]
        if name == "Mazowiecka 19" and gl:
            # poziom 0.00 = ul. Mazowiecka + 0.73 (M.07); chodnik przed frontem z NMT
            fr = extras.get("maz19_front_H")
            if fr:
                z0 = fr + 0.73
                d["poziom_0_00_szac_H"] = r2(z0)
                d["attyka_szac_H"] = r2(z0 + BUILDING_NOTES[name]["attyka_wzgl_0.00_m_odczyt_graficzny"])
                d["wysokosc_szac_m"] = r1(BUILDING_NOTES[name]["attyka_wzgl_0.00_m_odczyt_graficzny"] + 0.73)
                d["wysokosc_metoda"] = ("M.07 przekroj A-A: attyka ok. +21,0 m wzgl. 0,00 (odczyt graficzny +/-0,3 m); 0,00 = chodnik ul. Mazowieckiej + 0,73 m; "
                                        "chodnik przed frontem H=%.2f (NMT) -> wysokosc od chodnika ok. 21,7 m (opis M.07: 'ok. 20 m')" % fr)
        if d["wysokosc_szac_m"] and gl:
            d.setdefault("gora_szac_H", r2(gl["srednia"] + d["wysokosc_szac_m"]))
        bl.append(d)
    J["budynki"] = {"uwaga": "obrysy EGiB (e-mapa GESBZO); etykieta = kod funkcji + liczba kondygnacji nadziemnych; wysokosci szacunkowe",
                    "items": bl}

    # sytuacja
    Sx = S["situation"]

    def lines_out(lst):
        res = []
        for g in lst:
            if g["k"] == "text":
                res.append({"tekst": g["text"], "e": r2(g["pts"][0][0]), "n": r2(g["pts"][0][1]),
                            "rot_deg": r1(math.degrees(g.get("rot", 0))), "warstwa": g.get("layer")})
            else:
                d = {"pts": pts_r(g["pts"], 3), "zamknieta": bool(g.get("closed")), "warstwa": g.get("layer")}
                if g.get("z") is not None and max(g["z"]) > 50:
                    d["z"] = [r3(z) for z in g["z"]]
                res.append(d)
        return res
    J["ulice_i_sytuacja"] = {k: lines_out(v) for k, v in Sx.items() if k not in ("woda_linia_brzegu", "woda_opisy")}
    J["ulice_i_sytuacja"]["_opis"] = ("krawezniki/jezdnie/chodniki: warstwy e-mapy (urzedowe) oraz *_pomiar_NMT (3D polilinie z rzednymi z "
                                      "pomiaru uzupelniajacego, zasieg ok. e 4-135, n -8-114); MPZP linie rozgraniczajace - sekcja mpzp")
    J["most_grunwaldzki"] = extras["bridge"]
    J["woda"] = {"linia_brzegu": lines_out(Sx["woda_linia_brzegu"]), "opisy": lines_out(Sx["woda_opisy"]),
                 "uwaga": "linia brzegu wg e-mapy (GSSWWP); woda po stronie wschodniej/pln.-wsch. linii; Olawa uchodzi do Odry na wsch. od kwartalu"}

    # zielen
    J["zielen"] = {"drzewa": [{"nr": t["nr"], "e": r2(t["e"]), "n": r2(t["n"]), "typ": t["typ"], "zrodlo": t["zrodlo"],
                               "w_obszarze_inwestycji": bool(inv.contains(Point(t["e"], t["n"]))),
                               "w_ogrodkach": bool(B["ogrodki_przydomowe"].contains(Point(t["e"], t["n"]))),
                               "H_teren": (r2(float(T["f"](t["e"], t["n"]))) if not np.isnan(T["f"](t["e"], t["n"])) else None)}
                              for t in S["trees"]["items"]],
                   "kontrola": S["trees"]["kontrola"],
                   "uwaga": ("D = lisciaste, I = iglaste (warstwy DWG drzewa_lisciaste/drzewa_iglaste); E.. = drzewa z e-mapy bez numeru. "
                             "Gatunki, obwody, korony: do polaczenia z operatem dendrologicznym M.06 (inna numeracja - parowanie po polozeniu)."),
                   "zakrzaczenia": [{"pts": pts_r(g["pts"], 2)} for g in S["shrubs"]]}

    # teren
    G = T["grid"]
    Hg = [[(None if np.isnan(v) else round(float(v), 2)) for v in row] for row in G["H"]]
    J["teren"] = {
        "uklad_H": "PL-EVRF2007-NH",
        "pikiety": [[T["ids"][i], r3(p[0]), r3(p[1]), r2(p[2])] for i, p in enumerate(T["pikiety"])],
        "pikiety_opis": "[nr, e, n, H] - M.02 'model terenu/mazowiecka_pikiety do nmt.txt' (800 pkt, pomiar wykonawcy mapy)",
        "punkty_dodatkowe_z_linii_nieciaglosci": [[r3(p[0]), r3(p[1]), r2(p[2])] for p in T["extra"]],
        "linie_nieciaglosci": [{"warstwa": b["layer"], "pts": pts_r(b["pts"]), "z": [r2(z) for z in b["z"]]} for b in T["breaklines"]],
        "punkty_wysokosciowe_emapy": [{"e": r2(p["e"]), "n": r2(p["n"]), "H": p["h"], "warstwa": p["layer"]} for p in T["emapa_h"]],
        "siatka_NMT": {"e0": G["e0"], "n0": G["n0"], "krok_m": G["step"], "nx": G["nx"], "ny": G["ny"],
                       "metoda": "TIN (Delaunay) z pikiet + wierzcholkow 3D polilinii modelu terenu; interpolacja liniowa; null poza zasiegiem (trojkaty o krawedzi >15 m odrzucone)",
                       "H_wiersze_od_n0": Hg},
        "statystyki": extras["tstats"],
        "kontrola": {"dwg_vs_txt": T["kontrola_dwg"], "rzedne_txt_emapy_vs_pikiety": extras["ctrl_txt"],
                     "punkty_emapy_vs_TIN": extras["ctrl_h"]},
    }

    # uzbrojenie
    U = S["utilities"]
    ul = []
    for u in U["lines"]:
        ls = LineString(u["pts"])
        inside = ls.intersection(inv)
        inA = ls.intersection(B["wydzielenie_A_mpzp"])
        ul.append({"typ": u["typ"], "warstwa": u["layer"], "etykiety": u["etykiety"], "atrybuty": u["atrybuty"],
                   "nieczynny": u["nieczynny"], "projektowany": u["projektowany"], "pts": pts_r(u["pts"], 3),
                   "dlugosc_m": r2(ls.length),
                   "dl_w_obszarze_inwestycji_m": r2(inside.length), "dl_w_wydzieleniu_A_m": r2(inA.length),
                   "kolizja_z_obszarem_inwestycji": bool(inside.length > 0.05)})
    J["uzbrojenie"] = {"uwaga": ("przewody wg e-mapy (GESUT); etykieta: [proj.][liczba]kod[atrybut][DN][-ref|-niecz.]; kody: w-woda, "
                                 "k-kanal. (ks sanit., kd deszcz., ko ogolnospl.), g-gaz, e-elektro (eN nn, eS SN), t-telekom, c-cieplo; "
                                 "litery A/B po kodzie - atrybut wg instrukcji ZGKiKM (znaczenie nieustalone, do weryfikacji); "
                                 "kolizja = przebieg w granicach obszaru inwestycji (wymaga przebudowy/usuniecia - do uzgodnienia z gestorami)"),
                       "przewody": ul,
                       "punkty": [{"warstwa": p["layer"], "opis": p["opis"], "e": r2(p["e"]), "n": r2(p["n"])} for p in U["points"]],
                       "rzedne": [{"e": r2(p["e"]), "n": r2(p["n"]), "opis": p["opis"], "uwaga": p["uwaga"]} for p in U["rzedne"]],
                       "zestawienie_kolizji": extras["util_summary"]}

    # surowe warstwy (do rysunku 1:500)
    raw = {}
    for lay, ents in S["em"].by_layer.items():
        if lay in ("Warstwa 63",):
            continue
        lst = []
        for e in ents:
            if lay == "GSSUTR" and e["type"] != "LWPOLYLINE":
                continue
            for g in S["em"].geom(e):
                if g["k"] in ("line", "hatch"):
                    lst.append({"pts": pts_r(g["pts"], 3), "z": 1 if g.get("closed") else 0})
                elif g["k"] == "text":
                    lst.append({"t": g["text"], "p": pts_r(g["pts"], 2)[0], "r": r1(math.degrees(g.get("rot", 0))), "h": r2(g.get("h", 1))})
                elif g["k"] == "point":
                    lst.append({"p": pts_r(g["pts"], 3)[0], "b": g.get("block")})
        if lst:
            raw[lay] = {"opis": LAYER_DICT.get(lay, ("?", "?", "?")), "obiekty": lst}
    J["warstwy_emapy_surowe"] = {"uwaga": "pelna tresc e-mapy M.02 (bez tekstow wektorowych 'Warstwa 63' i symboli trawnika); "
                                          "obiekt: pts+z(1=zamkniety) | t,p,r,h (tekst) | p,b (symbol/blok)",
                                 "warstwy": raw}
    return J


# ============================================================================================
# most (przyczolek / os - przyblizenie)
# ============================================================================================
def bridge_info(S):
    Sx = S["situation"]
    tt = [LineString(g["pts"]) for g in Sx["tory_tramwajowe"]]
    region = box(85, 118, 160, 160)
    segs = []
    for l in tt:
        c = l.intersection(region)
        if c.is_empty:
            continue
        for part in (c.geoms if hasattr(c, "geoms") else [c]):
            cc = np.array(part.coords)
            segs.append(cc)
    if not segs:
        return {"uwaga": "brak torow w rejonie mostu"}
    allc = np.vstack(segs)
    # kierunek glowny (PCA)
    m = allc.mean(0)
    u, s, vt = np.linalg.svd(allc - m)
    d = vt[0]
    if d[1] < 0:
        d = -d
    az = azimuth(d[0], d[1])
    axis = LineString([m - 60 * d, m + 60 * d])
    shore = [LineString(g["pts"]) for g in Sx["woda_linia_brzegu"]]
    ip = None
    for sl in shore:
        x = axis.intersection(sl)
        if not x.is_empty:
            ip = x if x.geom_type == "Point" else list(x.geoms)[0]
            break
    walls = [g for g in Sx["mury"] if g["layer"] == "GSSZMO"]
    return {
        "nazwa": "Most Grunwaldzki (przyczolek poludniowy - poza/na krawedzi ramki mapy, pln.-wsch. naroznik)",
        "os_przyblizona": {"punkt": pts_r([m], 2)[0], "azymut_siatki_deg": r1(az), "pts": pts_r(axis.coords, 2),
                           "metoda": "glowny kierunek (PCA) osi torow tramwajowych GSLTTK w rejonie e>85, n>118 - przyblizenie osi mostu"},
        "przeciecie_osi_z_linia_brzegu": pts_r([ip.coords[0]], 2)[0] if ip else None,
        "mury_przyczolka_GSSZMO": [pts_r(g["pts"], 2) for g in walls],
        "opis_e-mapy": [{"tekst": g["text"], "e": r2(g["pts"][0][0]), "n": r2(g["pts"][0][1])} for g in Sx["nazwy_ulic"] if "most" in g["text"]],
        "dokladnosc": "orientacyjna (most w wiekszosci poza zasiegiem mapy; geometria pylonow/helmow - patrz docs/30_lokalizacja/img/most_grunwaldzki_*.jpg)",
    }


# ============================================================================================
# PNG kontrolny
# ============================================================================================
def make_png(S, J, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MPoly
    from matplotlib.lines import Line2D
    B = S["B"]
    T = S["terrain"]
    fig, ax = plt.subplots(figsize=(16.5, 21.0), dpi=110)
    fr = S["frame"]

    def pl(pts, closed=False, **kw):
        a = np.array(pts)
        if closed:
            a = np.vstack([a, a[:1]])
        ax.plot(a[:, 0], a[:, 1], **kw)

    # NMT - warstwice
    G = T["grid"]
    ge = G["e0"] + np.arange(G["nx"]) * G["step"]
    gn = G["n0"] + np.arange(G["ny"]) * G["step"]
    H = np.ma.masked_invalid(G["H"])
    lv = np.arange(117.75, 122.01, 0.25)
    cf = ax.contourf(ge, gn, H, levels=lv, cmap="terrain", alpha=0.35, zorder=0)
    cs = ax.contour(ge, gn, H, levels=lv, colors="#6b5b3e", linewidths=0.35, zorder=1)
    ax.clabel(cs, levels=lv[::2], fontsize=5, fmt="%.2f")
    # dzialki
    for q in S["parcels"]["items"]:
        pl(list(q["poly"].exterior.coords), color="#9a9a9a", lw=0.6, zorder=2)
    for l in S["parcels"]["labels"]:
        ax.text(l["ref"][0], l["ref"][1], l["text"], fontsize=6.5, color="#555", ha="center", va="center", zorder=8, style="italic")
    # sytuacja
    Sx = S["situation"]
    for g in Sx["jezdnie"]:
        pl(g["pts"], g.get("closed"), color="#7a8ca8", lw=0.5, zorder=3)
    for g in Sx["chodniki"]:
        pl(g["pts"], g.get("closed"), color="#c9a36b", lw=0.45, zorder=3)
    for g in Sx["krawezniki"] + Sx["krawezniki_pomiar_NMT"]:
        pl(g["pts"], g.get("closed"), color="#33415c", lw=0.8, zorder=3)
    for g in Sx["tory_tramwajowe"]:
        pl(g["pts"], color="#8c2d04", lw=0.9, ls=(0, (6, 2)), zorder=3)
    for g in Sx["skarpy"]:
        pl(g["pts"], g.get("closed"), color="#8c6d31", lw=0.4, zorder=3)
    for g in Sx["mury"] + Sx["schody_terenowe"]:
        pl(g["pts"], g.get("closed"), color="#444", lw=0.6, zorder=3)
    for g in Sx["ogrodzenia"]:
        pl(g["pts"], g.get("closed"), color="#6d4c41", lw=0.5, ls=":", zorder=3)
    for g in Sx["woda_linia_brzegu"]:
        pl(g["pts"], color="#1f78b4", lw=1.6, zorder=3)
    for g in Sx["woda_opisy"] + Sx["nazwy_ulic"]:
        ax.text(g["pts"][0][0], g["pts"][0][1], g["text"], fontsize=8, color="#1f4e79", rotation=math.degrees(g.get("rot", 0)), zorder=9)
    # budynki
    for q, jb in zip(S["buildings"], J["budynki"]["items"]):
        pol = q["poly"]
        ax.add_patch(MPoly(np.array(pol.exterior.coords), closed=True, fc="#bdbdbd", ec="#212121", lw=0.9, zorder=4))
        c = pol.representative_point()
        txt = q["label"]
        if jb["nazwa"]:
            txt = "%s\n%s" % (jb["nazwa"].replace("Wybrzeze J. Slowackiego", "Wyb. Slowackiego"), q["label"])
        ax.text(c.x, c.y, txt, fontsize=6.5, ha="center", va="center", zorder=9, color="#111")
    for p in B["obiekty_dziedzictwa"]:
        ax.add_patch(MPoly(np.array(p.exterior.coords), closed=True, fc="none", ec="#7b2cbf", hatch="xx", lw=0.6, zorder=5))
    # uzbrojenie (kolizje grubiej)
    ucol = {"wodociag": "#1565c0", "kanalizacja": "#6d4c41", "gaz": "#f9a825", "elektroenergetyka": "#d32f2f",
            "telekomunikacja": "#2e7d32", "cieplownictwo": "#e65100", "obudowa/oslona": "#9e9e9e"}
    for u in J["uzbrojenie"]["przewody"]:
        pl(u["pts"], color=ucol.get(u["typ"], "k"), lw=1.3 if u["kolizja_z_obszarem_inwestycji"] else 0.45,
           alpha=0.9 if u["kolizja_z_obszarem_inwestycji"] else 0.5, ls="--" if u["nieczynny"] else "-", zorder=5)
    # granice konkursowe
    pl(list(B["granica_opracowania_studialnego"].exterior.coords), color="#e040fb", lw=2.0, ls=(0, (7, 3)), zorder=6)
    ax.add_patch(MPoly(np.array(B["granica_opracowania_konkursowego"].exterior.coords), closed=True, fc="#29b6f6", alpha=0.10, ec="#0288d1", lw=2.2, zorder=6))
    ax.add_patch(MPoly(np.array(B["obszar_inwestycji"].exterior.coords), closed=True, fc="none", ec="#ff4500", lw=2.6, zorder=7))
    ax.add_patch(MPoly(np.array(B["wydzielenie_A_mpzp"].exterior.coords), closed=True, fc="none", ec="#d81b60", hatch="////", lw=1.2, zorder=7))
    ax.add_patch(MPoly(np.array(B["ogrodki_przydomowe"].exterior.coords), closed=True, fc="none", ec="#1a237e", hatch="\\\\", lw=0.9, ls="--", zorder=6))
    ax.add_patch(MPoly(np.array(B["dojazd_10_2"].exterior.coords), closed=True, fc="none", ec="#f06292", hatch="..", lw=1.0, zorder=6))
    ax.add_patch(MPoly(np.array(B["teren_uzyczony_9_2"].exterior.coords), closed=True, fc="#9ccc65", alpha=0.25, ec="#558b2f", lw=1.2, zorder=6))
    for l in S["mpzp"]["linie_zabudowy"]:
        a = np.array(l.coords)
        ax.plot(a[:, 0], a[:, 1], color="#c2185b", lw=1.6, zorder=7)
    for c in S["mpzp"]["linie_zabudowy_symbole"]:
        ax.plot(c[0], c[1], marker="v", color="#c2185b", ms=4, mfc="none", zorder=7)
    for g in S["mpzp"]["rozgraniczajace"]:
        if g["etype"] == "HATCH":
            continue
        pl(g["pts"], g["closed"], color="#ad1457", lw=0.8, ls=(0, (8, 2, 1, 2)), zorder=6)
    for g in S["mpzp"]["oznaczenia"]:
        if g["text"] != "SL":
            ax.text(g["pts"][0][0], g["pts"][0][1], g["text"], fontsize=9, color="#ad1457", weight="bold", zorder=9)
    # drzewa
    for t in J["zielen"]["drzewa"]:
        col = "#2e7d32" if t["typ"] == "lisciaste" else "#004d40"
        ax.plot(t["e"], t["n"], marker="o" if t["typ"] == "lisciaste" else "^", ms=4.5, mfc="none", mec=col, mew=1.0, zorder=8)
    # pikiety
    pk = T["pikiety"]
    ax.plot(pk[:, 0], pk[:, 1], ".", ms=1.2, color="#000", alpha=0.5, zorder=8)
    # sciany szczytowe
    for jb in J["budynki"]["items"]:
        for w in jb["sciany_na_granicy_obszaru_inwestycji"]:
            ax.plot([w["od"][0], w["do"][0]], [w["od"][1], w["do"][1]], color="#ffd600", lw=4.0, alpha=0.8, zorder=7.5, solid_capstyle="butt")
    # most
    br = J["most_grunwaldzki"]
    if "os_przyblizona" in br:
        a = np.array(br["os_przyblizona"]["pts"])
        ax.plot(a[:, 0], a[:, 1], color="#5d4037", lw=1.0, ls="-.", zorder=7)
    # ramka, siatka
    pl(list(fr.exterior.coords), color="k", lw=1.0, zorder=9)
    x0, y0, x1, y1 = fr.bounds
    ax.set_xlim(x0 - 2, x1 + 2)
    ax.set_ylim(y0 - 2, y1 + 2)
    ax.set_xticks(np.arange(10, 160, 10))
    ax.set_yticks(np.arange(-30, 150, 10))
    ax.grid(True, color="#000", lw=0.25, alpha=0.35)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=8)
    ax.set_xlabel("e [m] = Y - 6 433 500,00 (PL-2000/6)")
    ax.set_ylabel("n [m] = X - 5 664 100,00 (PL-2000/6)")
    ax.set_title("UMWD Wroclaw - geometria terenu (M.02 e-mapa + M.04) - kontrola warstw, siatka 10 m, warstwice NMT co 0,25 m (PL-EVRF2007-NH)",
                 fontsize=11)
    leg = [Line2D([], [], color="#ff4500", lw=2.6, label="obszar inwestycji (M.04)"),
           Line2D([], [], color="#0288d1", lw=2.2, label="granica opracowania konkursowego"),
           Line2D([], [], color="#e040fb", lw=2.0, ls="--", label="granica opracowania studialnego"),
           Line2D([], [], color="#d81b60", lw=1.2, label="wydzielenie A (MPZP, h 35-45 m)"),
           Line2D([], [], color="#c2185b", lw=1.6, marker="v", mfc="none", label="nieprzekraczalna linia zabudowy"),
           Line2D([], [], color="#ad1457", lw=0.8, ls=(0, (8, 2, 1, 2)), label="linie rozgraniczajace MPZP"),
           Line2D([], [], color="#1a237e", lw=0.9, ls="--", label="ogrodki przydomowe"),
           Line2D([], [], color="#f06292", lw=1.0, label="dojazd dz. 10/2"),
           Line2D([], [], color="#558b2f", lw=1.2, label="teren uzyczony dz. 9/2 (skwer)"),
           Line2D([], [], color="#ffd600", lw=4, label="sciany budynkow na granicy obszaru inw."),
           Line2D([], [], color="#7b2cbf", lw=0.6, label="obiekt dziedzictwa (szrafura)"),
           Line2D([], [], color="#1f78b4", lw=1.6, label="linia brzegu (Odra/Olawa)"),
           Line2D([], [], color="#8c2d04", lw=0.9, ls="--", label="tory tramwajowe"),
           Line2D([], [], color="#5d4037", lw=1.0, ls="-.", label="os Mostu Grunwaldzkiego (przybl.)"),
           Line2D([], [], color="#2e7d32", marker="o", ls="", mfc="none", label="drzewa lisciaste / ^ iglaste"),
           Line2D([], [], color="#d32f2f", lw=1.3, label="przewody kolidujace (grubo; -- nieczynne)")]
    ax.legend(handles=leg, loc="lower left", fontsize=7.5, framealpha=0.9)
    # strzalka polnocy + podzialka
    ax.annotate("N (siatka)", xy=(146, 140), xytext=(146, 128), arrowprops=dict(arrowstyle="-|>", lw=1.5), ha="center", fontsize=8, zorder=10)
    ax.plot([115, 135], [-31, -31], color="k", lw=3, zorder=10)
    ax.plot([115, 125], [-31, -31], color="w", lw=1.5, zorder=10)
    ax.text(125, -29.6, "0     10     20 m", ha="center", fontsize=7, zorder=10)
    fig.colorbar(cf, ax=ax, fraction=0.025, pad=0.01, label="H [m] PL-EVRF2007-NH")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=110)
    plt.close(fig)


# ============================================================================================
# geometria.md
# ============================================================================================
def make_md(P, S, J, out_md):
    G = J["granice"]
    inv = G["obszar_inwestycji"]
    T = J["teren"]
    st = {s["nazwa"]: s for s in T["statystyki"]}
    L = []
    w = L.append
    today = datetime.date.today().isoformat()
    w("# Geometria terenu i otoczenia – dane do modelu 3D i rysunków 1:500 / 1:200")
    w("")
    w("**Stan:** %s · **Generator:** `tools/site_extract.py` (deterministyczny; plik generowany – nie edytować ręcznie) · "
      "**Wynik:** `model/site.json`, `docs/30_lokalizacja/img/site_kontrola.png`  " % today)
    w("**Zasada wyłączenia:** opracowanie oparte wyłącznie na załącznikach Organizatora (M.02, M.04, M.07, M.08) – "
      "nie korzystano z żadnych informacji o pracach konkursowych.")
    w("")
    w("![Kontrola warstw](img/site_kontrola.png)")
    w("")
    w("## 1. Źródła")
    w("")
    w("| Skrót | Plik (względem `umwd/`) | Zawartość / uwagi |")
    w("|---|---|---|")
    desc = {"emapa_dwg": "mapa do celów projektowych 1:500 (AutoCAD 2000, 9 753 encje, ~150 warstw: EGiB, BDOT500, GESUT, nakładka MPZP); nr ZGKIKM.TM.6640.4638.2025 z 01.10.2025, protokół weryfikacji z 08.10.2025",
            "nmt_dwg": "model terenu: 765 punktów + 3D polilinie (krawężniki, chodniki, jezdnie, ogrodzenia, słupki) z rzędnymi",
            "zielen_dwg": "drzewa (41 liściastych, 15 iglastych) + zakrzaczenia (3D polilinie)",
            "m04_dwg": "mapa schematyczna: granice opracowania studialnego/konkursowego, obszar inwestycji, ogródki, dojazd 10/2, teren użyczony 9/2 (DWG przesunięty względem PL-2000 – patrz 2.2)",
            "pikiety_txt": "800 pikiet: nr X Y H (X=północ, Y=wschód) – podstawa NMT",
            "drzewa_txt": "56 punktów drzew: nr (D=liściaste, I=iglaste) X Y",
            "m04_pdf": "mapa schematyczna PDF (wektorowa) – niezależna kontrola georeferencji",
            "m02_pdf": "e-mapa PDF A3 – odczyt opisów (układy, legenda, oświadczenie)"}
    for k, v in J["meta"]["zrodla"].items():
        w("| %s | `%s` (sha256 %s…) | %s |" % (k, v["plik"], v["sha256"], desc.get(k, "")))
    w("| M.07 | `00_materialy/_rozpak/…/M.07. INWENTARYZACJA MAZOWIECKA 19.pdf` s. 9–10 | Mazowiecka 19: opis „Budynek w liczbach”, przekrój A-A (rzędne) – odczyt wizualny |")
    w("| M.08 | `00_materialy/tekst/M.08._INWENTARYZACJA_WYBRZEŻE_SŁOWACKIEGO_5.txt` | Wybrzeże Słowackiego 5: informacja o oknie w ścianie szczytowej |")
    w("")
    w("Opisy z mapy M.02 (PDF, tabliczka i legenda; odczyt wizualny renderu 250 dpi): *„1. Układ współrzędnych: 2000/6”, „2. Układ wysokościowy: PL-EVRF2007-NH”, "
      "„3. Obszar aktualizacji oznaczono linią szrafurowaną”*, legenda: *„Linie MPZP wrysowano na podstawie podkładu rastrowego wyeksportowanego ze strony www – SIP m. Wrocławia – Plany miejscowe”*, "
      "*„Nie wyklucza się istnienia w terenie innych, niewykazanych na mapie urządzeń podziemnych…”*. M.04 PDF: „układ 2000/6”, „PL-EVRF2007-NH” (zgodnie z `docs/30_lokalizacja/mpzp.md`).")
    w("")
    w("## 2. Metoda i dokładność")
    w("")
    w("### 2.1 Odczyt formatów")
    w("- **DWG → JSON**: libredwg skompilowane do WebAssembly (`%s`, Node.js; instalacja do katalogu cache z `--ignore-scripts`). Pakiet systemowy `libredwg-tools` nie jest dostępny w repozytoriach Ubuntu 24.04 (sprawdzono `apt-get`)." % LIBREDWG_PKG)
    w("- **DGN** (`mazowiecka_e-mapa.dgn`) to MicroStation **V8** (kontener OLE) – GDAL/OGR czyta tylko DGN v7; treść DGN jest duplikatem DWG, więc pominięto (bez straty informacji – wniosek).")
    w("- **PDF** (M.04) – wektory odczytane PyMuPDF wyłącznie do kontroli georeferencji (2.3).")
    w("")
    w("### 2.2 Georeferencja")
    sh = J["crs"]["przesuniecie_M04_DWG"]
    w("- DWG e-mapy, modelu terenu i zieleni są zapisane **bezpośrednio w PL-2000/6** (x DWG = Y, y DWG = X); odczyt pliku txt pikiet i drzew (X, Y) daje identyczne położenia (tab. 2.3).")
    w("- **DWG M.04 jest przesunięty** w osi Y o **ΔY = %+.3f m** (ΔX = %.3f m) względem PL-2000/6 – ustalone z %d wierzchołków granic działek (warstwa GESDZI, ta sama treść co e-mapa), "
      "odchyłka maks. po przesunięciu **%.3f m**. Narzędzie przelicza M.04 automatycznie. Kontrola: ramka M.04 po przesunięciu = narożniki opisane na mapie "
      "(SW Y 6433510,66 / X 5664064,48; NE Y 6433651,96 / X 5664248,09)." % (sh["dE_m"], sh["dN_m"], sh["n_vertices"], sh["residual_max_m"]))
    w("- Układ lokalny: **e = Y − 6 433 500,00; n = X − 5 664 100,00** [m]; ramka mapy: e %.2f…%.2f, n %.2f…%.2f." %
      tuple([J["crs"]["ramka_mapy"]["SW_Y_X"][0] - E0, J["crs"]["ramka_mapy"]["NE_Y_X"][0] - E0, J["crs"]["ramka_mapy"]["SW_Y_X"][1] - N0, J["crs"]["ramka_mapy"]["NE_Y_X"][1] - N0]))
    gd = J["crs"]["geodezja"]
    if "lat" in gd:
        w("- Położenie (środek działki, WGS84): φ = %.5f°, λ = %.5f°; **zbieżność południków γ = %+.3f°** (pyproj, EPSG:2177) – oś *n* jest obrócona względem północy geograficznej; "
          "do analiz nasłonecznienia azymut geograficzny Słońca należy przeliczyć na azymut siatki (wniosek: różnica ok. 0,75° – istotna tylko dla precyzyjnych analiz cienia). Skala odwzorowania m = %.6f (zniekształcenie długości ok. %.0f mm/100 m – pomijalne)." %
          (gd["lat"], gd["lon"], gd["zbieznosc_poludnikow_deg"], gd["skala_odwzorowania"], abs(gd["skala_odwzorowania"] - 1) * 1e5))
    w("")
    w("### 2.3 Punkty kontrolne i błędy")
    w("")
    w("| Test | Liczba | Wynik |")
    w("|---|---|---|")
    kg = J["kontrola_georeferencji"]
    tk = J["zielen"]["kontrola"]
    w("| Drzewa: `drzewa.txt` vs DWG zieleni (POINT) | %d / %d | odchyłka maks. %.3f m |" % (tk["n_txt"], tk["n_dwg_zielen"], tk["max_odchylka_dwg_vs_txt_m"]))
    cps = kg["punkty_kontrolne"]
    if cps:
        w("| Drzewa: `drzewa.txt` vs symbole drzew e-mapy (GSPRD*), przykłady: %s | %d | odchyłki %s m |" %
          (", ".join(c["punkt"].replace("drzewo ", "") for c in cps), len(cps), ", ".join("%.2f" % c["odchylka_m"] for c in cps)))
    kd = T["kontrola"]["dwg_vs_txt"]
    w("| Pikiety: DWG modelu terenu vs `pikiety do nmt.txt` | %d | %d zgodnych w XY < 2 cm, maks. ΔH %.3f m; %s |" % (kd["n_dwg"], kd["n_zgodnych_xy<2cm"], kd["max_dH_zgodnych_m"] or 0, kd["uwaga"]))
    ct = T["kontrola"]["rzedne_txt_emapy_vs_pikiety"]
    w("| Rzędne pomiaru w e-mapie (warstwa `txt`) vs pikiety | %d | odl. XY maks. %.3f m, ΔH maks. %.3f m |" % (ct["n"], ct["odl_xy_max_m"] or 0, ct["dH_max_m"] or 0))
    for lay, v in T["kontrola"]["punkty_emapy_vs_TIN"].items():
        w("| Urzędowe punkty wysokościowe e-mapy %s vs TIN z pikiet (niezależny pomiar) | %d | śr. %+.3f m, σ %.3f m, maks. |Δ| %.3f m |" % (lay, v["n"], v["srednia_m"], v["odch_std_m"], v["max_abs_m"]))
    pdf = kg["pdf_M04"]
    for nm in ("obszar_inwestycji", "granica_opracowania_konkursowego", "teren_uzyczony_9_2"):
        if nm in pdf:
            v = pdf[nm]
            w("| PDF M.04 (wektory, przeliczone przez ramkę 1:500) vs DWG: %s | %d wierzch. | odl. do obrysu DWG: mediana %.3f m, p95 %.3f m, maks. %.3f m |" %
              (nm, v["n_wierzcholkow_pdf"], v["odl_do_obrysu_DWG_m"]["mediana"], v["odl_do_obrysu_DWG_m"]["p95"], v["odl_do_obrysu_DWG_m"]["max"]))
    w("| Skala PDF M.04 (ramka) | – | %.6f / %.6f m/pt vs teoret. 1:500 = %.6f m/pt |" % (pdf["skala_x_m_na_pt"], pdf["skala_y_m_na_pt"], pdf["skala_teoretyczna_1_500_m_na_pt"]))
    w("| Blok vs polilinia granicy konkursowej w DWG M.04 | – | różnica symetryczna %.3f m² |" % G["granica_opracowania_konkursowego"]["roznica_blok_vs_polilinia_m2"])
    w("")
    w("**Ocena dokładności (wniosek):** treść EGiB/BDOT500/GESUT i pomiar uzupełniający – dokładność mapy zasadniczej 1:500 (rzędu ±0,1 m dla szczegółów I grupy); "
      "granice konkursowe M.04 – identyczne z DWG po przesunięciu (błąd < 1 cm); **linie MPZP (linie zabudowy, wydzielenie A, linie rozgraniczające) – wrysowane z rastra SIP 1:1000 – "
      "dokładność ok. ±0,3–0,5 m**; uzbrojenie – wg GESUT, bez gwarancji kompletności (zastrzeżenie na mapie). NMT – interpolacja liniowa TIN; w obrębie obszaru inwestycji gęstość ok. 1 pikieta / 10 m².")
    w("")
    w("## 3. Warstwy i ich interpretacja")
    w("")
    w("Kody warstw e-mapy (ZGKiKM Wrocław): `G` + grupa (`ES/EP/EL` – EGiB, `SS/SL/SP` – BDOT500 obiekty powierzchniowe/liniowe/punktowe, `UL/UP/US` – GESUT linie/punkty/obiekty) + kod obiektu; sufiks `_O` – opisy. "
      "Kolumna „pewność”: *pewna* – potwierdzona opisem/legendą/etykietami; *wniosek* – interpretacja własna.")
    w("")
    w("| Warstwa | Grupa | Treść | Pewność | Liczba obiektów |")
    w("|---|---|---|---|---|")
    raw = J["warstwy_emapy_surowe"]["warstwy"]
    for lay in sorted(raw):
        d = LAYER_DICT.get(lay)
        if not d:
            continue
        w("| `%s` | %s | %s | %s | %d |" % (lay, d[0], d[1], d[2], len(raw[lay]["obiekty"])))
    w("")
    w("M.04 (DWG, po przesunięciu): `__Obszar możliwej zabudowy` (blok `2505_MDCP_Granica możliwej zabudowy`) = **„Obszar inwestycji”** wg legendy PDF (rozbieżność nazwy warstwy i legendy – bez wpływu na geometrię); "
      "`__Obszar opracowania konkursowego`, `__Obszar opracowania studialnego`, `__Obszar istniejących ogródków przydomowych`, `__Dojazd do wnętrza podwórzowego`, `__Teren użyczony Województwu Dolnośląskiego`. "
      "„Wydzielenie wewn. A”, „Nieprzekraczalna linia zabudowy” i „Obiekt dziedzictwa kulturowego” z legendy M.04 pochodzą z warstwy `Warstwa 61` (nakładka MPZP wspólna z e-mapą). "
      "Bloki `2505_FS_linie zabudowy nr 2` i `2505_MPZP_funkcje nr 2` w DWG M.04 są zdefiniowane w innym układzie/skali i **nie są wstawione** w przestrzeń modelu – pominięto.")
    w("")
    w("## 4. Granice i powierzchnie")
    w("")
    w("| Poligon | Pole [m²] | Obwód [m] | Uwagi |")
    w("|---|---|---|---|")
    A = G["wydzielenie_A_mpzp"]
    w("| Obszar inwestycji (dz. 10/3, 11/6, 19/11, 9/1) | **%.1f** | %.1f | M.01: 3 729 m² (różnica %.1f m² = %.2f%%) |" % (inv["pole_m2"], inv["obwod_m"], inv["pole_m2"] - 3729, 100 * (inv["pole_m2"] - 3729) / 3729))
    w("| Granica opracowania konkursowego | %.1f | %.1f | obejmuje obszar inwestycji + dz. 9/2 + 10/2 + pas wzdłuż Wybrzeża |" % (G["granica_opracowania_konkursowego"]["pole_m2"], G["granica_opracowania_konkursowego"]["obwod_m"]))
    w("| Granica opracowania studialnego (w ramce M.04) | %.1f | %.1f | przycięta ramką mapy |" % (G["granica_opracowania_studialnego"]["pole_m2"], G["granica_opracowania_studialnego"]["obwod_m"]))
    w("| Wydzielenie A (MPZP) | %.1f | %.1f | w obszarze inwestycji: **%.1f m²** (%.0f%% obszaru) |" % (A["pole_m2"], A["obwod_m"], A["pole_w_obszarze_inwestycji_m2"], 100 * A["pole_w_obszarze_inwestycji_m2"] / inv["pole_m2"]))
    w("| Ogródki przydomowe | %.1f | %.1f | w całości w obszarze inwestycji: %s |" % (G["ogrodki_przydomowe"]["pole_m2"], G["ogrodki_przydomowe"]["obwod_m"],
      "tak" if S["B"]["ogrodki_przydomowe"].difference(S["B"]["obszar_inwestycji"]).area < 1 else "nie (%.1f m² poza)" % S["B"]["ogrodki_przydomowe"].difference(S["B"]["obszar_inwestycji"]).area))
    w("| Dojazd – dz. 10/2 | %.1f | %.1f | |" % (G["dojazd_dz_10_2"]["pole_m2"], G["dojazd_dz_10_2"]["obwod_m"]))
    w("| Teren użyczony – dz. 9/2 (skwer) | %.1f | %.1f | |" % (G["teren_uzyczony_dz_9_2"]["pole_m2"], G["teren_uzyczony_dz_9_2"]["obwod_m"]))
    for i, o in enumerate(G["obiekty_dziedzictwa_kulturowego"]):
        w("| Obiekt dziedzictwa kulturowego %d | %.1f | %.1f | obrys = budynek %s |" % (i + 1, o["pole_m2"], o["obwod_m"], ["Mazowiecka 19", "Mazowiecka 17"][i] if i < 2 else "?"))
    w("")
    w("Narożniki wydzielenia A (e, n): %s; Y/X: %s." % ("; ".join("(%.2f, %.2f)" % tuple(p) for p in A["pts"]),
                                                         "; ".join("%.2f / %.2f" % (p[0] + E0, p[1] + N0) for p in A["pts"])))
    w("Boki A: %s m." % ", ".join("%.2f" % math.dist(A["pts"][i], A["pts"][(i + 1) % len(A["pts"])]) for i in range(len(A["pts"]))))
    w("")
    w("### 4.1 Działki (pola geometryczne z mapy; nie są polami ewidencyjnymi)")
    w("")
    w("| Działka | Obręb | Użytki | Pole geom. [m²] | W obszarze inwestycji [m²] | Uwagi |")
    w("|---|---|---|---|---|---|")
    keyp = ["10/3", "11/6", "19/11", "9/1", "9/2", "10/2", "8/6", "8/8", "8/7", "11/3", "12", "10/1", "11/4", "11/5", "13", "20"]
    items = J["dzialki"]["items"]

    def pid(it):
        return it["nr"] if isinstance(it["nr"], str) else ("+".join(it["etykiety_w_poligonie"]) if it["etykiety_w_poligonie"] else "?")
    srt = sorted(items, key=lambda it: (keyp.index(pid(it)) if pid(it) in keyp else 99, -it["pole_geom_m2"]))
    for it in srt:
        if it["pole_geom_m2"] < 1:
            continue
        w("| %s | %s | %s | %.1f | %.1f | %s |" % (pid(it), it["obreb"] or "", ", ".join(it["uzytki"]), it["pole_geom_m2"], it["w_obszarze_inwestycji_m2"],
                                                  "przycięta ramką" if it["czesciowa_przycieta_ramka"] else ""))
    w("")
    sum_inv = sum(it["pole_geom_m2"] for it in items if pid(it) in ("10/3", "11/6", "19/11", "9/1"))
    w("Suma pól geometrycznych dz. 10/3 + 11/6 + 19/11 + 9/1 = **%.1f m²** (obszar inwestycji M.04: %.1f m²; M.01: 3 729 m²). "
      "Etykiety nieprzypisane do zamkniętych poligonów (działki przecięte ramką bez pełnego obrysu lub numery z odnośnikami poza ramką): %s." %
      (sum_inv, inv["pole_m2"], ", ".join(J["dzialki"]["etykiety_nieprzypisane"]) or "brak"))
    w("")
    w("### 4.2 Krawędzie obszaru inwestycji i fronty")
    w("")
    w("Kolejność CCW od wierzchołka 0; azymuty od północy siatki. Sąsiedztwo – działka/budynek 0,6 m na zewnątrz od środka krawędzi.")
    w("")
    w("| # | od (e, n) | do (e, n) | długość [m] | azymut krawędzi [°] | normalna zewn. [°] | sąsiad: działka | sąsiad: budynek |")
    w("|---|---|---|---|---|---|---|---|")
    for e in inv["krawedzie"]:
        w("| %d | %.2f, %.2f | %.2f, %.2f | %.2f | %.1f | %.1f | %s | %s |" % (e["i"], e["od"][0], e["od"][1], e["do"][0], e["do"][1], e["dlugosc_m"],
                                                                             e["azymut_krawedzi_deg"], e["azymut_normalnej_zewn_deg"], e["sasiad_dzialka"] or "–", e["sasiad_budynek"] or "–"))
    w("")
    w("**Fronty (grupy krawędzi o tym samym sąsiedztwie):**")
    w("")
    w("| Sąsiad (działka) | Sąsiad (budynek) | Długość [m] | od → do | Interpretacja (wniosek) |")
    w("|---|---|---|---|---|")
    interp = {"8/8": "front ul. Mazowieckiej (dz. drogowa 8/8)", "8/6": "front ul. Mazowieckiej (dz. drogowa 8/6)",
              "9/2": "granica ze skwerem dz. 9/2 → front Wybrzeża Słowackiego / przyczółek mostu",
              "10/2": "granica z dojazdem dz. 10/2", "11/3": "granica z dz. Mazowiecka 19", "12": "granica z dz. Wybrzeże Słowackiego 5",
              "20": "front Wybrzeża J. Słowackiego (wsch.)", "10/1": "granica z dz. 10/1 (pas wzdłuż Wybrzeża)",
              "11/4": "granica z dz. 11/4 (podwórze)", "11/5": "granica z dz. 11/5 (podwórze)", "13": "granica z dz. 13 (Wybrzeże Słowackiego 6)",
              "11/1": "granica z dz. 11/1 (podwórze)", "16/3": "granica z dz. 16/3"}
    for f in inv["fronty"]:
        w("| %s | %s | %.2f | (%.1f, %.1f) → (%.1f, %.1f) | %s |" % (f["sasiad_dzialka"] or "–", f["sasiad_budynek"] or "–", f["dlugosc_m"], f["od"][0], f["od"][1], f["do"][0], f["do"][1],
                                                                  interp.get(f["sasiad_dzialka"], "")))
    w("")
    w("### 4.3 Ściany budynków sąsiednich na granicy obszaru inwestycji")
    w("")
    w("| Budynek | Kondygn. | Ściana od → do (e, n) | Długość [m] | Normalna zewn. [°] | Uwagi |")
    w("|---|---|---|---|---|---|")
    for b in J["budynki"]["items"]:
        for s in b["sciany_na_granicy_obszaru_inwestycji"]:
            nt = ""
            if b["nazwa"] in BUILDING_NOTES:
                nt = BUILDING_NOTES[b["nazwa"]]["sciana_szczytowa"]
            w("| %s | %s | (%.2f, %.2f) → (%.2f, %.2f) | %.2f | %.1f | %s |" % (b["nazwa"] or b["etykieta"], b["kondygnacje_nadziemne"], s["od"][0], s["od"][1], s["do"][0], s["do"][1], s["dlugosc_m"], s["azymut_normalnej_zewn_deg"], nt))
    w("")
    w("## 5. Budynki istniejące (zasięg mapy)")
    w("")
    w("| Budynek | Etykieta | Funkcja (kod EGiB) | Kondygn. | Pole zab. [m²] | Teren wokół H śr. | Wysokość [m] | Góra ≈ H | Metoda / uwagi |")
    w("|---|---|---|---|---|---|---|---|---|")
    for b in sorted(J["budynki"]["items"], key=lambda b: (b["nazwa"] is None, b["nazwa"] or "", -b["pole_zabudowy_geom_m2"])):
        w("| %s | %s | %s | %s | %.1f | %s | %s | %s | %s |" % (
            (b["nazwa"] or "– (brak adresu)") + (" *(przycięty ramką)*" if b["czesciowy_przyciety_ramka"] else ""),
            b["etykieta"], b["funkcja"] or "", b["kondygnacje_nadziemne"] or "", b["pole_zabudowy_geom_m2"],
            ("%.2f" % b["teren_wokol_H"]["srednia"]) if b["teren_wokol_H"] else "poza NMT",
            ("%.1f" % b["wysokosc_szac_m"]) if b["wysokosc_szac_m"] else "",
            ("%.1f" % b["gora_szac_H"]) if b.get("gora_szac_H") else "",
            "inwentaryzacja M.07" if b["nazwa"] == "Mazowiecka 19" else "szacunek – do weryfikacji"))
    w("")
    m19 = [b for b in J["budynki"]["items"] if b["nazwa"] == "Mazowiecka 19"]
    if m19:
        b = m19[0]
        w("**Mazowiecka 19** (M.07, s. 9–10): kamienica z 1880 r. na dz. 11/3; 6 kondygnacji nadziemnych (w tym poddasze użytkowe), 1 podziemna; pow. zabudowy wg inwentaryzacji **259,00 m²** "
          "(z mapy: %.1f m² – zgodność %.1f%%); wysokość „ok. 20 m” (opis). Przekrój A-A: ±0,00 = parter (wejście od Mazowieckiej), ul. Mazowiecka −0,73, podwórze −1,15, spoczniki −0,85 / +1,78 / +5,51 / +9,28 / +13,05 / +16,79, poddasze +18,30; "
          "dach płaski kryty papą (spadek ok. 5%%), murek attykowy, attyka ok. **+21,0 m** wzgl. ±0,00 (odczyt graficzny z rysunku, ±0,3 m – wniosek). "
          "Przyjęto: chodnik przed frontem H = %s → ±0,00 ≈ %s m n.p.m., attyka ≈ **%s m n.p.m.** (do weryfikacji pomiarem). Okna w północnej ścianie szczytowej – do zamurowania w ramach inwestycji towarzyszącej (M.07)." %
          (b["pole_zabudowy_geom_m2"], 100 * b["pole_zabudowy_geom_m2"] / 259.0, J["_extras_md"].get("maz19_front_H"), b.get("poziom_0_00_szac_H"), b.get("attyka_szac_H")))
        w("")
    w("**Wybrzeże J. Słowackiego 5** (M.08): okno w ścianie szczytowej lokalu na kondygnacji 2 (1. piętro) **nie jest przeznaczone do zamurowania – należy uwzględnić jego istnienie w projekcie** (przesłanianie/nasłonecznienie, odległości wg WT). "
      "Wysokość budynku nie wynika z dostarczonych materiałów (rzuty – skany) – w `site.json` szacunek z liczby kondygnacji (5 → ok. %.1f m), do weryfikacji na zdjęciach M.09/M.10." % (BASE_RAISE + 5 * STOREY_H + ROOF_ADD))
    w("")
    w("## 6. Teren (NMT) – rzędne i spadki")
    w("")
    w("NMT: %d pikiet + %d punktów z wierzchołków linii nieciągłości (3D polilinie modelu terenu) → TIN → siatka %.1f m (%d × %d węzłów, `teren.siatka_NMT`). Zakres pikiet H %.2f…%.2f m." %
      (len(T["pikiety"]), len(T["punkty_dodatkowe_z_linii_nieciaglosci"]), T["siatka_NMT"]["krok_m"], T["siatka_NMT"]["nx"], T["siatka_NMT"]["ny"],
       min(p[3] for p in T["pikiety"]), max(p[3] for p in T["pikiety"])))
    w("")
    w("| Obszar | Pole [m²] | Pikiet | H min | H max | H śr. | H med. | Deniwelacja | Spadek płaszczyzny regresji | Kierunek spadku [°] | Spadki lokalne TIN: med./p90/max [%] |")
    w("|---|---|---|---|---|---|---|---|---|---|---|")
    for s in T["statystyki"]:
        if "H_min" not in s:
            continue
        pr = s["plaszczyzna_regresji"]
        sl = s["spadki_lokalne_TIN_procent"]
        w("| %s | %.1f | %d | %.2f | %.2f | %.2f | %.2f | %.2f | %.2f%% | %.0f | %.1f / %.1f / %.1f |" % (s["nazwa"], s["pole_m2"], s["pikiety_w_poligonie"], s["H_min"], s["H_max"], s["H_srednia"], s["H_mediana"],
                                                                                                   s["deniwelacja_m"], pr["spadek_procent"], pr["kierunek_spadku_azymut_deg"], sl["mediana"], sl["p90"], sl["max"]))
    w("")
    so = st.get("obszar inwestycji")
    if so:
        w("Obszar inwestycji: H min %.2f m w punkcie (e, n) = (%.1f, %.1f), H max %.2f m w (%.1f, %.1f). Lokalne maksima spadków TIN wynikają z krawężników, obrzeży i nasypów ogródków (skoki rzędu 0,1–0,3 m na krótkich odcinkach) – nie są spadkiem terenu (wniosek)." %
          (so["H_min"], so["H_min_e_n"][0], so["H_min_e_n"][1], so["H_max"], so["H_max_e_n"][0], so["H_max_e_n"][1]))
    w("")
    w("**Rzędne w narożnikach obszaru inwestycji** (TIN):")
    w("")
    w("| Wierzchołek | e | n | H |")
    w("|---|---|---|---|")
    for i, (p, h) in enumerate(J["_extras_md"]["corner_H"]):
        w("| %d | %.2f | %.2f | %s |" % (i, p[0], p[1], ("%.2f" % h) if h is not None else "poza NMT"))
    w("")
    w("Wniosek do projektu: teren praktycznie płaski (deniwelacja w obszarze inwestycji ok. %.1f m); poziom ±0,00 parteru można przyjąć ok. %.2f–%.2f m n.p.m. (chodnik + 0,15…0,30 m) – do decyzji projektowej i weryfikacji z wymaganiami dostępności (wejścia bez schodów)." %
      (so["deniwelacja_m"] if so else float("nan"), (so["H_mediana"] + 0.15) if so else 0, (so["H_mediana"] + 0.30) if so else 0))
    w("")
    w("## 7. Zieleń")
    w("")
    tk = J["zielen"]["kontrola"]
    dr = J["zielen"]["drzewa"]
    w("Drzewa z pomiaru (`drzewa.txt`): %d punktów, %d unikalnych numerów (numery z dwoma punktami – drzewa wielopniowe lub podwójny pomiar: %s); dodatkowo %d drzew z e-mapy bez numeru (poza zasięgiem pomiaru szczegółowego). "
      "W obszarze inwestycji: **%d** drzew, w tym w ogródkach przydomowych: **%d**. Gatunki, obwody, stan i korony – w operacie dendrologicznym M.06 (inna numeracja: do sparowania po położeniu – etap późniejszy)." %
      (tk["n_txt"], tk["n_numerow_unikalnych"], ", ".join(tk["numery_z_dwoma_punktami"]), sum(1 for t in dr if t["nr"].startswith("E")),
       sum(1 for t in dr if t["w_obszarze_inwestycji"]), sum(1 for t in dr if t["w_ogrodkach"])))
    w("")
    w("## 8. Uzbrojenie terenu – kolizje z obszarem inwestycji")
    w("")
    w("| Sieć | Etykiety | Długość w obszarze inwestycji [m] | w tym w wydzieleniu A [m] | Status |")
    w("|---|---|---|---|---|")
    for u in sorted(J["uzbrojenie"]["przewody"], key=lambda u: (u["typ"], -u["dl_w_obszarze_inwestycji_m"])):
        if not u["kolizja_z_obszarem_inwestycji"]:
            continue
        w("| %s (`%s`) | %s | %.1f | %.1f | %s |" % (u["typ"], u["warstwa"], ", ".join(u["etykiety"]) or "–", u["dl_w_obszarze_inwestycji_m"], u["dl_w_wydzieleniu_A_m"],
                                                    "nieczynny" if u["nieczynny"] else ("projektowany" if u["projektowany"] else "czynny/brak opisu")))
    w("")
    us = J["uzbrojenie"]["zestawienie_kolizji"]
    w("Podsumowanie (długość w obszarze inwestycji wg typu): %s." % ", ".join("%s %.1f m" % (k, v) for k, v in us.items()))
    w("")
    w("Uwaga: etykiety przypisano do najbliższej linii w promieniu 3 m (możliwe pojedyncze błędne przypisania przy liniach równoległych – wniosek). Przebiegi kolidujące wymagają warunków przebudowy od gestorów; "
      "dla parkingu podziemnego istotne są wszystkie przewody w obrysie (także nieczynne – do usunięcia).")
    w("")
    w("## 9. Most Grunwaldzki i nabrzeże")
    br = J["most_grunwaldzki"]
    if "os_przyblizona" in br:
        w("")
        w("Oś mostu (przybliżenie – kierunek osi torów tramwajowych w pn.-wsch. narożniku mapy): azymut siatki **%.1f°**, punkt (e, n) = (%.1f, %.1f); przecięcie z linią brzegu: %s. "
          "Mury przyczółka (GSSZMO): %d polilinie. Most leży w większości poza ramką mapy – geometria orientacyjna." %
          (br["os_przyblizona"]["azymut_siatki_deg"], br["os_przyblizona"]["punkt"][0], br["os_przyblizona"]["punkt"][1],
           ("(%.1f, %.1f)" % tuple(br["przeciecie_osi_z_linia_brzegu"])) if br["przeciecie_osi_z_linia_brzegu"] else "brak w ramce", len(br["mury_przyczolka_GSSZMO"])))
    w("")
    w("Linia brzegu (GSSWWP): Odra – od pn. ramki (e≈97) wzdłuż wsch. strony Wybrzeża; ujście Oławy na wsch. od kwartału. Odległość obszaru inwestycji od linii brzegu: **%.1f m** (minimum, wniosek z geometrii)." % J["_extras_md"]["dist_shore"])
    w("")
    w("## 10. Sprzeczności, niejasności, ograniczenia")
    w("")
    w("1. **Nazwa warstwy vs legenda M.04:** warstwa `__Obszar możliwej zabudowy` jest w legendzie PDF opisana jako „Obszar inwestycji”. Geometria = suma działek inwestycyjnych (pole %.1f m² vs M.01 3 729 m²) – przyjęto „obszar inwestycji”." % inv["pole_m2"])
    w("2. **Wydzielenie A – nazewnictwo:** legenda e-mapy M.02 opisuje różową szrafurę jako „strefa oddziaływania linii zabudowy”, M.04 – jako „Wydzielenie wewn. A zgodnie z MPZP”; plan: „obszar podwyższonej zabudowy oznaczony symbolem A” (patrz `mpzp.md`). Geometria identyczna.")
    w("3. **Dokładność linii MPZP**: wrysowane z rastra (opis na mapie) – nie należy ich traktować jako geodezyjnie wyznaczonych; zalecany zapas projektowy ≥0,3–0,5 m od linii zabudowy i granicy A (wniosek).")
    w("4. **DWG M.04 przesunięty** o ΔY = %.3f m – użycie DWG M.04 „wprost” (bez przeliczenia) w modelu dałoby błąd 165 m w osi wschód–zachód." % sh["dE_m"])
    w("5. **Pola działek** – pola geometryczne z mapy, nie z rejestru EGiB (różnice rzędu dziesiątych m² możliwe). Działki przy ramce są przycięte.")
    w("6. **Wysokości budynków** (poza Mazowiecką 19) – szacunkowe, z liczby kondygnacji; dla analiz przesłaniania należy je zweryfikować (zdjęcia 360° M.09, drona M.10, wizja lokalna).")
    w("7. **DGN V8** – nieodczytany (brak sterownika); treść zdublowana w DWG.")
    w("8. **Atrybuty A/B w etykietach przewodów** – znaczenie nieustalone (prawdopodobnie źródło/dokładność położenia wg instrukcji ZGKiKM) – do weryfikacji u gestorów/ZGKiKM.")
    w("9. **Most** – oś przybliżona (poza zasięgiem mapy); do wizualizacji należy uzupełnić geometrię mostu z innych źródeł (zdjęcia M.09/M.10, rysunki historyczne).")
    w("")
    w("## 11. Struktura `model/site.json` (skrót)")
    w("")
    w("`meta`, `crs` (definicja układu, zbieżność, przesunięcie M.04, ramka), `kontrola_georeferencji`, `granice` (obszar inwestycji + krawędzie + fronty, granice konkursowa/studialna, A, ogródki, dojazd 10/2, teren użyczony 9/2, obiekty dziedzictwa, obszar aktualizacji), "
      "`mpzp` (linie zabudowy, symbole, linie rozgraniczające, granica planów, oznaczenia), `dzialki`, `budynki`, `ulice_i_sytuacja`, `most_grunwaldzki`, `woda`, `zielen`, `teren` (pikiety, linie nieciągłości, siatka NMT 1 m, statystyki, kontrola), "
      "`uzbrojenie` (przewody z kolizjami, punkty, rzędne), `warstwy_emapy_surowe` (pełna treść e-mapy do rysunku 1:500). Poligony CCW w (e, n), bez powtórzenia 1. punktu.")
    w("")
    w("Odtworzenie: `python3 -I tools/site_extract.py` (pierwsze uruchomienie instaluje `%s` do cache i konwertuje DWG; kolejne korzystają z cache JSON)." % LIBREDWG_PKG)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(L) + "\n", encoding="utf-8")


# ============================================================================================
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--cache", default=os.environ.get("UMWD_DWG_CACHE", str(Path(tempfile.gettempdir()) / "umwd_dwg_cache")))
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--no-md", action="store_true")
    a = ap.parse_args()
    root = Path(a.root)
    mat = root / MAT_SUB
    m02 = mat / M02_SUB
    m04 = mat / M04_SUB
    P = {"root": root,
         "emapa_dwg": m02 / "mapa w formacie dgn dwg/mazowiecka_e-mapa.dwg",
         "nmt_dwg": m02 / "model terenu/mazowiecka_model terenu.dwg",
         "zielen_dwg": m02 / "zieleń/mazowiecka_zieleń.dwg",
         "pikiety_txt": m02 / "model terenu/mazowiecka_pikiety do nmt.txt",
         "drzewa_txt": m02 / "zieleń/mazowiecka_drzewa.txt",
         "m02_pdf": m02 / "e-mapa- pdf-A3/mazowiecka_e-mapa.pdf",
         "m04_dwg": m04 / "Mapa schematyczna WRO UMWD - M.04.dwg",
         "m04_pdf": m04 / "Mapa schematyczna WRO UMWD - M.04.pdf"}
    for k, v in P.items():
        if k != "root" and not v.exists():
            sys.exit("Brak pliku: %s" % v)
    S = extract(P, Path(a.cache))
    B = S["B"]
    inv = B["obszar_inwestycji"]
    T = S["terrain"]
    extras = {}
    extras["geod"] = geodetic_info()
    cps, ctrl_txt, ctrl_h = control_points(S)
    extras["georef"] = {"punkty_kontrolne": cps, "pdf_M04": check_pdf_georef(P, S),
                        "przesuniecie_M04": S["_m04_shift"]}
    extras["ctrl_txt"], extras["ctrl_h"] = ctrl_txt, ctrl_h
    extras["inv_edges"] = edges_info(inv, S, "obszar inwestycji")
    extras["inv_fronts"] = group_fronts(extras["inv_edges"])
    extras["tstats"] = [terrain_stats(T, inv, "obszar inwestycji"),
                        terrain_stats(T, B["wydzielenie_A_mpzp"].intersection(inv), "wydzielenie A ∩ obszar inwestycji"),
                        terrain_stats(T, B["granica_opracowania_konkursowego"], "granica opracowania konkursowego"),
                        terrain_stats(T, B["ogrodki_przydomowe"], "ogródki przydomowe"),
                        terrain_stats(T, B["teren_uzyczony_9_2"], "dz. 9/2 (skwer)"),
                        terrain_stats(T, B["dojazd_10_2"], "dz. 10/2 (dojazd)")]
    extras["bridge"] = bridge_info(S)
    # chodnik przed frontem Mazowieckiej 19 (pas 1-4 m na zachod od frontu)
    m19 = [q for q in S["buildings"] if q["addr_nr"] == "19"]
    if m19:
        pol = m19[0]["poly"]
        front = pol.buffer(4.0).difference(pol.buffer(1.0))
        west = box(pol.bounds[0] - 5, pol.bounds[1], pol.centroid.x - 4, pol.bounds[3])
        Pp = sample_poly(front.intersection(west), 0.5)
        Hh = T["f"](Pp[:, 0], Pp[:, 1]) if len(Pp) else np.array([])
        Hh = Hh[~np.isnan(Hh)]
        extras["maz19_front_H"] = r2(np.median(Hh)) if len(Hh) else None
    util_sum = collections.OrderedDict()
    for u in S["utilities"]["lines"]:
        ls = LineString(u["pts"])
        L_ = ls.intersection(inv).length
        if L_ > 0.05:
            util_sum[u["typ"]] = util_sum.get(u["typ"], 0.0) + L_
    extras["util_summary"] = {k: r1(v) for k, v in util_sum.items()}
    J = build_json(P, S, extras)
    corner_H = []
    for p in J["granice"]["obszar_inwestycji"]["pts"]:
        h = T["f"](p[0], p[1])
        corner_H.append((p, None if np.isnan(h) else float(h)))
    shore = unary_union([LineString(g["pts"]) for g in S["situation"]["woda_linia_brzegu"]])
    J["_extras_md"] = {"corner_H": [[c[0], (r2(c[1]) if c[1] is not None else None)] for c in corner_H],
                       "maz19_front_H": extras.get("maz19_front_H"), "dist_shore": r1(inv.distance(shore))}
    out_json = root / "model/site.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(J, f, ensure_ascii=False, separators=(",", ":"))
    print("zapisano", out_json, "%.1f MB" % (out_json.stat().st_size / 1e6))
    if not a.no_png:
        out_png = root / "docs/30_lokalizacja/img/site_kontrola.png"
        make_png(S, J, out_png)
        print("zapisano", out_png)
    if not a.no_md:
        out_md = root / "docs/30_lokalizacja/geometria.md"
        make_md(P, S, J, out_md)
        print("zapisano", out_md)


if __name__ == "__main__":
    main()
