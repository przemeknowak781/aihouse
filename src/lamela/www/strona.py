"""Składanie strony (index.html) z danych modelu (``dane.zbierz``), rysunków SVG, renderów i treści ``www/tresc.yaml``.
Strona bez <!DOCTYPE>/<html>/<head>/<body> (szkielet dodaje platforma Artifact): na górze <title> i <style>."""
from __future__ import annotations

import json
from datetime import datetime
from html import escape as E
from pathlib import Path

import yaml

from . import elewacje as EL
from . import rzuty as RZ
from . import schematy as SC
from .dane import fm, fm_m2

STATIC = Path(__file__).resolve().parent / "static"
FONTY = ("https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,500..900&family=Caveat:wght@600;700"
         "&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap")
CDN = ["https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js",
       "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/loaders/GLTFLoader.js",
       "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js",
       "https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/environments/RoomEnvironment.js"]
DOP = {"N": "północy", "S": "południa", "E": "wschodu", "W": "zachodu"}
MIEJSC = {"N": "północnej", "S": "południowej", "E": "wschodniej", "W": "zachodniej"}
LINIE_MAT = {"izolacja": "WELNA_FAS", "hydro": "HYDRO_PODPL", "szczelnosc": "MEMB_PAROSZ", "zewn": "DREWNO_TERMO"}


def wartosci(D: dict, tr: dict, teraz: datetime) -> dict:
    """Płaski słownik sformatowanych wartości do znaczników {klucz} w treściach (www/tresc.yaml)."""
    w, en, ins, dm, P = D["wsk"], D["en"] or {}, D["inst"], D["dzialka_min"], D["pow"]
    ori = D["orientacja"]
    gar_st = w["miejsca_postojowe"].get("garaz") or ins.get("garaz_stanowiska")
    return dict(
        nazwa=D["meta"].get("nazwa", ""), PU=fm_m2(P["PU"]), zabudowa=fm_m2(w["pow_zabudowy"]["wartosc"]),
        kubatura=f'{fm(D["kubatura"], 1)} m³', wys_zab=f'{fm(w["wysokosc_zabudowy"]["wartosc"])} m',
        kondygnacje=str(w["kondygnacje_nadziemne"]["wartosc"]), garaz_st=str(gar_st), garaz_A=fm_m2(P["garaz"]),
        EP=fm(en.get("EP"), 1), EP_max=fm(en.get("EP_max"), 0), pv_kWp=fm(ins.get("pv_kWp")),
        dz_szer=fm(dm["szer"]), dz_gl=fm(dm["gl"]), dz_lz=fm(dm["N"]["d"]) if dm["N"]["d"] is not None else "—",
        droga=DOP.get(ori.get("droga") or "N", "północy"), ogrod=DOP.get(ori.get("najwiecej") or "S", "południa"),
        zbiornik_V=fm(D["woda"]["zbiornik_V"], 1), niecka_A=fm_m2(D["woda"]["niecka_A"], 0),
        wt_uwagi=str(D["meta"].get("uwagi") or "zgodnie z modelem"), data=teraz.strftime("%d.%m.%Y"))


def tx(s: str, W: dict) -> str:
    """Treść z YAML: escape HTML, potem wstawki {klucz} (wartości też escapowane)."""
    out = E(str(s))
    for k, v in W.items():
        out = out.replace("{" + k + "}", E(str(v)))
    return out


def sekcja(id_: str, etykieta: str, tytul: str, metryka_extra: str, tresc: str, sep: str) -> str:
    return (f'<div class="wrap">{sep}</div><section class="wrap sek" id="{id_}" aria-labelledby="{id_}-h">'
            f'<div class="metryka"><span class="etk">{E(etykieta)}</span><h2 id="{id_}-h">{E(tytul)}</h2>{metryka_extra}</div>'
            f'<div class="tresc">{tresc}</div></section>')


def glowa(D: dict, tr: dict, css: str, W: dict) -> str:
    kol = {k: (D["model"].material(v).kolor if D["model"].material(v) else None) for k, v in LINIE_MAT.items()}
    dom = {"izolacja": "#D8C98A", "hydro": "#3F7FBF", "szczelnosc": "#2E7D32", "zewn": "#9B6B41"}
    linie = ";".join(f"--l-{k}:{kol.get(k) or dom[k]}" for k in dom)
    opis = E(f'{W["nazwa"]} — projekt domu jednorodzinnego, PU {W["PU"]}, {W["kondygnacje"]} kondygnacje, dach płaski.')
    return (f'<title>{E(W["nazwa"])}</title>\n<meta name="description" content="{opis}">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTY}">\n<style>\n{css}\n:root{{{linie}}}\n</style>\n')
