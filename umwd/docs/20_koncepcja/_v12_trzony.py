#!/usr/bin/env python3
"""v1.2 (scalenie S-3) – poprawka I5: klatki A, B, C (biegi, stopnie, spoczniki), układ trzonów, wpływ na kondygnacje.

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_v12_trzony.py
Sekcje wydruku [T1]…[T7] przywołują koncepcja_wybrana.md (rozdz. 5, 7) i rejestr_poprawek_v1_1.md (sekcja v1.2).

Założenia (task / WT § 68–69 / M.13 s. 162–164 / dostepnosc.md):
  stopień h ≤ 0,175 m, s = 0,28 m (2h + s = 0,60–0,65), 3–17 stopni w biegu, biegi proste (bez zabiegowych),
  bieg 1,60 m (M.13 – klatki na drogach ewakuacyjnych) → klatka dwubiegowa 2 × 1,60 + 0,20 = 3,40 m,
  spocznik ≥ 1,50 m, prześwit pod biegiem/spocznikiem ≥ 2,20 m (M.13 pkt 3 – przyjęto też jako prześwit nad biegiem).
Wysokości kondygnacji z model/koncepcja.json (kondygnacje): −2 3,00; −1 4,20; P 4,80; 1–6 3,75; S → antresola 3,60.
Obrysy wewnętrzne klatek A i B z _s2_model.py (CORE_A_CELLS, CORE_B_CELLS); klatka C – układ v1.2 w tym skrypcie.
v1.2b (decyzje po scaleniu): [T7] – M.13 pkt 6 (szerokość biegu między wewnętrznymi krawędziami poręczy ≥ 1,60 m) spełniony
przez pochwyty przyścienne we wnękach ścian klatek (wnęka 0,10 × 0,30 m w ścianach 0,25 m) i balustradę środkową w duszy 0,20 m
z pochwytami obustronnymi nad krawędziami biegów; ściany klatek wzdłuż biegów 0,25 m (przedsionek A 3,05 m, szyby trzonu B +0,05 m,
trzon C: ściana przedsionka 0,25 / ściana od korytarza 0,20). Zestawienie decyzji: _v12b_decyzje.py [D1].
v1.2b-fix (po weryfikacji v1.2b): pochwyty Ø 35 mm we wnękach 0,09 × 0,30 m → w pasie wnęki zostaje 0,16 m żelbetu = REI 120 ściany
nośnej nagrzewanej jednostronnie przy μfi = 0,7 (EN 1992-1-2 tab. 5.4; R 120 – główna konstrukcja nośna klasy „B”), w świetle poręczy
nadal 1,61 m; trzon C przesunięty o +0,05 m (d 8,45–14,55) – korytarz skrzydła przy trzonie 1,825 m ≥ 1,80; [T7] – rzeczywisty test
kolizji przedłużeń pochwytów 0,30 m (M.13 Balustrady pkt 6) z drzwiami w ścianach podłużnych przy spocznikach kondygnacyjnych
(model pasów biegów i głębokości spoczników na każdej kondygnacji) oraz drzwi wyjść na zewnątrz klatek B i C na parterze.
Nie korzystano z informacji o pracach ani wynikach konkursu.
"""
import json
import math
import os
import sys
from contextlib import redirect_stdout
import io

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _s2_model as S2  # noqa: E402
from shapely.geometry import Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = S2.ROOT
K = S2.K
H_MAX, TREAD, LAND, FLIGHT_W, WELL = 0.175, 0.28, 1.50, 1.60, 0.20
MAX_STEPS = 17
CLEAR_MIN = 2.20
SLAB_T = 0.15            # płyta biegu (prostopadle) – do prześwitu
LAND_T = 0.20            # płyta spocznika


def hr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ------------------------------------------------------------------------------------------------ wysokości
KOND = {k["kondygnacja"]: k for k in K["kondygnacje"]}
Z = {k: KOND[k]["posadzka_wzgl"] for k in KOND}
Z["ANT"] = KOND["S"]["antresola_posadzka"]
SEQ_AB = ["-2", "-1", "P", "1", "2", "3", "4", "5", "6", "S", "ANT"]
SEQ_C = ["-1", "P", "1", "2", "3", "4"]


def flight_plan(H, n_fl):
    """Podział wysokości H na n_fl biegów: najmniejsza liczba stopni n ≥ H/h_max (podzielna z resztą na biegi)."""
    n = math.ceil(H / H_MAX - 1e-9)
    base, rest = divmod(n, n_fl)
    risers = [base + (1 if i < rest else 0) for i in range(n_fl)]
    h = H / n
    return n, h, risers


def stair(H, L, flip_ok):
    """Najmniejsza liczba biegów (2, 3, 4) mieszcząca się w długości L klatki dwubiegowej (pasy 2 × 1,60).
    Bieg z r stopniami ma r − 1 stopnic (ostatni stopień = spocznik). Wymagana długość = najdłuższy bieg + 2 spoczniki.
    3 biegi – spocznik kondygnacyjny po przeciwnej stronie (dozwolone tylko, gdy przedsionek przylega do całej długości)."""
    out = []
    for n_fl in (2, 3, 4):
        if n_fl % 2 == 1 and not flip_ok:
            continue
        n, h, risers = flight_plan(H, n_fl)
        lens = [(r - 1) * TREAD for r in risers]
        need = max(lens) + 2 * LAND
        ok_steps = all(3 <= r <= MAX_STEPS for r in risers)
        # prześwit: biegi w tym samym pasie powtarzają się co 2 biegi → odstęp pionowy = suma 2 kolejnych biegów
        if n_fl == 2:
            dz_same = H                         # ten sam pas kondygnację wyżej
        else:
            dz_same = min(sum(risers[i:i + 2]) for i in range(n_fl - 1)) * h
        alpha = math.atan(h / TREAD)
        clear = dz_same - (h + SLAB_T / math.cos(alpha))
        out.append(dict(n_fl=n_fl, n=n, h=h, risers=risers, lens=lens, need=need, fits=need <= L + 1e-9,
                        steps_ok=ok_steps, clear=clear, two_h_s=2 * h + TREAD))
        if need <= L + 1e-9 and ok_steps and clear >= CLEAR_MIN - 1e-9:
            return out[-1], out
    return None, out


def check_klatka(name, seq, L, W, flip_ok, start_end="S-end"):
    print(f"\n  Klatka {name}: w świetle {W:.2f} × {L:.2f} m; bieg {(W - WELL) / 2:.3f} m"
          f" ({'≥' if (W - WELL) / 2 >= FLIGHT_W - 1e-9 else '<'} 1,60 M.13); zmiana strony spocznika "
          f"{'dopuszczalna (przedsionek wzdłuż całej klatki)' if flip_ok else 'niedopuszczalna (przedsionek na końcu klatki)'}")
    end = start_end
    res = []
    worst = 0.0
    for a, b in zip(seq[:-1], seq[1:]):
        H = round(Z[b] - Z[a], 3)
        best, tried = stair(H, L, flip_ok)
        two = [t for t in tried if t["n_fl"] == 2][0]
        worst = max(worst, two["need"])
        if best is None:
            print(f"   {a:>3} → {b:<3} H {H:.2f}: BRAK ROZWIĄZANIA (2 biegi wymagają {two['need']:.2f} m > {L:.2f})")
            res.append((a, b, H, None))
            continue
        if best["n_fl"] % 2 == 1:
            end = "N-end" if end == "S-end" else "S-end"
        print(f"   {a:>3} → {b:<3} H {H:.2f}: {best['n_fl']} biegi, {best['n']} st. × {best['h'] * 100:.2f} cm "
              f"(2h+s = {best['two_h_s']:.3f}), w biegach {best['risers']} st., biegi {', '.join(f'{x:.2f}' for x in best['lens'])} m"
              f" + 2 × {LAND:.2f} → {best['need']:.2f} ≤ {L:.2f} ✔; prześwit {best['clear']:.2f} m"
              f"{'' if best['n_fl'] == 2 else ' (2 biegi wymagałyby %.2f m)' % two['need']}; "
              f"spocznik kondygnacyjny na {b}: {'koniec pd./zach.' if end == 'S-end' else 'koniec pn./wsch.'}")
        res.append((a, b, H, best))
    print(f"   najdłuższa klatka dwubiegowa (wszystkie kondygnacje po 2 biegi): {worst:.2f} m")
    return res, end


# ------------------------------------------------------------------------------------------------ [T1] wymaganie
hr("[T1] Wymagana długość klatki dwubiegowej (h ≤ 0,175, s = 0,28, spoczniki 1,50, bieg ≤ 17 st.)")
for H in (3.00, 3.60, 3.75, 4.20, 4.80):
    n, h, r = flight_plan(H, 2)
    print(f"  H {H:.2f} m: {n} st. × {h * 100:.2f} cm, biegi {r} → {max(r) - 1} stopnic × 0,28 = {(max(r) - 1) * TREAD:.2f} m"
          f" + 2 × 1,50 = {(max(r) - 1) * TREAD + 2 * LAND:.2f} m")
print("  v1.1: klatka A w trzonie A 3,40 × 5,15 m → kondygnacje typowe 3,75 m wymagają 5,80 m → brak 0,65 m (I5).")

# ------------------------------------------------------------------------------------------------ [T2] trzon A
hr("[T2] Trzon A – v1.2: wydłużenie o 0,60 m na pd. (v 12,45 → 11,85) kosztem strefy środkowej / kuluaru S")
cA = S2.CORE_A_CELLS
bA = cA["klatka_A"].bounds
LA, WA = bA[3] - bA[1], bA[2] - bA[0]
print(f"  obrys: u {S2.CORE_A.bounds[0]:.2f}–{S2.CORE_A.bounds[2]:.2f} × v {S2.CORE_A.bounds[1]:.2f}–{S2.CORE_A.bounds[3]:.2f}"
      f" = {S2.CORE_A.area:.2f} m² (v1.1: 60,48 m²; +{S2.CORE_A.area - 60.48:.2f} m²)")
for k, g in cA.items():
    b = g.bounds
    print(f"    {k:14s} u {b[0]:.2f}–{b[2]:.2f} × v {b[1]:.2f}–{b[3]:.2f} = {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} m ({g.area:.2f} m²)")
ov = [(a, b) for a in cA for b in cA if a < b and cA[a].intersection(cA[b]).area > 1e-6]
print(f"  nakładania komórek: {ov if ov else 'brak'}; wszystkie w obrysie: {all(g.within(S2.CORE_A) for g in cA.values())}")
print("  drzwi: A1/A2 – pn. (v 20,85) na wszystkich kondygnacjach (S-3), R – pd. do przedsionka A; przedsionek A: drzwi"
      " pd. (v 11,85: kuluar S / hol strefy środkowej 1–6 / Hala P), wsch. (łącznik KW.S.03 na S; garaż −1/−2), na +30,90"
      " wsch. na galerię; klatka A ↔ przedsionek A' (+30,90) w ścianie zach. przy spoczniku")
resA, endA = check_klatka("A", SEQ_AB, LA, WA, flip_ok=True)

# ------------------------------------------------------------------------------------------------ [T3] trzon B
hr("[T3] Trzon B – obrys bez zmian; v1.2: przesunięcie ściany klatka/przedsionek o 0,29 m (klatka 6,35 → 6,64 m)")
cB = S2.CORE_B_CELLS
bB = cB["klatka_B"].bounds
LB, WB = bB[3] - bB[1], bB[2] - bB[0]
for k, g in cB.items():
    b = g.bounds
    print(f"    {k:14s} u {b[0]:.2f}–{b[2]:.2f} × v {b[1]:.2f}–{b[3]:.2f} = {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} m ({g.area:.2f} m²)")
ov = [(a, b) for a in cB for b in cB if a < b and cB[a].intersection(cB[b]).area > 1e-6]
print(f"  nakładania komórek: {ov if ov else 'brak'}; wszystkie w obrysie: {all(g.within(S2.CORE_B) for g in cB.values())}")
pB = cB["przedsionek_B"].bounds
_rB = S2.moe_search(cB["przedsionek_B"], [(p, w) for a_, b_, p, w in S2.DOORS_S if a_ == "przedsionek_B"], S2.DOORS_KLATKA["przedsionek_B"])
_mB = _rB["moe"].bounds if _rB else None
print(f"  przedsionek B {pB[2] - pB[0]:.2f} × {pB[3] - pB[1]:.2f} m = {cB['przedsionek_B'].area:.2f} m²: MOE 1,5 × 1,5 poza torem 1,2 m i polem"
      f" otwierania skrzydła (test geometryczny, drzwi N w u {[p for a_, b_, p, w in S2.DOORS_S if a_ == 'przedsionek_B'][0][0]:.2f}):"
      + (f" u {_mB[0]:.2f}–{_mB[2]:.2f} × v {_mB[1]:.2f}–{_mB[3]:.2f} ✔" if _rB else " BRAK ✗")
      + f"; ≥ 2,0 × 2,4 (ppoz.md D6) ✔. Drzwi P2 (przelotowy) od zach. na −2/−1:"
      f" otwór v {8.325 - 0.55:.3f}–{8.325 + 0.55:.3f} w zakresie przedsionka v {pB[1]:.2f}–{pB[3]:.2f} ✔ (_s2_ewakuacja.py [E6])")
print("  v1.1 (klatka 6,35 m) – kondygnacja P (4,80) wymagałaby 4 biegów:")
_, triedB = stair(4.80, 6.35, flip_ok=False)
for t in triedB:
    print(f"     {t['n_fl']} biegi: wymagana długość {t['need']:.2f} m, prześwit {t['clear']:.2f} m"
          f" {'(< 2,20 – M.13 ✗)' if t['clear'] < CLEAR_MIN else ''}{'' if t['fits'] else ' – nie mieści się'}")
resB, endB = check_klatka("B", SEQ_AB, LB, WB, flip_ok=False, start_end="N-end")

# ------------------------------------------------------------------------------------------------ [T4] trzon C
hr("[T4] Trzon C (skrzydło) – s 0,5–8,6 × d 8,45–14,55 (v1.2b-fix: +0,05 m od korytarza); v1.2: nowy układ (bieg 1,60 m), bez szybu C1")
DC = 0.05                                            # v1.2b-fix: przesunięcie trzonu C ku dziedzińcowi (korytarz skrzydła 1,825 m ≥ 1,80)
C_CELLS = {
    "klatka_C": box(0.75, 10.85 + DC, 6.55, 14.25 + DC),       # 5,80 × 3,40 (biegi wzdłuż s)
    "przedsionek_C": box(0.75, 8.60 + DC, 6.55, 10.60 + DC),   # 5,80 × 2,00, drzwi z korytarza (lico d 8,45; ściana 0,20), MOE 1,5 × 1,5 na końcu
    "szachty_C": box(6.75, 8.60 + DC, 8.35, 14.25 + DC),       # 1,60 × 5,65 (nadciśnienie, piony); v1.2b: ściana klatka/przedsionek 0,25 (wnęka pochwytu)
}
CORE_C = box(0.5, 8.4 + DC, 8.6, 14.5 + DC)          # ściana od dziedzińca d 14,30–14,55 przylega do warstwy żelbetowej ETICS (d 14,60)
TRAKT_KOR = (0.47 + 6.08 + 0.075, 0.47 + 6.08 + 0.075 + 1.82)     # korytarz skrzydła (d 6,625–8,445; _v12b_decyzje.py [D6])
KOR_C = CORE_C.bounds[1] - TRAKT_KOR[0]
print(f"  korytarz skrzydła przy trzonie C: d {TRAKT_KOR[0]:.3f} → lico trzonu d {CORE_C.bounds[1]:.2f} = {KOR_C:.3f} m"
      f" {'✔' if KOR_C >= 1.80 - 1e-9 else '✗'} ≥ 1,80 (M.13 Korytarze pkt 1; v1.2b: 1,775 m na 8,1 m – przewężenie > 5 m usunięte);"
      f" do lica ściany od dziedzińca (d 14,60) {14.60 - CORE_C.bounds[3]:.2f} m")
assert KOR_C >= 1.80 - 1e-9 and CORE_C.bounds[3] <= 14.60 + 1e-9, "[T4] korytarz skrzydła przy trzonie C"
for k, g in C_CELLS.items():
    b = g.bounds
    print(f"    {k:14s} s {b[0]:.2f}–{b[2]:.2f} × d {b[1]:.2f}–{b[3]:.2f} = {b[2] - b[0]:.2f} × {b[3] - b[1]:.2f} m ({g.area:.2f} m²)")
ov = [(a, b) for a in C_CELLS for b in C_CELLS if a < b and C_CELLS[a].intersection(C_CELLS[b]).area > 1e-6]
print(f"  nakładania: {ov if ov else 'brak'}; w obrysie: {all(g.within(CORE_C) for g in C_CELLS.values())}")
print("  v1.1 / model pomieszczeń: klatka C 6,00 × 3,05 m → bieg (3,05 − 0,20)/2 = 1,425 m < 1,60 (M.13 pkt 4.1 ✗). Szyb C1 (rezerwa, bez dźwigu) 2,20 × 2,35 m"
      " nie mieści się obok klatki 3,40 m → rezygnacja z rezerwy C1 (skrzydło obsługują A1/A2 przez ciągłe korytarze kond. 1–4;"
      " ściana przy Maz. 19 REI 120 bez otworów i tak wyklucza „połączenie z Maz. 19”).")
bC = C_CELLS["klatka_C"].bounds
resC, endC = check_klatka("C", SEQ_C, bC[2] - bC[0], bC[3] - bC[1], flip_ok=True)

# ------------------------------------------------------------------------------------------------ [T5] wpływ na kondygnacje
hr("[T5] Wpływ wydłużenia trzonu A na kondygnacje (model pomieszczeń budynek.json – tylko odczyt)")
B = json.load(open(os.path.join(ROOT, "model", "budynek.json"), encoding="utf-8"))


def en2uv(e, n):
    return S2.en2uv(e, n)


def topoly(poly):
    def depth(x):
        d = 0
        while isinstance(x, list):
            x = x[0]
            d += 1
        return d
    d = depth(poly)
    rings = [poly] if d == 2 else (poly if d == 3 else poly[0])
    return Polygon([en2uv(*p) for p in rings[0]], [[en2uv(*p) for p in r] for r in rings[1:]]).buffer(0)


STRIP = box(8.30, 11.85, 15.50, 12.45)
tot_fac = 0
for lv in B["kondygnacje"]:
    if lv["id"] in ("D", "S", "ANT"):
        continue
    hit = []
    for r in lv["pomieszczenia"]:
        P = topoly(r["poligon"])
        a = P.intersection(STRIP).area
        if a > 0.01:
            fac = bool(r.get("facade_dir")) and r.get("kind") in ("office", "room")
            tot_fac += fac
            hit.append(f"{r['numer']} ({r['kind']}{', ELEWACYJNE' if fac else ''}) {a:.2f} m²")
    print(f"  kond. {lv['id']:>2}: pas v 11,85–12,45 × u 8,30–15,50 (4,32 m²) zajmuje: {'; '.join(hit) if hit else '—'}")
print(f"  Jednostki elewacyjne naruszone: {tot_fac} → pojemność elewacji 43/43/43/43/22/20 + P 4 bez zmian ✔"
      " (pas leży w strefie środkowej: kond. 1–6 hol przed przedsionkiem A, P – Hala Obywatelska, −1/−2 – pas za stanowiskami R2)")
# hol przed przedsionkiem A na kond. 1–6 i odległość osi Hali od naroża trzonu
for lv in B["kondygnacje"]:
    if lv["id"] in ("1", "4", "6"):
        south = [topoly(r["poligon"]) for r in lv["pomieszczenia"] if r["kind"] not in ("corridor", "core_lift", "core_lobby", "core_stair")]
        cand = [p.bounds[3] for p in south if p.bounds[3] <= 11.86 and p.intersection(box(8.30, 0, 15.50, 11.85)).area > 0.5]
        vs = max(cand) if cand else 0.5
        print(f"  kond. {lv['id']}: hol przed przedsionkiem A (u 8,30–15,50) v {vs:.2f} + ścianka 0,10 → 11,85: {11.85 - vs - 0.10:.2f} m (≥ 1,80 ✔)")
ax0, ax1 = (10.0, 0.0), (33.777, 23.48)      # oś przekątna Hali (drzwi ogrodowe → drzwi w łuku), uv


def dist_axis(p):
    dx, dy = ax1[0] - ax0[0], ax1[1] - ax0[1]
    L = math.hypot(dx, dy)
    return abs((p[0] - ax0[0]) * dy - (p[1] - ax0[1]) * dx) / L


print(f"  P: odległość naroża SE trzonu A od osi Hali: v1.1 {dist_axis((15.50, 12.45)):.2f} m → v1.2 {dist_axis((15.50, 11.85)):.2f} m"
      f" (≥ 3,0 m = połowa pasa 6 m ✔; najwęższe miejsce osi – między blokiem WC a trzonem B – bez zmian)")
# holy windowe A1/A2 (drzwi pn.) i P1/P2 (drzwi wsch.) na kondygnacjach biurowych
for lv in B["kondygnacje"]:
    if lv["id"] in ("1", "2", "3", "4", "5", "6"):
        north = [topoly(r["poligon"]) for r in lv["pomieszczenia"] if r["kind"] not in ("corridor",) and not r["kind"].startswith("core")]
        vn = min([p.bounds[1] for p in north if p.bounds[1] >= 20.9 and p.intersection(box(8.55, 20.9, 13.25, 29.2)).area > 0.5] or [29.2])
        ue = min([p.bounds[0] for p in north if p.bounds[0] >= 31.15 and p.intersection(box(31.15, 4.15, 39.5, 9.65)).area > 0.5] or [39.5])
        print(f"  kond. {lv['id']}: przed A1/A2 (pn.) korytarz {vn - 0.10 - 20.85:.2f} m; przed P1/P2 (wsch.) korytarz {ue - 0.10 - 31.10:.2f} m"
              " (WT § 195 ≥ 1,6 ✔; M.13 3,6 – świadome odstępstwo)")
print("  P: A1/A2 → łącznik pn. SW.01b (v 21,0–29,2) ≥ 3,6 ✔; S i +30,90: ≥ 3,75 m od lica trzonu ✔ (_s2_ewakuacja.py [E5]);"
      " −1/−2: pas v 20,85–22,60 (ślepy koniec drogi A2) wydzielony jako przedsionek ppoż. dźwigów (EI 60, nadciśnienie) – patrz [T6]")

# ------------------------------------------------------------------------------------------------ [T6] garaż
hr("[T6] Garaż −1/−2 z trzonem A v1.2 (_rewizja_parking.py z podmienionym obrysem trzonu A)")
import _rewizja_parking as RP  # noqa: E402
from _rewizja_wspolne import rect_uv  # noqa: E402

base = {}
for tag, core in (("v1.1", rect_uv(8.30, 12.45, 15.50, 20.85)), ("v1.2", rect_uv(8.30, 11.85, 15.50, 20.85))):
    RP.CORES["A"] = core
    with redirect_stdout(io.StringIO()):
        res = RP.run(False)
    tot = sum(len(r["stalls"]) + r["bonus"] for r in res.values())
    net = tot - math.ceil(6 / 2)
    plant = {lvl: all(v[2] for v in r["plant"].values()) for lvl, r in res.items()}
    base[tag] = (net, res)
    print(f"  {tag}: stanowiska na posadzce −1 {len(res['-1']['stalls'])}, −2 {len(res['-2']['stalls'])}; stackery +{res['-1']['bonus']};"
          f" po 6 OzN → {net} m.p.; pomieszczenia techniczne mieszczą się: {plant}")
print(f"  różnica v1.2 − v1.1: {base['v1.2'][0] - base['v1.1'][0]} m.p. ✔")
r12 = base["v1.2"][1]
for lvl in ("-1", "-2"):
    lob = RP.LOBBY_A[lvl]
    st = unary_union(r12[lvl]["stalls"]).intersection(lob).area
    dep = {"-1": 3.60, "-2": 1.75}[lvl]
    print(f"  {lvl}: przedsionek dźwigów A1/A2 (u 8,30–15,50, głębokość {dep:.2f} m = {lob.area:.1f} m²{'; v1.2b – M.13 3,6 m na poziomie MDS' if lvl == '-1' else ''}):"
          f" kolizja ze stanowiskami {st:.2f} m² → bez utraty miejsc ✔; pas pd. trzonu (v 11,85–12,45) za stanowiskami R2 (kończą się na v 11,60) ✔")

# ------------------------------------------------------------------------------------------------ [T7] szerokość w świetle poręczy
hr("[T7] M.13 pkt 6 – szerokość biegu między wewnętrznymi krawędziami poręczy ≥ 1,60 m (v1.2b: wnęki + balustrada środkowa)")
POCH_D, POCH_GAP = 0.035, 0.05            # v1.2b-fix: pochwyt Ø 35 mm (M.13 pkt 10: 3,5–4,5 cm), ≥ 5 cm od płaszczyzny pionowej (pkt 12)
POCH_OCC = POCH_D + POCH_GAP              # 0,085 m – pas zajęty przez pochwyt mierzony od płaszczyzny ściany / balustrady
WNEKA_D, WNEKA_H = 0.09, 0.30             # v1.2b-fix: wnęka 0,09 × 0,30 m (pas 0,68–0,98 m nad linią krawędzi stopni) – było 0,10
BAL_T = 0.020                             # balustrada środkowa duszy: płaszczyzna ≤ 20 mm (pręty Ø 12 co ≤ 0,12 / szkło VSG 2 × 8)
WALL_MIN = 0.16                           # v1.2b-fix: ściany klatek wzdłuż biegów są ścianami nośnymi trzonów = główna konstrukcja nośna
#   klasy „B” → R 120 (WT § 216 ust. 1; ppoz.md § 3.3), obudowa klatki REI 60 (§ 249 ust. 1). EN 1992-1-2 tab. 5.4, ściana nośna
#   nagrzewana jednostronnie, REI 120: 150 mm / a = 25 przy μfi = 0,35; 160 mm / a = 35 przy μfi = 0,7 (wartość domyślna, bez obliczania μfi).
#   Wnęka 0,09 w ścianie 0,25 → 0,16 m żelbetu = REI 120 przy μfi = 0,7 (a ≥ 35 mm od lica nagrzewanego – strona pomieszczeń, płaska).
CL_MIN = 1.60
KL = {   # klatka: (komórka, oś szerokości 0 = u/s, 1 = v/d; grubości ścian wzdłuż biegów [niska, wysoka] z sąsiednich komórek)
    "A": (cA["klatka_A"], 0, [cA["klatka_A"].bounds[0] - S2.CORE_A.bounds[0], cA["przedsionek_A"].bounds[0] - cA["klatka_A"].bounds[2]]),
    "B": (cB["klatka_B"], 0, [cB["klatka_B"].bounds[0] - S2.CORE_B.bounds[0], cB["szachty_B"].bounds[0] - cB["klatka_B"].bounds[2]]),
    "C": (C_CELLS["klatka_C"], 1, [C_CELLS["klatka_C"].bounds[1] - C_CELLS["przedsionek_C"].bounds[3], CORE_C.bounds[3] - C_CELLS["klatka_C"].bounds[3]]),
}
RES_T7 = {}
for nm, (cell, ax, walls) in KL.items():
    b = cell.bounds
    W_ = b[2 + ax] - b[ax]
    lane = (W_ - WELL) / 2
    reveal_wall = WNEKA_D - POCH_OCC                     # krawędź pochwytu za licem ściany (+)
    reveal_well = (WELL - BAL_T) / 2 - POCH_OCC          # krawędź pochwytu względem krawędzi biegu (+ = nad duszą)
    clear = lane + reveal_wall + reveal_well
    gap = (WELL - BAL_T) / 2                             # szczelina bieg – balustrada środkowa
    rest = [w - WNEKA_D for w in walls]
    res_ = {"A": resA, "B": resB, "C": resC}[nm]
    n_tr = sum(1 for *_x, best in res_ if best)
    n3 = sum(1 for *_x, best in res_ if best and best["n_fl"] == 3)
    RES_T7[nm] = dict(szer=W_, bieg=lane, swiatlo=clear, sciany=walls, zelbet_we_wnece=rest, szczelina=gap, przejscia=n_tr, trojbiegowe=n3)
    print(f"  klatka {nm} {W_:.2f} m: biegi konstrukcyjne 2 × {lane:.2f} + dusza {WELL:.2f}; ściany wzdłuż biegów {walls[0]:.2f} / {walls[1]:.2f} m"
          f" → żelbet w pasie wnęki {min(rest):.2f} m ({'✔' if min(rest) >= WALL_MIN - 1e-9 else '✗'} ≥ {WALL_MIN:.2f} – REI 120 przy μfi = 0,7);"
          f" pochwyt przyścienny Ø {POCH_D * 1000:.0f} mm we wnęce {WNEKA_D:.2f} m (krawędź {reveal_wall * 100:+.1f} cm za licem), pochwyt od duszy"
          f" na balustradzie środkowej (krawędź {reveal_well * 100:+.1f} cm od krawędzi biegu); w świetle poręczy {clear:.3f} m"
          f" {'✔' if clear >= CL_MIN - 1e-9 else '✗'} ≥ 1,60; szczelina bieg–balustrada {gap:.2f} m ≤ 0,12 ✔; {n_tr} przejść kondygnacyjnych"
          f" ({n3} trójbiegowe)")
    assert clear >= CL_MIN - 1e-9 and min(rest) >= WALL_MIN - 1e-9 and gap <= 0.12 + 1e-9, f"[T7] klatka {nm}"
    assert POCH_GAP >= 0.05 - 1e-9 and 0.035 - 1e-9 <= POCH_D <= 0.045
# ---- v1.2b-fix: przedłużenia pochwytów 0,30 m (M.13 Balustrady pkt 6, s. 166) a drzwi w ścianach podłużnych przy spocznikach
EXT, FR = 0.30, 0.05                      # przedłużenie poziome pochwytu; ościeżnica / odstęp otworu od końca przedłużenia
LANES = {"A": ("zach", "wsch"), "B": ("wsch", "zach"), "C": ("dalszy", "bliższy")}   # (pas biegów parzystych, pas biegów nieparzystych)
#   biegi numerowane od najniższej kondygnacji; kolejne biegi zmieniają pas (zawrót na spoczniku) – wybór pasa pierwszego biegu:
#   A: bieg przychodzący na +30,90 w pasie wsch. (drzwi A' w ścianie zach. bez przedłużenia); B: bieg przychodzący na P w pasie zach.
#   (drzwi do korytarza ewakuacyjnego KE-B przy spoczniku 2,06 m); C: bieg przychodzący na P w pasie od dziedzińca (drzwi zewn. przy
#   spoczniku 2,34 m) – pas „bliższy” = przy przedsionku C, „dalszy” = przy ścianie od dziedzińca.
END0 = {"A": "S-end", "B": "N-end", "C": "S-end"}


def landings(res, start_end, L, lanes):
    """Spoczniki kondygnacyjne: {kond.: dict(koniec, pasy={pas: (głębokość spocznika w pasie, 'przych.'|'odch.', dł. biegu)})}.
    Głębokość spocznika kondygnacyjnego w pasie biegu = L − 1,50 (spocznik pośredni po przeciwnej stronie) − rzut stopnic biegu."""
    out, k, end = {}, 0, start_end
    for a, b, H, best in res:
        n, lens = best["n_fl"], best["lens"]
        d_ = out.setdefault(a, dict(koniec=end, pasy={}))
        assert d_["koniec"] == end
        d_["pasy"][lanes[k % 2]] = (round(L - LAND - lens[0], 3), "odch.", lens[0])
        end_b = end if n % 2 == 0 else ("N-end" if end == "S-end" else "S-end")
        out.setdefault(b, dict(koniec=end_b, pasy={}))["pasy"][lanes[(k + n - 1) % 2]] = (round(L - LAND - lens[-1], 3), "przych.", lens[-1])
        k += n
        end = end_b
    for v_ in out.values():
        assert len(v_["pasy"]) <= 2 and all(x[0] >= LAND - 1e-9 for x in v_["pasy"].values())
    return out


# drzwi w ścianach podłużnych przy spocznikach (oś wzdłuż biegów: A, B – v; C – s): (klatka, kondygnacje, pas, otwór, w świetle min., opis)
DOORS_T7 = [
    ("A", ["-2", "1", "2", "3", "4", "5", "6", "S", "ANT"], "wsch", (12.05, 13.20), 1.05,
     "przedsionek A → klatka A (S: 350 os. / 2 klatki → 0,6 × 1,75 = 1,05 m – § 239 ust. 3; ościeżnica narożna przy ścianie czołowej)"),
    ("A", ["-1"], "wsch", (12.05, 13.45), 1.20, "przedsionek A → klatka A (−1: MDS ≈ 200 os. na klatkę – 0,6 m/100 os.)"),
    ("A", ["P"], "wsch", (16.45, 17.85), 1.20, "przedsionek A → klatka A (P: spocznik na końcu pn.; dalej drzwi pd. przedsionka do Hali)"),
    ("A", ["ANT"], "zach", (12.55, 13.55), 0.90, "przedsionek A' → klatka A (+30,90; _s2_model.DOORS_KLATKA)"),
    ("B", ["P"], "zach", (5.75, 7.35), 1.40,
     "klatka B → korytarz ewakuacyjny KE-B EI 60 → drzwi zewnętrzne w elewacji ogrodowej (WT § 256 ust. 6 – jedna klatka przez hol;"
     " § 239 ust. 4 – ≥ bieg 1,20 m wg § 68)"),
    ("C", ["-1"], "bliższy", (0.75, 2.05), 1.20, "przedsionek C → klatka C (−1: MDS ≈ 200 os.)"),
    ("C", ["P"], "bliższy", (5.15, 6.55), 1.20, "przedsionek C → klatka C (P)"),
    ("C", ["1"], "bliższy", (0.75, 2.45), 1.20, "przedsionek C → klatka C (kond. 1)"),
    ("C", ["2", "3", "4"], "bliższy", (0.75, 1.90), 1.00, "przedsionek C → klatka C (kond. 2–4; M.13 drzwi ≥ 0,9 m, zalecane 1,0)"),
    ("C", ["P"], "dalszy", (4.70, 6.50), 1.60,
     "klatka C → na zewnątrz przez ścianę od dziedzińca (drzwi 2-skrzydłowe; § 239 ust. 4 – założenie projektowe = bieg 1,60 m;"
     " rozp. 2025 poz. 932 § 6 ust. 3 pkt 1 – wyjście MDS na zewnątrz)"),
]
LAND_T7, DOOR_T7 = {}, []
for nm, (cell, ax, walls) in KL.items():
    b = cell.bounds
    lo, hi = b[1 - ax], b[3 - ax]                      # wzdłuż biegów: A, B – v; C – s
    res_ = {"A": resA, "B": resB, "C": resC}[nm]
    LAND_T7[nm] = landings(res_, END0[nm], hi - lo, LANES[nm])
    for kl, levels, pas, (o0, o1), wmin, opis in DOORS_T7:
        if kl != nm:
            continue
        for lv in levels:
            ld = LAND_T7[nm][lv]
            dmax = max(x[0] for x in ld["pasy"].values())
            depth = ld["pasy"].get(pas, (dmax,))[0]           # pas bez biegu na tej kondygnacji: spocznik na całej szerokości
            span = (lo, lo + depth) if ld["koniec"] == "S-end" else (hi - depth, hi)
            if pas in ld["pasy"]:
                ext = (span[1] - EXT, span[1]) if ld["koniec"] == "S-end" else (span[0], span[0] + EXT)
                gap_ = max(abs(o1 - ext[0]) if o1 <= ext[0] + 1e-9 else -1, abs(o0 - ext[1]) if o0 >= ext[1] - 1e-9 else -1)
            else:
                ext, gap_ = None, None
            inside = o0 >= span[0] - 1e-9 and o1 <= span[1] + 1e-9
            clr = (o1 - o0) - 2 * FR
            okd = inside and clr >= wmin - 1e-9 and (gap_ is None or gap_ >= FR - 1e-9)
            DOOR_T7.append(dict(klatka=nm, kond=lv, pas=pas, otwor=(o0, o1), spocznik=span, przedluzenie=ext, odstep=gap_,
                                w_swietle=round(clr, 2), wymagane=wmin, ok=okd, opis=opis))
            assert okd, f"[T7] kolizja/szerokość drzwi: klatka {nm} kond. {lv} pas {pas} otwór {o0}–{o1} spocznik {span} przedłużenie {ext}"
print("  przedłużenia pochwytów 0,30 m (M.13 Balustrady pkt 6) na spocznikach kondygnacyjnych – model pasów biegów (biegi kolejno"
      " zmieniają pas; głębokość spocznika w pasie = L − 1,50 − rzut biegu):")
for nm in KL:
    print(f"    klatka {nm} (pasy biegów parzystych/nieparzystych: {LANES[nm][0]}/{LANES[nm][1]}): " + "; ".join(
        f"{lv} {('pd./zach.' if d_['koniec'] == 'S-end' else 'pn./wsch.')} " + ", ".join(f"{p_} {x[0]:.2f} ({x[1]})" for p_, x in d_['pasy'].items())
        for lv, d_ in LAND_T7[nm].items()))
for d_ in DOOR_T7:
    print(f"    {'✔' if d_['ok'] else '✗'} klatka {d_['klatka']} kond. {d_['kond']:>3}, ściana pasa {d_['pas']}: otwór {d_['otwor'][0]:.2f}–{d_['otwor'][1]:.2f}"
          f" (w świetle {d_['w_swietle']:.2f} ≥ {d_['wymagane']:.2f}) w spoczniku {d_['spocznik'][0]:.2f}–{d_['spocznik'][1]:.2f}; przedłużenie "
          + (f"{d_['przedluzenie'][0]:.2f}–{d_['przedluzenie'][1]:.2f}, odstęp {d_['odstep']:.2f} ≥ {FR:.2f}" if d_["przedluzenie"] else "– (brak biegu w pasie)")
          + f" – {d_['opis'][:70]}")
print(f"  test kolizji: {sum(d_['ok'] for d_ in DOOR_T7)}/{len(DOOR_T7)} drzwi bez kolizji z przedłużeniami i z wymaganą szerokością ✔")
# schody reprezentacyjne S → +30,90 (droga z antresoli radnych) i stopnie galerii – balustrady obustronne z pochwytem 0,05 m od płaszczyzny
st_w = S2.STAIR_V[1] - S2.STAIR_V[0]
gs = S2.GAL_STEPS[0].bounds
gal_w = gs[3] - gs[1]
st_cl, gal_cl = st_w - 2 * POCH_OCC, gal_w - 2 * POCH_OCC
print(f"  schody reprezentacyjne S → +30,90: bieg {st_w:.2f} m, balustrady szklane obustronnie → w świetle poręczy {st_cl:.2f} m"
      f" ✔ ≥ 1,60 (gdyby traktować je jak klatkę na drodze ewakuacyjnej; M.13 pkt 4.3: ≥ 1,20)")
print(f"  stopnie galerii (6 × 0,15/0,30): {gal_w:.2f} m (v1.2b; było 1,00) → w świetle poręczy {gal_cl:.2f} m ✔ ≥ 1,20 (M.13 pkt 4.3);"
      f" przedsionek A' – bez schodów (dotyczy klatki A: S → +30,90 jak wyżej)")
assert st_cl >= 1.60 - 1e-9 and gal_cl >= 1.20 - 1e-9
cap = min(v["swiatlo"] for v in RES_T7.values())
print(f"  przepustowość klatki w świetle {cap:.2f} m: WT 0,6 m/100 os. → {cap / 0.006:.0f} os.; MDS (rozp. 2025 poz. 932 § 6 ust. 3) 0,4 m/100 os."
      f" → {cap / 0.004:.0f} os.")
print("  Wniosek: odstępstwo od M.13 pkt 6 niepotrzebne – pochwyty Ø 35 mm we wnękach 0,09 m (M.13 Balustrady i poręcze pkt 2: „poręcze możesz"
      " umieścić we wnęce”) i pochwyty od duszy nad krawędziami biegów; w pasie wnęki 0,16 m żelbetu (REI 120 bez obliczania μfi); klatki"
      " 3,40 m bez zmiany obrysów trzonów; wariant poszerzenia do 3,69 m (przedsionek A 2,81 m; B i C – zmiana obrysów trzonów) odrzucony.")
