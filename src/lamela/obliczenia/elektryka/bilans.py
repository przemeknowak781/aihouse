"""Bilans mocy instalacji elektrycznej: odbiorniki (obwody) z modelu, moc zainstalowana, współczynniki jednoczesności,
moc szczytowa (bez i z dynamicznym zarządzaniem mocą — DLM), weryfikacja mocy przyłączeniowej i zabezpieczenia
przedlicznikowego, podział na fazy.

Podstawy (W-180…W-195, R7 §3.1–3.3):

* **WT §188 ust. 2** — obwody wydzielone: oświetlenie, gniazda ogólne, gniazda w łazience, gniazda kuchenne, odbiorniki
  wymagające indywidualnego zabezpieczenia; **§64** — oświetlenie zewnętrzne wejścia; **§102 pkt 3** — oświetlenie garażu.
* **Moc przyłączeniowa** — założenie R7 §3.1: **27 kW / zabezpieczenie przedlicznikowe 40 A** (W-192 [ZAŁ]); grupa
  przyłączeniowa V ≤ 40 kW (RSys §3 ust. 1 pkt 5); P = √3·U·I·cos φ (R7-L09: 40 A ↔ 27,7 kW przy cos φ = 1).
* **Współczynniki jednoczesności k_j** — wartości projektowe dla domu jednorodzinnego [ZAŁ] (literatura: N SEP-E-002,
  R7 §3.1 — „0,3–1,0”; wartości N SEP-E-002 **[NZW]**); porównanie z N SEP-E-002: 30 kVA bez elektrycznego ogrzewania
  + ogrzewanie elektryczne liczone osobno (R7-L08) [W].
* **PV** — moc przyłączeniowa ≥ moc mikroinstalacji (przyłączenie na zgłoszenie, Pr. energ. art. 7 ust. 8d4; W-194).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..inst_wspolne import DaneBudynku, Krok, Raport, Warunek, f, fa, wym, wym_zrodlo

U0, UN = 230.0, 400.0


@dataclass
class Odbiornik:
    id: str
    nazwa: str
    grupa: str
    P: float                         # kW — moc zainstalowana (umowna dla obwodów gniazd)
    fazy: int = 1
    cosphi: float = 0.95
    k_j: float = 1.0
    sterowany: bool = False          # objęty DLM (blokada/ograniczenie przy przekroczeniu mocy)
    lok: tuple | None = None         # (x, y, kond) — punkt najdalszy obwodu
    pomieszczenia: list = field(default_factory=list)
    typ_obwodu: str = "staly"        # oswietlenie | gniazda | staly | zewn
    In_min: int = 10
    char: str = "B"
    s_min: float = 1.5
    rcd: str = "RCBO typ A 30 mA"
    metoda: str = "C"
    przewod: str = "YDYp"
    podstawa: str = ""
    faza: str = ""                   # L1/L2/L3 (1f) lub L1L2L3
    generacja: bool = False          # źródło (PV) — poza bilansem poboru
    L_dodatkowa: float = 0.0         # m — odcinek zewnętrzny (ziemia) doliczany do trasy
    uwagi: str = ""

    @property
    def P_s(self) -> float:
        return 0.0 if self.generacja else self.k_j * self.P

    @property
    def I_B(self) -> float:
        if self.fazy == 3:
            return self.P * 1000.0 / (math.sqrt(3) * UN * self.cosphi)
        return self.P * 1000.0 / (U0 * self.cosphi)


@dataclass
class ParametryBilans:
    P_przylaczeniowa: float | None = None   # kW (W-192)
    I_zabezp: float | None = None           # A
    cosphi_sr: float = 0.95
    oswietlenie_W_m2: float = 5.0           # LED [ZAŁ]
    gniazda_P_obwod: float = 2.0            # kW — umowna moc obwodu gniazd [ZAŁ]
    maks_pow_obwodu_gniazd: float = 45.0    # m² na obwód gniazd ogólnych [ZAŁ]
    plyta_kW: float = 7.4
    piekarnik_kW: float = 3.5
    ev: bool | None = None                  # None → gdy jest garaż
    ev_kW: float = 11.0
    grzalka_kW: float = 6.0
    k_j: dict = field(default_factory=lambda: {
        "oswietlenie": 0.7, "gniazda": 0.2, "gniazda_kuchnia": 0.5, "gniazda_lazienka": 0.3, "gotowanie": 0.6,
        "agd": 0.6, "pc": 1.0, "grzalka": 1.0, "went": 1.0, "sterowanie": 1.0, "ev": 1.0, "zewn": 0.3, "tele": 1.0,
        "napedy": 0.3, "pompa": 0.3, "pv": 0.0})


@dataclass
class WynikBilans:
    dane: DaneBudynku
    par: ParametryBilans
    odbiorniki: list
    P_inst: float
    P_s_bez: float
    P_s_dlm: float
    P_przyl: float
    I_zab: float
    I_B: float
    fazy: dict
    asymetria: float
    sep: float
    warunki: list
    kroki: list
    zalozenia: list

    def do_dict(self) -> dict:
        return {"P_inst_kW": round(self.P_inst, 1), "P_szczyt_bez_DLM_kW": round(self.P_s_bez, 1),
                "P_szczyt_DLM_kW": round(self.P_s_dlm, 1), "P_przylaczeniowa_kW": self.P_przyl, "I_zab_A": self.I_zab,
                "fazy_kW": {k: round(v, 2) for k, v in self.fazy.items()}, "asymetria": round(self.asymetria, 3)}

    def raport(self) -> Raport:
        return _raport(self)

    def raport_md(self) -> str:
        return self.raport().md()


# --------------------------------------------------------------------------------------------------
# Odbiorniki z modelu
# --------------------------------------------------------------------------------------------------
def _wyp(dane: DaneBudynku, typ: str) -> list:
    return [e for e in dane.wyposazenie + (dane.inst.get("przybory_dodatkowe") or []) if e.get("typ") == typ and e.get("xy")]


def odbiorniki_z_modelu(dane: DaneBudynku, par: ParametryBilans | None = None, ogrzewanie=None, woda=None,
                        wentylacja_m3h: float | None = None, pv_kW_AC: float | None = None) -> list[Odbiornik]:
    """Lista odbiorników/obwodów wg WT §188 ust. 2 i rejestru R7 §3.3 na podstawie modelu i wyników modułów
    sanitarnych (moc PC, grzałki) — lokalizacje z modelu (pomieszczenia, wyposażenie, działka)."""
    par = par or ParametryBilans()
    kj = par.k_j
    out: list[Odbiornik] = []
    kond = [k["id"] for k in dane.kondygnacje]
    poms = dane.pomieszczenia
    mokre = set()
    try:
        from ..sanitarne.przybory import przybory_z_modelu
        mokre = {p.pom for p in przybory_z_modelu(dane) if p.typ in ("wanna", "prysznic", "wc", "umywalka", "umywalka_blat")}
    except Exception:
        pass

    def rodzaj(p):
        if p.id in mokre and p.rodzaj not in ("kuchnia",):
            return "lazienka"
        return p.rodzaj
    # --- oświetlenie: 1 obwód na kondygnację (+ garaż/techniczne osobno)
    for i, k in enumerate(kond):
        rs = [p for p in poms if p.kond == k and rodzaj(p) not in ("garaz",)]
        if not rs:
            continue
        P = max(0.1, par.oswietlenie_W_m2 * sum(p.pow for p in rs) / 1000.0)
        far = max(rs, key=lambda p: p.pow)
        out.append(Odbiornik(f"L{i + 1}", f"Oświetlenie {k}", "oswietlenie", P, 1, 0.95, kj["oswietlenie"],
                             lok=(*far.centroid, k), pomieszczenia=[p.id for p in rs], typ_obwodu="oswietlenie", In_min=10,
                             s_min=1.5, podstawa="WT §188 ust. 2, §189 ust. 2 (łączniki wieloobwodowe); PN-HD 60364-4-41 p. 411.3.4"))
    gar = [p for p in poms if rodzaj(p) in ("garaz", "techniczne")]
    if gar:
        out.append(Odbiornik(f"L{len(kond) + 1}", "Oświetlenie garażu i pom. technicznego", "oswietlenie",
                             max(0.1, par.oswietlenie_W_m2 * sum(p.pow for p in gar) / 1000), 1, 0.95, kj["oswietlenie"],
                             lok=(*gar[0].centroid, gar[0].kond), pomieszczenia=[p.id for p in gar], typ_obwodu="oswietlenie",
                             podstawa="WT §102 pkt 3"))
    # oświetlenie zewnętrzne (wejście — §64)
    m = dane.model
    wej = None
    if m is not None:
        dz = [o for o in m.otwory() if o.typ == "drzwi_zewn"]
        if dz:
            c = dz[0].srodek
            wej = (float(c[0]), float(c[1]), dz[0].kond)
    out.append(Odbiornik("L" + str(len([o for o in out if o.grupa == "oswietlenie"]) + 1), "Oświetlenie zewnętrzne (wejście, elewacje, taras)",
                         "oswietlenie", 0.2, 1, 0.95, kj["oswietlenie"], lok=wej, typ_obwodu="oswietlenie",
                         przewod="YDYp / YKY (ziemia)", podstawa="WT §64 (oświetlenie wejścia obowiązkowe); PN-HD 60364-7-714",
                         L_dodatkowa=10.0))
    # --- gniazda ogólne: pokoje, hole — grupy ≤ maks_pow_obwodu
    g = 0
    for k in kond:
        rs = [p for p in poms if p.kond == k and rodzaj(p) in ("pokoj", "sypialnia", "ruchu", "garderoba", "inne")]
        grupa, A = [], 0.0
        grupy = []
        for p in sorted(rs, key=lambda p: p.centroid):
            if grupa and A + p.pow > par.maks_pow_obwodu_gniazd:
                grupy.append(grupa)
                grupa, A = [], 0.0
            grupa.append(p)
            A += p.pow
        if grupa:
            grupy.append(grupa)
        for gr in grupy:
            g += 1
            far = gr[-1]
            out.append(Odbiornik(f"G{g}", f"Gniazda {k}: " + ", ".join(f"{p.id} {p.nazwa}" for p in gr), "gniazda",
                                 par.gniazda_P_obwod, 1, 0.95, kj["gniazda"], lok=(*far.centroid, k), pomieszczenia=[p.id for p in gr],
                                 typ_obwodu="gniazda", In_min=16, s_min=2.5, podstawa="WT §188 ust. 2; PN-HD 60364-4-41 p. 411.3.3"))
    # kuchnia — 2 obwody gniazd blatu
    for p in [p for p in poms if rodzaj(p) == "kuchnia"]:
        for j in (1, 2):
            g += 1
            out.append(Odbiornik(f"G{g}", f"Gniazda kuchenne {j} ({p.id} {p.nazwa})", "gniazda_kuchnia", par.gniazda_P_obwod, 1, 0.95,
                                 kj["gniazda_kuchnia"], lok=(*p.centroid, p.kond), pomieszczenia=[p.id], typ_obwodu="gniazda",
                                 In_min=16, s_min=2.5, podstawa="WT §188 ust. 2 (gniazda kuchenne)"))
    # łazienki — obwód gniazd na łazienkę
    for p in [p for p in poms if rodzaj(p) in ("lazienka", "wc")]:
        g += 1
        out.append(Odbiornik(f"G{g}", f"Gniazda łazienki ({p.id} {p.nazwa})", "gniazda_lazienka", par.gniazda_P_obwod, 1, 0.95,
                             kj["gniazda_lazienka"], lok=(*p.centroid, p.kond), pomieszczenia=[p.id], typ_obwodu="gniazda",
                             In_min=16, s_min=2.5, podstawa="WT §188 ust. 2 (gniazda w łazience); PN-HD 60364-7-701 (RCD 30 mA)"))
    if gar:
        g += 1
        out.append(Odbiornik(f"G{g}", "Gniazda garażu / pom. technicznego (IP44)", "gniazda", par.gniazda_P_obwod, 1, 0.95, kj["gniazda"],
                             lok=(*gar[0].centroid, gar[0].kond), typ_obwodu="gniazda", In_min=16, s_min=2.5, podstawa="WT §188 ust. 2"))
    g += 1
    taras = None
    if m is not None and m.tarasy():
        from lamela.model import make_polygon
        c = make_polygon(m.tarasy()[0]["obrys"]).centroid
        taras = (c.x, c.y, kond[0])
    out.append(Odbiornik(f"G{g}", "Gniazda zewnętrzne (taras, ogród; IP44/IP54)", "zewn", par.gniazda_P_obwod, 1, 0.95, kj["zewn"],
                         lok=taras or wej, typ_obwodu="gniazda", In_min=16, s_min=2.5, przewod="YKY (ziemia) / YDYp",
                         podstawa="PN-HD 60364-4-41 p. 411.3.3 (urządzenia ruchome na zewnątrz)", L_dodatkowa=8.0))
    # --- odbiorniki z indywidualnym zabezpieczeniem
    d = 0

    def D(nazwa, grupa, P, fazy, lok, In_min=16, char="B", s_min=2.5, rcd="RCBO typ A 30 mA", ster=False, podst="WT §188 ust. 2", **kw):
        nonlocal d
        d += 1
        out.append(Odbiornik(f"D{d}", nazwa, grupa, P, fazy, kw.pop("cosphi", 0.95), kj.get(grupa, 1.0), sterowany=ster, lok=lok,
                             typ_obwodu=kw.pop("typ", "staly"), In_min=In_min, char=char, s_min=s_min, rcd=rcd, podstawa=podst, **kw))
    for e in _wyp(dane, "plyta"):
        D("Płyta indukcyjna", "gotowanie", par.plyta_kW, 3, (*e["xy"], e.get("kond", "P0")), rcd="RCD 4P 40 A/30 mA typ A")
    kuch = [p for p in poms if rodzaj(p) == "kuchnia"]
    if kuch:
        D("Piekarnik", "gotowanie", par.piekarnik_kW, 1, (*kuch[0].centroid, kuch[0].kond))
    for typ, naz, P in (("zmywarka", "Zmywarka", 2.2), ("pralka", "Pralka", 2.2), ("suszarka", "Suszarka", 2.5)):
        for e in _wyp(dane, typ):
            D(naz, "agd", P, 1, (*e["xy"], e.get("kond", "P0")))
    # pompa ciepła i grzałka
    jz = dane.lok("pompa_ciepla_jz")
    zas = dane.lok("zasobnik") or dane.lok("RG")
    if ogrzewanie is not None:
        pc = ogrzewanie.pc
        P_el = max(p / c for p, c in zip(pc["P"], pc["COP"])) * 1.25
        grz = ogrzewanie.par.grzalka_kW
        nazwa_pc = pc["model"]
    else:
        P_el, grz, nazwa_pc = 3.0, par.grzalka_kW, "PC (moc wg DTR)"
    P_el = max(P_el, 1.5)
    D(f"Pompa ciepła — jednostka zewnętrzna ({nazwa_pc})", "pc", round(P_el, 2), 3 if P_el > 3.0 else 1, jz or zas, In_min=16, char="C",
      rcd="RCD typ F/B 30 mA wg DTR (falownik sprężarki)", przewod="YKY (zewn.) / YDYp", metoda="C",
      podst="R7 D6; PN-HD 60364-5-53 (typ RCD wg DTR)", L_dodatkowa=2.0)
    D(f"Grzałka rezerwowa PC / zasobnika c.w.u. ({f(grz, 1)} kW)", "grzalka", grz, 3, zas, In_min=10, ster=True,
      rcd="RCD 4P 40 A/30 mA typ A", podst="R7 D7 — blokada w systemie zarządzania mocą (DLM)")
    D("Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego", "sterowanie", 0.3, 1, zas, In_min=10, s_min=1.5)
    V = wentylacja_m3h if wentylacja_m3h is not None else 330.0
    rek = _wyp(dane, "rekuperator")
    D(f"Rekuperator (V ≈ {f(V, 0)} m³/h)", "went", max(0.15, 0.5 * V / 1000.0 + 0.0), 1,
      (*rek[0]["xy"], rek[0].get("kond", "P0")) if rek else (dane.lok("RG") or zas), In_min=10, s_min=1.5,
      podst="R7 D9; moc wentylatorów ≈ 0,5 W/(m³/h) [ZAŁ]")
    # falownik PV (generacja)
    if pv_kW_AC is None:
        pv_kW_AC = 6.0
    D(f"Falownik PV 3f ({f(pv_kW_AC, 1)} kW AC)", "pv", pv_kW_AC, 3, dane.lok("RG") or zas, In_min=16, char="B",
      rcd="RCD typ B 30 mA (lub wg 712.530.3.101 — DTR falownika)", podst="PN-HD 60364-7-712; R7-I06", generacja=True, cosphi=1.0)
    # EV
    ev = par.ev if par.ev is not None else bool(gar and any(rodzaj(p) == "garaz" for p in gar))
    if ev:
        gg = next(p for p in gar if rodzaj(p) == "garaz")
        D(f"Ładowarka EV {f(par.ev_kW, 0)} kW (3f) — garaż; przewód na 22 kW", "ev", par.ev_kW, 3, (*gg.centroid, gg.kond), In_min=20,
          char="C", s_min=6.0, ster=True, rcd="własny RCD typ B 30 mA lub A-EV + RDC-DD 6 mA DC", podst="PN-HD 60364-7-722; R7-J03",
          cosphi=0.99)
    # bramy, teletechnika, pompa zbiornika, osłony
    if m is not None and any(o.typ == "brama" for o in m.otwory()):
        o = next(o for o in m.otwory() if o.typ == "brama")
        D("Napęd bramy garażowej", "napedy", 0.3, 1, (float(o.srodek[0]), float(o.srodek[1]), o.kond), In_min=10, s_min=1.5)
    br = [b for b in dane.dzialka.get("bramy") or [] if b.get("typ") in ("przesuwna", "furtka")]
    if br:
        b = br[0]["xy_bud"]
        D("Brama wjazdowa, furtka, wideodomofon (linia ogrodzenia)", "napedy", 0.5, 1, (b[0], b[1], kond[0]), In_min=16,
          przewod="YKY (ziemia)", metoda="D1", podst="R7 D14")
    D("Teletechnika: ONT, router, szafka RACK, SSWiN", "tele", 0.2, 1, dane.lok("RG") or zas, In_min=16, podst="R7 D17; GIA art. 10")
    ret = dane.dzialka.get("retencja") or {}
    if (ret.get("zbiornik") or {}).get("xy") and dane.dzialka.get("transform") is not None:
        xy = tuple(dane.dzialka["transform"].do_budynku(ret["zbiornik"]["xy"]))
        D("Pompa zbiornika wody deszczowej (podlewanie)", "pompa", 0.8, 1, (xy[0], xy[1], kond[0]), In_min=16, przewod="YKY (ziemia)",
          metoda="D1", podst="R7 D15; W-145")
    if m is not None:
        n_osl = sum(1 for o in m.otwory() if (o.oslona or "brak") not in ("brak", None))
        if n_osl:
            D(f"Napędy osłon przeciwsłonecznych ({n_osl} szt.)", "napedy", 0.1 * n_osl, 1, dane.lok("RG") or zas, In_min=10, s_min=1.5,
              podst="R7 D16")
    return out


def _przypisz_fazy(odb: list[Odbiornik]) -> dict:
    fazy = {"L1": 0.0, "L2": 0.0, "L3": 0.0}
    for o in odb:
        if o.fazy == 3:
            o.faza = "L1L2L3"
            for k in fazy:
                fazy[k] += o.P_s / 3.0
    for o in sorted([o for o in odb if o.fazy == 1], key=lambda o: -max(o.P_s, 0.05 * o.P)):
        k = min(fazy, key=fazy.get)
        o.faza = k
        fazy[k] += o.P_s
    return fazy


def bilans_mocy(dane: DaneBudynku, odbiorniki: list[Odbiornik], par: ParametryBilans | None = None,
                pv_kWp: float | None = None) -> WynikBilans:
    par = par or ParametryBilans()
    P_przyl = par.P_przylaczeniowa if par.P_przylaczeniowa is not None else float(wym("elektryka", "moc_przylaczeniowa_projekt", 27) or 27)
    I_zab = par.I_zabezp if par.I_zabezp is not None else float(wym("elektryka", "zabezpieczenie_przedlicznikowe_projekt", 40) or 40)
    P_inst = sum(o.P for o in odbiorniki if not o.generacja)
    P_bez = sum(o.P_s for o in odbiorniki)
    P_nster = sum(o.P_s for o in odbiorniki if not o.sterowany)
    P_ster = sum(o.P_s for o in odbiorniki if o.sterowany)
    P_dlm = P_nster + min(P_ster, max(0.0, P_przyl - P_nster))
    fazy = _przypisz_fazy(odbiorniki)
    sr = sum(fazy.values()) / 3.0
    asym = (max(fazy.values()) - min(fazy.values())) / sr if sr > 0 else 0.0
    I_B = P_dlm * 1000.0 / (math.sqrt(3) * UN * par.cosphi_sr)
    I_faza_max = max(fazy.values()) * 1000.0 / (U0 * par.cosphi_sr)
    P_z_I = math.sqrt(3) * UN * I_zab / 1000.0
    ogrz = sum(o.P_s for o in odbiorniki if o.grupa in ("pc", "grzalka"))
    sep = 30.0 * par.cosphi_sr + ogrz
    war = [
        Warunek("Moc szczytowa z DLM ≤ moc przyłączeniowa", P_dlm, "<=", P_przyl, "kW", wym_zrodlo("elektryka", "moc_przylaczeniowa_projekt"), "W-192"),
        Warunek("Prąd szczytowy ≤ zabezpieczenie przedlicznikowe", I_B, "<=", I_zab, "A", "R7-L09", "W-192", nd=1),
        Warunek("Najbardziej obciążona faza: prąd ≤ zabezpieczenie przedlicznikowe", I_faza_max, "<=", I_zab, "A", "", "W-192", nd=1),
        Warunek("Moc przyłączeniowa ≤ 40 kW (grupa V)", P_przyl, "<=", float(wym("elektryka", "grupa_przylaczeniowa_V_moc_max", 40) or 40),
                "kW", "RSys §3 ust. 1 pkt 5", "W-192"),
        Warunek("Moc przyłączeniowa ↔ zabezpieczenie (√3·400·I_zab, cos φ = 1)", P_przyl, "<=", P_z_I, "kW", "R7-L09", "W-192"),
        Warunek("Asymetria obciążenia faz (max − min)/średnia", asym, "<=", 0.30, "", "praktyka [ZAŁ]", "W-180", nd=2),
    ]
    if pv_kWp is not None:
        war.append(Warunek("Moc PV ≤ moc przyłączeniowa (zgłoszenie mikroinstalacji)", pv_kWp, "<=", P_przyl, "kW",
                           "Pr. energ. art. 7 ust. 8d4", "W-194"))
    if P_bez > P_przyl:
        war.append(Warunek("Moc szczytowa BEZ zarządzania mocą ≤ moc przyłączeniowa (informacyjnie — wymagany DLM)", P_bez, "<=", P_przyl,
                           "kW", "R7 §3.1", "W-192", uwagi="DLM: ograniczenie EV i blokada grzałek"))
    kroki = [
        Krok("Moc zainstalowana (bez generacji PV)", "P_i = ΣP", "", P_inst, "kW", "", 1),
        Krok("Moc szczytowa bez zarządzania mocą", "P_s = Σk_j·P", "", P_bez, "kW", "k_j [ZAŁ]", 1),
        Krok("Moc szczytowa z DLM (odbiorniki sterowane ograniczone do mocy przyłączeniowej)",
             "P_s,DLM = P_nst + min(P_st; P_przył − P_nst)", f"{f(P_nster, 2)} + min({f(P_ster, 2)}; {f(P_przyl, 1)} − {f(P_nster, 2)})",
             P_dlm, "kW", "", 1),
        Krok("Prąd szczytowy", "I_B = P_s/(√3·U·cos φ)", f"{f(P_dlm * 1000, 0)}/(√3·400·{f(par.cosphi_sr, 2)})", I_B, "A", "", 1),
        Krok("Kontrolnie N SEP-E-002: 30 kVA + ogrzewanie elektryczne (PC + grzałka)", "P = 30·cos φ + P_ogrz",
             f"30·{f(par.cosphi_sr, 2)} + {f(ogrz, 2)}", sep, "kW", "R7-L08 [W]", 1),
        Krok("Moc odpowiadająca zabezpieczeniu przedlicznikowemu", "P = √3·400·I_zab", f"√3·400·{f(I_zab, 0)}", P_z_I, "kW", "R7-L09", 1),
    ]
    zal = ["Współczynniki jednoczesności: " + ", ".join(f"{k} {f(v, 1)}" for k, v in par.k_j.items()) + " [ZAŁ].",
           f"Obwody gniazd: moc umowna {f(par.gniazda_P_obwod, 1)} kW/obwód; oświetlenie LED {f(par.oswietlenie_W_m2, 0)} W/m² [ZAŁ].",
           "DLM (dynamiczne zarządzanie mocą): ograniczenie mocy ładowarki EV i blokada grzałki PC przy przekroczeniu mocy przyłączeniowej."]
    return WynikBilans(dane=dane, par=par, odbiorniki=odbiorniki, P_inst=P_inst, P_s_bez=P_bez, P_s_dlm=P_dlm, P_przyl=P_przyl,
                       I_zab=I_zab, I_B=I_B, fazy=fazy, asymetria=asym, sep=sep, warunki=war, kroki=kroki, zalozenia=zal)


def _raport(w: WynikBilans) -> Raport:
    R = Raport("Bilans mocy instalacji elektrycznej", f"Obiekt: {w.dane.nazwa}. Dane przykładowe oznaczono [ZAŁ].")
    R.h(2, "1. Podstawy i założenia")
    R.lista(["WT §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-180…W-195; rejestr R7 §3.1–3.3.",
             "Moc przyłączeniowa 27 kW / zabezpieczenie przedlicznikowe 40 A — założenie do wniosku o warunki przyłączenia "
             "(ENEA Operator, grupa V) [ZAŁ]."] + w.zalozenia)
    R.h(2, "2. Odbiorniki")
    R.tab(["Obw.", "Odbiornik", "Grupa", "P [kW]", "Fazy", "cos φ", "k_j", "P_s [kW]", "DLM", "Faza"],
          [[o.id, o.nazwa, o.grupa, f(o.P, 2), str(o.fazy), f(o.cosphi, 2), f(o.k_j, 2), f(o.P_s, 2) if not o.generacja else "gen.",
            "tak" if o.sterowany else "—", o.faza] for o in w.odbiorniki], "lllrrrrrll")
    R.h(2, "3. Moc szczytowa i przyłączeniowa")
    R.kroki(w.kroki)
    R.h(2, "4. Podział na fazy (moc szczytowa)")
    R.tab(["Faza", "P_s [kW]", "I [A]"], [[k, f(v, 2), f(v * 1000 / (U0 * w.par.cosphi_sr), 1)] for k, v in w.fazy.items()], "lrr")
    R.p(f"Asymetria (max − min)/średnia = {f(100 * w.asymetria, 0)} %. Odbiorniki 1-fazowe przypisano algorytmem zachłannym "
        "(najpierw największe, do najmniej obciążonej fazy).")
    R.h(2, "5. Sprawdzenia")
    R.war(w.warunki)
    R.zrodlo("WT §64, §102, §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.)", "RSys (t.j. Dz.U. 2025 poz. 919) §3 ust. 1 pkt 5; Pr. energ. art. 7",
             "N SEP-E-002 — wg SEP (Boczkowski 2013) [W]", "Rejestr R7 §3.1 (bilans szacunkowy), R7-L08, R7-L09")
    return R
