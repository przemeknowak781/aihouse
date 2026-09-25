"""PT-4 IE — część opisowa D: wyroby i parametry wymagane (wyroby przykładowe — lub równoważne), próby, pomiary
i odbiory (PN-HD 60364-6, PN-EN 62446-1), braki danych i zgodność rysunków z obliczeniami. Liczby z ``DanePTIE``."""
from __future__ import annotations

from pt_ie_dane import L, DanePTIE, Opis

from lamela.obliczenia.elektryka.bilans import U0

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"


def _w(D: DanePTIE, modul: str, fragment: str):
    return next((x for x in D.warunki(modul) if fragment in x.opis), None)


def rozdz_wyroby(o: Opis, D: DanePTIE):
    """13. Wyroby i parametry wymagane."""
    m, f, spd = D.pv.par.modul, D.pv.par.falownik, D.obw.spd
    icn = _w(D, "obwody", "zdolność łączeniowa")
    ev = next((x for x in D.obw.obwody if x.odb.grupa == "ev"), None)
    o.rozdzial("Wyroby i parametry wymagane", podstawa="PB art. 10; wyroby przykładowe — lub równoważne",
               nowa_strona=True)
    o.tekst(f"""
    Tom nie wskazuje nazw handlowych. Parametry urządzeń przyjęte w obliczeniach pochodzą z kart **wyrobów
    przykładowych** bibliotek obliczeniowych {FIKCJA}; wykonawca może zastosować dowolny wyrób spełniający parametry
    wymagane z tabeli, wprowadzony do obrotu zgodnie z przepisami o wyrobach budowlanych / o systemie oceny zgodności
    (DWU, deklaracja zgodności UE). Po wyborze wyrobów dane DTR wprowadzić do `model/instalacje.yaml` (`wyroby`)
    i przeliczyć tom (E-13).
    """)
    wiersze = [
        {"Wyrób": "Rozdzielnica główna RG", "Parametry wymagane": "PN-EN IEC 61439-3; ≥ IP40; rezerwa miejsca "
         f"≥ {L(100 * D.obw.par.rezerwa, 0)} % modułów; szyna PE/N oddzielna (TN-S)"},
        {"Wyrób": "Wyłączniki nadprądowe, RCBO, RCD", "Parametry wymagane": "PN-EN 60898-1, PN-EN 61009-1, "
         f"PN-EN 61008-1; zdolność łączeniowa I_cn ≥ {L(icn.limit if icn else None, 0)} kA; charakterystyki i prądy "
         "znamionowe wg zestawienia obwodów; RCD typ A (min.), typ F/B dla urządzeń z przekształtnikami wg DTR"},
        {"Wyrób": "Ochronniki przepięć (SPD)", "Parametry wymagane": f"PN-EN IEC 61643-11:2026-04; {spd['RG']}"},
        {"Wyrób": "Przewody i kable", "Parametry wymagane": "YDYp / YDY 450/750 V (Cu); WLZ "
         f"{D.obw.wlz['przewod']} 0,6/1 kV w ziemi; H1Z2Z2-K (PN-EN 50618:2015-03) {L(D.pv.par.s_DC, 0)} mm² po stronie "
         "DC PV; przekroje obwodów odbiorczych wg zestawienia obwodów"},
        {"Wyrób": "Moduł fotowoltaiczny", "Parametry wymagane": f"P_max ≥ {L(m['P'], 0)} Wp; U_oc ≤ {L(m['U_oc'], 1)} V; "
         f"I_sc ≤ {L(m['I_sc'], 1)} A; wymiary ≤ {L(m['dl'], 3)} × {L(m['szer'], 3)} m; PN-EN IEC 61215, PN-EN IEC 61730"},
        {"Wyrób": "Falownik PV 3-fazowy", "Parametry wymagane": f"P_AC ≤ {L(f['P_AC'], 1)} kW; U_DC,max ≥ "
         f"{L(f['U_dc_max'], 0)} V; zakres MPPT obejmujący {L(D.pv.lancuchy['Umpp_min'], 0)}–"
         f"{L(D.pv.lancuchy['Umpp_max'], 0)} V; ≥ {f['n_mppt']} wejścia MPPT; I_MPPT ≥ {L(f['I_mppt_max'], 1)} A; "
         "certyfikat NC RfG (lista PTPiREE); PN-EN 50549-1; SPD DC i rozłącznik DC wbudowane lub zewnętrzne"},
        {"Wyrób": "Punkt ładowania EV", "Parametry wymagane": (f"tryb 3, PN-EN IEC 61851-1; {L(ev.odb.P, 0)} kW 3f; "
         "wejście DLM (ograniczenie prądu); detekcja prądu stałego RDC-DD 6 mA albo RCD typ B") if ev else "nie dotyczy"},
        {"Wyrób": "Czujki dymu", "Parametry wymagane": "autonomiczne, PN-EN 14604; zasilanie bateryjne 10-letnie "
         "lub sieciowe z podtrzymaniem [ZAŁ]"},
        {"Wyrób": "Uziom, przewody wyrównawcze", "Parametry wymagane": D.odg.uziom["material"]},
    ]
    o.tabela(wiersze, tytul="Wyroby — parametry wymagane (wyroby przykładowe — lub równoważne)",
             zrodlo="lamela.obliczenia.elektryka (dane przykładowe wyrobów), rejestr wymagań A.3")


def rozdz_proby(o: Opis, D: DanePTIE):
    """14. Próby, pomiary i odbiory."""
    typy = {}
    for x in D.obw.obwody:
        typy.setdefault(x.zab.replace("3P ", ""), x.I_a)
    o.rozdzial("Próby, pomiary i odbiory", podstawa="PN-HD 60364-6:2016-07; PN-EN 62446-1; W-199", nowa_strona=True)
    o.tekst(f"""
    Sprawdzenie odbiorcze instalacji wg PN-HD 60364-6:2016-07 przed przekazaniem do użytkowania: oględziny;
    ciągłość przewodów ochronnych i połączeń wyrównawczych; rezystancja izolacji (500 V DC, ≥ 1 MΩ); samoczynne
    wyłączenie zasilania — pomiar impedancji pętli zwarcia w najdalszym punkcie każdego obwodu; działanie i czas
    zadziałania RCD; kolejność faz; spadek napięcia (wyrywkowo); działanie PWP (odcięcie wszystkich obwodów, w tym AC
    falownika); rezystancja uziemienia (wartość orientacyjna z obliczeń R ≈ {L(D.odg.uziom['R'], 1)} Ω).
    Mikroinstalacja PV — wg PN-EN 62446-1 (ciągłość, U_oc i I_sc łańcuchów, rezystancja izolacji DC, dokumentacja
    systemu). Tor światłowodowy — pomiar tłumienności (≤ {L(D.v('elektryka', 'swiatlowod_tlumienie_toru_max'), 1)} dB),
    okablowanie strukturalne — pomiary kat. 6A (PN-EN 50173-4). Protokoły badań instalacji dołącza się do
    zawiadomienia o zakończeniu budowy (PB art. 57 ust. 1 pkt 4 lit. a).
    """)
    o.tabela([{"Zabezpieczenie": k, "I_a [A]": ia, "Z_s,max = U₀/I_a [Ω]": U0 / ia} for k, ia in sorted(typy.items())],
             tytul="Największa dopuszczalna impedancja pętli zwarcia (t ≤ 0,4 s)",
             formaty={"I_a [A]": 0, "Z_s,max = U₀/I_a [Ω]": 2},
             uwagi="Wartość zmierzoną w temperaturze otoczenia porównać z Z_s,max z uwzględnieniem wzrostu rezystancji "
                   "przewodów w temperaturze pracy (PN-HD 60364-6); wartości obliczeniowe Z_s obwodów — rozdz. „Obliczenia”.")


def rozdz_braki(o: Opis, D: DanePTIE):
    """15. Braki danych, założenia, zgodność rysunków z obliczeniami."""
    o.rozdzial("Braki danych i zgodność części rysunkowej", podstawa="rejestr wymagań E.1–E.2", nowa_strona=True)
    br = D.braki_tabela()
    if br:
        o.tabela(br, tytul="Braki danych modelu wykazane przy generowaniu rysunków (BRAKI_DANYCH.md)")
    else:
        o.tekst("Generator rysunków IE nie wykazał braków danych modelu (`projekt/06_PT_instalacje_elektryczne/"
                "BRAKI_DANYCH.md` — tabela pusta).")
    zal = sorted({z for k in ("bilans", "obwody", "pv", "odgromowa") for z in (getattr(D.W[k], "zalozenia", []) or [])
                  if "[ZAŁ" in str(z)})
    if zal:
        o.tekst("**Założenia projektowe do potwierdzenia [ZAŁ]** (z obliczeń):\n\n" + "\n".join(f"* {z}" for z in zal))
    o.rozdzial("Zgodność rysunków z bieżącymi obliczeniami", poziom=2)
    if D.rozb_rys:
        o.tekst("Kontrola automatyczna porównała treść arkuszy (schemat RG, opisy urządzeń) z wynikami obliczeń tomu. "
                "Wiążące są wartości z obliczeń (część opisowa); arkusze wymagają ponownego wygenerowania:\n\n"
                + "\n".join(f"* {r}" for r in D.rozb_rys))
    else:
        o.tekst("Kontrola automatyczna nie wykazała rozbieżności między arkuszami a bieżącymi obliczeniami.")
    if D.ark_info:
        o.tekst("Uwagi generatora arkuszy (raport_widokow.json):\n\n" + "\n".join(f"* {u}" for u in D.ark_info))
