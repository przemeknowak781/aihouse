"""ZL — element „Załączniki” tomu I (RPB § 5 ust. 1 pkt 4, § 7 ust. 1a): informacja BIOZ (rozp. MI z 23.06.2003,
Dz.U. 2003 nr 120 poz. 1126, § 2 ust. 2 i ust. 3 pkt 1–6; plan BIOZ — PB art. 21a), strona zastępcza zezwolenia
na lokalizację zjazdu (u.d.p. art. 29 ust. 1, 3a), oświadczenie projektanta IS o sieci ciepłowniczej (PB art. 33
ust. 2 pkt 10), wzór oświadczenia Inwestora z art. 102a ust. 1 PB. Treść BIOZ z modelu (bez liczb wpisanych ręcznie)."""
from __future__ import annotations

from lamela.dokumenty import DANE_PRZYKLADOWE, NZW, ZAL, do_uzup, liczba


def L(v, nd=2):
    return liczba(v, nd)


def bioz_tresc(z, d) -> tuple[dict, list]:
    b, dz = z.bud, z.dz
    dr = z.droga()
    kn = z.w("kondygnacje_nadziemne")
    geo = b.get("geotechnika") or {}
    fund = b.get("fundamenty") or {}
    spod = min((e.get("spod", 0.0) for e in fund.get("elementy") or []), default=0.0)
    wz = z.W["wysokosc_zabudowy"]
    tmax = float(wz["t_max"])
    gl_f = max(0.0, tmax - (z.zero + spod))                          # głębokość wykopu fundamentowego od terenu
    gl_k = float(z.inst["par_kan"].glebokosc_kanalu)                 # dno kanału sieciowego [ZAŁ — ParametryKan]
    H = float(wz["z_top_abs"]) - float(wz["t_min"])
    h5, zr5, _ = z.wym("procedura", "plan_BIOZ_wysokosc_robot")
    w15, zr15, _ = z.wym("procedura", "plan_BIOZ_wykop_pionowy")
    ret = dz.get("retencja") or {}
    zb = ret.get("zbiornik") or {}
    wsp = list(z.m.wsporniki())
    dachy = list(z.m.dachy())
    pv = (b.get("energia") or {}).get("pv") or {}
    lam = list(z.m.lamele()) if hasattr(z.m, "lamele") else []
    ist = (dz.get("uzbrojenie") or {}).get("istniejace") or []
    sas = [s for s in z.sasiedzi() if s["przylega"] and s["odl_granicy"] is not None]
    drz = [t for t in z.drzewa() if t.get("istn") and not t.get("do_wyciecia")]
    t = {}
    t[1] = f"""Zamierzenie obejmuje jeden obiekt budowlany — budynek mieszkalny jednorodzinny ({kn} kondygnacje nadziemne,
bez podpiwniczenia, garaż w bryle parteru) — wraz z zagospodarowaniem działki. Kolejność realizacji:

1. roboty przygotowawcze: geodezyjne wytyczenie obiektu, ogrodzenie placu budowy, zaplecze, tablica informacyjna, zdjęcie warstwy ziemi urodzajnej (ok. {L(geo.get('humus', 0), 1)} m);
2. przyłącza wodociągowe, kanalizacyjne, elektroenergetyczne i telekomunikacyjne — wykopy wąskoprzestrzenne na działce i w pasie drogi {dr['symbol']} (włączenie do kanału sanitarnego na głębokości ok. {L(gl_k, 1)} m p.p.t. {ZAL});
3. stan zerowy: wykop pod płytę fundamentową (głębokość ok. {L(gl_f, 1)} m od terenu), płyta fundamentowa żelbetowa na izolacji termicznej, izolacje przeciwwilgociowe, uziom (PT-2 BO, PT-4 IE);
4. stan surowy: ściany, stropy i {len(wsp)} płyt wysuniętych/wsporników żelbetowych monolitycznych (deskowania i podparcia tymczasowe), słupy i rama stalowa przeszklenia, attyki;
5. stropodachy ({len(dachy)} pola, w tym dach zielony garażu), instalacja fotowoltaiczna ({pv.get('moduly', '—')} modułów);
6. stolarka zewnętrzna (w tym przeszklenia wielkoformatowe), elewacje, osłony z lamel ({len(lam)} pól) — z rusztowań;
7. instalacje wewnętrzne i roboty wykończeniowe;
8. zagospodarowanie terenu: zbiornik retencyjny {L(zb.get('V', 0), 1)} m³, niecka chłonna, separator, utwardzenia, ogrodzenie z bramą i furtką, zieleń."""
    t[2] = (f"Działka nr ewid. {d['dzialka']['nr']} jest niezabudowana — **brak istniejących obiektów budowlanych** na działce "
            f"{DANE_PRZYKLADOWE}. W pasie drogi {dr['symbol']} znajdują się sieci: " + "; ".join(s["opis"] for s in ist) + ". "
            + " ".join(f"Działka {s['nr']}: {s['opis']} — {L(s['odl_granicy'], 1)} m od granicy." for s in sas))
    t[3] = f"""Elementy zagospodarowania mogące stwarzać zagrożenie bezpieczeństwa i zdrowia ludzi:

* uzbrojenie terenu w pasie drogowym {dr['symbol']} ({', '.join(s['opis'].split(' (')[0].split(' —')[0] for s in ist)}) w rejonie wykopów pod przyłącza;
* ruch pojazdów na drodze {dr['symbol']} przy wjeździe na plac budowy i przy robotach w pasie drogowym;
* wykopy otwarte (fundament, przyłącza, zbiornik retencyjny) oraz składowiska materiałów;
* drzewa istniejące zachowywane ({len(drz)} szt.) — ryzyko uszkodzenia systemu korzeniowego i koron przez sprzęt."""
    t[5] = None
    t[6] = None
    zag = [
        (f"Roboty na wysokości: stan surowy, dachy i attyki, montaż lameli i PV — wysokość budynku ok. {L(H, 1)} m nad terenem",
         "upadek z wysokości, spadające przedmioty", "krawędzie stropów i dachów, rusztowania elewacyjne",
         "stan surowy, dachy, elewacje", "§ 6 pkt 1 lit. b", H > h5),
        (f"Wykopy o ścianach pionowych bez rozparcia — włączenie przyłącza kanalizacyjnego (ok. {L(gl_k, 1)} m {ZAL}), "
         f"fundament (ok. {L(gl_f, 1)} m), zbiornik retencyjny {do_uzup('głębokość posadowienia zbiornika')}",
         "przysypanie ziemią, upadek do wykopu", "trasy przyłączy, pas drogowy, rejon fundamentów i zbiornika",
         "przyłącza, stan zerowy, zagospodarowanie", "§ 6 pkt 1 lit. a", max(gl_k, gl_f) > w15),
        (f"Roboty z użyciem żurawia / HDS i pompy do betonu {ZAL} (zbrojenie, deskowania, elementy stalowe, przeszklenia)",
         "uderzenie, przygniecenie ładunkiem, upadek ładunku", "strefa pracy żurawia i rozładunku",
         "stan surowy, montaż stolarki", "§ 6 pkt 1 lit. f", True),
        ("Roboty pod lub w pobliżu napowietrznych linii elektroenergetycznych", "porażenie prądem",
         "— (sieci w drodze wyłącznie podziemne)", "—", "§ 6 pkt 1 lit. k",
         any("napowietrz" in str(s.get("opis", "")) for s in ist)),
        ("Roboty ziemne w pobliżu czynnych sieci podziemnych i w pasie drogowym przy ruchu pojazdów",
         "uszkodzenie sieci (gaz, kable nN), potrącenie", f"pas drogi {dr['symbol']}, granica działki", "przyłącza",
         "— (poza katalogiem § 6)", True),
        ("Betonowanie płyt wysuniętych i wsporników na podparciach tymczasowych", "zawalenie deskowania, przygniecenie",
         "płyty wysunięte i wsporniki", "stan surowy", "— (poza katalogiem § 6)", bool(wsp)),
    ]
    return t, zag


TRESC_5 = """Przed przystąpieniem do robót szczególnie niebezpiecznych (tabela zagrożeń) kierownik budowy lub osoba przez
niego wyznaczona przeprowadza **instruktaż stanowiskowy** pracowników, obejmujący: rodzaj i miejsce zagrożeń,
kolejność i technologię robót, stosowanie środków ochrony zbiorowej i indywidualnej, sposób postępowania w razie
wypadku lub awarii oraz drogi ewakuacji. Instruktaż powtarza się przy zmianie technologii, warunków lub składu
brygady; pracownicy potwierdzają go podpisem. Zakres instruktażu określa plan BIOZ."""


def tresc_6(z) -> str:
    dr = z.droga()
    return f"""Środki techniczne i organizacyjne zapobiegające niebezpieczeństwom:

* ogrodzenie i oznakowanie placu budowy; wyznaczenie i wygrodzenie **stref niebezpiecznych** przy obiekcie, pod rusztowaniami i w zasięgu pracy żurawia {NZW};
* **ochrony zbiorowe na krawędziach** stropów, płyt wysuniętych, otworów i biegów schodowych (balustrady z poręczą i krawężnikiem), rusztowania systemowe z pomostami, siatki ochronne; sprzęt chroniący przed upadkiem z wysokości tam, gdzie ochrony zbiorowe nie są możliwe;
* **zabezpieczenie wykopów**: skarpy o bezpiecznym nachyleniu albo obudowa ścian wykopów pionowych; zejścia do wykopów; składowanie urobku poza klinem odłamu;
* lokalizacja sieci podziemnych przed robotami ziemnymi, przekopy kontrolne ręcznie w pobliżu gazociągu i kabli; roboty w pasie drogowym wg zezwolenia zarządcy drogi i zatwierdzonej organizacji ruchu (u.d.p. art. 29 ust. 3 pkt 1 lit. b);
* nadzór nad pracą żurawia/HDS i pompy do betonu (sygnalista, strefa pod ładunkiem wyłączona z ruchu, zawiesia z ważnymi badaniami); deskowania i podparcia płyt wysuniętych wg projektu technologicznego, rozdeskowanie po osiągnięciu wymaganej wytrzymałości;
* **komunikacja umożliwiająca szybką ewakuację**: utwardzona droga dojazdowa od drogi {dr['symbol']}, wolne od składowania przejścia, oznakowane drogi ewakuacyjne; gaśnice przy pracach z otwartym ogniem, apteczka, telefony alarmowe na tablicy informacyjnej."""


def buduj_zl(zp, z, d):
    t, zag = bioz_tresc(z, d)
    t[5], t[6] = TRESC_5, tresc_6(z)
    zp.blok("Informacja BIOZ — strona tytułowa (§ 2 ust. 2) i część opisowa pkt 1–6 (§ 2 ust. 3); wniosek: plan BIOZ "
            "(PB art. 21a)", "informacja_bioz", t, zagrozenia=zag)
    for k in range(1, 7):
        zp._dodaj(f"**§ 2 ust. 3 pkt {k}.**", "", t[k] if t.get(k) else "(tabela zagrożeń — PDF)", "")
    dr = z.droga()
    zp.blok("Strona zastępcza — zezwolenie zarządcy drogi na lokalizację zjazdu", "dokument_zewnetrzny",
            f"Decyzja zarządcy drogi o lokalizacji zjazdu z drogi gminnej {dr['symbol']}",
            organ=f"Wójt (burmistrz) Gminy {d['dzialka']['gmina']} — zarządca drogi gminnej (u.d.p. art. 19 ust. 2 pkt 4)",
            podstawa="art. 29 ust. 1 i 3a ustawy o drogach publicznych (t.j. Dz.U. 2025 poz. 889 ze zm.); PB art. 33 ust. 2 pkt 1",
            uwagi="Zezwolenie określa miejsce lokalizacji i parametry techniczne zjazdu (u.d.p. art. 29 ust. 3); decyzja wygasa, "
                  "jeżeli w ciągu 3 lat od jej wydania zjazd nie został wybudowany (art. 29 ust. 5).")
    zp.blok("Oświadczenie projektanta instalacji sanitarnych o możliwości przyłączenia do sieci ciepłowniczej",
            "oswiadczenie_sieci_cieplowniczej",
            zalacznik="Oświadczenie projektanta dotyczące sieci ciepłowniczej (art. 33 ust. 2 pkt 10 PB)",
            uzasadnienie=("Stan uzbrojenia terenu wg modelu (dzialka.yaml): w drodze " + dr["symbol"] + " — "
                          + "; ".join(s["opis"] for s in (z.dz.get("uzbrojenie") or {}).get("istniejace") or [])
                          + "; sieci ciepłowniczej brak " + DANE_PRZYKLADOWE + ". "
                          + do_uzup("potwierdzenie braku sieci ciepłowniczej: mapa do celów projektowych lub informacja "
                                    "przedsiębiorstwa energetycznego") + "."))
    zp.zalacznik("Oświadczenie Inwestora o stosowaniu przepisów techniczno-budowlanych w brzmieniu obowiązującym do "
                 "19.09.2026 r. (art. 102a ust. 1 PB) — wzór", nowa_strona=True)
    zp.blok("Wzór oświadczenia Inwestora (art. 102a ust. 1, 2, 4 PB; Dz.U. 2026 poz. 1161)", "oswiadczenie_inwestora_102a",
            w_spisie=False)
