#!/usr/bin/env python3
"""Strona katalogowa „Dom LAMELA” (marka przykładowa „Pasmo i Cień”) generowana w całości z modelu.

    PYTHONPATH=src python3 tools/buduj_www.py                  # model/*.yaml → www/dist/ (index.html + assets/)
    PYTHONPATH=src python3 tools/buduj_www.py --szybko         # rendery w niższej jakości (podgląd, ~3× szybciej)
    PYTHONPATH=src python3 tools/buduj_www.py --bez-renderow   # bez nowych renderów (użyje cache, jeśli jest)

Uruchamiać po każdej zmianie modelu. Etapy: dane z modelu i modułów obliczeń (lamela.www.dane) → eksport glb
(lamela.pipeline, bez renderów pipeline'u) → rendery www 16:9 i 4:3 (lamela.www.rendery; cache w build/www/rendery/,
klucz = treść modelu + kod eksportu i renderera) → WebP → szkic Inwestora (maska) → rysunki SVG (rzuty, elewacje,
przekroje, przegrody, działka) → index.html (lamela.www.strona; treści i ceny PRZYKŁADOWE z www/tresc.yaml) →
raporty w www/raport/ (dane_strony.json, raport_budowy.json) → kontrola limitów (strona ≤ 16 MB, obraz ≤ 15 MB, razem ≤ 64 MB, zewnętrzne hosty tylko z listy dozwolonych).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from PIL import Image  # noqa: E402

from lamela.www import dane as DN  # noqa: E402
from lamela.www import rendery as RN  # noqa: E402
from lamela.www import schematy as SC  # noqa: E402
from lamela.www import strona as ST  # noqa: E402
from lamela.www.szkic import przetworz  # noqa: E402

HOSTY_OK = ("https://cdn.jsdelivr.net/npm/", "https://cdnjs.cloudflare.com/", "https://fonts.googleapis.com",
            "https://fonts.gstatic.com")
LIMIT_STRONA, LIMIT_OBRAZ, LIMIT_RAZEM = 16e6, 15e6, 64e6


def webp(src: Path, dst: Path, cel_kb: int = 380) -> int:
    """PNG → WebP; jakość obniżana, aż plik ≤ cel_kb (min. q 62)."""
    im = Image.open(src).convert("RGB")
    for q in (84, 80, 76, 72, 68, 62):
        im.save(dst, "WEBP", quality=q, method=6)
        if dst.stat().st_size <= cel_kb * 1024:
            break
    return dst.stat().st_size


def kontrola(dist: Path, html: str) -> dict:
    pliki = {str(p.relative_to(dist)): p.stat().st_size for p in dist.rglob("*") if p.is_file()}
    razem = sum(pliki.values())
    obcy = sorted({u for u in re.findall(r'''(?:src|href)=["'](https?://[^"']+)''', html) if not u.startswith(HOSTY_OK)})
    css_url = sorted({u for u in re.findall(r"url\((https?://[^)]+)\)", html)})
    bledy = []
    if pliki.get("index.html", 0) > LIMIT_STRONA:
        bledy.append("index.html > 16 MB")
    bledy += [f"{k} > 15 MB" for k, v in pliki.items() if v > LIMIT_OBRAZ]
    if razem > LIMIT_RAZEM:
        bledy.append("razem > 64 MB")
    if obcy or css_url:
        bledy.append(f"niedozwolone hosty: {obcy + css_url}")
    for zakazane in (r"<!doctype", r"<html[\s>]", r"<head[\s>]", r"<body[\s>]", r"<iframe", r"window\.print",
                     r"\balert\(", r"\bconfirm\(", r"\bprompt\(", r"\sdownload[\s=>]", r"<form[^>]*\saction=",
                     r"type=\"password\"", r"cc-number|card|karta płatnicza"):
        if re.search(zakazane, html, flags=re.I):
            bledy.append(f"zakazany element: {zakazane}")
    return dict(pliki=pliki, razem=razem, bledy=bledy)


def podglad(html: str, dist: Path, cel: Path):
    """Lokalny podgląd z minimalnym szkieletem dokumentu (jak dodaje platforma: charset, viewport) — tylko do testów:
    python3 -m http.server --directory build/www/podglad."""
    cel.mkdir(parents=True, exist_ok=True)
    (cel / "index.html").write_text('<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" '
                                    'content="width=device-width, initial-scale=1, viewport-fit=cover"></head><body>\n'
                                    + html + '</body></html>\n', encoding="utf-8")
    link = cel / "assets"
    if link.is_symlink() or link.exists():
        link.unlink() if link.is_symlink() else shutil.rmtree(link)
    link.symlink_to((dist / "assets").resolve(), target_is_directory=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budynek", default=str(ROOT / "model" / "budynek.yaml"))
    ap.add_argument("--dzialka", default=str(ROOT / "model" / "dzialka.yaml"))
    ap.add_argument("--wyposazenie", default=str(ROOT / "model" / "wyposazenie.yaml"))
    ap.add_argument("--tresc", default=str(ROOT / "www" / "tresc.yaml"))
    ap.add_argument("--out", default=str(ROOT / "www" / "dist"))
    ap.add_argument("--cache", default=str(ROOT / "build" / "www"))
    ap.add_argument("--szybko", action="store_true", help="rendery ss=1 (podgląd)")
    ap.add_argument("--bez-renderow", action="store_true")
    a = ap.parse_args(argv)
    t0 = time.time()
    teraz = datetime.now()
    dist, cache = Path(a.out), Path(a.cache)
    assets = dist / "assets"
    if dist.exists():
        shutil.rmtree(dist)
    assets.mkdir(parents=True)
    tr = yaml.safe_load(Path(a.tresc).read_text(encoding="utf-8"))
    print("[1] dane z modelu i modułów obliczeń…", flush=True)
    D = DN.zbierz(a.budynek, a.dzialka, a.wyposazenie)
    print(f"    PU {D['pow']['PU']} m², zabudowa {D['wsk']['pow_zabudowy']['wartosc']:.2f} m², "
          f"EP {D['en']['EP']:.1f}, działka min. {D['dzialka_min']['szer']} × {D['dzialka_min']['gl']} m", flush=True)
    print("[2] eksport glb (lamela.pipeline)…", flush=True)
    from lamela.pipeline import run as pipeline
    rep = pipeline(a.budynek, a.dzialka, out=str(cache / "pipeline"), render=False, verbose=False)
    glb = Path(rep["glb"]["plik"]) if isinstance(rep.get("glb"), dict) and rep["glb"].get("plik") else \
        cache / "pipeline" / f"{Path(a.budynek).stem}.glb"
    shutil.copy2(glb, assets / "model.glb")
    return _dalej(a, D, tr, glb, dist, assets, cache, teraz, t0)


def _dalej(a, D, tr, glb, dist, assets, cache, teraz, t0) -> int:
    print("[3] rendery www (16:9, 4:3)…", flush=True)
    ss = 1 if a.szybko else 2
    wej = [a.budynek, a.dzialka] + sorted(str(p) for p in (ROOT / "src" / "lamela").glob("*.py")) + \
        sorted(str(p) for p in (ROOT / "src" / "lamela" / "model3d").glob("*.py")) + [str(Path(RN.__file__))]
    m = D["model"]
    pomin = RN.drzewa_przeslaniajace(D["drzewa_bud"], m.bbox())
    klucz = RN.klucz_cache(wej, RN.UJECIA, RN.PROPORCJE, ss, extra=[t[0] for t in pomin])
    rdir = cache / "rendery" / klucz
    kotwice = SC.kotwice_szkicu(D)
    if a.bez_renderow and not rdir.exists():
        stare = sorted((cache / "rendery").glob("*/rendery_www.json"), key=lambda p: p.stat().st_mtime)
        if not stare:
            print("    brak renderów w cache — uruchom bez --bez-renderow", flush=True)
            return 2
        rdir = stare[-1].parent
        print(f"    UWAGA: rendery z cache {rdir.name} (model mógł się zmienić)", flush=True)
    log = lambda s: print("   ", s, flush=True)  # noqa: E731
    glb_ogrod = glb
    if pomin and not (rdir / "ogrod_169.png").exists():
        import copy
        from lamela.model3d import export_glb
        ids = {t[0] for t in pomin}
        ir2 = copy.copy(D["ir"])
        ir2.prisms = [p for p in D["ir"].prisms if p.element not in ids]
        ir2.meshes = [q for q in D["ir"].meshes if q.element not in ids]
        glb_ogrod = cache / "pipeline" / "render_ogrod.glb"
        export_glb(ir2, glb_ogrod, model=m)
        print(f"    ujęcie od ogrodu bez drzew przesłaniających elewację: {', '.join(sorted(ids))}", flush=True)
    ogr = {k: v for k, v in RN.UJECIA.items() if k == "ogrod"}
    R = RN.renderuj(glb_ogrod, rdir, ujecia=ogr, ss=ss, kotwice=kotwice, log=log)
    R = RN.renderuj(glb, rdir, ujecia={k: v for k, v in RN.UJECIA.items() if k not in ogr}, ss=ss, kotwice=kotwice, log=log)
    R["pominiete_drzewa"] = [dict(id=t[0], gatunek=t[4]) for t in pomin]
    for u in RN.UJECIA:
        for p in RN.PROPORCJE:
            n = webp(rdir / f"{u}_{p}.png", assets / f"{u}_{p}.webp")
            print(f"    {u}_{p}.webp: {n / 1024:.0f} kB", flush=True)
    print("[4] szkic Inwestora (maska tuszu)…", flush=True)
    szkic = przetworz(ROOT / "00_wejscie" / "szkic_koncepcyjny.jpg", assets / "szkic.png")
    print("[5] rysunki SVG i index.html…", flush=True)
    html, W = ST.zloz(D, tr, R, szkic, (assets / "model.glb").stat().st_size / 1e6, Path(a.budynek).parent, teraz)
    (dist / "index.html").write_text(html, encoding="utf-8")
    podglad(html, dist, cache / "podglad")
    dane = dict(wygenerowano=teraz.isoformat(timespec="seconds"), model=D["meta"], wartosci=W,
                PU=D["pow"]["PU"], PU_kond=D["pow"]["PU_kond"], dzialka_min={k: v for k, v in D["dzialka_min"].items()
                                                                              if k != "metoda"},
                EP=D["en"]["EP"], EP_max=D["en"]["EP_max"], rendery=R.get("pliki"), kotwice=R.get("kotwice"),
                cache_renderow=str(rdir.relative_to(ROOT)) if rdir.is_relative_to(ROOT) else str(rdir))
    rap = dist.parent / "raport"
    rap.mkdir(parents=True, exist_ok=True)
    (rap / "dane_strony.json").write_text(json.dumps(dane, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    k = kontrola(dist, html)
    print(f"[6] kontrola: index.html {k['pliki']['index.html'] / 1e6:.2f} MB, razem {k['razem'] / 1e6:.2f} MB, "
          f"{len(k['pliki'])} plików; czas {time.time() - t0:.0f} s", flush=True)
    for b in k["bledy"]:
        print("    BŁĄD:", b, flush=True)
    (rap / "raport_budowy.json").write_text(json.dumps(k, ensure_ascii=False, indent=1), encoding="utf-8")
    return 1 if k["bledy"] else 0


if __name__ == "__main__":
    sys.exit(main())
