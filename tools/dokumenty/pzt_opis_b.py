"""PZT — część opisowa, RPB § 14 pkt 4–5 (zestawienie powierzchni i wskaźników MPZP; ograniczenia, zabytki, szkody
górnicze, zagrożenia dla środowiska). Wartości: ``lamela.wskazniki``, audyt A1, ``lamela.obliczenia``, wymagania.yaml."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, ZAL, do_uzup, liczba

from redakcja import czysc

LOKALE_MIESZKALNE = 1   # program użytkowy (brief § 4; PAB § 20 ust. 1 pkt 6) — budynek z jednym lokalem mieszkalnym


def L(v, nd=2):
    return liczba(v, nd)


def _pr(v):
    return 100.0 * v


# ------------------------------------------------------------------------------------------------ § 14 pkt 4
def pkt4(zp, z, d):
    A = z.w("pow_dzialki")
    W = z.W
    zp.rozdzial("Zestawienie powierzchni i wskaźników zagospodarowania", f"""
    Powierzchnie obliczono z geometrii modelu (`lamela.wskazniki`) wg definicji ustawy o planowaniu i zagospodarowaniu
    przestrzennym (upzp, t.j. Dz.U. 2026 poz. 538) art. 2 pkt 28–35 oraz § 14 pkt 4 RPB; powierzchnię zabudowy budynku
    pomniejsza się o powierzchnię części zewnętrznych budynku, takich jak: tarasy naziemne i podparte słupami, gzymsy
    oraz balkony (§ 14 pkt 4 lit. a RPB). Powierzchnie w m² z dokładnością do 0,01 m².
    """, podstawa="§ 14 pkt 4 RPB")
    utw = W["pow_utwardzona"].get("elementy") or {}
    nazwy = {u["id"]: u.get("nawierzchnia", "").split("—")[0].strip() for u in z.dz.get("utwardzenia") or []}
    rows = [
        "a) powierzchnia zabudowy",
        {"Pozycja": "budynek projektowany — rzut ścian zewnętrznych wszystkich kondygnacji nadziemnych",
         "Powierzchnia [m²]": z.w("pow_zabudowy"), "Udział [%]": _pr(z.w("udzial_zabudowy"))},
        {"Pozycja": "obiekty istniejące", "Powierzchnia [m²]": 0.0, "Udział [%]": 0.0},
        {"Pozycja": "informacyjnie: wariant kontrolny z rzutem płyt wysuniętych i okapów",
         "Powierzchnia [m²]": z.w("pow_zabudowy_kontrolna"), "Udział [%]": _pr(z.w("udzial_zabudowy_kontrolny"))},
        "b) drogi, parkingi, place i chodniki",
    ] + [{"Pozycja": f"{k} — {nazwy.get(k, '')}", "Powierzchnia [m²]": v, "Udział [%]": _pr(v / A)} for k, v in utw.items()] + [
        {"_klasa": "pod", "Pozycja": "razem lit. b", "Powierzchnia [m²]": z.w("pow_utwardzona"), "Udział [%]": _pr(z.w("pow_utwardzona") / A)},
        "c) powierzchnia biologicznie czynna",
        {"Pozycja": "teren biologicznie czynny (upzp art. 2 pkt 28)", "Powierzchnia [m²]": z.w("pbc"), "Udział [%]": _pr(z.w("udzial_pbc"))},
        {"Pozycja": "informacyjnie: 50 % dachu zielonego (rezerwa — nie wliczana)", "Powierzchnia [m²]": z.w("pbc_rezerwa_dach"),
         "Udział [%]": _pr(z.w("pbc_rezerwa_dach") / A)},
        "d) inne części terenu (zgodność z MPZP)",
        {"Pozycja": "tarasy i podesty naziemne", "Powierzchnia [m²]": z.w("pow_tarasow"), "Udział [%]": _pr(z.w("pow_tarasow") / A)},
        {"Pozycja": "opaska żwirowa przy budynku", "Powierzchnia [m²]": z.w("pow_opaski"), "Udział [%]": _pr(z.w("pow_opaski") / A)},
    ]
    pk = W["pow_kondygnacji"]["wartosc"]
    rows += [{"Pozycja": f"powierzchnia kondygnacji {k} (upzp art. 2 pkt 33)", "Powierzchnia [m²]": v, "Udział [%]": None}
             for k, v in pk.items()]
    rows += [{"_klasa": "pod", "Pozycja": "suma powierzchni kondygnacji nadziemnych (art. 2 pkt 32)",
              "Powierzchnia [m²]": z.w("suma_pow_kondygnacji_nadziemnych"), "Udział [%]": None}]
    zp.tabela(rows, tytul=f"Zestawienie powierzchni — działka nr ewid. {d['dzialka']['nr']} ({L(A)} m²)",
              formaty={"Powierzchnia [m²]": 2, "Udział [%]": 2}, szerokosci=[None, "30mm", "22mm"],
              uwagi=["Powierzchnia zabudowy: " + czysc(W["pow_zabudowy"]["metoda"]) + ".",
                     "Powierzchnia biologicznie czynna: " + czysc(W["pbc"]["metoda"]) + "."],
              zrodlo="lamela.wskazniki (model/budynek.yaml + model/dzialka.yaml)")
    # bilans terenu (rzut parteru, nie powierzchnia zabudowy — wspornik wyższej kondygnacji nad terenem)
    p0 = float(z.p0.area)
    poz = [("rzut parteru (teren pod budynkiem)", p0), ("tarasy i podesty naziemne", z.w("pow_tarasow")),
           ("utwardzenia (lit. b)", z.w("pow_utwardzona")), ("opaska żwirowa", z.w("pow_opaski")),
           ("teren biologicznie czynny (lit. c)", z.w("pbc"))]
    reszta = A - sum(v for _, v in poz)
    poz.append(("pozostałe (teren nad zbiornikiem retencyjnym, styki warstw)", reszta))
    zp.tabela([{"Pokrycie terenu": k, "Powierzchnia [m²]": v, "Udział [%]": _pr(v / A)} for k, v in poz],
              tytul="Bilans pokrycia terenu działki", suma=True, etykieta_sumy="Powierzchnia działki",
              formaty={"Powierzchnia [m²]": 2, "Udział [%]": 2}, szerokosci=[None, "30mm", "22mm"],
              uwagi=["Rzut parteru jest mniejszy od powierzchni zabudowy o rzut wysuniętych części wyższych kondygnacji "
                     "(wspornik) nad terenem."])
    pkt4_mpzp(zp, z, d)


def pkt4_mpzp(zp, z, d):
    u_zab, zr_zab, i_zab = z.wym("mpzp", "udzial_pow_zabudowy_max")
    u_pbc, zr_pbc, i_pbc = z.wym("mpzp", "udzial_PBC_min")
    ints, zr_int, i_int = z.wym("mpzp", "intensywnosc_zakres")
    hmax, zr_h, i_h = z.wym("mpzp", "wys_zabudowy_max")
    hrez, zr_hr, _ = z.wym("mpzp", "wys_zabudowy_rezerwa")
    kmax, zr_k, i_k = z.wym("mpzp", "kondygnacje_nadziemne_max")
    dmax, zr_d, i_d = z.wym("mpzp", "dach_plaski_spadek_max")
    mp, zr_mp, i_mp = z.wym("mpzp", "miejsca_postojowe_na_lokal_min")
    ogr, zr_og, i_og = z.wym("mpzp", "ogrodzenie_od_drogi_wys_max")
    lz, zr_lz, i_lz = z.wym("usytuowanie", "linia_zabudowy_od_linii_rozgraniczajacej")
    W = z.W
    H = z.w("wysokosc_zabudowy")
    ne = W["miejsca_postojowe"]
    og = max((o["wys"] for o in z.ogrodzenie_od_drogi() if o["od_drogi"]), default=0.0)
    import re
    lz_a = next((w.wartosc for w in z.wyniki_audytu("MPZP") if w.element == "linia zabudowy"), "")
    lz_el = (re.search(r"\(([^)]+)\)", lz_a) or [None, "—"])[1]
    lz_w = (f"linia nieprzekroczona — rezerwa {L(z.lz_rezerwa)} m (element najbliższy linii: {lz_el})"
            if z.lz_rezerwa >= 0 else f"PRZEKROCZENIE linii o {L(-z.lz_rezerwa)} m ({lz_el})")
    zp.tabela_wynikow([
        dict(parametr="Udział powierzchni zabudowy", wartosc=_pr(z.w("udzial_zabudowy")), jedn="%",
             wymaganie=f"≤ {L(_pr(u_zab), 0)} %", podstawa=f"{zr_zab} [{i_zab}]", spelnia=z.w("udzial_zabudowy") <= u_zab),
        dict(parametr="Udział powierzchni biologicznie czynnej (bez rezerwy dachu zielonego)", wartosc=_pr(z.w("udzial_pbc")), jedn="%",
             wymaganie=f"≥ {L(_pr(u_pbc), 0)} %", podstawa=f"{zr_pbc} [{i_pbc}]", spelnia=z.w("udzial_pbc") >= u_pbc),
        dict(parametr="Intensywność zabudowy (nadziemna)", wartosc=L(z.w("intensywnosc_nadziemna"), 3),
             wymaganie=f"{L(ints[0])}–{L(ints[1])}", podstawa=f"{zr_int} [{i_int}]",
             spelnia=ints[0] <= z.w("intensywnosc_nadziemna") <= ints[1]),
        dict(parametr=f"Wysokość zabudowy ({W['wysokosc_zabudowy'].get('element', '—')})", wartosc=H, jedn="m",
             wymaganie=f"≤ {L(hmax)} m (rezerwa proj. {L(hrez)} m)", podstawa=f"{zr_h} [{i_h}]", spelnia=H <= hmax),
        dict(parametr="Liczba kondygnacji nadziemnych", wartosc=str(z.w("kondygnacje_nadziemne")), wymaganie=f"≤ {kmax}",
             podstawa=f"{zr_k} [{i_k}]", spelnia=z.w("kondygnacje_nadziemne") <= kmax),
        dict(parametr="Spadek dachów (dachy płaskie)", wartosc=z.w("kat_dachu"), jedn="°", wymaganie=f"≤ {dmax}°",
             podstawa=f"{zr_d} [{i_d}]", spelnia=z.w("kat_dachu") <= dmax),
        dict(parametr=f"Miejsca postojowe (garaż {ne.get('garaz')} + naziemne {ne.get('zewn')})", wartosc=str(ne["wartosc"]),
             jedn="szt.", wymaganie=f"≥ {mp} na lokal mieszkalny", podstawa=f"{zr_mp} [{i_mp}]",
             spelnia=ne["wartosc"] >= mp * LOKALE_MIESZKALNE),
        dict(parametr="Nieprzekraczalna linia zabudowy — element najbliższy linii", wartosc=lz_w,
             wymaganie=f"{L(lz)} m od linii rozgraniczającej; brak przekroczeń", podstawa=f"{zr_lz} [{i_lz}]",
             spelnia=z.lz_rezerwa >= 0),
        dict(parametr="Wysokość ogrodzenia od drogi (ażurowe)", wartosc=og, jedn="m", wymaganie=f"≤ {L(ogr)} m",
             podstawa=f"{zr_og} [{i_og}]", spelnia=og <= ogr),
    ], tytul=f"Zgodność z ustaleniami MPZP — {(z.dz.get('dzialka') or {}).get('mpzp', '—')}",
        uwagi=[f"Ustalenia MPZP przykładowe {DANE_PRZYKLADOWE}; wartości wymagań z `docs/10_podstawy_prawne/wymagania.yaml`. "
               f"Wysokość zabudowy wg upzp art. 2 pkt 30 lit. a: H = z_top − t_śr = {L(W['wysokosc_zabudowy']['z_top_abs'])} − "
               f"{L(W['wysokosc_zabudowy']['t_sr'])} m n.p.m. ({czysc(W['wysokosc_zabudowy']['metoda'])})."])
