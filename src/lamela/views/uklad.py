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
``max_dlugosc`` (2400), ``wolne_obszary`` (true), ``odstep_kieszeni`` (12).
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
    max_wysokosc=914.0, wolne_obszary=True, odstep_kieszeni=12.0,
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
    return h, max(0.0, X - float(e[0])), max(0.0, float(e[2]) - X - w), max(0.0, float(e[3]) - Y)


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
        pad = 2.0
        return pad + 3.5 + 3.5 * 1.8 + sum(self._item_h(i) for i in range(i0, i1)) - self.th * 0.9 + pad - 1.0

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
    zaj = obrys_widoku(vp) if kieszenie else []
    return Widok(nazwa, w, h, tw, th, nad, zaj)


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
            poz[i] = (x + (widoki[i].slot_w - widoki[i].slot_w) / 2.0, base)
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
    return out[:max_warianty]
