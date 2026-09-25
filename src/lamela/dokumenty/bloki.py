"""Treść bloków formalnych: oświadczenia (art. 34 ust. 3d pkt 3, art. 41 ust. 4a pkt 2, art. 33 ust. 2 pkt 10,
art. 102a ust. 1 PB), karty podpisów, informacja BIOZ (rozp. Dz.U. 2003 nr 120 poz. 1126 § 2, § 6).

Brzmienia przepisów przytoczono z tekstów aktów (API ELI Sejmu, stan 25.09.2026 — rejestr wymagań, R2):
* PB art. 34 ust. 3d pkt 3: „oświadczenie projektanta o sporządzeniu projektu zgodnie z obowiązującymi przepisami
  i zasadami wiedzy technicznej”; ust. 3e — imiona, nazwiska, numery uprawnień osób biorących udział w opracowaniu
  (art. 20 ust. 1 pkt 1a) i projektantów sprawdzających; ust. 3da — kopii nie dołącza się przy wpisie w e-CRUB;
* PB art. 41 ust. 4a pkt 2: PT „zgodnie z obowiązującymi przepisami, zasadami wiedzy technicznej, projektem
  zagospodarowania działki lub terenu oraz projektem architektoniczno-budowlanym oraz rozstrzygnięciami
  dotyczącymi zamierzenia budowlanego”;
* PB art. 33 ust. 2 pkt 10 + Prawo energetyczne art. 7b ust. 1, 3, 3c — oświadczenie o sieci ciepłowniczej
  z klauzulą „Jestem świadomy(-ma) odpowiedzialności karnej za złożenie fałszywego oświadczenia.”;
* PB art. 102a ust. 1, 2, 4 (Dz.U. 2026 poz. 1161) — brak urzędowego wzoru oświadczenia Inwestora (D-02).
"""
from __future__ import annotations

from markupsafe import Markup, escape

from .dane import ELEMENTY, Projektant, SPECJALNOSCI
from .formaty import data_slownie, liczba
from .znaczniki import do_uzup, DANE_PRZYKLADOWE, ZAL, NZW

PB = "ustawy z dnia 7 lipca 1994 r. – Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.)"
WT = ("rozporządzenie Ministra Infrastruktury z dnia 12 kwietnia 2002 r. w sprawie warunków technicznych, jakim powinny "
      "odpowiadać budynki i ich usytuowanie (t.j. Dz.U. 2022 poz. 1225 ze zm.)")


def _proj_dict(p: Projektant) -> dict:
    d = p.slownik()
    d["branza_nazwa"] = SPECJALNOSCI.get(p.branza, ("", "", p.branza))[2]
    return d


def karty_podpisow(osoby, data=None) -> list[dict]:
    out = []
    for o in osoby:
        if isinstance(o, dict):
            out.append(o)
            continue
        out.append(dict(rola=f"{o.funkcja} — {SPECJALNOSCI.get(o.branza, ('', '', o.branza))[2]}",
                        imie_nazwisko=o.imie_nazwisko,
                        opis=f"specjalność {o.specjalnosc_krotka}, nr uprawnień {o.nr_uprawnien}",
                        pole="data i podpis (postać papierowa)"))
    return out


def zawartosc_domyslna(dok) -> list[dict]:
    return [dict(kod=dok.kod, tytul=dok.tytul, biezacy=True)]


def _element_biernik(czesc: str) -> str:
    return ELEMENTY.get(czesc.split("-")[0], ("", "projekt", ""))[1]


def _zal(dok, tytul, zalacznik):
    """Jeżeli blok jest załącznikiem — rejestruje wpis „Załącznik nr N.” i zwraca (id, etykieta)."""
    if not zalacznik:
        return dok._nowe_id("osw"), None
    tyt = zalacznik if isinstance(zalacznik, str) else tytul
    id_, numer = dok._zalacznik_wpis(tyt)
    return id_, numer.rstrip(".")


# ------------------------------------------------------------------------------------ oświadczenie projektanta
def kontekst_oswiadczenia_projektanta(dok, *, projektant=None, osoby=None, techniczny=False, art102a=True,
                                      pnb=None, podpisuja=None) -> dict:
    osoby = list(osoby or dok.projektanci)
    el_b = _element_biernik(dok.czesc)
    zakres_pt = f" w zakresie: {dok.branza}" if dok.branza else ""
    if techniczny:
        tresc = Markup(
            f"Działając na podstawie art. 34 ust. 3d pkt 3 {PB}, <b>oświadczam, że projekt techniczny{escape(zakres_pt)}</b> "
            "dotyczący wyżej wymienionego zamierzenia budowlanego <b>został sporządzony zgodnie z obowiązującymi "
            "przepisami, zasadami wiedzy technicznej, projektem zagospodarowania działki lub terenu oraz projektem "
            "architektoniczno-budowlanym oraz rozstrzygnięciami dotyczącymi zamierzenia budowlanego</b> "
            f"(brzmienie zgodne z art. 41 ust. 4a pkt 2 PB), w tym z decyzją o pozwoleniu na budowę "
            f"{escape(pnb or do_uzup('nr i data decyzji o pozwoleniu na budowę, organ'))}.")
        podtytul = ("o sporządzeniu projektu technicznego zgodnie z obowiązującymi przepisami, zasadami wiedzy "
                    "technicznej, PZT, PAB i rozstrzygnięciami dotyczącymi zamierzenia budowlanego\n"
                    f"(art. 34 ust. 3d pkt 3 i art. 41 ust. 4a pkt 2 {PB})")
    else:
        tresc = Markup(
            f"Działając na podstawie art. 34 ust. 3d pkt 3 {PB}, <b>oświadczam, że {escape(el_b)}</b> dla wyżej "
            "wymienionego zamierzenia budowlanego <b>został sporządzony zgodnie z obowiązującymi przepisami "
            "oraz zasadami wiedzy technicznej</b>.")
        podtytul = (f"o sporządzeniu {ELEMENTY.get(dok.czesc, ('', '', 'projektu'))[2]} zgodnie z obowiązującymi przepisami "
                    f"oraz zasadami wiedzy technicznej\n(art. 34 ust. 3d pkt 3 {PB})")
    t102 = None
    if art102a:
        t102 = Markup(
            f"Przepisy techniczno-budowlane wydane na podstawie art. 7 ust. 2 pkt 1 PB — {escape(WT)} — zastosowano "
            f"w brzmieniu obowiązującym do dnia 19 września 2026 r., na podstawie art. 102a ust. "
            f"{'1 i 2' if techniczny else '1'} PB, w związku z oświadczeniem Inwestora z dnia "
            f"{escape(do_uzup('data złożenia oświadczenia z art. 102a PB'))}.")
    kopie = ("Kopii decyzji o nadaniu uprawnień budowlanych i zaświadczeń o przynależności do izby samorządu zawodowego "
             "(art. 34 ust. 3d pkt 1–2 PB) nie dołącza się dla uprawnień i osób wpisanych do centralnego rejestru osób "
             "posiadających uprawnienia budowlane (art. 34 ust. 3da PB) — "
             + do_uzup("potwierdzenie wpisu w e-CRUB albo dołączenie kopii") + ".")
    if dok.czesc in ("PZT", "PAB"):
        kopie += (" Przy tym samym autorze PZT i PAB kopie dołącza się tylko do jednego z projektów (§ 8 ust. 1 RPB), "
                  "a w oprawie wielotomowej — do pierwszego tomu (§ 8 ust. 2 RPB).")
    return dict(
        id=dok._nowe_id("osw"), miejscowosc=dok.miejscowosc, data=data_slownie(dok.data), podtytul=podtytul,
        element_nazwa=f"{dok.tytul} ({dok.kod})", tresc=tresc, art102a=t102,
        osoby=[dict(_proj_dict(p), specjalnosc=p.specjalnosc_skrot) for p in osoby],
        sprawdzajacy="nie dotyczy — projekt budynku mieszkalnego jednorodzinnego nie podlega sprawdzeniu "
                     "(art. 20 ust. 3 pkt 2 PB)",
        kopie=kopie, podpisy=karty_podpisow(podpisuja or ([projektant] if projektant else osoby), dok.data))


# ------------------------------------------------------------------------------------ sieć ciepłownicza
WARIANTY_SIECI = {
    "brak_sieci": "na terenie, na którym zlokalizowany jest projektowany obiekt, <b>nie istnieje sieć ciepłownicza</b> "
                  "i nie istnieją techniczne warunki dostarczania ciepła z systemu ciepłowniczego — obowiązek "
                  "przyłączenia obiektu do sieci ciepłowniczej, o którym mowa w art. 7b ust. 1 Prawa energetycznego, "
                  "nie występuje;",
    "zrodlo_indywidualne": "istnieją techniczne i ekonomiczne warunki przyłączenia obiektu do sieci ciepłowniczej, "
                           "jednak planowane jest dostarczanie ciepła z <b>indywidualnego źródła ciepła</b>, które "
                           "charakteryzuje się współczynnikiem nakładu nieodnawialnej energii pierwotnej nie wyższym "
                           "niż 0,8, a ciepło z niego wytworzone stanowi nie mniej niż 60 % ciepła z odnawialnych "
                           "źródeł energii (art. 7b ust. 3 Prawa energetycznego); spełnienie warunków stwierdzono "
                           "audytem z dnia " + do_uzup("data audytu, autor") + " (art. 7b ust. 3c);",
    "przylaczenie": "istnieją techniczne i ekonomiczne warunki przyłączenia obiektu do sieci ciepłowniczej "
                    "i dostarczania z niej ciepła — <b>obiekt zostanie przyłączony do sieci ciepłowniczej</b> "
                    "(art. 7b ust. 1 Prawa energetycznego).",
}


def kontekst_oswiadczenia_sieci(dok, *, projektant=None, wariant="brak_sieci", zrodlo_ciepla=None,
                                uzasadnienie=None, zalacznik=False) -> dict:
    if wariant not in WARIANTY_SIECI:
        raise ValueError(f"wariant: {', '.join(WARIANTY_SIECI)}")
    p = projektant or next((x for x in dok.dane.get("projektanci", []) if x.branza == "IS"), Projektant("IS"))
    id_, et = _zal(dok, "Oświadczenie projektanta dotyczące sieci ciepłowniczej (art. 33 ust. 2 pkt 10 PB)", zalacznik)
    return dict(
        id=id_, etykieta_zal=et, miejscowosc=dok.miejscowosc, data=data_slownie(dok.data), projektant=_proj_dict(p),
        warianty=[dict(tekst=Markup(t), wybrany=(k == wariant)) for k, t in WARIANTY_SIECI.items()],
        zrodlo_ciepla=zrodlo_ciepla or ("Projektowane źródło ciepła na potrzeby ogrzewania i przygotowania ciepłej wody "
                                        "użytkowej: pompa ciepła powietrze–woda z czynnikiem R290 (budynek zasilany "
                                        "wyłącznie energią elektryczną; gazociąg w drodze nie jest wykorzystywany)."),
        uzasadnienie=Markup(escape(uzasadnienie or (
            "Stan uzbrojenia terenu przyjęto wg briefu projektowego: w drodze 1KDD wodociąg, kanalizacja sanitarna, "
            "sieć nN 0,4 kV, światłowód i gazociąg; sieci ciepłowniczej brak " + DANE_PRZYKLADOWE + ". "
            + do_uzup("potwierdzenie braku sieci ciepłowniczej: mapa do celów projektowych lub informacja "
                      "przedsiębiorstwa ciepłowniczego") + "."))),
        podpis=karty_podpisow([p])[0])


# ------------------------------------------------------------------------------------ oświadczenie Inwestora 102a
def kontekst_oswiadczenia_102a(dok, *, organ=None, zakres=None, postepowanie=None) -> dict:
    powiat = dok.dane.get("dzialka", {}).get("powiat") or do_uzup("powiat")
    return dict(
        id=dok._nowe_id("osw"), miejscowosc=do_uzup("miejscowość"), data=do_uzup("data"),
        stan_prawny="25.09.2026 (Dz.U. do poz. 1244)",
        organ=organ or f"Starosta — organ administracji architektoniczno-budowlanej ({powiat})",
        zakres=zakres or "projektu zagospodarowania działki oraz projektu architektoniczno-budowlanego",
        postepowanie=postepowanie or "wniosku o pozwolenie na budowę (art. 102a ust. 1 pkt 1 PB)",
        podpis=dict(rola="Inwestor", imie_nazwisko=dok.dane["inwestor"]["nazwa"], opis=None,
                    pole="data i podpis Inwestora (każdego współinwestora)"))


# ------------------------------------------------------------------------------------ informacja BIOZ
BIOZ_DOMYSLNA = {
    1: """Zamierzenie obejmuje jeden obiekt — budynek mieszkalny jednorodzinny (3 kondygnacje nadziemne, bez podpiwniczenia,
garaż dwustanowiskowy w bryle) — oraz zagospodarowanie działki. Kolejność realizacji:

1. roboty przygotowawcze: geodezyjne wytyczenie obiektu, ogrodzenie placu budowy, zaplecze, tablica informacyjna, zdjęcie warstwy ziemi urodzajnej (ok. 0,4 m);
2. przyłącza wodociągowe, kanalizacyjne i elektroenergetyczne (wykopy wąskoprzestrzenne w pasie działki i drogi 1KDD);
3. stan zerowy: wykopy fundamentowe, fundamenty żelbetowe (wg PT-BO), izolacje przeciwwodne, uziom fundamentowy;
4. stan surowy: ściany murowane, stropy, wsporniki i płyty wysunięte żelbetowe monolityczne (deskowania i podparcia tymczasowe), rama boksu przeszklonego, attyki;
5. stropodachy, dach zielony garażu, instalacja fotowoltaiczna;
6. stolarka zewnętrzna (w tym przeszklenia wielkoformatowe), elewacje ETICS, lamele drewniane bryły II piętra (rusztowania);
7. instalacje wewnętrzne i roboty wykończeniowe;
8. zagospodarowanie terenu: zbiornik retencyjny wód opadowych, utwardzenia, ogrodzenie z bramą i furtką, zieleń.""",
    2: f"""Działka nr 123/4 jest niezabudowana — **brak istniejących obiektów budowlanych** na działce
{DANE_PRZYKLADOWE}. W pasie drogi gminnej 1KDD (ul. Lipowa) znajdują się sieci: wodociąg PE 110, kanalizacja
sanitarna PVC 200, sieć elektroenergetyczna nN 0,4 kV, światłowód i gazociąg. Na działkach sąsiednich (wschód, zachód)
— budynki mieszkalne jednorodzinne w odległości ≥ 8 m od granicy.""",
    3: f"""Elementy zagospodarowania mogące stwarzać zagrożenie bezpieczeństwa i zdrowia ludzi:

* uzbrojenie terenu w pasie drogowym — gazociąg i kable nN w rejonie wykopów pod przyłącza;
* ruch pojazdów na drodze gminnej 1KDD przy wjeździe na plac budowy;
* skarpy i wykopy otwarte (fundamenty, zbiornik retencyjny) oraz składowiska materiałów;
* drzewa istniejące przeznaczone do zachowania — ryzyko uszkodzenia systemu korzeniowego i gałęzi przez sprzęt {ZAL}.""",
    5: """Przed przystąpieniem do robót szczególnie niebezpiecznych (tabela zagrożeń) kierownik budowy lub osoba przez niego
wyznaczona przeprowadza **instruktaż stanowiskowy** pracowników, obejmujący: rodzaj i miejsce zagrożeń, kolejność
i technologię robót, stosowanie środków ochrony zbiorowej i indywidualnej, sposób postępowania w razie wypadku lub
awarii oraz drogi ewakuacji. Instruktaż powtarza się przy zmianie technologii, warunków lub składu brygady;
jego przeprowadzenie pracownicy potwierdzają podpisem. Treść instruktażu wynika z planu BIOZ.""",
    6: f"""Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom:

* ogrodzenie i oznakowanie placu budowy, wyznaczenie i wygrodzenie **stref niebezpiecznych** przy obiekcie, pod rusztowaniami i w zasięgu pracy żurawia {NZW};
* **ochrony zbiorowe na krawędziach** stropów, płyt wysuniętych, otworów w stropach i biegów schodowych (balustrady z poręczą i krawężnikiem), rusztowania systemowe z pomostami przy elewacjach, siatki ochronne; sprzęt chroniący przed upadkiem z wysokości tam, gdzie ochrony zbiorowe nie są możliwe;
* **zabezpieczenie wykopów**: skarpy o bezpiecznym nachyleniu albo obudowa ścian wykopów pionowych głębszych niż 1,5 m; zejścia do wykopów, odległość składowania urobku od krawędzi;
* nadzór nad pracą żurawia/HDS i pompy do betonu: sygnalista, strefa pod ładunkiem wyłączona z ruchu, zawiesia z ważnymi badaniami;
* lokalizacja sieci podziemnych przed robotami ziemnymi (przekopy kontrolne ręcznie w pobliżu gazociągu i kabli);
* deskowania i podparcia płyt wysuniętych wg projektu technologicznego; rozdeskowanie po osiągnięciu wytrzymałości;
* **komunikacja umożliwiająca szybką ewakuację**: utwardzona droga dojazdowa od ul. Lipowej, wolne od składowania przejścia, oznakowane drogi ewakuacyjne; gaśnice przy pracach z otwartym ogniem (papa termozgrzewalna), apteczka, telefony alarmowe na tablicy informacyjnej.""",
}

ZAGROZENIA_DOMYSLNE = [
    # (roboty, zagrożenie, miejsce, czas, § 6 rozp. BIOZ, występuje)
    ("Roboty na wysokości ponad 5,0 m: stropy i wsporniki nad I piętrem, dach II piętra i attyki, montaż lameli i PV",
     "upadek z wysokości, spadające przedmioty", "krawędzie stropów, dachy, rusztowania elewacyjne",
     "stan surowy, dachy, elewacje", "§ 6 pkt 1 lit. b", True),
    ("Wykopy: fundamenty, przyłącza, zbiornik retencyjny (wykop o ścianach pionowych bez rozparcia > 1,5 m)",
     "przysypanie ziemią, upadek do wykopu", "rejon fundamentów, trasy przyłączy, zbiornik",
     "roboty ziemne, stan zerowy, zagospodarowanie", "§ 6 pkt 1 lit. a", True),
    ("Roboty z użyciem żurawia / HDS (zbrojenie, deskowania, stolarka wielkoformatowa, elementy stalowe)",
     "uderzenie, przygniecenie ładunkiem, upadek ładunku", "strefa pracy żurawia i rozładunku",
     "stan surowy, montaż stolarki", "§ 6 pkt 1 lit. f", True),
    ("Roboty w pobliżu linii elektroenergetycznych napowietrznych", "porażenie prądem", "—", "—",
     "§ 6 pkt 1 lit. k", False),
    ("Roboty ziemne w pobliżu gazociągu i kabli nN w pasie drogowym (przyłącza)", "wybuch, pożar, porażenie",
     "pas drogi 1KDD, granica działki", "przyłącza", "— (poza katalogiem § 6)", True),
    ("Betonowanie wsporników i płyt wysuniętych na podparciach tymczasowych",
     "zawalenie deskowania, przygniecenie", "wsporniki P2, płyty wysunięte P0/P1", "stan surowy",
     "— (poza katalogiem § 6)", True),
]


def dodaj_informacje_bioz(dok, *, tresc=None, projektant=None, zagrozenia=None, jako_zalacznik=True):
    from .dokument import Dokument  # noqa: F401 (typ)
    t = dict(BIOZ_DOMYSLNA)
    t.update(tresc or {})
    p = projektant or next((x for x in dok.dane.get("projektanci", []) if x.branza == "AR"), Projektant("AR"))
    tytul = "Informacja dotycząca bezpieczeństwa i ochrony zdrowia (informacja BIOZ)"
    numer = None
    if jako_zalacznik:
        id_, numer = dok._zalacznik_wpis(tytul)
    else:
        id_ = dok._nowe_id("bioz")
        dok._wpis(id_, tytul, 1 + dok._przes)
    dok._bloki.append(("bioz_tytulowa", dict(id=id_, etykieta_zal=numer.rstrip(".") if numer else None,
                                             projektant=_proj_dict(p), data=data_slownie(dok.data),
                                             przyklad=dok.przyklad, podpis=karty_podpisow([p])[0])))
    dok.rozdzial("Zakres robót dla całego zamierzenia budowlanego oraz kolejność realizacji obiektów",
                 t[1], podstawa="§ 2 ust. 3 pkt 1")
    dok.rozdzial("Wykaz istniejących obiektów budowlanych", t[2], podstawa="§ 2 ust. 3 pkt 2")
    dok.rozdzial("Elementy zagospodarowania działki mogące stwarzać zagrożenie bezpieczeństwa i zdrowia ludzi",
                 t[3], podstawa="§ 2 ust. 3 pkt 3")
    dok.rozdzial("Przewidywane zagrożenia podczas realizacji robót budowlanych", podstawa="§ 2 ust. 3 pkt 4")
    if t.get(4):
        dok.markdown(t[4])
    z = zagrozenia or ZAGROZENIA_DOMYSLNE
    rows = [{"Rodzaj robót": r, "Zagrożenie": zg, "Miejsce": m, "Czas wystąpienia (etap)": c,
             "Rozp. BIOZ": Markup(f"<span class='mn'>{escape(par)}</span>"),
             "Występuje": Markup("<b class='nok'>tak</b>" if wyst else "<span class='nd'>nie</span>")}
            for r, zg, m, c, par, wyst in z]
    dok.tabela(rows, tytul="Skala i rodzaje zagrożeń, miejsce i czas ich wystąpienia", lp=True, klasa="zwarta",
               html_komorki=False, szerokosci=["7mm", None, "30mm", "31mm", "25mm", "19mm", "15mm"],
               wyrownanie={"Występuje": "c"},
               uwagi=["Katalog robót stwarzających szczególnie wysokie ryzyko — § 6 pkt 1 rozporządzenia BIOZ "
                      "(Dz.U. 2003 nr 120 poz. 1126); art. 21a ust. 2 PB."])
    wyst = [par for _, _, _, _, par, w in z if w and par.startswith("§")]
    if wyst:
        dok.wniosek("**Wniosek:** występują roboty wymienione w " + ", ".join(sorted(set(wyst)))
                    + " rozporządzenia BIOZ — **kierownik budowy sporządza plan BIOZ** przed rozpoczęciem budowy "
                      "(art. 21a ust. 1a pkt 1 i ust. 2 PB). Informacja BIOZ jest podstawą planu.", alarm=True)
    dok.rozdzial("Sposób prowadzenia instruktażu pracowników przed przystąpieniem do robót szczególnie niebezpiecznych",
                 t[5], podstawa="§ 2 ust. 3 pkt 5")
    dok.rozdzial("Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom, w tym komunikacja umożliwiająca "
                 "ewakuację", t[6], podstawa="§ 2 ust. 3 pkt 6")
    dok.blok_podpisow([p])
