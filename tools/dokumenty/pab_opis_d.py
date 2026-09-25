"""PAB — rozdziały 12–15 (RPB § 20 ust. 1 pkt 12–14, ust. 2). Liczby z ``DanePAB``; limity z rejestru wymagań."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, do_uzup, liczba as L
from lamela.dokumenty.znaczniki import INT, ZAL

from pab_opis_a import ok, tyt

ROLE = {"sciana_zewn": "ściana zewnętrzna", "dach": "stropodach / dach", "podloga_grunt": "podłoga na gruncie",
        "strop_zewn": "strop nad powietrzem zewnętrznym", "sciana_nieogrz": "ściana do garażu nieogrzewanego"}


def _krotko(txt: str, n: int = 95) -> str:
    t = str(txt).split(" (U")[0]
    return t if len(t) <= n else t[: n - 1].rsplit(" ", 1)[0] + "…"


def r12(pab, D, d):
    ob, og, wo, ka = D.ob, D.W["ogrzewanie"], D.Wd["woda"], D.Wd["kanalizacja"]
    bi, pv, od, went = D.Wd["bilans"], D.Wd["pv"], D.Wd["odgromowa"], D.went
    pc = (D.obc.dobor or {}).get("pc") or {}
    dob = D.obc.dobor or {}
    tele = next((u.get("opis") for u in ((D.Dz.get("uzbrojenie") or {}).get("projektowane") or [])
                 if u.get("branza") == "tele"), do_uzup("instalacja telekomunikacyjna"))
    pab.rozdzial(tyt("Zasadnicze elementy wyposażenia budowlano-instalacyjnego", 12))
    rows = []
    for (kod, rola), wu in ob.u.items():
        if rola in ROLE and (kod, rola) in ob.klucze_ogrz:
            pk = D.m.przegroda(kod)
            rows.append({"Przegroda": f"{kod} — {_krotko(pk.nazwa)}" if pk else f"{kod.split('|')[0]} — {ROLE[rola]}",
                         "Rodzaj": ROLE[rola], "U [W/(m²·K)]": wu.U, "U_max [W/(m²·K)]": wu.U_max,
                         "Ocena": ok(wu.U_max is None or wu.U <= wu.U_max + 1e-9)})
    for rola, opis in (("okno", "okna, drzwi balkonowe, przeszklenia"), ("drzwi", "drzwi zewnętrzne i do garażu")):
        ww = [x for x in ob.okna.values() if x.rola == rola]
        if ww:
            umax = min(x.U_max for x in ww if x.U_max)
            rows.append({"Przegroda": f"stolarka: {', '.join(sorted({x.symbol for x in ww}))}", "Rodzaj": opis,
                         "U [W/(m²·K)]": f"{L(min(x.U_w for x in ww))}–{L(max(x.U_w for x in ww))}",
                         "U_max [W/(m²·K)]": umax, "Ocena": ok(all(x.U_w <= x.U_max + 1e-9 for x in ww))})
    pab.markdown("""
    ## Przegrody zewnętrzne (izolacyjność cieplna)

    Konstrukcja murowo-żelbetowa: ściany nośne z bloków wapienno-piaskowych, stropy, schody i płyta fundamentowa
    żelbetowe monolityczne, słupy fasady stalowe; izolacja termiczna ciągła wokół kubatury ogrzewanej (ETICS, elewacja
    wentylowana za lamelami, stropodachy z izolacją spadkową, XPS pod płytą). Współczynniki przenikania ciepła
    (PN-EN ISO 6946, PN-EN ISO 13370, PN-EN ISO 10077 — `lamela.obliczenia.fizyka`) i wartości graniczne WT zał. 2:
    """)
    pab.tabela(rows, tytul="Współczynniki przenikania ciepła przegród i stolarki", klasa="zwarta",
               formaty={"U [W/(m²·K)]": 3, "U_max [W/(m²·K)]": 2}, szerokosci=[None, "38mm", "20mm", "20mm", "18mm"],
               zrodlo="lamela.obliczenia.energia.oblicz_obudowe (U_max — WT zał. 2 pkt 1.1–1.2; W-243, W-244)",
               uwagi=[f"Parametry stolarki — wyroby przykładowe {DANE_PRZYKLADOWE}; wymagane deklaracje właściwości użytkowych."])
    pab.markdown(f"""
    ## Źródło ciepła i przygotowanie ciepłej wody użytkowej

    * **Źródło ciepła:** {pc.get('opis', do_uzup('pompa ciepła'))} — wyrób przykładowy {og.pc.get('model', '')}
      {DANE_PRZYKLADOWE}; projektowe obciążenie cieplne budynku Φ_{{HL}} = {L(D.obc.Phi_HL / 1000, 2)} kW (PN-EN 12831-1),
      moc pompy przy θ_{{e}} = {L(D.obc.theta_e, 0)} °C: {L(dob.get('P_PC_te_kW'), 2)} kW, punkt biwalentny
      {L(og.biwalentny.get('theta_biv'), 1)} °C, grzałka elektryczna szczytowa (udział w energii
      {L(100 * og.bin.get('udzial_grzalki', 0), 2)} %). Jednostka zewnętrzna — monoblok na czynniku R290 na działce
      (strefa bezpieczeństwa wg DTR, W-156); moduł hydrauliczny w pomieszczeniu technicznym na parterze.
    * **Ogrzewanie:** wodne płaszczyznowe (podłogowe) niskotemperaturowe, temperatura zasilania {L(og.theta_V, 1)} °C,
      rozdzielacze na każdej kondygnacji, ściany grzewcze w łazienkach; regulacja — rozdz. 11. Garaż nieogrzewany.
    * **Ciepła woda użytkowa:** z pompy ciepła, zasobnik {wo['zasobnik_l']} dm³ (dobowe zapotrzebowanie {L(wo['cwu_V_d_l'], 0)} dm³),
      cyrkulacja: {wo['cyrkulacja']}; okresowa dezynfekcja termiczna; zawór termostatyczny przed punktami poboru.
    * **Wentylacja:** mechaniczna nawiewno-wywiewna z odzyskiem ciepła, centrala w pomieszczeniu technicznym II piętra;
      strumienie Σ nawiew = {L(went.suma_naw, 0)} m³/h, Σ wywiew = {L(went.suma_wyw, 0)} m³/h (PN-83/B-03430/Az3; WT § 149),
      sprawność odzysku {L(100 * went.eta, 0)} %; czerpnia i wyrzutnia dachowe (WT § 152; W-166). Garaż — wentylacja
      naturalna (kratki w bramie).
    * **Wodociąg i kanalizacja:** przyłącze wodociągowe, wodomierz {wo['wodomierz']} w pomieszczeniu technicznym;
      kanalizacja sanitarna grawitacyjna, piony {', '.join(f'{k} {v}' for k, v in (ka.get('piony') or {}).items())},
      przykanalik {ka['przykanalik']} do sieci; wody opadowe — rozdz. 9.
    * **Instalacja elektryczna:** zasilanie kablowe nN ze złącza w linii ogrodzenia, moc przyłączeniowa
      {L(bi['P_przylaczeniowa_kW'], 0)} kW, zabezpieczenie przedlicznikowe {L(bi['I_zab_A'], 0)} A (moc szczytowa z
      zarządzaniem obciążeniem {L(bi['P_szczyt_DLM_kW'], 1)} kW); układ TN-S, ochrona różnicowoprądowa i przeciwprzepięciowa,
      przeciwpożarowy wyłącznik prądu (rozdz. 13). Instalacja fotowoltaiczna {L(pv['P_kWp'], 2)} kWp na dachach płaskich
      (mikroinstalacja; PB art. 29 ust. 4 pkt 3 lit. c — W-194). Ochrona odgromowa: {od['decyzja_LPS']} (analiza ryzyka
      PN-EN 62305-2 — W-191); uziom {od['uziom']}.
    * **Instalacja telekomunikacyjna:** {tele}.
    * Szczegółowe rozwiązania i obliczenia: PT-3 IS, PT-4 IE (osobne tomy projektu technicznego).
    """)


def r13(pab, D, d):
    w, kn = D.w, D.w["kondygnacje_nadziemne"]["wartosc"]
    h6 = w["wysokosc_WT6"]
    V = D.kubatura
    netto = sum(r["pow"] for r in D.pom)
    wyj = sorted({o.raw.get("symbol") or o.id for o in D.m.otwory() if o.typ in ("drzwi_zewn", "drzwi_przesuwne_HS")
                  and o.kond == D.m.kondygnacje[0].id})
    sch = [b["szer"] for s in D.m.schody() for b in s.get("biegi", [])]
    s_min = min((min(s["d"], s["d_pl"]) for s in D.sasiedzi), default=None)
    l_zl = D.v("usytuowanie", "odl_ppoz_ZL_ZL")
    pv = D.Wd["pv"]
    zw = D.v("ppoz", "zwolnienie_213_kondygnacje_max")
    v_pwp = D.v("elektryka", "PWP_kubatura_strefy_prog")
    p_pv = D.v("procedura", "PV_prog_obowiazkow_ppoz")
    rows = [
        ("Kategoria zagrożenia ludzi", str(D.v("ppoz", "kategoria_ZL")), D.zr("ppoz", "kategoria_ZL")),
        ("Wysokość i grupa wysokości", f"{L(h6['wartosc'])} m — niski ({h6.get('grupa')})", "WT § 6, § 8 pkt 1"),
        ("Liczba kondygnacji nadziemnych / podziemnych", f"{kn} / 0", w["kondygnacje_nadziemne"]["podstawa"]),
        ("Strefa pożarowa", f"cały budynek z garażem — kubatura brutto {L(V)} m³; Σ pow. netto pomieszczeń {L(netto)} m²",
         "WT § 226 ust. 1 (W-212)"),
        ("Klasa odporności pożarowej budynku; klasy odporności ogniowej i stopień rozprzestrzeniania ognia elementów",
         "wymagań nie stawia się" if kn <= zw else "WYMAGANE — budynek > 3 kondygnacji", D.zr("ppoz", "zwolnienie_213_kondygnacje_max")),
        ("Ściany zewnętrzne, okładziny, przekrycie dachu", f"nierozprzestrzeniające ognia (ETICS NRO, dach B_ROOF(t1)) {ZAL}",
         "WT § 271 ust. 2, § 272 ust. 2 (W-213)"),
        ("Odległość od budynków sąsiednich", f"min. {L(s_min)} m — {ok(s_min is not None and s_min >= l_zl)} (≥ {L(l_zl)} m)",
         D.zr("usytuowanie", "odl_ppoz_ZL_ZL")),
        ("Przeciwpożarowy wyłącznik prądu", (f"projektuje się (kubatura strefy {L(V)} m³ > {L(v_pwp, 0)} m³)" if V > v_pwp
         else "projektuje się (rekomendacja W-190)") + " — przy złączu kablowo-pomiarowym / wejściu głównym, oznakowany",
         D.zr("elektryka", "PWP_kubatura_strefy_prog") + "; WT § 183 ust. 3; D-04"),
        ("Czujki dymu", f"autonomiczne czujki dymu w lokalu (na każdej kondygnacji i w sypialniach {ZAL})", "ROPoż § 28a (W-197)"),
        ("Instalacja fotowoltaiczna", f"{L(pv['P_kWp'], 2)} kWp ≤ {L(p_pv, 1)} kWp — bez uzgodnienia z rzeczoznawcą "
         "i zawiadomienia PSP" if pv["P_kWp"] <= p_pv else f"{L(pv['P_kWp'], 2)} kWp > {L(p_pv, 1)} kWp — wymagane "
         "uzgodnienie z rzeczoznawcą", D.zr("procedura", "PV_prog_obowiazkow_ppoz")),
        ("Droga pożarowa", "niewymagana (budynek niski ZL IV); dojazd i dojście od drogi publicznej "
         f"{D.droga.get('symbol', '')}", "rozp. Dz.U. 2009 nr 124 poz. 1030 § 12 ust. 1 (W-217)"),
        ("Zaopatrzenie w wodę do zewnętrznego gaszenia", f"≥ {L(D.v('ppoz', 'woda_ppoz_min'), 0)} dm³/s z sieci wodociągowej; "
         f"najbliższy hydrant ok. {L(D.hydrant['d'], 0) if D.hydrant else '—'} m od budynku {DANE_PRZYKLADOWE}",
         D.zr("ppoz", "woda_ppoz_min")),
        ("Ewakuacja", f"wyjścia na zewnątrz z parteru: {', '.join(wyj)}; schody wewnętrzne — biegi {L(min(sch)) if sch else '—'} m",
         "WT (budynek jednorodzinny — bez wymagań dla dróg ewakuacyjnych)" + f" {INT}"),
        ("Uzgodnienie projektu z rzeczoznawcą ds. zabezpieczeń ppoż.", "niewymagane", "rozp. Dz.U. 2023 poz. 1563 § 3 ust. 1 (W-218)"),
    ]
    pab.rozdzial(tyt("Dane dotyczące warunków ochrony przeciwpożarowej", 13))
    pab.tabela([{"Parametr": a, "Ustalenie": b, "Podstawa": c} for a, b, c in rows], tytul="Warunki ochrony przeciwpożarowej",
               klasa="zwarta", szerokosci=["46mm", None, "50mm"],
               uwagi=[f"Budynek mieszkalny jednorodzinny o nie więcej niż {zw} kondygnacjach nadziemnych — zwolnienie z WT § 212 "
                      "i § 216 na podstawie § 213 pkt 1 lit. a (zastrzeżenia § 217 ust. 2 i § 271 ust. 8a nie dotyczą). "
                      "Klas odporności ogniowej nie oznacza się na rysunkach (W-219)."],
               zrodlo="lamela.wskazniki; lamela.model; lamela.obliczenia; rejestr wymagań B.11")


def r14_15(pab, D, d):
    pab.rozdzial(tyt("Informacje i dane dotyczące warunków ochrony ludności", 14))
    pab.markdown("""
    **Nie dotyczy.** Budynek nie jest obiektem zbiorowej ochrony (budowlą ochronną ani obiektem przystosowanym do
    zorganizowania miejsca doraźnego schronienia) w rozumieniu ustawy z dnia 5 grudnia 2024 r. o ochronie ludności
    i obronie cywilnej (Dz.U. poz. 1907 ze zm.) — zakres projektu w części ochrony ludności dotyczy wyłącznie obiektów
    zbiorowej ochrony (RPB § 3 ust. 1 pkt 2 w brzmieniu nadanym rozporządzeniem Dz.U. 2026 poz. 597).
    """)
    niezg = D.audyt_statusy.get("NIEZGODNE", 0)
    pab.rozdzial("Informacja o zgodzie na odstępstwo (§ 20 ust. 2 RPB)")
    pab.markdown(f"""
    **Nie dotyczy** — nie wydano zgody na odstępstwo od przepisów techniczno-budowlanych (art. 9 PB) ani postanowienia,
    o którym mowa w art. 6a ust. 2 ustawy o ochronie przeciwpożarowej; projekt nie przewiduje rozwiązań wymagających
    takiej zgody (audyt zgodności z WT: {niezg} niezgodności).
    """)
