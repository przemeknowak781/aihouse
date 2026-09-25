"""Współczynnik przenikania ciepła U przegród nieprzezroczystych wg PN-EN ISO 6946:2017-10.

Zakres:
* opory przejmowania R_si / R_se wg kierunku strumienia ciepła (PN-EN ISO 6946:2017 p. 6.8, tab. 7):
  R_si = 0,10 (w górę) / 0,13 (poziomo ±30°) / 0,17 (w dół), R_se = 0,04; dla przegród do przestrzeni
  nieogrzewanej R_se = R_si (p. 6.8) [NZW — wartości potwierdzone w źródłach wtórnych, rejestr W-250];
* warstwy jednorodne R = d/λ (p. 6.7.1); warstwy powietrza niewentylowane (tab. 8, interpolacja liniowa),
  słabo wentylowane (½ R, p. 6.9.3) i dobrze wentylowane (pominięcie warstw zewnętrznych, R_se = R_si; p. 6.9.4);
* warstwy niejednorodne (ruszt, lamele, legary, ruszt stropu drewnianego) — metoda kresów (p. 6.7.2):
  R_T = (R'_T + R''_T)/2, błąd względny e = (R'_T − R''_T)/(2R_T); warunek stosowalności R'_T/R''_T ≤ 1,5;
* poprawki ΔU wg zał. F: ΔU_g (nieszczelności; poziom 0/1/2 → ΔU'' = 0/0,01/0,04), ΔU_f (łączniki mechaniczne:
  n_f·χ_p z deklaracji albo α·λ_f·A_f·n_f/d_0·(R_1/R_T,h)², α = 0,8 lub 0,8·d_1/d_0), ΔU_r (dach odwrócony:
  p·f·x·(R_1/R_T)²) [NZW — wzory zał. F z literatury, zał. F poza próbką normy];
* warstwy klinowe (izolacja spadkowa) — zał. C: wzory analityczne (C.3–C.5) dla prostokąta i trójkątów oraz
  całkowanie numeryczne po wieloboku dachu dla grubości rosnącej od wpustów;
* porównanie z U_C(max) wg WT zał. 2 pkt 1.1–1.2 i z celami projektu (rejestr W-243…W-245).

Wynik U_c podaje się z dokładnością do 2 cyfr znaczących (p. 6.? normy); obliczenia pośrednie — pełna precyzja.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Sequence

import numpy as np

from ..wspolne import (INT, NZW, PRZYKL, ZAL, Zalozenia, fmt, fmt_r, fmt_u, naglowek_raportu, ok, tabela_md,
                       wymaganie, wyrob, zaokr_znaczace)
from .warstwy import GRUNT_FUNKCJE, MatProp, funkcja_warstwy, mat_props

RSI = {"gora": 0.10, "poziomo": 0.13, "dol": 0.17}
RSE = 0.04
# PN-EN ISO 6946:2017 tab. 8 — opór niewentylowanej warstwy powietrza [m²K/W], powierzchnie o dużej emisyjności
_TAB8_D = [0.0, 0.005, 0.007, 0.010, 0.015, 0.025, 0.050, 0.100, 0.300]
_TAB8 = {"gora": [0.00, 0.11, 0.13, 0.15, 0.16, 0.16, 0.16, 0.16, 0.16],
         "poziomo": [0.00, 0.11, 0.13, 0.15, 0.17, 0.18, 0.18, 0.18, 0.18],
         "dol": [0.00, 0.11, 0.13, 0.15, 0.17, 0.19, 0.21, 0.22, 0.23]}
DU_PUSTKI = {0: 0.0, 1: 0.01, 2: 0.04}   # zał. F.2, ΔU'' [W/(m²K)]


def r_pustki(d: float, kierunek: str) -> float:
    """Opór cieplny niewentylowanej warstwy powietrza (PN-EN ISO 6946:2017 tab. 8, interpolacja liniowa) [NZW]."""
    tab = _TAB8[kierunek]
    if d >= _TAB8_D[-1]:
        return tab[-1]
    return float(np.interp(d, _TAB8_D, tab))


# --------------------------------------------------------------------------------------------------
# Struktury
# --------------------------------------------------------------------------------------------------
@dataclass
class WarstwaU:
    lp: int
    kod: str
    nazwa: str
    d: float
    lam: float | None
    R: float                      # opór warstwy (jednorodnej / równoważnej dolny kres) [m²K/W]
    rodzaj: str                   # jednorodna | niejednorodna | pustka_nw | pustka_sw | pustka_dw | pominieta | klin | grunt
    funkcja: str
    frakcje: list[tuple[str, float, float]] | None = None      # (kod, λ, udział)
    grupa: str | None = None
    uwagi: str = ""


@dataclass
class PoprawkiU:
    """Dane do poprawek ΔU wg PN-EN ISO 6946:2017 zał. F."""
    poziom_pustek: int = 1                    # 0 / 1 / 2  (rejestr W-250: poziom 1 domyślnie, chyba że wykazano 0)
    laczniki: dict | None = None              # {"n_f": 6, "chi_p": 0.002} albo {"n_f", "lam_f", "A_f", "d_0", "d_1"}
    dach_odwrocony: dict | None = None        # {"p": mm/d, "fx": W·d/(m²·K·mm)}
    warstwa_R1: int | None = None             # indeks warstwy izolacji do (R_1/R_T)² (domyślnie izolacja o max R)
    zrodlo_lacznikow: str = ""


@dataclass
class WynikU:
    kod: str
    nazwa: str
    rola: str
    kierunek: str
    Rsi: float
    Rse: float
    warstwy: list[WarstwaU]
    R_T: float                     # opór całkowity (z R_si, R_se) — średnia kresów dla przegród niejednorodnych
    R_gorny: float | None = None
    R_dolny: float | None = None
    blad_wzgl: float | None = None
    U0: float = 0.0                # 1/R_T
    dU_g: float = 0.0
    dU_f: float = 0.0
    dU_r: float = 0.0
    U_c: float = 0.0               # U0 + ΔU (przy stałej grubości)
    klin: dict | None = None       # {"U_sr": .., "d_min", "d_max", "metoda"}
    U: float = 0.0                 # wartość do bilansu (U_c; dla warstw klinowych — średnia z zał. C + ΔU)
    U_max: float | None = None
    U_cel: float | None = None
    wym_id: str | None = None
    wym_zrodlo: str = ""
    uwagi: list[str] = field(default_factory=list)
    R_f: float | None = None       # opór podłogi na gruncie bez R_si/R_se (do PN-EN ISO 13370)

    @property
    def U_zaokr(self) -> float:
        return zaokr_znaczace(self.U, 2)

    @property
    def spelnia_WT(self) -> bool | None:
        return None if self.U_max is None else self.U_zaokr <= self.U_max + 1e-9

    @property
    def spelnia_cel(self) -> bool | None:
        return None if self.U_cel is None else self.U_zaokr <= self.U_cel + 1e-9

    @property
    def dU(self) -> float:
        return self.dU_g + self.dU_f + self.dU_r


# --------------------------------------------------------------------------------------------------
# Rola przegrody → kierunek strumienia, R_se, wymagania
# --------------------------------------------------------------------------------------------------
ROLA_KIERUNEK = {"sciana_zewn": "poziomo", "sciana_nieogrz": "poziomo", "sciana_wewn": "poziomo",
                 "dach": "gora", "strop_zewn": "dol", "strop_nieogrz": "dol", "strop_nieogrz_gora": "gora",
                 "podloga_grunt": "dol", "strop_wewn": "dol"}
ROLA_STRONA = {"sciana_zewn": "zewn", "sciana_nieogrz": "nieogrz", "sciana_wewn": "nieogrz", "dach": "zewn",
               "strop_zewn": "zewn", "strop_nieogrz": "nieogrz", "strop_nieogrz_gora": "nieogrz",
               "podloga_grunt": "grunt", "strop_wewn": "nieogrz"}
ROLA_WYM = {  # (klucz U_max, klucz U_cel) w sekcji 'energia' wymagania.yaml
    "sciana_zewn": ("U_max_sciana", "U_cel_sciana"),
    "sciana_nieogrz": ("U_max_sciana_ogrzewane_nieogrzewane", "U_cel_sciana_dom_garaz"),
    "dach": ("U_max_stropodach", "U_cel_stropodach"),
    "strop_zewn": ("U_max_strop_nad_powietrzem_zewn", None),
    "strop_nieogrz": ("U_max_strop_nad_nieogrzewanym", None),
    "strop_nieogrz_gora": ("U_max_strop_nad_nieogrzewanym", None),
    "podloga_grunt": ("U_max_podloga_na_gruncie", "U_cel_podloga"),
    "okno": ("U_max_okno", "U_cel_okno"),
    "okno_polaciowe": ("U_max_okno_polaciowe", None),
    "drzwi": ("U_max_drzwi_zewn", "U_cel_drzwi"),
}
ROLA_OPIS = {"sciana_zewn": "ściana zewnętrzna", "sciana_nieogrz": "ściana do pom. nieogrzewanego",
             "dach": "stropodach/dach", "strop_zewn": "strop nad powietrzem zewn.",
             "strop_nieogrz": "strop nad pom. nieogrzewanym", "strop_nieogrz_gora": "strop pod pom. nieogrzewanym",
             "podloga_grunt": "podłoga na gruncie", "sciana_wewn": "ściana wewnętrzna", "strop_wewn": "strop wewnętrzny"}


def wymagania_u(rola: str) -> tuple[float | None, float | None, str | None, str]:
    """(U_max WT, U_cel projektu, id wymagania, źródło) dla roli przegrody (WT zał. 2 pkt 1.1–1.2; rejestr W-243…W-245)."""
    k = ROLA_WYM.get(rola)
    if not k:
        return None, None, None, ""
    wm = wymaganie("energia", k[0])
    wc = wymaganie("energia", k[1]) if k[1] else None
    zr = wm.opis()
    if wc is not None and wc.wartosc is not None:
        zr += f"; cel: {wc.zrodlo} {wc.znacznik}".rstrip()
    return wm.wartosc, (wc.wartosc if wc else None), wm.id, zr


# --------------------------------------------------------------------------------------------------
# Obliczenie U
# --------------------------------------------------------------------------------------------------
def _warstwy_we(warstwy: Sequence[Any]) -> list[dict]:
    out = []
    for w in warstwy:
        if isinstance(w, dict):
            out.append(dict(w))
        else:                                   # lamela.model.Warstwa
            out.append({"mat": w.mat, "d": w.d, "konstrukcyjna": getattr(w, "konstrukcyjna", False)})
    return out


def oblicz_u(warstwy: Sequence[Any], materialy: Any = None, *, rola: str = "sciana_zewn", kierunek: str | None = None,
             strona: str | None = None, kolejnosc_od_wewn: bool | None = None, poprawki: PoprawkiU | None = None,
             kod: str = "", nazwa: str = "", klin_U: dict | None = None) -> WynikU:
    """Opór cieplny i U przegrody wg PN-EN ISO 6946:2017 (p. 6.7–6.9, zał. C, zał. F).

    `warstwy` — lista {mat, d, [lambda], [R], [frakcje: [{mat, udzial, [lambda]}], grupa], [pustka: nw|sw|dw], [funkcja]}
    w kolejności modelu (ściany od wnętrza, przegrody poziome od góry). `rola` — ROLA_KIERUNEK.
    `kolejnosc_od_wewn` — None: wg roli (dach/strop_nieogrz_gora — od zewnątrz; pozostałe — od wnętrza).
    `klin_U` — wynik zał. C (u_klin_*) nadpisujący U0 średnim U warstwy klinowej.
    """
    kierunek = kierunek or ROLA_KIERUNEK.get(rola, "poziomo")
    strona = strona or ROLA_STRONA.get(rola, "zewn")
    ws = _warstwy_we(warstwy)
    if kolejnosc_od_wewn is None:
        kolejnosc_od_wewn = rola not in ("dach", "strop_nieogrz_gora")
    # kolejność od wnętrza (ciepła strona) do zewnątrz
    seq = list(range(len(ws))) if kolejnosc_od_wewn else list(range(len(ws)))[::-1]
    Rsi = RSI[kierunek]
    Rse = RSE if strona == "zewn" else (Rsi if strona == "nieogrz" else 0.0)
    uw: list[str] = []
    WU: list[WarstwaU] = []
    pominiete_od = None
    for n, i in enumerate(seq):
        w = ws[i]
        mp = mat_props(materialy, w.get("mat")) if w.get("mat") else MatProp(kod=str(w.get("nazwa", "?")))
        fn = funkcja_warstwy(mp, w)
        d = float(w.get("d", 0.0))
        lam = float(w["lambda"]) if w.get("lambda") is not None else mp.lam
        nm = mp.nazwa or mp.kod
        if pominiete_od is not None:
            WU.append(WarstwaU(i + 1, mp.kod, nm, d, lam, 0.0, "pominieta", fn,
                               uwagi="poza dobrze wentylowaną warstwą powietrza — pominięta (p. 6.9.4)"))
            continue
        if strona == "grunt" and fn in GRUNT_FUNKCJE:
            WU.append(WarstwaU(i + 1, mp.kod, nm, d, lam, 0.0, "grunt", fn,
                               uwagi="podsypka/grunt — uwzględniona w metodzie PN-EN ISO 13370 (λ gruntu)"))
            continue
        pust = w.get("pustka")
        if pust is None and fn == "pustka" and not w.get("frakcje"):
            pust = "nw"
        if pust:
            pust = {"niewentylowana": "nw", "slabo_wentylowana": "sw", "dobrze_wentylowana": "dw"}.get(pust, pust)
            if pust == "dw":
                WU.append(WarstwaU(i + 1, mp.kod, nm, d, None, 0.0, "pustka_dw", "pustka",
                                   uwagi="dobrze wentylowana — R_se := R_si, warstwy zewnętrzne pominięte (p. 6.9.4)"))
                pominiete_od = n
                Rse = Rsi
                continue
            Ra = r_pustki(d, kierunek)
            if pust == "sw":
                Ra *= 0.5
            WU.append(WarstwaU(i + 1, mp.kod, nm, d, None, Ra, "pustka_" + pust, "pustka",
                               uwagi=f"tab. 8 {NZW}" + (" ×0,5 (słabo wentylowana)" if pust == "sw" else "")))
            continue
        if w.get("R") is not None:
            WU.append(WarstwaU(i + 1, mp.kod, nm, d, lam, float(w["R"]), "R_zadane", fn, uwagi="R z deklaracji"))
            continue
        fr = w.get("frakcje")
        if fr:
            frl = []
            for f in fr:
                mpf = mat_props(materialy, f.get("mat")) if f.get("mat") else MatProp(kod="?")
                lf = float(f["lambda"]) if f.get("lambda") is not None else mpf.lam
                if f.get("pustka"):
                    lf = d / r_pustki(d, kierunek)
                if lf is None:
                    raise ValueError(f"warstwa {i + 1}: brak λ frakcji {f.get('mat')}")
                frl.append((mpf.kod, float(lf), float(f["udzial"])))
            s = sum(u for _, _, u in frl)
            if abs(s - 1.0) > 1e-6:
                raise ValueError(f"warstwa {i + 1}: suma udziałów frakcji = {s:.4f} ≠ 1")
            lam_eq = sum(lf * u for _, lf, u in frl)
            WU.append(WarstwaU(i + 1, mp.kod, nm, d, lam_eq, d / lam_eq, "niejednorodna", fn, frakcje=frl,
                               grupa=str(w.get("grupa", f"g{i}")),
                               uwagi="λ'' = Σ f_q·λ_q (kres dolny)"))
            continue
        if lam is None or lam <= 0:
            raise ValueError(f"warstwa {i + 1} ({mp.kod}): brak λ materiału")
        rodz = "klin" if w.get("klin") else "jednorodna"
        WU.append(WarstwaU(i + 1, mp.kod, nm, d, lam, d / lam, rodz, fn,
                           uwagi="grubość minimalna warstwy klinowej (zał. C)" if rodz == "klin" else ""))

    # --- R_T: jednorodna lub metoda kresów ---
    niej = [x for x in WU if x.rodzaj == "niejednorodna"]
    R_hom = Rsi + sum(x.R for x in WU) + Rse
    Rg = Rd = e = None
    if niej:
        grupy: dict[str, list[WarstwaU]] = {}
        for x in niej:
            grupy.setdefault(x.grupa, []).append(x)
        # sekcje: iloczyn kartezjański grup (warstwy w jednej grupie mają wspólny podział)
        sekcje = [({}, 1.0)]
        for g, lst in grupy.items():
            n_fr = len(lst[0].frakcje)
            if any(len(x.frakcje) != n_fr or any(abs(a[2] - b[2]) > 1e-9 for a, b in zip(x.frakcje, lst[0].frakcje))
                   for x in lst):
                raise ValueError(f"grupa '{g}': warstwy o różnym podziale frakcji")
            nowe = []
            for sel, f in sekcje:
                for q in range(n_fr):
                    s2 = dict(sel)
                    for x in lst:
                        s2[x.lp] = q
                    nowe.append((s2, f * lst[0].frakcje[q][2]))
            sekcje = nowe
        R_stale = Rsi + Rse + sum(x.R for x in WU if x.rodzaj != "niejednorodna")
        suma = 0.0
        for sel, f in sekcje:
            Rm = R_stale + sum(x.d / x.frakcje[sel[x.lp]][1] for x in niej)
            suma += f / Rm
        Rg = 1.0 / suma
        Rd = R_hom
        R_T = 0.5 * (Rg + Rd)
        e = (Rg - Rd) / (2 * R_T)
        if Rg / Rd > 1.5:
            uw.append(f"R'_T/R''_T = {Rg / Rd:.2f} > 1,5 — metoda kresów poza zakresem (p. 6.7.2.1) — wymagane obliczenie numeryczne")
    else:
        R_T = R_hom
    U0 = 1.0 / R_T

    # --- poprawki zał. F ---
    pop = poprawki or PoprawkiU(poziom_pustek=0)
    izol = [x for x in WU if x.funkcja == "izolacja" and x.rodzaj in ("jednorodna", "niejednorodna", "klin", "R_zadane")]
    if pop.warstwa_R1 is not None:
        R1_layer = next((x for x in WU if x.lp == pop.warstwa_R1), None)
    else:
        R1_layer = max(izol, key=lambda x: x.R) if izol else None
    R1 = R1_layer.R if R1_layer else 0.0
    dU_g = DU_PUSTKI.get(int(pop.poziom_pustek), 0.0) * (R1 / R_T) ** 2 if R1 else 0.0
    dU_f = 0.0
    if pop.laczniki and R1:
        L = pop.laczniki
        n_f = float(L.get("n_f", 0.0))
        if L.get("chi_p") is not None:
            dU_f = n_f * float(L["chi_p"])
        else:
            d0 = float(L["d_0"])
            d1 = float(L.get("d_1", d0))
            alfa = 0.8 * (d1 / d0 if d1 < d0 else 1.0)
            dU_f = alfa * float(L["lam_f"]) * float(L["A_f"]) * n_f / d0 * (R1 / R_hom) ** 2
    dU_r = 0.0
    if pop.dach_odwrocony and R1:
        D = pop.dach_odwrocony
        dU_r = float(D.get("p", 0.0)) * float(D.get("fx", 0.04)) * (R1 / R_T) ** 2
    U_c = U0 + dU_g + dU_f + dU_r
    if U_c > 0 and (dU_g + dU_f + dU_r) < 0.03 * U0 and (dU_g + dU_f + dU_r) > 0:
        uw.append("ΣΔU < 3 % U — poprawki mogłyby zostać pominięte (zał. F); przyjęto je zachowawczo")
    U_fin = U_c
    if klin_U:
        U_fin = klin_U["U_sr"] + (dU_g + dU_f + dU_r)
    Umax, Ucel, wid, wzr = wymagania_u(rola)
    Rf = None
    if strona == "grunt":
        Rf = sum(x.R for x in WU)
    return WynikU(kod=kod, nazwa=nazwa, rola=rola, kierunek=kierunek, Rsi=Rsi, Rse=Rse, warstwy=WU, R_T=R_T,
                  R_gorny=Rg, R_dolny=Rd, blad_wzgl=e, U0=U0, dU_g=dU_g, dU_f=dU_f, dU_r=dU_r, U_c=U_c, klin=klin_U,
                  U=U_fin, U_max=Umax, U_cel=Ucel, wym_id=wid, wym_zrodlo=wzr, uwagi=uw, R_f=Rf)


# --------------------------------------------------------------------------------------------------
# Warstwy klinowe — PN-EN ISO 6946:2017 zał. C
# --------------------------------------------------------------------------------------------------
def u_klin_prostokat(R0: float, R1: float) -> float:
    """Zał. C, wzór (C.3): prostokąt, grubość liniowo od 0 do d_max: U = (1/R1)·ln(1 + R1/R0)."""
    if R1 <= 1e-12:
        return 1.0 / R0
    return math.log1p(R1 / R0) / R1


def u_klin_trojkat_max_w_wierzcholku(R0: float, R1: float) -> float:
    """Zał. C, wzór (C.4): trójkąt, największa grubość w wierzchołku: U = 2/R1·[(1 + R0/R1)·ln(1 + R1/R0) − 1]."""
    if R1 <= 1e-12:
        return 1.0 / R0
    x = R1 / R0
    if x < 1e-4:                         # rozwinięcie w szereg (unikanie utraty dokładności)
        return (1.0 / R0) * (1 - 2 * x / 3 + x * x / 2)
    return 2.0 / R1 * ((1 + R0 / R1) * math.log1p(x) - 1)


def u_klin_trojkat_min_w_wierzcholku(R0: float, R1: float) -> float:
    """Zał. C, wzór (C.5): trójkąt, najmniejsza grubość w wierzchołku: U = 2/R1·[1 − (R0/R1)·ln(1 + R1/R0)]."""
    if R1 <= 1e-12:
        return 1.0 / R0
    x = R1 / R0
    if x < 1e-4:
        return (1.0 / R0) * (1 - x / 3 + x * x / 4)
    return 2.0 / R1 * (1 - R0 / R1 * math.log1p(x))


def u_klin_wielobok(wielobok, R0: float, lam_klin: float, *, d_add_fn=None, wpusty: Sequence | None = None,
                    spadek: float = 0.02, krok: float = 0.10) -> dict:
    """Średnie U dachu z izolacją spadkową — całkowanie numeryczne po wieloboku (zał. C, p. C.1: U = (1/A)∫dA/R(x,y)).

    R0 — opór całkowity przy grubości minimalnej (z R_si, R_se); przyrost grubości d_add(x, y):
    domyślnie spadek·(odległość do najbliższego wpustu) — model „lejów” do wpustów [ZAŁ — przybliżenie układu płyt
    spadkowych; dla projektu wykonawczego — wg rysunku układu płyt producenta].
    """
    from shapely.geometry import Point, Polygon
    P = wielobok if hasattr(wielobok, "bounds") else Polygon(wielobok)
    x0, y0, x1, y1 = P.bounds
    xs = np.arange(x0 + krok / 2, x1, krok)
    ys = np.arange(y0 + krok / 2, y1, krok)
    X, Y = np.meshgrid(xs, ys)
    pts = np.c_[X.ravel(), Y.ravel()]
    from shapely import contains_xy
    inside = contains_xy(P, pts[:, 0], pts[:, 1])
    pts = pts[inside]
    if d_add_fn is None:
        W = np.array(wpusty if wpusty else [P.centroid.coords[0]], float)
        dist = np.min(np.hypot(pts[:, None, 0] - W[None, :, 0], pts[:, None, 1] - W[None, :, 1]), axis=1)
        d_add = spadek * dist
    else:
        d_add = np.array([d_add_fn(x, y) for x, y in pts])
    U = 1.0 / (R0 + d_add / lam_klin)
    return {"U_sr": float(U.mean()), "d_add_sr": float(d_add.mean()), "d_add_max": float(d_add.max()),
            "n_pkt": int(len(pts)), "metoda": "całkowanie numeryczne (zał. C, p. C.1), siatka "
            f"{fmt(krok, 2)} m, grubość rosnąca {fmt(spadek * 100, 1)} % od wpustów"}


# --------------------------------------------------------------------------------------------------
# Integracja z modelem
# --------------------------------------------------------------------------------------------------
def warstwy_przegrody(m, kod: str) -> list[dict]:
    """Surowe warstwy przegrody z modelu (z polami rozszerzonymi: frakcje, pustka, klin, funkcja, lambda, R)."""
    p = m.przegroda(kod)
    if p is None:
        raise KeyError(f"brak przegrody {kod}")
    raw = (p.raw or {}).get("warstwy") or []
    out = []
    for j, w in enumerate(p.warstwy):
        d = dict(raw[j]) if j < len(raw) and isinstance(raw[j], dict) else {}
        d.update({"mat": w.mat, "d": w.d, "konstrukcyjna": w.konstrukcyjna})
        out.append(d)
    return out


def warstwy_stropu(m, strop: dict, kond_nad: str | None, *, mat_plyty: str | None = None) -> tuple[list[dict], str]:
    """Pełny układ warstw stropu (od góry): podłoga kondygnacji wyżej + płyta + sufit (kod przegrody lub materiału).

    Zwraca (warstwy, opis). Materiał płyty: `stropy[].mat` → `mat_plyty` → 'ZB_C30' (jeżeli istnieje) → pierwszy
    materiał o kreskowaniu ZELBET."""
    ws: list[dict] = []
    opis = []
    kn = m.kondygnacja(kond_nad) if kond_nad else None
    pod = strop.get("podloga") or (kn.podloga if kn else None)
    if pod and m.przegroda(pod) is not None:
        ws += warstwy_przegrody(m, pod)
        opis.append(f"podłoga {pod}")
    mat = strop.get("mat") or mat_plyty
    if mat is None:
        mats = m.materialy
        mat = "ZB_C30" if "ZB_C30" in mats else next((k for k, v in mats.items() if (v.kreskowanie or "") == "ZELBET"), None)
    ws.append({"mat": mat, "d": float(strop.get("grubosc", 0.2)), "konstrukcyjna": True})
    opis.append(f"płyta {mat} {float(strop.get('grubosc', 0.2)) * 100:.0f} cm")
    suf = strop.get("sufit")
    if suf:
        if m.przegroda(suf) is not None:
            ws += warstwy_przegrody(m, suf)
            opis.append(f"sufit {suf}")
        elif m.material(suf) is not None:
            ws.append({"mat": suf, "d": 0.01})
            opis.append(f"sufit {suf} 1 cm")
    return ws, " + ".join(opis)


def poprawki_domyslne(rola: str, warstwy: list[dict], materialy: Any, zal: Zalozenia | None = None) -> PoprawkiU:
    """Poprawki ΔU wg rejestru W-250: poziom pustek 1 (chyba że wykazano 0); łączniki ETICS dla ścian z izolacją
    zewnętrzną z tynkiem (dane przykładowe ETA); dach odwrócony — p wg danych klimatycznych (założenie)."""
    fun = [funkcja_warstwy(mat_props(materialy, w.get("mat")), w) for w in warstwy]
    pop = PoprawkiU(poziom_pustek=1)
    if rola == "sciana_zewn" and "izolacja" in fun:
        i_iz = max(i for i, f in enumerate(fun) if f == "izolacja")
        if any(f == "tynk" for f in fun[i_iz + 1:]):          # ETICS: tynk na izolacji
            L = wyrob("laczniki", "ETICS")
            if L:
                pop.laczniki = {"n_f": L.get("n_f_m2", 6.0), "chi_p": L.get("chi_p", 0.002)}
                pop.zrodlo_lacznikow = L.get("zrodlo", "")
                if zal:
                    zal.dodaj(f"Łączniki ETICS: n_f = {fmt(L.get('n_f_m2'), 1)} szt./m², χ_p = {fmt(L.get('chi_p'), 3)} W/K "
                              "(ΔU_f = n_f·χ_p, PN-EN ISO 6946:2017 zał. F.3)", PRZYKL, L.get("zrodlo", ""))
    if rola == "dach" and "hydroizolacja" in fun and "izolacja" in fun:
        i_h = min(i for i, f in enumerate(fun) if f == "hydroizolacja")
        if any(f == "izolacja" for f in fun[:i_h]):            # izolacja nad hydroizolacją (warstwy od góry)
            pop.dach_odwrocony = {"p": 1.4, "fx": 0.04}
            if zal:
                zal.dodaj("Dach odwrócony: p = 1,4 mm/d (średni opad w sezonie grzewczym, Poznań), f·x = 0,04 "
                          "W·d/(m²·K·mm) (pojedyncza warstwa XPS, styki proste, balast żwirowy)", NZW,
                          "PN-EN ISO 6946:2017 zał. F.4; BRE BR 443 p. 4.9 (f·x)")
    if zal:
        zal.dodaj("Nieszczelności w warstwie izolacji: poziom 1 (ΔU'' = 0,01 W/(m²·K)), chyba że wykazano poziom 0",
                  NZW, "PN-EN ISO 6946:2017 zał. F.2; rejestr W-250")
    return pop


def u_przegrody_modelu(m, kod: str, rola: str, *, poprawki: PoprawkiU | None = None, zal: Zalozenia | None = None,
                       warstwy: list[dict] | None = None, dach: dict | None = None, nazwa: str | None = None) -> WynikU:
    """U przegrody modelu w danej roli. Dla dachów z warstwą klinową (`klin` w warstwie albo nazwa „spadkow…”) liczy
    średnie U wg zał. C (wielobok dachu z `dachy[]`, wpusty, spadek)."""
    ws = warstwy if warstwy is not None else warstwy_przegrody(m, kod)
    p = m.przegroda(kod)
    nm = nazwa or (p.nazwa if p is not None else kod)
    if poprawki is None:
        poprawki = poprawki_domyslne(rola, ws, m.materialy, zal)
    wyn = oblicz_u(ws, m.materialy, rola=rola, poprawki=poprawki, kod=kod, nazwa=nm)
    # warstwa klinowa
    if rola == "dach":
        kl = next(((j, w) for j, w in enumerate(ws) if w.get("klin") or
                   ("spadk" in (mat_props(m.materialy, w.get("mat")).nazwa or "").lower() and
                    funkcja_warstwy(mat_props(m.materialy, w.get("mat")), w) == "izolacja")), None)
        if kl is not None:
            j, w = kl
            lam = mat_props(m.materialy, w.get("mat")).lam
            spec = w.get("klin") or {}
            R0 = wyn.R_T                              # przy grubości z modelu = minimalnej
            if spec.get("d_max") is not None:
                d_min = float(spec.get("d_min", w["d"]))
                R0 = wyn.R_T + (d_min - w["d"]) / lam
                R1 = (float(spec["d_max"]) - d_min) / lam
                ks = spec.get("ksztalt", "prostokat")
                f = {"prostokat": u_klin_prostokat, "trojkat_max": u_klin_trojkat_max_w_wierzcholku,
                     "trojkat_min": u_klin_trojkat_min_w_wierzcholku}[ks]
                klin = {"U_sr": f(R0, R1), "d_min": d_min, "d_max": float(spec["d_max"]),
                        "metoda": f"zał. C — wzór dla kształtu '{ks}'"}
            elif dach is not None:
                wp = [tuple(x["xy"]) if isinstance(x, dict) else tuple(x) for x in (dach.get("wpusty") or [])]
                sp = float(dach.get("spadek") or 0.02)
                r = u_klin_wielobok(dach["obrys"], R0, lam, wpusty=wp or None, spadek=sp)
                klin = {"U_sr": r["U_sr"], "d_min": w["d"], "d_max": w["d"] + r["d_add_max"],
                        "d_sr": w["d"] + r["d_add_sr"], "metoda": r["metoda"]}
                if zal:
                    zal.dodaj(f"Izolacja spadkowa dachu {dach.get('id')}: grubość z modelu ({w['d'] * 100:.0f} cm) = "
                              "grubość minimalna przy wpustach; przyrost wg spadku do najbliższego wpustu", ZAL)
            else:
                klin = None
            if klin:
                wyn.klin = klin
                wyn.U = klin["U_sr"] + wyn.dU
                wyn.uwagi.append(f"warstwa klinowa: U średnie wg PN-EN ISO 6946:2017 zał. C ({klin['metoda']}); "
                                 f"d_min = {fmt(klin['d_min'] * 100, 1)} cm, d_max = {fmt(klin['d_max'] * 100, 1)} cm")
    return wyn


# --------------------------------------------------------------------------------------------------
# Raport
# --------------------------------------------------------------------------------------------------
def raport_u(wyniki: Sequence[WynikU], zal: Zalozenia | None = None, tytul: str = "Współczynniki przenikania ciepła U "
             "przegród (PN-EN ISO 6946:2017)", szczegoly: bool = True) -> str:
    s = [naglowek_raportu(tytul, "PN-EN ISO 6946:2017-10 (p. 6.7–6.9, zał. C, zał. F); WT zał. 2 pkt 1.1 (U_C(max)); "
                          "cele projektu wg rejestru W-245", [
                              "U_c = 1/R_T + ΔU_g + ΔU_f + ΔU_r; R_T = R_si + Σ d_j/λ_j + R_se "
                              "(przegrody niejednorodne: R_T = (R'_T + R''_T)/2).",
                              "Wynik U podano z dokładnością do 2 cyfr znaczących; opory — do 0,01 m²·K/W."])]
    wiersze = []
    for w in wyniki:
        wiersze.append([w.kod, w.nazwa, ROLA_OPIS.get(w.rola, w.rola),
                        (f"R_f = {fmt_r(w.R_f)}" if w.rola == "podloga_grunt" else fmt_r(w.R_T)), fmt(w.dU, 3), fmt_u(w.U),
                        fmt(w.U_max, 2) if w.U_max else "—", ok(w.spelnia_WT),
                        fmt(w.U_cel, 2) if w.U_cel else "—", ok(w.spelnia_cel)])
    s.append(tabela_md(["Kod", "Przegroda", "Rola", "R_T [m²K/W]", "ΣΔU", "U_c [W/(m²K)]", "U_C(max) WT",
                        "WT", "U cel", "cel"], wiersze, "lllrrrrlrl"))
    s.append("")
    if szczegoly:
        for w in wyniki:
            s.append(f"### {w.kod} — {w.nazwa} ({ROLA_OPIS.get(w.rola, w.rola)})")
            s.append("")
            s.append(f"Kierunek strumienia: {w.kierunek}; R_si = {fmt(w.Rsi)} m²K/W, R_se = {fmt(w.Rse)} m²K/W.")
            s.append("")
            rows = []
            for x in w.warstwy:
                if x.rodzaj == "niejednorodna":
                    lam = " / ".join(f"{k}: {fmt(l, 3)}×{fmt(u * 100, 0)} %" for k, l, u in x.frakcje)
                else:
                    lam = fmt(x.lam, 3) if x.lam else "—"
                rows.append([x.lp, x.nazwa, x.funkcja, fmt(x.d * 100, 1), lam, fmt(x.R, 3) if x.rodzaj != "pominieta"
                             else "—", x.rodzaj + (f" — {x.uwagi}" if x.uwagi else "")])
            s.append(tabela_md(["Lp.", "Warstwa (od ciepłej strony)", "Funkcja", "d [cm]", "λ [W/(m·K)]", "R [m²K/W]",
                                "Uwagi"], rows, "rlllrrl"))
            s.append("")
            if w.rola == "podloga_grunt":
                s.append(f"Opór warstw podłogi R_f = Σ R_j = {fmt(w.R_f, 3)} m²K/W (bez R_si, R_se i gruntu) — U podłogi "
                         "na gruncie (U_equiv) wg PN-EN ISO 13370 — patrz 02_grunt.md.")
                s.append("")
                s.append(f"**U_equiv = {fmt_u(w.U)} W/(m²K)**; wymaganie WT: U ≤ {fmt(w.U_max) if w.U_max else '—'} "
                         f"({ok(w.spelnia_WT)}); cel: {fmt(w.U_cel) if w.U_cel else '—'} ({ok(w.spelnia_cel)}).")
                for u in w.uwagi:
                    s.append(f"* {u}")
                s.append("")
                continue
            if w.R_gorny is not None:
                s.append(f"Metoda kresów (p. 6.7.2): R'_T = {fmt(w.R_gorny, 3)}, R''_T = {fmt(w.R_dolny, 3)}, "
                         f"R_T = (R'_T + R''_T)/2 = {fmt(w.R_T, 3)} m²K/W, e = {fmt(w.blad_wzgl * 100, 1)} %.")
            else:
                s.append(f"R_T = {fmt(w.Rsi)} + Σ R_j + {fmt(w.Rse)} = {fmt(w.R_T, 3)} m²K/W; U₀ = 1/R_T = {fmt(w.U0, 4)} W/(m²K).")
            s.append("")
            s.append(f"Poprawki (zał. F): ΔU_g = {fmt(w.dU_g, 4)}, ΔU_f = {fmt(w.dU_f, 4)}, ΔU_r = {fmt(w.dU_r, 4)} W/(m²K); "
                     f"U_c = {fmt(w.U_c, 4)} W/(m²K).")
            if w.klin:
                s.append("")
                s.append(f"Warstwa klinowa: U_śr = {fmt(w.klin['U_sr'], 4)} W/(m²K) ({w.klin['metoda']}); "
                         f"U = U_śr + ΣΔU = {fmt(w.U, 4)} W/(m²K).")
            s.append("")
            s.append(f"**U = {fmt_u(w.U)} W/(m²K)**; wymaganie WT: U ≤ {fmt(w.U_max) if w.U_max else '—'} ({ok(w.spelnia_WT)}); "
                     f"cel: {fmt(w.U_cel) if w.U_cel else '—'} ({ok(w.spelnia_cel)}). Źródło wymagania: {w.wym_zrodlo or '—'}.")
            for u in w.uwagi:
                s.append(f"* {u}")
            s.append("")
    if zal:
        s.append(zal.md())
    return "\n".join(s)
