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
                # wydanie (V2 N-6): warianty na geometrii modelu — uskok PF1/PF2 i żebro pod SWG (katalog_dod._uskok_zebro);
                # posadzka garażu z modelu (POD-G ma już XPS 10 cm na płycie)
                usk, zeb = KD._uskok_zebro(m, [s for s in m.sciany() if s.przegroda_kod == kg])
                xps = G.material_z_modelu(m, "XPS300") if "XPS300" in m.materialy else G.MATERIALY_DOMYSLNE["XPS"]
                for op, blok, prz in (("bez bloku u podstawy ściany (odniesienie)", None, None),
                                      ("blok z betonu komórkowego 600 (24 cm) u podstawy ściany",
                                       (KD._mat(m, "BET_KOM_600"), 0.24) if "BET_KOM_600" in m.materialy else None, None),
                                      ("nośny blok termoizolacyjny (λ ≤ 0,045, 24 cm) + przerwa termiczna PF2 przy żebrze "
                                       "(XPS 10 cm na grubości płyty)",
                                       (KD._mat(m, "BLOK_TERM"), 0.24) if "BLOK_TERM" in m.materialy else None, (xps, 0.10))):
                    wv = D.wezel_garaz_plyta(KD._W(m, kg), KD._W(m, pd), KD._W(m, pg), blok=blok, id=w.id + "v",
                                             uskok=usk, zebro=zeb, przerwa=prz,
                                             izolacja_czola=bool(e.get("izolacja_czola_uskoku")))
                    out.setdefault(w.id, []).append((op,) + run(wv))
        except Exception as ex:          # wariant pomocniczy — błąd nie przerywa zestawienia
            log(f"  wariant {w.id}: {type(ex).__name__}: {ex}")
        finally:
            KD.LACZNIK = None
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--budynek", default=str(ROOT / "model" / "budynek.yaml"))
    ap.add_argument("--dzialka", default=str(ROOT / "model" / "dzialka.yaml"))
    ap.add_argument("--out", default=str(ROOT / "projekt" / "08_obliczenia" / "mostki"))
    ap.add_argument("--bez-katalogu", action="store_true", help="bez ponownej symulacji (wyniki_mostki.json istnieje)")
    ap.add_argument("--bez-wariantow", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    kod = 0
    if not a.bez_katalogu:
        import katalog_mostkow
        kod = katalog_mostkow.main(["--budynek", a.budynek, "--dzialka", a.dzialka, "--out", str(out), "--dodatkowe"])
    from lamela.model import load_model
    from lamela.obliczenia.mostki2d import zestawienie as Z
    from lamela.obliczenia.mostki2d.karta import psi_odniesienia
    from lamela.obliczenia.mostki2d.katalog import wezly_z_sekcji
    from lamela.obliczenia.mostki2d.katalog_dod import wezly_dodatkowe
    m = load_model(a.budynek, a.dzialka)
    wyn = json.loads((out / "wyniki_mostki.json").read_text(encoding="utf-8"))
    wezly, dl_model, _pom, kody = wezly_z_sekcji(m)
    for w, L in wezly_dodatkowe(m):
        wezly.append(w)
        kody[w.id] = []
    wezly = [w for w in wezly if w.id in wyn]
    geo = Z.dlugosci_geometryczne(m, wezly)
    chi = Z.mostki_punktowe(m)
    cache: dict = {}
    wpisy = {str(e["id"]): e for e in m.raw.get("wezly") or []}
    rows = []
    for w in wezly:
        d = wyn[w.id]
        baza = w.id if w.id in wpisy else w.id.rstrip("abcdefgh")
        kd = [k for k in (wpisy.get(baza, {}).get("przegrody") or []) if k in m.przegrody]
        if not kd:      # węzły dodatkowe — przegrody z danych węzła
            kd = [k for k in m.przegrody if k in w.nazwa]
        o4 = Z.ocena_4_linii(m, w, d, kd, cache)
        ref = psi_odniesienia(w)
        pary = d.get("psi_pary") or {}
        L_g = geo.get(w.id, (None, ""))[0]
        L_m = wpisy.get(baza, {}).get("dlugosc")
        rows.append(dict(id=w.id, nazwa=w.nazwa, typ=w.typ, psi_e=d.get("psi_e"), psi_oi=d.get("psi_oi"),
                         f_rsi=d.get("f_rsi"), ocena=d.get("ocena"), ref=ref, pary=pary, theta=d.get("theta_grup"),
                         L_geo=L_g, L_geo_opis=geo.get(w.id, (None, ""))[1], L_model=L_m,
                         L_model_czesc=dl_model.get(w.id), linie4=o4, przegrody=kd))
    war = {} if a.bez_wariantow else warianty(m, wezly, wyn)
    przel = Z.poziomy_przelewow(m)
    dane = dict(model=str(Path(a.budynek).name), wezly=rows, chi=chi, warianty=war, przelewy=przel,
                b_u=0.8)
    (out / "zestawienie_mostkow.json").write_text(json.dumps(dane, ensure_ascii=False, indent=1, default=str),
                                                  encoding="utf-8")
    import raport_mostkow_budynku as R
    R.zapisz(out, m, dane)
    print(f"→ {out / 'zestawienie_HTB.md'}, {out / 'REKOMENDACJE.md'}, {out / 'zestawienie_mostkow.json'}")
    return kod


if __name__ == "__main__":
    sys.exit(main())
