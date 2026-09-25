"""Materiały i przekroje: beton (PN-EN 1992-1-1 tabl. 3.1), stal zbrojeniowa B500SP (PN-H-93220:2018-02, zał. C EC2),
mur (PN-EN 1996-1-1 + NA, 3.6.1.2), stal konstrukcyjna (PN-EN 1993-1-1 tabl. 3.1), kształtowniki (charakterystyki liczone
numerycznie z geometrii przekroju — IPE/HEA/HEB z promieniem wyokrąglenia, rury prostokątne i okrągłe wg PN-EN 10219-2).

Charakterystyki kształtowników liczone są całkowaniem wieloboku (łuki aproksymowane ≥ 64 odcinkami na okrąg) — zgodność
z tablicami producentów ≈ 0,5 % (test: IPE 200, HEB 160, RK 120×120×6). Moment bezwładności przy skręcaniu I_t dwuteowników
— z tablic (ArcelorMittal, wyd. 2021 — wartości katalogowe), dla rur — wzory PN-EN 10219-2 zał. B.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from functools import lru_cache

from shapely.geometry import Point, Polygon, box
from shapely.geometry.polygon import orient
from shapely.ops import unary_union

from .wspolne import BladDanych, Parametry

# ==================================================================================================
# Beton
# ==================================================================================================
# klasa: (f_ck, f_ck,cube, f_cm, f_ctm, f_ctk,0.05, f_ctk,0.95, E_cm [GPa]) — PN-EN 1992-1-1 tabl. 3.1
TABL_BETON = {
    "C12/15": (12, 15, 20, 1.6, 1.1, 2.0, 27), "C16/20": (16, 20, 24, 1.9, 1.3, 2.5, 29),
    "C20/25": (20, 25, 28, 2.2, 1.5, 2.9, 30), "C25/30": (25, 30, 33, 2.6, 1.8, 3.3, 31),
    "C30/37": (30, 37, 38, 2.9, 2.0, 3.8, 33), "C35/45": (35, 45, 43, 3.2, 2.2, 4.2, 34),
    "C40/50": (40, 50, 48, 3.5, 2.5, 4.6, 35), "C45/55": (45, 55, 53, 3.8, 2.7, 4.9, 36),
    "C50/60": (50, 60, 58, 4.1, 2.9, 5.3, 37),
}


@dataclass
class Beton:
    """Beton zwykły ≤ C50/60 (PN-EN 1992-1-1 tabl. 3.1, p. 3.1.6, 3.1.7). Wytrzymałości w MPa."""
    klasa: str = "C25/30"
    gamma_c: float = 1.4
    alfa_cc: float = 1.0
    alfa_ct: float = 1.0

    def __post_init__(self):
        k = self.klasa.upper().replace(" ", "")
        if k not in TABL_BETON:
            raise BladDanych(f"nieznana klasa betonu: {self.klasa} (dostępne: {', '.join(TABL_BETON)})")
        self.klasa = k
        (self.f_ck, self.f_ck_cube, self.f_cm, self.f_ctm, self.f_ctk005, self.f_ctk095, E) = TABL_BETON[k]
        self.E_cm = E * 1000.0          # MPa
        self.eps_cu3 = 3.5e-3
        self.eps_c3 = 1.75e-3
        self.lam = 0.8                  # λ (3.19)
        self.eta = 1.0                  # η (3.21)

    @property
    def f_cd(self) -> float:
        """f_cd = α_cc·f_ck/γ_c (3.15)."""
        return self.alfa_cc * self.f_ck / self.gamma_c

    @property
    def f_ctd(self) -> float:
        """f_ctd = α_ct·f_ctk,0.05/γ_c (3.16)."""
        return self.alfa_ct * self.f_ctk005 / self.gamma_c

    @property
    def nu_1(self) -> float:
        """ν = 0,6·(1 − f_ck/250) — współczynnik redukcji wytrzymałości betonu zarysowanego przy ścinaniu (6.6N)."""
        return 0.6 * (1.0 - self.f_ck / 250.0)

    @classmethod
    def z_parametrow(cls, klasa: str, p: Parametry | None = None) -> "Beton":
        p = p or Parametry()
        return cls(klasa, gamma_c=p.gamma_c, alfa_cc=p.alfa_cc, alfa_ct=p.alfa_ct)


def klasa_betonu_z_nazwy(tekst: str | None) -> str | None:
    """Wyszukuje klasę betonu 'Cxx/yy' w nazwie/kodzie materiału (np. 'Żelbet C30/37', 'ZB_C30')."""
    if not tekst:
        return None
    m = re.search(r"C\s?(\d{2})\s?/\s?(\d{2})", tekst)
    if m:
        k = f"C{m.group(1)}/{m.group(2)}"
        return k if k in TABL_BETON else None
    m = re.search(r"C(\d{2})(?!\d)", tekst)
    if m:
        for k in TABL_BETON:
            if k.startswith(f"C{m.group(1)}/"):
                return k
    return None


# ==================================================================================================
# Stal zbrojeniowa i pręty
# ==================================================================================================
@dataclass
class StalZbrojeniowa:
    """Stal zbrojeniowa (PN-EN 1992-1-1 p. 3.2, zał. C). B500SP: f_yk = 500 MPa, klasa ciągliwości C (R5-55)."""
    gatunek: str = "B500SP"
    f_yk: float = 500.0
    gamma_s: float = 1.15
    E_s: float = 200_000.0
    klasa_ciagliwosci: str = "C"

    @property
    def f_yd(self) -> float:
        return self.f_yk / self.gamma_s

    @property
    def eps_yd(self) -> float:
        return self.f_yd / self.E_s

    def xi_eff_lim(self, beton: Beton) -> float:
        """Graniczna względna wysokość strefy ściskanej ξ_eff,lim = λ·ε_cu3/(ε_cu3 + ε_yd) (z płaskich przekrojów)."""
        return beton.lam * beton.eps_cu3 / (beton.eps_cu3 + self.eps_yd)


SREDNICE = (6, 8, 10, 12, 14, 16, 20, 25, 28, 32)
RHO_STALI = 7850.0   # kg/m³


def pole_preta(fi_mm: float) -> float:
    """Pole przekroju pręta [mm²]."""
    return math.pi * fi_mm ** 2 / 4.0


def masa_preta(fi_mm: float) -> float:
    """Masa 1 m pręta [kg/m] (ρ = 7850 kg/m³; PN-EN ISO 3766 / tabl. producentów: φ12 → 0,888)."""
    return RHO_STALI * pole_preta(fi_mm) * 1e-6


# ==================================================================================================
# Mur
# ==================================================================================================
@dataclass
class Mur:
    """Mur z elementów murowych na zaprawie (PN-EN 1996-1-1+A1 + NA, p. 3.6.1.2).

    Domyślnie: silikaty grupy 1, kat. I, klasa 20, zaprawa do cienkich spoin: f_k = K·f_b^0,85 (3.2),
    K = 0,60 (NA tabl. NA.5 po Ap2:2014-09), γ_M = 1,7 (klasa wykonania A) — R5-60…R5-62, W-270.
    """
    nazwa: str = "Silikat gr. 1, kat. I, kl. 20, zaprawa do cienkich spoin"
    f_b: float = 20.0
    K: float = 0.60
    alfa: float = 0.85
    beta: float = 0.0
    f_m: float = 10.0
    cienka_spoina: bool = True
    gamma_M: float = 1.7
    K_E: float = 1000.0
    fi_inf: float = 1.5
    ciezar: float = 18.0     # kN/m³ (orientacyjnie; w obliczeniach ciężar z ρ materiału modelu)

    @property
    def f_k(self) -> float:
        """f_k = K·f_b^α·f_m^β (3.1); dla zaprawy do cienkich spoin i elementów gr. 1: f_k = K·f_b^0,85 (3.2)."""
        if self.cienka_spoina:
            return self.K * self.f_b ** 0.85
        return self.K * self.f_b ** self.alfa * self.f_m ** self.beta

    @property
    def f_d(self) -> float:
        return self.f_k / self.gamma_M

    @property
    def E(self) -> float:
        return self.K_E * self.f_k

    @classmethod
    def z_parametrow(cls, p: Parametry | None = None, f_b: float | None = None, nazwa: str | None = None) -> "Mur":
        p = p or Parametry()
        m = cls(f_b=f_b if f_b is not None else p.mur_f_b, K=p.mur_K, gamma_M=p.mur_gamma_M, K_E=p.mur_K_E,
                fi_inf=p.mur_fi_inf)
        if nazwa:
            m.nazwa = nazwa
        return m


def klasa_muru_z_nazwy(tekst: str | None) -> float | None:
    """f_b z nazwy materiału, np. 'Bloczek wapienno-piaskowy 18 cm, kl. 20' → 20."""
    if not tekst:
        return None
    m = re.search(r"kl\.?\s*(\d{1,2})", tekst)
    return float(m.group(1)) if m else None


# ==================================================================================================
# Stal konstrukcyjna
# ==================================================================================================
TABL_STAL = {"S235": (235.0, 360.0), "S275": (275.0, 430.0), "S355": (355.0, 490.0), "S420": (420.0, 520.0),
             "S460": (460.0, 540.0)}


@dataclass
class StalKonstr:
    """Stal konstrukcyjna (PN-EN 1993-1-1 tabl. 3.1, t ≤ 40 mm): f_y, f_u [MPa]; E = 210 GPa, G = 81 GPa."""
    gatunek: str = "S355"
    E: float = 210_000.0
    G: float = 81_000.0

    def __post_init__(self):
        g = self.gatunek.upper()
        m = re.search(r"S\s?(235|275|355|420|460)", g)
        if not m:
            raise BladDanych(f"nieznany gatunek stali: {self.gatunek}")
        self.gatunek = f"S{m.group(1)}"
        self.f_y, self.f_u = TABL_STAL[self.gatunek]

    @property
    def eps(self) -> float:
        """ε = √(235/f_y) (tabl. 5.2)."""
        return math.sqrt(235.0 / self.f_y)

    @property
    def beta_w(self) -> float:
        """Współczynnik korelacji spoin pachwinowych β_w (PN-EN 1993-1-8 tabl. 4.1)."""
        return {"S235": 0.8, "S275": 0.85, "S355": 0.9}.get(self.gatunek, 1.0)


# ==================================================================================================
# Kształtowniki — geometria i charakterystyki
# ==================================================================================================
# (h, b, t_w, t_f, r) [mm], I_t [cm⁴] — wymiary wg PN-EN 10365 / katalog ArcelorMittal
TABL_I = {
    "IPE 80": (80, 46, 3.8, 5.2, 5, 0.70), "IPE 100": (100, 55, 4.1, 5.7, 7, 1.20),
    "IPE 120": (120, 64, 4.4, 6.3, 7, 1.74), "IPE 140": (140, 73, 4.7, 6.9, 7, 2.45),
    "IPE 160": (160, 82, 5.0, 7.4, 9, 3.60), "IPE 180": (180, 91, 5.3, 8.0, 9, 4.79),
    "IPE 200": (200, 100, 5.6, 8.5, 12, 6.98), "IPE 220": (220, 110, 5.9, 9.2, 12, 9.07),
    "IPE 240": (240, 120, 6.2, 9.8, 15, 12.9), "IPE 270": (270, 135, 6.6, 10.2, 15, 15.9),
    "IPE 300": (300, 150, 7.1, 10.7, 15, 20.1), "IPE 330": (330, 160, 7.5, 11.5, 18, 28.1),
    "IPE 360": (360, 170, 8.0, 12.7, 18, 37.3), "IPE 400": (400, 180, 8.6, 13.5, 21, 51.1),
    "HEA 100": (96, 100, 5.0, 8.0, 12, 5.24), "HEA 120": (114, 120, 5.0, 8.0, 12, 5.99),
    "HEA 140": (133, 140, 5.5, 8.5, 12, 8.13), "HEA 160": (152, 160, 6.0, 9.0, 15, 12.2),
    "HEA 180": (171, 180, 6.0, 9.5, 15, 14.8), "HEA 200": (190, 200, 6.5, 10.0, 18, 21.0),
    "HEA 220": (210, 220, 7.0, 11.0, 18, 28.5), "HEA 240": (230, 240, 7.5, 12.0, 21, 41.6),
    "HEA 260": (250, 260, 7.5, 12.5, 24, 52.4), "HEA 280": (270, 280, 8.0, 13.0, 24, 62.1),
    "HEA 300": (290, 300, 8.5, 14.0, 27, 85.2),
    "HEB 100": (100, 100, 6.0, 10.0, 12, 9.25), "HEB 120": (120, 120, 6.5, 11.0, 12, 13.8),
    "HEB 140": (140, 140, 7.0, 12.0, 12, 20.1), "HEB 160": (160, 160, 8.0, 13.0, 15, 31.2),
    "HEB 180": (180, 180, 8.5, 14.0, 15, 42.2), "HEB 200": (200, 200, 9.0, 15.0, 18, 59.3),
    "HEB 220": (220, 220, 9.5, 16.0, 18, 76.6), "HEB 240": (240, 240, 10.0, 17.0, 21, 103.0),
    "HEB 260": (260, 260, 10.0, 17.5, 24, 124.0), "HEB 280": (280, 280, 10.5, 18.0, 24, 144.0),
    "HEB 300": (300, 300, 11.0, 19.0, 27, 185.0),
}


@dataclass
class Przekroj:
    """Charakterystyki przekroju (jednostki: mm, mm², mm⁴, mm⁶). Oś y — silna (pozioma), z — słaba."""
    nazwa: str
    typ: str                 # I | RK | RO | PROST
    h: float
    b: float
    t_w: float = 0.0
    t_f: float = 0.0
    r: float = 0.0
    t: float = 0.0
    A: float = 0.0
    I_y: float = 0.0
    I_z: float = 0.0
    W_el_y: float = 0.0
    W_el_z: float = 0.0
    W_pl_y: float = 0.0
    W_pl_z: float = 0.0
    I_t: float = 0.0
    I_w: float = 0.0
    A_vz: float = 0.0
    A_vy: float = 0.0
    formowany_na_zimno: bool = True
    wielobok: Polygon | None = field(default=None, repr=False)

    @property
    def i_y(self) -> float:
        return math.sqrt(self.I_y / self.A)

    @property
    def i_z(self) -> float:
        return math.sqrt(self.I_z / self.A)

    @property
    def masa(self) -> float:
        """kg/m"""
        return self.A * 1e-6 * RHO_STALI

    def opis(self) -> str:
        return (f"{self.nazwa}: A = {self.A / 100:.2f} cm², I_y = {self.I_y / 1e4:.1f} cm⁴, I_z = {self.I_z / 1e4:.1f} cm⁴, "
                f"W_pl,y = {self.W_pl_y / 1e3:.1f} cm³, i_y = {self.i_y / 10:.2f} cm, i_z = {self.i_z / 10:.2f} cm, "
                f"masa {self.masa:.1f} kg/m").replace(".", ",")


def _ring_integrals(coords) -> tuple[float, float, float, float, float, float]:
    """Całki po wieloboku (wzory Greena): A, S_x=∫y, S_y=∫x, I_xx=∫y², I_yy=∫x², I_xy=∫xy (znak wg orientacji)."""
    A = Sx = Sy = Ixx = Iyy = Ixy = 0.0
    pts = list(coords)
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        c = x0 * y1 - x1 * y0
        A += c
        Sy += (x0 + x1) * c
        Sx += (y0 + y1) * c
        Iyy += (x0 * x0 + x0 * x1 + x1 * x1) * c
        Ixx += (y0 * y0 + y0 * y1 + y1 * y1) * c
        Ixy += (x0 * y1 + 2 * x0 * y0 + 2 * x1 * y1 + x1 * y0) * c
    return A / 2, Sx / 6, Sy / 6, Ixx / 12, Iyy / 12, Ixy / 24


def charakterystyki_wieloboku(g) -> dict:
    """A, środek ciężkości (xc, yc), I_y (względem osi poziomej przez środek), I_z (pionowej) — dla Polygon/MultiPolygon."""
    polys = [g] if isinstance(g, Polygon) else list(g.geoms)
    A = Sx = Sy = Ixx = Iyy = 0.0
    for p in polys:
        p = orient(p, 1.0)
        for ring in [p.exterior] + list(p.interiors):
            a, sx, sy, ixx, iyy, _ = _ring_integrals(ring.coords)
            A += a
            Sx += sx
            Sy += sy
            Ixx += ixx
            Iyy += iyy
    xc, yc = Sy / A, Sx / A
    return {"A": A, "xc": xc, "yc": yc, "I_y": Ixx - A * yc * yc, "I_z": Iyy - A * xc * xc}


def _W_pl(g, os: str) -> float:
    """Plastyczny wskaźnik wytrzymałości: suma momentów statycznych połówek pola względem osi dzielącej pole na pół."""
    c = charakterystyki_wieloboku(g)
    A = c["A"]
    minx, miny, maxx, maxy = g.bounds
    lo, hi = (miny, maxy) if os == "y" else (minx, maxx)
    for _ in range(60):                   # bisekcja osi obojętnej plastycznej
        mid = 0.5 * (lo + hi)
        part = g.intersection(box(minx - 1, mid, maxx + 1, maxy + 1) if os == "y" else box(mid, miny - 1, maxx + 1, maxy + 1))
        if part.area > A / 2:
            lo = mid
        else:
            hi = mid
    a = 0.5 * (lo + hi)
    if os == "y":
        top = g.intersection(box(minx - 1, a, maxx + 1, maxy + 1))
        bot = g.intersection(box(minx - 1, miny - 1, maxx + 1, a))
        ct, cb = charakterystyki_wieloboku(top), charakterystyki_wieloboku(bot)
        return ct["A"] * (ct["yc"] - a) + cb["A"] * (a - cb["yc"])
    rgt = g.intersection(box(a, miny - 1, maxx + 1, maxy + 1))
    lft = g.intersection(box(minx - 1, miny - 1, a, maxy + 1))
    cr, cl = charakterystyki_wieloboku(rgt), charakterystyki_wieloboku(lft)
    return cr["A"] * (cr["xc"] - a) + cl["A"] * (a - cl["xc"])


def _wypelnij(p: Przekroj, g) -> Przekroj:
    c = charakterystyki_wieloboku(g)
    p.A, p.I_y, p.I_z = c["A"], c["I_y"], c["I_z"]
    minx, miny, maxx, maxy = g.bounds
    p.W_el_y = p.I_y / max(maxy - c["yc"], c["yc"] - miny)
    p.W_el_z = p.I_z / max(maxx - c["xc"], c["xc"] - minx)
    p.W_pl_y = _W_pl(g, "y")
    p.W_pl_z = _W_pl(g, "z")
    p.wielobok = g
    return p


@lru_cache(maxsize=256)
def przekroj(nazwa: str) -> Przekroj:
    """Przekrój z nazwy: 'IPE 200', 'HEB 160', 'HEA 140', 'RK 120x120x6' (rura kwadratowa/prostokątna), 'RO 114.3x5'
    (rura okrągła), 'PROST 200x300' (przekrój pełny b×h, mm)."""
    n = nazwa.strip().upper().replace(",", ".").replace("×", "X")
    m = re.match(r"^(IPE|HEA|HEB)\s*(\d+)$", n)
    if m:
        key = f"{m.group(1)} {m.group(2)}"
        if key not in TABL_I:
            raise BladDanych(f"brak kształtownika {key} w tablicy")
        h, b, tw, tf, r, It = TABL_I[key]
        web = box(-tw / 2, -h / 2 + tf, tw / 2, h / 2 - tf)
        fl = [box(-b / 2, h / 2 - tf, b / 2, h / 2), box(-b / 2, -h / 2, b / 2, -h / 2 + tf)]
        fil = []
        for sx in (1, -1):
            for sy in (1, -1):
                cx, cy = sx * (tw / 2 + r), sy * (h / 2 - tf - r)
                sq = box(min(sx * tw / 2, cx), min(cy, sy * (h / 2 - tf)), max(sx * tw / 2, cx), max(cy, sy * (h / 2 - tf)))
                fil.append(sq.difference(Point(cx, cy).buffer(r, 64)))
        g = unary_union([web] + fl + fil)
        p = _wypelnij(Przekroj(key, "I", h, b, t_w=tw, t_f=tf, r=r, formowany_na_zimno=False), g)
        p.I_t = It * 1e4
        p.I_w = p.I_z * (h - tf) ** 2 / 4.0
        p.A_vz = max(p.A - 2 * b * tf + (tw + 2 * r) * tf, (h - 2 * tf) * tw)      # 6.2.6(3) a), η = 1,0 (bezpiecznie)
        p.A_vy = 2 * b * tf
        return p
    m = re.match(r"^(RK|RP|SHS|RHS)\s*(\d+(?:\.\d+)?)X(\d+(?:\.\d+)?)X(\d+(?:\.\d+)?)(\s*G)?$", n)
    if m:
        H, B, t = float(m.group(2)), float(m.group(3)), float(m.group(4))
        goraca = bool(m.group(5))
        ro = 1.5 * t if goraca else (2.0 * t if t <= 6 else (2.5 * t if t <= 10 else 3.0 * t))   # PN-EN 10219-2 / 10210-2
        ri = max(ro - t, 0.0)
        outer = box(-B / 2 + ro, -H / 2 + ro, B / 2 - ro, H / 2 - ro).buffer(ro, 32)
        inner = box(-B / 2 + t + ri, -H / 2 + t + ri, B / 2 - t - ri, H / 2 - t - ri).buffer(ri, 32) if ri > 0 else \
            box(-B / 2 + t, -H / 2 + t, B / 2 - t, H / 2 - t)
        g = outer.difference(inner)
        typ_n = f"RK {H:g}x{B:g}x{t:g}" + (" (gor.)" if goraca else "")
        p = _wypelnij(Przekroj(typ_n, "RK", H, B, t=t, r=ro, formowany_na_zimno=not goraca), g)
        Rc = (ro + ri) / 2                                         # PN-EN 10219-2 zał. B
        hp = 2 * ((B - t) + (H - t)) - 2 * Rc * (4 - math.pi)
        Ap = (B - t) * (H - t) - Rc ** 2 * (4 - math.pi)
        K = 2 * Ap * t / hp
        p.I_t = t ** 3 * hp / 3 + 2 * K * Ap
        p.A_vz = p.A * H / (B + H)                                 # 6.2.6(3) f)
        p.A_vy = p.A * B / (B + H)
        return p
    m = re.match(r"^(RO|CHS)\s*(\d+(?:\.\d+)?)X(\d+(?:\.\d+)?)$", n)
    if m:
        D, t = float(m.group(2)), float(m.group(3))
        g = Point(0, 0).buffer(D / 2, 64).difference(Point(0, 0).buffer(D / 2 - t, 64))
        p = _wypelnij(Przekroj(f"RO {D:g}x{t:g}", "RO", D, D, t=t), g)
        p.I_t = 2 * p.I_y
        p.A_vz = p.A_vy = 2 * p.A / math.pi
        return p
    m = re.match(r"^(PROST|P)\s*(\d+(?:\.\d+)?)X(\d+(?:\.\d+)?)$", n)
    if m:
        b, h = float(m.group(2)), float(m.group(3))
        g = box(-b / 2, -h / 2, b / 2, h / 2)
        p = _wypelnij(Przekroj(f"PROST {b:g}x{h:g}", "PROST", h, b), g)
        a, c = max(b, h), min(b, h)
        p.I_t = a * c ** 3 * (1 / 3 - 0.21 * c / a * (1 - c ** 4 / (12 * a ** 4)))
        p.A_vz = p.A_vy = p.A
        return p
    raise BladDanych(f"nie rozpoznano przekroju: {nazwa!r} (obsługiwane: IPE/HEA/HEB n, RK HxBxt, RO Dxt, PROST bxh)")
