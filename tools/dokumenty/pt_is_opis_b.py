"""PT-3 IS — część opisowa B: obliczenia i dobory (§ 23 pkt 8 lit. a–b RPB), charakterystyka energetyczna
(§ 23 pkt 11 lit. a–d, W-251), dane ppoż. (§ 23 pkt 10), zasadnicze urządzenia (§ 23 pkt 9), próby i odbiory,
dane do uzupełnienia. Liczby wyłącznie z ``DanePTIS`` (model + obliczenia przy uruchomieniu)."""
from __future__ import annotations

import re
from pathlib import Path

from pt_is_dane import KAT_ZRODLA, L, DanePTIS, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"
RE_IMG = re.compile(r"^!\[(?P<cap>[^\]]*)\]\((?P<src>[^)]+)\)\s*$", re.M)
OPS = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "==": "=", "zakres": "w zakresie"}


def wstaw_raport(o: Opis, tekst: str, *, tytul: str, podstawa: str | None = None, katalog: Path | None = None,
                 zrodlo: str = ""):
    """Raport Markdown biblioteki obliczeniowej jako podrozdział (poziom 2): „# …” → tytuł podrozdziału, „## n. …”
    → poziom 3 (numeracja z nagłówków usunięta — numeruje dokument), obrazy → ilustracje numerowane."""
    tekst = re.sub(r"\A\s*#\s+[^\n]*\n", "", tekst)
    tekst = re.sub(r"^(#{2,4})\s+\d+(?:\.\d+)*\.?\s+", r"\1 ", tekst, flags=re.M)
    tekst = re.sub(r"^(#{2,4})\s", lambda m: m.group(1)[1:] + "# ", tekst, flags=re.M)   # ## → # (+przesunięcie 1)
    o.rozdzial(tytul, poziom=2, podstawa=podstawa, nowa_strona=True)
    poz = 0
    for m in RE_IMG.finditer(tekst):
        if tekst[poz:m.start()].strip():
            o.dok.markdown(tekst[poz:m.start()], przesuniecie=2)
        plik = (katalog or KAT_ZRODLA) / m.group("src")
        if plik.exists():
            o.dok.obraz(plik, podpis=m.group("cap"), szerokosc="100%")
        poz = m.end()
    if tekst[poz:].strip():
        o.dok.markdown(tekst[poz:], przesuniecie=2)
    o.md.append(f"*[Pełna treść obliczeń — w PDF; źródło: {zrodlo}]*")


def wk(D: DanePTIS, modul: str, fragment: str, parametr: str | None = None, miejsca: int = 2) -> dict | None:
    """Wiersz tabeli wyników z pierwszego warunku modułu, którego opis zawiera ``fragment``."""
    x = next((w for w in D.warunki(modul) if fragment in w.opis), None)
    if x is None:
        return None
    lim = x.limit
    lim_t = (f"{L(lim[0], miejsca)}–{L(lim[1], miejsca)}" if isinstance(lim, (list, tuple))
             else L(lim, miejsca) if isinstance(lim, (int, float)) else str(lim or ""))
    return dict(parametr=parametr or x.opis, wartosc=x.wartosc, jedn=x.jedn or "", miejsca=miejsca,
                wymaganie=f"{OPS.get(x.op, x.op)} {lim_t} {x.jedn or ''}".strip() if x.op != "info" else "—",
                podstawa=f"{x.podstawa} [{x.id}]" if x.id else x.podstawa, spelnia=x.ok)


def rozdz_obliczenia(o: Opis, D: DanePTIS):
    """5. Założenia, obliczenia i dobór urządzeń (§ 23 pkt 8 lit. a–b) — zestawienie + pełne obliczenia."""
    obc, w, og, pc = D.obc, D.went, D.og, D.og.pc
    temps = sorted({round(p.theta, 1) for p in obc.pomieszczenia})
    o.rozdzial("Założenia, obliczenia i dobór urządzeń", podstawa="§ 23 pkt 8 lit. a–b RPB", nowa_strona=True)
    o.rozdzial("Parametry klimatu zewnętrznego i wewnętrznego", poziom=2, podstawa="§ 23 pkt 8 lit. a RPB; W-150, W-161")
    o.tekst(f"""
    Klimat zewnętrzny: θ_e = {L(obc.theta_e, 0)} °C (strefa II, W-150), θ_m,e = {L(obc.theta_me, 1)} °C; dane
    godzinowe TMY Poznań (WMO 12330) do bilansu pompy ciepła i charakterystyki energetycznej. Klimat wewnętrzny
    (WT § 134 ust. 2): temperatury obliczeniowe pomieszczeń {', '.join(L(t, 0) for t in temps)} °C (pokoje,
    kuchnia, komunikacja 20 °C; łazienki 24 °C; wartości z modelu). Powietrze zewnętrzne ≥ 20 m³/h na osobę
    ({w.osoby} os.), wywiew wg PN-83/B-03430/Az3 (W-161, W-162). Szczelność budynku n50 = {L(obc.n50, 1)} h⁻¹ [ZAŁ]
    (cel projektowy — potwierdzić próbą ciśnieniową, W-249); sprawność odzysku ciepła η_v = {L(obc.eta_v, 2)}.
    """)
    P7 = dict(zip(pc["T"], pc["P"])).get(-7)
    Wd = D.Wd
    rows = [dict(parametr="Projektowe obciążenie cieplne budynku Φ_HL", wartosc=obc.Phi_HL / 1000, jedn="kW",
                 wymaganie="—", podstawa="PN-EN 12831 [W-151]", spelnia=None),
            dict(parametr=f"Pompa ciepła {pc.get('model')}: moc P(A−7/W35)", wartosc=P7, jedn="kW", miejsca=1,
                 wymaganie="—", podstawa=FIKCJA, spelnia=None),
            wk(D, "ogrzewanie", "Pokrycie mocy przy θ_e", "Pokrycie mocy przy θ_e: P_PC + P_grzałki ≥ Φ_HL + Φ_W"),
            wk(D, "ogrzewanie", "Punkt biwalentny", miejsca=1),
            wk(D, "ogrzewanie", "Udział grzałki", miejsca=4),
            wk(D, "ogrzewanie", "Sezonowa efektywność"),
            wk(D, "ogrzewanie", "Moc nominalna PC", "Moc nominalna PC (R290 — rozp. (UE) 2024/573)", 1),
            wk(D, "ogrzewanie", "Temperatura zasilania ogrzewania podłogowego", miejsca=0),
            dict(parametr="Bufor c.o. / naczynie wzbiorcze c.o.", wartosc=f"{Wd['ogrzewanie']['bufor_l']} / "
                 f"{Wd['ogrzewanie']['naczynie_co_l']}", jedn="dm³", wymaganie="—", podstawa="obliczenia (rozdz. Ogrzewanie)",
                 spelnia=None),
            wk(D, "ogrzewanie", "Poziom mocy akustycznej", miejsca=0),
            wk(D, "ogrzewanie", "Hałas PC w nocy na granicy", miejsca=1),
            wk(D, "ogrzewanie", "Hałas PC w dzień na granicy", miejsca=1),
            wk(D, "ogrzewanie", "Odległość jednostki PC od granicy", miejsca=1),
            wk(D, "ogrzewanie", "Strefa bezpieczeństwa R290", miejsca=0),
            dict(parametr="Wentylacja: nawiew / wywiew", wartosc=f"{L(w.suma_naw, 0)} / {L(w.suma_wyw, 0)}", jedn="m³/h",
                 wymaganie=f"≥ {L(w.naw_min_osoby, 0)} / ≥ {L(w.suma_wyw_min, 0)}", podstawa="WT § 149 [W-161, W-162]",
                 spelnia=w.suma_naw >= w.naw_min_osoby and w.suma_wyw >= w.suma_wyw_min),
            dict(parametr="Centrala: wydajność maks. ≥ strumień okresowy", wartosc=(w.centrala or {}).get("V_max_m3h"),
                 jedn="m³/h", miejsca=0, wymaganie=f"≥ {L(w.V_boost, 0)} m³/h", podstawa="PN-83/B-03430/Az3",
                 spelnia=((w.centrala or {}).get("V_max_m3h") or 0) >= w.V_boost),
            dict(parametr="SFP nawiewu / wywiewu", wartosc=f"{L(w.SFP_naw, 2)} / {L(w.SFP_wyw, 2)}", jedn="kW/(m³/s)",
                 wymaganie=f"≤ {L(w.SFP_lim_naw, 2)} / ≤ {L(w.SFP_lim_wyw, 2)}", podstawa="WT § 154 ust. 10–11 [W-164]",
                 spelnia=w.SFP_naw <= w.SFP_lim_naw and w.SFP_wyw <= w.SFP_lim_wyw),
            wk(D, "woda", "Przepływ obliczeniowy ≤ Q3", miejsca=2),
            wk(D, "woda", "Wymagane ciśnienie w sieci", miejsca=3),
            wk(D, "woda", "Ciśnienie statyczne w punkcie ≤ 0,60 MPa", miejsca=2),
            wk(D, "woda", "Pojemność zasobnika", miejsca=0),
            wk(D, "woda", "Temperatura dezynfekcji", miejsca=0),
            dict(parametr="Kanalizacja: ΣDU / Q_ww", wartosc=f"{L(Wd['kanalizacja']['sum_DU'], 1)} / "
                 f"{L(Wd['kanalizacja']['Q_ww_l_s'], 2)}", jedn="l/s", wymaganie="—", podstawa="PN-EN 12056-2 [W-138]",
                 spelnia=None),
            wk(D, "kanalizacja", "Przykanalik: napełnienie"),
            wk(D, "kanalizacja", "Przykanalik: prędkość"),
            wk(D, "kanalizacja", "Najniższy wpust/przybór powyżej poziomu piętrzenia"),
            dict(parametr="Dachy: A / Q (r = 0,046 l/(s·m²))", wartosc=f"{L(Wd['deszczowa']['A_dachow_m2'], 1)} m² / "
                 f"{L(Wd['deszczowa']['Q_dachy_l_s'], 2)} l/s", jedn="", wymaganie="—",
                 podstawa="PN-EN 12056-3 [W-142]", spelnia=None),
            wk(D, "deszczowa", "Pojemność szczelnego zbiornika", miejsca=1),
            wk(D, "deszczowa", "Niecka: pojemność", miejsca=2),
            wk(D, "deszczowa", "Niecka: czas opróżniania", miejsca=1)]
    o.rozdzial("Zestawienie wyników i dobór urządzeń", poziom=2, podstawa="§ 23 pkt 8 lit. b RPB")
    o.dok.tabela_wynikow([r for r in rows if r], tytul="Podstawowe wyniki obliczeń i sprawdzeń PT-3 IS",
                         uwagi="Pełne sprawdzenia (wszystkie warunki) — w podrozdziałach obliczeń poniżej.",
                         zrodlo="lamela.obliczenia — uruchomienie przy generowaniu tomu")
    o.md.append("**Podstawowe wyniki** (tabela w PDF):\n\n" + "\n".join(
        f"* {r['parametr']}: {r['wartosc'] if isinstance(r['wartosc'], str) else L(r['wartosc'], r.get('miejsca', 2))}"
        f" {r['jedn']} ({r['wymaganie']}; {r['podstawa']})" for r in rows if r))
    from lamela.obliczenia.energia.obciazenie_cieplne import raport_obciazenie
    from lamela.obliczenia.energia.wentylacja import raport_wentylacja
    Z = D.R["zal"]
    wstaw_raport(o, raport_obciazenie(obc, Z["obc"]), tytul="Obliczenia: obciążenie cieplne pomieszczeń i budynku",
                 podstawa="PN-EN 12831; W-150, W-151", zrodlo="lamela.obliczenia.energia.obciazenie_cieplne")
    wstaw_raport(o, D.W["ogrzewanie"].raport_md(), tytul="Obliczenia: pompa ciepła, ogrzewanie podłogowe, bufor, "
                 "naczynia, hałas", podstawa="W-152…W-156, W-024", zrodlo="lamela.obliczenia.sanitarne.ogrzewanie")
    wstaw_raport(o, raport_wentylacja(w, Z["went"]), tytul="Obliczenia: wentylacja — bilans powietrza i dobór centrali",
                 podstawa="W-160…W-169", zrodlo="lamela.obliczenia.energia.wentylacja")
    wstaw_raport(o, D.W["woda"].raport_md(), tytul="Obliczenia: instalacja wodociągowa i c.w.u.",
                 podstawa="W-130…W-137", zrodlo="lamela.obliczenia.sanitarne.woda")
    wstaw_raport(o, D.W["kanalizacja"].raport_md(), tytul="Obliczenia: kanalizacja sanitarna",
                 podstawa="W-138…W-141", zrodlo="lamela.obliczenia.sanitarne.kanalizacja")
    wstaw_raport(o, D.W["deszczowa"].raport_md(), tytul="Obliczenia: wody opadowe, retencja (IMGW, PANDa)",
                 podstawa="PN-EN 12056-3; W-142…W-146", zrodlo="lamela.obliczenia.sanitarne.deszczowa")
    wstaw_raport(o, D.W["drenaz"].raport_md(), tytul="Obliczenia: drenaż i odwodnienie powierzchniowe",
                 podstawa="W-019", zrodlo="lamela.obliczenia.sanitarne.drenaz")


def rozdz_ep(o: Opis, D: DanePTIS):
    """6. Charakterystyka energetyczna budynku (§ 23 pkt 11 lit. a–d RPB; W-251)."""
    from lamela.obliczenia.energia import ep as EP
    ep, ep0, s, b = D.ep, D.ep0, D.ep.system, D.W["bilans"]
    o.rozdzial("Charakterystyka energetyczna budynku", podstawa="§ 23 pkt 11 RPB; W-240…W-251", nowa_strona=True)
    o.tekst(f"""
    Charakterystykę energetyczną opracowano wg metodologii (Dz.U. 2015 poz. 376 ze zm., ost. 2023 poz. 697; W-241)
    dla A_f = {L(ep.A_f, 1)} m² (bez garażu nieogrzewanego), metodą miesięczną z danymi klimatycznymi Poznań.
    Wariant projektowy **A** obejmuje instalację fotowoltaiczną (projektowaną w PT-4 IE); ponieważ energia z PV
    liczona jest tylko w części autokonsumowanej, a instalacja PV może nie zostać wykonana razem z budynkiem,
    **wariant A0 bez PV podano jawnie** — oba warianty sprawdzono względem EP_max. Dane urządzeń (SCOP, η_t,
    moce pomocnicze) z kart wyrobów przykładowych {FIKCJA} — przed wydaniem do realizacji zastąpić danymi
    deklarowanymi wybranych wyrobów (W-242) i przeliczyć.
    """)
    o.rozdzial("Bilans mocy urządzeń elektrycznych i zużywających inne rodzaje energii", poziom=2,
               podstawa="§ 23 pkt 11 lit. a RPB")
    rows = [{"Odbiornik": x.nazwa, "Grupa": x.grupa, "P [kW]": x.P, "Faz": x.fazy} for x in b.odbiorniki
            if not x.generacja and x.P >= 0.5]
    rows.append({"Odbiornik": "Moc zainstalowana (wszystkie odbiorniki)", "Grupa": "", "P [kW]": b.P_inst, "Faz": "",
                 "_klasa": "suma"})
    rows.append({"Odbiornik": "Moc szczytowa z układem ograniczania mocy (DLM)", "Grupa": "", "P [kW]": b.P_s_dlm,
                 "Faz": "", "_klasa": "suma"})
    o.tabela(rows, tytul="Bilans mocy — odbiorniki ≥ 0,5 kW (instalacje stałe budynku)", formaty={"P [kW]": 2},
             wyrownanie={"Odbiornik": "l", "Grupa": "l"},
             uwagi=f"Moc przyłączeniowa {L(b.P_przyl, 0)} kW, zabezpieczenie przedlicznikowe {L(b.I_zab, 0)} A — PT-4 IE. "
                   "Budynek nie ma urządzeń zużywających paliwa (gaz, olej, biomasa) ani urządzeń technologicznych.",
             zrodlo="lamela.obliczenia.elektryka.bilans (odczyt; obliczenia PT-4 IE)")
    o.rozdzial("Właściwości cieplne przegród zewnętrznych", poziom=2, podstawa="§ 23 pkt 11 lit. b RPB; W-243, W-244")
    seen, rowsU = set(), []
    for (kod, rola), wu in sorted(D.R["obudowa"].u.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        if (kod, rola) not in D.R["obudowa"].klucze_ogrz or rola in ("sciana_wewn", "strop_wewn") or kod in seen:
            continue
        seen.add(kod)
        rowsU.append({"Przegroda": kod.split("|")[0], "Rodzaj": rola.replace("_", " "), "U [W/(m²·K)]": wu.U,
                      "U_max [W/(m²·K)]": wu.U_max, "Spełnia": "tak" if wu.spelnia_WT else "NIE"})
    o.tabela(rowsU, tytul="Współczynniki przenikania ciepła przegród obudowy (szczegóły — PT-1 AR)",
             formaty={"U [W/(m²·K)]": 3, "U_max [W/(m²·K)]": 2}, wyrownanie={"Rodzaj": "l"},
             uwagi=f"Mostki cieplne: H_TB = {L(D.R['obudowa'].H_TB, 1)} W/K (Ψ z symulacji PN-EN ISO 10211 — "
                   "projekt/08_obliczenia/mostki); U podłogi na gruncie wg PN-EN ISO 13370.",
             zrodlo="lamela.obliczenia.energia.obudowa; WT zał. 2 pkt 1.1–1.2")
    o.rozdzial("Parametry sprawności energetycznej instalacji", poziom=2, podstawa="§ 23 pkt 11 lit. c RPB")
    og = D.Wd["ogrzewanie"]
    rows = [{"Instalacja": "Ogrzewanie", "Wytwarzanie η_g": s.eta_H_g, "Akumulacja η_s": s.eta_H_s,
             "Przesył η_d": s.eta_H_d, "Regulacja η_e": s.eta_H_e, "Łącznie η_tot": s.eta_H_tot},
            {"Instalacja": "Ciepła woda użytkowa", "Wytwarzanie η_g": s.eta_W_g, "Akumulacja η_s": s.eta_W_s,
             "Przesył η_d": s.eta_W_d, "Regulacja η_e": None, "Łącznie η_tot": s.eta_W_tot}]
    o.tabela(rows, tytul="Sprawności cząstkowe systemów (wariant projektowy A)",
             formaty={k: 2 for k in rows[0] if k != "Instalacja"},
             uwagi=[f"Źródło ogrzewania: {s.zrodlo_H}", f"C.w.u.: {s.zrodlo_W or 'wg modułu wody (η_W,d, zasobnik)'}",
                    f"Wentylacja: odzysk ciepła η_oc = {L(ep.eta_oc, 2)}; pomocnicze: "
                    + "; ".join(f"{p.opis} {L(p.P_W, 0)} W" for p in s.pomocnicze),
                    f"Moduł ogrzewania (bilans godzinowy TMY): SCOP obliczeniowy {L(og['SCOP_obl_TMY'], 2)} "
                    f"(deklarowany {L(og['SCOP_dekl'], 2)}), η_H,e = {L(og['do_EP']['eta_H_e'], 2)}, "
                    f"η_H,d = {L(og['do_EP']['eta_H_d'], 2)} — do ujednolicenia z EP po wyborze wyrobu."],
             zrodlo="lamela.obliczenia.energia.ep — metodologia tab. 2, 3, 6, 8, 12, 14")
    o.rozdzial("Wskaźniki EP, EK, EU, udział OZE — spełnienie wymagań", poziom=2,
               podstawa="§ 23 pkt 11 lit. d RPB; WT § 328–329 (W-240)")
    war = [w for w in D.R["ep_alt"]] + list(D.R["ep_wrazliwosc"])
    rows = [{"Wariant": x.system.nazwa, "EU": x.EU, "EK": x.EK, "EP": x.EP, "EP_max": x.EP_max, "U_OZE [%]": x.U_oze,
             "E_CO2 [t/rok]": x.E_CO2_t, "EP ≤ EP_max": "tak" if x.spelnia else "NIE",
             "_klasa": "suma" if x is ep else ("pod" if x is ep0 else None)} for x in war]
    o.tabela(rows, tytul="Charakterystyka energetyczna — wariant projektowy, wariant bez PV, alternatywy i wrażliwość "
             "[kWh/(m²·rok)]", formaty={"EU": 1, "EK": 1, "EP": 1, "EP_max": 1, "U_OZE [%]": 1, "E_CO2 [t/rok]": 2},
             wyrownanie={"Wariant": "l"},
             uwagi=["A — wariant projektowy (z PV); A0 — ten sam budynek i instalacje bez PV; B, C — analiza alternatyw "
                    "(RPB § 20 ust. 1 pkt 10, PAB); ostatnie wiersze — wrażliwość (szczelność, Ψ)."],
             zrodlo="lamela.obliczenia.energia.ep (metodologia Dz.U. 2015 poz. 376 ze zm.)")
    tekst = (f"Wariant projektowy A: EP = **{L(ep.EP, 1)}** kWh/(m²·rok) "
             f"{'≤' if ep.spelnia else '>'} EP_max = {L(ep.EP_max, 1)} — wymaganie {'spełnione' if ep.spelnia else 'NIESPEŁNIONE'}.")
    if ep0:
        tekst += (f" Wariant A0 bez PV: EP = **{L(ep0.EP, 1)}** kWh/(m²·rok) "
                  f"{'≤' if ep0.spelnia else '>'} EP_max — {'wymaganie spełnione także bez instalacji PV' if ep0.spelnia else 'bez PV wymaganie NIESPEŁNIONE — PV jest warunkiem spełnienia WT'}.")
    o.wniosek(tekst, alarm=not (ep.spelnia and (ep0 is None or ep0.spelnia)))
    kat = KAT_ZRODLA / "obliczenia"
    kat.mkdir(parents=True, exist_ok=True)
    EP.wykres_bilans(ep, kat / "bilans_energii.png")
    wstaw_raport(o, EP.raport_ep(ep, wykres="bilans_energii.png", zal=D.R["zal"]["ep"]), katalog=kat,
                 tytul="Obliczenia: charakterystyka energetyczna — wariant A", podstawa="W-240…W-242",
                 zrodlo="lamela.obliczenia.energia.ep")
    o.tekst("Dane do świadectwa charakterystyki energetycznej (centralny rejestr) przekazuje się po zakończeniu "
            "budowy na podstawie wyrobów wbudowanych i wyniku próby szczelności (W-251; PB art. 57 ust. 1 pkt 6a).")


def rozdz_ppoz(o: Opis, D: DanePTIS):
    """7. Dane dotyczące warunków ochrony przeciwpożarowej stosownie do zakresu PT-IS (§ 23 pkt 10 RPB)."""
    from lamela.obliczenia.wspolne import wymaganie
    zl, gw, zw = (wymaganie("ppoz", k) for k in ("kategoria_ZL", "grupa_wysokosci", "zwolnienie_213_kondygnacje_max"))
    n_k = len(D.B.get("kondygnacje", []))
    hyd = next((x for x in ((D.Dz.get("uzbrojenie") or {}).get("obiekty") or []) if x.get("id") == "HYDR"), {})
    o.rozdzial("Dane dotyczące warunków ochrony przeciwpożarowej", podstawa="§ 23 pkt 10 RPB", nowa_strona=True)
    o.tekst(f"""
    Budynek mieszkalny jednorodzinny: kategoria zagrożenia ludzi **{zl.wartosc}** ({zl.zrodlo}), grupa wysokości
    **{gw.wartosc}** ({gw.zrodlo}), {n_k} kondygnacje nadziemne — {'zwolniony' if n_k <= zw.wartosc else 'NIE zwolniony'}
    z wymagań klasy odporności pożarowej ({zw.zrodlo}; {zw.id}). W zakresie PT-3 IS:

    * przejścia instalacji przez stropy i ściany — bez wymagań odporności ogniowej przepustów (brak wymagań
      klasy odporności elementów, jw.); przejścia uszczelnione akustycznie i szczelnie powietrznie (W-249);
    * przewody wentylacyjne z materiałów palnych dopuszczalne w budynku jednorodzinnym jednolokalowym (W-168);
      centrala w wydzielonym pomieszczeniu technicznym;
    * pompa ciepła z czynnikiem palnym R290 (klasa A3 wg PN-EN 378-1+A1:2021-03): jednostka zewnętrzna poza
      budynkiem, strefa bezpieczeństwa wg DTR (typowo 1,0 m) wolna od otworów, wpustów, studzienek i źródeł
      zapłonu (W-156) — sprawdzenie w obliczeniach ogrzewania; instalacja wewnętrzna wyłącznie wodna (monoblok);
    * brak instalacji gazowej i urządzeń spalania paliw — nie występują przewody spalinowe;
    * zaopatrzenie w wodę do zewnętrznego gaszenia pożaru: {hyd.get('opis', 'wg PZT')} (dane PZT) — instalacja
      wodociągowa budynku nie pełni funkcji przeciwpożarowej (brak hydrantów wewnętrznych — nie wymagane).
    """)


def rozdz_urzadzenia(o: Opis, D: DanePTIS):
    """8. Zasadnicze urządzenia — parametry wymagane (§ 23 pkt 9 RPB); wyroby przykładowe lub równoważne."""
    og, pc, w, Wd = D.og, D.og.pc, D.went, D.Wd
    c = w.centrala or {}
    Pm15 = dict(zip(pc["T"], pc["P"])).get(-15)
    wymP = D.obc.Phi_HL / 1000 + og.Phi_W
    ret = D.Dz.get("retencja") or {}
    o.rozdzial("Zasadnicze urządzenia — parametry wymagane", podstawa="§ 23 pkt 9 RPB; PB art. 10", nowa_strona=True)
    o.tekst("""
    Urządzenia określono **parametrami wymaganymi**. Wyroby przywołane w obliczeniach są przykładowe — dopuszcza
    się wyroby równoważne o parametrach nie gorszych, wprowadzone do obrotu zgodnie z PB art. 10 (deklaracja
    właściwości użytkowych / deklaracja zgodności, oznakowanie CE lub znak budowlany B). Zamiana wyrobu wymaga
    ponownego przeliczenia EP, punktu biwalentnego i hałasu (generator tomu przelicza je z modelu).
    """)
    rows = [
        {"Urządzenie": "Pompa ciepła powietrze–woda, monoblok",
         "Parametry wymagane": f"czynnik naturalny R290 (GWP < 150); P(A−15/W35) ≥ {L(Pm15, 1)} kW i pokrycie "
                               f"Φ_HL + Φ_W = {L(wymP, 2)} kW przy θ_e z grzałką ≤ {L(og.par.grzalka_kW, 0)} kW; "
                               f"SCOP₃₅ ≥ {L(pc.get('SCOP_35'), 1)}; η_s ≥ 125 %; L_WA ≤ {L(pc.get('L_WA'), 0)} dB "
                               "(tryb nocny niżej); regulacja pogodowa, sterowanie zależne od zapotrzebowania",
         "Podstawa": "W-155, W-156, W-024; (UE) 2024/573, 813/2013"},
        {"Urządzenie": "Zasobnik c.w.u. z wężownicą",
         "Parametry wymagane": f"V ≥ {Wd['woda']['zasobnik_l']} dm³, wężownica ≥ {L(D.W['woda'].cwu.get('A_wez'), 1)} m² "
                               "(dla PC), grzałka do dezynfekcji, grupa bezpieczeństwa, izolacja fabryczna",
         "Podstawa": "W-133, W-134; PN-EN 16147+A1:2023-06"},
        {"Urządzenie": "Bufor c.o. (szeregowy)", "Parametry wymagane": f"V ≥ {Wd['ogrzewanie']['bufor_l']} dm³, izolowany",
         "Podstawa": "obliczenia ogrzewania"},
        {"Urządzenie": "Naczynia wzbiorcze przeponowe",
         "Parametry wymagane": f"c.o. ≥ {og.naczynie_co.get('V_dob')} dm³ (p₀ {L(og.naczynie_co.get('p_0'), 2)} bar); "
                               f"c.w.u. ≥ {og.naczynie_cwu.get('V_dob')} dm³ (p₀ {L(og.naczynie_cwu.get('p_0'), 1)} bar), przepływowe",
         "Podstawa": "PN-B-02414:1999 (powołana w WT) [W-154]"},
        {"Urządzenie": "Rozdzielacze ogrzewania podłogowego",
         "Parametry wymagane": "; ".join(f"{r['kond']}: {r['petle']} obwodów, przepływomierze, siłowniki 230 V/24 V NC"
                                         for r in og.rozdzielacze), "Podstawa": "W-152, W-154"},
        {"Urządzenie": "Centrala wentylacyjna z odzyskiem ciepła",
         "Parametry wymagane": f"V_max ≥ {L(w.V_boost, 0)} m³/h przy sprężu instalacji; η_t ≥ {L(100 * (c.get('eta_t') or 0), 0)} %; "
                               f"SFP ≤ {L(w.SFP_lim_naw, 2)} kW/(m³/s); SEC klasa ≥ A; by-pass 100 %; filtry ISO ePM1 50 % "
                               "(nawiew), ISO Coarse (wywiew); L_WA wg PN-B-02151-2 w pokojach",
         "Podstawa": "W-160…W-169; (UE) 1253/2014; PN-EN 13141-7+A1:2026-05"},
        {"Urządzenie": "Zestaw wodomierzowy",
         "Parametry wymagane": f"wodomierz {Wd['woda']['wodomierz']} (lub wg warunków gestora), zawory, filtr, EA; "
                               f"reduktor ciśnienia {'wymagany' if D.W['woda'].cisnienia.get('reduktor') else 'niewymagany'}",
         "Podstawa": "W-131, W-130; PN-EN 1717"},
        {"Urządzenie": "Zbiornik retencyjny wód opadowych",
         "Parametry wymagane": f"szczelny, V = {L((ret.get('zbiornik') or {}).get('V'), 1)} m³ (≤ 5 m³), osadnik, filtr, "
                               "pompa zatapialna do podlewania, przelew do niecki, właz z zabezpieczeniem",
         "Podstawa": "W-145; PW art. 16 pkt 65 lit. f"},
    ]
    o.tabela(rows, tytul="Zasadnicze urządzenia instalacji sanitarnych", wyrownanie={"Parametry wymagane": "l"},
             szerokosci=["38mm", None, "40mm"], uwagi=f"Dane liczbowe urządzeń przykładowych: {FIKCJA}.",
             zrodlo="model (instalacje.yaml, wyposazenie.yaml, dzialka.yaml); lamela.obliczenia")


def rozdz_proby(o: Opis, D: DanePTIS):
    """9. Próby, badania i odbiory."""
    o.rozdzial("Próby, badania i odbiory", podstawa="PB art. 57 ust. 1; C.3 rejestru", nowa_strona=True)
    o.tekst(f"""
    Roboty wykonywać zgodnie z PT, instrukcjami producentów wyrobów i zasadami wiedzy technicznej; odbiory
    częściowe przed zakryciem (przewody w posadzkach, bruzdach, pod płytą) z wpisem do dziennika budowy.

    1. **Instalacja wodociągowa** — próba szczelności przed zakryciem przewodów (kontrolnie PN-EN 806-4;
       ciśnienie próbne wg instrukcji systemu rur, nie niższe niż 1,5 × ciśnienie robocze); płukanie
       i dezynfekcja; badanie jakości wody przed oddaniem do użytkowania; protokół nastawy reduktora
       i sprawdzenia zaworu EA (PN-EN 1717).
    2. **Kanalizacja sanitarna** — próba szczelności przewodów pod posadzką i przykanalika przed zasypaniem
       (PN-EN 1610:2015-10), sprawdzenie spadków i rzędnych (inwentaryzacja geodezyjna przyłącza),
       próba drożności pionów i działania zaworów napowietrzających.
    3. **Ogrzewanie podłogowe** — próba ciśnieniowa pętli przed wylaniem jastrychu (instalacja pod ciśnieniem
       w trakcie wylewania), wygrzewanie jastrychu wg protokołu, regulacja hydrauliczna (nastawy przepływów
       rozdzielaczy wg tabeli pętli), sprawdzenie działania termostatów i siłowników w każdym pomieszczeniu.
    4. **Pompa ciepła** — montaż i uruchomienie przez serwis upoważniony przez producenta (czynnik R290),
       sprawdzenie strefy bezpieczeństwa, odprowadzenia skroplin i zabezpieczenia przed zamarzaniem; protokół
       uruchomienia z nastawami krzywej grzewczej i programu dezynfekcji c.w.u.
    5. **Wentylacja mechaniczna** — sprawdzenie szczelności i czystości przewodów, pomiar i regulacja
       strumieni powietrza na nawiewnikach i wywiewnikach (tolerancja ±10 % wartości projektowych — tabela
       strumieni), pomiar poziomu dźwięku w pokojach (PN-B-02151-2:2018-01), protokół regulacji.
    6. **Wody opadowe** — próba szczelności zbiornika i przewodów deszczowych, sprawdzenie przelewów awaryjnych
       dachów, działania niecki (czas opróżniania) i odwodnień liniowych.
    7. **Szczelność budynku** — próba ciśnieniowa n50 (PN-EN ISO 9972) przed wykończeniem; wynik warunkuje
       przyjętą wartość n50 = {L(D.obc.n50, 1)} h⁻¹ w charakterystyce energetycznej (W-249).
    8. **Dokumentacja odbiorowa** — protokoły prób i badań, DWU/deklaracje wbudowanych wyrobów, DTR i karty
       gwarancyjne urządzeń, instrukcja obsługi instalacji dla użytkownika, dokumentacja powykonawcza (PT
       z naniesionymi zmianami), dane do świadectwa charakterystyki energetycznej (C.3 rejestru).
    """)


def rozdz_braki(o: Opis, D: DanePTIS):
    """10. Dane do uzupełnienia i uzgodnienia międzybranżowe."""
    o.rozdzial("Dane do uzupełnienia i uzgodnienia międzybranżowe", podstawa="rejestr wymagań, sekcje D i E", nowa_strona=True)
    o.tekst("Uzgodnienia: PT-1 AR (przejścia przez przegrody, szachty, wyłaz), PT-2 BO (przejścia przez płytę "
            "fundamentową i stropy, podstawy urządzeń), PT-4 IE (zasilanie PC, grzałki, centrali, sterowników; "
            "połączenia wyrównawcze rur metalowych). Braki modelu zgłoszone przez generator rysunków IS "
            f"(`projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md`, stan z dnia generowania rysunków):")
    rows = D.braki_tabela()
    if rows:
        o.tabela(rows, tytul="Braki danych modelu — rysunki IS", wyrownanie={"Element": "l", "Brak / stan w modelu": "l"},
                 szerokosci=["8mm", "38mm", None, "30mm"],
                 uwagi="Pozycje wyznaczone algorytmicznie są na rysunkach oznaczone znacznikiem braku danych (linia kreskowa purpurowa, warstwa I-BRAKI). "
                       "Pozycje nieaktualne wobec bieżących obliczeń — patrz „Stan opracowania i sprawy otwarte”.",
                 zrodlo="projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md")
    if D.ark_info:
        o.tekst("Uwagi kontroli arkuszy (raport_widokow.json):\n\n" + "\n".join(f"* {u}" for u in D.ark_info))
