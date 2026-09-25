"""Generator tomu PT-1 AR — projekt techniczny, architektura („Dom LAMELA”).

Uruchomienie::

    PYTHONPATH=src python3 tools/dokumenty/tom_PT_AR.py [--wyjscie projekt/wydanie] [--bez-arkuszy]

Wynik:
* ``projekt/wydanie/PT_1_AR_rrrr.mm.dd.pdf`` — tom PT-1 AR (osobny plik, RPB § 5 ust. 3; nazwa wg zał. 1 RPB):
  strona tytułowa (§ 7 ust. 2, „Tom 1 z 4” — § 7 ust. 6), spis treści, oświadczenie projektanta PT
  (PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2), część opisowa (§ 23 pkt 4, 4a, 10 RPB),
  obliczenia (U — PN-EN ISO 6946, ψ/f_Rsi — PN-EN ISO 10211 i 13788, kondensacja — PN-EN ISO 13788, g — WT zał. 2),
  zestawienia (przegrody, stolarka — W-317, wykończenia), zasada „4 linii” i odwodnienie, część rysunkowa
  (§ 24 pkt 1–2: rzuty, przekroje, elewacje AR + detale PT-AR-D);
* ``projekt/09_opis_i_zalaczniki/PT_AR/`` — źródło Markdown części opisowej i raport walidatora (txt/json).

ŹRÓDŁA LICZB (odczyt przy każdym uruchomieniu — brak wartości wpisanych na sztywno):
``model/budynek.yaml`` + ``model/dzialka.yaml`` (lamela.model), ``lamela.obliczenia.fizyka_energia.oblicz_wszystko``
(U, grunt, okna, g, f_Rsi, Glaser, H_TB), ``projekt/08_obliczenia/mostki/zestawienie_mostkow.json`` (karty mostków
PN-EN ISO 10211: ψ, f_Rsi, „4 linie”), ``docs/10_podstawy_prawne/wymagania.yaml`` (wymagania z podstawą),
``lamela.wskazniki`` (kondygnacje, wysokość wg WT § 6), ``raport_widokow.json`` katalogów rysunków,
``projekt/10_PT_architektura/detale/raport_detali.md`` (przypisanie detali do węzłów).
Dane osobowe, uprawnienia, podpisy — ``[DO UZUPEŁNIENIA]``; działka/MPZP/grunt — ``[DANE PRZYKŁADOWE – FIKCYJNE]``.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
import time
from collections import OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from lamela.dokumenty import (Arkusz, Dokument, Tom, dane_obiektu, sprawdz_tom, LISTY_KONTROLNE,  # noqa: E402
                              liczba, do_uzup, DANE_PRZYKLADOWE, ZAL, NZW, zamknij_przegladarke)
from lamela.obliczenia.wspolne import wymaganie, orientacja  # noqa: E402

KAT_MOSTKI = REPO / "projekt/08_obliczenia/mostki"
KAT_DETALE = REPO / "projekt/10_PT_architektura/detale"
KAT_AR = [REPO / "projekt/03_PAB/rysunki", REPO / "projekt/01_koncepcja/widoki"]   # pierwszy istniejący
KAT_ZRODLA = REPO / "projekt/09_opis_i_zalaczniki/PT_AR"
KAT_WYDANIE = REPO / "projekt/wydanie"
PT_TOMY = 4                                  # PT-1 AR, PT-2 BO, PT-3 IS, PT-4 IE (rejestr C.2)
ROLE_WEWN = ("sciana_wewn", "strop_wewn")


# ============================================================================================ pomocnicze
def L(v, n=2, pusty="—"):
    """Liczba w zapisie polskim albo „—”."""
    return pusty if v is None else liczba(v, n)


def nr_iso(pid: str, kond: str) -> str:
    """Identyfikator modelu „0.01” → numer na arkuszach wg PN-B-01025 (parter = 1): „1.01” (W-314)."""
    try:
        return f"{int(kond[1:]) + 1}.{pid.split('.')[1]}"
    except Exception:
        return pid


def wym(sekcja: str, klucz: str):
    """Wymaganie z docs/10_podstawy_prawne/wymagania.yaml → (wartość, 'źródło; W-xxx')."""
    w = wymaganie(sekcja, klucz)
    return w.wartosc, f"{w.zrodlo}; {w.id}" if w.id else w.zrodlo


def _md_komorka(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, bool):
        return "tak" if v else "nie"
    if isinstance(v, float):
        return liczba(v, 3)
    return re.sub(r"<[^>]+>", "", str(v)).replace("|", "/").replace("\n", " ")


class Opis:
    """Zapis równoległy: bloki ``Dokument`` (PDF) i źródło Markdown (``projekt/09_opis_i_zalaczniki/PT_AR``)."""

    def __init__(self, dok: Dokument):
        self.dok = dok
        self.md: list[str] = []
        self.n_tab = 0

    def czesc(self, tytul: str, podstawa: str | None = None):
        self.dok.czesc_opisowa(tytul, podstawa=podstawa)
        self.md.append(f"# {tytul}" + (f" ({podstawa})" if podstawa else ""))

    def rozdzial(self, tytul: str, tresc: str | None = None, *, poziom: int = 1, podstawa: str | None = None,
                 nowa_strona: bool = False):
        tresc = textwrap.dedent(tresc).strip() if tresc else None
        self.dok.rozdzial(tytul, tresc, poziom=poziom, podstawa=podstawa, nowa_strona=nowa_strona)
        self.md.append(f"{'#' * (poziom + 1)} {tytul}" + (f" — {podstawa}" if podstawa else ""))
        if tresc:
            self.md.append(tresc)

    def tekst(self, tresc: str):
        tresc = textwrap.dedent(tresc).strip()
        self.dok.markdown(tresc)
        self.md.append(tresc)

    def wniosek(self, tresc: str, alarm: bool = False):
        self.dok.wniosek(textwrap.dedent(tresc).strip(), alarm=alarm)
        self.md.append("> " + textwrap.dedent(tresc).strip().replace("\n", "\n> "))

    def tabela(self, wiersze: list, *, tytul: str, uwagi=None, zrodlo: str | None = None, **kw):
        self.dok.tabela(wiersze, tytul=tytul, uwagi=uwagi, zrodlo=zrodlo, **kw)
        self.n_tab += 1
        kol = [k for k in (next((w for w in wiersze if isinstance(w, dict)), {}) or {}) if not k.startswith("_")]
        out = [f"**Tabela {self.n_tab}. {tytul}**", "", "| " + " | ".join(kol) + " |",
               "|" + "---|" * len(kol)]
        for w in wiersze:
            if isinstance(w, str):
                out.append(f"| **{w}** |" + " |" * (len(kol) - 1))
            else:
                out.append("| " + " | ".join(_md_komorka(w.get(k)) for k in kol) + " |")
        for u in ([uwagi] if isinstance(uwagi, str) else (uwagi or [])):
            out.append(f"\n{_md_komorka(u)}")
        if zrodlo:
            out.append(f"\n*Źródło: {zrodlo}*")
        self.md.append("\n".join(out))

    def zapisz(self, plik: Path):
        plik.parent.mkdir(parents=True, exist_ok=True)
        plik.write_text("\n\n".join(self.md) + "\n", encoding="utf-8")


# ============================================================================================ dane wejściowe
def wczytaj_dane() -> dict:
    """Model + komplet obliczeń fizyki budowli + karty mostków + wskaźniki (odczyt przy każdym uruchomieniu)."""
    from lamela.model import load_model
    from lamela.obliczenia.fizyka_energia import oblicz_wszystko
    from lamela.wskazniki import wskazniki
    m = load_model(REPO / "model/budynek.yaml", REPO / "model/dzialka.yaml", strict=False)
    if m.bledy:
        raise SystemExit("Model z błędami walidacji:\n" + m.raport_walidacji())
    R = oblicz_wszystko(m)                    # ψ węzłów: sekcja `wezly` modelu (runda poprawek — wartości projektowe)
    wsk = wskazniki(m)
    mostki = json.loads((KAT_MOSTKI / "zestawienie_mostkow.json").read_text(encoding="utf-8"))
    return dict(m=m, R=R, ob=R["obudowa"], wsk=wsk, mostki=mostki, detale=mapa_detali())


def mapa_detali() -> OrderedDict:
    """D-xx → {arkusz, tytul, skala, wezly}: arkusze z ``raport_widokow.json`` katalogu detali, rodzaj widoku
    z ``model/arkusze_detale.yaml``, węzły obsługiwane przez budowniczego detalu (``lamela.views.detale_katalog``)."""
    import yaml
    from lamela.views.detale_katalog import WEZEL_RODZAJ
    rap = json.loads((KAT_DETALE / "raport_widokow.json").read_text(encoding="utf-8"))
    cfg = yaml.safe_load((REPO / "model/arkusze_detale.yaml").read_text(encoding="utf-8"))
    rodz_ark = {a["nr"]: [w.get("rodzaj") for w in a.get("widoki", [])] for a in cfg.get("arkusze", [])}
    wez_rodz: dict[str, list[str]] = {}
    for w, r in WEZEL_RODZAJ.items():
        wez_rodz.setdefault(r, []).append(w)
    out: OrderedDict = OrderedDict()
    for a in rap.get("arkusze", []):
        rodz = rodz_ark.get(a["nr"], [])
        for k, w in enumerate(a.get("widoki", [])):
            mm = re.match(r"DETAL\s+(D-\d+\w?)\s+—\s+(.+)", w)
            if not mm:
                continue
            r = rodz[k] if k < len(rodz) else None
            out[mm.group(1)] = dict(arkusz=a["nr"], tytul=mm.group(2), skala=a.get("skala"), rodzaj=r,
                                    wezly=sorted(x for x in wez_rodz.get(r, []) if x.startswith("WZ")))
    return out


def detale_wezla(detale: dict, wid: str) -> str:
    """Odsyłacz do detali dla węzła (np. WZ-09a → „D-11 (PT-AR-D-05)”); dopasowanie także po węźle nadrzędnym."""
    baza = re.sub(r"[a-zNPT]$", "", wid) if re.match(r"WZ-\d+[a-zNPT]$", wid) else wid
    tr = [f"{d} ({v['arkusz']})" for d, v in detale.items() if wid in v["wezly"] or baza in v["wezly"]]
    return ", ".join(tr) if tr else "—"


def arkusze_branzy() -> tuple[list[Arkusz], list[str], Path | None]:
    """Arkusze AR (rzuty, przekroje, elewacje) + detale PT-AR-D — z ``raport_widokow.json`` katalogów rysunków."""
    ark, uwagi = [], []
    kat_ar = next((k for k in KAT_AR if (k / "raport_widokow.json").exists()), None)
    for kat in [kat_ar, KAT_DETALE]:
        if kat is None:
            uwagi.append("brak katalogu rysunków AR z raport_widokow.json")
            continue
        rap = json.loads((kat / "raport_widokow.json").read_text(encoding="utf-8"))
        for a in rap.get("arkusze", []):
            pdf = REPO / a["pliki"]["pdf"] if not Path(a["pliki"]["pdf"]).is_absolute() else Path(a["pliki"]["pdf"])
            if not pdf.exists():
                ark.append(Arkusz.planowany(a["nr"], a["tytul"], a.get("skala", "—"), a.get("format", "A3")))
                uwagi.append(f"{a['nr']}: brak pliku PDF — strona zastępcza")
                continue
            if not a.get("qa", {}).get("ok", True):
                uwagi.append(f"{a['nr']}: kontrola QA arkusza z błędami: {a['qa'].get('errors')}")
            ark.append(Arkusz.z_pdf(pdf))
    return ark, uwagi, kat_ar


# ============================================================================================ rozdziały
FUNKCJE = {"izolacja": "izolacja cieplna", "szczelnosc": "szczelność powietrzna", "paroizolacja": "paroizolacja",
           "hydroizolacja": "hydroizolacja", "przeciwwilgociowa": "izolacja przeciwwilgociowa/przeciwradonowa",
           "wiatroizolacja": "wiatroizolacja", "rozdzielajaca": "warstwa rozdzielająca", "drenaz": "drenaż",
           "geowloknina": "filtracja/ochrona", "substrat": "substrat roślinny", "bariera_korzenna": "bariera korzenna",
           "spadkowa": "warstwa spadkowa", "pustka": "pustka powietrzna"}
TYPY_PRZEGR = {"sciana_zewn": "ściana zewnętrzna", "sciana_wewn_nosna": "ściana wewnętrzna nośna",
               "scianka_dzialowa": "ścianka działowa", "attyka": "attyka", "podloga_na_gruncie": "podłoga na gruncie",
               "strop": "strop / sufit", "stropodach": "stropodach / dach", "taras": "płyta wysunięta / okap"}


def nazwa_przegrody(txt: str) -> str:
    """Nazwa z modelu bez wtrąceń „(U = …)” — wartość U podaje wyłącznie obliczenie (rozdz. 4)."""
    t = re.sub(r"\s*\((U[ _]?(stropu \S+ )?=|U_equiv)[^()]*(\([^()]*\)[^()]*)*\)", "", txt)
    return re.sub(r";\s*$", "", t).strip()


def rozdz_zakres(o: Opis, D: dict, kat_ar: Path | None):
    d = o.dok.dane
    w = D["wsk"]
    o.czesc("Część opisowa — architektura", podstawa="§ 7 ust. 1 pkt 3, § 23 RPB")
    o.rozdzial("Przedmiot i zakres tomu", f"""
    Przedmiotem tomu jest projekt techniczny w specjalności architektonicznej dla zamierzenia
    „{d['nazwa_zamierzenia']}” — {d['obiekt']}, {d['lokalizacja']}. Obiekt kategorii {d['kategoria']};
    {w['kondygnacje_nadziemne']['wartosc']} kondygnacje nadziemne, wysokość wg WT § 6:
    {L(w['wysokosc_WT6']['wartosc'])} m (grupa wysokości {w['wysokosc_WT6'].get('grupa', '—')}); 1 lokal mieszkalny.
    Dane działki, MPZP i gruntu są przykładowe {DANE_PRZYKLADOWE}.

    Tom PT-1 AR obejmuje: rozwiązania konstrukcyjno-materiałowe przegród zewnętrznych i wewnętrznych
    (§ 23 pkt 4 RPB), ocenę wymogu analizy akustycznej (§ 23 pkt 4a), obliczenia cieplno-wilgotnościowe przegród
    i węzłów, zestawienia przegród, stolarki i wykończeń, opis ciągłości warstw („4 linii”) i odwodnienia oraz dane
    dotyczące warunków ochrony przeciwpożarowej w zakresie architektury (§ 23 pkt 10). Część rysunkowa (§ 24 pkt 1–2)
    obejmuje rzuty z rzutem dachu, przekroje i elewacje w skali 1:50 oraz detale w skalach 1:5 i 1:10.

    **Pozostałe punkty § 23 RPB — gdzie opracowano:** pkt 1–2 (konstrukcja, posadowienie) — PT-2 BO; pkt 3
    (dokumentacja geologiczno-inżynierska) — nie dotyczy (warunki proste, rejestr C.2); pkt 5 i 6 — nie dotyczy
    (obiekt mieszkalny, niebędący obiektem liniowym); pkt 7–9 i 11 — PT-3 IS i PT-4 IE (instalacje, charakterystyka
    energetyczna); pkt 10 — w każdym tomie stosownie do zakresu (tu: rozdz. 8).

    **Podstawy:** PB (t.j. Dz.U. 2026 poz. 524 ze zm.) art. 34 ust. 3 pkt 4; RPB (t.j. Dz.U. 2022 poz. 1679 ze zm.)
    § 23–24; WT 2002 (t.j. Dz.U. 2022 poz. 1225 ze zm.) stosowane na podstawie art. 102a PB; PN-EN ISO 6946:2017-10,
    PN-EN ISO 13370:2017-09, PN-EN ISO 10077-1:2017-10, PN-EN ISO 10211:2017-09, PN-EN ISO 13788:2013-05,
    PN-EN ISO 14683:2017-09 (rejestr wymagań, W-243…W-250). Tom jest zgodny z PZT i PAB (PB art. 34 ust. 3c).
    """, podstawa="§ 23 RPB")
    o.rozdzial("Wyroby budowlane — zasada doboru", f"""
    Wyroby określono **parametrami wymaganymi** (λ obliczeniowe, grubość, klasa reakcji na ogień, opór dyfuzyjny s_d,
    U_w/U_D, g, klasa szczelności). Nazwy systemów i dane z kart katalogowych przywołane w modelu są
    **przykładowe — dopuszcza się wyroby równoważne** o parametrach nie gorszych, wprowadzone do obrotu zgodnie
    z PB art. 10 (oznakowanie CE lub znak budowlany B, deklaracja właściwości użytkowych). Wartości oznaczone
    {ZAL} (założenie) i {NZW} (niezweryfikowane) wymagają potwierdzenia deklaracją wybranego wyrobu przed
    wbudowaniem.
    """, podstawa="PB art. 10")


def rozdz_przegrody(o: Opis, D: dict):
    m, ob = D["m"], D["ob"]
    from lamela.obliczenia.fizyka.warstwy import funkcja_warstwy, mat_props
    U_kod = {}
    for (kod, rola), wu in ob.u.items():
        if rola not in ROLE_WEWN:
            U_kod.setdefault(kod.split("|")[0], wu)
    o.rozdzial("Rozwiązania konstrukcyjno-materiałowe przegród", """
    Przegrody zestawiono z modelu budynku (sekcje `przegrody` i `materialy`). Warstwy ścian podano od strony
    wewnętrznej, warstwy przegród poziomych — od góry. Grubości w milimetrach; λ — wartość obliczeniowa
    [W/(m·K)]. Współczynniki U wyznaczono w rozdz. 4.1.
    """, podstawa="§ 23 pkt 4 RPB", nowa_strona=True)
    wiersze = []
    for kod, p in m.przegrody.items():
        wu = U_kod.get(kod)
        wiersze.append({"Kod": kod, "Rodzaj": TYPY_PRZEGR.get(p.typ, p.typ), "Nazwa (model)": nazwa_przegrody(p.nazwa),
                        "Grubość [mm]": round(p.grubosc * 1000), "U [W/(m²·K)]": wu.U_zaokr if wu else None,
                        "Detale": ", ".join(sorted({d for d, v in D["detale"].items()
                                                    if any(kod in (e.get("przegrody") or []) for e in
                                                           (m.raw.get("wezly") or []) if e.get("id") in v["wezly"])}))
                        or "—"})
    o.tabela(wiersze, tytul="Zestawienie przegród budowlanych", formaty={"U [W/(m²·K)]": 2, "Grubość [mm]": 0},
             szerokosci=["16mm", "24mm", None, "15mm", "15mm", "22mm"], wyrownanie={"Detale": "l"},
             uwagi=["U — wartość z obliczenia wg PN-EN ISO 6946 / 13370 (rozdz. 4.1), zaokrąglona do 2 cyfr "
                    "znaczących; „—” — przegroda wewnętrzna między pomieszczeniami ogrzewanymi (bez wymagań U).",
                    "Detale — detale PT-AR-D obejmujące węzły z udziałem przegrody (sekcja `wezly` modelu)."],
             zrodlo="model/budynek.yaml — przegrody; lamela.obliczenia.fizyka_energia")
    grupy = [("Przegrody zewnętrzne i oddzielające od garażu", lambda p: p.typ in (
        "sciana_zewn", "attyka", "podloga_na_gruncie", "stropodach", "taras") or p.kod in ("SWG", "SUF-ZEW", "SUF-G")),
             ("Przegrody wewnętrzne", lambda p: True)]
    zrobione = set()
    for tyt, war in grupy:
        o.rozdzial(tyt, poziom=2)
        for kod, p in m.przegrody.items():
            if kod in zrobione or not war(p):
                continue
            zrobione.add(kod)
            rows = []
            for k, w in enumerate(p.warstwy, 1):
                mt = m.materialy.get(w.mat)
                raw = (p.raw.get("warstwy") or [{}])[k - 1] if k - 1 < len(p.raw.get("warstwy") or []) else {}
                fn = funkcja_warstwy(mat_props(m.materialy, w.mat), raw)
                uw = []
                if raw.get("klin"):
                    uw.append(f"spadkowa {L(raw['klin']['d_min'] * 1000, 0)}–{L(raw['klin']['d_max'] * 1000, 0)} mm")
                if raw.get("frakcje"):
                    uw.append("niejednorodna: " + ", ".join(f"{f['mat']} {L(f['udzial'] * 100, 0)} %"
                                                           for f in raw["frakcje"]))
                if w.konstrukcyjna:
                    uw.append("warstwa nośna / konstrukcyjna")
                rows.append({"Lp.": k, "Materiał / wyrób (parametry wymagane)": mt.nazwa if mt else w.mat,
                             "d [mm]": w.d * 1000, "λ [W/(m·K)]": mt.lambda_ if mt else None,
                             "Funkcja": FUNKCJE.get(fn, fn if fn != "inna" else "—"), "Uwagi": "; ".join(uw) or "—"})
            o.tabela(rows, tytul=f"{kod} — {nazwa_przegrody(p.nazwa)}", formaty={"d [mm]": 1, "λ [W/(m·K)]": 3},
                     szerokosci=["8mm", None, "13mm", "15mm", "30mm", "34mm"], wyrownanie={"Uwagi": "l"},
                     klasa="zwarta")
