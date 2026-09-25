"""Obwody instalacji elektrycznej: WLZ (ZKP → RG), obwody odbiorcze, dobór przekrojów i zabezpieczeń, spadki napięć,
impedancja pętli zwarcia i samoczynne wyłączenie, selektywność, RCD, SPD (CRL), kategorie udarowe, PWP.

Podstawy (W-180…W-190, R7 §3.1–3.9):

* **PN-HD 60364-5-52:2011** zał. B — I_z(metoda ułożenia, liczba żył obciążonych)·k_θ·k_grup (moduł ``tabele`` [NZW]);
  min. przekroje 1,5 mm² (oświetlenie, sterowanie siłowe), 2,5 mm² (gniazda) — W-184; WT §183 ust. 1 pkt 9 — Cu ≤ 10 mm².
* **PN-HD 60364-4-43:2024-04 p. 433.1** — **I_B ≤ I_n ≤ I_z; I₂ ≤ 1,45·I_z** (W-182 [NZW brzmienie]); dla wyłączników
  PN-EN 60898-1 I₂ = 1,45·I_n.
* **Spadki napięć** — ZKP → odbiornik ≤ 3 %, w tym ZKP → RG ≤ 0,5 % (W-185, N SEP-E-002 [NZW]); ∆U obliczane z
  rezystancją żył w temperaturze roboczej θ = θ_a + (70 − θ_a)·(I_B/I_z)²; obwody gniazd z I_B = I_n (R7 §3.3) [ZAŁ].
* **PN-HD 60364-4-41:2017-09** — układ TN-S (W-180), samoczynne wyłączenie w **t ≤ 0,4 s** (tabl. 41.1) dla obwodów
  końcowych ≤ 63 A z gniazdami i ≤ 32 A odbiorników stałych: **Z_s·I_a ≤ U₀** — I_a = 5·I_n (B), 10·I_n (C) (wyzwalacz
  elektromagnetyczny, t ≤ 0,1 s); I_k1,min = c_min·U₀/Z_s, c_min = 0,95 (PN-EN 60909-0), rezystancje żył w 70 °C [UPR];
  impedancja pętli w ZKP Z_Q — z warunków przyłączenia (RSys §4 ust. 2 pkt 17) [ZAŁ].
* **RCD 30 mA** — gniazda ≤ 32 A (411.3.3), oświetlenie w lokalu (411.3.4), łazienki (7-701), EV — typ B / A-EV + RDC-DD
  (7-722), falownik PV — typ B lub wg 712.530.3.101; typ AC niedopuszczalny (W-181).
* **SPD** — WT §183 ust. 1 pkt 10; PN-HD 60364-4-443:2016 p. 443.5: **CRL = f_env/(L_P·N_g)**, CRL < 1000 → SPD; typ 1+2
  w RG, I_imp ≥ 12,5 kA/biegun, U_p ≤ 2,5 kV (zalecane ≤ 1,5 kV); kategorie wytrzymałości udarowej IV 6 kV / III 4 kV /
  II 2,5 kV / I 1,5 kV (tabl. 443.2) (W-186).
* **Selektywność** — WT §183 ust. 1 pkt 5: przeciążeniowa (I_n,wyż/I_n,niż ≥ 1,6 [W]), zwarciowa do granicy I_s (tabele
  producenta; zachowawczo I_s = I_a,min zabezpieczenia wyższego = 5·I_n dla C [UPR]); RCD — brak RCD grupowego nad RCBO.
* **PWP** — WT §183 ust. 2–4 (strefa pożarowa > 1000 m³) vs ROPoż §4 ust. 2 pkt 2 — **projektować** (D-04, W-190).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import DaneBudynku, Krok, Raport, Warunek, ceil_to, f, fa, manhattan, wym, wym_zrodlo
from . import tabele as T
from .bilans import U0, UN, Odbiornik


@dataclass
class ParametryObwody:
    Z_Q: float = 0.30                  # Ω — impedancja pętli zwarcia w ZKP (L–PEN) [ZAŁ — warunki przyłączenia]
    I_k_ZKP_max: float = 6.0           # kA — maks. prąd zwarciowy w ZKP [ZAŁ]
    zab_przedlicznikowe: str = "C"     # ENEA: wyłącznik nadprądowy C (R7-L06)
    WLZ_przekroj: float = 25.0         # mm² — 16 mm² nie spełnia ∆U ZKP→RG ≤ 0,5 % (weryfikacja PT, I-5)
    WLZ_zyly: int = 5                  # 5 — rozdział PEN w ZKP (preferowany, D-12); 4 — PEN, rozdział w RG
    WLZ_metoda: str = "D1"
    WLZ_zapas: float = 5.0             # m
    theta_pow: float = 30.0
    theta_grunt: float = 20.0
    n_grupowanych: int = 2             # obwody prowadzone razem przy RG [ZAŁ]
    dU_max: float | None = None        # % (W-185)
    dU_WLZ_max: float | None = None
    L_wsp: float = 1.2                 # współczynnik trasy (odległość „miejska” × 1,2) [UPR]
    L_pionowe: float = 3.0             # m — zejścia/podejścia w ścianach [UPR]
    s_max: float = 10.0
    L_P_km: float = 0.30               # długość linii nN OSD do pierwszego SPD w sieci [ZAŁ] (443.5)
    F_env: float | None = None
    t_wyl: float = 0.4
    rezerwa: float = 0.2


@dataclass
class Obwod:
    odb: Odbiornik
    L: float
    I_B: float
    I_n: int
    char: str
    s: float
    metoda: str
    n_obc: int
    I_z: float
    dU: float
    dU_calk: float
    Z_s: float
    I_k1: float
    I_a: float
    I_k3_pocz: float
    theta: float
    uwagi: list = field(default_factory=list)

    @property
    def przewod(self) -> str:
        n = 5 if self.odb.fazy == 3 else 3
        typ = "YKY" if self.metoda.startswith("D") else ("YDY" if self.odb.grupa == "ev" else "YDYp")
        return f"{typ} {n}×{f(self.s, 1).replace(',0', '')}"

    @property
    def zab(self) -> str:
        p = "3P " if self.odb.fazy == 3 else ""
        return f"{p}{self.char}{self.I_n}"


@dataclass
class WynikObwody:
    dane: DaneBudynku
    par: ParametryObwody
    obwody: list
    wlz: dict
    rg_xy: tuple
    zkp_xy: tuple
    spd: dict
    pwp: dict
    selektywnosc: list
    warunki: list
    kroki: dict
    zalozenia: list

    def do_dict(self) -> dict:
        return {"WLZ": self.wlz["przewod"], "dU_WLZ_proc": round(self.wlz["dU"], 3), "obwody": len(self.obwody),
                "dU_max_proc": round(max((o.dU_calk for o in self.obwody), default=0), 2),
                "Z_s_max_ohm": round(max((o.Z_s for o in self.obwody), default=0), 3), "CRL": round(self.spd["CRL"], 0),
                "PWP": self.pwp["decyzja"]}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def _polozenie_rg(dane: DaneBudynku) -> tuple:
    l = dane.lok("RG")
    if l:
        return l
    t = [p for p in dane.pomieszczenia if p.rodzaj == "techniczne"]
    if t:
        return (*t[0].centroid, t[0].kond)
    h = [p for p in dane.pomieszczenia if p.rodzaj == "ruchu" and p.kond == dane.kondygnacje[0]["id"]]
    p = h[0] if h else dane.pomieszczenia[0]
    return (*p.centroid, p.kond)


def _polozenie_zkp(dane: DaneBudynku, rg) -> tuple:
    l = dane.lok("ZKP")
    if l:
        return l[:2]
    br = [b for b in dane.dzialka.get("bramy") or [] if b.get("typ") == "furtka"] or (dane.dzialka.get("bramy") or [])
    if br:
        x, y = br[0]["xy_bud"]
        return (x + 1.0, y)
    return (rg[0], rg[1] + 15.0)


def dU_proc(I: float, L: float, s: float, fazy: int, cosphi: float, theta: float) -> float:
    """∆U% = k·L·I·(r·cos φ + x·sin φ)/U·100; k = 2 (1f, U = U₀) lub √3 (3f, U = U_n)."""
    r = T.r_zyly(s, theta)
    sinphi = math.sqrt(max(0.0, 1 - cosphi ** 2))
    if fazy == 3:
        return math.sqrt(3) * L * I * (r * cosphi + T.X_KABLA * sinphi) / UN * 100.0
    return 2.0 * L * I * (r * cosphi + T.X_KABLA * sinphi) / U0 * 100.0


def oblicz_obwody(dane: DaneBudynku, odbiorniki: list[Odbiornik], par: ParametryObwody | None = None,
                  I_zab: float = 40.0) -> WynikObwody:
    par = par or ParametryObwody()
    dUmax = par.dU_max if par.dU_max is not None else float(wym("elektryka", "spadek_napiecia_ZKP_odbiornik_max", 3.0) or 3.0)
    dUwlz_max = par.dU_WLZ_max if par.dU_WLZ_max is not None else float(wym("elektryka", "spadek_napiecia_ZKP_RG_max", 0.5) or 0.5)
    t_max = float(wym("elektryka", "czas_wylaczenia_TN_230V_max", 0.4) or 0.4)
    war: list[Warunek] = []
    kroki: dict[str, list] = {}
    rg = _polozenie_rg(dane)
    zkp = _polozenie_zkp(dane, rg)
    # ---- WLZ
    L_w = par.L_wsp * manhattan(zkp, rg[:2]) + par.WLZ_zapas
    s_w = par.WLZ_przekroj
    kt = T.k_temp(par.WLZ_metoda, par.theta_grunt)
    Iz_w = T.iz(par.WLZ_metoda, 3, s_w) * kt
    dU_w = dU_proc(I_zab, L_w, s_w, 3, 1.0, 20.0)
    dU_w70 = dU_proc(I_zab, L_w, s_w, 3, 1.0, par.theta_grunt + (70 - par.theta_grunt) * (I_zab / Iz_w) ** 2)
    R_w = 2 * L_w * T.r_zyly(s_w, 70.0)
    X_w = 2 * L_w * T.X_KABLA
    wlz = {"przewod": f"YKY {par.WLZ_zyly}×{f(s_w, 0)}", "L": L_w, "I_z": Iz_w, "dU": dU_w70, "dU20": dU_w, "R": R_w,
           "metoda": par.WLZ_metoda}
    Zq = par.Z_Q
    Ik3_rg = min(par.I_k_ZKP_max * 1000, 1.1 * U0 / (Zq / 2 + L_w * T.r_zyly(s_w, 20)))
    kroki["wlz"] = [
        Krok("Długość WLZ (ZKP → RG)", "L = 1,2·(|∆x| + |∆y|) + zapas", f"1,2·{f(manhattan(zkp, rg[:2]), 2)} + {f(par.WLZ_zapas, 1)}", L_w, "m", "[UPR]", 1),
        Krok(f"Obciążalność YKY {par.WLZ_zyly}×{f(s_w, 0)} ({par.WLZ_metoda}, 3 żyły obc., θ_gr = {f(par.theta_grunt, 0)} °C)", "I_z = I_z,tab·k_θ",
             f"{f(T.iz(par.WLZ_metoda, 3, s_w), 0)}·{f(kt, 2)}", Iz_w, "A", "PN-HD 60364-5-52 tabl. B.52.4 [NZW]", 1),
        Krok("Spadek napięcia WLZ przy I = I_zab (20 °C — por. R7 §3.1)", "∆U = √3·L·I·r/U_n·100", f"√3·{f(L_w, 1)}·{f(I_zab, 0)}·{fa(T.r_zyly(s_w, 20), 4)}/400·100",
             dU_w, "%", "", 3),
        Krok("Spadek napięcia WLZ w temperaturze roboczej", "∆U(θ)", "", dU_w70, "%", "W-185: ≤ 0,5 %", 3),
    ]
    war.append(Warunek("WLZ: I_n (zabezpieczenie przedlicznikowe) ≤ I_z", I_zab, "<=", Iz_w, "A", "PN-HD 60364-4-43", "W-182", nd=0))
    war.append(Warunek("WLZ: obciążalność ≥ 50 A", Iz_w, ">=", float(wym("elektryka", "WLZ_obciazalnosc_min", 50) or 50), "A",
                       wym_zrodlo("elektryka", "WLZ_obciazalnosc_min"), "W-185", nd=0))
    war.append(Warunek("WLZ: spadek napięcia ZKP → RG", dU_w70, "<=", dUwlz_max, "%", wym_zrodlo("elektryka", "spadek_napiecia_ZKP_RG_max"),
                       "W-185", nd=2))
    # ---- obwody
    kg = T.k_grup(par.n_grupowanych)
    obw: list[Obwod] = []
    for o in odbiorniki:
        lok = o.lok or rg
        dz = abs(dane.rzedna(lok[2]) - dane.rzedna(rg[2])) if len(lok) > 2 else 0.0
        L = par.L_wsp * manhattan(rg[:2], lok[:2]) + dz + par.L_pionowe + o.L_dodatkowa
        I_B = o.I_B
        if o.typ_obwodu == "gniazda":
            I_B = max(I_B, float(o.In_min))
        I_n = int(ceil_to(max(I_B, o.In_min), T.SZEREG_IN) or 63)
        if o.typ_obwodu == "gniazda":
            I_B = float(I_n)
        met = o.metoda
        n_obc = 3 if o.fazy == 3 else 2
        kt = T.k_temp(met, par.theta_grunt if met.startswith("D") else par.theta_pow)
        uw = []
        s_sel = None
        for s in T.PRZEKROJE:
            if s < o.s_min or s > par.s_max:
                continue
            Iz = T.iz(met, n_obc, s) * kt * kg
            if I_n > Iz:
                continue
            th = (par.theta_pow if not met.startswith("D") else par.theta_grunt) + (70 - par.theta_pow) * (I_B / Iz) ** 2
            dU = dU_proc(I_B, L, s, o.fazy, o.cosphi if o.typ_obwodu != "gniazda" else 1.0, th)
            if dU + dU_w70 > dUmax:
                if s_sel is None:
                    uw.append(f"przekrój zwiększony ze względu na ∆U")
                s_sel = s_sel or s
                continue
            s_sel = s
            break
        else:
            s = s_sel or par.s_max
            Iz = T.iz(met, n_obc, s) * kt * kg
            th = par.theta_pow + (70 - par.theta_pow) * min(1.0, (I_B / Iz)) ** 2
            dU = dU_proc(I_B, L, s, o.fazy, o.cosphi, th)
            uw.append("∆U przekroczony przy s_max — rozważyć podrozdzielnicę")
        # impedancja pętli (L–PE): Z_Q + WLZ + obwód; rezystancje w 70 °C
        R_o = 2 * L * T.r_zyly(s, 70.0)
        X_o = 2 * L * T.X_KABLA
        Zs = math.hypot(Zq * 0.9 + R_w + R_o, Zq * 0.44 + X_w + X_o)
        Ik1 = 0.95 * U0 / Zs
        Ia = T.MNOZNIK_IA[o.char] * I_n
        obw.append(Obwod(odb=o, L=L, I_B=I_B, I_n=I_n, char=o.char, s=s, metoda=met, n_obc=n_obc, I_z=Iz, dU=dU,
                         dU_calk=dU + dU_w70, Z_s=Zs, I_k1=Ik1, I_a=Ia, I_k3_pocz=Ik3_rg, theta=th, uwagi=uw))
        war.append(Warunek(f"{o.id}: I_B ≤ I_n ≤ I_z", I_n, "zakres", (round(I_B, 2), round(Iz, 2)), "A", "PN-HD 60364-4-43 p. 433.1",
                           "W-182", nd=1))
        war.append(Warunek(f"{o.id}: ∆U ZKP → odbiornik", dU + dU_w70, "<=", dUmax, "%", "N SEP-E-002 [NZW]", "W-185", nd=2))
        war.append(Warunek(f"{o.id}: samoczynne wyłączenie (I_k1 ≥ I_a = {f(T.MNOZNIK_IA[o.char], 0)}·I_n, t ≤ {f(t_max, 1)} s)", Ik1, ">=", Ia,
                           "A", "PN-HD 60364-4-41 tabl. 41.1", "W-182", nd=0))
    # I₂ ≤ 1,45·I_z — wyłączniki PN-EN 60898: I₂ = 1,45·I_n → spełnione, gdy I_n ≤ I_z (sprawdzone wyżej)
    # ---- przykład obliczeń (najdłuższy obwód gniazd)
    gn = [x for x in obw if x.odb.typ_obwodu == "gniazda"]
    ob = max(gn, key=lambda x: x.L) if gn else obw[0]
    kroki["przyklad"] = [
        Krok(f"Obwód {ob.odb.id} ({ob.odb.nazwa}) — długość", "L = 1,2·(|∆x| + |∆y|) + |∆z| + 3 m", "", ob.L, "m", "[UPR]", 1),
        Krok("Prąd obliczeniowy", "I_B = I_n (obwód gniazd)" if ob.odb.typ_obwodu == "gniazda" else "I_B = P/(U·cos φ)", "", ob.I_B, "A",
             "R7 §3.3", 1),
        Krok(f"Obciążalność {ob.przewod} ({ob.metoda}), k_θ·k_grup", "I_z = I_z,tab·k_θ·k_gr",
             f"{f(T.iz(ob.metoda, ob.n_obc, ob.s), 1)}·{f(T.k_temp(ob.metoda, par.theta_pow), 2)}·{f(kg, 2)}", ob.I_z, "A",
             "PN-HD 60364-5-52 [NZW]", 1),
        Krok("Warunek przeciążeniowy", "I_B ≤ I_n ≤ I_z; I₂ = 1,45·I_n ≤ 1,45·I_z", f"{f(ob.I_B, 1)} ≤ {ob.I_n} ≤ {f(ob.I_z, 1)}",
             "spełniony" if ob.I_B <= ob.I_n <= ob.I_z else "NIE", "", "PN-HD 60364-4-43 p. 433.1"),
        Krok("Temperatura żył przy I_B", "θ = θ_a + (70 − θ_a)·(I_B/I_z)²", f"{f(par.theta_pow, 0)} + 40·({f(ob.I_B, 1)}/{f(ob.I_z, 1)})²",
             ob.theta, "°C", "", 1),
        Krok("Spadek napięcia w obwodzie", "∆U = 2·L·I_B·r_θ/U₀·100", f"2·{f(ob.L, 1)}·{f(ob.I_B, 1)}·{fa(T.r_zyly(ob.s, ob.theta), 4)}/230·100",
             ob.dU, "%", "", 2),
        Krok("Spadek całkowity ZKP → odbiornik", "∆U_c = ∆U_WLZ + ∆U", f"{f(dU_w70, 3)} + {f(ob.dU, 3)}", ob.dU_calk, "%", "W-185 (≤ 3 %)", 2),
        Krok("Impedancja pętli zwarcia (70 °C)", "Z_s = |Z_Q + Z_WLZ + Z_obw|", f"Z_Q = {f(Zq, 2)} Ω; R_WLZ = {f(R_w, 3)} Ω; R_obw = {f(2 * ob.L * T.r_zyly(ob.s, 70), 3)} Ω",
             ob.Z_s, "Ω", "", 3),
        Krok("Prąd zwarcia jednofazowego", "I_k1 = 0,95·U₀/Z_s", f"0,95·230/{f(ob.Z_s, 3)}", ob.I_k1, "A", "PN-EN 60909-0 (c_min)", 0),
        Krok("Warunek samoczynnego wyłączenia", f"I_k1 ≥ I_a = {f(T.MNOZNIK_IA[ob.char], 0)}·I_n", f"{f(ob.I_k1, 0)} ≥ {f(ob.I_a, 0)}",
             "spełniony" if ob.I_k1 >= ob.I_a else "NIE", "", "PN-HD 60364-4-41 tabl. 41.1 (t ≤ 0,1 s < 0,4 s)"),
    ]
    # ---- zwarcia maks. i zdolność łączeniowa
    war.append(Warunek("Prąd zwarciowy w RG ≤ zdolność łączeniowa aparatów (6 kA)", Ik3_rg / 1000.0, "<=", 6.0, "kA", "PN-EN 60898-1 (I_cn)",
                       "W-180", nd=2))
    # ---- selektywność
    sel = []
    I_s = T.MNOZNIK_IA[par.zab_przedlicznikowe] * I_zab * 0.5   # dolna granica wyzwalacza C = 5·I_n
    grupy_zab: dict = {}
    for x in obw:
        grupy_zab.setdefault(x.zab, []).append(x.odb.id)
    for zab, ids in grupy_zab.items():
        xx = next(x for x in obw if x.zab == zab)
        prz = I_zab / xx.I_n >= 1.6
        sel.append([zab, ", ".join(ids), f"{par.zab_przedlicznikowe}{int(I_zab)}", f"tak ({f(I_zab / xx.I_n, 1)})" if prz else "NIE",
                    f"do {f(I_s, 0)} A (I_k,max w RG ≈ {f(Ik3_rg, 0)} A)", "częściowa" if Ik3_rg > I_s else "pełna"])
    for x in obw:
        prz = I_zab / x.I_n >= 1.6
        if not prz:
            war.append(Warunek(f"{x.odb.id}: selektywność przeciążeniowa (I_n,ZKP/I_n ≥ 1,6)", I_zab / x.I_n, ">=", 1.6, "", "WT §183 ust. 1 pkt 5",
                               "W-180"))
    # ---- SPD (443.5)
    f_env = par.F_env if par.F_env is not None else float(wym("elektryka", "CRL_f_env", 170) or 170)
    Ng = float(wym("elektryka", "Ng", 1.8) or 1.8)
    CRL = f_env / (par.L_P_km * Ng)
    L_gr = f_env / (1000.0 * Ng) * 1000.0
    spd = {"CRL": CRL, "f_env": f_env, "Ng": Ng, "L_P": par.L_P_km, "L_gr_m": L_gr,
           "RG": "SPD typ 1+2 (T1+T2), I_imp ≥ 12,5 kA/biegun, U_p ≤ 1,5 kV, U_c ≥ 275 V; układ 3+1 (TN-S) lub 4+0 przy rozdziale PEN w RG",
           "DC": "SPD typ 2 DC przy falowniku (U_CPV ≥ U_oc,max łańcucha) — jeśli nie wbudowany w falownik",
           "tele": "SPD na wejściu linii miedzianych / antenowych (światłowód dielektryczny — bez SPD)",
           "T3": "ochrona lokalna T3 przy RACK i sterowniku PC (opcjonalnie)"}
    kroki["spd"] = [
        Krok("Współczynnik środowiskowy (tereny podmiejskie, F = 2)", "f_env = 85·F", "85·2", f_env, "", "443.5, odsyłacz krajowy (RST 2018) [NZW]", 0),
        Krok("Obliczeniowy poziom ryzyka CRL (PN-HD 60364-4-443 p. 443.5)", "CRL = f_env/(L_P·N_g)", f"{f(f_env, 0)}/({f(par.L_P_km, 2)}·{f(Ng, 1)})", CRL, "",
             "PN-HD 60364-4-443:2016 p. 443.5; L_P [ZAŁ]", 0),
        Krok("Graniczna długość linii kablowej nN, przy której CRL = 1000", "L = f_env/(1000·N_g)", "", L_gr, "m", "", 0),
    ]
    war.append(Warunek("SPD wymagany: CRL < 1000 (443.5) — niezależnie wymagany przez WT §183 ust. 1 pkt 10", CRL, "<", 1000.0, "",
                       "PN-HD 60364-4-443 p. 443.5; WT §183 ust. 1 pkt 10", "W-186", nd=0))
    war.append(Warunek("U_p SPD w RG ≤ wytrzymałość kat. II", 1.5, "<=", float(wym("elektryka", "SPD_Up_max", 2.5) or 2.5), "kV",
                       "PN-HD 60364-4-443 tabl. 443.2", "W-186", nd=1))
    # ---- PWP
    V = dane.kubatura
    prog = float(wym("elektryka", "PWP_kubatura_strefy_prog", 1000) or 1000)
    pwp = {"kubatura": V, "prog": prog, "wymagany_WT": V > prog,
           "decyzja": "PROJEKTOWAĆ (rekomendacja D-04 — spełnia WT §183 ust. 2 i jest zgodne z ROPoż)",
           "opis": ("Przycisk PWP przy wejściu głównym / ZKP, oznakowany (WT §183 ust. 4); działa na wyzwalacz wzrostowy lub napęd "
                    "aparatu głównego RG (rozłącznik z wyzwalaczem / wyłącznik selektywny) i odłącza wszystkie obwody, w tym AC "
                    "falownika PV; strona DC PV pozostaje pod napięciem — tabliczka ostrzegawcza przy RG, PWP i falowniku; "
                    "zadziałanie PWP nie może załączać innego źródła (§183 ust. 3); obwód sterowniczy PWP monitorowany "
                    "(wyzwalacz wzrostowy z kontrolą ciągłości lub zanikowy) [ZAŁ].")}
    war.append(Warunek(f"PWP: kubatura strefy pożarowej {f(V, 0)} m³ — wymagany wg WT §183 ust. 2: {'TAK' if V > prog else 'NIE'} "
                       f"(próg {f(prog, 0)} m³); projektowany niezależnie (D-04)", V, "info", prog, "m³",
                       "WT §183 ust. 2; ROPoż §4 ust. 2 pkt 2", "W-190", nd=0))
    # obwody wydzielone wymagane przez WT §188 ust. 2
    grupy = {x.odb.grupa for x in obw}
    wym188 = [("oświetlenie", "oswietlenie" in grupy), ("gniazda ogólnego przeznaczenia", "gniazda" in grupy)]
    if any(p.rodzaj == "kuchnia" for p in dane.pomieszczenia):
        wym188.append(("gniazda kuchenne", "gniazda_kuchnia" in grupy))
    if any(x.odb.grupa == "gniazda_lazienka" for x in obw) or any(p.rodzaj in ("lazienka", "wc") for p in dane.pomieszczenia):
        wym188.append(("gniazda w łazience", "gniazda_lazienka" in grupy))
    wym188.append(("odbiorniki z indywidualnym zabezpieczeniem", any(x.odb.id.startswith("D") for x in obw)))
    for nazwa, ok in wym188:
        war.append(Warunek(f"Obwód wydzielony: {nazwa}", 1 if ok else 0, ">=", 1, "szt.", "WT §188 ust. 2", "W-183", nd=0))
    zal = [f"RG: ({f(rg[0])}; {f(rg[1])}; {rg[2]}), ZKP: ({f(zkp[0])}; {f(zkp[1])}) — " + ("instalacje.yaml" if dane.lok("RG") else "automatycznie [ZAŁ]") + ".",
           f"Z_Q w ZKP = {f(Zq, 2)} Ω (R/X ≈ 0,9/0,44), I_k,max w ZKP ≤ {f(par.I_k_ZKP_max, 0)} kA [ZAŁ — dane z warunków przyłączenia OSD].",
           f"Temperatura otoczenia {f(par.theta_pow, 0)} °C (powietrze), {f(par.theta_grunt, 0)} °C (grunt); grupowanie {par.n_grupowanych} obwodów "
           f"(k = {f(kg, 2)}) [ZAŁ].",
           "Przewody: YDYp 450/750 V pod tynkiem (≥ 5 mm tynku, W-184) — metoda C; w stropach monolitycznych w rurach (B2); w ziemi YKY 0,6/1 kV "
           "w rurze (D1); Cu (WT §183 ust. 1 pkt 9).",
           "Aparat główny RG: rozłącznik izolacyjny 3P 63 A z wyzwalaczem PWP (selektywność względem zabezpieczenia przedlicznikowego C40 — R7 §3.1).",
           f"Rezerwa w RG ≥ {f(100 * par.rezerwa, 0)} % modułów."]
    return WynikObwody(dane=dane, par=par, obwody=obw, wlz=wlz, rg_xy=rg, zkp_xy=zkp, spd=spd, pwp=pwp, selektywnosc=sel,
                       warunki=war, kroki=kroki, zalozenia=zal)


KATEGORIE_UDAROWE = [["IV", "6 kV", "złącze ZKP, licznik, zabezpieczenie przedlicznikowe"],
                     ["III", "4 kV", "RG, oprzewodowanie, gniazda, łączniki"],
                     ["II", "2,5 kV", "odbiorniki (AGD, PC, rekuperator, falownik — strona AC)"],
                     ["I", "1,5 kV", "urządzenia specjalnie chronione (elektronika, RACK) — SPD T3"]]


def _raport(w: WynikObwody) -> Raport:
    R = Raport("Obwody instalacji elektrycznej — dobór przewodów i zabezpieczeń, spadki napięć, ochrona przeciwporażeniowa, SPD, PWP",
               f"Obiekt: {w.dane.nazwa}. Układ sieci TN-C (OSD) → TN-S od ZKP/RG. Dane przykładowe oznaczono [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-180…W-190.",
             "PN-HD 60364-4-41:2017-09, -4-43:2024-04, -4-443:2016-03, -5-52:2011, -5-53:2022-10, -5-54:2011, -7-701:2025-02, -7-712:2016-05, -7-722:2019-01."]
            + w.zalozenia)
    R.h(2, "2. Wewnętrzna linia zasilająca (ZKP → RG)")
    R.kroki(w.kroki["wlz"])
    R.p(f"WLZ: **{w.wlz['przewod']}**, L = {f(w.wlz['L'], 1)} m, w ziemi ≥ 0,7 m w piasku z taśmą niebieską, w rurze przy wejściu do budynku "
        "i pod utwardzeniami (R7-L07). Rozdział PEN preferowany w ZKP (WLZ 5-żyłowy — wymaga zgody OSD); inaczej YKY 4×16 (PEN) i rozdział w RG na GSU (D-12).")
    R.h(2, "3. Zestawienie obwodów")
    R.tab(["Obw.", "Przeznaczenie", "Faza", "P [kW]", "I_B [A]", "Zabezp.", "Przewód", "Met.", "I_z [A]", "L [m]", "∆U [%]", "∆U_c [%]",
           "Z_s [Ω]", "I_k1 [A]", "I_a [A]", "RCD", "Podstawa / uwagi"],
          [[x.odb.id, x.odb.nazwa, x.odb.faza, f(x.odb.P, 2), f(x.I_B, 1), x.zab, x.przewod, x.metoda, f(x.I_z, 1), f(x.L, 1), f(x.dU, 2),
            f(x.dU_calk, 2), f(x.Z_s, 3), f(x.I_k1, 0), f(x.I_a, 0), x.odb.rcd, "; ".join([x.odb.podstawa] + x.uwagi)] for x in w.obwody],
          "lllrrlllrrrrrrrll")
    R.p(f"Rezerwa: ≥ {f(100 * w.par.rezerwa, 0)} % miejsca w RG; obwody rezerwowe na drugi punkt ładowania EV (rura Ø ≥ 40 mm do podjazdu, "
        "EPBD art. 14 ust. 4 — dobrowolnie, W-195).")
    R.h(3, "3.1 Przykład obliczeń (obwód najbardziej niekorzystny)")
    R.kroki(w.kroki["przyklad"])
    R.h(2, "4. Ochrona przeciwporażeniowa — RCD")
    R.lista(["Każdy obwód gniazd ≤ 32 A, oświetlenia i łazienek: RCD I_Δn = 30 mA typ A (411.3.3, 411.3.4, 7-701) — preferowane RCBO 1P+N "
             "(awaria jednego obwodu nie wyłącza pozostałych — selektywność różnicowoprądowa; brak RCD grupowego nad RCBO).",
             "Pompa ciepła (falownik sprężarki): typ F lub B wg DTR; falownik PV: typ B, chyba że spełnia 712.530.3.101; EV: własny RCD typ B "
             "lub A-EV + RDC-DD 6 mA DC (7-722); typ AC niedopuszczalny (W-181).",
             "Połączenia wyrównawcze miejscowe w łazienkach — wg PN-HD 60364-7-701:2025-02 (przy instalacjach z tworzyw zwykle nie są "
             "wymagane dla wanny/brodzika); strefy 0/1/2 na rzutach (W-189)."])
    R.h(2, "5. Selektywność (WT §183 ust. 1 pkt 5)")
    R.tab(["Zabezp.", "Obwody", "Zabezp. przedlicznikowe", "Przeciążeniowa (I_n,ZKP/I_n ≥ 1,6)", "Zwarciowa", "Ocena"], w.selektywnosc, "llllll")
    R.p("Selektywność zwarciowa wyłączników B/C za wyłącznikiem C40 w ZKP jest częściowa — do granicy I_s z tabel producenta "
        "(zachowawczo I_s = 5·I_n,C40 = 200 A; dla wyłączników klasy ograniczania 3 typowo 0,3–0,6 kA). Rozwiązania: aparat główny "
        "RG jako rozłącznik (nie wyzwala), RCBO w obwodach odbiorczych; w warunkach przyłączenia zapytać OSD o bezpieczniki gG "
        "zamiast wyłącznika C (poprawa selektywności) [ZAŁ].")
    R.h(2, "6. Ochrona przed przepięciami")
    R.kroki(w.kroki["spd"])
    R.lista([w.spd["RG"], w.spd["DC"], w.spd["tele"], w.spd["T3"]])
    R.tab(["Kategoria", "U_w", "Miejsce w instalacji"], KATEGORIE_UDAROWE, "lrl")
    R.h(2, "7. Przeciwpożarowy wyłącznik prądu (PWP)")
    R.p(f"Kubatura budynku (strefa pożarowa) V = {f(w.pwp['kubatura'], 0)} m³ (próg WT §183 ust. 2: {f(w.pwp['prog'], 0)} m³). "
        f"Decyzja: **{w.pwp['decyzja']}**.")
    R.p(w.pwp["opis"])
    R.h(2, "8. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("WT §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.)", "PN-HD 60364-4-41:2017-09 (tekst IEC 60364-4-41 AMD1:2017 — tabl. 41.1, 411.3.3–411.3.4)",
             "PN-HD 60364-4-443:2016 p. 443.5, tabl. 443.2 (tekst IEC 60364-4-44 AMD1:2015)", "PN-HD 60364-5-52:2011 zał. B [NZW — wartości z literatury]",
             "PN-EN 60898-1 (charakterystyki B/C/D); PN-EN 60909-0 (c_min)", "N SEP-E-002 (spadki napięć) [NZW]",
             "ROPoż (t.j. Dz.U. 2023 poz. 822) §4 ust. 2 pkt 2; rejestr R7 §3.1–3.9, D-04, D-12")
    return R
