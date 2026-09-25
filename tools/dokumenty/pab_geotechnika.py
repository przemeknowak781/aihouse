"""PAB — załącznik nr 1: opinia geotechniczna (kategoria II) — rozp. Dz.U. 2012 poz. 463 § 7 ust. 1, § 8.

Dane podłoża pochodzą WYŁĄCZNIE z sekcji ``geotechnika`` modelu (dane przykładowe — [DANE PRZYKŁADOWE – FIKCYJNE]);
autor opinii, jego kwalifikacje i metryki badań to pola [DO UZUPEŁNIENIA] (system nie fabrykuje osób ani wyników badań).
"""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, do_uzup, liczba as L
from lamela.dokumenty.znaczniki import ZAL

from pab_opis_b import dane_posadowienia

POD_GEO = "rozp. Ministra Transportu, Budownictwa i Gospodarki Morskiej z dnia 25 kwietnia 2012 r. w sprawie ustalania " \
          "geotechnicznych warunków posadawiania obiektów budowlanych (Dz.U. 2012 poz. 463)"


def ocena_warunkow(D, P) -> tuple[str, list[str]]:
    """Warunki gruntowe wg § 4 ust. 2 — reguła jawna na danych modelu: proste, gdy grunt jednorodny mineralny
    (bez gruntów organicznych, nasypów, gruntów słabonośnych) i zwierciadło wody poniżej poziomu posadowienia."""
    gr = (P["geo"].get("grunt") or {})
    rodz = str(gr.get("rodzaj", "")).lower()
    z0 = float(D.m.zero_abs)
    t_max_rel = D.w["wysokosc_zabudowy"]["t_max"] - z0
    spod_min = min((float(e["spod"]) for e in (D.m.fundamenty().get("elementy") or []) if "spod" in e), default=None)
    gl_max = t_max_rel - spod_min if spod_min is not None else None
    uw = [f"najgłębszy spód fundamentu {L(gl_max, 2)} m poniżej najwyższej rzędnej terenu przy budynku; zwierciadło wody "
          f"{L(P['zwg'], 2)} m p.p.t."]
    zle = any(k in rodz for k in ("organ", "nasyp", "namuł", "torf", "słabono"))
    proste = (not zle) and gl_max is not None and P["zwg"] is not None and P["zwg"] > gl_max
    return ("proste" if proste else "złożone — do ustalenia"), uw


def opinia(pab, D, d):
    P = dane_posadowienia(D)
    g, gr = P["geo"], (P["geo"].get("grunt") or {})
    war, uw = ocena_warunkow(D, P)
    dr = D.Wd["drenaz"]
    kat = g.get("kategoria", do_uzup("kategoria geotechniczna"))
    pab.zalacznik("Opinia geotechniczna (kategoria geotechniczna II)", podstawa="rozp. Dz.U. 2012 poz. 463 § 7 ust. 1, § 8")
    pab.wniosek(f"**{DANE_PRZYKLADOWE}** Opinia sporządzona dla przykładu na parametrach podłoża przyjętych w modelu "
                "(sekcja `geotechnika`); przed złożeniem wniosku zastępuje się ją opinią sporządzoną na podstawie badań "
                "podłoża przez osobę o odpowiednich kwalifikacjach.", alarm=True)
    pab.markdown(f"""
    # Dane ogólne

    * Obiekt: {d['obiekt']}; lokalizacja: {d['lokalizacja']} {DANE_PRZYKLADOWE}.
    * Zleceniodawca: {d['inwestor']['nazwa']}.
    * Autor opinii: {do_uzup('imię i nazwisko, kwalifikacje zawodowe (świadectwo/uprawnienia), podpis')}.
    * Data opracowania: {do_uzup('data opinii')}.

    # Podstawa i cel opracowania

    Podstawa: {POD_GEO} — § 7 ust. 1 (opinię opracowuje się dla obiektów wszystkich kategorii) i § 8 (opinia ustala
    przydatność gruntów na potrzeby budownictwa i wskazuje kategorię geotechniczną); PN-EN 1997-1 i PN-EN 1997-2 (dla
    dokumentacji badań podłoża i projektu geotechnicznego, § 9–10). Cel: ocena przydatności podłoża do bezpośredniego
    posadowienia budynku oraz ustalenie kategorii geotechnicznej obiektu.

    # Charakterystyka obiektu

    Budynek mieszkalny jednorodzinny, {D.w['kondygnacje_nadziemne']['wartosc']} kondygnacje nadziemne, bez podpiwniczenia;
    wymiary w obrysie {L(D.wymiary['dl'])} × {L(D.wymiary['szer'])} m; konstrukcja murowo-żelbetowa ze stropami monolitycznymi
    i wspornikami (schemat statycznie niewyznaczalny). Posadowienie projektowane: płyta fundamentowa żelbetowa na warstwie
    XPS z żebrami pod ścianami i pogrubieniami pod słupami; spód żeber obwodowych ok. {L(P['gl_obw'], 2)} m poniżej terenu
    (rozdz. 5 opisu).

    # Zakres rozpoznania podłoża

    Program badań dla kategorii II (propozycja): co najmniej {D.v('geotechnika', 'badania_punkty_min')} punkty badawcze
    (sondowania CPT/DPL, wiercenia) w obrysie budynku do głębokości ≥ {L(D.v('geotechnika', 'badania_glebokosc_pod_posadowieniem_min'), 1)}
    m poniżej poziomu posadowienia, badania laboratoryjne uziarnienia, oznaczenie współczynnika filtracji k_{{f}} w miejscu
    niecki chłonnej ({D.zr('geotechnika', 'badania_punkty_min')}; {ZAL}). Metryki wykonanych otworów i sondowań:
    {do_uzup('metryki otworów, protokoły sondowań, data badań')}.

    # Warunki gruntowo-wodne {DANE_PRZYKLADOWE}
    """)
    pab.tabela([
        {"Warstwa": "I", "Opis gruntu": "gleba (ziemia urodzajna) — do zdjęcia", "Miąższość / głębokość [m]": f"0,00–{L(g.get('humus'), 2)}",
         "Parametry": "—"},
        {"Warstwa": "II", "Opis gruntu": str(gr.get("rodzaj", "—")), "Miąższość / głębokość [m]": f"poniżej {L(g.get('humus'), 2)}",
         "Parametry": f"I_D = {L(gr.get('I_D'), 2)}; φ' = {L(gr.get('phi'), 0)}°; γ = {L(gr.get('gamma'), 1)} kN/m³; "
                      f"M₀ = {L((gr.get('M0') or 0) / 1000, 0)} MPa"},
    ], tytul="Profil geotechniczny (uogólniony)", klasa="zwarta", szerokosci=["16mm", None, "32mm", "62mm"],
        zrodlo="model/budynek.yaml: geotechnika " + DANE_PRZYKLADOWE)
    pab.markdown(f"""
    Zwierciadło wody gruntowej: {L(P['zwg'], 2)} m p.p.t., swobodne; oddziaływanie wody na elementy w gruncie:
    {dr.get('klasa_oddzialywania_wody', '—')}. Głębokość przemarzania h_{{z}} = {L(g.get('h_z'), 2)} m
    ({D.zr('geotechnika', 'h_z')}). Nie stwierdzono gruntów organicznych, nasypów niekontrolowanych ani niekorzystnych
    zjawisk geologicznych {DANE_PRZYKLADOWE}.

    # Ocena warunków gruntowych i kategoria geotechniczna

    Warunki gruntowe: **{war}** (§ 4 ust. 2 pkt 1 — warstwy jednorodne, zwierciadło wody poniżej projektowanego poziomu
    posadowienia; {'; '.join(uw)}). Obiekt posadawiany bezpośrednio, wymagający ilościowej i jakościowej oceny danych
    geotechnicznych — **kategoria geotechniczna {kat}** (§ 4 ust. 3 pkt 2 lit. a). Kategoria pierwsza (§ 4 ust. 3 pkt 1
    lit. a) nie ma zastosowania — obejmuje budynki 1- lub 2-kondygnacyjne o statycznie wyznaczalnym schemacie.

    # Przydatność gruntów do celów budowlanych

    Grunty warstwy II — przydatne do bezpośredniego posadowienia (grunty niespoiste, nośne, niewysadzinowe,
    przepuszczalne). Warstwa gleby — nieprzydatna; usunąć spod budynku i utwardzeń, wykorzystać do kształtowania zieleni.

    # Zalecenia

    1. W projekcie technicznym (PT-2 BO) opracować dokumentację badań podłoża gruntowego i projekt geotechniczny (§ 7
       ust. 2, § 9–10); dokumentacja geologiczno-inżynierska — nie jest wymagana (§ 7 ust. 3).
    2. Parametry geotechniczne w kategorii II wyznaczyć z badań polowych lub laboratoryjnych ({D.zr('geotechnika', 'gamma_R_v')}
       — podejście obliczeniowe DA2*); sprawdzić osiadania ({D.zr('geotechnika', 'osiadanie_max')}).
    3. Podsypkę pod XPS wykonać z piasku zagęszczonego warstwami; podłoże chronić przed rozluźnieniem i zawilgoceniem;
       odbiór dna wykopu z udziałem autora opinii / geotechnika {do_uzup('osoba odbierająca podłoże')}.
    4. Drenaż opaskowy — {str(dr.get('drenaz_opaskowy', '—')).lower()} (warunki wodne jw.); wody opadowe odprowadzać od budynku
       spadkami terenu i opaską żwirową.
    """)
