"""Proceduralne, bezszwowe (periodyczne) tekstury podstawowe dla modelu 3D — generowane deterministycznie.

Szum periodyczny: filtrowany biały szum w dziedzinie FFT (1/f^β) ⇒ tekstury kafelkują się bez szwów.
Kolor bazowy materiału jest „wypalany” w teksturę (baseColorFactor = 1).
"""
from __future__ import annotations

import io
from functools import lru_cache

import numpy as np
from PIL import Image

SIZE = 512


def _noise(n: int, beta: float, seed: int, aniso=(1.0, 1.0)) -> np.ndarray:
    rng = np.random.default_rng(seed)
    w = rng.standard_normal((n, n))
    F = np.fft.fft2(w)
    fy = np.fft.fftfreq(n)[:, None] * aniso[1]
    fx = np.fft.fftfreq(n)[None, :] * aniso[0]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1.0
    F = F / f ** beta
    F[0, 0] = 0
    r = np.real(np.fft.ifft2(F))
    r = (r - r.mean()) / (r.std() + 1e-9)
    return r


def _hex(c: str) -> np.ndarray:
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float) / 255.0


def _to_img(rgb: np.ndarray, jpeg=True) -> Image.Image:
    arr = (np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)
    im = Image.fromarray(arr, "RGB")
    if jpeg:
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=88)
        buf.seek(0)
        im = Image.open(buf)
        im.load()
    return im


def _shade(base: np.ndarray, var: np.ndarray, amp: float) -> np.ndarray:
    return base[None, None, :] * (1.0 + amp * var[..., None])


def _grain(n, seed, stripes=48, warp=6.0):
    """Słoje drewna wzdłuż osi v (pionowo w obrazie)."""
    y, x = np.mgrid[0:n, 0:n] / n
    wn = _noise(n, 2.2, seed)
    ring = np.sin((x + wn * warp / n * 8) * 2 * np.pi * stripes)
    fine = _noise(n, 1.0, seed + 1, aniso=(1.0, 0.08))
    return 0.55 * ring + 0.45 * fine


@lru_cache(maxsize=64)
def texture(name: str, color: str) -> Image.Image:
    n = SIZE
    base = _hex(color)
    y, x = np.mgrid[0:n, 0:n] / n
    if name == "drewno":                         # lamele — słoje pionowe, pas deski
        g = _grain(n, 11, stripes=22)
        band = _noise(n, 2.6, 12, aniso=(1.0, 0.02))
        rgb = _shade(base, 0.45 * g + 0.5 * band, 0.16)
    elif name == "deski":                        # deski tarasowe wzdłuż u, 7 szt./m
        k = 7
        row = np.floor(y * k)
        g = _grain(n, 21, stripes=30).T
        tone = (np.sin(row * 12.9898) * 43758.5453) % 1.0 - 0.5
        rgb = _shade(base, 0.35 * g + 0.6 * tone, 0.18)
        gap = (np.abs((y * k) % 1.0) < 0.05)
        rgb[gap] *= 0.35
    elif name == "parkiet":                      # deska podłogowa 5 szt./m, przesunięte styki
        k = 5
        row = np.floor(y * k)
        off = (row * 0.37) % 1.0
        col = np.floor((x + off) * 1.0)
        g = _grain(n, 31, stripes=26).T
        tone = (np.sin((row * 7.1 + col * 3.3) * 12.9898) * 43758.5453) % 1.0 - 0.5
        rgb = _shade(base, 0.3 * g + 0.5 * tone, 0.14)
        edge = (np.abs((y * k) % 1.0) < 0.012) | (np.abs(((x + off) * 1.0) % 1.0) < 0.004)
        rgb[edge] *= 0.8
    elif name == "trawa":
        a = _noise(n, 1.6, 41)
        b = _noise(n, 0.6, 42)
        c = _noise(n, 2.4, 43)
        rgb = _shade(base, 0.45 * a + 0.35 * b + 0.3 * c, 0.20)
        rgb[..., 0] *= 1.0 + 0.06 * c
    elif name == "lisc":
        a = _noise(n, 0.8, 51)
        b = _noise(n, 1.8, 52)
        rgb = _shade(base, 0.55 * a + 0.45 * b, 0.28)
    elif name == "sedum":
        a = _noise(n, 1.2, 61)
        b = _noise(n, 2.2, 62)
        rgb = _shade(base, 0.5 * a + 0.4 * b, 0.25)
        red = np.clip(b - 0.9, 0, 3)[..., None] * np.array([0.25, -0.1, -0.05])
        rgb = rgb + red
    elif name in ("kostka", "kostka_jasna"):     # kostka 20×10 cm, wiązanie półcegiełkowe (1 m = 5×10)
        kx, ky = 5, 10
        row = np.floor(y * ky)
        xs = x * kx + (row % 2) * 0.5
        col = np.floor(xs)
        tone = (np.sin((row * 5.3 + col * 9.7) * 12.9898) * 43758.5453) % 1.0 - 0.5
        nz = _noise(n, 1.2, 71)
        rgb = _shade(base, 0.5 * tone + 0.25 * nz, 0.18)
        jx = np.abs(xs % 1.0 - 0.5) > 0.47
        jy = np.abs((y * ky) % 1.0 - 0.5) > 0.44
        rgb[jx | jy] *= 0.55
    elif name == "plyty":                        # płyty 60×60 (1,2 m kafel → 2×2)
        k = 2
        nz = _noise(n, 1.0, 81)
        tone = (np.sin((np.floor(x * k) * 3.1 + np.floor(y * k) * 7.7) * 12.9898) * 43758.5453) % 1.0 - 0.5
        rgb = _shade(base, 0.3 * tone + 0.3 * nz, 0.10)
        j = (np.abs((x * k) % 1.0 - 0.5) > 0.49) | (np.abs((y * k) % 1.0 - 0.5) > 0.49)
        rgb[j] *= 0.7
    elif name == "asfalt":
        a = _noise(n, 0.2, 91)
        b = _noise(n, 1.6, 92)
        rgb = _shade(base, 0.5 * a + 0.35 * b, 0.12)
    elif name == "zwir":
        a = _noise(n, 0.3, 95)
        rgb = _shade(base, a, 0.18)
    elif name == "beton":
        a = _noise(n, 1.4, 101)
        b = _noise(n, 0.4, 102)
        rgb = _shade(base, 0.6 * a + 0.3 * b, 0.05)
    elif name == "tynk":
        a = _noise(n, 0.9, 111)
        b = _noise(n, 1.9, 112)
        rgb = _shade(base, 0.5 * a + 0.5 * b, 0.018)
    else:
        rgb = np.broadcast_to(base, (n, n, 3)).copy()
    return _to_img(rgb)
