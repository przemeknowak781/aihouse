"""Rendery marketingowe strony www (16:9 i 4:3) — ten sam renderer co pipeline (tools/render3d: three.js, headless
Chromium), własny zestaw ujęć i oświetlenia. Kadry liczy ``render.build_views`` z geometrii modelu (glb), Słońce —
``lamela.sun`` (NOAA, Poznań). Zwraca też rzut punktów kotwiczących (adnotacje „szkicu” na renderze hero).

Wynik w katalogu cache (klucz = skrót glb + konfiguracji): <ujecie>_<proporcje>.png + rendery_www.json.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R3D = ROOT / "tools" / "render3d"

# ujęcie → (klucz widoku render.build_views, data, godzina, nadpisania cfg)
UJECIA = {
    "ogrod": ("c", "2026-06-21", "16:00", {"exposure": 1.0}),
    "ulica": ("d", "2026-06-21", "19:30", {"exposure": 1.05}),
    "lotniczy": ("a", "2026-05-20", "12:30", {"exposure": 1.0}),
    "aksonometria": ("e", "2026-03-21", "12:00", {}),
}
PROPORCJE = {"169": (1920, 1080), "43": (1600, 1200)}
WERSJA = "www-1"


def klucz_cache(glb: Path, ujecia: dict, proporcje: dict, ss: int, extra=None) -> str:
    h = hashlib.sha256(glb.read_bytes())
    h.update(json.dumps([WERSJA, ujecia, proporcje, ss, extra], sort_keys=True, default=str).encode())
    for f in ("render.js", "render.py"):
        h.update((R3D / f).read_bytes())
    return h.hexdigest()[:16]


def _slonce(data: str, godz: str) -> dict:
    from lamela.sun import sun_position
    az, el = sun_position(f"{data} {godz}")
    return {"az": round(az, 2), "el": round(el, 2), "data": data, "godz": godz}


def rzut_punktow(cam: dict, W: int, H: int, punkty: list) -> list:
    """Rzut punktów (układ budynku x→E, y→N, z↑) na obraz W×H — ta sama matematyka co three.js w render.js
    (PerspectiveCamera + lookAt, obiektyw przesuwny przez setViewOffset). Zwraca [(px, py, widoczny?)]."""
    def b2t(p):
        return (p[0], p[2], -p[1])

    def sub(a, b):
        return [a[i] - b[i] for i in range(3)]

    def dot(a, b):
        return sum(a[i] * b[i] for i in range(3))

    def cross(a, b):
        return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]

    def norm(a):
        n = math.sqrt(dot(a, a)) or 1.0
        return [x / n for x in a]
    pos, tgt = b2t(cam["pos"]), b2t(cam["target"])
    f = norm(sub(tgt, pos))
    r = norm(cross(f, [0.0, 1.0, 0.0]))
    u = cross(r, f)
    s = float(cam.get("shift") or 0.0)
    fov = math.radians(cam.get("fov", 35.0))
    tan_h = math.tan(fov / 2) * (1 + 2 * s)
    full_h = H * (1 + 2 * s)
    asp = W / full_h
    out = []
    for p in punkty:
        d = sub(b2t(p), pos)
        zc = dot(d, f)
        if zc <= 0.01:
            out.append((None, None, False))
            continue
        nx = dot(d, r) / (zc * tan_h * asp)
        ny = dot(d, u) / (zc * tan_h)
        px, py = (nx + 1) / 2 * W, (1 - ny) / 2 * full_h
        out.append((px, py, 0 <= px <= W and 0 <= py <= H))
    return out


def kadr_ogrodowy(v: dict, info: dict, W: int, H: int, drzewa: list, margines: float = 1.0) -> dict:
    """Ujęcie z poziomu oczu od ogrodu bez pnia/korony drzewa na pierwszym planie: kamerę stawia się tuż przed
    najbliższym drzewem stojącym w pasie widoku (drzewa z dzialka.yaml, układ budynku: (x, y, promień korony)),
    a kąt widzenia dobiera tak, by zmieścić szerokość bryły i jej najwyższy punkt (obiektyw przesuwny)."""
    x0, y0, z0, x1, y1, z1 = info["bbox_budynek"]
    cam = v["camera"]
    xc, yc = cam["pos"][0], cam["pos"][1]
    zeye = cam["pos"][2]
    szer = (x1 - x0) / 0.80
    blok = [ty + r + margines for tx, ty, r in drzewa if ty < y0 and abs(tx - xc) < szer / 2 + r and ty + r > yc]
    if not blok:
        return v
    yc = min(max(blok), y0 - 6.0)
    d = y0 - yc
    asp = W / H
    hfov = 2 * math.atan(szer / 2 / d)
    vfov = 2 * math.atan(math.tan(hfov / 2) / asp)
    s = 0.22
    wys = (z1 - zeye) / (d + (y1 - y0) * 0.35) / 0.92      # tangens kąta do najwyższego punktu (z zapasem)
    vfov = max(vfov, 2 * math.atan(wys / (1 + 2 * s)))
    v["camera"] = {**cam, "pos": [xc, yc, zeye], "target": [xc, yc + 100, zeye],
                   "fov": round(min(70.0, math.degrees(vfov)), 2), "shift": s}
    v["eye"] = [xc, yc]
    return v


def renderuj(glb: Path, cache: Path, ujecia: dict | None = None, proporcje: dict | None = None, ss: int = 2,
             kotwice: dict | None = None, drzewa: list | None = None, log=print) -> dict:
    """Renderuje brakujące ujęcia do ``cache``; ``kotwice`` = {nazwa: (x, y, z)} rzutowane na kadr 'ogrod'."""
    ujecia = ujecia or UJECIA
    proporcje = proporcje or PROPORCJE
    cache.mkdir(parents=True, exist_ok=True)
    meta_f = cache / "rendery_www.json"
    meta = json.loads(meta_f.read_text()) if meta_f.exists() else {"pliki": {}, "kamery": {}}
    brak = [(u, p) for u in ujecia for p in proporcje if not (cache / f"{u}_{p}.png").exists()]
    if not brak:
        log(f"  rendery: cache aktualny ({cache.name})")
        return _dopisz_kotwice(meta, kotwice)
    sys.path.insert(0, str(R3D))
    import render as R  # noqa: E402  (tools/render3d/render.py)
    from playwright.sync_api import sync_playwright
    from PIL import Image
    httpd, port = R._serve(glb.resolve())
    t0 = time.time()
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=R.CHROMIUM, headless=True,
                                    args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                          "--ignore-gpu-blocklist", "--disable-gpu-sandbox"])
            page = br.new_page(viewport={"width": 1280, "height": 900})
            page.set_default_timeout(900_000)
            page.goto(f"http://127.0.0.1:{port}/render.html")
            page.wait_for_function("window.__lamelaReady === true")
            info = page.evaluate("u => LAMELA.load(u)", "/__model.glb")
            for u, p in brak:
                key, data, godz, extra = ujecia[u]
                W, H = proporcje[p]
                v = next(x for x in R.build_views(info, W, H, key) if x["key"] == key)
                if key == "c" and drzewa:
                    v = kadr_ogrodowy(v, info, W, H, drzewa)
                if "eye" in v:
                    z = page.evaluate("p => LAMELA.groundZ(p)", [v["eye"]])[0]
                    if z is not None:
                        v["camera"]["pos"][2] = z + 1.6
                        v["camera"]["target"][2] = z + 1.6
                s = _slonce(data, godz)
                v["sun"] = {**v["sun"], **s} if key != "e" else v["sun"]
                v.update(extra)
                v["ss"] = ss
                t1 = time.time()
                res = page.evaluate("c => LAMELA.render(c)", v)
                img = R._decode(res["url"]).resize((W, H), Image.LANCZOS)
                if res.get("labels"):
                    R._draw_labels(img, res["labels"])
                img.save(cache / f"{u}_{p}.png", optimize=True)
                meta["pliki"][f"{u}_{p}"] = {"slonce": v["sun"], "W": W, "H": H, "czas_s": round(time.time() - t1, 1)}
                meta["kamery"][f"{u}_{p}"] = v["camera"]
                log(f"  render {u}_{p}: {time.time() - t1:.0f} s")
            br.close()
    finally:
        httpd.shutdown()
    meta["czas_s"] = round(time.time() - t0, 1)
    meta_f.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return _dopisz_kotwice(meta, kotwice)


def _dopisz_kotwice(meta: dict, kotwice: dict | None) -> dict:
    meta = dict(meta)
    meta["kotwice"] = {}
    if not kotwice:
        return meta
    for kadr, cam in meta.get("kamery", {}).items():
        if not kadr.startswith("ogrod_") or cam.get("type") == "ortho":
            continue
        W, H = meta["pliki"][kadr]["W"], meta["pliki"][kadr]["H"]
        pts = rzut_punktow(cam, W, H, list(kotwice.values()))
        meta["kotwice"][kadr] = {k: {"x": round(100 * px / W, 2), "y": round(100 * py / H, 2)}
                                 for k, (px, py, ok) in zip(kotwice, pts) if ok}
    return meta
