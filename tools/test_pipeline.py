#!/usr/bin/env python3
"""Test automatyczny rdzenia modelu i pipeline'u 3D (model testowy model/test/*.yaml).

Uruchomienie:
    PYTHONPATH=src python3 tools/test_pipeline.py              # pełny (z renderami i podglądem www)
    PYTHONPATH=src python3 tools/test_pipeline.py --szybko     # bez renderów i przeglądarki
    PYTHONPATH=src python3 tools/test_pipeline.py --pelne-rendery   # rendery 2400×1500 zamiast miniatur
Wyniki pomocnicze: build/test/ (katalog ignorowany przez git).
Funkcje test_* są zgodne z pytest (gdy jest zainstalowany).
"""
from __future__ import annotations

import copy
import json
import math
import socket
import sys
import threading
import time
import traceback
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np
import yaml
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools" / "render3d"))

from lamela.ir import build_ir  # noqa: E402
from lamela.model import Model, ModelValidationError, iter_polys, load_model  # noqa: E402
from lamela.model3d import export_glb, export_obj, load_glb_check  # noqa: E402
from lamela.sun import sun_position  # noqa: E402

B_TEST = ROOT / "model" / "test" / "dom_testowy.yaml"
D_TEST = ROOT / "model" / "test" / "dzialka_testowa.yaml"
OUT = ROOT / "build" / "test"
CHROMIUM = "/opt/pw-browsers/chromium"


def _load_raw(p):
    return yaml.safe_load(Path(p).read_text(encoding="utf-8"))


_M = None
_IR = None


def model():
    global _M
    if _M is None:
        _M = load_model(B_TEST, D_TEST)
    return _M


def ir():
    global _IR
    if _IR is None:
        _IR = build_ir(model())
    return _IR


def approx(a, b, tol=1e-3):
    return abs(a - b) <= tol


# ==================================================================================================
# 1. Wczytanie i walidacja modelu testowego
# ==================================================================================================
def test_model_testowy_bez_uwag():
    m = model()
    probs = [p for p in m.problemy if p.poziom != "INFO"]
    assert not probs, "\n".join(map(str, probs))
    assert [k.id for k in m.kondygnacje] == ["P0", "P1"]
    assert len(m.sciany()) == 14 and len(m.otwory()) == 20 and len(m.pomieszczenia()) == 9


def test_rzedne_scian():
    m = model()
    s = m.sciana("S0-01")
    assert approx(s.z_od, -0.225) and approx(s.z_do, 2.71), (s.z_od, s.z_do)
    s1 = m.sciana("S1-01")
    assert approx(s1.z_od, 2.91) and approx(s1.z_do, 5.77), (s1.z_od, s1.z_do)
    ext = [l for l in s.warstwy if l.strona == -1]
    assert ext and all(approx(l.z1, 2.91) and approx(l.z0, -0.525) for l in ext), [(l.z0, l.z1) for l in ext]
    ext1 = [l for l in s1.warstwy if l.strona == -1]
    assert all(approx(l.z1, 5.97 + 0.2235 + 0.30, 1e-4) for l in ext1), [l.z1 for l in ext1]


def test_powierzchnie_pomieszczen():
    m = model()
    exp = {"0.01": 3.99 * 4.32, "0.02": 3.99 * 3.32, "0.03": 5.59 * 4.395, "0.04": 5.59 * 3.395,
           "1.01": 3.99 * 3.02, "1.02": 3.99 * 4.62 - 2.2 * 3.275, "1.03": 5.59 * 4.32,
           "1.04": (9.895 - 7.075) * 3.32, "1.05": (6.925 - 4.305) * 3.32}
    for rid, a in exp.items():
        r = m.pomieszczenie(rid)
        assert approx(r.pow_netto, a, 2e-3), (rid, r.pow_netto, a)
        assert approx(r.wysokosc, 2.70, 1e-3), (rid, r.wysokosc)
        assert r.wsp_wysokosci == 1.0
    assert approx(m.pomieszczenie("0.01").obwod, 2 * (3.99 + 4.32), 2e-3)
    zs = m.zestawienie_powierzchni()
    assert approx(zs["pow_netto_razem"], sum(exp.values()), 0.02)
    assert approx(zs["pow_ruchu"], exp["0.02"] + exp["1.02"], 0.01)


def test_wspolczynnik_wysokosci():
    from lamela.model import wsp_wysokosci
    assert wsp_wysokosci(2.5) == 1.0 and wsp_wysokosci(2.2) == 1.0
    assert wsp_wysokosci(2.0) == 0.5 and wsp_wysokosci(1.4) == 0.5
    assert wsp_wysokosci(1.2) == 0.0


def test_wskazniki_budynku():
    m = model()
    zp = m.pow_zabudowy()
    a = (10 + 2 * 0.297) * (8 + 2 * 0.297)
    assert approx(zp["budynek"], a, 0.02), zp
    assert zp["z_plytami"] > zp["budynek"]
    kb = m.kubatura_brutto()
    # przestrzenie kondygnacji + płyty: szacunek ręczny
    exp = a * (2.71 + 0.225) + a * 0.12 + a * (5.77 - 2.91) + a * 0.20 + a * (5.97 + 0.2235 - 5.77 + 0.01)
    assert abs(kb["razem"] - exp) / exp < 0.02, (kb, exp)


def test_polaczenia_naroza_T():
    m = model()
    s1 = m.sciana("S0-01")
    assert s1.polaczenia[0]["typ"] == "L" and s1.polaczenia[1]["typ"] == "L"
    s5 = m.sciana("S0-05")
    assert s5.polaczenia[0]["typ"] == "T" and s5.polaczenia[0]["z"] == ["S0-01"]
    # konstrukcja S0-05 dochodzi do lica konstrukcji S0-01 (y = 0,09), tynk — do lica wykończonego (0,105)
    k = s5.warstwa_konstr.polygon
    assert approx(k.bounds[1], 0.09), k.bounds
    tyn = [l for l in s5.warstwy if not l.konstrukcyjna]
    assert all(approx(l.polygon.bounds[1], 0.105) for l in tyn), [l.polygon.bounds for l in tyn]
    # naroże L: izolacja i tynk ścięte po dwusiecznej — wierzchołki (−0,29; −0,29) i (−0,297; −0,297)
    ins = [l for l in s1.warstwy if l.klasa == "izolacja"][0].polygon
    assert any(approx(x, -0.29) and approx(y, -0.29) for x, y in ins.exterior.coords), list(ins.exterior.coords)
    tz = [l for l in s1.warstwy if l.mat == "TYNK_SIL"][0].polygon
    assert any(approx(x, -0.297) and approx(y, -0.297) for x, y in tz.exterior.coords), list(tz.exterior.coords)
    # konstrukcja S0-01 (priorytet: dłuższa) przechodzi do lica zewn. konstrukcji S0-04 (x = −0,09)
    assert approx(s1.warstwa_konstr.polygon.bounds[0], -0.09)


def _no_overlap_no_gaps(m, kond):
    polys = [w.polygon for s in m.sciany(kond) for w in s.warstwy if w.polygon is not None and not w.polygon.is_empty]
    tot = sum(p.area for p in polys)
    U = unary_union(polys)
    small = [Polygon(h).area for p in iter_polys(U) for h in p.interiors if Polygon(h).area < 0.3]
    return tot - U.area, small, U


def test_brak_zakladek_i_szczelin_model_testowy():
    m = model()
    for k in ("P0", "P1"):
        ov, small, U = _no_overlap_no_gaps(m, k)
        assert ov < 1e-6, (k, ov)
        assert not small, (k, small)
        assert len(iter_polys(U)) == 1, "ściany kondygnacji powinny tworzyć jedną spójną bryłę"


def test_otwory_polozenie():
    m = model()
    o = m.otwor("O0-01")
    assert np.allclose(o.p0, [5.0, 0.0]) and np.allclose(o.p1, [9.0, 0.0])
    assert approx(o.z0, 0.0) and approx(o.z1, 2.6)
    assert np.allclose(o.kierunek_zewn, [0, -1])
    t0, t1 = o.oscieze
    assert approx(t0, -0.297) and approx(t1, 0.105)
    o3 = m.otwor("O0-03")          # ściana S0-03 biegnie z (10,8) do (0,8)
    assert np.allclose(o3.p0, [3.7, 8.0]) and np.allclose(o3.p1, [2.6, 8.0])
    assert np.allclose(o3.kierunek_zewn, [0, 1])
    o6 = m.otwor("O1-06")
    assert approx(o6.z0, 3.06 + 0.9) and approx(o6.z1, 3.06 + 2.4)


# ==================================================================================================
# 2. Walidacja — przypadki błędne (modele syntetyczne)
# ==================================================================================================
def _base():
    raw = _load_raw(B_TEST)
    return raw


def _errs(raw):
    m = Model(raw, None)
    return m, [str(p) for p in m.bledy], [str(p) for p in m.ostrzezenia]


def test_walidacja_brak_pola():
    raw = _base()
    del raw["sciany"][0]["przegroda"]
    _, e, _ = _errs(raw)
    assert any("S0-01" in x and "brak wymaganego pola 'przegroda'" in x for x in e), e


def test_walidacja_odwolania():
    raw = _base()
    raw["sciany"][1]["przegroda"] = "XX"
    raw["przegrody"]["SZ1"]["warstwy"][2]["mat"] = "NIE_MA"
    raw["otwory"][0]["sciana"] = "S0-99"
    raw["pomieszczenia"][0]["kond"] = "P7"
    _, e, _ = _errs(raw)
    assert any("nieistniejącej przegrody 'XX'" in x for x in e), e
    assert any("nieistniejącego materiału 'NIE_MA'" in x for x in e), e
    assert any("O0-01" in x and "nieistniejącej ściany 'S0-99'" in x for x in e), e
    assert any("nieistniejącej kondygnacji 'P7'" in x for x in e), e


def test_walidacja_otwor_poza_sciana():
    raw = _base()
    raw["otwory"][1]["odl"] = 9.5          # O0-02: 9,5 + 1,8 > 10,0
    raw["otwory"][4]["parapet"] = 2.0      # O0-05: 2,0 + 1,5 > 2,71
    _, e, _ = _errs(raw)
    assert any("O0-02" in x and "wychodzi poza ścianę S0-01 w poziomie" in x for x in e), e
    assert any("O0-05" in x and "w pionie" in x for x in e), e


def test_walidacja_nakladajace_otwory():
    raw = _base()
    raw["otwory"][1]["odl"] = 4.0          # O0-02 (4,0–5,8) nachodzi na O0-01 (5,0–9,0)
    _, e, _ = _errs(raw)
    assert any("O0-01" in x and "O0-02" in x and "nakładają się" in x for x in e), e


def test_walidacja_niezamkniete_pomieszczenie_i_duplikat():
    raw = _base()
    raw["sciany"] = [s for s in raw["sciany"] if s["id"] != "S0-06"]
    raw["otwory"] = [o for o in raw["otwory"] if o["sciana"] != "S0-06"]
    raw["sciany"].append(copy.deepcopy(raw["sciany"][0]))
    raw["sciany"][-1]["os"] = [[0, 0], [0.1, 3.0]]
    _, e, w = _errs(raw)
    assert any("zdublowany identyfikator 'S0-01'" in x for x in e), e
    raw2 = _base()
    raw2["sciany"] = [s for s in raw2["sciany"] if s["id"] != "S0-04"]
    raw2["otwory"] = [o for o in raw2["otwory"] if o["sciana"] != "S0-04"]
    _, e2, _ = _errs(raw2)
    assert any("0.01" in x and "nie leży w zamkniętym obszarze" in x for x in e2), e2


def test_walidacja_strict_i_orientacja():
    raw = _base()
    raw["stropy"][0]["obrys"] = list(reversed(raw["stropy"][0]["obrys"]))
    m, e, w = _errs(raw)
    assert not e and any("CW" in x for x in w), w
    raw["sciany"][0]["wnetrze"] = "gora"
    tmp = OUT / "tmp_zly.yaml"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
    try:
        load_model(tmp)
        raise AssertionError("oczekiwano ModelValidationError")
    except ModelValidationError as ex:
        assert "wnetrze" in str(ex)


# ==================================================================================================
# 3. Łączenie naroży — geometrie nietypowe
# ==================================================================================================
def _mini(walls, prz=None, extra=None):
    raw = _base()
    keep = ("meta", "uklad", "materialy", "przegrody")
    r = {k: raw[k] for k in keep}
    r["kondygnacje"] = [raw["kondygnacje"][0]]
    r["stropy"] = [{"id": "ST1", "nad": "P0", "wierzch": 2.91, "grubosc": 0.2,
                    "obrys": [[-5, -5], [25, -5], [25, 25], [-5, 25]]}]
    r["sciany"] = []
    for i, (a, b, p, wn) in enumerate(walls):
        r["sciany"].append({"id": f"S0-{i + 1:02d}", "kond": "P0", "przegroda": p, "os": [a, b], "wnetrze": wn})
    if prz:
        r["przegrody"].update(prz)
    if extra:
        r.update(extra)
    return Model(r, None)


def test_naroze_skosne_i_rozne_grubosci():
    prz = {"SZ2": {"nazwa": "ściana cieńsza izolacja", "typ": "sciana_zewn", "warstwy": [
        {"mat": "TYNK_GIPS", "d": 0.015}, {"mat": "SIL18", "d": 0.18, "konstrukcyjna": True},
        {"mat": "EPS031", "d": 0.15}, {"mat": "TYNK_SIL", "d": 0.007}]}}
    pts = [(0, 0), (10, 0), (12, 6), (4, 9), (0, 6)]
    walls = [(pts[i], pts[(i + 1) % 5], "SZ1" if i % 2 == 0 else "SZ2", "lewa") for i in range(5)]
    m = _mini(walls, prz, {"pomieszczenia": [{"id": "0.01", "kond": "P0", "nazwa": "x", "punkt": [5, 4],
                                               "kategoria": "podstawowa"}]})
    assert not m.bledy, m.bledy
    ov, small, U = _no_overlap_no_gaps(m, "P0")
    assert ov < 1e-6 and not small, (ov, small)
    assert len(iter_polys(U)) == 1 and len(iter_polys(U)[0].interiors) == 1
    r = m.pomieszczenie("0.01")
    assert r.pow_netto > 0.8 * Polygon(pts).area


def test_naroze_T_przesuniete_X_i_wezel():
    walls = [((0, 0), (10, 0), "SZ1", "lewa"), ((10, 0), (10, 8), "SZ1", "lewa"), ((10, 8), (0, 8), "SZ1", "lewa"),
             ((0, 8), (0, 0), "SZ1", "lewa"),
             ((0.105, 4.0), (5.0, 4.0), "SD1", "srodek"),        # T: oś kończy się na licu wykończonym
             ((5.0, 0.0), (5.0, 8.0), "SW1", "srodek"),           # przechodzi przez węzeł (5,4)
             ((5.0, 4.0), (10.0, 4.0), "SD1", "srodek"),          # T w (5,4) po drugiej stronie → X z 4 ścian
             ((2.0, 1.0), (2.0, 3.5), "SD1", "srodek"),           # ścianka wolnostojąca
             ((7.0, 5.0), (7.0, 7.0), "SD1", "srodek"), ((6.0, 6.0), (8.0, 6.0), "SD1", "srodek")]  # X (krzyż)
    pom = [{"id": f"0.0{i + 1}", "kond": "P0", "nazwa": "x", "punkt": p, "kategoria": "podstawowa"}
           for i, p in enumerate([[1, 6], [3, 2], [8, 2], [9, 7.5]])]
    m = _mini(walls, None, {"pomieszczenia": pom})
    assert not m.bledy, m.bledy
    ov, small, U = _no_overlap_no_gaps(m, "P0")
    assert ov < 1e-6 and not small, (ov, small)
    assert m.sciana("S0-05").polaczenia[0]["typ"] == "T"
    a = [m.pomieszczenie(f"0.0{i}").pow_netto for i in range(1, 5)]
    assert all(x > 10 for x in a), a


# ==================================================================================================
# 4. IR
# ==================================================================================================
def test_ir_kompletnosc():
    r = ir()
    s = r.summary()
    for k in ("wall", "insulation", "frame", "glass", "door_leaf", "slab", "roof", "parapet", "canopy", "column", "beam",
              "footing", "stair_step", "landing", "railing", "lamella", "terrace", "pavement", "fence", "vegetation",
              "context", "road", "mesh:vegetation", "mesh:vehicle", "terrain_triangles"):
        assert s.get(k, 0) > 0, (k, s)
    for p in r.prisms:
        poly = p.shape()
        assert poly.is_valid and poly.area > 0 and p.z1 > p.z0, (p.id, p.kind)
    assert s["stair_step"] == 16 and s["landing"] == 1
    lam = [p for p in r.by_kind("lamella") if p.meta.get("part") != "rygiel"]
    assert len(lam) == int(math.floor((10.594 - 0.05) / 0.20 + 1e-9)) + 1, len(lam)
    groups = {p.meta.get("group") for p in r.prisms + r.meshes}
    assert {"P0", "P1", "dach", "fundamenty", "otoczenie"} <= groups, groups


def test_ir_sciana_z_otworami_objetosc():
    m, r = model(), ir()
    s = m.sciana("S0-01")
    k = s.warstwa_konstr
    V = sum(p.volume for p in r.prisms if p.meta.get("wall") == "S0-01" and p.meta.get("layer") == k.mat)
    exp = k.polygon.area * (s.z_do - s.z_od) - sum(o.szer * o.wys * k.d for o in s.otwory)
    assert approx(V, exp, 1e-4), (V, exp)
    parts = {p.meta.get("part") for p in r.prisms if p.meta.get("wall") == "S0-01"}
    assert {"filar", "podokienny", "nadproze"} <= parts, parts
    st = sorted(p.z1 for p in r.by_kind("stair_step"))
    assert approx(st[0], 0.17) and approx(max(st), 3.06 - 0.17), (st[0], max(st))


def test_ir_teren():
    m, r = model(), ir()
    t = r.terrain
    assert t is not None and len(t.faces) > 1000
    z = t.height_at(5.0, 4.0)
    assert -0.40 < z < -0.25, z
    fp = m.obrys_kondygnacji("P0")
    c = t.vertices[t.faces].mean(axis=1)
    import shapely
    assert not shapely.contains_xy(fp.buffer(-0.05), c[:, 0], c[:, 1]).any()
    pav = [p for p in r.by_kind("pavement")]
    for p in pav[:20]:
        cc = p.shape().centroid
        assert p.z1 >= t.height_at(cc.x, cc.y) - 1e-6


def test_slonce_poznan():
    az, el = sun_position("2026-06-21 12:00")
    assert 150 < az < 160 and 58 < el < 61
    az, el = sun_position("2026-12-21 12:00")
    assert 13.5 < el < 15.0
    az, el = sun_position("2026-03-21 12:00")
    assert 178 < az < 183 and 36 < el < 39


# ==================================================================================================
# 5. Eksport glTF / OBJ
# ==================================================================================================
def test_eksport_glb_obj():
    import pygltflib
    OUT.mkdir(parents=True, exist_ok=True)
    glb = OUT / "dom_testowy.glb"
    st = export_glb(ir(), glb, model=model())
    assert st["bajty"] > 100_000
    c = load_glb_check(glb)
    for g in ("budynek", "P0", "P1", "dach", "fundamenty", "teren", "otoczenie"):
        assert g in c["grupy"], c["grupy"]
    g = pygltflib.GLTF2().load(str(glb))
    names = {n.name: n for n in g.nodes}
    assert "S0-01" in names and names["S0-01"].extras.get("id") == "S0-01"
    assert names["S0-01|SIL18"].extras.get("material") == "SIL18"
    mats = {m.name: m for m in g.materials}
    assert mats["SZKLO"].alphaMode == "BLEND"
    assert mats["DREWNO_TERMO"].pbrMetallicRoughness.baseColorTexture is not None
    assert len(g.textures) >= 5
    meta = g.scenes[0].extras
    meta = meta.get("metadata", meta)
    assert "lamela" in meta and meta["lamela"]["kondygnacje"][1]["id"] == "P1"
    import trimesh
    sc = trimesh.load(glb)
    b = sc.bounds
    assert b[1][1] > 6.4 and b[0][1] < -0.5          # oś Y (góra): attyka ~6,5 m; fundamenty poniżej terenu
    o = export_obj(ir(), OUT / "obj" / "dom_testowy.obj", model=model())
    txt = Path(o["plik"]).read_text()
    assert "mtllib" in txt and (OUT / "obj" / "dom_testowy.mtl").exists()


# ==================================================================================================
# 6. Rendery i podgląd www (przeglądarka)
# ==================================================================================================
def test_rendery(full=False):
    from PIL import Image
    from render import render_all
    glb = OUT / "dom_testowy.glb"
    if not glb.exists():
        export_glb(ir(), glb, model=model())
    size = (2400, 1500) if full else (720, 450)
    r = render_all(glb.resolve(), OUT / ("rendery" if full else "rendery_mini"), "abcdefg", size, ss=2 if full else 1,
                   tile=900 if full else 300, verbose=False)
    assert not r["konsola_bledy"], r["konsola_bledy"]
    assert len(r["widoki"]) == 7
    for v in r["widoki"]:
        im = np.asarray(Image.open(v["plik"]).convert("L"), float)
        assert im.std() > 8, (v["plik"], im.std())
    im = Image.open(r["widoki"][0]["plik"])
    assert im.size == size


def _serve_root():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()

    class H(SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    httpd = ThreadingHTTPServer(("127.0.0.1", port), partial(H, directory=str(ROOT)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def _route_cdn_local(ctx):
    """Żądania do cdn.jsdelivr.net/npm/three@X/… obsługiwane z tools/render3d/node_modules/three (ta sama wersja).
    Sandbox przeglądarki nie ufa CA proxy; test sprawdza kod podglądu offline, URL-e CDN sprawdza curl/produkcja."""
    base = ROOT / "tools" / "render3d" / "node_modules" / "three"

    def handler(route):
        url = route.request.url.split("?")[0]
        rel = url.split("/npm/", 1)[1].split("/", 1)[1]
        fp = base / rel
        if fp.exists():
            route.fulfill(status=200, body=fp.read_bytes(), headers={"Content-Type": "text/javascript",
                                                                     "Access-Control-Allow-Origin": "*"})
        else:
            route.fulfill(status=404, body=b"")
    ctx.route("https://cdn.jsdelivr.net/npm/three@*/**", handler)


def test_podglad_www():
    from playwright.sync_api import sync_playwright
    glb = OUT / "dom_testowy.glb"
    if not glb.exists():
        export_glb(ir(), glb, model=model())
    httpd, port = _serve_root()
    shots = []
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(executable_path=CHROMIUM, headless=True,
                                   args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            for name, vp in (("desktop", {"width": 1440, "height": 900}), ("telefon", {"width": 390, "height": 844})):
                ctx = br.new_context(viewport=vp, device_scale_factor=1)
                _route_cdn_local(ctx)
                pg = ctx.new_page()
                errs = []
                pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
                pg.on("pageerror", lambda e: errs.append(str(e)))
                pg.goto(f"http://127.0.0.1:{port}/www/model3d/index.html?model=/build/test/dom_testowy.glb")
                pg.wait_for_function("window.__viewer && window.__viewer.ready()", timeout=120_000)
                pg.wait_for_timeout(2500)
                fp = OUT / f"www_{name}.png"
                pg.screenshot(path=str(fp))
                shots.append(fp)
                if name == "desktop":
                    pg.select_option("#clipMode", "z")
                    pg.eval_on_selector("#clip", "e => { e.value = '0.40'; e.dispatchEvent(new Event('input')); }")
                    pg.click("#evening")
                    pg.click("[data-view=se]")
                    pg.wait_for_timeout(2500)
                    fp = OUT / "www_desktop_przekroj_wieczor.png"
                    pg.screenshot(path=str(fp))
                    shots.append(fp)
                    grp = pg.evaluate("Object.keys(window.__viewer.groups())")
                    assert {"P0", "P1", "dach", "teren", "otoczenie"} <= set(grp), grp
                assert not errs, errs
                ctx.close()
            br.close()
    finally:
        httpd.shutdown()
    from PIL import Image
    for fp in shots:
        im = np.asarray(Image.open(fp).convert("L"), float)
        assert im.std() > 8, fp


# ==================================================================================================
def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--szybko", action="store_true", help="bez renderów i przeglądarki")
    ap.add_argument("--pelne-rendery", action="store_true")
    a = ap.parse_args(argv)
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_") and callable(f)]
    if a.szybko:
        tests = [(n, f) for n, f in tests if n not in ("test_rendery", "test_podglad_www")]
    ok = fail = 0
    t0 = time.time()
    for n, f in tests:
        t1 = time.time()
        try:
            if n == "test_rendery":
                f(full=a.pelne_rendery)
            else:
                f()
            ok += 1
            print(f"PASS  {n}  ({time.time() - t1:.1f} s)", flush=True)
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"FAIL  {n}: {e}", flush=True)
            traceback.print_exc(limit=3)
    print(f"\n{ok} zaliczonych, {fail} niezaliczonych, czas {time.time() - t0:.0f} s")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
