"""PAB — rozdziały 5–9 (RPB § 20 ust. 1 pkt 5–9). Liczby wyłącznie z ``DanePAB`` (model, obliczenia, rejestr)."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, do_uzup, liczba as L
from lamela.dokumenty.znaczniki import INT
from redakcja import liczby_pl

import re

from pab_opis_a import ok, tyt
from redakcja import czysc as _czysc_red


def czysc(txt: str) -> str:
    """Usuwa z opisów modelu odsyłacze do wewnętrznych audytów (A1–A3, J1–J3, K-n) i inne adnotacje robocze
    (``redakcja.czysc``); zostawia id rejestru W-xxx."""
    t = re.sub(r"\b(?:A\d|J\d) [A-Z]-?\d+;?\s*", "", str(txt))
    t = re.sub(r"\((?:\s*;?\s*)\)", "", t)
    return _czysc_red(re.sub(r"\s{2,}", " ", t).strip())


def przykanalik(D) -> str:
    """Przykanalik z obliczeń kanalizacji (ten sam odcinek co w opisie PZT): rura i spadek."""
    k = D.W["kanalizacja"]
    prz = next((o for o in getattr(k, "odcinki", []) or [] if o.rodzaj == "przykanalik"), None)
    return f"{prz.rura}, i = {L(100 * prz.i, 1)} %" if prz else liczby_pl(D.Wd["kanalizacja"].get("przykanalik", "—"))


def niecka(D) -> dict:
    """Niecka chłonna z modelu (dzialka.yaml: retencja.rozsaczanie) — powierzchnia i pojemność projektowana."""
    from lamela.model import make_polygon
    ro = ((D.Dz.get("retencja") or {}).get("rozsaczanie") or {})
    ob = ro.get("obrys") or []
    A = make_polygon(ob).area if len(ob) >= 3 else 0.0
    h = float(ro.get("glebokosc") or 0.0)
    return dict(A=A, h=h, V=A * h)


def dane_posadowienia(D) -> dict:
    """Parametry posadowienia z modelu: płyta, żebra, XPS, izolacja obwodowa, głębokość względem terenu, mostek cokołu."""
    m, geo = D.m, (D.B.get("geotechnika") or {})
    fu = m.fundamenty()
    el = fu.get("elementy") or []
    plyty = [e for e in el if "obrys" in e]
    zebra = [e for e in el if "os" in e and str(e.get("id", "")).startswith("ZF")]
    stopy = [e for e in el if "os" in e and str(e.get("id", "")).startswith("SF")]
    obw = [e for e in zebra if "krawędź" in str(e.get("uwagi", ""))]
    pod = m.przegroda(str(m.kondygnacje[0].podloga))
    xps = next((w for w in (pod.warstwy if pod else []) if "XPS" in w.mat), None)
    t_min_rel = D.w["wysokosc_zabudowy"]["t_min"] - float(m.zero_abs)
    spod_obw = max((float(e["spod"]) for e in obw), default=None)          # najpłytszy spód żebra obwodowego
    io = fu.get("izolacja_obwodowa") or {}
    mio = m.material(str(io.get("mat")))
    lam_io = mio.lambda_ if mio is not None else None
    cok = next((dict(id=k, **v) for k, v in D.mostki.items() if v.get("typ") == "sciana_grunt"), None)
    return dict(geo=geo, plyty=plyty, zebra=zebra, stopy=stopy, obw=obw, xps=xps, t_min_rel=t_min_rel,
                gl_obw=(t_min_rel - spod_obw) if spod_obw is not None else None, io=io, lam_io=lam_io,
                R_io=(io.get("d_n") / lam_io) if io.get("d_n") and lam_io else None, cokol=cok,
                zwg=abs(float(geo.get("ZWG"))) if geo.get("ZWG") is not None else None)


def r05(pab, D, d):
    P = dane_posadowienia(D)
    g, gr = P["geo"], (P["geo"].get("grunt") or {})
    dr = D.Wd["drenaz"]
    pl = P["plyty"]
    zb_b = sorted({(e["b"], e["h"]) for e in P["zebra"]})
    frsi_min = D.v("energia", "fRsi_min")
    pab.rozdzial(tyt("Opinia geotechniczna oraz informacja o sposobie posadowienia", 5))
    pab.markdown(f"""
    ## Opinia geotechniczna

    Opinię geotechniczną (rozp. Dz.U. 2012 poz. 463 § 7 ust. 1, § 8) przedstawiono w **pkt 5.3** opisu
    {DANE_PRZYKLADOWE}. Ustalenia opinii: podłoże — {gr.get('rodzaj', '—')} (I_{{D}} ≈ {L(gr.get('I_D'), 2)}), pod warstwą
    gleby o miąższości ok. {L(g.get('humus'), 2)} m; zwierciadło wody gruntowej ok. {L(P['zwg'], 2)} m p.p.t., poniżej
    poziomu posadowienia; warunki gruntowe proste (§ 4 ust. 2 pkt 1); grunty przydatne do bezpośredniego posadowienia.
    **Kategoria geotechniczna: {g.get('kategoria', do_uzup('kategoria'))}** (§ 4 ust. 3 pkt 2 lit. a — fundamenty bezpośrednie;
    budynek ma {D.w['kondygnacje_nadziemne']['wartosc']} kondygnacje nadziemne i statycznie niewyznaczalny układ stropów
    monolitycznych ze wspornikami, więc nie mieści się w opisie kategorii pierwszej z § 4 ust. 3 pkt 1 lit. a).
    Dla kategorii drugiej w projekcie technicznym (PT-2 BO) opracowuje się dodatkowo dokumentację badań podłoża
    gruntowego i projekt geotechniczny (§ 7 ust. 2; W-281); dokumentacja geologiczno-inżynierska nie jest wymagana
    (§ 7 ust. 3 — warunki proste).

    ## Sposób posadowienia

    Posadowienie bezpośrednie na **żelbetowej płycie fundamentowej** grubości {L(pl[0]['h'], 2) if pl else '—'} m
    ({(D.m.material(pl[0]['mat']).nazwa.split(' (')[0] if pl and D.m.material(pl[0]['mat']) else '—')}), ułożonej na warstwie polistyrenu
    ekstrudowanego grubości {L(P['xps'].d, 2) if P['xps'] else '—'} m, z pogrubieniami (żebrami) pod ścianami nośnymi
    ({'; '.join(f'{L(b, 2)} × {L(h, 2)} m' for b, h in zb_b)}) i pod słupami fasady ({len(P['stopy'])} szt.; przebicie).
    Płyta pod garażem obniżona względem części mieszkalnej (uskok w linii ściany dom–garaż). Wokół płyty
    przeciwprzemarzaniowa izolacja obwodowa z XPS: {L(P['io'].get('d_n'), 2)} m × {L(P['io'].get('D'), 2)} m
    (R = {L(P['R_io'], 2)} m²·K/W ≥ {L(D.v('energia', 'R_izolacji_obwodowej_min'), 1)} — {D.zr('energia', 'R_izolacji_obwodowej_min')};
    PN-EN ISO 13793). Spód żeber obwodowych leży ok. {L(P['gl_obw'], 2)} m poniżej najniższej rzędnej terenu przy budynku,
    tj. płycej niż głębokość przemarzania h_{{z}} = {L(g.get('h_z'), 2)} m ({D.zr('geotechnika', 'h_z')}) — ochronę przed
    przemarzaniem zapewnia izolacja obwodowa w połączeniu z niewysadzinowym podłożem piaszczystym (W-284 — wariant płyty
    z izolacją obwodową wg PN-EN ISO 13793). Szczegóły: rzuty i przekroje PAB, projekt
    geotechniczny i obliczenia PT-2 BO.

    **Uzasadnienie wyboru płyty na XPS zamiast ław fundamentowych:**

    1. *Ciągłość izolacji termicznej* pod całą kubaturą ogrzewaną: węzeł cokołu ściana–płyta
       {P['cokol']['id'] if P['cokol'] else ''} — Ψ_{{oi}} = {L(P['cokol']['psi_oi'], 3) if P['cokol'] else '—'} W/(m·K),
       f_{{Rsi}} = {L(P['cokol']['f_rsi'], 3) if P['cokol'] else '—'} ≥ {L(frsi_min, 2)} ({D.zr('energia', 'fRsi_min')}) —
       symulacja PN-EN ISO 10211 (`projekt/08_obliczenia/mostki`).
    2. *Warunki gruntowo-wodne:* piaski nośne i przepuszczalne, woda gruntowa głęboko — drenaż opaskowy
       **{str(dr.get('drenaz_opaskowy', '—')).lower()}** (klasa oddziaływania wody: {dr.get('klasa_oddzialywania_wody', '—')};
       obliczenia `lamela.obliczenia.sanitarne.drenaz`; W-285).
    3. *Rozkład obciążeń:* siły skupione ze słupów fasady południowej i obciążenia nierównomierne (wsporniki, trzon klatki)
       przenosi jedna sztywna płyta, co ogranicza różnice osiadań (wymagania {D.zr('geotechnika', 'osiadanie_max')}).
    4. *Szczelność i uziemienie:* ciągła izolacja przeciwwilgociowa i przeciwradonowa na płycie; uziom
       {D.Wd['odgromowa'].get('uziom', '—')} pod warstwą XPS (W-187, W-286).
    """)


def r06_08(pab, D, d):
    pab.rozdzial(tyt("Liczba lokali mieszkalnych i użytkowych", 6))
    pab.markdown("""
    Budynek zawiera **1 lokal mieszkalny** (wielopoziomowy, obejmujący wszystkie kondygnacje nadziemne wraz z garażem
    i pomieszczeniami technicznymi) oraz **0 lokali użytkowych** — zgodnie z definicją budynku mieszkalnego
    jednorodzinnego (PB art. 3 pkt 2a).
    """)
    pab.rozdzial(tyt("Liczba lokali mieszkalnych dostępnych dla osób niepełnosprawnych", 7))
    pab.markdown("""
    **Nie dotyczy.** Obowiązek określenia liczby lokali dostępnych dotyczy zamierzeń budowlanych obejmujących budynek
    mieszkalny wielorodzinny (RPB § 20 ust. 1 pkt 7); projektowany jest budynek mieszkalny jednorodzinny.
    """)
    pab.rozdzial(tyt("Opis zapewnienia warunków korzystania z obiektu przez osoby niepełnosprawne", 8))
    pab.markdown("""
    **Nie dotyczy.** Opis sporządza się dla obiektów użyteczności publicznej i mieszkaniowego budownictwa
    wielorodzinnego (RPB § 20 ust. 1 pkt 8, także w brzmieniu nadanym rozporządzeniem Dz.U. 2026 poz. 597, stosowanym
    od 5 listopada 2026 r.); budynek mieszkalny jednorodzinny do tej grupy nie należy.
    """)


def r09(pab, D, d):
    wo, ka, de, og = D.Wd["woda"], D.Wd["kanalizacja"], D.Wd["deszczowa"], D.Wd["ogrzewanie"]
    ep = D.ep
    ogo = D.W["ogrzewanie"]
    pco, ha = ogo.pc, ogo.halas
    nc = niecka(D)
    odp = czysc((D.Dz.get("odpady") or {}).get("opis", do_uzup("miejsce gromadzenia odpadów")))
    drz = D.Dz.get("drzewa") or []
    istn = [x for x in drz if x.get("istn")]
    wyc = [x for x in istn if x.get("do_wyciecia")]
    ce = czysc(next((x.get("opis") for x in D.Wy if x.get("typ") == "rekuperator"), ""))
    rad = D.m.material("MEMB_SBS_POD")
    pab.rozdzial(tyt("Wpływ obiektu na środowisko, zdrowie ludzi i obiekty sąsiednie (charakterystyka ekologiczna)", 9))
    pab.markdown(f"""
    ## Woda, ścieki, wody opadowe (lit. a)

    Zaopatrzenie w wodę z sieci wodociągowej (przyłącze — PZT). Zapotrzebowanie: średnie dobowe
    Q_{{d,śr}} = {L(wo['Q_d_sr_m3'], 2)} m³/d, maksymalne godzinowe Q_{{h,max}} = {L(wo['Q_h_max_m3'], 2)} m³/h, przepływ
    obliczeniowy q = {L(wo['q_obl_dm3s'], 3)} dm³/s; ciepła woda — {L(wo['cwu_V_d_l'], 0)} dm³/d. Jakość wody — woda
    przeznaczona do spożycia z sieci; zabezpieczenie przed przepływem zwrotnym za wodomierzem (PN-EN 1717, W-131).
    Ścieki bytowe odprowadzane do sieci kanalizacji sanitarnej: przepływ obliczeniowy Q_{{ww}} = {L(ka['Q_ww_l_s'], 2)} dm³/s,
    przykanalik {przykanalik(D)}; ilość ścieków równa zużyciu wody. Ścieki przemysłowe nie powstają.
    Wody opadowe z dachów (A = {L(de['A_dachow_m2'], 1)} m², Q = {L(de['Q_dachy_l_s'], 2)} dm³/s) zagospodarowane w całości
    na działce: szczelny zbiornik retencyjny V = {L(de['V_zbiornika_m3'], 1)} m³ (podlewanie ogrodu — pokrycie potrzeb
    {L(100 * de['pokrycie_podlewania'], 0)} %) z przelewem do niecki chłonnej (ogrodu deszczowego) o powierzchni
    {L(nc['A'], 1)} m² i pojemności {L(nc['V'], 2)} m³ przy głębokości {L(nc['h'], 2)} m — {ok(nc['V'] >= de['niecka_V_min_m3'])}
    warunek pojemności V ≥ V_{{min}} = {L(de['niecka_V_min_m3'], 2)} m³ (minimalna powierzchnia wg obliczenia
    {L(de['niecka_A_m2'], 1)} m²); wody z podjazdu przez osadnik z separatorem; brak odprowadzania wód na
    drogę publiczną i na działki sąsiednie (W-143…W-145; obliczenia `lamela.obliczenia.sanitarne.deszczowa`).

    ## Emisje zanieczyszczeń (lit. b)

    Budynek nie ma instalacji spalania paliw (źródło ciepła — pompa ciepła zasilana energią elektryczną; brak przewodów
    spalinowych i dymowych) — **brak emisji gazowych i pyłowych w miejscu**. Emisja pośrednia CO₂ związana z energią
    elektryczną z sieci: {L(ep.E_CO2_t, 2)} t/rok (charakterystyka energetyczna — rozdz. 10). Czynnik chłodniczy pompy
    ciepła — propan R290 (naturalny; rozp. (UE) 2024/573 — W-155). Powietrze usuwane wentylacją mechaniczną wyrzutnią
    dachową; wywiewki kanalizacyjne ponad dachem. Brak emisji płynnych i odorów poza typowymi dla gospodarstwa domowego.

    ## Odpady (lit. c)

    Odpady komunalne z gospodarstwa domowego (frakcje: zmieszane, papier, szkło, metale i tworzywa, bioodpady) —
    selektywne gromadzenie na działce: {odp}; ilość wg wskaźników regulaminu utrzymania czystości i porządku w gminie
    {do_uzup('wskaźnik nagromadzenia odpadów z regulaminu gminy')}. Odpady budowlane w fazie realizacji — segregacja
    i przekazanie uprawnionym odbiorcom przez wykonawcę. Odpady niebezpieczne nie powstają w eksploatacji.

    ## Akustyka, drgania, promieniowanie, pola elektromagnetyczne (lit. d)

    Źródłem hałasu jest jednostka zewnętrzna pompy ciepła {pco['model']} (dane wyrobu przykładowego {DANE_PRZYKLADOWE}):
    poziom mocy akustycznej L_{{WA}} = {L(pco['L_WA'], 0)} dB(A) w porze dnia i {L(pco['L_WA_noc'], 0)} dB(A) w trybie
    nocnym; odległość od granicy ({ha['granica']}) {L(ha['r'], 2)} m; poziom na granicy działki: noc
    L_{{A}} = {L(ha['L_A_granica'], 1)} dB(A) ≤ {L(D.v('usytuowanie', 'halas_LAeq_noc_max'), 0)} dB —
    {ok(ha['L_A_granica'] <= D.v('usytuowanie', 'halas_LAeq_noc_max'))}, dzień L_{{A}} = {L(ha['L_A_dzien'], 1)} dB(A)
    ≤ {L(D.v('usytuowanie', 'halas_LAeq_dzien_max'), 0)} dB — {ok(ha['L_A_dzien'] <= D.v('usytuowanie', 'halas_LAeq_dzien_max'))}
    ({D.zr('usytuowanie', 'halas_LAeq_noc_max')}) — obliczenia `lamela.obliczenia.sanitarne.ogrzewanie`
    (propagacja w półprzestrzeni z kierunkowością; te same wartości w opisie PZT). Centrala wentylacyjna w pomieszczeniu technicznym: {ce}.
    Drgania — brak źródeł poza urządzeniami na podkładkach antywibracyjnych. Promieniowanie jonizujące i pola
    elektromagnetyczne — brak źródeł poza instalacją elektryczną nN i instalacją fotowoltaiczną (falownik z deklaracją
    zgodności). Ochrona przed radonem z podłoża — {rad.nazwa.lower() if rad else do_uzup('izolacja przeciwradonowa')}.

    ## Drzewostan, powierzchnia ziemi, gleba, wody (lit. e)

    Drzewa istniejące na działce: {len(istn)} — {'do wycinki: ' + ', '.join(x['id'] for x in wyc) if wyc else 'wszystkie zachowane'};
    nowe nasadzenia drzew: {len(drz) - len(istn)} (PZT) {DANE_PRZYKLADOWE}. Warstwa gleby (ok.
    {L((D.B.get('geotechnika') or {}).get('humus'), 2)} m) zdjęta pod budynkiem i utwardzeniami, składowana i wykorzystana
    do kształtowania zieleni. Powierzchnia biologicznie czynna {L(D.w['pbc']['wartosc'])} m²
    ({L(100 * D.w['udzial_pbc']['wartosc'])} % działki) oraz dach zielony (rezerwa {L(D.w['pbc_rezerwa_dach']['wartosc'])} m²).
    Wody powierzchniowe — brak na działce; wody podziemne — zwierciadło poniżej posadowienia, brak drenażu i odwodnienia
    wykopów na etapie eksploatacji; infiltracja wód opadowych w niecce chłonnej. Obszar oddziaływania obiektu (PB art. 3
    pkt 20, art. 20 ust. 1 pkt 1c) mieści się w granicach działki — opis PZT {INT}.
    """)
