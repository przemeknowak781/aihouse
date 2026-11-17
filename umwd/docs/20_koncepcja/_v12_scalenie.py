#!/usr/bin/env python3
"""v1.2 – scalenie kondygnacji Sejmiku S-3 z koncepcją v1.1: zapis model/koncepcja.json (meta.wersja „1.2 (S-3)”) i walidacja.

Uruchomienie (z katalogu umwd/; po _s2_geometria.py, który zapisuje kondygnacja_S2.json):
    /home/user/aihouse/.venv-render/bin/python -I -W ignore docs/20_koncepcja/_v12_scalenie.py [--zapisz]
Bez --zapisz tylko buduje i waliduje. Przekształcenie jest idempotentne (wejście v1.1 lub v1.2 → ten sam wynik).
Źródła liczb: kondygnacja_S2.json (_s2_*.py), _v12_trzony.py (I5), _v12_koszt.py (koszt, PU, parking).
Walidacja [W1]–[W7]: JSON, poprawność wielokątów, położenie w obrysie wieży i w strefie A (site.json), brak nakładania
pomieszczeń S-3, sumy powierzchni, MPZP (rzędne dachów i kondygnacji bez zmian), spójność uv ↔ en.
NIE zmienia model/budynek.json (model pomieszczeń przelicza inny agent).
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
from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "model", "koncepcja.json")
K0 = json.load(open(OUT, encoding="utf-8"))
S3 = json.load(open(os.path.join(HERE, "kondygnacja_S2.json"), encoding="utf-8"))
SITE = json.load(open(os.path.join(ROOT, "model", "site.json"), encoding="utf-8"))
with redirect_stdout(io.StringIO()):
    import _v12_trzony as T                     # noqa: E402  (I5 – klatki, układ trzonów)
    import _v12_koszt as C                      # noqa: E402  (koszt, PU, parking)
import _s2_model as S2                          # noqa: E402

CU, SU, E0, N0 = 0.97155, 0.23684, 74.606, 40.756
uv2en = S2.uv2en


def sd2en(s, d):
    return (48.842 + 0.21498 * s + 0.97662 * d, 9.683 + 0.97662 * s - 0.21498 * d)


def ring_uv(g):
    return [[round(x, 3), round(y, 3)] for x, y in list(g.exterior.coords)[:-1]]


def ring_en(g, f=uv2en):
    pts = [[round(c, 3) for c in f(x, y)] for x, y in list(g.exterior.coords)[:-1]]
    if not Polygon(pts).exterior.is_ccw:
        pts = pts[::-1]
    return pts


def klatka_json(res, end_note):
    out = []
    for a, b, H, best in res:
        out.append({"z": a, "do": b, "H_m": H, "biegi": best["n_fl"], "stopnie": best["n"], "h_cm": round(best["h"] * 100, 2),
                    "s_cm": 28, "stopnie_w_biegach": best["risers"], "dl_biegow_m": [round(x, 2) for x in best["lens"]],
                    "wymagana_dl_klatki_m": round(best["need"], 2), "przeswit_m": round(best["clear"], 2)})
    return {"kondygnacje": out, "uwaga": end_note}


def build():
    d = copy.deepcopy(K0)
    m = d["meta"]
    m["wersja"] = "1.2 (S-3)"
    m["data_wersji"] = "17.11.2026"
    m["rejestr_poprawek"] = ("docs/20_koncepcja/rejestr_poprawek_v1_1.md – sekcje v1.0→v1.1 i „v1.2 – scalenie S-3” "
                             "(dowody: docs/20_koncepcja/_rewizja_*.py, _s2_*.py, _v12_*.py)")
    m.pop("kondygnacja_S_v1_1", None)
    m["kondygnacja_S_v1_2"] = ("kondygnacja_sejmiku = S-3 „hol z galerią” (docs/20_koncepcja/kondygnacja_S2.md, kondygnacja_S2.json, "
                               "skrypty _s2_*.py) scalona w v1.2; trzony A, B, C wg poprawki I5 (_v12_trzony.py)")
    m["zrodla"] = sorted(set(m.get("zrodla", []) + ["docs/20_koncepcja/kondygnacja_S2.md"]))

    # ------------------------------------------------------------------------------- kondygnacja Sejmiku = S-3
    ks = copy.deepcopy(S3)
    ks.pop("uklad", None)
    ks["zrodlo"] = ("docs/20_koncepcja/kondygnacja_S2.json (_s2_model.py → _s2_geometria.py); sala: _s2_sala.py; ewakuacja: "
                    "_s2_ewakuacja.py; trzony: _v12_trzony.py")
    ks["uklad_uv"] = "uv wieży: e = 74,606 + 0,97155·u − 0,23684·v; n = 40,756 + 0,23684·u + 0,97155·v"
    W_area = Polygon(d["bryly"][0]["obrys_ccw"]).area
    ks["ewakuacja"] = {
        "osoby_maks": 354, "strefa_ZL_I_m2": round(W_area + S3["antresola"]["pow_m2"], 1),
        "kuluar_szer_m": 2.20, "kuluar_przy_trzonie_A_m": round(S2.CORE_A.bounds[1] - 10.10, 2),
        "klatki_do_antresoli": ["A", "B"], "przedsionki": ["A", "A'", "B"],
        "limity": "ZL I bez tryskaczy: przejście 40 m (+25 % h > 5 m), dojście 10 / 40 m; kuluar i korytarz publiczny z samoczynnym "
                  "oddymianiem (SSP) → +50 % (15 / 60 m, § 256 ust. 3 – do potwierdzenia z rzeczoznawcą)",
        "dojscia_jednokierunkowe_ponad_10m": {"PHS.05c→B": 14.1, "SWD.11b→B": 10.2, "PP.06→B": 13.9},
    }
    d["kondygnacja_sejmiku"] = ks

    # ------------------------------------------------------------------------------- kondygnacje (S + antresola)
    for k in d["kondygnacje"]:
        if k["kondygnacja"] == "S":
            k["antresola_posadzka"] = S3["antresola"]["wzgl"]
            k["antresola"] = {"posadzka_wzgl": S3["antresola"]["wzgl"], "posadzka_npm": S3["antresola"]["npm"],
                              "pow_m2": S3["antresola"]["pow_m2"], "udzial_rzutu_proc": S3["antresola"]["udzial_rzutu_proc"],
                              "wys_w_swietle_pod_m": S3["antresola"]["wys_w_swietle_pod_m"],
                              "wys_w_swietle_nad_m": S3["antresola"]["wys_w_swietle_nad_m"],
                              "zakres": "wieża – antresola radnych (hol górny, bar, strefa multimedialna) i publiczności (galeria, hol P1/P2, korytarz EI 30)"}
    d["wysokosci_w_swietle"]["antresola_pod"] = S3["antresola"]["wys_w_swietle_pod_m"]
    d["wysokosci_w_swietle"]["antresola_nad"] = S3["antresola"]["wys_w_swietle_nad_m"]

    # ------------------------------------------------------------------------------- rdzenie
    r = d["rdzenie"]
    cA = S2.CORE_A_CELLS
    r["A"]["obrys_uv"] = ring_uv(S2.CORE_A)
    r["A"]["obrys_en"] = ring_en(S2.CORE_A)
    r["A"]["pow_m2"] = round(S2.CORE_A.area, 2)
    r["A"]["zakres"] = "−2…S + antresola +30,90"
    r["A"]["sklad"] = [
        "klatka A obudowana REI 60, 3,40 × 5,80 m w świetle: 2 biegi 1,60 m (M.13), stopnie ≤ 17,5 × 28 cm, spoczniki ≥ 1,50 m; "
        "kond. −1/P i P/1 – 3 biegi (spocznik kondygnacyjny parteru na końcu pn.); do antresoli +30,90",
        "przedsionek ppoż. A 3,10 × 5,80 m z MOE 1,5 × 1,5 m, krzesłem ewakuacyjnym i interkomem, nadciśnienie; drzwi pd. (kuluar S, hol strefy "
        "środkowej 1–6, Hala P), wsch. (łącznik S, garaż), na +30,90 wsch. na galerię; przedsionek A' (antresola radnych) przy ścianie zach. klatki",
        "dźwigi A1, A2 1 600 kg, kabiny 1,5 × 2,1 m, szyby 2,25 × 2,55 m, drzwi pn. na wszystkich kondygnacjach (S-3): hol S/ANT 5,95 m, "
        "łącznik pn. P, korytarz pn. kond. 1–6 2,15 m, przedsionek dźwigów −1/−2 (pas 7,20 × 1,75 m)",
        "dźwig R dla ekip ratowniczych PN-EN 81-72 i ewakuacyjny PN-EN 81-76, 1 000 kg, kabina 1,1 × 2,1 m, szyb 1,80 × 2,55 m REI 60, drzwi pd. do przedsionka A",
        "v1.2 (I5): trzon wydłużony o 0,60 m na pd. (v 12,45 → 11,85; ściana pd. 0,20 m) – kosztem holu strefy środkowej (kond. 1–6), Hali (P) i kuluaru S (2,20 → 1,75 m przy trzonie)",
    ]
    r["A"]["uklad_uv"] = {k: ring_uv(g) for k, g in cA.items()}
    r["A"]["drzwi_dzwigow"] = [x for x in S3["trzony_uklad"]["drzwi_dzwigow"] if x["dzwig"].startswith("A")] + \
        [{"dzwig": "R", "uv": [14.35, 18.05], "kierunek": [0, -1], "przystanki": "−2…S, ANT (do przedsionka A)"}]
    r["A"]["klatka"] = klatka_json(T.resA, "spocznik kondygnacyjny na końcu pd. (v 12,05–13,55) na wszystkich kondygnacjach poza P (koniec pn.)")
    cB = S2.CORE_B_CELLS
    r["B"]["pow_m2"] = round(S2.CORE_B.area, 2)
    r["B"]["zakres"] = "−2…S + antresola +30,90"
    r["B"]["sklad"] = [
        "klatka B obudowana REI 60, 3,40 × 6,64 m w świetle: 2 biegi 1,60 m na każdej kondygnacji (P: 2 × 14 stopni 17,14 × 28 cm), spoczniki ≥ 1,50 m; do antresoli +30,90",
        "przedsionek ppoż. B 3,40 × 2,06 m z MOE 1,5 × 1,5 m i interkomem, nadciśnienie (v1.2: ściana klatka/przedsionek przesunięta o 0,29 m)",
        "dźwigi publiczne P1, P2 1 600 kg, kabiny 1,5 × 2,1 m, szyby 2,15 × 2,65 m, drzwi wsch.; P1 – przystanki P, 1–6, ANT; P2 przelotowy – −2, −1 "
        "(drzwi zach. do przedsionka B), P, 1–6, S (służbowy, na klucz), ANT",
        "szacht 2,15 × 3,20 m (po dźwigu T): przewód spalin agregatu, wyrzut wentylacji i oddymiania garażu, piony centrali S → lamele korony od pd.",
    ]
    r["B"]["uklad_uv"] = {k: ring_uv(g) for k, g in cB.items()}
    r["B"]["drzwi_dzwigow"] = [x for x in S3["trzony_uklad"]["drzwi_dzwigow"] if x["dzwig"].startswith("P")]
    r["B"]["klatka"] = klatka_json(T.resB, "spocznik kondygnacyjny zawsze na końcu pn. (przy przedsionku B)")
    r["C"]["sklad"] = [
        "klatka C obudowana REI 60, 5,80 × 3,40 m w świetle (biegi wzdłuż s): 2 biegi 1,60 m (M.13; MDS 260 os. → 1,56 m), kond. −1/P i P/1 – 3 biegi",
        "przedsionek ppoż. C 5,80 × 2,00 m z MOE 1,5 × 1,5 m (koniec przeciwny do drzwi klatki) i interkomem, nadciśnienie; drzwi z korytarza (lico d 8,40)",
        "szachty 1,60 × 5,60 m (nadciśnienie, piony)",
        "v1.2 (I5): rezygnacja z szybu rezerwowego C1 (nie mieścił się obok klatki 3,40 m; ściana przy Maz. 19 REI 120 bez otworów) – skrzydło obsługują A1/A2 przez ciągłe korytarze kond. 1–4",
    ]
    r["C"]["uklad_sd"] = {k: ring_uv(g) for k, g in T.C_CELLS.items()}
    r["C"]["uklad_en"] = {k: ring_en(g, sd2en) for k, g in T.C_CELLS.items()}
    r["C"]["klatka"] = klatka_json(T.resC, "spocznik kondygnacyjny parteru na końcu przeciwnym niż na −1 i 1–4 (przedsionek wzdłuż całej klatki)")
    kA, kB = cA["klatka_A"], cB["klatka_B"]
    r["odleglosc_klatek_A_B_m"] = round(kA.centroid.distance(kB.centroid), 1)
    r["odleglosc_klatek_A_B_uwaga"] = (f"między środkami klatek {kA.centroid.distance(kB.centroid):.1f} m (v1.1: 20,0); najmniejsza między obudowami "
                                       f"{kA.distance(kB):.2f} m – sposób pomiaru „2 klatki ≥ 15 m” (MDS −2, rozp. 2025 poz. 932 § 6) do potwierdzenia")

    # ------------------------------------------------------------------------------- parter, podziemie, bilans
    for z in d["parter"]["wieza"]:
        if z.get("strefa") == "Trzon A":
            z["uv"] = [8.3, 11.85, 15.5, 20.85]
    for z in d["parter"]["segment"]:
        if "BESS" in z.get("strefa", ""):
            z["strefa"] = z["strefa"].replace("BESS 150 kWh 11", "BESS 100 kWh 11")
    d["podziemie"]["wymagane_MPZP"] = {
        "PU_m2": round(C.PU12, 2), "PU_gastronomia_m2": 88.47, "wymagane": C.REQ, "odczyt_ostrozny": C.REQ_CONS,
        "wzor": f"12/1000 × (PU − PU_gastr.) + 6/1000 × PU_gastr. = {12 / 1000 * (C.PU12 - 88.47) + 6 / 1000 * 88.47:.2f} → {C.REQ}".replace(".", ","),
    }
    d["podziemie"]["MDS"]["wyjscia"] = ("−2: klatki A, B (środki klatek 19,8 m; obudowy 13,95 m – pomiar do potwierdzenia); −1: klatka C (bieg 1,60 m), "
                                        "rampa, szyb wyjścia zapasowego (91,75; 32,00) + tunel 7,6 m")
    b = d["bilans"]
    b["PC_nadziemna_m2"] = C.PC_nad12
    b["PU_m2"] = round(C.PU12, 2)
    b["PU_definicja"] = ("PN-ISO 9836 – pomieszczenia kategorii PU (model pomieszczeń, F.15.A: 8 850,37 m²) skorygowane o kondygnację S-3 "
                         f"({C.dPU:+.2f} m²: _v12_koszt.py [K0]); bez RU, US, PG")
    b["koszt_mln_netto"] = round(C.RESULT["total"], 2)
    q = dict(C.km.REF)
    q.update(C.RESULT["P"])
    b["koszt_model_F14B_mid_mln"] = round(C.km.compute(q, "mid")["total"] / 1e6, 1)
    b["koszt_roboty_KS_mln"] = round(C.RESULT["works_ks"], 2)
    b["rezerwa_proc"] = 5
    b["rezerwa_mln"] = round(C.RESULT["rez"], 2)
    b["zapas_do_limitu_mln"] = round(C.RESULT["zapas"], 2)
    pc = C.RESULT["P"]["A_nad"] + C.RESULT["P"]["A_pod"]
    b["zl_m2_PC"] = round(C.RESULT["total"] * 1e6 / pc)
    b["zl_m2_PU"] = round(C.RESULT["total"] * 1e6 / C.PU12)
    b["koszt_wejscie_modelu"] = "docs/20_koncepcja/_rewizja_koszt_wejscie_v1_2.json"
    b["dzwignie_v1_2"] = C.RESULT["chosen"]

    # ------------------------------------------------------------------------------- kamery W7, W8
    for cam in d["kamery"]:
        if cam["id"] == "W7":
            cam["nastroj"] = ("początek błękitnej godziny; z holu dźwigów A1/A2 (drzwi pn.) ku pustce 2-kond. NW, schodom reprezentacyjnym "
                              "i oknom na pl. Społeczny i wieże katedry")
        if cam["id"] == "W8":
            cam["nastroj"] = ("światło dzienne z łuku za kamerą (za 4. rzędem, R ≈ 11 m od mównicy), prezydium przy pełnej ścianie pd.; "
                              "47 stanowisk w 4 rzędach (4 dla wózków), galeria zach. z balustradą szklaną i publicznością")
    return d


def validate(d):
    ok = True
    A_zone = Polygon(SITE["granice"]["wydzielenie_A_mpzp"]["pts"])
    W = Polygon(d["bryly"][0]["obrys_ccw"])
    M = Polygon(d["bryly"][1]["obrys_ccw"])
    SEG = Polygon(d["bryly"][2]["obrys_ccw"])
    print("[W1] JSON: serializacja i ponowne wczytanie …", end=" ")
    json.loads(json.dumps(d, ensure_ascii=False))
    print("OK")
    print("[W2] Wielokąty S-3 (obrys_en, obrys_uv): poprawność, w obrysie wieży, w strefie A, uv ↔ en")
    ks = d["kondygnacja_sejmiku"]
    bad, out_w, out_a, mism = [], [], [], []
    polys = {"S": {}, "ANT": {}}
    polys_uv = {"S": {}, "ANT": {}}
    dmax = 0.0
    for grp, lvl in (("pomieszczenia", "S"), ("antresola_pomieszczenia", "ANT")):
        for kk, v in ks[grp].items():
            gs_en = [Polygon(rg) for rg in v["obrys_en"]]
            gs_uv = [Polygon(rg) for rg in v["obrys_uv"]]
            g = unary_union(gs_en)
            if not all(x.is_valid for x in gs_en + gs_uv) or g.area <= 0:
                bad.append(kk)
            if g.difference(W.buffer(0.002)).area > 1e-4:
                out_w.append(kk)
            if g.difference(A_zone.buffer(0.002)).area > 1e-4:
                out_a.append(kk)
            guv = unary_union(gs_uv)
            g_en_from_uv = unary_union([Polygon([uv2en(x, y) for x, y in rg]) for rg in v["obrys_uv"]])
            sd = g_en_from_uv.symmetric_difference(g).area           # różnica z zaokrąglenia współrzędnych en do 1 mm
            dmax = max(dmax, sd / max(g.length, 1e-9))
            if abs(guv.area - v["pow_m2"]) > 0.02 or abs(g.area - v["pow_m2"]) > 0.05 or sd > 0.002 * g.length:
                mism.append((kk, round(guv.area, 2), round(g.area, 2), v["pow_m2"], round(sd, 4)))
            polys[lvl][kk] = g
            polys_uv[lvl][kk] = guv
    print(f"     pomieszczeń S {len(polys['S'])}, ANT {len(polys['ANT'])}; niepoprawne {bad or 'brak'}; poza wieżą {out_w or 'brak'};"
          f" poza strefą A {out_a or 'brak'}; niezgodne uv/en/pow {mism or 'brak'}"
          f" (maks. odchyłka en–uv {dmax * 1000:.2f} mm średnio na obwodzie – zaokrąglenie do 1 mm)")
    ok &= not (bad or out_w or out_a or mism)
    print("[W3] Nakładanie pomieszczeń S-3 – dokładnie w uv (> 0,0001 m²) i w en (> 0,01 m² – szum zaokrąglenia do 1 mm)")
    for lvl in ("S", "ANT"):
        for frame, D, tol in (("uv", polys_uv[lvl], 1e-4), ("en", polys[lvl], 1e-2)):
            items = list(D.items())
            if lvl == "ANT":
                items += [("C-A", Polygon(d["rdzenie"]["A"]["obrys_" + frame])), ("C-B", Polygon(d["rdzenie"]["B"]["obrys_" + frame]))]
            ov = [(items[i][0], items[j][0], round(items[i][1].intersection(items[j][1]).area, 4))
                  for i in range(len(items)) for j in range(i + 1, len(items)) if items[i][1].intersection(items[j][1]).area > tol]
            mx = max((items[i][1].intersection(items[j][1]).area for i in range(len(items)) for j in range(i + 1, len(items))), default=0)
            print(f"     {lvl} ({frame}): {ov if ov else 'brak'} (maks. styk {mx:.4f} m²)")
            ok &= not ov
    print("[W4] Rdzenie: poprawność i położenie (A, B w wieży i strefie A; C w skrzydle; T w segmencie); komórki w obrysach")
    for kk, host in (("A", W), ("B", W), ("C", M), ("T", SEG)):
        g = Polygon(d["rdzenie"][kk]["obrys_en"])
        inside = g.difference(host.buffer(0.002)).area < 1e-4
        inA = g.difference(A_zone.buffer(0.002)).area < 1e-4 if kk in ("A", "B") else None
        print(f"     {kk}: valid={g.is_valid}, CCW={g.exterior.is_ccw}, pole {g.area:.2f} m², w bryle {inside}" + (f", w strefie A {inA}" if inA is not None else ""))
        ok &= g.is_valid and inside and (inA is not False)
    for kk in ("A", "B"):
        host = Polygon(d["rdzenie"][kk]["obrys_uv"])
        cells = [Polygon(x) for x in d["rdzenie"][kk]["uklad_uv"].values()]
        okc = all(c.is_valid and c.within(host) for c in cells) and \
            all(cells[i].intersection(cells[j]).area < 1e-6 for i in range(len(cells)) for j in range(i + 1, len(cells)))
        print(f"     komórki {kk}: {len(cells)} – w obrysie i bez nakładania: {okc}")
        ok &= okc
    cellsC = [Polygon(x) for x in d["rdzenie"]["C"]["uklad_en"].values()]
    okC = all(c.within(Polygon(d["rdzenie"]["C"]["obrys_en"]).buffer(0.002)) for c in cellsC)
    print(f"     komórki C (en): w obrysie trzonu C: {okC}")
    ok &= okC
    # S-3 pomieszczenia vs trzony (S): kontrola, że C-A/C-B w JSON S-3 = rdzenie
    for kk, rk in (("C-A", "A"), ("C-B", "B")):
        g1 = Polygon(ks["pomieszczenia"][kk]["obrys_en"][0])
        g2 = Polygon(d["rdzenie"][rk]["obrys_en"])
        print(f"     {kk} (S-3) ≡ rdzenie.{rk}: różnica {g1.symmetric_difference(g2).area:.4f} m²")
        ok &= g1.symmetric_difference(g2).area < 1e-3
    print("[W5] Sumy powierzchni")
    bl = ks["bilans"]
    s_sum = bl["pomieszczenia_S_m2"] + bl["komunikacja_S_m2"] + bl["trzony_m2"] + bl["sciany_wewn_m2"]
    rooms_S = sum(v["pow_m2"] for v in ks["pomieszczenia"].values())
    print(f"     poziom S: pomieszczenia {bl['pomieszczenia_S_m2']} + komunikacja {bl['komunikacja_S_m2']} + trzony {bl['trzony_m2']} + ściany"
          f" {bl['sciany_wewn_m2']} = {s_sum:.2f} ≟ wnętrze {bl['wnetrze_S_m2']} (Δ {s_sum - bl['wnetrze_S_m2']:+.2f}); suma poligonów S z trzonami"
          f" {rooms_S:.2f} + ściany {bl['sciany_wewn_m2']} = {rooms_S + bl['sciany_wewn_m2']:.2f}")
    ok &= abs(s_sum - bl["wnetrze_S_m2"]) < 0.1 and abs(rooms_S + bl["sciany_wewn_m2"] - bl["wnetrze_S_m2"]) < 0.1
    ant = sum(v["pow_m2"] for v in ks["antresola_pomieszczenia"].values())
    print(f"     antresola: suma pomieszczeń {ant:.2f} ≟ antresola.pow_m2 {ks['antresola']['pow_m2']} ≟ bilans {bl['antresola_m2']};"
          f" radni {ks['antresola']['czesc_radnych_m2']} + publiczność {ks['antresola']['czesc_publiczna_m2']}"
          f" = {ks['antresola']['czesc_radnych_m2'] + ks['antresola']['czesc_publiczna_m2']:.2f}")
    ok &= abs(ant - ks["antresola"]["pow_m2"]) < 0.05 and abs(ks["antresola"]["czesc_radnych_m2"] + ks["antresola"]["czesc_publiczna_m2"] - ant) < 0.05
    kond = {k["kondygnacja"]: k for k in d["kondygnacje"]}
    pc_parts = {"P": 2005.8, "1–4": 4 * 2162.9, "5, 6, S": 3 * 1145.8, "antresola": ks["antresola"]["pow_m2"]}
    pc_sum = round(sum(pc_parts.values()), 1)
    print(f"     PC nadziemna: {' + '.join(f'{k} {v:.1f}' for k, v in pc_parts.items())} = {pc_sum} ≟ bilans {d['bilans']['PC_nadziemna_m2']}")
    ok &= abs(pc_sum - d["bilans"]["PC_nadziemna_m2"]) < 0.06
    prog = sum(v["pow_m2"] for k, v in {**ks["pomieszczenia"], **ks["antresola_pomieszczenia"]}.items()
               if k.startswith(("SWD", "PHS", "PP", "IT")))
    print(f"     program S-3 (SWD + PHS.05 + PP.06 + IT.02): {prog:.2f} ≟ bilans.projekt_suma_m2 {bl['projekt_suma_m2']}")
    ok &= abs(prog - bl["projekt_suma_m2"]) < 0.05
    print("[W6] MPZP i rzędne – bez zmian wobec wejścia")
    same_b = json.dumps([x["dach"] for x in d["bryly"]], sort_keys=True) == json.dumps([x["dach"] for x in K0["bryly"]], sort_keys=True)
    keys = ("posadzka_wzgl", "posadzka_npm", "wysokosc_kondygnacji", "strop_nad", "dach", "plyta_denna")
    same_k = all(json.dumps({kk: a.get(kk) for kk in keys}, sort_keys=True) == json.dumps({kk: b_.get(kk) for kk in keys}, sort_keys=True)
                 for a, b_ in zip(d["kondygnacje"], K0["kondygnacje"]))
    same_o = json.dumps([x["obrys_ccw"] for x in d["bryly"]]) == json.dumps([x["obrys_ccw"] for x in K0["bryly"]])
    dach = d["bryly"][0]["dach"]
    print(f"     dachy brył bez zmian: {same_b}; rzędne kondygnacji bez zmian: {same_k}; obrysy brył bez zmian: {same_o}")
    print(f"     wieża: najniższy pkt pokrycia {dach['najnizszy_pkt_pokrycia']['npm']} m n.p.m. = {dach['najnizszy_pkt_pokrycia']['nad_najwyzszym_terenem_A']} m"
          f" ≥ 35 (zapas {dach['najnizszy_pkt_pokrycia']['zapas']}); attyka {dach['attyka']['npm']} = {dach['attyka']['nad_najnizszym_terenem_A']} m ≤ 45;"
          f" antresola +30,90 i spód rusztu +34,15 w kubaturze wieży (S 8,90 m bez zmian)")
    ok &= same_b and same_k and same_o
    print("[W7] Trzony I5: klatki A, B, C mieszczą biegi na wszystkich kondygnacjach")
    for kk in ("A", "B", "C"):
        kl = d["rdzenie"][kk]["klatka"]["kondygnacje"]
        okk = all(x["wymagana_dl_klatki_m"] <= (5.80 if kk != "B" else 6.64) + 1e-9 and x["h_cm"] <= 17.5 + 1e-9 and
                  max(x["stopnie_w_biegach"]) <= 17 and x["przeswit_m"] >= 2.2 for x in kl)
        print(f"     {kk}: {len(kl)} przejść kondygnacyjnych, biegi {sorted(set(x['biegi'] for x in kl))}, maks. wymagana długość"
              f" {max(x['wymagana_dl_klatki_m'] for x in kl):.2f} m, min. prześwit {min(x['przeswit_m'] for x in kl):.2f} m → {okk}")
        ok &= okk
    print("WALIDACJA:", "OK" if ok else "BŁĘDY")
    return ok


def main():
    d = build()
    print("klucze najwyższego poziomu: usunięte", set(K0) - set(d), "dodane", set(d) - set(K0))
    print("kondygnacja_sejmiku – klucze:", sorted(d["kondygnacja_sejmiku"]), "(usunięte:",
          sorted(set(K0["kondygnacja_sejmiku"]) - set(d["kondygnacja_sejmiku"])), ")")
    ok = validate(d)
    txt = json.dumps(d, ensure_ascii=False, indent=1)
    if "--zapisz" in sys.argv:
        if not ok:
            print("NIE zapisano (walidacja z błędami)")
            return 1
        open(OUT, "w", encoding="utf-8").write(txt + "\n")
        print("zapisano", os.path.relpath(OUT, ROOT), len(txt), "B; meta.wersja =", d["meta"]["wersja"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
