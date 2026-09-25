"""PZT — część opisowa, RPB § 14 pkt 1–3 (przedmiot zamierzenia, stan istniejący, projektowane zagospodarowanie).
Wszystkie liczby z ``DaneZag`` (model, wskaźniki, audyt A1, obliczenia) — przy zmianie modelu tekst się aktualizuje."""
from __future__ import annotations

from shapely.geometry import LineString

from lamela.dokumenty import DANE_PRZYKLADOWE, ZAL, do_uzup, liczba

from pzt_dane import _poly
from redakcja import LEGENDA, czysc


def L(v, nd=2):
    return liczba(v, nd)


def _utw(z, uid):
    return next((u for u in z.dz.get("utwardzenia") or [] if u.get("id") == uid), {})


def _naw(z, uid):
    """Nawierzchnia utwardzenia bez powtórzonej nazwy elementu („podjazd — kostka …” → „kostka …”)."""
    n = str(_utw(z, uid).get("nawierzchnia", "—"))
    return n.split("—", 1)[1].strip() if "—" in n else n


def _gat(t):
    """Gatunek drzewa bez dopisku o stanie (stan — osobna kolumna)."""
    return str(t.get("gat", "—")).split(" (istniej")[0]


def _drenaz(o):
    """Decyzja o drenażu z modelu; wartości głębokości z opisu roboczego pomija się — głębokość posadowienia
    (z definicją) podaje PAB, rozdz. 5, a zwierciadło wody — pkt „Warunki gruntowe” niniejszego opisu."""
    import re
    if not o:
        return "Drenażu opaskowego nie przewiduje się"
    op = czysc(o.get("opis", ""))
    op = re.sub(r",?\s*(?:ZWG|posadowienie)\s*≈\s*[\d,]+\s*m\s*p\.p\.t\.", "", op)
    if "NIE PROJEKTUJE" in op.upper():
        return ("Drenażu opaskowego nie projektuje się — " + (op.split("—", 1)[1].strip() if "—" in op else "")
                + " (zwierciadło wody gruntowej poniżej poziomu posadowienia — warunki gruntowe w rozdziale opisu wg § 14 pkt 7 RPB; posadowienie — PAB, rozdz. 5)")
    return "Drenaż opaskowy: " + op


def dl_trasy(p) -> float | None:
    """Długość trasy przyłącza z geometrii modelu (jak na rys. PZT-03); pole ``dl`` — tylko gdy brak geometrii."""
    ln = p.get("linia") or []
    return LineString(ln).length if len(ln) >= 2 else p.get("dl")


def opis_obiektu(z, o) -> str:
    """Opis urządzenia z modelu bez adnotacji roboczych; odległości od granic liczone z geometrii (układ działki)."""
    import re
    from shapely.geometry import Point
    t = czysc(o.get("opis", "—"))
    if o.get("xy"):
        def odl(m):
            g = next((g for g in z.granice if g["kier"] == m.group(2)), None)
            return f"{L(Point(*o['xy']).distance(g['line']))} m od granicy {m.group(2)}" if g else m.group(0)
        t = re.sub(r"(\d+(?:,\d+)?) m od granicy ([NESW])\b", odl, t)
    return t


def _brama(z, typ):
    return next((b for b in z.dz.get("bramy") or [] if b.get("typ") == typ), None)


def wstep(zp, z, d):
    zp.markdown(f"""
    Opis sporządzono w zakresie określonym w § 14 rozporządzenia Ministra Rozwoju z dnia 11 września 2020 r.
    w sprawie szczegółowego zakresu i formy projektu budowlanego (t.j. Dz.U. 2022 poz. 1679, zm. Dz.U. 2023 poz. 2405
    i Dz.U. 2026 poz. 597) — dalej **RPB**. Wymagania techniczno-budowlane przyjęto wg rozporządzenia Ministra
    Infrastruktury w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (t.j. Dz.U. 2022
    poz. 1225 ze zm.) — dalej **WT** — w brzmieniu obowiązującym do 19.09.2026 r., stosowanego na podstawie art. 102a
    ust. 1 ustawy – Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.) — dalej **PB** — w związku z oświadczeniem
    Inwestora ({do_uzup('data złożenia oświadczenia z art. 102a PB')}; wzór — ZL).

    Działka, ustalenia miejscowego planu zagospodarowania przestrzennego (MPZP), uzbrojenie terenu i warunki gruntowe
    są danymi przykładowymi {DANE_PRZYKLADOWE}. Wartości liczbowe opisu wygenerowano z modelu projektu
    (`model/budynek.yaml`, `model/dzialka.yaml`) i obliczeń (`lamela.wskazniki`, audyt WT, `lamela.obliczenia`).
    Rzędne w układzie wysokościowym PL-EVRF2007-NH; ±0,00 = {L(z.zero)} m n.p.m. Rysunki: PZT-01 (plan
    zagospodarowania, 1:500), PZT-02 (plan szczegółowy — wymiary i rzędne, 1:200), PZT-03 (rysunek koordynacyjny
    uzbrojenia terenu, 1:200).

    {LEGENDA}
    """)


# ------------------------------------------------------------------------------------------------ § 14 pkt 1
def pkt1(zp, z, d):
    kn = z.w("kondygnacje_nadziemne")
    kond = ", ".join(k.nazwa if k.nazwa.split()[0].isupper() else k.nazwa[0].lower() + k.nazwa[1:]
                     for k in z.m.kondygnacje)
    mp = z.dz.get("miejsca_postojowe") or []
    n_gar = sum(1 for x in mp if x.get("typ") == "garaz")
    n_zew = sum(1 for x in mp if x.get("typ") != "garaz")
    dr = z.droga()
    ret = z.dz.get("retencja") or {}
    zb, ro = ret.get("zbiornik") or {}, ret.get("rozsaczanie") or {}
    niecka = _poly(ro.get("obrys"))
    br, fu = _brama(z, "przesuwna"), _brama(z, "furtka")
    proj = (z.dz.get("uzbrojenie") or {}).get("projektowane") or []
    naz = {"woda": "wodociągowe", "kan_sanit": "kanalizacji sanitarnej", "en": "elektroenergetyczne nN",
           "tele": "telekomunikacyjne (kanalizacja kablowa ze światłowodem)"}
    przyl = [naz[b] for b in dict.fromkeys(p["branza"] for p in proj) if b in naz]
    gaz = any(p.get("branza") == "gaz" for p in (z.dz.get("uzbrojenie") or {}).get("istniejace") or []) \
        and not any(p.get("branza") == "gaz" for p in proj)
    sep, skp = z.obiekt("SEP-1"), z.obiekt("SK-PC")
    tar = list(z.m.tarasy())
    drz_n = sum(1 for t in z.drzewa() if not t.get("istn"))
    zp.rozdzial("Przedmiot zamierzenia", f"""
    Przedmiotem zamierzenia budowlanego jest **budowa budynku mieszkalnego jednorodzinnego wolnostojącego
    „{d['nazwa_krotka']}”** (PB art. 3 pkt 2a) — {kn} kondygnacje nadziemne ({kond}), bez podpiwniczenia, z garażem
    {n_gar}-stanowiskowym w bryle parteru — wraz z zagospodarowaniem działki nr ewid. {d['dzialka']['nr']}
    i urządzeniami budowlanymi związanymi z budynkiem (PB art. 3 pkt 9). Zamierzenie obejmuje jeden obiekt budowlany;
    zakres całego zamierzenia:

    1. budynek mieszkalny jednorodzinny z garażem w bryle — obiekt kategorii {d['kategoria']} (załącznik do PB);
    2. zjazd z drogi publicznej {dr['symbol']} ({dr['nazwa']}) — w zakresie i na warunkach zezwolenia zarządcy drogi
       (u.d.p. art. 29 ust. 1, 3a; ZL);
    3. podjazd ({_naw(z, 'U1')}), dojście ({_naw(z, 'U2')}),
       {n_zew} stanowiska postojowe naziemne dla gości;
    4. tarasy i podesty naziemne ({len(tar)} szt., łącznie {L(z.w('pow_tarasow'))} m²);
    5. stanowisko pojemników na odpady — {(z.dz.get('odpady') or {}).get('opis', '—').split(';')[0]};
    6. zagospodarowanie wód opadowych: szczelny zbiornik retencyjny {L(zb.get('V', 0), 1)} m³, niecka chłonna
       (ogród deszczowy) {L(niecka.area if niecka is not None else 0, 1)} m², osadnik z separatorem substancji
       ropopochodnych {sep['id'] if sep else '—'}, odwodnienia liniowe, kanalizacja deszczowa na działce;
    7. fundament jednostki zewnętrznej pompy ciepła i studnia chłonna skroplin {skp['id'] if skp else '—'};
    8. ogrodzenie z bramą przesuwną ({L(br['szer'])} m) i furtką ({L(fu['szer'])} m);
    9. przyłącza: {', '.join(przyl)} — wg warunków przyłączenia gestorów sieci {do_uzup('nr i data warunków przyłączenia (E-05)')};
       {'przyłącza gazowego nie projektuje się — budynek bez instalacji gazowej (ogrzewanie i c.w.u. z pompy ciepła)' if gaz else ''};
    10. zieleń: trawniki, żywopłoty, rabaty, {drz_n} drzew projektowanych; zachowanie drzew istniejących.
    """, podstawa="§ 14 pkt 1 RPB")


# ------------------------------------------------------------------------------------------------ § 14 pkt 2
def pkt2(zp, z, d):
    t = z.teren_istn()
    a, b = z.wymiary_dzialki()
    dr = z.droga()
    sas = [s for s in z.sasiedzi() if s["przylega"]]
    ist = [t_ for t_ in z.drzewa() if t_.get("istn")]
    wyc = [t_ for t_ in z.drzewa() if t_.get("do_wyciecia")]
    siec = (z.dz.get("uzbrojenie") or {}).get("istniejace") or []
    zp.rozdzial("Istniejący stan zagospodarowania działki", f"""
    Działka nr ewid. {d['dzialka']['nr']}, obręb {d['dzialka']['obreb']}, gm. {d['dzialka']['gmina']}, ma kształt
    prostokąta {L(a)} × {L(b)} m o powierzchni {L(z.w('pow_dzialki'))} m² {DANE_PRZYKLADOWE}. Działka jest
    **niezabudowana; brak obiektów budowlanych przeznaczonych do rozbiórki**. Teren jest płaski: rzędne terenu
    istniejącego w granicach działki {L(t['z_min'])}–{L(t['z_max'])} m n.p.m. ({t['n']} punktów wysokościowych),
    spadek ok. {L(t['spadek_y'], 1)} % ku {t['ku_y']} i ok. {L(t['spadek_x'], 1)} % ku {t['ku_x']}.
    Grunt: {(z.dz.get('teren') or {}).get('grunt', '—')} {DANE_PRZYKLADOWE}.

    Otoczenie: od północy droga publiczna gminna {dr['symbol']} — {dr['nazwa']}, w liniach rozgraniczających
    {L(dr['szer_lr'])} m, jezdnia {dr['nawierzchnia']} szer. {L(dr['szer_jezdni'])} m;
    """ + "; ".join(f"działka nr {s['nr']} — {s['opis']}" for s in sas) + "." + f"""

    Zieleń istniejąca: {len(ist)} drzew{'a' if 1 < len(ist) < 5 else ''} ({'; '.join(_gat(t_) for t_ in ist) or 'brak'}),
    zachowywane; drzew i krzewów do usunięcia: {len(wyc) or 'brak'}. Uzbrojenie istniejące w pasie drogi
    {dr['symbol']}: {'; '.join(s['opis'] for s in siec)} {DANE_PRZYKLADOWE}. Stan istniejący — na mapie do celów
    projektowych {do_uzup('mapa do celów projektowych z klauzulą urzędową lub oświadczeniem geodety (E-01)')} (rys. PZT-01).
    """, podstawa="§ 14 pkt 2 RPB")


# ------------------------------------------------------------------------------------------------ § 14 pkt 3
def _kr(s, n=1):
    """Pierwsze ``n`` członów opisu z modelu (do przecinka/średnika) — skrót do tabeli."""
    import re
    return "; ".join(re.split(r"[;(]", str(s))[:n]).strip(" ,")


def pkt3(zp, z, d):
    zp.rozdzial("Projektowane zagospodarowanie działki", podstawa="§ 14 pkt 3 RPB")
    pkt3_ab(zp, z, d)
    pkt3_cd(zp, z, d)
    pkt3_ef(zp, z, d)


def pkt3_ab(zp, z, d):
    ob = [o for o in (z.dz.get("uzbrojenie") or {}).get("obiekty") or [] if o.get("id") != "HYDR"]
    ret = z.dz.get("retencja") or {}
    rows = [{"Element": o["id"], "Opis": opis_obiektu(z, o)} for o in ob]
    rows += [{"Element": "zbiornik retencyjny", "Opis": czysc((ret.get("zbiornik") or {}).get("opis", "—"))},
             {"Element": "niecka chłonna", "Opis": czysc((ret.get("rozsaczanie") or {}).get("opis", "—"))}]
    og = z.ogrodzenie_od_drogi()
    rows += [{"Element": "ogrodzenie od drogi", "Opis": f"{og[0]['typ'].split(',')[0]}; h = {L(max(o['wys'] for o in og if o['od_drogi']))} m; "
              f"łącznie {L(sum(o['dl'] for o in og if o['od_drogi']))} m"} if any(o["od_drogi"] for o in og) else {},
             {"Element": "ogrodzenie pozostałe", "Opis": "; ".join(f"{o['typ']}, h = {L(o['wys'])} m, {L(o['dl'])} m"
                                                           for o in og if not o["od_drogi"])}]
    rows += [{"Element": "furtka" if b["typ"] == "furtka" else f"brama {b['typ']}", "Opis": f"szer. w świetle {L(b['szer'])} m, h = {L(b['wys'])} m"}
             for b in z.dz.get("bramy") or []]
    rows += [{"Element": "stanowisko pojemników", "Opis": czysc((z.dz.get("odpady") or {}).get("opis", "—"))}]
    zp.markdown("## Urządzenia budowlane związane z budynkiem {podstawa: § 14 pkt 3 lit. a}\n"
                "Urządzenia budowlane (PB art. 3 pkt 9) projektowane na działce — położenie na rys. PZT-01 i PZT-03:")
    zp.tabela([r for r in rows if r], tytul="Urządzenia budowlane (z modelu `dzialka.yaml`)", lp=True,
              szerokosci=["9mm", "34mm", None], zrodlo="model/dzialka.yaml — uzbrojenie.obiekty, retencja, ogrodzenie, bramy, odpady")
    k = z.inst["kanalizacja"]
    prz = next((o for o in k.odcinki if o.rodzaj == "przykanalik"), None)
    ks = next((p for p in (z.dz.get("uzbrojenie") or {}).get("projektowane") or [] if p["branza"] == "kan_sanit"), {})
    sr = z.obiekt("SR1") or {}
    ks_ist = next((p for p in (z.dz.get("uzbrojenie") or {}).get("istniejace") or [] if p["branza"] == "kan_sanit"), {})
    kd = [p for p in (z.dz.get("uzbrojenie") or {}).get("projektowane") or [] if p["branza"] == "kan_deszcz"]
    dsz = z.inst["deszczowa"]
    zp.markdown(f"""
    ## Sposób odprowadzania ścieków i wód opadowych {{podstawa: § 14 pkt 3 lit. b}}
    **Ścieki bytowe** — grawitacyjnie do sieci kanalizacji sanitarnej ({ks_ist.get('opis', '—')}) w drodze
    {z.droga()['symbol']}: przykanalik {prz.rura if prz else '—'} o spadku {L(100 * prz.i, 1) if prz else '—'} %
    [ZAŁ — warunki gestora], ze studzienką rewizyjną SR1 ({czysc(sr.get('opis', '—'))}); długość trasy na działce
    i w pasie drogowym {L(dl_trasy(ks) or 0, 1)} m (rys. PZT-03).
    Ścieki przemysłowe nie powstają.

    **Wody opadowe i roztopowe** — zagospodarowane w całości w granicach działki (MPZP 3MN; WT § 28 ust. 2 [W-145]).
    Dachy o łącznej powierzchni rzutu {L(dsz.do_dict()['A_dachow_m2'], 1)} m² (przepływ obliczeniowy
    {L(dsz.do_dict()['Q_dachy_l_s'])} l/s, PN-EN 12056-3) odwadniane rurami spustowymi do kolektorów kanalizacji
    deszczowej na działce ({len(kd)} odcinków, łącznie {L(sum(dl_trasy(p) or 0 for p in kd), 1)} m) i dalej do szczelnego
    zbiornika retencyjnego z przelewem do niecki chłonnej (obliczenie retencji — rozdział opisu wg § 14 pkt 7 RPB). Wody z podjazdu i posadzki garażu
    (możliwe węglowodory) — odwodnieniami liniowymi przez osadnik z separatorem do niecki trawiastej, z pominięciem
    zbiornika. Skropliny pompy ciepła — do studni chłonnej. Wody opadowe nie są odprowadzane na drogę ani
    na działki sąsiednie (odwodnienie liniowe przy bramie wjazdowej; spadki terenu — lit. f).
    """)


def pkt3_cd(zp, z, d):
    u1 = _poly(_utw(z, "U1").get("obrys"))
    x0, y0, x1, y1 = u1.bounds if u1 is not None else (0, 0, 0, 0)
    szer_min, _, _ = z.wym("usytuowanie", "dojazd_szer_min")
    st_s, zr_st, _ = z.wym("usytuowanie", "stanowisko_szer")
    st_d, _, _ = z.wym("usytuowanie", "stanowisko_dl")
    gr_mp, zr_gr, _ = z.wym("usytuowanie", "parking_odl_granica_min")
    br, fu = _brama(z, "przesuwna"), _brama(z, "furtka")
    br_min, zr_br, _ = z.wym("usytuowanie", "brama_wjazdowa_szer_min")
    fu_min, _, _ = z.wym("usytuowanie", "furtka_szer_min")
    zj, zr_zj, _ = z.wym("usytuowanie", "zjazd_szer_zalozenie")
    dr = z.droga()
    zp.markdown(f"""
    ## Układ komunikacyjny {{podstawa: § 14 pkt 3 lit. c}}
    Wjazd bramą przesuwną w ogrodzeniu od drogi {dr['symbol']}; podjazd przed garażem szer. {L(x1 - x0)} m
    i dł. {L(y1 - y0)} m (nawierzchnia: {_naw(z, 'U1')}, spadek {L(100 * _utw(z, 'U1').get('spadek', 0), 1)} %
    od budynku) — dojazd szerszy od wymaganego {L(szer_min)} m ({z.wym('usytuowanie', 'dojazd_szer_min')[1]}).
    Dojście piesze od furtki do wejścia głównego: {_naw(z, 'U2')}. Stanowiska postojowe:
    """)
    rows = [{"Stanowisko": i, "Rodzaj": "w garażu" if t == "garaz" else "naziemne, niezadaszone",
             "Wymiary [m]": f"{L(a)} × {L(b)}", "Odl. od granic niedrogowych [m]": dd,
             "Ocena": "spełnia" if (a >= st_s - 1e-6 and b >= st_d - 1e-6 and (t == "garaz" or dd >= gr_mp - 1e-6)) else "NIE SPEŁNIA"}
            for i, t, (a, b), dd in z.mp_odleglosci()]
    zp.tabela(rows, tytul="Stanowiska postojowe", lp=True, formaty={"Odl. od granic niedrogowych [m]": 2},
              uwagi=[f"Stanowisko ≥ {L(st_s)} × {L(st_d)} m — {zr_st}; odległość stanowisk naziemnych od granicy działki "
                     f"≥ {L(gr_mp)} m — {zr_gr}. Liczba stanowisk a MPZP — pkt 4."])
    zp.markdown(f"""
    ## Sposób dostępu do drogi publicznej {{podstawa: § 14 pkt 3 lit. d}}
    Dostęp do drogi publicznej gminnej {dr['symbol']} ({dr['nazwa']}) — **projektowanym zjazdem indywidualnym**
    w osi bramy wjazdowej, na podstawie zezwolenia zarządcy drogi na lokalizację zjazdu (u.d.p. art. 29 ust. 1;
    zezwolenie dołącza się do wniosku o pozwolenie na budowę — art. 29 ust. 3a; ZL) {do_uzup('nr i data zezwolenia zarządcy drogi')}.
    Parametry zjazdu przyjęto wstępnie: szerokość jezdni zjazdu {L(zj)} m {ZAL} ({zr_zj}); ostateczne — wg zezwolenia;
    PZT w zakresie zjazdu podlega uzgodnieniu z zarządcą drogi (u.d.p. art. 29 ust. 3 pkt 2; strona zastępcza — ZL). Roboty w pasie drogowym
    — po uzyskaniu zezwolenia zarządcy drogi na ich prowadzenie (u.d.p. art. 29 ust. 3 pkt 1 lit. b).
    Brama przesuwna {L(br['szer'])} m ≥ {L(br_min)} m, furtka {L(fu['szer'])} m ≥ {L(fu_min)} m ({zr_br}).
    """)


def pkt3_ef(zp, z, d):
    proj = (z.dz.get("uzbrojenie") or {}).get("projektowane") or []
    naz = {"woda": "wodociąg", "kan_sanit": "kanalizacja sanitarna", "kan_deszcz": "kanalizacja deszczowa",
           "en": "elektroenergetyczna nN", "tele": "telekomunikacyjna"}
    zp.markdown("""
    ## Parametry techniczne sieci i urządzeń uzbrojenia terenu {podstawa: § 14 pkt 3 lit. e}
    Przebieg przyłączy i sieci na działce — rys. PZT-03 (rysunek koordynacyjny); parametry z modelu:
    """)
    zp.tabela([{"Branża": naz.get(p["branza"], p["branza"]), "Parametry (model)": czysc(p.get("opis", "—")),
                "Długość [m]": dl_trasy(p)} for p in proj], tytul="Projektowane przyłącza i przewody na działce",
              lp=True, formaty={"Długość [m]": 1}, szerokosci=["9mm", "30mm", None, "20mm"],
              uwagi=["Średnice, spadki i rzędne w punktach załamania i włączenia — rys. PZT-03 oraz PT-3 IS / PT-4 IE; "
                     "parametry przyłączy wg warunków przyłączenia " + do_uzup("warunki przyłączenia: ENEA Operator (nN), "
                     "gestor wod.-kan., operator telekomunikacyjny — E-05") + ". Długości — z geometrii tras w modelu "
                     "(rys. PZT-03), w granicach działki i w pasie drogowym do punktu włączenia."],
              zrodlo="model/dzialka.yaml — uzbrojenie.projektowane")
    t, tp = z.teren_istn(), z.teren_proj()
    sp_min, zr_sp, id_sp = z.wym("usytuowanie", "spadek_terenu_od_budynku_min")
    tsr = z.W["wysokosc_zabudowy"].get("t_sr")
    odw = z.dz.get("odwodnienia") or []
    drn = next((o for o in odw if o.get("typ") == "drenaz_opaskowy"), None)
    zp.markdown(f"""
    ## Ukształtowanie terenu i układ zieleni {{podstawa: § 14 pkt 3 lit. f}}
    Projektuje się niwelację terenu wyłącznie w otoczeniu budynku i utwardzeń: rzędne terenu projektowanego
    {L(tp.get('z_min', 0))}–{L(tp.get('z_max', 0))} m n.p.m. (teren istniejący {L(t['z_min'])}–{L(t['z_max'])} m n.p.m.);
    posadzka parteru ±0,00 = {L(z.zero)} m n.p.m., tj. {L(z.zero - tsr)} m ponad średni poziom terenu przy budynku.
    Teren przy budynku ze spadkiem ≥ {L(100 * sp_min, 0)} % od ścian ({zr_sp}; {id_sp}), opaska żwirowa wokół budynku
    ({L(z.w('pow_opaski'), 1)} m²), odwodnienia liniowe przy drzwiach bezprogowych, przed garażem i przy bramie;
    na granicach działki rzędne projektowane równe istniejącym. {_drenaz(drn)}.
    Rzędne — rys. PZT-02.
    """)
    zp.tabela([{"Symbol": o["id"], "Rodzaj": o.get("typ", "—").replace("_", " "), "Opis": czysc(_kr(o.get("opis"), 1)),
                "Odbiornik": o.get("odbiornik", "—")} for o in odw if o.get("typ") != "drenaz_opaskowy"],
              tytul="Odwodnienie powierzchniowe", szerokosci=["14mm", "20mm", None, "32mm"],
              zrodlo="model/dzialka.yaml — odwodnienia")
    zp_ = z.zielen_pow()
    zp.markdown(f"""
    Zieleń: trawniki (pozostała powierzchnia biologicznie czynna — pkt 4), żywopłoty na granicach bocznych i tylnej
    ({L(zp_.get('zywoplot', 0), 1)} m²), rabaty ({L(zp_.get('rabata', 0), 1)} m²), niecka chłonna jako ogród deszczowy.
    Drzewa:
    """)
    zp.tabela([{"Nr": t_["id"], "Gatunek": _gat(t_), "Stan": "istniejące — zachowane" if t_.get("istn") and not t_.get("do_wyciecia")
                else ("do usunięcia" if t_.get("do_wyciecia") else "projektowane"),
                "Średnica korony [m]": t_.get("sr_korony"), "Wysokość [m]": t_.get("wys")} for t_ in z.drzewa()],
              tytul="Drzewa istniejące i projektowane", formaty={"Średnica korony [m]": 1, "Wysokość [m]": 1},
              uwagi=["Przy drzewach zachowywanych — ochrona pni i systemu korzeniowego w zasięgu korony podczas robót. "
                     "Obwody pni drzew istniejących " + do_uzup("obwód na wys. 5 cm — mapa do celów projektowych (u.o.p. art. 83f)") + "."])
