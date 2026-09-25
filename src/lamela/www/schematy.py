"""Schematy strony z modelu: pasma elewacji południowej (separator sekcji), przegrody warstwowe (skala grubości,
kolory materiałów, „4 linie”), schemat minimalnej działki (WT § 12) i punkty kotwiczące liter szkicu (A–G)."""
from __future__ import annotations

from html import escape

from shapely.geometry import Polygon
from shapely.ops import unary_union

from .dane import fm
from .svg import Arkusz

LINIE = {"izolacja": "izolacja termiczna", "hydro": "hydroizolacja / przeciwwilgociowa",
         "szczelnosc": "szczelność powietrzna i paroizolacja", "zewn": "warstwa zewnętrzna"}


def pasma_poludniowe(m) -> list[dict]:
    """Poziome pasma elewacji ogrodowej: płyty wysunięte na południe (≥ 3 m długości) i ich rzędne — rytm „S”."""
    out = []
    for w in m.wsporniki():
        try:
            g = Polygon(w["obrys"])
        except Exception:  # noqa: BLE001
            continue
        x0, y0, x1, y1 = g.bounds
        if y0 < -0.5 and x1 - x0 >= 3.0 and w.get("wierzch") is not None:
            out.append(dict(id=w.get("id"), x0=x0, x1=x1, y0=y0, z=float(w["wierzch"]), t=float(w.get("grubosc") or 0.2)))
    return sorted(out, key=lambda b: -b["z"])


def separator_svg(m) -> str:
    """Separator sekcji = pasma elewacji S w skali (długość i przesunięcie W–E, kolejność pionowa jak w elewacji)."""
    b = pasma_poludniowe(m)
    if not b:
        return ""
    X0, X1 = min(q["x0"] for q in b), max(q["x1"] for q in b)
    zs = sorted({round(q["z"], 2) for q in b}, reverse=True)
    W, H = 1000.0, 8.0 * len(zs) + 4
    lines = []
    for q in b:
        y = 4 + 8 * zs.index(round(q["z"], 2))
        x0, x1 = (q["x0"] - X0) / (X1 - X0) * W, (q["x1"] - X0) / (X1 - X0) * W
        lines.append(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}"/>')
    return (f'<svg class="pasma" viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" aria-hidden="true" '
            f'focusable="false">{"".join(lines)}</svg>')


def grubosc_cm(d: float) -> str:
    v = d * 100
    return fm(v, 0) if abs(v - round(v)) < 0.05 else fm(v, 1)


def krotka_nazwa(n: str) -> str:
    """Nazwa materiału bez dopisków: „ETICS: warstwa zbrojona + tynk silikonowy 1,5 mm (…)” → „Warstwa zbrojona + tynk
    silikonowy”; „Tynk gipsowy maszynowy 1,5 cm” → „Tynk gipsowy maszynowy”."""
    import re
    n = n.split(" (")[0]
    if ":" in n:
        a, b = n.split(":", 1)
        n = b if len(a) < 12 else a
    n = re.split(r",\s(?=\D)", n)[0]
    n = re.sub(r"\s\d+([,.]\d+)?\s?(cm|mm)$", "", n.strip()).strip(" —-")
    return n[:1].upper() + n[1:]


def przegroda_html(p: dict, skala: float = 900.0, d_max: float | None = None) -> str:
    """Pasek warstw w skali grubości (1 m = ``skala`` j.) + lista warstw; ``data-linia`` = przynależność do 4 linii."""
    x = 0.0
    rects, marks = [], []
    for w in p["warstwy"]:
        dw = max(w["d"] * skala, 1.2)
        rects.append(f'<rect x="{x:.1f}" y="0" width="{dw:.1f}" height="60" fill="{w["kolor"]}">'
                     f'<title>{escape(w["nazwa"])} — {fm(w["d"] * 100, 1)} cm</title></rect>')
        if w["linia"] in LINIE:
            marks.append(f'<rect class="ln ln-{w["linia"]}" x="{x:.1f}" y="66" width="{dw:.1f}" height="8"/>')
        x += dw
    vb = max(x, (d_max or 0) * skala)
    svg = (f'<svg class="przeg-bar" viewBox="0 0 {vb:.0f} 76" preserveAspectRatio="xMinYMid meet" role="img" '
           f'aria-label="Warstwy przegrody {escape(p["kod"])} w skali grubości">{"".join(rects)}{"".join(marks)}</svg>')
    li = "".join(f'<li data-linia="{w["linia"]}"><span class="sw" style="background:{w["kolor"]}"></span>'
                 f'<span class="wn">{escape(w["nazwa"].split(" (")[0])}</span>'
                 f'<span class="wd">{grubosc_cm(w["d"])} cm</span></li>' for w in p["warstwy"])
    return f'{svg}<ol class="warstwy">{li}</ol>'


def dzialka_svg(D: dict) -> str:
    """Schemat minimalnej działki: prostokąt granic, obrys budynku i elementów, odległości od granic."""
    m, dm = D["model"], D["dzialka_min"]
    xW, yS, xE, yN = dm["ramka"]
    ark = Arkusz(xW - 3.2, yS - 3.2, xE + 3.2, yN + 4.6, klasa="rys rys-dz", tytul="Schemat minimalnej działki")
    ark.rect(xW - 3.0, yN, xE + 3.0, yN + 3.0, "dz-droga")
    ark.text((xW + xE) / 2, yN + 1.5, "droga (dojazd od północy)", "dz-t", dy=8)
    ark.path(ark.d_ring([(xW, yS), (xE, yS), (xE, yN), (xW, yN), (xW, yS)]), "dz-gr")
    el = [Polygon(w["obrys"]) for w in m.wsporniki() if w.get("obrys")] + \
         [Polygon(t["obrys"]) for t in m.tarasy() if t.get("obrys")]
    ark.geom(unary_union(el), "dz-el")
    ark.geom(unary_union([m.obrys_kondygnacji(k.id) for k in m.kondygnacje]), "dz-bud")
    ob = unary_union([m.obrys_kondygnacji(k.id) for k in m.kondygnacje] + el)
    bx0, by0, bx1, by1 = ob.bounds
    ym, xm = (by0 + by1) / 2, (bx0 + bx1) / 2
    for (a, b, lab) in (((xW, ym), (bx0, ym), f'{fm(bx0 - xW)} m'), ((bx1, ym), (xE, ym), f'{fm(xE - bx1)} m'),
                        ((xm, yS), (xm, by0), f'{fm(by0 - yS)} m'), ((xm, by1), (xm, yN), f'{fm(yN - by1)} m')):
        ark.line([a, b], "dz-wym")
        ark.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, lab, "dz-t dz-tw", dy=-8)
    ark.line([(xW, yS - 1.6), (xE, yS - 1.6)], "dz-wym")
    ark.text((xW + xE) / 2, yS - 1.6, f'szerokość min. {fm(dm["szer"])} m', "dz-t dz-tb", dy=-10)
    ark.line([(xE + 1.6, yS), (xE + 1.6, yN)], "dz-wym")
    ark.text(xE + 1.6, (yS + yN) / 2, f'{fm(dm["gl"])} m', "dz-t dz-tb", dy=0,
             extra=f' transform="rotate(-90 {ark.X(xE + 1.6):.0f} {ark.Y((yS + yN) / 2):.0f})"')
    return ark.svg(id_="dzialka-min", aria=f'Schemat minimalnej działki {fm(dm["szer"])} × {fm(dm["gl"])} m')


def kotwice_szkicu(D: dict) -> dict:
    """Punkty (x, y, z) liter szkicu Inwestora na bryle — do rzutu na render od ogrodu."""
    m = D["model"]
    out = {}
    lam = next((q for q in m.lamele() if str(q.get("elewacja")) == "S" and float(q.get("z_od", 0)) > 3), None)
    if lam:
        xs = [p[0] for p in lam["linia"]]
        off = float(lam.get("odsuniecie") or 0.0) + float(lam.get("h") or 0.0)
        out["A"] = ((min(xs) + max(xs)) / 2 - 2.5, lam["linia"][0][1] - off, (lam["z_od"] + lam["z_do"]) / 2)
    ks = m.kondygnacje
    if len(ks) > 1:
        g = m.obrys_kondygnacji(ks[1].id)
        x0, y0, x1, y1 = g.bounds
        out["B"] = (x0 + 1.0, y0, ks[1].rzedna + 1.7)
    b = {q["id"]: q for q in pasma_poludniowe(m)}
    ram = [q for q in b.values() if str(q["id"]).startswith("PL-C")]
    if len(ram) >= 2:
        lo, hi = min(ram, key=lambda q: q["z"]), max(ram, key=lambda q: q["z"])
        out["C"] = ((lo["x0"] + lo["x1"]) / 2 + 1.2, lo["y0"], (lo["z"] + hi["z"] - hi["t"]) / 2)
    if "PL-D" in b:
        q = b["PL-D"]
        out["D"] = ((q["x0"] + q["x1"]) / 2, q["y0"], q["z"] - q["t"] / 2)
    s0 = [o for o in m.otwory(kond=ks[0].id) if o.kierunek_zewn is not None and o.kierunek_zewn[1] < -0.9
          and o.typ in ("fix", "okno", "drzwi_przesuwne_HS")]
    if s0:
        xs = [o.srodek[0] for o in s0]
        out["E"] = (sum(xs) / len(xs) - 1.5, min(o.srodek[1] for o in s0) - 0.3, 1.2)
    gar = next((r for r in m.pomieszczenia(ks[0].id) if str(r.raw.get("rodzaj")) == "garaz"), None)
    if gar is not None and gar.polygon is not None:
        g0 = m.obrys_kondygnacji(ks[0].id)
        out["G"] = (gar.polygon.centroid.x, g0.bounds[1], 1.6)
    return out
