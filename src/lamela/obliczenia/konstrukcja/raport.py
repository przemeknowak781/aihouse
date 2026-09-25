"""Złożenie „Obliczeń statycznych” (markdown + rysunki PNG + JSON z wynikami; opcjonalnie HTML).

Układ: strona tytułowa → spis pozycji (z maks. wykorzystaniem nośności) → 0. Założenia (normy, parametry, materiały,
obciążenia ogólne: śnieg, wiatr, użytkowe) → Poz. 1…n (dachy, stropy, wsporniki, schody, belki, nadproża, wieńce, słupy,
ściany, fundamenty; w każdej: opis i schemat statyczny, zestawienie obciążeń, obliczenia (wzór → podstawienie → wynik),
tabele wymiarowania, wnioski „Przyjęto: …”) → wykaz stali (PN-EN ISO 3766) → uwagi, uproszczenia, brakujące dane.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
from pathlib import Path

from . import zelbet
from .materialy import Beton
from .pozycje import AnalizaKonstrukcji, Pozycja
from .wspolne import f, tabela

WERSJA = "1.0"

NORMY = [
    "PN-EN 1990:2004 + A1:2008 + NA:2010 — Podstawy projektowania konstrukcji",
    "PN-EN 1991-1-1:2004 + AC:2009 + NA:2010 — Ciężar objętościowy, ciężar własny, obciążenia użytkowe",
    "PN-EN 1991-1-3:2005 + AC:2009 + Ap1:2010 + NA:2010 — Obciążenie śniegiem",
    "PN-EN 1991-1-4:2008 + A1:2010 + AC:2009 + NA:2010 — Oddziaływania wiatru",
    "PN-EN 1992-1-1:2008 + AC:2011 + NA:2018-11 — Konstrukcje z betonu",
    "PN-EN 1993-1-1:2006 + A1:2014-07 + NA:2010; PN-EN 1993-1-8:2006 + NA:2011 — Konstrukcje stalowe",
    "PN-EN 1996-1-1+A1:2013-05 + NA:2014-03 (+Ap2:2014-09); PN-EN 1996-3 — Konstrukcje murowe",
    "PN-EN 1997-1:2008 + A1:2014-05 + Ap2:2010 + NA:2011 — Projektowanie geotechniczne",
    "PN-H-93220:2018-02 + Ap1:2018-04 — Stal B500SP; PN-EN ISO 3766 — rysunki zbrojenia",
    "Rozp. MTBiGM z 25.04.2012 (Dz.U. 2012 poz. 463) — geotechniczne warunki posadawiania",
]

METODY = [
    "Płyty: MES płytowy (element prostokątny ACM, teoria Kirchhoffa, ν = 0,2), podpory liniowe sztywne (ściany, belki), "
    "punktowe (słupy); obwiednia kombinacji 6.10a/6.10b, obciążeń szachownicowych pól i sytuacji wyjątkowej B2; momenty "
    "wymiarujące Wood–Armer; pola prostokątne podparte na obwodzie — sprawdzenie metodą tablic (współczynniki generowane MRS, "
    "zgodne z tablicami Timoshenki/Czernego ≤ 1 %), M_Ed = max(MES, tablice).",
    "Belki, schody, nadproża: schematy prętowe (MES belkowy), obwiednie układów obciążenia zmiennego.",
    "Ściany murowe: profile obciążeń wzdłuż osi (reakcje płyt z MES + ściany wyżej), przekazanie obciążeń znad otworów na "
    "filarki (po 0,5 m z każdej strony), nośność wg PN-EN 1996-1-1 6.1.2 + zał. G, filarki z η_A.",
    "Fundamenty: nośność wg PN-EN 1997-1 zał. D (DA2*), osiadanie — sumowanie warstw (Boussinesq), ławy niezbrojone "
    "poprzecznie wg PN-EN 1992-1-1 12.9.3; obciążenie ław — maks. średnia krocząca na 2,0 m.",
    "Ugięcia żelbetu: l/d (7.4.2), a gdy niespełnione — obliczenie z interpolacją ζ, pełzaniem φ = 2,5 i skurczem (7.4.3).",
]


def _pozycja_md(pz: Pozycja, out_dir: Path, poziom: int = 3) -> list[str]:
    L = []
    h = "#" * poziom
    eta = pz.wykorzystanie
    L.append(f"{h} Poz. {pz.nr} — {pz.tytul}")
    L.append("")
    L.append(f"*Element modelu: `{pz.ident}` · maks. wykorzystanie nośności η = {f(eta * 100, 0)}% · "
             f"{'wszystkie warunki spełnione' if pz.ok else '**WARUNKI NIESPEŁNIONE**'}*")
    L.append("")
    if pz.opis:
        L.append(f"{h}# Opis i schemat statyczny")
        L.append("")
        L += [t + "\n" for t in pz.opis]
    for p, cap in pz.rysunki:
        rel = os.path.relpath(p, out_dir)
        L.append(f"![{cap}]({rel})")
        L.append(f"*{cap}*")
        L.append("")
    if pz.obciazenia:
        L.append(f"{h}# Zestawienie obciążeń")
        L.append("")
        L += [t + "\n" for t in pz.obciazenia]
    if pz.wyniki:
        L.append(f"{h}# Obliczenia")
        L.append("")
        for w in pz.wyniki:
            L.append(w.md(poziom=poziom + 2))
    if pz.tabele:
        L.append(f"{h}# Wymiarowanie — zestawienia")
        L.append("")
        L += [t + "\n" for t in pz.tabele]
    if pz.uwagi:
        L += [f"> {u}" for u in pz.uwagi]
        L.append("")
    if pz.przyjeto:
        L.append(f"{h}# Wnioski")
        L.append("")
        L += [f"**Przyjęto:** {t}" + "  " for t in pz.przyjeto]
        L.append("")
    return L


def spis_pozycji(an: AnalizaKonstrukcji) -> str:
    rows = []
    for g in an.pozycje:
        rows.append([f"**{g.nr}**", "", f"**{g.tytul}**", "", ""])
        for pz in g.podpozycje:
            e = pz.wykorzystanie
            rows.append([pz.nr, f"`{pz.ident}`", pz.tytul, f"{f(e * 100, 0)}%", "spełnione" if pz.ok else "**niespełnione**"])
    return tabela(["Poz.", "Element", "Opis", "η_max", "Warunki"], rows)


def generuj_raport(an: AnalizaKonstrukcji, out_dir: str | Path, tytul: str | None = None, status: str | None = None,
                   html: bool = True) -> Path:
    """Zapisuje ``obliczenia_statyczne.md`` (+ ``.html``) oraz ``wyniki.json`` w katalogu out_dir. Rysunki — ``rys/``
    (analiza powinna być uruchomiona z ``rys_dir = out_dir/rys``)."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    m, p = an.m, an.p
    meta = m.raw.get("meta") or {}
    tytul = tytul or f"Obliczenia statyczne — {meta.get('nazwa', 'budynek')}"
    L = [f"# {tytul}", ""]
    L.append(f"Model: `{m.src_b}` (wersja {meta.get('wersja', '—')}, {meta.get('data', '—')}) · biblioteka "
             f"`lamela.obliczenia.konstrukcja` {WERSJA} · wygenerowano {_dt.date.today().isoformat()}")
    L.append("")
    if status:
        L.append(f"> **{status}**")
        L.append("")
    L.append("> Obliczenia wygenerowane automatycznie z modelu budynku. Wartości oznaczone [NZW] — niezweryfikowane w tekście "
             "normy (rejestr R5), [UPR] — uproszczenia biblioteki, [ZAŁ] — założenia. Dane gruntowe PRZYKŁADOWE "
             "(W-282, E-04). Dokument wymaga weryfikacji i podpisu projektanta z uprawnieniami: "
             "[DO UZUPEŁNIENIA: imię i nazwisko, specjalność, nr uprawnień].")
    L.append("")
    L.append("## Spis pozycji")
    L.append("")
    L.append(spis_pozycji(an))
    L.append("")
    # --- 0. założenia
    L.append("## Poz. 0 — Podstawa opracowania, założenia i obciążenia ogólne")
    L.append("")
    L.append("### 0.1 Normy i przepisy")
    L.append("")
    L += [f"- {n}" for n in NORMY]
    L.append("")
    L.append("Stosowane wyłącznie Eurokody 1. generacji z NA (R5-01…R5-03, W-260).")
    L.append("")
    L.append("### 0.2 Klasyfikacja i współczynniki")
    L.append("")
    po = an.pos_obc
    L += [t + "\n" for t in po.opis]
    L.append(tabela(["Parametr", "Wartość", "Parametr", "Wartość"], [
        ["γ_G,sup / γ_G,inf / ξ", f"{f(p.gG_sup)} / {f(p.gG_inf)} / {f(p.xi)}", "γ_Q", f(p.gQ)],
        ["EQU: γ_G,dst / γ_G,stb / γ_Q", f"{f(p.EQU_gG_dst)} / {f(p.EQU_gG_stb)} / {f(p.EQU_gQ)}", "K_FI", f(p.K_FI, 1)],
        ["γ_c / γ_s", f"{f(p.gamma_c, 1)} / {f(p.gamma_s)}", "α_cc", f(p.alfa_cc, 1) + " [NZW]"],
        ["γ_M (mur, kl. A)", f(p.mur_gamma_M, 1), "γ_M0 / γ_M1 / γ_M2", f"{f(p.gM0, 1)} / {f(p.gM1, 1)} / {f(p.gM2)}"],
        ["γ_R;v / γ_R;h (DA2*)", f"{f(p.gR_v, 1)} / {f(p.gR_h, 1)}", "kategoria geotechniczna", str(p.kategoria_geotechniczna)],
        ["s_k [kN/m²] (strefa 2)", f(p.s_k), "v_b,0 [m/s] (strefa 1), teren", f"{f(p.v_b0, 0)}, kat. {p.kategoria_terenu}"],
        ["φ(∞,t₀) / ε_cs", f"{f(p.fi_pelzania, 1)} / {f(p.eps_cs * 1000, 2)}‰ [ZAŁ]", "grunt", p.grunt.nazwa],
    ]))
    L.append("")
    L.append("### 0.3 Materiały, klasy ekspozycji i otulenia")
    L.append("")
    L += [t + "\n" for t in po.tabele]
    b = Beton.z_parametrow(p.beton_ekspozycja.get("XC1", "C25/30"), p)
    L.append(f"**Długości zakotwienia i zakładów prętów B500SP w betonie {b.klasa}** (PN-EN 1992-1-1 8.4, 8.7; σ_sd = f_yd, "
             "α = 1,0)\n")
    L.append(zelbet.tabela_zakotwien(b, stal=an.stal))
    L.append("")
    L.append("### 0.4 Obciążenia ogólne — śnieg i wiatr")
    L.append("")
    for w in po.wyniki:
        L.append(w.md(poziom=4))
    L.append("### 0.5 Metody obliczeń")
    L.append("")
    L += [f"- {t}" for t in METODY]
    L.append("")
    # --- pozycje
    for g in an.pozycje:
        L.append(f"## Poz. {g.nr} — {g.tytul}")
        L.append("")
        for pz in g.podpozycje:
            L += _pozycja_md(pz, out, 3)
    # --- wykaz stali
    prety = [pr for g in an.pozycje for pz in g.podpozycje for pr in pz.prety]
    if prety:
        L.append("## Zestawienie stali zbrojeniowej (orientacyjne — dane do rysunków zbrojenia, PN-EN ISO 3766)")
        L.append("")
        L.append("Kody kształtu wg PN-EN ISO 3766: 00 — pręt prosty, 11 — odgięty 90°, 21 — U, 51 — strzemię zamknięte. "
                 "Długości bez zakładów montażowych (doliczyć wg tabeli zakotwień). Ilości płyt — z pól wymiarowania.")
        L.append("")
        L.append(zelbet.wykaz_stali(prety))
        L.append("")
    # --- uwagi
    L.append("## Uwagi, uproszczenia i dane do uzupełnienia")
    L.append("")
    if an.uwagi:
        L.append("**Uwagi z analizy:**")
        L.append("")
        L += [f"- {u}" for u in an.uwagi]
        L.append("")
    if an.brak_danych:
        L.append("**Dane nieobecne w modelu (przyjęto wartości domyślne):**")
        L.append("")
        L += [f"- {u}" for u in an.brak_danych]
        L.append("")
    L.append("**Zakres wymagający osobnej analizy:** " + "; ".join(OGRANICZENIA))
    L.append("")
    md = "\n".join(L)
    fmd = out / "obliczenia_statyczne.md"
    fmd.write_text(md, encoding="utf-8")
    (out / "wyniki.json").write_text(json.dumps(wyniki_json(an), ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    if html:
        try:
            import markdown
            body = markdown.markdown(md, extensions=["tables"])
            (out / "obliczenia_statyczne.html").write_text(_HTML.replace("{{TITLE}}", tytul).replace("{{BODY}}", body),
                                                          encoding="utf-8")
        except ImportError:
            pass
    return fmd


OGRANICZENIA = [
    "ściany-tarcze z otworami, tarcze wieloprzęsłowe i wspornikowe (MES tarczowy / STM)",
    "przebicie płyt nad słupami (6.4) i płyt fundamentowych — tylko sygnalizowane",
    "słupy żelbetowe i ściany żelbetowe (5.8, efekty II rzędu)",
    "sztywność przestrzenna i stateczność ogólna budynku (tarcze stropowe, usztywnienie ścianami), oddziaływania wyjątkowe",
    "drgania stropów i wsporników (PN-B-02171)",
    "łączniki termoizolacyjne (ETA) — dobór wg producenta na siły z pozycji",
    "połączenia stalowe (blachy podstaw, kotwy) — tylko śruby/spoiny podstawowe",
    "ugięcia z uwzględnieniem kolejności wznoszenia, obrotu podpór wsporników i sztywności ścian",
    "płyta fundamentowa — tylko model Winklera pasma; osiadania — bez wpływu fundamentów sąsiednich",
    "stateczność skarp/wykopów, wypór wody, parcie gruntu na ściany piwnic",
]


def wyniki_json(an: AnalizaKonstrukcji) -> dict:
    out = {"pozycje": [], "uwagi": an.uwagi, "brak_danych": an.brak_danych}
    for g in an.pozycje:
        for pz in g.podpozycje:
            d = {"nr": pz.nr, "id": pz.ident, "tytul": pz.tytul, "rodzaj": pz.rodzaj, "wykorzystanie": round(pz.wykorzystanie, 4),
                 "ok": pz.ok, "przyjeto": pz.przyjeto,
                 "warunki": [{"opis": w.opis, "E": round(float(w.E), 4), "R": round(float(w.R), 4), "eta": round(w.eta, 4)}
                             for w in pz.warunki]}
            dane = {k: v for k, v in pz.dane.items() if k != "biegi"}
            d["dane"] = json.loads(json.dumps(dane, default=lambda o: str(o)))
            out["pozycje"].append(d)
    return out


_HTML = """<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{{TITLE}}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--ink:#0b0b0b;--ink2:#52514e;--grid:#dcdbd6;--bg:#fcfcfb;--acc:#2a78d6;--th:#f0efec}
body{font-family:"DejaVu Sans",Arial,sans-serif;color:var(--ink);background:var(--bg);max-width:1100px;margin:0 auto;padding:16px;font-size:14px;line-height:1.45}
h1{font-size:22px}h2{font-size:18px;border-bottom:2px solid var(--ink);padding-bottom:3px;margin-top:32px}
h3{font-size:16px;border-bottom:1px solid var(--grid);margin-top:26px}h4,h5,h6{font-size:14px}
table{border-collapse:collapse;margin:8px 0;font-size:12.5px;display:block;overflow-x:auto;max-width:100%}
th,td{border:1px solid var(--grid);padding:3px 6px;text-align:left;vertical-align:top}th{background:var(--th)}
img{max-width:100%;height:auto;border:1px solid var(--grid)}blockquote{border-left:3px solid var(--acc);margin:8px 0;padding:2px 10px;color:var(--ink2)}
code{font-size:12.5px}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--ink:#f2f2ef;--ink2:#c3c2b7;--grid:#3a3a37;--bg:#1a1a19;--th:#262624}}
:root[data-theme="dark"]{--ink:#f2f2ef;--ink2:#c3c2b7;--grid:#3a3a37;--bg:#1a1a19;--th:#262624}img{background:#fff}
</style></head><body>{{BODY}}</body></html>"""
