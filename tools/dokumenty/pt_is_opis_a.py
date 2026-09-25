"""PT-3 IS — część opisowa A: stan opracowania, podstawy, opis instalacji (§ 23 pkt 7 lit. a, d, e RPB),
powiązania z sieciami (§ 23 pkt 8 RPB). Wszystkie liczby z ``DanePTIS`` (model + obliczenia przy uruchomieniu)."""
from __future__ import annotations

from collections import Counter

from pt_is_dane import MODULY, L, DanePTIS, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"
NAZWY_MOD = {"woda": "Instalacja wodociągowa i c.w.u.", "kanalizacja": "Kanalizacja sanitarna",
             "deszczowa": "Wody opadowe i retencja", "drenaz": "Drenaż i odwodnienie powierzchniowe",
             "ogrzewanie": "Ogrzewanie (PC, podłogówka, bufor, naczynia, hałas)"}


def rozdz_stan(o: Opis, D: DanePTIS):
    """1. Stan opracowania — wynik sprawdzeń obliczeniowych i sprawy otwarte."""
    o.rozdzial("Stan opracowania i sprawy otwarte", podstawa="rejestr wymagań, sekcja E")
    wiersze = []
    for k in MODULY:
        w = D.warunki(k)
        wiersze.append({"Obszar obliczeń": NAZWY_MOD[k], "Warunków": len(w),
                        "Spełnione": sum(1 for x in w if x.ok is True),
                        "Niespełnione": sum(1 for x in w if x.ok is False),
                        "Informacyjne": sum(1 for x in w if x.ok is None)})
    sp = D.went.sprawdzenia
    wiersze.append({"Obszar obliczeń": "Wentylacja mechaniczna (bilans, centrala, czerpnia/wyrzutnia)",
                    "Warunków": len(sp), "Spełnione": sum(1 for s in sp if s[2] is True),
                    "Niespełnione": sum(1 for s in sp if s[2] is False), "Informacyjne": sum(1 for s in sp if s[2] is None)})
    ep_ok = [D.ep.spelnia] + ([D.ep0.spelnia] if D.ep0 else [])
    wiersze.append({"Obszar obliczeń": "Charakterystyka energetyczna (EP ≤ EP_max; wariant z PV i bez PV)",
                    "Warunków": len(ep_ok), "Spełnione": sum(ep_ok), "Niespełnione": len(ep_ok) - sum(ep_ok),
                    "Informacyjne": 0})
    o.tekst(f"""
    Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z {D.t_modelu}) i bibliotek obliczeniowych
    `lamela.obliczenia` uruchamianych przy każdym generowaniu tomu — każda liczba w tomie pochodzi z modelu albo
    z obliczeń. Działka, MPZP, warunki gruntowo-wodne i warunki przyłączenia są {FIKCJA}; parametry urządzeń
    przyjęto z kart **wyrobów przykładowych** (oznaczenie {FIKCJA} lub [ZAŁ]) — dopuszcza się wyroby równoważne
    spełniające parametry wymagane podane w rozdziale „Zasadnicze urządzenia”.
    """)
    o.tabela(wiersze, tytul="Wynik sprawdzeń obliczeniowych PT-3 IS",
             uwagi="Warunki informacyjne — wartości podawane bez kryterium (np. moc ścian grzewczych uzupełniających).",
             zrodlo="lamela.obliczenia.sanitarne, lamela.obliczenia.energia — uruchomienie przy generowaniu tomu")
    if D.otwarte:
        o.tekst("**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status "
                "aktualizuje się przy ponownym generowaniu):\n\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(D.otwarte, 1)))
    else:
        o.tekst("Brak spraw otwartych wykrytych przez kontrole spójności modelu i obliczeń.")
    if D.z_cache:
        o.wniosek("PODGLĄD — obliczenia odczytane z pamięci podręcznej; wersja nie do wydania.", alarm=True)


def rozdz_podstawy(o: Opis, D: DanePTIS, d: dict):
    """2. Przedmiot, zakres i podstawy opracowania."""
    chl = bool((D.B.get("energia") or {}).get("chlodzenie"))
    o.rozdzial("Przedmiot, zakres i podstawy opracowania", podstawa="§ 23 RPB", nowa_strona=True)
    o.tekst(f"""
    **Przedmiot.** Projekt techniczny instalacji sanitarnych budynku mieszkalnego jednorodzinnego
    „{d.get('nazwa_krotka', 'Dom LAMELA')}” — {d.get('lokalizacja') or d.get('adres', '')}: ogrzewanie wodne
    płaszczyznowe zasilane pompą ciepła powietrze–woda z automatyczną regulacją temperatury, wentylacja mechaniczna
    nawiewno-wywiewna z odzyskiem ciepła, instalacja wody zimnej i ciepłej, kanalizacja sanitarna, odprowadzenie
    i zagospodarowanie wód opadowych (retencja), odwodnienie powierzchniowe, charakterystyka energetyczna budynku.

    **Zakres wg RPB (rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, Dz.U. 2020
    poz. 1609, t.j. Dz.U. 2022 poz. 1679 ze zm.):**

    * § 23 pkt 7 lit. a — instalacje ogrzewcze z urządzeniami automatycznie regulującymi temperaturę oddzielnie
      w poszczególnych pomieszczeniach; lit. d — wentylacja mechaniczna; lit. e — instalacje wodociągowe
      i kanalizacyjne (w tym wody opadowe);
    * § 23 pkt 7 lit. b i c (chłodzenie, klimatyzacja) — {'dotyczy (chłodzenie w modelu)' if chl else 'nie dotyczy: w modelu brak instalacji chłodzenia (`energia.chlodzenie`)'};
      lit. f (gaz) — nie dotyczy: budynek bez instalacji gazowej (źródło ciepła elektryczne — pompa ciepła);
      lit. g–i — tom PT-4 IE; lit. j (instalacje ochrony przeciwpożarowej) — nie dotyczy (dom jednorodzinny);
    * § 23 pkt 8 — powiązanie z sieciami zewnętrznymi i punkty pomiarowe, założenia (lit. a — parametry klimatu
      wewnętrznego), obliczenia i dobór urządzeń (lit. b — moce cieplne i elektryczne);
    * § 23 pkt 9 — zasadnicze urządzenia (pompa ciepła, zasobnik c.w.u., bufor, centrala wentylacyjna, zbiornik
      retencyjny); § 23 pkt 10 — dane ppoż. stosownie do zakresu; § 23 pkt 11 lit. a–d — charakterystyka energetyczna;
    * § 23 pkt 5, 6 i 12 — nie dotyczy (budynek mieszkalny, nie liniowy); § 23 pkt 4a — nie dotyczy (W-231);
    * § 24 pkt 3 i pkt 4 lit. a — rzuty i schematy instalacji (część rysunkowa).

    **Podstawy prawne i techniczne (rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`).**
    Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.); warunki techniczne (WT 2002; t.j. Dz.U. 2022 poz. 1225
    ze zm.) — stosowane na podstawie art. 102a PB; metodologia charakterystyki energetycznej (Dz.U. 2015 poz. 376
    ze zm., ost. 2023 poz. 697); rozporządzenia (UE) 2024/573 (F-gazy), 813/2013 (ekoprojekt PC), 1253/2014
    (centrale wentylacyjne); rozporządzenie w sprawie dopuszczalnych poziomów hałasu w środowisku (t.j. Dz.U. 2014
    poz. 112); Prawo wodne (t.j. Dz.U. 2025 poz. 960 ze zm.). Normy: PN-EN 12831:2006 (wycof., powołana w WT)
    i kontrolnie PN-EN 12831-1:2017-08; PN-B-03430:1983/Az3:2000 (wycof., wiąże przez WT); PN-B-01706:1992
    (wycof., powołana w WT) i kontrolnie PN-EN 806-1…-5; PN-EN 1717:2003 / PN-EN 1717+A1:2026-09;
    PN-EN 12056-1…-5:2002; PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10;
    PN-EN 14825:2022-11; PN-EN 16147+A1:2023-06; PN-EN 13141-7+A1:2026-05; PN-EN 378-1+A1:2021-03;
    wytyczne operatora Aquanet S.A. (zał. C, 2024) z opadem PANDa 2050 i normami opadowymi IMGW 1991–2020.
    Metody obliczeniowe bibliotek powołujące normy spoza tabeli A.3 rejestru (np. PN-EN 1264 — ogrzewanie
    płaszczyznowe, PN-EN 12828 — naczynia, PN-EN 1253-2 — wpusty) oznaczono w obliczeniach [NZW] — status wydań
    do potwierdzenia przed wydaniem do realizacji.

    **Materiały wyjściowe:** PZT i PAB (tom I), PT-1 AR (przegrody, U), PT-2 BO (przejścia przez płytę i stropy),
    PT-4 IE (zasilanie urządzeń), model `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`,
    `wyposazenie.yaml`, dane klimatyczne Poznań (TMY, WMO 12330). Tom jest zgodny z PZT i PAB oraz rozstrzygnięciami
    dotyczącymi zamierzenia budowlanego (oświadczenie projektanta).
    """)


def _obj(D: DanePTIS, ident: str) -> dict:
    return next((x for x in ((D.Dz.get("uzbrojenie") or {}).get("obiekty") or []) if x.get("id") == ident), {})


def _pom_nazwa(D: DanePTIS, pid: str) -> str:
    p = next((x for x in D.went.pomieszczenia if x.id == pid), None)
    return f"{pid} {p.nazwa}" if p else pid


def rozdz_ogrzewanie(o: Opis, D: DanePTIS):
    """3.1 Źródło ciepła i ogrzewanie z automatyczną regulacją (§ 23 pkt 7 lit. a)."""
    og, obc, pc = D.og, D.obc, D.og.pc
    biw, Wd = og.biwalentny, D.Wd["ogrzewanie"]
    n_pom = len({p.pom for p in og.petle})
    rozdz = "; ".join(f"{r['kond']}: {r['rozdzielacze']} rozdzielacz, {r['petle']} "
                      f"{'pętle' if 2 <= r['petle'] % 10 <= 4 and not 12 <= r['petle'] % 100 <= 14 else 'pętli'}, "
                      f"{L(r['m_kgh'], 0)} kg/h, Δp_max {L(r['dp_max'], 1)} kPa" for r in og.rozdzielacze)
    sg = D.I.get("grzejniki") or []
    o.rozdzial("Opis instalacji", podstawa="§ 23 pkt 7 RPB", nowa_strona=True)
    o.rozdzial("Źródło ciepła i instalacja ogrzewcza z automatyczną regulacją temperatury", poziom=2,
               podstawa="§ 23 pkt 7 lit. a RPB; W-150…W-156")
    o.tekst(f"""
    **Obciążenie cieplne.** Projektowe obciążenie cieplne budynku Φ_HL = **{L(obc.Phi_HL / 1000, 2)} kW**
    (PN-EN 12831, θ_e = {L(obc.theta_e, 0)} °C, średnia roczna θ_m,e = {L(obc.theta_me, 1)} °C; W-150, W-151),
    z dodatkiem na c.w.u. Φ_W = {L(og.Phi_W / 1000, 2)} kW. Temperatury wewnętrzne wg WT § 134 ust. 2 (model
    `pomieszczenia[].temp`); garaż nieogrzewany (θ_u = {', '.join(L(v, 1) for v in obc.theta_u.values()) or '—'} °C).

    **Źródło ciepła.** Pompa ciepła powietrze–woda typu monoblok na czynniku naturalnym R290 (W-155) —
    dane urządzenia przykładowego „{pc.get('model')}” {FIKCJA}: moc grzewcza P(A−7/W35) =
    {L(dict(zip(pc['T'], pc['P'])).get(-7), 1)} kW, SCOP (35 °C) = {L(pc.get('SCOP_35'), 2)}, η_s = {L(100 * (pc.get('eta_s_35') or 0), 0)} %,
    poziom mocy akustycznej L_WA = {L(pc.get('L_WA'), 0)} dB (tryb nocny {L(pc.get('L_WA_noc'), 0)} dB). Układ
    monoenergetyczny: punkt biwalentny θ_biv = **{L(biw['theta_biv'], 1)} °C**, grzałka elektryczna
    {L(og.par.grzalka_kW, 1)} kW pokrywa {L(100 * biw['udzial_grzalki'], 2)} % rocznego zapotrzebowania (bilans godzinowy
    TMY Poznań). Jednostka zewnętrzna: {_obj(D, 'PC-JZ').get('opis', 'lokalizacja wg PZT')}. Skropliny —
    {_obj(D, 'SK-PC').get('opis', 'odprowadzenie wg W-146')}. Moduł hydrauliczny, zasobnik c.w.u. i bufor —
    pomieszczenie techniczne parteru.

    **Instalacja ogrzewcza.** Ogrzewanie podłogowe wodne niskotemperaturowe: θ_V = **{L(og.theta_V, 0)} °C**,
    Δθ = {L(og.par.sigma, 0)} K, rura {og.par.d_rury_petli[0]}×{L(og.par.d_rury_petli[1], 1)} mm (PE-X/PE-RT z barierą
    antydyfuzyjną), {len(og.petle)} pętli w {n_pom} pomieszczeniach (długość pętli ≤ {L(og.par.L_petli_max, 0)} m,
    Δp pętli ≤ {L(og.par.dp_petli_max, 0)} kPa). Rozdzielacze kondygnacyjne: {rozdz}.
    {'Uzupełniające ściany grzewcze wodne (model `instalacje.grzejniki`): ' + ', '.join(f"{g['pom']} — {L(g.get('moc_W'), 0)} W" for g in sg) + '.' if sg else ''}
    Bufor szeregowy {Wd.get('bufor_l')} dm³ (odszranianie i minimalny czas pracy sprężarki przy zamkniętych
    pętlach), naczynie wzbiorcze przeponowe c.o. {og.naczynie_co.get('V_dob')} dm³, zawór bezpieczeństwa
    {L(og.par.p_SV, 1)} bar. Przewody PC ↔ budynek: {og.przewody_pc.get('rura')}, izolacja wewnątrz
    {L(og.przewody_pc.get('izol_WT'), 0)} mm, na zewnątrz {L(og.przewody_pc.get('izol_zewn'), 0)} mm z płaszczem UV.

    **Automatyczna regulacja (§ 23 pkt 7 lit. a–c RPB, WT § 135 ust. 7–10, W-152).** Regulacja pogodowa temperatury
    zasilania (krzywa grzewcza sterownika PC, czujnik zewnętrzny) oraz regulacja **oddzielnie w każdym
    pomieszczeniu**: termostat pokojowy + siłowniki termoelektryczne na pętlach rozdzielacza (sterownik listwowy
    z funkcją sterowania zależną od zapotrzebowania). Pomieszczenia bez stałego pobytu ludzi (komunikacja,
    schowki) — regulacja strefowa z pomieszczeniem sąsiednim. Hydrauliczne zrównoważenie pętli — nastawy
    przepływu na rozdzielaczach (tabela pętli w obliczeniach).
    """)


def rozdz_wentylacja(o: Opis, D: DanePTIS):
    """3.2 Wentylacja mechaniczna nawiewno-wywiewna z odzyskiem ciepła (§ 23 pkt 7 lit. d)."""
    w, c = D.went, D.went.centrala or {}
    lok = D.I.get("lokalizacje") or {}
    rek = next((x for x in D.Wy if x.get("typ") == "rekuperator"), {})
    o.rozdzial("Wentylacja mechaniczna nawiewno-wywiewna z odzyskiem ciepła", poziom=2,
               podstawa="§ 23 pkt 7 lit. d RPB; W-160…W-169")
    o.tekst(f"""
    Wentylacja mechaniczna zrównoważona z odzyskiem ciepła (WT § 148 ust. 2 — w pomieszczeniach z wentylacją
    mechaniczną bez wentylacji grawitacyjnej; W-160). Strumienie wg PN-83/B-03430/Az3 i WT § 149: nawiew
    Σ = **{L(w.suma_naw, 0)} m³/h**, wywiew Σ = **{L(w.suma_wyw, 0)} m³/h** (minimum wywiewu {L(w.suma_wyw_min, 0)} m³/h,
    minimum powietrza zewnętrznego {L(w.naw_min_osoby, 0)} m³/h = 20 m³/h × {w.osoby} os.); tryb okresowy (kuchnia)
    {L(w.V_boost, 0)} m³/h. Nawiew do pokoi, wywiew z kuchni, łazienek, WC, pralni i pomieszczeń bezokiennych;
    przepływ powietrza przez podcięcia/kratki drzwi. Bilans: {w.zrodlo_bilansu}.

    **Centrala** (urządzenie przykładowe — lub równoważne; {c.get('status', FIKCJA)}): {c.get('opis', '—')};
    wydajność nominalna {L(c.get('V_nom_m3h'), 0)} m³/h (maks. {L(c.get('V_max_m3h'), 0)} m³/h), sprawność odzysku
    η_t = {L(100 * (c.get('eta_t') or 0), 0)} %, SFP = {L(w.SFP_naw, 2)} kW/(m³/s) (limit WT {L(w.SFP_lim_naw, 2)}),
    klasa SEC {c.get('SEC_klasa', '—')} (SEC = {L(c.get('SEC_kWh_m2a'), 0)} kWh/(m²·a); (UE) 1253/2014), filtry
    {c.get('filtry', '—')}, moc wentylatorów {L(w.P_el_W, 0)} W. Lokalizacja: {rek.get('kond', '—')} — {rek.get('opis', '—')}.
    Kanał główny Ø{L(w.kanal_glowny_D_mm, 0)} mm; przewody powietrza zewnętrznego i wyrzutowego izolowane cieplnie
    z paroizolacją (W-168); tłumiki akustyczne na króćcach centrali; skropliny do kanalizacji przez syfon
    z zamknięciem wodnym. Czerpnia na wys. {L((lok.get('czerpnia') or [None] * 3)[2], 1)} m, wyrzutnia na wys.
    {L((lok.get('wyrzutnia') or [None] * 3)[2], 1)} m (odległości wg WT § 152 — sprawdzenia w obliczeniach).
    Garaż — wentylacja naturalna, bez połączenia z centralą ({'; '.join(g[0] for g in w.garaz) if w.garaz else '—'}).
    """)
    rows = [{"Pomieszczenie": f"{p.id} {p.nazwa}", "Nawiew [m³/h]": p.naw, "Wywiew [m³/h]": p.wyw,
             "Podstawa": p.podstawa or ("pokój — rozdział nawiewu" if p.naw else "—")}
            for p in w.pomieszczenia if p.naw or p.wyw]
    rows.append({"Pomieszczenie": "Razem", "Nawiew [m³/h]": w.suma_naw, "Wywiew [m³/h]": w.suma_wyw,
                 "Podstawa": "bilans ±10 %", "_klasa": "suma"})
    o.tabela(rows, tytul="Strumienie powietrza wentylacji mechanicznej",
             formaty={"Nawiew [m³/h]": 0, "Wywiew [m³/h]": 0}, wyrownanie={"Podstawa": "l"},
             zrodlo="model/budynek.yaml (pomieszczenia[].went); lamela.obliczenia.energia.wentylacja")


def rozdz_woda(o: Opis, D: DanePTIS):
    """3.3 Instalacja wodociągowa i c.w.u. (§ 23 pkt 7 lit. e)."""
    wd, Wd = D.W["woda"], D.Wd["woda"]
    cw, cis = wd.cwu, wd.cisnienia
    typy = Counter(p.typ for p in wd.przybory)
    rury = sorted({od.rura.split(" ")[0] for od in wd.odcinki if getattr(od, "rura", None)})
    o.rozdzial("Instalacja wodociągowa wody zimnej i ciepłej", poziom=2, podstawa="§ 23 pkt 7 lit. e RPB; W-130…W-137")
    o.tekst(f"""
    Zasilanie z sieci wodociągowej przyłączem (PZT); wodomierz główny **{Wd['wodomierz']}** w pomieszczeniu
    technicznym parteru (W-131), za nim filtr, zawór antyskażeniowy EA (PN-EN 1717) i
    {'reduktor ciśnienia (nastawa ' + L(cis.get('p_stat_za_reduktorem'), 0) + ' kPa)' if cis.get('reduktor') else 'bez reduktora'}.
    Przybory ({len(wd.przybory)}): {', '.join(f'{k} ×{v}' for k, v in sorted(typy.items()))}. Zapotrzebowanie:
    Q_d,śr = {L(Wd['Q_d_sr_m3'], 2)} m³/d, Q_h,max = {L(Wd['Q_h_max_m3'], 2)} m³/h; przepływ obliczeniowy
    q = **{L(Wd['q_obl_dm3s'], 3)} dm³/s** (W-132); wymagane ciśnienie przed wodomierzem p_wym = **{L(Wd['p_wym_kPa'], 0)} kPa**
    (punkt krytyczny: {Wd['punkt_krytyczny']}); ciśnienie w punktach czerpalnych 0,05–0,60 MPa (W-130).
    Przewody: {', '.join(rury)} (materiał przykładowy — lub równoważny o klasie ciśnienia i temperatury nie niższej;
    wyroby w kontakcie z wodą do spożycia — W-137); prowadzenie w bruzdach i przestrzeniach instalacyjnych,
    piony w szachcie SI.

    **Ciepła woda użytkowa.** Zasobnik c.w.u. **{Wd['zasobnik_l']} dm³** z wężownicą o powierzchni
    {L(cw.get('A_wez'), 1)} m² ogrzewany pompą ciepła (czas ładowania {L(cw.get('t_lad'), 1)} h); zapotrzebowanie
    V_d = {L(Wd['cwu_V_d_l'], 0)} dm³/d (55 °C). Cyrkulacja: {Wd['cyrkulacja']} (W-134). Dezynfekcja termiczna
    ≥ {L(wd.par.theta_dez_punkt, 0)} °C w punktach (zasobnik {L(wd.par.theta_dez_zas, 0)} °C, co {wd.par.dezynfekcja_co_dni} dni —
    {L(Wd['dezynfekcja_kWh_a'], 0)} kWh/a) z termostatycznym zaworem mieszającym (W-133). Grupa bezpieczeństwa
    zasobnika, naczynie przeponowe c.w.u. {D.og.naczynie_cwu.get('V_dob')} dm³. Izolacja cieplna przewodów c.w.u.,
    cyrkulacji i c.o. wg WT zał. 2 pkt 1.5 (W-135).
    """)
    o.tabela([{"Miejsce": r[0], "Kategoria cieczy": r[1], "Zabezpieczenie": r[2], "Podstawa": r[3]}
              for r in wd.zabezpieczenia_1717], tytul="Zabezpieczenia przed przepływem zwrotnym (PN-EN 1717)",
             wyrownanie={"Miejsce": "l", "Zabezpieczenie": "l", "Podstawa": "l"}, zrodlo="lamela.obliczenia.sanitarne.woda")


def rozdz_kanalizacja(o: Opis, D: DanePTIS):
    """3.4 Kanalizacja sanitarna (§ 23 pkt 7 lit. e)."""
    ka, Kd = D.W["kanalizacja"], D.Wd["kanalizacja"]
    st = ka.studzienka or {}
    went = "; ".join(f"{x['pion']} DN{x['dn']} — {x['wentylacja']}" for x in (ka.wentylacja or []))
    cofka = [x for x in ka.warunki if x.id == "W-140"]
    o.rozdzial("Kanalizacja sanitarna", poziom=2, podstawa="§ 23 pkt 7 lit. e RPB; W-138…W-140")
    o.tekst(f"""
    Kanalizacja grawitacyjna, system I wg PN-EN 12056-2 (K = 0,5): ΣDU = **{L(Kd['sum_DU'], 1)} l/s**,
    Q_ww = 0,5·√ΣDU = **{L(Kd['Q_ww_l_s'], 2)} l/s** (W-138). Piony: {went}; wentylacja pionów wg WT § 125 (W-139).
    Przewody odpływowe pod posadzką parteru (w płycie fundamentowej — przejścia wg PT-2 BO) do wyjścia z budynku,
    przykanalik **{Kd['przykanalik'].replace('i=', 'i = ')}** ze studzienką rewizyjną: {st.get('typ', '—')}, głębokość
    {L(st.get('glebokosc'), 2)} m, {L(st.get('dystans_granica'), 1)} m od granicy. Rzędne dna (wzgl. ±0,000):
    {'; '.join(f'{k} {L(v, 2)} m' for k, v in (ka.rzedne or {}).items())}.
    Zabezpieczenie przed cofką (WT § 124, W-140): {'; '.join(f"{x.opis} — {'spełnione' if x.ok else 'NIESPEŁNIONE'}" for x in cofka) or 'wg obliczeń'}.
    Skropliny centrali wentylacyjnej i wpust podłogowy pomieszczenia technicznego — przez syfony z zamknięciem
    wodnym (syfon wpustu z zabezpieczeniem przed wyschnięciem). Materiały: rury i kształtki PP-HT wewnątrz,
    PVC-U lite SN8 pod posadzką i na przykanaliku (przykładowe — lub równoważne).
    """)


def rozdz_deszczowa(o: Opis, D: DanePTIS):
    """3.5 Wody opadowe, retencja, drenaż (§ 23 pkt 7 lit. e)."""
    de, Dd, dr = D.W["deszczowa"], D.Wd["deszczowa"], D.W["drenaz"]
    ret, ret_m = de.retencja or {}, D.Dz.get("retencja") or {}
    n_wp = sum(len(p.wpusty or []) for p in de.pola)
    rs = [u for u in (D.Dz.get("uzbrojenie") or {}).get("projektowane", []) if u.get("branza") == "kan_deszcz"]
    nie = (ret_m.get("rozsaczanie") or {})
    o.rozdzial("Odprowadzenie i zagospodarowanie wód opadowych, drenaż", poziom=2,
               podstawa="§ 23 pkt 7 lit. e RPB; W-142…W-146, W-018, W-019")
    o.tekst(f"""
    **Odwodnienie dachów** (PN-EN 12056-3, r = 0,046 l/(s·m²); W-142): {len(de.pola)} pól dachowych
    o łącznej powierzchni **{L(Dd['A_dachow_m2'], 1)} m²**, Q = **{L(Dd['Q_dachy_l_s'], 2)} l/s**; {n_wp} wpustów
    dachowych (podgrzewane) i przelewy awaryjne w attykach; dach zielony ekstensywny
    ({', '.join(f"{z['id']} {L(z['A'], 1)} m²" for z in (de.dach_zielony or [])) or '—'}). Rury spustowe wewnętrzne
    (szacht SI) i zewnętrzne → kolektory deszczowe PVC-U: {'; '.join(u.get('opis', '') for u in rs[:3])}.

    **Retencja — wariant bazowy (W-145).** Szczelny zbiornik **{L(Dd['V_zbiornika_m3'], 1)} m³** (≤ 5 m³ — nie
    jest urządzeniem wodnym) z osadnikiem i filtrem, pompą do podlewania ogrodu (pokrycie zapotrzebowania
    na podlewanie {L(100 * Dd['pokrycie_podlewania'], 0)} %; bilans IMGW 1991–2020) i przelewem do niecki chłonnej
    (ogród deszczowy). Powierzchnia zredukowana zlewni A_red = {L(Dd['A_red_m2'], 1)} m²; wymagana objętość niecki
    (PANDa 2050, C = 10 lat, f_b = 1,2; W-143) V_min = **{L(Dd['niecka_V_min_m3'], 2)} m³**; niecka w modelu
    (dzialka.yaml): {L(nie.get('V'), 1)} m³, głębokość {L(nie.get('glebokosc'), 2)} m — czas opróżniania
    {L(ret.get('t_opr'), 1)} h (≤ 24 h). Deszczówka — instalacja odrębna, bez połączenia z wodociągiem (W-136).
    Odwodnienia liniowe przy drzwiach bez progu i przed bramą garażu ({len(de.odwodnienia_liniowe or [])} korytek
    wg obliczeń); woda z podjazdu i garażu przez osadnik z separatorem — nie do zbiornika retencyjnego.
    Skrzynki rozsączające — wyłącznie wariant opcjonalny po stanowisku PGW Wody Polskie (D-05).

    **Drenaż opaskowy: {dr.decyzja}** ({D.Wd['drenaz'].get('klasa_oddzialywania_wody')}).
    {' '.join(dr.uzasadnienie)} Zalecenia: {' '.join(dr.zalecenia[:2])}
    """)


def rozdz_sieci(o: Opis, D: DanePTIS):
    """4. Powiązania z sieciami zewnętrznymi i punkty pomiarowe (§ 23 pkt 8)."""
    uz = D.Dz.get("uzbrojenie") or {}
    ist = {u.get("branza"): u.get("opis", "") for u in uz.get("istniejace", [])}
    proj = [u for u in uz.get("projektowane", []) if u.get("branza") in ("woda", "kan_sanit", "kan_deszcz")]
    o.rozdzial("Powiązania instalacji z sieciami zewnętrznymi i punkty pomiarowe", podstawa="§ 23 pkt 8 RPB",
               nowa_strona=True)
    rows = [{"Medium": {"woda": "woda", "kan_sanit": "ścieki bytowe", "kan_deszcz": "wody opadowe"}[u["branza"]],
             "Sieć zewnętrzna / odbiornik": ist.get(u["branza"], "zagospodarowanie na działce (retencja)"),
             "Przyłącze / przewód": u.get("opis", ""), "Długość [m]": u.get("dl")} for u in proj]
    o.tabela(rows, tytul="Powiązania z sieciami i odbiornikami zewnętrznymi (dane działki — "
             f"{FIKCJA})", formaty={"Długość [m]": 1},
             wyrownanie={"Sieć zewnętrzna / odbiornik": "l", "Przyłącze / przewód": "l"},
             zrodlo="model/dzialka.yaml — uzbrojenie istniejące i projektowane")
    o.tekst(f"""
    **Punkty pomiarowe:** wodomierz główny {D.Wd['woda']['wodomierz']} (odczyt gestora sieci; W-131); licznik
    energii elektrycznej w ZKP (PT-4 IE) — pompa ciepła i grzałka zasilane z instalacji budynku (moce elektryczne
    — rozdział „Charakterystyka energetyczna”, bilans mocy). Sieć gazowa: {ist.get('gaz', 'brak')} —
    budynek bez przyłącza gazowego. Sieć ciepłownicza — brak (oświadczenie projektanta instalacyjnego w ZL; W-158).
    Parametry sieci (ciśnienie dyspozycyjne i maksymalne, rzędna kanału) przyjęto jako założenia [ZAŁ] — do
    potwierdzenia w warunkach przyłączenia gestorów sieci (D-23): ciśnienie dyspozycyjne
    {L(D.W['woda'].par.p_sieci_min, 2)} MPa, maksymalne {L(D.W['woda'].par.p_sieci_max, 2)} MPa.
    """)
