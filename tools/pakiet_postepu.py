#!/usr/bin/env python3
"""Pakiet postępu do pobrania: plansze raportów, wyniki etapów, duże pojedyncze rysunki (PDF wektorowe + PNG) i tomy
robocze — składany z bieżącego stanu repozytorium do folderu i archiwum ZIP.

Użycie: python3 tools/pakiet_postepu.py [--out KATALOG] [--bez-png-arkuszy]
Wynik: <out>/LAMELA_postep_<data>_<godz>/ oraz <out>/LAMELA_postep_<data>_<godz>.zip (domyślnie w scratchpadzie sesji
albo w build/pakiety — katalog nie jest wersjonowany).
"""
import argparse
import datetime
import json
import shutil
import zipfile
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Europe/Warsaw")

# (katalog docelowy w pakiecie, lista wzorców glob względem ROOT)
ETAPY = [
    ("02_wyniki_etapow/01_wejscie_szkic_i_interpretacja", ["00_wejscie/*"]),
    ("02_wyniki_etapow/02_podstawy_prawne", ["docs/10_podstawy_prawne/grafiki/*.png", "docs/10_podstawy_prawne/00_rejestr_wymagan.md",
                                             "docs/10_podstawy_prawne/weryfikacja_upzp_art2_definicje.md", "docs/00_brief_projektowy.md"]),
    ("02_wyniki_etapow/03_koncepcja_warianty_i_ocena", ["docs/20_koncepcja/ocena_panel.png", "docs/20_koncepcja/werdykt_panelu.png",
                                                        "docs/20_koncepcja/porownanie_W1_W2.png", "docs/20_koncepcja/ocena_J*.md"]),
    ("02_wyniki_etapow/03_koncepcja_warianty_i_ocena/W1", ["docs/20_koncepcja/W1/*.png", "docs/20_koncepcja/W1/opis.md"]),
    ("02_wyniki_etapow/03_koncepcja_warianty_i_ocena/W2", ["docs/20_koncepcja/W2/*.png", "docs/20_koncepcja/W2/opis.md"]),
    ("02_wyniki_etapow/03_koncepcja_warianty_i_ocena/W3", ["docs/20_koncepcja/W3/*.png", "docs/20_koncepcja/W3/opis.md"]),
    ("02_wyniki_etapow/04_koncepcja_ostateczna", ["docs/20_koncepcja/final/*.png", "docs/20_koncepcja/final/bilans.md",
                                                  "docs/20_koncepcja/koncepcja.md", "docs/20_koncepcja/audyt_A*.md",
                                                  "docs/20_koncepcja/weryfikacja_*.md", "docs/20_koncepcja/poprawki_runda2_wejscie.md"]),
    ("02_wyniki_etapow/05_mostki_woda_izolacje", ["projekt/08_obliczenia/mostki/*.png", "projekt/08_obliczenia/mostki/*.md",
                                                 "projekt/08_obliczenia/mostki2d/*.md"]),
    ("02_wyniki_etapow/06_konstrukcja", ["projekt/04_PT_konstrukcja/*.md", "projekt/04_PT_konstrukcja/rysunki/kontrola_zbrojenia.md",
                                         "projekt/04_PT_konstrukcja/obliczenia/*.md", "projekt/04_PT_konstrukcja/obliczenia/*.html"]),
    ("02_wyniki_etapow/07_instalacje_braki_danych", ["projekt/05_PT_instalacje_sanitarne/BRAKI_DANYCH.md",
                                                     "projekt/06_PT_instalacje_elektryczne/BRAKI_DANYCH.md", "projekt/02_PZT/BRAKI_DANYCH.md"]),
    ("02_wyniki_etapow/08_arkusze_ekonomia", ["docs/30_arkusze/*.md"]),
    ("02_wyniki_etapow/09_strona_www", ["www/raport/zrzuty/*.jpg", "www/PLAN.md", "www/DO_POPRAWY.md"]),
    ("02_wyniki_etapow/10_weryfikacje_i_kompletnosc_tomow", ["projekt/09_opis_i_zalaczniki/weryfikacja_*.md",
                                                           "projekt/09_opis_i_zalaczniki/tom_I/weryfikacja_*.md",
                                                           "projekt/09_opis_i_zalaczniki/*/raport_*.txt",
                                                           "projekt/wydanie/raport_kompletnosci_*.md"]),
    ("02_wyniki_etapow/11_statystyki_sesji", ["docs/50_statystyki/*.md", "docs/50_statystyki/*.png",
                                            "docs/50_statystyki/dane/raport_*.md"]),
    ("02_wyniki_etapow/12_prezentacja", ["docs/40_prezentacja/README.md"]),
]
# duże pojedyncze rysunki: (katalog w pakiecie, katalog źródłowy)
RYSUNKI = [
    ("03_rysunki_duze/PZT_zagospodarowanie", "projekt/02_PZT/rysunki"),
    ("03_rysunki_duze/PAB_architektura", "projekt/03_PAB/rysunki"),
    ("03_rysunki_duze/PAB_architektura", "projekt/01_koncepcja/widoki"),      # zapas — tylko gdy komplet PAB nie istnieje
    ("03_rysunki_duze/PT_AR_arkusze_stadium_PT", "projekt/10_PT_architektura/rysunki"),
    ("03_rysunki_duze/PT_AR_detale", "projekt/10_PT_architektura/detale"),
    ("03_rysunki_duze/PT_BO_konstrukcja", "projekt/04_PT_konstrukcja/rysunki"),
    ("03_rysunki_duze/PT_IS_instalacje_sanitarne", "projekt/05_PT_instalacje_sanitarne/rysunki"),
    ("03_rysunki_duze/PT_IE_instalacje_elektryczne", "projekt/06_PT_instalacje_elektryczne/rysunki"),
]


def kopiuj(src: Path, dst_dir: Path) -> int:
    dst_dir.mkdir(parents=True, exist_ok=True)
    d = dst_dir / src.name
    if d.exists():
        return 0
    shutil.copy2(src, d)
    return src.stat().st_size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "build" / "pakiety"))
    ap.add_argument("--bez-png-arkuszy", action="store_true", help="z arkuszy tylko PDF (mniejsze archiwum)")
    ap.add_argument("--png-tylko", default=None, help="PNG podglądu tylko dla tych folderów (np. PZT,PAB)")
    ap.add_argument("--podziel", type=float, default=0, help="dziel archiwum na części ≤ N MiB (np. 28)")
    a = ap.parse_args()
    teraz = datetime.datetime.now(TZ)
    nazwa = f"LAMELA_postep_{teraz:%Y-%m-%d_%H%M}"
    out = Path(a.out) / nazwa
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    spis, rozm = [], 0

    # 01 — plansze postępu (kolaże A4)
    rap = sorted(ROOT.glob("raporty/raport_*.png"))
    for p in rap:
        rozm += kopiuj(p, out / "01_plansze_postepu")
    spis.append(("01_plansze_postepu", f"plansze A4 poziomo (kolaże z godziną): {len(rap)}, od pierwszej do ostatniej"))

    # 02 — wyniki etapów
    for kat, wz in ETAPY:
        n = 0
        for w in wz:
            for p in sorted(ROOT.glob(w)):
                if p.is_file():
                    rozm += kopiuj(p, out / kat)
                    n += 1
        if n:
            spis.append((kat, f"plików: {n}"))

    # 03 — duże pojedyncze rysunki (PDF wektorowe zawsze, PNG opcjonalnie)
    widziane = set()
    for kat, zr in RYSUNKI:
        d = ROOT / zr
        if not d.exists():
            continue
        if zr == "projekt/01_koncepcja/widoki" and any((ROOT / "projekt/03_PAB/rysunki").glob("*.pdf")):
            continue                                   # PAB wydany — dawne arkusze koncepcji byłyby nieaktualne
        n = 0
        for p in sorted(d.glob("*.pdf")):
            if p.name.startswith("tom") or p.stem in widziane:
                continue
            widziane.add(p.stem)
            rozm += kopiuj(p, out / kat / "PDF_wektor")
            n += 1
            png = p.with_suffix(".png")
            chce_png = not a.bez_png_arkuszy and (not a.png_tylko or any(k in kat for k in a.png_tylko.split(",")))
            if png.exists() and chce_png:
                rozm += kopiuj(png, out / kat / "PNG_podglad")
        if n:
            spis.append((kat, f"arkusze: {n} (PDF wektorowy{'' if a.bez_png_arkuszy else ' + PNG'}) z {zr}"))

    # 04 — tomy robocze
    tomy = sorted((ROOT / "projekt/wydanie").glob("*.pdf")) + sorted((ROOT / "projekt/09_opis_i_zalaczniki").glob("*/*.pdf"))
    for p in tomy:
        rozm += kopiuj(p, out / "04_tomy_robocze" / p.parent.name)
    if tomy:
        spis.append(("04_tomy_robocze", f"pliki PDF: {len(tomy)} (tomy i elementy — wersje robocze przed wydaniem)"))

    # README
    stan = json.loads((ROOT / "raporty/stan.json").read_text(encoding="utf-8"))
    ikon = {"done": "✔", "running": "►", "todo": "○"}
    L = [f"# Dom LAMELA — pakiet postępu prac ({teraz:%d.%m.%Y, godz. %H:%M} CEST)", "",
         "Projekt koncepcyjny, budowlany i techniczny domu jednorodzinnego „Dom LAMELA” (sylweta „S” z przesuniętych brył wg",
         "szkicu Inwestora). **Stan: prace w toku — rysunki i tomy w tym pakiecie są WERSJAMI ROBOCZYMI przed wydaniem**",
         "(etap wydania w toku: po zamrożeniu modelu rysunki i tomy zostaną wygenerowane ponownie; status każdego tomu",
         "podają raporty kompletności w `02_wyniki_etapow/10_weryfikacje_i_kompletnosc_tomow`).",
         "Działka, MPZP, warunki gruntowe i dane Inwestora są PRZYKŁADOWE/FIKCYJNE; dokumenty noszą oznaczenie",
         "„PRZYKŁAD – NIE DO ZŁOŻENIA”, a pola danych osobowych i uprawnień są do uzupełnienia.", "",
         "## Etapy", ""]
    for nazwa_et, st in stan.get("stages", []):
        L.append(f"- {ikon.get(st, '·')} {nazwa_et}")
    L += ["", "## Najważniejsze (z ostatniej planszy)", ""] + [f"- {n}" for n in stan.get("notes", [])]
    L += ["", "## Zawartość folderu", "", "| Folder | Zawartość |", "|---|---|"] + [f"| `{k}` | {v} |" for k, v in spis]
    L += ["", "Uwagi:",
          "- `01_wejscie_szkic_i_interpretacja`: obowiązuje `interpretacja_szkicu_v2.png` (sylweta „S” z brył, garaż w parterze);",
          "  `interpretacja_szkicu.png` (v1) i `interpretacja_S.png` zostały odrzucone po korekcie Inwestora.",
          "- Warianty W1–W3 to etap konkursowy koncepcji; bazą koncepcji ostatecznej jest W2 z przeszczepami z W1/W3.",
          "- Rysunki PDF są wektorowe (można je dowolnie powiększać); PNG to podglądy rastrowe.",
          "- Strona katalogowa (wersja robocza): https://claude.ai/artifact/DVkqc1LzLnchNsDBNVnhTy (prywatna).",
          "- Prezentacja (16 slajdów, do pobrania jako .pptx): https://claude.ai/artifact/TexRXPDTXrH99W7nd24UVB (prywatna).",
          "- Tom PT-4 ma nazwę `PT_4_WB_…` (RPB zał. 1: WB = więcej niż jedna specjalność — elektryczna i telekomunikacyjna).",
          "- Statystyki sesji (agenci, czas, iteracje, koszt porównawczy ze źródłami): `02_wyniki_etapow/11_statystyki_sesji`.", ""]
    (out / "README.md").write_text("\n".join(L), encoding="utf-8")

    pliki = [p for p in sorted(out.rglob("*")) if p.is_file() and p.name != "README.md"]
    if not a.podziel:
        grupy = [pliki]
    else:                                    # części ≤ N MiB, pliki w kolejności folderów (struktura zachowana)
        lim, grupy, cur, sz = a.podziel * 1024 * 1024, [], [], 0
        for p in pliki:
            n = p.stat().st_size
            if cur and sz + n > lim:
                grupy.append(cur)
                cur, sz = [], 0
            cur.append(p)
            sz += n
        if cur:
            grupy.append(cur)
    for i, g in enumerate(grupy, 1):
        suf = f"_czesc_{i}_z_{len(grupy)}" if len(grupy) > 1 else ""
        zp = Path(a.out) / f"{nazwa}{suf}.zip"
        with zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
            z.write(out / "README.md", (out / "README.md").relative_to(out.parent))
            for p in g:
                z.write(p, p.relative_to(out.parent))
        tops = sorted({str(p.relative_to(out)).split("/")[0] for p in g})
        print(f"archiwum: {zp.name}  {zp.stat().st_size / 1048576:.1f} MiB  ({len(g)} plików: {', '.join(tops)})")
    print(f"folder: {out}; pliki razem {rozm / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
