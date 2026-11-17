#!/usr/bin/env python3
"""Generator tabel obowiązkowych Etapu II na wzorach Organizatora: F.15.A, F.15.B, F.15.C, F.14.B.

Uruchomienie (z katalogu umwd/; idempotentne – każde uruchomienie nadpisuje te same pliki):
    python3 -I tools/tabele_konkursowe.py              # xlsx + PDF (A3 poziomo) + kontrola.md
    python3 -I tools/tabele_konkursowe.py --bez-pdf    # bez renderu PDF i bez weryfikacji w LibreOffice

Wyniki (build/tabele/):
    F.15.A.xlsx, F.15.B.xlsx, F.15.C.xlsx, F.14.B.xlsx   – wzory Organizatora (układ, style, nagłówki, kolumny bez zmian;
                                                          wiersze wstawiane ze stylem wiersza-wzorca, sumy jako formuły)
    F.15.A.pdf … F.14.B.pdf                              – rendery A3 poziomo (HTML -> tools/plansze/html2pdf.js;
                                                          awaryjnie LibreOffice)
    kontrola.md                                          – kontrole krzyżowe z Δ i lista niespójności
    _html/                                               – źródła HTML renderów

Źródła czytane przy KAŻDYM uruchomieniu (żadnych liczb projektu wpisanych na stałe):
    model/budynek.json                 – pomieszczenia (numer, nazwa, kod_grupy, powierzchnia, poligon, kind), płyty, miejsca post.
    model/koncepcja.json               – bilans, zabudowa, podziemie, kondygnacje, bryły (dachy, wysokości), elewacje.PV
    model/site.json                    – Obszar inwestycji (pole), budynki istniejące
    docs/20_program/program.yaml       – program (liczby i powierzchnie pozycji, kategorie PN-ISO 9836)
    tools/zagospodarowanie.py          – geometria nawierzchni i zieleni (wykonywany tylko fragment definicji geometrii)
    tools/koszty_model.py (+ parametry koncepcji z docs/20_koncepcja/_weryfikacja_koszt_eko.py, nadpisane danymi z modelu)
    docs/20_koncepcja/koncepcja_wybrana.md – korekty kosztu poza modelem, koszt Dokumentacji, rozbicie PU i grup kosztów
    build/rzuty/rzut_*_1-200.svg       – numery i sumy na rzutach (kontrola zgodności numeracji)

Kontrakt skryptu rewizji kosztów (docs/20_koncepcja/_v1N_*koszt*.py – pierwszeństwo – albo _rewizja_*.py): generator użyje go zamiast
koszty_model.py, jeśli moduł udostępnia (w kolejności): funkcję f14b_rows(level) lub stałą F14B_ROWS – listę krotek
(lp, opis, jm, ilosc, cena_jedn, wartosc) w konwencji koszty_model.compute()["rows"]; albo słownik PARAMS
(+ opcjonalnie POZA_MODELEM {opis: zł}) dla koszty_model.compute(); albo obsługuje wywołanie `--rows mid` z wydrukiem
tabeli markdown jak koszty_model.py. Opcjonalnie KOSZT_DOKUMENTACJI [zł netto]. Bez rewizji arkusz F.14.B dostaje
oznaczenie „WERSJA ROBOCZA – PRZED REWIZJĄ KOSZTÓW”.
"""
import argparse
import ast
import hashlib
import html
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from collections import OrderedDict, defaultdict
from copy import copy
from pathlib import Path

import openpyxl
import yaml
from openpyxl.styles import Alignment, Font
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[1]
TPL_DIR = ROOT / "00_materialy" / "_rozpak" / "4.Zalaczniki_Formalne_F.03-F.16_edytowalne"
OUT = ROOT / "build" / "tabele"
P = {
    "bud": ROOT / "model" / "budynek.json",
    "kon": ROOT / "model" / "koncepcja.json",
    "site": ROOT / "model" / "site.json",
    "prog": ROOT / "docs" / "20_program" / "program.yaml",
    "km": ROOT / "tools" / "koszty_model.py",
    "wer": ROOT / "docs" / "20_koncepcja" / "_weryfikacja_koszt_eko.py",
    "kmd": ROOT / "docs" / "20_koncepcja" / "koncepcja_wybrana.md",
    "bench": ROOT / "docs" / "50_research" / "koszty_benchmarki.md",
    "wermd": ROOT / "docs" / "20_koncepcja" / "weryfikacja_koszt_eko.md",
    "rej": ROOT / "docs" / "20_koncepcja" / "rejestr_poprawek_v1_1.md",
    "zag": ROOT / "tools" / "zagospodarowanie.py",
    "rzuty_py": ROOT / "tools" / "rzuty.py",
}
RZUTY_DIR = ROOT / "build" / "rzuty"
HTML2PDF = ROOT / "tools" / "plansze" / "html2pdf.js"
TEMPLATES = {
    "F.15.A": "F.15.A_Tabela Programowa.xlsx",
    "F.15.B": "F.15.B_Zestawienie pomiesczen.xlsx",
    "F.15.C": "F.15.C_Dane_bilansowe.xlsx",
    "F.14.B": "F.14.B_Informacja o kosztach - ETAP II.xlsx",
}

# ---- stałe metodyczne i regulaminowe (nie są danymi projektu) --------------------------------------------------
LIMIT_KOSZTU = 150e6            # Reg. R.III ust. 3; Wyj. 20 odp. 74 – nieprzekraczalny limit netto
LIMIT_USLUGI_PROC = 0.054       # Reg. R.III ust. 4 – koszt usługi ≤ 5,4 % planowanego kosztu realizacji netto
VAT = 0.23                      # stawka podstawowa (wzór F.14.B); 8 % pozostawione tam, gdzie wpisał je wzór
PBC_DACH_WSP = 0.5              # § 3 pkt 22 WT: 50 % powierzchni stropodachów/tarasów urządzonych jako zieleń
ETAPY_F01 = [("E1", 0.12), ("E2", 0.30), ("E3", 0.10), ("E4", 0.40), ("E5", 0.01), ("E6", 0.07)]  # F.01 § 14 ust. 2
# Podział pozycji zbiorczych modelu kosztów na wiersze wzoru – udziały typowe [Z] (założenie generatora, do weryfikacji
# kosztorysanta; model kosztów wycenia te instalacje jednym wskaźnikiem zł/m² PC).
UDZIALY = {
    "8.1-8.10": {1: .12, 2: .10, 3: .30, 4: .07, 5: .03, 6: .02, 7: .04, 8: .17, 9: .11, 10: .04},
    "9.1-9.9": {1: .35, 2: .12, 3: .06, 4: .10, 5: .02, 6: .17, 7: .10, 8: .04, 9: .04},
}
NOTY_F14B = {  # wiersze wzoru bez odpowiednika w modelu kosztów
    "13.7": "brak takich posadzek w koncepcji (pom. techniczne – poz. 13.4)",
    "14.5": "ujęte w poz. 14.2",
    "15.3": "brak parkingów naziemnych – miejsca postojowe w garażu podziemnym (gr. 3 i 13.5)",
    "17.1": "rekuperacja ujęta w poz. 7.6 (centrale z odzyskiem ciepła)",
}
KAT_NAZWY = {"PU": "powierzchnia użytkowa (PU)", "RU": "powierzchnia ruchu (komunikacja, hole)",
             "US": "powierzchnia usługowa / techniczna", "PG": "garaż – stanowiska postojowe (PG)"}
NOWE_SEKCJE = {  # grupy spoza wzoru F.15.A (Wyj. 20 odp. 73, S-16)
    "PHS": "Pomieszczenia higieniczno-sanitarne",
    "KW": "Komunikacja wewnętrzna (korytarze, klatki schodowe, przedsionki ppoż., szyby dźwigowe)",
}
NBSP = " "


# =================================================================================================== narzędzia
def pl(x, nd=2, unit=""):
    if x is None:
        return ""
    s = f"{x:,.{nd}f}".replace(",", "§").replace(".", ",").replace("§", NBSP)
    return s + (f" {unit}" if unit else "")


def dpl(x, nd=2, unit=""):
    """Δ ze znakiem."""
    if x is None:
        return "–"
    if abs(x) < 0.5 * 10 ** (-nd):
        return "0" + ("," + "0" * nd if nd else "") + (f" {unit}" if unit else "")
    return ("+" if x > 0 else "−") + pl(abs(x), nd, unit)


def xround(x, nd=2):
    """ROUND jak w Excelu/LibreOffice: 15 cyfr znaczących, potem połówki od zera (Python round() zaokrągla „do parzystej”)."""
    from decimal import ROUND_HALF_UP, Decimal
    return float(Decimal(f"{x:.15g}").quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def nat(s):
    return [(0, int(t), "") if t.isdigit() else (1, 0, t) for t in re.split(r"(\d+)", s or "") if t != ""]


def sha(p):
    try:
        return hashlib.sha1(Path(p).read_bytes()).hexdigest()[:10]
    except OSError:
        return "brak"


def rel(p):
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def mp(rings_list):
    ps = []
    for poly in rings_list or []:
        if poly and len(poly[0]) >= 3:
            g = Polygon(poly[0], [h for h in poly[1:] if len(h) >= 3])
            if not g.is_valid:
                g = make_valid(g)
            ps.append(g)
    return unary_union(ps) if ps else Polygon()


def num_pl(s):
    return float(s.replace(NBSP, "").replace(" ", "").replace(" ", "").replace(",", "."))


# =================================================================================================== dane
class Dane:
    def __init__(self):
        self.bud = json.loads(P["bud"].read_text(encoding="utf-8"))
        self.kon = json.loads(P["kon"].read_text(encoding="utf-8"))
        self.site = json.loads(P["site"].read_text(encoding="utf-8"))
        self.prog = yaml.safe_load(P["prog"].read_text(encoding="utf-8"))
        self.kmd = P["kmd"].read_text(encoding="utf-8") if P["kmd"].exists() else ""
        self.blocks = OrderedDict((b["kod"], b) for b in self.prog["bloki"])
        self.items = {it["id"]: (b["kod"], it) for b in self.prog["bloki"] for it in b["pomieszczenia"]}
        self.storeys = []
        self.rooms = []
        for i, k in enumerate(self.bud["kondygnacje"]):
            st = dict(id=k["id"], idx=i, rzedna=k.get("rzedna"), plyta=mp(k.get("plyta")).area,
                      miejsca=len(k.get("miejsca_postojowe") or []),
                      ozn=sum(1 for m in (k.get("miejsca_postojowe") or []) if m.get("ozn")))
            self.storeys.append(st)
            for r in k["pomieszczenia"]:
                pw = r.get("powierzchnia")
                room = dict(st=k["id"], sidx=i, numer=(r.get("numer") or "").strip(), nazwa=(r.get("nazwa") or "").strip(),
                            kod=r.get("kod_grupy") or "", pow=float(pw) if pw is not None else None,
                            pow_poly=mp(r.get("poligon")).area, kind=r.get("kind") or "", prog_id=r.get("prog_id") or "",
                            tags=r.get("tags") or [])
                room["kat"] = self.kategoria(room)
                self.rooms.append(room)
        self.sid = {s["id"]: s for s in self.storeys}
        self.tokens = {s["id"]: s["idx"] for s in self.storeys}
        for s in self.storeys:
            if s["id"].upper().startswith("ANT"):
                self.tokens["A"] = s["idx"]
        self.meta_storeys()

    @staticmethod
    def base_pid(pid):
        return re.sub(r"(?<=\d)[a-z]+$", "", pid or "")

    def prog_item(self, pid):
        return self.items.get(pid) or self.items.get(self.base_pid(pid))

    def kategoria(self, r):
        it = self.prog_item(r["prog_id"])
        if it and it[1].get("kategoria_pn_iso"):
            return it[1]["kategoria_pn_iso"]
        if r["kod"] == "KW" or r["kind"] in ("corridor", "core_lobby", "core_stair", "core_lift", "ramp"):
            return "RU"
        if r["kind"] == "shaft" or r["kod"] == "IT":
            return "US"
        if r["kind"] == "garage":
            return "PG"
        if r["kind"] == "roof":
            return "DACH"
        return "PU"

    def meta_storeys(self):
        n = 0
        ant_z = (self.kon.get("kondygnacja_sejmiku") or {}).get("antresola", {}).get("wzgl")
        for s in self.storeys:
            sid, z = s["id"], s["rzedna"]
            s["mezz"] = sid.upper().startswith("ANT")
            s["roof"] = sid == "D" or (z is None and all(r["kind"] == "roof" for r in self.rooms if r["st"] == sid))
            if s["roof"]:
                s["title"], s["kond"] = "DACH", "dach"
            elif z is not None and z < 0:
                s["title"], s["kond"] = f"KONDYGNACJA {sid}", sid
            elif sid == "P":
                s["title"], s["kond"], n = "PARTER", "P", 0
            elif s["mezz"]:
                zt = f" (posadzka +{pl(ant_z, 2)})" if ant_z is not None else ""
                s["title"], s["kond"] = f"ANTRESOLA KONDYGNACJI SEJMIKU{zt}", f"S ({n}) antr."
            else:
                n += 1
                if sid.isdigit():
                    s["title"], s["kond"] = f"{sid} PIĘTRO", sid
                elif sid == "S":
                    s["title"], s["kond"] = f"{n} PIĘTRO – KONDYGNACJA SEJMIKU (S)", f"S ({n})"
                else:
                    s["title"], s["kond"] = f"{n} PIĘTRO ({sid})", sid

    def net_rooms(self):
        return [r for r in self.rooms if r["kind"] != "roof" and not self.sid[r["st"]]["roof"]]

    def sort_key(self, r):
        m = re.match(r"^([A-Z]+)\.([^.]+)\.(\d+)$", r["numer"])
        if m and m.group(2) in self.tokens:
            return (1, self.tokens[m.group(2)], nat(r["numer"]))
        return (0, 0, nat(r["numer"]))


# =================================================================================================== arkusz
def col_w(ws, letter):
    d = ws.column_dimensions.get(letter)
    if d is not None and d.width and (d.customWidth or d.width != 13):
        return d.width
    return 8.43


def xl_lines(text, chars):
    n = 0
    for para in str(text or "").split("\n"):
        words, cur, k = para.split(), 0, 1
        for w in words:
            if cur == 0:
                cur = len(w)
            elif cur + 1 + len(w) <= chars:
                cur += 1 + len(w)
            else:
                k += 1
                cur = len(w)
        n += k
    return max(n, 1)


class Body:
    """Przebudowa części tabelarycznej arkusza wzoru: wiersze-wzorce (styl, wysokość, scalenia) -> nowe wiersze."""

    def __init__(self, ws, start):
        self.ws, self.start, self.r = ws, start, start
        maxr, self.maxc = ws.max_row, ws.max_column
        merges = [m for m in ws.merged_cells.ranges if m.min_row >= start]
        mm = defaultdict(list)
        for m in merges:
            mm[m.min_row].append((m.min_col, m.max_col))
        self.protos = {}
        for r in range(start, maxr + 1):
            self.protos[r] = dict(h=ws.row_dimensions[r].height if r in ws.row_dimensions else None,
                                  st={c: copy(ws.cell(r, c)._style) for c in range(1, self.maxc + 1)},
                                  m=list(mm.get(r, [])),
                                  v={c: ws.cell(r, c).value for c in range(1, self.maxc + 1)})
        for m in merges:
            ws.unmerge_cells(str(m))
        ws.delete_rows(start, maxr - start + 1)
        for r in [k for k in list(ws.row_dimensions.keys()) if k >= start]:
            del ws.row_dimensions[r]

    def val(self, proto, col):
        return self.protos[proto]["v"].get(col)

    def put(self, proto, values=None, height="proto", merges="proto", keep=False):
        """keep=True: przepisz też treść wiersza-wzorca (etykiety wzoru), potem nadpisz `values`."""
        p, r, ws = self.protos[proto], self.r, self.ws
        for c, st in p["st"].items():
            ws.cell(r, c)._style = copy(st)
            if keep and p["v"].get(c) is not None:
                ws.cell(r, c).value = p["v"][c]
        for c, v in (values or {}).items():
            ci = openpyxl.utils.column_index_from_string(c) if isinstance(c, str) else c
            ws.cell(r, ci).value = v
        h = p["h"] if height == "proto" else height
        if h is not None:
            ws.row_dimensions[r].height = h
        for c1, c2 in (p["m"] if merges == "proto" else merges):
            ws.merge_cells(start_row=r, start_column=c1, end_row=r, end_column=c2)
            for c in range(c1 + 1, c2 + 1):
                ws.cell(r, c)._style = copy(p["st"].get(c, p["st"][c1]))
        self.r += 1
        return r


def clean_meta(wb, title):
    pr = wb.properties
    for a in ("creator", "lastModifiedBy", "title", "subject", "description", "keywords", "category", "contentStatus",
              "identifier", "language", "version", "revision"):
        try:
            setattr(pr, a, None)
        except Exception:
            pass
    pr.lastPrinted = None
    try:
        wb.custom_doc_props.props.clear()
    except Exception:
        pass
    wb.calculation.fullCalcOnLoad = True


CORE_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.'
            'org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/'
            'terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>'
            '{t}</dc:title></cp:coreProperties>')
APP_XML = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Properties xmlns="http://schemas.openxmlformats.org/'
           'officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
           '<Application>Microsoft Excel</Application><DocSecurity>0</DocSecurity><ScaleCrop>false</ScaleCrop><LinksUpToDate>false'
           '</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged></Properties>')


def save_clean(wb, path, title):
    """Zapis xlsx bez metadanych (R-127/R-134): core.xml tylko z tytułem tabeli, app.xml bez Company/Manager,
    bez custom.xml, stałe znaczniki czasu w ZIP (powtarzalny wynik)."""
    clean_meta(wb, title)
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


def header_texts(ws):
    return [str(ws["B2"].value or "").strip(), str(ws["B3"].value or "").strip(), str(ws["B4"].value or "").strip()]


def note_style(cell, size=9, italic=True, bold=False, color=None):
    cell.font = Font(name="Calibri", sz=size, i=italic, b=bold, color=color)
    cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)


# =================================================================================================== F.15.A
def scan_f15a(ws):
    secs, cur = [], None
    for r in range(7, ws.max_row + 1):
        v = ws.cell(r, 2).value
        if v is None:
            continue
        s = str(v).strip()
        m = re.match(r"^([A-Z]+)(\.\d+|…)", s)
        if m:
            if cur is not None:
                cur.setdefault("item", r)
                cur["code"] = m.group(1)
        elif s.startswith("Razem"):
            if cur is not None:
                cur["razem"], cur["razem_text"] = r, str(v)
        elif s.startswith("…"):
            if cur is not None:
                cur["inne"] = r
        else:
            cur = dict(header=r, title=re.sub(r"\s+", " ", str(v)).strip())
            secs.append(cur)
    return [s for s in secs if "code" in s and "razem" in s]


def build_f15a(D, res):
    wb = openpyxl.load_workbook(TPL_DIR / TEMPLATES["F.15.A"])
    ws = wb.active
    hdr = header_texts(ws)
    secs = scan_f15a(ws)
    by = {s["code"]: s for s in secs}
    order = [s["code"] for s in secs]
    rooms = D.net_rooms()
    codes_model = []
    for r in rooms:
        if r["kod"] not in codes_model:
            codes_model.append(r["kod"])
    extra = [c for c in NOWE_SEKCJE if c not in order] + sorted(c for c in codes_model if c not in order and c not in NOWE_SEKCJE)
    order_all = order + extra
    body = Body(ws, 7)
    fallback = secs[-1]
    spacer_proto = secs[0]["razem"] + 1
    cw = col_w(ws, "C") * 1.08
    body.put(7)
    razem_cells, rows_html, sec_rows = [], [], []
    first_item = None
    for code in order_all:
        grp = sorted([r for r in rooms if r["kod"] == code], key=D.sort_key)
        sec = by.get(code, fallback)
        if code in by:
            title = sec["title"]
            razem_text = sec["razem_text"]
        else:
            nm = NOWE_SEKCJE.get(code) or D.blocks.get(code, {}).get("nazwa") or code
            title = nm
            razem_text = f"Razem -  {nm.split(' (')[0]} ({code})"
        hp = body.protos[sec["header"]]["h"]
        tl = xl_lines(title, (col_w(ws, "B") + col_w(ws, "C") + col_w(ws, "D") + col_w(ws, "E")) * 1.0)
        body.put(sec["header"], {"B": title}, height=max(hp or 15.0, 15.0 * tl) if (tl > 1 or code not in by) else "proto")
        rows_html.append(dict(k="sec", c={"nr": title}, span=("nr", "pow")))
        a = None
        for r in grp:
            ln = xl_lines(r["nazwa"], cw)
            ph = body.protos[sec["item"]]["h"] or 15.0
            rr = body.put(sec["item"], {"B": r["numer"], "C": r["nazwa"], "D": D.sid[r["st"]]["kond"], "E": r["pow"], "G": r["kat"]},
                          height=max(ph, 13.0 * ln + 2.4))
            a = a or rr
            first_item = first_item or rr
            rows_html.append(dict(k="item", c={"nr": r["numer"], "opis": r["nazwa"], "kond": D.sid[r["st"]]["kond"], "pow": pl(r["pow"])},
                                  numer=r["numer"]))
        b = body.r - 1
        tot = round(sum(r["pow"] or 0 for r in grp), 2)
        rr = body.put(sec["razem"], {"B": razem_text, "E": f"=SUM(E{a}:E{b})" if a else 0})
        razem_cells.append(f"E{rr}")
        sec_rows.append(dict(code=code, title=title, n=len(grp), pow=tot, cell=f"E{rr}"))
        rows_html.append(dict(k="sum", c={"nr": razem_text, "pow": pl(tot)}, span=("nr", "kond")))
        body.put(spacer_proto)
        rows_html.append(dict(k="gap"))
    last_item = body.r - 2
    # suma całkowita i rozbicie wg PN-ISO 9836 (SUMIF po pomocniczej, ukrytej kolumnie G z kategorią)
    total = round(sum(s["pow"] for s in sec_rows), 2)
    rt = body.put(fallback["razem"], {"B": "RAZEM BUDYNEK – powierzchnia netto wg PN-ISO 9836:2022-07 (suma sekcji)",
                                      "E": "=" + "+".join(razem_cells)})
    rows_html.append(dict(k="grand", c={"nr": "RAZEM BUDYNEK – powierzchnia netto wg PN-ISO 9836:2022-07", "pow": pl(total)},
                          span=("nr", "kond")))
    kat_sum = defaultdict(float)
    for r in rooms:
        kat_sum[r["kat"]] += r["pow"] or 0
    kat_cells = {}
    for k in ("PU", "RU", "US", "PG"):
        rr = body.put(fallback["item"], {"B": "", "C": f"w tym: {KAT_NAZWY[k]}", "D": k,
                                         "E": f'=SUMIF($G${first_item}:$G${last_item},"{k}",$E${first_item}:$E${last_item})'})
        kat_cells[k] = f"E{rr}"
        rows_html.append(dict(k="item", c={"nr": "", "opis": f"w tym: {KAT_NAZWY[k]}", "kond": k, "pow": pl(kat_sum[k])}))
    body.put(spacer_proto)
    notes = ["Numer pomieszczenia = kod grupy + numer kolejny, identyczny z rzutami 1:200 i z F.15.B (Wyj. 20 odp. 73); pomieszczenia "
             "KW i szachty IT z oznaczeniem kondygnacji (np. KW.3.05). Powierzchnie netto wg PN-ISO 9836:2022-07, liczone z obrysów "
             "pomieszczeń w świetle ścian. Dodane grupy spoza wzoru: " + ", ".join(extra) + ". Kolumna „kond.”: oznaczenie jak w F.15.B.",
             "Kategorie PN-ISO 9836 (kolumna D w wierszach „w tym”): PU – użytkowa, RU – ruchu, US – usługowa (techniczna), "
             "PG – stanowiska garażowe; przypisanie wg kategorii pozycji programu użytkowego (M.01; Wyj. 20 odp. 73)."]
    for t in notes:
        rr = body.put(spacer_proto, {"B": t}, height=15.0 * xl_lines(t, 105) + 2, merges=[(2, 5)])
        note_style(ws.cell(rr, 2))
        rows_html.append(dict(k="note", c={"nr": t}, span=("nr", "pow")))
    ws.column_dimensions["G"].hidden = True
    ws.cell(6, 7).value = "kat. PN-ISO (pomocn.)"
    ws.print_area = f"A1:E{body.r - 1}"
    path = OUT / "F.15.A.xlsx"
    save_clean(wb, path, "F.15.A Tabela programowa")
    res["F.15.A"] = dict(path=path, hdr=hdr, sec_rows=sec_rows, total=total, kat=dict(kat_sum), extra=extra, rows_html=rows_html,
                         checks={f"E{rt}": total, **{kat_cells[k]: round(kat_sum[k], 2) for k in kat_cells}})


# =================================================================================================== F.15.B
def build_f15b(D, res):
    wb = openpyxl.load_workbook(TPL_DIR / TEMPLATES["F.15.B"])
    ws = wb.active
    hdr = header_texts(ws)
    rows = {}
    for r in range(7, ws.max_row + 1):
        v = ws.cell(r, 2).value
        s = str(v).strip() if v is not None else ""
        if s.startswith("RAZEM") and s.strip() == "RAZEM":
            rows["total"] = r
        elif s.startswith("RAZEM"):
            rows.setdefault("razem", r)
        elif s.startswith("…"):
            rows.setdefault("item", r)
        elif s.startswith("*"):
            rows["foot"] = r
        elif s and "head" not in rows:
            rows["head"] = r
    rows["spacer"] = rows["razem"] + 1
    body = Body(ws, 7)
    cw = (col_w(ws, "C") + col_w(ws, "D") + col_w(ws, "E")) * 1.05
    storey_rows, razem_net, rows_html = [], [], []
    for s in D.storeys:
        rs = sorted([r for r in D.rooms if r["st"] == s["id"]], key=lambda r: nat(r["numer"]))
        body.put(rows["head"], {"B": s["title"]})
        rows_html.append(dict(k="sec", c={"nr": s["title"]}, span=("nr", "pow")))
        a = None
        for r in rs:
            ln = xl_lines(r["nazwa"], cw)
            rr = body.put(rows["item"], {"B": r["numer"], "C": r["nazwa"], "F": r["pow"]},
                          height=max(body.protos[rows["item"]]["h"] or 15.0, 13.0 * ln + 2.4))
            a = a or rr
            rows_html.append(dict(k="item", c={"nr": r["numer"], "opis": r["nazwa"], "pow": pl(r["pow"])}, numer=r["numer"]))
        b = body.r - 1
        tot = round(sum(r["pow"] or 0 for r in rs), 2)
        lab = f"RAZEM {s['title']}" if not s["roof"] else "RAZEM DACH (pola dachowe w obrysie attyk – informacyjnie, poza sumą)"
        rr = body.put(rows["razem"], {"B": lab, "F": f"=SUM(F{a}:F{b})" if a else 0})
        rows_html.append(dict(k="sum", c={"nr": lab, "pow": pl(tot)}, span=("nr", "opis")))
        storey_rows.append(dict(id=s["id"], title=s["title"], n=len(rs), pow=tot, cell=f"F{rr}", roof=s["roof"]))
        if not s["roof"]:
            razem_net.append(f"F{rr}")
        body.put(rows["spacer"])
        rows_html.append(dict(k="gap"))
    total = round(sum(x["pow"] for x in storey_rows if not x["roof"]), 2)
    rt = body.put(rows["total"], {"B": "RAZEM – powierzchnia netto kondygnacji (bez dachu)", "F": "=" + "+".join(razem_net)})
    rows_html.append(dict(k="grand", c={"nr": "RAZEM – powierzchnia netto kondygnacji (bez dachu)", "pow": pl(total)}, span=("nr", "opis")))
    body.put(rows["spacer"])
    notes = ["* numery pomieszczeń zgodne z częścią rysunkową pracy konkursowej (rzuty 1:200) i z tabelą F.15.A: kod grupy + numer "
             "kolejny; w grupach KW i IT (szachty) z oznaczeniem kondygnacji.",
             "Powierzchnie netto wg PN-ISO 9836:2022-07 z obrysów pomieszczeń w świetle ścian. Pozycje DACH to pola dachowe w obrysie "
             "attyk (nie są powierzchnią netto) – pokazane informacyjnie, niewliczone do RAZEM."]
    for i, t in enumerate(notes):
        rr = body.put(rows["foot"], {"B": t}, height=15.0 * xl_lines(t, 95) + 2, merges=[(2, 6)])
        note_style(ws.cell(rr, 2), size=10 if i == 0 else 9)
        rows_html.append(dict(k="note", c={"nr": t}, span=("nr", "pow")))
    ws.print_area = f"A1:F{body.r - 1}"
    path = OUT / "F.15.B.xlsx"
    save_clean(wb, path, "F.15.B Zestawienie pomieszczeń")
    res["F.15.B"] = dict(path=path, hdr=hdr, storey_rows=storey_rows, total=total, rows_html=rows_html, checks={f"F{rt}": total})


# =================================================================================================== F.15.C
def site_geometry(D):
    """Geometria nawierzchni z tools/zagospodarowanie.py (wykonany tylko fragment definicji, bez rysowania i zapisu)."""
    src = P["zag"].read_text(encoding="utf-8")
    cut = src.find("# ---------------- shadows")
    if cut < 0:
        raise RuntimeError("brak znacznika '# ---------------- shadows' w zagospodarowanie.py")
    ns = {"__file__": str(P["zag"]), "__name__": "zag_prefix"}
    sys.path.insert(0, str(ROOT / "src"))
    try:
        exec(compile(src[:cut], str(P["zag"]), "exec"), ns)
    finally:
        if sys.path and sys.path[0] == str(ROOT / "src"):
            sys.path.pop(0)
    inv, bld, garden, gard, paths, play, ogrodki = (ns[k] for k in ("inv", "bld", "garden", "gard", "paths", "play", "ogrodki"))
    pth = unary_union([p.buffer(1.1, cap_style=2) for p in paths]).intersection(garden)
    green = gard.difference(pth).difference(play)
    og = ogrodki.intersection(inv)
    return dict(inv=inv, bld=bld, paths=pth.intersection(gard).area, play=play.intersection(gard).area, green=green.area,
                og_oi=og.area, og_paths=og.intersection(pth).area, og_play=og.intersection(play).area,
                ogrodki=ogrodki.intersection(green).area, rain=ns.get("rain").area if ns.get("rain") is not None else None,
                paved=inv.difference(bld).difference(gard).area)


def site_balance(D):
    kon, site = D.kon, D.site
    oi = site["granice"]["obszar_inwestycji"]
    S = dict(OI=oi.get("pole_m2") or Polygon(oi["pts"]).area, PZ=kon["bilans"]["PZ_m2"], notes=[])
    inv = Polygon(oi["pts"]).buffer(0)
    ist = 0.0
    for b in site.get("budynki", {}).get("items", []):
        pts = b.get("pts") or b.get("obrys") or b.get("obrys_egib_en")
        if pts and len(pts) >= 3:
            ist += Polygon(pts).buffer(0).intersection(inv).area
    S["istn_raw"] = ist
    S["istn"] = ist if ist >= 1.0 else 0.0   # < 1 m²: styk obrysów EGiB z granicą (dokładność mapy ±0,3–0,5 m)
    roofs = [r for r in D.rooms if r["kind"] == "roof"]
    S["green_roof"] = round(sum(r["pow"] or 0 for r in roofs if re.search(r"zielon|zieleń", r["nazwa"], re.I)), 2)
    S["pbc_dach"] = round(PBC_DACH_WSP * S["green_roof"], 2)
    try:
        g = site_geometry(D)
        S.update(src="geometria tools/zagospodarowanie.py", paths=round(g["paths"], 2), play=round(g["play"], 2),
                 pbc_istn=round(g["ogrodki"], 2), pbc_rek=round(g["green"] - g["ogrodki"], 2), geo=g)
    except Exception as e:  # awaryjnie: PBC z bilansu koncepcji, reszta jako place
        S["notes"].append(f"geometria zagospodarowania niedostępna ({e}); PBC z koncepcja.bilans")
        S.update(src="koncepcja.bilans (awaryjnie)", paths=0.0, play=0.0, pbc_istn=0.0,
                 pbc_rek=round(kon["bilans"]["PBC_m2"] - S["pbc_dach"], 2), geo=None)
    S["pbc_ground"] = round(S["pbc_istn"] + S["pbc_rek"], 2)
    S["place"] = round(S["OI"] - S["PZ"] - S["istn"] - S["pbc_ground"] - S["paths"] - S["play"], 2)
    S["utw"] = round(S["place"] + S["paths"] + S["play"], 2)
    S["pbc"] = round(S["pbc_ground"] + S["pbc_dach"], 2)
    return S


def building_params(D):
    kon, b = D.kon, D.kon["bilans"]
    K = dict(PZ=b["PZ_m2"], PC_nad=b["PC_nadziemna_m2"], PC_pod=b["PC_podziemna_m2"], KW=b["KW_m3"])
    kond = kon["kondygnacje"]
    K["n_pod"] = sum(1 for k in kond if k["posadzka_wzgl"] < 0)
    K["n_nad"] = sum(1 for k in kond if k["posadzka_wzgl"] >= 0)
    pod = kon["podziemie"]
    v = 0.0
    for k in kond:
        if k["posadzka_wzgl"] < 0 and k["kondygnacja"] in pod:
            h = k["wysokosc_kondygnacji"]
            pd = k.get("plyta_denna")
            if pd:
                h += pd["wierzch"] - pd["spod"]
            v += pod[k["kondygnacja"]]["pow_m2"] * h
    K["KW_pod"] = round(v, 1)
    br = {x["id"]: x for x in kon["bryly"]}
    W = br.get("W", {}).get("dach", {})
    K["H_W_attyka"] = W.get("attyka", {}).get("nad_najnizszym_terenem_A")
    K["H_W_attyka_npm"] = W.get("attyka", {}).get("npm")
    K["H_W_min"] = W.get("najnizszy_pkt_pokrycia", {}).get("nad_najwyzszym_terenem_A")
    M = br.get("M", {}).get("dach", {})
    K["H_M"] = M.get("gzyms_attyka", {}).get("nad_najnizszym_terenem")
    Sg = br.get("S", {}).get("dach", {})
    K["H_S"] = Sg.get("attyka", {}).get("nad_najnizszym_terenem")
    lifts = {}
    for r in D.rooms:
        if r["kind"] == "core_lift":
            key = r["tags"][0] if r["tags"] else r["nazwa"]
            lifts[key] = r["nazwa"]
    K["lifts"] = lifts
    tow = re.compile(r"os\.\s*-\s*tow|osobowo-towar|towarow", re.I)   # uwaga: „ratowniczy”, „przelotowy” zawierają „tow”
    K["lifts_os"] = sum(1 for n in lifts.values() if not tow.search(n))
    K["lifts_tow"] = sum(1 for n in lifts.values() if tow.search(n))
    K["miejsca"] = pod.get("razem_miejsc")
    K["miejsca_kond"] = {k: v["miejsca"] for k, v in pod.items() if isinstance(v, dict) and "miejsca" in v}
    K["ozn"], K["ev"] = pod.get("OzN"), pod.get("EV_punkty")
    K["rowery"] = sum(int(m) for r in D.rooms if r["kod"] == "PR" for m in re.findall(r"(\d+)\s*stanowisk", r["nazwa"]))
    K["pv"] = (kon.get("elewacje", {}).get("PV") or {}).get("razem_kWp")
    net = D.net_rooms()
    K["net"] = round(sum(r["pow"] or 0 for r in net), 2)
    for k in ("PU", "RU", "US", "PG"):
        K["kat_" + k] = round(sum(r["pow"] or 0 for r in net if r["kat"] == k), 2)
    return K


def build_f15c(D, res):
    wb = openpyxl.load_workbook(TPL_DIR / TEMPLATES["F.15.C"])
    ws = wb.active
    hdr = header_texts(ws)
    S, K = site_balance(D), building_params(D)
    tr = {}
    for r in range(7, ws.max_row + 1):
        v = ws.cell(r, 2).value
        if v is not None:
            tr[str(v).strip()] = r
    foot = next(r for r in range(7, ws.max_row + 1) if str(ws.cell(r, 2).value or "").startswith("*"))
    head2 = next(r for r in range(tr["RAZEM TEREN OPRACOWANIA"] + 1, ws.max_row + 1) if ws.cell(r, 2).value == "nr")
    body = Body(ws, 7)
    R, html1, html2 = {}, [], []
    cwC = (col_w(ws, "C") + col_w(ws, "D") + col_w(ws, "E")) * 1.12

    def put(key, proto, desc=None, val=None, unit=None, hrows=None, part=1, disp=None, fmt=None):
        vals = {}
        d = desc if desc is not None else body.val(proto, 3)
        if desc is not None:
            vals["C"] = desc
        if val is not None:
            vals["F"] = val
        if unit is not None:
            vals["E"] = unit
        if key is not None and not str(body.val(proto, 2) or "").strip() == key:
            vals["B"] = key
        ln = xl_lines(d, cwC if part == 1 else (col_w(ws, "C") + col_w(ws, "D")) * 1.12)
        rr = body.put(proto, vals, height=max(body.protos[proto]["h"] or 15.0, 13.0 * ln + 2.4), keep=True)
        if fmt:
            ws.cell(rr, 6).number_format = fmt
        R[key or f"r{rr}"] = rr
        row = dict(k="item", c={"nr": key or str(body.val(proto, 2) or ""), "opis": str(d or "").strip(),
                                "pow": disp if disp is not None else (pl(val) if isinstance(val, (int, float)) else "")})
        if part == 2:
            row["c"]["jedn"] = unit if unit is not None else str(body.val(proto, 5) or "")
            row["c"]["ilosc"] = row["c"].pop("pow")
        (html1 if part == 1 else html2).append(row)
        return rr

    body.put(tr["BILANS TERENU"], keep=True)
    html1.append(dict(k="sec", c={"nr": "BILANS TERENU"}, span=("nr", "pow")))
    put("1", tr["1"], val=None)
    put("1.1", tr["1.1"], val=S["PZ"])
    put("1.2", tr["1.2"], val=round(S["istn"], 2))
    put("2", tr["2"])
    put("2.1", tr["2.1"], val=0)
    put("2.2", tr["2.2"], val=0)
    put("2.3", tr["2.3"], val=0)
    put("2.4", tr["2.4"], desc=" - w tym place (nawierzchnie z granitu: wejścia, pas od bulwaru, opaski przy budynku)", val=S["place"])
    put("2.5", tr["2.5"], desc=" - w tym chodniki (ścieżki ogrodowe z cegły i płyt na podbudowie przepuszczalnej)", val=S["paths"])
    put("2.6", tr["2.6"], desc="- w tym inne powierzchnie utwardzone: nawierzchnia placu zabaw (bezpieczna, przepuszczalna)", val=S["play"])
    put("3", tr["3"])
    put("3.1", tr["3.1"], desc=" - w tym powierzchnia biologicznie czynna istniejąca bez zmian (zachowane ogródki przydomowe)",
        val=S["pbc_istn"])
    put("3.2", tr["3.2"], desc=" - w tym powierzchnia biologicznie czynna istniejąca do rekompozycji / zmiany (ogród, trawniki, "
                               "ogród deszczowy)", val=S["pbc_rek"])
    put("3.3", tr["3.3"], desc=" - w tym powierzchnia biologicznie czynna projektowana na dachach / tarasach "
                               f"({pl(PBC_DACH_WSP * 100, 0)} % z {pl(S['green_roof'])} m² dachu zielonego, § 3 pkt 22 WT)",
        val=S["pbc_dach"])
    put("…*", tr["…*"], val=0)
    # formuły sum
    ws.cell(R["1"], 6).value = f"=F{R['1.1']}+F{R['1.2']}"
    ws.cell(R["2"], 6).value = "=" + "+".join(f"F{R[k]}" for k in ("2.1", "2.2", "2.3", "2.4", "2.5", "2.6"))
    ws.cell(R["3"], 6).value = "=" + "+".join(f"F{R[k]}" for k in ("3.1", "3.2", "3.3"))
    for k, v in (("1", S["PZ"] + S["istn"]), ("2", S["utw"]), ("3", S["pbc"])):
        next(x for x in html1 if x["c"].get("nr") == k)["c"]["pow"] = pl(v)
    rt = body.put(tr["RAZEM TEREN OPRACOWANIA"], {"F": f"=F{R['1']}+F{R['2']}+F{R['3']}-F{R['3.3']}"}, keep=True)
    teren = round(S["PZ"] + S["istn"] + S["utw"] + S["pbc_ground"], 2)
    html1.append(dict(k="sum", c={"nr": "RAZEM TEREN OPRACOWANIA", "pow": pl(teren)}, span=("nr", "opis")))
    t = (f"Bilans dla Obszaru inwestycji wg M.04 (Wyj. 8 odp. 59), pow. {pl(S['OI'])} m². Poz. 3.3 wliczona do poz. 3, lecz nie do "
         "RAZEM (dachy leżą nad powierzchnią zabudowy). Skwer dz. 9/2 i dojazd dz. 10/2 – poza Obszarem inwestycji.")
    rr = body.put(foot, {"B": t}, height=15.0 * xl_lines(t, 95) + 2)
    note_style(ws.cell(rr, 2))
    html1.append(dict(k="note", c={"nr": t}, span=("nr", "pow")))
    body.put(head2 - 1)
    body.put(head2, keep=True)
    body.put(tr["PODSTAWOWE PARAMETRY"], keep=True)
    html2.append(dict(k="sec", c={"nr": "PODSTAWOWE PARAMETRY"}, span=("nr", "ilosc")))
    i = lambda k: tr[k]  # noqa: E731
    put("I.1", i("I.1"), val=K["PZ"], part=2)
    r_i2 = put("I.2", i("I.2"), val=None, part=2, disp=pl(K["PC_nad"] + K["PC_pod"]))
    r_i3 = put("I.3", i("I.3"), val=K["PC_nad"], part=2)
    r_i4 = put("I.4", i("I.4"), val=K["PC_pod"], part=2)
    ws.cell(r_i2, 6).value = f"=F{r_i3}+F{r_i4}"
    put("I.5", i("I.5"), val=K["n_pod"], part=2, unit="[szt.]", disp=str(K["n_pod"]), fmt="0")
    mz = any(s["mezz"] for s in D.storeys)
    put("I.6", i("I.6"), desc=f"liczba kondygnacji nadziemnych (parter + {K['n_nad'] - 1} pięter, w tym kondygnacja Sejmiku"
        + ("; antresola w kondygnacji Sejmiku nie stanowi odrębnej kondygnacji)" if mz else ")"),
        val=K["n_nad"], part=2, unit="[szt.]", disp=str(K["n_nad"]), fmt="0")
    put("I.7", i("I.7"), desc="wysokość – dominanta: attyka nad najniższym terenem przy bryle"
        + (f" (attyka {pl(K['H_W_attyka_npm'])} m n.p.m.)" if K["H_W_attyka_npm"] else ""), val=K["H_W_attyka"], part=2)
    put("I.7.1", i("I.7"), desc=" - dominanta: najniższy punkt pokrycia dachu nad najwyższym terenem (MPZP ≥ 35 m)", val=K["H_W_min"], part=2)
    put("I.7.2", i("I.7"), desc=" - skrzydło Mazowieckie: gzyms/attyka nad najniższym terenem (MPZP 18–25 m)", val=K["H_M"], part=2)
    put("I.7.3", i("I.7"), desc=" - segment Wybrzeża: attyka nad najniższym terenem", val=K["H_S"], part=2)
    r_i8 = put("I.8", i("I.8"), val=K["KW"], part=2)
    r_i9 = put("I.9", i("I.9"), val=None, unit="[m3]", part=2, disp=pl(K["KW"] - K["KW_pod"]))
    r_i10 = put("I.10", i("I.10"), val=K["KW_pod"], part=2)
    ws.cell(r_i9, 6).value = f"=F{r_i8}-F{r_i10}"
    put("I.11", i("I.11"), val=K["lifts_os"], part=2, unit="[szt.]", disp=str(K["lifts_os"]), fmt="0")
    put("I.11.1", i("I.11"), desc=" - ponadto dźwigi osobowo-towarowe", val=K["lifts_tow"], part=2, unit="[szt.]", disp=str(K["lifts_tow"]), fmt="0")
    r_i12 = put("I.12", i("I.12"), desc="powierzchnia użytkowa (PN-ISO 9836; bez powierzchni ruchu, usługowej i stanowisk garażowych)",
                val=None, part=2, disp=pl(K["kat_PU"]))
    put("I.13", i("I.13"), val=S["green_roof"], part=2)
    mk = K["miejsca_kond"]
    opis_m = ("liczba miejsc postojowych w garażu podziemnym (" + ", ".join(f"{k}: {v}" for k, v in mk.items())
              + (f"; w tym dla OzN: {K['ozn']}" if K["ozn"] is not None else "")
              + (f"; z punktem ładowania EV: {K['ev']}" if K["ev"] is not None else "") + ")")
    put("I.14", i("I.13"), desc=opis_m, val=K["miejsca"], unit="[szt.]", part=2, disp=str(K["miejsca"]), fmt="0")
    put("I.15", i("I.13"), desc="liczba stanowisk postojowych dla rowerów w budynku (PR)", val=K["rowery"], unit="[szt.]", part=2,
        disp=str(K["rowery"]), fmt="0")
    r16 = put("I.16", i("I.13"), desc="powierzchnia netto wszystkich kondygnacji (PN-ISO 9836; = RAZEM F.15.B)", val=K["net"], part=2)
    r161 = put("I.16.1", i("I.13"), desc=" - w tym powierzchnia ruchu (komunikacja wewnętrzna KW, hole SW/SK/SWD, rampy)",
               val=K["kat_RU"], part=2)
    r162 = put("I.16.2", i("I.13"), desc=" - w tym powierzchnia usługowa / techniczna (IT, szachty)", val=K["kat_US"], part=2)
    r163 = put("I.16.3", i("I.13"), desc=" - w tym garaż – stanowiska postojowe i drogi manewrowe (PG)", val=K["kat_PG"], part=2)
    ws.cell(r_i12, 6).value = f"=F{r16}-F{r161}-F{r162}-F{r163}"
    r17 = put("I.17", i("I.13"), desc="udział powierzchni zabudowy w Obszarze inwestycji", unit="[%]", part=2,
              disp=pl(100 * S["PZ"] / S["OI"], 1) + " %")
    r18 = put("I.18", i("I.13"), desc="udział powierzchni biologicznie czynnej (z dachami) w Obszarze inwestycji", unit="[%]", part=2,
              disp=pl(100 * S["pbc"] / S["OI"], 1) + " %")
    ws.cell(r17, 6).value = f"=F{R['1']}/F{rt}"
    ws.cell(r18, 6).value = f"=F{R['3']}/F{rt}"
    for rr in (r17, r18):
        ws.cell(rr, 6).number_format = "0.0%"
    if K["pv"] is not None:
        put("I.19", i("I.13"), desc="moc instalacji fotowoltaicznych (BIPV: dachy i elewacje)", val=K["pv"], unit="[kWp]", part=2)
    body.put(head2 - 1)
    t0 = body.val(foot, 2)
    rr = body.put(foot, {"B": str(t0).strip()})
    html2.append(dict(k="note", c={"nr": str(t0).strip()}, span=("nr", "ilosc")))
    t = ("Powierzchnie wg PN-ISO 9836:2022-07; wysokości wg MPZP (od terenu w pasie 2 m wokół bryły, ±0,00 = "
         f"{pl(D.kon['meta']['zero']['wzgl_0_00_m_npm'])} m n.p.m.). Kubatura podziemna z obrysów kondygnacji podziemnych i grubości "
         "płyty dennej; nadziemna = brutto − podziemna. Pozycje I.7.1–I.19 dodane zgodnie z przypisem *.")
    rr = body.put(foot, {"B": t}, height=15.0 * xl_lines(t, 95) + 2)
    note_style(ws.cell(rr, 2))
    html2.append(dict(k="note", c={"nr": t}, span=("nr", "ilosc")))
    ws.print_area = f"A1:F{body.r - 1}"
    path = OUT / "F.15.C.xlsx"
    save_clean(wb, path, "F.15.C Dane bilansowe")
    res["F.15.C"] = dict(path=path, hdr=hdr, S=S, K=K, html=(html1, html2), teren=teren,
                         checks={f"F{rt}": teren, f"F{r_i2}": round(K["PC_nad"] + K["PC_pod"], 2), f"F{r_i12}": K["kat_PU"]})


# =================================================================================================== koszty
def md_korekty(text):
    """Korekty kosztu poza modelem z koncepcja_wybrana.md: '... (+1,5); ... (+0,5)' [mln zł]."""
    out = []
    for line in text.splitlines():
        if "Korekty poza modelem" in line:
            body = line.split(":", 1)[1] if ":" in line else line
            body = body.split("|")[0]
            for part in body.split(";"):
                m = re.search(r"(.+?)\s*\(\+\s*([\d,]+)\s*\)", part)
                if m:
                    nm = m.group(1).strip(" *")
                    out.append((nm[0].upper() + nm[1:], num_pl(m.group(2)) * 1e6))
    return out


def md_koszt_dok(text):
    m = re.search(r"Koszt Dokumentacji\s*≈?\s*([\d,]+)\s*mln", text)
    return num_pl(m.group(1)) * 1e6 if m else None


def md_grupy(text):
    """Tabela grup F.14.B w rozdz. 12 koncepcji: '| 1 Roboty … | 10,94 |' [mln zł]."""
    sec = text.split("## 12.", 1)[1].split("\n## ", 1)[0] if "## 12." in text else ""
    out = defaultdict(float)
    for m in re.finditer(r"^\|\s*(\d+)(?:\.\d+)?\s+[^|]*\|\s*([\d,]+)\s*\|\s*$", sec, re.M):
        out[int(m.group(1))] += num_pl(m.group(2))
    return dict(out)


def md_pu(text):
    for line in text.splitlines():
        if "PU (bez RU i US)" in line:
            m = re.search(r"\(([^)]*\d[^)]*)\)\s*\|?\s*$", line)
            if m:
                return [(re.sub(r"\s+[\d\s]+$", "", p).strip(), num_pl(re.search(r"([\d\s]+)$", p).group(1)))
                        for p in m.group(1).split(",") if re.search(r"\d\s*$", p)]
    return []


def find_revision():
    """Skrypty rewizji kosztów: nazwa z „koszt”/„f14” albo jawny kontrakt (f14b_rows / F14B_ROWS) w treści.
    Inne _rewizja_*.py (np. PV/EP) nie są uruchamiane."""
    d = ROOT / "docs" / "20_koncepcja"
    # najnowsza rewizja kosztów ma pierwszeństwo: _v1N_*koszt*.py (malejąco po numerze wersji), potem _rewizja_*.py
    v = sorted(d.glob("_v1*_*koszt*.py"), key=lambda p: [int(x) for x in re.findall(r"^_v(\d+)", p.name)] or [0], reverse=True)
    c = v + sorted(d.glob("_rewizja_*.py"))
    cost = [p for p in c if re.search(r"koszt|f14", p.name, re.I)]
    cost += [p for p in c if p not in cost
             and re.search(r"def\s+f14b_rows|^F14B_ROWS\s*=", p.read_text(encoding="utf-8", errors="ignore"), re.M)]
    return cost


def revision_rows(km, base_params):
    """Próba odczytu pozycji F.14.B ze skryptu rewizji kosztów (kontrakt w docstringu). Zwraca (rows, extras, fee, info)."""
    for p in find_revision():
        try:
            mod = load_module(p, "rewizja_koszt")
        except Exception as e:  # noqa: BLE001
            mod, err = None, e
        if mod is not None:
            fee = getattr(mod, "KOSZT_DOKUMENTACJI", None)
            for nm in ("f14b_rows", "F14B_ROWS"):
                obj = getattr(mod, nm, None)
                if obj is not None:
                    rows = obj("mid") if callable(obj) else obj
                    if isinstance(rows, dict):
                        rows = rows.get("rows")
                    if rows:
                        return list(rows), [], fee, f"{rel(p)} ({nm})"
            if isinstance(getattr(mod, "PARAMS", None), dict):
                q = dict(km.REF)
                q.update(mod.PARAMS)
                r = km.compute(q, "mid")
                ex = list((getattr(mod, "POZA_MODELEM", None) or {}).items())
                return r["rows"], ex, fee, f"{rel(p)} (PARAMS)"
        if not re.search(r"koszt|f14", p.name, re.I):
            continue
        try:
            out = subprocess.run([sys.executable, "-I", str(p), "--rows", "mid"], cwd=ROOT, capture_output=True, text=True, timeout=300)
            rows = []
            for line in out.stdout.splitlines():
                m = re.match(r"^\|\s*([\d.\-*a-z]+)\s*\|\s*(.+?)\s*\|\s*([\d\s,.]+)\s*\|\s*(\S+)\s*\|\s*([\d\s,.]+)\s*\|\s*([\d\s,.]+)\s*\|$", line)
                if m and re.match(r"^\d", m.group(1)):
                    f = lambda s: float(s.replace(" ", "").replace(",", ""))  # noqa: E731
                    rows.append((m.group(1), m.group(2), m.group(4), f(m.group(3)), f(m.group(5)), f(m.group(6))))
            if rows:
                return rows, [], None, f"{rel(p)} (--rows mid)"
        except Exception:  # noqa: BLE001
            pass
    return None, None, None, None


def cost_inputs(D):
    km = load_module(P["km"], "koszty_model")
    p, info = dict(km.REF), ["tools/koszty_model.py: REF"]
    try:
        wer = load_module(P["wer"], "weryfikacja_koszt")
        p.update(getattr(wer, "SPEC", {}))
        p.update(getattr(wer, "UKRYTE", {}))
        info.append("parametry koncepcji (rozdz. 12 spec.): SPEC + UKRYTE z docs/20_koncepcja/_weryfikacja_koszt_eko.py")
    except Exception as e:  # noqa: BLE001
        info.append(f"brak parametrów koncepcji ({e}) – użyto REF")
    kon, K = D.kon, building_params(D)
    live = {"A_nad": kon["bilans"].get("PC_nadziemna_m2"), "A_pod": kon["bilans"].get("PC_podziemna_m2"),
            "fp_pod": kon["podziemie"].get("-1", {}).get("pow_m2"), "fp_nad": kon["bilans"].get("PZ_m2"),
            "kwp_dach": (kon.get("elewacje", {}).get("PV") or {}).get("BIPV_dach_kWp"), "ev": kon["podziemie"].get("EV_punkty"),
            "drzewa": kon.get("zagospodarowanie", {}).get("nowe_nasadzenia"),
            "windy_os": K["lifts_os"] or None, "windy_tow": K["lifts_tow"] or None}
    diffs = []
    for k, v in live.items():
        if v is not None:
            if k in p and abs(float(p[k]) - float(v)) > 1e-9:
                diffs.append((k, p[k], v))
            p[k] = v
    info.append("nadpisane danymi modelu: " + ", ".join(k for k, v in live.items() if v is not None))
    return km, p, info, diffs


def parse_lp(lp):
    lp = str(lp).strip()
    m = re.match(r"^(\d+)\.(\d+)\s*-\s*(\d+)\.(\d+)$", lp)
    if m:
        return dict(kind="range", g=int(m[1]), a=int(m[2]), b=int(m[4]), key=f"{m[1]}.{m[2]}-{m[3]}.{m[4]}")
    m = re.match(r"^(\d+)\.(\d+)([a-z]*)(\*?)$", lp)
    if m:
        return dict(kind="star" if m[4] else ("sub" if m[3] else "exact"), g=int(m[1]), n=int(m[2]), suf=m[3])
    m = re.match(r"^(\d+)", lp)
    return dict(kind="other", g=int(m[1]) if m else 18)


JM = {"m2PC": "m2 PC", "szt": "szt.", "m2": "m2", "m3": "m3", "mb": "mb", "kg": "kg", "kpl": "kpl", "kWp": "kWp", "kWh": "kWh"}


def build_f14b(D, res):
    km, params, info, diffs = cost_inputs(D)
    rows, extras_md, fee, rev = revision_rows(km, params)
    draft = rows is None
    if draft:
        r = km.compute(params, "mid")
        rows = r["rows"]
        extras_md = md_korekty(D.kmd)
        model_total = r["total"]
    else:
        model_total = sum(x[5] for x in rows)
    if fee is None:
        fee = md_koszt_dok(D.kmd)
    fee_src = "koncepcja_wybrana.md (rozdz. 12)" if fee is not None else None

    wb = openpyxl.load_workbook(TPL_DIR / TEMPLATES["F.14.B"])
    ws = wb.active
    hdr = header_texts(ws)
    # --- struktura wzoru
    groups, cur = [], None
    total_row = note_row = fee_n = fee_b = None
    for rr in range(7, ws.max_row + 1):
        b, f = ws.cell(rr, 2).value, ws.cell(rr, 6).value
        sb = str(b).strip() if b is not None else ""
        if isinstance(f, str) and f.startswith("=SUM"):
            cur = dict(num=int(float(sb)), row=rr, name=str(ws.cell(rr, 3).value).strip(), det=[], ph=None)
            groups.append(cur)
        elif sb.startswith("Szacunkowy koszt realizacji"):
            total_row, cur = rr, None
        elif sb.startswith("UWAGA"):
            note_row = rr
        elif "NETTO wykonania" in sb:
            fee_n = rr
        elif "BRUTTO wykonania" in sb:
            fee_b = rr
        elif cur is not None and sb:
            if sb.startswith("…") or sb.startswith("...."):
                cur["ph"] = rr
            else:
                cur["det"].append(dict(row=rr, lp=sb, n=int(sb.split(".")[1]), opis=str(ws.cell(rr, 3).value or "").strip(),
                                       jm=ws.cell(rr, 5).value, vat=ws.cell(rr, 7).value))
    gnums = {g["num"]: g for g in groups}
    tpl = {(g["num"], d["n"]): d for g in groups for d in g["det"]}
    # --- przypisanie pozycji modelu do wierszy wzoru
    comp, extra = defaultdict(list), defaultdict(list)
    for lp, op, jm, q, c, v in rows:
        pp = parse_lp(lp)
        g = pp["g"] if pp["g"] in gnums else 18
        base = dict(lp=str(lp), opis=op, jm=JM.get(jm, jm), q=float(q), c=float(c), v=float(v))
        if pp["kind"] == "range" and all((pp["g"], n) in tpl for n in range(pp["a"], pp["b"] + 1)):
            sh = UDZIALY.get(pp["key"])
            if sh and abs(sum(sh.values()) - 1) < 1e-6:
                for n in range(pp["a"], pp["b"] + 1):
                    comp[(pp["g"], n)].append(dict(base, c=base["c"] * sh[n], v=base["v"] * sh[n], share=sh[n]))
            else:
                comp[(pp["g"], pp["a"])].append(base)
        elif pp["kind"] in ("exact", "sub") and (pp["g"], pp["n"]) in tpl:
            comp[(pp["g"], pp["n"])].append(base)
        else:
            extra[g].append(base)
    # korekty poza modelem (spec.) – przed rezerwą w gr. 18
    rez = [x for x in extra[18] if re.search(r"rezerw", x["opis"], re.I)]
    extra[18] = [x for x in extra[18] if x not in rez] + [dict(lp="spec.", opis=n, jm="kpl", q=1.0, c=v, v=v) for n, v in extras_md] + rez

    def row_vals(cs):
        if not cs:
            return None, None, None
        if len(cs) == 1:
            x = cs[0]
            d = round(x["q"], 2)
            return d, x["jm"], round(x["v"] / d if d else x["c"], 6)
        if len({x["jm"] for x in cs}) == 1:
            d = round(sum(x["q"] for x in cs), 2)
            v = sum(x["v"] for x in cs)
            return d, cs[0]["jm"], round(v / d if d else 0.0, 6)
        return 1.0, "kpl", round(sum(x["v"] for x in cs), 2)

    # kolumny Ilość / J.m. / wartości poszerzone kosztem „Opis” – ta sama łączna szerokość B:H co we wzorze (wydruk bez zmian)
    tot_w = sum(col_w(ws, c) for c in "BCDEFGH")
    for c, w in (("D", 10.5), ("E", 6.0), ("F", 18.0), ("H", 18.0)):
        ws.column_dimensions[c].width = max(w, col_w(ws, c))
    ws.column_dimensions["C"].width = round(tot_w - sum(col_w(ws, c) for c in "BDEFGH"), 2)
    body = Body(ws, 7)
    cwC = col_w(ws, "C") * 1.12
    out_rows, html_rows, gcells, gsum = [], [], [], {}
    vat_fill, jm_fill = [], []
    for g in groups:
        rg = body.put(g["row"], {"B": g["num"], "C": g["name"], "E": "kpl"})
        html_rows.append(dict(k="grp", c={"lp": str(g["num"]), "opis": g["name"], "jm": "kpl"}, ref=len(out_rows)))
        a, gF, gH = None, 0.0, 0.0
        lines = []
        for d in g["det"]:
            cs = comp.get((g["num"], d["n"]), [])
            D_, jm, J = row_vals(cs)
            vat = d["vat"] if isinstance(d["vat"], (int, float)) else VAT
            if not isinstance(d["vat"], (int, float)):
                vat_fill.append(d["lp"])
            if not d["jm"] and jm:
                jm_fill.append(d["lp"])
            if cs:
                notes = []
                if any("share" in x for x in cs):
                    x = cs[0]
                    notes.append(f"udział {pl(100 * x['share'], 0)} % pozycji zbiorczej {x['lp']} ({x['opis']}) [Z]")
                else:
                    for x in cs:
                        if x["opis"] != d["opis"] or len(cs) > 1:
                            notes.append(f"{x['lp']}: {x['opis']} – {pl(x['q'])} {x['jm']} × {pl(x['c'])} zł")
                lines.append(dict(proto=d["row"], lp=d["lp"], opis=d["opis"], D=D_, E=jm or d["jm"], J=J, G=vat, K="; ".join(notes)))
            else:
                if not d["jm"]:
                    jm_fill.append(d["lp"])
                lines.append(dict(proto=d["row"], lp=d["lp"], opis=d["opis"], D=None, E=d["jm"] or "kpl", J=None, G=vat, F0=0.0,
                                  K=NOTY_F14B.get(d["lp"], "brak pozycji w modelu kosztów")))
        nmax = max([d["n"] for d in g["det"]] or [0])
        for k, x in enumerate(extra.get(g["num"], [])):
            D_, jm, J = row_vals([x])
            lines.append(dict(proto=(g["det"][-1]["row"] if g["det"] else (g["ph"] or g["row"] + 1)), lp=f"{g['num']}.{nmax + k + 1}",
                              opis=x["opis"], D=D_, E=jm, J=J, G=VAT, K=f"pozycja dodatkowa (model: {x['lp']})", new=True))
        if not extra.get(g["num"]) and g["ph"]:
            lines.append(dict(proto=g["ph"], lp=None, opis=None, D=None, E=None, J=None, G=None, F0=0.0, K="", ph=True))
        for ln in lines:
            vals = {}
            if not ln.get("ph"):
                vals.update({"B": ln["lp"], "C": ln["opis"], "E": ln["E"], "G": ln["G"]})
            if ln["D"] is not None:
                vals.update({"D": ln["D"], "J": ln["J"]})
                F = xround(ln["D"] * ln["J"], 2)
            else:
                F = ln.get("F0", 0.0)
            vals["K"] = ln["K"] or None
            nl = xl_lines(ln["opis"] or "", cwC)
            rr = body.put(ln["proto"], vals, height=(13.2 * nl + 2.0) if nl > 1 else "proto", keep=bool(ln.get("ph")))
            ws.cell(rr, 6).value = f"=ROUND(D{rr}*J{rr},2)" if ln["D"] is not None else F
            G = ln["G"] if isinstance(ln["G"], (int, float)) else (body.val(ln["proto"], 7) if isinstance(body.val(ln["proto"], 7), (int, float)) else 0)
            ws.cell(rr, 8).value = f"=ROUND(F{rr}*(1+G{rr}),2)"
            for c in (4, 10):
                ws.cell(rr, c).number_format = "#,##0.00"
            H = xround(F * (1 + (G or 0)), 2)
            gF += F
            gH += H
            a = a or rr
            out_rows.append(dict(row=rr, g=g["num"], lp=ln["lp"], opis=ln["opis"], D=ln["D"], E=ln["E"], J=ln["J"], F=F, G=G, H=H,
                                 K=ln["K"], new=ln.get("new", False), ph=ln.get("ph", False)))
            html_rows.append(dict(k="item", c={"lp": ln["lp"] or "….*", "opis": ln["opis"] or "inne (proszę wymienić)",
                                               "il": pl(ln["D"]) if ln["D"] is not None else "", "jm": ln["E"] or "",
                                               "net": pl(F, 2), "vat": (pl(100 * G, 0) + " %") if G else "", "brt": pl(H, 2)}))
        b = body.r - 1
        ws.cell(rg, 6).value = f"=SUM(F{a}:F{b})"
        ws.cell(rg, 8).value = f"=SUM(H{a}:H{b})"
        gcells.append(rg)
        gsum[g["num"]] = (round(gF, 2), round(gH, 2))
        html_rows[[i for i, x in enumerate(html_rows) if x["k"] == "grp"][-1]]["c"].update(net=pl(gF, 2), brt=pl(gH, 2))
    totF = round(sum(v[0] for v in gsum.values()), 2)
    totH = round(sum(v[1] for v in gsum.values()), 2)
    rt = body.put(total_row, {"F": "=" + "+".join(f"F{r}" for r in gcells), "H": "=" + "+".join(f"H{r}" for r in gcells)}, keep=True)
    lab_t = str(body.val(total_row, 2))
    html_rows.append(dict(k="grand", c={"lp": lab_t, "jm": "kpl", "net": pl(totF, 2), "brt": pl(totH, 2)}, span=("lp", "il")))
    t_uw = str(body.val(note_row, 2))
    body.put(note_row, keep=True)
    html_rows.append(dict(k="note", c={"lp": t_uw.replace("\n\n", " ").replace("\n", " ")}, span=("lp", "brt")))
    zal = ("Założenia: ceny netto z narzutami, poziom cen II kw. 2026 (Wrocław), bez waloryzacji; ilości wg modelu koncepcji; koszty "
           "stałe budowy – gr. 16; rezerwa na nieprzewidziane – gr. 18; ceny jednostkowe – kolumna pomocnicza J (poza wydrukiem). "
           f"Koszt Dokumentacji ≤ {pl(100 * LIMIT_USLUGI_PROC, 1)} % × {pl(LIMIT_KOSZTU / 1e6, 0)} mln zł = "
           f"{pl(LIMIT_USLUGI_PROC * LIMIT_KOSZTU / 1e6, 1)} mln zł netto (Reg. R.III ust. 4).")
    rr = body.put(note_row + 1, {"B": zal}, height=13.0 * xl_lines(zal, 100) + 4, merges=[(2, 8)])
    note_style(ws.cell(rr, 2))
    html_rows.append(dict(k="note", c={"lp": zal}, span=("lp", "brt")))
    body.put(note_row + 2)
    r_fn = body.put(fee_n, {"H": round(fee, 2) if fee is not None else None}, keep=True)
    r_fb = body.put(fee_b, {"H": f"=ROUND(H{r_fn}*(1+{VAT}),2)"}, keep=True)
    fee_b_v = xround(fee * (1 + VAT), 2) if fee is not None else None
    html_rows.append(dict(k="fee", c={"lp": str(body.val(fee_n, 2)), "brt": pl(fee, 2) if fee else "–"}, span=("lp", "net")))
    html_rows.append(dict(k="fee", c={"lp": str(body.val(fee_b, 2)), "brt": pl(fee_b_v, 2) if fee_b_v else "–"}, span=("lp", "net")))
    # kolumny pomocnicze J/K
    for c, t in ((10, "Cena jedn. netto [zł/j.m.] (pomocn.)"), (11, "Uwagi / pochodzenie ilości (pomocn.)")):
        ws.cell(6, c)._style = copy(ws.cell(6, 8)._style)
        ws.cell(6, c).value = t
    ws.column_dimensions["K"].width = 70
    if draft:
        ws.merge_cells("B5:H5")
        ws["B5"].value = "WERSJA ROBOCZA – PRZED REWIZJĄ KOSZTÓW"
        ws["B5"].font = Font(name="Calibri", sz=11, b=True, color="FFC00000")
        ws["B5"].alignment = Alignment(horizontal="center", vertical="center")
    ws.print_area = f"A1:H{body.r - 1}"
    path = OUT / "F.14.B.xlsx"
    save_clean(wb, path, "F.14.B Informacja o kosztach")
    res["F.14.B"] = dict(path=path, hdr=hdr, draft=draft, rev=rev, info=info, diffs=diffs, params=params, rows=out_rows, gsum=gsum,
                         totF=totF, totH=totH, model_total=model_total, extras_md=extras_md, fee=fee, fee_b=fee_b_v, fee_src=fee_src,
                         vat_fill=vat_fill, jm_fill=jm_fill, html=html_rows, km=km,
                         checks={f"F{rt}": totF, f"H{rt}": totH, **({f"H{r_fb}": fee_b_v} if fee_b_v else {})})


# =================================================================================================== HTML / PDF
CSS = """
@page { size: 420mm 297mm; margin: 0 }
* { box-sizing: border-box }
html, body { margin: 0; padding: 0; background: #fff; color: #000; font-family: Carlito, Calibri, 'Liberation Sans', sans-serif }
.page { width: 420mm; height: 297mm; padding: 9mm 10mm 7mm 10mm; position: relative; page-break-after: always; overflow: hidden }
.page:last-child { page-break-after: auto }
.hdr { border: 0.25mm solid #000; text-align: center; margin-bottom: 3.5mm }
.hdr .k { font-size: 7.6pt; padding: 1.2mm 4mm 0.6mm; line-height: 1.25 }
.hdr .t { font-size: 13pt; font-weight: 700; padding: 0.4mm 0 0.6mm; letter-spacing: 0.02em }
.hdr .z { font-size: 8pt; font-weight: 700; text-align: right; padding: 0 3mm 1mm }
.draft { position: absolute; top: 10.5mm; left: 12mm; color: #c00000; font-weight: 700; font-size: 9pt; letter-spacing: 0.03em }
.cols { display: flex; gap: 6mm; align-items: flex-start }
table { border-collapse: collapse; table-layout: fixed; font-size: 7.2pt; line-height: 3.25mm }
td, th { border: 0.15mm solid #222; padding: 0.35mm 0.9mm; vertical-align: top; overflow-wrap: anywhere }
th { background: #B4C7E7; font-weight: 700; text-align: center; vertical-align: middle }
tr.sec td { background: #D9D9D9; font-weight: 700 }
tr.grp td { background: #D9D9D9; font-weight: 700 }
tr.sum td { background: #D9D9D9; font-weight: 700 }
tr.grand td { background: #92D050; font-weight: 700 }
tr.fee td { font-weight: 700; background: #F2F2F2 }
tr.note td { border: none; font-style: italic; font-size: 6.6pt; color: #333; padding-top: 0.8mm }
tr.gap td { border: none; height: 1.2mm; padding: 0 }
.r { text-align: right; white-space: nowrap } .c { text-align: center } .l { text-align: left }
.foot { position: absolute; bottom: 4mm; left: 10mm; right: 10mm; font-size: 6.8pt; color: #555; display: flex; justify-content: space-between }
"""
FS_PT, LH_MM, PADV = 7.2, 3.25, 1.0


def est_lines(text, w_mm, bold=False, italic=False, fs=FS_PT):  # noqa: ARG001
    cw = fs * 0.3528 * (0.50 if bold else 0.47)
    cap = max(1, int((w_mm - 2.0) / cw * 0.94))
    return xl_lines(text, cap)


def row_h(row, cols, base=FS_PT):
    if row["k"] == "gap":
        return 1.6
    span = row.get("span")
    keys = [c["key"] for c in cols]
    w = {c["key"]: c["w"] for c in cols}
    cells = []
    if span:
        i0, i1 = keys.index(span[0]), keys.index(span[1])
        cells.append((row["c"].get(span[0], ""), sum(w[k] for k in keys[i0:i1 + 1])))
        for k in keys[:i0] + keys[i1 + 1:]:
            cells.append((row["c"].get(k, ""), w[k]))
    else:
        cells = [(row["c"].get(k, ""), w[k]) for k in keys]
    bold = row["k"] in ("sec", "grp", "sum", "grand", "fee")
    fs = base * (6.6 / FS_PT if row["k"] == "note" else 1.0)
    n = max(est_lines(t, ww, bold, fs=fs) for t, ww in cells) if cells else 1
    return n * (LH_MM * fs / FS_PT) + PADV * base / FS_PT + (0.8 if row["k"] == "note" else 0)


def td_html(row, cols):
    keys = [c["key"] for c in cols]
    span = row.get("span")
    out, i = [], 0
    while i < len(keys):
        k = keys[i]
        col = cols[i]
        if span and k == span[0]:
            i1 = keys.index(span[1])
            n = i1 - i + 1
            al = "l"
            out.append(f'<td colspan="{n}" class="{al}">{html.escape(str(row["c"].get(k, "")))}</td>')
            i = i1 + 1
            continue
        al = col.get("al", "l")
        out.append(f'<td class="{al}">{html.escape(str(row["c"].get(k, "")))}</td>')
        i += 1
    return "".join(out)


def render_html(code, hdr, blocks, ncols, draft=None, gap=6.0, fs=FS_PT):
    avail = 297 - 9 - 7 - 22.5 - 6
    pages, page, col, used = [], [], None, 0.0

    def close_col():
        nonlocal page, col
        if col and col["rows"]:
            page.append(col)
            if len(page) == ncols:
                pages.append(page)
                page = []
        col = None

    for cols, rows in blocks:
        close_col()
        th_h = max(est_lines(c["label"], c["w"], True, fs=fs) for c in cols) * LH_MM * fs / FS_PT + PADV + 0.6
        for i, row in enumerate(rows):
            h = row_h(row, cols, fs)
            need = h + (row_h(rows[i + 1], cols, fs) if row["k"] == "sec" and i + 1 < len(rows) else 0)
            if col is None:
                col, used = dict(cols=cols, rows=[]), th_h
            if used + need > avail and col["rows"]:
                close_col()
                col, used = dict(cols=cols, rows=[]), th_h
            if row["k"] == "gap" and not col["rows"]:
                continue
            col["rows"].append(row)
            used += h
    close_col()
    if page:
        pages.append(page)
    n = len(pages)
    sc = (f"table{{font-size:{fs}pt;line-height:{LH_MM * fs / FS_PT:.2f}mm}} tr.note td{{font-size:{6.6 * fs / FS_PT:.2f}pt}} "
          f"td,th{{padding:{0.35 * fs / FS_PT:.2f}mm 0.9mm}}") if fs != FS_PT else ""
    parts = [f'<!doctype html><html lang="pl"><head><meta charset="utf-8"><title>{html.escape(code)}</title><style>{CSS}{sc}</style></head><body>']
    for pi, pg in enumerate(pages, 1):
        parts.append('<section class="page">')
        if draft:
            parts.append(f'<div class="draft">{html.escape(draft)}</div>')
        parts.append(f'<div class="hdr"><div class="k">{html.escape(hdr[0]).replace(chr(10), "<br>")}</div>'
                     f'<div class="t">{html.escape(hdr[1]).replace(chr(10), "<br>")}</div><div class="z">{html.escape(hdr[2])}</div></div>')
        parts.append('<div class="cols">')
        for c in pg:
            cols = c["cols"]
            wsum = sum(x["w"] for x in cols)
            parts.append(f'<table style="width:{wsum}mm"><colgroup>' + "".join(f'<col style="width:{x["w"]}mm">' for x in cols)
                         + "</colgroup><thead><tr>" + "".join(f"<th>{html.escape(x['label'])}</th>" for x in cols) + "</tr></thead><tbody>")
            for row in c["rows"]:
                parts.append(f'<tr class="{row["k"]}">' + ("<td colspan=\"%d\"></td>" % len(cols) if row["k"] == "gap" else td_html(row, cols)) + "</tr>")
            parts.append("</tbody></table>")
        parts.append("</div>")
        parts.append(f'<div class="foot"><span>{html.escape(code)} – {html.escape(hdr[1].splitlines()[0])}</span><span>strona {pi} / {n}</span></div>')
        parts.append("</section>")
    parts.append("</body></html>")
    return "".join(parts), n


def html_blocks(res):
    A = [dict(key="nr", label="nr", w=21, al="l"), dict(key="opis", label="opis", w=77, al="l"),
         dict(key="kond", label="kond.", w=13, al="c"), dict(key="pow", label="pow. [m2]", w=18, al="r")]
    B = [dict(key="nr", label="nr", w=21, al="l"), dict(key="opis", label="opis", w=90, al="l"), dict(key="pow", label="pow. [m2]", w=18, al="r")]
    C1 = [dict(key="nr", label="nr", w=14, al="c"), dict(key="opis", label="opis", w=153, al="l"), dict(key="pow", label="pow. [m2]", w=30, al="r")]
    C2 = [dict(key="nr", label="nr", w=14, al="c"), dict(key="opis", label="opis", w=131, al="l"), dict(key="jedn", label="jednostka", w=22, al="c"),
          dict(key="ilosc", label="ilość", w=30, al="r")]
    E = [dict(key="lp", label="L.p.", w=12, al="c"), dict(key="opis", label="Opis", w=90, al="l"), dict(key="il", label="Ilość", w=19, al="r"),
         dict(key="jm", label="J.m.", w=12, al="c"), dict(key="net", label="Wartość [netto] zł", w=27, al="r"),
         dict(key="vat", label="VAT", w=10, al="c"), dict(key="brt", label="Wartość [brutto] zł", w=27, al="r")]
    return {
        "F.15.A": ([(A, res["F.15.A"]["rows_html"])], 3, None, FS_PT),
        "F.15.B": ([(B, res["F.15.B"]["rows_html"])], 3, None, FS_PT),
        "F.15.C": ([(C1, res["F.15.C"]["html"][0]), (C2, res["F.15.C"]["html"][1])], 2, None, 9.6),
        "F.14.B": ([(E, res["F.14.B"]["html"])], 2, "WERSJA ROBOCZA – PRZED REWIZJĄ KOSZTÓW" if res["F.14.B"]["draft"] else None, FS_PT),
    }


def lo_profile(tmp):
    return f"-env:UserInstallation=file://{Path(tmp) / 'lo_profile'}"


def render_pdfs(res, log):
    hd = OUT / "_html"
    hd.mkdir(parents=True, exist_ok=True)
    out = {}
    for code, (blocks, ncols, draft, fs) in html_blocks(res).items():
        doc, n = render_html(code, res[code]["hdr"], blocks, ncols, draft, fs=fs)
        hp = hd / f"{code}.html"
        hp.write_text(doc, encoding="utf-8")
        pdf = OUT / f"{code}.pdf"
        ok, how = False, ""
        if shutil.which("node") and HTML2PDF.exists():
            try:
                p = subprocess.run(["node", str(HTML2PDF), str(hp), str(pdf), "420", "297"], cwd=ROOT, capture_output=True, text=True, timeout=600)
                ok, how = (p.returncode == 0 and pdf.exists()), "HTML → html2pdf.js (Chromium)"
                if not ok:
                    log.append(f"{code}: html2pdf.js nie powiodło się: {p.stderr[-300:]}")
            except Exception as e:  # noqa: BLE001
                log.append(f"{code}: html2pdf.js: {e}")
        if not ok and shutil.which("soffice"):
            ok, how = lo_pdf(res[code]["path"], pdf, log), "LibreOffice (xlsx → pdf, A3 poziomo)"
        out[code] = dict(pdf=pdf if ok else None, pages=n, how=how)
    return out


def lo_pdf(xlsx, pdf, log):
    with tempfile.TemporaryDirectory() as tmp:
        wb = openpyxl.load_workbook(xlsx)
        ws = wb.active
        ws.page_setup.paperSize = 8
        ws.page_setup.orientation = "landscape"
        src = Path(tmp) / xlsx.name
        wb.save(src)
        p = subprocess.run(["soffice", lo_profile(tmp), "--headless", "--norestore", "--convert-to", "pdf", "--outdir", tmp, str(src)],
                           capture_output=True, text=True, timeout=600)
        q = Path(tmp) / (xlsx.stem + ".pdf")
        if q.exists():
            shutil.copy(q, pdf)
            return True
        log.append(f"LibreOffice PDF {xlsx.name}: {p.stderr[-300:]}")
        return False


def lo_verify(res, log):
    """Otwarcie i przeliczenie każdego xlsx w LibreOffice; porównanie wyników formuł z wartościami z Pythona."""
    out = {}
    if not shutil.which("soffice"):
        return None
    with tempfile.TemporaryDirectory() as tmp:
        files = [str(res[c]["path"]) for c in TEMPLATES]
        p = subprocess.run(["soffice", lo_profile(tmp), "--headless", "--norestore", "--convert-to", "xlsx", "--outdir", str(Path(tmp) / "lo"),
                            *files], capture_output=True, text=True, timeout=900)
        for c in TEMPLATES:
            q = Path(tmp) / "lo" / res[c]["path"].name
            if not q.exists():
                out[c] = dict(ok=False, err=(p.stderr or p.stdout)[-300:], cells=[])
                continue
            ws = openpyxl.load_workbook(q, data_only=True).active
            cells = []
            for ref, exp in res[c]["checks"].items():
                got = ws[ref].value
                okc = isinstance(got, (int, float)) and exp is not None and abs(got - exp) < 0.015
                cells.append((ref, exp, got, okc))
            out[c] = dict(ok=all(x[3] for x in cells), cells=cells, err="")
    return out


def pdf_check(res, pdfs):
    out = {}
    for code in ("F.15.A", "F.15.B"):
        pdf = pdfs.get(code, {}).get("pdf")
        if not pdf or not shutil.which("pdftotext"):
            continue
        txt = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        toks = set(re.findall(r"[A-Z]{1,4}\.[A-Za-z0-9.\-]+", txt))
        nums = [r["numer"] for r in res[code]["rows_html"] if r.get("numer")]
        miss = [x for x in nums if x not in toks]
        out[code] = (len(nums), miss)
    return out


# =================================================================================================== rzuty (SVG)
def plan_check(D):
    fid = {"-2": "m2", "-1": "m1", "P": "P", "S": "S", "ANT": "S_antresola", "D": "dach"}
    try:
        m = re.search(r"FILE_ID\s*=\s*(\{[^}]*\})", P["rzuty_py"].read_text(encoding="utf-8"))
        fid = ast.literal_eval(m.group(1))
    except Exception:  # noqa: BLE001
        pass
    codes = {r["kod"] for r in D.rooms} | set(D.blocks) | {"D"}
    bud_mtime = P["bud"].stat().st_mtime
    out = []
    for s in D.storeys:
        f = RZUTY_DIR / f"rzut_{fid.get(s['id'], s['id'])}_1-200.svg"
        rs = [r for r in D.rooms if r["st"] == s["id"]]
        if not f.exists():
            out.append(dict(id=s["id"], file=None, n=len(rs)))
            continue
        txt = f.read_text(encoding="utf-8")
        texts = [html.unescape(re.sub(r"<[^>]+>", "", t)).strip() for t in re.findall(r"<text\b[^>]*>(.*?)</text>", txt, re.S)]
        exact, ranges = set(), []
        for t in texts:
            if re.fullmatch(r"[A-Z]{1,4}\.[A-Za-z0-9.\-]+", t):
                exact.add(t)
            m = re.fullmatch(r"([A-Z]{1,4}\.[A-Za-z0-9.\-]+)–([A-Za-z0-9]+)", t)
            if m:
                ranges.append((m.group(1), m.group(1).rsplit(".", 1)[0] + "." + m.group(2)))
            m = re.fullmatch(r"([A-Z]{1,4}\.[A-Za-z0-9.\-]+)…([A-Z]{1,4}\.[A-Za-z0-9.\-]+)", t)
            if m:
                ranges.append((m.group(1), m.group(2)))

        def covered(nm):
            if nm in exact:
                return True
            for a, b in ranges:
                if a.rsplit(".", 1)[0] == nm.rsplit(".", 1)[0] and nat(a) <= nat(nm) <= nat(b):
                    return True
            return False

        nums = {r["numer"] for r in rs}
        miss = sorted([r["numer"] for r in rs if not covered(r["numer"])], key=nat)
        extra = sorted([t for t in exact if t.split(".")[0] in codes and t not in nums], key=nat)
        lm = re.search(r"Razem (?:powierzchnia netto kondygnacji|pola dachowe w obrysie attyk):\s*([\d\s  ]+,\d+)", " ".join(texts))
        leg = num_pl(lm.group(1)) if lm else None
        out.append(dict(id=s["id"], file=f, n=len(rs), miss=miss, extra=extra, legend=leg,
                        stale=f.stat().st_mtime < bud_mtime, total=round(sum(r["pow"] or 0 for r in rs), 2)))
    return out


# =================================================================================================== kontrola.md
def md_table(head, rows, al=None):
    al = al or ["l"] + ["r"] * (len(head) - 1)
    sep = ["---:" if a == "r" else (":---:" if a == "c" else "---") for a in al]
    return "\n".join(["| " + " | ".join(head) + " |", "| " + " | ".join(sep) + " |"] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def kontrola(D, res, plans, lo, pdfs, pdfchk, log):
    L, issues = [], []
    ok = lambda b: "✔" if b else "✖"  # noqa: E731

    def issue(sev, txt):
        issues.append((sev, txt))

    A, B, C, F = res["F.15.A"], res["F.15.B"], res["F.15.C"], res["F.14.B"]
    S, K = C["S"], C["K"]
    net = D.net_rooms()
    L.append("# Kontrola tabel konkursowych F.15.A / F.15.B / F.15.C / F.14.B\n")
    L.append("Wygenerowano: `python3 -I tools/tabele_konkursowe.py` (generator idempotentny; dane czytane przy każdym uruchomieniu). "
             "Δ = wartość w tabeli − wartość odniesienia. ✔ zgodne, ✖ niespójność (szczegóły w ostatnim rozdziale).\n")
    L.append("## 1. Źródła (wersje plików – skrót SHA-1)\n")
    src = [("model/budynek.json", P["bud"]), ("model/koncepcja.json", P["kon"]), ("model/site.json", P["site"]),
           ("docs/20_program/program.yaml", P["prog"]), ("tools/koszty_model.py", P["km"]),
           ("docs/20_koncepcja/_weryfikacja_koszt_eko.py", P["wer"]), ("docs/20_koncepcja/koncepcja_wybrana.md", P["kmd"]),
           ("tools/zagospodarowanie.py", P["zag"])]
    L.append(md_table(["plik", "sha1"], [(f"`{a}`", f"`{sha(b)}`") for a, b in src], ["l", "l"]))
    rv = find_revision()
    other = [rel(x) for x in sorted((ROOT / "docs" / "20_koncepcja").glob("_rewizja_*.py")) if x not in rv]
    L.append(f"\nSkrypt rewizji kosztów `_rewizja_*.py`: {'**' + F['rev'] + '**' if F['rev'] else ('znaleziono ' + ', '.join(rel(x) for x in rv) + ' – bez odczytywalnych pozycji F.14.B' if rv else 'brak')}"
             + (f" (inne skrypty rewizji, nie dotyczą kosztów: {', '.join(other)})" if other else "") + ". "
             f"Rejestr poprawek v1.1: {'istnieje' if P['rej'].exists() else 'brak'}"
             + (f" (pozycje ⏳ w toku: {len(re.findall('⏳', P['rej'].read_text(encoding='utf-8')))})" if P["rej"].exists() else "") + ".")
    if F["draft"]:
        L.append("**F.14.B oznaczono „WERSJA ROBOCZA – PRZED REWIZJĄ KOSZTÓW”** (liczby z `tools/koszty_model.py`, poziom mid).")
    # ------------------------------------------------------------------ sumy kluczowe
    L.append("\n## 2. Sumy kluczowe\n")
    rows = [("F.15.A – RAZEM BUDYNEK (netto)", pl(A["total"]) + " m²"),
            ("F.15.A – w tym PU / RU / US / PG", " / ".join(pl(A["kat"].get(k, 0)) for k in ("PU", "RU", "US", "PG")) + " m²"),
            ("F.15.B – RAZEM (bez dachu)", pl(B["total"]) + " m²"),
            ("F.15.C – Obszar inwestycji / PZ / utwardzone / PBC teren / PBC dachy", " / ".join(pl(x) for x in (S["OI"], S["PZ"], S["utw"], S["pbc_ground"], S["pbc_dach"])) + " m²"),
            ("F.15.C – PC nadziemna / podziemna / razem", " / ".join(pl(x) for x in (K["PC_nad"], K["PC_pod"], K["PC_nad"] + K["PC_pod"])) + " m²"),
            ("F.15.C – PU (I.12) / KW (I.8)", f"{pl(K['kat_PU'])} m² / {pl(K['KW'], 0)} m³"),
            ("F.14.B – koszt realizacji netto / brutto", f"{pl(F['totF'])} zł / {pl(F['totH'])} zł"),
            ("F.14.B – koszt usługi netto / brutto", f"{pl(F['fee'])} zł / {pl(F['fee_b'])} zł" if F["fee"] else "brak")]
    L.append(md_table(["wielkość", "wartość"], rows, ["l", "r"]))
    # ------------------------------------------------------------------ program vs projekt
    L.append("\n## 3. Liczba pomieszczeń i powierzchnia grup – program (M.01, `program.yaml`) vs projekt (`budynek.json`)\n")
    rows = []
    groups = [s["code"] for s in A["sec_rows"]]
    for code in groups:
        blk = D.blocks.get(code)
        rs = [r for r in net if r["kod"] == code]
        pn = sum(it.get("liczba") or 0 for it in blk["pomieszczenia"]) if blk else None
        pa = blk.get("pow_suma") if blk else None
        ma = round(sum(r["pow"] or 0 for r in rs), 2)
        dn = len(rs) - pn if pn is not None else None
        da = ma - pa if pa is not None else None
        flag = ""
        if code == "KW":
            flag = "pozycja zbiorcza – liczba n/d"
        elif pa and abs(da) / pa > 0.10:
            flag = "Δ pow. > 10 %"
        rows.append((code, pn if pn is not None else "–", len(rs), dpl(dn, 0) if dn is not None else "–", pl(pa, 0) if pa else "–",
                     pl(ma), dpl(da) if da is not None else "–", (pl(100 * da / pa, 1) + " %") if pa else "–", flag))
    tp = sum(b.get("pow_suma") or 0 for b in D.blocks.values())
    rows.append(("**RAZEM**", "", len(net), "", pl(tp, 0), pl(A["total"]), dpl(A["total"] - tp), pl(100 * (A["total"] - tp) / tp, 1) + " %", ""))
    L.append(md_table(["grupa", "program szt.", "projekt szt.", "Δ szt.", "program m²", "projekt m²", "Δ m²", "Δ %", "uwaga"], rows,
                      ["l", "r", "r", "r", "r", "r", "r", "r", "l"]))
    big = [r for r in rows[:-1] if r[8] == "Δ pow. > 10 %"]
    if big:
        issue("ISTOTNE", "Powierzchnia grup odbiega od programu o > 10 %: " + ", ".join(f"{r[0]} ({r[6]} m², {r[7]})" for r in big) + ".")
    # pozycje programu
    cnt, area = defaultdict(int), defaultdict(float)
    for r in net:
        bp = D.base_pid(r["prog_id"])
        if bp in D.items:
            cnt[bp] += 1
            area[bp] += r["pow"] or 0
    rows = []
    for pid, (kod, it) in D.items.items():
        n = it.get("liczba") or 0
        if cnt[pid] != n and kod != "KW":
            parts = [r["numer"] for r in net if D.base_pid(r["prog_id"]) == pid]
            com = "brak w modelu (sprawdzić, czy ujęte w innym pomieszczeniu)" if not parts else (
                f"zrealizowane jako {len(parts)} części" if n == 1 else "inna liczba pomieszczeń niż w programie")
            rows.append((f"`{pid}`", it["nazwa"][:70], n, cnt[pid], pl(it.get("pow_laczna") or 0, 0), pl(area[pid]), com))
    L.append("\nPozycje programu, których liczba w projekcie różni się od programu:\n")
    L.append(md_table(["id", "nazwa (program)", "program", "projekt", "program m²", "projekt m²", "komentarz"], rows,
                      ["l", "l", "r", "r", "r", "r", "l"]) if rows else "brak")
    missing = [r for r in rows if r[3] == 0]
    if missing:
        issue("ISTOTNE", "Pozycje programu bez odpowiednika (wg prog_id) w modelu: " + ", ".join(f"{r[0]} {r[1][:40]}" for r in missing) + ".")
    # ------------------------------------------------------------------ F.15.B vs budynek, poligony, rzuty
    L.append("\n## 4. F.15.B per kondygnacja = suma pomieszczeń w `budynek.json`; obrysy; legenda rzutów\n")
    rows = []
    for sr in B["storey_rows"]:
        rs = [r for r in D.rooms if r["st"] == sr["id"]]
        sb = round(sum(r["pow"] or 0 for r in rs), 2)
        sp = round(sum(r["pow_poly"] for r in rs), 2)
        pc = next((p for p in plans if p["id"] == sr["id"]), {})
        leg = pc.get("legend")
        rows.append((D.sid[sr["id"]]["title"], sr["n"], pl(sr["pow"]), pl(sb), dpl(sr["pow"] - sb), pl(sp), dpl(sr["pow"] - sp),
                     pl(leg, 1) if leg is not None else "–", dpl(round(sr["pow"], 1) - leg, 1) if leg is not None else "–",
                     ok(abs(sr["pow"] - sb) < 0.01 and (leg is None or abs(round(sr["pow"], 1) - leg) < 0.15))))
    L.append(md_table(["kondygnacja", "szt.", "F.15.B", "budynek.json", "Δ", "z poligonów", "Δ poligon", "legenda rzutu", "Δ rzut", ""], rows,
                      ["l", "r", "r", "r", "r", "r", "r", "r", "r", "c"]))
    dpoly = [(r["numer"], r["pow"], round(r["pow_poly"], 2)) for r in D.rooms if r["pow"] is not None and abs(r["pow"] - r["pow_poly"]) > 0.05]
    nopow = [r["numer"] for r in D.rooms if not r["pow"]]
    L.append(f"\nPowierzchnie z `powierzchnia` vs pole poligonu (shapely): {len(dpoly)} pomieszczeń z |Δ| > 0,05 m²"
             + (": " + ", ".join(f"{a} ({pl(b)} vs {pl(c)})" for a, b, c in dpoly[:15]) if dpoly else " ✔")
             + (f"; bez powierzchni: {', '.join(nopow)}" if nopow else "") + ".")
    if dpoly:
        issue("INFO", f"{len(dpoly)} pomieszczeń: powierzchnia w budynek.json ≠ pole poligonu o > 0,05 m².")
    legbad = [r for r in rows if r[8] not in ("–",) and r[9] == "✖"]
    if legbad:
        issue("ISTOTNE", "Suma powierzchni w legendzie rzutu ≠ F.15.B: " + ", ".join(f"{r[0]} ({r[8]} m²)" for r in legbad) + ".")
    # ------------------------------------------------------------------ F.15.A = F.15.B
    L.append("\n## 5. F.15.A = F.15.B\n")
    d = A["total"] - B["total"]
    L.append(f"RAZEM F.15.A {pl(A['total'])} m² − RAZEM F.15.B {pl(B['total'])} m² = **{dpl(d)} m²** {ok(abs(d) < 0.01)}; "
             f"liczba pozycji: F.15.A {sum(s['n'] for s in A['sec_rows'])}, F.15.B (bez dachu) "
             f"{sum(x['n'] for x in B['storey_rows'] if not x['roof'])}. Pola dachowe ({pl(sum(x['pow'] for x in B['storey_rows'] if x['roof']))} m²) "
             "wykazano tylko w F.15.B (sekcja DACH, poza sumą).")
    if abs(d) >= 0.01:
        issue("KRYT", f"F.15.A ≠ F.15.B ({dpl(d)} m²).")
    # ------------------------------------------------------------------ numeracja
    L.append("\n## 6. Numeracja (R-118, R-217): unikalność, wzorzec „kod grupy + numer kolejny”, zgodność z rzutami\n")
    allnum = [r["numer"] for r in D.rooms]
    dup = sorted({x for x in allnum if allnum.count(x) > 1}, key=nat)
    empty = sum(1 for x in allnum if not x)
    bad = []
    for r in D.rooms:
        if r["kind"] == "roof":
            continue
        if not r["numer"].startswith(r["kod"] + "."):
            bad.append((r["numer"], f"prefiks ≠ kod grupy {r['kod']}"))
            continue
        rest = r["numer"][len(r["kod"]) + 1:]
        if not re.fullmatch(r"\d{2}[a-z]?|[-A-Z0-9]+\.\d{2}", rest):
            bad.append((r["numer"], "człon po kodzie nie jest numerem kolejnym"))
    L.append(f"- unikalność: {len(allnum)} numerów, duplikaty: {', '.join(dup) if dup else 'brak'} {ok(not dup)}; puste numery: {empty} {ok(not empty)}")
    L.append(f"- wzorzec: {len(bad)} odstępstw" + (": " + ", ".join(f"`{a}` ({b})" for a, b in bad) if bad else " ✔"))
    if dup:
        issue("KRYT", "Zdublowane numery pomieszczeń: " + ", ".join(dup))
    if bad:
        issue("ISTOTNE", "Numery niezgodne z zasadą „kod grupy + numer kolejny” (R-217): " + ", ".join(a for a, _ in bad) + ".")
    rows = []
    for p in plans:
        if p.get("file") is None:
            rows.append((D.sid[p["id"]]["title"], "brak pliku", p["n"], "–", "–", "–"))
            continue
        rows.append((D.sid[p["id"]]["title"], f"`{rel(p['file'])}`" + (" (starszy niż budynek.json)" if p["stale"] else ""), p["n"],
                     (", ".join(p["miss"][:12]) + (" …" if len(p["miss"]) > 12 else "")) if p["miss"] else "✔",
                     ", ".join(p["extra"][:12]) if p["extra"] else "✔", ok(not p["miss"] and not p["extra"] and not p["stale"])))
    L.append("\nZgodność z rzutami 1:200 (`build/rzuty/*.svg`: etykiety na rzucie + zakresy w legendzie):\n")
    L.append(md_table(["kondygnacja", "rzut", "pomieszczeń", "brak na rzucie", "na rzucie, brak w modelu", ""], rows, ["l", "l", "r", "l", "l", "c"]))
    pm = [p for p in plans if p.get("miss")]
    if pm:
        issue("ISTOTNE", "Numery z modelu nieodnalezione na rzutach: " + "; ".join(f"{p['id']}: {', '.join(p['miss'][:8])}" for p in pm) + ".")
    pe = [p for p in plans if p.get("extra")]
    if pe:
        issue("ISTOTNE", "Numery na rzutach bez pomieszczenia w modelu: " + "; ".join(f"{p['id']}: {', '.join(p['extra'][:8])}" for p in pe) + ".")
    ps = [p["id"] for p in plans if p.get("stale")]
    if ps:
        issue("INFO", "Rzuty SVG starsze niż budynek.json (wygenerować ponownie tools/rzuty.py): " + ", ".join(ps) + ".")
    # rozproszenie departamentów
    dept = [c for c in groups if any(it.get("komorka") for it in D.blocks.get(c, {}).get("pomieszczenia", []))]
    rows = []
    for c in dept:
        ids = sorted({r["sidx"] for r in net if r["kod"] == c})
        if not ids:
            continue
        adj = len(ids) <= 2 and (len(ids) == 1 or ids[1] - ids[0] == 1)
        if not adj:
            det = ", ".join(f"{D.storeys[i]['id']} ({pl(sum(r['pow'] for r in net if r['kod'] == c and r['sidx'] == i), 1)} m²)" for i in ids)
            rows.append((c, det))
    if rows:
        L.append("\nDepartamenty/komórki na więcej niż 2 kondygnacjach lub niesąsiednich (Wyj. 17 odp. 70 dopuszcza 2 sąsiednie): "
                 + "; ".join(f"**{a}**: {b}" for a, b in rows) + ".")
        issue("ISTOTNE", "Rozproszenie grup na kondygnacjach (Wyj. 17 odp. 70): " + "; ".join(f"{a}: {b}" for a, b in rows) + ".")
    # ------------------------------------------------------------------ PU
    L.append("\n## 7. F.15.C – PU (I.12) vs `koncepcja.bilans.PU_m2`\n")
    pu_k = D.kon["bilans"].get("PU_m2")
    dpu = K["kat_PU"] - pu_k
    L.append(f"I.12 = suma pomieszczeń kategorii PU (PN-ISO 9836; kategorie pozycji programu) = **{pl(K['kat_PU'])} m²**; "
             f"koncepcja.bilans.PU_m2 = {pl(pu_k)} m² (wartość szacunkowa „≈” z rozdz. 12 koncepcji) → **Δ = {dpl(dpu)} m² "
             f"({pl(100 * dpu / pu_k, 1)} %)** {ok(abs(dpu) / pu_k < 0.01)}.\n")
    comp = md_pu(D.kmd)
    pu = [r for r in net if r["kat"] == "PU"]
    mapf = [("pokoje", lambda r: r["kind"] == "office"), ("KS", lambda r: r["kod"] == "KS" and r["kind"] != "office"),
            ("Sejmik", lambda r: r["kod"] == "SWD"), ("konferencje", lambda r: r["kod"] == "SK"), ("strefa wejściowa", lambda r: r["kod"] == "SW"),
            ("sale narad", lambda r: r["kod"] == "SN"), ("socjalne", lambda r: r["kod"] == "PS"), ("pomocnicze", lambda r: r["kod"] == "PP"),
            ("WC", lambda r: r["kod"] == "PHS"), ("rowery", lambda r: r["kod"] == "PR"), ("PPT", lambda r: r["kod"] == "PPT")]
    used = set()
    rows = []
    for lab, val in comp:
        f = next((fn for k, fn in mapf if lab.lower().startswith(k.lower())), None)
        if f:
            sel = [r for r in pu if f(r) and id(r) not in used]
            used |= {id(r) for r in sel}
            mv = round(sum(r["pow"] for r in sel), 2)
            rows.append((lab, pl(val, 0), pl(mv), dpl(mv - val)))
        else:
            rows.append((lab, pl(val, 0), "–", "–"))
    rest = [r for r in pu if id(r) not in used]
    if rest:
        byk = defaultdict(float)
        for r in rest:
            byk[r["kod"]] += r["pow"]
        rows.append(("pozostałe PU w modelu (" + ", ".join(f"{k} {pl(v, 1)}" for k, v in sorted(byk.items())) + ")", "–",
                     pl(sum(byk.values())), dpl(sum(byk.values()))))
    rows.append(("**RAZEM**", pl(sum(v for _, v in comp), 0) if comp else "–", pl(K["kat_PU"]), dpl(K["kat_PU"] - (sum(v for _, v in comp) if comp else pu_k))))
    L.append(md_table(["składnik PU (rozbicie koncepcji)", "koncepcja", "model (F.15.A)", "Δ"], rows))
    L.append("\nWyjaśnienie: różnica wynika z (1) szacunkowego charakteru PU w koncepcji (zaokrąglone składniki), (2) przypisania kategorii "
             "z programu: hole SW.01, SK.06, SWD.02 i rampy = RU, IT = US (oprócz IT.14 odpady = PU), garaż = PG, (3) pomieszczeń "
             "dodanych w modelu (np. pokoje oczekiwania, wnęki MFP, zaplecza MDS) oraz rzeczywistych pól z poligonów.")
    if abs(dpu) / pu_k >= 0.01:
        issue("ISTOTNE", f"PU z pomieszczeń ({pl(K['kat_PU'])} m²) ≠ koncepcja.bilans.PU_m2 ({pl(pu_k)} m²), Δ {dpl(dpu)} m² – zaktualizować bilans/opis.")
    # ------------------------------------------------------------------ PC / PZ / KW
    L.append("\n## 8. Powierzchnia całkowita, zabudowy, kubatura – bilans koncepcji vs model\n")
    pcm = {s["id"]: s["plyta"] for s in D.storeys}
    nad = sum(s["plyta"] for s in D.storeys if not s["roof"] and not s["mezz"] and (s["rzedna"] or 0) >= 0)
    pod = sum(s["plyta"] for s in D.storeys if s["rzedna"] is not None and s["rzedna"] < 0)
    ant_rooms = [r for r in D.rooms if D.sid[r["st"]]["mezz"]]
    ant_pc = (D.kon.get("kondygnacja_sejmiku") or {}).get("antresola", {}).get("pow_m2")
    nad_t = nad + (ant_pc or 0)
    rows = [("PC nadziemna (płyty P…S + antresola wg koncepcji)", pl(K["PC_nad"]), pl(nad_t), dpl(K["PC_nad"] - nad_t)),
            ("PC podziemna (płyty −2, −1)", pl(K["PC_pod"]), pl(pod), dpl(K["PC_pod"] - pod)),
            ("PZ (bilans) vs obrys płyty kondygnacji 1 / suma rzutów brył", pl(K["PZ"]),
             f"{pl(max(s['plyta'] for s in D.storeys if not s['roof'] and (s['rzedna'] or 0) >= 0))} / "
             f"{pl(sum(b.get('pow_rzutu_m2') or 0 for b in D.kon['bryly']))}",
             dpl(K["PZ"] - sum(b.get("pow_rzutu_m2") or 0 for b in D.kon["bryly"]))),
            ("PZ – geometria (bryły ∩ Obszar inwestycji, shapely)", pl(K["PZ"]), pl(S["geo"]["bld"].intersection(S["geo"]["inv"]).area) if S.get("geo") else "–",
             dpl(K["PZ"] - S["geo"]["bld"].intersection(S["geo"]["inv"]).area) if S.get("geo") else "–")]
    L.append(md_table(["wielkość", "F.15.C (koncepcja)", "model", "Δ"], rows))
    if abs(K["PC_nad"] - nad_t) > 1 or abs(K["PC_pod"] - pod) > 1:
        issue("INFO", f"PC w bilansie koncepcji ≠ płyty w budynek.json: nadziemna Δ {dpl(K['PC_nad'] - nad_t)} m², podziemna Δ {dpl(K['PC_pod'] - pod)} m² "
                      f"(parter: płyta {pl(pcm.get('P', 0))} m²).")
    ant_net = sum(r["pow"] or 0 for r in ant_rooms)
    ant_kw = sum(r["pow"] or 0 for r in ant_rooms if r["kod"] == "KW")
    if ant_pc and ant_net > ant_pc + 0.5:
        L.append(f"\nAntresola: suma netto pomieszczeń {pl(ant_net)} m² > PC antresoli {pl(ant_pc)} m² (koncepcja) – w tym {pl(ant_kw)} m² "
                 "trzonów (KW.A.*), które dublują trzony kondygnacji S (szyby i klatki liczone drugi raz).")
        issue("ISTOTNE", f"Antresola: pomieszczenia KW.A.* ({pl(ant_kw)} m²) dublują trzony kondygnacji S – netto antresoli {pl(ant_net)} m² > PC {pl(ant_pc)} m²; "
                         "zawyża RAZEM F.15.A/F.15.B i powierzchnię ruchu.")
    # kubatura nadziemna – szacunek niezależny
    try:
        tops = [s for s in D.storeys if not s["roof"] and not s["mezz"] and (s["rzedna"] or 0) >= 0]
        Wd = next(b for b in D.kon["bryly"] if b["id"] == "W")["dach"]["najwyzszy_pkt_pokrycia"]["wzgl"]
        v = 0.0
        for i, s in enumerate(tops):
            h = (tops[i + 1]["rzedna"] - s["rzedna"]) if i + 1 < len(tops) else (Wd - s["rzedna"])
            v += s["plyta"] * h
        kv = K["KW"] - K["KW_pod"]
        L.append(f"\nKubatura nadziemna: I.9 = {pl(kv, 0)} m³ (= KW koncepcji − podziemna {pl(K['KW_pod'], 0)} m³); szacunek niezależny z płyt × wysokości "
                 f"kondygnacji (do najwyższego punktu pokrycia dachu dominanty) = {pl(v, 0)} m³ → Δ {dpl(kv - v, 0)} m³ ({pl(100 * (kv - v) / v, 1)} %; "
                 "różnica metody: attyki i warstwy dachów skrzydła/segmentu).")
    except Exception:  # noqa: BLE001
        pass
    # ------------------------------------------------------------------ teren
    L.append("\n## 9. Bilans terenu (Obszar inwestycji)\n")
    L.append(f"Źródło geometrii: {S['src']}. RAZEM = PZ + utwardzone + PBC na terenie = {pl(C['teren'])} m² vs pole Obszaru inwestycji "
             f"{pl(S['OI'])} m² → Δ {dpl(C['teren'] - S['OI'])} m² {ok(abs(C['teren'] - S['OI']) < 0.05)} (poz. 2.4 „place” domyka bilans – "
             f"zawiera też opaski przy budynku i różnicę PZ bilansu względem geometrii brył).")
    pbc_k = D.kon["bilans"].get("PBC_m2")
    L.append(f"\nPBC: teren {pl(S['pbc_ground'])} m² (ogródki zachowane {pl(S['pbc_istn'])} + ogród/trawniki {pl(S['pbc_rek'])}) + dachy "
             f"{pl(S['pbc_dach'])} m² ({pl(100 * PBC_DACH_WSP, 0)} % × {pl(S['green_roof'])} m² dachu zielonego D.*) = **{pl(S['pbc'])} m²** vs "
             f"koncepcja.bilans.PBC_m2 = {pl(pbc_k)} m² → Δ {dpl(S['pbc'] - pbc_k)} m² {ok(abs(S['pbc'] - pbc_k) < 5)}.")
    if abs(S["pbc"] - pbc_k) >= 5:
        issue("ISTOTNE", f"PBC z geometrii i dachów ({pl(S['pbc'])} m²) ≠ koncepcja.bilans.PBC_m2 ({pl(pbc_k)} m²), Δ {dpl(S['pbc'] - pbc_k)} m² "
                         "(koncepcja: ogród 1 139 m² + 50 % donic tarasu; model: taras D.03 opisany jako dach zielony intensywny).")
    if S["istn"] > 0:
        issue("INFO", f"Budynki istniejące w Obszarze inwestycji: {pl(S['istn'])} m² (poz. 1.2).")
    elif S.get("istn_raw", 0) > 0.005:
        L.append(f"\nPoz. 1.2 = 0: obrysy budynków sąsiednich (EGiB) nachodzą na granicę Obszaru inwestycji tylko na {pl(S['istn_raw'])} m² "
                 "(dokładność mapy) – pominięto.")
    g = S.get("geo")
    if g and g.get("og_paths", 0) + g.get("og_play", 0) > 1:
        L.append(f"\nZachowane ogródki przydomowe w Obszarze inwestycji: {pl(g['og_oi'])} m², z czego {pl(g['og_paths'] + g['og_play'])} m² "
                 "przykrywają ścieżki/plac zabaw z planu zagospodarowania (w bilansie liczone jako utwardzone).")
        issue("ISTOTNE", f"Plan zagospodarowania: ścieżki ogrodowe przecinają zachowane ogródki przydomowe na {pl(g['og_paths'] + g['og_play'])} m² "
                         f"(z {pl(g['og_oi'])} m²) – sprzeczne z deklaracją ich zachowania (i ochroną stref korzeni drzew ogródków).")
    for n in S["notes"]:
        issue("INFO", n)
    # ------------------------------------------------------------------ parking / dźwigi
    L.append("\n## 10. Miejsca postojowe, dźwigi\n")
    mm = sum(s["miejsca"] for s in D.storeys)
    mo = sum(s["ozn"] for s in D.storeys)
    L.append(md_table(["wielkość", "F.15.C (koncepcja)", "model (budynek.json)", "Δ"],
                      [("miejsca postojowe", K["miejsca"], mm, dpl((K["miejsca"] or 0) - mm, 0)),
                       ("w tym OzN", K["ozn"], mo, dpl((K["ozn"] or 0) - mo, 0)),
                       ("dźwigi osobowe / osobowo-towarowe", f"{K['lifts_os']} / {K['lifts_tow']}", ", ".join(sorted(K["lifts"])), "–")]))
    if K["miejsca"] is not None and mm != K["miejsca"]:
        issue("KRYT", f"Miejsca postojowe: koncepcja {K['miejsca']} (F.15.C I.14, wymóg MPZP), na rzutach/modelu tylko {mm} "
                      f"({', '.join(f'{s['id']}: {s['miejsca']}' for s in D.storeys if s['miejsca'])})"
                      + (f"; OzN {mo} zamiast {K['ozn']}" if K["ozn"] is not None and mo != K["ozn"] else "") + ".")
    tf = [t for t in D.bud.get("testy", []) if not t.get("ok")]
    if tf:
        L.append("\nTesty wewnętrzne `budynek.json` niespełnione: " + "; ".join(f"{t['test']} ({t.get('szczegoly', '')})" for t in tf) + ".")
        for t in tf:
            issue("ISTOTNE", f"budynek.json – test niespełniony: {t['test']} ({t.get('szczegoly', '')}).")
    # ------------------------------------------------------------------ koszty
    L.append("\n## 11. F.14.B – koszt realizacji\n")
    kk = D.kon["bilans"].get("koszt_mln_netto")
    km_mid = D.kon["bilans"].get("koszt_model_F14B_mid_mln")
    tot = F["totF"]
    L.append("Źródło liczb: " + ("; ".join(F["info"])) + ".")
    if F["diffs"]:
        L.append("Parametry modelu kosztów nadpisane danymi z modelu (wartość spec. → model): "
                 + ", ".join(f"{k} {pl(a, 1)} → {pl(b, 1)}" for k, a, b in F["diffs"]) + ".")
    rows = [("Suma F.14.B (wiersz sumy) netto", pl(tot), "", ""),
            ("koncepcja.bilans.koszt_mln_netto", pl(kk * 1e6) if kk else "–", dpl(tot - kk * 1e6) if kk else "–", ok(kk and abs(tot - kk * 1e6) < 0.06e6)),
            ("koncepcja.bilans.koszt_model_F14B_mid_mln (bez korekt poza modelem)", pl(km_mid * 1e6) if km_mid else "–",
             dpl(F["model_total"] - km_mid * 1e6) if km_mid else "–", "model: " + pl(F["model_total"])),
            ("limit 150 mln zł netto (Wyj. 20 odp. 74)", pl(LIMIT_KOSZTU), dpl(tot - LIMIT_KOSZTU), ok(tot <= LIMIT_KOSZTU)),
            ("wskaźnik zł/m² PC", pl(tot / (K["PC_nad"] + K["PC_pod"]), 0), "", ""),
            ("wskaźnik zł/m² PU (I.12)", pl(tot / K["kat_PU"], 0), "", "")]
    L.append(md_table(["pozycja", "wartość [zł]", "Δ (F.14.B − odniesienie)", ""], rows, ["l", "r", "r", "l"]))
    rez = sum(r["F"] for r in F["rows"] if r["opis"] and re.search(r"rezerw", r["opis"], re.I))
    L.append(f"\nZapas do limitu: {pl(LIMIT_KOSZTU - tot)} zł ({pl(100 * (LIMIT_KOSZTU - tot) / LIMIT_KOSZTU, 1)} %); rezerwa na nieprzewidziane w gr. 18: "
             f"{pl(rez)} zł. Korekty poza modelem (koncepcja, rozdz. 12) dodane jako pozycje gr. 18: "
             + (", ".join(f"{n} {pl(v)} zł" for n, v in F["extras_md"]) if F["extras_md"] else "brak") + ".")
    gm = md_grupy(D.kmd)
    if gm and F["draft"] and F["extras_md"]:
        gm[18] = gm.get(18, 0) + sum(v for _, v in F["extras_md"]) / 1e6   # korekty poza modelem dopisane w F.14.B do gr. 18
    if gm:
        rows = []
        for g, (gf, gh) in sorted(F["gsum"].items()):
            spec = gm.get(g)
            rows.append((g, pl(gf / 1e6, 3), pl(spec, 2) if spec is not None else "–", dpl(gf / 1e6 - spec, 3) if spec is not None else "–"))
        L.append("\nGrupy F.14.B vs tabela grup w koncepcji (rozdz. 12; gr. 18 łącznie z rezerwą i korektami poza modelem) [mln zł netto]:\n")
        L.append(md_table(["grupa", "F.14.B", "koncepcja", "Δ"], rows))
        dg = [r for r in rows if r[3] != "–" and abs(num_pl(r[3].replace("−", "-").replace("+", ""))) > 0.05]
        if dg:
            issue("INFO", "Grupy F.14.B różnią się od tabeli w koncepcji o > 0,05 mln: " + ", ".join(f"gr. {r[0]} ({r[3]})" for r in dg) +
                  " (korekty poza modelem przypisane do gr. 18; parametry nadpisane z modelu).")
    try:
        wt = P["wermd"].read_text(encoding="utf-8")
        m = re.search(r"Wynik:\s*\*\*([\d,]+)\s*mln", wt)
        if m and F["draft"]:
            L.append(f"\nWeryfikacja kosztów (`weryfikacja_koszt_eko.md`) po korektach ilości i pakiecie poprawek wskazuje **{m.group(1)} mln zł**; "
                     "do czasu rewizji F.14.B pozostaje na poziomie specyfikacji 1.0.")
            issue("KRYT", f"F.14.B w wersji roboczej ({pl(tot / 1e6, 2)} mln) – weryfikacja wskazuje {m.group(1)} mln (ościeża, pale, "
                          "dry-cooler, PV wg M.12); zapas do limitu po korektach ≈ 1 mln. Wymagana rewizja (rejestr v1.1, E-K-1).")
        elif m:
            L.append(f"\nF.14.B wg skryptu rewizji kosztów ({F['rev']}): **{pl(tot / 1e6, 2)} mln zł** netto (z rezerwą); weryfikacja kosztów "
                     f"v1.0 (`weryfikacja_koszt_eko.md`) po korektach ilości wskazywała {m.group(1)} mln zł – punkt wyjścia rewizji v1.1/v1.2.")
    except OSError:
        pass
    # zgodność F.14.B ↔ F.15.C
    p = F["params"]
    green_cost = (p.get("dach_ext") or 0) + (p.get("dach_int") or 0)
    rows = [("dachy zielone: I.13 vs 3.12 + 3.13* (dach_ext + dach_int)", pl(S["green_roof"]), pl(green_cost), dpl(S["green_roof"] - green_cost)),
            ("PC nadziemna: I.3 vs A_nad", pl(K["PC_nad"]), pl(p["A_nad"]), dpl(K["PC_nad"] - p["A_nad"])),
            ("PC podziemna: I.4 vs A_pod", pl(K["PC_pod"]), pl(p["A_pod"]), dpl(K["PC_pod"] - p["A_pod"])),
            ("dźwigi: I.11 + I.11.1 vs 10.1 + 10.2", K["lifts_os"] + K["lifts_tow"], int(p["windy_os"] + p["windy_tow"]), dpl(K["lifts_os"] + K["lifts_tow"] - p["windy_os"] - p["windy_tow"], 0)),
            ("punkty ładowania EV: I.14 vs 15.9", K["ev"], p.get("ev"), dpl((K["ev"] or 0) - (p.get("ev") or 0), 0))]
    L.append("\nSpójność F.14.B ↔ F.15.C (ilości):\n")
    L.append(md_table(["wielkość", "F.15.C", "F.14.B (parametr)", "Δ"], rows))
    if abs(S["green_roof"] - green_cost) > 1:
        issue("ISTOTNE", f"Dach zielony: F.15.C I.13 = {pl(S['green_roof'])} m² (D.* w budynek.json), F.14.B 3.12+3.13* = {pl(green_cost)} m² (parametr kosztów).")
    L.append("\nPoprawki błędów wzoru F.14.B: H163/H164 (wzór: `=F159`/`=H159`, czyli koszt budowy zamiast kosztu usługi) nadpisane kosztem "
             "Dokumentacji; brutto w każdym wierszu `=ROUND(F*(1+G),2)`; sumy grup i suma całkowita jako formuły po wstawieniu wierszy; "
             f"uzupełniono VAT 23 % w poz.: {', '.join(F['vat_fill']) or '–'}; uzupełniono j.m. w poz.: {', '.join(F['jm_fill']) or '–'}. "
             "Stawka 8 % (7.8, 15.7) pozostawiona jak we wzorze – do weryfikacji podatkowej (budynek biurowy).")
    issue("INFO", "F.14.B: VAT 8 % w poz. 7.8 (instalacja z pomp ciepła) i 15.7 (zieleń) przejęty ze wzoru – wątpliwy dla budynku biurowego (7.8).")
    sh = [r for r in F["rows"] if r["K"] and "[Z]" in r["K"]]
    if sh:
        issue("INFO", f"F.14.B: {len(sh)} wierszy gr. 8 i 9 to podział pozycji zbiorczych modelu (8.1–8.10, 9.1–9.9) wg udziałów typowych [Z] – do potwierdzenia kosztorysem.")
    zero = [r["lp"] for r in F["rows"] if not r["ph"] and not r["new"] and r["D"] is None]
    if zero:
        L.append(f"\nWiersze wzoru z wartością 0 (brak w koncepcji lub ujęte gdzie indziej – uwaga w kol. K): {', '.join(zero)}.")
    # ------------------------------------------------------------------ usługa
    L.append("\n## 12. Koszt usługi (Dokumentacja wg F.01)\n")
    fee = F["fee"]
    lim = LIMIT_USLUGI_PROC * LIMIT_KOSZTU
    if fee:
        rows = [("koszt usługi netto (H163)", pl(fee), F["fee_src"] or ""),
                (f"limit {pl(100 * LIMIT_USLUGI_PROC, 1)} % × 150 mln = {pl(lim / 1e6, 1)} mln netto", dpl(fee - lim), ok(fee <= lim)),
                (f"udział w koszcie realizacji F.14.B ({pl(tot / 1e6, 2)} mln)", pl(100 * fee / tot, 2) + " %", ok(fee / tot <= LIMIT_USLUGI_PROC)),
                (f"wariant ostrożny: 8,1 mln traktowane jako brutto → limit netto {pl(lim / (1 + VAT) / 1e6, 2)} mln", dpl(fee - lim / (1 + VAT)), ok(fee <= lim / (1 + VAT))),
                ("koszt usługi brutto (H164 = H163 × 1,23)", pl(F["fee_b"]), "")]
        try:
            bt = P["bench"].read_text(encoding="utf-8")
            t = {int(m.group(1).replace(" ", "")): num_pl(m.group(3)) for m in re.finditer(r"^\|\s*([\d ]{6,})\s*\|\s*([\d,]+)%\s*\|\s*([\d,]+)%\s*\|", bt, re.M)}
            if len(t) >= 2:
                (x0, y0), (x1, y1) = sorted(t.items())[:2]
                w = y0 + (y1 - y0) * (tot / 1e3 - x0) / (x1 - x0)
                rows.append((f"odniesienie: rozp. MRiT 2021, kat. V, W% przy WRB {pl(tot / 1e6, 1)} mln = {pl(w, 2)} % (same projekty)", pl(w / 100 * tot), "informacyjnie"))
        except OSError:
            pass
        L.append(md_table(["pozycja", "wartość", ""], rows, ["l", "r", "l"]))
        L.append("\nPodział wg etapów F.01 § 14 ust. 2: " + ", ".join(f"{e} {pl(fee * s / 1e6, 3)} mln" for e, s in ETAPY_F01) + ".")
        if fee > lim / (1 + VAT):
            issue("INFO", f"Koszt usługi {pl(fee / 1e6, 2)} mln netto mieści się w 8,1 mln netto, ale przekracza {pl(lim / (1 + VAT) / 1e6, 2)} mln, gdyby 8,1 mln uznać za brutto (niejasność Regulaminu).")
        if fee > lim:
            issue("KRYT", "Koszt usługi przekracza 5,4 % × 150 mln.")
    else:
        L.append("Brak kosztu Dokumentacji w źródłach – H163 puste ✖")
        issue("KRYT", "Brak kosztu usługi (H163) – F.14.B niekompletny.")
    # ------------------------------------------------------------------ pliki
    L.append("\n## 13. Pliki wynikowe i weryfikacja techniczna\n")
    rows = []
    for c in TEMPLATES:
        pth = res[c]["path"]
        z = zipfile.ZipFile(pth)
        core = z.read("docProps/core.xml").decode("utf-8")
        app = z.read("docProps/app.xml").decode("utf-8")
        meta_ok = not re.search(r"<dc:creator>|<cp:lastModifiedBy>|<Company>|<Manager>", core + app) and "docProps/custom.xml" not in z.namelist()
        try:
            openpyxl.load_workbook(pth)
            op = True
        except Exception:  # noqa: BLE001
            op = False
        lv = (lo or {}).get(c)
        lvt = "–" if lo is None else (ok(lv["ok"]) + " " + ", ".join(f"{a}={pl(g) if isinstance(g, (int, float)) else g}" for a, _, g, _ in lv["cells"]) if lv else "–")
        pd = pdfs.get(c, {}) if pdfs else {}
        rows.append((f"`{rel(pth)}`", ok(op), ok(meta_ok), lvt, (f"`{rel(pd['pdf'])}` ({pd['pages']} s., {pd['how']})" if pd.get("pdf") else "–")))
        if not meta_ok:
            issue("KRYT", f"{c}: metadane nieusunięte.")
        if lv and not lv["ok"]:
            issue("KRYT", f"{c}: formuły po przeliczeniu w LibreOffice ≠ wartości kontrolne ({lv['cells']}{lv['err']}).")
    L.append(md_table(["xlsx", "openpyxl", "metadane usunięte", "LibreOffice: przeliczone formuły kontrolne", "PDF A3 poziomo"], rows, ["l", "c", "c", "l", "l"]))
    for code, (n, miss) in (pdfchk or {}).items():
        L.append(f"\n{code}.pdf zawiera {n - len(miss)}/{n} numerów pomieszczeń {ok(not miss)}" + (f" – brak: {', '.join(miss[:10])}" if miss else ""))
        if miss:
            issue("ISTOTNE", f"{code}.pdf: brak numerów w renderze: {', '.join(miss[:10])}.")
    for x in log:
        L.append(f"\n- log: {x}")
    # ------------------------------------------------------------------ lista
    L.append("\n## 14. Lista niespójności (do audytu)\n")
    order = {"KRYT": 0, "ISTOTNE": 1, "INFO": 2}
    for i, (sev, t) in enumerate(sorted(issues, key=lambda x: order[x[0]]), 1):
        L.append(f"{i}. **[{sev}]** {t}")
    (OUT / "kontrola.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    return issues


# =================================================================================================== main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bez-pdf", action="store_true", help="bez renderu PDF i weryfikacji w LibreOffice")
    a = ap.parse_args(argv)
    OUT.mkdir(parents=True, exist_ok=True)
    D = Dane()
    res, log = {}, []
    build_f15a(D, res)
    build_f15b(D, res)
    build_f15c(D, res)
    build_f14b(D, res)
    plans = plan_check(D)
    pdfs, lo, pdfchk = {}, None, {}
    if not a.bez_pdf:
        pdfs = render_pdfs(res, log)
        lo = lo_verify(res, log)
        pdfchk = pdf_check(res, pdfs)
    issues = kontrola(D, res, plans, lo, pdfs, pdfchk, log)
    F = res["F.14.B"]
    print(f"F.15.A {pl(res['F.15.A']['total'])} m² | F.15.B {pl(res['F.15.B']['total'])} m² | PU {pl(res['F.15.C']['K']['kat_PU'])} m² | "
          f"F.14.B {pl(F['totF'] / 1e6, 2)} mln netto{' (WERSJA ROBOCZA)' if F['draft'] else ''} | usługa {pl((F['fee'] or 0) / 1e6, 2)} mln")
    print(f"niespójności: {len(issues)} (KRYT {sum(1 for s, _ in issues if s == 'KRYT')}, ISTOTNE {sum(1 for s, _ in issues if s == 'ISTOTNE')}) "
          f"→ {rel(OUT / 'kontrola.md')}")
    for c in TEMPLATES:
        print(" ", rel(res[c]["path"]), "|", rel(pdfs[c]["pdf"]) if pdfs.get(c, {}).get("pdf") else "bez PDF")


if __name__ == "__main__":
    main()
