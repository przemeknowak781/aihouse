"""Walidacja modułu tarcz (MES QM6 + STM) i demo tarczy wspornikowej wariantu W2.

(a1) **Rozwiązanie ścisłe teorii sprężystości** — belka-tarcza 2l × 2c obciążona równomiernie q na krawędzi górnej,
     podparta trakcjami stycznymi na końcach (Timoshenko & Goodier, *Theory of Elasticity*, 3rd ed. 1970, §22 [P]):
     σ_x = −q/(2I)·[(l² − x²)·z + 2z³/3 − 2c²z/5], σ_z = −q/(2I)·(−z³/3 + c²z + 2c³/3), τ_xz = q/(2I)·(c² − z²)·x,
     I = 2c³/3 (z w górę). Wzory sprawdzane w teście (równania równowagi, warunki brzegowe) — niezależnie od źródła.
     Obciążenie trakcjami końcowymi zgodnie z rozwiązaniem → MES odtwarza pole naprężeń (także dla l/h = 1 — belka-ściana).
(a2) **Belka-ściana jednoprzęsłowa** (podpory punktowe szer. 0,1·l, obciążenie równomierne od góry): ramię sił
     wewnętrznych i siła w ściągu z MES (sprężyste) i STM vs reguły projektowe CEB-FIP / DAfStb Heft 240 (z = 0,2·(l + 2h),
     z = 0,6·l dla l/h < 1 — oparte na analizach sprężystych Leonhardta [P]) oraz funkcja ``zelbet.belka_sciana``.
(b)  **Wspornik pełny** utwierdzony w ścianie poprzecznej, siła na końcu (trakcja paraboliczna): ugięcie końca vs teoria
     belek Timoshenki w = P·l³/(3EI) + P·l/(κ·G·A), κ = 5/6 — zgodność dla wspornika smukłego (granica l/h → ∞),
     odchylenie dla krótkich wsporników (tarcze wspornikowe) — wykres.
(c)  **Zbieżność siatki** tarczy demo (h = 0,20 / 0,10 / 0,05 m): ugięcie wspornika, siła w pasie górnym, reakcje.
(d)  **Równowaga**: ΣR = ΣF w kombinacjach, siły w przekrojach (całkowanie σ) vs statyka części tarczy.
"""
from __future__ import annotations

import math
import time
from pathlib import Path

import numpy as np
from shapely.geometry import box

from . import zelbet
from .materialy import Beton
from .obciazenia import Oddz
from .tarcze import AnalizaTarczy, DaneTarczy, OtworT, raport_tarczy
from .tarcze_mes import ObcLiniowe, ObcSkupione, PodporaT, TarczaMES, blok_przy_krawedzi
from .wspolne import Parametry, f, tabela


# ==================================================================================================
# (a1) Timoshenko–Goodier
# ==================================================================================================
def tg_naprezenia(x, z, l, c, q):
    """Rozwiązanie ścisłe (T&G §22, oś z w górę): (σ_x, σ_z, τ_xz) dla belki 2l × 2c, grubość 1, obciążenie q na z = +c."""
    I = 2 * c ** 3 / 3
    sx = -(q / (2 * I)) * ((l ** 2 - x ** 2) * z + 2 * z ** 3 / 3 - 2 * c ** 2 * z / 5)
    sz = -(q / (2 * I)) * (-z ** 3 / 3 + c ** 2 * z + 2 * c ** 3 / 3)
    t = (q / (2 * I)) * (c ** 2 - z ** 2) * x
    return sx, sz, t


def tg_kontrola_wzorow(l=1.0, c=0.5, q=10.0, h=1e-5) -> dict:
    """Numeryczne sprawdzenie wzorów: ∂σx/∂x + ∂τ/∂z = 0, ∂τ/∂x + ∂σz/∂z = 0, σ_z(+c) = −q, σ_z(−c) = 0, τ(±c) = 0,
    ∫τ dz na końcu = q·l (reakcja), ∫σ_x dz = ∫σ_x·z dz = 0 na końcu."""
    pts = [(0.3 * l, 0.2 * c), (-0.7 * l, -0.6 * c), (0.9 * l, 0.8 * c)]
    r1 = r2 = 0.0
    for x, z in pts:
        dsx = (tg_naprezenia(x + h, z, l, c, q)[0] - tg_naprezenia(x - h, z, l, c, q)[0]) / (2 * h)
        dtz = (tg_naprezenia(x, z + h, l, c, q)[2] - tg_naprezenia(x, z - h, l, c, q)[2]) / (2 * h)
        dtx = (tg_naprezenia(x + h, z, l, c, q)[2] - tg_naprezenia(x - h, z, l, c, q)[2]) / (2 * h)
        dsz = (tg_naprezenia(x, z + h, l, c, q)[1] - tg_naprezenia(x, z - h, l, c, q)[1]) / (2 * h)
        r1 = max(r1, abs(dsx + dtz))
        r2 = max(r2, abs(dtx + dsz))
    zs = np.linspace(-c, c, 2001)
    sx_e, _, t_e = tg_naprezenia(l, zs, l, c, q)
    return {"rown_x": r1, "rown_z": r2, "sz_gora": float(tg_naprezenia(0.2, c, l, c, q)[1]), "sz_dol": float(tg_naprezenia(0.2, -c, l, c, q)[1]),
            "tau_brzeg": float(abs(tg_naprezenia(0.4, c, l, c, q)[2])), "V_koniec": float(np.trapezoid(t_e, zs)),
            "N_koniec": float(np.trapezoid(sx_e, zs)), "M_koniec": float(np.trapezoid(sx_e * zs, zs)), "ql": q * l}


def walidacja_tg(l: float = 1.0, c: float = 0.5, q: float = 100.0, h: float = 0.05) -> dict:
    """MES tarczy 2l × 2c vs rozwiązanie ścisłe: maks. błąd względny σ_x, τ (względem maksimum) i σ_z (względem q)."""
    P = box(-l, -c, l, c)
    pods = [PodporaT("A", -l, -l, 0.0, tylko_docisk=False), PodporaT("B", l, l, 0.0, tylko_docisk=False)]
    m = TarczaMES(P, 1.0, 3.0e7, nu=0.2, gamma=0.0, podpory=pods, obciazenia=[ObcLiniowe("Q", -l, l, c, q)], siatka=h,
                  linie=((0.0,), (0.0,)))
    fv = m.wektor({"Q": 1.0})
    for xe, sgn in ((-l, -1), (l, 1)):
        nd = np.nonzero(np.abs(m.nodes[:, 0] - xe) < 1e-9)[0]
        nd = nd[np.argsort(m.nodes[nd, 1])]
        z = m.nodes[nd, 1]
        for a, b, ka, kb in zip(z[:-1], z[1:], nd[:-1], nd[1:]):
            for gp in (-1 / math.sqrt(3), 1 / math.sqrt(3)):
                zz = 0.5 * (a + b) + 0.5 * (b - a) * gp
                w = 0.5 * (b - a)
                sx, _, tz = tg_naprezenia(xe, zz, l, c, q)
                Na = (b - zz) / (b - a)
                fx, fz = sx * sgn * w, tz * sgn * w
                fv[2 * ka] += fx * Na
                fv[2 * kb] += fx * (1 - Na)
                fv[2 * ka + 1] += fz * Na
                fv[2 * kb + 1] += fz * (1 - Na)
    r = m.rozwiaz(fv)
    x, z = m.el_c[:, 0], m.el_c[:, 1]
    sx, sz, tz = tg_naprezenia(x, z, l, c, q)
    R = m.reakcje(r)
    # profil σ_x w środku rozpiętości (przekrój pionowy przez środki elementów)
    xc = float(m.el_c[np.argmin(np.abs(m.el_c[:, 0]))][0])
    cut = m.przekroj_pionowy(r, xc)
    zp = np.array([0.5 * (p_[0] + p_[1]) for p_ in cut["prof"]])
    sp = np.array([0.5 * (p_[3] + p_[4]) for p_ in cut["prof"]])
    return {"l_h": l / c, "h": h, "ne": m.ne,
            "err_sx": float(np.abs(r.sig[:, 0] - sx).max() / np.abs(sx).max()),
            "err_sz": float(np.abs(r.sig[:, 1] - sz).max() / q),
            "err_tau": float(np.abs(r.sig[:, 2] - tz).max() / np.abs(tz).max()),
            "R_resztkowe": float(abs(R["A"]["R"]) + abs(R["B"]["R"])),
            "profil": (zp, sp, tg_naprezenia(xc, zp, l, c, q)[0]), "x_profil": xc}


# ==================================================================================================
# (a2) Belka-ściana jednoprzęsłowa
# ==================================================================================================
def z_ceb(l: float, h: float) -> float:
    """Ramię sił wewnętrznych belki-ściany jednoprzęsłowej wg CEB-FIP (= DAfStb Heft 240 dla 1 ≤ l/h ≤ 2)."""
    return 0.6 * l if l / h < 1 else 0.2 * (l + 2 * h)


def walidacja_belka_sciana(l: float = 3.0, l_h: float = 1.5, q: float = 100.0, t: float = 0.20, siatka: float = 0.05,
                           stm: bool = True) -> dict:
    """Belka-ściana: rozpiętość l (osie podpór), podpory szer. a = 0,1·l na narożach dolnych, q [kN/m] na krawędzi górnej."""
    h = l / l_h
    a = 0.1 * l
    Lb = l + a
    pods = [PodporaT("A", 0.0, a, 0.0), PodporaT("B", l, l + a, 0.0)]
    obc = [ObcLiniowe("Q", 0.0, Lb, h, q, opis="obciążenie od góry")]
    m = TarczaMES(box(0, 0, Lb, h), t, 31e6, nu=0.2, gamma=0.0, podpory=pods, obciazenia=obc, siatka=siatka)
    r = m.rozwiaz_kombinacje({"Q": 1.0})
    xm = Lb / 2
    cx = 0.5 * (m.gx[:-1] + m.gx[1:])
    xc = float(cx[np.argmin(np.abs(cx - xm))])
    cut = m.przekroj_pionowy(r, xc)
    blk = blok_przy_krawedzi(cut["prof"], 0.0, True)
    T_el = blk["F"]
    RA = m.reakcje(r)["A"]
    M_st = RA["R"] * (xc - RA["xR"]) - q * xc ** 2 / 2          # statyka z reakcji MES (środek reakcji x_R)
    M_nom = q * (l ** 2 - a ** 2) / 8                            # reakcje w osiach podpór
    z_el = abs(cut["M"]) / T_el if T_el > 0 else float("nan")
    # funkcja biblioteki (ta sama geometria, q_d = q)
    bs = zelbet.belka_sciana(l, h, t, q, Beton("C30/37"), a_podp=a)
    out = {"l_h": l_h, "l": l, "h": h, "M_MES": abs(cut["M"]), "M_statyka": M_st, "M_nominalny": M_nom, "x_R": RA["xR"], "T_MES": T_el, "z_MES": z_el, "z_CEB": z_ceb(l, h),
           "T_CEB": q * l ** 2 / 8 / z_ceb(l, h), "T_belka_sciana": bs.T, "z_belka_sciana": bs.z, "h_rozc": blk["h"],
           "prof": ([0.5 * (p_[0] + p_[1]) for p_ in cut["prof"]], [0.5 * (p_[3] + p_[4]) / 1000 for p_ in cut["prof"]])}
    if stm:
        d = DaneTarczy(f"BS-{l_h:g}", Lb, h, t, podpory=[PodporaT("A", 0.0, a, 0.0), PodporaT("B", l, l + a, 0.0)],
                       obciazenia=[ObcLiniowe("Q", 0.0, Lb, h, q)], przypadki={"Q": Oddz("Q", "G")}, gamma=0.0, ekspozycja="XC1")
        an = AnalizaTarczy(d, Parametry(), siatka=max(siatka, 0.05))
        an._mes()
        an._kombinacje_i_rozwiazania()
        an.r_uls = {"Q": an.mes.rozwiaz_kombinacje({"Q": 1.0})}
        an.k_gov = "Q"
        an.s1_env = an.s2_env = np.abs(an.r_uls["Q"].sig[:, 0])
        an.stm = an._generuj_stm(an.r_uls["Q"])
        an._rozwiaz_stm("Q", an.r_uls["Q"])
        Fm = an.stm.F["Q"]
        W = an.stm.wezly
        mid = 0.5 * (W[an.stm.ii] + W[an.stm.jj])
        dol = (mid[:, 1] < 0.35 * h) & (np.abs(an.stm.U[:, 1]) < 0.3) & (np.abs(mid[:, 0] - xm) < 0.35 * l)
        out["T_STM"] = float(Fm[dol].max()) if dol.any() else float("nan")
        out["stm_an"] = an
    return out


# ==================================================================================================
# (b) Wspornik
# ==================================================================================================
def walidacja_wspornik(l: float, h: float = 0.5, t: float = 0.2, P: float = 100.0, E: float = 30e6, nu: float = 0.2,
                       siatka: float | None = None) -> dict:
    """Wspornik utwierdzony (x = 0, u_x = u_z = 0 na całej wysokości), trakcja paraboliczna P na końcu. Ugięcie osi końca
    vs teoria Timoshenki (zginanie + ścinanie, κ = 5/6)."""
    s = siatka or min(h / 10, l / 20)
    pods = [PodporaT("U", 0.0, 0.0, 0.0, kx=True, z1=h)]
    m = TarczaMES(box(0, 0, l, h), t, E, nu=nu, gamma=0.0, podpory=pods, obciazenia=[], siatka=s, linie=((), (h / 2,)))
    fv = np.zeros(2 * m.nn)
    nd = np.nonzero(np.abs(m.nodes[:, 0] - l) < 1e-9)[0]
    nd = nd[np.argsort(m.nodes[nd, 1])]
    zz = m.nodes[nd, 1]
    c = h / 2
    for a, b, ka, kb in zip(zz[:-1], zz[1:], nd[:-1], nd[1:]):
        for gp in (-1 / math.sqrt(3), 1 / math.sqrt(3)):
            z = 0.5 * (a + b) + 0.5 * (b - a) * gp
            w = 0.5 * (b - a)
            tau = 3 * P / (2 * t * h) * (1 - ((z - c) / c) ** 2)     # paraboliczny rozkład, ∫τ·t dz = P
            Na = (b - z) / (b - a)
            fv[2 * ka + 1] -= tau * t * w * Na
            fv[2 * kb + 1] -= tau * t * w * (1 - Na)
    r = m.rozwiaz(fv)
    w_mes = -m.przemieszczenie(r, l, c)[1]
    I = t * h ** 3 / 12
    G = E / (2 * (1 + nu))
    w_b = P * l ** 3 / (3 * E * I)
    w_s = P * l / (5 / 6 * G * t * h)
    return {"l_h": l / h, "w_MES": w_mes * 1000, "w_zginanie": w_b * 1000, "w_scinanie": w_s * 1000,
            "w_Timoshenko": (w_b + w_s) * 1000, "stosunek": w_mes / (w_b + w_s), "ne": m.ne,
            "R": m.reakcje(r)["U"]["R"]}


# ==================================================================================================
# Demo — tarcza wspornikowa typowa dla wariantu W2
# ==================================================================================================
def dane_demo(siatka_opis: str = "") -> DaneTarczy:
    """Tarcza wspornikowa P2 (wariant W2): L = 13,0 m (x = −1,50…11,50), H = 3,10 m, t = 18 cm, C30/37 (XC3); podpory — ściany
    P1 (silikat 18 cm, h = 2,90 m, k = E_mur·t/h) z przerwami; wspornik 1,50 m na zachód; otwory 3 × 1,80×1,50 i 3,20×2,40 m.
    Obciążenia (charakterystyczne, przykładowe): ST3 (stropodach) na krawędzi górnej, ST2 (strop P2) podwieszony na krawędzi
    dolnej, B3 (belka krawędziowa pod lekką ścianą zach.) i okap ST3 na końcu wspornika."""
    H = 3.10
    otw = [OtworT("O1", 0.5, 2.3, 0.9, 2.4), OtworT("O4", 2.9, 6.1, 0.3, 2.7), OtworT("O2", 6.8, 8.6, 0.9, 2.4),
           OtworT("O3", 9.2, 11.0, 0.9, 2.4)]
    E_mur = 1000 * 7.66e3          # kPa — E = K_E·f_k (PN-EN 1996-1-1, K_E = 1000 [NZW]), f_k = 7,66 MPa (R5 3.6)
    k = E_mur * 0.18 / 2.90        # kN/m² na 1 m podpory
    pods = [PodporaT("A", 0.0, 2.9, 0.0, k=k, opis="ściana P1 (oś A → wsch.)", sciana="S1-A"),
            PodporaT("B", 4.4, 7.6, 0.0, k=k, opis="ściana P1", sciana="S1-B"),
            PodporaT("C", 9.2, 11.5, 0.0, k=k, opis="ściana P1", sciana="S1-C")]
    obc = [ObcLiniowe("G", -1.5, 11.5, H, 17.0, opis="ST3 — ciężar (7,0 kN/m² × 2,40 m)"),
           ObcLiniowe("S", -1.5, 11.5, H, 1.7, opis="ST3 — śnieg (0,72 × 2,40)"),
           ObcLiniowe("H", -1.5, 11.5, H, 1.0, opis="ST3 — użytkowe dachu kat. H"),
           ObcLiniowe("G", -1.5, 11.5, 0.0, 16.8, opis="ST2 — ciężar (7,0 × 2,40)"),
           ObcLiniowe("QA", -1.5, 11.5, 0.0, 6.7, opis="ST2 — użytkowe + działowe ((2,0 + 0,8) × 2,40)"),
           ObcSkupione("G", -1.35, 0.0, 18.0, opis="B3 — reakcja (ściana lekka + wspornik ST2)"),
           ObcSkupione("QA", -1.35, 0.0, 6.0, opis="B3 — reakcja"),
           ObcSkupione("G", -1.35, H, 6.0, opis="okap ST3"), ObcSkupione("S", -1.35, H, 2.0, opis="okap ST3")]
    prz = {"G": Oddz("G", "G"), "QA": Oddz("QA", "Q", "A"), "S": Oddz("S", "Q", "S", "dach"), "H": Oddz("H", "Q", "H", "dach")}
    return DaneTarczy("T-P2-1", 13.0, H, 0.18, x0=-1.5, otwory=otw, podpory=pods, obciazenia=obc, przypadki=prz, beton="C30/37",
                      ekspozycja="XC3", g_dod=0.35, fi_podpor=1.5,
                      opis="Ściana podłużna P2 (oś 1) wariantu W2 — tarcza wspornikowa przenosząca wysunięcie bryły II piętra "
                           "o 1,50 m na zachód; ściany P1 poniżej z przerwami (otwory P1).")


def walidacja_zbieznosc(siatki=(0.20, 0.10, 0.05)) -> list[dict]:
    """Zbieżność siatki tarczy demo: ugięcie wspornika (ULS, sprężyste), siła w pasie górnym (MES), reakcja A, σ₁,max."""
    out = []
    for h in siatki:
        t0 = time.time()
        an = AnalizaTarczy(dane_demo(), Parametry(), siatka=h)
        an._mes()
        an._kombinacje_i_rozwiazania()
        r = an.r_uls[an.k_gov]
        pk = [q for q in an.punkty_ugiec() if q["typ"] == "wspornik"][0]
        w = an._ugiecie_pkt(r, pk) * 1000
        an._pasy_mes()
        top = next(v for k, v in an.pasy_mes.items() if k.startswith("krawędź górna"))
        RA = an.mes.reakcje(r)["A"]["R"]
        out.append({"h": h, "ne": an.mes.ne, "w_wsp": w, "T_gora": top["F"], "R_A": RA, "R_Amax": float(an.mes.reakcje(r)["A"]["r"].max()),
                    "s1_max": float(an.s1_env.max() / 1000), "czas": time.time() - t0})
    return out


def _richardson(v: list[float]) -> tuple[float, float]:
    """(rząd zbieżności p, wartość ekstrapolowana) z trzech siatek o stosunku 2."""
    a, b, c = v
    if abs(b - c) < 1e-12 or (a - b) / (b - c) <= 0:
        return float("nan"), c
    p = math.log(abs((a - b) / (b - c))) / math.log(2)
    return p, c + (c - b) / (2 ** p - 1)


# ==================================================================================================
# Raport walidacji + demo
# ==================================================================================================
def raport_walidacji(out_dir: str | Path, zbieznosc: bool = True) -> dict:
    """Zapisuje ``walidacja_tarcz.md`` + rysunki w out_dir/rys; zwraca wyniki liczbowe."""
    from .rysunki import BLUE, GRID, INK, INK2, ORANGE, RED, _save, plt
    out = Path(out_dir)
    (out / "rys").mkdir(parents=True, exist_ok=True)
    res: dict = {}
    L = ["# Walidacja modułu ścian-tarcz (MES QM6 + STM)", "",
         "Moduły `lamela.obliczenia.konstrukcja.tarcze_mes` (MES płaskiego stanu naprężenia) i `tarcze` (STM, wymiarowanie). "
         "[P] — źródło przytoczone z pamięci; wzory ścisłe sprawdzane niezależnie (równowaga, warunki brzegowe).", ""]
    # (a1)
    kw = tg_kontrola_wzorow()
    L += ["## (a1) Rozwiązanie ścisłe — belka-tarcza obciążona równomiernie (Timoshenko & Goodier §22)", "",
          "σ_x = −q/(2I)·[(l² − x²)·z + 2z³/3 − 2c²z/5], σ_z = −q/(2I)·(−z³/3 + c²z + 2c³/3), τ_xz = q/(2I)·(c² − z²)·x, "
          "I = 2c³/3; na końcach x = ±l przyłożone trakcje z rozwiązania (σ_x samozrównoważone, τ o wypadkowej q·l).", "",
          f"Kontrola wzorów: residua równań równowagi {kw['rown_x']:.1e} / {kw['rown_z']:.1e}; σ_z(+c) = {f(kw['sz_gora'], 3)} "
          f"(= −q = −10), σ_z(−c) = {f(kw['sz_dol'], 3)}, τ(±c) = {f(kw['tau_brzeg'], 3)}; ∫τ dz na końcu = {f(kw['V_koniec'], 3)} "
          f"(= q·l = {f(kw['ql'], 3)}), ∫σ_x dz = {f(kw['N_koniec'], 4)}, ∫σ_x·z dz = {f(kw['M_koniec'], 4)}.", ""]
    rows = []
    tg_res = []
    for l_, c_ in ((1.0, 1.0), (1.0, 0.5), (2.0, 0.5)):
        for h in (0.2, 0.1, 0.05):
            r = walidacja_tg(l_, c_, 100.0, h * c_)
            tg_res.append(r)
            rows.append([f(l_ / c_, 1), f(h / 2, 3), r["ne"], f(r["err_sx"] * 100, 2) + " %", f(r["err_sz"] * 100, 2) + " %",
                         f(r["err_tau"] * 100, 2) + " %", f"{r['R_resztkowe']:.1e}"])
    res["tg"] = tg_res
    L += [tabela(["l/h (rozpiętość 2l / wysokość 2c)", "h_el/h", "n_el", "max|Δσ_x|/max|σ_x|", "max|Δσ_z|/q", "max|Δτ|/max|τ|",
                  "reakcje resztkowe [kN]"], rows), ""]
    L += ["Błędy mierzone w środkach wszystkich elementów (także przy krawędziach obciążonych). Zbieżność liniowa w h dla σ_z "
          "(obciążenie krawędziowe), dla σ_x — błąd < 0,5 % już przy 10 elementach na wysokości.", ""]
    # wykres profilu
    fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.6))
    for ax, r in zip(axs, [tg_res[2], tg_res[5]]):
        zp, sp, se = r["profil"]
        ax.plot(se / 1000, zp, color=INK, lw=1.4, label="ścisłe (T&G)")
        ax.plot(sp / 1000, zp, "o", ms=3, color=ORANGE, label="MES QM6")
        ax.axvline(0, color=INK2, lw=0.5)
        ax.set_xlabel("σ_x [MPa] (x = 0)")
        ax.set_ylabel("z [m]")
        ax.grid(color=GRID, lw=0.4)
        ax.set_title(f"l/h = {r['l_h']:g}: σ_x w środku rozpiętości", loc="left")
        ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    _save(fig, out / "rys" / "walidacja_tg.png")
    L += ["![Profil σ_x — MES vs rozwiązanie ścisłe](rys/walidacja_tg.png)", ""]
    # (a2)
    L += ["## (a2) Belka-ściana jednoprzęsłowa — ramię sił wewnętrznych i siła w ściągu", "",
          "Rozpiętość l = 3,0 m (osie podpór), podpory szer. 0,1·l, obciążenie q = 100 kN/m od góry, t = 0,20 m. MES — przekrój "
          "w środku rozpiętości: M z całkowania σ_x, T — wypadkowa strefy rozciąganej przy krawędzi dolnej, z = M/T. Reguła "
          "projektowa CEB-FIP / DAfStb Heft 240 [P] (wyprowadzona z analiz sprężystych Leonhardta i Walthera, Heft 178 [P]): "
          "z = 0,2·(l + 2h) dla 1 ≤ l/h < 2, z = 0,6·l dla l/h < 1; `zelbet.belka_sciana` — ta sama reguła (dla l/h ≥ 2 ogranicza "
          "z do 0,9·d). STM — maks. siła w cięgnie dolnym modelu wygenerowanego automatycznie.", ""]
    rows = []
    bs_res = []
    for lh in (0.75, 1.0, 1.5, 2.0, 3.0):
        r = walidacja_belka_sciana(3.0, lh, 100.0, 0.2, 0.05, stm=True)
        bs_res.append(r)
        rows.append([f(lh, 2), f(r["h"], 2), (r["x_R"], 3), (r["M_MES"], 1), (r["M_statyka"], 1), (r["M_nominalny"], 1), (r["z_MES"], 3), (r["z_CEB"], 3),
                     f((r['z_MES'] / r['z_CEB'] - 1) * 100, 1) + " %", (r["T_MES"], 1), (r["T_belka_sciana"], 1), (r.get("T_STM", float("nan")), 1),
                     (r["h_rozc"] / r["h"], 3)])
    res["belka_sciana"] = [{k: v for k, v in r.items() if k not in ("prof", "stm_an")} for r in bs_res]
    L += [tabela(["l/h", "h [m]", "x_R [m]", "M_MES [kNm]", "M_statyka [kNm]", "q(l²−a²)/8 [kNm]", "z_MES [m]", "z_CEB [m]", "Δz", "T_MES [kN]",
                  "T belka_sciana [kN]", "T_STM [kN]", "h_rozc/h"], rows), ""]
    dz = [abs(r["z_MES"] / r["z_CEB"] - 1) for r in bs_res if r["l_h"] <= 1.5]
    r2 = next(r for r in bs_res if abs(r["l_h"] - 2.0) < 1e-9)
    dT = [abs(r["T_MES"] / r["T_belka_sciana"] - 1) for r in bs_res if r["l_h"] <= 2.0]
    L += ["x_R — środek reakcji podpory A z MES (podpora sztywna szer. 0,3 m: reakcja skupia się przy krawędzi wewnętrznej, stąd "
          "M < q(l² − a²)/8 liczone dla reakcji w osi podpory); M_statyka — z reakcji MES = M z całkowania naprężeń.", "",
          f"Wnioski: dla l/h = 0,75…1,5 sprężyste ramię sił wewnętrznych z_MES różni się od reguły CEB-FIP/DAfStb o ≤ "
          f"{f(max(dz) * 100, 1)} % (reguła jest zaokrągleniem analiz sprężystych Leonhardta [P]); dla l/h = 2 reguła daje ramię "
          f"{f(r2['z_CEB'] / r2['h'], 2)}·h wobec sprężystego {f(r2['z_MES'] / r2['h'], 2)}·h. Siła w ściągu z `zelbet.belka_sciana` "
          f"(M = q·l²/8 dla osi podpór) różni się od sprężystej wypadkowej T_MES o ≤ {f(max(dT) * 100, 1)} % dla l/h ≤ 2. "
          "Dla l/h = 3 (granica belki-ściany, 5.3.1(3)) z_MES → 0,67·h (liniowy rozkład σ_x — teoria belek). Strefa rozciągana "
          "przy krawędzi dolnej: 0,20·h (l/h = 0,75) … 0,5·h (l/h = 3) — por. rozkłady Leonhardta [P]. STM (dolne rozwiązanie "
          "plastyczne) daje ściąg mniejszy od sprężystego dla tarcz krępych (większe ramię), dla l/h ≥ 2 — zbliżony.", ""]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    for r, col in zip(bs_res, (INK, BLUE, ORANGE, RED, INK2)):
        zp, sp = r["prof"]
        ax.plot(sp, np.array(zp) / r["h"], color=col, lw=1.2, label=f"l/h = {r['l_h']:g}")
    ax.axvline(0, color=INK2, lw=0.5)
    ax.set_xlabel("σ_x [MPa] w środku rozpiętości (q = 100 kN/m, t = 0,2 m)")
    ax.set_ylabel("z/h")
    ax.grid(color=GRID, lw=0.4)
    ax.legend(fontsize=7, frameon=False)
    ax.set_title("Belka-ściana: nieliniowy rozkład σ_x (MES) — por. Leonhardt [P]", loc="left")
    fig.tight_layout()
    _save(fig, out / "rys" / "walidacja_belka_sciana.png")
    L += ["![Rozkład σ_x w belce-ścianie](rys/walidacja_belka_sciana.png)", ""]
    # (b)
    L += ["## (b) Wspornik — zgodność z teorią belek dla wspornika smukłego", "",
          "Wspornik h = 0,5 m, t = 0,2 m, utwierdzony w ścianie poprzecznej (u_x = u_z = 0 na całej wysokości), siła P = 100 kN "
          "na końcu (trakcja paraboliczna). Odniesienie: belka Timoshenki w = P·l³/(3EI) + P·l/(κGA), κ = 5/6, ν = 0,2.", ""]
    rows = []
    ws_res = []
    for lh in (0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 20.0):
        r = walidacja_wspornik(lh * 0.5)
        ws_res.append(r)
        rows.append([f(lh, 1), (r["w_zginanie"], 4), (r["w_scinanie"], 4), (r["w_Timoshenko"], 4), (r["w_MES"], 4),
                     f(r["stosunek"], 3), (r["R"], 2)])
    res["wspornik"] = ws_res
    L += [tabela(["l/h", "w_M [mm]", "w_V [mm]", "w_Timoshenko [mm]", "w_MES [mm]", "MES/belka", "R [kN]"], rows), ""]
    sm = [r for r in ws_res if r["l_h"] >= 5]
    kr = [r for r in ws_res if r["l_h"] <= 1]
    L += [f"Wspornik smukły (l/h ≥ 5): MES = teoria belek z dokładnością {f(max(abs(r['stosunek'] - 1) for r in sm) * 100, 2)} % "
          "(granica l/h → ∞ osiągnięta; reszta — sztywne utwierdzenie całego przekroju blokujące deplanację). Wsporniki krępe "
          f"(l/h ≤ 1): odchylenie od belki Timoshenki ≤ {f(max(abs(r['stosunek'] - 1) for r in kr) * 100, 1)} %, ale udział "
          "odkształceń postaciowych w ugięciu rośnie do ≈ 75 % (l/h = 0,5: teoria Eulera–Bernoulliego zaniża ugięcie ≈ 4×), a "
          "rozkład naprężeń jest nieliniowy (D-obszar) — stąd wymiarowanie tarczy wspornikowej modelem STM, a nie belkowo.", ""]
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    ax.semilogx([r["l_h"] for r in ws_res], [r["stosunek"] for r in ws_res], "o-", color=INK, lw=1.2)
    ax.axhline(1.0, color=INK2, lw=0.6, ls="--")
    ax.set_xlabel("l/h wspornika")
    ax.set_ylabel("w_MES / w_Timoshenko")
    ax.grid(color=GRID, lw=0.4, which="both")
    ax.set_title("Wspornik: MES vs teoria belek (granica smukła)", loc="left")
    fig.tight_layout()
    _save(fig, out / "rys" / "walidacja_wspornik.png")
    L += ["![Wspornik — MES vs belka](rys/walidacja_wspornik.png)", ""]
    # (c)
    if zbieznosc:
        zb = walidacja_zbieznosc()
        res["zbieznosc"] = zb
        rows = [[f(r["h"], 2), r["ne"], (r["w_wsp"], 4), (r["T_gora"], 2), (r["R_A"], 2), (r["R_Amax"], 1), (r["s1_max"], 3),
                 f(r["czas"], 1)] for r in zb]
        def rich(v):
            if abs(v[2] - v[1]) <= 1e-3 * abs(v[2]):
                return "zbieżne (zmiana < 0,1 %)"
            p_, e_ = _richardson(v)
            return f"→ {f(e_, 4 if abs(e_) < 10 else 2)} (rząd {f(p_, 2)})"
        L += ["## (c) Zbieżność siatki — tarcza demo (kombinacja miarodajna STR)", "",
              tabela(["h_el [m]", "n_el", "w_wspornika [mm]", "T pasa górnego (MES) [kN]", "R_A [kN]", "r_A,max [kN/m]",
                      "σ₁,max [MPa]", "czas [s]"], rows), "",
              f"Ekstrapolacja Richardsona: w_wsp {rich([r['w_wsp'] for r in zb])} mm, T {rich([r['T_gora'] for r in zb])} kN, "
              f"R_A {rich([r['R_A'] for r in zb])}. Wielkości całkowe (ugięcie, reakcje, momenty, siły w pasach) zbieżne — "
              "różnica h = 0,10 vs 0,05 m ≤ 2 %; σ₁,max i szczyt reakcji r_A,max rosną z zagęszczaniem (osobliwość w narożach wklęsłych otworów — "
              "dlatego wymiarowanie opiera się na wypadkowych, nie na wartościach szczytowych).", ""]
    # (d)
    an = AnalizaTarczy(dane_demo(), Parametry(), siatka=0.10)
    an._mes()
    an._kombinacje_i_rozwiazania()
    an._rownowaga()
    errs = []
    for n, r in an.r_uls.items():
        F = -float(r.f[1::2].sum())
        R = float(r.R[1::2].sum())
        errs.append(abs(F - R) / F)
    res["rownowaga"] = {"max_bl_sum": max(errs), "max_bl_przekroje": an.blad_przekrojow}
    L += ["## (d) Równowaga", "", f"ΣR_z = ΣF_z we wszystkich {len(errs)} kombinacjach STR — maks. błąd względny {max(errs):.1e}. "
          f"Siły w przekrojach pionowych (całkowanie σ_x, τ) vs statyka części tarczy — maks. rozbieżność "
          f"{an.blad_przekrojow * 100:.3f} %.", "", an.tabele[0], ""]
    (out / "walidacja_tarcz.md").write_text("\n".join(L), encoding="utf-8")
    return res


def demo(out_dir: str | Path, walidacja: bool = True, status: str | None = None) -> dict:
    """Demo: obliczenia tarczy wspornikowej wariantu W2 → raport w out_dir (+ walidacja)."""
    from .tarcze import oblicz_tarcze
    out = Path(out_dir)
    t0 = time.time()
    wt = oblicz_tarcze(dane_demo(), Parametry.z_wymagan(), siatka=0.10)
    dod = ["## Walidacja", "", "Szczegóły: [walidacja_tarcz.md](walidacja_tarcz.md) — (a) rozwiązanie ścisłe i belka-ściana, "
           "(b) wspornik smukły, (c) zbieżność siatki, (d) równowaga."] if walidacja else []
    fmd = raport_tarczy(wt, out, tytul="Obliczenia statyczne — ściana-tarcza wspornikowa P2 (wariant W2, demo)",
                        status=status or "DEMO — dane przykładowe typowe dla wariantu W2; nie jest pozycją projektu wykonawczego",
                        dodatki=dod)
    res = {"raport": str(fmd), "wynik": wt.dane(), "czas": time.time() - t0}
    if walidacja:
        res["walidacja"] = raport_walidacji(out)
    return res
