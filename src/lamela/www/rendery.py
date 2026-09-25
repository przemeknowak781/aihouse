"""Rendery marketingowe strony www (16:9 i 4:3) — renderer pipeline'u (tools/render3d/render.js: three.js, N8AO,
headless Chromium) uruchamiany przez nakładkę ``render/render_www.js`` (otoczenie: stonowana trawa, pas zieleni na
horyzoncie; budynek bez zmian). Ujęcia 3/4 z poziomu oczu (1,65 m, obiektyw przesuwny — piony bez zbieżności,
ogniskowa ~40 mm ekw.), Słońce z ``lamela.sun`` (NOAA, Poznań) dla podanej daty i godziny. Kamera stoi w dozwolonym
obszarze (działka z odsunięciem od żywopłotów albo pas drogi); drzewa z projektu zieleni, które zasłoniłyby bryłę
w danym ujęciu, są w nim pomijane (lista trafia do podpisu). Wynik: <ujecie>_<proporcje>.png + rendery_www.json."""
from __future__ import annotations

import hashlib
import json
import math
import socket
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
R3D = ROOT / "tools" / "render3d"
HERE = Path(__file__).resolve().parent / "render"

# ujęcie → typ: '34' (3/4 z poziomu oczu) albo klucz widoku render.build_views; az — azymut kamery od środka
# bryły [°]; obszar — gdzie może stać kamera ('dzialka' | 'droga'); data/godz — Słońce; f — ogniskowa [mm ekw.]
UJECIA = {
    "ogrod": dict(typ="34", az=206.0, obszar="dzialka", data="2026-06-21", godz="17:00", f=40.0),
    "ulica": dict(typ="34", az=28.0, obszar="droga", data="2026-06-21", godz="19:00", f=40.0),
    "lotniczy": dict(typ="a", data="2026-05-20", godz="12:30"),
    "aksonometria": dict(typ="e", data="2026-03-21", godz="12:00"),
}
PROPORCJE = {"169": (1920, 1080), "43": (1600, 1200)}
WERSJA = "www-2"
OKO = 1.65


def klucz_cache(pliki: list, ujecia: dict, proporcje: dict, ss: int, extra=None) -> str:
    """Klucz cache: treść plików wejściowych (model YAML, kod IR/eksportu 3D, renderery) + konfiguracja ujęć
    (w ``extra`` — kamery i pominięte drzewa z ``plan_ujec``). Eksport glb nie jest bajtowo deterministyczny,
    więc kluczem nie jest sam plik glb."""
    h = hashlib.sha256()
    for f in sorted(str(x) for x in pliki):
        h.update(f.encode())
        h.update(Path(f).read_bytes())
    h.update(json.dumps([WERSJA, ujecia, proporcje, ss, extra], sort_keys=True, default=str).encode())
    for f in (R3D / "render.js", R3D / "render.py", HERE / "render_www.js", HERE / "render_www.html"):
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _slonce(data: str, godz: str) -> dict:
    from lamela.sun import sun_position
    az, el = sun_position(f"{data} {godz}")
    return {"az": round(az, 2), "el": round(el, 2), "data": data, "godz": godz}


class _H(SimpleHTTPRequestHandler):
    glb: Path = None

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.split("?")[0] == "/__model.glb":
            data = self.glb.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "model/gltf-binary")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        return super().do_GET()

    def translate_path(self, path):
        p = path.split("?")[0]
        return str(R3D / p[5:]) if p.startswith("/r3d/") else str(HERE / p.lstrip("/"))

    def guess_type(self, path):
        return "text/javascript" if str(path).endswith(".js") else super().guess_type(path)


def _serwer(glb: Path):
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), type("H", (_H,), {"glb": glb}))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def rzut_punktow(cam: dict, W: int, H: int, punkty: list) -> list:
    """Rzut punktów (układ budynku x→E, y→N, z↑) na obraz W×H — matematyka three.js z render.js
    (PerspectiveCamera + lookAt, obiektyw przesuwny przez setViewOffset). Zwraca [(px, py, w_kadrze?)]."""
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
    tan_h = math.tan(math.radians(cam.get("fov", 35.0)) / 2) * (1 + 2 * s)
    full_h = H * (1 + 2 * s)
    asp = W / full_h
    out = []
    for p in punkty:
        d = sub(b2t(p), pos)
        zc = dot(d, f)
        if zc <= 0.01:
            out.append((None, None, False))
            continue
        px = (dot(d, r) / (zc * tan_h * asp) + 1) / 2 * W
        py = (1 - dot(d, u) / (zc * tan_h)) / 2 * full_h
        out.append((px, py, 0 <= px <= W and 0 <= py <= H))
    return out


def kamera_34(pkt: list, az: float, f_mm: float, W: int, H: int, obszar, z_ter: float) -> dict | None:
    """Kamera 3/4 z poziomu oczu: kierunek od środka bryły pod azymutem ``az``, oś widzenia pozioma (obiektyw
    przesuwny), najmniejsza odległość, przy której cała bryła (punkty ``pkt``) mieści się w kadrze z marginesem;
    kamera musi stać w ``obszar`` (shapely). Gdy się nie da — krótsza ogniskowa (do 26 mm)."""
    from shapely.geometry import Point
    xs, ys = [p[0] for p in pkt], [p[1] for p in pkt]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    dx, dy = math.sin(math.radians(az)), math.cos(math.radians(az))
    ze = z_ter + OKO
    f = f_mm
    while f >= 26.0:
        hfov = 2 * math.atan(18.0 / f)
        vfov = math.degrees(2 * math.atan(math.tan(hfov / 2) / (W / H)))
        ostatni = None
        for i in range(16, 400):
            d = i * 0.5
            pos = [cx + dx * d, cy + dy * d, ze]
            if not obszar.contains(Point(pos[0], pos[1])):
                if ostatni is not None:
                    break
                continue
            ostatni = d
            cam = {"type": "persp", "pos": pos, "target": [cx, cy, ze], "fov": vfov, "shift": 0.0}
            dep = [((p[0] - pos[0]) * -dx + (p[1] - pos[1]) * -dy) for p in pkt]
            if min(dep) <= 1.0:
                continue
            tan_top = max((p[2] - ze) / q for p, q in zip(pkt, dep))
            s = max(0.0, min(0.42, (tan_top * 1.14 / math.tan(math.radians(vfov) / 2) - 1) / 2))
            cam["shift"] = round(s, 3)
            pr = rzut_punktow(cam, W, H, pkt)
            if all(px is not None and 0.06 * W <= px <= 0.94 * W and 0.04 * H <= py <= 0.985 * H for px, py, _ok in pr):
                cam["fov"] = round(vfov, 3)
                cam["ogniskowa_mm"] = f
                return cam
        f -= 2.0
    return None


def drzewa_w_kadrze(cam: dict, pkt: list, drzewa: list, W: int, H: int) -> list:
    """Drzewa (id, x, y, r, …) stojące między kamerą a bryłą, których korona wchodzi w kadr — do pominięcia."""
    pos = cam["pos"]
    tx, ty = cam["target"][0] - pos[0], cam["target"][1] - pos[1]
    n = math.hypot(tx, ty) or 1.0
    tx, ty = tx / n, ty / n
    d_bud = min((p[0] - pos[0]) * tx + (p[1] - pos[1]) * ty for p in pkt)
    asp = W / (H * (1 + 2 * cam.get("shift", 0)))
    half = math.atan(math.tan(math.radians(cam["fov"]) / 2) * (1 + 2 * cam.get("shift", 0)) * asp)
    out = []
    for t in drzewa:
        vx, vy = t[1] - pos[0], t[2] - pos[1]
        dep = vx * tx + vy * ty
        if dep <= 0.3 or dep >= d_bud:
            continue
        lat = -vx * ty + vy * tx
        if abs(math.atan2(lat, dep)) - math.atan2(t[3], dep) < half:
            out.append(t)
    return out


def plan_ujec(ujecia: dict, proporcje: dict, pkt: list, obszary: dict, drzewa: list, z_ter: float) -> dict:
    """Kamery ujęć 3/4 (liczone w Pythonie z geometrii modelu) i drzewa do pominięcia w każdym kadrze."""
    plan = {}
    for u, c in ujecia.items():
        for p, (W, H) in proporcje.items():
            if c["typ"] != "34":
                plan[f"{u}_{p}"] = dict(ujecie=u, W=W, H=H, cam=None, pomin=[])
                continue
            cam = kamera_34(pkt, c["az"], c.get("f", 40.0), W, H, obszary[c["obszar"]], z_ter)
            if cam is None:
                raise RuntimeError(f"ujęcie {u}_{p}: brak miejsca na kamerę w obszarze '{c['obszar']}'")
            plan[f"{u}_{p}"] = dict(ujecie=u, W=W, H=H, cam=cam, pomin=drzewa_w_kadrze(cam, pkt, drzewa, W, H))
    return plan


def renderuj(glb_bez, cache: Path, plan: dict, ujecia: dict | None = None, ss: int = 2, kotwice: dict | None = None,
             log=print) -> dict:
    """Renderuje brakujące kadry do ``cache``. ``glb_bez(ids)`` zwraca ścieżkę glb bez podanych drzew (grupy kadrów
    o tym samym zestawie pominiętych drzew renderuje się z jednego pliku)."""
    import sys
    ujecia = ujecia or UJECIA
    cache.mkdir(parents=True, exist_ok=True)
    meta_f = cache / "rendery_www.json"
    meta = json.loads(meta_f.read_text()) if meta_f.exists() else {"pliki": {}, "kamery": {}}
    brak = [k for k in plan if not (cache / f"{k}.png").exists()]
    grupy: dict[tuple, list] = {}
    for k in brak:
        grupy.setdefault(tuple(sorted(t[0] for t in plan[k]["pomin"])), []).append(k)
    if grupy:
        sys.path.insert(0, str(R3D))
        import render as R  # noqa: E402  (tools/render3d/render.py — kadry widoków a/e, dekodowanie, etykiety)
        from PIL import Image
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=R.CHROMIUM, headless=True,
                                    args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                          "--ignore-gpu-blocklist", "--disable-gpu-sandbox"])
            for ids, kadry in grupy.items():
                httpd, port = _serwer(Path(glb_bez(ids)).resolve())
                try:
                    page = br.new_page(viewport={"width": 1280, "height": 900})
                    page.set_default_timeout(900_000)
                    bl = []
                    page.on("pageerror", lambda e: bl.append(str(e)))
                    page.goto(f"http://127.0.0.1:{port}/render_www.html")
                    page.wait_for_function("window.LAMELA_WWW === true && window.__lamelaReady === true")
                    info = page.evaluate("u => LAMELA.load(u)", "/__model.glb")
                    for k in kadry:
                        _kadr(page, R, info, plan[k], ujecia[plan[k]["ujecie"]], ss, cache / f"{k}.png", meta, k, Image)
                        log(f"render {k}{' (bez: ' + ', '.join(ids) + ')' if ids else ''}: {meta['pliki'][k]['czas_s']} s")
                    if bl:
                        log(f"błędy strony renderera: {bl[:3]}")
                    page.close()
                finally:
                    httpd.shutdown()
            br.close()
        meta_f.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    meta = dict(meta)
    meta["pominiete"] = {k: [dict(id=t[0], gatunek=t[4]) for t in v["pomin"]] for k, v in plan.items()}
    return _dopisz_kotwice(meta, kotwice)


def _kadr(page, R, info, pl: dict, cfg: dict, ss: int, plik: Path, meta: dict, k: str, Image):
    import time
    t1 = time.time()
    W, H = pl["W"], pl["H"]
    if pl["cam"] is not None:
        cam = dict(pl["cam"])
        z = page.evaluate("p => LAMELA.groundZ(p)", [cam["pos"][:2]])[0]
        if z is not None:
            cam["pos"] = [cam["pos"][0], cam["pos"][1], z + OKO]
            cam["target"] = [cam["target"][0], cam["target"][1], z + OKO]
        x0, y0, z0, x1, y1, z1 = info["bbox_budynek"]
        v = {"key": k, "width": W, "height": H, "camera": cam, "groups": {g: True for g in info["groups"]},
             "bg": "sky", "fog": True, "fogNear": 140, "fogFar": 1500, "exposure": 1.0,
             "shadowBox": [x0 - 22, y0 - 22, z0 - 1, x1 + 22, y1 + 22, z1 + 1]}
    else:
        v = next(x for x in R.build_views(info, W, H, cfg["typ"]) if x["key"] == cfg["typ"])
    if cfg["typ"] != "e":
        v["sun"] = _slonce(cfg["data"], cfg["godz"])
    v["ss"] = ss
    res = page.evaluate("c => LAMELA.render(c)", v)
    img = R._decode(res["url"]).resize((W, H), Image.LANCZOS)
    if res.get("labels"):
        R._draw_labels(img, res["labels"])
    img.save(plik, optimize=True)
    meta["pliki"][k] = {"slonce": v["sun"], "W": W, "H": H, "czas_s": round(time.time() - t1, 1),
                        "ogniskowa_mm": v["camera"].get("ogniskowa_mm")}
    meta["kamery"][k] = v["camera"]


def _dopisz_kotwice(meta: dict, kotwice: dict | None) -> dict:
    meta["kotwice"] = {}
    for kadr, cam in (meta.get("kamery") or {}).items():
        if not kotwice or not kadr.startswith("ogrod_") or cam.get("type") == "ortho":
            continue
        W, H = meta["pliki"][kadr]["W"], meta["pliki"][kadr]["H"]
        pts = rzut_punktow(cam, W, H, list(kotwice.values()))
        meta["kotwice"][kadr] = {k: {"x": round(100 * px / W, 2), "y": round(100 * py / H, 2)}
                                 for k, (px, py, ok) in zip(kotwice, pts) if ok}
    return meta
