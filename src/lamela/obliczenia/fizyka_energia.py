"""Komplet obliczeń fizyki budowli i charakterystyki energetycznej dla modelu — raporty Markdown + wykresy PNG.

    PYTHONPATH=src python3 -m lamela.obliczenia.fizyka_energia --budynek model/budynek.yaml --dzialka model/dzialka.yaml \
        --out projekt/08_obliczenia/<katalog> [--psi domyslna|dobra_praktyka] [--wezly-wyniki plik.json] [--bez-zacienienia]

Pliki wynikowe: 00_zestawienie.md, 01_przegrody_U.md, 02_grunt.md, 03_stolarka_g.md, 04_mostki.md,
05_wilgotnosc.md (+ glaser_*.png), 06_ciaglosc_warstw.md, 07_wentylacja.md, 08_obciazenie_cieplne.md,
09_charakterystyka_energetyczna.md (+ bilans_energii.png), 10_analiza_alternatyw.md, wyniki.json.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import numpy as np

from .energia import ep as EP
from .energia.klimat import klimat_miesieczny, opis_zrodla
from .energia.obciazenie_cieplne import obciazenie_cieplne, raport_obciazenie
from .energia.obudowa import oblicz_obudowe, raport_ciaglosc
from .energia.wentylacja import bilans_wentylacji, raport_wentylacja
from .fizyka import kondensacja as KD
from .fizyka import mostki as MB
from .fizyka.grunt import raport_grunt
from .fizyka.okna import raport_okna
from .fizyka.u_przegrody import raport_u, warstwy_przegrody
from .fizyka.warstwy import uwagi_wezla
from .wspolne import PRZYKL, Zalozenia, fmt, fmt_u, ok, tabela_md

ROLE_GLASER = ("sciana_zewn", "dach", "strop_zewn", "sciana_nieogrz", "strop_nieogrz", "strop_nieogrz_gora")


def oblicz_wszystko(m, *, wyniki_symulacji: dict | None = None, wariant_psi: str | None = None,
                    zacienienie: bool = True, klasa_wilgotnosci: int = 3) -> dict:
    """Pełny łańcuch obliczeń dla modelu `lamela.model.Model`. Zwraca słownik wyników (obiekty dataclass)."""
    R: dict = {"zal": {}}
    zU = R["zal"]["U"] = Zalozenia()
    ob = oblicz_obudowe(m, wyniki_symulacji=wyniki_symulacji, wariant_psi=wariant_psi, zacienienie=zacienienie, zal=zU)
    R["obudowa"] = ob
    zW = R["zal"]["went"] = Zalozenia()
    went = bilans_wentylacji(ob.bryla, cfg=ob.cfg, zal=zW)
    R["went"] = went
    zO = R["zal"]["obc"] = Zalozenia()
    obc = obciazenie_cieplne(ob, went, zal=zO)
    R["obc"] = obc
    # wilgotność — f_Rsi i Glaser
    fr = KD.f_rsi_min(20.0, phi_i=0.50)
    fr3 = KD.f_rsi_min(20.0, phi_i=None, klasa=klasa_wilgotnosci)
    elem = []
    for (kod, rola), wu in ob.u.items():
        if rola in ("sciana_wewn", "strop_wewn", "podloga_grunt_nieogrz") or \
                ((kod, rola) not in ob.klucze_ogrz and rola != "podloga_grunt"):
            continue
        f = KD.f_rsi_przegrody(wu.U if rola != "podloga_grunt" else (ob.grunt.U if ob.grunt else wu.U))
        elem.append({"id": kod, "opis": f"przegroda ({rola}), U = {fmt_u(wu.U)}", "f_Rsi": f,
                     "zrodlo": "1 − U·0,25 (PN-EN ISO 13788 p. 4.3)", "ok": f >= fr.f_Rsi_wym - 1e-9})
    elem += MB.sprawdz_frsi(ob.wezly, fr.f_Rsi_wym)
    fr.elementy = elem
    R["frsi"] = fr
    R["frsi_klasa"] = fr3
    gl = []
    k = klimat_miesieczny()
    seen = set()
    for (kod, rola), wu in ob.u.items():
        if rola not in ROLE_GLASER or (kod, rola) in seen:
            continue
        seen.add((kod, rola))
        e = next((x for x in ob.bryla.elementy_obudowy() if (x.uklad or x.przegroda) == kod and x.rola == rola), None)
        if e is None:
            continue
        ws = e.warstwy if e.warstwy is not None else warstwy_przegrody(m, kod)
        warstwy, Rsi, Rse = KD.warstwy_glaser(ws, m.materialy, rola=rola)
        te = None
        uw = []
        if rola in ("sciana_nieogrz", "strop_nieogrz", "strop_nieogrz_gora") and e.sasiad in obc.b_u:
            b = obc.b_u[e.sasiad]
            te = list(20.0 - b * (20.0 - k.theta_e))
            uw.append(f"strona zimna — przestrzeń nieogrzewana {e.sasiad}: θ_u,n = 20 − b_u·(20 − θ_e,n), b_u = "
                      f"{fmt(b, 2)}; ciśnienie pary jak na zewnątrz")
        r = KD.glaser(warstwy, Rsi, Rse, theta_i=20.0, klasa=klasa_wilgotnosci, kod=kod,
                      nazwa=(m.przegroda(kod).nazwa if m.przegroda(kod) else wu.nazwa), rola=rola, theta_e=te)
        r.uwagi += uw
        if any(w.funkcja == "substrat" for w in warstwy):
            r.uwagi.append("dach zielony: metoda Glasera (stan ustalony, bez transportu wilgoci w cieczy) ma ograniczoną "
                           "miarodajność dla warstw nad hydroizolacją — ocena warstw pod hydroizolacją")
        gl.append(r)
    R["glaser"] = gl
    R["zal"]["wilg"] = Zalozenia()
    R["zal"]["wilg"].dodaj(f"Glaser: warunki wewnętrzne — klasa wilgotności {klasa_wilgotnosci} "
                           f"({KD.KLASY_OPIS.get(klasa_wilgotnosci)}), θ_i = 20 °C, p_i = p_e + 1,10·Δp", "[ZAŁ]",
                           "PN-EN ISO 13788:2013 zał. A (zachowawczo: nieznane zagęszczenie)")
    R["zal"]["wilg"].dodaj("Kryterium akumulacji kondensatu 0,5 kg/m² (DIN 4108-3 — kryterium literaturowe)", "[ZAŁ]")
    R["zal"]["wilg"].dodaj(f"Dane klimatyczne: {opis_zrodla()}", "")
    # węzły — uwagi o ciągłości
    role = {c.kod: c.rola for c in ob.ciaglosc}
    uw = []
    for w in (m.raw.get("wezly") or []) if isinstance(m.raw.get("wezly"), list) else []:
        uw += uwagi_wezla(w, m.przegrody, m.materialy, role)
    R["wezly_uwagi"] = uw
    # EP i alternatywy
    _ep_warianty(R, m, ob, went, obc, wyniki_symulacji)
    return R


def _ep_warianty(R: dict, m, ob, went, obc, wyniki_symulacji, *, cfg: dict | None = None,
                 dobor: dict | None = None) -> None:
    """Charakterystyka energetyczna: wariant projektowy A, A0 (bez PV), alternatywy B, C i wrażliwość.
    ``cfg``/``dobor`` — domyślnie ``ob.cfg`` (sekcja `energia` modelu) i dobór PC modułu obciążenia cieplnego."""
    cfg = ob.cfg if cfg is None else cfg
    dobor = obc.dobor if dobor is None else dobor
    zE = R["zal"]["ep"] = Zalozenia()
    sA = EP.system_projektowy(cfg, went, ob.bryla.A_f, dobor, zal=zE)
    wA = EP.oblicz_ep(ob, went, sA, obc=obc, zal=zE)
    sB = EP.system_gazowy(ob.bryla.A_f, went, ob.cfg)
    wB = EP.oblicz_ep(ob, went, sB, obc=obc, zal=Zalozenia())
    sC = EP.system_pc_domyslny(ob.bryla.A_f, went)
    wC = EP.oblicz_ep(ob, went, sC, obc=obc, zal=Zalozenia())
    sA2 = EP.system_projektowy(cfg, went, ob.bryla.A_f, dobor, z_pv=False)
    sA2.nazwa = "A0: PC R290 + rekuperacja, bez PV"
    wA0 = EP.oblicz_ep(ob, went, sA2, obc=obc, zal=Zalozenia())
    wA4 = EP.oblicz_ep(ob, went, EP.system_projektowy(cfg, went, ob.bryla.A_f, dobor), obc=obc, n50=4.0,
                       zal=Zalozenia())
    wA4.system.nazwa = "A (n50 = 4 h⁻¹ — brak próby szczelności)"
    wrazl = [wA4]
    if any(x.status == "domyślna" for x in ob.wezly):
        import dataclasses
        wz = MB.wezly_z_modelu(m, wyniki_symulacji, wezly_auto=ob.bryla.wezly_auto, wariant_domyslny="dobra_praktyka")
        ob_dp = dataclasses.replace(ob, wezly=wz, H_TB=MB.h_tb(wz))
        wdp = EP.oblicz_ep(ob_dp, went, EP.system_projektowy(cfg, went, ob.bryla.A_f, dobor), obc=obc,
                           zal=Zalozenia())
        wdp.system.nazwa = (f"A (Ψ „dobra praktyka” zamiast domyślnych PN-EN ISO 14683: H_TB = {fmt(ob_dp.H_TB, 1)} "
                            f"zamiast {fmt(ob.H_TB, 1)} W/K)")
        wrazl.append(wdp)
    R["ep"] = wA
    R["ep_alt"] = [wA, wA0, wB, wC]
    R["ep_wrazliwosc"] = wrazl


def zapisz_raporty(R: dict, out, *, tytul: str = "", model_opis: str = "") -> list[str]:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    ob = R["obudowa"]
    pliki = []

    def zapisz(nazwa, tresc):
        p = out / nazwa
        p.write_text(tresc, encoding="utf-8")
        pliki.append(str(p))

    stopka = (f"\n---\n*Wygenerowano: {date.today().isoformat()} — biblioteka `lamela.obliczenia` "
              f"(PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: {PRZYKL}).*\n")
    # 01 U
    wu = [w for (k, r), w in ob.u.items() if r not in ("sciana_wewn", "strop_wewn")]
    zapisz("01_przegrody_U.md", f"# Obliczenia U przegród{(' — ' + tytul) if tytul else ''}\n\n" +
           raport_u(wu, R["zal"]["U"]) + stopka)
    # 02 grunt
    g = ""
    if ob.grunt:
        g += raport_grunt(ob.grunt, "strefa ogrzewana")
    if ob.grunt_nieogrz:
        g += "\n" + raport_grunt(ob.grunt_nieogrz, "pomieszczenia nieogrzewane (garaż)")
    zapisz("02_grunt.md", "# Podłoga na gruncie\n\n" + (g or "Brak podłóg na gruncie w strefie ogrzewanej.\n") + stopka)
    # 03 stolarka
    okna = list(ob.okna.values())
    zac = {k_: v for k_, v in ob.zacienienie.items()}
    zapisz("03_stolarka_g.md", "# Stolarka okienna i drzwiowa\n\n" + raport_okna(okna, ob.g_spr, zac) + stopka)
    # 04 mostki
    zapisz("04_mostki.md", "# Mostki cieplne\n\n" + raport_mostki_md(R) + stopka)
    # 05 wilgotność
    wyk = {}
    for r in R["glaser"]:
        fn = f"glaser_{re.sub(r'[^A-Za-z0-9_-]+', '_', r.kod)}.png"
        KD.wykres_glaser(r, out / fn)
        wyk[r.kod] = fn
        pliki.append(str(out / fn))
    s = "# Wilgotność: f_Rsi i kondensacja międzywarstwowa\n\n" + KD.raport_frsi(R["frsi"]) + "\n"
    f3 = R["frsi_klasa"]
    s += (f"Dla porównania — klasa wilgotności 3 (PN-EN ISO 13788 zał. A): miesiąc krytyczny "
          f"{f3.miesiac_kryt}, f_Rsi,max = {fmt(f3.f_Rsi_kryt, 3)} (informacyjnie; wymaganie WT — φ_i = 50 %).\n\n")
    s += KD.raport_glaser(R["glaser"], wyk, R["zal"]["wilg"])
    zapisz("05_wilgotnosc.md", s + stopka)
    # 06 ciągłość
    zapisz("06_ciaglosc_warstw.md", "# Ciągłość warstw\n\n" + raport_ciaglosc(ob.ciaglosc, R.get("wezly_uwagi")) + stopka)
    # 07 wentylacja
    zapisz("07_wentylacja.md", "# Wentylacja\n\n" + raport_wentylacja(R["went"], R["zal"]["went"]) + stopka)
    # 08 obciążenie
    zapisz("08_obciazenie_cieplne.md", "# Obciążenie cieplne\n\n" + raport_obciazenie(R["obc"], R["zal"]["obc"]) + stopka)
    # 09 EP
    EP.wykres_bilans(R["ep"], out / "bilans_energii.png")
    pliki.append(str(out / "bilans_energii.png"))
    s = "# Charakterystyka energetyczna\n\n" + EP.raport_ep(R["ep"], wykres="bilans_energii.png", zal=R["zal"]["ep"])
    s += "\n### Wrażliwość\n\n" + tabela_md(["Wariant", "EP [kWh/(m²·rok)]", "EP ≤ EP_max"],
                                            [[w.system.nazwa, fmt(w.EP, 1), ok(w.spelnia)] for w in R["ep_wrazliwosc"]])
    zapisz("09_charakterystyka_energetyczna.md", s + "\n" + stopka)
    # 10 alternatywy
    zapisz("10_analiza_alternatyw.md", "# Analiza alternatyw\n\n" + EP.raport_alternatywy(R["ep_alt"]) + stopka)
    # 00 zestawienie
    zapisz("00_zestawienie.md", zestawienie_md(R, tytul, model_opis, [Path(p).name for p in pliki]) + stopka)
    # json
    js = wyniki_json(R)
    (out / "wyniki.json").write_text(json.dumps(js, ensure_ascii=False, indent=1, default=_json_conv), encoding="utf-8")
    pliki.append(str(out / "wyniki.json"))
    return pliki


def raport_mostki_md(R) -> str:
    ob = R["obudowa"]
    return MB.raport_mostki(ob.wezly, R["frsi"].f_Rsi_wym, ob.A_obudowy)


def zestawienie_md(R, tytul, model_opis, pliki) -> str:
    ob = R["obudowa"]
    br = ob.bryla
    w = R["ep"]
    s = [f"# Zestawienie obliczeń fizyki budowli i charakterystyki energetycznej{(' — ' + tytul) if tytul else ''}", ""]
    if model_opis:
        s += [model_opis, ""]
    s += ["**Status: PRZYKŁAD – NIE DO ZŁOŻENIA.** Dane wyrobów — przykładowe (typowe wyroby danej klasy, lub równoważne); "
          "wartości oznaczone [NZW] do weryfikacji na egzemplarzach norm; [ZAŁ] — założenia projektowe.", ""]
    rows = [["A_f (pow. o regulowanej temperaturze)", f"{fmt(br.A_f, 2)} m²", ""],
            ["Kubatura netto strefy ogrzewanej", f"{fmt(br.V_netto, 1)} m³", ""],
            ["H_tr / H_ve", f"{fmt(w.H_tr, 1)} / {fmt(w.H_ve, 1)} W/K", ""],
            ["H_TB (mostki)", f"{fmt(ob.H_TB, 1)} W/K", "Ψ: " + ", ".join(sorted({x.status or '—' for x in ob.wezly}))],
            ["Obciążenie cieplne Φ_HL (θ_e = −18 °C)", f"{fmt(R['obc'].Phi_HL / 1000, 2)} kW",
             f"{fmt(R['obc'].Phi_HL / br.A_f, 1)} W/m²"],
            ["Wentylacja — strumień projektowy", f"{fmt(R['went'].q_m3h, 0)} m³/h", ok(all(c is not False for _, _, c in R["went"].sprawdzenia))],
            ["EU / EK / EP", f"{fmt(w.EU, 1)} / {fmt(w.EK, 1)} / **{fmt(w.EP, 1)}** kWh/(m²·rok)",
             f"EP_max = {fmt(w.EP_max, 0)} — {ok(w.spelnia)}"],
            ["U_oze / E_CO2", f"{fmt(w.U_oze, 1)} % / {fmt(w.E_CO2_t, 2)} t/rok", ""]]
    s.append(tabela_md(["Wielkość", "Wartość", "Uwagi"], rows, "lll"))
    s.append("")
    s.append("## Zgodność z wymaganiami (WT zał. 2, cele projektu)")
    s.append("")
    rows = []
    for (kod, rola), wu in ob.u.items():
        if wu.U_max is None and rola != "podloga_grunt":
            continue
        if rola == "podloga_grunt" and ob.grunt:
            rows.append([f"U {kod} (grunt, PN-EN ISO 13370)", fmt_u(ob.grunt.U), f"≤ {fmt(ob.grunt.U_max)}",
                         ok(ob.grunt.spelnia_WT), f"≤ {fmt(ob.grunt.U_cel)}: {ok(ob.grunt.spelnia_cel)}"])
            continue
        rows.append([f"U {kod} ({rola})", fmt_u(wu.U), f"≤ {fmt(wu.U_max)}", ok(wu.spelnia_WT),
                     f"≤ {fmt(wu.U_cel)}: {ok(wu.spelnia_cel)}" if wu.U_cel else "—"])
    sym = {}
    for o in ob.okna.values():
        if o.U_max is None:
            continue
        sym.setdefault(o.symbol, o)
    for sy, o in sym.items():
        rows.append([f"U_w {sy} ({o.typ})", fmt_u(o.U_w), f"≤ {fmt(o.U_max)}", ok(o.spelnia_WT),
                     f"≤ {fmt(o.U_cel)}: {ok(o.spelnia_cel)}" if o.U_cel else "—"])
    ng = sum(1 for g in ob.g_spr if g.spelnia is False)
    rows.append(["g ≤ 0,35 (okna E/S/W)", f"{len(ob.g_spr) - ng}/{len(ob.g_spr)} spełnia", "WT zał. 2 pkt 2.1", ok(ng == 0),
                 ", ".join(g.id for g in ob.g_spr if g.spelnia is False) or "—"])
    fr = R["frsi"]
    nf = [e for e in fr.elementy if e.get("ok") is False]
    nb = [e for e in fr.elementy if e.get("ok") is None]
    rows.append(["f_Rsi ≥ f_Rsi,wym", f"f_wym = {fmt(fr.f_Rsi_wym, 3)}", "WT zał. 2 pkt 2.2", ok(not nf),
                 (", ".join(e["id"] for e in nf) or "—") + (f"; bez danych: {len(nb)} węzłów (symulacja)" if nb else "")])
    kg = [g for g in R["glaser"] if not g.dopuszczalna]
    rows.append(["Kondensacja międzywarstwowa", f"{len(R['glaser']) - len(kg)}/{len(R['glaser'])} dopuszczalna",
                 "WT zał. 2 pkt 2.2.5", ok(not kg), ", ".join(g.kod for g in kg) or "—"])
    bc = [c for c in ob.ciaglosc if not c.ok]
    rows.append(["Ciągłość warstw (4 linie)", f"{len(ob.ciaglosc) - len(bc)}/{len(ob.ciaglosc)} przegród", "brief § 9",
                 ok(not bc), "; ".join(f"{c.kod}: {c.braki[0].opis}" for c in bc) or "—"])
    if ob.grunt and ob.grunt.izolacja:
        rows.append(["Izolacja obwodowa R ≥ 2,0", fmt(ob.grunt.izolacja.R_n, 2), "WT zał. 2 pkt 1.4",
                     ok(ob.grunt.spelnia_obwodowa), ""])
    else:
        rows.append(["Izolacja obwodowa R ≥ 2,0", "brak danych", "WT zał. 2 pkt 1.4", ok(None), "energia.grunt.izolacja_obwodowa"])
    rows.append(["EP ≤ EP_max", fmt(w.EP, 1), f"≤ {fmt(w.EP_max, 0)} (WT § 329)", ok(w.spelnia), w.system.nazwa])
    s.append(tabela_md(["Sprawdzenie", "Wartość", "Wymaganie", "Wynik", "Uwagi"], rows, "lllll"))
    s.append("")
    if br.ostrzezenia:
        s.append("## Ostrzeżenia geometrii (model)")
        s.append("")
        s += [f"* {x}" for x in br.ostrzezenia[:40]]
        s.append("")
    s.append("## Pliki")
    s.append("")
    s += [f"* [{p}]({p})" for p in pliki]
    s.append("")
    s.append(f"Dane klimatyczne: {opis_zrodla()}.")
    return "\n".join(s)


def _json_conv(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def wyniki_json(R) -> dict:
    ob = R["obudowa"]
    w = R["ep"]
    return {
        "A_f": ob.bryla.A_f, "V_netto": ob.bryla.V_netto,
        "U": {f"{k}|{r}": {"U": v.U, "U_max": v.U_max, "U_cel": v.U_cel} for (k, r), v in ob.u.items()},
        "U_grunt": ob.grunt.U if ob.grunt else None,
        "okna": {k: {"symbol": o.symbol, "U_w": o.U_w, "A_w": o.A_w} for k, o in ob.okna.items()},
        "H_TB": ob.H_TB, "Phi_HL_W": R["obc"].Phi_HL,
        "pomieszczenia_Phi_HL_W": {o.id: o.Phi_HL for o in R["obc"].pomieszczenia},
        "wentylacja_m3h": R["went"].q_m3h,
        "EP": {x.system.nazwa: {"EU": x.EU, "EK": x.EK, "EP": x.EP, "spelnia": x.spelnia, "E_CO2_t": x.E_CO2_t,
                                "U_oze": x.U_oze, "koszt_zl": x.koszt_zl} for x in R["ep_alt"]},
        "EP_projekt": w.EP, "EP_max": w.EP_max,
        "glaser": {g.kod: {"kondensacja": g.kondensacja, "wysycha": g.wysycha, "M_a_max_kg_m2": g.M_a_max,
                           "sd_par_wym": g.sd_par_wym} for g in R["glaser"]},
        "f_Rsi_wym": R["frsi"].f_Rsi_wym,
        "ciaglosc_braki": {c.kod: [u.opis for u in c.braki] for c in ob.ciaglosc},
        "ostrzezenia": ob.bryla.ostrzezenia,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Obliczenia fizyki budowli i charakterystyki energetycznej (Dom LAMELA)")
    ap.add_argument("--budynek", required=True)
    ap.add_argument("--dzialka")
    ap.add_argument("--out", required=True)
    ap.add_argument("--psi", choices=("domyslna", "dobra_praktyka"))
    ap.add_argument("--wezly-wyniki", help="wyniki symulacji ISO 10211 (JSON/YAML: {id: {psi, f_rsi, dlugosc}})")
    ap.add_argument("--bez-zacienienia", action="store_true")
    ap.add_argument("--tytul", default="")
    a = ap.parse_args(argv)
    from lamela.model import load_model
    m = load_model(a.budynek, a.dzialka, strict=False)
    if m.bledy:
        print(m.raport_walidacji())
    sym = MB.wczytaj_wyniki_symulacji(a.wezly_wyniki) if a.wezly_wyniki else None
    R = oblicz_wszystko(m, wyniki_symulacji=sym, wariant_psi=a.psi, zacienienie=not a.bez_zacienienia)
    pl = zapisz_raporty(R, a.out, tytul=a.tytul, model_opis=f"Model: `{a.budynek}`" + (f" + `{a.dzialka}`" if a.dzialka else ""))
    print("\n".join(pl))
    w = R["ep"]
    print(f"EP = {w.EP:.1f} kWh/(m²·rok) (EP_max {w.EP_max:.0f}); Φ_HL = {R['obc'].Phi_HL / 1000:.2f} kW")
    return 0


if __name__ == "__main__":
    sys.exit(main())
