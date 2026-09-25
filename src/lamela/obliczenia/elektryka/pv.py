"""Instalacja fotowoltaiczna ≤ 6,5 kWp: dobór modułów i falownika, rozmieszczenie na dachu, produkcja roczna (PVGIS 5.3,
Poznań), autokonsumpcja z symulacji godzinowej (dane do EP), konfiguracja łańcuchów i zabezpieczenia DC/AC.

Podstawy (W-194, R6-76…R6-80, R7-I01…I08):

* **PB art. 29 ust. 4 pkt 3 lit. c** (brzmienie Dz.U. 2025 poz. 1847) — PV > 6,5 kW wymaga uzgodnienia z rzeczoznawcą ppoż.,
  zawiadomienia PSP i planu dla ekip ratowniczych → **moc modułów (suma z tabliczek, OZE art. 2 pkt 19b lit. b) ≤ 6,5 kWp**;
  falownik ≤ 6,5 kW [ZAŁ R1-35]; mikroinstalacja na zgłoszenie do OSD (Pr. energ. art. 7 ust. 8d4).
* **Produkcja** — PVGIS 5.3 (JRC KE), baza SARAH3/ERA5 2005–2023, straty systemowe 14 %, pobrano 2026-09-25 (``inst_dane``);
  wariant rzędów na południe 15° (S15) lub wschód–zachód 10° (EW10) [ZAŁ — dach płaski]; brak sieci → dane zapisane;
  brak danych → wartość literaturowa 950 kWh/kWp [W].
* **Autokonsumpcja** — bilans godzinowy (PVGIS seriescalc 2019 przeskalowany do średniej wieloletniej × profil zużycia:
  gospodarstwo domowe (profil dobowy typu H0 [UPR]), pompa ciepła (TMY Poznań, COP(θ_e) z danych PC), c.w.u. (ładowanie
  w godzinach produkcji PV lub nocą), wentylacja, pompy); **do EP liczy się wyłącznie energia PV zużyta przez systemy
  techniczne (H, W, pomocnicze), w = 0** (metodologia tab. 1; R6-15; D-07) — przypisanie proporcjonalne do udziału
  godzinowego zużycia [UPR — brak wytycznych ministerialnych].
* **PN-HD 60364-7-712:2016-05** — SPD DC (712.443), RCD typ B lub wg 712.530.3.101, uziemienie funkcjonalne w jednym punkcie;
  zabezpieczenia łańcuchów niewymagane, gdy (N_p − 1)·I_sc ≤ I_R (prąd wsteczny modułu) [W]; przewody DC H1Z2Z2-K
  (PN-EN 50618); I_z ≥ 1,25·I_sc,STC; U_oc,max = N_s·U_oc·(1 + β·(θ_min − 25)).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..inst_wspolne import (DaneBudynku, Krok, Raport, Warunek, f, fa, pvgis_godzinowo, pvgis_miesiecznie, tmy, wym,
                            wym_zrodlo)

MODUL_PRZYKLAD = {"model": "PV-430 TOPCon (dane przykładowe)", "P": 430.0, "U_oc": 38.9, "I_sc": 14.0, "U_mpp": 32.4, "I_mpp": 13.3,
                  "beta_Uoc": -0.0025, "gamma_Umpp": -0.0030, "dl": 1.722, "szer": 1.134, "I_R": 25.0}
FALOWNIK_PRZYKLAD = {"model": "FAL-6K-3P (dane przykładowe)", "P_AC": 6.0, "U_dc_max": 1000.0, "U_mppt": (160.0, 950.0),
                     "I_mppt_max": 16.0, "n_mppt": 2, "SPD_DC_wbudowany": True}


def pobierz_pvgis(lat: float = 52.40, lon: float = 16.93, angle: float = 15, aspect: float = 0, timeout: float = 30.0) -> dict | None:
    """Próba pobrania PVcalc z API PVGIS 5.3 (JRC). Zwraca słownik z 'E_m', 'E_y' lub None (brak sieci)."""
    import json
    import urllib.request
    url = (f"https://re.jrc.ec.europa.eu/api/v5_3/PVcalc?lat={lat}&lon={lon}&peakpower=1&loss=14&angle={angle}"
           f"&aspect={aspect}&outputformat=json")
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            d = json.loads(r.read().decode("utf-8"))
        return {"E_m": [m["E_m"] for m in d["outputs"]["monthly"]["fixed"]], "E_y": d["outputs"]["totals"]["fixed"]["E_y"], "url": url}
    except Exception:
        return None


# profil dobowy zużycia gospodarstwa domowego (udziały godzinowe, czas lokalny; kształt typu H0 [UPR])
PROFIL_H0 = np.array([0.55, 0.45, 0.40, 0.40, 0.40, 0.45, 0.70, 1.00, 1.05, 0.95, 0.90, 0.95, 1.10, 1.05, 0.95, 0.90, 1.00, 1.25,
                      1.55, 1.70, 1.65, 1.45, 1.15, 0.80])
SEZON_H0 = np.array([1.20, 1.15, 1.05, 0.95, 0.90, 0.85, 0.85, 0.85, 0.90, 1.00, 1.10, 1.20])


@dataclass
class ParametryPV:
    P_max_kWp: float | None = None
    modul: dict = field(default_factory=lambda: dict(MODUL_PRZYKLAD))
    falownik: dict = field(default_factory=lambda: dict(FALOWNIK_PRZYKLAD))
    wariant: str = "auto"              # auto | S15 | EW10
    odstep_od_krawedzi: float = 1.0    # m — strefa brzegowa (wiatr, attyka, LPS) [ZAŁ]
    h_slonca_min: float = 14.2         # ° — 21.12, południe, Poznań (90 − 52,4 − 23,44)
    theta_min: float = -25.0           # °C — do U_oc,max [ZAŁ]
    theta_cell_max: float = 70.0       # °C [ZAŁ]
    E_gospodarstwo: float | None = None  # kWh/a (AGD, oświetlenie) — domyślnie 2500 + 300·N [ZAŁ]
    cwu_w_godzinach_pv: bool = True
    L_DC: float | None = None          # m — trasa DC dach → falownik
    s_DC: float = 6.0                  # mm² H1Z2Z2-K
    dU_DC_max: float = 1.0             # % [ZAŁ]
    siec: bool = False                 # próba pobrania PVGIS przy każdym wywołaniu


@dataclass
class WynikPV:
    dane: DaneBudynku
    par: ParametryPV
    n_mod: int
    P_kWp: float
    wariant: str
    dach: dict
    E_m: list
    E_y: float
    zrodlo_danych: str
    sym: dict
    lancuchy: dict
    dc: dict
    warunki: list
    kroki: dict
    zalozenia: list

    def do_dict(self) -> dict:
        s = self.sym
        return {"n_modulow": self.n_mod, "P_kWp": round(self.P_kWp, 2), "wariant": self.wariant, "E_PV_kWh_a": round(self.E_y, 0),
                "autokonsumpcja": round(s["autokonsumpcja"], 3), "pokrycie": round(s["pokrycie"], 3),
                "do_EP": {"E_PV_uzyta_H_kWh_a": round(s["E_auto_H"], 0), "E_PV_uzyta_W_kWh_a": round(s["E_auto_W"], 0),
                          "E_PV_uzyta_pom_kWh_a": round(s["E_auto_pom"], 0), "E_PV_uzyta_H_W_pom_miesiecznie_kWh":
                          [round(x, 1) for x in s["m_auto_tech"]], "w_PV": 0.0,
                          "metoda": "bilans godzinowy, przypisanie proporcjonalne [UPR]"}}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


def _dach_pv(dane: DaneBudynku, par: ParametryPV):
    kand = [d for d in dane.dachy if d.typ == "plaski"] or [d for d in dane.dachy if d.typ == "zielony"]
    if not kand:
        return None
    d = max(kand, key=lambda d: (d.rzedna, d.pole))
    A_uz = d.obrys.buffer(-par.odstep_od_krawedzi, join_style=2)
    return {"id": d.id, "typ": d.typ, "A": d.pole, "A_uz": float(A_uz.area) if not A_uz.is_empty else 0.0, "rzedna": d.rzedna,
            "attyka": d.attyka_wys or 0.0}


def oblicz_pv(dane: DaneBudynku, par: ParametryPV | None = None, ogrzewanie=None, woda=None, bilans=None,
              wentylacja_m3h: float = 330.0) -> WynikPV:
    par = par or ParametryPV()
    Pmax = par.P_max_kWp if par.P_max_kWp is not None else float(wym("elektryka", "PV_moc_modulow_max", 6.5) or 6.5)
    mod, fal = par.modul, par.falownik
    war: list[Warunek] = []
    kroki: dict[str, list] = {}
    zal: list[str] = [f"Moduł: {mod['model']}; falownik: {fal['model']} [ZAŁ — zastąpić DTR wybranych wyrobów, E-13]."]
    n = int(math.floor(Pmax * 1000.0 / mod["P"] + 1e-9))
    dach = _dach_pv(dane, par)
    # powierzchnia na moduł: S15 (rzędy, bez zacienienia 21.12 w południe) i EW10 (grzbiety)
    b, a = mod["szer"], mod["dl"]
    s15 = math.radians(15.0)
    pitch = b * math.cos(s15) + b * math.sin(s15) / math.tan(math.radians(par.h_slonca_min))
    A_S15 = a * pitch
    A_EW = a * (b * math.cos(math.radians(10.0)) + 0.05) + a * 0.15
    wariant = par.wariant
    if wariant == "auto":
        wariant = "S15" if (dach and n * A_S15 <= dach["A_uz"]) else "EW10"
    A_mod = A_S15 if wariant == "S15" else A_EW
    if dach and n * A_mod > dach["A_uz"]:
        n = int(dach["A_uz"] // A_mod)
        zal.append(f"Liczba modułów ograniczona powierzchnią dachu {dach['id']} (bez strefy brzegowej {f(par.odstep_od_krawedzi, 1)} m).")
    P_kWp = n * mod["P"] / 1000.0
    h_mod = b * math.sin(math.radians(15.0 if wariant == "S15" else 10.0)) + 0.10
    kroki["dob"] = [
        Krok("Maksymalna liczba modułów (próg 6,5 kWp)", "n = ⌊P_max/P_mod⌋", f"⌊{f(Pmax * 1000, 0)}/{f(mod['P'], 0)}⌋", n, "szt.",
             "PB art. 29 ust. 4 pkt 3 lit. c; OZE art. 2 pkt 19b lit. b", 0),
        Krok("Moc zainstalowana", "P = n·P_mod", f"{n}·{f(mod['P'], 0)}", P_kWp, "kWp", "", 2),
        Krok("Rozstaw rzędów S15 (brak zacienienia 21.12, h_s = 14,2°)", "p = b·cos β + b·sin β/tg h_s", "", pitch, "m", "", 2),
        Krok("Powierzchnia dachu na moduł: S15 / EW10", "A_mod", f"{f(A_S15, 2)} / {f(A_EW, 2)}", A_mod, "m²", f"wariant {wariant}", 2),
    ]
    if dach:
        war.append(Warunek(f"Moduły mieszczą się na dachu {dach['id']} (bez strefy brzegowej)", n * A_mod, "<=", dach["A_uz"], "m²",
                           "[ZAŁ]", "W-194", nd=1))
        war.append(Warunek("Moduły nie wystają ponad attykę (wysokość zabudowy)", h_mod, "<=", dach["attyka"] if dach["attyka"] else 0.0, "m",
                           "D-15, W-033 (PV nie ponad attykę)", "W-033", nd=2))
    war.append(Warunek("Moc zainstalowana PV (suma mocy modułów)", P_kWp, "<=", Pmax, "kWp", wym_zrodlo("elektryka", "PV_moc_modulow_max"),
                       "W-194"))
    war.append(Warunek("Moc falownika", fal["P_AC"], "<=", float(wym("elektryka", "PV_falownik_max", 6.5) or 6.5), "kW",
                       wym_zrodlo("elektryka", "PV_falownik_max"), "W-194"))
    # produkcja
    pm = pvgis_miesiecznie()
    zr = f"PVGIS 5.3 (JRC KE), pobrano {pm.get('data_pobrania')} — {pm['zrodlo']}"
    if par.siec:
        net = pobierz_pvgis(angle=15 if wariant == "S15" else 10, aspect=0 if wariant == "S15" else -90)
        if net:
            zr = f"PVGIS 5.3 — pobrano w trakcie obliczeń ({net['url']})"
    if wariant == "S15":
        Em1 = pm["warianty"]["S15"]["E_m"]
    else:
        Em1 = [(e + w) / 2 for e, w in zip(pm["warianty"]["E10"]["E_m"], pm["warianty"]["W10"]["E_m"])]
    E_m = [x * P_kWp for x in Em1]
    E_y = sum(E_m)
    kroki["prod"] = [Krok(f"Produkcja roczna ({wariant}, {f(P_kWp, 2)} kWp)", "E = Σ E_m,1kWp·P", f"{f(sum(Em1), 1)}·{f(P_kWp, 2)}", E_y,
                          "kWh/a", zr, 0)]
    # symulacja godzinowa
    h = pvgis_godzinowo()
    if wariant == "S15":
        p1 = h["P_S15"] / 1000.0
    else:
        p1 = (h["P_E10"] + h["P_W10"]) / 2000.0
    p1 = p1 * (sum(Em1) / max(p1.sum(), 1e-9))
    PV = p1 * P_kWp                                        # kWh w godzinie (UTC)
    osoby = dane.osoby
    E_hh = par.E_gospodarstwo if par.E_gospodarstwo is not None else 2500.0 + 300.0 * osoby
    idx = np.arange(8760)
    doy = idx // 24
    mies = np.clip(np.searchsorted(np.cumsum([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]), doy, side="right"), 0, 11)
    h_lok = (idx % 24 + 1) % 24                              # UTC+1 [UPR — bez czasu letniego]
    L_hh = PROFIL_H0[h_lok] * SEZON_H0[mies]
    L_hh = L_hh / L_hh.sum() * E_hh
    T = tmy()["T2m"]
    if ogrzewanie is not None:
        pc = ogrzewanie.pc
        H = ogrzewanie.Phi_HL / (ogrzewanie.par.theta_i - (ogrzewanie.par.theta_e if ogrzewanie.par.theta_e is not None else -18.0))
        Q = H * np.clip(ogrzewanie.par.theta_granica - T, 0, None) / 1000.0
        from ..sanitarne.ogrzewanie import interp_ekstrap
        cop = np.maximum(interp_ekstrap(T, pc["T"], pc["COP"]), 1.0)
        Pmx = interp_ekstrap(T, pc["T"], pc["P"])
        L_H = np.minimum(Q, Pmx) / cop + np.maximum(Q - Pmx, 0.0)
        cop_w = pc["COP_cwu"]
    else:
        L_H = np.zeros(8760)
        cop_w = 3.0
    Qw_d = (woda.cwu["Q_d"] / 0.85) if woda is not None else 10.0            # kWh/d z uwzgl. strat zasobnika [ZAŁ]
    E_w_d = Qw_d / cop_w
    L_W = np.zeros(8760)
    for d_ in range(365):
        sl = slice(d_ * 24, d_ * 24 + 24)
        if par.cwu_w_godzinach_pv:
            top = np.argsort(PV[sl])[-3:]
            L_W[d_ * 24 + top] += E_w_d / 3.0
        else:
            L_W[d_ * 24 + np.array([1, 2, 3])] += E_w_d / 3.0
    P_went = 0.5 * wentylacja_m3h / 1000.0
    L_pom = np.full(8760, P_went) + np.where(Q > 0, 0.025, 0.0) if ogrzewanie is not None else np.full(8760, P_went)
    L = L_hh + L_H + L_W + L_pom
    auto = np.minimum(PV, L)
    L_tech = L_H + L_W + L_pom
    udz = np.divide(L_tech, L, out=np.zeros_like(L), where=L > 0)
    a_tech = auto * udz
    a_H = auto * np.divide(L_H, L, out=np.zeros_like(L), where=L > 0)
    a_W = auto * np.divide(L_W, L, out=np.zeros_like(L), where=L > 0)
    a_P = auto * np.divide(L_pom, L, out=np.zeros_like(L), where=L > 0)
    m_auto_tech = [float(a_tech[mies == k].sum()) for k in range(12)]
    sym = {"E_PV": float(PV.sum()), "E_L": float(L.sum()), "E_auto": float(auto.sum()), "E_exp": float((PV - auto).sum()),
           "E_imp": float((L - auto).sum()), "autokonsumpcja": float(auto.sum() / PV.sum()) if PV.sum() else 0.0,
           "pokrycie": float(auto.sum() / L.sum()) if L.sum() else 0.0, "E_auto_H": float(a_H.sum()), "E_auto_W": float(a_W.sum()),
           "E_auto_pom": float(a_P.sum()), "E_hh": E_hh, "E_H": float(L_H.sum()), "E_W": float(L_W.sum()), "E_pom": float(L_pom.sum()),
           "m_auto_tech": m_auto_tech, "m_PV": [float(PV[mies == k].sum()) for k in range(12)],
           "m_L": [float(L[mies == k].sum()) for k in range(12)], "m_auto": [float(auto[mies == k].sum()) for k in range(12)]}
    kroki["sym"] = [
        Krok("Zużycie gospodarstwa (AGD, oświetlenie)", "E_hh = 2500 + 300·N", f"2500 + 300·{osoby}", E_hh, "kWh/a", "[ZAŁ]", 0),
        Krok("Pompa ciepła — ogrzewanie (TMY, COP(θ_e))", "E_H = Σ Q_h/COP_h", "", sym["E_H"], "kWh/a", "moduł ogrzewania", 0),
        Krok("C.w.u. (COP c.w.u., ładowanie " + ("w godzinach produkcji PV" if par.cwu_w_godzinach_pv else "nocą") + ")",
             "E_W = 365·Q_W,d/(η_s·COP_W)", f"365·{f(Qw_d * 0.85, 2)}/(0,85·{f(cop_w, 1)})", sym["E_W"], "kWh/a", "moduł wody", 0),
        Krok("Autokonsumpcja", "Σmin(PV_h; L_h)/ΣPV_h", f"{f(sym['E_auto'], 0)}/{f(sym['E_PV'], 0)}", 100 * sym["autokonsumpcja"], "%",
             "bilans godzinowy [UPR]", 1),
        Krok("Pokrycie zużycia z PV", "Σmin(PV_h; L_h)/ΣL_h", "", 100 * sym["pokrycie"], "%", "", 1),
        Krok("Energia PV zużyta przez systemy techniczne (H + W + pomocnicze) — do EP z w = 0", "E_PV,tech",
             f"{f(sym['E_auto_H'], 0)} + {f(sym['E_auto_W'], 0)} + {f(sym['E_auto_pom'], 0)}",
             sym["E_auto_H"] + sym["E_auto_W"] + sym["E_auto_pom"], "kWh/a", "metodologia tab. 1 lp. 6 (R6-15, D-07)", 0),
    ]
    # łańcuchy
    n_str = 1 if (wariant == "S15" and n * mod["I_sc"] / n <= fal["I_mppt_max"]) else 2
    if n_str == 2 and fal["n_mppt"] < 2:
        n_str = 1
    Ns = math.ceil(n / n_str)
    Uoc_max = Ns * mod["U_oc"] * (1 + mod["beta_Uoc"] * (par.theta_min - 25.0))
    Umpp_min = (n // n_str) * mod["U_mpp"] * (1 + mod["gamma_Umpp"] * (par.theta_cell_max - 25.0))
    Umpp_max = Ns * mod["U_mpp"] * (1 + mod["gamma_Umpp"] * (par.theta_min - 25.0))
    lan = {"n_str": n_str, "Ns": Ns, "Uoc_max": Uoc_max, "Umpp_min": Umpp_min, "Umpp_max": Umpp_max, "I_sc": mod["I_sc"],
           "bezpieczniki": False}
    kroki["lan"] = [
        Krok(f"Łańcuchy: {n_str} × {Ns} modułów ({'1 łańcuch' if n_str == 1 else 'po jednym na MPPT'})", "", "", None),
        Krok("Maks. napięcie łańcucha (θ_min = −25 °C)", "U_oc,max = N_s·U_oc·(1 + β·(θ_min − 25))",
             f"{Ns}·{f(mod['U_oc'], 1)}·(1 + ({f(100 * mod['beta_Uoc'], 2)}/100)·({f(par.theta_min, 0)} − 25))", Uoc_max, "V", "PN-HD 60364-7-712", 0),
        Krok("Min. napięcie MPP (θ_ogniwa = 70 °C)", "U_mpp,min = N_s·U_mpp·(1 + γ·(θ − 25))", "", Umpp_min, "V", "", 0),
    ]
    war.append(Warunek("U_oc,max łańcucha ≤ U_DC,max falownika", Uoc_max, "<=", fal["U_dc_max"], "V", "DTR falownika", "W-194", nd=0))
    war.append(Warunek("U_mpp,min ≥ dolna granica MPPT", Umpp_min, ">=", fal["U_mppt"][0], "V", "DTR", "W-194", nd=0))
    war.append(Warunek("U_mpp,max ≤ górna granica MPPT", Umpp_max, "<=", fal["U_mppt"][1], "V", "DTR", "W-194", nd=0))
    war.append(Warunek("1,25·I_sc ≤ I_max wejścia MPPT", 1.25 * mod["I_sc"], "<=", fal["I_mppt_max"] * 1.25, "A",
                       "DTR (prąd zwarciowy wejścia ≥ 1,25·I_sc)", "W-194", nd=1))
    war.append(Warunek("Brak bezpieczników łańcuchowych: (N_p − 1)·I_sc ≤ I_R", 0.0, "<=", mod["I_R"], "A",
                       "PN-HD 60364-7-712 (1 łańcuch na MPPT) [W]", "W-194", nd=1))
    # DC
    hmax = dane.H_max
    L_DC = par.L_DC if par.L_DC is not None else (hmax + 12.0)
    I_mpp = mod["I_mpp"]
    rho = 0.0175 * (1 + 0.00393 * 50)                     # Ω·mm²/m przy 70 °C
    dU_DC = 2 * L_DC * I_mpp * rho / par.s_DC / (Umpp_min if Umpp_min > 0 else 300) * 100
    Iz_DC = 70.0                                           # A — H1Z2Z2-K 6 mm² w powietrzu [W, karta kabla]
    Ng = float(wym("elektryka", "Ng", 1.8) or 1.8)
    L_crit = 115.0 / Ng
    dc = {"L": L_DC, "dU": dU_DC, "Iz": Iz_DC, "L_crit": L_crit,
          "SPD": "SPD DC typ 2, U_CPV ≥ " + f(Uoc_max, 0) + " V (klasa 1000 V DC) przy falowniku — "
                 + ("wbudowany w falownik (sprawdzić DTR)" if fal.get("SPD_DC_wbudowany") else "w skrzynce przyłączeniowej DC"),
          "rozlacznik": f"rozłącznik izolacyjny DC ≥ {f(Uoc_max, 0)} V, ≥ {f(1.25 * mod['I_sc'], 1)} A (zwykle wbudowany w falownik)"}
    kroki["dc"] = [
        Krok(f"Spadek napięcia DC (H1Z2Z2-K {f(par.s_DC, 0)} mm², L = {f(L_DC, 1)} m)", "∆U = 2·L·I_mpp·ρ_70/s/U_mpp·100",
             f"2·{f(L_DC, 1)}·{f(I_mpp, 1)}·{f(rho, 4)}/{f(par.s_DC, 0)}/{f(Umpp_min, 0)}·100", dU_DC, "%", "[ZAŁ ≤ 1 %]", 2),
        Krok("Długość krytyczna DC dla SPD", "L_crit = 115/N_g", f"115/{f(Ng, 1)}", L_crit, "m", "IEC 60364-7-712 tabl. 712.1", 1),
    ]
    war.append(Warunek("Spadek napięcia po stronie DC", dU_DC, "<=", par.dU_DC_max, "%", "[ZAŁ]", "W-194"))
    war.append(Warunek("Obciążalność przewodu DC ≥ 1,25·I_sc", Iz_DC, ">=", 1.25 * mod["I_sc"], "A", "PN-HD 60364-7-712 [W]", "W-194", nd=1))
    zal += [f"Dach PV: {dach['id']} ({dach['typ']}, A = {f(dach['A'], 1)} m², użytkowa {f(dach['A_uz'], 1)} m²)." if dach else "Brak dachu płaskiego w modelu.",
            "Symulacja: PVGIS 2019 (godzinowo, przeskalowane do średniej wieloletniej) × TMY (ogrzewanie) — różne lata typowe [UPR]; "
            "czas lokalny = UTC+1 (bez czasu letniego) [UPR].",
            "Energia oddana do sieci nie obniża EP (R6-15)."]
    return WynikPV(dane=dane, par=par, n_mod=n, P_kWp=P_kWp, wariant=wariant, dach=dach or {}, E_m=E_m, E_y=E_y, zrodlo_danych=zr,
                   sym=sym, lancuchy=lan, dc=dc, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikPV) -> Raport:
    R = Raport("Instalacja fotowoltaiczna (≤ 6,5 kWp)", f"Obiekt: {w.dane.nazwa}. Dane wyrobów przykładowe [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["PB art. 29 ust. 4 pkt 3 lit. c; OZE art. 2 pkt 19, 19b; Pr. energ. art. 7 ust. 8d4–8d12 (W-194).",
             "PN-HD 60364-7-712:2016-05; PN-EN 62446-1:2016-08 (odbiór); PN-EN 50549-1:2019-02; NC RfG — certyfikat PTPiREE (od 01.01.2027 etap II)."]
            + w.zalozenia)
    R.h(2, "2. Dobór i rozmieszczenie")
    R.kroki(w.kroki["dob"])
    R.h(2, "3. Produkcja energii")
    R.kroki(w.kroki["prod"])
    s = w.sym
    R.tab(["Miesiąc", "E_PV [kWh]", "Zużycie [kWh]", "Autokonsumpcja [kWh]", "PV → systemy techniczne (EP) [kWh]"],
          [[m + 1, f(s["m_PV"][m], 0), f(s["m_L"][m], 0), f(s["m_auto"][m], 0), f(s["m_auto_tech"][m], 0)] for m in range(12)]
          + [["Rok", f(s["E_PV"], 0), f(s["E_L"], 0), f(s["E_auto"], 0), f(sum(s["m_auto_tech"]), 0)]], "rrrrr")
    R.h(2, "4. Autokonsumpcja (bilans godzinowy) — dane do EP")
    R.kroki(w.kroki["sym"])
    R.p(f"Energia oddana do sieci: {f(s['E_exp'], 0)} kWh/a; pobrana z sieci: {f(s['E_imp'], 0)} kWh/a. Autokonsumpcję zwiększa ładowanie "
        "c.w.u. i bufora w godzinach produkcji (sterowanie PC — wejście SG Ready / sterownik falownika).")
    R.h(2, "5. Łańcuchy, strona DC i AC, zabezpieczenia")
    R.kroki(w.kroki["lan"])
    R.kroki(w.kroki["dc"])
    R.lista([w.dc["SPD"], w.dc["rozlacznik"],
             "Przewody DC H1Z2Z2-K (PN-EN 50618), łańcuchy prowadzone parami (małe pętle indukcyjne), w osłonach UV; przejście przez dach szczelne.",
             "Strona AC: obwód falownika w RG (zestawienie obwodów — D „Falownik PV”), RCD typ B lub wg 712.530.3.101; wyłącznik PWP odcina AC; "
             "DC pod napięciem — oznakowanie przy RG, PWP i falowniku.",
             "Uziemienie funkcjonalne/ochronne konstrukcji PV w jednym punkcie, połączenie z GSU (712.444.5.5.101); przy LPS — odstęp "
             "separacyjny s od zwodów (raport ochrony odgromowej).",
             "Falownik z certyfikatem zgodności NC RfG z listy PTPiREE (R7-I05)."])
    R.h(2, "6. Sprawdzenia")
    R.war(w.warunki)
    R.h(2, "7. Wyniki do charakterystyki energetycznej")
    R.tab(["Wielkość", "Wartość"], [[k, (fa(v, 4) if isinstance(v, float) else str(v))] for k, v in w.do_dict()["do_EP"].items()], "lr")
    R.zrodlo("PVGIS 5.3, European Commission JRC — PVcalc/seriescalc/TMY, Poznań 52,40 N 16,93 E (https://re.jrc.ec.europa.eu/pvg_tools/), pobrano 2026-09-25",
             "PB art. 29 ust. 4 pkt 3 lit. c (Dz.U. 2025 poz. 1847); ustawa OZE art. 2 pkt 19b; Pr. energ. art. 7",
             "IEC 60364-7-712:2017 (PN-HD 60364-7-712:2016-05) — 712.443, 712.530.3.101, tabl. 712.1",
             "Metodologia EP (Dz.U. 2015 poz. 376 ze zm.) tab. 1 lp. 6; Chwieduk B., JCEEA 2016 (R6-15)")
    return R
