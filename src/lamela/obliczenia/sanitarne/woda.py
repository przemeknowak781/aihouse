"""Instalacja wodociągowa wody zimnej i ciepłej (c.w.u.) — zapotrzebowanie, przepływy, średnice, straty ciśnienia,
wymagane ciśnienie, wodomierz, zabezpieczenia przed przepływem zwrotnym, zasobnik c.w.u., cyrkulacja, dezynfekcja
termiczna, izolacja przewodów.

Podstawy (stan wg rejestru wymagań, W-130…W-137):

* **WT §113 ust. 4, zał. 1 lp. 4 → PN-B-01706:1992 (+Az1:1999)** — norma wycofana, wiążąca przez WT (tryb art. 102a PB).
  **Przepływ obliczeniowy (budynki mieszkalne, Σq_n ≤ 20 dm³/s, q_n < 0,5 dm³/s): q = 0,682·(Σq_n)^0,45 − 0,14**
  (W-132, R6-50). Przyjęto: q ≥ max q_n na odcinku (odcinek zasilający jeden punkt: q = q_n) i q ≤ Σq_n [UPR].
* **Wybór metody (uzasadnienie):** (1) WT powołuje datowaną PN-B-01706 — metoda wiążąca w trybie art. 102a PB;
  (2) metoda PN-EN 806-3 (jednostki obciążenia LU) daje dla budynków mieszkalnych wartości niższe niż PN-B-01706
  (Nowakowski E., „Obliczeniowe przepływy wody w budynkach mieszkalnych – wybór metody”, Rynek Instalacyjny 4/2011),
  więc PN-B-01706 jest po stronie bezpiecznej; (3) przejście LU → Q_D w PN-EN 806-3 jest wyłącznie graficzne
  (nomogram) — w bibliotece liczona jest kontrolnie suma LU i Q_T = 0,1·ΣLU oraz stosowane są warunki ciśnień
  PN-EN 806-3 p. 4.3 (ciśnienie statyczne w punkcie ≤ 500 kPa, ogrodowe ≤ 1000 kPa; ciśnienie wypływu ≥ 100 kPa).
* **WT §114** — ciśnienie przed punktem czerpalnym 0,05–0,60 MPa (W-130); **§115–117** — zestaw wodomierzowy
  w pomieszczeniu technicznym, za wodomierzem zabezpieczenie przed przepływem zwrotnym (W-131).
* **PN-EN 1717:2003** (WT zał. 1 lp. 5; aktualna PN-EN 1717+A1:2026-09, EN) — dobór zabezpieczeń do kategorii płynu.
* **WT §120** — c.w.u. 55–60 °C w punktach; dezynfekcja termiczna 70–80 °C (W-133; wybrano metodę cieplną, S-1);
  cyrkulacja w domu jednorodzinnym niewymagana (W-134). **WT zał. 2 pkt 1.5** — grubości izolacji (W-135).
* Straty liniowe: Darcy–Weisbach, λ z Colebrooka–White'a (k = 0,007 mm — rury wielowarstwowe PE-RT/Al/PE-RT [W]);
  straty miejscowe — udział 50 % strat liniowych (Σ∆p = 1,5·Σ∆p_l, przykład PWr) [W/UPR], chyba że podano Σζ.
* Wodomierz: q_obl ≤ Q3 (PN-EN ISO 4064 / MID; przykład PWr), strata ciśnienia ∆p = ∆p(Q3)·(q/Q3)², klasa ΔP63 [ZAŁ].
* Zasobnik c.w.u.: dobowe zapotrzebowanie (max z 50 dm³/(os·d) i metodologii EP: V_Wi = 1,4 dm³/(m²·d), R6-18)
  i pobór szczytowy (1 h) z mieszaniem do 40 °C [ZAŁ/W]; „reguła 3 litrów” dla braku cyrkulacji (R6 §3.6) [W].

Przykład sprawdzalny ręcznie (test): PWr, „Materiały pomocnicze do projektu instalacji wodociągowej”, tab. 3:
Σq_n = 1,82 dm³/s → q = 0,75 dm³/s = 2,7 m³/h → wodomierz Q3 = 4,0 m³/h DN20, ∆p ≈ 28 kPa.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import (C_W, G, RHO_W, DaneBudynku, Krok, Raport, Warunek, ceil_to, f, fa, manhattan, wym,
                            wym_zrodlo)
from .przybory import KATALOG, Pion, Przybor, grupy_pionow, przybory_z_modelu, zestawienie

# --------------------------------------------------------------------------------------------------
# Szeregi rur
# --------------------------------------------------------------------------------------------------
# rury wielowarstwowe PE-RT/Al/PE-RT (d_z × s → d_w) [dane producentów, W]
RURY_WIELOWARSTWOWE = [(16, 2.0), (20, 2.0), (25, 2.5), (32, 3.0), (40, 3.5), (50, 4.0), (63, 4.5)]
# przyłącze PE100 SDR11
RURY_PE100_SDR11 = [(32, 2.9), (40, 3.7), (50, 4.6), (63, 5.8)]
V_MAX = {"przylacze": 1.0, "glowny": 1.0, "pion": 1.5, "rozdzielczy": 1.5, "podejscie": 2.0}
# wodomierze: (DN, Q3 [m³/h]) — szereg R10 wg PN-EN ISO 4064 / MID (typowe DN domowe)
WODOMIERZE = [(15, 2.5), (20, 4.0), (25, 6.3), (32, 10.0), (40, 16.0)]
# kv [m³/h przy 1 bar] — wartości przykładowe z kart katalogowych [ZAŁ]
KV_EA = {15: 3.0, 20: 4.9, 25: 7.5, 32: 12.0, 40: 19.0}      # zawór antyskażeniowy EA (PWr: DN20, 2,7 m³/h → 30 kPa)
KV_FILTR = {15: 5.0, 20: 7.2, 25: 10.0, 32: 16.0, 40: 25.0}  # filtr z płukaniem wstecznym (PWr: DN20 → 14 kPa)
ZASOBNIKI = [150, 200, 250, 300, 400, 500]


def ni_wody(T: float) -> float:
    """Lepkość kinematyczna wody [m²/s] — wzór Poiseuille'a: ν = 1,79·10⁻⁶/(1 + 0,0337·T + 0,000221·T²)."""
    return 1.79e-6 / (1.0 + 0.0337 * T + 0.000221 * T * T)


def rho_wody(T: float) -> float:
    """Gęstość wody [kg/m³] (Kell, 1975 — dopasowanie 0–100 °C)."""
    return (999.83952 + 16.945176 * T - 7.9870401e-3 * T ** 2 - 46.170461e-6 * T ** 3 + 105.56302e-9 * T ** 4
            - 280.54253e-12 * T ** 5) / (1 + 16.879850e-3 * T)


def lambda_cw(Re: float, eps_d: float) -> float:
    """Współczynnik oporu liniowego λ: laminarny 64/Re (Re < 2300), turbulentny — Colebrook–White (iteracja)."""
    if Re < 1e-9:
        return 0.0
    if Re < 2300:
        return 64.0 / Re
    lam = 0.25 / (math.log10(eps_d / 3.7 + 5.74 / Re ** 0.9)) ** 2   # Swamee–Jain jako start
    for _ in range(30):
        new = (-2.0 * math.log10(eps_d / 3.71 + 2.51 / (Re * math.sqrt(lam)))) ** -2
        if abs(new - lam) < 1e-10:
            break
        lam = new
    return lam


def spadek_jednostkowy(q_dm3s: float, d_w_mm: float, T: float = 10.0, k_mm: float = 0.007) -> tuple[float, float, float]:
    """(v [m/s], R [kPa/m], λ) dla przepływu q [dm³/s] w rurze o d_w [mm]; Darcy–Weisbach: R = λ/d·ρv²/2."""
    d = d_w_mm / 1000.0
    v = q_dm3s / 1000.0 / (math.pi * d * d / 4.0)
    Re = v * d / ni_wody(T)
    lam = lambda_cw(Re, k_mm / d_w_mm)
    R = lam / d * rho_wody(T) * v * v / 2.0 / 1000.0
    return v, R, lam


def przeplyw_pn01706(sum_qn: float) -> float:
    """q = 0,682·(Σq_n)^0,45 − 0,14 [dm³/s] (PN-92/B-01706, budynki mieszkalne; Σq_n ≤ 20 dm³/s)."""
    if sum_qn <= 0:
        return 0.0
    return 0.682 * sum_qn ** 0.45 - 0.14


def przeplyw_odcinka(qn: list[float]) -> float:
    """Przepływ obliczeniowy odcinka: formuła PN-B-01706 ograniczona do [max q_n, Σq_n] [UPR]."""
    qn = [x for x in qn if x > 0]
    if not qn:
        return 0.0
    s = sum(qn)
    return min(s, max(max(qn), przeplyw_pn01706(s)))


def dobierz_rure(q: float, v_max: float, szereg=RURY_WIELOWARSTWOWE, dz_min: float = 0.0):
    """Najmniejsza rura z szeregu o v ≤ v_max i d_z ≥ dz_min → (d_z, s, d_w, v)."""
    last = None
    for dz, s in szereg:
        if dz < dz_min:
            continue
        dw = dz - 2 * s
        v = q / 1000.0 / (math.pi * (dw / 1000.0) ** 2 / 4.0)
        last = (dz, s, dw, v)
        if v <= v_max + 1e-9:
            return last
    return last


def dobierz_wodomierz(q_dm3s: float, dp_Q3_kPa: float = 63.0):
    """Wodomierz: najmniejszy o Q3 ≥ q_obl [m³/h]; ∆p = ∆p(Q3)·(q/Q3)² → (DN, Q3, q_m3h, ∆p)."""
    qh = q_dm3s * 3.6
    for dn, q3 in WODOMIERZE:
        if qh <= q3 + 1e-9:
            return dn, q3, qh, dp_Q3_kPa * (qh / q3) ** 2
    dn, q3 = WODOMIERZE[-1]
    return dn, q3, qh, dp_Q3_kPa * (qh / q3) ** 2


def dp_kv(q_dm3s: float, kv: float) -> float:
    """Strata ciśnienia armatury ∆p = 100·(q/kv)² [kPa] (q w m³/h, kv w m³/h przy 1 bar)."""
    return 100.0 * (q_dm3s * 3.6 / kv) ** 2


def grubosc_izolacji_WT(d_w_mm: float) -> float:
    """Minimalna grubość izolacji [mm] przy λ = 0,035 W/(m·K) — WT zał. 2 pkt 1.5 lp. 1–4 (W-135)."""
    if d_w_mm <= 22:
        return 20.0
    if d_w_mm <= 35:
        return 30.0
    if d_w_mm <= 100:
        return float(d_w_mm)
    return 100.0


def grubosc_rownowazna(d_z_mm: float, t_ref_mm: float, lam: float, lam_ref: float = 0.035) -> float:
    """Grubość izolacji o przewodności ``lam`` dająca ten sam opór cieplny co ``t_ref`` przy λ_ref (cylinder):
    ln((d+2t)/d)/λ = ln((d+2t_ref)/d)/λ_ref → t = d/2·[((d+2t_ref)/d)^(λ/λ_ref) − 1]."""
    return d_z_mm / 2.0 * (((d_z_mm + 2 * t_ref_mm) / d_z_mm) ** (lam / lam_ref) - 1.0)


def strata_ciepla_rury(d_z_mm: float, t_izol_mm: float, lam: float, dT: float, h_zew: float = 8.0) -> float:
    """Strata ciepła przewodu izolowanego [W/m]: q = ∆T / (ln(D/d)/(2πλ) + 1/(h·π·D))."""
    d = d_z_mm / 1000.0
    D = (d_z_mm + 2 * t_izol_mm) / 1000.0
    R = math.log(D / d) / (2 * math.pi * lam) + 1.0 / (h_zew * math.pi * D)
    return dT / R


# --------------------------------------------------------------------------------------------------
# Parametry i wyniki
# --------------------------------------------------------------------------------------------------
@dataclass
class ParametryWoda:
    osoby: int | None = None
    q_bytowe: float = 120.0             # dm³/(os·d) — dom jednorodzinny z pełnym wyposażeniem [ZAŁ, W]
    N_d: float = 1.5                    # współczynnik nierównomierności dobowej [ZAŁ]
    N_h: float = 3.0                    # współczynnik nierównomierności godzinowej [ZAŁ]
    podlewanie_A: float = 100.0         # m² podlewanej zieleni [ZAŁ]
    podlewanie_q: float = 3.0           # dm³/(m²·d) w dni podlewania (maj–wrzesień) [ZAŁ]
    cwu_q: float = 50.0                 # dm³/(os·d) przy 55 °C [ZAŁ, W]
    theta_cwu: float = 55.0
    theta_zw: float = 10.0
    theta_dez_punkt: float = 70.0       # WT §120 ust. 2a
    theta_dez_zas: float = 75.0         # nastawa zasobnika w cyklu dezynfekcji [ZAŁ]
    dezynfekcja_co_dni: int = 7         # [ZAŁ]
    p_sieci_min: float = 0.35           # MPa — ciśnienie dyspozycyjne w sieci [ZAŁ, warunki gestora]
    p_sieci_max: float = 0.60           # MPa — maks. ciśnienie statyczne w sieci [ZAŁ]
    przykrycie_sieci: float = 1.40      # m — oś przewodu sieci pod terenem [ZAŁ]
    przykrycie_przylacza: float = 1.40  # m — przykrycie przyłącza (do wierzchu rury) [ZAŁ]
    k_mm: float = 0.007
    udzial_miejscowych: float = 0.5     # Σ∆p_m = 0,5·Σ∆p_l [W — PWr]
    dp_podgrzewacz: float = 10.0        # kPa — zasobnik z wężownicą (strona wody użytkowej) [ZAŁ]
    dp_TZM: float = 20.0                # kPa — termostatyczny zawór mieszający [ZAŁ]
    dp_wodomierz_Q3: float = 63.0       # kPa — klasa ΔP63 [ZAŁ]
    reduktor_nastawa: float = 0.40      # MPa [ZAŁ]
    lambda_izol: float = 0.040          # W/(m·K) — pianka PE [ZAŁ]
    cyrkulacja: str = "auto"            # auto | czasowa | brak
    cyrk_h_dzien: float = 6.0           # h/d pracy pompy cyrkulacyjnej (czasowa) [ZAŁ]
    cyrk_dT: float = 5.0                # K — spadek temperatury w pętli (DVGW W 551) [W]
    theta_otocz: float = 20.0
    v_max: dict = field(default_factory=lambda: dict(V_MAX))
    P_PC_cwu_kW: float = 6.0            # moc PC w trybie c.w.u. (do czasu ładowania) [ZAŁ; z modułu ogrzewania]


@dataclass
class Odcinek:
    nr: int
    od: str
    do: str
    opis: str
    typ: str                  # przylacze|glowny|pion|rozdzielczy|podejscie
    medium: str               # ZW | CWU
    L: float
    skladniki: list           # [(Przybor, 'zw'|'cw')]
    rura: str = ""
    dz: float = 0.0
    s: float = 0.0
    dw: float = 0.0
    sum_qn: float = 0.0
    q: float = 0.0
    sum_LU: float = 0.0
    v: float = 0.0
    R: float = 0.0
    dp_l: float = 0.0
    dp_m: float = 0.0
    T: float = 10.0

    @property
    def dp(self) -> float:
        return self.dp_l + self.dp_m

    @property
    def objetosc_l(self) -> float:
        return math.pi * (self.dw / 1000.0) ** 2 / 4.0 * self.L * 1000.0


@dataclass
class Punkt:
    przybor: Przybor
    medium: str
    sciezka: list
    h: float
    dp_l: float
    dp_m: float
    dp_urz: float
    p_w: float

    @property
    def p_wym(self) -> float:
        return RHO_W * G * self.h / 1000.0 + self.dp_l + self.dp_m + self.dp_urz + self.p_w


@dataclass
class WynikWoda:
    dane: DaneBudynku
    par: ParametryWoda
    przybory: list
    piony: list
    wezly: dict
    odcinki: list
    punkty: list
    zapotrzebowanie: dict
    wodomierz: dict
    urzadzenia: dict
    zabezpieczenia_1717: list
    cwu: dict
    izolacje: list
    cisnienia: dict
    warunki: list
    kroki: dict
    zalozenia: list

    @property
    def punkt_krytyczny(self) -> Punkt:
        return max(self.punkty, key=lambda p: p.p_wym)

    def do_dict(self) -> dict:
        pk = self.punkt_krytyczny
        return {"q_obl_dm3s": round(self.wodomierz["q"], 3), "p_wym_kPa": round(pk.p_wym, 1),
                "punkt_krytyczny": f"{pk.przybor.id} {pk.przybor.typ} ({pk.medium})",
                "wodomierz": f"DN{self.wodomierz['DN']} Q3={self.wodomierz['Q3']}",
                "Q_d_sr_m3": round(self.zapotrzebowanie["Q_d_sr"], 3), "Q_h_max_m3": round(self.zapotrzebowanie["Q_h_max"], 3),
                "cwu_V_d_l": round(self.cwu["V_d"], 0), "zasobnik_l": self.cwu["V_zas"],
                "cyrkulacja": self.cwu["cyrkulacja"], "eta_W_d": self.cwu["eta_W_d"],
                "Q_W_nd_kWh_a": round(self.cwu["Q_W_nd_kWh_a"], 0),
                "dezynfekcja_kWh_a": round(self.cwu["dez_E_rok"], 0)}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


# --------------------------------------------------------------------------------------------------
# Sieć (topologia i geometria) — budowa automatyczna z modelu
# --------------------------------------------------------------------------------------------------
def _pom_techniczne(dane: DaneBudynku):
    t = [p for p in dane.pomieszczenia if p.rodzaj == "techniczne" and p.kond == dane.kondygnacje[0]["id"]]
    return t[0] if t else None


def _punkt_sieci(dane: DaneBudynku):
    """Punkt włączenia do sieci wodociągowej (układ budynku) i punkt wejścia do budynku."""
    from shapely.geometry import LineString, Point
    from shapely.ops import nearest_points
    D = dane.dzialka.get("transform")
    obrys0 = dane.obrysy.get(dane.kondygnacje[0]["id"])
    siec_line, proj_line = None, None
    if D is not None:
        for u in (dane.dzialka.get("uzbrojenie") or {}).get("istniejace", []) or []:
            if u.get("branza") == "woda" and u.get("linia"):
                siec_line = LineString(D.ring_bud(u["linia"]))
        for u in (dane.dzialka.get("uzbrojenie") or {}).get("projektowane", []) or []:
            if u.get("branza") == "woda" and u.get("linia"):
                proj_line = (LineString(D.ring_bud(u["linia"])), u.get("dl"))
    if proj_line is not None:
        ln, dl = proj_line
        a, b = Point(ln.coords[0]), Point(ln.coords[-1])
        if siec_line is not None and siec_line.distance(a) < siec_line.distance(b):
            a, b = b, a
        wej = nearest_points(obrys0.exterior, b)[0] if obrys0 is not None and not obrys0.is_empty else b
        L = float(dl) if dl else ln.length
        return (b.x, b.y), (wej.x, wej.y), L + wej.distance(a), "uzbrojenie projektowane (dzialka.yaml)"
    if siec_line is not None and obrys0 is not None and not obrys0.is_empty:
        p_obr, p_siec = nearest_points(obrys0.exterior, siec_line)
        return (p_siec.x, p_siec.y), (p_obr.x, p_obr.y), manhattan((p_siec.x, p_siec.y), (p_obr.x, p_obr.y)), \
            "najkrótsza trasa do sieci istniejącej [UPR]"
    # brak danych — założenie 15 m
    if obrys0 is not None and not obrys0.is_empty:
        x0, y0, x1, y1 = obrys0.bounds
        wej = ((x0 + x1) / 2, y1)
    else:
        wej = (0.0, 0.0)
    return (wej[0], wej[1] + 15.0), wej, 15.0, "brak sieci w dzialka.yaml — przyjęto 15 m [ZAŁ]"


def _zbuduj_siec(dane: DaneBudynku, przybory: list[Przybor], piony: list[Pion], par: ParametryWoda):
    k0 = dane.kondygnacje[0]["id"]
    wezly: dict[str, tuple] = {}
    zal: list[str] = []
    siec_xy, wej_xy, L_przyl, src = _punkt_sieci(dane)
    z_siec = dane.teren_z(siec_xy) - par.przykrycie_sieci
    wezly["SIEC"] = (siec_xy[0], siec_xy[1], z_siec, "teren")
    wezly["WEJ"] = (wej_xy[0], wej_xy[1], -0.5, k0)
    zal.append(f"Przyłącze: {src}; L = {f(L_przyl)} m; oś sieci {f(par.przykrycie_sieci)} m p.p.t. [ZAŁ].")
    tech = _pom_techniczne(dane)
    wod = dane.lok("wodomierz")
    if wod:
        wod_xy = wod[:2]
        zal.append("Wodomierz: lokalizacja z instalacje.yaml.")
    elif tech is not None:
        wod_xy = tech.centroid
        zal.append(f"Wodomierz: pomieszczenie techniczne {tech.id} (W-131).")
    else:
        wod_xy = (wej_xy[0], wej_xy[1])
        zal.append("Wodomierz: brak pomieszczenia technicznego w modelu — przy wejściu przyłącza [ZAŁ].")
    z0 = dane.rzedna(k0)
    wezly["WOD"] = (wod_xy[0], wod_xy[1], z0 + 0.5, k0)
    wezly["T0"] = (wod_xy[0] + 0.3, wod_xy[1], z0 + 0.5, k0)
    zas = dane.lok("zasobnik")
    zas_xy = zas[:2] if zas else ((tech.centroid[0] + 0.7, tech.centroid[1]) if tech else (wod_xy[0] + 0.7, wod_xy[1]))
    wezly["ZAS"] = (zas_xy[0], zas_xy[1], z0 + 1.5, k0)
    odc: list[Odcinek] = []

    def add(od, do, opis, typ, medium, L, skl):
        odc.append(Odcinek(nr=len(odc) + 1, od=od, do=do, opis=opis, typ=typ, medium=medium, L=round(max(L, 0.3), 2),
                           skladniki=skl))

    wszystkie_zw = [(p, "zw") for p in przybory if p.t.qn_zw > 0]
    wszystkie_cw = [(p, "cw") for p in przybory if p.t.qn_cw > 0]
    add("SIEC", "WEJ", "przyłącze wodociągowe (PE100 SDR11)", "przylacze", "ZW", L_przyl, wszystkie_zw + wszystkie_cw)
    add("WEJ", "WOD", "wejście do budynku → zestaw wodomierzowy", "glowny", "ZW",
        manhattan(wej_xy, wod_xy) + 1.5, wszystkie_zw + wszystkie_cw)
    add("WOD", "T0", "zestaw wodomierzowy (zawór, wodomierz, filtr, EA)", "glowny", "ZW", 1.0, wszystkie_zw + wszystkie_cw)
    if wszystkie_cw:
        add("T0", "ZAS", "zasilanie zasobnika c.w.u. (grupa bezpieczeństwa)", "glowny", "ZW",
            manhattan(wezly["T0"], zas_xy) + 1.0, wszystkie_cw)
    # zawory ogrodowe i punkty poza pionami
    w_pionach = {id(p) for pn in piony for p in pn.przybory}
    for p in przybory:
        if id(p) in w_pionach:
            continue
        nid = f"{p.id}"
        wezly[nid] = (p.xy[0], p.xy[1], p.z_wyl, p.kond)
        if p.t.qn_zw > 0:
            add("T0", nid, f"przewód do {p.t.nazwa.lower()} ({p.id})", "rozdzielczy", "ZW",
                manhattan(wezly["T0"], p.xy) + abs(p.z_wyl - (z0 + 0.5)) + 1.0, [(p, "zw")])
    # piony
    for medium, zrodlo in (("ZW", "T0"), ("CWU", "ZAS")):
        comp = "zw" if medium == "ZW" else "cw"
        for pn in piony:
            skl_p = [(p, comp) for p in pn.przybory if (p.t.qn_zw if comp == "zw" else p.t.qn_cw) > 0]
            if not skl_p:
                continue
            base = f"{pn.id}{medium[0]}@{k0}"
            wezly[base] = (pn.xy[0], pn.xy[1], z0 + 0.3, k0)
            add(zrodlo, base, f"przewód rozdzielczy do pionu {pn.id}", "glowny", medium,
                manhattan(wezly[zrodlo], pn.xy) + 0.5, skl_p)
            kond_list = [k["id"] for k in dane.kondygnacje]
            top = max(kond_list.index(k) for k in pn.kondygnacje)
            prev = base
            for i in range(0, top + 1):
                kid = kond_list[i]
                node = f"{pn.id}{medium[0]}@{kid}"
                if i > 0:
                    wezly[node] = (pn.xy[0], pn.xy[1], dane.rzedna(kid) + 0.3, kid)
                    skl_up = [(p, c) for p, c in skl_p if kond_list.index(p.kond) >= i]
                    add(prev, node, f"pion {pn.id} {kond_list[i - 1]}→{kid}", "pion", medium,
                        dane.kond(kond_list[i - 1])["wys"], skl_up)
                prev = node
                for pid in pn.pomieszczenia.get(kid, []):
                    lst = [p for p in pn.przybory if p.pom == pid and p.kond == kid]
                    sk = [(p, comp) for p in lst if (p.t.qn_zw if comp == "zw" else p.t.qn_cw) > 0]
                    if not sk:
                        continue
                    cx = sum(p.xy[0] for p, _ in sk) / len(sk)
                    cy = sum(p.xy[1] for p, _ in sk) / len(sk)
                    rn = f"R{medium[0]}_{pid}"
                    wezly[rn] = (cx, cy, dane.rzedna(kid) + 0.3, kid)
                    pom = dane.pom(pid)
                    add(node, rn, f"odgałęzienie do pom. {pid} {pom.nazwa if pom else ''}".strip(), "rozdzielczy",
                        medium, manhattan(pn.xy, (cx, cy)) + 0.5, sk)
                    for p, c in sk:
                        fn = f"{p.id}{medium[0]}"
                        wezly[fn] = (p.xy[0], p.xy[1], p.z_wyl, kid)
                        add(rn, fn, f"podejście: {p.t.nazwa.lower()} ({p.id})", "podejscie", medium,
                            manhattan((cx, cy), p.xy) + abs(p.h_wyl - 0.3), [(p, c)])
    return wezly, odc, zal


def _oblicz_odcinki(odc: list[Odcinek], par: ParametryWoda):
    for o in odc:
        qn = [(p.t.qn_zw if c == "zw" else p.t.qn_cw) for p, c in o.skladniki]
        o.sum_qn = sum(qn)
        o.q = przeplyw_odcinka(qn)
        o.sum_LU = sum((p.t.LU_zw if c == "zw" else p.t.LU_cw) for p, c in o.skladniki)
        o.T = par.theta_cwu if o.medium == "CWU" else par.theta_zw
        dz_min = max([p.t.dz_wod for p, _ in o.skladniki] + [16])
        if o.typ == "przylacze":
            r = dobierz_rure(o.q, par.v_max["przylacze"], RURY_PE100_SDR11, 32)
            o.rura = f"PE100 SDR11 {r[0]}×{f(r[1], 1)}"
            k = 0.01
        else:
            r = dobierz_rure(o.q, par.v_max.get(o.typ, 1.5), RURY_WIELOWARSTWOWE, dz_min if o.typ == "podejscie" else 16)
            o.rura = f"PE-RT/Al/PE-RT {r[0]}×{f(r[1], 1)}"
            k = par.k_mm
        o.dz, o.s, o.dw, _ = r
        o.v, o.R, _ = spadek_jednostkowy(o.q, o.dw, o.T, k)
        o.dp_l = o.R * o.L
        o.dp_m = par.udzial_miejscowych * o.dp_l


def _sciezka(odc: list[Odcinek], do: str) -> list[Odcinek]:
    by_do = {o.do: o for o in odc}
    out = []
    n = do
    while n in by_do:
        o = by_do[n]
        out.append(o)
        n = o.od
    return list(reversed(out))


# --------------------------------------------------------------------------------------------------
# Obliczenia główne
# --------------------------------------------------------------------------------------------------
def oblicz_wode(dane: DaneBudynku, par: ParametryWoda | None = None) -> WynikWoda:
    """Pełne obliczenia instalacji wodociągowej dla modelu (patrz docstring modułu)."""
    par = par or ParametryWoda()
    przybory = przybory_z_modelu(dane)
    if not przybory:
        raise ValueError("Brak przyborów sanitarnych w modelu (wyposazenie.yaml / instalacje.yaml: przybory_dodatkowe).")
    piony = grupy_pionow(dane, przybory)
    wezly, odc, zal = _zbuduj_siec(dane, przybory, piony, par)
    _oblicz_odcinki(odc, par)
    kroki: dict[str, list[Krok]] = {}
    war: list[Warunek] = []
    osoby = par.osoby or dane.osoby

    # ---- zapotrzebowanie
    Qd = osoby * par.q_bytowe / 1000.0
    Qpod = par.podlewanie_A * par.podlewanie_q / 1000.0
    Qdmax = par.N_d * Qd + Qpod
    Qhmax = par.N_h * Qdmax / 24.0
    zap = {"Q_d_sr": Qd, "Q_pod": Qpod, "Q_d_max": Qdmax, "Q_h_max": Qhmax, "osoby": osoby}
    kroki["zap"] = [
        Krok("Średnie dobowe zapotrzebowanie (bytowe)", "Q_d,śr = N·q_j", f"{osoby}·{f(par.q_bytowe, 0)}/1000", Qd, "m³/d",
             "q_j = 120 dm³/(os·d) [ZAŁ — dom jednorodzinny z pełnym wyposażeniem]", 3),
        Krok("Podlewanie zieleni (sezon V–IX)", "Q_pod = A·q_p", f"{f(par.podlewanie_A, 0)}·{f(par.podlewanie_q, 1)}/1000",
             Qpod, "m³/d", "[ZAŁ]", 3),
        Krok("Maksymalne dobowe", "Q_d,max = N_d·Q_d,śr + Q_pod", f"{f(par.N_d, 1)}·{f(Qd, 3)} + {f(Qpod, 3)}", Qdmax, "m³/d",
             "N_d = 1,5 [ZAŁ]", 3),
        Krok("Maksymalne godzinowe", "Q_h,max = N_h·Q_d,max/24", f"{f(par.N_h, 1)}·{f(Qdmax, 3)}/24", Qhmax, "m³/h",
             "N_h = 3,0 [ZAŁ]", 3),
    ]

    # ---- przepływ na wodomierzu
    o_wod = next(o for o in odc if o.od == "WOD")
    q = o_wod.q
    kroki["q"] = [
        Krok("Suma wypływów normatywnych (woda zimna + ciepła) na zestawie wodomierzowym", "Σq_n", "", o_wod.sum_qn,
             "dm³/s", "PN-92/B-01706 tabl. 1", 2),
        Krok("Przepływ obliczeniowy", "q = 0,682·(Σq_n)^0,45 − 0,14",
             f"0,682·({f(o_wod.sum_qn)})^0,45 − 0,14", przeplyw_pn01706(o_wod.sum_qn), "dm³/s",
             "PN-92/B-01706 (budynki mieszkalne); W-132", 3),
        Krok("Przepływ obliczeniowy przyjęty (≥ max q_n, ≤ Σq_n)", "q", "", q, "dm³/s", "[UPR]", 3),
        Krok("Kontrolnie PN-EN 806-3: suma jednostek obciążenia i Q_T", "Q_T = 0,1·ΣLU", f"0,1·{f(o_wod.sum_LU, 0)}",
             0.1 * o_wod.sum_LU, "l/s", "PN-EN 806-3 tabl. 2 (Q_D z nomogramu normy ≤ Q_T)", 2),
    ]

    # ---- wodomierz, filtr, EA
    dn, q3, qh, dpw = dobierz_wodomierz(q, par.dp_wodomierz_Q3)
    dn_arm = min(max(dn, 15), 40)
    kv_ea = KV_EA.get(dn_arm, 4.9)
    kv_f = KV_FILTR.get(dn_arm, 7.2)
    dp_ea = dp_kv(q, kv_ea)
    dp_f = dp_kv(q, kv_f)
    wodomierz = {"DN": dn, "Q3": q3, "q": q, "q_m3h": qh, "dp": dpw}
    urz = {"dp_wod": dpw, "dp_EA": dp_ea, "dp_filtr": dp_f, "dp_podgrzewacz": par.dp_podgrzewacz,
           "dp_TZM": par.dp_TZM, "kv_EA": kv_ea, "kv_filtr": kv_f, "DN_arm": dn_arm}
    kroki["wod"] = [
        Krok("Przepływ obliczeniowy na wodomierzu", "q_wod = 3,6·q", f"3,6·{f(q, 3)}", qh, "m³/h", "", 2),
        Krok("Dobór wodomierza (pierwszy o Q3 ≥ q_wod)", "q_wod ≤ Q3", f"{f(qh, 2)} ≤ {f(q3, 1)}", f"DN{dn}, Q3 = {f(q3, 1)} m³/h",
             "", "PN-EN ISO 4064 (MID); przykład PWr"),
        Krok("Strata ciśnienia na wodomierzu", "∆p_wod = ∆p(Q3)·(q_wod/Q3)²", f"{f(par.dp_wodomierz_Q3, 0)}·({f(qh)}/{f(q3, 1)})²",
             dpw, "kPa", "klasa ΔP63 [ZAŁ] — przyjąć z karty wyrobu", 1),
        Krok(f"Strata na zaworze antyskażeniowym EA DN{dn_arm}", "∆p_EA = 100·(q_wod/k_v)²", f"100·({f(qh)}/{f(kv_ea, 1)})²",
             dp_ea, "kPa", "k_v [ZAŁ — karta wyrobu]", 1),
        Krok(f"Strata na filtrze DN{dn_arm}", "∆p_F = 100·(q_wod/k_v)²", f"100·({f(qh)}/{f(kv_f, 1)})²", dp_f, "kPa",
             "k_v [ZAŁ — karta wyrobu]", 1),
    ]
    war.append(Warunek("Przepływ obliczeniowy ≤ Q3 wodomierza", qh, "<=", q3, "m³/h", "PN-EN ISO 4064 / MID", "W-131"))
    war.append(Warunek("Przykrycie przyłącza wodociągowego (ochrona przed przemarzaniem)", par.przykrycie_przylacza, ">=",
                       float(wym("wodkan", "przykrycie_wodociagu_min", 1.2) or 1.2), "m", wym_zrodlo("wodkan", "przykrycie_wodociagu_min"),
                       "W-141"))
    war.append(Warunek("Średnica wodomierza ≤ średnicy wewn. przewodu", dn, "<=", o_wod.dw, "mm", "praktyka (PWr)", "W-131"))

    # ---- punkty i ciśnienie wymagane
    punkty: list[Punkt] = []
    z_siec = wezly["SIEC"][2]
    for p in przybory:
        for comp, med in (("zw", "Z"), ("cw", "C")):
            qn = p.t.qn_zw if comp == "zw" else p.t.qn_cw
            if qn <= 0:
                continue
            node = f"{p.id}{med}" if f"{p.id}{med}" in {o.do for o in odc} else p.id
            sc = _sciezka(odc, node)
            if not sc:
                continue
            dpu = dpw + dp_ea + dp_f + ((par.dp_podgrzewacz + par.dp_TZM) if comp == "cw" else 0.0)
            punkty.append(Punkt(przybor=p, medium=("c.w.u." if comp == "cw" else "woda zimna"), sciezka=sc,
                                h=p.z_wyl - z_siec, dp_l=sum(o.dp_l for o in sc), dp_m=sum(o.dp_m for o in sc),
                                dp_urz=dpu, p_w=p.t.p_w))
    pk = max(punkty, key=lambda x: x.p_wym)
    p_wym = pk.p_wym
    kroki["p"] = [
        Krok(f"Najniekorzystniej położony punkt: {pk.przybor.t.nazwa.lower()} {pk.przybor.id} (kond. {pk.przybor.kond}, "
             f"pom. {pk.przybor.pom or '—'}), {pk.medium}", "", "", None),
        Krok("Wysokość geometryczna (oś sieci → wylewka)", "h_g = z_wyl − z_sieci", f"{f(pk.przybor.z_wyl)} − ({f(z_siec)})",
             pk.h, "m", "", 2),
        Krok("Ciśnienie na pokonanie wysokości", "p_g = ρ·g·h_g", f"1000·9,81·{f(pk.h)}/1000", RHO_W * G * pk.h / 1000, "kPa",
             "", 1),
        Krok("Straty liniowe na drodze (odcinki " + ", ".join(str(o.nr) for o in pk.sciezka) + ")", "Σ∆p_l",
             " + ".join(f(o.dp_l, 1) for o in pk.sciezka), pk.dp_l, "kPa", "Darcy–Weisbach, Colebrook–White", 1),
        Krok("Straty miejscowe", "Σ∆p_m = 0,5·Σ∆p_l", f"0,5·{f(pk.dp_l, 1)}", pk.dp_m, "kPa", "PWr [W]", 1),
        Krok("Straty na urządzeniach (wodomierz, EA, filtr" + (", podgrzewacz, TZM" if pk.medium == "c.w.u." else "") + ")",
             "Σ∆p_urz", "", pk.dp_urz, "kPa", "", 1),
        Krok("Wymagane ciśnienie wypływu", "p_w", "", pk.p_w, "kPa", "PN-92/B-01706 tabl. 1; PN-EN 806-3 p. 4.3 (≥ 100 kPa)", 0),
        Krok("Wymagane ciśnienie w miejscu włączenia do sieci", "p_wym = p_g + Σ∆p_l + Σ∆p_m + Σ∆p_urz + p_w",
             f"{f(RHO_W * G * pk.h / 1000, 1)} + {f(pk.dp_l, 1)} + {f(pk.dp_m, 1)} + {f(pk.dp_urz, 1)} + {f(pk.p_w, 0)}",
             p_wym, "kPa", "W-130", 1),
    ]
    war.append(Warunek("Wymagane ciśnienie w sieci ≤ ciśnienie dyspozycyjne", p_wym / 1000.0, "<=", par.p_sieci_min, "MPa",
                       "warunki gestora [ZAŁ p_dysp]", "W-130",
                       uwagi="przy niespełnieniu — zestaw podnoszący ciśnienie (ZPC)", nd=3))
    # ciśnienie statyczne w najniższym punkcie
    z_min = min(p.z_wyl for p in przybory)
    p_stat = par.p_sieci_max * 1000 - RHO_W * G * (z_min - z_siec) / 1000.0
    reduktor = p_stat > 500.0 + 1e-9
    p_stat_za = min(p_stat, par.reduktor_nastawa * 1000) if reduktor else p_stat
    cis = {"p_wym": p_wym, "p_stat_max": p_stat, "reduktor": reduktor, "p_stat_za_reduktorem": p_stat_za,
           "z_siec": z_siec}
    kroki["stat"] = [
        Krok("Maks. ciśnienie statyczne w najniżej położonym punkcie", "p_st = p_sieci,max − ρ·g·(z_min − z_sieci)",
             f"{f(par.p_sieci_max * 1000, 0)} − 9,81·({f(z_min)} − ({f(z_siec)}))", p_stat, "kPa", "", 0),
    ]
    if reduktor:
        kroki["stat"].append(Krok("Reduktor ciśnienia za wodomierzem (nastawa)", "p_red", "", par.reduktor_nastawa * 1000, "kPa",
                                  "PN-EN 806-3 p. 4.3: p_st ≤ 500 kPa w punktach", 0))
        p_za_red = p_wym - (RHO_W * G * (wezly["WOD"][2] - z_siec) / 1000.0) - sum(
            o.dp for o in odc if o.od in ("SIEC", "WEJ", "WOD")) - dpw - dp_ea - dp_f
        war.append(Warunek("Nastawa reduktora ≥ ciśnienie wymagane za zestawem wodomierzowym (najniekorzystniejszy punkt)",
                           par.reduktor_nastawa * 1000, ">=", p_za_red, "kPa", "kolejność: wodomierz, filtr, EA, reduktor",
                           "W-130", nd=0))
    war.append(Warunek("Ciśnienie statyczne w punkcie ≤ 0,60 MPa (WT §114)", p_stat_za / 1000.0, "<=", 0.60, "MPa",
                       "WT §114 ust. 1", "W-130", nd=3))
    war.append(Warunek("Ciśnienie statyczne w punkcie ≤ 500 kPa (PN-EN 806-3 p. 4.3)", p_stat_za, "<=", 500.0, "kPa",
                       "PN-EN 806-3:2006 p. 4.3", "W-130", nd=0))
    for o in odc:
        if o.v > par.v_max.get(o.typ, 2.0) + 1e-6:
            war.append(Warunek(f"Prędkość na odcinku {o.nr} ({o.typ})", o.v, "<=", par.v_max.get(o.typ, 2.0), "m/s",
                               "PN-EN 806-3 (≤ 2 m/s) / [ZAŁ]", "W-132"))
    war.append(Warunek("Maks. prędkość w przewodach rozdzielczych i pionach",
                       max((o.v for o in odc if o.typ in ("glowny", "pion", "rozdzielczy")), default=0.0), "<=", 2.0, "m/s",
                       "PN-EN 806-3 (≤ 2 m/s)", "W-132"))

    # ---- zabezpieczenia PN-EN 1717
    z1717 = _zabezpieczenia_1717(przybory, dn_arm)

    # ---- c.w.u.
    cwu = _cwu(dane, przybory, odc, par, osoby, kroki, war)

    # ---- izolacje
    izol = _izolacje(odc, par, kroki)

    zal += [f"Rury instalacji: PE-RT/Al/PE-RT (k = {f(par.k_mm, 3)} mm); przyłącze PE100 SDR11 [ZAŁ].",
            f"Prędkości maks. [m/s]: " + ", ".join(f"{k} {f(v, 1)}" for k, v in par.v_max.items()) +
            " (PN-EN 806-3: ≤ 2 m/s; przewody główne 1,0 m/s dla ograniczenia strat i hałasu) [ZAŁ].",
            "Długości odcinków: trasy równoległe do ścian (odległość „miejska” w rzucie) + podejścia pionowe; "
            "piony zgrupowane automatycznie (R ≤ 3,5 m) lub z instalacje.yaml [UPR].",
            f"Ciśnienie w sieci: dyspozycyjne {f(par.p_sieci_min, 2)} MPa, maks. statyczne {f(par.p_sieci_max, 2)} MPa [ZAŁ — "
            "do potwierdzenia w warunkach technicznych gestora, D-23]."]
    return WynikWoda(dane=dane, par=par, przybory=przybory, piony=piony, wezly=wezly, odcinki=odc, punkty=punkty,
                     zapotrzebowanie=zap, wodomierz=wodomierz, urzadzenia=urz, zabezpieczenia_1717=z1717, cwu=cwu,
                     izolacje=izol, cisnienia=cis, warunki=war, kroki=kroki, zalozenia=zal)


def _zabezpieczenia_1717(przybory: list[Przybor], dn: int) -> list[list]:
    """Tabela zabezpieczeń przed przepływem zwrotnym (PN-EN 1717; kategorie płynów 1–5)."""
    rows = [["Za wodomierzem głównym (całe przyłącze)", "2", f"EA DN{dn} (zawór antyskażeniowy kontrolowany)",
             "WT §115 ust. 2; PN-EN 1717 tabl. 2–3; wymagania gestora (typ może być podwyższony w warunkach)"]]
    if any(p.t.qn_cw > 0 for p in przybory):
        rows.append(["Zasilanie zasobnika c.w.u. (woda zmieniona temperaturowo)", "2",
                     "EA w grupie bezpieczeństwa + zawór bezpieczeństwa + naczynie przeponowe c.w.u.",
                     "PN-EN 1717; PN-B-02440:1976 (powołana w WT, wycof.)"])
    rows.append(["Napełnianie/uzupełnianie instalacji c.o. (woda z inhibitorami)", "3",
                 "CA (zawór antyskażeniowy o strefach różnych ciśnień) + odłączany wąż napełniający",
                 "PN-EN 1717 — kat. 3 (przy glikolu toksycznym kat. 4 → BA)"])
    if any(p.typ == "zawor_ogrodowy" for p in przybory):
        rows.append(["Zawory ogrodowe (wąż, możliwy kontakt z nawozami)", "3 (4)",
                     "HA/HD — zawór ze złączką do węża z zabezpieczeniem; przy dozownikach nawozów kat. 4 → BA / przerwa",
                     "PN-EN 1717; R6 §3.6"])
    if any(p.typ in ("pralka", "zmywarka") for p in przybory):
        rows.append(["Pralka, zmywarka", "3", "zabezpieczenie wbudowane w urządzenie (PN-EN 61770)", "PN-EN 1717"])
    rows.append(["Instalacja wody deszczowej (jeśli uzupełniana z wodociągu)", "5",
                 "AA/AB — przerwa powietrzna; instalacje rozdzielone (bez połączenia)", "WT §126 ust. 3 (W-136)"])
    return rows


def _cwu(dane, przybory, odc, par: ParametryWoda, osoby, kroki, war) -> dict:
    dT = par.theta_cwu - par.theta_zw
    Vd1 = osoby * par.cwu_q
    Af = dane.A_f
    V_Wi = float(wym("energia", "V_Wi", 1.4) or 1.4)
    kR = float(wym("energia", "k_R", 0.9) or 0.9)
    Vd2 = V_Wi * Af
    Vd = max(Vd1, Vd2)
    Qd = Vd * 1.163e-3 * dT            # kWh/d (c = 1,163 Wh/(dm³·K))
    Q_W_nd = V_Wi * Af * 4.19 * 1000 * dT * kR * 365 / 3600.0 / 1000.0   # kWh/a (metodologia wzór 61)
    # pobór szczytowy (1 h) — mieszanie do 40 °C
    ma_wanne = any(p.typ == "wanna" for p in przybory)
    n_nat = sum(1 for p in przybory if p.typ == "prysznic")
    V40 = (140.0 if ma_wanne else 0.0) + min(max(n_nat, 1), 2) * 50.0 + 2 * 5.0
    V55_zlew = 10.0 if any(p.typ == "zlew" for p in przybory) else 0.0
    V55_peak = V40 * (40 - par.theta_zw) / dT + V55_zlew
    f_u = 0.8
    Vzas_min = max(V55_peak / f_u, 1.0 * Vd)
    Vzas = ceil_to(Vzas_min, ZASOBNIKI) or ZASOBNIKI[-1]
    t_lad = Vzas * 1.163e-3 * dT / par.P_PC_cwu_kW
    A_wez = 0.25 * par.P_PC_cwu_kW
    kroki["cwu"] = [
        Krok("Dobowe zapotrzebowanie c.w.u. (55 °C) — wskaźnik na osobę", "V_d1 = N·q_cwu", f"{osoby}·{f(par.cwu_q, 0)}", Vd1,
             "dm³/d", "q_cwu = 50 dm³/(os·d) [ZAŁ]", 0),
        Krok("Dobowe zapotrzebowanie wg metodologii EP", "V_d2 = V_Wi·A_f", f"{f(V_Wi, 2)}·{f(Af, 1)}", Vd2, "dm³/d",
             "Dz.U. 2015 poz. 376 tab. 27 (R6-18)", 0),
        Krok("Przyjęto", "V_d = max(V_d1, V_d2)", "", Vd, "dm³/d", "", 0),
        Krok("Dobowe ciepło na c.w.u.", "Q_d = V_d·c·(θ_cwu − θ_zw)", f"{f(Vd, 0)}·1,163·10⁻³·{f(dT, 0)}", Qd, "kWh/d", "", 2),
        Krok("Roczne zapotrzebowanie normatywne (do EP)", "Q_W,nd = V_Wi·A_f·c·ρ·(θ_W − θ_0)·k_R·t_R/3600",
             f"{f(V_Wi, 2)}·{f(Af, 1)}·4,19·1000·{f(dT, 0)}·{f(kR, 2)}·365/3600/1000", Q_W_nd, "kWh/a",
             "metodologia wzór (61) (R6-18)", 0),
        Krok("Pobór szczytowy (1 h): " + ("wanna 140 dm³ + " if ma_wanne else "") + f"{min(max(n_nat, 1), 2)} natrysk(i) × 50 dm³ "
             "+ 2 × umywalka 5 dm³ (40 °C) + zlewozmywak 10 dm³ (55 °C)", "V_55 = V_40·(40 − θ_zw)/(θ_cwu − θ_zw) + V_zl",
             f"{f(V40, 0)}·{f(40 - par.theta_zw, 0)}/{f(dT, 0)} + {f(V55_zlew, 0)}", V55_peak, "dm³", "[ZAŁ — profil poboru]", 0),
        Krok("Minimalna pojemność zasobnika", "V_zas ≥ max(V_55/f_u; V_d), f_u = 0,8",
             f"max({f(V55_peak, 0)}/0,8; {f(Vd, 0)})", Vzas_min, "dm³", "[ZAŁ/W — PC: zasobnik ≈ dobowe zapotrzebowanie]", 0),
        Krok("Dobrano zasobnik c.w.u. z wężownicą dla pompy ciepła", "V_zas", "", Vzas, "dm³", "", 0),
        Krok("Czas ładowania zasobnika (10 → 55 °C) mocą PC w trybie c.w.u.", "t = V_zas·c·∆θ/P_PC",
             f"{f(Vzas, 0)}·1,163·10⁻³·{f(dT, 0)}/{f(par.P_PC_cwu_kW, 1)}", t_lad, "h", "", 2),
        Krok("Wymagana powierzchnia wężownicy", "A ≥ 0,25 m²/kW·P_PC", f"0,25·{f(par.P_PC_cwu_kW, 1)}", A_wez, "m²",
             "dane producentów PC [W]", 2),
    ]
    # cyrkulacja — reguła 3 l
    cwu_odc = [o for o in odc if o.medium == "CWU"]
    obj = {}
    for o in cwu_odc:
        if o.typ == "podejscie":
            sc = _sciezka(odc, o.do)
            obj[o.do] = sum(x.objetosc_l for x in sc if x.medium == "CWU")
    V3 = max(obj.values()) if obj else 0.0
    tryb = par.cyrkulacja
    if tryb == "auto":
        tryb = "brak" if V3 <= 3.0 else "czasowa"
    # straty ciepła przewodów c.w.u. (bez podejść) i pętli cyrkulacji
    L_dys = sum(o.L for o in cwu_odc if o.typ != "podejscie")
    q_lin = []
    for o in cwu_odc:
        if o.typ == "podejscie":
            continue
        t_ref = grubosc_izolacji_WT(o.dw)
        t = grubosc_rownowazna(o.dz, t_ref, par.lambda_izol)
        q_lin.append(strata_ciepla_rury(o.dz, t, par.lambda_izol, par.theta_cwu - par.theta_otocz) * o.L)
    Q_loss_zas = sum(q_lin)
    L_cyrk = L_dys
    t_c = grubosc_rownowazna(16, 20.0, par.lambda_izol)
    Q_loss_cyrk = strata_ciepla_rury(16, t_c, par.lambda_izol, par.theta_cwu - par.cyrk_dT / 2 - par.theta_otocz) * L_cyrk
    Q_petla = Q_loss_zas + Q_loss_cyrk
    V_cyrk_dm3h = Q_petla * 3600.0 / (4190.0 * par.cyrk_dT)                    # kg/h ≈ dm³/h
    q_c = V_cyrk_dm3h / 3600.0
    v_c, R_c, _ = spadek_jednostkowy(q_c, 12.0, par.theta_cwu)
    dp_c = 1.5 * R_c * 2 * L_cyrk + 10.0      # pętla zasilanie+powrót, miejscowe 50 %, zawór termostatyczny 10 kPa
    h_pr = par.cyrk_h_dzien if tryb == "czasowa" else (24.0 if tryb == "ciagla" else 0.0)
    E_str_cyrk = Q_petla * h_pr * 365 / 1000.0
    eta_Wd = {"brak": float(wym("energia", "eta_Wd_bez_cyrkulacji", 0.60) or 0.60),
              "czasowa": float(wym("energia", "eta_Wd_cyrkulacja_czasowa", 0.80) or 0.80), "ciagla": 0.70}[tryb]
    kroki["cyrk"] = [
        Krok("Największa objętość wody w przewodach c.w.u. od zasobnika do punktu poboru", "V_max = Σ(π·d_w²/4·L)", "",
             V3, "dm³", "reguła 3 litrów (DVGW W 551; R6 §3.6) [W]", 2),
        Krok("Decyzja", "", "", {"brak": "cyrkulacja zbędna (V ≤ 3 dm³)", "czasowa": "cyrkulacja czasowa (V > 3 dm³)",
                                  "ciagla": "cyrkulacja ciągła"}[tryb], "", "WT §120 ust. 1 — w domu jednorodzinnym niewymagana"),
        Krok(f"Strata ciepła przewodów rozprowadzających c.w.u., L = {f(L_dys, 1)} m (izolacja wg WT, λ = "
             + f(par.lambda_izol, 3) + ")", "Q_z = Σ q_l·L", "", Q_loss_zas, "W", "", 1),
        Krok(f"Strata ciepła przewodu cyrkulacyjnego 16×2, L_c = {f(L_cyrk, 1)} m", "Q_c = q_l·L_c", "", Q_loss_cyrk,
             "W", "", 1),
        Krok("Strumień cyrkulacji", "V_c = (Q_z + Q_c)/(c·∆θ_c)", f"{f(Q_petla, 1)}·3600/(4190·{f(par.cyrk_dT, 0)})",
             V_cyrk_dm3h, "dm³/h", "∆θ_c = 5 K (DVGW W 551) [W]", 1),
        Krok("Wysokość podnoszenia pompy cyrkulacyjnej", "∆p = 1,5·R·2L_c + ∆p_TV", f"1,5·{f(R_c, 3)}·2·{f(L_cyrk, 1)} + 10",
             dp_c, "kPa", "zawór termostatyczny cyrkulacji 10 kPa [ZAŁ]", 1),
        Krok("Roczne straty ciepła w pętli przy pracy " + f(h_pr, 0) + " h/d", "E = Q·h·365", "", E_str_cyrk, "kWh/a", "", 0),
        Krok("Sprawność przesyłu c.w.u. do EP", "η_W,d", "", eta_Wd, "", "metodologia tab. 12 (R6-17)", 2),
    ]
    # dezynfekcja termiczna
    E_dez = Vzas * 1.163e-3 * (par.theta_dez_zas - par.theta_cwu) + Q_petla * 1.0 / 1000.0
    n_dez = 365.0 / par.dezynfekcja_co_dni
    kroki["dez"] = [
        Krok("Wymagana temperatura w punktach podczas dezynfekcji", "θ_dez", "", par.theta_dez_punkt, "°C",
             "WT §120 ust. 2a (70–80 °C; metoda cieplna wybrana — S-1)", 0),
        Krok("Nastawa zasobnika w cyklu dezynfekcji", "θ_zas", "", par.theta_dez_zas, "°C",
             "zapas na straty w przewodach [ZAŁ]; grzałka elektryczna / tryb PC R290 wysokotemperaturowy", 0),
        Krok("Energia jednego cyklu (dogrzanie zasobnika + 1 h pracy pętli)",
             "E_1 = V_zas·c·(θ_zas − θ_cwu) + Q_pętli·1 h",
             f"{f(Vzas, 0)}·1,163·10⁻³·{f(par.theta_dez_zas - par.theta_cwu, 0)} + {f(Q_petla / 1000, 3)}", E_dez, "kWh", "", 2),
        Krok("Energia roczna (cykl co " + str(par.dezynfekcja_co_dni) + " dni)", "E_rok = E_1·365/n", "", E_dez * n_dez,
             "kWh/a", "[ZAŁ]", 0),
    ]
    war.append(Warunek("Temperatura c.w.u. w punktach", par.theta_cwu, "zakres", (55, 60), "°C", "WT §120 ust. 2", "W-133",
                       nd=0))
    war.append(Warunek("Temperatura dezynfekcji w punktach", par.theta_dez_punkt, "zakres", (70, 80), "°C",
                       "WT §120 ust. 2a", "W-133", nd=0))
    war.append(Warunek("Nastawa zasobnika w dezynfekcji ≥ temp. wymagana w punktach", par.theta_dez_zas, ">=",
                       par.theta_dez_punkt, "°C", "", "W-133", nd=0))
    war.append(Warunek("Pojemność zasobnika ≥ minimalna", Vzas, ">=", Vzas_min, "dm³", "", "W-133", nd=0))
    if tryb == "brak":
        war.append(Warunek("Objętość przewodu c.w.u. do najdalszego punktu (reguła 3 l)", V3, "<=", 3.0, "dm³",
                           "DVGW W 551 [W]", "W-134"))
    return {"V_d": Vd, "V_d1": Vd1, "V_d2": Vd2, "Q_d": Qd, "Q_W_nd_kWh_a": Q_W_nd, "V55_peak": V55_peak,
            "V_zas_min": Vzas_min, "V_zas": Vzas, "t_lad": t_lad, "A_wez": A_wez, "V3": V3, "V_obj": obj,
            "cyrkulacja": tryb, "Q_petla_W": Q_petla, "V_cyrk_dm3h": V_cyrk_dm3h, "dp_cyrk_kPa": dp_c,
            "E_str_cyrk": E_str_cyrk, "eta_W_d": eta_Wd, "dez_E1": E_dez, "dez_E_rok": E_dez * n_dez,
            "h_cyrk": h_pr}


def _izolacje(odc: list[Odcinek], par: ParametryWoda, kroki) -> list[list]:
    rows = []
    seen = set()
    for o in sorted(odc, key=lambda x: (x.medium, x.dz)):
        key = (o.medium, o.dz, o.s)
        if key in seen or o.typ == "przylacze":
            continue
        seen.add(key)
        if o.medium == "CWU":
            t_ref = grubosc_izolacji_WT(o.dw)
            t = grubosc_rownowazna(o.dz, t_ref, par.lambda_izol)
            q = strata_ciepla_rury(o.dz, t, par.lambda_izol, par.theta_cwu - par.theta_otocz)
            rows.append([f"c.w.u. {o.rura}", f(o.dw, 0), f(t_ref, 0), f(t, 1), f(math.ceil(t / 5) * 5, 0),
                         f(t_ref / 2, 0), f(q, 1), "WT zał. 2 pkt 1.5 lp. 1–4 (W-135)"])
        else:
            rows.append([f"woda zimna {o.rura}", f(o.dw, 0), "—", "—", "9", "—", "—",
                         "izolacja przeciwroszeniowa 9 mm [ZAŁ; WT nie wymaga]"])
    t_ref = grubosc_izolacji_WT(12)
    t = grubosc_rownowazna(16, t_ref, par.lambda_izol)
    rows.append(["cyrkulacja 16×2,0", "12", f(t_ref, 0), f(t, 1), f(math.ceil(t / 5) * 5, 0), f(t_ref / 2, 0),
                 f(strata_ciepla_rury(16, t, par.lambda_izol, par.theta_cwu - par.theta_otocz), 1), "W-135"])
    d = 20.0
    kroki["izol"] = [
        Krok("Przeliczenie grubości izolacji na λ materiału (przykład d_z = 20 mm, t_ref = 20 mm)",
             "t = d_z/2·[((d_z + 2t_ref)/d_z)^(λ/0,035) − 1]",
             f"20/2·[((20 + 2·20)/20)^({f(par.lambda_izol, 3)}/0,035) − 1]", grubosc_rownowazna(d, 20.0, par.lambda_izol),
             "mm", "równoważność oporu cieplnego izolacji cylindrycznej [UPR]", 1)]
    return rows


# --------------------------------------------------------------------------------------------------
# Raport
# --------------------------------------------------------------------------------------------------
def _raport(w: WynikWoda) -> Raport:
    d, par = w.dane, w.par
    R = Raport("Obliczenia instalacji wodociągowej i c.w.u.",
               f"Obiekt: {d.nazwa}. Model: {', '.join(f'{k}: `{v}`' for k, v in d.zrodla.items())}. "
               "Dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE] tam, gdzie oznaczono [ZAŁ].")
    R.h(2, "1. Podstawy i metoda")
    R.lista([
        "WT §113–120 (t.j. Dz.U. 2022 poz. 1225 ze zm.), stosowane na podstawie art. 102a PB; wymagania W-130…W-137.",
        "PN-B-01706:1992 (+Az1:1999) — powołana w WT zał. 1 lp. 4 (wycofana w PKN, wiąże przez WT); kontrolnie PN-EN 806-3:2006.",
        "**Wybór metody przepływu obliczeniowego:** q = 0,682·(Σq_n)^0,45 − 0,14 (PN-B-01706, budynki mieszkalne) — metoda "
        "wskazana w rejestrze (W-132) i powołana przez WT; daje wartości wyższe (bezpieczniejsze) niż PN-EN 806-3 "
        "(Nowakowski, RI 4/2011); przejście LU → Q_D w PN-EN 806-3 jest graficzne — raport podaje ΣLU i Q_T = 0,1·ΣLU "
        "kontrolnie oraz warunki ciśnień PN-EN 806-3 p. 4.3.",
        "PN-EN 1717:2003 (WT zał. 1 lp. 5) / PN-EN 1717+A1:2026-09 (aktualna, EN) — zabezpieczenia przed przepływem zwrotnym.",
        "Straty liniowe: Darcy–Weisbach + Colebrook–White; straty miejscowe 50 % liniowych (PWr) [W].",
    ])
    R.h(2, "2. Dane wejściowe i założenia")
    R.lista(w.zalozenia + d.uwagi)
    R.h(3, "2.1 Przybory (z modelu)")
    R.tab(["Przybór", "Liczba", "q_n zw [dm³/s]", "q_n cw [dm³/s]", "Σq_n [dm³/s]", "LU (zw+cw)", "DU [l/s]", "Odpływ"],
          zestawienie(w.przybory), "lrrrrrrl")
    R.tab(["Id", "Typ", "Kond.", "Pomieszczenie", "x, y [m]", "Źródło"],
          [[p.id, p.typ, p.kond, f"{p.pom or '—'} {p.pom_nazwa}", f"{f(p.xy[0])}; {f(p.xy[1])}", p.zrodlo] for p in w.przybory],
          "llllll")
    R.h(3, "2.2 Piony")
    R.tab(["Pion", "Położenie x, y [m]", "Kondygnacje", "Pomieszczenia", "Przybory", "Źródło"],
          [[p.id, f"{f(p.xy[0])}; {f(p.xy[1])}", ", ".join(p.kondygnacje),
            "; ".join(f"{k}: {', '.join(v)}" for k, v in p.pomieszczenia.items()),
            ", ".join(x.id for x in p.przybory), p.zrodlo] for p in w.piony], "llllll")
    R.h(2, "3. Zapotrzebowanie na wodę")
    R.kroki(w.kroki["zap"])
    R.h(2, "4. Przepływ obliczeniowy")
    R.kroki(w.kroki["q"])
    R.h(2, "5. Wymiarowanie przewodów i straty ciśnienia")
    for med, tyt in (("ZW", "5.1 Woda zimna (z przyłączem i zasilaniem zasobnika)"), ("CWU", "5.2 Ciepła woda użytkowa (55 °C)")):
        R.h(3, tyt)
        R.tab(["Nr", "Odcinek", "Typ", "L [m]", "Σq_n [dm³/s]", "q [dm³/s]", "ΣLU", "Rura d_z×s", "d_w [mm]", "v [m/s]",
               "R [kPa/m]", "∆p_l [kPa]", "∆p_m [kPa]"],
              [[o.nr, f"{o.od}→{o.do}: {o.opis}", o.typ, f(o.L, 2), f(o.sum_qn, 2), f(o.q, 3), f(o.sum_LU, 0), o.rura,
                f(o.dw, 0), f(o.v, 2), f(o.R, 3), f(o.dp_l, 2), f(o.dp_m, 2)] for o in w.odcinki if o.medium == med],
              "lllrrrrlrrrrr")
    R.h(3, "5.3 Wymagane ciśnienie — najniekorzystniej położony punkt")
    R.kroki(w.kroki["p"])
    R.tab(["Punkt", "Medium", "h_g [m]", "Σ∆p_l [kPa]", "Σ∆p_m [kPa]", "Σ∆p_urz [kPa]", "p_w [kPa]", "p_wym [kPa]"],
          [[f"{p.przybor.id} {p.przybor.typ} ({p.przybor.kond})", p.medium, f(p.h, 2), f(p.dp_l, 1), f(p.dp_m, 1),
            f(p.dp_urz, 1), f(p.p_w, 0), f(p.p_wym, 1)] for p in sorted(w.punkty, key=lambda x: -x.p_wym)], "llrrrrrr")
    R.h(3, "5.4 Ciśnienie statyczne")
    R.kroki(w.kroki["stat"])
    R.h(2, "6. Zestaw wodomierzowy i zabezpieczenia")
    R.kroki(w.kroki["wod"])
    R.p("Zestaw wodomierzowy (od strony sieci): zawór odcinający, wodomierz, zawór odcinający, filtr z płukaniem wstecznym, "
        "zawór antyskażeniowy EA" + (", reduktor ciśnienia" if w.cisnienia["reduktor"] else "") +
        "; mostek wyrównawczy przed i za wodomierzem przy rurach metalowych (WT §116 ust. 3). Lokalizacja: pomieszczenie "
        "techniczne na parterze (WT §115 ust. 1; W-131).")
    R.h(3, "6.1 Zabezpieczenia przed przepływem zwrotnym (PN-EN 1717)")
    R.tab(["Miejsce", "Kategoria płynu", "Zabezpieczenie", "Podstawa"], w.zabezpieczenia_1717, "lcll")
    R.h(2, "7. Ciepła woda użytkowa")
    R.h(3, "7.1 Zapotrzebowanie i zasobnik")
    R.kroki(w.kroki["cwu"])
    R.h(3, "7.2 Cyrkulacja")
    R.kroki(w.kroki["cyrk"])
    if w.cwu["V_obj"]:
        R.tab(["Punkt", "Objętość do punktu [dm³]"], [[k, f(v, 2)] for k, v in sorted(w.cwu["V_obj"].items())], "lr")
    R.h(3, "7.3 Dezynfekcja termiczna")
    R.kroki(w.kroki["dez"])
    R.lista(["Termostatyczny zawór mieszający na wyjściu z zasobnika (ochrona przed poparzeniem, 45–55 °C) z obejściem / "
             "programem na czas dezynfekcji; w cyklu dezynfekcji praca pompy cyrkulacyjnej (jeśli jest).",
             "Zabezpieczenie zasobnika przed przekroczeniem ciśnienia i temperatury: grupa bezpieczeństwa (zawór bezpieczeństwa "
             "6 bar, zawór zwrotny EA), naczynie przeponowe c.w.u. (obliczenie w module ogrzewania).",
             "Ciepła woda po lewej stronie armatury (WT §120 ust. 5)."])
    R.h(2, "8. Izolacja cieplna przewodów")
    R.kroki(w.kroki["izol"])
    R.tab(["Przewód", "d_w [mm]", "t_WT (λ=0,035) [mm]", "t przy λ_izol [mm]", "t przyjęta [mm]", "przejścia (50 %) [mm]",
           "q_l [W/m]", "Podstawa"], w.izolacje, "lrrrrrrl")
    R.h(2, "9. Sprawdzenia")
    R.war(w.warunki)
    R.h(2, "10. Wyniki do innych opracowań")
    R.tab(["Wielkość", "Wartość"], [[k, (fa(v, 4) if isinstance(v, float) else str(v))] for k, v in w.do_dict().items()], "lr")
    R.zrodlo("WT — rozp. MI z 12.04.2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) §113–120, zał. 2 pkt 1.5 — stosowane na podst. art. 102a PB",
             "PN-B-01706:1992 (+Az1:1999) — wg PWr, „Materiały pomocnicze do projektu instalacji wodociągowej” (tabl. q_n, przykład obliczeniowy) [W]",
             "PN-EN 806-3:2006 p. 4.3 (ciśnienia) — próbka normy (iTeh, SIST EN 806-3:2006); tabl. LU wg instsani.pl [W]",
             "Nowakowski E., Obliczeniowe przepływy wody w budynkach mieszkalnych – wybór metody, Rynek Instalacyjny 4/2011",
             "PN-EN 1717:2003 / PN-EN 1717+A1:2026-09",
             "Rozp. MIiR z 27.02.2015 (Dz.U. 2015 poz. 376 ze zm.) — metodologia EP, wzór (61), tab. 12, 27",
             "DVGW W 551 — reguła 3 litrów, ∆θ cyrkulacji 5 K [W]",
             "Rejestr wymagań: docs/10_podstawy_prawne/00_rejestr_wymagan.md (W-130…W-137), wymagania.yaml")
    return R
