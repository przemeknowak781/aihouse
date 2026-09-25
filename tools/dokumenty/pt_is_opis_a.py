"""PT-3 IS — część opisowa A: stan opracowania, podstawy, opis instalacji (§ 23 pkt 7 lit. a, d, e RPB),
powiązania z sieciami (§ 23 pkt 8 RPB). Wszystkie liczby z ``DanePTIS`` (model + obliczenia przy uruchomieniu)."""
from __future__ import annotations

from collections import Counter

from pt_is_dane import MODULY, L, DanePTIS, Opis

FIKCJA = "[DANE PRZYKŁADOWE – FIKCYJNE]"
NAZWY_MOD = {"woda": "Instalacja wodociągowa i c.w.u.", "kanalizacja": "Kanalizacja sanitarna",
             "deszczowa": "Wody opadowe i retencja", "drenaz": "Drenaż i odwodnienie powierzchniowe",
             "ogrzewanie": "Ogrzewanie (PC, podłogówka, bufor, naczynia, hałas)"}


def rozdz_stan(o: Opis, D: DanePTIS):
    """1. Stan opracowania — wynik sprawdzeń obliczeniowych i sprawy otwarte."""
    o.rozdzial("Stan opracowania i sprawy otwarte", podstawa="E.1 rejestru; W-272", nowa_strona=False)
    wiersze = []
    for k in MODULY:
        w = D.warunki(k)
        wiersze.append({"Obszar obliczeń": NAZWY_MOD[k], "Warunków": len(w),
                        "Spełnione": sum(1 for x in w if x.ok is True),
                        "Niespełnione": sum(1 for x in w if x.ok is False),
                        "Informacyjne": sum(1 for x in w if x.ok is None)})
    sp = D.went.sprawdzenia
    wiersze.append({"Obszar obliczeń": "Wentylacja mechaniczna (bilans, centrala, czerpnia/wyrzutnia)",
                    "Warunków": len(sp), "Spełnione": sum(1 for s in sp if s[2] is True),
                    "Niespełnione": sum(1 for s in sp if s[2] is False), "Informacyjne": sum(1 for s in sp if s[2] is None)})
    ep_ok = [D.ep.spelnia] + ([D.ep0.spelnia] if D.ep0 else [])
    wiersze.append({"Obszar obliczeń": "Charakterystyka energetyczna (EP ≤ EP_max; wariant z PV i bez PV)",
                    "Warunków": len(ep_ok), "Spełnione": sum(ep_ok), "Niespełnione": len(ep_ok) - sum(ep_ok),
                    "Informacyjne": 0})
    o.tekst(f"""
    Tom opracowano automatycznie z modelu budynku (`model/*.yaml`, stan z {D.t_modelu}) i bibliotek obliczeniowych
    `lamela.obliczenia` uruchamianych przy każdym generowaniu tomu — każda liczba w tomie pochodzi z modelu albo
    z obliczeń. Działka, MPZP, warunki gruntowo-wodne i warunki przyłączenia są {FIKCJA}; parametry urządzeń
    przyjęto z kart **wyrobów przykładowych** (oznaczenie {FIKCJA} lub [ZAŁ]) — dopuszcza się wyroby równoważne
    spełniające parametry wymagane podane w rozdziale „Zasadnicze urządzenia”.
    """)
    o.tabela(wiersze, tytul="Wynik sprawdzeń obliczeniowych PT-3 IS",
             uwagi="Warunki informacyjne — wartości podawane bez kryterium (np. moc ścian grzewczych uzupełniających).",
             zrodlo="lamela.obliczenia.sanitarne, lamela.obliczenia.energia — uruchomienie przy generowaniu tomu")
    if D.otwarte:
        o.tekst("**Sprawy otwarte** (do zamknięcia przed wydaniem tomu do realizacji; po uzupełnieniu modelu status "
                "aktualizuje się przy ponownym generowaniu):\n\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(D.otwarte, 1)))
    else:
        o.tekst("Brak spraw otwartych wykrytych przez kontrole spójności modelu i obliczeń.")
    if D.z_cache:
        o.wniosek("PODGLĄD — obliczenia odczytane z pamięci podręcznej; wersja nie do wydania.", alarm=True)


def rozdz_podstawy(o: Opis, D: DanePTIS, d: dict):
    """2. Przedmiot, zakres i podstawy opracowania."""
    chl = bool((D.B.get("energia") or {}).get("chlodzenie"))
    o.rozdzial("Przedmiot, zakres i podstawy opracowania", podstawa="§ 23 RPB", nowa_strona=True)
    o.tekst(f"""
    **Przedmiot.** Projekt techniczny instalacji sanitarnych budynku mieszkalnego jednorodzinnego
    „{d.get('nazwa_krotka', 'Dom LAMELA')}” — {d.get('lokalizacja') or d.get('adres', '')}: ogrzewanie wodne
    płaszczyznowe zasilane pompą ciepła powietrze–woda z automatyczną regulacją temperatury, wentylacja mechaniczna
    nawiewno-wywiewna z odzyskiem ciepła, instalacja wody zimnej i ciepłej, kanalizacja sanitarna, odprowadzenie
    i zagospodarowanie wód opadowych (retencja), odwodnienie powierzchniowe, charakterystyka energetyczna budynku.

    **Zakres wg RPB (rozporządzenie w sprawie szczegółowego zakresu i formy projektu budowlanego, Dz.U. 2020
    poz. 1609, t.j. Dz.U. 2022 poz. 1679 ze zm.):**

    * § 23 pkt 7 lit. a — instalacje ogrzewcze z urządzeniami automatycznie regulującymi temperaturę oddzielnie
      w poszczególnych pomieszczeniach; lit. d — wentylacja mechaniczna; lit. e — instalacje wodociągowe
      i kanalizacyjne (w tym wody opadowe);
    * § 23 pkt 7 lit. b i c (chłodzenie, klimatyzacja) — {'dotyczy (chłodzenie w modelu)' if chl else 'nie dotyczy: w modelu brak instalacji chłodzenia (`energia.chlodzenie`)'};
      lit. f (gaz) — nie dotyczy: budynek bez instalacji gazowej (źródło ciepła elektryczne — pompa ciepła);
      lit. g–i — tom PT-4 IE; lit. j (instalacje ochrony przeciwpożarowej) — nie dotyczy (dom jednorodzinny);
    * § 23 pkt 8 — powiązanie z sieciami zewnętrznymi i punkty pomiarowe, założenia (lit. a — parametry klimatu
      wewnętrznego), obliczenia i dobór urządzeń (lit. b — moce cieplne i elektryczne);
    * § 23 pkt 9 — zasadnicze urządzenia (pompa ciepła, zasobnik c.w.u., bufor, centrala wentylacyjna, zbiornik
      retencyjny); § 23 pkt 10 — dane ppoż. stosownie do zakresu; § 23 pkt 11 lit. a–d — charakterystyka energetyczna;
    * § 23 pkt 5, 6 i 12 — nie dotyczy (budynek mieszkalny, nie liniowy); § 23 pkt 4a — nie dotyczy (W-231);
    * § 24 pkt 3 i pkt 4 lit. a — rzuty i schematy instalacji (część rysunkowa).

    **Podstawy prawne i techniczne (rejestr wymagań `docs/10_podstawy_prawne/00_rejestr_wymagan.md`).**
    Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.); warunki techniczne (WT 2002; t.j. Dz.U. 2022 poz. 1225
    ze zm.) — stosowane na podstawie art. 102a PB; metodologia charakterystyki energetycznej (Dz.U. 2015 poz. 376
    ze zm., ost. 2023 poz. 697); rozporządzenia (UE) 2024/573 (F-gazy), 813/2013 (ekoprojekt PC), 1253/2014
    (centrale wentylacyjne); rozporządzenie w sprawie dopuszczalnych poziomów hałasu w środowisku (t.j. Dz.U. 2014
    poz. 112); Prawo wodne (t.j. Dz.U. 2025 poz. 960 ze zm.). Normy: PN-EN 12831:2006 (wycof., powołana w WT)
    i kontrolnie PN-EN 12831-1:2017-08; PN-B-03430:1983/Az3:2000 (wycof., wiąże przez WT); PN-B-01706:1992
    (wycof., powołana w WT) i kontrolnie PN-EN 806-1…-5; PN-EN 1717:2003 / PN-EN 1717+A1:2026-09;
    PN-EN 12056-1…-5:2002; PN-EN 12380:2005; PN-EN 13564-1:2004; PN-EN 752:2017-06; PN-EN 1610:2015-10;
    PN-EN 14825:2022-11; PN-EN 16147+A1:2023-06; PN-EN 13141-7+A1:2026-05; PN-EN 378-1+A1:2021-03;
    wytyczne operatora Aquanet S.A. (zał. C, 2024) z opadem PANDa 2050 i normami opadowymi IMGW 1991–2020.
    Metody obliczeniowe bibliotek powołujące normy spoza tabeli A.3 rejestru (np. PN-EN 1264 — ogrzewanie
    płaszczyznowe, PN-EN 12828 — naczynia, PN-EN 1253-2 — wpusty) oznaczono w obliczeniach [NZW] — status wydań
    do potwierdzenia przed wydaniem do realizacji.

    **Materiały wyjściowe:** PZT i PAB (tom I), PT-1 AR (przegrody, U), PT-2 BO (przejścia przez płytę i stropy),
    PT-4 IE (zasilanie urządzeń), model `model/budynek.yaml`, `dzialka.yaml`, `instalacje.yaml`,
    `wyposazenie.yaml`, dane klimatyczne Poznań (TMY, WMO 12330). Tom jest zgodny z PZT i PAB oraz rozstrzygnięciami
    dotyczącymi zamierzenia budowlanego (oświadczenie projektanta).
    """)
