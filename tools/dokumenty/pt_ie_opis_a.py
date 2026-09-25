"""PT-4 IE — część opisowa A: stan opracowania, podstawy, powiązanie z siecią i zasilanie (§ 23 pkt 8 RPB),
instalacje elektroenergetyczne (§ 23 pkt 7 lit. g), fotowoltaika, punkt ładowania EV, instalacje telekomunikacyjne
(§ 23 pkt 7 lit. h), ochrona odgromowa i uziemienia (§ 23 pkt 7 lit. i). Liczby wyłącznie z ``DanePTIE``."""
from __future__ import annotations

import math

from pt_ie_dane import MODULY, NAZWY_MOD, L, DanePTIE, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


def _pl(n: int, j: str, d: str, m: str) -> str:
    return j if n == 1 else d if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14 else m


def rozdz_stan(o: Opis, D: DanePTIE):
    """1. Stan opracowania — wynik sprawdzeń obliczeniowych i sprawy otwarte."""
    o.rozdzial("Stan opracowania i sprawy otwarte", podstawa="rejestr wymagań, sekcja E")
    wiersze = []
    for k in MODULY:
        w = D.warunki(k)
        wiersze.append({"Obszar obliczeń": NAZWY_MOD[k], "Warunków": len(w),
                        "Spełnione": sum(1 for x in w if x.ok is True),
                        "Niespełnione": sum(1 for x in w if x.ok is False),
                        "Informacyjne": sum(1 for x in w if x.ok is None)})
    o.tekst(f"""
    Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z {D.t_modelu}) i bibliotek obliczeniowych
    `lamela.obliczenia` (moduły `elektryka`, `energia`, `sanitarne`) uruchamianych przy każdym generowaniu tomu —
    każda liczba w tomie pochodzi z modelu albo z obliczeń. Działka, MPZP, warunki gruntowe i **warunki przyłączenia
    do sieci** są {FIKCJA}; parametry urządzeń przyjęto z kart **wyrobów przykładowych** ([ZAŁ]) — dopuszcza się
    wyroby równoważne spełniające parametry wymagane podane w rozdziale „Wyroby i parametry wymagane”.
    """)
    o.tabela(wiersze, tytul="Wynik sprawdzeń obliczeniowych PT-4 IE",
             uwagi="Warunki informacyjne — wartości podawane bez kryterium (np. moc szczytowa bez zarządzania mocą).",
             zrodlo="lamela.obliczenia.elektryka — uruchomienie przy generowaniu tomu")
    if D.propozycje:
        o.tabela([{"Warunek niespełniony": p["warunek"], "Wynik": f"{L(p['wartosc'], 2)} {p['jedn']}",
                   "Wymaganie": f"≤ {L(p['limit'], 2)} {p['jedn']}", "Rozwiązanie": p["rozwiazanie"],
                   "Wynik po zmianie": f"≈ {L(p['wartosc_po'], 2)} {p['jedn']}"} for p in D.propozycje],
                 tytul="Warunki niespełnione i rozwiązania wyznaczone z wyników obliczeń",
                 uwagi="Spadek napięcia przeliczono proporcjonalnie do przekroju żył (∆U ∝ 1/s; reaktancja pominięta). "
                       "Rozwiązanie należy wprowadzić do danych obliczeń i przeliczyć tom wraz z arkuszami; tom "
                       "z niespełnionym warunkiem nie nadaje się do wydania.")
    if D.otwarte:
        o.tekst("**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status "
                "aktualizuje się przy ponownym generowaniu):\n\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(D.otwarte, 1)))
    else:
        o.tekst("Brak spraw otwartych wykrytych przez kontrole spójności modelu, obliczeń i rysunków.")
    if D.z_cache:
        o.wniosek("PODGLĄD — obliczenia odczytane z pamięci podręcznej; wersja nie do wydania.", alarm=True)


def rozdz_podstawy(o: Opis, D: DanePTIE, d: dict):
    """2. Przedmiot, zakres i podstawy opracowania."""
    o.rozdzial("Przedmiot, zakres i podstawy opracowania", podstawa="§ 23 RPB", nowa_strona=True)
    o.tekst(f"""
    **Przedmiot.** Projekt techniczny instalacji elektrycznych budynku mieszkalnego jednorodzinnego
    „{d.get('nazwa_krotka', 'Dom LAMELA')}” — {d.get('lokalizacja') or d.get('adres', '')}: zasilanie z sieci nN
    (złącze kablowo-pomiarowe, wewnętrzna linia zasilająca), rozdzielnica główna, instalacje oświetlenia, gniazd
    wtyczkowych i zasilania urządzeń (w tym pompy ciepła, centrali wentylacyjnej, punktu ładowania pojazdu
    elektrycznego), mikroinstalacja fotowoltaiczna, ochrona przeciwporażeniowa i przeciwprzepięciowa, uziemienia
    i połączenia wyrównawcze, ocena ryzyka piorunowego, instalacje telekomunikacyjne (przyłącze światłowodowe,
    okablowanie strukturalne, RTV/SAT, SSWiN, wideodomofon), przeciwpożarowy wyłącznik prądu, bilans mocy.

    **Autorzy i specjalności.** Tom obejmuje dwie specjalności uprawnień budowlanych: instalacyjną w zakresie
    sieci, instalacji i urządzeń elektrycznych i elektroenergetycznych (PB art. 15a ust. 22) — wszystkie rozdziały
    i arkusze z wyjątkiem wymienionych dalej; instalacyjną
    w zakresie sieci, instalacji i urządzeń telekomunikacyjnych (PB art. 15a ust. 18 — telekomunikacja przewodowa
    wraz z infrastrukturą telekomunikacyjną) — rozdz. „Instalacje telekomunikacyjne” i arkusze
    {D.arkusze_nr('teletechnika')}. Współautorów z zakresem opracowania wymieniono na stronie tytułowej
    i w oświadczeniu projektanta (PB art. 34 ust. 3e). Tom obejmujący więcej niż jedną specjalność ma w nazwie pliku
    symbol **WB** (zał. 1 RPB); oznaczenie tomu w odesłaniach innych tomów: PT-4.

    **Zakres wg RPB (rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, Dz.U. 2020
    poz. 1609, t.j. Dz.U. 2022 poz. 1679 ze zm.):**

    * § 23 pkt 7 lit. g — instalacje elektroenergetyczne; lit. h — instalacje telekomunikacyjne (W-196);
      lit. i — instalacja piorunochronna (analiza ryzyka, W-191); lit. j (instalacje ochrony przeciwpożarowej) —
      nie dotyczy: budynek ZL IV bez instalacji i urządzeń ppoż. wymaganych przepisami (PWP i czujki dymu — rozdz.
      „Dane dotyczące warunków ochrony przeciwpożarowej”); lit. a–f — tom PT-3 IS;
    * § 23 pkt 8 — powiązanie instalacji z siecią elektroenergetyczną i telekomunikacyjną wraz z punktami
      pomiarowymi, założenia i wyniki obliczeń, dobór urządzeń; lit. b — moc elektryczna urządzeń ogrzewczych
      i wentylacyjnych;
    * § 23 pkt 10 — dane dotyczące warunków ochrony przeciwpożarowej stosownie do zakresu tomu;
    * § 23 pkt 11 lit. a — bilans mocy urządzeń elektrycznych stanowiących stałe wyposażenie budynku (bez urządzeń
      technologicznych — budynek mieszkalny); lit. b–d — tom PT-3 IS (charakterystyka energetyczna);
    * § 23 pkt 1–5 i 9 — nie dotyczy tomu (konstrukcja, geotechnika, przegrody, urządzenia instalacji sanitarnych —
      PT-1 AR, PT-2 BO, PT-3 IS); § 23 pkt 4a — nie dotyczy (W-231); § 23 pkt 6 — nie dotyczy (budynek
      mieszkalny, nie obiekt liniowy);
    * § 23 pkt 12 (dodany Dz.U. 2026 poz. 597 § 1 pkt 6) — nie dotyczy: PZT i PAB nie przewidują budowli
      ochronnej ani miejsca doraźnego schronienia (PAB § 20 ust. 1 pkt 14 — n/d);
    * § 24 pkt 4 lit. b — rzuty instalacji elektroenergetycznych, telekomunikacyjnych i piorunochronnej, schemat
      rozdzielnicy głównej, uziom i połączenia wyrównawcze (część rysunkowa).

    **Podstawy prawne (rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`, sekcja A.2).**
    Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.); § 180–§ 192 rozporządzenia MI z 12.04.2002 w sprawie
    warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (WT; t.j. Dz.U. 2022 poz. 1225 ze zm.),
    stosowanego na podstawie art. 102a ust. 1 i 2 PB w związku z oświadczeniem Inwestora z dnia
    [DO UZUPEŁNIENIA: data oświadczenia Inwestora (art. 102a PB)]; rozporządzenie MSWiA w sprawie ochrony
    przeciwpożarowej budynków (ROPoż; t.j. Dz.U. 2023 poz. 822, zm. Dz.U. 2024 poz. 1716); Prawo energetyczne
    (t.j. Dz.U. 2026 poz. 43 ze zm.), ustawa o OZE (t.j. Dz.U. 2026 poz. 68), rozporządzenie systemowe (RSys;
    t.j. Dz.U. 2025 poz. 919 ze zm.); ustawa o elektromobilności (t.j. Dz.U. 2026 poz. 1243); rozporządzenia (UE)
    2024/1309 (art. 10 — infrastruktura światłowodowa), 2016/631 (NC RfG), dyrektywa (UE) 2024/1275 (EPBD,
    nietransponowana — stosowana dobrowolnie).

    **Normy (sekcja A.3 rejestru).** PN-HD 60364-1:2010; -4-41:2017-09; -4-42:2011; -4-43:2024-04; -4-443:2016-03;
    -5-52:2011; -5-53:2022-10; -5-54:2011; -6:2016-07; -7-701:2025-02; -7-712:2016-05; -7-714:2012; -7-722:2019-01;
    PN-EN 62305-1…-4:2008/2011/2012 (wycofane; wydania powołane w zał. 1 WT — stosowane) i PN-EN IEC
    62305-1…-4:2025-09 (aktualne, wersja angielska — rozdz. „Ocena ryzyka piorunowego”); PN-EN 12464-1:2012
    (natężenie oświetlenia; wydanie powołane w zał. 1 WT lp. 41); PN-EN IEC 61643-11:2026-04;
    PN-EN 62446-1:2016-08; PN-EN 50549-1:2019-02; PN-EN 50618:2015-03; PN-EN 50173-4:2018-07; PN-EN 50174-2:2018-08;
    PN-EN 50310:2016-09; PN-EN 14604:2006; PN-EN IEC 61439-3:2025-09; PN-EN 61082-1:2015-03. Normy wycofane
    przywoływane wyłącznie z podaniem statusu: PN-HD 60364-5-534:2012/2016-04 (zastąpiona przez PN-HD
    60364-5-53:2022-10 — dobór SPD wg wydania aktualnego), PN-86/E-05003/01 (źródło historycznej mapy N_G —
    dane informacyjne). Wartości tablicowe
    z literatury (obciążalności wg PN-HD 60364-5-52 zał. B, spadki napięć wg N SEP-E-002) oznaczono w obliczeniach
    [NZW] — do potwierdzenia z tekstem norm przed wydaniem do realizacji (D-19).

    **Materiały wyjściowe:** PZT i PAB (tom I), PT-1 AR, PT-2 BO (zbrojenie i uziom), PT-3 IS (moc pompy ciepła,
    centrali, grzałki; charakterystyka energetyczna), model `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`,
    `wyposazenie.yaml` (stan z {D.t_modelu}); dane PVGIS 5.3 (JRC) dla Poznania. Warunki przyłączenia OSD — {FIKCJA}
    (moc przyłączeniowa i parametry sieci jako [ZAŁ], E-05).
    """)


def _pom(D: DanePTIE, xyk) -> str:
    try:
        p = D.W["dane"].pom_w_punkcie(xyk[2], (xyk[0], xyk[1]))
        return f"{p.id} {p.nazwa}" if p else "—"
    except Exception:                                           # noqa: BLE001 — opis pomocniczy
        return "—"


def rozdz_zasilanie(o: Opis, D: DanePTIE):
    """3. Zasilanie i powiązanie z siecią elektroenergetyczną (§ 23 pkt 8)."""
    b, w, par = D.bil, D.obw.wlz, D.obw.par
    en, zkp = D.uzbrojenie("en"), D.obiekt("ZKP")
    rg = D.W["dane"].lok("RG") or D.obw.rg_xy
    o.rozdzial("Zasilanie i powiązanie z siecią elektroenergetyczną", podstawa="§ 23 pkt 8 RPB; W-192, W-193",
               nowa_strona=True)
    o.tekst(f"""
    **Źródło zasilania.** Sieć nN 0,4 kV operatora systemu dystrybucyjnego (układ TN-C) — kabel w ulicy wg PZT.
    Przyłącze kablowe i złącze kablowo-pomiarowe (ZKP) wykonuje OSD na podstawie warunków przyłączenia
    [DO UZUPEŁNIENIA: nr i data warunków przyłączenia OSD]. ZKP: {zkp.get('opis', '—')}.
    Pole odczytowe licznika ≥ 0,48 m nad terenem (W-192).

    **Parametry przyłączenia [ZAŁ — do potwierdzenia w warunkach przyłączenia, {FIKCJA}]:** moc przyłączeniowa
    **{L(b.P_przyl, 0)} kW**, zabezpieczenie przedlicznikowe **{par.zab_przedlicznikowe}{L(b.I_zab, 0)}**
    (3-fazowe), grupa przyłączeniowa V (≤ 1 kV, ≤ 40 kW — RSys § 3 ust. 1 pkt 5), pomiar bezpośredni, licznik
    3-fazowy dwukierunkowy (mikroinstalacja PV — zgłoszenie do OSD, W-194); impedancja pętli zwarcia w ZKP
    Z_Q = {L(par.Z_Q, 2)} Ω, prąd zwarciowy w ZKP ≤ {L(par.I_k_ZKP_max, 0)} kA.

    **Wewnętrzna linia zasilająca (WLZ)** ZKP → RG: kabel **{w['przewod']}** 0,6/1 kV, długość obliczeniowa
    L = {L(w['L'], 1)} m (trasa w terenie wg PZT {L(en.get('dl'), 1)} m + podejście w budynku i zapasy), obciążalność
    I_z = {L(w['I_z'], 1)} A (metoda {w['metoda']}), spadek napięcia przy prądzie zabezpieczenia przedlicznikowego
    ∆U = {L(w['dU'], 2)} % (temperatura robocza). Kabel w ziemi na głębokości ≥ 0,7 m w piasku z taśmą ostrzegawczą
    niebieską, pod utwardzeniami i przy wejściu do budynku w rurze osłonowej; przejście przez ścianę/płytę poniżej
    terenu gazoszczelne (W-214). Trasa w terenie: {D.trasa_wlz()}.

    **Układ sieci w budynku: TN-S** — oddzielne przewody ochronny PE i neutralny N w obwodach rozdzielczych
    i odbiorczych (WT § 183 ust. 1 pkt 2). Rozdział PEN — preferowany w ZKP z WLZ 5-żyłowym (wymaga zgody OSD);
    wariant zapasowy: WLZ 4-żyłowy (PEN) i rozdział w RG na głównej szynie uziemiającej (D-12, W-193).
    Punkt rozdziału PEN uziemić (połączenie z GSU i uziomem).

    **Rozdzielnica główna RG** — {_pom(D, rg)} (współrzędne w modelu: {L(rg[0], 2)}; {L(rg[1], 2)}; {rg[2]}),
    obudowa wg PN-EN IEC 61439-3, stopień ochrony ≥ IP40 (pomieszczenie suche), rezerwa miejsca ≥
    {L(100 * par.rezerwa, 0)} % modułów. Aparat główny: rozłącznik izolacyjny 3P z wyzwalaczem przeciwpożarowego
    wyłącznika prądu (PWP); ochronniki przepięć typu 1+2 (T1+T2) na wejściu; zabezpieczenia obwodów odbiorczych —
    wyłączniki nadprądowo-różnicowoprądowe (RCBO) i wyłączniki nadprądowe z RCD (obwody 3-fazowe).
    """)


def _skrot(t: str, n: int = 70) -> str:
    return t if len(t) <= n else t[:n - 1].rstrip(" ,:;") + "…"


def rozdz_elektroenergetyczne(o: Opis, D: DanePTIE):
    """4. Instalacje elektroenergetyczne (§ 23 pkt 7 lit. g)."""
    ob = D.obw.obwody
    o.rozdzial("Instalacje elektroenergetyczne", podstawa="§ 23 pkt 7 lit. g RPB; WT § 180–§ 192; W-180…W-190",
               nowa_strona=True)
    n = {g: len(D.obwody_grupy(*g.split("|"))) for g in ("oswietlenie", "gniazda|zewn", "gniazda_kuchnia",
                                                            "gniazda_lazienka")}
    n_d = sum(1 for x in ob if x.odb.id.startswith("D"))
    o.tekst(f"""
    Instalację podzielono na **{len(ob)} obwodów odbiorczych** wydzielonych zgodnie z WT § 188 ust. 2:
    oświetlenie — {n['oswietlenie']}, gniazda ogólnego przeznaczenia (w tym garaż i gniazda zewnętrzne) —
    {n['gniazda|zewn']}, gniazda kuchenne — {n['gniazda_kuchnia']}, gniazda w łazienkach — {n['gniazda_lazienka']},
    odbiorniki wymagające indywidualnego zabezpieczenia — {n_d}. Przyporządkowanie obwodów do faz wyrównuje obciążenie
    (asymetria mocy szczytowej {L(100 * D.bil.asymetria, 1)} %). Zestawienie obwodów — tabela poniżej; pełne
    obliczenia (I_B, I_z, ∆U, Z_s, I_k1) — rozdz. „Obliczenia”; schemat — arkusz {D.arkusze_nr('schemat')}.
    """)
    o.tabela([{"Obw.": x.odb.id, "Przeznaczenie": _skrot(x.odb.nazwa), "Faza": x.odb.faza,
               "P [kW]": x.odb.P, "Zabezp.": x.zab, "Ochrona różnicowoprądowa": x.odb.rcd, "Przewód": x.przewod,
               "L [m]": x.L, "∆U_c [%]": x.dU_calk} for x in ob],
             tytul="Obwody odbiorcze rozdzielnicy głównej RG",
             formaty={"P [kW]": 2, "L [m]": 1, "∆U_c [%]": 2},
             uwagi="∆U_c — spadek napięcia od ZKP do najdalszego odbiornika obwodu (WLZ + obwód), temperatura robocza żył.",
             zrodlo="lamela.obliczenia.elektryka.obwody (obwody z modelu: pomieszczenia, wyposażenie, instalacje.yaml)")
    lazienki = [x.odb.nazwa.split("(", 1)[-1].rstrip(")") for x in D.obwody_grupy("gniazda_lazienka")]
    urz = [x for x in ob if x.odb.grupa in ("pc", "grzalka", "went", "sterowanie", "pompa", "napedy", "agd",
                                             "gotowanie", "tele", "ev", "pv")]
    o.rozdzial("Oświetlenie", poziom=2, podstawa="WT § 64, § 102, § 188 ust. 2, § 189; W-183")
    o.tekst(f"""
    Obwody oświetleniowe: {', '.join(f'{x.odb.id} — {x.odb.nazwa} ({x.zab}, {x.przewod})' for x in D.obwody_grupy('oswietlenie'))}.
    Oprawy LED (moc obliczeniowa wg wskaźnika z obliczeń bilansu), w pomieszczeniach mieszkalnych łączniki
    wieloobwodowe; w pokoju o powierzchni do 20 m² co najmniej jeden wypust oświetleniowy, w większym — co najmniej
    dwa (W-183). Oświetlenie zewnętrzne wejścia do budynku (WT § 64) i oświetlenie garażu (WT § 102) na obwodach
    wydzielonych; oprawy zewnętrzne ≥ IP44 (PN-HD 60364-7-714). Obwody oświetleniowe chronione RCD 30 mA
    (PN-HD 60364-4-41:2017-09 p. 411.3.4 — lokal jednego gospodarstwa domowego). Rozmieszczenie — arkusze
    {D.arkusze_nr('oświetlenia')}.
    """)
    o.rozdzial("Gniazda wtyczkowe, łazienki", poziom=2, podstawa="WT § 188 ust. 2; PN-HD 60364-7-701:2025-02; W-181, W-189")
    o.tekst(f"""
    Gniazda wtyczkowe 16 A z bolcem ochronnym, w obwodach 16 A (przekroje 2,5–4 mm² dobrane z warunku spadku
    napięcia), każdy obwód z RCD I_∆n = 30 mA typu A (typ AC niedopuszczalny, W-181). Gniazda kuchenne — dwa obwody
    wydzielone; gniazda zewnętrzne i w garażu ≥ IP44. Łazienki ({'; '.join(lazienki)}) — obwody wydzielone;
    osprzęt w strefach 1–2 co najmniej IPX4, bez gniazd i łączników w strefach 0–2 (wymiary stref wg
    PN-HD 60364-7-701:2025-02; W-189); miejscowe połączenia wyrównawcze — wg tej normy (przy instalacjach
    z tworzyw sztucznych zwykle niewymagane). Rozmieszczenie — arkusze {D.arkusze_nr('gniazda')}.
    """)
    o.rozdzial("Zasilanie urządzeń", poziom=2, podstawa="§ 23 pkt 8 lit. b RPB; WT § 188 ust. 2")
    o.tabela([{"Obw.": x.odb.id, "Urządzenie": _skrot(x.odb.nazwa, 80), "P [kW]": x.odb.P, "Fazy": x.odb.fazy,
               "I_B [A]": x.I_B, "Zabezp.": x.zab, "Przewód": x.przewod, "Ochrona różnicowoprądowa": x.odb.rcd}
              for x in urz], tytul="Urządzenia zasilane z obwodów wydzielonych",
             formaty={"P [kW]": 2, "I_B [A]": 1},
             uwagi="Moc pompy ciepła, grzałki i centrali wentylacyjnej — z doboru w PT-3 IS (moduły ogrzewania "
                   "i wentylacji); typ RCD dla urządzeń z przekształtnikami (PC, falownik PV, ładowarka EV) — wg DTR.",
             zrodlo="lamela.obliczenia.elektryka.bilans (odbiorniki z modelu) i obwody")
    o.rozdzial("Przewody, osprzęt, sposób wykonania", poziom=2, podstawa="WT § 183 ust. 1 pkt 8–9, § 187; W-184, W-198")
    o.tekst("""
    Przewody o żyłach miedzianych (WT § 183 ust. 1 pkt 9), izolacja 450/750 V; w ścianach pod tynkiem (grubość tynku
    nad przewodem ≥ 5 mm), w stropach monolitycznych i w warstwach posadzkowych — w rurach osłonowych umożliwiających
    wymianę przewodów (WT § 187); trasy równoległe do krawędzi ścian i stropów (WT § 183 ust. 1 pkt 8); przekrój
    minimalny 1,5 mm² (obwody siłowe i oświetleniowe). Kable w ziemi YKY 0,6/1 kV w rurach osłonowych. Przejścia
    przez przegrody oddzielenia pożarowego — nie występują (jedna strefa pożarowa). Puszki instalacyjne w ścianach
    z płyt g-k i w warstwie izolacji — szczelne powietrznie (ciągłość warstwy szczelności — PT-1 AR).
    Zaleca się urządzenia do detekcji zwarć łukowych (AFDD, PN-HD 60364-4-42) w obwodach sypialni (W-198 —
    zalecenie, nieobowiązkowe).
    """)
