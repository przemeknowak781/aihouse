#!/usr/bin/env python3
"""Parametryczny model kosztów realizacji (UMWD) w układzie Załącznika F.14.B.

Poziom cen: II kw. 2026 (data złożenia pracy Etapu II: 10.07.2026), Wrocław, ceny NETTO
z narzutami (koszty pośrednie + zysk w cenach jednostkowych). Metoda i źródła stawek:
docs/50_research/koszty_benchmarki.md (rozdz. 4-7). Stawki oznaczone tam jako "Z" to
założenia zespołu skalibrowane do benchmarków przetargowych, NIE ceny ze źródła.

Użycie:
    python3 -I tools/koszty_model.py                 # wariant referencyjny V1, low/mid/high
    python3 -I tools/koszty_model.py wejscie.json    # parametry z modelu bryły (klucze jak w REF)
    python3 -I tools/koszty_model.py wejscie.json --rows mid   # pozycje F.14.B dla poziomu mid
"""
import json
import sys

# ---------------------------------------------------------------- wejście z modelu bryły
REF = {
    "A_nad": 14000.0,      # m2 PC nadziemna (PN-ISO 9836)
    "A_pod": 3900.0,       # m2 PC podziemna
    "fp_pod": 2900.0,      # m2 obrys podziemia (rzut płyty fundamentowej)
    "obw_pod": 220.0,      # m obwód ścian szczelinowych
    "h_wyk": 6.0,          # m średnia głębokość wykopu
    "h_sz": 15.0,          # m głębokość ścian szczelinowych (z zagłębieniem w gliny)
    "h_pod": 4.0,          # m wysokość ścian podziemia (do izolacji)
    "t_plyty": 1.1,        # m grubość płyty fundamentowej (wypór wody, dominanta)
    "fp_nad": 2500.0,      # m2 obrys parteru (powierzchnia zabudowy)
    "fp_wypor": 400.0,     # m2 część podziemia poza obrysem nadziemia (wymaga kotwienia/pali)
    "n_klatek": 3, "n_kond_klatki": 8,           # klatki ewakuacyjne i średnia liczba kondygnacji na klatkę
    "windy_os": 6, "windy_tow": 1,
    "fas_went": 3800.0,    # m2 elewacja wentylowana ceramika/klinkier (bez otworów)
    "fas_kamien": 600.0,   # m2 kamień (cokół, portal)
    "fas_tynk": 0.0,       # m2 tynk szlachetny/ETICS (np. podwórze)
    "okna": 2400.0,        # m2 okna w elewacji otworowej
    "fas_sr": 800.0,       # m2 ściany słupowo-ryglowe (hol, sala Sejmiku)
    "fas_bipv": 400.0,     # m2 BIPV elewacyjne
    # UWAGA (weryfikator 2026-11-16): kwp_dach 200 + 0,15 kWp/m2 x 400 m2 = 260 kWp < 400 kWp (minimum M.12 pkt B).
    # Zgodność z M.12 wymaga ok. 1 333 m2 BIPV (zamiennie z fas_went): V1 mid 146,3 -> 147,3 mln zł.
    "przeslony": 1200.0,   # m2 lamele / przesłony stałe
    "drzwi_zew": 120.0, "swietliki": 60.0, "klapy": 12.0, "okna_wew": 80.0,
    "dach": 2700.0,        # m2 dachy płaskie łącznie
    "dach_ext": 1200.0,    # m2 w tym zielony ekstensywny
    "dach_int": 500.0,     # m2 w tym intensywny / taras użytkowy
    "stal_kg": 60000.0,    # kg konstrukcje stalowe (przekrycie sali, zadaszenia)
    "kwp_dach": 200.0,     # kWp PV na dachach (BIPV dachowe)
    "kwh_bess": 250.0,     # kWh magazyn energii elektrycznej
    "mb_odw": 14400.0,     # mb odwiertów GPC (wynik analizy M.12)
    "A_teren": 2100.0,     # m2 zagospodarowanie (działka bez zabudowy + skwer 9/2 + pasy)
    "t_kam": 1300.0, "t_ziel": 600.0, "drogi": 250.0, "ogrodzenie": 40.0,
    "drzewa": 12, "ev": 10,
    "sciany_mobilne": 150.0, "bal_zew": 150.0, "bal_wew": 120.0,
}

# ------------------------------------------------- stawki (low, mid, high) netto II kw. 2026
# Pozycja: (lp F.14.B, opis, j.m., funkcja ilości, (low, mid, high))
def Q(p):
    A, Ap, fp = p["A_nad"], p["A_pod"], p["fp_pod"]
    stair = p["n_klatek"] * p["n_kond_klatki"]
    return [
        ("1.1", "Przygotowanie i zabezpieczenie placu budowy (ogrodzenie, wycinka)", "kpl", 1, (0.5e6, 0.8e6, 1.2e6)),
        ("1.2", "Zdjęcie humusu", "m3", 0.2 * p["A_teren"], (40, 60, 80)),
        ("1.3", "Odwodnienie wykopu (wewnątrz obudowy)", "kpl", 1, (0.4e6, 0.8e6, 1.5e6)),
        ("1.4", "Wykop pod budynek z wywozem i utylizacją nasypów", "m3", fp * p["h_wyk"], (60, 80, 110)),
        ("1.5", "Wymiana gruntów", "m3", 500, (80, 100, 130)),
        ("1.6*", "Ściany szczelinowe (obudowa wykopu = ściany zewn. garażu)", "m2", p["obw_pod"] * p["h_sz"], (1100, 1400, 1800)),
        ("1.7*", "Badania i nadzór archeologiczny (relikty piwnic kamienic)", "kpl", 1, (0.3e6, 0.6e6, 1.2e6)),
        ("1.8*", "Zabezpieczenie i monitoring budynków WS 5 i Mazowiecka 19", "kpl", 1, (0.6e6, 1.2e6, 2.5e6)),
        ("2.1", "Przyłącze ciepłownicze (źródło rezerwowe/szczytowe)", "kpl", 1, (0.3e6, 0.5e6, 0.8e6)),
        ("2.2", "Przyłącze wodociągowe", "kpl", 1, (0.15e6, 0.25e6, 0.4e6)),
        ("2.3", "Przyłącze kanalizacyjne", "kpl", 1, (0.2e6, 0.35e6, 0.6e6)),
        ("2.4", "Przyłącze energetyczne (z ew. stacją SN/nn)", "kpl", 1, (0.4e6, 0.8e6, 1.5e6)),
        ("2.5", "Przyłącze telekomunikacyjne", "kpl", 1, (0.05e6, 0.1e6, 0.2e6)),
        ("2.6", "Kanalizacja sanitarna zewn. wraz z urządzeniami", "kpl", 1, (0.15e6, 0.25e6, 0.4e6)),
        ("2.7", "Kanalizacja deszczowa zewn. wraz z urządzeniami", "kpl", 1, (0.25e6, 0.4e6, 0.6e6)),
        ("2.8", "Instalacja wodociągowa zewn.", "kpl", 1, (0.08e6, 0.15e6, 0.25e6)),
        ("2.9", "Instalacja ciepłownicza zewn.", "kpl", 1, (0.08e6, 0.15e6, 0.25e6)),
        ("2.10", "Instalacja elektryczna zewn.", "kpl", 1, (0.15e6, 0.25e6, 0.4e6)),
        ("2.11", "Rezerwowe źródło wody", "kpl", 1, (0.1e6, 0.2e6, 0.35e6)),
        ("2.12a", "GPC: pole odwiertów pionowych z sondami", "mb", p["mb_odw"], (190, 240, 300)),
        ("2.12b", "GPC: pompy ciepła, maszynownia, hydraulika źródła", "kpl", 1, (1.8e6, 2.5e6, 3.5e6)),
        ("2.13", "PV dachowe (BIPV dachu dominanty)", "kWp", p["kwp_dach"], (3500, 4000, 5000)),
        ("3.1", "Płyta fundamentowa", "m3", fp * p["t_plyty"], (1200, 1400, 1650)),
        ("3.2", "Izolacja termiczna i przeciwwodna garażu (detale białej wanny)", "m2", fp + p["obw_pod"] * p["h_pod"], (120, 180, 260)),
        ("3.3", "Ściany żelbetowe (rdzenie, ściany wewn., okładzinowe)", "m2", 0.30 * (A + Ap), (450, 550, 700)),
        ("3.4", "Słupy żelbetowe", "m3", 0.022 * (A + Ap), (2600, 3100, 3800)),
        ("3.5", "Ściany murowane", "m2", 0.15 * A, (180, 230, 300)),
        ("3.6", "Stropy żelbetowe nadziemia", "m2", A - p["fp_nad"], (380, 450, 560)),
        ("3.6b", "Stropy podziemia (w tym strop nad garażem z obciążeniem terenu)", "m2", Ap, (520, 620, 760)),
        ("3.7", "Stropodach (konstrukcja)", "m2", p["dach"], (380, 450, 560)),
        ("3.8", "Schody prefabrykowane + spoczniki", "kpl", stair + p["A_pod"] / fp, (25e3, 35e3, 50e3)),
        ("3.9", "Konstrukcje stalowe", "kg", p["stal_kg"], (12, 15, 20)),
        ("3.10", "Ocieplenia ścian i sufitów wewn. (strop nad garażem)", "m2", fp, (120, 160, 220)),
        ("3.11", "Izolacje termiczne i przeciwwodne dachu", "m2", p["dach"] - p["dach_ext"] - p["dach_int"], (350, 450, 600)),
        ("3.12", "Dach zielony ekstensywny (z izolacjami)", "m2", p["dach_ext"], (550, 700, 900)),
        ("3.13*", "Dach intensywny / taras użytkowy (z izolacjami)", "m2", p["dach_int"], (900, 1200, 1600)),
        ("3.14*", "Rampa zjazdowa i konstrukcje dodatkowe podziemia", "kpl", 1, (0.5e6, 0.8e6, 1.2e6)),
        ("3.15*", "Zabezpieczenie przed wyporem (pale/kotwy) poza obrysem nadziemia", "m2", p["fp_wypor"], (400, 600, 900)),
        ("4.1", "Stolarka okienna zewn. (alu, 3-szybowa)", "m2", p["okna"], (1500, 1800, 2200)),
        ("4.2", "Stolarka drzwiowa zewn. (wejścia automatyczne)", "m2", p["drzwi_zew"], (2500, 3500, 5000)),
        ("4.3", "Świetliki dachowe", "m2", p["swietliki"], (2500, 3500, 4500)),
        ("4.4", "Klapy dymowe", "m2", p["klapy"], (4000, 5500, 7000)),
        ("4.5*", "Ściany słupowo-ryglowe (hol, sala Sejmiku)", "m2", p["fas_sr"], (2300, 2800, 3500)),
        ("5.1", "Drzwi wewnętrzne", "szt", A / 28, (1800, 2500, 3500)),
        ("5.2", "Stolarka drzwiowa przeciwpożarowa", "szt", 3 * stair + Ap / 150, (3500, 5000, 7000)),
        ("5.3", "Stolarka okienna wewnętrzna", "m2", p["okna_wew"], (900, 1200, 1600)),
        ("6.1", "Elewacja wentylowana z okładziną ceramiczną/klinkierową", "m2", p["fas_went"], (1150, 1450, 1800)),
        ("6.2", "Izolacja termiczna + tynk elewacyjny", "m2", p["fas_tynk"], (280, 350, 450)),
        ("6.3", "Stałe przesłony światła, lamele", "m2", p["przeslony"], (500, 800, 1200)),
        ("6.4*", "Okładzina kamienna (granit) na kotwach, z izolacją", "m2", p["fas_kamien"], (1600, 2000, 2600)),
        ("6.5*", "Elewacja BIPV (moduły szkło-szkło z podkonstrukcją)", "m2", p["fas_bipv"], (1900, 2400, 3000)),
        ("7.1", "Instalacje wody wodociągowej i szarej", "m2PC", A + Ap, (90, 110, 140)),
        ("7.2", "Instalacje ppoż (hydranty, zawory)", "m2PC", A + Ap, (45, 60, 85)),
        ("7.3", "Kanalizacja ścieków czarnych i szarych", "m2PC", A + Ap, (70, 90, 120)),
        ("7.4", "Instalacje CO (wodne niskotemperaturowe)", "m2PC", A, (210, 260, 330)),
        ("7.5", "Węzeł cieplny (rezerwa z sieci)", "kpl", 1, (0.25e6, 0.4e6, 0.6e6)),
        ("7.6", "Wentylacja mechaniczna z centralami (odzysk ciepła)", "m2PC", A, (330, 400, 500)),
        ("7.6b", "Wentylacja garażu i oddymianie podziemia", "m2PC", Ap, (200, 260, 340)),
        ("7.7", "Instalacja chłodnicza (TABS / klimakonwektory)", "m2PC", A, (230, 280, 360)),
        ("7.8", "Rozdział ciepła i chłodu z pomp ciepła", "kpl", 1, (0.6e6, 0.9e6, 1.3e6)),
        ("7.9", "Magazyny energii cieplnej (bufory)", "kpl", 1, (0.3e6, 0.5e6, 0.8e6)),
        ("8.1-8.10", "Instalacje elektryczne podstawowe (tablice, trasy, oświetlenie, gniazda, siła, odgrom)", "m2PC", A + 0.6 * Ap, (430, 520, 650)),
        ("8.11", "Serwerownia", "kpl", 1, (0.5e6, 0.8e6, 1.3e6)),
        ("8.12", "System SMS", "kpl", 1, (0.1e6, 0.2e6, 0.3e6)),
        ("8.13", "System BMS/EMS", "kpl", 1, (0.6e6, 1.0e6, 1.5e6)),
        ("8.14", "Wzmocnienie sygnału GSM", "kpl", 1, (0.1e6, 0.2e6, 0.3e6)),
        ("8.15", "Agregat prądotwórczy", "kpl", 1, (0.5e6, 0.7e6, 1.0e6)),
        ("8.16", "UPS", "kpl", 1, (0.2e6, 0.35e6, 0.5e6)),
        ("8.17", "Magazyn energii elektrycznej (PV)", "kWh", p["kwh_bess"], (1600, 2200, 3000)),
        ("9.1-9.9", "Teletechnika (LAN, KD, SSWiN, CCTV, przyzywowa, SSP, DSO, światłowód, tel.)", "m2PC", A + 0.5 * Ap, (280, 345, 440)),
        ("9.10", "Instalacja AV: sala Sejmiku (głosowanie, transmisja, PJM, pętle) + centrum konferencyjne", "kpl", 1, (2.5e6, 4.0e6, 6.0e6)),
        ("9.11", "System integrujący i wizualizacyjny", "kpl", 1, (0.3e6, 0.5e6, 0.8e6)),
        ("9.12", "Oddymianie i napowietrzanie klatek", "kpl", p["n_klatek"], (0.25e6, 0.35e6, 0.5e6)),
        ("10.1", "Windy osobowe (w tym dla ekip ratowniczych)", "szt", p["windy_os"], (0.45e6, 0.6e6, 0.8e6)),
        ("10.2", "Winda towarowa / osobowo-towarowa", "szt", p["windy_tow"], (0.6e6, 0.8e6, 1.0e6)),
        ("11.1", "Tynki / gładzie", "m2", 1.2 * A, (35, 45, 60)),
        ("11.2", "Ścianki działowe GK (akustyczne)", "m2", 0.85 * A, (160, 200, 260)),
        ("11.3", "Ścianki działowe HPL (kabiny WC)", "m2", 300, (500, 650, 850)),
        ("11.4", "Ścianki mobilne (sala 200 os., sale narad)", "m2", p["sciany_mobilne"], (1500, 2000, 2800)),
        ("11.5", "Ścianki działowe szklane", "m2", 0.10 * A, (900, 1200, 1600)),
        ("11.6", "Płytki ceramiczne ścienne", "m2", 0.12 * A, (200, 260, 340)),
        ("11.7", "Roboty malarskie", "m2", 2.5 * A + 2.0 * Ap, (18, 24, 32)),
        ("11.8", "Okładziny ścienne (drewno akustyczne, kamień w holach)", "m2", 0.06 * A, (700, 1000, 1500)),
        ("11.9", "Wyposażenie stałe (recepcje, kancelaria, zabudowy, SIW, tyflomapy)", "kpl", 1, (1.2e6, 2.0e6, 3.0e6)),
        ("11.10*", "Sala Sejmiku: amfiteatr, stanowiska stałe, akustyka", "kpl", 1, (1.2e6, 2.0e6, 3.0e6)),
        ("12.1", "Sufit podwieszany modułowy", "m2", 0.55 * A, (140, 180, 240)),
        ("12.2", "Sufit pełny GK", "m2", 0.20 * A, (120, 150, 200)),
        ("12.3", "Sufit akustyczny (sale, hole)", "m2", 0.12 * A, (300, 420, 600)),
        ("13.1", "Warstwy podposadzkowe (izolacje + wylewki)", "m2", 0.92 * A, (90, 120, 160)),
        ("13.2", "Płytki ceramiczne klatek schodowych", "m2", 30 * stair, (180, 230, 300)),
        ("13.3", "Płytki ceramiczne / PCV antypoślizgowe (WC, socjalne)", "m2", 0.10 * A, (160, 210, 280)),
        ("13.4", "Posadzka żywiczna (pom. techniczne)", "m2", 0.15 * Ap, (120, 160, 220)),
        ("13.5", "Posadzka żywiczna - garaż podziemny", "m2", 0.75 * Ap, (110, 150, 200)),
        ("13.6", "Wykładzina (PCV / dywanowa)", "m2", 0.55 * A, (110, 150, 200)),
        ("13.8*", "Posadzki kamienne / lastryko w holach", "m2", 0.06 * A, (600, 850, 1200)),
        ("14.1", "Balustrada schodowa na klatkach", "mb", 14 * stair, (700, 900, 1200)),
        ("14.2", "Pochwyt ścienny (klatki)", "mb", 11 * stair, (150, 200, 280)),
        ("14.3", "Balustrada zewnętrzna (tarasy)", "mb", p["bal_zew"], (1200, 1600, 2200)),
        ("14.4", "Balustrada wewnętrzna (galerie, antresola)", "mb", p["bal_wew"], (1500, 2000, 2800)),
        ("15.1", "Roboty ziemne (teren)", "m2", p["A_teren"], (30, 45, 60)),
        ("15.2", "Drogi wewnętrzne (dojazd, wjazd do garażu)", "m2", p["drogi"], (350, 450, 600)),
        ("15.4", "Chodniki, place - nawierzchnie z kamienia naturalnego", "m2", p["t_kam"], (700, 900, 1200)),
        ("15.5", "Ogrodzenie, bramy, furtki", "mb", p["ogrodzenie"], (800, 1200, 1800)),
        ("15.6", "Mała architektura (ławki, kosze, stojaki rowerowe)", "kpl", 1, (0.3e6, 0.5e6, 0.8e6)),
        ("15.7a", "Zieleń niska (w tym na stropie garażu)", "m2", p["t_ziel"], (350, 500, 800)),
        ("15.7b", "Zieleń wysoka - drzewa duże z systemem korzeniowym", "szt", p["drzewa"], (10e3, 18e3, 30e3)),
        ("15.8", "Oświetlenie terenów zewnętrznych", "kpl", 1, (0.25e6, 0.4e6, 0.7e6)),
        ("15.9", "Stacje ładowania pojazdów elektrycznych", "szt", p["ev"], (25e3, 35e3, 50e3)),
        ("15.10", "System retencji wód opadowych (zbiorniki)", "kpl", 1, (0.5e6, 0.8e6, 1.2e6)),
        ("17.2*", "Stacja podczyszczania wody szarej (spłukiwanie WC)", "kpl", 1, (0.3e6, 0.5e6, 0.8e6)),
        ("17.3*", "Odzysk ciepła z wody szarej", "kpl", 1, (0.1e6, 0.2e6, 0.3e6)),
        ("18.1*", "Adaptacja garażu na MDS (wyposażenie, wentylacja, sanitariaty)", "kpl", 1, (0.8e6, 1.5e6, 2.5e6)),
        ("18.2*", "Zamurowanie okien w szczycie Mazowiecka 19 z wentylacją", "kpl", 1, (0.1e6, 0.2e6, 0.4e6)),
    ]

KS = (0.02, 0.03, 0.04)       # 16.1 koszty stałe budowy (zaplecze, żurawie, ochrona, media, CAR) - Z
REZ = (0.03, 0.05, 0.07)      # 18.3* rezerwa na nieprzewidziane - Z
LEVELS = {"low": 0, "mid": 1, "high": 2}


def compute(p, level="mid"):
    i = LEVELS[level]
    rows = [(lp, op, jm, q, r[i], q * r[i]) for lp, op, jm, q, r in Q(p)]
    works = sum(x[5] for x in rows)
    ks = works * KS[i]
    rows.append(("16.1", "Koszty stałe budowy", "kpl", 1, ks, ks))
    rez = (works + ks) * REZ[i]
    rows.append(("18.3*", "Rezerwa na nieprzewidziane", "kpl", 1, rez, rez))
    total = works + ks + rez
    groups = {}
    for r in rows:
        g = int(r[0].split(".")[0])
        groups[g] = groups.get(g, 0) + r[5]
    return {"rows": rows, "works": works, "ks": ks, "rez": rez, "total": total, "groups": groups,
            "zl_m2_PC": total / (p["A_nad"] + p["A_pod"])}


def escalate(value, years, rate):
    """Waloryzacja od II kw. 2026: value * (1+rate)**years."""
    return value * (1 + rate) ** years


def main(argv):
    p = dict(REF)
    if len(argv) > 1 and argv[1].endswith(".json"):
        with open(argv[1], encoding="utf-8") as f:
            p.update(json.load(f))
    if "--rows" in argv:
        lvl = argv[argv.index("--rows") + 1]
        res = compute(p, lvl)
        print("| L.p. | Opis | Ilość | J.m. | Cena jedn. netto | Wartość netto |")
        print("|---|---|---:|---|---:|---:|")
        for lp, op, jm, q, c, v in res["rows"]:
            n = lambda x: f"{x:,.0f}".replace(",", " ")
            print(f"| {lp} | {op} | {n(q)} | {jm} | {n(c)} | {n(v)} |")
        return
    for lvl in LEVELS:
        r = compute(p, lvl)
        print(f"{lvl:4s}: roboty {r['works']/1e6:6.1f} | +KS {r['ks']/1e6:4.1f} | +rezerwa {r['rez']/1e6:4.1f} | "
              f"RAZEM {r['total']/1e6:6.1f} mln zł netto | {r['zl_m2_PC']:,.0f} zł/m2 PC | "
              f"2027 (+5%): {escalate(r['total'], 1, 0.05)/1e6:6.1f}")
    g = compute(p, "mid")["groups"]
    print("grupy F.14.B (mid, mln):", {k: round(v / 1e6, 2) for k, v in sorted(g.items())})


if __name__ == "__main__":
    main(sys.argv)
