"""PT-4 IE — część opisowa B: mikroinstalacja fotowoltaiczna (PN-HD 60364-7-712), punkt ładowania EV
(PN-HD 60364-7-722), instalacje telekomunikacyjne (§ 23 pkt 7 lit. h, W-196), ochrona odgromowa, uziom i połączenia
wyrównawcze (§ 23 pkt 7 lit. i, W-187, W-188, W-191). Liczby wyłącznie z ``DanePTIE`` (model + obliczenia)."""
from __future__ import annotations

import math

from pt_ie_dane import L, DanePTIE, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


def _e(D: DanePTIE, k: str, d=None):
    return D.v("elektryka", k, d)


def rozdz_pv(o: Opis, D: DanePTIE):
    """5. Mikroinstalacja fotowoltaiczna."""
    pv, m, f = D.pv, D.pv.par.modul, D.pv.par.falownik
    lan, dc, s = pv.lancuchy, pv.dc, pv.sym
    ob = next((x for x in D.obw.obwody if x.odb.grupa == "pv"), None)
    n2 = pv.n_mod - lan["Ns"] * (lan["n_str"] - 1)
    o.rozdzial("Mikroinstalacja fotowoltaiczna", podstawa="PN-HD 60364-7-712:2016-05; W-194", nowa_strona=True)
    o.tekst(f"""
    **Zakres i status formalny.** {pv.n_mod} modułów o mocy {L(m['P'], 0)} Wp — moc zainstalowana
    **{L(pv.P_kWp, 2)} kWp** (suma mocy z tabliczek modułów) ≤ {L(_e(D, 'PV_moc_modulow_max'), 1)} kWp,
    falownik 3-fazowy {L(f['P_AC'], 1)} kW ≤ {L(_e(D, 'PV_falownik_max'), 1)} kW — mikroinstalacja (≤
    {L(_e(D, 'mikroinstalacja_max'), 0)} kW) przyłączana na zgłoszenie do OSD (Pr. energ. art. 7 ust. 8d4); przy mocy
    ≤ {L(_e(D, 'PV_moc_modulow_max'), 1)} kW bez uzgodnienia z rzeczoznawcą ds. zabezpieczeń przeciwpożarowych
    i zawiadomienia PSP (PB art. 29 ust. 4 pkt 3 lit. c; W-194). Moc mikroinstalacji ≤ mocy przyłączeniowej
    ({L(D.bil.P_przyl, 0)} kW). Magazyn energii — nie przewiduje się (rezerwa w RG).

    **Rozmieszczenie.** Dach {pv.dach['id']} (płaski, powierzchnia {L(pv.dach['A'], 1)} m², użytkowa po odjęciu
    strefy brzegowej {L(pv.dach['A_uz'], 1)} m²), układ {pv.wariant}; moduły nie wystają ponad attykę
    ({L(pv.dach.get('attyka'), 2)} m). Konstrukcja balastowa bez przebijania pokrycia (obciążenie dachu — PT-2 BO;
    zabezpieczenie przed wiatrem wg PN-EN 1991-1-4). Rozmieszczenie — arkusze {D.arkusze_nr('fotowolt')}.

    **Łańcuchy i strona DC.** {lan['n_str']} {'łańcuchy' if lan['n_str'] < 5 else 'łańcuchów'}
    ({lan['Ns']} + {n2} modułów; po jednym na wejście MPPT) — maksymalne napięcie łańcucha w temperaturze minimalnej
    U_oc,max = {L(lan['Uoc_max'], 0)} V, zakres napięć MPP {L(lan['Umpp_min'], 0)}–{L(lan['Umpp_max'], 0)} V
    (mieści się w zakresie MPPT falownika {L(f['U_mppt'][0], 0)}–{L(f['U_mppt'][1], 0)} V);
    {'bez bezpieczników łańcuchowych (jeden łańcuch na MPPT)' if not lan['bezpieczniki'] else 'bezpieczniki łańcuchowe gPV'}.
    Przewody DC H1Z2Z2-K (PN-EN 50618) {L(D.pv.par.s_DC, 0)} mm², trasa dach → falownik L = {L(dc['L'], 1)} m,
    prowadzone parami (małe pętle indukcyjne), w osłonach odpornych na UV; spadek napięcia DC {L(dc['dU'], 2)} %.
    {dc['SPD']}; {dc['rozlacznik']}. Długość krytyczna DC dla SPD L_crit = {L(dc['L_crit'], 1)} m.

    **Strona AC.** Obwód {ob.odb.id if ob else '—'} w RG: {ob.zab if ob else '—'}, {ob.przewod if ob else '—'},
    {ob.odb.rcd if ob else '—'}. Falownik z certyfikatem zgodności z NC RfG (rozp. (UE) 2016/631) i nastawami wg
    PN-EN 50549-1 oraz wymagań OSD; zabezpieczenie przed pracą wyspową wbudowane. Przeciwpożarowy wyłącznik prądu
    odcina stronę AC falownika; strona DC pozostaje pod napięciem — tabliczki ostrzegawcze przy RG, PWP i falowniku.
    Konstrukcja PV uziemiona w jednym punkcie i połączona z GSU (712.444.5.5.101).

    **Produkcja energii** (PVGIS 5.3, Poznań): E = {L(pv.E_y, 0)} kWh/rok; autokonsumpcja (bilans godzinowy)
    {L(100 * s['autokonsumpcja'], 1)} %, pokrycie zużycia {L(100 * s['pokrycie'], 1)} %; energia PV zużyta przez
    systemy techniczne (ogrzewanie, c.w.u., pomocnicze) {L(s['E_auto_H'] + s['E_auto_W'] + s['E_auto_pom'], 0)}
    kWh/rok — przekazana do charakterystyki energetycznej (PT-3 IS). Odbiór: PN-EN 62446-1 (rozdz. „Próby”).
    """)


def rozdz_ev(o: Opis, D: DanePTIE):
    """6. Punkt ładowania pojazdu elektrycznego."""
    ev = next((x for x in D.obw.obwody if x.odb.grupa == "ev"), None)
    mp = D.miejsca_postojowe
    prog, udz = _e(D, "EPBD_miejsca_prog", 3), _e(D, "EPBD_okablowanie_wstepne_udzial", 0.5)
    n_wst = math.ceil(udz * len(mp)) if len(mp) > prog else 0
    o.rozdzial("Punkt ładowania pojazdu elektrycznego", podstawa="PN-HD 60364-7-722:2019-01; W-195")
    if ev is None:
        o.tekst("W obliczeniach nie przewidziano obwodu punktu ładowania (brak garażu w modelu) — nie dotyczy.")
        return
    o.tekst(f"""
    Obowiązek wyposażenia budynku jednorodzinnego w punkt ładowania nie wynika z ustawy o elektromobilności (W-195).
    Projektuje się **obwód wydzielony {ev.odb.id}** — {ev.odb.nazwa}: moc {L(ev.odb.P, 1)} kW, I_B = {L(ev.I_B, 1)} A,
    zabezpieczenie {ev.zab}, przewód {ev.przewod} (L = {L(ev.L, 1)} m, ∆U_c = {L(ev.dU_calk, 2)} %), ochrona
    różnicowoprądowa: {ev.odb.rcd}. Punkt ładowania (tryb 3, PN-EN IEC 61851-1) objęty dynamicznym zarządzaniem mocą
    (DLM) — ograniczenie prądu ładowania przy przekroczeniu mocy przyłączeniowej (rozdz. „Bilans mocy”). Obwód nie
    może pracować w układzie TN-C; osobny RCD dla każdego punktu przyłączenia (722.531.2).

    Miejsca postojowe w PZT: {len(mp)} ({', '.join(f"{x['id']} — {'garaż' if x.get('typ') == 'garaz' else 'zewnętrzne'}" for x in mp)}).
    {'Przy liczbie miejsc > ' + L(prog, 0) + ' dyrektywa EPBD (UE) 2024/1275 art. 14 ust. 4 — nietransponowana, stosowana dobrowolnie — przewiduje okablowanie wstępne ≥ ' + L(100 * udz, 0) + ' % miejsc (tu ' + str(n_wst) + ') i kanały kablowe dla pozostałych: projektuje się rurę osłonową do miejsc zewnętrznych i rezerwę w RG na drugi punkt ładowania.' if n_wst else 'Liczba miejsc nie przekracza progu EPBD art. 14 ust. 4 (' + L(prog, 0) + ') — rezerwa w RG na drugi punkt ładowania.'}
    """)


def rozdz_tele(o: Opis, D: DanePTIE):
    """7. Instalacje telekomunikacyjne (§ 23 pkt 7 lit. h)."""
    t = D.uzbrojenie("tele")
    tele = next((x for x in D.obw.obwody if x.odb.grupa == "tele"), None)
    o.rozdzial("Instalacje telekomunikacyjne", podstawa="§ 23 pkt 7 lit. h RPB; rozp. (UE) 2024/1309 art. 10; W-196",
               nowa_strona=True)
    o.tekst(f"""
    **Przyłącze światłowodowe.** Budynek wyposaża się w infrastrukturę fizyczną przystosowaną do sieci światłowodowej
    i okablowanie światłowodowe do punktu zakończenia sieci (rozp. (UE) 2024/1309 art. 10 ust. 1 — wniosek o pozwolenie
    na budowę po 12.02.2026; W-196). Kanalizacja od granicy działki do budynku: {t.get('opis', '—')}, długość
    {L(t.get('dl'), 1)} m (wg PZT); wprowadzenie do budynku gazoszczelne (W-214). Kabel światłowodowy jednomodowy
    ≥ {L(_e(D, 'swiatlowod_wlokna_min'), 0)} włókna, złącza SC/APC, tłumienie toru ≤
    {L(_e(D, 'swiatlowod_tlumienie_toru_max'), 1)} dB (dobra praktyka — W-196). Punkt zakończenia sieci (ONT)
    w szafie teleinformatycznej; przyłącze wykonuje operator wg warunków technicznych
    [DO UZUPEŁNIENIA: operator i nr warunków technicznych przyłączenia telekomunikacyjnego].

    **Instalacja wewnętrzna.** Okablowanie strukturalne w topologii gwiazdy od szafy teleinformatycznej (RACK):
    skrętka kat. 6A U/FTP do gniazd RJ45, punkty dostępowe Wi-Fi zasilane PoE, instalacja RTV/SAT, wideodomofon
    i system sygnalizacji włamania i napadu (SSWiN, stopień 2 wg PN-EN 50131-1) — wg PN-EN 50173-4:2018-07
    (okablowanie w domach) i PN-EN 50174-2:2018-08 (instalowanie), połączenia wyrównawcze wg PN-EN 50310:2016-09.
    Przewody w rurach osłonowych, w odległości ≥ 0,1 m od przewodów elektroenergetycznych (albo z przegrodą);
    obudowa szafy objęta połączeniami wyrównawczymi (WT § 183 ust. 1a pkt 8). Zasilanie szafy: obwód
    {tele.odb.id + ' (' + tele.zab + ', ' + tele.przewod + ')' if tele else '—'}. Światłowód dielektryczny nie wymaga
    SPD; linie miedziane wchodzące do budynku (antena, wideodomofon) — SPD na wejściu. Rozmieszczenie — arkusze
    {D.arkusze_nr('teletechnika')}.
    """)
