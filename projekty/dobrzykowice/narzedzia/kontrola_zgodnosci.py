#!/usr/bin/env python3
"""Kontrola zgodności modelu z DWG: linie ścian z pliku źródłowego (lokal 1, parter i piętro) vs lica ścian modelu.

Wejście: zrzut JSON pliku Projekt_wersja_15_10_2026.dwg (LibreDWG → @mlightcad/libredwg-web, struktura DwgDatabase) —
plik źródłowy nie jest wersjonowany (dane Inwestora). Wynik: udział długości linii DWG leżących na licu ściany modelu
(≤ tolerancja) albo wewnątrz ściany/słupa modelu (linie osi, szyb, ościeży) oraz lista odchyłek.

Użycie:
    PYTHONPATH=src python3 projekty/dobrzykowice/narzedzia/kontrola_zgodnosci.py <Projekt.json> [--tol 0.015]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from shapely.geometry import LineString, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
from lamela.model import load_model, parse_przekroj  # noqa: E402

X0 = {"P0": 1914.3, "P1": 3216.2}          # przesunięcie rzutu w DWG [cm] → oś A
RZUT = {"P0": (1870, 2980), "P1": (3180, 4280)}
Y0 = 4098.1


def segs(e):
    if e["type"] == "LINE":
        return [((e["startPoint"]["x"], e["startPoint"]["y"]), (e["endPoint"]["x"], e["endPoint"]["y"]))]
    if e["type"] == "LWPOLYLINE":
        V = [(v["x"], v["y"]) for v in e["vertices"]]
        closed = bool((e.get("flag", 0) or 0) & 513)
        return list(zip(V, V[1:] + (V[:1] if closed else [])))
    return []


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("json")
    ap.add_argument("--tol", type=float, default=0.015)
    a = ap.parse_args(argv)
    db = json.load(open(a.json, encoding="utf-8"))
    ms = [e for e in db["entities"] if e.get("ownerBlockRecordSoftId") == "1F"]
    m = load_model(ROOT / "projekty/dobrzykowice/model/budynek.yaml", None, strict=False)
    raport = {}
    for k in ("P0", "P1"):
        polys = [s.polygon for s in m.sciany(k)]
        z = next(kk.rzedna for kk in m.kondygnacje if kk.id == k) + 1.0
        for sl in m.raw.get("slupy") or []:
            if sl["z_od"] <= z <= sl["z_do"]:
                bx, by = parse_przekroj(sl["przekroj"])
                x, y = sl["xy"]
                polys.append(box(x - bx / 2, y - by / 2, x + bx / 2, y + by / 2))
        U = unary_union(polys)
        Ub = U.buffer(a.tol)
        tot = cov = 0.0
        klasy = {"schody / otwór schodowy": 0.0, "szacht instalacyjny (pominięty w modelu)": 0.0, "inne": 0.0}
        odch = []
        xa, xb = RZUT[k]
        for e in ms:
            if e.get("colorIndex") != 1 or (e.get("lineType") or "") not in ("", "BYLAYER"):
                continue                                     # tylko ciągłe czerwone (ściany); osie kreskowe pomijamy
            for p, q in segs(e):
                if not (xa <= min(p[0], q[0]) and max(p[0], q[0]) <= xb and 4000 <= min(p[1], q[1]) and
                        max(p[1], q[1]) <= 4990):
                    continue
                P = [((x - X0[k]) / 100, (y - Y0) / 100) for x, y in (p, q)]
                ls = LineString(P)
                L = ls.length
                if L < 0.05:
                    continue
                tot += L
                c = ls.intersection(Ub).length               # część linii DWG w obrębie ścian/słupów modelu (± tol)
                cov += c
                rest = L - c
                if rest < 0.01:
                    continue
                mx, my_ = ls.interpolate(0.5, normalized=True).coords[0]
                if 1.3 <= mx <= 5.6 and 3.85 <= my_ <= 4.78:
                    klasy["schody / otwór schodowy"] += rest
                elif 2.6 <= mx <= 3.4 and 0.1 <= my_ <= 0.4:
                    klasy["szacht instalacyjny (pominięty w modelu)"] += rest
                else:
                    klasy["inne"] += rest
                    odch.append((round(rest, 3), [tuple(round(v, 3) for v in pt) for pt in P]))
        # kontrola odwrotna: lica ścian modelu lokalu 1 (Y ≤ 8,865) vs linie DWG (wszystkie czerwone, także osie)
        dl = []
        for e in ms:
            if e.get("colorIndex") != 1:
                continue
            for p, q in segs(e):
                if xa <= min(p[0], q[0]) and max(p[0], q[0]) <= xb and 4000 <= min(p[1], q[1]) and max(p[1], q[1]) <= 4990:
                    dl.append(LineString([((x - X0[k]) / 100, (y - Y0) / 100) for x, y in (p, q)]))
        D = unary_union(dl).buffer(a.tol)
        Uo = U.difference(unary_union([o.footprint.buffer(1e-4) for w in m.sciany(k) for o in w.otwory]))  # otwory wycięte
        Bm = Uo.boundary.intersection(box(-1.0, -1.0, 11.0, 8.865 + 1e-6))
        rev_tot, rev_cov = Bm.length, Bm.intersection(D).length
        extra = Bm.difference(D)
        ex = [g for g in getattr(extra, "geoms", [extra]) if g.length > 0.05]
        raport[k] = dict(dlugosc_m=round(tot, 2), w_scianach_m=round(cov, 2),
                         zgodne_proc=round(100 * cov / tot, 1) if tot else None,
                         poza_scianami={kk: round(v, 2) for kk, v in klasy.items()}, odchylki=sorted(odch, reverse=True),
                         lica_modelu_m=round(rev_tot, 2), lica_z_linia_dwg_m=round(rev_cov, 2),
                         lica_bez_dwg=sorted(((round(g.length, 3), [tuple(round(v, 3) for v in c) for c in g.coords][:2])
                                              for g in ex), reverse=True))
    for k, r in raport.items():
        print(f"{k}: czerwone linie ciągłe DWG {r['dlugosc_m']} m, w obrębie ścian/słupów modelu (±{a.tol} m): "
              f"{r['w_scianach_m']} m ({r['zgodne_proc']} %); poza: {r['poza_scianami']}")
        print(f"    kontrola odwrotna: lica ścian modelu (lokal 1) {r['lica_modelu_m']} m, w tym na liniach DWG "
              f"{r['lica_z_linia_dwg_m']} m ({100 * r['lica_z_linia_dwg_m'] / r['lica_modelu_m']:.1f} %)")
        for L, P in r["lica_bez_dwg"][:12]:
            print(f"      lico modelu bez linii w DWG: {L:6.3f} m  od {P}")
        for L, P in r["odchylki"][:15]:
            print(f"    poza ścianami {L:6.3f} m  linia DWG {P}")
    return raport


if __name__ == "__main__":
    main()
