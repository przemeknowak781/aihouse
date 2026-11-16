#!/usr/bin/env python3
"""Szacunkowy bilans energii, emisji, wody i retencji dla koncepcji budynku UMWD (etap konkursowy).

Uruchomienie:  python3 -I _bilans_energii.py
Wszystkie wartosci wejsciowe to ZALOZENIA koncepcyjne (wniosek), do aktualizacji po ustaleniu bryly.
Zrodla parametrow: patrz strategia_energetyczna.md (rozdz. 4) i zero_emisja.md.
"""

# --- 1. Geometria (z docs/20_program/program.md; wniosek) ------------------------------
AF = 12_500          # m2, powierzchnia o regulowanej temperaturze (Af) - czesc nadziemna netto + ogrzewane pom. podziemne
PC_TOTAL = 20_000    # m2, powierzchnia calkowita (nadziemna ok. 14 000 + podziemna ok. 6 000)
PC_ABOVE = 14_000

# --- 2. Zapotrzebowanie na energie uzytkowa [kWh/(m2 Af rok)] (wniosek) ----------------
Q_H = 25.0     # ogrzewanie + wentylacja po odzysku ciepla (przegrody lepsze od WT, MVHR >= 80 %)
Q_W = 4.0      # c.w.u. (biuro, bistro bez kuchni, prysznice przy rowerowni)
Q_C = 30.0     # chlodzenie (biura, sala obrad, sale konferencyjne; osłony zewn. fc <= 0,15)
IT_KW = 10.0   # sredni pobor serwerowni TIER II (kW, ciagly) - cieplo odzyskiwane

# --- 3. Sprawnosci systemow (wniosek; do potwierdzenia symulacja) -----------------------
SCOP_H = 4.5   # gruntowa PC, niskotemperaturowe ogrzewanie (TABS/belki ok. 30-35 C)
COP_W = 3.0    # c.w.u. 55-60 C (stopien dogrzewu)
FC_SHARE = 0.5 # udzial chlodu z free-coolingu gruntowego (bez sprezarki)
SEER_FC = 20.0 # free-cooling (pompy obiegowe)
EER_ACT = 5.5  # chlodzenie aktywne PC (wysokotemperaturowe 16/19 C)

E_FANS = 5.0   # wentylatory [kWh/(m2 rok)] SFP ok. 1,2-1,5 kW/(m3/s), DCV wg CO2
E_AUX = 2.0    # pompy, automatyka
E_LIGHT = 6.5  # LED ok. 5 W/m2, sterowanie swiatlem dziennym i obecnoscia (LENI)

# Odbiory poza zakresem EP (nieregulowane)
E_PLUG = 18.0  # urzadzenia biurowe
E_LIFT = 2.0
E_OTHER = 1.0  # bistro (bez kuchni), pralnia, drobne

# --- 4. PV (PVGIS 5.3, SARAH3, Wroclaw 51,112 N 17,045 E, straty 14 %) ---------------------
PV = [  # (opis, kWp, kWh/kWp*rok po zacienieniu - wniosek)
    ("dachy - BIPV/biosolar E-W 10 st. i dach dominanty", 240, 900),   # PVGIS: 893 (E/W 10), 983 (S 10)
    ("dominanta - BIPV elewacje S/E/W powyzej ok. 25 m", 150, 600),    # PVGIS: 787 S, 532 E, 536 W (pion)
    ("skrzydla - BIPV parapety/pasy od dziedzinca", 50, 450),          # zacienienie zabudowa
]
SELF_CONS = 0.80   # autokonsumpcja (profil dzienny biura + BESS + EV + magazyny ciepla/chlodu)

W_EL = 2.5         # wsp. nakladu nieodnawialnej energii pierwotnej - energia elektryczna (Dz.U. 2023 poz. 697)
EF_GRID = 0.60     # kg CO2/kWh - rzad wielkosci dla sieci krajowej (KOBiZE; do aktualizacji)

# --- 5. Dolne zrodlo (wniosek; do weryfikacji TRT i symulacja EED/EWS) ----------------------
N_BHE = 75
L_BHE = 99.0       # m (<= 100 m: poza rezimem art. 86 PGiG)
L_ACT = 95.0       # m czynnej dlugosci
Q_EXT = 45.0       # W/m - poboru (praca > 2000 h, piaski/zwiry nawodnione + gliny)
Q_INJ = 55.0       # W/m - oddawania ciepla latem

# --- 6. Woda (wniosek) -------------------------------------------------------------------
STAFF = 403; VISIT = 100; DAYS = 250
FLUSH_STAFF = 13.0; FLUSH_VISIT = 5.0           # l/os.d (WC 6/3 l, srednio <= 3,5 l; pisuary <= 1 l)
BASIN = 5.0                                     # l/os.d (baterie <= 6 l/min)
SHOWERS_PER_DAY = 30; SHOWER_L = 40.0           # 8 l/min x 5 min
POTABLE_STAFF = 30.0; POTABLE_VISIT = 10.0      # l/os.d - calkowite zuzycie wody w biurze (bazowe)
P_YEAR = 0.570                                  # m opadu/rok - rzad wielkosci dla Wroclawia (do weryfikacji IMGW)
ROOF_HARD = 1_100; ROOF_GREEN = 1_200           # m2 powierzchni zbieranych
GREEN_GROUND = 900; IRR = 0.15                  # m2; m3/m2 sezon

# --- 7. Retencja (MPWiK RW25 v.4.1, Model I Kotowski 2010, C = 10 lat - zabudowa srodmiejska) -
Q15_C10 = 204.7    # dm3/(s ha)
H60_C10 = 30.44    # mm
SURF = [  # (opis, m2, psi_przed, psi_po)
    ("dach dominanty z PV", 900, 0.95, 0.95),
    ("dachy skrzydel", 1_200, 0.95, 0.30),       # zielony dach > 10 cm warstw sypkich
    ("tarasy", 200, 0.95, 0.80),
    ("nawierzchnie dziedzinca/dojazd", 500, 0.80, 0.60),   # kostka na podbudowie przepuszczalnej
    ("zielen na gruncie", 900, 0.10, 0.10),
]


def main():
    e_h = Q_H / SCOP_H
    e_w = Q_W / COP_W
    e_c = Q_C * FC_SHARE / SEER_FC + Q_C * (1 - FC_SHARE) / EER_ACT
    epb = e_h + e_w + e_c + E_FANS + E_AUX + E_LIGHT
    server = IT_KW * 8760 / AF
    non_epb = E_PLUG + E_LIFT + E_OTHER + server
    total = epb + non_epb
    print("== ENERGIA KONCOWA (elektryczna) [kWh/(m2 Af rok)]")
    for k, v in [("ogrzewanie", e_h), ("c.w.u.", e_w), ("chlodzenie", e_c), ("wentylatory", E_FANS),
                 ("pomocnicze", E_AUX), ("oswietlenie", E_LIGHT)]:
        print(f"  {k:14s} {v:6.1f}")
    print(f"  SUMA EPB       {epb:6.1f}  -> {epb*AF/1000:7.0f} MWh/rok")
    print(f"  nieregulowane  {non_epb:6.1f}  (w tym serwerownia {server:.1f}) -> {non_epb*AF/1000:7.0f} MWh/rok")
    print(f"  RAZEM          {total:6.1f}  -> {total*AF/1000:7.0f} MWh/rok  | na PC: {total*AF/PC_TOTAL:5.1f} kWh/(m2 PC rok)")

    pv_kwp = sum(p[1] for p in PV)
    pv_mwh = sum(p[1] * p[2] for p in PV) / 1000
    print(f"\n== PV: {pv_kwp} kWp = {pv_kwp/1000:.2f} MWp, produkcja {pv_mwh:.0f} MWh/rok")
    for d, kwp, y in PV:
        print(f"  {d:60s} {kwp:4d} kWp x {y:4d} = {kwp*y/1000:5.0f} MWh")
    self_c = pv_mwh * SELF_CONS
    print(f"  autokonsumpcja {SELF_CONS:.0%}: {self_c:.0f} MWh; eksport {pv_mwh-self_c:.0f} MWh")
    print(f"  PV / zapotrzebowanie EPB = {pv_mwh/(epb*AF/1000):.0%};  PV / calosc = {pv_mwh/(total*AF/1000):.0%}")

    # EP (metodyka PL): energia z PV wykorzystana na potrzeby EPB pomniejsza energie dostarczona.
    pv_to_epb_low, pv_to_epb_high = 0.0, min(self_c, epb * AF / 1000) * 0.6
    ep_noPV = epb * W_EL
    ep_PV = (epb * AF / 1000 - pv_to_epb_high) * 1000 / AF * W_EL
    print(f"\n== EP [kWh/(m2 rok)]: bez PV {ep_noPV:.0f}; z PV (60 % autokonsumpcji przypisane EPB) {ep_PV:.0f}")
    print("   EPmax WT2002 (100 % chlodzone, t0 < 2500 h): 45 + 25 + 25 = 95; prog ZEB (projekt WT od 2028 dla JSFP): 40 + 22 + 23 = 85")
    eco2_zeb = 0.000274 * 85 + 0.0081
    grid_epb = epb * AF / 1000 - pv_to_epb_high
    grid_all = total * AF / 1000 - self_c
    print(f"\n== Emisje operacyjne (lokalizacyjne, EF={EF_GRID}): EPB {grid_epb*EF_GRID*1000/AF:.1f} kg/(m2 rok); "
          f"calosc {grid_all*EF_GRID*1000/AF:.1f} kg/(m2 rok); prog ZEB projekt WT: {eco2_zeb*1000:.1f} kg/(m2 rok)")

    # Dolne zrodlo
    l_tot = N_BHE * L_ACT
    p_ext = l_tot * Q_EXT / 1000
    p_inj = l_tot * Q_INJ / 1000
    q_h_peak_cap = p_ext / (1 - 1 / 4.0)       # moc grzewcza PC przy COP 4,0 w szczycie
    q_c_cap = p_inj / (1 + 1 / EER_ACT)
    print(f"\n== Dolne zrodlo: {N_BHE} BHE x {L_BHE:.0f} m (czynne {l_tot:.0f} m), siatka 6x6 m -> {N_BHE*36:.0f} m2")
    print(f"   pobor {p_ext:.0f} kW -> moc grzewcza PC ok. {q_h_peak_cap:.0f} kW; oddawanie {p_inj:.0f} kW -> chlod aktywny ok. {q_c_cap:.0f} kW")
    ext_year = Q_H * AF / 1000 * (1 - 1 / SCOP_H)
    inj_year = (Q_C * FC_SHARE + Q_C * (1 - FC_SHARE) * (1 + 1 / EER_ACT)) * AF / 1000
    print(f"   bilans roczny gruntu: pobor {ext_year:.0f} MWh, oddanie {inj_year:.0f} MWh -> nadwyzka ciepla {inj_year-ext_year:.0f} MWh "
          f"(do zbilansowania: odzysk do c.w.u./ogrzewania, dry-cooler w okresach przejsciowych)")

    # Woda
    flush = (STAFF * FLUSH_STAFF + VISIT * FLUSH_VISIT) * DAYS / 1000
    grey = (STAFF * BASIN + SHOWERS_PER_DAY * SHOWER_L) * DAYS / 1000
    rain = (ROOF_HARD * 0.8 + ROOF_GREEN * 0.35) * P_YEAR * 0.9
    irr = GREEN_GROUND * IRR
    potable_base = (STAFF * POTABLE_STAFF + VISIT * POTABLE_VISIT) * DAYS / 1000 + irr
    subst = min(flush, grey + rain * 0.75) + min(irr, rain * 0.25)
    print(f"\n== Woda [m3/rok]: splukiwanie {flush:.0f}; woda szara {grey:.0f}; deszczowa {rain:.0f}; podlewanie {irr:.0f}")
    print(f"   zuzycie bazowe wody wodociagowej ok. {potable_base:.0f}; zastapione {subst:.0f} -> redukcja {subst/potable_base:.0%}")

    # Retencja
    a = sum(s[1] for s in SURF)
    psi_b = sum(s[1] * s[2] for s in SURF) / a
    psi_a = sum(s[1] * s[3] for s in SURF) / a
    q_b = Q15_C10 * psi_b * a / 10_000
    q_a = Q15_C10 * psi_a * a / 10_000
    v60 = H60_C10 / 1000 * psi_a * a
    print(f"\n== Retencja: F={a} m2; psi przed {psi_b:.2f}, po {psi_a:.2f}; Qdm(15 min, C=10) {q_b:.0f} -> {q_a:.0f} dm3/s; "
          f"objetosc opadu 60 min C=10 z powierzchni zredukowanej: {v60:.0f} m3")


if __name__ == "__main__":
    main()
