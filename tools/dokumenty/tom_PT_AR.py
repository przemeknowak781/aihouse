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
                              liczba, DANE_PRZYKLADOWE, ZAL, NZW, zamknij_przegladarke)
from lamela.obliczenia.wspolne import wymaganie  # noqa: E402

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
    """Nazwa z modelu bez wtrąceń „(U = …)” — wartość U podaje wyłącznie obliczenie."""
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
    energetyczna); pkt 10 — w każdym tomie stosownie do zakresu (tu: rozdział „Dane dotyczące warunków ochrony przeciwpożarowej”).

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
    [W/(m·K)]. Współczynniki U wyznaczono w rozdziale „Obliczenia cieplno-wilgotnościowe przegród i węzłów”.
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
             uwagi=["U — wartość z obliczenia wg PN-EN ISO 6946 / 13370 (obliczenia cieplno-wilgotnościowe), zaokrąglona do 2 cyfr "
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


def rozdz_akustyka(o: Opis, D: dict):
    m = D["m"]
    n_pz, z_pz = wym("akustyka", "norma_izolacyjnosc_przegrod")
    n_hal, z_hal = wym("akustyka", "norma_poziomy_w_pomieszczeniach")
    akust = [f"{k} — {nazwa_przegrody(p.nazwa)}" for k, p in m.przegrody.items()
             if re.search(r"akust|R'?w|R'A1", p.nazwa)]
    akust += [f"{k} — {v.get('opis', '')}" for k, v in (m.raw.get("stolarka") or {}).items()
              if re.search(r"akust|R_w", str(v.get("opis", "")))]
    o.rozdzial("Analiza akustyczna (§ 23 pkt 4a RPB) — nie dotyczy", f"""
    **Nie dotyczy.** Zgodnie z § 23 pkt 4a RPB (dodanym rozp. Dz.U. 2023 poz. 2405) analizę w zakresie rozwiązań
    technicznych i materiałowych mających na celu spełnienie wymagań akustycznych sporządza się „w przypadku budynku
    mieszkalnego jednorodzinnego z dwoma lokalami, budynku mieszkalnego jednorodzinnego w zabudowie szeregowej lub
    bliźniaczej lub budynku mieszkalnego wielorodzinnego”. Projektowany budynek jest wolnostojącym budynkiem
    mieszkalnym jednorodzinnym z **jednym** lokalem (rejestr W-231).

    Wymagania WT § 326 ust. 1–3 obowiązują niezależnie od analizy: poziom hałasu w pomieszczeniach wg {n_hal}
    ({z_hal}), izolacyjność akustyczna przegród wg {n_pz} ({z_pz}). Rozwiązania ograniczające przenoszenie
    dźwięku przyjęte w modelu:
    """, podstawa="§ 23 pkt 4a RPB")
    if akust:
        o.dok.lista(akust)
        o.md.append("\n".join(f"* {a}" for a in akust))


def rozdz_U(o: Opis, D: dict):
    ob = D["ob"]
    from lamela.obliczenia.fizyka.u_przegrody import ROLA_OPIS
    o.rozdzial("Obliczenia cieplno-wilgotnościowe przegród i węzłów", podstawa="W-243…W-250", nowa_strona=True)
    zal = "; ".join(f"{z.tresc} {z.status}".strip() for z in D["R"]["zal"]["U"].lista[:6])
    o.rozdzial("Współczynniki przenikania ciepła U (PN-EN ISO 6946, PN-EN ISO 13370)", f"""
    Opory przejmowania ciepła R_si/R_se wg kierunku strumienia (PN-EN ISO 6946:2017-10 p. 6.8); warstwy niejednorodne
    — metoda kresów (p. 6.7.2); poprawki ΔU wg zał. F (nieszczelności ΔU_g, łączniki ΔU_f, dach odwrócony ΔU_r);
    izolacja spadkowa — zał. C (U średnie po powierzchni). Wymagania U_C,max — WT zał. 2 pkt 1.1–1.2 (W-243, W-244);
    cele projektowe — W-245 {ZAL}. Założenia obliczeń: {zal}.
    """, poziom=2, podstawa="PN-EN ISO 6946:2017-10")
    rows, szczeg = [], []
    for (kod, rola), wu in ob.u.items():
        if rola in ROLE_WEWN:
            continue
        ocena = "—" if wu.spelnia_WT is None else ("spełnia" if wu.spelnia_WT else "NIE SPEŁNIA")
        rows.append({"Przegroda": kod.split("|")[0], "Rola": ROLA_OPIS.get(rola, rola), "R_T [m²·K/W]": wu.R_T,
                     "U₀ [W/(m²·K)]": wu.U0, "ΔU [W/(m²·K)]": wu.dU, "U [W/(m²·K)]": wu.U_zaokr,
                     "U_max [W/(m²·K)]": wu.U_max, "U_cel [W/(m²·K)]": wu.U_cel, "Ocena": ocena})
        szczeg.append((kod, rola, wu))
    g = ob.grunt
    if g is not None:
        rows.append({"Przegroda": "POD-0 (grunt)", "Rola": "podłoga na gruncie — U_equiv wg PN-EN ISO 13370",
                     "R_T [m²·K/W]": g.R_f, "U₀ [W/(m²·K)]": g.U0, "ΔU [W/(m²·K)]": None, "U [W/(m²·K)]": g.U_zaokr,
                     "U_max [W/(m²·K)]": g.U_max, "U_cel [W/(m²·K)]": g.U_cel,
                     "Ocena": "—" if g.spelnia_WT is None else ("spełnia" if g.spelnia_WT else "NIE SPEŁNIA")})
    o.tabela(rows, tytul="Współczynniki przenikania ciepła przegród zewnętrznych — zestawienie",
             formaty={"R_T [m²·K/W]": 2, "U₀ [W/(m²·K)]": 3, "ΔU [W/(m²·K)]": 3, "U [W/(m²·K)]": 2,
                      "U_max [W/(m²·K)]": 2, "U_cel [W/(m²·K)]": 2}, klasa="zwarta", wyrownanie={"Ocena": "c"},
             uwagi=["U — wartość do bilansu (U₀ + ΔU; dla izolacji spadkowej — średnia wg zał. C), 2 cyfry znaczące. "
                    "Dla podłogi na gruncie R_T oznacza R_f (bez R_si/R_se)."],
             zrodlo="lamela.obliczenia.fizyka (u_przegrody, grunt); wymagania.yaml — sekcja energia")
    if g is not None:
        iz = g.izolacja
        o.tekst(f"""
        Podłoga na gruncie (PN-EN ISO 13370:2017-09): A = {L(g.A, 1)} m², P = {L(g.P, 1)} m, B' = {L(g.B, 2)} m,
        d_t = {L(g.d_t, 2)} m, U = {L(g.U_zaokr)} W/(m²·K). Izolacja krawędziowa
        {iz.typ if iz else '—'} D = {L(iz.D if iz else None)} m, d_n = {L(iz.d_n if iz else None)} m,
        λ_n = {L(iz.lam_n if iz else None, 3)} W/(m·K) — R_n ≥ R_min = {L(g.R_obwod_min, 1)} m²·K/W:
        {'spełnia' if g.spelnia_obwodowa else 'do sprawdzenia'} (WT zał. 2 pkt 1.4; W-246).
        """)
    o.rozdzial("Obliczenie U — układy warstw z oporami cieplnymi", poziom=2)
    for kod, rola, wu in szczeg:
        wr = [{"Lp.": w.lp, "Warstwa": w.nazwa, "d [mm]": w.d * 1000, "λ [W/(m·K)]": w.lam, "R [m²·K/W]": w.R,
               "Rodzaj": w.rodzaj.replace("_", " ")} for w in wu.warstwy]
        wr.insert(0, {"_klasa": "pod", "Lp.": "", "Warstwa": "R_si", "d [mm]": None, "λ [W/(m·K)]": None,
                      "R [m²·K/W]": wu.Rsi, "Rodzaj": wu.kierunek})
        wr.append({"_klasa": "pod", "Lp.": "", "Warstwa": "R_se", "d [mm]": None, "λ [W/(m·K)]": None,
                   "R [m²·K/W]": wu.Rse, "Rodzaj": ""})
        wr.append({"_klasa": "suma", "Lp.": "", "Warstwa": "R_T (kresy: " + (f"{L(wu.R_gorny, 2)}/{L(wu.R_dolny, 2)}"
                   if wu.R_gorny else "—") + ")", "d [mm]": sum(w.d for w in wu.warstwy) * 1000,
                   "λ [W/(m·K)]": None, "R [m²·K/W]": wu.R_T, "Rodzaj": ""})
        u = [f"U₀ = 1/R_T = {L(wu.U0, 3)}; ΔU_g = {L(wu.dU_g, 3)}, ΔU_f = {L(wu.dU_f, 3)}, ΔU_r = {L(wu.dU_r, 3)}; "
             f"U_c = {L(wu.U_c, 3)}" + (f"; izolacja spadkowa: U_śr = {L(wu.klin.get('U_sr'), 3)} "
                                        f"({wu.klin.get('metoda', 'zał. C')})" if wu.klin else "")
             + f"; **U = {L(wu.U_zaokr)} W/(m²·K)** (U_max = {L(wu.U_max)}; {wu.wym_zrodlo or 'WT zał. 2 pkt 1.1'})."]
        u += [x for x in wu.uwagi][:3]
        o.tabela(wr, tytul=f"{kod.split('|')[0]} — {ROLA_OPIS.get(rola, rola)}: obliczenie U",
                 formaty={"d [mm]": 1, "λ [W/(m·K)]": 3, "R [m²·K/W]": 3}, klasa="zwarta", uwagi=u,
                 szerokosci=["8mm", None, "15mm", "15mm", "17mm", "26mm"])


def _karta(mostki: dict, wid: str) -> list[dict]:
    """Wpisy kart mostków (PN-EN ISO 10211) dla węzła modelu — sam węzeł albo jego podwęzły a/b/c."""
    k = [w for w in mostki.get("wezly", []) if w["id"] == wid]
    return k or [w for w in mostki.get("wezly", []) if re.fullmatch(re.escape(wid) + r"[a-z]", w["id"])]


def rozdz_mostki(o: Opis, D: dict):
    ob, mostki, R = D["ob"], D["mostki"], D["R"]
    fr = R["frsi"]
    f_wym = fr.f_Rsi_wym
    o.rozdzial("Mostki cieplne — ψ i f_Rsi (PN-EN ISO 10211, PN-EN ISO 13788)", f"""
    Węzły liniowe obliczono numerycznie w modelu 2D (PN-EN ISO 10211:2017-09; karty węzłów:
    `projekt/08_obliczenia/mostki/katalog_mostkow.md`). ψ_oi — w systemie wymiarów wewnętrznych całkowitych.
    Do bilansu (H_TB) przyjęto wartości projektowe z sekcji `wezly` modelu (runda poprawek; węzły złożone —
    średnia ważona podwęzłów). Mostki punktowe χ — wartości przykładowe {DANE_PRZYKLADOWE} do zastąpienia
    deklaracją (ETA) wybranych łączników. Kryterium kondensacji powierzchniowej i pleśni:
    f_Rsi ≥ f_Rsi,wym = max(f_Rsi,kryt = {L(fr.f_Rsi_kryt, 3)} — miesiąc krytyczny {fr.miesiac_kryt + 1},
    {fr.opis_wilg}; {L(fr.f_Rsi_WT)} — WT zał. 2 pkt 2.2.1) = **{L(f_wym, 3)}**.
    """, poziom=2, podstawa="PN-EN ISO 10211, 13788, 14683")
    rows, rozbiezne = [], []
    for w in ob.wezly:
        if w.psi is None:
            continue
        kk = _karta(mostki, w.id)
        psi_k = "; ".join(f"{x['id'][len(w.id):] or ''}{':' if len(kk) > 1 else ''} {L(x['psi_oi'], 3)}".strip()
                          for x in kk) or "—"
        fk = min((x["f_rsi"] for x in kk), default=None)
        if len(kk) == 1 and abs(kk[0]["psi_oi"] - w.psi) > 0.005:
            rozbiezne.append(w.id)
        f_ocena = w.f_rsi if w.f_rsi is not None else fk
        rows.append({"Węzeł": w.id, "Opis": w.nazwa[:70] + ("…" if len(w.nazwa) > 70 else ""),
                     "ψ_oi karta [W/(m·K)]": psi_k, "ψ projekt [W/(m·K)]": w.psi, "l [m]": w.dlugosc,
                     "ψ·l [W/K]": w.H, "f_Rsi karta": fk, "f_Rsi projekt": w.f_rsi,
                     "f_Rsi ≥ wym.": "—" if f_ocena is None else ("tak" if f_ocena >= f_wym - 1e-9 else "NIE"),
                     "Detal": detale_wezla(D["detale"], w.id)})
    o.tabela(rows, tytul="Mostki cieplne liniowe — ψ, długości, f_Rsi",
             formaty={"ψ projekt [W/(m·K)]": 3, "l [m]": 2, "ψ·l [W/K]": 2, "f_Rsi karta": 3, "f_Rsi projekt": 3},
             klasa="zwarta", wyrownanie={"Opis": "l", "Detal": "l", "ψ_oi karta [W/(m·K)]": "r"},
             szerokosci=["12mm", None, "17mm", "13mm", "11mm", "11mm", "11mm", "11mm", "10mm", "20mm"],
             uwagi=[f"Rozbieżność karty i wartości projektowej > 0,005 W/(m·K): {', '.join(rozbiezne)} — wartość "
                    "projektowa pochodzi z rundy poprawek modelu; karty węzłów należy odświeżyć "
                    "(tools/mostki_budynku.py) przed wydaniem."] if rozbiezne else None,
             zrodlo="model/budynek.yaml — wezly; projekt/08_obliczenia/mostki/zestawienie_mostkow.json")
    pkt = [{"Węzeł": w.id, "Opis": w.nazwa, "n [szt.]": w.liczba, "χ [W/K]": w.chi, "n·χ [W/K]": w.H,
            "Źródło χ": w.zrodlo_psi or w.status} for w in ob.wezly if w.chi is not None]
    if pkt:
        o.tabela(pkt, tytul="Mostki cieplne punktowe χ", formaty={"n [szt.]": 0, "χ [W/K]": 3, "n·χ [W/K]": 2},
                 klasa="zwarta", wyrownanie={"Źródło χ": "l"})
    o.tekst(f"""
    Współczynnik strat przez mostki cieplne **H_TB = Σψ·l + Σχ = {L(ob.H_TB, 2)} W/K** (moduł energii, ψ projektowe
    z modelu; do charakterystyki energetycznej w PT-3 IS).
    """)
    # f_Rsi przegród
    el = [e for e in fr.elementy if not str(e["id"]).startswith("WZ")]
    o.tabela([{"Przegroda": e["id"], "Opis": e["opis"], "f_Rsi": e["f_Rsi"], "Metoda": e["zrodlo"],
               "Ocena": "spełnia" if e["ok"] else "NIE SPEŁNIA"} for e in el],
             tytul=f"Czynnik temperaturowy f_Rsi przegród w polu (wymagane ≥ {L(f_wym, 3)})",
             formaty={"f_Rsi": 3}, klasa="zwarta", wyrownanie={"Opis": "l", "Metoda": "l"},
             zrodlo="lamela.obliczenia.fizyka.kondensacja — f_rsi_przegrody, f_rsi_min")


def rozdz_kondensacja(o: Opis, D: dict):
    R = D["R"]
    gl = R["glaser"]
    zal = "; ".join(f"{z.tresc} {z.status}".strip() for z in R["zal"]["wilg"].lista)
    o.rozdzial("Kondensacja międzywarstwowa (PN-EN ISO 13788, metoda Glasera)", f"""
    Obliczenie miesięczne dla przegród zewnętrznych i oddzielających od garażu. Założenia: {zal}.
    Wymaganie: brak kondensacji albo kondensacja okresowa wysychająca w cyklu rocznym (WT zał. 2 pkt 2.2.5; W-248).
    """, poziom=2, podstawa="PN-EN ISO 13788:2013-05")
    rows = []
    for g in gl:
        rows.append({"Przegroda": g.kod.split("|")[0], "Rola": g.rola.replace("_", " "),
                     "Kondensacja": "tak" if g.kondensacja else "nie",
                     "M_a,max [g/m²]": g.M_a_max * 1000, "Wysycha": "tak" if g.wysycha else "nie",
                     "s_d paroizolacji istn. [m]": g.sd_par_ist, "s_d wym. (brak kond.) [m]": g.sd_par_wym,
                     "Ocena": ("dopuszczalna" if g.dopuszczalna else "NIEDOPUSZCZALNA") + " — " + g.ocena})
    o.tabela(rows, tytul="Kondensacja międzywarstwowa — wyniki", klasa="zwarta",
             formaty={"M_a,max [g/m²]": 1, "s_d paroizolacji istn. [m]": 1, "s_d wym. (brak kond.) [m]": 1},
             wyrownanie={"Ocena": "l"}, szerokosci=["16mm", "20mm", "15mm", "15mm", "13mm", "17mm", "17mm", None],
             uwagi=[u for g in gl for u in g.uwagi[:1]][:3] or None,
             zrodlo="lamela.obliczenia.fizyka.kondensacja — glaser, wymagane_sd_paroizolacji")
    cg = D["ob"].ciaglosc
    braki = [(c.kod, u.opis) for c in cg for u in c.braki]
    o.tekst("Kontrola ciągłości warstw funkcjonalnych w przekroju przegród (izolacja, szczelność, paroizolacja, "
            "ochrona przed wodą): " + ("**brak braków** w " + ", ".join(c.kod.split("|")[0] for c in cg) + "."
                                       if not braki else "braki: " + "; ".join(f"{k}: {t}" for k, t in braki) + "."))


TYPY_OTW = {"okno": "okno", "fix": "przeszklenie stałe", "drzwi_zewn": "drzwi zewnętrzne",
            "drzwi_przesuwne_HS": "drzwi podnoszono-przesuwne HS", "brama": "brama garażowa",
            "drzwi": "drzwi wewnętrzne", "otwor": "otwór bez stolarki"}
OSLONY = {"zaluzja_zewn": "żaluzja zewn.", "roleta_zewn": "roleta zewn.", "screen_zip": "screen ZIP", "brak": "—"}
ZEWN = ("okno", "fix", "drzwi_zewn", "drzwi_przesuwne_HS", "brama")


def _zakres(v: list, n: int = 2) -> str:
    v = [x for x in v if x is not None]
    if not v:
        return "—"
    return L(min(v), n) if abs(max(v) - min(v)) < 10 ** -n else f"{L(min(v), n)}–{L(max(v), n)}"


def rozdz_stolarka(o: Opis, D: dict):
    m, ob = D["m"], D["ob"]
    st = m.raw.get("stolarka") or {}
    kl_min, kl_zr = wym("energia", "okna_klasa_szczelnosci_min")
    g_max, g_zr = wym("energia", "g_c_max")
    grupy: OrderedDict = OrderedDict()
    montaze: OrderedDict = OrderedDict()
    for ot in m.otwory():
        if ot.typ == "otwor":
            continue
        g = grupy.setdefault(ot.symbol or ot.id, dict(o=ot, n=0, kond=set(), ids=[], montaz=set()))
        g["n"] += 1
        g["kond"].add(ot.kond)
        g["ids"].append(ot.id)
        mt = ot.raw.get("montaz")
        if mt:
            g["montaz"].add(montaze.setdefault(mt, f"M{len(montaze) + 1}"))
    o.rozdzial("Zestawienie stolarki okiennej i drzwiowej", f"""
    Zestawienie stolarki wygenerowano z modelu (sekcje `otwory` i `stolarka`), grupując otwory według symbolu
    (W-317). Wymiary — w świetle otworu w murze. Parametry cieplne: U_w obliczone wg PN-EN ISO 10077-1:2017-10
    dla wymiarów otworu i danych przykładowego wyrobu {DANE_PRZYKLADOWE}; U_w wym. — wartość wymagana dla wyrobu
    (model); U_max — WT zał. 2 pkt 1.2 (W-244). Szczelność: klasa ≥ {kl_min} ({kl_zr}). Całkowita przepuszczalność
    energii promieniowania słonecznego g = f_C·g_n ≤ {L(g_max)} dla okien E, S, W ({g_zr}).
    """, podstawa="W-317, W-244, W-247, W-249", nowa_strona=True)
    U_sym, g_sym = {}, {}
    for wo in ob.okna.values():
        U_sym.setdefault(wo.symbol, []).append(wo)
    for x in ob.g_spr:
        g_sym.setdefault(x.symbol, []).append(x)
    r1, r2, r3 = [], [], []
    for sym, g in grupy.items():
        ot = g["o"]
        otw = ot.otwieranie or {}
        opis = (st.get(sym) or {}).get("opis", "—")
        wiersz = {"Symbol": sym, "Rodzaj": TYPY_OTW.get(ot.typ, ot.typ), "Opis wyrobu (parametry wymagane)": opis,
                  "Wymiary [cm]": f"{round(ot.szer * 100)} × {round(ot.wys * 100)}", "Szt.": g["n"],
                  "Kond.": ", ".join(sorted(g["kond"])),
                  "Otwieranie": ", ".join(str(x) for x in (otw.get("rodzaj"), otw.get("strona"),
                                                             str(otw.get("kierunek", "")).replace("_", " ")) if x)
                  or "stałe"}
        if ot.typ not in ZEWN:
            r3.append(wiersz)
            continue
        wiersz.update({"Osłona": OSLONY.get(ot.oslona or "brak", ot.oslona), "Montaż": ", ".join(sorted(g["montaz"]))
                       or "—"})
        r1.append(wiersz)
        wos = U_sym.get(sym, [])
        dn = wos[0].dane if wos else None
        gs = g_sym.get(sym, [])
        ms = st.get(sym) or {}
        r2.append({"Symbol": sym, "U_w obl. [W/(m²·K)]": _zakres([w.U_w for w in wos]),
                   "U_w wym. [W/(m²·K)]": ms.get("U_w", ms.get("U_D")),
                   "U_max [W/(m²·K)]": wos[0].U_max if wos else None, "g_n": ms.get("g_n", dn.g_n if dn else None),
                   "f_C": _zakres([x.f_C for x in gs]), "g": _zakres([x.g for x in gs], 3),
                   "Ocena g": ("; ".join(sorted({x.zwolnienie for x in gs if x.zwolnienie != "—"})) or
                               ("spełnia" if all(x.spelnia for x in gs) else "NIE SPEŁNIA")) if gs else "—",
                   "Klasa szczeln.": dn.klasa_szczelnosci if dn and dn.klasa_szczelnosci else
                   (f"≥ {kl_min}" if ot.typ in ("okno", "fix", "drzwi_przesuwne_HS") else "—")})
    o.tabela(r1, tytul="Zestawienie stolarki zewnętrznej — wymiary, otwieranie, osłony, montaż", klasa="zwarta",
             wyrownanie={"Opis wyrobu (parametry wymagane)": "l", "Otwieranie": "l"},
             szerokosci=["11mm", "20mm", None, "16mm", "8mm", "12mm", "17mm", "14mm", "11mm"],
             zrodlo="model/budynek.yaml — otwory, stolarka (grupowanie po symbolu)")
    o.tabela(r2, tytul="Zestawienie stolarki zewnętrznej — parametry cieplne, g, szczelność", klasa="zwarta",
             formaty={"U_w wym. [W/(m²·K)]": 2, "U_max [W/(m²·K)]": 1, "g_n": 2}, wyrownanie={"Ocena g": "l"},
             uwagi=["U_w obl. — zakres dla otworów danego symbolu (PN-EN ISO 10077-1; drzwi — U_D z danych wyrobu). "
                    "f_C — współczynnik redukcji osłony (WT zał. 2 pkt 2.1.3 lub PN-EN ISO 52022-1 metodą "
                    f"uproszczoną {NZW}). Deklarowane U_w, g, klasa szczelności wybranego wyrobu — do potwierdzenia "
                    "deklaracją właściwości użytkowych."],
             zrodlo="lamela.obliczenia.fizyka.okna — u_okna, sprawdz_g")
    o.tabela([{"Kod": k, "Sposób montażu (osadzenia) stolarki": t, "Detal": detale_wezla(D["detale"], "WZ-11")}
              for t, k in montaze.items()], tytul="Montaż stolarki zewnętrznej", klasa="zwarta",
             wyrownanie={"Sposób montażu (osadzenia) stolarki": "l"}, szerokosci=["12mm", None, "36mm"])
    if r3:
        o.tabela(r3, tytul="Zestawienie drzwi wewnętrznych", klasa="zwarta",
                 wyrownanie={"Opis wyrobu (parametry wymagane)": "l", "Otwieranie": "l"},
                 szerokosci=["12mm", "22mm", None, "17mm", "9mm", "14mm", "20mm"])


def rozdz_wykonczenia(o: Opis, D: dict):
    m = D["m"]
    uzyte: OrderedDict = OrderedDict()
    rows = []
    for p in m.raw.get("pomieszczenia") or []:
        kody = [p.get("posadzka"), p.get("sciany_wyk"), p.get("sufit")]
        for k in kody:
            if k:
                uzyte.setdefault(k, None)
        rows.append({"Nr": nr_iso(p["id"], p["kond"]), "Pomieszczenie": p["nazwa"], "Posadzka": p.get("posadzka") or "—",
                     "Podłoga / strop": p.get("podloga") or "—", "Ściany": p.get("sciany_wyk") or "—",
                     "Sufit": p.get("sufit") or "—", "θ_i [°C]": p.get("temp")})
    o.rozdzial("Zestawienie wykończeń wnętrz", """
    Wykończenia pomieszczeń wg modelu (kody materiałów — legenda w tabeli następnej; układ warstw podłóg i stropów —
    rozdział „Rozwiązania konstrukcyjno-materiałowe przegród”). Numeracja pomieszczeń jak na rzutach (parter = 1.xx).
    """, podstawa="W-317", nowa_strona=True)
    o.tabela(rows, tytul="Wykończenia pomieszczeń", klasa="zwarta", formaty={"θ_i [°C]": 0},
             szerokosci=["10mm", None, "22mm", "22mm", "22mm", "20mm", "12mm"],
             zrodlo="model/budynek.yaml — pomieszczenia")
    o.tabela([{"Kod": k, "Wyrób / wykończenie (parametry wymagane)": (m.materialy.get(k).nazwa
                                                                    if m.materialy.get(k) else k)} for k in uzyte],
             tytul="Legenda wykończeń", klasa="zwarta", szerokosci=["24mm", None])
    el = []
    for x in m.raw.get("lamele") or []:
        mt = m.materialy.get(x.get("mat"))
        el.append({"Element": x["id"], "Rodzaj": f"lamele, elewacja {x.get('elewacja', '—')}",
                   "Opis": f"{mt.nazwa if mt else x.get('mat')}; rozstaw {L(x.get('rozstaw'))} m, "
                           f"rzędne {L(x.get('z_od'))}…{L(x.get('z_do'))} m; {x.get('uwagi', '')}"})
    for x in m.raw.get("balustrady") or []:
        el.append({"Element": x["id"], "Rodzaj": f"balustrada / pochwyt h = {L(x.get('wys'))} m", "Opis": x.get("typ", "")})
    for x in m.raw.get("tarasy") or []:
        el.append({"Element": x["id"], "Rodzaj": f"taras / podest, rzędna {L(x.get('rzedna'))} m",
                   "Opis": f"{x.get('nawierzchnia', '')}; {x.get('uwagi', '')}"})
    if el:
        o.tabela(el, tytul="Lamele, balustrady, tarasy i podesty", klasa="zwarta", wyrownanie={"Opis": "l"},
                 szerokosci=["16mm", "40mm", None], zrodlo="model/budynek.yaml — lamele, balustrady, tarasy")


def rozdz_4linie(o: Opis, D: dict):
    m, mostki = D["m"], D["mostki"]
    from lamela.obliczenia.fizyka.warstwy import funkcja_warstwy, mat_props
    zewn = [p for p in m.przegrody.values() if p.typ in ("sciana_zewn", "stropodach", "podloga_na_gruncie", "attyka")
            or p.kod in ("SUF-ZEW", "SWG")]
    fun: dict[str, OrderedDict] = {k: OrderedDict() for k in ("izolacja", "hydro", "szczel", "par")}
    for p in zewn:
        for k, w in enumerate(p.warstwy):
            raw = (p.raw.get("warstwy") or [{}])[k] if k < len(p.raw.get("warstwy") or []) else {}
            fn = funkcja_warstwy(mat_props(m.materialy, w.mat), raw)
            klucz = {"izolacja": "izolacja", "hydroizolacja": "hydro", "przeciwwilgociowa": "hydro",
                     "szczelnosc": "szczel", "paroizolacja": "par", "wiatroizolacja": "hydro"}.get(fn)
            if klucz:
                fun[klucz].setdefault(w.mat, []).append(p.kod)
    def opis(k):
        return "; ".join(f"{(m.materialy.get(mt).nazwa if m.materialy.get(mt) else mt)} ({', '.join(pp)})"
                         for mt, pp in fun[k].items()) or "—"
    o.rozdzial("Zasada „4 linii” — ciągłość warstw obudowy", f"""
    Obudowę części ogrzewanej projektuje się tak, aby cztery warstwy funkcjonalne były ciągłe w każdym węźle
    i były możliwe do narysowania jedną linią bez odrywania ołówka na każdym detalu:

    1. **I — izolacja cieplna:** {opis('izolacja')}; w węzłach — łączniki termoizolacyjne płyt wysuniętych i bloki
       termoizolacyjne u podstawy attyk (parametry wg PT-2 BO, W-272);
    2. **H — ochrona przed wodą (hydroizolacja, izolacja przeciwwilgociowa, wiatroizolacja):** {opis('hydro')};
    3. **S — szczelność powietrzna:** {opis('szczel')}; połączenia ze stolarką i przejścia instalacji — taśmy
       i mankiety systemowe; próba szczelności budynku PN-EN ISO 9972 (W-249);
    4. **P — kontrola pary wodnej:** {opis('par')}; opór dyfuzyjny warstw maleje ku stronie zimnej (sprawdzenie — „Kondensacja międzywarstwowa”).

    Ocenę ciągłości w węzłach (karty mostków, PN-EN ISO 10211) i odesłania do detali zawiera tabela poniżej.
    """, podstawa="§ 24 pkt 2 RPB; W-248, W-249", nowa_strona=True)
    zn = {"OK": "✓", "UWAGA": "!", "BRAK": "✗"}
    rows = []
    for w in mostki.get("wezly", []):
        l4 = w.get("linie4") or {}
        st = {k: zn.get((l4.get(k) or ["—"])[0], (l4.get(k) or ["—"])[0]) for k in "IHSP"}
        ci = str(l4.get("ciaglosc", "—"))
        rows.append({"Węzeł": w["id"], "Opis": w["nazwa"][:60] + ("…" if len(w["nazwa"]) > 60 else ""),
                     "I": st["I"], "H": st["H"], "S": st["S"], "P": st["P"],
                     "Ciągłość / uwaga": ci[:150] + ("…" if len(ci) > 150 else ""),
                     "Detal": detale_wezla(D["detale"], w["id"])})
    o.tabela(rows, tytul="Ciągłość „4 linii” w węzłach obudowy", klasa="zwarta",
             wyrownanie={"I": "c", "H": "c", "S": "c", "P": "c", "Opis": "l", "Ciągłość / uwaga": "l", "Detal": "l"},
             szerokosci=["12mm", "42mm", "5mm", "5mm", "5mm", "5mm", None, "22mm"],
             uwagi=["✓ — ciągłość zachowana; ! — uwaga wykonawcza (opis w kolumnie „Ciągłość / uwaga” i na karcie "
                    "węzła); ✗ — brak ciągłości."],
             zrodlo="projekt/08_obliczenia/mostki/zestawienie_mostkow.json — linie4")


def _det_tyt(detale: dict, wzorzec: str) -> str:
    tr = [f"{d} ({v['arkusz']})" for d, v in detale.items() if re.search(wzorzec, v["tytul"], re.I)]
    return ", ".join(tr) or "—"


def _rura(r: dict) -> str:
    trasa = "wewn." if "wewn" in str(r.get("trasa", "")) else "zewn."
    return f"{r['id']} DN{r.get('dn')} ({trasa}) → {r.get('do', '—')}"


def rozdz_odwodnienie(o: Opis, D: dict):
    m, det = D["m"], D["detale"]
    sp_min, sp_zr = wym("wodkan", "spadek_dachu_min")
    o.rozdzial("Odwodnienie dachów, tarasów i przyziemia", f"""
    Każde pole dachu ma izolację spadkową (spadek ≥ {L(sp_min * 100 if sp_min < 1 else sp_min, 1)} % — {sp_zr}),
    co najmniej jeden wpust z grzałką i przelew awaryjny w attyce. Obróbki attyk, wpustów i przelewów — detale
    {_det_tyt(det, 'attyk|wpust|przelew')}; rury spustowe przy cokole — {_det_tyt(det, 'rura')}; progi z odwodnieniem
    liniowym — {_det_tyt(det, 'próg')}. Wymiarowanie hydrauliczne i odbiorniki wód opadowych — PT-3 IS.
    """, podstawa="PN-EN 12056-3; W-142", nowa_strona=False)
    rows, prz = [], []
    for d in m.raw.get("dachy") or []:
        rows.append({"Dach": d["id"], "Przegroda": d.get("przegroda", "—"),
                     "Spadek [%]": (d.get("spadek") or 0) * 100,
                     "Wpusty": "; ".join(f"{w.get('opis', '').split(' — ')[0]} DN{w.get('dn')}"
                                         + (" z grzałką" if w.get("podgrzewany") else "") for w in d.get("wpusty") or [])
                     or "—",
                     "Rury spustowe": "; ".join(_rura(r) for r in d.get("rury_spustowe") or []) or "—",
                     "Attyka nad pokryciem [m]": (d.get("attyka") or {}).get("wys_nad_pokryciem")})
        for p in d.get("przelewy_awaryjne") or []:
            prz.append({"Przelew": p.get("opis", "").split(" — ")[0], "Dach": d["id"],
                        "Wymiary [cm]": f"{round(p.get('szer', 0) * 100)} × {round(p.get('wys', 0) * 100)}",
                        "Rzędna dna [m]": p.get("rzedna_dna"), "Rzędna pokrycia [m]": p.get("rzedna_pokrycia"),
                        "Δh [mm]": (p["rzedna_dna"] - p["rzedna_pokrycia"]) * 1000
                        if p.get("rzedna_dna") is not None and p.get("rzedna_pokrycia") is not None else None,
                        "Opis": p.get("opis", "")})
    o.tabela(rows, tytul="Odwodnienie dachów", klasa="zwarta", formaty={"Spadek [%]": 1, "Attyka nad pokryciem [m]": 2},
             wyrownanie={"Wpusty": "l", "Rury spustowe": "l"}, szerokosci=["10mm", "16mm", "13mm", None, None, "17mm"],
             zrodlo="model/budynek.yaml — dachy")
    if prz:
        o.tabela(prz, tytul="Przelewy awaryjne w attykach — rzędne", klasa="zwarta",
                 formaty={"Rzędna dna [m]": 3, "Rzędna pokrycia [m]": 3, "Δh [mm]": 0}, wyrownanie={"Opis": "l"},
                 szerokosci=["13mm", "10mm", "15mm", "16mm", "18mm", "12mm", None],
                 uwagi=["Δh — wzniesienie dna przelewu ponad lokalną rzędną pokrycia (wierzch hydroizolacji); przelew "
                        "działa po zablokowaniu wpustu, poniżej korony attyki. Rzędne względne: ±0,000 = posadzka "
                        f"parteru = {L(m.zero_abs, 2)} m n.p.m. {DANE_PRZYKLADOWE}."],
                 zrodlo="model/budynek.yaml — dachy.przelewy_awaryjne")
    o.tekst("Przyziemie: nawierzchnie przy budynku ze spadkiem od ścian, odwodnienia liniowe przy progach drzwi HS, "
            "drzwi zewnętrznych i bramy (tarasy i podesty — tabela „Lamele, balustrady, tarasy i podesty”); "
            "hydroizolację płyty fundamentowej wywija się na cokół (detal "
            f"{_det_tyt(det, 'cokół')}).")


def rozdz_ppoz(o: Opis, D: dict):
    m, w = D["m"], D["wsk"]
    zl, zl_z = wym("ppoz", "kategoria_ZL")
    gr, gr_z = wym("ppoz", "grupa_wysokosci")
    kmax, k_z = wym("ppoz", "zwolnienie_213_kondygnacje_max")
    kond = w["kondygnacje_nadziemne"]["wartosc"]
    ei = [f"{k} — {nazwa_przegrody(p.nazwa)}" for k, p in m.przegrody.items() if re.search(r"\bE?I\s?\d{2}", p.nazwa)]
    nro = [mt.nazwa for mt in m.materialy.values() if "NRO" in mt.nazwa]
    o.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", f"""
    Dane w zakresie architektury (§ 23 pkt 10 RPB — stosownie do zakresu projektu; dane ogólne budynku — PAB,
    § 20 ust. 1 pkt 13):

    * kategoria zagrożenia ludzi **{zl}** ({zl_z}); grupa wysokości **{gr}** ({gr_z}), wysokość wg WT § 6 —
      {L(w['wysokosc_WT6']['wartosc'])} m;
    * {kond} kondygnacje nadziemne ≤ {kmax} — wymagań klasy odporności pożarowej budynku nie stawia się ({k_z});
      budynek stanowi jedną strefę pożarową razem z garażem (W-212);
    * ściany zewnętrzne i dach — nierozprzestrzeniające ognia (W-213): ETICS jako system z klasyfikacją NRO
      ({'; '.join(nro) or 'wg deklaracji systemu'}); pokrycia dachów z klasyfikacją B_ROOF(t1) {ZAL};
    * okładziny elewacyjne i lamele mocowane mechanicznie do konstrukcji (W-216);
    * obudowy szachtów instalacyjnych: {'; '.join(ei) or 'nie występują'};
    * przejścia instalacji przez przegrody zewnętrzne poniżej terenu — gazoszczelne (W-214), uszczelnienia
      systemowe wg PT-3 IS i PT-4 IE;
    * klasy odporności ogniowej podaje się na rysunkach wyłącznie dla elementów, dla których są wymagane (W-219).
    """, podstawa="§ 23 pkt 10 RPB", nowa_strona=True)


# ============================================================================================ składanie
def buduj(D: dict, arkusze: list, kat_ar: Path | None, data: str) -> tuple[Dokument, Opis]:
    d = dane_obiektu()
    dok = Dokument("Projekt techniczny", "PT-AR", d, kod="PT-1 AR", branza="architektura", data=data,
                   tom=(1, PT_TOMY), podtytul="Tom PT-1 — architektura (AR)")
    dok.oswiadczenie_projektanta()           # PB art. 34 ust. 3d pkt 3 w brzmieniu art. 41 ust. 4a pkt 2 (PT)
    o = Opis(dok)
    o.md.append(f"<!-- wygenerowano: tools/dokumenty/tom_PT_AR.py; model: model/budynek.yaml ({data}) -->\n"
                "# PT-1 AR — projekt techniczny, architektura (źródło części opisowej)")
    rozdz_zakres(o, D, kat_ar)
    rozdz_przegrody(o, D)
    rozdz_akustyka(o, D)
    rozdz_U(o, D)
    rozdz_mostki(o, D)
    rozdz_kondensacja(o, D)
    rozdz_stolarka(o, D)
    rozdz_wykonczenia(o, D)
    rozdz_4linie(o, D)
    rozdz_odwodnienie(o, D)
    rozdz_ppoz(o, D)
    zr = kat_ar.relative_to(REPO) if kat_ar else "—"
    o.rozdzial("Wykaz rysunków — część rysunkowa", f"""
    Część rysunkowa (§ 24 pkt 1–2 RPB) obejmuje rzuty wszystkich kondygnacji z rzutem dachu, przekroje i elewacje
    w skali 1:50 (arkusze AR z katalogu `{zr}` — rysunki PAB dołączone jako podstawa rozwiązań PT; zmiany
    względem PAB — brak) oraz detale cieplne i szczelności PT-AR-D w skalach 1:5 i 1:10. Wykaz rysunków z numerami,
    skalami i formatami — karta części rysunkowej (generowana z tabliczek arkuszy).
    """, podstawa="§ 24 RPB", nowa_strona=True)
    o.tabela([{"Nr": a.nr, "Tytuł": a.tytul, "Skala": a.skala or "—", "Format": a.format or "—"} for a in arkusze],
             tytul="Wykaz rysunków tomu PT-1 AR", klasa="zwarta", szerokosci=["24mm", None, "20mm", "16mm"])
    dok.czesc_rysunkowa(arkusze)
    return dok, o


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--wyjscie", default=str(KAT_WYDANIE))
    ap.add_argument("--bez-arkuszy", action="store_true", help="bez dołączania arkuszy (szybki podgląd opisu)")
    a = ap.parse_args(argv)
    t0 = time.time()
    out = Path(a.wyjscie)
    out.mkdir(parents=True, exist_ok=True)
    KAT_ZRODLA.mkdir(parents=True, exist_ok=True)
    D = wczytaj_dane()
    data = dane_obiektu()["data"]
    arkusze, uw_ark, kat_ar = arkusze_branzy()
    for u in uw_ark:
        print("  ! arkusze:", u)
    dok, o = buduj(D, [] if a.bez_arkuszy else arkusze, kat_ar, data)
    o.zapisz(KAT_ZRODLA / "PT-1_AR_czesc_opisowa.md")
    tom = Tom("PT-1 AR", [dok], dane=dok.dane, data=data, nr=1, symbol="AR", tom=(1, PT_TOMY),
              strona_tytulowa=False, laczny_spis=False)
    w = tom.zloz(out)
    print(f"✓ {w.nazwa}: {w.strony} stron, {w.rozmiar_mb:.2f} MB → {w.sciezka}")
    r = sprawdz_tom(w, LISTY_KONTROLNE["PT_AR"])
    (KAT_ZRODLA / "raport_walidacji_PT_AR.txt").write_text(r.tekst(), encoding="utf-8")
    r.zapisz_json(KAT_ZRODLA / "raport_walidacji_PT_AR.json")
    s = r.podsumowanie()
    print(f"  walidator PT_AR: {s['status']} — OK {s['OK']}, BRAK {s['BRAK']}, DO UZUPEŁNIENIA {s['DO UZUPEŁNIENIA']}, "
          f"N/D {s['N/D']}, OSTRZ. {s['OSTRZEŻENIE']}; znaczniki [DO UZUPEŁNIENIA] ×{s['znaczniki_do_uzupelnienia']}")
    for p in r.braki:
        print(f"    ✗ {p.id} {p.opis} — {p.szczegoly}")
    zamknij_przegladarke()
    print(f"gotowe w {time.time() - t0:.1f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
