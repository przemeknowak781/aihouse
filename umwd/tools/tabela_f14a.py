#!/usr/bin/env python3
"""F.14.A – „Wstępna informacja o szacowanych kosztach realizacji Inwestycji oraz kosztach wykonania Przedmiotu usługi”
(Etap I, Opracowanie studialne; Reg. R.V ust. 2 pkt 3 lit. d – brak informacji = brak oceny Opracowania, R-076).

Uruchomienie (z katalogu umwd/; idempotentne – każde uruchomienie nadpisuje te same pliki):
    /home/user/aihouse/.venv-render/bin/python -I tools/tabela_f14a.py             # xlsx + PDF + kontrola LibreOffice
    /home/user/aihouse/.venv-render/bin/python -I tools/tabela_f14a.py --bez-pdf   # tylko xlsx
    /home/user/aihouse/.venv-render/bin/python -I tools/tabela_f14a.py --json      # dodatkowo wydruk grup (JSON) na stdout

Wynik (wyłącznie): build/tabele/F.14.A.xlsx – wzór Organizatora „F.14.A_Informacja o kosztach - ETAP I.xlsx” bez zmian
                   układu (wiersze, kolumny, scalenia, formuły sum F28/H28); wypełnione: Ilość, Wartość netto, VAT, brutto
                   (=ROUND(F*(1+G);2)), koszt usługi netto/brutto (H32/H33 – błąd wzoru `=F28`/`=H28` nadpisany wartością
                   i formułą, formularze_tabele.md 2.3 pkt 1); kolumna pomocnicza J (skład grupy) poza obszarem wydruku;
                   metadane wyczyszczone (R-082), brak numeru identyfikacyjnego i danych autora.
                   build/tabele/F.14.A.pdf  – A4 pionowo (format wzoru), HTML → tools/plansze/html2pdf.js (Chromium);
                   awaryjnie LibreOffice; metadane PDF neutralne (tylko /Title).

Źródła (tylko odczyt, żadnych liczb projektu wpisanych na stałe):
    model/koncepcja.json                              – bilans (koszt_mln_netto, koszt_roboty_KS_mln, rezerwa_*), wersja
    docs/20_koncepcja/_rewizja_koszt_wejscie_v1_N.json – wejście modelu kosztów (najnowsze N; = bilans.koszt_wejscie_modelu)
    tools/koszty_model.py                             – stawki mid (II kw. 2026, netto), KS i rezerwa
    docs/20_koncepcja/_v12_koszt.py → _rewizja_koszt.py – pozycje spoza modelu (POZA_F); skrypty wykonywane w piaskownicy:
                                                        każde otwarcie pliku do zapisu jest przechwytywane (nic nie jest
                                                        zapisywane), bez plików .pyc
    docs/20_koncepcja/koncepcja_wybrana.md            – koszt Dokumentacji („Koszt Dokumentacji ≈ X mln zł netto”)
    00_materialy/_rozpak/4.Zalaczniki_Formalne_F.03-F.16_edytowalne/F.14.A_… .xlsx – wzór
Metoda: roboty = pozycje modelu (mid) + pozycje spoza modelu; koszty stałe budowy = KS × roboty; rezerwa na nieprzewidziane
= REZ × (roboty + KS) – tak jak w _rewizja_koszt.total() i koncepcja.json["bilans"]. Wartości grup zaokrąglone do 1 000 zł
(etap studialny – wartości szacunkowe). Kontrole: suma w mln zł z 2 miejscami po przecinku = bilans.koszt_mln_netto
(ta sama kwota, którą podaje opis), tak samo roboty + KS = bilans.koszt_roboty_KS_mln i rezerwa = bilans.rezerwa_mln;
suma ≤ 150 mln zł netto; koszt usługi ≤ 5,4 % planowanego kosztu realizacji (R-051). Gdy kontrola zgodności z bilansem nie
przechodzi (np. skrypty kosztów zmienione, a koncepcja.json jeszcze nie), pliki NIE są nadpisywane (kod 1) – chyba że --wymus.
Pozycje spoza modelu o wartości 0 zł (np. szyb C1 – usunięty w v1.2) nie są wymieniane w kolumnie J.
Podział na 20 grup wzoru F.14.A: grupy 1–16 jak w modelu F.14.B; 17 – woda szara i odzysk ciepła z wody szarej;
18 – system bezemisyjny (gruntowe pompy ciepła z polem sond, ścianami i palami energetycznymi, PV dachowe, BIPV);
19 – magazyny energii (elektrycznej, bufory ciepła); 20 – MDS/budowla ochronna, stackery, zapora, zamurowanie okien
Maz. 19, rezerwa na nieprzewidziane. Każda pozycja modelu trafia do dokładnie jednej grupy (bez podwójnego liczenia).
Kody wyjścia: 0 OK · 1 błąd danych/kontroli (np. suma ≠ bilans) · 2 błąd zapisu/renderu.
"""
from __future__ import annotations

import argparse
import builtins
import html
import importlib.util
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from contextlib import redirect_stdout
from copy import copy
from pathlib import Path

sys.dont_write_bytecode = True          # skrypty koncepcji ładowane tylko do odczytu – bez __pycache__

import openpyxl  # noqa: E402
from openpyxl.styles import Alignment, Font  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
KONC_DIR = ROOT / "docs" / "20_koncepcja"
TPL = ROOT / "00_materialy" / "_rozpak" / "4.Zalaczniki_Formalne_F.03-F.16_edytowalne" / "F.14.A_Informacja o kosztach - ETAP I.xlsx"
OUT = ROOT / "build" / "tabele"
HTML2PDF = ROOT / "tools" / "plansze" / "html2pdf.js"
P_KON = ROOT / "model" / "koncepcja.json"
P_KMD = KONC_DIR / "koncepcja_wybrana.md"
P_KM = ROOT / "tools" / "koszty_model.py"

# ---- stałe regulaminowe i metodyczne (nie są danymi projektu)
LIMIT_KOSZTU = 150e6            # Reg. R.III ust. 3 pkt 1; Wyj. 20 odp. 74 – nieprzekraczalny limit netto (R-049, R-222)
LIMIT_USLUGI_PROC = 0.054       # Reg. R.III ust. 4 – koszt usługi ≤ 5,4 % planowanego kosztu realizacji netto (R-051)
VAT = 0.23                      # stawka podstawowa; wzór F.14.A nie podaje stawek – przyjęto 23 % dla wszystkich grup
ZAOKR = 1000.0                  # zaokrąglenie wartości grup (etap studialny)
TOL_MLN = 0.005                 # zgodność z koncepcja.json["bilans"] [mln zł] – kwota w mln zł z 2 miejscami jak w bilansie
NBSP = " "

GRUPY = {  # nr wzoru → krótki opis składu (kolumna pomocnicza J i PDF nie zmieniają nazw wzoru)
    1: "obudowa wykopu (ściany szczelinowe, iniekcja strumieniowa przy Maz. 19), wykop, odwodnienie, archeologia, monitoring sąsiadów",
    2: "przyłącza i sieci zewnętrzne (bez źródeł OZE – gr. 18)",
    3: "konstrukcja żelbetowa, podziemie, pale, rampy, stropodachy, taras zielony segmentu",
    4: "okna, drzwi zewnętrzne, fasady słupowo-ryglowe",
    5: "drzwi wewnętrzne, przeciwpożarowe, okna wewnętrzne",
    6: "granit, ceramika, tynk dziedzińcowy, lamele korony, ościeża (bez BIPV – gr. 18)",
    7: "woda, kanalizacja, c.o., wentylacja z odzyskiem, chłód (TABS), rozdział ciepła z pomp ciepła, dry-cooler",
    8: "instalacje elektryczne, serwerownia, BMS/EMS, agregat HVO, UPS (bez magazynu energii – gr. 19)",
    9: "teletechnika, SSP/DSO, AV sali obrad i konferencji, ochrona klatek i przedsionków przed zadymieniem",
    10: "dźwigi osobowe (w tym ratowniczy) i osobowo-towarowy",
    11: "ścianki, okładziny, malowanie, wyposażenie stałe, sala Sejmiku, lapidarium",
    12: "sufity (biura z odsłoniętym stropem TABS i wyspami akustycznymi)",
    13: "posadzki i podłogi",
    14: "balustrady i pochwyty",
    15: "nawierzchnie, zieleń, drzewa, mała architektura, oświetlenie, retencja, punkty ładowania EV",
    16: "koszty stałe budowy od wszystkich robót",
    17: "woda szara (podczyszczanie) i odzysk ciepła z wody szarej",
    18: "gruntowe pompy ciepła z polem sond, ścianami i palami energetycznymi; fotowoltaika dachowa i BIPV",
    19: "magazyn energii elektrycznej i bufory ciepła",
    20: "MDS i budowla ochronna, stackery, zapora przeciwpowodziowa, zamurowanie okien Maz. 19, rezerwa na nieprzewidziane",
}
POZA_GRUPY = [  # pozycje spoza modelu (opis z _rewizja_koszt.py / _v12_koszt.py) → grupa F.14.A; pierwsze trafienie
    (r"budowla ochronna|ukrycie", 20), (r"szyb wyjścia zapasowego|MDS", 20), (r"stacker", 20),
    (r"zapora przeciwpowodziowa", 20), (r"lapidarium", 11), (r"ścianki szklane|SZKLO", 11), (r"TABS|sufit", 12),
    (r"^GPC", 18), (r"dry-cooler", 7), (r"agregat", 8), (r"ościeża", 6), (r"iniekcja|ściany szczelinowej", 1),
    (r"pale|uskok|rampy|trzon|klatki", 3), (r"szyb C1", 10), (r"ogródków|ścieżki ogrodu|pas od bulwaru|drzew", 15),
]


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def pl(x, nd=2):
    s = f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", NBSP)
    return s


def load_module(path, name, ro_open=None):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    if ro_open is not None:
        mod.open = ro_open                    # globalne `open` modułu – zapis przechwycony
    sys.modules[name] = mod
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


# ================================================================================================ dane kosztowe
def cost_input_file(kon):
    ref = kon.get("bilans", {}).get("koszt_wejscie_modelu")
    cands = sorted(KONC_DIR.glob("_rewizja_koszt_wejscie_v1_*.json"),
                   key=lambda p: [int(x) for x in re.findall(r"\d+", p.stem.split("wejscie_")[-1])])
    latest = cands[-1] if cands else None
    if ref and (ROOT / ref).exists() and latest and (ROOT / ref).resolve() != latest.resolve():
        log(f"UWAGA: bilans.koszt_wejscie_modelu = {ref}, a najnowsze wejście to {latest.relative_to(ROOT)} – użyto najnowszego")
    if latest is None:
        raise SystemExit("brak docs/20_koncepcja/_rewizja_koszt_wejscie_v1_*.json")
    return latest


def poza_modelem(params):
    """Pozycje spoza modelu z _v12_koszt.py (POZA_F) – w piaskownicy. Zwraca (dict opis → zł, info, P_skryptu) albo (None, …)."""
    blocked = []

    def ro_open(file, mode="r", *a, **k):
        if any(c in mode for c in "wax+"):
            blocked.append(str(file))
            return io.BytesIO() if "b" in mode else io.StringIO()
        return builtins.open(file, mode, *a, **k)

    sys.path.insert(0, str(KONC_DIR))
    try:
        load_module(KONC_DIR / "_rewizja_koszt.py", "_rewizja_koszt", ro_open)
        v12 = load_module(KONC_DIR / "_v12_koszt.py", "_v12_koszt", ro_open)
        poza = {k: float(v[0]) for k, v in v12.POZA_F.items()}
        p_skr = dict(v12.P_sel)
        diff = [k for k in set(params) | set(p_skr) if abs(float(params.get(k, 0)) - float(p_skr.get(k, 0))) > 1e-9]
        info = (f"pozycje spoza modelu: docs/20_koncepcja/_v12_koszt.py (POZA_F, {len(poza)} poz.); próby zapisu przechwycone: "
                f"{len(blocked)}; parametry skryptu = plik wejścia: {'TAK' if not diff else 'NIE (' + ', '.join(sorted(diff)) + ')'}")
        return poza, info, diff
    except Exception as e:  # noqa: BLE001
        return None, f"pozycje spoza modelu niedostępne ze skryptu ({type(e).__name__}: {e}) – ujęte zbiorczo z bilansu", None
    finally:
        sys.path.remove(str(KONC_DIR))


def grupa_modelu(lp):
    lp = str(lp)
    if lp in ("2.12a", "2.12b", "2.13", "6.5*"):
        return 18
    if lp in ("7.9", "8.17"):
        return 19
    if lp.startswith("17."):
        return 17
    if lp.startswith("18."):
        return 20
    return int(lp.split(".")[0])


def grupa_poza(opis):
    for rx, g in POZA_GRUPY:
        if re.search(rx, opis, re.I):
            return g, True
    return 20, False


def krotko(opis, n=70):
    s = re.sub(r"^dźwignia v1\.2 \w+:\s*", "", opis)
    m = re.search(r" \(|: | = ", s[12:])
    s = s[: 12 + m.start()] if m else s
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"


def koszt_dokumentacji(text):
    m = re.search(r"Koszt Dokumentacji\s*≈?\s*([\d\s,]+)\s*mln", text)
    return float(m.group(1).replace(" ", "").replace(",", ".")) * 1e6 if m else None


def compute():
    kon = json.loads(P_KON.read_text(encoding="utf-8"))
    bil = kon["bilans"]
    f_in = cost_input_file(kon)
    params = json.loads(f_in.read_text(encoding="utf-8"))
    km = load_module(P_KM, "koszty_model")
    q = dict(km.REF)
    q.update(params)
    r = km.compute(q, "mid")
    ks_rate, rez_rate = km.KS[1], km.REZ[1]
    rows = [x for x in r["rows"] if not str(x[0]).startswith(("16.", "18.3"))]
    works_model = sum(x[5] for x in rows)
    poza, info_poza, pdiff = poza_modelem(params)
    issues = []
    if pdiff:
        issues.append("parametry skryptu _v12_koszt.py różnią się od pliku wejścia: " + ", ".join(sorted(pdiff)))
    if poza is None:
        ex_total = bil["koszt_roboty_KS_mln"] * 1e6 / (1 + ks_rate) - works_model
        poza = {"pozycje spoza modelu kosztów – zbiorczo (z bilansu koncepcji)": ex_total}
        issues.append(info_poza)
    groups = {g: dict(v=0.0, model=[], poza=[]) for g in range(1, 21)}
    for lp, opis, jm, ilosc, cena, wart in rows:
        g = grupa_modelu(lp)
        groups[g]["v"] += wart
        groups[g]["model"].append(str(lp))
    unmapped = []
    for opis, v in poza.items():
        if abs(v) < 1e-6:                       # pozycja zerowa (np. szyb C1 usunięty w v1.2) – nie wymieniać w składzie grupy
            continue
        g, ok = grupa_poza(opis)
        if not ok:
            unmapped.append(opis[:60])
        groups[g]["v"] += v
        groups[g]["poza"].append(krotko(opis))
    if unmapped:
        issues.append("pozycje spoza modelu bez reguły grupy (→ gr. 20): " + "; ".join(unmapped))
    works = works_model + sum(poza.values())
    ks = works * ks_rate
    rez = (works + ks) * rez_rate
    groups[16]["v"] += ks
    groups[16]["model"].append(f"16.1 ({ks_rate:.0%} robót)")
    groups[20]["v"] += rez
    groups[20]["model"].append(f"18.3* rezerwa {rez_rate:.0%}")
    total_exact = works + ks + rez
    # zaokrąglenie grup do ZAOKR metodą największych reszt – suma grup = zaokrąglona suma dokładna (bez narastania błędu)
    target = round(total_exact / ZAOKR)
    base = {g: int(v["v"] // ZAOKR) for g, v in groups.items()}
    rest = sorted(groups, key=lambda g: groups[g]["v"] / ZAOKR - base[g], reverse=True)
    for g in rest[: max(0, target - sum(base.values()))]:
        base[g] += 1
    for g, v in groups.items():
        v["F"] = base[g] * ZAOKR
        v["H"] = round(v["F"] * (1 + VAT), 2)
    totF = round(sum(g["F"] for g in groups.values()), 2)
    totH = round(sum(g["H"] for g in groups.values()), 2)
    fee = koszt_dokumentacji(P_KMD.read_text(encoding="utf-8")) if P_KMD.exists() else None
    def zgodne(x_zl, b_mln):                    # kwota widoczna w mln zł (2 miejsca) = wartość bilansu (to, co podaje opis)
        return round(x_zl / 1e6, 2) == round(b_mln, 2) and abs(x_zl / 1e6 - b_mln) <= TOL_MLN

    checks = [
        ("suma = bilans.koszt_mln_netto (mln zł, 2 miejsca)", zgodne(totF, bil["koszt_mln_netto"]),
         f"{totF / 1e6:.4f} → {round(totF / 1e6, 2):.2f} vs {bil['koszt_mln_netto']}"),
        ("roboty + KS = bilans.koszt_roboty_KS_mln", zgodne(works + ks, bil["koszt_roboty_KS_mln"]),
         f"{(works + ks) / 1e6:.4f} vs {bil['koszt_roboty_KS_mln']}"),
        ("rezerwa = bilans.rezerwa_mln", zgodne(rez, bil["rezerwa_mln"]), f"{rez / 1e6:.4f} vs {bil['rezerwa_mln']}"),
        ("stawka rezerwy = bilans.rezerwa_proc", abs(rez_rate * 100 - bil["rezerwa_proc"]) < 1e-9, f"{rez_rate:.2%} vs {bil['rezerwa_proc']} %"),
        ("suma ≤ limit 150 mln zł netto", totF <= LIMIT_KOSZTU, f"zapas {(LIMIT_KOSZTU - totF) / 1e6:.2f} mln"),
        ("koszt usługi podany", fee is not None, "koncepcja_wybrana.md" if fee else "brak"),
        ("koszt usługi ≤ 5,4 % planowanego kosztu realizacji (R-051)",
         fee is not None and fee <= LIMIT_USLUGI_PROC * min(totF, LIMIT_KOSZTU) + 0.005,
         f"{(fee or 0) / 1e6:.2f} ≤ {LIMIT_USLUGI_PROC * min(totF, LIMIT_KOSZTU) / 1e6:.2f} mln"),
    ]
    zgodnosc = all(ok for n, ok, _ in checks[:3])
    return dict(kon=kon, bil=bil, f_in=f_in, groups=groups, works_model=works_model, poza=poza, works=works, ks=ks, rez=rez,
                total_exact=total_exact, totF=totF, totH=totH, fee=fee, fee_b=round(fee * (1 + VAT), 2) if fee else None,
                checks=checks, zgodnosc=zgodnosc, issues=issues, info=[f"wejście modelu: {f_in.relative_to(ROOT)}", info_poza],
                ks_rate=ks_rate, rez_rate=rez_rate)


# ================================================================================================ xlsx
CORE_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.'
            'org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/'
            'terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>'
            '{t}</dc:title></cp:coreProperties>')
APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/'
           'officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           '<Application>Microsoft Excel</Application><DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><LinksUpToDate>false'
           '</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged></Properties>')


def save_clean(wb, path, title):
    """Zapis bez metadanych (R-082, R-127): core.xml tylko z tytułem, app.xml bez Company/Manager, bez custom.xml,
    stałe znaczniki czasu w ZIP (wynik powtarzalny)."""
    pr = wb.properties
    for a in ("creator", "lastModifiedBy", "title", "subject", "description", "keywords", "category", "contentStatus",
              "identifier", "language", "version", "revision"):
        try:
            setattr(pr, a, None)
        except Exception:  # noqa: BLE001
            pass
    pr.lastPrinted = None
    wb.calculation.fullCalcOnLoad = True
    tmp = path.with_suffix(".tmp.xlsx")
    wb.save(tmp)
    with zipfile.ZipFile(tmp) as zin, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename == "docProps/custom.xml":
                continue
            if info.filename == "docProps/core.xml":
                data = CORE_XML.format(t=html.escape(title)).encode("utf-8")
            elif info.filename == "docProps/app.xml":
                data = APP_XML.encode("utf-8")
            elif info.filename in ("[Content_Types].xml", "_rels/.rels"):
                data = re.sub(rb"<(Override|Relationship)[^>]*custom\.xml[^>]*/>", b"", data)
            zi = zipfile.ZipInfo(info.filename, date_time=(1980, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)
    tmp.unlink()


def scan_template(ws):
    """Wiersze wzoru: grupy 1–20 (B = numer), wiersz „….*”, suma, UWAGA, koszt usługi netto/brutto."""
    rows = {"grupy": {}}
    for rr in range(7, ws.max_row + 1):
        b = ws.cell(rr, 2).value
        sb = str(b).strip() if b is not None else ""
        if re.fullmatch(r"\d+", sb):
            rows["grupy"][int(sb)] = rr
        elif sb.startswith("…") or sb.startswith("...."):
            rows["inne"] = rr
        elif sb.startswith("Szacunkowy koszt realizacji"):
            rows["suma"] = rr
        elif sb.startswith("UWAGA"):
            rows["uwaga"] = rr
        elif "NETTO wykonania" in sb:
            rows["fee_n"] = rr
        elif "BRUTTO wykonania" in sb:
            rows["fee_b"] = rr
    need = ["inne", "suma", "uwaga", "fee_n", "fee_b"]
    if sorted(rows["grupy"]) != list(range(1, 21)) or any(k not in rows for k in need):
        raise SystemExit(f"nieoczekiwany układ wzoru F.14.A: {rows}")
    return rows


ZALOZENIA_PDF = ("Założenia: wartości szacunkowe netto, poziom cen II kw. 2026 (Wrocław), bez waloryzacji; VAT 23 % (wzór nie podaje "
                 "stawek); grupy zaokrąglone do 1 000 zł; koszty stałe budowy – gr. 16; rezerwa na nieprzewidziane – gr. 20.")
ZALOZENIA = ZALOZENIA_PDF[:-1] + "; skład grup – kolumna pomocnicza J (poza wydrukiem)."



def build_xlsx(R):
    wb = openpyxl.load_workbook(TPL)
    ws = wb.active
    T = scan_template(ws)
    hdr = [str(ws["B2"].value or "").strip(), str(ws["B3"].value or "").strip(), str(ws["B4"].value or "").strip()]
    fmt_zl = ws.cell(T["suma"], 6).number_format
    for g, rr in T["grupy"].items():
        G = R["groups"][g]
        if not ws.cell(rr, 5).value:                      # wzór bez j.m. w gr. 18–19 → „kpl” jak w pozostałych grupach
            ws.cell(rr, 5).value = "kpl"
            ws.cell(rr, 5)._style = copy(ws.cell(T["grupy"][1], 5)._style)
            ws.cell(rr, 4)._style = copy(ws.cell(T["grupy"][1], 4)._style)
        ws.cell(rr, 4).value = 1                          # j.m. „kpl” → ilość 1
        ws.cell(rr, 6).value = G["F"]
        ws.cell(rr, 7).value = VAT
        ws.cell(rr, 7).number_format = "0%"
        ws.cell(rr, 8).value = f"=ROUND(F{rr}*(1+G{rr}),2)"
        for c in (6, 8):
            ws.cell(rr, c).number_format = fmt_zl
        parts = [GRUPY[g]]
        if G["model"]:
            parts.append("model: " + ", ".join(G["model"]))
        if G["poza"]:
            parts.append("spoza modelu: " + "; ".join(G["poza"]))
        ws.cell(rr, 10).value = " | ".join(parts)
        ws.cell(rr, 10).alignment = Alignment(wrap_text=False, vertical="center")
    # sumy – formuły wzoru (F28 =SUM(F7:F26), H28 =SUM(H7:H26)) pozostają; wiersz „….*” pusty (brak pozycji dodatkowych)
    assert str(ws.cell(T["suma"], 6).value).startswith("=SUM"), "wzór: brak formuły sumy"
    # założenia – wiersz pusty pod UWAGA (wiersz 30 wzoru), scalony B:H jak UWAGA
    rz = T["uwaga"] + 1
    ws.merge_cells(start_row=rz, start_column=2, end_row=rz, end_column=8)
    c = ws.cell(rz, 2)
    c.value = ZALOZENIA
    c.font = Font(name="Calibri", sz=9, i=True)
    c.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
    ws.row_dimensions[rz].height = 38
    # koszt usługi – nadpisanie błędu wzoru (H32 `=F28`, H33 `=H28`)
    ws.cell(T["fee_n"], 8).value = round(R["fee"], 2) if R["fee"] is not None else None
    ws.cell(T["fee_b"], 8).value = f"=ROUND(H{T['fee_n']}*(1+{VAT}),2)" if R["fee"] is not None else None
    # kolumna pomocnicza J (szerokość ustawiona we wzorze, pusta) – nagłówek w stylu wzoru, poza obszarem wydruku
    ws.cell(6, 10)._style = copy(ws.cell(6, 8)._style)
    ws.cell(6, 10).value = "Skład grupy (pomocniczo, poza wydrukiem)"
    ws.column_dimensions["J"].width = 110
    ws.print_area = f"A1:H{T['fee_b']}"
    path = OUT / "F.14.A.xlsx"
    save_clean(wb, path, "F.14.A Wstępna informacja o kosztach")
    checks = {f"F{T['suma']}": R["totF"], f"H{T['suma']}": R["totH"]}
    if R["fee"] is not None:
        checks[f"H{T['fee_n']}"] = round(R["fee"], 2)
        checks[f"H{T['fee_b']}"] = R["fee_b"]
    names = {g: re.sub(r"\s+", " ", str(ws.cell(rr, 3).value or "")).strip() for g, rr in T["grupy"].items()}
    jm = {g: (ws.cell(rr, 5).value or "") for g, rr in T["grupy"].items()}
    texts = dict(suma=str(ws.cell(T["suma"], 2).value), uwaga=str(ws.cell(T["uwaga"], 2).value), inne=(
        str(ws.cell(T["inne"], 2).value), str(ws.cell(T["inne"], 3).value)), fee_n=str(ws.cell(T["fee_n"], 2).value),
        fee_b=str(ws.cell(T["fee_b"], 2).value), head=[str(ws.cell(6, c).value or "").strip() for c in range(2, 9)])
    return dict(path=path, hdr=hdr, checks=checks, names=names, jm=jm, texts=texts, rows=T)


def lo_verify(x):
    """Przeliczenie xlsx w LibreOffice i porównanie wyników formuł z wartościami z Pythona."""
    if not shutil.which("soffice"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        prof = f"-env:UserInstallation=file://{Path(tmp) / 'lo_profile'}"
        subprocess.run(["soffice", prof, "--headless", "--norestore", "--convert-to", "xlsx", "--outdir", str(Path(tmp) / "lo"),
                        str(x["path"])], capture_output=True, text=True, timeout=600)
        q = Path(tmp) / "lo" / x["path"].name
        if not q.exists():
            return [("LibreOffice", None, None, False)]
        ws = openpyxl.load_workbook(q, data_only=True).active
        out = []
        for ref, exp in x["checks"].items():
            got = ws[ref].value
            out.append((ref, exp, got, isinstance(got, (int, float)) and abs(got - exp) < 0.015))
        return out


# ================================================================================================ PDF (A4 pionowo)
CSS = """
@page { size: 210mm 297mm; margin: 0 }
* { box-sizing: border-box }
html, body { margin: 0; padding: 0; background: #fff; color: #000; font-family: Carlito, Calibri, 'Liberation Sans', sans-serif }
.page { width: 210mm; height: 297mm; padding: 11mm 12mm 8mm 12mm; position: relative }
.hdr { text-align: center; margin-bottom: 4mm }
.hdr .k { font-size: 9.5pt; line-height: 1.3; margin-bottom: 2.5mm }
.hdr .t { font-size: 14pt; font-weight: 700; line-height: 1.25; border: 0.5mm solid #000; padding: 1.8mm 3mm }
.hdr .z { font-size: 10.5pt; font-weight: 700; text-align: right; margin-top: 1.5mm }
table { border-collapse: collapse; table-layout: fixed; width: 186mm; font-size: 11pt; line-height: 1.22 }
td, th { border: 0.2mm solid #222; padding: 0.8mm 1.3mm; vertical-align: middle }
th { background: #B4C7E7; font-weight: 700; text-align: center }
td.lp { text-align: center; font-weight: 700 }
td.r { text-align: right; white-space: nowrap }
td.c { text-align: center }
tr.inne td { font-size: 10pt; color: #333 }
tr.suma td { background: #BFBFBF; font-weight: 700 }
tr.uwaga td, tr.zal td { border: none; font-size: 9.5pt; padding-top: 2mm; line-height: 1.3 }
tr.zal td { font-style: italic; color: #333; padding-top: 0.5mm }
tr.gap td { border: none; height: 4mm }
tr.fee td { background: #B4C7E7; font-weight: 700; font-size: 11pt; border: 0.4mm solid #000 }
tr.fee td.lab { text-align: center }
"""
COLS = [("L.p.", 10), ("Opis", 80), ("Ilość", 11), ("J.m.", 10), ("Wartość [netto]", 31), ("VAT", 12), ("Wartość [brutto]", 32)]


def zl(x):
    return f"{pl(x, 2)}{NBSP}zł"


def render_html(R, X):
    e = html.escape
    hdr = X["hdr"]
    p = ['<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>F.14.A</title><style>', CSS, "</style></head><body>",
         '<section class="page"><div class="hdr">',
         f'<div class="k">{e(hdr[0]).replace(chr(10), "<br>")}</div>',
         f'<div class="t">{e(hdr[1]).replace(chr(10), "<br>")}</div>',
         f'<div class="z">{e(hdr[2])}</div></div>',
         "<table><colgroup>" + "".join(f'<col style="width:{w}mm">' for _, w in COLS) + "</colgroup>",
         "<thead><tr>" + "".join(f"<th>{e(h)}</th>" for h in X["texts"]["head"]) + "</tr></thead><tbody>"]
    for g in range(1, 21):
        G = R["groups"][g]
        jm = X["jm"][g]
        p.append(f'<tr><td class="lp">{g}</td><td>{e(X["names"][g])}</td><td class="c">1</td>'
                 f'<td class="c">{e(jm or "kpl")}</td><td class="r">{zl(G["F"])}</td><td class="c">{int(round(VAT * 100))}{NBSP}%</td>'
                 f'<td class="r">{zl(G["H"])}</td></tr>')
    a, b = X["texts"]["inne"]
    p.append(f'<tr class="inne"><td class="lp">{e(a)}</td><td>{e(b)}</td><td></td><td></td><td></td><td></td><td></td></tr>')
    p.append(f'<tr class="suma"><td colspan="2">{e(re.sub(r"[ ]+", " ", X["texts"]["suma"]))}</td><td></td><td class="c">kpl</td>'
             f'<td class="r">{zl(R["totF"])}</td><td></td><td class="r">{zl(R["totH"])}</td></tr>')
    uw = e(X["texts"]["uwaga"]).replace("\n\n", "<br>").replace("\n", "<br>")
    p.append(f'<tr class="uwaga"><td colspan="7">{uw}</td></tr>')
    p.append(f'<tr class="zal"><td colspan="7">{e(ZALOZENIA_PDF)}</td></tr>')
    p.append('<tr class="gap"><td colspan="7"></td></tr>')
    fee_n = zl(R["fee"]) if R["fee"] is not None else "–"
    fee_b = zl(R["fee_b"]) if R["fee_b"] is not None else "–"
    p.append(f'<tr class="fee"><td class="lab" colspan="6">{e(X["texts"]["fee_n"])}</td><td class="r">{fee_n}</td></tr>')
    p.append(f'<tr class="fee"><td class="lab" colspan="6">{e(X["texts"]["fee_b"])}</td><td class="r">{fee_b}</td></tr>')
    p.append("</tbody></table></section></body></html>")
    return "".join(p)


def neutral_pdf(src, dst, title):
    from pypdf import PdfReader, PdfWriter
    w = PdfWriter(clone_from=PdfReader(str(src)))
    w.metadata = None
    w.add_metadata({"/Title": title})
    try:
        w.xmp_metadata = None
    except Exception:  # noqa: BLE001
        pass
    root = w._root_object
    for k in ("/Metadata", "/PieceInfo"):
        if k in root:
            del root[k]
    with open(dst, "wb") as fh:
        w.write(fh)


def build_pdf(R, X):
    pdf = OUT / "F.14.A.pdf"
    with tempfile.TemporaryDirectory() as tmp:
        hp = Path(tmp) / "F.14.A.html"
        hp.write_text(render_html(R, X), encoding="utf-8")
        raw = Path(tmp) / "raw.pdf"
        how = None
        if shutil.which("node") and HTML2PDF.exists():
            p = subprocess.run(["node", str(HTML2PDF), str(hp), str(raw), "210", "297"], cwd=ROOT, capture_output=True, text=True,
                               timeout=600)
            if p.returncode == 0 and raw.exists():
                how = "HTML → html2pdf.js (Chromium), A4 pionowo"
            else:
                log(f"html2pdf.js: {p.stderr[-300:]}")
        if how is None and shutil.which("soffice"):
            prof = f"-env:UserInstallation=file://{Path(tmp) / 'lo_profile'}"
            subprocess.run(["soffice", prof, "--headless", "--norestore", "--convert-to", "pdf", "--outdir", tmp, str(X["path"])],
                           capture_output=True, text=True, timeout=600)
            q = Path(tmp) / "F.14.A.pdf"
            if q.exists():
                shutil.copy(q, raw)
                how = "LibreOffice (xlsx → pdf)"
        if how is None:
            raise RuntimeError("nie udało się złożyć PDF")
        neutral_pdf(raw, pdf, "F.14.A Wstępna informacja o kosztach")
    import pymupdf
    d = pymupdf.open(str(pdf))
    k = 72 / 25.4
    info = dict(pages=d.page_count, size=[round(d[0].rect.width / k), round(d[0].rect.height / k)], how=how)
    txt = " ".join(pg.get_text() for pg in d)
    d.close()
    info["flags"] = [f for f, bad in (("słowo „robocz…”", re.search(r"robocz", txt, re.I)),
                                      ("liczba 6-cyfrowa (R-133?)", re.search(r"\b\d{6}\b", txt))) if bad]
    info["suma_w_pdf"] = pl(R["totF"]) in txt.replace(" ", NBSP)
    return pdf, info


# ================================================================================================ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--bez-pdf", action="store_true")
    ap.add_argument("--json", action="store_true", help="wydruk grup i kontroli jako JSON na stdout")
    ap.add_argument("--wymus", action="store_true", help="zapisz pliki mimo niezgodności z koncepcja.json[\"bilans\"]")
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    R = compute()
    for i in R["info"]:
        log("  " + i)
    log(f"  roboty: model {R['works_model'] / 1e6:.3f} + spoza modelu {sum(R['poza'].values()) / 1e6:.3f} = {R['works'] / 1e6:.3f} mln; "
        f"KS {R['ks_rate']:.0%} {R['ks'] / 1e6:.3f}; rezerwa {R['rez_rate']:.0%} {R['rez'] / 1e6:.3f}; razem {R['total_exact'] / 1e6:.4f} mln")
    if not R["zgodnosc"] and not a.wymus:
        for name, ok, det in R["checks"][:3]:
            log(f"  {'✔' if ok else '✖'} {name}: {det}")
        log("✖ suma F.14.A ≠ koncepcja.json[\"bilans\"] – pliki build/tabele/F.14.A.* NIE zostały nadpisane (najpierw zaktualizować "
            "bilans koncepcji albo skrypty kosztów; --wymus zapisuje mimo to)")
        return 1
    X = build_xlsx(R)
    log(f"  {X['path'].relative_to(ROOT)}: suma netto {pl(R['totF'])} zł, brutto {pl(R['totH'])} zł; usługa netto "
        f"{pl(R['fee'] or 0)} zł, brutto {pl(R['fee_b'] or 0)} zł")
    lo = lo_verify(X)
    if lo is not None:
        for ref, exp, got, ok in lo:
            R["checks"].append((f"LibreOffice {ref}", ok, f"{got} vs {exp}"))
    code = 0
    pinfo = None
    if not a.bez_pdf:
        try:
            pdf, pinfo = build_pdf(R, X)
            log(f"  {pdf.relative_to(ROOT)}: {pinfo['pages']} str., {pinfo['size'][0]}×{pinfo['size'][1]} mm, {pinfo['how']}"
                + (f"; UWAGA: {', '.join(pinfo['flags'])}" if pinfo["flags"] else ""))
            R["checks"].append(("PDF: 1 strona A4, suma widoczna", pinfo["pages"] == 1 and pinfo["size"] == [210, 297] and pinfo["suma_w_pdf"],
                                f"{pinfo['pages']} str. {pinfo['size']}"))
        except Exception as e:  # noqa: BLE001
            log(f"✖ PDF: {e}")
            code = 2
    for name, ok, det in R["checks"]:
        log(f"  {'✔' if ok else '✖'} {name}: {det}")
        if not ok and code == 0:
            code = 1
    for i in R["issues"]:
        log(f"  UWAGA: {i}")
    if a.json:
        print(json.dumps({
            "wersja_koncepcji": R["kon"]["meta"].get("wersja"), "wejscie": str(R["f_in"].relative_to(ROOT)),
            "grupy": {g: {"nazwa": X["names"][g], "netto": R["groups"][g]["F"], "brutto": R["groups"][g]["H"],
                          "sklad": GRUPY[g], "model": R["groups"][g]["model"], "spoza_modelu": R["groups"][g]["poza"]}
                      for g in range(1, 21)},
            "suma_netto": R["totF"], "suma_brutto": R["totH"], "suma_dokladna": round(R["total_exact"], 2),
            "roboty_model": round(R["works_model"], 2), "roboty_spoza_modelu": round(sum(R["poza"].values()), 2),
            "koszty_stale": round(R["ks"], 2), "rezerwa": round(R["rez"], 2),
            "usluga_netto": R["fee"], "usluga_brutto": R["fee_b"],
            "kontrole": [{"kontrola": n, "ok": bool(o), "szczegoly": d} for n, o, d in R["checks"]], "uwagi": R["issues"],
            "pdf": pinfo}, ensure_ascii=False, indent=1))
    return code


if __name__ == "__main__":
    sys.exit(main())
