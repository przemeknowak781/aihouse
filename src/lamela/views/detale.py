"""Generator DETALI architektonicznych (projekt techniczny, PT) — typ widoku `detal` rejestru `sheets.VIEW_TYPES`.

Widok: ``{typ: detal, wezel: WZ-08}`` albo ``{typ: detal, rodzaj: cokol}``, podziałka 1:10 lub 1:5 (``skala``).
Geometria warstw z przegród modelu (`detale_geom.Detal.stos_v/stos_h` — grubości, materiały, kliny), kreskowania
materiałów wg PN-B-01030:2000 (aktualna) i PN-EN ISO 128-3:2023 (zastąpiła wycofane PN-ISO 128-50), opisy warstw
odnośnikami w kolumnach poza rysunkiem (od zewnątrz do wewnątrz, grubości w mm — bez kolizji z założenia układu:
kolumny poza obrysem treści, bloki opisów układane bez nakładania), wymiary [mm], rzędne, spadki, obróbki
z kapinosami, taśmy i membrany; zasada **„4 linii”** kolorami: hydroizolacja — niebieska, szczelność powietrzna —
czerwona przerywana, paroizolacja — fioletowa, izolacja cieplna — obrys pomarańczowy, z oceną „ciągłość zachowana /
uwaga” (karta mostka + ciągłość linii na rysunku); w polu opisu ψ i f_Rsi z karty mostka
(`projekt/08_obliczenia/mostki/zestawienie_mostkow.json`).

Rodzaje detali — `detale_katalog.RODZAJE` (id węzła → rodzaj: `detale_katalog.WEZEL_RODZAJ`). Raport modułu (kontrola
grubości z przegrodami modelu, kolizje opisów, ciągłość linii) — `raport_detali()`; zapisywany do pliku
`wspolne.raport_detali` konfiguracji arkuszy przy każdym wygenerowanym detalu.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, fmt, styles
from ..draft import text as T
from ..draft.core import PLine, PText, Viewport, text_items
from ..draft.elements import CutSet
from ..draft.geom import polygons_of
from .common import IR_MATS, hatch_code
from .detale_geom import CIENKA, DET_MATS, Detal
from .sheets import register_view

ROOT = Path(__file__).resolve().parents[3]
H_OPIS = 1.8          # [mm] pismo opisów warstw (PN-EN ISO 3098: 1,8)
WIERSZ = 3.1          # [mm] odstęp wierszy opisu
H_WYM = 1.8           # [mm] liczby wymiarowe detalu

# ---------------------------------------------------------------------------------------------- warstwy rysunku
KOLORY = {"H": "#1565c0", "S": "#d32f2f", "P": "#7b1fa2", "I": "#ef6c00", "W": "#455a64", "G": "#757575",
          "T_in": "#7b1fa2", "T_out": "#1565c0"}
_WARSTWY = [  # nazwa, opis, rola, rodzaj linii, ACI, kolor wydruku, z
    ("A-DET-HYDRO", "Detal — hydroizolacja / ochrona przed wodą (linia niebieska)", "gruba", "CIAGLA", 5, KOLORY["H"], 24),
    ("A-DET-SZCZEL", "Detal — szczelność powietrzna (czerwona przerywana)", "srednia", "KRESKOWA", 1, KOLORY["S"], 24),
    ("A-DET-PARO", "Detal — paroizolacja / kontrola pary (fioletowa)", "srednia", "CIAGLA", 6, KOLORY["P"], 24),
    ("A-DET-IZOL", "Detal — obrys izolacji cieplnej (pomarańczowy)", "srednia", "CIAGLA", 30, KOLORY["I"], 23),
    ("A-DET-TASMA", "Detal — taśmy uszczelniające (paroszczelne / paroprzepuszczalne)", "gruba", "CIAGLA", 6, None, 25),
    ("A-DET-MEMBRANY", "Detal — membrany wiatroizolacyjne, włókniny, bariery", "cienka", "PUNKTOWA_KROTKA", 8,
     KOLORY["W"], 23),
    ("A-DET-OBROBKI", "Detal — obróbki blacharskie, okapniki, rynny", "srednia", "CIAGLA", 7, None, 23),
    ("A-DET-PRZERWA", "Detal — linie przerwania", "cienka", "CIAGLA", 8, None, 22),
    ("A-DET-OPIS", "Detal — pole opisu (wyniki mostków, ocena 4 linii)", "cienka", "CIAGLA", 2, None, 26),
]
for _n, _o, _r, _lt, _aci, _rgb, _z in _WARSTWY:
    styles.LAYERS.setdefault(_n, styles.LayerDef(_n, _o, _r, _lt, _aci, _rgb, True, _z))
for _k, (_nm, _h, _kind, _lam) in DET_MATS.items():          # nazwy materiałów detali w legendzie kreskowań
    IR_MATS.setdefault(_k, (_nm, "#d0d0d0", _h))

# pióra [mm] (szereg ISO 128-2) i rodzaje linii 4 linii / taśm
STYL = {"H": ("A-DET-HYDRO", 0.7, "CIAGLA"), "S": ("A-DET-SZCZEL", 0.5, "KRESKOWA"),
        "P": ("A-DET-PARO", 0.5, "CIAGLA"), "W": ("A-DET-MEMBRANY", 0.35, "PUNKTOWA_KROTKA"),
        "G": ("A-DET-MEMBRANY", 0.25, "KRESKOWA_DROBNA"), "T_in": ("A-DET-TASMA", 1.0, "CIAGLA"),
        "T_out": ("A-DET-TASMA", 1.0, "KROPKOWA")}
LEGENDA_4 = [("H", "hydroizolacja / izolacja przeciwwodna i przeciwwilgociowa (ochrona przed wodą)"),
             ("S", "warstwa szczelności powietrznej (tynk wewn., płyta ŻB, OSB, membrana, taśmy)"),
             ("P", "paroizolacja / kontrola pary (folia, papa z Al, membrana sd ≥ 10 m)"),
             ("I", "izolacja cieplna — obrys ciągłej warstwy izolacji (test „ołówka”)"),
             ("T_in", "taśma paroszczelna (od wewnątrz — ciepły montaż)"),
             ("T_out", "taśma paroprzepuszczalna / uszczelnienie zewnętrzne (ciepły montaż, próg)"),
             ("W", "membrana wiatroizolacyjna paroprzepuszczalna"),
             ("G", "geowłóknina, bariera przeciwkorzenna, mata drenażowa")]

KIND_CUT = {"konstr": "konstr", "izol": "izol", "wyk": "wyk", "warstwa": "warstwa", "grunt": "grunt", "stal": "stal",
            "dzial": "dzial"}


def _hc(model, mat: str) -> str:
    if mat in DET_MATS:
        return DET_MATS[mat][1]
    return hatch_code(model, mat)


def _okno(det: Detal):
    if det.okno is None:
        return None
    return box(*det.okno)


def rysuj_elementy(vp: Viewport, det: Detal) -> dict:
    """Elementy przecięte (kreskowanie + kontury), warstwy cienkie, linie 4 linii, taśmy, obróbki, obrys izolacji.
    Zwraca {hatch_mats, izolacja (geometria), linie (rodzaj → [LineString])}."""
    m = det.model
    ok = _okno(det)
    cs = CutSet()
    hm: dict = {}
    for i, c in enumerate(det.czesci):
        g = c.poly if ok is None else c.poly.intersection(ok)
        if g.is_empty or g.area < 1e-10:
            continue
        hc = _hc(m, c.mat)
        cs.add(g, hc, KIND_CUT.get(c.kind, "warstwa"), priority=100 + i, axis=c.os, group=c.grupa or c.mat)
        hm.setdefault(hc, [])
        if c.mat not in hm[hc]:
            hm[hc].append(c.mat)
    for v in det.otwory:
        cs.cut_out(v)
    res = cs.draw(vp, merge_thin_mm=0.0)
    # obrys izolacji cieplnej (pomarańczowy) — suma elementów izolacyjnych po rozstrzygnięciu nakładania
    iz = [g for it, g in res if it.kind == "izol"]
    izol = unary_union(iz) if iz else Polygon()
    if not izol.is_empty:
        inset = izol.buffer(-0.45 * vp.k, join_style=2)
        for pg in polygons_of(inset):
            vp.geom(pg, "A-DET-IZOL", pen=0.5, color=KOLORY["I"], z=23.5)
    linie: dict = {}
    def _lin(rodz, P, ly=None):
        if ok is not None:
            g = LineString(P).intersection(ok)
            parts = [np.asarray(a.coords) for a in getattr(g, "geoms", [g]) if not a.is_empty and a.length > 0]
        else:
            parts = [np.asarray(P)]
        ly_, pen, lt = STYL[rodz]
        for a in parts:
            vp.polyline(a, ly or ly_, pen=pen, lt=lt, color=KOLORY.get(rodz), z=24.5 if rodz in "HSP" else 24.0)
            linie.setdefault(rodz, []).append(LineString(a))
    for P, mat, rodz, _op in det.cienkie:
        _lin(rodz if rodz in STYL else "G", P)
    for rodz, P, _op in det.linie:
        _lin(rodz, P)
    for P, _op in det.obrobki:
        vp.polyline(P, "A-DET-OBROBKI", pen=0.5, color="#000000", z=24.2)
    for p1, p2 in det.przerwy:
        linia_przerwania(vp, p1, p2)
    return {"hatch_mats": hm, "izolacja": izol, "linie": linie}


def linia_przerwania(vp: Viewport, p1, p2, amp_mm: float = 2.0):
    """Linia przerwania (cienka z zygzakiem w środku, PN-EN ISO 128-2 — linia 01.1 z zygzakiem)."""
    A, B = np.asarray(p1, float), np.asarray(p2, float)
    d = B - A
    L = float(np.linalg.norm(d))
    if L <= 0:
        return
    u = d / L
    n = np.array([-u[1], u[0]])
    k = vp.k
    e = 2.0 * k
    M = (A + B) / 2
    a = amp_mm * k
    pts = [A - u * e, M - u * a, M - u * a * 0.3 + n * a, M + u * a * 0.3 - n * a, M + u * a, B + u * e]
    vp.polyline(pts, "A-DET-PRZERWA", pen=0.25, color="#000000", z=24.0)


def rysuj_adnotacje(vp: Viewport, det: Detal):
    """Wymiary [mm], rzędne, spadki, znaki (poziom wody, strzałki)."""
    for pts, at, kier, labels in det.wymiary:
        dims.dim_chain(vp, pts, at, kier, unit_="mm", h=H_WYM, labels=labels)
    for pt, z, kind, strona, tekst in det.rzedne:
        dims.level_section(vp, pt, det.z0 + z, kind=kind, side=strona, text=tekst, h=H_WYM)
    for a, b, pct, tekst in det.spadki:
        dims.slope(vp, a, b, pct, text=tekst, h=H_WYM)
    for rodz, d in det.znaki:
        if rodz == "woda":           # poziom wody / nawierzchni — trójkąt odwrócony z kreskami (PN-B-01025)
            P = np.asarray(d["pt"], float)
            k = vp.k
            s = 1.8 * k
            vp.polygon([P, P + np.array([-s, s * 1.2]), P + np.array([s, s * 1.2])], "A-SYMBOLE", pen=0.25,
                       color=KOLORY["H"])
            for j, w in enumerate((1.0, 0.6)):
                y = P[1] - (0.9 + 0.8 * j) * k
                vp.line((P[0] - s * w, y), (P[0] + s * w, y), "A-SYMBOLE", pen=0.25, color=KOLORY["H"])
            if d.get("tekst"):
                vp.text(P + np.array([2.6 * k, 0.4 * k]), d["tekst"], H_WYM, layer="A-SYMBOLE", color=KOLORY["H"],
                        mask=0.3)
        elif rodz == "kontur":
            vp.polyline(d["pts"], "A-WIDOK", closed=d.get("zamkniety", True), pen=d.get("pen", 0.35), lt=d.get("lt"))
        elif rodz == "strzalka":      # kierunek spływu / przepływu
            dims.slope(vp, d["a"], d["b"], None, text=d.get("tekst", ""), h=H_WYM)


# ---------------------------------------------------------------------------------------------- opisy (odnośniki)
def _zawin(s: str, w_mm: float, h: float = H_OPIS) -> list[str]:
    if T.width(s, h) <= w_mm:
        return [s]
    out, cur = [], ""
    for word in s.split(" "):
        t = (cur + " " + word).strip()
        if T.width(t, h) > w_mm and cur:
            out.append(cur)
            cur = word
        else:
            cur = t
    if cur:
        out.append(cur)
    return out


def rysuj_opisy(vp: Viewport, det: Detal, bbox, szer_mm: float = 62.0) -> list:
    """Odnośniki opisów w kolumnach poza obrysem treści `bbox` (x0, y0, x1, y1 [m]). Bloki układane od góry według
    rzędnej wyjścia odnośnika, bez nakładania (odstęp ≥ 1,2 mm); kolano odnośnika na krawędzi treści + 3 mm.
    Zwraca [(tekst, prostokąt napisu)] do kontroli kolizji."""
    k = vp.k
    x0, y0, x1, y1 = bbox
    boxes = []
    for strona in ("R", "L"):
        its = [o for o in det.opisy if o.strona == strona]
        if not its:
            continue
        bloki = []
        for o in its:
            wiersze = []
            for t in o.teksty:
                wiersze += [(t, j) for j, t in enumerate(_zawin(t, szer_mm))]
            y_w = (o.wyjscie[1] if o.wyjscie else o.pts[0][1])
            x_w = (o.wyjscie[0] if o.wyjscie else o.pts[0][0])
            n = len(wiersze) + (1 if o.tytul else 0)
            bloki.append(dict(o=o, wiersze=wiersze, y=y_w, x=x_w, h=n * WIERSZ * k))
        sgx = 1.0 if strona == "R" else -1.0
        bloki.sort(key=lambda b: (-round(b["y"] / (2.2 * k)), sgx * b["x"]))
        # kolana odnośników rozsunięte (≥ 2,2 mm) w tej samej kolejności co wyjścia — brak nakładania poziomych
        # odcinków odnośników o bliskich rzędnych
        yk = []
        for b in bloki:
            y = b["y"]
            if yk and y > yk[-1] - 2.2 * k:
                y = yk[-1] - 2.2 * k
            yk.append(y)
        if yk:
            sr = float(np.mean([b["y"] - y for b, y in zip(bloki, yk)]))
            yk = [y + max(0.0, sr) for y in yk]
            for i in range(1, len(yk)):
                yk[i] = min(yk[i], yk[i - 1] - 2.2 * k)
        for b, y in zip(bloki, yk):
            b["yk"] = y
        # układ 1D: góra bloku = y wyjścia + pół wiersza, bez nakładania — przesuwanie w dół, potem korekta w górę
        gap = 1.2 * k
        tops = []
        for b in bloki:
            t = b["yk"] + 0.5 * WIERSZ * k
            if tops and t > tops[-1] - bloki[len(tops) - 1]["h"] - gap:
                t = tops[-1] - bloki[len(tops) - 1]["h"] - gap
            tops.append(t)
        # przesunięcie całej kolumny w górę, gdy średnio poniżej wyjść (równoważenie)
        sr = float(np.mean([tops[i] - (b["yk"] + 0.5 * WIERSZ * k) for i, b in enumerate(bloki)]))
        if sr < 0:
            lift = min(-sr, max(0.0, (y1 + 4 * k) - tops[0]))
            tops = [t + lift for t in tops]
        x_k = (x1 + 3.0 * k) if strona == "R" else (x0 - 3.0 * k)
        x_c = (x1 + 9.0 * k) if strona == "R" else (x0 - 9.0 * k)
        sg = 1.0 if strona == "R" else -1.0
        for b, top in zip(bloki, tops):
            o = b["o"]
            P = [np.asarray(p, float) for p in o.pts]
            with vp.on("A-OPISY"):
                if len(P) > 1:
                    vp.polyline(P, pen=0.18)
                for p in P:
                    vp.dot(p, 0.7, "A-OPISY")
                start = P[0]
                path = [start]
                if o.wyjscie is not None:
                    path.append(np.asarray(o.wyjscie, float))
                y_e = path[-1][1]
                if abs(b["yk"] - y_e) > 1e-9:          # kolano rozsunięte — odcinek do kolana ukośny
                    path.append(np.array([x_k - sg * 2.0 * k, y_e]))
                path.append(np.array([x_k, b["yk"]]))
                y_txt = top - (1.0 + (1 if o.tytul else 0)) * WIERSZ * k + 0.9 * k
                path.append(np.array([x_c - sg * 1.5 * k, y_txt + 0.5 * H_OPIS * k]))
                path.append(np.array([x_c, y_txt + 0.5 * H_OPIS * k]))
                vp.polyline(path, pen=0.18)
                y = top - WIERSZ * k + 0.9 * k
                if o.tytul:
                    p = vp.text((x_c + sg * 1.0 * k, y), o.tytul, H_OPIS, ha="left" if sg > 0 else "right",
                                style="bold")
                    boxes.append((o.tytul, Polygon(text_items(p, k)[1])))
                    y -= WIERSZ * k
                for t, j in b["wiersze"]:
                    xt = x_c + sg * (1.0 + (2.0 if j else 0.0)) * k
                    p = vp.text((xt, y), t, H_OPIS, ha="left" if sg > 0 else "right")
                    boxes.append((t, Polygon(text_items(p, k)[1])))
                    y -= WIERSZ * k
    return boxes


def rysuj_pole_opisu(vp: Viewport, det: Detal, bbox, wiersze: list[tuple[str, str | None]]):
    """Pole opisu pod rysunkiem: wyniki mostka (ψ, f_Rsi) i ocena 4 linii (kolor statusu)."""
    k = vp.k
    x0, y0 = bbox[0], bbox[1] - 7.0 * k
    for j, (t, kol) in enumerate(wiersze):
        vp.text((x0, y0 - j * 3.2 * k), t, H_OPIS, layer="A-DET-OPIS", color=kol, style="bold" if j == 0 else "normal")


# ---------------------------------------------------------------------------------------------- wyniki i ocena
def wczytaj_wyniki(ctx) -> dict:
    """Wiersze węzłów z `zestawienie_mostkow.json` (tools/mostki_budynku.py) — {id: wiersz}."""
    p = Path(str((ctx.cfg or {}).get("wyniki_mostkow") or "projekt/08_obliczenia/mostki/zestawienie_mostkow.json"))
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except Exception:          # pragma: no cover
        return {}
    return {r["id"]: r for r in d.get("wezly") or []} | {"_chi": {c["id"]: c for c in d.get("chi") or []}}


def _skladowe(linie: list, tol: float) -> int:
    """Liczba spójnych składowych zbioru odcinków (odległość ≤ tol = połączone)."""
    n = len(linie)
    if n == 0:
        return 0
    par = list(range(n))

    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i
    for i in range(n):
        for j in range(i + 1, n):
            if linie[i].distance(linie[j]) <= tol:
                par[f(i)] = f(j)
    return len({f(i) for i in range(n)})


def ocena_linii(det: Detal, info: dict, wyniki: dict, k: float) -> dict:
    """Ocena ciągłości 4 linii detalu: status z karty mostka (zestawienie 4 linii węzłów) + ciągłość linii narysowanych
    (liczba składowych; izolacja — liczba składowych obrysu). {H|S|P|I: (status, opis)}."""
    out = {}
    wz = [wyniki[w] for w in det.wezly if w in wyniki]
    for L in "HSPI":
        st, op = "OK", []
        for r in wz:
            s4, t4 = (r.get("linie4") or {}).get(L, ("OK", ""))
            if s4 != "OK":
                st = "UWAGA" if st == "OK" else st
                op.append(f"{r['id']}: {t4[:110]}")
        if L == "I":
            n = len(polygons_of(info["izolacja"])) if not info["izolacja"].is_empty else 0
            if n > 1:
                op.append(f"obrys izolacji: {n} części (w tym warstwy dodatkowe, np. izolacja podłogi)")
        else:
            ls = list(info["linie"].get(L, [])) + [LineString(P) for r_, P in det.polaczenia if r_ == L]
            # taśmy (T_in — paroszczelna dla S/P, T_out — paroprzepuszczalna dla H) łączą linię z ramą; taśma, która
            # nie styka się z linią (np. nadproże osłonięte okapem), jest osobnym elementem — nie przerwą linii
            tasmy = list(info["linie"].get("T_in" if L in "SP" else "T_out", []))
            dod = True
            while dod and ls:
                dod = False
                for t_ in list(tasmy):
                    if any(t_.distance(x) <= 1.5 * k for x in ls):
                        ls.append(t_)
                        tasmy.remove(t_)
                        dod = True
            n = _skladowe(ls, 1.5 * k) if info["linie"].get(L) else 0
            if n > 1:
                op.append(f"linia na rysunku — {n} odcinki (przerwa?)")
                st = "UWAGA" if st == "OK" else st
            if n == 0 and not wz:
                op.append("brak w detalu")
        out[L] = (st, "; ".join(op) if op else "ciągłość zachowana")
    return out


def wiersze_opisu(det: Detal, wyniki: dict, oc: dict) -> list[tuple[str, str | None]]:
    out = []
    for w in det.wezly:
        r = wyniki.get(w)
        if r is None:
            ch = (wyniki.get("_chi") or {}).get(w)
            if ch:
                out.append((f"{w} — mostek punktowy: χ = {fmt.num(ch['chi'], 3)} W/K × {int(ch['n'])} szt. = "
                            f"{fmt.num(ch['chi'] * ch['n'], 2)} W/K ({ch['zrodlo'][:60]})", None))
            continue
        fr = r.get("f_rsi")
        out.append((f"{w}: ψ_e = {fmt.num(r['psi_e'], 3)}, ψ_oi = {fmt.num(r['psi_oi'], 3)} W/(m·K); "
                    f"f_Rsi = {fmt.num(fr, 3)} {'≥' if (fr or 0) >= 0.72 else '<'} 0,72 — {r.get('ocena')}", None))
    if not out:
        out.append(("Węzeł bez karty mostka 2D (mostek punktowy / element systemowy) — patrz uwagi", None))
    sym = {"OK": "OK", "UWAGA": "uwaga", "BRAK": "BRAK"}
    txt = ", ".join(f"{L} {sym[oc[L][0]]}" for L in "HSPI")
    zle = [f"{L}: {oc[L][1]}" for L in "HSPI" if oc[L][0] != "OK"]
    out.append((f"4 linie: {txt} — " + ("ciągłość zachowana" if not zle else "uwaga"),
                "#1a7f37" if not zle else "#b7791f"))
    for z in zle:
        out.append((_skroc(z, 165), "#b7791f"))
    return out


def _skroc(t: str, n: int) -> str:
    """Skrót tekstu do n znaków na granicy słowa (z wielokropkiem)."""
    if len(t) <= n:
        return t
    c = t[:n - 1]
    i = max(c.rfind(" "), c.rfind(";"))
    return (c[:i] if i > n // 2 else c).rstrip(" ,;(") + "…"


def kontrola_grubosci(det: Detal) -> list[tuple]:
    """[(kod, idx, mat, d_model, d_rys, status)] — zgodność grubości warstw narysowanych z przegrodami modelu."""
    out = []
    for kod, idx, mat, d_m, d_r, klin in det.kontrola:
        if klin:
            ok = float(klin["d_min"]) - 5e-4 <= d_r <= float(klin["d_max"]) + 5e-4
        else:
            ok = abs(d_m - d_r) <= 5e-4
        out.append((kod, idx, mat, d_m, d_r, "OK" if ok else "RÓŻNICA"))
    return out


def kolizje(boxes: list, vp: Viewport) -> dict:
    """Kolizje napisów: napis–napis dla WSZYSTKICH napisów rzutni (opisy, rzędne, wymiary, pole opisu; pole
    wspólne > 0,05 mm²) i napis opisu–linie rysunku (prymitywy poza warstwą opisów)."""
    k2 = vp.k * vp.k
    wszystkie = [Polygon(text_items(p, vp.k)[1]) for p in vp.prims if isinstance(p, PText)]
    tt = 0
    for i in range(len(wszystkie)):
        for j in range(i + 1, len(wszystkie)):
            if wszystkie[i].intersects(wszystkie[j]) and wszystkie[i].intersection(wszystkie[j]).area / k2 > 0.05:
                tt += 1
    tl = 0
    linie = [LineString(p.pts) for p in vp.prims if isinstance(p, PLine) and p.layer not in ("A-OPISY",)
             and len(p.pts) >= 2]
    for _t, b in boxes:
        bb = b.buffer(-0.2 * vp.k)
        if any(bb.intersects(l_) for l_ in linie):
            tl += 1
    return {"napis_napis": tt, "napis_linia": tl, "napisy": len(boxes)}


# ---------------------------------------------------------------------------------------------- widok arkusza
@dataclass
class DetalResult:
    det: Detal
    hatch_mats: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)
    column_blocks: list = field(default_factory=list)
    units_note: str | None = None
    raport: dict = field(default_factory=dict)
    rooms: list = field(default_factory=list)
    north: bool = False


RAPORT: dict[str, dict] = {}
UWAGI_OGOLNE = [
    "Kreskowania materiałów wg PN-B-01030:2000 (aktualna) i PN-EN ISO 128-3:2023-02 (zastąpiła wycofane PN-ISO "
    "128-50:2006); oznaczenia spoza normy — w legendzie arkusza.",
    "Opisy warstw od zewnątrz do wewnątrz (kolejność kropek na linii odnośnika = kolejność wierszy), grubości w mm "
    "wg przegród modelu (kontrola zgodności — raport modułu detali).",
    "Zasada „4 linii” (brief §9.1): hydroizolacja — niebieska, szczelność powietrzna — czerwona przerywana, "
    "paroizolacja — fioletowa, izolacja cieplna — obrys pomarańczowy; każda linia ciągła wokół kubatury ogrzewanej.",
    "Wywinięcia hydroizolacji ≥ 15 cm ponad warstwę wierzchnią (żwir, substrat, nawierzchnia) — Wytyczne DAFA dla "
    "dachów płaskich; DIN 18531 (pomocniczo); PN-EN 1991 wysokości wywinięć nie określa. Cokół: uszczelnienie "
    "≥ 30 cm nad terenem (brief §9.4; DIN 18533-1 — pomocniczo) albo odwodnienie liniowe przy drzwiach bezprogowych.",
    "Wyroby (łączniki termoizolacyjne, taśmy, profile progowe, wpusty, konsole) — dane przykładowe „lub równoważne”; "
    "parametry (ETA/DWU) do potwierdzenia przed realizacją.",
]


def _blok_legenda(sh, x, y, w):
    if getattr(sh, "_det_legenda", False):
        return y
    sh._det_legenda = True
    with sh.on("R-LEGENDA"):
        sh.text((x, y - 3.5), "ZASADA „4 LINII” I OZNACZENIA DETALI", 3.5, style="bold")
        yy = y - 9.0
        for kod, txt in LEGENDA_4:
            if kod == "I":
                sh.rect(x + 1, yy - 0.6, x + 13, yy + 2.2, "R-LEGENDA", pen=0.5, color=KOLORY["I"])
            else:
                ly, pen, lt = STYL[kod]
                sh.line((x + 1, yy + 0.9), (x + 13, yy + 0.9), "R-LEGENDA", pen=pen, lt=lt, color=KOLORY.get(kod))
            ls = _zawin(txt, w - 18.0)
            for j, s in enumerate(ls):
                sh.text((x + 16, yy - j * 2.7), s, 1.8)
            yy -= 2.7 * len(ls) + 1.6
        sh.line((x + 1, yy + 0.9), (x + 13, yy + 0.9), "R-LEGENDA", pen=0.5, color="#000000")
        sh.text((x + 16, yy), "obróbka blacharska z okapnikiem (kapinosem), rynna ukryta", 1.8)
        yy -= 4.3
    return yy + 1.0


def _blok_wyniki(det_id: str, wiersze: list):
    def fn(sh, x, y, w):
        yy = y
        if not getattr(sh, "_det_wyniki", False):
            sh._det_wyniki = True
            sh.text((x, yy - 3.5), "WYNIKI MOSTKÓW (PN-EN ISO 10211) I OCENA 4 LINII", 3.5, layer="R-LEGENDA",
                    style="bold")
            yy -= 8.0
        ls = _zawin(f"{det_id}: " + wiersze[0][0], w - 2.0)
        for t, kol in [(s, None) for s in ls] + [(s, kol) for t_, kol in wiersze[1:] for s in _zawin(t_, w - 6.0)]:
            sh.text((x + (0 if t in ls else 4.0), yy), t, 1.8, layer="R-LEGENDA", color=kol)
            yy -= 2.7
        return yy - 1.0
    return fn


def widok_detalu(ctx, spec: dict, scale: float, opts: dict):
    from . import detale_katalog as DK
    rodzaj = spec.get("rodzaj") or DK.WEZEL_RODZAJ.get(str(spec.get("wezel")))
    if rodzaj not in DK.RODZAJE:
        raise KeyError(f"detal: nieznany rodzaj/węzeł „{spec.get('rodzaj') or spec.get('wezel')}” "
                       f"(rodzaje: {', '.join(DK.RODZAJE)})")
    det: Detal = DK.RODZAJE[rodzaj](ctx.model, dict(opts, **{k: v for k, v in spec.items() if k in ("id_detalu",)}))
    if spec.get("id_detalu"):
        det.id = str(spec["id_detalu"])
    sk = int(spec.get("skala") or det.skala or scale)
    title = spec.get("tytul_widoku") or f"DETAL {det.id} — {det.tytul.upper()}"
    vp = Viewport(sk, title)
    info = rysuj_elementy(vp, det)
    rysuj_adnotacje(vp, det)
    bbox = vp.extents()
    boxes = rysuj_opisy(vp, det, bbox)
    wyniki = wczytaj_wyniki(ctx)
    oc = ocena_linii(det, info, wyniki, vp.k)
    wiersze = wiersze_opisu(det, wyniki, oc)
    e = vp.extents()
    rysuj_pole_opisu(vp, det, (bbox[0], min(bbox[1], e[1]), bbox[2], bbox[3]), wiersze)
    kg = kontrola_grubosci(det)
    kol = kolizje(boxes, vp)
    res = DetalResult(det, info["hatch_mats"])
    res.units_note = (f"Wymiary w mm, rzędne w m względem ±0,000 = {fmt.level_abs(ctx.model.zero_abs)} m n.p.m. "
                      "(PL-EVRF2007-NH).")
    n_ok = sum(1 for r in kg if r[5] == "OK")
    res.notes = list(UWAGI_OGOLNE) + [f"Detal {det.id}: {u}" for u in det.uwagi]
    res.column_blocks = [("legenda4", _blok_legenda), (f"wyniki-{det.id}", _blok_wyniki(det.id, wiersze))]
    res.raport = dict(id=det.id, tytul=det.tytul, skala=sk, wezly=list(det.wezly), grubosci=kg,
                      grubosci_ok=f"{n_ok}/{len(kg)}", kolizje=kol, linie4={L: oc[L] for L in "HSPI"},
                      wyniki=[w for w, _k in wiersze])
    RAPORT[det.id] = res.raport
    _zapisz_raport(ctx)
    return vp, res, title


def _zapisz_raport(ctx):
    p = (ctx.cfg or {}).get("raport_detali")
    if not p:
        return
    p = Path(str(p))
    if not p.is_absolute():
        p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(raport_detali(), encoding="utf-8")


def raport_detali(raport: dict | None = None) -> str:
    R = raport if raport is not None else RAPORT
    L = ["# Raport modułu detali (lamela.views.detale)", "",
         "Kontrola automatyczna każdego detalu: zgodność grubości warstw narysowanych z przegrodami `model/budynek.yaml` "
         "(tolerancja 0,5 mm; warstwy klinowe — w zakresie d_min…d_max), kolizje opisów (napis–napis, napis–linia "
         "rysunku), ciągłość 4 linii (karta mostka + liczba odcinków linii na rysunku).", "",
         "| detal | tytuł | skala | węzły | grubości zgodne | kolizje napis–napis | napisy na liniach | H | S | P | I |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    sym = {"OK": "✓", "UWAGA": "!", "BRAK": "✗"}
    for d in R.values():
        k = d["kolizje"]
        L.append(f"| {d['id']} | {d['tytul']} | 1:{d['skala']} | {', '.join(d['wezly']) or '—'} | {d['grubosci_ok']} | "
                 f"{k['napis_napis']} | {k['napis_linia']} | " + " | ".join(sym[d['linie4'][x][0]] for x in "HSPI")
                 + " |")
    L += ["", "## Szczegóły — grubości warstw (model ↔ rysunek)", ""]
    for d in R.values():
        zle = [r for r in d["grubosci"] if r[5] != "OK"]
        L.append(f"* **{d['id']}** — {d['grubosci_ok']} warstw zgodnych" + (": " + "; ".join(
            f"{r[0]}[{r[1]}] {r[2]} model {r[3] * 1000:.1f} mm ≠ rysunek {r[4] * 1000:.1f} mm" for r in zle)
                                                                         if zle else "") + "; 4 linie: " + "; ".join(
            f"{x} — {d['linie4'][x][1]}" for x in "HSPI"))
    return "\n".join(L) + "\n"


register_view("detal", widok_detalu, rodzaj="detal")
