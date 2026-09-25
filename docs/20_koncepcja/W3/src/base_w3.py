# -*- coding: utf-8 -*-
"""Wariant W3 koncepcji Domu LAMELA - SWIATLO / OGROD / SEKWENCJA WEJSCIA.
Baza modelu: osie, typy przegrod, poziomy, konstruktory rekordow.
Uklad: x->E, y->N, z->gora; (0,0) = przeciecie osi A (zach. os nosna bryly B) i osi 1 (pd.). Wymiary w metrach."""
from shapely.geometry import box

# ------------------------------------------------------------------ osie konstrukcyjne (os warstwy nosnej silikat 18)
OSIE_X = {"A'": -1.000, "A": 0.000, "B": 4.050, "B'": 4.500, "C": 6.400, "D": 9.650, "E": 12.000, "F": 18.400}
OSIE_Y = {"0": -0.150, "1": 0.000, "1'": 1.200, "2": 4.800, "3": 5.400, "4": 8.900, "5": 11.300}

# ------------------------------------------------------------------ typy przegrod: L = odsuniecie lica po stronie lewej (wnetrze), R = po prawej
TYPY = {
    "SZ1":  dict(nazwa="ściana zewn. nośna: tynk 1,5 + silikat 18 + EPS grafit/wełna 20 + tynk 1 cm (U≈0,15)", L=0.105, R=0.300, kol="#8c8c8c"),
    "SZL":  dict(nazwa="ściana zewn. lekka (P2: wspornik i lico loggii): szkielet stal/drewno + wełna 20 + płyta, gr. 40,5 cm", L=0.105, R=0.300, kol="#b0a58c"),
    "SW18": dict(nazwa="ściana wewn. nośna: silikat 18 + 2x tynk 1,5", L=0.105, R=0.105, kol="#8c8c8c"),
    "SWG":  dict(nazwa="ściana nośna dom/garaż: tynk 1,5 + silikat 18 + wełna 12 + tynk 1 (U≈0,28)", L=0.105, R=0.220, kol="#8c8c8c"),
    "DZ12": dict(nazwa="ścianka działowa: silikat 12 + 2x tynk 1,5", L=0.075, R=0.075, kol="#c8c8c8"),
    "DZL":  dict(nazwa="ścianka działowa lekka GK 12,5 cm (na stropie nad otwarciem / krawędzi pustki)", L=0.0625, R=0.0625, kol="#dedede"),
    "SK":   dict(nazwa="przegroda szklana w ramie stalowej (wiatrołap / hol), gr. 6 cm", L=0.030, R=0.030, kol="#cfe3f7"),
}

# ------------------------------------------------------------------ poziomy (wzgl. +-0,00 = 101,65 m n.p.m.)
POZ = dict(zero_abs=101.65, P0=0.00, P1=3.15, P2=6.30, wys_kond=3.15, podl=0.15,
           ST1=(2.80, 3.00),            # strop nad P0 (plyta 20 cm)
           ST2=(5.95, 6.15),            # strop nad P1 (plyta 20 cm)
           ST2L=(5.70, 5.90),           # obnizona plyta loggii P2 (y -1,2...1,2), taras nad pom. ogrzewanym
           ST3=(9.10, 9.32),            # stropodach P2 i nadbudowy (plyta 22 cm)
           STG=(2.76, 3.00),            # stropodach garazu (plyta 24 cm, dach zielony)
           dach_P2_warstwy=9.62, attyka_P2=9.85, dach_P1_warstwy=6.50, attyka_P1=6.70,
           dach_P0_warstwy=3.30, attyka_P0=3.40, dach_G_warstwy=3.40, attyka_G=3.65,
           lawa_spod=-1.10, teren_sr=-0.28)

E = 0.30  # przedluzenie sciany w narozu zewnetrznym (do lica ocieplenia)


def W(i, k, t, p1, p2, e1=0.0, e2=0.0, uw=""):
    """Sciana: os warstwy nosnej p1->p2; wnetrze (strona 'L') po lewej stronie kierunku."""
    return dict(id=i, kond=k, typ=t, p1=p1, p2=p2, ext=(e1, e2), uw=uw)


def O(i, s, a, b, typ, wys, par=0.0, sym="", zaw=None, kier=None, uw="", kw=1, podz=None, hs=None):
    """Otwor: sciana s, zakres a..b wzdluz sciany (x dla poziomych, y dla pionowych); podz = wsp. slupkow; hs = kwatery z drzwiami HS."""
    return dict(id=i, sciana=s, a=a, b=b, szer=round(b - a, 3), typ=typ, wys=wys, par=par, sym=sym, zaw=zaw,
                kier=kier, uw=uw, kw=kw, podz=podz or [], hs=hs or [])


def R(i, n, k, geo, kat, pobyt=False, minimum=None, posadzka="", uw=""):
    poly = box(*geo) if isinstance(geo, tuple) and len(geo) == 4 else geo
    return dict(id=i, nazwa=n, kond=k, poly=poly, kat=kat, pobyt=pobyt, min=minimum, posadzka=posadzka, uw=uw)


# wspolne piony instalacyjne (te same wspolrzedne na wszystkich kondygnacjach)
SZACHT_SI = box(6.505, 5.505, 6.905, 5.905)    # pion kan. K1 (lazienki P1/P2) + kanaly went. -> przez dach
SZACHT_S2 = box(9.755, 8.395, 10.155, 8.795)   # pion kan. K2 (pralnia P1) przez pom. techn. P0
# rdzen schodow (os B..C, 3..4) - wymiary w swietle
SCH_X = (4.155, 6.295)
SCH_Y = (5.505, 8.795)
