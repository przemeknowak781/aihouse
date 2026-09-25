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


def webp(src: Path, dst: Path, cel_kb: int = 400) -> int:
    """PNG → WebP; wysoka jakość (q 92), obniżana tylko gdy plik > cel_kb (min. q 70)."""
    im = Image.open(src).convert("RGB")
    for q in (92, 88, 84, 80, 75, 70):
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


def punkty_bryly(ir) -> list:
    """Punkty obwiedni bryły do kadrowania (otoczka wypukła rzutów elementów budynku × rzędne spodu i wierzchu)."""
    from shapely.geometry import MultiPoint
    pts, z0, z1 = [], 1e9, -1e9
    for p in ir.prisms:
        if p.meta.get("group") in ("otoczenie", "teren", "fundamenty") or p.kind in ("terrain", "footing"):
            continue
        pts += list(p.polygon)
        z0, z1 = min(z0, p.z0), max(z1, p.z1)
    hull = MultiPoint(pts).convex_hull
    return [(x, y, z) for x, y in list(hull.exterior.coords)[:-1] for z in (max(z0, -0.3), z1)]


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




def glb_na_gltf_json(glb: Path, cel: Path) -> Path:
    """GLB → glTF (JSON) z buforem osadzonym jako data URI (base64). Platforma publikacji nie serwuje .glb, a serwuje
    .json; GLTFLoader.parse() rozpoznaje JSON po braku nagłówka „glTF” i wczytuje go bez zmian w widoku 3D."""
    import base64
    import struct
    b = glb.read_bytes()
    magic, ver, dl = struct.unpack_from("<4sII", b, 0)
    if magic != b"glTF":
        raise ValueError("to nie jest plik GLB")
    off, js, binb = 12, None, b""
    while off < dl:
        clen, ctyp = struct.unpack_from("<II", b, off)
        chunk = b[off + 8: off + 8 + clen]
        if ctyp == 0x4E4F534A:
            js = json.loads(chunk.decode("utf-8"))
        elif ctyp == 0x004E4942:
            binb = chunk
        off += 8 + clen
    if js is None:
        raise ValueError("brak części JSON w GLB")
    if js.get("buffers"):
        js["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(binb).decode("ascii")
        js["buffers"][0]["byteLength"] = len(binb)
    cel.write_text(json.dumps(js, separators=(",", ":")), encoding="utf-8")
    return cel

def wydziel_svg(html: str, assets: Path, prog: int = 6000) -> tuple[str, int]:
    """Duże rysunki SVG (rzuty, elewacje, przekroje, działka) → osobne pliki assets/svg/*.svg, wstawiane do strony
    skryptem (fetch → outerHTML), dzięki czemu zachowują tokeny CSS motywu jasnego/ciemnego, a index.html jest lekki
    (strona czytelna do przeglądu przed publikacją). Małe SVG (separatory, ikony) zostają w treści."""
    (assets / "svg").mkdir(parents=True, exist_ok=True)
    n = [0]

    def rep(m):
        s = m.group(0)
        if len(s) < prog:
            return s
        n[0] += 1
        name = f"svg/rys{n[0]:02d}.svg"
        body = s if "xmlns=" in s[:400] else s.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        (assets / name).write_text(body, encoding="utf-8")
        return f'<div class="svg-ext" data-svg="assets/{name}"></div>'

    html = re.sub(r"<svg\b.*?</svg>", rep, html, flags=re.S)
    loader = ("<style>.svg-ext{min-height:12rem}</style><script>(function(){"
              "Array.prototype.forEach.call(document.querySelectorAll('.svg-ext[data-svg]'),function(el){"
              "fetch(el.getAttribute('data-svg')).then(function(r){if(!r.ok)throw new Error(r.status);return r.text();})"
              ".then(function(t){el.outerHTML=t;})"
              ".catch(function(){el.textContent='Rysunek nie wczytał się. Odśwież stronę.';});});})();</script>")
    i = html.find("</main>")
    html = html[:i] + loader + html[i:] if i >= 0 else html + loader
    return html, n[0]

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
        sorted(str(p) for p in (ROOT / "src" / "lamela" / "model3d").glob("*.py"))
    m = D["model"]
    pkt = punkty_bryly(D["ir"])
    z_ter = float(((D["ir"].meta or {}).get("dzialka") or {}).get("teren_z_budynek") or 0.0)
    # kamera: na działce ≥ 1,8 m od granic (żywopłoty) albo po drugiej stronie ulicy (pas drogi + 4,6 m, poza działką)
    droga = m.dz.poly_bud(m.dz.raw["droga"]["linie_rozgraniczajace"])
    obszary = {"dzialka": m.dz.obrys.buffer(-1.8), "droga": droga.buffer(4.6).difference(m.dz.obrys.buffer(0.5))}
    plan = RN.plan_ujec(RN.UJECIA, RN.PROPORCJE, pkt, obszary, D["drzewa_bud"], z_ter)
    kam = {k: [v["cam"], [t[0] for t in v["pomin"]]] for k, v in plan.items()}
    klucz = RN.klucz_cache(wej, RN.UJECIA, RN.PROPORCJE, ss, extra=kam)
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
    gotowe = {(): glb}

    def glb_bez(ids: tuple) -> Path:
        if ids not in gotowe:
            import copy
            from lamela.model3d import export_glb
            ir2 = copy.copy(D["ir"])
            ir2.prisms = [p for p in D["ir"].prisms if p.element not in ids]
            ir2.meshes = [q for q in D["ir"].meshes if q.element not in ids]
            gotowe[ids] = cache / "pipeline" / f"render_bez_{'_'.join(ids)}.glb"
            export_glb(ir2, gotowe[ids], model=m)
        return gotowe[ids]
    R = RN.renderuj(glb_bez, rdir, plan, ss=ss, kotwice=kotwice, log=log)
    for u in RN.UJECIA:
        for p in RN.PROPORCJE:
            n = webp(rdir / f"{u}_{p}.png", assets / f"{u}_{p}.webp")
            print(f"    {u}_{p}.webp: {n / 1024:.0f} kB", flush=True)
    print("[4] szkic Inwestora (maska tuszu)…", flush=True)
    szkic = przetworz(ROOT / "00_wejscie" / "szkic_koncepcyjny.jpg", assets / "szkic.png")
    print("[5] rysunki SVG i index.html…", flush=True)
    html, W = ST.zloz(D, tr, R, szkic, (assets / "model.glb").stat().st_size / 1e6, Path(a.budynek).parent, teraz)
    html, n_svg = wydziel_svg(html, assets)
    if (assets / "model.glb").exists():                     # publikacja: .glb nie jest serwowany → glTF JSON
        glb_na_gltf_json(assets / "model.glb", assets / "model.gltf.json")
        (assets / "model.glb").unlink()
        html = html.replace('"assets/model.glb"', '"assets/model.gltf.json"')
    print(f"    rysunki SVG wydzielone do assets/svg: {n_svg}", flush=True)
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
