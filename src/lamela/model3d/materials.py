"""Biblioteka materiałów PBR dla modelu 3D (kolor, szorstkość, metaliczność, przezroczystość, tekstura).

Kolejność ustalania: (1) ``materialy.<KOD>.pbr`` w budynek.yaml (rozszerzenie opcjonalne:
``pbr: {kolor: "#rrggbb", szorstkosc: 0.8, metal: 0.0, alpha: 1.0, tekstura: drewno|tynk|beton|..., uv: 1.0}``),
(2) kody pomocnicze IR (ramy, szkło, teren, otoczenie), (3) reguły wg kodu/nazwy materiału, (4) ``kolor`` z modelu.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PBR:
    color: str = "#cccccc"
    roughness: float = 0.85
    metallic: float = 0.0
    alpha: float = 1.0
    texture: str | None = None      # nazwa tekstury proceduralnej (textures.py)
    uv: float = 1.0                 # rozmiar kafla tekstury [m]
    double_sided: bool = False
    cast_shadow: bool = True
    emissive: str | None = None


# kody pomocnicze (IR) — ustalone
FIXED: dict[str, PBR] = {
    "RAMA_ALU": PBR("#2b2f33", 0.38, 0.55),
    "SZKLO": PBR("#9fb9c4", 0.04, 0.2, alpha=0.26, double_sided=True, cast_shadow=False),
    "SZKLO_BAL": PBR("#c9dde2", 0.04, 0.1, alpha=0.18, double_sided=True, cast_shadow=False),
    "STAL_BAL": PBR("#2c3034", 0.45, 0.6),
    "STAL_NIERDZ": PBR("#b9bdc0", 0.25, 0.9),
    "DRZWI_WEWN": PBR("#efece6", 0.5),
    "DRZWI_ZEWN": PBR("#34383c", 0.42, 0.35),
    "BRAMA_GAR": PBR("#3a3e42", 0.45, 0.4),
    "OBROBKA_BLACH": PBR("#3b3f43", 0.42, 0.5),
    "PARAPET_WEWN": PBR("#f1f0ec", 0.45),
    "SCHODY": PBR("#c7a276", 0.55, texture="parkiet", uv=1.0),
    "TEREN_TRAWA": PBR("#627f3c", 0.96, texture="trawa", uv=3.0),
    "TEREN_POZA": PBR("#72843f", 0.97, texture="trawa", uv=5.0),
    "NAW_KOSTKA": PBR("#6c6e71", 0.85, texture="kostka", uv=1.0),
    "NAW_KOSTKA_JASNA": PBR("#a9a59d", 0.85, texture="kostka", uv=1.0),
    "NAW_PLYTY": PBR("#bdb9b0", 0.8, texture="plyty", uv=1.2),
    "NAW_ASFALT": PBR("#4c4e51", 0.92, texture="asfalt", uv=4.0),
    "NAW_DESKA": PBR("#6d5847", 0.75, texture="deski", uv=1.0),
    "NAW_ZWIR": PBR("#a49e92", 0.95, texture="zwir", uv=1.0),
    "NAW_KRATKA": PBR("#7b8b58", 0.95, texture="trawa", uv=1.0),
    "NAW_BETON": PBR("#b3b0a8", 0.85, texture="beton", uv=2.0),
    "NAW_PODBUDOWA": PBR("#8f8b85", 0.95),
    "MULCZ": PBR("#4c3a2b", 1.0, texture="zwir", uv=1.0),
    "ZYWOPLOT": PBR("#3e5c2a", 0.95, texture="lisc", uv=1.5),
    "KORONA": PBR("#58773a", 0.9, texture="lisc", uv=1.5),
    "KORONA_BRZOZA": PBR("#7a9747", 0.9, texture="lisc", uv=1.5),
    "KORONA_IGL": PBR("#33502c", 0.9, texture="lisc", uv=1.5),
    "KRZEW": PBR("#4d6c33", 0.9, texture="lisc", uv=1.0),
    "PIEN": PBR("#594838", 0.95),
    "PIEN_BRZOZA": PBR("#d9d4c9", 0.9),
    "OGRODZENIE": PBR("#2e3236", 0.5, 0.5),
    "SIATKA": PBR("#2e3236", 0.5, 0.5, alpha=0.35, double_sided=True, cast_shadow=False),
    "PODMUROWKA": PBR("#9e9b96", 0.88, texture="beton", uv=2.0),
    "SASIEDNI_SCIANA": PBR("#e2ded6", 0.9),
    "SASIEDNI_DACH": PBR("#565a5f", 0.8),
    "AUTO_LAKIER_1": PBR("#d7dadd", 0.3, 0.6),
    "AUTO_LAKIER_2": PBR("#1f2b38", 0.28, 0.6),
    "AUTO_LAKIER_3": PBR("#3d4044", 0.3, 0.6),
    "AUTO_SZYBA": PBR("#1b2127", 0.1, 0.5),
    "AUTO_OPONA": PBR("#1c1c1c", 0.9),
}

RULES: list[tuple[str, PBR]] = [
    (r"SZKL|GLASS|SZYB", FIXED["SZKLO"]),
    (r"^TYNK.*(SIL|ZEW|ELEW|AKR|MINER)|ELEWAC", PBR("#f3f2ee", 0.92, texture="tynk", uv=2.0)),
    (r"TYNK|GLAD|GŁAD|GK|FARB|MALOW", PBR("#f4f2ee", 0.9)),
    (r"TERMO|LAMEL|MODRZ|DREWNO|TIMBER|WOOD|JESION|SOSN", PBR("#9b6a40", 0.68, texture="drewno", uv=1.0)),
    (r"KOMPOZ|DESKA_KOMP|WPC", PBR("#6d5a49", 0.75, texture="deski", uv=1.0)),
    (r"DESKA|PARKIET|DEB|DĄB|PODLOG|PANEL", PBR("#b58a5a", 0.55, texture="parkiet", uv=1.0)),
    (r"GRES|PLYTK|PŁYTK|TERAKOT|KAMIEN|KAMIEŃ|KONGL", PBR("#cdc7bd", 0.45, texture="plyty", uv=1.2)),
    (r"ZIELON|SEDUM|ROZCHOD|SUBSTRAT|EKSTENS", PBR("#6e7d3e", 0.95, texture="sedum", uv=2.0)),
    (r"ZWIR|ŻWIR|OTOCZ|GRYS", PBR("#a39d91", 0.95, texture="zwir", uv=1.0)),
    (r"^(ZB|ZELBET|ŻELBET|BET|C\d\d)|BETON", PBR("#bdb9b1", 0.85, texture="beton", uv=2.0)),
    (r"JASTRYCH|WYLEW|ANHYDR", PBR("#c9c5bb", 0.9)),
    (r"XPS", PBR("#a8cdb0", 0.9)),
    (r"PIR|PUR", PBR("#d8c98a", 0.9)),
    (r"WELN|WEŁN|^MW|WOOL", PBR("#d9c27a", 0.95)),
    (r"EPS|STYRO", PBR("#dedcd5", 0.95)),
    (r"EPDM|PAPA|MEMBR|HYDRO|PAROIZ|FOLIA|PVC|TPO", PBR("#303133", 0.8)),
    (r"SIL|SILIKAT|CEGL|CERAM|BLOCZ|PUSTAK|YTONG|GAZOBET|MUR|KAMIEN", PBR("#d9d4ca", 0.95)),
    (r"STAL|ALU|BLACH|METAL|INOX|CYNK|TYTAN", PBR("#3a3e42", 0.45, 0.55)),
    (r"PIASEK|GRUNT|PODSYP|ZIEMIA", PBR("#d4c39c", 0.98)),
]


def pbr_for(code: str, model=None) -> PBR:
    """Parametry PBR dla kodu materiału (z uwzględnieniem danych z modelu)."""
    mat = model.material(code) if model is not None and hasattr(model, "material") else None
    raw = getattr(mat, "raw", None) or {}
    over = raw.get("pbr") if isinstance(raw, dict) else None
    base = None
    if code in FIXED:
        base = FIXED[code]
    else:
        key = code.upper()
        name = (getattr(mat, "nazwa", "") or "").upper()
        for pat, p in RULES:
            if re.search(pat, key) or (name and re.search(pat, name)):
                base = p
                break
        if base is not None and re.search(r"EPS", key) and re.search(r"GRAFIT|031|032", key + " " + name):
            base = replace(base, color="#8f9296")
        if base is None:
            col = getattr(mat, "kolor", None) or "#c8c8c8"
            base = PBR(col, 0.85)
    if isinstance(over, dict):
        base = replace(base,
                       color=str(over.get("kolor", base.color)),
                       roughness=float(over.get("szorstkosc", base.roughness)),
                       metallic=float(over.get("metal", base.metallic)),
                       alpha=float(over.get("alpha", base.alpha)),
                       texture=over.get("tekstura", base.texture),
                       uv=float(over.get("uv", base.uv)))
    return base


def hex_rgb(c: str) -> tuple[float, float, float]:
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
