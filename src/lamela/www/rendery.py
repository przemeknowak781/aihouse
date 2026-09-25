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
    "ogrod": dict(typ="34", az=212.0, obszar="dzialka", data="2026-06-21", godz="17:00", f=40.0),
    "ulica": dict(typ="34", az=28.0, obszar="droga", data="2026-06-21", godz="19:00", f=40.0),
    "lotniczy": dict(typ="a", data="2026-05-20", godz="12:30"),
    "aksonometria": dict(typ="e", data="2026-03-21", godz="12:00"),
}
PROPORCJE = {"169": (1920, 1080), "43": (1600, 1200)}
WERSJA = "www-2"
OKO = 1.65


def klucz_cache(pliki: list, ujecia: dict, proporcje: dict, ss: int, extra=None) -> str:
    """Klucz cache: treść plików wejściowych (model YAML, kod IR/eksportu 3D, renderery) + konfiguracja ujęć.
    Eksport glb nie jest bajtowo deterministyczny, więc kluczem nie jest sam plik glb."""
    h = hashlib.sha256()
    for f in sorted(str(x) for x in pliki):
        h.update(f.encode())
        h.update(Path(f).read_bytes())
    h.update(json.dumps([WERSJA, ujecia, proporcje, ss, extra], sort_keys=True, default=str).encode())
    for f in (R3D / "render.js", R3D / "render.py", HERE / "render_www.js", Path(__file__)):
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
