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
