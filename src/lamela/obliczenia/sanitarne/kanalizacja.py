"""Instalacja kanalizacji sanitarnej — PN-EN 12056-2:2002, system I (pojedynczy pion spustowy z częściowo wypełnionymi
podejściami), przewody odpływowe, przykanalik, studzienka, wentylacja pionów, zabezpieczenie przed cofką.

Podstawy (W-138…W-140, R6-55…R6-59):

* **WT §122 ust. 1–2, zał. 1 lp. 10** — PN-EN 12056-1…5:2002 (aktualne, PL). **WT §125** — piony wyprowadzone ponad dach
  jako wywiewki, powyżej górnej krawędzi okien/drzwi w odległości poziomej < 4 m; zawory napowietrzające (PN-EN 12380)
  dopuszczalne, jeśli ostatni pion na każdym przewodzie odpływowym i co najmniej co piąty wyprowadzono ponad dach.
  **WT §124** — zabezpieczenie przed cofką (PN-EN 13564-1, PN-EN 12056-4). **WT §281** — brak studzienek w garażu.
* **PN-EN 12056-2 tabl. 2** — równoważniki odpływu DU (system I), **tabl. 3** — K = 0,5 (użytkowanie nieciągłe);
  **Q_ww = K·√ΣDU**, nie mniej niż największy DU [NZW — praktyka].
* **Podejścia**: tabl. 5 (nieodpowietrzane, system I) i tabl. 7 (odpowietrzane) — Q_max(DN) [NZW, wartości wg literatury];
  ograniczenia podejść nieodpowietrzanych (tabl. 6): L ≤ 4,0 m, ≤ 3 kolana 90°, spadek ≥ 1 % [NZW]; podejście z miską
  ustępową DN100 (110).
* **Piony**: tabl. 11 (wentylacja główna, trójniki proste/skośne) [NZW]; pion z miską ustępową ≥ DN100 (R6-58).
* **Przewody odpływowe i przykanalik**: przepustowość z wzoru Colebrooka–White'a dla częściowego wypełnienia
  (k_b = 1,0 mm, ν = 1,31·10⁻⁶ m²/s — jak tabl. B.1/B.2 PN-EN 12056-2) — napełnienie h/d ≤ 0,5 w budynku,
  ≤ 0,7 poza budynkiem; spadki minimalne: podejścia 2 %, przewody pod posadzką 2 % (≤ DN100) / 1,5 % (> DN100),
  przykanalik 2 % [ZAŁ — praktyka krajowa, PN-B-01707:1992 wycof.; warunki gestora].
* **Zawory napowietrzające**: Q_a ≥ 8·Q_ww dla pionu, 1–2·Q_ww dla podejść (R6-58) [W].

Przykład sprawdzalny ręcznie (test): ΣDU = 17 → Q_ww = 0,5·√17 = 2,06 l/s (R6 §3.7); pojedyncza miska ustępowa:
0,5·√2 = 0,71 < DU = 2,0 → Q_ww = 2,0 l/s; przewód do połowy wypełniony: Q(h/d = 0,5) = Q(pełny)/2 (R_h jednakowe).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import DaneBudynku, Krok, Raport, Warunek, f, fa, manhattan, wym
from .przybory import KATALOG, Pion, Przybor, grupy_pionow, przybory_z_modelu

# PN-EN 12056-2, system I [NZW — wartości z literatury]
PODEJSCIA_NIEODP = [(40, 0.50), (50, 0.80), (70, 1.50), (80, 2.00), (100, 2.50)]     # (DN, Q_max) tabl. 5 (DN60/90 pominięte)
PODEJSCIA_ODP = [(50, 0.75), (70, 2.25), (80, 3.00), (100, 3.75)]                    # tabl. 7
PIONY_WENT_GLOWNA = [(70, 1.5, 2.0), (80, 2.0, 2.6), (100, 4.0, 5.2), (125, 5.8, 7.6), (150, 9.5, 12.4)]  # tabl. 11 (proste, skośne)
# rury (DN → d_z × s, d_w [mm]): wewnątrz PP-HT (EN 1451), poza budynkiem/pod posadzką PVC-U SN8 (EN 1401)
RURY_HT = {40: (40, 1.8), 50: (50, 1.8), 70: (75, 1.9), 100: (110, 2.7), 125: (125, 3.1), 150: (160, 3.9)}
RURY_PVC = {100: (110, 3.2), 125: (125, 3.7), 150: (160, 4.7), 200: (200, 5.9)}
K_B = 1.0e-3          # m — chropowatość obliczeniowa (PN-EN 12056-2 zał. B)
NU_SC = 1.31e-6       # m²/s


def q_ww(sum_DU: float, K: float = 0.5, DU_max: float = 0.0) -> float:
    """Q_ww = K·√ΣDU [l/s], nie mniej niż największy pojedynczy DU (PN-EN 12056-2 p. 6.2)."""
    return max(K * math.sqrt(max(sum_DU, 0.0)), DU_max)


def _geom(D: float, hd: float) -> tuple[float, float]:
    """Pole przekroju i obwód zwilżony przewodu kołowego przy napełnieniu h/d."""
    hd = min(max(hd, 1e-6), 1.0)
    th = 2.0 * math.acos(1.0 - 2.0 * hd)      # kąt środkowy
    A = D * D / 8.0 * (th - math.sin(th))
    P = D * th / 2.0
    return A, P


def przeplyw_czesciowy(D: float, hd: float, i: float, k: float = K_B, nu: float = NU_SC) -> tuple[float, float]:
    """(Q [l/s], v [m/s]) przy napełnieniu h/d — Colebrook–White z R_h: v = −2·√(2g·4R·i)·log10(k/(14,84R) + 2,51ν/(4R·√(2g·4R·i)))."""
    A, P = _geom(D, hd)
    Rh = A / P
    Dh = 4.0 * Rh
    s = math.sqrt(2.0 * 9.81 * Dh * i)
    v = -2.0 * s * math.log10(k / (3.71 * Dh) + 2.51 * nu / (Dh * s))
    return v * A * 1000.0, v


def napelnienie(Q: float, D: float, i: float, k: float = K_B) -> tuple[float, float]:
    """(h/d, v) dla przepływu Q [l/s] — bisekcja (Q rośnie z h/d do ≈ 0,94)."""
    qmax, _ = przeplyw_czesciowy(D, 0.938, i, k)
    if Q >= qmax:
        return 1.0, przeplyw_czesciowy(D, 1.0, i, k)[1]
    lo, hi = 1e-4, 0.938
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if przeplyw_czesciowy(D, mid, i, k)[0] < Q:
            lo = mid
        else:
            hi = mid
    hd = 0.5 * (lo + hi)
    return hd, przeplyw_czesciowy(D, hd, i, k)[1]


def dobierz_z_tabeli(Q: float, tab, dn_min: int = 0):
    for row in tab:
        if row[0] >= dn_min and Q <= row[1] + 1e-9:
            return row
    return None


@dataclass
class ParametryKan:
    K: float | None = None
    spadek_podejscia: float = 0.02
    spadek_poziomy_male: float = 0.02      # ≤ DN100
    spadek_poziomy_duze: float = 0.015     # > DN100
    spadek_przykanalika: float = 0.02
    hd_max_wewn: float = 0.5
    hd_max_zewn: float = 0.7
    v_min: float = 0.7                     # informacyjnie
    glebokosc_kanalu: float = 2.20         # m p.p.t. — dno kanału sieciowego [ZAŁ]
    przykrycie_min: float | None = None    # domyślnie h_z + 0,2 m (geotechnika.h_z)
    z_dna_startu: float = -0.65            # m — dno przewodu pod posadzką przy najdalszym pionie [ZAŁ]
    wylot_nad_dachem: float = 0.50         # m [ZAŁ]


@dataclass
class OdcinekKan:
    id: str
    opis: str
    rodzaj: str               # podejscie | podejscie_zbiorcze | pion | poziom | przykanalik
    dn: int
    rura: str
    L: float
    sum_DU: float
    Q: float
    i: float | None = None
    hd: float | None = None
    v: float | None = None
    Q_max: float | None = None
    uwagi: str = ""


@dataclass
class WynikKanalizacja:
    dane: DaneBudynku
    par: ParametryKan
    przybory: list
    piony: list
    odcinki: list
    wentylacja: list
    rzedne: dict
    studzienka: dict
    warunki: list
    kroki: dict
    zalozenia: list

    def do_dict(self) -> dict:
        prz = next((o for o in self.odcinki if o.rodzaj == "przykanalik"), None)
        return {"sum_DU": sum(KATALOG[p.typ].DU for p in self.przybory), "Q_ww_l_s": round(prz.Q, 2) if prz else None,
                "przykanalik": f"DN{prz.dn} i={prz.i}" if prz else None,
                "piony": {p["pion"]: f"DN{p['dn']}" for p in self.wentylacja}}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def _okna_w_poblizu(dane: DaneBudynku, xy, r: float = 4.0) -> list[tuple[str, float]]:
    """Otwory (okna, drzwi) w odległości poziomej < r od punktu: [(id, rzędna górnej krawędzi)]."""
    out = []
    m = dane.model
    if m is None:
        return out
    for o in m.otwory():
        if o.typ not in ("okno", "fix", "drzwi_przesuwne_HS", "drzwi_zewn", "drzwi"):
            continue
        if o.typ == "drzwi":
            continue
        try:
            fp = o.footprint
            d = fp.distance(__import__("shapely.geometry", fromlist=["Point"]).Point(xy[0], xy[1]))
        except Exception:
            c = o.srodek
            d = math.hypot(c[0] - xy[0], c[1] - xy[1])
        if d < r:
            out.append((o.id, float(o.z1)))       # Otwor.z1 — rzędna względem ±0,00 budynku
    return out


def oblicz_kanalizacje(dane: DaneBudynku, par: ParametryKan | None = None) -> WynikKanalizacja:
    par = par or ParametryKan()
    K = par.K if par.K is not None else float(wym("wodkan", "kanalizacja_K", 0.5) or 0.5)
    h_z = float(wym("geotechnika", "h_z", 0.8) or 0.8)
    przykr_min = par.przykrycie_min if par.przykrycie_min is not None else h_z + 0.2
    przybory = [p for p in przybory_z_modelu(dane) if KATALOG[p.typ].DU > 0 or KATALOG[p.typ].dn_kan]
    przybory = [p for p in przybory if p.pom is not None]
    piony = grupy_pionow(dane, przybory)
    odc: list[OdcinekKan] = []
    war: list[Warunek] = []
    kroki: dict[str, list] = {}
    zal: list[str] = [f"K = {f(K, 1)} — użytkowanie nieciągłe (budynek mieszkalny), PN-EN 12056-2 tabl. 3 ({'W-138'}).",
                      "Rury: wewnątrz PP-HT (PN-EN 1451-1), pod posadzką i przykanalik PVC-U SN8 lity (PN-EN 1401-1+A1:2023-09) [ZAŁ].",
                      f"Spadki: podejścia {f(100 * par.spadek_podejscia, 1)} %, przewody pod posadzką {f(100 * par.spadek_poziomy_male, 1)} % "
                      f"(≤ DN100) / {f(100 * par.spadek_poziomy_duze, 1)} % (> DN100), przykanalik {f(100 * par.spadek_przykanalika, 1)} % [ZAŁ].",
                      "Trasy: podejścia i przewody pod posadzką równoległe do ścian (odległość „miejska”) [UPR]."]

    # ---- podejścia (per przybór) i zbiorcze (per pomieszczenie)
    for pn in piony:
        for kid, rooms in pn.pomieszczenia.items():
            for rid in rooms:
                lst = [p for p in pn.przybory if p.pom == rid and p.kond == kid]
                for p in lst:
                    t = KATALOG[p.typ]
                    L = max(manhattan(p.xy, pn.xy), 0.3)
                    dn = t.dn_kan or 50
                    odc.append(OdcinekKan(f"{p.id}", f"podejście: {t.nazwa.lower()}", "podejscie", dn,
                                          f"PP-HT {RURY_HT[dn][0]}", round(L, 2), t.DU, t.DU, par.spadek_podejscia))
                sDU = sum(KATALOG[p.typ].DU for p in lst)
                if len(lst) > 1:
                    Q = q_ww(sDU, K, max(KATALOG[p.typ].DU for p in lst))
                    L = max(manhattan(p.xy, pn.xy) for p in lst)
                    ma_wc = any(p.typ == "wc" for p in lst)
                    dn_min = 100 if ma_wc else max(KATALOG[p.typ].dn_kan or 40 for p in lst)
                    row = dobierz_z_tabeli(Q, PODEJSCIA_NIEODP, dn_min)
                    uw = "nieodpowietrzane (tabl. 5)"
                    tab = PODEJSCIA_NIEODP
                    if row is None or L > 4.0:
                        row = dobierz_z_tabeli(Q, PODEJSCIA_ODP, dn_min) or PODEJSCIA_ODP[-1]
                        uw = "odpowietrzane (tabl. 7) — L > 4 m lub Q > Q_max: zawór napowietrzający na końcu podejścia"
                        tab = PODEJSCIA_ODP
                    odc.append(OdcinekKan(f"PZ_{rid}", f"podejście zbiorcze w pom. {rid} → pion {pn.id}",
                                          "podejscie_zbiorcze", row[0], f"PP-HT {RURY_HT[row[0]][0]}", round(L, 2), sDU, Q,
                                          par.spadek_podejscia, Q_max=row[1], uwagi=uw))
                    war.append(Warunek(f"Podejście zbiorcze {rid}: Q_ww ≤ Q_max(DN{row[0]})", Q, "<=", row[1], "l/s",
                                       "PN-EN 12056-2 " + ("tabl. 5" if tab is PODEJSCIA_NIEODP else "tabl. 7"), "W-138"))
                    if tab is PODEJSCIA_NIEODP:
                        war.append(Warunek(f"Podejście nieodpowietrzane {rid}: długość", L, "<=", 4.0, "m",
                                           "PN-EN 12056-2 tabl. 6 [NZW]", "W-138"))
    # ---- piony
    went = []
    kond_ids = [k["id"] for k in dane.kondygnacje]
    for pn in piony:
        sDU = sum(KATALOG[p.typ].DU for p in pn.przybory)
        DUmax = max(KATALOG[p.typ].DU for p in pn.przybory)
        Q = q_ww(sDU, K, DUmax)
        dn_min = 100 if pn.ma_wc else max(70, max(KATALOG[p.typ].dn_kan or 50 for p in pn.przybory))
        row = next((r for r in PIONY_WENT_GLOWNA if r[0] >= dn_min and Q <= r[1]), PIONY_WENT_GLOWNA[-1])
        top = max(kond_ids.index(k) for k in pn.kondygnacje)
        H = dane.rzedna(kond_ids[top]) + 1.0 - (dane.rzedna(kond_ids[0]) - 0.6)
        odc.append(OdcinekKan(f"PION_{pn.id}", f"pion {pn.id} ({', '.join(pn.kondygnacje)})", "pion", row[0],
                              f"PP-HT {RURY_HT[row[0]][0]}", round(H, 2), sDU, Q, None, Q_max=row[1],
                              uwagi="wentylacja główna, trójniki proste (tabl. 11)"))
        kroki.setdefault("piony", []).append(
            Krok(f"Pion {pn.id}: przepływ ścieków", "Q_ww = K·√ΣDU (≥ DU_max)",
                 f"{f(K, 1)}·√{f(sDU, 1)} = {f(K * math.sqrt(sDU), 2)}; DU_max = {f(DUmax, 1)}", Q, "l/s",
                 "PN-EN 12056-2 wzór (1), tabl. 2–3", 2))
        war.append(Warunek(f"Pion {pn.id}: Q_ww ≤ Q_max(DN{row[0]}, wentylacja główna)", Q, "<=", row[1], "l/s",
                           "PN-EN 12056-2 tabl. 11 [NZW]", "W-138"))
        if pn.ma_wc:
            war.append(Warunek(f"Pion {pn.id} z miską ustępową: średnica", row[0], ">=", 100, "DN",
                               "PN-EN 12056-2; R6-58", "W-138", nd=0))
        went.append({"pion": pn.id, "dn": row[0], "Q": Q, "xy": pn.xy, "top": kond_ids[top]})

    # ---- przewody pod posadzką (kolektor) — łańcuch od najdalszego pionu do wyjścia
    stud = dane.lok("studzienka")
    obrys0 = dane.obrysy.get(kond_ids[0])
    from shapely.geometry import Point
    from shapely.ops import nearest_points
    if stud is not None:
        s_xy = stud[:2]
    else:
        # w kierunku kanału sieciowego (dzialka.yaml) — 1,0 m od granicy działki [ZAŁ]
        s_xy = None
        D = dane.dzialka.get("transform")
        if D is not None:
            from shapely.geometry import LineString
            for u in (dane.dzialka.get("uzbrojenie") or {}).get("istniejace", []) or []:
                if u.get("branza") == "kan_sanit" and u.get("linia"):
                    ln = LineString(D.ring_bud(u["linia"]))
                    a = nearest_points(obrys0, ln)[1]
                    ob = dane.dzialka.get("obrys")
                    b = nearest_points(ob.exterior, a)[0] if ob is not None else a
                    vx, vy = (b.x - a.x), (b.y - a.y)
                    n = math.hypot(vx, vy) or 1.0
                    s_xy = (b.x + vx / n * 1.0, b.y + vy / n * 1.0)
        if s_xy is None:
            x0, y0, x1, y1 = obrys0.bounds
            s_xy = ((x0 + x1) / 2, y1 + 8.0)
        zal.append("Studzienka rewizyjna: 1,0 m od granicy działki w kierunku kanału sieciowego [ZAŁ].")
    E = nearest_points(obrys0.exterior, Point(*s_xy))[0]
    E_xy = (E.x, E.y)
    kol = sorted(piony, key=lambda p: -manhattan(p.xy, E_xy))
    rz = {}
    z = par.z_dna_startu
    sDU_cum = 0.0
    DUmax_cum = 0.0
    for i, pn in enumerate(kol):
        sDU_cum += sum(KATALOG[p.typ].DU for p in pn.przybory)
        DUmax_cum = max([DUmax_cum] + [KATALOG[p.typ].DU for p in pn.przybory])
        nxt = kol[i + 1].xy if i + 1 < len(kol) else E_xy
        L = manhattan(pn.xy, nxt)
        Q = q_ww(sDU_cum, K, DUmax_cum)
        dn_min = max(100 if any(pp.ma_wc for pp in kol[: i + 1]) else 70, 100)
        for dn in sorted(RURY_PVC):
            if dn < dn_min:
                continue
            i_s = par.spadek_poziomy_male if dn <= 100 else par.spadek_poziomy_duze
            dz, s = RURY_PVC[dn]
            Dw = (dz - 2 * s) / 1000.0
            hd, v = napelnienie(Q, Dw, i_s)
            if hd <= par.hd_max_wewn:
                break
        rz[f"pion {pn.id}"] = z
        z_end = z - i_s * L
        odc.append(OdcinekKan(f"KOL{i + 1}", f"przewód odpływowy pod posadzką: pion {pn.id} → "
                              + (f"włączenie pionu {kol[i + 1].id}" if i + 1 < len(kol) else "wyjście z budynku"),
                              "poziom", dn, f"PVC-U SN8 {RURY_PVC[dn][0]}", round(L, 2), sDU_cum, Q, i_s, hd, v,
                              Q_max=przeplyw_czesciowy(Dw, par.hd_max_wewn, i_s)[0]))
        war.append(Warunek(f"KOL{i + 1}: napełnienie h/d", hd, "<=", par.hd_max_wewn, "", "PN-EN 12056-2 zał. B (tabl. B.1)",
                           "W-138"))
        z = z_end
    rz["wyjście z budynku"] = z
    # ---- przykanalik
    sDU = sum(KATALOG[p.typ].DU for p in przybory)
    Q = q_ww(sDU, K, max(KATALOG[p.typ].DU for p in przybory))
    L_p = manhattan(E_xy, s_xy) + 1.0
    dn = 150
    dz, s = RURY_PVC[dn]
    Dw = (dz - 2 * s) / 1000.0
    hd, v = napelnienie(Q, Dw, par.spadek_przykanalika)
    z_st = z - par.spadek_przykanalika * L_p
    odc.append(OdcinekKan("PRZ", "przykanalik: budynek → studzienka rewizyjna", "przykanalik", dn,
                          f"PVC-U SN8 {dz}", round(L_p, 2), sDU, Q, par.spadek_przykanalika, hd, v,
                          Q_max=przeplyw_czesciowy(Dw, par.hd_max_zewn, par.spadek_przykanalika)[0],
                          uwagi="min. DN150 (praktyka gestorów) [ZAŁ]"))
    teren_st = dane.teren_z(s_xy)
    teren_E = dane.teren_z(E_xy)
    deficyt = max(0.0, przykr_min - (teren_E - (z + Dw)), przykr_min - (teren_st - (z_st + Dw)))
    if deficyt > 1e-6:
        zal.append(f"Rzędne przewodów obniżono o {f(deficyt, 2)} m względem założenia startowego "
                   f"({f(par.z_dna_startu, 2)} m), aby zapewnić przykrycie przykanalika ≥ {f(przykr_min, 2)} m (strefa przemarzania).")
        rz = {k: v - deficyt for k, v in rz.items()}
        z -= deficyt
        z_st -= deficyt
        rz["wyjście z budynku"] = z
    rz["studzienka (dno wlotu)"] = z_st
    przykr_E = teren_E - (z + Dw)
    przykr_st = teren_st - (z_st + Dw)
    war.append(Warunek("Przykanalik: napełnienie h/d", hd, "<=", par.hd_max_zewn, "", "PN-EN 12056-2 zał. B (tabl. B.2)",
                       "W-138"))
    war.append(Warunek("Przykanalik: prędkość przy Q_ww (samooczyszczanie)", v, ">=", par.v_min, "m/s",
                       "praktyka [ZAŁ] — informacyjnie przy małych Q (spłukiwanie miską ustępową)", "W-138"))
    war.append(Warunek("Przykrycie przykanalika przy budynku (ochrona przed przemarzaniem)", przykr_E, ">=", przykr_min,
                       "m", f"h_z = {f(h_z, 2)} m + 0,2 m (geotechnika.h_z) [ZAŁ]", "W-141"))
    war.append(Warunek("Przykrycie przykanalika przy studzience (ochrona przed przemarzaniem)", przykr_st, ">=", przykr_min,
                       "m", f"h_z = {f(h_z, 2)} m + 0,2 m (geotechnika.h_z) [ZAŁ]", "W-141"))
    # połączenie ze siecią
    z_kanal = teren_st - par.glebokosc_kanalu
    war.append(Warunek("Grawitacyjne połączenie: dno studzienki ≥ dno kanału sieciowego + 0,10 m", z_st, ">=",
                       z_kanal + 0.10, "m", "rzędna dna kanału [ZAŁ — mapa do celów projektowych / warunki gestora]",
                       "W-138"))
    # cofka (WT §124): poziom piętrzenia = teren przy studzience sieciowej (ulica)
    z_ulica = teren_st
    D = dane.dzialka.get("droga") or {}
    if D.get("jezdnia") is not None:
        c = D["jezdnia"].representative_point()
        z_ulica = dane.teren_z((c.x, c.y))
    z_min_wpust = min(dane.rzedna(p.kond) for p in przybory)
    war.append(Warunek("Najniższy wpust/przybór powyżej poziomu piętrzenia (teren przy kanale w ulicy)", z_min_wpust, ">",
                       z_ulica, "m", "WT §124; PN-EN 12056-1 — inaczej zamknięcie przeciwzalewowe PN-EN 13564-1 lub "
                       "przepompownia PN-EN 12056-4", "W-140"))
    stud_d = {"xy": s_xy, "typ": "studzienka rewizyjna z tworzywa PP DN425 z kinetą przelotową, właz żeliwny B125 [ZAŁ]",
              "teren": teren_st, "dno": z_st, "glebokosc": teren_st - z_st, "z_ulica": z_ulica,
              "dystans_granica": dane.dystans_do_granicy(s_xy)}
    # garaż — zakaz studzienek (WT §281)
    gar = [p for p in dane.pomieszczenia if p.rodzaj == "garaz"]
    for g in gar:
        if g.polygon is not None and g.polygon.contains(Point(*s_xy)):
            war.append(Warunek("Studzienka w garażu", 1, "==", 0, "", "WT §281", "W-118"))
    # ---- wentylacja pionów (WT §125)
    naj = kol[0].id if kol else None
    for i, wv in enumerate(went):
        pn = next(p for p in piony if p.id == wv["pion"])
        nad_dach = (pn.id == naj) or (i % 5 == 0)
        # dach nad pionem
        from shapely.geometry import Point as P
        roofs = [dd for dd in dane.dachy if dd.typ in ("plaski", "zielony") and dd.obrys.buffer(0.3).contains(P(*pn.xy))]
        z_dach = max((dd.rzedna for dd in roofs), default=dane.H_max)
        z_wyl = z_dach + par.wylot_nad_dachem
        okna = _okna_w_poblizu(dane, pn.xy, 4.0)
        z_okna = max((z1 for _, z1 in okna), default=None)
        wv.update({"wentylacja": "wywiewka ponad dach" if nad_dach else "zawór napowietrzający PN-EN 12380 (dozwolony)",
                   "z_dach": z_dach, "z_wylotu": z_wyl if nad_dach else None, "okna_4m": okna,
                   "Q_a_min": 8.0 * wv["Q"], "uzasadnienie": ("ostatni pion na przewodzie odpływowym" if pn.id == naj
                                                               else ("co piąty pion" if i % 5 == 0 else "pion pośredni"))})
        if nad_dach and z_okna is not None:
            war.append(Warunek(f"Wywiewka pionu {pn.id}: wylot powyżej górnej krawędzi okien/drzwi w odl. < 4 m",
                               z_wyl, ">", z_okna, "m", "WT §125 ust. 1", "W-139",
                               uwagi="okna: " + ", ".join(o for o, _ in okna)))
        czerp = dane.lok("czerpnia")
        if nad_dach and czerp is not None:
            war.append(Warunek(f"Wywiewka {pn.id} — odległość od czerpni", math.hypot(czerp[0] - pn.xy[0], czerp[1] - pn.xy[1]),
                               ">=", 6.0, "m", "WT §152 ust. 4 (czerpnia dachowa) / ust. 3 (8 m — terenowa)", "W-166"))
    kroki["przykanalik"] = [
        Krok("Suma równoważników odpływu budynku", "ΣDU", " + ".join(f(KATALOG[p.typ].DU, 1) for p in przybory), sDU, "l/s", "", 1),
        Krok("Przepływ ścieków w przykanaliku", "Q_ww = K·√ΣDU", f"{f(K, 1)}·√{f(sDU, 1)}", Q, "l/s", "PN-EN 12056-2 p. 6.2", 2),
        Krok(f"Napełnienie DN{dn} (d_w = {f(Dw * 1000, 1)} mm) przy i = {f(100 * par.spadek_przykanalika, 1)} %",
             "Q(h/d) z Colebrooka–White'a", "", hd, "", "k_b = 1,0 mm", 3),
        Krok("Prędkość przy Q_ww", "v", "", v, "m/s", "", 2),
        Krok("Rzędna dna przykanalika przy studzience", "z_st = z_E − i·L", f"{f(z, 3)} − {f(par.spadek_przykanalika, 3)}·{f(L_p, 2)}",
             z_st, "m", "", 3),
        Krok("Przykrycie przykanalika przy studzience", "h = z_ter − (z_st + d)", f"{f(teren_st, 3)} − ({f(z_st, 3)} + {f(Dw, 3)})",
             przykr_st, "m", "", 2),
    ]
    return WynikKanalizacja(dane=dane, par=par, przybory=przybory, piony=piony, odcinki=odc, wentylacja=went, rzedne=rz,
                            studzienka=stud_d, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikKanalizacja) -> Raport:
    d = w.dane
    R = Raport("Obliczenia instalacji kanalizacji sanitarnej",
               f"Obiekt: {d.nazwa}. PN-EN 12056-2:2002, system I. Dane przykładowe oznaczono [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §122–125, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-138…W-140, W-118.",
             "PN-EN 12056-1…5:2002 (PL, aktualne); PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10.",
             "Tablice PN-EN 12056-2 (Q_max podejść i pionów) — wartości z literatury, oznaczone [NZW] (treść normy płatna; "
             "rejestr R6 Nierozstrz. 8). Przepustowość przewodów odpływowych liczona wzorem Colebrooka–White'a jak w zał. B normy."]
            + w.zalozenia)
    R.h(2, "2. Przybory i równoważniki odpływu")
    R.tab(["Id", "Przybór", "Kond.", "Pom.", "DU [l/s]", "Podejście"],
          [[p.id, KATALOG[p.typ].nazwa, p.kond, p.pom or "—", f(KATALOG[p.typ].DU, 1),
            f"DN{KATALOG[p.typ].dn_kan}" if KATALOG[p.typ].dn_kan else "—"] for p in w.przybory], "llllrl")
    R.h(2, "3. Przewody")
    R.tab(["Odcinek", "Opis", "Rodzaj", "DN", "Rura", "L [m]", "ΣDU [l/s]", "Q_ww [l/s]", "i [%]", "h/d", "v [m/s]",
           "Q_max [l/s]", "Uwagi"],
          [[o.id, o.opis, o.rodzaj, str(o.dn), o.rura, f(o.L, 2), f(o.sum_DU, 1), f(o.Q, 2),
            f(100 * o.i, 1) if o.i else "—", f(o.hd, 2) if o.hd is not None else "—", f(o.v, 2) if o.v is not None else "—",
            f(o.Q_max, 2) if o.Q_max else "—", o.uwagi] for o in w.odcinki], "lllrlrrrrrrrl")
    R.h(3, "3.1 Piony")
    R.kroki(w.kroki.get("piony", []))
    R.h(3, "3.2 Przykanalik i studzienka")
    R.kroki(w.kroki["przykanalik"])
    s = w.studzienka
    R.lista([f"Studzienka: {s['typ']}; położenie (układ budynku) {f(s['xy'][0])}; {f(s['xy'][1])}; teren {f(s['teren'], 2)} m, "
             f"dno {f(s['dno'], 2)} m (względne), głębokość {f(s['glebokosc'], 2)} m; odległość od granicy działki "
             f"{f(s['dystans_granica'], 2)} m.",
             "Rewizje: czyszczaki u podstawy każdego pionu (≈ 0,5 m nad posadzką) i przy zmianach kierunku przewodów pod posadzką; "
             "przejście przez ścianę fundamentową w tulei ochronnej, gazoszczelne (WT §234 ust. 4, W-214)."])
    R.tab(["Punkt", "Rzędna dna [m, wzgl. ±0,00]"], [[k, f(v, 3)] for k, v in w.rzedne.items()], "lr")
    R.h(2, "4. Wentylacja pionów (WT §125)")
    R.tab(["Pion", "DN", "Q_ww [l/s]", "Zakończenie", "Uzasadnienie", "Dach [m]", "Wylot [m]", "Okna < 4 m", "Q_a zaworu ≥ [l/s]"],
          [[v["pion"], str(v["dn"]), f(v["Q"], 2), v["wentylacja"], v["uzasadnienie"], f(v["z_dach"], 2),
            f(v["z_wylotu"], 2) if v["z_wylotu"] else "—", ", ".join(f"{o} (↑{f(z, 2)})" for o, z in v["okna_4m"]) or "—",
            f(v["Q_a_min"], 1)] for v in w.wentylacja], "lrrllrrlr")
    R.lista(["Wywiewki: wylot ≥ 0,5 m nad pokryciem [ZAŁ], ≥ 6 m od czerpni dachowej (WT §152 ust. 4) i ≥ 8 m od czerpni "
             "terenowej/ściennej (§152 ust. 3); nie włączać do kanałów wentylacyjnych (§125 ust. 3).",
             "Zawory napowietrzające (PN-EN 12380) w miejscu dostępnym, wentylowanym, powyżej najwyższego podejścia; "
             "przepływ nominalny Q_a ≥ 8·Q_ww (pion), 1–2·Q_ww (podejście) [W]."])
    R.h(2, "5. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("WT §122–125, §152, §234, §281 (t.j. Dz.U. 2022 poz. 1225 ze zm.) — art. 102a PB",
             "PN-EN 12056-2:2002 — tabl. 2, 3, 5–7, 11, zał. B (wartości wg kalkulatorprojektanta.pl, instsani.pl — [NZW])",
             "Rejestr R6: R6-55…R6-59, §3.7; rejestr wymagań W-138…W-141")
    return R
