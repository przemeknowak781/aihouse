# -*- coding: utf-8 -*-
"""Obliczenia kontrolne wariantu W2 (powierzchnie, 1/8, schody, odleglosci, wskazniki MPZP, wysokosc)."""
import math
import numpy as np
from shapely.geometry import box, Point
from shapely.ops import unary_union
import model_w2 as M

Z = M.DZ
P = M.POZ


def fmt(v, nd=2):
    return f"{v:.{nd}f}".replace(".", ",")


def pu():
    per = {}
    for k in ("P0", "P1", "P2"):
        per[k] = round(sum(M.room_area(r) for r in M.POMIESZCZENIA if r["kond"] == k and r["kat"] != "garaż"), 2)
    gar = M.room_area(next(r for r in M.POMIESZCZENIA if r["id"] == "0.13"))
    return per, round(sum(per.values()), 2), gar


def okna():
    rows = []
    for rid, ids in M.OKNA_POM.items():
        r = next(x for x in M.POMIESZCZENIA if x["id"] == rid)
        A = M.room_area(r)
        Ao = sum(M.okno_w_swietle(M.otwor(i)) for i in ids)
        rows.append(dict(id=rid, nazwa=r["nazwa"], A=A, okna=", ".join(ids), Ao=round(Ao, 2), wym=round(A / 8, 2), stos=Ao / A))
    return rows


def schody():
    S = M.SCHODY
    h, s = S["h"], S["s"]
    alfa = math.atan(h / s)
    t_v = S["gr_plyty_biegu"] / math.cos(alfa)
    przeswit = M.POZ["wys_kond"] - h - t_v        # pion. od linii nosków biegu dolnego do spodu biegu gornego
    return dict(h=h, s=s, n=S["n_podn"], bieg=S["stopni_w_biegu"], dl_biegu=round((S["stopni_w_biegu"] - 1) * s, 2),
                szer=S["szer"], spocz_gl=round(S["spocznik"]["y"][1] - S["spocznik"]["y"][0], 3),
                spocz_szer=round(S["spocznik"]["x"][1] - S["spocznik"]["x"][0], 3), dwa_h_s=round(2 * h + s, 3),
                kat=round(math.degrees(alfa), 1), przeswit=round(przeswit, 2))


def odleglosci():
    xw, xe, ys, yn = Z["xw"], Z["xe"], Z["ys"], Z["yn"]
    by = {p["id"]: p["poly"] for p in M.PLYTY}
    rows = [
        ("W", "ściana zach. P0/P1 (lico ocieplenia, okna)", -0.30 - xw, 4.0),
        ("W", "ściana zach. P2 na wsporniku (okno)", -1.30 - xw, 4.0),
        ("W", "okap ST1 zach. (1,50 m)", by["E-okap-W"].bounds[0] - xw, 1.5),
        ("W", "płyty ST2/ST3 (krawędź zach.)", by["ST3-okap"].bounds[0] - xw, 1.5),
        ("W", "taras ogrodowy", M.TEREN_ELEM["taras"]["poly"].bounds[0] - xw, 1.5),
        ("E", "ściana wsch. garażu (drzwi boczne)", xe - 18.70, 4.0),
        ("E", "ściana wsch. brył B i A (okna)", xe - 12.30, 4.0),
        ("E", "rama C / okapy (krawędź wsch.)", xe - 12.60, 1.5),
        ("E", "jednostka zewn. pompy ciepła", xe - M.TEREN_ELEM["pc_plyta"]["poly"].bounds[2], 3.0),
        ("E", "miejsce gościnne P2 (niezadaszone, WT §19 ust. 2)", xe - M.MIEJSCA_GOSC[1].bounds[2], 3.0),
        ("W", "miejsce gościnne P1 (niezadaszone)", M.MIEJSCA_GOSC[0].bounds[0] - xw, 3.0),
        ("N", "ściana pn. garażu (brama) — do linii rozgraniczającej drogi", yn - 9.30, 6.0),
        ("N", "ściana pn. części mieszkalnej (drzwi wejściowe)", yn - 8.70, 6.0),
        ("N", "daszek nad wejściem (najbardziej wysunięty element)", yn - by["daszek"].bounds[3], 6.0),
        ("S", "ściany pd. (przeszklenie E)", -0.30 - ys, 4.0),
        ("S", "okapy pd. (ST1/ST2/ST3, rama C)", -1.30 - ys, 1.5),
        ("S", "taras", M.TEREN_ELEM["taras"]["poly"].bounds[1] - ys, 1.5),
    ]
    return [dict(str=a, el=b, d=round(c, 2), min=d) for a, b, c, d in rows]


def wysokosc():
    walls = unary_union([M.outline("P0"), M.outline("P1"), M.outline("P2")])
    pts = [walls.exterior.interpolate(t, normalized=True) for t in np.linspace(0, 1, 400)]
    zs = [M.teren_wzgl(p.x, p.y) for p in pts]
    zmin, zmax = min(zs), max(zs)
    zsr = (zmin + zmax) / 2
    # najnizsze wejscie na P0: drzwi HS (pd.), wejsciowe (pn.), gospodarcze (pd.), boczne garazu (wsch.)
    wejscia = {"drzwi HS salonu (pd.)": (0.30 + 2.28 * 1.5, -0.30), "drzwi HS jadalni (pd.)": (0.30 + 2.28 * 3.5, -0.30),
               "drzwi wejściowe (pn.)": (10.75, 8.70), "drzwi gospodarcze (pd.)": (12.70, -0.30), "drzwi boczne garażu (wsch.)": (18.70, 5.45)}
    zw = {k: M.teren_wzgl(*v) for k, v in wejscia.items()}
    kmin = min(zw, key=zw.get)
    top_WT = P["dach_P2_warstwy"]
    top = P["attyka_P2"]
    return dict(zmin=zmin, zmax=zmax, zsr=zsr, H_mpzp=top - zsr, wejscie=kmin, z_wej=zw[kmin], H_WT=top_WT - zw[kmin],
                top=top, top_WT=top_WT, zw=zw)


def rozpietosci():
    return [
        ("ST1 (nad P0), 20 cm", "N–S, ciągła 2-przęsłowa: oś 1 (belka B1) – oś 3 – oś 4", "4,80 / 3,60", "okap pd. 1,00; zach. 1,50; daszek pn. 1,30"),
        ("ST1-G (nad garażem i strefą gosp.), 24 cm", "E–W: oś E – oś F", "6,40", "attyka +3,85; dach zielony ekstensywny"),
        ("ST2 (nad P1), 20 cm", "N–S: oś 1 (belka B2 / ściana) – oś 3 – oś 4", "4,80 / 3,60", "okap pd. 1,00; zach. 2,40 od osi A (patrz wspornik A)"),
        ("ST3 (stropodach P2), 22 cm", "N–S: oś 1 – oś 3; nadbudowa: oś 3 – oś 4", "4,80 / 3,60", "okap pd. 1,00; zach. 1,10 od lica A; wsch. 0,30"),
        ("Płyty spocznikowe / biegi, 18 cm", "między ścianami C, D i ścianką środkową", "2,12 / 2,24", "oparte na ścianach klatki"),
    ]


if __name__ == "__main__":
    print(pu())
    for r in okna():
        print(r)
    print(schody())
    for r in odleglosci():
        print(r)
    print(wysokosc())
