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
BIER = {"N": "północ", "S": "południe", "E": "wschód", "W": "zachód"}
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


def _pominiete(R: dict) -> str:
    d = R.get("pominiete_drzewa") or []
    if not d:
        return ""
    return "W ujęciu pominięto " + ", ".join(f'{x["gatunek"].split("(")[0].strip()} ({x["id"]})' for x in d) + \
        " — drzewo z projektu zieleni zasłaniałoby elewację."


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
            f'<div class="hero-cap"><span>Widok od ogrodu, render z modelu 3D · {E(_slonce_txt(info))}. {E(_pominiete(R))}</span>'
            f'<span>A–G: litery ze szkicu Inwestora</span></div>'
            f'<div class="hero-tyt"><h1 id="h-nazwa"><span class="kod">Projekt {E(tr["marka"]["kod_projektu"])} · dom jednorodzinny</span>'
            f'{E(h["naglowek"])}</h1><p class="lead">{tx(h["lead"], W)}</p><div class="cta">'
            f'<a class="btn btn-g" href="#rzuty">{E(h["cta_1"])}</a><a class="btn" href="#zapytanie">{E(h["cta_2"])}</a>'
            f'</div></div><div class="tabliczka" aria-label="Kluczowe parametry">{tab}</div></section>')


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
        if u == "ogrod" and _pominiete(R):
            sl += ". " + _pominiete(R)
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
                f'<p class="etk" style="margin-top:.6rem">Płaszczyzna {E(pl)}, widok na {E(BIER.get(str(sec.get("patrz")), ""))} · '
                f'kolor: izolacja termiczna przecięta, ciemny: konstrukcja</p></div>')
        zak += f'<button type="button" role="tab" id="t-el-{sid}" aria-controls="p-el-{sid}" aria-selected="false" tabindex="-1">Przekrój {E(sid)}-{E(sid)}</button>'
    body = (f'<p class="lead">{tx(tr["elewacje"]["opis"], W)}</p><div class="zakl" role="tablist" aria-label="Elewacje i przekroje">{zak}</div>{pan}')
    return sekcja("elewacje", "Rysunki", tr["elewacje"]["tytul"], "", body, sep)


def model3d(D: dict, tr: dict, W: dict, sep: str) -> str:
    m = D["model"]
    x0, y0, x1, y1 = unary_bounds(m)
    top = D["wsk"]["wysokosc_zabudowy"]["z_top"]
    c = [(x0 + x1) / 2, (y0 + y1) / 2, top / 2]
    R = max(x1 - x0, y1 - y0, top) * 0.75
    ks = [k.id for k in m.kondygnacje]
    from ..sun import sun_position, sun_vector
    az, el = sun_position("2026-06-21 15:00")
    sv = sun_vector(az, el, D["orientacja"]["azymut_osi_y"])
    wid = {"ogrod": dict(poz=[c[0] - 4, y0 - 2.6 * R, 1.7], cel=[c[0], c[1], c[2] * 0.8]),
           "ulica": dict(poz=[c[0] + 3, y1 + 2.4 * R, 1.7], cel=[c[0], c[1], c[2] * 0.8]),
           "lotniczy": dict(poz=[x1 + 1.6 * R, y0 - 1.9 * R, 1.6 * R], cel=c),
           "gora": dict(poz=[c[0], c[1] - 0.01, 3.4 * R], cel=[c[0], c[1], 0])}
    cfg = dict(plik="assets/model.glb", srodek=c, promien=R, slonce=list(sv), widoki=wid, kolejnosc=ks + ["dach"],
               krok=round(max(k.wys_kondygnacji or 3.0 for k in m.kondygnacje) * 0.9, 2), otoczenie=["otoczenie"])
    btn = [("widok", "ogrod", "Ogród"), ("widok", "ulica", "Ulica"), ("widok", "lotniczy", "Z lotu ptaka"),
           ("widok", "gora", "Z góry"), ("przelacz", "rozsun", "Rozsuń kondygnacje"), ("przelacz", "otoczenie", "Otoczenie")]
    ster = "".join(f'<button type="button" data-{a}="{b}" disabled'
                   + (f' aria-pressed="{"true" if b == "otoczenie" else "false"}"' if a == "przelacz" else "")
                   + f'>{E(n)}</button>' for a, b, n in btn)
    t = tr["widok3d"]
    body = (f'<p class="lead">{tx(t["opis"], W)}</p><div class="v3d" id="v3d">'
            f'<div class="v3d-plakat" id="v3d-plakat" style="background-image:url(assets/lotniczy_169.webp)">'
            f'<p>Model 3D (glTF, {E(W.get("glb_mb", ""))} MB) — wczytuje się po kliknięciu.</p>'
            f'<button type="button" class="btn btn-g" id="v3d-start">{E(t["przycisk"])}</button></div>'
            f'<p class="v3d-stan" id="v3d-stan" role="status" aria-live="polite"></p></div>'
            f'<div class="v3d-ster" id="v3d-ster" role="group" aria-label="Sterowanie widokiem 3D">{ster}</div>'
            f'<script type="application/json" id="dane-3d">{json.dumps(cfg)}</script>')
    return sekcja("model-3d", "Interaktywnie", t["tytul"], '<p class="nota">Mysz: obrót, kółko — przybliżenie, prawy '
                  'przycisk — przesunięcie. Dotyk: jeden palec obraca, dwa przybliżają.</p>', body, sep)


def unary_bounds(m):
    from shapely.ops import unary_union
    return unary_union([m.obrys_kondygnacji(k.id) for k in m.kondygnacje]).bounds


def technologia(D: dict, tr: dict, W: dict, sep: str) -> str:
    en = D["en"] or {}
    karty = ""
    for p in D["przegrody"]:
        nz = p["nazwa"].split(":")[0].split("(")[0].strip()
        u = (f'<span class="u">U = {fm(p["U"], 3)}<small> W/(m²·K)</small></span>'
             + (f'<span class="etk">wymaganie ≤ {fm(p["U_max"])}</span>' if p.get("U_max") else "")) if p.get("U") else \
            '<span class="etk">U — nie dotyczy</span>'
        karty += (f'<div class="karta przeg"><div class="przeg-gl"><h3><span class="nr">{E(p["kod"])}</span> {E(nz)}</h3>{u}</div>'
                  f'{SC.przegroda_html(p)}<p class="etk">grubość {fm(p["d"] * 100, 1)} cm</p></div>')
    k, f, g, st = D["konstr"], D["fund"], D["geo"], D["stolarka"]
    ok = [v for v in st.values() if isinstance(v, dict) and str(v.get("wyrob", "")).startswith(("okno", "fix", "HS"))]
    beton = k.get("beton") or {}
    rows = [("Ściany nośne", E(str(k.get("mur", "")))),
            ("Stropy i ściany ŻB", E(str(beton.get("stropy_sciany", "")))),
            ("Elementy wysunięte", E(str(beton.get("krawedzie_wysuniete", ""))) + "; łączniki termoizolacyjne"),
            ("Stal zbrojeniowa", E(str(k.get("stal_zbrojeniowa", "")))),
            ("Fundament", f'płyta fundamentowa — {E(str(beton.get("fundament", "")))}; izolacja obwodowa: '
                          f'{E(str((f.get("izolacja_obwodowa") or {}).get("opis", "")))}' if f.get("typ") == "plyta" else E(str(f.get("typ")))),
            ("Grunt (założenie)", f'{E(str((g.get("grunt") or {}).get("rodzaj", "")))}; kategoria geotechniczna {E(str(g.get("kategoria", "")))}; '
                                  f'{E(str(g.get("uwagi", "")))}'),
            ("Okna i przeszklenia", f'{len(ok)} typów, 3-szybowe; U<sub>w</sub> {fm(en.get("Uw_min"))}–{fm(en.get("Uw_max"))} W/(m²·K) '
                                    f'(moduł fizyki, {en.get("n_okien", 0)} pozycji); ciepły montaż'),
            ("Klasy konstrukcji", f'{E(str(k.get("klasa_konsekwencji", "")))}/{E(str(k.get("klasa_niezawodnosci", "")))}, '
                                  f'okres użytkowania {E(str(k.get("okres_uzytkowania", "")))} lat')]
    tab = "".join(f'<tr><th scope="row">{a}</th><td>{b}</td></tr>' for a, b in rows)
    body = (f'<p class="lead">{tx(tr["technologia"]["lead"], W)}</p><div class="siatka-2">{karty}</div>'
            f'<h3>Konstrukcja i stolarka</h3><div class="tab-wrap"><table>{tab}</table></div>')
    return sekcja("technologia", "Przegrody z U", tr["technologia"]["tytul"],
                  f'<p class="nota">U: {E(en.get("zrodlo", ""))}. Kolory warstw — kolory materiałów w modelu; pasek pod '
                  f'przegrodą — przynależność warstwy do „4 linii”.</p>', body, sep)


def jakosc(D: dict, tr: dict, W: dict, prz_svg: str, sep: str) -> str:
    """4 linie: skład każdej linii zebrany z warstw przegród modelu + wynik kontroli ciągłości modułu fizyki; woda."""
    zb = {k: {} for k in SC.LINIE}
    for p in D["przegrody"]:
        for w in p["warstwy"]:
            if w["linia"] in zb:
                nz = w["nazwa"].split(" (")[0].split(",")[0].split(":")[-1].strip()
                zb[w["linia"]].setdefault(nz, set()).add(w["d"])
    li = ""
    for k, nazwa in SC.LINIE.items():
        el = "; ".join(f'{n} {"/".join(fm(d * 100, 1 if d < 0.01 else 0) for d in sorted(ds))} cm'
                       for n, ds in list(zb[k].items())[:5])
        li += f'<li style="--k:var(--l-{k})"><b>{E(nazwa.capitalize())}</b><p>{E(el)}</p></li>'
    en = D["en"] or {}
    br = en.get("ciaglosc_braki") or {}
    n = en.get("ciaglosc_n", 0)
    kontrola = (f'<p><span class="{"ok" if not br else "uw"}">Kontrola ciągłości (moduł fizyki): {n - len(br)} z {n} '
                f'przegród bez braków.</span> '
                + " ".join(f'Uwaga do weryfikacji: {E(kk)} — {E("; ".join(v))}.' for kk, v in br.items()) + '</p>')
    wd = D["woda"]
    def _grz(d):
        return f' ({d["podgrzewane"]} z grzałką)' if d["podgrzewane"] else ""
    wiersze = "".join(f'<tr><td class="nr">{E(str(d["id"]))}</td><td>{E(str(d["przegroda"]))}</td><td class="l">{fm(d["A"], 1)}</td>'
                      f'<td class="l">{fm(100 * (d["spadek"] or 0), 0)} %</td><td class="l">{d["wpusty"]}{_grz(d)}</td>'
                      f'<td class="l">{d["przelewy"]}</td><td class="l">{d["rury"]}</td></tr>' for d in wd["dachy"])
    dachy = (f'<div class="tab-wrap"><table><thead><tr><th>Pole</th><th>Przegroda</th><th class="l">m²</th><th class="l">Spadek</th>'
             f'<th class="l">Wpusty</th><th class="l">Przelewy awaryjne</th><th class="l">Rury spustowe</th></tr></thead>'
             f'<tbody>{wiersze}</tbody></table></div>')
    teren = (f'<ul class="adapt"><li>Wszystkie rury spustowe prowadzą do szczelnego zbiornika {fm(wd["zbiornik_V"], 1)} m³ '
             f'(woda do podlewania), przelew — do niecki chłonnej {fm_m2(wd["niecka_A"], 0)} o głębokości {fm(wd["niecka_gl"])} m.</li>'
             f'<li>Wokół budynku opaska żwirowa {fm(wd["opaska"])} m, spadek terenu od ścian; {wd["liniowe"]} odwodnienia liniowe '
             f'(progi HS, wejście, brama garażu, wjazd) i {wd["niecki"]} niecki trawiaste.</li>'
             + ('<li>Woda z podjazdu i posadzki garażu przechodzi przez osadnik z separatorem i nie trafia do zbiornika.</li>'
                if wd["separator"] else "")
             + (f'<li>Drenażu opaskowego nie przewidziano: {E(str(wd["grunt"]))} (przyjęte w modelu — do potwierdzenia '
                f'opinią geotechniczną).</li>' if not wd["drenaz"] else "") + '</ul>')
    body = (f'<p class="lead">{tx(tr["jakosc"]["lead"], W)}</p><ul class="linie4">{li}</ul>{kontrola}'
            f'<div class="rys-box">{prz_svg}</div><p class="etk">Przekrój z modelu: izolacja termiczna przecięta w kolorze '
            f'pierwszej linii — ciągła od płyty fundamentowej po attyki.</p>'
            f'<h3>Odprowadzenie wody z dachów</h3>{dachy}<h3>Woda na działce</h3>{teren}')
    return sekcja("jakosc", "Wyróżnik jakości", tr["jakosc"]["tytul"], '<p class="nota">Skład linii zebrany automatycznie '
                  'z warstw przegród modelu (pola „funkcja” warstw i materiałów).</p>', body, sep)


def energia(D: dict, tr: dict, W: dict, sep: str) -> str:
    en, ins = D["en"] or {}, D["inst"]
    if not en:
        return ""
    mx = max(en["EP_max"] * 1.25, en["EP"] * 1.1)
    skala = (f'<div class="skala-ep" role="img" aria-label="EP {fm(en["EP"], 1)} przy wymaganiu {fm(en["EP_max"], 0)} kWh/(m²·rok)">'
             f'<div class="pas" style="width:{100 * en["EP"] / mx:.1f}%"></div><div class="max" style="left:{100 * en["EP_max"] / mx:.1f}%"></div>'
             f'<span style="left:0">EP {fm(en["EP"], 1)}</span><span style="left:{100 * en["EP_max"] / mx:.1f}%">EP<sub>max</sub> {fm(en["EP_max"], 0)}</span></div>')
    kaf = [(fm(en["EP"], 1), "kWh/(m²·rok)", "energia pierwotna EP"),
           (fm(en["EK"], 1), "kWh/(m²·rok)", "energia końcowa EK"), (fm(en["EU"], 1), "kWh/(m²·rok)", "energia użytkowa EU"),
           (fm(en["U_oze"], 0), "%", "udział OZE"), (fm(en["Phi_HL_kW"], 1), "kW", "projektowe obciążenie cieplne"),
           (fm(en["went_m3h"], 0), "m³/h", "strumień wentylacji projektowy"),
           (fm(ins["pc_P"], 1), "kW", f'pompa ciepła A-7/W35, SCOP {fm(ins["pc_SCOP"], 1)}'),
           (fm(100 * (ins["reku_eta"] or 0), 0), "%", f'odzysk ciepła, centrala {fm(ins["reku_V"], 0)} m³/h'),
           (fm(ins["pv_kWp"]), "kWp", f'PV: {ins["pv_n"]} × {ins["pv_Wp"]} Wp, azymut {ins["pv_az"]}°'),
           (fm(ins["cwu_V"], 0), "dm³", "zasobnik c.w.u."), (fm(ins["n50"], 1), "1/h", "szczelność n50 (cel)"),
           (fm(en["A_f"], 1), "m²", "powierzchnia A_f o regulowanej temp.")]
    kafle = "".join(f'<div><span class="w">{E(a)}<small>{E(b)}</small></span><p>{E(c)}</p></div>' for a, b, c in kaf)
    alt = "".join(f'<tr><td>{E(a["nazwa"])}</td><td class="l">{fm(a["EP"], 1)}</td><td class="l">{fm(a["U_oze"], 0)} %</td>'
                  f'<td>{"<span class=ok>spełnia</span>" if a["spelnia"] else "<span class=uw>nie spełnia</span>"}</td></tr>'
                  for a in en["alternatywy"])
    body = (f'<p class="lead">{tx(tr["energia"]["lead"], W)}</p><div class="wsk-ep">{skala}'
            f'<p>Klasa energetyczna: moduł obliczeń jej nie wyznacza, dlatego jej nie podajemy.</p></div>'
            f'<div class="kafle">{kafle}</div><h3>Warianty źródła ciepła (ten sam budynek)</h3>'
            f'<div class="tab-wrap"><table><thead><tr><th>Wariant</th><th class="l">EP</th><th class="l">OZE</th><th>EP ≤ EP<sub>max</sub></th>'
            f'</tr></thead><tbody>{alt}</tbody></table></div>')
    return sekcja("energia", "Charakterystyka energetyczna", tr["energia"]["tytul"],
                  f'<p class="nota">Źródło: {E(en["zrodlo"])}. Dane urządzeń przykładowe („lub równoważne”) — potwierdza PT.</p>',
                  body, sep)


def dzialka(D: dict, tr: dict, W: dict, sep: str) -> str:
    dm, ori = D["dzialka_min"], D["orientacja"]
    nz = {"W": "zachód", "E": "wschód", "S": "południe (ogród)", "N": "północ (droga)"}
    rows = ""
    for k in ("W", "E", "S", "N"):
        q = dm[k]
        pod = "WT § 12 ust. 6 (element wysunięty)" if q["d"] == 1.5 else (
            "linia zabudowy (MPZP); § 12 nie dotyczy granicy z drogą (ust. 10)" if k == "N" else
            f'WT § 12 ust. 1 pkt {"1" if q["d"] == 4.0 else "2"}')
        rows += (f'<tr><td>{nz[k]}</td><td>{E(str(q["el"]))}</td><td class="l">{fm(q["d"])} m</td>'
                 f'<td class="pod">{E(pod)}</td></tr>')
    ref = dm.get("referencyjna") or {}
    body = (f'<p class="lead">{tx(tr["dzialka"]["lead"], W)}</p>'
            f'<div class="tabliczka"><div><span class="etk">Szerokość min.</span><span class="w">{fm(dm["szer"])}<small>m</small></span>'
            f'<span class="p">granice boczne W–E</span></div><div><span class="etk">Głębokość min.</span><span class="w">{fm(dm["gl"])}'
            f'<small>m</small></span><span class="p">od drogi do granicy tylnej</span></div><div><span class="etk">Prostokąt</span>'
            f'<span class="w">{fm(dm["pow"], 0)}<small>m²</small></span><span class="p">bez wymagań MPZP co do powierzchni</span></div>'
            f'<div><span class="etk">Wjazd i wejście</span><span class="w">od {E(DOP.get(ori["droga"] or "N", ""))}</span>'
            f'<span class="p">ogród od {E(DOP.get(ori["najwiecej"], ""))}</span></div></div>'
            f'<div class="rys-box">{SC.dzialka_svg(D)}</div>'
            f'<div class="tab-wrap"><table><thead><tr><th>Strona</th><th>Element decydujący</th><th class="l">Odległość</th>'
            f'<th>Podstawa</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<p><b>Metoda.</b> {E(dm["metoda"])}</p>'
            f'<p>Działka referencyjna w modelu projektu (fikcyjna): {fm(ref.get("szer"))} × {fm(ref.get("gl"))} m, '
            f'{fm_m2(ref.get("pow"), 0)}. Na działce węższej niż minimum zmiana usytuowania wymaga zgody autora i ponownego '
            f'sprawdzenia przepisów przez projektanta adaptującego (np. ściana bez okien może stanąć bliżej granicy).</p>')
    return sekcja("dzialka", "Wymagania działki", tr["dzialka"]["tytul"],
                  f'<p class="nota">Nachylenie dachu {fm(D["wsk"]["kat_dachu"]["wartosc"], 1)}° (spadek dachu płaskiego); '
                  f'przeszklenia wg kierunków: S {fm(ori["przeszklenia"]["S"], 1)}, W {fm(ori["przeszklenia"]["W"], 1)}, '
                  f'E {fm(ori["przeszklenia"]["E"], 1)}, N {fm(ori["przeszklenia"]["N"], 1)} m².</p>', body, sep)


def dokumentacja(D: dict, tr: dict, W: dict, model_dir: Path, sep: str) -> str:
    t, a = tr["dokumentacja"], tr["adaptacja"]
    li = ""
    for c in t["czesci"]:
        n = None
        if c.get("arkusze") and (model_dir / c["arkusze"]).exists():
            n = len((yaml.safe_load((model_dir / c["arkusze"]).read_text(encoding="utf-8")) or {}).get("arkusze") or [])
        li += (f'<li><span class="kod">{E(c["kod"])}</span><b>{E(c["nazwa"])}</b><p>{E(c["opis"])}</p>'
               + (f'<p class="etk">{n} arkuszy rysunkowych w konfiguracji modelu</p>' if n else "") + '</li>')
    ad = "".join(f'<li>{tx(p, W)}</li>' for p in a["punkty"])
    body = (f'<p class="lead">{tx(t["lead"], W)}</p><ul class="tomy">{li}</ul><p>{tx(t["uwaga"], W)}</p>'
            f'<h3 id="adaptacja">{E(a["tytul"])}</h3><ul class="adapt">{ad}</ul><p class="demo">{tx(a["zastrzezenie"], W)}</p>')
    return sekcja("dokumentacja", "Komplet dokumentacji", t["tytul"], '<p class="nota">Liczba arkuszy odczytana z plików '
                  'konfiguracji rysunków modelu (model/arkusze*.yaml).</p>', body, sep)


def pakiety(tr: dict, W: dict, sep: str) -> str:
    t = tr["pakiety"]
    karty = "".join(f'<div class="pakiet{" wyr" if p.get("wyroznij") else ""}"><h3>{E(p["nazwa"])}</h3><p>{E(p["dla"])}</p>'
                    f'<p class="cena num">{E(p["cena"])}<small>cena przykładowa</small></p>'
                    f'<ul>{"".join(f"<li>{E(z)}</li>" for z in p["zawiera"])}</ul>'
                    f'<a class="btn{" btn-g" if p.get("wyroznij") else ""}" href="#zapytanie" data-pakiet="{E(p["nazwa"])}">'
                    f'Zapytaj o pakiet {E(p["nazwa"])}</a></div>' for p in t["lista"])
    op = "".join(f'<tr><td>{E(o["nazwa"])}</td><td class="l">{E(o["cena"])}</td></tr>' for o in t["opcje"])
    body = (f'<p class="baner">{E(t["etykieta"])}</p><div class="pakiety">{karty}</div><h3>{E(t["opcje_tytul"])}</h3>'
            f'<div class="tab-wrap"><table class="opcje"><thead><tr><th>Opcja</th><th class="l">Cena przykładowa</th></tr></thead>'
            f'<tbody>{op}</tbody></table></div>')
    return sekcja("pakiety", "Cennik (przykładowy)", t["tytul"], '<p class="nota">Ceny brutto przykładowe. Strona jest '
                  'demonstracją — nie można tu niczego kupić.</p>', body, sep)


def faq(tr: dict, W: dict, sep: str) -> str:
    t = tr["faq"]
    q = "".join(f'<details class="faq"><summary>{tx(x["p"], W)}</summary><p>{tx(x["o"], W)}</p></details>' for x in t["lista"])
    return sekcja("pytania", "FAQ", t["tytul"], "", f"<div>{q}</div>", sep)


def formularz(tr: dict, W: dict, sep: str) -> str:
    t, mk = tr["formularz"], tr["marka"]
    tem = "".join(f'<option>{E(x)}</option>' for x in t["tematy"])
    pak = "".join(f'<option>{E(p["nazwa"])}</option>' for p in tr["pakiety"]["lista"])

    def pole(id_, lab, inp, pelna=False):
        return (f'<div class="pole{" pelna" if pelna else ""}"><label for="{id_}">{lab}</label>{inp}'
                f'<span class="blad" id="{id_}-blad" aria-live="polite"></span></div>')
    f = (f'<form class="zap" id="form-zap" novalidate>'
         + pole("z-imie", "Imię i nazwisko *", '<input id="z-imie" name="imie" type="text" autocomplete="name" required '
                'aria-describedby="z-imie-blad">')
         + pole("z-email", "E-mail *", '<input id="z-email" name="email" type="email" autocomplete="email" required '
                'aria-describedby="z-email-blad">')
         + pole("z-tel", "Telefon (opcjonalnie)", '<input id="z-tel" name="tel" type="tel" autocomplete="tel" '
                'aria-describedby="z-tel-blad">')
         + pole("z-temat", "Temat *", f'<select id="z-temat" name="temat" required aria-describedby="z-temat-blad">'
                f'<option value="">— wybierz —</option>{tem}</select>')
         + pole("z-pakiet", "Pakiet", f'<select id="z-pakiet" name="pakiet"><option value="">— bez wskazania —</option>{pak}</select>')
         + pole("z-miejsce", "Gmina lub miejscowość działki", '<input id="z-miejsce" name="miejsce" type="text" '
                'autocomplete="address-level2">')
         + pole("z-tresc", "Treść zapytania *", '<textarea id="z-tresc" name="tresc" required maxlength="2000" '
                'aria-describedby="z-tresc-blad"></textarea>', True)
         + f'<div class="pole pelna"><label class="zgoda" for="z-zgoda"><input type="checkbox" id="z-zgoda" name="zgoda" '
           f'aria-describedby="z-zgoda-blad"> <span>{E(t["zgoda"])} *</span></label>'
           f'<span class="blad" id="z-zgoda-blad" aria-live="polite"></span></div>'
         + '<div class="pelna cta"><button class="btn btn-g" type="submit">Wyślij zapytanie</button>'
           '<button class="btn" type="reset">Wyczyść</button></div></form>')
    wynik = ('<div class="wynik" id="wynik" role="status" tabindex="-1" hidden><h3>Zapytanie sprawdzone — nic nie zostało wysłane</h3>'
             '<p>To strona demonstracyjna. Dane pozostały wyłącznie w tej karcie przeglądarki i znikną po jej zamknięciu. '
             'Tak wyglądałoby zapytanie:</p><dl id="wynik-dl"></dl></div>')
    body = (f'<p class="demo"><b>{E(t["demo"])}</b></p>{f}{wynik}'
            f'<p class="adres">{E(t["kontakt"])} <code id="adres-txt">{E(mk["adres_tekst"])}</code>'
            f'<button type="button" data-kopiuj="adres-txt">Kopiuj adres</button></p>')
    return sekcja("zapytanie", "Formularz — demonstracja", t["tytul"], '<p class="nota">Pola z gwiazdką są wymagane. '
                  'Formularz nie zbiera danych płatniczych ani haseł.</p>', body, sep)


def stopka(D: dict, tr: dict, W: dict, sep_svg: str, teraz: datetime) -> str:
    mk, st = tr["marka"], tr["stopka"]
    meta = D["meta"]
    li = "".join(f"<li>{tx(x, W)}</li>" for x in st["zastrzezenia"])
    return (f'<footer class="stopka"><div class="wrap"><div>{sep_svg}<b>{E(mk["nazwa"])}</b><p>{E(mk["podtytul"])} · '
            f'{E(mk["oznaczenie"])}</p><p class="mono">Wygenerowano {teraz.strftime("%d.%m.%Y %H:%M")} skryptem '
            f'tools/buduj_www.py z modelu „{E(str(meta.get("nazwa", "")))}” w wersji {E(str(meta.get("wersja", "")))} '
            f'({E(str(meta.get("data", "")))}).</p></div><ul>{li}</ul></div></footer>')


def zloz(D: dict, tr: dict, R: dict, szkic: dict, glb_mb: float, model_dir: Path, teraz: datetime) -> str:
    """Pełna treść index.html (bez szkieletu dokumentu)."""
    W = wartosci(D, tr, teraz)
    W["glb_mb"] = fm(glb_mb, 1)
    css = (STATIC / "strona.css").read_text(encoding="utf-8")
    js = (STATIC / "strona.js").read_text(encoding="utf-8")
    js3 = (STATIC / "widok3d.js").read_text(encoding="utf-8")
    sep = SC.separator_svg(D["model"])
    arkusze = model_dir / "arkusze.yaml"
    secs = EL.przekroje_def(D["model"], arkusze)
    top = max(p.z1 for p in D["ir"].prisms if p.meta.get("group") not in ("otoczenie", "teren") and p.kind != "terrain")
    prz = EL.przekroj(D, secs[0], (-1.4, top + 1.1)).replace(f'id="prz-{secs[0].get("id")}"', 'id="prz-linie"') if secs else ""
    czesci = [glowa(D, tr, css, W), naglowek(tr, W), '<main id="tresc">', hero(D, tr, W, R, sep), parametry(D, tr, W, sep),
              idea(D, tr, W, szkic, sep), galeria(D, tr, W, R, sep), rzuty_sekcja(D, tr, W, sep),
              elewacje_sekcja(D, tr, W, arkusze, sep), model3d(D, tr, W, sep), technologia(D, tr, W, sep),
              jakosc(D, tr, W, prz, sep), energia(D, tr, W, sep), dzialka(D, tr, W, sep),
              dokumentacja(D, tr, W, model_dir, sep), pakiety(tr, W, sep), faq(tr, W, sep), formularz(tr, W, sep),
              '</main>', stopka(D, tr, W, sep, teraz)]
    czesci += [f'<script src="{u}"></script>' for u in CDN]
    czesci += [f"<script>\n{js}\n</script>", f"<script>\n{js3}\n</script>"]
    return "\n".join(czesci) + "\n", W
