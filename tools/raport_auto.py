#!/usr/bin/env python3
"""Automatyczny raport postępu: bierze stan z raporty/stan.json i najnowsze obrazy z katalogów roboczych, składa kolaż A4.

Użycie: python3 tools/raport_auto.py [--title "..."] [--img ścieżka ...]
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import collage  # noqa: E402

SCAN = ["docs/20_koncepcja", "projekt", "www"]
SKIP = ("raporty", "node_modules", "00_demo_silnika/tmp")


def latest_images(n=6):
    files = []
    for d in SCAN:
        p = ROOT / d
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg") and not any(s in str(f) for s in SKIP):
                if f.stat().st_size > 20_000:
                    files.append(f)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    # różnorodność: max 2 obrazy z jednego katalogu
    out, per_dir = [], {}
    for f in files:
        k = str(f.parent)
        if per_dir.get(k, 0) >= 2:
            continue
        per_dir[k] = per_dir.get(k, 0) + 1
        out.append(f)
        if len(out) >= n:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title")
    ap.add_argument("--img", nargs="*", default=None)
    ap.add_argument("--cap", nargs="*", default=None)
    a = ap.parse_args()
    stan = json.loads((ROOT / "raporty/stan.json").read_text(encoding="utf-8"))
    nr = max([int(p.name.split("_")[1]) for p in (ROOT / "raporty").glob("raport_*.png")] + [0]) + 1
    if a.img:
        imgs = [ROOT / i if not Path(i).is_absolute() else Path(i) for i in a.img]
        caps = a.cap or [p.stem for p in imgs]
    else:
        imgs = latest_images()
        caps = [str(p.relative_to(ROOT)) for p in imgs]
    spec = {"nr": nr, "title": a.title or stan.get("title", "Postęp prac"), "stages": stan["stages"],
            "notes": stan.get("notes", []),
            "images": [{"path": str(p), "caption": c} for p, c in zip(imgs, caps)]}
    sp = ROOT / "raporty" / f"spec_{nr:02d}.json"
    sp.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    collage.main(str(sp))


if __name__ == "__main__":
    main()
