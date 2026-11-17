#!/usr/bin/env python3
"""v1.2b – decyzje po scaleniu S-3: zamknięcie spraw otwartych specyfikacji v1.2 (V12-OPEN 2, 3, 5, 8 i lista
docs/90_audyt/do_przeliczenia_po_v11.md) – dowody liczbowe i zapis do model/koncepcja.json.

Uruchomienie (z katalogu umwd/; PO _v12_scalenie.py --zapisz – skrypt dopisuje klucze do zapisanego JSON):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_v12b_decyzje.py [--zapisz]
Bez --zapisz tylko liczy i waliduje. Zapis jest idempotentny (ponowne uruchomienie daje ten sam plik).

Sekcje (każda kończy się assertami):
  [D1] M.13 pkt 6 – szerokość biegu między poręczami ≥ 1,60 m (klatki A, B, C; schody S → +30,90; stopnie galerii)
  [D2] MDS – podstawa prawna, pojemność, powierzchnia, wysokość, wyjścia (w tym zapasowe poza strefą zagruzowania), sanitariaty,
       wentylacja; „ukrycie”/„2 klatki ≥ 15 m” – rozwiązanie niezależne od sposobu pomiaru
  [D3] Hala Obywatelska – oś przekątna, strefa wolna 6,30 m (wielokąt), drzwi ogrodowe w osi, przeniesienia pomieszczeń, słupy
  [D4] Sala Sejmiku – galeria 20 + 3 wobec brzmienia programu (PU s. 6)
  [D5] Elewacja segmentu od dziedzińca (lico S-W, elewacja Sg) – otwory na kondygnacjach (pole dla przebiegu rzutów)
  [D6] Przegrody od dziedzińca – ETICS (tabela przegród, U, koszt)
  [D7] Wartości użyte w rysunkach (pochwyt, kaseta ZIP, ΔU, strop glin QpB, spadek dachu skrzydła, fryz)
  [D8] Pas 4,6 m od bulwaru – 2 drzewa w pasie, strefy korzeniowe i skrzynki rozsączające
  [D9] Odstępstwa od wytycznych M.13 – usunięte i pozostałe (meta.odstepstwa, R-013)
  [W]  walidacja zapisu
Źródła: koncepcja.json (po _v12_scalenie.py), site.json, _s2_model.py, _v12_trzony.py, _v12_koszt.py, _rewizja_parking.py,
_rewizja_drzewa_wynik.json, M.13 (tekst: 00_materialy/tekst), rozp. MSWiA Dz.U. 2025 poz. 932, ustawa o ochronie ludności
(art. 93–95a w brzmieniu Dz.U. 2026 poz. 646). NIE zmienia model/budynek.json, tools/*, docs/95_opis, render/.
Nie korzystano z informacji o pracach ani wynikach konkursu.

v1.2b-fix (po weryfikacji v1.2b, 17.11.2026): [D1] pochwyty Ø 35 we wnękach 0,09 m (0,16 m żelbetu – REI 120), drzwi przy spocznikach
bez kolizji z przedłużeniami pochwytów (_v12_trzony.py [T7]); [D2] wyjścia: przez Halę tylko klatka A (WT § 256 ust. 6), klatka B –
korytarz ewakuacyjny KE-B do elewacji ogrodowej, klatka C – drzwi zewnętrzne od dziedzińca; MDS projektowo 600 os. (≥ ⌈PU/15⌉ z PU
z pomieszczeniami MDS podziemia), punkt przygotowania posiłków (§ 8 ust. 2 pkt 3), Ad = 25 kN/m² na całym stropie nad −1, podpory
tymczasowe (liczba = koszt); [D3] strefa wolna 6,30 m z 2 słupami – pas bez przeszkód 4,26 m (wymaganie sformułowane wprost), pokój
cichy po stronie NW osi, wymagania dla agenta 3D; [D8] pnie 1,60 m od dojazdu (korona bez nawisu); [D9] O2 – liczby pogłębienia −2.
"""
import copy
import io
import json
import math
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from shapely.geometry import Point, Polygon, LineString, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "model", "koncepcja.json")
K0 = json.load(open(OUT, encoding="utf-8"))
SITE = json.load(open(os.path.join(ROOT, "model", "site.json"), encoding="utf-8"))
with redirect_stdout(io.StringIO()):
    import _s2_model as S2                      # noqa: E402
    import _v12_trzony as T                     # noqa: E402
    import _v12_koszt as C                      # noqa: E402
    import _rewizja_parking as RP               # noqa: E402
    import _rewizja_drzewa as RD                # noqa: E402
from _rewizja_wspolne import rect_uv, uv2en, en2uv, sd2en as sd2en_, OI, OGR, D102, W as W_EN, SEG as SEG_EN  # noqa: E402

uv2en_, en2uv_ = S2.uv2en, S2.en2uv
DATA = {}                      # wyniki sekcji → zapis JSON
CHECKS = []                    # (sekcja, opis, wynik)


def hr(t):
    print("\n" + "=" * 110 + "\n" + t + "\n" + "=" * 110)


def ok(sec, txt, cond):
    CHECKS.append((sec, txt, bool(cond)))
    assert cond, f"{sec}: {txt}"
    return "✔"


def pl(x, nd=2):
    return f"{x:,.{nd}f}".replace(",", " ").replace(".", ",")


def ring_uv(g, nd=3):
    return [[round(x, nd), round(y, nd)] for x, y in list(g.exterior.coords)[:-1]]


def ring_en_from_uv(g, nd=3):
    pts = [[round(c, nd) for c in uv2en_(x, y)] for x, y in list(g.exterior.coords)[:-1]]
    return pts if Polygon(pts).exterior.is_ccw else pts[::-1]


def ring_en(g, nd=3):
    pts = [[round(x, nd), round(y, nd)] for x, y in list(g.exterior.coords)[:-1]]
    return pts if Polygon(pts).exterior.is_ccw else pts[::-1]


def to_uv(g):
    return Polygon([en2uv_(*p) for p in g.exterior.coords])


KOND = {k["kondygnacja"]: k for k in K0["kondygnacje"]}
PU = float(K0["bilans"]["PU_m2"])

# ================================================================================================ [D1]
hr("[D1] M.13 pkt 6 – szerokość biegu mierzona między wewnętrznymi krawędziami poręczy ≥ 1,60 m")
print("  M.13 (Schody – biegi): pkt 4.1 „minimum 1,6 m – na klatkach schodowych znajdujących się na drogach ewakuacyjnych”; pkt 6"
      " „Szerokość biegu mierz pomiędzy wewnętrznymi krawędziami poręczy”; Balustrady i poręcze pkt 2 „Poręcze możesz umieścić we wnęce"
      " zlokalizowanej na ścianie”, pkt 6 – przedłużenie pochwytów 0,3 m poza pierwszy i ostatni stopień, pkt 12 „≥ 5 cm między poręczą"
      " a najbliższą płaszczyzną pionową”, pkt 10 – Ø 3,5–4,5 cm.")
print("  Ognioodporność (v1.2b-fix): ściany klatek wzdłuż biegów są ścianami nośnymi trzonów – główna konstrukcja nośna klasy „B” R 120"
      " (WT § 216 ust. 1; ppoz.md § 3.3); EN 1992-1-2 tab. 5.4 (ściana nośna nagrzewana jednostronnie): REI 120 – 150 mm / a 25 przy"
      " μfi = 0,35, 160 mm / a 35 przy μfi = 0,7 → wnęka 0,09 m w ścianie 0,25 m zostawia 0,16 m (bez obliczania μfi); pochwyt Ø 35 mm"
      " (dolna granica M.13) zachowuje 1,61 m w świetle poręczy.")
print("  Dotyczy: klatek A, B, C (drogi ewakuacyjne; klatka A także S → +30,90). Przedsionek A' nie jest klatką (bez schodów)."
      " Schody reprezentacyjne S → +30,90 i stopnie galerii – kontrolnie (pkt 4.3: ≥ 1,20 m).")
print("  Warianty: (a) pochwyty we wnękach + balustrada środkowa duszy – klatki 3,40 m bez zmian obrysów; (b) poszerzenie klatek do"
      f" {2 * (1.60 + 0.095 + 0.05) + 0.20:.2f} m (pochwyty na wspornikach): A – przedsionek 3,10 → 2,81 m (wykonalne), B – brak 0,29 m"
      " w obrysie (przesunięcie ściany trzonu B o 0,29 m zabiera pokój KS.04c na kond. 6 i pomieszczenia pd. na kond. 1–5),"
      " C – przedsionek 2,00 → 1,71 m (< 2,0 dla MOE); (c) poszerzenie tylko A + odstępstwo B, C – odrzucone (zgodność > koszt).")
for k, v in T.RES_T7.items():
    print(f"  klatka {k}: bieg {v['bieg']:.2f} m, w świetle poręczy {v['swiatlo']:.3f} m {ok('D1', f'klatka {k} ≥ 1,60', v['swiatlo'] >= 1.60 - 1e-9)};"
          f" ściany wzdłuż biegów {v['sciany'][0]:.2f}/{v['sciany'][1]:.2f} m, żelbet w pasie wnęki ≥ {min(v['zelbet_we_wnece']):.2f} m"
          f" {ok('D1', f'klatka {k} żelbet ≥ 0,15', min(v['zelbet_we_wnece']) >= 0.15 - 1e-9)}; przejść kondygnacyjnych {v['przejscia']}"
          f" ({v['trojbiegowe']} trójbiegowe)")
cA, cB = S2.CORE_A_CELLS, S2.CORE_B_CELLS
D1_REQ = [
    "ściany klatek A, B, C wzdłuż biegów 0,25 m (żelbet C30/37) – ściany nośne trzonów R 120; we wnękach 0,09 × 0,30 m (pas 0,68–0,98 m"
    " nad linią krawędzi stopni, ciągły wzdłuż biegów i spoczników oraz na przedłużeniach 0,30 m) pochwyty Ø 35 mm na 0,75 i 0,90 m,"
    " 5 cm od tła wnęki, mocowane od dołu – krawędź pochwytu 0,5 cm za licem ściany; w pasie wnęki 0,16 m żelbetu, otulina od strony"
    " pomieszczeń a ≥ 35 mm (REI 120 przy μfi = 0,7 – EN 1992-1-2 tab. 5.4)",
    "dusza 0,20 m: balustrada środkowa (płaszczyzna ≤ 20 mm – pręty pionowe Ø 12 co ≤ 0,12 m lub szkło VSG 2 × 8 mm, wys. 1,10 m),"
    " słupki kotwione bocznie w czołach płyt biegów; pochwyty obustronne Ø 35 na wspornikach od dołu, 5 cm od płaszczyzny balustrady –"
    " krawędź pochwytu 0,5 cm nad duszą od krawędzi biegu; szczelina bieg–balustrada 0,09 m ≤ 0,12",
    "pasy biegów (biegi kolejno zmieniają pas): A – bieg przychodzący na S, 1–6 i +30,90 w pasie wsch.; B – bieg przychodzący na P w pasie"
    " zach.; C – bieg przychodzący na P w pasie od dziedzińca; głębokość spocznika kondygnacyjnego w pasie = długość klatki − 1,50 − rzut"
    " biegu (_v12_trzony.py [T7], rdzenie.klatki_M13_pkt6.spoczniki)",
    "drzwi w ścianach podłużnych przy spocznikach – otwory (z ościeżnicą) poza przedłużeniami pochwytów 0,30 m z odstępem ≥ 0,05 m:"
    " A – przedsionek → klatka (ściana wsch.) v 12,05–13,20 (w świetle 1,05; −1: v 12,05–13,45; P: v 16,45–17,85), A' → klatka"
    " (ściana zach., +30,90) v 12,55–13,55; B – na P drzwi z podestu do korytarza KE-B (ściana zach.) v 5,75–7,35; C – przedsionek → klatka"
    " s 0,75–2,05 (−1), 5,15–6,55 (P), 0,75–2,45 (1), 0,75–1,90 (2–4); C – na P drzwi zewnętrzne w ścianie od dziedzińca s 4,70–6,50"
    " (lista: rdzenie.klatki_M13_pkt6.drzwi_przy_spocznikach)",
    f"przedsionek A u {cA['przedsionek_A'].bounds[0]:.2f}–{cA['przedsionek_A'].bounds[2]:.2f} (3,05 × 5,80 m; MOE – _s2_ewakuacja.py [E6])",
    f"trzon B: szacht i szyby P1, P2 u {cB['P1'].bounds[0]:.2f}–{cB['P1'].bounds[2]:.2f} (+0,05 m na wsch.), ściana wsch. trzonu 0,20 m"
    " (drzwi P1/P2 w licu u 31,10 bez zmian; drzwi zach. P2 na −2/−1 w ścianie 0,25 m)",
    "trzon C (v1.2b-fix: +0,05 m ku dziedzińcowi – korytarz skrzydła przy trzonie 1,825 m): obrys d 8,45–14,55, przedsionek d 8,65–10,65"
    " (5,80 × 2,00 m), ściana klatka/przedsionek 0,25 m, ściana od korytarza 0,20 m, klatka d 10,90–14,30, szachty d 8,65–14,30; ściana"
    " trzonu od dziedzińca (d 14,30–14,55) przylega do warstwy żelbetowej ściany ETICS (d 14,60)",
    "spoczniki pośrednie: pochwyt od duszy ciągły (zawinięty wokół końca duszy); przyścienny we wnękach ścian podłużnych – na ścianie"
    " czołowej spocznika (długość 3,40 m > 3,0 m, M.13 pkt 5) dopuszczalna przerwa",
]
for r_ in D1_REQ:
    print("   – " + r_)
DATA["D1"] = {
    "decyzja": "M.13 pkt 6 spełniony bez odstępstwa: pochwyty przyścienne Ø 35 mm we wnękach 0,09 m ścian klatek (0,16 m żelbetu – REI 120)"
               " i pochwyty od duszy na balustradzie środkowej; klatki 3,40 m bez zmian obrysów trzonów; drzwi przy spocznikach poza"
               " przedłużeniami pochwytów (v1.2b-fix)",
    "ognioodpornosc": "ściany klatek wzdłuż biegów = ściany nośne trzonów, R 120 (klasa „B”, WT § 216 ust. 1); w pasie wnęki 0,16 m żelbetu"
                      " ≥ 160 mm / a ≥ 35 mm (EN 1992-1-2 tab. 5.4, REI 120, μfi = 0,7 – bez obliczania μfi); obudowa klatki REI 60 (§ 249)",
    "spoczniki": {k: {lv: {"koniec": ("pd./zach." if d_["koniec"] == "S-end" else "pn./wsch."),
                           "pasy": {p_: {"glebokosc_m": x[0], "bieg": x[1]} for p_, x in d_["pasy"].items()}}
                      for lv, d_ in T.LAND_T7[k].items()} for k in T.LAND_T7},
    "pasy_biegow": {k: {"biegi_parzyste": v[0], "biegi_nieparzyste": v[1]} for k, v in T.LANES.items()},
    "drzwi_przy_spocznikach": [{"klatka": d_["klatka"], "kond": d_["kond"], "sciana_pasa": d_["pas"],
                                "otwor_m": [round(d_["otwor"][0], 2), round(d_["otwor"][1], 2)], "w_swietle_m": d_["w_swietle"],
                                "wymagane_m": d_["wymagane"],
                                "przedluzenie_pochwytu_m": [round(x, 2) for x in d_["przedluzenie"]] if d_["przedluzenie"] else None,
                                "opis": d_["opis"]} for d_ in T.DOOR_T7],
    "pochwyt": {"srednica_m": T.POCH_D, "odstep_od_plaszczyzny_m": T.POCH_GAP, "wysokosci_m": [0.75, 0.90]},
    "wneka": {"glebokosc_m": T.WNEKA_D, "wysokosc_m": T.WNEKA_H, "pas_nad_krawedzia_stopni_m": [0.68, 0.98]},
    "balustrada_duszy": {"plaszczyzna_max_m": T.BAL_T, "wysokosc_m": 1.10, "szczelina_bieg_balustrada_m": round((T.WELL - T.BAL_T) / 2, 3)},
    "klatki": {k: {"szerokosc_klatki_m": round(v["szer"], 2), "bieg_konstrukcyjny_m": round(v["bieg"], 2),
                   "w_swietle_poreczy_m": round(v["swiatlo"], 3), "sciany_wzdluz_biegow_m": [round(x, 2) for x in v["sciany"]],
                   "zelbet_w_pasie_wneki_m": round(min(v["zelbet_we_wnece"]), 2), "przejscia_kondygnacyjne": v["przejscia"]}
               for k, v in T.RES_T7.items()},
    "schody_reprezentacyjne_w_swietle_m": round((S2.STAIR_V[1] - S2.STAIR_V[0]) - 2 * T.POCH_OCC, 2),
    "stopnie_galerii": {"szerokosc_m": round(S2.GAL_STEPS[0].bounds[3] - S2.GAL_STEPS[0].bounds[1], 2),
                        "w_swietle_poreczy_m": round(S2.GAL_STEPS[0].bounds[3] - S2.GAL_STEPS[0].bounds[1] - 2 * T.POCH_OCC, 2)},
    "warianty_odrzucone": "poszerzenie klatek do 3,69 m (B i C wymagają zmiany obrysów trzonów; C – przedsionek < 2,0 m); odstępstwo",
    "wymagania_dla_rzutow": D1_REQ,
    "dowod": "_v12_trzony.py [T7] (szerokość w świetle poręczy, żelbet w pasie wnęki, test kolizji drzwi z przedłużeniami); _s2_ewakuacja.py"
             " [E6] (MOE w przedsionku A 3,05 m z drzwiami do klatki v 12,05–13,20)",
}
ok("D1", "drzwi przy spocznikach bez kolizji z przedłużeniami pochwytów", all(d_["ok"] for d_ in T.DOOR_T7) and len(T.DOOR_T7) >= 20)
ok("D1", "żelbet w pasie wnęki ≥ 0,16 (REI 120, μfi = 0,7)", all(min(v["zelbet_we_wnece"]) >= 0.16 - 1e-9 for v in T.RES_T7.values()))
print(f"  drzwi przy spocznikach (_v12_trzony.py [T7]): {len(T.DOOR_T7)} przypadków (klatka × kondygnacja) – bez kolizji z przedłużeniami"
      f" pochwytów 0,30 m i z wymaganą szerokością ✔")

# ================================================================================================ [D2]
hr("[D2] MDS – miejsce doraźnego schronienia (art. 94 ustawy o ochronie ludności; rozp. MSWiA Dz.U. 2025 poz. 932)")
N_MIN = math.ceil(PU / 15 - 1e-9)
assert N_MIN == C.MDS_N_MIN and abs(PU - C.PU12) < 0.01, "PU/15 w kosztach ≠ bilans"
N_MDS = C.MDS_N                                  # v1.2b-fix: pojemność projektowa 600 os. (≥ ⌈PU/15⌉; zapas na PU po przebiegu rzutów)
print(f"  Podstawa: art. 94 ust. 1 pkt 1 (brzmienie Dz.U. 2026 poz. 646) – kondygnacje podziemne i garaże, w których nie przewidziano"
      f" budowli ochronnej, umożliwiają MDS o pojemności ≥ PU użyteczności publicznej / 15 m²: {pl(PU)} / 15 = {PU / 15:.2f} → {N_MDS} os.;"
      f" pkt 3 (garaż: 2 × 110 m.p. = 220) – mniej; art. 93: budowla ochronna (zwolnienie – decyzja, art. 93 ust. 2; pojemność i kategoria"
      f" – postanowienie organu, art. 95a ust. 3).")
RP.CORES["A"] = rect_uv(*[S2.CORE_A.bounds[i] for i in (0, 1, 2, 3)])
with redirect_stdout(io.StringIO()):
    PRES = RP.run(False)
gate = LineString([uv2en(40.0, -0.40), uv2en(40.0, -4.40)])            # brama garażu (lico wsch. segmentu, próg 119,10)
LEVEL_MDS = {}
for lvl, r in PRES.items():
    I = r["I"]
    plant = unary_union([v[0] for v in r["spec"]["plant"].values()]).intersection(I).difference(r["aisles"])
    stack = []
    if lvl == "-1":
        used = set()
        for f, a, b in RP.STACK_ROWS_M1:                                # jednostki podwójne stackerów (jak RP.stacker_bonus)
            row = RP.to_poly(f, a, b).buffer(0.01)
            inrow = [i for i, x in enumerate(r["stalls"]) if x.within(row)]
            for i in inrow:
                if i in used:
                    continue
                for j in inrow:
                    if j != i and j not in used and r["stalls"][i].buffer(0.02).intersection(r["stalls"][j]).area > 0.01 \
                            and r["stalls"][i].union(r["stalls"][j]).area > 24.0:
                        used |= {i, j}
                        stack += [r["stalls"][i], r["stalls"][j]]
                        break
    stackU = unary_union(stack) if stack else Polygon()
    free = I.difference(r["obst"]).difference(plant).difference(stackU)
    free20 = free.difference(gate.buffer(20.0))
    h = K0["wysokosci_w_swietle"]["garaz_" + lvl]
    vol = I.difference(r["obst"]).difference(plant).area * h
    cap = int(free20.area / (1.5 + 0.03 * 0.5))                       # 1,5 m²/os., 3 % osób na wózkach po 2,0 m² (§ 9 ust. 4)
    LEVEL_MDS[lvl] = dict(I=I.area, free=free.area, free20=free20.area, stack=stackU.area, plant=plant.area, h=h, V=vol, cap=cap,
                          n_stack=len(stack) // 2)
    print(f"  {lvl}: wnętrze {I.area:.1f} m²; − rdzenie, słupy, rampy {I.intersection(r['obst']).area:.1f}; − pomieszczenia techniczne"
          f" (strefy) {plant.area:.1f}; − stackery {len(stack) // 2} jedn. ({stackU.area:.1f} m², pod platformą < 2 m – § 9 ust. 2)"
          f" → wolna {free.area:.1f}; poza 20 m od bramy (§ 7 ust. 3) {free20.area:.1f} m²; wysokość w świetle {h:.2f} m (≥ 2,0 ✔);"
          f" pojemność ≤ {cap} os. (1,5 m²/os., 3 % na wózkach × 2,0 m²); kubatura netto ≈ {vol:.0f} m³")
print(f"  v1.2b-fix: PU z pomieszczeniami MDS/ukrycia podziemia ze specyfikacji (_v12_koszt.py [K0]) {pl(PU)} m² → ⌈PU/15⌉ = {N_MIN} os.;"
      f" pojemność projektowa MDS {N_MDS} os. (zapas na PU ≤ {pl(N_MDS * 15, 0)} m² po przebiegu rzutów; reguła: MDS ≥ ⌈PU z F.15.C / 15⌉)"
      f" {ok('D2', 'MDS ≥ ⌈PU/15⌉', N_MDS >= N_MIN)}")
L1 = LEVEL_MDS["-1"]
cap94 = int(0.75 * (LEVEL_MDS["-1"]["I"] + LEVEL_MDS["-2"]["I"]) / 1.5)
print(f"  górna granica art. 94 (75 % pow. netto podziemia / 1,5): {cap94} os. – nie ogranicza")
print(f"  DECYZJA: MDS {N_MDS} os. w całości na −1 ({L1['free20']:.0f} m² wolnej powierzchni ≥ {N_MDS} × 1,515 = {N_MDS * 1.515:.0f} m²"
      f" {ok('D2', 'pojemność −1 ≥ PU/15', L1['cap'] >= N_MDS)}) – spełnia art. 94 przy każdej wykładni: (i) MDS w całym podziemiu,"
      f" (ii) budowla ochronna na −2 + MDS w kondygnacji bez budowli ochronnej, (iii) zwolnienie z art. 93. −2 = rezerwa budowli ochronnej"
      f" (ukrycie, filtrowentylacja; projektowo do 300 os.; pojemność i kategoria wg postanowienia organu – art. 95a ust. 3).")
# ---- wyjścia (§ 6 ust. 2–4)
n_ew = math.ceil(N_MDS / 200)
n_zap = math.ceil(N_MDS / 400)
kl_cl = min(v["swiatlo"] for v in T.RES_T7.values())
w_req = 0.4 * N_MDS / 100
# v1.2b-fix: drogi z klatek na zewnątrz na parterze – WT § 256 ust. 6 pkt 1 (przez jeden hol droga tylko z jednej klatki; Wyj. 20 odp. 78),
# rozp. 2025 poz. 932 § 6 ust. 3 pkt 1 (wyjście umożliwia ewakuację na zewnątrz)
KOR_B = unary_union([box(23.05, 0.50, 24.85, 7.45), box(19.00, 0.50, 24.85, 2.30)])      # korytarz KE-B (w świetle 1,80 m), uv wieży
KOR_B_DRZWI_KL = ((24.85, 5.75), (24.85, 7.35))                  # z podestu P klatki B (ściana zach. trzonu B) – _v12_trzony.py [T7]
KOR_B_DRZWI_ZEW = ((19.25, 0.50), (20.85, 0.50))                 # drzwi zewnętrzne 1,60 m (2 skrzydła) w elewacji ogrodowej (lico wewn.)
TRASY = {"A": ["klatka A", "przedsionek A (drzwi pd.)", "Hala Obywatelska (hol – § 256 ust. 6)", "drzwi ogrodowe 1,80 m / drzwi Bramy Mostowej"],
         "B": ["klatka B (podest P, drzwi v 5,75–7,35)", "korytarz ewakuacyjny KE-B EI 60 (1,80 m)", "drzwi zewnętrzne 1,60 m u 19,25–20,85"],
         "C": ["klatka C (podest P)", "drzwi zewnętrzne 1,80 m w ścianie od dziedzińca s 4,70–6,50", "dziedziniec → brama ogrodowa → Mazowiecka"]}
n_hol = sum(1 for t in TRASY.values() if any("Hala" in x for x in t))
print(f"  drogi z klatek na zewnątrz (parter): " + "; ".join(f"{k}: {' → '.join(v)}" for k, v in TRASY.items()))
print(f"  WT § 256 ust. 6 pkt 1: przez Halę droga ewakuacyjna tylko z klatki A ({n_hol} klatka) {ok('D2', 'jedna klatka przez hol', n_hol == 1)};"
      f" klatki B i C – wyjścia bezpośrednio na zewnątrz (B – korytarzem wydzielonym jak klatka) {ok('D2', 'B i C bez wspólnego holu', all(not any('Hala' in x for x in TRASY[k]) for k in ('B', 'C')))};"
      f" Hala: wysokość 4,80 ≥ 3,3 m ✔, drzwi zewnętrzne +50 % (§ 239 ust. 4 × 1,5 = 1,80 m: drzwi ogrodowe 1,80 ✔, drzwi w łuku ≥ 2,40)")
print(f"  § 6 ust. 2 pkt 1: wyjścia ewakuacyjne ceil({N_MDS}/200) = {n_ew} → klatki A, B, C (przedsionki, drzwi ≥ 1,2 m ≥ 0,8 × 1,8; każda z drogą"
      f" na zewnątrz – § 6 ust. 3 pkt 1) + rampa {ok('D2', 'wyjścia ewakuacyjne', len(TRASY) >= n_ew)}; szerokość ≥ 0,4 m/100 os. = {w_req:.2f} m"
      f" ≤ 3 × {kl_cl:.2f} = {3 * kl_cl:.2f} {ok('D2', 'szerokość dróg', 3 * kl_cl >= w_req)} (WT 0,6 m/100 os.: {0.6 * N_MDS / 100:.2f} ✔);"
      f" wyjścia zapasowe ceil({N_MDS}/400) = {n_zap}")
# ---- strefa prognozowanego zagruzowania (§ 6 ust. 7–8) i szyb podwójny
Mw = Polygon(K0["bryly"][1]["obrys_ccw"]).buffer(0)
BUD = unary_union([W_EN, Mw, SEG_EN])
H_W = K0["bryly"][0]["dach"]["attyka"]["nad_najnizszym_terenem_A"]
H_M = K0["bryly"][1]["dach"]["gzyms_attyka"]["nad_najnizszym_terenem"]
H_S = K0["bryly"][2]["dach"]["attyka"]["nad_najnizszym_terenem"]
ZAG = H_W / 3
MARG = 0.30
print(f"  strefa zagruzowania § 6 ust. 7–8: wysokość budynku = najwyższa część (wieża, attyka od najniższego terenu) {H_W:.2f} m → H/3 ="
      f" {ZAG:.2f} m od KAŻDEJ ściany zewnętrznej budynku (wykładnia ścisła – jeden budynek); wykładnia „po częściach”: skrzydło"
      f" {H_M / 3:.2f}, segment {H_S / 3:.2f} m")
old = Point(91.75, 32.00)
print(f"  szyb P-I6 (91,75; 32,00): od wieży {old.distance(W_EN):.2f}, skrzydła {old.distance(Mw):.2f}, segmentu {old.distance(SEG_EN):.2f} m"
      f" – w strefie przy wykładni ścisłej ({old.distance(SEG_EN):.2f} < {ZAG:.2f}) ✗ → zastąpiony")
su, sv = C.MDS_SZYB_UV
fp = rect_uv(su - C.MDS_SZYB_WYM[0] / 2, sv - C.MDS_SZYB_WYM[1] / 2, su + C.MDS_SZYB_WYM[0] / 2, sv + C.MDS_SZYB_WYM[1] / 2)
pos = {int(k): tuple(v) for k, v in json.load(open(os.path.join(HERE, "_rewizja_drzewa_wynik.json"), encoding="utf-8"))["polozenia_M06"].items()}
bil = json.load(open(os.path.join(HERE, "_rewizja_drzewa_wynik.json"), encoding="utf-8"))["bilans"]
kept = bil["zachowane"] + bil["ochrona"]
Z12 = unary_union([Point(pos[n]).buffer(RD.TREES_M06[n][2]) for n in kept if n in pos and RD.TREES_M06[n][1] in ("Z1", "Z2")])
Z3 = {n: Point(pos[n]).buffer(RD.TREES_M06[n][2]) for n in kept if n in pos and RD.TREES_M06[n][1] == "Z3"}
pa = uv2en(*C.MDS_PORTAL_UV)
pc = fp.centroid
tunel = LineString([pa, (pc.x, pc.y)])
trench = tunel.buffer(1.7, cap_style=2)
d_fp = {"wieża": fp.distance(W_EN), "skrzydło": fp.distance(Mw), "segment": fp.distance(SEG_EN)}
z3hit = [n for n, g in Z3.items() if g.intersects(fp.union(trench))]
print(f"  SZYB PODWÓJNY SZ-MDS: środek uv ({su:.2f}; {sv:.2f}) = en ({pc.x:.2f}; {pc.y:.2f}); obrys {C.MDS_SZYB_WYM[0]:.2f} × {C.MDS_SZYB_WYM[1]:.2f} m"
      f" (2 przedziały 1,00 × 1,05 m w świetle, żelbet 0,25 m, drabiny, 2 włazy 0,8 × 0,8 ≥ 0,6 × 0,6 – § 6 ust. 4 pkt 2 i ust. 5 pkt 2a)")
print(f"     odległość obrysu od ścian: wieża {d_fp['wieża']:.2f}, skrzydło {d_fp['skrzydło']:.2f}, segment {d_fp['segment']:.2f} m ≥ H/3 + {MARG:.2f}"
      f" = {ZAG + MARG:.2f} {ok('D2', 'szyb poza strefą zagruzowania (wykładnia ścisła)', min(d_fp.values()) >= ZAG + MARG - 1e-6)};"
      f" w obszarze inwestycji {ok('D2', 'szyb w OI', OI.buffer(-0.5).contains(fp))}; poza ogródkami"
      f" {ok('D2', 'szyb poza ogródkami', not fp.intersects(OGR.buffer(0.5)))} i dojazdem dz. 10/2 {ok('D2', 'poza D102', not fp.intersects(D102.buffer(0.5)))};"
      f" poza strefami Z1/Z2 drzew M.06 {ok('D2', 'szyb poza Z1/Z2', not fp.intersects(Z12.buffer(0.5)))}")
print(f"     tunel podwójny z −1: wylot w ścianie szczelinowej uv {C.MDS_PORTAL_UV} (droga u stopy rampy ulicznej), długość {C.MDS_TUNEL_M:.1f} m,"
      f" przekrój 2 × 0,90 × 1,50 m (≥ 0,6 × 0,8); wykop tunelu (±1,7 m) poza Z1/Z2 {ok('D2', 'tunel poza Z1/Z2', not trench.intersects(Z12))}"
      f" i ogródkami {ok('D2', 'tunel poza ogródkami', not trench.intersects(OGR))}; strefy Z3 (dopuszczalne z ochroną): {z3hit or 'brak'}")
# wylot w drodze, bez stanowisk
r1 = PRES["-1"]
portal_uv = box(C.MDS_PORTAL_UV[0] - 1.40, -4.40, C.MDS_PORTAL_UV[0] + 1.40, -3.60)
portal = Polygon([uv2en(*p) for p in portal_uv.exterior.coords])
col_st = portal.intersection(unary_union(r1["stalls"])).area
col_ob = portal.intersection(r1["obst"]).area
in_aisle = portal.intersection(r1["aisles"]).area / portal.area
print(f"     wylot na −1 (u {C.MDS_PORTAL_UV[0] - 1.40:.2f}–{C.MDS_PORTAL_UV[0] + 1.40:.2f}): kolizja ze stanowiskami {col_st:.2f} m²"
      f" {ok('D2', 'wylot bez utraty stanowisk', col_st < 0.01)}, z rampą/słupami {col_ob:.2f} m² {ok('D2', 'wylot poza rampą', col_ob < 0.01)};"
      f" w drodze {in_aisle:.0%} – garaż 110 m.p. bez zmian")
kA, kB = cA["klatka_A"], cB["klatka_B"]
dA = Point(uv2en(*kA.centroid.coords[0])).distance(fp)
dB = Point(uv2en(*kB.centroid.coords[0])).distance(fp)
print(f"  „2 klatki ≥ 15 m” (§ 6 ust. 5 pkt 1b): środki klatek A–B {kA.centroid.distance(kB.centroid):.1f} m, obudowy {kA.distance(kB):.2f} m –"
      f" BEZ ZNACZENIA: wyjścia zapasowe leżą poza strefą zagruzowania (ust. 4 pkt 1), więc ust. 5 (limit 300 os., 30 m³/os.) nie ma"
      f" zastosowania; gdyby organ zastosował ust. 5 do −2 – szyb SZ-MDS jest {min(dA, dB):.1f} m od klatek A/B (≥ 15 m, ust. 5 pkt 2a)"
      f" {ok('D2', 'szyb ≥ 15 m od klatek', min(dA, dB) >= 15.0)}, a pojemność −2 w tym reżimie ≤ V/30 = {LEVEL_MDS['-2']['V'] / 30:.0f} os.")
# ---- sanitariaty (§ 8 ust. 2)
n_um = math.ceil(N_MDS / 75)
SAN = {"miski_ustepowe": 3, "ustepy_suche": n_um - 3, "umywalki": n_um}
pos_plant = [k for k in PRES["-1"]["plant"] if "posiłków" in k]
P_POS = 2 * 3.5 * 0.5 + 2.0                       # punkt przygotowania posiłków: 2 płyty 3,5 kW (współczynnik 0,5) + warnik/chłodziarka 2 kW
E_POS = P_POS * 12                                # 12 h pracy w ciągu 48 h (posiłki ciepłe 3 × dziennie, napoje)
print(f"  § 8 ust. 2 pkt 3 (> 200 os.): urządzenia do przygotowywania posiłków – punkt przygotowania posiłków MDS 6 m² obok sanitariatów"
      f" (zlewozmywak z wodą pitną i kanalizacją, 2 płyty indukcyjne 3,5 kW, warnik 20 l, chłodziarka, blat; zasilanie z szyny odbiorów"
      f" krytycznych) {ok('D2', '§ 8 ust. 2 pkt 3 – posiłki', len(pos_plant) == 1 and PRES['-1']['plant'][pos_plant[0]][2])};"
      f" moc ≈ {P_POS:.1f} kW, energia w 48 h ≈ {E_POS:.0f} kWh; pkt 4 – odcięcie prądu i wody przy wejściu instalacji do MDS ✔")
print(f"  § 8 ust. 2 (> 200 os.): na 75 os. umywalka i miska/ustęp suchy → {n_um} + {n_um}: sanitariaty MDS −1 30 m² – 3 miski (w tym WC"
      f" dostępne; za przedsionkiem dźwigów A1/A2) + umywalka zbiorcza 8 stanowisk; magazyn MDS – {SAN['ustepy_suche']} ustępów suchych"
      f" (≤ 3 × 3 {ok('D2', 'ustępy suche ≤ 3:1', SAN['ustepy_suche'] <= 3 * SAN['miski_ustepowe'])}); kabiny ≥ 0,9 m, pole 0,6 × 0,9 przed miską"
      f" (§ 8 ust. 4); kanalizacja z przepompownią ścieków na zasilaniu awaryjnym")
# ---- wentylacja 48 h (§ 8 ust. 1 pkt 3)
q_co2 = 0.020 / (0.020 - 0.00042)
q_o2 = 0.022 / (0.2095 - 0.18)
Q = 3.0 * N_MDS
P_kw = 2 * 1.5 + 1.0 * L1["I"] / 1000 * 3.0 + 3.0
E48 = P_kw * 48 + E_POS                          # v1.2b-fix: + punkt przygotowania posiłków
print(f"  § 8 ust. 1 pkt 3 (48 h; O₂ ≥ 18 %, CO₂ ≤ 2 %): minimalny strumień powietrza zewn. {max(q_co2, q_o2):.2f} m³/h/os."
      f" (CO₂ 20 l/h/os. → {q_co2:.2f}; O₂ 22 l/h/os. → {q_o2:.2f}); przyjęto 3,0 m³/h/os. (jak § 14 ust. 8 dla mds wolnostojących) → {Q:.0f} m³/h"
      f" wentylatorami garażu na szynie odbiorów krytycznych; moc ≈ {P_kw:.0f} kW (wentylacja, oświetlenie ≥ 50 lx, pompy) + posiłki"
      f" {P_POS:.1f} kW → 48 h ≈ {E48:.0f} kWh – agregat HVO (zbiornik ≥ {0.30 * E48:.0f} l) + BESS 100 kWh; bez wentylacji kubatura"
      f" {L1['V'] / N_MDS:.1f} m³/os. nie wystarcza na 48 h – wentylacja mechaniczna obowiązkowa")
# ---- konstrukcja (zał. 1)
AD = 10 + 2.5 * (8 - 2)                          # v1.2b-fix: jeden budynek (jak strefa zagruzowania), najwyższa część – wieża, szkielet, 8 kond. nadz.
I1_out = PRES["-1"]["I"].difference(BUD)
_go = [I1_out] if I1_out.geom_type == "Polygon" else list(getattr(I1_out, "geoms", []))
d_out = max((Point(x, y).distance(BUD) for g in _go if g.geom_type == "Polygon" for x, y in g.exterior.coords), default=0.0)
N_PODP = math.ceil(L1["free20"] / 2.5 ** 2 - 1e-9)
print(f"  zał. 1 (konstrukcja projektowana dla MDS): strop nad −1 – obciążenie wyjątkowe Ad = 10 + 2,5 × (8 − 2) = {AD:.1f} kN/m² na CAŁYM"
      f" stropie (pkt 1 ppkt 2 lit. a: budynek szkieletowy, 8 kond. nadz. – wieża), spójnie z wykładnią strefy zagruzowania (jeden budynek,"
      f" H wieży); wnętrze −1 poza obrysem budynku {I1_out.area:.1f} m² leży ≤ {d_out:.2f} m od ścian, czyli w strefie zagruzowania"
      f" ({ok('D2', 'pas −1 poza obrysem w strefie zagruzowania', d_out <= ZAG)}) – wartość 10 kN/m² nie ma zastosowania; nośność z systemem"
      f" podpór tymczasowych (zał. 1 pkt 3: elementy ≤ 50 kg, rozstaw ≥ 2,5 m, punkty mocowania wyznaczone w stropie): ⌈{L1['free20']:.0f} / 2,5²⌉"
      f" = {N_PODP} podpór {ok('D2', 'liczba podpór = pozycja kosztowa', N_PODP == C.N_PODP)} (magazyn MDS – regały); ściany żelbetowe ≥ 0,20"
      f" (szczelinowe 0,60) ✔; § 7 ust. 3 – oznakowanie liniami zielone/pomarańczowe na granicy 20 m")
def _kz(fr):
    return C.POZA12B[next(k for k in C.POZA12B if fr in k)][0] * C.KS_REZ / 1e6


print(f"  koszt (_v12_koszt.py POZA12B, z KS i rezerwą): szyb podwójny + tunel {_kz('szyb podwójny'):.3f} mln (pełna kwota; szyb P-I6 usunięty"
      f" z pozycji v1.1), pojemność {N_MDS} os. {_kz('pojemność'):+.3f}, podpory tymczasowe {_kz('podpór'):+.3f}, punkt posiłków"
      f" {_kz('posiłków'):+.3f}, korytarz KE-B {_kz('korytarz ewakuacyjny'):+.3f}, drzwi zewn. klatki C {_kz('klatka C'):+.3f} mln")
DATA["D2"] = {
    "podstawa_prawna": "art. 94 ust. 1 pkt 1 ustawy z 5.12.2024 o ochronie ludności i obronie cywilnej (Dz.U. 2024 poz. 1907; brzmienie"
                       " Dz.U. 2026 poz. 646, w/ż 29.05.2026); wymagania – rozp. MSWiA z 9.07.2025 (Dz.U. 2025 poz. 932) § 6–10;"
                       " budowla ochronna – art. 93, 95a (rezerwa na −2)",
    "pojemnosc_os": N_MDS, "pojemnosc_min_PU15_os": N_MIN,
    "wzor": f"PU {pl(PU)} m² / 15 m² = {pl(PU / 15)} → ≥ {N_MIN}; projektowo {N_MDS} (zapas na PU ≤ {pl(N_MDS * 15, 0)} m² po przebiegu rzutów –"
            f" reguła MDS ≥ ⌈PU z F.15.C / 15⌉); garaż: 2 × 110 = 220 – mniej; górna granica 75 % pow. netto / 1,5 = {cap94}",
    "MDS_-1_os": N_MDS,
    "ukrycie_-2": "rezerwa budowli ochronnej (art. 93; ukrycie z filtrowentylacją, projektowo do 300 os.) – pojemność i kategoria wg"
                  " postanowienia organu (art. 95a ust. 3); w reżimie MDS −2 może przyjąć dodatkowe osoby (wyjście zapasowe przez rampę"
                  " wewnętrzną do szybu SZ-MDS; w reżimie § 6 ust. 5 ≤ V/30)",
    "pojemnosc_wg_powierzchni": {k: {"wolna_m2": round(v["free20"], 1), "wys_m": v["h"], "maks_os": v["cap"], "kubatura_netto_m3": round(v["V"])}
                                 for k, v in LEVEL_MDS.items()},
    "metoda_powierzchni": "wnętrze kondygnacji (od lica ścian szczelinowych) − rdzenie, słupy, rampy − strefy pomieszczeń technicznych −"
                          " stackery (pod platformą < 2,0 m, § 9 ust. 2) − pas 20 m od bramy garażu (§ 7 ust. 3); 1,5 m²/os., 3 % osób"
                          " na wózkach × 2,0 m² (§ 9 ust. 4)",
    "wyjscia_ewakuacyjne": {"wymagane": n_ew, "zapewnione": ["klatka A", "klatka B", "klatka C", "rampa (dodatkowo)"],
                            "szerokosc_wymagana_m": round(w_req, 2), "klatki_w_swietle_m": round(kl_cl, 3),
                            "drogi_na_zewnatrz_parter": {k: " → ".join(v) for k, v in TRASY.items()},
                            "zasada": "WT § 256 ust. 6 pkt 1 – przez Halę (hol) prowadzi droga tylko z klatki A; B – korytarz ewakuacyjny KE-B"
                                      " wydzielony jak klatka do drzwi w elewacji ogrodowej; C – drzwi zewnętrzne od dziedzińca"
                                      " (rozp. 2025 poz. 932 § 6 ust. 3 pkt 1 – wyjście na zewnątrz)"},
    "wyjscia_zapasowe": {"wymagane": n_zap, "szyb": "SZ-MDS – szyb podwójny (2 przedziały = 2 wyjścia zapasowe), włazy 0,8 × 0,8 m",
                         "srodek_uv": [su, sv], "srodek_en": [round(pc.x, 3), round(pc.y, 3)], "obrys_en": ring_en(fp),
                         "tunel": {"wylot_uv": list(C.MDS_PORTAL_UV), "dlugosc_m": C.MDS_TUNEL_M, "przekroj": "2 × 0,90 × 1,50 m",
                                   "os_en": [[round(pa[0], 3), round(pa[1], 3)], [round(pc.x, 3), round(pc.y, 3)]]},
                         "odleglosc_od_scian_m": {k: round(v, 2) for k, v in d_fp.items()},
                         "strefa_zagruzowania_m": round(ZAG, 2),
                         "zastepuje": "szyb P-I6 (91,75; 32,00) – 8,42 m od segmentu, w strefie przy wykładni ścisłej"},
    "dwie_klatki_15m": f"bez znaczenia – § 6 ust. 5 nie jest stosowany (wyjścia zapasowe poza strefą); środki klatek A–B"
                       f" {kA.centroid.distance(kB.centroid):.1f} m, obudowy {kA.distance(kB):.2f} m; szyb ≥ {min(dA, dB):.1f} m od klatek",
    "sanitariaty": {"wymagane": f"{n_um} umywalek + {n_um} misek/ustępów (§ 8 ust. 2 pkt 2)", **SAN,
                    "rozmieszczenie": "sanitariaty MDS −1 30 m² za przedsionkiem dźwigów A1/A2 (3 miski w tym WC dostępne, umywalka"
                                      f" zbiorcza 8 st.) i obok punkt przygotowania posiłków 6 m², magazyn MDS 20 m² ({SAN['ustepy_suche']}"
                                      " ustępów suchych, podpory tymczasowe stropu na regałach), pralnia MDS 10 m² przy centrali S, porządkowe"
                                      " 8 m² w M1; −2: WC ukrycia 15 m²"},
    "posilki_par8_ust2_pkt3": f"punkt przygotowania posiłków MDS 6 m² obok sanitariatów (pn. od trzonu A, za przedsionkiem dźwigów): zlewozmywak"
                              f" (woda pitna, kanalizacja z przepompownią), 2 płyty indukcyjne 3,5 kW, warnik 20 l, chłodziarka, blat; zasilanie"
                              f" z szyny odbiorów krytycznych ≈ {P_POS:.1f} kW, {E_POS:.0f} kWh w 48 h",
    "wentylacja": {"min_m3_h_os": round(max(q_co2, q_o2), 2), "przyjeto_m3_h_os": 3.0, "strumien_m3_h": round(Q),
                   "zasilanie": "szyna odbiorów krytycznych: agregat HVO + BESS 100 kWh; 48 h",
                   "energia_48h_kWh": round(E48), "w_tym_posilki_kWh": round(E_POS)},
    "instalacje_par8": "§ 8 ust. 1: woda pitna (przyłącza w sanitariatach i punkcie posiłków), ścieki (przepompownia), wentylacja 48 h,"
                       " energia, oświetlenie ≥ 50 lx, ogrzewanie (przyłącza), odwodnienie (pompownia), odbiór radia (antena/DAS);"
                       " § 8 ust. 2: kanalizacja, sanitariaty (8 + 8), urządzenia do przygotowywania posiłków (punkt 6 m²), odcięcie"
                       " prądu i wody przy wejściu instalacji do MDS; bez instalacji gazowej",
    "konstrukcja_zal1": f"Ad = {AD:.0f} kN/m² na całym stropie nad −1, także w pasie pod dziedzińcem (zał. 1 pkt 1 ppkt 2 lit. a: szkielet,"
                        f" 8 kond. nadz. – wieża; wykładnia jak strefa zagruzowania – jeden budynek; całe wnętrze −1 poza obrysem leży"
                        f" ≤ {d_out:.2f} m od ścian, w strefie zagruzowania) – nośność z systemem podpór tymczasowych: {N_PODP} podpór"
                        " aluminiowych ≤ 50 kg w rozstawie 2,5 m, punkty mocowania wyznaczone w stropie i posadzce, przechowywane"
                        " w magazynie MDS",
    "podpory_tymczasowe_szt": N_PODP,
    "oznakowanie": "§ 7 ust. 3 – część dla osób ≥ 20 m od bramy, linie 0,08–0,10 m zielona / pomarańczowa; znak OC i napis"
                   " „MIEJSCE DORAŹNEGO SCHRONIENIA” (§ 10 pkt 6)",
    "koszt": f"_v12_koszt.py POZA12B: szyb SZ-MDS + tunel (pełna kwota), pojemność {N_MDS}, podpory tymczasowe, punkt posiłków, korytarz KE-B,"
             " drzwi zewnętrzne klatki C",
    "dowod": "_v12b_decyzje.py [D2]",
}

# ================================================================================================ [D3]
hr("[D3] Hala Obywatelska – oś przekątna Brama Mostowa → drzwi ogrodowe; strefa wolna ≥ 6,30 m (wielokąt), drzwi w osi")
AX_OD_EN = (101.863, 71.566)            # drzwi w łuku Bramy Mostowej (linia szklenia R 11,0) – v1.0/v1.1, bez zmian
AX_LICO_EN = (84.321, 43.124)           # przecięcie osi z licem zewn. ściany pd. wieży (v 0,00) – v1.1 („do”)
SZER = 6.30
M_uv = en2uv_(*AX_OD_EN)
G0 = en2uv_(*AX_LICO_EN)
dvec = (M_uv[0] - G0[0], M_uv[1] - G0[1])
L_ax = math.hypot(*dvec)
d = (dvec[0] / L_ax, dvec[1] / L_ax)
nrm = (-d[1], d[0])                      # + = strona NW (trzon A), − = strona SE (trzon B)


def s_of(p):
    return (p[0] - G0[0]) * nrm[0] + (p[1] - G0[1]) * nrm[1]


def u_at(v):
    return G0[0] + (v - G0[1]) * d[0] / d[1]


az = math.degrees(math.atan2(AX_LICO_EN[0] - AX_OD_EN[0], AX_LICO_EN[1] - AX_OD_EN[1])) % 360
rM = math.hypot(M_uv[0] - 26.0, M_uv[1] - 15.7)
print(f"  oś: drzwi w łuku uv ({M_uv[0]:.2f}; {M_uv[1]:.2f}) (R {rM:.2f} od środka łuku – linia szklenia R 11,0 ✔) → lico pd. uv"
      f" ({G0[0]:.2f}; {G0[1]:.2f}); azymut {az:.1f}°; kierunek w uv {math.degrees(math.atan2(d[1], d[0])):.1f}° (oś promieniowa łuku)")
ok("D3", "drzwi Bramy na łuku R 11", abs(rM - 11.0) < 0.05)
WN_D = float(K0["cofniecia_wneki"]["wneka_wejscia_ogrodowego"]["glebokosc_m"])
WN_W = 2.80
V_DRZWI = WN_D                          # płaszczyzna drzwi = tył wnęki (lico zewn.), ściana 0,30
uG = u_at(V_DRZWI)
WNEKA = box(uG - WN_W / 2, 0.0, uG + WN_W / 2, V_DRZWI + 0.30)
print(f"  wnęka v1.1 „pd. wieży, u 8,6–11,4”: oś przecina tył wnęki (v {V_DRZWI:.2f}) w u {uG:.2f} – POZA wnęką (drzwi nie mogą leżeć w osi)"
      f" → wnęka przesunięta: u {uG - WN_W / 2:.2f}–{uG + WN_W / 2:.2f} (szer. {WN_W:.2f}, głęb. {WN_D:.2f}); drzwi ogrodowe 2 × 0,90 m"
      f" (1,80 w świetle) z osią w u {uG:.2f} na v {V_DRZWI:.2f} ✔ – zmiana geometrii zewnętrznej (agent 3D, elewacja S)")
INNER_P = (box(0.5, 0.5, 39.5, 29.2)
           .difference(box(26.0, 15.7, 40.0, 30.0).difference(Point(26.0, 15.7).buffer(11.0, resolution=256)))
           .difference(box(13.5, 26.70, 26.0, 29.2))
           .difference(WNEKA))
LINE = LineString([(G0[0] - 3 * d[0], G0[1] - 3 * d[1]), (M_uv[0] + 3 * d[0], M_uv[1] + 3 * d[1])])
STRIP = LINE.buffer(SZER / 2, cap_style=2)
Zr = STRIP.intersection(INNER_P)
mid = Point((G0[0] + M_uv[0]) / 2, (G0[1] + M_uv[1]) / 2)
ZONE = next(g for g in ([Zr] if Zr.geom_type == "Polygon" else list(Zr.geoms)) if g.distance(mid) < 1e-6)
ZONE = ZONE.simplify(0.002)
Z10 = ZONE.buffer(0.10, join_style=2)
t_door = (uG - G0[0]) * d[0] + (V_DRZWI + 0.30 - G0[1]) * d[1]
t_arc = L_ax
widths = []
for i in range(0, 201):
    t = t_door + 3.3 + (t_arc - 3.3 - t_door - 3.3) * i / 200
    c = (G0[0] + d[0] * t, G0[1] + d[1] * t)
    cut = LineString([(c[0] - nrm[0] * 4, c[1] - nrm[1] * 4), (c[0] + nrm[0] * 4, c[1] + nrm[1] * 4)]).intersection(ZONE)
    widths.append(cut.length)
print(f"  strefa wolna: pas {SZER:.2f} m (±{SZER / 2:.2f} od osi) ∩ wnętrze parteru (lico ścian, szklenie R 11 i v 26,70, wnęka) –"
      f" {ZONE.area:.1f} m², długość osi wewnątrz {t_arc - t_door:.1f} m; szerokość wolna od ścian, pomieszczeń i wyposażenia w przekrojach"
      f" poprzecznych od 3,3 m za drzwiami ogrodowymi do 3,3 m przed drzwiami w łuku: min {min(widths):.2f} m"
      f" {ok('D3', 'strefa bez przegród i wyposażenia ≥ 6,30 na całej długości', min(widths) >= SZER - 1e-6)}"
      f" (dalej strefa kończy się klinem na licu ściany pd. i na szkleniu łuku – oś trafia w środki drzwi)")
dA = LINE.distance(S2.CORE_A)
dB = LINE.distance(S2.CORE_B)
print(f"  trzony: naroże SE trzonu A (I5, v 11,85) {dA:.2f} m od osi ≥ 3,15 {ok('D3', 'trzon A poza strefą', ZONE.intersection(S2.CORE_A).area < 1e-6)}"
      f" (zapas {dA - SZER / 2:.2f}); naroże NW trzonu B {dB:.2f} m {ok('D3', 'trzon B poza strefą', ZONE.intersection(S2.CORE_B).area < 1e-6)}"
      f" (zapas {dB - SZER / 2:.2f}) – wydłużenie trzonu A w I5 nie koliduje z osią")
# ---- słupy w hali (siatka wieży; łuk – słupy promieniowe)
SW = K0["siatka"]["wieza"]
cols = []
for u_ in SW["osie_u"][1:-1]:
    for v_ in SW["osie_v"][1:-1]:
        if u_ >= 26.0 and v_ >= 15.7:
            continue
        p_ = Point(u_, v_)
        if p_.within(S2.CORE_A.buffer(0.4)) or p_.within(S2.CORE_B.buffer(0.4)):
            continue
        cols.append(("siatka", (u_, v_)))
for R_ in (7.0, 13.5):
    for th in range(0, 91, 15):
        cols.append((f"R {R_:.1f} / {th}°", (26.0 + R_ * math.cos(math.radians(th)), 15.7 + R_ * math.sin(math.radians(th)))))
R_COL = 0.225                                   # słupy w hali okrągłe Ø 0,45 m (rdzeń stalowy) – decyzja v1.2b
hit = [(n, p, s_of(p)) for n, p in cols if Point(p).buffer(R_COL).intersects(ZONE) or
       (n.startswith("R 13.5") and abs(s_of(p)) < SZER / 2 + R_COL)]
print("  słupy konstrukcyjne w pasie osi (v1.2): " + "; ".join(f"{n} ({p[0]:.2f}; {p[1]:.2f}) s = {s:+.2f}" for n, p, s in hit))
USUN = [n for n, p, s in hit if n.startswith("R 7.0") or n.startswith("R 13.5")]
ZOST = [(n, p, s) for n, p, s in hit if n == "siatka"]
for R_, th in ((7.0, 15), (7.0, 75), (13.5, 30), (13.5, 60)):
    p_ = (26.0 + R_ * math.cos(math.radians(th)), 15.7 + R_ * math.sin(math.radians(th)))
    ok("D3", f"słup R {R_} / {th}° poza strefą", abs(s_of(p_)) - R_COL >= SZER / 2 - 1e-6)
print(f"  DECYZJA (konstrukcja): w łuku bez słupów R 7,0 na 30°, 45°, 60° (przęsło 15°–75°: cięciwa {2 * 7.0 * math.sin(math.radians(30)):.2f} m"
      f" ≤ 8,70 – płyta sprężona z pasmem nad osią) i bez słupa R 13,5 na 45° (przęsło Bramy 30°–60°: {2 * 13.5 * math.sin(math.radians(15)):.2f} m,"
      f" belka nadproża w stropie nad P) – na wszystkich kondygnacjach; słupy R 7,0 / 15° i 75° oraz R 13,5 / 30° i 60° poza strefą ✔")
free_band = min(abs(s) - R_COL for n, p, s in ZOST) if ZOST else SZER / 2
print(f"  pozostają w strefie 2 słupy siatki (strona NW): " + "; ".join(f"({p[0]:.2f}; {p[1]:.2f}) s = {s:+.2f}" for n, p, s in ZOST)
      + f" – usunięcie wymagałoby transferu nad parterem (obciążenie z 7 stropów, rozpiętość 16,2 m) albo przesunięcia słupów do garażu"
      f" (droga A1 i rząd R2 – utrata stanowisk) → pozostają jako słupy okrągłe Ø 0,45 m; pas całkowicie wolny (bez słupów) od krawędzi SE"
      f" do pierwszego słupa: {SZER / 2 + free_band:.2f} m; sama oś wolna {ok('D3', 'oś bez słupów', all(abs(s) > R_COL for n, p, s in ZOST))}")
ok("D3", "pas wolny od słupów ≥ 4,0 m", SZER / 2 + free_band >= 4.0)
# v1.2b-fix: szerokość wolna Z ODJĘCIEM słupów – najdłuższy odcinek przekroju poprzecznego strefy poza słupami (przekroje co ≈ 0,06 m
# + przekroje przez środki słupów)
COLS_Z = unary_union([Point(p).buffer(R_COL, resolution=128) for n, p, s_ in ZOST]) if ZOST else Polygon()
ts = [t_door + 3.3 + (t_arc - 3.3 - t_door - 3.3) * i / 400 for i in range(401)]
ts += [(p[0] - G0[0]) * d[0] + (p[1] - G0[1]) * d[1] for n, p, s_ in ZOST]
w_free = []
for t in ts:
    c = (G0[0] + d[0] * t, G0[1] + d[1] * t)
    cut = LineString([(c[0] - nrm[0] * 4, c[1] - nrm[1] * 4), (c[0] + nrm[0] * 4, c[1] + nrm[1] * 4)]).intersection(ZONE).difference(COLS_Z)
    segs = [cut] if cut.geom_type == "LineString" else [g for g in getattr(cut, "geoms", []) if g.geom_type == "LineString"]
    w_free.append((max(g.length for g in segs), t))
W_FREE, t_min = min(w_free)
p_min = (G0[0] + d[0] * t_min, G0[1] + d[1] * t_min)
print(f"  v1.2b-fix – szerokość wolna Z ODJĘCIEM słupów (najdłuższy odcinek przekroju poprzecznego strefy poza słupami Ø {2 * R_COL:.2f}):"
      f" min {W_FREE:.3f} m w punkcie osi ({p_min[0]:.2f}; {p_min[1]:.2f}) {ok('D3', 'pas bez przeszkód (z odjęciem słupów) ≥ 4,26 m', W_FREE >= 4.26 - 1e-3)}"
      f" – WYMAGANIE (sformułowane wprost): strefa 6,30 m wolna od ścian, pomieszczeń i wyposażenia stałego, w niej 2 słupy konstrukcyjne"
      f" Ø 0,45 m po stronie NW (kolumnada), pas całkowicie wolny ≥ 4,26 m na całej długości, oś wolna; 6,30 m bez słupów wymagałoby"
      f" transferu 2 słupów nad parterem (7 stropów, ≈ 5–6 MN na słup) – odrzucone (koszt, wysokość belek w kond. 1)")
# ---- pomieszczenia v1.1 (strefy parter.wieza) wobec strefy i przykładowe obrysy v1.2b (dowód wykonalności dla przebiegu rzutów)
ZON = {z["strefa"].split(" ")[0]: z for z in K0["parter"]["wieza"] if "uv" in z}
conf = {}
for z in K0["parter"]["wieza"]:
    if "uv" in z:
        g = box(*z["uv"])
        a = g.intersection(ZONE).area
        if a > 0.005:
            conf[z["strefa"][:40]] = round(a, 2)
print(f"  kolizje stref parteru v1.1 z pasem: {conf} oraz w modelu pomieszczeń (budynek.json): PHS.04 (toalety konferencyjne na osi),"
      f" SW.06 (pokój cichy), SW.02, PR.01, PHS.02")
PROG = {"PR.01": 75, "SW.02": 30, "SW.06p": 16, "PHS.02": 24, "PHS.03": 12}
EX = {}
EX["PR.01"] = box(0.5, 0.5, 8.15, 12.3).difference(Z10)
EX["PHS.02+PHS.03"] = box(15.65, 12.05, 21.0, 20.85).difference(Z10)
EX["PHS.03"] = box(15.65, 16.85, 18.65, 20.85)
EX["SW.02"] = (box(28.60, 10.05, 35.60, 19.00).difference(box(33.25, 7.0, 40.0, 15.85))
               .difference(Z10).intersection(INNER_P))
EX["SW.06p"] = box(8.25, 7.30, 12.55, 11.75).difference(Z10)        # v1.2b-fix: pokój cichy po stronie NW osi, pod trzonem A (bez okna)
for k, g in EX.items():
    g = g if g.geom_type == "Polygon" else max(g.geoms, key=lambda x: x.area)
    EX[k] = g
ok("D3", "przykładowe obrysy poza strefą", all(g.intersection(ZONE).area < 1e-6 for g in EX.values()))
ok("D3", "przykładowe obrysy poza trzonami", all(g.intersection(S2.CORE_A.union(S2.CORE_B)).area < 1e-6 for g in EX.values()))
a_wc = EX["PHS.02+PHS.03"].area - EX["PHS.03"].area - 0.10 * 5.35
print(f"  przykłady (wykonalność, nie narzucony podział): rowerownia PR.01 {EX['PR.01'].area:.1f} m² (≥ 75 {ok('D3', 'PR.01', EX['PR.01'].area >= 75)};"
      f" ścięcie naroża SE przy drzwiach ogrodowych); blok WC u 15,65–21,0 × v 12,05–20,85 ze ścięciem wzdłuż strefy: komfortka PHS.03"
      f" 3,00 × 4,00 = {EX['PHS.03'].area:.1f} m² (pn., ≤ 20 m od wejścia) + toalety PHS.02 {a_wc:.1f} m² (≥ 24 {ok('D3', 'PHS.02', a_wc >= 24)});"
      f" kancelaria SW.02 {EX['SW.02'].area:.1f} m² (≥ 30 {ok('D3', 'SW.02', EX['SW.02'].area >= 30)}; ścięta wzdłuż strefy – lada niska"
      f" na ukosie od osi, poszerzona ku łukowi nad DK II; drzwi przedsionka B (u 27,2–28,4) i hol P2 wolne); pokój cichy {EX['SW.06p'].area:.1f} m²"
      f" (≥ 16 {ok('D3', 'pokój cichy', EX['SW.06p'].area >= 16)}; v1.2b-fix: po stronie NW osi pod trzonem A u 8,25–12,55 × v 7,30–11,75 –"
      f" pas przy elewacji ogrodowej obok trzonu B zajmuje korytarz ewakuacyjny klatki B)")
# ---- v1.2b-fix: korytarz ewakuacyjny KE-B klatki B (WT § 256 ust. 6) – geometria wobec strefy, pomieszczeń i trzonów ([D2] TRASY)
W_EI60 = 0.15
KOR_B_SC = KOR_B.buffer(W_EI60, join_style=2)
bnd = KOR_B.boundary
on_core = bnd.intersection(LineString([(24.85, 0.0), (24.85, 10.0)])).length
on_fac = bnd.intersection(LineString([(0.0, 0.50), (40.0, 0.50)])).length
L_new = bnd.length - on_core - on_fac
s_kb = max(s_of(pt) for pt in KOR_B_SC.exterior.coords)
dkl = LineString(KOR_B_DRZWI_KL)
dzw = LineString(KOR_B_DRZWI_ZEW)
print(f"  korytarz ewakuacyjny KE-B (klatka B → elewacja ogrodowa): w świetle 1,80 m – wzdłuż trzonu B u 23,05–24,85 × v 0,50–7,45 i wzdłuż"
      f" elewacji u 19,00–24,85 × v 0,50–2,30 ({KOR_B.area:.1f} m²), ściany EI 60 {W_EI60:.2f} m (nowe {L_new:.1f} m ≈ koszt {C.L_KEB:.1f} m"
      f" {ok('D3', 'ściany KE-B = pozycja kosztowa', abs(L_new - C.L_KEB) < 0.8)}); lico zewn. ścian ≥ {-s_kb:.2f} m od osi ≥ 3,25"
      f" {ok('D3', 'KE-B poza strefą wolną', not KOR_B_SC.intersects(ZONE) and -s_kb >= SZER / 2 + 0.10)}; rozłączny z pomieszczeniami"
      f" {ok('D3', 'KE-B rozłączny z pomieszczeniami', all(KOR_B_SC.intersection(g).area < 1e-6 for g in EX.values()))} i trzonem A"
      f" {ok('D3', 'KE-B poza trzonami', KOR_B.intersection(S2.CORE_A.union(S2.CORE_B)).area < 1e-6)}; w obrysie parteru"
      f" {ok('D3', 'KE-B w obrysie', KOR_B.within(INNER_P.buffer(1e-6)))}; drzwi z podestu P klatki B (v 5,75–7,35) na ścianie trzonu"
      f" {ok('D3', 'drzwi klatka B → KE-B', dkl.within(KOR_B.boundary.buffer(1e-6)))}; drzwi zewnętrzne u 19,25–20,85 w licu wewn."
      f" elewacji pd. (elewacja zewnętrzna wieży tylko u 0–21,0 – segment od u 21) {ok('D3', 'drzwi zewn. KE-B w elewacji ogrodowej', dzw.within(KOR_B.boundary.buffer(1e-6)) and KOR_B_DRZWI_ZEW[1][0] <= 21.0 - 0.10)}")
fz = next(z for z in K0["parter"]["skrzydlo"] if z["strefa"].startswith("Foyer"))
fa = Polygon(fz["en"]).area
need_f = 40 + 22 + 20 + 50
print(f"  PHS.04 (toalety strefy konferencyjnej, program 50 m², zakres 40–70) → poza Halą: blok foyer skrzydła s 39,75–50 ({fa:.1f} m² brutto,"
      f" ≈ {0.96 * fa:.0f} netto): PHS.04 ≥ 40 + szatnia SK.07 ≥ 22 + magazyn SK.05 ≥ 20 + foyer SK.06 ≥ 50 = {need_f} m²"
      f" {ok('D3', 'budżet foyer', need_f <= 0.96 * fa)} (foyer uzupełnia łącznik SW.01b 105 m² – program: „może stanowić część holu”)")
G_door_en = uv2en_(uG, V_DRZWI)
G_door_en_ = G_door_en
D3_REQ = [
    f"strefa wolna (wielokąt parter.wieza[Hala].os.strefa_wolna_uv/en, {ZONE.area:.1f} m², szer. 6,30 m) – bez ścian, przegród, pomieszczeń"
    " i wyposażenia stałego (lada informacji, tyflomapa, witryny lapidarium, siedziska poczekalni, stojaki) – ściany pomieszczeń"
    " przyległych ≥ 0,10 m poza strefą; w strefie wyłącznie 2 słupy konstrukcyjne Ø 0,45 m po stronie NW – pas całkowicie wolny"
    f" ≥ {W_FREE:.2f} m na całej długości (min_szer_bez_przeszkod_m), oś wolna",
    f"drzwi ogrodowe: środek w u {uG:.2f}, v {V_DRZWI:.2f} (tył wnęki), 2 × 0,90 m; wnęka wejścia ogrodowego u {uG - WN_W / 2:.2f}–{uG + WN_W / 2:.2f}"
    " (cofniecia_wneki.wneka_wejscia_ogrodowego)",
    "PHS.04 przenieść do bloku foyer skrzydła (s 39,75–50) – ≥ 40 m²; w wieży na osi nie może być toalet",
    "pokój cichy (w modelu SW.06) – po stronie NW osi pod trzonem A u 8,25–12,55 × v 7,30–11,75 (przyklady_uv.SW.06p, bez okna – pokój"
    " wyciszenia, światło regulowane); dojście do drzwi pd. przedsionka A (u 13,10–14,30) wolne; poczekalnia 40 m² (program SW.06)"
    " i informacja 8 m² jako strefy otwarte poza strefą wolną (lada informacji ≥ 3,25 m od osi + głębokość lady)",
    "korytarz ewakuacyjny KE-B klatki B (WT § 256 ust. 6 – przez Halę droga tylko z klatki A): w świetle 1,80 m, wzdłuż trzonu B"
    " u 23,05–24,85 × v 0,50–7,45 i wzdłuż elewacji ogrodowej u 19,00–24,85 × v 0,50–2,30 (korytarz_ewakuacyjny_B), ściany EI 60 0,15 m,"
    " drzwi z podestu P klatki B w ścianie zach. trzonu v 5,75–7,35 (1,50 m), drzwi zewnętrzne 2-skrzydłowe 1,60 m u 19,25–20,85,"
    " bez innych drzwi; nadciśnienie jak klatka; przedsionek B na P – drzwi do Hali (u 27,80) bez zmian (dostęp z Hali do klatki)",
    "kancelaria SW.02 ≥ 30 m² (program 30–45) poza strefą: ścięcie wzdłuż krawędzi strefy (lada niska na ukosie), poszerzenie ku łukowi nad"
    " DK II (v ≥ 15,85), początek u ≥ 28,60 (drzwi przedsionka B u 27,80 otwarte do holu); przykład: przyklady_uv.SW.02",
    "blok WC/komfortka u 15,65–21,0 × v 12,05–20,85 ze ścięciem wzdłuż strefy (przykład przyklady_uv.PHS.02+PHS.03); na P bez drzwi"
    " przedsionka A od wsch. (drzwi pd. do Hali)",
    "rowerownia PR.01 – ścięcie naroża SE (przy drzwiach ogrodowych) wzdłuż strefy",
    "słupy w hali: okrągłe Ø 0,45 m; w łuku bez słupów R 7,0 na 30°, 45°, 60° i bez słupa R 13,5 na 45° (Brama); w strefie dopuszczone"
    " wyłącznie słupy siatki (16,20; 8,70) i (24,30; 16,00)",
    "SW.02, SW.06/pokój cichy, PHS.02/03, PR.01, korytarz KE-B, trzony A i B – poza strefą (kontrola: pole przecięcia z wielokątem = 0)",
    "drzwi w łuku Bramy Mostowej (wyjście Hali jako drogi z klatki A – § 256 ust. 6: drzwi zewnętrzne +50 %) ≥ 2,40 m w świetle;"
    " drzwi ogrodowe 1,80 m (= 1,5 × 1,20)",
]
D3_3D = [
    "strefa wolna wg os.strefa_wolna_en – bez lady informacji, tyflomapy, witryn i siedzisk; lada informacji poza strefą (|l| ≥ 3,25 m od osi"
    " + głębokość lady, np. przy trzonie A po stronie NW), tyflomapa przy wejściu poza strefą (lub na krawędzi strefy w ścianie)",
    "słupy hali okrągłe Ø 0,45 m (nie Ø 0,56); w strefie wyłącznie słupy (16,20; 8,70) i (24,30; 16,00); w łuku bez słupów R 7,0 na 30°,"
    " 45°, 60° i bez słupa R 13,5 na 45° (podcień Bramy Mostowej – przęsło 6,99 m)",
    f"drzwi ogrodowe z JSON (os.drzwi_ogrodowe): środek uv ({uG:.2f}; {V_DRZWI:.2f}) = en ({G_door_en_[0]:.2f}; {G_door_en_[1]:.2f}), 1,80 m"
    f" (2 × 0,90), we wnęce u {uG - WN_W / 2:.2f}–{uG + WN_W / 2:.2f} (cofniecia_wneki) – stała ZALOZENIA wejscie_ogrodowe_hali_S ="
    f" ({uG - 0.90:.2f}; {uG + 0.90:.2f}) zamiast (15,9; 18,3); ścieżka dotykowa po osi bez skrętu",
    "nowe drzwi zewnętrzne (geometria elewacji): wieża, elewacja ogrodowa (pd.) u 19,25–20,85 – wyjście korytarza KE-B klatki B (2 skrzydła"
    " 1,60 m, wys. 2,40 m, w osi płyciny przy narożu z segmentem); skrzydło, elewacja od dziedzińca s 4,70–6,50 – wyjście klatki C (2 skrzydła"
    " 1,80 m) – elewacje.drzwi_ewakuacyjne_v12b_fix",
]
for r_ in D3_REQ:
    print("   – " + r_)
DATA["D3"] = {
    "os": {"od": list(AX_OD_EN), "do": [round(G_door_en[0], 3), round(G_door_en[1], 3)], "lico_pd_en": list(AX_LICO_EN),
           "od_uv": [round(M_uv[0], 3), round(M_uv[1], 3)], "do_uv": [round(uG, 3), V_DRZWI], "azymut_deg": round(az, 1),
           "dl_m": round(math.hypot(G_door_en[0] - AX_OD_EN[0], G_door_en[1] - AX_OD_EN[1]), 1), "min_szer_m": SZER,
           "min_szer_bez_przeszkod_m": round(W_FREE, 2),
           "wymaganie": f"strefa {SZER:.2f} m wolna od ścian, pomieszczeń i wyposażenia stałego; w strefie 2 słupy konstrukcyjne Ø 0,45 m"
                        f" (strona NW); pas całkowicie wolny (z odjęciem słupów) ≥ {W_FREE:.2f} m na całej długości; oś wolna (v1.2b-fix –"
                        " wymaganie „6,30 m wolnej szerokości” dotyczy przegród i wyposażenia, nie słupów)",
           "strefa_wolna_uv": ring_uv(ZONE), "strefa_wolna_en": ring_en_from_uv(ZONE), "strefa_wolna_m2": round(ZONE.area, 1),
           "drzwi_ogrodowe": {"srodek_uv": [round(uG, 3), V_DRZWI], "srodek_en": [round(G_door_en[0], 3), round(G_door_en[1], 3)],
                              "szerokosc_m": 1.80, "skrzydla": "2 × 0,90 m", "plaszczyzna": "tył wnęki (lico zewn. v 1,50; ściana 0,30)"},
           "trzony_od_osi_m": {"A": round(dA, 2), "B": round(dB, 2)},
           "slupy_w_strefie": [{"uv": [p[0], p[1]], "s_m": round(s, 2), "przekroj": "okrągły Ø 0,45 m"} for n, p, s in ZOST],
           "pas_bez_slupow_m": round(SZER / 2 + free_band, 2),
           "slupy_usuniete": USUN,
           "wymagania_dla_rzutow": D3_REQ,
           "wymagania_dla_3D": D3_3D,
           "przyklady_uv": {k: ring_uv(g) for k, g in EX.items()},
           "przyklady_m2": {k: round(g.area, 1) for k, g in EX.items()},
           "dowod": "_v12b_decyzje.py [D3]"},
    "wneka": {"elewacja": f"pd. wieży, u {pl(uG - WN_W / 2)}–{pl(uG + WN_W / 2)}", "glebokosc_m": WN_D,
              "drzwi_uv": [round(uG, 3), V_DRZWI], "uwaga": f"v1.2b: przesunięta z u 8,6–11,4 o +{uG - 10.0:.2f} m – drzwi ogrodowe w osi Hali"},
    "korytarz_B": {"opis": "korytarz ewakuacyjny KE-B klatki B (WT § 256 ust. 6 pkt 1 – przez Halę droga tylko z klatki A), w świetle 1,80 m,"
                           " ściany EI 60 0,15 m, nadciśnienie jak klatka, bez innych drzwi",
                   "obrys_uv": ring_uv(KOR_B), "obrys_en": ring_en_from_uv(KOR_B), "pow_m2": round(KOR_B.area, 1),
                   "drzwi_z_klatki_uv": [list(x) for x in KOR_B_DRZWI_KL], "drzwi_z_klatki_szer_m": 1.50,
                   "drzwi_zewnetrzne_uv": [list(x) for x in KOR_B_DRZWI_ZEW],
                   "drzwi_zewnetrzne_en": [[round(c, 3) for c in uv2en_(x[0], 0.0)] for x in KOR_B_DRZWI_ZEW], "drzwi_zewnetrzne_szer_m": 1.60,
                   "odleglosc_od_osi_m": round(-s_kb, 2), "dowod": "_v12b_decyzje.py [D2] (TRASY), [D3]"},
    "luk_v12b": "słupy promieniowe co 15° na R 13,5 i R 7,0 z wyjątkiem: R 7,0 – 30°, 45°, 60° (przęsło 7,0 m nad osią Hali), R 13,5 –"
                " 45° (przęsło Bramy Mostowej 6,99 m); w hali parteru słupy okrągłe Ø 0,45 m",
}

# ================================================================================================ [D4]
hr("[D4] Sala Sejmiku – galeria 20 + 3 wobec programu (M.01 PU s. 6)")
sala = K0["kondygnacja_sejmiku"]["sala"]
poza = sala["miejsca_poza_rzedami"]
plyta = sala["stale_stanowiska"] + sum(poza.values())
razem = plyta + sala["galeria"] + sala["galeria_wozki"]
print("  M.01 s. 6 (dosłownie): „Sala obrad Sejmiku powinna mieć charakter reprezentacyjny i być przeznaczona dla maksymalnie 100 osób”;"
      " strefy: radni, prezydium, zarząd, zaproszeni goście, przedstawiciele mediów, obsługa techniczna i kancelaryjna (w tym tłumacze"
      " PJM); „Część przeznaczona dla publiczności powinna posiadać oddzielne wejście i może być wizualnie odseparowana” – program NIE"
      " podaje liczby miejsc publiczności, mediów ani gości („25 publiczność” w program.md to podział zaproponowany przez zespół – wniosek).")
print(f"  projekt: stanowiska stałe {sala['stale_stanowiska']} (w tym 4 dla wózków; wymagane {sala['wymagane_stanowiska']}) + prezydium"
      f" {poza['prezydium']} + goście {poza['gosc']} + media {poza['media']} + obsługa {poza['obsluga']} + PJM {poza['PJM']} = płyta {plyta};"
      f" galeria {sala['galeria']} + {sala['galeria_wozki']} miejsca dla wózków → razem {razem}"
      f" {ok('D4', 'sala ≤ 100 os.', razem <= 100)}; stanowiska ≥ 44 {ok('D4', 'stanowiska', sala['stale_stanowiska'] >= sala['wymagane_stanowiska'])};"
      f" M.13 s. 218: ≥ 3 miejsca dla wózków na 100 miejsc widowni – galeria 3 {ok('D4', 'wózki galeria', sala['galeria_wozki'] >= 3)} (+ 4 na płycie);"
      f" oddzielne wejście publiczności (P1/P2 → hol +30,90 → galeria) ✔")
print("  DECYZJA: zgodne z programem – bez zmian (więcej miejsc publiczności nie jest wymagane; przy 100 os. maksymalnie każde dodatkowe"
      " miejsce na galerii musiałoby zastąpić miejsce gościa lub mediów na płycie).")
DATA["D4"] = {"zgodnosc_programu": {
    "brzmienie": "M.01 s. 6: sala „przeznaczona dla maksymalnie 100 osób”; strefy radnych, prezydium, zarządu, gości, mediów, obsługi"
                 " (PJM); publiczność z oddzielnym wejściem, może być odseparowana – bez liczby miejsc publiczności",
    "plyta": plyta, "galeria": sala["galeria"] + sala["galeria_wozki"], "razem": razem, "maks_programu": 100,
    "wozki_galeria": sala["galeria_wozki"], "M13_s218": "≥ 3 na 100 miejsc widowni ✔",
    "wniosek": "zgodne; „25 publiczność” w program.md to podział proponowany przez zespół (wniosek), nie wymóg",
    "dowod": "_v12b_decyzje.py [D4]; _s2_sala.py [S1]–[S7]; _s2_geometria.py [G2]"}}

# ================================================================================================ [D5]
hr("[D5] Elewacja segmentu od dziedzińca (lico S-W, elewacja Sg) – otwory dla przebiegu rzutów")
P3, P0 = K0["bryly"][2]["obrys_ccw"][3], K0["bryly"][2]["obrys_ccw"][0]      # (95,02; 45,681) przy wieży → (96,694; 38,813)
L_sw = math.dist(P3, P0)
OS_SK = float(K0["elewacje"]["skrzydlo"]["os_m"])
WIN = K0["elewacje"]["skrzydlo"]["okno_m"]
PAR = float(K0["elewacje"]["skrzydlo"]["parapet_m"])
m0 = (L_sw - 3 * OS_SK) / 2
cs = [m0 + (j + 0.5) * OS_SK for j in range(3)]
Zf = {k: KOND[k]["posadzka_wzgl"] for k in ("P", "1", "2", "3", "4")}


def sw_en(s):
    t = s / L_sw
    return [round(P3[0] + (P0[0] - P3[0]) * t, 3), round(P3[1] + (P0[1] - P3[1]) * t, 3)]


hw = WIN[0] / 2
OTW = {
    "P": [],
    "1": [{"typ": "żaluzja powietrza agregatu HVO (≈ 8 m²)", "s": [cs[0] - hw, cs[1] + hw], "z_nad_posadzka": [0.45, 2.95]},
          {"typ": "żaluzja wentylacji trafo (≈ 1,5 m², kanał z parteru)", "s": [cs[2] - hw, cs[2] + hw], "z_nad_posadzka": [1.70, 2.95]}],
    "2": [{"typ": "okno 1,20 × 2,35 (parapet 0,60, kwatera stała do 0,90)", "s": [c - hw, c + hw], "z_nad_posadzka": [PAR, PAR + WIN[1]]}
          for c in cs],
    "3": [{"typ": "żaluzja akustyczna dry-coolera (≈ 12 m²)", "s": [cs[0] - hw, cs[2] + hw], "z_nad_posadzka": [0.60, 2.90]}],
    "4": [{"typ": "żaluzja akustyczna dry-coolera (≈ 12 m²)", "s": [cs[0] - hw, cs[2] + hw], "z_nad_posadzka": [0.40, 2.70]}],
}
for k, lst in OTW.items():
    for o in lst:
        o["s"] = [round(x, 3) for x in o["s"]]
        o["en"] = [sw_en(o["s"][0]), sw_en(o["s"][1])]
        o["z_wzgl"] = [round(Zf[k] + o["z_nad_posadzka"][0], 2), round(Zf[k] + o["z_nad_posadzka"][1], 2)]
okna = {k: sum(1 for o in v if o["typ"].startswith("okno")) for k, v in OTW.items()}
svg_ok = os.path.exists(os.path.join(ROOT, "build", "rysunki", "elewacja_Sg_1-200.svg"))
print(f"  lico S-W segmentu: ({P3[0]}; {P3[1]}) → ({P0[0]}; {P0[1]}), {L_sw:.2f} m; 3 osie co {OS_SK:.3f} m (s = {', '.join(f'{c:.2f}' for c in cs)});"
      f" wg tools/elewacje.py segment_faces() / build/rysunki/elewacja_Sg_1-200.svg (plik: {svg_ok})")
print(f"  okna: P {okna['P']}, 1 {okna['1']}, 2 {okna['2']}, 3 {okna['3']}, 4 {okna['4']} → bez okien na P, 1, 3, 4"
      f" {ok('D5', 'bez okien P,1,3,4', all(okna[k] == 0 for k in ('P', '1', '3', '4')))}; P – ściana pełna (płyciny ślepe w osiach, cokół"
      f" granitowy 0,70, kordon); kond. 2 – 3 okna (pomieszczenia pasa zach.: falownikownia 12 m² od strony wnętrza, bez okna)")
DATA["D5"] = {"lico": "S-W segmentu (od dziedzińca)", "od_en": P3, "do_en": P0, "dlugosc_m": round(L_sw, 2),
              "osie_s_m": [round(c, 3) for c in cs], "otwory": OTW, "okna_na_kondygnacjach": okna,
              "zasada": "P, 1, 3, 4 – bez okien (P pełny; 1 – żaluzje agregatu i trafo; 3–4 – żaluzje akustyczne dry-coolera); 2 – 3 okna",
              "zrodlo": "tools/elewacje.py segment_faces() – elewacja Sg (build/rysunki/elewacja_Sg_1-200.svg)",
              "wymaganie_dla_rzutow": "budynek.json: usunąć okna z lica S-W segmentu na kond. P, 1, 3, 4 (model ma 3 okna); na kond. 1, 3, 4"
                                      " w licu S-W tylko żaluzje wg listy; kond. 2 – 3 okna w osiach s"}

# ================================================================================================ [D6]
hr("[D6] Przegrody od dziedzińca – ETICS (tynk mineralny 10 / wełna 240 λ 0,031 / żelbet 150 = 0,40 m)")
RSI, RSE = 0.13, 0.04
lay = [("tynk mineralny cienkowarstwowy", 0.010, 0.70), ("wełna mineralna (fasadowa, ETICS)", 0.240, 0.031), ("żelbet", 0.150, 2.5)]
R_T = RSI + RSE + sum(t / lam for _, t, lam in lay)
U0 = 1 / R_T
dU_f = 0.005                           # łączniki mechaniczne z zaślepką (χ ≈ 0,001 W/K × 5/m²) – PN-EN ISO 6946 zał. F
U_et = U0 + dU_f
t_et = sum(t for _, t, _ in lay)
print(f"  ETICS: {' / '.join(f'{n} {t * 1000:.0f}' for n, t, _ in lay)} = {t_et:.2f} m; R_T = {R_T:.3f} → U₀ = {U0:.3f} + ΔU_f {dU_f:.3f}"
      f" = {U_et:.3f} W/(m²K) {ok('D6', 'U ≈ 0,13', abs(U_et - 0.13) < 0.006)} ≤ 0,20 (WT 2021); reakcja na ogień A2-s1,d0 (NRO – § 216 ust. 8)")
lic_M = Polygon(K0["bryly"][1]["obrys_ccw"])
dz_len = math.dist((63.498, 6.487), (70.839, 39.838)) + math.dist((70.839, 39.838), (74.557, 40.744))
H_el = 20.85 + 0.35
a_dz = dz_len * H_el * (1 - float(K0["elewacje"]["skrzydlo"]["WWR"])) - 4.05 * 4.8
a_seg = L_sw * H_el - 3 * WIN[0] * WIN[1] - 34.0
print(f"  koszt: poz. 6.2 „Izolacja termiczna + tynk elewacyjny” (= ETICS) – fas_tynk {C.P_sel.get('fas_tynk', 0):.0f} m² × 350 zł (mid) od v1.1;"
      f" oszczędność ceramika → tynk −0,49 mln JUŻ UJĘTA (_rewizja_koszt.py, dźwignia v1.1). Kontrola powierzchni: lica dziedzińcowe skrzydła"
      f" ≈ {a_dz:.0f} m² + segmentu ≈ {a_seg:.0f} m² (pełne) = {a_dz + a_seg:.0f} m² > 410 – różnica wyceniona jak ceramika (droższa) →"
      f" wycena zachowawcza, koszt bez zmian {ok('D6', 'ETICS w kosztach', C.P_sel.get('fas_tynk', 0) >= 410)}")
TRAKT = [("ściana od ulicy (ceramika 40 / pustka 40 / wełna 240 / żelbet 150)", 0.47), ("pokój", 6.08), ("ściana korytarza GK", 0.075),
         ("korytarz", 1.82), ("ściana korytarza GK", 0.075), ("pokój", 6.08), ("ściana od dziedzińca ETICS", round(t_et, 2))]
s_tr = sum(x for _, x in TRAKT)
print(f"  trakt skrzydła 15,00 = {' + '.join(f'{x:.3f}'.rstrip('0').rstrip('.') for _, x in TRAKT)} = {s_tr:.2f}"
      f" {ok('D6', 'trakt 15,00', abs(s_tr - 15.0) < 1e-6)} → korytarz 1,82 m ≥ 1,80 (M.13 s. 173; było 1,70) przy pokojach 3,95 × 6,08 = 24,02 m²"
      f" (ściany korytarza GK 75 mm – CW 50 + 2 × 12,5 z wełną, R'A1 ≥ 35 dB)")
PRZEGRODY = [
    {"przegroda": "ściana wieży (filar / płycina)", "warstwy": "granit 40 / pustka 40 / wełna 260 λ 0,033 / żelbet; płycina Al 3 / pustka 40 /"
     " wełna 260 / żelbet 200", "U": K0["elewacje"]["U_scian"]["wieza"], "ogien": "A1"},
    {"przegroda": "ściana skrzydła i segmentu od ulic", "warstwy": "ceramika ekstrudowana 40 / pustka 40 / wełna 240 λ 0,031 / żelbet 150;"
     " konsole nierdzewne punktowe (ΔU 0,020) = 0,47 m", "U": K0["elewacje"]["U_scian"]["skrzydlo_segment"], "ogien": "A1"},
    {"przegroda": "ściana skrzydła i segmentu od dziedzińca (ETICS)", "warstwy": "tynk mineralny cienkowarstwowy 10 / wełna mineralna"
     " fasadowa 240 λ 0,031 (klejona + łączniki z zaślepką) / żelbet 150 = 0,40 m", "U": round(U_et, 2), "ogien": "A2-s1,d0 (NRO)"},
]
DATA["D6"] = {"przegrody": PRZEGRODY, "U_dziedziniec_ETICS": round(U_et, 3), "trakt_skrzydla": TRAKT,
              "koszt": "bez zmian – ETICS (poz. 6.2, fas_tynk 410 m² × 350 zł) i oszczędność −0,49 mln ujęte od v1.1"}

# ================================================================================================ [D7]
hr("[D7] Wartości użyte w rysunkach – dopisane do JSON")
pk = K0["bryly"][1]["dach"]
spadek = (pk["najwyzszy_pkt_pokrycia"]["npm"] - pk["najnizszy_pkt_pokrycia"]["npm"]) / (15.0 / 2 - 0.47)
print(f"  pochwyt ochronny 1,10 m (Ø 40, stal nierdzewna, w świetle ościeży okien skrzydła; WT § 298 ust. 2); kaseta ZIP 0,18 m"
      f" (nadproże 2,95 → 3,13 m ≤ spód stropu); ΔU konsol fasady wentylowanej 0,020; strop glin zwałowych QpB 101,8–103,4 m n.p.m."
      f" (geotechnika.md; ściany szczelinowe wcięte); spadek dachu skrzydła ({pk['najwyzszy_pkt_pokrycia']['npm']} − {pk['najnizszy_pkt_pokrycia']['npm']})"
      f" / (7,50 − 0,47) = {spadek * 100:.2f} % ≈ 2,8 % {ok('D7', 'spadek 2,8 %', abs(spadek * 100 - 2.8) < 0.1)} (kalenica w osi traktu 15,00,"
      f" d = 7,50); fryz wklęsły 0,15 × 0,15 m (139,30–139,45; tło Al RAL 8019)")
DATA["D7"] = {"pochwyt_ochronny_m": 1.10, "kaseta_ZIP_m": 0.18, "dU_konsole": 0.020, "strop_glin_QpB_npm": [101.8, 103.4],
              "dach_skrzydla": {"spadek_proc": 2.8, "spadek_obliczony_proc": round(spadek * 100, 2),
                                "kalenica": "w osi traktu 15,00 m (d = 7,50)", "pokrycie_npm": [pk["najnizszy_pkt_pokrycia"]["npm"],
                                                                                         pk["najwyzszy_pkt_pokrycia"]["npm"]]},
              "fryz_wklesly": {"wysokosc_m": 0.15, "glebokosc_m": 0.15, "npm": [139.30, 139.45], "tlo": "blacha Al RAL 8019"}}

# ================================================================================================ [D8]
hr("[D8] Pas 4,6 m od bulwaru – 2 drzewa W pasie, strefy korzeniowe w systemie komór, skrzynki rozsączające")
sw_line = LineString([(96.694, 38.813), (115.979, 39.930)])             # lico pd. segmentu
STRIP46 = (OI.intersection(sw_line.buffer(4.6, single_sided=True).union(sw_line.buffer(-4.6, single_sided=True)))
           .difference(SEG_EN).difference(D102).intersection(Polygon([(96.0, 25.0), (118.0, 25.0), (118.0, 39.9), (96.0, 38.8)])))
(x0, y0), (x1, y1) = sw_line.coords
Lw = math.hypot(x1 - x0, y1 - y0)
tt = ((x1 - x0) / Lw, (y1 - y0) / Lw)
nn = (tt[1], -tt[0])                                                       # w głąb pasa (na pd.)
W46 = max(((px - x0) * nn[0] + (py - y0) * nn[1]) for px, py in STRIP46.exterior.coords)


def loc(a, b):
    return (x0 + tt[0] * a + nn[0] * b, y0 + tt[1] * a + nn[1] * b)


def rect_loc(a0, a1, b0, b1):
    return Polygon([loc(a0, b0), loc(a1, b0), loc(a1, b1), loc(a0, b1)])


A_TREES, B_TREE, RZ = (4.2, 9.2), W46 - 1.60, (3.80, 2.40)     # v1.2b-fix: pnie 1,60 m od granicy dojazdu (korona Ø 3,0 bez nawisu)
KORONA = 3.0
TREES = [loc(a, B_TREE) for a in A_TREES]
ROOT_Z = [rect_loc(a - RZ[0] / 2, a + RZ[0] / 2, W46 - 0.15 - RZ[1], W46 - 0.15) for a in A_TREES]
CRATES = STRIP46.buffer(-0.15, join_style=2)
for z_ in ROOT_Z:
    CRATES = CRATES.difference(z_.buffer(0.05, join_style=2))
CRATES = CRATES if CRATES.geom_type == "Polygon" else max(CRATES.geoms, key=lambda g: g.area)
win_ws5 = Point(110.53, 29.02)
V_cr = CRATES.area * 1.15 * 0.95
tot = CRATES.area + sum(z_.area for z_ in ROOT_Z)
print(f"  pas: {STRIP46.area:.2f} m² (szer. {W46:.2f} m, lico pd. segmentu ↔ granica dojazdu dz. 10/2); v1.1: skrzynki = pas − 0,60 m = 60,18 m²,"
      f" 2 drzewa poza pasem (PZT: (95,9; 35,6), (88,75; 35,5))")
for i, (tr, z_) in enumerate(zip(TREES, ROOT_Z), 1):
    print(f"  drzewo D{i} ({tr[0]:.2f}; {tr[1]:.2f}): {Point(tr).distance(SEG_EN):.2f} m od lica segmentu, {Point(tr).distance(D102):.2f} m od granicy"
          f" dojazdu, {Point(tr).distance(win_ws5):.1f} m od okna chronionego WS 5; strefa korzeniowa (komory/grunt strukturalny) {RZ[0]:.2f} × {RZ[1]:.2f}"
          f" = {z_.area:.2f} m² w pasie {ok('D8', f'strefa D{i} w pasie', z_.within(STRIP46))}")
print(f"  skrzynki rozsączające: pas − 0,15 m − strefy korzeniowe (+0,05 geomembrana) = {CRATES.area:.2f} m² ≥ 60,2"
      f" {ok('D8', 'skrzynki ≥ 60,2', CRATES.area >= 60.2)} × 1,15 m × 0,95 = {V_cr:.1f} m³ (v1.1: 66); skrzynki + strefy = {tot:.2f}"
      f" ≤ {STRIP46.area:.2f} {ok('D8', 'w pasie', tot <= STRIP46.area)}; rozstaw drzew {math.dist(*TREES):.1f} m ≥ 4,5"
      f" {ok('D8', 'rozstaw', math.dist(*TREES) >= 4.5)}; przejście wzdłuż lica segmentu {B_TREE - 0.30:.2f} m (pnie z kratą 0,6 m)")
d_dz = min(Point(t_).distance(D102) for t_ in TREES)
print(f"  korona Ø {KORONA:.1f} m (promień {KORONA / 2:.2f}) wobec odległości pni od granicy dojazdu {d_dz:.2f} m → nawis"
      f" {max(0.0, KORONA / 2 - d_dz):.2f} m {ok('D8', 'korona bez nawisu nad dojazdem dz. 10/2', d_dz >= KORONA / 2 - 1e-6)};"
      f" pień w strefie korzeniowej {ok('D8', 'pień w strefie korzeniowej', all(Point(t_).within(z_) for t_, z_ in zip(TREES, ROOT_Z)))}")
print("  gatunek: grab pospolity 'Fastigiata' lub klon polny 'Elsrijk' (korona ≤ 3 m – bez nawisu nad dojazdem); dno skrzynek ≥ 117,45"
      " (≥ 1,0 m nad ZWG maks. 116,45); przy ścianie szczelinowej segmentu geomembrana (biała wanna projektowana na zwierciadło 119,0)")
DATA["D8"] = {"pas_en": ring_en(STRIP46), "pas_m2": round(STRIP46.area, 2),
              "drzewa": [{"id": f"D{i}", "en": [round(t[0], 2), round(t[1], 2)], "gatunek": "grab pospolity 'Fastigiata' / klon polny 'Elsrijk'",
                          "korona_m": KORONA, "od_granicy_dojazdu_m": round(Point(t).distance(D102), 2),
                          "od_lica_segmentu_m": round(Point(t).distance(SEG_EN), 2)} for i, t in enumerate(TREES, 1)],
              "strefy_korzeniowe_en": [ring_en(z_) for z_ in ROOT_Z], "strefy_korzeniowe_m2": [round(z_.area, 2) for z_ in ROOT_Z],
              "system": "komory strukturalne (np. typu soil cell) wypełnione gruntem, 1,0 m głęb., pod nawierzchnią przepuszczalną; bariera"
                        " korzeniowa wzdłuż granicy dojazdu",
              "skrzynki_en": ring_en(CRATES), "skrzynki_m2": round(CRATES.area, 2), "skrzynki_retencja_m3": round(V_cr, 1),
              "uwaga": "drzewa liczone w 26 nowych nasadzeniach (zamiast 2 „u wylotu pasa”); ława granitowa przy licu segmentu bez kolizji",
              "dowod": "_v12b_decyzje.py [D8]"}

# ================================================================================================ [D9]
hr("[D9] Odstępstwa od wytycznych M.13 (przy spełnionych WT) – usunięte i pozostałe")
with redirect_stdout(io.StringIO()):
    import _s2_ewakuacja as E                   # noqa: E402
Sx = S2.level_S()
kul_w = S2.CORE_A.bounds[1] - S2.KUL_V0
b03 = Sx["KW.S.03"].bounds
n1 = S2.KW_S03_BAY.bounds[1] - b03[1]
n2 = b03[3] - S2.KW_S03_BAY.bounds[3]
b02 = Sx["KW.S.02"].bounds
p2_stops = next(x for x in S2.LIFT_DOORS if x[0] == "P2")[3]
lob1 = RP.LOBBY_A["-1"]
lost1 = sum(1 for st in PRES["-1"]["stalls"] if st.intersection(lob1).area > 0.05)
san1 = next(v for k, v in PRES["-1"]["plant"].items() if k.startswith("sanitariaty MDS"))
fil2 = next(v for k, v in PRES["-2"]["plant"].items() if k.startswith("filtrowentylacja"))
_lob2 = RP.LOBBY_A["-2"]
RP.LOBBY_A["-2"] = rect_uv(8.30, 20.85, 15.50, 24.45)              # wariant: przedsionek −2 pogłębiony do 3,60 m (O2)
with redirect_stdout(io.StringIO()):
    _pd = RP.run(False)
RP.LOBBY_A["-2"] = _lob2
fil2_deep = next(v for k, v in _pd["-2"]["plant"].items() if k.startswith("filtrowentylacja"))[0]
ok("D9", "O2: pogłębienie przedsionka −2 nie mieści filtrowentylacji i WC ukrycia", fil2_deep < fil2[1])
USUNIETE = [
    {"id": "U1", "element": "klatki A, B, C – bieg między poręczami", "bylo": "≈ 1,46 m", "jest": f"{min(v['swiatlo'] for v in T.RES_T7.values()):.2f} m",
     "jak": "pochwyty Ø 35 mm we wnękach 0,09 m ścian (0,16 m żelbetu – REI 120) + balustrada środkowa duszy; drzwi przy spocznikach poza"
            " przedłużeniami pochwytów ([D1])", "M13": "Schody pkt 4.1 i 6; Balustrady pkt 6"},
    {"id": "U2", "element": "kuluar S przy trzonie A", "bylo": "1,75 m na 7,20 m", "jest": f"{kul_w:.2f} m",
     "jak": "ściana kuluaru od pomieszczeń pd. 0,15 m zamiast 0,20 (pomieszczenia bez zmian)", "M13": "Korytarze pkt 1 (1,8 m)"},
    {"id": "U3", "element": "łącznik KW.S.03 (S)", "bylo": "1,40 m na 8,55 m", "jest": f"1,40 m z polem mijania 1,80 × 2,00 m; przewężenia {n1:.2f} i {n2:.2f} m ≤ 5 m",
     "jak": "wnęka 0,40 × 2,00 m kosztem PHS.05a (−0,80 m² PU) przed drzwiami przedsionka A", "M13": "Korytarze pkt 2.2 i 3"},
    {"id": "U4", "element": "dojście do SWD.11b (KW.S.02)", "bylo": "1,60 m (traktowane jako odstępstwo)",
     "jest": f"1,60 × {b02[3] - b02[1]:.2f} m – przewężenie miejscowe ≤ 5 m przy kuluarze 2,25 m (pole mijania)", "jak": "wykładnia M.13 – zgodne",
     "M13": "Korytarze pkt 2.2"},
    {"id": "U5", "element": "przystanek P2 na S (hol 1,60 m)", "bylo": "przystanek służbowy S*", "jest": "P2: P, 1–6, ANT (drzwi wsch.) oraz −2, −1 (drzwi zach.) – bez S",
     "jak": "rezygnacja z przystanku S* – dostawy baru dźwigami A1/A2 (i R) do holu +30,90", "M13": "Wewn. urządzenia transportu pionowego pkt 6"},
    {"id": "U6", "element": "korytarz skrzydła (kond. 1–4)", "bylo": "1,70 m", "jest": f"1,82 m (przy trzonie C {T.KOR_C:.3f} m)",
     "jak": "ściana od dziedzińca ETICS 0,40 m (zamiast 0,47) i ściany korytarza GK 0,075 m – pokoje 24,02 m² bez zmian ([D6]); v1.2b-fix:"
            " trzon C przesunięty o +0,05 m (lico d 8,45) – bez przewężenia 1,775 m na 8,1 m",
     "M13": "Dostępność pomieszczeń (s. 173: trasa ≥ 1,8 m)"},
    {"id": "U7", "element": "stopnie galerii (6 stopni z foyer na podest +0,90)", "bylo": "1,00 m", "jest": f"1,40 m (w świetle poręczy {T.gal_cl:.2f} m)".replace(".", ","),
     "jak": "poszerzenie stopni (_s2_model.GAL_STEPS)", "M13": "Schody pkt 4.3 (≥ 1,2 m)"},
    {"id": "U8", "element": "−1 (MDS): przedsionek dźwigów A1/A2", "bylo": "7,20 × 1,75 m", "jest": "7,20 × 3,60 m (v 20,85–24,45)",
     "jak": f"sanitariaty MDS 30 m² za przedsionkiem (dostępne {san1[0]:.1f} m²), pralnia MDS 10 m² przy centrali S, porządkowe 8 m² w M1"
            f" (_rewizja_parking.py); stanowiska bez zmian (kolizja {lost1})", "M13": "Wewn. urządzenia transportu pionowego pkt 6"},
]
POZOSTALE = [
    {"id": "O1", "element": "holy windowe na kondygnacjach biurowych 1–6 (i P2 na parterze)",
     "wartosc": "A1/A2 – korytarz pn. 2,15 m; P1/P2 – korytarz wsch. 2,20 m (kond. 1–6); P2 na P – 2,20 m do ściany DK II",
     "wymaganie": "M.13 s. 170 pkt 6: ≥ 3,6 m (miejsce oczekiwania 1,6 × 1,6 + trasa 2,0 m)",
     "przepisy": "WT § 195: ≥ 1,6 m ✔; § 242 (korytarz ≥ 1,4 m) ✔",
     "uzasadnienie": "trzony A i B stoją w strefie środkowej wieży, a naprzeciw drzwi dźwigów leżą pokoje elewacyjne (głębokość 6,10 m);"
                     " hol 3,6 m zabrałby 2 jednostki elewacyjne na każdej z 6 kondygnacji (12 z 218 przy zerowej rezerwie – 187 pokoi"
                     " programu niewykonalne) albo wymagał powiększenia wieży poza obszar A MPZP. Kompensacja: na poziomach publicznych"
                     " (P – łącznik ≥ 3,6 m przed A1/A2, hol Wejścia Obywatelskiego przed P1; S i +30,90 – 3,60–3,75 m) wymóg spełniony;"
                     " na kond. 1–6 korytarz 2,15–2,20 m ≥ trasa wolna 2,0 m, pole manewrowe 1,5 × 1,5 m bez drzwi otwieranych w hol,"
                     " panele przyzywowe po obu stronach, sygnalizacja kierunku (M.13 pkt 10)"},
    {"id": "O2", "element": "garaż −1/−2: przedsionki dźwigów",
     "wartosc": "−2: A1/A2 – przedsionek ppoż. 7,20 × 1,75 m; −1 i −2: P2 (drzwi zach.) – przedsionek B 3,40 m od drzwi",
     "wymaganie": "M.13 s. 170 pkt 6: ≥ 3,6 m", "przepisy": "WT § 195 ✔; przedsionki ppoż. EI 60 z nadciśnieniem (garaż)",
     "uzasadnienie": f"na −2 (rezerwa ukrycia, bez MDS) pogłębienie do 3,6 m (+{pl((3.60 - 1.75) * 7.20)} m² = 1,85 × 7,20) odebrałoby strefie"
                     f" filtrowentylacji i WC ukrycia {pl(fil2[0] - fil2_deep, 1)} m² (dostępne {pl(fil2[0], 1)} m², wymagane {fil2[1]} – po pogłębieniu"
                     f" {pl(fil2_deep, 1)} < {fil2[1]}; _rewizja_parking.py z przedsionkiem −2 do v 24,45); w przedsionku pole manewrowe"
                     " 1,5 × 1,5 m ✔, stanowiska OzN przy trzonach A i B; przedsionek B – 3,40 m (−0,20) wynika z szerokości klatki B w obrysie"
                     " trzonu (ściana trzonu ciągła od fundamentu); na −1 (MDS) przedsionek A1/A2 3,60 m ✔ (U8)"},
]
for u_ in USUNIETE:
    print(f"  usunięte {u_['id']}: {u_['element']}: {u_['bylo']} → {u_['jest']} ({u_['jak']})")
for o_ in POZOSTALE:
    print(f"  POZOSTAJE {o_['id']}: {o_['element']}: {o_['wartosc']} – {o_['wymaganie']}; {o_['przepisy']}")
ok("D9", "kuluar ≥ 1,80", kul_w >= 1.80 - 1e-9)
ok("D9", "przewężenia KW.S.03 ≤ 5 m", n1 <= 5.0 and n2 <= 5.0)
ok("D9", "P2 bez przystanku S*", "S*" not in p2_stops)
ok("D9", "−1: przedsionek 3,60 bez utraty stanowisk", lost1 == 0)
ok("D9", "−1: sanitariaty MDS mieszczą się za przedsionkiem", san1[2])
ok("D9", "−1: pomieszczenia techniczne mieszczą się", all(v[2] for v in PRES["-1"]["plant"].values()))
DATA["D9"] = {"usuniete": USUNIETE, "pozostale": POZOSTALE,
              "R013": "uzasadnienie odstępstw w części opisowej (R-013) – teksty w meta.odstepstwa"}

# ================================================================================================ [W] zapis
hr("[W] Zapis do model/koncepcja.json (idempotentny) i walidacja")
PROTECT = ("bryly", "kondygnacje")                    # [W6] _v12_scalenie.py – bez zmian


def apply(src):
    d = copy.deepcopy(src)
    m = d["meta"]
    m["rejestr_poprawek"] = ("docs/20_koncepcja/rejestr_poprawek_v1_1.md – sekcje v1.0→v1.1, „v1.2 – scalenie S-3” i „v1.2b – decyzje po"
                             " scaleniu” (dowody: docs/20_koncepcja/_rewizja_*.py, _s2_*.py, _v12_*.py, _v12b_decyzje.py)")
    m["wersja_v12b"] = ("v1.2b – decyzje po scaleniu S-3 (17.11.2026): M.13 pkt 6 (wnęki pochwytów), MDS 592 os. na −1 z szybem SZ-MDS,"
                        " oś Hali ze strefą wolną, galeria 20 + 3 zgodna, elewacja Sg, ETICS od dziedzińca, wartości rysunkowe, drzewa w pasie"
                        " od bulwaru, odstępstwa M.13 (_v12b_decyzje.py)")
    m["wersja_v12b_fix"] = ("v1.2b-fix – poprawki po weryfikacji v1.2b (17.11.2026): wyjścia klatek na parterze (WT § 256 ust. 6 – przez Halę"
                            " tylko klatka A; korytarz KE-B klatki B; drzwi zewnętrzne klatki C), pochwyty Ø 35 we wnękach 0,09 (REI 120),"
                            " drzwi przy spocznikach poza przedłużeniami pochwytów, trzon C +0,05 m, MDS 600 os. z punktem posiłków"
                            " i Ad 25 kN/m², podpory tymczasowe w kosztach, PU z pomieszczeniami MDS podziemia, strefa Hali z 2 słupami"
                            " (pas bez przeszkód 4,26 m), pokój cichy po stronie NW, drzewa 1,60 m od dojazdu, F.14.B bez szybu P-I6")
    m["odstepstwa"] = POZOSTALE
    m["odstepstwa_usuniete_v12b"] = USUNIETE
    # [D1]
    d["rdzenie"]["klatki_M13_pkt6"] = DATA["D1"]
    # [D2]
    md = DATA["D2"]
    d["podziemie"]["MDS"] = {
        "pojemnosc_os": md["pojemnosc_os"], "pojemnosc_min_PU15_os": md["pojemnosc_min_PU15_os"], "MDS_-1_os": md["MDS_-1_os"],
        "ukrycie_-2_os": 300,
        "podstawa_prawna": md["podstawa_prawna"], "wzor": md["wzor"], "ukrycie_-2": md["ukrycie_-2"],
        "wyjscia": (f"−1: wyjścia ewakuacyjne klatki A, B, C (w świetle poręczy {md['wyjscia_ewakuacyjne']['klatki_w_swietle_m']:.2f} m;"
                    f" wymagane {md['wyjscia_ewakuacyjne']['wymagane']}, szerokość ≥ {md['wyjscia_ewakuacyjne']['szerokosc_wymagana_m']:.2f} m) +"
                    f" rampa; 2 wyjścia zapasowe – szyb podwójny SZ-MDS (en {md['wyjscia_zapasowe']['srodek_en'][0]:.2f};"
                    f" {md['wyjscia_zapasowe']['srodek_en'][1]:.2f}) z tunelem podwójnym {md['wyjscia_zapasowe']['tunel']['dlugosc_m']:.1f} m,"
                    f" poza strefą zagruzowania (≥ {md['wyjscia_zapasowe']['strefa_zagruzowania_m'] + 0.30:.2f} m od ścian); −2 (rezerwa"
                    " ukrycia): klatki A, B i rampa wewnętrzna do −1"),
        "sanitariaty": md["sanitariaty"]["rozmieszczenie"] + f" – {md['sanitariaty']['wymagane']}",
        "pojemnosc_wg_powierzchni": md["pojemnosc_wg_powierzchni"], "metoda_powierzchni": md["metoda_powierzchni"],
        "wyjscia_ewakuacyjne": md["wyjscia_ewakuacyjne"], "wyjscia_zapasowe": md["wyjscia_zapasowe"],
        "dwie_klatki_15m": md["dwie_klatki_15m"], "sanitariaty_szczegoly": md["sanitariaty"], "wentylacja": md["wentylacja"],
        "instalacje_par8": md["instalacje_par8"], "posilki_par8_ust2_pkt3": md["posilki_par8_ust2_pkt3"],
        "konstrukcja_zal1": md["konstrukcja_zal1"], "podpory_tymczasowe_szt": md["podpory_tymczasowe_szt"], "oznakowanie": md["oznakowanie"],
        "koszt": md["koszt"], "dowod": md["dowod"]}
    d["podziemie"]["technika"]["-1"] = ("warsztat PPT, odpady, magazyn MDS (ustępy suche, podpory tymczasowe stropu na regałach),"
                                        " porządkowe 8 m² (M1, przy trzonie C); sanitariaty MDS 30 m² z WC dostępnym i punkt przygotowania"
                                        " posiłków MDS 6 m² (pn. od trzonu A, za przedsionkiem dźwigów A1/A2 7,20 × 3,60 m); centrala S"
                                        " + pralnia MDS 10 m² (wsch. od trzonu B); woda szara MBR (łuk); przyłącze wody (pod rampą);"
                                        " korytarz do dźwigu T (v1.2b / v1.2b-fix)")
    d["zagospodarowanie"]["szyb_MDS"] = {"srodek_en": md["wyjscia_zapasowe"]["srodek_en"], "obrys_en": md["wyjscia_zapasowe"]["obrys_en"],
                                         "tunel_os_en": md["wyjscia_zapasowe"]["tunel"]["os_en"],
                                         "uwaga": "v1.2b: zastępuje szyb (91,75; 32,00); 2 płaskie włazy w trawniku; ogród deszczowy, ścieżki"
                                                  " i drzewa nowe ≥ 1,0 m od obrysu (drzewo (87,5; 26,75) i niecka pn. ogrodu deszczowego"
                                                  " do korekty na PZT); wykop tunelu w strefie Z3 drzewa nr 8 – ochrona"}
    # [D3]
    for z in d["parter"]["wieza"]:
        if "os" in z:
            z["os"] = DATA["D3"]["os"]
            z["korytarz_ewakuacyjny_B"] = DATA["D3"]["korytarz_B"]
            z["strefa"] = ("Hala Obywatelska (oś przekątna 211,7°, informacja 8, poczekalnia 40, lapidarium, pokój cichy 16 – po stronie NW osi"
                           " pod trzonem A; v1.2b-fix: korytarz ewakuacyjny KE-B klatki B wzdłuż trzonu B i elewacji ogrodowej)")
        if z["strefa"].startswith("Kancelaria"):
            z["obrys_uv_v12b"] = DATA["D3"]["os"]["przyklady_uv"]["SW.02"]
            z["uwaga_v12b"] = "prostokąt „uv” koliduje z osią Hali – obowiązuje obrys_uv_v12b lub inny poza strefą wolną (≥ 30 m²)"
        if z["strefa"].startswith("WC ogólnodostępne"):
            z["obrys_uv_v12b"] = DATA["D3"]["os"]["przyklady_uv"]["PHS.02+PHS.03"]
            z["uwaga_v12b"] = "blok WC + komfortka u 15,65–21,0 × v 12,05–20,85 ze ścięciem wzdłuż strefy wolnej (PHS.02 ≥ 24, PHS.03 12)"
        if z["strefa"].startswith("Rowerownia"):
            z["obrys_uv_v12b"] = DATA["D3"]["os"]["przyklady_uv"]["PR.01"]
            z["uwaga_v12b"] = "ścięcie naroża SE przy drzwiach ogrodowych (strefa wolna osi Hali)"
    cw = d["cofniecia_wneki"]["wneka_wejscia_ogrodowego"]
    cw.update(DATA["D3"]["wneka"])
    d["siatka"]["wieza"]["luk_v12b"] = DATA["D3"]["luk_v12b"]
    # [D4]
    d["kondygnacja_sejmiku"]["sala"]["zgodnosc_programu"] = DATA["D4"]["zgodnosc_programu"]
    # [D5]
    d["elewacje"]["segment_lico_SW"] = DATA["D5"]
    if "FILARY" in C.chosen:                     # v1.2b-fix: dźwignia rezerwowa FILARY wybrana przez _v12_koszt.py [K3] (zapas < 0,5 mln bez niej)
        for mt in d["elewacje"]["materialy"]:
            if mt["id"] == "G" and "v1.2b-fix" not in mt["gdzie"]:
                mt["gdzie"] = mt["gdzie"].replace("filary wieży,", "filary wieży od ulic, rzeki i łuku (v1.2b-fix: filary elewacji pd. od dziedzińca –"
                                                  " ceramika C),")
            if mt["id"] == "C" and "v1.2b-fix" not in mt["gdzie"]:
                mt["gdzie"] = mt["gdzie"] + ("; v1.2b-fix: filary elewacji pd. wieży (od dziedzińca, u 0–21) – ceramika glazurowana w tonie granitu"
                                             " (NCS S 1502-Y), ten sam podział i relief filara (dźwignia kosztowa FILARY, _v12_koszt.py [K3])")
        d["elewacje"]["wieza"]["filary_pd_material"] = ("ceramika glazurowana półmatowa w tonie granitu NCS S 1502-Y (v1.2b-fix – dźwignia FILARY:"
                                                        " granit → ceramika na elewacji pd. od dziedzińca; pozostałe elewacje wieży – granit)")
    kb = DATA["D3"]["korytarz_B"]
    d["elewacje"]["drzwi_ewakuacyjne_v12b_fix"] = [
        {"bryla": "wieża", "elewacja": "pd. (ogrodowa), u 19,25–20,85 (lico zewn. v 0,00)", "en": kb["drzwi_zewnetrzne_en"],
         "szer_m": 1.60, "wys_m": 2.40, "opis": "wyjście korytarza ewakuacyjnego KE-B klatki B – drzwi 2-skrzydłowe pełne z zamknięciem panicznym,"
                                               " w osi płyciny przy narożu z segmentem (WT § 256 ust. 6)"},
        {"bryla": "skrzydło", "elewacja": "od dziedzińca, s 4,70–6,50 (lico d 15,00)", "en": [[round(c, 3) for c in sd2en_(x, 15.0)] for x in (4.70, 6.50)],
         "szer_m": 1.80, "wys_m": 2.40, "opis": "wyjście klatki C na dziedziniec (P; rozp. 2025 poz. 932 § 6 ust. 3 pkt 1) – drzwi 2-skrzydłowe,"
                                               " w świetle ≥ 1,60 m; dalej dziedziniec → brama ogrodowa → Mazowiecka"}]
    # [D6] + [D7]
    e = d["elewacje"]
    e["przegrody"] = DATA["D6"]["przegrody"]
    e["U_scian"]["dziedziniec_ETICS"] = DATA["D6"]["U_dziedziniec_ETICS"]
    e["U_scian"]["dU_konsole"] = DATA["D7"]["dU_konsole"]
    e["U_scian"]["opis"] = ("wełna 260 λ 0,033 (wieża) / 240 λ 0,031 (skrzydło, segment), konsole nierdzewne z przekładką (ΔU 0,020);"
                            " od dziedzińca ETICS: tynk mineralny 10 / wełna 240 λ 0,031 / żelbet 150 = 0,40 m, U ≈ 0,13")
    sk = e["skrzydlo"]
    sk["pochwyt_ochronny_m"] = DATA["D7"]["pochwyt_ochronny_m"]
    sk["pochwyt_ochronny"] = "stal nierdzewna Ø 40 mm w świetle ościeży, 1,10 m nad posadzką (okna z parapetem 0,60 i kwaterą stałą do 0,90)"
    sk["kaseta_ZIP_m"] = DATA["D7"]["kaseta_ZIP_m"]
    sk["dach"] = DATA["D7"]["dach_skrzydla"]
    sk["gzyms"]["fryz_wklesly_glebokosc_m"] = DATA["D7"]["fryz_wklesly"]["glebokosc_m"]
    sk["gzyms"]["fryz_wklesly"] = "0,15 × 0,15 m (wys. × głęb.), 139,30–139,45 m n.p.m., tło z blachy Al RAL 8019"
    d["siatka"]["posadowienie"]["strop_glin_QpB_npm"] = DATA["D7"]["strop_glin_QpB_npm"]
    d["siatka"]["skrzydlo"]["trakt_m"] = ("15,00 = 0,47 + 6,08 + 0,075 + 1,82 + 0,075 + 6,08 + 0,40 (v1.2b: od dziedzińca ETICS 0,40 m,"
                                          " ściany korytarza GK 0,075 m → korytarz 1,82 m ≥ 1,80 – M.13)")
    # [D8]
    d["zagospodarowanie"]["pas_od_bulwaru"] = DATA["D8"]
    # zestawienie decyzji
    d["decyzje_v12b"] = {
        "V12B-M13": DATA["D1"]["decyzja"],
        "V12B-MDS": f"MDS {md['pojemnosc_os']} os. na −1 (art. 94); szyb podwójny SZ-MDS poza strefą zagruzowania; „2 klatki ≥ 15 m” bez znaczenia",
        "V12B-HALA": "oś Hali ze strefą wolną 6,30 m (wielokąt), drzwi ogrodowe w osi (wnęka przesunięta), PHS.04 do foyer skrzydła,"
                     " słupy R 7,0 / 30–60° i R 13,5 / 45° usunięte",
        "V12B-GAL": "galeria 20 + 3, płyta 77 – razem 100 = maksimum programu; bez zmian",
        "V12B-SG": "lico S-W segmentu: bez okien na P, 1, 3, 4; kond. 2 – 3 okna",
        "V12B-ETICS": "od dziedzińca ETICS 0,40 m, U 0,13; koszt bez zmian (ujęty od v1.1)",
        "V12B-RYS": "pochwyt 1,10; ZIP 0,18; ΔU 0,020; QpB 101,8–103,4; spadek 2,8 %; fryz 0,15 × 0,15",
        "V12B-PAS": "2 drzewa w pasie od bulwaru, strefy korzeniowe 2 × 9,12 m², skrzynki 61,2 m²",
        "V12B-ODST": "usunięte U1–U8; pozostałe O1 (holy windowe 1–6), O2 (przedsionki dźwigów w garażu −2)",
        "skrypt": "docs/20_koncepcja/_v12b_decyzje.py"}
    d["decyzje_v12b_fix"] = {
        "V12BF-EWAK": "WT § 256 ust. 6 pkt 1: przez Halę droga tylko z klatki A; klatka B – korytarz KE-B EI 60 (1,80 m) z podestu P do drzwi"
                      " 1,60 m w elewacji ogrodowej u 19,25–20,85; klatka C – drzwi zewnętrzne 1,80 m od dziedzińca s 4,70–6,50; pokój cichy"
                      " po stronie NW osi pod trzonem A",
        "V12BF-OS": f"strefa 6,30 m bez przegród i wyposażenia, 2 słupy Ø 0,45 m w strefie – pas bez przeszkód {W_FREE:.2f} m (wymaganie wprost);"
                    " wymagania dla 3D (os.wymagania_dla_3D)",
        "V12BF-REI": "pochwyty Ø 35 we wnękach 0,09 m – 0,16 m żelbetu (REI 120 przy μfi = 0,7); 1,61 m w świetle poręczy bez zmian",
        "V12BF-PRZEDL": "drzwi przy spocznikach poza przedłużeniami pochwytów 0,30 m – pasy biegów i otwory (rdzenie.klatki_M13_pkt6)",
        "V12BF-C": f"trzon C +0,05 m (d 8,45–14,55) – korytarz skrzydła przy trzonie {T.KOR_C:.3f} m ≥ 1,80",
        "V12BF-MDS": f"MDS projektowo {md['pojemnosc_os']} os. (≥ ⌈PU/15⌉ = {md['pojemnosc_min_PU15_os']}); punkt przygotowania posiłków 6 m²;"
                     f" Ad = {AD:.0f} kN/m² na całym stropie nad −1; {md['podpory_tymczasowe_szt']} podpór tymczasowych (w kosztach)",
        "V12BF-PU": f"PU {pl(PU)} m² z pomieszczeniami MDS/ukrycia podziemia (−1 {C.dPU_pod['-1']:+.2f}, −2 {C.dPU_pod['-2']:+.2f} m²)",
        "V12BF-PAS": "pnie drzew D1, D2 1,60 m od granicy dojazdu – korona Ø 3,0 m bez nawisu",
        "V12BF-KOSZT": "F.14.B: szyb SZ-MDS jedną pozycją pełnej kwoty (bez P-I6), opisy bez kodów wersji; nowe pozycje: podpory, posiłki,"
                       " KE-B, drzwi klatki C, konstrukcja Hali i łuku",
        "skrypt": "docs/20_koncepcja/_v12b_decyzje.py"}
    return d


D = apply(K0)
D2_ = apply(D)
txt = json.dumps(D, ensure_ascii=False, indent=1)
print(f"  idempotencja: apply(apply(K)) == apply(K): {ok('W', 'idempotencja', txt == json.dumps(D2_, ensure_ascii=False, indent=1))}")
for k in PROTECT:
    ok("W", f"klucz {k} bez zmian ([W6])", json.dumps(D[k], sort_keys=True) == json.dumps(K0[k], sort_keys=True))
json.loads(txt)
geoms = [Polygon(D["parter"]["wieza"][0]["os"]["strefa_wolna_en"]), Polygon(D["zagospodarowanie"]["pas_od_bulwaru"]["skrzynki_en"]),
         Polygon(D["parter"]["wieza"][0]["korytarz_ewakuacyjny_B"]["obrys_en"]),
         Polygon(D["podziemie"]["MDS"]["wyjscia_zapasowe"]["obrys_en"])] + \
        [Polygon(r_) for r_ in D["zagospodarowanie"]["pas_od_bulwaru"]["strefy_korzeniowe_en"]]
print(f"  wielokąty (strefa wolna, skrzynki, szyb, strefy korzeniowe): poprawne {ok('W', 'wielokąty poprawne', all(g.is_valid and g.area > 0 for g in geoms))};"
      f" strefa wolna w obrysie wieży {ok('W', 'strefa w wieży', geoms[0].difference(W_EN.buffer(0.01)).area < 1e-3)}")
print(f"  testy: {sum(1 for c in CHECKS if c[2])}/{len(CHECKS)} ✔")
if "--zapisz" in sys.argv:
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
    print("  zapisano", os.path.relpath(OUT, ROOT), len(txt), "B")
else:
    print("  (bez --zapisz – tylko kontrola)")
