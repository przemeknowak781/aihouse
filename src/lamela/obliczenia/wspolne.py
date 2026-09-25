"""Wspólne narzędzia biblioteki obliczeń (fizyka budowli, energia) — „Dom LAMELA”.

* formatowanie liczb w konwencji polskiej (przecinek dziesiętny), zaokrąglanie do cyfr znaczących
  (PN-EN ISO 6946:2017 p. 6.? — U podaje się z dokładnością do 2 cyfr znaczących, R do 2 miejsc po przecinku);
* generator tabel Markdown (`tabela_md`);
* znaczniki statusu danych zgodne z rejestrem wymagań (`docs/10_podstawy_prawne/00_rejestr_wymagan.md`, sekcja E):
  [NZW] niezweryfikowane, [INT] interpretacja, [ZAŁ] założenie, [PROG] program, [DANE PRZYKŁADOWE – FIKCYJNE];
* dostęp do wartości wymagań z `docs/10_podstawy_prawne/wymagania.yaml` (`wym`, `wymaganie`);
* rejestr założeń i źródeł (`Zalozenia`) dołączany do raportów.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml

ROOT = Path(__file__).resolve().parents[3]          # katalog repozytorium
DANE = Path(__file__).resolve().parent / "dane"
WYMAGANIA_YAML = ROOT / "docs" / "10_podstawy_prawne" / "wymagania.yaml"

# znaczniki (rejestr wymagań, sekcja E.1 / „Oznaczenia statusu”)
NZW = "[NZW]"
INT = "[INT]"
ZAL = "[ZAŁ]"
PROG = "[PROG]"
PRZYKL = "[DANE PRZYKŁADOWE – FIKCYJNE]"
DO_UZUP = "[DO UZUPEŁNIENIA]"

RHO_C_POWIETRZA = 1200.0     # J/(m³·K) — metodologia wzór (57); PN-EN 12831-1: ρ·c_p = 0,34 Wh/(m³·K)
RHO_C_WH = RHO_C_POWIETRZA / 3600.0


# --------------------------------------------------------------------------------------------------
# Liczby
# --------------------------------------------------------------------------------------------------
def zaokr_znaczace(x: float | None, n: int = 2) -> float | None:
    """Zaokrąglenie do n cyfr znaczących (U wg PN-EN ISO 6946:2017 — 2 cyfry znaczące)."""
    if x is None or x == 0 or not math.isfinite(x):
        return x
    return round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))


def fmt(x: Any, n: int = 2, *, znak: bool = False, pusty: str = "—") -> str:
    """Liczba z przecinkiem dziesiętnym i separatorem tysięcy (spacja niełamliwa wąska)."""
    if x is None:
        return pusty
    if isinstance(x, bool):
        return "tak" if x else "nie"
    if isinstance(x, str):
        return x
    try:
        v = float(x)
    except (TypeError, ValueError):
        return str(x)
    if not math.isfinite(v):
        return pusty
    s = f"{v:+,.{n}f}" if znak else f"{v:,.{n}f}"
    s = s.replace(",", "\u202f").replace(".", ",")
    if s.startswith("-") or s.startswith("+"):
        pass
    return s.replace("-", "−")


def fmt_u(u: float | None) -> str:
    """U [W/(m²·K)] — 2 cyfry znaczące (PN-EN ISO 6946:2017)."""
    if u is None:
        return "—"
    z = zaokr_znaczace(u, 2)
    n = max(0, -int(math.floor(math.log10(abs(z)))) + 1) if z else 2
    return fmt(z, n)


def fmt_r(r: float | None) -> str:
    """R [m²·K/W] — 2 miejsca po przecinku (PN-EN ISO 6946:2017)."""
    return fmt(r, 2)


def ok(b: bool | None) -> str:
    if b is None:
        return "—"
    return "✔ spełnia" if b else "✘ NIE spełnia"


# --------------------------------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------------------------------
def tabela_md(naglowki: Sequence[str], wiersze: Iterable[Sequence[Any]], wyrownanie: str | None = None,
              n: int = 2) -> str:
    """Tabela Markdown. `wyrownanie` — łańcuch znaków 'l'/'r'/'c' dla kolumn (domyślnie: tekst l, liczby r).
    Wartości float formatowane `fmt(x, n)`; str wstawiane bez zmian."""
    wiersze = [list(w) for w in wiersze]
    k = len(naglowki)
    if wyrownanie is None:
        wyr = []
        for j in range(k):
            num = any(isinstance(w[j], (int, float)) and not isinstance(w[j], bool) for w in wiersze if j < len(w))
            wyr.append("r" if num else "l")
    else:
        wyr = list(wyrownanie)
    sep = {"l": ":---", "r": "---:", "c": ":---:"}
    out = ["| " + " | ".join(str(h) for h in naglowki) + " |",
           "|" + "|".join(sep.get(a, "---") for a in wyr) + "|"]
    for w in wiersze:
        cells = []
        for j in range(k):
            v = w[j] if j < len(w) else ""
            if isinstance(v, float):
                cells.append(fmt(v, n))
            elif isinstance(v, bool):
                cells.append("tak" if v else "nie")
            elif v is None:
                cells.append("—")
            else:
                cells.append(str(v).replace("|", "\\|").replace("\n", " "))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def naglowek_raportu(tytul: str, podstawa: str, uwagi: Sequence[str] = ()) -> str:
    """Nagłówek sekcji obliczeń do części opisowej PAB/PT."""
    s = [f"## {tytul}", "", f"**Podstawa:** {podstawa}", ""]
    for u in uwagi:
        s.append(f"> {u}")
    if uwagi:
        s.append("")
    return "\n".join(s)


# --------------------------------------------------------------------------------------------------
# Wymagania (docs/10_podstawy_prawne/wymagania.yaml)
# --------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _wymagania_raw() -> dict:
    if WYMAGANIA_YAML.exists():
        return yaml.safe_load(WYMAGANIA_YAML.read_text(encoding="utf-8")) or {}
    return {}


@dataclass
class Wymaganie:
    klucz: str
    wartosc: Any
    jedn: str = ""
    typ: str = ""
    id: str | None = None
    status: str = ""
    zrodlo: str = ""

    @property
    def znacznik(self) -> str:
        return {"niezweryfikowane": NZW, "interpretacja": INT, "zalozenie": ZAL, "program": PROG}.get(self.status, "")

    def opis(self) -> str:
        z = f" {self.znacznik}" if self.znacznik else ""
        return f"{self.zrodlo} ({self.id}){z}" if self.id else f"{self.zrodlo}{z}"


def wymaganie(sekcja: str, klucz: str, domyslna: Any = None) -> Wymaganie:
    """Wpis z wymagania.yaml; gdy brak pliku/klucza — wartość domyślna ze statusem 'zalozenie'."""
    d = _wymagania_raw().get(sekcja, {}).get(klucz)
    if isinstance(d, dict):
        return Wymaganie(klucz, d.get("wartosc"), d.get("jedn", ""), d.get("typ", ""), d.get("id"),
                         d.get("status", ""), d.get("zrodlo", ""))
    return Wymaganie(klucz, domyslna, status="zalozenie", zrodlo="wartość domyślna biblioteki (brak w wymagania.yaml)")


def wym(sekcja: str, klucz: str, domyslna: Any = None) -> Any:
    return wymaganie(sekcja, klucz, domyslna).wartosc


# --------------------------------------------------------------------------------------------------
# Rejestr założeń i źródeł
# --------------------------------------------------------------------------------------------------
@dataclass
class Zalozenie:
    tresc: str
    status: str = ZAL          # NZW / INT / ZAL / PRZYKL / "" (zweryfikowane)
    zrodlo: str = ""

    def md(self) -> str:
        z = f" — źródło: {self.zrodlo}" if self.zrodlo else ""
        st = f" {self.status}" if self.status else ""
        return f"* {self.tresc}{st}{z}"


@dataclass
class Zalozenia:
    lista: list[Zalozenie] = field(default_factory=list)

    def dodaj(self, tresc: str, status: str = ZAL, zrodlo: str = "") -> None:
        if not any(z.tresc == tresc for z in self.lista):
            self.lista.append(Zalozenie(tresc, status, zrodlo))

    def md(self, tytul: str = "Założenia i dane wejściowe") -> str:
        if not self.lista:
            return ""
        return "\n".join([f"**{tytul}:**", ""] + [z.md() for z in self.lista]) + "\n"


# --------------------------------------------------------------------------------------------------
# Dane przykładowe wyrobów (karty katalogowe — dane przykładowe, bez nazw handlowych)
# --------------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def wyroby_przykladowe() -> dict:
    p = DANE / "wyroby_przykladowe.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


def wyrob(grupa: str, klucz: str | None = None) -> dict:
    g = wyroby_przykladowe().get(grupa, {})
    if klucz is None:
        return g
    return g.get(klucz, {})


def odczytaj_yaml(p) -> Any:
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------------
# Kierunki
# --------------------------------------------------------------------------------------------------
ORIENTACJE = ("N", "NE", "E", "SE", "S", "SW", "W", "NW")


def orientacja(azymut: float | None) -> str:
    """Azymut [°] (od N, zgodnie z ruchem wskazówek) → oznaczenie 8-kierunkowe."""
    if azymut is None:
        return "poziom"
    i = int(((azymut % 360) + 22.5) // 45) % 8
    return ORIENTACJE[i]


def miesiace_pl() -> list[str]:
    return ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"]


GODZINY_MIES = [744, 672, 744, 720, 744, 720, 744, 744, 720, 744, 720, 744]
DNI_MIES = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
