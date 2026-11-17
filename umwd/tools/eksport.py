#!/usr/bin/env python3
"""Eksport plansz do postaci elektronicznej wymaganej Regulaminem.

Etap II (R-129–R-133, S-01): plansze 100×70 cm poziomo, JPG lub TIFF, 300 dpi → 11 811 × 8 268 px, każdy plik ≤ 100 MB;
plansze pomniejszone do A3 300 dpi (4 961 × 3 508 px); nazwy neutralne bez numeru identyfikacyjnego (PLANSZA_1.jpg …,
PLANSZA_1_A3.jpg); obrazy spłaszczone, bez warstw i bez metadanych autora (R-084, R-127, R-133).
Etap I (R-081–R-089): 2 plansze, te same zasady → build/eksport/etap1/.

Źródło: build/plansze/etap{1,2}_P*.pdf (wektorowe, 1000×700 mm) rasteryzowane pdftoppm w 300 dpi (bez interpolacji
podglądów PNG). Kontrole: wymiar w pikselach, gęstość 300 dpi zapisana w JFIF, rozmiar pliku, brak EXIF/XMP/komentarzy.
Użycie: eksport.py [--etap 1|2|oba] [--plansze 1,3] [--jakosc 92]
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "build" / "plansze"
OUT = ROOT / "build" / "eksport"
FULL = (11811, 8268)        # 1000 × 700 mm @ 300 dpi
A3 = (4961, 3508)           # 420 × 297 mm @ 300 dpi
LIMIT = 100 * 1024 * 1024   # R-131 / S-01


def rasterize(pdf: Path, tmp: Path) -> Image.Image:
    base = tmp / pdf.stem
    subprocess.run(["pdftoppm", "-q", "-r", "300", "-singlefile", "-png", "-aa", "yes", "-aaVector", "yes", str(pdf), str(base)], check=True)
    im = Image.open(str(base) + ".png").convert("RGB")
    if im.size != FULL:                       # page box rounding (±1 px) → exact target size
        im = im.resize(FULL, Image.LANCZOS)
    return im


def save_clean(im: Image.Image, path: Path, q: int):
    # brand-new image object → no info/exif/icc carried over; JFIF density 300 dpi; no comment
    clean = Image.new("RGB", im.size)
    clean.paste(im)
    clean.save(path, "JPEG", quality=q, subsampling=0, optimize=True, dpi=(300, 300))
    return path.stat().st_size


def check(path: Path, size):
    im = Image.open(path)
    ok = im.size == size and round(im.info.get("dpi", (0, 0))[0]) == 300 and path.stat().st_size <= LIMIT
    leaks = [k for k in ("exif", "xmp", "comment", "icc_profile", "photoshop") if k in im.info]
    return ok and not leaks, {"plik": path.name, "px": im.size, "dpi": im.info.get("dpi"), "MB": round(path.stat().st_size / 2**20, 1), "metadane": leaks}


def run(etap: int, which, q: int):
    pdfs = sorted(SRC.glob(f"etap{etap}_P*.pdf"), key=lambda p: int(re.search(r"P(\d+)", p.stem).group(1)))
    if which:
        pdfs = [p for p in pdfs if int(re.search(r"P(\d+)", p.stem).group(1)) in which]
    od = OUT if etap == 2 else OUT / "etap1"
    od.mkdir(parents=True, exist_ok=True)
    rep = []
    with tempfile.TemporaryDirectory() as td:
        for pdf in pdfs:
            n = int(re.search(r"P(\d+)", pdf.stem).group(1))
            im = rasterize(pdf, Path(td))
            f1 = od / f"PLANSZA_{n}.jpg"
            qq = q
            while save_clean(im, f1, qq) > LIMIT and qq > 70:
                qq -= 4
            f2 = od / f"PLANSZA_{n}_A3.jpg"
            save_clean(im.resize(A3, Image.LANCZOS), f2, 92)
            for f, s in ((f1, FULL), (f2, A3)):
                ok, info = check(f, s)
                info["ok"] = ok
                rep.append(info)
                print(("✔" if ok else "✗"), info)
    (od / "kontrola_eksportu.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return all(r["ok"] for r in rep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etap", default="2", choices=["1", "2", "oba"])
    ap.add_argument("--plansze", default="")
    ap.add_argument("--jakosc", type=int, default=92)
    a = ap.parse_args()
    which = {int(x) for x in a.plansze.split(",") if x.strip()}
    ok = True
    for e in ((1, 2) if a.etap == "oba" else (int(a.etap),)):
        ok &= run(e, which, a.jakosc)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
