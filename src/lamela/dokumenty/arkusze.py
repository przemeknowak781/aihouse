"""Arkusze części rysunkowej (PDF wektorowe z ``lamela.draft`` / ``lamela.views`` lub z innych programów).

``Arkusz.z_pdf(plik)`` odczytuje numer, tytuł, skalę i datę z tabliczki rysunkowej (metryki wg § 10 RPB,
układ ``lamela.draft.sheet.TitleBlock``): pola rozpoznaje po etykietach „NR RYSUNKU”, „TYTUŁ RYSUNKU”, „SKALA”,
„DATA WYDANIA”, „REW.”. Gdy tabliczki nie da się odczytać — z metadanych PDF (Title) i nazwy pliku
(``PZT-01_plan_1-500.pdf`` → nr ``PZT-01``, skala ``1:500``). Wartości podane jawnie mają pierwszeństwo.

Arkusz bez pliku (``plik=None``) to rysunek **planowany** — pojawia się w wykazie rysunków ze znacznikiem
``[DO UZUPEŁNIENIA]``, w tomie jako strona zastępcza, a walidator zgłasza go jako brak.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf

from .formaty import PT2MM, wykryj_format, rozmiar_formatu
from .znaczniki import do_uzup

MM = 72.0 / 25.4


@dataclass
class Arkusz:
    plik: str | Path | None = None
    nr: str | None = None
    tytul: str | None = None
    skala: str | None = None
    format: str | None = None
    data: str | None = None
    rewizja: str | None = None
    branza: str | None = None
    uwagi: str = ""
    strony: int = 0
    wymiary_mm: list = field(default_factory=list)
    zrodlo_danych: str = ""

    @classmethod
    def z_pdf(cls, plik, **jawne) -> "Arkusz":
        """Arkusz z pliku PDF — pola odczytane z tabliczki; argumenty ``jawne`` (nr, tytul, skala…) nadpisują."""
        p = Path(plik)
        a = cls(plik=p)
        doc = pymupdf.open(str(p))
        try:
            a.strony = doc.page_count
            a.wymiary_mm = [(round(pg.rect.width * PT2MM, 1), round(pg.rect.height * PT2MM, 1)) for pg in doc]
            w, h = a.wymiary_mm[0]
            a.format = wykryj_format(w, h)
            m = _metryka(doc[0])
            src = "tabliczka" if m else ""
            meta_t = (doc.metadata or {}).get("title") or ""
        finally:
            doc.close()
        a.nr = m.get("nr")
        a.tytul = m.get("tytul")
        a.skala = m.get("skala")
        a.data = m.get("data")
        a.rewizja = m.get("rew")
        stem = p.stem
        if not a.nr:
            mm = re.match(r"^([A-Z]{1,4}(?:-[A-Z]{1,4})*-\d{1,3}[A-Z]?)", stem)
            a.nr = mm.group(1) if mm else stem
            src = src or "nazwa pliku"
        if not a.tytul:
            a.tytul = meta_t or stem.replace("_", " ")
            src = src or "metadane PDF"
        if not a.skala:
            ms = re.search(r"(?<!\d)1[-_:](\d{1,4})(?!\d)", stem)
            a.skala = f"1:{ms.group(1)}" if ms else "—"
        a.zrodlo_danych = src
        for k, v in jawne.items():
            if not hasattr(a, k):
                raise TypeError(f"Arkusz nie ma pola {k!r}")
            setattr(a, k, v)
        return a

    @classmethod
    def planowany(cls, nr: str, tytul: str, skala: str = "—", format: str | None = None, **kw) -> "Arkusz":
        """Rysunek przewidziany w projekcie, którego plik jeszcze nie istnieje."""
        return cls(plik=None, nr=nr, tytul=tytul, skala=skala, format=format,
                   uwagi=kw.pop("uwagi", do_uzup("arkusz do wygenerowania z modelu")), **kw)

    @property
    def istnieje(self) -> bool:
        return self.plik is not None and Path(self.plik).exists()

    @property
    def etykieta(self) -> str:
        s = f"{self.nr} — {self.tytul}"
        return s + (f", {self.skala}" if self.skala and self.skala != "—" else "")

    def wymiar_tekst(self) -> str:
        if self.wymiary_mm:
            w, h = self.wymiary_mm[0]
            return f"{round(w)}×{round(h)}"
        if self.format:
            try:
                s, l = rozmiar_formatu(self.format)
                return f"{l}×{s}"
            except ValueError:
                pass
        return "—"


def _metryka(page: pymupdf.Page) -> dict:
    """Odczyt pól tabliczki (prawy dolny róg arkusza). Zwraca {} gdy nie rozpoznano etykiet."""
    r = page.rect
    clip = pymupdf.Rect(max(0, r.width - 200 * MM), max(0, r.height - 110 * MM), r.width, r.height)
    spans = []
    for b in page.get_text("dict", clip=clip).get("blocks", []):
        for ln in b.get("lines", []):
            for s in ln.get("spans", []):
                t = s["text"].strip()
                if t:
                    spans.append((pymupdf.Rect(s["bbox"]), s["size"], t))
    if not spans:
        return {}

    def etykieta(txt):
        for rect, size, t in spans:
            if t.upper() == txt:
                return rect, size
        return None

    def wartosc(lab, wiele=False, y_max=None):
        e = etykieta(lab)
        if not e:
            return None
        L, ls = e
        kand = [(rect, size, t) for rect, size, t in spans
                if size > ls + 0.5 and rect.y0 >= L.y0 - 1 and rect.y0 <= L.y1 + (60 if wiele else 14)
                and L.x0 - 3 <= rect.x0 <= L.x0 + (175 * MM if wiele else 45 * MM)
                and (y_max is None or rect.y1 <= y_max + 1)]
        if not kand:
            return None
        kand.sort(key=lambda k: (round(k[0].y0), k[0].x0))
        if not wiele:
            return kand[0][2]
        s0 = kand[0][1]
        return " ".join(t for rect, size, t in kand if abs(size - s0) < 0.3)

    wyn = {}
    sk = etykieta("SKALA")
    wyn["tytul"] = wartosc("TYTUŁ RYSUNKU", wiele=True, y_max=sk[0].y0 if sk else None)
    wyn["nr"] = wartosc("NR RYSUNKU")
    wyn["skala"] = wartosc("SKALA")
    wyn["data"] = wartosc("DATA WYDANIA")
    wyn["rew"] = wartosc("REW.")
    return {k: v for k, v in wyn.items() if v}


def arkusze_z_katalogu(katalog, wzorzec: str = "*.pdf", pomin=("tom",)) -> list[Arkusz]:
    """Wszystkie arkusze PDF z katalogu (sortowane po nazwie); pomija pliki zawierające w nazwie ``pomin``."""
    out = []
    for p in sorted(Path(katalog).glob(wzorzec)):
        if any(x.lower() in p.stem.lower() for x in pomin):
            continue
        out.append(Arkusz.z_pdf(p))
    return out


# ------------------------------------------------------------------------------------ składanie wersji papierowej
def plan_skladania(arkusze: list[Arkusz]) -> list[dict]:
    """Plan składania arkuszy do formatu A4 dla wersji papierowej (RPB § 2a — oprawa do A4).

    Wykorzystuje ``lamela.draft.sheet.fold_positions`` (sposób „do wpięcia”: tabliczka na wierzchu, lewy pas
    210 mm z marginesem 20 mm na oprawę, wg PN-N-01603 / DIN 824 A). Zwraca listę
    ``{nr, format, wymiary, zlozenia_pionowe, zlozenia_poziome, opis}``."""
    try:
        from lamela.draft.sheet import fold_positions
    except Exception:           # pragma: no cover — silnik rysunkowy niedostępny
        fold_positions = None
    out = []
    for a in arkusze:
        if not a.wymiary_mm and not a.format:
            continue
        if a.wymiary_mm:
            W, H = a.wymiary_mm[0]
        else:
            s, l = rozmiar_formatu(a.format)
            W, H = l, s
        if fold_positions is not None:
            xs, ys = fold_positions(W, H)
        else:
            xs, ys = [], []
        if not xs and not ys:
            opis = "bez składania (A4)"
        else:
            opis = (f"{len(xs)} zgięć pionowych (harmonijka, pas 210 mm z marginesem do oprawy), "
                    f"{len(ys)} zgięć poziomych; tabliczka na wierzchu")
        out.append({"nr": a.nr, "format": a.format, "wymiary": f"{round(W)}×{round(H)}",
                    "zlozenia_pionowe": [round(x, 1) for x in xs], "zlozenia_poziome": [round(y, 1) for y in ys],
                    "opis": opis})
    return out
