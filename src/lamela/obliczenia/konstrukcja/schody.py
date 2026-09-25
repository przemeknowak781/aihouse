"""Schody żelbetowe płytowe: bieg (płyta pochyła ze stopniami) + spocznik jako pasmo płyty jednokierunkowej
(PN-EN 1992-1-1; obciążenia PN-EN 1991-1-1: schody kat. A q_k = 4,0 kN/m², Q_k = 4,0 kN — R5 3.3).

Schemat: belka swobodnie podparta (lub ciągła) w rzucie poziomym — odcinki „bieg” i „spocznik” z różnymi obciążeniami;
ciężar płyty biegu γ·h/cos α, stopni γ·h_s/2, wykończenia na stopnicach i podstopnicach g_w·(1 + h_s/s), tynku g_t/cos α
(na 1 m² rzutu). Momenty w rzucie poziomym są równe momentom w płycie pochyłej (obciążenia pionowe).
Zbrojenie: główne dołem wzdłuż biegu, rozdzielcze ≥ 20 % (9.3.1.1(2)); w załamaniu bieg–spocznik pręty krzyżowane
z zakotwieniem l_bd (uwaga konstrukcyjna). Ugięcie: l/d (7.4.2, K = 1,0) i obliczeniowe (7.4.3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .materialy import Beton, StalZbrojeniowa
from .obciazenia import ZestawienieStale, krok_obliczeniowe, obciazenie_uzytkowe
from .statyka import Belka, ObcQ, Podpora, obwiednia_ULS, kombinacja_SLS
from .wspolne import Parametry, Wynik, f
from . import zelbet


@dataclass
class OdcinekSchodow:
    x0: float
    x1: float
    typ: str            # bieg | spocznik


@dataclass
class Schody(Wynik):
    L: float = 0.0
    h: float = 0.0
    alfa: float = 0.0
    g_bieg: float = 0.0
    g_spocz: float = 0.0
    M_Ed: float = 0.0
    V_Ed: float = 0.0
    R_G: tuple = ()
    R_Q: tuple = ()
    zbrojenie: str = ""
    prety: list = field(default_factory=list)
    belka: object = None
    obwiednia: object = None
    zest_bieg: object = None
    zest_spocz: object = None


def plyta_schodowa(nazwa: str, odcinki: list[OdcinekSchodow], h: float, h_st: float, s_st: float, szer: float,
                   beton: Beton, p: Parametry | None = None, g_wykoncz: float = 1.0, g_tynk: float = 0.20,
                   podpory: tuple = ("przegub", "przegub"), stal: StalZbrojeniowa | None = None,
                   ekspozycja: str = "XC1") -> Schody:
    """Płyta schodowa. odcinki — w rzucie poziomym od podpory dolnej (x = 0) do górnej (x = L); h — grubość płyty [m]
    (prostopadle do biegu); h_st, s_st — wysokość i głębokość stopnia [m]; szer — szerokość biegu [m];
    g_wykoncz — wykończenie stopnic/spocznika [kN/m²]; g_tynk — tynk od spodu [kN/m²]."""
    p = p or Parametry()
    stal = stal or StalZbrojeniowa()
    w = Schody(nazwa=nazwa)
    L = odcinki[-1].x1
    alfa = math.atan2(h_st, s_st)
    w.krok("Geometria biegu", "tg α = h_s/s", f"{f(h_st * 100, 1)}/{f(s_st * 100, 1)}", f"α = {f(math.degrees(alfa), 1)}°")
    w.krok("Rozpiętość w rzucie (osie podpór)", "L", "", L, "m", nd=3)
    g = p.ciezar_zelbetu
    zb = ZestawienieStale("Bieg — na 1 m² rzutu poziomego")
    zb.dodaj_wartosc("Płyta żelbetowa γ·h/cos α", g * h / math.cos(alfa), f"25·{f(h, 3)}/cos {f(math.degrees(alfa), 1)}°")
    zb.dodaj_wartosc("Stopnie betonowe γ·h_s/2", g * h_st / 2, f"25·{f(h_st, 3)}/2")
    zb.dodaj_wartosc("Wykończenie stopnic i podstopnic g_w·(1 + h_s/s)", g_wykoncz * (1 + h_st / s_st),
                     f"{f(g_wykoncz, 2)}·(1 + {f(h_st, 3)}/{f(s_st, 3)})")
    zb.dodaj_wartosc("Tynk od spodu g_t/cos α", g_tynk / math.cos(alfa), f"{f(g_tynk, 2)}/cos α")
    zs = ZestawienieStale("Spocznik — na 1 m²")
    zs.dodaj_wartosc("Płyta żelbetowa γ·h", g * h, f"25·{f(h, 3)}")
    zs.dodaj_wartosc("Wykończenie", g_wykoncz, "")
    zs.dodaj_wartosc("Tynk od spodu", g_tynk, "")
    uz = obciazenie_uzytkowe("schody", p)
    w.zest_bieg, w.zest_spocz = zb, zs
    w.krok("Obciążenie stałe biegu (rzut)", "g_k,b", "", zb.g_k, "kN/m²", nd=3)
    w.krok("Obciążenie stałe spocznika", "g_k,s", "", zs.g_k, "kN/m²", nd=3)
    w.krok("Obciążenie użytkowe schodów (kat. A)", "q_k", "", uz.q_k, "kN/m²", nd=2, zrodlo=uz.zrodlo)
    krok_obliczeniowe(w, zb.g_k, uz.q_k, uz.psi[0], p, "q_b")
    krok_obliczeniowe(w, zs.g_k, uz.q_k, uz.psi[0], p, "q_s")
    pods = [Podpora(0.0, podpory[0], nazwa="A"), Podpora(L, podpory[1], nazwa="B")]
    bel = Belka(L, pods, EI=1.0, dx=0.02)
    G = [ObcQ(zb.g_k if o.typ == "bieg" else zs.g_k, o.x0, o.x1) for o in odcinki]
    Q = [ObcQ(uz.q_k, 0.0, L)]
    ob, baz = obwiednia_ULS(bel, G, [Q], p, psi0=uz.psi[0])
    w.obwiednia, w.belka = ob, bel
    MEd, VEd = ob.M_przeslo, ob.V_Ed
    w.krok("Moment przęsłowy (obwiednia 6.10a/b, na 1 m szerokości)", "M_Ed", "", MEd, "kNm/m")
    w.krok("Siła poprzeczna przy podporze", "V_Ed", "", VEd, "kN/m")
    w.R_G = tuple(baz["G"].R)
    w.R_Q = tuple(baz["Q"][0].R)
    c = zelbet.otulina(ekspozycja, 12, p).c_nom
    d = h - c / 1000 - 0.006
    zg = zelbet.zginanie_prostokat(MEd, 1.0, h, d, beton, stal, nazwa="Zginanie płyty biegu (na 1 m)", element="plyta")
    w.dolacz(zg, "Wymiarowanie na zginanie")
    smax = zelbet.smax_plyta(h, True, True)
    fi, s, As = zelbet.dobierz_plyta(zg.As_req, smax, 10, 16, As_min=zg.As_min)
    w.krok("Przyjęto zbrojenie główne dołem", f"φ{fi} co {f(s / 10, 0)} cm", "", As / 100, "cm²/m", nd=2)
    w.warunek("Zbrojenie główne", max(zg.As_req, zg.As_min), As, "mm²/m", "(9.1N)", nd=0, symbol_E="A_s,req", symbol_R="A_s,prov")
    sc = zelbet.scinanie_bez_zbrojenia(VEd, 1.0, d, As, beton, nazwa="Ścinanie płyty biegu")
    w.dolacz(sc, "Ścinanie")
    ld = zelbet.ugiecie_ld(L, d, zg.As_req, As, 1.0, beton, K=1.0, stal=stal)
    w.dolacz(ld, "Ugięcie (l/d)")
    qp = kombinacja_SLS(baz, uz.psi[2])
    Mqp = float(qp.M.max())
    wel = qp.w_max()
    ug = zelbet.ugiecie_obliczeniowe(Mqp, wel, L, 1.0, h, d, As, beton, p, k_skurcz=0.125)
    w.dolacz(ug, "Ugięcie obliczeniowe")
    ry = zelbet.rysy_bez_obliczen(Mqp, 1.0, h, d, As, fi, s, beton, p.w_max.get(ekspozycja, 0.4))
    w.dolacz(ry, "Rysy")
    Asr = max(0.2 * As, 0.0)
    fir, sr, Asrp = zelbet.dobierz_plyta(Asr, zelbet.smax_plyta(h, False, True), 8, 10)
    w.zbrojenie = f"dołem φ{fi} co {f(s / 10, 0)} cm (wzdłuż biegu), rozdzielcze φ{fir} co {f(sr / 10, 0)} cm; " \
                  f"w podporach górą φ{fi} co {f(2 * s / 10, 0)} cm na długości 0,25·L (9.3.1.2(2))"
    w.krok("Przyjęto", "", "", w.zbrojenie)
    lbd = zelbet.zakotwienie(fi, beton, stal).l_bd
    w.uwaga(f"W załamaniu bieg–spocznik pręty dolne krzyżować (nie prowadzić po wklęsłym narożu), zakotwienie l_bd = {f(lbd, 0)} mm.")
    Lr = sum(math.hypot(o.x1 - o.x0, (o.x1 - o.x0) * math.tan(alfa)) if o.typ == "bieg" else (o.x1 - o.x0) for o in odcinki)
    n = int(szer / (s / 1000)) + 1
    nr = int(Lr / (sr / 1000)) + 1
    w.prety = [zelbet.Pret(nazwa, 1, fi, round(Lr + 2 * 0.15, 2), n, "00", "dołem wzdłuż biegu (+ odgięcia w podporach)"),
               zelbet.Pret(nazwa, 2, fir, round(szer - 0.05, 2), nr, "00", "rozdzielcze"),
               zelbet.Pret(nazwa, 3, fi, round(0.25 * L + 0.3, 2), 2 * int(szer / (2 * s / 1000) + 1), "11", "górą przy podporach")]
    w.L, w.h, w.alfa, w.g_bieg, w.g_spocz, w.M_Ed, w.V_Ed = L, h, math.degrees(alfa), zb.g_k, zs.g_k, MEd, VEd
    return w
