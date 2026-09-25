#!/usr/bin/env python3
"""Rendery wizualizacyjne modelu (.glb) — three.js w headless Chromium (Playwright), 2× supersampling → PNG.

Użycie:
    PYTHONPATH=src python3 tools/render3d/render.py --glb build/test/dom_testowy.glb --out build/test/rendery
    opcje: --views a,b,c,d,e,f,g  --size 2400x1500  --ss 2  --tile 900

Widoki:
  a  lotniczy z płd.-wsch. (21.03, 12:00)          d  od ulicy (północ, 21.06, 19:30)
  b  lotniczy z płd.-zach. (21.06, 15:00)          e  aksonometria rozwarstwiona kondygnacji (21.03, 12:00)
  c  z poziomu oczu z ogrodu (płd., 21.06, 15:00)  f  elewacja płd. — rzut prostokątny (21.06, 15:00)
  g  analiza nasłonecznienia: widoki z góry 21.03 / 21.06 / 21.12 × 9:00 / 12:00 / 15:00 (siatka 3×3)
Pozycja Słońca: lamela.sun (algorytm NOAA) dla Poznania, czas Europe/Warsaw.
Wymaga: npm install w tools/render3d (three, n8ao, postprocessing); Chromium: /opt/pw-browsers/chromium.
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
import socket
import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lamela.sun import sun_position  # noqa: E402

CHROMIUM = "/opt/pw-browsers/chromium"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

VIEW_NAMES = {
    "a": "a_lotniczy_SE", "b": "b_lotniczy_SW", "c": "c_ogrod_S_poziom_oczu", "d": "d_ulica_N",
    "e": "e_aksonometria_rozwarstwiona", "f": "f_elewacja_S_orto", "g": "g_naslonecznienie_3x3",
}


# --------------------------------------------------------------------------------------------------
# Serwer HTTP (strona renderera + plik modelu)
# --------------------------------------------------------------------------------------------------
class _Handler(SimpleHTTPRequestHandler):
    glb_path: Path = None

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/__model.glb":
            data = self.glb_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "model/gltf-binary")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def guess_type(self, path):
        if str(path).endswith(".js"):
            return "text/javascript"
        return super().guess_type(path)


def _serve(glb: Path):
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    handler = type("H", (_Handler,), {"glb_path": glb})
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(handler, directory=str(HERE)))
    th = threading.Thread(target=httpd.serve_forever, daemon=True)
    th.start()
    return httpd, port


# --------------------------------------------------------------------------------------------------
# Geometria kamer
# --------------------------------------------------------------------------------------------------
def _dir(az_deg: float, el_deg: float):
    a, e = math.radians(az_deg), math.radians(el_deg)
    return (math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))


def _corners(bb):
    x0, y0, z0, x1, y1, z1 = bb
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]


def _ortho_fit(bb, az, el, aspect, margin=1.08):
    """Połowa wysokości kadru ortogonalnego mieszczącego bbox (widok z azymutu az, wysokości el)."""
    d = _dir(az, el)
    fwd = (-d[0], -d[1], -d[2])
    up0 = (0, 0, 1)
    rx = (fwd[1] * up0[2] - fwd[2] * up0[1], fwd[2] * up0[0] - fwd[0] * up0[2], fwd[0] * up0[1] - fwd[1] * up0[0])
    n = math.sqrt(sum(c * c for c in rx)) or 1
    rx = tuple(c / n for c in rx)
    uy = (rx[1] * fwd[2] - rx[2] * fwd[1], rx[2] * fwd[0] - rx[0] * fwd[2], rx[0] * fwd[1] - rx[1] * fwd[0])
    cs = _corners(bb)
    xs = [sum(p[i] * rx[i] for i in range(3)) for p in cs]
    ys = [sum(p[i] * uy[i] for i in range(3)) for p in cs]
    hw, hh = (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    center = tuple(cx * rx[i] + cy * uy[i] for i in range(3))
    # składowa wzdłuż kierunku patrzenia — środek bboxa
    bc = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
    t = sum(bc[i] * fwd[i] for i in range(3))
    center = tuple(center[i] + t * fwd[i] for i in range(3))
    return max(hh, hw / aspect) * margin, center


def build_views(info: dict, W: int, H: int, only: str) -> list[dict]:
    bb = info["bbox_budynek"]
    meta = info.get("meta") or {}
    dz = meta.get("dzialka") or {}
    aspect = W / H
    x0, y0, z0, x1, y1, z1 = bb
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    zc = (z0 + z1) / 2
    Wd, Dd, Hh = x1 - x0, y1 - y0, z1 - z0
    R = 0.5 * math.sqrt(Wd ** 2 + Dd ** 2 + Hh ** 2)
    zt = dz.get("teren_z_budynek", z0)
    shadow_near = [x0 - 22, y0 - 22, zt - 1, x1 + 22, y1 + 22, z1 + 1]
    groups_all = {g: True for g in info["groups"]}
    views = []

    def sun(date, hour, minute=0):
        az, el = sun_position(f"{date} {hour:02d}:{minute:02d}")
        return {"az": round(az, 2), "el": round(el, 2), "data": date, "godz": f"{hour:02d}:{minute:02d}"}

    if "a" in only or "b" in only:
        for key, az_cam, s in (("a", 142.0, sun("2026-03-21", 12)), ("b", 218.0, sun("2026-06-21", 15))):
            if key not in only:
                continue
            el_cam = 27.0
            fov = 30.0
            dist = R / math.tan(math.radians(fov / 2)) * 1.25
            d = _dir(az_cam, el_cam)
            tgt = (cx, cy, zc - 0.8)
            pos = tuple(tgt[i] + d[i] * dist for i in range(3))
            views.append({"key": key, "name": VIEW_NAMES[key], "width": W, "height": H,
                          "camera": {"type": "persp", "pos": pos, "target": tgt, "fov": fov},
                          "sun": s, "groups": groups_all, "bg": "sky", "fog": True, "fogNear": 180, "fogFar": 1400,
                          "shadowBox": shadow_near, "exposure": 1.0})
    if "c" in only:
        s = sun("2026-06-21", 15)
        vfov = 34.0
        hfov = 2 * math.degrees(math.atan(math.tan(math.radians(vfov / 2)) * aspect))
        shift = 0.18
        width_need = Wd / 0.78
        dist = width_need / 2 / math.tan(math.radians(hfov / 2))
        top_need = (z1 - (zt + 1.6)) / 0.82
        dist = max(dist, top_need / (math.tan(math.radians(vfov / 2)) * (1 + 2 * shift)))
        ob = dz.get("obrys")
        ycam = y0 - dist
        if ob:
            ymin = min(p[1] for p in ob) + 1.2
            if ycam < ymin:
                ycam = ymin
                d_eff = y0 - ycam
                need_h = 2 * math.degrees(math.atan(width_need / 2 / d_eff))
                vfov = min(62.0, 2 * math.degrees(math.atan(math.tan(math.radians(need_h / 2)) / aspect)))
        xcam = cx - 0.06 * Wd
        views.append({"key": "c", "name": VIEW_NAMES["c"], "width": W, "height": H, "eye": [xcam, ycam],
                      "camera": {"type": "persp", "pos": [xcam, ycam, zt + 1.6], "target": [xcam, ycam + 100, zt + 1.6],
                                 "fov": vfov, "shift": shift},
                      "sun": s, "groups": groups_all, "bg": "sky", "fog": True, "fogNear": 120, "fogFar": 1200,
                      "shadowBox": shadow_near, "exposure": 1.0})
    if "d" in only:
        s = sun("2026-06-21", 19, 30)
        jz = dz.get("jezdnia")
        vfov = 34.0
        shift = 0.18
        hfov = 2 * math.degrees(math.atan(math.tan(math.radians(vfov / 2)) * aspect))
        width_need = Wd / 0.78
        dist = width_need / 2 / math.tan(math.radians(hfov / 2))
        top_need = (z1 - (zt + 1.6)) / 0.82
        dist = max(dist, top_need / (math.tan(math.radians(vfov / 2)) * (1 + 2 * shift)))
        ycam = y1 + dist
        if jz:
            ys = [p[1] for p in jz]
            yroad = (min(ys) + max(ys)) / 2 if min(ys) > y1 else None
            if yroad is not None:
                ycam = min(ycam, yroad) if ycam > yroad else ycam
                d_eff = ycam - y1
                need_h = 2 * math.degrees(math.atan(width_need / 2 / d_eff))
                vfov = min(64.0, max(vfov, 2 * math.degrees(math.atan(math.tan(math.radians(need_h / 2)) / aspect))))
        xcam = cx + 0.08 * Wd
        views.append({"key": "d", "name": VIEW_NAMES["d"], "width": W, "height": H, "eye": [xcam, ycam],
                      "camera": {"type": "persp", "pos": [xcam, ycam, zt + 1.6], "target": [xcam, ycam - 100, zt + 1.6],
                                 "fov": vfov, "shift": shift},
                      "sun": s, "groups": groups_all, "bg": "sky", "fog": True, "fogNear": 120, "fogFar": 1200,
                      "shadowBox": shadow_near, "exposure": 1.05})
    if "e" in only:
        s = sun("2026-03-21", 12)
        levels = [k["id"] for k in meta.get("kondygnacje", [])] or [g for g in info["groups"] if g.startswith("P")]
        step = 3.6
        explode = {lv: i * step for i, lv in enumerate(levels)}
        explode["dach"] = len(levels) * step
        groups = {g: (g in levels or g in ("dach", "budynek")) for g in info["groups"]}
        ebb = [x0 - 0.5, y0 - 0.5, z0, x1 + 0.5, y1 + 0.5, z1 + len(levels) * step]
        hh, ctr = _ortho_fit(ebb, 150.0, 30.0, aspect, 1.1)
        d = _dir(150.0, 30.0)
        pos = tuple(ctr[i] + d[i] * 300 for i in range(3))
        views.append({"key": "e", "name": VIEW_NAMES["e"], "width": W, "height": H,
                      "camera": {"type": "ortho", "pos": pos, "target": ctr, "halfHeight": hh},
                      "sun": {**s, "az": 200.0, "el": 48.0}, "groups": groups, "explode": explode, "bg": "studio",
                      "fog": False, "shadowBox": [ebb[0] - 6, ebb[1] - 6, ebb[2], ebb[3] + 6, ebb[4] + 6, ebb[5]],
                      "exposure": 1.0, "aoRadius": 0.9})
    if "f" in only:
        s = sun("2026-06-21", 15)
        groups = {g: (g != "otoczenie") for g in info["groups"]}
        hh = max((Hh + 1.6) / 2 * 1.08, (Wd + 3.0) / aspect / 2)
        tgt = (cx, y0 - 1, (z0 + z1) / 2 + 0.2)
        views.append({"key": "f", "name": VIEW_NAMES["f"], "width": W, "height": H,
                      "camera": {"type": "ortho", "pos": [cx, y0 - 200, tgt[2]], "target": [cx, y0, tgt[2]],
                                 "halfHeight": hh},
                      "sun": s, "groups": groups, "bg": "white", "fog": False, "groundDisc": False,
                      "shadowBox": shadow_near, "exposure": 1.0, "aoRadius": 0.8})
    return views


def sun_study_views(info: dict, tile: int) -> list[dict]:
    meta = info.get("meta") or {}
    dz = meta.get("dzialka") or {}
    bb = info["bbox_budynek"]
    if dz.get("obrys"):
        xs = [p[0] for p in dz["obrys"]]
        ys = [p[1] for p in dz["obrys"]]
        x0, x1, y0, y1 = min(xs) - 3, max(xs) + 3, min(ys) - 3, max(ys) + 3
    else:
        x0, x1, y0, y1 = bb[0] - 15, bb[3] + 15, bb[1] - 15, bb[4] + 15
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hh = max(x1 - x0, y1 - y0) / 2
    out = []
    for date in ("2026-03-21", "2026-06-21", "2026-12-21"):
        for hour in (9, 12, 15):
            az, el = sun_position(f"{date} {hour:02d}:00")
            out.append({"key": f"g_{date[5:7]}{date[8:]}_{hour:02d}", "name": f"g_{date}_{hour:02d}00", "width": tile,
                        "height": tile, "data": date, "godz": hour,
                        "camera": {"type": "ortho", "pos": [cx, cy, 300], "target": [cx, cy, 0], "up": [0, 1, 0],
                                   "halfHeight": hh},
                        "sun": {"az": round(az, 2), "el": round(el, 2)},
                        "groups": {g: True for g in info["groups"]}, "bg": "sky", "fog": False,
                        "shadowBox": [x0 - 25, y0 - 25, bb[2] - 1, x1 + 25, y1 + 25, bb[5] + 1], "exposure": 1.0,
                        "aoRadius": 1.0})
    return out


# --------------------------------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------------------------------
def _decode(data_url: str) -> Image.Image:
    b = base64.b64decode(data_url.split(",", 1)[1])
    return Image.open(io.BytesIO(b)).convert("RGB")


def _font(sz, bold=False):
    try:
        return ImageFont.truetype(FONT_B if bold else FONT, sz)
    except OSError:
        return ImageFont.load_default()


def compose_sun_grid(tiles: list[tuple[dict, Image.Image]], out: Path, title: str):
    n = 3
    t = tiles[0][1].size[0]
    pad, head, lab = 24, 110, 46
    Wg = n * t + (n + 1) * pad
    Hg = head + n * (t + lab) + (n + 1) * pad
    im = Image.new("RGB", (Wg, Hg), (250, 250, 248))
    dr = ImageDraw.Draw(im)
    dr.text((pad, 22), title, fill=(20, 20, 20), font=_font(38, True))
    dr.text((pad, 70), "Rzut z góry, północ u góry. Pozycja Słońca: algorytm NOAA, Poznań 52,41°N 16,93°E, "
                       "czas urzędowy (CET/CEST).", fill=(70, 70, 70), font=_font(22))
    for k, (v, img) in enumerate(tiles):
        r, c = divmod(k, n)
        x = pad + c * (t + pad)
        y = head + pad + r * (t + lab + pad)
        im.paste(img, (x, y + lab))
        dd = v["data"]
        txt = f"{dd[8:10]}.{dd[5:7]}.  godz. {v['godz']:02d}:00   —   azymut {v['sun']['az']:.0f}°, wys. {v['sun']['el']:.0f}°"
        dr.text((x, y + 8), txt, fill=(30, 30, 30), font=_font(24, True))
        # strzałka północy
        ax, ay = x + t - 46, y + lab + 20
        dr.polygon([(ax, ay), (ax - 12, ay + 34), (ax, ay + 26), (ax + 12, ay + 34)], fill=(20, 20, 20))
        dr.text((ax - 8, ay + 36), "N", fill=(20, 20, 20), font=_font(22, True))
    im.save(out, optimize=True)


def render_all(glb: Path, out: Path, views: str = "abcdefg", size=(2400, 1500), ss: int = 2, tile: int = 900,
               verbose: bool = True) -> dict:
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    httpd, port = _serve(glb)
    results = {"glb": str(glb), "widoki": []}
    t0 = time.time()
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(executable_path=CHROMIUM, headless=True,
                                   args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                         "--ignore-gpu-blocklist", "--disable-gpu-sandbox"])
            page = br.new_page(viewport={"width": 1280, "height": 900})
            page.set_default_timeout(600_000)
            logs = []
            page.on("console", lambda m: logs.append(f"{m.type}: {m.text}"))
            page.on("pageerror", lambda e: logs.append(f"pageerror: {e}"))
            page.goto(f"http://127.0.0.1:{port}/render.html")
            page.wait_for_function("window.__lamelaReady === true")
            info = page.evaluate("u => LAMELA.load(u)", "/__model.glb")
            results["info"] = {k: info[k] for k in ("groups", "bbox_budynek", "bbox_all")}
            vlist = build_views(info, size[0], size[1], views)
            # rzędna terenu pod kamerami „z poziomu oczu”
            for v in vlist:
                if "eye" in v:
                    z = page.evaluate("p => LAMELA.groundZ(p)", [v["eye"]])[0]
                    if z is not None:
                        v["camera"]["pos"][2] = z + 1.6
                        v["camera"]["target"][2] = z + 1.6
            for v in vlist:
                v["ss"] = ss
                t1 = time.time()
                url = page.evaluate("c => LAMELA.render(c)", v)
                img = _decode(url).resize((v["width"], v["height"]), Image.LANCZOS)
                fp = out / f"{v['name']}.png"
                img.save(fp, optimize=True)
                results["widoki"].append({"plik": str(fp), "widok": v["key"], "slonce": v["sun"],
                                          "czas_s": round(time.time() - t1, 1)})
                if verbose:
                    print(f"  {fp.name}: {time.time() - t1:.1f} s", flush=True)
            if "g" in views:
                tiles = []
                sub = out / "naslonecznienie"
                sub.mkdir(exist_ok=True)
                for v in sun_study_views(info, tile):
                    v["ss"] = ss
                    t1 = time.time()
                    url = page.evaluate("c => LAMELA.render(c)", v)
                    img = _decode(url).resize((v["width"], v["height"]), Image.LANCZOS)
                    img.save(sub / f"{v['name']}.png", optimize=True)
                    tiles.append((v, img))
                    if verbose:
                        print(f"  {v['name']}: {time.time() - t1:.1f} s", flush=True)
                name = (info.get("meta") or {}).get("nazwa") or ""
                fp = out / f"{VIEW_NAMES['g']}.png"
                compose_sun_grid(tiles, fp, f"Analiza nasłonecznienia — {name}".rstrip(" —"))
                results["widoki"].append({"plik": str(fp), "widok": "g",
                                          "slonce": [{"data": v["data"], "godz": v["godz"], **v["sun"]} for v, _ in tiles]})
            errs = [l for l in logs if l.startswith(("error", "pageerror"))]
            results["konsola_bledy"] = errs
            br.close()
    finally:
        httpd.shutdown()
    results["czas_s"] = round(time.time() - t0, 1)
    (out / "rendery.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--glb", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--views", default="abcdefg")
    ap.add_argument("--size", default="2400x1500")
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--tile", type=int, default=900)
    a = ap.parse_args(argv)
    w, h = (int(x) for x in a.size.lower().split("x"))
    r = render_all(Path(a.glb).resolve(), Path(a.out), a.views, (w, h), a.ss, a.tile)
    print(json.dumps({k: v for k, v in r.items() if k != "info"}, ensure_ascii=False, indent=1))
    return 1 if r.get("konsola_bledy") else 0


if __name__ == "__main__":
    sys.exit(main())
