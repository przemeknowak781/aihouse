"""PAB — część opisowa, wstęp i rozdziały 1–4 (RPB § 20 ust. 1 pkt 1–4). Wszystkie liczby z ``DanePAB``."""
from __future__ import annotations

import re

from lamela.dokumenty import DANE_PRZYKLADOWE, do_uzup, liczba as L, rzedna
from lamela.dokumenty.znaczniki import INT, ZAL

RPB = "rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego (Dz.U. 2020 poz. 1609; t.j. Dz.U. 2022 " \
      "poz. 1679, zm. Dz.U. 2023 poz. 2405 i Dz.U. 2026 poz. 597)"
WT = "rozporządzenie w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (t.j. Dz.U. " \
     "2022 poz. 1225 ze zm.)"
KAT_OPIS = {"podstawowa": "podstawowa", "pomocnicza": "pomocnicza", "komunikacja": "komunikacja",
            "klatka schodowa": "komunikacja — schody", "garaż": "garaż", "techniczna": "techniczna"}


def tyt(nazwa: str, pkt: str) -> str:
    """Tytuł rozdziału z jednostką redakcyjną przepisu (§ 20 ust. 1 pkt N RPB)."""
    return f"{nazwa} (§ 20 ust. 1 pkt {pkt} RPB)"


def ok(b: bool) -> str:
    return "spełnia" if b else "NIE SPEŁNIA"


def wstep(pab, D, d):
    mp = (D.Dz.get("dzialka") or {}).get("mpzp") or do_uzup("MPZP — uchwała")
    pab.czesc_opisowa("Opis techniczny do projektu architektoniczno-budowlanego", podstawa="§ 20 RPB")
    pab.markdown(f"""
    **Podstawy opracowania:** ustawa z dnia 7 lipca 1994 r. – Prawo budowlane (t.j. Dz.U. 2026 poz. 524; dalej PB);
    {RPB} — dalej RPB; {WT} — dalej WT, w brzmieniu stosowanym na podstawie art. 102a PB w związku z oświadczeniem
    Inwestora z dnia {do_uzup('data oświadczenia Inwestora (art. 102a ust. 1 PB)')}; miejscowy plan zagospodarowania
    przestrzennego: {mp} {DANE_PRZYKLADOWE}; mapa do celów projektowych {do_uzup('nr ewidencyjny PZGiK i data')};
    opinia geotechniczna — załącznik nr 1 do niniejszego opisu {DANE_PRZYKLADOWE}.

    **Dane źródłowe wartości liczbowych:** model budynku i działki (`model/budynek.yaml`, `dzialka.yaml`,
    `instalacje.yaml`, `wyposazenie.yaml`; wersja modelu {D.B.get('meta', {}).get('wersja', '—')} z dnia
    {D.B.get('meta', {}).get('data', '—')}), biblioteka obliczeń `lamela.obliczenia` (fizyka budowli, charakterystyka
    energetyczna, instalacje), moduł wskaźników `lamela.wskazniki` (definicje ustawy o planowaniu i zagospodarowaniu
    przestrzennym, art. 2 pkt 28–35), audyt zgodności z WT `tools/audyt_wt.py` oraz wyniki symulacji mostków cieplnych
    wg PN-EN ISO 10211 (`projekt/08_obliczenia/mostki`). Wszystkie wartości zestawień są generowane z tych źródeł przy
    każdym wydaniu opisu; powierzchnie i kubatura podane z dokładnością do 0,01 (RPB § 20 ust. 1 pkt 4, W-316).

    **Oznaczenia:** {do_uzup()} — dane do uzupełnienia przed złożeniem; {DANE_PRZYKLADOWE} — dane przykładowe
    (działka, ustalenia MPZP, badania podłoża, wyroby); {ZAL} — założenie projektowe; {INT} — interpretacja przepisu.
    Numery pomieszczeń wg PN-B-01025 (parter = 1.xx), zgodnie z częścią rysunkową.
    """)


def r01(pab, D, d):
    wt6 = D.w["wysokosc_WT6"]
    kn = D.w["kondygnacje_nadziemne"]["wartosc"]
    kons = (D.B.get("konstrukcja") or {})
    geo = (D.B.get("geotechnika") or {})
    pab.rozdzial(tyt("Rodzaj i kategoria obiektu budowlanego", 1))
    pab.markdown(f"""
    Przedmiotem zamierzenia jest {d['obiekt'][0].lower() + d['obiekt'][1:]} — budynek mieszkalny jednorodzinny
    w rozumieniu art. 3 pkt 2a PB (budynek wolno stojący, służący zaspokajaniu potrzeb mieszkaniowych, stanowiący
    konstrukcyjnie samodzielną całość; wydzielono w nim jeden lokal mieszkalny), z garażem dwustanowiskowym
    i pomieszczeniem technicznym w bryle budynku. Zamierzenie budowlane:
    {d['nazwa_zamierzenia']}. Lokalizacja: {d['lokalizacja']} {DANE_PRZYKLADOWE}.

    Kategoria obiektu budowlanego: **{d['kategoria_opis']}**.
    """)
    wiersze = [
        {"Cecha": "Rodzaj obiektu", "Ustalenie": "budynek mieszkalny jednorodzinny wolnostojący",
         "Podstawa / źródło": "PB art. 3 pkt 2a"},
        {"Cecha": "Kategoria obiektu budowlanego", "Ustalenie": f"kategoria {d['kategoria']}",
         "Podstawa / źródło": "załącznik do PB"},
        {"Cecha": "Kategoria geotechniczna", "Ustalenie": f"{geo.get('kategoria', do_uzup('kategoria'))} — rozdz. 5 "
         "i załącznik nr 1", "Podstawa / źródło": "rozp. Dz.U. 2012 poz. 463 § 4; " + D.zr("geotechnika", "kategoria_geotechniczna")},
        {"Cecha": "Liczba kondygnacji nadziemnych / podziemnych", "Ustalenie": f"{kn} / 0",
         "Podstawa / źródło": D.w["kondygnacje_nadziemne"]["podstawa"]},
        {"Cecha": "Grupa wysokości", "Ustalenie": f"niski ({wt6.get('grupa')}) — H = {L(wt6['wartosc'])} m",
         "Podstawa / źródło": "WT § 6, § 8 pkt 1"},
        {"Cecha": "Kategoria zagrożenia ludzi", "Ustalenie": str(D.v("ppoz", "kategoria_ZL")),
         "Podstawa / źródło": D.zr("ppoz", "kategoria_ZL")},
        {"Cecha": "Klasa konsekwencji / niezawodności", "Ustalenie": f"{kons.get('klasa_konsekwencji', '—')} / "
         f"{kons.get('klasa_niezawodnosci', '—')}", "Podstawa / źródło": "PN-EN 1990 zał. B (model: konstrukcja)"},
        {"Cecha": "Kubatura brutto", "Ustalenie": f"{L(D.kubatura)} m³ — rozdz. 4.1",
         "Podstawa / źródło": "RPB § 20 ust. 1 pkt 4 lit. a; W-069"},
        {"Cecha": "Sprawdzenie projektu", "Ustalenie": d["sprawdzajacy"], "Podstawa / źródło": "PB art. 20 ust. 3 pkt 2"},
    ]
    pab.tabela(wiersze, tytul="Klasyfikacja obiektu", szerokosci=["52mm", None, "60mm"])
    if D.kubatura > 1000.0:
        pab.akapit(f"Kubatura brutto przekracza 1000 m³ — projekt sporządzają projektanci z uprawnieniami do projektowania "
                   f"bez ograniczeń w odpowiednich specjalnościach (W-069).")


def r02(pab, D, d):
    osoby = D.I.get("osoby") or (D.B.get("energia") or {}).get("osoby")
    mp = D.w["miejsca_postojowe"]
    pokoje = [r for r in D.pom if r["pobyt"]]
    pab.rozdzial(tyt("Zamierzony sposób użytkowania oraz program użytkowy", 2))
    pab.markdown(f"""
    Budynek przeznaczony jest na stały pobyt jednej rodziny — w projekcie przyjęto **{osoby} osób** (model: instalacje.osoby)
    — i stanowi **jeden lokal mieszkalny wielopoziomowy** na {len(D.m.kondygnacje)} kondygnacjach nadziemnych, połączonych
    wewnętrzną klatką schodową. Program obejmuje {len(pokoje)} pomieszczeń przeznaczonych na pobyt ludzi (strefa dzienna,
    pokoje, sypialnia), pomieszczenia pomocnicze (łazienki, WC, pralnia, garderoba, spiżarnia), komunikację, pomieszczenia
    techniczne oraz garaż na {mp.get('garaz', 0)} samochody osobowe w bryle budynku, dostępny bezpośrednio z domu;
    na działce {mp.get('zewn', 0)} dodatkowe stanowiska zewnętrzne (PZT). Budynek nie zawiera lokali użytkowych.
    Zestawienie pomieszczeń z powierzchniami — rozdz. 4.2.
    """)
    rows = []
    for k in D.m.kondygnacje:
        rr = [r for r in D.pom if r["kond"] == k.id]
        nazwy = "; ".join(f"{D.nr_iso(r['id'], r['kond'])} {r['nazwa']}" for r in rr)
        rows.append({"Kondygnacja": f"{k.nazwa} ({rzedna(float(k.rzedna))})", "Pomieszczenia": nazwy,
                     "PU [m²]": sum(r["pow_zal"] for r in rr if D.w_pu(r))})
    pab.tabela(rows, tytul="Program użytkowy według kondygnacji", suma=["PU [m²]"], klasa="zwarta",
               szerokosci=["30mm", None, "18mm"], zrodlo="model/budynek.yaml (pomieszczenia); PU wg rozdz. 4.2 (W-316)")


# ------------------------------------------------------------------------------------------ rozdz. 3
def _kolor(nazwa: str) -> tuple[str, str]:
    """(kolorystyka, kategoria palety MPZP) z nazwy materiału modelu; reguła jawna, [INT] dla przyporządkowań."""
    n = nazwa.lower()
    kod = re.findall(r"RAL \d{4}|NCS S \d{4}-[A-Z0-9]+", nazwa)
    if kod:
        k = kod[0]
        if k.startswith("RAL 7016"):
            return k + " (antracytowoszary)", "grafit " + INT
        if k.startswith("NCS") and k.endswith("-N"):
            return ("biały / " if "biał" in n else "") + k, "biele, szarości " + INT
        return k, do_uzup("przyporządkowanie do palety MPZP")
    if "drewn" in n or "dęb" in n or "termojesion" in n:
        return "naturalny kolor drewna" + (" (olejowane)" if "olejow" in n else ""), "naturalne drewno"
    if "czarn" in n:
        return "czarny", do_uzup("kolor czarny spoza palety MPZP — interpretacja: tło szczeliny za lamelami")
    if "żwir" in n:
        return "naturalny (kruszywo)", "— (pokrycie dachu)"
    if "substrat" in n or "sedum" in n:
        return "roślinność (rozchodniki)", "— (pokrycie dachu)"
    if "beton" in n or "żelbet" in n:
        return "beton naturalny", "beton architektoniczny"
    return do_uzup("kolor wg karty kolorystyki (RAL/NCS)"), do_uzup("paleta MPZP")


def wyroby_elewacji(D) -> list[dict]:
    """Wyroby wykończeniowe widoczne w elewacjach i na dachach — z modelu (przegrody, lamele, płyty, słupy, stolarka)."""
    m, uzyte = D.m, {}

    def dodaj(mat: str, kat: str, ident: str):
        mt = m.material(str(mat)) if mat else None
        if mt is not None:
            uzyte.setdefault(mat, (mt.nazwa, {}))[1].setdefault(kat, []).append(ident)
    for kod in sorted({s.przegroda_kod for s in m.sciany() if s.typ == "sciana_zewn" and s.przegroda_kod}):
        dodaj(m.przegroda(kod).warstwy[-1].mat, "ściany zewnętrzne", kod)
    for lm in m.lamele():
        if "wewn" not in str(lm.get("uwagi", "")).lower():
            dodaj(lm["mat"], "lamele", lm["id"])
    for wsp in m.wsporniki():
        p = m.przegroda(str(wsp.get("przegroda"))) if wsp.get("przegroda") else None
        dodaj(p.warstwy[-1].mat if p else wsp.get("mat"), "płyty wysunięte, okapy, obudowy", wsp["id"])
    for sl in m.slupy():
        dodaj(sl.get("mat"), "słupy", sl["id"])
    for dh in m.dachy():
        p = m.przegroda(str(dh.get("przegroda")))
        if p:
            dodaj(p.warstwy[0].mat, "pokrycie dachu", dh["id"])
    rows = []
    for mat, (nazwa, kat) in uzyte.items():
        kol, pal = _kolor(nazwa)
        el = "; ".join(f"{k}: {', '.join(v)}" for k, v in kat.items())
        rows.append({"Element": el, "Wyrób (model)": nazwa, "Kolorystyka": kol, "Paleta MPZP": pal})
    typy = sorted({str((D.B.get("stolarka") or {}).get(o.raw.get("symbol"), {}).get("wyrob", "")).split("_")[1]
                   for o in m.otwory() if o.typ in ("okno", "fix", "drzwi_przesuwne_HS")
                   and "_" in str((D.B.get("stolarka") or {}).get(o.raw.get("symbol"), {}).get("wyrob", ""))})
    rows.append({"Element": "stolarka okienna i drzwiowa zewnętrzna", "Wyrób (model)": "ramy: " + ", ".join(typy) +
                 " (model: stolarka); szyby 3-szybowe", "Kolorystyka": do_uzup("kolor ram (RAL)"),
                 "Paleta MPZP": do_uzup("paleta MPZP")})
    return rows
