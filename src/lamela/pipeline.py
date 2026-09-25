"""Pipeline: model YAML → walidacja → wskaźniki → IR → glTF/OBJ → rendery → podgląd www.

    PYTHONPATH=src python3 -m lamela.pipeline --budynek model/budynek.yaml --dzialka model/dzialka.yaml \\
        --out projekt/07_model_3D/wstepne --www www/model3d

Opcje: --views abcdefg (patrz tools/render3d/render.py), --size 2400x1500, --bez-renderow, --strict, --nazwa model.
Wyniki w katalogu --out:
  walidacja.txt, wskazniki.json, ir_podsumowanie.json, <nazwa>.glb, obj/<nazwa>.obj(+.mtl, tekstury),
  rendery/*.png (+ rendery.json), raport_pipeline.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path

from .ir import build_ir
from .model import load_model
from .model3d import export_glb, export_obj, load_glb_check

ROOT = Path(__file__).resolve().parents[2]


def wskazniki(m) -> dict:
    zp = m.pow_zabudowy()
    return {
        "nazwa": (m.meta or {}).get("nazwa"),
        "kondygnacje": [{"id": k.id, "nazwa": k.nazwa, "rzedna": k.rzedna} for k in m.kondygnacje],
        "pow_zabudowy_m2": zp["budynek"],
        "pow_zabudowy_z_plytami_m2": zp["z_plytami"],
        "pow_brutto_kondygnacji_m2": m.pow_brutto_kondygnacji(),
        "kubatura_brutto_m3": m.kubatura_brutto(),
        "zestawienie_powierzchni": m.zestawienie_powierzchni(),
        "liczba": {"sciany": len(m.sciany()), "otwory": len(m.otwory()), "pomieszczenia": len(m.pomieszczenia())},
    }


def run(budynek, dzialka=None, out="build/pipeline", www=None, views="abcdefg", size=(2400, 1500), render=True,
        strict=False, nazwa=None, ss=2, verbose=True) -> dict:
    t0 = time.time()
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rep: dict = {"budynek": str(budynek), "dzialka": str(dzialka) if dzialka else None, "etapy": {}}

    def log(msg):
        if verbose:
            print(msg, flush=True)

    m = load_model(budynek, dzialka, strict=strict)
    (out / "walidacja.txt").write_text(m.raport_walidacji() + "\n", encoding="utf-8")
    rep["walidacja"] = {"bledy": len(m.bledy), "ostrzezenia": len(m.ostrzezenia),
                        "problemy": [str(p) for p in m.problemy if p.poziom != "INFO"][:200]}
    log(f"[1] walidacja: {len(m.bledy)} błędów, {len(m.ostrzezenia)} ostrzeżeń → {out / 'walidacja.txt'}")
    if not m.sciany():
        rep["status"] = "przerwano — brak ścian po walidacji"
        (out / "raport_pipeline.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
        return rep
    w = wskazniki(m)
    (out / "wskazniki.json").write_text(json.dumps(w, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log(f"[2] wskaźniki: zabudowa {w['pow_zabudowy_m2']} m², kubatura {w['kubatura_brutto_m3']['razem']} m³, "
        f"PU {w['zestawienie_powierzchni']['pow_uzytkowa_PU']} m²")
    ir = build_ir(m)
    summ = ir.summary()
    (out / "ir_podsumowanie.json").write_text(json.dumps({"rodzaje": summ, "meta": ir.meta}, ensure_ascii=False,
                                                         indent=1, default=float), encoding="utf-8")
    log(f"[3] IR: {len(ir.prisms)} pryzm, {len(ir.meshes)} siatek, teren: "
        f"{len(ir.terrain.faces) if ir.terrain is not None else 0} trójkątów")
    stem = nazwa or Path(budynek).stem
    glb = out / f"{stem}.glb"
    g = export_glb(ir, glb, model=m)
    chk = load_glb_check(glb)
    rep["glb"] = {**g, "grupy": chk["grupy"], "materialy": chk["materialy"]}
    o = export_obj(ir, out / "obj" / f"{stem}.obj", model=m)
    rep["obj"] = o["plik"]
    log(f"[4] glTF: {glb} ({g['bajty'] / 1e6:.1f} MB, {g['trojkaty']} trójkątów); OBJ: {o['plik']}")
    if www:
        wd = Path(www)
        wd.mkdir(parents=True, exist_ok=True)
        shutil.copy2(glb, wd / "model.glb")
        rep["www"] = str(wd / "model.glb")
        log(f"[5] podgląd www: {wd / 'index.html'} (model.glb skopiowany)")
    if render:
        sys.path.insert(0, str(ROOT / "tools" / "render3d"))
        from render import render_all  # noqa: E402
        r = render_all(glb.resolve(), out / "rendery", views, size, ss, verbose=verbose)
        rep["rendery"] = {"pliki": [v["plik"] for v in r["widoki"]], "bledy_konsoli": r.get("konsola_bledy"),
                          "czas_s": r.get("czas_s")}
        log(f"[6] rendery: {len(r['widoki'])} plików w {out / 'rendery'} ({r.get('czas_s')} s)")
    rep["czas_s"] = round(time.time() - t0, 1)
    rep["status"] = "ok" if not m.bledy else "ok (model zawiera błędy walidacji — wyniki częściowe)"
    (out / "raport_pipeline.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1, default=float),
                                              encoding="utf-8")
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--budynek", required=True)
    ap.add_argument("--dzialka")
    ap.add_argument("--out", required=True)
    ap.add_argument("--www")
    ap.add_argument("--views", default="abcdefg")
    ap.add_argument("--size", default="2400x1500")
    ap.add_argument("--ss", type=int, default=2)
    ap.add_argument("--nazwa")
    ap.add_argument("--bez-renderow", action="store_true")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args(argv)
    w, h = (int(x) for x in a.size.lower().split("x"))
    rep = run(a.budynek, a.dzialka, a.out, a.www, a.views, (w, h), not a.bez_renderow, a.strict, a.nazwa, a.ss)
    print(json.dumps({k: rep[k] for k in ("status", "czas_s") if k in rep}, ensure_ascii=False))
    return 0 if rep.get("status", "").startswith("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
