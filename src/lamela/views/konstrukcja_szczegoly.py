"""Przekroje i szczegóły konstrukcyjne 1:20–1:10 (typ widoku ``k_przekroj`` — rejestracja w ``konstrukcja``).

Szczegóły (``detal``): ``zebro`` (przekrój żebra płyty fundamentowej — ``przekroj: "1"|"2"`` z rzutu fundamentów albo
``element: ZF…``), ``stopa`` (pogrubienie płyty pod słupem), ``wspornik`` (węzeł płyty wspornikowej z łącznikiem
termoizolacyjnym — ``element: PL-…``), ``wieniec`` (wieniec ściany zewnętrznej pod krawędzią stropu — ``poziom``),
``oparcie`` (strop ciągły nad ścianą wewnętrzną z muru silikatowego — ``poziom``).

Układ lokalny szczegółu: oś x — normalna do linii elementu (żebro, ściana, linia zamocowania wspornika) skierowana
na zewnątrz / w stronę wspornika, x = 0 w osi elementu; oś z — rzędna bezwzględna modelu [m]. Warstwy, grubości,
rzędne i materiały — z modelu; pręty (φ, rozstaw, liczba, numer pozycji) — z generatora zbrojenia (obliczenia).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

from ..draft import dims, elements as E, fmt, hatch as H, symbols as S
from ..draft.core import Viewport
from . import konstrukcja_dane as KD
from .common import Placer, clean, cut_kind, hatch_code, klasa_mat, material_name

L_ZBR = "K-ZBROJENIE"
L_OPI = "K-ZBROJENIE-OPIS"
L_OPS = "A-OPISY"
KOL_UZ = "#b0006a"


@dataclass
class Rama:
    """Układ lokalny szczegółu: punkt Q (x = 0), normalna n (kierunek +x)."""
    Q: np.ndarray
    n: np.ndarray

    def x(self, p) -> float:
        return float((np.asarray(p, float) - self.Q) @ self.n)


def warstwy_sciany(w, R: Rama) -> list:
    """Warstwy ściany w układzie lokalnym: [(x0, x1, kod materiału, konstrukcyjna, klasa)] (x rośnie wzdłuż R.n)."""
    s = float(w.n @ R.n)
    x_os = R.x(w.p1) if abs(float(w.u @ R.n)) < 1e-6 else R.x(w.pt(w.st(R.Q)[0], 0.0))
    out = []
    for ly in w.warstwy:
        a, b = sorted((x_os + ly.t0 * s, x_os + ly.t1 * s))
        out.append((a, b, ly.mat, ly.konstrukcyjna, ly.klasa))
    return out


def dodaj_warstwy_pionowe(cs, model, warstwy, z0: float, z1: float, typ: str = "sciana_zewn"):
    for a, b, mat, konstr, klasa in warstwy:
        hc = hatch_code(model, mat)
        cs.add(box(a, z0, b, z1), hc, cut_kind(hc, klasa_mat(model, mat), konstr, typ))


def dodaj_warstwy_poziome(cs, model, przegroda, x0: float, x1: float, z_top_konstr: float, gora: bool = True,
                          pomin_konstr: bool = True) -> list:
    """Warstwy przegrody poziomej nad (gora=True) lub pod warstwą konstrukcyjną; zwraca [(z0, z1, mat)]."""
    out = []
    if przegroda is None:
        return out
    ws = przegroda.warstwy
    k = przegroda.idx_konstr
    if gora:
        z = z_top_konstr
        for w in reversed(ws[:k]):
            out.append((z, z + w.d, w.mat))
            z += w.d
    else:
        z = z_top_konstr
        for w in ws[k + 1:]:
            out.append((z - w.d, z, w.mat))
            z -= w.d
    for z0, z1, mat in out:
        if z1 - z0 < 1e-5:
            continue
        hc = hatch_code(model, mat)
        cs.add(box(x0, z0, x1, z1), hc, cut_kind(hc, klasa_mat(model, mat)))
    return out


# ------------------------------------------------------------------------------------------------ zbrojenie
def pret_kropka(vp, x, z, fi):
    """Pręt prostopadły do płaszczyzny rysunku — kółko zaczernione średnicy φ (min. 0,9 mm na papierze)."""
    r = max(fi / 2000.0, 0.45 * vp.k)
    vp.fill(Point(x, z).buffer(r, 16), L_ZBR, "#000000", z=30)


def pret_linia(vp, pts, pen=0.5):
    vp.polyline(pts, L_ZBR, pen=pen, z=30)


def strzemie(vp, x0, z0, x1, z1, fi):
    """Strzemię zamknięte (oś pręta) z hakami 135° w narożu górnym lewym."""
    vp.rect(x0, z0, x1, z1, L_ZBR, pen=0.35, z=30)
    d = max(0.04, 3 * vp.k)
    vp.line((x0, z1), (x0 + d, z1 - d), L_ZBR, pen=0.35, z=30)
    vp.line((x0, z1 - 0.004), (x0 + d * 0.9, z1 - d * 1.1), L_ZBR, pen=0.35, z=30)


def rzad_kropek(vp, x0, x1, z, fi, s_mm):
    """Pręty rozdzielcze / siatki prostopadłe do rysunku co s w przedziale [x0, x1]."""
    n = max(int(math.floor((x1 - x0) / (s_mm / 1000.0))), 0) + 1
    if n <= 1:
        pret_kropka(vp, (x0 + x1) / 2, z, fi)
        return
    dx = (x1 - x0) / (n - 1)
    for i in range(n):
        pret_kropka(vp, x0 + i * dx, z, fi)


def opis(vp, placer: Placer, pt, tekst: str, nr: int | None = None, kier: str = "prawo", dz_mm: float = 8.0,
         h: float = 2.5, ts=None):
    """Odnośnik (kropka na elemencie) + półka z opisem; numer pozycji pręta w okręgu przed tekstem."""
    from .konstrukcja import _nr_poz
    from ..draft.text import width as tw
    k = vp.k
    P = np.asarray(pt, float)
    wt = tw(tekst, h) + (7.0 if nr is not None else 0.0)
    cands = []
    for dz in (dz_mm, -dz_mm, 1.5 * dz_mm, -1.5 * dz_mm, 2.2 * dz_mm, -2.2 * dz_mm):
        for dx in ((12.0, 22.0, 34.0) if kier == "prawo" else (-12.0, -22.0, -34.0)):
            cands.append((dx, dz))

    def draw(c, cand):
        dx, dz = cand
        B = P + np.array([dx * k, dz * k])
        sg = 1.0 if dx > 0 else -1.0
        c.line(P, B, L_OPI, pen="cienka")
        c.dot(P, 0.8, L_OPI)
        E_ = B + np.array([sg * wt * k, 0.0])
        c.line(B, E_, L_OPI, pen="cienka")
        x = B[0] + (0.8 * k if sg > 0 else -wt * k + 0.8 * k)
        if nr is not None:
            _nr_poz(c, (x + 2.6 * k, B[1] + 2.9 * k), nr, 2.5, L_OPI)
            x += 6.4 * k
        c.text((x, B[1] + 0.9 * k), tekst, h, 0.0, "left", "baseline", L_OPI)
    placer.place(vp, draw, cands, penalty_step=0.15)


def urwanie(vp, p0, p1):
    """Linia urwania (zygzak) między punktami p0, p1."""
    k = vp.k
    a, b = np.asarray(p0, float), np.asarray(p1, float)
    m = (a + b) / 2
    d = b - a
    L = float(np.hypot(*d))
    u = d / L
    nn = np.array([-u[1], u[0]])
    z = 2.0 * k
    pts = [a - u * 2 * k, m - u * z * 0.6, m + nn * z - u * z * 0.2, m - nn * z + u * z * 0.2, m + u * z * 0.6,
           b + u * 2 * k]
    vp.polyline(pts, "A-OPISY", pen="cienka")


# ================================================================================================ fundament
def _podloga(m, kid: str):
    k = m.kondygnacja(kid)
    return m.przegroda(k.podloga) if getattr(k, "podloga", None) else None


def _sciana_na_linii(m, kid: str, Q, u, tol: float = 0.12):
    best = None
    for w in m.sciany(kid):
        if abs(abs(float(w.u @ u)) - 1.0) > 1e-3:
            continue
        d = w.axis_line().distance(Point(*Q))
        if d < tol and (best is None or d < best[0]):
            best = (d, w)
    return best[1] if best else None


def _promien(P, Q, n) -> float:
    """Odległość od Q do brzegu wieloboku P wzdłuż kierunku n."""
    ln = LineString([tuple(Q), tuple(np.asarray(Q) + np.asarray(n) * 50.0)])
    g = ln.intersection(P.exterior)
    ts = [float((np.asarray(p.coords[0]) - Q) @ n) for p in getattr(g, "geoms", [g]) if not p.is_empty]
    ts = [t for t in ts if t > 1e-6]
    return min(ts) if ts else 0.0


def szczegol_fundamentu(ctx, spec, vp, res, placer):
    """Przekrój żebra płyty fundamentowej (lub pogrubienia pod słupem) z warstwami, izolacją obwodową, zbrojeniem
    i uziomem. Zwraca tytuł."""
    from .konstrukcja import _przekroje_fund
    D = KD.dane(ctx)
    m = ctx.model
    F = D.plyta_f
    PF = KD.prety_fundamentu(D)
    els = [e for e in (m.fundamenty().get("elementy") or []) if "os" in e]
    przek = _przekroje_fund(ctx, els)
    lab = str(spec.get("przekroj") or "")
    eid = str(spec.get("element") or next((e for nm, e, _ in przek if nm == lab), ""))
    frac = next((f_ for nm, e_, f_ in przek if e_ == eid), 0.5)
    e = next((x for x in els if str(x["id"]) == eid), None)
    if e is None or F is None:
        raise KeyError(f"k_przekroj/zebro: brak elementu fundamentu '{eid or lab}'")
    ln = LineString(e["os"])
    B, hr, sp_r = float(e.get("b", 0.6)), float(e.get("h", 0.3)), float(e.get("spod", -0.7))
    stopa = ln.length < B
    Q = np.asarray(ln.interpolate(frac, normalized=True).coords[0])
    u = KD_unit(np.asarray(e["os"][1], float) - np.asarray(e["os"][0], float)) if not stopa else np.array([0.0, 1.0])
    n = np.array([-u[1], u[0]])
    obw = F.poly.exterior.distance(Point(*Q)) < 0.5 and not stopa
    if obw and F.poly.buffer(-0.01).contains(Point(*(Q + n * 0.8))):
        n = -n
    R = Rama(Q, n)
    top, sp_p = F.spod + F.h, F.spod
    x_edge = _promien(F.poly, Q, n) if obw else 1.4
    x_in = -1.3 if not stopa else -(B / 2 + 0.7)
    x_out = x_edge if obw else (-x_in)
    cs = E.CutSet()
    # żebro przycięte do lica płyty (model: żebro obwodowe może wystawać poza obrys płyty — zgłaszane w BRAKI_DANYCH)
    beton = unary_union([box(x_in, sp_p, x_out, top), box(-B / 2, sp_r, min(B / 2, x_out), sp_p)])
    cs.add(beton, "ZELBET", "fund")
    k0 = m.kondygnacje[0].id
    pod = _podloga(m, k0)
    # warstwy pod płytą (od betonu w dół), na czole płyty — izolacja pionowa
    prev = beton
    pod_w = []
    if pod is not None:
        for w in pod.warstwy[pod.idx_konstr + 1:]:
            if w.d < 0.002:
                continue
            sh = prev.buffer(w.d, join_style=2).difference(prev)
            sh = sh.difference(box(x_in - 1, sp_p - 1e-6, x_out - 1e-6 if obw else x_out + 1, top + 5))
            sh = sh.intersection(box(x_in, -50, (x_out + w.d + 0.4) if obw else x_out, top))
            hc = hatch_code(m, w.mat)
            sh = clean(sh)
            if not sh.is_empty:
                cs.add(sh, hc, cut_kind(hc, klasa_mat(m, w.mat)))
            pod_w.append((w.mat, w.d))
            prev = prev.union(sh)
    t_v = sum(d for mat, d in pod_w[:1])          # izolacja pionowa czoła = pierwsza warstwa pod płytą (XPS)
    # ściana nad żebrem, warstwy podłogi
    w = None if stopa else _sciana_na_linii(m, k0, Q, u)
    x_wall_in = x_in
    if w is not None:
        wl = warstwy_sciany(w, R)
        dodaj_warstwy_pionowe(cs, m, wl, top, top + 0.7, w.typ)
        x_wall_in = min(a for a, b, *_ in wl)
        x_wall_out = max(b for a, b, *_ in wl)
    if pod is not None:
        if w is not None and not obw:
            dodaj_warstwy_poziome(cs, m, pod, x_in, x_wall_in, top, True)
            dodaj_warstwy_poziome(cs, m, pod, x_wall_out, x_out, top, True)
        else:
            dodaj_warstwy_poziome(cs, m, pod, x_in, x_wall_in if w is not None else (-0.3 if stopa else x_out), top, True)
    # izolacja obwodowa (PN-EN ISO 13793) i teren
    iz = m.fundamenty().get("izolacja_obwodowa") or {}
    z_t = None
    if obw:
        try:
            z_t = float(D.an._teren_przy(tuple(Q + n * (x_edge + 1.0))))
        except Exception:  # noqa: BLE001
            z_t = -0.02
        if iz:
            Dz, dn, gl = float(iz.get("D", 1.0)), float(iz.get("d_n", 0.1)), float(iz.get("glebokosc", 0.45))
            xa, xb = x_edge + t_v, x_edge + t_v + Dz
            za = z_t - gl
            wing = Polygon([(xa, za), (xb, za - 0.02 * Dz), (xb, za - 0.02 * Dz - dn), (xa, za - dn)])
            hc = hatch_code(m, str(iz.get("mat", "XPS300")))
            cs.add(wing, hc, "izol")
        cs.add(box(x_out + t_v, (z_t - 0.9) if z_t is not None else sp_r, x_out + t_v + (float(iz.get("D", 1.0)) + 0.35),
                   z_t), "NASYP", "grunt")
    cs.draw(vp)
    if obw and z_t is not None:
        H.ground_line(vp, [(x_out + t_v, z_t), (x_out + t_v + float(iz.get("D", 1.0)) + 0.35, z_t)])
    if w is not None:
        from .konstrukcja_szczegoly import urwanie as _urw
        _urw(vp, (x_wall_in - 0.05, top + 0.7), (x_wall_out + 0.05, top + 0.7))
    # zbrojenie
    _zbrojenie_fund(vp, placer, D, PF, F, e, R, B, sp_r, sp_p, top, x_in, x_out, obw, stopa, u)
    # wymiary i rzędne (poza obrysem rysunku — łańcuchy pod spodem, rzędne z lewej)
    z_dn = sp_r - sum(d for _m, d in pod_w) - 0.12
    if obw and z_t is not None and iz:
        z_dn = min(z_dn, z_t - float(iz.get("glebokosc", 0.45)) - float(iz.get("d_n", 0.1)) - 0.12)
    ch = sorted({round(v, 4) for v in [-B / 2, min(B / 2, x_out)] + ([x_edge] if obw else [])})
    dims.dim_h(vp, ch, z_dn - 0.05, None, layer="K-WYMIARY")
    if obw and iz:
        ch2 = [x_edge, x_edge + t_v, x_edge + t_v + float(iz.get("D", 1.0))]
        dims.dim_h(vp, ch2, z_dn - 0.05 - 7 * vp.k, None, layer="K-WYMIARY")
    zs = sorted({round(v, 4) for v in (sp_r, sp_p, top)})
    dims.dim_v(vp, zs, x_in - 0.12, None, layer="K-WYMIARY")
    lv = [(top, "konstr"), (sp_p, "konstr"), (sp_r, "konstr")]
    if pod is not None:
        lv.append((top + sum(w_.d for w_ in pod.warstwy[:pod.idx_konstr]), "wyk"))
    dims.levels(vp, x_in - 0.12 - 9 * vp.k, lv, side="left")
    if z_t is not None:
        dims.level_section(vp, (x_out + t_v + float(iz.get("D", 1.0)) + 0.2, z_t), z_t, "wyk", "right")
    nazwa = (f"POGRUBIENIE {eid}" if stopa else f"ŻEBRO {eid}")
    return nazwa, pod, w


def KD_unit(v):
    v = np.asarray(v, float)
    return v / max(float(np.hypot(*v)), 1e-12)


def _grupa_kier(grupy, kier):
    return next((g for g in grupy if g.kier == kier), None)


def _zbrojenie_fund(vp, placer, D, PF, F, e, R, B, sp_r, sp_p, top, x_in, x_out, obw, stopa, u):
    cb, ct = D.c_fund[1] / 1000.0, D.c_fund[0] / 1000.0
    eid = str(e["id"])
    kier_rys = "y" if abs(u[0]) > 0.5 else "x"         # pręty w płaszczyźnie przekroju (prostopadłe do żebra)
    kier_kr = "x" if kier_rys == "y" else "y"
    x_end = x_out - cb
    for warstwa, z_lin, sg in (("dol", sp_p + cb, 1.0), ("gora", top - ct, -1.0)):
        gl = _grupa_kier(PF[warstwa], kier_rys)
        gk = _grupa_kier(PF[warstwa], kier_kr)
        w = F.dol if warstwa == "dol" else F.gora
        fi = w.fi / 1000.0
        z1 = z_lin + sg * fi / 2
        z2 = z_lin + sg * 1.5 * fi
        pret_linia(vp, [(x_in, z1), (x_end, z1)])
        rzad_kropek(vp, x_in + 0.05, x_end - 0.02, z2, w.fi, w.s)
        nrs = "/".join(str(g.pret.nr) for g in (gl, gk) if g is not None)
        opis(vp, placer, (x_in + 0.30, z1), f"poz. {nrs}: siatka {'górna' if warstwa == 'gora' else 'dolna'} "
             f"Ø{w.fi} co {w.s / 10:g}", None, "prawo", 12.0 if warstwa == "gora" else -12.0, h=1.8)
    if stopa:
        st = PF["stopy"].get(eid)
        S_ = next((s_ for s_ in D.stopy if s_.id == eid), None)
        if st and S_:
            fi = S_.siatka.fi / 1000.0
            z = S_.spod + cb + fi / 2
            xa, xb = -B / 2 + cb, B / 2 - cb
            pret_linia(vp, [(xa, z + 0.15), (xa, z), (xb, z), (xb, z + 0.15)])
            rzad_kropek(vp, xa + 0.03, xb - 0.03, z + fi * 1.5, S_.siatka.fi, S_.siatka.s)
            opis(vp, placer, (0.0, z), f"{st['n1']} Ø{S_.siatka.fi} co {S_.siatka.s / 10:g}", st["x"].nr, "prawo", -8.0)
            opis(vp, placer, (xb - 0.1, z + fi * 1.5), f"{st['n2']} Ø{S_.siatka.fi} co {S_.siatka.s / 10:g}",
                 st["y"].nr, "prawo", 8.0)
        return
    z = PF["zebra"].get(eid)
    Z = next((x for x in D.zebra if x.id == eid), None)
    if z is None or Z is None:
        return
    fs = z["strz"].fi / 1000.0
    x0, x1 = -B / 2 + cb + fs / 2, B / 2 - cb - fs / 2
    strzemie(vp, x0, sp_r + cb + fs / 2, x1, top - ct - fs / 2, z["strz"].fi)
    fi = z["dol"].fi / 1000.0
    for nb, zz, pr in ((z["n_dol"], sp_r + cb + fs + fi / 2, z["dol"]),
                       (z["n_gora"], top - ct - fs - 2 * (F.gora.fi / 1000.0) - fi / 2, z["gora"])):
        xs = np.linspace(x0 + fs / 2 + fi / 2, x1 - fs / 2 - fi / 2, max(nb, 2)) if nb > 1 else [0.0]
        for xx in xs:
            pret_kropka(vp, xx, zz, pr.fi)
        opis(vp, placer, (xs[-1], zz), f"{nb} Ø{pr.fi} (żebro {eid})", pr.nr, "prawo", -8.0 if pr is z["dol"] else 6.0)
    opis(vp, placer, (x1, (sp_r + sp_p) / 2), f"strzemiona Ø{z['strz'].fi} co {Z.strz[1] / 10:g}", z["strz"].nr, "prawo",
         0.0)
    if obw:
        pod_t = sum(d for d in [0.2]) if True else 0.0
        zu = sp_r - 0.30
        vp.fill(Point(0.0, zu).buffer(max(0.005, 0.6 * vp.k), 16), "E-UZIOM", KOL_UZ, z=31)
        opis(vp, placer, (0.0, zu), "uziom otokowy V4A Ø10 (w gruncie pod XPS)", None, "prawo", -6.0, h=1.8)
        xr = x0 + 0.06
        vp.fill(box(xr, sp_r + cb + fs + 0.03, xr + 0.03, sp_r + cb + fs + 0.034), "E-UZIOM", KOL_UZ, z=31)
        vp.rect(xr - 0.004, sp_r + cb + fs + 0.026, xr + 0.034, sp_r + cb + fs + 0.038, "E-UZIOM", pen=0.25, color=KOL_UZ)
        opis(vp, placer, (xr + 0.015, sp_r + cb + fs + 0.032), "przewód wyrównawczy FeZn 30×4", None, "lewo", -10.0,
             h=1.8)


def opis_warstw(vp, placer, x, z0, z1, warstwy, model, strona="lewo", tytul=None):
    """Opis warstw poziomych (drabinka) — od najwyższej; warstwy: [(z0, z1, mat)]."""
    from .common import layer_text
    if not warstwy:
        return
    ws = sorted(warstwy, key=lambda t: -t[1])
    txt = [layer_text(model, mat, zz1 - zz0) for zz0, zz1, mat in ws]
    marks = [(x, (a + b) / 2) for a, b, _ in ws]
    k = vp.k
    p_start = (x, (ws[-1][0] + ws[-1][1]) / 2)
    p_end = (x + (-1 if strona == "lewo" else 1) * 14 * k, max(z1, ws[0][1]) + 6 * k)
    r = S.layer_callout(vp, p_start, p_end, txt, side="left" if strona == "lewo" else "right", h=1.8, marks=marks,
                        layer=L_OPS, title=tytul)
    placer.add(box(*r), "text", 1.0)


# ================================================================================================ stropy: węzły
def _kond_nad(m, z: float):
    ks = [k for k in m.kondygnacje if abs(k.rzedna - z) < 0.45]
    return min(ks, key=lambda k: abs(k.rzedna - z)) if ks else None


def _wybor_wezla(D, lv, rodzaj: str, element: str | None, m):
    """(Q, n, ściana pod, element płyty zaplecza, element wspornika | None, grupa prętów wspornika | None)."""
    from .konstrukcja import sciany_pod
    sc = sciany_pod(m, lv.spod)
    P = KD.prety_poziomu(D, lv)
    if rodzaj == "wspornik":
        e = next((x for x in lv.elementy if x.id == element), None) or next((x for x in lv.elementy if x.typ == "wspornik"
                                                                           and x.lacznik), None)
        if e is None:
            raise KeyError("k_przekroj/wspornik: brak płyty wspornikowej w poziomie")
        gs = [g for g in P["gora"] if g.element == e.id and g.rola == "wspornik" and g.haki[0] != g.haki[1]]
        g = max(gs, key=lambda q: q.n) if gs else None
        if g is None:
            raise KeyError(f"k_przekroj/wspornik: brak zbrojenia wspornika {e.id}")
        a, b = np.asarray(g.linia[0]), np.asarray(g.linia[1])
        tip = a if g.haki[0] else b
        u = KD_unit(tip - (b if g.haki[0] else a))
        kz = KD.korzenie(e, lv)
        rr, gap, _n = min(kz, key=lambda t: t[0].distance(Point(*tip)) if abs(float(KD_unit(np.subtract(t[0].coords[-1],
                                                                                                    t[0].coords[0])) @ u)) < 0.1 else 1e9)
        Q = np.asarray(rr.interpolate(rr.project(Point(*tip))).coords[0])
        host = next((x for x in lv.elementy if x is not e and x.poly.buffer(0.01).contains(Point(*(Q - u * (gap + 0.2))))), None)
        e._szczelina = gap
        wall = min((w for w in sc if abs(float(w.u @ u)) < 1e-3), key=lambda w: w.axis_line().distance(Point(*(Q - u * 0.3))),
                   default=None)
        return Q, u, wall, host, e, g
    kand = []
    Pl = lv.poly.buffer(-0.05)
    for w in sc:
        if w.warstwa_konstr.polygon is None:
            continue
        for fr in (0.5, 0.35, 0.65, 0.25, 0.75):
            mid = w.pt(w.L * fr, 0.0)
            if any(o.s0 - 0.3 <= w.L * fr <= o.s1 + 0.3 for o in w.otwory):
                continue                              # przekrój poza otworem (nadprożem)
            if rodzaj == "wieniec" and w.ext_side is not None:
                nn = w.n * w.ext_side
                if any(x.typ == "wspornik" and x.poly.distance(Point(*(mid + nn * 0.6))) < 0.4 for x in lv.elementy):
                    continue
                if Pl.contains(Point(*(mid - nn * 0.8))):
                    kand.append((w.L, w, nn, mid))
                    break
            elif rodzaj == "oparcie" and w.typ == "sciana_wewn_nosna":
                if Pl.contains(Point(*(mid + w.n * 0.8))) and Pl.contains(Point(*(mid - w.n * 0.8))):
                    kand.append((w.L, w, w.n, mid))
                    break
    if element:
        kand = [k_ for k_ in kand if k_[1].id == element] or kand
    if not kand:
        raise KeyError(f"k_przekroj/{rodzaj}: brak odpowiedniej ściany pod płytą {lv.nazwa}")
    L_, w, nn, Q = max(kand, key=lambda t: t[0])
    host = next((x for x in lv.elementy if x.poly.buffer(0.01).contains(Point(*(Q - nn * 0.4)))), lv.elementy[0])
    return Q, nn, w, host, None, None


def _grupy_przy(P, warstwa, Q, n, rola=None, r=1.5):
    """Grupy prętów przecinające odcinek Q ± n·r (w płaszczyźnie przekroju) — (grupa, kierunek w płaszczyźnie?)."""
    ln = LineString([tuple(Q - n * r), tuple(Q + n * r)])
    out = []
    for g in P[warstwa]:
        if rola and g.rola not in rola:
            continue
        a, b = np.asarray(g.linia[0]), np.asarray(g.linia[1])
        u = KD_unit(b - a)
        if abs(float(u @ n)) > 0.9:
            # pręt w płaszczyźnie przekroju — musi mieć zasięg rozkładu obejmujący Q
            r0, r1 = np.asarray(g.rozklad[0]), np.asarray(g.rozklad[1])
            v = KD_unit(r1 - r0) if np.hypot(*(r1 - r0)) > 1e-6 else np.array([-n[1], n[0]])
            t0, t1 = sorted((float((r0 - Q) @ v), float((r1 - Q) @ v)))
            if t0 - 0.1 <= 0.0 <= t1 + 0.1 and LineString([a, b]).distance(ln) < 2.0:
                out.append((g, True))
        elif LineString([a, b]).buffer(0.01).intersects(ln) or g.zakres is not None and g.zakres.intersects(ln):
            out.append((g, False))
    return out


def szczegol_stropu(ctx, spec, vp, res, placer, rodzaj: str):
    """Węzeł stropu: ``wspornik`` (płyta wspornikowa z łącznikiem termoizolacyjnym), ``wieniec`` (krawędź stropu na
    ścianie zewnętrznej), ``oparcie`` (strop ciągły nad ścianą wewnętrzną)."""
    D = KD.dane(ctx)
    m = ctx.model
    lv = None
    for key in ("poziom", "element", "kond"):
        if spec.get(key) and lv is None:
            lv = D.poziom(spec.get(key))
    if lv is None:
        raise KeyError(f"k_przekroj/{rodzaj}: brak poziomu płyt")
    P = KD.prety_poziomu(D, lv)
    Q, n, wall, host, wsp, gw = _wybor_wezla(D, lv, rodzaj, spec.get("element") if rodzaj != "wspornik" else
                                             spec.get("element"), m)
    R = Rama(Q, n)
    host = host or lv.elementy[0]
    top_h, sp_h = host.wierzch, host.wierzch - host.h
    cs = E.CutSet()
    wl = warstwy_sciany(wall, R) if wall is not None else []
    xw0 = min((a for a, b, *_ in wl), default=-0.1)
    xw1 = max((b for a, b, *_ in wl), default=0.1)
    xk = [(a, b) for a, b, mat, konstr, kl in wl if konstr]
    xk0, xk1 = xk[0] if xk else (-0.09, 0.09)
    x_in = xk0 - 1.3
    tl = KD.LACZNIK_T
    if rodzaj == "wspornik":
        l_c = _promien(wsp.poly, Q + n * 0.01, n) + 0.01
        gap = getattr(wsp, "_szczelina", 0.0)
        tl = gap if gap >= 0.03 else KD.LACZNIK_T
        x_edge_h = -tl
        x_out = l_c
    elif rodzaj == "wieniec":
        x_edge_h = _promien(host.poly, Q, n)
        x_out = x_edge_h
    else:
        x_edge_h = xk1 + 1.3
        x_out = x_edge_h
    z_bot = sp_h - 0.75
    if wall is not None:
        dodaj_warstwy_pionowe(cs, m, wl, z_bot, min(wall.z_do, sp_h), wall.typ)
    cs.add(box(x_in, sp_h, x_edge_h, top_h), "ZELBET", "strop")
    # ściana powyżej (ta sama oś), warstwy podłogi i sufitu
    kn = _kond_nad(m, top_h)
    w_up = _sciana_na_linii(m, kn.id, Q, np.array([-n[1], n[0]])) if (kn is not None and wall is not None) else None
    wl_up = warstwy_sciany(w_up, R) if w_up is not None else []
    if wl_up:
        dodaj_warstwy_pionowe(cs, m, wl_up, top_h, top_h + 0.7, w_up.typ)
    pod = m.przegroda(kn.podloga) if kn is not None and getattr(kn, "podloga", None) else None
    u0 = min((a for a, b, *_ in wl_up), default=x_edge_h)
    u1 = max((b for a, b, *_ in wl_up), default=x_edge_h)
    warstwy_pod = []
    if pod is not None:
        if rodzaj == "oparcie" and wl_up:
            warstwy_pod = dodaj_warstwy_poziome(cs, m, pod, x_in, u0, top_h, True)
            dodaj_warstwy_poziome(cs, m, pod, u1, x_out, top_h, True)
        else:
            warstwy_pod = dodaj_warstwy_poziome(cs, m, pod, x_in, u0 if wl_up else (x_edge_h if rodzaj != "wspornik"
                                                                                  else xw0), top_h, True)
        pd_ = pod
        dodaj_warstwy_poziome(cs, m, pd_, x_in, xw0 if wall is not None else x_out, sp_h, False)
        if rodzaj == "oparcie":
            dodaj_warstwy_poziome(cs, m, pd_, xw1, x_out, sp_h, False)
    if rodzaj == "wspornik":
        tc, spc = wsp.wierzch, wsp.wierzch - wsp.h
        cs.add(box(0.0, spc, l_c, tc), "ZELBET", "strop")
        prz = m.przegroda(wsp.raw.get("przegroda")) if wsp.raw.get("przegroda") else None
        if prz is not None:
            dodaj_warstwy_poziome(cs, m, prz, 0.0, l_c, tc, True)
            dodaj_warstwy_poziome(cs, m, prz, 0.0, l_c, spc, False)
        zl0, zl1 = max(sp_h, spc), min(top_h, tc)
        cs.add(box(-tl, zl0, 0.0, zl1), "IZOL_TWARDA", "izol")
    cs.draw(vp)
    if wall is not None:
        urwanie(vp, (xw0 - 0.05, z_bot), (xw1 + 0.05, z_bot))
    if wl_up:
        urwanie(vp, (u0 - 0.05, top_h + 0.7), (u1 + 0.05, top_h + 0.7))
    urwanie(vp, (x_in, sp_h - 0.05), (x_in, top_h + 0.12))
    if rodzaj == "oparcie":
        urwanie(vp, (x_out, sp_h - 0.05), (x_out, top_h + 0.12))
    zb = _zbrojenie_wezla(vp, placer, D, P, lv, host, wsp, gw, R, Q, n, rodzaj, x_in, x_out, x_edge_h, xk0, xk1,
                          top_h, sp_h)
    # wymiary, rzędne
    ch = sorted({round(v, 4) for v in [xk0, xk1] + ([x_edge_h, 0.0, x_out] if rodzaj == "wspornik" else [x_edge_h])
                 if x_in < v <= x_out + 1e-6})
    dims.dim_h(vp, ch, z_bot - 0.12, None, layer="K-WYMIARY")
    zz = sorted({round(v, 4) for v in (sp_h, top_h)})
    dims.dim_v(vp, zz, x_in - 0.15, None, layer="K-WYMIARY")
    lvl = [(top_h, "konstr"), (sp_h, "konstr")]
    if pod is not None:
        lvl.append((top_h + sum(w_.d for w_ in pod.warstwy[:pod.idx_konstr]), "wyk"))
    dims.levels(vp, x_in + 0.1, lvl, side="left")
    if rodzaj == "wspornik":
        dims.dim_v(vp, sorted({round(wsp.wierzch - wsp.h, 4), round(wsp.wierzch, 4)}), x_out + 0.15, None,
                   layer="K-WYMIARY")
        dims.levels(vp, x_out - 0.1, [(wsp.wierzch, "konstr")], side="right")
    if warstwy_pod:
        opis_warstw(vp, placer, x_in + 0.45, sp_h, top_h, warstwy_pod, m, "lewo",
                    tytul=f"{pod.nazwa.split(':')[0][:40]}" if pod is not None else None)
    tyt = {"wspornik": f"WĘZEŁ WSPORNIKA {wsp.id if wsp else ''} — ŁĄCZNIK TERMOIZOLACYJNY",
           "wieniec": f"WIENIEC — KRAWĘDŹ STROPU {host.id} NA ŚCIANIE {wall.id if wall else ''}",
           "oparcie": f"OPARCIE STROPU {host.id} NA ŚCIANIE {wall.id if wall else ''}"}[rodzaj]
    return tyt, zb


def _zbrojenie_wezla(vp, placer, D, P, lv, host, wsp, gw, R, Q, n, rodzaj, x_in, x_out, x_edge_h, xk0, xk1, top_h, sp_h):
    k = vp.k
    uzyte = []

    def c_of(eid):
        e = next((x for x in lv.elementy if x.id == eid), host)
        return e.c_nom / 1000.0, e

    def rysuj_w_plaszczyznie(g, warstwa, lab_dz):
        c, e = c_of(g.element)
        top, sp = e.wierzch, e.wierzch - e.h
        fi = g.pret.fi / 1000.0
        a, b = np.asarray(g.linia[0]), np.asarray(g.linia[1])
        xa, xb = R.x(a), R.x(b)
        if xa > xb:
            xa, xb = xb, xa
            hk = (g.haki[1], g.haki[0])
        else:
            hk = g.haki
        xa, xb = max(xa, x_in), min(xb, x_out)
        z = (sp + c + fi / 2) if warstwa == "dol" else (top - c - fi / 2)
        leg = e.h - 2 * c
        pts = [(xa, z), (xb, z)]
        if hk[0] and warstwa == "gora":
            pts = [(xa, z - leg)] + pts
        if hk[1] and warstwa == "gora":
            pts = pts + [(xb, z - leg)]
        pret_linia(vp, pts)
        xm = (xa + xb) / 2
        opis(vp, placer, (xm, z), f"{g.n if g.kawalki == 1 else g.n // g.kawalki} Ø{g.pret.fi}"
             + (f" co {g.s / 10:g}" if g.s else "") + f" l={g.pret.L_mm / 10:g}", g.pret.nr,
             "prawo" if xm > 0 else "lewo", lab_dz)
        uzyte.append(g)

    def kropki(g, warstwa, x0, x1, off):
        c, e = c_of(g.element)
        top, sp = e.wierzch, e.wierzch - e.h
        fi = g.pret.fi / 1000.0
        z = (sp + c + off + fi / 2) if warstwa == "dol" else (top - c - off - fi / 2)
        if g.s:
            rzad_kropek(vp, x0 + 0.04, x1 - 0.04, z, g.pret.fi, g.s)
        opis(vp, placer, ((x0 + x1) / 2, z), f"Ø{g.pret.fi}" + (f" co {g.s / 10:g}" if g.s else ""), g.pret.nr,
             "lewo" if x1 < 0.3 else "prawo", 10.0 if warstwa == "gora" else -10.0)
        uzyte.append(g)

    lab = {"dol": -6.0, "gora": 6.0}
    for warstwa in ("dol", "gora"):
        gr = _grupy_przy(P, warstwa, Q, n)
        inpl = [g for g, ip in gr if ip and g.rola != "naroze"]
        perp = [g for g, ip in gr if not ip and g.rola != "naroze"]
        seen = set()
        for i, g in enumerate(sorted(inpl, key=lambda q: -q.n)):
            key = (g.element, g.pret.nr, round(R.x(g.linia[0]), 1))
            if key in seen:
                continue
            seen.add(key)
            rysuj_w_plaszczyznie(g, warstwa, lab[warstwa] * (1 + 0.8 * i))
        fi_in = max((g.pret.fi for g in inpl), default=8) / 1000.0
        for g in perp[:2]:
            c, e = c_of(g.element)
            x0 = x_in if e is host else 0.0
            x1 = (x_edge_h - c) if e is host else x_out - c
            kropki(g, warstwa, x0, x1, fi_in)
    # wieniec w płycie nad ścianą murowaną
    wn = next((w for w in D.wience if lv.idx in w.ids), None)
    if wn is not None and rodzaj in ("wieniec", "oparcie", "wspornik"):
        cw = wn.c_nom / 1000.0
        fs = wn.strz[0] / 1000.0
        x0, x1 = xk0 + cw, xk1 - cw
        z0, z1 = sp_h + cw, top_h - cw - 0.012
        strzemie(vp, x0, z0, x1, z1, wn.strz[0])
        fi = wn.dol[1] / 1000.0
        for xx in (x0 + fs + fi / 2, x1 - fs - fi / 2):
            for zz in (z0 + fs + fi / 2, z1 - fs - fi / 2):
                pret_kropka(vp, xx, zz, wn.dol[1])
        opis(vp, placer, (x1 - fs, z0 + fs), f"wieniec {wn.dol[0] + wn.gora[0]}Ø{wn.dol[1]}, strz. Ø{wn.strz[0]} co "
             f"{wn.strz[1] / 10:g} (poz. obl. {wn.poz})", None, "prawo" if rodzaj != "wspornik" else "lewo", -14.0, h=1.8)
    if rodzaj == "wspornik" and wsp is not None:
        gap = getattr(wsp, "_szczelina", 0.0)
        tl = gap if gap >= 0.03 else KD.LACZNIK_T
        c = wsp.c_nom / 1000.0
        zt = min(top_h, wsp.wierzch) - c - 0.006
        vp.line((-tl - 0.55, zt), (0.55, zt), L_ZBR, pen=0.35, lt="KRESKOWA", z=31)
        zb_ = max(sp_h, wsp.wierzch - wsp.h) + c + 0.02
        vp.rect(-tl - 0.02, zb_, 0.02, zb_ + 0.05, L_ZBR, pen=0.35, z=31)
        opis(vp, placer, (0.3, zt), "pręty rozciągane łącznika (ETA), zakład z prętami płyt", None, "prawo", 16.0, h=1.8)
        opis(vp, placer, (-tl / 2, zb_ + 0.025), "moduł ściskany łącznika", None, "prawo", -16.0, h=1.8)
        pz = max(wsp.pola, key=lambda p: p.poly.area) if wsp.pola else None
        kier = "x" if abs(n[0]) > 0.5 else "y"
        w = pz.warstwy.get("gora_" + kier) if pz else None
        opis(vp, placer, (-tl / 2, (max(sp_h, wsp.wierzch - wsp.h) + min(top_h, wsp.wierzch)) / 2),
             f"łącznik termoizolacyjny (ETA) h = {wsp.h * 100:.0f} cm, izolacja {tl * 1000:.0f} mm, "
             f"m_Ed = {w.M:.1f} kNm/m" if w else "łącznik termoizolacyjny (ETA)", None, "lewo", 22.0, h=1.8)
    return uzyte
