"""PZT — część opisowa, RPB § 14 pkt 1–3 (przedmiot zamierzenia, stan istniejący, projektowane zagospodarowanie).
Wszystkie liczby z ``DaneZag`` (model, wskaźniki, audyt A1, obliczenia) — przy zmianie modelu tekst się aktualizuje."""
from __future__ import annotations

from shapely.geometry import LineString

from lamela.dokumenty import DANE_PRZYKLADOWE, ZAL, do_uzup, liczba

from pzt_dane import _poly


def L(v, nd=2):
    return liczba(v, nd)


def _utw(z, uid):
    return next((u for u in z.dz.get("utwardzenia") or [] if u.get("id") == uid), {})


def _brama(z, typ):
    return next((b for b in z.dz.get("bramy") or [] if b.get("typ") == typ), None)


def wstep(zp, z, d):
    zp.markdown(f"""
    Opis sporządzono w zakresie określonym w § 14 rozporządzenia Ministra Rozwoju, Pracy i Technologii w sprawie
    szczegółowego zakresu i formy projektu budowlanego (t.j. Dz.U. 2022 poz. 1679, zm. Dz.U. 2023 poz. 2405
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
    """)


# ------------------------------------------------------------------------------------------------ § 14 pkt 1
def pkt1(zp, z, d):
    kn = z.w("kondygnacje_nadziemne")
    kond = ", ".join(k.nazwa.lower() for k in z.m.kondygnacje)
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
    gaz = next((p for p in (z.dz.get("uzbrojenie") or {}).get("istniejace") or [] if p.get("branza") == "gaz"), None)
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
    3. podjazd ({_utw(z, 'U1').get('nawierzchnia', '—')}), dojście ({_utw(z, 'U2').get('nawierzchnia', '—')}),
       {n_zew} stanowiska postojowe naziemne dla gości;
    4. tarasy i podesty naziemne ({len(tar)} szt., łącznie {L(z.w('pow_tarasow'))} m²);
    5. stanowisko pojemników na odpady — {(z.dz.get('odpady') or {}).get('opis', '—').split(';')[0]};
    6. zagospodarowanie wód opadowych: szczelny zbiornik retencyjny {L(zb.get('V', 0), 1)} m³, niecka chłonna
       (ogród deszczowy) {L(niecka.area if niecka is not None else 0, 1)} m², osadnik z separatorem substancji
       ropopochodnych {sep['id'] if sep else '—'}, odwodnienia liniowe, kanalizacja deszczowa na działce;
    7. fundament jednostki zewnętrznej pompy ciepła i studnia chłonna skroplin {skp['id'] if skp else '—'};
    8. ogrodzenie z bramą przesuwną ({L(br['szer'])} m) i furtką ({L(fu['szer'])} m);
    9. przyłącza: {', '.join(przyl)} — wg warunków przyłączenia gestorów sieci {do_uzup('nr i data warunków przyłączenia (E-05)')};
       {('gazu nie przyłącza się (' + gaz['opis'].split('—')[-1].strip() + ')') if gaz else ''};
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
    """ + "".join(f"działka nr {s['nr']} — {s['opis']}; " for s in sas) + f"""

    Zieleń istniejąca: {len(ist)} drzew{'a' if 1 < len(ist) < 5 else ''} ({'; '.join(t_['gat'] for t_ in ist) or 'brak'}),
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
    rows = [{"Element": o["id"], "Opis": _kr(o.get("opis"), 2)} for o in ob]
    rows += [{"Element": "zbiornik retencyjny", "Opis": _kr((ret.get("zbiornik") or {}).get("opis"), 2)},
             {"Element": "niecka chłonna", "Opis": _kr((ret.get("rozsaczanie") or {}).get("opis"), 1)}]
    og = z.ogrodzenie_od_drogi()
    rows += [{"Element": "ogrodzenie od drogi", "Opis": f"{og[0]['typ'].split(',')[0]}; h = {L(max(o['wys'] for o in og if o['od_drogi']))} m; "
              f"łącznie {L(sum(o['dl'] for o in og if o['od_drogi']))} m"} if any(o["od_drogi"] for o in og) else {},
             {"Element": "ogrodzenie pozostałe", "Opis": "; ".join(f"{o['typ']}, h = {L(o['wys'])} m, {L(o['dl'])} m"
                                                           for o in og if not o["od_drogi"])}]
    rows += [{"Element": f"{b['typ']}", "Opis": f"szer. w świetle {L(b['szer'])} m, h = {L(b['wys'])} m"}
             for b in z.dz.get("bramy") or []]
    rows += [{"Element": "stanowisko pojemników", "Opis": _kr((z.dz.get("odpady") or {}).get("opis"), 1)}]
    zp.markdown("## Urządzenia budowlane związane z budynkiem {podstawa: § 14 pkt 3 lit. a}\n"
                "Urządzenia budowlane (PB art. 3 pkt 9) projektowane na działce — położenie na rys. PZT-01 i PZT-03:")
    zp.tabela([r for r in rows if r], tytul="Urządzenia budowlane (z modelu `dzialka.yaml`)", lp=True,
              szerokosci=["7mm", "38mm", None], zrodlo="model/dzialka.yaml — uzbrojenie.obiekty, retencja, ogrodzenie, bramy, odpady")
    k = z.inst["kanalizacja"]
    prz = next((o for o in k.odcinki if o.rodzaj == "przykanalik"), None)
    ks = next((p for p in (z.dz.get("uzbrojenie") or {}).get("projektowane") or [] if p["branza"] == "kan_sanit"), {})
    ks_ist = next((p for p in (z.dz.get("uzbrojenie") or {}).get("istniejace") or [] if p["branza"] == "kan_sanit"), {})
    kd = [p for p in (z.dz.get("uzbrojenie") or {}).get("projektowane") or [] if p["branza"] == "kan_deszcz"]
    dsz = z.inst["deszczowa"]
    zp.markdown(f"""
    ## Sposób odprowadzania ścieków i wód opadowych {{podstawa: § 14 pkt 3 lit. b}}
    **Ścieki bytowe** — grawitacyjnie do sieci kanalizacji sanitarnej ({ks_ist.get('opis', '—')}) w drodze
    {z.droga()['symbol']}: przykanalik {prz.rura if prz else '—'} o spadku {L(100 * prz.i, 1) if prz else '—'} %
    [ZAŁ — warunki gestora], {_kr(ks.get('opis'), 2)}; długość trasy na rysunku {L(ks.get('dl', 0), 1)} m.
    Ścieki przemysłowe nie powstają.

    **Wody opadowe i roztopowe** — zagospodarowane w całości w granicach działki (MPZP 3MN; WT § 28 ust. 2 [W-145]).
    Dachy o łącznej powierzchni rzutu {L(dsz.do_dict()['A_dachow_m2'], 1)} m² (przepływ obliczeniowy
    {L(dsz.do_dict()['Q_dachy_l_s'])} l/s, PN-EN 12056-3) odwadniane rurami spustowymi do kolektorów kanalizacji
    deszczowej na działce ({len(kd)} odcinków, łącznie {L(sum(p.get('dl', 0) for p in kd), 1)} m) i dalej do szczelnego
    zbiornika retencyjnego z przelewem do niecki chłonnej (obliczenie — pkt 7). Wody z podjazdu i posadzki garażu
    (możliwe węglowodory) — odwodnieniami liniowymi przez osadnik z separatorem do niecki trawiastej, z pominięciem
    zbiornika. Skropliny pompy ciepła — do studni chłonnej. Wody opadowe nie są odprowadzane na drogę ani
    na działki sąsiednie (odwodnienie liniowe przy bramie wjazdowej; spadki terenu — lit. f).
    """)
