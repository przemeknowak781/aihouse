# -*- coding: utf-8 -*-
"""Kondygnacja Sejmiku S-2 – kontrole geometrii, bilans powierzchni wobec programu i eksport JSON.

Uruchomienie (z katalogu umwd/):  python3 docs/20_koncepcja/_s2_geometria.py
Zapisuje: docs/20_koncepcja/kondygnacja_S2.json (struktura jak koncepcja.json["kondygnacja_sejmiku"]).
Sekcje wydruku [G1]…[G8] są przywoływane w kondygnacja_S2.md.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s2_model as M  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kondygnacja_S2.json")


def hr(t):
    print("\n" + "=" * 96 + "\n" + t + "\n" + "=" * 96)


S = M.level_S()
A = M.level_ANT()
rows, aisles = M.build_rows()
CORES = {"C-A": M.CORE_A, "C-B": M.CORE_B}
CIRC_S = {"KUL", "KW.S.01", "KW.S.02", "KW.S.03", "KW.S.04", "SWD.02"}
CIRC_A = {"KW.A.01", "KW.A.02", "KW.A.03", "SWD.02g", "SWD.01g"}
OPEN_ZONES = {"SWD.06", "SWD.05", "SWD.03"}

# -------------------------------------------------------------------------------------------------
hr("[G1] Poprawność poligonów, położenie w obrysie wieży (strefa A) i w licu wewnętrznym")
bad = 0
for lvl, D in (("S", S), ("ANT", A)):
    for k, g in D.items():
        ok = g.is_valid and g.area > 0
        out_w = g.difference(M.W_UV).area
        out_i = g.difference(M.INNER.buffer(1e-6)).area
        if not ok or out_w > 1e-6 or out_i > 1e-3:
            bad += 1
            print(f"  ! {lvl} {k}: valid={g.is_valid} poza wieżą {out_w:.4f} poza licem {out_i:.4f}")
print(f"Wieża (uv): pole {M.W_UV.area:.2f} m² (koncepcja 1 145,83); wnętrze od lica 0,50 m: {M.INNER.area:.2f} m² (1 080,1)")
print(f"Pomieszczeń S: {len(S)}, antresoli: {len(A)}; niepoprawnych lub poza obrysem: {bad}")
en_out = 0
for D in (S, A):
    for k, g in D.items():
        for ring in M.poly_list_en(g):
            from shapely.geometry import Polygon
            if Polygon(ring).difference(M.W_EN.buffer(0.002)).area > 1e-4:
                en_out += 1
print(f"Kontrola w układzie (e, n): poligony wystające poza obrys wieży z koncepcja.json: {en_out}")

# -------------------------------------------------------------------------------------------------
hr("[G2] Kolizje (nakładanie się pomieszczeń, trzonów, rzędów)")
items = list(S.items()) + list(CORES.items())
ov = []
for i in range(len(items)):
    for j in range(i + 1, len(items)):
        a = items[i][1].intersection(items[j][1]).area
        if a > 1e-4:
            ov.append((items[i][0], items[j][0], round(a, 4)))
print("Poziom S – nakładania > 0,0001 m²:", ov if ov else "brak")
itemsA = list(A.items()) + list(CORES.items())
ovA = []
for i in range(len(itemsA)):
    for j in range(i + 1, len(itemsA)):
        a = itemsA[i][1].intersection(itemsA[j][1]).area
        if a > 1e-4:
            ovA.append((itemsA[i][0], itemsA[j][0], round(a, 4)))
print("Antresola – nakładania:", ovA if ovA else "brak")
rz = unary_union([r["band"] for r in rows] + [aisles["east"], aisles["west_ramp"], aisles["west_flat"]])
print(f"Rzędy i przejścia w obrysie sali: poza salą {rz.difference(S['SWD.01'].buffer(1e-6)).area:.4f} m²; "
      f"kolizja z prezydium/mównicą: {unary_union([r['band'] for r in rows]).intersection(M.PRES.union(M.LECTERN)).area:.4f} m²")

# -------------------------------------------------------------------------------------------------
hr("[G3] Dostęp: każde pomieszczenie ma drzwi na komunikację (punkt drzwi ≤ 0,30 m od obu poligonów)")
cellsA = {**M.CORE_A_CELLS, **M.CORE_B_CELLS}


def geom(name, lvl):
    if name in cellsA:
        return cellsA[name]
    return (S if lvl == "S" else A)[name]


miss = []
for lvl, D, doors, circ in (("S", S, M.DOORS_S, CIRC_S), ("ANT", A, M.DOORS_ANT, CIRC_A)):
    reach = {k: False for k in D if k not in circ}
    for a_, b_, (u, v), w in doors:
        p = Point(u, v)
        da, db = geom(a_, lvl).distance(p), geom(b_, lvl).distance(p)
        okd = da <= 0.30 and db <= 0.30
        if not okd:
            print(f"  ! {lvl} drzwi {a_}→{b_} ({u},{v}) odległości {da:.2f}/{db:.2f}")
        if a_ in reach and (b_ in circ or b_ in cellsA) and okd:
            reach[a_] = True
    for k, r in reach.items():
        if not r and k in OPEN_ZONES:      # strefy otwarte (lada szatni, bar, strefa multimedialna) – styk z holem ≥ 2 m
            hall = S["SWD.02"] if lvl == "S" else A["SWD.02g"]
            if D[k].boundary.intersection(hall.buffer(0.01)).length >= 2.0:
                reach[k] = True
                print(f"  {lvl} {k}: strefa otwarta, styk z holem {D[k].boundary.intersection(hall.buffer(0.01)).length:.1f} m")
        if not reach[k]:
            miss.append((lvl, k))
print("Pomieszczenia bez drzwi na komunikację:", miss if miss else "brak (K1 usunięte)")
print("Uwaga: SWD.01 (sala) – 4 drzwi: NW do holu 1,6 m, SW 1,2 m i SE 1,6 m do kuluaru, drzwi prezydium 1,0 m;"
      " galeria – drzwi z korytarza publicznego i drzwi przedsionka A.")

# -------------------------------------------------------------------------------------------------
hr("[G4] Bilans powierzchni netto wobec programu (program.yaml: SWD, PHS.05, PP.06, IT.02)")
tab = []
order = ["SWD.01", "SWD.01g", "SWD.02", "SWD.02g", "SWD.03", "SWD.04", "SWD.05", "SWD.06", "SWD.07", "SWD.08", "SWD.09",
         "SWD.10a", "SWD.10b", "SWD.11a", "SWD.11b", "SWD.12a", "SWD.12b", "SWD.13", "SWD.14", "SWD.15",
         "PHS.05a", "PHS.05b", "PHS.05c", "PP.06", "IT.02"]
area = {**{k: v.area for k, v in S.items()}, **{k: v.area for k, v in A.items()}}
print(f"{'kod':9s} {'pow. [m²]':>9s} {'program':>8s} {'zakres':>11s} {'Δ':>7s}  poziom  nazwa")
for k in order:
    nm, cat, pr, rg = M.PROG[k]
    lvl = "ANT" if k in A else "S"
    a = area[k]
    d = (a - pr) if pr else None
    flag = ""
    if rg:
        aa = a + (area.get(k + "g", 0.0) if k in ("SWD.01", "SWD.02") else 0.0)
        flag = ("✔" if rg[0] - 1e-6 <= aa <= rg[1] + 1e-6 else "✗") + ("Σ" if k in ("SWD.01", "SWD.02") else "")
    print(f"{k:9s} {a:9.2f} {pr if pr else '':>8} {str(rg) if rg else '':>11s} {('%+.1f' % d) if d is not None else '':>7s}  {lvl:5s} {flag} {nm[:60]}")
    tab.append((k, a, pr, rg, d, lvl))
sala_tot = area["SWD.01"] + area["SWD.01g"]
hol_tot = area["SWD.02"] + area["SWD.02g"]
phs = area["PHS.05a"] + area["PHS.05b"] + area["PHS.05c"]
print(f"\nSWD.01 razem (płyta + galeria) = {area['SWD.01']:.1f} + {area['SWD.01g']:.1f} = {sala_tot:.1f} m² (program 320; zakres 280–380) "
      f"{'✔' if 280 <= sala_tot <= 380 else '✗'}")
print(f"SWD.02 hol razem (wolna podłoga bez szatni i baru) = {area['SWD.02']:.1f} + {area['SWD.02g']:.1f} = {hol_tot:.1f} m² "
      f"(program 150; zakres 120–220) {'✔' if 120 <= hol_tot <= 220 else '✗'}")
print(f"PHS.05 razem = {phs:.1f} m² (program 45; zakres 35–60) {'✔' if 35 <= phs <= 60 else '✗'}")
prog_sum = sum(M.PROG[k][2] for k in order if M.PROG[k][2]) + M.PHS05_PROG[0]
proj_sum = sum(area[k] for k in order)
print(f"Suma programu SWD + PHS.05 + PP.06 + IT.02 = {prog_sum} m²; w projekcie (S + antresola) = {proj_sum:.1f} m² "
      f"(Δ {proj_sum - prog_sum:+.1f})")
lo_sum = sum((M.PROG[k][3][0] if M.PROG[k][3] else 0) for k in order) + M.PHS05_PROG[1][0]
print(f"Suma dolnych granic zakresów = {lo_sum} m² → zapas projektu nad minimum {proj_sum - lo_sum:+.1f} m²")
TOT = {"SWD.01": sala_tot, "SWD.02": hol_tot}
below = [k for k, a, pr, rg, d, l in tab if rg and TOT.get(k, a) < rg[0] - 1e-6]
above = [k for k, a, pr, rg, d, l in tab if rg and TOT.get(k, a) > rg[1] + 1e-6]
print("Pozycje poniżej / powyżej zakresu (SWD.01 i SWD.02 liczone łącznie z częścią na antresoli):",
      below if below else "brak", "/", above if above else "brak")

# -------------------------------------------------------------------------------------------------
hr("[G5] Bilans poziomu S (od lica wewnętrznego) i ściany wewnętrzne (D1)")
occ = unary_union(list(S.values()) + list(CORES.values()))
walls = M.INNER.difference(occ)
rooms_net = sum(v.area for k, v in S.items() if k not in CIRC_S or k == "SWD.02")
circ = sum(S[k].area for k in CIRC_S if k != "SWD.02")
cores = M.CORE_A.area + M.CORE_B.area
print(f"Wnętrze {M.INNER.area:.1f} = pomieszczenia (z salą, holem, szatnią) {rooms_net:.1f} + komunikacja KW/KUL {circ:.1f} "
      f"+ trzony {cores:.1f} + ściany wewn. {walls.area:.1f}  (kontrola: {rooms_net + circ + cores + walls.area:.1f})")
# długość ścian ≈ (suma obwodów pomieszczeń + trzonów − obwód wnętrza)/2
touch = 0.0
wb = walls.buffer(0.02)
ext = M.INNER.boundary.buffer(0.02)
for g in list(S.values()) + list(CORES.values()):
    touch += g.boundary.intersection(wb).difference(ext).length
wall_len = touch / 2
print(f"Długość ścian wewn. (styk pomieszczeń ze ścianą, /2) ≈ {wall_len:.0f} m → średnia grubość {walls.area / wall_len:.3f} m "
      f"(koncepcja v1.0: 0,151 m; D1: ≈ 0,20 / 0,30 m)")
thick = {}
for t in (0.20, 0.30):
    thick[t] = walls.buffer(-t / 2 + 0.01).area
print(f"Kontrola grubości: część ścian grubszych niż 0,18 m: {walls.buffer(-0.09).buffer(0.09).area / walls.area * 100:.0f} % pola ścian;"
      f" grubszych niż 0,28 m: {walls.buffer(-0.14).buffer(0.14).area / walls.area * 100:.0f} %")
print(f"Ściany zewn. (pas 0,50 m): {M.W_UV.area - M.INNER.area:.1f} m²; PC poziomu S = {M.W_UV.area:.1f} m²")
print(f"Udział ścian wewn. + zewn. w PC: {(walls.area + M.W_UV.area - M.INNER.area) / M.W_UV.area * 100:.1f} %")

# -------------------------------------------------------------------------------------------------
hr("[G6] Antresola +30,90 – powierzchnia, udział, otwarcie na wnętrze (WT § 3 pkt 19)")
antw = A["SWD.02g"].union(A["SWD.03"]).union(A["SWD.05"]).union(A["KW.A.03"])
pub = A["SWD.01g"].union(A["KW.A.01"]).union(A["KW.A.02"]).union(A["PHS.05c"])
ant_tot = sum(v.area for v in A.values())
print(f"Antresola razem {ant_tot:.1f} m² = {ant_tot / M.W_UV.area * 100:.1f} % rzutu wieży "
      f"(część radnych {antw.area:.1f} m²; część publiczna {pub.area:.1f} m²)")
edge_hall = antw.boundary.intersection(M.VOID_HALL.buffer(0.01)).length
edge_sala = A["SWD.01g"].boundary.intersection(box(21.95, 12.6, 22.05, 22.65)).length
print(f"Krawędź antresoli radnych otwarta na pustkę holu: {edge_hall:.1f} m; krawędź galerii otwarta na salę: {edge_sala:.1f} m")
print("Zamknięte przegrodami na poziomie +30,90 są tylko: przedsionek A' (element klatki A), toaleta PHS.05c i korytarz"
      " publiczny EI 30 – dojścia ewakuacyjne/usługi galerii; wszystkie pomieszczenia programu zamknięte leżą na poziomie S.")
over_rooms = {}
for k in ("SWD.12a", "SWD.12b", "SWD.13", "SWD.14", "PHS.05a", "PHS.05b", "KW.S.01", "KW.S.03", "SWD.11b", "SWD.07", "KW.S.02"):
    over_rooms[k] = (S[k].intersection(antw.union(pub)).area / S[k].area) if S[k].area else 0
print("Udział rzutu pomieszczeń S przykryty antresolą (wys. w świetle pod nią 3,30 m ≥ 3,0 m):",
      {k: f"{v * 100:.0f} %" for k, v in over_rooms.items() if v > 0.001})
fac = M.INNER.difference(M.INNER.buffer(-1.35))
print(f"Antresola w pasie 1,35 m od lica elewacji: {antw.union(pub).intersection(fac).area:.2f} m² "
      f"(0 → okna 1,65 × 4,20 / 5,00 m bez zmian, porządek elewacji zachowany)")

# -------------------------------------------------------------------------------------------------
hr("[G7] Sala obrad – stanowiska (szczegóły: _s2_sala.py)")
n_desk = sum(r["n"] for r in rows)
print("Rzędy:", [(r["k"], r["R"], r["z"], r["n"], "+1 wózek") for r in rows])
print(f"Stanowiska stałe: {n_desk} + {len(rows)} dla wózków = {n_desk + len(rows)} (wymagane 44) "
      f"{'✔' if n_desk + len(rows) >= 44 else '✗'}; prezydium 4 + mównica na posadzce +0,00")
fs = M.floor_seats()
cnt = {}
for *_, t in fs:
    cnt[t] = cnt.get(t, 0) + 1
print("Poza rzędami:", cnt)
gs = M.gallery_seats()
gcnt = {}
for *_, t in gs:
    gcnt[t] = gcnt.get(t, 0) + 1
print("Galeria:", gcnt, "→ miejsca siedzące", gcnt.get("miejsce", 0) + gcnt.get("opiekun", 0), "+ wózki", gcnt.get("wozek", 0))

# -------------------------------------------------------------------------------------------------
hr("[G8] Eksport JSON")


def entry(k, g, lvl):
    nm, cat, pr, rg = M.PROG.get(k, (k, "inne", None, None))
    return {"nazwa": nm, "kategoria": cat, "poziom": lvl, "pow_m2": round(g.area, 2), "program_m2": pr,
            "zakres_m2": list(rg) if rg else None,
            "obrys_uv": M.poly_list_uv(g), "obrys_en": M.poly_list_en(g)}


pom = {}
for k, g in CORES.items():
    pom[k] = {"nazwa": "Trzon A (obrys bez zmian; układ: klatka A + przedsionek z MOE, A1/A2 1 600 kg kab. 1,5×2,1 drzwi pn., R 1 000 kg)"
              if k == "C-A" else "Trzon B (obrys bez zmian; układ: klatka B + przedsionek z MOE, P1/P2 1 600 kg kab. 1,5×2,1 drzwi wsch., szachty po dźwigu T)",
              "kategoria": "trzon", "poziom": "S+ANT", "pow_m2": round(g.area, 2), "program_m2": None, "zakres_m2": None,
              "obrys_uv": M.poly_list_uv(g), "obrys_en": M.poly_list_en(g)}
for k, g in S.items():
    pom[k] = entry(k, g, "S")
antp = {k: entry(k, g, "ANT") for k, g in A.items()}

rz_json = []
for r in rows:
    rz_json.append({"R": r["R"], "miejsc": r["n"] + 1, "w_tym_dla_wozka": 1, "rzedna": r["z"],
                    "sektor_deg": [round(r["a0"], 1), round(r["a1"], 1)], "linia_siedzisk_R": round(r["rc"], 2),
                    "obrys_uv": M.poly_list_uv(r["band"])})
J = {
    "wersja": "S-2 / wariant „hol z galerią” – 17.11.2026 (opracowanie kondygnacji Sejmiku do scalenia z koncepcja.json)",
    "zrodlo": "docs/20_koncepcja/_s2_model.py (geometria), _s2_geometria.py (kontrole i eksport), _s2_sala.py, _s2_ewakuacja.py",
    "uklad": "uv wieży: e = 74,606 + 0,97155·u − 0,23684·v; n = 40,756 + 0,23684·u + 0,97155·v",
    "posadzka": {"wzgl": M.Z_S, "npm": 146.6},
    "wysokosc_do_najnizszego_pokrycia_m": 8.9,
    "antresola": {"wzgl": M.Z_ANT, "npm": 150.2, "pow_m2": round(ant_tot, 2),
                  "udzial_rzutu_proc": round(ant_tot / M.W_UV.area * 100, 1),
                  "czesc_radnych_m2": round(antw.area, 2), "czesc_publiczna_m2": round(pub.area, 2),
                  "wycofanie_od_elewacji_m": 1.35, "wys_w_swietle_pod_m": 3.30,
                  "wys_w_swietle_nad_m": round(M.Z_SPOD_DACHU - M.Z_ANT, 2)},
    "sala": {
        "pow_m2": round(area["SWD.01"], 2), "pow_z_galeria_m2": round(sala_tot, 2),
        "wys_w_swietle_m": round(M.H_SALA, 2),
        "wymiary": "u 22,0–39,5 × v 12,6–29,2 minus łuk R 13,5 i reżyserka SWD.04 (naroże SE)",
        "ognisko_rzedow_uv": list(M.F), "rozstaw_rzedow_m": M.PITCH, "przewyzszenie_rzedu_m": M.RISE,
        "rzedy": rz_json,
        "stale_stanowiska": n_desk + len(rows), "wymagane_stanowiska": 44,
        "modul_stanowiska_m": M.DESK_W, "plyta_razem": 70, "galeria": 31,
        "galeria_wozki": 3,
        "wozki": "w każdym rzędzie stanowisko dla wózka 1,5 m na końcu zach. przy pochylni (4) + 3 na galerii",
        "pochylnie": "przejście wsch. promieniowe i zach. wzdłuż ściany sali – nachylenie ≤ 5,0 % (0,09 m na 1,80 m), poręcze 0,75/0,90",
        "prezydium": "stół 6,0 m (4 os.) przy pełnej ścianie pd., posadzka +0,00; za nim drzwi z kuluaru",
        "mownica": "przed prezydium w ognisku F, blat regulowany 0,75–1,20 m (D6), pętla indukcyjna",
        "galeria_publicznosci": {"poziom": M.Z_ANT, "obrys_uv": M.poly_list_uv(A["SWD.01g"]),
                                  "rzedy": [{"nr": n, "u_oka": ue, "podest_m": dz, "v": [v0, v1], "uklad": t}
                                            for n, ue, dz, v0, v1, t in M.GAL_ROWS],
                                  "balustrada": "część pionowa 0,70 m + pozioma 0,50 m (WT § 298 ust. 7)"},
        "miejsca_poza_rzedami": cnt,
    },
    "pomieszczenia": pom,
    "antresola_pomieszczenia": antp,
    "pustka_holu": {"pow_m2": round(M.VOID_HALL.area, 2), "obrys_uv": M.poly_list_uv(M.VOID_HALL)},
    "trzony_uklad": {"zalozenie": "do scalenia z poprawką I5 (obrysy trzonów bez zmian)",
                     "A": {k: M.poly_list_uv(v)[0] for k, v in M.CORE_A_CELLS.items()},
                     "B": {k: M.poly_list_uv(v)[0] for k, v in M.CORE_B_CELLS.items()},
                     "drzwi_dzwigow": [{"dzwig": a, "uv": list(p), "kierunek": list(d), "przystanki": s}
                                       for a, p, d, s in M.LIFT_DOORS]},
    "drzwi": {"S": [{"z": a, "do": b, "uv": list(p), "szer_m": w} for a, b, p, w in M.DOORS_S],
              "ANT": [{"z": a, "do": b, "uv": list(p), "szer_m": w} for a, b, p, w in M.DOORS_ANT]},
    "bilans": {"wnetrze_S_m2": round(M.INNER.area, 2), "pomieszczenia_S_m2": round(rooms_net, 2),
               "komunikacja_S_m2": round(circ, 2), "trzony_m2": round(cores, 2), "sciany_wewn_m2": round(walls.area, 2),
               "antresola_m2": round(ant_tot, 2), "program_suma_m2": prog_sum, "projekt_suma_m2": round(proj_sum, 2),
               "hol_razem_m2": round(hol_tot, 2), "PHS05_razem_m2": round(phs, 2)},
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(J, f, ensure_ascii=False, indent=1)
print("Zapisano", os.path.relpath(OUT, M.ROOT), f"({os.path.getsize(OUT) / 1024:.0f} kB)")
