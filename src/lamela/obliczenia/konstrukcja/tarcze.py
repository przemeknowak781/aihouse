"""Ściany-tarcze żelbetowe — belki-ściany, tarcze wspornikowe, tarcze z otworami (PN-EN 1992-1-1:2008 + NA).

Procedura (pozycja „Obliczeń statycznych”):

1. **MES tarczy** (:mod:`.tarcze_mes`, element QM6, płaski stan naprężenia, beton niezarysowany E_cm, ν = 0,2):
   obrys z otworami, podpory liniowe/punktowe (sztywne lub sprężyste — ściany poniżej: k = E·t/h), obciążenia
   (ciężar własny, liniowe od stropów na poziomie stropu/wieńca, profile reakcji płyt, skupione); kombinacje z
   :func:`.obciazenia.kombinacje` (STR 6.10a/b z G korzystnym, SLS charakterystyczna i quasi-stała, wyjątkowa 6.11b).
   Wyniki: mapy σ_x, σ_z, τ_xz, naprężenia główne i ich kierunki (trajektorie), reakcje podpór (rozkład → bilans
   ścieżki obciążeń), wypadkowe stref rozciąganych przy krawędziach (całkowanie σ w przekrojach — pasy tarczy,
   nadproża i podokienniki), siły w przekrojach (kontrola równowagi).
2. **Model kratownicowy STM** (5.6.4, 6.5) generowany z wyników MES: węzły na liniach pasów — odsunięcie od krawędzi
   = środek bloku naprężeń z MES (ograniczony do [a_s; 0,15·h_pasma]), wspólne linie pasów w sąsiednich pasmach,
   kolumny przy krawędziach otworów, podporach i siłach skupionych; pręty kandydujące (ground structure) wewnątrz
   betonu; siły prętów z programowania liniowego (Dorn–Gomory–Greenberg 1964): min Σ c_i·|F_i|·l_i przy równowadze
   węzłów, z kosztem cięgien 1,0 i krzyżulców r_c = 0,3 (kryterium „minimum zbrojenia”, Schlaich i in. 1987)
   powiększonym, gdy kierunek pręta przeczy znakowi naprężenia sprężystego σ_ee z MES (EC2 5.6.4(5): trajektorie
   naprężeń z analizy liniowo-sprężystej). Obciążenia i reakcje z MES przeniesione na węzły STM z zachowaniem
   wypadkowej i momentu (dokładna równowaga). Model wyznaczany dla każdej kombinacji STR (obwiednia).
3. **Wymiarowanie**: krzyżulce σ ≤ 0,6·ν'·f_cd (6.56), węzły CCC/CCT/CTT k·ν'·f_cd, k = 1,0/0,85/0,75 (6.60–6.62),
   docisk na podporach; cięgna A_s = F_t/f_yd (6.5.3) z F_t = max(STM; wypadkowa rozciągania z MES), zakotwienie
   (8.4 — z uwzględnieniem warunków przyczepności górnych prętów), zbrojenie minimalne ze względu na rysy (7.3.2),
   siatki przy obu powierzchniach: ściany 9.6.2/9.6.3 i belki-ściany 9.7 (≥ 0,1 % i 150 mm²/m na powierzchnię,
   s ≤ min(2t; 300 mm)), zbrojenie z pola naprężeń wg zał. F (sprawdzenie uzupełniające), otwory — pręty ukośne
   w narożach (siła rozciągająca w przekroju wzdłuż dwusiecznej naroża z MES) i obwodowe, rysy w_k (7.3.4) pasów,
   ugięcie wspornika/przęseł (SLS quasi-stała, E_c,eff z pełzaniem, sztywność zarysowana — :func:`.tarcze_mes.D_zarysowany`),
   równowaga statyczna EQU wspornika (PN-EN 1990 tabl. A1.2(A): 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb), reakcje na
   ściany/wieńce poniżej (charakterystyczne, wg przypadków — do bilansu ścieżki obciążeń).

Źródła (literatura — przytaczana z pamięci autora, oznaczona [P]; wzory normowe sprawdzone z treścią PN-EN 1992-1-1
w zakresie cytowanym w bibliotece ``zelbet``):
* PN-EN 1992-1-1:2008 p. 5.6.4, 6.5.1–6.5.4, 7.3, 7.4, 8.4, 9.6, 9.7, zał. F [NZW — wartości zalecane NA];
* J. Schlaich, K. Schäfer, M. Jennewein, *Toward a Consistent Design of Structural Concrete*, PCI Journal 32(3),
  1987 — metoda ścieżek obciążeń, orientacja STM wg pola sprężystego, kryterium minimum energii cięgien [P];
* fib Bulletin 45 *Practitioners' guide to finite element modelling of reinforced concrete structures* (2008) oraz
  fib Bulletin 61 *Design examples for strut-and-tie models* (2011); fib Model Code 2010, §7.3 (pola naprężeń) [P];
* F. Leonhardt, E. Mönnig, *Vorlesungen über Massivbau*, T. 2, Springer 1975; F. Leonhardt, R. Walther,
  *Wandartige Träger*, DAfStb Heft 178, 1966; DAfStb Heft 240 (Grasser, Thielen, 1991) — ramię sił wewnętrznych
  belek-ścian z = 0,3·h·(3 − h/l) dla 0,5 ≤ h/l < 1 i z = 0,6·l dla h/l ≥ 1 (zgodne z CEB-FIP: 0,2·(l + 2h)) [P];
* W.S. Dorn, R.E. Gomory, H.J. Greenberg, *Automatic design of optimal structures*, J. de Mécanique 3 (1964) [P];
* A. Muttoni, J. Schwartz, B. Thürlimann, *Design of Concrete Structures with Stress Fields*, Birkhäuser 1997 [P];
* J. Kobiak, W. Stachurski, *Konstrukcje żelbetowe*, t. 2 (tarcze — tablice Leonhardta) [P].

Ograniczenia: patrz :data:`OGRANICZENIA_TARCZ`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import shapely
from scipy import sparse
from scipy.optimize import linprog
from shapely.geometry import LineString, Point, Polygon, box

from . import zelbet
from .materialy import Beton, StalZbrojeniowa, pole_preta
from .obciazenia import Kombinacja, Oddz, kombinacje
from .tarcze_mes import (D_izo, D_zarysowany, ObcLiniowe, ObcProfil, ObcSkupione, PodporaT, TarczaMES, WynikT,
                         blok_przy_krawedzi, glowne, wypadkowa_rozciagania)
from .wspolne import BladDanych, Krok, Parametry, Warunek, Wynik, f, tabela

K_WEZLA = {"CCC": 1.0, "CCT": 0.85, "CTT": 0.75}      # 6.5.4(4) — wartości zalecane [NZW NA]
R_C = 0.3          # koszt krzyżulca względem cięgna w LP (kryterium minimum zbrojenia)
BETA_MES = 2.0     # kara za niezgodność pręta z polem sprężystym MES

OGRANICZENIA_TARCZ = [
    "analiza liniowo-sprężysta tarczy niezarysowanej (ULS: STM jako rozwiązanie dolne z obciążeniami i reakcjami z MES; "
    "redystrybucja reakcji po zarysowaniu — nieuwzględniona; SLS: sztywność zarysowana rysami rozmytymi [UPR])",
    "obrys prostokątny lub schodkowy (siatka ortogonalna), otwory prostokątne; zginanie z płaszczyzny, wyboczenie "
    "i stateczność boczna strefy ściskanej nie są sprawdzane (tarcza stężona stropami — [ZAŁ])",
    "półki stropów współpracujące z tarczą — tylko gdy podane jako strefy o innej grubości",
    "STM: węzły wewnętrzne — szerokość krzyżulca przyjmowana jako rozstaw węzłów siatki [UPR]; krzyżulce sprawdzane "
    "na 0,6·ν'·f_cd (strefa zarysowana, bezpiecznie)",
    "ścinanie w styku roboczym (6.2.5), docisk w ścianie poniżej — w pozycji ściany/wieńca poniżej",
    "zbrojenie z pola naprężeń (zał. F) — sprawdzenie uzupełniające; osobliwości w narożach otworów pokrywają pręty ukośne",
]


# ==================================================================================================
# Dane wejściowe
# ==================================================================================================
@dataclass
class OtworT:
    """Otwór prostokątny w tarczy: s0…s1 wzdłuż ściany, z0…z1 w pionie (układ lokalny tarczy)."""
    id: str
    s0: float
    s1: float
    z0: float
    z1: float

    @property
    def szer(self) -> float:
        return self.s1 - self.s0

    @property
    def wys(self) -> float:
        return self.z1 - self.z0


@dataclass
class DaneTarczy:
    """Dane tarczy. Układ lokalny: x wzdłuż ściany (x0…x0 + L), z w górę (z0…z0 + H). przypadki — {nazwa: Oddz}
    (rodzaj G/Q/A, kategoria ψ, grupa wykluczeń); ciężar własny tarczy należy do przypadku ``przypadek_cw``."""
    id: str
    L: float
    H: float
    t: float
    x0: float = 0.0
    z0: float = 0.0
    otwory: list = field(default_factory=list)
    podpory: list = field(default_factory=list)
    obciazenia: list = field(default_factory=list)
    przypadki: dict = field(default_factory=dict)
    beton: str = "C30/37"
    ekspozycja: str = "XC3"
    gamma: float = 25.0
    g_dod: float = 0.0
    przypadek_cw: str = "G"
    obrys: Polygon | None = None
    strefy: list = field(default_factory=list)
    opis: str = ""
    kierunki: tuple = ("zachód", "wschód")      # nazwy kierunków −x / +x (opisy wsporników)
    fi_podpor: float = 0.0                     # pełzanie podpór sprężystych (mur ≈ 1,5) — SLS długotrwałe
    fi_siatki: int = 8
    fi_otwory: int = 12

    def polygon(self) -> Polygon:
        P = self.obrys if self.obrys is not None else box(self.x0, self.z0, self.x0 + self.L, self.z0 + self.H)
        for o in self.otwory:
            P = P.difference(box(o.s0, o.z0, o.s1, o.z1))
        if not isinstance(P, Polygon):
            raise BladDanych(f"Tarcza {self.id}: otwory dzielą tarczę na części — obrys niespójny")
        return P


# ==================================================================================================
# Wyniki
# ==================================================================================================
@dataclass
class Pas:
    """Cięgno (pas rozciągany) — grupa cięgien STM przy jednej krawędzi lub strefa zbrojenia."""
    klucz: str
    opis: str
    kierunek: str                 # h | v | d | w (siatka/środnik)
    krawedz: object = None
    F_stm: float = 0.0
    k_stm: str = ""
    F_mes: float = 0.0
    k_mes: str = ""
    x_mes: float = 0.0
    F_qp: float = 0.0             # wypadkowa rozciągania z MES — SLS quasi-stała
    zakres: tuple = (0.0, 0.0)
    a: float = 0.06               # odległość osi cięgna od krawędzi [m]
    h_t: float = 0.0              # wysokość strefy rozciąganej z MES [m]
    k_c: float = 0.4
    konce: list = field(default_factory=list)   # [(x, z, F, kierunek (+1/−1))]
    As_req: float = 0.0
    As_min: float = 0.0
    n: int = 0
    fi: int = 0
    As_prov: float = 0.0
    zakotwienie: list = field(default_factory=list)
    w_k: float = 0.0
    sigma_s: float = 0.0

    @property
    def F_Ed(self) -> float:
        return max(self.F_stm, self.F_mes)


@dataclass
class Krawedz:
    id: str
    opis: str
    typ: str            # h | v
    wsp: float          # z (h) lub x (v)
    a: float
    b: float
    strona: int         # +1: beton nad (h) / na prawo (v); −1: pod / na lewo
    otwor: str | None = None


@dataclass
class ModelSTM:
    wezly: np.ndarray
    ii: np.ndarray
    jj: np.ndarray
    L: np.ndarray
    U: np.ndarray
    info: list
    sbar: np.ndarray
    Wz: object = None
    Wx: object = None
    P: dict = field(default_factory=dict)       # kombinacja → obciążenia węzłów [n × 2]
    Rw: dict = field(default_factory=dict)      # kombinacja → reakcje podpór w węzłach [n × 2]
    F: dict = field(default_factory=dict)       # kombinacja → siły prętów
    luz: dict = field(default_factory=dict)     # kombinacja → maks. niezrównoważenie [kN]
    l_docisku: np.ndarray | None = None


@dataclass
class WynikTarczy(Wynik):
    """Wynik obliczeń tarczy (pola liczbowe; obiekty analizy w atrybucie ``an``)."""
    L: float = 0.0
    H: float = 0.0
    t: float = 0.0
    beton: str = ""
    n_elementow: int = 0
    kombinacja_miarodajna: str = ""
    sigma1_max: float = 0.0       # MPa (ULS)
    sigma2_min: float = 0.0       # MPa (ULS)
    T_max: float = 0.0            # kN — największa siła w cięgnie (F_Ed)
    C_max: float = 0.0            # kN — największa siła w krzyżulcu
    w_max: float = 0.0            # mm — miarodajne ugięcie SLS (wspornik lub przęsło)
    w_dop: float = 0.0
    eta_EQU: float = 0.0
    masa_stali: float = 0.0       # kg
    sum_R: float = 0.0            # ΣR ULS miarodajna [kN]
    blad_rownowagi: float = 0.0   # względny błąd ΣF_z (MES)


# ==================================================================================================
# Geometria pomocnicza
# ==================================================================================================
def krawedzie(P: Polygon, otwory: list[OtworT]) -> list[Krawedz]:
    """Krawędzie poziome i pionowe obrysu i otworów z nazwami (pasy, nadproża, podokienniki, ościeża)."""
    out = []
    Pb = P.buffer(0)
    lic = {"dol": 0, "gora": 0, "lewy": 0, "prawy": 0}

    def otw_dla(ring):
        x0, z0, x1, z1 = Polygon(ring).bounds
        for o in otwory:
            if abs(o.s0 - x0) < 1e-6 and abs(o.s1 - x1) < 1e-6 and abs(o.z0 - z0) < 1e-6 and abs(o.z1 - z1) < 1e-6:
                return o.id
        return None
    for k, ring in enumerate([P.exterior] + list(P.interiors)):
        oid = None if k == 0 else otw_dla(ring)
        c = list(ring.coords)
        for (x0, z0), (x1, z1) in zip(c[:-1], c[1:]):
            if abs(z0 - z1) < 1e-9 and abs(x1 - x0) > 1e-9:
                a, b = min(x0, x1), max(x0, x1)
                up = Pb.contains(Point(0.5 * (a + b), z0 + 1e-4))
                if oid:
                    opis = f"nad otworem {oid}" if up else f"pod otworem {oid}"
                else:
                    kk = "dol" if up else "gora"
                    lic[kk] += 1
                    opis = ("krawędź dolna" if up else "krawędź górna")
                out.append(Krawedz("", opis, "h", z0, a, b, 1 if up else -1, oid))
            elif abs(x0 - x1) < 1e-9 and abs(z1 - z0) > 1e-9:
                a, b = min(z0, z1), max(z0, z1)
                right = Pb.contains(Point(x0 + 1e-4, 0.5 * (a + b)))
                if oid:
                    opis = f"ościeże {'prawe' if right else 'lewe'} otworu {oid}"
                else:
                    opis = f"koniec {'lewy' if right else 'prawy'} tarczy (x = {f(x0, 2)})"
                out.append(Krawedz("", opis, "v", x0, a, b, 1 if right else -1, oid))
    # nazwy jednoznaczne (np. kilka odcinków krawędzi dolnej)
    cnt: dict = {}
    for e in out:
        cnt[e.opis] = cnt.get(e.opis, 0) + 1
    seen: dict = {}
    for e in out:
        if cnt[e.opis] > 1:
            seen[e.opis] = seen.get(e.opis, 0) + 1
            e.opis = f"{e.opis} ({f(e.a, 2)}…{f(e.b, 2)} m)"
        e.id = e.opis
    return out


def _pasma(P: Polygon, kraw: list[Krawedz]):
    """Pasma pionowe między liniami x krawędzi pionowych: [(xa, xb, [[za, zb], …])] — przedziały pełne."""
    XL = sorted({round(e.wsp, 6) for e in kraw if e.typ == "v"})
    ZL = sorted({round(e.wsp, 6) for e in kraw if e.typ == "h"})
    out = []
    for xa, xb in zip(XL[:-1], XL[1:]):
        xm = 0.5 * (xa + xb)
        ints = []
        for za, zb in zip(ZL[:-1], ZL[1:]):
            if P.contains(Point(xm, 0.5 * (za + zb))):
                if ints and abs(ints[-1][1] - za) < 1e-9:
                    ints[-1][1] = zb
                else:
                    ints.append([za, zb])
        out.append((xa, xb, ints))
    return out


def _dl_promienia(P: Polygon, p, kier) -> float:
    """Długość odcinka od punktu p w kierunku kier do brzegu betonu [m]."""
    p = np.asarray(p, float)
    d = np.asarray(kier, float) / np.hypot(*kier)
    ln = LineString([tuple(p), tuple(p + 50 * d)])
    pts = []
    for ring in [P.exterior] + list(P.interiors):
        g = ln.intersection(ring)
        if g.is_empty:
            continue
        geoms = [g] if g.geom_type == "Point" else list(getattr(g, "geoms", []))
        for q in geoms:
            if q.geom_type == "Point":
                pts.append(np.hypot(q.x - p[0], q.y - p[1]))
            elif q.geom_type == "LineString":
                for c in q.coords:
                    pts.append(np.hypot(c[0] - p[0], c[1] - p[1]))
    pts = [v for v in pts if v > 1e-6]
    return min(pts) if pts else 0.0


# ==================================================================================================
# Analiza
# ==================================================================================================
class AnalizaTarczy:
    """Pełne obliczenia tarczy: MES (ULS/SLS), STM, wymiarowanie, SLS, EQU. Użycie: ``AnalizaTarczy(dane).uruchom()``."""

    def __init__(self, dane: DaneTarczy, p: Parametry | None = None, stal: StalZbrojeniowa | None = None,
                 siatka: float = 0.10, dx_stm: float = 0.75, dz_stm: float = 0.80):
        self.d = dane
        self.p = p or Parametry()
        self.stal = stal or StalZbrojeniowa(f_yk=self.p.f_yk, gamma_s=self.p.gamma_s, E_s=self.p.E_s)
        self.beton = Beton.z_parametrow(dane.beton, self.p)
        self.siatka = siatka
        self.dx_stm, self.dz_stm = dx_stm, dz_stm
        self.uwagi: list[str] = []
        self.sekcje: list[Wynik] = []
        self.tabele: list[str] = []
        self.przyjeto: list[str] = []
        self.prety: list = []
        self.pasy: list[Pas] = []
        self.rys: list = []
        self.P = dane.polygon()
        self.kraw = krawedzie(self.P, dane.otwory)
        ot = zelbet.otulina(dane.ekspozycja, max(dane.fi_otwory, 12), self.p)
        self.c_nom = ot.c_nom / 1000.0            # m
        self.a_s = self.c_nom + dane.fi_siatki / 1000 + 0.008     # oś pręta φ16 za siatką [m]
        if dane.przypadek_cw not in dane.przypadki:
            dane.przypadki[dane.przypadek_cw] = Oddz(dane.przypadek_cw, "G")
        brak = sorted({o.przypadek for o in dane.obciazenia} - set(dane.przypadki))
        if brak:
            raise BladDanych(f"Tarcza {dane.id}: brak definicji przypadków obciążeń {brak} (DaneTarczy.przypadki)")

    # ---------------------------------------------------------------------------------------------
    def uruchom(self, stm: bool = True, sls: bool = True) -> "AnalizaTarczy":
        self._mes()
        self._kombinacje_i_rozwiazania()
        self._reakcje_przypadki()
        self._rownowaga()
        self._pasy_mes()
        if stm:
            self._stm()
        self._siatki()
        self._ciegna()
        self._zal_F_kontrola()
        if stm:
            self._krzyzulce_wezly()
        self._otwory()
        if sls:
            self._sls()
        self._equ()
        self._zestawienie_stali()
        return self

    # ---------------------------------------------------------------------------------------------
    # 1. MES
    # ---------------------------------------------------------------------------------------------
    def _mes(self):
        d, p = self.d, self.p
        self.mes = TarczaMES(self.P, d.t, self.beton.E_cm * 1000, nu=p.nu_beton, gamma=d.gamma, g_dod=d.g_dod,
                             podpory=d.podpory, obciazenia=d.obciazenia, siatka=self.siatka, strefy=d.strefy,
                             przypadek_cw=d.przypadek_cw)
        for u in self.mes.uwagi:
            self._uwaga(u)

    def _uwaga(self, t: str):
        if t not in self.uwagi:
            self.uwagi.append(t)

    def _kombinacje_i_rozwiazania(self):
        d, p = self.d, self.p
        odz = list(d.przypadki.values())
        uzyte = set(self.mes.przypadki())
        odz = [o for o in odz if o.nazwa in uzyte]
        self.odz = odz
        self.k_uls = kombinacje(odz, p, "STR", G_korzystne=True)
        self.k_char = kombinacje(odz, p, "char")
        self.k_qp = kombinacje(odz, p, "quasi")
        self.k_wyj = kombinacje(odz, p, "wyj") if any(o.rodzaj == "A" for o in odz) else []
        self.r_uls = {k.nazwa: self.mes.rozwiaz_kombinacje(k.wsp, k.nazwa) for k in self.k_uls + self.k_wyj}
        self.r_char = {k.nazwa: self.mes.rozwiaz_kombinacje(k.wsp, k.nazwa) for k in self.k_char}
        self.r_qp = {k.nazwa: self.mes.rozwiaz_kombinacje(k.wsp, k.nazwa) for k in self.k_qp}
        self.kmap = {k.nazwa: k for k in self.k_uls + self.k_wyj + self.k_char + self.k_qp}

        def tot(r):
            return float(-r.f[1::2].sum())
        self.k_gov = max(self.r_uls, key=lambda n: tot(self.r_uls[n]) if not n.startswith("6.11") else -1)
        self.k_char_gov = max(self.r_char, key=lambda n: tot(self.r_char[n]))
        self.k_qp_gov = max(self.r_qp, key=lambda n: tot(self.r_qp[n]))
        # obwiednia naprężeń ULS
        s1 = np.max([glowne(r.sig)[0] for r in self.r_uls.values()], axis=0)
        s2 = np.min([glowne(r.sig)[1] for r in self.r_uls.values()], axis=0)
        self.s1_env, self.s2_env = s1, s2

    def _reakcje_przypadki(self):
        """Reakcje charakterystyczne wg przypadków — bilans ścieżki obciążeń. Podpory jednostronne: zbiór węzłów w kontakcie
        ustalony z miarodajnej kombinacji charakterystycznej, dalej rozwiązania liniowe (superpozycja) [UPR]."""
        self.r_przyp = {}
        self.reakcje_przyp: dict = {}
        akt = self.r_char[self.k_char_gov].aktywne
        n_odl = len(self.r_char[self.k_char_gov].odlaczone)
        if n_odl:
            self._uwaga(f"Podpory jednostronne: w kombinacji {self.k_char_gov} {n_odl} węzłów podpór bez docisku (odrywanie krawędzi "
                        "podpory) — reakcje wg przypadków liczone z tym zbiorem kontaktu.")
        for c in self.mes.przypadki():
            r = self.mes.rozwiaz(self.mes.wektor({c: 1.0}), opis=c, aktywne=akt)
            self.r_przyp[c] = r
            self.reakcje_przyp[c] = self.mes.reakcje(r)

    def _rownowaga(self):
        """Kontrola równowagi: ΣR_z = ΣF_z dla kombinacji oraz siły w przekrojach pionowych vs statyka."""
        w = Wynik(nazwa="Kontrola równowagi modelu MES")
        r = self.r_uls[self.k_gov]
        F = float(-r.f[1::2].sum())
        R = float(r.R[1::2].sum())
        err = abs(F - R) / max(abs(F), 1e-9)
        self.blad_rownowagi = err
        w.krok(f"Suma obciążeń pionowych ({self.k_gov})", "ΣF_z", "", F, "kN")
        w.krok("Suma reakcji", "ΣR_z", "", R, "kN")
        w.krok("Błąd względny", "|ΣF_z − ΣR_z|/ΣF_z", "", f"{err:.1e}")
        # przekroje pionowe: V i M z całkowania σ vs statyka lewej części
        rows = []
        mes = self.mes
        fz = r.f[1::2]
        Rz = r.R[1::2]
        fx = r.f[0::2] + r.R[0::2]
        xs = self._x_kontrolne()
        err_max = 0.0
        for x in xs:
            c = mes.przekroj_pionowy(r, x)
            lewe = mes.nodes[:, 0] < x
            Vst = -float((fz[lewe] + Rz[lewe]).sum())          # siła poprzeczna (lewa część, w dół +)
            # równowaga części lewej względem punktu (x, 0): M_MES = ∫σ_x·t·z dz = Σ[(x_i − x)·F_z,i − z_i·F_x,i]
            Mst = float(((fz[lewe] + Rz[lewe]) * (mes.nodes[lewe, 0] - x)).sum()) - float((fx[lewe] * mes.nodes[lewe, 1]).sum())
            dv = abs(c["V"] - Vst)
            dm = abs(c["M"] - Mst)
            rel = max(dv / max(abs(Vst), 1.0), dm / max(abs(Mst), 1.0))
            err_max = max(err_max, rel)
            rows.append([f(x, 2), (c["N"], 2), (Vst, 1), (c["V"], 1), (Mst, 1), (c["M"], 1)])
        self.tab_rownowaga = rows
        self.blad_przekrojow = err_max
        self.tabele.append("**Kontrola równowagi w przekrojach pionowych (kombinacja " + self.k_gov + ")** — siły z całkowania "
                           "naprężeń MES (N = ∫σ_x·t dz, V = ∫τ·t dz, M = ∫σ_x·t·z dz) i ze statyki części lewej\n\n" + tabela(
                               ["x [m]", "N_MES [kN]", "V statyka [kN]", "V MES [kN]", "M statyka [kNm]", "M MES [kNm]"], rows))
        w.krok("Maks. względna rozbieżność V, M w przekrojach kontrolnych (MES vs statyka)", "", "", f"{err_max * 100:.2f} %")
        self.sekcje.append(w)

    def _x_kontrolne(self) -> list[float]:
        mes = self.mes
        cx = 0.5 * (mes.gx[:-1] + mes.gx[1:])
        out = []
        for s in self.d.podpory:
            for xx in (s.s0 - 0.35, s.s1 + 0.35, 0.5 * (s.s0 + s.s1)):
                if mes.gx[0] < xx < mes.gx[-1]:
                    out.append(float(cx[np.argmin(np.abs(cx - xx))]))
        return sorted(set(round(v, 4) for v in out))[:8]

    # ---------------------------------------------------------------------------------------------
    # 2. Pasy z MES (całkowanie naprężeń przy krawędziach)
    # ---------------------------------------------------------------------------------------------
    def _bloki_krawedzi(self, r: WynikT, e: Krawedz) -> list[dict]:
        """Bloki naprężeń przylegające do krawędzi e w przekrojach co element: [{"x", "F", "e", "h"}]."""
        mes = self.mes
        out = []
        if e.typ == "h":
            cx = 0.5 * (mes.gx[:-1] + mes.gx[1:])
            for x in cx[(cx > e.a) & (cx < e.b)]:
                c = mes.przekroj_pionowy(r, x)
                prof = [q for q in c["prof"] if (q[0] >= e.wsp - 1e-9 if e.strona > 0 else q[1] <= e.wsp + 1e-9)]
                if not prof:
                    continue
                b = blok_przy_krawedzi(prof, e.wsp, e.strona > 0)
                # głębokość pasma (do najbliższej krawędzi przeciwnej)
                zz = sorted(prof, key=lambda q: q[0])
                band = 0.0
                if e.strona > 0:
                    z_ = e.wsp
                    for q in zz:
                        if abs(q[0] - z_) > 1e-9:
                            break
                        z_ = q[1]
                    band = z_ - e.wsp
                else:
                    z_ = e.wsp
                    for q in reversed(zz):
                        if abs(q[1] - z_) > 1e-9:
                            break
                        z_ = q[0]
                    band = e.wsp - z_
                comp = any((q[3] < 0 or q[4] < 0) for q in prof) if b["F"] > 0 else True
                F_ = b["F"]
                if F_ > 0 and b["h"] >= band - 1e-6 and band > 0:
                    # całe pasmo rozciągane — udział cięgna tej krawędzi z reguły dźwigni (cięgna przy obu krawędziach)
                    F_ = F_ * min(max(1.0 - b["e"] / band, 0.0), 1.0)
                out.append({"x": float(x), "F": F_, "e": b["e"], "h": b["h"], "band": band, "sciskanie": comp, "s0": b["s0"],
                            "F_blok": b["F"]})
        else:
            cz = 0.5 * (mes.gz[:-1] + mes.gz[1:])
            for z in cz[(cz > e.a) & (cz < e.b)]:
                c = mes.przekroj_poziomy(r, z)
                prof = [q for q in c["prof"] if (q[0] >= e.wsp - 1e-9 if e.strona > 0 else q[1] <= e.wsp + 1e-9)]
                if not prof:
                    continue
                b = blok_przy_krawedzi(prof, e.wsp, e.strona > 0)
                zz = sorted(prof, key=lambda q: q[0])
                if e.strona > 0:
                    z_ = e.wsp
                    for q in zz:
                        if abs(q[0] - z_) > 1e-9:
                            break
                        z_ = q[1]
                    band = z_ - e.wsp
                else:
                    z_ = e.wsp
                    for q in reversed(zz):
                        if abs(q[1] - z_) > 1e-9:
                            break
                        z_ = q[0]
                    band = e.wsp - z_
                F_ = b["F"]
                comp = any((q[3] < 0 or q[4] < 0) for q in prof) if F_ > 0 else True
                if F_ > 0 and b["h"] >= band - 1e-6 and band > 0:
                    F_ = F_ * min(max(1.0 - b["e"] / band, 0.0), 1.0)
                out.append({"x": float(z), "F": F_, "e": b["e"], "h": b["h"], "band": band, "sciskanie": comp, "s0": b["s0"],
                            "F_blok": b["F"]})
        return out

    def _pasy_mes(self):
        """Wypadkowe stref rozciąganych przy krawędziach (obwiednia ULS) i SLS quasi-stała."""
        self.bloki: dict = {}          # (krawędź, kombinacja) → lista bloków
        self.pasy_mes: dict = {}
        for e in self.kraw:
            best = None
            for n, r in self.r_uls.items():
                bl = self._bloki_krawedzi(r, e)
                self.bloki[(e.id, n)] = bl
                for b in bl:
                    if b["F"] > 0 and (best is None or b["F"] > best[0]["F"]):
                        best = (b, n)
            qp = 0.0
            for n, r in self.r_qp.items():
                for b in self._bloki_krawedzi(r, e):
                    if b["F"] > qp:
                        qp = b["F"]
            s_char = 0.0
            for n, r in self.r_char.items():
                for b in self._bloki_krawedzi(r, e):
                    if b["F"] > 0:
                        s_char = max(s_char, b["s0"])
            if best is not None:
                bl = [b for b in self.bloki[(e.id, best[1])] if b["F"] > 0.05 * best[0]["F"]]
                zak = (min(b["x"] for b in bl), max(b["x"] for b in bl)) if bl else (e.a, e.b)
                self.pasy_mes[e.id] = {"F": best[0]["F"], "k": best[1], "x": best[0]["x"], "e": best[0]["e"],
                                       "h": best[0]["h"], "band": best[0]["band"], "sciskanie": best[0]["sciskanie"], "F_qp": qp,
                                       "s_char": s_char, "zakres": zak}

    # ---------------------------------------------------------------------------------------------
    # 3. STM
    # ---------------------------------------------------------------------------------------------
    def _stm(self):
        self.stm = self._generuj_stm(self.r_uls[self.k_gov])
        for n, r in self.r_uls.items():
            self._rozwiaz_stm(n, r)
        # miarodajna kombinacja STM: max Σ T·l (objętość cięgien)
        self.k_stm = max(self.stm.F, key=lambda n: float((np.clip(self.stm.F[n], 0, None) * self.stm.L).sum()))

    def _offset_h(self, r: WynikT, xa: float, xb: float, z: float, up: bool, amax: float) -> float:
        mes = self.mes
        cx = 0.5 * (mes.gx[:-1] + mes.gx[1:])
        Fs, es = [], []
        for x in cx[(cx > xa) & (cx < xb)]:
            c = mes.przekroj_pionowy(r, x)
            prof = [q for q in c["prof"] if (q[0] >= z - 1e-9 if up else q[1] <= z + 1e-9)]
            if not prof:
                continue
            b = blok_przy_krawedzi(prof, z, up)
            Fs.append(abs(b["F"]))
            es.append(b["e"])
        Fs, es = np.array(Fs), np.array(es)
        e = float((Fs * es).sum() / Fs.sum()) if len(Fs) and Fs.sum() > 0 else self.a_s
        return min(max(e, self.a_s), max(amax, self.a_s))

    def _offset_v(self, r: WynikT, za: float, zb: float, x: float, right: bool, amax: float) -> float:
        mes = self.mes
        cz = 0.5 * (mes.gz[:-1] + mes.gz[1:])
        Fs, es = [], []
        for z in cz[(cz > za) & (cz < zb)]:
            c = mes.przekroj_poziomy(r, z)
            prof = [q for q in c["prof"] if (q[0] >= x - 1e-9 if right else q[1] <= x + 1e-9)]
            if not prof:
                continue
            b = blok_przy_krawedzi(prof, x, right)
            Fs.append(abs(b["F"]))
            es.append(b["e"])
        Fs, es = np.array(Fs), np.array(es)
        e = float((Fs * es).sum() / Fs.sum()) if len(Fs) and Fs.sum() > 0 else self.a_s
        return min(max(e, self.a_s), max(amax, self.a_s))

    def _generuj_stm(self, r: WynikT) -> ModelSTM:
        """Węzły i pręty kandydujące STM na podstawie geometrii i pola naprężeń MES (kombinacja r)."""
        P, mes, d = self.P, self.mes, self.d
        Dx, Dz = self.dx_stm, self.dz_stm
        pasma = _pasma(P, self.kraw)
        # --- wiersze (linie pasów) w pasmach
        strips = []
        for xa, xb, ints in pasma:
            ii_ = []
            for za, zb in ints:
                band = zb - za
                amax = min(0.25, 0.15 * band)
                ea = self._offset_h(r, xa, xb, za, True, amax)
                eb = self._offset_h(r, xa, xb, zb, False, amax)
                r0, r1 = za + ea, zb - eb
                if r1 - r0 > 0.05:
                    n = max(int(math.ceil((r1 - r0) / Dz - 1e-9)), 1)
                    rows = [(float(v), None) for v in np.linspace(r0, r1, n + 1)]
                    rows[0] = (rows[0][0], ("h", za, ea))
                    rows[-1] = (rows[-1][0], ("h", zb, eb))
                else:
                    rows = [(0.5 * (za + zb), ("h", za, 0.5 * band))]
                ii_.append([za, zb, rows])
            strips.append([xa, xb, ii_])
        # wspólne linie pasów z pasm sąsiednich
        for k, (xa, xb, ints) in enumerate(strips):
            nb = [strips[j] for j in (k - 1, k + 1) if 0 <= j < len(strips)]
            for it in ints:
                za, zb, rows = it
                extra = []
                for _, _, ints_n in nb:
                    for za2, zb2, rows2 in ints_n:
                        for rz, inf in (rows2[0], rows2[-1]):
                            if za + 0.03 < rz < zb - 0.03:
                                extra.append((rz, None))
                allr = sorted(rows + extra, key=lambda q: q[0])
                out = [allr[0]]
                for q in allr[1:]:
                    if q[0] - out[-1][0] < 0.05:
                        if q[1] is not None and out[-1][1] is None:
                            out[-1] = q
                        continue
                    out.append(q)
                it[2] = out
        # --- kolumny
        cols = []
        for e in self.kraw:
            if e.typ != "v":
                continue
            cand = [q.wsp for q in self.kraw if q.typ == "v" and (q.wsp > e.wsp + 1e-6 if e.strona > 0 else q.wsp < e.wsp - 1e-6)
                    and q.a < e.b - 1e-6 and q.b > e.a + 1e-6]
            wd = min(abs(v - e.wsp) for v in cand) if cand else 1.0
            ev = self._offset_v(r, e.a, e.b, e.wsp, e.strona > 0, min(0.25, 0.15 * wd))
            cols.append((e.wsp + e.strona * ev, 3, ("v", e.wsp, ev)))
        x_lo, x_hi = P.bounds[0] + 0.02, P.bounds[2] - 0.02
        for s in d.podpory:
            if s.dl > 1e-9:
                cols += [(min(max(s.s0, x_lo), x_hi), 1, None), (min(max(s.s1, x_lo), x_hi), 1, None)]
            else:
                cols.append((s.s0, 2, None))
        for o in d.obciazenia:
            if isinstance(o, ObcSkupione):
                cols.append((o.s, 2, None))
        cols.sort(key=lambda q: q[0])
        cc = []
        for q in cols:
            if cc and abs(cc[-1][0] - q[0]) < 0.08:
                if q[1] > cc[-1][1]:
                    cc[-1] = q
                continue
            cc.append(q)
        full = [cc[0]]
        for q0, q1 in zip(cc[:-1], cc[1:]):
            n = max(int(math.ceil((q1[0] - q0[0]) / Dx - 1e-9)), 1)
            for v in np.linspace(q0[0], q1[0], n + 1)[1:-1]:
                full.append((float(v), 0, None))
            full.append(q1)
        # --- węzły
        wezly, info = [], []
        for xc, _, cinf in full:
            for xa, xb, ints in strips:
                if xa - 1e-9 <= xc <= xb + 1e-9:
                    for za, zb, rows in ints:
                        for rz, rinf in rows:
                            if P.buffer(-0.01).contains(Point(xc, rz)):
                                wezly.append((xc, rz))
                                info.append({"h": rinf, "v": cinf})
                    break
        W = np.array(wezly)
        # --- pręty kandydujące
        N = len(W)
        R_max = 1.95 * max(Dx, Dz)
        ii, jj = np.triu_indices(N, 1)
        dd = np.hypot(*(W[jj] - W[ii]).T)
        sel = (dd <= R_max) & (dd > 0.02)
        ii, jj, dd = ii[sel], jj[sel], dd[sel]
        lines = shapely.linestrings(np.stack([W[ii], W[jj]], axis=1))
        Pp = P.buffer(0.004)
        shapely.prepare(Pp)
        ok = shapely.contains(Pp, lines)
        ii, jj, dd = ii[ok], jj[ok], dd[ok]
        keep = np.ones(len(ii), bool)
        for k in range(len(ii)):
            pa, pb = W[ii[k]], W[jj[k]]
            u = (pb - pa) / dd[k]
            rel = W - pa
            t_ = rel @ u
            perp = np.abs(rel @ np.array([-u[1], u[0]]))
            if np.any((t_ > 1e-6) & (t_ < dd[k] - 1e-6) & (perp < 0.02)):
                keep[k] = False
        ii, jj, dd = ii[keep], jj[keep], dd[keep]
        U = (W[jj] - W[ii]) / dd[:, None]
        # naprężenie sprężyste wzdłuż pręta (średnia z 5 punktów)
        sbar = np.zeros(len(ii))
        for k in range(len(ii)):
            vals = []
            for tt in (0.1, 0.3, 0.5, 0.7, 0.9):
                q = W[ii[k]] + tt * (W[jj[k]] - W[ii[k]])
                sg = mes.naprezenia_xy(r, *q)
                if sg is None:
                    continue
                u = U[k]
                vals.append(u[0] ** 2 * sg[0] + u[1] ** 2 * sg[1] + 2 * u[0] * u[1] * sg[2])
            sbar[k] = float(np.mean(vals)) if vals else 0.0
        # stopień węzła (usunięcie izolowanych)
        deg = np.bincount(np.concatenate([ii, jj]), minlength=N)
        if (deg == 0).any():
            keepn = np.nonzero(deg > 0)[0]
            remap = -np.ones(N, int)
            remap[keepn] = np.arange(len(keepn))
            W = W[keepn]
            info = [info[k] for k in keepn]
            ii, jj = remap[ii], remap[jj]
        model = ModelSTM(W, ii, jj, dd, U, info, sbar)
        self._macierze_przeniesienia(model)
        return model

    def _macierze_przeniesienia(self, m: ModelSTM):
        """Macierze przeniesienia sił węzłowych MES → węzły STM (zachowanie wypadkowej i momentu):
        siła pionowa w (x, z) → dwa węzły STM obejmujące x (preferowane linie pasów), pozioma → obejmujące z."""
        mes = self.mes
        W = m.wezly
        krawedziowy = np.array([inf["h"] is not None for inf in m.info])
        pion = np.array([inf["v"] is not None for inf in m.info])
        n_f, n_s = mes.nn, len(W)
        rz, cz, vz = [], [], []
        rx, cx_, vx = [], [], []
        for k, (x, z) in enumerate(mes.nodes):
            for axis in (0, 1):
                dd = np.hypot(W[:, 0] - x, W[:, 1] - z)
                pen = dd + np.where(krawedziowy if axis == 0 else pion | krawedziowy, 0.0, 50.0)
                near = np.argsort(pen)[:16]
                c = (x, z)[axis]
                cv = W[near, axis]
                lo = near[cv <= c + 1e-9]
                hi = near[cv >= c - 1e-9]
                best = None
                if len(lo) and len(hi):
                    A_ = W[lo, axis][:, None]
                    B_ = W[hi, axis][None, :]
                    sc = pen[lo][:, None] + pen[hi][None, :]
                    same = np.abs(B_ - A_) < 1e-9
                    sc = np.where(same & (np.abs(A_ - c) > 1e-9), np.inf, sc)
                    a_i, b_i = np.unravel_index(np.argmin(sc), sc.shape)
                    if np.isfinite(sc[a_i, b_i]):
                        a, b = lo[a_i], hi[b_i]
                        xa, xb = W[a, axis], W[b, axis]
                        wa = 1.0 if abs(xb - xa) < 1e-9 else (xb - c) / (xb - xa)
                        best = (a, b, wa)
                if best is None:
                    # ekstrapolacja liniowa: najbliższy węzeł a i najbliższy b o współrzędnej różnej o ≥ 0,3 m
                    order = np.argsort(pen)
                    a = order[0]
                    far = order[np.abs(W[order, axis] - W[a, axis]) >= 0.3]
                    b = far[0] if len(far) else order[1]
                    xa, xb = W[a, axis], W[b, axis]
                    best = (a, b, (xb - c) / (xb - xa) if abs(xb - xa) > 1e-9 else 1.0)
                a, b, wa = best
                if axis == 0:
                    rz += [a, b]
                    cz += [k, k]
                    vz += [wa, 1 - wa]
                else:
                    rx += [a, b]
                    cx_ += [k, k]
                    vx += [wa, 1 - wa]
        m.Wz = sparse.csr_matrix((vz, (rz, cz)), shape=(n_s, n_f))
        m.Wx = sparse.csr_matrix((vx, (rx, cx_)), shape=(n_s, n_f))
        # długość docisku przypisana węzłom (podpory): Σ w·l_trib
        trib = np.zeros(n_f)
        for s in self.d.podpory:
            nd = mes.pod_wezly[s.id]
            trib[nd] += mes.pod_trib[s.id] if s.dl > 1e-9 else 0.15
        m.l_docisku = np.asarray(m.Wz @ trib).ravel()

    def _rozwiaz_stm(self, nazwa: str, r: WynikT):
        m = self.stm
        Fx = r.f[0::2] + r.R[0::2]
        Fz = r.f[1::2] + r.R[1::2]
        P = np.stack([m.Wx @ Fx, m.Wz @ Fz], axis=1)
        Rw = np.stack([m.Wx @ r.R[0::2], m.Wz @ r.R[1::2]], axis=1)
        # rzutowanie na dokładną równowagę (usunięcie składowych ciała sztywnego — błąd numeryczny ~1e-12)
        n = len(m.wezly)
        G = np.zeros((2 * n, 3))
        G[0::2, 0] = 1
        G[1::2, 1] = 1
        G[0::2, 2] = -m.wezly[:, 1]
        G[1::2, 2] = m.wezly[:, 0]
        pv = P.ravel()
        pv = pv - G @ np.linalg.lstsq(G, pv, rcond=None)[0]
        P = pv.reshape(-1, 2)
        M_ = len(m.ii)
        rows = np.concatenate([2 * m.ii, 2 * m.ii + 1, 2 * m.jj, 2 * m.jj + 1])
        colsA = np.concatenate([np.arange(M_)] * 4)
        vals = np.concatenate([m.U[:, 0], m.U[:, 1], -m.U[:, 0], -m.U[:, 1]])
        A = sparse.csr_matrix((vals, (rows, colsA)), shape=(2 * n, M_))
        sref = max(float(np.percentile(np.abs(np.concatenate([self.s1_env, self.s2_env])), 90)), 1.0)
        st = np.clip(m.sbar / sref, 0, 1)
        sc = np.clip(-m.sbar / sref, 0, 1)
        cT = m.L * (1.0 + BETA_MES * sc)
        cC = m.L * (R_C + BETA_MES * st)
        big = 1e3 * float(m.L.max())
        I = sparse.identity(2 * n, format="csr")
        Aeq = sparse.hstack([A, -A, I, -I]).tocsr()
        c = np.concatenate([cT, cC, np.full(4 * n, big)])
        res = linprog(c, A_eq=Aeq, b_eq=-P.ravel(), bounds=(0, None), method="highs")
        if res.x is None:
            raise BladDanych(f"STM tarczy {self.d.id}: brak rozwiązania LP ({res.message})")
        Fm = res.x[:M_] - res.x[M_:2 * M_]
        luz = float(np.abs(res.x[2 * M_:]).max()) if 4 * n else 0.0
        m.F[nazwa] = Fm
        m.P[nazwa] = P
        m.Rw[nazwa] = Rw
        m.luz[nazwa] = luz
        if luz > 1e-3 * max(np.abs(P).max(), 1.0):
            self._uwaga(f"STM ({nazwa}): niezrównoważenie węzłów {luz:.2f} kN — siatka węzłów zbyt rzadka [UPR]")

    # ---------------------------------------------------------------------------------------------
    # 4. Siatki (zbrojenie minimalne 9.6, 9.7) i zbrojenie z pola naprężeń (zał. F)
    # ---------------------------------------------------------------------------------------------
    def _siatki(self):
        d, p, b, st = self.d, self.p, self.beton, self.stal
        t_mm = d.t * 1000
        w = Wynik(nazwa="Zbrojenie minimalne ścian i belek-ścian — siatki przy obu powierzchniach (9.6, 9.7)")
        Asv_min = 0.002 * t_mm * 1000
        w.krok("Zbrojenie pionowe ściany (łącznie)", "A_s,vmin = 0,002·A_c", f"0,002·{f(t_mm, 0)}·1000", Asv_min, "mm²/m", nd=0,
               zrodlo="9.6.2(1) [NZW NA]")
        Ash_min = max(0.25 * Asv_min, 0.001 * t_mm * 1000)
        w.krok("Zbrojenie poziome ściany (łącznie)", "A_s,hmin = max(0,25·A_s,v; 0,001·A_c)", "", Ash_min, "mm²/m", nd=0,
               zrodlo="9.6.3(1) [NZW NA]")
        Adb = max(0.001 * t_mm * 1000, 150.0)
        w.krok("Belka-ściana: siatka przy każdej powierzchni w obu kierunkach", "A_s,dbmin = max(0,1 %·A_c; 150 mm²/m)",
               f"max(0,001·{f(t_mm, 0)}·1000; 150)", Adb, "mm²/m", nd=0, zrodlo="9.7(1) [NZW NA]")
        smax = min(2 * t_mm, 300.0, 3 * t_mm, 400.0)
        w.krok("Maks. rozstaw prętów siatki", "s_max = min(2t; 300 mm) (9.7(2)); ściany: min(3t; 400 mm)", "", smax, "mm", nd=0)
        # zał. F — obwiednia ULS (poza strefami osobliwymi naroży otworów)
        req_x, req_z, scd = self._zal_F()
        self.req_x, self.req_z, self.scd = req_x, req_z, scd
        msk = self._maska_nieosobliwa()
        rx95 = float(np.percentile(req_x[msk], 95)) if msk.any() else 0.0
        rz95 = float(np.percentile(req_z[msk], 95)) if msk.any() else 0.0
        need_face = max(Adb, Asv_min / 2, Ash_min / 2, rx95 / 2, rz95 / 2)
        fi = d.fi_siatki
        a1 = pole_preta(fi)
        s = min(int(smax // 25 * 25), int(a1 * 1000 / need_face // 25 * 25))      # rozstaw co 25 mm
        while s < 100 and fi < 12:
            fi += 2
            a1 = pole_preta(fi)
            s = min(int(smax // 25 * 25), int(a1 * 1000 / need_face // 25 * 25))
        As_face = a1 * 1000 / s
        self.siatka_fi, self.siatka_s, self.siatka_As = fi, s, As_face
        w.krok("Zbrojenie z pola naprężeń (zał. F, obwiednia ULS, 95 % elementów poza narożami otworów)",
               "a_sx; a_sz (łącznie obie powierzchnie)", "", f"{f(rx95, 0)}; {f(rz95, 0)} mm²/m", zrodlo="zał. F (F.2–F.7)")
        w.krok("Przyjęto siatkę przy każdej powierzchni", f"φ{fi} co {s} mm (w obu kierunkach)", "", As_face, "mm²/m", nd=0)
        w.warunek("Siatka przy powierzchni ≥ A_s,dbmin (9.7) i połowa A_s,vmin (9.6)", max(Adb, Asv_min / 2), As_face, "mm²/m",
                  "9.6.2, 9.7(1)", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
        self.sekcje.append(w)
        self.przyjeto.append(f"Siatki przy obu powierzchniach: φ{fi} co {s} mm w obu kierunkach (A_s = {f(As_face, 0)} mm²/m "
                             f"na powierzchnię), otulina c_nom = {f(self.c_nom * 1000, 0)} mm ({d.ekspozycja}).")

    def _zal_F_kontrola(self):
        """Zał. F: zbrojenie z pola naprężeń poza strefami cięgien (pasma u przy krawędziach) i naroży otworów ≤ siatki."""
        b = self.beton
        mes = self.mes
        msk = self._maska_nieosobliwa()
        for pas in self.pasy:
            e = pas.krawedz
            if e is None:
                continue
            u = 2 * pas.a + 0.10
            c = mes.el_c
            if e.typ == "h":
                z0, z1 = sorted((e.wsp, e.wsp + e.strona * u))
                inb = (c[:, 1] > z0) & (c[:, 1] < z1) & (c[:, 0] > e.a - 0.1) & (c[:, 0] < e.b + 0.1)
            else:
                x0, x1 = sorted((e.wsp, e.wsp + e.strona * u))
                inb = (c[:, 0] > x0) & (c[:, 0] < x1) & (c[:, 1] > e.a - 0.1) & (c[:, 1] < e.b + 0.1)
            msk &= ~inb
        self.maska_srodnika = msk
        w = Wynik(nazwa="Zbrojenie z pola naprężeń MES (zał. F) — środnik poza cięgnami i narożami otworów")
        cap = 2 * self.siatka_As
        rxm = float(self.req_x[msk].max()) if msk.any() else 0.0
        rzm = float(self.req_z[msk].max()) if msk.any() else 0.0
        w.krok("Zbrojenie wymagane (ściskanie dodatnie; σ_Edx > σ_Edy): σ_Edx ≤ |τ| → f_tdx = |τ| − σ_Edx, f_tdy = |τ| − σ_Edy, "
               "σ_cd = 2|τ|; σ_Edx > |τ| → f_tdx = 0, f_tdy = τ²/σ_Edx − σ_Edy, σ_cd = σ_Edx·(1 + (τ/σ_Edx)²); a_s = f_td·t/f_yd",
               "", "", "", zrodlo="zał. F, (F.2)–(F.7) [P]")
        w.warunek("Zbrojenie poziome środnika (maks.) ≤ siatki obu powierzchni", rxm, cap, "mm²/m", "zał. F", nd=0,
                  symbol_E="a_sx,req", symbol_R="a_sx,prov")
        w.warunek("Zbrojenie pionowe środnika (maks.) ≤ siatki obu powierzchni", rzm, cap, "mm²/m", "zał. F", nd=0,
                  symbol_E="a_sz,req", symbol_R="a_sz,prov")
        nu = 0.6 * (1 - b.f_ck / 250)
        if msk.any():
            e_ = int(np.argmax(np.where(msk, self.eta_F, -1)))
            w.warunek("Naprężenie w betonie σ_cd ≤ ν·f_cd (ściskanie dwuosiowe: ≤ f_cd)", self.scd[e_] / 1000,
                      self.scd[e_] / 1000 / max(self.eta_F[e_], 1e-9), "MPa", "zał. F (F.4), (F.7), F(3); (6.6N)",
                      symbol_E="σ_cd", symbol_R="σ_Rd")
        self.sekcje.append(w)

    def _zal_F(self):
        """Zbrojenie wg zał. F (obwiednia ULS): a_sx, a_sz [mm²/m, łącznie], σ_cd [kPa] w elementach."""
        fyd = self.stal.f_yd * 1000   # kPa
        t = self.mes.t_el
        rx = np.zeros(self.mes.ne)
        rz = np.zeros(self.mes.ne)
        sc = np.zeros(self.mes.ne)
        for r in self.r_uls.values():
            sx, sz, tau = -r.sig[:, 0], -r.sig[:, 1], np.abs(r.sig[:, 2])      # ściskanie dodatnie (zał. F)
            swap = sz > sx
            A_ = np.where(swap, sz, sx)       # większe ściskanie → kierunek „x” zał. F
            B_ = np.where(swap, sx, sz)
            bez = (A_ >= 0) & (B_ >= 0) & (A_ * B_ >= tau ** 2)
            c1 = A_ <= tau
            ftA = np.where(c1, tau - A_, 0.0)
            ftB = np.where(c1, tau - B_, np.where(A_ > 1e-9, tau ** 2 / np.maximum(A_, 1e-9), 0.0) - B_)
            scd = np.where(c1, 2 * tau, A_ * (1 + (tau / np.maximum(A_, 1e-9)) ** 2))
            ftA = np.where(bez, 0.0, np.clip(ftA, 0, None))
            ftB = np.where(bez, 0.0, np.clip(ftB, 0, None))
            scd = np.where(bez, np.maximum(A_, B_), scd)
            fx = np.where(swap, ftB, ftA)
            fz = np.where(swap, ftA, ftB)
            rx = np.maximum(rx, fx * t / fyd * 1e6)
            rz = np.maximum(rz, fz * t / fyd * 1e6)
            # wytężenie betonu: σ_cd/(ν·f_cd) przy zbrojeniu, σ_max/f_cd w dwuosiowym ściskaniu (F(3))
            nu = 0.6 * (1 - self.beton.f_ck / 250)
            eta_c = np.where(bez, scd / (self.beton.f_cd * 1000), scd / (nu * self.beton.f_cd * 1000))
            self.eta_F = np.maximum(getattr(self, "eta_F", np.zeros_like(eta_c)), eta_c)
            sc = np.maximum(sc, scd)
        return rx, rz, sc

    def _maska_nieosobliwa(self, r_=0.15) -> np.ndarray:
        """Elementy dalej niż r_ od naroży wklęsłych (naroża otworów, załamania obrysu) — bez osobliwości sprężystych."""
        pts = []
        for o in self.d.otwory:
            pts += [(o.s0, o.z0), (o.s1, o.z0), (o.s0, o.z1), (o.s1, o.z1)]
        for s in self.d.podpory:
            pts += [(s.s0, s.z), (s.s1, s.z)]
        if not pts:
            return np.ones(self.mes.ne, bool)
        pts = np.array(pts)
        c = self.mes.el_c
        dmin = np.min(np.hypot(c[:, None, 0] - pts[None, :, 0], c[:, None, 1] - pts[None, :, 1]), axis=1)
        return dmin > r_

    # ---------------------------------------------------------------------------------------------
    # 5. Cięgna (pasy) — grupowanie STM, MES, dobór zbrojenia, zakotwienie, rysy
    # ---------------------------------------------------------------------------------------------
    def _krawedz_preta(self, pa, pb, U) -> tuple[str, Krawedz | None]:
        """Przypisanie cięgna do krawędzi (pas przy krawędzi) lub strefy (środnik/wieszaki/ukośne)."""
        mid = 0.5 * (pa + pb)
        ang = abs(math.degrees(math.atan2(U[1], U[0])))
        ang = min(ang, 180 - ang)
        P = self.P
        best = None
        if ang <= 25:
            for e in self.kraw:
                if e.typ != "h" or not (e.a - 0.05 <= mid[0] <= e.b + 0.05):
                    continue
                dz = (mid[1] - e.wsp) * e.strona
                if dz <= 0 or dz > 0.45:
                    continue
                if not P.buffer(1e-4).contains(LineString([(mid[0], e.wsp + e.strona * 1e-3), tuple(mid)])):
                    continue
                if best is None or dz < best[0]:
                    best = (dz, e)
            return ("h", best[1]) if best else ("wh", None)
        if ang >= 65:
            for e in self.kraw:
                if e.typ != "v" or not (e.a - 0.05 <= mid[1] <= e.b + 0.05):
                    continue
                dx = (mid[0] - e.wsp) * e.strona
                if dx <= 0 or dx > 0.40:
                    continue
                if not P.buffer(1e-4).contains(LineString([(e.wsp + e.strona * 1e-3, mid[1]), tuple(mid)])):
                    continue
                if best is None or dx < best[0]:
                    best = (dx, e)
            return ("v", best[1]) if best else ("wv", None)
        return ("d", None)

    def _ciegna(self):
        d, p, b, st = self.d, self.p, self.beton, self.stal
        grupy: dict = {}
        wv_demand = wh_demand = wd_demand = 0.0      # cięgna środnika: gęstość sił [kN/m]
        if hasattr(self, "stm"):
            m = self.stm
            for n, F in m.F.items():
                Fmax = max(float(np.abs(F).max()), 1e-9)
                for k in np.nonzero(F > 0.01 * Fmax)[0]:
                    pa, pb = m.wezly[m.ii[k]], m.wezly[m.jj[k]]
                    typ, e = self._krawedz_preta(pa, pb, m.U[k])
                    if typ in ("h", "v"):
                        g = grupy.setdefault(e.id, {"e": e, "F": 0.0, "k": "", "prety": []})
                        if F[k] > g["F"]:
                            g["F"], g["k"] = float(F[k]), n
                        ax = 0 if e.typ == "h" else 1
                        g["prety"].append((min(pa[ax], pb[ax]), max(pa[ax], pb[ax]), float(F[k]),
                                           float(0.5 * (abs(pa[1 - ax] - e.wsp) + abs(pb[1 - ax] - e.wsp)))))
                    else:
                        wdt = self.dx_stm if typ == "wv" else self.dz_stm
                        dem = float(F[k]) / wdt
                        if typ == "wv":
                            wv_demand = max(wv_demand, dem)
                        elif typ == "wh":
                            wh_demand = max(wh_demand, dem)
                        else:
                            wd_demand = max(wd_demand, dem / math.sqrt(2))
        for e in self.kraw:
            pm = self.pasy_mes.get(e.id)
            if pm and pm["F"] > 5.0 and e.id not in grupy:
                grupy[e.id] = {"e": e, "F": 0.0, "k": "", "prety": []}
        self.odcinki_ciegien = {}
        for key, g in grupy.items():
            env: dict = {}
            for a0, a1, Fv, _ in g["prety"]:
                kk_ = (round(a0, 3), round(a1, 3))
                env[kk_] = max(env.get(kk_, 0.0), Fv)
            self.odcinki_ciegien[key] = [(a0, a1, Fv) for (a0, a1), Fv in sorted(env.items())]
        fyd = st.f_yd
        wmax = p.w_max.get(d.ekspozycja, 0.3)
        w = Wynik(nazwa="Cięgna (pasy rozciągane) — STM i całkowanie naprężeń MES (6.5.3, 7.3.2, 7.3.4, 8.4)")
        rows = []
        for key, g in grupy.items():
            e = g["e"]
            pm = self.pasy_mes.get(key, {})
            pas = Pas(key, e.opis, e.typ, e, F_stm=g["F"], k_stm=g["k"], F_mes=pm.get("F", 0.0), k_mes=pm.get("k", ""),
                      x_mes=pm.get("x", 0.0), F_qp=pm.get("F_qp", 0.0))
            if pas.F_Ed < 1.0:
                continue
            istotne = [q for q in g["prety"] if q[2] > 0.05 * max(g["F"], 1e-9)]
            if istotne:
                z0 = min(q[0] for q in istotne)
                z1 = max(q[1] for q in istotne)
                pas.a = float(np.median([q[3] for q in istotne]))
            else:
                z0, z1 = pm.get("zakres", (e.a, e.b))
                pas.a = self.a_s
            if pm.get("zakres"):
                z0, z1 = min(z0, pm["zakres"][0]), max(z1, pm["zakres"][1])
            pas.zakres = (max(z0, e.a), min(z1, e.b))
            # siły na końcach cięgna (do zakotwienia)
            F_lo = max([q[2] for q in istotne if abs(q[0] - z0) < 0.06] or [0.0])
            F_hi = max([q[2] for q in istotne if abs(q[1] - z1) < 0.06] or [0.0])
            if not istotne:
                F_lo = F_hi = pas.F_Ed
            pas.konce = [F_lo, F_hi]
            band = pm.get("band", 0.5)
            pas.h_t = pm.get("h", 0.0)
            pas.k_c = 0.4 if pm.get("sciskanie", True) else 1.0
            # zbrojenie minimalne (7.3.2) — gdy strefa rysuje się w kombinacji charakterystycznej (σ > f_ctm) [UPR]
            s_char = pm.get("s_char", 0.0) / 1000
            if pas.F_mes > 0 and s_char > b.f_ctm:
                hmm = max(min(pas.h_t, band), 0.05) * 1000
                kk = 1.0 if hmm <= 300 else (0.65 if hmm >= 800 else 1.0 - 0.35 * (hmm - 300) / 500)
                As_min = pas.k_c * kk * b.f_ctm * (d.t * 1000 * hmm) / st.f_yk
            else:
                As_min = 0.0
            pas.As_min = As_min
            pas.As_req = pas.F_Ed * 1000 / fyd
            need = max(pas.As_req, As_min)
            u_band = max(2 * pas.a, 0.10)
            for n_face, fi in self._kandydaci_ciegna(need, u_band):
                pas.n, pas.fi = 2 * n_face, fi
                pas.As_prov = 2 * n_face * pole_preta(fi)
                if pas.F_qp > 0:
                    pas.sigma_s = pas.F_qp * 1000 / pas.As_prov
                    pas.w_k = self._wk(pas, band)
                    if pas.w_k <= wmax:
                        break
                else:
                    break
            self.pasy.append(pas)
            rows.append([pas.opis, (pas.F_stm, 1), (pas.F_mes, 1), (pas.F_Ed, 1), (pas.As_req, 0),
                         (As_min, 0) if As_min > 0 else f"— (σ_char = {f(s_char, 2)} ≤ f_ctm)",
                         f"{pas.n}φ{pas.fi} ({pas.n // 2}/pow.)", (pas.As_prov, 0), (pas.sigma_s, 0) if pas.F_qp > 0 else "—",
                         f(pas.w_k, 3) if pas.F_qp > 0 else "—"])
            w.warunek(f"Cięgno „{pas.opis}”: A_s ≥ max(F_Ed/f_yd; A_s,min)", need, pas.As_prov, "mm²", "6.5.3, 7.3.2", nd=0,
                      symbol_E="A_s,req", symbol_R="A_s,prov")
            if pas.F_qp > 0:
                w.warunek(f"Rysy — cięgno „{pas.opis}” (quasi-stała)", pas.w_k, wmax, "mm", "7.3.4, tabl. 7.1N", nd=3,
                          symbol_E="w_k", symbol_R="w_max")
            self._zakotwienie(pas, w)
        self.pasy.sort(key=lambda q: -q.F_Ed)
        w.krok("Siły w cięgnach: F_Ed = max(F_STM; F_MES); F_MES — wypadkowa rozciągania w strefie przy krawędzi (całkowanie "
               "σ w przekrojach co element, obwiednia ULS; gdy rozciągane jest całe pasmo — udział krawędzi z reguły dźwigni "
               "F·(1 − e/h_pasma)); A_s,req = F_Ed/f_yd", "", "", "", zrodlo="6.5.3, 5.6.4(5)")
        w.krok("Zbrojenie minimalne ze względu na rysy w strefie rozciąganej (h_t z MES), gdy σ_ct,char > f_ctm",
               "A_s,min = k_c·k·f_ct,eff·A_ct/σ_s", "σ_s = f_yk, k_c = 0,4 (zginanie) / 1,0 (rozciąganie całego pasma)", "",
               zrodlo="(7.1) [UPR]")
        w.krok("Szerokość rys cięgna", "w_k = s_r,max·(ε_sm − ε_cm), σ_s = F_qp,MES/A_s, h_c,ef = min(2,5·(c + φ/2); h_pasma/2), "
               "k₁ = 0,8, k₂ = 0,5 (zginanie) / 1,0, k_t = 0,4", "", "", zrodlo="(7.8)–(7.11)")
        self.tabele.append("**Cięgna (pasy rozciągane)** — siły ULS i dobór zbrojenia (pręty przy obu powierzchniach)\n\n" + tabela(
            ["Cięgno", "F_STM [kN]", "F_MES [kN]", "F_Ed [kN]", "A_s,req [mm²]", "A_s,min [mm²]", "Przyjęto", "A_s,prov [mm²]",
             "σ_s,qp [MPa]", "w_k [mm]"], rows))
        As_mesh2 = 2 * self.siatka_As
        cap = As_mesh2 * fyd / 1000        # kN/m
        if wv_demand > 0:
            w.krok("Pionowe cięgna środnika (wieszaki) — maks. gęstość siły z STM", "t_v = F/Δx", "", wv_demand, "kN/m")
            w.warunek("Wieszaki: siatka pionowa obu powierzchni", wv_demand, cap, "kN/m", "6.5.3, 9.7", symbol_E="t_v,Ed",
                      symbol_R="a_sv·f_yd")
        if wh_demand > 0:
            w.krok("Poziome cięgna środnika — maks. gęstość siły z STM", "t_h = F/Δz", "", wh_demand, "kN/m")
            w.warunek("Środnik: siatka pozioma obu powierzchni", wh_demand, cap, "kN/m", "6.5.3, 9.7", symbol_E="t_h,Ed",
                      symbol_R="a_sh·f_yd")
        if wd_demand > 0:
            w.krok("Ukośne cięgna środnika — składowa na kierunek siatki", "t_d/√2", "", wd_demand, "kN/m")
            w.warunek("Środnik: siatka (cięgna ukośne)", wd_demand, cap, "kN/m", "6.5.3", symbol_E="t_d,Ed", symbol_R="a_s·f_yd")
        self.sekcje.append(w)
        self.T_max = max((q.F_Ed for q in self.pasy), default=0.0)

    def _kandydaci_ciegna(self, As_req: float, u_band: float) -> list[tuple[int, int]]:
        """Warianty zbrojenia cięgna (n na powierzchnię, φ) o A_s ≥ A_s,req, rosnąco wg pola; pręty w pasie u rozstawione
        ≥ max(φ; 20 mm; d_g + 5) (8.2)."""
        cand = []
        for fi in (12, 14, 16, 20, 25):
            smin = max(fi, 20, self.p.fi_kruszywa + 5)
            for n in (1, 2, 3, 4):
                if (n - 1) * (fi + smin) / 1000 > max(u_band, 0.08) + 1e-9:
                    continue
                A = 2 * n * pole_preta(fi)
                if A >= As_req:
                    cand.append((A, -n, fi, n))
        cand.sort()
        return [(c[3], c[2]) for c in cand] or [(4, 25)]

    def _wk(self, pas: Pas, band: float) -> float:
        p, b = self.p, self.beton
        c = self.c_nom * 1000 + self.d.fi_siatki
        fi = pas.fi
        a_s = c + fi / 2
        hce = min(2.5 * a_s, max(band, 0.1) * 1000 / 2)
        rho = pas.As_prov / (self.d.t * 1000 * hce)
        ae = p.E_s / b.E_cm
        sig = pas.sigma_s
        de = max((sig - 0.4 * b.f_ctm / rho * (1 + ae * rho)) / p.E_s, 0.6 * sig / p.E_s)
        k2 = 1.0 if pas.k_c >= 1.0 else 0.5
        sr = 3.4 * c + 0.8 * k2 * 0.425 * fi / rho
        return sr * de

    def _zakotwienie(self, pas: Pas, w: Wynik):
        """Zakotwienie cięgna za skrajnymi węzłami (8.4, 6.5.4(7)): długość dostępna do krawędzi betonu wzdłuż cięgna;
        σ_sd = F_koniec/A_s,prov. Gdy brak miejsca na pręt prosty lub z hakiem (α₁ = 0,7) — U-pręty (strzemiona
        zamykające) na końcu, łączone z prętami cięgna na zakład l₀ (8.7) mierzony do wnętrza tarczy."""
        b, st = self.beton, self.stal
        e = pas.krawedz
        if e is None:
            return
        if e.typ == "h":
            z_osi = e.wsp + e.strona * pas.a
            # 8.4.2(2), rys. 8.2: pręty poziome w elemencie h > 600 mm leżące ≤ 300 mm od górnej powierzchni — warunki „inne”
            dobra = not (self.d.H > 0.6 and (self.d.z0 + self.d.H - z_osi) < 0.30)
        else:
            dobra = True
        for sgn, F_end in ((-1, pas.konce[0] if pas.konce else pas.F_Ed), (1, pas.konce[1] if pas.konce else pas.F_Ed)):
            sig = min(max(F_end, 0.0) * 1000 / pas.As_prov, st.f_yd)
            zk = zelbet.zakotwienie(pas.fi, b, st, sigma_sd=max(sig, 1.0), dobra_przyczepnosc=dobra)
            lbd = zk.l_bd / 1000
            lbd_hak = max(0.7 * zk.l_bd / 1000, 10 * pas.fi / 1000, 0.1)
            x_end = pas.zakres[1] if sgn > 0 else pas.zakres[0]
            if e.typ == "h":
                pnt, kier = (x_end, e.wsp + e.strona * pas.a), (sgn, 0.0)
            else:
                pnt, kier = (e.wsp + e.strona * pas.a, x_end), (0.0, sgn)
            l_av = _dl_promienia(self.P, pnt, kier) - self.c_nom
            L_in = pas.zakres[1] - pas.zakres[0]
            if l_av >= lbd:
                spos, E_, R_, sE, sR = "proste", lbd, l_av, "l_bd", "l_dost"
            elif l_av >= lbd_hak:
                spos, E_, R_, sE, sR = "hak 90° (α₁ = 0,7)", lbd_hak, l_av, "l_bd,h", "l_dost"
            else:
                zkU = zelbet.zakotwienie(pas.fi, b, st, sigma_sd=max(sig, 1.0), dobra_przyczepnosc=dobra, proc_laczonych=100)
                spos, E_, R_, sE, sR = f"U-pręty φ{pas.fi} na końcu (zakład l₀)", zkU.l_0 / 1000, L_in + max(l_av, 0.0), "l₀", "l_cięgna"
            pas.zakotwienie.append({"strona": sgn, "l_av": l_av, "l_bd": lbd, "sposob": spos, "l_req": E_, "F": F_end,
                                    "dobra": dobra})
            konc = "prawy/górny" if sgn > 0 else "lewy/dolny"
            w.warunek(f"Zakotwienie „{pas.opis}” — koniec {konc}, F = {f(F_end, 1)} kN: {spos}", E_ * 1000, R_ * 1000, "mm",
                      "8.4.4, 8.7.3, 6.5.4(7)", nd=0, symbol_E=sE, symbol_R=sR)

    # ---------------------------------------------------------------------------------------------
    # 6. Krzyżulce i węzły (6.5.2, 6.5.4)
    # ---------------------------------------------------------------------------------------------
    def _szerokosci_wezlow(self):
        """Długości przypisane węzłom wzdłuż pasa (l_row) i kolumny (l_col) oraz głębokość pasa u = 2a."""
        W = self.stm.wezly
        n = len(W)
        l_row = np.full(n, self.dx_stm)
        l_col = np.full(n, self.dz_stm)
        Pb = self.P.buffer(1e-3)
        for axis, arr in ((0, l_row), (1, l_col)):
            other = 1 - axis
            keys = np.round(W[:, other], 5)
            for kv in np.unique(keys):
                idx = np.nonzero(keys == kv)[0]
                idx = idx[np.argsort(W[idx, axis])]
                for j, k in enumerate(idx):
                    dl = dr = None
                    if j > 0 and Pb.contains(LineString([tuple(W[idx[j - 1]]), tuple(W[k])])):
                        dl = W[k, axis] - W[idx[j - 1], axis]
                    if j < len(idx) - 1 and Pb.contains(LineString([tuple(W[k]), tuple(W[idx[j + 1]])])):
                        dr = W[idx[j + 1], axis] - W[k, axis]
                    vals = [v for v in (dl, dr) if v is not None]
                    if vals:
                        arr[k] = sum(v / 2 for v in vals) if len(vals) == 2 else vals[0] / 2 + 0.1
        return l_row, l_col

    def _krzyzulce_wezly(self):
        m, b, d = self.stm, self.beton, self.d
        nu_p = 1 - b.f_ck / 250
        fcd = b.f_cd
        sRd_strut = 0.6 * nu_p * fcd
        l_row, l_col = self._szerokosci_wezlow()
        self.l_row, self.l_col = l_row, l_col
        t = d.t
        wyn_s = Wynik(nazwa="Model kratownicowy — krzyżulce ściskane (6.5.2)")
        wyn_n = Wynik(nazwa="Model kratownicowy — węzły (6.5.4) i docisk")
        best_s, best_n = {}, {}
        typ_wezla_gov = {}

        def szer(k, ang_rad):
            inf = m.info[k]
            s_, c_ = abs(math.sin(ang_rad)), abs(math.cos(ang_rad))
            if inf["h"] is not None:
                u = 2 * inf["h"][2]
                l_ = max(m.l_docisku[k], l_row[k]) if m.l_docisku[k] > 1e-6 else l_row[k]
                return l_ * s_ + u * c_
            if inf["v"] is not None:
                u = 2 * inf["v"][2]
                return l_col[k] * c_ + u * s_
            return min(l_row[k], l_col[k])
        for n, F in m.F.items():
            Fmax = max(float(np.abs(F).max()), 1e-9)
            # krzyżulce: bez rozciągania poprzecznego (σ₁ z MES w środku krzyżulca ≤ f_ctd) — f_cd (6.55), w strefie
            # zarysowanej — 0,6·ν'·f_cd (6.56)
            rr = self.r_uls[n]
            for k in np.nonzero(F < -0.01 * Fmax)[0]:
                ang = math.atan2(m.U[k, 1], m.U[k, 0])
                wi, wj = szer(m.ii[k], ang), szer(m.jj[k], ang)
                wmin = max(min(wi, wj), 0.02)
                sig = -F[k] / (t * wmin) / 1000
                sg = self.mes.naprezenia_xy(rr, *(0.5 * (m.wezly[m.ii[k]] + m.wezly[m.jj[k]])))
                s1m = glowne(sg[None])[0][0] / 1000 if sg is not None else 0.0
                lim = fcd if s1m <= b.f_ctd else sRd_strut
                eta = sig / lim
                if k not in best_s or eta > best_s[k][0]:
                    best_s[k] = (eta, n, -F[k], wmin, sig, lim, s1m)
            # węzły
            Pn = m.P[n]
            Rw = m.Rw[n]
            for k in range(len(m.wezly)):
                inc = np.nonzero((m.ii == k) | (m.jj == k))[0]
                inc = inc[np.abs(F[inc]) > 0.02 * Fmax]
                if len(inc) == 0:
                    continue
                ties = [q for q in inc if F[q] > 0]
                dirs = []
                for q in ties:
                    a = math.degrees(math.atan2(m.U[q, 1], m.U[q, 0])) % 180
                    if not any(min(abs(a - d_), 180 - abs(a - d_)) < 15 for d_ in dirs):
                        dirs.append(a)
                typ = "CCC" if not dirs else ("CCT" if len(dirs) == 1 else "CTT")
                sigs = []
                for q in inc:
                    if F[q] < 0:
                        ang = math.atan2(m.U[q, 1], m.U[q, 0])
                        sigs.append(-F[q] / (t * max(szer(k, ang), 0.02)) / 1000)
                Rk = Rw[k, 1]
                if Rk > 1e-6 and m.l_docisku[k] > 1e-6:
                    sigs.append(Rk / (t * m.l_docisku[k]) / 1000)
                Pk = -Pn[k, 1] - (Rk if Rk > 0 else 0.0)
                if Pk > 5.0:
                    ls = next((o.dl_docisku for o in d.obciazenia if isinstance(o, ObcSkupione)
                               and abs(o.s - m.wezly[k, 0]) < 0.05), None)
                    if ls:
                        sigs.append(Pk / (t * ls) / 1000)
                if not sigs:
                    continue
                s_ = max(sigs)
                lim = K_WEZLA[typ] * nu_p * fcd
                eta = s_ / lim
                if k not in best_n or eta > best_n[k][0]:
                    best_n[k] = (eta, n, typ, s_, lim, Rk)
                typ_wezla_gov.setdefault(n, {})[k] = typ
        self.typ_wezla = typ_wezla_gov
        wyn_s.krok("Nośność krzyżulców w strefie zarysowanej (rozciąganie poprzeczne, σ₁ > f_ctd)", "σ_Rd,max = 0,6·ν'·f_cd, "
                   "ν' = 1 − f_ck/250", f"0,6·{f(nu_p, 3)}·{f(fcd, 2)}", sRd_strut, "MPa", zrodlo="(6.56), (6.57N)")
        wyn_s.krok("Krzyżulce bez rozciągania poprzecznego (σ₁ z MES ≤ f_ctd, np. pasy ściskane)", "σ_Rd,max = f_cd", "", fcd, "MPa",
                   zrodlo="(6.55)")
        wyn_s.krok("Szerokość krzyżulca na końcu", "w = l·sin θ + u·cos θ (węzeł na pasie: l — długość docisku/pasa, u = 2a); "
                   "węzeł wewnętrzny: w = rozstaw węzłów [UPR]", "", "")
        top = sorted(best_s.items(), key=lambda kv: -kv[1][0])[:8]
        rows = []
        self.C_max = max((v[2] for v in best_s.values()), default=0.0)
        for k, (eta, n, C, wmin, sig, lim, s1m) in top:
            pa, pb = m.wezly[m.ii[k]], m.wezly[m.jj[k]]
            ang = math.degrees(math.atan2(pb[1] - pa[1], pb[0] - pa[0]))
            rows.append([f"({f(pa[0])}; {f(pa[1])})–({f(pb[0])}; {f(pb[1])})", f(abs(ang) if abs(ang) <= 90 else 180 - abs(ang), 0) + "°",
                         (C, 1), (wmin * 1000, 0), (s1m, 2), (sig, 2), (lim, 2), f"{f(eta * 100, 0)}%", n])
        if top:
            k, (eta, n, C, wmin, sig, lim, s1m) = top[0]
            wyn_s.warunek(f"Krzyżulec miarodajny (C = {f(C, 1)} kN, w = {f(wmin * 1000, 0)} mm, σ₁ = {f(s1m, 2)} MPa)", sig, lim, "MPa",
                          "(6.55)" if lim == fcd else "(6.56)", symbol_E="σ_Ed", symbol_R="σ_Rd,max")
        self.tabele.append("**Krzyżulce ściskane — najbardziej wytężone (obwiednia kombinacji STR)**\n\n" + tabela(
            ["Krzyżulec (x; z) [m]", "kąt", "C [kN]", "w [mm]", "σ₁ MES [MPa]", "σ_Ed [MPa]", "σ_Rd,max [MPa]", "η", "Kombinacja"], rows))
        self.sekcje.append(wyn_s)
        # węzły
        for typ, k_ in K_WEZLA.items():
            wyn_n.krok(f"Nośność węzła {typ}", f"σ_Rd,max = k·ν'·f_cd, k = {f(k_, 2)}", f"{f(k_, 2)}·{f(nu_p, 3)}·{f(fcd, 2)}",
                       k_ * nu_p * fcd, "MPa", zrodlo={"CCC": "(6.60)", "CCT": "(6.61)", "CTT": "(6.62)"}[typ])
        topn = sorted(best_n.items(), key=lambda kv: -kv[1][0])
        podp = [kv for kv in topn if kv[1][5] > 1e-6]
        sel = topn[:6] + [kv for kv in podp[:6] if kv not in topn[:6]]
        rows = []
        for k, (eta, n, typ, s_, lim, Rk) in sel:
            rows.append([f"({f(m.wezly[k, 0])}; {f(m.wezly[k, 1])})", typ, (Rk, 1) if Rk > 1e-6 else "—",
                         (m.l_docisku[k] * 1000, 0) if Rk > 1e-6 else "—", (s_, 2), (lim, 2), f"{f(eta * 100, 0)}%", n])
        if topn:
            k, (eta, n, typ, s_, lim, Rk) = topn[0]
            wyn_n.warunek(f"Węzeł miarodajny {typ} ({f(m.wezly[k, 0])}; {f(m.wezly[k, 1])})", s_, lim, "MPa",
                          "6.5.4(4)", symbol_E="σ_Ed", symbol_R="σ_Rd,max")
        if podp:
            k, (eta, n, typ, s_, lim, Rk) = podp[0]
            if k != topn[0][0]:
                wyn_n.warunek(f"Węzeł podporowy {typ} ({f(m.wezly[k, 0])}; {f(m.wezly[k, 1])}), R = {f(Rk, 1)} kN", s_, lim, "MPa",
                              "6.5.4(4)", symbol_E="σ_Ed", symbol_R="σ_Rd,max")
        self.tabele.append("**Węzły STM — najbardziej wytężone i podporowe** (σ_Ed — maks. z docisku i czół krzyżulców)\n\n" + tabela(
            ["Węzeł (x; z) [m]", "Typ", "R [kN]", "l_docisku [mm]", "σ_Ed [MPa]", "σ_Rd,max [MPa]", "η", "Kombinacja"], rows))
        self.sekcje.append(wyn_n)

    # ---------------------------------------------------------------------------------------------
    # 7. Otwory — pręty ukośne i obwodowe
    # ---------------------------------------------------------------------------------------------
    def _otwory(self):
        d, st = self.d, self.stal
        if not d.otwory:
            return
        w = Wynik(nazwa="Zbrojenie przy otworach — pręty ukośne w narożach i obwodowe")
        fi = d.fi_otwory
        A2 = 4 * pole_preta(fi)        # 2 pręty przy każdej powierzchni
        rows = []
        self.naroza = []
        Fmax_all = 0.0
        for o in d.otwory:
            for (x, z, bx, bz) in ((o.s0, o.z1, -1, 1), (o.s1, o.z1, 1, 1), (o.s0, o.z0, -1, -1), (o.s1, o.z0, 1, -1)):
                kier = np.array([bx, bz]) / math.sqrt(2)
                Lc = min(0.8, _dl_promienia(self.P, (x + bx * 1e-4, z + bz * 1e-4), kier))
                if Lc < 0.05:
                    continue
                best = (0.0, "")
                for n, r in self.r_uls.items():
                    c = self.mes.przekroj_linia(r, (x + bx * 1e-4, z + bz * 1e-4), (x + kier[0] * Lc, z + kier[1] * Lc), n=48)
                    if c["Ft"] > best[0]:
                        best = (c["Ft"], n)
                Fd = best[0]
                Fmax_all = max(Fmax_all, Fd)
                req = Fd * 1000 / st.f_yd
                nazwa = f"{o.id} naroże {'górne' if bz > 0 else 'dolne'} {'lewe' if bx < 0 else 'prawe'}"
                self.naroza.append({"otwor": o.id, "xy": (x, z), "kier": (bx, bz), "F": Fd, "k": best[1], "As_req": req})
                rows.append([nazwa, (Lc, 2), (Fd, 1), (req, 0), f"4φ{fi}", (A2, 0), f"{f(req / A2 * 100, 0)}%"])
                w.warunek(f"Pręty ukośne — {nazwa}", req, A2, "mm²", "MES: przekrój wzdłuż dwusiecznej naroża; 6.5.3",
                          nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
        w.krok("Siła rozciągająca w poprzek potencjalnej rysy z naroża", "F_t = ∫max(σ_nn; 0)·t ds (przekrój wzdłuż dwusiecznej, "
               "l ≤ 0,8 m, obwiednia ULS)", "", Fmax_all, "kN", zrodlo="MES [UPR]; praktyka: ≥ 2φ12 przy każdej powierzchni")
        w.krok("Przyjęto w każdym narożu pręty ukośne 45°", f"2φ{fi} przy każdej powierzchni (4φ{fi})", "", A2, "mm²", nd=0)
        w.krok("Pręty obwodowe wzdłuż krawędzi otworów (zastępują przerwaną siatkę; nadproża i podokienniki — cięgna wyżej)",
               f"2φ{fi} przy każdej powierzchni, zakotwione l_bd poza narożem", "", "")
        self.tabele.append("**Naroża otworów — siły w poprzek rysy z naroża (MES) i pręty ukośne**\n\n" + tabela(
            ["Naroże", "l_przekroju [m]", "F_t [kN]", "A_s,req [mm²]", "Przyjęto", "A_s,prov [mm²]", "η"], rows))
        self.sekcje.append(w)
        self.przyjeto.append(f"Otwory: w każdym narożu 2φ{fi} ukośne przy każdej powierzchni (l ≈ 2·l_bd), wzdłuż krawędzi "
                             f"otworów 2φ{fi} obwodowe przy każdej powierzchni zakotwione poza narożami.")

    # ---------------------------------------------------------------------------------------------
    # 8. SLS — ugięcia (sztywność zarysowana, pełzanie)
    # ---------------------------------------------------------------------------------------------
    def punkty_ugiec(self) -> list[dict]:
        """Wsporniki (końce poza skrajnymi podporami) i przęsła między podporami (przerwy > 0,5 m)."""
        d = self.d
        x_min, x_max = self.mes.gx[0], self.mes.gx[-1]
        pod = sorted([s for s in d.podpory], key=lambda s: s.s0)
        out = []
        if pod:
            s0 = min(s.s0 for s in pod)
            s1 = max(s.s1 for s in pod)
            if s0 - x_min > 0.3:
                out.append({"typ": "wspornik", "x": x_min, "x_t": s0, "l": s0 - x_min, "opis": f"wspornik ({d.kierunki[0]})"})
            if x_max - s1 > 0.3:
                out.append({"typ": "wspornik", "x": x_max, "x_t": s1, "l": x_max - s1, "opis": f"wspornik ({d.kierunki[1]})"})
            for a, b_ in zip(pod[:-1], pod[1:]):
                if b_.s0 - a.s1 > 0.5:
                    out.append({"typ": "przeslo", "x": 0.5 * (a.s1 + b_.s0), "xa": a.s1, "xb": b_.s0, "l": b_.s0 - a.s1,
                                "opis": f"przęsło między podporami {a.id}–{b_.id}"})
        return out

    def _ugiecie_pkt(self, r: WynikT, pk: dict) -> float:
        """Ugięcie względne [m] (dodatnie w dół): wspornik — koniec względem krawędzi podpory; przęsło — środek względem
        cięciwy. Średnia z krawędzi dolnej i górnej przekroju."""
        mes = self.mes

        def uz_sr(x):
            vals = []
            for z in (mes.gz[0], mes.gz[-1], 0.5 * (mes.gz[0] + mes.gz[-1])):
                e = mes.element_w(x, z)
                if e is not None:
                    vals.append(mes.przemieszczenie(r, x, z)[1])
            if not vals:
                d_ = np.abs(mes.nodes[:, 0] - x)
                k = np.argsort(d_)[:4]
                vals = list(r.u[2 * k + 1])
            return float(np.mean(vals))
        if pk["typ"] == "wspornik":
            return -(uz_sr(pk["x"] if pk["x"] < pk["x_t"] else pk["x"] - 1e-6) - uz_sr(pk["x_t"]))
        return -(uz_sr(pk["x"]) - 0.5 * (uz_sr(pk["xa"]) + uz_sr(pk["xb"])))

    def _sls(self):
        d, p, b, st = self.d, self.p, self.beton, self.stal
        pk_list = self.punkty_ugiec()
        self.ugiecia = []
        if not pk_list:
            return
        w = Wynik(nazwa="Stan graniczny ugięć tarczy (7.4) — MES ze sztywnością zarysowaną i pełzaniem")
        Ec = b.E_cm * 1000
        Eeff = Ec / (1 + p.fi_pelzania)
        w.krok("Efektywny moduł betonu (quasi-stała, t = ∞)", "E_c,eff = E_cm/(1 + φ)", f"{f(b.E_cm, 0)}/(1 + {f(p.fi_pelzania, 1)})",
               Eeff / 1000, "MPa", nd=0, zrodlo="(7.20)")
        mes = self.mes
        # zarysowanie: zasięg z kombinacji charakterystycznej (E_cm, stan niezarysowany)
        rc = self.r_char[self.k_char_gov]
        s1c, _, thc = glowne(rc.sig)
        fctm = b.f_ctm * 1000
        rys = s1c > fctm
        zeta = np.where(rys, 1 - 0.5 * (fctm / np.maximum(s1c, 1e-9)) ** 2, 0.0)
        # zbrojenie rozmyte: siatki + cięgna w pasmach u = 2a przy krawędziach
        rho0 = 2 * self.siatka_As / (d.t * 1e6)
        rx = np.full(mes.ne, rho0)
        rz = np.full(mes.ne, rho0)
        for pas in self.pasy:
            e = pas.krawedz
            if e is None:
                continue
            u = max(2 * pas.a, 2.5 * (self.c_nom + pas.fi / 2000), 0.12)
            if e.typ == "h":
                z0, z1 = sorted((e.wsp, e.wsp + e.strona * u))
                msk = (mes.el_c[:, 1] > z0) & (mes.el_c[:, 1] < z1) & (mes.el_c[:, 0] > pas.zakres[0] - 0.3) & (mes.el_c[:, 0] < pas.zakres[1] + 0.3)
                rx[msk] += pas.As_prov / (d.t * u * 1e6)
            else:
                x0, x1 = sorted((e.wsp, e.wsp + e.strona * u))
                msk = (mes.el_c[:, 0] > x0) & (mes.el_c[:, 0] < x1) & (mes.el_c[:, 1] > pas.zakres[0] - 0.3) & (mes.el_c[:, 1] < pas.zakres[1] + 0.3)
                rz[msk] += pas.As_prov / (d.t * u * 1e6)
        self.rho_x, self.rho_z = rx, rz
        self.n_rys = int(rys.sum())
        w.krok("Zasięg zarysowania (kombinacja charakterystyczna, σ₁ > f_ctm)", "n_el,zar / n_el", f"{self.n_rys}/{mes.ne}",
               f"{f(self.n_rys / mes.ne * 100, 1)} %", zrodlo="[UPR]")
        # sprężyny podpór — pełzanie muru
        kf = 1.0 / (1.0 + d.fi_podpor)

        def rozwiaz_dl(wsp, E_c, zarys: bool):
            E_el = mes.E_el / self.beton.E_cm / 1000 * E_c
            D = np.array(mes.D_domyslne(E_el))
            D[:, 0, 0] += rx * p.E_s * 1000            # zbrojenie rozmyte także w stanie niezarysowanym (przekrój sprowadzony)
            D[:, 1, 1] += rz * p.E_s * 1000
            if zarys and rys.any():
                D[rys] = D_zarysowany(E_c, p.nu_beton, thc[rys], rx[rys], rz[rys], p.E_s * 1000, zeta[rys])
            ks = {}
            for s in mes.podpory:
                ks[s.id] = mes.pod_k[s.id]
                if mes.pod_k[s.id] is not None and E_c < Ec - 1:
                    mes.pod_k[s.id] = mes.pod_k[s.id] * kf
            try:
                mes._lu_cache.clear()
                r = mes.rozwiaz(mes.wektor(wsp), D_el=D)
            finally:
                for s in mes.podpory:
                    mes.pod_k[s.id] = ks[s.id]
                mes._lu_cache.clear()
            return r
        kq = self.kmap[self.k_qp_gov]
        kG = {d.przypadek_cw: 1.0, **{o.nazwa: 1.0 for o in self.odz if o.rodzaj in ("G",)}}
        r_qp_I = rozwiaz_dl(kq.wsp, Eeff, False)
        r_qp_II = rozwiaz_dl(kq.wsp, Eeff, True)
        r_G0 = rozwiaz_dl(kG, Ec, False)
        self.r_qp_II = r_qp_II
        rows = []
        gov = None
        for pk in pk_list:
            wI = self._ugiecie_pkt(r_qp_I, pk) * 1000
            wII = self._ugiecie_pkt(r_qp_II, pk) * 1000
            w0 = self._ugiecie_pkt(r_G0, pk) * 1000
            if pk["typ"] == "wspornik":
                Lref = p.wspornik_L_mnoznik * pk["l"]
            else:
                Lref = pk["l"]
            wdop = Lref * 1000 / p.ugiecie_mian
            winc_dop = Lref * 1000 / p.ugiecie_przyrost_mian
            winc = max(wII - w0, 0.0)
            pk.update({"w_I": wI, "w_II": wII, "w_0": w0, "w_dop": wdop, "w_inc": winc, "w_inc_dop": winc_dop, "L_ref": Lref})
            self.ugiecia.append(pk)
            rows.append([pk["opis"], (pk["l"], 2), (Lref, 2), (wI, 2), (wII, 2), (wdop, 1), (winc, 2), (winc_dop, 1)])
            w.warunek(f"Ugięcie — {pk['opis']} (quasi-stała, t = ∞, zarysowanie)", abs(wII), wdop, "mm",
                      "7.4.1(4); L = 2·l_k dla wspornika (R5-56)" if pk["typ"] == "wspornik" else "7.4.1(4)", nd=2,
                      symbol_E="w", symbol_R="L/250")
            w.warunek(f"Przyrost ugięcia — {pk['opis']} (po wykonaniu wykończeń)", winc, winc_dop, "mm", "7.4.1(5) [NZW]", nd=2,
                      symbol_E="Δw", symbol_R="L/500")
            if gov is None or abs(wII) / wdop > gov[0]:
                gov = (abs(wII) / wdop, abs(wII), wdop)
        self.w_gov = gov
        w.krok("Ugięcia względne: wspornik — koniec względem krawędzi podpory (z obrotem podpory sprężystej), przęsło — środek "
               "względem cięciwy; w_I — niezarysowane, w_II — zarysowane (ζ = 1 − 0,5·(f_ctm/σ₁)², rysy rozmyte) [UPR]",
               "", "", "")
        w.krok("Przyrost ugięcia po wykonaniu wykończeń", "Δw = w_II(qp, ∞) − w_0(G, t₀)", "", "", zrodlo="[UPR]")
        w.krok("Krzywizna skurczowa (7.21) dla tarczy o wysokości H ≈ " + f(d.H, 2) + " m pomijalna (≈ ε_cs·α_e·S/I·l² < 0,1 mm)",
               "", "", "")
        self.tabele.append("**Ugięcia tarczy (SLS)** — w [mm], dodatnie w dół\n\n" + tabela(
            ["Miejsce", "l [m]", "L_ref [m]", "w_I (qp, ∞)", "w_II (qp, ∞, zarys.)", "w_lim = L/250", "Δw", "Δw_lim = L/500"], rows))
        self.sekcje.append(w)

    # ---------------------------------------------------------------------------------------------
    # 9. EQU — równowaga statyczna wspornika
    # ---------------------------------------------------------------------------------------------
    def _momenty_przypadkow(self, x_t: float, strona: int) -> dict:
        """{przypadek: (M_dst, M_stb)} względem krawędzi obrotu x_t [kNm]; strona −1 — wspornik po stronie x < x_t."""
        mes = self.mes
        out = {}
        for c in mes.przypadki():
            fz = -mes.wektor({c: 1.0})[1::2]         # obciążenia w dół dodatnie
            ramie = (mes.nodes[:, 0] - x_t) * (-strona)   # >0 po stronie stabilizującej
            M = fz * ramie
            out[c] = (float(-M[M < 0].sum()), float(M[M > 0].sum()))
        return out

    def _equ(self):
        p = self.p
        pk = [q for q in self.punkty_ugiec() if q["typ"] == "wspornik"]
        self.eta_equ = 0.0
        if not pk:
            return
        w = Wynik(nazwa="Równowaga statyczna wspornika tarczy (EQU)")
        for q in pk:
            strona = -1 if q["x"] < q["x_t"] else 1
            mom = self._momenty_przypadkow(q["x_t"], strona)
            Gd = sum(v[0] for c, v in mom.items() if self.d.przypadki[c].rodzaj == "G")
            Gs = sum(v[1] for c, v in mom.items() if self.d.przypadki[c].rodzaj == "G")
            Qs = [(c, v[0]) for c, v in mom.items() if self.d.przypadki[c].rodzaj == "Q"]
            best = (0.0, "—")
            for c, Md in Qs:
                o = self.d.przypadki[c]
                tot = p.EQU_gQ * Md
                for c2, Md2 in Qs:
                    o2 = self.d.przypadki[c2]
                    if c2 == c or (o.grupa and o2.grupa == o.grupa):
                        continue
                    tot += p.EQU_gQ * p.psi_of(o2.kat)[0] * Md2
                if tot > best[0]:
                    best = (tot, c)
            Ed = p.EQU_gG_dst * Gd + best[0]
            Es = p.EQU_gG_stb * Gs
            w.krok(f"{q['opis'].capitalize()}: krawędź obrotu x = {f(q['x_t'], 2)} m (skraj podpory), wysięg {f(q['l'], 2)} m", "", "", "")
            w.krok("Moment destabilizujący", "M_dst = 1,10·M_G,dst + 1,5·M_Q,dst (+ 1,5·ψ₀·M_Q,i)",
                   f"1,10·{f(Gd, 2)} + {f(best[0], 2)} (wiodące: {best[1]})", Ed, "kNm", zrodlo="PN-EN 1990 tabl. A1.2(A)")
            w.krok("Moment stabilizujący", "M_stb = 0,90·M_G,stb", f"0,90·{f(Gs, 2)}", Es, "kNm")
            w.warunek(f"EQU — {q['opis']}", Ed, Es, "kNm", "PN-EN 1990 (6.7), tabl. A1.2(A)", symbol_E="M_Ed,dst", symbol_R="M_Ed,stb")
            self.eta_equ = max(self.eta_equ, Ed / max(Es, 1e-9))
        # odrywanie podpór (ULS, MES)
        rmin = []
        for n, r in self.r_uls.items():
            for sid, rr in self.mes.reakcje(r).items():
                rmin.append((float(rr["Rw"].min()), sid, n, rr))
        mn = min(rmin, key=lambda t_: t_[0])
        if mn[0] < -1e-3:
            neg = float(-mn[3]["Rw"][mn[3]["Rw"] < 0].sum())
            w.uwaga(f"MES: reakcje rozciągające na podporze {mn[1]} ({mn[2]}): Σ = {f(neg, 1)} kN — wymagane zakotwienie tarczy "
                    f"w elemencie poniżej: A_s ≥ {f(neg * 1000 / self.stal.f_yd, 0)} mm² (pręty startowe z wieńca, l_bd w obu elementach).")
        else:
            w.krok("MES: reakcje podpór we wszystkich kombinacjach STR ściskające (brak odrywania)", "min R_węzeł", "", mn[0], "kN")
        self.sekcje.append(w)

    # ---------------------------------------------------------------------------------------------
    # 10. Zestawienie stali
    # ---------------------------------------------------------------------------------------------
    def _zestawienie_stali(self):
        d = self.d
        prety = []
        nr = 1
        el = f"Tarcza {d.id}"
        for pas in self.pasy:
            if pas.krawedz is None or pas.n == 0:
                continue
            L_ = pas.zakres[1] - pas.zakres[0]
            ext, u_bars = 0.0, []
            for z_ in pas.zakotwienie:
                if z_["sposob"] == "proste":
                    ext += z_["l_req"]
                elif z_["sposob"].startswith("hak"):
                    ext += z_["l_req"] + 10 * pas.fi / 1000
                else:
                    ext += max(z_["l_av"], 0.0)
                    u_bars.append(z_["l_req"])
            dl = round(L_ + ext, 2)
            ksz = "00" if all(z_["sposob"] == "proste" for z_ in pas.zakotwienie) else "11"
            prety.append(zelbet.Pret(el, nr, pas.fi, dl, pas.n, ksz, f"cięgno: {pas.opis}"))
            nr += 1
            for l0 in u_bars:
                prety.append(zelbet.Pret(el, nr, pas.fi, round(2 * l0 + d.t - 2 * self.c_nom, 2), pas.n // 2, "21",
                                         f"U-pręt końcowy cięgna: {pas.opis}"))
                nr += 1
            zak = "; ".join(z_["sposob"] for z_ in pas.zakotwienie) or "l_bd"
            self.przyjeto.append(f"Cięgno „{pas.opis}”: {pas.n}φ{pas.fi} ({pas.n // 2} przy każdej powierzchni), oś {f(pas.a * 100, 0)} cm "
                                 f"od krawędzi, na odcinku {f(pas.zakres[0], 2)}…{f(pas.zakres[1], 2)} m + zakotwienie ({zak}).")
        # siatki (liczba prętów zmniejszona proporcjonalnie do pola otworów — orientacyjnie)
        frac = self.P.area / (d.L * d.H)
        s = self.siatka_s / 1000
        n_h = int(round((int(math.ceil(d.H / s)) + 1) * frac))
        n_v = int(round((int(math.ceil(d.L / s)) + 1) * frac))
        prety.append(zelbet.Pret(el, nr, self.siatka_fi, round(d.L - 2 * self.c_nom, 2), 2 * n_h, "00",
                                 f"siatka pozioma co {self.siatka_s} mm (2 pow.)"))
        nr += 1
        prety.append(zelbet.Pret(el, nr, self.siatka_fi, round(d.H - 2 * self.c_nom + 0.4, 2), 2 * n_v, "00",
                                 f"siatka pionowa co {self.siatka_s} mm (2 pow., z zakładem 0,4 m)"))
        nr += 1
        fi = d.fi_otwory
        lbd = zelbet.zakotwienie(fi, self.beton, self.stal).l_bd / 1000
        for o in d.otwory:
            prety.append(zelbet.Pret(el, nr, fi, round(o.szer + 2 * lbd, 2), 8, "00", f"obwodowe poziome {o.id}"))
            nr += 1
            prety.append(zelbet.Pret(el, nr, fi, round(o.wys + 2 * lbd, 2), 8, "00", f"obwodowe pionowe {o.id}"))
            nr += 1
            prety.append(zelbet.Pret(el, nr, fi, round(2 * lbd, 2), 16, "00", f"ukośne w narożach {o.id}"))
            nr += 1
        self.prety = prety
        self.masa_stali = zelbet.masa_stali(prety)

    # ---------------------------------------------------------------------------------------------
    # Wynik
    # ---------------------------------------------------------------------------------------------
    def wynik(self) -> WynikTarczy:
        d = self.d
        wt = WynikTarczy(nazwa=f"Ściana-tarcza {d.id}", L=d.L, H=d.H, t=d.t, beton=self.beton.klasa, n_elementow=self.mes.ne,
                         kombinacja_miarodajna=self.k_gov)
        s1 = self.s1_env / 1000
        s2 = self.s2_env / 1000
        wt.sigma1_max, wt.sigma2_min = float(s1.max()), float(s2.min())
        wt.T_max = getattr(self, "T_max", 0.0)
        wt.C_max = getattr(self, "C_max", 0.0)
        if getattr(self, "w_gov", None):
            wt.w_max, wt.w_dop = self.w_gov[1], self.w_gov[2]
        wt.eta_EQU = self.eta_equ
        wt.masa_stali = getattr(self, "masa_stali", 0.0)
        r = self.r_uls[self.k_gov]
        wt.sum_R = float(r.R[1::2].sum())
        wt.blad_rownowagi = self.blad_rownowagi
        for s in self.sekcje:
            wt.dolacz(s, s.nazwa)
        for u in self.uwagi:
            wt.uwaga(u)
        wt.an = self
        return wt


def oblicz_tarcze(dane: DaneTarczy, p: Parametry | None = None, stal: StalZbrojeniowa | None = None, siatka: float = 0.10,
                  stm: bool = True, sls: bool = True) -> WynikTarczy:
    """Obliczenia tarczy (MES → STM → wymiarowanie → SLS → EQU). Zwraca :class:`WynikTarczy` (``.an`` — analiza)."""
    return AnalizaTarczy(dane, p, stal, siatka).uruchom(stm=stm, sls=sls).wynik()


# ==================================================================================================
# Pozycja „Obliczeń statycznych” i raport
# ==================================================================================================
METODA_TARCZ = [
    "MES płaskiego stanu naprężenia: element prostokątny QM6 (biliniowy + 4 mody niekonforemne, kondensacja statyczna) na "
    "siatce ortogonalnej dopasowanej do krawędzi otworów, podpór i punktów przyłożenia obciążeń; beton niezarysowany "
    "E_cm, ν = 0,2; podpory sprężyste k = E·t/h ściany poniżej (lub sztywne). Walidacja: rozwiązanie ścisłe Timoshenki–"
    "Goodiera (belka-tarcza, obciążenie równomierne), wspornik smukły (teoria belek z odkształceniem postaciowym), "
    "zbieżność siatki, równowaga sił i przekrojów (tarcze_walidacja).",
    "Siły w pasach: całkowanie naprężeń σ w przekrojach co element — wypadkowa strefy rozciąganej przylegającej do krawędzi "
    "(pas górny/dolny, nadproża, podokienniki, ościeża).",
    "Model kratownicowy (5.6.4, 6.5): węzły na liniach pasów (odsunięcie od krawędzi = środek bloku naprężeń z MES), pręty "
    "kandydujące w obrębie betonu, siły z programowania liniowego (minimum Σ c·|F|·l, cięgna 1,0, krzyżulce 0,3, kara za "
    "niezgodność z polem sprężystym), obciążenia i reakcje z MES (dokładna równowaga); obwiednia kombinacji STR.",
    "Wymiarowanie: cięgna F_Ed = max(STM; MES), krzyżulce 0,6·ν'·f_cd, węzły CCC/CCT/CTT, zakotwienie (8.4), siatki 9.6/9.7, "
    "zał. F (środnik), pręty przy otworach, rysy (7.3.4), ugięcia MES ze sztywnością zarysowaną (rysy rozmyte, ζ wg 7.19) "
    "i pełzaniem, EQU wspornika (PN-EN 1990 tabl. A1.2(A)).",
]

ZRODLA_TARCZ = [
    "PN-EN 1992-1-1:2008 + AC:2011 + NA — p. 5.6.4, 6.5, 7.3, 7.4, 8.4, 8.7, 9.6, 9.7, zał. F [wartości zalecane — NZW NA]",
    "PN-EN 1990:2004 + NA — tabl. A1.2(A) (EQU), A1.2(B) (STR), 6.5.3 (SLS)",
    "S. Timoshenko, J.N. Goodier, Theory of Elasticity, 3rd ed., McGraw-Hill 1970, §22 (belka obciążona równomiernie — "
    "rozwiązanie wielomianowe) [P — wzory sprawdzane w teście: równania równowagi i warunki brzegowe]",
    "E.L. Wilson, R.L. Taylor, W.P. Doherty, J. Ghaboussi, Incompatible displacement models, 1973; R.L. Taylor, P.J. Beresford, "
    "E.L. Wilson, A non-conforming element for stress analysis, IJNME 10 (1976) 1211–1219 [P]",
    "J. Schlaich, K. Schäfer, M. Jennewein, Toward a Consistent Design of Structural Concrete, PCI Journal 32(3), 1987 [P]",
    "fib Bulletin 45 (2008) Practitioners' guide to finite element modelling of RC structures; fib Bulletin 61 (2011) Design "
    "examples for strut-and-tie models; fib Model Code 2010 §7.3 [P]",
    "F. Leonhardt, R. Walther, Wandartige Träger, DAfStb Heft 178 (1966); F. Leonhardt, E. Mönnig, Vorlesungen über Massivbau "
    "T. 2 (1975); DAfStb Heft 240 (1991) — ramię sił wewnętrznych belek-ścian [P]",
    "W.S. Dorn, R.E. Gomory, H.J. Greenberg, Automatic design of optimal structures, J. de Mécanique 3 (1964) [P]",
    "A. Muttoni, J. Schwartz, B. Thürlimann, Design of Concrete Structures with Stress Fields, Birkhäuser 1997 [P]",
]


def _tabela_obciazen(d: DaneTarczy) -> str:
    rows = []
    for o in d.obciazenia:
        if isinstance(o, ObcLiniowe):
            q1 = o.q0 if o.q1 is None else o.q1
            rows.append([o.przypadek, o.opis or "liniowe", f"{f(o.s0)}…{f(o.s1)}", f(o.z), f"{f(o.q0)}" + (f" → {f(q1)}" if q1 != o.q0 else ""),
                         (o.wypadkowa, 1)])
        elif isinstance(o, ObcProfil):
            rows.append([o.przypadek, o.opis or "profil", f"{f(o.s0)}…{f(o.s1)}", f(o.z),
                         f"śr. {f(o.wypadkowa / max(o.s1 - o.s0, 1e-9))} (maks. {f(float(o.q.max()))})", (o.wypadkowa, 1)])
        else:
            rows.append([o.przypadek, o.opis or "skupione", f(o.s), f(o.z), f"P = {f(o.P)} kN" + (f", P_x = {f(o.Px)}" if o.Px else ""),
                         (o.P, 1)])
    W = (d.gamma * d.t + d.g_dod) * d.polygon().area
    rows.append([d.przypadek_cw, f"ciężar własny: {f(d.gamma, 0)}·{f(d.t)} + {f(d.g_dod)} = {f(d.gamma * d.t + d.g_dod)} kN/m² "
                 f"× {f(d.polygon().area)} m²", "—", "—", "—", (W, 1)])
    return tabela(["Przypadek", "Obciążenie", "x [m]", "z [m]", "q [kN/m] / P", "Wypadkowa [kN]"], rows)


def _tabela_reakcji(an: AnalizaTarczy) -> str:
    pods = [s.id for s in an.d.podpory]
    rows = []
    for c, rr in an.reakcje_przyp.items():
        rows.append([c] + [f"{f(rr[s]['R'], 1)} (x_R = {f(rr[s]['xR'], 2)})" for s in pods] + [(sum(rr[s]["R"] for s in pods), 1)])
    rg = an.mes.reakcje(an.r_uls[an.k_gov])
    rows.append([f"**ULS {an.k_gov}**"] + [f"**{f(rg[s]['R'], 1)}**" for s in pods] + [(sum(rg[s]["R"] for s in pods), 1)])
    return tabela(["Przypadek (charakt.)"] + [f"{s} — R [kN]" for s in pods] + ["Σ [kN]"], rows)


def pozycja_tarczy(wt: WynikTarczy, rys_dir: str | Path | None = None, ident: str | None = None, tytul: str | None = None,
                   metoda: bool = True):
    """Pozycja „Obliczeń statycznych” (:class:`.pozycje.Pozycja`) z wyniku tarczy; rysunki zapisywane w rys_dir."""
    from .pozycje import Pozycja
    an: AnalizaTarczy = wt.an
    d = an.d
    pz = Pozycja("", ident or d.id, tytul or f"Ściana-tarcza żelbetowa {d.id}", "tarcza")
    otw = ", ".join(f"{o.id} {f(o.szer)}×{f(o.wys)} m (x = {f(o.s0)}…{f(o.s1)}, z = {f(o.z0)}…{f(o.z1)})" for o in d.otwory) or "brak"
    pod = "; ".join(f"{s.id}: x = {f(s.s0)}…{f(s.s1)} m" + (f" ({s.opis})" if s.opis else "") +
                    (", sztywna" if s.k is None else f", sprężysta k = {f(s.k / 1000, 0)} MN/m²") +
                    (", tylko docisk" if s.tylko_docisk else "") for s in d.podpory)
    wsp = [q for q in an.punkty_ugiec() if q["typ"] == "wspornik"]
    pz.opis.append(f"{d.opis + ' ' if d.opis else ''}Tarcza żelbetowa gr. t = {f(d.t * 100, 0)} cm, długość L = {f(d.L)} m "
                   f"(x = {f(d.x0)}…{f(d.x0 + d.L)}), wysokość H = {f(d.H)} m; beton {an.beton.klasa} ({d.ekspozycja}, c_nom = "
                   f"{f(an.c_nom * 1000, 0)} mm), stal {an.stal.gatunek} (f_yd = {f(an.stal.f_yd, 1)} MPa). Otwory: {otw}. "
                   f"Podpory (ściany/elementy poniżej): {pod}."
                   + (" Wsporniki: " + "; ".join(f"{q['opis']} l_k = {f(q['l'])} m" for q in wsp) + "." if wsp else ""))
    r = an.r_uls[an.k_gov]
    pz.opis.append(f"Model MES: {an.mes.ne} elementów QM6 (bok ≤ {f(an.siatka * 100, 0)} cm), {len(an.k_uls)} kombinacji STR"
                   + (f" + {len(an.k_wyj)} wyjątkowych" if an.k_wyj else "") + f", SLS: {len(an.k_char)} charakterystycznych, "
                   f"{len(an.k_qp)} quasi-stałych. Kombinacja miarodajna (maks. ΣF): {an.k_gov}; ΣF_z = {f(-float(r.f[1::2].sum()), 1)} kN, "
                   f"ΣR = {f(float(r.R[1::2].sum()), 1)} kN (błąd {an.blad_rownowagi:.1e}). Naprężenia (obwiednia STR): "
                   f"σ₁,max = {f(wt.sigma1_max)} MPa, σ₂,min = {f(wt.sigma2_min)} MPa (f_ctm = {f(an.beton.f_ctm, 1)}, "
                   f"f_cd = {f(an.beton.f_cd, 2)} MPa).")
    if metoda:
        pz.opis += [f"Metoda: {t}" for t in METODA_TARCZ]
    else:
        pz.opis.append("Metoda: MES tarczowy (QM6) → model kratownicowy STM z pola naprężeń → wymiarowanie wg PN-EN 1992-1-1 "
                       "(szczegóły — p. 0.5 „Metody obliczeń”).")
    pz.obciazenia.append("**Obciążenia charakterystyczne tarczy**\n\n" + _tabela_obciazen(d))
    pz.obciazenia.append("**Kombinacje STR (PN-EN 1990 + NA)**\n\n" + tabela(["Kombinacja", "Współczynniki"],
                                                                                 [[k.nazwa, k.opis()] for k in an.k_uls + an.k_wyj]))
    pz.obciazenia.append("**Reakcje podpór — przekazanie na ściany/wieńce poniżej** (charakterystyczne wg przypadków, liniowo; "
                         "rozkład wzdłuż podpory w danych pozycji i na rysunku)\n\n" + _tabela_reakcji(an))
    pz.wyniki = list(an.sekcje)
    pz.tabele = list(an.tabele)
    if rys_dir is not None:
        from .tarcze_rys import rysunki_tarczy
        pz.rysunki += rysunki_tarczy(an, Path(rys_dir))
    pz.przyjeto = list(an.przyjeto) + [f"Masa stali tarczy (orientacyjnie): {f(an.masa_stali, 0)} kg."]
    pz.uwagi = [f"[UPR/ZAŁ] {u}" for u in OGRANICZENIA_TARCZ] + list(an.uwagi)
    pz.prety = list(an.prety)
    pz.dane = {**wt.dane(),
               "reakcje_k": {c: {s: round(v["R"], 3) for s, v in rr.items()} for c, rr in an.reakcje_przyp.items()},
               "ciegna": [{"opis": q.opis, "F_Ed": round(q.F_Ed, 2), "F_STM": round(q.F_stm, 2), "F_MES": round(q.F_mes, 2),
                           "zbrojenie": f"{q.n}φ{q.fi}", "As_prov": round(q.As_prov, 1), "w_k": round(q.w_k, 3)} for q in an.pasy],
               "ugiecia": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in u.items()} for u in getattr(an, "ugiecia", [])]}
    return pz


def raport_tarczy(wt: WynikTarczy, out_dir: str | Path, tytul: str | None = None, status: str | None = None,
                  html: bool = True, dodatki: list[str] | None = None) -> Path:
    """Samodzielny raport pozycji tarczowej (markdown + rysunki w ``rys/`` + opcjonalnie HTML) w stylu „Obliczeń statycznych”."""
    import datetime as _dt
    import json

    from .raport import _HTML, _pozycja_md
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    an = wt.an
    pz = pozycja_tarczy(wt, out / "rys")
    pz.nr = "1"
    tytul = tytul or f"Obliczenia statyczne — ściana-tarcza {an.d.id}"
    L = [f"# {tytul}", "", f"Biblioteka `lamela.obliczenia.konstrukcja` (moduły `tarcze`, `tarcze_mes`) · wygenerowano "
         f"{_dt.date.today().isoformat()}", ""]
    if status:
        L += [f"> **{status}**", ""]
    L += ["> Obliczenia automatyczne. Oznaczenia: [NZW] — wartość zalecana/niezweryfikowana w NA, [UPR] — uproszczenie, "
          "[ZAŁ] — założenie, [P] — źródło przytoczone z pamięci. Wymagana weryfikacja projektanta z uprawnieniami.", ""]
    L += [f"**Wynik:** maks. wykorzystanie η = {f(pz.wykorzystanie * 100, 0)}% — "
          f"{'wszystkie warunki spełnione' if pz.ok else '**warunki niespełnione**'}; T_max = {f(wt.T_max, 1)} kN, "
          f"C_max = {f(wt.C_max, 1)} kN, ugięcie miarodajne {f(wt.w_max, 2)} mm (lim {f(wt.w_dop, 1)} mm), "
          f"EQU η = {f(wt.eta_EQU * 100, 0)}%, stal ≈ {f(wt.masa_stali, 0)} kg.", ""]
    L += _pozycja_md(pz, out, 2)
    if pz.prety:
        L += ["## Wykaz stali zbrojeniowej (PN-EN ISO 3766, orientacyjny)", "", zelbet.wykaz_stali(pz.prety), ""]
    for t in dodatki or []:
        L += [t, ""]
    L += ["## Źródła", ""] + [f"- {z}" for z in ZRODLA_TARCZ] + [""]
    md = "\n".join(L)
    fmd = out / f"tarcza_{an.d.id}.md"
    fmd.write_text(md, encoding="utf-8")
    (out / f"tarcza_{an.d.id}.json").write_text(json.dumps(pz.dane, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    if html:
        try:
            import markdown
            body = markdown.markdown(md, extensions=["tables"])
            fmd.with_suffix(".html").write_text(_HTML.replace("{{TITLE}}", tytul).replace("{{BODY}}", body), encoding="utf-8")
        except ImportError:
            pass
    return fmd
