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
from .common import Placer, cut_kind, hatch_code, klasa_mat, material_name

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
    beton = unary_union([box(x_in, sp_p, x_out, top), box(-B / 2, sp_r, B / 2, sp_p)])
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
    # wymiary i rzędne
    ch = sorted({round(v, 4) for v in ([-B / 2, B / 2] + ([x_edge] if obw else []))})
    dims.dim_h(vp, ch, (sp_r if not obw else min(sp_r, (z_t or sp_r) - 1.0)) - 0.25, None, layer="K-WYMIARY")
    zs = sorted({round(v, 4) for v in (sp_r, sp_p, top)})
    dims.dim_v(vp, zs, x_in - 0.18, None, layer="K-WYMIARY")
    lv = [(top, "konstr"), (sp_p, "konstr"), (sp_r, "konstr")]
    if pod is not None:
        lv.append((top + sum(w_.d for w_ in pod.warstwy[:pod.idx_konstr]), "wyk"))
    dims.levels(vp, x_in + 0.05, lv, side="left")
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
        if gl is not None:
            opis(vp, placer, (x_in + 0.35, z1), f"{gl.pret.fi and 'Ø' + str(gl.pret.fi)} co {w.s / 10:g}", gl.pret.nr,
                 "lewo", 9.0 if warstwa == "gora" else -9.0)
        if gk is not None:
            opis(vp, placer, (x_in + 0.35 + w.s / 1000.0 * 2, z2), f"Ø{gk.pret.fi} co {w.s / 10:g}", gk.pret.nr,
                 "lewo", 16.0 if warstwa == "gora" else -16.0)
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
        inne = unary_union([x.poly for x in lv.elementy if x is not e])
        root = [q for q in KD.odcinki_proste(e.poly.boundary.intersection(inne.buffer(0.02))) if q.length > 0.3]
        rr = min(root, key=lambda q: q.distance(Point(*tip)) if abs(abs(float(KD_unit(np.subtract(q.coords[-1], q.coords[0])) @ u))) < 0.1 else 1e9)
        Q = np.asarray(rr.interpolate(rr.project(Point(*tip))).coords[0])
        host = next((x for x in lv.elementy if x is not e and x.poly.buffer(0.01).contains(Point(*(Q - u * 0.2)))), None)
        wall = min((w for w in sc if abs(float(w.u @ u)) < 1e-3), key=lambda w: w.axis_line().distance(Point(*(Q - u * 0.3))),
                   default=None)
        return Q, u, wall, host, e, g
    kand = []
    for w in sc:
        if w.warstwa_konstr.polygon is None:
            continue
        mid = w.pt(w.L / 2, 0.0)
        if rodzaj == "wieniec" and w.ext_side is not None:
            nn = w.n * w.ext_side
            if any(x.typ == "wspornik" and x.poly.distance(Point(*(mid + nn * 0.6))) < 0.3 for x in lv.elementy):
                continue
            kand.append((w.L, w, nn))
        elif rodzaj == "oparcie" and w.typ == "sciana_wewn_nosna" and w.ext_side is None:
            if lv.poly.buffer(-0.05).contains(Point(*(mid + w.n * 0.8))) and lv.poly.buffer(-0.05).contains(Point(*(mid - w.n * 0.8))):
                kand.append((w.L, w, w.n))
    if element:
        kand = [k_ for k_ in kand if k_[1].id == element] or kand
    if not kand:
        raise KeyError(f"k_przekroj/{rodzaj}: brak odpowiedniej ściany pod płytą {lv.nazwa}")
    L_, w, nn = max(kand, key=lambda t: t[0])
    Q = w.pt(w.L / 2, 0.0)
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
