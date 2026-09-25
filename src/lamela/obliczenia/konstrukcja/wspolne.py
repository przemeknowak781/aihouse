"""Elementy wspólne biblioteki obliczeń konstrukcyjnych: formatowanie, kroki obliczeń, wyniki, parametry projektu.

Konwencje jednostek (wewnętrznie):
* siły [kN], momenty [kNm], obciążenia powierzchniowe [kN/m²] = [kPa], liniowe [kN/m];
* długości [m] (wymiary przekrojów w wynikach również podawane w mm), pola zbrojenia w wynikach [cm²] lub [mm²/m];
* wytrzymałości materiałów [MPa] (= N/mm² = 1000 kN/m²).

Każdy wynik obliczeń (:class:`Wynik`) przechowuje listę kroków (:class:`Krok`: opis, wzór, podstawienie, wynik, jednostka,
podstawa normowa) oraz warunków stanu granicznego (:class:`Warunek`: E_d ≤ R_d → wykorzystanie η = E_d/R_d). Z tego
składany jest raport w stylu polskich „Obliczeń statycznych” (wzór → podstawienie → wynik).

Wartości domyślne :class:`Parametry` pochodzą z rejestru R5 (``docs/10_podstawy_prawne/R5_konstrukcja_obciazenia_geotechnika.md``)
i rejestru wymagań W-260…W-286 (``wymagania.yaml``, sekcje ``konstrukcja`` i ``geotechnika``). Oznaczenie [NZW] = wartość
niezweryfikowana w tekście normy (wg R5), [UPR] = uproszczenie przyjęte w bibliotece, [ZAŁ] = założenie projektowe.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, fields, asdict
from pathlib import Path
from typing import Any

G_GRAV = 9.81          # m/s² — przeliczenie gęstości [kg/m³] na ciężar [kN/m³]: γ = ρ·g/1000
MINUS = "−"


# ==================================================================================================
# Formatowanie liczb (przecinek dziesiętny — praktyka krajowa)
# ==================================================================================================
def f(x: Any, nd: int = 2) -> str:
    """Liczba z przecinkiem dziesiętnym: f(12.345) → '12,35'; f(-0.001) → '0,00'. Napisy przepuszcza bez zmian."""
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    if isinstance(x, bool):
        return "tak" if x else "nie"
    try:
        xf = float(x)
    except (TypeError, ValueError):
        return str(x)
    if math.isinf(xf):
        return "∞"
    if math.isnan(xf):
        return "—"
    s = f"{xf:.{nd}f}" if nd > 0 else f"{round(xf):d}"
    s = s.replace(".", ",")
    if s.startswith("-"):
        body = s[1:]
        if set(body) <= set("0,"):
            return body
        s = MINUS + body
    return s


def fa(x: float, nd: int = 3) -> str:
    """Liczba z automatycznym doborem miejsc (≈ 3–4 cyfry znaczące)."""
    if x is None:
        return "—"
    ax = abs(float(x))
    if ax == 0:
        return "0"
    if ax >= 100:
        return f(x, 1 if ax < 1000 else 0)
    if ax >= 10:
        return f(x, 2)
    if ax >= 1:
        return f(x, 3 if nd > 2 else nd)
    if ax >= 0.01:
        return f(x, 4 if nd > 3 else 3)
    return f(x, 5)


def proc(x: float, nd: int = 0) -> str:
    return f(100.0 * x, nd) + "%"


# ==================================================================================================
# Kroki, warunki, wyniki
# ==================================================================================================
@dataclass
class Krok:
    """Jeden krok obliczeń: ``opis: wzór = podstawienie = wynik [jedn]  (podstawa)``."""
    opis: str
    wzor: str = ""
    podst: str = ""
    wynik: Any = None
    jedn: str = ""
    nd: int = 2
    zrodlo: str = ""

    def md(self) -> str:
        parts = []
        if self.wzor:
            parts.append(self.wzor)
        if self.podst:
            parts.append(self.podst)
        if self.wynik is not None:
            w = self.wynik if isinstance(self.wynik, str) else f(self.wynik, self.nd)
            parts.append(f"**{w}**" + (f" {self.jedn}" if self.jedn else ""))
        body = " = ".join(parts)
        z = f" *({self.zrodlo})*" if self.zrodlo else ""
        return f"- {self.opis}: {body}{z}" if body else f"- {self.opis}{z}"


@dataclass
class Warunek:
    """Warunek stanu granicznego E ≤ R (E, R dodatnie). ``odwrotny=True`` → warunek R ≥ E zapisany jako E_min ≤ wartość."""
    opis: str
    E: float
    R: float
    jedn: str = ""
    zrodlo: str = ""
    nd: int = 2
    symbol_E: str = "E_d"
    symbol_R: str = "R_d"

    @property
    def eta(self) -> float:
        if self.R is None or self.E is None:
            return float("nan")
        if self.R == 0:
            return float("inf") if self.E > 0 else 0.0
        return abs(self.E) / abs(self.R)

    @property
    def ok(self) -> bool:
        return self.eta <= 1.0 + 1e-9

    def md_row(self) -> str:
        st = "spełniony" if self.ok else "**NIESPEŁNIONY**"
        return (f"| {self.opis} | {self.symbol_E} = {f(self.E, self.nd)} {self.jedn} | {self.symbol_R} = {f(self.R, self.nd)} "
                f"{self.jedn} | {f(self.eta * 100, 0)}% | {st} | {self.zrodlo} |")


@dataclass
class Wynik:
    """Bazowy wynik obliczeń (dataclass). Klasy pochodne dodają pola liczbowe."""
    nazwa: str = ""
    kroki: list = field(default_factory=list)
    warunki: list = field(default_factory=list)
    uwagi: list = field(default_factory=list)

    # ---- API ----
    def krok(self, *a, **k) -> Krok:
        kr = Krok(*a, **k)
        self.kroki.append(kr)
        return kr

    def warunek(self, *a, **k) -> Warunek:
        w = Warunek(*a, **k)
        self.warunki.append(w)
        return w

    def uwaga(self, tekst: str):
        if tekst not in self.uwagi:
            self.uwagi.append(tekst)

    @property
    def wykorzystanie(self) -> float:
        """Największe wykorzystanie nośności η = max(E_d/R_d) ze wszystkich warunków (0 — brak warunków)."""
        vals = [w.eta for w in self.warunki if w.eta == w.eta]
        return max(vals) if vals else 0.0

    @property
    def ok(self) -> bool:
        return all(w.ok for w in self.warunki)

    def dolacz(self, inny: "Wynik", prefiks: str = ""):
        """Dołącza kroki/warunki/uwagi innego wyniku (np. zginanie + ścinanie w wyniku belki)."""
        if prefiks:
            self.kroki.append(Krok(f"*{prefiks}*"))
        self.kroki.extend(inny.kroki)
        self.warunki.extend(inny.warunki)
        for u in inny.uwagi:
            self.uwaga(u)
        return inny

    def md(self, naglowek: str | None = None, poziom: int = 4) -> str:
        out = []
        if naglowek or self.nazwa:
            out.append("#" * poziom + " " + (naglowek or self.nazwa))
            out.append("")
        out += [k.md() for k in self.kroki]
        if self.warunki:
            out.append("")
            out.append(tabela_warunkow(self.warunki))
        if self.uwagi:
            out.append("")
            out += [f"> {u}" for u in self.uwagi]
        out.append("")
        return "\n".join(out)

    def dane(self) -> dict:
        """Pola liczbowe wyniku (bez kroków) — do eksportu JSON."""
        d = {}
        for fl in fields(self):
            if fl.name in ("kroki", "warunki", "uwagi"):
                continue
            v = getattr(self, fl.name)
            if isinstance(v, (int, float, str, bool)) or v is None:
                d[fl.name] = v
        d["wykorzystanie"] = round(self.wykorzystanie, 4)
        d["ok"] = self.ok
        return d


def tabela_warunkow(warunki: list[Warunek]) -> str:
    rows = ["| Warunek | Efekt | Nośność / limit | η | Stan | Podstawa |", "|---|---|---|---|---|---|"]
    rows += [w.md_row() for w in warunki]
    return "\n".join(rows)


def tabela(naglowki: list[str], wiersze: list[list], wyrownanie: str | None = None) -> str:
    """Tabela markdown; liczby formatowane f(·, 2) (krotka (x, nd) → f(x, nd))."""
    def cell(v):
        if isinstance(v, tuple) and len(v) == 2 and isinstance(v[1], int):
            return f(v[0], v[1])
        if isinstance(v, float):
            return f(v, 2)
        return str(v)
    al = wyrownanie or ("---|" * len(naglowki))
    out = ["| " + " | ".join(naglowki) + " |", "|" + al if not al.startswith("|") else al]
    for w in wiersze:
        out.append("| " + " | ".join(cell(v) for v in w) + " |")
    return "\n".join(out)


class BladDanych(ValueError):
    """Brak lub niespójność danych wejściowych obliczeń."""


# ==================================================================================================
# Grunt i parametry projektu
# ==================================================================================================
@dataclass
class Grunt:
    """Parametry warstwy nośnej podłoża (wartości charakterystyczne).

    Wartości domyślne — dane PRZYKŁADOWE z briefu (piaski średnie Ps, I_D ≈ 0,6; ZWG ≈ 3,8 m p.p.t.; R5 3.8, R5-86).
    W II kategorii geotechnicznej parametry MUSZĄ pochodzić z badań (CPT/DPL) — W-282, E-04.
    """
    nazwa: str = "Piasek średni (Ps), średnio zagęszczony, I_D ≈ 0,6 [DANE PRZYKŁADOWE]"
    fi_k: float = 33.0          # φ'_k [°] (PN-81/B-03020 rys. 3: I_D 0,5 → 33°; R5-86)
    c_k: float = 0.0            # c'_k [kPa]
    gamma: float = 18.5         # γ [kN/m³] powyżej ZWG (R5 3.8)
    gamma_sat: float = 20.0     # γ_sat [kN/m³] (γ' = γ_sat − 10)
    M0: float = 100_000.0       # edometryczny moduł ściśliwości pierwotnej M_0 [kPa] [ZAŁ — do badań]
    E: float = 80_000.0         # moduł odkształcenia E [kPa] [ZAŁ]
    nu: float = 0.25
    ZWG: float = 3.8            # głębokość zwierciadła wody gruntowej [m p.p.t.]
    humus: float = 0.4          # warstwa ziemi urodzajnej do usunięcia [m]
    wysadzinowy: bool = False
    status: str = "przykladowe"

    @property
    def gamma_prim(self) -> float:
        return self.gamma_sat - 10.0


@dataclass
class Parametry:
    """Parametry obliczeń konstrukcyjnych projektu (domyślnie: R5 + rejestr W-260…W-286).

    Nadpisanie: z sekcji ``konstrukcja`` / ``geotechnika`` modelu (propozycja R5 3.11) — :meth:`z_modelu`,
    albo z ``wymagania.yaml`` — :meth:`z_wymagan`.
    """
    # --- PN-EN 1990 + NA (W-261, W-262) ---
    gG_sup: float = 1.35
    gG_inf: float = 1.00
    xi: float = 0.85
    gQ: float = 1.50
    EQU_gG_dst: float = 1.10
    EQU_gG_stb: float = 0.90
    EQU_gQ: float = 1.50
    K_FI: float = 1.0
    klasa_konsekwencji: str = "CC2/RC2"
    psi: dict = field(default_factory=lambda: {
        "A": (0.7, 0.5, 0.3), "schody": (0.7, 0.5, 0.3), "taras": (0.7, 0.5, 0.3), "dzialowe": (0.7, 0.5, 0.3),
        "H": (0.0, 0.0, 0.0), "S": (0.5, 0.2, 0.0), "W": (0.6, 0.2, 0.0), "F": (0.7, 0.7, 0.6)})
    psi_wyjatkowa: str = "psi1"     # 6.11b: ψ1,1 albo ψ2,1 przy wiodącym zmiennym (NA — [NZW]); ψ1 bezpieczniej
    # --- PN-EN 1991-1-1 (W-263) ---
    q_strop: float = 2.0
    Q_strop: float = 3.0
    q_schody: float = 4.0
    Q_schody: float = 4.0
    q_taras: float = 4.0
    Q_taras: float = 3.0
    q_dach_H: float = 0.4
    Q_dach_H: float = 1.0
    q_garaz: float = 2.5            # kat. F (pojazdy ≤ 30 kN) — PN-EN 1991-1-1 tabl. 6.8 (2,5 kN/m², Q_k 20 kN)
    Q_garaz: float = 20.0
    ciezar_zelbetu: float = 25.0    # kN/m³ (PN-EN 1991-1-1 zał. A)
    # --- PN-EN 1991-1-3 (W-264) ---
    s_k: float = 0.9
    C_e: float = 1.0
    C_t: float = 1.0
    gamma_snieg: float = 2.0
    mu_w_min: float = 0.8
    mu_w_max: float = 4.0
    mu_attyka_max: float = 2.0
    ls_min: float = 5.0
    ls_max: float = 15.0
    snieg_B2: bool = True           # NA: przypadek B2 (wyjątkowe zaspy, zał. B) obowiązkowy
    mu_B2_max: float = 8.0
    B2_pomin_przeszkody_do_h: float = 1.0   # zał. B pkt B4(2) po AC:2009 wg IB [NZW]
    # --- PN-EN 1991-1-4 (W-265) ---
    v_b0: float = 22.0
    c_dir: float = 1.0
    c_season: float = 1.0
    rho_air: float = 1.25
    kategoria_terenu: str = "II"
    c_pi: tuple = (0.2, -0.3)
    # --- PN-EN 1992-1-1 (W-266…W-269) ---
    gamma_c: float = 1.4
    gamma_s: float = 1.15
    alfa_cc: float = 1.0            # [NZW] (NA)
    alfa_ct: float = 1.0
    klasa_konstrukcji: str = "S4"
    dc_dev: float = 10.0            # mm
    ekspozycja: dict = field(default_factory=lambda: {
        "strop": "XC1", "dach": "XC1", "wspornik": "XC4", "taras": "XC4", "belka": "XC1", "belka_zewn": "XC4",
        "wieniec": "XC1", "nadproze": "XC1", "schody": "XC1", "fundament": "XC2", "sciana_fund": "XC2"})
    beton_ekspozycja: dict = field(default_factory=lambda: {
        "X0": "C20/25", "XC1": "C25/30", "XC2": "C25/30", "XC3": "C30/37", "XC4": "C30/37"})
    stal_zbr: str = "B500SP"
    f_yk: float = 500.0
    E_s: float = 200_000.0
    fi_pelzania: float = 2.5        # φ(∞,t0) — PN-EN 1992-1-1 rys. 3.1 (RH 50 %, t0 = 28 d, h0 ≈ 200 mm) [ZAŁ]
    eps_cs: float = 0.40e-3         # odkształcenie skurczowe końcowe (3.1.4, RH 50 %, C25/30) [ZAŁ]
    ugiecie_mian: float = 250.0     # L/250 (7.4.1(4))
    ugiecie_przyrost_mian: float = 500.0
    wspornik_L_mnoznik: float = 2.0  # L = 2·wysięg (R5-56, W-268)
    w_max: dict = field(default_factory=lambda: {"X0": 0.4, "XC1": 0.4, "XC2": 0.3, "XC3": 0.3, "XC4": 0.3})
    fi_kruszywa: float = 16.0       # d_g [mm]
    # --- PN-EN 1996-1-1 (W-270) ---
    mur_K: float = 0.60
    mur_f_b: float = 20.0
    mur_alfa: float = 0.85
    mur_gamma_M: float = 1.7
    mur_K_E: float = 1000.0         # E = K_E·f_k [NZW — NA]
    mur_fi_inf: float = 1.5         # końcowy współczynnik pełzania muru silikatowego (tabl. 3.3) [NZW]
    mur_f_xk1: float = 0.20         # MPa [NZW — NA tabl.; DWU]
    mur_f_xk2: float = 0.40         # MPa [NZW]
    mur_lambda_c: float = 15.0      # smukłość, poniżej której e_k = 0 (6.1.2.2(2)) [NZW]
    # --- PN-EN 1993-1-1 (W-271) ---
    gM0: float = 1.0
    gM1: float = 1.0
    gM2: float = 1.25
    stal_konstr: str = "S355"
    # --- PN-EN 1997-1 (W-280…W-284) ---
    gR_v: float = 1.4
    gR_h: float = 1.1
    kategoria_geotechniczna: int = 2
    h_z: float = 0.8
    D_min_zewn: float = 1.0
    D_min_wewn: float = 0.5
    s_max_mm: float = 50.0
    grunt: Grunt = field(default_factory=Grunt)
    teren_domyslny: float = -0.30   # rzędna terenu przy budynku, gdy brak punktów terenu [m] [ZAŁ]
    # --- analiza ---
    siatka_mes: float = 0.20        # bok elementu płytowego MES [m]
    nu_beton: float = 0.2
    zrodla: dict = field(default_factory=dict)   # nazwa pola → źródło nadpisania

    # ------------------------------------------------------------------------------------------
    def psi_of(self, kat: str) -> tuple:
        return self.psi.get(kat, self.psi["A"])

    @property
    def f_yd(self) -> float:
        return self.f_yk / self.gamma_s

    def beton_dla(self, rola: str) -> tuple[str, str]:
        """(klasa ekspozycji, klasa betonu) dla roli elementu (strop, dach, wspornik, fundament, …)."""
        ex = self.ekspozycja.get(rola, "XC1")
        return ex, self.beton_ekspozycja.get(ex, "C25/30")

    # ---- wczytywanie nadpisań ----
    def _ustaw(self, nazwa: str, wartosc, zrodlo: str):
        if not hasattr(self, nazwa):
            return
        cur = getattr(self, nazwa)
        try:
            if isinstance(cur, float):
                wartosc = float(wartosc)
            elif isinstance(cur, int) and not isinstance(cur, bool):
                wartosc = int(wartosc)
        except (TypeError, ValueError):
            return
        setattr(self, nazwa, wartosc)
        self.zrodla[nazwa] = zrodlo

    @classmethod
    def z_wymagan(cls, sciezka: str | Path | None = None) -> "Parametry":
        """Parametry z ``docs/10_podstawy_prawne/wymagania.yaml`` (sekcje ``konstrukcja``, ``geotechnika``)."""
        import yaml
        p = cls()
        if sciezka is None:
            sciezka = Path(__file__).resolve().parents[4] / "docs" / "10_podstawy_prawne" / "wymagania.yaml"
        sciezka = Path(sciezka)
        if not sciezka.exists():
            return p
        raw = yaml.safe_load(sciezka.read_text(encoding="utf-8")) or {}
        kon = raw.get("konstrukcja") or {}
        geo = raw.get("geotechnika") or {}
        mapa = {"gamma_G_sup": "gG_sup", "xi": "xi", "gamma_G_inf": "gG_inf", "gamma_Q": "gQ",
                "EQU_gamma_G_dst": "EQU_gG_dst", "EQU_gamma_G_stb": "EQU_gG_stb", "K_FI": "K_FI",
                "q_k_strop": "q_strop", "Q_k_strop": "Q_strop", "q_k_schody": "q_schody", "Q_k_schody": "Q_schody",
                "q_k_dach_H": "q_dach_H", "Q_k_dach_H": "Q_dach_H", "ciezar_zelbetu": "ciezar_zelbetu",
                "s_k": "s_k", "C_e": "C_e", "C_t": "C_t", "gamma_snieg": "gamma_snieg", "mu_B2_max": "mu_B2_max",
                "v_b0": "v_b0", "c_dir": "c_dir", "gamma_c": "gamma_c", "gamma_s": "gamma_s", "dc_dev": "dc_dev",
                "ugiecie_mianownik": "ugiecie_mian", "ugiecie_przyrost_mianownik": "ugiecie_przyrost_mian",
                "wspornik_L_wspolczynnik": "wspornik_L_mnoznik", "f_yk": "f_yk", "mur_K": "mur_K",
                "mur_gamma_M_A": "mur_gamma_M", "stal_gamma_M0": "gM0", "stal_gamma_M2": "gM2"}
        for k, pole in mapa.items():
            v = kon.get(k)
            if isinstance(v, dict) and "wartosc" in v:
                p._ustaw(pole, v["wartosc"], f"wymagania.yaml: konstrukcja.{k} ({v.get('id', '')})")
        for k, (a, b) in {"mu_2_attyka_zakres": ("mu_w_min", "mu_attyka_max"),
                          "mu_w_uskok_zakres": ("mu_w_min", "mu_w_max"),
                          "l_s_zaspy_zakres": ("ls_min", "ls_max")}.items():
            v = kon.get(k)
            if isinstance(v, dict) and isinstance(v.get("wartosc"), list) and len(v["wartosc"]) == 2:
                p._ustaw(a, v["wartosc"][0], f"wymagania.yaml: konstrukcja.{k}")
                p._ustaw(b, v["wartosc"][1], f"wymagania.yaml: konstrukcja.{k}")
        for k, kat in (("psi_kat_A", "A"), ("psi_dach_H", "H"), ("psi_snieg", "S"), ("psi_wiatr", "W")):
            v = kon.get(k)
            if isinstance(v, dict) and isinstance(v.get("wartosc"), list) and len(v["wartosc"]) == 3:
                p.psi[kat] = tuple(float(x) for x in v["wartosc"])
                if kat == "A":
                    for kk in ("schody", "taras", "dzialowe"):
                        p.psi[kk] = p.psi["A"]
        gmap = {"gamma_R_v": "gR_v", "gamma_R_h": "gR_h", "osiadanie_max": "s_max_mm", "h_z": "h_z",
                "posadowienie_zewn_min": "D_min_zewn", "posadowienie_wewn_min": "D_min_wewn",
                "kategoria_geotechniczna": "kategoria_geotechniczna"}
        for k, pole in gmap.items():
            v = geo.get(k)
            if isinstance(v, dict) and "wartosc" in v:
                p._ustaw(pole, v["wartosc"], f"wymagania.yaml: geotechnika.{k} ({v.get('id', '')})")
        for k, pole in (("humus_do_usuniecia", "humus"), ("ZWG_ppt", "ZWG")):
            v = geo.get(k)
            if isinstance(v, dict) and "wartosc" in v:
                setattr(p.grunt, pole, float(v["wartosc"]))
        return p

    def z_modelu(self, raw_budynek: dict) -> "Parametry":
        """Nadpisania z sekcji ``konstrukcja`` / ``geotechnika`` modelu (format propozycji R5 3.11)."""
        kon = (raw_budynek or {}).get("konstrukcja") or {}
        geo = (raw_budynek or {}).get("geotechnika") or kon.get("geotechnika") or {}
        src = "model: konstrukcja"
        kb = kon.get("kombinacje") or {}
        for k, pole in (("gG_sup", "gG_sup"), ("gG_inf", "gG_inf"), ("xi", "xi"), ("gQ", "gQ")):
            if k in kb:
                self._ustaw(pole, kb[k], src)
        sn = kon.get("snieg") or {}
        for k, pole in (("s_k", "s_k"), ("C_e", "C_e"), ("C_t", "C_t"), ("gamma_sniegu", "gamma_snieg"),
                        ("mu_w_max", "mu_w_max")):
            if k in sn:
                self._ustaw(pole, sn[k], src)
        if "przypadki" in sn:
            self.snieg_B2 = "B2" in (sn.get("przypadki") or [])
        wi = kon.get("wiatr") or {}
        for k, pole in (("v_b0", "v_b0"), ("c_dir", "c_dir")):
            if k in wi:
                self._ustaw(pole, wi[k], src)
        if "kategoria_terenu_obwiednia" in wi:
            self.kategoria_terenu = str(wi["kategoria_terenu_obwiednia"])
        uz = kon.get("uzytkowe") or {}
        for k, (a, b) in {"strop_A": ("q_strop", "Q_strop"), "schody_A": ("q_schody", "Q_schody"),
                          "taras_A": ("q_taras", "Q_taras"), "dach_H": ("q_dach_H", "Q_dach_H")}.items():
            if isinstance(uz.get(k), list) and len(uz[k]) == 2:
                self._ustaw(a, uz[k][0], src)
                self._ustaw(b, uz[k][1], src)
        bt = kon.get("beton") or {}
        for k, pole in (("gamma_c", "gamma_c"), ("gamma_s", "gamma_s")):
            if k in bt:
                self._ustaw(pole, bt[k], src)
        for ex in ("XC1", "XC2", "XC3", "XC4"):
            v = bt.get(ex) or (bt.get("XC4_XF1") if ex == "XC4" else None)
            if isinstance(v, dict) and v.get("klasa"):
                self.beton_ekspozycja[ex] = str(v["klasa"])
        if isinstance(kon.get("ekspozycja"), dict):
            self.ekspozycja.update({str(k): str(v) for k, v in kon["ekspozycja"].items()})
        sz = kon.get("stal_zbrojeniowa") or {}
        if "f_yk" in sz:
            self._ustaw("f_yk", sz["f_yk"], src)
        mu = kon.get("mur") or {}
        for k, pole in (("K", "mur_K"), ("gamma_M", "mur_gamma_M"), ("f_b", "mur_f_b")):
            if k in mu:
                self._ustaw(pole, mu[k], src)
        sk = kon.get("stal_konstrukcyjna") or {}
        for k, pole in (("gamma_M0", "gM0"), ("gamma_M1", "gM1")):
            if k in sk:
                self._ustaw(pole, sk[k], src)
        if sk.get("gatunek"):
            self.stal_konstr = str(sk["gatunek"])
        for k, pole in (("gR_v", "gR_v"), ("gR_h", "gR_h"), ("h_z", "h_z"), ("D_min_zewn", "D_min_zewn"),
                        ("D_min_wewn", "D_min_wewn"), ("s_max_mm", "s_max_mm")):
            if k in geo:
                self._ustaw(pole, geo[k], "model: geotechnika")
        gr = geo.get("grunt") if isinstance(geo.get("grunt"), dict) else None
        if gr:
            for k in ("nazwa", "fi_k", "c_k", "gamma", "gamma_sat", "M0", "E", "nu", "ZWG", "humus", "status"):
                if k in gr:
                    cur = getattr(self.grunt, k)
                    setattr(self.grunt, k, type(cur)(gr[k]) if not isinstance(cur, str) else str(gr[k]))
            if "wysadzinowy" in gr:
                self.grunt.wysadzinowy = bool(gr["wysadzinowy"])
        return self

    def opis_md(self) -> str:
        """Tabela przyjętych parametrów (rozdział „Założenia” raportu)."""
        d = asdict(self)
        rows = []
        for k, v in d.items():
            if k in ("zrodla", "psi", "ekspozycja", "beton_ekspozycja", "w_max", "grunt"):
                continue
            rows.append([k, v if not isinstance(v, float) else f(v, 3), self.zrodla.get(k, "R5 / rejestr W-26x (domyślnie)")])
        return tabela(["Parametr", "Wartość", "Źródło"], rows)
