"""Dane do rysunków konstrukcyjnych PT-BO z obliczeń ``lamela.obliczenia.konstrukcja``.

Moduł pomocniczy generatora ``lamela.views.konstrukcja``:
  * analiza konstrukcji uruchamiana raz na kontekst widoków (``analiza(ctx)``; opcjonalny cache pickle —
    zmienna środowiskowa ``LAMELA_KONSTR_CACHE`` = katalog; klucz = skrót plików modelu i biblioteki),
  * ekstrakcja zbrojenia WYNIKAJĄCEGO Z OBLICZEŃ (``dane(ctx)``): pola płyt (φ/s dołem i górą z wymiarowania MES
    biblioteki), belki/nadproża (n·φ, strzemiona), wieńce, schody, fundamenty (żebra/ławy, pogrubienia pod słupami,
    płyta — biblioteka zwraca tylko A_s,req pasma Winklera → dobór prętów ``dobierz_siatke`` tego modułu),
  * kształty i długości prętów wg PN-EN ISO 3766 (kody 00, 11, 21, 51) z odliczeniem gięcia (trzpień wg
    PN-EN 1992-1-1 tabl. 8.1N), zestawienie stali z numeracją pozycji i masami (ρ = 7850 kg/m³),
  * kontrola A_s,prov ≥ max(A_s,req; A_s,min), A_s ≤ A_s,max, s ≤ s_max (PN-EN 1992-1-1 9.2.1.1, 9.3.1.1)
    — raport ``kontrola_zbrojenia.md/json`` i lista braków danych ``BRAKI_DANYCH.md``.
Wszystkie wartości geometryczne pochodzą z modelu (``ctx.model``), zbrojenie — z obiektów wyników biblioteki.
"""
from __future__ import annotations

import hashlib
import math
import os
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path

from ..obliczenia.konstrukcja.materialy import masa_preta, pole_preta

GATUNEK = "B500SP"
SREDNICE_PL = (8, 10, 12, 14, 16, 20)
KODY_ISO3766 = {"00": "prosty", "11": "jedno odgięcie 90°", "21": "dwa odgięcia 90° (U)", "51": "strzemię zamknięte",
                "26": "odgięty (bieg schodów)"}


# ================================================================================================ analiza (cache)
def _skrot_plikow(paths) -> str:
    h = hashlib.sha1()
    for p in paths:
        try:
            h.update(Path(p).read_bytes())
        except OSError:
            h.update(str(p).encode())
    return h.hexdigest()[:16]


class _Pickler(pickle.Pickler):
    """Pickler pomijający obiekty nieserializowalne (faktoryzacje SuperLU macierzy MES) — do cache analizy."""

    def reducer_override(self, obj):
        if type(obj).__name__ in ("SuperLU", "Figure", "Axes"):
            return (type(None), ())
        return NotImplemented


def analiza(ctx):
    """AnalizaKonstrukcji dla modelu kontekstu (raz na kontekst). Błędy etapów trafiają do ``an.uwagi``."""
    an = getattr(ctx, "_konstr_an", None)
    if an is not None:
        return an
    from ..obliczenia.konstrukcja import AnalizaKonstrukcji, Parametry
    cache_dir = os.environ.get("LAMELA_KONSTR_CACHE")
    pk = None
    if cache_dir:
        lib = Path(__file__).resolve().parents[1] / "obliczenia" / "konstrukcja"
        src = [ctx.src] + sorted(str(p) for p in lib.glob("*.py"))
        dz = getattr(getattr(ctx.model, "dz", None), "raw", None)
        key = _skrot_plikow(src) + hashlib.sha1(repr(dz).encode()).hexdigest()[:8]
        pk = Path(cache_dir) / f"analiza_{key}.pkl"
        if pk.exists():
            try:
                an = pickle.loads(pk.read_bytes())
                an.m = ctx.model
                ctx._konstr_an = an
                return an
            except Exception:  # noqa: BLE001 — cache uszkodzony: liczymy od nowa
                an = None
    an = AnalizaKonstrukcji(ctx.model, Parametry.z_wymagan()).uruchom()
    if pk is not None:
        try:
            pk.parent.mkdir(parents=True, exist_ok=True)
            import io
            buf = io.BytesIO()
            _Pickler(buf, protocol=pickle.HIGHEST_PROTOCOL).dump(an)
            pk.write_bytes(buf.getvalue())
        except Exception:  # noqa: BLE001
            pass
    ctx._konstr_an = an
    return an


# ================================================================================================ pręty (ISO 3766)
def trzpien(fi: float) -> float:
    """Minimalna średnica trzpienia φ_m,min [mm] — PN-EN 1992-1-1 tabl. 8.1N (φ ≤ 16: 4φ; φ > 16: 7φ)."""
    return 4.0 * fi if fi <= 16 else 7.0 * fi


def odgiecie(fi: float) -> float:
    """Odliczenie długości na jedno gięcie 90° przy wymiarach zewnętrznych [mm]: Δ = 0,5·r + φ, r = φ_m/2
    (PN-EN ISO 3766 — wymiary zewnętrzne; reguła jak BS 8666 tabl. 3)."""
    return 0.5 * trzpien(fi) / 2.0 + fi


def hak_strzemienia(fi: float) -> float:
    """Zakończenie strzemienia hakiem 135° z prostym odcinkiem ≥ max(10φ; 70 mm) — PN-EN 1992-1-1 rys. 8.5."""
    return max(10.0 * fi, 70.0) + 0.5 * math.pi * (trzpien(fi) / 2.0 + fi / 2.0) * 0.75


def dlugosc_preta(fi: float, ksztalt: str, wym) -> float:
    """Długość rozwinięcia pręta [mm] dla kodu kształtu ISO 3766 i wymiarów zewnętrznych ``wym`` [mm]."""
    w = [float(x) for x in wym]
    if ksztalt == "00":
        return w[0]
    if ksztalt == "11":                       # L: a, b
        return w[0] + w[1] - odgiecie(fi)
    if ksztalt == "21":                       # U: a (ramię), b (grzbiet), c (ramię)
        return w[0] + w[1] + w[2] - 2 * odgiecie(fi)
    if ksztalt == "26":                       # łamany (bieg–spocznik): suma odcinków, gięcia rozwarte ≈ 0
        return sum(w)
    if ksztalt == "51":                       # strzemię zamknięte a × b (zewn.) z dwoma hakami 135°
        return 2 * (w[0] + w[1]) - 3 * odgiecie(fi) + 2 * hak_strzemienia(fi)
    return sum(w)


@dataclass
class Pret:
    """Pręt (pozycja zestawienia): kod kształtu PN-EN ISO 3766, wymiary odcinków [mm], liczba sztuk, element."""
    fi: int
    ksztalt: str
    wym: tuple
    n: int
    element: str
    opis: str = ""
    nr: int = 0
    gatunek: str = GATUNEK

    def __post_init__(self):
        self.wym = tuple(int(round(float(x) / 10.0) * 10) for x in self.wym)   # wymiary co 10 mm
        self.n = int(self.n)

    @property
    def L_mm(self) -> float:
        return math.ceil(dlugosc_preta(self.fi, self.ksztalt, self.wym) / 10.0) * 10.0   # w górę do 10 mm

    @property
    def dl(self) -> float:
        return self.L_mm / 1000.0

    @property
    def dl_calk(self) -> float:
        return self.dl * self.n

    @property
    def masa(self) -> float:
        return self.dl_calk * masa_preta(self.fi)

    def klucz(self) -> tuple:
        return (self.fi, self.ksztalt, self.wym, self.gatunek)

    def etykieta(self, s_mm: float | None = None) -> str:
        """Oznaczenie pręta na rysunku (PN-EN ISO 3766 p. 5): liczba, nr pozycji, φ, rozstaw, długość."""
        t = f"{self.n} Ø{self.fi}"
        if s_mm:
            t += f" co {s_mm / 10:g}"
        return t + f" l={self.L_mm / 10:g}"


class Zestawienie:
    """Zestawienie stali (wykaz prętów) z numeracją pozycji: identyczne pręty (φ, kształt, wymiary) mają
    wspólny numer (liczby sztuk sumowane)."""

    def __init__(self, start: int = 1):
        self.prety: list[Pret] = []
        self._nr = start - 1
        self._idx: dict = {}

    def dodaj(self, p: Pret) -> Pret:
        """Dodaje pręt; zwraca pozycję zestawienia (istniejącą przy identycznym kształcie) z nadanym numerem."""
        if p.n <= 0:
            return p
        k = p.klucz()
        if k in self._idx:
            q = self._idx[k]
            q.n += p.n
            if p.element not in q.element.split(", "):
                q.element = (q.element + ", " + p.element)[:60]
            return q
        self._nr += 1
        p.nr = self._nr
        self.prety.append(p)
        self._idx[k] = p
        return p

    def srednice(self) -> list[int]:
        return sorted({p.fi for p in self.prety})

    def dl_wg_srednic(self) -> dict:
        return {d: sum(p.dl_calk for p in self.prety if p.fi == d) for d in self.srednice()}

    def masy(self) -> dict:
        return {d: L * masa_preta(d) for d, L in self.dl_wg_srednic().items()}

    @property
    def masa(self) -> float:
        return sum(self.masy().values())


# ================================================================================================ dobór prętów
def as_min_plyty(h: float, d: float, f_ctm: float, f_yk: float = 500.0) -> float:
    """A_s,min [mm²/m] — PN-EN 1992-1-1 (9.1N) + NA: max(0,26·f_ctm/f_yk·b·d; 0,0013·b·d), b = 1 m."""
    return max(0.26 * f_ctm / f_yk * 1000.0 * d * 1000.0, 0.0013 * 1000.0 * d * 1000.0)


def s_max_plyty(h: float, glowne: bool = True, strefa_max: bool = True) -> float:
    """s_max,slabs [mm] — PN-EN 1992-1-1 9.3.1.1(3) + NA: główne 2h ≤ 250 (strefa M_max) / 3h ≤ 400; rozdzielcze
    3h ≤ 400 / 3,5h ≤ 450."""
    hm = h * 1000.0
    if glowne:
        return min(2 * hm, 250.0) if strefa_max else min(3 * hm, 400.0)
    return min(3 * hm, 400.0) if strefa_max else min(3.5 * hm, 450.0)


def dobierz_siatke(As_req: float, As_min: float, h: float, s_max: float | None = None, fi_min: int = 10,
                   fi_max: int = 16, d_g: float = 16.0) -> tuple[int, float, float]:
    """Dobór prętów pasma płyty b = 1 m (A_s,req → φ, s): (φ [mm], s [mm], A_s,prov [mm²/m]).

    Warunki: A_s,prov ≥ max(A_s,req; A_s,min) (6.1, 9.2.1.1(1)); A_s,prov ≤ A_s,max = 0,04·A_c (9.2.1.1(3));
    s ≤ s_max (9.3.1.1(3)); rozstaw w świetle ≥ max(φ; d_g + 5 mm; 20 mm) (8.2(2)). Kryterium — najmniejsza masa
    stali, przy równej masie rozstawy „okrągłe” (100/125/150/200/250) i większa średnica."""
    s_max = s_max or s_max_plyty(h)
    need = max(As_req, As_min, 1e-9)
    As_max = 0.04 * 1000.0 * h * 1000.0
    best = None
    for fi in SREDNICE_PL:
        if fi < fi_min or fi > fi_max:
            continue
        s_min_cl = max(fi, d_g + 5.0, 20.0) + fi
        for s in range(int(s_max // 5 * 5), int(math.ceil(s_min_cl)) - 1, -5):
            As = pole_preta(fi) * 1000.0 / s
            if As >= need:
                if As > As_max:
                    break
                okragly = 0 if s in (100, 125, 150, 175, 200, 250) else (1 if s % 10 == 0 else 2)
                cand = (round(As, 0), okragly, -fi, s, fi, As)
                if best is None or cand < best:
                    best = cand
                break
    if best is None:
        raise ValueError(f"nie można dobrać zbrojenia: A_s,req = {As_req:.0f} mm²/m przy h = {h:.2f} m")
    return best[4], float(best[3]), best[5]


def dobierz_prety_belki(As_req: float, b_w: float, c_nom: float, fi_s: float = 8, d_g: float = 16.0,
                        srednice=(12, 14, 16, 20, 25), n_min: int = 2) -> tuple[int, int, float]:
    """Dobór prętów podłużnych belki (n·φ w jednej warstwie): (n, φ, A_s,prov [mm²]); rozstaw w świetle ≥ max(φ;
    d_g + 5; 20 mm) (8.2(2)). Zwraca pierwszy (najlżejszy) wariant mieszczący się w jednej warstwie."""
    best = None
    for fi in srednice:
        n = max(n_min, int(math.ceil(As_req / pole_preta(fi) - 1e-9)))
        smin = max(fi, d_g + 5.0, 20.0)
        n_row = int((b_w * 1000.0 - 2 * c_nom - 2 * fi_s + smin) // (fi + smin))
        if n > n_row:
            continue
        cand = (n * pole_preta(fi), fi, n)
        if best is None or cand < best:
            best = cand
    if best is None:
        fi = srednice[-1]
        n = max(n_min, int(math.ceil(As_req / pole_preta(fi))))
        return n, fi, n * pole_preta(fi)
    return best[2], best[1], best[0]


# ================================================================================================ parsowanie wyników
_RE_FS = re.compile(r"[φ⌀Ø]\s*(\d+)\s*co\s*([\d]+(?:[,.]\d+)?)\s*cm")
_RE_NFI = re.compile(r"(\d+)\s*[φ⌀Ø]\s*(\d+)")


def fi_s(txt: str | None):
    """„φ10 co 15 cm” → (10, 150.0) albo None."""
    m = _RE_FS.search(txt or "")
    if not m:
        return None
    return int(m.group(1)), float(m.group(2).replace(",", ".")) * 10.0


def n_fi(txt: str | None):
    """„4φ12 …” → (4, 12) albo None."""
    m = _RE_NFI.search(txt or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def krok_wynik(w, *prefiksy):
    """Wartość liczbowa pierwszego kroku wyniku, którego opis zaczyna się od jednego z prefiksów."""
    for k in getattr(w, "kroki", []):
        if any(str(k.opis).startswith(p) for p in prefiksy) and isinstance(k.wynik, (int, float)):
            return float(k.wynik)
    return None


def warunki_niespelnione(wyniki) -> list[str]:
    out = []
    for r in wyniki:
        for w in getattr(r, "warunki", []):
            if not w.ok:
                s = f"{w.opis} (η = {w.eta * 100:.0f}%)"
                if s not in out:
                    out.append(s)
    return out


# ================================================================================================ struktury danych
@dataclass
class Warstwa:
    """Zbrojenie pasma płyty w jednym kierunku i warstwie (z obliczeń): φ, s, A_s,req, A_s,min, A_s,prov [mm²/m]."""
    kier: str                  # x | y
    poloz: str                 # dol | gora | naroze
    fi: int
    s: float                   # mm
    As_req: float
    As_min: float
    As_prov: float
    M: float = 0.0             # kNm/m (wartość bezwzględna momentu miarodajnego)
    zrodlo: str = "biblioteka"

    @property
    def need(self) -> float:
        return max(self.As_req, self.As_min if self.As_req > 1e-6 or self.poloz == "dol" else 0.0)

    @property
    def ok(self) -> bool:
        return self.As_prov + 1e-6 >= self.need

    @property
    def opis(self) -> str:
        return f"Ø{self.fi} co {self.s / 10:g}"


@dataclass
class PolePl:
    element: str
    pole: str
    rect: tuple                # x0, y0, x1, y1 (osie podpór pola)
    poly: object               # pole ∩ obrys elementu
    lx: float
    ly: float
    brzegi: str                # x0, x1, y0, y1: S — podparta, U — utwierdzona (ciągła), W — swobodna
    warstwy: dict = field(default_factory=dict)   # dol_x, dol_y, gora_x, gora_y, naroze → Warstwa
    eta: float = 0.0
    niesp: list = field(default_factory=list)
    V: float = 0.0


@dataclass
class ElementPl:
    id: str
    typ: str                   # strop | dach | wspornik
    poz: str
    poly: object
    h: float
    wierzch: float
    beton: str
    eksp: str
    c_nom: float
    lacznik: bool = False
    pola: list = field(default_factory=list)
    eta: float = 0.0
    niesp: list = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class Poziom:
    """Grupa płyt liczonych wspólnie (jeden model MES) — jeden rzut konstrukcji / zbrojenia."""
    idx: int
    nazwa: str
    wierzch: float
    elementy: list = field(default_factory=list)
    podpory: list = field(default_factory=list)   # (id, LineString, rodzaj: sciana | belka)
    slupy: list = field(default_factory=list)     # (id, (x, y))

    @property
    def poly(self):
        from shapely.ops import unary_union
        return unary_union([e.poly for e in self.elementy]).buffer(0)

    @property
    def spod(self) -> float:
        return min(e.wierzch - e.h for e in self.elementy)


_WARSTWY_RE = (("dol_x", "dół, kierunek x"), ("dol_y", "dół, kierunek y"), ("gora_x", "góra, x"),
               ("gora_y", "góra, y"), ("naroze", "zbrojenie narożne"))


def _warstwa_z_wyniku(zg, klucz: str) -> Warstwa | None:
    fs = fi_s(getattr(zg, "zbrojenie", ""))
    if fs is None:
        return None
    return Warstwa(klucz.split("_")[-1] if "_" in klucz else "xy", klucz.split("_")[0], fs[0], fs[1],
                   float(zg.As_req), float(zg.As_min), float(zg.As_prov), float(getattr(zg, "M_Ed", 0.0)))


def _obszar_pola(c: dict, poly):
    """Obszar pola = scalone komórki siatki podpór biblioteki (``c['rect']`` — wielobok) ∩ obrys elementu płyty.
    Pasy węższe niż 0,4 m (np. płyta poza osią ściany zewnętrznej) nie są osobnymi polami — obejmują je pręty pól
    przyległych przedłużone do krawędzi."""
    reg = c["rect"].intersection(poly)
    if reg.is_empty or reg.area < 0.05 or reg.buffer(-0.2).is_empty:
        return None
    return reg


def _plyty(an, D):
    from shapely.geometry import box
    from ..obliczenia.konstrukcja import zelbet
    pos = {pz.ident: pz for pz in an.pos_plyty}
    for g in an.grupy:
        if g.fe is None or not g.komorki:
            if any(e.id in pos for e in g.el):
                continue
            D.braki.append(f"Płyta(y) {g.nazwa}: brak wyników MES w bibliotece (model MES niewykonalny) — zbrojenie "
                           "nie może być narysowane z obliczeń [WYMAGA ANALIZY].")
            continue
        kom = {c["id"]: c for c in g.komorki}
        lv = Poziom(g.idx, g.nazwa, float(g.wierzch))
        lv.podpory = [(s.id, s.linia, getattr(s, "rodzaj", "sciana")) for s in g.podp_l]
        lv.slupy = [(s.id, tuple(s.xy)) for s in g.podp_p]
        for e in g.el:
            pz = pos.get(e.id)
            if pz is None:
                continue
            c_nom = zelbet.otulina(e.ekspozycja, 10, an.p).c_nom
            el = ElementPl(e.id, e.typ, pz.nr, e.poly_full, float(e.h), float(e.wierzch), e.beton.klasa, e.ekspozycja,
                           float(c_nom), bool(e.raw.get("lacznik_termiczny")), raw=e.raw)
            el.eta = pz.wykorzystanie
            el.niesp = warunki_niespelnione(pz.wyniki + [w for sp in pz.podpozycje for w in sp.wyniki])
            dane_pol = {d["pole"]: d for d in pz.dane.get("pola", [])}
            for sp in pz.podpozycje:
                c = kom.get(sp.ident)
                if c is None:
                    continue
                reg = _obszar_pola(c, e.poly_full)
                if reg is None:
                    continue                          # pas krawędziowy — pokryty prętami pól przyległych
                pol = PolePl(e.id, c["id"], (c["x0"], c["y0"], c["x1"], c["y1"]), reg,
                             float(c["lx"]), float(c["ly"]), str(c.get("brzegi", "SSSS")))
                for zg in sp.wyniki:
                    nm = getattr(zg, "nazwa", "")
                    for klucz, frag in _WARSTWY_RE:
                        if frag in nm and hasattr(zg, "As_prov"):
                            w = _warstwa_z_wyniku(zg, klucz)
                            if w is not None:
                                pol.warstwy[klucz] = w
                pol.eta = max((w.eta for r_ in sp.wyniki for w in r_.warunki), default=0.0)
                pol.niesp = warunki_niespelnione(sp.wyniki)
                pol.V = float(dane_pol.get(c["id"], {}).get("V", 0.0))
                el.pola.append(pol)
            lv.elementy.append(el)
        if lv.elementy:
            D.poziomy.append(lv)
    D.poziomy.sort(key=lambda L: L.wierzch)


@dataclass
class BelkaZ:
    """Belka / nadproże / wieniec z obliczeń: przekrój, zbrojenie podłużne (n·φ), strzemiona, A_s."""
    id: str
    rodzaj: str                # belka | nadproze | wieniec
    poz: str
    p0: tuple
    p1: tuple
    b: float
    h: float                   # wysokość całkowita przekroju żelbetowego (z płytą, jeśli zespolona)
    spod: float
    beton: str
    eksp: str
    c_nom: float               # otulenie strzemion [mm]
    dol: tuple = (2, 12)
    gora: tuple = (2, 12)
    As_dol: tuple = (0.0, 0.0, 0.0)     # (req, min, prov) [mm²]
    As_gora: tuple = (0.0, 0.0, 0.0)
    strz: tuple = (6, 250.0, 2)          # φ, s [mm], liczba ramion
    h_pl: float = 0.0
    M: float = 0.0
    V: float = 0.0
    eta: float = 0.0
    niesp: list = field(default_factory=list)
    opis: str = ""
    sciana: str = ""
    oparcie: float = 0.2
    ids: list = field(default_factory=list)   # nadproża typowe: identyfikatory otworów danego typu

    @property
    def L(self) -> float:
        return math.hypot(self.p1[0] - self.p0[0], self.p1[1] - self.p0[1])


def _zginania(wyniki):
    return [w for w in wyniki if hasattr(w, "As_prov") and hasattr(w, "As_req") and hasattr(w, "M_Ed")]


def _as_z_warunku(wyniki, opis):
    for r in wyniki:
        for w in getattr(r, "warunki", []):
            if w.opis == opis:
                return float(w.E), float(w.R)
    return None


def _belki(an, D):
    from ..obliczenia.konstrukcja import zelbet
    m, p = an.m, an.p
    bel = {str(b["id"]): b for b in m.belki()}
    for pz in an.pos_belki:
        b = bel.get(pz.ident)
        if b is None or not pz.przyjeto:
            D.braki.append(f"Belka {pz.ident}: brak kompletu wyników wymiarowania w bibliotece — zbrojenie nie "
                           "wyznaczone [WYMAGA ANALIZY].")
            continue
        txt = " ".join(pz.przyjeto)
        mm = re.search(r"dołem (\d+)[φ⌀](\d+), górą (\d+)[φ⌀](\d+)", txt)
        mh = re.search(r"(\d+)×(\d+) cm", txt)
        sc = next((w for w in pz.wyniki if hasattr(w, "strzemiona") and w.strzemiona), None)
        if mm is None or sc is None:
            continue
        ex = p.ekspozycja.get("belka", "XC1")
        fis = fi_s(sc.strzemiona)
        c_s = zelbet.otulina(ex, fis[0], p).c_nom
        zd = _as_z_warunku(pz.wyniki, "Zbrojenie dolne") or (0.0, 0.0)
        zgs = _zginania(pz.wyniki)
        zt = _as_z_warunku(pz.wyniki, "Zbrojenie górne")
        h_tot = float(mh.group(2)) / 100.0 if mh else float(b["h"])
        kl = re.search(r"C\d+/\d+", txt)
        B = BelkaZ(pz.ident, "belka", pz.nr, tuple(b["os"][0]), tuple(b["os"][1]), float(b["b"]), h_tot,
                   float(b["spod"]), kl.group(0) if kl else "C25/30", ex, float(c_s),
                   dol=(int(mm.group(1)), int(mm.group(2))), gora=(int(mm.group(3)), int(mm.group(4))),
                   As_dol=(zgs[0].As_req if zgs else zd[0], zgs[0].As_min if zgs else 0.0, zd[1]),
                   As_gora=((zt[0], 0.0, zt[1]) if zt else (0.0, 0.0, int(mm.group(3)) * pole_preta(int(mm.group(4))))),
                   strz=(fis[0], fis[1], 2), h_pl=max(h_tot - float(b["h"]), 0.0),
                   M=float(zgs[0].M_Ed) if zgs else 0.0, V=float(sc.V_Ed), eta=pz.wykorzystanie,
                   niesp=warunki_niespelnione(pz.wyniki), opis=str(b.get("uwagi") or ""))
        D.belki.append(B)
    got = {x.id for x in D.belki}
    for bid, b in bel.items():
        if bid not in got and not bid.startswith("N"):
            D.braki.append(f"Belka {bid} ({b.get('uwagi', '')[:60]}…): brak pozycji wymiarowania w bibliotece "
                           "(belka nie jest podporą płyty w modelu MES — np. belka odwrócona/wspornikowa) — "
                           "zbrojenie do obliczenia indywidualnego [WYMAGA ANALIZY].")


def _nadproza(an, D):
    from ..obliczenia.konstrukcja import zelbet
    m, p = an.m, an.p
    for pz in an.pos_nadproza:
        oid = pz.ident[2:]
        o = m.otwor(oid)
        txt = " ".join(pz.przyjeto)
        mm = re.search(r"(\d+)×(\d+) cm, (C\d+/\d+), dołem (\d+)[φ⌀](\d+), strzemiona ([^,]+), oparcie ≥ (\d+)", txt)
        if o is None or mm is None:
            continue
        w = o.sciana or m.sciana(o.sciana_id)
        if w is None:
            continue
        a = float(mm.group(7)) / 100.0
        t, hn = float(mm.group(1)) / 100.0, float(mm.group(2)) / 100.0
        fis = fi_s(mm.group(6)) or (6, 250.0)
        ex = p.ekspozycja.get("nadproze", "XC1")
        zd = _as_z_warunku(pz.wyniki, "Zbrojenie dolne") or (0.0, 0.0)
        zgs = _zginania(pz.wyniki)
        B = BelkaZ(pz.ident, "nadproze", pz.nr, tuple(w.pt(max(o.s0 - a, 0.0), 0.0)), tuple(w.pt(min(o.s1 + a, w.L), 0.0)),
                   t, hn, float(o.z1), mm.group(3), ex, float(zelbet.otulina(ex, fis[0], p).c_nom),
                   dol=(int(mm.group(4)), int(mm.group(5))), gora=(2, 10),
                   As_dol=(zgs[0].As_req if zgs else zd[0], zgs[0].As_min if zgs else 0.0, zd[1]),
                   As_gora=(0.0, 0.0, 2 * pole_preta(10)), strz=(fis[0], fis[1], 2),
                   M=float(pz.dane.get("M", 0.0)), eta=pz.wykorzystanie, niesp=warunki_niespelnione(pz.wyniki),
                   opis=f"nad otworem {oid} ({o.szer * 100:.0f} cm) w ścianie {w.id}", sciana=w.id, oparcie=a,
                   ids=[oid])
        D.nadproza.append(B)


def _wience(an, D):
    from ..obliczenia.konstrukcja import zelbet
    p = an.p
    for pz in an.pos_wience:
        txt = " ".join(pz.przyjeto)
        nf = n_fi(txt) or (4, 12)
        fs = fi_s(txt) or (6, 250.0)
        kl = re.search(r"C\d+/\d+", txt)
        l0 = re.search(r"l₀ = (\d+) mm", txt)
        grp = next((g for g in an.grupy if pz.ident == f"W-{re.sub(r'[^A-Za-z0-9_-]+', '_', g.nazwa)[:40]}"), None)
        ex = p.ekspozycja.get("wieniec", "XC1")
        W = BelkaZ(pz.ident, "wieniec", pz.nr, (0.0, 0.0), (1.0, 0.0), 0.18, float(max((e.h for e in grp.el), default=0.22))
                   if grp else 0.22, 0.0, kl.group(0) if kl else "C25/30", ex, float(zelbet.otulina(ex, fs[0], p).c_nom),
                   dol=(nf[0] // 2, nf[1]), gora=(nf[0] - nf[0] // 2, nf[1]), strz=(fs[0], fs[1], 2),
                   As_dol=(0.0, 0.0, 0.0), eta=pz.wykorzystanie, niesp=warunki_niespelnione(pz.wyniki),
                   opis=f"wieńce pod płytą {grp.nazwa if grp else pz.ident}; zakład l₀ = {l0.group(1) if l0 else '?'} mm")
        for r in pz.wyniki:
            for w in r.warunki:
                if w.opis.startswith("Ściąg obwodowy"):
                    W.As_dol = (float(w.E), 0.0, float(w.R))
        W.ids = [grp.idx] if grp else []
        D.wience.append(W)


@dataclass
class BiegZ:
    schody: str
    nr: int
    poz: str
    h: float
    L: float                  # rozpiętość w rzucie [m]
    alfa: float
    glowne: Warstwa | None = None
    rozdz: tuple = (8, 400.0)
    gorne: tuple = (10, 400.0)
    prety: list = field(default_factory=list)   # Pret biblioteki (zelbet.Pret)
    niesp: list = field(default_factory=list)
    eta: float = 0.0
    beton: str = "C25/30"
    c_nom: float = 25.0


def _schody(an, D):
    from ..obliczenia.konstrukcja import zelbet
    p = an.p
    for pz in an.pos_schody:
        for i, w in enumerate(pz.wyniki, 1):
            txt = getattr(w, "zbrojenie", "") or ""
            fss = _RE_FS.findall(txt)
            if len(fss) < 2:
                continue
            fi, s = int(fss[0][0]), float(fss[0][1].replace(",", ".")) * 10
            As = _as_z_warunku([w], "Zbrojenie główne") or (0.0, pole_preta(fi) * 1000 / s)
            zg = next((k for k in w.kroki if k.opis.startswith("Zbrojenie minimalne")), None)
            ex = p.ekspozycja.get("schody", "XC1")
            b = BiegZ(pz.ident, i, pz.nr, float(w.h), float(w.L), float(w.alfa),
                      Warstwa("x", "dol", fi, s, float(As[0]), float(zg.wynik) if zg else 0.0, float(As[1])),
                      rozdz=(int(fss[1][0]), float(fss[1][1].replace(",", ".")) * 10),
                      gorne=(int(fss[2][0]), float(fss[2][1].replace(",", ".")) * 10) if len(fss) > 2 else (fi, 2 * s),
                      prety=list(getattr(w, "prety", [])), niesp=warunki_niespelnione([w]), eta=w.wykorzystanie,
                      c_nom=float(zelbet.otulina(ex, fi, p).c_nom))
            kl = re.search(r"C\d+/\d+", " ".join(pz.przyjeto))
            b.beton = kl.group(0) if kl else b.beton
            D.biegi.append(b)


@dataclass
class StopaZ:
    id: str
    poz: str
    xy: tuple
    B: float
    L: float
    h: float
    spod: float
    siatka: Warstwa | None = None
    niesp: list = field(default_factory=list)
    eta: float = 0.0


@dataclass
class PlytaFZ:
    id: str
    poz: str
    poly: object
    h: float
    spod: float
    beton: str
    eksp: str
    c_nom: float
    M: float = 0.0
    As_req: float = 0.0
    As_min: float = 0.0
    dol: Warstwa | None = None
    gora: Warstwa | None = None
    niesp: list = field(default_factory=list)
    uwagi: list = field(default_factory=list)


def _c_nom_modelu(m, klucz: str, domyslne: float) -> tuple[float, float]:
    """Otulenie z opisu modelu (konstrukcja.beton.<klucz>: „… c_nom 35 mm (50 mm od gruntu)”) → (c_nom, c_dół)."""
    txt = str(((m.raw.get("konstrukcja") or {}).get("beton") or {}).get(klucz) or "")
    a = re.search(r"c_nom\s*(\d+)\s*mm", txt)
    b = re.search(r"(\d+)\s*mm od gruntu", txt)
    c = float(a.group(1)) if a else domyslne
    return c, float(b.group(1)) if b else c


def _fundamenty(an, D):
    from ..obliczenia.konstrukcja import zelbet
    from shapely.geometry import Polygon
    m, p = an.m, an.p
    els = {str(e["id"]): e for e in (m.fundamenty().get("elementy") or [])}
    ex = p.ekspozycja.get("fundament", "XC2")
    c_lib = zelbet.otulina(ex, 12, p, na_gruncie="podbeton").c_nom
    c_top, c_bot = _c_nom_modelu(m, "fundament", c_lib)
    for pz in an.pos_fund:
        el = els.get(pz.ident)
        if el is None:
            continue
        kl = re.search(r"C\d+/\d+", " ".join(pz.przyjeto) + str(el.get("mat")))
        beton = kl.group(0) if kl else "C25/30"
        if "os" not in el:
            win = next((w for w in pz.wyniki if "Winkler" in getattr(w, "nazwa", "")), None)
            h = float(el.get("h", 0.25))
            F = PlytaFZ(pz.ident, pz.nr, Polygon(el["obrys"]), h, float(el.get("spod", -0.4)), beton, ex, c_bot)
            if win is not None:
                F.M = krok_wynik(win, "Moment maksymalny", "Moment pod") or 0.0
                F.As_req = krok_wynik(win, "Wymagane zbrojenie rozciągane", "Zbrojenie rozciągane") or 0.0
                F.As_min = krok_wynik(win, "Zbrojenie minimalne") or 0.0
                As2 = krok_wynik(win, "Zbrojenie ściskane") or 0.0
            else:
                As2 = 0.0
                D.braki.append(f"{pz.ident}: brak wyniku pasma płyty (Winkler) — siatki z A_s,min [WYMAGA ANALIZY].")
            d = h - c_bot / 1000.0 - 0.006
            As_min = F.As_min or as_min_plyty(h, d, 2.6)
            if As2 > 0 or F.As_req > 0.04 * 1000 * h * 1000 * 0.5:
                F.uwagi.append(
                    f"Biblioteka (pasmo Winklera h = {h * 100:.0f} cm pod ścianą krawędziową, BEZ żeber ZF): M_Ed = "
                    f"{F.M:.1f} kNm/m, A_s,req = {F.As_req / 100:.1f} cm²/m (μ > μ_lim — przekrój podwójnie zbrojony). "
                    "Model pasma nie uwzględnia żeber pod ścianami — siatki płyty przyjęto z A_s,min (9.1N), obciążenie "
                    "liniowe ścian przejmują żebra ZF. KONTROLA A_s NIESPEŁNIONA dla pasma przykrawędziowego — "
                    "wymagany MES płyty z żebrami na podłożu sprężystym [WYMAGA ANALIZY].")
                need_req = 0.0
            else:
                need_req = F.As_req
            fi, s, As = dobierz_siatke(need_req, As_min, h, s_max_plyty(h), fi_min=10, fi_max=16)
            F.dol = Warstwa("xy", "dol", fi, s, F.As_req, As_min, As, F.M, "dobór modułu (dobierz_siatke)")
            F.gora = Warstwa("xy", "gora", fi, s, F.As_req, As_min, As, F.M, "dobór modułu (dobierz_siatke)")
            F.niesp = warunki_niespelnione(pz.wyniki)
            D.plyta_f = F
            D.c_fund = (c_top, c_bot)
            continue
        r = next((w for w in pz.wyniki if hasattr(w, "zbrojenie_poprz")), None)
        if r is None:
            continue
        (x0, y0), (x1, y1) = el["os"][0], el["os"][1]
        if pz.tytul.startswith("Stopa"):
            fs = fi_s(r.zbrojenie_poprz) or (12, 200.0)
            B, hf = float(el.get("b", 1.0)), float(el.get("h", 0.45))
            Lf = math.hypot(x1 - x0, y1 - y0) + B
            Asr = (krok_wynik(r, "Wymagane zbrojenie rozciągane") or 0.0) / B
            Asm = (krok_wynik(r, "Zbrojenie minimalne") or 0.0) / B
            D.stopy.append(StopaZ(pz.ident, pz.nr, ((x0 + x1) / 2, (y0 + y1) / 2), B, Lf, hf, float(el.get("spod", -0.85)),
                                  Warstwa("xy", "dol", fs[0], fs[1], Asr, Asm, pole_preta(fs[0]) * 1000 / fs[1]),
                                  warunki_niespelnione(pz.wyniki), pz.wykorzystanie))
            continue
        nf = n_fi(r.zbrojenie_podl) or (4, 12)
        st = fi_s(r.zbrojenie_podl) or (6, 300.0)
        pp = None if "nie wymaga" in (r.zbrojenie_poprz or "") else fi_s(r.zbrojenie_poprz)
        Asm = krok_wynik(r, "Zbrojenie podłużne") or 0.0
        Z = BelkaZ(pz.ident, "zebro", pz.nr, (x0, y0), (x1, y1), float(el.get("b", 0.6)), float(el.get("h", 0.3)),
                   float(el.get("spod", -0.7)), beton, ex, c_bot, dol=(nf[0] - nf[0] // 2, nf[1]),
                   gora=(nf[0] // 2, nf[1]), As_dol=(0.0, Asm, nf[0] * pole_preta(nf[1])), strz=(st[0], st[1], 2),
                   eta=pz.wykorzystanie, niesp=warunki_niespelnione(pz.wyniki), opis=str(el.get("uwagi") or ""))
        Z.ids = [pp] if pp else []
        D.zebra.append(Z)


# ================================================================================================ agregat
@dataclass
class DaneKonstr:
    an: object
    poziomy: list = field(default_factory=list)
    belki: list = field(default_factory=list)
    nadproza: list = field(default_factory=list)
    wience: list = field(default_factory=list)
    biegi: list = field(default_factory=list)
    stopy: list = field(default_factory=list)
    zebra: list = field(default_factory=list)
    plyta_f: PlytaFZ | None = None
    c_fund: tuple = (35.0, 50.0)
    braki: list = field(default_factory=list)
    rys: dict = field(default_factory=dict)       # rejestr zbrojenia narysowanego: klucz → wiersz kontroli
    cache: dict = field(default_factory=dict)

    def poziom(self, klucz) -> Poziom | None:
        """Poziom (grupa płyt) po: id elementu (np. 'ST1'), kondygnacji pod stropem ('P0') albo indeksie grupy."""
        k = str(klucz)
        for lv in self.poziomy:
            if k in [e.id for e in lv.elementy] or k == str(lv.idx) or k == lv.nazwa:
                return lv
        m = self.an.m
        try:
            kd = m.kondygnacja(k)
            z = kd.rzedna + kd.wys_kondygnacji
            return min(self.poziomy, key=lambda L: abs(L.wierzch - z)) if self.poziomy else None
        except KeyError:
            return None

    def element(self, eid: str) -> ElementPl | None:
        for lv in self.poziomy:
            for e in lv.elementy:
                if e.id == eid:
                    return e
        return None


def dane(ctx) -> DaneKonstr:
    """Dane konstrukcyjne (raz na kontekst): analiza + ekstrakcja zbrojenia z wyników biblioteki."""
    D = getattr(ctx, "_konstr_dane", None)
    if D is not None:
        return D
    an = analiza(ctx)
    D = DaneKonstr(an)
    for fn in (_plyty, _belki, _nadproza, _wience, _schody, _fundamenty):
        try:
            fn(an, D)
        except Exception as ex:  # noqa: BLE001 — brak jednego rodzaju elementów nie blokuje rysunków
            import traceback
            tb = traceback.extract_tb(ex.__traceback__)[-1]
            D.braki.append(f"Ekstrakcja danych ({fn.__name__[1:]}): {type(ex).__name__}: {ex} "
                           f"[{Path(tb.filename).name}:{tb.lineno}] [BŁĄD MODUŁU]")
    D.braki += [f"Biblioteka: {b}" for b in an.brak_danych]
    D.braki += [f"Biblioteka (uwaga analizy): {u}" for u in an.uwagi
                if "WYMAGA ANALIZY" in u or "BŁĄD" in u or "niewykonalny" in u]
    ctx._konstr_dane = D
    return D


# ================================================================================================ kontrola A_s
def rejestruj(D: DaneKonstr, element: str, miejsce: str, poz: str, As_req: float, As_min: float, As_prov: float,
              zbrojenie: str, jedn: str = "mm²/m", s: float | None = None, s_max: float | None = None,
              As_max: float | None = None, arkusz: str = "", uwagi: str = "", wymuszone_ok: bool | None = None):
    """Rejestruje zbrojenie NARYSOWANE (φ, s / n·φ) wraz z wymaganiem z obliczeń — do raportu kontroli
    A_s,prov ≥ max(A_s,req; A_s,min), s ≤ s_max, A_s ≤ A_s,max (PN-EN 1992-1-1 9.2.1.1, 9.3.1.1)."""
    need = max(As_req, As_min)
    ok = As_prov + 1e-6 >= need
    if s is not None and s_max is not None and s > s_max + 1e-6:
        ok = False
        uwagi = (uwagi + "; " if uwagi else "") + f"s = {s:.0f} > s_max = {s_max:.0f} mm"
    if As_max is not None and As_prov > As_max + 1e-6:
        ok = False
        uwagi = (uwagi + "; " if uwagi else "") + f"A_s > A_s,max = {As_max:.0f}"
    if wymuszone_ok is not None:
        ok = ok and wymuszone_ok
    k = (element, miejsce)
    row = D.rys.get(k) or dict(element=element, miejsce=miejsce, poz=poz, arkusze=[])
    row.update(As_req=round(As_req, 1), As_min=round(As_min, 1), As_prov=round(As_prov, 1), jedn=jedn,
               zbrojenie=zbrojenie, s=s, s_max=s_max, ok=bool(ok), uwagi=uwagi,
               zapas=round(As_prov / need - 1.0, 3) if need > 1e-9 else None)
    if arkusz and arkusz not in row["arkusze"]:
        row["arkusze"].append(arkusz)
    D.rys[k] = row
    return row


def zapisz_raporty(D: DaneKonstr, ctx):
    """Zapisuje raport kontroli zbrojenia (MD + JSON) i listę braków danych — ścieżki z konfiguracji arkuszy
    (``wspolne.raport_zbrojenia``, ``wspolne.braki_danych``); brak pól = nic nie jest zapisywane."""
    import json
    cfg = ctx.cfg
    rp = cfg.get("raport_zbrojenia")
    if rp:
        rows = sorted(D.rys.values(), key=lambda r: (r["element"], r["miejsce"]))
        n_ok = sum(1 for r in rows if r["ok"])
        L = ["# Kontrola zbrojenia rysunków PT-BO — A_s,prov ≥ max(A_s,req; A_s,min)", "",
             "Plik generowany automatycznie przez `lamela.views.konstrukcja` (moduł `konstrukcja_dane.rejestruj`) przy "
             "rysowaniu arkuszy. A_s,req, A_s,min — z obiektów wyników biblioteki `lamela.obliczenia.konstrukcja` "
             "(pozycje obliczeń statycznych); A_s,prov — zbrojenie NARYSOWANE na arkuszach (φ/s lub n·φ). Warunki: "
             "PN-EN 1992-1-1 6.1, 9.2.1.1(1) (9.1N) + NA, 9.2.1.1(3) (A_s,max = 0,04·A_c), 9.3.1.1(3) (s_max).", "",
             f"**Wynik: {n_ok}/{len(rows)} pozycji spełnia warunek A_s,prov ≥ A_s,req** "
             f"({len(rows) - n_ok} niespełnionych — kolumna „Uwagi”).", "",
             "| Element | Miejsce | Poz. obl. | A_s,req | A_s,min | A_s,prov | Jedn. | Zbrojenie | Zapas | Wynik | "
             "Arkusze | Uwagi |", "|---|---|---|---:|---:|---:|---|---|---:|---|---|---|"]
        for r in rows:
            zp = f"{r['zapas'] * 100:+.0f}%" if r.get("zapas") is not None else "—"
            L.append(f"| {r['element']} | {r['miejsce']} | {r['poz']} | {r['As_req']:.0f} | {r['As_min']:.0f} | "
                     f"{r['As_prov']:.0f} | {r['jedn']} | {r['zbrojenie']} | {zp} | {'✓' if r['ok'] else '✗'} | "
                     f"{', '.join(r['arkusze'])} | {r['uwagi']} |")
        p = Path(rp)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(L) + "\n", encoding="utf-8")
        p.with_suffix(".json").write_text(json.dumps(dict(ok=n_ok, razem=len(rows), wiersze=rows), indent=1,
                                                     ensure_ascii=False, default=str), encoding="utf-8")
    bp = cfg.get("braki_danych")
    if bp:
        stale = cfg.get("braki_danych_stale") or []
        L = ["# BRAKI DANYCH — projekt techniczny konstrukcji (PT-BO)", "",
             "Lista generowana automatycznie przez `lamela.views.konstrukcja` z: (1) braków zgłoszonych przez bibliotekę "
             "obliczeń (`AnalizaKonstrukcji.brak_danych`, uwagi „WYMAGA ANALIZY”), (2) elementów modelu bez wyników "
             "wymiarowania, (3) danych niezbędnych do rysunków wykonawczych, których model nie zawiera. Uzupełnienie — "
             "w `tools/buduj_model.py` (model generowany) lub w bibliotece obliczeń.", ""]
        if stale:
            L += ["## Dane do uzupełnienia w modelu / uzgodnienia międzybranżowe", ""] + [f"- {s}" for s in stale] + [""]
        L += ["## Wyniki obliczeń — elementy bez wymiarowania lub z niespełnionymi warunkami", ""]
        L += [f"- {b}" for b in dict.fromkeys(D.braki)]
        bad = [r for r in D.rys.values() if not r["ok"]]
        if bad:
            L += ["", "## Kontrola zbrojenia — pozycje niespełnione (szczegóły: raport kontroli zbrojenia)", ""]
            L += [f"- {r['element']} / {r['miejsce']} (poz. {r['poz']}): A_s,prov = {r['As_prov']:.0f} < "
                  f"max(A_s,req; A_s,min) = {max(r['As_req'], r['As_min']):.0f} {r['jedn']} {r['uwagi']}"
                  if r['As_prov'] < max(r['As_req'], r['As_min']) else
                  f"- {r['element']} / {r['miejsce']} (poz. {r['poz']}): {r['uwagi']}" for r in bad]
        p = Path(bp)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(L) + "\n", encoding="utf-8")


# ================================================================================================ pręty płyt (rzut)
@dataclass
class GrupaPr:
    """Grupa jednakowych prętów w rzucie: pozycja zestawienia, reprezentatywny pręt i linia rozkładu."""
    pret: Pret
    n: int
    s: float | None
    linia: tuple               # ((x, y), (x, y)) — pręt reprezentatywny
    rozklad: tuple             # ((x, y), (x, y)) — zasięg rozkładu (prostopadle do prętów)
    warstwa: str               # dol | gora
    kier: str                  # x | y
    element: str
    pole: str
    wym: Warstwa | None = None
    zakres: object = None      # strefa (wielobok) — zbrojenie narożne
    haki: tuple = (False, False)
    rola: str = ""             # przeslo | podpora | wspornik | naroze | brzeg
    kawalki: int = 1           # pręty dłuższe niż L_MAX dzielone na kawałki łączone na zakład l₀
    l0: float = 0.0            # długość zakładu [m] (gdy kawalki > 1)


def _seg_linii(region, kier: str, t: float, lo: float, hi: float):
    from shapely.geometry import LineString
    ln = LineString([(lo, t), (hi, t)]) if kier == "x" else LineString([(t, lo), (t, hi)])
    g = ln.intersection(region)
    out = []
    for gg in getattr(g, "geoms", [g]):
        if gg.is_empty or gg.geom_type != "LineString" or gg.length < 0.15:
            continue
        cs = list(gg.coords)
        a = min(c[0] if kier == "x" else c[1] for c in cs)
        b = max(c[0] if kier == "x" else c[1] for c in cs)
        out.append((round(a, 2), round(b, 2)))
    return out


def skanuj(region, kier: str, t_lo: float, t_hi: float, s_m: float) -> list[tuple]:
    """Rozmieszczenie prętów kierunku ``kier`` w obszarze: pozycje poprzeczne t_k = t_lo + (k + ½)·Δ, Δ ≤ s;
    zwraca grupy (a, b, [t…]) — pręty o jednakowych końcach (zaokr. 1 cm) i ciągłym rozkładzie."""
    if region is None or region.is_empty or t_hi - t_lo < 0.05:
        return []
    x0, y0, x1, y1 = region.bounds
    lo, hi = (x0 - 1.0, x1 + 1.0) if kier == "x" else (y0 - 1.0, y1 + 1.0)
    n = max(int(math.ceil((t_hi - t_lo) / s_m - 1e-6)), 1)
    dt = (t_hi - t_lo) / n
    groups: dict = {}
    order = []
    for k in range(n):
        t = t_lo + (k + 0.5) * dt
        for ab in _seg_linii(region, kier, t, lo, hi):
            lst = groups.get(ab)
            if lst and t - lst[-1][-1] > 1.6 * dt:
                lst.append([t])
            elif lst:
                lst[-1].append(t)
            else:
                groups[ab] = [[t]]
                order.append(ab)
    out = []
    for ab in order:
        for run in groups[ab]:
            out.append((ab[0], ab[1], run))
    return out


def _rozciagnij(poly, kier: str, ext: float):
    """Suma przesunięć wieloboku wzdłuż kierunku (przybliżenie sumy Minkowskiego z odcinkiem ±ext)."""
    from shapely.affinity import translate
    from shapely.ops import unary_union
    ds = [-ext, -ext / 2, 0.0, ext / 2, ext]
    return unary_union([translate(poly, d, 0) if kier == "x" else translate(poly, 0, d) for d in ds]).buffer(0)


L_MAX = 12.0     # maks. długość handlowa pręta [m] — dłuższe dzielone, zakład l₀ (PN-EN 1992-1-1 8.7)


def _l0(fi: int, beton: str) -> float:
    from ..obliczenia.konstrukcja import zelbet
    from ..obliczenia.konstrukcja.materialy import Beton
    return zelbet.zakotwienie(fi, Beton.z_parametrow(beton)).l_0 / 1000.0


def _grupy_z_skanu(skan, kier, warstwa, fi, s_mm, element, pole, wym, zest, rola, haki_fn=None, h_leg=0.0,
                   beton: str = "C25/30"):
    out = []
    for a, b, ts in skan:
        L = (b - a) * 1000.0
        hk = haki_fn(a, b, ts) if haki_fn else (False, False)
        kaw, l0 = 1, 0.0
        if L / 1000.0 > L_MAX and not any(hk):
            l0 = _ceil5(_l0(fi, beton))
            kaw = int(math.ceil((L / 1000.0 - l0) / (L_MAX - l0)))
            L = ((L / 1000.0 + (kaw - 1) * l0) / kaw) * 1000.0
        if hk[0] and hk[1]:
            pr = Pret(fi, "21", (h_leg * 1000, L, h_leg * 1000), len(ts), element)
        elif hk[0] or hk[1]:
            pr = Pret(fi, "11", (L, h_leg * 1000), len(ts), element)
        else:
            pr = Pret(fi, "00", (L,), len(ts) * kaw, element)
        n = pr.n
        pr = zest.dodaj(pr)
        # pręt reprezentatywny: 35 % / 65 % rozkładu (naprzemiennie wg pola) — pręty sąsiednich pól nie leżą w linii
        fr = 0.35 if (sum(map(ord, str(pole) + kier)) % 2) else 0.65
        tm = ts[min(int(len(ts) * fr), len(ts) - 1)] if rola == "przeslo" else ts[len(ts) // 2]
        lin = ((a, tm), (b, tm)) if kier == "x" else ((tm, a), (tm, b))
        am = (a + b) / 2 + (0.18 * (b - a) if rola == "przeslo" and kier == "y" else 0.0)
        am = min(max(am, a + 0.1), b - 0.1)
        t0, t1 = ts[0], ts[-1]
        roz = ((am, t0), (am, t1)) if kier == "x" else ((t0, am), (t1, am))
        out.append(GrupaPr(pr, n, s_mm, lin, roz, warstwa, kier, element, pole, wym, haki=hk, rola=rola, kawalki=kaw,
                           l0=l0))
    return out


def _lbd(fi: int, beton: str) -> float:
    """Obliczeniowa długość zakotwienia l_bd [m] (8.4, warunki dobre, pręty proste) — z biblioteki."""
    from ..obliczenia.konstrukcja import zelbet
    from ..obliczenia.konstrukcja.materialy import Beton
    return zelbet.zakotwienie(fi, Beton.z_parametrow(beton)).l_bd / 1000.0


def _ceil5(x: float) -> float:
    return math.ceil(x * 20.0 - 1e-9) / 20.0


def prety_poziomu(D: DaneKonstr, lv: Poziom) -> dict:
    """Pręty płyt poziomu (grupa MES): {'dol': [GrupaPr], 'gora': [GrupaPr], 'zest': Zestawienie} — numeracja
    wspólna dla warstw dolnej i górnej (cache)."""
    key = ("poziom", lv.idx)
    if key in D.cache:
        return D.cache[key]
    from shapely.geometry import LineString, Point, box
    from shapely.ops import unary_union
    zest = Zestawienie()
    dol, gora = [], []
    # ---------------------------------------------------------------- dołem: siatki pól
    for el in lv.elementy:
        c = el.c_nom / 1000.0
        Pin = el.poly.buffer(-c, join_style=2)
        reszta = el.poly.difference(unary_union([p.poly for p in el.pola]).buffer(0.01)).buffer(0.01)
        for pol in el.pola:
            for kier in ("x", "y"):
                w = pol.warstwy.get("dol_" + kier)
                if w is None or pol.poly.is_empty:
                    continue
                ext = max(10 * w.fi / 1000.0, 0.10)
                reg = _rozciagnij(pol.poly, kier, ext).union(_rozciagnij(pol.poly, kier, 0.6).intersection(reszta))
                reg = reg.intersection(Pin)
                bx = pol.poly.intersection(Pin).bounds
                if not bx or len(bx) < 4:
                    continue
                t_lo, t_hi = (bx[1], bx[3]) if kier == "x" else (bx[0], bx[2])
                sk = skanuj(reg, kier, t_lo, t_hi, w.s / 1000.0)
                dol += _grupy_z_skanu(sk, kier, "dol", w.fi, w.s, el.id, pol.pole, w, zest, "przeslo", beton=el.beton)
    # ---------------------------------------------------------------- górą: nad podporami
    Pg = lv.poly
    cmax = max(e.c_nom for e in lv.elementy) / 1000.0
    Ping = Pg.buffer(-cmax, join_style=2)
    wsp = [e for e in lv.elementy if e.typ == "wspornik"]
    pola = [(el, pol) for el in lv.elementy if el.typ != "wspornik" for pol in el.pola]
    h_lv = max(e.h for e in lv.elementy)
    for sid, ln, rodz in lv.podpory:
        (xa, ya), (xb, yb) = ln.coords[0], ln.coords[-1]
        if abs(xa - xb) < 1e-3:
            kier, xs, r0, r1 = "x", xa, min(ya, yb), max(ya, yb)
        elif abs(ya - yb) < 1e-3:
            kier, xs, r0, r1 = "y", ya, min(xa, xb), max(xa, xb)
        else:
            continue
        i0, i1 = (0, 2) if kier == "x" else (1, 3)       # indeksy rect: x0/x1 lub y0/y1 (strona podpory)
        j0, j1 = (1, 3) if kier == "x" else (0, 2)       # zakres wzdłuż podpory
        lewe = [(el, p) for el, p in pola if abs(p.rect[i1] - xs) < 0.05 and p.brzegi[1 if kier == "x" else 3] != "W"]
        prawe = [(el, p) for el, p in pola if abs(p.rect[i0] - xs) < 0.05 and p.brzegi[0 if kier == "x" else 2] != "W"]
        cuts = sorted({r0, r1} | {min(max(p.rect[j], r0), r1) for _, p in lewe + prawe for j in (j0, j1)})
        for t0, t1 in zip(cuts[:-1], cuts[1:]):
            if t1 - t0 < 0.15:
                continue
            tm = (t0 + t1) / 2

            def pokrywa(p):
                return p.rect[j0] - 1e-6 <= tm <= p.rect[j1] + 1e-6
            L_ = next(((el, p) for el, p in lewe if pokrywa(p)), None)
            R_ = next(((el, p) for el, p in prawe if pokrywa(p)), None)
            if L_ is None and R_ is None:
                continue
            # wspornik przy podporze (≤ 0,6 m) — zbrojenie górne wspornika przechodzi nad podporą
            probe = box(xs - 0.6, t0, xs + 0.6, t1) if kier == "x" else box(t0, xs - 0.6, t1, xs + 0.6)
            if any(e.poly.intersects(probe) for e in wsp):
                continue
            ws = [x[1].warstwy.get("gora_" + kier) for x in (L_, R_) if x is not None and x[1].warstwy.get("gora_" + kier)]
            if not ws:
                continue
            w = max(ws, key=lambda q: (q.As_prov, q.fi))
            beton = (L_ or R_)[0].beton
            lbd = _lbd(w.fi, beton)
            # przęsło: 0,3·l (każda strona podpory pośredniej; ≥ 0,2·l od lica przy skrajnej — 9.3.1.2(2)), ≥ l_bd;
            # strona bez pola (krawędź płyty) — do krawędzi z odgięciem (obcięcie obszarem płyty)
            la = _ceil5(max(0.30 * (L_[1].lx if kier == "x" else L_[1].ly), lbd)) if L_ else 1.0
            ra = _ceil5(max(0.30 * (R_[1].lx if kier == "x" else R_[1].ly), lbd)) if R_ else 1.0
            reg = (box(xs - la, t0, xs + ra, t1) if kier == "x" else box(t0, xs - la, t1, xs + ra)).intersection(Ping)
            sk = skanuj(reg, kier, t0, t1, w.s / 1000.0)
            bnd = Ping.boundary

            def haki(a, b, ts, _k=kier):
                t = ts[len(ts) // 2]
                pa = Point(a, t) if _k == "x" else Point(t, a)
                pb = Point(b, t) if _k == "x" else Point(t, b)
                return (pa.distance(bnd) < 0.02, pb.distance(bnd) < 0.02)
            gora += _grupy_z_skanu(sk, kier, "gora", w.fi, w.s, (L_ or R_)[0].id, sid, w, zest, "podpora", haki,
                                   h_lv - 2 * cmax)
    D.cache[key] = dict(dol=dol, gora=gora, zest=zest)
    _gora_wsporniki(D, lv, zest, gora, Ping, h_lv, cmax)
    _naroza(D, lv, zest, dol, gora)
    return D.cache[key]


def odcinki_proste(g) -> list:
    """Odcinki proste geometrii liniowej (łamane rozbite w wierzchołkach, odcinki współliniowe scalone)."""
    from shapely.geometry import LineString
    out = []
    for gg in getattr(g, "geoms", [g]):
        if gg.is_empty or gg.geom_type not in ("LineString", "LinearRing"):
            continue
        cs = list(gg.coords)
        cur = [cs[0]]
        for a, b in zip(cs[:-1], cs[1:]):
            if len(cur) >= 2:
                (x0, y0), (x1, y1) = cur[-2], cur[-1]
                cr = (x1 - x0) * (b[1] - a[1]) - (y1 - y0) * (b[0] - a[0])
                if abs(cr) > 1e-9:
                    out.append(LineString([cur[0], cur[-1]]))
                    cur = [a]
            cur.append(b)
        if len(cur) >= 2:
            out.append(LineString([cur[0], cur[-1]]))
    return [o for o in out if o.length > 1e-6]


LACZNIK_T = 0.08      # grubość korpusu izolacji łącznika termoizolacyjnego [m] (typowo 80 mm; 120 mm — wyroby „XT”)


def _gora_wsporniki(D, lv, zest, gora, Ping, h_lv, cmax):
    """Zbrojenie górne płyt wspornikowych: od krawędzi swobodnej (odgięcie) przez linię zamocowania do przęsła
    zaplecza na długość max(l_c; l_bd) za najbliższą podporą (ściana/belka ≤ 1,6 m od zamocowania — wspornik wielostopniowy, np. ST2Z + PL-2)."""
    from shapely.geometry import LineString, Point, box
    from shapely.ops import unary_union
    for el in [e for e in lv.elementy if e.typ == "wspornik"]:
        inne = unary_union([e.poly for e in lv.elementy if e is not el])
        if inne.is_empty:
            continue
        root = el.poly.boundary.intersection(inne.buffer(0.02))
        segs = [g for g in odcinki_proste(root) if g.length > 0.3]
        for sg in segs:
            (xa, ya), (xb, yb) = sg.coords[0], sg.coords[-1]
            if abs(ya - yb) < 1e-3:
                kier, r = "y", ya
                t0, t1 = sorted((xa, xb))
            elif abs(xa - xb) < 1e-3:
                kier, r = "x", xa
                t0, t1 = sorted((ya, yb))
            else:
                continue
            probe = box(t0, r - 0.05, t1, r + 0.05) if kier == "y" else box(r - 0.05, t0, r + 0.05, t1)
            strona = 1.0 if el.poly.intersection(probe.buffer(0.3)).centroid.coords[0][1 if kier == "y" else 0] > r \
                else -1.0                                       # strona wspornika względem linii zamocowania
            pol = max(el.pola, key=lambda p: p.poly.area) if el.pola else None
            if pol is None:
                continue
            w = pol.warstwy.get("gora_" + kier)
            if w is None:
                continue
            big = 1e3
            half = (box(-big, min(r, r + strona * big), big, max(r, r + strona * big)) if kier == "y"
                    else box(min(r, r + strona * big), -big, max(r, r + strona * big), big))
            arm = el.poly.intersection(half)
            if arm.is_empty:
                continue
            ab = arm.bounds
            l_c = (ab[3] - ab[1]) if kier == "y" else (ab[2] - ab[0])
            t0, t1 = (ab[0], ab[2]) if kier == "y" else (ab[1], ab[3])
            podp = [ln for _, ln, _r in lv.podpory
                    if (kier == "y" and abs(ln.coords[0][1] - ln.coords[-1][1]) < 1e-3 and 0 < -strona * (ln.coords[0][1] - r) < 1.6)
                    or (kier == "x" and abs(ln.coords[0][0] - ln.coords[-1][0]) < 1e-3 and 0 < -strona * (ln.coords[0][0] - r) < 1.6)]
            if not podp:
                continue                                        # styk bez podpory przy zamocowaniu — nie wspornik
            d_s = min(abs((ln.coords[0][1] if kier == "y" else ln.coords[0][0]) - r) for ln in podp)
            back = _ceil5(d_s + max(l_c, _lbd(w.fi, el.beton)))
            a, b = sorted((r - strona * back, r + strona * (l_c + 0.5)))
            reg = (box(t0, a, t1, b) if kier == "y" else box(a, t0, b, t1)).intersection(Ping)
            if el.lacznik:
                # łącznik termoizolacyjny: pręty NIE przechodzą przez korpus izolacji (8 cm po stronie płyty zaplecza) —
                # część wspornikowa (od krawędzi do łącznika) i część w płycie zaplecza zakładkowane z prętami łącznika
                korp = (box(t0 - 1, min(r, r - strona * (LACZNIK_T + 0.02)), t1 + 1, max(r, r - strona * (LACZNIK_T + 0.02)))
                        if kier == "y" else
                        box(min(r, r - strona * (LACZNIK_T + 0.02)), t0 - 1, max(r, r - strona * (LACZNIK_T + 0.02)), t1 + 1))
                reg = reg.difference(korp)
            sk = skanuj(reg, kier, t0 + el.c_nom / 1000, t1 - el.c_nom / 1000, w.s / 1000.0)
            bnd = el.poly.buffer(-el.c_nom / 1000.0, join_style=2).boundary

            def haki(a_, b_, ts, _k=kier):
                t = ts[len(ts) // 2]
                pa = Point(t, a_) if _k == "y" else Point(a_, t)
                pb = Point(t, b_) if _k == "y" else Point(b_, t)
                return (pa.distance(bnd) < 0.02, pb.distance(bnd) < 0.02)
            gora += _grupy_z_skanu(sk, kier, "gora", w.fi, w.s, el.id, pol.pole, w, zest, "wspornik", haki,
                                   el.h - 2 * el.c_nom / 1000.0)


def _naroza(D, lv, zest, dol, gora):
    """Zbrojenie stref narożnych pól (0,2·l_min × 0,2·l_min, górą i dołem, 2 kierunki) — wymagane przez bibliotekę
    (moment skręcający; PN-EN 1992-1-1 9.3.1.3) w narożach pól między krawędziami podpartymi, z których co najmniej
    jedna jest swobodnie podparta (przy dwóch krawędziach ciągłych naroże pokrywa zbrojenie podporowe)."""
    from shapely.geometry import box
    for el in lv.elementy:
        Pin = el.poly.buffer(-el.c_nom / 1000.0, join_style=2)
        for pol in el.pola:
            w = pol.warstwy.get("naroze")
            if w is None or el.typ == "wspornik":
                continue
            x0, y0, x1, y1 = pol.rect
            br = pol.brzegi
            a_n = 0.2 * min(pol.lx, pol.ly)
            for (xx, bx_), (yy, by_) in (((x0, br[0]), (y0, br[2])), ((x1, br[1]), (y0, br[2])),
                                         ((x1, br[1]), (y1, br[3])), ((x0, br[0]), (y1, br[3]))):
                if not (bx_ in "SU" and by_ in "SU") or "S" not in bx_ + by_:
                    continue
                zone = box(xx - a_n, yy - a_n, xx + a_n, yy + a_n).intersection(pol.poly)
                if zone.area < 0.01:
                    continue
                ext = max(10 * w.fi / 1000.0, 0.15)
                for warstwa, lst in (("dol", dol), ("gora", gora)):
                    for kier in ("x", "y"):
                        reg = _rozciagnij(zone, kier, ext).intersection(Pin)
                        bx = zone.bounds
                        t_lo, t_hi = (bx[1], bx[3]) if kier == "x" else (bx[0], bx[2])
                        gs = _grupy_z_skanu(skanuj(reg, kier, t_lo, t_hi, w.s / 1000.0), kier, warstwa, w.fi, w.s,
                                            el.id, pol.pole, w, zest, "naroze")
                        for g in gs:
                            g.zakres = zone
                        lst += gs


# ================================================================================================ nadproża — typy
def typy_nadprozy(D: DaneKonstr) -> list:
    """Nadproża z obliczeń pogrupowane w typy (jednakowy przekrój, długość co 5 cm, zbrojenie, beton): lista
    (oznaczenie „NA”, „NB”…, [BelkaZ]). Otwory z nadprożem–belką modelu (np. N6 „nadproże otworu O2-01”) pominięte."""
    if "typy_nadprozy" in D.cache:
        return D.cache["typy_nadprozy"]
    zbelki = set()
    for b in D.an.m.belki():
        mm = re.search(r"otworu (O[\w-]+)", str(b.get("uwagi") or ""))
        if mm and any(x.id == str(b["id"]) for x in D.belki):
            zbelki.add(mm.group(1))
    grp: dict = {}
    for n in D.nadproza:
        if n.ids and n.ids[0] in zbelki:
            continue
        key = (round(n.b, 3), round(n.h, 3), round(math.ceil(n.L * 20 - 1e-6) / 20, 2), n.dol, n.gora, n.strz, n.beton)
        grp.setdefault(key, []).append(n)
    out = []
    lit = "ABCDEFGHJKLMNPRSTUWXYZ"
    for i, (key, lst) in enumerate(sorted(grp.items(), key=lambda t: (t[0][2], t[0][1], t[0][3]))):
        nm = "N" + (lit[i] if i < len(lit) else lit[i // len(lit) - 1] + lit[i % len(lit)])
        out.append((nm, lst))
    D.cache["typy_nadprozy"] = out
    return out


def typ_nadproza(D: DaneKonstr, nid: str) -> str | None:
    for nm, lst in typy_nadprozy(D):
        if any(n.id == nid for n in lst):
            return nm
    return None


# ================================================================================================ pręty fundamentu
def prety_fundamentu(D: DaneKonstr) -> dict:
    """Zbrojenie płyty fundamentowej z żebrami i pogrubieniami: siatki płyty (dół/góra — ``dobierz_siatke``),
    żebra (n·φ z obliczeń ław, dołem i górą, strzemiona zamknięte na pełną wysokość żebro + płyta), pogrubienia pod
    słupami (siatka dołem z odgięciami — z obliczeń stóp), pręty narożne L żeber obwodowych (l₀ × l₀)."""
    if "fund" in D.cache:
        return D.cache["fund"]
    from shapely.geometry import LineString, Point
    m = D.an.m
    zest = Zestawienie()
    F = D.plyta_f
    out = dict(zest=zest, dol=[], gora=[], zebra={}, stopy={}, naroza=None)
    c_top, c_bot = D.c_fund
    if F is not None:
        P = F.poly
        Pin = P.buffer(-c_bot / 1000.0, join_style=2)
        x0, y0, x1, y1 = Pin.bounds
        for warstwa, w in (("dol", F.dol), ("gora", F.gora)):
            for kier in ("x", "y"):
                t_lo, t_hi = (y0, y1) if kier == "x" else (x0, x1)
                sk = skanuj(Pin, kier, t_lo, t_hi, w.s / 1000.0)
                out[warstwa] += _grupy_z_skanu(sk, kier, warstwa, w.fi, w.s, F.id, "siatka", w, zest, "przeslo",
                                               beton=F.beton)
    els = {str(e["id"]): e for e in (m.fundamenty().get("elementy") or [])}
    for Z in D.zebra:
        e = els.get(Z.id)
        if e is None:
            continue
        ln = LineString(e["os"])
        h_tot = Z.h + (F.h if F is not None else 0.0)
        c = Z.c_nom / 1000.0
        L = ln.length + Z.b - 2 * c if ln.length > Z.b else ln.length
        fi = Z.dol[1]
        pd = zest.dodaj(Pret(fi, "00", (L * 1000,), Z.dol[0], Z.id, "dołem"))
        pg = zest.dodaj(Pret(fi, "00", (L * 1000,), Z.gora[0], Z.id, "górą"))
        fs, ss = Z.strz[0], Z.strz[1]
        ns = int(math.ceil(ln.length / (ss / 1000.0))) + 1
        pst = zest.dodaj(Pret(fs, "51", ((Z.b - 2 * c + 2 * fs / 1000) * 1000, (h_tot - 2 * c + 2 * fs / 1000) * 1000),
                              ns, Z.id, "strzemię"))
        pp = None
        if Z.ids and Z.ids[0]:
            fi_p, s_p = Z.ids[0]
            pp = zest.dodaj(Pret(int(fi_p), "00", ((Z.b - 2 * c) * 1000,), int(math.ceil(ln.length / (s_p / 1000.0))) + 1,
                                 Z.id, "poprzeczne"))
        out["zebra"][Z.id] = dict(dol=pd, gora=pg, strz=pst, n_strz=ns, poprz=pp, h_tot=h_tot, L=L,
                                  n_dol=Z.dol[0], n_gora=Z.gora[0])
    # narożniki żeber obwodowych: pręty L l₀ × l₀ (po 2 dołem i górą w każdym narożu)
    if F is not None and D.zebra:
        fi = D.zebra[0].dol[1]
        l0 = _ceil5(_l0(fi, F.beton))
        n_nar = sum(1 for _ in list(F.poly.exterior.coords)[:-1])
        out["naroza"] = zest.dodaj(Pret(fi, "11", (l0 * 1000, l0 * 1000), 4 * n_nar, "naroża", "narożniki żeber"))
    for S_ in D.stopy:
        w = S_.siatka
        c = c_bot / 1000.0
        n1 = int(math.ceil((S_.B - 2 * c) / (w.s / 1000.0))) + 1
        n2 = int(math.ceil((S_.L - 2 * c) / (w.s / 1000.0))) + 1
        leg = 150.0                        # odgięcie 15 cm — jak w pozycji obliczeniowej stopy (biblioteka)
        p1 = zest.dodaj(Pret(w.fi, "21", (leg, (S_.L - 2 * c) * 1000, leg), n1, S_.id, "siatka dołem"))
        p2 = zest.dodaj(Pret(w.fi, "21", (leg, (S_.B - 2 * c) * 1000, leg), n2, S_.id, "siatka dołem"))
        out["stopy"][S_.id] = dict(x=p1, y=p2, n1=n1, n2=n2)
    D.cache["fund"] = out
    return out
