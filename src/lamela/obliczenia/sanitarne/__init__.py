"""Obliczenia instalacji sanitarnych „Dom LAMELA” — woda i c.w.u., kanalizacja, wody opadowe, drenaż, ogrzewanie (PC).

Moduły (każdy: funkcja obliczeniowa → dataclass wyniku z ``warunki`` (W-xxx), ``kroki`` (wzór → podstawienie → wynik),
``do_dict()`` i ``raport()`` / ``raport_md()`` — raport markdown z tabelami, wzorami i podstawieniami):

* ``przybory``     — KATALOG przyborów (q_n PN-B-01706, LU PN-EN 806-3, DU PN-EN 12056-2), ``przybory_z_modelu``, ``grupy_pionow``;
* ``woda``         — ``oblicz_wode(dane, ParametryWoda)``: zapotrzebowanie, q = 0,682·Σq_n^0,45 − 0,14, średnice, straty,
                     p_wym, wodomierz, PN-EN 1717, zasobnik c.w.u., cyrkulacja (reguła 3 l), dezynfekcja, izolacje (WT zał. 2);
* ``kanalizacja``  — ``oblicz_kanalizacje(dane, ParametryKan)``: PN-EN 12056-2 system I, podejścia, piony, przewody pod
                     posadzką (Colebrook–White, h/d), przykanalik, studzienka, wentylacja pionów (WT §125), cofka (§124);
* ``deszczowa``    — ``oblicz_deszczowa(dane, ParametryDeszcz)``: pola dachów, wpusty, przelewy awaryjne, rury spustowe,
                     dach zielony, odwodnienia liniowe, zbiornik ≤ 5 m³ + niecka (Aquanet/PANDa), bilans roczny, skrzynki;
* ``drenaz``       — ``ocen_drenaz(dane, ParametryDrenaz)``: decyzja o drenażu opaskowym, spadki terenu, cokół;
* ``ogrzewanie``   — ``oblicz_ogrzewanie(dane, phi_hl, ParametryOgrz, cwu)``: PC R290 (punkt biwalentny, bilans TMY),
                     podłogówka PN-EN 1264, rozdzielacze, bufor, naczynia c.o./c.w.u., hałas PC;
* ``schemat_pc``   — ``rysuj_schemat_pc(og, woda, plik.png)``.

Dane wejściowe: ``lamela.obliczenia.inst_wspolne.dane_z_modelu(budynek, dzialka, wyposazenie, instalacje)``.
Komplet obliczeń + raporty: ``python -m lamela.obliczenia.instalacje`` (patrz ``lamela.obliczenia.instalacje``).
"""
