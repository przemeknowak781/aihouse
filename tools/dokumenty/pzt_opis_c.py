"""PZT — część opisowa, RPB § 14 pkt 5–8 i § 18: ograniczenia i zagrożenia, ochrona ppoż., ochrona ludności,
inne dane (retencja, strefa R290), obszar oddziaływania obiektu; część rysunkowa."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, ZAL, Arkusz, arkusze_z_katalogu, do_uzup, liczba

from pzt_dane import _poly


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
    Działka leży w terenie **3MN** — zabudowa mieszkaniowa jednorodzinna wolnostojąca — MPZP: {(z.dz.get('dzialka') or {}).get('mpzp', '—')}
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
         "Ocena": "brak zrzutu do wód i na teren sąsiedni (pkt 3 lit. b, pkt 7)"},
        {"Oddziaływanie": "Odpady", "Charakterystyka": "odpady komunalne segregowane w stanowisku pojemników przy ogrodzeniu",
         "Ocena": "odbiór wg regulaminu gminy"},
        {"Oddziaływanie": "Zieleń", "Charakterystyka": f"drzewa do usunięcia: {len(wyc) or 'brak'}; drzewa istniejące zachowane",
         "Ocena": "zezwolenie / zgłoszenie usunięcia drzew nie dotyczy (u.o.p. art. 83f [W-023])" if not wyc else "wymagane zgłoszenie (u.o.p. art. 83f)"},
        {"Oddziaływanie": "Grunty rolne", "Charakterystyka": f"klasy gruntów {ZAL} — mineralne RIVb/RV {do_uzup('wypis z EGiB (E-03)')}",
         "Ocena": f"decyzja o wyłączeniu z produkcji nie dotyczy przy klasach IV–VI mineralnych [W-025]"},
        {"Oddziaływanie": "Czynnik chłodniczy R290 (propan)", "Charakterystyka": "strefa bezpieczeństwa wokół jednostki zewnętrznej bez otworów, wpustów, studzienek i źródeł zapłonu",
         "Ocena": (f"{r290.wartosc} ({r290.status})" if r290 else "—") + " [W-156]"},
    ], tytul="Oddziaływania i zagrożenia", lp=True, szerokosci=["7mm", "34mm", None, "46mm"],
        zrodlo="lamela.obliczenia.sanitarne.ogrzewanie (hałas: PORT PC p. 4.4); audyt A1; model/dzialka.yaml")


# ------------------------------------------------------------------------------------------------ § 14 pkt 6, 6a
def pkt6(zp, z, d):
    grupa = z.W["wysokosc_WT6"].get("grupa", "—")
    gr, zr_gr, _ = z.wym("ppoz", "grupa_wysokosci")
    zl, zr_zl, _ = z.wym("ppoz", "kategoria_ZL")
    o8, zr_o8, i_o8 = z.wym("usytuowanie", "odl_ppoz_ZL_ZL")
    q, zr_q, i_q = z.wym("ppoz", "woda_ppoz_min")
    sas = [s for s in z.sasiedzi() if s["odl_bud"] is not None]
    smin = min(sas, key=lambda s: s["odl_bud"]) if sas else None
    dh, hyd = z.odl_hydrantu()
    u2 = _poly(next((u for u in z.dz.get("utwardzenia") or [] if u.get("id") == "U2"), {}).get("obrys"))
    zp.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", f"""
    Budynek mieszkalny jednorodzinny, kategoria zagrożenia ludzi **{zl}** ({zr_zl}), grupa wysokości **{grupa}** —
    budynek niski (wysokość wg WT § 6: {L(z.w('wysokosc_WT6'))} m; {zr_gr}). Odległość od najbliższego budynku
    sąsiedniego (dz. {smin['nr'] if smin else '—'}): {L(smin['odl_bud']) if smin else '—'} m ≥ {L(o8, 1)} m ({zr_o8};
    {i_o8}) — ściany zewnętrzne i dach nierozprzestrzeniające ognia (PAB).

    **Droga pożarowa** — nie jest wymagana: budynek {zl} niski nie należy do obiektów, dla których wymaga się drogi
    pożarowej (rozporządzenie MSWiA w sprawie przeciwpożarowego zaopatrzenia w wodę oraz dróg pożarowych,
    Dz.U. 2009 nr 124 poz. 1030, § 12 ust. 1). Dojście od drogi publicznej {z.droga()['symbol']} — przez furtkę
    utwardzonym dojściem długości ok. {L(u2.bounds[3] - u2.bounds[1], 1) if u2 is not None else '—'} m do wejścia głównego (rys. PZT-01).

    **Przeciwpożarowe zaopatrzenie w wodę** — wymagana wydajność ≥ {L(q, 0)} dm³/s ({zr_q}; {i_q}) z sieci wodociągowej
    w drodze {z.droga()['symbol']}: najbliższy hydrant zewnętrzny — {(hyd or {}).get('opis', '—')}, w odległości ok.
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
