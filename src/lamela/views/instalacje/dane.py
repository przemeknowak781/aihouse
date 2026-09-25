"""Obliczenia instalacji uruchamiane na AKTUALNYM modelu (``lamela.obliczenia``) — raz na proces, z pamięcią podręczną
na dysku (``build/cache_instalacje``, klucz = skrót plików modelu i źródeł bibliotek obliczeniowych).

Sekwencja jak w :func:`lamela.obliczenia.instalacje.oblicz_wszystko` (woda → ogrzewanie → woda z mocą PC → kanalizacja →
deszczowa → drenaż → odbiorniki → PV → bilans → obwody → odgromowa), z jedną korektą danych wejściowych:
``instalacje.piony`` zawierają w modelu także rury spustowe (RS…) — biblioteka grupowania pionów traktuje każdy jawny
pion jako pion kanalizacyjny/wodny, więc piony deszczowe (``rodzaj: deszczowa`` albo id „RS…”/opis „rura spustowa”)
są przed obliczeniami wod.-kan. odfiltrowane (zapisane w ``dane.inst['piony_deszczowe']``) — patrz BRAKI_DANYCH.
"""
from __future__ import annotations

import hashlib
import pickle
import re
from dataclasses import dataclass, field
from pathlib import Path

_MEM: dict = {}


@dataclass
class Wyniki:
    dane: object
    woda: object
    kanalizacja: object
    deszczowa: object
    drenaz: object
    ogrzewanie: object
    bilans: object
    obwody: object
    pv: object
    odgromowa: object
    wentylacja: dict
    odbiorniki: list
    zrodla: dict
    korekty: list = field(default_factory=list)
    energia_obc: object = None          # WynikObc (PN-EN 12831) — moduł energii
    energia_went: object = None         # WynikWent (bilans wentylacji) — moduł energii


def sciezki(ctx) -> dict:
    """Ścieżki plików modelu: budynek (ctx.src), działka (model), wyposażenie, instalacje (konfiguracja
    ``wspolne.instalacje`` / ``wspolne.wyposazenie`` albo pliki obok budynku)."""
    bud = Path(ctx.src or "model/budynek.yaml")
    m = ctx.model
    dz = ctx.cfg.get("dzialka") or getattr(m, "src_d", None)
    if dz and not Path(dz).exists():
        cand = bud.with_name(Path(dz).name)
        dz = str(cand) if cand.exists() else None
    out = {"budynek": str(bud), "dzialka": str(dz) if dz else None}
    for key, nm in (("wyposazenie", "wyposazenie.yaml"), ("instalacje", "instalacje.yaml")):
        p = ctx.cfg.get(key)
        if not p:
            c = bud.with_name(nm)
            p = str(c) if c.exists() else None
        out[key] = p
    return out


def _klucz(p: dict) -> str:
    h = hashlib.sha1()
    for k in sorted(p):
        v = p[k]
        h.update(k.encode())
        if v and Path(v).exists():
            h.update(Path(v).read_bytes())
    root = Path(__file__).resolve().parents[2] / "obliczenia"
    files = [root / "inst_wspolne.py", root / "wspolne.py"] + sorted((root / "sanitarne").glob("*.py")) + \
        sorted((root / "elektryka").glob("*.py")) + sorted((root / "energia").glob("*.py"))
    for f in files:
        if f.exists():
            h.update(f.read_bytes())
    h.update(Path(__file__).read_bytes())
    return h.hexdigest()[:16]


def pion_deszczowy(p: dict) -> bool:
    rodz = str(p.get("rodzaj", "")).lower()
    if rodz:
        return rodz in ("deszczowa", "kd", "rura_spustowa", "deszcz")
    txt = f"{p.get('opis', '')}".lower()
    return bool(re.match(r"^rs\d", str(p.get("id", "")).lower())) or "spustow" in txt or "deszcz" in txt


def oblicz(ctx) -> Wyniki:
    p = sciezki(ctx)
    key = _klucz(p)
    if key in _MEM:
        return _MEM[key]
    cache = Path("build/cache_instalacje") / f"wyniki_{key}.pkl"
    if cache.exists():
        try:
            w = pickle.loads(cache.read_bytes())
            _MEM[key] = w
            return w
        except Exception:
            pass
    w = _oblicz(p)
    _MEM[key] = w
    try:
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(pickle.dumps(w))
    except Exception:
        pass
    return w


def _oblicz(p: dict) -> Wyniki:
    from ...obliczenia.elektryka.bilans import bilans_mocy, odbiorniki_z_modelu
    from ...obliczenia.elektryka.obwody import oblicz_obwody
    from ...obliczenia.elektryka.odgromowa import ocena_ryzyka
    from ...obliczenia.elektryka.pv import oblicz_pv
    from ...obliczenia.inst_wspolne import dane_z_modelu, wentylacja_z
    from ...obliczenia.sanitarne.deszczowa import oblicz_deszczowa
    from ...obliczenia.sanitarne.drenaz import ocen_drenaz
    from ...obliczenia.sanitarne.kanalizacja import oblicz_kanalizacje
    from ...obliczenia.sanitarne.ogrzewanie import oblicz_ogrzewanie
    from ...obliczenia.sanitarne.woda import ParametryWoda, oblicz_wode

    dane = dane_z_modelu(p["budynek"], p["dzialka"], p["wyposazenie"], p["instalacje"])
    korekty = []
    piony = list(dane.inst.get("piony") or [])
    desz = [x for x in piony if pion_deszczowy(x)]
    if desz:
        dane.inst = dict(dane.inst, piony=[x for x in piony if not pion_deszczowy(x)], piony_deszczowe=desz)
        korekty.append("Piony deszczowe " + ", ".join(str(x.get("id")) for x in desz) + " wyłączone z grupowania pionów "
                       "wod.-kan. (w modelu `instalacje.piony` bez pola `rodzaj`).")
    obc = went_e = None
    try:                                  # Φ_HL i strumienie powietrza z modułu energii (jak CLI: --phi-hl energia)
        from ...obliczenia.instalacje import z_modulu_energii
        obc, went_e = z_modulu_energii(p["budynek"], p["dzialka"])
    except Exception as ex:               # pragma: no cover
        korekty.append(f"Moduł energii niedostępny ({type(ex).__name__}: {ex}) — Φ_HL wskaźnikowe, strumienie z modelu.")
    went = wentylacja_z(went_e, dane)
    V = max(went["suma_wyw"], went["suma_naw"]) or 330.0
    woda0 = oblicz_wode(dane, ParametryWoda())
    og = oblicz_ogrzewanie(dane, phi_hl=obc, cwu=woda0.cwu)
    P7 = float(dict(zip(og.pc["T"], og.pc["P"])).get(7, 6.0))
    woda = oblicz_wode(dane, ParametryWoda(P_PC_cwu_kW=P7))
    kan = oblicz_kanalizacje(dane)
    desz_w = oblicz_deszczowa(dane)
    dren = ocen_drenaz(dane)
    odb = odbiorniki_z_modelu(dane, ogrzewanie=og, woda=woda, wentylacja_m3h=V)
    pv = oblicz_pv(dane, ogrzewanie=og, woda=woda, wentylacja_m3h=V)
    bil = bilans_mocy(dane, odb, pv_kWp=pv.P_kWp)
    obw = oblicz_obwody(dane, odb, I_zab=bil.I_zab)
    odg = ocena_ryzyka(dane, pv=pv)
    return Wyniki(dane, woda, kan, desz_w, dren, og, bil, obw, pv, odg, went, odb, p, korekty, obc, went_e)
