"""Odwodnienie dachów i zagospodarowanie wód opadowych na działce — PN-EN 12056-3:2002, metodyka Aquanet 2024
(PANDa 2050), wariant bazowy D-05: szczelny zbiornik ≤ 5 m³ z przelewem do niecki / ogrodu deszczowego.

Zakres (wymaganie Inwestora 25.09.2026 — brief §9 pkt 3 i 6, schemat modelu §6):

* **każde pole dachu** (``dachy`` i ``wsporniki_plyty`` z modelu): powierzchnia rzutu, rodzaj (płaski / zielony / taras),
  przepływ obliczeniowy **Q = r·A·C** (PN-EN 12056-3 p. 4; r = 0,046 l/(s·m²) — W-142, PANDa C10 5 min), wpusty
  (z modelu ``dachy[].wpusty`` lub propozycja), spadki ≥ 2 % (W-142), grubość izolacji spadkowej z najdłuższej drogi
  spływu, podgrzewanie wpustów;
* **przelewy awaryjne** w attykach dla każdego pola: przepływ przy całkowitym zablokowaniu wpustów z **współczynnikiem
  ryzyka F_R = 2,0** (PN-EN 12056-3 tabl. 2 — woda może przedostać się do budynku) [NZW]; przepustowość przelewu
  prostokątnego (Poleni): **Q = ⅔·μ·b·√(2g)·h^1,5**, μ = 0,6 [W — hydraulika]; rzędna dna przelewu nad pokryciem
  i poniżej wywinięcia hydroizolacji (≥ 0,15 m ponad warstwę wierzchnią — brief §9 pkt 4); obciążenie wodą spiętrzoną;
* **rury spustowe** (``dachy[].rury_spustowe``: średnica, trasa wewn. w szachcie / zewn., odbiornik): przepustowość
  **Q_RWP = 2,5·10⁻⁴·k_b^−0,167·d_i^2,667·f^1,667** (PN-EN 12056-3 wzór (7?); k_b = 0,25 mm, f = 0,33) [NZW];
* **dach zielony** (np. garaż): współczynnik spływu ψ = 0,5 (Aquanet tab. 2) do bilansu; do wymiarowania wpustów
  C = 1,0 (substrat nasycony/zamarznięty) [ZAŁ]; retencja w substracie i warstwie drenażowej; kontrola warstw
  (bariera przeciwkorzenna, drenaż, geowłóknina, opaska żwirowa przy attyce);
* **odwodnienia liniowe** przy drzwiach bezprogowych (HS, drzwi tarasowe) i przed bramą garażu (PN-EN 1433 — klasy
  obciążenia A15/B125/C250);
* **bilans zbiornika ≤ 5 m³** (PB art. 29 ust. 2 pkt 36 — bez zgłoszenia; W-145) i **niecki** (metoda bilansowa Aquanet:
  V_obl = max_td[0,06·q(t_d, C10)·ΣψA·t_d − 0,06·Q_inf·t_d], Q_inf = 1000·A_inf·k_f,nn, k_f,nn = 0,5·k_f,
  V_min = f_b·V_obl, opróżnianie ≤ 24 h; W-143), bilans roczny z normami opadowymi IMGW 1991–2020 (Poznań, 538,9 mm);
* wariant opcjonalny: **skrzynki rozsączające** (ta sama metoda bilansowa; DWA-A 138-1:2024 jako tło; wymaga stanowiska
  PGW Wody Polskie — D-05).

Przykłady sprawdzalne ręcznie (test): R6 §3.8 — A_red = 200 m², skrzynki 4,8 × 2,4 × 0,66 m, k_f = 1·10⁻⁴ m/s →
Q_inf = 0,81 l/s, V_obl ≈ 4,2 m³ (t_d ≈ 30 min), V_min ≈ 5,1 m³, opróżnianie ≈ 1,7 h; Aquanet (2024) rozdz. IV:
0,06·(17,388·4,84 + 55,5 − 52,93 − 20)·484 = 1937,7 m³.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import (DaneBudynku, Krok, Raport, Warunek, f, fa, interp_loglog, manhattan, opady_imgw, panda_c10,
                            wym, wym_zrodlo)
from .kanalizacja import napelnienie, przeplyw_czesciowy

WPUST_Q = {50: 0.9, 70: 1.7, 100: 4.5, 125: 7.0, 150: 8.1}   # l/s przy 35 mm spiętrzenia [NZW — PN-EN 1253-2 / karta wyrobu]
RURY_SPUSTOWE = [(70, 66.0), (80, 76.0), (100, 96.0), (125, 121.0), (150, 146.0)]  # (DN, d_i mm) — PVC/stal [ZAŁ]
PSI = {"plaski": 0.95, "zielony": 0.5, "taras": 0.95, "wspornik": 0.95, "kostka": 0.8, "azur": 0.4, "ogrod": 0.15,
       "niecka": 1.0, "zwir": 0.6}


def q_panda(td_min: float, tab=None) -> float:
    """Natężenie deszczu q(t_d, C10) [dm³/(s·ha)] — PANDa 2050 Poznań (Aquanet 2024 tab. 3), interpolacja log-log;
    dla t_d > 1440 min ekstrapolacja log-log z ostatniego przedziału [UPR]."""
    tab = tab or panda_c10()["t_min_q"]
    ts = [t for t, _ in tab]
    qs = [q for _, q in tab]
    for t, q in tab:
        if abs(t - td_min) < 1e-9:
            return q
    return interp_loglog(td_min, ts, qs)


def objetosc_bilansowa(A_red_ha: float, Q_odp: float, t_max: int = 4320, Q_o: float = 0.0, tab=None) -> tuple[float, float]:
    """(V_obl [m³], t_d miarodajny [min]) — Aquanet 2024 wzór (1): V = max_td 0,06·[q·ΣψA + ΣQ_o − Q_inf − Q_od]·t_d;
    krok 1 min do 300 min, 5 min dalej."""
    best, tb = -1e9, 5
    t = 5
    while t <= t_max:
        V = 0.06 * (q_panda(t, tab) * A_red_ha + Q_o - Q_odp) * t
        if V > best:
            best, tb = V, t
        t += 1 if t < 300 else 5
    return max(best, 0.0), tb


def przepustowosc_rury_spustowej(d_i_mm: float, f_nap: float = 0.33, k_b_mm: float = 0.25) -> float:
    """Q_RWP [l/s] = 2,5·10⁻⁴·k_b^−0,167·d_i^2,667·f^1,667 (PN-EN 12056-3, rury spustowe) [NZW]."""
    return 2.5e-4 * k_b_mm ** -0.167 * d_i_mm ** 2.667 * f_nap ** 1.667


def przepustowosc_przelewu(b: float, h: float, mu: float = 0.6) -> float:
    """Przelew prostokątny o ostrej krawędzi (Poleni): Q = ⅔·μ·b·√(2g)·h^1,5 [l/s] (b, h w m)."""
    return 2.0 / 3.0 * mu * b * math.sqrt(2 * 9.81) * max(h, 0.0) ** 1.5 * 1000.0


@dataclass
class ParametryDeszcz:
    r: float | None = None                 # l/(s·m²) — domyślnie wymagania.yaml (W-142)
    F_R: float = 2.0                       # współczynnik ryzyka przelewów awaryjnych (PN-EN 12056-3 tabl. 2) [NZW]
    C_wymiarowanie: float = 1.0            # współczynnik spływu do wpustów/rur (PN-EN 12056-3) — także dach zielony [ZAŁ]
    dn_wpustu: int = 100                   # [ZAŁ] gdy brak w modelu
    wywiniecie_hydroiz: float = 0.15       # m ponad warstwę wierzchnią (brief §9 pkt 4)
    h0_przelewu: float = 0.05              # m — dno przelewu nad pokryciem przy wpuście [ZAŁ]
    rezerwa_wywiniecia: float = 0.02       # m
    k_f: float = 1.0e-4                    # m/s — piaski średnie [ZAŁ; badania E-04]
    V_zbiornika: float | None = None       # m³ (≤ 5); domyślnie dzialka.retencja.zbiornik.V lub 5,0
    h_niecki: float = 0.30                 # m (W-145: ≤ 0,3 m)
    A_niecki: float | None = None          # m² (None → dobór)
    f_b: float | None = None
    t_opr_max: float | None = None
    eta_filtra: float = 0.9                # sprawność filtra deszczówki (ubytek na płukanie) [ZAŁ]
    podlewanie_A: float = 100.0            # m² [ZAŁ] — jak w module wody
    podlewanie_mm_mies: dict = field(default_factory=lambda: {5: 60.0, 6: 80.0, 7: 90.0, 8: 80.0, 9: 50.0})  # mm/mies. [ZAŁ]
    skrzynki: tuple | None = None          # (L, B, H) [m] wariant opcjonalny; None → dobór
    porowatosc_skrzynek: float = 0.95      # dane producentów [W]
    retencja_substratu: float = 30.0       # dm³/m² — substrat 8–10 cm + drenaż (dane producentów) [ZAŁ]
    ZWG_ppt: float | None = None           # m p.p.t. (domyślnie geotechnika.ZWG_ppt)
    podlaczone_utwardzenia: bool = False   # czy utwardzenia odprowadzane do zbiornika (domyślnie spływ na zieleń)


@dataclass
class PoleDachu:
    id: str
    typ: str
    A: float
    psi: float
    Q: float
    wpusty: list
    n_wpustow: int
    Q_wpustow: float
    spadek: float | None
    L_splywu: float
    dh_spadkowa: float
    przelewy: list
    Q_awar: float
    Q_przelewow: float
    h_spietrzenia: float
    obc_woda: float
    rury: list
    rzedna: float
    attyka: float | None
    uwagi: list = field(default_factory=list)


@dataclass
class WynikDeszcz:
    dane: DaneBudynku
    par: ParametryDeszcz
    pola: list
    odwodnienia_liniowe: list
    retencja: dict
    skrzynki: dict
    bilans_roczny: dict
    dach_zielony: list
    warunki: list
    kroki: dict
    zalozenia: list

    def do_dict(self) -> dict:
        return {"A_dachow_m2": round(sum(p.A for p in self.pola), 1), "Q_dachy_l_s": round(sum(p.Q for p in self.pola), 2),
                "A_red_m2": round(self.retencja["A_red"], 1), "V_zbiornika_m3": self.retencja["V_zb"],
                "niecka_A_m2": round(self.retencja["A_n"], 1), "niecka_V_min_m3": round(self.retencja["V_min_a"], 2),
                "pokrycie_podlewania": round(self.bilans_roczny["pokrycie"], 3)}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def _odl_max_do_wpustow(poly, wpusty_xy) -> float:
    """Najdłuższa droga spływu w rzucie: max po wierzchołkach i punktach siatki odległości do najbliższego wpustu."""
    import numpy as np
    from shapely.geometry import Point
    if not wpusty_xy:
        return 0.0
    x0, y0, x1, y1 = poly.bounds
    pts = [Point(x, y) for x in np.linspace(x0, x1, 25) for y in np.linspace(y0, y1, 25)]
    pts = [p for p in pts if poly.contains(p)] + [Point(c) for c in poly.exterior.coords]
    return max(min(math.hypot(p.x - w[0], p.y - w[1]) for w in wpusty_xy) for p in pts)


def _wpusty_propozycja(poly, n: int) -> list:
    """Rozmieszczenie n wpustów w rzucie pola (punkty reprezentatywne podziału wzdłuż dłuższego boku) [UPR]."""
    from shapely.geometry import box
    x0, y0, x1, y1 = poly.bounds
    out = []
    for k in range(n):
        if (x1 - x0) >= (y1 - y0):
            cell = box(x0 + k * (x1 - x0) / n, y0, x0 + (k + 1) * (x1 - x0) / n, y1)
        else:
            cell = box(x0, y0 + k * (y1 - y0) / n, x1, y0 + (k + 1) * (y1 - y0) / n)
        g = poly.intersection(cell)
        if not g.is_empty:
            c = g.representative_point()
            out.append((round(c.x, 2), round(c.y, 2)))
    return out


def oblicz_deszczowa(dane: DaneBudynku, par: ParametryDeszcz | None = None, podlewanie=None) -> WynikDeszcz:
    par = par or ParametryDeszcz()
    r = par.r if par.r is not None else float(wym("wodkan", "deszcz_natezenie_rynny", 0.046) or 0.046)
    fb = par.f_b if par.f_b is not None else float(wym("wodkan", "retencja_wsp_bezp_fb", 1.2) or 1.2)
    kf_red = float(wym("wodkan", "retencja_kf_redukcja", 0.5) or 0.5)
    t_opr_max = par.t_opr_max if par.t_opr_max is not None else float(wym("wodkan", "retencja_oproznianie_max", 24) or 24)
    V_zb_max = float(wym("wodkan", "zbiornik_opadowy_bez_zgloszenia_max", 5.0) or 5.0)
    spadek_min = float(wym("wodkan", "spadek_dachu_min", 0.02) or 0.02)
    psi_tab = dict(PSI)
    psi_tab["plaski"] = float(wym("wodkan", "psi_dach_plaski", 0.95) or 0.95)
    psi_tab["zielony"] = float(wym("wodkan", "psi_dach_zielony_ekstensywny", 0.5) or 0.5)
    war: list[Warunek] = []
    kroki: dict[str, list] = {}
    zal = [f"Natężenie deszczu do wymiarowania odwodnienia dachów r = {f(r, 3)} l/(s·m²) ({wym_zrodlo('wodkan', 'deszcz_natezenie_rynny')}).",
           f"C = {f(par.C_wymiarowanie, 1)} dla wszystkich dachów przy wymiarowaniu wpustów i przelewów (także zielonych — "
           "substrat nasycony lub zamarznięty) [ZAŁ]; ψ wg Aquanet (tab. 2) wyłącznie do bilansu retencji.",
           f"Przelewy awaryjne: pełne zablokowanie wpustów, współczynnik ryzyka F_R = {f(par.F_R, 1)} (PN-EN 12056-3 tabl. 2 — "
           "spiętrzenie może spowodować przeciek do budynku) [NZW].",
           f"Przepustowość wpustów przy 35 mm spiętrzenia: " + ", ".join(f"DN{k} {f(v, 1)} l/s" for k, v in WPUST_Q.items()) +
           " [NZW — przyjąć z karty wyrobu wg PN-EN 1253-2]."]
    pola = []
    for dd in dane.dachy:
        if dd.pole < 1.0:
            continue
        A = dd.pole
        psi = psi_tab.get(dd.typ, 0.95)
        Q = r * A * par.C_wymiarowanie
        wp = list(dd.wpusty)
        uw = []
        if not wp:
            n = max(1, math.ceil(Q / WPUST_Q[par.dn_wpustu]))
            if A > 150:
                n = max(n, 2)
            wp = [{"xy": xy, "dn": par.dn_wpustu, "podgrzewany": None, "propozycja": True}
                  for xy in _wpusty_propozycja(dd.obrys, n)]
            uw.append(f"brak wpustów w modelu — proponowane {n} × DN{par.dn_wpustu} (uzupełnić `dachy[].wpusty`)")
        Qw = sum(WPUST_Q.get(int(w.get("dn") or par.dn_wpustu), WPUST_Q[100]) for w in wp)
        L_spl = _odl_max_do_wpustow(dd.obrys, [w["xy"] for w in wp])
        sp = float(dd.spadek) if dd.spadek is not None else None
        dh = (sp if sp else spadek_min) * L_spl
        # przelewy awaryjne
        Q_aw = par.F_R * r * A * par.C_wymiarowanie
        prz = list(dd.przelewy)
        h_dop = par.wywiniecie_hydroiz - par.rezerwa_wywiniecia - par.h0_przelewu
        at = dd.attyka_wys
        if dd.typ in ("taras", "wspornik") and at is None:
            h_dop = max(h_dop, 0.05)
        if not prz and (at or 0) > 0:
            b_req = Q_aw / 1000.0 / (2.0 / 3.0 * 0.6 * math.sqrt(2 * 9.81) * max(h_dop, 0.02) ** 1.5)
            n_p = max(1, math.ceil(b_req / 0.30))
            b1 = max(0.10, math.ceil(b_req / n_p * 20) / 20)
            prz = [{"szer": b1, "wys": 0.10, "rzedna_dna": round(dd.rzedna + par.h0_przelewu, 3), "propozycja": True}
                   for _ in range(n_p)]
            uw.append(f"brak przelewów awaryjnych w modelu — proponowane {n_p} × {f(b1 * 100, 0)}×10 cm, dno {f(par.h0_przelewu * 100, 0)} cm "
                      "nad pokryciem (uzupełnić `dachy[].przelewy_awaryjne`)")
        Qp = 0.0
        h_sp = 0.0
        for p in prz:
            b = float(p.get("szer", 0.2))
            hw = float(p.get("wys", 0.1))
            dno = float(p.get("rzedna_dna", dd.rzedna + par.h0_przelewu))
            h_eff = min(hw, dd.rzedna + par.wywiniecie_hydroiz - par.rezerwa_wywiniecia - dno)
            Qp += przepustowosc_przelewu(b, h_eff)
            h0 = dno - dd.rzedna
            war.append(Warunek(f"Pole {dd.id}: dno przelewu nad pokryciem (odpływ normalny przez wpusty)", h0, ">=", 0.03, "m",
                               "[ZAŁ] ≥ 3 cm", "W-142"))
            war.append(Warunek(f"Pole {dd.id}: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa)", dno, "<=",
                               dd.rzedna + par.wywiniecie_hydroiz - par.rezerwa_wywiniecia - 0.02, "m",
                               "brief §9 pkt 4 (wywinięcie ≥ 15 cm)", "W-142", nd=3))
        # spiętrzenie przy Q_aw (wszystkie przelewy o łącznej szerokości)
        B = sum(float(p.get("szer", 0.2)) for p in prz)
        if B > 0:
            h_sp = (Q_aw / 1000.0 / (2.0 / 3.0 * 0.6 * B * math.sqrt(2 * 9.81))) ** (2.0 / 3.0)
            dno_min = min(float(p.get("rzedna_dna", dd.rzedna + par.h0_przelewu)) for p in prz)
            z_wody = dno_min + h_sp
            war.append(Warunek(f"Pole {dd.id}: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji",
                               z_wody, "<", dd.rzedna + par.wywiniecie_hydroiz, "m", "PN-EN 12056-3 p. 7 [NZW]; brief §9", "W-142", nd=3))
            obc = 10.0 * (z_wody - dd.rzedna)
        else:
            obc = 0.0
        # rury spustowe
        rury = []
        rs = list(dd.rury_spustowe)
        if not rs:
            for i, w in enumerate(wp):
                qw = Q / len(wp)
                dn = next((dn for dn, di in RURY_SPUSTOWE if przepustowosc_rury_spustowej(di) >= qw and dn >= int(w.get("dn") or 100)),
                          RURY_SPUSTOWE[-1][0])
                rs.append({"id": f"RS-{dd.id}-{i + 1}", "od_wpustu": i, "trasa": "wewn_szacht", "dn": dn, "do": "zbiornik",
                           "propozycja": True})
            uw.append("brak rur spustowych w modelu — proponowane (trasa wewn. w szachcie izolowanym, odbiornik: zbiornik)")
        for rr in rs:
            dn = int(rr.get("dn") or 100)
            di = dict(RURY_SPUSTOWE).get(dn, dn - 4.0)
            qcap = przepustowosc_rury_spustowej(di)
            n_obsl = max(1, sum(1 for x in rs if True))
            q_r = Q / n_obsl
            rury.append({**rr, "d_i": di, "Q_RWP": qcap, "Q": q_r})
            war.append(Warunek(f"Rura spustowa {rr.get('id')}: Q ≤ Q_RWP(DN{dn}, f = 0,33)", q_r, "<=", qcap, "l/s",
                               "PN-EN 12056-3 (rury spustowe) [NZW]", "W-142"))
            if rr.get("trasa") == "zewn":
                uw.append(f"{rr.get('id')}: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury "
                          "przewodem grzejnym (zamarzanie) [ZAŁ]")
            else:
                uw.append(f"{rr.get('id')}: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy "
                          "[ZAŁ]; przejście przez stropodach szczelne (paroizolacja!)")
        podg = [w for w in wp if w.get("podgrzewany")]
        if dd.typ in ("plaski", "zielony") and not podg:
            uw.append("wpusty: rozważyć podgrzewanie (wpust w strefie zacienionej / odpływ przez przestrzeń nieogrzewaną) [ZAŁ]")
        war.append(Warunek(f"Pole {dd.id}: przepustowość wpustów ≥ Q", Qw, ">=", Q, "l/s", "PN-EN 12056-3 p. 6", "W-142"))
        if dd.typ in ("plaski", "zielony"):
            war.append(Warunek(f"Pole {dd.id}: spadek połaci", sp if sp is not None else 0.0, ">=", spadek_min, "",
                               wym_zrodlo("wodkan", "spadek_dachu_min"), "W-142", nd=3,
                               uwagi="" if sp is not None else "brak spadku w modelu"))
            war.append(Warunek(f"Pole {dd.id}: przelewy awaryjne (Q_przel ≥ F_R·Q)", Qp, ">=", Q_aw, "l/s",
                               "PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3", "W-142"))
        pola.append(PoleDachu(id=dd.id, typ=dd.typ, A=A, psi=psi, Q=Q, wpusty=wp, n_wpustow=len(wp), Q_wpustow=Qw, spadek=sp,
                              L_splywu=L_spl, dh_spadkowa=dh, przelewy=prz, Q_awar=Q_aw, Q_przelewow=Qp, h_spietrzenia=h_sp,
                              obc_woda=obc, rury=rury, rzedna=dd.rzedna, attyka=at, uwagi=uw))
    kroki["dach"] = []
    if pola:
        p0 = max(pola, key=lambda p: p.A)
        kroki["dach"] = [
            Krok(f"Pole {p0.id} ({p0.typ}): przepływ obliczeniowy", "Q = r·A·C", f"{f(r, 3)}·{f(p0.A, 1)}·{f(par.C_wymiarowanie, 1)}",
                 p0.Q, "l/s", "PN-EN 12056-3 wzór (1)", 2),
            Krok(f"Pole {p0.id}: przepływ dla przelewów awaryjnych", "Q_aw = F_R·r·A·C", f"{f(par.F_R, 1)}·{f(p0.Q, 2)}",
                 p0.Q_awar, "l/s", "tabl. 2 [NZW]", 2),
            Krok("Przepustowość przelewu 20×10 cm przy h = 8 cm", "Q = ⅔·μ·b·√(2g)·h^1,5", "⅔·0,6·0,20·√(2·9,81)·0,08^1,5",
                 przepustowosc_przelewu(0.20, 0.08), "l/s", "Poleni [W]", 2),
            Krok("Przepustowość rury spustowej DN100 (d_i = 96 mm), f = 0,33", "Q_RWP = 2,5·10⁻⁴·k_b^−0,167·d_i^2,667·f^1,667",
                 "2,5·10⁻⁴·0,25^−0,167·96^2,667·0,33^1,667", przepustowosc_rury_spustowej(96.0), "l/s", "[NZW]", 2),
            Krok(f"Pole {p0.id}: najdłuższa droga spływu i przyrost grubości izolacji spadkowej", "∆h = i·L_max",
                 f"{f(p0.spadek or spadek_min, 3)}·{f(p0.L_splywu, 2)}", p0.dh_spadkowa, "m", "", 3),
        ]

    # ---- dach zielony
    zielone = []
    for dd in dane.dachy:
        if dd.typ != "zielony":
            continue
        txt = " ".join((n or "").lower() for _, _, n in dd.warstwy)
        chk = {"bariera przeciwkorzenna": any(s in txt for s in ("korzen", "korzeń")),
               "warstwa drenażowa": "drena" in txt, "geowłóknina (filtracyjna)": "włókn" in txt or "wlokn" in txt,
               "substrat": "substrat" in txt or "ziem" in txt}
        V_ret = dd.pole * par.retencja_substratu / 1000.0
        zielone.append({"id": dd.id, "A": dd.pole, "V_ret": V_ret, "warstwy": chk})
        for k, v in chk.items():
            war.append(Warunek(f"Dach zielony {dd.id}: warstwa „{k}” w przegrodzie {dd.przegroda}", 1 if v else 0, ">=", 1, "",
                               "brief §9 pkt 3; schemat modelu §6", "W-119", nd=0))
    # ---- odwodnienia liniowe (HS bezprogowe, drzwi tarasowe P0, brama garażowa)
    liniowe = []
    m = dane.model
    k0 = dane.kondygnacje[0]["id"]
    if m is not None:
        for o in m.otwory():
            if o.typ in ("drzwi_przesuwne_HS", "brama") or (o.typ == "drzwi_zewn" and float(o.parapet or 0) <= 0.02):
                if o.kond != k0 and o.typ != "drzwi_przesuwne_HS":
                    continue
                szer = float(o.szer)
                if o.typ == "brama":
                    A_z = szer * 5.0
                    kl = "C250 (PN-EN 1433) — ruch samochodów osobowych"
                    psi = 1.0
                else:
                    A_z = szer * 3.0
                    kl = "A15 / B125 (taras, ruch pieszy)"
                    psi = 1.0
                naz = {"drzwi_przesuwne_HS": "drzwi przesuwne HS bez progu", "brama": "brama garażowa",
                       "drzwi_zewn": "drzwi zewnętrzne bezprogowe"}[o.typ]
                wys = "P0" if o.kond == k0 else o.kond
                Qo = r * A_z * psi
                L = szer + 0.20
                liniowe.append({"otwor": o.id, "opis": f"{naz} ({wys})", "L": L, "A": A_z, "Q": Qo, "klasa": kl,
                                "odbiornik": "zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej",
                                "z_modelu": False})
    for od in dane.dzialka.get("odwodnienia") or []:
        if od.get("typ") == "liniowe":
            liniowe.append({"otwor": od.get("id"), "opis": "odwodnienie liniowe z dzialka.yaml", "L": None, "A": None, "Q": None,
                            "klasa": od.get("klasa", "—"), "odbiornik": od.get("odbiornik", "—"), "z_modelu": True})
    # ---- retencja: zbiornik ≤ 5 m³ + niecka
    ret = dane.dzialka.get("retencja") or {}
    V_zb = par.V_zbiornika if par.V_zbiornika is not None else float((ret.get("zbiornik") or {}).get("V", 5.0) or 5.0)
    A_red = sum(p.A * p.psi for p in pola)
    skl = [(f"dach {p.id} ({p.typ})", p.A, p.psi) for p in pola]
    if par.podlaczone_utwardzenia:
        for u in dane.dzialka.get("utwardzenia") or []:
            a = u["poly"].area
            psi = PSI["kostka"] if "kostk" in str(u.get("nawierzchnia", "")) else 0.8
            A_red += a * psi
            skl.append((f"utwardzenie {u.get('id')}", a, psi))
    kf_nn = kf_red * par.k_f
    # dobór niecki (A_n) — iteracja: V_min(a) ≤ A_n·h i opróżnianie ≤ 24 h
    def niecka(A_n: float, kredyt_zb: float):
        A_inf = A_n            # niecka płytka: dno ≈ powierzchnia zwierciadła [UPR]
        Qi = 1000.0 * A_inf * kf_nn
        V, td = objetosc_bilansowa((A_red + A_n * 1.0) / 1e4, Qi)
        V_n = max(V - kredyt_zb, 0.0)
        return V_n, fb * V_n, td, Qi
    if par.A_niecki:
        A_n = par.A_niecki
    else:
        A_n = 2.0
        while A_n < 500:
            Va, Vma, td, Qi = niecka(A_n, 0.0)
            if Vma <= A_n * par.h_niecki and Vma / (Qi / 1000.0) / 3600.0 <= t_opr_max:
                break
            A_n += 0.5
    Va, Vma, tda, Qia = niecka(A_n, 0.0)
    Vb, Vmb, tdb, Qib = niecka(A_n, V_zb)
    t_opr = Vma / (Qia / 1000.0) / 3600.0 if Qia > 0 else float("inf")
    V_n = A_n * par.h_niecki
    ZWG = par.ZWG_ppt if par.ZWG_ppt is not None else float(wym("geotechnika", "ZWG_ppt", 3.8) or 3.8)
    war.append(Warunek("Pojemność szczelnego zbiornika (bez zgłoszenia)", V_zb, "<=", V_zb_max, "m³",
                       wym_zrodlo("wodkan", "zbiornik_opadowy_bez_zgloszenia_max"), "W-145"))
    war.append(Warunek("Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia)", V_n, ">=", Vma, "m³",
                       "Aquanet 2024 wzór (1), f_b", "W-143"))
    war.append(Warunek("Niecka: głębokość", par.h_niecki, "<=", 0.30, "m", "W-145 (≤ 0,3 m)", "W-145"))
    war.append(Warunek("Niecka: czas opróżniania", t_opr, "<=", t_opr_max, "h", wym_zrodlo("wodkan", "retencja_oproznianie_max"),
                       "W-143", nd=1))
    war.append(Warunek("Dno niecki nad maks. zwierciadłem wód gruntowych", ZWG - par.h_niecki, ">=",
                       float(wym("wodkan", "rozsaczanie_dno_nad_ZWG_min", 1.0) or 1.0), "m", "Aquanet 2024; W-144", "W-144"))
    # lokalizacja urządzeń z dzialka.yaml
    lok = []
    D = dane.dzialka.get("transform")
    from shapely.geometry import Point
    obr = dane.obrys_zabudowy
    if D is not None:
        if (ret.get("zbiornik") or {}).get("xy"):
            xy = tuple(D.do_budynku(ret["zbiornik"]["xy"]))
            lok.append(("zbiornik szczelny", xy, obr.distance(Point(*xy)), dane.dystans_do_granicy(xy)))
        if (ret.get("rozsaczanie") or {}).get("obrys"):
            P = D.poly_bud(ret["rozsaczanie"]["obrys"])
            c = P.representative_point()
            lok.append(("niecka / rozsączanie", (c.x, c.y), obr.distance(P), dane.dzialka["obrys"].exterior.distance(P)
                        if dane.dzialka.get("obrys") is not None else float("nan")))
    for nazwa, xy, d_f, d_g in lok:
        if "rozs" in nazwa or "niecka" in nazwa:
            war.append(Warunek(f"{nazwa}: odległość od fundamentów", d_f, ">=",
                               float(wym("wodkan", "rozsaczanie_odl_fundament_min", 3.0) or 3.0), "m", "W-144 (S-4)", "W-144"))
            war.append(Warunek(f"{nazwa}: odległość od granicy działki", d_g, ">=",
                               float(wym("wodkan", "rozsaczanie_odl_granica_min", 2.0) or 2.0), "m", "W-144", "W-144"))
    kroki["ret"] = [
        Krok("Powierzchnia zredukowana zlewni (dachy)", "A_red = Σψ_i·A_i", " + ".join(f"{f(p, 2)}·{f(a, 1)}" for _, a, p in skl),
             A_red, "m²", "Aquanet 2024 tab. 2 (W-143)", 1),
        Krok("Zdolność chłonna niecki", "Q_inf = 1000·A_inf·k_f,nn = 1000·A_n·0,5·k_f", f"1000·{f(A_n, 1)}·{fa(kf_nn)}", Qia,
             "l/s", "Aquanet 2024 wzór (2); k_f [ZAŁ — badania]", 3),
        Krok(f"Objętość obliczeniowa (czasza niecki zasilana opadem ψ = 1,0), t_d = {tda} min",
             "V_obl = max_td[0,06·q(t_d)·(A_red + A_n)·t_d − 0,06·Q_inf·t_d]",
             f"0,06·{f(q_panda(tda), 2)}·{fa((A_red + A_n) / 1e4, 4)}·{tda} − 0,06·{f(Qia, 3)}·{tda}", Va, "m³",
             "Aquanet 2024 wzór (1); PANDa 2050 C10", 2),
        Krok("Minimalna objętość niecki (zbiornik ≤ 5 m³ pełny — bez zaliczenia)", "V_min = f_b·V_obl", f"{f(fb, 1)}·{f(Va, 2)}",
             Vma, "m³", "f_b wg W-143", 2),
        Krok("Wariant: zbiornik pusty na początku opadu (zaliczenie V_zb)", "V_min' = f_b·max(V_obl − V_zb; 0)",
             f"{f(fb, 1)}·max({f(Va, 2)} − {f(V_zb, 1)}; 0)", Vmb, "m³", "", 2),
        Krok("Przyjęta niecka (ogród deszczowy)", "A_n × h", f"{f(A_n, 1)} × {f(par.h_niecki, 2)}", V_n, "m³", "W-145", 2),
        Krok("Czas opróżniania niecki", "t = V_min/Q_inf", f"{f(Vma, 2)}/{f(Qia / 1000, 5)}/3600", t_opr, "h", "", 1),
    ]
    retencja = {"A_red": A_red, "skladniki": skl, "V_zb": V_zb, "A_n": A_n, "V_n": V_n, "V_obl_a": Va, "V_min_a": Vma,
                "V_min_b": Vmb, "t_d": tda, "Q_inf": Qia, "t_opr": t_opr, "kf": par.k_f, "lokalizacje": lok}
    # ---- skrzynki rozsączające (wariant opcjonalny)
    if par.skrzynki:
        L, B, H = par.skrzynki
    else:
        L, B, H = 2.4, 1.2, 0.66
        while True:
            A_inf = L * B + 0.5 * 2 * (L + B) * H
            Qi = 1000 * A_inf * kf_nn
            V, _ = objetosc_bilansowa(A_red / 1e4, Qi)
            if fb * V <= L * B * H * par.porowatosc_skrzynek or L > 30:
                break
            L += 1.2
    A_inf = L * B + 0.5 * 2 * (L + B) * H
    Qi = 1000 * A_inf * kf_nn
    V, tds = objetosc_bilansowa(A_red / 1e4, Qi)
    skr = {"L": L, "B": B, "H": H, "A_inf": A_inf, "Q_inf": Qi, "V_obl": V, "t_d": tds, "V_min": fb * V,
           "V_netto": L * B * H * par.porowatosc_skrzynek, "t_opr": fb * V / (Qi / 1000) / 3600 if Qi else float("inf")}
    # ---- bilans roczny (miesięczny) zbiornika
    op = opady_imgw()
    A_dach_zb = sum(p.A * p.psi for p in pola)
    S = 0.0
    rows = []
    tot = {"dop": 0.0, "pob": 0.0, "pokr": 0.0, "prz": 0.0}
    for mi, P_mm in enumerate(op["miesiace_mm"], start=1):
        dop = P_mm / 1000.0 * A_dach_zb * par.eta_filtra
        pob = par.podlewanie_A * par.podlewanie_mm_mies.get(mi, 0.0) / 1000.0
        dost = S + dop
        uzyte = min(dost, pob)
        S = dost - uzyte
        prz = max(0.0, S - V_zb)
        S = min(S, V_zb)
        rows.append([mi, P_mm, dop, pob, uzyte, prz, S])
        tot["dop"] += dop
        tot["pob"] += pob
        tot["pokr"] += uzyte
        tot["prz"] += prz
    bil = {"wiersze": rows, "suma": tot, "pokrycie": tot["pokr"] / tot["pob"] if tot["pob"] else 1.0, "P_rok": op["rok_mm"],
           "zrodlo": op["zrodlo"]}
    zal += [f"k_f gruntu = {fa(par.k_f)} m/s (piaski średnie) [ZAŁ — wymagane badania, E-04]; k_f,nn = {f(kf_red, 1)}·k_f.",
            f"Zbiornik szczelny V = {f(V_zb, 1)} m³ (dzialka.yaml / W-145), przelew do niecki; wody z utwardzeń "
            + ("odprowadzane do zbiornika." if par.podlaczone_utwardzenia else "spływają na przyległe powierzchnie biologicznie czynne (W-018)."),
            "Bilans roczny: miesięczny (normy IMGW 1991–2020, Poznań), podlewanie V–IX [ZAŁ]; filtr deszczówki η = 0,9 [ZAŁ]."]
    return WynikDeszcz(dane=dane, par=par, pola=pola, odwodnienia_liniowe=liniowe, retencja=retencja, skrzynki=skr,
                       bilans_roczny=bil, dach_zielony=zielone, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikDeszcz) -> Raport:
    d = w.dane
    R = Raport("Odwodnienie dachów i zagospodarowanie wód opadowych",
               f"Obiekt: {d.nazwa}. PN-EN 12056-3:2002; metodyka Aquanet 2024 (PANDa 2050, C = 10 lat). Dane przykładowe oznaczono [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §28–29, §126, §319 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-018, W-019, W-142…W-146.",
             "PN-EN 12056-3:2002 (PL, aktualna); PN-EN 1253-2 (wpusty dachowe); PN-EN 1433 (odwodnienia liniowe).",
             "Aquanet S.A., Załącznik C (2024) — metodyka bilansowa, PANDa 2050 RCP 4.5 Poznań-Ławica C10; DWA-A 138-1:2024 (tło).",
             "Wariant bazowy (D-05): szczelny zbiornik ≤ 5 m³ + przelew do niecki (ogród deszczowy ≤ 0,3 m); skrzynki rozsączające "
             "wyłącznie jako opcja po stanowisku PGW Wody Polskie (PW art. 16 pkt 65 lit. f, art. 389 pkt 6)."] + w.zalozenia)
    R.h(2, "2. Pola dachów — wpusty, spadki, przelewy awaryjne, rury spustowe")
    R.tab(["Pole", "Rodzaj", "A [m²]", "ψ", "Q [l/s]", "Wpusty", "ΣQ_wp [l/s]", "Spadek", "L_spł [m]", "∆h spadk. [cm]",
           "Q_aw [l/s]", "Przelewy", "Q_prz [l/s]", "h_spiętrz. [cm]", "q_woda [kN/m²]"],
          [[p.id, p.typ, f(p.A, 1), f(p.psi, 2), f(p.Q, 2),
            f"{p.n_wpustow}× " + ", ".join(f"DN{w.get('dn') or 100}" + (" (prop.)" if w.get("propozycja") else "") for w in p.wpusty[:3]),
            f(p.Q_wpustow, 1), f(p.spadek, 3) if p.spadek is not None else "brak", f(p.L_splywu, 1), f(100 * p.dh_spadkowa, 1),
            f(p.Q_awar, 2), f"{len(p.przelewy)}× " + ", ".join(f"{f(100 * float(x.get('szer', 0.2)), 0)}×{f(100 * float(x.get('wys', 0.1)), 0)}"
                                                              for x in p.przelewy[:3]),
            f(p.Q_przelewow, 2), f(100 * p.h_spietrzenia, 1), f(p.obc_woda, 2)] for p in w.pola], "llrrrlrrrrrlrrr")
    R.kroki(w.kroki["dach"])
    for p in w.pola:
        if p.uwagi:
            R.p(f"**Pole {p.id}:** " + "; ".join(p.uwagi) + ".")
    R.tab(["Rura", "Pole", "DN", "d_i [mm]", "Trasa", "Odbiornik", "Q [l/s]", "Q_RWP [l/s]"],
          [[r.get("id"), p.id, str(r.get("dn")), f(r["d_i"], 0), r.get("trasa", "—"), r.get("do", "—"), f(r["Q"], 2),
            f(r["Q_RWP"], 2)] for p in w.pola for r in p.rury], "llrrllrr")
    R.p("Obciążenie wodą spiętrzoną przy zablokowanych wpustach (q_woda) przekazać do obliczeń konstrukcji stropodachów "
        "(obciążenie wyjątkowe/zmienne wg decyzji konstruktora).")
    if w.dach_zielony:
        R.h(3, "2.1 Dach zielony")
        for z in w.dach_zielony:
            R.lista([f"{z['id']}: A = {f(z['A'], 1)} m²; retencja substratu i warstwy drenażowej ≈ {f(z['V_ret'], 2)} m³ "
                     f"({f(w.par.retencja_substratu, 0)} dm³/m² [ZAŁ — dane producenta]); ψ = 0,5 (bilans), C = 1,0 (wpusty).",
                     "Warstwy w przegrodzie: " + ", ".join(f"{k}: {'jest' if v else '**brak**'}" for k, v in z["warstwy"].items()) + ".",
                     "Przy attyce i wpustach opaska żwirowa ≥ 0,3–0,5 m (strefa bez roślin, kontrola wpustów) [ZAŁ; brief §9 pkt 3]."])
    R.h(2, "3. Odwodnienia liniowe (drzwi bezprogowe, brama garażowa)")
    if w.odwodnienia_liniowe:
        R.tab(["Otwór", "Opis", "L [m]", "A zlewni [m²]", "Q [l/s]", "Klasa obciążenia", "Odbiornik"],
              [[o["otwor"], o["opis"], f(o["L"], 2) if o["L"] else "—", f(o["A"], 1) if o["A"] else "—",
                f(o["Q"], 2) if o["Q"] else "—", o["klasa"], o["odbiornik"]] for o in w.odwodnienia_liniowe], "llrrrll")
        R.p("Odwodnienie liniowe przy drzwiach bez progu: korytko przed progiem na całej szerokości + 0,1 m z każdej strony, "
            "spadek nawierzchni tarasu/podjazdu od budynku ≥ 1,5–2 %, ruszt szczelinowy; posadzka wewnętrzna ≥ 2 cm nad rusztem "
            "[ZAŁ; brief §9 pkt 4]. Odpływ przez osadnik do zbiornika lub niecki.")
    else:
        R.p("Brak drzwi bezprogowych i bram w modelu.")
    R.h(2, "4. Zbiornik ≤ 5 m³ i niecka (wariant bazowy)")
    R.kroki(w.kroki["ret"])
    if w.retencja["lokalizacje"]:
        R.tab(["Urządzenie", "x, y (układ budynku)", "Odl. od budynku [m]", "Odl. od granicy [m]"],
              [[n, f"{f(xy[0])}; {f(xy[1])}", f(a, 2), f(b, 2)] for n, xy, a, b in w.retencja["lokalizacje"]], "llrr")
    R.h(3, "4.1 Bilans roczny zbiornika (normy opadowe IMGW 1991–2020)")
    R.tab(["Mies.", "Opad [mm]", "Dopływ [m³]", "Podlewanie [m³]", "Pokryte [m³]", "Przelew do niecki [m³]", "Stan końcowy [m³]"],
          [[r[0], f(r[1], 1), f(r[2], 2), f(r[3], 2), f(r[4], 2), f(r[5], 2), f(r[6], 2)] for r in w.bilans_roczny["wiersze"]],
          "rrrrrrr")
    s = w.bilans_roczny["suma"]
    R.p(f"Rocznie: dopływ {f(s['dop'], 1)} m³, zapotrzebowanie na podlewanie {f(s['pob'], 1)} m³, pokryte {f(s['pokr'], 1)} m³ "
        f"({f(100 * w.bilans_roczny['pokrycie'], 0)} %), przelew do niecki {f(s['prz'], 1)} m³. Opad roczny {f(w.bilans_roczny['P_rok'], 1)} mm "
        f"({w.bilans_roczny['zrodlo']}).")
    R.h(2, "5. Wariant opcjonalny: skrzynki rozsączające")
    k = w.skrzynki
    R.kroki([Krok(f"Skrzynki {f(k['L'], 2)} × {f(k['B'], 2)} × {f(k['H'], 2)} m — powierzchnia infiltracji",
                  "A_inf = L·B + ½·2(L + B)·H", "", k["A_inf"], "m²", "Aquanet 2024", 2),
             Krok("Zdolność chłonna", "Q_inf = 1000·A_inf·k_f,nn", "", k["Q_inf"], "l/s", "", 3),
             Krok(f"V_obl (t_d = {k['t_d']} min) / V_min = f_b·V_obl", "", f"{f(k['V_obl'], 2)} / {f(k['V_min'], 2)}", k["V_min"], "m³", "", 2),
             Krok("Objętość netto skrzynek (porowatość 95 %)", "V_n = L·B·H·0,95", "", k["V_netto"], "m³", "dane producentów [W]", 2),
             Krok("Czas opróżniania", "t = V_min/Q_inf", "", k["t_opr"], "h", "≤ 24 h", 1)])
    R.p("Skrzynki: osadnik przed urządzeniem; odległości wg W-144; wymagają stanowiska PGW Wody Polskie / pozwolenia "
        "wodnoprawnego (D-05) — dlatego nie stanowią wariantu bazowego.")
    R.h(2, "6. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("PN-EN 12056-3:2002 — p. 4 (Q = r·A·C), tabl. 2 (współczynnik ryzyka), rury spustowe [NZW — treść płatna]",
             "Aquanet S.A., Załącznik C — Metodyka obliczania niezbędnej objętości zbiorników detencyjno-retencyjnych, 2024, wzory (1)–(2), tab. 2–3",
             "IMGW-PIB, Normy klimatyczne 1991–2020, Poznań (12330) — sumy opadów https://klimat.imgw.pl/pl/climate-normals/OPAD_SUMA",
             "Dąbrowski W., Dąbrowska B., Jasik H., Odwadnianie dachów — wymiarowanie rynien, Rynek Instalacyjny 12/2015 (r = 0,03–0,05 l/(s·m²))",
             "Rejestr wymagań W-018, W-019, W-119, W-142…W-146; brief §9 (wymagania Inwestora 25.09.2026)")
    return R
