"""Projektowe obciążenie cieplne pomieszczeń i budynku — PN-EN 12831-1:2017-08 (kontrolnie wobec PN-EN 12831:2006).

Formalnie WT § 134 ust. 1 (zał. 1 lp. 16) powołuje PN-EN 12831:2006 (wycofaną); PN-EN 12831-1:2017 istnieje tylko
w wersji angielskiej, bez polskiego załącznika krajowego (rejestr W-151, R6-34). Przyjęto formuły wspólne obu wydań
(metoda podstawowa), parametry krajowe wg NA do PN-EN 12831:2006 [NZW]:
  Φ_HL,i = Φ_T,i + Φ_V,i + Φ_RH,i
  Φ_T,i = Σ_k A_k·U_k·(θ_int,i − θ_e) [zewn.] + Σ A_k·U_k·(θ_int,i − θ_u) [nieogrzewane, θ_u z bilansu PN-EN ISO 13789]
        + Σ A_k·U_k·(θ_int,i − θ_j) [sąsiednie ogrzewane o innej temperaturze]
        + f_g1·f_g2,i·G_w·A_g,i·U_equiv·(θ_int,i − θ_e) [grunt, f_g2,i = (θ_int,i − θ_m,e)/(θ_int,i − θ_e)]
        + H_TB·(A_obud,i/A_obud)·(θ_int,i − θ_e) [mostki — rozdział proporcjonalny do pola obudowy pomieszczenia]
  Φ_V,i = ρc·[q_inf,i·(θ_int,i − θ_e) + q_su,i·(θ_int,i − θ_su) + q_tr,i·(θ_int,i − θ_tr)],
        ρc = 0,34 Wh/(m³·K); θ_su = θ_e + η_v·(θ_ex − θ_e) (odzysk ciepła); q_inf,i = 2·V_i·n50·e_i·ε_i
        (e_i = 0,02 — jedna ściana z otworami, 0,03 — więcej; osłonięcie średnie; ε = 1,0 do 10 m) [NZW];
  Φ_RH,i = A_i·f_RH (opcjonalnie; domyślnie 0 — praca ciągła PC, ogrzewanie płaszczyznowe bez obniżeń);
  budynek: ΣΦ_T,i + ΣΦ_V,i (infiltracja × 0,5 — jednoczesność) + ΣΦ_RH,i.
θ_e = −18 °C (strefa II), θ_m,e = 7,9 °C; θ_int wg WT § 134 ust. 2 (pokoje, kuchnie, przedpokoje 20 °C,
łazienki 24 °C) — z pola `temp` pomieszczenia (rejestr W-150).
Dobór pompy ciepła: moc przy θ_e, punkt biwalentny i udział grzałki z rozkładu godzinowego temperatur TMY Poznań.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..wspolne import NZW, PRZYKL, RHO_C_WH, ZAL, Zalozenia, fmt, naglowek_raportu, ok, tabela_md, wym, wyrob
from .klimat import klimat_godzinowy
from .wentylacja import WynikWent


@dataclass
class ObcPom:
    id: str
    nazwa: str
    theta: float
    A: float
    V: float
    H_e: float = 0.0          # do zewnątrz (bez gruntu)
    H_g: float = 0.0          # grunt (12831)
    H_u: float = 0.0          # do nieogrzewanych (A·U, bez b)
    H_j: float = 0.0          # do ogrzewanych o innej temp. (Σ A·U·(θ_i − θ_j)/(θ_i − θ_e))
    H_TB: float = 0.0
    Phi_T: float = 0.0
    q_inf: float = 0.0
    q_su: float = 0.0
    q_tr: float = 0.0
    Phi_V: float = 0.0
    Phi_RH: float = 0.0
    skladniki: list[tuple[str, str, float, float, float, float]] = field(default_factory=list)  # (el, opis, A, U, ΔT, Φ)

    @property
    def Phi_HL(self) -> float:
        return self.Phi_T + self.Phi_V + self.Phi_RH


@dataclass
class WynikObc:
    theta_e: float
    theta_me: float
    theta_su: float
    theta_u: dict
    b_u: dict
    pomieszczenia: list[ObcPom]
    Phi_T: float
    Phi_V: float
    Phi_RH: float
    n50: float
    eta_v: float
    dobor: dict = field(default_factory=dict)

    @property
    def Phi_HL(self) -> float:
        return self.Phi_T + self.Phi_V + self.Phi_RH


def theta_nieogrzewanej(ob, pid: str, theta_e: float, *, n_u: float = 3.0, temp_ogrz: dict | None = None) -> tuple[float, float, float, float]:
    """Temperatura przestrzeni nieogrzewanej z bilansu (PN-EN ISO 13789:2017 p. 6.4; PN-EN 12831-1 p. 6.3.2.4):
    θ_u = (Σ H_iu·θ_i + H_ue·θ_e)/(Σ H_iu + H_ue); H_ue = Σ A·U (zewn.) + H_g + ρc·n_u·V_u.
    Zwraca (θ_u, b = H_ue/(H_iu + H_ue), H_iu, H_ue)."""
    br = ob.bryla
    pu = br.pomieszczenia[pid]
    H_ue = 0.0
    for e in pu.elementy:
        if e.sasiad == "zewn":
            H_ue += e.A * ob.U(e)
        elif e.sasiad == "grunt" and ob.grunt_nieogrz is not None:
            H_ue += ob.grunt_nieogrz.H_g * e.A / max(ob.grunt_nieogrz.A, 1e-9)
    H_ue += RHO_C_WH * n_u * pu.V
    H_iu = 0.0
    sum_t = 0.0
    for p in br.ogrzewane:
        for e in p.elementy:
            if e.sasiad == pid:
                h = e.A * ob.U(e)
                H_iu += h
                sum_t += h * ((temp_ogrz or {}).get(p.id, p.theta or 20.0))
    if H_iu + H_ue <= 0:
        return theta_e, 1.0, 0.0, 0.0
    th = (sum_t + H_ue * theta_e) / (H_iu + H_ue)
    return th, H_ue / (H_iu + H_ue), H_iu, H_ue


def obciazenie_cieplne(ob, went: WynikWent, *, theta_e: float | None = None, theta_me: float | None = None,
                       n50: float | None = None, f_RH: float = 0.0, n_u: float | None = None,
                       zal: Zalozenia | None = None) -> WynikObc:
    cfg = ob.cfg
    theta_e = float(wym("ogrzewanie", "theta_e", -18)) if theta_e is None else theta_e
    theta_me = float(wym("ogrzewanie", "theta_me", 7.9)) if theta_me is None else theta_me
    n50 = float(n50 if n50 is not None else cfg.get("n50", wym("energia", "n50_cel", 1.0)))
    n_u = float(n_u if n_u is not None else (cfg.get("garaz") or {}).get("n_went", 3.0))
    br = ob.bryla
    eta = went.eta
    wp = {p.id: p for p in went.pomieszczenia}
    # temperatura powietrza wywiewanego (średnia ważona wywiewem) i nawiewu po odzysku
    s_w = sum(p.wyw for p in went.pomieszczenia)
    th_ex = sum(p.wyw * p.theta for p in went.pomieszczenia) / s_w if s_w else 20.0
    th_su = theta_e + eta * (th_ex - theta_e)
    naw_p = [p for p in went.pomieszczenia if p.naw > 0]
    th_tr = sum(p.naw * p.theta for p in naw_p) / sum(p.naw for p in naw_p) if naw_p else 20.0
    # nieogrzewane
    th_u, b_u = {}, {}
    for pu in br.nieogrzewane:
        t, b, _, _ = theta_nieogrzewanej(ob, pu.id, theta_e, n_u=n_u)
        th_u[pu.id], b_u[pu.id] = t, b
    A_obud = ob.A_obudowy or 1.0
    wyn = []
    grunt = ob.grunt
    for p in br.ogrzewane:
        ti = p.theta or 20.0
        o = ObcPom(p.id, p.nazwa, ti, p.A, p.V)
        A_ob_i = 0.0
        n_fasad = len({round(e.azymut or -1) for e in p.elementy if e.sasiad == "zewn" and e.rodzaj in ("okno", "drzwi")})
        for e in p.elementy:
            U = ob.U(e)
            if e.sasiad == "zewn":
                h = e.A * U
                o.H_e += h
                A_ob_i += e.A
                o.skladniki.append((e.id, f"{e.rola} {e.przegroda or ''}", e.A, U, ti - theta_e, h * (ti - theta_e)))
            elif e.sasiad == "grunt":
                f_g2 = (ti - theta_me) / (ti - theta_e)
                G_w = grunt.G_w if grunt else 1.0
                f_g1 = grunt.f_g1 if grunt else 1.45
                h = f_g1 * f_g2 * G_w * e.A * U
                o.H_g += h
                A_ob_i += e.A
                o.skladniki.append((e.id, f"grunt {e.przegroda} (f_g1·f_g2·G_w = {fmt(f_g1 * f_g2 * G_w, 3)})", e.A, U,
                                    ti - theta_e, h * (ti - theta_e)))
            elif e.sasiad in th_u:
                h = e.A * U
                o.H_u += h
                A_ob_i += e.A
                dT = ti - th_u[e.sasiad]
                o.skladniki.append((e.id, f"{e.rola} → {e.sasiad} (θ_u = {fmt(th_u[e.sasiad], 1)} °C)", e.A, U, dT, h * dT))
            elif e.sasiad in br.pomieszczenia:
                tj = br.pomieszczenia[e.sasiad].theta or 20.0
                if abs(ti - tj) < 0.1:
                    continue
                h = e.A * U
                o.H_j += h * (ti - tj) / (ti - theta_e)
                o.skladniki.append((e.id, f"{e.rola} → {e.sasiad} ({fmt(tj, 0)} °C)", e.A, U, ti - tj, h * (ti - tj)))
        o.H_TB = ob.H_TB * A_ob_i / A_obud
        if o.H_TB:
            o.skladniki.append(("TB", "mostki (H_TB rozdzielone proporcjonalnie do pola obudowy)", A_ob_i, None,
                                ti - theta_e, o.H_TB * (ti - theta_e)))
        o.Phi_T = sum(x[5] for x in o.skladniki)
        e_i = 0.0 if n_fasad == 0 else (0.02 if n_fasad == 1 else 0.03)
        o.q_inf = 2 * p.V * n50 * e_i * 1.0
        w = wp.get(p.id)
        if w:
            o.q_su = w.naw
            o.q_tr = w.transfer
        o.Phi_V = RHO_C_WH * (o.q_inf * (ti - theta_e) + o.q_su * (ti - th_su) + o.q_tr * max(0.0, ti - th_tr))
        o.Phi_RH = p.A * f_RH
        wyn.append(o)
    Phi_T = sum(o.Phi_T for o in wyn)
    Phi_V = sum(RHO_C_WH * (0.5 * o.q_inf * (o.theta - theta_e) + o.q_su * (o.theta - th_su) +
                            o.q_tr * max(0.0, o.theta - th_tr)) for o in wyn)
    Phi_RH = sum(o.Phi_RH for o in wyn)
    r = WynikObc(theta_e, theta_me, th_su, th_u, b_u, wyn, Phi_T, Phi_V, Phi_RH, n50, eta)
    r.dobor = dobor_pc(r, cfg)
    if zal:
        zal.dodaj(f"θ_e = {fmt(theta_e, 0)} °C (strefa II, Poznań), θ_m,e = {fmt(theta_me, 1)} °C", NZW,
                  "NA do PN-EN 12831:2006; rejestr W-150")
        zal.dodaj(f"Szczelność: n50 = {fmt(n50, 1)} h⁻¹ (cel projektu — do potwierdzenia próbą PN-EN ISO 9972); "
                  "e_i = 0,02/0,03 (osłonięcie średnie), ε = 1,0", NZW, "PN-EN 12831:2006 tab. D.6–D.7")
        zal.dodaj(f"Nawiew po odzysku: θ_su = θ_e + η·(θ_ex − θ_e) = {fmt(th_su, 1)} °C (η = {fmt(eta, 2)}; bez "
                  "nagrzewnicy wtórnej); powietrze transferowe do łazienek o θ = {fmt(th_tr, 1)} °C", ZAL)
        for pid, t in th_u.items():
            zal.dodaj(f"Przestrzeń nieogrzewana {pid}: θ_u = {fmt(t, 1)} °C, b_u = {fmt(b_u[pid], 2)} z bilansu "
                      f"(n_u = {fmt(n_u, 1)} h⁻¹ — przestrzeń ze stałymi otworami wentylacyjnymi)", NZW,
                      "PN-EN ISO 13789:2017 p. 6.4 i tab. krotności dla przestrzeni nieogrzewanych")
    return r


def dobor_pc(r: WynikObc, cfg: dict) -> dict:
    """Dobór pompy ciepła powietrze–woda: moc wymagana przy θ_e, punkt biwalentny, udział grzałki (TMY godzinowy)."""
    pc_cfg = (cfg.get("ogrzewanie") or {}).get("zrodlo") if isinstance(cfg.get("ogrzewanie"), dict) else None
    pc = dict(wyrob("pompa_ciepla", pc_cfg if isinstance(pc_cfg, str) else "PC_R290_monoblok"))
    if isinstance(pc_cfg, dict):
        pc.update(pc_cfg)
    Phi = r.Phi_HL / 1000.0
    ti = 20.0
    te = r.theta_e
    t_gr = 15.0
    # charakterystyka PC — liniowa przez punkty A-15, A-7, A2 (W35)
    pts = sorted([(-15.0, pc.get("P_Am15W35_kW")), (-7.0, pc.get("P_Am7W35_kW")), (2.0, pc.get("P_A2W35_kW"))],
                 key=lambda x: x[0])
    pts = [(t, float(p)) for t, p in pts if p is not None]
    ts = np.array([t for t, _ in pts])
    ps = np.array([p for _, p in pts])

    def P_pc(t):
        t = np.asarray(t, float)
        slope_lo = (ps[1] - ps[0]) / (ts[1] - ts[0]) if len(ts) > 1 else 0.0
        v = np.interp(t, ts, ps)
        return np.where(t < ts[0], ps[0] + slope_lo * (t - ts[0]), v)

    def Q_bud(t):
        return np.clip(Phi * (ti - np.asarray(t, float)) / (ti - te), 0, None)

    tt = np.linspace(te, t_gr, 400)
    diff = P_pc(tt) - Q_bud(tt)
    biw = float(tt[np.argmax(diff >= 0)]) if np.any(diff >= 0) else None
    k = klimat_godzinowy()
    T = k.DBT
    grz = T < t_gr
    Qh = Q_bud(T[grz])
    Pp = P_pc(T[grz])
    E_tot = float(Qh.sum())
    E_grz = float(np.maximum(Qh - Pp, 0).sum())
    return {"Phi_HL_kW": Phi, "P_PC_te_kW": float(P_pc(te)), "P_PC_Am7_kW": pc.get("P_Am7W35_kW"),
            "biwalentny_C": biw, "udzial_grzalki": E_grz / E_tot if E_tot else 0.0,
            "moc_grzalki_kW": pc.get("moc_grzalki_kW"), "pc": pc, "t_graniczna": t_gr,
            "wystarczy_bez_grzalki": bool(float(P_pc(te)) >= Phi),
            "moc_grzalki_wym_kW": max(0.0, Phi - float(P_pc(te)))}


def raport_obciazenie(r: WynikObc, zal: Zalozenia | None = None, szczegoly: bool = True) -> str:
    s = [naglowek_raportu("Projektowe obciążenie cieplne (PN-EN 12831-1:2017, kontrolnie PN-EN 12831:2006)",
                          "WT § 134 ust. 1–2 (θ_int), zał. 1 lp. 16; PN-EN 12831-1:2017-08 p. 6 (metoda podstawowa); "
                          "PN-EN ISO 13370 (grunt), PN-EN ISO 13789 (przestrzenie nieogrzewane)",
                          ["Φ_HL,i = Φ_T,i + Φ_V,i + Φ_RH,i; Φ_V,i = 0,34·[q_inf·(θ_i − θ_e) + q_su·(θ_i − θ_su) + "
                           "q_tr·(θ_i − θ_tr)]."])]
    rows = []
    for o in r.pomieszczenia:
        rows.append([o.id, o.nazwa, fmt(o.theta, 0), fmt(o.A, 1), fmt(o.Phi_T, 0), fmt(o.q_inf, 1), fmt(o.q_su, 0),
                     fmt(o.q_tr, 0), fmt(o.Phi_V, 0), fmt(o.Phi_RH, 0), fmt(o.Phi_HL, 0), fmt(o.Phi_HL / o.A, 1)])
    rows.append(["", "**Budynek**", "", fmt(sum(o.A for o in r.pomieszczenia), 1), fmt(r.Phi_T, 0), "", "", "",
                 fmt(r.Phi_V, 0), fmt(r.Phi_RH, 0), f"**{fmt(r.Phi_HL, 0)}**",
                 fmt(r.Phi_HL / max(sum(o.A for o in r.pomieszczenia), 1e-9), 1)])
    s.append(tabela_md(["Pom.", "Nazwa", "θ_int [°C]", "A [m²]", "Φ_T [W]", "q_inf [m³/h]", "q_su [m³/h]",
                        "q_tr [m³/h]", "Φ_V [W]", "Φ_RH [W]", "Φ_HL [W]", "[W/m²]"], rows, "lllrrrrrrrrr"))
    s.append("")
    s.append(f"θ_e = {fmt(r.theta_e, 0)} °C; nawiew po odzysku θ_su = {fmt(r.theta_su, 1)} °C (η = {fmt(r.eta_v, 2)}); "
             f"n50 = {fmt(r.n50, 1)} h⁻¹. Budynek: infiltracja z wsp. jednoczesności 0,5.")
    for pid, t in r.theta_u.items():
        s.append(f"Przestrzeń nieogrzewana {pid}: θ_u = {fmt(t, 1)} °C (b_u = {fmt(r.b_u[pid], 2)}).")
    s.append("")
    d = r.dobor
    if d:
        s.append("### Dobór źródła ciepła — pompa ciepła powietrze–woda")
        s.append("")
        pc = d["pc"]
        s.append(tabela_md(["Wielkość", "Wartość"], [
            ["Projektowe obciążenie cieplne budynku Φ_HL", f"{fmt(d['Phi_HL_kW'], 2)} kW"],
            ["Wyrób (dane przykładowe)", f"{pc.get('opis', '')} — {pc.get('zrodlo', '')}"],
            ["Moc PC przy A−7/W35 (deklaracja)", f"{fmt(d['P_PC_Am7_kW'], 1)} kW"],
            [f"Moc PC przy θ_e = {fmt(r.theta_e, 0)} °C (ekstrapolacja)", f"{fmt(d['P_PC_te_kW'], 2)} kW"],
            ["Punkt biwalentny (P_PC = Φ(θ))", f"{fmt(d['biwalentny_C'], 1)} °C" if d['biwalentny_C'] is not None else "—"],
            ["Udział grzałki w cieple sezonowym (TMY Poznań, θ < 15 °C)", f"{fmt(d['udzial_grzalki'] * 100, 2)} %"],
            ["Wymagana moc grzałki przy θ_e", f"{fmt(d['moc_grzalki_wym_kW'], 2)} kW (zainstalowana {fmt(d['moc_grzalki_kW'], 1)} kW)"],
        ], "ll"))
        s.append("")
        s.append("Charakterystyka mocy PC — interpolacja liniowa punktów A−15/A−7/A2 (W35) z karty; zapotrzebowanie "
                 "liniowe względem θ_e (θ_int = 20 °C). Przygotowanie c.w.u. — priorytet z blokadą ogrzewania; zasobnik "
                 "wyrównuje obciążenie (sprawdzenie czasu ładowania w PT).")
        s.append("")
    if szczegoly:
        s.append("### Składniki strat przez przenikanie (pomieszczenia)")
        s.append("")
        for o in r.pomieszczenia:
            rows = [[x[0], x[1], fmt(x[2], 2), fmt(x[3], 3) if x[3] is not None else "—", fmt(x[4], 1), fmt(x[5], 0)]
                    for x in o.skladniki]
            s.append(f"**{o.id} {o.nazwa}** (θ = {fmt(o.theta, 0)} °C): Φ_T = {fmt(o.Phi_T, 0)} W")
            s.append("")
            s.append(tabela_md(["Element", "Opis", "A [m²]", "U [W/(m²K)]", "ΔT [K]", "Φ [W]"], rows, "llrrrr"))
            s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
