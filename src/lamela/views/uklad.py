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
   / „słabe”, ``kara_skladania``). Długości „ładnie” składane (pasy pośrednie harmonijki 180–210 mm, równe:
   570–630, 930–1050, 1300–1470 … mm; wysokość 297 / 594 / 891 mm) wygrywają, gdy dopłata papieru jest mała.
3. **Upakowanie** (dla danego W × H): tabliczka w prawym dolnym rogu ramki (z tabelą zmian nad nią), widoki
   w grupie (wiersz / kolumna / siatka — wariant o najmniejszym polu), bloki kolumny opisowej (legendy, tabele,
   uwagi, róża + podziałka) rozmieszczane algorytmem wolnych prostokątów (MaxRects): najpierw kolumna nad tabliczką,
   potem kolejne kolumny w lewo, pas pod widokami i wolne obszary w obrysie widoków („kieszenie” przy krawędzi
   obwiedni — zajętość widoku liczona pasami 5 mm z prymitywów rzutni, odstęp ≥ ``odstep_widok_blok``); gdy bloki
   zajmują kilka kolumn, są przestawiane tak, aby kolejność listy czytała się kolumnami od lewej, w kolumnie od góry.
   Uwagi — w całości, a gdy się nie mieszczą — w najmniejszej liczbie części (≤ ``max_czesci_uwag``, ≥ 2 pozycje
   w części, gdy się da; numeracja ciągła, „cd.”) ułożonych w kolejności czytania: część k+1 pod częścią k w tej
   samej kolumnie albo w kolumnie na prawo; każda dodatkowa część podnosi koszt (``kara_czesci_uwag``). Róża
   kierunków i podziałka — jeden wiersz bezpośrednio nad tabliczką (węższy, gdy trzeba ominąć znak centrujący).
   **Znaki centrujące** (ISO 5457 4.3: osie arkusza, 10 mm za ramkę): strefy znaków są rezerwowane dla bloków,
   tytuł widoku trafiający na znak jest przesuwany w prawo; gdy rezerwacja pogorszyłaby upakowanie (więcej części
   uwag lub kolumn), bloki stoją jak bez niej, a znak jest skracany na arkuszu
   (``Sheet.przytnij_znaki_centrujace`` — nigdy nie dotyka treści). Odstępy: widok–widok ≥ 12 mm, widok–blok
   ≥ 10 mm, blok–blok ≥ 5 mm, treść–znak ≥ 1,5 mm; nic się nie nakłada (``sprawdz_nakladanie``).
4. **Tryby** (``format`` w ``wspolne`` lub w arkuszu): ``auto`` = ``ekonomiczny`` (wszystkie kandydaty),
   ``standardowy`` (tylko ISO 216 + wydłużone, nowe upakowanie), ``klasyczny`` (dawny algorytm ``sheets.py``:
   pierwszy mieszczący się z listy FORMATS, kolumna 180 mm na całą wysokość), nazwa formatu (``A2``, ``A3x3`` —
   jak dotąd), wymiary ``[H, L]`` lub ``"780x594"`` (L × H).

Parametry (``wspolne`` lub arkusz, wszystkie opcjonalne): ``format``, ``wysokosci``, ``krok_dlugosci`` (10),
``modul_skladania`` (``auto`` — wszystkie długości do +35 %, wybór kosztem z oceną składania; liczba m — tylko
L = 210 + m·n, np. 190; 0 — tylko najmniejsza długość), ``max_wysokosc`` (914),
``kara_niestandard`` (0,03), ``kara_skladania`` ({dobre: 0, poprawne: 0,04, słabe: 0,10} — na kierunek),
``max_dlugosc`` (2400), ``wolne_obszary`` (true — bloki także w pustych narożnikach obwiedni widoków),
``odstep_widok_blok`` (10 mm), ``kara_czesci_uwag`` (0,02 — na każdą część uwag ponad jedną),
``max_czesci_uwag`` (4), ``kolejnosc_uwag`` (``czytania`` | ``dowolna`` — dawny podział: najmniej papieru, bez
warunku kolejności i bez przestawiania kolumn), ``znaki_centrujace`` (``auto`` | ``rezerwuj`` — zawsze
rezerwacja stref | ``skracaj`` — bez rezerwacji, znaki skracane).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from ..draft import text as T
from ..draft.sheet import (ISO_A, ISO_ELONGATED, ZNAK_CENTR_DL, ZNAK_CENTR_GR, ZNAK_CENTR_ODSTEP, custom_size,
                           sheet_size)
from ..draft.skladanie import ocena_skladania

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
    max_wysokosc=914.0, wolne_obszary=True, odstep_widok_blok=GAP_VB, kara_czesci_uwag=0.02, max_czesci_uwag=4,
    znaki_centrujace="auto", kolejnosc_uwag="czytania",
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
    w_min: float = 0.0              # > 0: blok może być rysowany węższy (do w_min) — np. wiersz nad tabliczką

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


def blok(nazwa: str, fn, w: float = TB_W, kotwica: str = "", w_min: float = 0.0) -> Blok:
    h, dx0, dx1, dy1 = zmierz_blok(fn, w)
    return Blok(nazwa, fn, w, h, dx0, dx1, dy1, kotwica, w_min=w_min)


def _wezszy(b: Blok, w: float) -> Blok:
    """Wariant bloku rysowany z szerokością ``w`` (pomiar z pamięcią podręczną)."""
    c = b.__dict__.setdefault("_wezsze", {})
    k = round(float(w), 1)
    if k not in c:
        h, dx0, dx1, dy1 = zmierz_blok(b.fn, k)
        c[k] = Blok(b.nazwa, b.fn, k, h, dx0, dx1, dy1, b.kotwica, w_min=b.w_min)
    return c[k]


def bloki_z_kolumny(pary, w: float = TB_W, gap: float = GAP_B) -> list[Blok]:
    """Bloki kolumny opisowej z listy ``(nazwa, fn)`` z pomiarem sekwencyjnym jak ``sheets.Column``: bloki zależne od
    poprzednich (stan arkusza — np. legenda rysowana raz na arkusz, ciąg dalszy wyników bez nagłówka w detalach) są
    łączone z poprzednim blokiem w jeden blok złożony, a bloki, które w sekwencji nic nie rysują — pomijane.
    Dzięki temu rozmieszczenie w wielu kolumnach nie rozrywa bloków, które dotąd rysowały się jeden pod drugim."""
    from ..draft.sheet import Sheet
    seq = Sheet("A0", draw_frame=False)
    X, y = 100.0, 5000.0
    grupy = []
    for nm, fn in pary:
        h_sam = zmierz_blok(fn, w)[0]
        yb = float(fn(seq, X, y, w))
        h_seq = y - yb
        y = yb - gap
        if h_seq <= 0.05:
            continue                                   # nic nie narysował (np. legenda już jest na arkuszu)
        if grupy and abs(h_seq - h_sam) > 0.5:
            grupy[-1].append((nm, fn))                 # zależny od poprzednich — ciąg dalszy
        else:
            grupy.append([(nm, fn)])
    out = []
    for g in grupy:
        if len(g) == 1:
            out.append(blok(g[0][0], g[0][1], w))
            continue
        fns = [f for _n, f in g]

        def zlozony(sh, x, yy, ww, fns=fns):
            for i, f in enumerate(fns):
                yy = float(f(sh, x, yy, ww)) - (gap if i < len(fns) - 1 else 0.0)
            return yy
        out.append(blok(" + ".join(n for n, _f in g), zlozony, w))
    return out


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

    def tytul_rect(self, dx: float = 2.0) -> tuple:
        """Prostokąt tytułu względem lewego dolnego rogu treści (``dx`` — odsunięcie od lewej krawędzi)."""
        if self.tytul_nad:
            return (dx, self.h, dx + self.tytul_w, self.h + self.tytul_h)
        return (dx, -self.tytul_h, dx + self.tytul_w, 0.0)

    def prostokaty(self, dx: float = 2.0) -> list[tuple]:
        """Zajętość względem lewego dolnego rogu treści: pasy treści (lub cały prostokąt) + tytuł (ostatni)."""
        r = list(self.zajete) or [(0.0, 0.0, self.w, self.h)]
        r.append(self.tytul_rect(dx))
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

    def kopia(self) -> "Wolne":
        w = Wolne((0.0, 0.0, 0.0, 0.0))
        w.free = list(self.free)
        return w

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

    def prostokaty(self, widoki, ox: float, oy: float, tdx=None) -> list[tuple]:
        out = []
        for i, (v, (x, y)) in enumerate(zip(widoki, self.poz)):
            for r in v.prostokaty(tdx[i] if tdx else 2.0):
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
    tytuly_dx: list = field(default_factory=list)    # odsunięcia tytułów widoków od lewej krawędzi treści [mm]
    znaki: bool = False                              # strefy znaków centrujących zarezerwowane
    czesci_uwag: int = 0                             # części uwag (wszystkich bloków uwag)
    bloki_uwag: int = 0

    @property
    def dodatkowe_czesci(self) -> int:
        """Części uwag ponad jedną na blok uwag (rozdrobnienie — kara w koszcie)."""
        return max(0, self.czesci_uwag - self.bloki_uwag)


def rama(W: float, H: float) -> tuple:
    return (MARG_L, MARG, W - MARG, H - MARG)


def strefy_znakow(W: float, H: float, odst: float = ZNAK_CENTR_ODSTEP) -> dict:
    """Strefy znaków centrujących w polu rysunkowym (linia 0,7 mm na osi arkusza, 10 mm za ramkę + odstęp):
    {strona: (x0, y0, x1, y1)} — ``g``, ``d`` (oś W/2), ``l``, ``p`` (oś H/2); jak ``draft.sheet.znaki_centrujace``."""
    fx0, fy0, fx1, fy1 = rama(W, H)
    a = ZNAK_CENTR_GR / 2.0 + odst
    d = ZNAK_CENTR_DL + odst
    cx, cy = W / 2.0, H / 2.0
    return {"g": (cx - a, fy1 - d, cx + a, fy1), "d": (cx - a, fy0, cx + a, fy0 + d),
            "l": (fx0, cy - a, fx0 + d, cy + a), "p": (fx1 - d, cy - a, fx1, cy + a)}


def _tytuly_od_znakow(widoki, grupa, ox: float, oy: float, strefy: dict) -> list:
    """Odsunięcia tytułów widoków: tytuł trafiający na strefę znaku centrującego — przesunięty w prawo za znak,
    jeśli mieści się w szerokości miejsca widoku (poza nim mógłby wejść na sąsiedni widok); inaczej 2 mm."""
    out = []
    for v, (x, y) in zip(widoki, grupa.poz):
        vx, vy = ox + x, oy + y

        def trafia(dx):
            t = v.tytul_rect(dx)
            tr = (vx + t[0], vy + t[1], vx + t[2], vy + t[3])
            return [z for z in strefy.values() if _przec(tr, z)]
        dx = 2.0
        hit = trafia(dx)
        if hit:
            for z in sorted(hit, key=lambda z: z[2]):
                nd = z[2] + 1.0 - vx
                if nd + v.tytul_w <= v.slot_w + 1e-6 and not trafia(nd):
                    dx = nd
                    break
        out.append(dx)
    return out


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
          przes: tuple = (0.0, 0.0), gap_vb: float = GAP_VB, znaki="auto", max_czesci: int = 4,
          kolejnosc: str = "czytania") -> Rozmieszczenie:
    """Rozmieszczenie na arkuszu W × H. ``przes`` — przesunięcie grupy widoków od lewego górnego rogu pola.
    ``znaki``: ``auto`` — z rezerwacją stref znaków centrujących, chyba że bez niej upakowanie jest lepsze (mniej
    części uwag / kolumn bloków; wtedy znaki skraca ``Sheet.przytnij_znaki_centrujace``); ``rezerwuj`` / True;
    ``skracaj`` / False."""
    tr = str(znaki).lower()
    args = (W, H, widoki, grupa, bloki, tb_h, przes, gap_vb)
    if znaki is True or tr in ("rezerwuj", "tak"):
        return _pakuj(*args, True, max_czesci, kolejnosc)
    if znaki is False or tr in ("skracaj", "nie", "bez"):
        return _pakuj(*args, False, max_czesci, kolejnosc)
    r1 = _pakuj(*args, True, max_czesci, kolejnosc)
    r0 = _pakuj(*args, False, max_czesci, kolejnosc)
    if r1.ok and (not r0.ok or _jakosc(r1)[:2] <= _jakosc(r0)[:2]):
        return r1
    return r0 if r0.ok else r1


def _jakosc(R: Rozmieszczenie) -> tuple:
    """Ocena upakowania (mniej = lepiej): części uwag, kolumny bloków, liczba bloków, brak rezerwacji znaków."""
    rb = [r for k, _n, r in R.prostokaty if k == "blok"]
    return (R.dodatkowe_czesci, len(_kolumny(rb)), len(R.bloki), 0 if R.znaki else 1)


def _pakuj(W, H, widoki, grupa, bloki, tb_h, przes, gap_vb, znaki: bool, max_czesci: int,
           kolejnosc: str = "czytania") -> Rozmieszczenie:
    fx0, fy0, fx1, fy1 = rama(W, H)
    R = Rozmieszczenie(False, W, H, grupa, znaki=znaki)
    tb = (fx1 - TB_W, fy0, fx1, fy0 + tb_h)
    R.tabliczka = tb
    if tb[3] > fy1 - PAD_B or fx1 - fx0 < TB_W:
        R.brak = "tabliczka nie mieści się w ramce"
        return R
    R.prostokaty.append(("tabliczka", "tabliczka", tb))
    strefy = strefy_znakow(W, H) if znaki else {}
    ox = fx0 + PAD_V + przes[0]
    oy = fy1 - PAD_V - grupa.h - przes[1]
    if grupa.poz:
        if ox + grupa.w > fx1 - PAD_B + 1e-6 or oy < fy0 + PAD_B - 1e-6:
            R.brak = "widoki nie mieszczą się w ramce"
            return R
        tdx = _tytuly_od_znakow(widoki, grupa, ox, oy, strefy) if strefy else [2.0] * len(widoki)
        vr = grupa.prostokaty(widoki, ox, oy, tdx)
        tbz = _napompuj(tb, gap_vb, 0, 0, gap_vb)
        if any(_przec(r, tbz) for r in vr):
            R.brak = "widoki kolidują z tabliczką"
            return R
        R.tytuly_dx = tdx
        for i, (v, (x, y)) in enumerate(zip(widoki, grupa.poz)):
            R.widoki.append((ox + x, oy + y))
            rs = v.prostokaty(tdx[i])              # zajętość (pasy treści + tytuł) — bloki mogą wejść w kieszenie
            for j, r in enumerate(rs):
                R.prostokaty.append(("tytul" if j == len(rs) - 1 else "widok", v.nazwa,
                                     (ox + x + r[0], oy + y + r[1], ox + x + r[2], oy + y + r[3])))
    wolne = Wolne((fx0 + PAD_B, fy0 + PAD_B, fx1, fy1 - PAD_B))
    wolne.zajmij(_napompuj(tb, GAP_C, GAP_B, 0, GAP_B))
    if grupa.poz:
        for r in vr:
            wolne.zajmij(_napompuj(r, gap_vb, gap_vb, gap_vb, gap_vb))
    for st, z in strefy.items():
        wolne.zajmij(z)
        R.prostokaty.append(("znak", st, z))
    for b in bloki:                                # wiersz nad tabliczką (róża, podziałka) — przed pozostałymi
        if not b.kotwica:
            continue
        pos, bb = _umiesc_kotwice(wolne, b, tb, fx1)
        if pos is None:
            R.brak = f"blok „{b.nazwa}” ({b.szer:.0f}×{b.wys:.0f} mm) nie mieści się"
            return R
        _dodaj_blok(wolne, R, bb, pos[0], pos[1])
    baza, n_b, n_p = wolne.kopia(), len(R.bloki), len(R.prostokaty)
    kolejne = [b for b in bloki if not b.kotwica]
    for b in kolejne:
        if b.uwagi is not None:
            ok = (_pakuj_uwagi_dowolnie(wolne, b, R) if kolejnosc == "dowolna"
                  else _pakuj_uwagi(wolne, b, R, max_czesci))
            if not ok:
                R.brak = f"blok „{b.nazwa}” nie mieści się"
                return R
            continue
        pos = _umiesc_blok(wolne, b, b.szer, b.wys)
        if pos is None:
            R.brak = f"blok „{b.nazwa}” ({b.szer:.0f}×{b.wys:.0f} mm) nie mieści się"
            return R
        _dodaj_blok(wolne, R, b, pos[0], pos[1])
    R.ok = True
    if kolejnosc != "dowolna":
        _porzadek_czytania(R, baza, kolejne, n_b, n_p)
    return R


def _umiesc_kotwice(wolne: Wolne, b: Blok, tb: tuple, fx1: float):
    """Wiersz bezpośrednio nad tabliczką (prawa krawędź przy ramce); gdy zajęty z prawej (np. strefa znaku
    centrującego) — węższy wariant bloku (``w_min``) z lewą krawędzią jak tabliczka; inaczej najlepsze wolne miejsce."""
    y0 = tb[3] + GAP_B
    r = (fx1 - b.szer, y0, fx1, y0 + b.wys)
    if wolne.miesci(r):
        return (r[0], r[1]), b
    if b.w_min > 0:
        xo = fx1 - b.szer + b.dx0                  # początek rysowania jak w pełnym wariancie
        w = b.w - 2.5
        while w >= b.w_min - 1e-6:
            bn = _wezszy(b, w)
            r = (xo - bn.dx0, y0, xo - bn.dx0 + bn.szer, y0 + bn.wys)
            if wolne.miesci(r):
                return (r[0], r[1]), bn
            w -= 2.5
    pos = _umiesc_blok(wolne, b, b.szer, b.wys)
    return pos, b


def _dodaj_blok(wolne: Wolne, R: Rozmieszczenie, b: Blok, x0: float, y0: float):
    rect = (x0, y0, x0 + b.szer, y0 + b.wys)
    wolne.zajmij(_napompuj(rect, GAP_C, GAP_B, GAP_C, GAP_B))
    R.bloki.append((b, x0 + b.dx0, y0 + b.h, b.w))
    R.prostokaty.append(("blok", b.nazwa, rect))


def _po(a, b, eps: float = 0.5) -> bool:
    """Prostokąt ``b`` stoi po ``a`` w kolejności czytania: w kolumnie na prawo albo pod ``a`` w tej samej kolumnie."""
    if b[0] >= a[2] - eps:
        return True
    ov = min(a[2], b[2]) - max(a[0], b[0])
    return ov > 0.5 * min(a[2] - a[0], b[2] - b[0]) and b[3] <= a[1] + eps


def _kolumny(rects) -> list:
    """Kolumny prostokątów (nakładanie w poziomie > 50 % węższego) od lewej: [[x0, x1, [indeksy]]]."""
    cols = []
    for i, r in enumerate(rects):
        for c in cols:
            if min(c[1], r[2]) - max(c[0], r[0]) > 0.5 * min(c[1] - c[0], r[2] - r[0]):
                c[0], c[1] = min(c[0], r[0]), max(c[1], r[2])
                c[2].append(i)
                break
        else:
            cols.append([r[0], r[2], [i]])
    return sorted(cols, key=lambda c: c[0])


def _max_k(U, i0: int, hmax: float) -> int:
    """Największe k: uwagi i0…k-1 mieszczą się w wysokości ``hmax`` (i0 — gdy nawet jedna się nie mieści)."""
    k = i0
    while k < len(U.lines) and U.wysokosc(i0, k + 1) <= hmax + 1e-6:
        k += 1
    return k


def _pakuj_uwagi(wolne: Wolne, b: Blok, R: Rozmieszczenie, max_czesci: int = 4) -> bool:
    """Uwagi w całości (najlepsze miejsce jak inne bloki), a gdy się nie mieszczą — w najmniejszej liczbie części
    (≤ ``max_czesci``; najpierw ≥ 2 pozycje w części) w kolejności czytania (``_po``): część k+1 pod częścią k
    w tej samej kolumnie albo w kolumnie na prawo. Przeszukiwanie z nawrotami (budżet węzłów)."""
    U = b.uwagi
    n = len(U.lines)
    if n == 0:
        return True
    h = U.wysokosc(0, n)
    pos = _umiesc_blok(wolne, b, U.w, h)
    sol = [(0, n, pos[0], pos[1])] if pos is not None else None
    budzet = [300]
    for P in range(2, min(max_czesci, n) + 1):
        if sol:
            break
        for mp in (2, 1):
            if mp * P <= n:
                sol = _uwagi_szukaj(wolne, U, 0, None, P, mp, budzet)
                if sol:
                    break
    if not sol:
        return False
    for i0, i1, x0, y0 in sol:
        _dodaj_blok(wolne, R, Blok(f"{b.nazwa}[{i0 + 1}–{i1}]", U.fn(i0, i1), U.w, U.wysokosc(i0, i1)), x0, y0)
    R.czesci_uwag += len(sol)
    R.bloki_uwag += 1
    return True


def _pakuj_uwagi_dowolnie(wolne: Wolne, b: Blok, R: Rozmieszczenie) -> bool:
    """Dawny podział (``kolejnosc_uwag: dowolna``): kolejno najdłuższa część mieszcząca się w najlepszym miejscu —
    bez warunku kolejności czytania i bez limitu części (najmniej papieru, części „(cd.)” mogą stać nad
    poprzednimi)."""
    U = b.uwagi
    n, i0 = len(U.lines), 0
    while i0 < n:
        for k in range(n, i0, -1):
            hh = U.wysokosc(i0, k)
            pos = _umiesc_blok(wolne, b, U.w, hh)
            if pos is not None:
                _dodaj_blok(wolne, R, Blok(f"{b.nazwa}[{i0 + 1}–{k}]", U.fn(i0, k), U.w, hh), pos[0], pos[1])
                R.czesci_uwag += 1
                i0 = k
                break
        else:
            return False
    R.bloki_uwag += 1 if n else 0
    return True


def _uwagi_szukaj(wolne: Wolne, U, i0: int, prev, P: int, mp: int, budzet: list):
    """Części uwag i0…n w co najwyżej P częściach po prostokącie ``prev``: [(i0, i1, x0, y0)] albo None."""
    n, w = len(U.lines), U.w
    if i0 >= n:
        return []
    if P <= 0 or budzet[0] <= 0:
        return None
    budzet[0] -= 1
    usable = [f for f in wolne.free if f[2] - f[0] >= w - 1e-6]
    hs = sorted((f[3] - f[1] for f in usable), reverse=True)
    if sum(hs[:P]) < U.wysokosc(i0, n) - 1e-6:           # ograniczenie: nawet P najwyższych pól nie wystarczy
        return None
    cands = []
    for f in usable:
        k = _max_k(U, i0, f[3] - f[1])
        if k <= i0 or (P == 1 and k < n):
            continue
        if k < n:
            if n - k < mp:
                k = n - mp
            if k - i0 < mp:
                continue
        hh = U.wysokosc(i0, k)
        xs = {round(f[2] - w, 6)}
        if prev is not None and f[0] - 1e-6 <= prev[0] <= f[2] - w + 1e-6:
            xs.add(round(prev[0], 6))                     # wyrównanie pod poprzednią częścią
        for x in xs:
            rect = (x, f[3] - hh, x + w, f[3])
            if prev is not None and not _po(prev, rect):
                continue
            ciag = prev is not None and abs(x - prev[0]) < 0.5 and prev[1] - rect[3] < GAP_B + 5.0
            key = (-(k - i0), not ciag, -round(f[2] / 5.0), -round(f[3] / 5.0), -f[2], -f[3], x)
            cands.append((key, x, rect[1], k, rect))
    cands.sort(key=lambda c: c[0])
    tried = []                                     # próbowane miejsca: kolejne kandydatki w innych polach
    for _key, x, y, k, rect in cands:
        if any(_przec(rect, t) for t in tried):
            continue
        tried.append(rect)
        wl = wolne.kopia()
        wl.zajmij(_napompuj(rect, GAP_C, GAP_B, GAP_C, GAP_B))
        sub = _uwagi_szukaj(wl, U, k, rect, P - 1, mp, budzet)
        if sub is not None:
            return [(i0, k, x, y)] + sub
        if len(tried) >= 4 or budzet[0] <= 0:
            break
    return None


def _porzadek_czytania(R: Rozmieszczenie, baza: Wolne, kolejne: list, n_b: int, n_p: int):
    """Gdy bloki (bez wiersza nad tabliczką) zajmują kilka kolumn, a kolejność listy nie czyta się kolumnami od
    lewej i w kolumnie od góry — ponowne ułożenie w tych samych kolumnach (sloty: wolne odcinki kolumn od lewej,
    w kolumnie od góry): kolejne bloki listy i pozycje uwag dzielone na sloty w kolejności tak, aby najbardziej
    wypełniony slot był jak najmniej wypełniony (kolumny wyrównane, bez pustej kolumny obok przepełnionej); część
    uwag „(cd.)” obciążona karą. Przyjmowane, gdy wszystko się mieści, a części uwag nie przybywa."""
    wpisy = R.bloki[n_b:]
    rects = [r for k, _n, r in R.prostokaty[n_p:] if k == "blok"]
    if len(rects) < 2 or len(rects) != len(wpisy):
        return
    cols = _kolumny(rects)
    if len(cols) < 2:
        return
    ci = {i: c for c, col in enumerate(cols) for i in col[2]}
    if all(ci[i + 1] > ci[i] or (ci[i + 1] == ci[i] and _po(rects[i], rects[i + 1])) for i in range(len(rects) - 1)):
        return
    sloty = []                                     # (x0, x1, y_bot, y_top)
    for x0, x1, idx in cols:
        y_lo = min(rects[i][1] for i in idx)
        y_hi = max(rects[i][3] for i in idx)
        scal = []
        for a, b in sorted((f[1], f[3]) for f in baza.free if f[0] <= x0 + 1e-6 and f[2] >= x1 - 1e-6):
            if scal and a <= scal[-1][1] + 1e-6:
                scal[-1][1] = max(scal[-1][1], b)
            else:
                scal.append([a, b])
        sloty += [(x0, x1, a, b) for a, b in sorted(scal, key=lambda t: -t[1]) if b > y_lo + 1e-6 and a < y_hi - 1e-6]
    units = []                                     # ("b", blok, None) | ("u", blok uwag, nr pozycji)
    for b in kolejne:
        units += [("b", b, None)] if b.uwagi is None else [("u", b, i) for i in range(len(b.uwagi.lines))]
    m, S = len(units), len(sloty)
    if not S:
        return

    def grupy(c0, c1):                             # [(blok, i0, i1)] — uwagi jako jedna część w slocie
        out, i = [], c0
        while i < c1:
            kind, b, idx = units[i]
            if kind == "b":
                out.append((b, None, None))
                i += 1
                continue
            k = i
            while k < c1 and units[k][1] is b:
                k += 1
            out.append((b, idx, units[k - 1][2] + 1))
            i = k
        return out

    def koszt_slotu(j, c0, c1):
        if c0 == c1:
            return 0.0
        x0, x1, a, bb = sloty[j]
        h, kara = -GAP_B, 0.0
        for b, i0, i1 in grupy(c0, c1):
            if i0 is None:
                if b.szer > x1 - x0 + 1e-6:
                    return None
                h += b.wys + GAP_B
                continue
            n = len(b.uwagi.lines)
            if i1 - i0 < 2 and n >= 2 and not (i0 == 0 and i1 == n):
                return None                        # część z jedną pozycją
            h += b.uwagi.wysokosc(i0, i1) + GAP_B
            kara += 0.3 if i0 > 0 else 0.0         # część „(cd.)”
        return None if h > bb - a + 1e-6 else h / max(1e-6, bb - a) + kara
    INF = float("inf")
    dp = [[INF] * (m + 1) for _ in range(S + 1)]
    arg = [[0] * (m + 1) for _ in range(S + 1)]
    dp[0][0] = 0.0
    for j in range(1, S + 1):
        for c in range(m + 1):
            for c0 in range(c + 1):
                if dp[j - 1][c0] == INF:
                    continue
                k = koszt_slotu(j - 1, c0, c)
                if k is not None and max(dp[j - 1][c0], k) < dp[j][c] - 1e-12:
                    dp[j][c], arg[j][c] = max(dp[j - 1][c0], k), c0
    if dp[S][m] == INF:
        return
    podzial, c = [], m
    for j in range(S, 0, -1):
        podzial.append((j - 1, arg[j][c], c))
        c = arg[j][c]
    wl = baza.kopia()
    nowe, czesci = [], 0
    for j, c0, c1 in reversed(podzial):
        x0, x1, a, top = sloty[j]
        for b, i0, i1 in grupy(c0, c1):
            if i0 is not None:
                b = Blok(f"{b.nazwa}[{i0 + 1}–{i1}]", b.uwagi.fn(i0, i1), b.uwagi.w, b.uwagi.wysokosc(i0, i1))
                czesci += 1
            r = (x1 - b.szer, top - b.wys, x1, top)
            if not wl.miesci(r):
                return
            wl.zajmij(_napompuj(r, GAP_C, GAP_B, GAP_C, GAP_B))
            nowe.append((b, r[0], r[1]))
            top = r[1] - GAP_B
    if czesci > R.czesci_uwag:
        return
    R.bloki = R.bloki[:n_b]
    R.prostokaty = R.prostokaty[:n_p]
    for b, x0, y0 in nowe:
        R.bloki.append((b, x0 + b.dx0, y0 + b.h, b.w))
        R.prostokaty.append(("blok", b.nazwa, (x0, y0, x0 + b.szer, y0 + b.wys)))
    if any(b.uwagi is not None for b in kolejne):
        R.czesci_uwag = czesci


# ================================================================================================ dobór formatu
def min_szerokosc(H: float, widoki, grupy, bloki, tb_h: float, o: dict):
    """Najmniejsza szerokość arkusza o wysokości H mieszcząca treść: (W, grupa, rozmieszczenie) lub None."""
    Wmax = float(o["max_dlugosc"])
    gap = float(o.get("odstep_widok_blok", GAP_VB))
    mc = int(o.get("max_czesci_uwag", 4))
    ko = str(o.get("kolejnosc_uwag", "czytania"))
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
        while W <= Wmax + 1e-6:            # wykonalność: bez rezerwacji stref znaków (najluźniejszy wariant)
            r = pakuj(W, H, widoki, g, bloki, tb_h, gap_vb=gap, znaki=False, max_czesci=mc, kolejnosc=ko)
            if r.ok:
                break
            prev, W = W, W + step
        if r is None or not r.ok:
            continue
        if prev is not None:
            Wf = prev + 5.0
            while Wf < W - 1e-6:
                rf = pakuj(Wf, H, widoki, g, bloki, tb_h, gap_vb=gap, znaki=False, max_czesci=mc, kolejnosc=ko)
                if rf.ok:
                    W, r = Wf, rf
                    break
                Wf += 5.0
        if best is None or W < best[0] - 1e-6:
            best = (W, g, r)
    return best


def _pakuj_wysrodkuj(W, H, widoki, g, bloki, tb_h, W_need, gap_vb: float = GAP_VB, o: dict | None = None):
    """Pakowanie na W × H z grupą widoków wyśrodkowaną w nadwyżce szerokości / wysokości — przyjmowane tylko, gdy
    nie pogarsza upakowania względem układu bez przesunięcia (``_jakosc``: części uwag, kolumny bloków, liczba
    bloków, rezerwacja znaków); inaczej układ bez przesunięcia. None — nic się nie mieści."""
    o = o or DOMYSLNE
    kw = dict(znaki=o.get("znaki_centrujace", "auto"), max_czesci=int(o.get("max_czesci_uwag", 4)),
              kolejnosc=str(o.get("kolejnosc_uwag", "czytania")))
    extra = max(0.0, W - W_need)
    slack = max(0.0, (H - 2 * MARG) - PAD_V - PAD_B - g.h)
    r0 = pakuj(W, H, widoki, g, bloki, tb_h, (0.0, 0.0), gap_vb, **kw)
    for p in ((extra / 2.0, slack / 2.0), (extra / 2.0, 0.0), (0.0, slack / 2.0)):
        if p[0] < 0.5 and p[1] < 0.5:
            continue
        r = pakuj(W, H, widoki, g, bloki, tb_h, p, gap_vb, **kw)
        if r.ok and (not r0.ok or _jakosc(r) <= _jakosc(r0)):
            return r
    return r0 if r0.ok else None


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
                    czesci_uwag=self.roz.czesci_uwag, znaki_rezerwowane=self.roz.znaki,
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
        if _k == "znak":
            continue
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
    kc = float(o.get("kara_czesci_uwag", 0.02))
    if tryb == "jawny":
        nm, W, H = jawny
        std = nazwa_standardowa(W, H)
        best = None
        for g in grupy:                            # warianty ułożenia widoków: najlepsze upakowanie (_jakosc)
            if not pakuj(W, H, widoki, g, bloki, tb_h, gap_vb=gap, znaki=False,
                         max_czesci=int(o["max_czesci_uwag"]), kolejnosc=str(o["kolejnosc_uwag"])).ok:
                continue
            need = _dociagnij(W, H, widoki, g, bloki, tb_h, gap)
            r = _pakuj_wysrodkuj(W, H, widoki, g, bloki, tb_h, need, gap, o)
            if r is not None and (best is None or _jakosc(r) < _jakosc(best)):
                best = r
        if best is None:
            return None
        k, oc = koszt(W, H, std is not None, o, tb_h)
        k *= 1.0 + kc * best.dodatkowe_czesci
        return Uklad(std[0] if std else nm, W, H, std[1] if std else None, std is not None, tryb, best, k, oc,
                     [], wypelnienie_ukladu(best))
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
        # koszt pełny = koszt papieru i składania × (1 + kara za każdą dodatkową część uwag) — znany po upakowaniu;
        # kandydaci w kolejności kosztu papieru, do pierwszego, którego sam koszt papieru nie jest już lepszy
        best_h = None
        for k, nm, L, ori, is_std, oc in opts[:12]:
            if best_h is not None and k >= best_h.koszt - 1e-9:
                break
            r = _pakuj_wysrodkuj(L, H, widoki, g, bloki, tb_h, W_need, gap, o)
            if r is None:
                continue
            kt = k * (1.0 + kc * r.dodatkowe_czesci)
            if best_h is None or kt < best_h.koszt - 1e-9:
                best_h = Uklad(nm, L, H, ori, is_std, tryb, r, kt, oc)
        if best_h is not None:
            cands.append(best_h)
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
    while Wn - 20.0 >= lo and pakuj(Wn - 20.0, H, widoki, g, bloki, tb_h, gap_vb=gap_vb, znaki=False).ok:
        Wn -= 20.0
    return Wn


def sprawdz_nakladanie(R: Rozmieszczenie, tol: float = 0.5) -> list[str]:
    """Kontrola rozmieszczenia: nakładanie się prostokątów (widoki z tytułami, bloki, tabliczka, strefy znaków
    centrujących) i wyjście poza ramkę. Strefa znaku jest sprawdzana z blokami (rezerwacja); z widokami, tytułami
    i tabliczką nie — tam znak skraca ``Sheet.przytnij_znaki_centrujace`` (kontrola na arkuszu:
    ``kolizje_znakow``)."""
    bledy = []
    fx0, fy0, fx1, fy1 = rama(R.W, R.H)
    P = R.prostokaty
    for i, (k1, n1, a) in enumerate(P):
        if a[0] < fx0 - tol or a[1] < fy0 - tol or a[2] > fx1 + tol or a[3] > fy1 + tol:
            bledy.append(f"{k1} „{n1}” poza ramką {tuple(round(v, 1) for v in a)}")
        for k2, n2, b in P[i + 1:]:
            if {k1, k2} <= {"widok", "tytul"} and n1 == n2:
                continue                           # pasy zajętości i tytuł jednego widoku
            if "znak" in (k1, k2) and (k2 if k1 == "znak" else k1) != "blok":
                continue
            if _przec(a, b, tol):
                bledy.append(f"{k1} „{n1}” nakłada się na {k2} „{n2}”")
    return bledy


def kolizje_znakow(sh, odstep: float = 0.2) -> list[str]:
    """Kontrola na narysowanym arkuszu: znaki centrujące (po przycięciu) nie dotykają treści (prymitywy arkusza
    i rzutni poza ramką i samymi znakami)."""
    from ..draft.sheet import ZNAK_CENTR_GR as GR, _obwiednie_w_pasach
    out = []
    zn = getattr(sh, "znaki", None) or {}
    pasy = {}
    for s_, p in zn.items():
        (xa, ya), (xb, yb) = p.pts[0], p.pts[-1]
        a = GR / 2.0 + odstep
        r = (min(xa, xb) - a, min(ya, yb) - a, max(xa, xb) + a, max(ya, yb) + a)
        x0, y0, x1, y1 = sh.frame                  # tylko część za ramką (w marginesie nic nie ma)
        r = (max(r[0], x0 + 0.5), max(r[1], y0 + 0.5), min(r[2], x1 - 0.5), min(r[3], y1 - 0.5))
        if r[2] > r[0] and r[3] > r[1]:
            pasy[s_] = r
    for B in _obwiednie_w_pasach(sh, pasy):
        for s_, r in pasy.items():
            m = (B[:, 0] < r[2]) & (B[:, 2] > r[0]) & (B[:, 1] < r[3]) & (B[:, 3] > r[1])
            if m.any():
                out.append(f"znak centrujący „{s_}” dotyka treści ({int(m.sum())} el.)")
    return sorted(set(out))


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
