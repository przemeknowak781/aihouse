# -*- coding: utf-8 -*-
"""W3 - schody, elementy zewnetrzne (plyty wysuniete, rama C, lamele, slupy), zagospodarowanie dzialki."""
from shapely.geometry import box
from shapely.ops import unary_union

# ------------------------------------------------------------------ schody: jeden rdzen (osie B-C / 3-4), dwubiegowe, identyczne na P0->P1 i P1->P2
# bieg nieparzysty (1, 3): pas wsch. x 5,295...6,295, w gore ku PN od y 5,505; spocznik pn.; bieg parzysty (2, 4): pas zach.
# x 4,155...5,155, w gore ku PD, wyjscie na y 5,505 (otwor w scianie grzbietowej). Oko 0,14 m (balustrada szklana).
SCHODY = dict(h=0.175, s=0.28, n_podn=18, biegi=2, podn_w_biegu=9, stopni_w_biegu=8, szer=1.00, oko=0.14,
              bieg_E=dict(x=(5.295, 6.295), y0=5.505, kier=+1),
              spocznik=dict(x=(4.155, 6.295), y=(7.745, 8.795)),
              bieg_W=dict(x=(4.155, 5.155), y0=7.745, kier=-1),
              gr_plyty_biegu=0.18)

# ------------------------------------------------------------------ plyty wysuniete i rama C (rzut + zakres z)
PLYTY = [
    dict(id="E-okap", opis="ST1: okap pd. strefy dziennej (linia E) - wysunięcie 1,00 m; na wsch. do x 13,80 (1,5 m nad patio)",
         poly=box(-1.80, -1.30, 13.80, -0.30), z=(2.75, 3.05), lacznik=True),
    dict(id="E-okap-W", opis="ST1: okap zach. salonu - wysunięcie 1,50 m (taras zach.)", poly=box(-1.80, -0.30, -0.30, 5.40), z=(2.75, 3.05), lacznik=True),
    dict(id="daszek", opis="ST1: daszek nad wejściem 2,70 x 1,20 m (na osi widoku)", poly=box(6.90, 11.60, 9.60, 12.80), z=(2.80, 3.05), lacznik=True),
    dict(id="C-dol", opis="rama C - płyta dolna (linia D) wysunięcie 1,00 m", poly=box(3.60, -1.30, 12.90, -0.30), z=(3.45, 3.65), lacznik=True),
    dict(id="C-gora", opis="rama C - płyta górna wysunięcie 1,00 m", poly=box(3.60, -1.30, 12.90, -0.30), z=(5.15, 5.35), lacznik=True),
    dict(id="C-boki", opis="rama C - boki (żebra 20 cm)", poly=unary_union([box(3.60, -1.30, 3.80, -0.30), box(12.70, -1.30, 12.90, -0.30)]),
         z=(3.45, 5.35), lacznik=True),
    dict(id="ST2L", opis="ST2L: płyta loggii P2 (obniżona 5,70-5,90) - wysunięcie pd. 0,90 m, zach. 0,90 m poza lico A",
         poly=unary_union([box(-2.20, -1.20, 12.60, -0.30), box(-2.20, -0.30, -1.30, 5.70)]), z=(5.70, 5.90), lacznik=True),
    dict(id="ST3-okap", opis="ST3: stropodach bryły A - wysunięcie pd. 0,90, zach. 0,90, wsch. 0,30 m",
         poly=unary_union([box(-2.20, -1.20, 12.60, -0.30), box(-2.20, -0.30, -1.30, 5.70), box(12.30, -0.30, 12.60, 5.70)]),
         z=(9.10, 9.85), lacznik=True),
    dict(id="G-okap", opis="STG: okap pd. garażu (linia D nad patio) - wysunięcie 1,00 m", poly=box(12.30, 3.50, 18.70, 4.50), z=(2.76, 3.65), lacznik=False),
]
DACHY = [  # dachy (rzut po obrysie zewn.), attyka
    dict(id="D-G", opis="dach zielony ekstensywny garażu (nieużytkowy)", poly=box(12.30, 4.50, 18.70, 11.60), attyka=3.65),
    dict(id="D-P0", opis="dach zielony skrzydła wejściowego + świetlik nad wiatrołapem", poly=box(-0.30, 9.20, 12.30, 11.60), attyka=3.40),
    dict(id="D-P1W", opis="dach P1 nad pokojem dziecka 2 (żwir/zielony)", poly=box(-0.30, 5.70, 3.75, 9.20), attyka=6.70),
    dict(id="D-P1E", opis="dach P1 nad pralnią (żwir)", poly=box(9.95, 5.70, 12.30, 9.20), attyka=6.70),
    dict(id="D-P2", opis="stropodach P2 + nadbudowy - PV ≤ 6,5 kWp, latarnia nad klatką", poly=unary_union([box(-2.20, -1.20, 12.60, 5.70), box(3.75, 5.70, 9.95, 9.20)]), attyka=9.85),
]
SWIETLIKI = [dict(id="SW1", opis="latarnia nad klatką (szkło 3-szybowe, stałe, bez wyniesienia ponad attykę)", poly=box(4.30, 5.70, 6.15, 8.60)),
             dict(id="SW2", opis="świetlik nad wiatrołapem na osi wejścia", poly=box(7.40, 9.60, 8.60, 11.00))]
LOGGIA = dict(poly=box(-1.00, 0.00, 12.00, 0.90), opis="loggia P2 (taras nad pom. ogrzewanymi, poziom +6,28) za ekranem lamel")
LAMELE = dict(x=(-1.30, 12.30), y=-0.40, z=(5.90, 9.10), rozstaw=0.12, b=0.04, h=0.08, mat="drewno termo / aluminium drewnopodobne")
SLUPY = [dict(id=f"SL{i+1}", xy=(x, 0.0), przekroj="RK 120x120x8 S355 w słupku fasady", z=(0.0, 2.80)) for i, x in enumerate([2.60, 4.50, 6.90, 9.30])]
SLUPKI_C = [dict(id=f"SLC{i+1}", xy=(x, 0.0), przekroj="RK 120x120x8 w słupku boksu C", z=(3.00, 5.70)) for i, x in enumerate([6.90, 9.30])]
SLUPY_P2 = [dict(id=f"SLA{i+1}", xy=(x, 0.0), przekroj="RK 100x100x6 w płaszczyźnie lamel", z=(5.90, 9.10)) for i, x in enumerate([-1.00, 2.60, 6.90, 9.30, 12.00])]

# ------------------------------------------------------------------ dzialka (uklad budynku): 32,00 x 50,00 m
DZ = dict(xw=-7.30, xe=24.70, ys=-31.00, yn=19.00)
LINIA_ZAB = DZ["yn"] - 6.0
H_NAROZ = dict(NW=101.40, NE=101.55, SW=101.10, SE=101.25)

TEREN_ELEM = dict(
    podjazd=dict(poly=box(12.30, 11.60, 18.70, 19.00), opis="podjazd - kostka betonowa szara, odwodnienie liniowe przed bramą garażu", typ="utw"),
    dojscie=dict(poly=box(7.40, 12.80, 8.60, 19.00), opis="dojście na osi furtka - drzwi (x = 8,00) - płyty betonowe 1,20 m", typ="utw"),
    lacznik=dict(poly=box(8.60, 13.20, 12.30, 14.20), opis="łącznik dojście - podjazd (płyty)", typ="utw"),
    taras=dict(poly=unary_union([box(-1.80, -4.50, 12.30, -0.30), box(-1.80, -0.30, -0.30, 5.40)]), opis="taras ogrodowy S + W (deska kompozytowa na legarach, -0,05)", typ="utw"),
    patio=dict(poly=box(12.30, -0.30, 17.40, 4.50), opis="patio poranne przy kuchni (E) - płyty na podsypce, osłonięte ścianą garażu od pn.", typ="utw"),
    os_ogrodowa=dict(poly=box(7.60, -22.00, 8.40, -4.50), opis="oś ogrodowa - ścieżka z płyt w trawie (przedłużenie osi wejścia)", typ="aż"),
    smietnik=dict(poly=box(9.20, 17.90, 11.30, 18.90), opis="osłona na pojemniki 4 x 240 l przy furtce, drzwiczki od ulicy", typ="utw"),
    pc_plyta=dict(poly=box(10.20, 11.85, 11.40, 12.45), opis="jedn. zewn. PC (R290) na fundamencie z wibroizolacją, osłona lamelowa", typ="utw"),
    niecka=dict(poly=box(-5.50, -15.00, 0.50, -11.00), opis="niecka chłonna / ogród deszczowy 24 m2 (przelew ze zbiornika)", typ="bio"),
)
MIEJSCA_GOSC = [box(12.90, 12.30, 15.40, 17.30), box(15.60, 12.30, 18.10, 17.30)]
ZBIORNIK = dict(xy=(-3.50, -7.50), wym=(2.4, 1.6), V=5.0, opis="szczelny zbiornik retencyjny 5 m3 (podlewanie), przelew do niecki chłonnej")
OGRODZENIE = dict(brama=(12.70, 17.90), furtka=(7.50, 8.50), wys=1.50)
ZK = (11.50, 12.30)
SIEC = dict(woda=22.20, kan=24.70, en=20.00, tel=20.50, gaz=28.00, jezdnia=(21.25, 26.75), pas=(19.00, 29.00))
PRZYLACZA = dict(
    woda=dict(pts=[(10.80, SIEC["woda"]), (10.80, 11.60)], opis="przyłącze wody PE 40 do przedsionka → wodomierz w pom. techn. 0.06"),
    kan=dict(pts=[(5.00, 11.60), (5.00, 15.00), (5.00, SIEC["kan"])], opis="przykanalik PVC 160, studzienka rewizyjna D425 (5,00; 15,00)"),
    en=dict(pts=[(11.90, 19.00), (11.90, 12.60), (11.30, 11.60)], opis="WLZ YKY 5x10 z ZK do RG (pom. techn.)"),
    tel=dict(pts=[(12.10, SIEC["tel"]), (12.10, 12.70), (11.60, 11.60)], opis="światłowód 2 x HDPE 40"),
    deszcz=dict(pts=[(-0.60, 11.60), (-1.20, 11.90), (-1.20, -6.70), (-2.30, -7.50)], opis="kanalizacja deszczowa z rur spustowych → zbiornik"),
)
DRZEWA = [(-3.5, -18.0, 4.0), (8.0, -24.5, 5.0), (19.0, -16.0, 4.0), (-4.5, -27.0, 3.5), (20.5, -27.0, 3.5), (2.5, 15.8, 1.8), (21.5, 9.0, 2.0)]
