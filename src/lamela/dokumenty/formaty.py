"""Formatowanie liczb i dat (konwencja polska) oraz rozpoznawanie formatów arkuszy (PN-EN ISO 5457)."""
from __future__ import annotations

import datetime as _dt
import math
import re

NBSP = " "

MIESIACE = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września",
            "października", "listopada", "grudnia"]
MIESIACE_M = ["styczeń", "luty", "marzec", "kwiecień", "maj", "czerwiec", "lipiec", "sierpień", "wrzesień",
              "październik", "listopad", "grudzień"]


def liczba(x, miejsca: int | None = 2, *, tysiace: bool = True, znak: bool = False, pusty: str = "—") -> str:
    """Liczba w zapisie polskim: przecinek dziesiętny, twarda spacja jako separator tysięcy (``1 234,56``).
    ``miejsca=None`` — bez zaokrąglania (liczby całkowite bez części ułamkowej). ``znak`` — plus przed dodatnimi."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return pusty
    if isinstance(x, str):
        return x
    if isinstance(x, bool):
        return "tak" if x else "nie"
    if miejsca is None:
        miejsca = 0 if float(x).is_integer() else len(repr(float(x)).split(".")[1])
    s = f"{abs(float(x)):,.{miejsca}f}"
    s = s.replace(",", "\u0001").replace(".", ",").replace("\u0001", NBSP if tysiace else "")
    if float(x) < 0 and float(s.replace(",", ".").replace(NBSP, "")) != 0:
        s = "−" + s
    elif znak and float(x) > 0:
        s = "+" + s
    return s


def rzedna(x, miejsca: int = 3) -> str:
    """Rzędna w zapisie PN-B-01025 (±0,000 / +3,150 / −0,450)."""
    if abs(x) < 0.5 * 10 ** -miejsca:
        return "±" + liczba(0, miejsca)
    return liczba(x, miejsca, znak=True)


def data_iso(d=None) -> str:
    if d is None:
        d = _dt.date.today()
    if isinstance(d, str):
        return _parsuj_date(d).isoformat()
    return d.isoformat() if isinstance(d, _dt.date) else str(d)


def _parsuj_date(s: str) -> _dt.date:
    s = s.strip()
    for f in ("%Y-%m-%d", "%Y.%m.%d", "%d.%m.%Y", "%d-%m-%Y"):
        try:
            return _dt.datetime.strptime(s, f).date()
        except ValueError:
            pass
    raise ValueError(f"Nierozpoznany format daty: {s!r} (oczekiwano rrrr-mm-dd)")


def jako_date(d=None) -> _dt.date:
    if d is None:
        return _dt.date.today()
    if isinstance(d, _dt.datetime):
        return d.date()
    if isinstance(d, _dt.date):
        return d
    return _parsuj_date(str(d))


def data_slownie(d=None) -> str:
    """„25 września 2026 r.”"""
    d = jako_date(d)
    return f"{d.day} {MIESIACE[d.month - 1]} {d.year} r."


def data_miesiac(d=None) -> str:
    """„wrzesień 2026 r.”"""
    d = jako_date(d)
    return f"{MIESIACE_M[d.month - 1]} {d.year} r."


def data_pliku(d=None) -> str:
    """Data w nazwie pliku wg zał. 1 RPB: ``rrrr.mm.dd``."""
    return jako_date(d).strftime("%Y.%m.%d")


# ----------------------------------------------------------------------------------------------- formaty arkuszy
ISO_A = {"A0": (841, 1189), "A1": (594, 841), "A2": (420, 594), "A3": (297, 420), "A4": (210, 297)}
PT2MM = 25.4 / 72.0


def rozmiar_formatu(nazwa: str) -> tuple[float, float]:
    """(krótszy, dłuższy) bok [mm] formatu 'A0'…'A4' lub wydłużonego 'A3x3', 'A2×3' (Ak×n: krótszy bok =
    dłuższy bok Ak, dłuższy = n × krótszy bok Ak — PN-EN ISO 5457 tabl. 2–3)."""
    k = nazwa.upper().replace("×", "X").replace(" ", "")
    if k in ISO_A:
        return ISO_A[k]
    m = re.fullmatch(r"(A[0-4])X(\d+)", k)
    if not m:
        raise ValueError(f"Nieznany format {nazwa!r}")
    s, l = ISO_A[m.group(1)]
    return (l, s * int(m.group(2)))


def _kandydaci():
    out = dict(ISO_A)
    for base in ("A4", "A3", "A2", "A1", "A0"):
        for n in range(2, 10):
            out[f"{base}×{n}"] = rozmiar_formatu(f"{base}x{n}")
    return out


_KANDYDACI = _kandydaci()


def wykryj_format(szer_mm: float, wys_mm: float, tol: float = 2.5) -> str:
    """Nazwa formatu dla wymiarów strony [mm] (niezależnie od orientacji), np. 'A3', 'A3×3';
    format niestandardowy — ``'nst. 500×700'``."""
    a, b = sorted((szer_mm, wys_mm))
    for nazwa, (s, l) in _KANDYDACI.items():
        if abs(a - s) <= tol and abs(b - l) <= tol:
            return nazwa
    return f"nst. {round(szer_mm)}×{round(wys_mm)}"


def orientacja(szer_mm: float, wys_mm: float) -> str:
    return "pionowa" if wys_mm >= szer_mm else "pozioma"


def odmiana(n: int, jeden: str, kilka: str, wiele: str) -> str:
    """Forma rzeczownika po liczebniku: 1 strona, 2–4 strony, 5 stron (22 strony, 25 stron, 12 stron)."""
    n = abs(int(n))
    if n == 1:
        return jeden
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return kilka
    return wiele
