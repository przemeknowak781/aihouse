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
        return kontrola(f"K-{kod}-AKT", f"Aktualność rysunków {kod} względem modelu", pod, "BRAK",
                        f"rysunki z {fmt(t_rys)}, model zmieniony {fmt(t_mod)} ({', '.join(nowsze)}) — "
                        f"przed wydaniem wygenerować ponownie (tools/generuj_widoki.py)")
    return kontrola(f"K-{kod}-AKT", f"Aktualność rysunków {kod} względem modelu", pod, "OK",
                    f"rysunki z {fmt(t_rys)} — nowsze niż model/*.yaml")


# ------------------------------------------------------------------------------------------ plik tomu
def wektorowosc(pdf: Path, arkusze_tomu: list) -> tuple[dict, list[dict]]:
    """Analiza każdego arkusza rysunkowego w tomie: ścieżki wektorowe, tekst (znaki), udział rastra w polu strony."""
    doc = pymupdf.open(str(pdf))
    wiersze = []
    try:
        for a, s in arkusze_tomu:
            pg = doc[s - 1]
            pole = pg.rect.width * pg.rect.height
            rast = sum(abs(pymupdf.Rect(im["bbox"]).get_area()) for im in pg.get_image_info())
            n_sc = len(pg.get_cdrawings())
            n_zn = len(pg.get_text("text").strip())
            zast = getattr(a, "plik", None) is None
            udz = rast / pole if pole else 0.0
            ok = zast or (udz <= PROG_RASTRA and n_sc > 0)
            wiersze.append(dict(nr=str(a.nr), strona=s, format=a.format or "—", skala=a.skala or "—",
                                wymiary_mm=[round(pg.rect.width / 72 * 25.4), round(pg.rect.height / 72 * 25.4)],
                                sciezki=n_sc, znaki=n_zn, udzial_rastra=round(udz, 4), zastepczy=zast,
                                status="OK" if ok else "BRAK"))
    finally:
        doc.close()
    zle = [w["nr"] for w in wiersze if w["status"] != "OK"]
    zast = [w["nr"] for w in wiersze if w["zastepczy"]]
    pod = "RPB § 2b ust. 2; W-300"
    if zle:
        k = kontrola("K-WEKTOR", "Arkusze rysunkowe w postaci wektorowej", pod, "BRAK",
                     f"arkusze rastrowe lub bez ścieżek wektorowych: {', '.join(zle)}")
    else:
        n = len(wiersze) - len(zast)
        mx = max((w["udzial_rastra"] for w in wiersze), default=0.0)
        k = kontrola("K-WEKTOR", "Arkusze rysunkowe w postaci wektorowej", pod, "OK",
                     f"{n} arkuszy wektorowych (łącznie {sum(w['sciezki'] for w in wiersze)} ścieżek); "
                     f"największy udział rastra {mx * 100:.1f} % (próg {PROG_RASTRA * 100:.0f} %)"
                     + (f"; arkusze zastępcze: {', '.join(zast)}" if zast else ""))
    return k, wiersze


def metryki(pdf: Path, arkusze_tomu: list) -> dict:
    """Metryki arkuszy (RPB § 10 ust. 1 pkt 3): pola projektanta, sprawdzającego i opracowującego wypełnione —
    danymi albo znacznikiem ``[DO UZUPEŁNIENIA]`` / „nie dotyczy (art. 20 ust. 3 pkt 2 PB)”; pole puste = BRAK."""
    from lamela.dokumenty.dokument import metryka_arkusza
    pod = "RPB § 10 ust. 1 pkt 3; PB art. 20 ust. 3 pkt 2; W-305"
    doc = pymupdf.open(str(pdf))
    puste, uzup, bez = [], [], []
    try:
        for a, s in arkusze_tomu:
            if getattr(a, "plik", None) is None:
                continue
            pg = doc[s - 1]
            rows = metryka_arkusza(pg)
            if not rows:
                bez.append(str(a.nr))
                continue
            if any(r["pusty"] for r in rows):
                puste.append(str(a.nr))
            elif "DO UZUPEŁNIENIA" in pg.get_text():
                uzup.append(str(a.nr))
    finally:
        doc.close()
    if puste:
        return kontrola("K-METRYKA", "Metryki arkuszy — autorzy, uprawnienia, sprawdzający", pod, "BRAK",
                        f"puste pola metryki: {', '.join(puste)}")
    st = "DO UZUPEŁNIENIA" if uzup else "OK"
    return kontrola("K-METRYKA", "Metryki arkuszy — autorzy, uprawnienia, sprawdzający", pod, st,
                    (f"{len(uzup)} arkuszy z polami [DO UZUPEŁNIENIA] (imię i nazwisko, specjalność i nr uprawnień); "
                     "sprawdzający: nie dotyczy (art. 20 ust. 3 pkt 2 PB)" if uzup else "metryki wypełnione")
                    + (f"; bez rozpoznanej tabliczki: {', '.join(bez)}" if bez else ""))


def rozmiar(pdf: Path, limit_mb: float = 150.0) -> dict:
    mb = pdf.stat().st_size / 1048576
    return kontrola("K-ROZMIAR", f"Rozmiar pliku ≤ {limit_mb:.0f} MB", "RPB § 2b ust. 3; W-300; D-26",
                    "OK" if mb <= limit_mb else "BRAK", f"{mb:.2f} MB")


def metadane(pdf: Path) -> dict:
    doc = pymupdf.open(str(pdf))
    m = doc.metadata or {}
    toc = doc.get_toc()
    doc.close()
    brak = [k for k in ("title", "author", "subject", "keywords") if not m.get(k)]
    return kontrola("K-META", "Metadane PDF i zakładki", "dobra praktyka; AUD-RYS",
                    "OSTRZEŻENIE" if brak or not toc else "OK",
                    f"Title: „{m.get('title', '')}”; zakładek: {len(toc)}" + (f"; brak: {', '.join(brak)}" if brak else ""))


def spis_zalacznikow(pdf: Path, strony_frontu: int = 2) -> dict:
    """Łączny spis treści (strony za stroną tytułową tomu) obejmuje załączniki elementu ZL."""
    doc = pymupdf.open(str(pdf))
    toc = doc.get_toc()
    zl = [t for lvl, t, s in toc if "Załącznik nr" in t]
    konc = next((s for lvl, t, s in toc if t.startswith("PZT")), strony_frontu + 1)
    front = " ".join(doc[i].get_text() for i in range(0, max(1, konc - 1)))
    doc.close()
    w_spisie = [t for t in zl if t.split("—")[0].split(".")[0].strip() in front]
    st = "OK" if zl and len(w_spisie) == len(zl) else "BRAK"
    return kontrola("K-SPIS-ZL", "Łączny spis treści obejmuje spis załączników (ZL)", "RPB § 7 ust. 7 pkt 1, ust. 1a",
                    st, f"załączników w zakładkach: {len(zl)}, w łącznym spisie: {len(w_spisie)}")
