"""Geometria detali architektonicznych (PT) — klasa `Detal`: elementy przecięte z materiałami modelu, warstwy
przegród układane wprost z `model/budynek.yaml` (grubości, kolejność, kliny), warstwy cienkie (membrany, papy,
folie) jako linie „4 linii”, taśmy, obróbki blacharskie z kapinosami, opisy (odnośniki), wymiary, rzędne, spadki.

Układ lokalny detalu: metry, x w prawo (zwykle na zewnątrz), y w górę; `z0` — rzędna (wzgl. ±0,00) poziomu y = 0.
Każde użycie warstwy przegrody jest rejestrowane (`kontrola`) — porównanie grubości narysowanej z modelem
(raport modułu `lamela.views.detale`).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import Polygon, box

CIENKA = 0.006          # [m] warstwy cieńsze — linia (membrany, papy, folie, taśmy)
# funkcja materiału (pole `funkcja` modelu) → rodzaj linii „4 linii” / linii pomocniczej
FUNKCJA_LINII = {"hydroizolacja": "H", "przeciwwilgociowa": "H", "paroizolacja": "P", "wiatroizolacja": "W",
                 "bariera_korzenna": "G", "geowloknina": "G", "drenaz": "G"}

# materiały detali spoza modelu: kod → (nazwa, wzór kreskowania silnika, rodzaj elementu, λ [W/(m·K)] | None)
DET_MATS = {
    "RAMA_ALU": ("Rama stolarki — profil aluminiowy z przekładką termiczną", "STAL", "stal", None),
    "SZYBA3": ("Pakiet szybowy 3-szybowy (ciepła ramka)", "SZKLO", "warstwa", None),
    "PODWALINA": ("Podwalina progowa / profil nośny z XPS 300 lub PUR-GF, λ ≤ 0,05", "IZOL_XPS", "izol", 0.05),
    "LACZNIK": ("Łącznik termoizolacyjny płyty (moduł izolacyjny + pręty nierdzewne, ETA)", "IZOL_TWARDA", "izol", 0.08),
    "PARAPET_WEWN": ("Parapet wewnętrzny — konglomerat / MDF lakierowany 20 mm", "BRAK_OZN", "wyk", None),
    "PROFIL_XPS": ("Profil nośny parapetu zewn. z XPS (ciepły montaż)", "IZOL_XPS", "izol", 0.035),
    "PIANKA": ("Pianka PUR niskoprężna (wypełnienie szczeliny)", "IZOL_MIEKKA", "izol", 0.04),
    "GRUNT": ("Grunt rodzimy — piasek średni (MSa)", "GRUNT_RODZIMY", "grunt", None),
    "KRUSZYWO": ("Podbudowa z kruszywa łamanego 0/31,5 zagęszczona", "ZWIR", "warstwa", None),
    "PLYTA_BET": ("Płyta betonowa chodnikowa 60×60×5 cm na podsypce", "BETON", "warstwa", None),
    "DESKA_KOMP": ("Deska tarasowa kompozytowa 25 mm na legarach", "TWORZYWO", "warstwa", None),
    "LEGAR": ("Legar aluminiowy / kompozytowy na wspornikach regulowanych", "TWORZYWO", "warstwa", None),
    "KORYTKO": ("Odwodnienie liniowe — korytko z polimerobetonu z rusztem (klasa A15/B125)", "BETON", "warstwa", None),
    "RURA_PVC": ("Rura PVC-U kanalizacji deszczowej", "TWORZYWO", "warstwa", None),
    "WPUST": ("Wpust dachowy PP/PUR z kołnierzem i grzałką", "TWORZYWO", "warstwa", None),
    "KONSOLA": ("Konsola stalowa nierdzewna z przekładką termiczną", "STAL", "stal", None),
    "PRZEKLADKA": ("Przekładka termoizolacyjna PA / EPDM 10 mm", "TWORZYWO", "warstwa", 0.25),
    "RYGIEL": ("Rygiel aluminiowy rusztu lamel", "STAL", "stal", None),
    "CZOLO_WLOKNO": ("Blenda / podsufitka — płyta włóknocementowa 12 mm", "PLYTA_GK", "wyk", None),
    "RUSZT": ("Ruszt drewniany impregnowany / profil Al (szczelina wentylowana)", "DREWNO_POPRZ", "warstwa", None),
    "OSCIEZNICA": ("Cokół / oścież świetlika — ocieplona kaseta systemowa", "IZOL_PIR", "izol", 0.03),
    "SKLEJKA": ("Sklejka wodoodporna 18 mm", "SKLEJKA", "warstwa", None),
    "USZCZELNIACZ": ("Masa uszczelniająca / taśma butylowa", "TWORZYWO", "warstwa", None),
}


def skrot_nazwy(nazwa: str, maks: int = 40) -> str:
    """Krótka nazwa materiału do opisu warstwy (bez grubości i nawiasów, ≤ maks znaków)."""
    s = re.sub(r"\([^)]*\)", "", nazwa or "")
    s = re.sub(r"\b\d+([,.]\d+)?\s*(mm|cm|m)\b", "", s)
    s = s.split(",")[0].split(";")[0]
    s = re.sub(r"\s+", " ", s).strip(" —-:")
    if len(s) > maks:
        s = s[:maks].rsplit(" ", 1)[0] + "…"
    return s


def mm(d: float) -> str:
    v = d * 1000.0
    return (f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 0.05 else f"{round(v):d}").replace(".", ",")


@dataclass
class Czesc:
    poly: Polygon
    mat: str
    kind: str
    grupa: str | None = None
    os: tuple | None = None


@dataclass
class Opis:
    pts: list                 # punkty wskazywane (od strony wyjścia odnośnika do wnętrza)
    teksty: list              # wiersze opisu (kolejność = kolejność punktów)
    strona: str = "R"         # R | L — kolumna opisów
    tytul: str | None = None
    wyjscie: tuple | None = None   # punkt wyjścia linii odnośnika poza rysunek (domyślnie — poziomo do kolumny)


@dataclass
class Detal:
    model: object
    id: str
    tytul: str
    wezly: tuple = ()
    skala: int = 10
    z0: float = 0.0
    czesci: list = field(default_factory=list)
    cienkie: list = field(default_factory=list)     # (pts, mat, rodzaj, opis)
    linie: list = field(default_factory=list)       # (rodzaj H|S|P|T_in|T_out|W|G, pts, opis)
    obrobki: list = field(default_factory=list)     # (pts, opis)
    opisy: list = field(default_factory=list)
    wymiary: list = field(default_factory=list)     # (pts, at, kierunek, labels)
    rzedne: list = field(default_factory=list)      # (pt, z_rel, kind, strona, tekst)
    spadki: list = field(default_factory=list)      # (a, b, pct, tekst)
    przerwy: list = field(default_factory=list)     # (p1, p2)
    znaki: list = field(default_factory=list)       # (rodzaj, dane) — symbole dodatkowe (woda, strzałki)
    kontrola: list = field(default_factory=list)    # (kod, idx, mat, d_model, d_rys, klin)
    polaczenia: list = field(default_factory=list)  # (rodzaj, pts) — niewidoczne łączniki linii (np. przez ramę
    #                                                  okna w przerwie widoku) — tylko do oceny ciągłości
    uwagi: list = field(default_factory=list)
    okno: tuple | None = None

    # ------------------------------------------------------------------ materiały
    def mat_info(self, kod: str) -> tuple[str, float | None, str]:
        """(nazwa, λ, klasa) materiału modelu albo detalu."""
        if kod in DET_MATS:
            n, _h, k, lam = DET_MATS[kod]
            return n, lam, k
        m = self.model.material(kod)
        if m is None:
            return kod, None, "warstwa"
        try:
            kl = self.model._klasa_mat(kod)
        except Exception:      # pragma: no cover
            kl = "inna"
        return m.nazwa or kod, float(m.lambda_), kl

    def kind_of(self, kod: str, konstr: bool = False) -> str:
        if kod in DET_MATS:
            return DET_MATS[kod][2]
        _n, lam, kl = self.mat_info(kod)
        if konstr:
            return "konstr"
        if kl == "izolacja" or (lam is not None and lam <= 0.06):
            return "izol"
        if kl == "wykonczenie":
            return "wyk"
        if kl == "konstrukcja":
            return "konstr"
        return "warstwa"

    def funkcja(self, kod: str) -> str:
        m = self.model.material(kod)
        raw = getattr(m, "raw", None) or {}
        return str(raw.get("funkcja") or "")

    # ------------------------------------------------------------------ elementy
    def rect(self, x0, y0, x1, y1, mat, kind=None, grupa=None, os=None, konstr=False) -> Czesc | None:
        if abs(x1 - x0) < 1e-6 or abs(y1 - y0) < 1e-6:
            return None
        return self.poly(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), mat, kind, grupa, os, konstr)

    def poly(self, g, mat, kind=None, grupa=None, os=None, konstr=False) -> Czesc | None:
        g = g if isinstance(g, Polygon) else Polygon(g)
        if g.is_empty or g.area < 1e-9:
            return None
        c = Czesc(g, mat, kind or self.kind_of(mat, konstr), grupa, os)
        self.czesci.append(c)
        return c

    def warstwy(self, kod: str) -> list[dict]:
        """Warstwy przegrody modelu: [{mat, d, konstr, klin, funkcja, idx}] (kolejność modelu)."""
        p = self.model.przegroda(kod)
        if p is None:
            raise KeyError(f"brak przegrody {kod} w modelu")
        raw = (p.raw or {}).get("warstwy") or []
        out = []
        for i, w in enumerate(p.warstwy):
            r = raw[i] if i < len(raw) and isinstance(raw[i], dict) else {}
            out.append(dict(mat=w.mat, d=float(w.d), konstr=bool(w.konstrukcyjna), klin=r.get("klin"),
                            funkcja=str(r.get("funkcja") or self.funkcja(w.mat)), idx=i))
        return out

    def _rejestr(self, kod, w, d_rys):
        self.kontrola.append((kod, w["idx"], w["mat"], w["d"], d_rys, w.get("klin")))

    def stos_v(self, kod: str, x0: float, y0: float, y1: float, kier: int = +1, zakres: dict | None = None,
               od: int = 0, do: int | None = None, grupa: dict | None = None) -> list[tuple]:
        """Warstwy ściany `kod` (kolejność modelu — od wnętrza) od x0 w kierunku `kier` (+1 w prawo), wysokość
        y0…y1 (zakres {idx: (y0, y1)} — inna wysokość warstwy). Zwraca [(xa, xb, warstwa)] (xa < xb)."""
        ws = self.warstwy(kod)[od:do]
        out, x = [], x0
        for w in ws:
            d = w["d"]
            xa, xb = (x, x + d) if kier > 0 else (x - d, x)
            ya, yb = (zakres or {}).get(w["idx"], (y0, y1))
            if d < CIENKA:
                xm = (xa + xb) / 2
                self.cienka([(xm, ya), (xm, yb)], w["mat"], opis=None)
            else:
                self.rect(xa, ya, xb, yb, w["mat"], konstr=w["konstr"], grupa=(grupa or {}).get(w["idx"]),
                          os=((xa, ya), (xa, yb)))
            self._rejestr(kod, w, xb - xa)
            out.append((xa, xb, w))
            x = x + kier * d
        return out

    def stos_h(self, kod: str, x0: float, x1: float, y_top: float, zakres: dict | None = None,
               grub: dict | None = None, od: int = 0, do: int | None = None, grupa: dict | None = None,
               w_gore: bool = False) -> list[tuple]:
        """Warstwy przegrody poziomej `kod` (kolejność modelu — od góry) od y_top w dół (w_gore=True — od y_top
        w górę w odwrotnej kolejności), szerokość x0…x1 (zakres {idx: (x0, x1)}); grub {idx: d} — grubość lokalna
        warstwy klinowej. Zwraca [(y_gora, y_dol, warstwa)]."""
        ws = self.warstwy(kod)[od:do]
        if w_gore:
            ws = list(reversed(ws))
        out, y = [], y_top
        for w in ws:
            d = (grub or {}).get(w["idx"], w["d"])
            yg, yd = (y + d, y) if w_gore else (y, y - d)
            xa, xb = (zakres or {}).get(w["idx"], (x0, x1))
            if d < CIENKA:
                ym = (yg + yd) / 2
                self.cienka([(xa, ym), (xb, ym)], w["mat"])
            else:
                self.rect(xa, yd, xb, yg, w["mat"], konstr=w["konstr"], grupa=(grupa or {}).get(w["idx"]),
                          os=((xa, yd), (xb, yd)))
            self._rejestr(kod, w, d)
            out.append((yg, yd, w))
            y = yg if w_gore else yd
        return out

    # ------------------------------------------------------------------ linie
    def cienka(self, pts, mat: str, rodzaj: str | None = None, opis: str | None = None):
        r = rodzaj or FUNKCJA_LINII.get(self.funkcja(mat) if mat not in DET_MATS else "", "G")
        self.cienkie.append((np.asarray(pts, float), mat, r, opis))

    def linia(self, rodzaj: str, pts, opis: str | None = None):
        """Linia „4 linii” / taśma: H (hydro), S (szczelność powietrzna), P (paroizolacja), T_in (taśma
        paroszczelna), T_out (taśma paroprzepuszczalna / uszczelnienie zewn.), W (wiatroizolacja), G (inne)."""
        self.linie.append((rodzaj, np.asarray(pts, float), opis))

    def polaczenie(self, rodzaj: str, pts):
        """Łącznik ciągłości linii przez element szczelny (rama okna, profil) — nie rysowany."""
        self.polaczenia.append((rodzaj, np.asarray(pts, float)))

    def kontur(self, pts, zamkniety: bool = True, pen: float = 0.35, lt: str | None = None, opis: str | None = None):
        """Element w widoku / schematyczny (np. kaseta osłony, lamela za płaszczyzną cięcia)."""
        self.znak("kontur", pts=np.asarray(pts, float), zamkniety=zamkniety, pen=pen, lt=lt)

    def obrobka(self, pts, opis: str | None = None, kapinos: bool = True, strona: float | None = None):
        """Obróbka blacharska (blacha powlekana 0,7 mm) — łamana; `kapinos` — okapnik: odgięcie 45° na końcu
        (na zewnątrz: strona = +1 w prawo / −1 w lewo; domyślnie wg kierunku łamanej)."""
        P = np.asarray(pts, float)
        if kapinos and len(P) >= 2:
            sx = strona if strona is not None else (1.0 if P[-1][0] >= P[0][0] else -1.0)
            P = np.vstack([P, P[-1] + np.array([sx * 0.010, -0.010])])
        self.obrobki.append((P, opis))

    # ------------------------------------------------------------------ adnotacje
    def opis(self, pts, teksty, strona: str = "R", tytul: str | None = None, wyjscie=None):
        self.opisy.append(Opis([tuple(map(float, p)) for p in pts], list(teksty), strona, tytul,
                               tuple(map(float, wyjscie)) if wyjscie is not None else None))

    def tekst_warstwy(self, w: dict, d: float | None = None, klin: bool = False) -> str:
        n, _lam, _k = self.mat_info(w["mat"])
        dd = w["d"] if d is None else d
        if w.get("klin") and klin:
            kl = w["klin"]
            return f"{skrot_nazwy(n)} — spadkowa {mm(float(kl['d_min']))}…{mm(float(kl['d_max']))} mm"
        return f"{skrot_nazwy(n)} — {mm(dd)} mm"

    def opis_stosu(self, stos: list, pointer: str, poz: float, strona: str = "R", tytul: str | None = None,
                   odwroc: bool = False, wyjscie=None, pomin_cienkie: bool = False):
        """Opis warstw stosu (wynik stos_v / stos_h) jednym odnośnikiem: punkty na osi `pointer` ('x' — linia
        pionowa x = poz przez warstwy poziome; 'y' — linia pozioma y = poz przez warstwy pionowe). Teksty od
        pierwszej warstwy stosu (odwroc — od ostatniej)."""
        its = list(reversed(stos)) if odwroc else list(stos)
        pts, tx = [], []
        for a, b, w in its:
            if pomin_cienkie and abs(b - a) < CIENKA:
                continue
            c = (a + b) / 2
            pts.append((poz, c) if pointer == "x" else (c, poz))
            tx.append(self.tekst_warstwy(w, abs(b - a), klin=True))
        self.opis(pts, tx, strona, tytul, wyjscie)

    def wymiar(self, pts, at, kierunek: str = "h", labels=None):
        self.wymiary.append(([tuple(map(float, p)) for p in pts], at, kierunek, labels))

    def rzedna(self, pt, z_rel: float, kind: str = "wyk", strona: str = "right", tekst: str | None = None):
        self.rzedne.append((tuple(map(float, pt)), float(z_rel), kind, strona, tekst))

    def spadek(self, a, b, pct: float | None = None, tekst: str | None = None):
        self.spadki.append((tuple(map(float, a)), tuple(map(float, b)), pct, tekst))

    def przerwa(self, p1, p2):
        self.przerwy.append((tuple(map(float, p1)), tuple(map(float, p2))))

    def znak(self, rodzaj: str, **dane):
        self.znaki.append((rodzaj, dane))

    def zakres(self) -> tuple[float, float, float, float]:
        from shapely.ops import unary_union
        g = unary_union([c.poly for c in self.czesci])
        return g.bounds
