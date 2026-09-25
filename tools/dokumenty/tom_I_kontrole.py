"""Kontrole złożonego tomu I (PZT + PAB + ZL) uzupełniające walidator ``lamela.dokumenty.sprawdz_tom``.

* źródło rysunków PAB: ``projekt/03_PAB/rysunki`` (komplet AR) albo — gdy go brak — ``projekt/01_koncepcja/widoki``
  (informacja w raporcie; numeracja arkuszy wg ``model/arkusze.yaml`` jest ta sama: PB-AR-xx);
* zgodność arkuszy dołączonych do tomu z ``raport_widokow.json`` katalogów rysunków;
* wektorowość arkuszy (RPB § 2b ust. 2; W-300): liczba ścieżek wektorowych, znaków tekstu i udział rastra na stronie;
* rozmiar pliku (RPB § 2b ust. 3; limit 150 MB) i metadane;
* aktualność rysunków względem modelu (data modyfikacji ``model/*.yaml`` a ``raport_widokow.json``).

Każda kontrola zwraca słownik ``{id, opis, podstawa, status, szczegoly}`` ze statusem jak walidator
(OK · BRAK · OSTRZEŻENIE · N/D).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pymupdf

REPO = Path(__file__).resolve().parents[2]
KAT_PZT = REPO / "projekt/02_PZT/rysunki"
KAT_PAB = [REPO / "projekt/03_PAB/rysunki", REPO / "projekt/03_PAB/widoki", REPO / "projekt/03_PAB"]
KAT_PAB_ZAPAS = REPO / "projekt/01_koncepcja/widoki"
PLIKI_MODELU = ("budynek.yaml", "dzialka.yaml", "instalacje.yaml", "wyposazenie.yaml")
PROG_RASTRA = 0.35          # jak walidator (spec „wektor”): raster > 35 % pola arkusza = arkusz rastrowy


def kontrola(id_: str, opis: str, podstawa: str, status: str, szczegoly: str = "") -> dict:
    return dict(id=id_, opis=opis, podstawa=podstawa, status=status, szczegoly=szczegoly)


def _rel(p: Path | None) -> str:
    if p is None:
        return "—"
    try:
        return str(Path(p).resolve().relative_to(REPO))
    except ValueError:
        return str(p)


def wczytaj_raport(kat: Path) -> dict | None:
    p = kat / "raport_widokow.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ------------------------------------------------------------------------------------------ źródło rysunków PAB
def zrodlo_rysunkow_pab(D) -> tuple[Path | None, str]:
    """Ustala katalog rysunków PAB dla ``DanePAB``. Brak kompletu w ``projekt/03_PAB`` → arkusze koncepcji
    (``projekt/01_koncepcja/widoki``) zamiast arkuszy zastępczych; wpis w ``D.otwarte`` jest odpowiednio zmieniany."""
    if D.raport_rys is not None:
        return D.kat_rys, f"rysunki PAB z {_rel(D.kat_rys)} (raport_widokow.json)"
    rap = wczytaj_raport(KAT_PAB_ZAPAS)
    if rap is None:
        return None, ("brak raport_widokow.json w projekt/03_PAB/rysunki i projekt/01_koncepcja/widoki — "
                      "arkusze zastępcze wg model/arkusze.yaml")
    D.raport_rys, D.kat_rys = rap, KAT_PAB_ZAPAS
    D.otwarte = [x for x in D.otwarte if "nie jest jeszcze" not in x]
    msg = ("brak projekt/03_PAB/rysunki/raport_widokow.json — dołączono arkusze PB-AR z projekt/01_koncepcja/widoki "
           "(ten sam generator lamela.views i ta sama numeracja wg model/arkusze.yaml); przed wydaniem zastąpić "
           "kompletem z projekt/03_PAB/rysunki")
    D.otwarte.append("Rysunki PAB: " + msg + ".")
    return KAT_PAB_ZAPAS, msg


# ------------------------------------------------------------------------------------------ zgodność z raportami
def zgodnosc_z_raportem(kod: str, kat: Path | None, arkusze_tomu: list) -> dict:
    """Czy każdy arkusz z ``raport_widokow.json`` katalogu jest w tomie jako plik (nie arkusz zastępczy)."""
    pod = "RPB § 7 ust. 1 pkt 4, § 15–17 (PZT), § 21 (PAB); raport_widokow.json"
    rap = wczytaj_raport(kat) if kat else None
    if rap is None:
        return kontrola(f"K-{kod}-RAP", f"Arkusze {kod} zgodne z raport_widokow.json", pod, "OSTRZEŻENIE",
                        f"brak raport_widokow.json ({_rel(kat)})")
    w_tomie = {str(a.nr): a for a, _ in arkusze_tomu}
    brak, zast = [], []
    for a in rap.get("arkusze") or []:
        nr = str(a.get("nr"))
        if nr not in w_tomie:
            brak.append(nr)
        elif getattr(w_tomie[nr], "plik", None) is None:
            zast.append(nr)
    n = len(rap.get("arkusze") or [])
    if brak or zast:
        sz = "; ".join(x for x in [f"nie dołączono: {', '.join(brak)}" if brak else "",
                                   f"tylko arkusze zastępcze: {', '.join(zast)}" if zast else ""] if x)
        return kontrola(f"K-{kod}-RAP", f"Arkusze {kod} zgodne z raport_widokow.json", pod, "BRAK", sz)
    prob = [str(p) for p in rap.get("problemy") or []]
    sz = f"{n} z {n} arkuszy z {_rel(kat)}"
    if prob:
        sz += f"; generator zgłasza {len(prob)} brak(i) danych modelu (poniżej, pkt „Sprawy otwarte”)"
    return kontrola(f"K-{kod}-RAP", f"Arkusze {kod} zgodne z raport_widokow.json", pod, "OK", sz)


def problemy_generatora(kat: Path | None) -> list[str]:
    rap = wczytaj_raport(kat) if kat else None
    return [str(p) for p in (rap or {}).get("problemy") or []]


def aktualnosc(kod: str, kat: Path | None) -> dict:
    """Rysunki wygenerowane po ostatniej zmianie modelu? (data modyfikacji plików)."""
    pod = "spójność części opisowej i rysunkowej (model jedynym źródłem danych)"
    p = (kat / "raport_widokow.json") if kat else None
    if p is None or not p.exists():
        return kontrola(f"K-{kod}-AKT", f"Aktualność rysunków {kod} względem modelu", pod, "OSTRZEŻENIE",
                        "brak raportu generatora widoków")
    t_rys = p.stat().st_mtime
    mod = [(f, (REPO / "model" / f).stat().st_mtime) for f in PLIKI_MODELU if (REPO / "model" / f).exists()]
    nowsze = [f for f, t in mod if t > t_rys + 1]
    fmt = lambda t: dt.datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")  # noqa: E731
    if nowsze:
        t_mod = max(t for _, t in mod)
        return kontrola(f"K-{kod}-AKT", f"Aktualność rysunków {kod} względem modelu", pod, "OSTRZEŻENIE",
                        f"rysunki z {fmt(t_rys)}, model zmieniony {fmt(t_mod)} ({', '.join(nowsze)}) — "
                        f"przed wydaniem wygenerować ponownie (tools/generuj_widoki.py)")
    return kontrola(f"K-{kod}-AKT", f"Aktualność rysunków {kod} względem modelu", pod, "OK",
                    f"rysunki z {fmt(t_rys)} — nowsze niż model/*.yaml")
