#!/usr/bin/env python3
"""Wspólna postprodukcja wizualizacji konkursowych – jeden „look” całego kompletu (docs/50_research: metodyka wizualizacji).

Kroki (wszystkie łagodne, parametry w PRESETS): 1) krzywa tonalna (lekki S, uniesione czernie), 2) split-toning (ciepłe światła,
chłodne cienie), 3) nasycenie selektywne (zieleń i niebo −, ceramika/granit neutralnie), 4) poświata świateł (bloom z progu
luminancji), 5) atmosfera (delikatna mgiełka w górnej części kadru dla widoków z lotu ptaka), 6) winieta, 7) wyostrzenie (unsharp),
8) ziarno. Wejście PNG/JPG (sRGB), wyjście JPG q95 + podgląd przed/po.
Użycie: postprodukcja.py IN OUT [--preset dzien|zmierzch|wnetrze|lot] [--compare PATH]
"""
import sys, argparse
import numpy as np
from PIL import Image, ImageFilter

PRESETS = {
    "dzien":    dict(contrast=0.06, lift=0.000, warm=0.030, cool=0.010, sat=1.00, green=-0.08, sky=-0.04, bloom=0.08, bloom_th=0.88, haze=0.00, vign=0.08, sharp=0.40, grain=0.006),
    "lot":      dict(contrast=0.05, lift=0.000, warm=0.025, cool=0.012, sat=0.98, green=-0.10, sky=-0.05, bloom=0.05, bloom_th=0.92, haze=0.06, vign=0.07, sharp=0.35, grain=0.005),
    "zmierzch": dict(contrast=0.08, lift=0.000, warm=0.050, cool=0.030, sat=1.04, green=-0.03, sky=0.00, bloom=0.30, bloom_th=0.68, haze=0.00, vign=0.12, sharp=0.40, grain=0.008),
    "wnetrze":  dict(contrast=0.05, lift=0.000, warm=0.035, cool=0.008, sat=1.00, green=-0.03, sky=0.00, bloom=0.12, bloom_th=0.84, haze=0.00, vign=0.06, sharp=0.40, grain=0.005),
}


def srgb_to_lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def luminance(rgb):
    return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]


def process(img, p):
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    h, w, _ = a.shape
    # 1 tone curve (in display space): gentle S around 0.45, lifted blacks
    c = p["contrast"]
    a = a + c * (a - 0.45) * (1 - np.abs(2 * a - 1)) * 1.6
    a = p["lift"] + a * (1 - p["lift"])
    # 2 split toning by luminance
    L = luminance(a)[..., None]
    warm = np.array([1.0, 0.55, 0.15], np.float32)
    cool = np.array([0.15, 0.45, 1.0], np.float32)
    a = a + p["warm"] * (L ** 1.5) * (warm - 0.5) + p["cool"] * ((1 - L) ** 2) * (cool - 0.5)
    # 3 saturation (global + selective green and sky)
    L = luminance(a)[..., None]
    a = L + (a - L) * p["sat"]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    greenish = np.clip((g - np.maximum(r, b)) * 4, 0, 1)[..., None]
    skyish = np.clip((b - np.maximum(r, g)) * 3, 0, 1)[..., None] * np.linspace(1, 0.2, h, dtype=np.float32)[:, None, None]
    L = luminance(a)[..., None]
    a = a + greenish * p["green"] * (a - L) + skyish * p["sky"] * (a - L)
    a = np.clip(a, 0, 1)
    # 4 bloom (linear light)
    lin = srgb_to_lin(a)
    if p["bloom"] > 0:
        Ll = luminance(a)
        mask = np.clip((Ll - p["bloom_th"]) / (1 - p["bloom_th"] + 1e-6), 0, 1)[..., None] * lin
        mimg = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8))
        bl = np.zeros_like(lin)
        for rad, wgt in ((max(2, w // 300), 0.5), (max(4, w // 90), 0.35), (max(8, w // 30), 0.15)):
            bl += wgt * np.asarray(mimg.filter(ImageFilter.GaussianBlur(rad)), dtype=np.float32) / 255.0
        lin = lin + p["bloom"] * bl
    a = lin_to_srgb(lin)
    # 5 haze (top-weighted, toward a pale warm-grey)
    if p["haze"] > 0:
        ramp = np.clip(1 - np.linspace(0, 1.6, h, dtype=np.float32), 0, 1)[:, None, None] ** 1.5
        a = a * (1 - p["haze"] * ramp) + np.array([0.86, 0.87, 0.89], np.float32) * p["haze"] * ramp
    # 6 vignette (elliptical, soft)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = a * (1 - p["vign"] * np.clip(d - 0.55, 0, 1) ** 1.6)[..., None]
    a0 = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    m0, m1 = luminance(a0).mean(), luminance(np.clip(a, 0, 1)).mean()
    if m1 > 1e-3:
        a = np.clip(a * (m0 / m1) ** 0.85, 0, 1)        # keep overall exposure close to the render
    out = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    # 7 sharpen
    if p["sharp"] > 0:
        out = out.filter(ImageFilter.UnsharpMask(radius=max(1.0, w / 2400), percent=int(p["sharp"] * 100), threshold=2))
    # 8 grain (luminance, fine)
    if p["grain"] > 0:
        rng = np.random.default_rng(7)
        n = rng.normal(0, p["grain"], (h, w, 1)).astype(np.float32)
        a = np.asarray(out, dtype=np.float32) / 255.0 + n
        out = Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--preset", default="dzien", choices=PRESETS.keys())
    ap.add_argument("--compare")
    a = ap.parse_args()
    im = Image.open(a.inp)
    res = process(im, PRESETS[a.preset])
    res.save(a.out, quality=95, subsampling=0)
    if a.compare:
        w = 1100
        l = im.convert("RGB").resize((w, int(im.size[1] * w / im.size[0])))
        r = res.resize(l.size)
        c = Image.new("RGB", (w * 2 + 10, l.size[1]), "white")
        c.paste(l, (0, 0)); c.paste(r, (w + 10, 0))
        c.save(a.compare, quality=88)
    print(a.out)


if __name__ == "__main__":
    main()
