"""PAB — rozdział 4: charakterystyczne parametry obiektu (RPB § 20 ust. 1 pkt 4 lit. a–e). Liczby z ``DanePAB``."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, liczba as L, rzedna
from lamela.dokumenty.znaczniki import INT

from pab_opis_a import KAT_OPIS, tyt

KOL_POM = ["Nr", "Pomieszczenie", "Kategoria", "h w świetle [m]", "Pow. netto [m²]", "Współczynnik", "Pow. do PU [m²]", "Uwagi"]


def _h(r) -> str:
    """Wysokość w świetle albo strefa wysokości (pomieszczenia pod biegiem schodów — audyt A1, próbkowanie 0,25 m)."""
    if r.get("schody"):
        st = r.get("strefy") or {}
        z = [k for k, v in st.items() if v > 1e-6]
        return "strefa " + ", ".join(z) if z else "—"
    return L(r["h"]) if r.get("h") is not None else "—"


def _uwagi(D, r) -> str:
    g = D.grupa_pu(r)
    if g == "garaż":
        return "poza PU — garaż"
    if g == "techniczna":
        return "poza PU — pomieszczenie techniczne / szacht"
    if g == "klatka schodowa":
        return "poza PU — schody wewn. i podesty"
    if r["pow"] > 0 and r["pow_zal"] < r["pow"] - 1e-6:
        return "h 1,40–2,20 m — 50 %" if r["pow_zal"] > 1e-6 else "h < 1,40 m — 0 %"
    return ""


def sumy(D) -> dict:
    s = {g: 0.0 for g in ("podstawowa", "pomocnicza", "komunikacja", "klatka schodowa", "garaż", "techniczna")}
    s_n = dict(s)
    for r in D.pom:
        g = D.grupa_pu(r)
        s[g] += r["pow_zal"] if g not in ("klatka schodowa",) else 0.0
        s_n[g] += r["pow"]
    pu = s["podstawowa"] + s["pomocnicza"] + s["komunikacja"]
    red = sum(r["pow"] - r["pow_zal"] for r in D.pom if D.w_pu(r))
    return dict(s=s, netto=s_n, pu=pu, red=red, netto_razem=sum(r["pow"] for r in D.pom))


def r04(pab, D, d):
    w, S = D.w, sumy(D)
    if abs(S["pu"] - D.pu.get("PU_mieszkalna", S["pu"])) > 0.05:
        D.otwarte.append(f"PU: suma z tabeli pomieszczeń {L(S['pu'])} m² ≠ audyt A1 {L(D.pu.get('PU_mieszkalna'))} m² — "
                         "sprawdzić reguły grup W-316.")
    pab.rozdzial(tyt("Charakterystyczne parametry obiektu budowlanego", 4))
    # a) kubatura
    sk = D.kub["skladniki"]
    pab.markdown(f"""
    ## Kubatura (lit. a)

    Kubatura brutto budynku **V = {L(D.kubatura)} m³** — objętość ograniczona zewnętrznymi powierzchniami przegród, od spodu
    warstwy konstrukcyjnej podłogi najniższej kondygnacji do wierzchu płyt dachowych z warstwami, bez attyk i elementów
    wysuniętych (PN-ISO 9836; algorytm `lamela.model.kubatura_brutto`, suma składników kondygnacji i płyt). Kubatura obejmuje
    garaż i pomieszczenia techniczne (jedna strefa pożarowa — rozdz. 13).
    """)
    pab.tabela([{"Składnik": k.replace("plyta", "płyta"), "Kubatura [m³]": v} for k, v in sk.items()],
               tytul="Składniki kubatury brutto", suma=["Kubatura [m³]"], szerokosci=[None, "35mm"],
               zrodlo="model/budynek.yaml — lamela.model.kubatura_brutto()")
    # b) zestawienie powierzchni
    pk = w["pow_kondygnacji"]["wartosc"]
    rows = [{"Pozycja": "Powierzchnia zabudowy (informacyjnie — PZT)", "Powierzchnia [m²]": w["pow_zabudowy"]["wartosc"],
             "Podstawa / reguła": w["pow_zabudowy"]["podstawa"]},
            {"_klasa": "grupa", "Pozycja": "Powierzchnia całkowita (Σ kondygnacji po obrysie zewnętrznym, bez tarasów, "
             "balkonów i loggii)", "Powierzchnia [m²]": w["suma_pow_kondygnacji"]["wartosc"],
             "Podstawa / reguła": "PN-ISO 9836; RPB § 20 ust. 1 pkt 4 lit. b tiret 5"}]
    rows += [{"_klasa": "pod", "Pozycja": f"   w tym {D.wym_kond[k]['nazwa']}", "Powierzchnia [m²]": v,
              "Podstawa / reguła": "obrys ścian zewnętrznych kondygnacji"} for k, v in pk.items()]
    rows += [{"Pozycja": "Powierzchnia netto pomieszczeń (Σ)", "Powierzchnia [m²]": S["netto_razem"],
              "Podstawa / reguła": "lica ścian wykończonych (audyt A1)"},
             {"_klasa": "suma", "Pozycja": "POWIERZCHNIA UŻYTKOWA lokalu mieszkalnego (PU)", "Powierzchnia [m²]": S["pu"],
              "Podstawa / reguła": "PN-ISO 9836:2022 z modyfikacjami RPB § 20 ust. 1 pkt 4 lit. b (W-316)"},
             {"_klasa": "pod", "Pozycja": "   w tym pomieszczenia podstawowe", "Powierzchnia [m²]": S["s"]["podstawowa"],
              "Podstawa / reguła": "z wagą wysokości"},
             {"_klasa": "pod", "Pozycja": "   w tym pomieszczenia pomocnicze (z szafami, schowkami, garderobą)",
              "Powierzchnia [m²]": S["s"]["pomocnicza"], "Podstawa / reguła": "lit. b tiret 2–3"},
             {"_klasa": "pod", "Pozycja": "   w tym komunikacja wewnętrzna (bez schodów i podestów)",
              "Powierzchnia [m²]": S["s"]["komunikacja"], "Podstawa / reguła": "lit. b tiret 1"},
             {"Pozycja": "Garaż (poza PU)", "Powierzchnia [m²]": S["s"]["garaż"], "Podstawa / reguła": "W-316 — osobno"},
             {"Pozycja": "Pomieszczenia techniczne i szachty (poza PU)", "Powierzchnia [m²]": S["s"]["techniczna"],
              "Podstawa / reguła": "W-316 — osobno"},
             {"Pozycja": "Schody wewnętrzne i podesty w lokalu wielopoziomowym (poza PU)",
              "Powierzchnia [m²]": S["netto"]["klatka schodowa"], "Podstawa / reguła": "lit. b tiret 1"},
             {"Pozycja": "Pomniejszenie PU z tytułu wysokości (h < 2,20 m)", "Powierzchnia [m²]": S["red"],
              "Podstawa / reguła": "lit. b tiret 3 (50 % / 0 %)"}]
    pab.markdown("## Zestawienie powierzchni (lit. b)")
    pab.tabela(rows, tytul="Zestawienie powierzchni budynku", szerokosci=[None, "26mm", "62mm"], klasa="zwarta",
               zrodlo="lamela.wskazniki (pow. zabudowy i kondygnacji); tools/audyt_wt.py (pomieszczenia, strefy wysokości)")
    tab = []
    for k in D.m.kondygnacje:
        rr = [r for r in D.pom if r["kond"] == k.id]
        tab.append(f"{k.nazwa} ({rzedna(float(k.rzedna))})")
        for r in sorted(rr, key=lambda x: x["id"]):
            tab.append({"Nr": D.nr_iso(r["id"], r["kond"]), "Pomieszczenie": r["nazwa"], "Kategoria": KAT_OPIS[D.grupa_pu(r)],
                        "h w świetle [m]": _h(r), "Pow. netto [m²]": r["pow"],
                        "Współczynnik": (r["pow_zal"] / r["pow"]) if (r["pow"] > 0 and D.w_pu(r)) else None,
                        "Pow. do PU [m²]": r["pow_zal"] if D.w_pu(r) else None, "Uwagi": _uwagi(D, r)})
        tab.append({"_klasa": "pod", "Nr": "", "Pomieszczenie": f"Razem {k.nazwa.lower()}", "Kategoria": "",
                    "h w świetle [m]": "", "Pow. netto [m²]": sum(r["pow"] for r in rr), "Współczynnik": None,
                    "Pow. do PU [m²]": sum(r["pow_zal"] for r in rr if D.w_pu(r)), "Uwagi": ""})
    tab.append({"_klasa": "suma", "Nr": "", "Pomieszczenie": "RAZEM budynek", "Kategoria": "", "h w świetle [m]": "",
                "Pow. netto [m²]": S["netto_razem"], "Współczynnik": None, "Pow. do PU [m²]": S["pu"], "Uwagi": ""})
    pab.tabela(tab, KOL_POM, tytul="Zestawienie pomieszczeń (z modelu)", klasa="zwarta",
               formaty={"Współczynnik": 2}, wyrownanie={"h w świetle [m]": "r"},
               szerokosci=["10mm", None, "23mm", "17mm", "16mm", "15mm", "16mm", "33mm"],
               uwagi=["Numeracja wg PN-B-01025 (parter = 1.xx; identyfikator modelu K.NN → K+1.NN). Współczynnik: h ≥ 2,20 m — "
                      "1,00; 1,40 ≤ h < 2,20 m — 0,50; h < 1,40 m — 0 (RPB § 20 ust. 1 pkt 4 lit. b tiret 3). Pomieszczenia pod "
                      "biegiem schodów — powierzchnie stref wysokości z próbkowania geometrii (audyt A1)."],
               zrodlo="model/budynek.yaml; tools/audyt_wt.py")
    _wysokosc(pab, D)


def _wysokosc(pab, D):
    w = D.w
    hz, h6 = w["wysokosc_zabudowy"], w["wysokosc_WT6"]
    z0 = float(D.m.zero_abs)
    pab.markdown("## Wysokość, długość, szerokość, liczba kondygnacji (lit. c–d)")
    pab.tabela([
        {"Parametr": "Wysokość zabudowy", "Wartość [m]": hz["wartosc"],
         "Sposób wyznaczenia": f"od średniej rzędnej terenu na obwodzie ścian zewn. t_śr = ({L(hz['t_min'], 2)} + "
         f"{L(hz['t_max'], 2)}) / 2 = {L(hz['t_sr'], 2)} m n.p.m. do najwyższego punktu: {hz['element']} "
         f"({L(hz['z_top_abs'], 2)} m n.p.m.)", "Podstawa": hz["podstawa"]},
        {"Parametr": "Wysokość budynku wg WT", "Wartość [m]": h6["wartosc"],
         "Sposób wyznaczenia": f"od terenu przy najniżej położonym wejściu ({h6['wejscie']}, {L(h6['H_teren'], 2)} m n.p.m.) "
         f"do górnej powierzchni stropodachu {h6['dach']} z warstwami; grupa wysokości: niski ({h6['grupa']})",
         "Podstawa": "WT § 6, § 8 pkt 1"},
        {"Parametr": "Długość × szerokość budynku", "Wartość [m]": f"{L(D.wymiary['dl'])} × {L(D.wymiary['szer'])}",
         "Sposób wyznaczenia": "obrys zewnętrzny ścian wszystkich kondygnacji (kierunek W–E × N–S); z płytami wysuniętymi "
         f"i okapami {L(D.wymiary['dl_calk'])} × {L(D.wymiary['szer_calk'])} m", "Podstawa": "lit. c; lamela.wskazniki"},
        {"Parametr": "Liczba kondygnacji", "Wartość [m]": f"{w['kondygnacje_nadziemne']['wartosc']} nadziemne, 0 podziemnych",
         "Sposób wyznaczenia": "kondygnacje niezagłębione poniżej terenu", "Podstawa": w["kondygnacje_nadziemne"]["podstawa"]},
    ], tytul="Wysokość, wymiary i liczba kondygnacji", wyrownanie={"Wartość [m]": "r"}, klasa="zwarta",
        szerokosci=["30mm", "22mm", None, "40mm"],
        uwagi=[f"Poziom ±0,000 = {L(z0, 2)} m n.p.m. (posadzka parteru). Rzędne terenu {DANE_PRZYKLADOWE} — wg mapy do "
               f"celów projektowych. Średnica — nie dotyczy."], zrodlo="lamela.wskazniki (upzp art. 2 pkt 30 lit. a; WT § 6)")
    pab.markdown("## Dane dotyczące usytuowania niezbędne do oceny wymagań ochrony przeciwpożarowej (lit. e)")
    rows = [{"Budynek sąsiedni (działka)": f"{s['nr']} — {s['opis']}", "Odl. od ścian [m]": s["d"],
             "Odl. od płyt wysuniętych [m]": s["d_pl"], "Wymaganie [m]": D.v("usytuowanie", "odl_ppoz_ZL_ZL"),
             "Ocena": "spełnia" if min(s["d"], s["d_pl"]) >= D.v("usytuowanie", "odl_ppoz_ZL_ZL") else "NIE SPEŁNIA"}
            for s in D.sasiedzi]
    pab.tabela(rows, tytul="Odległości od budynków na działkach sąsiednich", klasa="zwarta",
               szerokosci=[None, "20mm", "24mm", "20mm", "18mm"], zrodlo="model/dzialka.yaml: sasiedzi " + DANE_PRZYKLADOWE,
               uwagi=[f"Wymaganie: {D.zr('usytuowanie', 'odl_ppoz_ZL_ZL')}; ściany zewnętrzne i przekrycie dachu projektowane "
                      "jako nierozprzestrzeniające ognia (bez zwiększenia odległości wg WT § 271 ust. 2; W-213). Położenie "
                      f"budynków sąsiednich — do potwierdzenia na mapie do celów projektowych {INT}."])
    pab.tabela([{"Granica": f"{o['kier']}", "Elementy": o["grupa"], "Min. odległość [m]": o["d"],
                 "Element": o["el"], "Wymaganie [m]": o["lim"], "Ocena": "spełnia" if o["d"] >= o["lim"] - 1e-6 else "NIE SPEŁNIA"}
                for o in D.odl_min], tytul="Najmniejsze odległości od granic działki (bez granicy z drogą)",
               klasa="zwarta", szerokosci=["16mm", None, "22mm", "18mm", "20mm", "18mm"],
               uwagi=[f"Ściany z otworami ≥ {L(D.v('usytuowanie', 'odl_granica_z_otworami'))} m "
                      f"({D.zr('usytuowanie', 'odl_granica_z_otworami')}); bez otworów ≥ "
                      f"{L(D.v('usytuowanie', 'odl_granica_bez_otworow'))} m ({D.zr('usytuowanie', 'odl_granica_bez_otworow')}); "
                      f"okapy, gzymsy, tarasy ≥ {L(D.v('usytuowanie', 'odl_granica_okap_gzyms_balkon_schody'))} m "
                      f"({D.zr('usytuowanie', 'odl_granica_okap_gzyms_balkon_schody')}); dla płyt wysuniętych i okapów przyjęto "
                      "wymaganie ostrzejsze (założenie projektowe audytu A1). Od granicy z drogą — linia zabudowy MPZP (rozdz. 3)."],
               zrodlo="tools/audyt_wt.py (odległości każdej płaszczyzny ściany i elementu)")
