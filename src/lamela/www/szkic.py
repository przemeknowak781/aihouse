"""Szkic koncepcyjny Inwestora (00_wejscie/szkic_koncepcyjny.jpg) w formie przetworzonej: wycinek serwetki z rysunkiem,
wyłuskany niebieski tusz długopisu jako maska alfa (PNG w odcieniach szarości + alfa). Na stronie maska zabarwia się
kolorem tokenu (CSS mask-image), więc działa w obu motywach. Parametry wycinka opisują zdjęcie, nie budynek."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

# wycinek serwetki z rysunkiem — ułamki szerokości/wysokości zdjęcia (bez sztućców, zegarka i nadruków)
WYCINEK = (0.226, 0.455, 0.768, 0.80)


def przetworz(src: Path, dst: Path, szer: int = 1400) -> dict:
    im = Image.open(src).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = (int(WYCINEK[0] * W), int(WYCINEK[1] * H), int(WYCINEK[2] * W), int(WYCINEK[3] * H))
    im = im.crop((x0, y0, x1, y1))
    a = np.asarray(im, dtype=np.float32)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    L = 0.299 * R + 0.587 * G + 0.114 * B
    # tło serwetki — jasność lokalna (rozmyta) → kompensacja cienia i nierównego oświetlenia
    tlo = np.asarray(Image.fromarray(L.astype(np.uint8)).filter(ImageFilter.GaussianBlur(25)), dtype=np.float32)
    niebieski = np.clip((B - R - 6.0) * 7.0, 0, 255)
    ciemny = np.clip((tlo - L - 10.0) * 5.0, 0, 255)
    alfa = np.minimum(niebieski, ciemny)
    alfa = np.where(alfa < 40, 0, alfa)
    out = Image.fromarray(alfa.astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(0.6))
    bb = out.point(lambda v: 255 if v > 60 else 0).getbbox()
    if bb:
        pad = 30
        out = out.crop((max(0, bb[0] - pad), max(0, bb[1] - pad), min(out.width, bb[2] + pad),
                        min(out.height, bb[3] + pad)))
    if out.width > szer:
        out = out.resize((szer, round(out.height * szer / out.width)), Image.LANCZOS)
    rgba = Image.new("LA", out.size, 0)
    rgba.putalpha(out)
    dst.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(dst, optimize=True)
    return dict(plik=str(dst), W=out.width, H=out.height)
