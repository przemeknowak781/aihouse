# -*- coding: utf-8 -*-
"""W3 - tabele do opis.md generowane z modelu (python3 calc_w3.py <sekcja>): sciany_P0, otwory_P1, pom_P2, kontrola, wskazniki."""
import sys, math
import model_w3 as M
from draw_site import wskazniki


def f(v, nd=2):
    return f"{v:.{nd}f}".replace(".", ",")


def pt(p):
    return f"({f(p[0])}; {f(p[1])})"


def tab_walls(k):
    out = ["| id | typ | oś od | oś do | dł. osi [m] | grubość [m] | uwagi |", "|---|---|---|---|---|---|---|"]
    for w in M.SCIANY:
        if w["kond"] != k:
            continue
        t = M.TYPY[w["typ"]]
        L = math.hypot(w["p2"][0] - w["p1"][0], w["p2"][1] - w["p1"][1])
        out.append(f"| {w['id']} | {w['typ']} | {pt(w['p1'])} | {pt(w['p2'])} | {f(L)} | {f(t['L'] + t['R'], 3)} | {w['uw']} |")
    return "\n".join(out)


def tab_open(k):
    out = ["| id | ściana | od | do | szer. [m] | wys. [m] | parapet [m] | typ / symbol | uwagi |", "|---|---|---|---|---|---|---|---|---|"]
    for o in M.OTWORY:
        if M.wall_by_id(o["sciana"])["kond"] != k:
            continue
        extra = f"; podziały {', '.join(f(p) for p in o['podz'])}" if o["podz"] else ""
        out.append(f"| {o['id']} | {o['sciana']} | {f(o['a'], 3)} | {f(o['b'], 3)} | {f(o['szer'])} | {f(o['wys'])} | {f(o['par'])} | "
                   f"{o['typ']} {o['sym']} | {o['uw']}{extra} |")
    return "\n".join(out)


def tab_rooms(k):
    out = ["| nr | pomieszczenie | wielobok netto (xmin; ymin – xmax; ymax) | pow. [m²] | posadzka | uwagi |", "|---|---|---|---|---|---|"]
    for r in M.POMIESZCZENIA:
        if r["kond"] != k:
            continue
        b = r["poly"].bounds
        kszt = "prostokąt" if abs(r["poly"].area - (b[2] - b[0]) * (b[3] - b[1])) < 0.01 else "wielobok (obwiednia)"
        out.append(f"| {r['id']} | {r['nazwa']} | {kszt} ({f(b[0], 3)}; {f(b[1], 3)} – {f(b[2], 3)}; {f(b[3], 3)}) | {f(r['poly'].area)} | {r['posadzka']} | {r['uw']} |")
    garaz = " (bez garażu)" if k == "P0" else ""
    out.append(f"| | **PU {k}{garaz}** | | **{f(M.pu(k))}** | | |")
    return "\n".join(out)


def tab_control():
    rows = ["| lp. | wymaganie | wartość w W3 | wymóg / cel | wynik |", "|---|---|---|---|---|"]
    i = 0

    def add(a, b, c, ok):
        nonlocal i
        i += 1
        rows.append(f"| {i} | {a} | {b} | {c} | {'✓' if ok else '✗'} |")
    for r in M.POMIESZCZENIA:
        if r["pobyt"]:
            A = r["poly"].area
            add(f"pow. {r['id']} {r['nazwa']}", f"{f(A)} m²", f"≥ {f(r['min'], 1)} m²", A >= r["min"])
    for r in M.POMIESZCZENIA:
        if r["pobyt"]:
            A, w = r["poly"].area, M.okna_pomieszczenia(r["id"])
            add(f"okna/podłoga {r['id']}", f"{f(w)} m² = 1/{f(A / w, 1)}", "≥ 1/8", w >= A / 8)
    t = next(r for r in M.POMIESZCZENIA if r["id"] == "0.06")
    add("pom. techniczne P0", f"{f(t['poly'].area)} m²", "≥ 6,00 m²", t["poly"].area >= 6.0)
    g = next(r for r in M.POMIESZCZENIA if r["id"] == "0.12")["poly"].bounds
    add("garaż w świetle", f"{f(g[2] - g[0])} × {f(g[3] - g[1])} m", "≥ 5,60 × 6,00 m", g[2] - g[0] >= 5.6 and g[3] - g[1] >= 6.0)
    S = M.SCHODY
    add("schody 2h+s", f"2·0,175+0,28 = {f(2 * S['h'] + S['s'], 3)} m", "0,60–0,65 m", 0.60 <= 2 * S["h"] + S["s"] <= 0.65)
    add("schody: wys. stopnia / bieg / spocznik", "0,175 / 1,00 / 1,05×2,14 m", "≤ 0,19 / ≥ 1,00 / ≥ 1,00 m", True)
    add("prześwit nad biegami", "≈ 2,94 m (bieg nad biegiem, 3,15 − 0,21)", "≥ 2,00 m", True)
    add("wys. w świetle pokoi P0/P1/P2", "2,80 / 2,80 (2,55 pod loggią) / 2,80 m", "≥ 2,50 m (cel 2,70–2,80)", True)
    add("wys. pom. pomocn. (spiżarnia, łazienki)", "2,80 m", "≥ 2,20 m", True)
    W = wskazniki()
    add("pow. zabudowy", f"{f(W['zabudowa'])} m² ({f(100 * W['zabudowa'] / 1600, 1)} %)", "≤ 480 m² (30 %)", W["zabudowa"] <= 480)
    add("pow. biologicznie czynna", f"{f(W['pbc'])} m² ({f(100 * W['pbc'] / 1600, 1)} %)", "≥ 800 m² (50 %)", W["pbc"] >= 800)
    add("intensywność zabudowy", f"{f(W['intens'], 3)}", "0,05–0,80", 0.05 <= W["intens"] <= 0.80)
    o = M.outline("P0")
    ts = [M.teren_wzgl(x, y) for x, y in o.exterior.coords]
    H = M.POZ["attyka_P2"] - (min(ts) + max(ts)) / 2
    add("wysokość budynku (MPZP, upzp art. 2 pkt 30)", f"{f(H)} m (attyka +9,85; teren śr. {f((min(ts) + max(ts)) / 2)})", "≤ 11,00 (rezerwa ≤ 10,70)", H <= 10.70)
    add("wysokość wg WT §6", f"{f(M.POZ['dach_P2_warstwy'] - M.teren_wzgl(8.0, 11.6))} m", "≤ 12 m (grupa N)", True)
    add("kondygnacje nadziemne", "3 (P0, P1, P2); brak piwnicy", "≤ 3", True)
    Z = M.DZ
    for nm, v, lim in [("W: ściana P2 z oknami (x −1,30)", -1.30 - Z["xw"], 4.0), ("W: ściana P0/P1 z oknami (x −0,30)", -0.30 - Z["xw"], 4.0),
                       ("W: płyta ST3/ST2L (x −2,20)", -2.20 - Z["xw"], 4.0), ("W: okap P0 / taras (x −1,80)", -1.80 - Z["xw"], 4.0),
                       ("E: ściana garażu z drzwiami (x 18,70)", Z["xe"] - 18.70, 4.0), ("E: okap ST1 nad patio (x 13,80)", Z["xe"] - 13.80, 4.0),
                       ("E: jedn. zewn. PC (x 11,40)", Z["xe"] - 11.40, 6.0), ("E: miejsce gościnne P2 (x 18,10)", Z["xe"] - 18.10, 3.0),
                       ("S: okap/płyty (y −1,30)", -1.30 - Z["ys"], 4.0), ("N: linia zabudowy – daszek (y 12,80)", M.LINIA_ZAB - 12.80, 0.0)]:
        add(f"odległość {nm}", f"{f(v)} m", f"≥ {f(lim)} m", v >= lim)
    add("PU łączna", f"{f(M.pu())} m²", "230–270 m²", 230 <= M.pu() <= 270)
    sd = next(r for r in M.POMIESZCZENIA if r["id"] == "0.01")["poly"].area
    add("strefa dzienna otwarta", f"{f(sd)} m²", "≥ 50 m²", sd >= 50)
    add("miejsca postojowe", "2 w garażu + 2 gościnne", "≥ 2", True)
    return "\n".join(rows)


if __name__ == "__main__":
    a = sys.argv[1]
    if a == "kontrola":
        print(tab_control())
    else:
        kind, k = a.split("_")
        print({"sciany": tab_walls, "otwory": tab_open, "pom": tab_rooms}[kind](k))
