"""Bilans wentylacji mechanicznej nawiewno-wywiewnej z odzyskiem ciepła — dom jednorodzinny.

Podstawy (rejestr W-160…W-169, R6-37…R6-46):
* wywiew minimalny wg PN-83/B-03430/Az3:2000 (wycofana, wiążąca przez WT § 147 ust. 1, § 149 ust. 1) [NZW — źródła
  wtórne zgodne]: kuchnia z kuchenką elektryczną 30 m³/h (≤ 3 osób) / 50 m³/h (> 3 osób), okresowo ≥ 120 m³/h;
  łazienka 50; WC 30; pomieszczenie pomocnicze bezokienne 15; pralnia ≥ 2 h⁻¹;
* nawiew ≥ 20 m³/h na osobę na pobyt stały i ≥ Σ wywiewu (WT § 149 ust. 1, § 150 ust. 2–3); przepływ z pokoi do
  kuchni i pomieszczeń higieniczno-sanitarnych (powietrze transferowe);
* bilans zrównoważony nawiew = wywiew (±10 %);
* odzysk ciepła: obowiązek ≥ 50 % od 500 m³/h (WT § 151 ust. 1 — tu nie zachodzi), cel projektu η ≥ 0,85 [ZAŁ];
* SFP: nawiew z odzyskiem ≤ 1,60 kW/(m³/s), wywiew z odzyskiem ≤ 1,00 kW/(m³/s), +0,3 przy odzysku > 67 %
  (WT § 154 ust. 10–11); ekoprojekt (UE) 1253/2014 — SEC ≤ −20 kWh/(m²·a), by-pass, napęd wielobiegowy;
* czerpnia/wyrzutnia — WT § 152 (odległości); garaż nieogrzewany — otwory ≥ 0,04 m²/stanowisko (WT § 108 ust. 1).
Rodzaj pomieszczenia rozpoznawany z nazwy (lub pola `rodzaj` pomieszczenia w modelu).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
import numpy as np

from ..wspolne import ZAL, Zalozenia, fmt, naglowek_raportu, ok, tabela_md, wym, wyrob

RODZAJE = [
    (r"gara[zż]", "garaz"),
    (r"kuch|aneks", "kuchnia"),
    (r"[lł]azien|natrysk|prysznic|[lł]a[zź]\.", "lazienka"),
    (r"\bwc\b|toalet|ust[eę]p", "wc"),
    (r"pral|suszar", "pralnia"),
    (r"techn|kot[lł]own|rekuperac|wentylatorn|maszynown", "techniczne"),
    (r"garderob|spi[zż]ar|schowek|sk[lł]adzik|magazyn|gospodarcz|szaf", "pomocnicze"),
    (r"\bhol\b|korytarz|komunikac|wiatro[lł]ap|przedpok|klatk|schod|antre|przedsion", "komunikacja"),
    (r"pok[oó]j|sypial|gabinet|salon|dzienn|jadal|bibliotek|go[sś]ci|dziec|rodzin|studio|biuro", "pokoj"),
]


def rodzaj_pomieszczenia(nazwa: str, kategoria: str = "", raw: dict | None = None) -> str:
    if raw and raw.get("rodzaj"):
        return str(raw["rodzaj"])
    n = nazwa.lower()
    for wz, r in RODZAJE:
        if re.search(wz, n):
            return r
    return "pokoj" if kategoria == "podstawowa" else "inne"


@dataclass
class PomWent:
    id: str
    nazwa: str
    rodzaj: str
    A: float
    V: float
    okna: int
    pobyt: bool
    wyw_min: float
    naw_model: float | None
    wyw_model: float | None
    naw: float = 0.0
    wyw: float = 0.0
    transfer: float = 0.0
    theta: float = 20.0
    podstawa: str = ""

    @property
    def n_h(self) -> float:
        return max(self.naw, self.wyw) / self.V if self.V else 0.0


@dataclass
class WynikWent:
    pomieszczenia: list[PomWent]
    osoby: int
    naw_min_osoby: float
    suma_wyw_min: float
    suma_naw: float
    suma_wyw: float
    zrodlo_bilansu: str
    V_boost: float
    centrala: dict
    eta: float
    P_el_W: float
    SFP_naw: float
    SFP_wyw: float
    SFP_lim_naw: float
    SFP_lim_wyw: float
    kanal_glowny_D_mm: int
    sprawdzenia: list[tuple[str, str, bool | None]] = field(default_factory=list)
    garaz: list[tuple[str, str, bool | None]] = field(default_factory=list)
    uwagi: list[str] = field(default_factory=list)

    @property
    def q_m3h(self) -> float:
        return max(self.suma_naw, self.suma_wyw)

    @property
    def zrownowazony(self) -> bool:
        return abs(self.suma_naw - self.suma_wyw) <= 0.10 * max(self.suma_naw, self.suma_wyw, 1e-9)


def wywiew_minimalny(rodzaj: str, V: float, okna: int, osoby: int) -> tuple[float, str]:
    """Minimalny strumień wywiewu [m³/h] wg PN-83/B-03430/Az3:2000 (rejestr W-162)."""
    if rodzaj == "kuchnia":
        if osoby > 3:
            return float(wym("wentylacja", "wywiew_kuchnia_el_ponad_3_os", 50)), "kuchnia z kuchenką elektryczną, > 3 osób"
        return float(wym("wentylacja", "wywiew_kuchnia_el_do_3_os", 30)), "kuchnia z kuchenką elektryczną, ≤ 3 osób"
    if rodzaj == "lazienka":
        return float(wym("wentylacja", "wywiew_lazienka", 50)), "łazienka"
    if rodzaj == "wc":
        return float(wym("wentylacja", "wywiew_wc", 30)), "wydzielony WC"
    if rodzaj == "pralnia":
        return float(wym("wentylacja", "wywiew_pralnia_krotnosc", 2)) * V, "pralnia ≥ 2 h⁻¹"
    if rodzaj in ("pomocnicze", "techniczne") and okna == 0:
        return float(wym("wentylacja", "wywiew_pomieszczenie_bezokienne", 15)), "pomieszczenie pomocnicze bezokienne"
    return 0.0, ""


def bilans_wentylacji(bryla, *, osoby: int | None = None, centrala: dict | str | None = None,
                      cfg: dict | None = None, zal: Zalozenia | None = None) -> WynikWent:
    """Bilans powietrza pomieszczeń ogrzewanych i dobór centrali."""
    cfg = cfg or {}
    wc = cfg.get("wentylacja") or {}
    osoby = int(osoby or cfg.get("osoby") or wym("wentylacja", "liczba_osob", 5))
    naw_os = float(wym("wentylacja", "nawiew_na_osobe_min", 20))
    PW: list[PomWent] = []
    for p in bryla.ogrzewane:
        rodz = rodzaj_pomieszczenia(p.nazwa, p.kategoria, p.raw)
        n_ok = sum(1 for e in p.elementy if e.rodzaj == "okno" and e.sasiad == "zewn")
        wmin, pod = wywiew_minimalny(rodz, p.V, n_ok, osoby)
        went = p.went or {}
        PW.append(PomWent(p.id, p.nazwa, rodz, p.A, p.V, n_ok, p.pobyt, wmin,
                          float(went["naw"]) if went.get("naw") is not None else None,
                          float(went["wyw"]) if went.get("wyw") is not None else None, theta=p.theta or 20.0,
                          podstawa=pod))
    s_wmin = sum(p.wyw_min for p in PW)
    q_min = max(s_wmin, naw_os * osoby)
    # model — czy kompletny i poprawny?
    model_ok = False
    if any((p.naw_model or 0) > 0 or (p.wyw_model or 0) > 0 for p in PW):
        sn = sum(p.naw_model or 0 for p in PW)
        sw = sum(p.wyw_model or 0 for p in PW)
        war = all((p.wyw_model or 0) >= p.wyw_min - 1e-6 for p in PW)
        model_ok = war and abs(sn - sw) <= 0.1 * max(sn, sw) and sn >= naw_os * osoby - 1e-6
    uw = []
    if model_ok:
        for p in PW:
            p.naw, p.wyw = p.naw_model or 0.0, p.wyw_model or 0.0
        zr = "strumienie z modelu (`pomieszczenia[].went`) — sprawdzone: minima, bilans ±10 %, 20 m³/h·os."
    else:
        if any(p.naw_model is not None for p in PW):
            uw.append("Strumienie w modelu (`went`) nie spełniają minimów lub bilansu — przyjęto bilans projektowy "
                      "(poniżej); do przeniesienia do modelu.")
        # wywiew: minimum; nadwyżkę do wymaganego nawiewu rozdziel na pomieszczenia wywiewne proporcjonalnie do minimów
        for p in PW:
            p.wyw = p.wyw_min
        s_w = sum(p.wyw for p in PW)
        if s_w < q_min - 1e-6:
            wyw_pom = [p for p in PW if p.wyw_min > 0] or [p for p in PW if p.rodzaj in ("kuchnia", "komunikacja")] or PW
            dod = q_min - s_w
            base = sum(p.wyw_min for p in wyw_pom) or len(wyw_pom)
            for p in wyw_pom:
                p.wyw += dod * ((p.wyw_min / base) if base and p.wyw_min else 1.0 / len(wyw_pom))
        Q = sum(p.wyw for p in PW)
        naw_pom = [p for p in PW if p.rodzaj == "pokoj"] or [p for p in PW if p.pobyt] or PW
        A_s = sum(p.A for p in naw_pom)
        for p in naw_pom:
            p.naw = Q * p.A / A_s
        # min. 20 m³/h na pokój (pobyt ludzi) — przerzut z największych
        for _ in range(5):
            male = [p for p in naw_pom if p.naw < 20.0]
            if not male:
                break
            brak = sum(20.0 - p.naw for p in male)
            for p in male:
                p.naw = 20.0
            duze = [p for p in naw_pom if p.naw > 20.0 + 1e-9 and p not in male]
            sd = sum(p.naw for p in duze)
            for p in duze:
                p.naw -= brak * p.naw / sd if sd else 0
        zr = "bilans projektowy (minima PN-83/B-03430/Az3 + nawiew 20 m³/h·os., rozdział nawiewu proporcjonalnie do " \
             "powierzchni pokoi, min. 20 m³/h na pokój)"
    for p in PW:
        p.transfer = max(0.0, p.wyw - p.naw)
    s_naw = sum(p.naw for p in PW)
    s_wyw = sum(p.wyw for p in PW)
    kuch = [p for p in PW if p.rodzaj == "kuchnia"]
    V_boost = s_wyw + sum(max(0.0, float(wym("wentylacja", "wywiew_kuchnia_okresowo", 120)) - p.wyw) for p in kuch)
    # centrala
    if isinstance(centrala, str) or centrala is None:
        klucz = centrala or wc.get("centrala") or "RVU_450"
        c = dict(wyrob("centrala_wentylacyjna", klucz)) if isinstance(klucz, str) else dict(klucz)
        c.setdefault("klucz", klucz if isinstance(klucz, str) else "model")
    else:
        c = dict(centrala)
    if isinstance(wc.get("centrala"), dict):
        c.update(wc["centrala"])
    eta = float(c.get("eta_t", 0.85))
    q = max(s_naw, s_wyw)
    P = float(c.get("SFP_Wh_m3", 0.30)) * q                     # W (oba wentylatory)
    q_s = q / 3600.0
    SFP_n = (P / 2.0) / q_s / 1000.0 if q_s else 0.0             # kW/(m³/s) — podział 50/50 [ZAŁ]
    SFP_w = SFP_n
    dod = float(wym("wentylacja", "SFP_dodatek_odzysk_ponad_67", 0.3)) if eta > 0.67 else 0.0
    lim_n = float(wym("wentylacja", "SFP_nawiew_z_odzyskiem_max", 1.6)) + dod
    lim_w = float(wym("wentylacja", "SFP_wywiew_z_odzyskiem_max", 1.0)) + dod
    v = float(wc.get("predkosc_kanal_glowny", 3.0))
    D = math.sqrt(4 * q_s / (math.pi * v)) * 1000 if q_s else 0.0
    Dn = next((d for d in (100, 125, 160, 180, 200, 250, 315) if d >= D), 315)
    W = WynikWent(PW, osoby, naw_os * osoby, s_wmin, s_naw, s_wyw, zr, V_boost, c, eta, P, SFP_n, SFP_w, lim_n, lim_w,
                  Dn, uwagi=uw)
    spr = W.sprawdzenia
    spr.append(("Nawiew ≥ 20 m³/h·os. (WT § 149 ust. 1)", f"{fmt(s_naw, 0)} ≥ {fmt(naw_os * osoby, 0)} m³/h",
                s_naw >= naw_os * osoby - 1e-6))
    spr.append(("Wywiew ≥ minima PN-B-03430/Az3 (WT § 149 ust. 1)", f"{fmt(s_wyw, 0)} ≥ {fmt(s_wmin, 0)} m³/h",
                all(p.wyw >= p.wyw_min - 1e-6 for p in PW)))
    spr.append(("Bilans nawiew = wywiew (±10 %)", f"{fmt(s_naw, 0)} / {fmt(s_wyw, 0)} m³/h", W.zrownowazony))
    spr.append(("Wydajność centrali ≥ strumień okresowy (kuchnia 120 m³/h)",
                f"{fmt(c.get('V_max_m3h', c.get('V_nom_m3h', 0)), 0)} ≥ {fmt(V_boost, 0)} m³/h",
                float(c.get("V_max_m3h", c.get("V_nom_m3h", 0))) >= V_boost - 1e-6))
    spr.append(("Odzysk ciepła ≥ 50 % (WT § 151 — obowiązkowy od 500 m³/h)", f"q = {fmt(q, 0)} m³/h; η = {fmt(eta, 2)}",
                True if q < 500 else eta >= 0.5))
    spr.append(("Odzysk ciepła ≥ cel projektu 0,85 [ZAŁ]", f"η = {fmt(eta, 2)}",
                eta >= float(wym("wentylacja", "odzysk_sprawnosc_cel", 0.85)) - 1e-9))
    spr.append(("SFP nawiewu z odzyskiem (WT § 154 ust. 10–11)", f"{fmt(SFP_n, 2)} ≤ {fmt(lim_n, 2)} kW/(m³/s)",
                SFP_n <= lim_n + 1e-9))
    spr.append(("SFP wywiewu z odzyskiem (WT § 154 ust. 10–11)", f"{fmt(SFP_w, 2)} ≤ {fmt(lim_w, 2)} kW/(m³/s)",
                SFP_w <= lim_w + 1e-9))
    sec = c.get("SEC_kWh_m2a")
    spr.append(("Ekoprojekt (UE) 1253/2014: SEC ≤ −20 kWh/(m²·a), by-pass, napęd wielobiegowy",
                f"SEC = {fmt(sec, 0)} kWh/(m²·a) (klasa {c.get('SEC_klasa', '?')})",
                None if sec is None else float(sec) <= float(wym("wentylacja", "centrala_SEC_max", -20))))
    # czerpnia / wyrzutnia
    spr += sprawdz_czerpnie_wyrzutnie(bryla.model, wc)
    # garaż
    for p in bryla.nieogrzewane:
        if rodzaj_pomieszczenia(p.nazwa, p.kategoria, p.raw) == "garaz":
            st = int((cfg.get("garaz") or {}).get("stanowiska", 2))
            otw = (cfg.get("garaz") or {}).get("otwory_went_m2")
            req = float(wym("garaz", "went_otwory_na_stanowisko", 0.04)) * st
            W.garaz.append((f"Garaż {p.id}: otwory wentylacji naturalnej ≥ 0,04 m²/stanowisko (WT § 108 ust. 1 pkt 1)",
                            f"{fmt(otw, 3) if otw is not None else '[DO UZUPEŁNIENIA]'} ≥ {fmt(req, 2)} m² ({st} stan.)",
                            None if otw is None else float(otw) >= req - 1e-9))
            W.garaz.append((f"Garaż {p.id}: bez podłączenia do rekuperacji (R6 3.5)", "wentylacja naturalna", True))
    if zal:
        zal.dodaj(f"Liczba osób: {osoby}", "[PROG]", "brief §4; wymagania.yaml wentylacja.liczba_osob")
        zal.dodaj("Centrala: " + str(c.get("opis", c.get("klucz", ""))) + f"; η_t = {fmt(eta, 2)}, SFP = "
                  f"{fmt(c.get('SFP_Wh_m3'), 2)} Wh/m³", "[DANE PRZYKŁADOWE – FIKCYJNE]" if "PRZYK" in str(c.get("status", ""))
                  else "", str(c.get("zrodlo", "")))
        zal.dodaj("Podział mocy wentylatorów nawiew/wywiew 50/50 do sprawdzenia SFP", ZAL)
    return W


def _odl(a, b):
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


def sprawdz_czerpnie_wyrzutnie(m, wc: dict) -> list[tuple[str, str, bool | None]]:
    """WT § 152 — kontrola położenia czerpni i wyrzutni (gdy podano w `energia.wentylacja.czerpnia/wyrzutnia` [x, y, z])."""
    out = []
    cz = wc.get("czerpnia")
    wy = wc.get("wyrzutnia")
    if cz is None or wy is None:
        out.append(("Czerpnia/wyrzutnia — położenie (WT § 152)", "[DO UZUPEŁNIENIA] energia.wentylacja.czerpnia/wyrzutnia",
                    None))
        return out
    cz = [float(x) for x in cz]
    wy = [float(x) for x in wy]
    dach = wc.get("typ_czerpni", "dachowa" if cz[2] > 3.0 else "scienna")
    zrodla = []
    dz = getattr(m, "dz", None)
    if dz is not None:
        try:
            dr = dz.raw.get("droga") or {}
            if dr.get("jezdnia"):
                from shapely.geometry import Polygon
                J = Polygon(dz.ring_bud(dr["jezdnia"]))
                zrodla.append(("jezdnia drogi", J))
            od = dz.raw.get("odpady") or {}
            if od.get("obrys"):
                from shapely.geometry import Polygon
                zrodla.append(("miejsce gromadzenia odpadów", Polygon(dz.ring_bud(od["obrys"]))))
        except Exception:  # noqa: BLE001
            pass
    from shapely.geometry import Point
    for xy in wc.get("wywiewki_kanalizacyjne") or []:
        zrodla.append(("wywiewka kanalizacyjna", Point(xy[:2])))
    lim = float(wym("wentylacja", "czerpnia_odl_ulica_odpady_wywiewki_min", 8.0))
    if dach == "scienna":
        teren = float(wc.get("rzedna_terenu", -0.30))
        out.append(("Czerpnia ścienna: dolna krawędź ≥ 2,0 m nad terenem (WT § 152 ust. 3)",
                    f"{fmt(cz[2] - teren, 2)} m", cz[2] - teren >= 2.0 - 1e-9))
        for nm, g in zrodla:
            d = g.distance(Point(cz[:2]))
            out.append((f"Czerpnia ścienna ≥ {fmt(lim, 0)} m od: {nm} (WT § 152 ust. 3)", f"{fmt(d, 2)} m", d >= lim - 1e-9))
    else:
        for nm, g in zrodla:
            if nm.startswith("wywiewka"):
                d = g.distance(Point(cz[:2]))
                out.append(("Czerpnia dachowa ≥ 6 m od wywiewek (WT § 152 ust. 4)", f"{fmt(d, 2)} m", d >= 6.0 - 1e-9))
    d_cw = _odl(cz, wy)
    dz_ = wy[2] - cz[2]
    pion = wc.get("wyrzut", "pionowy") == "pionowy"
    if pion:
        out.append(("Czerpnia–wyrzutnia na dachu ≥ 6 m, wyrzutnia ≥ 1 m wyżej (wyrzut pionowy, WT § 152 ust. 10)",
                    f"{fmt(d_cw, 2)} m; Δz = {fmt(dz_, 2)} m", (d_cw >= 6.0 and dz_ >= 1.0) or bool(wc.get("zestaw_zblokowany"))))
    else:
        out.append(("Czerpnia–wyrzutnia ≥ 10 m (wyrzut poziomy, WT § 152 ust. 10)", f"{fmt(d_cw, 2)} m",
                    d_cw >= 10.0 or bool(wc.get("zestaw_zblokowany"))))
    return out


def raport_wentylacja(W: WynikWent, zal: Zalozenia | None = None) -> str:
    s = [naglowek_raportu("Wentylacja mechaniczna z odzyskiem ciepła — bilans powietrza i dobór centrali",
                          "PN-83/B-03430/Az3:2000 (przez WT § 147 ust. 1, § 149 ust. 1) [NZW]; WT § 148–154; "
                          "rozp. (UE) 1253/2014",
                          [f"Źródło strumieni: {W.zrodlo_bilansu}."])]
    rows = []
    for p in W.pomieszczenia:
        rows.append([p.id, p.nazwa, p.rodzaj, fmt(p.A, 1), fmt(p.V, 1), fmt(p.wyw_min, 0), fmt(p.wyw, 0), fmt(p.naw, 0),
                     fmt(p.transfer, 0), fmt(p.n_h, 2), p.podstawa or "—"])
    rows.append(["", "**Razem**", "", "", "", fmt(W.suma_wyw_min, 0), fmt(W.suma_wyw, 0), fmt(W.suma_naw, 0), "", "", ""])
    s.append(tabela_md(["Pom.", "Nazwa", "Rodzaj", "A [m²]", "V [m³]", "Wywiew min [m³/h]", "Wywiew [m³/h]",
                        "Nawiew [m³/h]", "Transfer [m³/h]", "n [h⁻¹]", "Podstawa wywiewu"], rows, "lllrrrrrrrl"))
    s.append("")
    c = W.centrala
    s.append(f"Strumień projektowy q = max(Σ nawiewu; Σ wywiewu) = **{fmt(W.q_m3h, 0)} m³/h**; okresowo (kuchnia 120 m³/h) "
             f"{fmt(W.V_boost, 0)} m³/h. Centrala: {c.get('opis', '')} — V_nom = {fmt(c.get('V_nom_m3h'), 0)} m³/h, "
             f"η_t = {fmt(W.eta, 2)}, P_el = SFP·q = {fmt(W.P_el_W, 0)} W; kanał główny Ø{W.kanal_glowny_D_mm} mm "
             "(v ≤ 3 m/s).")
    s.append("")
    s.append(tabela_md(["Sprawdzenie", "Wartość", "Wynik"], [[a, b, ok(c_)] for a, b, c_ in W.sprawdzenia + W.garaz], "lll"))
    s.append("")
    for u in W.uwagi:
        s.append(f"* {u}")
    s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
