"""Ekonomiczne ustawienie na arkuszach — wspólny silnik doboru formatu i upakowania treści arkusza (wszystkie typy
widoków: AR, PZT, IS/IE, BO, detale; także rejestrowane przez ``sheets.register_view``).

Wymaganie Inwestora: „Pamiętaj o ekonomicznym ustawieniu na arkuszach, nie musimy sztywno trzymać się geometrii
wielokrotności A3, chociaż fajnie jak się ładnie będzie składało.”

1. **Formaty-kandydaci**: ISO 216 (A4 pionowo, A3…A0), wydłużone PN-EN ISO 5457 (A4×n, A3×n, A2×n, A1×n) oraz
   **niestandardowe** H × L: wysokość H z ``wysokosci`` (domyślnie 297, 420, 594, 841, 891 mm), długość L dopasowana
   do treści (krok ``krok_dlugosci``, 10 mm). H ≤ 914 mm: arkusz drukuje się na rolce plotera 36″ (914,4 mm; typowe
   rolki: 297, 420, 594/610 (24″), 841, 914 (36″) mm) z długością L odcinaną z rolki — format niestandardowy nie
   podraża wydruku, liczy się pole papieru. Większe H (A0×n, 1189 mm) wymagają rolki 1189 mm (47″, rzadkie) —
   tylko jawnie.
2. **Koszt**: pole arkusza × (1 + kara składania pionowego + kara składania poziomego) × (1 + ``kara_niestandard``
   dla formatu niestandardowego) — kary wg oceny ``lamela.draft.skladanie.ocena_skladania`` („dobre” / „poprawne”
   / „słabe”, ``kara_skladania``). Długości „ładnie” składane (pasy harmonijki 180–210 mm w parach równych:
   570–630, 960–1050, 1330–1470 … mm; wysokość 297 / 594 / 891 mm) wygrywają, gdy dopłata papieru jest mała.
3. **Upakowanie** (dla danego W × H): tabliczka w prawym dolnym rogu ramki (z tabelą zmian nad nią), widoki
   w grupie (wiersz / kolumna / siatka — wariant o najmniejszym polu), bloki kolumny opisowej (legendy, tabele,
   uwagi, róża + podziałka) rozmieszczane algorytmem wolnych prostokątów (MaxRects): najpierw kolumna nad tabliczką,
   potem kolejne kolumny w lewo, pas pod widokami i wolne obszary w obrysie widoków („kieszenie” przy krawędzi
   obwiedni, z odstępem ≥ ``odstep_kieszeni``); uwagi dzielone na kolumny (numeracja ciągła, „cd.”); róża
   kierunków i podziałka — jeden wiersz bezpośrednio nad tabliczką. Odstępy: widok–widok ≥ 12 mm, widok–blok
   ≥ 10 mm, blok–blok ≥ 5 mm; nic się nie nakłada (``sprawdz_nakladanie``).
4. **Tryby** (``format`` w ``wspolne`` lub w arkuszu): ``auto`` = ``ekonomiczny`` (wszystkie kandydaty),
   ``standardowy`` (tylko ISO 216 + wydłużone, nowe upakowanie), ``klasyczny`` (dawny algorytm ``sheets.py``:
   pierwszy mieszczący się z listy FORMATS, kolumna 180 mm na całą wysokość), nazwa formatu (``A2``, ``A3x3`` —
   jak dotąd), wymiary ``[H, L]`` lub ``"780x594"`` (L × H).

Parametry (``wspolne`` lub arkusz, wszystkie opcjonalne): ``format``, ``wysokosci``, ``krok_dlugosci`` (10),
``modul_skladania`` (190 — docelowa szerokość pasa harmonijki; 0 — bez kandydatów „ładnych” długości),
``kara_niestandard`` (0,03), ``kara_skladania`` ({dobre: 0, poprawne: 0,04, słabe: 0,10} — na kierunek),
``max_dlugosc`` (2400), ``wolne_obszary`` (true — bloki także w pustych narożnikach obwiedni widoków),
``odstep_widok_blok`` (10 mm).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..draft import text as T
from ..draft.sheet import ISO_A, ISO_ELONGATED, custom_size, sheet_size
from ..draft.skladanie import ocena_skladania, pasy_pionowe

MARG_L, MARG = 20.0, 10.0           # ramka: margines na oprawę 20 mm, pozostałe 10 mm
TB_W = 180.0                        # szerokość tabliczki (PN-EN ISO 7200)
GAP_V = 12.0                        # widok ↔ widok
GAP_VB = 10.0                       # widok ↔ blok / tabliczka
GAP_B = 5.0                         # blok ↔ blok (w pionie)
GAP_C = 6.0                         # blok ↔ blok (w poziomie)
PAD_V = 6.0                         # ramka ↔ widok
PAD_B = 3.0                         # ramka ↔ blok (góra, dół, lewo); z prawej bloki licują z ramką jak tabliczka

DOMYSLNE = dict(
    format="auto", wysokosci=[297, 420, 594, 841, 891], krok_dlugosci=10.0, modul_skladania="auto",
    kara_niestandard=0.03, kara_skladania={"dobre": 0.0, "poprawne": 0.04, "słabe": 0.10}, max_dlugosc=2400.0,
    max_wysokosc=914.0, wolne_obszary=True, odstep_widok_blok=GAP_VB,
)
TRYBY = ("auto", "ekonomiczny", "standardowy", "klasyczny")


def opcje(cfg: dict | None, spec: dict | None = None) -> dict:
    """Parametry silnika: wartości domyślne ← ``wspolne`` ← arkusz (``spec``)."""
    o = dict(DOMYSLNE)
    for src in (cfg or {}, spec or {}):
        for k in DOMYSLNE:
            if src.get(k) is not None:
                o[k] = src[k]
    ks = dict(DOMYSLNE["kara_skladania"])
    ks.update(o.get("kara_skladania") or {})
    o["kara_skladania"] = ks
    return o


def tryb_formatu(fmt) -> tuple[str, tuple | None]:
    """('ekonomiczny' | 'standardowy' | 'klasyczny' | 'jawny', (nazwa, W, H) dla jawnego)."""
    if isinstance(fmt, (list, tuple)) and len(fmt) == 2:             # [H, L]
        H, L = float(fmt[0]), float(fmt[1])
        return "jawny", (f"{L:.0f}×{H:.0f}", L, H)
    s = str(fmt if fmt is not None else "auto").strip()
    low = s.lower()
    if low in ("auto", "ekonomiczny", "ekonomiczne", "eko"):
        return "ekonomiczny", None
    if low in ("standardowy", "standard", "iso"):
        return "standardowy", None
    if low in ("klasyczny", "dawny", "stary"):
        return "klasyczny", None
    cs = custom_size(s)
    if cs is not None:
        return "jawny", (f"{cs[0]:.0f}×{cs[1]:.0f}", cs[0], cs[1])
    W, H = sheet_size(s)
    return "jawny", (s.replace("x", "×").replace("X", "×"), W, H)


# ================================================================================================ formaty
def formaty_standardowe(max_h: float = 914.0, max_l: float = 2400.0) -> list[tuple[str, float, float, str]]:
    """Formaty ISO 216 i wydłużone PN-EN ISO 5457: (nazwa, W, H, orientacja) — poziomo; A4 i A3 także pionowo."""
    out = [("A4", 210.0, 297.0, "portrait"), ("A3", 297.0, 420.0, "portrait")]
    for nm, (s, l) in list(ISO_A.items()) + list(ISO_ELONGATED.items()):
        if nm == "A4":
            continue
        if s <= max_h + 0.5 and l <= max_l + 0.5:
            out.append((nm.replace("x", "×"), float(l), float(s), "landscape"))
    return sorted(out, key=lambda f: (f[1] * f[2], f[0]))


def nazwa_standardowa(W: float, H: float, tol: float = 1.0) -> tuple[str, str] | None:
    """(nazwa, orientacja), gdy wymiary W × H odpowiadają formatowi ISO 216 / wydłużonemu (w dowolnej orientacji)."""
    for nm, (s, l) in list(ISO_A.items()) + list(ISO_ELONGATED.items()):
        if abs(W - l) <= tol and abs(H - s) <= tol:
            return nm.replace("x", "×"), "landscape"
        if abs(W - s) <= tol and abs(H - l) <= tol:
            return nm.replace("x", "×"), "portrait"
    return None


def kara_skladania(W: float, H: float, o: dict, tb_h: float | None = None) -> tuple[float, dict]:
    """Kara względna za składanie (suma kar kierunków) i plan składania."""
    oc = ocena_skladania(W, H, tb_h)
    ks = o["kara_skladania"]
    k = float(ks[oc["ocena_pion"]]) + float(ks[oc["ocena_poziom"]])
    if not oc["tabliczka_na_wierzchu"]:
        k += float(ks["słabe"])
    return k, oc


def dlugosci_kandydaci(W_need: float, o: dict) -> list[float]:
    """Długości L ≥ W_need do oceny funkcją kosztu (``modul_skladania``):

    * ``auto`` (domyślnie) — wszystkie L z siatki ``krok_dlugosci`` od najmniejszej do +35 % (preferencja
      „ładnego” składania wynika z kary w koszcie);
    * liczba m > 0 — tylko L = 210 + m·n (pierwszy pas z marginesem + pasy modułu; np. 190 → 590, 780, 970 …);
    * 0 / false — tylko najmniejsza długość (bez dopasowania do składania)."""
    krok = max(1.0, float(o["krok_dlugosci"]))
    L0 = math.ceil((W_need - 1e-6) / krok) * krok
    Lmax = float(o["max_dlugosc"])
    m = o.get("modul_skladania", "auto")
    out = [L0]
    if m is None or str(m).lower() == "auto":
        L = L0
        while L <= min(Lmax, L0 * 1.35):
            out.append(L)
            L += krok
    elif m and float(m) > 0:
        n = max(0, math.ceil((W_need - 210.0 - 1e-6) / float(m)))
        out = [210.0 + float(m) * (n + i) for i in range(3)]
    return sorted(set(x for x in out if W_need - 1e-6 <= x <= Lmax + 1e-6)) or [L0]


# ================================================================================================ elementy arkusza
@dataclass
class Blok:
    """Blok kolumny opisowej: ``fn(sh, x, y_top, w) -> y_bottom`` rysuje go na arkuszu; wymiary z pomiaru."""
    nazwa: str
    fn: object
    w: float = TB_W                 # szerokość przekazywana do fn
    h: float = 0.0                  # wysokość (od y_top w dół)
    dx0: float = 0.0                # wystawanie w lewo poza x
    dx1: float = 0.0                # wystawanie w prawo poza x + w
    dy1: float = 0.0                # wystawanie ponad y_top (np. tytuł tabeli)
    kotwica: str = ""               # "nad_tabliczka" — wiersz bezpośrednio nad tabliczką
    uwagi: object = None            # BlokUwag — blok dzielony na części (numeracja ciągła)

    @property
    def szer(self) -> float:
        return self.dx0 + self.w + self.dx1

    @property
    def wys(self) -> float:
        return self.h + self.dy1


def zmierz_blok(fn, w: float = TB_W) -> tuple[float, float, float, float]:
    """(h, dx0, dx1, dy1) bloku — rysowanie na arkuszu próbnym i obwiednia prymitywów."""
    from ..draft.sheet import Sheet
    sh = Sheet("A0", draw_frame=False)
    X, Y = 100.0, 5000.0
    yb = float(fn(sh, X, Y, w))
    e = sh.extents()
    if e is None:
        return max(0.0, Y - yb), 0.0, 0.0, 0.0
    h = max(Y - yb, Y - float(e[1]))
    snap = (lambda v: v if v >= 0.5 else 0.0)          # wystawanie < 0,5 mm (grubość linii) — pomijalne
    return h, snap(X - float(e[0])), snap(float(e[2]) - X - w), snap(float(e[3]) - Y)


def blok(nazwa: str, fn, w: float = TB_W, kotwica: str = "") -> Blok:
    h, dx0, dx1, dy1 = zmierz_blok(fn, w)
    return Blok(nazwa, fn, w, h, dx0, dx1, dy1, kotwica)


class BlokUwag:
    """Uwagi numerowane dzielone na części (kolumny): wysokości liczone jak w ``draft.sheet.notes_box``."""

    def __init__(self, lines: list[str], title: str = "OBJAŚNIENIA I UWAGI", h: float = 1.8, w: float = TB_W):
        self.lines, self.title, self.th, self.w = list(lines), title, h, w

    def _item_h(self, i: int) -> float:
        from ..draft.sheet import wrap
        pad = 2.0
        prefix = f"{i + 1}. "
        ind = T.width(prefix, self.th)
        n = len(wrap(self.lines[i], self.w - 2 * pad - ind, self.th))
        return n * self.th * 1.6 + self.th * 0.3

    def wysokosc(self, i0: int, i1: int) -> float:
        """Wysokość części z uwagami i0…i1-1 (z tytułem i ramką)."""
        if getattr(self, "_hs", None) is None:
            self._hs = [self._item_h(i) for i in range(len(self.lines))]
        pad = 2.0
        return pad + 3.5 + 3.5 * 1.8 + sum(self._hs[i0:i1]) - self.th * 0.9 + pad - 1.0

    def fn(self, i0: int, i1: int):
        from ..draft.sheet import notes_box
        title = self.title + (" (cd.)" if i0 > 0 else "")

        def draw(sh, x, y, w):
            return notes_box(sh, x, y, w, self.lines[i0:i1], title, h=self.th, start=i0 + 1)[1]
        return draw


@dataclass
class Widok:
    """Widok na arkuszu: prostokąt treści w × h [mm] (z marginesem rzutni), tytuł pod lub nad, obrys zajętości."""
    nazwa: str
    w: float
    h: float
    tytul_w: float = 0.0
    tytul_h: float = 11.0
    tytul_nad: bool = False
    zajete: list = field(default_factory=list)   # prostokąty treści względem lewego dolnego rogu (x0, y0, x1, y1)

    @property
    def slot_w(self) -> float:
        return max(self.w, 2.0 + self.tytul_w)

    @property
    def dol(self) -> float:          # pas pod treścią (tytuł pod widokiem)
        return 0.0 if self.tytul_nad else self.tytul_h

    @property
    def gora(self) -> float:         # treść + tytuł nad widokiem
        return self.h + (self.tytul_h if self.tytul_nad else 0.0)

    def prostokaty(self) -> list[tuple]:
        """Zajętość względem lewego dolnego rogu treści: pasy treści (lub cały prostokąt) + tytuł."""
        r = list(self.zajete) or [(0.0, 0.0, self.w, self.h)]
        if self.tytul_nad:
            r.append((2.0, self.h, 2.0 + self.tytul_w, self.h + self.tytul_h))
        else:
            r.append((2.0, -self.tytul_h, 2.0 + self.tytul_w, 0.0))
        return r


def obrys_widoku(vp, pad: float = 3.0, res: float = 5.0, tol: float = 20.0) -> list[tuple]:
    """Zajętość rzutni jako pasy poziome [mm papieru, względem lewego dolnego rogu treści z marginesem ``pad``]:
    w każdym pasie wysokości ``res`` — zakres od skrajnie lewego do skrajnie prawego prymitywu (dziury wewnątrz
    nie są wolne); pasy o zakresach różnych o < ``tol`` łączone. Pozwala wstawić blok w pusty narożnik obwiedni
    (np. nad niższym skrzydłem elewacji) bez nakładania na rysunek."""
    from ..draft import styles
    from ..draft.core import PArc, PFill, PLine, PText, prim_points
    e = vp.extents()
    if e is None:
        return []
    k = vp.k
    boxes = []
    for p in vp.prims:
        try:
            if not styles.layer(p.layer).plot:
                continue
        except Exception:                        # noqa: BLE001 — warstwa spoza słownika: traktuj jako treść
            pass
        if isinstance(p, PFill) and str(p.fill).lower() in ("#ffffff", "#fff", "white"):
            continue
        if isinstance(p, PLine):
            a = np.asarray(p.pts, float)
            if len(a) >= 2:
                if p.closed:
                    a = np.vstack([a, a[:1]])
                lo, hi = np.minimum(a[:-1], a[1:]), np.maximum(a[:-1], a[1:])
                boxes.append(np.hstack([lo, hi]))
            continue
        if isinstance(p, (PArc, PFill, PText)):
            for pts in prim_points(p, k):
                a = np.asarray(pts, float).reshape(-1, 2)
                boxes.append(np.array([[a[:, 0].min(), a[:, 1].min(), a[:, 0].max(), a[:, 1].max()]]))
    if not boxes:
        return []
    B = np.vstack(boxes)
    B = (B - np.array([e[0], e[1], e[0], e[1]])) / k + pad            # mm względem rogu treści
    Wm, Hm = (e[2] - e[0]) / k + 2 * pad, (e[3] - e[1]) / k + 2 * pad
    nb = max(1, int(math.ceil(Hm / res)))
    b0 = np.clip(np.floor(B[:, 1] / res).astype(int), 0, nb - 1)
    b1 = np.clip(np.floor(B[:, 3] / res).astype(int), 0, nb - 1)
    cnt = b1 - b0 + 1
    idx = np.repeat(np.arange(len(B)), cnt)
    off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
    band = b0[idx] + off
    xmin = np.full(nb, np.inf)
    xmax = np.full(nb, -np.inf)
    np.minimum.at(xmin, band, B[idx, 0])
    np.maximum.at(xmax, band, B[idx, 2])
    rects, cur = [], None
    for i in range(nb):
        if not np.isfinite(xmin[i]):
            if cur:
                rects.append(cur)
                cur = None
            continue
        x0 = max(0.0, math.floor((xmin[i] - 1.0) / res) * res)
        x1 = min(Wm, math.ceil((xmax[i] + 1.0) / res) * res)
        y0, y1 = i * res, min(Hm, (i + 1) * res)
        if cur and abs(cur[0] - x0) < tol and abs(cur[2] - x1) < tol:
            cur = (min(cur[0], x0), cur[1], max(cur[2], x1), y1)
        else:
            if cur:
                rects.append(cur)
            cur = (x0, y0, x1, y1)
    if cur:
        rects.append(cur)
    return rects


def widok_z_rzutni(nazwa: str, vp, w: float, h: float, tytul: str, skala: bool, podtytul: bool = False,
                   nad: bool = False, kieszenie: bool = True) -> Widok:
    """Widok do upakowania z rzutni ``vp`` (po narysowaniu): wymiary, tytuł (jak ``Sheet.view_title``), zajętość."""
    from ..draft import fmt
    tw = T.width(tytul or "", 5.0, "bold")
    if skala:
        tw += 3.0 + T.width(fmt.scale_str(vp.scale), 3.5)
    th = 10.0 if nad else (14.0 if podtytul else 10.5)
    zaj = [tuple(float(v) for v in r) for r in obrys_widoku(vp)] if kieszenie else []
    return Widok(nazwa, float(w), float(h), float(tw), th, nad, zaj)


# ================================================================================================ wolne prostokąty
def _przec(a, b, eps: float = 1e-6) -> bool:
    return a[0] < b[2] - eps and b[0] < a[2] - eps and a[1] < b[3] - eps and b[1] < a[3] - eps


def _zawiera(a, b, eps: float = 1e-6) -> bool:
    return a[0] <= b[0] + eps and a[1] <= b[1] + eps and a[2] >= b[2] - eps and a[3] >= b[3] - eps


class Wolne:
    """Zbiór maksymalnych wolnych prostokątów (MaxRects) w polu arkusza [mm]."""

    def __init__(self, rect):
        self.free = [tuple(map(float, rect))] if rect[2] > rect[0] and rect[3] > rect[1] else []

    def zajmij(self, r):
        new = []
        for f in self.free:
            if not _przec(f, r):
                new.append(f)
                continue
            if r[0] > f[0]:
                new.append((f[0], f[1], r[0], f[3]))
            if r[2] < f[2]:
                new.append((r[2], f[1], f[2], f[3]))
            if r[1] > f[1]:
                new.append((f[0], f[1], f[2], r[1]))
            if r[3] < f[3]:
                new.append((f[0], r[3], f[2], f[3]))
        new = [f for f in new if f[2] - f[0] > 1.0 and f[3] - f[1] > 1.0]
        new.sort(key=lambda f: (-(f[2] - f[0]) * (f[3] - f[1]), f))
        out = []
        for f in new:
            if not any(_zawiera(g, f) for g in out):
                out.append(f)
        self.free = out

    def miesci(self, r) -> bool:
        return any(_zawiera(f, r) for f in self.free)

    def pozycje(self, w: float, h: float):
        """Kandydaci (x0, y0) lewego dolnego rogu prostokąta w × h: prawy górny róg każdego wolnego prostokąta."""
        for f in self.free:
            if f[2] - f[0] >= w - 1e-6 and f[3] - f[1] >= h - 1e-6:
                yield (f[2] - w, f[3] - h, f)


def _napompuj(r, dl, dd, dp, dg):
    return (r[0] - dl, r[1] - dd, r[2] + dp, r[3] + dg)


# ================================================================================================ grupa widoków
@dataclass
class Grupa:
    """Ułożenie widoków: pozycje lewych dolnych rogów treści względem lewego dolnego rogu grupy."""
    w: float
    h: float
    poz: list                  # [(x, y)] dla kolejnych widoków
    wiersze: list              # [[indeksy]]
    opis: str = ""

    def prostokaty(self, widoki, ox: float, oy: float) -> list[tuple]:
        out = []
        for v, (x, y) in zip(widoki, self.poz):
            for r in v.prostokaty():
                out.append((ox + x + r[0], oy + y + r[1], ox + x + r[2], oy + y + r[3]))
        return out


def _grupa_z_wierszy(widoki, wiersze, gap: float = GAP_V) -> Grupa:
    rows = []
    for idx in wiersze:
        vs = [widoki[i] for i in idx]
        rw = sum(v.slot_w for v in vs) + gap * (len(vs) - 1)
        dol = max(v.dol for v in vs)
        gora = max(v.gora for v in vs)
        rows.append((idx, rw, dol, gora))
    W = max(r[1] for r in rows)
    H = sum(r[2] + r[3] for r in rows) + gap * (len(rows) - 1)
    poz = [None] * len(widoki)
    y_top = H
    for idx, rw, dol, gora in rows:
        base = y_top - gora                       # linia dolna treści w wierszu
        x = (W - rw) / 2.0
        for i in idx:
            poz[i] = (x, base)
            x += widoki[i].slot_w + gap
        y_top = base - dol - gap
    opis = "wiersz" if len(rows) == 1 else ("kolumna" if all(len(r[0]) == 1 for r in rows) else
                                            f"siatka {len(rows)} wiersze")
    return Grupa(W, H, poz, [list(r[0]) for r in rows], opis)


def uklady_widokow(widoki: list[Widok], max_warianty: int = 6) -> list[Grupa]:
    """Warianty ułożenia widoków (kolejność zachowana): wiersz, kolumna i siatki r wierszy (podział
    minimalizujący najszerszy wiersz). Dla 1 widoku — jeden wariant."""
    n = len(widoki)
    if n == 0:
        return [Grupa(0.0, 0.0, [], [], "brak")]
    if n == 1:
        return [_grupa_z_wierszy(widoki, [[0]])]
    out = []
    ws = [v.slot_w for v in widoki]
    for r in range(1, n + 1):
        best = None
        if n <= 9:
            import itertools
            for cuts in itertools.combinations(range(1, n), r - 1):
                b = (0,) + cuts + (n,)
                rows = [list(range(b[i], b[i + 1])) for i in range(r)]
                mw = max(sum(ws[i] for i in rw) + GAP_V * (len(rw) - 1) for rw in rows)
                g = _grupa_z_wierszy(widoki, rows)
                key = (mw, g.w * g.h)
                if best is None or key < best[0]:
                    best = (key, g)
        else:
            per = math.ceil(n / r)
            rows = [list(range(i, min(n, i + per))) for i in range(0, n, per)]
            best = (None, _grupa_z_wierszy(widoki, rows))
        out.append(best[1])
    out.sort(key=lambda g: (g.w * g.h, g.w))
    if len(out) > max_warianty:                     # zawsze: wiersz i kolumna + najmniejsze pola
        keep = out[:max_warianty - 2] + [g for g in out if g.opis in ("wiersz", "kolumna")]
        out = sorted({id(g): g for g in keep}.values(), key=lambda g: (g.w * g.h, g.w))
    return out


# ================================================================================================ upakowanie
@dataclass
class Rozmieszczenie:
    ok: bool
    W: float
    H: float
    grupa: Grupa | None = None
    widoki: list = field(default_factory=list)       # [(x, y)] lewe dolne rogi treści widoków [mm arkusza]
    bloki: list = field(default_factory=list)        # [(Blok, x, y_top, w)] — wywołania fn(sh, x, y_top, w)
    prostokaty: list = field(default_factory=list)   # [(rodzaj, nazwa, rect)] — kontrola nakładania
    tabliczka: tuple = ()
    brak: str = ""


def rama(W: float, H: float) -> tuple:
    return (MARG_L, MARG, W - MARG, H - MARG)


def _umiesc_blok(wolne: Wolne, b: Blok, szer: float, wys: float):
    """Najlepsza pozycja (x0, y0) prostokąta bloku: najbardziej na prawo, potem najwyżej (kolumny od tabliczki
    w lewo, w kolumnie od góry)."""
    best = None
    for x0, y0, f in wolne.pozycje(szer, wys):
        key = (-round(f[2] / 5.0), -round(f[3] / 5.0), -f[2], -f[3], round(x0, 3), round(y0, 3))
        if best is None or key < best[0]:
            best = (key, x0, y0)
    return None if best is None else best[1:]


def pakuj(W: float, H: float, widoki: list[Widok], grupa: Grupa, bloki: list[Blok], tb_h: float,
          przes: tuple = (0.0, 0.0), gap_vb: float = GAP_VB) -> Rozmieszczenie:
    """Rozmieszczenie na arkuszu W × H. ``przes`` — przesunięcie grupy widoków od lewego górnego rogu pola."""
    fx0, fy0, fx1, fy1 = rama(W, H)
    R = Rozmieszczenie(False, W, H, grupa)
    tb = (fx1 - TB_W, fy0, fx1, fy0 + tb_h)
    R.tabliczka = tb
    if tb[3] > fy1 - PAD_B or fx1 - fx0 < TB_W:
        R.brak = "tabliczka nie mieści się w ramce"
        return R
    R.prostokaty.append(("tabliczka", "tabliczka", tb))
    ox = fx0 + PAD_V + przes[0]
    oy = fy1 - PAD_V - grupa.h - przes[1]
    if grupa.poz:
        if ox + grupa.w > fx1 - PAD_B + 1e-6 or oy < fy0 + PAD_B - 1e-6:
            R.brak = "widoki nie mieszczą się w ramce"
            return R
        vr = grupa.prostokaty(widoki, ox, oy)
        tbz = _napompuj(tb, gap_vb, 0, 0, gap_vb)
        if any(_przec(r, tbz) for r in vr):
            R.brak = "widoki kolidują z tabliczką"
            return R
        for v, (x, y) in zip(widoki, grupa.poz):
            R.widoki.append((ox + x, oy + y))
            for r in v.prostokaty():               # zajętość (pasy treści + tytuł) — bloki mogą wejść w kieszenie
                R.prostokaty.append(("widok", v.nazwa, (ox + x + r[0], oy + y + r[1], ox + x + r[2], oy + y + r[3])))
    wolne = Wolne((fx0 + PAD_B, fy0 + PAD_B, fx1, fy1 - PAD_B))
    wolne.zajmij(_napompuj(tb, GAP_C, GAP_B, 0, GAP_B))
    if grupa.poz:
        for r in vr:
            wolne.zajmij(_napompuj(r, gap_vb, gap_vb, gap_vb, gap_vb))
    for b in bloki:
        if b.uwagi is not None:
            if not _pakuj_uwagi(wolne, b, R):
                R.brak = f"blok „{b.nazwa}” nie mieści się"
                return R
            continue
        szer, wys = b.szer, b.wys
        pos = None
        if b.kotwica == "nad_tabliczka":
            r = (fx1 - szer, tb[3] + GAP_B, fx1, tb[3] + GAP_B + wys)
            if wolne.miesci(r):
                pos = (r[0], r[1])
        if pos is None:
            pos = _umiesc_blok(wolne, b, szer, wys)
        if pos is None:
            R.brak = f"blok „{b.nazwa}” ({szer:.0f}×{wys:.0f} mm) nie mieści się"
            return R
        _dodaj_blok(wolne, R, b, pos[0], pos[1])
    R.ok = True
    return R


def _dodaj_blok(wolne: Wolne, R: Rozmieszczenie, b: Blok, x0: float, y0: float):
    rect = (x0, y0, x0 + b.szer, y0 + b.wys)
    wolne.zajmij(_napompuj(rect, GAP_C, GAP_B, GAP_C, GAP_B))
    R.bloki.append((b, x0 + b.dx0, y0 + b.h, b.w))
    R.prostokaty.append(("blok", b.nazwa, rect))


def _pakuj_uwagi(wolne: Wolne, b: Blok, R: Rozmieszczenie) -> bool:
    """Uwagi: w całości, a gdy się nie mieszczą — częściami (najdłuższa część mieszcząca się w najlepszym miejscu)."""
    U = b.uwagi
    n = len(U.lines)
    i0 = 0
    while i0 < n:
        placed = False
        for k in range(n, i0, -1):
            hh = U.wysokosc(i0, k)
            pos = _umiesc_blok(wolne, b, U.w, hh)
            if pos is not None:
                part = Blok(f"{b.nazwa}[{i0 + 1}–{k}]", U.fn(i0, k), U.w, hh)
                _dodaj_blok(wolne, R, part, pos[0], pos[1])
                i0 = k
                placed = True
                break
        if not placed:
            return False
    return True


# ================================================================================================ dobór formatu
def min_szerokosc(H: float, widoki, grupy, bloki, tb_h: float, o: dict):
    """Najmniejsza szerokość arkusza o wysokości H mieszcząca treść: (W, grupa, rozmieszczenie) lub None."""
    Wmax = float(o["max_dlugosc"])
    gap = float(o.get("odstep_widok_blok", GAP_VB))
    Hf = H - 2 * MARG
    a_b = sum(b.szer * b.wys for b in bloki if b.uwagi is None)
    a_b += sum(b.uwagi.wysokosc(0, len(b.uwagi.lines)) * b.uwagi.w for b in bloki if b.uwagi is not None)
    best = None
    for g in grupy:
        if g.h + PAD_V + PAD_B > Hf:
            continue
        lb = max(MARG_L + PAD_V + g.w + PAD_B + MARG, MARG_L + TB_W + MARG,
                 (g.w * g.h + a_b + TB_W * tb_h) / (Hf - PAD_B) + MARG_L + MARG)
        if best is not None and lb >= best[0]:
            continue
        W = math.ceil(lb / 5.0) * 5.0
        step, prev, r = 20.0, None, None
        while W <= Wmax + 1e-6:
            r = pakuj(W, H, widoki, g, bloki, tb_h, gap_vb=gap)
            if r.ok:
                break
            prev, W = W, W + step
        if r is None or not r.ok:
            continue
        if prev is not None:
            Wf = prev + 5.0
            while Wf < W - 1e-6:
                rf = pakuj(Wf, H, widoki, g, bloki, tb_h, gap_vb=gap)
                if rf.ok:
                    W, r = Wf, rf
                    break
                Wf += 5.0
        if best is None or W < best[0] - 1e-6:
            best = (W, g, r)
    return best


def _pakuj_wysrodkuj(W, H, widoki, g, bloki, tb_h, W_need, gap_vb: float = GAP_VB):
    """Pakowanie na W × H z grupą widoków wyśrodkowaną w nadwyżce szerokości / wysokości (gdy się da)."""
    extra = max(0.0, W - W_need)
    slack = max(0.0, (H - 2 * MARG) - PAD_V - PAD_B - g.h)
    for p in ((extra / 2.0, slack / 2.0), (extra / 2.0, 0.0), (0.0, slack / 2.0), (0.0, 0.0)):
        r = pakuj(W, H, widoki, g, bloki, tb_h, p, gap_vb)
        if r.ok:
            return r
    return None


@dataclass
class Uklad:
    """Wynik doboru: format, rozmieszczenie, koszt i plan składania."""
    nazwa: str                     # „A2”, „A3×3”, „780×594”
    W: float
    H: float
    orientacja: str | None         # dla Sheet(): standardowe — landscape/portrait; niestandardowe — None
    standard: bool
    tryb: str
    roz: Rozmieszczenie
    koszt: float = 0.0
    skladanie: dict = field(default_factory=dict)
    kandydaci: list = field(default_factory=list)
    wypelnienie_szac: float = 0.0

    @property
    def sheet_fmt(self) -> str:
        """Argument ``fmt_name`` dla ``Sheet``."""
        return self.nazwa.replace("×", "x") if self.standard else f"{self.W:.0f}x{self.H:.0f}"

    def info(self) -> dict:
        return dict(format=self.nazwa, wymiary_mm=[round(self.W, 1), round(self.H, 1)],
                    pole_m2=round(self.W * self.H / 1e6, 4), standardowy=self.standard, tryb=self.tryb,
                    koszt=round(self.koszt, 4), wypelnienie_szac=round(self.wypelnienie_szac, 3),
                    uklad_widokow=self.roz.grupa.opis if self.roz.grupa else "", skladanie=self.skladanie,
                    kandydaci=self.kandydaci[:6])


def koszt(W: float, H: float, standard: bool, o: dict, tb_h: float | None = None) -> tuple[float, dict]:
    k, oc = kara_skladania(W, H, o, tb_h)
    return W * H / 1e6 * (1.0 + k) * (1.0 if standard else 1.0 + float(o["kara_niestandard"])), oc


def wypelnienie_ukladu(R: Rozmieszczenie, res: float = 2.0) -> float:
    """Szacunkowe wypełnienie: pole sumy prostokątów widoków, bloków i tabliczki / pole wewnątrz ramki."""
    fx0, fy0, fx1, fy1 = rama(R.W, R.H)
    nx, ny = int(math.ceil((fx1 - fx0) / res)), int(math.ceil((fy1 - fy0) / res))
    occ = np.zeros((ny, nx), bool)
    for _k, _n, r in R.prostokaty:
        c0, c1 = int((r[0] - fx0) / res), int(math.ceil((r[2] - fx0) / res))
        r0, r1 = int((r[1] - fy0) / res), int(math.ceil((r[3] - fy0) / res))
        occ[max(0, r0):max(0, r1), max(0, c0):max(0, c1)] = True
    return float(occ.sum()) / (nx * ny)


def rozmiesc(widoki: list[Widok], bloki: list[Blok], tb_h: float, o: dict | None = None,
             fmt=None) -> Uklad | None:
    """Dobór formatu i rozmieszczenie treści arkusza. ``fmt`` — wartość pola ``format`` (domyślnie z ``o``).
    Zwraca None, gdy nic się nie mieści (wtedy ``sheets.py`` używa układu klasycznego z uwagą)."""
    o = opcje(o)
    tryb, jawny = tryb_formatu(o["format"] if fmt is None else fmt)
    grupy = uklady_widokow(widoki)
    gap = float(o.get("odstep_widok_blok", GAP_VB))
    if tryb == "jawny":
        nm, W, H = jawny
        std = nazwa_standardowa(W, H)
        for g in grupy:
            r = pakuj(W, H, widoki, g, bloki, tb_h, gap_vb=gap)
            if r.ok:
                need = _dociagnij(W, H, widoki, g, bloki, tb_h, gap)
                r = _pakuj_wysrodkuj(W, H, widoki, g, bloki, tb_h, need, gap) or r
                k, oc = koszt(W, H, std is not None, o, tb_h)
                return Uklad(std[0] if std else nm, W, H, std[1] if std else None, std is not None, tryb, r, k, oc,
                             [], wypelnienie_ukladu(r))
        return None
    stdf = formaty_standardowe(float(o["max_wysokosc"]), float(o["max_dlugosc"]))
    heights = sorted({float(h) for h in o["wysokosci"] if float(h) <= float(o["max_wysokosc"]) + 1e-6}
                     | {f[2] for f in stdf})
    cands = []
    for H in heights:
        mw = min_szerokosc(H, widoki, grupy, bloki, tb_h, o)
        if mw is None:
            continue
        W_need, g, _r = mw
        opts = []
        for nm, Ws, Hs, ori in stdf:
            if abs(Hs - H) < 0.5 and Ws >= W_need - 1e-6:
                k, oc = koszt(Ws, Hs, True, o, tb_h)
                opts.append((k, nm, Ws, ori, True, oc))
        if tryb == "ekonomiczny" and any(abs(float(h) - H) < 0.5 for h in o["wysokosci"]):
            for L in dlugosci_kandydaci(W_need, o):
                std = nazwa_standardowa(L, H)
                k, oc = koszt(L, H, std is not None, o, tb_h)
                opts.append((k, std[0] if std else f"{L:.0f}×{H:.0f}", L, std[1] if std else None, std is not None,
                             oc))
        opts.sort(key=lambda t: (round(t[0], 6), not t[4], t[2]))
        for k, nm, L, ori, is_std, oc in opts[:12]:
            r = _pakuj_wysrodkuj(L, H, widoki, g, bloki, tb_h, W_need, gap)
            if r is not None:
                cands.append(Uklad(nm, L, H, ori, is_std, tryb, r, k, oc))
                break
    if not cands:
        return None
    cands.sort(key=lambda u: (round(u.koszt, 6), not u.standard, u.W * u.H, u.W))
    best = cands[0]
    best.kandydaci = [dict(format=u.nazwa, wymiary_mm=[round(u.W), round(u.H)], koszt=round(u.koszt, 4),
                           pole_m2=round(u.W * u.H / 1e6, 4), skladanie=u.skladanie["ocena"]) for u in cands]
    best.wypelnienie_szac = wypelnienie_ukladu(best.roz)
    return best


def _dociagnij(W, H, widoki, g, bloki, tb_h, gap_vb: float = GAP_VB) -> float:
    """Najmniejsza szerokość ≤ W, przy której treść się mieści (do wyśrodkowania w formacie jawnym)."""
    lo = MARG_L + TB_W + MARG
    Wn = W
    while Wn - 20.0 >= lo and pakuj(Wn - 20.0, H, widoki, g, bloki, tb_h, gap_vb=gap_vb).ok:
        Wn -= 20.0
    return Wn


def sprawdz_nakladanie(R: Rozmieszczenie, tol: float = 0.5) -> list[str]:
    """Kontrola rozmieszczenia: nakładanie się prostokątów (widoki, bloki, tabliczka) i wyjście poza ramkę."""
    bledy = []
    fx0, fy0, fx1, fy1 = rama(R.W, R.H)
    P = R.prostokaty
    for i, (k1, n1, a) in enumerate(P):
        if a[0] < fx0 - tol or a[1] < fy0 - tol or a[2] > fx1 + tol or a[3] > fy1 + tol:
            bledy.append(f"{k1} „{n1}” poza ramką {tuple(round(v, 1) for v in a)}")
        for k2, n2, b in P[i + 1:]:
            if k1 == k2 == "widok" and n1 == n2:
                continue                           # pasy zajętości jednego widoku
            if _przec(a, b, tol):
                bledy.append(f"{k1} „{n1}” nakłada się na {k2} „{n2}”")
    return bledy


# ================================================================================================ pomiar arkusza
_METRYKI = None


def wypelnienie_pdf(pdf) -> dict | None:
    """Wypełnienie arkusza zmierzone na PDF tą samą metodą co ``tools/metryki_arkuszy.py`` (``analyze_pdf``:
    obwiednie bloków treści z PyMuPDF, domknięcie 6 mm, tabliczka jako stały blok). None — narzędzie niedostępne."""
    global _METRYKI
    from pathlib import Path
    if _METRYKI is None:
        import importlib.util
        p = Path(__file__).resolve().parents[3] / "tools" / "metryki_arkuszy.py"
        if not p.exists():
            _METRYKI = False
        else:
            spec = importlib.util.spec_from_file_location("_lamela_metryki_arkuszy", p)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            _METRYKI = mod
    if not _METRYKI:
        return None
    r = _METRYKI.analyze_pdf(Path(pdf))
    e = r["pusty_prostokat"]
    return dict(wypelnienie=round(r["wypelnienie"], 3), wypelnienie_rys=round(r["wypelnienie_rys"], 3),
                wypelnienie_kontur=round(r["wypelnienie_kontur"], 3), pole_arkusza_m2=round(r["pole_arkusza_m2"], 4),
                pole_ramki_m2=round(r["pole_ramki_m2"], 4),
                pusty_prostokat_mm=[round(e["w"]), round(e["h"])],
                przyciety_mm=[round(min(r["przyciety"]["W"], r["W"])), round(min(r["przyciety"]["H"], r["H"]))],
                metoda="tools/metryki_arkuszy.py (analyze_pdf)")
