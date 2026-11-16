#!/usr/bin/env python3
"""Rozpakowuje archiwa materiałów konkursowych (również zagnieżdżone ZIP-y) z poprawnym dekodowaniem polskich nazw."""
import sys, zipfile, io
from pathlib import Path

def dec(info):
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode("cp437", "replace")
    for enc in ("utf-8", "cp852", "cp1250"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return info.filename

def extract(zf: zipfile.ZipFile, dst: Path, depth=0):
    dst.mkdir(parents=True, exist_ok=True)
    for info in zf.infolist():
        name = dec(info)
        if info.is_dir():
            continue
        parts = [p for p in Path(name).parts if p not in ("..", "/", "")]
        out = dst.joinpath(*parts)
        out.parent.mkdir(parents=True, exist_ok=True)
        data = zf.read(info)
        if out.suffix.lower() == ".zip" and depth < 3:
            try:
                extract(zipfile.ZipFile(io.BytesIO(data)), out.with_suffix(""), depth + 1)
                continue
            except zipfile.BadZipFile:
                pass
        out.write_bytes(data)

if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    extract(zipfile.ZipFile(src), dst)
    print("OK", dst)
