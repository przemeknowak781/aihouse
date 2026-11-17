#!/usr/bin/env python3
"""v1.2 (scalenie S-3) – PU, miejsca postojowe i koszt realizacji (F.14.B, mid, netto, II kw. 2026), limit 150 mln zł.

Uruchomienie (z katalogu umwd/):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_v12_koszt.py
Zapisuje wejście modelu: docs/20_koncepcja/_rewizja_koszt_wejscie_v1_2.json (wszystkie klucze `tools/koszty_model.py`),
tak by `python3 -I tools/koszty_model.py docs/20_koncepcja/_rewizja_koszt_wejscie_v1_2.json` odtworzył część modelową.

Kroki:
  [K0] PU wg PN-ISO 9836 po S-3 (kategorie programu jak w tools/tabele_konkursowe.py) i wymóg MPZP § 13 wobec 110 m.p.;
  [K1] punkt wyjścia v1.1 – `_rewizja_koszt.py` (149,18 mln; A_nad z rezerwą antresoli do ≈ 180 m²);
  [K2] v1.2 – antresola S-3 297,9 m² (kondygnacja_S2.json), klatka A do +30,90, zmiany trzonów I5 (_v12_trzony.py);
  [K3] dźwignie v1.2 (efekt pojedynczy) i wybór: najpierw oszczędności niewidoczne na planszach, potem rezerwowe v1.1,
       aż zapas do 150 mln ≥ 1,0 mln przy rezerwie 5 %;
  [K4] wynik, wskaźniki, warianty kontrolne, wariant ryzyka (pozycje otwarte v1.2) i sposób pokrycia.
Kontrakt generatora tabel (tools/tabele_konkursowe.py): f14b_rows(level) – pozycje F.14.B (model bez 16.1 i 18.3* + pozycje
spoza modelu jako 18.10*… + 16.1 i 18.3* od sumy), KOSZT_DOKUMENTACJI [zł netto].
v1.2-fix (po weryfikacji scalenia): baza PU zamrożona (S, ANT modelu v1.1), balustrady podestu galerii, dźwignia „pokoje bez sufitu
podwieszanego” z podziałem na bryły, ścianki pokoi od korytarza – pełna ściana GK (bez naświetli), wariant ryzyka [K4].
"""
import io
import json
import math
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _rewizja_koszt as RK  # noqa: E402

km = RK.km
ROOT = RK.ROOT
LIMIT = 150.0
ZAPAS_MIN = 1.0
K = json.load(open(os.path.join(ROOT, "model", "koncepcja.json"), encoding="utf-8"))
S3 = json.load(open(os.path.join(HERE, "kondygnacja_S2.json"), encoding="utf-8"))
B = json.load(open(os.path.join(ROOT, "model", "budynek.json"), encoding="utf-8"))
KS_REZ = (1 + km.KS[1]) * (1 + km.REZ[1])


def hr(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


# ------------------------------------------------------------------------------------------------ [K0] PU i parking
hr("[K0] PU (PN-ISO 9836) po S-3 i wymóg miejsc postojowych (MPZP § 13)")
PU11 = 8850.37
GASTRO = 88.47


def kat(code):
    """Kategoria wg programu (program.yaml: SWD.* PU poza SWD.02 = RU; PHS, PP – PU; IT – US; KW, KUL – RU)."""
    c = code.upper()
    if c.startswith("SWD.02"):
        return "RU"
    if c.startswith(("SWD", "PHS", "PP")):
        return "PU"
    if c.startswith("IT"):
        return "US"
    return "RU"


OLD_FROZEN = {"S": 756.32, "ANT": 69.66}   # PU poziomów S i ANT modelu pomieszczeń v1.1 (stan, z którego policzono PU11 = 8 850,37)
old_live = {lv["id"]: sum(r["powierzchnia"] for r in lv["pomieszczenia"] if kat(r["numer"]) == "PU")
            for lv in B["kondygnacje"] if lv["id"] in ("S", "ANT")}
S3_IN_MODEL = any(r["numer"].startswith("SWD.01g") for lv in B["kondygnacje"] if lv["id"] in ("S", "ANT") for r in lv["pomieszczenia"])
if not S3_IN_MODEL:
    assert all(abs(old_live[k] - OLD_FROZEN[k]) < 0.01 for k in OLD_FROZEN), \
        f"model pomieszczeń zmieniony bez S-3 ({old_live}) – sprawdzić bazę PU (PU11 = 8 850,37 liczono z S/ANT {OLD_FROZEN})"
old = dict(OLD_FROZEN)
new_rooms = {**S3["pomieszczenia"], **S3["antresola_pomieszczenia"]}
new = {"S": sum(v["pow_m2"] for k, v in S3["pomieszczenia"].items() if kat(k) == "PU"),
       "ANT": sum(v["pow_m2"] for k, v in S3["antresola_pomieszczenia"].items() if kat(k) == "PU")}
dPU = sum(new.values()) - sum(old.values())
PU12 = PU11 + dPU
assert PU12 > PU11 - 1e-6, "PU v1.2 nie może spaść poniżej bazy v1.1 (S-3 ma więcej PU niż S v1.0)"
print(f"  PU kondygnacji S + antresoli w modelu pomieszczeń v1.1 (baza zamrożona): S {old['S']:.2f} + ANT {old['ANT']:.2f} = {sum(old.values()):.2f} m²"
      + (f"; model pomieszczeń PRZELICZONY z S-3 (S {old_live['S']:.2f} + ANT {old_live['ANT']:.2f}) – PU v1.2 nadal od bazy zamrożonej,"
         " kontrola z F.15.A po przeliczeniu" if S3_IN_MODEL else "; model pomieszczeń bez S-3 – zgodny z bazą ✔"))
print(f"  PU S-3: S {new['S']:.2f} + ANT {new['ANT']:.2f} = {sum(new.values()):.2f} m² (SWD bez SWD.02/02g – RU; PHS.05a–c, PP.06;"
      f" IT.02 – US; kuluar, KW – RU)")
print(f"  ΔPU = {dPU:+.2f} m² → PU v1.2 = {PU11:.2f} {dPU:+.2f} = {PU12:.2f} m² (antresola wnosi PU: galeria {S3['antresola_pomieszczenia']['SWD.01g']['pow_m2']},"
      f" SWD.03 {S3['antresola_pomieszczenia']['SWD.03']['pow_m2']}, SWD.05 {S3['antresola_pomieszczenia']['SWD.05']['pow_m2']},"
      f" PHS.05c {S3['antresola_pomieszczenia']['PHS.05c']['pow_m2']})")
req = 12 / 1000 * (PU12 - GASTRO) + 6 / 1000 * GASTRO
REQ = math.ceil(req)
REQ_CONS = math.ceil(12 / 1000 * PU12) + math.ceil(6 / 1000 * GASTRO)
MP = K["podziemie"]["razem_miejsc"]
print(f"  wymagane: 12/1000 × ({PU12:.2f} − {GASTRO}) + 6/1000 × {GASTRO} = {req:.2f} → {REQ} m.p.; odczyt ostrożny"
      f" {math.ceil(12 / 1000 * PU12)} + {math.ceil(6 / 1000 * GASTRO)} = {REQ_CONS}; projekt {MP} m.p. → zapas {MP - REQ} / {MP - REQ_CONS} ✔"
      f" (bar SWD.05 policzony ostrożnie jako PU biurowe 12/1000, nie gastronomia)")
PU_MAX = (MP - 6 / 1000 * GASTRO) / 0.012 + GASTRO
print(f"  110 m.p. wystarcza (odczyt podstawowy) dopóki PU ≤ {PU_MAX:.1f} m² → rezerwa PU {PU_MAX - PU12:.1f} m²")

# ------------------------------------------------------------------------------------------------ [K1] v1.1
hr("[K1] Punkt wyjścia v1.1 (_rewizja_koszt.py)")
f11 = os.path.join(HERE, "_rewizja_koszt_wejscie_v1_1.json")
before = open(f11, "rb").read()
with redirect_stdout(io.StringIO()):
    r11 = RK.main()
after = open(f11, "rb").read()
if after != before:                      # main() zapisuje wejście v1.1 – przywróć bajtowo, jeśli różni się formatem
    open(f11, "wb").write(before)
P11, POZA11 = r11["P"], r11["poza"]
ex11 = sum(v[0] for v in POZA11.values())
t11, wk11, _ = RK.total(P11, ex11)
print(f"  v1.1: A_nad {P11['A_nad']} (w tym rezerwa antresoli do ≈ 180 m²), roboty + KS {wk11:.2f}, razem z rezerwą 5 % {t11:.2f} mln,"
      f" zapas {LIMIT - t11:.2f} mln; plik wejścia v1.1 bez zmian: {after == before}")

# ------------------------------------------------------------------------------------------------ [K2] v1.2 – ilości
hr("[K2] v1.2 – antresola S-3, klatka A do +30,90, trzony wg I5")
ant12 = S3["antresola"]["pow_m2"]
ant10 = 69.7
PC_nad11 = 14164.5                      # bilans v1.1 (P 2 005,8 + 4 × 2 162,9 + 3 × 1 145,8 + antresola 69,7)
PC_nad12 = round(PC_nad11 - ant10 + ant12, 1)
P = dict(P11)
P["A_nad"] = PC_nad12
P["n_kond_klatki"] = round((P11["n_klatek"] * P11["n_kond_klatki"] + 1) / P11["n_klatek"], 2)   # + klatka A: S → +30,90
BAL_PODEST = S3["antresola"]["balustrady_podestu_galerii_mb"]          # v1.2-fix: krawędzie podestu galerii (+0,90)
D_EDGE = S3["antresola"]["krawedz_otwarta_na_hol_m"] - 21.75             # zmiana krawędzi antresoli radnych (otwór nad biegiem) wobec S-3
P["bal_wew"] = round(P11["bal_wew"] + 5 + BAL_PODEST + D_EDGE, 1)        # S-3: galeria 10,2 + krawędź holu + schody (≈ +5 mb wobec v1.0)
print(f"  PC nadziemna: {PC_nad11} − antresola v1.0 {ant10} + antresola S-3 {ant12} = {PC_nad12} m² (A_nad v1.1 z rezerwą: {P11['A_nad']};"
      f" przyrost ponad rezerwę {PC_nad12 - P11['A_nad']:+.1f} m²)")
print(f"  klatki: n_kond_klatki {P11['n_kond_klatki']} → {P['n_kond_klatki']} (klatka A przedłużona do +30,90); balustrady wewn."
      f" {P11['bal_wew']} → {P['bal_wew']} mb (S-3 +5; v1.2-fix: podest galerii +{BAL_PODEST:.1f}, krawędź otworu nad schodami {D_EDGE:+.1f})")
H_TRZON = 34.15 - (-7.30)
POZA12 = {
    f"trzon A (I5): wydłużenie o 0,60 m na pd. – ściany żelbetowe 2 × 0,60 m × {H_TRZON:.2f} m (−7,30…+34,15) × 550 zł/m²":
        (2 * 0.60 * H_TRZON * 550, "_v12_trzony.py [T2]; stawka 3.3 mid"),
    "klatki A i C trójbiegowe na kond. −1/P i P/1: 4 biegi + 4 spoczniki ≈ 2 × (35 000 + 30 m² × 230 + 14 mb × 900 + 11 mb × 200)":
        (2 * (35000 + 30 * 230 + 14 * 900 + 11 * 200), "_v12_trzony.py [T2], [T4]; stawki 3.8, 13.2, 14.1, 14.2"),
    "trzon C (I5): bez szybu C1 – ściany szybu −2,55 m × 24,0 m (−4,20…+19,80) × 550 zł/m²":
        (-2.55 * 24.0 * 550, "_v12_trzony.py [T4]"),
}
for k, (v, why) in POZA12.items():
    print(f"     + {k}: {v * KS_REZ / 1e6:+.3f} mln (z KS i rezerwą; {why})")
POZA = {**POZA11, **POZA12}
ex = sum(v[0] for v in POZA.values())
t0, wk0, r0 = RK.total(P, ex)
print(f"  v1.2 przed dźwigniami: roboty + KS {wk0:.2f}, razem {t0:.2f} mln (Δ wobec v1.1 {t0 - t11:+.2f}), zapas {LIMIT - t0:.2f} mln")
eff_ant = RK.total(dict(P11, A_nad=PC_nad12), ex11)[0] - t11
print(f"     w tym antresola ponad rezerwę (sama zmiana A_nad): {eff_ant:+.2f} mln; klatka A i balustrady:"
      f" {RK.total(dict(P11, A_nad=PC_nad12, n_kond_klatki=P['n_kond_klatki'], bal_wew=P['bal_wew']), ex11)[0] - t11 - eff_ant:+.2f};"
      f" trzony I5: {sum(v[0] for v in POZA12.values()) * KS_REZ / 1e6:+.2f}")

# ------------------------------------------------------------------------------------------------ [K3] dźwignie
hr("[K3] Dźwignie v1.2 (efekt pojedynczy, mln zł z KS i rezerwą 5 %)")
from shapely.geometry import Point as _Pt, Polygon as _Pg  # noqa: E402
_BR = {nm: _Pg(K["bryly"][i]["obrys_ccw"]) for i, nm in enumerate(("wieża", "skrzydło", "segment"))}


def _bryla(r):
    pg = r["poligon"]
    while isinstance(pg[0][0], list):
        pg = pg[0]
    c = _Pg(pg).representative_point()
    return next((nm for nm, g in _BR.items() if g.buffer(0.05).contains(c)), "inne")


POK = {}
for lv in B["kondygnacje"]:
    for r in lv["pomieszczenia"]:
        if r.get("kind") == "office":
            POK[_bryla(r)] = POK.get(_bryla(r), 0.0) + r["powierzchnia"]
pokoje = sum(POK.values())
NASW = 0.0                               # v1.2-fix: ściany GK pełne, bez naświetli (z naświetlem 25 % efekt −0,23 zamiast −0,31 mln)
LEV = [
    # (klucz, opis, widoczność na planszach, zmiana P, kwota spoza modelu)
    ("TABS", "pokoje bez sufitu podwieszanego – strop odsłonięty z wyspami akustycznymi 0,35 m²/m² × 260 zł zamiast sufitu modułowego"
             f" 180 zł/m² (poz. 12.1): wieża (TABS, baffle) {POK.get('wieża', 0):,.0f} m², skrzydło {POK.get('skrzydło', 0):,.0f} m²,"
             f" segment {POK.get('segment', 0):,.0f} m² (rozdz. 4.2; instalacje w korytarzach i w warstwie podłogi)",
     "niewidoczne (wnętrza biur poza kadrami W6–W8)", {}, -pokoje * (180 - 0.35 * 260)),
    ("SZKLO", "ścianki szklane wewn. 10 % → 8 % A (poz. 11.5): pokoje biurowe od korytarza – pełna ściana GK (bez naświetli;"
              " korytarze oświetlone sztucznie); szkło w salach narad, sekretariatach, holach i strefie Sejmiku bez zmian",
     "niewidoczne (korytarze biurowe)", {}, -0.02 * PC_nad12 * (1200 - 200) * (1 - NASW)),
    ("BESS", "magazyn energii 150 → 100 kWh (dźwignia rezerwowa v1.1; autokonsumpcja PV 0,80 w _bilans_energii.py bez zmian)",
     "niewidoczne", {"kwh_bess": 100}, 0.0),
    ("FILARY", "filary elewacji pd. wieży (dziedziniec) granit → ceramika (dźwignia rezerwowa v1.1)",
     "WIDOCZNE (elewacja pd. P7, kadr W10)", {}, -0.23e6 / KS_REZ),
]
eff = {}
for key, opis, vis, dp, dx in LEV:
    t_, _, _ = RK.total(dict(P, **dp), ex + dx)
    eff[key] = t_ - t0
    print(f"  {key:6s} {eff[key]:+.2f}  – {opis} [{vis}]")
chosen = []
t_sel, P_sel, ex_sel = t0, dict(P), ex
for key, opis, vis, dp, dx in LEV:
    if LIMIT - t_sel >= ZAPAS_MIN - 1e-9:
        break
    chosen.append(key)
    P_sel.update(dp)
    ex_sel += dx
    t_sel, _, _ = RK.total(P_sel, ex_sel)
print(f"  wybrane (kolejność: niewidoczne → rezerwowe v1.1, do zapasu ≥ {ZAPAS_MIN:.1f} mln): {chosen} → razem {t_sel:.2f} mln,"
      f" zapas {LIMIT - t_sel:.2f} mln")
POZA_LEV = {}
for key, opis, vis, dp, dx in LEV:
    if key in chosen and dx:
        POZA_LEV[f"dźwignia v1.2 {key}: {opis}"] = (dx, vis)

# ------------------------------------------------------------------------------------------------ [K4] wynik
hr("[K4] Wynik v1.2 (mid, netto, II kw. 2026)")
POZA_F = {**POZA, **POZA_LEV}
exF = sum(v[0] for v in POZA_F.values())
tF, wkF, rF = RK.total(P_sel, exF)
rez = km.REZ[1]
print(f"  roboty – model {rF['works'] / 1e6:.2f}; pozycje spoza modelu {exF / 1e6:.2f}; koszty stałe 3 % {(rF['ks'] + exF * km.KS[1]) / 1e6:.2f}")
print(f"  roboty + koszty stałe: {wkF:.2f} mln; rezerwa (contingency) {rez:.0%}: {wkF * rez:.2f} mln")
print(f"  RAZEM {tF:.2f} mln ≤ {LIMIT:.0f}: {'TAK' if tF <= LIMIT else 'NIE'}; zapas {LIMIT - tF:.2f} mln ({(LIMIT - tF) / LIMIT:.1%});"
      f" bufor (rezerwa + zapas) {wkF * rez + LIMIT - tF:.2f} mln ({(wkF * rez + LIMIT - tF) / wkF:.1%} robót)")
t4, _, _ = RK.total(P_sel, exF, rez=0.04)
print(f"  wariant kontrolny: rezerwa 4,0 % → {t4:.2f} mln (zapas {LIMIT - t4:.2f})")
g = {k: v / 1e6 for k, v in rF["groups"].items()}
g18_model = rF["groups"][18] - rF["rez"]
print(f"  grupy do tabeli 12: " + "; ".join(f"{k}: {g[k]:.2f}" for k in sorted(g) if k not in (16, 18))
      + f"; 18 (MDS, zamurowanie): {g18_model / 1e6:.2f}; roboty – model {rF['works'] / 1e6:.2f}")
print(f"  pozycje spoza modelu (robót): {exF / 1e6:.2f} mln; koszty stałe 3 % razem: {(rF['ks'] + exF * km.KS[1]) / 1e6:.2f};"
      f" roboty z KS {wkF:.2f}")
pc = P_sel["A_nad"] + P_sel["A_pod"]
print(f"  wskaźniki: {tF * 1e6 / pc:,.0f} zł/m² PC (PC {pc:,.1f} m²); {tF * 1e6 / PU12:,.0f} zł/m² PU (PU {PU12:,.2f}); PC/PU {pc / PU12:.2f}")
for lvl, fac in (("low", 0.8), ("high", 1.3)):
    q = dict(km.REF)
    q.update(P_sel)
    r = km.compute(q, lvl)
    i = km.LEVELS[lvl]
    print(f"  scenariusz {lvl}: {r['total'] / 1e6 + exF * fac * (1 + km.KS[i]) * (1 + km.REZ[i]) / 1e6:.1f} mln")
print(f"  waloryzacja +5 % (2027) od kosztu całkowitego: {tF * 1.05:.1f} mln")
print("  pozycje spoza modelu v1.2 (nowe):")
for k, (v, why) in {**POZA12, **POZA_LEV}.items():
    print(f"     {v / 1e6:+.3f} mln robót ({v * KS_REZ / 1e6:+.3f} z KS i rezerwą): {k[:150]}")
# ---- wariant ryzyka: pozycje otwarte v1.2 z wariantem awaryjnym (mln zł z KS i rezerwą 5 %)
print("  wariant ryzyka (pozycje otwarte v1.2 – rozdz. 16, rejestr V12-OPEN):")
RISK = {
    "R1": ("tryskacze w strefie S (pompownia 80 m² i zbiornik; weryfikacja_koszt_eko.md: +0,5…+1,0 mln)", (0.5e6, 1.0e6),
           "NIEPOTRZEBNE po v1.2-fix: dojścia ZL I bez zwiększeń +50 % (_s2_ewakuacja.py [E2]) – wariant tylko informacyjnie"),
    "R2": ("szyb awaryjny z −2 (gdy „2 klatki ≥ 15 m” liczone między obudowami: 13,95 m) – jak szyb MDS + tunel (P-I6)", (0.25e6, 0.25e6),
           "otwarte – pomiar do potwierdzenia (rozp. 2025 poz. 932 § 6)"),
    "R3": ("MDS 592 zamiast 560 os. (+32 os.; adaptacja 18.1* 1,5 mln × 32/560)", (1.5e6 * 32 / 560, 1.5e6 * 32 / 560),
           "otwarte – pojemność z postanowienia organu (art. 95a)"),
}
for k, (nm, (lo, hi), st) in RISK.items():
    rng = f"{lo * KS_REZ / 1e6:.2f}" + (f"–{hi * KS_REZ / 1e6:.2f}" if hi != lo else "")
    print(f"     {k}: +{rng} mln – {nm}; {st}")
R_OPEN = sum(RISK[k][1][1] for k in ("R2", "R3")) * KS_REZ / 1e6
z_r = LIMIT - tF - R_OPEN
z_rf = z_r - eff["FILARY"] if "FILARY" not in chosen else z_r
t4r = t4 + R_OPEN * (1 + km.KS[1]) * 1.04 / KS_REZ
print(f"     R2 + R3 (otwarte): +{R_OPEN:.2f} mln → zapas {z_r:.2f} mln {'≥' if z_r >= ZAPAS_MIN else '<'} {ZAPAS_MIN:.1f};"
      f" pokrycie: dźwignia FILARY ({eff['FILARY']:+.2f}) → zapas {z_rf:.2f}; rezerwa 4 % (≥ 4 % – wymóg) → razem {t4r:.2f} mln,"
      f" zapas {LIMIT - t4r:.2f} mln {'≥' if LIMIT - t4r >= ZAPAS_MIN else '<'} {ZAPAS_MIN:.1f}")
r1lo, r1hi = (x * KS_REZ / 1e6 for x in RISK["R1"][1])
print(f"     gdyby mimo to wymagano tryskaczy (R1): zapas przy rezerwie 4 % i R2 + R3: {LIMIT - t4r - r1hi * 1.04 / 1.05:.2f}…"
      f"{LIMIT - t4r - r1lo * 1.04 / 1.05:.2f} mln (+ FILARY {-eff['FILARY']:.2f})")
out = os.path.join(HERE, "_rewizja_koszt_wejscie_v1_2.json")
json.dump({k_: P_sel[k_] for k_ in sorted(P_sel)}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"  wejście modelu zapisane: {os.path.relpath(out, ROOT)}")
RESULT = dict(total=tF, works_ks=wkF, rez=wkF * rez, zapas=LIMIT - tF, t4=t4, P=P_sel, PU=PU12, REQ=REQ, REQ_CONS=REQ_CONS,
              PC_nad=PC_nad12, chosen=chosen, model=rF["works"] / 1e6, poza=exF / 1e6,
              ryzyko=dict(R_open=R_OPEN, zapas_po=z_r, zapas_po_filary=z_rf, t4_po=t4r, R1=(r1lo, r1hi)))

# ------------------------------------------------------------------------------------------------ kontrakt F.14.B
KOSZT_DOKUMENTACJI = 7.6e6          # koszt Dokumentacji [zł netto] (rozdz. 12; ≤ 5,4 % × 150 mln = 8,1 mln)


def f14b_rows(level="mid"):
    """Pozycje F.14.B v1.2 (konwencja koszty_model.compute()["rows"]): pozycje modelu bez 16.1 i 18.3*, pozycje spoza modelu
    (18.10*…; wartość robót, low × 0,8 / high × 1,3 jak w scenariuszach), 16.1 = KS × (roboty + spoza modelu),
    18.3* = REZ × (roboty + spoza modelu + KS). Dla mid suma = RESULT["total"]."""
    i = km.LEVELS[level]
    q = dict(km.REF)
    q.update(P_sel)
    r = km.compute(q, level)
    rows = [x for x in r["rows"] if x[0] not in ("16.1", "18.3*")]
    fac = {"low": 0.8, "mid": 1.0, "high": 1.3}[level]
    ex_rows = []
    for k, (nm, (v, why)) in enumerate([(n, x) for n, x in POZA_F.items() if abs(x[0]) > 1e-6], start=10):
        val = v * fac
        ex_rows.append((f"18.{k}*", nm[0].upper() + nm[1:], "kpl", 1, val, val))
    works = sum(x[5] for x in rows) + sum(x[5] for x in ex_rows)
    ks = works * km.KS[i]
    rz = (works + ks) * km.REZ[i]
    return rows + ex_rows + [("16.1", "Koszty stałe budowy", "kpl", 1, ks, ks),
                             ("18.3*", "Rezerwa na nieprzewidziane", "kpl", 1, rz, rz)]


_rows_mid = f14b_rows("mid")
assert abs(sum(x[5] for x in _rows_mid) / 1e6 - tF) < 1e-6, "f14b_rows(mid) ≠ RESULT['total']"
print(f"  kontrakt F.14.B: f14b_rows('mid') – {len(_rows_mid)} pozycji, suma {sum(x[5] for x in _rows_mid) / 1e6:.2f} mln = wynik ✔;"
      f" KOSZT_DOKUMENTACJI {KOSZT_DOKUMENTACJI / 1e6:.1f} mln")
