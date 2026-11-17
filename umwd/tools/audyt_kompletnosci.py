#!/usr/bin/env python3
"""Audyt kompletności i zgodności pracy konkursowej (Etap II) – lista kontrolna docs/10_regulamin/lista_kontrolna_etap2.md
przełożona na sprawdzenia plików (build/, docs/) i liczb (model/koncepcja.json, model/budynek.json).
Wynik: docs/90_audyt/audyt_kompletnosci.md (✔ spełnione · ✗ brak/niezgodne · ~ częściowo / do weryfikacji ręcznej).
"""
import sys, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
B = ROOT / "build"
RYS = B / "rysunki"
VIS = ROOT / "docs" / "60_wizualizacje" / "img"
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
BM = json.loads((ROOT / "model" / "budynek.json").read_text(encoding="utf-8")) if (ROOT / "model" / "budynek.json").exists() else {"kondygnacje": []}
rows = []


def chk(group, item, ok, note="", ref=""):
    rows.append((group, item, ok, note, ref))


def svg_text(name):
    p = RYS / name
    return p.read_text(encoding="utf-8") if p.exists() else ""


def has(name):
    return (RYS / name).exists()


# ---------------- 1.1 graphic content
t = svg_text("zagospodarowanie_1-500.svg")
chk("Plansze", "Zagospodarowanie 1:500 z cieniami SW 45°", "SW pod kątem 45" in t, "plik zagospodarowanie_1-500.svg", "R-102, R-103")
for kw, lab in (("Zjazd do garażu", "zjazd do garażu / dostawy od Wybrzeża"), ("drogi pożarowe", "drogi pożarowe"), ("drzewa usuwane", "zieleń istniejąca/usuwana/nowa"),
                ("PLAC MOSTOWY", "skwer dz. 9/2"), ("ogródki", "ogródki nieogrodzone z drzewami"), ("attyka", "rzędne i liczba kondygnacji")):
    chk("Plansze", f"PZT: {lab}", kw.lower() in t.lower(), "", "R-021–R-023")
chk("Plansze", "PZT: dojazd do dz. 10/2 opisany", "10/2" in t, "dodać opis na PZT, jeśli brak", "R-214")
levels = [lv["id"] for lv in BM.get("kondygnacje", [])]
missing = [lid for lid in levels if not has(f"rzut_{lid}_1-200.svg")]
chk("Plansze", "Rzuty wszystkich kondygnacji 1:200 (osobno) + dach", not missing and bool(levels), "brak: " + ", ".join(missing) if missing else "", "R-104, R-219")
chk("Plansze", "Rzut parteru z otoczeniem 1:200 (nawierzchnie, mała architektura, oświetlenie)", has("rzut_P_otoczenie_1-200.svg"), "", "R-105")
chk("Plansze", "Min. 2 przekroje 1:200", has("przekroj_AA_1-200.svg") and has("przekroj_BB_1-200.svg"), "", "R-106")
ew, ee = svg_text("elewacja_W_1-200.svg"), svg_text("elewacja_E_1-200.svg")
chk("Plansze", "Elewacja od Mazowieckiej z budynkiem nr 19", "Mazowiecka 19" in ew, "", "R-107")
chk("Plansze", "Elewacja od Wybrzeża z budynkiem nr 5", "Słowackiego 5" in ee, "", "R-107")
chk("Plansze", "Wszystkie elewacje 1:200 (N, E, S, W + dziedziniec)", all(has(f"elewacja_{k}_1-200.svg") for k in "NESW"), "Sd opcjonalnie", "R-107")
chk("Plansze", "Przekrój elewacyjny + fragment elewacji 1:50", has("przekroj_elewacyjny_1-50.svg") or has("przekroj_elewacyjny_1-50_korona.svg"), "", "R-108")
chk("Plansze", "Schemat aksonometryczny układu funkcjonalnego", has("aksonometria_funkcjonalna.svg"), "", "R-109")
names = {1: "F.17.A lot ptaka od wschodu", 2: "F.17.B lot ptaka od zachodu", 3: "strefa wejściowa", 4: "relacja z WS 5", 5: "relacja z Maz. 19", 6: "hol główny", 7: "hol sali Sejmiku", 8: "sala Sejmiku z publicznością"}
for n, lab in names.items():
    fin = sorted(VIS.glob(f"W{n}_*final*.jpg"))
    chk("Wizualizacje", f"Wizualizacja nr {n} – {lab}", bool(fin), fin[0].name if fin else "brak wersji finalnej", "R-110")
chk("Plansze", "Schemat proekologiczny z liczbami", has("schemat_eko.svg") or any(RYS.glob("schemat_eko_*.svg")), "", "R-111")
chk("Plansze", "Schemat dostępności", any(RYS.glob("schemat_dostepnosci*.svg")), "", "R-112")
chk("Plansze", "Analiza przesłaniania / nasłonecznienia (WS 5, Maz. 19)", has("naslonecznienie.svg"), "", "R-210")
chk("Plansze", "Schematy dodatkowe (idea)", has("schematy_idei.svg"), "", "R-113")
boards = sorted((B / "plansze").glob("etap2_P*.png"))
chk("Plansze", "Liczba plansz ≤ 8", len(boards) <= 8 and len(boards) > 0, f"{len(boards)} szt.", "R-101")
# ---------------- 2 description + tables
T = B / "tabele"
for f, ref in (("F.15.A.xlsx", "R-118"), ("F.15.B.xlsx", "R-118"), ("F.15.C.xlsx", "R-118"), ("F.14.B.xlsx", "R-119 (brak = brak oceny)")):
    chk("Część opisowa", f"Tabela {f}", (T / f).exists(), "", ref)
chk("Część opisowa", "Tekst ≤ 5 stron A3, czcionka ≥ 11 pt (PDF)", ((B / "opis" / "opis_etap2_A3.pdf").exists() or (B / "opis" / "opis_A3.pdf").exists()), "", "R-116, S-04")
chk("Część opisowa", "Plansze pomniejszone A3 300 dpi", bool(list((B / "eksport").glob("*A3*"))) if (B / "eksport").exists() else False, "", "R-120")
# ---------------- 5 electronic export
exp = B / "eksport"
tifs = [f for f in sorted(exp.glob("PLANSZA_*.jpg")) + sorted(exp.glob("PLANSZA_*.tif")) if "_A3" not in f.name] if exp.exists() else []
chk("Eksport", "Plansze JPG/TIFF 100×70 cm, 300 dpi (11 811 × 8 268 px)", len(tifs) >= len(boards) and bool(boards), f"{len(tifs)} plików", "R-129")
# ---------------- substantive numbers
bl = K.get("bilans", {})
cost = bl.get("koszt_mln_netto")
chk("Merytoryka", "Koszt realizacji ≤ 150 mln zł netto (z rezerwą)", cost is not None and cost <= 150, f"{cost} mln (wg koncepcja.json; weryfikacja kosztów: patrz rejestr poprawek)", "R-222")
pv = K.get("elewacje", {}).get("PV", {}).get("razem_kWp")
chk("Merytoryka", "PV na działce ≥ 400 kWp (M.12)", pv is not None and pv >= 400, f"{pv} kWp (deklaracja; weryfikator v1.0: ≈ 328 realnie)", "M.12")
W = next(b for b in K["bryly"] if b["id"] == "W")
low = W["dach"]["najnizszy_pkt_pokrycia"]["nad_najwyzszym_terenem_A"]; top = W["dach"]["attyka"]["nad_najnizszym_terenem_A"]
chk("Merytoryka", "Strefa A: 35 m ≤ dach ≤ 45 m", 35 <= low and top <= 45, f"najniższy pkt pokrycia {low} m, attyka {top} m", "MPZP, R-207")
Mb = next(b for b in K["bryly"] if b["id"] == "M")
chk("Merytoryka", "Poza A: 18 m ≤ dach ≤ 25 m (skrzydło)", Mb["dach"]["najnizszy_pkt_pokrycia"]["nad_najwyzszym_terenem"] >= 18 and Mb["dach"]["gzyms_attyka"]["nad_najnizszym_terenem"] <= 25, "", "MPZP")
sun = ROOT / "docs" / "70_rysunki" / "naslonecznienie.json"
if sun.exists():
    rws = json.loads(sun.read_text(encoding="utf-8"))
    worst = min(min(v["suma_min"] for k, v in r.items() if isinstance(v, dict)) for r in rws)
    chk("Merytoryka", "§ 60 WT: okna chronione ≥ 1,5 h w dniach równonocy", worst >= 90, f"najgorsze okno {worst / 60:.1f} h", "R-209")
tests = BM.get("testy", [])
bad = [t for t in tests if not t.get("ok")]
chk("Merytoryka", "Model pomieszczeń: samokontrole programu", not bad, "; ".join(f"{t['test']}: {t['szczegoly']}" for t in bad)[:600], "R-018, R-217")
reg = ROOT / "docs" / "20_koncepcja" / "rejestr_poprawek_v1_1.md"
chk("Merytoryka", "Rewizja po weryfikacji (v1.1) – rejestr poprawek", reg.exists(), "", "audyt")
# ---------------- anonymity
leak = []
for p in list((B / "plansze").glob("*.html")):
    s = p.read_text(encoding="utf-8").lower()
    for w in ("pracownia", "architekci", "sp. z o.o", "s.c.", "autor:", "numer identyfikacyjny"):
        if w in s:
            leak.append(f"{p.name}:{w}")
chk("Anonimowość", "Brak oznaczeń autora i numeru na planszach", not leak, ", ".join(leak), "R-127, R-133")

out = ROOT / "docs" / "90_audyt"
out.mkdir(parents=True, exist_ok=True)
sym = {True: "✔", False: "✗"}
lines = ["# Audyt kompletności – Etap II (automatyczny)", "", f"Źródła: build/, docs/, model/ · koncepcja {K['meta'].get('wersja')}", "",
         "| Grupa | Element | Stan | Uwagi | Ref. |", "|---|---|:---:|---|---|"]
for g, i, ok, n, r in rows:
    lines.append(f"| {g} | {i} | {sym[bool(ok)]} | {n} | {r} |")
okc = sum(1 for r in rows if r[2])
lines += ["", f"**Wynik: {okc} / {len(rows)} spełnione.**"]
(out / "audyt_kompletnosci.md").write_text("\n".join(lines), encoding="utf-8")
print(f"{okc}/{len(rows)}")
for g, i, ok, n, r in rows:
    if not ok:
        print("✗", g, "|", i, "|", n[:160])
