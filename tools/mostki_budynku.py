"""Mostki cieplne budynku — katalog kart (tools/katalog_mostkow.py) + zestawienie ψ·L do H_TB z długościami
policzonymi z GEOMETRII modelu, mostki punktowe χ, ocena ciągłości „4 linii” każdego węzła, warianty poprawy
i rekomendacje (bez edycji modelu).

Wyniki (katalog --out):
  katalog_mostkow.md, szczegoly_obliczen.md, WZ-*_karta.png, rys/ — z tools/katalog_mostkow.py (--dodatkowe);
  zestawienie_HTB.md — tabela węzłów (ψ, f_Rsi, 4 linie), długości model ↔ geometria, H_TB, χ;
  REKOMENDACJE.md — węzły niespełniające f_Rsi / z ψ gorszym od wytycznych (warianty policzone), woda i detale;
  zestawienie_mostkow.json — dane dla generatora detali (lamela.views.detale) i modułu energii.

Użycie:
  PYTHONPATH=src python3 tools/mostki_budynku.py [--budynek model/budynek.yaml] [--dzialka model/dzialka.yaml]
      [--out projekt/08_obliczenia/mostki] [--bez-katalogu] [--bez-wariantow]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

SYM = {"OK": "✓", "UWAGA": "!", "BRAK": "✗"}
PROG_WYRAZNIE = 0.03        # [W/(m·K)] ψ_oi „wyraźnie gorsze” od dobrej praktyki: > dobra praktyka + 0,03 [ZAŁ]


def f(x, n=3, znak=False):
    if x is None:
        return "—"
    s = f"{x:+.{n}f}" if znak else f"{x:.{n}f}"
    return s.replace(".", ",").replace("-", "−")


def warianty(m, wezly, wyn, log=print) -> dict:
    """Warianty poprawy węzłów „do poprawy” / „złych”: łącznik 120 mm, blok u podstawy attyki, izolacja posadzki
    garażu + blok w ścianie. Zwraca {id: [(opis, ψ_oi, f_Rsi, ψ_pary)]}."""
    from lamela.obliczenia.mostki2d import geometria as G, katalog_dod as KD, wezly_dod as D
    from lamela.obliczenia.mostki2d.wyniki import oblicz_wezel
    wp = {str(e["id"]): e for e in m.raw.get("wezly") or []}
    L120 = G.Material("LACZNIK_120", 0.08, "Łącznik termoizolacyjny 120 mm, λ_eq = 0,08 W/(m·K)", "#d1495b",
                      zrodlo="[DANE PRZYKŁADOWE – FIKCYJNE] — do zastąpienia wartością z ETA wybranego wyrobu")
    BLOK = G.Material("BLOK_TERM", 0.045, "Blok termoizolacyjny nośny (szkło piankowe / PUR-GF), λ = 0,045",
                      "#e3b04b", zrodlo="[DANE PRZYKŁADOWE – FIKCYJNE]")
    out: dict[str, list] = {}

    def run(w):
        r = oblicz_wezel(w)
        p = r.psi_glowne
        return round(p.psi_oi, 3), round(float(r.f["f_Rsi"]), 3), {f"{q.grupy[0]}-{q.grupy[1]}": round(q.psi_oi, 3)
                                                                   for q in r.psi}
    zle = {i for i, d in wyn.items() if d.get("ocena") in ("DO POPRAWY", "ZŁY", "NIE SPEŁNIA")}
    for w in wezly:
        if w.id not in zle:
            continue
        baza = w.id.rstrip("abcdefgh") if w.id not in wp else w.id
        e = wp.get(baza)
        try:
            if "łącznik" in w.dane or "łącznik" in str(w.dane.get("płyta wspornikowa", "")) or \
                    ("okap" in w.dane and e is not None):
                KD.LACZNIK = (L120, 0.12)
                ws = [x for x, _L in (KD.zbuduj(m, e) or []) if x.id == w.id]
                if ws:
                    out.setdefault(w.id, []).append(("łącznik 120 mm, λ_eq 0,08 (zamiast 80 mm / 0,09)",) + run(ws[0]))
                if w.typ == "attyka" and "okap" in w.dane:
                    wsp = KD.wspornik_z_nazwy(m, e["nazwa"])[0]
                    pl, _r = KD.plyta_pod_wspornikiem(m, wsp)
                    sc = KD._max(KD.sciany_wzdluz(m, __import__("shapely.geometry", fromlist=["Polygon"]).Polygon(
                        wsp["obrys"]), KD.kond_przy(m, float(pl["plyta"]["wierzch"]), "dol")))
                    wv = D.wezel_attyka_wspornik(KD._W(m, sc), KD._W(m, pl["przegroda"]),
                                                 KD._W(m, pl["attyka"]["przegroda"]),
                                                 h_nad_pokryciem=float(pl["attyka"]["wys_nad_pokryciem"]),
                                                 t_wsp=float(wsp["grubosc"]), dy_wsp=0.0, mat_wsp=KD._mat(m, wsp["mat"]),
                                                 wysieg=1.0, lacznik=L120, d_lacznika=0.12, blok_attyki=(BLOK, 0.15),
                                                 id=w.id + "v")
                    out[w.id].append(("łącznik 120 mm + blok termoizolacyjny nośny 15 cm u podstawy attyki",)
                                     + run(wv))
            elif w.typ == "garaz" and "posadzka garażu" in w.dane:
                kg = next(k for k in e["przegrody"] if (KD._typ_p(m, k) or "").startswith("sciana"))
                pd = next(k for k in e["przegrody"] if KD._typ_p(m, k) == "podloga_na_gruncie")
                pg = next((k for k, p in m.przegrody.items() if p.typ == "podloga_na_gruncie" and k != pd
                           and "gara" in (p.nazwa or "").lower()), pd)
                W = KD._W(m, pg)
                ki = G.indeks_konstrukcyjnej(W)
                xps = G.Warstwa(G.material_z_modelu(m, "XPS300") if "XPS300" in m.materialy
                                else G.MATERIALY_DOMYSLNE["XPS"], 0.10)
                W2 = W[:ki] + [xps] + W[ki:]
                for op, blok in (("XPS 10 cm na płycie pod posadzką garażu", None),
                                 ("XPS 10 cm pod posadzką garażu + blok z betonu komórkowego 400 (24 cm) u podstawy "
                                  "ściany", (G.MATERIALY_DOMYSLNE["BET_KOM_400"], 0.24))):
                    wv = D.wezel_garaz_plyta(KD._W(m, kg), KD._W(m, pd), W2, blok=blok, id=w.id + "v")
                    out.setdefault(w.id, []).append((op,) + run(wv))
        except Exception as ex:          # wariant pomocniczy — błąd nie przerywa zestawienia
            log(f"  wariant {w.id}: {type(ex).__name__}: {ex}")
        finally:
            KD.LACZNIK = None
    return out
