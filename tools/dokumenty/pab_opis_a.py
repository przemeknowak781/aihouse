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
    lim = D.v("procedura", "uprawnienia_ograniczone_kubatura_max")
    if lim is not None and D.kubatura > lim:
        pab.akapit(f"Kubatura brutto przekracza {L(lim, 0)} m³ — projekt sporządzają projektanci z uprawnieniami do "
                   f"projektowania bez ograniczeń w odpowiednich specjalnościach ({D.zr('procedura', 'uprawnienia_ograniczone_kubatura_max')}).")


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


def mpzp_wiersze(D) -> list[dict]:
    """Zgodność z ustaleniami MPZP — wartości z ``lamela.wskazniki`` / audytu A1, limity z rejestru (sekcja mpzp)."""
    w, v = D.w, D.v
    kol_ok = all(not str(r["Paleta MPZP"]).startswith("[DO UZUP") for r in wyroby_elewacji(D))
    iz = v("mpzp", "intensywnosc_zakres", [None, None])
    rez = D.audyt.info.get("linia_zabudowy_rezerwa")
    r = [
        ("Udział powierzchni zabudowy", f"≤ {L(100 * v('mpzp', 'udzial_pow_zabudowy_max'), 0)} %",
         f"{L(100 * w['udzial_zabudowy']['wartosc'])} % (z płytami wysuniętymi {L(100 * w['udzial_zabudowy_kontrolny']['wartosc'])} %)",
         w["udzial_zabudowy"]["wartosc"] <= v("mpzp", "udzial_pow_zabudowy_max") and
         w["udzial_zabudowy_kontrolny"]["wartosc"] <= v("mpzp", "udzial_pow_zabudowy_max"), D.zr("mpzp", "udzial_pow_zabudowy_max")),
        ("Udział powierzchni biologicznie czynnej", f"≥ {L(100 * v('mpzp', 'udzial_PBC_min'), 0)} %",
         f"{L(100 * w['udzial_pbc']['wartosc'])} % (bez rezerwy dachu zielonego)",
         w["udzial_pbc"]["wartosc"] >= v("mpzp", "udzial_PBC_min"), D.zr("mpzp", "udzial_PBC_min")),
        ("Intensywność zabudowy (nadziemna)", f"{L(iz[0])}–{L(iz[1])}", L(w["intensywnosc_nadziemna"]["wartosc"], 3),
         iz[0] <= w["intensywnosc_nadziemna"]["wartosc"] <= iz[1], D.zr("mpzp", "intensywnosc_zakres")),
        ("Wysokość zabudowy", f"≤ {L(v('mpzp', 'wys_zabudowy_max'))} m", f"{L(w['wysokosc_zabudowy']['wartosc'])} m",
         w["wysokosc_zabudowy"]["wartosc"] <= v("mpzp", "wys_zabudowy_max"), D.zr("mpzp", "wys_zabudowy_max")),
        ("Liczba kondygnacji nadziemnych", f"≤ {v('mpzp', 'kondygnacje_nadziemne_max')}",
         str(w["kondygnacje_nadziemne"]["wartosc"]),
         w["kondygnacje_nadziemne"]["wartosc"] <= v("mpzp", "kondygnacje_nadziemne_max"), D.zr("mpzp", "kondygnacje_nadziemne_max")),
        ("Geometria dachu (dach płaski)", f"kąt ≤ {L(v('mpzp', 'dach_plaski_spadek_max'), 0)}°",
         f"{L(w['kat_dachu']['wartosc'], 1)}°", w["kat_dachu"]["wartosc"] <= v("mpzp", "dach_plaski_spadek_max"),
         D.zr("mpzp", "dach_plaski_spadek_max")),
        ("Miejsca postojowe", f"≥ {v('mpzp', 'miejsca_postojowe_na_lokal_min')} na lokal",
         f"{w['miejsca_postojowe']['wartosc']} (w garażu {w['miejsca_postojowe'].get('garaz')})",
         w["miejsca_postojowe"]["wartosc"] >= v("mpzp", "miejsca_postojowe_na_lokal_min"), D.zr("mpzp", "miejsca_postojowe_na_lokal_min")),
        ("Nieprzekraczalna linia zabudowy", f"{L(v('usytuowanie', 'linia_zabudowy_od_linii_rozgraniczajacej'))} m od linii "
         "rozgraniczającej drogi", f"nieprzekroczona; rezerwa {L(rez)} m" if rez is not None else do_uzup("PZT"),
         rez is not None and rez >= 0, D.zr("usytuowanie", "linia_zabudowy_od_linii_rozgraniczajacej")),
        ("Kolorystyka elewacji", ", ".join(v("mpzp", "kolorystyka_elewacji") or []), "tabela wyrobów wykończeniowych",
         kol_ok, D.zr("mpzp", "kolorystyka_elewacji")),
    ]
    return [{"Ustalenie MPZP": a, "Wartość dopuszczalna": b, "Projekt": c, "Ocena": ok(e) if e else
             ("do potwierdzenia" if a.startswith("Kolor") else ok(e)), "Podstawa": f} for a, b, c, e, f in r]


def r03(pab, D, d):
    m = D.m
    dachy = m.dachy()
    ziel = [dh["id"] for dh in dachy if "ziel" in (m.przegroda(str(dh.get("przegroda"))).nazwa.lower()
                                                   if m.przegroda(str(dh.get("przegroda"))) else "")]
    sp = sorted({float(dh.get("spadek") or 0) for dh in dachy})
    lam = sorted({lm["elewacja"] for lm in m.lamele() if "wewn" not in str(lm.get("uwagi", "")).lower()})
    rz = D.arkusze_ref("rzut") + D.arkusze_ref("dach")
    el = D.arkusze_ref("elewacja")
    pab.rozdzial(tyt("Układ przestrzenny, forma architektoniczna, wyroby wykończeniowe i kolorystyka; zgodność z MPZP", 3))
    pab.markdown(f"""
    ## Układ przestrzenny i forma architektoniczna

    Budynek tworzą {len(m.kondygnacje)} kondygnacje nadziemne o różnych obrysach — trzy poziome bryły przesunięte względem
    siebie na przemian ku zachodowi i wschodowi, co w elewacji ogrodowej (południowej) daje sylwetę „S”. Parter mieści strefę
    dzienną otwartą na ogród, część gościnną, pomieszczenia gospodarcze i garaż; I piętro — strefę dzieci i pokój rodzinny
    w przeszklonym boksie w ramie stalowej; II piętro — apartament rodziców i gabinet w bryle osłoniętej pionowymi lamelami
    drewnianymi (elewacje: {', '.join(lam) or '—'}). Poziome krawędzie wysuniętych płyt stropowych pełnią funkcję okapów
    i stałych osłon przeciwsłonecznych od południa. Dachy płaskie ze spadkiem {', '.join(L(100 * s, 1) + ' %' for s in sp)}
    ukrytym za attykami; dach nad garażem i pasem gospodarczym ({', '.join(ziel) or '—'}) — zielony ekstensywny,
    nieużytkowy. Wejście główne od strony drogi (północ) pod daszkiem, wjazd do garażu od północy. Układ funkcjonalny
    przedstawiono na rzutach ({', '.join(rz)}), formę — na elewacjach ({', '.join(el)}) i przekrojach
    ({', '.join(D.arkusze_ref('przekroj'))}).
    """)
    rows = [{"Kondygnacja": f"{v['nazwa']} ({k})", "Rzędna posadzki [m]": rzedna(v["rzedna"]),
             "Obrys zewn. dł. × szer. [m]": f"{L(v['dl'])} × {L(v['szer'])}", "Wys. kondygnacji [m]": v["h_kond"],
             "Wys. w świetle [m]": v["h_sw"]} for k, v in D.wym_kond.items()]
    pab.tabela(rows, tytul="Kondygnacje — obrysy i wysokości", wyrownanie={"Rzędna posadzki [m]": "r",
               "Obrys zewn. dł. × szer. [m]": "r"}, zrodlo="model/budynek.yaml (kondygnacje; obrys po licach ścian "
               "zewnętrznych — lamela.model.obrys_kondygnacji)")
    pab.markdown("## Wyroby wykończeniowe i kolorystyka elewacji")
    pab.tabela(wyroby_elewacji(D), tytul="Charakterystyczne wyroby wykończeniowe i kolorystyka (z modelu)", klasa="zwarta",
               szerokosci=["42mm", None, "30mm", "28mm"],
               uwagi=[f"Wyroby „lub równoważne”; kolory ram stolarki i pokrycia dachu — wg karty kolorystyki "
                      f"{do_uzup('karta kolorystyki elewacji')}. Przyporządkowanie kodów RAL/NCS do palety MPZP — {INT}."],
               zrodlo="model/budynek.yaml: materialy, przegrody, lamele, wsporniki_plyty, slupy, dachy, stolarka")
    pab.markdown(f"""
    ## Zgodność z ustaleniami miejscowego planu zagospodarowania przestrzennego

    Ustalenia MPZP dla terenu {DANE_PRZYKLADOWE} i wartości projektu (definicje: ustawa o planowaniu i zagospodarowaniu
    przestrzennym, t.j. Dz.U. 2026 poz. 538, art. 2 pkt 28–35 — obliczenia `lamela.wskazniki`; szczegóły bilansu terenu
    w opisie PZT, RPB § 14 pkt 4). Dla zamierzenia nie ustalono pozwoleń, uzgodnień ani opinii innych organów, o których
    mowa w art. 32 ust. 1 pkt 2 PB {INT}; do projektu dołącza się decyzję zarządcy drogi o lokalizacji zjazdu (PB art. 33
    ust. 2 pkt 1; u.d.p. art. 29 ust. 3a; W-020) — element „Załączniki”.
    """)
    pab.tabela(mpzp_wiersze(D), tytul="Zgodność z ustaleniami MPZP", klasa="zwarta",
               szerokosci=["36mm", "30mm", None, "18mm", "44mm"], zrodlo="lamela.wskazniki; tools/audyt_wt.py; "
               "docs/10_podstawy_prawne/wymagania.yaml (sekcja mpzp) " + DANE_PRZYKLADOWE)
