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


def _slonce_txt(r: dict) -> str:
    s = (r or {}).get("slonce") or {}
    if not s.get("data"):
        return ""
    d = datetime.strptime(s["data"], "%Y-%m-%d")
    return f'{d.day}.{d.month:02d}, godz. {s.get("godz", "")}, Słońce: azymut {fm(s["az"], 0)}°, wysokość {fm(s["el"], 0)}°'


def naglowek(tr: dict, W: dict) -> str:
    mk = tr["marka"]
    nav = [("parametry", "Parametry"), ("galeria", "Wizualizacje"), ("rzuty", "Rzuty"), ("model-3d", "Model 3D"),
           ("technologia", "Technologia"), ("energia", "Energia"), ("dzialka", "Działka"), ("pakiety", "Pakiety"),
           ("zapytanie", "Zapytanie")]
    linki = "".join(f'<a href="#{a}">{E(b)}</a>' for a, b in nav)
    return (f'<a class="pomin" href="#tresc">Przejdź do treści</a><header class="gora"><div class="wrap">'
            f'<a class="marka" href="#top"><b>{E(mk["nazwa"])}</b><span>{E(mk["podtytul"])}</span></a>'
            f'<span class="chip">{E(mk["oznaczenie"])}</span>'
            f'<nav class="nav" aria-label="Sekcje strony">{linki}</nav></div></header>')


def hero(D: dict, tr: dict, W: dict, R: dict, sep: str) -> str:
    h = tr["hero"]
    adn = ""
    for kadr, cls in (("ogrod_169", "adn-169"), ("ogrod_43", "adn-43")):
        for lit, p in (R.get("kotwice", {}).get(kadr) or {}).items():
            adn += f'<span class="adn {cls}" style="left:{p["x"]}%;top:{p["y"] - 2.5:.2f}%" aria-hidden="true">{E(lit)}</span>'
    info = R.get("pliki", {}).get("ogrod_169") or {}
    w, dm = D["wsk"], D["dzialka_min"]
    kaf = [("Powierzchnia użytkowa", fm(D["pow"]["PU"]), "m²", "RPB § 20, PN-ISO 9836"),
           ("Powierzchnia zabudowy", fm(w["pow_zabudowy"]["wartosc"]), "m²", "upzp art. 2 pkt 35"),
           ("Wysokość zabudowy", fm(w["wysokosc_zabudowy"]["wartosc"]), "m", "upzp art. 2 pkt 30"),
           ("Kubatura brutto", fm(D["kubatura"], 1), "m³", "PN-ISO 9836"),
           ("Kondygnacje nadziemne", str(w["kondygnacje_nadziemne"]["wartosc"]), "", "upzp art. 2 pkt 34"),
           ("Działka min.", f'{fm(dm["szer"], 1)} × {fm(dm["gl"], 1)}', "m", "WT § 12, linia zabudowy")]
    tab = "".join(f'<div><span class="etk">{E(a)}</span><span class="w">{E(b)}<small>{E(c)}</small></span>'
                  f'<span class="p">{E(d)}</span></div>' for a, b, c, d in kaf)
    return (f'<section class="hero wrap" id="top" aria-labelledby="h-nazwa">'
            f'<figure class="hero-fig"><picture><source media="(max-width: 700px)" srcset="assets/ogrod_43.webp">'
            f'<img src="assets/ogrod_169.webp" width="1920" height="1080" fetchpriority="high" '
            f'alt="Dom LAMELA od strony ogrodu: przeszklony parter, pełne piętro z boksem w ramie i najwyższa bryła w pionowych lamelach">'
            f'</picture>{adn}</figure>'
            f'<div class="hero-cap"><span>Widok od ogrodu, render z modelu 3D · {E(_slonce_txt(info))}</span>'
            f'<span>A–G: litery ze szkicu Inwestora</span></div>'
            f'<div class="hero-tyt"><h1 id="h-nazwa"><span class="kod">Projekt {E(tr["marka"]["kod_projektu"])} · dom jednorodzinny</span>'
            f'{E(h["naglowek"])}</h1><div><p class="lead">{tx(h["lead"], W)}</p><div class="cta">'
            f'<a class="btn btn-g" href="#rzuty">{E(h["cta_1"])}</a><a class="btn" href="#zapytanie">{E(h["cta_2"])}</a>'
            f'</div></div></div><div class="tabliczka" aria-label="Kluczowe parametry">{tab}</div></section>')


def _wiersz(a, b, c, cls=""):
    return f'<tr class="{cls}"><td>{a}</td><td class="l">{b}</td><td class="pod">{c}</td></tr>'


def parametry(D: dict, tr: dict, W: dict, sep: str) -> str:
    w, P, en, dm, ori = D["wsk"], D["pow"], D["en"] or {}, D["dzialka_min"], D["orientacja"]
    H = w["wysokosc_zabudowy"]
    zal = " Najwyższy punkt: " + E(str(H.get("element", ""))) + "." if H.get("element") else ""
    rows = [_wiersz("Powierzchnia użytkowa (PU)", f"<b>{fm_m2(P['PU'])}</b>", E(P["metoda"]))]
    for k in D["kondygnacje"]:
        rows.append(_wiersz(f"— {E(k['nazwa'])} ({k['id']})", fm_m2(k["PU"]), f"wys. kondygnacji {fm(k['h'])} m, "
                            f"w świetle {fm(k['h_sw'])} m; pow. brutto {fm_m2(k['brutto'])}"))
    rows += [
        _wiersz("Garaż (poza PU)", fm_m2(P["garaz"]), f"{W['garaz_st']} stanowiska w bryle parteru; miejsca postojowe "
                f"na działce razem: {w['miejsca_postojowe']['wartosc']} (dzialka.yaml)"),
        _wiersz("Pomieszczenia techniczne (poza PU)", fm_m2(P["techniczne"]), "kategoria techniczna PN-ISO 9836"),
        _wiersz("Powierzchnia zabudowy", fm_m2(w["pow_zabudowy"]["wartosc"]), E(w["pow_zabudowy"]["podstawa"])),
        _wiersz("Wysokość zabudowy", f'{fm(H["wartosc"])} m', E(H["podstawa"]) + ": H = z<sub>top</sub> − t<sub>śr</sub> = "
                f'{fm(H["z_top_abs"], 2)} − {fm(H["t_sr"], 2)} m n.p.m.' + zal),
        _wiersz("Wysokość budynku (WT § 6)", f'{fm(w["wysokosc_WT6"]["wartosc"])} m',
                f'grupa wysokości: {"niski (N)" if w["wysokosc_WT6"].get("grupa") == "N" else E(str(w["wysokosc_WT6"].get("grupa")))}; '
                + E(w["wysokosc_WT6"]["podstawa"])),
        _wiersz("Kubatura brutto", f'{fm(D["kubatura"], 1)} m³', "PN-ISO 9836: od spodu płyty do wierzchu pokrycia, bez attyk"),
        _wiersz("Kondygnacje nadziemne", str(w["kondygnacje_nadziemne"]["wartosc"]), E(w["kondygnacje_nadziemne"]["podstawa"])),
        _wiersz("Dach", f'płaski, {fm(w["kat_dachu"]["wartosc"], 1)}°',
                f'spadek {fm(100 * max(d["spadek"] or 0 for d in D["woda"]["dachy"]), 0)} % na izolacji spadkowej; '
                f'{len(D["woda"]["dachy"])} pola dachu, w tym dach zielony nad garażem'),
        _wiersz("Gabaryty (lica ścian)", f'{fm(D["gabaryty"]["dl"])} × {fm(D["gabaryty"]["szer"])} m', "rzut ścian zewnętrznych wszystkich kondygnacji"),
        _wiersz("Działka minimalna", f'{fm(dm["szer"])} × {fm(dm["gl"])} m', 'WT § 12 + linia zabudowy — <a href="#dzialka">metoda</a>'),
        _wiersz("Orientacja zalecana", f'wjazd od {DOP.get(ori["droga"] or "N")}',
                f'strefa dzienna i {fm(100 * ori["przeszklenia"][ori["najwiecej"]] / max(1e-6, sum(ori["przeszklenia"].values())), 0)} % '
                f'przeszkleń od {DOP.get(ori["najwiecej"])}; azymut osi y modelu {fm(ori["azymut_osi_y"], 0)}°'),
        _wiersz("Energia pierwotna EP", f'{fm(en.get("EP"), 1)} kWh/(m²·rok)',
                f'wymaganie ≤ {fm(en.get("EP_max"), 0)}; klasa energetyczna — nie wyznaczana przez moduł obliczeń'),
    ]
    tab = (f'<div class="tab-wrap"><table><thead><tr><th>Parametr</th><th class="l">Wartość</th><th>Podstawa i metoda</th>'
           f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
    meta = D["meta"]
    extra = (f'<p class="nota">Wartości z modelu projektu w wersji {E(str(meta.get("wersja", "")))} '
             f'z {E(str(meta.get("data", "")))} ({E(str(meta.get("stadium", "")))}). Walidacja modelu: '
             f'{D["walidacja"]["bledy"]} błędów, {D["walidacja"]["ostrzezenia"]} ostrzeżeń.</p>')
    return sekcja("parametry", "Metryka projektu", "Parametry", extra, tab, sep)


def litery(D: dict) -> list[tuple]:
    """Litery szkicu Inwestora z opisem i wymiarami odczytanymi z modelu."""
    m = D["model"]
    ks = m.kondygnacje
    ob = {k.id: m.obrys_kondygnacji(k.id).bounds for k in ks}
    b = {q["id"]: q for q in SC.pasma_poludniowe(m)}
    out = []
    if len(ks) >= 3:
        lam = next((q for q in m.lamele() if str(q.get("elewacja")) == "S" and float(q.get("z_od", 0)) > 3), None)
        mat = m.material(lam["mat"]).nazwa.split(",")[0] if lam and m.material(lam["mat"]) else "drewno"
        out.append(("A", f"{ks[2].nazwa}: bryła w pionowych lamelach ({mat.lower()})",
                    f"wysunięta {fm(ob[ks[1].id][0] - ob[ks[2].id][0])} m na zachód poza lico piętra niżej"
                    + (f"; rozstaw lamel {fm(lam['rozstaw'] * 100, 0)} cm" if lam else "")))
        out.append(("B", f"{ks[1].nazwa}: pełna bryła w tynku",
                    f"długość {fm(ob[ks[1].id][2] - ob[ks[1].id][0])} m, cofnięta względem bryły A"))
    ram = sorted([q for q in b.values() if str(q["id"]).startswith("PL-C")], key=lambda q: q["z"])
    if ram:
        n = sum(1 for o in m.otwory(kond=ks[1].id) if o.symbol == "BC1")
        out.append(("C", "Boks w lekkiej ramie stalowej", f"rama długości {fm(ram[0]['x1'] - ram[0]['x0'])} m, "
                    f"wysunięta {fm(ob[ks[1].id][1] - min(q['y0'] for q in ram))} m przed lico; "
                    f"{n} kwatery okna"))
    if "PL-D" in b and ram:
        x0, x1 = min(ram[0]["x0"], b["PL-D"]["x0"]), max(ram[0]["x1"], b["PL-D"]["x1"])
        out.append(("D", "Pozioma linia — głęboka krawędź", f"na rzędnej +{fm(b['PL-D']['z'])} m, "
                    f"{fm(x1 - x0)} m do narożnika garażu"))
    s0 = [o for o in m.otwory(kond=ks[0].id) if o.kierunek_zewn is not None and o.kierunek_zewn[1] < -0.9
          and o.typ in ("fix", "okno", "drzwi_przesuwne_HS")]
    if s0:
        out.append(("E", f"{ks[0].nazwa}: przeszklenie od ogrodu", f"{len(s0)} kwater, razem {fm(sum(o.szer for o in s0))} m "
                    f"szerokości i {fm(max(o.wys for o in s0))} m wysokości"))
    zd = [d for d in D["woda"]["dachy"] if str(d.get("przegroda", "")).startswith("DZ")]
    out.append(("G", "Garaż w bryle parteru", f"{fm_m2(D['pow']['garaz'])}, {D['inst'].get('garaz_stanowiska')} stanowiska"
                + (f"; nad nim dach zielony {fm_m2(sum(d['A'] for d in zd), 0)}" if zd else "")))
    return out


def idea(D: dict, tr: dict, W: dict, szkic: dict, sep: str) -> str:
    t = tr["idea"]
    li = "".join(f'<li><span class="lt" aria-hidden="true">{E(a)}</span><div><p><b>{E(a)} · {E(b)}</b></p>'
                 f'<p class="num">{E(c)}</p></div></li>' for a, b, c in litery(D))
    ar = f'{szkic["W"]} / {szkic["H"]}'
    body = (f'<p class="lead">{tx(t["tekst"], W)}</p>'
            f'<div class="szkic-box"><span class="etk">Szkic Inwestora · przetworzony z fotografii</span>'
            f'<div class="szkic" role="img" aria-label="Szkic odręczny elewacji ogrodowej: trzy przesunięte pasma, lamele, przeszklony parter" '
            f'style="--szkic:url(assets/szkic.png);--szkic-ar:{ar}"></div></div>'
            f'<ul class="litery">{li}</ul>')
    return sekcja("idea", "Idea", t["tytul"], '<p class="nota">Litery A–G oznaczają te same elementy na szkicu, '
                  'na renderze w nagłówku strony i w opisie obok.</p>', body, sep)


GAL = [("ogrod", "Od ogrodu", "z poziomu oczu, elewacja południowa"),
       ("lotniczy", "Z lotu ptaka", "od południowego wschodu"),
       ("ulica", "Od ulicy", "elewacja północna z wejściem i bramą garażu"),
       ("aksonometria", "Aksonometria rozwarstwiona", "kondygnacje rozsunięte w pionie")]


def galeria(D: dict, tr: dict, W: dict, R: dict, sep: str) -> str:
    fig = ""
    for i, (u, tyt, op) in enumerate(GAL):
        info = R.get("pliki", {}).get(f"{u}_169") or {}
        sl = _slonce_txt(info) if u != "aksonometria" else "światło studyjne, rzut aksonometryczny"
        opis = f"{tyt} — {op}. {sl}"
        fig += (f'<figure class="{"szer" if i == 0 else ""}"><button type="button" data-duzy="assets/{u}_169.webp" '
                f'data-opis="{E(opis)}" aria-label="Powiększ: {E(tyt)}"><picture>'
                f'<source media="(max-width: 700px)" srcset="assets/{u}_43.webp">'
                f'<img src="assets/{u}_169.webp" width="1920" height="1080" loading="lazy" alt="{E(tyt)}: {E(op)}">'
                f'</picture></button><figcaption><b>{E(tyt)}</b> · {E(op)}. {E(sl)}</figcaption></figure>')
    dlg = ('<dialog class="lupa" id="lupa" aria-label="Powiększenie wizualizacji"><img id="lupa-img" src="" alt="">'
           '<div class="lupa-pasek"><p id="lupa-opis"></p><button type="button" id="lupa-poprz">Poprzednia</button>'
           '<button type="button" id="lupa-nast">Następna</button><button type="button" id="lupa-zamknij">Zamknij</button>'
           '</div></dialog>')
    return sekcja("galeria", "Wizualizacje", tr["galeria"]["tytul"], f'<p class="nota">{tx(tr["galeria"]["opis"], W)}</p>',
                  f'<div class="gal">{fig}</div>{dlg}', sep)


KAT = {"podstawowa": "podstawowa", "pomocnicza": "pomocnicza", "ruchu": "komunikacja", "techniczna": "techniczna"}


def rzuty_sekcja(D: dict, tr: dict, W: dict, sep: str) -> str:
    m = D["model"]
    okno = RZ.zasieg(m)
    zak, pan = "", ""
    wiersze = {k["id"]: [] for k in D["kondygnacje"]}
    for r in D["pow"]["pomieszczenia"]:
        wiersze.setdefault(r["kond"], []).append(r)
    for i, k in enumerate(D["kondygnacje"]):
        kid = k["id"]
        rz = RZ.rzut(D, kid, okno)
        zak += (f'<button type="button" role="tab" id="t-rz-{kid}" aria-controls="p-rz-{kid}" '
                f'aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}">{E(k["nazwa"])}</button>')
        tr_ = ""
        for r in sorted(wiersze.get(kid, []), key=lambda q: q["id"]):
            pu = fm(r["A_zal"]) if r["grupa"] == "PU" else {"garaz": "garaż", "klatka": "klatka", "techniczne": "techn."}[r["grupa"]]
            wsp = "" if r["wsp"] in (1, 1.0) or r["grupa"] != "PU" else f' <span class="etk">({int(r["wsp"] * 100)} %)</span>'
            tr_ += (f'<tr data-pom="{E(r["id"])}" tabindex="0"><td class="nr">{E(r["id"])}</td><td>{E(r["nazwa"])}</td>'
                    f'<td class="l">{fm(r["A"])}</td><td class="l">{pu}{wsp}</td></tr>')
        tr_ += (f'<tr class="suma"><td></td><td>PU kondygnacji</td><td class="l"></td><td class="l">{fm(k["PU"])}</td></tr>')
        tab = (f'<div class="tab-wrap"><table><caption class="pomin">Zestawienie pomieszczeń — {E(k["nazwa"])}</caption>'
               f'<thead><tr><th>Nr</th><th>Pomieszczenie</th><th class="l">Netto m²</th><th class="l">PU m²</th></tr></thead>'
               f'<tbody>{tr_}</tbody></table></div>')
        pan += (f'<div class="panel" role="tabpanel" id="p-rz-{kid}" aria-labelledby="t-rz-{kid}"{"" if i == 0 else " hidden"}>'
                f'<div class="uklad-rzut"><div class="rys-box">{rz["svg"]}</div><div>{tab}</div></div></div>')
    leg = "".join(f'<li><i style="background:var(--d-room{j})"></i>{E(v)}</li>'
                  for j, v in enumerate(KAT.values(), start=1))
    leg += '<li><i style="background:var(--d-ins)"></i>izolacja termiczna w ścianie</li>'
    P = D["pow"]
    extra = (f'<p class="nota">PU razem: {fm_m2(P["PU"])} (P0 {fm(P["PU_kond"].get("P0"))}, P1 {fm(P["PU_kond"].get("P1"))}, '
             f'P2 {fm(P["PU_kond"].get("P2"))}). Garaż {fm_m2(P["garaz"])}, pomieszczenia techniczne {fm_m2(P["techniczne"])} '
             f'i klatka schodowa {fm_m2(P["klatki"])} — poza PU. Wysokość cięcia rzutu +{fm(RZ.CIECIE)} m.</p>')
    body = (f'<p class="lead">{tx(tr["rzuty"]["opis"], W)}</p><div class="zakl" role="tablist" aria-label="Kondygnacje">{zak}</div>'
            f'{pan}<ul class="legenda">{leg}</ul>')
    return sekcja("rzuty", "Rzuty z umeblowaniem", tr["rzuty"]["tytul"], extra, body, sep)


def elewacje_sekcja(D: dict, tr: dict, W: dict, arkusze: Path | None, sep: str) -> str:
    m = D["model"]
    x0, y0, x1, y1 = m.bbox()
    top = max(p.z1 for p in D["ir"].prisms if p.meta.get("group") not in ("otoczenie", "teren") and p.kind != "terrain")
    zr = (-1.4, top + 1.1)
    zak, pan = "", ""
    poz = [("S", "Południowa"), ("N", "Północna"), ("E", "Wschodnia"), ("W", "Zachodnia")]
    for st, nz in poz:
        fu = EL.KIER[st][0]
        us = [fu(x, y) for x in (x0, x1) for y in (y0, y1)]
        svg = EL.elewacja(D, st, (min(us) - 2.2, max(us) + 2.2), zr)
        pan += f'<div class="panel" role="tabpanel" id="p-el-{st}" aria-labelledby="t-el-{st}"{"" if st == "S" else " hidden"}>' \
               f'<div class="rys-box">{svg}</div></div>'
        zak += (f'<button type="button" role="tab" id="t-el-{st}" aria-controls="p-el-{st}" aria-selected="{"true" if st == "S" else "false"}" '
                f'tabindex="{0 if st == "S" else -1}">{nz}</button>')
    for sec in EL.przekroje_def(m, arkusze):
        sid = str(sec.get("id"))
        svg = EL.przekroj(D, sec, zr)
        pl = f'x = {fm(sec["x"])} m' if "x" in sec else f'y = {fm(sec["y"])} m'
        pan += (f'<div class="panel" role="tabpanel" id="p-el-{sid}" aria-labelledby="t-el-{sid}" hidden><div class="rys-box">{svg}</div>'
                f'<p class="etk" style="margin-top:.6rem">Płaszczyzna {E(pl)}, widok na {E(MIEJSC.get(str(sec.get("patrz")), "")).replace("ej", "")} · '
                f'kolor: izolacja termiczna przecięta, ciemny: konstrukcja</p></div>')
        zak += f'<button type="button" role="tab" id="t-el-{sid}" aria-controls="p-el-{sid}" aria-selected="false" tabindex="-1">Przekrój {E(sid)}-{E(sid)}</button>'
    body = (f'<p class="lead">{tx(tr["elewacje"]["opis"], W)}</p><div class="zakl" role="tablist" aria-label="Elewacje i przekroje">{zak}</div>{pan}')
    return sekcja("elewacje", "Rysunki", tr["elewacje"]["tytul"], "", body, sep)
