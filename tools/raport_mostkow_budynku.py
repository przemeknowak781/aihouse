"""Raporty Markdown zestawienia mostków budynku (wywoływane z tools/mostki_budynku.py): zestawienie_HTB.md
i REKOMENDACJE.md. Dane wejściowe — słownik `dane` (zestawienie_mostkow.json)."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

SYM = {"OK": "✓", "UWAGA": "!", "BRAK": "✗"}
PROG = 0.03       # ψ_oi „wyraźnie gorsze” od dobrej praktyki: > dobra praktyka + 0,03 W/(m·K) [ZAŁ]


def f(x, n=3, znak=False):
    if x is None:
        return "—"
    s = f"{x:+.{n}f}" if znak else f"{x:.{n}f}"
    return s.replace(".", ",").replace("-", "−")


def _htb(dane):
    """Wiersze H_TB: (id, para, ψ, L, b, ψ·L·b, źródło L) + sumy."""
    b_u = float(dane.get("b_u", 0.8))
    wiersze, s_e, s_u, s_m = [], 0.0, 0.0, 0.0
    for r in dane["wezly"]:
        L = r["L_geo"] if r["L_geo"] is not None else (r["L_model_czesc"] or 0.0)
        zr = "geometria" if r["L_geo"] is not None else "model"
        pary = r["pary"] or {}
        pie = next((v for k, v in pary.items() if set(k.split("-")) == {"i", "e"}), None)
        piu = next((v for k, v in pary.items() if set(k.split("-")) == {"i", "u"}), None)
        if pie is None and piu is None and r["psi_oi"] is not None:
            pie = {"psi_oi": r["psi_oi"]}
        if pie is not None:
            wiersze.append((r["id"], "i–e", pie["psi_oi"], L, 1.0, pie["psi_oi"] * L, zr))
            s_e += pie["psi_oi"] * L
        if piu is not None:
            wiersze.append((r["id"], "i–u", piu["psi_oi"], L, b_u, piu["psi_oi"] * L * b_u, zr))
            s_u += piu["psi_oi"] * L * b_u
        if r["L_model_czesc"] is not None and r["psi_oi"] is not None:
            s_m += r["psi_oi"] * r["L_model_czesc"]
    s_chi = sum(c["chi"] * c["n"] for c in dane["chi"])
    return wiersze, s_e, s_u, s_chi, s_m


def zestawienie_md(m, dane) -> str:
    rows = dane["wezly"]
    wiersze, s_e, s_u, s_chi, s_m = _htb(dane)
    b_u = float(dane.get("b_u", 0.8))
    L = [f"# Mostki cieplne — zestawienie ψ·L → H_TB, ciągłość „4 linii” (Dom LAMELA)", "",
         f"Model: `model/{dane['model']}` (stan na {_dt.date.today().isoformat()}); karty węzłów, mapy temperatur i "
         "metoda: [`katalog_mostkow.md`](katalog_mostkow.md), szczegóły: [`szczegoly_obliczen.md`]"
         "(szczegoly_obliczen.md), rekomendacje: [`REKOMENDACJE.md`](REKOMENDACJE.md). Wygenerowano: "
         "`PYTHONPATH=src python3 tools/mostki_budynku.py`.", "",
         "**Zakres:** wszystkie wpisy sekcji `wezly` modelu (węzły liniowe — symulacja 2D PN-EN ISO 10211, węzły "
         "złożone rozdzielone na podwęzły a/b/c wg geometrii) + węzły spoza sekcji wykryte w geometrii (WZ-X…: dach – "
         "ściana wyższej kondygnacji) + mostki punktowe χ (konsole, kotwy, przejścia — wartości deklarowane/typowe).",
         "", "## 1. Węzły — ψ, f_Rsi, ciągłość 4 linii", "",
         "f_Rsi,min = 0,72 (WT 2021 zał. 2 pkt 2.2.1; PN-EN ISO 13788 — kryterium pleśni, R_si = 0,25). 4 linie: "
         "**I** izolacja cieplna, **H** hydroizolacja / ochrona przed wodą, **S** szczelność powietrzna, "
         "**P** paroizolacja / kontrola pary (✓ ciągłość zachowana, ! uwaga, ✗ brak). ψ_oi — system wymiarów "
         "wewnętrznych całkowitych (H_TB); odniesienia: wartość domyślna PN-EN ISO 14683 / dobra praktyka "
         "(`fizyka.mostki.PSI_DOMYSLNE`, [NZW]).", "",
         "| węzeł | nazwa | ψ_e | ψ_oi | ψ_oi dom. / dobra pr. | f_Rsi | ocena | I | H | S | P | ciągłość |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        o = r["linie4"]
        ref = r["ref"]
        pary = r["pary"] or {}
        extra = "; ".join(f"ψ_{k.replace('-', '')} = {f(v['psi_oi'], znak=True)}" for k, v in pary.items()
                          if set(k.split("-")) != {"i", "e"})
        L.append(f"| {r['id']} | {r['nazwa'][:95]}{(' (' + extra + ')') if extra else ''} | {f(r['psi_e'], znak=True)} | "
                 f"**{f(r['psi_oi'], znak=True)}** | {f(ref[0], 2) + ' / ' + f(ref[1], 2) if ref else '—'} | "
                 f"{f(r['f_rsi'])} {'✓' if (r['f_rsi'] or 0) >= 0.72 else '✗'} | {r['ocena']} | "
                 + " | ".join(SYM[o[k][0]] for k in "IHSP") + f" | {o['ciaglosc'][:160]} |")
    L += ["", "Pozycje „!/✗” 4 linii — opis w kolumnie „ciągłość” i w [`REKOMENDACJE.md`](REKOMENDACJE.md); pełne "
          "listy kontrolne wody i wilgoci — karty w [`katalog_mostkow.md`](katalog_mostkow.md).", ""]
    # długości
    L += ["## 2. Długości mostków liniowych — geometria modelu ↔ pole `dlugosc` sekcji `wezly`", "",
          "Długości policzono z geometrii (obrysy kondygnacji, dachy, płyty wspornikowe, stropy, ściany, otwory, "
          "pomieszczenia — próbkowanie krawędzi co 0,125 m, klasyfikacja każdego odcinka do JEDNEGO węzła: attyka / "
          "attyka z okapem / płyta wspornikowa / dach–ściana wyższa / strop pośredni / cokół / próg). Różnice wobec "
          "modelu wynikają głównie z podwójnego liczenia odcinków w `dlugosc` (np. WZ-01 zawiera odcinki z płytą "
          "PL-3 liczone też w WZ-06; WZ-05 i WZ-07 — krawędź A′; WZ-08 zawiera progi WZ-11T; WZ-10 — połączenia dachów "
          "D2/D3 ze ścianami P2 liczone dwukrotnie).", "",
          "| węzeł | L model [m] | L geometria [m] | Δ [m] | sposób liczenia (geometria) |", "|---|---|---|---|---|"]
    for r in rows:
        dm = r["L_model"]
        dg = r["L_geo"]
        L.append(f"| {r['id']} | {f(dm, 2) if dm is not None else '— (spoza sekcji)'} | {f(dg, 2)} | "
                 f"{f((dg or 0) - (r['L_model_czesc'] or 0), 2, True) if dm is not None and dg is not None else '—'}"
                 f" | {r['L_geo_opis'][:170]} |")
    L += ["", "Dla węzłów złożonych (podwęzły a/b/c) „L model” to długość całego wpisu, a Δ liczono względem części "
          "przypisanej proporcjonalnie do geometrii.", ""]
    # H_TB
    L += ["## 3. H_TB = Σ ψ_oi·l + Σ χ (PN-EN ISO 14683 / PN-EN ISO 13789)", "",
          f"Połączenia z garażem nieogrzewanym: para i–u × b_u = {f(b_u, 2)} (θ_u z bilansu modułu energii: "
          "−10,6 °C przy n_u = 1,0 h⁻¹ → b_u ≈ 0,81; przyjęto 0,80) — składnik H_U; para u–e (obudowa garażu) "
          "nie wchodzi do H_TB budynku.", "",
          "| węzeł | para stref | ψ_oi [W/(m·K)] | l [m] | b | ψ·l·b [W/K] | źródło l |", "|---|---|---|---|---|---|---|"]
    for w in wiersze:
        L.append(f"| {w[0]} | {w[1]} | {f(w[2], znak=True)} | {f(w[3], 2)} | {f(w[4], 2)} | {f(w[5], 2, True)} | {w[6]} |")
    L += ["", "| mostek punktowy | n [szt.] | χ [W/K] | n·χ [W/K] | liczba | źródło χ |", "|---|---|---|---|---|---|"]
    for c in dane["chi"]:
        L.append(f"| {c['id']} — {c['nazwa'][:70]} | {f(c['n'], 0)} | {f(c['chi'], 3)} | {f(c['n'] * c['chi'], 3)} | "
                 f"{c['opis_n']} | {c['zrodlo'][:90]} |")
    tot = s_e + s_u + s_chi
    L += ["", f"**H_TB (do zewnętrza, ψ_oi·l z geometrii) = {f(s_e, 2)} W/K**; połączenia z garażem "
              f"(ψ_iu·l·b_u) = {f(s_u, 2)} W/K; mostki punktowe Σ χ = {f(s_chi, 2)} W/K → "
              f"**H_TB,całk. = {f(tot, 2)} W/K**.", "",
          f"Dla porównania: Σ ψ_oi·l z długościami pola `dlugosc` modelu (katalog, bez χ, bez b_u) = {f(s_m, 2)} W/K; "
          "H_TB z wartości domyślnych Ψ (PN-EN ISO 14683) w module energii = 137,6 W/K "
          "(`docs/20_koncepcja/weryfikacja_koncepcji.md`, tab. EP). Wartości symulowane obniżają H_TB kilkukrotnie — "
          "do obliczeń EP (moduł `energia`) przekazać `wyniki_mostki.json` (ψ) z długościami z tej tabeli.", "",
          "**Ograniczenia:** 2D (mostki liniowe); χ — dane przykładowe (konsole lamel wg `wyroby_przykladowe.yaml`, "
          "kotwy/przejścia wg `fizyka.mostki.CHI_DOMYSLNE` [NZW]) — do zastąpienia deklaracjami (ETA) lub obliczeniem "
          "3D (PN-EN ISO 10211 model 3D); łączniki termoizolacyjne i profile progowe — dane przykładowe; "
          "ramy okien jako materiał zastępczy (λ_eq z U_f); warstwy powietrza wentylowane pominięte (R_se = 0,04 — "
          "wariant ostrożny); wierzch płyt wspornikowych zrównany ze stropem (konwencja audytu A2 K-1)."]
    return "\n".join(L) + "\n"


def _wywiniecia(m) -> list[tuple]:
    """(dach, korona attyki, max wierzch warstw dachu przy attyce, wys. wywinięcia min.) — z geometrii modelu."""
    from lamela.obliczenia.mostki2d.zestawienie import poziomy_dachu
    out = []
    for d in m.dachy():
        att = d.get("attyka") or {}
        if not att:
            continue
        p = m.przegroda(d["przegroda"])
        kor = float(d["plyta"]["wierzch"]) + p.d_nad_konstr() + float(att.get("wys_nad_pokryciem", 0.0))
        zmax = max(poziomy_dachu(m, d, xy)["wierzch"] for xy in d["obrys"])
        out.append((d["id"], kor, zmax, kor - zmax))
    return out


def rekomendacje_md(m, dane) -> str:
    rows = {r["id"]: r for r in dane["wezly"]}
    war = dane.get("warianty") or {}
    fmin = min((r["f_rsi"], r["id"]) for r in dane["wezly"] if r["f_rsi"] is not None)
    L = ["# REKOMENDACJE — mostki cieplne, ciągłość 4 linii, odprowadzenie wody (Dom LAMELA)", "",
         "Rekomendacje zmian projektu wynikające z katalogu mostków (symulacja 2D PN-EN ISO 10211) i kontroli detali. "
         "**Modelu nie zmieniano** — zmiany do wprowadzenia w parametrach `tools/buduj_model.py` przez zespół modelu. "
         "Warianty policzono tym samym solverem (`tools/mostki_budynku.py`, funkcja `warianty`).", "",
         f"**f_Rsi:** wszystkie węzły spełniają f_Rsi ≥ 0,72 (WT zał. 2 pkt 2.2.1 / PN-EN ISO 13788) — "
         f"minimum {f(fmin[0])} w węźle {fmin[1]}." if fmin[0] >= 0.72 else
         f"**f_Rsi:** węzeł {fmin[1]} NIE spełnia f_Rsi ≥ 0,72 ({f(fmin[0])}) — zmiana obowiązkowa.", ""]
    # A — ψ
    L += ["## A. Węzły z ψ wyraźnie gorszym od wytycznych albo z przerwaną linią izolacji", "",
          f"Kryterium: ψ_oi > dobra praktyka + {f(PROG, 2)} W/(m·K) [ZAŁ] albo ocena „ZŁY” (izolacja przerwana "
          "konstrukcją). Dobra praktyka / wartość domyślna — `fizyka.mostki.PSI_DOMYSLNE` [NZW].", "",
          "| węzeł | ψ_oi | dobra pr. | ocena | wariant policzony | ψ_oi wariantu | f_Rsi wariantu |",
          "|---|---|---|---|---|---|---|"]
    flag = []
    for r in dane["wezly"]:
        ref = r["ref"]
        gorszy = ref is not None and r["psi_oi"] is not None and r["psi_oi"] > ref[1] + PROG
        if gorszy or r["ocena"] in ("ZŁY", "NIE SPEŁNIA"):
            flag.append(r)
            vs = war.get(r["id"]) or [("— (patrz opis)", None, None, {})]
            for j, v in enumerate(vs):
                L.append(f"| {r['id'] if j == 0 else ''} | {f(r['psi_oi'], znak=True) if j == 0 else ''} | "
                         f"{f(ref[1], 2) if (ref and j == 0) else ''} | {r['ocena'] if j == 0 else ''} | {v[0]} | "
                         f"{f(v[1], znak=True)} | {f(v[2])} |")
    L += [""]
    txt = {
        "wspornik": "Płyta wspornikowa: łącznik termoizolacyjny z modułem izolacyjnym **120 mm** (w warstwie ocieplenia "
                    "20 cm) i λ_eq ≤ 0,08 W/(m·K) wg ETA (zamiast przykładowego 80 mm / 0,09) — ψ spada do poziomu "
                    "dobrej praktyki; łącznik w strefie izolacji, płyta stropu do lica konstrukcji (audyt A2 K-1).",
        "strop_zewn_krawedz": "Krawędź stropu nad powietrzem z płytą PL-2: jak wyżej — łącznik 120 mm; belki "
                              "odwrócone B3/B4/B5 w linii ściany obłożyć ociepleniem ściany na całą wysokość (wełna "
                              "elewacji A ciągła do podsufitki); podsufitka jedna płaszczyzna pod wspornikiem A i pasem "
                              "zach. PL-2 (audyt A2 I-5) — ψ < dobra praktyka możliwe dopiero przy łączniku 120 mm.",
        "attyka": "Attyka z okapem PL-3: łącznik 120 mm **oraz** nośny blok termoizolacyjny u podstawy attyki "
                  "(element attykowy z ETA / szkło piankowe klasy nośności wg PT-K, h ≈ 15 cm) — ψ ≈ dobra praktyka "
                  "(wariant policzony); alternatywa: attyka lekka (rama drewniana/stalowa z przekładką) na płycie "
                  "ocieplonej z góry.",
        "garaz": "Połączenie z garażem na ciągłej płycie: płyta fundamentowa jest ciągła pod ścianą SWG (XPS tylko "
                 "pod płytą) — ciepło z domu przepływa płytą do posadzki garażu (ψ_iu duże). Zalecane: **XPS ≥ 10 cm "
                 "na płycie pod posadzką garażu** (cała posadzka albo pas ≥ 1,5–2,0 m przy SWG; jastrych garażu "
                 "zbrojony, z dylatacją obwodową) + blok termoizolacyjny w 1. warstwie muru SWG (nośność — PT-K). "
                 "Pod stropem (WZ-09b/c) pas docieplenia SUF-G 1,0 m ogranicza mostek (f_Rsi spełnione); ocena „ZŁY” "
                 "wynika z testu ołówka (płyta ŻB dochodzi do przestrzeni nieogrzewanej) — akceptowalne przy ψ_ie "
                 "≤ 0,10; alternatywa: docieplenie całego spodu stropu garażu przy ścianach E i 2 pasem 1,5 m."}
    uzyte = set()
    for r in flag:
        t = "garaz" if r["typ"] == "garaz" else r["typ"]
        if t in txt and t not in uzyte:
            uzyte.add(t)
            L.append(f"* **{', '.join(x['id'] for x in flag if (('garaz' if x['typ'] == 'garaz' else x['typ']) == t))}** — {txt[t]}")
    L += [""]
    return "\n".join(L)


def rekomendacje_woda_md(m, dane) -> str:
    from shapely.geometry import Polygon
    L = ["## B. Woda, hydroizolacja, detale (weryfikacja koncepcji / audyt A2 — uwzględnione w detalach PT-AR-D)", ""]
    # B1 — okapy
    L += ["### R-W1. Odwodnienie płyt wysuniętych (okapy, daszek)", "",
          "Płyty mają w modelu spadek 2 % od budynku i okapnik, bez odbioru wody — linia kapania wypada nad tarasem, "
          "podestem wejścia i podestem drzwi gospodarczych (ryzyko oblodzenia, zachlapania przeszkleń HS i cokołu). "
          "Zalecenie: **spadek ≥ 2 % od budynku do czoła, rynna ukryta za blendą czołową** (korytko ze stali "
          "nierdzewnej / blachy powlekanej 0,7 mm, spadek 0,5 % do wylotu), wyloty do rur spustowych przy narożach "
          "i słupach, rury do kanalizacji deszczowej KD → zbiornik retencyjny; kapinos (okapnik ≥ 3 cm) na obróbce "
          "blendy i na podsufitce. Uzasadnienie: linia kapania przy wejściu i nad tarasem użytkowym jest "
          "niedopuszczalna funkcjonalnie (brief §9.3), a odwodnienie liniowe pod linią kapania na tarasie z deski na "
          "wspornikach wymagałoby przerwania nawierzchni i nie chroni podestu T2 przed oblodzeniem; rynna ukryta nie "
          "narusza łącznika termoizolacyjnego (mocowana do czoła płyty za blendą, poza strefą izolacji).", "",
          "| płyta | pow. [m²] | Q = r·A·C [l/s] (r = 0,030 l/(s·m²), C = 1,0) | pod linią kapania | zalecenie |",
          "|---|---|---|---|---|"]
    tar = [(t["id"], Polygon(t["obrys"]), t.get("uwagi", "")) for t in m.raw.get("tarasy") or []]
    for w in m.wsporniki():
        if not w.get("przegroda"):
            continue
        P = Polygon(w["obrys"])
        pod = [f"{i}" for i, T, _u in tar if T.intersects(P.buffer(0.3))]
        L.append(f"| {w['id']} | {f(P.area, 1)} | {f(0.030 * P.area, 2)} | {', '.join(pod) or 'teren / elewacja'} | "
                 f"rynna ukryta za blendą, spadek 2 % do czoła, RS DN70–DN90 do KD |")
    L += ["", "Obciążenie normowe deszczem r = 300 l/(s·ha) = 0,030 l/(s·m²) [ZAŁ — przyjęcie typowe w PL; wymiarowanie "
          "wg PN-EN 12056-3 w PT instalacji]; rynna 100 mm przy spadku 0,5 % odbiera ≥ 1 l/s — z zapasem.", ""]
    # B2 — przelewy
    L += ["### R-W2. Rzędne przelewów awaryjnych", "",
          "Kryteria: dno przelewu ≥ pokrycie przy wpuście + 0,03 m (W-142; J2 poprawka 5.1: 30–50 mm) i nie niżej niż "
          "pokrycie w miejscu przelewu; górna krawędź otworu ≤ wierzch wywinięć (pokrycie + 0,15 m, DAFA) i poniżej "
          "korony attyki. Pokrycie = wierzch hydroizolacji; grubość izolacji spadkowej d = d_min + spadek × odległość "
          "od wpustu (powierzchnia stożkowa wokół wpustu) [INT].", "",
          "| dach | przelew | dno model | pokrycie przy wpuście | pokrycie w miejscu przelewu | zakres dna | ocena | "
          "zalecane dno |", "|---|---|---|---|---|---|---|---|"]
    for p in dane["przelewy"]:
        L.append(f"| {p['dach']} | {p['opis'][:40]} | {f(p['dno'])} | {f(p['pokrycie_wpust'])} | "
                 f"{f(p['pokrycie_lok'])} | {f(p['dno_min'])}…{f(p['dno_max'])} | {'✓' if p['ok'] else '✗'} | "
                 f"**{f(p['zalecane'])}** |")
    L += ["", "Wniosek: rzędne przelewów w modelu odnoszą się do pokrycia **średniego** (grubość średnia izolacji "
          "spadkowej), a nie do pokrycia przy wpuście — przy izolacji spadkowej przelewy D2/D3/D4 leżą 0,13–0,23 m nad "
          "pokryciem przy wpuście (spiętrzenie wody ponad dopuszczalne), a przy odniesieniu do pokrycia średniego — "
          "D1 poniżej pokrycia (uwaga weryfikacji A3). Zalecenie: w modelu podać rzędne pokrycia przy wpustach "
          "(pole `rzedna_pokrycia`), dno przelewu = pokrycie przy wpuście + 0,03…0,05 m; przelewy, dla których "
          "pokrycie lokalne jest wyższe niż ten zakres (PA2, PA3, PA5, PA6), przenieść na odcinki attyki bliżej "
          "wpustów (najniższa strefa pola) albo wykonać w attyce kosz/obniżenie izolacji spadkowej do rzędnej dna.",
          ""]
    # B3 — wywinięcia
    L += ["### R-W3. Wysokość wywinięć hydroizolacji na attykach (≥ 15 cm ponad warstwę wierzchnią)", "",
          "| dach | korona attyki | max wierzch warstw dachu przy attyce | wywinięcie min. | ocena |", "|---|---|---|---|---|"]
    for d, kor, zmax, h in _wywiniecia(m):
        L.append(f"| {d} | {f(kor)} | {f(zmax)} | {f(h, 2)} m | {'✓' if h >= 0.15 - 1e-3 else '✗ < 0,15'} |")
    L += ["", "Źródło wymagania: Stowarzyszenie DAFA, „Wytyczne do projektowania i wykonywania dachów z izolacją "
          "wodochronną — wytyczne dachów płaskich” (wywinięcie ≥ 15 cm ponad najwyższą warstwę wykończeniową — żwir, "
          "substrat; 12/10 cm dla dachów o większym spadku); zgodnie z DIN 18531 / ZVDH Flachdachrichtlinie "
          "(przywoływane pomocniczo). PN-EN 1991 (oddziaływania na konstrukcje) wysokości wywinięć **nie** określa. "
          "Na D1 w najwyższych narożach pól wywinięcie wynosi dokładnie 15 cm — bez zapasu na tolerancję wykonania "
          "izolacji spadkowej: zalecane podniesienie korony attyki D1 o 5 cm albo obniżenie d_max klinów przy attyce.", ""]
    # B4 — DZ2, podsufitka, konwencja
    L += ["### R-W4. Cokół przy drzwiach DZ2 garażu", "",
          "Weryfikacja koncepcji (§6 A5): cokół 0,14 m przy DZ2 (strona wsch., teren wyższy) < 0,30 m, brak odwodnienia "
          "liniowego." + _dz2_z_modelu(m) + " Zalecenie (detal PT-AR-D-14): odwodnienie liniowe przed progiem DZ2 na "
          "całą szerokość drzwi + 0,15 m "
          "z każdej strony, podłączone do KD-E; nawierzchnia ze spadkiem 2 % od drzwi; uszczelnienie progu taśmą "
          "EPDM / masą KMB wywiniętą ≥ 15 cm na ościeża poza strefę rozbryzgu i połączoną z izolacją przeciwwilgociową "
          "płyty; lokalne obniżenie terenu przy DZ2 (niecka NT-E) tak, by cokół poza drzwiami ≥ 0,30 m "
          "(DIN 18533-1: uszczelnienie cokołu ok. 30 cm, min. 15 cm nad terenem w stanie końcowym).", "",
          "### R-W5. Podsufitka i czoło wspornika bryły A", "",
          "Audyt A2 poz. I-5 / weryfikacja B8: docieplenie spodu ST2Z odkryte, uskok względem spodu PL-2. Zalecenie "
          "(detal PT-AR-D): jedna płaska podsufitka włóknocementowa pod wspornikiem A i pasem zach. PL-2 na rzędnej "
          "spodu SUF-ZEW (spód ST2Z − 0,252 m), czoło PL-2 obudowane blendą do tej rzędnej, wełna 20 cm ciągła od "
          "ściany P1 (ETICS) do czoła, szczelina wentylowana 4 cm z kratką przeciw owadom na obwodzie.", "",
          "### R-W6. Konwencja obrysów płyt (audyt A2 K-1)", "",
          "Stropy i dachy przyciąć do lica warstwy konstrukcyjnej (±0,09 m od osi ścian zewn.), wierzchy płyt "
          "wspornikowych zrównać ze stropem, łącznik termoizolacyjny w strefie izolacji, attyka 0,18 m w osi muru. "
          "Obliczenia mostków i detale PT-AR-D wykonano wg tej docelowej konwencji.", ""]
    return "\n".join(L)


def _dz2_z_modelu(m) -> str:
    """Cokół przy DZ2 z bieżącego modelu (posadzka garażu, teren projektowany TIN 0,6 m przed drzwiami)."""
    try:
        from lamela.views.detale_katalog import teren_projektowany
        o = next(o for o in m.otwory() if o.raw.get("symbol") == "DZ2")
        s_ = o.sciana
        t_ = (s_.p2 - s_.p1) / s_.L
        mid = s_.p1 + t_ * (float(o.raw.get("odl", 0)) + float(o.szer) / 2)
        tz = teren_projektowany(m, mid + s_.n * (1 if s_.wnetrze == "prawa" else -1) * 0.6)
        gar = next(p for p in m.pomieszczenia("P0") if (p.raw or {}).get("rodzaj") == "garaz")
        zf = float(gar.raw.get("rzedna"))
    except Exception:
        return ""
    if tz is None:
        return ""
    return (f" Bieżący model: posadzka garażu {zf:+.2f}, teren projektowany przed DZ2 (TIN) {tz:+.3f} → cokół "
            f"{zf - tz:.2f} m.").replace(".", ",")


def rekomendacje_reszta_md(m, dane) -> str:
    geo = m.raw.get("geotechnika") or {}
    fund = m.fundamenty() or {}
    spod = min((float(e.get("spod", 0)) for e in fund.get("elementy") or []), default=None)
    zwg = geo.get("ZWG")
    dz = (m.dz.raw if getattr(m, "dz", None) is not None else {}) or {}
    dren = [o for o in dz.get("odwodnienia") or [] if "drenaz" in str(o.get("typ", ""))]
    L = ["## C. Drenaż opaskowy", ""]
    if dren:
        d = dren[0]
        L += [f"Decyzja w modelu działki: `{d.get('id')}` — {d.get('opis')} (`dzialka.odwodnienia`; fundamenty: "
              f"„{fund.get('uwagi', '')[:160]}…”). **Detalu drenażu nie opracowano** — detal cokołu PT-AR-D pokazuje "
              "opaskę żwirową, spadek terenu i uszczelnienie strefy cokołu.", ""]
    else:
        L += ["**Brak decyzji o drenażu w modelu działki** — rekomendacja poniżej do wprowadzenia w `dzialka.odwodnienia`.", ""]
    L += ["Uzasadnienie geotechniczne (potwierdzenie decyzji): "
          f"grunt: {(geo.get('grunt') or {}).get('rodzaj', '?')} (niespoisty, przepuszczalny — typowo k ≈ 10⁻⁵…10⁻⁴ m/s "
          f"[NZW]); ZWG {f(zwg, 1) if zwg is not None else '?'} m p.p.t.; najniższe posadowienie "
          f"{f(spod, 2) if spod is not None else '?'} m (względem ±0,00, teren ≈ −0,25…−0,30) → odległość zwierciadła "
          f"od spodu fundamentu ≈ {f(abs((zwg or 0) - (spod or 0) - 0.3), 1)} m, znacznie powyżej podciągania "
          "kapilarnego piasków średnich (rzędu 0,1–0,3 m [NZW]). Obciążenie wodą: wilgoć gruntowa i woda "
          "infiltrująca, niespiętrzająca się → wystarcza izolacja przeciwwilgociowa (membrana SBS na płycie, XPS pod "
          "płytą, uszczelnienie cokołu), drenaż opaskowy nie jest wymagany (brief §9.6). Warunki utrzymania decyzji "
          "(do potwierdzenia w opinii geotechnicznej i projekcie geotechnicznym, W-280…W-282): (1) brak przewarstwień "
          "gruntów spoistych do ok. 2 m pod poziomem posadowienia (ryzyko wody zawieszonej), (2) maksymalny stan ZWG "
          "(wahania sezonowe) ≥ 1,0 m poniżej spodu XPS, (3) spadki terenu ≥ 2 % na 1,5–2 m od budynku — w obecnym "
          "modelu działki 0,2–1,1 % przy licach (weryfikacja §6 A2: dodać punkty projektowane przy cokole), "
          "(4) opaska żwirowa 16/32 na geowłókninie i odwodnienia liniowe przy HS, wejściu, bramie i DZ2. Jeżeli "
          "badania wykażą gliny/pyły lub wodę zawieszoną — drenaż opaskowy DN100 w obsypce filtracyjnej na poziomie "
          "spodu XPS, ze studzienkami kontrolnymi w narożach, odprowadzony do niecki chłonnej (nie do zbiornika wody "
          "deszczowej bez zabezpieczenia przed cofką).", ""]
    L += ["## D. Model — spójność sekcji `wezly`", "",
          "1. Pole `dlugosc` sekcji `wezly` liczy część odcinków podwójnie (WZ-01↔WZ-06, WZ-05↔WZ-07↔WZ-16, "
          "WZ-08↔WZ-11T, WZ-10 — połączenia dach–ściana ×2, WZ-12 — naroża garażu). Zalecenie: długości z "
          "`zestawienie_HTB.md` §2 (geometria, każdy odcinek raz) albo generować je w `buduj_model.py` tą samą "
          "metodą (`mostki2d.zestawienie.dlugosci_geometryczne`).",
          "2. Dodać do sekcji `wezly` węzły wykryte w geometrii: **WZ-X1** (dachy D2/D3 – ściany P2) i **WZ-X2** "
          "(dach D4 nad pasem gospodarczym – ściana P1), typ „dach_sciana” (dziś wliczone do WZ-10 jako strop "
          "pośredni, co zaniża ψ).",
          "3. Rozdzielić WZ-07 na krawędź A′ (ściana lekka na belce B3 z okapem PL-2) i krawędź nad ścianą osi A, "
          "a WZ-09 na: ścianę SWG na płycie fundamentowej, SWG pod dachem zielonym (oś 2) i SWG pod stropem ze ścianą "
          "P1 (oś E) — geometrie różne, ψ różne o rząd wielkości (katalog: podwęzły a/b/c).",
          "4. Materiał WELNA_FAS ma w nazwie „elewacja wentylowana” — solver mostków traktował go jako pustkę "
          "wentylowaną (poprawione w `mostki2d.geometria.material_z_modelu`: tylko materiały-powietrze).", "",
          "## E. Dane do potwierdzenia przed wydaniem PT", "",
          "* Łączniki termoizolacyjne płyt (PL-E, PL-DA, PL-2, PL-3): ETA wybranego wyrobu — λ_eq, grubość modułu "
          "(zalecane 120 mm), ψ i f_Rsi producenta; wartości w obliczeniach są DANYMI PRZYKŁADOWYMI.",
          "* Konsole lamel i ramy C (χ): deklaracja producenta lub obliczenie 3D; profile progowe HS (λ podwaliny).",
          "* Klasa wilgotności pomieszczeń (Glaser — przyjęto klasę 3, PN-EN ISO 13788 zał. A).", ""]
    return "\n".join(L)


def zapisz(out: Path, m, dane) -> None:
    (Path(out) / "zestawienie_HTB.md").write_text(zestawienie_md(m, dane), encoding="utf-8")
    txt = rekomendacje_md(m, dane) + "\n" + rekomendacje_woda_md(m, dane) + "\n" + rekomendacje_reszta_md(m, dane)
    (Path(out) / "REKOMENDACJE.md").write_text(txt, encoding="utf-8")
