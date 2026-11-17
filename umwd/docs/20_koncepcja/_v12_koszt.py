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
  [K4] wynik, wskaźniki, warianty kontrolne.
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


old = {lv["id"]: sum(r["powierzchnia"] for r in lv["pomieszczenia"] if kat(r["numer"]) == "PU")
       for lv in B["kondygnacje"] if lv["id"] in ("S", "ANT")}
new_rooms = {**S3["pomieszczenia"], **S3["antresola_pomieszczenia"]}
new = {"S": sum(v["pow_m2"] for k, v in S3["pomieszczenia"].items() if kat(k) == "PU"),
       "ANT": sum(v["pow_m2"] for k, v in S3["antresola_pomieszczenia"].items() if kat(k) == "PU")}
dPU = sum(new.values()) - sum(old.values())
PU12 = PU11 + dPU
print(f"  PU kondygnacji S + antresoli w modelu pomieszczeń (stan v1.0 S): S {old['S']:.2f} + ANT {old['ANT']:.2f} = {sum(old.values()):.2f} m²")
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
P["bal_wew"] = P11["bal_wew"] + 5        # S-3: galeria 10,2 + krawędź holu 21,8 + schody reprezentacyjne (≈ +5 mb wobec v1.0)
print(f"  PC nadziemna: {PC_nad11} − antresola v1.0 {ant10} + antresola S-3 {ant12} = {PC_nad12} m² (A_nad v1.1 z rezerwą: {P11['A_nad']};"
      f" przyrost ponad rezerwę {PC_nad12 - P11['A_nad']:+.1f} m²)")
print(f"  klatki: n_kond_klatki {P11['n_kond_klatki']} → {P['n_kond_klatki']} (klatka A przedłużona do +30,90); balustrady wewn."
      f" {P11['bal_wew']} → {P['bal_wew']} mb")
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
pokoje = sum(r["powierzchnia"] for lv in B["kondygnacje"] for r in lv["pomieszczenia"] if r.get("kind") == "office")
LEV = [
    # (klucz, opis, widoczność na planszach, zmiana P, kwota spoza modelu)
    ("TABS", f"biura z odsłoniętym TABS (rozdz. 4.2: „TABS odsłonięty, baffle”; skrzydło – kaseta ZIP pod stropem 3,20): pokoje"
             f" {pokoje:.0f} m² – wyspy akustyczne 0,35 m²/m² × 260 zł zamiast sufitu modułowego 180 zł/m² (poz. 12.1 – korekta spójności)",
     "niewidoczne (wnętrza biur poza kadrami W6–W8)", {}, -pokoje * (180 - 0.35 * 260)),
    ("SZKLO", "ścianki szklane wewn. 10 % → 8 % A (poz. 11.5): pokoje biurowe od korytarza – ściana GK z naświetlem; szkło w salach"
              " narad, sekretariatach, holach i strefie Sejmiku bez zmian",
     "niewidoczne (korytarze biurowe)", {}, -0.02 * PC_nad12 * (1200 - 200)),
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
out = os.path.join(HERE, "_rewizja_koszt_wejscie_v1_2.json")
json.dump({k_: P_sel[k_] for k_ in sorted(P_sel)}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"  wejście modelu zapisane: {os.path.relpath(out, ROOT)}")
RESULT = dict(total=tF, works_ks=wkF, rez=wkF * rez, zapas=LIMIT - tF, t4=t4, P=P_sel, PU=PU12, REQ=REQ, REQ_CONS=REQ_CONS,
              PC_nad=PC_nad12, chosen=chosen, model=rF["works"] / 1e6, poza=exF / 1e6)
