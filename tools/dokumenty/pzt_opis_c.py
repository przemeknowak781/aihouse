"""PZT — część opisowa, RPB § 14 pkt 5–8 i § 18: ograniczenia i zagrożenia, ochrona ppoż., ochrona ludności,
inne dane (retencja, strefa R290), obszar oddziaływania obiektu; część rysunkowa."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, ZAL, Arkusz, arkusze_z_katalogu, do_uzup, liczba

from pzt_dane import _poly
from redakcja import czysc, podstawa


def L(v, nd=2):
    return liczba(v, nd)


# ------------------------------------------------------------------------------------------------ § 14 pkt 5
def pkt5(zp, z, d):
    lz, _, _ = z.wym("usytuowanie", "linia_zabudowy_od_linii_rozgraniczajacej")
    kol, zr_kol, _ = z.wym("mpzp", "kolorystyka_elewacji")
    og = z.inst["ogrzewanie"]
    h = og.halas
    Ln, zr_n, i_n = z.wym("usytuowanie", "halas_LAeq_noc_max")
    Ld, zr_d, _ = z.wym("usytuowanie", "halas_LAeq_dzien_max")
    Lc, zr_c, _ = z.wym("usytuowanie", "halas_noc_cel")
    wyc = [t for t in z.drzewa() if t.get("do_wyciecia")]
    ha, _, _ = z.wym("usytuowanie", "wylaczenie_gruntow_bez_oplat_max")
    r290 = next((w for w in z.wyniki_audytu("Zagospodarowanie") if "R290" in w.element), None)
    zp.rozdzial("Informacje o ograniczeniach, zabytkach, wpływie eksploatacji górniczej i zagrożeniach",
                podstawa="§ 14 pkt 5 RPB")
    zp.markdown(f"""
    ## Ograniczenia i zakazy wynikające z aktów prawa miejscowego {{podstawa: § 14 pkt 5 lit. a}}
    Działka leży na terenie objętym miejscowym planem zagospodarowania przestrzennego — {(z.dz.get('dzialka') or {}).get('mpzp', '—')},
    przeznaczenie: zabudowa mieszkaniowa jednorodzinna wolnostojąca
    {DANE_PRZYKLADOWE} {do_uzup('wypis i wyrys z MPZP (E-02)')}. Ustalenia istotne dla zagospodarowania:
    nieprzekraczalna linia zabudowy {L(lz)} m od linii rozgraniczającej drogi {z.droga()['symbol']}; wskaźniki
    powierzchni zabudowy, powierzchni biologicznie czynnej, intensywności, wysokości, liczby kondygnacji, geometrii
    dachów i liczby miejsc postojowych (sprawdzenie — pkt 4); kolorystyka elewacji: {', '.join(kol)} ({zr_kol});
    ogrodzenie od drogi ażurowe, bez prefabrykatów betonowych; wody opadowe zagospodarowane w granicach działki;
    ogrzewanie ze źródeł niskoemisyjnych lub OZE (pompa ciepła powietrze–woda, budynek bez przyłącza gazowego).

    ## Ochrona konserwatorska {{podstawa: § 14 pkt 5 lit. b}}
    Działka nie jest wpisana do rejestru zabytków ani do gminnej ewidencji zabytków i nie leży na obszarze objętym
    ochroną konserwatorską (MPZP bez ustaleń ochrony konserwatorskiej) {DANE_PRZYKLADOWE}.

    ## Wpływ eksploatacji górniczej {{podstawa: § 14 pkt 5 lit. c}}
    Nie dotyczy — działka nie leży w granicach terenu górniczego {DANE_PRZYKLADOWE}.

    ## Zagrożenia dla środowiska oraz higieny i zdrowia {{podstawa: § 14 pkt 5 lit. d}}
    Zamierzenie nie jest przedsięwzięciem mogącym znacząco oddziaływać na środowisko (rozporządzenie Rady Ministrów,
    Dz.U. 2019 poz. 1839 ze zm., § 3 ust. 1 pkt 55 lit. a — progi powierzchni zabudowy mieszkaniowej nieosiągnięte
    [W-026]) — decyzja o środowiskowych uwarunkowaniach nie jest wymagana. Charakterystyka oddziaływań:
    """)
    zp.tabela([
        {"Oddziaływanie": "Hałas — jednostka zewnętrzna pompy ciepła",
         "Charakterystyka": f"{og.pc['model']}, L_WA = {L(og.pc['L_WA'], 0)} / {L(og.pc['L_WA_noc'], 0)} dB(A) (dzień / tryb nocny) {ZAL}; "
                            f"odległość od granicy ({h['granica']}) {L(h['r'])} m; poziom na granicy: noc {L(h['L_A_granica'], 1)} dB(A), "
                            f"dzień {L(h['L_A_dzien'], 1)} dB(A)",
         "Ocena": f"≤ {L(Ln, 0)} dB noc, ≤ {L(Ld, 0)} dB dzień ({zr_n}); cel ≤ {L(Lc, 0)} dB [{i_n}] — "
                  + ("spełnia" if h["L_A_granica"] <= Ln and h["L_A_dzien"] <= Ld else "NIE SPEŁNIA")},
        {"Oddziaływanie": "Emisje do powietrza", "Charakterystyka": "budynek bez źródeł spalania (ogrzewanie i c.w.u. — pompa ciepła, energia elektryczna, PV)",
         "Ocena": "brak emisji z instalacji spalania"},
        {"Oddziaływanie": "Ścieki i wody opadowe", "Charakterystyka": "ścieki bytowe do sieci; wody opadowe na działce; wody z podjazdu i garażu przez separator",
         "Ocena": "brak zrzutu do wód i na teren sąsiedni (opis wg § 14 pkt 3 lit. b i pkt 7 RPB)"},
        {"Oddziaływanie": "Odpady", "Charakterystyka": "odpady komunalne segregowane w stanowisku pojemników przy ogrodzeniu",
         "Ocena": "odbiór wg regulaminu gminy"},
        {"Oddziaływanie": "Zieleń", "Charakterystyka": f"drzewa do usunięcia: {len(wyc) or 'brak'}; drzewa istniejące zachowane",
         "Ocena": "zezwolenie / zgłoszenie usunięcia drzew nie dotyczy (u.o.p. art. 83f [W-023])" if not wyc else "wymagane zgłoszenie (u.o.p. art. 83f)"},
        {"Oddziaływanie": "Grunty rolne", "Charakterystyka": f"klasy gruntów {ZAL} — mineralne RIVb/RV {do_uzup('wypis z EGiB (E-03)')}",
         "Ocena": f"decyzja o wyłączeniu z produkcji nie dotyczy przy klasach IV–VI mineralnych [W-025]"},
        {"Oddziaływanie": "Czynnik chłodniczy R290 (propan)", "Charakterystyka": "strefa bezpieczeństwa wokół jednostki zewnętrznej bez otworów, wpustów, studzienek i źródeł zapłonu",
         "Ocena": (f"elementy w strefie: {czysc(r290.wartosc)} — " + ("spełnia" if r290.status == "OK" else "do sprawdzenia")
                   if r290 else "—") + " [W-156]"},
    ], tytul="Oddziaływania i zagrożenia", lp=True, szerokosci=["7mm", "34mm", None, "46mm"],
        zrodlo="lamela.obliczenia.sanitarne.ogrzewanie (hałas: wytyczne PORT PC, p. 4.4; ten sam wyrób i Φ_HL co w PAB, "
               "rozdz. 9 i 12); sprawdzenie geometryczne modelu (tools/audyt_wt.py); model/dzialka.yaml")


# ------------------------------------------------------------------------------------------------ § 14 pkt 6, 6a
def pkt6(zp, z, d):
    grupa = z.W["wysokosc_WT6"].get("grupa", "—")
    gr, zr_gr, _ = z.wym("ppoz", "grupa_wysokosci")
    zl, zr_zl, _ = z.wym("ppoz", "kategoria_ZL")
    o8, zr_o8, i_o8 = z.wym("usytuowanie", "odl_ppoz_ZL_ZL")
    q, zr_q, i_q = z.wym("ppoz", "woda_ppoz_min")
    sas = [s for s in z.sasiedzi() if s["odl_bud"] is not None]
    smin = min(sas, key=lambda s: s["odl_bud"]) if sas else None
    spl = min(sas, key=lambda s: s["odl_pl"]) if sas else None
    dh, hyd = z.odl_hydrantu()
    u2 = _poly(next((u for u in z.dz.get("utwardzenia") or [] if u.get("id") == "U2"), {}).get("obrys"))
    zp.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", f"""
    Budynek mieszkalny jednorodzinny, kategoria zagrożenia ludzi **{zl}** ({zr_zl}), grupa wysokości **{grupa}** —
    budynek niski (wysokość wg WT § 6: {L(z.w('wysokosc_WT6'))} m; {zr_gr}). Najmniejsza odległość od budynków
    sąsiednich: od ścian zewnętrznych {L(smin['odl_bud']) if smin else '—'} m (dz. {smin['nr'] if smin else '—'}),
    od płyt wysuniętych i okapów {L(spl['odl_pl']) if spl else '—'} m (dz. {spl['nr'] if spl else '—'}) — obie
    ≥ {L(o8, 1)} m ({zr_o8}; {i_o8}); ściany zewnętrzne i dach nierozprzestrzeniające ognia (PAB, rozdz. 13).

    **Droga pożarowa** — nie jest wymagana: budynek {zl} niski nie należy do obiektów, dla których wymaga się drogi
    pożarowej (rozporządzenie MSWiA w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych,
    Dz.U. 2009 nr 124 poz. 1030, § 12 ust. 1). Dojście od drogi publicznej {z.droga()['symbol']} — przez furtkę
    utwardzonym dojściem długości ok. {L(u2.bounds[3] - u2.bounds[1], 1) if u2 is not None else '—'} m do wejścia głównego (rys. PZT-01).

    **Przeciwpożarowe zaopatrzenie w wodę** — wymagana wydajność ≥ {L(q, 0)} dm³/s ({zr_q}; {i_q}) z sieci wodociągowej
    w drodze {z.droga()['symbol']}: {str((hyd or {}).get('opis', '—')).split(' — ')[0]}, w odległości ok.
    {L(dh, 0) if dh is not None else '—'} m od budynku {DANE_PRZYKLADOWE}
    {do_uzup('potwierdzenie lokalizacji i wydajności hydrantu przez gestora sieci')}.
    Przeciwpożarowy wyłącznik prądu — przy złączu kablowo-pomiarowym / wejściu (PT-4 IE).
    """, podstawa="§ 14 pkt 6 RPB")
    zp.rozdzial("Dane dotyczące ochrony ludności", """
    **Nie dotyczy.** Informacje i dane dotyczące warunków ochrony ludności podaje się w przypadku obiektu zbiorowej
    ochrony (§ 14 pkt 6a RPB, dodany Dz.U. 2026 poz. 597). Budynek mieszkalny jednorodzinny bez kondygnacji podziemnych
    nie jest obiektem, dla którego ustawa z dnia 5 grudnia 2024 r. o ochronie ludności i obronie cywilnej
    (Dz.U. 2024 poz. 1907 ze zm.) przewiduje budowlę ochronną lub miejsce doraźnego schronienia (art. 93–95 tej ustawy).
    """, podstawa="§ 14 pkt 6a RPB")


# ------------------------------------------------------------------------------------------------ § 14 pkt 7
def pkt7(zp, z, d):
    dsz = z.inst["deszczowa"]
    r = dsz.retencja
    ret = z.dz.get("retencja") or {}
    ro = ret.get("rozsaczanie") or {}
    ni = _poly(ro.get("obrys"))
    A_n, h_n = (ni.area if ni is not None else 0.0), float(ro.get("glebokosc") or 0.0)
    V_n = A_n * h_n
    vmax, zr_v, i_v = z.wym("wodkan", "zbiornik_opadowy_bez_zgloszenia_max")
    tmax, zr_t, _ = z.wym("wodkan", "retencja_oproznianie_max")
    fb, zr_fb, _ = z.wym("wodkan", "retencja_wsp_bezp_fb")
    lok = {w.element: w for w in z.wyniki_audytu("Zagospodarowanie") if w.element.startswith("retencja/")}
    geo = z.bud.get("geotechnika") or {}
    pv = (z.bud.get("energia") or {}).get("pv") or {}
    kwp = (pv.get("moduly") or 0) * (pv.get("P_modul_Wp") or 0) / 1000.0
    pvmax, zr_pv, i_pv = z.wym("procedura", "PV_prog_obowiazkow_ppoz")
    zp.rozdzial("Inne dane wynikające ze specyfiki zamierzenia", f"""
    ## Retencja i zagospodarowanie wód opadowych {{podstawa: § 14 pkt 7; W-143…W-145}}
    Metoda bilansowa Aquanet (2024), opad PANDa 2050 (C = 10 lat) {ZAL}; współczynnik filtracji gruntu
    k_f = {L(r['kf'] * 1e4, 1)}·10⁻⁴ m/s {ZAL} {do_uzup('k_f z badań podłoża (E-04)')}. Wyniki
    (`lamela.obliczenia.sanitarne.deszczowa`):
    """, podstawa="§ 14 pkt 7 RPB")
    zp.tabela_wynikow([
        dict(parametr="Powierzchnia zredukowana zlewni (dachy)", wartosc=r["A_red"], jedn="m²", wymaganie="—",
             podstawa="Aquanet 2024 tab. 2", spelnia=None),
        dict(parametr="Pojemność szczelnego zbiornika retencyjnego", wartosc=r["V_zb"], jedn="m³", wymaganie=f"≤ {L(vmax, 1)} m³",
             podstawa=f"{zr_v} [{i_v}]", spelnia=r["V_zb"] <= vmax),
        dict(parametr=f"Niecka chłonna {L(A_n, 1)} m² × {L(h_n)} m — pojemność", wartosc=V_n, jedn="m³",
             wymaganie=f"≥ V_min = {L(fb, 1)}·V_obl = {L(r['V_min_a'])} m³", podstawa=zr_fb, spelnia=V_n >= r["V_min_a"]),
        dict(parametr="Czas opróżniania niecki", wartosc=r["t_opr"], jedn="h", wymaganie=f"≤ {L(tmax, 0)} h",
             podstawa=zr_t, spelnia=r["t_opr"] <= tmax),
    ] + [dict(parametr=f"Lokalizacja — {k.split('/')[1].replace('rozsaczanie', 'niecka chłonna')}: odl. od granic / od "
                        f"budynku", wartosc=czysc(w.wartosc), wymaganie=czysc(w.wymog),
              podstawa=podstawa(w.podstawa), spelnia=w.status == "OK") for k, w in lok.items()],
        tytul="Retencja wód opadowych (wariant bazowy: zbiornik szczelny + niecka)",
        uwagi=["Zbiornik ≤ 5 m³ nie wymaga pozwolenia ani zgłoszenia (PB art. 29 ust. 2 pkt 36); rozsączanie skrzynkowe — "
               "wyłącznie po stanowisku PGW Wody Polskie (rejestr D-05, E-07)."])
    zp.markdown(f"""
    ## Warunki gruntowe i pozostałe dane
    Kategoria geotechniczna: **{geo.get('kategoria', '—')}** ({czysc(geo.get('uwagi', '—'))}); grunt: {(geo.get('grunt') or {}).get('rodzaj', '—')},
    zwierciadło wody gruntowej ok. {L(abs(geo.get('ZWG', 0)), 1)} m p.p.t. {DANE_PRZYKLADOWE}
    {do_uzup('opinia geotechniczna (E-04)')}. Instalacja fotowoltaiczna na dachach: {pv.get('moduly', '—')} modułów,
    {L(kwp)} kWp ≤ {L(pvmax, 1)} kWp ({zr_pv.split(' (')[0]}; {i_pv}).
    """)


# ------------------------------------------------------------------------------------------------ § 14 pkt 8, § 18
def pkt8(zp, z, d):
    l_o, zr_o, i_o = z.wym("usytuowanie", "odl_granica_z_otworami")
    l_b, zr_b, _ = z.wym("usytuowanie", "odl_granica_bez_otworow")
    l_k, zr_k, _ = z.wym("usytuowanie", "odl_granica_okap_gzyms_balkon_schody")
    o8, zr_o8, _ = z.wym("usytuowanie", "odl_ppoz_ZL_ZL")
    oj, zr_oj, _ = z.wym("usytuowanie", "odl_krawedz_jezdni_gminnej")
    hn, zr_hn, _ = z.wym("usytuowanie", "naslonecznienie_h_min")
    gr_mp, zr_mp, _ = z.wym("usytuowanie", "parking_odl_granica_min")
    Ln, zr_n, _ = z.wym("usytuowanie", "halas_LAeq_noc_max")
    kier = [g["kier"] for g in z.granice if not g["drogowa"]]

    def mn(prefix, otw=None):
        c = [z.odl_min(k, prefix, otw) for k in kier]
        c = [x for x in c if x]
        return min(c, key=lambda x: x[0]) if c else (float("nan"), "—", 0)
    s_o, s_b, s_k = mn("ściana", True), mn("ściana", False), mn("płyta")
    sas = [s for s in z.sasiedzi() if s["odl_bud"] is not None]
    smin = min(sas, key=lambda s: s["odl_bud"]) if sas else None
    spl = min(sas, key=lambda s: s["odl_pl"]) if sas else None
    H = z.W["wysokosc_zabudowy"]["z_top_abs"] - z.W["wysokosc_zabudowy"]["t_min"]
    ns = z.naslonecznienie_sasiadow()
    dmin_s = min(s["odl_bud"] for s in sas) if sas else float("nan")
    h = z.inst["ogrzewanie"].halas
    mp = [x for x in z.mp_odleglosci() if x[1] != "garaz"]
    dr = z.droga()
    rows = [
        ("WT § 12 ust. 1 pkt 1", "ściany z oknami/drzwiami od granicy", s_o[0], f"≥ {L(l_o)} m", s_o[0] >= l_o, s_o[1]),
        ("WT § 12 ust. 1 pkt 2", "ściany bez otworów od granicy", s_b[0], f"≥ {L(l_b)} m", s_b[0] >= l_b, s_b[1]),
        ("WT § 12 ust. 6 pkt 1", "okapy, płyty wysunięte, daszki od granicy", s_k[0],
         f"≥ {L(l_k)} m" + (f" (przyjęto ≥ {L(s_k[2])} m {ZAL})" if s_k[2] and s_k[2] > l_k + 1e-6 else ""),
         s_k[0] >= max(l_k, s_k[2] or 0) - 1e-6, s_k[1]),
        ("WT § 13", "przesłanianie budynków sąsiednich: odległość ≥ wysokość przesłaniania",
         dmin_s, f"≥ {L(H)} m (z_top − t_min)", dmin_s >= H, "budynki sąsiednie"),
        ("WT § 60", "nasłonecznienie budynków sąsiednich w dniach równonocy (ocena uproszczona)",
         min(x["h_min"] for x in ns) if ns else float("nan"), f"≥ {L(hn, 0)} h", all(x["h_min"] >= hn for x in ns), "cień budynku"),
        ("WT § 19 ust. 2", "stanowiska postojowe naziemne od granicy", min(x[3] for x in mp) if mp else float("nan"),
         f"≥ {L(gr_mp)} m", all(x[3] >= gr_mp for x in mp), ", ".join(x[0] for x in mp)),
        ("WT § 271 ust. 1", "odległość ścian budynków ZL od budynków sąsiednich (od płyt wysuniętych: "
         f"{L(spl['odl_pl']) if spl else '—'} m, dz. {spl['nr'] if spl else '—'})", dmin_s, f"≥ {L(o8)} m",
         dmin_s >= o8 and (spl is None or spl["odl_pl"] >= o8), f"dz. {smin['nr']}" if smin else "—"),
        ("u.d.p. art. 43 ust. 1", f"budynek od zewnętrznej krawędzi jezdni drogi gminnej {dr['symbol']}", dr["odl_bud_jezdnia"],
         f"≥ {L(oj)} m", dr["odl_bud_jezdnia"] >= oj, "—"),
        ("POŚ art. 144 ust. 2; Dz.U. 2014 poz. 112", "hałas instalacji (PC) na granicy — pora nocy", h["L_A_granica"],
         f"≤ {L(Ln, 0)} dB(A)", h["L_A_granica"] <= Ln, h["granica"]),
    ]
    jedn = ["m", "m", "m", "m", "h", "m", "m", "m", "dB(A)"]
    ok = all(r[4] for r in rows) and z.lz_rezerwa >= 0
    zp.rozdzial("Informacja o obszarze oddziaływania obiektu", f"""
    Obszar oddziaływania obiektu (PB art. 3 pkt 20 — teren wyznaczony w otoczeniu obiektu na podstawie przepisów
    odrębnych, wprowadzających związane z tym obiektem ograniczenia w zabudowie tego terenu) określono na podstawie
    przepisów wymienionych w tabeli (§ 18 pkt 1 RPB) oraz: WT § 23 (miejsca gromadzenia odpadów — dla zabudowy
    jednorodzinnej odległości nieustalone), WT § 28 (wody opadowe — zagospodarowane na działce), ustawy – Prawo
    wodne (t.j. Dz.U. 2025 poz. 960 ze zm.) art. 234 ust. 1 (zakaz zmiany kierunku i natężenia odpływu wód opadowych
    ze szkodą dla gruntów sąsiednich i odprowadzania wód na grunty sąsiednie), ustaleń MPZP (linia zabudowy,
    wskaźniki — rozdział opisu wg § 14 pkt 4 RPB). Wartości — minimum dla wszystkich elementów budynku i granic
    niedrogowych (sprawdzenie geometryczne modelu — `tools/audyt_wt.py`).
    """, podstawa="§ 14 pkt 8, § 18 RPB")
    zp.tabela([{"Przepis": a, "Ograniczenie": b, "Projekt": f"{L(c, 1 if u != 'm' else 2)} {u}", "Wymaganie": e,
                "Ocena": "spełnia" if f else "NIE SPEŁNIA", "Element": g} for (a, b, c, e, f, g), u in zip(rows, jedn)],
              tytul="Przepisy wyznaczające obszar oddziaływania i sprawdzenie", wyrownanie={"Projekt": "r"},
              szerokosci=["26mm", None, "18mm", "22mm", "16mm", "18mm"], klasa="zwarta",
              uwagi=[f"{zr_o} [{i_o}]; {zr_k}; {zr_hn} — " + ", ".join(".".join(reversed(x.split("-"))) for x in ns[0]["daty"])
                     + f", godz. "
                     f"{ns[0]['przedzial'][0]}–{ns[0]['przedzial'][1]}" if ns else zr_o])
    if ok:
        zp.wniosek(f"**Obszar oddziaływania obiektu mieści się w całości na działce nr ewid. {d['dzialka']['nr']}, "
                   "na której obiekt został zaprojektowany** (§ 18 pkt 2 RPB).")
    else:
        zp.wniosek("**Obszar oddziaływania obiektu wykracza poza działkę** — zasięg wg pozycji „NIE SPEŁNIA” w tabeli; "
                   "wymagana korekta projektu lub opis zasięgu (§ 18 pkt 2 RPB).", alarm=True)


# ------------------------------------------------------------------------------------------------ część rysunkowa
def rysunki(zp, z, d):
    kat = z.repo / "projekt/02_PZT/rysunki"
    ark = arkusze_z_katalogu(kat)
    for a in ark:
        if a.nr == "PZT-01":
            a.uwagi = ("podkład: mapa przykładowa (fikcyjna) — " +
                       do_uzup("mapa do celów projektowych z klauzulą lub oświadczeniem geodety (E-01)"))
    zp.czesc_rysunkowa(ark, podstawa="§ 7 ust. 1 pkt 4, § 15–17 RPB")
